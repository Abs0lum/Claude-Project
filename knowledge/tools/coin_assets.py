#!/usr/bin/env python3
"""coin_assets.py — the GOLD COIN's art + geometry (v1.3.219, his G1-G4): writes _docs/coin/
  textures/blocks/pw_gold_coin_pile.png (32 x 32: coin face 0..15 x 0..15, reeded edge 16..31 x 0..15, darker face below)
  textures/blocks/pw_gold_coin_pile_mer.png + pw_gold_coin_pile.texture_set.json (gold: metalness 0.95, roughness 0.30)
  textures/items/pw_gold_coin.png (32 x 32 icon: one coin, slightly turned, embossed crown mark)
  models/blocks/pw_gold_coin_pile.geo.json: 16 coins c1..c16 (each a disc = 2 crossed boxes, 1 px thick), four stacks of
  four, the k-th coin on stack (k-1) % 4 at level (k-1) // 4, small offsets so the stacks look hand-piled.
  The BP block shows coin k when q.block_state('pw:count') >= k (bone_visibility).
Usage: coin_assets.py"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path("/home/claude/_docs/coin")
GOLD = (212, 165, 32)
GOLD_HI = (250, 214, 92)
GOLD_LO = (150, 108, 18)
GOLD_EDGE = (176, 128, 24)


def coin_face(size=16, turned=False):
    """a round gold coin face: rim, field, a raised crown-and-dot mark, light from the upper left."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = im.load()
    c = (size - 1) / 2
    r = size / 2 - 0.3
    for y in range(size):
        for x in range(size):
            dx, dy = x - c, (y - c) * (1.25 if turned else 1.0)
            d = math.hypot(dx, dy)
            if d > r:
                continue
            light = 0.5 - (dx + dy) / (2.2 * r)                      # upper-left light
            if d > r - 1.6:                                         # the rim
                col = GOLD_HI if light > 0.55 else GOLD if light > 0.35 else GOLD_LO
            else:
                col = GOLD if light > 0.4 else (196, 150, 28)
            px[x, y] = col + (255,)
    # the mark: a small crown (three points on a band) and a dot below, embossed (light edge up-left, dark down-right)
    s = size / 16
    mark = [(5, 6), (8, 5), (11, 6), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8), (8, 11)]
    for (mx, my) in mark:
        x, y = int(mx * s), int(my * s * (1 / 1.25 if turned else 1)) + (2 if turned else 0)
        if 0 <= x < size and 0 <= y < size and px[x, y][3]:
            px[x, y] = GOLD_HI + (255,)
            if x + 1 < size and y + 1 < size and px[x + 1, y + 1][3]:
                px[x + 1, y + 1] = GOLD_LO + (255,)
    return im


def edge_strip(w=16, h=16):
    """the reeded edge: fine vertical grooves."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    px = im.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (GOLD_HI if x % 2 == 0 else GOLD_EDGE) + (255,)
    return im


def main():
    (OUT / "textures/blocks").mkdir(parents=True, exist_ok=True)
    (OUT / "textures/items").mkdir(parents=True, exist_ok=True)
    (OUT / "models/blocks").mkdir(parents=True, exist_ok=True)
    tex = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    tex.paste(coin_face(16), (0, 0))
    tex.paste(edge_strip(), (16, 0))
    under = coin_face(16)
    under = Image.eval(under, lambda v: v)                            # same disc, darker (the underside)
    up = under.load()
    for y in range(16):
        for x in range(16):
            r, g, b, a = up[x, y]
            up[x, y] = (int(r * 0.72), int(g * 0.72), int(b * 0.72), a)
    tex.paste(under, (0, 16))
    tex.paste(edge_strip(), (16, 16))
    tex.save(OUT / "textures/blocks/pw_gold_coin_pile.png")
    # MER: red metalness, green emissive, blue roughness
    mer = Image.new("RGBA", (32, 32), (242, 0, 77, 255))
    mer.save(OUT / "textures/blocks/pw_gold_coin_pile_mer.png")
    (OUT / "textures/blocks/pw_gold_coin_pile.texture_set.json").write_text(json.dumps({
        "format_version": "1.21.30",
        "minecraft:texture_set": {"color": "pw_gold_coin_pile", "metalness_emissive_roughness": "pw_gold_coin_pile_mer"}}, indent=1))
    icon = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    face = coin_face(26, turned=True)
    icon.paste(face, (3, 5), face)
    # the coin's thickness under the turned face (2 px of edge)
    ip = icon.load()
    for x in range(32):
        col = [y for y in range(32) if ip[x, y][3]]
        if col:
            yb = max(col)
            for k in (1, 2):
                if yb + k < 32:
                    ip[x, yb + k] = GOLD_EDGE + (255,) if (x % 2) else GOLD_LO + (255,)
    icon.save(OUT / "textures/items/pw_gold_coin.png")

    # geometry: 16 coins (4 stacks x 4), each coin = two crossed boxes 5x1x3 and 3x1x5 px (a round-ish disc, 5 px across)
    stacks = [(-6.5, -6.0), (1.5, -6.5), (-6.0, 1.5), (1.8, 1.6)]
    jitter = [(0, 0), (0.4, -0.3), (-0.3, 0.2), (0.2, 0.4)]
    bones = [{"name": "root", "pivot": [0, 0, 0]}]
    # one 5 x 1 x 5 box per coin; the round face (transparent corners, alpha_test) on top and below, the reeded edge round
    face_uv = lambda: {"north": {"uv": [16, 0], "uv_size": [16, 1]}, "south": {"uv": [16, 2], "uv_size": [16, 1]},
                       "east": {"uv": [16, 4], "uv_size": [16, 1]}, "west": {"uv": [16, 6], "uv_size": [16, 1]},
                       "up": {"uv": [0, 0], "uv_size": [16, 16]}, "down": {"uv": [0, 16], "uv_size": [16, 16]}}
    for k in range(16):
        sx, sz = stacks[k % 4]
        jx, jz = jitter[(k // 4) % 4]
        y = (k // 4) * 1.0
        x0, z0 = sx + jx, sz + jz
        cubes = [{"origin": [x0, y, z0], "size": [5, 1, 5], "uv": face_uv()}]
        bones.append({"name": f"c{k + 1}", "parent": "root", "pivot": [x0 + 2.5, y, z0 + 2.5], "cubes": cubes})
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.pw_gold_coin_pile", "texture_width": 32, "texture_height": 32,
                        "visible_bounds_width": 2, "visible_bounds_height": 1.5, "visible_bounds_offset": [0, 0.25, 0]},
        "bones": bones}]}
    (OUT / "models/blocks/pw_gold_coin_pile.geo.json").write_text(json.dumps(geo, indent=1))
    # every cube inside the block's 16 x 16 x 16 cell (the engine rejects a block model that leaves it)
    for b in bones[1:]:
        for c in b["cubes"]:
            (ox, oy, oz), (sx2, sy2, sz2) = c["origin"], c["size"]
            assert -8 <= ox and ox + sx2 <= 8 and 0 <= oy and oy + sy2 <= 16 and -8 <= oz and oz + sz2 <= 8, (b["name"], c)
    print(f"coin assets -> {OUT}")


if __name__ == "__main__":
    main()
