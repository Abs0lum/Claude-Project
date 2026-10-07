#!/usr/bin/env python3
"""trader_decor_outer.py — D-C275: the trader llama's blanket/tassels/halter are painted on the INNER fur shell of
trader_llama_<variant>.png (decor = the pixels where it differs from the plain <variant>.png). With the Patrix shells properly
separated (Converter B), the outer fur covers them. This copies the decor pixels onto the OUTER shell's UV regions of the same
texture (body b0 -> b3/b4: +52 u, +35 v; head c0 -> c1/c2: +52 u, +29 v, in 128x64 texel units), leaving every other pixel as is.
Usage: trader_decor_outer.py <src textures/entity/llama dir> <dst dir>"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

BODY = (30, 0, 76, 29, 52, 35)     # u0, v0, u1, v1 (texels, 128x64), du, dv
HEAD = (0, 0, 30, 36, 52, 29)


def build(src, dst):
    out = {}
    for v in ("creamy", "white", "brown", "gray"):
        t = np.asarray(Image.open(src / f"trader_llama_{v}.png").convert("RGBA")).copy()
        p = np.asarray(Image.open(src / f"{v}.png").convert("RGBA"))
        H, W = t.shape[:2]; s = W // 128
        mask = np.abs(t.astype(int) - p.astype(int)).sum(-1) > 24
        res = t.copy(); moved = 0
        for u0, v0, u1, v1, du, dv in (BODY, HEAD):
            ys, xs = np.nonzero(mask[v0 * s:v1 * s, u0 * s:u1 * s])
            ys = ys + v0 * s; xs = xs + u0 * s
            ty, tx = ys + dv * s, xs + du * s
            ok = (ty < H) & (tx < W)
            res[ty[ok], tx[ok]] = t[ys[ok], xs[ok]]; moved += int(ok.sum())
        Image.fromarray(res).save(dst / f"trader_llama_{v}.png")
        out[v] = moved
    return out


if __name__ == "__main__":
    print(build(Path(sys.argv[1]), Path(sys.argv[2])))
