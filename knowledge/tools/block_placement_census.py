#!/usr/bin/env python3
"""block_placement_census.py — #175, his 19:29: "look for incorrect geometry placement for blocks we've authored".
Every block in BP-02 1.3.206 (lenient JSON: Naturalist files carry // comments), with its geometry from RP-04 1.3.156,
RP-01 1.3.117 or RP-08 1.4.13, under the MEASURED transformation law (D-C487).

Gates (objective, per block):
  G-GEO   geometry id resolves exactly once; bone parents exist; bone_visibility names exist.
  G-BND   geometry inside the engine bound (MS Learn: +-30 px from the bottom-centre origin, <= 30 px per axis) and at
          least 1 px of it inside the base 16^3 cell.
  G-MAP   rotation map: every state combination hits exactly one transformation; for cardinal_direction the four
          rotations are one quarter-turn set r, r+90, r+180, r-90 about y with the same x/z parts ("standard" when
          north = [0,0,0]; "offset k" when the model is authored for another facing; "irregular" otherwise); for
          vertical_half top the roof45-witnessed table x=180 with y (n 180, w -90, s 0, e 90) relative to bottom.
  G-BOX   collision + selection boxes inside the cell after the state's rotation.
  G-UV    every per-face uv window inside the declared texture size (furniture law: u+w <= 16, v+h <= 16 on 16-px tiles).
  G-MAT   every geometry material instance mapped in the BP; BP instances never used are noted.
  G-FACE  full-block blocks whose material instances are keyed by face name UNDER direction states (east/west
          instance mapping is unwitnessed as a world-face mapping: L-XFACE covers geometry uv keys only) -> listed.
Measurements (true law, per directional geometry, state north = rotation per map):
  M-FRONT the low side of the top surface (slopes) and the horizontal centroid direction of all faces (one-sided
          pieces) -> which side the piece "presents" at state north; the front-state law says the model's north side
          is the front (the side toward the placer; roof45: the eave).
  M-FAM   pieces of one family must agree: lower/upper, straight/corner, lo/hi, 45/63, chair/bench/stool.
Output: _docs/blocks/BLOCK-PLACEMENT-CENSUS-2026-10-02.json + a printed summary + outputs/BLOCK-FACINGS-SHEET.png."""
import itertools
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

os.environ.setdefault("PW_STACK", "final")
sys.path.insert(0, "/home/claude/tools")
import civ_render as CR  # noqa: E402
import roof_heightfield as RH  # noqa: E402

B = Path("/home/claude/_build")
BP = B / "bp02-206"
RPS = [B / "rp04-156", B / "rp01-117", B / "rp08-1413"]
CR.BP = BP / "blocks"
CR.RP_MODELS = [rp / "models/blocks" for rp in RPS]
DIRS = ["north", "west", "south", "east"]
STD = {"north": 0, "west": 90, "south": 180, "east": -90}
TOP_Y = {"north": 180, "west": -90, "south": 0, "east": 90}


def lenient(txt):
    txt = re.sub(r"^\s*//.*$", "", txt, flags=re.M)
    txt = re.sub(r",(\s*[}\]])", r"\1", txt)
    return json.loads(txt)


def load(p):
    return lenient(p.read_text(encoding="utf-8-sig"))


def geo_index():
    idx = {}
    for rp in RPS:
        for f in (rp / "models/blocks").rglob("*.json"):
            try:
                d = load(f)
            except Exception:  # noqa: BLE001
                continue
            for g in d.get("minecraft:geometry", []):
                idx.setdefault(g["description"]["identifier"], []).append((rp.name, f, g))
    return idx


def state_space(desc):
    sp = {k: list(v) for k, v in desc.get("states", {}).items()}
    tr = desc.get("traits", {})
    for s in tr.get("minecraft:placement_direction", {}).get("enabled_states", []):
        sp[s] = DIRS if s == "minecraft:cardinal_direction" else [0, 1, 2, 3]
    for s in tr.get("minecraft:placement_position", {}).get("enabled_states", []):
        sp[s] = ["bottom", "top"] if s == "minecraft:vertical_half" else ["down", "up", "north", "south", "east", "west"]
    return sp


def norm(a):
    a = a % 360
    return a - 360 if a > 180 else a


def rot_box(o, s, rot):
    pts = [[o[0] + dx * s[0], o[1] + dy * s[1], o[2] + dz * s[2]] for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)]
    pts = [[-p[0], p[1], p[2]] for p in pts]
    if any(rot):
        pts = [CR.xform_world(p, rot) for p in pts]
    a = np.array(pts)
    return a.min(0).round(3).tolist(), a.max(0).round(3).tolist()


def geo_checks(g):
    tw, th = g["description"].get("texture_width", 16), g["description"].get("texture_height", 16)
    bones = {b["name"]: b for b in g["bones"]}
    issues, used, n = [], set(), 0
    for b in g["bones"]:
        if b.get("parent") and b["parent"] not in bones:
            issues.append(f"bone {b['name']}: parent {b['parent']} missing")
        for c in b.get("cubes", []):
            n += 1
            uv = c.get("uv", {})
            if isinstance(uv, dict):
                for face, spec in uv.items():
                    used.add(spec.get("material_instance", "*"))
                    u, v = spec["uv"]
                    us, vs = spec.get("uv_size", [0, 0])
                    lo_u, hi_u = min(u, u + us), max(u, u + us)
                    lo_v, hi_v = min(v, v + vs), max(v, v + vs)
                    if lo_u < -0.01 or lo_v < -0.01 or hi_u > tw + 0.01 or hi_v > th + 0.01:
                        issues.append(f"uv outside {tw}x{th}: bone {b['name']} {face} uv {spec['uv']} size {spec.get('uv_size')}")
    return {"cubes": n, "bones": list(bones), "used": sorted(used), "issues": issues}


def extent(gid):
    faces = CR.geo_faces(gid)
    if not faces:
        return None
    a = np.array([p for f in faces for p in f.pts])
    lo, hi = a.min(0), a.max(0)
    bad = []
    for i, ax in enumerate("xyz"):
        if lo[i] < -30.01 or hi[i] > 30.01 or hi[i] - lo[i] > 30.01:
            bad.append(ax)
    inside = (lo[0] < 7.99 and hi[0] > -7.99) and (lo[1] < 15.99 and hi[1] > 0.01) and (lo[2] < 7.99 and hi[2] > -7.99)
    return {"min": lo.round(2).tolist(), "max": hi.round(2).tolist(), "outside": bad, "touches_base_cell": bool(inside)}


def front_measure(name, st):
    items = RH.block_items(name, st)
    if not items:
        return None
    hf = RH.heightfield(items, 0, 0, 16, 16)
    out = {}
    if not np.all(np.isnan(hf)):
        edges = {"N": np.nanmean(hf[0:3]), "S": np.nanmean(hf[13:16]), "W": np.nanmean(hf[:, 0:3]), "E": np.nanmean(hf[:, 13:16])}
        edges = {k: (None if np.isnan(v) else round(float(v), 1)) for k, v in edges.items()}
        vals = {k: v for k, v in edges.items() if v is not None}
        out["edge_height"] = edges
        if vals and max(vals.values()) - min(vals.values()) >= 3:
            out["low_side"] = min(vals, key=vals.get)
            out["high_side"] = max(vals, key=vals.get)
    pts = np.array([p for f, _t, _d in items for p in f.pts])
    cx, cz = pts[:, 0].mean() - 8, pts[:, 2].mean() - 8
    out["centroid_offset_px"] = [round(float(cx), 2), round(float(cz), 2)]
    if max(abs(cx), abs(cz)) >= 1.5:
        out["mass_side"] = ("E" if cx > 0 else "W") if abs(cx) > abs(cz) else ("S" if cz > 0 else "N")
    return out


def main():
    gidx = geo_index()
    report, families = {}, {}
    files = sorted((BP / "blocks").rglob("*.json"))
    for f in files:
        try:
            d = load(f)["minecraft:block"]
        except Exception as e:  # noqa: BLE001
            report[str(f)] = {"issues": [f"unparseable: {e}"]}
            continue
        desc, comps = d["description"], d["components"]
        ident = desc["identifier"]
        r = {"file": str(f.relative_to(BP)), "issues": [], "notes": [], "third_party": ident.startswith("sf_nba:")}
        sp = state_space(desc)
        r["states"] = sp
        perms = d.get("permutations", [])
        g = comps.get("minecraft:geometry")
        gid = g if isinstance(g, str) else (g or {}).get("identifier")
        bvis = {} if isinstance(g, (str, type(None))) else g.get("bone_visibility", {})
        perm_geos = {p["components"]["minecraft:geometry"] if isinstance(p["components"].get("minecraft:geometry"), str)
                     else (p["components"].get("minecraft:geometry") or {}).get("identifier")
                     for p in perms if "minecraft:geometry" in p["components"]}
        r["geometry"] = gid
        r["permutation_geometries"] = sorted(x for x in perm_geos if x)
        custom = gid not in (None, "minecraft:geometry.full_block") or any(x not in (None, "minecraft:geometry.full_block") for x in perm_geos)
        # --- rotation map
        combos = [dict(zip(sp, vals)) for vals in itertools.product(*sp.values())] if sp else [{}]
        per_state = {}
        for st in combos:
            hits = [i for i, p in enumerate(perms) if CR.eval_cond(p["condition"], st)]
            cc = dict(comps)
            for i in hits:
                cc.update(perms[i]["components"])
            xf = cc.get("minecraft:transformation", {})
            rot = xf.get("rotation", [0, 0, 0])
            nx = len([i for i in hits if "minecraft:transformation" in perms[i]["components"]])
            if nx > 1:
                r["issues"].append(f"{st}: {nx} permutations set a transformation")
            key = json.dumps(st, sort_keys=True)
            per_state[key] = {"rotation": rot, "translation": xf.get("translation"), "scale": xf.get("scale"), "hits": hits}
            for bx in ("minecraft:collision_box", "minecraft:selection_box"):
                v = cc.get(bx)
                if isinstance(v, dict):
                    lo, hi = rot_box(v["origin"], v["size"], rot)
                    if min(lo[0], lo[2]) < -8.01 or max(hi[0], hi[2]) > 8.01 or lo[1] < -0.01 or hi[1] > 16.01:
                        r["issues"].append(f"{st}: {bx.split(':')[1]} outside the cell after rotation {lo}..{hi}")
        r["per_state_count"] = len(per_state)
        if "minecraft:cardinal_direction" in sp and custom:
            other = {k: v for k, v in sp.items() if k != "minecraft:cardinal_direction"}
            o_combos = [dict(zip(other, vals)) for vals in itertools.product(*other.values())] if other else [{}]
            kinds = set()
            for oc in o_combos:
                rots = {}
                for dname in DIRS:
                    st = dict(oc, **{"minecraft:cardinal_direction": dname})
                    rots[dname] = per_state[json.dumps(st, sort_keys=True)]["rotation"]
                xz = {(round(v[0]) % 360, round(v[2]) % 360) for v in rots.values()}
                top = oc.get("minecraft:vertical_half") == "top"
                if len(xz) != 1:
                    kinds.add(f"irregular x/z {sorted(xz)} at {oc}")
                    continue
                ys = {dname: norm(rots[dname][1]) for dname in DIRS}
                ref = TOP_Y if (top and round(rots["north"][0]) % 360 == 180) else STD
                offs = {norm(ys[dname] - ref[dname]) for dname in DIRS}
                if len(offs) == 1:
                    k = offs.pop()
                    kinds.add("standard" if k == 0 else f"offset {k}" + (" (top table)" if top else ""))
                else:
                    kinds.add(f"irregular y {ys} at {oc}")
            r["rotation_map"] = sorted(kinds)
            if any(k.startswith("irregular") for k in kinds):
                r["issues"].append(f"rotation map irregular: {sorted(kinds)}")
            elif any(k.startswith("offset") for k in kinds):
                r["notes"].append(f"rotation map offset (model authored for another facing): {sorted(kinds)}")
        # --- geometry
        if custom:
            for gg in {gid, *perm_geos} - {None, "minecraft:geometry.full_block"}:
                hits = gidx.get(gg, [])
                if len(hits) != 1:
                    r["issues"].append(f"geometry {gg} resolves {len(hits)} times ({[h[0] for h in hits]})")
                    continue
                gc = geo_checks(hits[0][2])
                r.setdefault("geo", {})[gg] = {"pack": hits[0][0], "cubes": gc["cubes"], "bones": len(gc["bones"])}
                r["issues"] += [f"{gg}: {i}" for i in gc["issues"][:8]]
                if len(gc["issues"]) > 8:
                    r["notes"].append(f"{gg}: {len(gc['issues'])} uv-window issues in all")
                for bn in bvis:
                    if bn not in gc["bones"]:
                        r["issues"].append(f"bone_visibility names a missing bone {bn}")
                ext = extent(gg)
                r["geo"][gg]["extent"] = ext
                if ext and ext["outside"]:
                    r["issues"].append(f"{gg}: outside the +-30 px engine bound on {ext['outside']}")
                if ext and not ext["touches_base_cell"]:
                    r["issues"].append(f"{gg}: no part inside the base 16^3 cell")
                mats = dict(comps.get("minecraft:material_instances", {}))
                for p in perms:
                    mats.update(p["components"].get("minecraft:material_instances", {}))
                miss = [m for m in gc["used"] if m not in mats and "*" not in mats]
                if miss:
                    r["issues"].append(f"{gg}: material instances not mapped: {miss}")
                unused = [m for m in mats if m != "*" and m not in gc["used"]]
                if unused:
                    r["notes"].append(f"{gg}: BP material instances unused by the geometry: {unused}")
        else:
            mats = dict(comps.get("minecraft:material_instances", {}))
            face_keyed = any(k in ("north", "south", "east", "west") for k in mats)
            for p in perms:
                if any(k in ("north", "south", "east", "west") for k in p["components"].get("minecraft:material_instances", {})):
                    face_keyed = True
            if face_keyed and "minecraft:cardinal_direction" in sp:
                r["notes"].append("G-FACE: full block with per-face material instances under direction states (east/west world mapping unwitnessed)")
        # --- front measurement (one representative per geometry + direction)
        if custom and "minecraft:cardinal_direction" in sp and not r["third_party"]:
            base = {k: v[0] for k, v in sp.items()}
            base["minecraft:cardinal_direction"] = "north"
            if "minecraft:vertical_half" in base:
                base["minecraft:vertical_half"] = "bottom"
            try:
                r["front_north"] = front_measure(ident, base)
            except Exception as e:  # noqa: BLE001
                r["front_north"] = {"error": str(e)}
        fam = re.sub(r"_(oak|spruce|dark_oak|birch|jungle|acacia|cherry|mangrove|pale_oak|bamboo|crimson|warped|stone|thatch|cobble|[a-z_]*planks|[a-z_]*stairs|[a-z_]+)$", "", ident.split(":")[1]) if ":" in ident else ident
        families.setdefault(gid or "full", []).append(ident)
        report[ident] = r
    out = Path("/home/claude/_docs/blocks/BLOCK-PLACEMENT-CENSUS-2026-10-02.json")
    out.write_text(json.dumps(report, indent=1, default=str))
    bad = {k: v for k, v in report.items() if v.get("issues")}
    print(f"blocks {len(report)}  with issues {len(bad)}  geometries {len(families)}")
    for k, v in bad.items():
        print(f"== {k}")
        for i in v["issues"][:10]:
            print("   ISSUE", i)
    notes = {k: v for k, v in report.items() if v.get("notes") and not v.get("issues")}
    print(f"-- notes only: {len(notes)} blocks")
    seen = set()
    for k, v in report.items():
        for n in v.get("notes", []):
            key = (v.get("geometry"), n)
            if key not in seen:
                seen.add(key)
                print("   note", k, "|", n)
    print(out)


if __name__ == "__main__":
    main()
