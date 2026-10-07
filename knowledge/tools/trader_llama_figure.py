#!/usr/bin/env python3
"""trader_llama_figure.py — the witness figure for RP-07 v1.4.11 (D-C253).
Row 1: his 09:57 screenshot (white trader llama, 2x) | the SHIPPED trader geometry rendered from a matching camera |
       the FIXED trader (= the ordinary llama geometry) from the same camera.
Row 2: side-view schematics with numbers (cube units) for ordinary llama / trader now / trader fixed.
"""
import sys, math
sys.path.insert(0, "/home/claude/tools")
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from entity_render import load_geo, render, extents

ROOT = Path("/home/claude"); OUT = ROOT / "_design/trader-llama-geometry-v1411.png"
SHOT = Path("/root/.claude/uploads/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/fc8d4466-image.png")
G = ROOT / "_build/rp07-1410/models/entity"
COL = {"body_cube": (222, 208, 176), "head2": (236, 226, 200), "snout": (200, 186, 160), "left_ear": (210, 196, 166), "right_ear": (210, 196, 166),
       "leg0": (226, 222, 214), "leg1": (226, 222, 214), "leg2": (226, 222, 214), "leg3": (226, 222, 214)}
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)


def cam(az_deg, dist, eye_y=34.5, tgt=(0, 18, -6)):
    az = math.radians(az_deg)
    return (tgt[0] + dist * math.sin(az), eye_y, tgt[2] - dist * math.cos(az)), tgt


def side_view(cubes, title, notes, size=(520, 420)):
    """Orthographic side view (x collapsed), head at the left: z -> horizontal (front = left), y up."""
    W, H = size; im = Image.new("RGB", size, (250, 248, 244)); d = ImageDraw.Draw(im)
    s = 8.0; ox, oy = W / 2 + 10, H - 40
    def X(z): return ox + z * s
    def Y(y): return oy - y * s
    for y in range(0, 41, 8):
        d.line([(30, Y(y)), (W - 10, Y(y))], fill=(225, 222, 216)); d.text((6, Y(y) - 7), str(y), fill=(90, 90, 90), font=F)
    d.line([(30, Y(0)), (W - 10, Y(0))], fill=(60, 60, 60), width=2)
    order = ["body_cube", "head2", "snout", "left_ear", "right_ear", "leg0", "leg1", "leg2", "leg3"]
    drawn = set()
    for bone in order:
        for b, P in cubes:
            if b != bone: continue
            key = (b, round(min(p[1] for p in P), 1), round(min(p[2] for p in P), 1))
            if key in drawn: continue
            drawn.add(key)
            y0, y1 = min(p[1] for p in P), max(p[1] for p in P); z0, z1 = min(p[2] for p in P), max(p[2] for p in P)
            col = COL.get(b, (200, 200, 200))
            d.rectangle([X(z0), Y(y1), X(z1), Y(y0)], fill=col, outline=(70, 60, 50))
    d.text((34, 6), title, fill=(30, 30, 30), font=FB)
    yy = 28
    for n in notes: d.text((34, yy), n, fill=(60, 60, 60), font=F); yy += 18
    d.text((W - 120, H - 30), "front = left", fill=(90, 90, 90), font=F)
    return im


def main():
    tr = load_geo(G / "trader_llama.geo.json", "geometry.trader_llama.patrix")
    ll = load_geo(G / "llama.geo.json", "geometry.llama.patrix")
    eye, tgt = cam(45, 40)
    a = render(tr, eye, tgt, fov=70, size=(420, 640), colours=COL, ground=0)
    b = render(ll, eye, tgt, fov=70, size=(420, 640), colours=COL, ground=0)
    shot = Image.open(SHOT).crop((1100, 250, 1500, 880)).resize((406, 640), Image.LANCZOS)
    W, H = 420 * 3 + 40, 640 + 60 + 420 + 50
    im = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(im)
    d.text((10, 8), "TRADER LLAMA — your screen vs what the two geometry files predict (same camera: eye ~1.5 cubes above the body top, front-left)", fill=(20, 20, 20), font=FB)
    labels = ["A  your screenshot 09:57 (white trader llama)", "B  SHIPPED trader geometry (1.4.10) — render", "C  FIXED 1.4.11 = the ordinary llama geometry — render"]
    for i, (img, lab) in enumerate(zip([shot, a, b], labels)):
        x = 10 + i * 430; im.paste(img, (x, 60)); d.text((x, 40), lab, fill=(20, 20, 20), font=FB)
    notes_l = ["body y 13–24 sits on legs 0–16", "neck 15–33 rises from inside the body", "head pivot 24"]
    notes_t = ["body y 22–33 FLOATS 9 above legs 0–13", "neck 15–33 hangs 7 below the body", "3 cubes proud of its front; head pivot 21"]
    notes_f = ["same bones + cubes as the ordinary llama", "trader textures + decor unchanged", ""]
    y2 = 60 + 640 + 30
    for i, (c, t, n) in enumerate([(ll, "ordinary llama (geometry.llama.patrix)", notes_l), (tr, "trader NOW (1.4.10 trader_llama.patrix)", notes_t), (ll, "trader FIXED (1.4.11 = llama geometry, renamed)", notes_f)]):
        im.paste(side_view(c, t, n), (10 + i * 430, y2))
    d.text((10, y2 - 22), "Side views, cube units (1 block = 16), front at the left", fill=(60, 60, 60), font=F)
    OUT.parent.mkdir(exist_ok=True); im.save(OUT); print(OUT, im.size)


if __name__ == "__main__":
    main()
