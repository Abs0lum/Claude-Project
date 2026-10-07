#!/usr/bin/env python3
"""warden_uv_compare.py — R12 z08 'UV mapping error' (his FAIL note), mechanism sheet.
Row A  WHAT THE GAME DRAWS: Mojang geometry.warden (bedrock-samples 1.26.50, box UVs) + OUR RP-06 warden.png
       (= Patrix 1.21.11 128x warden.png, pixel-identical, 1024x1024).
Row B  WHAT THAT TEXTURE WAS PAINTED FOR: the Patrix warden.jem (same file in every Patrix version we hold) + the same texture.
Row C  VANILLA REFERENCE: Mojang geometry.warden + Mojang's own 128x128 warden.png.
Also prints the per-part UV table (vanilla box UV vs Patrix per-face UV) for the numbers.
Output: _docs/sizes/WARDEN-UV-COMPARE.png"""
import json, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import convb
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV

ROOT = Path("/home/claude")
GEO = ROOT / "_intake/bedrock-samples/resource_pack/models/entity/warden.geo.json"
OURS = ROOT / "_build/rp06-1419/textures/entity/warden/warden.png"
VAN = ROOT / "_intake/bedrock-samples/resource_pack/textures/entity/warden/warden.png"
OUT = ROOT / "_docs/sizes/WARDEN-UV-COMPARE.png"
W, H = 330, 300
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception:
    FB = FR = ImageFont.load_default()


def vanilla_bones():
    t = re.sub(r"//.*", "", GEO.read_text(encoding="utf-8"))
    g = next(x for x in json.loads(t)["minecraft:geometry"] if x["description"]["identifier"] == "geometry.warden")
    return g["bones"], g["description"]["texture_width"], g["description"]["texture_height"]


def faces_of(bones, tw, th):
    return truth_posed_faces(bones, tw, th, bone_affines(bones))


def tile(img, title, sub, color):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 32], fill=color)
    d.text((5, 2), title, fill=(255, 255, 255), font=FB); d.text((5, 17), sub, fill=(225, 230, 240), font=FR)
    return img


def main():
    vb, vtw, vth = vanilla_bones()
    pb, ptw, pth, info = convb.bake("warden")
    rows = [("A  IN GAME NOW", "Mojang geometry + our Patrix texture", faces_of(vb, vtw, vth), OURS, (170, 40, 40)),
            ("B  PAINTED FOR", "Patrix warden.jem + the same texture", faces_of(pb, ptw, pth), OURS, (30, 110, 60)),
            ("C  VANILLA", "Mojang geometry + Mojang 128px texture", faces_of(vb, vtw, vth), VAN, (60, 60, 60))]
    views = [("front", "front (you facing NORTH, he faces SOUTH)"), ("front-east", "front-east"), ("east", "side (east)")]
    out = Image.new("RGB", (len(views) * (W + 4) - 4, len(rows) * (H + 4) - 4), (255, 255, 255))
    for r, (tag, sub, faces, tex, col) in enumerate(rows):
        for c, (view, vname) in enumerate(views):
            e, t = camera(faces, view)
            floor = min(0.0, min(q[1] for f in faces for q in f.pts))
            img = render_entity(faces, tex, e, t, W, H, fov=FOV, floor_y=floor)
            out.paste(tile(img, f"{tag} — {vname}", sub, col), (c * (W + 4), r * (H + 4)))
    OUT.parent.mkdir(parents=True, exist_ok=True); out.save(OUT); print(OUT)
    # the numbers: where each part's FRONT (north) face samples, vanilla box UV vs Patrix per-face UV (128 px texture units)
    print("\npart            vanilla box uv  -> vanilla front-face rect      | Patrix JEM front-face rect")
    jem = json.loads((convb.CEM / "warden.jem").read_text())
    pfront = {}
    def walk(m, name):
        for bx in m.get("boxes", []):
            if "uvNorth" in bx: pfront.setdefault(name, bx["uvNorth"])
        for s in m.get("submodels", []): walk(s, name)
    for m in jem["models"]: walk(m, m.get("part"))
    for b in vb:
        for cu in b.get("cubes", []):
            u, v = cu["uv"]; sx, sy, sz = cu["size"]
            front = [u + sz, v + sz, u + sz + sx, v + sz + sy]
            print(f"{b['name']:15s} {str(cu['uv']):14s}  {str(front):28s} | {pfront.get(b['name'], '-')}")


if __name__ == "__main__":
    main()
