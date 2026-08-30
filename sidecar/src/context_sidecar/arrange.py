"""Loop-to-song arrangement planner. Does not write Live."""

from __future__ import annotations

from typing import Any

from context_sidecar.schema import SCHEMA_VERSION, validate_arrangement

GENRE_DEFAULTS = {
    "melodic techno": {"bars": 96, "sections": ("intro", "verse", "build", "drop", "outro")},
    "pop": {"bars": 80, "sections": ("intro", "verse", "chorus", "verse", "chorus", "outro")},
}


def loop_to_song(
    *,
    genre_target: str = "melodic techno",
    loop_bars: int = 8,
    tempo_bpm: float = 124,
    musical_key: str = "Am",
    source_kind: str = "audio",
    source_path: str = "",
) -> dict[str, Any]:
    genre = (genre_target or "melodic techno").strip().lower()
    preset = GENRE_DEFAULTS.get(genre, GENRE_DEFAULTS["melodic techno"])
    beats_per_bar = 4
    cursor = 0.0
    sections = []
    for index, label in enumerate(preset["sections"]):
        length_bars = 16 if label in {"drop", "chorus", "verse"} else 8
        if label == "build":
            length_bars = 8
        length = length_bars * beats_per_bar
        sections.append(
            {
                "id": f"{label}-{index}",
                "label": label if label != "chorus" else "chorus",
                "start_beats": cursor,
                "length_beats": length,
                "energy": 0.2 + 0.15 * index,
                "density": 0.2 + 0.12 * index,
                "velocity": 70 + 6 * index,
            }
        )
        cursor += length
    track_kind = "audio" if source_kind == "audio" else "midi"
    clip: dict[str, Any] = {
        "id": "loop-0",
        "kind": track_kind,
        "start_beats": 0,
        "length_beats": loop_bars * beats_per_bar,
    }
    if track_kind == "audio":
        clip["file_path"] = source_path or "live://loop"
    else:
        clip["notes"] = []
    plan = {
        "schema_version": SCHEMA_VERSION,
        "tempo_bpm": tempo_bpm,
        "musical_key": musical_key,
        "time_signature": [4, 4],
        "sections": [
            {key: section[key] for key in ("id", "label", "start_beats", "length_beats")}
            for section in sections
        ],
        "tracks": [
            {
                "id": "arrangement",
                "name": "Arrangement",
                "kind": track_kind,
                "clips": [clip],
            }
        ],
        "automation": [
            {"target": "volume", "start_beats": 0, "end_beats": 16, "from": 0.0, "to": 0.8},
            {"target": "filter", "start_beats": 48, "end_beats": 64, "from": 0.2, "to": 1.0},
        ],
        "locators": [
            {"name": section["label"], "beats": section["start_beats"]} for section in sections
        ],
        "colors": {"arrangement": "#7C5CFF"},
        "meta": {"genre_target": genre, "loop_bars": loop_bars, "sections_detail": sections},
    }
    validate_arrangement(
        {
            "schema_version": plan["schema_version"],
            "tempo_bpm": plan["tempo_bpm"],
            "musical_key": plan["musical_key"],
            "time_signature": plan["time_signature"],
            "sections": plan["sections"],
            "tracks": plan["tracks"],
        }
    )
    return plan
