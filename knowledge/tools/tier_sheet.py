#!/usr/bin/env python3
"""tier_sheet.py — before/after sheet for the FINAL tier-round list (_docs/blocks/TIER-ROUND.json, entries without
'skipped'). One row per chosen texture: OLD (delivered build) colour | normal | roughness  ||  NEW (tier build) colour |
normal | roughness. Every cell is drawn at the same display size (nearest-neighbour), so a 256 texture shows its finer
detail and a 64 texture shows its coarser pixels. Each cell label carries the real pixel size.
Output: _docs/blocks/TIER-BEFORE-AFTER-FINAL.png"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path("/home/claude")
OLD = {"RP-04": "rp04-146", "RP-10": "rp10-144", "RP-05": "rp05-52", "RP-03": "rp03-61", "RP-01": "rp01-108"}
NEW = {"RP-04": "rp04-147", "RP-10": "rp10-145", "RP-05": "rp05-53", "RP-03": "rp03-62", "RP-01": "rp01-109"}
PICK = ["dirt_v2", "coarse_dirt_v7", "dirt_podzol_side_v3", "rooted_dirt", "mud_v4", "packed_mud_v2",
        "muddy_mangrove_roots_side_v5", "farmland_dry", "farmland_wet", "oak_log_v5", "log_oak",
        "end_bricks_v2", "purpur_block", "purpur_pillar", "chorus_flower"]
CELL, PAD, HEAD = 192, 6, 30
EXT = (".png", ".tga", ".jpg")


def find(build, stem):
    d = ROOT / "_build" / build / "textures/blocks"
    ts = d / f"{stem}.texture_set.json"
    out = {}
    if ts.exists():
        s = json.loads(ts.read_text())["minecraft:texture_set"]
        for k, v in s.items():
            if isinstance(v, str) and not v.startswith("#"):
                p = next((d / (v + e) for e in EXT if (d / (v + e)).exists()), None)
                if p:
                    out["normal" if k == "normal" else ("mers" if k.startswith("metalness") else k)] = p
    if "color" not in out:
        p = next((d / (stem + e) for e in EXT if (d / (stem + e)).exists()), None)
        if p:
            out["color"] = p
    return out


def cell(p, kind):
    if p is None:
        im = Image.new("RGB", (CELL, CELL), (60, 0, 60))
        ImageDraw.Draw(im).text((8, 8), "none", fill=(255, 255, 255))
        return im, "none"
    src = Image.open(p)
    w, h = src.size
    if h > w:
        src = src.crop((0, 0, w, w))   # flipbook: first frame
    a = np.asarray(src.convert("RGBA"))
    if kind == "mers":
        g = a[..., 2]                   # roughness in blue
        im = Image.fromarray(np.stack([g] * 3, -1).astype(np.uint8))
        lab = f"rough {w}x{h} mean {g.mean():.0f}"
    elif kind == "normal":
        im = Image.fromarray(a[..., :3])
        lab = f"normal {w}x{h}"
    else:
        bg = np.full(a.shape[:2] + (3,), 40.0)
        al = a[..., 3:4] / 255.0
        im = Image.fromarray((a[..., :3] * al + bg * (1 - al)).astype(np.uint8))
        lab = f"colour {w}x{h}"
    return im.resize((CELL, CELL), Image.NEAREST), lab


def main():
    rep = json.loads((ROOT / "_docs/blocks/TIER-ROUND.json").read_text())
    acc = {x["path"].rsplit("/", 1)[1]: x for x in rep if not x.get("skipped")}
    rows = [s for s in PICK if s in acc]
    W = PAD + 6 * (CELL + PAD) + 20
    H = HEAD + len(rows) * (CELL + 34 + PAD) + 10
    sheet = Image.new("RGB", (W, H), (24, 24, 28))
    dr = ImageDraw.Draw(sheet)
    dr.text((PAD, 8), "TIER ROUND (final list) - left 3 = NOW (delivered WeJvidvY)   |   right 3 = AFTER (tier build).  "
            "Same display size; label = real pixels.", fill=(230, 230, 230))
    y = HEAD
    for s in rows:
        e = acc[s]
        pk = e["pack"].split()[0]
        o, n = find(OLD[pk], s), find(NEW[pk], s)
        dr.text((PAD, y), f"{s}  ({e['pack'].split()[0]})  {e['from'][0]} -> {e['to'][0]}", fill=(255, 220, 120))
        x = PAD
        for side, m in (("NOW", o), ("AFTER", n)):
            for k in ("color", "normal", "mers"):
                im, lab = cell(m.get(k), k)
                sheet.paste(im, (x, y + 16))
                dr.text((x, y + 18 + CELL), f"{side} {lab}", fill=(200, 200, 200))
                x += CELL + PAD
            x += 20 if side == "NOW" else 0
        y += CELL + 34 + PAD
    out = ROOT / "_docs/blocks/TIER-BEFORE-AFTER-FINAL.png"
    sheet.save(out)
    print(out, sheet.size, len(rows), "rows")


if __name__ == "__main__":
    main()
