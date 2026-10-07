#!/usr/bin/env python3
"""truth_ba.py — BEFORE/AFTER with the truth placement (bb_truth): same geometry id from two model roots, same cameras.
usage: truth_ba.py <root_before> <root_after> <ident> <texture> <out> <view>[,<view>] [zoom] [label_before] [label_after]"""
import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from truth_compare import geometry, cam, W, H, FB


def main(rb, ra, ident, tex, out, views, zoom=1.0, lb="BEFORE (ships now)", la="AFTER"):
    sets = []
    for root, lab in ((rb, lb), (ra, la)):
        bones, tw, th = geometry(root, ident); sets.append((lab, truth_posed_faces(bones, tw, th, bone_affines(bones))))
    cells = []
    for v in views:
        for i, (lab, fs) in enumerate(sets):
            e, t = cam(sets[0][1], v, zoom)
            im = render_entity(fs, tex, e, t, W, H, fov=50.0, floor_y=0.0).convert("RGB"); d = ImageDraw.Draw(im)
            d.rectangle([0, 0, W, 18], fill=(130, 30, 30) if i == 0 else (30, 110, 60)); d.text((4, 2), f"{lab} — {v}", fill=(255, 255, 255), font=FB)
            cells.append(im)
    sheet = Image.new("RGB", (2 * (W + 4), len(views) * (H + 4)), (255, 255, 255))
    for i, c in enumerate(cells): sheet.paste(c, ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    sheet.save(out); print(out)


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], a[4], a[5], a[6].split(","), float(a[7]) if len(a) > 7 else 1.0, *(a[8:10]))
