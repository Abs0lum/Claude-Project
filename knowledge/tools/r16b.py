#!/usr/bin/env python3
"""r16b.py — R16b (D-C314): the Patrix fidelity ports (fox, goat, cat, ocelot, cod, iron golem, hoglin, zoglin) — FA-1 method.

Per mob: the Java values the JEM reads before it writes them (SEEDS, as Molang at the top of pre_animation; the same values as
Python for the gate), the render parameters Bedrock has under other names (PX), the vanilla parts whose Java pose moves Patrix
geometry although the JEM never assigns them (EXTRA_DRIVEN), and the pivot rule per top-level part (PART_PIVOT: every part whose
t* the JEM assigns sits at its RUNTIME pivot, so Bedrock runtime = rest + (value - rest) = OptiFine's value exactly).

Gates this module provides (used by verify_r16b.py):
  N2  Molang (molang_eval) == JEM (cem_eval) on every driven channel, per state case          (jem_anim_port.numeric_check)
  N3  WORLD GEOMETRY: the rest bake posed by the port's animation (Bedrock transform: parent . T(pos) . T(pivot) . R . S . T(-pivot))
      == the JEM baked AT that pose (single sample, the same seeds) — every cube corner, per state case
Knowledge sources: research sheet _docs/r16b/R16B-RESEARCH.md (Java model constants, Mojang's own Bedrock queries)."""
import copy, math, re, sys
from contextlib import contextmanager
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb
import jem_anim_port as P
import molang_eval as ME
from jem_convert import load_json

D2R = 0.0174532925
PI = math.pi


def tri(x, p):
    """Java Mth.triangleWave(x, p) (x >= 0)"""
    return (abs(math.fmod(x, p) - p * 0.5) - p * 0.25) / (p * 0.25)


def mtri(x, p):
    return f"((math.abs(math.mod({x}, {p:.1f}) - {p * 0.5:.2f}) - {p * 0.25:.3f}) / {p * 0.25:.3f})"


# ----------------------------------------------------------------------------------------------------------------- per-mob tables
POS = {"pos_x": "q.position(0)", "pos_y": "q.position(1)", "pos_z": "q.position(2)"}
COMMON = {"frame_time": "q.delta_time", "frame_counter": "q.life_time", "is_child": "0.0", "is_riding": "q.is_riding", **POS}

# --- FOX (FoxModel.setupAnim; Mojang's fox controller: q.is_stalking / q.is_sleeping / q.is_sitting)
_ST, _SL = "q.is_stalking", "(!q.is_stalking && q.is_sleeping)"
_SI = "(!q.is_stalking && !q.is_sleeping && q.is_sitting)"
# D-C318 sit settle (0.25 s): see blend_if below
SIT_RAMP = ("q.is_sitting ? math.min(1.0, (v.pw_fx_sit_amt ?? 0.0) + q.delta_time * 4.0) "
            ": math.max(0.0, (v.pw_fx_sit_amt ?? 0.0) - q.delta_time * 4.0)")
_SW = "((!q.is_stalking && !q.is_sleeping) ? v.pw_fx_sit_amt : 0.0)"      # sitting weight for the Java seeds
FOX_SEEDS = {
    "sit": {"amt": SIT_RAMP},
    # D-C315: FoxRenderer pitches the whole fox by its xRot while POUNCING (and while faceplanted in snow). Bedrock has no pounce
    # query: Mojang's own fox controller enters 'pounce' from wiggle (q.is_interested) when it leaves the ground -> the same latch
    "pounce": {"on": "(!q.is_on_ground) ? ((((v.pw_fx_pounce_on ?? 0.0) > 0.0) || q.is_interested || q.is_stalking) ? 1.0 : 0.0) : 0.0"},
    "crouch": {"amt": "q.is_stalking ? math.min(3.0, (v.pw_fx_crouch_amt ?? 0.0) + q.delta_time * 4.0) : 0.0"},   # +0.2 / tick, max 3
    "body": {"rx": f"q.is_stalking ? 1.67551608 : (1.5707963 + (0.52359878 - 1.5707963) * {_SW})",   # NOT above pi/2: the JEM tests body.rx > pi/2 (pounce)
             "ry": "q.is_stalking ? math.cos(q.life_time * 20.0 * 57.2957795) * 0.01 : 0.0",
             "rz": f"{_SL} ? -1.57079633 : 0.0",
             "tx": "0.0",
             "ty": f"16.0 + (q.is_stalking ? v.pw_fx_crouch_amt : ({_SL} ? 5.0 : -7.0 * {_SW}))",
             "tz": f"-6.0 + 3.0 * {_SW}"},
    **{f"leg{i}": {"visible": f"{_SL} ? 0.0 : 1.0"} for i in (1, 2, 3, 4)},
}


# the pitch itself: Mojang's approximation of the leap angle (its 'pounce' animation: vertical speed * -7 deg), Mojang's 60 deg for
# 'stuck' (faceplanted); about the entity origin as Java's renderer does (whole model)
FOX_RENDER = [("pw_render", [0.0, 0.0, 0.0], {"rotation": ["q.is_stunned ? 60.0 : ((v.pw_fx_pounce_on ?? 0.0) * q.vertical_speed * -7.0)", 0.0, 0.0]})]


# D-C318 (his R17 answer 3 "add short settle"): Java + FreshLX switch the sit pose instantly; ours settles over 0.25 s. Every JEM
# `if(... is_sitting, X, REST)` branch becomes (X)*sit_amt + (REST)*(1-sit_amt), sit_amt ramping 0 <-> 1 at 4 / s; the Java
# seeds do the same. At sit_amt 0 or 1 the pose is FreshLX's exactly (N2 / N3 unchanged); in between it is a straight blend.


def _split_args(s, i):
    """s[i] == '(' -> (args, index of the matching ')')"""
    depth, cur, args = 0, "", []
    for j in range(i, len(s)):
        ch = s[j]
        if ch == "(":
            depth += 1
            if depth == 1: continue
        elif ch == ")":
            depth -= 1
            if depth == 0: args.append(cur); return args, j
        elif ch == "," and depth == 1: args.append(cur); cur = ""; continue
        cur += ch
    raise ValueError("unbalanced: " + s)


def blend_if(expr, cond="is_sitting", w="sit_amt"):
    """rewrite every JEM if() branch whose condition is exactly `cond` into a weighted blend (recursive, multi-branch aware)"""
    out, i = "", 0
    while True:
        m = re.search(r"\bif\s*\(", expr[i:])
        if not m: return out + expr[i:]
        a = i + m.start(); o = i + m.end() - 1
        args, e = _split_args(expr, o)
        args = [blend_if(x, cond, w) for x in args]
        def chain(k):
            if k == len(args) - 1: return args[k]
            c, v = args[k].strip(), args[k + 1]
            rest = chain(k + 2)
            if c == cond: return f"(({v})*{w} + ({rest})*(1-{w}))"
            return f"if({args[k]},{v},{rest})"
        out += expr[i:a] + chain(0); i = e + 1


def fox_java(c):
    st, sl, si = c.get("_st", 0), c.get("_sl", 0) and not c.get("_st", 0), c.get("_si", 0) and not c.get("_st", 0) and not c.get("_sl", 0)
    age = c.get("age", 0.0)
    body = {"rx": 1.67551608 if st else (0.52359878 if si else PI / 2), "ry": math.cos(age) * 0.01 if st else 0.0,
            "rz": -PI / 2 if sl else 0.0, "tx": 0.0, "ty": 16.0 + (3.0 if st else 5.0 if sl else -7.0 if si else 0.0), "tz": -6.0 + (3.0 if si else 0.0)}
    return {"body": body, **{f"leg{i}": {"visible": not sl} for i in (1, 2, 3, 4)}}


def fox_env(c):
    return {"q.is_stalking": float(c.get("_st", 0)), "q.is_sleeping": float(c.get("_sl", 0)), "q.is_sitting": float(bool(c.get("is_sitting"))),
            "v.pw_fx_crouch_amt": 3.0 if c.get("_st") else 0.0, "q.delta_time": 0.05}


# --- HOGLIN / ZOGLIN (HoglinModel: head.xRot = lerp(h, 50 deg, -20 deg), h = 1 - |10 - 2 ticksLeft| / 10; Mojang reads v.attack_time)
HOG_SEEDS = {"head": {"rx": "0.87266463 - 1.22173047 * (((v.attack_time ?? 0.0) > 0.0) ? (1.0 - math.abs(2.0 * (v.attack_time ?? 0.0) - 1.0)) : 0.0)"}}


def hog_java(c):
    t = c.get("_attack", 0.0); h = (1.0 - abs(2.0 * t - 1.0)) if t > 0 else 0.0
    return {"head": {"rx": 0.87266463 - 1.22173047 * h}}


def hog_env(c):
    return {"v.attack_time": c.get("_attack", 0.0), "q.delta_time": 0.05}


# --- COD (CodModel: tail.yRot = -f 0.45 sin(0.6 age), f = 1 in water, 1.5 on land)
COD_SEEDS = {"tail": {"ry": "-(q.is_in_water ? 1.0 : 1.5) * 0.45 * math.sin(q.life_time * 20.0 * 0.6 * 57.2957795)"}}


# CodRenderer.setupRotations: yaw 4.3 sin(0.6 age) deg (entity Y -> model -Y), then out of water translate(0.1, 0.1, -0.1) + roll 90 on Z
# (FreshLX's body2.rz carries -90 deg to lie the fish back on its side with his own flop on top). Two bones keep Java's order.
_DRY = "(1.0 - q.is_in_water)"
COD_RENDER = [("pw_render_yaw", [0.0, 0.0, 0.0], {"rotation": [0.0, "-4.3 * math.sin(q.life_time * 20.0 * 0.6 * 57.2957795)", 0.0]}),
              ("pw_render_roll", [0.0, 0.0, 0.0], {"rotation": [0.0, 0.0, f"90.0 * {_DRY}"], "position": [f"-1.6 * {_DRY}", f"1.6 * {_DRY}", f"-1.6 * {_DRY}"]})]


def cod_java(c):
    f = 1.0 if c.get("is_in_water", False) else 1.5
    return {"tail": {"ry": -f * 0.45 * math.sin(0.6 * c.get("age", 0.0))}}


def pos_env(c):
    return {"q.position(0.0)": c.get("pos_x", 0.0), "q.position(1.0)": c.get("pos_y", 64.0), "q.position(2.0)": c.get("pos_z", 0.0), "q.delta_time": 0.05}


# --- CAT / OCELOT (FelineModel lie-down; Mojang's cat controller: v.state 0 sneak, 1 sprint, 2 sit, 3 walk, 4 lie down)
_LA, _LT = "(v.liedownamount ?? 0.0)", "(v.liedownamounttail ?? 0.0)"
_LY = f"({_LA} > 0.0)"
CAT_SEEDS = {   # FelineModel lie-down: rotLerp toward the lying values by lieDownAmount (tail by lieDownAmountTail); legs set outright
    "head": {"rx": "q.target_x_rotation * 0.0174532925",
             "ry": f"q.target_y_rotation * 0.0174532925 + (1.27079633 - q.target_y_rotation * 0.0174532925) * {_LA}",
             "rz": f"-1.27079633 * {_LA}"},
    "front_left_leg": {"rx": f"{_LY} ? -0.47079635 : 0.0", "ry": "0.0"},
    "front_right_leg": {"rx": f"{_LY} ? -1.27079633 : 0.0", "ry": "0.0"},
    "back_left_leg": {"rx": f"{_LY} ? -0.4 : 0.0", "ry": "0.0"},
    "back_right_leg": {"rx": f"{_LY} ? 0.5 : 0.0", "ry": "0.0"},
    "tail": {"rx": f"1.57079633 + (0.8 - 1.57079633) * {_LT}"},
    "tail2": {"rx": f"1.72787596 + (-0.4 - 1.72787596) * {_LT}"},
}
# CatRenderer.setupRotations: translate(0.4f, 0.15f, 0.1f) * amount, roll 90 deg * amount about the entity origin, then (on a sleeping
# player) translate(0.15, 0, 0) in the rolled frame. Entity -> model space = diag(-1,-1,1); Java model px -> file (x, -y, z) with
# the cat's 0.8 render scale undone (model px = blocks * 16 / 0.8): x -8.0, y +3.0 (+3.0 on a player), z +2.0; roll +90 on z
CAT_RENDER = [("pw_render", [0.0, 0.0, 0.0], {"rotation": [0.0, 0.0, f"90.0 * {_LA}"],
                                               "position": [f"-8.0 * {_LA}", f"3.0 * {_LA} + 3.0 * (v.lieonplayer ?? 0.0)", f"2.0 * {_LA}"]})]
CAT_PX = {"is_sitting": "q.is_sitting", "is_tamed": "q.is_tamed", "health": "q.health",
          "is_sneaking": "((v.state ?? 3.0) == 0.0)", "is_sprinting": "((v.state ?? 3.0) == 1.0)"}


def cat_java(c):
    ly = c.get("_lie", 0)
    return {"head": {"rx": math.radians(c.get("head_pitch", 0.0)), "ry": 1.27079633 if ly else math.radians(c.get("head_yaw", 0.0)), "rz": -1.27079633 if ly else 0.0},
            "front_left_leg": {"rx": -0.47079635 if ly else 0.0, "ry": 0.0}, "front_right_leg": {"rx": -1.27079633 if ly else 0.0, "ry": 0.0},
            "back_left_leg": {"rx": -0.4 if ly else 0.0, "ry": 0.0}, "back_right_leg": {"rx": 0.5 if ly else 0.0, "ry": 0.0},
            "tail": {"rx": 0.8 if ly else PI / 2}, "tail2": {"rx": -0.4 if ly else 1.72787596}}    # (the gate states amount 0 or 1)


def cat_env(c):
    st = 4.0 if c.get("_lie") else 0.0 if c.get("is_sneaking") else 1.0 if c.get("is_sprinting") else 3.0
    return {**pos_env(c), "v.state": st, "v.liedownamount": 1.0 if c.get("_lie") else 0.0, "v.liedownamounttail": 1.0 if c.get("_lie") else 0.0, "q.is_sitting": float(bool(c.get("is_sitting"))), "q.is_tamed": float(bool(c.get("is_tamed"))),
            "q.health": c.get("health", 10.0), "q.is_riding": float(bool(c.get("is_riding")))}


# --- GOAT (GoatModel: head.xRot = rammingXHeadRot when != 0; horns = hasLeft/RightHorn; Mojang: v.should_bow_head, v.goat_has_*_horn)
GOAT_SEEDS = {"head": {"rx": "q.target_x_rotation * 0.0174532925 + math.sin((v.should_bow_head ?? 0.0) * 90.0) * 0.65100781"},
              "left_horn": {"visible": "(v.goat_has_left_horn ?? 1.0)"}, "right_horn": {"visible": "(v.goat_has_right_horn ?? 1.0)"}}
GOAT_PX = {"rule_index": "(q.is_on_ground ? 2.0 : 1.0)"}      # 2 = Patrix's 'standing on grass' rule (no block-below query in a RP)


def goat_java(c):
    return {"head": {"rx": math.radians(c.get("head_pitch", 0.0)) + math.sin(math.radians(c.get("_bow", 0.0) * 90.0)) * 0.65100781},
            "left_horn": {"visible": bool(c.get("_lh", 1))}, "right_horn": {"visible": bool(c.get("_rh", 1))}}


def goat_env(c):
    return {**pos_env(c), "v.should_bow_head": c.get("_bow", 0.0), "v.goat_has_left_horn": float(c.get("_lh", 1)), "v.goat_has_right_horn": float(c.get("_rh", 1)),
            "q.is_riding": float(bool(c.get("is_riding")))}


# --- IRON GOLEM (IronGolemModel: attack / flower / walk arms, walk legs; Mojang: v.attack_animation_tick, v.offer_flower_tick)
_WT = mtri("q.modified_distance_moved", 13.0)
_AT = mtri("v.attack_animation_tick", 10.0)
_FT = mtri("v.offer_flower_tick", 70.0)
_ATK, _FLW = "((v.attack_animation_tick ?? 0.0) > 0.0)", "((v.offer_flower_tick ?? 0.0) > 0.0)"
GOLEM_SEEDS = {
    "right_arm": {"rx": f"{_ATK} ? (-2.0 + 1.5 * {_AT}) : ({_FLW} ? (-0.8 + 0.025 * {_FT}) : ((-0.2 + 1.5 * {_WT}) * q.modified_move_speed))"},
    "left_arm": {"rx": f"{_ATK} ? (-2.0 + 1.5 * {_AT}) : ({_FLW} ? 0.0 : ((-0.2 - 1.5 * {_WT}) * q.modified_move_speed))"},
    "right_leg": {"rx": f"-1.5 * {_WT} * q.modified_move_speed"},
    "left_leg": {"rx": f"1.5 * {_WT} * q.modified_move_speed"},
}
GOLEM_RENDER = [("pw_render", [0.0, 0.0, 0.0], {"rotation": [0.0, 0.0,
                  f"(q.modified_move_speed >= 0.01) ? 6.5 * {mtri('(q.modified_distance_moved + 6.0)', 13.0)} : 0.0"]})]
GOLEM_PX = {"health": "q.health", "max_health": "q.max_health", "is_aggressive": "q.has_target", "rot_y": "0.0"}


def golem_java(c):
    h, g = c.get("limb_swing", 0.0), c.get("limb_speed", 0.0); a, f = c.get("_atk", 0.0), c.get("_flw", 0.0)
    if a > 0: r = l = -2.0 + 1.5 * tri(a, 10.0)
    elif f > 0: r, l = -0.8 + 0.025 * tri(f, 70.0), 0.0
    else: r, l = (-0.2 + 1.5 * tri(h, 13.0)) * g, (-0.2 - 1.5 * tri(h, 13.0)) * g
    return {"right_arm": {"rx": r}, "left_arm": {"rx": l}, "right_leg": {"rx": -1.5 * tri(h, 13.0) * g}, "left_leg": {"rx": 1.5 * tri(h, 13.0) * g}}


def golem_env(c):
    return {**pos_env(c), "v.attack_animation_tick": c.get("_atk", 0.0), "v.offer_flower_tick": c.get("_flw", 0.0), "q.health": c.get("health", 100.0),
            "q.max_health": c.get("max_health", 100.0), "q.has_target": float(bool(c.get("is_aggressive")))}


MOBS = {
    "hoglin": {"prefix": "pw_hg", "px": {**COMMON}, "seeds": HOG_SEEDS, "java": hog_java, "env": hog_env, "extra": {}},
    "zoglin": {"prefix": "pw_zg", "px": {**COMMON}, "seeds": HOG_SEEDS, "java": hog_java, "env": hog_env, "extra": {}},
    "cod": {"prefix": "pw_cd", "px": {**COMMON}, "seeds": COD_SEEDS, "java": cod_java, "env": pos_env, "extra": {}, "render": COD_RENDER},
    "fox": {"prefix": "pw_fx", "px": {**COMMON, "is_sitting": "q.is_sitting", "sit_amt": "v.pw_fx_sit_amt"}, "seeds": FOX_SEEDS, "java": fox_java, "env": fox_env,
            "blend": "is_sitting",
            "extra": {"body": {"rx", "ry", "rz", "tx", "ty", "tz"}, **{f"leg{i}": {"visible"} for i in (1, 2, 3, 4)}},
            "pivot": {"body": "template+rot"}, "render": FOX_RENDER},
    "cat": {"prefix": "pw_ct", "px": {**COMMON, **CAT_PX}, "seeds": CAT_SEEDS, "java": cat_java, "env": cat_env, "extra": {}, "render": CAT_RENDER},
    "ocelot": {"prefix": "pw_oc", "px": {**COMMON, **CAT_PX}, "seeds": CAT_SEEDS, "java": cat_java, "env": cat_env, "extra": {}},
    "goat": {"prefix": "pw_gt", "px": {**COMMON, **GOAT_PX}, "seeds": GOAT_SEEDS, "java": goat_java, "env": goat_env, "extra": {}},
    "iron_golem": {"prefix": "pw_ig", "px": {**COMMON, **GOLEM_PX}, "seeds": GOLEM_SEEDS, "java": golem_java, "env": golem_env,
                   "extra": {"right_arm": {"rx"}, "left_arm": {"rx"}}, "root": True, "render": GOLEM_RENDER},
}


def jem_of(m):
    return convb.split_this(load_json(convb.CEM / f"{m}.jem"))


def set_part_pivots(m):
    """every top-level part whose t* the JEM assigns sits at its runtime pivot ('anim'); per-mob overrides on top (fox body:
    Java's template pivot + rotation, the JEM never assigns it)."""
    jem = jem_of(m); asg = convb.assigned_attrs(jem)
    pp = {}
    for part in jem["models"]:
        n = part.get("part") or part.get("id")
        if {"tx", "ty", "tz"} & asg.get(n, set()): pp[n] = "anim"
    pp.update(MOBS[m].get("pivot", {}))
    convb.PART_PIVOT[m] = pp
    return pp


def bake(m):
    set_part_pivots(m)
    convb.SEED_PATCH[m] = {part: {ch: v for ch, v in d.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
                           for part, d in MOBS[m]["java"](rest_case(m)).items()}
    return convb.bake(m)


def rest_case(m):
    return {"is_in_water": m == "cod", "is_on_ground": m != "cod"}


def uses_frame_counter(m):
    return any("frame_counter" in e for _, e in P.assignments(jem_of(m)))


def port(m):
    """frame_counter (Java: +1 every rendered frame; the JEMs compare it with last frame's copy so a model evaluated twice in one
    frame updates its ramps once) -> a per-entity counter bumped once per pre_animation run = once per rendered frame"""
    b, tw, th, info = bake(m)
    cfg = MOBS[m]; pf = cfg["prefix"]
    names = [x["name"] for x in b]
    px, seeds = dict(cfg["px"]), dict(cfg["seeds"])
    if uses_frame_counter(m):
        seeds = {"fc": {"n": f"(v.{pf}_fc_n ?? 0.0) + 1.0"}, **seeds}; px["frame_counter"] = f"v.{pf}_fc_n"
    b = hierarchy(m, b); names = [x["name"] for x in b]
    rewrites = ()
    if cfg.get("blend"):
        asg = [(t, e) for t, e in P.assignments(jem_of(m)) if re.search(r"\b%s\b" % cfg["blend"], e)]
        assert len({t for t, _ in asg}) == len(asg), "a blended target is assigned twice"
        rewrites = [(t, blend_if(e, cfg["blend"])) for t, e in asg]
    init, pre, anim, rep = P.port(m, names, pf, params_extra=px, seeds=seeds, extra_driven=cfg["extra"], rewrites=rewrites)
    rep["blended"] = [t for t, _ in rewrites]
    # a driven vanilla part with no cube anywhere below it draws nothing (the fox `head`: FreshLX moves it for Java's held-item
    # layer only) - leave it out of the animation (its variables still run); the Bedrock binder would otherwise wrap a real bone
    keep = {x["name"] for x in b if subtree_has_cubes(b, x["name"])} | ({"root"} if cfg.get("root") else set())
    rep["pruned"] = sorted(k for k in anim["bones"] if k not in keep)
    anim["bones"] = {k: v for k, v in anim["bones"].items() if k in keep}
    for name, piv, ch in cfg.get("render", []):          # the Java renderer's whole-model moves (setupRotations), outermost first
        anim["bones"] = {name: ch, **anim["bones"]}
    return b, tw, th, init, pre, anim, rep


ROOT_PIVOT = [0.0, 24.0, 0.0]         # Java model root = PartPose.ZERO -> file (0, 24, 0)


def render_names(m):
    return [r[0] for r in MOBS[m].get("render", [])]


def hierarchy(m, bones):
    """root (the golem's JEM root) under the renderer bones (Java setupRotations: cat lie-down roll, cod wiggle + flop roll, golem
    walk sway), outermost first; every former top-level bone hangs below; rest pose unchanged (all rotations 0)"""
    cfg = MOBS[m]
    if cfg.get("root"): bones = add_root(bones)
    for name, piv, ch in reversed(cfg.get("render", [])):
        bones = copy.deepcopy(bones)
        for x in bones:
            if not x.get("parent"): x["parent"] = name
        bones = [{"name": name, "pivot": list(piv), "rotation": [0.0, 0.0, 0.0], "cubes": []}] + bones
    return bones


def add_root(bones):
    """the golem JEM moves `root` (Java's model root: the damaged limp + the sideways sway with the left leg); the bake has no such
    part -> a cube-less `root` at Java's origin, parent of every top-level bone (rest pose unchanged: rotation 0)"""
    bones = copy.deepcopy(bones)
    assert "root" not in {x["name"] for x in bones}
    for x in bones:
        if not x.get("parent"): x["parent"] = "root"
    return [{"name": "root", "pivot": list(ROOT_PIVOT), "rotation": [0.0, 0.0, 0.0], "cubes": []}] + bones


def subtree_has_cubes(bones, n):
    kids = {n}; grew = True
    while grew:
        more = {x["name"] for x in bones if x.get("parent") in kids} - kids; grew = bool(more); kids |= more
    return any(x.get("cubes") for x in bones if x["name"] in kids)


# ----------------------------------------------------------------------------------------------------------------- state cases
def cases(m):
    base = [{"age": a, "limb_swing": ls, "limb_speed": sp, "head_yaw": hy, "head_pitch": hp}
            for a, ls, sp, hy, hp in ((0.0, 0.0, 0.0, 0.0, 0.0), (37.0, 5.1, 0.35, 20.0, -10.0), (211.0, 13.7, 0.9, -35.0, 15.0), (505.0, 2.2, 0.1, 50.0, 0.0))]
    for c in base: c.update(rest_case(m))
    out = [dict(c) for c in base]
    if m in ("hoglin", "zoglin"): out += [dict(c, _attack=t) for c in base[:2] for t in (0.25, 0.5, 0.8)]
    if m == "cod": out += [dict(c, is_in_water=False, is_on_ground=True, pos_x=3.5, pos_y=63.2, pos_z=-7.0) for c in base]
    if m == "fox": out += [dict(c, **k) for c in base[:3] for k in ({"_st": 1}, {"_sl": 1}, {"_si": 1, "is_sitting": True},
                                                                        {"is_in_water": True, "is_on_ground": False})]
    if m in ("cat", "ocelot"):
        out += [dict(c, **k) for c in base[:3] for k in ({"_lie": 1}, {"is_sitting": True}, {"is_sneaking": True}, {"is_sprinting": True},
                                                          {"is_tamed": True, "health": 20.0}, {"is_in_water": True, "is_on_ground": False})]
    if m == "goat": out += [dict(c, **k) for c in base[:3] for k in ({"_bow": 0.6}, {"_lh": 0}, {"_rh": 0}, {"is_on_ground": False})]
    if m == "iron_golem":
        for c in out: c.update(health=100.0, max_health=100.0)          # CemContext defaults to 20 (a badly hurt golem): state it
        out += [dict(c, **k) for c in out[:3] for k in ({"_atk": 7.0}, {"_atk": 3.0}, {"_flw": 30.0}, {"health": 20.0}, {"health": 40.0})]
    return out


def jem_frames(jem, params, seeds, iterations):
    """cem_eval.rest_pose with Java's frame counter advancing one per frame (the JEM ramps update every frame, as in game)"""
    from cem_eval import CemContext, evaluate, assign
    ctx = CemContext(params); ctx.params["id"] = 1.0
    steps = [(part.get("part") or part.get("id"), k, v) for part in jem.get("models", []) if isinstance(part, dict)
             for block in part.get("animations", []) or [] for k, v in block.items()]
    errs = {}
    for i in range(iterations):
        ctx.params["frame_counter"] = float(i + 1)
        for mm, d in (seeds or {}).items(): ctx.model(mm).update(d)
        for pname, k, v in steps:
            try: assign(k, evaluate(v, ctx, pname), ctx, pname)
            except Exception as e: errs[k] = str(e)[:80]
    return ctx, errs


def n2(m, init, pre, anim):
    """Molang (molang_eval) == JEM (cem_eval) on every driven channel; both sides run convb.ITERATIONS frames (N2 of FA-1 with the
    frame counter advancing)"""
    cfg = MOBS[m]; jem, rest = P.rest_of(m)
    worst = {"rotation": 0.0, "position": 0.0, "scale": 0.0}
    for c in cases(m):
        ctx, _ = jem_frames(jem, {k: v for k, v in c.items() if not k.startswith("_")}, cfg["java"](c), convb.ITERATIONS)
        with ME.strict():                 # D-C317: a never-set variable is an error in game, so it is one here too
            chans = eval_channels(m, init, pre, anim, c)
        for part, b in anim["bones"].items():
            if part in render_names(m): continue            # the Java RENDERER's moves: not JEM channels (N3 + the preview judge them)
            mm = ctx.model(part); r = rest.get(part, {})
            for kind, chs in (("rotation", ("rx", "ry", "rz")), ("position", ("tx", "ty", "tz")), ("scale", ("sx", "sy", "sz"))):
                if kind not in b: continue
                for i, ch in enumerate(chs):
                    if not isinstance(b[kind][i], str): continue
                    got = chans[part][kind][i]
                    if kind == "rotation": want = math.degrees(mm[ch] - r.get(ch, 0.0))
                    elif kind == "position": want = (mm[ch] - r.get(ch, 0.0)) * (-1.0 if ch == "ty" else 1.0)
                    else:
                        want = mm[ch] if ch in mm else 1.0
                        if not mm.get("visible", True): want = 0.0
                    worst[kind] = max(worst[kind], abs(got - want))
    return worst


# ----------------------------------------------------------------------------------------------------------------- N3 world geometry
@contextmanager
def single_pose(m, c):
    """convb.bake evaluates the JEM ONCE at case c (Java seeds of c) instead of averaging the idle; the fox body sits at its Java
    runtime pose for the case (RUNTIME_POSE)"""
    old_avg, old_seeds = convb.averaged_models, convb.seeds_for
    old_pp = copy.deepcopy(convb.PART_PIVOT.get(m)); old_rt = copy.deepcopy(convb.RUNTIME_POSE.get(m))
    js = MOBS[m]["java"](c)
    num = {part: {ch: v for ch, v in d.items() if isinstance(v, (int, float)) and not isinstance(v, bool)} for part, d in js.items()}

    def seeds(jem, jname, tkey):
        s = old_seeds(jem, jname, tkey)
        for part, d in js.items(): s[part] = {**s.get(part, {}), **d}
        return s

    def avg(jem, sd, n=None, params=None, avg_limb_swing=False):
        pr = {k: v for k, v in c.items() if not k.startswith("_")}
        ctx, err = jem_frames(jem, pr, sd, convb.ITERATIONS)
        out = {mm: {k: float(v) for k, v in d.items() if isinstance(v, (int, float)) and not isinstance(v, bool)} for mm, d in ctx.models.items()}
        for mm, d in ctx.models.items():
            if "visible" in d: out.setdefault(mm, {})["visible"] = bool(d["visible"])
        return out, err
    try:
        convb.averaged_models, convb.seeds_for = avg, seeds
        set_part_pivots(m)
        for part, mode in (MOBS[m].get("pivot") or {}).items():
            if mode == "template+rot":               # truth: the Java pose of THIS case
                convb.PART_PIVOT[m][part] = "runtime"
                convb.RUNTIME_POSE.setdefault(m, {})[part] = num[part]
        yield
    finally:
        convb.averaged_models, convb.seeds_for = old_avg, old_seeds
        if old_pp is None: convb.PART_PIVOT.pop(m, None)
        else: convb.PART_PIVOT[m] = old_pp
        if old_rt is None: convb.RUNTIME_POSE.pop(m, None)
        else: convb.RUNTIME_POSE[m] = old_rt


def eval_channels(m, init, pre, anim, c):
    cfg = MOBS[m]
    env = {f"v.{cfg['prefix']}_rid": 0.5, "q.modified_distance_moved": c.get("limb_swing", 0.0), "q.modified_move_speed": c.get("limb_speed", 0.0),
           "q.life_time": c.get("age", 0.0) / 20.0, "q.target_y_rotation": c.get("head_yaw", 0.0), "q.target_x_rotation": c.get("head_pitch", 0.0),
           "q.is_alive": 1.0, "q.hurt_time": 0.0, "v.attack_time": c.get("swing_progress", 0.0),
           "q.is_on_ground": 1.0 if c.get("is_on_ground", True) else 0.0, "q.is_in_water": 1.0 if c.get("is_in_water", False) else 0.0}
    env.update(cfg["env"](c))
    for _ in range(convb.ITERATIONS):                 # the same frame count as the JEM truth (rest_pose): ramps (var.run) settle alike
        for s in pre: ME.run(s, env)
    chans = {}
    for bone, ch in anim["bones"].items():
        d = {}
        for kind in ("rotation", "position", "scale"):
            if kind in ch: d[kind] = [ME.run(x, dict(env)) if isinstance(x, str) else float(x) for x in ch[kind]]
        chans[bone] = d
    return chans


def n3(m, rest_bones, init, pre, anim, case_list=None):
    """max corner distance (px) between the posed port and the JEM baked at the pose, over the cases; hidden parts skipped"""
    import wing_contact as WC
    worst, per = 0.0, []
    for c in case_list or cases(m):
        with ME.strict():
            chans = eval_channels(m, init, pre, anim, c)
        hidden = {b for b, d in chans.items() if "scale" in d and min(abs(v) for v in d["scale"]) < 1e-6}
        with single_pose(m, c):
            tb, *_ = convb.bake(m)
        # the truth bake has neither the JEM root nor the renderer bones: the same bones, moved by the same channels (N2 checks the
        # root channels against the JEM; the renderer moves come from the Java renderer, not the JEM)
        tb = hierarchy(m, tb)
        chans_t = {k: chans.get(k, {}) for k in (["root"] if MOBS[m].get("root") else []) + render_names(m)}
        by_t = {b["name"]: b for b in tb}
        def subtree(names, bones):
            out, kids = set(names), True
            while kids:
                kids = {b["name"] for b in bones if b.get("parent") in out} - out; out |= kids
            return out
        skip = subtree(hidden, rest_bones)
        names = {b["name"] for b in rest_bones if b.get("cubes")} - skip
        A = {(n, i): pts for n, i, pts in WC.boxes(rest_bones, WC.affines(rest_bones, chans), names)}
        B = {(n, i): pts for n, i, pts in WC.boxes(tb, WC.affines(tb, chans_t), names & set(by_t))}
        common = set(A) & set(B)
        e = max((float(np.abs(A[k] - B[k]).max()) for k in common), default=0.0)
        per.append((e, {k: v for k, v in c.items()}, len(common), len(A), len(B)))
        worst = max(worst, e)
    return worst, per


if __name__ == "__main__":
    for m in sys.argv[1:] or list(MOBS):
        b, tw, th, init, pre, anim, rep = port(m)
        w2 = n2(m, init, pre, anim)
        w3, per = n3(m, b, init, pre, anim)
        bad = sorted(per, key=lambda x: -x[0])[:3]
        print(f"{m}: {len(b)} bones, {len(pre)} statements, {len(anim['bones'])} driven bones, skipped {rep['skipped']}")
        print(f"   N2 {({k: round(v, 5) for k, v in w2.items()})}   N3 worst {w3:.4f} px   (cubes compared {bad[0][2]} of {bad[0][3]}/{bad[0][4]})")
        for e, c, *_ in bad: print(f"      {e:.4f} px  {({k: v for k, v in c.items() if k.startswith('_') or k in ('is_sitting', 'is_in_water', 'is_sneaking', 'is_sprinting', 'health', 'limb_speed')})}")
