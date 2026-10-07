#!/usr/bin/env python3
"""build_r16a.py — R16a (D-C309 / D-C310, his GO + picks 01:20-02:30 CT 09-30). The quick half of the round:
  RP-06 v1.4.22 from 1.4.21:
    VEX      min_engine_version 1.8.0 -> 1.21.0 (the only held-item entity still pinned at Mojang's 1.8.0 = a tie with
             vanilla's vex; every mob that draws its item runs 1.21.0 or unpinned; RBW lint 0 findings so the strict Molang
             reading of 1.21.0 drops nothing) + Mojang's vex.idle item scale (rightItem / leftItem 0.7) as animation.pw_vex.hand
    PHANTOM  wing tips on a TRUE HINGE (his pick A): helper bone <tip>_hinge on the join line, the tip turns only about the
             edge it shares with the inner wing (the flap kept, the extra sideways tilt dropped) — the joint never opens
  RP-07 v1.4.28 from 1.4.27:
    ALLAY    Mojang's hold_item item-bone channels (rightItem scale 0.7 + the trident turn) as animation.pw_allay.hand
    PARROT   flight wing: the outer feather block seated on the inner block (Patrix's designed 0.9-1.3 px gap closed) + TRUE HINGE
Everything else byte-identical. Usage: build_r16a.py -> _build/rp06-1422, _build/rp07-1428 (+ _docs/r16/build_r16a.json)"""
import json, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import wing_contact as W
import wing_hinge as WH

ROOT = Path("/home/claude")
DATE = "2026-09-30"
VEX_HAND_ID = "animation.pw_vex.hand"
VEX_HAND = {"format_version": "1.8.0", "animations": {VEX_HAND_ID: {"loop": True, "bones": {
    "rightItem": {"scale": 0.7}, "leftItem": {"scale": 0.7}}}}}                                 # Mojang animation.vex.idle
AL_HAND_ID = "animation.pw_allay.hand"
AL_HAND = {"format_version": "1.8.0", "animations": {AL_HAND_ID: {"loop": True, "bones": {
    "rightItem": {"scale": 0.7, "rotation": ["-15.0 * (variable.holding_trident)", 0, "90.0 * (variable.holding_trident)"],
                  "position": [0.0, "3.50 * (variable.holding_trident)", 0.0]}}}}}             # Mojang animation.allay.hold_item
REPORT = {}


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD r16a: {m}\n")


def copy(src, dst):
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=False)


def manifest(dst, ver, name, desc):
    mp = dst / "manifest.json"; m = json.loads(mp.read_text(encoding="utf-8-sig"))
    v = [int(x) for x in ver.split(".")]
    m["header"]["version"] = v; m["header"]["name"] = name; m["header"]["description"] = desc
    for mod in m["modules"]: mod["version"] = v
    mp.write_text(json.dumps(m, indent=1), encoding="utf-8")


def anim_file(dst, anim_id):
    for f in sorted((dst / "animations").glob("*.json")):
        d = R.jl(f)
        if anim_id in (d.get("animations") or {}): return f, d
    raise FileNotFoundError(anim_id)


def hinge(dst, stem, gid, anim_id, pairs, close_gap):
    gp, g = R.geo_file(dst, gid); gd = R.jl(gp)
    af, ad = anim_file(dst, anim_id)
    spec = dict(W.SPECS[stem], pack=dst)
    bones, ab = g["bones"], ad["animations"][anim_id]["bones"]
    reps = []
    for a, b in pairs:
        bones, ab, rep = WH.hinge_fix(bones, ab, a, b, spec, close_gap=close_gap); reps.append(rep)
    gd["minecraft:geometry"][0]["bones"] = bones; ad["animations"][anim_id]["bones"] = ab
    R.wj(gp, gd); R.wj(af, ad)
    REPORT[stem] = {"geometry_file": str(gp.relative_to(dst)), "animation_file": str(af.relative_to(dst)), "hinges": reps}
    log(f"{stem}: true hinge on {[p[1] for p in pairs]} ({reps})")


def add_hand(dst, stem, anim_short, anim_id, doc, fname, mev=None):
    R.wj(dst / f"animations/{fname}", doc)
    pe = dst / f"entity/{stem}.entity.json"; e = R.jl(pe); desc = e["minecraft:client_entity"]["description"]
    assert anim_short not in desc["animations"], (stem, anim_short)
    desc["animations"][anim_short] = anim_id; desc["scripts"]["animate"].append(anim_short)
    if mev:
        REPORT.setdefault(stem, {})["min_engine_version"] = [desc.get("min_engine_version"), mev]
        desc["min_engine_version"] = mev
    R.wj(pe, e)
    log(f"{stem}: {anim_id} (item bones 0.7){' + min_engine_version ' + mev if mev else ''}")


def rp06():
    src, dst = ROOT / "_build/rp06-1421", ROOT / "_build/rp06-1422"
    copy(src, dst)
    add_hand(dst, "vex", "pw_hand", VEX_HAND_ID, VEX_HAND, "pw_vex_hand.animation.json", mev="1.21.0")
    hinge(dst, "phantom", "geometry.pw_phantom", "animation.pw_phantom.jem",
          (("left_wing2", "left_wing_tip2"), ("right_wing2", "right_wing_tip2")), close_gap=False)
    manifest(dst, "1.4.22", "AbsolutRealism Hostile Mobs RP v1.4.22",
             f"v1.4.22 ({DATE}) R16a: the vex on engine version 1.21.0 (it was the only item-holding mob still on Mojang's 1.8.0) "
             "+ Mojang's 70 % held-item size; the phantom's wing tips on a true hinge (the joint no longer opens). Includes all of 1.4.21.")


def rp07():
    src, dst = ROOT / "_build/rp07-1427", ROOT / "_build/rp07-1428"
    copy(src, dst)
    add_hand(dst, "allay", "pw_hand", AL_HAND_ID, AL_HAND, "pw_allay_hand.animation.json")
    hinge(dst, "parrot", "geometry.pw_parrot", "animation.pw_parrot.jem",
          (("left_wing_fly", "left_wing_fly2"), ("right_wing_fly", "right_wing_fly2")), close_gap=True)
    manifest(dst, "1.4.28", "AbsolutRealism Neutral Mobs RP v1.4.28",
             f"v1.4.28 ({DATE}) R16a: the allay holds items at Mojang's 70 % size (the sword was bigger than the allay); the parrot's "
             "flight wing on a true hinge with its outer feathers seated on the inner wing (the joint no longer opens). Includes all of 1.4.27.")


if __name__ == "__main__":
    rp06(); rp07()
    p = ROOT / "_docs/r16/build_r16a.json"; p.parent.mkdir(parents=True, exist_ok=True)
    json.dump(REPORT, open(p, "w"), indent=1); log(f"report {p}")
