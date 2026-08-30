"""Read-only frequency masking audit. Does not apply EQ."""

from __future__ import annotations

from typing import Any

from context_sidecar.analysis import analyze_audio


def audit_stems(stems: dict[str, str], *, mud_threshold: float = 0.002) -> dict[str, Any]:
    reports = {name: analyze_audio(path) for name, path in stems.items() if path}
    hits: list[dict[str, Any]] = []
    names = list(reports)
    for left in range(len(names)):
        for right in range(left + 1, len(names)):
            a = names[left]
            b = names[right]
            mud = min(reports[a]["bands"]["mud"], reports[b]["bands"]["mud"])
            pair = {a.lower(), b.lower()}
            named_mud = bool({"kick", "bass"} & pair) and bool({"kick", "bass", "drums"} & pair)
            if mud >= mud_threshold or named_mud:
                hits.append(
                    {
                        "kind": "masking",
                        "stems": [a, b],
                        "hz": 250,
                        "band": "mud",
                        "note": f"Possible overlap near 250 Hz between {a} and {b}. Carve one.",
                        "suggested_carve_db": 3.0,
                    }
                )
    return {"ok": True, "wrote": False, "hits": hits, "reports": reports}
