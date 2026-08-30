"""Build a ProjectSnapshot plus host_track from a Live-set dictionary."""

from __future__ import annotations

from typing import Any

from context_sidecar.roles import infer_role


def _clip_from_live(raw: dict[str, Any], track_kind: str, index: int) -> dict[str, Any]:
    clip: dict[str, Any] = {
        "id": str(raw.get("id") or f"clip-{index}"),
        "kind": track_kind,
        "start_beats": float(raw.get("start_beats") or 0),
        "length_beats": float(raw.get("length_beats") or 4),
    }
    if track_kind == "audio":
        clip["file_path"] = str(raw.get("file_path") or raw.get("file_path_placeholder") or "live://clip")
    else:
        clip["notes"] = list(raw.get("notes") or [])
    return clip


def _track_from_live(raw: dict[str, Any], index: int) -> dict[str, Any]:
    name = str(raw.get("name") or f"Track {index}")
    kind = "midi" if raw.get("has_midi_input") else "audio"
    if raw.get("kind") in ("audio", "midi"):
        kind = raw["kind"]
    clips = [
        _clip_from_live(clip, kind, clip_index)
        for clip_index, clip in enumerate(raw.get("clips") or [])
    ]
    return {
        "id": str(raw.get("id") or f"track-{index}"),
        "name": name,
        "kind": kind,
        "inferred_role": infer_role(name),
        "clips": clips,
        "frozen": bool(raw.get("frozen")),
        "locked": bool(raw.get("locked")),
    }


def build_project_snapshot(live_set: dict[str, Any], *, host_track_id: str | None = None) -> dict[str, Any]:
    tracks = [_track_from_live(track, index) for index, track in enumerate(live_set.get("tracks") or [])]
    if not tracks:
        raise ValueError("live_set.tracks must not be empty")
    host = None
    if host_track_id:
        host = next((track for track in tracks if track["id"] == host_track_id), None)
    if host is None:
        host = tracks[0]
    return {
        "project": {
            "tempo_bpm": float(live_set.get("tempo_bpm") or 120),
            "musical_key": str(live_set.get("musical_key") or ""),
            "playhead_beats": float(live_set.get("playhead_beats") or 0),
            "tracks": [
                {
                    "id": track["id"],
                    "name": track["name"],
                    "kind": track["kind"],
                    "inferred_role": track["inferred_role"],
                    "clips": [
                        {key: value for key, value in clip.items() if key != "frozen"}
                        for clip in track["clips"]
                    ],
                }
                for track in tracks
            ],
        },
        "host_track": {
            "id": host["id"],
            "name": host["name"],
            "inferred_role": host["inferred_role"],
        },
    }
