#!/usr/bin/env python3
"""Before | after sheets for the Academy II renders (round 232 #23). Usage: compose_ba.py <before dir> <after dir> <out dir>.
Full sheets for the 4 views + zoomed crops of the central building (plan frame: px = 70 + 4 z, py = 110 + 4 x)."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

B, A, OUT = sys.argv[1:4]
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
F2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
VIEWS = {"GROUND": "ACADEMY-II-PLAN-GROUND.png", "UPPER": "ACADEMY-II-PLAN-UPPER.png",
         "BASEMENT": "ACADEMY-II-PLAN-BASEMENT.png", "MASSING": "ACADEMY-II-MASSING.png"}
HEAD = 70


def sheet(left, right, title_l, title_r, note, fname):
    w, h = left.width + right.width + 30, max(left.height, right.height) + HEAD + 40
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((20, 14), title_l, fill=(120, 30, 30), font=F)
    d.text((left.width + 50, 14), title_r, fill=(20, 90, 40), font=F)
    img.paste(left, (0, HEAD))
    img.paste(right, (left.width + 30, HEAD))
    d.line([(left.width + 15, HEAD), (left.width + 15, h - 40)], fill=(60, 60, 60), width=4)
    d.text((20, h - 34), note, fill=(60, 60, 60), font=F2)
    img.save(os.path.join(OUT, fname))
    print("wrote", fname, img.size)


def px(x, z):
    return 70 + 4 * z, 110 + 4 * x


NOTE = ("Top-down plans: gate side (x 0) at the TOP, lake at the bottom, z 0 at the LEFT. 1 block = 4 px. "
        "Before = round-231 scripts untouched; after = round 232 #23 (tower at the crossing).")
for k, fn in VIEWS.items():
    lb, ra = Image.open(os.path.join(B, fn)), Image.open(os.path.join(A, fn))
    note = NOTE if k != "MASSING" else "3/4 view from the gate-side corner (gate side nearest, lake at the top right). Sketch only."
    sheet(lb, ra, f"BEFORE (231): {k}", f"AFTER (232 #23): {k}", note, f"ACAD-BA-{k}.png")
    if k != "MASSING":
        x0, z0, x1, z1 = 88, 84, 262, 300                     # central building + its courts and the cloister ring
        a, b = px(x0, z0), px(x1, z1)
        box = (a[0], a[1], b[0], b[1])
        cl, cr = lb.crop(box), ra.crop(box)
        cl = cl.resize((cl.width * 3 // 2, cl.height * 3 // 2), Image.LANCZOS)
        cr = cr.resize((cr.width * 3 // 2, cr.height * 3 // 2), Image.LANCZOS)
        sheet(cl, cr, f"BEFORE: {k} centre", f"AFTER: {k} centre",
              f"Crop x {x0}-{x1}, z {z0}-{z1} at 6 px per block; gate side at the top.", f"ACAD-BA-CENTRE-{k}.png")
