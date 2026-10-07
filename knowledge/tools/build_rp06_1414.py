#!/usr/bin/env python3
"""build_rp06_1414.py — D-C280 (his 09:59 first-load log). RP-06 Hostile Mobs RP v1.4.14 from v1.4.13:
  1. SPIDER walk back legs: 6 rotations (leg_LB_b/c/d, leg_RB_b/c/d .rz) failed to load in the game with
     "binary Add '+' operator at end of expression". The Patrix JEM writes `clamp(+cos(var.ls)/5*limb_speed, ...)`; jem2molang
     carried the unary `+` over, and Bedrock has no unary plus. jem2molang now drops it (`+x` == `x`, value unchanged), and the
     walk animation is regenerated. Nothing else in the pack changes.
  2. GATE: every Molang string in the pack is parsed with Bedrock's grammar (molang_lint.py — calibrated on his log: it reports
     exactly his 6 errors in 1.4.13 and 0 in RP-07 1.4.20 / TestRunner RP 0.3.0), and the regenerated walk is evaluated in
     Molang and compared with the JEM source at many phases/speeds (the 1.4.13 gate only evaluated the JEM side).
  manifest 1.4.14, uuid kept. verify: verify_rp06_1414.py."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_eval as ME
import molang_lint as ML
from spider_walk import walk_animation, eval_add_rot, LEGS

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []
ANIM = "animations/pw_spider.animation.json"
BAD6 = [f"leg_{q}_{s}" for q in ("LB", "RB") for s in ("b", "c", "d")]


def spider_walk_fix(dst):
    p = dst / ANIM; d = R.jl(p); old = d["animations"]["animation.pw_spider.walk"]
    new = walk_animation()
    assert set(new["bones"]) == set(old["bones"]), "walk bone set changed"
    diff = sorted(b for b in new["bones"] if new["bones"][b] != old["bones"][b])
    assert diff == sorted(BAD6), f"expected only the 6 failing bones to change, got {diff}"
    d["animations"]["animation.pw_spider.walk"] = new
    R.wj(p, d); CHANGED.append(ANIM)
    return f"walk regenerated; changed bones {diff} (unary + dropped)"


def verify_extra(cfg, check):
    NEW, OLD = cfg["dst"], cfg["src"]
    n, errs = ML.lint_pack(NEW)
    # n > 150: since D-C281 an entity's pre_animation / initialize list counts as ONE script (230 -> 181 strings, same content)
    check("ML1 every Molang string in the pack parses with Bedrock's grammar", not errs and n > 150,
          f"{n} strings, {len(errs)} errors {[(e[0], e[1]) for e in errs[:3]]}")
    n0, e0 = ML.lint_pack(OLD)
    check("ML2 lint calibration: 1.4.13 shows exactly the 6 errors of his 09:59 content log",
          sorted(e[1].split(".bones.")[1].split(".")[0] for e in e0) == sorted(BAD6) and all(e[0] == ANIM for e in e0),
          f"1.4.13: {len(e0)} errors on {sorted(e[1].split('.bones.')[1].split('.')[0] for e in e0 if '.bones.' in e[1])}")
    a_new = R.jl(NEW / ANIM)["animations"]; a_old = R.jl(OLD / ANIM)["animations"]
    same_other = all(a_new[k] == a_old[k] for k in a_old if k != "animation.pw_spider.walk") and set(a_new) == set(a_old)
    wb_new, wb_old = a_new["animation.pw_spider.walk"]["bones"], a_old["animation.pw_spider.walk"]["bones"]
    check("SP4 only the 6 failing rotations changed; base/walking/swimming/climbing and the other 26 walk bones identical",
          same_other and all(wb_new[b] == wb_old[b] for b in wb_old if b not in BAD6)
          and all(wb_new[b] != wb_old[b] for b in BAD6), f"other anims identical {same_other}")
    # SP3: the Molang the game will run == the Patrix JEM, numerically (every leg, every axis)
    worst = 0.0; cases = 0
    for ph in [k * math.pi / 8 for k in range(16)] + [0.37, 2.9, 5.5]:
        for sp in (0.0, 0.15, 0.6, 1.0):
            for og in (True, False):
                ref = eval_add_rot(ph, sp, on_ground=og)
                env = {"v.pw_ls": ph, "q.modified_move_speed": sp, "q.is_on_ground": 1.0 if og else 0.0}
                for b, ch in wb_new.items():
                    for ax, e in enumerate(ch["rotation"]):
                        got = ME.run(e, dict(env)) if isinstance(e, str) else float(e)
                        worst = max(worst, abs(got - ref[b][ax])); cases += 1
    check("SP3 Molang walk == JEM walk (molang_eval, degrees) at 19 phases x 4 speeds x ground/air", worst < 1e-6,
          f"{cases} values, max |Molang - JEM| = {worst:.2e} deg")
    # SP2 carried over: the feet still lift
    from equine_compare import bone_affines
    from bb_truth import truth_posed_faces
    _, g = R.geo_file(ROOT / "_build/rp07-1420", "geometry.spider")
    kids = {}
    for b in g["bones"]: kids.setdefault(b.get("parent"), []).append(b["name"])
    def sub(nm):
        out = [nm]
        for c in kids.get(nm, []): out += sub(c)
        return out
    dsub = {q: set(sub(f"leg_{q}_d")) for q in LEGS}
    def feet(add):
        F = truth_posed_faces(g["bones"], 64, 32, bone_affines(g["bones"], add_rot=add))
        return {q: min(p[1] for f in F if f.bone in dsub[q] for p in f.pts) for q in LEGS}
    rest = feet({}); lifts = []; back = 0
    for k in range(8):
        ft = feet(eval_add_rot(k * math.pi / 4, 0.6))
        lifts.append(sum(1 for q in LEGS if ft[q] - rest[q] > 1.0)); back += sum(1 for q in ("LB", "RB") if ft[q] - rest[q] > 1.0)
    check("SP2 feet lift while walking (back legs included)", min(lifts) >= 2 and back >= 4,
          f"legs lifted > 1 px at 8 phases: {lifts}; back-leg lifts over the cycle: {back}")


CFG = {
    "src": ROOT / "_build/rp06-1413", "dst": ROOT / "_build/rp06-1414", "version": "1.4.14",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.14",
    "desc": ("v1.4.14 (2026-09-29) SPIDER WALK FIX (D-C280): the back legs' walk rotations load again (1.4.13 content-log "
             "Molang errors 'binary Add + operator'); every Molang string in the pack now parsed before shipping. "
             "Includes all of 1.4.13 (guardian spikes, Patrix spider walk, ravager/pillager nose, top/bottom faces)."),
    "jobs": [], "look": {},
    "post": [spider_walk_fix],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "verify_hooks": [verify_extra], "unbound_ok": {}, "placement": {},
    "report": ROOT / "_docs/convb/build_rp06_1414_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp06_1414_files.json", "w"), indent=1)
