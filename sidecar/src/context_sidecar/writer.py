"""Decide which Live tracks receive writes. Session files go through export.py."""

from __future__ import annotations

from typing import Any


def _unlocked(track: dict[str, Any]) -> bool:
    return not track.get("frozen") and not track.get("locked")


def select_write_targets(tracks: list[dict[str, Any]]) -> dict[str, Any]:
    audio = next((track for track in tracks if track.get("kind") == "audio" and _unlocked(track)), None)
    midi = next((track for track in tracks if track.get("kind") == "midi" and _unlocked(track)), None)
    return {"audio": audio, "midi": midi}


def apply_plan(
    *,
    sidecar_ok: bool,
    prompt: str,
    tracks: list[dict[str, Any]],
    audio_path: str,
    position_beats: float = 0.0,
    midi_start_beats: float = 0.0,
    midi_length_beats: float = 4.0,
) -> dict[str, Any]:
    if not sidecar_ok:
        return {"ok": False, "wrote": False, "error": "sidecar_down", "actions": []}
    if not (prompt or "").strip():
        return {"ok": False, "wrote": False, "error": "empty_prompt", "actions": []}
    targets = select_write_targets(tracks)
    if not targets["audio"] or not targets["midi"]:
        return {
            "ok": False,
            "wrote": False,
            "error": "need_unlocked_audio_and_midi_tracks",
            "actions": [],
        }
    actions = [
        {
            "method": "create_audio_clip",
            "track_id": targets["audio"]["id"],
            "file_path": audio_path,
            "position": position_beats,
        },
        {
            "method": "create_midi_clip",
            "track_id": targets["midi"]["id"],
            "start": midi_start_beats,
            "length": midi_length_beats,
        },
    ]
    return {
        "ok": True,
        "wrote": True,
        "error": None,
        "actions": actions,
        "undo_hint": "Wrote clips into the arrangement. Undo in Live to revert.",
    }


def arrangement_write_actions(plan: dict[str, Any], locks: list[str]) -> list[dict[str, Any]]:
    locked = set(locks or [])
    actions: list[dict[str, Any]] = []
    for locator in plan.get("locators") or []:
        actions.append({"method": "set_or_create_locator", "name": locator["name"], "beats": locator["beats"]})
    for track in plan.get("tracks") or []:
        if track.get("id") in locked:
            continue
        color = (plan.get("colors") or {}).get(track["id"])
        if color:
            actions.append({"method": "set_track_color", "track_id": track["id"], "color": color})
        for clip in track.get("clips") or []:
            if clip.get("id") in locked:
                continue
            if clip.get("kind") == "audio":
                actions.append(
                    {
                        "method": "create_audio_clip",
                        "track_id": track["id"],
                        "file_path": clip.get("file_path"),
                        "position": clip.get("start_beats"),
                    }
                )
            else:
                actions.append(
                    {
                        "method": "create_midi_clip",
                        "track_id": track["id"],
                        "start": clip.get("start_beats"),
                        "length": clip.get("length_beats"),
                    }
                )
    for move in plan.get("automation") or []:
        actions.append({"method": "create_automation", **move})
    return actions
