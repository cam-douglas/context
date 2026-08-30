"""Localhost HTTP for the Context device. Bind 127.0.0.1 only."""

from __future__ import annotations

import errno
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from context_sidecar.adapters import synthesize_texture
from context_sidecar.compose import compose_to_folder, publish_drops
from context_sidecar.generation import current_generator, rotate as rotate_generator
from context_sidecar.genres import index_meta, lineage_for, match_genres
from context_sidecar.analysis import analyze_paths
from context_sidecar.arrange import loop_to_song
from context_sidecar.dsp import dawdreamer_rehearse, ducking_plan, room_curve, room_impulse
from context_sidecar.export import export_session, parse_als_readonly
from context_sidecar.intent import validate_intent
from context_sidecar.mix_audit import audit_stems
from context_sidecar.schema import SchemaError, empty_arrangement
from context_sidecar.search import sample_library, search_local
from context_sidecar.progress import snapshot as progress_snapshot
from context_sidecar.stack import probe
from context_sidecar.stems import split_stems

DEFAULT_PORT = 8765
BIND_HOST = "127.0.0.1"


def listen_port() -> int:
    raw = os.environ.get("CONTEXT_SIDECAR_PORT", "").strip()
    if not raw:
        return DEFAULT_PORT
    return int(raw)


def ready_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "bind": BIND_HOST,
        "service": "context_sidecar",
        "generator": current_generator(),
    }


def health_payload() -> dict[str, Any]:
    payload = probe()
    payload["service"] = "context_sidecar"
    payload["generator"] = current_generator()
    payload["genre_index"] = index_meta()
    return payload


def handle_intent(body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    try:
        intent = validate_intent(body)
    except SchemaError as exc:
        return 400, {"ok": False, "error": str(exc)}
    preview = empty_arrangement(
        tempo_bpm=float(intent["project"]["tempo_bpm"]),
        musical_key=str(intent["project"].get("musical_key") or "C"),
    )
    return 200, {"ok": True, "intent": intent, "preview": preview}


class ContextHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _write(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            full = (parse_qs(parsed.query).get("full") or [""])[0] in {"1", "true", "yes"}
            self._write(200, health_payload() if full else ready_payload())
            return
        if parsed.path == "/progress":
            self._write(200, progress_snapshot())
            return
        if parsed.path == "/genres":
            query = (parse_qs(parsed.query).get("q") or [""])[0]
            matches = match_genres(query) if query.strip() else []
            self._write(
                200,
                {
                    **index_meta(),
                    "query": query,
                    "matches": matches[:25],
                    "lineage": [lineage_for(name) for name in matches[:8]],
                },
            )
            return
        self._write(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._write(400, {"ok": False, "error": "invalid json"})
            return
        if not isinstance(body, dict):
            self._write(400, {"ok": False, "error": "body must be an object"})
            return
        if path == "/rotate":
            self._write(200, {"ok": True, "generator": rotate_generator()})
            return
        if path == "/intent":
            status, payload = handle_intent(body)
            if status == 200 and os.environ.get("CONTEXT_COMPOSE_ON_INTENT", "0") == "1":
                prompt = str(body.get("prompt") or "").strip()
                if prompt:
                    dest = str(body.get("dest_dir") or "").strip()
                    try:
                        payload["compose"] = compose_to_folder(prompt, dest) if dest else publish_drops(prompt)
                    except OSError as exc:
                        payload["compose"] = {"ok": False, "error": str(exc)}
            self._write(status, payload)
            return
        if path == "/analyze":
            paths = [item for item in body.get("paths") or [] if isinstance(item, str)]
            self._write(200, analyze_paths(paths))
            return
        if path == "/mix-audit":
            stems = body.get("stems") or {}
            if not isinstance(stems, dict):
                self._write(400, {"ok": False, "error": "stems must be an object"})
                return
            self._write(200, audit_stems({str(key): str(value) for key, value in stems.items()}))
            return
        if path == "/arrange":
            self._write(
                200,
                loop_to_song(
                    genre_target=str(body.get("genre_target") or "melodic techno"),
                    loop_bars=int(body.get("loop_bars") or 8),
                    tempo_bpm=float(body.get("tempo_bpm") or 124),
                    musical_key=str(body.get("musical_key") or "Am"),
                    source_kind=str(body.get("source_kind") or "audio"),
                    source_path=str(body.get("source_path") or ""),
                ),
            )
            return
        if path == "/search":
            self._write(
                200,
                search_local(
                    str(body.get("query") or ""),
                    str(body.get("folder") or sample_library()),
                    limit=int(body.get("limit") or 80),
                    quick=bool(body.get("quick", True)),
                ),
            )
            return
        if path == "/stems":
            self._write(200, split_stems(str(body.get("file_path") or "")))
            return
        if path == "/synthesize":
            self._write(
                200,
                synthesize_texture(str(body.get("prompt") or ""), backend=str(body.get("backend") or "none")),
            )
            return
        if path == "/dsp":
            kind = str(body.get("kind") or "ducking")
            if kind == "room":
                knobs = body.get("knobs") if isinstance(body.get("knobs"), dict) else None
                self._write(
                    200,
                    room_impulse(knobs=knobs, family=str(body.get("family") or ""))
                    if body.get("simulate")
                    else room_curve(body.get("balance")),
                )
                return
            if kind == "dawdreamer":
                self._write(
                    200,
                    dawdreamer_rehearse(str(body.get("plugin_id") or ""), list(body.get("automation") or [])),
                )
                return
            self._write(200, ducking_plan(list(body.get("hits") or []), amount=float(body.get("amount") or 0.4)))
            return
        if path == "/export":
            if body.get("parse_only"):
                self._write(200, parse_als_readonly(str(body.get("source_als") or "")))
                return
            dest = str(body.get("dest_dir") or "").strip()
            if not dest:
                self._write(400, {"ok": False, "error": "dest_dir must not be empty"})
                return
            arrangement = body.get("arrangement") if isinstance(body.get("arrangement"), dict) else None
            self._write(
                200,
                export_session(
                    dest,
                    midi_path=body.get("midi_path"),
                    stem_paths=list(body.get("stem_paths") or []),
                    arrangement=arrangement,
                    source_als=body.get("source_als"),
                    notes=list(body.get("notes") or []) if isinstance(body.get("notes"), list) else None,
                    tempo_bpm=float(body.get("tempo_bpm") or 120),
                    musical_key=str(body.get("musical_key") or "C"),
                    bars=int(body.get("bars") or 4),
                    locks=list(body.get("locks") or []),
                    slug=str(body.get("slug") or "Context"),
                    render=body.get("render", True) is not False,
                ),
            )
            return
        if path == "/compose":
            prompt = str(body.get("prompt") or "").strip()
            dest = str(body.get("dest_dir") or "").strip()
            if not prompt:
                self._write(400, {"ok": False, "error": "prompt must not be empty"})
                return
            knobs = body.get("knobs") if isinstance(body.get("knobs"), dict) else {}
            reference = str(body.get("reference_path") or "").strip()
            library = str(body.get("library_folder") or "").strip()
            policy = {
                "system_prompt": body.get("system_prompt"),
                "rules": body.get("rules"),
                "negative_prompt": body.get("negative_prompt"),
            }
            try:
                self._write(
                    200,
                    compose_to_folder(
                        prompt,
                        dest,
                        knobs=knobs,
                        reference_path=reference,
                        policy=policy,
                        library_folder=library or None,
                        split_stems_after=body.get("stems") is True,
                    )
                    if dest
                    else publish_drops(prompt),
                )
            except ValueError as exc:
                self._write(400, {"ok": False, "error": str(exc)})
            except OSError as exc:
                self._write(500, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self._write(500, {"ok": False, "error": str(exc)})
            return
        self._write(404, {"ok": False, "error": "not found"})


def _warm_generator() -> None:
    try:
        from context_sidecar.generation import _audioldm2_pipe, _musicgen_pipe, _sao_pipe, current_generator

        gid = current_generator()["id"]
        if gid == "audioldm2":
            _audioldm2_pipe()
        elif gid == "stable_audio_open":
            _sao_pipe()
        elif gid == "musicgen":
            _musicgen_pipe()
        print(f"context_sidecar warmed {gid}", flush=True)
    except Exception as exc:
        print(f"context_sidecar warm failed: {exc}", flush=True)


def make_server(port: int | None = None) -> ThreadingHTTPServer:
    chosen = DEFAULT_PORT if port is None else port
    return ThreadingHTTPServer((BIND_HOST, chosen), ContextHandler)


def main() -> None:
    port = listen_port()
    try:
        server = make_server(port)
    except OSError as exc:
        if exc.errno == errno.EADDRINUSE:
            print(f"context_sidecar already bound on {BIND_HOST}:{port}", flush=True)
            return
        raise
    print(f"context_sidecar listening on {BIND_HOST}:{port}", flush=True)
    threading.Thread(target=_warm_generator, name="context-warm-generator", daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
