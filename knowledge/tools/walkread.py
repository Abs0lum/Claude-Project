import json, re, sys
from collections import defaultdict
L = sys.argv[1]
tests, traces, stalls, stallgrid = [], defaultdict(list), [], defaultdict(list)
for line in open(L, errors="ignore"):
    m = re.search(r"\[CIV-WALKTEST\] (\{.*\})\s*$", line)
    if m: tests.append(json.loads(m.group(1))); continue
    m = re.search(r"\[CIV-WALKTRACE\] (\{.*\})\s*$", line)
    if m: d = json.loads(m.group(1)); traces[d["n"]].append(d); continue
    m = re.search(r"\[CIV-WALKSTALL\] (\{.*\})\s*$", line)
    if m: stalls.append(json.loads(m.group(1))); continue
    m = re.search(r"\[CIV-WALKSTALL\] (.+?) (y-?\d+: .*)$", line)
    if m: stallgrid[m.group(1)].append(m.group(2))
for t in tests: print("TEST", t)
for n, tr in traces.items():
    print(f"\n== {n}: {len(tr)} samples")
    for d in tr[:: max(1, len(tr) // 12)]:
        print("  t", d["t"], "at", d["at"], "feet", d["feet"], "below", d["below"], "i", d["i"], "/", d["of"], "lead", d["lead"], "d", d.get("d"), "idle", d["idle"], d["mode"])
for s in stalls:
    print("\nSTALL", json.dumps(s)[:900])
if "-g" in sys.argv:
    for n, g in stallgrid.items():
        print("\nGRID", n); [print("  ", x[:400]) for x in g[:8]]
