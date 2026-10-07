#!/bin/sh
# leakdiag_run.sh — after founding: pause the clock, then each mode followed by a quiet window (pause re-sent each time)
L=""
while [ -z "$L" ]; do sleep 5; L=$(ls -t /home/claude/_bds/logs/civtest-*.txt | head -1); done
while ! grep -a -q '"step":"foundplots"' $L; do sleep 5; done
sleep 20
P=$(pgrep -x bedrock_server)
inj() { echo "$(date -u +%H:%M:%S) inject $1" >> /home/claude/_logs/leakdiag_inject.log; printf '%s\n' "$1" > /proc/$P/fd/0; }
inj "scriptevent pw:clock pause"; sleep 90
for c in "quiet" "gtopid 1000" "quiet" "gtopy 1000" "quiet" "gblock 1000" "quiet" "gblockhi 1000" "quiet" "ground 600" "quiet"; do
  inj "scriptevent pw:clock pause"
  [ "$c" != "quiet" ] && inj "scriptevent pw:leak $c"
  sleep 90
done
