# 2026-09-08 continuation

- Persistent monitor started for HF Job `6a9f9c85259f8e97255ee0b7` (Stage A caption LoRA after `6a9f97ec` lost every clip to a strict duration filter at exactly 9s). Adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora`. No persist apply. No job submit.
- `hf` CLI installed to `~/.local/bin` (huggingface_hub 1.30.0). No Hub login in this VM. Poll 0: API 401, job page login wall. Gmail/Slack/Notion have no status for this id.
- Durable poller running in tmux session `hf-job-6a9f9c` (`python3 /tmp/hf-job-6a9f9c85259f8e97255ee0b7/monitor.py`), interval 120s, 14h timeout.
- 2026-09-08T15:17Z: 304 polls, still `no_token` / API 401. Persist untouched. No job submitted.
- 2026-09-08T19:31:50Z: poller DONE `timeout_14h` (poll 420). Stage, exception, logs, and `adapter_model.safetensors` never readable. Gmail/Slack empty for this id.
- Blocker: `.cursor/memory/blockers/hf-job-monitor-missing-token.md`.
