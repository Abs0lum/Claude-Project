#!/usr/bin/env python3
"""mob_size_census.py — his 09-28 23:34 "check for similar unseen issues like this across all mobs" (D-C277).

For every vanilla mob our packs re-model (client entity identifier minecraft:*), compare how BIG we draw it with how big the game
draws it:
  ours     = our default geometry's rest bounding box x our client-entity adult scale (scripts.scale; 1.0 when absent)
  vanilla  = the current vanilla Bedrock geometry's bounding box x the vanilla client-entity adult scale (Mojang/bedrock-samples
             main, sparse clone in the scratchpad) — Bedrock's own size for the mob
  java     = where the Patrix JEM encodes Java's renderer scale: FreshLX lifts/lowers the vanilla `root` by 24*(1 - s) so the feet stay
             on the ground after the renderer scales the model (horse -2.4 = 1.1, donkey +3 = 0.87, mule +2 = 0.92)
Flags: SCALE (our entity scale differs from vanilla's / Java's), SIZE (our drawn height or length differs from vanilla's by > 15 %).
Output: _docs/convb/size_census.json + a table on stdout."""
import glob, json, re, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
from face_alpha_census import jl
from verify_rp07_1415_rp06_1410 import world_boxes

ROOT = Path("/home/claude")
BS = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/bs_main")
PACKS = [("RP-07", ROOT / "_build/rp07-1419"), ("RP-06", ROOT / "_build/rp06-1412")]
CEM = ROOT / "_intake/patrix-mobs/assets/minecraft/optifine/cem"


def adult_scale(desc):
    s = (desc.get("scripts") or {}).get("scale")
    if s is None: return 1.0, None
    if isinstance(s, (int, float)): return float(s), str(s)
    m = re.search(r"\?\s*[-\d.]+f?\s*:\s*([-\d.]+)", str(s))
    if m: return float(m.group(1)), str(s)
    try: return float(str(s).strip().rstrip("f")), str(s)
    except ValueError: return None, str(s)


def geometries(root):
    out = {}
    for f in glob.glob(str(root / "models/entity/**/*.json"), recursive=True):
        d = jl(f)
        if not d: continue
        for g in d.get("minecraft:geometry", []) or []:
            out[g["description"]["identifier"]] = g.get("bones", [])
        for k, v in d.items():
            if k.startswith("geometry.") and isinstance(v, dict): out[k.split(":")[0]] = v.get("bones", [])
    return out


def bbox(bones, legacy_bind=False):
    import copy
    bones = copy.deepcopy(bones)
    if legacy_bind:
        for b in bones:
            if "bind_pose_rotation" in b and not any(b.get("rotation", [0, 0, 0]) or [0]):
                b["rotation"] = [-v for v in b["bind_pose_rotation"]]
    pts = [p for x in world_boxes(bones) for p in x[2]]
    if not pts: return None
    P = np.array(pts); return P.min(0), P.max(0)


def java_root_scale(stem):
    """Java renderer scale encoded by FreshLX in root.ty (see module doc); None when the JEM has no such root."""
    f = CEM / f"{stem}.jem"
    if not f.exists(): return None, None
    t = f.read_text(errors="replace")
    if not re.search(r'"root\.ty"\s*:', t): return None, None
    from convb import split_this, averaged_models, seeds_for, AQUATIC, TEMPLATE_KEY
    from jem_convert import load_json
    jem = split_this(load_json(f)); tk = TEMPLATE_KEY.get(stem, stem)
    rest, _ = averaged_models(jem, seeds_for(jem, stem, tk), n=8, params=AQUATIC.get(stem))
    ty = rest.get("root", {}).get("ty")
    if ty is None: return None, None
    return round(1 - ty / 24.0, 3), round(ty, 2)


def main():
    van_ents = {}
    for f in glob.glob(str(BS / "resource_pack/entity/*.json")):
        d = jl(f)
        if not d: continue
        desc = d.get("minecraft:client_entity", {}).get("description", {})
        ident = desc.get("identifier")
        if not ident: continue
        rank = (1 if re.search(r"_v\d", Path(f).stem) else 0, Path(f).stem)       # prefer the newest _vN file
        if ident not in van_ents or rank > van_ents[ident][0]: van_ents[ident] = (rank, f, desc)
    van_geo = geometries(BS / "resource_pack")
    rows = []
    for tag, rp in PACKS:
        ours_geo = geometries(rp)
        for f in sorted(glob.glob(str(rp / "entity/*.json"))):
            d = jl(f)
            if not d: continue
            desc = d.get("minecraft:client_entity", {}).get("description", {})
            ident = desc.get("identifier", "")
            if not ident.startswith("minecraft:"): continue
            stem = ident.split(":")[1]
            gid = (desc.get("geometry") or {}).get("default")
            s_ours, s_ours_raw = adult_scale(desc)
            ob = bbox(ours_geo.get(gid, [])) if gid in ours_geo else None
            v = van_ents.get(ident)
            s_van, s_van_raw, vb, vgid = None, None, None, None
            if v:
                vdesc = v[2]; s_van, s_van_raw = adult_scale(vdesc)
                vg = vdesc.get("geometry") or {}
                vgid = vg.get("default") or next(iter(vg.values()), None)
                if vgid in van_geo: vb = bbox(van_geo[vgid], legacy_bind=True)
            jname = {"zombie_pigman": "zombified_piglin", "evocation_illager": "evoker", "tropicalfish": "tropical_fish_a", "snow_golem": "snow_golem"}.get(stem, stem)
            s_java, ty = java_root_scale(jname)
            r = {"pack": tag, "entity": ident, "file": Path(f).name, "geometry": gid, "scale_ours": s_ours, "scale_ours_raw": s_ours_raw,
                 "scale_vanilla": s_van, "scale_vanilla_raw": s_van_raw, "vanilla_geometry": vgid, "java_root_scale": s_java, "freshlx_root_ty": ty}
            if ob is not None:
                lo, hi = ob; r["ours_h"] = round(float(hi[1] - max(lo[1], -99)) * (s_ours or 1), 1); r["ours_len"] = round(float(hi[2] - lo[2]) * (s_ours or 1), 1)
            if vb is not None:
                lo, hi = vb; r["van_h"] = round(float(hi[1] - lo[1]) * (s_van or 1), 1); r["van_len"] = round(float(hi[2] - lo[2]) * (s_van or 1), 1)
            flags = []
            target = s_java if s_java is not None else s_van
            if target is not None and s_ours is not None and abs(target - s_ours) > 0.02: flags.append(f"SCALE ours {s_ours} vs {'java' if s_java is not None else 'vanilla'} {target}")
            if "ours_h" in r and "van_h" in r and r["van_h"] > 0:
                rh = r["ours_h"] / r["van_h"]; r["ratio_h"] = round(rh, 2)
                if abs(rh - 1) > 0.15: flags.append(f"SIZE height x{rh:.2f}")
            if "ours_len" in r and "van_len" in r and r["van_len"] > 0:
                rl = r["ours_len"] / r["van_len"]; r["ratio_len"] = round(rl, 2)
                if abs(rl - 1) > 0.15: flags.append(f"SIZE length x{rl:.2f}")
            r["flags"] = flags; rows.append(r)
    json.dump(rows, open(ROOT / "_docs/convb/size_census.json", "w"), indent=1)
    print(f"{'entity':34s} {'pack':5s} {'ours':>5s} {'van':>5s} {'java':>5s}  {'h ours/van':>13s} {'len ours/van':>14s}  flags")
    for r in sorted(rows, key=lambda r: (not r["flags"], r["entity"])):
        print(f"{r['entity']:34s} {r['pack']:5s} {str(r['scale_ours']):>5s} {str(r['scale_vanilla']):>5s} {str(r['java_root_scale']):>5s}  "
              f"{str(r.get('ours_h')):>5s}/{str(r.get('van_h')):>6s} {str(r.get('ours_len')):>6s}/{str(r.get('van_len')):>6s}  {'; '.join(r['flags'])}")


if __name__ == "__main__":
    main()
