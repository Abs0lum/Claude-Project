#!/usr/bin/env python3
"""sand_vv_preview.py — offline look-alike of Vibrant Visuals shading on sand (his 20:23 report: VV sand lumpy, blue,
'too drastic'; phone without VV = the look he wants). NOT the game renderer: a simple model to compare the CAUSES.

Model per pixel (linear light): albedo * (SUN * max(0, N.L) + SKY * (0.5 + 0.5 N.z)), Reinhard tone map, sRGB.
  SUN warm white, SKY blue fill (the blue in his photos' pits = shadowed facets lit by sky only).
Panels: NO-VV (colour only, flat light, = phone) | CURRENT maps | A = current depth, small lumps removed |
        B = depth from the colour's own soft mottling (what he sees on the phone, made gently 3-D).
Each panel = 6 x 6 blocks, random variants (fixed seed), at two sun heights: 20 deg (late afternoon) and 60 deg.
Height maps are made tile-seamless (Frankot-Chellappa integration / periodic+smooth split), so B and A have no block
borders from the depth map. Output: _docs/sand/SAND-VV-PREVIEW.png + candidate maps in _staging/sand_vv/<A|B>/."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

ROOT = Path("/home/claude")
SRC = ROOT / "_build/rp04-146/textures/blocks"
OUT = ROOT / "_docs/sand"
STAGE = ROOT / "_staging/sand_vv"
N_TILE, GRID = 256, 6
SUN_RGB = np.array([1.00, 0.92, 0.80]) * 2.2
SKY_RGB = np.array([0.42, 0.58, 1.00]) * 0.55
TARGET_TILT = {"A": 3.0, "B": 3.0}          # mean degrees of slope (current sand = 7.4)


def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055) * 255


def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(float)


def decode_normal(a):
    n = a / 255.0 * 2 - 1
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def encode_normal(n):
    n = n / np.linalg.norm(n, axis=-1, keepdims=True)
    return np.clip(np.round((n + 1) / 2 * 255), 0, 255).astype(np.uint8)


def frankot_chellappa(n):
    """Integrate a normal map to a periodic height field (FFT; the result tiles seamlessly by construction)."""
    p, q = -n[..., 0] / n[..., 2], -n[..., 1] / n[..., 2]
    h, w = p.shape
    wx = np.fft.fftfreq(w) * 2 * np.pi
    wy = np.fft.fftfreq(h) * 2 * np.pi
    WX, WY = np.meshgrid(wx, wy)
    den = WX ** 2 + WY ** 2
    den[0, 0] = 1
    Z = (-1j * WX * np.fft.fft2(p) - 1j * WY * np.fft.fft2(q)) / den
    Z[0, 0] = 0
    return np.real(np.fft.ifft2(Z))


def periodic_part(u):
    """Moisan periodic + smooth decomposition: returns the periodic component (no wrap seam)."""
    h, w = u.shape
    v = np.zeros_like(u)
    v[0, :] += u[-1, :] - u[0, :]
    v[-1, :] += u[0, :] - u[-1, :]
    v[:, 0] += u[:, -1] - u[:, 0]
    v[:, -1] += u[:, 0] - u[:, -1]
    cx = np.cos(2 * np.pi * np.arange(w) / w)
    cy = np.cos(2 * np.pi * np.arange(h) / h)
    den = 2 * cx[None, :] + 2 * cy[:, None] - 4
    den[0, 0] = 1
    S = np.fft.fft2(v) / den
    S[0, 0] = 0
    return u - np.real(np.fft.ifft2(S))


def normals_from_height(hgt, target_tilt):
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) / 2
    gy = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) / 2

    def make(k):
        n = np.stack([-gx * k, -gy * k, np.ones_like(hgt)], -1)
        return n / np.linalg.norm(n, axis=-1, keepdims=True)
    lo, hi = 0.0, 1e4
    for _ in range(60):                                       # bisection on strength -> requested mean slope
        k = (lo + hi) / 2
        t = np.degrees(np.arccos(make(k)[..., 2])).mean()
        lo, hi = (k, hi) if t < target_tilt else (lo, k)
    return make((lo + hi) / 2)


def tilt(n):
    return float(np.degrees(np.arccos(np.clip(n[..., 2], -1, 1))).mean())


def candidate(v, kind):
    col = load_rgb(SRC / f"pw_sand_v{v}.png")
    if kind == "current":
        ts = json.loads((SRC / f"pw_sand_v{v}.texture_set.json").read_text())["minecraft:texture_set"]
        return col, decode_normal(load_rgb(SRC / f"{ts['normal']}.png"))
    if kind == "A":
        ts = json.loads((SRC / f"pw_sand_v{v}.texture_set.json").read_text())["minecraft:texture_set"]
        hgt = frankot_chellappa(decode_normal(load_rgb(SRC / f"{ts['normal']}.png")))
        hgt = gaussian_filter(hgt, 6, mode="wrap")            # keep shapes wider than ~12 px (1/20 of a block)
    else:                                                     # B: the colour's own soft mottling as height
        lum = col @ np.array([0.2126, 0.7152, 0.0722])
        hgt = gaussian_filter(periodic_part(lum), 5, mode="wrap")
    return col, normals_from_height(hgt, TARGET_TILT[kind])


def shade(col, n, sun_elev, flat=False):
    alb = srgb_to_lin(col)
    if flat:                                                  # phone, VV off: colour with plain even light
        lit = alb * 1.0
    else:
        az = np.radians(200)                                  # sun from the upper-left of the panel
        L = np.array([np.cos(np.radians(sun_elev)) * np.cos(az), np.cos(np.radians(sun_elev)) * np.sin(az),
                      np.sin(np.radians(sun_elev))])
        ndl = np.clip(n @ L, 0, None)[..., None]
        lit = alb * (SUN_RGB * ndl + SKY_RGB * (0.5 + 0.5 * n[..., 2:3]))
        lit = lit / (1 + lit)                                 # Reinhard
        lit = lit * 1.6
    return lin_to_srgb(lit).astype(np.uint8)


def panel(kind, sun_elev, layout, cache):
    img = np.zeros((GRID * N_TILE, GRID * N_TILE, 3), np.uint8)
    for (r, c), v in np.ndenumerate(layout):
        key = (kind if kind != "novv" else "current", v)
        if key not in cache:
            cache[key] = candidate(v, key[0])
        col, n = cache[key]
        img[r * N_TILE:(r + 1) * N_TILE, c * N_TILE:(c + 1) * N_TILE] = shade(col, n, sun_elev, flat=kind == "novv")
    return Image.fromarray(img).resize((GRID * 96, GRID * 96), Image.LANCZOS)


def main():
    rng = np.random.default_rng(7)
    layout = rng.integers(1, 25, (GRID, GRID))
    cache = {}
    cols = [("novv", "NO VV (phone)"), ("current", "CURRENT maps"), ("A", "A: current depth, lumps removed"),
            ("B", "B: depth from the colour's soft mottling")]
    rows = [20, 60]
    W, H, pad, head = GRID * 96, GRID * 96, 10, 24
    sheet = Image.new("RGB", (pad + len(cols) * (W + pad), head + len(rows) * (H + head + pad)), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    for j, e in enumerate(rows):
        y = head + j * (H + head + pad)
        for i, (k, lab) in enumerate(cols):
            x = pad + i * (W + pad)
            d.text((x, y - 16), f"{lab}" + ("" if k == "novv" else f" - sun {e} deg"), fill=(235, 235, 235))
            sheet.paste(panel(k, e, layout, cache), (x, y))
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT / "SAND-VV-PREVIEW.png")
    report = {}
    for kind in ("current", "A", "B"):
        ts = [tilt(cache[(kind, v)][1]) for v in sorted({int(v) for v in layout.flat})]
        report[kind] = {"mean_tilt_deg": round(float(np.mean(ts)), 2)}
    for kind in ("A", "B"):                                    # stage all 24 candidate normal maps
        (STAGE / kind).mkdir(parents=True, exist_ok=True)
        for v in range(1, 25):
            _, n = cache.get((kind, v)) or candidate(v, kind)
            Image.fromarray(encode_normal(n)).save(STAGE / kind / f"pw_sand_v{v}_n.png")
    (OUT / "SAND-VV-PREVIEW.json").write_text(json.dumps(report, indent=1))
    print(sheet.size, report)


if __name__ == "__main__":
    main()
