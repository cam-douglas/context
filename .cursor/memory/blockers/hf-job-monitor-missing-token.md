# Blocker: HF Job monitor cannot authenticate

## Symptoms

- Replacement Stage A Job named `context-musicgen-stage-a-caption-lora` (owner `cam-douglas`) cannot be listed or inspected from this Cloud VM. Abandoned Job `6a9f83aa259f8e97255edca6` ERROR'd OOMKilled (exit 137).
- `hf auth whoami` reports not logged in.
- `hf jobs inspect` and `HfApi.inspect_job` return 401.
- Job page `https://huggingface.co/jobs/cam-douglas/6a9f83aa259f8e97255edca6` redirects to login.
- Private adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora` `model_info` also 401.

## Evidence

- 2026-09-08T03:50:08Z poll 1 on abandoned Job: `token_present=false`, CLI not logged in, API 401, page login wall.
- 2026-09-08T04:17:31Z `hf jobs list --namespace cam-douglas --name context-musicgen-stage-a-caption-lora` after 60s wait: 401.
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

1. Discover newest Job named `context-musicgen-stage-a-caption-lora`; never watch `6a9f83aa259f8e97255edca6`.
2. Poll every 120s until COMPLETED/ERROR/CANCELED or 14h TIMEOUT. On ERROR ping with log tail.
3. If a token appears, inspect JSON, collect logs, and check `adapter_model.safetensors` without applying the adapter.
4. Do not start Stage B. Do not set `CONTEXT_MUSICGEN_ADAPTER`. Persist stays stock.

## Resolution criteria

- Authenticated `hf jobs inspect` returns a terminal stage, or 14h TIMEOUT is recorded with last useful logs.
