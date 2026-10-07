#!/usr/bin/env python3
"""eye_removal_preview.py — his 09-28 19:20 ruling "get rid of the 3D/animated eyes ... on any mobs": the head of every mob whose
USED geometry carries added eye bones (pupils / lids / brows / eyeballs), rendered front-on with the eye bones and with them
removed, on the texture the entity binds — to prove the painted eyes underneath read as eyes (no blank sockets)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines, posed_faces
from face_alpha_census import all_geometries, resolve_texture
from entity_tex_render import render_entity

ROOT = Path("/home/claude")
# mob -> (geometry id, texture stem, eye bones to remove (descendants go with them), head centre [x,y,z file], dist)
EYES = {
    "villager / wandering trader": ("geometry.villager", "textures/entity/villager2/villager", ["pupil_r", "pupil_l", "lids_main", "brows_main"], [0, 28, -4], 26),
    "bee": ("geometry.bee", "textures/entity/bee/bee", ["eyeballs"], [0, 5, -5], 16),
    "zombie villager": ("geometry.zombie.villager_v2", "textures/entity/zombie_villager2/zombie-villager", ["eye_right", "eye_left", "eyeball", "eyebrown"], [0, 27.5, -4], 26),
    "ravager": ("geometry.ravager", "textures/entity/illager/ravager", ["eyebrow", "pupil_right", "pupil_left", "eyelids"], [0, 20, -28], 50),
}


def strip(bones, names):
    drop = set(names); changed = True
    while changed:
        changed = False
        for b in bones:
            if b["name"] not in drop and b.get("parent") in drop: drop.add(b["name"]); changed = True
    return [b for b in bones if b["name"] not in drop], sorted(drop & {b["name"] for b in bones})


def main():
    G = all_geometries(); cells = []
    try: F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except Exception: F = ImageFont.load_default()
    for label, (gid, tstem, names, c, dist) in EYES.items():
        f, bones, tw, th = G[gid]; tp = resolve_texture(tstem)
        kept, dropped = strip(bones, names)
        eye = [c[0] + dist * 0.25, c[1] + dist * 0.1, -(c[2]) + dist]      # world frame: file z mirrored, mob faces +z
        tgt = [c[0], c[1], -c[2]]
        for title, bs in (("WITH the added eyes (now)", bones), ("eyes REMOVED (proposed)", kept)):
            img = render_entity(posed_faces(bs, tw, th, bone_affines(bs)), tp, eye, tgt, 380, 300, fov=50)
            d = ImageDraw.Draw(img); d.rectangle([0, 0, 380, 22], fill=(20, 24, 32)); d.text((6, 3), f"{label}: {title}", fill=(255, 255, 255), font=F)
            cells.append(img)
        print(f"{label:28s} {gid:30s} remove {dropped}")
    sheet = Image.new("RGB", (2 * 384, (len(cells) // 2) * 304), (255, 255, 255))
    for i, im in enumerate(cells): sheet.paste(im, ((i % 2) * 384, (i // 2) * 304))
    out = ROOT / "_docs/eyes_removal_preview.png"; sheet.save(out); print(out)


if __name__ == "__main__":
    main()
