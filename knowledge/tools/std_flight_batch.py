#!/usr/bin/env python3
"""std_flight_batch.py — Phase 3a batch: the v2 standard flight on every non-Patrix FLIGHT bird + its gates.
  G1 GROUND  the resting pose (v.std_u = 0) is texel-identical to the standardized rig before the flight was added
  G2 CONTACT opening gap between neighbouring wing pieces over a full beat in flight (v.std_u = 1), both wings
  G3 CLIP    wing-surface sample points that end up INSIDE a body cube during the beat (reported for his eye)
  G4 NAMES   every bone the flight animation drives exists
Writes _docs/standard/FLIGHT-BIRDS.md."""
import copy
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
import std_birds_b as BB  # noqa: E402
import std_flight as FL  # noqa: E402
import std_wingsplit as W  # noqa: E402
import wing_gap as G  # noqa: E402
import std_cube as CU  # noqa: E402
import contact_gate as CG  # noqa: E402
from bb_truth import truth_posed_faces  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

PATRIX_OWN = {"minecraft:parrot", "minecraft:bat", "minecraft:phantom"}


def clip_count(bones, sides):
    """wing face samples inside any non-wing, non-leg cube (posed)."""
    aff = bone_affines(bones)
    by = {b["name"]: b for b in bones}
    wing = set()
    for s in sides:
        wing |= set(FL.subtree(bones, f"shoulder_fly_{s}"))
    legs = {n for n in by if n.split("_")[0] in ("hip", "thigh", "knee", "shin", "ankle", "foot", "toe", "thighs",
                                                    "shins", "feet", "toes", "legs")}
    body_boxes = []
    for n, b in by.items():
        if n in wing or n in legs:
            continue
        A, t = aff[n]
        for c in b.get("cubes") or []:
            lo, hi = CU.box(c)
            Rc, tc = CU.cube_affine(c)                        # cube rotation applied
            body_boxes.append((A @ Rc, A @ tc + t, lo + 0.05, hi - 0.05))   # a 0.05 px skin: touching is not clipping
    d = bones[0]
    faces = [f for f in truth_posed_faces(bones, 64, 64, aff) if f.bone in wing]
    n = 0
    for f in faces:
        P = [np.array(p, float) for p in f.pts]
        for a in (0.25, 0.5, 0.75):
            for b in (0.25, 0.5, 0.75):
                q = P[0] + a * (P[1] - P[0]) + b * (P[3] - P[0])
                for A, t, lo, hi in body_boxes:
                    l = np.linalg.solve(A, q - t)
                    if np.all(l > lo) and np.all(l < hi):
                        n += 1
                        break
    return n


LEG_TOKENS = ("hip", "thigh", "knee", "shin", "ankle", "foot", "toe", "thighs", "shins", "feet", "toes", "legs")


def leg_contact(bones, an):
    """G5 CONNECTION: leg pieces (and whatever they touch: body, other leg pieces) still touch during the unfold and in
    flight (u = 0.5 and 1). Returns (worst gap px, pair)."""
    legs = [b["name"] for b in bones if b["name"].split("_")[0] in LEG_TOKENS]
    by = {b["name"]: b for b in bones}

    def ancestors(n):
        out = []
        while by[n].get("parent") in by:
            n = by[n]["parent"]
            out.append(n)
        return out
    # the married connections only: leg piece <-> leg piece, and leg piece <-> the cube-carrying bone it hangs from
    # (body / root); a tail that merely touches a thigh at rest is not one
    pairs = [(a, b) for a, b in CG.touching_pairs(bones, legs)
             if not ({a.rsplit("_", 1)[-1], b.rsplit("_", 1)[-1]} == {"l", "r"})   # left leg vs right leg: not married
             and (b in legs or b in ancestors(a) or a in ancestors(b)
             or b.split("_")[0] in ("body", "torso", "chest", "belly", "pelvis", "hips", "root"))]
    w = (0.0, None)
    for u in (0.5, 1.0):
        d = CG.worst(FL.preview_pose(bones, an, {"q.life_time": 0.0, "v.std_r": 0.0, "v.std_u": u}), pairs)
        if d[0] > w[0]:
            w = d
    return w


def root_gap(bones, an, rep, T):
    """G6 ROOT CONTACT (his 13:04): in flight the wing's root point (the slide point) lies on the body surface — the
    largest distance from it to the torso over a beat (0 when on / inside the body surface)."""
    from equine_compare import bone_affines as BA
    obbs = FL.body_obbs(bones)
    if not obbs:
        return None
    worst = 0.0
    for f in [i / 8 for i in range(8)]:
        posed = FL.preview_pose(bones, an, {"q.life_time": f * T, "v.std_r": 0.0, "v.std_u": 1.0})
        aff = BA(posed)
        by = {b["name"]: b for b in posed}
        for s in rep["sides"]:
            n = f"shoulder_out_{s}"
            A, t = aff[n]
            p = A @ np.array(by[n]["pivot"], float) + t
            d = min(float(np.linalg.norm(L - np.clip(L, lo, hi))) for M, tt, lo, hi in obbs
                    for L in [np.linalg.solve(M, p - tt)])
            worst = max(worst, d)
    return worst


def main(ids=None):
    rows = json.loads((ROOT / "_docs/standard/BIRD-RIG-MAP.json").read_text())
    census = {c["id"]: c for c in json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())}
    plan = {r["id"]: r for r in json.loads((ROOT / "_docs/sizes/size_law_v2_plan.json").read_text())}
    todo = [r["id"] for r in rows if BB.flight_class(r["id"]) == "FLIGHT" and r["id"] not in PATRIX_OWN
            and r["class"] != "NO-WINGS-FOUND"]
    if ids:
        todo = [i for i in todo if i in ids]
    packs = {}
    lines = ["# FLIGHT v2 — standard flight on the non-Patrix flying birds", "",
             "| mob | beat s | glide | unfold out / fwd (l) | stretch | tuck from library | G1 ground misses | G2 gap px | G3 clip pts | G4 | G5 leg contact px | G6 root gap px | slide (l) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for mob in todo:
        rp = census[mob]["rp"].replace("rp07-1438", "rp07-1439").replace("rp06-1424", "rp06-1425")
        P = packs.setdefault(rp, S.Pack(ROOT / "_build" / rp))
        slug = S.slug_of(mob)
        before = copy.deepcopy(S.jload(S.STAGE / rp / f"models/entity/std/{slug}.geo.json")["minecraft:geometry"][0]["bones"])
        try:
            rep = FL.build_v2(mob, P, plan.get(mob))
        except AssertionError as e:
            lines.append(f"| {mob} | REFUSED {e} |||||||||")
            print(mob, "REFUSED", e)
            continue
        g = S.jload(S.STAGE / rp / f"models/entity/std/{slug}.geo.json")["minecraft:geometry"][0]
        an = S.jload(S.STAGE / rp / f"animations/std/{slug}.animation.json")["animations"][f"animation.std.{slug}.flight"]["bones"]
        tw, th = g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)
        # G1
        ground = FL.preview_pose(g["bones"], an, {"q.life_time": 0.37, "v.std_r": 0.0, "v.std_u": 0.0})
        m1, m2, _, _ = W.uv_gate(before, ground, tw, th)
        if any(f.get("fold") for f in rep["flight"].values()):
            # his J5: this bird's ground pose is now the Z-fold (intentional) — G1 checks the FLIGHT pose instead:
            # wings fully out, no beat (flap envelope 0 at u = 0.7) = the authored spread rest
            # rig check without the fold channels: the standardized rig + flight joints at rest still equal the bird
            drop = {k for s_, f in rep["flight"].items() if f.get("fold")
                    for k in [f"shoulder_out_{s_}", f"shoulder_fwd_{s_}", f"shoulder_stretch_{s_}"] + f.get("fold_joints", [])}
            nofold = {k: v for k, v in an.items() if k not in drop}
            for s_ in rep["flight"]:   # the rest-anchor slide on the fly joint
                if f"shoulder_fly_{s_}" in nofold:
                    nofold[f"shoulder_fly_{s_}"] = {c: v for c, v in nofold[f"shoulder_fly_{s_}"].items() if c != "position"}
            g_nf = FL.preview_pose(g["bones"], nofold, {"q.life_time": 0.37, "v.std_r": 0.0, "v.std_u": 0.0})
            m1, m2, _, _ = W.uv_gate(before, g_nf, tw, th)
        # G2 + G3 over a beat
        T, sides = rep["period"], rep["sides"]
        names = {b["name"] for b in g["bones"]}
        envs = [{"q.life_time": f * T, "v.std_r": 0.0, "v.std_u": 1.0} for f in [i / 10 for i in range(10)]]
        gap, clip = 0.0, 0
        static = {k: {c: v for c, v in ch.items() if c != "scale"} for k, ch in an.items()}
        for s in sides:
            seq = [x for x in [f"wing_inner_{s}", f"primary_{s}_1", f"primary_{s}_2", f"primary_{s}_3"] if x in names]
            gap = max(gap, G.gap(g["bones"], static, envs, list(zip(seq, seq[1:]))))
        for env in envs[::3]:
            clip += clip_count(FL.preview_pose(g["bones"], an, env), sides)
        g4 = all(k in names for k in an)
        g5, g5pair = leg_contact(g["bones"], an)
        g6 = root_gap(g["bones"], an, rep, T)
        f = rep["flight"].get("l") or next(iter(rep["flight"].values()))
        lines.append(f"| {mob} | {rep['period']} | {'yes' if rep['glide'] else ''} | {f['out']} / {f['fwd']} | {f['stretch']} | "
                     f"{'yes' if rep['tuck_from_library'] else 'default'} | {m1 + m2} | {gap:.3f} | {clip} | {'ok' if g4 else 'MISSING'} | "
                     f"{g5:.3f}{'' if g5 < CG.TOUCH else ' ' + '/'.join(g5pair)} | "
                     f"{'-' if g6 is None else f'{g6:.3f}'} | {f.get('slide_d')} |")
        print(mob, rep["period"], "G1", m1 + m2, "G2", round(gap, 3), "G3", clip, "G4", g4, "G5", round(g5, 3), g5pair if g5 >= CG.TOUCH else "",
              "G6", None if g6 is None else round(g6, 3), "slide", f.get("slide_d"), flush=True)
    import report_merge as RM   # 10-01: a run on some mobs merges into the report (16:55 fisher-only overwrite)
    RM.write_table(ROOT / "_docs/standard/FLIGHT-BIRDS.md", "\n".join(lines) + "\n", partial=bool(ids))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
