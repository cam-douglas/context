"""Infer a host-track role from a Live track name (P-8)."""

from __future__ import annotations

ROLE_TOKENS = (
    ("drums", ("drum", "drums", "kit", "kick", "perc", "beat")),
    ("bass", ("bass", "808", "sub")),
    ("vocal", ("vocal", "vox", "voice", "lead vox")),
    ("lead", ("lead", "synth lead", "melody")),
    ("harmony", ("harm", "pad", "chord", "keys", "piano", "guitar")),
    ("fx", ("fx", "riser", "sweep", "impact", "transition")),
    ("ambient", ("ambient", "atm", "texture", "drone")),
)


def infer_role(name: str) -> str:
    lowered = (name or "").strip().lower()
    if not lowered:
        return "other"
    for role, tokens in ROLE_TOKENS:
        if any(token in lowered for token in tokens):
            return role
    return "other"
