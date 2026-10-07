#!/usr/bin/env python3
"""verify_rp07_1415_rp06_1410.py — gate for RP-07 v1.4.15 + RP-06 v1.4.10 (D-C269).
  A  diff vs 1.4.14 / 1.4.9 = exactly the planned files (nothing else touched)
  B  equine cubes == the Patrix JEM cubes (same sizes, inflate and per-face UVs, one-for-one) and every cube centre within 1.0 px
     of the Patrix FreshLX rest bake (age 0) — i.e. the geometry IS the Patrix model in its rest posture
  C  joints are real (his symptom): skull∩neck, muzzle∩skull, ears∩skull, forelock∩skull, mane∩neck, tail∩body, legs touch body,
     chests touch body — each pair's boxes overlap or touch (sampled points within 0.3 px)
  D  two ears, apart: ear centres ≥ 2.5 px apart; donkey/mule ears splay outward (±15°)
  E  look: no relative_to-entity bone under a rotated ancestor in the 5 entities; the look animation's bones (neck, head) exist;
     every bone each equine entity animates exists (known shim placeholder aside); render-controller part_visibility bones exist
  F  eyes: the 4 geometries carry no eye bones; no RP-07 entity names a *.pw.eyes animation; every animate entry has its key
  G  zombie-villager.png: only the head-front texels changed, and none of them is transparent any more
  H  every changed / added JSON parses; manifests 1.4.15 / 1.4.10 with their uuids kept; no other pack in the local stack defines
     the 5 equine client entities or geometry ids
Exit 1 on any FAIL."""
import filecmp, glob, json, math, re, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines, rot_matrix
from jem_convert import bake_rest2, to_bedrock, jem_tree, load_json as jload
from entity_render import transform

ROOT = Path("/home/claude")
O7, N7, O6, N6 = ROOT / "_build/rp07-1414", ROOT / "_build/rp07-1415", ROOT / "_build/rp06-149", ROOT / "_build/rp06-1410"
CEM = ROOT / "_intake/patrix-mobs/assets/minecraft/optifine/cem"
SEEDS = {"neck": {"ty": 4.0, "tz": -12.0, "rx": 0.5235988}, "body": {"rx": 0.0}, "tail": {"ry": 0.0}}
EQ = [("horse", N7, "horse.geo.json", "geometry.horse.patrix", "horse"), ("donkey", N7, "pw_donkey.geo.json", "geometry.pw_donkey", "donkey"),
      ("mule", N7, "pw_mule.geo.json", "geometry.pw_mule", "mule"), ("zombie_horse", N6, "zombie_horse.geo.json", "geometry.zombie_horse.patrix", "zombie_horse"),
      ("skeleton_horse", N6, "skeleton_horse.geo.json", "geometry.skeleton_horse.patrix", "skeleton_horse")]
PW_EYES_ENTS = {"axolotl", "cod", "dolphin", "donkey", "horse", "llama", "mule", "pig", "salmon", "sheep", "trader_llama", "turtle"}
EYE = re.compile(r"eye|pupil|iris|blink|lid|brow|sclera", re.I)
results = []


def check(tag, ok, msg):
    results.append((tag, bool(ok), msg)); print(f"{'PASS' if ok else 'FAIL'} {tag}: {msg}")


def jl(p):
    t = re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M)
    try: return json.loads(t)
    except json.JSONDecodeError: return json.loads(re.sub(r",(\s*[}\]])", r"\1", t))


def files(root):
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def geo(root, fname, ident):
    d = jl(root / "models/entity" / fname)
    g = next(x for x in d["minecraft:geometry"] if x["description"]["identifier"] == ident)
    return g["bones"], g["description"]


def world_boxes(bones):
    """[(bone, cube index, 8 world corners (file frame), size, inflate, uv)] with every bone + cube rotation applied."""
    aff = bone_affines(bones); out = []
    for b in bones:
        A, t = aff[b["name"]]
        for i, c in enumerate(b.get("cubes", [])):
            o, s = np.array(c["origin"], float), np.array(c["size"], float); inf = c.get("inflate", 0) or 0
            lo, hi = o - inf, o + s + inf
            pts = [np.array([x, y, z]) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
            if any(c.get("rotation", [0, 0, 0]) or []): pts = [np.array(transform(list(p), c.get("pivot", [0, 0, 0]), c["rotation"])) for p in pts]
            out.append((b["name"], i, [A @ p + t for p in pts], [round(v, 4) for v in c["size"]], round(inf, 4), json.dumps(c.get("uv"), sort_keys=True)))
    return out


def inside_frac(box_pts_a, box_pts_b, tol=0.3):
    """Do boxes A and B overlap or touch? Sample A densely (6^3 incl. surface) and test against B's own frame."""
    B = np.array(box_pts_b); o = B[0]; ex = B[4] - o; ey = B[2] - o; ez = B[1] - o
    M = np.stack([ex, ey, ez], 1)
    try: Minv = np.linalg.inv(M)
    except np.linalg.LinAlgError: return False
    lens = np.array([np.linalg.norm(ex), np.linalg.norm(ey), np.linalg.norm(ez)])
    A = np.array(box_pts_a); a0 = A[0]; ax, ay, az = A[4] - a0, A[2] - a0, A[1] - a0
    for i in np.linspace(0, 1, 6):
        for j in np.linspace(0, 1, 6):
            for k in np.linspace(0, 1, 6):
                p = a0 + ax * i + ay * j + az * k
                f = Minv @ (p - o)
                slack = tol / np.maximum(lens, 1e-6)
                if np.all(f >= -slack) and np.all(f <= 1 + slack): return True
    return False


def main():
    # A — diff
    exp7_changed = {"models/entity/horse.geo.json", "models/entity/pw_donkey.geo.json", "models/entity/pw_mule.geo.json", "models/entity/villager.geo.json",
                    "models/entity/bee.geo.json", "models/entity/ravager.geo.json", "models/entity/zombie_villager_v2.geo.json",
                    "textures/entity/zombie_villager2/zombie-villager.png", "manifest.json"} | {f"entity/{e}.entity.json" for e in PW_EYES_ENTS}
    f7o, f7n = files(O7), files(N7)
    ch7 = {f for f in f7o & f7n if not filecmp.cmp(O7 / f, N7 / f, shallow=False)}
    check("A1 RP-07", f7n - f7o == {"animations/pw_equine_look.animation.json"} and not (f7o - f7n) and ch7 == exp7_changed,
          f"added {sorted(f7n - f7o)} removed {sorted(f7o - f7n)} changed {len(ch7)} (unexpected {sorted(ch7 - exp7_changed)}, missing {sorted(exp7_changed - ch7)})")
    exp6_changed = {"models/entity/zombie_horse.geo.json", "models/entity/skeleton_horse.geo.json", "entity/zombie_horse.entity.json",
                    "entity/skeleton_horse.entity.json", "manifest.json"}
    f6o, f6n = files(O6), files(N6)
    ch6 = {f for f in f6o & f6n if not filecmp.cmp(O6 / f, N6 / f, shallow=False)}
    check("A2 RP-06", f6n - f6o == {"animations/pw_undead_equine_look.animation.json"} and not (f6o - f6n) and ch6 == exp6_changed,
          f"added {sorted(f6n - f6o)} changed {sorted(ch6)}")
    # B/C/D — equines
    for mob, root, fname, ident, jname in EQ:
        bones, desc = geo(root, fname, ident)
        jem = jload(CEM / f"{jname}.jem"); pbb, _, err = bake_rest2(jem, jname, seeds=SEEDS); pb = to_bedrock(pbb)
        ours = world_boxes(bones); theirs = world_boxes(pb)
        key = lambda x: (tuple(x[3]), x[4], x[5])
        ko = sorted(key(x) for x in ours); kt = sorted(key(x) for x in theirs)
        check(f"B1 {mob}", ko == kt and (desc["texture_width"], desc["texture_height"]) == tuple(jem.get("textureSize", [64, 64])),
              f"{len(ours)} cubes == the JEM's {len(theirs)} (size, inflate, per-face UV one-for-one); texture {desc['texture_width']}x{desc['texture_height']}")
        # legs: the static JEM stance (our walk/idle animations drive them) — compared to the un-animated JEM, exact;
        # everything else: the FreshLX rest posture — compared to the age-0 rest bake, within 1 px (the build averages the idle sway)
        static = world_boxes(to_bedrock(jem_tree(jem)))
        LEGS = {"leg0", "leg1", "leg2", "leg3"}
        worst = {"legs": (0.0, None), "posture": (0.0, None)}
        pools = {"legs": list(static), "posture": list(theirs)}
        for x in ours:
            grp = "legs" if x[0] in LEGS else "posture"
            cands = [y for y in pools[grp] if key(y) == key(x)]
            ctr = np.mean(x[2], 0)
            d, y = min(((float(np.linalg.norm(ctr - np.mean(y[2], 0))), y) for y in cands), key=lambda t: t[0])
            pools[grp].remove(y)
            if d > worst[grp][0]: worst[grp] = (d, x[0])
        check(f"B2 {mob}", worst["legs"][0] <= 0.01 and worst["posture"][0] <= 1.0,
              f"posture cubes within {worst['posture'][0]:.2f} px of the Patrix rest bake (worst {worst['posture'][1]}); "
              f"leg cubes within {worst['legs'][0]:.3f} px of the static JEM stance")
        W = {}
        for x in ours: W.setdefault(x[0], []).append(x[2])
        pairs = [("head2", "neck" if "neck" in W else "neck_bones"), ("snout", "head2"), ("left_ear", "head2"), ("right_ear", "head2"),
                 ("mane_top", "head2"), ("mane", "neck"), ("tail", "body"), ("leg0", "body"), ("leg1", "body"), ("leg2", "body"), ("leg3", "body"),
                 ("right_chest_rot", "body"), ("left_chest_rot", "body")]
        touch = lambda a, b: any(inside_frac(p, q) or inside_frac(q, p) for p in W[a] for q in W[b])
        bad = [f"{a}-{b}" for a, b in pairs if a in W and b in W and not touch(a, b)]
        checked = [f"{a}-{b}" for a, b in pairs if a in W and b in W]
        check(f"C {mob}", not bad and len(checked) >= 6, f"{len(checked)} joints touch/overlap" + (f"; APART: {bad}" if bad else ""))
        if "left_ear" in W:
            cl, cr = np.mean(W["left_ear"][0], 0), np.mean(W["right_ear"][0], 0)
            by = {b["name"]: b for b in bones}
            splay = (by["left_ear"].get("rotation", [0, 0, 0])[2], by["right_ear"].get("rotation", [0, 0, 0])[2])
            want_splay = mob in ("donkey", "mule")
            check(f"D {mob}", abs(cl[0] - cr[0]) >= 2.5 and (not want_splay or (splay[0] * splay[1] < 0 and min(abs(splay[0]), abs(splay[1])) >= 14)),
                  f"ear centres {abs(cl[0] - cr[0]):.2f} px apart; roll {splay}")
    # E — look + references
    ents = {"horse": N7, "donkey": N7, "mule": N7, "zombie_horse": N6, "skeleton_horse": N6}
    anims = {}
    for root in (N7, N6, ROOT / "_intake/bedrock-samples/resource_pack"):
        for f in glob.glob(str(root / "animations/*.json")):
            try: d = jl(f)
            except Exception: continue
            for k, v in d.get("animations", {}).items(): anims.setdefault(k, v)
    geo_of = {m: geo(r, fn, i)[0] for m, r, fn, i, _ in EQ}
    for e, root in ents.items():
        desc = jl(root / f"entity/{e}.entity.json")["minecraft:client_entity"]["description"]
        bones = {b["name"].lower(): b for b in geo_of[e]}
        rel_bad, missing = [], set()
        for short, aid in desc["animations"].items():
            a = anims.get(aid)
            if not isinstance(a, dict): continue
            for bn, bv in (a.get("bones") or {}).items():
                if bn.lower() not in bones: missing.add(bn); continue
                if isinstance(bv, dict) and (bv.get("relative_to") or {}).get("rotation") == "entity":
                    n = bones.get((bones[bn.lower()].get("parent") or "").lower())
                    while n:
                        if any(abs(x) > 0.01 for x in (n.get("rotation") or [0, 0, 0])): rel_bad.append(bn); break
                        n = bones.get((n.get("parent") or "").lower())
        look = anims.get(desc["animations"].get("look_at_target"), {})
        look_ok = set((look.get("bones") or {}).keys()) == {"neck", "head"} and all(b in bones for b in ("neck", "head"))
        allowed = {"placeholder_bone"}                                 # the animation.horse.setup shim's own no-op bone
        check(f"E1 {e}", not rel_bad and look_ok and not (missing - allowed),
              f"look = {desc['animations'].get('look_at_target')} (neck+head present: {look_ok}); relative_to under a rotated parent: {rel_bad}; "
              f"animated bones missing: {sorted(missing - allowed)}")
        rcs = desc.get("render_controllers", [])
        vis = set()
        for rcf in glob.glob(str(root / "render_controllers/*.json")) + glob.glob(str(N7 / "render_controllers/*.json")):
            try: d = jl(rcf)
            except Exception: continue
            for rc in rcs:
                k = rc if isinstance(rc, str) else list(rc)[0]
                v = d.get("render_controllers", {}).get(k)
                if v:
                    for pv in v.get("part_visibility", []) or []: vis |= set(pv)
        check(f"E2 {e}", all(b.lower() in bones for b in vis), f"part_visibility bones {sorted(vis)} exist")
    # F — eyes
    eye_left = {}
    for fname, ident in (("villager.geo.json", "geometry.villager"), ("bee.geo.json", "geometry.bee"), ("ravager.geo.json", "geometry.ravager"),
                         ("zombie_villager_v2.geo.json", "geometry.zombie.villager_v2")):
        bones, _ = geo(N7, fname, ident)
        left = [b["name"] for b in bones if EYE.search(b["name"])]
        if left: eye_left[ident] = left
    check("F1", not eye_left, f"eye bones left: {eye_left}")
    pw_eyes_left, dangling = [], []
    for p in sorted((N7 / "entity").glob("*.json")):
        t = p.read_text(encoding="utf-8-sig", errors="replace")
        if ".pw.eyes" in t: pw_eyes_left.append(p.name)
        if p.stem.split(".")[0] in PW_EYES_ENTS | set(ents):
            desc = jl(p)["minecraft:client_entity"]["description"]
            keys = set(desc.get("animations", {}))
            for a in (desc.get("scripts") or {}).get("animate", []) or []:
                for k in ([a] if isinstance(a, str) else list(a)):
                    if k not in keys: dangling.append((p.name, k))
    check("F2", not pw_eyes_left and not dangling, f"*.pw.eyes left {pw_eyes_left}; animate entries without a key {dangling}")
    # G — zombie villager skin
    a = np.asarray(Image.open(O7 / "textures/entity/zombie_villager2/zombie-villager.png").convert("RGBA")).astype(int)
    b = np.asarray(Image.open(N7 / "textures/entity/zombie_villager2/zombie-villager.png").convert("RGBA")).astype(int)
    diff = np.argwhere(np.any(a != b, axis=2))
    inside = all(8 <= y < 18 and 8 <= x < 16 for y, x in diff)
    holes = int((b[8:18, 8:16, 3] < 128).sum())
    check("G", a.shape == b.shape and inside and holes == 0 and len(diff) > 0, f"{len(diff)} texels changed, all in the head front: {inside}; transparent texels left in the face: {holes}")
    # H — parse, manifests, uniqueness in the local stack
    bad = []
    for root, fs in ((N7, ch7 | {"animations/pw_equine_look.animation.json"}), (N6, ch6 | {"animations/pw_undead_equine_look.animation.json"})):
        for f in fs:
            if f.endswith(".json"):
                try: json.loads((root / f).read_text(encoding="utf-8-sig"))
                except Exception as e: bad.append((f, str(e)[:60]))
    check("H1", not bad, f"strict-JSON parse of changed/added files: {bad}")
    m7o, m7n, m6o, m6n = (jl(r / "manifest.json") for r in (O7, N7, O6, N6))
    check("H2", m7n["header"]["version"] == [1, 4, 15] and m7n["header"]["uuid"] == m7o["header"]["uuid"] and m6n["header"]["version"] == [1, 4, 10]
          and m6n["header"]["uuid"] == m6o["header"]["uuid"], "manifests 1.4.15 / 1.4.10, uuids kept")
    ids = {"minecraft:horse", "minecraft:donkey", "minecraft:mule", "minecraft:zombie_horse", "minecraft:skeleton_horse"}
    gids = {i for *_, i, _ in EQ}
    holders = {}
    for root in [N7, N6] + [ROOT / p for p in ("_build/rp08-147", "_build/rp10-142", "_build/rp05-51", "_build/rp04-142", "_build/testrunner-rp-0.3.0", "_build/markers-0.2.1")]:
        for f in glob.glob(str(root / "**/*.json"), recursive=True):
            t = open(f, encoding="utf-8-sig", errors="replace").read()
            for i in ids | gids:
                if (f'"identifier": "{i}"' in t or f'"identifier":"{i}"' in t): holders.setdefault(i, set()).add(root.name)
    multi = {k: sorted(v) for k, v in holders.items() if len(v) > 1}
    check("H3", not multi and all(k in holders for k in ids | gids), f"each equine entity + geometry id held by one pack: {({k: sorted(v) for k, v in holders.items()})}")
    fails = [r for r in results if not r[1]]
    print(f"GATE {'OPEN' if not fails else 'CLOSED'} {len(results) - len(fails)}/{len(results)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
