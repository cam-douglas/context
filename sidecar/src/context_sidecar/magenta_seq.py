"""Magenta NoteSequence quantize via note-seq. No TF models, no stand-in audio."""

from __future__ import annotations

from typing import Any

from context_sidecar.midi_io import program_and_drums


def quantize_notes(plan: dict[str, Any], notes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    if not notes:
        return notes, "none"
    try:
        import note_seq
        from note_seq.protobuf import music_pb2
    except Exception:
        return notes, "none"

    tempo = max(40.0, float(plan["tempo_bpm"]))
    seconds_per_beat = 60.0 / tempo
    program, drums = program_and_drums(plan)
    sequence = music_pb2.NoteSequence()
    sequence.tempos.add(qpm=tempo)
    sequence.ticks_per_quarter = 480
    total = 0.0
    for note in notes:
        item = sequence.notes.add()
        item.pitch = max(0, min(127, int(note["pitch"])))
        item.velocity = max(1, min(127, int(note.get("velocity") or 100)))
        item.start_time = max(0.0, float(note["start"]) * seconds_per_beat)
        item.end_time = item.start_time + max(0.03, float(note["length"]) * seconds_per_beat)
        item.program = program
        item.is_drum = drums
        total = max(total, item.end_time)
    sequence.total_time = total
    try:
        quantized = note_seq.quantize_note_sequence(sequence, steps_per_quarter=4)
    except Exception:
        return notes, "none"

    steps = int(quantized.quantization_info.steps_per_quarter or 4)
    snapped: list[dict[str, Any]] = []
    for item in quantized.notes:
        start = float(item.quantized_start_step) / steps
        length = max(0.05, float(item.quantized_end_step - item.quantized_start_step) / steps)
        snapped.append(
            {
                "pitch": int(item.pitch),
                "start": start,
                "length": length,
                "velocity": int(item.velocity),
            }
        )
    return snapped or notes, "note_seq"
