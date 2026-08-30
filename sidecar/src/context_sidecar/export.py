"""Export a Context arrangement into a DAW session with source-set integrity."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from context_sidecar.dsp import dawdreamer_render_arrangement
from context_sidecar.schema import SCHEMA_VERSION
from context_sidecar.session_export import export_live_set, parse_session


def arrangement_from_assets(
    *,
    tempo_bpm: float = 120,
    musical_key: str = "C",
    midi_path: str | None = None,
    stem_paths: list[str] | None = None,
    notes: list[dict[str, Any]] | None = None,
    bars: int = 4,
    slug: str = "Context",
) -> dict[str, Any]:
    length = max(4, int(bars) * 4)
    tracks: list[dict[str, Any]] = []
    audio_clips = []
    for index, path in enumerate(stem_paths or []):
        if path and Path(path).is_file():
            audio_clips.append(
                {
                    "id": f"audio-{index}",
                    "kind": "audio",
                    "start_beats": 0,
                    "length_beats": length,
                    "file_path": path,
                }
            )
    if audio_clips:
        tracks.append({"id": "context-audio", "name": slug, "kind": "audio", "clips": audio_clips})
    tracks.append(
        {
            "id": "context-midi",
            "name": f"{slug} MIDI",
            "kind": "midi",
            "clips": [
                {
                    "id": "midi-0",
                    "kind": "midi",
                    "start_beats": 0,
                    "length_beats": length,
                    "notes": list(notes or []),
                    "file_path": midi_path,
                }
            ],
        }
    )
    sections = [{"id": "export", "label": "other", "start_beats": 0, "length_beats": length}]
    return {
        "schema_version": SCHEMA_VERSION,
        "tempo_bpm": tempo_bpm,
        "musical_key": musical_key,
        "time_signature": [4, 4],
        "sections": sections,
        "tracks": tracks,
        "locators": [{"name": "Context", "beats": 0}],
    }


def export_session(
    dest_dir: str,
    *,
    midi_path: str | None = None,
    stem_paths: list[str] | None = None,
    arrangement: dict[str, Any] | None = None,
    source_als: str | None = None,
    notes: list[dict[str, Any]] | None = None,
    tempo_bpm: float = 120,
    musical_key: str = "C",
    bars: int = 4,
    locks: list[str] | None = None,
    slug: str = "Context",
    render: bool = True,
) -> dict[str, Any]:
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    if midi_path and Path(midi_path).is_file():
        target = dest / Path(midi_path).name
        if target.resolve() != Path(midi_path).resolve():
            shutil.copy2(midi_path, target)
        copied.append(str(target if target.exists() else midi_path))
    staged_stems: list[str] = []
    for path in stem_paths or []:
        source = Path(path)
        if not source.is_file():
            continue
        target = dest / source.name
        if target.resolve() != source.resolve():
            shutil.copy2(source, target)
        staged = str(target if target.exists() else source)
        copied.append(staged)
        staged_stems.append(staged)
    plan = arrangement or arrangement_from_assets(
        tempo_bpm=tempo_bpm,
        musical_key=musical_key,
        midi_path=copied[0] if midi_path else None,
        stem_paths=staged_stems,
        notes=notes,
        bars=bars,
        slug=slug,
    )
    try:
        session = export_live_set(
            str(dest),
            plan,
            source_als=source_als,
            midi_path=midi_path,
            stem_paths=staged_stems,
            locks=locks,
            slug=slug,
        )
    except ValueError as exc:
        session = {"ok": False, "wrote_als": False, "error": str(exc)}
    rendered = (
        dawdreamer_render_arrangement(plan, dest / f"{slug}-render.wav")
        if render
        else {"ok": False, "wrote": False, "error": "render_skipped"}
    )
    if rendered.get("path"):
        copied.append(str(rendered["path"]))
    files = copied + [path for path in (session.get("als_path"), session.get("als_json_path")) if path]
    return {
        "ok": bool(session.get("ok")),
        "wrote_als": bool(session.get("wrote_als")),
        "format": session.get("format") or "midi_and_stems",
        "files": files,
        "session": session,
        "render": rendered,
        "claim": session.get("claim")
        or "file-drop only; does not arrange Logic, GarageBand, or FL projects",
    }


def parse_als_readonly(path: str) -> dict[str, Any]:
    parsed = parse_session(path)
    if not parsed.get("ok"):
        return {"ok": False, "wrote_als": False, "error": parsed.get("error") or "not_an_als"}
    inventory = parsed["inventory"]
    return {
        "ok": True,
        "wrote_als": False,
        "tag": "Ableton",
        "tracks": inventory.get("track_names"),
        "clip_count": inventory.get("clip_count"),
        "tempo": inventory.get("tempo"),
        "claim": "als-json parse; write goes through export_session and never overwrites the source",
    }
