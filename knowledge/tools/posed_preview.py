#!/usr/bin/env python3
"""posed_preview.py — render a SHIPPED geometry posed by a SHIPPED animation at a given moment (D-C299, FA-1 previews).
The entity's pre_animation runs in molang_eval (queries from `env`), then each animated bone gets rotation += value (degrees,
Bedrock file sign) and position += value (px, file frame, applied to the bone's subtree in its PARENT's rest frame; D-C311). Preview only: the
rotation order / parent-frame position follow the Bedrock convention closely enough to show a pose; the gates are numeric."""
import copy, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import convb_build as CB
import molang_eval as ME
from equine_compare import bone_affines


def posed_bones(bones, anim_bones, env):
    bones = copy.deepcopy(bones); by = {b["name"]: b for b in bones}
    aff = bone_affines(bones)
    for name, ch in anim_bones.items():
        if name not in by: continue
        b = by[name]
        if "position" in ch:
            p = [ME.run(x, dict(env)) if isinstance(x, str) else float(x) for x in ch["position"]]
            par = b.get("parent"); A = aff[par][0] if par else np.eye(3)
            d = A @ np.array([p[0], p[1], p[2]])      # D-C311: Bedrock animation position is in the geometry FILE frame (x NOT
                                                      # mirrored; Mojang's elytra + Naturalist bird wings prove it) — was -p[0]
            CB._shift_subtree(bones, name, [float(v) for v in d])
        if "rotation" in ch:
            r = [ME.run(x, dict(env)) if isinstance(x, str) else float(x) for x in ch["rotation"]]
            b["rotation"] = [b.get("rotation", [0, 0, 0])[k] + r[k] for k in range(3)]
    return bones


def pose(dst, stem, gid, t, extra_env=None, anims_to_play=None):
    ent = R.jl(dst / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
    env = {"q.life_time": t, "q.delta_time": 0.05, "q.is_on_ground": 1.0, "q.is_alive": 1.0, **(extra_env or {})}
    for s in ent["scripts"].get("initialize", []): ME.run(s, env)
    for _ in range(3):
        for s in ent["scripts"].get("pre_animation", []): ME.run(s, env)
    lib = {}
    for f in (dst / "animations").glob("*.json"): lib.update(R.jl(f).get("animations", {}))
    _, g = R.geo_file(dst, gid); bones = g["bones"]
    for short in (anims_to_play or ent["scripts"].get("animate", [])):
        aid = ent["animations"].get(short if isinstance(short, str) else list(short)[0])
        a = lib.get(aid)
        if a: bones = posed_bones(bones, a.get("bones", {}), env)
    return bones, g["description"]["texture_width"], g["description"]["texture_height"]
