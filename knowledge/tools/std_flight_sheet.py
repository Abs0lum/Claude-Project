#!/usr/bin/env python3
"""std_flight_sheet.py — preview sheet for the standard flight v2 (textured, the bird's own skin):
  REST (v.std_u = 0, side view) · UNFOLD half-way (u = 0.5) · FLIGHT wings up · FLIGHT wings down · FLIGHT side view
Usage: std_flight_sheet.py OUT.png [--colour] mob_id [mob_id …]   (--colour: one solid colour per wing piece)"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
import std_flight as FL  # noqa: E402
import std_preview as SP  # noqa: E402


def frames(T):
    # flap phase p = 360 (t + r) / T; wing tip up at p = 90, down at p = 270
    return [("REST (on the ground)", {"q.life_time": 0.0, "v.std_u": 0.0}, "front-east"),
            ("UNFOLD half-way", {"q.life_time": 0.0, "v.std_u": 0.5}, "front-east"),
            ("FLIGHT wings up", {"q.life_time": T * 0.25, "v.std_u": 1.0}, "front"),
            ("FLIGHT wings down", {"q.life_time": T * 0.75, "v.std_u": 1.0}, "front"),
            ("FLIGHT side", {"q.life_time": T * 0.25, "v.std_u": 1.0}, "east"),
            ("FLIGHT 3/4", {"q.life_time": T * 0.5, "v.std_u": 1.0}, "front-east")]


def row(mob, colour=False):
    census = next(c for c in json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text()) if c["id"] == mob)
    rp = census["rp"].replace("rp07-1438", "rp07-1439").replace("rp06-1424", "rp06-1425")
    P = S.Pack(ROOT / "_build" / rp)
    ef, desc = P.entities[mob]
    slug = S.slug_of(mob)
    st = S.STAGE / rp
    g = S.jload(st / f"models/entity/std/{slug}.geo.json")["minecraft:geometry"][0]
    anims = S.jload(st / f"animations/std/{slug}.animation.json")["animations"]
    an = (anims.get(f"animation.std.{slug}.flight") or anims[f"animation.std.{slug}.flutter"])["bones"]
    rate = [c for c in an.get(f"shoulder_fly_l", an.get("shoulder_fly_r", {})).get("rotation", [""])
            if "q.life_time" in c]
    import re
    m = re.search(r"\* ([0-9.]+)\)", rate[0]) if rate else None
    T = 360.0 / float(m.group(1)) if m else 0.35
    tw, th = g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)
    tex = SP.texture_of(P, desc)
    tiles = []
    for label, env, view in frames(T):
        b = FL.preview_pose(g["bones"], an, {"v.std_r": 0.0, "v.std_air": 0.5, **env})
        if colour:
            tmp = ROOT / "_staging/std_flight_sheet_tex.png"
            cb, ctw, cth = SP.colour_texture(b, tmp)
            tiles.append(SP.render(cb, ctw, cth, tmp, view, f"{mob} · {label}" if not tiles else label))
        else:
            tiles.append(SP.render(b, tw, th, tex, view, f"{mob} · {label}" if not tiles else label))
    r = Image.new("RGB", (len(tiles) * (SP.W_ + 4), SP.H_), (255, 255, 255))
    for i, im in enumerate(tiles):
        r.paste(im, (i * (SP.W_ + 4), 0))
    return r


def main(out, ids, colour=False):
    rows = [row(m, colour) for m in ids]
    img = Image.new("RGB", (rows[0].width, len(rows) * (SP.H_ + 4)), (255, 255, 255))
    for i, r in enumerate(rows):
        img.paste(r, (0, i * (SP.H_ + 4)))
    img.save(out)
    print(out, img.size)


if __name__ == "__main__":
    args = sys.argv[1:]
    colour = "--colour" in args
    args = [a for a in args if a != "--colour"]
    main(args[0], args[1:], colour)
