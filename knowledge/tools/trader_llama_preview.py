#!/usr/bin/env python3
"""trader_llama_preview.py — the trader llama as RP-07 1.4.18 draws it: main model (plain coat) + the blanket layer
(geometry.trader_llama_decor.patrix with textures/entity/llama/trader_llama.png) in ONE z-buffer (the two textures are packed
side by side into one atlas so the rasterizer can draw both layers together), next to what ships now (1.4.17). Floor = ground."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines, posed_faces
from entity_tex_render import render_entity
from face_alpha_census import jl

ROOT = Path("/home/claude"); NEW, OLD = ROOT / "_build/rp07-1418", ROOT / "_build/rp07-1417"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/user-data/outputs/trader-llama-blanket-layer.png")


def geo(root, fname):
    g = jl(root / "models/entity" / fname)["minecraft:geometry"][0]
    return g["bones"], g["description"]["texture_width"], g["description"]["texture_height"]


def atlas(a, b, tmp):
    A, Bm = Image.open(a).convert("RGBA"), Image.open(b).convert("RGBA").resize(Image.open(a).size, Image.NEAREST)
    out = Image.new("RGBA", (A.width * 2, A.height)); out.paste(A, (0, 0)); out.paste(Bm, (A.width, 0)); out.save(tmp); return tmp


def remap(faces, half):
    for f in faces:
        u0, v0, u1, v1 = f.uv; f.uv = (u0 / 2 + half, v0, u1 / 2 + half, v1)
    return faces


def main():
    tmp = "/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/tl_atlas.png"
    mb, mtw, mth = geo(NEW, "trader_llama.geo.json"); db, dtw, dth = geo(NEW, "trader_llama_decor.geo.json"); ob, otw, oth = geo(OLD, "trader_llama.geo.json")
    try: F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    except Exception: F = ImageFont.load_default()
    rows = []
    for coat in ("creamy", "brown"):
        at = atlas(NEW / f"textures/entity/llama/{coat}.png", NEW / "textures/entity/llama/trader_llama.png", tmp.replace(".png", f"_{coat}.png"))
        faces = remap(posed_faces(mb, mtw, mth, bone_affines(mb)), 0.0) + remap(posed_faces(db, dtw, dth, bone_affines(db)), 0.5)
        look = remap(posed_faces(mb, mtw, mth, bone_affines(mb, add_rot={"head": [0, 30, 0]})), 0.0) + remap(posed_faces(db, dtw, dth, bone_affines(db, add_rot={"head": [0, 30, 0]})), 0.5)
        old = posed_faces(ob, otw, oth, bone_affines(ob, abs_rot={"head": [0, 0, 0]}))
        cells = []; tgt = [0, 20, -2]
        for fs, tex, lab, col, d in ((old, OLD / f"textures/entity/llama/trader_llama_{coat}.png", f"SHIPPING 1.4.17 ({coat})", (130, 30, 30), (0.7, 0.55, 0.7)),
                                     (faces, at, f"1.4.18 blanket layer ({coat})", (30, 70, 140), (0.7, 0.55, 0.7)),
                                     (faces, at, "1.4.18 — from behind", (30, 70, 140), (-0.8, 0.5, -0.6)),
                                     (look, at, "1.4.18 — looking 30° left", (30, 110, 90), (0.7, 0.55, 0.7))):
            dv = np.array(d, float); dv /= np.linalg.norm(dv); eye = [tgt[0] + dv[0] * 60, tgt[1] + dv[1] * 60, tgt[2] + dv[2] * 60]
            im = render_entity(fs, str(tex), eye, tgt, 380, 300, fov=45, floor_y=0.0).convert("RGB"); dr = ImageDraw.Draw(im)
            dr.rectangle([0, 0, 380, 20], fill=col); dr.text((5, 3), lab, fill=(255, 255, 255), font=F); cells.append(im)
        row = Image.new("RGB", (4 * 384 - 4, 300), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * 384, 0))
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, 2 * 304 - 4), (255, 255, 255)); sheet.paste(rows[0], (0, 0)); sheet.paste(rows[1], (0, 304))
    sheet.save(OUT); print(OUT, sheet.size)


if __name__ == "__main__":
    main()
