#!/usr/bin/env python3
"""civ_dump_render.py — render what the SERVER built: the villageprobe's region dump ([CIVDUMP] run-length rows per y +
[CIVPAL] palette, from a bds_civtest console log) through the true-law renderer (civ_render, D-C487), terrain included.
Output: a review sheet (street view from the south-west above, the other side, and a top-down plan) so the village the
clock raised can be looked at as a whole. Usage: civ_dump_render.py LOG OUT.png"""
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("PW_STACK", "final")
sys.path.insert(0, "/home/claude/tools")
import civ_render as CR  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

CR.BP = Path("/home/claude/_build/bp02-207/blocks")
CR.RP_MODELS = [Path("/home/claude/_build/rp04-156/models/blocks"), Path("/home/claude/_build/rp01-117/models/blocks")]
# flat colours for the terrain the dump carries (civ_render knows the building materials; the ground is new here)
TERRAIN = {"minecraft:grass_block": (96, 140, 60), "minecraft:dirt": (120, 85, 55), "minecraft:stone": (125, 125, 125),
           "minecraft:grass_path": (150, 125, 80), "minecraft:sand": (210, 195, 150), "minecraft:gravel": (135, 130, 125),
           "minecraft:water": (50, 90, 170), "minecraft:coarse_dirt": (110, 80, 55), "minecraft:podzol": (100, 75, 45),
           "minecraft:snow_layer": (235, 240, 245), "minecraft:short_grass": (90, 150, 60), "minecraft:tall_grass": (85, 145, 55),
           "minecraft:fern": (80, 130, 60), "minecraft:oak_leaves": (60, 110, 40), "minecraft:birch_leaves": (90, 140, 60),
           "minecraft:spruce_leaves": (50, 90, 50), "minecraft:oak_log": (95, 75, 45), "minecraft:birch_log": (200, 200, 185),
           "minecraft:clay": (160, 165, 175), "minecraft:bedrock": (60, 60, 60), "minecraft:andesite": (135, 135, 130),
           "minecraft:granite": (150, 110, 95), "minecraft:diorite": (190, 190, 190), "minecraft:dandelion": (230, 210, 60),
           "minecraft:poppy": (200, 50, 40), "minecraft:sugar_cane": (120, 170, 80), "minecraft:seagrass": (60, 120, 70),
           "minecraft:kelp": (50, 100, 60), "minecraft:lily_pad": (40, 120, 40)}


def parse(log, crop=None):
    """crop = (x0, x1, z0, z1) in WORLD coords keeps only that window (a 374 x 390 x 110 dump of three towns is 5 GB as a
    block list — the renderer was OOM-killed on run 0.0.14's dump); the head is shifted to the window."""
    rows, pal = {}, {}
    head = None
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
    nz = z1 - z0 + 1
    cx0, cx1, cz0, cz1 = crop if crop else (x0, x1, z0, z1)
    cx0, cx1, cz0, cz1 = max(cx0, x0), min(cx1, x1), max(cz0, z0), min(cz1, z1)
    blocks = []
    for y, parts in rows.items():
        s = "".join(parts[i] for i in sorted(parts))
        i = 0
        for run in s.split(","):
            if not run:
                continue
            k, n = (run.split("*") + ["1"])[:2]
            k, n = int(k), int(n)
            if k >= 0:
                name, states = pal[k]
                if name != "minecraft:light_block_14":
                    for j in range(i, i + n):
                        wx, wz = x0 + j // nz, z0 + j % nz
                        if wx < cx0 or wx > cx1 or wz < cz0 or wz > cz1:
                            continue
                        blocks.append([wx - cx0, y - head["y0"], wz - cz0, name, states])
            i += n
    if crop:
        head = dict(head, x0=cx0, x1=cx1, z0=cz0, z1=cz1)
    return head, blocks


def main(log, out, crop=None, title="VILLAGE"):
    head, blocks = parse(log, crop)
    sx, sz = head["x1"] - head["x0"] + 1, head["z1"] - head["z0"] + 1
    sy = head["y1"] - head["y0"] + 1
    for k, v in TERRAIN.items():
        CR.FLAT.setdefault(k, v)
    # the grass top is greyscale in the pack (the game tints it per biome): draw the ground flat green for the review
    CR.VANILLA.pop("minecraft:grass_block", None)
    CR.FLAT["minecraft:grass_block"] = TERRAIN["minecraft:grass_block"]
    for k, v in {"minecraft:coal_ore": (90, 90, 90), "minecraft:copper_ore": (150, 120, 100), "minecraft:iron_ore": (160, 140, 125),
                 "minecraft:bush": (70, 120, 50), "minecraft:cornflower": (80, 100, 200), "minecraft:waterlily": (40, 120, 40),
                 "minecraft:azure_bluet": (230, 230, 240)}.items():
        CR.FLAT.setdefault(k, v)
    for k, v in {"minecraft:spruce_planks": ("planks_spruce", "planks_spruce"), "minecraft:dark_oak_planks": ("planks_big_oak", "planks_big_oak"),
                 "minecraft:oak_log": ("log_oak", "log_top_oak"), "minecraft:dark_oak_log": ("log_big_oak", "log_top_big_oak"),
                 "minecraft:gravel": ("gravel", "gravel"), "minecraft:bricks": ("brick", "brick")}.items():
        CR.VANILLA.setdefault(k, v)
    for k, v in {"minecraft:web": (235, 235, 235), "minecraft:spruce_fence": (95, 70, 45), "minecraft:lantern": (255, 200, 90),
                 "minecraft:barrel": (120, 90, 55), "minecraft:farmland": (95, 65, 40), "minecraft:wheat": (200, 180, 80)}.items():
        CR.FLAT.setdefault(k, v)
    CR.VTHIN.setdefault("minecraft:iron_chain", (-1.5, 0, -1.5, 3, 16, 3))
    CR.VCOL.setdefault("minecraft:iron_chain", (90, 90, 95))
    man = {"size": [sx, sy, sz], "datum_y": 0, "blocks": blocks, "entities": []}
    items = CR.scene(man, min_feet=0)
    cx, cz = sx * 8, sz * 8
    span = max(sx, sz) * 16
    top = sy * 16
    W, H = 1400, 820
    shots = [("from the south-west, above (street runs left-right, fronts face it)", (cx - span * 0.75, top + span * 0.45, cz + span * 0.95), (cx, top * 0.35, cz)),
             ("from the north-east, above", (cx + span * 0.75, top + span * 0.45, cz - span * 0.9), (cx, top * 0.35, cz)),
             ("plan, from above, tilted a little toward the south (north at the top)", (cx, top + span * 1.2, cz + span * 0.18), (cx, 0, cz))]
    tiles = []
    for label, eye, tgt in shots:
        im = Image.fromarray(CR.render(items, eye, tgt, W=W, H=H, fov=50))
        ImageDraw.Draw(im).text((10, 8), label, fill=(255, 255, 255))
        tiles.append(im)
    sheet = Image.new("RGB", (W + 20, (H + 12) * len(tiles) + 40), (18, 18, 22))
    ImageDraw.Draw(sheet).text((10, 6), f"{title} as the server built it — dump {Path(log).name}: x {head['x0']}..{head['x1']}, z {head['z0']}..{head['z1']}, "
                                        f"y {head['y0']}..{head['y1']}, {len(blocks):,} blocks, {len(set(b[3] for b in blocks))} block types", fill=(255, 210, 120))
    for i, t in enumerate(tiles):
        sheet.paste(t, (10, 30 + i * (H + 12)))
    sheet.save(out)
    print(out, sheet.size, len(blocks), "blocks")


if __name__ == "__main__":
    # civ_dump_render.py LOG OUT.png [x0 x1 z0 z1 [TITLE]]
    crop = tuple(int(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else None
    main(sys.argv[1], sys.argv[2], crop, sys.argv[7] if len(sys.argv) >= 8 else "VILLAGE")
