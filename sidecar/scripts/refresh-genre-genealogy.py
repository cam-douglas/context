#!/usr/bin/env python3
"""Refresh the open Wikidata genre genealogy. Does not use musicmap.info."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "src" / "context_sidecar" / "data" / "genre_genealogy.json"
UA = "ContextSidecar/0.4 (local; wikidata genealogy)"
ENDPOINT = "https://query.wikidata.org/sparql"
PARENT_QUERY = """SELECT DISTINCT ?genreLabel ?parentLabel ?year WHERE {
  ?genre wdt:P31/wdt:P279* wd:Q188451 .
  OPTIONAL { ?genre wdt:P279 ?parent . }
  OPTIONAL { ?genre wdt:P571 ?inception . BIND(YEAR(?inception) AS ?year) }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 3000 OFFSET %s"""
INFLUENCE_QUERY = """SELECT DISTINCT ?genreLabel ?influenceLabel WHERE {
  ?genre wdt:P31/wdt:P279* wd:Q188451 .
  ?genre wdt:P737 ?influence .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""


def _norm(name: str) -> str:
    text = (name or "").lower().replace("&", " and ").replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _fetch(query: str) -> list[dict]:
    url = ENDPOINT + "?" + urllib.parse.urlencode({"format": "json", "query": query})
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = json.loads(response.read().decode())
    return payload["results"]["bindings"]


def _val(row: dict, key: str) -> str:
    return ((row.get(key) or {}).get("value") or "").strip()


def main() -> None:
    parent_rows: list[dict] = []
    for offset in range(0, 18000, 3000):
        rows = _fetch(PARENT_QUERY % offset)
        parent_rows.extend(rows)
        if len(rows) < 3000:
            break
    influence_rows = _fetch(INFLUENCE_QUERY)
    graph: dict[str, dict] = {}
    for row in parent_rows:
        genre = _norm(_val(row, "genreLabel"))
        if len(genre) < 3:
            continue
        node = graph.setdefault(genre, {"parents": [], "influences": [], "year": None})
        parent = _norm(_val(row, "parentLabel"))
        if parent and parent != genre and parent not in node["parents"] and len(parent) >= 3:
            node["parents"].append(parent)
        year = _val(row, "year")
        if year.isdigit() and node["year"] is None:
            year_i = int(year)
            if 1600 <= year_i <= 2026:
                node["year"] = year_i
    for row in influence_rows:
        genre = _norm(_val(row, "genreLabel"))
        if len(genre) < 3:
            continue
        node = graph.setdefault(genre, {"parents": [], "influences": [], "year": None})
        influence = _norm(_val(row, "influenceLabel"))
        if influence and influence != genre and influence not in node["influences"] and len(influence) >= 3:
            node["influences"].append(influence)
    compact = {}
    for name, node in graph.items():
        if not (node["parents"] or node["influences"] or node["year"]):
            continue
        entry = {}
        if node["parents"]:
            entry["parents"] = node["parents"][:8]
        if node["influences"]:
            entry["influences"] = node["influences"][:8]
        if node["year"]:
            entry["year"] = node["year"]
        compact[name] = entry
    OUT.write_text(
        json.dumps(
            {
                "retrieved_at": date.today().isoformat(),
                "source": {
                    "name": "Wikidata music genre (Q188451)",
                    "url": "https://query.wikidata.org/",
                    "license": "CC0",
                    "note": "Open genealogy. Not derived from musicmap.info.",
                },
                "count": len(compact),
                "genres": compact,
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    print(f"wrote {OUT} ({len(compact)} nodes)")


if __name__ == "__main__":
    main()
