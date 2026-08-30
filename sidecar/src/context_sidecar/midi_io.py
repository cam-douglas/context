"""MIDI write via mido, with pretty_midi then stdlib fallbacks."""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any


def program_and_drums(plan: dict[str, Any]) -> tuple[int, bool]:
    style = str(plan.get("style") or "")
    family = str(plan.get("family") or style)
    drums = style in {"drums", "house", "techno", "trap", "dnb"} or family in {
        "drums",
        "house",
        "techno",
        "trap",
        "dnb",
    }
    program = 38 if style == "bass" or family == "bass" else 0
    return program, drums


def write_midi(plan: dict[str, Any], notes: list[dict[str, Any]], dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        return _write_midi_mido(plan, notes, dest)
    except Exception:
        pass
    try:
        return _write_midi_pretty_midi(plan, notes, dest)
    except Exception:
        return _write_midi_stdlib(plan, notes, dest)


def _write_midi_mido(plan: dict[str, Any], notes: list[dict[str, Any]], dest: Path) -> str:
    from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

    ticks = 480
    program, drums = program_and_drums(plan)
    channel = 9 if drums else 0
    mid = MidiFile(type=1, ticks_per_beat=ticks)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(float(plan["tempo_bpm"])), time=0))
    track.append(MetaMessage("track_name", name=str(plan.get("style") or "context")[:32], time=0))
    track.append(Message("program_change", program=program, channel=channel, time=0))

    events: list[tuple[int, int, int, int]] = []
    for note in notes:
        start = int(round(float(note["start"]) * ticks))
        end = int(round((float(note["start"]) + float(note["length"])) * ticks))
        if end <= start:
            end = start + 1
        pitch = max(0, min(127, int(note["pitch"])))
        velocity = max(1, min(127, int(note.get("velocity") or 100)))
        events.append((start, 1, pitch, velocity))
        events.append((end, 0, pitch, 0))
    events.sort()
    last = 0
    for tick, kind, pitch, velocity in events:
        delta = max(0, tick - last)
        name = "note_on" if kind == 1 else "note_off"
        track.append(Message(name, note=pitch, velocity=velocity, channel=channel, time=delta))
        last = tick
    mid.save(str(dest))
    return "mido"


def _write_midi_pretty_midi(plan: dict[str, Any], notes: list[dict[str, Any]], dest: Path) -> str:
    import pretty_midi

    tempo = float(plan["tempo_bpm"])
    program, drums = program_and_drums(plan)
    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    instrument = pretty_midi.Instrument(program=program, is_drum=drums)
    for note in notes:
        start = float(note["start"]) * 60.0 / tempo
        end = start + float(note["length"]) * 60.0 / tempo
        instrument.notes.append(
            pretty_midi.Note(
                velocity=max(1, min(127, int(note.get("velocity") or 100))),
                pitch=int(note["pitch"]),
                start=start,
                end=max(start + 0.03, end),
            )
        )
    midi.instruments.append(instrument)
    midi.write(str(dest))
    return "pretty_midi"


def _write_midi_stdlib(plan: dict[str, Any], notes: list[dict[str, Any]], dest: Path) -> str:
    def vlq(value: int) -> bytes:
        parts = [value & 0x7F]
        value >>= 7
        while value:
            parts.append(0x80 | (value & 0x7F))
            value >>= 7
        return bytes(reversed(parts))

    tempo = int(60_000_000 / float(plan["tempo_bpm"]))
    ticks = 480
    events: list[tuple[int, bytes]] = [
        (0, bytes([0xFF, 0x51, 0x03, (tempo >> 16) & 0xFF, (tempo >> 8) & 0xFF, tempo & 0xFF])),
        (0, bytes([0xFF, 0x03, len(str(plan["style"]))]) + str(plan["style"]).encode("ascii")),
    ]
    for note in notes:
        start = int(float(note["start"]) * ticks)
        end = int((float(note["start"]) + float(note["length"])) * ticks)
        pitch = int(note["pitch"])
        vel = int(note.get("velocity") or 100)
        events.append((start, bytes([0x90, pitch, vel])))
        events.append((end, bytes([0x80, pitch, 0])))
    events.sort(key=lambda item: item[0])
    events.append((events[-1][0] if events else 0, bytes([0xFF, 0x2F, 0x00])))
    track = bytearray()
    last = 0
    for tick, payload in events:
        track += vlq(max(0, tick - last))
        track += payload
        last = tick
    dest.write_bytes(b"MThd" + struct.pack(">IHHH", 6, 1, 1, ticks) + b"MTrk" + struct.pack(">I", len(track)) + track)
    return "stdlib"
