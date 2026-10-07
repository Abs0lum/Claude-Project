#!/usr/bin/env python3
"""std_preview.py — Phase 2 preview sheet: for each mob, the ORIGINAL (textured), the STANDARDIZED (textured — must look
the same), the standardized rig with one solid colour per wing piece, and a DEMO BEND (the new elbow / wrist / primary
joints turned a few degrees) that shows the new articulation exists. The demo bend is not an animation — the standard
flight animation comes in Phase 3 / 4.
Usage: std_preview.py OUT.png mob_id [mob_id …]"""
import copy
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
from bb_truth import truth_posed_faces  # noqa: E402
from convb_preview3 import camera, FOV  # noqa: E402
from entity_tex_render import render_entity  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

COLOURS = {"wing_inner": (220, 40, 40), "primary_l_1": (40, 160, 40), "primary_r_1": (40, 160, 40),
           "primary_l_2": (40, 80, 230), "primary_r_2": (40, 80, 230), "primary_l_3": (235, 200, 30),
           "primary_r_3": (235, 200, 30)}
BEND = {"elbow": (0, 0, 18), "wrist": (0, 0, 14), "primary_base": (0, 0, 10)}
W_, H_ = 260, 230
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)


def texture_of(P, desc):
    rel = (desc.get("textures") or {}).get("default") or next(iter((desc.get("textures") or {}).values()))
    for base in (P.path, S.VANILLA):
        for ext in (".png", ".tga"):
            if (base / (rel + ext)).exists():
                return base / (rel + ext)
    raise FileNotFoundError(rel)


def colour_texture(bones, tmp):
    """one texel per bone; every cube's faces point at its bone's texel."""
    bones = copy.deepcopy(bones)
    tex = np.zeros((1, len(bones), 4), np.uint8)
    for k, b in enumerate(bones):
        c = next((v for key, v in COLOURS.items() if b["name"].startswith(key) or b["name"] == key), (150, 150, 150))
        tex[0, k] = (*c, 255)
        for cube in b.get("cubes") or []:
            cube["uv"] = {f: {"uv": [k, 0], "uv_size": [1, 1]} for f in ("north", "south", "east", "west", "up", "down")}
            cube.pop("mirror", None)
    Image.fromarray(tex, "RGBA").save(tmp)
    return bones, len(bones), 1


def render(bones, tw, th, tex, view, label):
    f = truth_posed_faces(bones, tw, th, bone_affines(bones))
    e, t = camera(f, view)
    fl = min(0.0, min(q[1] for x in f for q in x.pts))
    im = render_entity(f, tex, e, t, W_, H_, fov=FOV, floor_y=fl).convert("RGB")
    ImageDraw.Draw(im).text((4, 4), label, fill=(0, 0, 0), font=F)
    return im


def main(out, ids):
    rows = []
    tmp = ROOT / "_staging/std_preview_tex.png"
    for mob in ids:
        census = next(c for c in json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text()) if c["id"] == mob)
        P = S.Pack(ROOT / "_build" / census["rp"].replace("rp07-1438", "rp07-1439").replace("rp06-1424", "rp06-1425"))
        ef, desc = P.entities[mob]
        slug = S.slug_of(mob)
        st = S.STAGE / P.path.name
        nd = S.jload(st / f"entity/std/{slug}.entity.json")["minecraft:client_entity"]["description"]
        new_geos = {g["description"]["identifier"]: g for g in S.jload(st / f"models/entity/std/{slug}.geo.json")["minecraft:geometry"]}
        g_old = P.geos[desc["geometry"]["default"] if "default" in desc["geometry"] else next(iter(desc["geometry"].values()))]
        g_new = new_geos[nd["geometry"]["default"] if "default" in nd["geometry"] else next(iter(nd["geometry"].values()))]
        tw, th = g_old["description"].get("texture_width", 64), g_old["description"].get("texture_height", 64)
        tex = texture_of(P, desc)
        bent = copy.deepcopy(g_new["bones"])
        for b in bent:
            for key, rot in BEND.items():
                if b["name"].startswith(key):
                    sign = 1 if b["name"].endswith("_l") or "_l_" in b["name"] else -1
                    b["rotation"] = [b.get("rotation", [0, 0, 0])[i] + sign * rot[i] for i in range(3)]
        cb, ctw, cth = colour_texture(g_new["bones"], tmp)
        cbent, _, _ = colour_texture(bent, tmp)
        tiles = [render(g_old["bones"], tw, th, tex, "front-east", f"{mob} - ORIGINAL"),
                 render(g_new["bones"], tw, th, tex, "front-east", "STANDARD (same look)"),
                 render(cb, ctw, cth, tmp, "top", "pieces (top view)"),
                 render(cbent, ctw, cth, tmp, "front", "DEMO bend of the new joints")]
        row = Image.new("RGB", (4 * (W_ + 4), H_), (255, 255, 255))
        for i, im in enumerate(tiles):
            row.paste(im, (i * (W_ + 4), 0))
        rows.append(row)
    legend = Image.new("RGB", (rows[0].width, 22), (255, 255, 255))
    d = ImageDraw.Draw(legend)
    x = 4
    for lab, c in (("inner wing", (220, 40, 40)), ("primary 1", (40, 160, 40)), ("primary 2", (40, 80, 230)),
                   ("primary 3", (235, 200, 30)), ("rest of the body", (150, 150, 150))):
        d.rectangle([x, 5, x + 12, 17], fill=c)
        d.text((x + 16, 5), lab, fill=(0, 0, 0), font=F)
        x += 150
    img = Image.new("RGB", (rows[0].width, 22 + len(rows) * (H_ + 4)), (255, 255, 255))
    img.paste(legend, (0, 0))
    for i, r in enumerate(rows):
        img.paste(r, (0, 22 + i * (H_ + 4)))
    img.save(out)
    print(out, img.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
