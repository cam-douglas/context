"""Match prompts against the shipped Every Noise + MusicBrainz genre index."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

INDEX_PATH = Path(__file__).with_name("data") / "genre_index.json"
GENEALOGY_PATH = Path(__file__).with_name("data") / "genre_genealogy.json"

ALIASES = {
    "dnb": "drum and bass",
    "d and b": "drum and bass",
    "drum n bass": "drum and bass",
    "rnb": "r and b",
    "r n b": "r and b",
    "ukg": "uk garage",
    "kpop": "k pop",
    "jpop": "j pop",
    "bossa": "bossa nova",
    "afro beats": "afrobeats",
    "four on the floor": "house",
}

ROLE_STYLES = (
    ("drums", ("drums", "breakbeat", "percussion", "kick pattern")),
    ("bass", ("bassline", "bass line", "sub bass")),
    ("arp", ("arp", "arpeggio")),
    ("melody", ("melody", "piano", "lead", "riff", "hook", "topline")),
    ("bass", ("bass",)),
)

FAMILY_NEEDLES = (
    ("house", ("house", "four on the floor", "garage")),
    ("techno", ("techno", "acid")),
    ("dnb", ("drum and bass", "dnb", "jungle")),
    ("trap", ("trap", "808", "drill")),
    ("lofi", ("lofi", "lo fi", "chillhop")),
    ("ambient", ("ambient", "drone", "texture")),
    ("jazz", ("jazz", "swing", "bebop")),
    ("funk", ("funk", "groove")),
    ("pop", ("pop", "k pop", "j pop")),
    ("drums", ("breakbeat", "percussion")),
    ("bass", ("bassline", "bass")),
)


def normalize(value: str) -> str:
    text = (value or "").lower().replace("&", " and ").replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=1)
def load_index() -> dict[str, Any]:
    return json.loads(INDEX_PATH.read_text())


def genre_count() -> int:
    return int(load_index().get("count") or len(load_index().get("genres") or []))


def expand_aliases(text: str) -> str:
    padded = f" {text} "
    extra: list[str] = []
    for alias, canonical in ALIASES.items():
        if f" {alias} " in padded:
            extra.append(canonical)
    return (text + " " + " ".join(extra)).strip() if extra else text


def match_genres(prompt: str) -> list[str]:
    text = expand_aliases(normalize(prompt))
    remaining = f" {text} "
    found: list[str] = []
    for genre in load_index().get("genres") or []:
        needle = f" {genre} "
        if needle in remaining:
            found.append(genre)
            remaining = remaining.replace(needle, " ", 1)
    return found


def match_role(prompt: str) -> str | None:
    text = normalize(prompt)
    for name, needles in ROLE_STYLES:
        if any(needle in text for needle in needles):
            return name
    return None


def match_style(prompt: str) -> tuple[str, list[str]]:
    genres = match_genres(prompt)
    if genres:
        return genres[0], genres
    role = match_role(prompt)
    if role:
        return role, []
    return "default", []


def family_for(style: str) -> str:
    text = normalize(style)
    for name, needles in FAMILY_NEEDLES:
        if any(needle in text for needle in needles):
            return name
    return "default"


@lru_cache(maxsize=1)
def load_genealogy() -> dict[str, Any]:
    if not GENEALOGY_PATH.is_file():
        return {"count": 0, "genres": {}}
    return json.loads(GENEALOGY_PATH.read_text())


def _genealogy_node(style: str) -> tuple[str, dict[str, Any]]:
    graph = load_genealogy().get("genres") or {}
    name = normalize(style)
    for candidate in (name, f"{name} music", name.removesuffix(" music").strip()):
        if candidate and candidate in graph:
            return candidate, graph[candidate]
    return name, {}


def lineage_for(style: str, depth: int = 3) -> dict[str, Any]:
    graph = load_genealogy().get("genres") or {}
    key, node = _genealogy_node(style)
    if not node:
        return {"name": key, "parents": [], "influences": [], "ancestors": [], "year": None}
    ancestors: list[str] = []
    current = key
    seen = {current}
    for _ in range(max(1, depth)):
        parents = (graph.get(current) or {}).get("parents") or []
        nxt = next((parent for parent in parents if parent not in seen), None)
        if not nxt:
            break
        ancestors.append(nxt)
        seen.add(nxt)
        current = nxt
    return {
        "name": key,
        "parents": list(node.get("parents") or []),
        "influences": list(node.get("influences") or []),
        "ancestors": ancestors,
        "year": node.get("year"),
    }


def lineage_text(style: str) -> str:
    lineage = lineage_for(style)
    bits: list[str] = []
    if lineage.get("year"):
        bits.append(f"emerged around {lineage['year']}")
    if lineage.get("ancestors"):
        bits.append("family " + " > ".join([lineage["name"], *lineage["ancestors"]]))
    elif lineage.get("parents"):
        bits.append("descended from " + ", ".join(lineage["parents"][:3]))
    if lineage.get("influences"):
        bits.append("influenced by " + ", ".join(lineage["influences"][:3]))
    return "; ".join(bits)


def index_meta() -> dict[str, Any]:
    payload = load_index()
    genealogy = load_genealogy()
    return {
        "count": int(payload.get("count") or 0),
        "retrieved_at": payload.get("retrieved_at"),
        "sources": payload.get("sources") or [],
        "genealogy": {
            "count": int(genealogy.get("count") or 0),
            "retrieved_at": genealogy.get("retrieved_at"),
            "source": genealogy.get("source"),
        },
    }
