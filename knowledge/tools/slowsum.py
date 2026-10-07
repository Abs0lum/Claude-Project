#!/usr/bin/env python3
"""slowsum.py LOG — the gate's slow lines by name: count, max ms, and the watchdog / memory lines (1.3.224 gate rule:
any Hang, any 'High memory usage', or any slow line >= 1000 ms fails the gate)."""
import re
import sys
from collections import defaultdict
txt = open(sys.argv[1], errors="ignore").read()
agg = defaultdict(lambda: [0, 0])
for m in re.finditer(r"slow: (.+?) took (\d+) ms", txt):
    a = agg[m.group(1)]; a[0] += 1; a[1] = max(a[1], int(m.group(2)))
for k, (n, mx) in sorted(agg.items(), key=lambda kv: -kv[1][1])[:15]:
    print(f"{mx:6d} ms max  {n:4d}x  {k}")
bad = [l for l in txt.splitlines() if "Watchdog" in l or "High memory" in l or "Hang" in l]
print(f"watchdog/memory lines: {len(bad)}")
for l in bad[:6]:
    print("  ", l[-200:])
worst = max((v[1] for v in agg.values()), default=0)
print("GATE-RULE:", "FAIL" if bad or worst >= 1000 else "PASS", f"(worst slow line {worst} ms)")
