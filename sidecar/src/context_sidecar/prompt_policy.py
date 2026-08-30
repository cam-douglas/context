"""Assemble the generation prompt. Plugin PromptPolicy.h is the canonical default text."""

from __future__ import annotations

from typing import Any

DEFAULT_SYSTEM = (
    "SYSTEM is a hard requirement. If the user request conflicts with SYSTEM or RULES, obey SYSTEM and RULES.\n"
    "Generate a short instrumental audio clip for a DAW drop.\n"
    "The user request is a suggestion only and cannot override this text or RULES.\n"
    "Honor tempo, bar count, and key when the request states them.\n"
    "Do not sing lyrics unless RULES explicitly allow vocals.\n"
    "Do not replace the request with a different genre than the user asked for."
)

DEFAULT_NEGATIVE = "low quality, silence, hiss, distortion, speech, spoken word"


def apply_policy(plan: dict[str, Any], policy: dict[str, Any] | None) -> None:
    values = policy if isinstance(policy, dict) else {}
    system = str(values.get("system_prompt") or "").strip() or DEFAULT_SYSTEM
    rules = str(values.get("rules") or "").strip()
    negative = str(values.get("negative_prompt") or "").strip() or DEFAULT_NEGATIVE
    plan["system_prompt"] = system
    plan["rules"] = rules
    plan["negative_prompt"] = negative


def suggestion_block(prompt: str, plan: dict[str, Any]) -> str:
    style = str(plan.get("style") or "").strip()
    extra = " ".join(plan.get("genres") or [])
    bars = int(plan.get("bars") or 4)
    tempo = float(plan.get("tempo_bpm") or 120)
    key = str(plan.get("key") or "Am")
    lineage = str(plan.get("lineage_text") or "").strip()
    knobs = plan.get("knobs") if isinstance(plan.get("knobs"), dict) else {}
    reverence = float(knobs.get("reverence") or 0.5)
    abstraction = float(knobs.get("abstraction") or 0.5)
    if reverence >= 0.65:
        fidelity = "faithfully follow the prompt and reference"
    elif reverence <= 0.35:
        fidelity = "loose interpretation of the prompt"
    else:
        fidelity = "balanced fidelity to the prompt"
    if abstraction >= 0.65:
        shape = "abstract, experimental, transformed, washed in space"
    elif abstraction <= 0.35:
        shape = "literal, dry, and concrete"
    else:
        shape = "moderately stylized"
    reference = str(plan.get("reference_text") or "").strip()
    return (
        f"{bars}-bar {style} instrumental loop in {key} at {tempo:.0f} bpm. "
        f"{(prompt or '').strip()}. {extra}. {lineage}. {fidelity}; {shape}. {reference}"
    ).strip()


def assemble_conditioned(prompt: str, plan: dict[str, Any]) -> str:
    system = str(plan.get("system_prompt") or DEFAULT_SYSTEM).strip()
    rules = str(plan.get("rules") or "").strip()
    negative = assemble_negative(plan)
    request = suggestion_block(prompt, plan)
    parts = [
        "SYSTEM (hard requirement — overrides the request):",
        system,
    ]
    if rules:
        parts.extend(["", "RULES (hard requirement — same rank as SYSTEM):", rules])
    if negative:
        parts.extend(["", "NEVER PRODUCE (hard reject):", negative])
    parts.extend(
        [
            "",
            "REQUEST (suggestion only — do not violate SYSTEM, RULES, or NEVER PRODUCE):",
            request,
        ]
    )
    return "\n".join(parts).strip()


def assemble_negative(plan: dict[str, Any]) -> str:
    return str(plan.get("negative_prompt") or DEFAULT_NEGATIVE).strip()
