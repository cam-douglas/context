# Decision: MusicGen-small LoRA on MusicBench via Hugging Face Jobs

- Status: accepted for pinned-stack submit (owner authorized 2026-09-01)
- Date: 2026-09-01
- Owner: user/operator

## Decision

Fine-tune `facebook/musicgen-small` with LoRA on `amaai-lab/MusicBench` using a detached Hugging Face Job. Do not train on the Cursor Cloud VM or the owner Mac. Push the adapter only to a private Hub model repo named `cam-douglas/context-musicgen-small-musicbench-lora`. Persist stays stock. Do not apply the adapter.

Pin the Job to transformers 4.51.3 / datasets 3.2.0 / peft 0.14.0 / accelerate 1.6.0. Never edit or string-patch `ylacombe/musicgen-dreamboothing`. Use a `load_dataset` shim and a serial `map` shim only. Refuse `MusicBench.tar.gz` until `PREFLIGHT_OK`.

## Why

Persist already loads `facebook/musicgen-small`. MusicBench is the authorized captioned music set. Seven Jobs failed when the 2024 dreamboothing trainer ran against latest transformers 5 / datasets 4.

## Job shape

- Entry: `train/scripts/musicgen-lora-musicbench.py` (`preflight()` then `bulk()`)
- Trainer: `ylacombe/musicgen-dreamboothing` cloned inside the Job, unmodified
- Flavor: `a10g-large` at $1.50/h, timeout 16h, estimated max ~$24
- Caps: 20 000 rows, 2500 steps
- `guidance_scale=1.0` for the non-melody small checkpoint
- Token forwarded with `--secrets HF_TOKEN` only; never written to git

## License

MusicGen base weights are **CC-BY-NC 4.0**. The adapter card must state that. MusicBench is cc-by-sa-3.0.

## Related

- Workstream: `docs/workstreams/20260901-musicgen-musicbench-lora/`
- Persist host: `sidecar/src/context_sidecar/generation.py` (`facebook/musicgen-small`)
