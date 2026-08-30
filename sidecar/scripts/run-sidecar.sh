#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export CONTEXT_SIDECAR_PORT="${CONTEXT_SIDECAR_PORT:-8765}"
export CONTEXT_ENABLE_GENERATION="${CONTEXT_ENABLE_GENERATION:-1}"
export CONTEXT_ENABLE_DEMUCS="${CONTEXT_ENABLE_DEMUCS:-1}"
export CONTEXT_ENABLE_CLAP="${CONTEXT_ENABLE_CLAP:-1}"
export CONTEXT_MODEL_CACHE_DIR="${CONTEXT_MODEL_CACHE_DIR:-$HOME/Library/Application Support/Context/models}"
export CONTEXT_SAMPLE_LIBRARY="${CONTEXT_SAMPLE_LIBRARY:-$HOME/Library/Application Support/Context/Samples}"
export PYTHONPATH="$ROOT/src"
mkdir -p "$CONTEXT_MODEL_CACHE_DIR" "$CONTEXT_SAMPLE_LIBRARY"

LOG_DIR="${HOME}/Library/Logs/Context"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/sidecar.log"

PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

exec "$PY" -m context_sidecar.http >>"$LOG" 2>&1
