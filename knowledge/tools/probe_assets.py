#!/usr/bin/env python3
"""probe_assets.py — the pw:probe ROTATION-LAW CHART entity (PW-TestRunner RP 0.2.0 + BP 0.2.0; D-C257, PHASE0-PROTOCOL §2).

Writes:
  RP: entity/pw_probe.entity.json · models/entity/pw_probe.geo.json · textures/entity/pw_probe.png (64x64 colour chart)
      animations/pw_probe.animation.json · animation_controllers/pw_probe.animation_controllers.json
      render_controllers/pw_probe.render_controllers.json
  BP: entities/pw_probe.json (floats, no AI, cannot be pushed or hurt; property pw:anim set by event pw:t6)
  figure: _design/p0-probe-predicted.png — what the VERIFIED law predicts he will see in shots A/B/C/D
          (world view: the probe faces SOUTH, he stands SOUTH of it looking NORTH; file -z = the model's front,
          file +x = the model's LEFT = world EAST when it faces south; world = file with z mirrored)

Every bone is a solid colour from the chart; the bars start at their pivot so "the tip" is unambiguous.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from entity_render import cubes_from_bones, render

SWATCH = {"yellow": (0, 0, (240, 220, 40)), "red": (16, 0, (220, 40, 40)), "blue": (32, 0, (40, 80, 230)), "grey": (48, 0, (150, 150, 150)),
          "green": (0, 16, (40, 200, 60)), "orange": (16, 16, (245, 140, 20)), "cyan": (32, 16, (40, 210, 220)), "magenta": (48, 16, (220, 40, 200))}


def face_uv(u, v, size):
    w, h, d = size
    return {"north": {"uv": [u, v], "uv_size": [w, h]}, "south": {"uv": [u, v], "uv_size": [w, h]}, "east": {"uv": [u, v], "uv_size": [d, h]},
            "west": {"uv": [u, v], "uv_size": [d, h]}, "up": {"uv": [u, v], "uv_size": [w, d]}, "down": {"uv": [u, v], "uv_size": [w, d]}}


def cube(origin, size, colour):
    u, v, _ = SWATCH[colour]
    return {"origin": origin, "size": size, "uv": face_uv(u, v, size)}


# bone: (name, pivot, rotation, colour, cube origin, cube size)
BONES = [
    ("core", [0, 24, 0], [0, 0, 0], "grey", [-2, 22, -2], [4, 4, 4]),
    ("nose", [0, 24, -2], [0, 0, 0], "yellow", [-2, 22, -5], [4, 4, 3]),          # the model's FRONT (file -z)
    ("left_mark", [2, 24, 0], [0, 0, 0], "red", [2, 22, -2], [4, 4, 4]),          # file +x = the model's LEFT
    ("right_mark", [-2, 24, 0], [0, 0, 0], "blue", [-6, 22, -2], [4, 4, 4]),      # file -x = the model's RIGHT
    ("zbar", [0, 26, 0], [0, 0, 30], "green", [-1, 26, -1], [2, 10, 2]),           # T1: Z sign
    ("ybar", [0, 20, 0], [0, 45, 0], "orange", [0, 19, -1], [10, 2, 2]),           # T2: Y sign (bar toward file +x)
    ("xbar", [0, 16, 0], [30, 0, 0], "cyan", [-1, 15, -10], [2, 2, 10]),           # T3: X sign (bar toward the front)
    ("cbar", [0, 4, 0], [45, 45, 0], "magenta", [-1, 4, -1], [2, 8, 2]),           # T5: order
]
COLOURS = {n: SWATCH[c][2] for n, _, _, c, _, _ in BONES}


def geometry():
    bones = []
    for name, pivot, rot, colour, o, s in BONES:
        b = {"name": name, "pivot": pivot, "cubes": [cube(o, s, colour)]}
        if any(rot): b["rotation"] = rot
        bones.append(b)
    return {"format_version": "1.16.0", "minecraft:geometry": [{"description": {"identifier": "geometry.pw_probe", "texture_width": 64, "texture_height": 64,
                                                                                 "visible_bounds_width": 3, "visible_bounds_height": 3, "visible_bounds_offset": [0, 1.25, 0]},
                                                                 "bones": bones}]}


def texture(path):
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for name, (u, v, rgb) in SWATCH.items(): d.rectangle([u, v, u + 15, v + 15], fill=rgb + (255,))
    im.save(path)


def client_entity():
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": "pw:probe", "materials": {"default": "entity_alphatest"}, "textures": {"default": "textures/entity/pw_probe"},
        "geometry": {"default": "geometry.pw_probe"}, "animations": {"t6": "animation.pw_probe.t6", "ctrl": "controller.animation.pw_probe"},
        "scripts": {"animate": ["ctrl"]}, "render_controllers": ["controller.render.pw_probe"]}}}


def animation():
    # Bedrock animations ADD to the bind pose (T6): xbar +30 X on top of the file's 30; zbar rises 8 cubes (half a block)
    return {"format_version": "1.8.0", "animations": {"animation.pw_probe.t6": {"loop": True, "bones": {"xbar": {"rotation": [30, 0, 0]}, "zbar": {"position": [0, 8, 0]}}}}}


def animation_controller():
    return {"format_version": "1.10.0", "animation_controllers": {"controller.animation.pw_probe": {"initial_state": "default", "states": {
        "default": {"transitions": [{"t6": "q.property('pw:anim')"}]},
        "t6": {"animations": ["t6"], "transitions": [{"default": "!q.property('pw:anim')"}]}}}}}


def render_controller():
    return {"format_version": "1.10.0", "render_controllers": {"controller.render.pw_probe": {"geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"]}}}


def bp_entity():
    return {"format_version": "1.21.80", "minecraft:entity": {
        "description": {"identifier": "pw:probe", "is_spawnable": False, "is_summonable": True, "is_experimental": False,
                        "properties": {"pw:anim": {"type": "bool", "default": False, "client_sync": True}}},
        "components": {
            "minecraft:type_family": {"family": ["pw_probe", "inanimate"]},
            "minecraft:collision_box": {"width": 0.6, "height": 2.4},
            "minecraft:physics": {"has_gravity": False, "has_collision": False},
            "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
            "minecraft:knockback_resistance": {"value": 1.0},
            "minecraft:damage_sensor": {"triggers": [{"cause": "all", "deals_damage": "no"}]},
            "minecraft:health": {"value": 1, "max": 1},
            "minecraft:persistent": {},
            "minecraft:fire_immune": {},
            "minecraft:breathable": {"breathes_air": True, "breathes_water": True, "breathes_lava": True, "breathes_solids": True},
            "minecraft:body_rotation_blocked": {},
            "minecraft:conditional_bandwidth_optimization": {}},
        "events": {"pw:t6": {"set_property": {"pw:anim": True}}, "pw:t6_off": {"set_property": {"pw:anim": False}}}}}


def write_all(rp_dir, bp_dir):
    rp, bp = Path(rp_dir), Path(bp_dir)
    for d in ("entity", "models/entity", "textures/entity", "animations", "animation_controllers", "render_controllers"): (rp / d).mkdir(parents=True, exist_ok=True)
    (bp / "entities").mkdir(parents=True, exist_ok=True)
    dump = lambda p, o: Path(p).write_text(json.dumps(o, indent=1) + "\n", encoding="utf-8")
    dump(rp / "entity/pw_probe.entity.json", client_entity())
    dump(rp / "models/entity/pw_probe.geo.json", geometry())
    texture(rp / "textures/entity/pw_probe.png")
    dump(rp / "animations/pw_probe.animation.json", animation())
    dump(rp / "animation_controllers/pw_probe.animation_controllers.json", animation_controller())
    dump(rp / "render_controllers/pw_probe.render_controllers.json", render_controller())
    dump(bp / "entities/pw_probe.json", bp_entity())


# ----------------------------------------------------------------------------------------------------------------- figure
def bones_for(anim=False):
    bones = []
    for name, pivot, rot, colour, o, s in BONES:
        b = {"name": name, "pivot": list(pivot), "rotation": list(rot), "cubes": [{"origin": list(o), "size": list(s)}]}
        if anim and name == "xbar": b["rotation"] = [rot[0] + 30, rot[1], rot[2]]
        if anim and name == "zbar": b["pivot"][1] += 8; b["cubes"][0]["origin"][1] += 8
        bones.append(b)
    return bones


def to_world(cubes):
    """file frame -> world frame for a probe facing SOUTH: file -z (front) -> world +z (south); file +x (left) -> world +x (east)."""
    return [(bone, [[p[0], p[1], -p[2]] for p in P]) for bone, P in cubes]


def figure(out):
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15); FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    static = to_world(cubes_from_bones(bones_for(False))); anim = to_world(cubes_from_bones(bones_for(True)))
    views = [("A  FRONT: you stand SOUTH of it, look NORTH", "its yellow nose toward you; RED must be on YOUR RIGHT", static, (0, 22, 46), (0, 20, 0)),
             ("B  EAST SIDE: you stand EAST of it, look WEST", "the nose is on your left; the cyan tip points left and DOWN", static, (46, 22, 0), (0, 20, 0)),
             ("C  TOP: fly above it, look DOWN", "north is UP on this picture, east is RIGHT (nose at the bottom)", static, (0, 66, 5), (0, 20, 0)),
             ("D  FRONT again, ANIMATED (pw:t6)", "cyan dips twice as far; green sits half a block higher", anim, (0, 22, 46), (0, 20, 0))]
    W, H = 460, 460
    sheet = Image.new("RGB", (2 * W + 30, 2 * H + 190), (238, 240, 244)); d = ImageDraw.Draw(sheet)
    d.text((10, 8), "pw:probe — what the VERIFIED rotation law predicts you will see (PW-TestRunner 0.2.0, steps q1 / q2)", fill=(20, 20, 20), font=FB)
    d.text((10, 32), "yellow = nose (the model's front) · RED = the model's LEFT (= EAST when it faces south) · BLUE = its right", fill=(60, 60, 60), font=F)
    d.text((10, 50), "green bar [0,0,30] · orange bar [0,45,0] · cyan bar [30,0,0] · magenta bar [45,45,0] · every bar starts at its pivot", fill=(60, 60, 60), font=F)
    for k, (label, sub, cubes, eye, tgt) in enumerate(views):
        im = render(cubes, eye, tgt, fov=60, size=(W, H), colours=COLOURS, ground=None, bg=(214, 224, 236))
        x = 10 + (k % 2) * (W + 10); y = 76 + (k // 2) * (H + 52)
        sheet.paste(im, (x, y)); d.text((x, y + H + 4), label, fill=(20, 20, 20), font=FB); d.text((x, y + H + 26), sub, fill=(60, 60, 60), font=F)
    d.text((10, 2 * H + 172), "If a shot disagrees with its panel, that row's sign or order is inverted in the engine — tell me which panel and how.", fill=(120, 30, 30), font=F)
    sheet.save(out)
    return out


if __name__ == "__main__":
    rp, bp = sys.argv[1], sys.argv[2]
    write_all(rp, bp)
    print("wrote probe assets to", rp, bp)
    if len(sys.argv) > 3: print("figure", figure(sys.argv[3]))
