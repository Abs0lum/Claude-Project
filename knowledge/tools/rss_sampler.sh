#!/bin/sh
# rss_sampler.sh OUT — every 30 s: UTC time, bedrock_server RSS (MB), last CIVTEST step; every 5 min: tickingarea list
OUT="$1"; n=0
while true; do
  P=$(pgrep -x bedrock_server)
  [ -z "$P" ] && { sleep 30; n=$((n+1)); [ $n -gt 20 ] && exit 0; continue; }
  n=0
  R=$(awk '/VmRSS/{print int($2/1024)}' /proc/$P/status 2>/dev/null)
  L=$(ls -t /home/claude/_bds/logs/civtest-*.txt | head -1)
  S=$(grep -a '"step":"' $L | grep -a -v '"queue"' | tail -1 | grep -a -o '"step":"[a-z]*"\(,"cmd":"[^"]*"\)\?' )
  D=$(grep -a "village day" $L | tail -1 | grep -a -o "day [0-9.]* · [0-9]* building")
  echo "$(date -u +%H:%M:%S) rss=${R}MB $S $D" >> "$OUT"
  M=$(date +%M)
  case "$M" in 00|05|10|15|20|25|30|35|40|45|50|55) printf 'tickingarea list all-dimensions\n' > /proc/$P/fd/0 2>/dev/null ;; esac
  sleep 30
done
