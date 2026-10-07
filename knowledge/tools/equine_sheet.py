#!/usr/bin/env python3
"""equine_sheet.py — the one-page comparison sheet for his 09-28 18:36 question (horse / donkey / mule / zombie horse /
skeleton horse): per mob, Patrix at rest (what it is supposed to look like) vs ours in game (what our files draw), from the
side his shot was taken, plus his shot.  Uses equine_compare's model (seeded FreshLX rest pose; look_at relative_to)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import MOBS, patrix_bones, our_bones, bone_affines, posed_faces, texture
from entity_tex_render import render_entity

ROOT = Path("/home/claude"); OUT = ROOT / "_docs/equine"
SHOTS = {"horse": ("124030.png", (1080, 200, 1780, 720), "west"), "donkey": ("124101.png", (1080, 140, 1760, 600), "east"),
         "mule": ("124118.png", (980, 130, 1680, 560), "west"), "zombie_horse": (None, None, "west"), "skeleton_horse": (None, None, "west")}
REF = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/ref/crop_horse.jpg")
W, H = 460, 345
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17); FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    FT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
except Exception:
    FB = FR = FT = ImageFont.load_default()


def cam(view, dist=58.0):
    # side views centred on the neck/head junction region (world frame: mob faces SOUTH = +z)
    tgt = [0.0, 22.0, 6.0]
    d = {"west": (-1.0, 0.12, 0.10), "east": (1.0, 0.12, 0.10), "front": (0.25, 0.18, 1.0)}[view]
    d = np.array(d); d /= np.linalg.norm(d)
    return [tgt[i] + d[i] * dist for i in range(3)], tgt


def tile(img, title, sub, color=(20, 24, 32)):
    img = img.convert("RGB").resize((W, H)) if img.size != (W, H) else img.convert("RGB")
    d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 42], fill=color)
    d.text((8, 3), title, fill=(255, 255, 255), font=FB); d.text((8, 23), sub, fill=(215, 222, 235), font=FR)
    return img


def fit(img):
    im = img.convert("RGB"); r = min(W / im.width, (H - 42) / im.height)
    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))))
    c = Image.new("RGB", (W, H), (236, 238, 242)); c.paste(im, ((W - im.width) // 2, 42 + (H - 42 - im.height) // 2)); return c


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for mob in MOBS:
        pb, ptw, pth = patrix_bones(mob); ob, otw, oth = our_bones(mob)
        pf = posed_faces(pb, ptw, pth, bone_affines(pb))
        of = posed_faces(ob, otw, oth, bone_affines(ob, abs_rot={n: [0, 0, 0] for n in MOBS[mob][4]}))
        tex = texture(mob); shot, box, view = SHOTS[mob]
        e, t = cam(view); ef, tf = cam("front", 64)
        cells = [tile(render_entity(pf, tex, e, t, W, H, fov=60, floor_y=0), f"{mob.replace('_', ' ').upper()} — PATRIX (target)", "Java: the Patrix JEM + FreshLX rest pose", (22, 90, 52)),
                 tile(render_entity(of, tex, e, t, W, H, fov=60, floor_y=0), f"{mob.replace('_', ' ').upper()} — OURS in game", "RP files + look-at (relative to entity), at rest", (130, 30, 30)),
                 tile(render_entity(pf, tex, ef, tf, W, H, fov=60, floor_y=0), "PATRIX — front", "two ears, head angled down", (22, 90, 52)),
                 tile(render_entity(of, tex, ef, tf, W, H, fov=60, floor_y=0), "OURS — front", "", (130, 30, 30))]
        if shot:
            cells.append(tile(fit(Image.open(ROOT / "_intake/r2-shots" / shot).crop(box)), f"HIS SHOT {shot[:-4]} (09-28)", "RP-07 1.4.13 on the PS5 / phone", (40, 60, 120)))
        elif mob == "zombie_horse" and REF.exists():
            cells.append(tile(fit(Image.open(REF)), "WEB REFERENCE (search)", "Patrix horse, video thumbnail (YouTube)", (40, 60, 120)))
        else:
            cells.append(tile(Image.new("RGB", (W, H), (236, 238, 242)), "no shot for this mob yet", "", (90, 90, 90)))
        row = Image.new("RGB", (len(cells) * (W + 6) - 6, H), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * (W + 6), 0))
        rows.append(row)
    head = Image.new("RGB", (rows[0].width, 56), (20, 24, 32)); d = ImageDraw.Draw(head)
    d.text((12, 12), "EQUINE FAMILY — what Patrix looks like (green) vs what our files draw in game (red) vs his shots (blue) · 2026-09-28", fill=(255, 255, 255), font=FT)
    sheet = Image.new("RGB", (rows[0].width, 56 + sum(r.height + 8 for r in rows)), (255, 255, 255)); sheet.paste(head, (0, 0))
    y = 62
    for r in rows: sheet.paste(r, (0, y)); y += r.height + 8
    sheet.save(OUT / "equine_family_compare.png"); print(OUT / "equine_family_compare.png", sheet.size)


if __name__ == "__main__":
    main()
