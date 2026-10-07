#!/usr/bin/env python3
"""verify_rp07_1416.py — gate for RP-07 Neutral Mobs RP v1.4.16 (build_rp07_1416.py). Static checks only rule OUT (P1);
his in-game witness rules IN.
A  diff: only the expected files changed / added; everything else byte-identical to 1.4.15
B  every rebuilt geometry == the Converter B bake (world boxes, 0.02 px), legs excepted (stood straight by design: sizes/UVs equal)
C  placement vs the vanilla Bedrock geometry: land mobs stand on the ground (min y in [-1, 0.5]); swimmers' box centre within 6 px
D  joints: no floating bone (every bone's boxes touch another bone's boxes, 0.3 px)
E  every bone our animations / render controllers name exists (documented exceptions only)
F  every render-controller part_visibility bone OWNS cubes (L-PARTVIS-OWN — the 1.4.15 saddlebag regression)
G  every bone our animations rotate / move has a rest parent frame <= 45 deg from the entity frame; the look bone's <= 5 deg
H  look axis: +30 deg look yaw turns the head about an axis within 5 deg of the world vertical
I  the 7 look entities run animation.pw_convb.look (no relative_to look left on them); the animation binds `head`
J  strict JSON for every changed / added file; no NaN / Infinity
K  manifest 1.4.16, header + module uuids unchanged
L  geometry texture size == the JEM textureSize; the entity texture paths unchanged
M  donkey / mule == tools/equine_b.py build; their chest bones own cubes"""
import hashlib, json, math, re, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
from verify_rp07_1415_rp06_1410 import world_boxes, inside_frac
from equine_compare import bone_affines, rot_matrix
from convb import bake, CEM
from jem_convert import load_json
from convb_preview import JOBS, library, bind_info
from convb_build import _angle
import equine_b
import build_rp07_1416 as B

ROOT = Path("/home/claude"); OLD, NEW = ROOT / "_build/rp07-1415", ROOT / "_build/rp07-1416"
fails = []; n = 0
def check(tag, ok, msg):
    global n; n += 1
    print(("PASS " if ok else "FAIL ") + tag + " — " + msg)
    if not ok: fails.append(tag)

def jl(p): return B.jl(p)
def strict(p):
    t = Path(p).read_text(encoding="utf-8")
    json.loads(t, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def files(root): return {str(p.relative_to(root)): p for p in root.rglob("*") if p.is_file()}

READY = [j for j in JOBS if j[0] in B.READY]
LAND = {"panda", "mooshroom", "wolf", "frog", "turtle"}
UNBOUND_OK = {"turtle": {"tail"}, "tropical fish A": {"left_fin0", "right_fin0"}}
VANILLA_CENTRE = {"salmon": (6.93, 5.5), "dolphin": (4.74, 6.0), "axolotl": (2.0, 3.0), "tropical fish A": (3.5, 2.0), "tropical fish B": (3.0, 5.5)}


def geo(ident):
    for q in sorted((NEW / "models/entity").glob("*.json")):
        d = jl(q)
        for g in d.get("minecraft:geometry", []):
            if g["description"]["identifier"] == ident: return q, g
    raise FileNotFoundError(ident)


def keyed(bones, skip=lambda n: False):
    out = {}
    for x in world_boxes(bones):
        if skip(x[0]): continue
        out.setdefault((tuple(x[3]), x[5]), []).append(np.array(x[2]))
    return out


def main():
    rep = json.load(open(ROOT / "_docs/convb/build_1416_report.json"))
    # A — diff
    fo, fn = files(OLD), files(NEW)
    changed = sorted(k for k in fo if k in fn and md5(fo[k]) != md5(fn[k])); added = sorted(set(fn) - set(fo)); removed = sorted(set(fo) - set(fn))
    exp_geo = {f"models/entity/{r['file']}" for r in rep.values()} | {"models/entity/pw_donkey.geo.json", "models/entity/pw_mule.geo.json"}
    exp_ent = {f"entity/{s}.entity.json" for s in B.LOOK_ENTITIES}
    expected = exp_geo | exp_ent | {"manifest.json"}
    check("A1 changed set", set(changed) == expected, f"{len(changed)} changed; unexpected {sorted(set(changed) - expected)}; missing {sorted(expected - set(changed))}")
    check("A2 added / removed", added == ["animations/pw_convb_look.animation.json"] and not removed, f"added {added} removed {removed}")
    # J — strict JSON
    bad = []
    for k in changed + added:
        try: strict(fn[k])
        except Exception as e: bad.append(f"{k}: {e}")
    check("J strict JSON", not bad, f"{len(changed) + len(added)} files; {bad[:3]}")
    # K — manifest
    mo, mn = jl(OLD / "manifest.json"), jl(NEW / "manifest.json")
    check("K manifest", mn["header"]["version"] == [1, 4, 16] and all(m["version"] == [1, 4, 16] for m in mn["modules"])
          and mn["header"]["uuid"] == mo["header"]["uuid"] and [m["uuid"] for m in mn["modules"]] == [m["uuid"] for m in mo["modules"]],
          f"version {mn['header']['version']} uuid kept {mn['header']['uuid'] == mo['header']['uuid']}")
    anims, rcs = library(NEW)
    for label, stem, gkey, jname, tkey in READY:
        ent_new = jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        ent_old = jl(OLD / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        ident = ent_new["geometry"][gkey]; p, g = geo(ident); bones = g["bones"]; by = {b["name"]: b for b in bones}
        tag = label.replace(" ", "_")
        # B — cubes == bake (legs: sizes/uv only)
        bk, tw, th, info = bake(jname)
        isleg = lambda nm: bool(re.fullmatch(r"leg\d", nm))
        legcubes = {tuple(x[3]) for x in world_boxes(bones) if isleg(x[0])}
        A = keyed(bones, isleg); Bk = keyed(bk)
        errs, miss = [], []
        for k, lst in A.items():
            if k not in Bk: miss.append(k); continue
            for arr in lst: errs.append(min(float(np.abs(arr - q).max()) for q in Bk[k]))
        nb = sum(len(v) for v in Bk.values()); nn = sum(len(b.get("cubes", [])) for b in bones)
        check(f"B {tag} cubes == bake", not miss and (max(errs) if errs else 0) < 0.02 and nb == nn,
              f"{nn} cubes (bake {nb}); max corner error {max(errs) if errs else 0:.4f} px; unmatched {len(miss)}; legs stood straight {len(legcubes)}")
        # L — texture size + texture paths
        jem = load_json(CEM / f"{jname}.jem"); ts = jem.get("textureSize") or [64, 32]
        check(f"L {tag} texture", [g["description"]["texture_width"], g["description"]["texture_height"]] == list(ts) and ent_new["textures"] == ent_old["textures"],
              f"geometry {g['description']['texture_width']}x{g['description']['texture_height']} JEM {ts[0]}x{ts[1]}; entity textures unchanged {ent_new['textures'] == ent_old['textures']}")
        # C — placement
        P = np.array([q for x in world_boxes(bones) for q in x[2]]); lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2
        if label in LAND:
            check(f"C {tag} on the ground", -1.0 <= lo[1] <= 0.5, f"min y {lo[1]:.2f} (box y {lo[1]:.1f}..{hi[1]:.1f}, z {lo[2]:.1f}..{hi[2]:.1f})")
        else:
            vy, vz = VANILLA_CENTRE[label]
            check(f"C {tag} placement", abs(c[1] - vy) <= 6 and abs(c[2] - vz) <= 6, f"centre y {c[1]:.1f} z {c[2]:.1f} vs vanilla y {vy} z {vz}")
        # D — joints
        W = {}
        for x in world_boxes(bones): W.setdefault(x[0], []).append(x[2])
        floating = [nm for nm, bx in W.items() if not any(inside_frac(a, q) or inside_frac(q, a) for a in bx for m2, bs in W.items() if m2 != nm for q in bs)]
        check(f"D {tag} joints", not floating or len(W) == 1, f"{len(W)} bones with boxes; floating {floating}")
        # E — binds
        names, rel, _ = bind_info(ent_new, anims, rcs)
        missing = sorted(nm for nm in names - {"placeholder_bone"} if nm not in by)
        check(f"E {tag} binds", set(missing) <= UNBOUND_OK.get(label, set()), f"{len(names)} names; missing {missing} (allowed {sorted(UNBOUND_OK.get(label, set()))})")
        # F — part_visibility bones own cubes
        pv = set()
        for rc in ent_new.get("render_controllers", []):
            k = rc if isinstance(rc, str) else list(rc)[0]
            for pp in (rcs.get(k, {}).get("part_visibility") or []): pv |= {x for x in pp if x != "*"}
        empty = sorted(x for x in pv if x in by and not by[x].get("cubes"))
        check(f"F {tag} part_visibility owns cubes", not empty, f"pv bones {sorted(pv)}; empty {empty}")
        # G — frames
        aff = bone_affines(bones); moving = B.moving_bones(ent_new, anims)
        worst = max([(_angle(aff[by[nm]["parent"]][0]), nm) for nm in moving if nm in by and by[nm].get("parent")], default=(0.0, "-"))
        lookp = _angle(aff[by["head"]["parent"]][0]) if stem in B.LOOK_ENTITIES and by["head"].get("parent") else 0.0
        check(f"G {tag} frames", worst[0] <= 45.0 and lookp <= 5.0, f"worst moved-bone parent frame {worst[0]:.1f} deg ({worst[1]}); look parent {lookp:.1f} deg")
        # H — look axis / I — look binding
        if stem in B.LOOK_ENTITIES:
            a0 = bone_affines(bones)["head"][0]; a1 = bone_affines(bones, add_rot={"head": [0, 30, 0]})["head"][0]
            Rw = a1 @ a0.T; w, v = np.linalg.eig(Rw); ax = np.real(v[:, np.argmin(np.abs(w - 1))]); tilt = math.degrees(math.acos(min(1, abs(ax[1]) / np.linalg.norm(ax))))
            check(f"H {tag} look axis", tilt <= 5.0 and abs(_angle(Rw) - 30) < 1.0, f"yaw axis {tilt:.2f} deg from vertical, turn {_angle(Rw):.1f} deg")
            la = ent_new["animations"].get("look_at_target"); relb = [b for b, v in (anims.get(la, {}).get("bones") or {}).items() if isinstance(v, dict) and v.get("relative_to")]
            check(f"I {tag} look", la == B.LOOK_ID and not relb and "head" in (anims.get(la, {}).get("bones") or {}), f"look_at_target -> {la}; relative_to bones {relb}")
    # M — donkey / mule
    for mob, fname, ident in B.EQUINE_FIX:
        p, g = geo(ident); bones = g["bones"]; by = {b["name"]: b for b in bones}
        eb, *_ = equine_b.build(mob)
        same = json.dumps(eb, sort_keys=True) == json.dumps(bones, sort_keys=True)
        ent = jl(NEW / f"entity/{mob}.entity.json")["minecraft:client_entity"]["description"]
        pv = set()
        for rc in ent.get("render_controllers", []):
            k = rc if isinstance(rc, str) else list(rc)[0]
            for pp in (rcs.get(k, {}).get("part_visibility") or []): pv |= {x for x in pp if x != "*"}
        empty = sorted(x for x in pv if x in by and not by[x].get("cubes")); absent = sorted(x for x in pv if x not in by)
        check(f"M {mob}", same and not empty and not absent and {"left_chest", "right_chest"} <= pv,
              f"== equine_b {same}; pv bones {sorted(pv)}; empty {empty}; absent {absent}")
    print(f"\n{'GATE OPEN' if not fails else 'GATE CLOSED'} {n - len(fails)}/{n}" + (f"  FAILS: {fails}" if fails else ""))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
