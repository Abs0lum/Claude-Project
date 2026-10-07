#!/usr/bin/env python3
"""convb.py — CONVERTER B, general form (D-C272; the equine build, D-C269, is its witnessed special case).

A Bedrock geometry built straight from a Patrix JEM in its FreshLX rest posture:
  1. SEEDS — the per-frame values the vanilla Java model writes before the CEM animations run, taken from the vanilla
     template (CEM Template Models v5.0.3) for every part the JEM reads but never assigns:
        tx = t[0], ty = 24 + t[1], tz = -t[2]  (template translate t = -pivot_BB)
        rx = -rad(r[0]), ry = -rad(r[1]), rz = +rad(r[2])  (template rotate r = BB degrees)
     plus per-mob overrides where the template is known to disagree with the Java model Patrix targets (equines: neck).
  2. REST POSE — every animation evaluated at rest (cem_eval) with the seeds re-applied each iteration, AVERAGED over 64
     idle times so the idle sway cancels and the designed pose remains.
  3. BAKE — jem_convert.bake_rest2 with that averaged pose (CEM-RT: each top-level part sits at the vanilla part's pivot and
     rest rotation unless the animation assigns it; submodels at their JEM pivots; animated attributes REPLACE the static ones).
  4. RENAME — the bones our client entity's animations / render controllers bind are mapped onto the baked bones: same name
     first, then an alias table, then (for legs) nearest pivot in the same body quadrant. Unmapped bind names are reported.
  5. to_bedrock (CONV-1 frames).
API: bake(mob) -> (bedrock_bones, tw, th, info)   ·   rename(bones, bind_names, ours_bones) -> (bones, mapping, missing)
"""
import json, math, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import jem_convert
from cem_eval import rest_pose
from jem_convert import bake_rest2, to_bedrock, load_json, vanilla_template

CEM = Path("/home/claude/_intake/patrix-mobs/assets/minecraft/optifine/cem")
TEMPLATE_KEY = {"zombified_piglin": "piglin", "mooshroom": "cow", "glow_squid": "squid",
                "trader_llama": "llama",   # D-C275: the template has no trader llama; without the llama body pose (90 deg) the body stood upright
                "trader_llama_decor": "llama", "llama_decor": "llama"}
_EQUINE_SEEDS = {"neck": {"ty": 4.0, "tz": -12.0, "rx": 0.5235988}, "body": {"rx": 0.0}, "tail": {"ry": 0.0}}   # witnessed D-C271
SEED_OVERRIDE = {m: _EQUINE_SEEDS for m in ("horse", "donkey", "mule", "zombie_horse", "skeleton_horse")}
N_SAMPLES = 64


def template_seeds(tkey):
    tpl = vanilla_template(tkey)
    out = {}
    for p in (tpl or {}).get("models", []):
        if not isinstance(p, dict): continue
        name = p.get("part") or p.get("id")
        t = p.get("translate") or [0, 0, 0]; r = p.get("rotate") or [0, 0, 0]
        out[name] = {"tx": float(t[0]), "ty": 24.0 + float(t[1]), "tz": -float(t[2]),
                     "rx": -math.radians(r[0]), "ry": -math.radians(r[1]), "rz": math.radians(r[2])}
    return out


def read_only_parts(jem):
    """vanilla parts the JEM READS in expressions but never assigns (only those need seeding)."""
    import re
    assigned, rhs = set(), []
    for m in jem.get("models", []):
        for blk in m.get("animations", []) or []:
            for k, v in blk.items():
                assigned.add(k.rpartition(".")[0]); rhs.append(str(v))
    reads = set()
    for v in rhs:
        for mm, a in re.findall(r"\b([a-z_][a-z0-9_]*)\.(tx|ty|tz|rx|ry|rz)\b", v):
            if mm not in ("var", "varb", "render") and mm not in assigned: reads.add(mm)
    return reads


# vanilla part state the Java model sets per frame that the template cannot carry (turtle: egg belly hidden = not carrying an
# egg; with it visible the JEM's digging branch fires and folds one flipper)
SEED_EXTRA = {"turtle": {"body2": {"visible": False}},
              "frog": {"croaking_body": {"visible": False}}}   # D-C276: vanilla shows the croak sac only while croaking
# mobs whose rest pose also averages over the walk cycle phase (the JEM keeps sin(limb_swing) terms at limb_speed 0 —
# turtle front flippers 6.5 deg vs 33.5 deg at limb_swing 0; the cycle mean is the designed neutral 20 deg / 20 deg)
AVG_LIMB_SWING = {"turtle"}


# D-C278 — Java static part poses the CEM template does not carry, for vanilla parts the JEM READS (seed values, OptiFine
# units: radians, Java signs). Dolphin: DolphinModel left_fin / right_fin = offsetAndRotation(±2, -2, 4, 60 deg, 0, ±120 deg);
# FreshLX copies them (right_fin2.r* = right_fin.r* + motion) — with template seeds of 0 the flippers lay flat along the
# belly (his R4 e03 "parts?"; 022955-023005). FreshLX's own static rotate [-55, 0, ±120] is the same pose.
SEED_PATCH = {"dolphin": {"right_fin": {"rx": 1.0471976, "ry": 0.0, "rz": -2.0943952},
                          "left_fin": {"rx": 1.0471976, "ry": 0.0, "rz": 2.0943952}}}


def seeds_for(jem, jname, tkey):
    if jname in SEED_OVERRIDE or tkey in SEED_OVERRIDE:
        out = dict(SEED_OVERRIDE.get(jname) or SEED_OVERRIDE[tkey])
    else:
        ts = template_seeds(tkey); need = read_only_parts(jem)
        out = {p: ts[p] for p in need if p in ts}
    for part, d in SEED_PATCH.get(jname, {}).items(): out[part] = {**out.get(part, {}), **d}
    for part, d in SEED_EXTRA.get(jname, {}).items(): out[part] = {**out.get(part, {}), **d}
    return out


AQUATIC = {"turtle": {"is_in_water": False, "is_on_ground": True}, "axolotl": {"is_in_water": True}, "salmon": {"is_in_water": True, "is_on_ground": False},
           "dolphin": {"is_in_water": True, "is_on_ground": False}, "squid": {"is_in_water": True, "is_on_ground": False},
           "glow_squid": {"is_in_water": True, "is_on_ground": False}, "tropical_fish_a": {"is_in_water": True, "is_on_ground": False},
           "tropical_fish_b": {"is_in_water": True, "is_on_ground": False}, "cod": {"is_in_water": True, "is_on_ground": False},
           # D-C285 (his R8 a18/b18 "on its side"): tadpole.jem rolls body2 -70 deg OUT of water (Patrix flop-on-land) — the rest pose
           # must be the in-water branch; the pufferfish JEMs branch on is_in_water too
           "tadpole": {"is_in_water": True, "is_on_ground": False}, "puffer_fish_big": {"is_in_water": True, "is_on_ground": False},
           "puffer_fish_medium": {"is_in_water": True, "is_on_ground": False}, "puffer_fish_small": {"is_in_water": True, "is_on_ground": False}}
# vanilla rest rotations (BB degrees) the template does not carry but the Java model applies (QuadrupedModel body pose)
REST_ROT_OVERRIDE = {"panda": {"body": [-90.0, 0.0, 0.0]}}
# JEM parts left out of the geometry (the shipped entity has no controller for them)
DROP_PARTS = {"llama": {"chest_left", "chest_right"}, "trader_llama": {"chest_left", "chest_right"},
              "trader_llama_decor": {"chest_left", "chest_right"}, "llama_decor": {"chest_left", "chest_right"}}
# D-C273 — OptiFine hangs a JEM part model under the VANILLA part: world = V + R_v·(p − D). The declared-pivot rule assumes
# V = D. Parts listed here use the runtime vanilla pivot V instead: "anim" = the averaged animated <part>.t* (Java root
# children only: V_BB = (−tx, 24 − ty, tz), unassigned components stay at D); "template" = the vanilla template pivot.
# Evidence (vanilla Bedrock placement): turtle shell y 3..9 / z −9..13 (vanilla 3..9 / −7..13); axolotl body2 pivot y 4
# (vanilla body pivot y 4); salmon body_front z 0 (vanilla); dolphin z −13.8..25.3 (vanilla −13..25).
# "template+rot" = the template pivot AND its static rotation (R_v): squid tentacles — declared rule 6/8 on the ring, exact
# rule 8/8 on a radius-5 ring at 45 deg steps (D-C274). Zombified piglin / ravager: FreshLX re-poses the (Java root-child)
# vanilla parts — ravager leg4 t* = 0 puts the legs' content 24 px up onto the ground (declared rule: 24 px under it).
_TENTACLES = {f"tentacle{i}": "template+rot" for i in range(1, 9)}
PART_PIVOT = {"turtle": {"body": "anim"}, "axolotl": {"body": "anim"}, "salmon": {"body_front": "anim"}, "dolphin": {"body": "template"},
              "squid": _TENTACLES, "glow_squid": _TENTACLES,
              "zombified_piglin": {p: "anim" for p in ("head", "body", "left_arm", "right_arm", "left_leg", "right_leg")},
              "ravager": {"body": "anim", "leg4": "anim"},
              # D-C277 — the same FreshLX humanoid re-pose as the zombified piglin (body/arms/legs t* assigned, d 0.1..3 px)
              **{m: {p: "anim" for p in ("head", "body", "left_arm", "right_arm", "left_leg", "right_leg")} for m in ("piglin", "piglin_brute", "bogged")},
              "tadpole": {"body": "anim"},          # body.ty/tz assigned: runtime pivot (0, 1.5, -0.5) vs declared (0, 1, 1.5)
              "spider": {"neck": "anim"},           # neck.ty assigned: 1.8 px below the declared pivot
              # bee: OptiFine `body` = Java `bone` (root, scaled 0.7..1.0 per bee; median 0.85); `torso` = Java `body`, a CHILD of
              # bone -> its runtime pivot is the parent's plus its own offset ("anim_child", JAVA_PARENT below)
              "bee": {"body": "anim", "torso": "anim_child"}}
# Java parent of a JEM part where the vanilla Java model nests parts (the flat CEM part list loses it): the child's runtime
# pivot is relative to the parent's, the parent's rotation turns it and the parent's scale scales it (D-C277). Minecraft
# 1.21.2+ model trees (Patrix targets 1.21.11): HumanoidModel/PlayerModel head > hat (OptiFine `headwear`); BeeModel bone >
# body (OptiFine `body` > `torso`). The child's mode is "anim_child" (PART_PIVOT is filled from this table below).
# Java per-frame part poses the template cannot carry and the JEM does not assign (setupAnim writes them every frame): the part
# then sits at V = (-tx, 24 - ty, tz) with the Java rotation R_v, and the Patrix content hangs off it (world = V + R_v (p - D)).
# GUARDIAN spikes (D-C277, his 00:10 "research what the guardians are SUPPOSED to look like"): Java GuardianModel.setupSpikes
# puts spike i at (SPIKE_X[i]*k, 16 + SPIKE_Y[i]*k, SPIKE_Z[i]*k), k = 1 + cos(age*1.5 + i)*0.01 - (1 - spikesAnim)*0.55,
# rotated (PI*SPIKE_X_ROT[i], PI*SPIKE_Y_ROT[i], PI*SPIKE_Z_ROT[i]) — the same numbers Mojang's Bedrock port carries in
# animation.guardian.setup / .spikes (bedrock-samples). OptiFine spine1..12 = spike0..11 (EMF mapping). Rest = idle in water
# (spikesAnim 1 -> k = 1: fully extended, the iconic pose). The Patrix JEM zeroes its own spineN_rotation (the template's
# design-time stand-in for R_v), so without R_v the spikes lay flat along the edges (the dry-run preview he rejected).
_SPK_XR = [1.75, 0.25, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 1.25, 0.75, 0.0, 0.0]
_SPK_YR = [0.0, 0.0, 0.0, 0.0, 0.25, 1.75, 1.25, 0.75, 0.0, 0.0, 0.0, 0.0]
_SPK_ZR = [0.0, 0.0, 0.25, 1.75, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.75, 1.25]
_SPK_X = [0.0, 0.0, 8.0, -8.0, -8.0, 8.0, 8.0, -8.0, 0.0, 0.0, 8.0, -8.0]
_SPK_Y = [-8.0, -8.0, -8.0, -8.0, 0.0, 0.0, 0.0, 0.0, 8.0, 8.0, 8.0, 8.0]
_SPK_Z = [8.0, -8.0, 0.0, 0.0, -8.0, -8.0, 8.0, 8.0, 8.0, -8.0, 0.0, 0.0]
_SPIKES = {f"spine{i + 1}": {"tx": _SPK_X[i], "ty": 16.0 + _SPK_Y[i], "tz": _SPK_Z[i],
                             "rx": math.pi * _SPK_XR[i], "ry": math.pi * _SPK_YR[i], "rz": math.pi * _SPK_ZR[i]} for i in range(12)}
# RABBIT (D-C278, his R4 e12 "back feet aren't touching the ground"): the Patrix rabbit animates only its head/ears; every other
# part hangs on the Java part (classic RabbitModel, the OptiFine part names left_foot/left_thigh/left_arm): feet (±3, 17.5, 3.7);
# haunches the same pivot, xRot (jump*50 - 21) deg = -21 deg at rest; body (0, 19, 8) xRot -20 deg; front legs (±3, 17, -1)
# xRot (jump*-40 - 11) deg = -11 deg; tail (0, 20, 7) xRot -20 deg. The CEM template's rabbit is a different model (22.5 deg
# poses), so the converter kept the DECLARED pivots and the feet sat 3 px up (declared y 9.5 vs Java 24 - 17.5 = 6.5).
_RAD = math.pi / 180.0
_RABBIT = {"body": {"tx": 0.0, "ty": 19.0, "tz": 8.0, "rx": -20 * _RAD, "ry": 0.0, "rz": 0.0},
           "left_arm": {"tx": 3.0, "ty": 17.0, "tz": -1.0, "rx": -11 * _RAD, "ry": 0.0, "rz": 0.0},
           "right_arm": {"tx": -3.0, "ty": 17.0, "tz": -1.0, "rx": -11 * _RAD, "ry": 0.0, "rz": 0.0},
           "left_thigh": {"tx": 3.0, "ty": 17.5, "tz": 3.7, "rx": -21 * _RAD, "ry": 0.0, "rz": 0.0},
           "right_thigh": {"tx": -3.0, "ty": 17.5, "tz": 3.7, "rx": -21 * _RAD, "ry": 0.0, "rz": 0.0},
           "left_foot": {"tx": 3.0, "ty": 17.5, "tz": 3.7, "rx": 0.0, "ry": 0.0, "rz": 0.0},
           "right_foot": {"tx": -3.0, "ty": 17.5, "tz": 3.7, "rx": 0.0, "ry": 0.0, "rz": 0.0},
           "tail": {"tx": 0.0, "ty": 20.0, "tz": 7.0, "rx": -20 * _RAD, "ry": 0.0, "rz": 0.0}}
RUNTIME_POSE = {"guardian": _SPIKES, "elder_guardian": _SPIKES, "rabbit": _RABBIT}
for _m, _parts in RUNTIME_POSE.items():
    for _p in _parts: PART_PIVOT.setdefault(_m, {})[_p] = "runtime"
JAVA_PARENT = {"bee": {"torso": "body"},
               **{m: {"headwear": "head"} for m in ("piglin", "piglin_brute", "bogged", "zombified_piglin")}}
for _m, _kids in JAVA_PARENT.items():
    for _c in _kids: PART_PIVOT.setdefault(_m, {})[_c] = "anim_child"
ITERATIONS = 24          # >= the longest var.* lag chain in the Patrix JEMs (turtle/salmon: 10-step pos_y history)


def averaged_models(jem, seeds, n=N_SAMPLES, params=None, avg_limb_swing=False):
    """Mean of every model attribute over n idle times (and walk-cycle phases when asked); `visible` is the majority vote."""
    acc, vis, errs = {}, {}, {}
    for i in range(n):
        pr = dict(params or {}); pr["age"] = i * 97.0
        if avg_limb_swing: pr["limb_swing"] = i * (2.0 * math.pi / 16.0) / 1.3
        ctx, err = rest_pose(jem, params=pr, iterations=ITERATIONS, seeds=seeds); errs.update(err)
        for m, d in ctx.models.items():
            for k, v in d.items():
                if k == "visible": vis.setdefault(m, []).append(bool(v)); continue
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    acc.setdefault(m, {}).setdefault(k, []).append(float(v))
    out = {m: {k: sum(v) / len(v) for k, v in d.items()} for m, d in acc.items()}
    for m, d in acc.items():            # D-C276: scales are states (open/blinking eye, water/land leg set) — take the MEDIAN, not the mean
        for k in ("sx", "sy", "sz"):
            if k in d: out[m][k] = sorted(d[k])[len(d[k]) // 2]
    for m, v in vis.items(): out.setdefault(m, {})["visible"] = sum(v) * 2 >= len(v)
    return out, errs


def split_this(jem):
    """Top-level `this.<var>` (the custom model) gets its own name <part>__custom so it does not collide with `<part>.<var>`
    (the original vanilla part) in the rest-pose evaluation."""
    import copy, re as _re
    jem = copy.deepcopy(jem)
    for part in jem.get("models", []):
        pname = part.get("part") or part.get("id")
        for block in part.get("animations", []) or []:
            items = list(block.items()); block.clear()
            for k, v in items:
                k2 = _re.sub(r"^this\.", pname + "__custom.", k)
                v2 = _re.sub(r"\bthis\.", pname + "__custom.", str(v)) if isinstance(v, str) else v
                block[k2] = v2
    return jem


def assigned_attrs(jem):
    out = {}
    for part in jem.get("models", []):
        pname = part.get("part") or part.get("id")
        for block in part.get("animations", []) or []:
            for k in block:
                m, _, a = k.rpartition("."); m = pname if m in ("this", "part") else m.split(":")[-1]
                out.setdefault(m, set()).add(a)
    return out


# D-C284: parts hidden at rest that must STAY in the geometry because a render controller shows them in another state
# (evoker: FreshLX shows right_arm/left_arm only while casting, var.spell >= 0.2; the entity's part_visibility does it in Bedrock)
KEEP_HIDDEN = {"evoker": {"right_arm", "left_arm"}}


def boxuv_to_faces(u, v, size, mirror):
    """D-C284: a box-UV spec as explicit per-face UV in the JEM/Blockbench display form ({face: {uv, uv_size}}, the form
    jem_convert.face_uv reads from a JEM's uvNorth..uvDown) — the SAME texels Bedrock's box UV picks for that size and mirror
    (bb_truth.box_face_uvs = Blockbench cube.js updateUV). to_bedrock -> bedrock_uv then writes it in Bedrock's per-face form
    (up/down turned 180 deg), exactly like a JEM box that was per-face from the start."""
    from bb_truth import box_face_uvs
    out = {}
    for face, (u1, v1, u2, v2) in box_face_uvs(u, v, list(size), mirror).items():
        out[face] = {"uv": [u1, v1], "uv_size": [u2 - u1, v2 - v1]}
    return out


def bake(jname, tkey=None):
    """CONVERTER B bake (the witnessed equine rule, generalised):
       top-level parts stay at the JEM's DECLARED pivot (the author's rest placement); their rotation = the averaged
       animated value where assigned, else the JEM's static rotate, else the vanilla template rotate when the template
       pivot equals the declared pivot (same model version), else an explicit override (panda body);
       submodels take every assigned attribute from the averaged rest pose (translations in the part's frame: depth-1
       absolute, deeper relative to the parent pivot), carrying their boxes and descendants."""
    from jem_convert import jem_tree
    tkey = tkey or TEMPLATE_KEY.get(jname, jname)
    jem = split_this(load_json(CEM / f"{jname}.jem"))
    seeds = seeds_for(jem, jname, tkey)
    rest, errs = averaged_models(jem, seeds, params=AQUATIC.get(jname), avg_limb_swing=jname in AVG_LIMB_SWING)
    asg = assigned_attrs(jem)
    tpl = vanilla_template(tkey) or {}
    tparts = {(p.get("part") or p.get("id")): p for p in tpl.get("models", []) if isinstance(p, dict)}
    bones = jem_tree(jem)
    by = {b["name"]: b for b in bones}
    hidden, applied, pivot_shift = [], {}, {}
    custom_bones = []

    def shift(name, d):
        b = by[name]; b["pivot"] = [b["pivot"][k] + d[k] for k in range(3)]
        for x in b["boxes"]: x["from"] = [x["from"][k] + d[k] for k in range(3)]
        for c in bones:
            if c["parent"] == name: shift(c["name"], d)

    for b in bones: b["declared"] = list(b["pivot"])
    for b in sorted(bones, key=lambda b: b["depth"]):
        n = b["name"]; st = rest.get(n, {}); a = asg.get(n, set())
        if st.get("visible") is False and "visible" in a: hidden.append(n)
        rot = list(b["rotation"])
        if b["depth"] == 0:
            # OptiFine CEM: the JEM part model hangs under the ORIGINAL (vanilla) part. Vanilla part: pose = Java static pose
            # (template rotate, when the template describes the same part: same pivot) or an explicit override, replaced
            # where the animation assigns <part>.r*. Custom model: its JEM `rotate` about the ENTITY ORIGIN (why Patrix
            # authors zero it with `this.r* = 0` when it only copies the vanilla pose), replaced by `this.r*` assignments.
            custom = list(rot); cst = rest.get(n + "__custom", {}); ca = asg.get(n + "__custom", set())
            for k, x in enumerate(("rx", "ry", "rz")):
                if x in ca: custom[k] = (-1 if k < 2 else 1) * math.degrees(cst.get(x, 0.0))
            rot = [0.0, 0.0, 0.0]
            tp = tparts.get(n)
            if tp and tp.get("rotate") and all(abs(-(tp.get("translate") or [0, 0, 0])[k] - b["pivot"][k]) < 0.01 for k in range(3)):
                rot = list(tp["rotate"])
            if n in REST_ROT_OVERRIDE.get(jname, {}): rot = list(REST_ROT_OVERRIDE[jname][n])
            mode = PART_PIVOT.get(jname, {}).get(n); d = [0.0, 0.0, 0.0]
            if mode == "anim":
                V = list(b["pivot"])
                if "tx" in a: V[0] = -st.get("tx", 0.0)
                if "ty" in a: V[1] = 24.0 - st.get("ty", 0.0)
                if "tz" in a: V[2] = st.get("tz", 0.0)
                d = [V[k] - b["pivot"][k] for k in range(3)]
            elif mode == "runtime":
                rp_ = RUNTIME_POSE[jname][n]
                V = [-rp_["tx"], 24.0 - rp_["ty"], rp_["tz"]]
                d = [V[k] - b["pivot"][k] for k in range(3)]
                rot = [-math.degrees(rp_["rx"]), -math.degrees(rp_["ry"]), math.degrees(rp_["rz"])]
            elif mode == "anim_child":
                # Java child part: runtime pivot = the parent's (unrotated) pivot + the child's own offset (Java t*, local:
                # BB = (-tx, -ty, +tz)); an unassigned component keeps the vanilla offset (template child - template parent;
                # 0 when the template lacks either: the 1.21.x hat / bee body are PartPose.ZERO under their parent — NOT the
                # declared difference: FreshLX declares the empty piglin head at (0,0,0)). The parent's rotation then reaches the
                # child through the Bedrock hierarchy (nested below), exactly as the Java ModelPart tree does.
                pn = JAVA_PARENT[jname][n]; par = by[pn]  # already placed (the parent comes first in the JEM part order)
                tpp, tpc = tparts.get(pn), tparts.get(n)
                if tpp and tpc: off0 = [-(tpc.get("translate") or [0, 0, 0])[k] + (tpp.get("translate") or [0, 0, 0])[k] for k in range(3)]
                else: off0 = [0.0, 0.0, 0.0]
                V = [par["pivot"][k] + off0[k] for k in range(3)]
                for k, x, sgn in ((0, "tx", -1.0), (1, "ty", -1.0), (2, "tz", 1.0)):
                    if x in a: V[k] = par["pivot"][k] + sgn * st.get(x, 0.0)
                d = [V[k] - b["pivot"][k] for k in range(3)]
            elif mode in ("template", "template+rot") and tp:
                d = [-(tp.get("translate") or [0, 0, 0])[k] - b["pivot"][k] for k in range(3)]
                if mode == "template+rot": rot = list(tp.get("rotate") or [0.0, 0.0, 0.0])   # the vanilla part's static pose (R_v)
            if any(abs(v) > 1e-9 for v in d):
                shift(n, d); pivot_shift[n] = [round(v, 3) for v in d]
            if mode == "anim_child": b["parent"] = JAVA_PARENT[jname][n]     # Bedrock hierarchy = Java hierarchy
            if any(abs(v) > 1e-6 for v in custom):
                custom_bones.append((n, custom))
        else:
            want = [x for x in ("tx", "ty", "tz") if x in a]
            if want and st:
                par = by.get(b["parent"])
                if b["depth"] == 1:   # absolute in the custom root's frame; the root sits at V - D (D-C273)
                    ps = pivot_shift.get(b["parent"], [0.0, 0.0, 0.0])
                    target = [-st.get("tx", 0.0) + ps[0], -st.get("ty", 0.0) + ps[1], st.get("tz", 0.0) + ps[2]]
                else: target = [par["pivot"][0] - st.get("tx", 0.0), par["pivot"][1] - st.get("ty", 0.0), par["pivot"][2] + st.get("tz", 0.0)]
                new = list(b["pivot"])
                for k, x in enumerate(("tx", "ty", "tz")):
                    if x in want: new[k] = target[k]
                d = [new[k] - b["pivot"][k] for k in range(3)]
                if any(abs(v) > 1e-9 for v in d): shift(n, d)
        for k, x in enumerate(("rx", "ry", "rz")):
            if x in a and st: rot[k] = (-1 if k < 2 else 1) * math.degrees(st.get(x, 0.0))
        b["rotation"] = rot
        if any(abs(v) > 1e-6 for v in rot) or n in hidden: applied[n] = [round(v, 2) for v in rot]
    # D-C276 — part SCALES at rest (FreshLX <part>.s* / this.s*): Java scales a part's boxes and children about its pivot; Converter B
    # used to drop them. Scale ~0 = the part is hidden in that state (axolotl: land legs in water); otherwise baked into the boxes.
    scaled = {}; perface_from_scale = []
    def descendants(name):   # (Java children are nested under their Java parent above, so a parent's scale reaches them)
        out, stack = [], [name]
        while stack:
            x = stack.pop(); out.append(x); stack += [c["name"] for c in bones if c["parent"] == x]
        return out
    for b in sorted(bones, key=lambda b: b["depth"]):
        n = b["name"]; sc = [1.0, 1.0, 1.0]
        for key in (n, n + "__custom"):
            st, a = rest.get(key, {}), asg.get(key, set())
            for k, x in enumerate(("sx", "sy", "sz")):
                if x in a and x in st: sc[k] *= st[x]
        if all(abs(v - 1.0) <= 0.02 for v in sc): continue
        if min(abs(v) for v in sc) < 0.05:
            if n not in hidden: hidden.append(n)
            scaled[n] = [round(v, 3) for v in sc]; continue
        p0 = list(b["pivot"]); mag = [abs(v) for v in sc]
        for dn in descendants(n):
            d = by[dn]
            if dn != n: d["pivot"] = [p0[k] + (d["pivot"][k] - p0[k]) * mag[k] for k in range(3)]
            for x in d["boxes"]:
                if isinstance(x.get("uv"), list):
                    # D-C284 SCALED BOX-UV: box UV derives every face rectangle from the cube SIZE, so a scaled box would
                    # sample a shrunken layout (spider body 0.8: faces reach into the sheet's empty gaps -> square holes,
                    # his 13:26 report). Freeze the texture layout of the UNSCALED box as explicit per-face UV first.
                    x["uv"] = boxuv_to_faces(x["uv"][0], x["uv"][1], x["size"], bool(d.get("mirror")))
                    perface_from_scale.append(dn)
                x["from"] = [p0[k] + (x["from"][k] - p0[k]) * mag[k] for k in range(3)]
                x["size"] = [x["size"][k] * mag[k] for k in range(3)]
                if x.get("inflate"): x["inflate"] = x["inflate"] * sum(mag) / 3.0
        scaled[n] = [round(v, 3) for v in sc]
    # custom-model rotations (about the entity origin): an intermediate bone between the part and its boxes/submodels
    for n, custom in custom_bones:
        b = by[n]; cname = n + "_custom"
        cb = {"name": cname, "parent": n, "depth": b["depth"] + 1, "pivot": list(pivot_shift.get(n, [0.0, 0.0, 0.0])), "rotation": custom, "mirror": b["mirror"],
              "boxes": b["boxes"], "part": b.get("part")}
        b["boxes"] = []
        for c in bones:
            if c["parent"] == n: c["parent"] = cname
        bones.insert(bones.index(b) + 1, cb); by[cname] = cb
        applied[cname] = [round(v, 2) for v in custom]
    # drop hidden-at-rest parts and the per-mob drop list (with descendants)
    drop = (set(hidden) - KEEP_HIDDEN.get(jname, set())) | DROP_PARTS.get(jname, set()); changed = True
    while changed:
        changed = False
        for b in bones:
            if b["name"] not in drop and b["parent"] in drop: drop.add(b["name"]); changed = True
    bones = [b for b in bones if b["name"] not in drop]
    tw, th = jem.get("textureSize") or [64, 32]
    return to_bedrock(bones), tw, th, {"seeds": seeds, "errors": errs, "template": tkey, "has_template": bool(tpl),
                                        "hidden_at_rest": sorted(hidden), "dropped": sorted(drop), "rotations": applied,
                                        "pivot_shift": pivot_shift, "scaled": scaled,
                                        "perface_from_scale": sorted(set(perface_from_scale))}


def relocate_leg_pivots(bones, names):
    """Legs our walk animations swing: a zero-rotation leg bone gets its pivot at the top-centre of its cubes (the hip),
    which leaves the rest geometry unchanged and makes the swing hinge at the body."""
    import re as _re
    for b in bones:   # quadruped legs: the witnessed equine build stands them straight (our walk/idle animations swing them)
        if _re.fullmatch(r"leg\d", b["name"]) and b["name"] in names and b.get("parent") in (None, "body"):
            b["rotation"] = [0.0, 0.0, 0.0]
    for b in bones:
        if b["name"] in names and b.get("cubes") and not any(abs(v) > 1e-6 for v in b.get("rotation", [0, 0, 0])):
            if any(any(c.get("rotation", [0, 0, 0]) or [0]) for c in b["cubes"]): continue
            top = max(c["origin"][1] + c["size"][1] for c in b["cubes"])
            b["pivot"] = [b["pivot"][0], round(top, 4), b["pivot"][2]]
    return bones


ALIASES = {  # our bone name -> JEM/Java part names to try, in order
    "leg0": ["leg0", "right_hind_leg", "back_right_leg", "leg1"], "leg1": ["leg1", "left_hind_leg", "back_left_leg", "leg2"],
    "leg2": ["leg2", "right_front_leg", "front_right_leg", "leg3"], "leg3": ["leg3", "left_front_leg", "front_left_leg", "leg4"],
    "rightArm": ["right_arm"], "leftArm": ["left_arm"], "rightLeg": ["right_leg"], "leftLeg": ["left_leg"], "hat": ["headwear", "hat"],
}


def _cube_centre(b):
    cs = b.get("cubes") or []
    if not cs: return b.get("pivot", [0, 0, 0])
    xs = [c["origin"][0] + c["size"][0] / 2 for c in cs]; ys = [c["origin"][1] + c["size"][1] / 2 for c in cs]; zs = [c["origin"][2] + c["size"][2] / 2 for c in cs]
    return [sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)]


def rename(bones, bind_names, ours):
    """Rename baked bones so every name in bind_names exists. Legs are matched by the quadrant of OUR leg's pivot."""
    by = {b["name"]: b for b in bones}; ob = {b["name"]: b for b in ours}
    mapping, missing, taken = {}, [], set()
    import re as _re
    legs_first = sorted(bind_names, key=lambda n: (not _re.fullmatch(r"leg\d", n), n))
    for want in legs_first:
        if want in by and want not in taken and not _re.fullmatch(r"leg\d", want): mapping[want] = want; taken.add(want); continue
        cands = [a for a in ALIASES.get(want, []) if a in by and a not in taken and a not in bind_names]
        if want.startswith("leg") and want in ob:
            op = ob[want].get("pivot", [0, 0, 0])
            legs = [n for n in by if n not in taken and ("leg" in n) and by[n].get("parent") is None
                    and (n == want or n not in bind_names or _re.fullmatch(r"leg\d", n))]
            if legs:
                best = min(legs, key=lambda n: (math.copysign(1, by[n]["pivot"][0]) != math.copysign(1, op[0] or 1e-9)) * 100
                           + (math.copysign(1, by[n]["pivot"][2]) != math.copysign(1, op[2] or 1e-9)) * 100
                           + abs(by[n]["pivot"][0] - op[0]) + abs(by[n]["pivot"][2] - op[2]))
                cands = [best]
        if cands:
            mapping[want] = cands[0]; taken.add(cands[0])
        else:
            missing.append(want)
    rev = {v: k for k, v in mapping.items()}
    out = []
    for b in bones:
        nb = dict(b); nb["name"] = rev.get(b["name"], b["name"])
        if b.get("parent"): nb["parent"] = rev.get(b["parent"], b["parent"])
        out.append(nb)
    names = [b["name"] for b in out]
    dup = {n for n in names if names.count(n) > 1}
    assert not dup, f"duplicate bone names after rename: {dup}"
    return out, mapping, missing


if __name__ == "__main__":
    for m in sys.argv[1:]:
        bones, tw, th, info = bake(m)
        print(f"== {m} {tw}x{th} template={info['template']}({info['has_template']}) seeds={list(info['seeds'])} errors={len(info['errors'])}")
        for b in bones:
            print(f"   {b['name']:22s} parent={str(b.get('parent')):16s} pivot={[round(v, 2) for v in b['pivot']]} rot={[round(v, 1) for v in b['rotation']]} cubes={len(b['cubes'])}")


def _subtree_centroid(bones, name):
    """Mean centre of the cubes a bone owns, or (if none) of every cube in its subtree; None when the subtree is empty."""
    kids = {}
    for b in bones: kids.setdefault(b.get("parent"), []).append(b)
    by = {b["name"]: b for b in bones}
    pts = []
    def walk(n, own_only):
        for c in by[n].get("cubes", []) or []:
            pts.append([c["origin"][k] + c["size"][k] / 2 for k in range(3)])
        if not own_only:
            for k in kids.get(n, []): walk(k["name"], False)
    walk(name, True)
    if not pts: walk(name, False)
    if not pts: return None
    return [sum(p[k] for p in pts) / len(pts) for k in range(3)]


def rename2(bones, bind_names, ours, max_dist=6.0):
    """Map every name our animations / RCs bind onto the new bones.
       1 same name, when the new bone carries geometry (own or subtree) or the old one carried none;
       2 otherwise the new bone (owning cubes, not yet mapped) whose cube centre is nearest the old bone's (<= max_dist px).
       A same-named but empty new bone that loses its name is renamed <name>_jem. Returns (bones, mapping, missing)."""
    by = {b["name"]: b for b in bones}; ob = {b["name"]: b for b in ours}
    mapping, missing, taken = {}, [], set()
    need = sorted(n for n in bind_names if n in ob or n in by)
    for n in need:
        if n in by and (_subtree_centroid(bones, n) is not None or n not in ob or _subtree_centroid(ours, n) is None):
            mapping[n] = n; taken.add(n)
    for n in need:
        if n in mapping: continue
        oc = _subtree_centroid(ours, n) if n in ob else None
        if oc is None: missing.append(n); continue
        cands = [b["name"] for b in bones if b.get("cubes") and b["name"] not in taken and b["name"] not in bind_names]
        if not cands: missing.append(n); continue
        best = min(cands, key=lambda c: sum((_subtree_centroid(bones, c)[k] - oc[k]) ** 2 for k in range(3)))
        d = sum((_subtree_centroid(bones, best)[k] - oc[k]) ** 2 for k in range(3)) ** 0.5
        if d <= max_dist: mapping[n] = best; taken.add(best)
        else: missing.append(n)
    rev = {v: k for k, v in mapping.items() if k != v}
    displaced = {k for k in mapping if mapping[k] != k and k in by}          # new bones whose name is being taken
    out = []
    for b in bones:
        nb = dict(b)
        nm = b["name"]
        nb["name"] = rev.get(nm, nm + "_jem" if nm in displaced else nm)
        if b.get("parent"):
            p = b["parent"]; nb["parent"] = rev.get(p, p + "_jem" if p in displaced else p)
        out.append(nb)
    names = [b["name"] for b in out]
    dup = {n for n in names if names.count(n) > 1}
    assert not dup, f"duplicate bone names after rename: {dup}"
    return out, {k: v for k, v in mapping.items()}, missing
