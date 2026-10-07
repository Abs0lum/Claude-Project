#!/usr/bin/env python3
"""build_rp06_1416.py — D-C285 (R8 witness round: his first load of the 1.4.22 stack, p4 re-run, p5; Round 11 GO 16:1x CT 09-29).
RP-06 Hostile Mobs RP v1.4.16 from v1.4.15.

  1. SILVERFISH VISIBLE (p4 a17 / p5 b04 "invisible, but I can see his shadow"). 1.4.15 kept the vanilla render controller
     `controller.render.silverfish`: part_visibility [{"*": "0"}, bodypart_0..6: 1, bodylayer_0..2: 1] = hide everything except
     the vanilla bone names. pw_silverfish has 34 bones (17 with cubes), none of those names -> 0 visible, shadow only.
     (1.4.15's note "those visibility entries simply do nothing" was wrong: the "*" default did everything.)
     Fix: our own controller.render.pw_silverfish (no part_visibility) + material entity_alphatest (the Patrix skin is a cut-out;
     the vanilla "silverfish" material is not ours to rely on).
  2. SKELETON / WITHER SKELETON BOW GRIP (p5 b09 "patrix bow, but not quite set in the skeleton's hand correctly"). The vanilla bow
     attachable (attachables/bow.json, geometry.bow_standby: texture mesh on bone `rightitem`, wield offset [0.5, -2.5, 1]) hangs on
     the holder's rightItem bone. Vanilla geometry.skeleton.v1.8: rightItem pivot [-6, 15, 1] on a 12-px arm (y 12..24) = 3 px up
     from the fingertips, on the arm's outer face, 1 px forward. pw_skeleton / wither_skeleton.patrix: rightitem [-5, 12, 0] = the
     forearm's fingertip end, arm centre -> the grip sat 3 px low, 1 px in, 1 px back. Fix: rightitem -> [-6, 15, 1], leftitem ->
     [6, 15, 1] (vanilla leftItem); nothing else in either geometry changes.
  Not in this build: the stray / zombie / husk / drowned / piglin / witch / evoker / bogged models have NO rightItem bone — the
  p6 HELD ITEMS step asks what he sees before anything changes. Guardian "shivered in place" near full extension: his 16:15
  "done well enough" -> backlog (LOW).
verify: python3 tools/verify_rp06_1416.py  (the standard convb_round gate + the lines below)"""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []
VANILLA_SF_RC = "controller.render.silverfish"
SF_RC = "controller.render.pw_silverfish"
SF_RC_DOC = {"format_version": "1.8.0", "render_controllers": {SF_RC: {
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"]}}}
HOLD = {"rightitem": [-6, 15, 1], "leftitem": [6, 15, 1]}          # vanilla geometry.skeleton.v1.8 rightItem / leftItem
HOLD_GEOS = ("geometry.pw_skeleton", "geometry.wither_skeleton.patrix")


def silverfish_rc(dst):
    pe = dst / "entity/silverfish.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    assert desc["render_controllers"] == [VANILLA_SF_RC], desc["render_controllers"]
    assert desc["geometry"] == {"default": "geometry.pw_silverfish"}, desc["geometry"]
    desc["render_controllers"] = [SF_RC]
    desc["materials"] = {"default": "entity_alphatest"}
    R.wj(pe, d); CHANGED.append("entity/silverfish.entity.json")
    pr = dst / "render_controllers/pw_silverfish.render.json"; assert not pr.exists()
    R.wj(pr, SF_RC_DOC); ADDED.append("render_controllers/pw_silverfish.render.json")
    return f"silverfish -> {SF_RC} (no part_visibility), material entity_alphatest"


def hold_points(dst):
    out = []
    for gid in HOLD_GEOS:
        p, g = R.geo_file(dst, gid); by = {b["name"]: b for b in g["bones"]}
        for n, piv in HOLD.items():
            b = by[n]
            assert b["pivot"] == ([-5, 12, 0] if n == "rightitem" else [5, 12, 0]) and not b.get("cubes") and not b.get("rotation"), (gid, n, b)
            par = by[b["parent"]]; c = par["cubes"][0]
            assert c["origin"][1] == 12 and c["size"][1] == 6, (gid, par["name"], c)        # the forearm ends at y 12 (hand tip)
            b["pivot"] = list(piv)
        d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d); CHANGED.append(p.relative_to(dst).as_posix())
        out.append(f"{gid}: rightitem {HOLD['rightitem']}, leftitem {HOLD['leftitem']}")
    return "; ".join(out)


def verify_extra(cfg, check):
    OLD, NEW = cfg["src"], cfg["dst"]
    import rc_visibility_lint as RV
    ent = R.jl(NEW / "entity/silverfish.entity.json")["minecraft:client_entity"]["description"]
    rc = R.jl(NEW / "render_controllers/pw_silverfish.render.json")["render_controllers"][SF_RC]
    _, g = R.geo_file(NEW, "geometry.pw_silverfish")
    cube_bones = [b["name"] for b in g["bones"] if b.get("cubes")]
    vis = [b for b in cube_bones if RV.visible_state(rc.get("part_visibility"), b) != 0]
    old_rc = RV.rc_table([OLD])[VANILLA_SF_RC]
    vis_old = [b for b in cube_bones if RV.visible_state(old_rc.get("part_visibility"), b) != 0]
    check("SF1 silverfish: own render controller, every cube-bearing bone visible (was 0 under the vanilla RC)",
          ent["render_controllers"] == [SF_RC] and "part_visibility" not in rc and len(vis) == len(cube_bones) == 17 and not vis_old,
          f"{len(vis)}/{len(cube_bones)} visible now; under {VANILLA_SF_RC}: {len(vis_old)}")
    ent_o = R.jl(OLD / "entity/silverfish.entity.json")["minecraft:client_entity"]["description"]
    a, b = copy.deepcopy(ent_o), copy.deepcopy(ent)
    for x in (a, b): x.pop("render_controllers"); x.pop("materials")
    check("SF2 silverfish entity: only render_controllers + materials changed (animation port, geometry, texture untouched)",
          a == b and ent["materials"] == {"default": "entity_alphatest"}, f"materials {ent['materials']}")
    for gid in HOLD_GEOS:
        _, go = R.geo_file(OLD, gid); _, gn = R.geo_file(NEW, gid)
        bo = {x["name"]: x for x in go["bones"]}; bn = {x["name"]: x for x in gn["bones"]}
        others = all(bo[k] == bn[k] for k in bo if k not in HOLD) and set(bo) == set(bn) and go["description"] == gn["description"]
        piv = {k: bn[k]["pivot"] for k in HOLD}
        check(f"SK1 {gid}: hold points at vanilla's (right [-6,15,1], left [6,15,1]); every other bone byte-equal",
              others and piv == HOLD, f"{piv}")
    import rc_visibility_lint
    n, f = rc_visibility_lint.lint_pack(NEW, tuple(cfg.get("ars_stack", ())))
    check("RC0 calibration: the RCV gate finds the silverfish in 1.4.15 (the witnessed defect) and nothing else",
          [x[0] for x in rc_visibility_lint.lint_pack(OLD, tuple(cfg.get("ars_stack", ())))[1]] == ["entity/silverfish.entity.json"], "")


CFG = {
    "src": ROOT / "_build/rp06-1415", "dst": ROOT / "_build/rp06-1416", "version": "1.4.16",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.16",
    "desc": ("v1.4.16 (2026-09-29) R8 FIXES (D-C285): the silverfish is visible again (its own render controller - the vanilla one "
             "hid every part of the Patrix model); skeletons and wither skeletons hold their bow / sword where the game's own "
             "skeleton does (3 px higher, at the hand). Includes all of 1.4.15."),
    "pre": [], "jobs": [], "look": {}, "unbound_ok": {}, "placement": {},
    "post": [silverfish_rc, hold_points],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-06", "ars_stack": [ROOT / "_build/rp07-1422"],
    "prec_order": [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                   ("RP-07", ROOT / "_build/rp07-1422"), ("RP-06", ROOT / "_build/rp06-1416")],
    "verify_hooks": [verify_extra], "report": ROOT / "_docs/convb/build_rp06_1416_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp06_1416_files.json", "w"), indent=1)
