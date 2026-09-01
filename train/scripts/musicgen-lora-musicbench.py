#!/usr/bin/env python3
"""HF Jobs entry: LoRA-tune facebook/musicgen-small on amaai-lab/MusicBench.

Runs on Hugging Face Jobs, not on the Context Cloud VM or the owner Mac.

Root-cause pin: ylacombe/musicgen-dreamboothing (2024, check_min_version 4.40)
must run on transformers 4.51.3 / datasets 3.2.0. Do not float to latest.

Flow: _assert_stack() -> preflight() -> PREFLIGHT_OK -> bulk().
Refuse MusicBench.tar.gz until PREFLIGHT_OK.

Never edit or string-patch dreamboothing. Compatibility is load_dataset shim
plus serial Dataset.map/filter shim only. Persist stays stock musicgen-small.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tarfile
import time
import wave
from pathlib import Path
from typing import Any, Callable

DATASET_ID = "amaai-lab/MusicBench"
BASE_MODEL = "facebook/musicgen-small"
ADAPTER_SLUG = "context-musicgen-small-musicbench-lora"
ADAPTER_REPO = f"cam-douglas/{ADAPTER_SLUG}"
DREAMBOOTH_REPO = "https://github.com/ylacombe/musicgen-dreamboothing.git"
MAX_TRAIN_SAMPLES = 20_000
MAX_STEPS = 2500
SEED = 456
WORK = Path("/tmp/context-musicgen-lora")
RAW = WORK / "musicbench-raw"
EXTRACT = WORK / "musicbench-audio"
PREPARED = WORK / "musicbench-hfds"
DREAM_DIR = WORK / "musicgen-dreamboothing"
PREFLIGHT_AUDIO = WORK / "preflight-audio"
PREFLIGHT_DS = WORK / "preflight-hfds"
PREFLIGHT_OUT = WORK / "preflight-out"
BULK_OUT = WORK / "bulk-out"
TRAIN_JSON_NAME = "MusicBench_train.json"
TAR_NAME = "MusicBench.tar.gz"

TRANSFORMERS_PIN = "4.51.3"
HUB_PIN = ">=0.26.0,<1.0"
DATASETS_PIN = "3.2.0"
PEFT_PIN = "0.14.0"
ACCELERATE_PIN = "1.6.0"
EXTRA_PKGS = ("evaluate", "sentencepiece", "librosa", "soundfile", "torchaudio")
UV_WITH = (
    f"transformers=={TRANSFORMERS_PIN}",
    f"huggingface_hub{HUB_PIN}",
    f"datasets=={DATASETS_PIN}",
    f"peft=={PEFT_PIN}",
    f"accelerate=={ACCELERATE_PIN}",
) + EXTRA_PKGS
FORBIDDEN_FLAGS = ("--overwrite_output_dir", "--preprocessing_num_workers")

PREFLIGHT_OK = False
_DREAM_SHA256 = ""
_SHIMS_INSTALLED = False


def _log(msg: str) -> None:
    print(msg, flush=True)


def _require_token() -> None:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        raise SystemExit("BLOCKED: missing HF_TOKEN inside the Job")


def _assert_stack() -> None:
    """Exit if the Job image floated to transformers 5 or dropped tokenizer=."""
    try:
        import transformers
        from transformers import Seq2SeqTrainer
    except Exception as exc:
        raise SystemExit(f"ERROR: transformers import failed: {exc.__class__.__name__}") from exc

    version = str(getattr(transformers, "__version__", "0"))
    try:
        major = int(version.split(".")[0])
    except ValueError:
        major = 0
    if major >= 5:
        raise SystemExit(
            f"ERROR: transformers {version} major>=5; pin transformers=={TRANSFORMERS_PIN}"
        )
    params = inspect.signature(Seq2SeqTrainer.__init__).parameters
    if "tokenizer" not in params:
        raise SystemExit(
            "ERROR: Seq2SeqTrainer lacks tokenizer=; pin "
            f"transformers=={TRANSFORMERS_PIN}"
        )
    ds_ver = ""
    try:
        import datasets

        ds_ver = str(getattr(datasets, "__version__", ""))
        ds_major = int(ds_ver.split(".")[0])
        if ds_major >= 4:
            raise SystemExit(
                f"ERROR: datasets {ds_ver} major>=4; pin datasets=={DATASETS_PIN}"
            )
    except SystemExit:
        raise
    except Exception:
        ds_ver = "unimported"
    _log(f"stack_ok transformers={version} datasets={ds_ver}")


def _username() -> str:
    from huggingface_hub import whoami

    info = whoami()
    name = info.get("name") or info.get("fullname")
    if not name:
        raise SystemExit(f"ERROR: whoami returned no name; keys={sorted(info)}")
    return str(name)


def _create_private_repo(repo_id: str) -> None:
    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(repo_id, private=True, exist_ok=True, repo_type="model")
    card = f"""---
license: cc-by-nc-4.0
base_model: {BASE_MODEL}
library_name: peft
tags:
  - text-to-audio
  - musicgen
  - lora
  - peft
datasets:
  - amaai-lab/MusicBench
---

# Context MusicGen-small MusicBench LoRA

Private LoRA adapter for [`{BASE_MODEL}`](https://huggingface.co/{BASE_MODEL})
trained on [`amaai-lab/MusicBench`](https://huggingface.co/datasets/amaai-lab/MusicBench)
(`main_caption` + `location` audio) via
[ylacombe/musicgen-dreamboothing](https://github.com/ylacombe/musicgen-dreamboothing).

## Licenses

- **Base weights (`{BASE_MODEL}`): CC-BY-NC 4.0.** This adapter is a derivative
  of those weights and is **not licensed for commercial use**.
- MusicBench captions/audio: cc-by-sa-3.0.

## Training notes

- Pinned stack: transformers=={TRANSFORMERS_PIN}, datasets=={DATASETS_PIN},
  peft=={PEFT_PIN}, accelerate=={ACCELERATE_PIN}, huggingface_hub{HUB_PIN}.
- 1 epoch intent, capped at {MAX_TRAIN_SAMPLES} rows and {MAX_STEPS} steps.
- LoRA, fp16, gradient checkpointing, batch 1, grad accum 8, lr 2e-4.
- `guidance_scale=1.0` (dreamboothing FAQ: NaNs on some non-melody checkpoints).
- `max_duration_in_seconds=10` (MusicBench clips are short).
- Persist remains stock `{BASE_MODEL}`. This adapter is not applied by the Job.
"""
    api.upload_file(
        path_or_fileobj=card.encode("utf-8"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
    )
    _log(f"private adapter repo ready: {repo_id}")


def _write_sine(path: Path, sr: int = 32000, seconds: float = 2.0, freq: float = 440.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = int(sr * seconds)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sr)
        frames = b"".join(
            struct.pack(
                "<h",
                int(32767 * 0.2 * math.sin(2.0 * math.pi * freq * i / sr)),
            )
            for i in range(n)
        )
        handle.writeframes(frames)


def _decode_wav(path: Path) -> tuple[int, int]:
    with wave.open(str(path), "r") as handle:
        nframes = handle.getnframes()
        rate = handle.getframerate()
        frames = handle.readframes(nframes)
    if nframes < 1 or not frames:
        raise SystemExit(f"ERROR: audio decode empty: {path}")
    return rate, nframes


def _load_dataset_shim(original: Callable[..., Any]) -> Callable[..., Any]:
    def wrapped(path_or_name: Any = None, *args: Any, **kwargs: Any) -> Any:
        from datasets import load_from_disk

        if path_or_name is None:
            return original(path_or_name, *args, **kwargs)
        candidate = Path(str(path_or_name))
        if candidate.exists() and (
            (candidate / "dataset_dict.json").exists() or (candidate / "state.json").exists()
        ):
            loaded = load_from_disk(str(candidate))
            split = kwargs.get("split")
            keys = list(getattr(loaded, "keys", lambda: [])())
            if split and split in keys:
                return loaded[split]
            if "train" in keys:
                return loaded["train"]
            return loaded
        return original(path_or_name, *args, **kwargs)

    return wrapped


def _serial_call(original: Callable[..., Any]) -> Callable[..., Any]:
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        kwargs.pop("num_proc", None)
        return original(*args, **kwargs)

    return wrapped


def _install_shims() -> None:
    """Patch datasets in-process. Do not write dreamboothing source."""
    global _SHIMS_INSTALLED
    import datasets
    from datasets import Dataset, DatasetDict

    datasets.load_dataset = _load_dataset_shim(datasets.load_dataset)
    Dataset.map = _serial_call(Dataset.map)
    Dataset.filter = _serial_call(Dataset.filter)
    DatasetDict.map = _serial_call(DatasetDict.map)
    DatasetDict.filter = _serial_call(DatasetDict.filter)
    _SHIMS_INSTALLED = True
    _log("shims_installed load_dataset + serial map/filter")


def _trainer_argv(
    *,
    dataset_name: str,
    output_dir: str,
    max_steps: int,
    max_train_samples: int,
    push_to_hub: bool,
    hub_model_id: str | None = None,
) -> list[str]:
    argv = [
        "--use_lora",
        "--model_name_or_path",
        BASE_MODEL,
        "--dataset_name",
        dataset_name,
        "--text_column_name",
        "main_caption",
        "--target_audio_column_name",
        "location",
        "--train_split_name",
        "train",
        "--do_train",
        "--num_train_epochs",
        "1",
        "--max_steps",
        str(max_steps),
        "--max_train_samples",
        str(max_train_samples),
        "--fp16",
        "--gradient_checkpointing",
        "--per_device_train_batch_size",
        "1",
        "--gradient_accumulation_steps",
        "8",
        "--learning_rate",
        "2e-4",
        "--guidance_scale",
        "1.0",
        "--max_duration_in_seconds",
        "10",
        "--min_duration_in_seconds",
        "1.0",
        "--pad_token_id",
        "2048",
        "--decoder_start_token_id",
        "2048",
        "--output_dir",
        output_dir,
        "--report_to",
        "none",
        "--logging_steps",
        "10",
        "--save_steps",
        "500",
        "--save_total_limit",
        "2",
        "--dataloader_num_workers",
        "0",
        "--seed",
        str(SEED),
    ]
    if push_to_hub:
        if not hub_model_id:
            raise SystemExit("ERROR: hub_model_id required when push_to_hub")
        argv.extend(
            [
                "--push_to_hub",
                "--hub_model_id",
                hub_model_id,
                "--hub_private_repo",
                "true",
            ]
        )
    for flag in FORBIDDEN_FLAGS:
        if flag in argv:
            raise SystemExit(f"ERROR: forbidden flag leaked into argv: {flag}")
    return argv


def _clone_dreamboothing() -> Path:
    if DREAM_DIR.exists():
        shutil.rmtree(DREAM_DIR)
    subprocess.check_call(["git", "clone", "--depth", "1", DREAMBOOTH_REPO, str(DREAM_DIR)])
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=DREAM_DIR, text=True).strip()
    _log(f"cloned musicgen-dreamboothing @ {sha}")
    script = DREAM_DIR / "dreambooth_musicgen.py"
    if not script.is_file():
        raise SystemExit("ERROR: dreambooth_musicgen.py missing after clone")
    return script


def _dream_sha256(script: Path) -> str:
    return hashlib.sha256(script.read_bytes()).hexdigest()


def _assert_dreamboothing_untouched(script: Path) -> None:
    current = _dream_sha256(script)
    if _DREAM_SHA256 and current != _DREAM_SHA256:
        raise SystemExit("ERROR: dreamboothing source changed; wrapper must not edit it")


def _ast_compile(script: Path) -> None:
    source = script.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(script))
    compile(tree, str(script), "exec")
    _log(f"ast_compile_ok {script.name}")


def _import_trainer(script: Path) -> Any:
    if str(DREAM_DIR) not in sys.path:
        sys.path.insert(0, str(DREAM_DIR))
    spec = importlib.util.spec_from_file_location("dreambooth_musicgen", script)
    if spec is None or spec.loader is None:
        raise SystemExit("ERROR: cannot load dreambooth_musicgen")
    module = importlib.util.module_from_spec(spec)
    sys.modules["dreambooth_musicgen"] = module
    spec.loader.exec_module(module)
    if hasattr(module, "load_dataset"):
        import datasets

        module.load_dataset = datasets.load_dataset
    _log("import_trainer_ok dreambooth_musicgen")
    return module


def _parse_real_flags(module: Any, argv: list[str]) -> None:
    from transformers import HfArgumentParser, Seq2SeqTrainingArguments

    parser = HfArgumentParser(
        (module.ModelArguments, module.DataSeq2SeqTrainingArguments, Seq2SeqTrainingArguments)
    )
    parser.parse_args_into_dataclasses(args=argv)
    _log("hf_argument_parser_ok")


def _save_local_dataset(rows: list[dict[str, str]], dest: Path) -> None:
    from datasets import Audio, Dataset, DatasetDict

    if dest.exists():
        shutil.rmtree(dest)
    ds = Dataset.from_list(rows)
    ds = ds.cast_column("location", Audio())
    DatasetDict({"train": ds}).save_to_disk(str(dest))
    _log(f"saved DatasetDict dest={dest} rows={len(ds)}")


def _run_trainer(module: Any, argv: list[str]) -> None:
    old = sys.argv
    try:
        sys.argv = ["dreambooth_musicgen.py", *argv]
        module.main()
    finally:
        sys.argv = old


def _refuse_tar_until_preflight() -> None:
    if not PREFLIGHT_OK:
        raise SystemExit("REFUSED: MusicBench.tar.gz until PREFLIGHT_OK")


def _download_musicbench() -> tuple[Path, Path]:
    _refuse_tar_until_preflight()
    from huggingface_hub import hf_hub_download

    RAW.mkdir(parents=True, exist_ok=True)
    _log(f"downloading {TRAIN_JSON_NAME} from {DATASET_ID} (metadata only first)")
    train_json = Path(
        hf_hub_download(
            repo_id=DATASET_ID,
            filename=TRAIN_JSON_NAME,
            repo_type="dataset",
            local_dir=str(RAW),
        )
    )
    _log(f"downloading {TAR_NAME} from {DATASET_ID} inside the Job (not the submit VM)")
    tar_path = Path(
        hf_hub_download(
            repo_id=DATASET_ID,
            filename=TAR_NAME,
            repo_type="dataset",
            local_dir=str(RAW),
        )
    )
    return train_json, tar_path


def _extract_tar(tar_path: Path) -> Path:
    EXTRACT.mkdir(parents=True, exist_ok=True)
    _log(f"extracting {tar_path} -> {EXTRACT}")
    with tarfile.open(tar_path, "r:gz") as tf:
        tf.extractall(EXTRACT)
    wavs = list(EXTRACT.rglob("*.wav"))
    _log(f"extracted wav count={len(wavs)}")
    if not wavs:
        raise SystemExit("ERROR: MusicBench tar contained no wav files")
    return EXTRACT


def _audio_root(extract_dir: Path) -> Path:
    probe = extract_dir / "data_aug2"
    if probe.is_dir():
        return extract_dir
    nested = list(extract_dir.glob("*/data_aug2"))
    if nested:
        return nested[0].parent
    return extract_dir


def _prepare_dataset(train_json: Path, extract_dir: Path) -> None:
    rows: list[dict[str, str]] = []
    with train_json.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    _log(f"train json rows={len(rows)} keys={sorted(rows[0].keys()) if rows else []}")
    root = _audio_root(extract_dir)
    kept: list[dict[str, str]] = []
    missing = 0
    for row in rows:
        rel = row.get("location")
        caption = row.get("main_caption")
        if not rel or not caption:
            continue
        abs_path = root / rel
        if not abs_path.is_file():
            missing += 1
            continue
        kept.append({"location": str(abs_path), "main_caption": caption})
    _log(f"resolvable rows={len(kept)} missing_wav={missing} audio_root={root}")
    if len(kept) < 100:
        raise SystemExit(f"ERROR: too few resolvable wav+caption rows ({len(kept)})")
    if len(kept) > MAX_TRAIN_SAMPLES:
        kept = kept[:MAX_TRAIN_SAMPLES]
    _save_local_dataset(kept, PREPARED)


def preflight() -> None:
    """Clone, compile, import, parse flags, decode 2 sines, 1-step smoke, no Hub push."""
    global PREFLIGHT_OK, _DREAM_SHA256

    PREFLIGHT_OK = False
    WORK.mkdir(parents=True, exist_ok=True)
    script = _clone_dreamboothing()
    _DREAM_SHA256 = _dream_sha256(script)
    _ast_compile(script)
    _install_shims()
    module = _import_trainer(script)

    stamp = str(int(time.time()))
    out_dir = PREFLIGHT_OUT / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    PREFLIGHT_AUDIO.mkdir(parents=True, exist_ok=True)
    wav1 = PREFLIGHT_AUDIO / "sine_a.wav"
    wav2 = PREFLIGHT_AUDIO / "sine_b.wav"
    _write_sine(wav1, freq=440.0)
    _write_sine(wav2, freq=660.0)
    for wav in (wav1, wav2):
        rate, nframes = _decode_wav(wav)
        _log(f"audio_decode_ok path={wav.name} rate={rate} nframes={nframes}")

    _save_local_dataset(
        [
            {"location": str(wav1), "main_caption": "a short sine tone"},
            {"location": str(wav2), "main_caption": "another short sine tone"},
        ],
        PREFLIGHT_DS,
    )
    argv = _trainer_argv(
        dataset_name=str(PREFLIGHT_DS),
        output_dir=str(out_dir),
        max_steps=1,
        max_train_samples=2,
        push_to_hub=False,
    )
    _parse_real_flags(module, argv)
    _log("preflight_smoke_start max_steps=1 no_hub_push")
    _run_trainer(module, argv)
    _assert_dreamboothing_untouched(script)
    PREFLIGHT_OK = True
    _log("PREFLIGHT_OK")


def bulk() -> None:
    """Download MusicBench inside the Job only after PREFLIGHT_OK."""
    _refuse_tar_until_preflight()
    user = _username()
    repo_id = f"{user}/{ADAPTER_SLUG}"
    if repo_id != ADAPTER_REPO:
        _log(f"WARN: whoami repo {repo_id} differs from intended {ADAPTER_REPO}")
    _log(f"hub user={user} adapter={repo_id}")
    _create_private_repo(repo_id)
    train_json, tar_path = _download_musicbench()
    extract_dir = _extract_tar(tar_path)
    _prepare_dataset(train_json, extract_dir)
    script = DREAM_DIR / "dreambooth_musicgen.py"
    _assert_dreamboothing_untouched(script)
    if not _SHIMS_INSTALLED:
        _install_shims()
    module = sys.modules.get("dreambooth_musicgen")
    if module is None:
        module = _import_trainer(script)
    stamp = str(int(time.time()))
    out_dir = BULK_OUT / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    argv = _trainer_argv(
        dataset_name=str(PREPARED),
        output_dir=str(out_dir),
        max_steps=MAX_STEPS,
        max_train_samples=MAX_TRAIN_SAMPLES,
        push_to_hub=True,
        hub_model_id=repo_id,
    )
    _parse_real_flags(module, argv)
    _log("bulk_train_start")
    _run_trainer(module, argv)
    _assert_dreamboothing_untouched(script)
    _log(f"training process returned; adapter intended at {repo_id}")


def main() -> None:
    _log(f"host={BASE_MODEL} dataset={DATASET_ID} persist=stock-no-apply")
    _log(
        f"caps: max_train_samples={MAX_TRAIN_SAMPLES} max_steps={MAX_STEPS} "
        f"pins={' '.join(UV_WITH)}"
    )
    _require_token()
    _assert_stack()
    preflight()
    bulk()


if __name__ == "__main__":
    main()
