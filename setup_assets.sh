#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "==> Checking fonts..."
if [ ! -f pipeline/fonts/NotoSansTC.ttf ] || [ ! -f pipeline/fonts/NotoSerifTC.ttf ]; then
  echo "Fonts missing. Copy NotoSansTC.ttf and NotoSerifTC.ttf into pipeline/fonts/"
  echo "Download: https://github.com/notofonts/noto-cjk/releases"
  exit 1
else
  echo "Fonts OK"
fi

echo "==> Checking BGM..."
if [ ! -d pipeline/bgm ] || [ -z "$(ls -A pipeline/bgm/*.wav 2>/dev/null || true)" ]; then
  echo "BGM missing. Run: python3 pipeline/make_bgm.py"
else
  echo "BGM OK"
fi

echo "==> Python deps"
pip install -q -r pipeline/requirements.txt
echo "Done. Set NVIDIA_API_KEY then try:"
echo "  python3 pipeline/nvidia_client.py --prompt '你好'"
