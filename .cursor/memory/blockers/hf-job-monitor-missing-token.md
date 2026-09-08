# Blocker: HF Job monitor cannot authenticate

## Symptoms

- Job `6a9f97ece686246ca69a9fff` cannot be inspected from this Cloud VM.
- `hf auth whoami` reports not logged in.
- Hub Jobs API and private adapter API return 401.
- Job page is a login wall.
- Private adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora` is 401.

## Evidence

- 2026-09-08T05:11:52Z poll 0: `auth=False`, `error=no_token`, job/adapter HTTP 401.
- Gmail/Slack/Notion have no status threads for this id.
- Sibling monitors for `6a9f83aa`, `6a9f8be`, and `6a9f8e93` hit the same missing-token wall.

## Attempts

- Installed `huggingface_hub` 1.30.0 + `hf` to `~/.local/bin`.
- Inspected job id, Hub model API, and HTML page (login wall).
- Gmail `from:huggingface.co` and job-id searches returned no threads.

## Files

- Live poll artifacts: `/tmp/hf-job-6a9f97ece686246ca69a9fff/`
- Job URL: https://huggingface.co/jobs/cam-douglas/6a9f97ece686246ca69a9fff

## Unknowns

- Whether a Hub token will be injected later into this run.
- Current remote Job stage (SCHEDULING/RUNNING/COMPLETED/ERROR/CANCELED).

## Next actions

1. Poll `6a9f97ece686246ca69a9fff` every 120s until COMPLETED/ERROR/CANCELED or 14h TIMEOUT.
2. If a token appears, inspect JSON, collect ERROR log tail, and check `adapter_model.safetensors` without applying the adapter.
3. Do not submit jobs. Do not apply persist.

## Resolution criteria

- Authenticated `hf jobs inspect` returns a terminal stage, or 14h TIMEOUT is recorded with last useful evidence.
