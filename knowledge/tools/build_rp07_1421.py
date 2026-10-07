#!/usr/bin/env python3
"""build_rp07_1421.py — D-C283 (R6 witness round, his 11:41 + 12:40 answers). RP-07 Neutral Mobs RP v1.4.21 from v1.4.20.

PHASE 1 (mechanisms known, D-C282):
  1. CHICKEN warm + cold rebuilt by Converter B from their own Patrix JEMs (warm_chicken.jem == chicken.jem; cold adds a crest box).
     1.4.17 rebuilt only the entity's 'default' geometry slot, so warm/cold kept the 1.4.12 Converter A geometries without the
     JEM's part rotations (tail plane standing 3 px above the back, tall body box, detached legs — his "every other colour chicken").
  2. ENDERMAN on the Patrix model + skin. RP-07 shipped enderman.tga (64x32, vanilla-like) beside the Patrix enderman.png
     (512x256); inside one pack the .tga wins, so the game drew the old skin (his a16 "confirming we're using the Patrix texture":
     we were not). The Patrix skin is laid out for enderman.jem, so the model is converted too:
       - RP-07 now OWNS the enderman client entity (ownership law): the April entity his movement comes from (StripMine RP 3.0.1
         entity/enderman.v1.8.animation.json — the same animations, controllers and scripts), geometry -> geometry.pw_enderman;
       - geometry.pw_enderman = Converter B bake of enderman.jem bound to the April animation bones (his "movement is perfect");
       - textures/entity/enderman/enderman.tga removed.
PHASE 2 (R6 investigations, D-C283/D-C284):
  3. ENDERMAN jaw: the Patrix JEM's jaw expressions ported (jem_anim_port, only head2/jaw/jaw2; angry = q.is_angry).
  4. DOLPHIN fins: the April swim's -120/+120 fin twist dropped (it cancelled the Java 60/+-120 rest; the flap stays).
  5. SQUID / GLOW SQUID tilt: Java pitches the body toward the swim direction (xBodyRot = query.body_x_rotation); the RP-07 shim
     animation.squid.rotate was a do-nothing placeholder. A/B sign: squid +, glow squid - (his witness picks).
  6. RABBIT head: the head subtree moves to the classic Java head pivot (0, 8, -1): +2 px back, +0.5 px up (the a09 gap).
  7. MOOSHROOM: name-tag probe A-D (see mooshroom_probe); the 0.65 plane shrink was withdrawn (wrong layer, D-C284).
  8. SPIDER texture holes: the scaled cubes' box UV replaced by their unscaled layout as per-face UV (spider_uv, D-C284).
  9. SIZES: the passive + neutral mobs under 0.60 m real + fox / wolf / sheep drawn at the real-size relationship (sizes, D-C284).
manifest 1.4.21, uuid kept. verify: verify_rp07_1421.py."""
import copy, json, sys, zipfile
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML

ROOT = Path("/home/claude")
STRIPMINE_RP = ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"
CHANGED, ADDED, REMOVED = [], [], []


def enderman_setup(dst):
    """the April enderman entity moves into RP-07 (geometry.pw_enderman), a placeholder geometry for the job, the .tga goes."""
    z = zipfile.ZipFile(STRIPMINE_RP)
    ent = ML._parse_json(z.read("entity/enderman.v1.8.animation.json").decode("utf-8-sig"))
    desc = ent["minecraft:client_entity"]["description"]
    assert desc["identifier"] == "minecraft:enderman" and desc["geometry"] == {"default": "geometry.enderman.v1.8"}
    desc["geometry"] = {"default": "geometry.pw_enderman"}
    pe = dst / "entity/enderman.entity.json"; assert not pe.exists()
    R.wj(pe, ent); ADDED.append("entity/enderman.entity.json")
    _, g = R.geo_file(dst, "geometry.enderman.v1.8")
    ph = copy.deepcopy(g); ph["description"]["identifier"] = "geometry.pw_enderman"
    pg = dst / "models/entity/pw_enderman.geo.json"; assert not pg.exists()
    R.wj(pg, {"format_version": "1.16.0", "minecraft:geometry": [ph]}); ADDED.append("models/entity/pw_enderman.geo.json")
    tga = dst / "textures/entity/enderman/enderman.tga"
    assert tga.exists() and (dst / "textures/entity/enderman/enderman.png").exists()
    tga.unlink(); REMOVED.append("textures/entity/enderman/enderman.tga")
    return "entity/enderman.entity.json (April entity, geometry.pw_enderman) + placeholder geometry added; enderman.tga removed"


# Converter B bind for the enderman: the Patrix (Java) part names onto the April rig's bone names, the whole headwear part
# (head2 skin + jaw) as `head` (Java copies the head rotation onto the headwear every frame), the torso box as `body1`
# (the April breathing scale); the arms follow the body as in the April rig
import convb_build as CB
CB.EXPLICIT["enderman"] = {"rightArm": "right_arm", "leftArm": "left_arm", "rightLeg": "right_leg", "leftLeg": "left_leg",
                           "head": "headwear", "body1": "body_y"}
CB.PARENT_OF["enderman"] = {"rightArm": "body", "leftArm": "body"}
APRIL_FRAMES = [("Root", None, [0.0, 4.0, 0.0]), ("upper_body", "Root", [0.0, 30.1, 0.0]), ("lower_body", "Root", [0.0, 4.0, 0.0])]
APRIL_PARENT = {"head": "upper_body", "body": "upper_body", "rightLeg": "lower_body", "leftLeg": "lower_body"}


def enderman_rig(dst):
    """the April rig's empty frame bones (Root > upper_body / lower_body, the April pivots) so its whole-body motion (bob, lean,
    stride sway) keeps driving the Patrix model; re-parenting under rotation-free empty bones moves nothing at rest."""
    p = dst / "models/entity/pw_enderman.geo.json"; d = R.jl(p); g = d["minecraft:geometry"][0]; bones = g["bones"]
    have = {b["name"] for b in bones}
    assert not ({n for n, _, _ in APRIL_FRAMES} & have), have
    by = {b["name"]: b for b in bones}
    for child, parent in APRIL_PARENT.items():
        assert child in by and not by[child].get("parent"), (child, by.get(child, {}).get("parent"))
        by[child]["parent"] = parent
    frames = []
    for name, parent, piv in APRIL_FRAMES:
        f = {"name": name, "pivot": piv, "rotation": [0.0, 0.0, 0.0], "cubes": []}
        if parent: f["parent"] = parent
        frames.append(f)
    g["bones"] = frames + bones
    # (checked D-C283: the jaw2 layer already sits 0.5 px inside the skull — JEM sizeAdd -0.5 -> inflate -0.5 — so skull and
    # jaw never Z-fight; the jaw shows only through the skull's cut-away mouth)
    assert all(c.get("inflate") == -0.5 for c in by["jaw2"].get("cubes", [])), by["jaw2"].get("cubes")
    R.wj(p, d)
    return f"frame bones {[n for n, _, _ in APRIL_FRAMES]} added; {APRIL_PARENT}"


# the Patrix jaw (his 13:01 "yes please do"): FreshLX's skull/jaw expressions ported (jem_anim_port, only head2 / jaw / jaw2),
# the rest of the head motion stays the April animation's. Two readings Bedrock has no query for, rewritten:
#   varb.distance (player within 30 blocks: jaw scale 1 instead of 0.98) -> 1 (always near)
#   var.aggroC's `head.ty<=-15` (Java raises the vanilla head 5 px when the enderman is creepy) -> is_aggressive
EM_PREFIX = "pw_em"
EM_JAW = "animation.pw_enderman.jaw"
EM_RW = [("varb.distance", "1"),
         ("var.aggroC", "clamp(if( frame_counter == var.frame_counter_prev, var.aggroC,  is_aggressive, min(20, var.aggroC +0.03 "
                        "*frame_time*20), max(0, var.aggroC -0.2 *frame_time*20)), if(!is_alive, 1, 0), 1)")]
EM_PX = {"is_aggressive": "q.is_angry", "frame_counter": "q.life_time", "frame_time": "q.delta_time"}


def em_jaw_port(geo_bones):
    import jem_anim_port as P
    return P.port("enderman", geo_bones, EM_PREFIX, only={"head2", "jaw", "jaw2"}, rewrites=EM_RW, params_extra=EM_PX)


def enderman_jaw(dst):
    g = R.geo_file(dst, "geometry.pw_enderman")[1]
    init, pre, anim, rep = em_jaw_port([b["name"] for b in g["bones"]])
    pa = dst / "animations/pw_enderman.animation.json"; assert not pa.exists()
    R.wj(pa, {"format_version": "1.8.0", "animations": {EM_JAW: anim}}); ADDED.append("animations/pw_enderman.animation.json")
    pe = dst / "entity/enderman.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    sc = desc.setdefault("scripts", {})
    assert "animate" not in sc and "initialize" not in sc and "pw_jaw" not in desc["animations"]
    desc["animations"]["pw_jaw"] = EM_JAW
    sc["initialize"] = init; sc["pre_animation"] = list(sc.get("pre_animation", [])) + pre; sc["animate"] = ["pw_jaw"]
    R.wj(pe, d)
    return f"{EM_JAW}: {sorted(anim['bones'])}, {len(pre)} pre_animation statements"


def jaw_frames_check(steps=400, dt=0.05):
    """the jaw port against the JEM, frame by frame (the aggro ramps are recurrences): calm, then angry, then calm again."""
    import math, molang_eval as ME, jem_anim_port as P
    from cem_eval import CemContext, evaluate, assign
    g_bones = [b["name"] for b in R.geo_file(ROOT / "_build/rp07-1421", "geometry.pw_enderman")[1]["bones"]]
    init, pre, anim, rep = em_jaw_port(g_bones)
    jem, rest = P.rest_of("enderman"); rw = dict(EM_RW)
    ctx = CemContext({"id": 1.0}); env = {f"v.{EM_PREFIX}_rid": 0.5, "q.is_alive": 1.0, "q.hurt_time": 0.0}
    worst = 0.0; seen = []
    for i in range(steps):
        angry = 100 <= i < 300
        ctx.params.update({"frame_counter": float(i), "frame_time": dt, "age": i * dt * 20, "is_aggressive": angry})
        for target, expr in P.assignments(jem):
            if target.startswith("render."): continue
            try: assign(target, evaluate(rw.get(target, expr), ctx), ctx)
            except Exception: pass
        env.update({"q.life_time": i * dt, "q.delta_time": dt, "q.is_angry": 1.0 if angry else 0.0})
        for st in pre: ME.run(st, env)
        for part, b in anim["bones"].items():
            m = ctx.model(part); r = rest.get(part, {})
            for kind, chans in (("rotation", ("rx", "ry", "rz")), ("position", ("tx", "ty", "tz")), ("scale", ("sx", "sy", "sz"))):
                for k, ch in enumerate(chans):
                    e = b.get(kind, [0, 0, 0])[k]
                    if not isinstance(e, str): continue
                    got = ME.run(e, dict(env))
                    want = (math.degrees(m[ch] - r.get(ch, 0.0)) if kind == "rotation" else
                            (m[ch] - r.get(ch, 0.0)) * (-1.0 if ch == "ty" else 1.0) if kind == "position" else m[ch])
                    worst = max(worst, abs(got - want))
        if i in (99, 299, 399): seen.append(round(env[f"v.{EM_PREFIX}_aggrob"], 3))
    return worst, seen


# ---------------------------------------------------------------------------------------------------- PHASE 2 (investigations)
DOLPHIN_SWIM = "animation.pw_dolphin.swim"


def dolphin_fins(dst):
    """animation.ar_dolphin.swim (the April swim, weight 1 - speed: slow / idle) adds z -120 / +120 to left_fin / right_fin —
    written for a model whose fins rested at 0. Our fins rest in the Java flipper pose (z +119.9 / -119.9), so the two cancel
    (119.9 - 120 = -0.1 deg) and the fins fold flat on the flanks (his a10 110407 / 110416). pw copy: the +-4 deg flap kept,
    the +-120 dropped; the entity points ar_swim at it."""
    src = R.jl(dst / "animations/ar_dolphin.animation.json")["animations"]["animation.ar_dolphin.swim"]
    a = json.loads(json.dumps(src))
    lf, rf = a["bones"]["left_fin"]["rotation"], a["bones"]["right_fin"]["rotation"]
    assert lf[2] == "math.sin(query.life_time * 3.0) * 4.0 - 120.0" and rf[2] == "math.sin(query.life_time * 3.0 + 1.5) * 4.0 + 120.0", (lf, rf)
    lf[2] = "math.sin(query.life_time * 3.0) * 4.0"; rf[2] = "math.sin(query.life_time * 3.0 + 1.5) * 4.0"
    pa = dst / "animations/pw_dolphin_swim.animation.json"; assert not pa.exists()
    R.wj(pa, {"format_version": "1.8.0", "animations": {DOLPHIN_SWIM: a}}); ADDED.append("animations/pw_dolphin_swim.animation.json")
    pe = dst / "entity/dolphin.entity.json"; d = R.jl(pe); an = d["minecraft:client_entity"]["description"]["animations"]
    assert an["ar_swim"] == "animation.ar_dolphin.swim"; an["ar_swim"] = DOLPHIN_SWIM
    R.wj(pe, d); CHANGED.append("entity/dolphin.entity.json")
    return "dolphin fins: the April swim's -120/+120 fin twist dropped (flap kept)"


# squid tilt: RP-07 shipped animation.squid.rotate as a do-nothing shim, so the squid never pitched toward its swim direction
# (Java: xBodyRot -> -90 when swimming sideways, 0 at rest; Bedrock: query.body_x_rotation). The sign for our model is decided by
# his witness: the SQUID gets +, the GLOW SQUID gets - (TestRunner pushes both sideways; the one that leads with its mantle wins).
SQUID_TILT = {"squid": ("animation.pw_squid.tilt_a", "query.body_x_rotation"),
              "glow_squid": ("animation.pw_squid.tilt_b", "-query.body_x_rotation")}


def squid_tilt(dst):
    anims = {}
    for stem, (aid, x) in SQUID_TILT.items():
        anims[aid] = {"loop": True, "bones": {"body": {"rotation": [x, "variable.squid.swim_rotation ?? 0.0", 0.0]}}}
        pe = dst / f"entity/{stem}.entity.json"; d = R.jl(pe); an = d["minecraft:client_entity"]["description"]["animations"]
        assert an["rotate"] == "animation.squid.rotate", an["rotate"]
        an["rotate"] = aid; R.wj(pe, d); CHANGED.append(f"entity/{stem}.entity.json")
    pa = dst / "animations/pw_squid_tilt.animation.json"; assert not pa.exists()
    R.wj(pa, {"format_version": "1.8.0", "animations": anims}); ADDED.append("animations/pw_squid_tilt.animation.json")
    return "squid tilt restored (A/B sign: squid +, glow squid -)"


RABBIT_HEAD_SHIFT = [0.0, 0.5, 2.0]


def rabbit_head(dst):
    """the head (with ears + nose) sits 2 px ahead of / 0.5 px below the classic Java head pivot (0, 8, -1) the body pose it now
    shares comes from (1.4.20 RUNTIME_POSE) — the gap in his a09 110254. The head subtree moves to the Java pivot."""
    import convb_build as CB
    p, g = R.geo_file(dst, "geometry.rabbit.patrix"); by = {b["name"]: b for b in g["bones"]}
    assert by["head"]["pivot"] == [0.0, 7.5, -3.0], by["head"]["pivot"]
    CB._shift_subtree(g["bones"], "head", RABBIT_HEAD_SHIFT)
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    if p.relative_to(dst).as_posix() not in CHANGED: CHANGED.append(p.relative_to(dst).as_posix())
    return f"rabbit head subtree shifted {RABBIT_HEAD_SHIFT} (pivot now {by['head']['pivot']})"


# MOOSHROOM (his a11 "mushroom layer goes too high") — D-C284: the 0.65 plane shrink first planned here is WITHDRAWN. Our 6
# planes' visible art tops out 4.6-5.4 px above the back; the tall tier in his shots (~12 px, floating pieces) is the GAME's own
# mushroom blocks drawn with the Patrix block textures (RP-01/RP-05 red_mushroom/brown_mushroom). Renaming the anchor bones (red,
# 1.4.20) did not remove them. Instead: a NAME-TAG PROBE. The render controller picks the geometry by query.get_name (the vanilla
# rabbit controller's 'Toast' check proves the query works client-side); unnamed mooshrooms draw exactly as in 1.4.20.
#   'Moo A'  control: today's red (our planes, no anchor bones)
#   'Moo B'  no planes, no anchor bones            -> the game's layer alone, loose
#   'Moo C'  no planes, anchors in the vanilla frame (body [0,19,2] / head [0,20,-8], unrotated) -> the game's layer alone, anchored
#   'Moo D'  our planes + anchors scaled to 1 % by an animation -> is the game's layer hidden? (A-R10-1)
PROBE_NAMES = {"Moo A": "Geometry.default", "Moo B": "Geometry.bare", "Moo C": "Geometry.bare_anchored", "Moo D": "Geometry.anchored"}
PROBE_ANIM = "animation.pw_mooshroom.probe_hide"
PROBE_RC_GEOMETRY = ("query.get_name == 'Moo A' ? Geometry.default : (query.get_name == 'Moo B' ? Geometry.bare : "
                     "(query.get_name == 'Moo C' ? Geometry.bare_anchored : (query.get_name == 'Moo D' ? Geometry.anchored : "
                     "Array.geos[math.clamp(query.variant, 0, 1)])))")
VANILLA_ANCHOR = {"body": [0.0, 19.0, 2.0], "head": [0.0, 20.0, -8.0]}      # geometry.mooshroom.v2 bone pivots (runtime: unrotated)


def mooshroom_probe(dst):
    _, red = R.geo_file(dst, "geometry.pw_mooshroom")
    _, anch = R.geo_file(dst, "geometry.pw_mooshroom_anchored")
    mush = {b["name"] for b in red["bones"] if b["name"].startswith("mushroom")}
    assert mush == {"mushroom1", "mushroom2", "mushroom3"}, mush
    assert not any(b.get("parent") in mush for b in red["bones"] + anch["bones"])           # nothing hangs under a mushroom
    bare = copy.deepcopy(red); bare["description"]["identifier"] = "geometry.pw_mooshroom_bare"
    bare["bones"] = [b for b in bare["bones"] if b["name"] not in mush]
    bare_a = copy.deepcopy(anch); bare_a["description"]["identifier"] = "geometry.pw_mooshroom_bare_anchored"
    bare_a["bones"] = [b for b in bare_a["bones"] if b["name"] not in mush]
    by = {b["name"]: b for b in bare_a["bones"]}
    for n, piv in VANILLA_ANCHOR.items():
        assert not by[n].get("cubes") and not any(by[n].get("rotation") or [0]), by[n]
        by[n]["pivot"] = list(piv)
    for g_, fname in ((bare, "pw_mooshroom_bare.geo.json"), (bare_a, "pw_mooshroom_bare_anchored.geo.json")):   # one geometry per file
        pg = dst / "models/entity" / fname; assert not pg.exists()
        R.wj(pg, {"format_version": "1.16.0", "minecraft:geometry": [g_]}); ADDED.append(f"models/entity/{fname}")
    pa = dst / "animations/pw_mooshroom_probe.animation.json"; assert not pa.exists()
    hide = "query.get_name == 'Moo D' ? 0.01 : 1.0"
    R.wj(pa, {"format_version": "1.8.0", "animations": {PROBE_ANIM: {"loop": True, "bones": {"body": {"scale": hide}, "head": {"scale": hide}}}}})
    ADDED.append("animations/pw_mooshroom_probe.animation.json")
    pe = dst / "entity/mooshroom.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    assert set(desc["geometry"]) == {"default", "anchored", "baby"}, desc["geometry"]
    desc["geometry"]["bare"] = "geometry.pw_mooshroom_bare"; desc["geometry"]["bare_anchored"] = "geometry.pw_mooshroom_bare_anchored"
    assert "pw_probe_hide" not in desc["animations"]
    desc["animations"]["pw_probe_hide"] = PROBE_ANIM; desc["scripts"]["animate"].append("pw_probe_hide")
    R.wj(pe, d); CHANGED.append("entity/mooshroom.entity.json")
    pr = dst / "render_controllers/pw_mooshroom.render.json"; rc = R.jl(pr); c = rc["render_controllers"]["controller.render.pw_mooshroom"]
    assert c["geometry"] == "Array.geos[math.clamp(query.variant, 0, 1)]", c["geometry"]
    c["geometry"] = PROBE_RC_GEOMETRY
    R.wj(pr, rc); CHANGED.append("render_controllers/pw_mooshroom.render.json")
    return f"name-tag probe {sorted(PROBE_NAMES)}: 2 probe geometries + {PROBE_ANIM}; unnamed mooshrooms unchanged"


# SPIDER — D-C284 SCALED BOX-UV (his 13:26 "exact squares … the hit box is there, but no texture is applied to certain spots"):
# the spider's neck group is scaled 0.8 at rest (spider.jem neck.s* = 1 + var.scale); Converter B baked that into the box SIZES
# but kept box UV, and box UV derives every face rectangle from the size — so each face sampled the texture layout shrunk to
# 80 %: 90 of 246 faces reach into the sheet's transparent gaps (142.6 px², 6.6 % of the surface; the abdomen's side face is
# 38.5 % see-through = an exact rectangle of nothing). convb.bake now freezes the unscaled layout as per-face UV before scaling.
# The fix is SURGICAL: a rebuild through the job would also add walk frame bones (the RP-06 entity now plays the ported Patrix
# walk, built for today's bones), so only the `uv` of the 41 scaled cubes is replaced; every other byte of the geometry stays.
def spider_uv(dst):
    import convb
    p, g = R.geo_file(dst, "geometry.spider")
    mapping = dict(json.load(open(ROOT / "_docs/convb/build_1419_report.json"))["spider"]["mapping"])   # shipped name <- JEM name
    bones, tw, th, info = convb.bake("spider")
    assert [tw, th] == [g["description"]["texture_width"], g["description"]["texture_height"]]
    new_by = {b["name"]: b for b in bones}
    swapped = 0
    for b in g["bones"]:
        src = new_by.get(mapping.get(b["name"], b["name"]))
        cubes = b.get("cubes", [])
        if not cubes: continue
        assert src is not None and len(src["cubes"]) == len(cubes), b["name"]
        for c, s in zip(cubes, src["cubes"]):
            assert all(abs(x - y) < 1e-6 for x, y in zip(c["size"], s["size"])), (b["name"], c["size"], s["size"])
            assert abs((c.get("inflate") or 0) - (s.get("inflate") or 0)) < 1e-6, b["name"]
            if isinstance(c.get("uv"), list) and isinstance(s.get("uv"), dict):
                c["uv"] = s["uv"]; swapped += 1
            else:
                assert c.get("uv") == s.get("uv"), (b["name"], c.get("uv"), s.get("uv"))
    assert swapped == len(info["perface_from_scale"]) == 41, (swapped, len(info["perface_from_scale"]))
    d = R.jl(p); d["minecraft:geometry"] = [x if x["description"]["identifier"] != "geometry.spider" else g for x in d["minecraft:geometry"]]
    R.wj(p, d); CHANGED.append(p.relative_to(dst).as_posix())
    return f"geometry.spider: {swapped} scaled cubes now carry their unscaled layout as per-face UV (nothing else changed)"


# SIZES (D-C284, his 12:40 rulings; tools/size_rule.py): the passive + neutral mobs under 0.60 m real, plus fox / wolf / sheep,
# drawn at the real-size relationship with his character (5'10" = 1.875 blocks) as the yardstick — resource pack only (client
# scripts.scale), hitboxes unchanged; larger mobs and hostile ones wait for the hitbox work.
SIZE_STACK = [ROOT / "_build/rp08-148", ROOT / "_build/rp06-1415", ROOT / "_build/rp05-51"]
SIZE_PLAN = []


def sizes(dst):
    import size_rule as SR
    rows = SR.plan(dst, SIZE_STACK); SIZE_PLAN[:] = rows
    json.dump(rows, open(ROOT / "_docs/convb/size_plan_1421.json", "w"), indent=1)
    done = []
    for r in rows:
        if r["factor"] == 1.0: continue
        pe = dst / f"entity/{r['stem']}.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
        sc = desc.setdefault("scripts", {})
        sc["scale"] = SR.scaled_script(sc.get("scale"), r["factor"])
        R.wj(pe, d)
        if f"entity/{r['stem']}.entity.json" not in CHANGED: CHANGED.append(f"entity/{r['stem']}.entity.json")
        done.append(f"{r['stem']} x{r['factor']}")
    return "client scale: " + ", ".join(done)


def verify_extra(cfg, check):
    """D-C283/D-C284 checks for the Phase-2 fixes (the standard B/C/D/E/F/G lines cover the three Converter B jobs)."""
    import copy, numpy as np
    from PIL import Image
    OLD, NEW = cfg["src"], cfg["dst"]
    ids = {}
    for f in (NEW / "entity").glob("*.json"):
        ids.setdefault(ML._parse_json(f.read_text(encoding="utf-8-sig"))["minecraft:client_entity"]["description"]["identifier"], []).append(f.name)
    en = R.jl(NEW / "entity/enderman.entity.json")["minecraft:client_entity"]["description"]
    check("EN1 enderman: owned once, geometry.pw_enderman, the .tga gone (the Patrix .png draws)",
          ids.get("minecraft:enderman") == ["enderman.entity.json"] and en["geometry"] == {"default": "geometry.pw_enderman"}
          and not (NEW / "textures/entity/enderman/enderman.tga").exists() and (NEW / "textures/entity/enderman/enderman.png").exists(), "")
    worst, seen = jaw_frames_check()
    check("EN2 enderman jaw == the Patrix JEM frame by frame (calm -> angry -> calm, 400 frames)", worst < 1e-3 and seen == [0.0, 1.0, 0.0],
          f"max diff {worst:.2e}; aggro ramp at frames 99/299/399 {seen}")
    sw = R.jl(NEW / "animations/pw_dolphin_swim.animation.json")["animations"][DOLPHIN_SWIM]["bones"]
    dn = R.jl(NEW / "entity/dolphin.entity.json")["minecraft:client_entity"]["description"]["animations"]
    check("DO1 dolphin: fin twist dropped, flap kept, entity plays it", "120" not in json.dumps(sw["left_fin"]) + json.dumps(sw["right_fin"])
          and "math.sin" in sw["left_fin"]["rotation"][2] and dn["ar_swim"] == DOLPHIN_SWIM, "")
    tl = R.jl(NEW / "animations/pw_squid_tilt.animation.json")["animations"]
    ok = all(R.jl(NEW / f"entity/{s}.entity.json")["minecraft:client_entity"]["description"]["animations"]["rotate"] == a
             and tl[a]["bones"]["body"]["rotation"][0] == x for s, (a, x) in SQUID_TILT.items())
    check("SQ1 squid (+) / glow squid (-) tilt on query.body_x_rotation", ok, "")
    _, ro = R.geo_file(OLD, "geometry.rabbit.patrix"); _, rn = R.geo_file(NEW, "geometry.rabbit.patrix")
    import convb_build as CB
    sub = set(CB._subtree(ro["bones"], "head")); bad = []
    for a, b in zip(ro["bones"], rn["bones"]):
        if a["name"] not in sub:
            if a != b: bad.append(a["name"])
            continue
        want = copy.deepcopy(a); want["pivot"] = [round(a["pivot"][k] + RABBIT_HEAD_SHIFT[k], 6) for k in range(3)]
        for c in want.get("cubes", []): c["origin"] = [round(c["origin"][k] + RABBIT_HEAD_SHIFT[k], 6) for k in range(3)]
        got = copy.deepcopy(b); got["pivot"] = [round(v, 6) for v in got["pivot"]]
        for c in got.get("cubes", []): c["origin"] = [round(v, 6) for v in c["origin"]]
        if want != got: bad.append(a["name"])
    check("RB1 rabbit: head subtree moved +0.5 up / +2 back (pivot = classic Java 0, 8, -1), every other bone identical",
          not bad and [round(v, 4) for v in {b["name"]: b for b in rn["bones"]}["head"]["pivot"]] == [0.0, 8.0, -1.0], f"{len(sub)} head-subtree bones; mismatched {bad}")
    rc = None
    for f in (NEW / "render_controllers").glob("*.json"):
        d = R.jl(f).get("render_controllers", {})
        if "controller.render.pw_mooshroom" in d: rc = d["controller.render.pw_mooshroom"]
    md = R.jl(NEW / "entity/mooshroom.entity.json")["minecraft:client_entity"]["description"]
    bare = R.geo_file(NEW, "geometry.pw_mooshroom_bare")[1]; bare_a = R.geo_file(NEW, "geometry.pw_mooshroom_bare_anchored")[1]
    bb = {b["name"]: b for b in bare_a["bones"]}
    ok = (rc["geometry"] == PROBE_RC_GEOMETRY and rc["geometry"].endswith("Array.geos[math.clamp(query.variant, 0, 1)])))")
          and not any(b["name"].startswith("mushroom") for b in bare["bones"] + bare_a["bones"])
          and not any(b["name"] in ("body", "head") for b in bare["bones"])
          and [bb["body"]["pivot"], bb["head"]["pivot"]] == [VANILLA_ANCHOR["body"], VANILLA_ANCHOR["head"]]
          and md["geometry"].get("bare") == "geometry.pw_mooshroom_bare" and md["geometry"].get("bare_anchored") == "geometry.pw_mooshroom_bare_anchored"
          and md["animations"].get("pw_probe_hide") == PROBE_ANIM and "pw_probe_hide" in md["scripts"]["animate"])
    check("MO1 mooshroom probe: names A-D pick 4 set-ups, unnamed mooshrooms keep the 1.4.20 choice", ok, "")
    _, so = R.geo_file(OLD, "geometry.spider"); _, sn = R.geo_file(NEW, "geometry.spider")
    a, b = copy.deepcopy(so["bones"]), copy.deepcopy(sn["bones"]); nuv = 0
    for x, y in zip(a, b):
        for c1, c2 in zip(x.get("cubes", []), y.get("cubes", [])):
            nuv += c1.get("uv") != c2.get("uv"); c1.pop("uv", None); c2.pop("uv", None)
    import face_alpha_census as F
    alpha = np.asarray(Image.open(NEW / "textures/entity/spider/spider.png").convert("RGBA"))[..., 3]
    holes = tot = 0.0
    for bo in sn["bones"]:
        for c in bo.get("cubes", []):
            s = c["size"]
            for name, rect in F.face_rects(c, bo.get("mirror", False)).items():
                dims = {"north": (s[0], s[1]), "south": (s[0], s[1]), "east": (s[2], s[1]), "west": (s[2], s[1]), "up": (s[0], s[2]), "down": (s[0], s[2])}[name]
                op, _ = F.opaque_fraction(alpha, rect, 64, 32); tot += dims[0] * dims[1]; holes += (1 - op) * dims[0] * dims[1]
    check("SP1 spider: only the UVs of the 41 scaled cubes changed; no see-through face area left", a == b and nuv == 41 and holes < 0.5,
          f"{nuv} cubes re-mapped; see-through {holes:.1f} of {tot:.1f} px²")
    import size_rule as SR
    after = SR.plan(NEW, SIZE_STACK); off = []
    for r in after:
        if r["action"].startswith("grow (capped"): continue            # the pufferfish: +20 % is the cap, not the target
        if abs(r["current_blocks"] / r["target_blocks"] - 1.0) > 0.08: off.append(f"{r['stem']} {r['current_blocks']} vs {r['target_blocks']}")
    check("SZ1 sizes: every planned mob now measures within 8 % of its real-size target (5'10\" = 1.875 blocks)", not off,
          "; ".join(f"{r['stem']} {r['current_blocks']}" for r in after) + (f" | OFF {off}" if off else ""))


CFG = {
    "src": ROOT / "_build/rp07-1420", "dst": ROOT / "_build/rp07-1421", "version": "1.4.21",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.21",
    "desc": ("v1.4.21 (2026-09-29) R6 FIXES (D-C283): warm + cold chickens built like the white one; the enderman on its Patrix "
             "model and skin (same movement) with the Patrix jaw; dolphin fins, squid tilt, rabbit head fixed; spider texture holes fixed; mooshroom name-tag probe A-D; small mobs + fox and sheep drawn at real-size "
             "proportions to a 5'10\" player."),
    "pre": [enderman_setup],
    "jobs": [("chicken warm", "chicken", "warm", "warm_chicken", "warm"),
             ("chicken cold", "chicken", "cold", "cold_chicken", "cold"),
             ("enderman", "enderman", "default", "enderman", "default")],
    "look": {"chicken": R.LOOK_ID},
    # the April face rig (eyelids / eyeballs / eye layers / jaw pieces top/top2) has no Patrix counterpart: the Patrix face is
    # painted on the head and its jaw is a JEM expression (not ported) — those April face channels have nothing to move
    "unbound_ok": {"enderman": {"eye_layer_x", "eye_layer_x2", "eyeball_left", "eyeball_right", "eyelid_layer_left",
                                "eyelid_layer_right", "eyelid_left", "eyelid_right", "facial", "left", "right", "top", "top2"}},
    "placement": {"chicken warm": ("ground",), "chicken cold": ("ground",), "enderman": ("ground",)},
    "post": [enderman_rig, enderman_jaw, dolphin_fins, squid_tilt, rabbit_head, mooshroom_probe, spider_uv, sizes],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-07", "ars_stack": [ROOT / "_build/rp06-1415"],
    "verify_hooks": [verify_extra], "report": ROOT / "_docs/convb/build_rp07_1421_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp07_1421_files.json", "w"), indent=1)
