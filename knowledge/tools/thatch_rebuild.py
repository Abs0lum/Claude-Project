#!/usr/bin/env python3
"""thatch_rebuild.py — replace the corrupt thatch textures (D-C527: pw_thatch, pw_deck45_thatch, pw_deck45h_thatch and the
thatch parts of pw_fill_45_thatch / pw_fill_ridge_thatch are rainbow streak noise, mean saturation ~100 vs ~35 for straw).
New straw is made from our own hay_block_side (RP-04): the two red binding bands are cut out, the strands run vertically
(down the roof slope), and darker horizontal course lines every 1/4 tile give the layered look of laid thatch. Each target
keeps its own size and alpha (the fills keep their stepped shape; only their saturated thatch pixels are replaced).
Usage: thatch_rebuild.py RP_TEXTURE_BLOCKS_DIR [--preview OUT.png]"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def straw_tile(blocks, size):
    hay = np.asarray(Image.open(blocks / "hay_block_side.png").convert("RGB"), dtype=float)
    red = (hay[..., 0] - hay[..., 1]).mean(1)
    keep = [i for i in range(hay.shape[0]) if red[i] < red.mean() + 8]          # rows without the red binding bands
    rows = hay[keep]
    rows = np.concatenate([rows, rows[::-1]], 0)                                   # mirror so the strip tiles seamlessly
    img = Image.fromarray(rows.astype(np.uint8)).resize(size, Image.LANCZOS)
    a = np.asarray(img, dtype=float)
    a = a * np.array([1.0, 0.86, 0.62])                                           # weathered straw, less yellow than fresh hay
    h = a.shape[0]
    for k in range(4):                                                             # four laid courses: shade toward each course's lower edge
        y0, y1 = k * h // 4, (k + 1) * h // 4
        ramp = np.linspace(1.05, 0.72, y1 - y0)[:, None, None]
        a[y0:y1] *= ramp
    return np.clip(a, 0, 255)


def main():
    blocks = Path(sys.argv[1])
    out = {}
    for name in ("pw_thatch", "pw_deck45_thatch", "pw_deck45h_thatch", "pw_fill_45_thatch", "pw_fill_ridge_thatch"):
        p = blocks / f"{name}.png"
        src = np.asarray(Image.open(p).convert("RGBA"), dtype=float)
        h, w = src.shape[:2]
        tile = straw_tile(blocks, (w, h))
        sat = src[..., :3].max(-1) - src[..., :3].min(-1)
        mask = (src[..., 3] > 0) & (sat > 70) if name.startswith("pw_fill") else (src[..., 3] > 0)
        new = src.copy()
        new[..., :3][mask] = tile[mask]
        Image.fromarray(new.astype(np.uint8), "RGBA").save(p)
        nsat = (new[..., :3].max(-1) - new[..., :3].min(-1))[new[..., 3] > 0].mean()
        out[name] = (w, h, int(mask.sum()), round(float(nsat), 1))
    print(out)
    if "--preview" in sys.argv:
        prev = Image.new("RGBA", (5 * 200, 200), "white")
        for i, n in enumerate(out):
            prev.paste(Image.open(blocks / f"{n}.png").convert("RGBA").resize((190, 190)), (i * 200, 5))
        prev.save(sys.argv[sys.argv.index("--preview") + 1])


if __name__ == "__main__":
    main()
