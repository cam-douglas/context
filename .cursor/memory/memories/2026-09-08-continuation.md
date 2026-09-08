# 2026-09-08 continuation

- Persistent monitor started for HF Job `6a9f97ece686246ca69a9fff` (Stage A caption LoRA after `6a9f8e93` failed because `rows.append` sat after `continue`). Adapter `cam-douglas/context-musicgen-small-stage-a-caption-lora`. No persist apply. No job submit.
- `hf` CLI installed to `~/.local/bin` (huggingface_hub 1.30.0). No Hub login in this VM. Poll 0: API 401, job page login wall.
- Durable poller running in tmux session `hf-job-6a9f97` (`python3 /tmp/hf-job-6a9f97ece686246ca69a9fff/monitor.py`), interval 120s, 14h timeout.
- Blocker: `.cursor/memory/blockers/hf-job-monitor-missing-token.md`.
- Terminal for `6a9f97ece686246ca69a9fff`: parent-confirmed ERROR. Prepared 600 rows; trainer saw `num_samples=0` because dreamboothing keeps `min < duration < max` and clips were truncated to exactly 9s (`max=9s`). Official Hub inspect/logs remain 401 on this VM. Replacement Job `6a9f9c85259f8e97255ee0b7` writes 8s clips and is monitored elsewhere. No persist apply. No job submit.
