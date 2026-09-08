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

- Official Hub JSON/log tail for `6a9f8e93` (still 401).
- Whether `adapter_model.safetensors` exists on the private adapter repo.

## Next actions

1. Never watch `6a9f8be6259f8e97255eddce`.
2. Job `6a9f8e93` is parent-confirmed ERROR; do not keep polling it.
3. Do not submit jobs. Do not apply persist.

## Resolution criteria

- Monitor closed on parent-confirmed ERROR. Official inspect remains 401 until a token is injected.
