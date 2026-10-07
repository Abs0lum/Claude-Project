#!/usr/bin/env python3
"""convb_after_sheet.py — what RP-07 1.4.16 ships vs what 1.4.15 shipped, for the Converter B READY set + donkey/mule.
Every tile has the checker FLOOR at y = 0 (the ground the mob stands on) — the 21:18 preview had none, which hid the
turtle (12 px) and axolotl (22 px) sitting under the ground (D-C273). Same camera for NEW and OLD in a row.
Columns: NEW side · NEW 3/4 · NEW 3/4 looking 30° to its left (the new look animation) · OLD 3/4 (1.4.15 as in game).
Outputs _docs/convb/after_1416_<n>.png."""
import sys, re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines, posed_faces
from entity_tex_render import render_entity, frame_camera
from face_alpha_census import resolve_texture
from convb_preview import JOBS, library, bind_info
import build_rp07_1416 as B

ROOT = Path("/home/claude"); OUT = ROOT / "_docs/convb"; OLD, NEW = ROOT / "_build/rp07-1415", ROOT / "_build/rp07-1416"
LOOK_STEMS = set(B.LOOK_ENTITIES)   # overridable for later rounds
NEW_V, OLD_V = "1.4.16", "1.4.15"
W, H = 360, 270
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14); FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    FT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
except Exception:
    FB = FR = FT = ImageFont.load_default()


def geo(root, ident):
    for q in sorted((root / "models/entity").glob("*.json")):
        d = B.jl(q)
        for g in d.get("minecraft:geometry", []):
            if g["description"]["identifier"] == ident: return g
    raise FileNotFoundError(ident)


def tile(img, title, sub, color):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 34], fill=color)
    d.text((6, 2), title, fill=(255, 255, 255), font=FB); d.text((6, 18), sub, fill=(225, 230, 240), font=FR)
    return img


def row_for(label, stem, gkey, hide=()):
    en = B.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
    eo = B.jl(OLD / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
    ident = en["geometry"][gkey]; gn, go = geo(NEW, ident), geo(OLD, ident)
    tk = gkey if gkey in en["textures"] else "default"
    tp = resolve_texture(en["textures"][tk])
    nb = [b for b in gn["bones"] if b["name"] not in hide]; ob = [b for b in go["bones"] if b["name"] not in hide]
    ntw, nth = gn["description"]["texture_width"], gn["description"]["texture_height"]
    otw, oth = go["description"]["texture_width"], go["description"]["texture_height"]
    anims, rcs = library(OLD); _, rel, _ = bind_info(eo, anims, rcs)
    oldnames = {b["name"] for b in ob}
    of = posed_faces(ob, otw, oth, bone_affines(ob, abs_rot={n: [0, 0, 0] for n in rel if n in oldnames}))
    nf = posed_faces(nb, ntw, nth, bone_affines(nb))
    has_head = any(b["name"] == "head" for b in nb) and stem in LOOK_STEMS
    lf = posed_faces(nb, ntw, nth, bone_affines(nb, add_rot={"head": [0, 30, 0]})) if has_head else None
    P = np.array([p for f in nf for p in f.pts]); lo, hi = P.min(0), P.max(0)
    cells = []
    for v, faces, title, col, sub in (("east", nf, f"NEW {NEW_V} — side", (30, 70, 140), f"box y {lo[1]:.1f}..{hi[1]:.1f} px"),
                                      ("front-east", nf, f"NEW {NEW_V} — 3/4", (30, 70, 140), "floor = ground (y 0)"),
                                      ("front-east", lf, "NEW — looking 30° left", (30, 110, 90), "animation.pw_convb.look" if lf else "no look animation"),
                                      ("front-east", of, f"OLD {OLD_V} — 3/4", (130, 30, 30), "what shipped before")):
        e, t = frame_camera(nf + of, v)
        img = render_entity(faces, tp, e, t, W, H, fov=55, floor_y=0.0) if faces else Image.new("RGB", (W, H), (214, 224, 236))
        cells.append(tile(img, f"{label.upper()} · {title}", sub, col))
    row = Image.new("RGB", (4 * (W + 4) - 4, H), (255, 255, 255))
    for i, c in enumerate(cells): row.paste(c, (i * (W + 4), 0))
    return row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, stem, gkey, jname, tkey in JOBS:
        if label in B.READY: rows.append(row_for(label, stem, gkey)); print("row", label)
    for mob in ("donkey", "mule"):   # no chest equipped: the render controller hides left_chest / right_chest
        rows.append(row_for(f"{mob} (no chest)", mob, "default", hide=("left_chest", "right_chest"))); print("row", mob)
    head = Image.new("RGB", (rows[0].width, 44), (20, 24, 32))
    ImageDraw.Draw(head).text((10, 10), "RP-07 1.4.16 — Converter B round 2 (blue = new, green = new looking left, red = 1.4.15) · floor = ground · 2026-09-28",
                              fill=(255, 255, 255), font=FT)
    for part in range(0, len(rows), 6):
        chunk = rows[part:part + 6]
        sheet = Image.new("RGB", (rows[0].width, 44 + sum(r.height + 6 for r in chunk)), (255, 255, 255)); sheet.paste(head, (0, 0)); y = 50
        for r in chunk: sheet.paste(r, (0, y)); y += r.height + 6
        sheet.save(OUT / f"after_1416_{part // 6 + 1}.png"); print("sheet", part // 6 + 1)


if __name__ == "__main__":
    main()
