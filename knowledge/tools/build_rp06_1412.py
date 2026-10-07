#!/usr/bin/env python3
"""build_rp06_1412.py — D-C277. RP-06 Hostile Mobs RP v1.4.12 from v1.4.11:
  1. GUARDIAN + ELDER GUARDIAN (his 00:10 "research what the guardians are SUPPOSED to look like" -> 00:18 "the spikes layout looks
     perfect now!" + "yes, let's fix the animations"):
     a. geometry from the Patrix JEMs with the Java RUNTIME spike pose (convb RUNTIME_POSE: Java GuardianModel.setupSpikes position +
        rotation = Mojang's animation.guardian.setup/.spikes numbers): 12 spikes centred on the 12 edge midpoints, pointing out along
        the diagonals, fully extended (resting in water). Everything hangs under `head` (Java head > spikes, eye, tail0 > tail1 >
        tail2) so the look turns the whole guardian.
     b. OUR animations (animations/pw_guardian.animation.json) — the vanilla ones are 1.8-format absolute positions for the vanilla
        rig and RP-07 replaces them with no-op shims anyway:
          animation.pw_guardian.spikes  each spike slides along its own axis (Java: offset k = 1 + cos(age*1.5 + i)*0.01 -
                                        (1 - spikesAnim)*0.55; distance from the centre 11.31 k) — out when resting, in when swimming
          animation.pw_guardian.swim    tail yaw sin(tailAnim) * 9 / 18 / 27 deg (Java 0.05 / 0.10 / 0.15 pi)
          animation.pw_guardian.eye     the eye slides toward its target (Mojang's query.eye_target_x/y_rotation, as vanilla)
     c. scripts: our copies had BOTH time checks backwards (life_time > 0.1 -> speeds held at 0 forever: spikes would have stayed
        pulled in and the tail still) and the tail-speed test inverted (> 0.5): now vanilla's `< 0.1` / Java's `< 0.5`; the smoothing
        runs per game tick (delta_time) so the motion speed does not depend on the frame rate. The unused `setup` is dropped.
  2. CONVERTER B: piglin, piglin brute, bogged (FreshLX re-posed humanoids like the zombified piglin; the Java head > hat tree kept
     so the Patrix head in the hat part carries the head's pose).
  3. HUSK drawn at Java's 1.0625x (HuskRenderer; the husk behaviour has no adult scale).
  manifest 1.4.12, uuid kept. verify: verify_rp06_1412.py."""
import math, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import convb

ROOT = Path("/home/claude")
GUARDIANS = ("guardian", "elder_guardian")
ANIM_FILE = "animations/pw_guardian.animation.json"
TAIL_AMP = {"tail1": 9.0, "tail2": 18.0, "tail3": 27.0}          # Java tail[0..2].yRot = sin(tailAnim) * PI * 0.05 / 0.10 / 0.15
SPIKE_R = math.hypot(8.0, 8.0)                                   # |(SPIKE_X, SPIKE_Y, SPIKE_Z)| = 11.3137 for every spike
PRE = [
    "variable.spike_shake = math.sin(query.life_time * 2000) / 50;",
    "variable.spike_animation_speed = query.life_time < 0.1 ? 0.0 : (!query.is_in_water ? (math.round(math.sin(query.life_time * 2000)) == 0.0 ? math.random(0.0, 1.0) : variable.spike_animation_speed) : (query.is_moving ? variable.spike_animation_speed * math.pow(0.75, query.delta_time * 20.0) : 1.0 - (1.0 - variable.spike_animation_speed) * math.pow(0.94, query.delta_time * 20.0)));",
    "variable.spike_extension = (1.0 - variable.spike_animation_speed) * 0.55;",
    "variable.tail_animation_speed = query.life_time < 0.1 ? 0.0 : (!query.is_in_water ? 2.0 : (query.is_moving ? (variable.tail_animation_speed < 0.5 ? 4.0 : variable.tail_animation_speed + (0.5 - variable.tail_animation_speed) * 0.1) : variable.tail_animation_speed + (0.125 - variable.tail_animation_speed) * 0.2));",
    "variable.tail_swim = query.life_time < 0.1 ? 0.0 : variable.tail_swim + variable.tail_animation_speed * query.delta_time * 20.0;",
    "variable.tail_base_angle = math.sin(variable.tail_swim * 57.29578);",
]
NEW_ANIMS = {"spikes": "animation.pw_guardian.spikes", "swim": "animation.pw_guardian.swim", "move_eye": "animation.pw_guardian.eye"}


def spike_signs(bones):
    """+1 / -1 per spike: the direction of the spike bone's local +Y (the Patrix spike's long axis after the Java rotation) relative
    to OUTWARD (edge midpoint minus body centre). The slide is animated on spineN_rotation, whose parent spineN carries that rotation,
    so a position [0, d, 0] moves the spike along its own axis — no X component, so no X-axis convention question."""
    from equine_compare import bone_affines
    aff = bone_affines(bones); out = {}
    for i in range(12):
        n = f"spine{i + 1}"
        axis = aff[n][0][:, 1]
        centre = np.array([convb._SPK_X[i], 24.0 - (16.0 + convb._SPK_Y[i]), convb._SPK_Z[i]])
        outward = centre - np.array([0.0, 8.0, 0.0]); outward /= np.linalg.norm(outward)
        d = float(axis @ outward); assert abs(abs(d) - 1.0) < 1e-3, (n, d)
        out[n] = 1.0 if d > 0 else -1.0
    return out


def guardian_animations(dst):
    _, g = R.geo_file(dst, R.jl(dst / "entity/guardian.entity.json")["minecraft:client_entity"]["description"]["geometry"]["default"])
    signs = spike_signs(g["bones"])
    _, ge = R.geo_file(dst, R.jl(dst / "entity/elder_guardian.entity.json")["minecraft:client_entity"]["description"]["geometry"]["default"])
    assert spike_signs(ge["bones"]) == signs
    spikes = {}
    for i in range(12):
        n = f"spine{i + 1}"; s = signs[n]
        k1 = f"(0.01 * math.cos((query.life_time * 30.0 + {i}) * 57.29578) - (variable.spike_extension + variable.spike_shake))"
        spikes[f"{n}_rotation"] = {"position": [0.0, f"{s * SPIKE_R:.4f} * {k1}", 0.0]}
    doc = {"format_version": "1.8.0", "animations": {
        "animation.pw_guardian.spikes": {"loop": True, "bones": spikes},
        "animation.pw_guardian.swim": {"loop": True, "bones": {b: {"rotation": [0.0, f"{a} * variable.tail_base_angle", 0.0]} for b, a in TAIL_AMP.items()}},
        "animation.pw_guardian.eye": {"loop": True, "bones": {"eye_part": {"position": ["query.eye_target_x_rotation", "query.eye_target_y_rotation", 0.0]}}}}}
    R.wj(dst / ANIM_FILE, doc)
    for stem in GUARDIANS:
        pe = dst / f"entity/{stem}.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
        desc["animations"].pop("setup", None)
        for k, v in NEW_ANIMS.items(): desc["animations"][k] = v
        sc = desc["scripts"]; sc["pre_animation"] = list(PRE)
        sc["animate"] = [a for a in sc["animate"] if a != "setup"]
        R.wj(pe, d)
    return {"spike_signs": signs, "file": ANIM_FILE}


def husk_scale(dst):
    pe = dst / "entity/husk.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    assert "scale" not in desc.get("scripts", {})
    desc.setdefault("scripts", {})["scale"] = "1.0625"; R.wj(pe, d)
    return {"husk": "1.0625"}


def verify_extra(cfg, check):
    """GA — guardian animations: every animated bone exists in both geometries; simulating the slide at rest (k = 1) leaves every spike
    on its edge midpoint and at the swimming extension (0.55) moves every spike INWARD along its own axis by 6.2 px; the scripts are
    the corrected ones; the husk scale; nothing else in the entities changed."""
    from equine_compare import bone_affines
    from verify_rp07_1415_rp06_1410 import world_boxes
    from convb_build import _shift_subtree
    NEW, OLD = cfg["dst"], cfg["src"]
    doc = R.jl(NEW / ANIM_FILE)["animations"]
    need = {b for a in doc.values() for b in a["bones"]}
    miss = {}
    for stem in GUARDIANS:
        e = R.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        _, g = R.geo_file(NEW, e["geometry"]["default"]); names = {b["name"] for b in g["bones"]}
        miss[stem] = sorted(need - names)
    check("GA1 animated bones exist", not any(miss.values()), f"{len(need)} bones animated; missing {miss}")
    e = R.jl(NEW / "entity/guardian.entity.json")["minecraft:client_entity"]["description"]
    _, g = R.geo_file(NEW, e["geometry"]["default"])
    import copy
    rows, ok = [], True
    for ext in (0.0, 0.55):
        bones = copy.deepcopy(g["bones"])
        for i in range(12):
            n = f"spine{i + 1}_rotation"
            y = doc["animation.pw_guardian.spikes"]["bones"][n]["position"][1]
            s = float(y.split(" * ")[0])
            _shift_subtree(bones, n, [0.0, s * (0.0 - ext), 0.0])          # cos term ~0, no shake: the pure extension
        W = {}
        for x in world_boxes(bones): W.setdefault(x[0], []).append(np.array(x[2]))
        for i in range(12):
            c = [q for nm, bs in W.items() if nm.startswith(f"spine{i + 1}_rotation") for q in bs][0].mean(0)
            dist = float(np.linalg.norm(c - np.array([0.0, 8.0, 0.0])))
            want = SPIKE_R * (1.0 - ext)
            if abs(dist - want) > 0.05: ok = False
            if i in (0, 4, 10): rows.append(f"e{ext}: spine{i + 1} {dist:.2f} (Java {want:.2f})")
    check("GA2 spike slide = Java", ok, "; ".join(rows))
    for stem in GUARDIANS:
        n = R.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        o = R.jl(OLD / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        good = (n["scripts"]["pre_animation"] == PRE and "setup" not in n["animations"] and "setup" not in n["scripts"]["animate"]
                and all(n["animations"][k] == v for k, v in NEW_ANIMS.items())
                and {k: v for k, v in n.items() if k not in ("scripts", "animations", "geometry")} == {k: v for k, v in o.items() if k not in ("scripts", "animations", "geometry")}
                and any("life_time > 0.1" in x for x in o["scripts"]["pre_animation"]))
        check(f"GA3 {stem} scripts + animations", good, f"animate {n['scripts']['animate']}; animations {n['animations']}; old file had the backwards time check: {any('life_time > 0.1' in x for x in o['scripts']['pre_animation'])}")
    n = R.jl(NEW / "entity/husk.entity.json")["minecraft:client_entity"]["description"]
    o = R.jl(OLD / "entity/husk.entity.json")["minecraft:client_entity"]["description"]
    check("S1 husk scale", n["scripts"].get("scale") == "1.0625" and {k: v for k, v in n["scripts"].items() if k != "scale"} == o["scripts"]
          and {k: v for k, v in n.items() if k != "scripts"} == {k: v for k, v in o.items() if k != "scripts"}, f"husk scale {o['scripts'].get('scale')} -> {n['scripts'].get('scale')}")


_ARTIC = {"leftForearm", "rightForearm", "leftShin", "rightShin"}
CFG = {
    "src": ROOT / "_build/rp06-1411", "dst": ROOT / "_build/rp06-1412", "version": "1.4.12",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.12",
    "desc": ("v1.4.12 (2026-09-29) GUARDIANS + CONVERTER B (D-C277): guardian and elder guardian rebuilt from the Patrix models with the "
             "12 spikes where Java puts them (edge midpoints, pointing out on the diagonals), animated like Java - spikes slide in while "
             "swimming and out at rest, the tail sways, the eye follows its target, the body turns to look; piglin, piglin brute and "
             "bogged rebuilt from the Patrix models; husk drawn at Java's 1.0625x. Everything else byte-identical to v1.4.11."),
    "jobs": [("guardian", "guardian", "default", "guardian", "default"), ("elder guardian", "elder_guardian", "default", "elder_guardian", "default"),
             ("piglin", "piglin", "default", "piglin", "default"), ("piglin brute", "piglin_brute", "default", "piglin_brute", "default"),
             ("bogged", "bogged", "default", "bogged", "default")],
    "look": {"guardian": "animation.common.look_at_target", "elder_guardian": "animation.common.look_at_target"},
    "post": [guardian_animations, husk_scale],
    "extra_changed": ["entity/husk.entity.json"],
    "extra_added": [ANIM_FILE],
    "verify_hooks": [verify_extra],
    "unbound_ok": {"piglin": _ARTIC, "piglin brute": _ARTIC, "bogged": _ARTIC},
    # guardians: the reference is VANILLA (body cube y 2..14, centre y 8; the tail runs back to z ~26): the April geometry sat 8 px
    # higher (centre y 16) — above its own 0.85-block hitbox; the Patrix body is a 16-cube centred on y 8 like Java's spike ring
    "frame_exempt": {"guardian": {f"spine{i}_rotation" for i in range(1, 13)}, "elder guardian": {f"spine{i}_rotation" for i in range(1, 13)}},
    "placement": {"guardian": ("centre", 8.0, 8.0), "elder guardian": ("centre", 8.0, 8.0), "piglin": ("ground",), "piglin brute": ("ground",), "bogged": ("ground",)},
    "report": ROOT / "_docs/convb/build_rp06_1412_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
