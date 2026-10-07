#!/usr/bin/env python3
"""tree_trunk_sheet_228.py — the program-228 AFTER sheet of the changed tree groups (TREE-TRUNK-PLAN §9 conventions).

One row per changed group. Left, boxed: the group's representative (the template that lost the most logs; for
jungle_young the first root-fix template) as BEFORE side | AFTER side | BEFORE top | AFTER top. Right: every changed
template of the group, AFTER side view. Side = orthographic from the south (east to the right), top = from the sky
(north up). Colours: leaves green (darker = deeper), wood brown, pw root block MAGENTA, mangrove prop roots dark brown.
Overlays: RED outline = trunk tip; WHITE outline = trunk cell hidden behind leaves (x-ray); ORANGE-RED fill = trunk log
seen in the top 4 layers (from the sky or along a horizontal axis, leaves opaque). Labels: nn; 'R' = root-fix template.
Usage: tree_trunk_sheet_228.py BEFORE_DIR AFTER_DIR VERIFY_JSON OUT_PNG"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/home/claude/tools")
import install_trees_228 as V  # noqa: E402   (load, trunk_of, is_* helpers)

PX = 4
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11)
BIG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
BG, PANEL = (24, 26, 30), (40, 44, 50)


def kind(n):
    if V.is_root(n):
        return "root"
    if n == "minecraft:mangrove_roots":
        return "mroot"
    if V.is_log(n):
        return "wood"
    if V.is_leaf(n):
        return "leaf"
    return None


BASE = {"leaf": (76, 150, 58), "wood": (120, 84, 50), "root": (210, 60, 200), "mroot": (70, 50, 35)}


def shade(c, depth, n):
    f = 1.0 - 0.45 * (depth / max(1, n - 1))
    return tuple(int(v * f) for v in c)


def analyse(path):
    size, cells = V.load(path)
    cells = {p: v for p, v in cells.items() if kind(v[0])}
    rootc = min((p for p, v in cells.items() if V.is_root(v[0])), key=lambda p: p[1])
    trunk = V.trunk_of(cells, rootc)
    top_y = max(p[1] for p, v in cells.items() if V.is_leaf(v[0]))
    tip = max(p[1] for p in trunk)
    seen = set()
    sx, sy, sz = size
    for p in trunk:
        if p[1] < top_y - 3:
            continue
        x, y, z = p
        rays = [[(x, yy, z) for yy in range(y + 1, sy)], [(xx, y, z) for xx in range(x + 1, sx)], [(xx, y, z) for xx in range(0, x)],
                [(x, y, zz) for zz in range(z + 1, sz)], [(x, y, zz) for zz in range(0, z)]]
        if any(not any(q in cells for q in ray) for ray in rays):
            seen.add(p)
    return size, cells, trunk, tip, seen


def side(an):
    size, cells, trunk, tip, seen = an
    sx, sy, sz = size
    img = Image.new("RGB", (sx * PX, sy * PX), PANEL)
    d = ImageDraw.Draw(img)
    for x in range(sx):
        for y in range(sy):
            for z in range(sz - 1, -1, -1):                      # from the south (+z) looking north
                v = cells.get((x, y, z))
                if v:
                    p = (x, y, z)
                    col = (235, 80, 40) if p in seen else shade(BASE[kind(v[0])], sz - 1 - z, sz)
                    X, Y = x * PX, (sy - 1 - y) * PX
                    d.rectangle([X, Y, X + PX - 1, Y + PX - 1], fill=col)
                    break
    front = {}
    for x in range(sx):
        for y in range(sy):
            front[(x, y)] = next((z for z in range(sz - 1, -1, -1) if (x, y, z) in cells), None)
    for p in trunk:
        X, Y = p[0] * PX, (sy - 1 - p[1]) * PX
        if p[1] == tip:
            d.rectangle([X - 1, Y - 1, X + PX, Y + PX], outline=(255, 30, 30))
        elif front[(p[0], p[1])] != p[2] and not any(front[(p[0], p[1])] == q[2] for q in trunk if (q[0], q[1]) == (p[0], p[1])):
            d.rectangle([X, Y, X + PX - 1, Y + PX - 1], outline=(240, 240, 240))
    return img


def top(an):
    size, cells, trunk, tip, seen = an
    sx, sy, sz = size
    img = Image.new("RGB", (sx * PX, sz * PX), PANEL)
    d = ImageDraw.Draw(img)
    for x in range(sx):
        for z in range(sz):
            for y in range(sy - 1, -1, -1):
                v = cells.get((x, y, z))
                if v:
                    p = (x, y, z)
                    col = (235, 80, 40) if p in seen else shade(BASE[kind(v[0])], sy - 1 - y, sy)
                    d.rectangle([x * PX, z * PX, x * PX + PX - 1, z * PX + PX - 1], fill=col)
                    break
    for p in trunk:
        if p[1] == tip:
            d.rectangle([p[0] * PX - 1, p[2] * PX - 1, p[0] * PX + PX, p[2] * PX + PX], outline=(255, 30, 30))
    return img


def main():
    bdir, adir, vj, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    ver = json.loads(vj.read_text())
    per = ver["per_template"]
    groups = defaultdict(list)
    for s in ver["changed"]:
        groups[s.rsplit("_", 1)[0]].append(s)
    rows = []
    for g in sorted(groups):
        names = sorted(groups[g])
        rep = names[0] if g == "jungle_young" else max(names, key=lambda s: (per[s]["logs_removed"], s))
        b, a = analyse(bdir / f"{rep}.mcstructure"), analyse(adir / f"{rep}.mcstructure")
        ref = [side(b), side(a), top(b), top(a)]
        afters = [(s, side(analyse(adir / f"{s}.mcstructure"))) for s in names]
        rows.append((g, rep, ref, afters, len(names)))
    GAP, LBL, HEAD = 6, 14, 20
    widths, heights = [], []
    for g, rep, ref, afters, n in rows:
        w = sum(i.width for i in ref) + GAP * 5 + 16 + sum(i.width + GAP for _, i in afters)
        h = HEAD + max(max(i.height for i in ref), max(i.height for _, i in afters)) + LBL + 8
        widths.append(w)
        heights.append(h)
    title_h = 46
    W, H = max(widths) + 20, sum(heights) + title_h + 10
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((10, 6), "PROGRAM 228 TREES — AFTER (BP-02 1.3.228 overlay). Left box: representative BEFORE side | AFTER side | BEFORE top | "
                    "AFTER top. Right: every changed template, AFTER side (from the south).", fill=(230, 230, 230), font=FONT)
    d.text((10, 24), "red outline = trunk tip · white outline = trunk hidden in leaves · orange-red = trunk seen in top 4 layers · "
                     "magenta = pw root block · R = jungle_young root-fix template", fill=(200, 200, 200), font=FONT)
    y0 = title_h
    for (g, rep, ref, afters, n), h in zip(rows, heights):
        d.text((10, y0 + 2), f"{g}: {n} changed · representative {rep} (logs removed {per[rep]['logs_removed']}, trunk tip "
                             f"{per[rep]['trunk_tip'][0]}->{per[rep]['trunk_tip'][1]}, crown top {per[rep]['crown_top']}, "
                             f"height {per[rep]['size'][0][1]}->{per[rep]['size'][1][1]})", fill=(240, 220, 120), font=BIG)
        x = 10
        base = y0 + h - LBL - 8
        bx0 = x - 3
        for lab, im in zip(("B side", "A side", "B top", "A top"), ref):
            yy = base - im.height if "side" in lab else y0 + HEAD
            sheet.paste(im, (x, yy))
            d.text((x, base + 2), lab, fill=(200, 200, 200), font=FONT)
            x += im.width + GAP
        d.rectangle([bx0, y0 + HEAD - 3, x - GAP + 3, base + LBL + 2], outline=(240, 220, 120))
        x += 16
        for s, im in afters:
            sheet.paste(im, (x, base - im.height))
            tag = s[-2:] + ("R" if per[s].get("root_fix") else "")
            d.text((x, base + 2), tag, fill=(200, 200, 200), font=FONT)
            x += im.width + GAP
        d.line([0, y0 + h - 2, W, y0 + h - 2], fill=(60, 64, 70))
        y0 += h
    sheet.save(out, optimize=True)
    print(f"{out} {W}x{H}")


if __name__ == "__main__":
    main()
