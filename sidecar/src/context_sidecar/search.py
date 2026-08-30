"""Local sample search. Filename tokens by default; CLAP ranks when enabled."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

AUDIO_SUFFIXES = {".wav", ".aiff", ".aif", ".flac", ".mp3", ".ogg"}
CLAP_MODEL = "laion/clap-htsat-unfused"

_CLAP = None


def sample_library() -> Path:
    raw = os.environ.get("CONTEXT_SAMPLE_LIBRARY", "").strip()
    path = Path(raw) if raw else Path.home() / "Library/Application Support/Context/Samples"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _enabled() -> bool:
    return os.environ.get("CONTEXT_ENABLE_CLAP", "0").strip() == "1"


def _cache_dir() -> str:
    raw = os.environ.get("CONTEXT_MODEL_CACHE_DIR", "").strip()
    path = Path(raw) if raw else Path.home() / "Library/Application Support/Context/models"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def _audio_paths(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in AUDIO_SUFFIXES
    )


def _hit(path: Path, root: Path, score: float, backend: str) -> dict[str, Any]:
    try:
        folder = str(path.parent.relative_to(root))
    except ValueError:
        folder = str(path.parent)
    if folder == ".":
        folder = ""
    return {
        "file_path": str(path),
        "name": path.name,
        "folder": folder,
        "score": float(score),
        "backend": backend,
    }


def _browse_hits(paths: list[Path], root: Path, *, limit: int) -> list[dict[str, Any]]:
    return [_hit(path, root, 0.0, "browse") for path in paths[:limit]]


def _filename_hits(query: str, paths: list[Path], root: Path, *, limit: int) -> list[dict[str, Any]]:
    tokens = [token.lower() for token in query.split() if token]
    hits = []
    for path in paths:
        try:
            relative = str(path.relative_to(root)).lower()
        except ValueError:
            relative = path.name.lower()
        blob = f"{path.name.lower()} {relative} {path.parent.name.lower()}"
        score = float(sum(1 for token in tokens if token in blob)) if tokens else 0.0
        hits.append(_hit(path, root, score, "filename-tokens"))
    hits.sort(key=lambda item: (-item["score"], item["name"]))
    return hits[:limit]


def _clap_pair():
    global _CLAP
    if _CLAP is not None:
        return _CLAP
    from transformers import ClapModel, ClapProcessor

    cache = _cache_dir()
    processor = ClapProcessor.from_pretrained(CLAP_MODEL, cache_dir=cache)
    model = ClapModel.from_pretrained(CLAP_MODEL, cache_dir=cache)
    model.eval()
    _CLAP = (processor, model)
    return _CLAP


def _clap_hits(query: str, paths: list[Path], root: Path, *, limit: int) -> list[dict[str, Any]]:
    import numpy as np
    import torch

    os.environ.setdefault("HF_HOME", _cache_dir())
    processor, model = _clap_pair()
    text = processor(text=[query], return_tensors="pt", padding=True)
    with torch.no_grad():
        text_emb = model.get_text_features(**text)
        text_emb = torch.nn.functional.normalize(text_emb, dim=-1)
    hits: list[dict[str, Any]] = []
    for path in paths:
        try:
            import librosa

            audio, _sr = librosa.load(str(path), sr=48000, mono=True)
        except Exception:
            continue
        if audio.size == 0:
            continue
        peak = float(np.max(np.abs(audio)) or 1.0)
        audio = audio / peak
        inputs = processor(audios=[audio], sampling_rate=48000, return_tensors="pt", padding=True)
        with torch.no_grad():
            audio_emb = model.get_audio_features(**inputs)
            audio_emb = torch.nn.functional.normalize(audio_emb, dim=-1)
            score = float((text_emb * audio_emb).sum())
        hits.append(_hit(path, root, score, "clap"))
    hits.sort(key=lambda item: item["score"], reverse=True)
    return hits[:limit]


def search_local(query: str, folder: str, *, limit: int = 80, quick: bool = False) -> dict[str, Any]:
    root = Path(folder)
    if not root.is_dir():
        return {"ok": False, "error": "folder_not_found", "hits": [], "count": 0}
    paths = _audio_paths(root)
    cap = max(1, min(int(limit), 400))
    if not query.strip():
        return {
            "ok": True,
            "wrote": False,
            "backend": "browse",
            "hits": _browse_hits(paths, root, limit=cap),
            "count": len(paths),
        }
    ranked = _filename_hits(query, paths, root, limit=cap)
    if quick or not _enabled():
        return {
            "ok": True,
            "wrote": False,
            "backend": "filename-tokens",
            "hits": ranked,
            "count": len(paths),
        }
    try:
        hits = _clap_hits(query, paths[: min(len(paths), 40)], root, limit=cap)
        return {"ok": True, "wrote": False, "backend": "clap", "hits": hits, "count": len(paths)}
    except Exception as exc:
        return {
            "ok": True,
            "wrote": False,
            "backend": "filename-tokens",
            "error": "clap_unavailable",
            "detail": str(exc),
            "hits": ranked,
            "count": len(paths),
        }
