# HF Jobs: MusicGen-small LoRA on MusicBench

No secrets in this file. Do not paste `HF_TOKEN`. Never print `HF_TOKEN`.

## Why a Job wrapper

`amaai-lab/MusicBench` on the Hub is JSONL + `MusicBench.tar.gz` (~16.7 GB), not a streaming `Audio` parquet.

Do **not** download the tar on the Cursor Cloud VM or the owner Mac. The Job script downloads it only after `PREFLIGHT_OK`.

`ylacombe/musicgen-dreamboothing` is cloned **inside the Job**. The wrapper never edits it and never string-patches it. Compatibility is a `load_dataset` shim (local `save_to_disk` paths) plus a serial `Dataset.map` / `Dataset.filter` shim (strip `num_proc`).

## Root cause of the seven failed Jobs

The 2024 trainer (`check_min_version` 4.40, `Seq2SeqTrainer(tokenizer=)`, `send_example_telemetry`) was run against latest transformers 5 / datasets 4. Fix the stack pin. Do not float to latest libs.

## Required pins (exact)

- `transformers==4.51.3`
- `huggingface_hub>=0.26.0,<1.0`
- `datasets==3.2.0`
- `peft==0.14.0`
- `accelerate==1.6.0`
- `evaluate`, `sentencepiece`, `librosa`, `soundfile`, `torchaudio`

`_assert_stack()` exits if transformers major>=5 or `Seq2SeqTrainer` lacks `tokenizer=`.

## Preflight then bulk

1. Clone dreamboothing, `ast`+compile, import trainer, `HfArgumentParser` on real flags.
2. Two sine clips, audio decode, 1-step smoke, no Hub push.
3. Print `PREFLIGHT_OK`.
4. Only then download `MusicBench.tar.gz` and run the capped train + private push.

Do not pass `--overwrite_output_dir` or `--preprocessing_num_workers`. Use a fresh timestamped output dir.

## Hardware

Chosen: **a10g-large** — 1x A10G 24 GB, 12 vCPU, 46 GB RAM, 200 GB disk, **$1.50/h**.

Timeout **16h** → estimated max **~$24**. If create returns HTTP 402, STOP. Do not retry other flavors.

## Caps

- `MAX_TRAIN_SAMPLES = 20000`
- `MAX_STEPS = 2500`

## Adapter

Private Hub repo: `cam-douglas/context-musicgen-small-musicbench-lora`

Base checkpoint license: **CC-BY-NC 4.0**. Persist stays stock `facebook/musicgen-small`. Do not apply the adapter.

## Submit

Requires `hf auth whoami` to succeed on the submit machine, then:

```bash
bash train/remote/submit-musicgen-lora.sh
```

Watch until `PREFLIGHT_OK`, then until COMPLETED or ERROR. Confirm adapter weights on the Hub (`adapter_model.safetensors` or equivalent).
