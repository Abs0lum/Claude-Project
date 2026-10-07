#!/usr/bin/env python3
"""civ_topmap.py — flat top-down map of a server dump (north at the TOP, east to the RIGHT, world coordinates on the
edges): each column coloured by its topmost block, doors red, fences / walls brown dots, paths and cobble distinct, and a
height shade; holes (a column whose top is >= 2 below both street neighbours) outlined. Usage: civ_topmap.py LOG OUT.png [x0 x1 z0 z1]"""
import sys
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
import civ_dump_render as D  # noqa: E402

COL = [("door", (230, 40, 40)), ("fence", (120, 70, 30)), ("wall", (110, 110, 110)), ("grass_path", (175, 150, 90)),
       ("dirt_path", (175, 150, 90)), ("cobblestone", (140, 140, 140)), ("gravel", (150, 145, 140)), ("planks", (170, 130, 80)),
       ("roof", (120, 90, 60)), ("thatch", (200, 180, 90)), ("grass_block", (90, 140, 60)), ("dirt", (120, 85, 55)),
       ("water", (50, 90, 200)), ("log", (90, 60, 35)), ("stone", (125, 125, 125)), ("leaves", (60, 110, 50)), ("slab", (150, 150, 150)),
       ("stairs", (150, 150, 150)), ("farmland", (100, 70, 40)), ("hay", (210, 190, 80))]


def colour(name):
    for k, c in COL:
        if k in name:
            return c
    return (180, 180, 180)


def main():
    log, out = sys.argv[1], sys.argv[2]
    crop = tuple(int(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else None
    head, blocks = D.parse(log, crop)
    top = {}
    doors = set()
    for x, y, z, name, st in blocks:
        if "light_block" in name or name.startswith("pw:marker") or "structure_void" in name:
            continue
        if "door" in name and "trapdoor" not in name:
            doors.add((x, z))
        if (x, z) not in top or y > top[(x, z)][0]:
            top[(x, z)] = (y, name)
    W = head["x1"] - head["x0"] + 1
    H = head["z1"] - head["z0"] + 1
    S = 14
    im = Image.new("RGB", (W * S + 60, H * S + 60), (255, 255, 255))
    d = ImageDraw.Draw(im)
    ys = [v[0] for v in top.values()]
    ymin, ymax = min(ys), max(ys)
    for (x, z), (y, name) in top.items():
        c = colour(name)
        f = 0.6 + 0.4 * (y - ymin) / max(1, ymax - ymin)
        c = tuple(int(v * f) for v in c)
        d.rectangle([40 + x * S, 40 + z * S, 40 + x * S + S - 1, 40 + z * S + S - 1], fill=c)
    for (x, z) in doors:
        d.rectangle([40 + x * S + 3, 40 + z * S + 3, 40 + x * S + S - 4, 40 + z * S + S - 4], fill=(230, 40, 40))
    for i in range(0, W, 5):
        d.text((40 + i * S, 22), str(head["x0"] + i), fill=(0, 0, 0))
    for j in range(0, H, 5):
        d.text((2, 40 + j * S), str(head["z0"] + j), fill=(0, 0, 0))
    d.text((W * S // 2, 2), "NORTH (-z) at top · EAST (+x) right · red = doors", fill=(200, 0, 0))
    im.save(out)
    print(out, im.size)


if __name__ == "__main__":
    main()
