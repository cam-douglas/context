"""Inventory of the owner-requested stack. Import-safe; never stores secrets."""

from __future__ import annotations

import importlib.util
import os
from typing import Any

CORE_MODULES = (
    ("python", "sys"),
    ("numpy", "numpy"),
    ("scipy", "scipy"),
    ("librosa", "librosa"),
    ("soundfile", "soundfile"),
    ("pydub", "pydub"),
    ("mido", "mido"),
    ("pretty_midi", "pretty_midi"),
    ("music21", "music21"),
    ("note_seq", "note_seq"),
    ("pedalboard", "pedalboard"),
    ("pyroomacoustics", "pyroomacoustics"),
)

HEAVY_MODULES = (
    ("torchaudio", "torchaudio"),
    ("diffusers", "diffusers"),
    ("transformers", "transformers"),
    ("demucs", "demucs"),
    ("laion_clap", "laion_clap"),
    ("audiocraft", "audiocraft"),
    ("dawdreamer", "dawdreamer"),
    ("magenta", "magenta"),
)

SESSION_MODULES = (
    ("als_json", "context_sidecar.als_json"),
)

BLOCKED_OR_DEFERRED = {
    "musicgen": "transformers pipeline facebook/musicgen-small; CONTEXT_ENABLE_GENERATION=1 for /synthesize",
    "clap": "transformers laion/clap-htsat-unfused; CONTEXT_ENABLE_CLAP=1",
    "demucs": "demucs.api Separator; CONTEXT_ENABLE_DEMUCS=1",
    "audioldm2": "diffusers AudioLDM2Pipeline + cvssp/audioldm2-music on rotate/compose; /synthesize stays blocked (NC weights)",
    "heartmula": "not packaged; adapter stub",
    "magenta": "TF Magenta is sidecar/.venv-magenta (MelodyRNN + MusicVAE notes). Not imported into the torch/diffusers venv",
    "stable_audio_open": "diffusers StableAudioPipeline + stabilityai/stable-audio-open-1.0",
    "bark": "not packaged; adapter stub",
    "parler_tts": "not packaged; adapter stub",
    "f5_tts": "not packaged; adapter stub",
    "chattts": "not packaged; adapter stub",
    "elevenlabs": "needs ELEVENLABS_API_KEY in the process env",
    "suno": "needs SUNO_API_KEY in the process env",
    "udio": "needs UDIO_API_KEY in the process env",
    "scythe": "needs SCYTHE_API_KEY in the process env",
    "als_write": "als-json session export writes a cloned .als; never overwrites the source set",
    "fmod": "game engine; not in this host",
    "wwise": "game engine; not in this host",
    "skia_webgl": "JUCE is the frontend",
    "web_audio_api": "JUCE is the frontend",
}


def _present(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception:
        return False


def probe() -> dict[str, Any]:
    installed = {label: _present(module) for label, module in CORE_MODULES + HEAVY_MODULES + SESSION_MODULES}
    from context_sidecar.magenta_models import status as magenta_status

    return {
        "ok": True,
        "bind": "127.0.0.1",
        "installed": installed,
        "magenta": magenta_status(),
        "flags": {
            "CONTEXT_ENABLE_GENERATION": os.environ.get("CONTEXT_ENABLE_GENERATION", "0"),
            "CONTEXT_ENABLE_DEMUCS": os.environ.get("CONTEXT_ENABLE_DEMUCS", "0"),
            "CONTEXT_ENABLE_CLAP": os.environ.get("CONTEXT_ENABLE_CLAP", "0"),
        },
        "env_names_only": (
            "ELEVENLABS_API_KEY",
            "SUNO_API_KEY",
            "UDIO_API_KEY",
            "SCYTHE_API_KEY",
            "CONTEXT_SIDECAR_PORT",
            "CONTEXT_MODEL_CACHE_DIR",
            "CONTEXT_SAMPLE_LIBRARY",
        ),
        "deferred": BLOCKED_OR_DEFERRED,
        "frontend": "juce",
    }
