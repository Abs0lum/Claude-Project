#!/usr/bin/env python3
"""truth_compare.py — render a shipped geometry with the OLD face placement (equine_compare.posed_faces) and the
TRUTH placement (bb_truth, D-C278) side by side, same cameras, so a witness screenshot can be matched to one of them.
usage: truth_compare.py <rp_build_dir> <geometry_identifier> <texture_png> <out_png> <view>[,<view>...] [zoom]"""
import sys, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines, posed_faces
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity, load_json
from convb_preview3 import DIRS

W, H = 420, 340
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)


def geometry(rp, ident):
    for p in Path(rp, "models/entity").rglob("*.json"):
        try: d = load_json(p)
        except Exception: continue
        for g in d.get("minecraft:geometry", []):
            if g["description"]["identifier"] == ident:
                return g["bones"], g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)
    raise SystemExit(f"no {ident} in {rp}")


def cam(faces, view, zoom=1.0, focus=None):
    P = np.array([p for f in faces for p in f.pts]) * np.array([1, 1, -1])
    lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2 if focus is None else np.array(focus, float) * np.array([1, 1, -1])
    r = float(np.linalg.norm(hi - lo)) / 2
    d = np.array(DIRS[view], float); d /= np.linalg.norm(d)
    dist = max(10.0, r / math.sin(math.radians(25)) * 1.15) / zoom
    return list(c + d * dist), list(c)


def main(rp, ident, tex, out, views, zoom=1.0, focus=None):
    bones, tw, th = geometry(rp, ident)
    aff = bone_affines(bones)
    sets = {"OLD placement": posed_faces(bones, tw, th, aff), "TRUTH placement": truth_posed_faces(bones, tw, th, aff)}
    cells = []
    for view in views:
        for k, fs in sets.items():
            e, t = cam(sets["TRUTH placement"], view, zoom, focus)
            im = render_entity(fs, tex, e, t, W, H, fov=50.0, floor_y=0.0).convert("RGB")
            d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 18], fill=(30, 70, 140) if k.startswith("TRUTH") else (130, 30, 30))
            d.text((4, 2), f"{k} — {view}", fill=(255, 255, 255), font=FB); cells.append(im)
    cols = 2; rows = len(views)
    sheet = Image.new("RGB", (cols * (W + 4), rows * (H + 4)), (255, 255, 255))
    for i, c in enumerate(cells): sheet.paste(c, ((i % cols) * (W + 4), (i // cols) * (H + 4)))
    sheet.save(out); print(out)


if __name__ == "__main__":
    a = sys.argv
    focus = [float(x) for x in a[7].split(",")] if len(a) > 7 else None
    main(a[1], a[2], a[3], a[4], a[5].split(","), float(a[6]) if len(a) > 6 else 1.0, focus)
