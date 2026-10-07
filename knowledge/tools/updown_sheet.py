#!/usr/bin/env python3
"""updown_sheet.py — D-C278 check: every geometry whose up/down faces were turned, BEFORE (old pack) vs AFTER (new pack),
seen from above and from below (truth placement), one small tile each, with the entity's default texture."""
import json, sys, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from truth_compare import geometry, cam
from updown_census import lj
FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
W, H = 150, 120

def tex_for(ident, packs):
    for rp in packs:
        for f in (Path(rp) / "entity").glob("*.json"):
            try: d = lj(f)["minecraft:client_entity"]["description"]
            except Exception: continue
            if ident in (d.get("geometry") or {}).values():
                t = list((d.get("textures") or {}).values())
                for tt in t:
                    for base in packs:
                        for ext in (".png", ".tga"):
                            p = Path(base) / (tt + ext)
                            if p.exists(): return str(p)
    return None

def main(old, new, report, out, packs):
    rep = json.load(open(report)); cells = []
    for ident in sorted(rep):
        tex = tex_for(ident, packs)
        if not tex: continue
        row = []
        for root in (old, new):
            b, tw, th = geometry(root, ident); F = truth_posed_faces(b, tw, th, bone_affines(b))
            for v in ("top", "below"):
                e, t = cam(F, v, 1.2)
                row.append(render_entity(F, tex, e, t, W, H, fov=50.0).convert("RGB"))
        cells.append((ident.replace("geometry.", ""), row))
    cols = 2; cw = 4 * (W + 2) + 8
    sheet = Image.new("RGB", (cols * cw, math.ceil(len(cells) / cols) * (H + 14)), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    for i, (name, row) in enumerate(cells):
        x0 = (i % cols) * cw; y0 = (i // cols) * (H + 14)
        d.text((x0 + 2, y0), f"{name}: before top | before below | AFTER top | AFTER below", fill=(0, 0, 0), font=FR)
        for j, im in enumerate(row): sheet.paste(im, (x0 + j * (W + 2), y0 + 12))
    sheet.save(out); print(out, len(cells))

if __name__ == "__main__":
    a = sys.argv; main(a[1], a[2], a[3], a[4], a[5].split(","))
