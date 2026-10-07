#!/usr/bin/env python3
"""mob_normals_sheet.py — before/after sheet for the creature normal-map round (his 17:55 approval).
Per creature: the picture | lit WITHOUT a normal (what he has now) | lit WITH the new normal | the normal map itself.
Lighting is a 2D stand-in for the game: one low sun from the upper-left (L = (-0.55, -0.55, 0.63)), ambient 0.35,
a little specular from the MERS roughness. It shows relief, not the final in-game look (witness decides)."""
import io
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
os.environ.setdefault("PW_STACK", "final")
import stack_now as SN  # noqa: E402

STAGE = ROOT / "_staging/mobnormals"
CELL = 300
L = np.array([-0.55, -0.55, 0.63])
L = L / np.linalg.norm(L)
SAMPLES = ["textures/entity/pw_menagerie/ysav/savanna_edition/bufalo",
           "textures/entity/pw_menagerie/anf/cyd/ulta/entity/mammals/lion_african",
           "textures/entity/sf_nba/anteater",
           "textures/entity/pw_menagerie/anf/cyd/ulta/entity/reptiles/crocodile_african",
           "textures/entity/pw_menagerie/anf/cyd/ulta/entity/insects/beetle_atlas",
           "textures/entity/pw_menagerie/anf/cyd/ulta/entity/sealife/seal_grey",
           "textures/entity/pw_menagerie/anf/cyd/ulta/entity/birds/stork_adjutant",
           "textures/entity/zombie_villager2/zombie-villager"]


def load_rgba(data):
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGBA")).astype(float)


def shade(colour, normal, rough):
    n = normal[..., :3] / 255 * 2 - 1
    n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
    diff = np.clip(n @ L, 0, 1)
    h = (L + np.array([0, 0, 1.0]))
    h /= np.linalg.norm(h)
    gloss = 1 - rough / 255
    spec = np.clip(n @ h, 0, 1) ** (2 + 60 * gloss) * 0.35 * gloss
    lit = colour[..., :3] / 255 * (0.35 + 0.75 * diff)[..., None] + spec[..., None]
    out = np.clip(lit * 255, 0, 255)
    return np.dstack([out, colour[..., 3]]).astype(np.uint8)


def cell(arr):
    im = Image.fromarray(arr.astype(np.uint8), "RGBA")
    s = CELL / max(im.size)
    im = im.resize((max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))), Image.NEAREST)
    bg = Image.new("RGBA", (CELL, CELL), (40, 40, 44, 255))
    bg.alpha_composite(im, ((CELL - im.size[0]) // 2, (CELL - im.size[1]) // 2))
    return bg


def main():
    P = SN.packs()
    report = {r["path"]: r for r in json.loads((ROOT / "_docs/mers/MOB-NORMALS-REPORT.json").read_text())}
    rows = []
    for path in SAMPLES:
        r = report[path]
        p, f = SN.find_image(P, path)
        colour = load_rgba(p.read(f))
        stem = Path(path).name
        stage_dir = STAGE / r["target_pack"] / Path(path).parent
        normal = np.asarray(Image.open(stage_dir / f"{stem}_n.png").convert("RGBA")).astype(float)
        ts = json.loads((stage_dir / f"{stem}.texture_set.json").read_text())["minecraft:texture_set"]
        mers_name = ts.get("metalness_emissive_roughness_subsurface")
        mers_file = stage_dir / f"{mers_name}.png"
        if mers_file.exists():
            mers = np.asarray(Image.open(mers_file).convert("RGBA")).astype(float)
        else:
            mp, mf = SN.find_image(P, f"{Path(path).parent.as_posix()}/{mers_name}")
            mers = load_rgba(mp.read(mf))
        if mers.shape[:2] != colour.shape[:2]:
            mers = np.asarray(Image.fromarray(mers.astype(np.uint8)).resize(colour.shape[1::-1], Image.BOX)).astype(float)
        rough = mers[..., 2]
        flat = np.zeros_like(normal)
        flat[..., 0], flat[..., 1], flat[..., 2] = 127.5, 127.5, 255
        rows.append((f"{stem}  ({r['material']}, {r['size'][0]}x{r['size'][1]}, {r['target_pack']})",
                     [cell(colour), cell(shade(colour, flat, rough)), cell(shade(colour, normal, rough)), cell(normal)]))
    font = ImageFont.load_default()
    head = 26
    sheet = Image.new("RGBA", (CELL * 4 + 50, 40 + len(rows) * (CELL + head + 10)), (24, 24, 28, 255))
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(["picture", "lit now (no normal map)", "lit with new normal map", "the normal map"]):
        d.text((10 + i * (CELL + 10) + 6, 12), t, fill=(235, 235, 235, 255), font=font)
    y = 40
    for title, cells in rows:
        d.text((16, y + 4), title, fill=(255, 210, 120, 255), font=font)
        for i, c in enumerate(cells):
            sheet.alpha_composite(c, (10 + i * (CELL + 10), y + head))
        y += CELL + head + 10
    out = Path("/mnt/user-data/outputs/CREATURE-NORMALS-BEFORE-AFTER.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
