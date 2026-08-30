"""Prompt, project snapshot, and knob contract for Context."""

from __future__ import annotations

from typing import Any

from context_sidecar.schema import SCHEMA_VERSION, SchemaError, _require, _validate_track

INTENT_MODES = ("track_follow", "drop_in", "reference", "project")
SCOPES = ("this_track", "selection", "set")
FOCUS_KINDS = ("playhead", "loop", "selected_clip", "host_clip")
TRACK_ROLES = (
    "drums",
    "bass",
    "harmony",
    "lead",
    "vocal",
    "fx",
    "ambient",
    "other",
)
KNOB_NAMES = ("reverence", "abstraction")


def _optional(mapping: dict[str, Any], key: str) -> Any:
    return mapping.get(key)


def _require_unit_interval(mapping: dict[str, Any], key: str) -> float:
    value = _require(mapping, key, (int, float))
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise SchemaError(f"{key} must be between 0 and 1")
    return number


def _require_nonempty_path(mapping: dict[str, Any], key: str) -> str:
    path = _require(mapping, key, str).strip()
    if not path:
        raise SchemaError(f"{key} must be a non-empty string")
    return path


def validate_project_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise SchemaError("project must be an object")
    _require(snapshot, "tempo_bpm", (int, float))
    _require(snapshot, "musical_key", str)
    tracks = _require(snapshot, "tracks", list)
    if not tracks:
        raise SchemaError("project.tracks must not be empty")
    for track in tracks:
        _validate_track(track)
        if "inferred_role" in track and track["inferred_role"] not in TRACK_ROLES:
            raise SchemaError("unknown inferred_role")
    playhead = _require(snapshot, "playhead_beats", (int, float))
    if playhead < 0:
        raise SchemaError("playhead_beats invalid")
    return snapshot


def validate_intent(intent: dict[str, Any]) -> dict[str, Any]:
    """Validate a user intent. Raises SchemaError on failure."""
    if not isinstance(intent, dict):
        raise SchemaError("intent must be an object")

    version = _require(intent, "schema_version", int)
    if version != SCHEMA_VERSION:
        raise SchemaError(f"unsupported schema_version {version}")

    prompt = _require(intent, "prompt", str).strip()
    if not prompt:
        raise SchemaError("prompt must not be empty")

    mode = _require(intent, "mode", str)
    if mode not in INTENT_MODES:
        raise SchemaError(f"unknown mode {mode}")

    scope = _require(intent, "scope", str)
    if scope not in SCOPES:
        raise SchemaError(f"unknown scope {scope}")

    knobs = _require(intent, "knobs", dict)
    for name in KNOB_NAMES:
        _require_unit_interval(knobs, name)

    host = _require(intent, "host_track", dict)
    _require(host, "id", str)
    _require(host, "name", str)
    role = _require(host, "inferred_role", str)
    if role not in TRACK_ROLES:
        raise SchemaError("unknown host_track.inferred_role")

    validate_project_snapshot(_require(intent, "project", dict))

    focus = _require(intent, "focus", dict)
    kind = _require(focus, "kind", str)
    if kind not in FOCUS_KINDS:
        raise SchemaError(f"unknown focus.kind {kind}")

    locks = _require(intent, "locks", list)
    if not all(isinstance(item, str) and item for item in locks):
        raise SchemaError("locks must be a list of non-empty strings")

    if mode == "drop_in":
        drop_in = _require(intent, "drop_in", dict)
        _require_nonempty_path(drop_in, "file_path")
    elif "drop_in" in intent and intent["drop_in"] is not None:
        raise SchemaError("drop_in is only valid in drop_in mode")

    if mode == "reference":
        reference = _require(intent, "reference", dict)
        _require_nonempty_path(reference, "file_path")
    elif "reference" in intent and intent["reference"] is not None:
        raise SchemaError("reference is only valid in reference mode")

    target = _optional(intent, "target_section")
    if target is not None and not isinstance(target, str):
        raise SchemaError("target_section must be a string")

    genre = _optional(intent, "genre_target")
    if genre is not None and not isinstance(genre, str):
        raise SchemaError("genre_target must be a string")

    return intent


def empty_intent(
    *,
    prompt: str = "expand on this riff",
    mode: str = "track_follow",
) -> dict[str, Any]:
    intent: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "prompt": prompt,
        "mode": mode,
        "scope": "this_track",
        "host_track": {
            "id": "track-0",
            "name": "Drums",
            "inferred_role": "drums",
        },
        "project": {
            "tempo_bpm": 120,
            "musical_key": "Am",
            "playhead_beats": 0,
            "tracks": [
                {
                    "id": "track-0",
                    "name": "Drums",
                    "kind": "midi",
                    "inferred_role": "drums",
                    "clips": [
                        {
                            "id": "clip-0",
                            "kind": "midi",
                            "start_beats": 0,
                            "length_beats": 16,
                            "notes": [],
                        }
                    ],
                }
            ],
        },
        "knobs": {
            "reverence": 0.5,
            "abstraction": 0.5,
        },
        "focus": {"kind": "host_clip"},
        "locks": [],
        "tempo_key_lock": True,
        "variation": False,
        "target_section": None,
    }
    if mode == "drop_in":
        intent["drop_in"] = {"file_path": "/tmp/drop-in.wav"}
    if mode == "reference":
        intent["reference"] = {"file_path": "/tmp/reference.wav"}
    return intent
