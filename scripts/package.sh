#!/usr/bin/env bash
# Build one ZIP per skill in dist/, ready for upload to Claude.ai
# (Settings > Capabilities > Skills > Upload skill).
# Each ZIP holds the skill folder itself, so the folder name matches the skill name.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"

rm -rf "$DIST"
mkdir -p "$DIST"

cd "$ROOT/skills"
for dir in */; do
  name="${dir%/}"
  if [[ ! -f "$name/SKILL.md" ]]; then
    echo "skip $name: no SKILL.md" >&2
    continue
  fi
  zip -qr "$DIST/$name.zip" "$name" -x '*.DS_Store' -x '*/__pycache__/*'
  echo "built dist/$name.zip"
done
