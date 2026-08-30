"""Read-only analysis. librosa is optional; wave/stdlib is the default path."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path
from typing import Any


def _load_mono_pcm(path: str) -> tuple[list[float], int]:
    with wave.open(path, "r") as handle:
        channels = handle.getnchannels()
        rate = handle.getframerate()
        width = handle.getsampwidth()
        frames = handle.readframes(handle.getnframes())
    if width != 2:
        raise ValueError("analysis supports 16-bit WAV only")
    samples = struct.unpack("<" + "h" * (len(frames) // 2), frames)
    if channels == 1:
        mono = [sample / 32768.0 for sample in samples]
    else:
        mono = []
        for index in range(0, len(samples), channels):
            frame = samples[index : index + channels]
            mono.append(sum(frame) / (32768.0 * len(frame)))
    return mono, rate


def _rms(samples: list[float]) -> float:
    if not samples:
        return 0.0
    return math.sqrt(sum(sample * sample for sample in samples) / len(samples))


def _band_energy(samples: list[float], rate: int, low_hz: float, high_hz: float) -> float:
    # Zero-crossing / windowed RMS proxy so tests do not require numpy/librosa.
    window = max(int(rate * 0.02), 32)
    band = []
    step = window
    for start in range(0, len(samples) - window, step):
        chunk = samples[start : start + window]
        crossings = sum(
            1
            for index in range(1, len(chunk))
            if chunk[index - 1] == 0 or chunk[index - 1] * chunk[index] < 0
        )
        freq = (crossings * rate) / (2 * len(chunk))
        if low_hz <= freq <= high_hz:
            band.extend(chunk)
    return _rms(band) if band else _rms(samples) * 0.1


def analyze_audio(path: str) -> dict[str, Any]:
    samples, rate = _load_mono_pcm(path)
    energy = _rms(samples)
    duration = len(samples) / float(rate)
    tempo_bpm = 120.0
    musical_key = "C"
    backend = "wave-stdlib"
    lufs = 20.0 * math.log10(max(energy, 1e-9))
    try:
        import librosa
        import numpy as np
        from scipy.signal import butter, sosfilt

        y, sr = librosa.load(path, sr=None, mono=True)
        tempo_bpm = float(librosa.feature.rhythm.tempo(y=y, sr=sr)[0])
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        musical_key = ("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")[
            int(np.argmax(np.mean(chroma, axis=1)))
        ]
        sos = butter(2, [80 / (sr / 2), 4000 / (sr / 2)], btype="band", output="sos")
        filtered = sosfilt(sos, y)
        energy = float(np.sqrt(np.mean(np.square(filtered)))) if len(filtered) else energy
        lufs = 20.0 * math.log10(max(float(np.sqrt(np.mean(np.square(y)))), 1e-9))
        backend = "librosa+scipy"
    except Exception:
        backend = "wave-stdlib"
    return {
        "file_path": path,
        "duration_seconds": duration,
        "tempo_bpm": tempo_bpm,
        "musical_key": musical_key,
        "energy": energy,
        "lufs_proxy": lufs,
        "section_candidates": [
            {"label": "intro", "start_beats": 0, "length_beats": 8},
            {"label": "build", "start_beats": 8, "length_beats": 8},
        ],
        "bands": {
            "low": _band_energy(samples, rate, 20, 120),
            "mud": _band_energy(samples, rate, 180, 320),
            "mid": _band_energy(samples, rate, 800, 3000),
        },
        "backend": backend,
    }


def analyze_paths(paths: list[str]) -> dict[str, Any]:
    reports = []
    for path in paths:
        if path and Path(path).is_file() and path.lower().endswith(".wav"):
            reports.append(analyze_audio(path))
    return {
        "ok": True,
        "wrote": False,
        "reports": reports,
        "host_role_hint": None,
    }
