#!/usr/bin/env python3
"""build_rp06_1417.py — D-C286 (R9 witness p6 c07 "only one creature (bog?) isn't holding an item" + the content-log error "binding
expression q.item_slot_to_bone_name(c.item_slot) returned a bone name that doesn't exist"; shots 163950 / 163952b; Round 12 GO).
RP-06 Hostile Mobs RP v1.4.17 from v1.4.16.

  BOGGED: bogged.patrix has no rightItem / leftItem bone, so the bow attachable's binding finds no bone and the bow is not drawn.
  STRAY: pw_stray (the same two-segment arm rig as pw_skeleton) has none either; its bow shows flat at the hip (163950/163952b —
  the look the skeleton had before 1.4.16).
  Fix (L-HOLD-POINT): vanilla-frame hold points — 3 px up from the hand end of the arm, on the arm's outer x face and its +z face,
  exactly where geometry.skeleton.v1.8 puts rightItem [-6, 15, 1] on its 12-px arm:
    pw_stray       rightitem [-6, 15, 1] under rightForearm · leftitem [6, 15, 1] under leftForearm   (== pw_skeleton 1.4.16)
    bogged.patrix  rightItem [-6, 14.4956, 0.0008] under rightArm · leftItem [6, 14.4956, 2.4992] under leftArm (its arm cubes)
  Zombie / husk / drowned / piglin / pillager visibly hold their items (his PASS) — unchanged.
verify: python3 tools/verify_rp06_1417.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []


def _hold(arm_bone):
    """vanilla-frame hold point for an arm bone whose own (or forearm's) single cube ends at the hand: x on the outer face,
    y 3 px above the cube's bottom, z on the cube's +z face."""
    c = arm_bone["cubes"][0]; o, s = c["origin"], c["size"]
    outer_x = o[0] if o[0] < 0 else o[0] + s[0]
    return [round(outer_x, 4), round(o[1] + 3.0, 4), round(o[2] + s[2], 4)]


PLAN = {"geometry.pw_stray": (("rightitem", "rightForearm"), ("leftitem", "leftForearm")),
        "geometry.bogged.patrix": (("rightItem", "rightArm"), ("leftItem", "leftArm"))}
EXPECT = {"geometry.pw_stray": {"rightitem": [-6, 15, 1], "leftitem": [6, 15, 1]},
          "geometry.bogged.patrix": {"rightItem": [-6.0, 14.4956, 0.0008], "leftItem": [6.0, 14.4956, 2.4992]}}


def hold_points(dst):
    out = []
    for gid, pairs in PLAN.items():
        p, g = R.geo_file(dst, gid); by = {b["name"]: b for b in g["bones"]}
        assert not any(n.lower() in ("rightitem", "leftitem") for n in by), (gid, [n for n in by if "item" in n.lower()])
        for name, parent in pairs:
            piv = _hold(by[parent])
            assert piv == EXPECT[gid][name], (gid, name, piv)
            g["bones"].append({"name": name, "parent": parent, "pivot": piv})
        d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d); CHANGED.append(p.relative_to(dst).as_posix())
        out.append(f"{gid}: " + ", ".join(f"{n} {EXPECT[gid][n]} under {pa}" for n, pa in pairs))
    return "; ".join(out)


def verify_extra(cfg, check):
    OLD, NEW = cfg["src"], cfg["dst"]
    for gid in PLAN:
        _, go = R.geo_file(OLD, gid); _, gn = R.geo_file(NEW, gid)
        bo = {b["name"]: b for b in go["bones"]}; bn = {b["name"]: b for b in gn["bones"]}
        added = sorted(set(bn) - set(bo))
        ok = (all(bo[k] == bn[k] for k in bo) and go["description"] == gn["description"] and added == sorted(EXPECT[gid])
              and all(bn[k]["pivot"] == EXPECT[gid][k] and not bn[k].get("cubes") and not bn[k].get("rotation") for k in added))
        check(f"HP1 {gid}: only the two hold points added (no cubes, no rotation), every other bone byte-equal", ok, f"added {added}")
    _, sk = R.geo_file(NEW, "geometry.pw_skeleton"); _, st = R.geo_file(NEW, "geometry.pw_stray")
    ps = {b["name"]: b.get("pivot") for b in sk["bones"] if "item" in b["name"]}; pt = {b["name"]: b.get("pivot") for b in st["bones"] if "item" in b["name"]}
    check("HP2 pw_stray's hold points == pw_skeleton's (the rig he passed in c06)", ps == pt, f"{pt}")


CFG = {
    "src": ROOT / "_build/rp06-1416", "dst": ROOT / "_build/rp06-1417", "version": "1.4.17",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.17",
    "desc": ("v1.4.17 (2026-09-29) R9 FIX (D-C286): the bogged holds its bow again and the stray holds its bow in the hand (both got "
             "the hand point the skeleton has). Includes all of 1.4.16: silverfish visible, skeleton + wither skeleton grip."),
    "pre": [], "jobs": [], "look": {}, "unbound_ok": {}, "placement": {},
    "post": [hold_points],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-06", "ars_stack": [ROOT / "_build/rp07-1424"],
    "prec_order": [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                   ("RP-07", ROOT / "_build/rp07-1424"), ("RP-06", ROOT / "_build/rp06-1417")],
    "verify_hooks": [verify_extra], "report": ROOT / "_docs/convb/build_rp06_1417_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp06_1417_files.json", "w"), indent=1)
