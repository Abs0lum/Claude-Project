#!/usr/bin/env python3
"""ctm_grid.py — his 23:41 ask: what each new pack (and ours, and Patrix) produces as a 6 x 6 patch of blocks, using
that pack's own connected-texture rule, colour only (= how the picture tiles; no lighting). One PNG per block per pack,
native resolution (6 x tile size), delivered separately so he can zoom.

Rules read from each pack's files (2026-10-01):
  Patrix 26.2 256x  planks: optifine ctm method=repeat 4x4 (tiles 1-16)   sand: repeat 6x6 (tiles 1-36)
  Stratum 256x      one texture per block (no CTM)
  GameplayFriendly  planks: repeat 3x2 (tiles 0-5)  sand: repeat 2x2 (tiles 0-3)   128x
  RenderingStuff    R1-14 512x: oak / dark oak one texture; sand repeat 2x2 (tiles 0-3)
  OURS (RP-04 1.3.147) Bedrock random 'variations' (4 per plank species, 24 for sand) — rendered with a fixed seed
OptiFine 'repeat' on a top face: tile = (x mod w) + (z mod h) * w, counted from the world origin.
Output: _docs/grids/<block>__<source>.png + INDEX.json."""
import io
import json
import random
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import pbr_round as PR  # noqa: E402

NEW = ROOT / "_intake/newpacks-1001"
OUT = ROOT / "_docs/grids"
OURS = ROOT / "_build/rp04-147/textures/blocks"
GRID = 6


def zread(z, name):
    return Image.open(io.BytesIO(z.read(name))).convert("RGBA")


def repeat_grid(tiles, w, h):
    return [[tiles[(x % w) + (z % h) * w] for x in range(GRID)] for z in range(GRID)]


def single_grid(t):
    return [[t] * GRID for _ in range(GRID)]


def random_grid(tiles, seed=11):
    rng = random.Random(seed)
    return [[rng.choice(tiles) for _ in range(GRID)] for _ in range(GRID)]


def compose(grid, title, out):
    s = grid[0][0].size[0]
    img = Image.new("RGB", (GRID * s, GRID * s + 28), (20, 20, 22))
    for z, row in enumerate(grid):
        for x, t in enumerate(row):
            t = t.resize((s, s), Image.NEAREST) if t.size[0] != s else t
            bg = Image.new("RGBA", t.size, (20, 20, 22, 255))
            img.paste(Image.alpha_composite(bg, t).convert("RGB"), (x * s, 28 + z * s))
    ImageDraw.Draw(img).text((8, 8), title, fill=(235, 235, 235))
    img.save(out)
    return img.size


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pz = zipfile.ZipFile(PR.PATRIX256)
    st = zipfile.ZipFile(NEW / "Stratum 256x.zip")
    gf = zipfile.ZipFile(NEW / "GameplayFriendlyTextures_128x_v12.zip")
    rs_outer = zipfile.ZipFile(NEW / "RenderingStuff_2019_512x_d.zip")
    rs = zipfile.ZipFile(io.BytesIO(rs_outer.read("R1-14_Textures_512x.zip")))
    index = []

    def save(block, src, grid, rule):
        name = f"{block}__{src}.png"
        size = compose(grid, f"{block} - {src} - {rule} - 6 x 6 blocks, colour only", OUT / name)
        index.append({"file": name, "block": block, "source": src, "rule": rule, "px": size})

    for sp in ("oak", "spruce", "birch", "dark_oak"):
        blk = f"{sp}_planks"
        save(blk, "OURS-RP04-1.3.147", random_grid([Image.open(OURS / f"{blk}_v{i}.png").convert("RGBA") for i in range(4)]),
             "random of 4 variants (seed 11), 128px")
        pt = [zread(pz, f"assets/minecraft/optifine/ctm/patrix/planks/{sp}/{i}.png") for i in range(1, 17)]
        save(blk, "Patrix-256", repeat_grid(pt, 4, 4), "repeat 4x4 (16 tiles), 256px")
        save(blk, "Stratum-256", single_grid(zread(st, f"assets/minecraft/textures/block/{blk}.png")), "one texture, 256px")
        gt = [zread(gf, f"assets/minecraft/optifine/ctm/{blk}/{i}.png") for i in range(6)]
        save(blk, "GameplayFriendly-128", repeat_grid(gt, 3, 2), "repeat 3x2 (6 tiles), 128px")
        n = f"assets/minecraft/textures/block/{blk}.png"
        if n in rs.namelist():
            save(blk, "RenderingStuff-512", single_grid(zread(rs, n)), "one texture, 512px")
    save("sand", "OURS-RP04-1.3.147", random_grid([Image.open(OURS / f"pw_sand_v{i}.png").convert("RGBA") for i in range(1, 25)]),
         "random of 24 variants (seed 11), 256px")
    save("sand", "Patrix-256", repeat_grid([zread(pz, f"assets/minecraft/optifine/ctm/patrix/sand/yellow/{i}.png")
                                            for i in range(1, 37)], 6, 6), "repeat 6x6 (36 tiles), 256px")
    save("sand", "Stratum-256", single_grid(zread(st, "assets/minecraft/textures/block/sand.png")), "one texture, 256px")
    save("sand", "GameplayFriendly-128", repeat_grid([zread(gf, f"assets/minecraft/optifine/ctm/sand/{i}.png") for i in range(4)], 2, 2),
         "repeat 2x2 (4 tiles), 128px")
    save("sand", "RenderingStuff-512", repeat_grid([zread(rs, f"assets/minecraft/optifine/ctm/sand/{i}.png") for i in range(4)], 2, 2),
         "repeat 2x2 (4 tiles), 512px")
    (OUT / "INDEX.json").write_text(json.dumps(index, indent=1))
    for e in index:
        print(e["file"], e["px"])


if __name__ == "__main__":
    main()
