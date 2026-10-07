#!/usr/bin/env python3
"""parts_compare.py — his FAIL parts? mobs (09-28): the Patrix model (JEM + FreshLX rest pose, CONV-1, textured with the SAME
texture file our entity binds) next to OUR shipped geometry, from the same cameras, plus a per-mob count of faces whose UV
lands on transparent texels (= holes: "missing parts of the texture").

Usage: python3 tools/parts_compare.py [mob ...]   -> _docs/parts/<mob>_parts.png + _docs/parts/parts_sheet.png
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines, posed_faces
from face_alpha_census import all_geometries, resolve_texture, jl, RPS, face_rects, opaque_fraction
from entity_tex_render import render_entity, frame_camera
from jem_convert import bake_rest2, to_bedrock, load_json as jload

ROOT = Path("/home/claude"); CEM = ROOT / "_intake/patrix-mobs/assets/minecraft/optifine/cem"; OUT = ROOT / "_docs/parts"
# mob -> (entity file stem, JEM name, vanilla-template key)
MOBS = {"turtle": ("turtle", "turtle", "turtle"), "salmon": ("salmon", "salmon", "salmon"), "axolotl": ("axolotl", "axolotl", "axolotl"),
        "rabbit": ("rabbit", "rabbit", "rabbit"), "chicken": ("chicken", "chicken", "chicken"), "frog": ("frog", "frog", "frog"),
        "squid": ("squid", "squid", "squid"), "glow_squid": ("glow_squid", "glow_squid", "glow_squid"), "pillager": ("pillager", "pillager", "pillager"),
        "ravager": ("ravager", "ravager", "ravager"), "skeleton_horse": ("skeleton_horse", "skeleton_horse", "skeleton_horse")}
W, H = 420, 315
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15); FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except Exception:
    FB = FR = ImageFont.load_default()
GEOS = None


def entity(stem):
    for tag, rp in RPS:
        f = rp / f"entity/{stem}.entity.json"
        if f.exists():
            return tag, jl(f)["minecraft:client_entity"]["description"]
    raise FileNotFoundError(stem)


def ours(stem):
    global GEOS
    GEOS = GEOS or all_geometries()
    tag, desc = entity(stem)
    gid = desc["geometry"]["default"]; tp = resolve_texture(desc["textures"]["default"])
    f, bones, tw, th = GEOS[gid]
    return tag, gid, bones, tw, th, tp


def patrix(jname, tkey):
    jem = jload(CEM / f"{jname}.jem")
    bb, ctx, err = bake_rest2(jem, tkey)
    tw, th = jem.get("textureSize") or [64, 32]
    return to_bedrock(bb), tw, th, err


def holes(bones, tw, th, tp):
    alpha = np.asarray(Image.open(tp).convert("RGBA"))[..., 3]
    n = area = 0.0; tot = 0.0
    for b in bones:
        for c in b.get("cubes", []):
            s = c["size"]
            for name, rect in face_rects(c, b.get("mirror", False)).items():
                dims = {"north": (s[0], s[1]), "south": (s[0], s[1]), "east": (s[2], s[1]), "west": (s[2], s[1]), "up": (s[0], s[2]), "down": (s[0], s[2])}[name]
                a = dims[0] * dims[1]
                if a < 2.0 or min(s) < 0.05: continue          # skip slivers and alpha-card planes (fins, fronds: transparent by design)
                op, off = opaque_fraction(alpha, rect, tw, th)
                tot += a
                if op < 0.5 or off: n += 1; area += a
    return int(n), (area / tot * 100 if tot else 0)


def tile(img, title, sub, color):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 38], fill=color)
    d.text((6, 2), title, fill=(255, 255, 255), font=FB); d.text((6, 20), sub, fill=(220, 226, 236), font=FR)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for mob in (sys.argv[1:] or MOBS):
        stem, jname, tkey = MOBS[mob]
        tag, gid, ob, otw, oth, tp = ours(stem)
        try:
            pb, ptw, pth, err = patrix(jname, tkey)
        except Exception as e:
            print(mob, "JEM failed:", e); continue
        pf = posed_faces(pb, ptw, pth, bone_affines(pb)); of = posed_faces(ob, otw, oth, bone_affines(ob))
        hp = holes(pb, ptw, pth, tp); ho = holes(ob, otw, oth, tp)
        cells = []
        for v in ("front-east", "west", "back"):
            e, t = frame_camera(pf + of, v)
            cells.append(tile(render_entity(pf, tp, e, t, W, H, fov=55, floor_y=None), f"{mob.upper()} PATRIX — {v}", f"hole faces {hp[0]} ({hp[1]:.0f}% of box area)", (22, 90, 52)))
            cells.append(tile(render_entity(of, tp, e, t, W, H, fov=55, floor_y=None), f"{mob.upper()} OURS ({tag}) — {v}", f"hole faces {ho[0]} ({ho[1]:.0f}% of box area)", (130, 30, 30)))
        row = Image.new("RGB", (len(cells) * (W + 4) - 4, H), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * (W + 4), 0))
        row.save(OUT / f"{mob}_parts.png"); rows.append(row)
        print(f"{mob:14s} {tag} {gid:32s} texture {tp.relative_to(ROOT)}  holes: PATRIX {hp[0]} faces {hp[1]:.0f}%  OURS {ho[0]} faces {ho[1]:.0f}%  bake-errors {len(err)}")
    if rows:
        sheet = Image.new("RGB", (max(r.width for r in rows), sum(r.height + 6 for r in rows)), (255, 255, 255)); y = 0
        for r in rows: sheet.paste(r, (0, y)); y += r.height + 6
        sheet.save(OUT / "parts_sheet.png")


if __name__ == "__main__":
    main()
