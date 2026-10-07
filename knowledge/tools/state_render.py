#!/usr/bin/env python3
"""state_render.py — D-C291 (his 19:58 "the black bear and the grizzly bear look like they're having UV mapping issues"):
render a client entity the way the game draws it in its EVERYDAY state — render-controller part_visibility evaluated with every
query false / 0 (awake, not angry, not sheared, not tamed, not eating, adult) — instead of the size tools' rule of dropping every
conditional part. Three close cameras. usage: state_render.py <identifier> [...] -> _docs/sizes/STATE-<name>.png"""
import re, sys, fnmatch
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import visible_size as V, roster_size_census as R, size_law_lineup as L
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV

W, H = 360, 300
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)


def hidden_bones(desc, roots):
    return V.everyday_rules(desc, roots)


def render(ident):
    p, pack, desc = L.find_entity(ident)
    roots = [pack] + [q for q in R.PACKS if q != pack] + [V.VANILLA]
    bones, tw, th = V.find_geometry(roots, desc["geometry"]["default"])
    tp = V.find_texture(roots, (desc.get("textures") or {}).get("default"))
    rules = hidden_bones(desc, roots)
    def vis(n):
        v = True
        for pat, hid in rules:
            if fnmatch.fnmatch(n.lower(), pat): v = not hid
        return v
    par = {b["name"]: b.get("parent") for b in bones}
    def shown(n):
        while n:
            if not vis(n): return False
            n = par.get(n)
        return True
    faces = [f for f in truth_posed_faces(bones, tw, th, bone_affines(bones)) if shown(f.bone)]
    cells = []
    for view in ("front-east", "east", "back-east"):
        e, t = camera(faces, view, pad=1.1)
        im = render_entity(faces, str(tp), e, t, W, H, fov=FOV, floor_y=0.0).convert("RGB")
        d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 20], fill=(30, 70, 140)); d.text((5, 3), f"{ident} — {view} — everyday state", fill="white", font=FB)
        cells.append(im)
    out = Image.new("RGB", (3 * (W + 4) - 4, H), "white")
    for i, c in enumerate(cells): out.paste(c, (i * (W + 4), 0))
    o = Path(f"/home/claude/_docs/sizes/STATE-{ident.split(':')[1]}.png"); out.save(o)
    return o, tp, [b for b in {f.bone for f in faces}]


if __name__ == "__main__":
    for a in sys.argv[1:]:
        o, tp, b = render(a); print(o, tp, sorted(b))
