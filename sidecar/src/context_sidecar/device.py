"""Device chrome contract: fail-closed rules and design-spec copy."""

from __future__ import annotations

from typing import Any

STATUS = {
    "sidecar_down": "Context sidecar is not running on localhost. Start it, then retry.",
    "empty_prompt": "Type what to do next, then run.",
    "apply_success": "Wrote clips into the arrangement. Undo in Live to revert.",
    "apply_failure": "Could not write every clip. Undo in Live if the arrangement looks partial.",
    "empty_source": "Play or select material on this track, or drop a loop.",
    "reference_knobs_disabled": "Load a reference to enable reverence and abstraction.",
}

CHROME_ROWS = (
    "header_health",
    "host_strip",
    "prompt_run",
    "drop_in",
    "reference_reverence_abstraction",
    "granular_row",
    "inspect",
    "preview",
    "audition_apply",
    "status",
)

SCOPES = ("this_track", "selection", "set")
FOCUS_KINDS = ("playhead", "loop", "selected_clip", "host_clip")


def sidecar_healthy(health: dict[str, Any] | None) -> bool:
    return bool(health and health.get("ok") is True)


def prompt_ready(prompt: str) -> bool:
    return bool((prompt or "").strip())


def reference_knobs_enabled(reference_path: str) -> bool:
    return bool((reference_path or "").strip())


def can_run(*, health: dict[str, Any] | None, prompt: str) -> bool:
    return sidecar_healthy(health) and prompt_ready(prompt)


def can_apply(*, health: dict[str, Any] | None, has_preview: bool) -> bool:
    return sidecar_healthy(health) and has_preview


def can_audition(*, has_preview: bool) -> bool:
    return has_preview


def status_for(*, health: dict[str, Any] | None, prompt: str, has_preview: bool) -> str:
    if not sidecar_healthy(health):
        return STATUS["sidecar_down"]
    if not prompt_ready(prompt):
        return STATUS["empty_prompt"]
    if not has_preview:
        return "Type what to do next, then run."
    return "Preview ready. Audition stays in-device. Apply writes."


def default_chrome_state() -> dict[str, Any]:
    return {
        "rows": list(CHROME_ROWS),
        "scope": "this_track",
        "focus": "host_clip",
        "knobs": {
            "reverence": 0.5,
            "abstraction": 0.5,
        },
        "tempo_key_lock": True,
        "variation": False,
        "locks": [],
        "target_section": None,
        "drop_in_path": "",
        "reference_path": "",
        "audition_writes": False,
    }
