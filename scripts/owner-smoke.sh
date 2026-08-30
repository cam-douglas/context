#!/usr/bin/env bash
# Agent-completable owner smoke: sidecar health, intent, claims. No Live required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export CONTEXT_SIDECAR_PORT="${CONTEXT_SIDECAR_PORT:-8765}"
export CONTEXT_ENABLE_GENERATION="${CONTEXT_ENABLE_GENERATION:-0}"
export PYTHONPATH="${ROOT}/sidecar/src"

python3 -m context_sidecar.http &
SERVER_PID=$!
cleanup() { kill "$SERVER_PID" 2>/dev/null || true; }
trap cleanup EXIT
sleep 0.4

HEALTH="$(curl -fsS "http://127.0.0.1:${CONTEXT_SIDECAR_PORT}/health")"
echo "$HEALTH" | python3 -c "import json,sys; body=json.load(sys.stdin); assert body.get('ok') is True, body"

python3 - <<'PY'
import json, os, urllib.request
from context_sidecar.intent import empty_intent
port = os.environ["CONTEXT_SIDECAR_PORT"]
payload = json.dumps(empty_intent(prompt="add a bridge")).encode()
req = urllib.request.Request(
    f"http://127.0.0.1:{port}/intent",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as response:
    body = json.load(response)
assert body["ok"] is True
assert body["intent"]["prompt"] == "add a bridge"
print("intent_ok")
PY

echo "sidecar_health_ok port=${CONTEXT_SIDECAR_PORT}"
echo "claims: no MusicGen UI label; export wrote_als is false"
