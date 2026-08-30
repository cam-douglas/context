#!/usr/bin/env bash
# Isolated TensorFlow Magenta venv + official checkpoints. Do not mix into sidecar/.venv.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv-magenta"
PY="${CONTEXT_MAGENTA_PYTHON:-python3}"
CACHE="${CONTEXT_MODEL_CACHE_DIR:-$HOME/Library/Application Support/Context/models/magenta}"
mkdir -p "$CACHE"

if [[ ! -x "$VENV/bin/python" ]]; then
  "$PY" -m venv "$VENV"
fi
"$VENV/bin/pip" install -U pip
"$VENV/bin/pip" install -r "$ROOT/requirements-magenta.txt"
"$VENV/bin/pip" install --no-deps 'magenta==2.1.4'

fetch() {
  local url="$1"
  local dest="$2"
  if [[ -f "$dest" && -s "$dest" ]]; then
    return 0
  fi
  curl -L --fail --retry 2 -o "$dest.partial" "$url"
  mv "$dest.partial" "$dest"
}

fetch "http://download.magenta.tensorflow.org/models/attention_rnn.mag" "$CACHE/attention_rnn.mag"
fetch "https://storage.googleapis.com/magentadata/models/music_vae/checkpoints/cat-mel_2bar_big.tar" "$CACHE/cat-mel_2bar_big.tar"
fetch "https://storage.googleapis.com/magentadata/models/music_vae/checkpoints/cat-drums_2bar_small.lokl.tar" "$CACHE/cat-drums_2bar_small.lokl.tar"

TF_USE_LEGACY_KERAS=1 "$VENV/bin/python" -c "from magenta.models.melody_rnn import melody_rnn_sequence_generator; print('melody_rnn', list(melody_rnn_sequence_generator.get_generator_map()))"
ls -lh "$CACHE"
