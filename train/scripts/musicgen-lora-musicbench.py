#!/usr/bin/env python3
"""HF Jobs entry: LoRA-tune facebook/musicgen-small on amaai-lab/MusicBench.

This script is meant to run on Hugging Face Jobs, not on the Context Cloud VM
or the owner Mac. It:

1. Resolves the logged-in Hub user (never prints HF_TOKEN).
2. Creates a PRIVATE adapter repo.
3. Downloads MusicBench metadata + MusicBench.tar.gz inside the Job.
4. Rewrites the ``location`` column to absolute wav paths and saves a local
   DatasetDict for dreamboothing.
5. Clones ylacombe/musicgen-dreamboothing and runs ``dreambooth_musicgen.py``.

MusicBench Hub files are JSONL + a 16.7 GB tar (not parquet audio). Caption
column is ``main_caption``. Audio column is ``location``
(e.g. ``data_aug2/<id>.wav``).

Budget cap: 20_000 train rows and 2500 optimizer steps (batch 1, grad accum 8)
so wall time stays under the 16h Job timeout. A full 52_768-row epoch would be
6596 steps plus a full-set EnCodec map.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

DATASET_ID = "amaai-lab/MusicBench"
BASE_MODEL = "facebook/musicgen-small"
ADAPTER_SLUG = "context-musicgen-small-musicbench-lora"
DREAMBOOTH_REPO = "https://github.com/ylacombe/musicgen-dreamboothing.git"
MAX_TRAIN_SAMPLES = 20_000
MAX_STEPS = 2500
SEED = 456
WORK = Path("/tmp/context-musicgen-lora")
RAW = WORK / "musicbench-raw"
EXTRACT = WORK / "musicbench-audio"
PREPARED = WORK / "musicbench-hfds"
DREAM_DIR = WORK / "musicgen-dreamboothing"
OUT_DIR = Path("/tmp/musicgen-lora")
TRAIN_JSON_NAME = "MusicBench_train.json"
TAR_NAME = "MusicBench.tar.gz"


def _log(msg: str) -> None:
    print(msg, flush=True)


def _require_token() -> None:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        raise SystemExit("BLOCKED: missing HF_TOKEN inside the Job")


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

- 1 epoch intent, capped at {MAX_TRAIN_SAMPLES} rows and {MAX_STEPS} steps.
- LoRA, fp16, gradient checkpointing, batch 1, grad accum 8, lr 2e-4.
- `guidance_scale=1.0` (dreamboothing FAQ: NaNs on some non-melody checkpoints).
- `max_duration_in_seconds=10` (MusicBench clips are short).
"""
    api.upload_file(
        path_or_fileobj=card.encode("utf-8"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
    )
    _log(f"private adapter repo ready: {repo_id}")


def _download_musicbench() -> tuple[Path, Path]:
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
    # MusicBench tar typically contains data_aug2/*.wav at the root or one down.
    wavs = list(EXTRACT.rglob("*.wav"))
    _log(f"extracted wav count={len(wavs)}")
    if not wavs:
        raise SystemExit("ERROR: MusicBench tar contained no wav files")
    return EXTRACT


def _audio_root(extract_dir: Path) -> Path:
    """Return the directory that `location` paths are relative to."""
    probe = extract_dir / "data_aug2"
    if probe.is_dir():
        return extract_dir
    nested = list(extract_dir.glob("*/data_aug2"))
    if nested:
        return nested[0].parent
    # Fall back: directory that actually contains the first relative prefix.
    return extract_dir


def _prepare_dataset(train_json: Path, extract_dir: Path) -> None:
    from datasets import Audio, Dataset, DatasetDict

    _log(f"loading train json lines from {train_json}")
    rows = []
    with train_json.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    _log(f"train json rows={len(rows)} keys={sorted(rows[0].keys()) if rows else []}")

    root = _audio_root(extract_dir)
    kept = []
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

    ds = Dataset.from_list(kept).shuffle(seed=SEED)
    if len(ds) > MAX_TRAIN_SAMPLES:
        ds = ds.select(range(MAX_TRAIN_SAMPLES))
    ds = ds.cast_column("location", Audio())
    DatasetDict({"train": ds}).save_to_disk(str(PREPARED))
    _log(f"prepared DatasetDict at {PREPARED} train_rows={len(ds)}")


def _clone_dreamboothing() -> Path:
    if DREAM_DIR.exists():
        shutil.rmtree(DREAM_DIR)
    subprocess.check_call(["git", "clone", "--depth", "1", DREAMBOOTH_REPO, str(DREAM_DIR)])
    sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=DREAM_DIR, text=True
    ).strip()
    _log(f"cloned musicgen-dreamboothing @ {sha}")
    return DREAM_DIR / "dreambooth_musicgen.py"


def _patch_local_dataset_load(script: Path) -> None:
    """Allow dataset_name to be a save_to_disk DatasetDict path."""
    text = script.read_text(encoding="utf-8")
    needle = "raw_datasets[\"train\"] = load_dataset("
    if needle not in text:
        _log("WARN: dreamboothing load_dataset site changed; using script as-is")
        return
    patch = """from pathlib import Path as _CtxPath
from datasets import load_from_disk as _ctx_load_from_disk
_ctx_ds_path = _CtxPath(data_args.dataset_name)
if (_ctx_ds_path / "dataset_dict.json").exists() or (_ctx_ds_path / "state.json").exists():
    _ctx_loaded = _ctx_load_from_disk(str(_ctx_ds_path))
    raw_datasets["train"] = _ctx_loaded["train"] if "train" in getattr(_ctx_loaded, "keys", lambda: [])() else _ctx_loaded
else:
    raw_datasets["train"] = load_dataset("""
    text = text.replace(needle, patch, 1)
    # Close the original load_dataset(...) call by leaving it in the else branch.
    script.write_text(text, encoding="utf-8")
    _log(f"patched {script.name} to accept a local save_to_disk dataset")


def _run_dreamboothing(script: Path, repo_id: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(script),
        "--use_lora",
        "--model_name_or_path",
        BASE_MODEL,
        "--dataset_name",
        str(PREPARED),
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
        str(MAX_STEPS),
        "--max_train_samples",
        str(MAX_TRAIN_SAMPLES),
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
        "--push_to_hub",
        "true",
        "--hub_model_id",
        repo_id,
        "--hub_private_repo",
        "true",
        "--output_dir",
        str(OUT_DIR),
        "--overwrite_output_dir",
        "--report_to",
        "none",
        "--logging_steps",
        "10",
        "--save_steps",
        "500",
        "--save_total_limit",
        "2",
        "--dataloader_num_workers",
        "2",
        "--preprocessing_num_workers",
        "2",
        "--seed",
        str(SEED),
    ]
    _log("exec dreambooth_musicgen.py (argv redacted of secrets; none expected)")
    _log("command: " + " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(DREAM_DIR))


def main() -> None:
    _log(f"host={BASE_MODEL} dataset={DATASET_ID}")
    _log(
        f"caps: max_train_samples={MAX_TRAIN_SAMPLES} max_steps={MAX_STEPS} "
        "(full MusicBench train is 52768 rows / ~6596 steps at batch 1 accum 8)"
    )
    _require_token()
    user = _username()
    repo_id = f"{user}/{ADAPTER_SLUG}"
    _log(f"hub user={user} adapter={repo_id}")
    WORK.mkdir(parents=True, exist_ok=True)
    _create_private_repo(repo_id)
    train_json, tar_path = _download_musicbench()
    extract_dir = _extract_tar(tar_path)
    _prepare_dataset(train_json, extract_dir)
    script = _clone_dreamboothing()
    _patch_local_dataset_load(script)
    _run_dreamboothing(script, repo_id)
    _log(f"training process returned; adapter intended at {repo_id}")


if __name__ == "__main__":
    main()
