#!/usr/bin/env python3
"""box_law_179.py — L-BOX-1 applied to the roof family (Abs0lum 2026-09-21 19:17/19:19):
"what the box SHOULD contain is the filled in areas" — collision AND selection box = the AABB of the visible solid
(rotation applied, gable_fill end planes excluded), clamped to the cell.  Invisible overshoot never collides (engine:
collision comes only from collision_box).

Input : _build/bp02-178 (BP-02 v1.3.178 tree) + RP-04 .128 tree for the geometries
Output: _build/bp02-179 — ONLY the 16 roof block files differ (collision_box + selection_box), plus manifest/ledger stamps.
Ramps, gussets, angled walls, snowcaps: untouched (gussets already full; ramps wait for the voxel-shape pass).
"""
import json, math, shutil, itertools, re
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST = ROOT / "_build/bp02-178", ROOT / "_build/bp02-179"
RP = ROOT / "_build/rp04-128"
VER = "1.3.179"
FAMILY = {  # block stem -> geometry identifier
    "roof45_oak": "geometry.pw.roof45_straight", "roof45_spruce": "geometry.pw.roof45_straight", "roof45_thatch": "geometry.pw.roof45_straight",
    "roof45_ridge_oak": "geometry.pw.roof45_ridge", "roof45_ridge_spruce": "geometry.pw.roof45_ridge", "roof45_ridge_thatch": "geometry.pw.roof45_ridge",
    "roof_ridge_end_oak": "geometry.pw.roof_ridge_end", "roof_ridge_end_spruce": "geometry.pw.roof_ridge_end",
    "roof63_lower_oak": "geometry.pw.roof63_lower", "roof63_lower_spruce": "geometry.pw.roof63_lower",
    "roof63_upper_oak": "geometry.pw.roof63_upper", "roof63_upper_spruce": "geometry.pw.roof63_upper",
    "roof_hip_oak": "geometry.pw.roof_hip", "roof_hip_spruce": "geometry.pw.roof_hip",
    "roof_pyramidion_oak": "geometry.pw.roof_pyramidion", "roof_pyramidion_spruce": "geometry.pw.roof_pyramidion",
}
SIGN = -1   # rotation sign convention that keeps every roof piece inside y >= 0 (D-C197; fill_sim's calibration)

def rot_point(p, pivot, rot):
    x, y, z = [p[i] - pivot[i] for i in range(3)]
    rx, ry, rz = [math.radians(SIGN * r) for r in rot]
    c, s = math.cos(rx), math.sin(rx); y, z = y * c - z * s, y * s + z * c
    c, s = math.cos(ry), math.sin(ry); x, z = x * c + z * s, -x * s + z * c
    c, s = math.cos(rz), math.sin(rz); x, y = x * c - y * s, x * s + y * c
    return [x + pivot[0], y + pivot[1], z + pivot[2]]

def solid_aabb(geo):
    mins, maxs = [1e9] * 3, [-1e9] * 3
    for b in geo["bones"]:
        if b["name"] == "gable_fill": continue                       # zero-thickness end planes: texture, not solid
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]; rot = c.get("rotation", [0, 0, 0]); piv = c.get("pivot", [0, 0, 0])
            for dx, dy, dz in itertools.product([0, 1], [0, 1], [0, 1]):
                p = [o[0] + dx * s[0], o[1] + dy * s[1], o[2] + dz * s[2]]
                q = rot_point(p, piv, rot) if any(rot) else p
                for i in range(3): mins[i] = min(mins[i], q[i]); maxs[i] = max(maxs[i], q[i])
    return mins, maxs

def filled_box(geo):
    mn, mx = solid_aabb(geo)
    lo = [max(-8.0, mn[0]), max(0.0, mn[1]), max(-8.0, mn[2])]
    hi = [min(8.0, mx[0]), min(16.0, mx[1]), min(8.0, mx[2])]
    r = lambda v: round(v, 2)
    return {"origin": [r(lo[0]), r(lo[1]), r(lo[2])], "size": [r(hi[0] - lo[0]), r(hi[1] - lo[1]), r(hi[2] - lo[2])]}

def main():
    geos = {}
    for p in (RP / "models/blocks").glob("*.json"):
        for g in json.loads(p.read_text(encoding="utf-8-sig")).get("minecraft:geometry", []):
            geos[g["description"]["identifier"]] = g
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    rows = []
    for stem, gid in FAMILY.items():
        path = DST / "blocks" / f"{stem}.json"
        d = json.loads(path.read_text(encoding="utf-8-sig"))
        comps = d["minecraft:block"]["components"]
        assert comps.get("minecraft:geometry") in (gid, {"identifier": gid}) or (isinstance(comps.get("minecraft:geometry"), dict) and comps["minecraft:geometry"].get("identifier") == gid), stem
        old = comps["minecraft:collision_box"]
        new = filled_box(geos[gid])
        comps["minecraft:collision_box"] = new
        comps["minecraft:selection_box"] = json.loads(json.dumps(new))
        path.write_text(json.dumps(d, indent=1) + "\n", encoding="utf-8")
        rows.append((stem, old, new))
    man = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    man["header"]["name"] = f"AbsolutRealism Tectonic BP v{VER}"
    man["header"]["description"] = (f"v{VER} (2026-09-21) L-BOX-1 — the box contains the filled areas: collision + selection box of the 16 roof "
        f"blocks (roof45 x3, roof45_ridge x3, ridge_end x2, roof63 lower/upper x2, hip x2, pyramidion x2) set to the AABB of the visible "
        f"solid (rotation applied, gable planes excluded), clamped to the cell. Abs0lum: \"the geometry can have whatever invisible length "
        f"it wants, as long as it doesn't have collision properties within its invisible pieces ... what the box SHOULD contain is the "
        f"filled in areas.\" Straight 45/63/hip -> full cell; ridge 9.65 tall; ridge_end 10; pyramidion 9.2 (overhang cannot collide). "
        f"Gussets/ramps untouched. Otherwise byte-identical to v1.3.178. Pair with RP-04 v1.3.128 + RP-02 v2.0.2.")
    man["header"]["version"] = [1, 3, 179]
    for m in man["modules"]: m["version"] = [1, 3, 179]
    (DST / "manifest.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    led = DST / "PW-DEPENDENCIES.md"
    led.write_text(led.read_text(encoding="utf-8").replace("v1.3.178 ·", f"v{VER} ·", 1), encoding="utf-8")
    for stem, old, new in rows:
        print(f"{stem:26s} {json.dumps(old['origin'])} {json.dumps(old['size'])}  ->  {json.dumps(new['origin'])} {json.dumps(new['size'])}")
    return rows

if __name__ == "__main__":
    main()
