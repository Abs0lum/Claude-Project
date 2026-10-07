#!/usr/bin/env python3
"""before_after.py — D-C283: render ONE geometry identifier from two pack builds with the same cameras (bb_truth face placement,
the renderer every witness match since D-C278 has used), BEFORE on the left, AFTER on the right, one row per view.
The camera is framed on the AFTER model so both cells share it exactly.
usage: before_after.py <rp_before> <rp_after> <geometry_identifier> <texture_png> <out_png> <view>[,<view>...] [zoom] [focus x,y,z]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from truth_compare import geometry, cam, W, H, FB


def faces_of(rp, ident):
    bones, tw, th = geometry(rp, ident)
    return truth_posed_faces(bones, tw, th, bone_affines(bones))


def main(rp_a, rp_b, ident, tex, out, views, zoom=1.0, focus=None, labels=("BEFORE", "AFTER")):
    fa, fb = faces_of(rp_a, ident), faces_of(rp_b, ident)
    cells = []
    for view in views:
        e, t = cam(fb, view, zoom, focus)
        for lab, fs, col in ((labels[0], fa, (130, 30, 30)), (labels[1], fb, (30, 70, 140))):
            im = render_entity(fs, tex, e, t, W, H, fov=50.0, floor_y=0.0).convert("RGB")
            d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 18], fill=col)
            d.text((4, 2), f"{lab} — {view}", fill=(255, 255, 255), font=FB); cells.append(im)
    sheet = Image.new("RGB", (2 * (W + 4), len(views) * (H + 4)), (255, 255, 255))
    for i, c in enumerate(cells): sheet.paste(c, ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    Path(out).parent.mkdir(parents=True, exist_ok=True); sheet.save(out); print(out)


if __name__ == "__main__":
    a = sys.argv
    focus = [float(x) for x in a[8].split(",")] if len(a) > 8 else None
    main(a[1], a[2], a[3], a[4], a[5], a[6].split(","), float(a[7]) if len(a) > 7 else 1.0, focus)
