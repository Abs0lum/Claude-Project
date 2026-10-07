#!/usr/bin/env python3
"""size_lineup.py — D-C284: the size relationship as a picture. Each mob side-on at ONE scale (near-orthographic camera), before
(RP-07 1.4.20) and after (1.4.21), next to a 5'10" player silhouette (1.875 blocks) and a 1-block bar.
usage: size_lineup.py <out_png>"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import visible_size as V
import molang_lint as ML
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from block_render import Face

ROOT = Path("/home/claude")
BEFORE, AFTER = ROOT / "_build/rp07-1420", ROOT / "_build/rp07-1421"
STACK = [ROOT / "_build/rp08-148", ROOT / "_build/rp06-1415", ROOT / "_build/rp05-51"]
MOBS = ["sheep", "wolf", "fox", "ocelot", "cat", "rabbit", "chicken", "axolotl", "frog", "pufferfish", "tropicalfish", "tadpole", "bee"]
PPB = 64.0                     # image pixels per block
S = PPB / 16.0                 # image pixels per model pixel
D = 4000.0                     # camera distance (model px): near-orthographic
H = 190; BASE = H - 26
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)


def mob_faces(pack, stem):
    desc = ML._parse_json((pack / f"entity/{stem}.entity.json").read_text(encoding="utf-8-sig"))["minecraft:client_entity"]["description"]
    roots = [pack] + STACK + [V.VANILLA]
    bones, tw, th = V.find_geometry(roots, desc["geometry"]["default"])
    tex = desc.get("textures") or {}
    tp = V.find_texture(roots, tex.get("default") or next(iter(tex.values())))
    cs = V.client_scale(desc)
    cond = V.conditional_bones(desc, V.render_controllers(roots))
    par = {b["name"]: b.get("parent") for b in bones}
    def hidden(n):
        while n:
            if n.lower() in cond: return True
            n = par.get(n)
        return False
    faces = [f for f in truth_posed_faces(bones, tw, th, bone_affines(bones)) if not hidden(f.bone)]
    return [Face([[p[0] * cs, p[1] * cs, p[2] * cs] for p in f.pts], f.uv, f.mat, f.name, f.bone) for f in faces], tp, cs


def render_mob(pack, stem):
    faces, tp, cs = mob_faces(pack, stem)
    P = np.array([p for f in faces for p in f.pts]) * np.array([1, 1, -1])
    lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2
    Wc = int((hi[2] - lo[2]) * S) + 30
    focal = S * D
    fov = 2 * np.degrees(np.arctan((H / 2) / focal))
    ty = (H / 2 - (H - BASE)) / S            # ground (y = 0) lands on the BASE row
    eye = [c[0] + D, ty, c[2]]; tgt = [c[0], ty, c[2]]
    im = render_entity(faces, str(tp), eye, tgt, Wc, H, fov=fov, bg=(236, 240, 246), floor_y=None).convert("RGB")
    return im, cs


def person(d, x0):
    """side-on 5'10" silhouette: Steve's 32-px model x 0.9375 (head 8, body + arms 12, legs 12; 4 px deep, head 8)."""
    k = 0.9375 * S
    def box(xa, y_top, w, h): d.rectangle([xa, BASE - y_top * k, xa + w * k, BASE - (y_top - h) * k], fill=(120, 124, 132), outline=(60, 60, 70))
    box(x0 + 2 * k, 12, 4, 12); box(x0 + 2 * k, 24, 4, 12); box(x0, 32, 8, 8)
    d.text((x0 - 6, BASE + 4), "you 5'10\"", fill=(40, 40, 50), font=F)
    return int(x0 + 8 * k + 16)


def row(pack, label, col):
    cells = [render_mob(pack, m) for m in MOBS]
    Wt = 120 + sum(c[0].width for c in cells) + 8 * len(cells)
    img = Image.new("RGB", (Wt, H + 22), (236, 240, 246)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, Wt, 20], fill=col); d.text((6, 3), label, fill="white", font=FB)
    x = person(d, 24)
    for (im, cs), m in zip(cells, MOBS):
        img.paste(im, (x, 22)); d.text((x + 4, 22 + BASE + 6), m, fill=(20, 20, 30), font=F)
        x += im.width + 8
    d.line([0, 22 + BASE, Wt, 22 + BASE], fill=(90, 90, 100), width=1)
    d.rectangle([Wt - 90, 30, Wt - 90 + PPB, 36], fill=(30, 30, 30)); d.text((Wt - 90, 38), "1 block", fill=(30, 30, 30), font=F)
    return img


def main(out):
    a = row(BEFORE, "BEFORE — RP-07 1.4.20 (drawn size today)", (130, 30, 30))
    b = row(AFTER, "AFTER — RP-07 1.4.21 (real-size relationship, your character = 5'10\")", (30, 70, 140))
    W = max(a.width, b.width)
    s = Image.new("RGB", (W, a.height + b.height + 6), (255, 255, 255)); s.paste(a, (0, 0)); s.paste(b, (0, a.height + 6))
    s.save(out); print(out, s.size)


if __name__ == "__main__":
    main(sys.argv[1])
