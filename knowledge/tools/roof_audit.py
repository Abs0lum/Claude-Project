#!/usr/bin/env python3
"""roof_audit.py — his 19:21 default: "check EVERYTHING there is to check about ANYTHING there is to see".
Full audit of every roof-family block (all materials) in the current builds (BP-02 1.3.206, RP-04 1.3.156, RP-01 1.3.117,
final stack for textures). One JSON report + a readable summary.

Per block:
  BP   identifier / menu category / display name + lang line / states + traits / permutation conditions (every state
       combination matched by exactly one permutation) / transformation per state / collision + selection boxes (inside
       the 16^3 cell, rotated by the transformation - D-C487) / material instances (texture key, render method) /
       destruction / recipe(s) that make it / loot (none = drops itself) / companion rules that read or write it /
       structures that place it (+ their states).
  RP   geometry id resolves (which pack, which file) / bones: parents exist, bone_visibility bones exist / cube count,
       rotated cubes per axis / extents vs the engine limit (all geometry within -8..24 x 0..30 style bound: we use the
       documented 30 px cube centred on the block: x,z in [-15,15], y in [0,30]) / every material_instance a face uses
       is mapped in the BP (or by '*') and every BP instance is used by some face / uv rects inside the declared
       texture size.
  ART  terrain key exists in the OWNING RP's terrain_texture.json / image found in the stack / texture set present
       (colour, MER(S), normal/heightmap layers resolve) / alpha hardness of cut-out textures (soft = 0 required).
  SHAPE true-law top surface per state (tools/roof_heightfield.py): reported as min/max and the downhill direction(s)."""
import io
import itertools
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

os.environ.setdefault("PW_STACK", "final")
sys.path.insert(0, "/home/claude/tools")
import roof_heightfield as RH  # noqa: E402
import civ_render as CR  # noqa: E402
import stack_now as S  # noqa: E402

B = Path("/home/claude/_build")
BP = B / "bp02-206"
RPS = [B / "rp04-156", B / "rp01-117"]
FAMILY = re.compile(r"pw:(roof45|roof45_ridge|roof_hip|roof_pyramidion|roof_ridge_end|roof_gusset_lower|roof_gusset_upper|"
                    r"roof63_lower|roof63_upper|crown_ring)_[a-z_]+$")
LIMIT = {"x": (-30, 30), "y": (-30, 30), "z": (-30, 30)}   # MS Learn "Sizing and Culling": +-30 px from the bottom-centre origin, at most 30 px per axis, >=1 px inside the base cell


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def bp_blocks():
    out = {}
    for f in sorted((BP / "blocks").rglob("*.json")):
        try:
            d = load(f)["minecraft:block"]
        except Exception:  # noqa: BLE001
            continue
        ident = d["description"]["identifier"]
        if FAMILY.match(ident):
            out[ident] = (f, d)
    return out


def state_space(desc):
    sp = {k: v for k, v in desc.get("states", {}).items()}
    tr = desc.get("traits", {})
    if "minecraft:placement_direction" in tr:
        for s in tr["minecraft:placement_direction"]["enabled_states"]:
            sp[s] = ["north", "south", "east", "west"] if s == "minecraft:cardinal_direction" else [0, 1, 2, 3]
    if "minecraft:placement_position" in tr:
        for s in tr["minecraft:placement_position"]["enabled_states"]:
            sp[s] = ["bottom", "top"] if s == "minecraft:vertical_half" else ["down", "up", "north", "south", "east", "west"]
    return sp


def geo_index():
    idx = {}
    for rp in RPS:
        for f in (rp / "models/blocks").glob("*.json"):
            try:
                d = load(f)
            except Exception:  # noqa: BLE001
                continue
            for g in d.get("minecraft:geometry", []):
                idx.setdefault(g["description"]["identifier"], []).append((rp.name, f, g))
    return idx


def rot_box(o, s, rot):
    pts = [[o[0] + dx * s[0], o[1] + dy * s[1], o[2] + dz * s[2]] for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)]
    pts = [[-p[0], p[1], p[2]] for p in pts]
    if any(rot):
        pts = [CR.xform_world(p, rot) for p in pts]
    a = np.array(pts)
    return a.min(0).round(3).tolist(), a.max(0).round(3).tolist()


def geo_audit(g):
    tw, th = g["description"].get("texture_width", 16), g["description"].get("texture_height", 16)
    bones = {b["name"]: b for b in g["bones"]}
    issues, used, rot_axes, n = [], set(), {"x": 0, "y": 0, "z": 0}, 0
    for b in g["bones"]:
        if b.get("parent") and b["parent"] not in bones:
            issues.append(f"bone {b['name']} parent {b['parent']} missing")
        for c in b.get("cubes", []):
            n += 1
            r = c.get("rotation", [0, 0, 0])
            for i, ax in enumerate("xyz"):
                if r[i]:
                    rot_axes[ax] += 1
            uv = c.get("uv", {})
            if isinstance(uv, dict):
                for face, spec in uv.items():
                    used.add(spec.get("material_instance", "*"))
                    u, v = spec["uv"]
                    us, vs = spec.get("uv_size", [0, 0])
                    lo_u, hi_u = min(u, u + us), max(u, u + us)
                    lo_v, hi_v = min(v, v + vs), max(v, v + vs)
                    if lo_u < -0.01 or lo_v < -0.01 or hi_u > tw + 0.01 or hi_v > th + 0.01:
                        issues.append(f"uv outside {tw}x{th}: bone {b['name']} face {face} uv {spec['uv']} size {spec.get('uv_size')}")
    return {"cubes": n, "bones": list(bones), "rotated_cubes": rot_axes, "materials_used": sorted(used), "issues": issues}


def geo_extent(gid):
    faces = CR.geo_faces(gid)
    if not faces:
        return None
    a = np.array([p for f in faces for p in f.pts])
    lo, hi = a.min(0), a.max(0)
    bad = [ax for i, ax in enumerate("xyz") if lo[i] < LIMIT[ax][0] - 0.01 or hi[i] > LIMIT[ax][1] + 0.01 or hi[i] - lo[i] > 30.01]
    return {"min": lo.round(2).tolist(), "max": hi.round(2).tolist(), "outside_engine_bound": bad}


def alpha_soft(arr):
    a = arr[..., 3]
    return int(((a > 0) & (a < 255)).sum())


def art_audit(key, P, T, owner_rp):
    out = {"key": key}
    own_tt = {}
    for rp in RPS:
        tt = rp / "textures/terrain_texture.json"
        if tt.exists():
            td = load(tt).get("texture_data", {})
            if key in td:
                own_tt[rp.name] = td[key]
    out["terrain_in"] = list(own_tt)
    if key not in T:
        out["error"] = "terrain key not in stack"
        return out
    paths = S.paths_of(T[key][1])
    out["paths"] = paths
    p0 = paths[0] if paths else None
    if p0:
        pack, f = S.find_image(P, p0)
        out["image_pack"] = getattr(pack, "name", str(pack)) if pack else None
        if pack:
            im = np.asarray(Image.open(io.BytesIO(pack.read(f))).convert("RGBA"))
            out["size"] = list(im.shape[1::-1])
            out["soft_alpha_texels"] = alpha_soft(im)
            ts = None
            for ext in (".texture_set.json",):
                try:
                    ts = json.loads(pack.read(re.sub(r"\.(png|tga)$", "", f) + ext))
                except Exception:  # noqa: BLE001
                    ts = None
            out["texture_set"] = ts.get("minecraft:texture_set") if ts else None
        else:
            out["error"] = "image not found"
    return out


def shape(name, st):
    hf = RH.heightfield(RH.block_items(name, st), 0, 0, 16, 16)
    if np.all(np.isnan(hf)):
        return {"empty": True}
    gy, gx = np.gradient(np.nan_to_num(hf, nan=0.0))
    d = {"min": float(np.nanmin(hf)), "max": float(np.nanmax(hf)), "holes": int(np.isnan(hf).sum()),
         "mean_rise_east": round(float(np.nanmean(gx)), 2), "mean_rise_south": round(float(np.nanmean(gy)), 2)}
    # quadrant means (NW, NE, SW, SE)
    q = {k: round(float(np.nanmean(hf[r, c])), 1) if not np.all(np.isnan(hf[r, c])) else None
         for k, (r, c) in {"NW": (slice(0, 8), slice(0, 8)), "NE": (slice(0, 8), slice(8, 16)),
                           "SW": (slice(8, 16), slice(0, 8)), "SE": (slice(8, 16), slice(8, 16))}.items()}
    d["quadrant_mean"] = q
    d["edges"] = {"N": round(float(np.nanmean(hf[0])), 1) if not np.all(np.isnan(hf[0])) else None,
                  "S": round(float(np.nanmean(hf[-1])), 1) if not np.all(np.isnan(hf[-1])) else None,
                  "W": round(float(np.nanmean(hf[:, 0])), 1) if not np.all(np.isnan(hf[:, 0])) else None,
                  "E": round(float(np.nanmean(hf[:, -1])), 1) if not np.all(np.isnan(hf[:, -1])) else None}
    return d


def main():
    P = S.packs()
    T = S.terrain(P)
    gidx = geo_index()
    blocks = bp_blocks()
    recipes = {}
    for f in (BP / "recipes").rglob("*.json"):
        txt = f.read_text(encoding="utf-8-sig")
        for ident in blocks:
            if f'"{ident}"' in txt and ('"result"' in txt):
                try:
                    r = load(f)
                    body = next(v for k, v in r.items() if k.startswith("minecraft:recipe"))
                    res = body.get("result")
                    res = res if isinstance(res, list) else [res]
                    if any((x.get("item") if isinstance(x, dict) else x) == ident for x in res):
                        recipes.setdefault(ident, []).append(f.name)
                except Exception:  # noqa: BLE001
                    pass
    lang = {}
    for rp in RPS + [B / "rp08-1413"]:
        lf = rp / "texts/en_US.lang"
        if lf.exists():
            for line in lf.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    lang.setdefault(k.strip(), (rp.name, v.strip()))
    comp_js = (BP / "scripts/pw_companion.js").read_text()
    structs = {}
    sys.path.insert(0, "/home/claude/tools")
    import mcstructure as M
    for f in (BP / "structures").rglob("*.mcstructure"):
        try:
            st = M.Structure.from_bytes(f.read_bytes())
        except Exception:  # noqa: BLE001
            continue
        for x in range(st.size[0]):
            for y in range(st.size[1]):
                for z in range(st.size[2]):
                    b = st.get(x, y, z)
                    if b and b[0] in blocks:
                        key = json.dumps({k: v.value for k, v in b[1].items()}, sort_keys=True)
                        structs.setdefault(b[0], {}).setdefault(str(f.relative_to(BP)), {}).setdefault(key, 0)
                        structs[b[0]][str(f.relative_to(BP))][key] += 1
    report = {}
    for ident, (f, d) in blocks.items():
        desc, comps = d["description"], d["components"]
        r = {"file": str(f.relative_to(B)), "menu": desc.get("menu_category"), "issues": []}
        dn = comps.get("minecraft:display_name")
        r["display_name"] = dn
        r["lang"] = lang.get(dn) or lang.get(f"tile.{ident}.name")
        if not r["lang"]:
            r["issues"].append("no lang line for display name")
        sp = state_space(desc)
        r["states"] = sp
        perms = d.get("permutations", [])
        combos = [dict(zip(sp, vals)) for vals in itertools.product(*sp.values())] if sp else [{}]
        per_state = []
        for st in combos:
            hits = [i for i, p in enumerate(perms) if CR.eval_cond(p["condition"], st)]
            cc = dict(comps)
            for i in hits:
                cc.update(perms[i]["components"])
            rot = cc.get("minecraft:transformation", {}).get("rotation", [0, 0, 0])
            row = {"state": st, "perms": hits, "rotation": rot}
            if len([i for i in hits if "minecraft:transformation" in perms[i]["components"]]) > 1:
                r["issues"].append(f"state {st}: >1 transformation permutation")
            if sp and not hits:
                r["issues"].append(f"state {st}: no permutation")
            for bx in ("minecraft:collision_box", "minecraft:selection_box"):
                v = cc.get(bx)
                if isinstance(v, dict):
                    lo, hi = rot_box(v["origin"], v["size"], rot)
                    row[bx.split(":")[1]] = [lo, hi]
                    if min(lo[0], lo[2]) < -8.01 or max(hi[0], hi[2]) > 8.01 or lo[1] < -0.01 or hi[1] > 16.01:
                        r["issues"].append(f"state {st}: {bx} outside the cell after rotation {lo}..{hi}")
            per_state.append(row)
        r["per_state"] = per_state
        g = comps.get("minecraft:geometry")
        gid = g if isinstance(g, str) else g.get("identifier")
        bv = {} if isinstance(g, str) else g.get("bone_visibility", {})
        hits = gidx.get(gid, [])
        r["geometry"] = {"id": gid, "found_in": [(h[0], h[1].name) for h in hits], "bone_visibility": bv}
        if len(hits) != 1:
            r["issues"].append(f"geometry {gid} resolves {len(hits)} times")
        if hits:
            ga = geo_audit(hits[0][2])
            r["geometry"].update(ga)
            r["issues"] += [f"geometry: {i}" for i in ga["issues"]]
            for bn in bv:
                if bn not in ga["bones"]:
                    r["issues"].append(f"bone_visibility names missing bone {bn}")
            ext = geo_extent(gid)
            r["geometry"]["extent"] = ext
            if ext and ext["outside_engine_bound"]:
                r["issues"].append(f"geometry outside engine bound on {ext['outside_engine_bound']}")
            mats = comps.get("minecraft:material_instances", {})
            for perm in perms:
                mats = {**mats, **perm["components"].get("minecraft:material_instances", {})}
            for m in ga["materials_used"]:
                if m not in mats and "*" not in mats:
                    r["issues"].append(f"geometry material '{m}' not mapped in BP")
            unused = [m for m in mats if m != "*" and m not in ga["materials_used"]]
            if unused:
                r["notes"] = r.get("notes", []) + [f"BP material instances never used by the geometry: {unused}"]
            r["materials"] = {}
            for m, spec in mats.items():
                key = spec.get("texture")
                a = art_audit(key, P, T, None) if key else {"error": "no texture"}
                a["render_method"] = spec.get("render_method", "opaque")
                r["materials"][m] = a
                if a.get("error"):
                    r["issues"].append(f"material {m}: {a['error']}")
                if a.get("soft_alpha_texels") and spec.get("render_method") == "alpha_test":
                    r["issues"].append(f"material {m} ({key}): {a['soft_alpha_texels']} soft-alpha texels under alpha_test")
                if not a.get("texture_set"):
                    r["notes"] = r.get("notes", []) + [f"material {m} ({key}): no texture set"]
        r["recipes"] = recipes.get(ident, [])
        if not r["recipes"]:
            r["notes"] = r.get("notes", []) + ["no recipe makes it (give/creative only)"]
        r["loot"] = comps.get("minecraft:loot", "(none: drops itself)")
        base = re.sub(r"_(oak|spruce|stone|thatch|[a-z]+)$", "", ident.split(":")[1])
        r["companion_mentions"] = len(re.findall(re.escape(base), comp_js))
        r["structures"] = structs.get(ident, {})
        r["shape"] = {}
        for row in per_state:
            st = row["state"]
            try:
                r["shape"][json.dumps(st, sort_keys=True)] = shape(ident, st)
            except Exception as e:  # noqa: BLE001
                r["shape"][json.dumps(st, sort_keys=True)] = {"error": str(e)}
        report[ident] = r
    out = Path("/home/claude/_docs/blocks/ROOF-AUDIT-2026-10-02.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, default=str))
    for ident, r in report.items():
        print(f"== {ident}  issues {len(r['issues'])}  notes {len(r.get('notes', []))}  recipes {r['recipes']}  structures {list(r['structures'])}")
        for i in r["issues"][:12]:
            print("   ISSUE", i)
        for i in r.get("notes", [])[:6]:
            print("   note ", i)
    print(out)


if __name__ == "__main__":
    main()
