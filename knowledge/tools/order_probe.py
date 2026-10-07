#!/usr/bin/env python3
"""order_probe.py — D-C278 hypothesis test: render a geometry with the Euler order we assume (X first: v' = Rz Ry Rx v,
Blockbench 'ZYX') and with the reverse (Z first: v' = Rx Ry Rz v), same witness-like camera, side by side.
usage: order_probe.py <rp> <ident> <texture> <out> "ex,ey,ez"[;"ex,ey,ez"...] [fov]"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
import entity_render, equine_compare, bb_truth
from entity_render import rot_x, rot_y, rot_z
from equine_compare import bone_affines
from entity_tex_render import render_entity
from truth_compare import geometry, FB

def t_zfirst(p, pivot, rot):
    q = [p[i] - pivot[i] for i in range(3)]
    q = rot_z(q, -rot[2]); q = rot_y(q, rot[1]); q = rot_x(q, -rot[0])
    return [q[i] + pivot[i] for i in range(3)]

ORIG = entity_render.transform

def render(rp, ident, tex, eye, order, fov):
    fn = ORIG if order == "X-first (assumed)" else t_zfirst
    equine_compare.transform = fn; bb_truth.transform = fn
    bones, tw, th = geometry(rp, ident)
    faces = bb_truth.truth_posed_faces(bones, tw, th, bone_affines(bones))
    P = np.array([p for f in faces for p in f.pts]) * np.array([1, 1, -1]); c = (P.min(0) + P.max(0)) / 2
    im = render_entity(faces, tex, [float(x) * 16 for x in eye.split(",")], list(c), 560, 420, fov=fov, floor_y=0.0).convert("RGB")
    ImageDraw.Draw(im).text((4, 2), f"{order} · eye {eye}", fill=(0, 0, 0), font=FB); return im

def main(rp, ident, tex, out, eyes, fov=70.0):
    cells = []
    for eye in eyes.split(";"):
        for order in ("X-first (assumed)", "Z-first (alternative)"):
            cells.append(render(rp, ident, tex, eye, order, fov))
    equine_compare.transform = ORIG; bb_truth.transform = ORIG
    sheet = Image.new("RGB", (2 * 564, (len(cells) // 2) * 424), (255, 255, 255))
    for i, c in enumerate(cells): sheet.paste(c, ((i % 2) * 564, (i // 2) * 424))
    sheet.save(out); print(out)

if __name__ == "__main__":
    a = sys.argv; main(a[1], a[2], a[3], a[4], a[5], float(a[6]) if len(a) > 6 else 70.0)
