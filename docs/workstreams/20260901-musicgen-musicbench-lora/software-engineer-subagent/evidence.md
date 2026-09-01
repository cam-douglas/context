---
schema_version: 1
task_id: 20260901-musicgen-musicbench-lora
role_id: software-engineer-subagent
revision: 1
environment: Cursor Cloud VM, repo github.com/cam-douglas/context, branch cursor/musicgen-musicbench-lora-a3c5
---

# Engineering evidence

## E-1 Auth

- requirement_id: SE-1
- claim: This Cloud VM is not logged in to Hugging Face. Job submit cannot proceed.
- evidence_state: VERIFIED
- method: CLI
- command_or_tool: `hf auth whoami --format json` (hf 1.29.0)
- artifact_or_source: stdout
- result: `Error: Not logged in` (exit 1). `hf auth list` → `No access tokens found.` Username unavailable.
- timestamp: 2026-09-01T11:43:00Z
- limitations: Token must already be present as `HF_TOKEN` or `hf auth login`. Do not paste a token into chat.
- follow_up: Owner/lead inject `HF_TOKEN` into the Cloud environment (write-scoped, Jobs-capable), then rerun `bash train/remote/submit-musicgen-lora.sh`.

## E-2 Hardware and price

- requirement_id: SE-6
- claim: `a10g-large` is $1.50/h; 16h timeout caps spend at ~$24.
- evidence_state: VERIFIED
- method: CLI
- command_or_tool: `hf jobs hardware --format json`
- artifact_or_source: public hardware catalog (no login required)
- result: snippet

```json
{"name": "a10g-large", "pretty name": "Nvidia A10G - large", "cpu": "12 vCPU", "ram": "46 GB", "storage": "200 GB", "accelerator": "1x A10G (24 GB)", "cost/min": "$0.0250", "cost/hour": "$1.50"}
{"name": "l4x1", "pretty name": "1x Nvidia L4", "accelerator": "1x L4 (24 GB)", "cost/hour": "$0.80"}
{"name": "t4-medium", "accelerator": "1x T4 (16 GB)", "cost/hour": "$0.60"}
```

- timestamp: 2026-09-01T11:43:00Z
- limitations: Prices are the catalog at inspect time.
- follow_up: none

## E-3 MusicBench columns (no audio download)

- requirement_id: SE-3
- claim: Train rows use `main_caption` and `location`. Audio lives in `MusicBench.tar.gz` (~16.7 GB), not in parquet.
- evidence_state: VERIFIED
- method: Hub metadata + JSON only
- command_or_tool: `hf datasets info amaai-lab/MusicBench`; `hf datasets list amaai-lab/MusicBench`; `hf datasets parquet amaai-lab/MusicBench`; `hf download ... MusicBench_train.json` (82 MB JSON, not the tar)
- artifact_or_source: Hub card + first JSONL row
- result:
  - used_storage 17515974503; siblings include `MusicBench.tar.gz` (16757993240 bytes) and `MusicBench_train.json`
  - parquet convert: train 21 MB / test 325 KB (metadata only)
  - JSONL rows=52768
  - keys: `alt_caption, beats, bpm, chords, chords_time, dataset, is_audioset_eval_mcaps, key, keyprob, location, main_caption, prompt_aug, prompt_bpm, prompt_bt, prompt_ch, prompt_key`
  - `location` sample: `data_aug2/-0SdAVK79lg_1.wav`
  - license tag: `cc-by-sa-3.0`
- timestamp: 2026-09-01T11:44:00Z
- limitations: Did not download or extract `MusicBench.tar.gz` on this VM.
- follow_up: Job wrapper extracts the tar on HF Jobs only.

## E-4 Exact submit command (not executed)

- requirement_id: SE-1
- claim: Submit is gated by login. The command that would run is below. Token is forwarded as `--secrets HF_TOKEN` and is never printed.
- evidence_state: VERIFIED (command prepared; create not reached)
- method: `bash train/remote/submit-musicgen-lora.sh` then raw `hf jobs uv run`
- result:
  - submit script: `BLOCKED: missing HF_TOKEN` (exit 2)
  - raw: `Error: Not logged in. Run 'hf auth login' first.` (exit 1)
- timestamp: 2026-09-01T11:46:00Z
- command_or_tool:

```bash
hf jobs uv run --detach \
  --flavor a10g-large \
  --timeout 16h \
  --name context-musicgen-musicbench-lora \
  --secrets HF_TOKEN \
  --with accelerate \
  --with peft \
  --with datasets \
  --with soundfile \
  --with torchaudio \
  --with "transformers>=4.44" \
  --with huggingface_hub \
  train/scripts/musicgen-lora-musicbench.py
```

- limitations: No Job id. No 402 body (auth failed first).
- follow_up: After token is present, run the script once. If create returns 402, stop.

## E-5 Job id / status / logs

- requirement_id: SE-1
- claim: No Job was created.
- evidence_state: VERIFIED
- method: submit attempts above
- result: Job id = none. Status = not submitted. Inspect URL = none. First log lines = none.
- timestamp: 2026-09-01T11:46:00Z
- limitations: Cannot prove model/dataset load on HF until submit succeeds.
- follow_up: `hf jobs inspect <id>` and `hf jobs logs <id> --tail 80` after submit.

## E-6 Adapter repo

- requirement_id: SE-4
- claim: Intended private repo is `<logged-in-user>/context-musicgen-small-musicbench-lora`. Not created because whoami failed.
- evidence_state: VERIFIED (intent only)
- method: script + missing whoami
- result: intended id unresolved; wrapper calls `HfApi.create_repo(..., private=True)` at Job start.
- timestamp: 2026-09-01T11:46:00Z
- limitations: Hub username on this VM is unknown.
- follow_up: After login, print username only via `hf auth whoami`.

## E-7 Script and license notes

- requirement_id: SE-2, SE-5
- claim: Wrapper targets `facebook/musicgen-small`, LoRA via dreamboothing, guidance 1.0, 20k/2500 cap, CC-BY-NC 4.0 on the adapter card. No token values or weights in git.
- evidence_state: VERIFIED
- method: file inspection
- artifact_or_source: `train/scripts/musicgen-lora-musicbench.py`
- result: compile OK (`python3 -m py_compile`). Caps and license text present. Git commit `8c9ef96` contains only the listed paths.
- timestamp: 2026-09-01T11:46:00Z
- limitations: Dreamboothing clone/patch runs only inside the Job.
- follow_up: none

## E-8 Persist host match

- requirement_id: SE-2
- claim: Sidecar persist host is `facebook/musicgen-small`.
- evidence_state: VERIFIED
- method: read
- artifact_or_source: `sidecar/src/context_sidecar/generation.py` (`pipeline("text-to-audio", model="facebook/musicgen-small")`)
- result: matches Job `--model_name_or_path`
- timestamp: 2026-09-01T11:42:00Z
- limitations: Adapter is not applied to persist (non-goal).
- follow_up: none
