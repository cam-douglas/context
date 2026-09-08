# Blocker: HF Job 6a9f8be monitor cannot authenticate

## Status

**Terminal for this Job:** CANCELED with 0 usable rows (parent-confirmed). Official Hub inspect/logs remain 401 on this VM.

## Symptoms

- Persistent monitor for Job `6a9f8be6259f8e97255eddce` cannot inspect stage from this Cloud VM.
- `hf auth whoami` reports not logged in.
- `hf jobs inspect 6a9f8be6259f8e97255eddce` returns not logged in.
- Job page `https://huggingface.co/jobs/cam-douglas/6a9f8be6259f8e97255eddce` redirects to login.
- Private adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora` `model_info` is 401.

## Evidence

- 2026-09-08T04:28:36Z poll 1: `token_present=false`, CLI not logged in, API 401, page 302 login wall, adapter API 401.
- Same personal environment previously recorded missing Hub login on sibling MusicGen LoRA submit/monitor agents.
- Gmail `from:huggingface.co newer_than:14d` and Slack search for this Job ID returned no threads.

## Attempts

- Installed `huggingface_hub` 1.30.0 + `hf` CLI to `~/.local/bin`.
- Inspected job id, `cam-douglas/<id>`, Hub model API, and HTML page.
- Gmail/Slack status search: no matching mail or messages.

## Files

- Live poll artifacts: `/tmp/hf-job-6a9f8be/`
- Job URL: https://huggingface.co/jobs/cam-douglas/6a9f8be6259f8e97255eddce
- Adapter: `cam-douglas/context-musicgen-small-stage-a-caption-lora`

## Unknowns

- Whether `HF_TOKEN` will be injected later into this run.
- Current remote Job stage (SCHEDULING/RUNNING/COMPLETED/ERROR/CANCELED).

## Next actions

1. Poll every 120s until COMPLETED/ERROR/CANCELED. Do not exit while RUNNING.
2. If a token appears, inspect JSON, collect last 30 useful log lines, and check `adapter_model.safetensors` without applying the adapter.
3. Do not start Stage B. Do not submit another Job. Do not apply persist.

## Resolution criteria

- Authenticated `hf jobs inspect` returns a terminal stage, or a terminal stage is otherwise evidenced, and the required STAGE/JOB/ADAPTER_PUSHED/ERROR_SUMMARY/NEXT block is produced.

## Outcome

- 2026-09-08T06:03Z: STAGE=CANCELED. Parent: canceled; 0 usable rows. Official logs unavailable (401). ADAPTER_PUSHED=unknown. NEXT=diagnose.
