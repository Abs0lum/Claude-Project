#!/usr/bin/env python3
"""anim_bind_census.py — D-C277 sweep: for every client entity RP-06 / RP-07 override, every bone its animations and render
controllers name vs the bones its geometry actually has (case-insensitive, as the engine binds). A missing bone = that channel
silently does nothing in game. Output _docs/convb/anim_bind_census.json + table."""
import glob, json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
from face_alpha_census import jl
from convb_preview import library, bind_info
from convb_round import geo_file

ROOT = Path("/home/claude")
PACKS = [("RP-07", ROOT / "_build/rp07-1419"), ("RP-06", ROOT / "_build/rp06-1412")]


def geo_any(ident):
    for _, rp in PACKS:
        try: return geo_file(rp, ident)[1]
        except (FileNotFoundError, AssertionError): pass
        for q in sorted((rp / "models/entity").glob("**/*.json")):
            d = jl(q)
            if not d: continue
            for g in d.get("minecraft:geometry", []) or []:
                if g["description"]["identifier"] == ident: return g
            for k, v in d.items():
                if k.split(":")[0] == ident and isinstance(v, dict): return v
    return None


def main():
    rows = []
    for tag, rp in PACKS:
        anims, rcs = library(rp)
        for f in sorted(glob.glob(str(rp / "entity/*.json"))):
            d = jl(f)
            if not d: continue
            desc = d.get("minecraft:client_entity", {}).get("description", {})
            ident = desc.get("identifier", "")
            if not ident.startswith("minecraft:"): continue
            names, _, _ = bind_info(desc, anims, rcs)
            names -= {"placeholder_bone"}
            for gk, gid in (desc.get("geometry") or {}).items():
                g = geo_any(gid)
                if g is None: rows.append({"entity": ident, "pack": tag, "geometry": gid, "status": "geometry not found"}); continue
                have = {b["name"].lower() for b in g.get("bones", [])}
                missing = sorted(n for n in names if n.lower() not in have)
                rows.append({"entity": ident, "pack": tag, "gkey": gk, "geometry": gid, "names": len(names), "missing": missing})
    json.dump(rows, open(ROOT / "_docs/convb/anim_bind_census.json", "w"), indent=1)
    for r in rows:
        if r.get("missing") or r.get("status"):
            print(f"{r['entity']:30s} {r['pack']} {r.get('gkey', ''):8s} {r['geometry']:36s} {r.get('status') or ('missing ' + str(len(r['missing'])) + '/' + str(r['names']) + ': ' + ', '.join(r['missing'][:12]))}")


if __name__ == "__main__":
    main()
