#!/usr/bin/env python3
"""build_rp06_1420.py — FA-1 (D-C294/D-C296/D-C298/D-C299). RP-06 Hostile Mobs RP v1.4.20 from v1.4.19.
The mobs whose Patrix 1.21.11 128x textures sat on Mojang's models (L-UV-LAYOUT, R12 z08 warden) + the FA-1 flyers, each on
its Converter B geometry (`geometry.pw_<mob>`, unshadowable):
  WARDEN    vanilla animations on the Patrix model (torso -> body; Java parents restored); 5 layers on one geometry:
            tendrils layer = the Patrix sheet's tendril faces (Java draws the tendril glow from the main texture);
            bioluminescent layer = the Patrix LabPBR emission (warden_s alpha, normalised to its strongest texel) — the Patrix
            bioluminescent sheet itself is empty (Patrix glows through LabPBR); heart + spots = the Patrix sheets.
            Client scale 1.2 kept (his ruling; hitbox vanilla).
  CREAKING  vanilla animations; an `upperBody` bone at Mojang's pivot carries head, body and arms (Java upper_body); eyes layer
  ENDERMITE the Patrix JEM animation ported (jointed body, legs, tail); the vanilla section wiggle dropped
  VEX       JEM port with Java VexModel arm SEEDS (charging / held-item poses the JEM reads), rightItem / leftItem hand points,
            the Patrix 256 px vex + charging sheets (the old 128 px copies sat at a path Bedrock never reads)
  PHANTOM   JEM port (unwrapped body yaw for the banking roll); the Patrix eye overlay merged into the one texture
            (alpha 18 on the eye texels = the emissive marker vanilla's phantom.tga uses)
  BLAZE     JEM port with Java BlazeModel stick SEEDS (3 rings orbiting + bobbing; stick1 carries the body)
  BREEZE    vanilla animations; head + rods from breeze.jem, the three wind layers from breeze_wind.jem on their own
            geometries (vanilla's scrolling render controllers kept); eyes layer = the Patrix LabPBR emission
Texture tier: Patrix 1.21.11 128x (his 21:5x ruling). manifest 1.4.20, uuid kept. verify: verify_rp06_1420.py."""
import copy, io, itertools, json, math, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import convb_build as CB
import jem_anim_port as P
import molang_lint as ML
from convb import bake

ROOT = Path("/home/claude")
VRP = ROOT / "_intake/bedrock-samples/resource_pack"
ZIP = ROOT / "_intake/zips/Patrix_1.21.11_128x_mobs.zip"
CHANGED, ADDED, REMOVED = [], [], []
_Z = None


def ptex(rel):
    """a Patrix 1.21.11 128x texture (path under textures/entity/) as an RGBA image"""
    global _Z
    _Z = _Z or zipfile.ZipFile(ZIP)
    return Image.open(io.BytesIO(_Z.read(f"assets/minecraft/textures/entity/{rel}"))).convert("RGBA")


def put_png(dst, rel, img):
    p = dst / rel; existed = p.exists()
    if existed:                                   # identical pixels already shipped -> keep the file (and the diff) untouched
        old = np.asarray(Image.open(p).convert("RGBA")); new = np.asarray(img.convert("RGBA"))
        if old.shape == new.shape and (old == new).all(): return
    p.parent.mkdir(parents=True, exist_ok=True); img.save(p, optimize=True)
    (CHANGED if existed else ADDED).append(rel)


def vgeo(ident):
    """a Mojang geometry (new or legacy format) -> (bones, tw, th)"""
    for p in (VRP / "models/entity").rglob("*.json"):
        t = p.read_text(encoding="utf-8")
        if ident not in t: continue
        d = ML._parse_json(t)
        for g in d.get("minecraft:geometry", []) or []:
            if g["description"]["identifier"] == ident:
                return copy.deepcopy(g["bones"]), g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)
        for k, g in d.items():
            if isinstance(g, dict) and k.split(":")[0] == ident and g.get("bones"):
                return copy.deepcopy(g["bones"]), g.get("texturewidth", 64), g.get("textureheight", 64)
    raise KeyError(ident)


def placeholder(dst, new_id, from_id, fname):
    bones, tw, th = vgeo(from_id)
    pg = dst / f"models/entity/{fname}.geo.json"; assert not pg.exists(), pg
    R.wj(pg, {"format_version": "1.16.0", "minecraft:geometry": [
        {"description": {"identifier": new_id, "texture_width": tw, "texture_height": th}, "bones": bones}]})
    ADDED.append(f"models/entity/{fname}.geo.json")


def new_entity(dst, stem, mutate):
    """RP-06 owns minecraft:<stem> for the first time: Mojang's definition, mutated; returns the description"""
    v = ML._parse_json((VRP / f"entity/{stem}.entity.json").read_text(encoding="utf-8"))
    desc = v["minecraft:client_entity"]["description"]
    mutate(desc)
    # D-C285 (FMT): scripts.animate / initialize are not valid before format 1.10.0; the legacy `animation_controllers` list
    # (1.8.0) is gone in 1.10.0 — whatever a mob keeps from it moves into animations + scripts.animate inside mutate()
    if (desc.get("scripts") or {}).get("animate") or (desc.get("scripts") or {}).get("initialize"):
        if tuple(int(x) for x in v["format_version"].split(".")) < (1, 10, 0): v["format_version"] = "1.10.0"
        assert "animation_controllers" not in desc, (stem, "legacy animation_controllers left")
    pe = dst / f"entity/{stem}.entity.json"; assert not pe.exists(), pe
    R.wj(pe, v); ADDED.append(f"entity/{stem}.entity.json")
    return desc


def emission_layer(colour, spec, norm=True):
    """LabPBR emission (specular alpha 1..254) -> a Bedrock glow layer: the colour texels, alpha = emission strength
    (normalised so the sheet's strongest emitter is opaque)"""
    c = np.asarray(colour.convert("RGBA")).astype(np.float32); s = np.asarray(spec.convert("RGBA"))
    if s.shape != c.shape: s = np.asarray(spec.convert("RGBA").resize((c.shape[1], c.shape[0]), Image.NEAREST))
    a = s[..., 3].astype(np.float32)
    em = (a > 0) & (a < 255) & (c[..., 3] > 16)
    top = float(a[em].max()) if em.any() else 1.0
    out = np.zeros_like(c); out[..., :3] = c[..., :3]
    out[..., 3] = np.where(em, np.clip(a / (top if norm else 254.0) * 255.0, 0, 255), 0)
    return Image.fromarray(out.astype(np.uint8), "RGBA"), int(em.sum()), top


def port_anim(dst, stem, anim_id, init, pre, anim, extra=None):
    pa = dst / f"animations/pw_{stem}.animation.json"; assert not pa.exists()
    R.wj(pa, {"format_version": "1.8.0", "animations": {anim_id: anim, **(extra or {})}}); ADDED.append(f"animations/pw_{stem}.animation.json")


# ======================================================================================================================= WARDEN
CB.EXPLICIT["warden"] = {"body": "torso"}
CB.PARENT_OF["warden"] = {"head": "body", "left_ribcage": "body", "right_ribcage": "body", "left_arm": "body", "right_arm": "body",
                          "left_tendril": "head", "right_tendril": "head"}
WARDEN_TENDRIL_RECTS = [(100, 60, 116, 76), (82, 60, 98, 76)]     # Patrix warden.jem tendril faces (128 units)


def warden_setup(dst):
    pe = dst / "entity/warden.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    assert desc["geometry"] == {"default": "geometry.warden"} and desc["scripts"]["scale"] == "1.2", (desc["geometry"], desc["scripts"].get("scale"))
    desc["geometry"] = {"default": "geometry.pw_warden"}
    R.wj(pe, d); CHANGED.append("entity/warden.entity.json")
    placeholder(dst, "geometry.pw_warden", "geometry.warden", "pw_warden")
    base = Image.open(dst / "textures/entity/warden/warden.png").convert("RGBA")
    assert (np.asarray(base) == np.asarray(ptex("warden/warden.png"))).all(), "RP-06 warden.png is not the Patrix 1.21.11 sheet"
    s = base.size[0] // 128; out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    for u0, v0, u1, v1 in WARDEN_TENDRIL_RECTS:
        box = (u0 * s, v0 * s, u1 * s, v1 * s); out.paste(base.crop(box), box[:2])
    put_png(dst, "textures/entity/warden/warden_tendrils.png", out)
    bio, n, top = emission_layer(base, ptex("warden/warden_s.png"))
    put_png(dst, "textures/entity/warden/warden_bioluminescent_layer.png", bio)
    return f"entity -> geometry.pw_warden; tendrils sheet from the Patrix tendril faces; bioluminescent sheet = Patrix emission ({n} texels, strongest {top:.0f}/254 -> opaque)"


# ===================================================================================================================== CREAKING
CB.EXPLICIT["creaking"] = {"leftArm": "left_arm", "rightArm": "right_arm", "leftLeg": "left_leg", "rightLeg": "right_leg"}


def creaking_setup(dst):
    def mut(desc):
        assert desc["geometry"] == {"default": "geometry.creaking"}
        desc["geometry"] = {"default": "geometry.pw_creaking"}
    new_entity(dst, "creaking", mut)
    placeholder(dst, "geometry.pw_creaking", "geometry.creaking", "pw_creaking")
    return "RP-06 owns minecraft:creaking (Mojang definition) on geometry.pw_creaking"


def creaking_upper_body(dst):
    """Java CreakingModel: root > upper_body > head, body, arms. The JEM has no upper_body (vanilla part, animated by the
    walk); our `upperBody` = a rotation-0 bone at Mojang's pivot [-1, 19, 0] that the head, body and arms hang from."""
    p, g = R.geo_file(dst, "geometry.pw_creaking"); names = {b["name"] for b in g["bones"]}
    assert "upperBody" not in names and {"head", "body", "leftArm", "rightArm"} <= names, names
    kids = [b for b in g["bones"] if b["name"] in ("head", "body", "leftArm", "rightArm")]
    assert all(not b.get("parent") for b in kids), [(b["name"], b.get("parent")) for b in kids]
    for b in kids: b["parent"] = "upperBody"
    g["bones"].insert(0, {"name": "upperBody", "pivot": [-1.0, 19.0, 0.0], "rotation": [0.0, 0.0, 0.0], "cubes": []})
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    return "upperBody [-1, 19, 0] over head, body, leftArm, rightArm (rest pose unchanged: rotation 0, absolute pivots)"


# ==================================================================================================================== ENDERMITE
EM = {"prefix": "pw_em", "anim": "animation.pw_endermite.jem", "scale_div": {"body2": 0.6}}


def em_port():
    b, _, _, _ = bake("endermite")
    return P.port("endermite", [x["name"] for x in b], EM["prefix"], scale_div=EM["scale_div"])


def endermite_setup(dst):
    init, pre, anim, rep = em_port()
    port_anim(dst, "endermite", EM["anim"], init, pre, anim)
    def mut(desc):
        assert desc["geometry"] == {"default": "geometry.endermite"} and desc["animations"] == {"move": "animation.endermite.move"}, desc["animations"]
        desc["geometry"] = {"default": "geometry.pw_endermite"}
        assert desc.pop("animation_controllers") == [{"move": "controller.animation.endermite.move"}]
        desc["animations"] = {"pw_jem": EM["anim"]}
        desc["scripts"] = {"initialize": init, "pre_animation": pre, "animate": ["pw_jem"]}
    new_entity(dst, "endermite", mut)
    placeholder(dst, "geometry.pw_endermite", "geometry.endermite", "pw_endermite")
    return f"RP-06 owns minecraft:endermite on geometry.pw_endermite + {EM['anim']} ({len(pre)} statements, {len(anim['bones'])} bones)"


# ========================================================================================================================== VEX
VX = {"prefix": "pw_vx", "anim": "animation.pw_vex.jem"}
PX_COMMON = {"is_riding": "q.is_riding", "death_time": "q.death_ticks", "frame_time": "q.delta_time", "frame_counter": "q.life_time",
             "pos_y": "q.position(1)"}
_F = "(math.cos(q.life_time * 20.0 * 5.5) * 0.1)"
_CH, _RH, _LH = "q.is_charging", "q.is_item_equipped(0)", "q.is_item_equipped(1)"
_EMPTY = f"(!{_RH} && !{_LH})"
# Java VexModel.setupAnim (the values the JEM reads before it assigns the arms): zRot = +-(pi/5 + f); charging ->
# setArmsCharging: empty hands both arms (-1.2217305, +-pi/12, -+(0.47123888 + f)); a held item -> that arm (3.6651914, ...)
VEX_SEEDS = {"right_arm": {"rx": f"{_CH} ? ({_EMPTY} ? -1.2217305 : ({_RH} ? 3.6651914 : 0.0)) : 0.0",
                           "ry": f"({_CH} && ({_EMPTY} || {_RH})) ? 0.2617994 : 0.0",
                           "rz": f"({_CH} && ({_EMPTY} || {_RH})) ? (-0.47123888 - {_F}) : (0.62831853 + {_F})"},
             "left_arm": {"rx": f"{_CH} ? ({_EMPTY} ? -1.2217305 : ({_LH} ? 3.6651914 : 0.0)) : 0.0",
                          "ry": f"({_CH} && ({_EMPTY} || {_LH})) ? -0.2617994 : 0.0",
                          "rz": f"({_CH} && ({_EMPTY} || {_LH})) ? (0.47123888 + {_F}) : -(0.62831853 + {_F})"}}


def vex_java(c):
    age = c.get("age", 0.0); f = math.cos(math.radians(age * 5.5)) * 0.1
    ch, rh, lh = c.get("_ch", 0), c.get("_rh", 0), c.get("_lh", 0); empty = not rh and not lh
    r = {"rx": 0.0, "ry": 0.0, "rz": math.pi / 5 + f}; l = {"rx": 0.0, "ry": 0.0, "rz": -(math.pi / 5 + f)}
    if ch:
        if empty or rh: r = {"rx": -1.2217305 if empty else 3.6651914, "ry": 0.2617994, "rz": -0.47123888 - f}
        if empty or lh: l = {"rx": -1.2217305 if empty else 3.6651914, "ry": -0.2617994, "rz": 0.47123888 + f}
    return {"right_arm": r, "left_arm": l}


def common_env(c):
    return {"q.is_riding": float(c.get("is_riding", False)), "q.death_ticks": c.get("death_time", 0.0), "q.delta_time": c.get("frame_time", 0.05),
            "q.position(1.0)": c.get("pos_y", 64.0)}


def vex_env(c):
    return {**common_env(c), "q.is_charging": float(c.get("_ch", 0)), "q.is_item_equipped(0.0)": float(c.get("_rh", 0)),
            "q.is_item_equipped(1.0)": float(c.get("_lh", 0))}


def vx_port():
    b, _, _, _ = bake("vex")
    return P.port("vex", [x["name"] for x in b], VX["prefix"], params_extra=PX_COMMON, seeds=VEX_SEEDS)


def vex_setup(dst):
    init, pre, anim, rep = vx_port()
    port_anim(dst, "vex", VX["anim"], init, pre, anim)
    def mut(desc):
        assert desc["geometry"] == {"default": "geometry.vex.v1.8"}, desc["geometry"]
        desc["geometry"] = {"default": "geometry.pw_vex"}
        desc["textures"] = {"default": "textures/entity/illager/vex", "charging": "textures/entity/illager/vex_charging"}
        desc.pop("animation_controllers")          # humanoid look / vex charge / idle: bone animations the JEM replaces
        desc["animations"] = {"pw_jem": VX["anim"]}
        desc["scripts"] = {"initialize": init, "pre_animation": pre, "animate": ["pw_jem"], "scale": "1.0"}
    new_entity(dst, "vex", mut)
    placeholder(dst, "geometry.pw_vex", "geometry.vex.v1.8", "pw_vex")
    put_png(dst, "textures/entity/illager/vex.png", ptex("illager/vex.png"))
    put_png(dst, "textures/entity/illager/vex_charging.png", ptex("illager/vex_charging.png"))
    return f"RP-06 owns minecraft:vex on geometry.pw_vex + {VX['anim']} ({len(pre)} statements); Patrix 256 px vex sheets"


def hand_points(dst, gid, pairs):
    """rightItem / leftItem at the bottom centre of the arm's cubes (world rest), child of the arm, rotation 0"""
    from verify_rp07_1415_rp06_1410 import world_boxes
    p, g = R.geo_file(dst, gid); bones = g["bones"]; names = {b["name"] for b in bones}
    out = {}
    for item, arm in pairs:
        assert item not in names and arm in names, (gid, item, arm)
        sub = set(CB._subtree(bones, arm))
        Pts = np.array([q for x in world_boxes(bones) if x[0] in sub for q in x[2]])
        # world_boxes are in the geometry's own frame (Bedrock file coordinates); a child's pivot is absolute in that frame
        piv = [round(float((Pts[:, 0].min() + Pts[:, 0].max()) / 2), 3), round(float(Pts[:, 1].min()), 3), round(float((Pts[:, 2].min() + Pts[:, 2].max()) / 2), 3)]
        bones.append({"name": item, "parent": arm, "pivot": piv, "rotation": [0.0, 0.0, 0.0], "cubes": []}); out[item] = piv
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    return out


def vex_hands(dst):
    return f"vex hand points {hand_points(dst, 'geometry.pw_vex', [('rightItem', 'right_arm'), ('leftItem', 'left_arm')])}"


# ====================================================================================================================== PHANTOM
PH = {"prefix": "pw_ph", "anim": "animation.pw_phantom.jem", "pitch": "animation.pw_phantom.pitch",
      "dust": "controller.animation.pw_phantom.wing_dust", "dust_file": "animation_controllers/pw_phantom.animation_controllers.json"}
# Java PhantomRenderer.setupRotations pitches the WHOLE model by the entity's xRot about its origin (Mojang's base_pose does the
# same on its body bone: rotation -q.target_x_rotation); the JEM adds its own body2 pitch on top when slow
PH_PITCH = {"loop": True, "bones": {"pw_pitch": {"rotation": ["-q.target_x_rotation", 0.0, 0.0]}}}
# rot_y: Java's yaw is continuous; Bedrock's body yaw wraps at +-180 -> unwrap it (the JEM banks on rot_y minus a 20-frame
# delayed copy; a wrap would read as a full-turn roll)
PH_UNWRAP = ["v.pw_ph_dyaw = q.body_y_rotation - (v.pw_ph_pyaw ?? q.body_y_rotation);",
             "v.pw_ph_dyaw = v.pw_ph_dyaw > 180.0 ? v.pw_ph_dyaw - 360.0 : (v.pw_ph_dyaw < -180.0 ? v.pw_ph_dyaw + 360.0 : v.pw_ph_dyaw);",
             "v.pw_ph_yawu = (v.pw_ph_yawu ?? q.body_y_rotation) + v.pw_ph_dyaw;",
             "v.pw_ph_pyaw = q.body_y_rotation;"]
PX_PH = {"rot_y": "(v.pw_ph_yawu * 0.0174532925)"}


def ph_port():
    b, _, _, _ = bake("phantom")
    init, pre, anim, rep = P.port("phantom", [x["name"] for x in b], PH["prefix"], params_extra=PX_PH)
    return init, PH_UNWRAP + pre, anim, rep


PH_DUST_DOC = {"format_version": "1.10.0", "animation_controllers": {"controller.animation.pw_phantom.wing_dust": {"initial_state": "default", "states": {
    "default": {"particle_effects": [{"effect": "wing_dust", "locator": "left_wing"}, {"effect": "wing_dust", "locator": "right_wing"}]}}}}}


def phantom_wing_locators(dst):
    """D-C301: Mojang's wing-tip locators (left_wing on the left tip, right_wing on the right) at the OUTER END of our Patrix tips
    (Mojang: [21, 26, 0] / [-22, 24, 0] on its tips, whose cubes end at x +-21..22; ours end at +-21.51, top y 7, same z 0)"""
    p, g = R.geo_file(dst, "geometry.pw_phantom"); by = {b["name"]: b for b in g["bones"]}
    kids = lambda n: [n] + [k for b in g["bones"] if b.get("parent") == n for k in kids(b["name"])]
    out = {}
    for bone, loc, side in (("left_wing_tip2", "left_wing", 1), ("right_wing_tip2", "right_wing", -1)):
        xs, ys = [], []           # the tip's cubes (the right tip's sit in its split child right_wing_tip_sub_0), bind-pose coordinates
        for c in [c for n in kids(bone) for c in by[n].get("cubes", [])]:
            o, sz = c["origin"], c["size"]
            xs += [o[0], o[0] + sz[0]]; ys += [o[1], o[1] + sz[1]]
        tip = [round(max(xs) if side > 0 else min(xs), 4), round(max(ys), 4), 0.0]
        by[bone]["locators"] = {**(by[bone].get("locators") or {}), loc: tip}; out[loc] = tip
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    return f"phantom wing locators {out}"


def phantom_texture():
    """Patrix phantom.png + phantom_eyes.png -> one RGBA sheet: eye texels = the overlay colour at alpha 18 (vanilla
    phantom.tga marks its glowing eyes with alpha 18 under the `phantom` material), cut-outs stay alpha 0"""
    base = ptex("phantom.png"); eyes = ptex("phantom_eyes.png")
    b = np.asarray(base).copy(); e = np.asarray(eyes)
    m = e[..., 3] > 16
    b[m, :3] = e[m, :3]; b[m, 3] = 18
    return Image.fromarray(b, "RGBA"), int(m.sum())


def phantom_setup(dst):
    init, pre, anim, rep = ph_port()
    port_anim(dst, "phantom", PH["anim"], init, pre, anim, extra={PH["pitch"]: PH_PITCH})
    def mut(desc):
        assert desc["geometry"] == {"default": "geometry.phantom"}, desc["geometry"]
        desc["geometry"] = {"default": "geometry.pw_phantom"}
        desc.pop("animation_controllers", None)    # base_pose / move: bone animations the JEM + our pitch replace
        desc["animations"] = {"pw_jem": PH["anim"], "pw_pitch": PH["pitch"], "pw_dust": PH["dust"]}
        desc["scripts"] = {"initialize": init, "pre_animation": pre, "animate": ["pw_jem", "pw_pitch", "pw_dust"], "should_update_effects_offscreen": "1.0"}
    new_entity(dst, "phantom", mut)
    # D-C301: Mojang's base_pose controller also played the wing dust (minecraft:phantom_trail_particle at the wing-tip locators);
    # dropping base_pose dropped the trail -> our own controller plays the particles only (the pitch is pw_pitch's job)
    R.wj(dst / PH["dust_file"], PH_DUST_DOC); ADDED.append(PH["dust_file"])
    placeholder(dst, "geometry.pw_phantom", "geometry.phantom", "pw_phantom")
    img, n = phantom_texture(); put_png(dst, "textures/entity/phantom.png", img)
    return f"RP-06 owns minecraft:phantom on geometry.pw_phantom + {PH['anim']} ({len(pre)} statements); eye glow merged ({n} texels, alpha 18)"


# ======================================================================================================================== BLAZE
BZ = {"prefix": "pw_bz", "anim": "animation.pw_blaze.jem"}
# the bake leaves stick1 (a vanilla part the JEM never assigns; Java moves it every frame) at the origin while the body under it
# cancels the stick's TEMPLATE position (-7, -2, -7): the whole blaze sat 7 px off-centre in x and z and 2 px low. Shift = minus
# that seed (CONV-1): body pivot lands on Mojang's stick pivot (0, 24, 0); rings = Mojang's heights (A 18-26, C 5-13)
CB.MODEL_OFFSET["blaze"] = [-7.0, 2.0, -7.0133]
_AGE = "(q.life_time * 20.0)"


def _deg(x): return f"(({x}) * 57.2957795)"


def blaze_seed_exprs():
    """Java BlazeModel.setupAnim, stick i (0-based) -> OptiFine stick<i+1>.tx/ty/tz (Java model units)"""
    out = {}
    for i in range(12):
        if i < 4: f, r, y = f"({_AGE} * 3.14159265 * -0.1 + {i})", 9.0, f"(-2.0 + math.cos({_deg(f'({2 * i} + {_AGE}) * 0.25')}))"
        elif i < 8: f, r, y = f"(0.78539816 + {_AGE} * 3.14159265 * 0.03 + {i - 4})", 7.0, f"(2.0 + math.cos({_deg(f'({2 * i} + {_AGE}) * 0.25')}))"
        else: f, r, y = f"(0.47123894 + {_AGE} * 3.14159265 * -0.05 + {i - 8})", 5.0, f"(11.0 + math.cos({_deg(f'({1.5 * i} + {_AGE}) * 0.5')}))"
        out[f"stick{i + 1}"] = {"tx": f"(math.cos({_deg(f)}) * {r})", "ty": y, "tz": f"(math.sin({_deg(f)}) * {r})"}
    return out


def blaze_java(c):
    age = c.get("age", 0.0); out = {}
    for i in range(12):
        if i < 4: f, r, y = age * math.pi * -0.1 + i, 9.0, -2.0 + math.cos((2 * i + age) * 0.25)
        elif i < 8: f, r, y = math.pi / 4 + age * math.pi * 0.03 + (i - 4), 7.0, 2.0 + math.cos((2 * i + age) * 0.25)
        else: f, r, y = 0.47123894 + age * math.pi * -0.05 + (i - 8), 5.0, 11.0 + math.cos((1.5 * i + age) * 0.5)
        out[f"stick{i + 1}"] = {"tx": math.cos(f) * r, "ty": y, "tz": math.sin(f) * r}
    return out


def bz_port():
    b, _, _, _ = bake("blaze")
    return P.port("blaze", [x["name"] for x in b], BZ["prefix"], params_extra={"is_burning": "q.is_on_fire"},
                  seeds=blaze_seed_exprs(), extra_driven={"stick1": {"tx", "ty", "tz"}})


def blaze_setup(dst):
    init, pre, anim, rep = bz_port()
    port_anim(dst, "blaze", BZ["anim"], init, pre, anim)
    def mut(desc):
        assert desc["geometry"] == {"default": "geometry.blaze"} and desc["render_controllers"] == ["controller.render.blaze"], desc
        desc["geometry"] = {"default": "geometry.pw_blaze"}
        ac = desc.pop("animation_controllers")
        assert ac == [{"move": "controller.animation.blaze.move"}, {"flame": "controller.animation.blaze.flame"}], ac
        desc["animations"] = {"pw_jem": BZ["anim"], "flame": "controller.animation.blaze.flame"}   # the flame particles stay
        desc["scripts"] = {"initialize": init, "pre_animation": pre, "animate": ["pw_jem", "flame"]}
        desc["render_controllers"] = ["controller.render.pw_blaze"]
    new_entity(dst, "blaze", mut)
    placeholder(dst, "geometry.pw_blaze", "geometry.blaze", "pw_blaze")
    # vanilla: {"*": body}, {"head": head}; the Patrix head cubes live on bone2 (head2 > bone1 > bone2)
    rc = {"format_version": "1.8.0", "render_controllers": {"controller.render.pw_blaze": {
        "geometry": "Geometry.default", "materials": [{"*": "Material.body"}, {"bone2": "Material.head"}], "textures": ["Texture.default"]}}}
    pr = dst / "render_controllers/pw_blaze.render_controllers.json"; assert not pr.exists()
    R.wj(pr, rc); ADDED.append("render_controllers/pw_blaze.render_controllers.json")
    return f"RP-06 owns minecraft:blaze on geometry.pw_blaze + {BZ['anim']} ({len(pre)} statements incl. 36 Java stick seeds)"


# ======================================================================================================================= BREEZE
CB.EXPLICIT["breeze"] = {}
CB.PARENT_OF["breeze"] = {"head": "body", "rods": "body"}   # Java BreezeModel: body > head, rods (the JEM list is flat)
WIND = {"tornado_top": "wind_top", "tornado_mid": "wind_middle", "tornado_bottom": "wind_bottom"}


def breeze_setup(dst):
    def mut(desc):
        assert desc["geometry"] == {"default": "geometry.breeze", "breeze_eyes": "geometry.breeze_eyes", "breeze_wind_top": "geometry.breeze_wind_top",
                                    "breeze_wind_mid": "geometry.breeze_wind_mid", "breeze_wind_bottom": "geometry.breeze_wind_bottom"}, desc["geometry"]
        desc["geometry"] = {"default": "geometry.pw_breeze", "breeze_eyes": "geometry.pw_breeze_eyes", "breeze_wind_top": "geometry.pw_breeze_wind_top",
                            "breeze_wind_mid": "geometry.pw_breeze_wind_mid", "breeze_wind_bottom": "geometry.pw_breeze_wind_bottom"}
    new_entity(dst, "breeze", mut)
    placeholder(dst, "geometry.pw_breeze", "geometry.breeze", "pw_breeze")
    body = ptex("breeze/breeze.png"); put_png(dst, "textures/entity/breeze/breeze.png", body)
    put_png(dst, "textures/entity/breeze/breeze_wind.png", ptex("breeze/breeze_wind.png"))
    eyes, n, top = emission_layer(body, ptex("breeze/breeze_s.png"))
    put_png(dst, "textures/entity/breeze/breeze_eyes.png", eyes)
    return f"RP-06 owns minecraft:breeze (5 geometries); Patrix 256 px body, wind sheet, eyes = Patrix emission ({n} texels)"


def breeze_layers(dst):
    """eyes + three wind geometries. Each keeps the whole skeleton (vanilla does: the animations drive every geometry) with
    only its own cubes. Wind = breeze_wind.jem (Java BreezeModel wind_body > wind_bottom > wind_mid > wind_top, restored)."""
    p, g = R.geo_file(dst, "geometry.pw_breeze"); base = g["bones"]
    wb, wtw, wth, info = bake("breeze_wind")
    for ours, jem in WIND.items(): CB._rename(wb, jem, ours)
    wb.insert(0, {"name": "tornado_body", "pivot": [0.0, 0.0, 0.0], "rotation": [0.0, 0.0, 0.0], "cubes": []})
    for b in wb:
        if b["name"] == "tornado_bottom": b["parent"] = "tornado_body"
    CB.reparent(wb, "tornado_mid", "tornado_bottom"); CB.reparent(wb, "tornado_top", "tornado_mid")
    def strip(bones, keep):
        out = copy.deepcopy(bones)
        for b in out:
            if b["name"] not in keep: b["cubes"] = []
        return out
    head_sub = set(CB._subtree(base, "head"))
    docs = {"geometry.pw_breeze_eyes": (strip(base, head_sub), g["description"]["texture_width"], g["description"]["texture_height"])}
    for ours in WIND:
        sub = set(CB._subtree(wb, ours)) - (set(CB._subtree(wb, {"tornado_bottom": "tornado_mid", "tornado_mid": "tornado_top"}.get(ours, "__none"))) if ours != "tornado_top" else set())
        docs[f"geometry.pw_breeze_wind_{ours.split('_')[1]}"] = (strip(wb, sub), wtw, wth)
    n = {}
    for gid, (bones, tw, th) in docs.items():
        fname = gid.replace("geometry.", "")
        pg = dst / f"models/entity/{fname}.geo.json"; assert not pg.exists()
        R.wj(pg, {"format_version": "1.16.0", "minecraft:geometry": [{"description": {"identifier": gid, "texture_width": tw, "texture_height": th,
              "visible_bounds_width": 3, "visible_bounds_height": 3, "visible_bounds_offset": [0, 1, 0]}, "bones": bones}]})
        ADDED.append(f"models/entity/{fname}.geo.json"); n[gid] = sum(len(b.get("cubes", [])) for b in bones)
    return f"breeze layers {n}"


# ========================================================================================================================= JOBS
JOBS = [("warden", "warden", "default", "warden", "default"),
        ("creaking", "creaking", "default", "creaking", "default"),
        ("endermite", "endermite", "default", "endermite", "default"),
        ("vex", "vex", "default", "vex", "default"),
        ("phantom", "phantom", "default", "phantom", "default"),
        ("blaze", "blaze", "default", "blaze", "default"),
        ("breeze", "breeze", "default", "breeze", "default")]
PRE = [warden_setup, creaking_setup, endermite_setup, vex_setup, phantom_setup, blaze_setup, breeze_setup]
def phantom_pitch_root(dst):
    """`pw_pitch` at the entity origin, parent of every top-level bone (rest pose unchanged: rotation 0, absolute pivots)"""
    p, g = R.geo_file(dst, "geometry.pw_phantom")
    tops = [b for b in g["bones"] if not b.get("parent")]
    for b in tops: b["parent"] = "pw_pitch"
    g["bones"].insert(0, {"name": "pw_pitch", "pivot": [0.0, 0.0, 0.0], "rotation": [0.0, 0.0, 0.0], "cubes": []})
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    return f"pw_pitch over {[b['name'] for b in tops]}"


def textures_list(dst):
    """D-C301: the new warden tendrils sheet joins textures/textures_list.json (the other warden sheets are listed there)"""
    tl = dst / "textures/textures_list.json"; lst = R.jl(tl); add = [x for x in ("textures/entity/warden/warden_tendrils",) if x not in lst]
    if add: lst += add; R.wj(tl, lst); CHANGED.append("textures/textures_list.json")
    return f"textures_list + {add}"


RETRO_VB = {"evoker": ("evocation_illager", "default", "geometry.pw_evoker"), "silverfish": ("silverfish", "default", "geometry.pw_silverfish")}


def retro_bounds(dst):
    """D-C303 (his ruling "Fix in FA-1"): the L-VISBOUNDS fix for the two Converter B mobs delivered before it (pw_evoker, pw_silverfish):
    their culling box only (description); bones untouched"""
    out = {}
    for label, (stem, gkey, gid) in RETRO_VB.items():
        p, g = R.geo_file(dst, gid); d = R.jl(p)
        for gg in d["minecraft:geometry"]:
            if gg["description"]["identifier"] == gid:
                gg["description"] = {"identifier": gid, **R.bounds(gg["description"], gg["bones"], R.van_box(stem, gkey))}
                out[label] = {k: gg["description"][k] for k in R.VB_KEYS}
        R.wj(p, d); CHANGED.append(str(p.relative_to(dst)))
    return f"culling boxes {out}"


POST = [creaking_upper_body, vex_hands, breeze_layers, phantom_pitch_root, phantom_wing_locators, textures_list, retro_bounds]
HUMANOID = {"leftarm", "leftleg", "rightarm", "rightleg", "waist"}   # Mojang's warden entity plays humanoid base_pose/swimming (no-ops)
UNBOUND_OK = {"warden": HUMANOID, "creaking": {"upperBody"}, "breeze": {"tornado_body", "tornado_top", "tornado_mid", "tornado_bottom", "eyes"},
              "phantom": {"pw_pitch"}}   # upperBody / pw_pitch are added by the post hooks (verified in the final geometry by E)


def _jem_parts(j):
    return {t.split(".")[0] for t, _ in P.assignments(P.rest_of(j)[0]) if not t.startswith(("var.", "varb.", "render."))}


FRAME_EXEMPT = {m: _jem_parts(m) for m in ("endermite", "vex", "phantom", "blaze")}
FRAME_EXEMPT["blaze"] |= {"stick1"}
PLACEMENT = {"warden": ("ground",), "creaking": ("ground",), "endermite": ("ground",),
             # flyers: within 6 px of the Mojang geometry's box centre (y, z) — vex.v1.8 (5.5, 0), phantom (24, 0.5), blaze (22, 0), breeze (19.2, -0.9)
             "vex": ("centre", 5.5, 0.0), "phantom": ("centre", 4.0, 0.5), "blaze": ("centre", 17.5, 0.0), "breeze": ("centre", 19.2, -0.9)}
# phantom: Mojang's geometry sits 20 px higher and its base_pose animation moves the body down 20 (= Java's renderer offset),
# so the reference is 24 - 20 = 4; blaze: Mojang's animated rings span y 5..26 + head to 28 -> centre ~17
PNG_CHECKED = ["textures/entity/breeze/breeze.png", "textures/entity/breeze/breeze_eyes.png", "textures/entity/breeze/breeze_wind.png",
               "textures/entity/illager/vex.png", "textures/entity/illager/vex_charging.png", "textures/entity/phantom.png",
               "textures/entity/warden/warden_bioluminescent_layer.png"]   # whole-sheet swaps: verify T1-T5

CFG = {
    "src": ROOT / "_build/rp06-1419", "dst": ROOT / "_build/rp06-1420", "version": "1.4.20",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.20",
    "desc": ("v1.4.20 (2026-09-29) FA-1: the warden, creaking, endermite, blaze, breeze, vex and phantom on their Patrix models "
             "(their Patrix skins were drawn on Mojang's models - the warden's 'UV mapping error'); vex holds its sword; the "
             "phantom's eyes and the warden's and breeze's Patrix glow. Includes all of 1.4.19."),
    "pre": PRE, "jobs": JOBS, "look": {}, "frame_exempt": FRAME_EXEMPT, "unbound_ok": UNBOUND_OK, "placement": PLACEMENT,
    "post": POST, "png_checked_elsewhere": PNG_CHECKED, "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-06", "ars_stack": [ROOT / "_build/rp07-1425"],
    "verify_hooks": [], "report": ROOT / "_docs/convb/build_rp06_1420_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp06_1420_files.json", "w"), indent=1)
