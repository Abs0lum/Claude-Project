#!/usr/bin/env python3
"""civ_preview.py — review sheet for a generated CIVITAS building: an isometric cut-away view (front-left, roof on),
the same with the roof lifted off, and one floor plan per storey (basement, ground, loft) with every marker drawn.
Colours are flat per block family (a quick read of layout, not the textures). Usage: civ_preview.py MANIFEST.json OUT.png"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

COL = {
    "minecraft:oak_planks": (176, 138, 86), "minecraft:spruce_log": (92, 64, 40), "minecraft:stone_bricks": (128, 128, 124),
    "minecraft:cobblestone": (110, 110, 106), "minecraft:smooth_stone": (160, 160, 156), "minecraft:dirt": (122, 88, 58),
    "minecraft:grass_block": (96, 150, 70), "minecraft:glass_pane": (170, 210, 230), "minecraft:wooden_door": (150, 105, 60),
    "minecraft:ladder": (190, 150, 90), "minecraft:bed": (180, 40, 40), "minecraft:chest": (160, 110, 40),
    "minecraft:barrel": (130, 90, 50), "pw:roof45_spruce": (84, 60, 44), "pw:hearth_oak_planks": (200, 90, 40),
    "pw:flue_oak_planks": (150, 120, 90), "pw:manhole_cover": (70, 70, 70), "minecraft:light_block_14": None,
    "minecraft:air": None,
}
MARK = {"zone": (40, 200, 255), "station": (255, 210, 0), "port": (255, 0, 200), "datum": (255, 255, 255), "pw:hatch_lid": (0, 255, 120)}


def colour(name):
    if name in COL:
        return COL[name]
    if name.startswith("pw:furn_"):
        return (200, 160, 110)
    if name.startswith("pw:roof"):
        return (84, 60, 44)
    return (200, 0, 200)


def iso(blocks, size, cut_feet=None, datum=15, s=14, min_feet=-1):
    """isometric view of the street front (x = 0) and the z = W side, painter's order.
    Only feet >= min_feet are drawn (the ground and the building, not the buried section)."""
    sx, sy, sz = size
    base = min_feet + datum                                  # box row drawn at the bottom
    rmax = sy - 1 - base
    W = (sx + sz) * s + 2 * s + 20
    H = (sx + sz) * s // 2 + (rmax + 2) * s + 20
    im = Image.new("RGB", (W, H), (28, 30, 36))
    d = ImageDraw.Draw(im)
    ox, oy = sz * s + s + 10, (rmax + 1) * s + 10
    grid = {}
    for x, y, z, name, _ in blocks:
        c = colour(name)
        if c is None or y < base or (cut_feet is not None and y - datum > cut_feet):
            continue
        grid[(x, y, z)] = c
    for (x, y, z) in sorted(grid, key=lambda p: ((sx - 1 - p[0]) + p[2], p[1])):
        c = grid[(x, y, z)]
        xm = sx - 1 - x                                      # mirrored so the street front (x = 0) faces the viewer
        px, py = ox + (xm - z) * s, oy + (xm + z) * s // 2 - (y - base) * s
        top = [(px, py - s // 2), (px + s, py), (px, py + s // 2), (px - s, py)]
        left = [(px - s, py), (px, py + s // 2), (px, py + s // 2 + s), (px - s, py + s)]
        right = [(px, py + s // 2), (px + s, py), (px + s, py + s), (px, py + s // 2 + s)]
        d.polygon(top, fill=c)
        d.polygon(left, fill=tuple(int(v * 0.72) for v in c))
        d.polygon(right, fill=tuple(int(v * 0.55) for v in c))
    return im


def plan(blocks, ents, size, feet, datum=15, s=26):
    sx, sy, sz = size
    im = Image.new("RGB", (sx * s + 2, sz * s + 2), (20, 22, 26))
    d = ImageDraw.Draw(im)
    for x, y, z, name, _ in blocks:
        if y - datum != feet:
            continue
        c = colour(name)
        if c is None:
            continue
        d.rectangle([x * s + 1, z * s + 1, x * s + s - 1, z * s + s - 1], fill=c)
        if name.startswith("pw:furn_") or name in ("minecraft:bed", "minecraft:chest", "minecraft:barrel", "minecraft:ladder",
                                                   "pw:hearth_oak_planks", "minecraft:wooden_door", "pw:manhole_cover"):
            d.text((x * s + 3, z * s + 6), name.split(":")[1][:4].replace("furn", "").strip("_")[:4], fill=(0, 0, 0))
    for e in ents:
        x, f, z = e["cell"]
        if f != feet:
            continue
        col = MARK["pw:hatch_lid"] if e["id"] == "pw:hatch_lid" else MARK[e["fam"]]
        d.ellipse([x * s + s - 11, z * s + 3, x * s + s - 3, z * s + 11], fill=col, outline=(0, 0, 0))
    return im


def section(blocks, size, zcut, datum=15, s=12):
    """vertical section along the depth at frontage column zcut (street on the left)."""
    sx, sy, sz = size
    im = Image.new("RGB", (sx * s + 2, sy * s + 2), (20, 22, 26))
    d = ImageDraw.Draw(im)
    for x, y, z, name, _ in blocks:
        if z != zcut:
            continue
        c = colour(name)
        if c is None:
            continue
        yy = (sy - 1 - y) * s
        d.rectangle([x * s + 1, yy + 1, x * s + s - 1, yy + s - 1], fill=c)
    d.line([0, (sy - 1 - datum) * s + s, sx * s, (sy - 1 - datum) * s + s], fill=(255, 255, 255))
    return im


def sheet(man_path, out):
    m = json.loads(Path(man_path).read_text())
    blocks, size, ents, datum = m["blocks"], m["size"], m["entities"], m["datum_y"]
    a = iso(blocks, size, cut_feet=None, datum=datum)
    b = iso(blocks, size, cut_feet=4, datum=datum)
    plans = [(f, plan(blocks, ents, size, f, datum)) for f in (-5, 0, 4)]
    sec = section(blocks, size, size[2] // 2, datum)
    W = max(a.width + b.width + sec.width + 40, sum(p.width + 40 for _, p in plans) + 10)
    H = max(a.height, b.height, sec.height) + max(p.height for _, p in plans) + 110
    S = Image.new("RGB", (W, H), (16, 17, 20))
    d = ImageDraw.Draw(S)
    d.text((10, 6), f"{m['name']}  box {size[0]}x{size[1]}x{size[2]} (depth x height x frontage+clearance)  ·  "
                    f"left: roof on · right: cut at the loft floor  ·  plans: basement -5 · ground 0 · loft +4", fill=(235, 235, 235))
    S.paste(a, (10, 24))
    S.paste(b, (a.width + 20, 24))
    S.paste(sec, (a.width + b.width + 30, 24))
    d.text((a.width + b.width + 30, 24 + sec.height + 4), "section (street left, white = datum)", fill=(200, 200, 200))
    x = 10
    y0 = max(a.height, b.height, sec.height) + 60
    for f, p in plans:
        d.text((x, y0 - 14), f"plan feet {f:+d}", fill=(220, 220, 220))
        S.paste(p, (x, y0))
        x += p.width + 40
    d.text((10, H - 30), "plans: street = LEFT edge (x = 0, the door wall); clearance column = TOP row (z = 0)", fill=(200, 200, 200))
    d.text((10, H - 16), "markers: blue = zone corner · yellow = station · magenta = port · white = datum · green = ladder hatch",
           fill=(200, 200, 200))
    S.save(out)
    return S.size


if __name__ == "__main__":
    print(sheet(sys.argv[1], sys.argv[2]))
