#!/usr/bin/env python3
"""civ_section.py — a VERTICAL SECTION through a server dump (civ_dump_render's [CIVDUMP] rows): every block of one
world x (a z-section) or one world z (an x-section) coloured by family, so what the clock carved underground (sewer trench,
water, outfall tunnels, the well's shaft, cellars) can be seen. Usage: civ_section.py LOG OUT.png x=<X> | z=<Z> [z0 z1 | x0 x1] [scale]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, "/home/claude/tools")
import civ_dump_render as D  # noqa: E402

COL = [("water", (40, 90, 220)), ("flowing_water", (90, 140, 240)), ("iron_bars", (200, 200, 220)), ("stone_bricks", (150, 150, 155)),
       ("stone_brick", (140, 140, 150)), ("smooth_stone", (190, 190, 190)), ("cobblestone", (120, 120, 120)), ("grass_block", (96, 140, 60)),
       ("grass_path", (150, 125, 80)), ("dirt", (120, 85, 55)), ("stone", (100, 100, 100)), ("andesite", (110, 110, 105)),
       ("diorite", (170, 170, 170)), ("granite", (140, 100, 90)), ("gravel", (135, 130, 125)), ("sand", (210, 195, 150)),
       ("planks", (175, 135, 80)), ("log", (95, 75, 45)), ("leaves", (60, 110, 40)), ("ladder", (160, 120, 60)), ("ramp", (125, 125, 125)),
       ("fence", (120, 90, 50)), ("roof", (110, 80, 50)), ("thatch", (200, 180, 90)), ("door", (200, 60, 60)), ("glass", (180, 220, 240)),
       ("lantern", (255, 220, 120)), ("bed", (220, 80, 120)), ("chest", (170, 120, 60)), ("barrel", (150, 100, 50)), ("hay", (210, 190, 80)),
       ("cauldron", (80, 80, 90)), ("manhole", (90, 90, 100)), ("snow", (235, 240, 245))]


def colour(name):
    n = name.replace("minecraft:", "").replace("pw:", "")
    for k, c in COL:
        if k in n:
            return c
    return (200, 160, 200)


def main():
    log, out = sys.argv[1], sys.argv[2]
    axis, val = sys.argv[3].split("=")
    val = int(val)
    lo = int(sys.argv[4]) if len(sys.argv) > 4 else None
    hi = int(sys.argv[5]) if len(sys.argv) > 5 else None
    scale = int(sys.argv[6]) if len(sys.argv) > 6 else 6
    if axis == "x":
        crop = (val, val, lo, hi) if lo is not None else (val, val, -10**6, 10**6)
    else:
        crop = (lo, hi, val, val) if lo is not None else (-10**6, 10**6, val, val)
    head, blocks = D.parse(log, crop=crop)
    y0 = head["y0"]
    cells = {}
    for x, y, z, name, states in blocks:
        along = z if axis == "x" else x
        cells[(along, y)] = name
    if not cells:
        raise SystemExit("no blocks on that section")
    a0 = min(a for a, _ in cells); a1 = max(a for a, _ in cells)
    ymin = min(y for _, y in cells); ymax = max(y for _, y in cells)
    W, H = (a1 - a0 + 1) * scale, (ymax - ymin + 1) * scale
    im = Image.new("RGB", (W + 60, H + 30), (20, 20, 24))
    d = ImageDraw.Draw(im)
    for (a, y), name in cells.items():
        px = 50 + (a - a0) * scale
        py = 10 + (ymax - y) * scale
        d.rectangle([px, py, px + scale - 1, py + scale - 1], fill=colour(name))
    for y in range(ymin, ymax + 1, 5):
        py = 10 + (ymax - y) * scale
        d.text((2, py), str(y + y0), fill=(230, 230, 230))
    base = head["z0"] if axis == "x" else head["x0"]
    for a in range(a0, a1 + 1, 10):
        d.text((50 + (a - a0) * scale, H + 14), str(base + a), fill=(230, 230, 230))
    d.text((2, 0), f"section {axis}={val} ({'z' if axis == 'x' else 'x'} across, world coords; y up)", fill=(255, 255, 0))
    im.save(out)
    print(out, im.size, "cells", len(cells))


if __name__ == "__main__":
    main()
