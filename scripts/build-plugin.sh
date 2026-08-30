#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JUCE_DIR="$ROOT/plugin/third_party/JUCE"
BUILD_DIR="$ROOT/plugin/build"

mkdir -p "$ROOT/plugin/third_party"

if [[ ! -f "$JUCE_DIR/CMakeLists.txt" ]]; then
  git clone --depth 1 --branch 8.0.8 https://github.com/juce-framework/JUCE.git "$JUCE_DIR"
fi

cmake -S "$ROOT/plugin" -B "$BUILD_DIR" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=11.0

cmake --build "$BUILD_DIR" --config Release --parallel

bash "$ROOT/scripts/install-sidecar-agent.sh"

echo "Built:"
find "$BUILD_DIR" -name "Context.app" -o -name "Context.vst3" -o -name "Context.component" | head -20
echo "AU copy: $HOME/Library/Audio/Plug-Ins/Components/Context.component"
echo "VST3 copy: $HOME/Library/Audio/Plug-Ins/VST3/Context.vst3"
