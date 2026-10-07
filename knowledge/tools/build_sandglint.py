#!/usr/bin/env python3
"""build_sandglint.py — his 22:51 / 00:07: Florida-beach glint on sand B. Mineral grains act as tiny tilted mirrors.
His ruling 00:07: keep sand's random face rotation; grains tilted in 8 directions (E, NE, N, NW, W, SW, S, SE),
12.5 % each — so whatever rotation a block gets, there are always grains facing the rising and the setting sun.

Per grain (MERS, the old v1.1.1 glint spec, FOUNDATION §6.5): R 128 (metalness 0.5), G 0, B 12 (roughness 0.05), A 12.
Every other pixel keeps RP-04's sand MERS. Grain normal: tilt 8-14 deg (mirror condition for a sun ~10 deg high seen
looking toward it at ~30 deg down = ~10 deg tilt toward the sun). Base normal = sand B (seamless, 3 deg).
Grain size: 70 % one texel, 30 % 2 x 2 (wrapped at the tile edge, so tiles stay seamless).
  G1 = 0.6 % of the texels are grain   G2 = 1.5 %
Packs: PW-SandTest-G1 / G2 RP 1.0.0 — 24 sand sets each (colour copied from RP-04 1.3.147), capabilities pbr.
Preview: _docs/sand/SAND-GLINT-PREVIEW.png (sun 10 deg east, camera west of the sand looking east; Blinn-Phong spec)."""
import json
import shutil
import uuid
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path("/home/claude")
SRC = ROOT / "_build/rp04-147/textures/blocks"
NB = ROOT / "_staging/sand_vv/B"
DIRS = np.radians(np.arange(8) * 45.0)
DENS = {"G1": 0.006, "G2": 0.015}
GRAIN_MERS = np.array([128, 0, 12, 12], np.uint8)


def grains(v, dens):
    rng = np.random.default_rng(1000 + v)
    n = 256
    count = int(dens * n * n / (0.7 * 1 + 0.3 * 4))
    ys, xs = rng.integers(0, n, count), rng.integers(0, n, count)
    big = rng.random(count) < 0.3
    d = rng.integers(0, 8, count)                       # direction index: exactly uniform in expectation (12.5 %)
    tilt = np.radians(rng.uniform(8, 14, count))
    mask = np.full((n, n), -1, np.int32)
    tl = np.zeros((n, n))
    for i in range(count):
        cells = [(ys[i], xs[i])] + ([((ys[i] + 1) % n, xs[i]), (ys[i], (xs[i] + 1) % n), ((ys[i] + 1) % n, (xs[i] + 1) % n)]
                                    if big[i] else [])
        for y, x in cells:
            mask[y, x] = d[i]
            tl[y, x] = tilt[i]
    return mask, tl


def make(v, dens):
    col = Image.open(SRC / f"pw_sand_v{v}.png").convert("RGBA")
    mers = np.asarray(Image.open(SRC / f"pw_sand_v{v}_mers.png").convert("RGBA")).copy()
    nb = np.asarray(Image.open(NB / f"pw_sand_v{v}_n.png").convert("RGB")).astype(float) / 255 * 2 - 1
    mask, tl = grains(v, dens)
    g = mask >= 0
    ang = DIRS[np.clip(mask, 0, 7)]
    gn = np.stack([np.sin(tl) * np.cos(ang), np.sin(tl) * np.sin(ang), np.cos(tl)], -1)
    n = np.where(g[..., None], gn, nb)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    mers[g] = GRAIN_MERS
    nimg = np.clip(np.round((n + 1) / 2 * 255), 0, 255).astype(np.uint8)
    share = np.bincount(mask[g], minlength=8) / g.sum()
    return col, Image.fromarray(nimg, "RGB"), Image.fromarray(mers, "RGBA"), float(g.mean()), share


def build(kind):
    dst = ROOT / f"_build/sandtest-{kind.lower()}-100"
    assert not dst.exists(), "never rebuild a build dir"
    tb = dst / "textures/blocks"
    tb.mkdir(parents=True)
    stats = []
    for v in range(1, 25):
        stem = f"pw_sand_v{v}"
        col, n, m, frac, share = make(v, DENS[kind])
        shutil.copy2(SRC / f"{stem}.png", tb / f"{stem}.png")
        n.save(tb / f"{stem}_n.png")
        m.save(tb / f"{stem}_mers.png")
        (tb / f"{stem}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
            "color": stem, "normal": f"{stem}_n", "metalness_emissive_roughness_subsurface": f"{stem}_mers"}}, indent=2))
        stats.append((frac, share))
    (dst / "manifest.json").write_text(json.dumps({"format_version": 2, "header": {
        "name": f"PW-SandTest {kind} v1.0.0",
        "description": f"TEST ONLY (10-02): sand B + mineral glint {DENS[kind] * 100:.1f} % of texels, grains tilted in 8 "
                       "directions (12.5 % each). Put it at the TOP of the stack. Not for normal play.",
        "uuid": str(uuid.uuid4()), "version": [1, 0, 0], "min_engine_version": [1, 21, 120]},
        "modules": [{"description": f"sand glint {kind}", "type": "resources", "uuid": str(uuid.uuid4()), "version": [1, 0, 0]}],
        "capabilities": ["pbr"]}, indent=2))
    shutil.copy2(ROOT / "_build/lighttest-sat-100/pack_icon.png", dst / "pack_icon.png")
    fr = np.mean([s[0] for s in stats])
    sh = np.mean([s[1] for s in stats], axis=0)
    print(kind, f"grain texels {fr * 100:.2f} %", "direction shares", np.round(sh * 100, 1).tolist())
    return dst


def preview():
    """Two panels per density: sunrise view (sun 10 deg in the east, camera looking east) and noon (sun 70 deg)."""
    rng = np.random.default_rng(3)
    layout = rng.integers(1, 25, (4, 4))
    rots = rng.integers(0, 4, (4, 4))
    panels = []
    for kind in ("B-only", "G1", "G2"):
        for elev in (10, 70):
            img = np.zeros((1024, 1024, 3))
            for (r, c), v in np.ndenumerate(layout):
                if kind == "B-only":
                    col = np.asarray(Image.open(SRC / f"pw_sand_v{v}.png").convert("RGB")).astype(float)
                    n = np.asarray(Image.open(NB / f"pw_sand_v{v}_n.png").convert("RGB")).astype(float) / 255 * 2 - 1
                    rough = np.asarray(Image.open(SRC / f"pw_sand_v{v}_mers.png").convert("RGBA"))[..., 2] / 255.0
                    metal = np.zeros(rough.shape)
                else:
                    ci, ni, mi, _, _ = make(v, DENS[kind])
                    col = np.asarray(ci.convert("RGB")).astype(float)
                    n = np.asarray(ni).astype(float) / 255 * 2 - 1
                    mm = np.asarray(mi).astype(float) / 255
                    rough, metal = mm[..., 2], mm[..., 0]
                k = rots[r, c]                                     # random face rotation (isotropic)
                col, rough, metal = np.rot90(col, k), np.rot90(rough, k), np.rot90(metal, k)
                n = np.rot90(n, k).copy()
                for _ in range(k):                                 # rotate the normal vectors with the texture
                    n[..., 0], n[..., 1] = -n[..., 1].copy(), n[..., 0].copy()
                n /= np.linalg.norm(n, axis=-1, keepdims=True)
                L = np.array([np.cos(np.radians(elev)), 0, np.sin(np.radians(elev))])    # +x = east
                V = np.array([-np.cos(np.radians(30)), 0, np.sin(np.radians(30))])       # camera to the west
                H = (L + V) / np.linalg.norm(L + V)
                alb = (col / 255) ** 2.2
                ndl = np.clip(n @ L, 0, None)
                ndh = np.clip(n @ H, 0, None)
                a = np.maximum(rough, 0.03) ** 2
                spec_pow = 2 / a ** 2 - 2
                f0 = 0.04 * (1 - metal) + metal * 0.9
                spec = f0 * (spec_pow + 8) / 8 * ndh ** spec_pow * ndl
                lit = alb * (2.2 * ndl[..., None] + 0.35) + np.clip(spec, 0, 30)[..., None] * np.array([1.0, 0.85, 0.6])
                lit = lit / (1 + lit) * 1.5
                img[r * 256:(r + 1) * 256, c * 256:(c + 1) * 256] = np.clip(lit, 0, 1) ** (1 / 2.2) * 255
            panels.append((f"{kind} - sun {elev} deg {'(sunrise, looking toward the sun)' if elev == 10 else '(midday)'}",
                           Image.fromarray(img.astype(np.uint8))))
    sheet = Image.new("RGB", (2 * 1034 + 10, 3 * 1060 + 10), (20, 20, 22))
    d = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(panels):
        x, y = 10 + (i % 2) * 1034, 10 + (i // 2) * 1060
        d.text((x, y), t, fill=(235, 235, 235))
        sheet.paste(im, (x, y + 22))
    out = ROOT / "_docs/sand/SAND-GLINT-PREVIEW.png"
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    import sys
    if "--preview-only" not in sys.argv:
        build("G1")
        build("G2")
    preview()
