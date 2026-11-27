#!/usr/bin/env bash
# Installs this skill as a user-level Claude Code skill (~/.claude/skills) and checks its dependencies.
# Usage: bash install.sh            (run from anywhere; safe to re-run, it replaces the installed copy)
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/cinematic-video-production"
mkdir -p "$(dirname "$DEST")"
if [ "$SRC" != "$DEST" ]; then
  rm -rf "$DEST.new" && mkdir -p "$DEST.new"
  (cd "$SRC" && tar --exclude='__pycache__' -cf - .) | (cd "$DEST.new" && tar -xf -)
  rm -rf "$DEST" && mv "$DEST.new" "$DEST"
fi
chmod +x "$DEST/scripts/cvp.py"
echo "installed: $DEST"
python3 -c "import numpy, PIL" 2>/dev/null || echo "note: run  python3 -m pip install numpy pillow"
command -v ffmpeg >/dev/null || echo "note: install FFmpeg (macOS: brew install ffmpeg)"
python3 "$DEST/scripts/cvp.py" doctor || true
