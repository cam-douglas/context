"""License-gated generation adapters. AudioLDM 2 stays out of /synthesize. MusicGen/SAO/AudioLDM 2 use the rotate path."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from context_sidecar.generation import run_generator

BLOCKED_BACKENDS = ("audioldm2", "audioldm 2")
COMMERCIAL_ENV = {
    "elevenlabs": "ELEVENLABS_API_KEY",
    "suno": "SUNO_API_KEY",
    "udio": "UDIO_API_KEY",
    "scythe": "SCYTHE_API_KEY",
}
LOCAL_GENERATORS = {
    "musicgen": "musicgen",
    "audiocraft": "musicgen",
    "stable_audio_open": "stable_audio_open",
    "stable-audio-open": "stable_audio_open",
    "sao": "stable_audio_open",
}


def generation_enabled() -> bool:
    return os.environ.get("CONTEXT_ENABLE_GENERATION", "0").strip() == "1"


def _dumps() -> Path:
    raw = os.environ.get("CONTEXT_DUMPS_DIR", "").strip()
    path = Path(raw) if raw else Path.home() / "Library/Application Support/Context/Plugin"
    path.mkdir(parents=True, exist_ok=True)
    return path


def synthesize_texture(prompt: str, *, backend: str = "none") -> dict[str, Any]:
    name = (backend or "none").strip().lower()
    if name in BLOCKED_BACKENDS:
        return {
            "ok": False,
            "wrote": False,
            "error": "blocked_backend",
            "detail": "AudioLDM 2 stays out of the commercial path. Use a local pedalboard texture instead.",
        }
    if name in COMMERCIAL_ENV:
        env_name = COMMERCIAL_ENV[name]
        if not os.environ.get(env_name, "").strip():
            return {"ok": False, "wrote": False, "error": "missing_env", "env_name": env_name}
        return {"ok": False, "wrote": False, "error": "commercial_adapter_not_called", "env_name": env_name}
    if name in LOCAL_GENERATORS:
        if not generation_enabled():
            return {
                "ok": False,
                "wrote": False,
                "error": "generation_disabled",
                "detail": "Set CONTEXT_ENABLE_GENERATION=1 to synthesize with MusicGen or Stable Audio Open.",
            }
        dest = _dumps() / f"{LOCAL_GENERATORS[name]}-texture.wav"
        generated = run_generator(
            LOCAL_GENERATORS[name],
            prompt,
            dest,
            {"duration_sec": 8.0, "tempo_bpm": 120.0, "bars": 4, "key": "Am", "style": "texture", "seed": 0},
        )
        return {
            "ok": bool(generated.get("ok") and dest.is_file()),
            "wrote": dest.is_file(),
            "backend": generated.get("backend") or LOCAL_GENERATORS[name],
            "file_path": str(dest) if dest.is_file() else None,
            "generator": generated,
        }
    if not generation_enabled():
        return {
            "ok": False,
            "wrote": False,
            "error": "generation_disabled",
            "detail": "Set CONTEXT_ENABLE_GENERATION=1 after a reviewed adapter is installed.",
        }
    return {
        "ok": False,
        "wrote": False,
        "error": "no_weight_download",
        "detail": f"No local foundation weights are vendored for: {prompt}",
    }
