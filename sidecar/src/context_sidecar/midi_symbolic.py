"""Symbolic MIDI helpers. pretty_midi/music21 are optional."""

from __future__ import annotations

import struct
from typing import Any


def parse_empty_or_notes(path: str) -> dict[str, Any]:
    with open(path, "rb") as handle:
        data = handle.read()
    if not data.startswith(b"MThd"):
        raise ValueError("not a MIDI file")
    return {"file_path": path, "format": struct.unpack(">H", data[8:10])[0], "notes": []}


def humanize_notes(notes: list[dict[str, Any]], amount: float) -> list[dict[str, Any]]:
    shifted = []
    for index, note in enumerate(notes):
        item = dict(note)
        item["start"] = float(note.get("start") or 0) + (0.01 * amount * ((index % 3) - 1))
        item["velocity"] = max(1, min(127, int(note.get("velocity") or 80) + ((index % 5) - 2)))
        shifted.append(item)
    return shifted


def ghost_notes(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extras = []
    for note in notes:
        if int(note.get("velocity") or 0) >= 90:
            extras.append(
                {
                    "pitch": int(note.get("pitch") or 36),
                    "start": float(note.get("start") or 0) - 0.125,
                    "duration": 0.05,
                    "velocity": 30,
                    "ghost": True,
                }
            )
    return notes + extras


def counter_melody(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "pitch": int(note.get("pitch") or 60) + 4,
            "start": float(note.get("start") or 0),
            "duration": float(note.get("duration") or 0.5),
            "velocity": max(1, int(note.get("velocity") or 70) - 20),
            "counter": True,
        }
        for note in notes
    ]
