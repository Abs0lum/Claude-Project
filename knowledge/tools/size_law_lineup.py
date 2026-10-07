#!/usr/bin/env python3
"""size_law_lineup.py — D-C291: L-SIZE-REAL as a picture. Each mob side-on at ONE scale (near-orthographic), TODAY (what the
game draws: client scale x BP scale) and PROPOSED (x the size_law factor), next to his 5'10" character and a 1-block bar.
usage: size_law_lineup.py <group> <out_png>     groups: vanilla, wild"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import visible_size as V
import molang_lint as ML
import roster_size_census as R
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from block_render import Face

ROOT = Path("/home/claude")
PLAN = {r["id"]: r for r in json.load(open(ROOT / "_docs/sizes/size_law_plan.json"))}
GROUPS = {
    "vanilla": (40.0, ["minecraft:cow", "minecraft:llama", "minecraft:horse", "minecraft:goat", "minecraft:panda", "minecraft:polar_bear",
                       "minecraft:turtle", "minecraft:salmon", "minecraft:cod", "minecraft:tropicalfish", "minecraft:parrot"]),
    "wild": (16.0, ["sf_nba:black_bear", "sf_nba:grizzly_bear", "sf_nba:boar", "sf_nba:deer", "sf_nba:tortoise", "sf_nba:great_white_shark",
                    "sf_nba:hammer_head_shark", "sf_nba:moray", "sf_nba:electric_eel", "sf_nba:jungle_scorpion", "sf_nba:desert_scorpion",
                    "sf_nba:anteater", "sf_nba:elephant", "sf_nba:whale"]),
}
D = 6000.0
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)


def find_entity(ident):
    for pack in R.PACKS:
        for p in pack.glob("entity/*.json"):
            de = R.client_desc(p)
            if de and de.get("identifier") == ident: return p, pack, de
    return None


def faces_for(ident, factor=1.0):
    p, pack, desc = find_entity(ident)
    roots = [pack] + [q for q in R.PACKS if q != pack] + [V.VANILLA]
    bones, tw, th = V.find_geometry(roots, desc["geometry"]["default"])
    tex = desc.get("textures") or {}
    tp = V.find_texture(roots, tex.get("default") or next(iter(tex.values())))
    k = V.client_scale(desc) * R.bp_scale(ident) * factor
    import fnmatch
    rules = V.everyday_rules(desc, roots)          # D-C291: draw the everyday state (the old rule dropped every conditional part)
    def vis(n):
        v = True
        for pat, hid in rules:
            if fnmatch.fnmatch(n.lower(), pat): v = not hid
        return v
    par = {b["name"]: b.get("parent") for b in bones}
    def hidden(n):
        while n:
            if not vis(n): return True
            n = par.get(n)
        return False
    faces = [f for f in truth_posed_faces(bones, tw, th, bone_affines(bones)) if not hidden(f.bone)]
    return [Face([[q[0] * k, q[1] * k, q[2] * k] for q in f.pts], f.uv, f.mat, f.name, f.bone) for f in faces], tp


def render(ident, factor, S, H, BASE):
    faces, tp = faces_for(ident, factor)
    P = np.array([q for f in faces for q in f.pts]) * np.array([1, 1, -1])
    lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2
    Wc = max(int((hi[2] - lo[2]) * S) + 24, 96)             # room for the name under narrow mobs
    fov = 2 * np.degrees(np.arctan((H / 2) / (S * D)))
    ty = (H / 2 - (H - BASE)) / S
    return render_entity(faces, str(tp), [c[0] + D, ty, c[2]], [c[0], ty, c[2]], Wc, H, fov=fov, bg=(236, 240, 246), floor_y=None).convert("RGB")


def person(d, x0, S, BASE):
    k = 0.9375 * S / 16.0 * 16.0 / 16.0 * 16.0 / 16.0   # model px -> image px
    k = 0.9375 * S
    def box(xa, y_top, w, h): d.rectangle([xa, BASE - y_top * k, xa + w * k, BASE - (y_top - h) * k], fill=(120, 124, 132), outline=(60, 60, 70))
    box(x0 + 2 * k, 12, 4, 12); box(x0 + 2 * k, 24, 4, 12); box(x0, 32, 8, 8)
    d.text((x0 - 4, BASE + 4), "you", fill=(40, 40, 50), font=F)
    return int(x0 + 8 * k + 14)


def row(mobs, S, H, BASE, proposed, label, col, PPB):
    cells = []
    for m in mobs:
        f = PLAN.get(m, {}).get("factor") or 1.0
        if not proposed or PLAN.get(m, {}).get("action", "").startswith("keep"): f = f if proposed and not PLAN.get(m, {}).get("action", "").startswith("keep") else 1.0
        cells.append((render(m, f if proposed else 1.0, S, H, BASE), m))
    Wt = 90 + sum(c[0].width for c in cells) + 8 * len(cells)
    img = Image.new("RGB", (Wt, H + 52), (236, 240, 246)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, Wt, 20], fill=col); d.text((6, 3), label, fill="white", font=FB)
    x = person(d, 20, S, 22 + BASE)
    for im, m in cells:
        img.paste(im, (x, 22)); nm = m.split(":")[1]
        pl = PLAN.get(m, {})
        sub = f"x{pl.get('factor')}" if proposed and pl.get("factor") and not pl.get("action", "").startswith("keep") else ("keep" if proposed else f"{pl.get('current', '')} blk")
        d.text((x + 2, 22 + BASE + 4), nm, fill=(20, 20, 30), font=F); d.text((x + 2, 22 + BASE + 17), sub, fill=(60, 60, 80), font=F)
        x += im.width + 8
    d.line([0, 22 + BASE, Wt, 22 + BASE], fill=(90, 90, 100), width=1)
    d.rectangle([Wt - 80, 28, Wt - 80 + PPB, 33], fill=(30, 30, 30)); d.text((Wt - 80, 35), "1 block", fill=(30, 30, 30), font=F)
    return img


def main(group, out):
    PPB, mobs = GROUPS[group]
    S = PPB / 16.0
    tallest = 0
    for m in mobs:
        for f in (1.0, PLAN.get(m, {}).get("factor") or 1.0):
            faces, _ = faces_for(m, f)
            tallest = max(tallest, max(q[1] for fc in faces for q in fc.pts))
    H = int(max(2.2 * 16, tallest) * S) + 20; BASE = H - 6
    a = row(mobs, S, H, BASE, False, "TODAY — what the game draws (client scale x BP scale)", (130, 30, 30), PPB)
    b = row(mobs, S, H, BASE, True, "PROPOSED — real life (your character = 5'10\"; 1 m = 1.05 blocks)", (30, 70, 140), PPB)
    W = max(a.width, b.width)
    s = Image.new("RGB", (W, a.height + b.height + 6), (255, 255, 255)); s.paste(a, (0, 0)); s.paste(b, (0, a.height + 6))
    s.save(out); print(out, s.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
