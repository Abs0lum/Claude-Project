#!/usr/bin/env python3
"""sculk_seamless.py — SCULK option 3 made SEAMLESS (his ruling D-C307: "number 3 but we improve it to seamless"). PREVIEW ONLY.

Option 3 = Bedrock random variations: each sculk block shows one of Patrix's four CTM tiles (block/1-4, 2 frames each, each on its
own period). In Java the four tiles only ever meet in their 2x2 mosaic order, so a random neighbour shows a seam.

Seamless recipe (no pixel is invented — every value is a Patrix pixel or a blend of two Patrix pixels):
  1 FRAME  tile 1 made self-tiling: blended with its own half-offset copy (the offset copy's centre is continuous across the
           wrap), weight = distance from the edge -> its border band continues into itself on every side.
  2 BAND   each tile keeps its own interior; inside a border band (BAND px, smooth, edge wobbled by low-frequency noise so it
           is not a square ring) it fades into the FRAME -> every tile carries the identical border -> any tile beside any other.
  3 STILL  the band uses the frame's FIRST animation frame in both frames: tiles pulse on different periods, so an animated band
           would flicker out of step at the seams; the glow pulse stays in each tile's interior.
Outputs: _docs/sculk/SCULK-SEAMLESS.png (Java reference · option 3 as it was · option 3 seamless, at t = 0 and mid-pulse, + a
4x seam close-up) and _docs/sculk/SCULK-SEAMLESS.gif; the candidate tiles go to _docs/sculk/seamless_tiles/ (not a pack)."""
import random
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import sculk_options_preview as SO

ROOT = Path("/home/claude"); OUT = ROOT / "_docs/sculk"; TILES_OUT = OUT / "seamless_tiles"
T = 128
BAND = 14                     # border band (px of 128) that fades into the shared frame (14: 61 % of each tile keeps its own pixels + pulse; 22 looked more repetitive)
WOBBLE = 5.0                  # px: the band's inner edge follows low-frequency noise, not a straight line
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0); return x * x * (3 - 2 * x)


def edge_distance():
    y, x = np.mgrid[0:T, 0:T].astype(float) + 0.5
    return np.minimum(np.minimum(x, T - x), np.minimum(y, T - y))


def self_tiling(a):
    """a (T,T,3) -> seamless with itself: blend with the half-offset copy by distance from the edge"""
    b = np.roll(np.roll(a, T // 2, 0), T // 2, 1)
    w = smoothstep(edge_distance() / (T * 0.25))[..., None]        # 1 in the centre (a), 0 at the edges (b: continuous across the wrap)
    return a * w + b * (1 - w)


def lowfreq_noise(seed):
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 1, (5, 5))
    return np.asarray(Image.fromarray(((g - g.min()) / (np.ptp(g) or 1) * 255).astype(np.uint8)).resize((T, T), Image.BICUBIC)).astype(float) / 127.5 - 1.0


def band_mask(seed):
    """1 = the tile's own pixel, 0 = the shared frame; the transition wobbles with noise"""
    d = edge_distance() + WOBBLE * lowfreq_noise(seed)
    return smoothstep((d - 2.0) / (BAND - 2.0))[..., None]


def build():
    frame0 = self_tiling(SO.TILES[1][0])                     # the shared border: tile 1, frame 0, self-tiling
    out = {}
    for n in (1, 2, 3, 4):
        m = band_mask(100 + n)
        out[n] = tuple(SO.TILES[n][f] * m + frame0 * (1 - m) for f in (0, 1))
    return out, frame0


def seam_error(tiles):
    """largest RGB step across a seam between any two tiles (both frames, both directions) vs the step inside a tile"""
    worst = 0.0
    for a in tiles.values():
        for b in tiles.values():
            for fa in a:
                for fb in b:
                    worst = max(worst, float(np.abs(fa[:, -1] - fb[:, 0]).mean()), float(np.abs(fa[-1, :] - fb[0, :]).mean()))
    inside = np.mean([float(np.abs(f[:, 1:] - f[:, :-1]).mean()) for t in tiles.values() for f in t])
    return worst, inside


def floor(tiles, t, seed=7, n=SO.N):
    rnd = random.Random(seed)
    img = np.zeros((n * T, n * T, 3))
    for by in range(n):
        for bx in range(n):
            k = rnd.choice((1, 2, 3, 4)); img[by * T:(by + 1) * T, bx * T:(bx + 1) * T] = SO.at(tiles[k], SO.FT[k], t)
    return img


def as_img(a, px=SO.PX, n=SO.N):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((n * px, n * px), Image.LANCZOS)


def main():
    tiles, frame0 = build()
    raw = {k: SO.TILES[k] for k in (1, 2, 3, 4)}
    err_raw, inside = seam_error(raw); err_new, _ = seam_error(tiles)
    TILES_OUT.mkdir(parents=True, exist_ok=True)
    for k, (f0, f1) in tiles.items():
        Image.fromarray(np.clip(np.concatenate([f0, f1], 0), 0, 255).astype(np.uint8)).save(TILES_OUT / f"sculk_seamless_{k}.png")
    t_mid = 30.0
    cols = [("2 JAVA Patrix (reference)", lambda t: SO.floor("JAVA", t)), ("3 RANDOM tiles as they were", lambda t: as_img(floor(raw, t))),
            ("3 RANDOM tiles SEAMLESS", lambda t: as_img(floor(tiles, t)))]
    W = SO.N * SO.PX
    sheet = Image.new("RGB", (3 * (W + 6) - 6, 2 * (W + 26) + 26 + 2 * T * 2 + 40), (235, 235, 235))
    d = ImageDraw.Draw(sheet)
    for r, (t, lab) in enumerate(((0.0, "t=0"), (t_mid, "mid-pulse"))):
        for c, (name, fn) in enumerate(cols):
            x0, y0 = c * (W + 6), r * (W + 26)
            d.text((x0 + 4, y0 + 4), f"{name}  {lab}", fill=(10, 10, 10), font=F); sheet.paste(fn(t), (x0, y0 + 24))
    # 4x close-up of one seam: tile 1 beside tile 1 (a pair Java never shows), before and after
    y0 = 2 * (W + 26) + 6
    d.text((4, y0), f"SEAM CLOSE-UP (x2): tile 1 beside tile 1 and tile 3 above tile 2. Mean colour step across a seam: before {err_raw:.1f}, "
                    f"after {err_new:.1f} (inside a tile: {inside:.1f})", fill=(10, 10, 10), font=F)
    def pair(ts, a, b, horiz=True):
        A, B = ts[a][0], ts[b][0]
        return np.concatenate([A, B], 1 if horiz else 0)
    for i, (ts, lab) in enumerate(((raw, "before"), (tiles, "after"))):
        p = Image.fromarray(np.clip(pair(ts, 1, 1), 0, 255).astype(np.uint8)).resize((4 * T, 2 * T), Image.NEAREST)
        q = Image.fromarray(np.clip(pair(ts, 3, 2, False), 0, 255).astype(np.uint8)).resize((T, 2 * T), Image.NEAREST)
        x = 4 + i * (4 * T + T + 40)
        sheet.paste(p, (x, y0 + 26)); sheet.paste(q, (x + 4 * T + 10, y0 + 26))
        d.text((x, y0 + 26 + 2 * T + 4), lab, fill=(10, 10, 10), font=F)
    sheet.save(OUT / "SCULK-SEAMLESS.png")
    frames = []
    for i in range(24):
        t = i * 4.0
        row = Image.new("RGB", (3 * (W + 6) - 6, W + 24), (235, 235, 235)); dd = ImageDraw.Draw(row)
        for c, (name, fn) in enumerate(cols):
            dd.text((c * (W + 6) + 4, 4), name, fill=(10, 10, 10), font=F); row.paste(fn(t), (c * (W + 6), 24))
        frames.append(row)
    frames[0].save(OUT / "SCULK-SEAMLESS.gif", save_all=True, append_images=frames[1:], duration=250, loop=0)
    print(f"seam step before {err_raw:.2f}, after {err_new:.2f}, inside a tile {inside:.2f}")
    print(OUT / "SCULK-SEAMLESS.png", OUT / "SCULK-SEAMLESS.gif")


if __name__ == "__main__":
    main()
