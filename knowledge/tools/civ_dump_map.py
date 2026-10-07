#!/usr/bin/env python3
"""civ_dump_map.py — a light PLAN VIEW of a civtest region dump ([CIVDUMP] rows + [CIVPAL] palette): the top block of every
column, coloured by block kind, shaded by height, with contour-ish light. Memory-light (no block list): the true-law
renderer (civ_dump_render.py) was OOM-killed on a 374 x 390 x 110 dump of three towns.
Usage: civ_dump_map.py LOG OUT.png [scale] [TITLE]"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

KIND = [  # (substring, colour) — first match wins
    ("water", (40, 90, 200)), ("flowing_water", (50, 100, 210)),
    ("grass_path", (170, 140, 80)), ("gravel", (135, 130, 125)), ("cobblestone", (118, 118, 118)), ("stone_bricks", (150, 150, 155)),
    ("spruce_planks", (110, 80, 50)), ("oak_planks", (160, 130, 80)), ("dark_oak_planks", (70, 50, 30)), ("planks", (150, 120, 75)),
    ("roof45_thatch", (190, 160, 80)), ("roof45_spruce", (90, 65, 45)), ("roof45_oak", (140, 105, 60)), ("roof45", (120, 90, 60)), ("roof", (120, 90, 60)),
    ("spruce_log", (80, 60, 40)), ("oak_log", (120, 95, 60)), ("_log", (110, 85, 55)), ("stump", (100, 75, 50)),
    ("leaves", (40, 110, 40)), ("pw:oak", (45, 120, 45)), ("pw:birch", (70, 135, 60)), ("pw:spruce", (30, 90, 45)), ("pw:", (60, 120, 60)),
    ("wheat", (200, 180, 80)), ("farmland", (95, 65, 40)), ("hay", (210, 180, 70)),
    ("grass_block", (95, 150, 70)), ("short_grass", (95, 150, 70)), ("tall_grass", (95, 150, 70)), ("fern", (90, 140, 70)),
    ("dirt", (120, 85, 60)), ("sand", (215, 200, 150)), ("snow", (240, 240, 245)), ("stone", (128, 128, 128)), ("andesite", (130, 130, 130)),
    ("diorite", (200, 200, 200)), ("granite", (150, 110, 95)), ("deepslate", (80, 80, 85)), ("clay", (160, 165, 175)),
    ("web", (235, 235, 235)), ("fence", (120, 90, 55)), ("lantern", (255, 200, 90)), ("barrel", (120, 90, 55)), ("door", (160, 110, 60)),
    ("glass", (200, 230, 240)), ("bed", (200, 60, 60)), ("sign", (170, 130, 80)), ("wall", (140, 140, 140)),
]


def colour(name):
    for sub, c in KIND:
        if sub in name:
            return c
    return (150, 120, 160)


def main(log, out, scale=3, title="PLAN"):
    head = None
    rows, pal = {}, {}
    for line in Path(log).read_text(errors="ignore").splitlines():
        if "[CIVTEST]" in line and '"dumphead"' in line:
            head = json.loads(line.split("[CIVTEST] ", 1)[1])
        m = re.search(r"\[CIVDUMP\] (-?\d+) (\d+) (.*)$", line)
        if m:
            rows.setdefault(int(m.group(1)), {})[int(m.group(2))] = m.group(3)
        m = re.search(r"\[CIVPAL\] (\d+) (\[.*\])\s*$", line)
        if m:
            for j, e in enumerate(json.loads(m.group(2))):
                pal[int(m.group(1)) + j] = e
    assert head, "no dumphead"
    x0, x1, z0, z1 = head["x0"], head["x1"], head["z0"], head["z1"]
    nx, nz = x1 - x0 + 1, z1 - z0 + 1
    top = [None] * (nx * nz)            # (y, name) of the highest non-air block per column
    for y in sorted(rows, reverse=True):
        s = "".join(rows[y][i] for i in sorted(rows[y]))
        i = 0
        for run in s.split(","):
            if not run:
                continue
            k, n = (run.split("*") + ["1"])[:2]
            k, n = int(k), int(n)
            if k >= 0:
                name = pal[k][0]
                if name not in ("minecraft:air", "minecraft:light_block_14"):
                    for j in range(i, i + n):
                        if top[j] is None:
                            top[j] = (y, name)
            i += n
    ys = [t[0] for t in top if t]
    lo, hi = min(ys), max(ys)
    img = Image.new("RGB", (nx * scale, nz * scale), (10, 10, 14))
    px = img.load()
    for j, t in enumerate(top):
        if not t:
            continue
        cx, cz = j // nz, j % nz
        y, name = t
        r, g, b = colour(name)
        shade = 0.55 + 0.45 * (y - lo) / max(1, hi - lo)
        # a hillshade: lighter where the column west of it is lower
        w = top[j - nz] if cx > 0 else None
        if w and w[0] < y:
            shade = min(1.0, shade + 0.12)
        elif w and w[0] > y:
            shade = max(0.3, shade - 0.12)
        c = (int(r * shade), int(g * shade), int(b * shade))
        for dx in range(scale):
            for dz in range(scale):
                px[cx * scale + dx, cz * scale + dz] = c
    sheet = Image.new("RGB", (img.width + 20, img.height + 46), (18, 18, 22))
    sheet.paste(img, (10, 36))
    d = ImageDraw.Draw(sheet)
    d.text((10, 6), f"{title} — plan view (north up), dump {Path(log).name}: x {x0}..{x1}, z {z0}..{z1}, ground y {lo}..{hi}; "
                    f"path tan · gravel/cobble grey · roofs brown/straw · stone-brick wall light grey · water blue · trees green", fill=(255, 210, 120))
    d.text((10, 20), f"{scale} px per block · x grows to the right, z grows downward", fill=(200, 200, 200))
    sheet.save(out)
    print(out, sheet.size, "columns", sum(1 for t in top if t))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3, sys.argv[4] if len(sys.argv) > 4 else "PLAN")
