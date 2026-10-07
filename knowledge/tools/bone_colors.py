#!/usr/bin/env python3
"""bone_colors.py — flat-colour render of a geometry, one colour per bone (legend), to name the parts in a witness shot.
usage: bone_colors.py <rp> <ident> <out> <view>[,<view>] [zoom] [bone,bone,...(only these)]"""
import sys, math, colorsys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import Cam, _fill, to_world_faces, DIM
from truth_compare import geometry, cam
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
W, H = 520, 420

def render(faces, colors, eye, tgt):
    faces = to_world_faces(faces); c = Cam(eye, tgt, W, H, 50.0)
    z = np.full((H, W), np.inf, np.float32); img = np.zeros((H, W, 3), np.float32); img[:] = 0.9
    for f in faces:
        pr = [c.project(p) for p in f.pts]
        if any(q[2] <= 0.5 for q in pr): continue
        _fill(img, z, pr, None, None, np.array(colors[f.bone], np.float32) * DIM[f.name], W, H)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))

def main(rp, ident, out, views, zoom=1.0, only=None):
    bones, tw, th = geometry(rp, ident); aff = bone_affines(bones)
    faces = truth_posed_faces(bones, tw, th, aff)
    if only: faces = [f for f in faces if f.bone in only]
    names = sorted({f.bone for f in faces})
    colors = {n: colorsys.hsv_to_rgb(i / max(1, len(names)), 0.75, 0.95) for i, n in enumerate(names)}
    cells = []
    for v in views:
        e, t = cam(faces, v, zoom); im = render(faces, colors, e, t); d = ImageDraw.Draw(im); d.text((4, 2), v, fill=(0, 0, 0), font=FB); cells.append(im)
    leg = Image.new("RGB", (170, H), (255, 255, 255)); d = ImageDraw.Draw(leg)
    for i, n in enumerate(names):
        d.rectangle([4, 4 + i * 14, 14, 14 + i * 14], fill=tuple(int(x * 255) for x in colors[n])); d.text((18, 3 + i * 14), n, fill=(0, 0, 0), font=FB)
    sheet = Image.new("RGB", (len(cells) * (W + 4) + 170, H), (255, 255, 255))
    for i, c in enumerate(cells): sheet.paste(c, (i * (W + 4), 0))
    sheet.paste(leg, (len(cells) * (W + 4), 0)); sheet.save(out); print(out)

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], a[4].split(","), float(a[5]) if len(a) > 5 else 1.0, set(a[6].split(",")) if len(a) > 6 else None)
