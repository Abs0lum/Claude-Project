#!/usr/bin/env python3
"""ref_rig_sheet.py — render reference rigs from a build dir; geometry searched recursively under models/entity,
texture resolved with .png/.tga. Usage: ref_rig_sheet.py <build_dir> <out.png> <geometry_id>=<texture path w/o ext ok> [...]"""
import sys, json
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import pack_geo_preview as P


def geo_file(dst, ident):
    for p in sorted((dst / "models/entity").rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        for g in d.get("minecraft:geometry", []):
            if g.get("description", {}).get("identifier") == ident:
                return p, g
        for k, g in d.items():  # legacy 1.8 / 1.10 format: "geometry.x[:parent]": {...}
            if k.split(":")[0] == ident and isinstance(g, dict):
                return p, {"description": {"identifier": ident,
                                           "texture_width": g.get("texturewidth", 64),
                                           "texture_height": g.get("textureheight", 64)},
                           "bones": g.get("bones", [])}
    raise FileNotFoundError(ident)


R.geo_file = geo_file


def tex(dst, t):
    for c in (t, t + ".png", t + ".tga"):
        if (dst / c).exists():
            return c
    raise FileNotFoundError(t)


if __name__ == "__main__":
    dst = Path(sys.argv[1])
    pairs = []
    for a in sys.argv[3:]:
        g, t = a.split("=", 1)
        pairs.append((g, tex(dst, t)))
    print(P.sheet(dst, sys.argv[2], pairs, views=("front-east", "east", "top")))
