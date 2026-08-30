#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.context.sidecar"
DOMAIN="gui/$(id -u)"
SUPPORT="$HOME/Library/Application Support/Context"
AGENTS="$HOME/Library/LaunchAgents"
LOG_DIR="$HOME/Library/Logs/Context"
PLIST="$AGENTS/$LABEL.plist"
SCRIPT="$ROOT/sidecar/scripts/run-sidecar.sh"
PY="$ROOT/sidecar/.venv/bin/python"

mkdir -p "$SUPPORT" "$AGENTS" "$LOG_DIR"
chmod +x "$SCRIPT"
printf '%s\n' "$ROOT/sidecar" > "$SUPPORT/sidecar-root.txt"

if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$SCRIPT</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$ROOT/sidecar</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>CONTEXT_SIDECAR_PORT</key>
    <string>8765</string>
    <key>CONTEXT_ENABLE_GENERATION</key>
    <string>1</string>
    <key>CONTEXT_ENABLE_DEMUCS</key>
    <string>1</string>
    <key>CONTEXT_ENABLE_CLAP</key>
    <string>1</string>
    <key>CONTEXT_COMPOSE_ON_INTENT</key>
    <string>0</string>
    <key>PYTHONPATH</key>
    <string>$ROOT/sidecar/src</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <dict>
    <key>SuccessfulExit</key>
    <false/>
  </dict>
  <key>ThrottleInterval</key>
  <integer>10</integer>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/sidecar.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/sidecar.log</string>
</dict>
</plist>
EOF
cp "$PLIST" "$SUPPORT/$LABEL.plist"

if curl -sf --connect-timeout 1 "http://127.0.0.1:8765/health" | grep -q '"ok"'; then
  echo "sidecar already healthy on 127.0.0.1:8765; plist updated for next restart"
  exit 0
fi

launchctl bootout "$DOMAIN/$LABEL" >/dev/null 2>&1 || true
launchctl bootstrap "$DOMAIN" "$PLIST"
launchctl kickstart "$DOMAIN/$LABEL"

for _ in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s --connect-timeout 1 "http://127.0.0.1:8765/health" | grep -q '"ok"'; then
    echo "sidecar agent running on 127.0.0.1:8765"
    exit 0
  fi
  sleep 0.3
done

echo "sidecar agent installed but health is not up yet; see $LOG_DIR/sidecar.log" >&2
exit 1
