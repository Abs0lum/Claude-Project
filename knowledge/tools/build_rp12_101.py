#!/usr/bin/env python3
"""build_rp12_101.py — RP-12 Gallery 1.0.1 (full + LITE) from 1.0.0: PAINTINGS FACE THE ROOM, FLUSH TO THE WALL (his 16:50).

Mechanism (10-05 17:0x): the frame bones were authored as if the model's axes were the world's, but Bedrock draws an
entity model turned 180 degrees at yaw 0. Bone n (file z 7..8, art on its 'north' face) therefore landed on the ROOM side
of the cell (world z -0.5..-0.4375) with its art pointing into the wall: the back faced the room and a 0.94-block gap
stood behind it. Every facing had the same 180-degree error, so the fix shows the OPPOSITE bone for each facing:
facing 0 -> s, 1 -> w, 2 -> n, 3 -> e (that bone sits on the wall side; its art face points into the room; a pure rotation
keeps the picture unmirrored). Persistent paintings keep their pw:facing, so pictures already hanging are fixed by this
pack alone. Also: the Curator's Wand and the Framed Painting item icons + names (BP-02 1.3.224).
Usage: python3 tools/build_rp12_101.py   (rp12-101 / rp12-101-lite must not exist)"""
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

B = Path("/home/claude/_build")
JOBS = [(B / "rp12-100", B / "rp12-101", False), (B / "rp12-100-lite", B / "rp12-101-lite", True)]
VERSION = [1, 0, 1]
RENDER = {"format_version": "1.10.0", "render_controllers": {"controller.render.pw_art": {
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"],
    "part_visibility": [{"*": False}, {"s": "query.property('pw:facing') == 0"}, {"w": "query.property('pw:facing') == 1"},
                        {"n": "query.property('pw:facing') == 2"}, {"e": "query.property('pw:facing') == 3"}]}}}


def wand_icon():
    """a dark walnut rod with a gilt hook-and-ring head (32 x 32, original)"""
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(18):                                   # the rod, lower-left to the head
        x, y = 5 + k, 26 - k
        d.rectangle([x, y, x + 1, y + 1], fill=(92, 58, 33, 255))
        d.point((x + 1, y), fill=(128, 84, 50, 255))
    d.ellipse([20, 3, 29, 12], outline=(214, 170, 60, 255), width=2)          # the gilt ring
    d.point((24, 7), fill=(255, 226, 130, 255))
    d.rectangle([4, 25, 7, 28], fill=(214, 170, 60, 255))                     # the ferrule
    return im


def framed_icon():
    """a small gilt frame holding a dusk landscape (32 x 32, original)"""
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([3, 6, 28, 25], fill=(190, 145, 52, 255))
    d.rectangle([4, 7, 27, 24], fill=(150, 108, 34, 255))
    d.rectangle([6, 9, 25, 22], fill=(120, 150, 190, 255))                   # sky
    d.rectangle([6, 17, 25, 22], fill=(70, 98, 52, 255))                     # land
    d.polygon([(6, 18), (12, 13), (17, 18)], fill=(96, 110, 120, 255))       # a hill
    d.ellipse([19, 10, 22, 13], fill=(250, 215, 120, 255))                   # the sun
    return im


def main():
    for src, dst, lite in JOBS:
        if dst.exists():
            raise SystemExit(f"never rebuild {dst}")
        shutil.copytree(src, dst)
        (dst / "render_controllers/pw_art.render.json").write_text(json.dumps(RENDER, indent=1))
        wand_icon().save(dst / "textures/items/pw_curators_wand.png")
        framed_icon().save(dst / "textures/items/pw_framed_painting.png")
        itp = dst / "textures/item_texture.json"
        it = json.loads(itp.read_text())
        it["texture_data"]["pw_curators_wand"] = {"textures": "textures/items/pw_curators_wand"}
        it["texture_data"]["pw_framed_painting"] = {"textures": "textures/items/pw_framed_painting"}
        itp.write_text(json.dumps(it, indent=1))
        lang = dst / "texts/en_US.lang"
        lang.write_text(lang.read_text().rstrip("\n") + "\nitem.pw:curators_wand.name=Curator's Wand\nitem.pw:framed_painting.name=Framed Painting\naction.interact.pw_talk=Talk\n")
        mp = dst / "manifest.json"
        m = json.loads(mp.read_text())
        m["header"]["version"] = VERSION
        m["header"]["name"] = f"RP-12 AbsolutRealism Gallery{' LITE' if lite else ''} v1.0.1"
        m["header"]["description"] = ("v1.0.1 (2026-10-05) PAINTINGS FACE THE ROOM, FLUSH TO THE WALL (1.0.0 drew every frame turned around, "
                                      "a block off the wall); the Curator's Wand and the Framed Painting. " + m["header"]["description"].split(": ", 1)[-1])
        for mod in m["modules"]:
            mod["version"] = VERSION
        mp.write_text(json.dumps(m, indent=1))
        rc = json.loads((dst / "render_controllers/pw_art.render.json").read_text())
        vis = rc["render_controllers"]["controller.render.pw_art"]["part_visibility"]
        assert [list(v)[0] for v in vis] == ["*", "s", "w", "n", "e"], vis
        print(f"DONE {dst}")


if __name__ == "__main__":
    main()
