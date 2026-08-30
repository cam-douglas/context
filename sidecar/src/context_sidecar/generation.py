"""Rotate the active music generator for owner performance tests."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from context_sidecar.prompt_policy import apply_policy, assemble_conditioned, assemble_negative, suggestion_block
from context_sidecar.progress import begin as progress_begin
from context_sidecar.progress import finish as progress_finish
from context_sidecar.progress import mark_preview as progress_mark_preview
from context_sidecar.progress import preview_wav_path
from context_sidecar.progress import update as progress_update
from context_sidecar.render_dsp import render_wav as render_symbolic

GENERATORS = (
    {"id": "pedalboard", "label": "Pedalboard + symbolic (baseline)"},
    {"id": "musicgen", "label": "MusicGen (Meta AudioCraft / transformers)"},
    {"id": "stable_audio_open", "label": "Stable Audio Open (Stability AI)"},
    {"id": "audioldm2", "label": "AudioLDM 2 (CVSSP / diffusers)"},
    {"id": "suno", "label": "Suno API"},
    {"id": "udio", "label": "Udio API"},
    {"id": "elevenlabs", "label": "ElevenLabs sound effects"},
)

STATE_PATH = Path.home() / "Library/Application Support/Context/generation-rotate.json"
PERF_PATH = Path.home() / "Library/Application Support/Context/generation-perf.jsonl"


def _state_path() -> Path:
    raw = os.environ.get("CONTEXT_GENERATOR_STATE", "").strip()
    return Path(raw) if raw else STATE_PATH


def _load() -> dict[str, Any]:
    path = _state_path()
    if path.is_file():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            pass
    return {"index": 0, "id": GENERATORS[0]["id"]}


def _save(state: dict[str, Any]) -> None:
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n")


def current_generator() -> dict[str, Any]:
    forced = os.environ.get("CONTEXT_GENERATOR", "").strip()
    if forced:
        for index, item in enumerate(GENERATORS):
            if item["id"] == forced:
                return {**item, "index": index, "count": len(GENERATORS), "forced": True}
    state = _load()
    index = int(state.get("index") or 0) % len(GENERATORS)
    item = GENERATORS[index]
    return {**item, "index": index, "count": len(GENERATORS), "forced": False}


def rotate() -> dict[str, Any]:
    state = _load()
    index = (int(state.get("index") or 0) + 1) % len(GENERATORS)
    item = GENERATORS[index]
    next_state = {
        "index": index,
        "id": item["id"],
        "rotated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save(next_state)
    return {**item, "index": index, "count": len(GENERATORS), "rotated_at": next_state["rotated_at"]}


def _log_perf(entry: dict[str, Any]) -> None:
    PERF_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PERF_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def generate_wav(prompt: str, plan: dict[str, Any], notes: list[dict[str, Any]], dest: Path) -> dict[str, Any]:
    generator = current_generator()
    started = time.perf_counter()
    result: dict[str, Any] = {
        "id": generator["id"],
        "label": generator["label"],
        "ok": False,
        "fallback": None,
    }
    progress_begin(generator["id"], steps=0, message="starting")
    try:
        if generator["id"] == "pedalboard":
            result["backend"] = render_symbolic(plan, notes, dest)
            result["ok"] = True
        else:
            result.update(_try_model(generator["id"], prompt, dest, plan))
    except Exception as exc:
        result["error"] = str(exc)
        result["ok"] = False
    progress_finish(ok=bool(result.get("ok")), message="done" if result.get("ok") else str(result.get("error") or "failed"))
    result["seconds"] = round(time.perf_counter() - started, 3)
    _log_perf(
        {
            "at": datetime.now(timezone.utc).isoformat(),
            "id": generator["id"],
            "ok": bool(result.get("ok")),
            "seconds": result["seconds"],
            "error": result.get("error"),
            "fallback": result.get("fallback"),
            "prompt": prompt[:80],
        }
    )
    return result


def run_generator(generator_id: str, prompt: str, dest: Path, plan: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = plan if isinstance(plan, dict) else {"tempo_bpm": 120.0, "style": "melody", "family": "melody"}
    if generator_id == "pedalboard":
        notes = payload.get("notes") or [{"pitch": 60, "start": 0.0, "length": 1.0, "velocity": 90}]
        return {"ok": True, "id": "pedalboard", "backend": render_symbolic(payload, notes, dest)}
    result = _try_model(generator_id, prompt, dest, payload)
    return {"id": generator_id, **result}


def _try_model(generator_id: str, prompt: str, dest: Path, plan: dict[str, Any]) -> dict[str, Any]:
    if generator_id == "musicgen":
        return _musicgen(prompt, dest, plan)
    if generator_id == "stable_audio_open":
        return _stable_audio_open(prompt, dest, plan)
    if generator_id == "audioldm2":
        return _audioldm2(prompt, dest, plan)
    env = {
        "suno": "SUNO_API_KEY",
        "udio": "UDIO_API_KEY",
        "elevenlabs": "ELEVENLABS_API_KEY",
    }.get(generator_id)
    if env and not os.environ.get(env, "").strip():
        return {"ok": False, "error": "missing_env", "env_name": env}
    if env:
        return {"ok": False, "error": "commercial_adapter_not_called", "env_name": env}
    return {"ok": False, "error": f"unknown_generator:{generator_id}"}


_MUSICGEN_PIPE = None
MUSICGEN_FRAMES_PER_SEC = 50
MUSICGEN_MAX_TOKENS = 1500


def _musicgen_prompt(prompt: str, plan: dict[str, Any]) -> str:
    if not str(plan.get("system_prompt") or "").strip():
        apply_policy(plan, None)
    return assemble_conditioned(prompt, plan)


def _fit_length(data, rate: int, seconds: float):
    import numpy as np

    target = max(1, int(round(seconds * rate)))
    if data.shape[-1] == target:
        return data
    if data.shape[-1] > target:
        return data[..., :target]
    repeats = int(np.ceil(target / data.shape[-1]))
    tiled = np.tile(data, (1, repeats) if data.ndim == 2 else repeats)
    return tiled[..., :target]


def _as_stereo(waveform):
    import numpy as np

    wave = np.asarray(waveform, dtype=np.float32)
    wave = np.nan_to_num(wave, nan=0.0, posinf=0.0, neginf=0.0)
    if wave.ndim == 0 or wave.size < 32:
        return None
    if wave.ndim == 1:
        wave = np.stack([wave, wave])
    elif wave.ndim == 2 and wave.shape[0] > wave.shape[1]:
        wave = wave.T
    elif wave.ndim > 2:
        wave = wave.reshape(wave.shape[0], -1)
        if wave.shape[0] > 2:
            wave = wave[:2]
    peak = float(np.max(np.abs(wave)))
    if peak < 1e-4:
        return None
    if peak > 1.0:
        wave = wave * (0.89 / peak)
    return wave


def _write_pcm16(dest: Path, waveform, rate: int) -> bool:
    stereo = _as_stereo(waveform)
    if stereo is None:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        import soundfile as sf

        tmp = dest.with_suffix(".tmp.wav")
        sf.write(str(tmp), stereo.T, int(rate), subtype="PCM_16")
        tmp.replace(dest)
        return dest.is_file() and dest.stat().st_size >= 1000
    except Exception:
        return False


def _cpu_vae_vocoder(pipe) -> None:
    try:
        pipe.vae.to("cpu")
        pipe.vocoder.to("cpu")
    except Exception:
        pass


def _decode_audioldm2_latents(pipe, latents, seconds: float):
    import numpy as np
    import torch

    if latents is None:
        return None
    raw = latents[0] if isinstance(latents, (list, tuple)) else latents
    if hasattr(raw, "detach"):
        tensor = raw.detach()
        if int(getattr(tensor, "ndim", 0)) >= 3:
            _cpu_vae_vocoder(pipe)
            vae = getattr(pipe, "vae", None)
            scaling = float(getattr(getattr(vae, "config", None), "scaling_factor", 1.0) or 1.0)
            batch = tensor[-1:].to("cpu", dtype=torch.float32)
            with torch.no_grad():
                mel = pipe.vae.decode(batch / scaling).sample
                if mel.dim() == 4:
                    mel = mel.squeeze(1)
                audio = pipe.vocoder(mel)
            wave = np.asarray(audio.detach().cpu().float())
        else:
            wave = np.asarray(tensor.detach().cpu().float())
    else:
        wave = np.asarray(raw)
    if wave.ndim >= 3:
        return None
    if wave.ndim == 2 and wave.shape[0] > 8 and wave.shape[0] > wave.shape[-1]:
        wave = wave[0]
    stereo = _as_stereo(wave)
    if stereo is None:
        return None
    rate = int(getattr(getattr(getattr(pipe, "vocoder", None), "config", None), "sampling_rate", None) or 16000)
    return _fit_length(stereo, rate, max(1.0, float(seconds))), rate


_SAO_PIPE = None
_AUDIOLDM2_PIPE = None
_PIPE_LOCK = threading.Lock()
STABLE_AUDIO_MODEL = "stabilityai/stable-audio-open-1.0"
AUDIOLDM2_MODEL = "cvssp/audioldm2-music"


def _model_cache() -> str:
    cache = os.environ.get("CONTEXT_MODEL_CACHE_DIR", "").strip() or str(
        Path.home() / "Library/Application Support/Context/models"
    )
    Path(cache).mkdir(parents=True, exist_ok=True)
    token_path = Path.home() / ".cache/huggingface/token"
    if token_path.is_file() and not os.environ.get("HF_TOKEN", "").strip():
        os.environ["HF_TOKEN"] = token_path.read_text().strip()
    return cache


def _torch_device():
    import torch

    if torch.backends.mps.is_available():
        return "mps", torch.float32
    if torch.cuda.is_available():
        return "cuda", torch.float16
    return "cpu", torch.float32


def _hub_cache_ready(model_id: str) -> bool:
    cache = Path(_model_cache()) / f"models--{model_id.replace('/', '--')}"
    return cache.is_dir() and any(cache.rglob("model_index.json"))


def _load_diffusers(cls, model_id: str, dtype):
    cache = _model_cache()
    local_only = _hub_cache_ready(model_id)
    kwargs = {"cache_dir": cache, "local_files_only": local_only}
    try:
        return cls.from_pretrained(model_id, dtype=dtype, **kwargs)
    except TypeError:
        return cls.from_pretrained(model_id, torch_dtype=dtype, **kwargs)
    except Exception:
        if not local_only:
            raise
        try:
            return cls.from_pretrained(model_id, dtype=dtype, cache_dir=cache)
        except TypeError:
            return cls.from_pretrained(model_id, torch_dtype=dtype, cache_dir=cache)


def _sao_pipe():
    global _SAO_PIPE
    if _SAO_PIPE is not None:
        return _SAO_PIPE
    from diffusers import StableAudioPipeline

    device, dtype = _torch_device()
    pipe = StableAudioPipeline.from_pretrained(STABLE_AUDIO_MODEL, dtype=dtype, cache_dir=_model_cache())
    pipe = pipe.to(device)
    if device == "mps":
        pipe.enable_attention_slicing()
    _SAO_PIPE = pipe
    return pipe


def _audioldm2_pipe():
    global _AUDIOLDM2_PIPE
    if _AUDIOLDM2_PIPE is not None:
        return _AUDIOLDM2_PIPE
    with _PIPE_LOCK:
        if _AUDIOLDM2_PIPE is not None:
            return _AUDIOLDM2_PIPE
        from diffusers.pipelines.audioldm2.pipeline_audioldm2 import AudioLDM2Pipeline

        device, dtype = _torch_device()
        pipe = _load_diffusers(AudioLDM2Pipeline, AUDIOLDM2_MODEL, dtype)
        pipe = pipe.to(device)
        if device == "mps":
            pipe.enable_attention_slicing()
        _patch_audioldm2_language_model(pipe)
        _AUDIOLDM2_PIPE = pipe
        return pipe


def _patch_audioldm2_language_model(pipe) -> None:
    """cvssp/audioldm2-music ships GPT2Model, which lacks GenerationMixin on transformers 5."""
    lm = getattr(pipe, "language_model", None)
    if lm is None or hasattr(lm, "_update_model_kwargs_for_generation"):
        return
    try:
        from transformers.generation.utils import GenerationMixin

        lm._update_model_kwargs_for_generation = GenerationMixin._update_model_kwargs_for_generation.__get__(
            lm, type(lm)
        )
        return
    except Exception:
        pass

    def _update(outputs, model_kwargs, **_kwargs):
        import torch

        past = getattr(outputs, "past_key_values", None)
        if past is not None:
            model_kwargs["past_key_values"] = past
        mask = model_kwargs.get("attention_mask")
        if mask is not None:
            model_kwargs["attention_mask"] = torch.cat([mask, mask.new_ones((mask.shape[0], 1))], dim=-1)
        return model_kwargs

    lm._update_model_kwargs_for_generation = _update


def _audioldm2_prompt(prompt: str, plan: dict[str, Any]) -> str:
    if not str(plan.get("system_prompt") or "").strip():
        apply_policy(plan, None)
    # CLAP 512 / T5 128. Put the typed request first so it is not drowned by the template.
    request = (prompt or "").strip()
    bars = int(plan.get("bars") or 4)
    tempo = float(plan.get("tempo_bpm") or 120.0)
    key = str(plan.get("key") or "Am")
    style = str(plan.get("style") or "").strip()
    extra = " ".join(plan.get("genres") or []).strip()
    parts = [request] if request else []
    parts.append(f"{bars}-bar {style} instrumental, {key}, {tempo:.0f} bpm")
    if extra:
        parts.append(extra)
    return ". ".join(part for part in parts if part).strip()[:400]


def _prompt_seed(prompt: str, plan: dict[str, Any]) -> int:
    try:
        raw = int(plan.get("seed") or 0)
    except (TypeError, ValueError):
        raw = 0
    if raw:
        return raw
    import hashlib

    return int(hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()[:8], 16)


def _audioldm2_negative(plan: dict[str, Any]) -> str:
    return assemble_negative(plan)[:200]


def _copy_to_preview(source: Path) -> None:
    dest = preview_wav_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        dest.write_bytes(source.read_bytes())
        progress_mark_preview()
    except OSError:
        pass


def _write_numpy_preview(waveform, rate: int) -> bool:
    dest = preview_wav_path()
    if not _write_pcm16(dest, waveform, rate):
        return False
    progress_mark_preview()
    return True


def _write_audioldm2_preview(pipe, latents, seconds: float) -> bool:
    try:
        decoded = _decode_audioldm2_latents(pipe, latents, seconds)
        if decoded is None:
            return False
        waveform, rate = decoded
        return _write_numpy_preview(waveform, rate)
    except Exception:
        return False


def _audioldm2(prompt: str, dest: Path, plan: dict[str, Any]) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        import torch
    except Exception as exc:
        return {"ok": False, "error": f"audioldm2_import:{exc.__class__.__name__}"}

    wanted = min(20.0, max(1.0, float(plan.get("duration_sec") or 8.0)))
    seconds = min(8.0, max(1.0, wanted))
    steps = max(8, int(os.environ.get("CONTEXT_AUDIOLDM2_STEPS") or 24))
    progress_update(steps=steps, phase="loading", message="loading AudioLDM 2")
    try:
        pipe = _audioldm2_pipe()
    except Exception as exc:
        return {
            "ok": False,
            "error": f"audioldm2_load:{exc.__class__.__name__}",
            "detail": str(exc)[:240],
        }

    conditioned = _audioldm2_prompt(prompt, plan)
    generator = torch.Generator(device="cpu").manual_seed(_prompt_seed(prompt, plan))
    progress_update(step=0, steps=steps, phase="denoise", message="generating")
    _cpu_vae_vocoder(pipe)

    def _on_step(step: int, _timestep, latents) -> None:
        done = step + 1
        progress_update(step=done, steps=steps, phase="denoise", message=f"step {done} of {steps}")
        if done >= 4 and (done % 4 == 0 or done == steps):
            _write_audioldm2_preview(pipe, latents, seconds)

    try:
        output = pipe(
            conditioned,
            negative_prompt=_audioldm2_negative(plan),
            num_inference_steps=steps,
            audio_length_in_s=seconds,
            num_waveforms_per_prompt=1,
            guidance_scale=6.0,
            generator=generator,
            output_type="latent",
            callback=_on_step,
            callback_steps=1,
        )
    except Exception as exc:
        return {
            "ok": False,
            "error": f"audioldm2_infer:{exc.__class__.__name__}",
            "detail": str(exc)[:240],
        }
    decoded = _decode_audioldm2_latents(pipe, getattr(output, "audios", None), seconds)
    if decoded is None:
        return {"ok": False, "error": "audioldm2_silent"}
    waveform, rate = decoded
    waveform = _fit_length(waveform, rate, wanted)
    if not _write_pcm16(dest, waveform, rate):
        return {"ok": False, "error": "audioldm2_empty"}
    _copy_to_preview(dest)
    return {
        "ok": True,
        "backend": "audioldm2-music",
        "duration_sec": round(wanted, 3),
        "steps": steps,
        "conditioned_prompt": conditioned,
    }


def _stable_audio_open(prompt: str, dest: Path, plan: dict[str, Any]) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        import numpy as np
        import soundfile as sf
        import torch
    except Exception as exc:
        return {"ok": False, "error": f"stable_audio_import:{exc.__class__.__name__}"}

    wanted = min(47.0, max(1.0, float(plan.get("duration_sec") or 8.0)))
    seconds = min(47.0, max(8.0, wanted))
    pipe = _sao_pipe()
    try:
        from diffusers import DDIMScheduler

        pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
    except Exception:
        pass
    conditioned = _musicgen_prompt(prompt, plan)
    steps = max(8, int(os.environ.get("CONTEXT_SAO_STEPS") or 80))
    generator = torch.Generator(device="cpu").manual_seed(int(plan.get("seed") or 0))
    progress_update(step=0, steps=steps, phase="denoise", message="generating")

    def _on_step(step: int, _timestep, _latents) -> None:
        done = step + 1
        progress_update(step=done, steps=steps, phase="denoise", message=f"step {done} of {steps}")

    audio = pipe(
        conditioned,
        negative_prompt=assemble_negative(plan),
        num_inference_steps=steps,
        audio_end_in_s=seconds,
        num_waveforms_per_prompt=1,
        generator=generator,
        callback=_on_step,
        callback_steps=1,
    ).audios
    waveform = audio[0].float().cpu().numpy()
    if waveform.ndim == 1:
        waveform = np.stack([waveform, waveform])
    elif waveform.ndim == 2 and waveform.shape[0] > waveform.shape[1]:
        waveform = waveform.T
    rate = int(getattr(getattr(pipe, "vae", None), "sampling_rate", None) or 44100)
    waveform = _fit_length(waveform, rate, wanted)
    sf.write(str(dest), waveform.T if waveform.shape[0] <= 2 else waveform, rate)
    if not dest.is_file() or dest.stat().st_size < 1000:
        return {"ok": False, "error": "stable_audio_empty"}
    return {
        "ok": True,
        "backend": "stable-audio-open-1.0",
        "duration_sec": round(wanted, 3),
        "steps": steps,
        "conditioned_prompt": conditioned,
    }


def _musicgen_pipe():
    global _MUSICGEN_PIPE
    if _MUSICGEN_PIPE is not None:
        return _MUSICGEN_PIPE
    from transformers import pipeline

    cache = os.environ.get("CONTEXT_MODEL_CACHE_DIR", "").strip() or str(
        Path.home() / "Library/Application Support/Context/models"
    )
    os.environ.setdefault("HF_HOME", cache)
    _MUSICGEN_PIPE = pipeline("text-to-audio", model="facebook/musicgen-small")
    return _MUSICGEN_PIPE


def _musicgen(prompt: str, dest: Path, plan: dict[str, Any]) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        import numpy as np
        import soundfile as sf
    except Exception as exc:
        return {"ok": False, "error": f"musicgen_import:{exc.__class__.__name__}"}

    seconds = float(plan.get("duration_sec") or 8.0)
    tokens = max(64, min(MUSICGEN_MAX_TOKENS, int(round(seconds * MUSICGEN_FRAMES_PER_SEC))))
    progress_update(step=0, steps=max(1, int(round(seconds))), phase="denoise", message="generating")
    pipe = _musicgen_pipe()
    conditioned = _musicgen_prompt(prompt, plan)
    chunks: list[Any] = []
    remaining = seconds
    rate = 32000
    while remaining > 0.25:
        chunk_seconds = min(remaining, MUSICGEN_MAX_TOKENS / MUSICGEN_FRAMES_PER_SEC)
        chunk_tokens = max(64, min(MUSICGEN_MAX_TOKENS, int(round(chunk_seconds * MUSICGEN_FRAMES_PER_SEC))))
        audio = pipe(conditioned, forward_params={"max_new_tokens": chunk_tokens or tokens})
        data = np.asarray(audio["audio"])
        rate = int(audio.get("sampling_rate") or 32000)
        if data.ndim == 1:
            data = np.stack([data, data])
        elif data.ndim == 2 and data.shape[0] > data.shape[1]:
            data = data.T
        chunks.append(data)
        remaining -= data.shape[-1] / rate
        made = max(0.0, seconds - remaining)
        progress_update(
            step=max(1, int(round(made))),
            steps=max(1, int(round(seconds))),
            phase="denoise",
            message=f"{made:.0f}s of {seconds:.0f}s",
        )
        preview = np.concatenate(chunks, axis=1)
        if _write_numpy_preview(preview, rate):
            progress_mark_preview()
        if data.shape[-1] / rate < 0.5:
            break
    if not chunks:
        return {"ok": False, "error": "musicgen_empty"}
    stereo = np.concatenate(chunks, axis=1)
    stereo = _fit_length(stereo, rate, seconds)
    sf.write(str(dest), stereo.T if stereo.shape[0] <= 2 else stereo, rate)
    return {
        "ok": True,
        "backend": "musicgen-small",
        "duration_sec": round(seconds, 3),
        "tokens": tokens,
        "conditioned_prompt": conditioned,
    }
