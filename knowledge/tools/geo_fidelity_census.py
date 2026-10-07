#!/usr/bin/env python3
"""geo_fidelity_census.py — R14 retro-sweep (D-C306): is each shipped RP-06/07 mob geometry the Patrix model?
For every entity whose identifier has a Patrix 26.2 JEM: Converter B bake (rest) vs the shipped geometry (rest), cubes matched
by (sorted size, uv) — the displacement of each matched cube centre, the unmatched counts, and the overall height (top y).
A shipped model built by hand in April shows up as unmatched cubes / large displacements / a different height.
Static rest poses only (P1). Output: _docs/r14/GEO-FIDELITY-CENSUS.md + .json"""
import sys, json, traceback
sys.path.insert(0, "/home/claude/tools")
from pathlib import Path
import numpy as np
import convb_round as R
import convb
from verify_rp07_1415_rp06_1410 import world_boxes

CEM = Path("/home/claude/_intake/patrix262/assets/minecraft/optifine/cem")
PACKS = [Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/claude/_build/rp06-1420"),
         Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/home/claude/_build/rp07-1426")]
OUT = Path("/home/claude/_docs/r14")


def boxes(bones):
    out = []
    for n, i, pts, size, inf, uv in world_boxes(bones):
        P = np.array(pts); out.append({"bone": n, "c": P.mean(0), "size": tuple(sorted(round(abs(s), 2) for s in size)), "uv": uv, "top": P[:, 1].max(), "bot": P[:, 1].min()})
    return out


def compare(a, b):
    """greedy: each baked cube -> the nearest unused shipped cube of the same sorted size (uv as a tie-break)"""
    used = set(); d = []
    for x in a:
        cands = [(np.linalg.norm(x["c"] - y["c"]) - (0.01 if y["uv"] == x["uv"] else 0), j) for j, y in enumerate(b) if j not in used and y["size"] == x["size"]]
        if cands:
            dist, j = min(cands); used.add(j); d.append(float(np.linalg.norm(x["c"] - b[j]["c"])))
    return d, len(a) - len(d), len(b) - len(used)


rows = []
for D in PACKS:
    for f in sorted((D / "entity").glob("*.json")):
        try: desc = R.jl(f)["minecraft:client_entity"]["description"]
        except Exception: continue
        stem = desc.get("identifier", "").split(":")[-1]
        geos = desc.get("geometry") or {}
        gid = geos.get("default") if isinstance(geos, dict) else None
        if not gid or not (CEM / f"{stem}.jem").exists(): continue
        try:
            _, g = R.geo_file(D, gid); shipped = boxes(g["bones"])
            baked = boxes(convb.bake(stem)[0])
        except Exception as e:
            rows.append({"pack": D.name, "mob": stem, "geo": gid, "error": f"{type(e).__name__}: {str(e)[:80]}"}); continue
        d, miss_a, miss_b = compare(baked, shipped)
        top_a = max(x["top"] for x in baked) if baked else 0; top_b = max(x["top"] for x in shipped) if shipped else 0
        rows.append({"pack": D.name, "mob": stem, "geo": gid, "baked_cubes": len(baked), "shipped_cubes": len(shipped),
                     "matched": len(d), "baked_unmatched": miss_a, "shipped_unmatched": miss_b,
                     "median_px": round(float(np.median(d)), 2) if d else None, "max_px": round(float(max(d)), 2) if d else None,
                     "top_baked": round(float(top_a), 2), "top_shipped": round(float(top_b), 2), "top_diff": round(float(top_b - top_a), 2)})
        print(rows[-1], flush=True)


def verdict(r):
    if "error" in r: return "ERROR"
    if r["baked_unmatched"] == 0 and r["shipped_unmatched"] == 0 and (r["max_px"] or 0) <= 0.6 and abs(r["top_diff"]) <= 0.6: return "MATCH"
    if r["matched"] >= 0.8 * r["baked_cubes"] and (r["median_px"] or 0) <= 1.0 and abs(r["top_diff"]) <= 1.0: return "CLOSE"
    return "DIFFERS"


for r in rows: r["verdict"] = verdict(r)
json.dump(rows, open(OUT / "GEO-FIDELITY-CENSUS.json", "w"), indent=1)
md = ["# Geometry fidelity census — shipped vs Patrix JEM (Converter B bake), rest pose", "",
      "| pack | mob | geometry | verdict | cubes baked / shipped | matched | unmatched baked / shipped | median / max px | top y baked -> shipped |", "|---|---|---|---|---|---|---|---|---|"]
for r in sorted(rows, key=lambda r: ({"DIFFERS": 0, "ERROR": 1, "CLOSE": 2, "MATCH": 3}[r["verdict"]], r["mob"])):
    if "error" in r: md.append(f"| {r['pack']} | {r['mob']} | {r['geo']} | ERROR | {r['error']} | | | | |"); continue
    md.append(f"| {r['pack']} | {r['mob']} | {r['geo']} | **{r['verdict']}** | {r['baked_cubes']} / {r['shipped_cubes']} | {r['matched']} | {r['baked_unmatched']} / {r['shipped_unmatched']} | {r['median_px']} / {r['max_px']} | {r['top_baked']} -> {r['top_shipped']} ({r['top_diff']:+}) |")
(OUT / "GEO-FIDELITY-CENSUS.md").write_text("\n".join(md) + "\n")
from collections import Counter
print(Counter(r["verdict"] for r in rows))
