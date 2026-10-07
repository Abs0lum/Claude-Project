#!/usr/bin/env python3
"""uv_layout_sheet.py — visual check of every MISMATCH row of uv_layout_census (D-C295).
Per mob, three cells (front-east view): OUR TEXTURE on Mojang's geometry (= what his game draws) | MOJANG's texture on the
same geometry (vanilla reference) | our texture flat, for reading what it was painted for.
Output: _docs/sizes/UV-LAYOUT-SHEET.png"""
import json, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV

ROOT = Path("/home/claude"); VAN = ROOT / "_intake/bedrock-samples/resource_pack"
OUT = ROOT / "_docs/sizes/UV-LAYOUT-SHEET.png"
# label, geometry id, texture path, pack build holding OUR texture
ROWS = [("warden (RP-06)", "geometry.warden", "textures/entity/warden/warden", "rp06-1419"),
        ("blaze (RP-06)", "geometry.blaze", "textures/entity/blaze", "rp06-1419"),
        ("breeze wind (RP-06)", "geometry.breeze_wind_mid", "textures/entity/breeze/breeze_wind", "rp06-1419"),
        ("phantom (RP-06)", "geometry.phantom", "textures/entity/phantom", "rp06-1419"),
        ("creaking (RP-06)", "geometry.creaking", "textures/entity/creaking/creaking", "rp06-1419"),
        ("endermite (RP-06)", "geometry.endermite", "textures/entity/endermite", "rp06-1419"),
        ("slime (RP-06)", "geometry.slime", "textures/entity/slime/slime", "rp06-1419"),
        ("allay (RP-07)", "geometry.allay", "textures/entity/allay/allay", "rp07-1425"),
        ("sniffer (RP-07)", "geometry.sniffer", "textures/entity/sniffer/sniffer", "rp07-1425"),
        ("copper golem eyes (RP-07)", "geometry.copper_golem", "textures/entity/copper_golem/copper_golem_eyes", "rp07-1425"),
        ("ender crystal (RP-04)", "geometry.ender_crystal", "textures/entity/endercrystal/endercrystal", "rp04-142")]
W, H = 300, 250
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception:
    FB = FR = ImageFont.load_default()


def vgeo(ident):
    for p in (VAN / "models/entity").rglob("*.json"):
        t = p.read_text(encoding="utf-8")
        if ident not in t: continue
        d = ML._parse_json(t)
        for g in d.get("minecraft:geometry", []) or []:
            if g["description"]["identifier"] == ident:
                return g["bones"], g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)
        for k, g in d.items():                      # legacy 1.8 format ("geometry.blaze": {...}, "geometry.x:parent")
            if isinstance(g, dict) and k.split(":")[0] == ident and g.get("bones"):
                return g["bones"], g.get("texturewidth", 64), g.get("textureheight", 64)
    raise KeyError(ident)


def tex(base, path):
    for ext in (".png", ".tga"):
        if (base / (path + ext)).exists(): return base / (path + ext)
    return None


def tile(img, title, sub, col):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 32], fill=col)
    d.text((5, 2), title, fill=(255, 255, 255), font=FB); d.text((5, 17), sub, fill=(225, 230, 240), font=FR)
    return img


def flat(p):
    im = Image.open(p).convert("RGBA"); bg = Image.new("RGBA", im.size, (70, 70, 100, 255)); bg.alpha_composite(im)
    bg.thumbnail((W - 10, H - 42)); c = Image.new("RGB", (W, H), (255, 255, 255)); c.paste(bg.convert("RGB"), (5, 37)); return c


def main():
    rows = []
    for label, gid, tpath, build in ROWS:
        bones, tw, th = vgeo(gid)
        faces = truth_posed_faces(bones, tw, th, bone_affines(bones))
        ours, van = tex(ROOT / "_build" / build, tpath), tex(VAN, tpath)
        e, t = camera(faces, "front-east")
        floor = min(0.0, min(q[1] for f in faces for q in f.pts))
        a = tile(render_entity(faces, ours, e, t, W, H, fov=FOV, floor_y=floor), f"{label.upper()} — IN GAME NOW", "Mojang geometry + OUR texture", (170, 40, 40))
        b = tile(render_entity(faces, van, e, t, W, H, fov=FOV, floor_y=floor), f"{label.upper()} — VANILLA", "Mojang geometry + Mojang texture", (60, 60, 60))
        c = tile(flat(ours), f"our {Path(tpath).name}.png", f"{Image.open(ours).size[0]}x{Image.open(ours).size[1]} (what it was painted as)", (40, 70, 130))
        row = Image.new("RGB", (3 * W + 8, H), (255, 255, 255))
        for i, im in enumerate((a, b, c)): row.paste(im, (i * (W + 4), 0))
        rows.append(row)
    out = Image.new("RGB", (rows[0].width, len(rows) * (H + 4) - 4), (255, 255, 255))
    for i, r in enumerate(rows): out.paste(r, (0, i * (H + 4)))
    out.save(OUT); print(OUT, out.size)


if __name__ == "__main__":
    main()
