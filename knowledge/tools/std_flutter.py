#!/usr/bin/env python3
"""std_flutter.py — the standard FLUTTER for the non-flying fowl (his F2 + 09:5x: "chickens don't fly … it would look more
like the bee or insect flap, and they would get hang time without producing lift — only for a short time, before giving
up and falling back to the ground"). Birds: minecraft:chicken, sf_nba:turkey / peafowl / kakapo, pw:turkey_wa,
pw:kakapo_wwa.

Rig (identity at rest): parent -> [shoulder_level_<s> (bind = parent^-1)] -> shoulder_fly_<s> -> [shoulder_unlevel_<s>]
-> shoulder_<s>, all at the shoulder pivot — the flutter turns about the ENTITY's forward / up axes.
Motion while airborne (v.std_u eases 0 -> 1 at 4 / s after leaving the ground, as for the fliers):
  lift  the wings rise out from the body to ~40 deg (the "giving it everything" pose)
  buzz  a fast, short beat ±28 deg about that lift, period 0.11 s (bee-like), tiny sweep a quarter-beat late
  tire  the beat fades after ~1.2 s in the air (v.std_air counts airborne seconds) to a slow ±10 deg — giving up
The hang time / fall itself is movement physics (behavior side), not animation: noted for his review.
The bird's own airborne wing channels (falling / flapping clips) are removed from the std copy — the flutter drives them."""
import copy
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
import std_flight as FL  # noqa: E402
import std_stepc as SC  # noqa: E402
import std_cube as CU  # noqa: E402
import std_wingsplit as W  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

FLUTTER_IDS = ["minecraft:chicken", "sf_nba:turkey", "sf_nba:peafowl", "sf_nba:kakapo", "pw:turkey_wa", "pw:kakapo_wwa"]
PERIOD = 0.11
AIRBORNE = r"fly|flying|flap|glide|soar|fall"


def sign_point(bones, joint, axis, offset_world, want_world):
    """+1 / -1: the sign of a rotation about `joint`'s local axis that moves the point (joint pivot + offset_world, carried
    by the joint) along want_world."""
    def at(deg):
        add = [0.0, 0.0, 0.0]
        add[axis] = deg
        aff = bone_affines(bones, add_rot={joint: add})
        A, t = aff[joint]
        A0, t0 = bone_affines(bones)[joint]
        piv = np.array(next(b for b in bones if b["name"] == joint).get("pivot", [0, 0, 0]), float)
        p_file = np.linalg.solve(A0, (A0 @ piv + t0 + np.array(offset_world, float)) - t0)
        return A @ p_file + t
    return 1.0 if (at(5.0) - at(0.0)) @ np.array(want_world, float) >= 0 else -1.0


def mirror_error(bones, anim, sides, envs):
    """max |left - mirrored right| of the two wing roots' outer pieces' centres over the moments (px)."""
    worst = 0.0
    for env in envs:
        b2 = FL.preview_pose(bones, anim, env)
        aff = bone_affines(b2)
        by = {b["name"]: b for b in b2}
        cen = {}
        for s in sides:
            ps = [A @ CU.centre(c) + t for n in FL.subtree(b2, f"shoulder_{s}") for c in by[n].get("cubes") or []
                  for A, t in [aff[n]]]
            cen[s] = np.mean(ps, axis=0)
        if len(cen) == 2:
            worst = max(worst, float(np.linalg.norm(cen["l"] - cen["r"] * np.array([-1.0, 1.0, 1.0]))))
    return worst


def build(mob, P):
    rp = P.path.name
    st = SC.Staged(rp, mob)
    slug = S.slug_of(mob)
    rep = {"mob": mob}
    for geo in st.geo["minecraft:geometry"]:          # adult + any baby geometry in the same file
        bones = geo["bones"]
        assert not any(b["name"].startswith("shoulder_fly_") for b in bones), "already built"
        aff = bone_affines(bones)
        by = {b["name"]: b for b in bones}
        for s in ("l", "r"):
            sh = f"shoulder_{s}"
            if sh not in by:
                continue
            parent = by[sh].get("parent")
            # the flutter turns the wing about the centre of its ROOT edge (its top edge, against the body): it lifts
            # off the flank without a gap at the seam (his 12:58) and without the upper half dipping into the body
            span, nrm, chord, sp = FL.wing_frame(bones, s)
            root_w = FL.slide_point(bones, aff, FL.subtree(bones, sh), span, sp)
            piv = [round(float(x), 4) for x in FL.to_frame(aff, parent, root_w)]
            Ap = aff[parent][0] if parent else np.eye(3)
            if not np.allclose(Ap, np.eye(3), atol=1e-9):
                nb = [{"name": f"shoulder_level_{s}", "pivot": piv,
                       "rotation": [round(float(x), 6) for x in CU.euler_of(Ap.T)], **({"parent": parent} if parent else {})},
                      {"name": f"shoulder_fly_{s}", "parent": f"shoulder_level_{s}", "pivot": piv},
                      {"name": f"shoulder_unlevel_{s}", "parent": f"shoulder_fly_{s}", "pivot": piv,
                       "rotation": [round(float(x), 6) for x in CU.euler_of(Ap)]}]
                by[sh]["parent"] = f"shoulder_unlevel_{s}"
            else:
                nb = [{"name": f"shoulder_fly_{s}", "pivot": piv, **({"parent": parent} if parent else {})}]
                by[sh]["parent"] = f"shoulder_fly_{s}"
            i = bones.index(by[sh])
            bones[i:i] = nb
    st.save()
    g0 = st.geo["minecraft:geometry"][0]["bones"]
    sides = [s for s in ("l", "r") if any(b["name"] == f"shoulder_fly_{s}" for b in g0)]
    # signs measured on the adult rig: + lift = wing tip UP and OUT
    lift = "math.clamp((v.std_u - 0.1) / 0.5, 0, 1)"
    tire = "math.clamp(1.0 - (v.std_air - 1.2) / 0.6, 0.35, 1.0)"
    ph = f"((q.life_time + v.std_r) * {360.0 / PERIOD:.3f})"
    out = {}
    for s in sides:
        tip = next((n for n in (f"wing_inner_{s}",) if any(b["name"] == n and b.get("cubes") for b in g0)), None)
        tip = tip or next(b["name"] for b in g0 if b["name"] in FL.subtree(g0, f"shoulder_{s}") and b.get("cubes"))
        # a wing hanging BELOW its shoulder rises either way about the forward axis (first order the tip moves
        # sideways): the wanted move is OUT (away from the body) and up — turkey / kakapo went inward on "up" alone
        aff0 = bone_affines(g0)
        A0, t0 = aff0[tip]
        cx = float(np.mean([A0 @ CU.centre(c) + t0 for c in next(b for b in g0 if b["name"] == tip)["cubes"]], axis=0)[0])
        out_x = 1.0 if cx > 0 else -1.0
        sf = FL.sign_for(g0, f"shoulder_fly_{s}", 2, tip, [out_x, 0.4, 0.0])
        # sweep: + = the wing's OUTER side moves forward. Measured on a point 6 px out to that side of the joint (a
        # hanging wing's own centre sits almost on the turning axis — its sign came out the same on both sides, so one
        # wing swept forward while the other swept back into the body: his J4, 13:06)
        ss = sign_point(g0, f"shoulder_fly_{s}", 1, [out_x * 6.0, 0.0, 0.0], [0.0, 0.0, -1.0])
        out[f"shoulder_fly_{s}"] = {"rotation": [
            "0",
            f"{ss * 6.0:.1f} * math.sin({ph} - 90) * {tire} * {lift}",
            f"{sf:.0f} * (40.0 * {lift} + 28.0 * math.sin({ph}) * {tire} * {lift})"]}
            # (no slide: a 1 px out-slide opened a visible gap at the shoulder seam — his 12:58 report)
    st.anim["animations"][f"animation.std.{slug}.flutter"] = {"loop": True, "bones": out}
    wing = set()
    for s in sides:
        wing |= set(FL.subtree(g0, f"shoulder_{s}"))
    n = 0
    for aid, a in st.anim["animations"].items():
        if aid.startswith(f"animation.std.{slug}.flutter") or not re.search(AIRBORNE, aid):
            continue
        for k in list(a.get("bones") or {}):
            if k in wing:
                del a["bones"][k]
                n += 1
    st.save()
    ef = S.STAGE / rp / f"entity/std/{slug}.entity.json"
    ent = S.jload(ef)
    d = ent["minecraft:client_entity"]["description"]
    d.setdefault("animations", {})["std_flutter"] = f"animation.std.{slug}.flutter"
    sc = d.setdefault("scripts", {})
    sc["animate"] = [a for a in sc.get("animate") or [] if not (a == "std_flutter" or (isinstance(a, dict) and "std_flutter" in a))]
    sc["animate"].append("std_flutter")
    init = sc.setdefault("initialize", [])
    for line in ("v.std_r = math.random(0.0, 1.0);", "v.std_u = 0.0;", "v.std_air = 0.0;"):
        if line.split("=")[0] not in "".join(init):
            init.append(line)
    pre = sc.setdefault("pre_animation", [])
    pre[:] = [x for x in pre if "v.std_u" not in x and "v.std_air" not in x]
    pre.append("v.std_u = v.std_u + ((q.is_on_ground ? 0.0 : 1.0) - v.std_u) * math.min(1.0, q.delta_time * 4.0);")
    pre.append("v.std_air = q.is_on_ground ? 0.0 : v.std_air + q.delta_time;")
    ef.write_text(json.dumps(ent, indent=1))
    rep.update({"sides": sides, "stripped_channels": n})
    return rep


def main(ids=None):
    census = {c["id"]: c for c in json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())}
    lines = ["# FLUTTER — standard flutter on the non-flying fowl", "",
             "| mob | sides | old airborne wing channels removed | G1 ground misses | G4 names | G3 clip pts (lifted, mid-beat) | G6 mirror px (beyond the rest asymmetry) |",
             "|---|---|---|---|---|---|---|"]
    packs = {}
    import std_flight_batch as FB
    for mob in ids or FLUTTER_IDS:
        rp = census[mob]["rp"].replace("rp07-1438", "rp07-1439").replace("rp06-1424", "rp06-1425")
        P = packs.setdefault(rp, S.Pack(ROOT / "_build" / rp))
        slug = S.slug_of(mob)
        before = copy.deepcopy(S.jload(S.STAGE / rp / f"models/entity/std/{slug}.geo.json")["minecraft:geometry"][0]["bones"])
        rep = build(mob, P)
        g = S.jload(S.STAGE / rp / f"models/entity/std/{slug}.geo.json")["minecraft:geometry"][0]
        an = S.jload(S.STAGE / rp / f"animations/std/{slug}.animation.json")["animations"][f"animation.std.{slug}.flutter"]["bones"]
        tw, th = g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)
        ground = FL.preview_pose(g["bones"], an, {"q.life_time": 0.37, "v.std_r": 0.0, "v.std_u": 0.0, "v.std_air": 0.0})
        m1, m2, _, _ = W.uv_gate(before, ground, tw, th)
        g4 = all(k in {b["name"] for b in g["bones"]} for k in an)
        posed = FL.preview_pose(g["bones"], an, {"q.life_time": PERIOD / 4, "v.std_r": 0.0, "v.std_u": 1.0, "v.std_air": 0.5})
        clip = FB.clip_count(posed, rep["sides"])
        envs = [{"q.life_time": PERIOD * f, "v.std_r": 0.0, "v.std_u": 1.0, "v.std_air": 0.5} for f in (0, .25, .5, .75)]
        ground = [{"q.life_time": 0.0, "v.std_r": 0.0, "v.std_u": 0.0, "v.std_air": 0.0}]
        mir = mirror_error(g["bones"], an, rep["sides"], envs) - mirror_error(g["bones"], an, rep["sides"], ground)
        lines.append(f"| {mob} | {'/'.join(rep['sides'])} | {rep['stripped_channels']} | {m1 + m2} | {'ok' if g4 else 'MISSING'} | {clip} | {mir:.3f} |")
        print(mob, "G1", m1 + m2, "G4", g4, "G3", clip, "G6", round(mir, 3), rep, flush=True)
    import report_merge as RM   # 10-01: partial runs merge
    RM.write_table(ROOT / "_docs/standard/FLUTTER-BIRDS.md", "\n".join(lines) + "\n", partial=bool(ids))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
