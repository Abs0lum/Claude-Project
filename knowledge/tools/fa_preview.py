#!/usr/bin/env python3
"""fa_preview.py — D-C290 FA-0: a preview sheet of every flight + aquatic Patrix model, as Converter B would bake it (rest pose =
the JEM's averaged animated pose, water mobs in their in-water branch), textured with the Patrix 1.21.11 128x texture our shipped
mobs use (the nautilus family exists only in Patrix 26.2 -> its 256x texture, the JEM from 26.2).
Faces are placed with bb_truth (the witnessed Bedrock face placement). Three cameras per mob: front-east, east (side), top.
Output: _docs/fa/FA0-PREVIEW-<group>.png (one row per mob) + a printed bake report (bones, cubes, bake errors).
Usage: fa_preview.py [group ...]   groups: fly1 fly2 water1 water2"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import convb
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV

ROOT = Path("/home/claude"); OUT = ROOT / "_docs/fa"
T128 = ROOT / "_intake/patrix12111_128/assets/minecraft/textures/entity"
T262 = ROOT / "_intake/patrix262/assets/minecraft/textures/entity"
CEM262 = ROOT / "_intake/patrix262/assets/minecraft/optifine/cem"
W, H = 300, 250
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception:
    FB = FR = ImageFont.load_default()

# label, jem, texture, source-of-jem
GROUPS = {
    "fly1": [("parrot (red-blue)", "parrot", T128 / "parrot/parrot_red_blue.png", "1.21.11"),
             ("bat", "bat", T128 / "bat.png", "1.21.11"),
             ("allay", "allay", T128 / "allay/allay.png", "1.21.11"),
             ("vex", "vex", T128 / "illager/vex.png", "1.21.11"),
             ("phantom", "phantom", T128 / "phantom.png", "1.21.11")],
    "fly2": [("ghast", "ghast", T128 / "ghast/ghast.png", "1.21.11"),
             ("happy ghast", "happy_ghast", T128 / "ghast/happy_ghast.png", "1.21.11"),
             ("blaze", "blaze", T128 / "blaze.png", "1.21.11"),
             ("breeze", "breeze", T128 / "breeze/breeze.png", "1.21.11"),
             ("wither", "wither", T128 / "wither/wither.png", "1.21.11")],
    "water1": [("squid", "squid", T128 / "squid/squid.png", "1.21.11"),
               ("cod", "cod", T128 / "fish/cod.png", "1.21.11"),
               ("salmon", "salmon", T128 / "fish/salmon.png", "1.21.11"),
               ("pufferfish small", "puffer_fish_small", T128 / "fish/pufferfish.png", "1.21.11"),
               ("tropical fish A", "tropical_fish_a", T128 / "fish/tropical_a.png", "1.21.11"),
               ("tropical fish B", "tropical_fish_b", T128 / "fish/tropical_b.png", "1.21.11")],
    "water2": [("turtle", "turtle", T128 / "turtle/big_sea_turtle.png", "1.21.11"),
               ("tadpole", "tadpole", T128 / "tadpole/tadpole.png", "1.21.11"),
               ("nautilus", "nautilus", T262 / "nautilus/nautilus.png", "26.2"),
               ("zombie nautilus", "zombie_nautilus", T262 / "nautilus/zombie_nautilus.png", "26.2")],
}
VIEWS = [("front-east", "front-east"), ("east", "side (east)"), ("top", "top")]


def bake_any(jname, src):
    old = convb.CEM
    if src == "26.2": convb.CEM = CEM262
    try:
        return convb.bake(jname)
    finally:
        convb.CEM = old


def tile(img, title, sub):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 32], fill=(30, 70, 140))
    d.text((5, 2), title, fill=(255, 255, 255), font=FB); d.text((5, 17), sub, fill=(225, 230, 240), font=FR)
    return img


def sheet(group):
    rows, report = [], []
    for label, jname, tex, src in GROUPS[group]:
        bones, tw, th, info = bake_any(jname, src)
        faces = truth_posed_faces(bones, tw, th, bone_affines(bones))
        ncubes = sum(len(b.get("cubes", [])) for b in bones)
        report.append(f"{label}: {len(bones)} bones, {ncubes} cubes, texture {tw}x{th} -> {tex.name}, JEM {src}")
        cells = []
        for view, vname in VIEWS:
            e, t = camera(faces, view)
            floor = min(0.0, min(q[1] for f in faces for q in f.pts))   # D-C293: a model hanging below its origin (the ghast's tentacles) stays visible
            img = render_entity(faces, tex, e, t, W, H, fov=FOV, floor_y=floor)
            cells.append(tile(img, f"{label.upper()} — {vname}", f"Patrix {src} JEM · {ncubes} cubes · rest pose"))
        row = Image.new("RGB", (len(cells) * (W + 4) - 4, H), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * (W + 4), 0))
        rows.append(row)
    out = Image.new("RGB", (rows[0].width, len(rows) * (H + 4) - 4), (255, 255, 255))
    for i, r in enumerate(rows): out.paste(r, (0, i * (H + 4)))
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"FA0-PREVIEW-{group}.png"; out.save(p)
    return p, report


if __name__ == "__main__":
    for g in sys.argv[1:] or list(GROUPS):
        p, rep = sheet(g)
        print(p); [print("  ", r) for r in rep]
