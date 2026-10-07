#!/usr/bin/env python3
"""build_palace_blocks.py — the two WALK-THROUGH blocks of the palace's hidden world (D-C570, his P3 "both"):
  pw:jib_panel        a full cube that looks like spruce panelling, NO collision: a jib door you walk through (the judges'
                      wardrobe back, the concealed way beside the strongroom). Villagers path through it (no collision).
  pw:secret_painting  a 2 x 2 framed canvas (4 tiles, state pw:tile 0..3: 0 upper-left, 1 upper-right, 2 lower-left,
                      3 lower-right as seen from the canvas side) on a spruce-panelled cube, NO collision: the Tesoretto's
                      door (Palazzo Vecchio / Versailles). Faces the direction of minecraft:cardinal_direction (trait).
BP side: blocks/pw_jib_panel.json, blocks/pw_secret_painting.json (written into a BP build dir).
RP side: textures/blocks/pw_secret_painting_<tile>.png (256 px, Claude-authored: a gilt frame around a landscape — a
hill, a lake, a lone oak, evening sky) + terrain_texture keys + blocks.json sound entries (written into an RP build dir).
Usage: build_palace_blocks.py BP_DIR RP_DIR"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROT = {"south": [0, 0, 0], "north": [0, 180, 0], "east": [0, 90, 0], "west": [0, 270, 0]}     # the kit's convention


def painting(size=512, seed=7):
    """a 2 x 2 block painting: gilt frame (24 px), a landscape in oils — rolling hills, a lake, a lone oak, a warm sky"""
    rng = np.random.default_rng(seed)
    W = H = size
    img = Image.new("RGB", (W, H), (120, 90, 40))
    d = ImageDraw.Draw(img)
    F = 26                                                         # frame width
    # frame: gilt with a bevel and a dark inner lip
    for i in range(F):
        t = i / F
        gold = (int(150 + 90 * math.sin(t * math.pi)), int(110 + 70 * math.sin(t * math.pi)), int(30 + 30 * math.sin(t * math.pi)))
        d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=gold)
    d.rectangle([F, F, W - 1 - F, H - 1 - F], outline=(60, 40, 20)); d.rectangle([F + 1, F + 1, W - 2 - F, H - 2 - F], outline=(90, 60, 30))
    # canvas
    cw, ch = W - 2 * (F + 2), H - 2 * (F + 2)
    cv = Image.new("RGB", (cw, ch))
    px = cv.load()
    for y in range(ch):
        t = y / ch
        # sky: warm evening gradient
        if t < 0.55:
            k = t / 0.55
            r, g, b = 235 - 60 * k, 200 - 70 * k, 150 - 40 * k
            # a sun low on the right
            for x in range(cw):
                dx, dy = x - cw * 0.72, y - ch * 0.42
                s = math.exp(-(dx * dx + dy * dy) / (2 * (cw * 0.06) ** 2))
                px[x, y] = (min(255, int(r + 40 * s)), min(255, int(g + 50 * s)), min(255, int(b + 30 * s)))
        else:
            for x in range(cw):
                px[x, y] = (70, 95, 55)
    cd = ImageDraw.Draw(cv)
    # distant hills (three bands), a lake, a near meadow
    hz = int(ch * 0.55)
    for band, (col, amp, base) in enumerate((((110, 120, 140), 0.06, 0.52), ((85, 110, 80), 0.05, 0.58), ((60, 95, 55), 0.04, 0.64))):
        pts = [(x, int(ch * base + ch * amp * math.sin(x / cw * 6.3 + band) + ch * 0.02 * math.sin(x / cw * 31 + band * 3))) for x in range(0, cw, 4)]
        cd.polygon([(0, ch)] + pts + [(cw, ch)], fill=col)
    cd.rectangle([int(cw * 0.1), int(ch * 0.66), int(cw * 0.6), int(ch * 0.78)], fill=(120, 150, 170))
    cd.ellipse([int(cw * 0.05), int(ch * 0.64), int(cw * 0.65), int(ch * 0.80)], fill=(130, 160, 180))
    cd.polygon([(0, int(ch * 0.74)), (cw, int(ch * 0.70)), (cw, ch), (0, ch)], fill=(75, 110, 50))
    # the oak: trunk + a blobby crown
    tx, ty = int(cw * 0.78), int(ch * 0.80)
    cd.rectangle([tx - 6, ty - 70, tx + 6, ty], fill=(70, 45, 25))
    for i in range(40):
        a = rng.uniform(0, 6.3); r = rng.uniform(0, 60)
        cx, cy = tx + math.cos(a) * r, ty - 90 + math.sin(a) * r * 0.7
        rad = rng.uniform(14, 30)
        g = int(rng.uniform(70, 120))
        cd.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(40, g, 35))
    # brush texture: a little noise + a soft blur, then varnish vignette
    arr = np.asarray(cv).astype(np.float32)
    arr += rng.normal(0, 6, arr.shape)
    yy, xx = np.mgrid[0:ch, 0:cw]
    vig = 1 - 0.25 * (((xx / cw - 0.5) ** 2 + (yy / ch - 0.5) ** 2) * 2)
    arr *= vig[..., None]
    cv = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    img.paste(cv, (F + 2, F + 2))
    return img


def block_jsons(bp):
    jib = {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": "pw:jib_panel", "menu_category": {"category": "construction"}},
        "components": {
            "minecraft:geometry": "minecraft:geometry.full_block",
            "minecraft:material_instances": {"*": {"texture": "spruce_planks", "render_method": "opaque"}},
            "minecraft:collision_box": False,
            "minecraft:selection_box": True,
            "minecraft:destructible_by_mining": {"seconds_to_destroy": 1.5},
            "minecraft:destructible_by_explosion": {"explosion_resistance": 3},
            "minecraft:flammable": {"catch_chance_modifier": 5, "destroy_chance_modifier": 20},
            "minecraft:map_color": "#6b4e2e"}}}
    perms = []
    for dirn, rot in ROT.items():
        for tile in range(4):
            perms.append({"condition": f"q.block_state('minecraft:cardinal_direction') == '{dirn}' && q.block_state('pw:tile') == {tile}",
                          "components": {"minecraft:transformation": {"rotation": rot},
                                         "minecraft:material_instances": {"*": {"texture": "spruce_planks", "render_method": "opaque"},
                                                                          "north": {"texture": f"pw_secret_painting_{tile}", "render_method": "opaque", "face_dimming": False, "ambient_occlusion": False}}}})
    paint = {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": "pw:secret_painting", "menu_category": {"category": "construction"},
                        "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"], "y_rotation_offset": 180}},
                        "states": {"pw:tile": [0, 1, 2, 3]}},
        "components": {
            "minecraft:geometry": "minecraft:geometry.full_block",
            "minecraft:material_instances": {"*": {"texture": "spruce_planks", "render_method": "opaque"},
                                             "north": {"texture": "pw_secret_painting_0", "render_method": "opaque", "face_dimming": False, "ambient_occlusion": False}},
            "minecraft:collision_box": False,
            "minecraft:selection_box": True,
            "minecraft:destructible_by_mining": {"seconds_to_destroy": 1.5},
            "minecraft:destructible_by_explosion": {"explosion_resistance": 3},
            "minecraft:map_color": "#6b4e2e"},
        "permutations": perms}}
    (bp / "blocks/pw_jib_panel.json").write_text(json.dumps(jib, indent=1))
    (bp / "blocks/pw_secret_painting.json").write_text(json.dumps(paint, indent=1))


def rp_assets(rp):
    img = painting()
    out = rp / "textures/blocks"
    tiles = {0: (0, 0), 1: (256, 0), 2: (0, 256), 3: (256, 256)}
    for t, (x, y) in tiles.items():
        img.crop((x, y, x + 256, y + 256)).save(out / f"pw_secret_painting_{t}.png", optimize=True)
    img.save(Path("/home/claude/_docs/palace/secret-painting-512.png"))
    tp = rp / "textures/terrain_texture.json"
    tt = json.loads(tp.read_text())
    for t in range(4):
        tt["texture_data"][f"pw_secret_painting_{t}"] = {"textures": f"textures/blocks/pw_secret_painting_{t}"}
    tp.write_text(json.dumps(tt, indent=1))
    bj = rp / "blocks.json"
    import re
    txt = re.sub(r"(?m)^\s*//.*$", "", bj.read_text(encoding="utf-8-sig"))
    b = json.loads(txt)
    b["pw:jib_panel"] = {"sound": "wood"}
    b["pw:secret_painting"] = {"sound": "wood"}
    bj.write_text(json.dumps(b, indent=1))


if __name__ == "__main__":
    bp, rp = Path(sys.argv[1]), Path(sys.argv[2])
    block_jsons(bp)
    rp_assets(rp)
    print("palace blocks written:", bp / "blocks/pw_jib_panel.json", bp / "blocks/pw_secret_painting.json", "+ RP textures / keys / sounds")
