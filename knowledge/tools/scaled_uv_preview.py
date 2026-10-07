#!/usr/bin/env python3
"""scaled_uv_preview.py — D-C284: render a Converter B bake BEFORE (box UV kept on scaled boxes) and AFTER (per-face UV frozen
from the unscaled box) with the same cameras (bb_truth placement, alpha-test at 0.5 like the game's cutout materials).
usage: scaled_uv_preview.py <jem_stem> <texture_png> <out_png> <view>[,<view>...] [zoom]"""
import importlib.util, sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
import convb
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from truth_compare import cam, W, H, FB

OLD = Path("/home/claude/_backup_tools/convb.py.pre_dc284")


def old_convb():
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("convb_pre_dc284", str(OLD))
    spec = importlib.util.spec_from_loader("convb_pre_dc284", loader)
    m = importlib.util.module_from_spec(spec); loader.exec_module(m); return m


def faces(mod, stem):
    bones, tw, th, info = mod.bake(stem)
    return truth_posed_faces(bones, tw, th, bone_affines(bones)), info


def main(stem, tex, out, views, zoom=1.0):
    fa, _ = faces(old_convb(), stem)
    fb, info = faces(convb, stem)
    cells = []
    for view in views:
        e, t = cam(fb, view, zoom)
        for lab, fs, col in (("BEFORE (box UV on scaled boxes)", fa, (130, 30, 30)), ("AFTER (per-face UV frozen)", fb, (30, 70, 140))):
            im = render_entity(fs, tex, e, t, W, H, fov=50.0, floor_y=None).convert("RGB")
            d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 18], fill=col); d.text((4, 2), f"{lab} — {view}", fill=(255, 255, 255), font=FB)
            cells.append(im)
    sheet = Image.new("RGB", (2 * (W + 4), len(views) * (H + 4)), (255, 255, 255))
    for i, c in enumerate(cells): sheet.paste(c, ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    sheet.save(out); print(out, "per-face from scale:", len(info.get("perface_from_scale", [])), "bones")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], a[4].split(","), float(a[5]) if len(a) > 5 else 1.0)
