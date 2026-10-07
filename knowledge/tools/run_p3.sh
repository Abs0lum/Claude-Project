#!/bin/sh
# D-C353/D-C354: the whole menagerie pipeline, staging rebuilt from scratch every time.  usage: run_p3.sh [P3|R2]
set -e
cd /home/claude
WAVE=${1:-P3}
python3 tools/menagerie_jobs.py P3 > _logs/menagerie_jobs_P3.txt
python3 -c "
import json
J=json.load(open('_logs/menagerie_jobs_P3.json'))
json.dump({'entities': J['p1_entities']+J['entities'], 'items': J['p1_items']+J['items']}, open('_logs/menagerie_jobs_P1P3.json','w'), indent=1)
json.dump({'wave': 'R2', 'entities': [e for e in J['entities'] if e[2] in J.get('borrow', {})], 'items': []}, open('_logs/menagerie_jobs_R2.json','w'), indent=1)"
rm -rf _build/menagerie-stage
python3 -W ignore tools/addon_port.py --jobs _logs/menagerie_jobs_P1P3.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('port', d['creatures'], 'creatures', d['files'], 'files, missing sound files left out:', len(d.get('sound_files_missing', [])))"
python3 -W ignore tools/menagerie_p3_adjust.py > _logs/menagerie_p3_adjust.txt
if [ "$WAVE" = "STAGE" ]; then echo "staged only (no pack built)"; exit 0; fi
# D-C356: R2 is SHIPPED (rp07-1434 / stripmine-bp-139) — never rebuild a delivered version
if [ "$WAVE" = "R2" ] || [ "$WAVE" = "P3" ]; then echo "REFUSED: wave $WAVE is delivered; use STAGE + build_menagerie_r3.py"; exit 1; fi
python3 tools/build_menagerie_wave.py $WAVE | tail -1
