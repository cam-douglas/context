"""Live generation progress for the plugin ETA and preview."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()
_STARTED = 0.0
_STATE: dict[str, Any] = {
    "ok": True,
    "active": False,
    "id": "",
    "phase": "idle",
    "step": 0,
    "steps": 0,
    "eta_sec": None,
    "elapsed_sec": 0.0,
    "preview_wav": None,
    "preview_ready": False,
    "preview_generation": 0,
    "message": "",
}


def progress_path() -> Path:
    raw = os.environ.get("CONTEXT_PROGRESS_PATH", "").strip()
    return Path(raw) if raw else Path.home() / "Library/Application Support/Context/generation-progress.json"


def preview_wav_path() -> Path:
    raw = os.environ.get("CONTEXT_PREVIEW_WAV", "").strip()
    if raw:
        return Path(raw)
    return Path.home() / "Library/Application Support/Context/Plugin/.preview/live.wav"


def snapshot() -> dict[str, Any]:
    with _LOCK:
        payload = dict(_STATE)
    preview = preview_wav_path()
    if preview.is_file() and preview.stat().st_size >= 1000:
        payload["preview_wav"] = str(preview)
        payload["preview_ready"] = True
    return payload


def begin(generator_id: str, *, steps: int = 0, message: str = "starting") -> None:
    global _STARTED
    _STARTED = time.perf_counter()
    with _LOCK:
        _STATE.update(
            {
                "ok": True,
                "active": True,
                "id": generator_id,
                "phase": "starting",
                "step": 0,
                "steps": max(0, int(steps)),
                "eta_sec": None,
                "elapsed_sec": 0.0,
                "preview_wav": None,
                "preview_ready": False,
                "preview_generation": 0,
                "message": message,
            }
        )
    _persist()


def update(*, step: int | None = None, steps: int | None = None, phase: str | None = None, message: str | None = None) -> None:
    elapsed = time.perf_counter() - _STARTED if _STARTED else 0.0
    with _LOCK:
        if steps is not None:
            _STATE["steps"] = max(0, int(steps))
        if step is not None:
            _STATE["step"] = max(0, min(int(step), int(_STATE.get("steps") or int(step))))
        if phase:
            _STATE["phase"] = phase
        if message is not None:
            _STATE["message"] = message
        _STATE["elapsed_sec"] = round(elapsed, 3)
        total = int(_STATE.get("steps") or 0)
        current = int(_STATE.get("step") or 0)
        if current >= 1 and total > current and elapsed > 0:
            _STATE["eta_sec"] = round((elapsed / current) * (total - current), 1)
        elif current >= total > 0:
            _STATE["eta_sec"] = 0.0
        _STATE["active"] = True
    _persist()


def mark_preview() -> None:
    path = preview_wav_path()
    with _LOCK:
        _STATE["preview_generation"] = int(_STATE.get("preview_generation") or 0) + 1
        _STATE["preview_ready"] = path.is_file() and path.stat().st_size >= 1000
        _STATE["preview_wav"] = str(path) if _STATE["preview_ready"] else None
    _persist()


def finish(*, ok: bool = True, message: str = "") -> None:
    elapsed = time.perf_counter() - _STARTED if _STARTED else 0.0
    with _LOCK:
        _STATE["active"] = False
        _STATE["phase"] = "done" if ok else "error"
        _STATE["eta_sec"] = 0.0
        _STATE["elapsed_sec"] = round(elapsed, 3)
        if int(_STATE.get("steps") or 0) > 0:
            _STATE["step"] = int(_STATE["steps"])
        if message:
            _STATE["message"] = message
        _STATE["ok"] = ok
    _persist()


def _persist() -> None:
    path = progress_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snapshot()) + "\n")
    except OSError:
        pass
