#!/bin/sh
# gate_peek.sh — one-screen status of the newest civtest log
L=$(ls -t /home/claude/_bds/logs/civtest-*.txt | head -1)
echo "$L  bds=$(pgrep -c bedrock_server)  $(date -u +%H:%MZ)"
grep -a "CIVTEST" $L | grep -a -o '"step":"evo","cmd":"[^"]*","expect":"[^"]*","tier":"[^"]*","plots":[0-9]*\|"step":"[a-zA-Z]*"' | grep -a -v '"queue"' | tail -3
grep -a "Watchdog\|Hang\|dynamic properties\|\[error\]\|ERROR" $L | cut -c1-180 | tail -3
grep -a "slow" $L | grep -E "took (8[0-9]{2}|9[0-9]{2}|[0-9]{4}) ms|: (8[0-9]{2}|9[0-9]{2}|[0-9]{4}) ms \(" | cut -c30-200 | tail -5
grep -a "STATESIZE" $L | grep -a -o '"total":[0-9]*' | tail -1
grep -a "bare tree" $L | cut -c45-200 | tail -2
