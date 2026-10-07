#!/usr/bin/env python3
"""kit_probe_check.py — read _bds/kitprobe/records.json and tabulate per street and t: the top block + height (relative
to the planned H) at every width cell, and the sewer column at w = 6 (local y0..12 from the piece origin H - 14)."""
import json
import sys
recs = json.load(open("/home/claude/_bds/kitprobe/records.json"))
cols = [r for r in recs if r.get("step") == "col"]
Y0 = 184
only = sys.argv[1] if len(sys.argv) > 1 else None


def top(col):
    for i in range(len(col) - 1, -1, -1):
        if col[i] not in ".?":
            return Y0 + i, col[i]
    return None, None


for street in ["east", "west", "south", "north"]:
    if only and street != only:
        continue
    print("==", street)
    for r in cols:
        if r["street"] != street:
            continue
        t, H, c = r["t"], r["H"], r["cols"]
        tops = [top(c[w]) for w in range(13)]
        origin = H - 14
        sew = "".join(c[6][origin + k - Y0] for k in range(0, 13))
        surf = " ".join(f"{tp[1]}{tp[0] - H:+d}" if tp[0] is not None else "??" for tp in tops)
        print(f"t{t:2d} H{H} {surf} | w6 y0..12 {sew}")
