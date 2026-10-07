#!/bin/sh
# discard.sh — his 14:41 (10-01) rule: NEVER delete; discarding = MOVING into /home/claude/_garbage/<stamp>/<original path>,
# kept for safe keeping in case of catastrophic failure.  Usage: sh tools/discard.sh PATH [PATH ...]
set -e
STAMP=$(date -u +%Y%m%d-%H%M%S)
for p in "$@"; do
  [ -e "$p" ] || { echo "discard: $p does not exist" >&2; continue; }
  abs=$(cd "$(dirname "$p")" && pwd)/$(basename "$p")
  rel=${abs#/home/claude/}
  dst=/home/claude/_garbage/$STAMP/$rel
  mkdir -p "$(dirname "$dst")"
  mv "$abs" "$dst"
  echo "discarded $rel -> _garbage/$STAMP/$rel"
done
