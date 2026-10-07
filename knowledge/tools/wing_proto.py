#!/usr/bin/env python3
"""wing_proto.py — scratch packs for the wing-contact fixes: copy a mob's entity / animation / geometry files into a scratch
pack, apply a fix, then measure (wing_contact) + render the worst moments next to the shipped build."""
import copy, json, os, shutil, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import wing_contact as W
import wing_hinge as WH

SCR = Path("/tmp/claude-0/wingproto")


def scratch(mob, tag):
    spec = W.SPECS[mob]; src = spec["pack"]; dst = SCR / f"{mob}-{tag}"
    if dst.exists(): shutil.rmtree(dst)
    (dst / "entity").mkdir(parents=True); (dst / "animations").mkdir(); (dst / "models/entity").mkdir(parents=True)
    shutil.copy(src / f"entity/{spec['stem']}.entity.json", dst / "entity")
    for f in (src / "animations").glob("*.json"): shutil.copy(f, dst / "animations")
    gp, _ = W.find_geo(src, spec["gid"]); shutil.copy(gp, dst / "models/entity" / gp.name)
    os.symlink(src / "textures", dst / "textures")
    s2 = dict(spec); s2["pack"] = dst
    return s2, gp.name


def edit(spec2, gfile, anim_id, fn):
    gp = spec2["pack"] / "models/entity" / gfile; gd = W.jl(gp); geo = gd["minecraft:geometry"][0]
    af = None
    for f in (spec2["pack"] / "animations").glob("*.json"):
        d = W.jl(f)
        if anim_id in d.get("animations", {}): af, ad = f, d
    bones, abones = fn(geo["bones"], ad["animations"][anim_id]["bones"])
    geo["bones"] = bones; ad["animations"][anim_id]["bones"] = abones
    gp.write_text(json.dumps(gd, indent=1)); af.write_text(json.dumps(ad, indent=1))
