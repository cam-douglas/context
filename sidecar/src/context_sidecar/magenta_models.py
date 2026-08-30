"""Call isolated Magenta MelodyRNN / MusicVAE. Same path for every prompt. Never fake notes."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

WORKER = Path(__file__).resolve().parents[2] / "scripts" / "magenta_worker.py"
VENV_PYTHON = Path(__file__).resolve().parents[2] / ".venv-magenta" / "bin" / "python"


def _model_root() -> Path:
    raw = os.environ.get("CONTEXT_MAGENTA_DIR", "").strip()
    if raw:
        path = Path(raw)
    else:
        cache = os.environ.get("CONTEXT_MODEL_CACHE_DIR", "").strip()
        path = Path(cache) / "magenta" if cache else Path.home() / "Library/Application Support/Context/models/magenta"
    path.mkdir(parents=True, exist_ok=True)
    return path


def status() -> dict[str, Any]:
    root = _model_root()
    return {
        "venv_python": str(VENV_PYTHON),
        "venv_ready": VENV_PYTHON.is_file(),
        "worker": str(WORKER),
        "worker_ready": WORKER.is_file(),
        "attention_rnn": (root / "attention_rnn.mag").is_file(),
        "music_vae_mel": (root / "cat-mel_2bar_big.tar").is_file(),
        "music_vae_drums": (root / "cat-drums_2bar_small.lokl.tar").is_file(),
    }


def _scale_primer(plan: dict[str, Any]) -> list[int]:
    key = str(plan.get("key") or "")
    try:
        from music21 import scale

        pitches = (
            scale.MajorScale("C").getPitches("C4", "G4")
            if key == "C"
            else scale.MinorScale("A").getPitches("A3", "E4")
        )
        midis = [int(pitch.midi) for pitch in pitches][:4]
        if midis:
            return midis
    except Exception:
        pass
    return [60, 64, 67, 71]


def _primer_from_notes(notes: list[dict[str, Any]]) -> list[int]:
    pitches: list[int] = []
    for note in notes:
        pitch = max(0, min(127, int(note["pitch"])))
        if pitch not in pitches:
            pitches.append(pitch)
        if len(pitches) >= 4:
            break
    return pitches or _scale_primer({})


def _run(payload: dict[str, Any]) -> dict[str, Any] | None:
    if not VENV_PYTHON.is_file() or not WORKER.is_file():
        return None
    try:
        env = os.environ.copy()
        env.setdefault("TF_USE_LEGACY_KERAS", "1")
        env.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
        proc = subprocess.run(
            [str(VENV_PYTHON), str(WORKER)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if not proc.stdout.strip():
        return None
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if not result.get("ok") or not result.get("notes"):
        return None
    return result


def generate_notes(plan: dict[str, Any]) -> tuple[list[dict[str, Any]] | None, str]:
    """MusicVAE seeds a phrase; MelodyRNN extends it. No genre switch."""
    info = status()
    if not info["venv_ready"]:
        return None, "magenta_venv_missing"
    root = _model_root()
    tempo = plan.get("tempo_bpm")
    bars = plan.get("bars")
    vae = None
    if info["music_vae_mel"]:
        vae = _run(
            {
                "model": "music_vae",
                "config": "cat-mel_2bar_big",
                "checkpoint": str(root / "cat-mel_2bar_big.tar"),
                "tempo_bpm": tempo,
                "bars": bars,
                "temperature": 0.5,
            }
        )
    primer = _primer_from_notes(list(vae["notes"])) if vae else _scale_primer(plan)
    if info["attention_rnn"]:
        rnn = _run(
            {
                "model": "melody_rnn",
                "bundle": str(root / "attention_rnn.mag"),
                "tempo_bpm": tempo,
                "bars": bars,
                "primer": primer,
                "temperature": 1.0,
            }
        )
        if rnn:
            used = "melody_rnn+music_vae" if vae else "melody_rnn"
            return list(rnn["notes"]), used
    if vae:
        return list(vae["notes"]), "music_vae"
    return None, "magenta_weights_or_worker_failed"
