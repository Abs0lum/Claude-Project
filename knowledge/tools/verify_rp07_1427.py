#!/usr/bin/env python3
"""verify_rp07_1427.py — the gate for tools/build_rp07_1427.py (R14 fix round, RP-07).
convb_round.verify: diff A/J/K + per-job B/C/D/E/F/G/L (allay) + standing gates; plus:
  N2   the allay port == the JEM with Java AllayModel seeds (unchanged by the nesting)
  JT1  allay right_arm / left_arm are children of body;  JT2 shoulder -> body <= 0.6 px idle / dancing / flying / holding
  HPT  allay rightItem + lead locator identical to 1.4.26
  PB1  polar bear cubes == the Patrix polar_bear.jem bake (world boxes + face UVs): body 2, neck 1, head 3, snout 1, legs 4
       (April leg0/leg1 = the FRONT legs = Patrix leg3/leg4; leg2/leg3 = the hind = Patrix leg1/leg2)
  PB2  every bone the polar bear's animations drive exists (walk / idle / ambient / look / neck)
  PB3  top y 19 (was 23); every leg sinks >= 3 px into the body; the largest body bob of its animations (0.44 px) < that
  PB4  polar bear entity: only animations.pw_neck + animate "pw_neck" added
  PB5  animation.pw_polar_bear.neck: neck rotation = (pitch / 4.5, yaw / 3, 0) (FreshLX: neck.rx = (head.rx / 1.5) / 3, neck.ry = head.ry / 3)
Static checks only rule OUT (P1); his in-game witness rules IN."""
import itertools, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import build_rp07_1427 as B
import build_rp07_1426 as B7
import jem_anim_port as P
import molang_eval as ME
import arm_tree_gap as AG
import fa_preview as FP
from verify_rp07_1415_rp06_1410 import world_boxes

ROOT = Path("/home/claude")
OLD, NEW = B.CFG["src"], B.CFG["dst"]


def hooks(cfg, check):
    # ---------------------------------------------------------------- N2
    init, pre, anim, _ = B7.al_port()
    cs = []
    for a, l, s, y, p, (h, d) in itertools.product((0.0, 41.0, 333.0), (0.0, 2.3), (0.0, 0.2, 0.6), (0.0, 35.0), (0.0, -20.0), ((0, 0), (1, 0), (0, 1))):
        cs.append({"age": a, "limb_swing": l, "limb_speed": s, "head_yaw": y, "head_pitch": p, "_hold": h, "_dance": d})
    w = P.numeric_check("allay", B7.AL["prefix"], init, pre, anim, cs, seed_fn=B7.al_java, env_fn=B7.al_env)
    check(f"N2 allay Molang == JEM with Java AllayModel seeds ({len(cs)} cases)", w["rotation"] < 1e-3 and w["position"] < 1e-4 and w["scale"] < 1e-6, str(w))
    # ---------------------------------------------------------------- JT
    _, g = R.geo_file(NEW, "geometry.pw_allay"); by = {b["name"]: b for b in g["bones"]}
    check("JT1 allay arms are children of body (Java AllayModel tree)", all(by[a].get("parent") == "body" for a in ("right_arm", "left_arm")),
          str({a: (by[a].get("parent"), by[a]["pivot"]) for a in ("right_arm", "left_arm")}))
    rows = {}
    for st, env in {"idle": {}, "dancing": {"q.is_dancing": 1.0}, "flying": {"q.modified_move_speed": 0.5}, "holding": {"v.is_holding_right": 1.0}}.items():
        wst = AG.sim(NEW, "allay", "geometry.pw_allay", env, False); rows[st] = round(max(v[0] for v in wst.values()), 2)
    check("JT2 allay shoulder -> body <= 0.6 px (1.4.26: dancing 4.08, flying 3.59)", max(rows.values()) <= 0.6, str(rows))
    _, go = R.geo_file(OLD, "geometry.pw_allay"); bo = {b["name"]: b for b in go["bones"]}
    check("HPT allay rightItem + body lead locator identical to 1.4.26", by["rightItem"] == bo["rightItem"] and by["body"].get("locators") == bo["body"].get("locators"),
          str(by["rightItem"]))
    # ---------------------------------------------------------------- PB1
    bake = FP.bake_any("polar_bear", "26.2")[0]; pby = {b["name"]: b for b in bake}
    wb = {}
    for n, i, pts, *_ in world_boxes(bake): wb.setdefault(n, []).append(pts)
    _, gp = R.geo_file(NEW, "geometry.pw_polar_bear"); pb = {b["name"]: b for b in gp["bones"]}
    pairs = [("body_cube", "bone2"), ("neck", "neck"), ("head2", "head")] + [(o, p) for o, p in B.PB_LEGS.items()]
    bad = []
    for ours, pat in pairs:
        want = [B.world_cube(pts, c) for pts, c in zip(wb[pat], pby[pat]["cubes"])]
        if json.dumps(pb[ours]["cubes"], sort_keys=True) != json.dumps(want, sort_keys=True): bad.append(ours)
    snout_ok = pb["bone"]["cubes"] == pby["bone"]["cubes"] and pb["bone"]["pivot"] == pby["bone"]["pivot"] and pb["bone"]["rotation"] == pby["bone"]["rotation"]
    check("PB1 polar bear cubes == the Patrix JEM bake (body 2, neck, head 3, snout, 4 legs the right way round)", not bad and snout_ok, f"differs {bad}, snout {snout_ok}")
    # ---------------------------------------------------------------- PB2
    ent = R.jl(NEW / "entity/polar_bear.entity.json")["minecraft:client_entity"]["description"]
    lib = {}
    for f in (NEW / "animations").glob("*.json"): lib.update(R.jl(f).get("animations", {}))
    lib.update({k: v for k, v in R.jl(R.VAN_RP / "animations/look_at_target.animation.json").get("animations", {}).items()} if (R.VAN_RP / "animations/look_at_target.animation.json").exists() else {})
    driven = set()
    for short, aid in ent["animations"].items():
        a = lib.get(aid)
        if a: driven |= set(a.get("bones", {}))
    missing = sorted(b for b in driven if b not in pb)
    check("PB2 every bone the polar bear's animations drive exists in the new geometry", not missing, f"driven {sorted(driven)}; missing {missing}")
    # ---------------------------------------------------------------- PB3
    boxes = {}
    for n, i, pts, *_ in world_boxes(gp["bones"]): boxes.setdefault(n, []).append(np.array(pts))
    top = max(b[:, 1].max() for v in boxes.values() for b in v)
    body_bottom = min(b[:, 1].min() for b in boxes["body_cube"])
    sink = {l: round(float(boxes[l][0][:, 1].max() - body_bottom), 2) for l in ("leg0", "leg1", "leg2", "leg3")}
    check("PB3 polar bear top y 19 (April 23); legs sink >= 3 px into the body; body bob of its animations <= 0.44 px < that",
          abs(top - 19.0) < 1e-6 and min(sink.values()) >= 3.0, f"top {top}, sink {sink}")
    # ---------------------------------------------------------------- PB4
    old = R.jl(OLD / "entity/polar_bear.entity.json")["minecraft:client_entity"]["description"]
    exp = json.loads(json.dumps(old)); exp["animations"]["pw_neck"] = B.PB_NECK_ANIM; exp["scripts"]["animate"].append("pw_neck")
    check("PB4 polar bear entity: only the neck animation added", ent == exp, "")
    # ---------------------------------------------------------------- PB5
    a = lib[B.PB_NECK_ANIM]["bones"]["neck"]["rotation"]
    env = {"q.target_x_rotation": -18.0, "q.target_y_rotation": 30.0}
    got = [ME.run(x, dict(env)) if isinstance(x, str) else float(x) for x in a]
    check("PB5 neck follow = (pitch / 4.5, yaw / 3, 0) (FreshLX's neck.rx = head.rx/1.5/3, neck.ry = head.ry/3)",
          np.allclose(got, [-4.0, 10.0, 0.0]), str(got))


B.CFG["verify_hooks"] = [hooks]
B.CFG["prec_order"] = [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                       ("RP-07", NEW), ("RP-06", ROOT / "_build/rp06-1421")]

if __name__ == "__main__":
    files = json.load(open(ROOT / "_docs/convb/build_rp07_1427_files.json"))
    B.CFG["extra_changed"], B.CFG["extra_added"], B.CFG["extra_removed"] = files["changed"], files["added"], files["removed"]
    sys.exit(R.verify(B.CFG))
