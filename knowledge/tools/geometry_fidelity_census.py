#!/usr/bin/env python3
"""geometry_fidelity_census.py — D-C277 ("check for similar unseen issues across all mobs"): every mob geometry we ship vs what the
Patrix JEM actually builds (Converter B bake = the witnessed-correct path). Structural faults of the April converter show up here
without anyone having to spot them in game:
  cubes      shipped cube count vs the bake's
  sizes      share of the bake's box sizes (w,h,d multiset) that the shipped geometry contains
  shells     layered fur/armour shells (sizeAdd) the bake has but the shipped geometry flattened (the llama's coplanar-shell fault)
  height     shipped vs bake bounding-box height / length
  scaled     parts the JEM scales at rest (dropped by the April converter)   hidden = parts hidden at rest but drawn
Output: _docs/convb/fidelity_census.json + table."""
import glob, json, re, sys
from collections import Counter
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
from face_alpha_census import jl
from verify_rp07_1415_rp06_1410 import world_boxes
import convb

ROOT = Path("/home/claude")
PACKS = [("RP-07", ROOT / "_build/rp07-1419"), ("RP-06", ROOT / "_build/rp06-1412")]
JNAME = {"zombie_pigman": "zombified_piglin", "villager_v2": "villager", "zombie_villager_v2": "zombie_villager", "evocation_illager": "evoker",
         "tropicalfish": "tropical_fish_a"}


def all_geos():
    out = {}
    for tag, rp in PACKS:
        for f in glob.glob(str(rp / "models/entity/**/*.json"), recursive=True):
            d = jl(f)
            if not d: continue
            for g in d.get("minecraft:geometry", []) or []: out.setdefault(g["description"]["identifier"], (tag, f, g.get("bones", [])))
            for k, v in d.items():
                if k.startswith("geometry.") and isinstance(v, dict): out.setdefault(k.split(":")[0], (tag, f, v.get("bones", [])))
    return out


def sig(bones):
    sizes, infl = Counter(), Counter()
    for b in bones:
        for c in b.get("cubes", []):
            sizes[tuple(round(v, 1) for v in c["size"])] += 1
            infl[round(float(c.get("inflate", 0) or 0), 2)] += 1
    P = [p for x in world_boxes(bones) for p in x[2]]
    ext = (np.array(P).min(0), np.array(P).max(0)) if P else None
    return sizes, infl, ext


def main():
    geos = all_geos(); rows = []
    for tag, rp in PACKS:
        for f in sorted(glob.glob(str(rp / "entity/*.json"))):
            d = jl(f)
            if not d: continue
            desc = d.get("minecraft:client_entity", {}).get("description", {})
            ident = desc.get("identifier", "")
            if not ident.startswith("minecraft:"): continue
            stem = ident.split(":")[1]
            for gkey, gid in (desc.get("geometry") or {}).items():
                if gkey not in ("default", "typeA", "typeB"): continue
                jname = JNAME.get(stem, stem)
                if stem == "tropicalfish": jname = "tropical_fish_b" if gkey == "typeB" else "tropical_fish_a"
                if not (convb.CEM / f"{jname}.jem").exists() or gid not in geos:
                    rows.append({"entity": ident, "geometry": gid, "status": "no JEM" if gid in geos else "geometry not in RP-06/07"}); continue
                try:
                    bk, tw, th, info = convb.bake(jname)
                except Exception as e:
                    rows.append({"entity": ident, "geometry": gid, "status": f"bake error {e}"}); continue
                gtag, gfile, shipped = geos[gid]
                s_sz, s_in, s_ext = sig(shipped); b_sz, b_in, b_ext = sig(bk)
                common = sum((s_sz & b_sz).values()); total = sum(b_sz.values())
                shells_bake = sorted(k for k in b_in if k > 0.05); shells_ship = sorted(k for k in s_in if k > 0.05)
                r = {"entity": ident, "geometry": gid, "geometry_pack": gtag, "file": Path(gfile).name, "jem": jname,
                     "cubes_shipped": sum(s_sz.values()), "cubes_bake": total, "size_match": round(common / total, 2) if total else None,
                     "shells_bake": shells_bake, "shells_shipped": shells_ship, "scaled": info.get("scaled"), "hidden_at_rest": info.get("hidden_at_rest")}
                if s_ext and b_ext:
                    r["h_ratio"] = round(float((s_ext[1][1] - s_ext[0][1]) / max(1e-6, b_ext[1][1] - b_ext[0][1])), 2)
                    r["len_ratio"] = round(float((s_ext[1][2] - s_ext[0][2]) / max(1e-6, b_ext[1][2] - b_ext[0][2])), 2)
                flags = []
                if r["size_match"] is not None and r["size_match"] < 0.85: flags.append(f"BOXES {r['size_match']:.0%} of the Patrix boxes present")
                if len(shells_bake) > len(shells_ship): flags.append(f"SHELLS flattened (Patrix {shells_bake} vs shipped {shells_ship})")
                if r.get("h_ratio") and abs(r["h_ratio"] - 1) > 0.12: flags.append(f"HEIGHT x{r['h_ratio']}")
                if r.get("len_ratio") and abs(r["len_ratio"] - 1) > 0.12: flags.append(f"LENGTH x{r['len_ratio']}")
                if info.get("scaled"): flags.append(f"SCALED parts {sorted(info['scaled'])}")
                if abs(r["cubes_shipped"] - total) > max(1, 0.1 * total): flags.append(f"CUBES {r['cubes_shipped']} vs {total}")
                r["flags"] = flags; rows.append(r)
    json.dump(rows, open(ROOT / "_docs/convb/fidelity_census.json", "w"), indent=1)
    for r in sorted(rows, key=lambda r: (-len(r.get("flags", [])), r["entity"])):
        if "status" in r: print(f"{r['entity']:34s} {r['geometry']:34s} {r['status']}"); continue
        print(f"{r['entity']:34s} {r['geometry']:34s} [{r['geometry_pack']}] cubes {r['cubes_shipped']:3d}/{r['cubes_bake']:3d} match {r['size_match']}  "
              f"{'; '.join(r['flags']) or 'ok'}")


if __name__ == "__main__":
    main()
