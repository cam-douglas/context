# Hugging Face Job monitor (private Jobs)

## Purpose

Poll one private Hugging Face Job every 120s until COMPLETED, ERROR, or CANCELED. Never print tokens. Never submit Jobs. Never apply persist.

## Commands

```bash
python3 /tmp/hf-job-<jobid>/monitor.py
# or tmux session hf-job-<short-id>
```

Authenticated inspect (when a Hub login exists in the environment, not in git):

```text
hf jobs inspect <jobid> --format json
hf jobs logs <jobid>
```

On COMPLETED, confirm `adapter_model.safetensors` on the private adapter repo. Do not download weights onto persist.

## This run

- Job: `6a9f97ece686246ca69a9fff`
- URL: https://huggingface.co/jobs/cam-douglas/6a9f97ece686246ca69a9fff
- Adapter: `cam-douglas/context-musicgen-small-stage-a-caption-lora`
- Artifacts: `/tmp/hf-job-6a9f97ece686246ca69a9fff/`
