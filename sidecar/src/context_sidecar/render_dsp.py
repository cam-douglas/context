"""Render notes with numpy, then process through pedalboard. Fallback is stdlib wave."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path
from typing import Any


def _knobs(plan: dict[str, Any]) -> tuple[float, float]:
    values = plan.get("knobs") if isinstance(plan.get("knobs"), dict) else {}
    return float(values.get("reverence") or 0.5), float(values.get("abstraction") or 0.5)


def _voice_shape(voice: str) -> dict[str, Any]:
    return {
        "pedalboard": {"wave": "sine", "detune": 0.0, "width": 0.05, "brightness": 0.45},
        "musicgen": {"wave": "triangle", "detune": 0.003, "width": 0.18, "brightness": 0.55},
        "stable_audio_open": {"wave": "saw", "detune": 0.014, "width": 0.5, "brightness": 0.9},
        "audioldm2": {"wave": "pad", "detune": 0.022, "width": 0.65, "brightness": 0.22},
        "suno": {"wave": "square", "detune": 0.007, "width": 0.22, "brightness": 0.72},
        "udio": {"wave": "triangle", "detune": 0.02, "width": 0.55, "brightness": 0.48},
        "elevenlabs": {"wave": "noise", "detune": 0.0, "width": 0.35, "brightness": 0.62},
    }.get(voice, {"wave": "sine", "detune": 0.0, "width": 0.05, "brightness": 0.45})


def _tone(wave: str, freq: float, t: float, phase: float) -> float:
    if wave == "saw":
        return 2.0 * ((phase / (2.0 * math.pi)) % 1.0) - 1.0
    if wave == "square":
        return 1.0 if math.sin(phase) >= 0 else -1.0
    if wave == "triangle":
        return (2.0 / math.pi) * math.asin(max(-1.0, min(1.0, math.sin(phase))))
    if wave == "pad":
        return 0.7 * math.sin(phase) + 0.3 * math.sin(phase * 1.997)
    if wave == "noise":
        n = ((int(t * 44100) * 1103515245 + 12345) % 32768) / 16384.0 - 1.0
        return 0.35 * math.sin(phase) + 0.65 * n
    return math.sin(phase)


def _oscillator_buffer(plan: dict[str, Any], notes: list[dict[str, Any]], sr: int = 44100) -> tuple[list[list[float]], int]:
    tempo = float(plan["tempo_bpm"])
    end = max((note["start"] + note["length"]) for note in notes)
    total = int((end + 0.25) * 60.0 / tempo * sr)
    left = [0.0] * total
    right = [0.0] * total
    reverence, abstraction = _knobs(plan)
    voice = _voice_shape(str(plan.get("voice") or "pedalboard"))
    detune = float(voice["detune"]) + (1.0 - reverence) * 0.03 + abstraction * 0.015
    width = min(0.9, float(voice["width"]) + abstraction * 0.35)
    brightness = min(1.0, float(voice["brightness"]) + (1.0 - reverence) * 0.25)
    octave = abstraction * 0.6
    wave_name = str(voice["wave"])
    for note in notes:
        length = max(1, int(note["length"] * 60.0 / tempo * sr))
        freq = 440.0 * (2.0 ** ((int(note["pitch"]) - 69) / 12.0))
        vel = int(note.get("velocity") or 100) / 127.0
        pitch = int(note["pitch"])
        start = int(float(note["start"]) * 60.0 / tempo * sr)
        for i in range(length):
            index = start + i
            if index >= total:
                break
            t = i / sr
            env = min(1.0, i / (0.01 * sr)) * math.exp(-t * (18.0 if pitch < 40 else 3.2 + reverence * 2.5))
            if pitch < 40:
                osc = math.sin(2 * math.pi * (freq * math.exp(-t * 8.0)) * t)
                left[index] += 0.55 * vel * env * osc
                right[index] += 0.55 * vel * env * osc
                continue
            if pitch in {42, 44, 46}:
                osc = ((i * 1103515245 + 12345) % 32768) / 16384.0 - 1.0
                env = math.exp(-t * 40.0)
                left[index] += 0.45 * vel * env * osc
                right[index] += 0.45 * vel * env * osc
                continue
            phase = 2 * math.pi * freq * t
            osc = _tone(wave_name, freq, t, phase)
            osc += brightness * 0.35 * math.sin(4 * math.pi * freq * (1.0 + detune) * t)
            if octave > 0.05:
                osc += octave * 0.4 * math.sin(4 * math.pi * freq * t)
            sample = 0.5 * vel * env * osc
            left[index] += sample
            right[index] += 0.5 * vel * env * _tone(wave_name, freq * (1.0 + detune), t, phase * (1.0 + detune * width * 8.0))
    peak = max((max(abs(l), abs(r)) for l, r in zip(left, right, strict=False)), default=1.0) or 1.0
    scale = 0.89 / peak
    return [[sample * scale for sample in left], [sample * scale for sample in right]], sr


def _pedalboard_for(style: str, knobs: dict[str, Any] | None = None) -> Any:
    from pedalboard import Chorus, Compressor, Delay, HighpassFilter, LadderFilter, Pedalboard, Reverb

    values = knobs if isinstance(knobs, dict) else {}
    reverence = float(values.get("reverence") or 0.5)
    abstraction = float(values.get("abstraction") or 0.5)
    room = min(0.28, 0.04 + abstraction * 0.18 + (0.04 if style == "ambient" else 0.0))
    wet_level = min(0.16, 0.02 + abstraction * 0.12)
    dry_level = max(0.72, 1.0 - wet_level)
    chorus_mix = min(0.65, abstraction * 0.62)
    delay_mix = min(0.48, abstraction * 0.42)
    cutoff = max(600.0, 14000.0 * (0.18 + reverence * 0.82))
    grit = (1.0 - reverence) * 0.35

    return Pedalboard(
        [
            HighpassFilter(cutoff_frequency_hz=40),
            Compressor(threshold_db=-18, ratio=2.0 + (1.0 - reverence)),
            LadderFilter(cutoff_hz=cutoff, resonance=0.08 + grit),
            Chorus(rate_hz=0.25 + abstraction * 0.9, mix=chorus_mix),
            Delay(delay_seconds=0.08 + abstraction * 0.28, mix=delay_mix),
            Reverb(room_size=room, wet_level=wet_level, dry_level=dry_level),
        ]
    )


def render_wav(plan: dict[str, Any], notes: list[dict[str, Any]], dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    channels, sr = _oscillator_buffer(plan, notes)
    backend = "wave-stdlib"
    try:
        import numpy as np
        from pedalboard.io import AudioFile

        stereo = np.array(channels, dtype=np.float32)
        knobs = plan.get("knobs") if isinstance(plan.get("knobs"), dict) else {}
        board = _pedalboard_for(str(plan.get("family") or plan.get("style") or "default"), knobs)
        processed = board(stereo, sr)
        with AudioFile(str(dest), "w", sr, processed.shape[0]) as handle:
            handle.write(processed)
        backend = f"pedalboard-{plan.get('voice') or 'pedalboard'}"
        return backend
    except Exception:
        with wave.open(str(dest), "wb") as handle:
            handle.setnchannels(2)
            handle.setsampwidth(2)
            handle.setframerate(sr)
            frames = bytearray()
            for left, right in zip(channels[0], channels[1], strict=False):
                frames += struct.pack(
                    "<hh",
                    int(max(-32767, min(32767, left * 32767))),
                    int(max(-32767, min(32767, right * 32767))),
                )
            handle.writeframes(frames)
        return backend
