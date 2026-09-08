# Blocker: HF Job monitor cannot authenticate

## Symptoms

- Hugging Face Job `6a9f83aa259f8e97255edca6` (owner `cam-douglas`, flavor `a10g-large`, Stage A caption-only) cannot be inspected from this Cloud VM.
- `hf auth whoami` reports not logged in.
- `hf jobs inspect` and `HfApi.inspect_job` return 401.
- Job page `https://huggingface.co/jobs/cam-douglas/6a9f83aa259f8e97255edca6` redirects to login.
- Private adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora` `model_info` also 401.

## Evidence

- 2026-09-08T03:50:08Z poll 1: `token_present=false`, CLI not logged in, API 401, page login wall.
- Same personal environment previously recorded `BLOCKED: missing HF_TOKEN` on sibling MusicGen LoRA submit agents.

## Attempts

- Installed `huggingface_hub` 1.30.0 + `hf` CLI to `~/.local/bin`.
- Inspected job id, `cam-douglas/<id>`, Hub model API, and HTML page.
- Gmail search for the job id and `from:huggingface.co` newer than 3d returned no threads.

## Files

- Live poll artifacts: `/tmp/hf-job-monitor/`
- Job URL: https://huggingface.co/jobs/cam-douglas/6a9f83aa259f8e97255edca6

## Unknowns

- Whether `HF_TOKEN` will be injected later into this run.
- Current remote Job stage (SCHEDULING/RUNNING/COMPLETED/ERROR/CANCELED).

## Next actions

1. Keep polling every 120s until COMPLETED/ERROR/CANCELED or 14h TIMEOUT.
2. If a token appears, inspect JSON, collect logs, and check `adapter_model.safetensors` without applying the adapter.
3. Do not start Stage B. Do not set `CONTEXT_MUSICGEN_ADAPTER`. Persist stays stock.

## Resolution criteria

- Authenticated `hf jobs inspect` returns a terminal stage, or 14h TIMEOUT is recorded with last useful logs.
