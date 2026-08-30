"""Offline DSP. pyroomacoustics room IR is applied on compose; other helpers stay plan-only."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def ducking_plan(hits: list[dict[str, Any]], *, amount: float = 0.4) -> dict[str, Any]:
    moves = []
    for hit in hits:
        moves.append(
            {
                "type": "eq_cut",
                "hz": hit.get("hz") or 250,
                "db": -3.0 * max(0.0, min(1.0, amount)),
                "stems": hit.get("stems") or [],
                "sidechain": True,
            }
        )
    return {"ok": True, "wrote": False, "backend": "plan-only", "moves": moves}


def room_curve(balance: dict[str, float] | None = None) -> dict[str, Any]:
    bands = balance or {"low": 1.2, "mud": 1.1, "high": 0.9}
    curve = []
    for name, value in bands.items():
        gain = 0.0
        if value > 1.05:
            gain = -2.0
        elif value < 0.95:
            gain = 1.5
        curve.append({"band": name, "gain_db": gain})
    return {
        "ok": True,
        "wrote": False,
        "kind": "untreated_room_corrector",
        "curve": curve,
        "apply_explicit": True,
    }


def _beats_to_seconds(beats: float, tempo_bpm: float) -> float:
    return float(beats) * 60.0 / max(40.0, float(tempo_bpm))


def _render_arrangement_inline(arrangement: dict[str, Any], dest_path: Path) -> dict[str, Any]:
    try:
        import dawdreamer as daw
        import numpy as np
        import soundfile as sf
        from scipy.signal import resample

        sample_rate = 44100
        engine = daw.RenderEngine(sample_rate, 128)
        tempo = float(arrangement.get("tempo_bpm") or 120)
        engine.set_bpm(tempo)
        graph: list[Any] = []
        names: list[str] = []
        duration = 0.25
        for track in arrangement.get("tracks") or []:
            for clip in track.get("clips") or []:
                path = Path(str(clip.get("file_path") or ""))
                if clip.get("kind") != "audio" or not path.is_file():
                    continue
                audio, rate = sf.read(str(path), always_2d=True)
                data = np.asarray(audio.T, dtype=np.float32)
                if rate != sample_rate:
                    target = max(1, int(round(data.shape[1] * sample_rate / float(rate))))
                    data = np.vstack([resample(channel, target).astype(np.float32) for channel in data])
                start = _beats_to_seconds(float(clip.get("start_beats") or 0), tempo)
                pad = int(round(start * sample_rate))
                if pad:
                    data = np.pad(data, ((0, 0), (pad, 0)))
                name = f"clip_{clip.get('id') or path.stem}_{len(names)}"
                processor = engine.make_playback_processor(name, data)
                graph.append((processor, []))
                names.append(name)
                duration = max(duration, data.shape[1] / sample_rate)
        if not graph:
            return {
                "ok": False,
                "wrote": False,
                "backend": "dawdreamer",
                "error": "no_audio_clips",
                "detail": "DawDreamer needs at least one readable audio clip to render.",
            }
        if len(graph) == 1:
            engine.load_graph(graph)
        else:
            mixer = engine.make_add_processor("mix", len(names))
            graph.append((mixer, names))
            engine.load_graph(graph)
        engine.render(duration)
        mixed = np.asarray(engine.get_audio(), dtype=np.float32)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(dest_path), mixed.T, sample_rate)
        return {
            "ok": True,
            "wrote": True,
            "backend": "dawdreamer",
            "path": str(dest_path),
            "duration_sec": duration,
            "processors": names,
            "tempo_bpm": tempo,
            "detail": "Offline stem mix rendered to confirm arrangement timing.",
        }
    except Exception as exc:
        return {
            "ok": False,
            "wrote": False,
            "error": "dawdreamer_unavailable",
            "detail": str(exc),
            "path": None,
        }


def dawdreamer_render_arrangement(arrangement: dict[str, Any], dest: str | Path) -> dict[str, Any]:
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        plan_path = Path(tmp) / "arrangement.json"
        plan_path.write_text(json.dumps(arrangement), encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "context_sidecar.dawdreamer_worker", str(plan_path), str(dest_path)],
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
        except Exception as exc:
            return {
                "ok": False,
                "wrote": False,
                "error": "dawdreamer_unavailable",
                "detail": str(exc),
                "path": None,
            }
        try:
            payload = json.loads(completed.stdout or "")
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
        return {
            "ok": False,
            "wrote": False,
            "error": "dawdreamer_unavailable",
            "detail": (completed.stderr or completed.stdout or f"exit {completed.returncode}")[-500:],
            "path": None,
        }


def dawdreamer_rehearse(plugin_id: str, automation: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        import dawdreamer as daw

        engine = daw.RenderEngine(44100, 128)
        engine.set_bpm(120)
        return {
            "ok": True,
            "wrote": False,
            "backend": "dawdreamer",
            "detail": "Headless render engine is live. Session write stays on the als-json export path.",
            "plugin_id": plugin_id,
            "automation": automation,
            "session_state": {"bpm": 120, "block_size": 128, "sample_rate": 44100},
        }
    except Exception as exc:
        return {
            "ok": False,
            "wrote": False,
            "error": "dawdreamer_unavailable",
            "detail": str(exc),
            "plugin_id": plugin_id,
            "automation": automation,
            "session_state": None,
        }


def _knobs(values: dict[str, Any] | None) -> tuple[float, float]:
    knobs = values if isinstance(values, dict) else {}
    return float(knobs.get("reverence") or 0.5), float(knobs.get("abstraction") or 0.5)


def room_size(knobs: dict[str, Any] | None = None, family: str = "") -> tuple[float, float, float]:
    reverence, abstraction = _knobs(knobs)
    width = 3.2 + abstraction * 8.8
    length = 4.0 + abstraction * 12.0
    height = 2.4 + abstraction * 1.8
    if family == "ambient":
        width += 1.5
        length += 2.0
        height += 0.4
    scale = 1.0 - 0.18 * reverence
    return width * scale, length * scale, height


def _rir(width: float, length: float, height: float, fs: int = 16000, absorption: float = 0.25) -> Any:
    import numpy as np
    import pyroomacoustics as pra

    room = pra.ShoeBox(
        [width, length, height],
        fs=fs,
        max_order=3,
        materials=pra.Material(max(0.05, min(0.85, absorption))),
    )
    src = [min(1.2, width * 0.3), min(1.2, length * 0.3), min(1.6, height * 0.55)]
    mic = [max(width - 1.2, width * 0.7), max(length - 1.2, length * 0.7), min(1.7, height * 0.62)]
    room.add_source(src)
    room.add_microphone(mic)
    room.compute_rir()
    return np.asarray(room.rir[0][0], dtype=np.float32)


def room_impulse(
    width: float = 5.0,
    length: float = 7.0,
    height: float = 2.6,
    knobs: dict[str, Any] | None = None,
    family: str = "",
) -> dict[str, Any]:
    try:
        import numpy as np
        import pyroomacoustics as pra

        if knobs is not None:
            width, length, height = room_size(knobs, family)
        reverence, _abstraction = _knobs(knobs)
        rir = _rir(width, length, height, absorption=0.18 + reverence * 0.45)
        return {
            "ok": True,
            "wrote": False,
            "backend": "pyroomacoustics",
            "samples": int(np.asarray(rir).size),
            "rt60_est": float(pra.experimental.rt60.measure_rt60(rir, fs=16000, decay_db=20)),
            "room": [width, length, height],
        }
    except Exception as exc:
        return {"ok": False, "wrote": False, "error": "pyroomacoustics_unavailable", "detail": str(exc)}


def apply_room_to_wav(
    path: str | Path,
    knobs: dict[str, Any] | None = None,
    family: str = "",
) -> dict[str, Any]:
    dest = Path(path)
    if not dest.is_file():
        return {"ok": False, "wrote": False, "error": "missing_wav"}
    try:
        import numpy as np
        import pyroomacoustics as pra
        import soundfile as sf
        from scipy.signal import fftconvolve, resample

        audio, rate = sf.read(str(dest), always_2d=True)
        reverence, abstraction = _knobs(knobs)
        width, length, height = room_size(knobs, family)
        rir = _rir(width, length, height, absorption=0.18 + reverence * 0.45)
        target = max(8, int(round(rir.size * (rate / 16000.0))))
        ir = np.asarray(resample(rir, target), dtype=np.float32)
        ir = ir[: max(8, int(rate * 0.55))]
        peak_ir = float(np.max(np.abs(ir)) or 1.0)
        ir = ir / peak_ir
        wet = min(0.62, 0.10 + abstraction * 0.42 + (0.08 if family == "ambient" else 0.0))
        dry = 1.0 - wet
        mixed = np.zeros_like(audio, dtype=np.float32)
        for channel in range(audio.shape[1]):
            wet_ch = fftconvolve(audio[:, channel], ir, mode="full")[: audio.shape[0]]
            mixed[:, channel] = dry * audio[:, channel] + wet * wet_ch
        peak = float(np.max(np.abs(mixed)) or 1.0)
        mixed = mixed * (0.89 / peak)
        sf.write(str(dest), mixed, rate)
        return {
            "ok": True,
            "wrote": True,
            "backend": "pyroomacoustics",
            "samples": int(ir.size),
            "wet": wet,
            "room": [width, length, height],
            "rt60_est": float(pra.experimental.rt60.measure_rt60(ir, fs=rate, decay_db=20)),
        }
    except Exception as exc:
        return {"ok": False, "wrote": False, "error": "pyroomacoustics_unavailable", "detail": str(exc)}
