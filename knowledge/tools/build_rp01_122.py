#!/usr/bin/env python3
"""build_rp01_122.py — RP-01 1.3.122 from the frozen 1.3.121 (never rebuilt): the FALLING TREE on physics (round 1004b,
D-C563 / D-C565; research R6-FALLING-TREE-PHYSICS-AND-ANIMATION-2026-10-04). Pairs with BP-02 1.3.220.
  1. animation.ft_falling_tree.fall — a Molang CURVE on the root's z rotation instead of the 5.05 s keyframe table:
       hold 0.15 s -> creak ramp 0 -> 2° (cosine, 0.45 s) -> theta(f) = 2 + 88·f^3.85, f = (t - 0.6) / T, T = ft:fall_t / 10
       (the script sets T = 1.10·sqrt(H)); past f = 1 the curve continues at its end slope (downhill rests > 90°); clamped at
       -ft:rest_angle (the resting angle from the tree's own cells). Mirrors pw_fall_physics.thetaAt exactly.
  2. animation.ft_falling_tree.rest — the rebound goes UP (rest_angle + 2.3 at 0.22 s, back at 0.43, + 0.3 at 0.55, rest at
       0.65). The old "rest_angle - 4.0" drove the trunk 4° deeper INTO the ground.
  3. controller.animation.ft_falling_tree.fall — leaves the fall state when the CURVE reaches the resting angle (client-side,
       no snap), on ft:fall_stopped (the collision pin), or by a time fallback.
  4. root bone pivots: every falling-tree geometry hinges on the trunk's LEADING FACE (file -x, the side the negative z
       rotation tips toward — L-ROT-DIR): legacy models at -(log_1 x half-width), the 544 carbon copies at -(root column
       width)/2 (ft_tpl_gen_lite regenerated from the BP-02 1.3.220 templates, same meshing arguments as 1.3.121).
Usage: build_rp01_122.py   (rp01-122 must not exist; BP = _build/bp02-220 with its final templates)"""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST, BP = B / "rp01-121", B / "rp01-122", B / "bp02-220"
ARGS = ["--maxb=8", "--clusters=12", "--runfrom=3", "--close=3"]          # exactly 1.3.121's meshing

HOLD, RAMP, LEAN0, P, END_SLOPE = 0.15, 0.45, 2.0, 3.85, 88 * 3.85
F_EXPR = "((q.anim_time - 0.6) / (q.property('ft:fall_t') * 0.1))"
CURVE = (f"({F_EXPR} <= 1.0 ? (2.0 + 88.0 * math.pow(math.max(0.0, {F_EXPR}), 3.85)) : (90.0 + {END_SLOPE:.1f} * ({F_EXPR} - 1.0)))")
THETA = (f"math.min(q.anim_time <= 0.15 ? 0.0 : (q.anim_time < 0.6 ? (1.0 - math.cos(400.0 * (q.anim_time - 0.15))) : {CURVE}), "
         f"-q.property('ft:rest_angle'))")
FALL_ROT_Z = f"-({THETA})"
REACHED_REST = f"({CURVE}) >= (-q.property('ft:rest_angle') - 0.01)"
TIME_FALLBACK = "q.anim_time > 0.6 + q.property('ft:fall_t') * 0.1 * 1.15 + 0.3"


def theta_py(t, T, rest):
    """the same curve in Python (mirrors pw_fall_physics.thetaAt) — used to check the Molang algebra below"""
    if t <= HOLD:
        th = 0.0
    elif t < HOLD + RAMP:
        th = LEAN0 * (1 - math.cos((t - HOLD) / RAMP * math.pi)) / 2
    else:
        f = max(0.0, (t - HOLD - RAMP) / T)
        th = LEAN0 + 88 * f ** P if f <= 1 else 90 + END_SLOPE * (f - 1)
    return min(th, rest)


def molang_py(t, T, rest):
    """the Molang expression's algebra evaluated in Python (math.cos in DEGREES as Molang does)"""
    f = (t - 0.6) / (T * 10 * 0.1)
    curve = (2.0 + 88.0 * max(0.0, f) ** 3.85) if f <= 1.0 else (90.0 + END_SLOPE * (f - 1.0))
    th = 0.0 if t <= 0.15 else ((1.0 - math.cos(math.radians(400.0 * (t - 0.15)))) if t < 0.6 else curve)
    return min(th, rest)


def check_algebra():
    worst = 0.0
    for T in (0.8, 2.7, 3.5, 4.9, 8.0):
        for rest in (40, 70, 85, 90, 96, 110, 135):
            t = 0.0
            while t <= 0.6 + T * 1.2:
                worst = max(worst, abs(theta_py(t, T, rest) - molang_py(t, T, rest)))
                t += 0.01
    if worst > 1e-9:
        raise SystemExit(f"Molang algebra differs from the physics curve by {worst}")
    print("Molang algebra == physics curve (max |diff| %.1e)" % worst)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    if not (BP / "structures/pw/trees").exists():
        raise SystemExit(f"{BP} has no templates")
    check_algebra()
    shutil.copytree(SRC, DST)
    # 1 + 2: animations
    ap = DST / "animations/falling_tree.animation.json"
    an = json.loads(ap.read_text())
    fall = an["animations"]["animation.ft_falling_tree.fall"]
    fall["loop"] = "hold_on_last_frame"
    fall["animation_length"] = 10.0
    fall["bones"]["root"] = {"rotation": [0, 0, FALL_ROT_Z], "position": [0, -16, 0]}
    rest = an["animations"]["animation.ft_falling_tree.rest"]
    rest["loop"] = "hold_on_last_frame"
    rest["animation_length"] = 0.65
    rest["bones"]["root"] = {"rotation": {"0.0": [0, 0, "q.property('ft:rest_angle')"],
                                          "0.22": [0, 0, "q.property('ft:rest_angle') + 2.3"],
                                          "0.43": [0, 0, "q.property('ft:rest_angle')"],
                                          "0.55": [0, 0, "q.property('ft:rest_angle') + 0.3"],
                                          "0.65": [0, 0, "q.property('ft:rest_angle')"]},
                             "position": [0, -16, 0]}
    ap.write_text(json.dumps(an, indent=1))
    # 3: controller
    cp = DST / "animation_controllers/falling_tree.json"
    ac = json.loads(cp.read_text())
    st = ac["animation_controllers"]["controller.animation.ft_falling_tree.fall"]["states"]
    st["falling"]["transitions"] = [{"rest": "q.property('ft:fall_stopped') == 1"}, {"rest": REACHED_REST}, {"rest": TIME_FALLBACK}]
    cp.write_text(json.dumps(ac, indent=1))
    # 4a: legacy geometries — root pivot at -(log_1 x half-width)
    n_legacy = 0
    for f in sorted((DST / "models/entity").glob("falling_tree_*.geo.json")):
        doc = json.loads(f.read_text())
        for g in doc["minecraft:geometry"]:
            bones = {b["name"]: b for b in g["bones"]}
            log1 = bones.get("log_1")
            hw = 8.0
            if log1 and log1.get("cubes"):
                hw = max(max(abs(c["origin"][0]), abs(c["origin"][0] + c["size"][0])) for c in log1["cubes"])
            bones["root"]["pivot"] = [-hw, 0, 0]
            n_legacy += 1
        f.write_text(json.dumps(doc, separators=(",", ":")))
    # 4b: the carbon copies, regenerated with the pivot law (generator patched 1004b) from the 1.3.220 templates
    r = subprocess.run([sys.executable, "/home/claude/tools/ft_tpl_gen_lite.py", str(DST), str(BP)] + ARGS, capture_output=True, text=True)
    print(r.stdout[-1200:], r.stderr[-1200:])
    if r.returncode != 0:
        raise SystemExit("lite generator failed")
    piv = {}
    for f in (DST / "models/entity/ft_tpl").glob("*.geo.json"):
        g = json.loads(f.read_text())["minecraft:geometry"][0]
        root = next(b for b in g["bones"] if b["name"] == "root")
        piv[root["pivot"][0]] = piv.get(root["pivot"][0], 0) + 1
    print("carbon-copy root pivots (x -> count):", dict(sorted(piv.items())), "legacy geometries:", n_legacy)
    if 0 in piv or any(x > 0 for x in piv):
        raise SystemExit("a carbon copy kept a centre / wrong-side pivot")
    # manifest
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = [1, 3, 122]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 122]
    m["header"]["name"] = "AbsolutRealism Tectonic RP v1.3.122"
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.121 (2026-10-03) "):
        raise SystemExit("description prefix")
    m["header"]["description"] = ("v1.3.122 (2026-10-04) FALLING TREES ON PHYSICS: the fall is a Molang curve timed by the tree's height "
                                  "(BP-02 1.3.220 sets ft:fall_t), hinged on the trunk's leading edge, stopping where the tree's own "
                                  "cells meet the real ground, with an upward rebound; birch copies regenerated. Includes all of " + desc)[:1000]
    mp.write_text(json.dumps(m, indent=1))
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
