# Hugging Face Job monitor (private Jobs)

## Purpose

Poll one private Hugging Face Job every 120s until COMPLETED, ERROR, or CANCELED. Never print tokens. Never submit Jobs. Never apply persist.

## Commands

```bash
python3 /tmp/hf-job-6a9f9c85259f8e97255ee0b7/monitor.py
# or tmux session hf-job-6a9f9c
python3 /tmp/hf-job-6a9f9c85259f8e97255ee0b7/monitor.py --once
```

Authenticated inspect (when a Hub login exists in the environment, not in git):

```text
hf jobs inspect 6a9f9c85259f8e97255ee0b7 --namespace cam-douglas
hf jobs logs 6a9f9c85259f8e97255ee0b7 --namespace cam-douglas
```

On COMPLETED, confirm `adapter_model.safetensors` on the private adapter repo. Do not download weights onto persist.

## This run

- Job: `6a9f9c85259f8e97255ee0b7`
- URL: https://huggingface.co/jobs/cam-douglas/6a9f9c85259f8e97255ee0b7
- Adapter: `cam-douglas/context-musicgen-small-stage-a-caption-lora`
- Context: prior Job `6a9f97ec` prepared 600 rows then trainer saw `num_samples=0` because dreamboothing uses strict `min < duration < max` (`max=9s`) and clips were truncated to exactly 9s. This Job writes 8s clips.
- Artifacts: `/tmp/hf-job-6a9f9c85259f8e97255ee0b7/`
