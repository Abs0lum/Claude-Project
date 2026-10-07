#!/usr/bin/env python3
"""small_mob_census.py — D-C282 (his 11:41 "the axolotl should be the size the bee is now, and the bee 25 % smaller … apply this
kind of change to ALL smaller mobs … the fox is too large, wolf is too small, sheep a bit large").

For every client entity our packs draw, the size the game draws it at TODAY:
  drawn = default geometry's rest bounding box (blocks) x client scripts.scale (RP side) x StripMine BP minecraft:scale (Realm only)
Reported: height, length (z), width (x) and the largest dimension, local (no StripMine BP) and Realm (with StripMine BP 1.3.3).
Output: _docs/convb/small_mob_census.json + a table on stdout."""
import glob, json, re, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
from mob_size_census import bbox

ROOT = Path("/home/claude")
PACKS = [("RP-06", ROOT / "_build/rp06-1414"), ("RP-07", ROOT / "_build/rp07-1420")]
SM_BP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/sm/bp")


def load(p):
    try:
        return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def geometries(root):
    out = {}
    for f in glob.glob(str(root / "models/entity/**/*.json"), recursive=True):
        d = load(f)
        if not d: continue
        for g in d.get("minecraft:geometry", []) or []:
            out[g["description"]["identifier"]] = g.get("bones", [])
        for k, v in d.items():
            if k.startswith("geometry.") and isinstance(v, dict): out[k.split(":")[0]] = v.get("bones", [])
    return out


def client_scale(desc):
    s = (desc.get("scripts") or {}).get("scale")
    if s is None: return 1.0
    if isinstance(s, (int, float)): return float(s)
    m = re.search(r"\?\s*[-\d.]+f?\s*:\s*([-\d.]+)", str(s))
    if m: return float(m.group(1))
    try: return float(str(s).strip().rstrip("f"))
    except ValueError: return None


def bp_scales():
    """StripMine BP adult minecraft:scale per identifier (components, not baby groups)."""
    out = {}
    for f in glob.glob(str(SM_BP / "entities/**/*.json"), recursive=True):
        d = load(f)
        if not d: continue
        e = d.get("minecraft:entity") or {}
        ident = (e.get("description") or {}).get("identifier")
        sc = ((e.get("components") or {}).get("minecraft:scale") or {}).get("value")
        if ident and sc is not None: out[ident] = float(sc)
    return out


def main():
    bps = bp_scales(); rows = []
    for tag, root in PACKS:
        geos = geometries(root)
        for f in sorted(glob.glob(str(root / "entity/*.json"))):
            d = load(f)
            if not d: continue
            desc = (d.get("minecraft:client_entity") or {}).get("description", {})
            ident = desc.get("identifier"); g = (desc.get("geometry") or {}).get("default")
            if not ident or not g or g not in geos: continue
            bb = bbox(geos[g])
            if bb is None: continue
            lo, hi = bb; size = (hi - lo) / 16.0          # px -> blocks
            cs = client_scale(desc) or 1.0; bs = bps.get(ident, 1.0)
            w, h, l = [float(v) for v in size]
            rows.append({"pack": tag, "id": ident, "geometry": g, "client_scale": cs, "stripmine_scale": bs,
                         "local": {"h": round(h * cs, 3), "l": round(l * cs, 3), "w": round(w * cs, 3), "max": round(max(w, h, l) * cs, 3)},
                         "realm": {"h": round(h * cs * bs, 3), "l": round(l * cs * bs, 3), "w": round(w * cs * bs, 3), "max": round(max(w, h, l) * cs * bs, 3)}})
    rows.sort(key=lambda r: r["local"]["max"])
    json.dump(rows, open(ROOT / "_docs/convb/small_mob_census.json", "w"), indent=1)
    print(f"{'id':32} {'pack':5} {'cscale':>6} {'SMsc':>5} | local h/l/max (blk) | realm max")
    for r in rows:
        L = r["local"]; R = r["realm"]
        print(f"{r['id']:32} {r['pack']:5} {r['client_scale']:6.2f} {r['stripmine_scale']:5.2f} | {L['h']:5.2f} {L['l']:5.2f} {L['max']:5.2f} | {R['max']:5.2f}")


if __name__ == "__main__":
    main()
