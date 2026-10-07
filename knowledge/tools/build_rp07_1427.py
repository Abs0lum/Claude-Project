#!/usr/bin/env python3
"""build_rp07_1427.py — R14 fix round (D-C306 / D-C307, his GO 00:5x CT 09-30). RP-07 Neutral Mobs RP v1.4.27 from v1.4.26.
  ALLAY       arms nested UNDER the body (Java AllayModel tree root > body > right_arm / left_arm; FreshLX's JEM subtracts
              body.r* in the arm formulas = it assumes the nesting). Converter B `anim_child`; rightItem (under body) and
              Mojang's locators re-applied after the re-bake. R14 f03/f05 "disconnected parts / the arms".
  POLAR BEAR  the April hand geometry replaced by the PATRIX model's cubes (Converter B bake of polar_bear.jem, rest pose):
              body blocks 3-4 px lower (the legs sink 3-4 px into the body as Patrix draws them), the NECK block restored, the
              legs the right way round (April had the hind-leg shape + UVs on the front legs and vice versa). The bones the
              April animations drive keep their names (body / body_cube / head / head2 / bone / leg0-3), so the walk / idle /
              ambient motion he has seen stays; the head pivot moves to z -11.5 (the point FreshLX's head translation swings
              the head around: tx = -4 sin(yaw), tz = 4.5 - 4.5 cos(yaw)); FreshLX's neck follow (neck.ry = head yaw / 3,
              neck.rx = head pitch / 4.5) as animation.pw_polar_bear.neck. R14 f14 "strangely tall / front legs".
Everything else byte-identical to 1.4.26. manifest 1.4.27, uuid kept. verify: verify_rp07_1427.py."""
import copy, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import convb
import build_rp07_1426 as B7                   # sets convb.CEM to the FA-1 symlink folder (same Patrix JEMs) + allay helpers
import fa_preview as FP
from verify_rp07_1415_rp06_1410 import world_boxes

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []

convb.JAVA_PARENT["allay"] = {"right_arm": "body", "left_arm": "body"}
for _c in ("right_arm", "left_arm"): convb.PART_PIVOT.setdefault("allay", {})[_c] = "anim_child"


def allay_check_port(dst):
    """the allay port is independent of the nesting (arm channels are Java-local deltas): prove the shipped one is what it gives"""
    init, pre, anim, _ = B7.al_port()
    shipped = R.jl(dst / "animations/pw_allay.animation.json")["animations"][B7.AL["anim"]]
    same = json.dumps(shipped, sort_keys=True) == json.dumps(json.loads(json.dumps(anim)), sort_keys=True)
    assert same, "the allay port changed with the nesting - stop and look"
    return "allay port re-run: identical to 1.4.26"


def allay_hand(dst):
    B7._redirect(); return B7.allay_hand(dst)


def allay_locators(dst):
    """Mojang's allay locators onto the re-baked bones (B7.carry_locators, allay only)"""
    keep = dict(B7.LOCATOR_MOBS)
    B7.LOCATOR_MOBS.clear(); B7.LOCATOR_MOBS["allay"] = keep["allay"]
    try: return B7.carry_locators(dst)
    finally: B7.LOCATOR_MOBS.clear(); B7.LOCATOR_MOBS.update(keep)


# ================================================================================================================= POLAR BEAR
PB_LEGS = {"leg0": "leg3", "leg1": "leg4", "leg2": "leg1", "leg3": "leg2"}     # our (April) name -> Patrix part (same side, same end)
PB_HEAD_PIVOT = [0.0, 14.0, -11.5]
PB_NECK_PIVOT = [0.0, 14.25, -10.0]            # where the neck meets the body's front face (the neck box's centre height)
PB_NECK_ANIM = "animation.pw_polar_bear.neck"
PB_NECK_DOC = {"format_version": "1.8.0", "animations": {PB_NECK_ANIM: {"loop": True, "bones": {
    "neck": {"rotation": ["q.target_x_rotation / 4.5", "q.target_y_rotation / 3.0", 0.0]}}}}}


def world_cube(pts, c):
    """a cube whose net bone rotation is identity: its axis-aligned world box, the face UVs kept"""
    P = np.array(pts); lo, hi = P.min(0), P.max(0)
    out = {k: v for k, v in c.items() if k not in ("origin", "size", "pivot", "rotation")}
    out["origin"] = [round(float(v), 4) for v in lo]; out["size"] = [round(float(v), 4) for v in hi - lo]
    return out


def polar_bear(dst):
    bake = FP.bake_any("polar_bear", "26.2")[0]
    wb = {}
    for n, i, pts, *_ in world_boxes(bake): wb.setdefault(n, []).append(pts)
    pby = {b["name"]: b for b in bake}
    # every Patrix cube we carry must sit on a bone whose net rotation is identity (body 90 then bone2 -90; legs / head 0)
    from equine_compare import bone_affines
    aff = bone_affines(bake)
    for n in ("bone2", "neck", "head", "leg1", "leg2", "leg3", "leg4"):
        assert np.allclose(aff[n][0], np.eye(3), atol=1e-6), (n, aff[n][0])
    p, g = R.geo_file(dst, "geometry.pw_polar_bear"); by = {b["name"]: b for b in g["bones"]}
    old = copy.deepcopy(g["bones"])
    by["body_cube"]["cubes"] = [world_cube(pts, c) for pts, c in zip(wb["bone2"], pby["bone2"]["cubes"])]
    for ours, pat in PB_LEGS.items():
        by[ours]["cubes"] = [world_cube(pts, c) for pts, c in zip(wb[pat], pby[pat]["cubes"])]
        by[ours]["pivot"] = [float(v) for v in pby[pat]["pivot"]]
    head_cubes = [world_cube(pts, c) for pts, c in zip(wb["head"], pby["head"]["cubes"])]
    by["head2"]["cubes"] = head_cubes
    by["head"]["pivot"] = list(PB_HEAD_PIVOT); by["head2"]["pivot"] = list(PB_HEAD_PIVOT)
    assert "neck" not in by
    neck = {"name": "neck", "parent": "body", "pivot": list(PB_NECK_PIVOT),
            "cubes": [world_cube(pts, c) for pts, c in zip(wb["neck"], pby["neck"]["cubes"])]}
    g["bones"].insert([b["name"] for b in g["bones"]].index("body_cube") + 1, neck)
    g["description"] = {"identifier": "geometry.pw_polar_bear", **R.bounds(g["description"], g["bones"], R.van_box("polar_bear", "default")),
                        "texture_width": g["description"]["texture_width"], "texture_height": g["description"]["texture_height"]}
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d); CHANGED.append(str(p.relative_to(dst)))
    R.wj(dst / "animations/pw_polar_bear_neck.animation.json", PB_NECK_DOC); ADDED.append("animations/pw_polar_bear_neck.animation.json")
    pe = dst / "entity/polar_bear.entity.json"; e = R.jl(pe); desc = e["minecraft:client_entity"]["description"]
    assert "pw_neck" not in desc["animations"]
    desc["animations"]["pw_neck"] = PB_NECK_ANIM; desc["scripts"]["animate"].append("pw_neck")
    R.wj(pe, e); CHANGED.append("entity/polar_bear.entity.json")
    top_old = max(max(q[1] for q in pts) for _, _, pts, *_ in world_boxes(old)); top_new = max(max(q[1] for q in pts) for _, _, pts, *_ in world_boxes(g["bones"]))
    return f"polar bear: Patrix cubes on the April bones (body / neck / legs swapped round / head pivot {PB_HEAD_PIVOT}); top y {top_old:.1f} -> {top_new:.1f}; neck follow animation"


JOBS = [("allay", "allay", "default", "allay", "default")]
PRE = [allay_check_port, polar_bear]
POST = [allay_hand, allay_locators]

CFG = {
    "src": ROOT / "_build/rp07-1426", "dst": ROOT / "_build/rp07-1427", "version": "1.4.27",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.27",
    "desc": ("v1.4.27 (2026-09-30) R14 fixes: the allay's arms hang from its body (they floated while dancing and flying); "
             "the polar bear on Patrix's own model - lower body, its neck back, the legs the right way round. Includes all of 1.4.26."),
    "pre": PRE, "jobs": JOBS, "look": {}, "frame_exempt": {"allay": B7.FRAME_EXEMPT["allay"]},
    "unbound_ok": {"allay": B7.UNBOUND_OK["allay"]}, "placement": {"allay": B7.PLACEMENT["allay"]},
    "post": POST, "png_checked_elsewhere": [], "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-07", "ars_stack": [ROOT / "_build/rp06-1421"], "verify_hooks": [],
    "report": ROOT / "_docs/convb/build_rp07_1427_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp07_1427_files.json", "w"), indent=1)
