#!/usr/bin/env python3
"""homestead_build.py — builds the HOMESTEAD families into their HOME packs (ruling 2026-09-21 17:23:
"All changes go into their current relevant packs. We ONLY make new packs when necessary").

  BP-02 Tectonic BP  v1.3.177 -> v1.3.178 : blocks (hearth/flue/wall x 53 materials, rafter45 x 2 woods),
                                            recipes, scripts (pw_homestead*.js + one import in main.js)
  RP-04 Basic RP     v1.3.127 -> v1.3.128 : geometries (models/blocks/pw_homestead.geo.json), textures
                                            (pw_hearth_soot/ash/embers + MERS), terrain_texture keys, lang
  RP-02 Atmospherics v2.0.1   -> v2.0.2   : particles (pw:room_smoke on a generated puff sprite, pw:chimney_smoke on the
                                            existing campfire_smoke flipbook), fog pw:smoke_room

Units: geometry in CUBES (1/16 block); textures 128 px per block => 1 cube = 8 px.
Local -z = the face toward the placer (roof-family convention: cardinal_direction + y_rotation_offset 180,
'north' -> rotation [0,0,0]).  Inputs: _packs/bp02-177/ (unzipped), _packs/RP-04-v1_3_127.mcpack,
_packs/RP-02-v2_0_1.mcpack.  Output trees: _build/bp02-178, _build/rp04-128, _build/rp02-202.
Packaging is NOT done here — verify_homestead.py packages only after every gate passes (D-101).
"""
import json, os, re, shutil, sys, zipfile, hashlib, io
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from homestead_materials import OUTER, INNER16, RAFTER_WOODS  # noqa: E402

ROOT = Path("/home/claude")
BP_SRC = ROOT / "_packs/bp02-177"
RP04_ZIP = ROOT / "_packs/RP-04-v1_3_127.mcpack"
RP02_ZIP = ROOT / "_packs/RP-02-v2_0_1.mcpack"
BP_OUT = ROOT / "_build/bp02-178"
RP04_OUT = ROOT / "_build/rp04-128"
RP02_OUT = ROOT / "_build/rp02-202"
SRC = ROOT / "tools/homestead_src"

BP_VER, RP04_VER, RP02_VER = [1, 3, 178], [1, 3, 128], [2, 0, 2]
DATE = "2026-09-21"

ROT = {"north": [0, 0, 0], "west": [0, 90, 0], "south": [0, 180, 0], "east": [0, -90, 0]}   # roof45 table (witnessed)
FULL_BOX = {"origin": [-8, 0, -8], "size": [16, 16, 16]}

def jdump(obj, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

# =============================================================================================
# GEOMETRY (cubes; texture_width/height 16 so UV units are cubes)
# =============================================================================================
def face(uv_w, uv_h, inst=None, u=0, v=0):
    d = {"uv": [u, v], "uv_size": [min(uv_w, 16), min(uv_h, 16)]}
    if inst: d["material_instance"] = inst
    return d

def box(origin, size, faces, pivot=None, rotation=None, inflate=None):
    c = {"origin": origin, "size": size, "uv": faces}
    if pivot is not None: c["pivot"] = pivot
    if rotation is not None: c["rotation"] = rotation
    if inflate is not None: c["inflate"] = inflate
    return c

def geo(identifier, bones, vis=(1.5, 1.5, [0, 0.75, 0])):
    return {
        "description": {"identifier": identifier, "texture_width": 16, "texture_height": 16,
                        "visible_bounds_width": vis[0], "visible_bounds_height": vis[1], "visible_bounds_offset": vis[2]},
        "bones": [{"name": n, "pivot": [0, 0, 0], "cubes": cubes} for n, cubes in bones],
    }

def hearth_geometry(phase):
    """skin (2-cube back wall at +z, fire face = soot) · floor · bed · logs (fueled/lit) · flames (lit)."""
    skin = box([-8, 0, 6], [16, 16, 2], {
        "north": face(16, 16, "soot"), "south": face(16, 16), "east": face(2, 16), "west": face(2, 16),
        "up": face(16, 2, "top"), "down": face(16, 2, "top")})
    floor = box([-8, 0, -8], [16, 1, 14], {
        "up": face(16, 14, "soot"), "north": face(16, 1, "soot"), "east": face(14, 1, "soot"), "west": face(14, 1, "soot"),
        "down": face(16, 14, "top")})
    bed = box([-6, 1, -5], [12, 1, 8], {
        "up": face(12, 8, "bed"), "north": face(12, 1, "bed"), "south": face(12, 1, "bed"), "east": face(8, 1, "bed"), "west": face(8, 1, "bed")})
    bones = [("skin", [skin]), ("floor", [floor]), ("bed", [bed])]
    if phase in ("fueled", "lit"):
        logs = []
        for z0 in (-4.5, -0.5):     # lower pair along x
            logs.append(box([-6, 2, z0], [12, 3, 3], {
                "north": face(12, 3, "log"), "south": face(12, 3, "log"), "up": face(12, 3, "log"), "down": face(12, 3, "log"),
                "east": face(3, 3, "log_end", 6, 6), "west": face(3, 3, "log_end", 6, 6)}))
        for x0 in (-4.5, -0.5):     # upper pair along z
            logs.append(box([x0, 5, -7], [3, 3, 12], {
                "east": face(12, 3, "log"), "west": face(12, 3, "log"), "up": face(3, 12, "log"), "down": face(3, 12, "log"),
                "north": face(3, 3, "log_end", 6, 6), "south": face(3, 3, "log_end", 6, 6)}))
        bones.append(("logs", logs))
    if phase == "lit":
        flames = []
        for rot in ([0, 45, 0], [0, -45, 0]):   # two crossed alpha-test quads on the vanilla fire_0 flipbook
            flames.append(box([-6, 4, -1], [12, 10, 0], {"north": face(16, 16, "flame"), "south": face(16, 16, "flame")},
                              pivot=[0, 4, -1], rotation=rot, inflate=0.01))     # Lesson #175: 0.01 inflate on zero-axis boxes
        bones.append(("flames", flames))
    return geo(f"geometry.pw_hearth_{phase}", bones)

def flue_cap_geometry():
    body = box([-8, 0, -8], [16, 16, 16], {"north": face(16, 16), "south": face(16, 16), "east": face(16, 16), "west": face(16, 16), "down": face(16, 16, "top")})
    rim = [
        box([-9, 16, -9], [18, 2, 3], {"north": face(16, 2), "south": face(16, 2), "east": face(3, 2), "west": face(3, 2), "up": face(16, 3, "top"), "down": face(16, 3, "top")}),
        box([-9, 16, 6], [18, 2, 3], {"north": face(16, 2), "south": face(16, 2), "east": face(3, 2), "west": face(3, 2), "up": face(16, 3, "top"), "down": face(16, 3, "top")}),
        box([-9, 16, -6], [3, 2, 12], {"east": face(12, 2), "west": face(12, 2), "up": face(3, 12, "top"), "down": face(3, 12, "top")}),
        box([6, 16, -6], [3, 2, 12], {"east": face(12, 2), "west": face(12, 2), "up": face(3, 12, "top"), "down": face(3, 12, "top")}),
    ]
    throat = box([-6, 16, -6], [12, 0.5, 12], {"up": face(12, 12, "soot")})
    return geo("geometry.pw_flue_cap", [("body", [body]), ("rim", rim), ("throat", [throat])], vis=(1.5, 1.5, [0, 0.75, 0]))

def rafter_geometry():
    # one beam on the cell diagonal, HIGH end toward the placer (-z): JSON rotation -45 about x lifts the -z end
    beam = box([-2, 6, -11.314], [4, 4, 22.627], {
        "north": face(4, 4, "end"), "south": face(4, 4, "end"), "east": face(16, 4), "west": face(16, 4), "up": face(16, 4), "down": face(16, 4)},
        pivot=[0, 8, 0], rotation=[-45, 0, 0])
    return geo("geometry.pw_rafter45", [("beam", [beam])], vis=(1.5, 1.5, [0, 0.5, 0]))

def build_geometry_file():
    return {"format_version": "1.16.0", "minecraft:geometry": [
        hearth_geometry("cold"), hearth_geometry("fueled"), hearth_geometry("lit"), hearth_geometry("embers"),
        flue_cap_geometry(), rafter_geometry()]}

# =============================================================================================
# TEXTURES (numpy-generated, 128 px = 16 cubes; derived from RP-04's Patrix stone brick for the soot)
# =============================================================================================
def _noise(shape, seed, blur=2.0):
    rng = np.random.default_rng(seed)
    n = rng.random(shape).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im).astype(np.float32) / 255.0
    a = (a - a.min()) / max(1e-6, (a.max() - a.min()))
    return a

def tex_soot(src_rgba):
    src = src_rgba[..., :3].astype(np.float32) / 255.0
    h = src.shape[0]
    grad = np.linspace(0.18, 0.42, h, dtype=np.float32)[:, None, None]   # darker at the top (smoke stain)
    n = _noise(src.shape[:2], 11, 1.2)[..., None]
    out = src * grad * (0.75 + 0.5 * n)
    out = np.clip(out, 0, 1)
    rgba = np.dstack([(out * 255).astype(np.uint8), np.full(src.shape[:2], 255, np.uint8)])
    mers = np.dstack([np.zeros(src.shape[:2], np.uint8), np.zeros(src.shape[:2], np.uint8), np.full(src.shape[:2], 245, np.uint8), np.zeros(src.shape[:2], np.uint8)])
    return rgba, mers

def tex_ash(size=128):
    n1 = _noise((size, size), 21, 3.0); n2 = _noise((size, size), 22, 0.8)
    g = 0.55 + 0.25 * n1 + 0.08 * (n2 - 0.5)
    chunks = _noise((size, size), 23, 1.5) > 0.72                            # charcoal lumps
    rgb = np.stack([g * 0.95, g * 0.93, g * 0.90], -1)
    rgb[chunks] = np.array([0.12, 0.11, 0.10]) * (0.6 + 0.8 * n2[chunks])[:, None]
    rgba = np.dstack([(np.clip(rgb, 0, 1) * 255).astype(np.uint8), np.full((size, size), 255, np.uint8)])
    mers = np.dstack([np.zeros((size, size), np.uint8), np.zeros((size, size), np.uint8), np.full((size, size), 255, np.uint8), np.zeros((size, size), np.uint8)])
    return rgba, mers

def tex_embers(size=128):
    coal = 0.10 + 0.10 * _noise((size, size), 31, 1.0)                        # charcoal base
    cracks = _noise((size, size), 32, 2.2)
    glow = np.clip((cracks - 0.55) / 0.25, 0, 1) ** 1.4                       # glowing fissures between the coals
    hot = _noise((size, size), 33, 0.9) > 0.86                                 # bright sparks
    glow = np.maximum(glow, hot.astype(np.float32) * 0.9)
    ember = np.array([1.0, 0.42, 0.06]); core = np.array([1.0, 0.85, 0.35])
    rgb = np.stack([coal * 0.9, coal * 0.8, coal * 0.75], -1)
    rgb = rgb * (1 - glow[..., None]) + (ember * (1 - glow[..., None] * 0.5) + core * glow[..., None] * 0.5) * glow[..., None]
    rgba = np.dstack([(np.clip(rgb, 0, 1) * 255).astype(np.uint8), np.full((size, size), 255, np.uint8)])
    mers = np.dstack([np.zeros((size, size), np.uint8), (glow * 250).astype(np.uint8), np.full((size, size), 230, np.uint8), np.zeros((size, size), np.uint8)])
    return rgba, mers

def tex_smoke_sprite(size=64):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    r = np.sqrt((xx - size / 2 + 0.5) ** 2 + (yy - size / 2 + 0.5) ** 2) / (size / 2)
    n = _noise((size, size), 41, 2.5)
    a = np.clip(1 - r / (0.82 + 0.18 * n), 0, 1) ** 1.6 * (0.75 + 0.25 * n)
    g = (0.78 + 0.12 * n)
    rgba = np.dstack([(g * 255).astype(np.uint8)] * 3 + [(a * 255).astype(np.uint8)])
    return rgba

def texture_set(color, mers):
    return {"format_version": "1.21.30", "minecraft:texture_set": {"color": color, "metalness_emissive_roughness_subsurface": mers}}

# =============================================================================================
# BLOCKS
# =============================================================================================
def common_components(display_key, seconds, resistance, dampening=15):
    return {
        "minecraft:collision_box": FULL_BOX, "minecraft:selection_box": FULL_BOX,
        "minecraft:light_dampening": dampening,
        "minecraft:destructible_by_mining": {"seconds_to_destroy": seconds},
        "minecraft:destructible_by_explosion": {"explosion_resistance": resistance},
        "minecraft:display_name": display_key,
    }

def mi(texture, method="opaque", **extra):
    d = {"texture": texture, "render_method": method}; d.update(extra); return d

# L-VAR-1 (witnessed 2026-09-22): custom-block material_instances flatten weighted `variations` keys into an un-weighted
# array (first entry used, one content-log warning per face per permutation).  Custom blocks therefore reference
# SINGLE-PATH keys only: pw_mat_<material>[_top], pw_mat_stripped_<wood>[_top], pw_hearth_flame.  The RP section
# below defines them from each material's first variation path.
def _single_keys():
    """Keys whose RP-04 .127 entry is already a single path — those are referenced as-is (no pw_mat alias needed)."""
    with zipfile.ZipFile(RP04_ZIP) as z:
        td = json.loads(z.read("textures/terrain_texture.json").decode("utf-8-sig"))["texture_data"]
    return {k for k, v in td.items() if isinstance(v.get("textures"), str)}
SINGLE = _single_keys()
def matkey(mid, top=False):
    name, item, side, topk = OUTER[mid]
    key = topk if top else side
    if key in SINGLE: return key
    if top and topk != side: return f"pw_mat_{mid}_top"
    return f"pw_mat_{mid}"
def rafterkey(wid, end=False):
    wname, planks, side, endk = RAFTER_WOODS[wid]
    key = endk if end else side
    if key in SINGLE: return key
    return f"pw_mat_stripped_{wid}_top" if end else f"pw_mat_stripped_{wid}"

def hearth_materials(mid, phase):
    # L-RM-1 (witnessed 2026-09-22): "[Components][error] MaterialInstances can't mix and match opaque and transparent
    # materials" — every instance of a block must share ONE render_method.  The flame needs alpha_test, so the whole
    # hearth is alpha_test (the roof family's convention; opaque textures render identically under alpha_test).
    bed = "pw_hearth_embers" if phase in ("lit", "embers") else "pw_hearth_ash"
    A = "alpha_test"
    m = {"*": mi(matkey(mid), A), "top": mi(matkey(mid, top=True), A), "soot": mi("pw_hearth_soot", A), "bed": mi(bed, A),
         "log": mi("pw_hearth_log", A), "log_end": mi("pw_hearth_log_end", A),
         "flame": mi("pw_hearth_flame", A, face_dimming=False, ambient_occlusion=False)}
    return m

def hearth_block(mid, name, item, side, top):
    ident = f"pw:hearth_{mid}"
    comps = common_components(f"tile.{ident}.name", 2.0, 6)
    comps.update({
        "minecraft:geometry": {"identifier": "geometry.pw_hearth_cold"},
        "minecraft:material_instances": hearth_materials(mid, "cold"),
        "minecraft:light_emission": 0,
        "minecraft:map_color": "#5a4632",
        "minecraft:custom_components": ["pw:hearth"],
    })
    perms = [{"condition": f"q.block_state('minecraft:cardinal_direction') == '{d}'", "components": {"minecraft:transformation": {"rotation": r}}} for d, r in ROT.items()]
    light = {"cold": 0, "fueled": 0, "lit": 15, "embers": 7}
    for ph in ("fueled", "lit", "embers"):
        perms.append({"condition": f"q.block_state('pw:phase') == '{ph}'", "components": {
            "minecraft:geometry": {"identifier": f"geometry.pw_hearth_{ph}"},
            "minecraft:material_instances": hearth_materials(mid, ph),
            "minecraft:light_emission": light[ph]}})
    return {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": ident, "menu_category": {"category": "construction"},
                        "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"], "y_rotation_offset": 180}},
                        "states": {"pw:phase": ["cold", "fueled", "lit", "embers"]}},
        "components": comps, "permutations": perms}}

def flue_block(mid, name, item, side, top):
    ident = f"pw:flue_{mid}"
    comps = common_components(f"tile.{ident}.name", 1.5, 6)
    comps.update({
        "minecraft:geometry": "minecraft:geometry.full_block",
        "minecraft:material_instances": {"*": mi(matkey(mid)), "up": mi(matkey(mid, top=True)), "down": mi(matkey(mid, top=True))},
        "minecraft:map_color": "#6f6f6f",
        "minecraft:custom_components": ["pw:flue"],
    })
    perms = [{"condition": "q.block_state('pw:cap') == true", "components": {
        "minecraft:geometry": {"identifier": "geometry.pw_flue_cap"},
        "minecraft:material_instances": {"*": mi(matkey(mid)), "top": mi(matkey(mid, top=True)), "soot": mi("pw_hearth_soot")}}}]
    return {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": ident, "menu_category": {"category": "construction"}, "states": {"pw:cap": [False, True]}},
        "components": comps, "permutations": perms}}

def wall_block(mid, name, item, side, top):
    ident = f"pw:wall_{mid}"
    comps = common_components(f"tile.{ident}.name", 1.5, 6)
    comps.update({
        "minecraft:geometry": "minecraft:geometry.full_block",
        "minecraft:material_instances": {"*": mi(matkey(mid)), "up": mi(matkey(mid, top=True)), "down": mi(matkey(mid, top=True)), "north": mi(matkey(INNER16[0]))},
        "minecraft:map_color": "#8a7f70",
        "minecraft:custom_components": ["pw:wall_dual"],
    })
    if mid.endswith("_planks"):
        comps["minecraft:flammable"] = {"catch_chance_modifier": 5, "destroy_chance_modifier": 20}
    perms = []
    for d in ("north", "south", "east", "west"):
        for inner in INNER16:
            perms.append({"condition": f"q.block_state('minecraft:cardinal_direction') == '{d}' && q.block_state('pw:inner') == '{inner}'",
                          "components": {"minecraft:material_instances": {"*": mi(matkey(mid)), "up": mi(matkey(mid, top=True)), "down": mi(matkey(mid, top=True)), d: mi(matkey(inner))}}})
    return {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": ident, "menu_category": {"category": "construction"},
                        "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"], "y_rotation_offset": 180}},
                        "states": {"pw:inner": list(INNER16)}},
        "components": comps, "permutations": perms}}

def rafter_block(wid, wname, planks, side, end):
    ident = f"pw:rafter45_{wid}"
    comps = {
        "minecraft:geometry": {"identifier": "geometry.pw_rafter45"},
        "minecraft:material_instances": {"*": mi(rafterkey(wid)), "end": mi(rafterkey(wid, end=True))},
        "minecraft:collision_box": False,
        "minecraft:selection_box": FULL_BOX,
        "minecraft:light_dampening": 0,
        "minecraft:destructible_by_mining": {"seconds_to_destroy": 0.8},
        "minecraft:destructible_by_explosion": {"explosion_resistance": 2},
        "minecraft:display_name": f"tile.{ident}.name",
        "minecraft:map_color": "#7a5230",
        "minecraft:flammable": {"catch_chance_modifier": 5, "destroy_chance_modifier": 20},
    }
    perms = [{"condition": f"q.block_state('minecraft:cardinal_direction') == '{d}'", "components": {"minecraft:transformation": {"rotation": r}}} for d, r in ROT.items()]
    return {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": ident, "menu_category": {"category": "construction"},
                        "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"], "y_rotation_offset": 180}}},
        "components": comps, "permutations": perms}}

# =============================================================================================
# RECIPES (house style: format 1.20.10, crafting_table + pw:builders_table, unlock)
# =============================================================================================
def recipe_shaped(ident, pattern, key, result, count, unlock_item):
    return {"format_version": "1.20.10", "minecraft:recipe_shaped": {
        "description": {"identifier": ident}, "tags": ["crafting_table", "pw:builders_table"],
        "pattern": pattern, "key": key, "unlock": [{"item": unlock_item}], "result": {"item": result, "count": count}}}

def recipes_for(mid, item):
    M = {"item": item}
    return [
        (f"pw_hearth_{mid}", recipe_shaped(f"pw:hearth_{mid}", ["MMM", "MCM", "MMM"], {"M": M, "C": {"item": "minecraft:campfire"}}, f"pw:hearth_{mid}", 1, "minecraft:campfire")),
        (f"pw_flue_{mid}", recipe_shaped(f"pw:flue_{mid}", ["M M", "M M", "M M"], {"M": M}, f"pw:flue_{mid}", 3, item)),
        (f"pw_wall_{mid}", recipe_shaped(f"pw:wall_{mid}", ["M", "M", "M"], {"M": M}, f"pw:wall_{mid}", 3, item)),
    ]

# =============================================================================================
# PARTICLES + FOG (RP-02)
# =============================================================================================
def particle_room_smoke():
    return {"format_version": "1.10.0", "particle_effect": {
        "description": {"identifier": "pw:room_smoke", "basic_render_parameters": {"material": "particles_alpha", "texture": "textures/particle/pw_smoke"}},
        "components": {
            "minecraft:emitter_initialization": {"creation_expression": "variable.spin = math.random(-40, 40);"},
            "minecraft:emitter_rate_instant": {"num_particles": 1},
            "minecraft:emitter_lifetime_once": {"active_time": 0.1},
            "minecraft:emitter_shape_point": {"offset": [0, 0, 0], "direction": ["math.random(-1, 1)", "math.random(0.6, 1.4)", "math.random(-1, 1)"]},
            "minecraft:particle_initial_speed": 0.12,
            "minecraft:particle_initial_spin": {"rotation": "math.random(0, 360)", "rotation_rate": "variable.spin"},
            "minecraft:particle_lifetime_expression": {"max_lifetime": "math.random(9, 15)"},
            "minecraft:particle_motion_dynamic": {"linear_acceleration": ["math.random(-0.03, 0.03)", 0.05, "math.random(-0.03, 0.03)"], "linear_drag_coefficient": 0.9},
            "minecraft:particle_motion_collision": {"collision_drag": 6.0, "coefficient_of_restitution": 0.0, "collision_radius": 0.15, "expire_on_contact": False},
            "minecraft:particle_appearance_billboard": {
                "size": ["0.45 + 0.09 * variable.particle_age", "0.45 + 0.09 * variable.particle_age"],
                "facing_camera_mode": "lookat_xyz",
                "uv": {"texture_width": 64, "texture_height": 64, "uv": [0, 0], "uv_size": [64, 64]}},
            "minecraft:particle_appearance_tinting": {"color": {"interpolant": "variable.particle_age / variable.particle_lifetime",
                "gradient": {"0.0": "#00807A72", "0.12": "#5C807A72", "0.7": "#4A6F6A64", "1.0": "#00605C58"}}},
        }}}

def particle_chimney_smoke():
    return {"format_version": "1.10.0", "particle_effect": {
        "description": {"identifier": "pw:chimney_smoke", "basic_render_parameters": {"material": "particles_alpha", "texture": "textures/particle/campfire_smoke"}},
        "components": {
            "minecraft:emitter_initialization": {"creation_expression": "variable.spin = math.random(-30, 30);"},
            "minecraft:emitter_rate_instant": {"num_particles": 1},
            "minecraft:emitter_lifetime_once": {"active_time": 0.1},
            "minecraft:emitter_shape_point": {"offset": [0, 0, 0], "direction": ["math.random(-0.25, 0.25)", 1.0, "math.random(-0.25, 0.25)"]},
            "minecraft:particle_initial_speed": 0.55,
            "minecraft:particle_initial_spin": {"rotation": "math.random(0, 360)", "rotation_rate": "variable.spin"},
            "minecraft:particle_lifetime_expression": {"max_lifetime": "math.random(5, 8)"},
            "minecraft:particle_motion_dynamic": {"linear_acceleration": ["math.random(-0.04, 0.04) + 0.02", 0.12, "math.random(-0.04, 0.04)"], "linear_drag_coefficient": 0.5},
            "minecraft:particle_appearance_billboard": {
                "size": ["0.6 + 0.22 * variable.particle_age", "0.6 + 0.22 * variable.particle_age"],
                "facing_camera_mode": "lookat_xyz",
                "uv": {"texture_width": 64, "texture_height": 768,
                       "flipbook": {"base_UV": [0, 0], "size_UV": [64, 64], "step_UV": [0, 64], "frames_per_second": 4, "max_frame": 12, "stretch_to_lifetime": True, "loop": False}}},
            "minecraft:particle_appearance_tinting": {"color": {"interpolant": "variable.particle_age / variable.particle_lifetime",
                "gradient": {"0.0": "#00A8A49E", "0.1": "#B4A8A49E", "0.6": "#80B0ACA6", "1.0": "#00B8B4AE"}}},
        }}}

def fog_smoke_room():
    # command-layer fog (top of the stack): distance haze only; volumetric props fall through to the biome's VV values
    return {"format_version": "1.21.90", "minecraft:fog_settings": {
        "description": {"identifier": "pw:smoke_room"},
        "distance": {"air": {"fog_start": 0.0, "fog_end": 7.0, "fog_color": "#6B6660", "render_distance_type": "fixed",
                             "transition_fog": {"init_fog": {"fog_start": 0.0, "fog_end": 60.0, "fog_color": "#6B6660", "render_distance_type": "fixed"},
                                                "min_percent": 0.2, "mid_seconds": 2, "mid_percent": 0.7, "max_seconds": 6}}}}}

# =============================================================================================
# LEDGERS + MANIFESTS
# =============================================================================================
def needs_hash(rows):
    return hashlib.sha256(json.dumps(sorted([list(r) for r in rows])).encode()).hexdigest()[:16]

def bp_ledger_update(text, new_rows):
    rows = set(re.findall(r'^\|(\w+)\|`([^`]+)`\|$', text, re.M))
    rows |= set(new_rows)
    body = "\n".join(f"|{t}|`{i}`|" for t, i in sorted(rows))
    ver = ".".join(map(str, BP_VER))
    return f"# PW-DEPENDENCIES — BP-02 Tectonic BP\n\nv{ver} · needs-hash `{needs_hash(rows)}`\n\n|type|identifier|\n|---|---|\n{body}\n", len(rows)

def bump_manifest(man, ver, name_re, new_name, description):
    man["header"]["name"] = new_name
    man["header"]["description"] = description
    man["header"]["version"] = list(ver)
    for m in man.get("modules", []): m["version"] = list(ver)
    return man

# =============================================================================================
# BUILD
# =============================================================================================
def main():
    for p in (BP_OUT, RP04_OUT, RP02_OUT):
        if p.exists(): shutil.rmtree(p)
    # --- BP-02: copy the .177 tree
    shutil.copytree(BP_SRC, BP_OUT)
    # --- RP-04 / RP-02: extract
    with zipfile.ZipFile(RP04_ZIP) as z: z.extractall(RP04_OUT)
    with zipfile.ZipFile(RP02_ZIP) as z: z.extractall(RP02_OUT)

    counts = {"blocks": 0, "recipes": 0}
    lang = []
    needs = set()
    # ---------------- BP-02 blocks + recipes ----------------
    for mid, (name, item, side, top) in OUTER.items():
        for fn, obj in ((f"pw_hearth_{mid}", hearth_block(mid, name, item, side, top)),
                        (f"pw_flue_{mid}", flue_block(mid, name, item, side, top)),
                        (f"pw_wall_{mid}", wall_block(mid, name, item, side, top))):
            jdump(obj, BP_OUT / "blocks" / f"{fn}.json"); counts["blocks"] += 1
        for fn, r in recipes_for(mid, item):
            jdump(r, BP_OUT / "recipes" / f"{fn}.json"); counts["recipes"] += 1
        lang += [f"tile.pw:hearth_{mid}.name=Hearth ({name})", f"tile.pw:flue_{mid}.name=Flue ({name})", f"tile.pw:wall_{mid}.name=Dual Wall ({name})"]
        needs |= {("terrain_key", matkey(mid)), ("terrain_key", matkey(mid, top=True))}
        for inner in INNER16: needs.add(("terrain_key", matkey(inner)))
    for wid, (wname, planks, side, end) in RAFTER_WOODS.items():
        jdump(rafter_block(wid, wname, planks, side, end), BP_OUT / "blocks" / f"pw_rafter45_{wid}.json"); counts["blocks"] += 1
        jdump(recipe_shaped(f"pw:rafter45_{wid}", ["P  ", " P ", "  P"], {"P": {"item": planks}}, f"pw:rafter45_{wid}", 3, planks),
              BP_OUT / "recipes" / f"pw_rafter45_{wid}.json"); counts["recipes"] += 1
        lang.append(f"tile.pw:rafter45_{wid}.name=Rafter 45° ({wname})")
        needs |= {("terrain_key", rafterkey(wid)), ("terrain_key", rafterkey(wid, end=True))}
    needs |= {("geometry", g) for g in ("geometry.pw_hearth_cold", "geometry.pw_hearth_fueled", "geometry.pw_hearth_lit", "geometry.pw_hearth_embers", "geometry.pw_flue_cap", "geometry.pw_rafter45")}
    needs |= {("terrain_key", k) for k in ("pw_hearth_soot", "pw_hearth_ash", "pw_hearth_embers", "pw_hearth_log", "pw_hearth_log_end", "pw_hearth_flame")}

    # ---------------- BP-02 scripts ----------------
    for f in ("pw_homestead.js", "pw_homestead_logic.js"):
        shutil.copy(SRC / f, BP_OUT / "scripts" / f)
    mats = {"HEARTH_IDS": [f"pw:hearth_{m}" for m in OUTER], "FLUE_IDS": [f"pw:flue_{m}" for m in OUTER],
            "WALL_IDS": [f"pw:wall_{m}" for m in OUTER], "RAFTER_IDS": [f"pw:rafter45_{w}" for w in RAFTER_WOODS], "INNER16": list(INNER16)}
    js = "// pw_homestead_materials.js — GENERATED by tools/homestead_build.py from homestead_materials.py. Do not edit by hand.\n"
    for k, v in mats.items(): js += f"export const {k} = {json.dumps(v)};\n"
    (BP_OUT / "scripts/pw_homestead_materials.js").write_text(js, encoding="utf-8")
    main_js = (BP_OUT / "scripts/main.js").read_text(encoding="utf-8")
    anchor = 'import "./pw_companion.js"; // PW-C2 companion module (roof family port, dossier-cited)\n'
    assert anchor in main_js, "main.js import anchor not found"
    main_js = main_js.replace(anchor, anchor + 'import "./pw_homestead.js"; // HOMESTEAD: hearth / flue / dual wall / rafter (v1.3.178)\n', 1)
    (BP_OUT / "scripts/main.js").write_text(main_js, encoding="utf-8")

    # ---------------- BP-02 manifest + ledger ----------------
    man = json.loads((BP_OUT / "manifest.json").read_text(encoding="utf-8-sig"))
    desc = (f"v1.3.178 ({DATE}) HOMESTEAD — hearth / flue / dual wall / rafter families, one block per material (53 build materials: "
            f"pw:hearth_<m>, pw:flue_<m>, pw:wall_<m>) + pw:rafter45_oak/spruce; 161 recipes; scripts/pw_homestead.js (+_logic, +_materials) "
            f"imported by main.js. Hearth: fuel planks 1/4 day, log 1/2 day, coal 1 day; flint & steel from cold-with-fuel only; fuel on lit/embers "
            f"never relights; embers = 2x the lit phase. Smoke: chute walk through pw:flue (auto-cap), room fill by bounded flood-fill, level 0..15, "
            f"pw:room_smoke / pw:chimney_smoke particles + pw:smoke_room fog (RP-02 v2.0.2). Rafters: no collision, slowness inside. "
            f"Everything else byte-identical to v1.3.177. Pair with RP-04 v1.3.128 + RP-02 v2.0.2.")
    bump_manifest(man, BP_VER, None, "AbsolutRealism Tectonic BP v1.3.178", desc)
    jdump(man, BP_OUT / "manifest.json")
    led, nrows = bp_ledger_update((BP_OUT / "PW-DEPENDENCIES.md").read_text(encoding="utf-8"), needs)
    (BP_OUT / "PW-DEPENDENCIES.md").write_text(led, encoding="utf-8")

    # ---------------- RP-04: geometry, textures, keys, lang, manifest ----------------
    jdump(build_geometry_file(), RP04_OUT / "models/blocks/pw_homestead.geo.json")
    src = np.asarray(Image.open(RP04_OUT / "textures/blocks/stone_bricks_v13.png").convert("RGBA"))
    tb = RP04_OUT / "textures/blocks"
    for nm, (rgba, mers) in {"pw_hearth_soot": tex_soot(src), "pw_hearth_ash": tex_ash(), "pw_hearth_embers": tex_embers()}.items():
        Image.fromarray(rgba, "RGBA").save(tb / f"{nm}.png")
        Image.fromarray(mers, "RGBA").save(tb / f"{nm}_mers.png")
        jdump(texture_set(nm, f"{nm}_mers"), tb / f"{nm}.texture_set.json")
    ttp = RP04_OUT / "textures/terrain_texture.json"
    tt = json.loads(ttp.read_text(encoding="utf-8-sig"))
    add = {"pw_hearth_soot": "textures/blocks/pw_hearth_soot", "pw_hearth_ash": "textures/blocks/pw_hearth_ash",
           "pw_hearth_embers": "textures/blocks/pw_hearth_embers",
           "pw_hearth_log": "textures/blocks/oak_log_v0", "pw_hearth_log_end": "textures/blocks/log_top_oak_v1"}
    def first_path(entry):
        t = entry.get("textures")
        if isinstance(t, str): return t
        if isinstance(t, list): return t[0] if isinstance(t[0], str) else t[0].get("path")
        if isinstance(t, dict) and "variations" in t:
            v = t["variations"][0]; return v.get("path") if isinstance(v, dict) else v
        return t.get("path")
    td = tt["texture_data"]
    for mid, (name, item, side, top) in OUTER.items():
        if matkey(mid) != side: add[matkey(mid)] = first_path(td[side])
        if top != side and matkey(mid, top=True) != top: add[matkey(mid, top=True)] = first_path(td[top])
    for wid, (wname, planks, side, end) in RAFTER_WOODS.items():
        if rafterkey(wid) != side: add[rafterkey(wid)] = first_path(td[side])
        if rafterkey(wid, end=True) != end: add[rafterkey(wid, end=True)] = first_path(td[end])
    add["pw_hearth_flame"] = "textures/blocks/fire_0"
    for k, p in add.items():
        assert k not in td, f"key collision {k}"
        assert (RP04_OUT / (p + ".png")).exists(), f"{k}: {p}.png missing"
        td[k] = {"textures": p}
    ttp.write_text(json.dumps(tt, indent=1) + "\n", encoding="utf-8")
    fbp = RP04_OUT / "textures/flipbook_textures.json"
    fb = json.loads(fbp.read_text(encoding="utf-8-sig"))
    flame = dict([e for e in fb if e.get("atlas_tile") == "fire_0"][0]); flame["atlas_tile"] = "pw_hearth_flame"; fb.append(flame)
    fbp.write_text(json.dumps(fb, indent=1) + "\n", encoding="utf-8")
    (RP04_OUT / "texts").mkdir(exist_ok=True)
    (RP04_OUT / "texts/en_US.lang").write_text("\n".join(lang) + "\n", encoding="utf-8")
    (RP04_OUT / "texts/languages.json").write_text('[\n "en_US"\n]\n', encoding="utf-8")
    man = json.loads((RP04_OUT / "manifest.json").read_text(encoding="utf-8-sig"))
    desc = (f"v1.3.128 ({DATE}) HOMESTEAD — geometries for the hearth (4 phases: cold/fueled/lit/embers; 2-cube back skin, soot liner, ember bed, "
            f"crossed logs, fire_0 flame quads), the capped flue and the 45° rafter (models/blocks/pw_homestead.geo.json); generated textures "
            f"pw_hearth_soot/ash/embers (+MERS, embers emissive) from the Patrix stone brick; 5 terrain keys; texts/en_US.lang for the 161 new "
            f"BP-02 blocks. Every existing file byte-identical to v1.3.127. Pair with BP-02 v1.3.178.")
    bump_manifest(man, RP04_VER, None, "AbsolutRealism Basic RP v1.3.128", desc)
    jdump(man, RP04_OUT / "manifest.json")
    ledp = RP04_OUT / "PW-DEPENDENCIES.md"
    ledp.write_text(ledp.read_text(encoding="utf-8").replace("v1.3.127 ·", "v1.3.128 ·", 1), encoding="utf-8")

    # ---------------- RP-02: particles + sprite + fog + manifest ----------------
    jdump(particle_room_smoke(), RP02_OUT / "particles/pw_room_smoke.json")
    jdump(particle_chimney_smoke(), RP02_OUT / "particles/pw_chimney_smoke.json")
    (RP02_OUT / "textures/particle").mkdir(parents=True, exist_ok=True)
    Image.fromarray(tex_smoke_sprite(), "RGBA").save(RP02_OUT / "textures/particle/pw_smoke.png")
    jdump(fog_smoke_room(), RP02_OUT / "fogs/pw_smoke_room_fog_setting.json")
    man = json.loads((RP02_OUT / "manifest.json").read_text(encoding="utf-8-sig"))
    desc = (f"v2.0.2 ({DATE}) HOMESTEAD SMOKE — particles pw:room_smoke (block-colliding, slow rise, 9–15 s) and pw:chimney_smoke, their "
            f"sprite textures/particle/pw_smoke.png, and the command-layer fog pw:smoke_room (distance haze only; volumetric falls through) "
            f"pushed on players inside a smoke-filled room by BP-02 v1.3.178. Every existing file byte-identical to v2.0.1.")
    bump_manifest(man, RP02_VER, None, "AbsolutRealism Atmospheric Effects RP v2.0.2", desc)
    jdump(man, RP02_OUT / "manifest.json")

    print(f"built: {counts['blocks']} blocks, {counts['recipes']} recipes, ledger rows {nrows}, lang lines {len(lang)}")
    print("trees:", BP_OUT, RP04_OUT, RP02_OUT)

if __name__ == "__main__":
    main()
