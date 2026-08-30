"""Arrangement schema for Context. Hosts (Max for Live, later VST3/AU) share this contract."""

from __future__ import annotations

from typing import Any, Literal

SCHEMA_VERSION = 1
CLIP_KINDS = ("audio", "midi")
SECTION_LABELS = (
    "intro",
    "verse",
    "chorus",
    "break",
    "bridge",
    "build",
    "drop",
    "outro",
    "other",
)


class SchemaError(ValueError):
    pass


def _require(mapping: dict[str, Any], key: str, expected: type | tuple[type, ...]) -> Any:
    if key not in mapping:
        raise SchemaError(f"missing {key}")
    value = mapping[key]
    if not isinstance(value, expected):
        label = (
            expected.__name__
            if isinstance(expected, type)
            else " or ".join(item.__name__ for item in expected)
        )
        raise SchemaError(f"{key} must be {label}")
    return value


def validate_arrangement(plan: dict[str, Any]) -> dict[str, Any]:
    """Validate and return the arrangement plan. Raises SchemaError on failure."""
    if not isinstance(plan, dict):
        raise SchemaError("arrangement must be an object")

    version = _require(plan, "schema_version", int)
    if version != SCHEMA_VERSION:
        raise SchemaError(f"unsupported schema_version {version}")

    tempo = _require(plan, "tempo_bpm", (int, float))
    if not 20 <= float(tempo) <= 400:
        raise SchemaError("tempo_bpm out of range")

    _require(plan, "musical_key", str)
    signature = _require(plan, "time_signature", list)
    if len(signature) != 2 or not all(isinstance(part, int) and part > 0 for part in signature):
        raise SchemaError("time_signature must be [numerator, denominator]")

    sections = _require(plan, "sections", list)
    if not sections:
        raise SchemaError("sections must not be empty")
    for section in sections:
        _validate_section(section)

    tracks = _require(plan, "tracks", list)
    if not tracks:
        raise SchemaError("tracks must not be empty")
    for track in tracks:
        _validate_track(track)

    return plan


def _validate_section(section: Any) -> None:
    if not isinstance(section, dict):
        raise SchemaError("section must be an object")
    _require(section, "id", str)
    label = _require(section, "label", str)
    if label not in SECTION_LABELS:
        raise SchemaError(f"unknown section label {label}")
    start = _require(section, "start_beats", (int, float))
    length = _require(section, "length_beats", (int, float))
    if start < 0 or length <= 0:
        raise SchemaError("section timing invalid")


def _validate_track(track: Any) -> None:
    if not isinstance(track, dict):
        raise SchemaError("track must be an object")
    _require(track, "id", str)
    _require(track, "name", str)
    kind = _require(track, "kind", str)
    if kind not in CLIP_KINDS:
        raise SchemaError(f"unknown track kind {kind}")
    clips = _require(track, "clips", list)
    for clip in clips:
        _validate_clip(clip, kind)


def _validate_clip(clip: Any, track_kind: str) -> None:
    if not isinstance(clip, dict):
        raise SchemaError("clip must be an object")
    _require(clip, "id", str)
    kind: Literal["audio", "midi"] = _require(clip, "kind", str)
    if kind != track_kind:
        raise SchemaError("clip kind must match track kind")
    start = _require(clip, "start_beats", (int, float))
    length = _require(clip, "length_beats", (int, float))
    if start < 0 or length <= 0:
        raise SchemaError("clip timing invalid")
    if kind == "audio" and "file_path" not in clip:
        raise SchemaError("audio clip requires file_path")
    if kind == "midi" and "notes" not in clip:
        raise SchemaError("midi clip requires notes")


def empty_arrangement(
    *,
    tempo_bpm: float = 120,
    musical_key: str = "C",
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "tempo_bpm": tempo_bpm,
        "musical_key": musical_key,
        "time_signature": [4, 4],
        "sections": [
            {
                "id": "intro",
                "label": "intro",
                "start_beats": 0,
                "length_beats": 16,
            }
        ],
        "tracks": [
            {
                "id": "sketch",
                "name": "Sketch",
                "kind": "midi",
                "clips": [
                    {
                        "id": "sketch-1",
                        "kind": "midi",
                        "start_beats": 0,
                        "length_beats": 16,
                        "notes": [],
                    }
                ],
            }
        ],
    }
