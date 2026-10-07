#!/usr/bin/env python3
"""convb_closeup.py — head / part close-ups, NEW (convb_build) vs OLD (shipping), same cameras.
Usage: convb_closeup.py <stem> <gkey> <jname> <tkey> <cx> <cy> <cz> <dist> [out.png]   (target in Bedrock file coords, px)"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from convb_preview2 import entity, geo
from convb_build import build_mob
from convb_preview import library, bind_info
from equine_compare import bone_affines, posed_faces
from entity_tex_render import render_entity
from face_alpha_census import resolve_texture


def closeup(stem, gkey, jname, tkey, target, dist, out, hide_new=(), size=(420, 340)):
    tag, rp, desc = entity(stem); anims, rcs = library(rp)
    old, otw, oth = geo(rp, desc["geometry"][gkey]); names, rel, _ = bind_info(desc, anims, rcs)
    new, tw, th, info = build_mob(jname, stem, names, old, look_bones=["head"] if rel else [])
    new = [b for b in new if b["name"] not in hide_new]
    tp = resolve_texture(desc["textures"][tkey])
    oldn = {b["name"] for b in old}
    nf = posed_faces(new, tw, th, bone_affines(new))
    of = posed_faces(old, otw, oth, bone_affines(old, abs_rot={n: [0, 0, 0] for n in rel if n in oldn}))
    cx, cy, cz = target; tw_ = [cx, cy, -cz]          # render_entity(world=True) flips z
    views = {"side E": (1, 0.25, 0), "front-E": (0.7, 0.3, 0.7), "front": (0, 0.2, 1), "side W": (-1, 0.25, 0)}
    try: F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    except Exception: F = ImageFont.load_default()
    rows = []
    for faces, lab, col in ((nf, "NEW", (30, 70, 140)), (of, "OLD", (130, 30, 30))):
        cells = []
        for vn, d in views.items():
            d = np.array(d, float); d /= np.linalg.norm(d)
            eye = [tw_[0] + d[0] * dist, tw_[1] + d[1] * dist, tw_[2] + d[2] * dist]
            im = render_entity(faces, tp, eye, tw_, size[0], size[1], fov=40, floor_y=0.0).convert("RGB")
            dr = ImageDraw.Draw(im); dr.rectangle([0, 0, size[0], 20], fill=col); dr.text((5, 3), f"{stem} {lab} — {vn}", fill=(255, 255, 255), font=F)
            cells.append(im)
        row = Image.new("RGB", (len(cells) * (size[0] + 4) - 4, size[1]), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * (size[0] + 4), 0))
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, 2 * size[1] + 4), (255, 255, 255)); sheet.paste(rows[0], (0, 0)); sheet.paste(rows[1], (0, size[1] + 4))
    sheet.save(out); return out


if __name__ == "__main__":
    a = sys.argv[1:]
    closeup(a[0], a[1], a[2], a[3], [float(a[4]), float(a[5]), float(a[6])], float(a[7]), a[8] if len(a) > 8 else f"/home/claude/_docs/convb/closeup_{a[0]}.png")
