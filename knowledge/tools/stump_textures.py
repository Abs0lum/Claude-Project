#!/usr/bin/env python3
"""stump_textures.py — his F9 = yes (15:42 10-02): "a cut stump block with growth rings by age". Built from OUR Patrix
end-grain (RP-01 pw_<species>_log_top_v0 + its MER / normal) by a polar remap around the pith, so it stays Patrix art:
  young   shows the inner 45 % of the rings, stretched to the edge  -> few, wide rings (~5)
  mature  inner 72 %                                                   -> ~8
  old     the end grain as it is                                       -> ~11
  elder   rings packed 1.7x toward the pith, the outer band repeated   -> ~18, tight
The outer 9 % (bark rim) is kept from the original in every age, and the fresh cut face is lifted 6 % brighter.
The same remap is applied to the MER and normal so the texture set lines up. Output: _staging/stumps/ + a preview sheet."""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path("/home/claude/_build/rp01-116/textures/blocks")
OUT = Path("/home/claude/_staging/stumps")
TIERS = {"oak": ["young", "mature", "old", "elder"], "spruce": ["young", "mature", "old", "elder"],
         "birch": ["young", "mature", "old"], "jungle": ["young", "mature", "old", "elder"],
         "dark_oak": ["elder"], "pale_oak": ["elder"]}
SCALE = {"young": 0.45, "mature": 0.72, "old": 1.0, "elder": 1.7}
RIM = 0.91


def remap(img, age, brighten):
    """Circular polar remap around the pith (bilinear), feathered back into the original bark rim (square edge band)."""
    from scipy import ndimage
    a = np.asarray(img.convert("RGBA")).astype(np.float32)
    h, w = a.shape[:2]
    cy, cx = (h - 1) / 2, (w - 1) / 2
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    r = np.hypot(dx, dy) / (w / 2)                               # rings are circles in the Patrix end grain
    s = SCALE[age]
    t = r * s
    if s > 1.0:                                                  # elder: tighter rings; past the old edge the outer ring
        lo, hi = 0.55, 0.85                                      # band repeats MIRRORED (ping-pong), so no seam
        span = hi - lo
        over = np.maximum(t - hi, 0)
        ping = hi - np.abs((over % (2 * span)) - span)
        t = np.where(t <= hi, t, ping)
    k = np.where(r > 1e-6, t / np.maximum(r, 1e-6), 0)
    sx, sy = cx + dx * k, cy + dy * k
    out = np.stack([ndimage.map_coordinates(a[..., c], [sy, sx], order=1, mode="nearest") for c in range(4)], -1)
    if brighten and a[..., :3].mean() < 180:                   # pale oak is already near white: never lift it
        out[..., :3] = np.clip(out[..., :3] * 1.06, 0, 255)
    edge = np.maximum(np.abs(dx), np.abs(dy)) / (w / 2)          # the bark rim follows the square block edge
    wgt = np.clip((edge - 0.84) / (0.93 - 0.84), 0, 1)[..., None]
    out = out * (1 - wgt) + a * wgt
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles = []
    for sp, ages in TIERS.items():
        base = Image.open(SRC / f"pw_{sp}_log_top_v0.png")
        mer = SRC / f"pw_{sp}_log_top_v0_mer.png"
        nrm = next((SRC / f"pw_{sp}_log_top_v0{s}.png" for s in ("_n", "_normal") if (SRC / f"pw_{sp}_log_top_v0{s}.png").exists()), None)
        for age in ages:
            stem = f"pw_{sp}_{age}_stump_top"
            col = remap(base, age, True)
            col.save(OUT / f"{stem}.png")
            layers = {"color": stem}
            if mer.exists():
                remap(Image.open(mer), age, False).save(OUT / f"{stem}_mer.png")
                layers["metalness_emissive_roughness"] = f"{stem}_mer"
            if nrm:
                remap(Image.open(nrm), age, False).save(OUT / f"{stem}_n.png")
                layers["normal"] = f"{stem}_n"
            (OUT / f"{stem}.texture_set.json").write_text(
                '{"format_version": "1.21.30", "minecraft:texture_set": ' + str(layers).replace("'", '"') + "}")
            tiles.append((sp, age, col))
    # preview: species rows x age columns, 3x zoom
    z = 2
    tw = 128 * z
    sheet = Image.new("RGB", (4 * (tw + 10) + 120, len(TIERS) * (tw + 24) + 30), (30, 30, 34))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    ages = ["young", "mature", "old", "elder"]
    for i, a in enumerate(ages):
        d.text((120 + i * (tw + 10), 8), a.upper(), fill=(240, 220, 160))
    for r, sp in enumerate(TIERS):
        d.text((8, 30 + r * (tw + 24) + tw // 2), sp, fill=(240, 240, 240))
        for spp, age, col in tiles:
            if spp != sp:
                continue
            i = ages.index(age)
            sheet.paste(col.convert("RGB").resize((tw, tw), Image.BILINEAR), (120 + i * (tw + 10), 30 + r * (tw + 24)))
    sheet.save("/mnt/user-data/outputs/STUMP-RINGS-PREVIEW.png")
    print(len(tiles), "stump tops", sheet.size)


if __name__ == "__main__":
    main()
