#!/usr/bin/env python3
"""spider_walk.py — D-C278 (his R4 n08 "the legs don't seem to leave the ground during walking animation").
Port of the Patrix spider WALK (spider.jem) to Molang: for each leg Q the walk terms (those with var.ls) of
leg_Q_2.ry and leg_Q_b/c/d.rz. var.ls = limb_swing / 1.3 * (1 - var.scale*2), var.scale = -0.4*random(id) -> median factor 1.4;
Bedrock limb_swing == query.modified_distance_moved and limb_speed == query.modified_move_speed (Mojang's own translation:
vanilla quadruped walk cos(modified_distance_moved * 38.17 deg) * 80 deg * modified_move_speed == Java cos(limbSwing*0.6662)*1.4*amount).
Rotation units: degrees = deg(JEM radians), same sign on every axis (jem2molang.py).
API: walk_animation() -> animation dict  ·  eval_add_rot(phase, speed) -> {bone: [rx, ry, rz]} (numeric check)"""
import json, math, sys
sys.path.insert(0, "/home/claude/tools")
from jem2molang import walk_terms, to_molang
from cem_eval import CemContext, evaluate

JEM = "/home/claude/_intake/patrix-mobs/assets/minecraft/optifine/cem/spider.jem"
LEGS = ("LF", "LFm", "LBm", "LB", "RF", "RFm", "RBm", "RB")
TARGETS = (("2", "ry"), ("b", "rz"), ("c", "rz"), ("d", "rz"))
LS_FACTOR = 1.4 / 1.3
VARMAP = {"var.ls": "v.pw_ls", "limb_speed": "q.modified_move_speed", "is_on_ground": "q.is_on_ground"}


def exprs():
    j = json.load(open(JEM)); out = {}
    for m in j["models"]:
        for a in m.get("animations", []) or []:
            for k, v in a.items(): out[k] = v
    return out


def walk_animation():
    E = exprs(); bones = {}
    for q in LEGS:
        for seg, ax in TARGETS:
            key = f"leg_{q}_{seg}.{ax}"; w = walk_terms(E[key])
            if w == "0": continue
            mol = f"({to_molang(w, VARMAP)}) * 57.2957795"
            rot = bones.setdefault(f"leg_{q}_{seg}", {"rotation": [0.0, 0.0, 0.0]})["rotation"]
            rot[{"rx": 0, "ry": 1, "rz": 2}[ax]] = mol
    return {"loop": True, "bones": bones}


def eval_add_rot(phase, speed, on_ground=True):
    E = exprs(); out = {}
    ctx = CemContext({"limb_speed": speed, "is_on_ground": on_ground})
    ctx.vars["var.ls"] = phase
    for q in LEGS:
        for seg, ax in TARGETS:
            w = walk_terms(E[f"leg_{q}_{seg}.{ax}"])
            val = 0.0 if w == "0" else evaluate(w, ctx)
            r = out.setdefault(f"leg_{q}_{seg}", [0.0, 0.0, 0.0]); r[{"rx": 0, "ry": 1, "rz": 2}[ax]] = math.degrees(val)
    return out


if __name__ == "__main__":
    a = walk_animation()
    print(json.dumps(a, indent=1)[:1500])
