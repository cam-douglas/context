"""Prompt → notes → WAV → MIDI → als-json Live Set export."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

from context_sidecar.analysis import analyze_audio
from context_sidecar.dsp import apply_room_to_wav
from context_sidecar.export import arrangement_from_assets, export_session
from context_sidecar.generation import current_generator, generate_wav
from context_sidecar.genres import family_for, lineage_for, lineage_text, match_style
from context_sidecar.magenta_models import generate_notes as magenta_generate_notes
from context_sidecar.magenta_seq import quantize_notes
from context_sidecar.midi_io import write_midi as write_midi_file
from context_sidecar.prompt_policy import apply_policy, assemble_conditioned
from context_sidecar.render_dsp import render_wav as render_wav_file
from context_sidecar.search import sample_library, search_local
from context_sidecar.stems import split_stems


def _norm(prompt: str) -> str:
    return re.sub(r"[^a-z0-9\s]+", " ", (prompt or "").lower()).strip()


def parse_prompt(prompt: str) -> dict[str, Any]:
    text = _norm(prompt)
    if not text:
        raise ValueError("prompt must not be empty")

    tempo = 120.0
    tempo_match = re.search(r"(\d{2,3})\s*bpm", text)
    if tempo_match:
        tempo = float(tempo_match.group(1))

    bars = 4
    bars_match = re.search(r"(\d{1,2})\s*-?\s*(?:bar|bars|measure|measures)\b", text)
    if bars_match:
        bars = max(1, min(64, int(bars_match.group(1))))

    key = "Am"
    if re.search(r"\bc major\b|\bcmaj\b|\bin c\b", text):
        key = "C"
    elif re.search(r"\ba minor\b|\bin am\b|\bam\b", text):
        key = "Am"
    elif "minor" in text:
        key = "Am"
    elif "major" in text:
        key = "C"

    style, genres = match_style(text)
    family = family_for(style)

    if family == "house" and tempo == 120.0 and "bpm" not in text:
        tempo = 124.0
    if family == "techno" and "bpm" not in text:
        tempo = 130.0
    if family == "trap" and "bpm" not in text:
        tempo = 140.0
    if family == "dnb" and "bpm" not in text:
        tempo = 174.0
    if family == "ambient" and "bpm" not in text:
        tempo = 80.0
    if family == "lofi" and "bpm" not in text:
        tempo = 86.0

    slug_style = re.sub(r"[^a-z0-9]+", "-", style).strip("-") or "custom"
    slug = f"{slug_style}-" + (re.sub(r"[^a-z0-9]+", "-", text)[:32].strip("-") or "context")
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16) % 10_000
    seconds = duration_seconds(bars, tempo)
    return {
        "prompt": prompt.strip(),
        "style": style,
        "family": family,
        "genres": genres,
        "lineage": lineage_for(style),
        "lineage_text": lineage_text(style),
        "tempo_bpm": tempo,
        "bars": bars,
        "key": key,
        "slug": slug,
        "seed": seed,
        "duration_sec": seconds,
    }


def duration_seconds(bars: int, tempo_bpm: float) -> float:
    return max(1, int(bars)) * 4.0 * 60.0 / max(40.0, float(tempo_bpm))


def _scale(key: str) -> list[int]:
    try:
        from music21 import scale

        pitches = (
            scale.MajorScale("C").getPitches("C4", "C5")
            if key == "C"
            else scale.MinorScale("A").getPitches("A3", "A4")
        )
        midis = [int(pitch.midi) for pitch in pitches][:8]
        if len(midis) >= 7:
            return midis
    except Exception:
        pass
    if key == "C":
        return [60, 62, 64, 65, 67, 69, 71, 72]
    return [57, 60, 62, 64, 67, 69, 72, 74]


def notes_for(plan: dict[str, Any]) -> list[dict[str, Any]]:
    style = str(plan.get("family") or plan["style"])
    bars = int(plan["bars"])
    beats = bars * 4
    scale = _scale(str(plan["key"]))
    seed = int(plan["seed"])
    notes: list[dict[str, Any]] = []

    def add(pitch: int, start: float, length: float, velocity: int = 100) -> None:
        notes.append({"pitch": pitch, "start": start, "length": length, "velocity": velocity})

    if style == "house":
        for beat in range(beats):
            add(36, beat, 0.2, 120)
            add(42, beat + 0.5, 0.15, 70)
            if beat % 2 == 1:
                add(39, beat, 0.2, 110)
            if beat % 4 in {0, 3}:
                add(33, beat, 0.4, 100)
        return notes
    if style == "techno":
        for beat in range(beats):
            add(36, beat, 0.18, 120)
            add(42, beat + 0.25, 0.1, 80)
            add(42, beat + 0.75, 0.1, 60)
            if beat % 8 == 4:
                add(37, beat, 0.2, 90)
        return notes
    if style in {"ambient", "lofi"}:
        roots = [scale[0] - 12, scale[2] - 12, scale[4] - 12, scale[0]]
        for bar in range(bars):
            root = roots[(bar + seed) % len(roots)]
            add(root, bar * 4, 4.0, 70)
            add(root + 7, bar * 4, 4.0, 55)
            add(root + 12, bar * 4 + 2, 2.0, 50)
        if style == "lofi":
            for beat in range(0, beats, 2):
                add(42, beat + 0.5, 0.1, 40)
        return notes
    if style == "trap":
        for beat in range(beats):
            if beat % 4 == 0:
                add(36, beat, 0.2, 120)
            add(42, beat + 0.5, 0.08, 60)
            if beat % 4 == 2:
                add(38, beat, 0.15, 110)
            if beat % 2 == 0:
                add(33, beat + 0.75, 0.2, 95)
        return notes
    if style == "dnb":
        for beat in range(beats):
            add(36, beat if beat % 2 == 0 else beat + 0.25, 0.12, 120)
            add(42, beat + 0.5, 0.08, 75)
            if beat % 2 == 1:
                add(40, beat, 0.12, 105)
        return notes
    if style in {"jazz", "funk", "pop"}:
        voicings = ([0, 4, 7, 11], [2, 5, 9, 12], [0, 5, 7, 10], [0, 4, 7, 9])
        for bar in range(bars):
            chord = voicings[(bar + seed) % 4]
            for offset in chord:
                add(scale[0] - 12 + offset, bar * 4, 3.5 if style != "funk" else 1.0, 80)
            if style == "funk":
                add(36, bar * 4, 0.15, 110)
                add(38, bar * 4 + 2, 0.15, 100)
        return notes
    if style == "bass":
        pattern = [0, 0, 3, 0, 5, 5, 3, 0]
        for beat in range(beats):
            add(scale[0] - 24 + pattern[(beat + seed) % 8], beat, 0.45, 110)
        return notes
    if style == "drums":
        for beat in range(beats):
            if beat % 4 in {0, 2}:
                add(36, beat, 0.15, 115)
            if beat % 4 in {1, 3}:
                add(38, beat, 0.15, 105)
            add(42, beat + 0.5, 0.1, 70)
        return notes
    if style == "arp":
        degrees = [0, 2, 4, 7, 4, 2]
        for i in range(beats * 2):
            add(scale[degrees[i % len(degrees)] % len(scale)], i * 0.5, 0.4, 90)
        return notes

    # default / melody: prompt-seeded line, not a house beat
    for i in range(beats):
        degree = (seed + i * 3) % len(scale)
        add(scale[degree], float(i), 0.7 if i % 4 else 1.2, 95)
        if i % 4 == 0:
            add(scale[0] - 12, float(i), 2.0, 70)
    return notes


def render_wav(plan: dict[str, Any], notes: list[dict[str, Any]], dest: Path) -> str:
    return render_wav_file(plan, notes, dest)


def write_midi(plan: dict[str, Any], notes: list[dict[str, Any]], dest: Path) -> str:
    return write_midi_file(plan, notes, dest)


STALE_HOUSE_NAMES = ("HOUSE-LOOP.wav", "HOUSE-LOOP.mid", "house-loop.wav", "house-loop.mid")


def dumps_dir() -> Path:
    raw = os.environ.get("CONTEXT_DUMPS_DIR", "").strip()
    path = Path(raw) if raw else Path.home() / "Library/Application Support/Context/Plugin"
    path.mkdir(parents=True, exist_ok=True)
    return path


def apply_knobs(plan: dict[str, Any], notes: list[dict[str, Any]], knobs: dict[str, Any] | None) -> list[dict[str, Any]]:
    values = knobs if isinstance(knobs, dict) else {}
    reverence = float(values.get("reverence") or 0.5)
    abstraction = float(values.get("abstraction") or 0.5)
    plan["knobs"] = {"reverence": reverence, "abstraction": abstraction}
    shaped: list[dict[str, Any]] = []
    extras: list[dict[str, Any]] = []
    for index, note in enumerate(notes):
        start = float(note["start"])
        pitch = int(note["pitch"])
        velocity = int(note.get("velocity") or 100)
        if reverence >= 0.7:
            start = round(start * 4.0) / 4.0
        elif reverence <= 0.3:
            pitch += -5 if index % 2 == 0 else 4
            start += 0.14 if index % 2 else -0.08
        if abstraction >= 0.7:
            pitch += 7 if index % 3 == 0 else 0
            extras.append(
                {
                    **note,
                    "pitch": pitch + 12,
                    "start": max(0.0, start + 0.25),
                    "velocity": max(36, velocity - 28),
                }
            )
        elif abstraction <= 0.3:
            start = round(start * 2.0) / 2.0
        shaped.append({**note, "start": max(0.0, start), "pitch": pitch, "velocity": velocity})
    return shaped + extras


def apply_reference(plan: dict[str, Any], reference_path: str | None) -> None:
    if not reference_path:
        return
    path = Path(reference_path)
    if not path.is_file():
        return
    knobs = plan.get("knobs") if isinstance(plan.get("knobs"), dict) else {}
    reverence = float(knobs.get("reverence") or 0.5)
    abstraction = float(knobs.get("abstraction") or 0.5)
    report = None
    try:
        report = analyze_audio(str(path))
    except Exception:
        try:
            import librosa
            import numpy as np

            y, sr = librosa.load(str(path), sr=None, mono=True)
            tempo = float(librosa.feature.rhythm.tempo(y=y, sr=sr)[0])
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            key = ("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")[
                int(np.argmax(np.mean(chroma, axis=1)))
            ]
            report = {"tempo_bpm": tempo, "musical_key": key, "energy": float(np.sqrt(np.mean(np.square(y))))}
        except Exception:
            report = None
    plan["reference_path"] = str(path)
    if report:
        if reverence >= 0.55 and "bpm" not in _norm(str(plan.get("prompt") or "")):
            plan["tempo_bpm"] = float(report.get("tempo_bpm") or plan["tempo_bpm"])
            plan["duration_sec"] = duration_seconds(int(plan["bars"]), float(plan["tempo_bpm"]))
        closeness = "stay close to the reference timbre and rhythm" if abstraction < 0.55 else "transform the reference abstractly"
        mix = "use the reference as the main character" if reverence >= 0.7 else "use the reference as a guide"
        plan["reference_text"] = (
            f"{mix}: {report.get('tempo_bpm', 120):.0f} bpm {report.get('musical_key', 'C')}, "
            f"{closeness}"
        )


def compose_to_folder(
    prompt: str,
    dest_dir: str,
    knobs: dict[str, Any] | None = None,
    reference_path: str | None = None,
    policy: dict[str, Any] | None = None,
    library_folder: str | None = None,
    split_stems_after: bool = False,
) -> dict[str, Any]:
    plan = parse_prompt(prompt)
    apply_policy(plan, policy)
    apply_reference(plan, reference_path)
    folder = Path(dest_dir)
    folder.mkdir(parents=True, exist_ok=True)
    generator = current_generator()
    stem = f"{generator['id']}-{plan['slug']}"
    wav = folder / f"{stem}.wav"
    mid = folder / f"{stem}.mid"
    if generator["id"] == "pedalboard":
        magenta_notes, magenta_status = magenta_generate_notes(plan)
        notes = apply_knobs(plan, magenta_notes or notes_for(plan), knobs)
        notes_backend = magenta_status if magenta_notes else "notes_for"
        notes, quantize_backend = quantize_notes(plan, notes)
        generated = generate_wav(prompt, plan, notes, wav)
    else:
        generated = generate_wav(prompt, plan, [], wav)
        magenta_notes, magenta_status = None, "skipped_for_neural_wav"
        notes = apply_knobs(plan, notes_for(plan), knobs)
        notes_backend = "notes_for"
        notes, quantize_backend = quantize_notes(plan, notes)
    room = (
        apply_room_to_wav(wav, knobs=plan.get("knobs"), family=str(plan.get("family") or ""))
        if wav.is_file()
        else {"ok": False, "wrote": False, "error": "missing_wav"}
    )
    split_source = str(plan["reference_path"]) if plan.get("reference_path") else (str(wav) if wav.is_file() else "")
    stems = (
        split_stems(split_source, dest_dir=str(folder / "stems"))
        if split_source and split_stems_after
        else {
            "ok": False,
            "wrote": False,
            "error": "stems_skipped" if not split_stems_after else "missing_wav",
            "stems": {},
        }
    )
    library = Path(library_folder) if (library_folder or "").strip() else sample_library()
    samples = search_local(prompt, str(library), quick=True)
    midi_backend = write_midi(plan, notes, mid)
    if plan["style"] != "house":
        for name in STALE_HOUSE_NAMES:
            (folder / name).unlink(missing_ok=True)
    stem_files = [path for path in (stems.get("stems") or {}).values() if path]
    files = [str(path) for path in (wav, mid) if path.is_file()] + stem_files
    arrangement = arrangement_from_assets(
        tempo_bpm=float(plan["tempo_bpm"]),
        musical_key=str(plan["key"]),
        midi_path=str(mid) if mid.is_file() else None,
        stem_paths=files,
        notes=notes,
        bars=int(plan["bars"]),
        slug=str(plan["slug"]),
    )
    session = export_session(
        str(folder),
        midi_path=str(mid) if mid.is_file() else None,
        stem_paths=files,
        arrangement=arrangement,
        notes=notes,
        tempo_bpm=float(plan["tempo_bpm"]),
        musical_key=str(plan["key"]),
        bars=int(plan["bars"]),
        slug=str(plan["slug"]),
        render=False,
    )
    files = list(dict.fromkeys(files + list(session.get("files") or [])))
    nested = session.get("session") if isinstance(session.get("session"), dict) else {}
    session = {
        "ok": session.get("ok"),
        "wrote_als": session.get("wrote_als"),
        "format": session.get("format"),
        "files": session.get("files"),
        "als_path": nested.get("als_path") or session.get("als_path"),
        "als_json_path": nested.get("als_json_path") or session.get("als_json_path"),
        "claim": session.get("claim"),
        "error": session.get("error") or nested.get("error"),
        "overwrote_source": session.get("overwrote_source") or nested.get("overwrote_source"),
        "render": session.get("render"),
    }
    return {
        "ok": bool(generated.get("ok") and wav.is_file()),
        "style": plan["style"],
        "family": plan["family"],
        "genres": plan["genres"],
        "lineage": plan.get("lineage"),
        "lineage_text": plan.get("lineage_text"),
        "knobs": plan.get("knobs"),
        "reference_path": plan.get("reference_path"),
        "tempo_bpm": plan["tempo_bpm"],
        "key": plan["key"],
        "bars": plan["bars"],
        "duration_sec": plan["duration_sec"],
        "slug": plan["slug"],
        "folder": str(folder),
        "wav": str(wav) if wav.is_file() else None,
        "midi": str(mid) if mid.is_file() else None,
        "files": files,
        "generator": generated,
        "room": room,
        "stems": stems,
        "samples": samples,
        "session": session,
        "backends": {
            "audio": generated.get("backend") or generated.get("fallback") or "pedalboard",
            "midi": midi_backend,
            "notes": notes_backend,
            "notes_detail": None if magenta_notes else magenta_status,
            "quantize": quantize_backend,
            "scale": "music21",
            "room": room.get("backend") if room.get("ok") else room.get("error") or "skipped",
            "stems": stems.get("backend") if stems.get("ok") else stems.get("error") or "skipped",
            "search": samples.get("backend") if samples.get("ok") else samples.get("error") or "skipped",
            "session": "als-json" if session.get("wrote_als") else session.get("error") or "skipped",
            "render": (session.get("render") or {}).get("backend")
            if (session.get("render") or {}).get("ok")
            else (session.get("render") or {}).get("error") or "skipped",
            "generator": generated.get("id"),
        },
        "claim": "cloned Live Set plus file-drop WAV/MIDI; source .als is never overwritten",
        "system_prompt": plan.get("system_prompt"),
        "rules": plan.get("rules"),
        "negative_prompt": plan.get("negative_prompt"),
        "conditioned_prompt": generated.get("conditioned_prompt") or assemble_conditioned(prompt, plan),
        "prompt_ranks": {
            "system": "hard",
            "rules": "hard",
            "negative": "hard_reject",
            "request": "suggestion",
        },
    }


def publish_drops(prompt: str) -> dict[str, Any]:
    return compose_to_folder(prompt, str(dumps_dir()))
