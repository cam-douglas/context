#!/usr/bin/env bash
# Submit the MusicGen-small MusicBench LoRA Job. Never prints HF_TOKEN.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/train/scripts/musicgen-lora-musicbench.py"

if ! command -v hf >/dev/null 2>&1; then
  echo "ERROR: hf CLI not on PATH" >&2
  exit 2
fi

if ! hf auth whoami >/dev/null 2>&1; then
  echo "BLOCKED: missing HF_TOKEN" >&2
  exit 2
fi

USER_NAME="$(hf auth whoami --format json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("name") or "")')"
echo "hub_user=${USER_NAME}"
echo "adapter_repo=${USER_NAME}/context-musicgen-small-musicbench-lora"
echo "flavor=a10g-large timeout=16h est_max_usd=24"

exec hf jobs uv run --detach \
  --flavor a10g-large \
  --timeout 16h \
  --name context-musicgen-musicbench-lora \
  --secrets HF_TOKEN \
  --with accelerate \
  --with peft \
  --with datasets \
  --with soundfile \
  --with torchaudio \
  --with "transformers>=4.44" \
  --with huggingface_hub \
  "$SCRIPT"
