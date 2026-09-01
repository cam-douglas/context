#!/usr/bin/env bash
# Submit the MusicGen-small MusicBench LoRA Job. Never prints HF_TOKEN.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/train/scripts/musicgen-lora-musicbench.py"

if ! command -v hf >/dev/null 2>&1; then
  echo "ERROR: hf CLI not on PATH" >&2
  exit 2
fi

# hf auth whoami can print "Not logged in" and still exit 0.
WHOAMI_TEXT="$(hf auth whoami 2>&1 || true)"
if printf '%s\n' "$WHOAMI_TEXT" | grep -qi 'not logged in'; then
  echo "BLOCKED: missing HF_TOKEN" >&2
  exit 2
fi

USER_NAME="$(
  python3 -c 'from huggingface_hub import whoami; print(whoami().get("name") or "")' 2>/dev/null \
    || true
)"
if [ -z "$USER_NAME" ]; then
  echo "BLOCKED: missing HF_TOKEN" >&2
  exit 2
fi

echo "hub_user=${USER_NAME}"
echo "adapter_repo=${USER_NAME}/context-musicgen-small-musicbench-lora"
echo "flavor=a10g-large timeout=16h est_max_usd=24"
echo "pins=transformers==4.51.3 huggingface_hub>=0.26.0,<1.0 datasets==3.2.0 peft==0.14.0 accelerate==1.6.0 evaluate sentencepiece librosa soundfile torchaudio"

set +e
hf jobs uv run --detach \
  --flavor a10g-large \
  --timeout 16h \
  --name context-musicgen-musicbench-lora \
  --secrets HF_TOKEN \
  --with "transformers==4.51.3" \
  --with "huggingface_hub>=0.26.0,<1.0" \
  --with "datasets==3.2.0" \
  --with "peft==0.14.0" \
  --with "accelerate==1.6.0" \
  --with "evaluate" \
  --with "sentencepiece" \
  --with "librosa" \
  --with "soundfile" \
  --with "torchaudio" \
  "$SCRIPT"
status=$?
set -e

if [ "$status" -eq 402 ]; then
  echo "STOP: hf jobs create returned 402" >&2
  exit 402
fi

if [ "$status" -ne 0 ]; then
  echo "ERROR: hf jobs create exited ${status}" >&2
  exit "$status"
fi
