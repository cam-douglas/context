# Blocker: HF Job monitor cannot authenticate

## Symptoms

- Job `6a9f9c85259f8e97255ee0b7` cannot be inspected from this Cloud VM.
- Hub Jobs API and private adapter API return 401.
- Job page is a login wall.
- Private adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora` is 401.

## Evidence

- 2026-09-08T05:31:30Z poll 0: `auth=False`, `error=no_token`, job/adapter HTTP 401.
- Gmail searches for this id and `from:huggingface.co newer_than:2d` returned no threads.
- Slack search for this id returned no messages.
- Sibling monitors for `6a9f97ec`, `6a9f8e93`, `6a9f8be`, and `6a9f83aa` hit the same missing-token wall.

## Attempts

- Installed `huggingface_hub` 1.30.0 + `hf` to `~/.local/bin`.
- Inspected job id, Hub model API, and HTML page (login wall).
- Gmail/Slack/Notion have no status threads for this id.

## Files

- Live poll artifacts: `/tmp/hf-job-6a9f9c85259f8e97255ee0b7/`
- Job URL: https://huggingface.co/jobs/cam-douglas/6a9f9c85259f8e97255ee0b7

## Unknowns

- Whether a Hub token will be injected later into this run.
- Current remote Job stage (SCHEDULING/RUNNING/COMPLETED/ERROR/CANCELED).

## Next actions

1. Poll `6a9f9c85259f8e97255ee0b7` every 120s until COMPLETED/ERROR/CANCELED or 14h TIMEOUT.
2. If a token appears, inspect JSON, collect ERROR exception + log tail, and check `adapter_model.safetensors` without applying the adapter.
3. Do not submit jobs. Do not apply persist.

## Resolution criteria

- Authenticated `hf jobs inspect` returns a terminal stage, or 14h TIMEOUT is recorded with last useful evidence.
