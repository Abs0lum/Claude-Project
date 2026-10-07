#!/usr/bin/env python3
"""pack_geo_preview.py — render geometries AS SHIPPED in a build dir (file JSON -> bb_truth faces), with a texture.
Usage: pack_geo_preview.py <build_dir> <out.png> <geometry_id>=<texture relpath> [...]"""
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV
W, H = 300, 270
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)


def faces_of(dst, gid):
    p, g = R.geo_file(dst, gid)
    b = g["bones"]; tw, th = g["description"]["texture_width"], g["description"]["texture_height"]
    return truth_posed_faces(b, tw, th, bone_affines(b))


def sheet(dst, out, pairs, views=("front", "front-east", "east", "top")):
    rows = []
    for gid, tex in pairs:
        f = faces_of(dst, gid)
        row = Image.new("RGB", (len(views) * (W + 4) - 4, H), (255, 255, 255))
        for i, v in enumerate(views):
            e, t = camera(f, v); fl = min(0.0, min(q[1] for x in f for q in x.pts))
            im = render_entity(f, dst / tex, e, t, W, H, fov=FOV, floor_y=fl).convert("RGB")
            ImageDraw.Draw(im).text((4, 4), f"{gid} - {v}", fill=(0, 0, 0), font=F)
            row.paste(im, (i * (W + 4), 0))
        rows.append(row)
    img = Image.new("RGB", (rows[0].width, len(rows) * (H + 4) - 4), (255, 255, 255))
    for i, r in enumerate(rows): img.paste(r, (0, i * (H + 4)))
    img.save(out); return out


if __name__ == "__main__":
    dst = Path(sys.argv[1]); pairs = [tuple(a.split("=", 1)) for a in sys.argv[3:]]
    print(sheet(dst, sys.argv[2], pairs))
