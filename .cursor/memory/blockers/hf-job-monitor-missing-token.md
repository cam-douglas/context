# Blocker: HF Job monitor cannot authenticate

## Symptoms

- Job `6a9f9c85259f8e97255ee0b7` cannot be inspected from this Cloud VM.
- Hub Jobs API and private adapter API return 401.
- Job page is a login wall.
- Private adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora` is 401.

## Evidence

- 2026-09-08T05:31:30Z poll 0: `auth=False`, `error=no_token`, job/adapter HTTP 401.
- 2026-09-08T15:17:46Z: 304 polls over 9h46m, every poll `no_token`. Job and adapter APIs still 401.
- 2026-09-08T19:31:50Z: tmux poller wrote DONE `timeout_14h` after poll 420. Final once-poll 19:33:11Z still `no_token`. Job and adapter APIs still 401. Gmail still empty for this id.
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

1. 14h TIMEOUT recorded. Remote stage remains unknown from this VM.
2. Inspect from a Hub-logged-in session: job JSON, ERROR exception + log tail, and `adapter_model.safetensors` without applying the adapter.
3. Do not submit jobs. Do not apply persist.

## Resolution criteria

- Authenticated `hf jobs inspect` returns a terminal stage, or 14h TIMEOUT is recorded with last useful evidence.
