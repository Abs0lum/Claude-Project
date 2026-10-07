#!/usr/bin/env python3
"""sculk_options_preview.py — SCULK plan (D-C305): what a 6x6 sculk floor looks like under each way of bringing Patrix's
animated sculk to Bedrock. Patrix (Java, OptiFine CTM) uses method=repeat 2x2: tiles 1-4 form ONE seamless 256 px mosaic
chosen by block POSITION, each tile cross-fading between 2 frames (frames [0,0,1], interpolate) with its own period.
Bedrock has no positional tiling: terrain 'variations' pick a variant at RANDOM per block.

Options rendered (top-down, 96 px per block, the same seed everywhere):
  1 NOW          our shipped sculk (RP-04 sculk.png), one still frame
  2 JAVA         Patrix as Java draws it: the 2x2 mosaic by position, each tile on its own period (the reference)
  3 RANDOM       Bedrock variations: a random Patrix tile per block, animated -> seams where tiles were never meant to touch
  4 MOSAIC       the whole 2x2 mosaic inside ONE block (a 256 px texture): seamless + animated, pattern at half scale
  5 BASE+PULSE   our shipped still tile + a derived 2nd frame (Patrix's speck brightening, +20 % on the glowing specks),
                 4 random variants of the SAME picture that differ only in period (Patrix's 57/81/69/45 ticks): no seams, desynced
Outputs: _docs/sculk/SCULK-OPTIONS.png (t = 0 and mid-pulse) + _docs/sculk/SCULK-OPTIONS.gif (6 s loop at 4x speed)"""
import random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/claude")
PAT = ROOT / "_intake/patrix128/sculk_pull/assets/minecraft"
CTM = PAT / "optifine/ctm/patrix/sculk/block"
OURS = ROOT / "_build/rp04-142/textures/blocks/sculk.png"
OUT = ROOT / "_docs/sculk"; OUT.mkdir(parents=True, exist_ok=True)
N, PX = 6, 96
FT = {1: 19, 2: 27, 3: 23, 4: 15}                   # Patrix frametimes (ticks); frames [0,0,1] -> period 3 x ft
SEQ = [0, 0, 1]
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)


def load_tile(n):
    a = np.asarray(Image.open(CTM / f"{n}.png").convert("RGB")).astype(float)
    return a[:128], a[128:256]


TILES = {n: load_tile(n) for n in (1, 2, 3, 4)}


def at(frames, ft, t):
    """Java / Bedrock blended flipbook: frame list SEQ, each entry ft ticks, linear blend to the next entry"""
    pos = (t / ft) % len(SEQ); i = int(pos); f = pos - i
    a, b = frames[SEQ[i]], frames[SEQ[(i + 1) % len(SEQ)]]
    return a * (1 - f) + b * f


def base_frames():
    base = np.asarray(Image.open(OURS).convert("RGB")).astype(float)
    s = np.asarray(Image.open(PAT / "textures/block/sculk_s.png").convert("RGBA")).astype(float)
    glow = ((s[..., 3] > 0) & (s[..., 3] < 255)).astype(float)[..., None]
    return base, np.clip(base * (1 + 0.20 * glow), 0, 255)


BASE = base_frames()


def floor(option, t, seed=7):
    rnd = random.Random(seed)
    img = np.zeros((N * 128, N * 128, 3))
    for by in range(N):
        for bx in range(N):
            if option == "NOW":
                tile = BASE[0]
            elif option == "JAVA":
                n = 1 + (bx % 2) + 2 * (by % 2); tile = at(TILES[n], FT[n], t)
            elif option == "RANDOM":
                n = rnd.choice((1, 2, 3, 4)); tile = at(TILES[n], FT[n], t)
            elif option == "MOSAIC":
                q = np.zeros((256, 256, 3))
                for n, (oy, ox) in {1: (0, 0), 2: (0, 128), 3: (128, 0), 4: (128, 128)}.items():
                    q[oy:oy + 128, ox:ox + 128] = at(TILES[n], FT[n], t)
                tile = np.asarray(Image.fromarray(q.astype(np.uint8)).resize((128, 128), Image.LANCZOS)).astype(float)
            else:                                      # BASE+PULSE
                n = rnd.choice((1, 2, 3, 4)); tile = at(BASE, FT[n], t)
            img[by * 128:(by + 1) * 128, bx * 128:(bx + 1) * 128] = tile
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((N * PX, N * PX), Image.LANCZOS)


OPTS = [("NOW", "1 NOW (shipped): still"), ("JAVA", "2 JAVA Patrix (reference)"), ("RANDOM", "3 RANDOM tiles (Bedrock)"),
        ("MOSAIC", "4 MOSAIC in one block"), ("BASE+PULSE", "5 BASE + PULSE (derived)")]


def panel(t, label_t):
    W = N * PX
    sheet = Image.new("RGB", (len(OPTS) * (W + 8), W + 30), (235, 235, 235)); d = ImageDraw.Draw(sheet)
    for i, (k, lab) in enumerate(OPTS):
        sheet.paste(floor(k, t), (i * (W + 8), 30)); d.text((i * (W + 8) + 4, 6), f"{lab}  {label_t}", fill=(0, 0, 0), font=F)
    return sheet


def main():
    a, b = panel(0, "t=0"), panel(19 * 1.5, "mid-pulse")
    s = Image.new("RGB", (a.width, a.height * 2 + 6), (255, 255, 255)); s.paste(a, (0, 0)); s.paste(b, (0, a.height + 6))
    s.save(OUT / "SCULK-OPTIONS.png")
    frames = [panel(t, "").resize((a.width // 2, a.height // 2), Image.LANCZOS) for t in range(0, 120, 4)]
    frames[0].save(OUT / "SCULK-OPTIONS.gif", save_all=True, append_images=frames[1:], duration=50, loop=0)
    print(OUT / "SCULK-OPTIONS.png", s.size, "|", OUT / "SCULK-OPTIONS.gif", len(frames), "frames")


if __name__ == "__main__":
    main()
