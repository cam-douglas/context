# Blocker: HF Job monitor cannot authenticate

## Symptoms

- Job `6a9f97ece686246ca69a9fff` cannot be inspected from this Cloud VM (official JSON/logs 401).
- Parent later confirmed the Job already failed: 600 rows prepared, trainer `num_samples=0`.
- `hf auth whoami` reports not logged in.
- Hub Jobs API and private adapter API return 401.
- Job page is a login wall.
- Private adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora` is 401.

## Evidence

- 2026-09-08T05:11:52Z poll 0 through poll 14 (05:40:00Z): `auth=False`, `error=no_token`, job/adapter HTTP 401, 120s cadence held.
- Gmail/Slack/Notion have no status threads for this id.
- Sibling monitors for `6a9f83aa`, `6a9f8be`, and `6a9f8e93` hit the same missing-token wall.
- 2026-09-08 parent dispatch for replacement Job `6a9f9c85259f8e97255ee0b7`: previous Job `6a9f97ec` prepared 600 rows then trainer saw `num_samples=0` because dreamboothing uses strict `min < duration < max` (max=9s) and clips were truncated to exactly 9s.

## Attempts

- Installed `huggingface_hub` 1.30.0 + `hf` to `~/.local/bin`.
- Inspected job id, Hub model API, and HTML page (login wall).
- Gmail `from:huggingface.co` and job-id searches returned no threads.

## Files

- Live poll artifacts: `/tmp/hf-job-6a9f97ece686246ca69a9fff/`
- Job URL: https://huggingface.co/jobs/cam-douglas/6a9f97ece686246ca69a9fff

## Unknowns

- Official Hub `status.stage` string and redacted log tail (this VM still has no token).
- Whether `adapter_model.safetensors` was pushed despite `num_samples=0` (API 401).

## Next actions

1. Treat `6a9f97ece686246ca69a9fff` as parent-confirmed ERROR. Do not submit a replacement from this agent.
2. If a token appears later, optionally fetch the official log tail for the record. Do not apply persist.
3. Official `adapter_model.safetensors` check remains 401 / unknown.

## Resolution criteria

- Parent-confirmed trainer failure is recorded. Authenticated log tail is still missing on this VM.
