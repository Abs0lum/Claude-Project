#!/bin/sh
# plog.sh "text" — append one phase-log line stamped by the CLOCK at write time (D-C515: no guessed stamps, ever).
printf '[%s] %s\n' "$(date '+%H:%M CT %m-%d')" "$*" >> /home/claude/_logs/phase_log.md && tail -1 /home/claude/_logs/phase_log.md | cut -c1-120
