# Blocker: HF Job monitor cannot authenticate

## Symptoms

- Job `6a9f8e93e686246ca69a9f00` cannot be inspected from this Cloud VM.
- Canceled Job `6a9f8be6259f8e97255eddce` is not watched (0 usable rows).
- `hf auth whoami` reports not logged in.
- `hf jobs inspect` and Hub model API return 401.
- Job page redirects to login.
- Private adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora` is 401.

## Evidence

- 2026-09-08T04:32:39Z poll 0: `auth=False`, `error=no_token`.
- Subsequent 120s polls through at least poll 9: same 401 / no token.
- Gmail/Slack/Drive have no job-status threads for this id.

## Attempts

- Installed `huggingface_hub` 1.30.0 + `hf` CLI to `~/.local/bin`.
- Inspected job id, Hub model API, and HTML page (login wall).
- Gmail search for the job id and `from:huggingface.co` returned no threads.

## Files

- Live poll artifacts: `/tmp/hf-job-6a9f8e93/`
- Job URL: https://huggingface.co/jobs/cam-douglas/6a9f8e93e686246ca69a9f00

## Unknowns

- Whether `HF_TOKEN` will be injected later into this run.
- Current remote Job stage (SCHEDULING/RUNNING/COMPLETED/ERROR/CANCELED).

## Next actions

1. Never watch `6a9f8be6259f8e97255eddce`.
2. Poll `6a9f8e93e686246ca69a9f00` every 120s until COMPLETED/ERROR/CANCELED or 14h TIMEOUT.
3. If a token appears, inspect JSON, collect ERROR log tail, and check `adapter_model.safetensors` without applying the adapter.
4. Do not submit jobs. Do not apply persist.

## Resolution criteria

- Authenticated `hf jobs inspect` returns a terminal stage, or 14h TIMEOUT is recorded with last useful evidence.
