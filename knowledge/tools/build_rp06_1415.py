#!/usr/bin/env python3
"""build_rp06_1415.py — D-C283 (R6 witness round). RP-06 Hostile Mobs RP v1.4.15 from v1.4.14:
  1. SILVERFISH on its Patrix model + FreshLX's own animation (his a17 "parts?"). The entity drew the VANILLA silverfish geometry
     (7 body parts + 3 fur boxes, 64x32 layout) wearing the Patrix 512x256 texture laid out for silverfish.jem: the fur boxes
     sampled 72-100 % empty texels and drew as black slabs. Now:
       - geometry.pw_silverfish = Converter B bake of silverfish.jem (jointed head, 5-segment tail, 6 legs, antennae);
       - animation.pw_silverfish.jem = the JEM's whole animation ported (jem_anim_port.py): every assignment as a Molang
         statement in pre_animation, the bones driven by the difference from the baked rest (tail wave, head sway + look, leg
         steps, antenna twitch, breathing, death curl); body2's random 0.5-0.7 size kept as a +-17 % per-individual variation
         around 1 (the pack's size rule owns the base size);
       - the vanilla `move` and `look_at_target` dropped (they drive bones this model does not have; the JEM looks by itself).
  2. PILLAGER: anim_fall / anim_landing aliased (controller.animation.villager.landing plays them; content-log errors in his
     a22 run), as the villager defines them: animation.villager.fall / .landing.
  3. VINDICATOR: two animation-map entries that point at animations defined nowhere (eye_target, attack_face) and that no
     controller plays, removed (the standing animation-name gate's finding).
  4. EVOKER (D-C284): RP-06 now owns minecraft:evocation_illager (the old file named minecraft:evoker, an id Bedrock never uses,
     so the vanilla model drew under our Patrix skin): the vanilla definition (casting, spell particles, celebrating, riding,
     scale 0.9375) on geometry.pw_evoker = Converter B bake of evoker.jem (crossed arms; the casting arms kept for the render
     controller to show), hand locators for the spell particles, its own move controller (the stack's villager controller
     plays names the evoker does not have).
  5. GUARDIAN + ELDER GUARDIAN spikes (D-C284, his "out motion" = the spikes wobble as they come out after it stops): a steady
     moving flag (smoothed horizontal speed, on above 0.9 b/s, off below 0.25) and Java's rates (in 25 %/tick, out 6 %/tick).
manifest 1.4.15, uuid kept. verify: verify_rp06_1415.py."""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import jem_anim_port as P
import molang_lint as ML
from convb import bake

ROOT = Path("/home/claude")
VANILLA_GEO = ROOT / "_intake/bedrock-samples/resource_pack/models/entity/silverfish.geo.json"
CHANGED, ADDED, REMOVED = [], [], []
SF_PREFIX = "pw_sf"
SF_ANIM = "animation.pw_silverfish.jem"


def _sf_port():
    bones, _, _, _ = bake("silverfish")
    return P.port("silverfish", [b["name"] for b in bones], SF_PREFIX, scale_div={"body2": 0.6})


def silverfish_setup(dst):
    """placeholder geometry (the vanilla bones) for the job, the port animation, the entity rewired onto both."""
    v = ML._parse_json(VANILLA_GEO.read_text())                  # legacy 1.8.0 form: {"geometry.silverfish": {...}}
    old = v["geometry.silverfish"]
    ph = {"description": {"identifier": "geometry.pw_silverfish", "texture_width": old.get("texturewidth", 64),
                          "texture_height": old.get("textureheight", 32)}, "bones": copy.deepcopy(old["bones"])}
    pg = dst / "models/entity/pw_silverfish.geo.json"; assert not pg.exists()
    R.wj(pg, {"format_version": "1.16.0", "minecraft:geometry": [ph]}); ADDED.append("models/entity/pw_silverfish.geo.json")
    init, pre, anim, rep = _sf_port()
    pa = dst / "animations/pw_silverfish.animation.json"; assert not pa.exists()
    R.wj(pa, {"format_version": "1.8.0", "animations": {SF_ANIM: anim}}); ADDED.append("animations/pw_silverfish.animation.json")
    pe = dst / "entity/silverfish.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    assert desc["geometry"] == {"default": "geometry.silverfish"}, desc["geometry"]
    assert desc["animations"] == {"look_at_target": "animation.common.look_at_target", "move": "animation.silverfish.move"}, desc["animations"]
    desc["geometry"] = {"default": "geometry.pw_silverfish"}
    desc["animations"] = {"pw_jem": SF_ANIM}
    desc["scripts"] = {"initialize": init, "pre_animation": pre, "animate": ["pw_jem"]}
    R.wj(pe, d); CHANGED.append("entity/silverfish.entity.json")
    return f"placeholder geometry + {SF_ANIM} ({len(pre)} pre_animation statements, {len(anim['bones'])} bones) + entity rewired"


def pillager_alias(dst):
    pe = dst / "entity/pillager.entity.json"; d = R.jl(pe); a = d["minecraft:client_entity"]["description"]["animations"]
    assert "anim_fall" not in a and "anim_landing" not in a and a.get("ctrl_impact") == "controller.animation.villager.landing"
    a["anim_fall"] = "animation.villager.fall"; a["anim_landing"] = "animation.villager.landing"
    R.wj(pe, d); CHANGED.append("entity/pillager.entity.json")
    return "pillager anim_fall / anim_landing -> animation.villager.fall / .landing"


def vindicator_dangling(dst):
    pe = dst / "entity/vindicator.entity.json"; d = R.jl(pe); a = d["minecraft:client_entity"]["description"]["animations"]
    gone = {k: a.pop(k) for k in ("eye_target", "attack_face")}
    assert gone == {"eye_target": "animation.vindicator.eye_target", "attack_face": "animation.vindicator.attack_face"}, gone
    R.wj(pe, d); CHANGED.append("entity/vindicator.entity.json")
    return f"removed {gone}"


# ---------------------------------------------------------------------------------------------------------------------------
# EVOKER (his R6: the game showed the VANILLA evoker). RP-06's entity/evoker.entity.json named `minecraft:evoker`, an id Bedrock
# does not use (the evoker is `minecraft:evocation_illager`), so the file never applied; the vanilla definition drew the vanilla
# 64x64 model under RP-06's Patrix 512 skin. Now RP-06 owns `minecraft:evocation_illager`: the vanilla definition (casting arms +
# spell particles, celebrating, riding, scale 0.9375 = Java's IllagerRenderer) on geometry.pw_evoker = Converter B bake of
# evoker.jem. Our copies of the vanilla arm animations use this geometry's bone names; the crossed-arms pose is the Patrix bake's
# own (Java IllagerModel pose), so `general` only switches which arms show (vanilla re-posed its own 1.8 arms with "- this").
VANILLA_RP = ROOT / "_intake/bedrock-samples/resource_pack"
EVOKER_ANIMS = {
    "animation.pw_evoker.general": {"loop": True, "bones": {"arms": {"scale": 1.0}, "leftArm": {"scale": 0.0}, "rightArm": {"scale": 0.0}}},
    "animation.pw_evoker.casting": {"loop": True, "bones": {
        "arms": {"scale": 0.0},
        "leftArm": {"rotation": ["math.cos(query.life_time * 763.4) * 14.3239 - this", "-this", "-135.0 - this"], "scale": 1.0},
        "rightArm": {"rotation": ["math.cos(query.life_time * 763.4) * 14.3239 - this", "-this", "135.0 - this"], "scale": 1.0}}},
    "animation.pw_evoker.celebrating": {"loop": True, "bones": {
        "arms": {"scale": 0.0},
        "leftArm": {"rotation": ["(math.cos(query.life_time * 800.0) * 2.865)", 180.0, -135.0], "scale": 1.0},
        "rightArm": {"rotation": ["(math.cos(query.life_time * 800.0) * 2.865)", 180.0, 153.0], "scale": 1.0}}},
    "animation.pw_evoker.riding_legs": {"loop": True, "bones": {
        "leftLeg": {"rotation": ["-81.0 - this", "-18.0 - this", "-this"]}, "rightLeg": {"rotation": ["-81.0 - this", "18.0 - this", "-this"]}}},
}
EVOKER_MAP = {"general": "animation.pw_evoker.general", "casting": "animation.pw_evoker.casting",
              "celebrating": "animation.pw_evoker.celebrating", "riding.legs": "animation.pw_evoker.riding_legs"}
# the stack redefines controller.animation.villager.move (RP-07's villager set: anim_idle / anim_walk / anim_run / anim_swim /
# anim_sleep states) — the vanilla evoker only defines `move`, so it would log "can't find animation" (the standing
# animation-name gate caught it). The evoker gets the vanilla controller's behaviour under its own id.
EVOKER_MOVE_CTRL = {"controller.animation.pw_evoker.move": {"initial_state": "default", "states": {
    "default": {"animations": [{"move": "query.modified_move_speed"}]}}}}
# part_visibility only hides the named bone's OWN cubes (L-PARTVIS-OWN): the crossed arms' cubes live on arms_rotation
EVOKER_VIS = [{"*": True}, {"arms_rotation": "!(query.is_casting || query.is_celebrating)"},
              {"leftArm": "query.is_casting || query.is_celebrating"}, {"rightArm": "query.is_casting || query.is_celebrating"}]
import convb_build as CB
CB.EXPLICIT["evocation_illager"] = {"leftArm": "left_arm", "rightArm": "right_arm", "leftLeg": "left_leg", "rightLeg": "right_leg"}
# Java IllagerModel: head > hat, nose; Bedrock's vanilla evoker hangs every part under body (riding.body lifts the whole model)
CB.PARENT_OF["evocation_illager"] = {"hat": "head", "nose": "head", "head": "body", "arms": "body", "leftArm": "body", "rightArm": "body",
                          "leftLeg": "body", "rightLeg": "body"}


def evoker_setup(dst):
    """RP-06 owns minecraft:evocation_illager: the vanilla definition, our geometry id + skin + render controller + arm animations."""
    old = dst / "entity/evoker.entity.json"
    od = R.jl(old)["minecraft:client_entity"]["description"]
    assert od["identifier"] == "minecraft:evoker" and od["textures"] == {"default": "textures/entity/illager/evoker"}, od["identifier"]
    old.unlink(); REMOVED.append("entity/evoker.entity.json")
    v = ML._parse_json((VANILLA_RP / "entity/evocation_illager.entity.json").read_text())
    desc = v["minecraft:client_entity"]["description"]
    assert desc["identifier"] == "minecraft:evocation_illager" and desc["geometry"] == {"default": "geometry.evoker.v1.8"}
    desc["min_engine_version"] = "1.21.0"
    desc["materials"] = {"default": "entity_alphatest"}
    desc["geometry"] = {"default": "geometry.pw_evoker"}
    desc["render_controllers"] = ["controller.render.pw_evoker"]
    for short, aid in EVOKER_MAP.items():
        assert short in desc["animations"], short
        desc["animations"][short] = aid
    assert desc["animations"]["controller_move"] == "controller.animation.villager.move"
    desc["animations"]["controller_move"] = "controller.animation.pw_evoker.move"
    pc = dst / "animation_controllers/pw_evoker.animation_controllers.json"; assert not pc.exists()
    R.wj(pc, {"format_version": "1.10.0", "animation_controllers": EVOKER_MOVE_CTRL}); ADDED.append("animation_controllers/pw_evoker.animation_controllers.json")
    pe = dst / "entity/evocation_illager.entity.json"; assert not pe.exists()
    R.wj(pe, v); ADDED.append("entity/evocation_illager.entity.json")
    pa = dst / "animations/pw_evoker.animation.json"; assert not pa.exists()
    R.wj(pa, {"format_version": "1.8.0", "animations": EVOKER_ANIMS}); ADDED.append("animations/pw_evoker.animation.json")
    # the render controller: the vanilla part visibility on our bone names
    import glob
    hit = None
    for f in glob.glob(str(dst / "render_controllers/*.json")):
        d = R.jl(Path(f))
        if "controller.render.pw_evoker" in d.get("render_controllers", {}): hit = (Path(f), d)
    assert hit, "controller.render.pw_evoker not found"
    rc = hit[1]["render_controllers"]["controller.render.pw_evoker"]
    assert rc == {"geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"]}, rc
    rc["part_visibility"] = EVOKER_VIS
    R.wj(hit[0], hit[1]); CHANGED.append(hit[0].relative_to(dst).as_posix())
    # placeholder geometry (the vanilla 1.8 bones) for the job
    vg = ML._parse_json((VANILLA_RP / "models/entity/evoker.geo.json").read_text())["geometry.evoker.v1.8"]
    ph = {"description": {"identifier": "geometry.pw_evoker", "texture_width": vg.get("texturewidth", 64),
                          "texture_height": vg.get("textureheight", 64)}, "bones": copy.deepcopy(vg["bones"])}
    pg = dst / "models/entity/pw_evoker.geo.json"; assert not pg.exists()
    R.wj(pg, {"format_version": "1.16.0", "minecraft:geometry": [ph]}); ADDED.append("models/entity/pw_evoker.geo.json")
    return "entity/evoker.entity.json (dead id minecraft:evoker) -> entity/evocation_illager.entity.json (vanilla definition on our model)"


def evoker_locators(dst):
    """spell particles leave from locators left_hand / right_hand (vanilla: 10 px below the shoulder pivot) — put them at the
    bottom centre of our arm cubes."""
    p, g = R.geo_file(dst, "geometry.pw_evoker"); by = {b["name"]: b for b in g["bones"]}
    out = {}
    for bone, loc in (("leftArm", "left_hand"), ("rightArm", "right_hand")):
        cubes = [c for b in g["bones"] if b["name"] == bone or _is_under(g["bones"], b["name"], bone) for c in b.get("cubes", [])]
        assert cubes, bone
        lo = min(c["origin"][1] for c in cubes)
        xs = [c["origin"][0] + c["size"][0] / 2 for c in cubes]; zs = [c["origin"][2] + c["size"][2] / 2 for c in cubes]
        pos = [round(sum(xs) / len(xs), 3), round(lo, 3), round(sum(zs) / len(zs), 3)]
        by[bone].setdefault("locators", {})[loc] = pos; out[loc] = pos
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    return f"locators {out}"


def _is_under(bones, name, anc):
    par = {b["name"]: b.get("parent") for b in bones}
    n = par.get(name)
    while n:
        if n == anc: return True
        n = par.get(n)
    return False


# ---------------------------------------------------------------------------------------------------------------------------
# GUARDIAN spikes (his a08 "out motion" = 13:26 YES: the spikes wobble as they extend after it stops). Java (Guardian.aiStep):
# isMoving() is one synced flag from the AI; spikes: moving -> s += (0 - s) * 0.25 per tick, else s += (1 - s) * 0.06; tail:
# moving -> (speed < 0.5 ? 4.0 : speed + (0.5 - speed) * 0.1), else speed + (0.125 - speed) * 0.2. 1.4.13 used a CONTINUOUS
# signal clamp((|v| - 0.4) / 0.8) over horizontal + VERTICAL speed: a guardian coming to rest keeps bobbing around 0.4-0.6 b/s,
# so the target flickered and the fast 0.25 retract kept interrupting the slow 0.06 extension = the wobble. Now a steady flag:
# smoothed HORIZONTAL speed with hysteresis (on above 0.9 b/s, off below 0.25 b/s) and Java's two rates exactly.
GUARDIAN_INIT2 = ["variable.spike_animation_speed = 0.0;", "variable.tail_animation_speed = 0.0;", "variable.tail_swim = 0.0;",
                  "variable.pw_hs = 0.0;", "variable.pw_moving = 0.0;"]
GUARDIAN_PRE2 = [
    "variable.pw_hs = query.life_time < 0.1 ? 0.0 : variable.pw_hs + (query.ground_speed - variable.pw_hs) * (1.0 - math.pow(0.8, query.delta_time * 20.0));",
    "variable.pw_moving = query.life_time < 0.1 ? 0.0 : (variable.pw_moving > 0.5 ? (variable.pw_hs > 0.25 ? 1.0 : 0.0) : (variable.pw_hs > 0.9 ? 1.0 : 0.0));",
    "variable.spike_shake = !query.is_in_water ? math.sin(query.life_time * 2000) / 50 : 0.0;",
    "variable.spike_animation_speed = query.life_time < 0.1 ? 0.0 : (!query.is_in_water ? (math.round(math.sin(query.life_time * 2000)) == 0.0 ? math.random(0.0, 1.0) : variable.spike_animation_speed) : (variable.pw_moving > 0.5 ? variable.spike_animation_speed * math.pow(0.75, query.delta_time * 20.0) : 1.0 - (1.0 - variable.spike_animation_speed) * math.pow(0.94, query.delta_time * 20.0)));",
    "variable.spike_extension = (1.0 - variable.spike_animation_speed) * 0.55;",
    "variable.tail_animation_speed = query.life_time < 0.1 ? 0.0 : (!query.is_in_water ? 2.0 : (variable.pw_moving > 0.5 ? (variable.tail_animation_speed < 0.5 ? 4.0 : variable.tail_animation_speed + (0.5 - variable.tail_animation_speed) * (1.0 - math.pow(0.9, query.delta_time * 20.0))) : variable.tail_animation_speed + (0.125 - variable.tail_animation_speed) * (1.0 - math.pow(0.8, query.delta_time * 20.0))));",
    "variable.tail_swim = query.life_time < 0.1 ? 0.0 : variable.tail_swim + variable.tail_animation_speed * query.delta_time * 20.0;",
    "variable.tail_base_angle = math.sin(variable.tail_swim * 57.29578);",
]


def guardian_moving(dst):
    import build_rp06_1413 as G
    for stem in ("guardian", "elder_guardian"):
        pe = dst / f"entity/{stem}.entity.json"; d = R.jl(pe); s = d["minecraft:client_entity"]["description"]["scripts"]
        assert s["pre_animation"] == G.GUARDIAN_PRE and s["initialize"] == G.GUARDIAN_INIT, stem
        s["initialize"] = GUARDIAN_INIT2; s["pre_animation"] = GUARDIAN_PRE2
        R.wj(pe, d); CHANGED.append(f"entity/{stem}.entity.json")
    return "guardian + elder guardian: steady moving flag (hysteresis 0.9 / 0.25 b/s, horizontal) + Java spike rates 0.25 / 0.06"


def guardian_sim(pre, init, seed=7):
    """20 Hz simulation: 3 s swimming (2.5 b/s), 1 s slowing down, 5 s at rest with drift noise + a vertical bob, then swimming
    again. `spike_extension` is the RETRACTION (0 = spikes fully out, 0.55 = fully in). Returns (direction reversals of the spikes
    while at rest = the wobble, seconds from the start of the slow-down until 95 % out, seconds from moving again until 95 % in)."""
    import math, random
    import molang_eval as ME
    rng = random.Random(seed); env = {}
    for s in init: ME.run(s, env)
    ext, dt, t = [], 0.05, 0.0
    def speed(t):
        if t < 3.0: return 2.5 + rng.uniform(-0.3, 0.3)
        if t < 4.0: return 2.5 * (4.0 - t) + rng.uniform(-0.2, 0.2)
        if t < 9.0: return max(0.0, 0.3 + 0.25 * math.sin(t * 5.0) + rng.uniform(-0.25, 0.25))
        return 2.5 + rng.uniform(-0.3, 0.3)
    while t < 11.0:
        env.update({"q.life_time": t + 1.0, "q.delta_time": dt, "q.ground_speed": speed(t), "q.is_in_water": 1.0,
                    "q.vertical_speed": 0.4 * math.sin(t * 3.0)})
        for s in pre: ME.run(s, env, rng)
        ext.append((t, env["v.spike_extension"])); t += dt
    rest = [e for tt, e in ext if 4.0 <= tt < 9.0]
    d = [b - a for a, b in zip(rest, rest[1:])]
    rev = sum(1 for a, b in zip(d, d[1:]) if a * b < 0 and abs(a) > 1e-4 and abs(b) > 1e-4)
    t_out = next((round(tt - 3.0, 2) for tt, e in ext if tt >= 3.0 and e <= 0.05 * 0.55), None)
    t_in = next((round(tt - 9.0, 2) for tt, e in ext if tt >= 9.0 and e >= 0.95 * 0.55), None)
    return rev, t_out, t_in


def verify_extra(cfg, check):
    NEW = cfg["dst"]
    init, pre, anim, rep = _sf_port()
    import itertools
    cases = [{"age": a, "limb_swing": l, "limb_speed": s, "head_yaw": y, "head_pitch": p}
             for a, l, s, y, p in itertools.product((0.0, 37.0, 211.0), (0.0, 1.3, 4.9), (0.0, 0.3, 1.0), (0.0, 25.0), (0.0, -10.0))]
    cases += [{"age": 50.0, "is_alive": False, "is_hurt": True, "hurt_time": 5.0}, {"age": 80.0, "swing_progress": 0.4}]
    w = P.numeric_check("silverfish", SF_PREFIX, init, pre, anim, cases, scale_div={"body2": 0.6})
    check("SF1 silverfish Molang animation == the JEM (molang_eval vs cem_eval, 110 cases)",
          w["rotation"] < 1e-3 and w["position"] < 1e-4 and w["scale"] < 1e-6, f"max diff {w}")
    shipped = R.jl(NEW / "animations/pw_silverfish.animation.json")["animations"][SF_ANIM]
    geo_bones = {b["name"] for b in R.geo_file(NEW, "geometry.pw_silverfish")[1]["bones"]}
    check("SF2 every animated bone exists in geometry.pw_silverfish; shipped animation == the port",
          set(shipped["bones"]) <= geo_bones and shipped == anim, f"{len(shipped['bones'])} bones; missing {sorted(set(shipped['bones']) - geo_bones)}")
    d = R.jl(NEW / "entity/silverfish.entity.json")["minecraft:client_entity"]["description"]
    check("SF3 entity: Patrix geometry, the port animation, its scripts", d["geometry"] == {"default": "geometry.pw_silverfish"}
          and d["animations"] == {"pw_jem": SF_ANIM} and d["scripts"]["pre_animation"] == pre and d["scripts"]["initialize"] == init, "")
    a = R.jl(NEW / "entity/pillager.entity.json")["minecraft:client_entity"]["description"]["animations"]
    check("PL1 pillager anim_fall / anim_landing", a.get("anim_fall") == "animation.villager.fall" and a.get("anim_landing") == "animation.villager.landing", "")
    # evoker
    ids = {}
    for f in (NEW / "entity").glob("*.json"):
        i = R.jl(f)["minecraft:client_entity"]["description"]["identifier"]; ids.setdefault(i, []).append(f.name)
    ev = R.jl(NEW / "entity/evocation_illager.entity.json")["minecraft:client_entity"]["description"]
    check("EV1 evoker: minecraft:evocation_illager owned once, the dead minecraft:evoker gone",
          ids.get("minecraft:evocation_illager") == ["evocation_illager.entity.json"] and "minecraft:evoker" not in ids, str(ids.get("minecraft:evocation_illager")))
    van = ML._parse_json((VANILLA_RP / "entity/evocation_illager.entity.json").read_text())["minecraft:client_entity"]["description"]
    keep = {k: van[k] for k in ("scripts", "particle_effects", "spawn_egg", "textures")}
    OURS = {**EVOKER_MAP, "controller_move": "controller.animation.pw_evoker.move"}
    check("EV2 evoker keeps the vanilla definition (scale 0.9375, spell particles, controllers, riding) on our model",
          all(ev[k] == v for k, v in keep.items()) and ev["geometry"] == {"default": "geometry.pw_evoker"}
          and {k: v for k, v in ev["animations"].items() if k not in OURS} == {k: v for k, v in van["animations"].items() if k not in OURS}
          and ev["animations"]["controller_move"] == "controller.animation.pw_evoker.move"
          and all(ev["animations"][k] == v for k, v in EVOKER_MAP.items()), "")
    g = R.geo_file(NEW, "geometry.pw_evoker")[1]; gb = {b["name"] for b in g["bones"]}
    locs = {k for b in g["bones"] for k in (b.get("locators") or {})}
    anim_bones = {bn for a in EVOKER_ANIMS.values() for bn in a["bones"]}
    check("EV3 evoker geometry: every bone our arm animations + part visibility name exists, hand locators present",
          anim_bones <= gb and {"head", "body", "leftLeg", "rightLeg"} <= gb and locs == {"left_hand", "right_hand"}, f"missing {sorted(anim_bones - gb)}; locators {sorted(locs)}")
    # guardian
    import build_rp06_1413 as G
    runs = [(guardian_sim(G.GUARDIAN_PRE, G.GUARDIAN_INIT, s), guardian_sim(GUARDIAN_PRE2, GUARDIAN_INIT2, s)) for s in range(1, 6)]
    ok = all(n[0] == 0 and o[0] > 0 and n[1] is not None and n[1] <= 5.0 and n[2] is not None and n[2] <= 1.0 for o, n in runs)
    check("GU1 guardian spikes: no wobble at rest (5 seeded runs), out within 5 s of slowing, in within 1 s of moving",
          ok, "; ".join(f"old rev {o[0]} out {o[1]} in {o[2]} | new rev {n[0]} out {n[1]} in {n[2]}" for o, n in runs[:2]))
    for stem in ("guardian", "elder_guardian"):
        s = R.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]["scripts"]
        check(f"GU2 {stem} scripts == the hysteresis set", s["pre_animation"] == GUARDIAN_PRE2 and s["initialize"] == GUARDIAN_INIT2, "")


CFG = {
    "src": ROOT / "_build/rp06-1414", "dst": ROOT / "_build/rp06-1415", "version": "1.4.15",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.15",
    "desc": ("v1.4.15 (2026-09-29) R6 FIXES (D-C283): the silverfish on its Patrix model with FreshLX's own animation; pillager "
             "falling/landing animation error fixed; two dangling vindicator entries removed; the evoker on its Patrix model "
             "(casting arms + spell particles kept); guardian spikes come out smoothly after it stops. Includes all of 1.4.14."),
    "pre": [silverfish_setup, evoker_setup],
    "jobs": [("silverfish", "silverfish", "default", "silverfish", "default"),
             ("evoker", "evocation_illager", "default", "evoker", "default")],
    "look": {},
    # the port animation is written for the baked rest (Euler add): no frame bones on this model
    "frame_exempt": {"silverfish": {t.split(".")[0] for t, _ in P.assignments(P.rest_of("silverfish")[0])
                                    if not t.startswith(("var.", "varb.", "render."))}},
    # the vanilla silverfish render controller names the vanilla model's segment / fur bones in part_visibility; the Patrix
    # model has none of them, so those visibility entries simply do nothing
    "unbound_ok": {"silverfish": {"bodylayer_0", "bodylayer_1", "bodylayer_2"} | {f"bodypart_{i}" for i in range(7)}}, "placement": {"silverfish": ("ground",), "evoker": ("ground",)},
    "post": [pillager_alias, vindicator_dangling, evoker_locators, guardian_moving],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-06", "ars_stack": [ROOT / "_build/rp07-1421"],
    "verify_hooks": [verify_extra], "report": ROOT / "_docs/convb/build_rp06_1415_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp06_1415_files.json", "w"), indent=1)
