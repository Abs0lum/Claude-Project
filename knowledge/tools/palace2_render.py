#!/usr/bin/env python3
"""palace2_render.py — FLOOR PLANS of PALACE II (tools/palacegen2.py), one image per level, plus a section strip.

A plan is a horizontal cut at a walking level f, seen FROM ABOVE in the model frame: +x (east, deeper from the street) to
the RIGHT, +z (south) DOWN, so the street / gate side is on the LEFT and model north is at the top. One cell = 4 px.
Cell colours: walls by material, walkable floor by what it stands on, water, doors (wood orange, iron dark red), the
SECRET blocks (jib panel magenta, secret painting pink), spiral stairs (purple), vanilla stairs (violet), ladders /
trapdoors (yellow), beds by role (lord gold, noble blue, child cyan, servant tan, guard red, clerk green, cell black).
Red outlines = the hidden network (no-walk boxes for ordinary townsfolk); white numbers = rooms (legend on the right);
the grey grid = the 4 x 4 piece cut (64 cells). With --reach the walk check is painted over the floor: green = reachable
from the gate both ways, amber = in only, grey hatch = not reached.
Usage: palace2_render.py [--reach] [--out DIR]"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/home/claude/tools")
import palace2_verify as V  # noqa: E402

OUT = Path("/home/claude/_docs/palace/palace2")
S = 4
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LEVELS = [(-12, "B2", "B2 — tunnels and sewers (walk -12)"), (-7, "B1", "B1 — cellars, Pozzi, crypt, grotto (walk -7)"),
          (0, "G", "GROUND (walk 0)"), (6, "N", "ÉTAGE NOBLE — state floor (walk 6)"),
          (11, "E", "ENTRESOL upper / wing + tower mezzanines (walk 11)"), (15, "A", "ATTIC (walk 15)")]
ROLE_COL = {"lord": (230, 180, 30), "noble": (60, 110, 220), "child": (40, 220, 230), "servant": (190, 150, 100),
            "guard": (220, 40, 40), "clerk": (40, 170, 70), "cell": (10, 10, 10)}


def wall_colour(n):
    if n is None:
        return (20, 20, 24)
    if "glass" in n:
        return (150, 200, 230)
    if "planks" in n or "spruce" in n or "oak" in n or "barrel" in n or "bookshelf" in n:
        return (120, 86, 52)
    if "wool" in n:
        return (60, 140, 60)
    if "bars" in n:
        return (90, 90, 100)
    if "hay" in n:
        return (200, 180, 60)
    if "brick" in n and "stone" not in n:
        return (150, 70, 55)
    return (92, 92, 96)


def floor_colour(n):
    if n is None:
        return (25, 25, 30)
    if n.endswith("_carpet"):
        return {"red": (170, 50, 50), "blue": (60, 70, 160)}.get(n.split(":")[1].split("_")[0], (150, 60, 60))
    if "grass" in n:
        return (90, 150, 70)
    if "gravel" in n:
        return (165, 160, 150)
    if "planks" in n or "slab" in n and ("spruce" in n or "oak" in n):
        return (205, 170, 120)
    if "diorite" in n or "quartz" in n:
        return (235, 235, 230)
    if "andesite" in n:
        return (175, 178, 180)
    if "cobble" in n:
        return (140, 140, 140)
    if "bars" in n:
        return (120, 130, 150)
    return (200, 200, 196)


def plan(p, m, f, title, path, both=None, fwd=None):
    sx, _, sz = m.size
    W, H = sx * S, sz * S
    LEG = 470
    img = Image.new("RGB", (W + LEG, H + 40), (14, 14, 18))
    px = np.zeros((sz, sx, 3), dtype=np.uint8)
    y = f - m.bottom
    code, idx, names = m.code, m.idx, m.names
    beds = {(b["x"], b["z"]): b["role"] for b in p.bed_roles if b["feet"] == f}
    for x in range(sx):
        for z in range(sz):
            c0, c1, cb = code[x, y, z], code[x, y + 1, z], code[x, y - 1, z]
            n0, nb = names[idx[x, y, z]], names[idx[x, y - 1, z]]
            if c0 & V.WATER:
                col = (40, 90, 200)
            elif c0 & V.SPIRAL:
                col = (150, 70, 200)
            elif c0 & V.STAIR:
                col = (190, 120, 230)
            elif c0 & V.SECRET:
                col = (255, 40, 220) if n0 == "pw:jib_panel" else (255, 150, 200)
            elif c0 & V.IRON:
                col = (130, 20, 20)
            elif c0 & V.DOOR:
                col = (240, 140, 30)
            elif c0 & (V.LAD | V.TRAP):
                col = (240, 220, 40)
            elif c0 & V.BED:
                col = ROLE_COL.get(beds.get((x, z)) or beds.get((x - 1, z)) or beds.get((x + 1, z)) or beds.get((x, z - 1)) or beds.get((x, z + 1)), (200, 200, 200))
            elif (c0 & V.PASS) and (c1 & V.PASS | c1 & V.SECRET | c1 & V.DOOR):
                if cb & V.WATER:
                    col = (60, 120, 220)
                elif cb & (V.SUP | V.SECRET | V.NOSTEP):
                    col = floor_colour(n0 if n0 and n0.endswith("_carpet") else nb)
                else:
                    col = (8, 8, 10)                                     # open to below (a well, a stair hall, a vault)
            elif c0 & V.PASS:
                col = (60, 60, 64)                                       # too low to stand (a crawl / under a stair)
            elif c0 & V.NOSTEP:
                col = (70, 60, 50)
            elif c0 & V.SUP and n0 and not any(k in n0 for k in ("brick", "stone", "planks", "glass", "dirt", "wool", "andesite", "diorite", "quartz", "hay", "bars")):
                col = (180, 140, 90)                                     # furniture
            else:
                col = wall_colour(n0)
            if both is not None and (c0 & V.PASS or c0 & V.SECRET or c0 & V.DOOR) and (x, y, z) in fwd:
                if (x, y, z) not in both:
                    col = tuple(int(0.4 * a + 0.6 * b) for a, b in zip(col, (255, 170, 0)))
            px[z, x] = col
    big = Image.fromarray(px).resize((W, H), Image.NEAREST)
    img.paste(big, (0, 40))
    d = ImageDraw.Draw(img)
    if both is not None:                                                  # hatch walkable floor that is not reached
        for x in range(sx):
            for z in range(sz):
                c0 = code[x, y, z]
                if (c0 & V.PASS) and (code[x, y + 1, z] & V.PASS) and (code[x, y - 1, z] & V.SUP) and (x, y, z) not in fwd:
                    d.line([(x * S, 40 + z * S), (x * S + S - 1, 40 + z * S + S - 1)], fill=(255, 255, 255))
    for k in range(1, 4):
        d.line([(k * 64 * S, 40), (k * 64 * S, 40 + H)], fill=(110, 110, 110), width=1)
        d.line([(0, 40 + k * 64 * S), (W, 40 + k * 64 * S)], fill=(110, 110, 110), width=1)
    for h in p.hidden:
        x0, x1, z0, z1, f0, f1 = h["box"]
        if f0 - 1 <= f <= f1 + 1:
            d.rectangle([x0 * S, 40 + z0 * S, (x1 + 1) * S - 1, 40 + (z1 + 1) * S - 1], outline=(255, 50, 50), width=1)
    ft = ImageFont.truetype(FONT, 11)
    fb = ImageFont.truetype(FONTB, 18)
    fl = ImageFont.truetype(FONT, 10)
    d.text((8, 10), f"PALACE II — {title}   (from above: street/gate LEFT = west, model north UP; 1 cell = {S} px; grid = 64-cell pieces)", fill=(240, 240, 240), font=fb if len(title) < 40 else ft)
    rooms = [r for r in p.rooms if r["f"] == f or (r["f"] in (f - 1, f + 1) and r["level"] in ("E",) and f == 11)]
    rooms = [r for r in p.rooms if abs(r["f"] - f) <= 1]
    ly = 46
    d.text((W + 10, ly), "rooms at this level (number = label on the plan)", fill=(255, 255, 255), font=ft); ly += 16
    per_col = max(1, (H - 260) // 12)
    for i, r in enumerate(rooms):
        x0, x1, z0, z1 = r["box"]
        cx, cz = (x0 + x1 + 1) * S // 2, 40 + (z0 + z1 + 1) * S // 2
        lab = str(i + 1)
        tw = d.textlength(lab, font=fl)
        d.rectangle([cx - tw / 2 - 1, cz - 6, cx + tw / 2 + 1, cz + 6], fill=(0, 0, 0) if not r["hidden"] else (120, 0, 0))
        d.text((cx - tw / 2, cz - 6), lab, fill=(255, 255, 255), font=fl)
        col = i // per_col
        if col < 2:
            d.text((W + 10 + col * 230, ly + (i % per_col) * 12), f"{i + 1:>3} {r['name'][:32]}{' *' if r['hidden'] else ''}",
                   fill=(255, 160, 160) if r["hidden"] else (220, 220, 220), font=fl)
    ky = 40 + H - 200
    keys = [((240, 140, 30), "wooden door"), ((130, 20, 20), "iron door (one-way)"), ((255, 40, 220), "jib panel (secret, walk-through)"),
            ((255, 150, 200), "secret painting"), ((150, 70, 200), "spiral stair (pw:)"), ((190, 120, 230), "vanilla stair"),
            ((240, 220, 40), "ladder / trapdoor"), ((40, 90, 200), "water"), ((8, 8, 10), "open to below"),
            ((230, 180, 30), "bed: lord"), ((60, 110, 220), "bed: noble"), ((40, 220, 230), "bed: child"), ((190, 150, 100), "bed: servant"),
            ((220, 40, 40), "bed: guard"), ((40, 170, 70), "bed: clerk"), ((255, 50, 50), "outline: hidden network (no-walk) / * room")]
    for i, (c, t) in enumerate(keys):
        xx, yy = W + 10 + (i // 8) * 230, ky + (i % 8) * 16
        d.rectangle([xx, yy, xx + 10, yy + 10], fill=c)
        d.text((xx + 14, yy - 2), t, fill=(220, 220, 220), font=fl)
    img.save(path)
    return path


def section(p, m, z, path):
    """a vertical cut along x at frontage z, seen from the south (looking north, +x to the right)"""
    sx, sy, _ = m.size
    px = np.zeros((sy, sx, 3), dtype=np.uint8)
    for x in range(sx):
        for y in range(sy):
            c, n = m.code[x, y, z], m.names[m.idx[x, y, z]]
            if c & V.WATER:
                col = (40, 90, 200)
            elif c & V.SPIRAL:
                col = (150, 70, 200)
            elif c & V.SECRET:
                col = (255, 40, 220)
            elif c & V.PASS:
                col = (16, 16, 20) if not (c & (V.LAD | V.DOOR)) else (240, 220, 40)
            elif n and n.startswith("pw:roof"):
                col = (150, 90, 50)
            elif n and "dirt" in n:
                col = (95, 70, 45)
            elif n and "grass" in n:
                col = (80, 140, 60)
            else:
                col = wall_colour(n)
            px[sy - 1 - y, x] = col
    big = Image.fromarray(px).resize((sx * S, sy * S), Image.NEAREST)
    img = Image.new("RGB", (sx * S, sy * S + 30), (14, 14, 18))
    img.paste(big, (0, 30))
    d = ImageDraw.Draw(img)
    for f in (-12, -7, 0, 6, 15):
        yy = 30 + (sy - 1 - (f - m.bottom)) * S + S
        d.line([(0, yy), (6, yy)], fill=(255, 255, 0))
        d.text((8, yy - 10), f"walk {f}", fill=(255, 255, 0), font=ImageFont.truetype(FONT, 10))
    d.text((8, 6), f"PALACE II section at z {z}, seen from the south (looking north): street LEFT, +x right; 1 cell = {S} px", fill=(240, 240, 240), font=ImageFont.truetype(FONT, 12))
    img.save(path)
    return path


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else OUT
    out.mkdir(parents=True, exist_ok=True)
    R, (p, m, W, fwd, both, fwd_shut) = V.run(None) if "--reach" in sys.argv else (None, (None,) * 6)
    if p is None:
        import palacegen2 as P2
        p = P2.build(); m = V.Model(p)
    for (f, tag, title) in LEVELS:
        print(plan(p, m, f, title, out / f"PALACE2-PLAN-{tag}{'-reach' if both is not None else ''}.png", both, fwd))
    for z in (75, 127, 177, 23):
        print(section(p, m, z, out / f"PALACE2-SECTION-z{z}.png"))
