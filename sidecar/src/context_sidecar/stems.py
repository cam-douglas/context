"""Demucs stem split. MIT is allowed; weights download into the model cache. Fail closed."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

STEM_NAMES = ("drums", "bass", "vocals", "other")


def _enabled() -> bool:
    return os.environ.get("CONTEXT_ENABLE_DEMUCS", "0").strip() == "1"


def _cache_dir() -> str:
    raw = os.environ.get("CONTEXT_MODEL_CACHE_DIR", "").strip()
    path = Path(raw) if raw else Path.home() / "Library/Application Support/Context/models"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def split_stems(file_path: str, dest_dir: str | None = None) -> dict[str, Any]:
    if not (file_path or "").strip():
        return {"ok": False, "wrote": False, "error": "missing_file_path", "stems": {}}
    source = Path(file_path)
    if not source.is_file():
        return {"ok": False, "wrote": False, "error": "missing_file", "stems": {}}
    if not _enabled():
        return {
            "ok": False,
            "wrote": False,
            "error": "demucs_disabled",
            "detail": "Set CONTEXT_ENABLE_DEMUCS=1 to split stems with Demucs.",
            "stems": {},
        }
    try:
        from demucs.api import Separator, save_audio
    except Exception:
        return {
            "ok": False,
            "wrote": False,
            "error": "demucs_not_installed",
            "stems": {},
        }
    try:
        os.environ.setdefault("TORCH_HOME", _cache_dir())
        separator = Separator()
        _origin, separated = separator.separate_audio_file(source)
        folder = Path(dest_dir) if dest_dir else source.parent / "stems"
        folder.mkdir(parents=True, exist_ok=True)
        written: dict[str, str] = {}
        rate = int(getattr(separator, "samplerate", None) or 44100)
        for name in STEM_NAMES:
            tensor = separated.get(name)
            if tensor is None:
                continue
            dest = folder / f"{source.stem}-{name}.wav"
            save_audio(tensor, dest, samplerate=rate)
            if dest.is_file():
                written[name] = str(dest)
        if not written:
            return {"ok": False, "wrote": False, "error": "demucs_empty", "stems": {}}
        return {
            "ok": True,
            "wrote": True,
            "backend": "demucs",
            "stems": written,
            "folder": str(folder),
        }
    except Exception as exc:
        return {
            "ok": False,
            "wrote": False,
            "error": "demucs_failed",
            "detail": str(exc),
            "stems": {},
        }
