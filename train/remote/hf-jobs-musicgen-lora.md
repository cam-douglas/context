# HF Jobs: MusicGen-small LoRA on MusicBench

No secrets in this file. Do not paste `HF_TOKEN`.

## Why a Job wrapper

`amaai-lab/MusicBench` on the Hub is JSONL + `MusicBench.tar.gz` (~16.7 GB), not a streaming `Audio` parquet. `hf datasets info` and the parquet convert branch expose text metadata only.

Discovered train JSON columns (52 768 rows):

`alt_caption`, `beats`, `bpm`, `chords`, `chords_time`, `dataset`, `is_audioset_eval_mcaps`, `key`, `keyprob`, `location`, `main_caption`, `prompt_aug`, `prompt_bpm`, `prompt_bt`, `prompt_ch`, `prompt_key`

- Caption: `main_caption`
- Audio: `location` (relative, e.g. `data_aug2/-0SdAVK79lg_1.wav`) inside the tar
- License: cc-by-sa-3.0
- Do **not** download the tar on the Cursor Cloud VM or the owner Mac. The Job script does that.

`ylacombe/musicgen-dreamboothing` is cloned **inside the Job** and run as `dreambooth_musicgen.py --use_lora`.

## Hardware (2026-09-01 `hf jobs hardware`)

Chosen: **a10g-large** — 1x A10G 24 GB, 12 vCPU, 46 GB RAM, 200 GB disk, **$1.50/h**.

Timeout **16h** → estimated max **~$24** on the $30 one-off credit.

Rejected:

- a100 / h200 (explicitly out of scope)
- l4x1 ($0.80/h, 24 GB VRAM) — VRAM is enough for musicgen-small LoRA, but 30 GB RAM is tighter for tar extract + dataset map
- t4-small/medium (16 GB) — not clearly enough once EnCodec + LoRA + activation checkpointing run together

## Caps

Full train split = 52 768 rows. At batch 1 and grad accum 8 that is 6596 optimizer steps per epoch, plus EnCodec over the full set. That can blow 16h.

Job wrapper caps:

- `MAX_TRAIN_SAMPLES = 20000`
- `MAX_STEPS = 2500`

## Adapter

Private Hub repo: `<logged-in-user>/context-musicgen-small-musicbench-lora`

Base checkpoint license: **CC-BY-NC 4.0**. The Job writes that on the adapter card. Never commit weights to git.

## Submit

Requires `hf auth whoami` to succeed on the submit machine, then:

```bash
bash train/remote/submit-musicgen-lora.sh
```

Do not `hf jobs wait` the full run. Confirm SCHEDULING or RUNNING, then inspect.

If create returns HTTP 402, stop. Do not retry other flavors.
