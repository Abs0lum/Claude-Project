#!/usr/bin/env python3
"""build_rp07_1412.py — RP-07 AbsolutRealism Neutral Mobs RP v1.4.12: the P0 WIRING build (D-C259 / D-C260).

What it does (all ADDITIVE on top of the 1.4.11 tree; no 1.4.11 file is deleted except the two dead-id entity files):
  1. copies _build/rp07-1411 -> _build/rp07-1412
  2. NEW unshadowable geometries  models/entity/pw_<mob>.geo.json  (identifier geometry.pw_<mob>) copied from the
     shipped .patrix geometries (RP-06/RP-08 1.4.6 ship same-path copies of wolf/cat/polar_bear/chicken.geo.json, so
     the .patrix identifiers inside them can vanish depending on pack order — new file names cannot be shadowed)
     cow + mooshroom: head reparented under body (neck/head marriage)
  3. NEW ambient animations  animations/pw_<mob>_ambient_v2.animation.json (id animation.pw_<mob>.ambient):
     body bob 0.5 -> 0.15 cube, body tilt 2.0 -> 0.6 deg, the same bob copied onto every ROOT bone (head, legs) so
     nothing separates; constant leg yaw dropped.
  4. rewired client entities (format 1.26.0, min_engine_version 1.21.0, material entity_alphatest, Patrix textures,
     .patrix geometry through the pw_ copies, ar_* + pw ambient + headtrack):
     wolf fox panda polar_bear cat ocelot goat camel chicken; tropical_fish -> tropicalfish (vanilla id, material
     'tropicalfish' 2-sampler RC); zombified_piglin -> zombie_pigman (vanilla id) with the Patrix 512x512 texture;
     donkey/mule chests on query.is_chested; cow/mooshroom on the fixed geometry + ambient v2.
  5. textures: frog x3 replaced by the clean Patrix 1.21.11 source files (0 magenta px); piglin/zombified_piglin.png
     added; cat (12) + chicken (3) copied to textures/entity/pw_cat/ + pw_chicken/ (paths RP-06/RP-08 shadow).
  6. manifest 1.4.12.
Run: python3 tools/build_rp07_1412.py   (then tools/verify_rp07_1412.py, then package)
"""
import copy, json, os, re, shutil, sys, time

SRC = "_build/rp07-1411"
DST = "_build/rp07-1412"
PATRIX = "_intake/patrix128mobs"           # range-read from Patrix_1.21.11_128x_mobs.zip (Drive)
VERSION = [1, 4, 12]
REPORT = {"geometries": [], "ambients": [], "entities": [], "textures": [], "removed": [], "notes": []}

def jload(p):
    with open(p) as f:
        return json.load(f)

def jsave(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)

def log(msg):
    with open("_logs/phase_log.md", "a") as f:
        f.write(f"[{time.strftime('%H:%M')} CT 09-27] BUILD 1.4.12 — {msg}\n")

# ----------------------------------------------------------------------------------------------------------------
# 1. copy tree
# ----------------------------------------------------------------------------------------------------------------
if os.path.exists(DST):
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)
log(f"tree copied {SRC} -> {DST}")

# ----------------------------------------------------------------------------------------------------------------
# 2. unshadowable geometries
# ----------------------------------------------------------------------------------------------------------------
# new name -> (source file, source identifier)
GEOS = {
    "pw_wolf":          ("wolf.geo.json",            "geometry.wolf.patrix"),
    "pw_fox":           ("fox.geo.json",             "geometry.fox.patrix"),
    "pw_panda":         ("panda.geo.json",           "geometry.panda.patrix"),
    "pw_polar_bear":    ("polar_bear.geo.json",      "geometry.polar_bear.patrix"),
    "pw_cat":           ("cat.geo.json",             "geometry.cat.patrix"),
    "pw_goat":          ("goat.geo.json",            "geometry.goat.patrix"),
    "pw_camel":         ("camel.geo.json",           "geometry.camel.patrix"),
    "pw_chicken":       ("chicken.geo.json",         "geometry.chicken.patrix"),
    "pw_chicken_warm":  ("warm_chicken.geo.json",    "geometry.warm_chicken.patrix"),
    "pw_chicken_cold":  ("cold_chicken.geo.json",    "geometry.cold_chicken.patrix"),
    "pw_tropicalfish_a": ("tropical_fish_a.geo.json", "geometry.tropicalfish_a.patrix"),
    "pw_tropicalfish_b": ("tropical_fish_b.geo.json", "geometry.tropicalfish_b.patrix"),
    "pw_zombie_pigman": ("zombified_piglin.geo.json", "geometry.zombified_piglin.patrix"),
    "pw_cow":           ("cow.geo.json",             "geometry.cow.patrix"),
    "pw_mooshroom":     ("mooshroom.geo.json",       "geometry.mooshroom.patrix"),
    "pw_donkey":        ("donkey.geo.json",          "geometry.donkey.patrix"),
    "pw_mule":          ("mule.geo.json",            "geometry.mule.patrix"),
}
REPARENT_HEAD = {"pw_cow", "pw_mooshroom"}   # head becomes a child of body (was a root bone)

def find_geo(path, ident):
    j = jload(path)
    for g in j.get("minecraft:geometry", []):
        if g["description"]["identifier"] == ident:
            return j.get("format_version", "1.12.0"), g
    raise SystemExit(f"geometry {ident} not in {path}")

geo_bones = {}
for new, (src, ident) in GEOS.items():
    fv, g = find_geo(f"{SRC}/models/entity/{src}", ident)
    g = copy.deepcopy(g)
    g["description"]["identifier"] = f"geometry.{new}"
    if new in REPARENT_HEAD:
        for b in g["bones"]:
            if b["name"] == "head" and b.get("parent") is None:
                b["parent"] = "body"
        REPORT["notes"].append(f"{new}: head reparented under body")
    jsave(f"{DST}/models/entity/{new}.geo.json", {"format_version": fv, "minecraft:geometry": [g]})
    geo_bones[new] = {b["name"]: b.get("parent") for b in g["bones"]}
    REPORT["geometries"].append(f"{new} <- {src}:{ident} ({len(g['bones'])} bones)")
log(f"{len(GEOS)} unshadowable geometries written (models/entity/pw_*.geo.json)")

# ----------------------------------------------------------------------------------------------------------------
# 3. ambient v2 (marriage-safe)
# ----------------------------------------------------------------------------------------------------------------
# mob -> (source animation file, source id, geometry key for the root-bone list)
AMBIENTS = {
    "wolf":       ("wolf_pw_ambient",       "animation.wolf.pw.ambient",       "pw_wolf"),
    "fox":        ("fox_pw_ambient",        "animation.fox.pw.ambient",        "pw_fox"),
    "panda":      ("panda_pw_ambient",      "animation.panda.pw.ambient",      "pw_panda"),
    "polar_bear": ("polar_bear_pw_ambient", "animation.polar_bear.pw.ambient", "pw_polar_bear"),
    "cat":        ("cat_pw_ambient",        "animation.cat.pw.ambient",        "pw_cat"),
    "ocelot":     ("ocelot_pw_ambient",     "animation.ocelot.pw.ambient",     "pw_cat"),
    "goat":       ("goat_pw_ambient",       "animation.goat.pw.ambient",       "pw_goat"),
    "camel":      ("camel_pw_ambient",      "animation.camel.pw.ambient",      "pw_camel"),
    "chicken":    ("chicken_pw_ambient",    "animation.chicken.pw.ambient",    "pw_chicken"),
    "cow":        ("cow_pw_ambient",        "animation.cow.pw.ambient",        "pw_cow"),
    "mooshroom":  ("mooshroom_pw_ambient",  "animation.mooshroom.pw.ambient",  "pw_mooshroom"),
}
BOB_RE = re.compile(r"^\(0\.5\*math\.sin\(")
TILT_RE = re.compile(r"^\(2\.0\*math\.sin\(")

for mob, (srcfile, srcid, geokey) in AMBIENTS.items():
    j = jload(f"{SRC}/animations/{srcfile}.animation.json")
    anim = copy.deepcopy(j["animations"][srcid])
    bones = anim.setdefault("bones", {})
    body = bones.get("body", {})
    changes = []
    bob_expr = None
    if "position" in body and isinstance(body["position"], list) and isinstance(body["position"][1], str):
        y = body["position"][1]
        if BOB_RE.match(y):
            y = "(0.15*math.sin(" + y[len("(0.5*math.sin("):]
            body["position"][1] = y
            changes.append("bob 0.5->0.15")
        bob_expr = body["position"][1]
    if "rotation" in body and isinstance(body["rotation"], list) and isinstance(body["rotation"][0], str):
        x = body["rotation"][0]
        if TILT_RE.match(x):
            body["rotation"][0] = "(0.6*math.sin(" + x[len("(2.0*math.sin("):]
            changes.append("tilt 2.0->0.6")
    # drop constant leg yaw (leg3 -4 deg idle twist)
    for leg in [k for k in bones if re.match(r"^leg\d$", k)]:
        rot = bones[leg].get("rotation")
        if isinstance(rot, list) and isinstance(rot[1], str) and rot[1].startswith("(-4*"):
            del bones[leg]
            changes.append(f"{leg} constant yaw dropped")
    # copy the body bob onto every other ROOT bone so the rig breathes as one piece
    if bob_expr:
        roots = [n for n, p in geo_bones[geokey].items() if p is None and n != "body" and not n.startswith("pw_")]
        for r in roots:
            entry = bones.setdefault(r, {})
            pos = entry.get("position", [0, 0, 0])
            if not isinstance(pos, list):
                pos = [0, 0, 0]
            pos = list(pos)
            pos[1] = bob_expr if (pos[1] in (0, 0.0)) else f"({pos[1]})+{bob_expr}"
            entry["position"] = pos
        changes.append(f"bob copied to roots {roots}")
    # pupils (l_pupil/r_pupil) are absent from every .patrix geometry — drop dead entries
    for dead in [k for k in bones if k in ("l_pupil", "r_pupil")]:
        del bones[dead]
    newid = f"animation.pw_{mob}.ambient"
    jsave(f"{DST}/animations/pw_{mob}_ambient_v2.animation.json",
          {"format_version": "1.8.0", "animations": {newid: anim}})
    REPORT["ambients"].append(f"{newid} <- {srcid}: {', '.join(changes) or 'no pattern change'}")
log(f"{len(AMBIENTS)} ambient v2 animations written (animation.pw_<mob>.ambient)")

# ----------------------------------------------------------------------------------------------------------------
# 4. textures
# ----------------------------------------------------------------------------------------------------------------
def copy_tex(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    REPORT["textures"].append(f"{dst[len(DST)+1:]} <- {src}")

# frog: clean Patrix source files (0 magenta px) over our marker-painted copies (same in-pack names)
for ours, src in [("cold_frog.png", "cold_frog.png"), ("frog_temperate.png", "temperate_frog.png"), ("frog_warm.png", "warm_frog.png")]:
    copy_tex(f"{PATRIX}/textures/entity/frog/{src}", f"{DST}/textures/entity/frog/{ours}")
# piglin: the Patrix zombified piglin (JEM textureSize 64x64 -> 512x512 = 8x)
copy_tex(f"{PATRIX}/textures/entity/piglin/zombified_piglin.png", f"{DST}/textures/entity/piglin/zombified_piglin.png")
# cat + chicken: RP-06/RP-08 1.4.6 ship 64x32 vanilla copies on the textures/entity/cat + chicken paths -> pw_ dirs
CAT_FILES = {   # vanilla texture key -> Patrix 512x256 file in RP-07 textures/entity/cat
    "white": "white", "black": "tuxedo", "red": "red", "siamese": "siamese", "british": "british_shorthair",
    "calico": "calico", "persian": "persian", "ragdoll": "ragdoll", "tabby": "tabby", "all_black": "all_black",
    "jellie": "jellie", "ocelot": "ocelot",
}
for key, fn in CAT_FILES.items():
    copy_tex(f"{SRC}/textures/entity/cat/{fn}.png", f"{DST}/textures/entity/pw_cat/{fn}.png")
for fn in ["chicken", "chicken_warm", "chicken_cold"]:
    copy_tex(f"{SRC}/textures/entity/chicken/{fn}.png", f"{DST}/textures/entity/pw_chicken/{fn}.png")
log(f"{len(REPORT['textures'])} textures placed (frog x3 clean, piglin, pw_cat x12, pw_chicken x3)")

# ----------------------------------------------------------------------------------------------------------------
# 5. render controllers + client entities
# ----------------------------------------------------------------------------------------------------------------
PRE = ["variable.gliding_speed_value = 1.0;",
       "variable.tcos0 = (math.cos(query.modified_distance_moved * 38.17) * query.modified_move_speed / variable.gliding_speed_value) * 57.3;"]
MOVE = "math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)"
IDLE = "1.0 - math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)"

def rc_file(name, body):
    jsave(f"{DST}/render_controllers/{name}.render.json", {"format_version": "1.10.0", "render_controllers": body})

def entity(ident, textures, geometry, rcs, animations, animate, pre=PRE, materials=None, scale=None, egg_index=None, extra_scripts=None):
    d = {
        "identifier": ident,
        "min_engine_version": "1.21.0",
        "materials": materials or {"default": "entity_alphatest"},
        "textures": textures,
        "geometry": geometry,
        "render_controllers": rcs,
        "animations": animations,
        "scripts": {"pre_animation": list(pre), "animate": animate},
    }
    if scale is not None:
        d["scripts"]["scale"] = scale
    if extra_scripts:
        d["scripts"].update(extra_scripts)
    if egg_index is not None:
        d["spawn_egg"] = {"texture": "spawn_egg", "texture_index": egg_index}
    return {"format_version": "1.26.0", "minecraft:client_entity": {"description": d}}

def write_entity(fname, obj):
    d = obj["minecraft:client_entity"]["description"]
    # spawn egg: always the vanilla entry for that identifier (never a guessed atlas index)
    vf = f"_intake/vanilla-1.21/entity/{d['identifier'].split(':')[1]}.entity.json"
    try:
        vegg = jload(vf)["minecraft:client_entity"]["description"].get("spawn_egg")
        if vegg:
            d["spawn_egg"] = vegg
        else:
            d.pop("spawn_egg", None)
    except Exception:
        REPORT["notes"].append(f"{fname}: vanilla entity file unavailable ({vf}); spawn_egg left as in 1.4.11")
    jsave(f"{DST}/entity/{fname}.entity.json", obj)
    REPORT["entities"].append(f"{fname}: {d['identifier']}")

def look_anim(mob):
    """pw headtrack when the pack has one (drives head + head2 relative to the entity), else vanilla common."""
    p = f"{SRC}/animations/{mob}_pw_ambient.animation.json"
    if os.path.exists(p) and f"animation.{mob}.pw.headtrack" in jload(p)["animations"]:
        return f"animation.{mob}.pw.headtrack"
    return "animation.common.look_at_target"

# ---- WOLF ------------------------------------------------------------------------------------------------------
WOLF_VARIANTS = ["pale", "ashen", "black", "chestnut", "rusty", "snowy", "spotted", "striped", "woods"]  # vanilla order
wolf_tex = {}
for v in WOLF_VARIANTS:
    stem = "wolf" if v == "pale" else f"wolf_{v}"
    wolf_tex[f"{v}_default"] = f"textures/entity/wolf/{stem}"
    wolf_tex[f"{v}_angry"] = f"textures/entity/wolf/{stem}_angry"
    wolf_tex[f"{v}_tame"] = f"textures/entity/wolf/{stem}_tame"
wolf_tex["default"] = "textures/entity/wolf/wolf"
rc_file("pw_wolf", {"controller.render.pw_wolf": {
    "arrays": {"textures": {
        "Array.default": [f"Texture.{v}_default" for v in WOLF_VARIANTS],
        "Array.angry":   [f"Texture.{v}_angry" for v in WOLF_VARIANTS],
        "Array.tame":    [f"Texture.{v}_tame" for v in WOLF_VARIANTS]}},
    "geometry": "Geometry.default",
    "materials": [{"*": "Material.default"}],
    "textures": ["query.is_angry ? Array.angry[math.clamp(query.variant, 0, 8)] : (query.is_tamed ? Array.tame[math.clamp(query.variant, 0, 8)] : Array.default[math.clamp(query.variant, 0, 8)])"]}})
write_entity("wolf", entity("minecraft:wolf", wolf_tex,
    {"default": "geometry.pw_wolf", "baby": "geometry.pw_wolf"}, ["controller.render.pw_wolf"],
    {"setup": "animation.pw_wolf.setup", "look_at_target": look_anim("wolf"),
     "ar_walk": "animation.ar_wolf.walk", "ar_idle": "animation.ar_wolf.idle", "tail": "animation.pw_wolf.tail_default",
     "pw_ambient": "animation.pw_wolf.ambient", "baby_scaling": "animation.pw_wolf.baby_scaling"},
    ["setup", "look_at_target", {"ar_walk": MOVE}, {"ar_idle": IDLE}, "tail", "pw_ambient", {"baby_scaling": "query.is_baby"}],
    egg_index=10))

# ---- FOX -------------------------------------------------------------------------------------------------------
rc_file("pw_fox", {"controller.render.pw_fox": {
    "arrays": {"textures": {"Array.skins": ["Texture.red", "Texture.arctic"], "Array.sleep": ["Texture.red_sleep", "Texture.arctic_sleep"]}},
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
    "textures": ["query.is_sleeping ? Array.sleep[math.clamp(query.variant, 0, 1)] : Array.skins[math.clamp(query.variant, 0, 1)]"]}})
write_entity("fox", entity("minecraft:fox",
    {"default": "textures/entity/fox/fox", "red": "textures/entity/fox/fox", "arctic": "textures/entity/fox/fox_snow",
     "red_sleep": "textures/entity/fox/fox_sleep", "arctic_sleep": "textures/entity/fox/fox_snow_sleep"},
    {"default": "geometry.pw_fox", "baby": "geometry.pw_fox"}, ["controller.render.pw_fox"],
    {"look_at_target": look_anim("fox"), "ar_walk": "animation.ar_fox.walk", "ar_idle": "animation.ar_fox.idle",
     "pw_ambient": "animation.pw_fox.ambient"},
    ["look_at_target", {"ar_walk": MOVE}, {"ar_idle": IDLE}, "pw_ambient"], egg_index=53))

# ---- PANDA -----------------------------------------------------------------------------------------------------
PANDA = ["default", "lazy", "worried", "playful", "brown", "weak", "aggressive"]   # vanilla Array.skins order
panda_tex = {"default": "textures/entity/panda/panda"}
for v in PANDA[1:]:
    panda_tex[v] = f"textures/entity/panda/{v}_panda"
rc_file("pw_panda", {"controller.render.pw_panda": {
    "arrays": {"textures": {"Array.skins": [f"Texture.{v}" for v in PANDA]}},
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
    "textures": ["Array.skins[math.clamp(query.variant, 0, 6)]"]}})
write_entity("panda", entity("minecraft:panda", panda_tex,
    {"default": "geometry.pw_panda", "baby": "geometry.pw_panda"}, ["controller.render.pw_panda"],
    {"look_at_target": look_anim("panda"), "ar_walk": "animation.ar_panda.walk", "ar_idle": "animation.ar_panda.idle",
     "ar_lay": "animation.ar_panda.lay_on_back", "ar_sneeze": "animation.ar_panda.sneeze", "pw_ambient": "animation.pw_panda.ambient"},
    ["look_at_target", {"ar_walk": MOVE}, {"ar_idle": IDLE}, {"ar_lay": "query.is_rolling"}, {"ar_sneeze": "query.is_sneezing"}, "pw_ambient"],
    egg_index=52))

# ---- POLAR BEAR (Java PolarBearRenderer draws the model at 1.2 -> same here) ------------------------------------
rc_file("pw_polar_bear", {"controller.render.pw_polar_bear": {
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"]}})
write_entity("polar_bear", entity("minecraft:polar_bear", {"default": "textures/entity/bear/polarbear"},
    {"default": "geometry.pw_polar_bear", "baby": "geometry.pw_polar_bear"}, ["controller.render.pw_polar_bear"],
    {"look_at_target": look_anim("polar_bear"), "ar_walk": "animation.ar_polar_bear.walk", "ar_idle": "animation.ar_polar_bear.idle",
     "pw_ambient": "animation.pw_polar_bear.ambient"},
    ["look_at_target", {"ar_walk": MOVE}, {"ar_idle": IDLE}, "pw_ambient"], scale="1.2", egg_index=38))

# ---- CAT (Java CatRenderer scales the ocelot model by 0.8) + OCELOT (1.0) --------------------------------------
CAT_ORDER = ["white", "black", "red", "siamese", "british", "calico", "persian", "ragdoll", "tabby", "all_black", "jellie"]  # vanilla Array.skins
cat_tex = {k: f"textures/entity/pw_cat/{CAT_FILES[k]}" for k in CAT_ORDER}
cat_tex["default"] = cat_tex["tabby"]
rc_file("pw_cat", {"controller.render.pw_cat": {
    "arrays": {"textures": {"Array.skins": [f"Texture.{k}" for k in CAT_ORDER]}},
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
    "textures": ["Array.skins[math.clamp(query.variant, 0, 10)]"]}})
CAT_ANIMS = lambda mob: {"look_at_target": look_anim(mob), "ar_walk": f"animation.ar_{mob}.walk", "ar_idle": f"animation.ar_{mob}.idle",
                         "pw_ambient": f"animation.pw_{mob}.ambient"}
cat_animate = ["look_at_target", {"ar_walk": MOVE}, {"ar_idle": IDLE}, "pw_ambient"]
write_entity("cat", entity("minecraft:cat", cat_tex, {"default": "geometry.pw_cat", "baby": "geometry.pw_cat"}, ["controller.render.pw_cat"],
    dict(CAT_ANIMS("cat"), tail="animation.ar_cat.tail_flick"), cat_animate + ["tail"], scale="0.8", egg_index=54))
rc_file("pw_ocelot", {"controller.render.pw_ocelot": {
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"]}})
# ocelot shares the cat geometry, so it uses the cat's ar_ walk/idle (ar_ocelot.* was authored for thigh_* bones the
# .patrix cat does not have) — its own headtrack/ambient stay ocelot's
write_entity("ocelot", entity("minecraft:ocelot", {"default": "textures/entity/pw_cat/ocelot"},
    {"default": "geometry.pw_cat", "baby": "geometry.pw_cat"}, ["controller.render.pw_ocelot"],
    {"look_at_target": look_anim("ocelot"), "ar_walk": "animation.ar_cat.walk", "ar_idle": "animation.ar_cat.idle",
     "pw_ambient": "animation.pw_ocelot.ambient"}, cat_animate, egg_index=9))

# ---- GOAT + CAMEL (material entity_alphatest = 1 sampler == 1 RC binding; the 'llama' 3-slot material was the magenta) -
rc_file("pw_goat", {"controller.render.pw_goat": {
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"]}})
write_entity("goat", entity("minecraft:goat", {"default": "textures/entity/goat/goat"},
    {"default": "geometry.pw_goat", "baby": "geometry.pw_goat"}, ["controller.render.pw_goat"],
    {"look_at_target": look_anim("goat"), "ar_walk": "animation.ar_goat.walk", "ar_idle": "animation.ar_goat.idle",
     "ar_ram": "animation.ar_goat.ram", "pw_ambient": "animation.pw_goat.ambient"},
    ["look_at_target", {"ar_walk": MOVE}, {"ar_idle": IDLE}, {"ar_ram": "variable.has_target && variable.attack_time >= 0.0"}, "pw_ambient"],
    egg_index=66))
rc_file("pw_camel", {"controller.render.pw_camel": {
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"]}})
write_entity("camel", entity("minecraft:camel", {"default": "textures/entity/camel/camel"},
    {"default": "geometry.pw_camel", "baby": "geometry.pw_camel"}, ["controller.render.pw_camel"],
    {"look_at_target": look_anim("camel"), "ar_walk": "animation.ar_camel.walk", "ar_idle": "animation.ar_camel.idle",
     "pw_ambient": "animation.pw_camel.ambient"},
    ["look_at_target", {"ar_walk": MOVE}, {"ar_idle": IDLE}, "pw_ambient"], egg_index=75))

# ---- CHICKEN (vanilla 1.21 climate scheme: v.index from query.property('minecraft:climate_variant')) ----------
rc_file("pw_chicken", {"controller.render.pw_chicken": {
    "arrays": {"textures": {"Array.textures": ["Texture.default", "Texture.warm", "Texture.cold"]},
               "geometries": {"Array.geos": ["Geometry.default", "Geometry.warm", "Geometry.cold"]}},
    "geometry": "Array.geos[variable.index]", "materials": [{"*": "Material.default"}],
    "textures": ["Array.textures[variable.index]"]}})
write_entity("chicken", entity("minecraft:chicken",
    {"default": "textures/entity/pw_chicken/chicken", "warm": "textures/entity/pw_chicken/chicken_warm", "cold": "textures/entity/pw_chicken/chicken_cold"},
    {"default": "geometry.pw_chicken", "warm": "geometry.pw_chicken_warm", "cold": "geometry.pw_chicken_cold", "baby": "geometry.pw_chicken"},
    ["controller.render.pw_chicken"],
    {"look_at_target": look_anim("chicken"), "ar_walk": "animation.ar_chicken.walk", "ar_idle": "animation.ar_chicken.idle",
     "ar_flap": "animation.ar_chicken.wing_flap_fall", "pw_ambient": "animation.pw_chicken.ambient"},
    ["look_at_target", {"ar_walk": MOVE}, {"ar_idle": IDLE}, {"ar_flap": "!query.is_on_ground && !query.is_in_water"}, "pw_ambient"],
    pre=PRE + ["temp.variant = query.property('minecraft:climate_variant');",
               "variable.index = (temp.variant == 'temperate') ? 0 : ((temp.variant == 'warm') ? 1 : 2);"],
    egg_index=1))

# ---- TROPICAL FISH (vanilla id minecraft:tropicalfish; 2-sampler 'tropicalfish' material = base + pattern) -------
fish_tex = {"typeA": "textures/entity/fish/tropical_a", "typeB": "textures/entity/fish/tropical_b"}
for i in range(1, 7):
    fish_tex[f"aPattern{i}"] = f"textures/entity/fish/tropical_a_pattern_{i}"
    fish_tex[f"bPattern{i}"] = f"textures/entity/fish/tropical_b_pattern_{i}"
rc_file("pw_tropicalfish", {"controller.render.pw_tropicalfish": {
    "arrays": {"geometries": {"Array.models": ["Geometry.typeA", "Geometry.typeB"]},
               "textures": {"Array.types": ["Texture.typeA", "Texture.typeB"],
                            "Array.patterns": [f"Texture.aPattern{i}" for i in range(1, 7)] + [f"Texture.bPattern{i}" for i in range(1, 7)]}},
    "geometry": "Array.models[variable.TropicalFish.Base]", "materials": [{"*": "Material.default"}],
    "textures": ["Array.types[variable.TropicalFish.Base]", "Array.patterns[variable.TropicalFish.Pattern]"]}})
old = f"{DST}/entity/tropical_fish.entity.json"
if os.path.exists(old):
    os.remove(old); REPORT["removed"].append("entity/tropical_fish.entity.json (dead id minecraft:tropical_fish)")
write_entity("tropicalfish", entity("minecraft:tropicalfish", fish_tex,
    {"typeA": "geometry.pw_tropicalfish_a", "typeB": "geometry.pw_tropicalfish_b", "default": "geometry.pw_tropicalfish_a"},
    ["controller.render.pw_tropicalfish"],
    {"ar_swim_a": "animation.ar_tropical_fish_a.swim", "ar_flop_a": "animation.ar_tropical_fish_a.flop",
     "ar_swim_b": "animation.ar_tropical_fish_b.swim", "pw_ambient": "animation.tropical_fish.pw.ambient"},
    [{"ar_swim_a": "query.is_in_water && variable.TropicalFish.Base == 0"}, {"ar_flop_a": "!query.is_in_water"},
     {"ar_swim_b": "query.is_in_water && variable.TropicalFish.Base == 1"}, "pw_ambient"],
    materials={"default": "tropicalfish"}, egg_index=44))
REPORT["notes"].append("tropicalfish: variable.TropicalFish.Base/Pattern are engine-provided (vanilla entity defines none)")

# ---- ZOMBIFIED PIGLIN -> vanilla id minecraft:zombie_pigman ----------------------------------------------------
old = f"{DST}/entity/zombified_piglin.entity.json"
if os.path.exists(old):
    os.remove(old); REPORT["removed"].append("entity/zombified_piglin.entity.json (dead id minecraft:zombified_piglin)")
rc_file("pw_zombie_pigman", {"controller.render.pw_zombie_pigman": {
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"]}})
write_entity("zombie_pigman", entity("minecraft:zombie_pigman", {"default": "textures/entity/piglin/zombified_piglin"},
    {"default": "geometry.pw_zombie_pigman", "baby": "geometry.pw_zombie_pigman"}, ["controller.render.pw_zombie_pigman"],
    {"move": "animation.humanoid_articulated.move", "look_at_target": "animation.humanoid_articulated.look_at_target",
     "pw_ambient": "animation.zombified_piglin.pw.ambient"},
    [{"move": MOVE}, "look_at_target", "pw_ambient"], egg_index=16))

# ---- DONKEY / MULE: chests only when chested -------------------------------------------------------------------
for mob in ["donkey", "mule"]:
    e = jload(f"{SRC}/entity/{mob}.entity.json")
    d = e["minecraft:client_entity"]["description"]
    d["geometry"] = {"default": f"geometry.pw_{mob}", "baby": f"geometry.pw_{mob}"}
    rc_file(f"pw_{mob}", {f"controller.render.pw_{mob}": {
        "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"],
        "part_visibility": [{"left_chest": "query.is_chested"}, {"right_chest": "query.is_chested"}]}})
    write_entity(mob, e)

# ---- COW / MOOSHROOM: fixed geometry + ambient v2 --------------------------------------------------------------
for mob in ["cow", "mooshroom"]:
    e = jload(f"{SRC}/entity/{mob}.entity.json")
    d = e["minecraft:client_entity"]["description"]
    d["geometry"] = {"default": f"geometry.pw_{mob}", "baby": f"geometry.pw_{mob}"}
    d["animations"]["pw_ambient"] = f"animation.pw_{mob}.ambient"
    d["animations"].pop("pw_eyes", None)
    d["scripts"]["animate"] = [a for a in d["scripts"]["animate"] if a != "pw_eyes"]
    write_entity(mob, e)
log(f"{len(REPORT['entities'])} client entities written; removed {REPORT['removed']}")

# ----------------------------------------------------------------------------------------------------------------
# 6. manifest
# ----------------------------------------------------------------------------------------------------------------
m = jload(f"{DST}/manifest.json")
m["header"]["version"] = VERSION
m["modules"][0]["version"] = VERSION
m["header"]["name"] = "AbsolutRealism Neutral Mobs RP v1.4.12"
m["header"]["description"] = (
    "v1.4.12 (2026-09-27) P0 WIRING (D-C259/D-C260, 176-shot witness round): wolf/fox/panda/polar bear/cat/ocelot/"
    "goat/camel/chicken rewired to their Patrix geometries + textures through unshadowable pw_ copies "
    "(geometry.pw_<mob>, animation.pw_<mob>.ambient, textures/entity/pw_cat + pw_chicken); goat + camel off the "
    "3-slot 'llama' material (the solid magenta); chicken carries the 1.21 climate scheme; tropical fish on the "
    "vanilla id minecraft:tropicalfish + 2-sampler 'tropicalfish' material; zombified piglin on the vanilla id "
    "minecraft:zombie_pigman with the Patrix 512x512 texture; donkey/mule chests only when chested; cow + mooshroom "
    "head parented under body + breathing bob 0.5->0.15 cube copied onto every root bone (the 'not married' "
    "legs/neck); frog textures replaced by the clean Patrix 1.21.11 files (the magenta N/E/S/W tiles were our own "
    "markers). No 1.4.11 asset deleted except the two dead-id entity files.")
jsave(f"{DST}/manifest.json", m)
log("manifest 1.4.12 stamped")

json.dump(REPORT, open("_logs/rp07_1412_build_report.json", "w"), indent=1)
print(json.dumps(REPORT, indent=1))
