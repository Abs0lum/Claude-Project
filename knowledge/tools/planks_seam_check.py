#!/usr/bin/env python3
"""planks_seam_check.py — checks the BP-02 1.3.201 plank face mapping without the game:
  1. index check: on every face plane, the block to the viewer's right shows col+1 and the block above shows row-1
     (Patrix 'repeat' grid order) for all 64 position states.
  2. pixel check: the edge between neighbouring blocks (each face plane, 8 x 8 blocks) is as smooth as the inside of a
     tile (mean |difference| across the seam vs across interior pixel columns), oak.
  3. preview: a 6-wide x 4-high x 6-deep slab of oak grid blocks drawn as three unfolded faces (top, south, east).
Reads the generated block JSON (so it tests what ships). Output: _docs/planks/PLANKS-SEAM.png + printout."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path("/home/claude")
BLK = ROOT / "_build/bp02-201/blocks/pw_planks_grid_oak.json"
TEX = ROOT / "_build/rp04-149/textures/blocks/pw_planks"


def load():
    d = json.loads(BLK.read_text())["minecraft:block"]
    m = {}
    for p in d["permutations"]:
        c = p["condition"]
        g = [int(c.split(f"'pw:{a}') == ")[1][0]) for a in ("gx", "gy", "gz")]
        m[tuple(g)] = {f: int(v["texture"].rsplit("_", 1)[1]) for f, v in p["components"]["minecraft:material_instances"].items()}
    return m


def cr(t):
    return (t - 1) % 4, (t - 1) // 4


def tex(t, cache={}):
    if t not in cache:
        cache[t] = np.asarray(Image.open(TEX / f"oak_{t}.png").convert("RGB")).astype(float)
    return cache[t]


def face_grid(m, face, n=8):
    """picture of one face plane, n x n blocks, as seen from outside; returns tile ids [row][col]."""
    ids = [[0] * n for _ in range(n)]
    for r in range(n):          # r = screen row (0 top)
        for c in range(n):      # c = screen column (0 left)
            if face == "up":    x, y, z = c, 0, r                # looking down, north at top
            elif face == "south": x, y, z = c, n - 1 - r, 0      # right = east
            elif face == "north": x, y, z = n - 1 - c, n - 1 - r, 0
            elif face == "east": x, y, z = 0, n - 1 - r, n - 1 - c   # right = north
            elif face == "west": x, y, z = 0, n - 1 - r, c       # right = south
            else: x, y, z = c, 0, n - 1 - r                    # down, looking up, south at top
            ids[r][c] = m[(x % 4, y % 4, z % 4)][face]
    return ids


def main():
    m = load()
    bad = 0
    for face in ("up", "down", "north", "south", "east", "west"):
        ids = face_grid(m, face)
        for r in range(8):
            for c in range(8):
                col, row = cr(ids[r][c])
                if c < 7:
                    bad += cr(ids[r][c + 1]) != ((col + 1) % 4, row)
                if r < 7:
                    bad += cr(ids[r + 1][c]) != (col, (row + 1) % 4)
    print("1. index check: mismatches", bad, "(0 = every neighbour continues the Patrix grid)")
    for face in ("up", "south", "east"):
        ids = face_grid(m, face)
        img = np.concatenate([np.concatenate([tex(t) for t in row], 1) for row in ids], 0)
        g = img.mean(-1)
        seams_v = [abs(g[:, k * 256 - 1] - g[:, k * 256]).mean() for k in range(1, 8)]
        inner_v = [abs(g[:, k * 256 + 127] - g[:, k * 256 + 128]).mean() for k in range(8)]
        seams_h = [abs(g[k * 256 - 1] - g[k * 256]).mean() for k in range(1, 8)]
        inner_h = [abs(g[k * 256 + 127] - g[k * 256 + 128]).mean() for k in range(8)]
        print(f"2. {face:5s} seam |d| vertical {np.mean(seams_v):.1f} vs inside {np.mean(inner_v):.1f}; "
              f"horizontal {np.mean(seams_h):.1f} vs inside {np.mean(inner_h):.1f}")
    # 3. unfolded preview (top above, south below-left, east below-right), 6 x 6 top, 6 x 4 walls, 64 px per block
    s = 64
    def plane(face, w, h):
        ids = face_grid(m, face, 8)
        im = np.zeros((h * s, w * s, 3))
        for r in range(h):
            for c in range(w):
                t = Image.fromarray(tex(ids[r][c]).astype(np.uint8)).resize((s, s), Image.LANCZOS)
                im[r * s:(r + 1) * s, c * s:(c + 1) * s] = np.asarray(t)
        return im
    top, south, east = plane("up", 6, 6), plane("south", 6, 4), plane("east", 6, 4)
    sheet = Image.new("RGB", (12 * s + 30, 10 * s + 50), (24, 24, 28))
    sheet.paste(Image.fromarray(top.astype(np.uint8)), (10, 30))
    sheet.paste(Image.fromarray(south.astype(np.uint8)), (10, 30 + 6 * s + 10))
    sheet.paste(Image.fromarray(east.astype(np.uint8)), (20 + 6 * s, 30 + 6 * s + 10))
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), "oak plank grid (BP-02 1.3.201 mapping): top 6x6 | south wall 6x4 | east wall 6x4", fill=(235, 235, 235))
    out = ROOT / "_docs/planks/PLANKS-SEAM.png"
    sheet.save(out)
    print("3.", out, sheet.size)


if __name__ == "__main__":
    main()
