#!/usr/bin/env python3
"""Write an audible 4-bar house loop. Never copies fixtures/silence.wav."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

TEMPO = 124.0
BARS = 4
SR = 44100
BEATS = BARS * 4


def beat_to_sample(beat: float) -> int:
    return int(beat * 60.0 / TEMPO * SR)


def add(buf: list[float], start: int, values: list[float]) -> None:
    for i, value in enumerate(values):
        index = start + i
        if 0 <= index < len(buf):
            buf[index] += value


def kick(sr: int = SR) -> list[float]:
    length = int(0.22 * sr)
    out = []
    phase = 0.0
    for i in range(length):
        t = i / sr
        freq = 150.0 * math.exp(-t * 18.0) + 38.0
        phase += 2.0 * math.pi * freq / sr
        env = math.exp(-t * 14.0)
        out.append(0.95 * env * math.sin(phase))
    return out


def clap(sr: int = SR) -> list[float]:
    length = int(0.18 * sr)
    out = []
    for i in range(length):
        t = i / sr
        noise = ((i * 1103515245 + 12345) % 32768) / 16384.0 - 1.0
        env = math.exp(-t * 28.0)
        out.append(0.45 * env * noise)
    return out


def hat(sr: int = SR, open_hat: bool = False) -> list[float]:
    length = int((0.12 if open_hat else 0.045) * sr)
    out = []
    prev = 0.0
    for i in range(length):
        t = i / sr
        noise = ((i * 214013 + 2531011) % 32768) / 16384.0 - 1.0
        hp = noise - prev
        prev = noise
        env = math.exp(-t * (18.0 if open_hat else 55.0))
        out.append((0.22 if open_hat else 0.16) * env * hp)
    return out


def bass(freq: float, beats: float, sr: int = SR) -> list[float]:
    length = beat_to_sample(beats)
    out = []
    for i in range(length):
        t = i / sr
        env = min(1.0, t / 0.01) * math.exp(-t * 3.5)
        osc = math.sin(2.0 * math.pi * freq * t) + 0.3 * math.sin(4.0 * math.pi * freq * t)
        out.append(0.35 * env * osc)
    return out


def render() -> list[float]:
    total = beat_to_sample(BEATS) + 2048
    buf = [0.0] * total
    kick_s = kick()
    clap_s = clap()
    hat_s = hat()
    open_s = hat(open_hat=True)
    for beat in range(BEATS):
        add(buf, beat_to_sample(float(beat)), kick_s)
        add(buf, beat_to_sample(float(beat) + 0.5), hat_s)
        if beat % 2 == 1:
            add(buf, beat_to_sample(float(beat)), clap_s)
        if beat % 4 == 3:
            add(buf, beat_to_sample(float(beat) + 0.5), open_s)
        if beat % 4 in {0, 3}:
            add(buf, beat_to_sample(float(beat)), bass(55.0, 0.45))
        elif beat % 4 == 2:
            add(buf, beat_to_sample(float(beat)), bass(73.42, 0.4))
    peak = max(abs(sample) for sample in buf) or 1.0
    scale = 0.89 / peak
    return [max(-1.0, min(1.0, sample * scale)) for sample in buf]


def write_wav(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        frames = bytearray()
        for sample in samples:
            value = int(max(-32767, min(32767, sample * 32767)))
            frames += struct.pack("<hh", value, value)
        handle.writeframes(frames)


def write_midi(path: Path) -> None:
    def vlq(value: int) -> bytes:
        parts = [value & 0x7F]
        value >>= 7
        while value:
            parts.append(0x80 | (value & 0x7F))
            value >>= 7
        return bytes(reversed(parts))

    tempo = int(60_000_000 / TEMPO)
    events: list[tuple[int, bytes]] = [
        (0, bytes([0xFF, 0x51, 0x03, (tempo >> 16) & 0xFF, (tempo >> 8) & 0xFF, tempo & 0xFF])),
        (0, bytes([0xFF, 0x03, 0x0A]) + b"House Loop"),
    ]
    ticks_per_beat = 480
    for beat in range(BEATS):
        tick = beat * ticks_per_beat
        events.append((tick, bytes([0x99, 36, 120])))
        events.append((tick + 80, bytes([0x89, 36, 0])))
        events.append((tick + 240, bytes([0x99, 42, 70])))
        events.append((tick + 280, bytes([0x89, 42, 0])))
        if beat % 2 == 1:
            events.append((tick, bytes([0x99, 39, 110])))
            events.append((tick + 100, bytes([0x89, 39, 0])))
        if beat % 4 in {0, 3}:
            events.append((tick, bytes([0x90, 33, 100])))
            events.append((tick + 200, bytes([0x80, 33, 0])))
    events.append((BEATS * ticks_per_beat, bytes([0xFF, 0x2F, 0x00])))
    events.sort(key=lambda item: item[0])
    track = bytearray()
    last = 0
    for tick, payload in events:
        track += vlq(tick - last)
        track += payload
        last = tick
    mid = bytearray()
    mid += b"MThd" + struct.pack(">IHHH", 6, 1, 1, ticks_per_beat)
    mid += b"MTrk" + struct.pack(">I", len(track)) + track
    path.write_bytes(mid)


def main() -> None:
    samples = render()
    names = ("HOUSE-LOOP.wav", "HOUSE-LOOP.mid")
    folders = [
        Path.home() / "Documents" / "Context Drops",
        Path.home() / "Desktop",
    ]
    written = []
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
        wav = folder / names[0]
        mid = folder / names[1]
        write_wav(wav, samples)
        write_midi(mid)
        written.extend([wav, mid])
    silent = Path.home() / "Documents" / "Context Drops" / "Context.wav"
    if silent.exists() and silent.stat().st_size == 176444:
        silent.unlink()
    old_mid = Path.home() / "Documents" / "Context Drops" / "Context.mid"
    if old_mid.exists() and old_mid.stat().st_size <= 50:
        old_mid.unlink()
    print("wrote:")
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
