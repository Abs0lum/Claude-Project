#!/bin/sh
# drive_pull.sh <file-id> <out-path> — Google Drive download that survives the large-file confirm page.
ID="$1"; OUT="$2"
curl -sL -o "$OUT" "https://drive.google.com/uc?export=download&id=$ID"
if file "$OUT" | grep -q -i html; then
  UUID=$(grep -o 'name="uuid" value="[^"]*"' "$OUT" | sed 's/.*value="//;s/"$//')
  curl -sL -o "$OUT" "https://drive.usercontent.google.com/download?id=$ID&export=download&confirm=t&uuid=$UUID"
fi
ls -l "$OUT"; file "$OUT"; md5sum "$OUT"
