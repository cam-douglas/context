# Decision: MusicGen-small LoRA on MusicBench via Hugging Face Jobs

- Status: accepted for submit (owner authorized 2026-09-01)
- Date: 2026-09-01
- Owner: user/operator

## Decision

Fine-tune `facebook/musicgen-small` with LoRA on `amaai-lab/MusicBench` using a detached Hugging Face Job. Do not train on the Cursor Cloud VM or the owner Mac. Push the adapter only to a private Hub model repo named `<user>/context-musicgen-small-musicbench-lora`.

## Why

Persist already loads `facebook/musicgen-small`. MusicBench is the authorized captioned music set (~52 768 train rows, cc-by-sa-3.0). The owner added a $30 one-off HF Jobs credit and forbade local GPU/MPS/CPU training.

## Job shape

- Entry: `train/scripts/musicgen-lora-musicbench.py`
- Trainer: `ylacombe/musicgen-dreamboothing` cloned inside the Job
- Flavor: `a10g-large` at $1.50/h, timeout 16h, estimated max ~$24
- Caps: 20 000 rows, 2500 steps (full epoch would be 6596 steps)
- `guidance_scale=1.0` for the non-melody small checkpoint
- Token forwarded with `--secrets HF_TOKEN` only; never written to git

## License

MusicGen base weights are **CC-BY-NC 4.0**. The adapter card must state that. MusicBench is cc-by-sa-3.0.

## Related

- Workstream: `docs/workstreams/20260901-musicgen-musicbench-lora/`
- Persist host: `sidecar/src/context_sidecar/generation.py` (`facebook/musicgen-small`)
