#!/usr/bin/env python3
"""Build the local genre index from Every Noise + MusicBrainz."""

from __future__ import annotations

import csv
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

EVERYNOISE = "https://raw.githubusercontent.com/AyrtonB/EveryNoise-Watch/main/data/genre_attrs.csv"
MUSICBRAINZ = "https://musicbrainz.org/ws/2/genre/all?fmt=txt"
OUT = Path(__file__).resolve().parents[1] / "src" / "context_sidecar" / "data" / "genre_index.json"
USER_AGENT = "ContextSidecar/0.4 (local music tool)"


def _norm(name: str) -> str:
    text = (name or "").lower().replace("&", " and ").replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main() -> None:
    everynoise_raw = _fetch(EVERYNOISE).decode("utf-8", errors="replace")
    musicbrainz_raw = _fetch(MUSICBRAINZ).decode("utf-8", errors="replace")
    everynoise = []
    reader = csv.DictReader(everynoise_raw.splitlines())
    for row in reader:
        name = _norm(row.get("genre") or "")
        if name:
            everynoise.append(name)
    musicbrainz = [_norm(line) for line in musicbrainz_raw.splitlines() if _norm(line)]
    merged = sorted({name for name in [*everynoise, *musicbrainz] if len(name) >= 3}, key=lambda item: (-len(item), item))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "retrieved_at": date.today().isoformat(),
                "sources": [
                    {
                        "name": "Every Noise at Once",
                        "url": "https://everynoise.com/",
                        "via": EVERYNOISE,
                        "count": len(set(everynoise)),
                    },
                    {
                        "name": "MusicBrainz genre taxonomy",
                        "url": MUSICBRAINZ,
                        "count": len(set(musicbrainz)),
                    },
                ],
                "count": len(merged),
                "genres": merged,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {OUT} ({len(merged)} genres)")


if __name__ == "__main__":
    main()
