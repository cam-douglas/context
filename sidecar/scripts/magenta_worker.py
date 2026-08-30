"""Run MelodyRNN / MusicVAE in the isolated TensorFlow venv. JSON stdin → JSON stdout."""

from __future__ import annotations

import os

os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

np.bool = getattr(np, "bool_", bool)  # Magenta 2.1.4 MusicVAE still uses removed np.bool


def _sequence_to_notes(sequence: Any, tempo_bpm: float) -> list[dict[str, Any]]:
    seconds_per_beat = 60.0 / max(40.0, float(tempo_bpm))
    notes: list[dict[str, Any]] = []
    for item in sequence.notes:
        start = float(item.start_time) / seconds_per_beat
        length = max(0.05, (float(item.end_time) - float(item.start_time)) / seconds_per_beat)
        notes.append(
            {
                "pitch": int(item.pitch),
                "start": start,
                "length": length,
                "velocity": int(item.velocity or 100),
            }
        )
    return notes


def _tile(notes: list[dict[str, Any]], bars: int, cell_bars: int) -> list[dict[str, Any]]:
    copies = max(1, int(bars) // max(1, int(cell_bars)))
    if copies <= 1:
        return notes
    tiled: list[dict[str, Any]] = []
    width = float(cell_bars) * 4.0
    for index in range(copies):
        shift = index * width
        for note in notes:
            tiled.append({**note, "start": float(note["start"]) + shift})
    return tiled


def _melody_rnn(req: dict[str, Any]) -> dict[str, Any]:
    from magenta.models.melody_rnn import melody_rnn_sequence_generator
    from magenta.models.shared import sequence_generator_bundle
    from note_seq.protobuf import generator_pb2, music_pb2

    bundle_path = Path(req["bundle"])
    if not bundle_path.is_file():
        return {"ok": False, "error": "melody_rnn_bundle_missing", "path": str(bundle_path)}

    tempo = float(req.get("tempo_bpm") or 120)
    bars = max(1, int(req.get("bars") or 4))
    primer = [int(pitch) for pitch in (req.get("primer") or [60]) if 0 <= int(pitch) <= 127]
    if not primer:
        primer = [60]

    bundle = sequence_generator_bundle.read_bundle_file(str(bundle_path))
    generator_map = melody_rnn_sequence_generator.get_generator_map()
    generator = generator_map["attention_rnn"](checkpoint=None, bundle=bundle)
    generator.initialize()

    primer_seq = music_pb2.NoteSequence()
    primer_seq.tempos.add(qpm=tempo)
    cursor = 0.0
    step = 60.0 / tempo / 2.0
    for pitch in primer[:4]:
        note = primer_seq.notes.add()
        note.pitch = pitch
        note.velocity = 100
        note.start_time = cursor
        note.end_time = cursor + step
        cursor = note.end_time
    primer_seq.total_time = cursor

    seconds = bars * 4.0 * 60.0 / tempo
    options = generator_pb2.GeneratorOptions()
    options.args["temperature"].float_value = float(req.get("temperature") or 1.0)
    section = options.generate_sections.add()
    section.start_time = primer_seq.total_time
    section.end_time = max(primer_seq.total_time + 0.5, seconds)

    sequence = generator.generate(primer_seq, options)
    return {"ok": True, "backend": "melody_rnn", "notes": _sequence_to_notes(sequence, tempo)}


def _music_vae(req: dict[str, Any]) -> dict[str, Any]:
    from magenta.models.music_vae import configs, trained_model

    checkpoint = Path(req["checkpoint"])
    if not checkpoint.is_file() and not checkpoint.is_dir():
        return {"ok": False, "error": "music_vae_checkpoint_missing", "path": str(checkpoint)}

    config_id = str(req.get("config") or "cat-mel_2bar_big")
    if config_id not in configs.CONFIG_MAP:
        return {"ok": False, "error": "music_vae_config_unknown", "config": config_id}

    tempo = float(req.get("tempo_bpm") or 120)
    bars = max(1, int(req.get("bars") or 4))
    model = trained_model.TrainedModel(
        configs.CONFIG_MAP[config_id],
        batch_size=1,
        checkpoint_dir_or_path=str(checkpoint),
    )
    samples = model.sample(n=1, length=32, temperature=float(req.get("temperature") or 0.5))
    if not samples:
        return {"ok": False, "error": "music_vae_empty"}
    notes = _sequence_to_notes(samples[0], tempo)
    return {
        "ok": True,
        "backend": "music_vae",
        "config": config_id,
        "notes": _tile(notes, bars, 2),
    }


def main() -> int:
    req = json.loads(sys.stdin.read() or "{}")
    model = str(req.get("model") or "")
    try:
        if model == "melody_rnn":
            result = _melody_rnn(req)
        elif model == "music_vae":
            result = _music_vae(req)
        else:
            result = {"ok": False, "error": f"unknown_model:{model}"}
    except Exception as exc:
        result = {"ok": False, "error": f"{exc.__class__.__name__}:{exc}"}
    sys.stdout.write(json.dumps(result))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
