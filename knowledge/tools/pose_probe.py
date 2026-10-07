#!/usr/bin/env python3
"""pose_probe.py — render a shipped geometry (truth placement) with extra animation rotations on named bones, from a
witness-like camera (eye position in blocks relative to the mob's feet, world frame: +z = the mob's front/south).
usage: pose_probe.py <rp> <ident> <texture> <out> "<bone>:rx,ry,rz;<bone>:..." "ex,ey,ez" [fov]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from truth_compare import geometry, FB

def main(rp, ident, tex, out, poses, eye, fov=70.0):
    bones, tw, th = geometry(rp, ident)
    add = {}
    for item in [p for p in poses.split(";") if p.strip()]:
        n, v = item.split(":"); add[n] = [float(x) for x in v.split(",")]
    faces = truth_posed_faces(bones, tw, th, bone_affines(bones, add_rot=add))
    P = np.array([p for f in faces for p in f.pts]) * np.array([1, 1, -1]); c = (P.min(0) + P.max(0)) / 2
    e = [float(x) * 16 for x in eye.split(",")]
    im = render_entity(faces, tex, e, list(c), 700, 520, fov=fov, floor_y=0.0).convert("RGB")
    ImageDraw.Draw(im).text((4, 2), f"{ident} · {poses or 'rest'} · eye {eye} blocks", fill=(0, 0, 0), font=FB)
    im.save(out); print(out)

if __name__ == "__main__":
    a = sys.argv; main(a[1], a[2], a[3], a[4], a[5], a[6], float(a[7]) if len(a) > 7 else 70.0)
