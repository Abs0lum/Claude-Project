#!/usr/bin/env python3
"""convb_preview2.py — Phase B preview (his 09-28 21:43 GO): the Converter B build path used for 1.4.16 (convb_build: bake +
bind + leg pivots + frame bones) for the mobs still failing, NEW vs what ships now (OLD, from the latest build dir), with a
floor at y 0 in every tile (D-C273 lesson). Per mob one row: NEW east · NEW west · NEW front-east · NEW back · OLD east · OLD
front-east. Usage: convb_preview2.py [label ...]  -> _docs/convb/p2_<stem>_<gkey>.png (+ _docs/convb/p2_report.json)"""
import json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from convb_build import build_mob
from convb_preview import JOBS, library, bind_info, holes, floating
from equine_compare import bone_affines, posed_faces
from entity_tex_render import render_entity, frame_camera
from face_alpha_census import all_geometries, resolve_texture, jl

ROOT = Path("/home/claude"); OUT = ROOT / "_docs/convb"
PACKS = [("RP-07", ROOT / "_build/rp07-1418"), ("RP-06", ROOT / "_build/rp06-1411")]
W, H = 330, 250
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13); FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception:
    FB = FR = ImageFont.load_default()
EXTRA_JOBS = [("trader llama", "trader_llama", "default", "trader_llama", "default"), ("ravager", "ravager", "default", "ravager", "default")]


def entity(stem):
    for tag, rp in PACKS:
        f = rp / f"entity/{stem}.entity.json"
        if f.exists(): return tag, rp, jl(f)["minecraft:client_entity"]["description"]
    raise FileNotFoundError(stem)


def geo(rp, ident):
    for q in sorted((rp / "models/entity").glob("*.json")):
        d = jl(q)
        if not d: continue
        for g in d.get("minecraft:geometry", []):
            if g["description"]["identifier"] == ident: return g["bones"], g["description"]["texture_width"], g["description"]["texture_height"]
    G = all_geometries(); _, b, tw, th = G[ident]; return b, tw, th


def tile(img, title, sub, color):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 32], fill=color)
    d.text((5, 2), title, fill=(255, 255, 255), font=FB); d.text((5, 17), sub, fill=(225, 230, 240), font=FR)
    return img


def preview(label, stem, gkey, jname, tkey, hide=(), out_name=None):
    tag, rp, desc = entity(stem); anims, rcs = library(rp)
    ident = desc["geometry"][gkey]; old, otw, oth = geo(rp, ident)
    tp = resolve_texture(desc["textures"][tkey])
    names, rel, _ = bind_info(desc, anims, rcs)
    new, ntw, nth, info = build_mob(jname, stem, names, old, look_bones=["head"] if rel else [])
    new = [b for b in new if b["name"] not in hide]
    oldn = {b["name"] for b in old}
    of = posed_faces(old, otw, oth, bone_affines(old, abs_rot={n: [0, 0, 0] for n in rel if n in oldn}))
    nf = posed_faces(new, ntw, nth, bone_affines(new))
    P = np.array([p for f in nf for p in f.pts]); lo, hi = P.min(0), P.max(0)
    h_new, h_old = holes(new, ntw, nth, tp), holes(old, otw, oth, tp)
    fl_new, fl_old = floating(new), floating(old)
    cells = []
    for v, faces, t, col in (("east", nf, "NEW side (E)", (30, 70, 140)), ("west", nf, "NEW side (W)", (30, 70, 140)),
                             ("front-east", nf, "NEW 3/4 front", (30, 70, 140)), ("back", nf, "NEW back", (30, 70, 140)),
                             ("east", of, "OLD side (E)", (130, 30, 30)), ("front-east", of, "OLD 3/4 front", (130, 30, 30))):
        e, tg = frame_camera(nf + of, v)
        sub = (f"holes {h_new:.0f}% · floating {len(fl_new)} · y {lo[1]:.1f}..{hi[1]:.1f}" if faces is nf else f"holes {h_old:.0f}% · floating {len(fl_old)}")
        cells.append(tile(render_entity(faces, tp, e, tg, W, H, fov=55, floor_y=0.0), f"{label.upper()} — {t}", sub, col))
    row = Image.new("RGB", (6 * (W + 4) - 4, H), (255, 255, 255))
    for i, c in enumerate(cells): row.paste(c, (i * (W + 4), 0))
    name = out_name or f"p2_{stem}_{gkey}.png"; row.save(OUT / name)
    r = {"pack": tag, "geometry": ident, "texture": str(tp), "tex_geo_old": [otw, oth], "tex_jem": [ntw, nth], "holes_old": round(h_old, 1), "holes_new": round(h_new, 1),
         "floating_old": fl_old, "floating_new": fl_new, "unbound": info["missing"], "mapping": {k: v for k, v in info["mapping"].items() if k != v},
         "frames": sorted(info["frames"]), "pivot_shift": info["pivot_shift"], "hidden_at_rest": info["hidden_at_rest"], "extent": [lo.round(2).tolist(), hi.round(2).tolist()]}
    print(label, json.dumps(r)); return r, row


def main():
    only = set(sys.argv[1:]); rep = {}
    for job in JOBS + EXTRA_JOBS:
        if only and job[0] not in only and job[1] not in only: continue
        rep[job[0]], _ = preview(*job)
    old = json.load(open(OUT / "p2_report.json")) if (OUT / "p2_report.json").exists() else {}
    old.update(rep); json.dump(old, open(OUT / "p2_report.json", "w"), indent=1)


if __name__ == "__main__":
    main()
