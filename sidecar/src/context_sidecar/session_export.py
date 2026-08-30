"""Merge a Context arrangement into an Ableton Live Set without touching the source file."""

from __future__ import annotations

import hashlib
import shutil
import time
import wave
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from context_sidecar.als_json import (
    als_to_tree,
    attr,
    ensure_child,
    iter_ids,
    parse_als,
    remap_ids,
    set_value,
    tree_to_json,
    write_als,
    write_als_json,
)
from context_sidecar.schema import validate_arrangement

LIVE_TEMPLATE_CANDIDATES = (
    Path("/Applications/Ableton Live 11 Suite.app/Contents/App-Resources/Builtin/Templates/DefaultLiveSet.als"),
    Path("/Applications/Ableton Live 11 Standard.app/Contents/App-Resources/Builtin/Templates/DefaultLiveSet.als"),
    Path("/Applications/Ableton Live 11 Intro.app/Contents/App-Resources/Builtin/Templates/DefaultLiveSet.als"),
)

CONTEXT_COLOR = "17"


def live_template_path() -> Path | None:
    for candidate in LIVE_TEMPLATE_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_dest_dir(dest_dir: str) -> Path:
    dest = Path(dest_dir).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def _safe_source(path: str | None) -> Path | None:
    if not path:
        return None
    source = Path(path).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".als":
        raise ValueError("source_als must be an existing .als file")
    return source


def _leaf(tag: str, value: Any | None = None, **attrib: str) -> Element:
    element = Element(tag, attrib)
    if value is not None:
        element.set("Value", str(value))
    return element


def _nested(*tags: str) -> Element:
    root = Element(tags[0])
    cursor = root
    for tag in tags[1:]:
        nxt = Element(tag)
        cursor.append(nxt)
        cursor = nxt
    return root


def _fmt(number: float) -> str:
    if float(number).is_integer():
        return str(int(number))
    return repr(float(number))


def _track_name(track: Element) -> str:
    effective = track.find("Name/EffectiveName")
    if effective is not None:
        return attr(effective, "Value")
    return ""


def _set_track_name(track: Element, name: str) -> None:
    name_el = ensure_child(track, "Name")
    set_value(ensure_child(name_el, "EffectiveName"), name)
    set_value(ensure_child(name_el, "UserName"), name)


def _inventory(root: Element) -> dict[str, Any]:
    live = root.find("LiveSet")
    tracks_el = live.find("Tracks") if live is not None else None
    tracks = []
    for track in list(tracks_el or []):
        events = (
            track.find("DeviceChain/MainSequencer/Sample/ArrangerAutomation/Events")
            or track.find("DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events")
        )
        clips = []
        for clip in list(events or []):
            if clip.tag not in {"AudioClip", "MidiClip"}:
                continue
            clips.append(
                {
                    "tag": clip.tag,
                    "name": attr(clip.find("Name"), "Value"),
                    "start": attr(clip.find("CurrentStart"), "Value"),
                    "end": attr(clip.find("CurrentEnd"), "Value"),
                }
            )
        tracks.append({"tag": track.tag, "id": attr(track, "Id"), "name": _track_name(track), "clips": clips})
    locators = []
    for locator in root.findall("LiveSet/Locators/Locators/Locator"):
        locators.append({"name": attr(locator.find("Name"), "Value"), "beats": attr(locator.find("Time"), "Value")})
    tempo = None
    for element in root.findall(".//Tempo/Manual"):
        tempo = attr(element, "Value")
        break
    return {
        "creator": attr(root, "Creator"),
        "minor_version": attr(root, "MinorVersion"),
        "tempo": tempo,
        "tracks": tracks,
        "track_names": [track["name"] for track in tracks],
        "clip_count": sum(len(track["clips"]) for track in tracks),
        "locator_names": [item["name"] for item in locators],
        "locators": locators,
    }


def _minimal_live_set() -> Element:
    root = Element(
        "Ableton",
        {
            "MajorVersion": "5",
            "MinorVersion": "11.0_433",
            "SchemaChangeCount": "3",
            "Creator": "Ableton Live 11.3.43",
            "Revision": "context-session-export",
        },
    )
    live = Element("LiveSet")
    root.append(live)
    live.append(_leaf("NextPointeeId", "64"))
    live.append(_leaf("OverwriteProtectionNumber", "2815"))
    live.append(_leaf("LomId", "0"))
    live.append(_leaf("LomIdView", "0"))
    tracks = Element("Tracks")
    live.append(tracks)
    tracks.append(_synthetic_track("midi", "1-MIDI", track_id="12"))
    tracks.append(_synthetic_track("audio", "2-Audio", track_id="8"))
    live.append(_synthetic_master("MasterTrack"))
    live.append(_synthetic_master("PreHearTrack"))
    locators = Element("Locators")
    locators.append(Element("Locators"))
    live.append(locators)
    scale = Element("ScaleInformation")
    scale.append(_leaf("RootNote", "0"))
    scale.append(_leaf("Name", "Major"))
    live.append(scale)
    return root


def _events_path(kind: str) -> tuple[str, ...]:
    if kind == "audio":
        return ("Sample", "ArrangerAutomation", "Events")
    return ("ClipTimeable", "ArrangerAutomation", "Events")


def _synthetic_track(kind: str, name: str, track_id: str = "0") -> Element:
    tag = "AudioTrack" if kind == "audio" else "MidiTrack"
    track = Element(tag, {"Id": track_id})
    track.append(_leaf("LomId", "0"))
    track.append(_leaf("LomIdView", "0"))
    name_el = Element("Name")
    name_el.append(_leaf("EffectiveName", name))
    name_el.append(_leaf("UserName", name))
    name_el.append(_leaf("Annotation", ""))
    name_el.append(_leaf("MemorizedFirstClipName", ""))
    track.append(name_el)
    track.append(_leaf("Color", CONTEXT_COLOR))
    chain = Element("DeviceChain")
    sequencer = Element("MainSequencer")
    slots = Element("ClipSlotList")
    slot = Element("ClipSlot", {"Id": "0"})
    slot.append(_leaf("LomId", "0"))
    slot.append(_nested("ClipSlot", "Value"))
    slot.append(_leaf("HasStop", "true"))
    slot.append(_leaf("NeedRefreeze", "true"))
    slots.append(slot)
    sequencer.append(slots)
    cursor = sequencer
    for tag_name in _events_path(kind)[:-1]:
        nxt = Element(tag_name)
        cursor.append(nxt)
        cursor = nxt
    cursor.append(Element("Events"))
    chain.append(sequencer)
    track.append(chain)
    return track


def _synthetic_master(tag: str) -> Element:
    track = Element(tag)
    name = Element("Name")
    name.append(_leaf("EffectiveName", tag))
    track.append(name)
    chain = Element("DeviceChain")
    mixer = Element("Mixer")
    tempo = Element("Tempo")
    tempo.append(_leaf("LomId", "0"))
    tempo.append(_leaf("Manual", "120"))
    mixer.append(tempo)
    chain.append(mixer)
    track.append(chain)
    return track


def _load_base(source: Path | None) -> tuple[Element, str]:
    if source is not None:
        return als_to_tree(source), "user-set"
    template = live_template_path()
    if template is not None:
        return als_to_tree(template), "live-default-template"
    return _minimal_live_set(), "synthetic"


def _next_track_id(root: Element) -> int:
    tracks = root.find("LiveSet/Tracks")
    used = [int(attr(track, "Id") or "0") for track in list(tracks or []) if attr(track, "Id").lstrip("-").isdigit()]
    return (max(used) + 1) if used else 1


def _clone_kind_track(root: Element, kind: str, name: str) -> Element:
    tag = "AudioTrack" if kind == "audio" else "MidiTrack"
    tracks = root.find("LiveSet/Tracks")
    source = next((track for track in list(tracks or []) if track.tag == tag), None)
    if source is None:
        clone = _synthetic_track(kind, name, track_id=str(_next_track_id(root)))
    else:
        clone = ET.fromstring(ET.tostring(source, encoding="utf-8"))
        used = set(iter_ids(root))
        remap_ids(clone, used)
        clone.set("Id", str(_next_track_id(root)))
    _set_track_name(clone, name)
    color = clone.find("Color")
    if color is not None:
        set_value(color, CONTEXT_COLOR)
    events = _arrangement_events(clone, kind)
    events.clear()
    return clone


def _arrangement_events(track: Element, kind: str) -> Element:
    path = "DeviceChain/MainSequencer/" + "/".join(_events_path(kind))
    events = track.find(path)
    if events is not None:
        return events
    sequencer = track.find("DeviceChain/MainSequencer")
    if sequencer is None:
        chain = ensure_child(track, "DeviceChain")
        sequencer = ensure_child(chain, "MainSequencer")
    cursor = sequencer
    for tag in _events_path(kind):
        cursor = ensure_child(cursor, tag)
    return cursor


def _wav_info(path: Path) -> tuple[int, int, int]:
    with wave.open(str(path), "rb") as handle:
        return handle.getnframes(), handle.getframerate(), handle.getnchannels()


def _file_ref(path: Path, rel: str) -> tuple[Element, int, int]:
    ref = Element("FileRef")
    frames = rate = 0
    if path.suffix.lower() == ".wav" and path.is_file():
        try:
            frames, rate, _channels = _wav_info(path)
        except Exception:
            frames = rate = 0
    ref.append(_leaf("RelativePathType", "1"))
    ref.append(_leaf("RelativePath", rel))
    ref.append(_leaf("Path", str(path.resolve())))
    ref.append(_leaf("Type", "1" if path.suffix.lower() == ".wav" else "0"))
    ref.append(_leaf("LivePackName", ""))
    ref.append(_leaf("LivePackId", ""))
    if path.is_file():
        ref.append(_leaf("OriginalFileSize", str(path.stat().st_size)))
    return ref, frames, rate


def _common_clip_fields(clip: Element, *, name: str, start: float, end: float, color: str = CONTEXT_COLOR) -> None:
    clip.append(_leaf("LomId", "0"))
    clip.append(_leaf("LomIdView", "0"))
    clip.append(_leaf("CurrentStart", _fmt(start)))
    clip.append(_leaf("CurrentEnd", _fmt(end)))
    loop = Element("Loop")
    length = max(0.25, end - start)
    loop.append(_leaf("LoopStart", "0"))
    loop.append(_leaf("LoopEnd", _fmt(length)))
    loop.append(_leaf("StartRelative", "0"))
    loop.append(_leaf("LoopOn", "false"))
    loop.append(_leaf("OutMarker", _fmt(length)))
    loop.append(_leaf("HiddenLoopStart", "0"))
    loop.append(_leaf("HiddenLoopEnd", _fmt(length)))
    clip.append(loop)
    clip.append(_leaf("Name", name))
    clip.append(_leaf("Annotation", "Context"))
    clip.append(_leaf("Color", color))
    clip.append(_leaf("LaunchMode", "0"))
    clip.append(_leaf("LaunchQuantisation", "0"))
    signature = Element("TimeSignature")
    stamps = Element("TimeSignatures")
    remote = Element("RemoteableTimeSignature", {"Id": "0"})
    remote.append(_leaf("Numerator", "4"))
    remote.append(_leaf("Denominator", "4"))
    remote.append(_leaf("Time", "0"))
    stamps.append(remote)
    signature.append(stamps)
    clip.append(signature)
    envelopes = Element("Envelopes")
    envelopes.append(Element("Envelopes"))
    clip.append(envelopes)
    scroller = Element("ScrollerTimePreserver")
    scroller.append(_leaf("LeftTime", _fmt(start)))
    scroller.append(_leaf("RightTime", _fmt(end)))
    clip.append(scroller)
    selection = Element("TimeSelection")
    selection.append(_leaf("AnchorTime", "0"))
    selection.append(_leaf("OtherTime", "0"))
    clip.append(selection)
    clip.append(_leaf("Legato", "false"))
    clip.append(_leaf("Ram", "false"))
    groove = Element("GrooveSettings")
    groove.append(_leaf("GrooveId", "-1"))
    clip.append(groove)
    clip.append(_leaf("Disabled", "false"))
    clip.append(_leaf("VelocityAmount", "0"))
    follow = Element("FollowAction")
    for key, value in (
        ("FollowTime", "4"),
        ("IsLinked", "true"),
        ("LoopIterations", "1"),
        ("FollowActionA", "4"),
        ("FollowActionB", "0"),
        ("FollowChanceA", "100"),
        ("FollowChanceB", "0"),
        ("JumpIndexA", "0"),
        ("JumpIndexB", "0"),
        ("FollowActionEnabled", "false"),
    ):
        follow.append(_leaf(key, value))
    clip.append(follow)
    grid = Element("Grid")
    for key, value in (
        ("FixedNumerator", "1"),
        ("FixedDenominator", "16"),
        ("GridIntervalPixel", "20"),
        ("Ntoles", "2"),
        ("SnapToGrid", "true"),
        ("Fixed", "false"),
    ):
        grid.append(_leaf(key, value))
    clip.append(grid)
    clip.append(_leaf("FreezeStart", "0"))
    clip.append(_leaf("FreezeEnd", "0"))
    clip.append(_leaf("IsWarped", "true"))
    clip.append(_leaf("TakeId", "0"))


def _audio_clip(*, name: str, start: float, length: float, path: Path, rel: str, clip_id: int) -> Element:
    end = start + max(0.25, length)
    clip = Element("AudioClip", {"Id": str(clip_id), "Time": _fmt(start)})
    _common_clip_fields(clip, name=name, start=start, end=end)
    sample = Element("SampleRef")
    file_ref, frames, rate = _file_ref(path, rel)
    sample.append(file_ref)
    sample.append(_leaf("LastModDate", str(int(path.stat().st_mtime)) if path.is_file() else "0"))
    source = Element("SourceContext")
    source.append(Element("SourceContext", {"Id": "0"}))
    sample.append(source)
    sample.append(_leaf("SampleUsageHint", "0"))
    sample.append(_leaf("DefaultDuration", str(frames or 1)))
    sample.append(_leaf("DefaultSampleRate", str(rate or 44100)))
    clip.append(sample)
    onsets = Element("Onsets")
    onsets.append(Element("UserOnsets"))
    onsets.append(_leaf("HasUserOnsets", "false"))
    clip.append(onsets)
    clip.append(_leaf("WarpMode", "0"))
    clip.append(_leaf("GranularityTones", "0"))
    clip.append(_leaf("GranularityTexture", "0"))
    clip.append(_leaf("FluctuationTexture", "0"))
    clip.append(_leaf("TransientResolution", "6"))
    clip.append(_leaf("TransientLoopMode", "0"))
    clip.append(_leaf("TransientEnvelope", "100"))
    clip.append(_leaf("ComplexProFormants", "0"))
    clip.append(_leaf("ComplexProEnvelope", "100"))
    clip.append(_leaf("Sync", "true"))
    clip.append(_leaf("HiQ", "true"))
    clip.append(_leaf("Fade", "true"))
    fades = Element("Fades")
    for key, value in (
        ("FadeInLength", "0"),
        ("FadeOutLength", "0"),
        ("ClipFadesAreInitialized", "true"),
        ("CrossfadeInState", "0"),
        ("FadeInCurveSkew", "0"),
        ("FadeInCurveSlope", "0"),
        ("FadeOutCurveSkew", "0"),
        ("FadeOutCurveSlope", "0"),
        ("IsDefaultFadeIn", "true"),
        ("IsDefaultFadeOut", "true"),
    ):
        fades.append(_leaf(key, value))
    clip.append(fades)
    clip.append(_leaf("PitchCoarse", "0"))
    clip.append(_leaf("PitchFine", "0"))
    clip.append(_leaf("SampleVolume", "0"))
    markers = Element("WarpMarkers")
    seconds = (frames / rate) if frames and rate else max(0.25, length * 0.5)
    markers.append(Element("WarpMarker", {"Id": "0", "SecTime": "0", "BeatTime": "0"}))
    markers.append(Element("WarpMarker", {"Id": "1", "SecTime": _fmt(seconds), "BeatTime": _fmt(max(0.25, length))}))
    clip.append(markers)
    clip.append(Element("SavedWarpMarkersForStretched"))
    clip.append(_leaf("MarkersGenerated", "true"))
    clip.append(_leaf("IsSongTempoMaster", "false"))
    return clip


def _midi_clip(*, name: str, start: float, length: float, notes: list[dict[str, Any]], clip_id: int) -> Element:
    end = start + max(0.25, length)
    clip = Element("MidiClip", {"Id": str(clip_id), "Time": _fmt(start)})
    _common_clip_fields(clip, name=name, start=start, end=end)
    notes_el = Element("Notes")
    key_tracks = Element("KeyTracks")
    by_pitch: dict[int, list[dict[str, Any]]] = {}
    note_id = 1
    for raw in notes:
        pitch = max(0, min(127, int(raw.get("pitch") or 60)))
        by_pitch.setdefault(pitch, []).append(raw)
    for index, (pitch, group) in enumerate(sorted(by_pitch.items())):
        key = Element("KeyTrack", {"Id": str(index)})
        bucket = Element("Notes")
        for raw in group:
            onset = float(raw.get("start") or raw.get("time") or 0)
            duration = float(raw.get("length") or raw.get("duration") or 0.25)
            velocity = max(1, min(127, int(raw.get("velocity") or 100)))
            bucket.append(
                Element(
                    "MidiNoteEvent",
                    {
                        "Time": _fmt(onset),
                        "Duration": _fmt(max(0.03125, duration)),
                        "Velocity": str(velocity),
                        "VelocityDeviation": "0",
                        "OffVelocity": "64",
                        "Probability": "1",
                        "IsEnabled": "true",
                        "NoteId": str(note_id),
                    },
                )
            )
            note_id += 1
        key.append(bucket)
        key.append(_leaf("MidiKey", str(pitch)))
        key_tracks.append(key)
    notes_el.append(key_tracks)
    store = Element("PerNoteEventStore")
    store.append(Element("EventLists"))
    notes_el.append(store)
    generator = Element("NoteIdGenerator")
    generator.append(_leaf("NextId", str(note_id)))
    notes_el.append(generator)
    clip.append(notes_el)
    clip.append(_leaf("BankSelectCoarse", "-1"))
    clip.append(_leaf("BankSelectFine", "-1"))
    clip.append(_leaf("ProgramChange", "-1"))
    for tag in (
        "NoteEditorFoldInZoom",
        "NoteEditorFoldInScroll",
        "NoteEditorFoldOutZoom",
        "NoteEditorFoldOutScroll",
        "NoteEditorFoldScaleZoom",
        "NoteEditorFoldScaleScroll",
    ):
        clip.append(_leaf(tag, "0"))
    scale = Element("ScaleInformation")
    scale.append(_leaf("RootNote", "0"))
    scale.append(_leaf("Name", "Minor" if str(name).endswith("m") else "Major"))
    clip.append(scale)
    clip.append(_leaf("IsInKey", "false"))
    clip.append(_leaf("NoteSpellingPreference", "0"))
    clip.append(_leaf("PreferFlatRootNote", "false"))
    grid = Element("ExpressionGrid")
    for key, value in (
        ("FixedNumerator", "1"),
        ("FixedDenominator", "16"),
        ("GridIntervalPixel", "20"),
        ("Ntoles", "2"),
        ("SnapToGrid", "false"),
        ("Fixed", "false"),
    ):
        grid.append(_leaf(key, value))
    clip.append(grid)
    return clip


def _set_tempo(root: Element, bpm: float) -> None:
    master = root.find("LiveSet/MasterTrack")
    search = master.findall(".//Tempo/Manual") if master is not None else []
    if not search:
        search = root.findall(".//Tempo/Manual")
    if search:
        set_value(search[0], _fmt(bpm))
        return
    live = ensure_child(root, "LiveSet")
    master_el = ensure_child(live, "MasterTrack")
    chain = ensure_child(master_el, "DeviceChain")
    mixer = ensure_child(chain, "Mixer")
    tempo = ensure_child(mixer, "Tempo")
    set_value(ensure_child(tempo, "Manual"), _fmt(bpm))


def _set_scale(root: Element, musical_key: str) -> None:
    live = root.find("LiveSet")
    if live is None:
        return
    scale = ensure_child(live, "ScaleInformation")
    raw = musical_key.strip()
    minor = raw.lower().endswith("m") or "minor" in raw.lower()
    token = raw.lower().replace("minor", "").replace("major", "").replace("min", "").strip(" -")
    token = token[:-1] if token.endswith("m") and token not in {"am"} else token
    roots = {
        "c": 0,
        "c#": 1,
        "db": 1,
        "d": 2,
        "eb": 3,
        "d#": 3,
        "e": 4,
        "f": 5,
        "f#": 6,
        "gb": 6,
        "g": 7,
        "ab": 8,
        "g#": 8,
        "a": 9,
        "bb": 10,
        "a#": 10,
        "b": 11,
    }
    key = token[:2] if token[:2] in roots else token[:1]
    set_value(ensure_child(scale, "RootNote"), str(roots.get(key, 0)))
    set_value(ensure_child(scale, "Name"), "Minor" if minor else "Major")


def _add_locators(root: Element, locators: list[dict[str, Any]], used: set[int]) -> list[str]:
    live = ensure_child(root, "LiveSet")
    wrapper = ensure_child(live, "Locators")
    bucket = ensure_child(wrapper, "Locators")
    existing = {attr(item.find("Name"), "Value") for item in list(bucket)}
    added: list[str] = []
    next_id = (max(used) + 1) if used else 1
    for locator in locators:
        name = str(locator.get("name") or "Section")
        if name in existing:
            continue
        node = Element("Locator", {"Id": str(next_id)})
        used.add(next_id)
        next_id += 1
        node.append(_leaf("LomId", "0"))
        node.append(_leaf("Time", _fmt(float(locator.get("beats") or 0))))
        node.append(_leaf("Name", name))
        node.append(_leaf("Annotation", "Context"))
        node.append(_leaf("IsSongStart", "false"))
        bucket.append(node)
        existing.add(name)
        added.append(name)
    return added


def _stage_file(path: str | None, samples: Path) -> tuple[Path | None, str]:
    if not path:
        return None, ""
    source = Path(path)
    if not source.is_file():
        return None, ""
    samples.mkdir(parents=True, exist_ok=True)
    dest = samples / source.name
    if dest.resolve() != source.resolve():
        shutil.copy2(source, dest)
    rel = f"Samples/Context/{dest.name}"
    return dest, rel


def _unique_name(name: str, existing: set[str]) -> str:
    candidate = name
    index = 2
    while candidate in existing:
        candidate = f"{name} {index}"
        index += 1
    existing.add(candidate)
    return candidate


def _append_track(root: Element, track: Element) -> None:
    tracks = ensure_child(ensure_child(root, "LiveSet"), "Tracks")
    insert_at = len(list(tracks))
    for index, child_el in enumerate(list(tracks)):
        if child_el.tag == "ReturnTrack":
            insert_at = index
            break
    tracks.insert(insert_at, track)


def _bump_pointee(root: Element, used: set[int]) -> None:
    live = root.find("LiveSet")
    if live is None:
        return
    pointee = ensure_child(live, "NextPointeeId")
    set_value(pointee, str((max(used) + 1) if used else 1))


def merge_arrangement(
    root: Element,
    arrangement: dict[str, Any],
    *,
    samples_dir: Path,
    locks: list[str] | None = None,
) -> dict[str, Any]:
    validate_arrangement(
        {
            "schema_version": arrangement["schema_version"],
            "tempo_bpm": arrangement["tempo_bpm"],
            "musical_key": arrangement["musical_key"],
            "time_signature": arrangement["time_signature"],
            "sections": arrangement["sections"],
            "tracks": arrangement["tracks"],
        }
    )
    locked = set(locks or [])
    before = _inventory(root)
    existing_names = set(before["track_names"])
    used = set(iter_ids(root))
    added_tracks: list[str] = []
    added_clips = 0
    _set_tempo(root, float(arrangement["tempo_bpm"]))
    _set_scale(root, str(arrangement.get("musical_key") or "C"))
    added_locators = _add_locators(root, list(arrangement.get("locators") or []), used)
    clip_id = (max(used) + 1) if used else 1
    for track in arrangement["tracks"]:
        if track.get("id") in locked:
            continue
        kind = str(track["kind"])
        name = _unique_name(f"Context {track['name']}", existing_names)
        cloned = _clone_kind_track(root, kind, name)
        used.update(iter_ids(cloned))
        events = _arrangement_events(cloned, kind)
        for clip in track.get("clips") or []:
            if clip.get("id") in locked:
                continue
            start = float(clip.get("start_beats") or 0)
            length = float(clip.get("length_beats") or 4)
            clip_name = str(clip.get("id") or name)
            if kind == "audio":
                staged, rel = _stage_file(str(clip.get("file_path") or ""), samples_dir)
                if staged is None:
                    continue
                events.append(
                    _audio_clip(name=clip_name, start=start, length=length, path=staged, rel=rel, clip_id=clip_id)
                )
            else:
                events.append(
                    _midi_clip(
                        name=clip_name,
                        start=start,
                        length=length,
                        notes=list(clip.get("notes") or []),
                        clip_id=clip_id,
                    )
                )
            used.add(clip_id)
            clip_id += 1
            added_clips += 1
        _append_track(root, cloned)
        added_tracks.append(name)
        used.update(iter_ids(cloned))
    _bump_pointee(root, used)
    after = _inventory(root)
    preserved = [name for name in before["track_names"] if name in after["track_names"]]
    return {
        "added_tracks": added_tracks,
        "added_clips": added_clips,
        "added_locators": added_locators,
        "preserved_tracks": preserved,
        "before": before,
        "after": after,
    }


def export_live_set(
    dest_dir: str,
    arrangement: dict[str, Any],
    *,
    source_als: str | None = None,
    midi_path: str | None = None,
    stem_paths: list[str] | None = None,
    locks: list[str] | None = None,
    slug: str = "Context",
) -> dict[str, Any]:
    dest = _safe_dest_dir(dest_dir)
    source = _safe_source(source_als)
    als_path = dest / f"{slug}.als"
    if source is not None and als_path.resolve() == source:
        als_path = dest / f"{slug}-export-{int(time.time())}.als"
    root, template_kind = _load_base(source)
    samples = dest / "Samples" / "Context"
    extras = [path for path in ([midi_path] if midi_path else []) + list(stem_paths or []) if path]
    for extra in extras:
        _stage_file(extra, samples)
    merge = merge_arrangement(root, arrangement, samples_dir=samples, locks=locks)
    write_als(als_path, root)
    tree_json = tree_to_json(root)
    json_path = dest / f"{slug}.als.json"
    write_als_json(json_path, tree_json)
    reparsed = als_to_tree(als_path)
    after = _inventory(reparsed)
    source_hash = _sha256(source) if source is not None else None
    dest_hash = _sha256(als_path)
    intact = (
        set(merge["preserved_tracks"]) == set(merge["before"]["track_names"])
        and after["clip_count"] >= merge["before"]["clip_count"] + merge["added_clips"]
        and (source is None or dest_hash != source_hash or als_path.resolve() != source)
        and als_path.is_file()
    )
    if source is not None and als_path.resolve() == source:
        intact = False
    return {
        "ok": intact,
        "wrote_als": True,
        "format": "ableton-als",
        "als_path": str(als_path),
        "als_json_path": str(json_path),
        "template": template_kind,
        "source_als": str(source) if source else None,
        "source_sha256": source_hash,
        "dest_sha256": dest_hash,
        "overwrote_source": bool(source and als_path.resolve() == source),
        "integrity": {
            "preserved_user_tracks": merge["preserved_tracks"],
            "added_tracks": merge["added_tracks"],
            "added_clips": merge["added_clips"],
            "added_locators": merge["added_locators"],
            "reparsed_tracks": after["track_names"],
            "reparsed_clip_count": after["clip_count"],
            "tempo": after["tempo"],
            "intact": intact,
        },
        "claim": "cloned session plus Context tracks; source .als was not overwritten",
    }


def parse_session(path: str) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file() or source.suffix.lower() != ".als":
        return {"ok": False, "error": "not_an_als"}
    root = als_to_tree(source)
    return {"ok": True, "inventory": _inventory(root), "als_json": parse_als(source)}
