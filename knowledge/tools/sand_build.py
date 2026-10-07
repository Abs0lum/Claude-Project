#!/usr/bin/env python3
"""sand_build.py — the SAND round (his 18:10 ask + 18:55 rulings, D-C423): 64 seamless variants per sand family from
Patrix 26.2 256x's own CTM sand (optifine/ctm/patrix/sand/<yellow|red>/1..36, method=repeat 6x6), all layers at 256:
  COLOUR   the 6x6 Patrix grid (a 1536 px torus: method=repeat means it tiles) -> 64 crops of 256 at spread offsets.
           Seamless against ANY neighbour (Bedrock picks variants at random, not in grid order): every crop fades into one
           shared self-tiling BORDER tile inside a band at its edges, so wherever two variants meet, border meets border.
  NORMAL   Patrix _n (#156) through the same crops + fades, plus WIND RIPPLES: one height field with a 256 px period (so it
           runs on across block edges), crests ~ 1/6 block apart along a prevailing wind, gently warped; slopes kept small
           so the noon sun shows little and a low sun (sunset) draws long ripple shading.
  MERS     Patrix _s by Lesson #156 (R smoothness -> roughness, G -> metal only >= 230, A -> emissive only < 255, B -> SSS):
           NO emissive (his 18:55); the glint = Patrix's own smoothness specks (~0.9 % of pixels) -> low roughness,
           so they throw real specular when the sun is low; everything else stays a rough dielectric.
Writes _staging/sand/<family>/{colour,normal,mers}/<name>_v<k>.png and previews in _docs/sand/."""
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import mers_derive as MD  # noqa: E402

ZIP = ROOT / "_intake/patrix262_256/Patrix_26.2_256x_basic.zip"
CTM = "assets/minecraft/optifine/ctm/patrix/sand/{fam}/{k}{suf}.png"
OUT = ROOT / "_staging/sand"
DOCS = ROOT / "_docs/sand"
T, N_VAR, BAND = 256, 64, 24
FAMILIES = {"yellow": "pw_sand"}          # his 19:04: red sand is already right — yellow only
RIPPLE_SLOPE = 0.09          # mean ripple slope added to the normal (Patrix sand's own mean slope is ~0.3)


def zread(Z, fam, k, suf):
    return np.asarray(Image.open(io.BytesIO(Z.read(CTM.format(fam=fam, k=k, suf=suf)))).convert("RGBA"))


def grid(Z, fam, suf):
    g = np.zeros((6 * T, 6 * T, 4), np.uint8)
    for k in range(1, 37):
        r, c = divmod(k - 1, 6)
        g[r * T:(r + 1) * T, c * T:(c + 1) * T] = zread(Z, fam, k, suf)
    return g


def crop(g, y, x):
    """256 crop of the torus at (y, x) with wrap-around."""
    return np.roll(np.roll(g, -y, 0), -x, 1)[:T, :T]


def fade_mask():
    """1 inside, falling smoothly to 0 at the edges over BAND px (smoothstep)."""
    d = np.minimum.outer(np.minimum(np.arange(T), T - 1 - np.arange(T)), np.minimum(np.arange(T), T - 1 - np.arange(T)))
    t = np.clip(d / BAND, 0, 1)
    return t * t * (3 - 2 * t)


def self_tiling(tile):
    """a tile that wraps onto itself: blend it with its half-offset copy, the copy weighted near the tile's own edges."""
    sh = np.roll(np.roll(tile, T // 2, 0), T // 2, 1).astype(float)
    m = fade_mask()[..., None]
    return tile.astype(float) * m + sh * (1 - m)


def ripple_field():
    """one height field with a 256 px period in both axes: integer wave vectors only, so it continues across block edges.
    Crests run across the prevailing wind (wave vector ~ (5, 3) per block = crests ~ 44 px = 1/6 block apart, diagonal),
    a finer secondary set, a gentle warp so the crests wander. Slopes by PERIODIC central differences (np.gradient's
    one-sided edges drew a line at every block edge in the first preview)."""
    yy, xx = np.mgrid[0:T, 0:T].astype(float) / T * 2 * np.pi
    warp = 0.7 * np.sin(1 * xx + 1 * yy) + 0.5 * np.sin(2 * xx - 1 * yy + 1.3)
    h = (np.sin(5 * xx + 3 * yy + warp) * 1.0 + np.sin(9 * xx + 5 * yy + 1.4 * warp + 2.1) * 0.35
         + np.sin(4 * xx + 4 * yy + 0.6 * warp + 4.0) * 0.25)
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) / 2
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) / 2
    s = np.sqrt(gx * gx + gy * gy).mean()
    return gx / s * RIPPLE_SLOPE, gy / s * RIPPLE_SLOPE


def add_ripples(nrm, rx, ry):
    """Patrix normal (RG = XY, measured convention R ~ -dh/dcolumn, G ~ -dh/drow) + ripple slopes, renormalised."""
    v = nrm[..., :3].astype(float) / 255 * 2 - 1
    v[..., 0] -= rx
    v[..., 1] -= ry
    v /= np.linalg.norm(v, axis=-1, keepdims=True)
    out = nrm.copy()
    out[..., :3] = np.round((v + 1) / 2 * 255).clip(0, 255)
    return out


MOUND_SIGMA = 4.0          # px: slopes broader than this are removed from Patrix's normal (19:1x preview: its tile-sized
#                             mounds showed the 4x4 grid of random variants — H-32 again, in the normal map this time)


def highpass_normal(nrm):
    """keep Patrix's grain, drop its tile-sized mounds: slopes minus their Gaussian blur on the torus (wrap), renormalised.
    The dune feeling then comes from the ripple field, which is continuous across every block edge."""
    from scipy import ndimage
    v = nrm[..., :3].astype(float) / 255 * 2 - 1
    sx, sy = v[..., 0] / v[..., 2], v[..., 1] / v[..., 2]
    sx = sx - ndimage.gaussian_filter(sx, MOUND_SIGMA, mode="wrap")
    sy = sy - ndimage.gaussian_filter(sy, MOUND_SIGMA, mode="wrap")
    n = np.stack([sx, sy, np.ones_like(sx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    out = nrm.copy()
    out[..., :3] = np.round((n + 1) / 2 * 255).clip(0, 255)
    return out


def offsets(n, seed):
    """64 crop positions spread over the 1536 torus (a jittered 8x8 lattice)."""
    rng = np.random.default_rng(seed)
    step = 6 * T / 8
    return [(int((i * step + rng.integers(0, step)) % (6 * T)), int((j * step + rng.integers(0, step)) % (6 * T)))
            for i in range(8) for j in range(8)][:n]


def calm_spot(gc):
    """the 256 crop whose luminance varies least (std) and holds the fewest dark specks — the border every variant fades to
    is seen at EVERY block edge, so it must carry no feature of its own."""
    lum = gc[..., :3].astype(float).mean(-1)
    med = np.median(lum)
    best = None
    for y in range(0, 6 * T, 32):
        for x in range(0, 6 * T, 32):
            c = np.roll(np.roll(lum, -y, 0), -x, 1)[:T, :T]
            score = c.std() + 400 * float((c < med - 40).mean())
            if best is None or score < best[0]:
                best = (score, y, x)
    return best[1], best[2]


def build_family(Z, fam, name, seed):
    gc, gn, gs = grid(Z, fam, ""), grid(Z, fam, "_n"), grid(Z, fam, "_s")
    gn = highpass_normal(MD.normal_156(gn))
    gs = MD.mers_156(gs)
    by, bx = calm_spot(gc)                               # the shared BORDER tile: the CALMEST spot of the torus (19:1x: a
    #                                                      pebble in red sand's first border drew a dark cross at every edge)
    border = [self_tiling(crop(g, by, bx)) for g in (gc, gn, gs)]
    m = fade_mask()[..., None]
    rx, ry = ripple_field()
    out = []
    for k, (y, x) in enumerate(offsets(N_VAR, seed)):
        layers = []
        for g, b in zip((gc, gn, gs), border):
            layers.append(np.round(crop(g, y, x).astype(float) * m + b * (1 - m)).clip(0, 255).astype(np.uint8))
        c, n, s = layers
        c[..., 3] = 255
        n = add_ripples(n, rx, ry)
        n[..., 3] = 255
        s[..., 1] = 0                                     # never emissive (his 18:55)
        out.append((c, n, s))
        for kind, arr in (("colour", c), ("normal", n), ("mers", s)):
            p = OUT / fam / kind / f"{name}_v{k}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(arr, "RGBA").save(p, optimize=True)
    return out


def shade(c, n, s, sun_elev_deg, sun_az_deg=-35.0, exposure=1.0):
    """preview shading: Lambert + GGX-ish specular from MERS roughness (B) and metal (R), sun of the given elevation.
    The view looks down at 35 deg from the south. A PREVIEW only (not the game's renderer)."""
    el, az = np.radians(sun_elev_deg), np.radians(sun_az_deg)
    L = np.array([np.cos(el) * np.sin(az), -np.cos(el) * np.cos(az), np.sin(el)])
    V = np.array([0.0, -np.cos(np.radians(35)), np.sin(np.radians(35))])
    H = (L + V) / np.linalg.norm(L + V)
    nv = n[..., :3].astype(float) / 255 * 2 - 1
    nv = np.stack([nv[..., 0], -nv[..., 1], nv[..., 2]], -1)       # image rows run south -> world y up the screen
    nv /= np.linalg.norm(nv, axis=-1, keepdims=True)
    ndl = np.clip((nv * L).sum(-1), 0, 1)
    ndh = np.clip((nv * H).sum(-1), 0, 1)
    r = np.clip(s[..., 2].astype(float) / 255, 0.05, 1)
    a2 = (r * r) ** 2
    D = a2 / (np.pi * ((ndh * ndh) * (a2 - 1) + 1) ** 2)
    F0 = 0.04 + (s[..., 0] / 255) * 0.9
    spec = D * F0 * ndl * 0.25
    sun = np.array([1.0, 0.93, 0.82]) if sun_elev_deg > 20 else np.array([1.0, 0.62, 0.35])
    col = c[..., :3].astype(float) / 255
    out = col * (ndl[..., None] * sun * 0.9 + 0.12) + spec[..., None] * sun * 3.0
    return Image.fromarray((out * 255 * exposure).clip(0, 255).astype(np.uint8))


def preview(fam, name, var, old_dir):
    DOCS.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    pick = rng.integers(0, len(var), size=(4, 4))
    def mosaic(i):
        return np.concatenate([np.concatenate([var[pick[r, c]][i] for c in range(4)], 1) for r in range(4)], 0)
    C, Nn, Sm = mosaic(0), mosaic(1), mosaic(2)
    tiles = [("NEW colour: 16 random variants side by side (seams?)", Image.fromarray(C[..., :3])),
             ("NEW noon (sun 70 deg)", shade(C, Nn, Sm, 70)),
             ("NEW sunset (sun 8 deg): ripples + glint", shade(C, Nn, Sm, 8, exposure=1.6)),
             ("NEW roughness (dark = glossy specks)", Image.fromarray(Sm[..., 2]).convert("RGB"))]
    if old_dir:   # today's RP-04 sand, same 4x4 random layout, same preview lighting
        olds = []
        for k in range(1, 25):
            cp = old_dir / f"{name}_v{k}.png"
            mp = old_dir / f"{name}_v{k}_mers.png"
            npth = old_dir / f"{name}_v{k}_n.png"
            if cp.exists():
                c = np.asarray(Image.open(cp).convert("RGBA"))
                s_ = np.asarray(Image.open(mp).convert("RGBA")) if mp.exists() else np.zeros_like(c)
                n_ = np.asarray(Image.open(npth).convert("RGBA")) if npth.exists() else np.full_like(c, [128, 128, 255, 255])
                olds.append((c, n_, s_))
        if olds:
            pk = rng.integers(0, len(olds), size=(4, 4))
            def om(i):
                return np.concatenate([np.concatenate([olds[pk[r, c]][i] for c in range(4)], 1) for r in range(4)], 0)
            tiles = [("TODAY (RP-04 1.3.144) sunset, same lighting", shade(om(0), om(1), om(2), 8, exposure=1.6))] + tiles
    S = 512
    img = Image.new("RGB", (len(tiles) * (S + 8), S + 22), "white")
    d = ImageDraw.Draw(img)
    for i, (lab, im) in enumerate(tiles):
        img.paste(im.resize((S, S), Image.BOX), (i * (S + 8), 20))
        d.text((i * (S + 8) + 2, 4), lab, fill=(0, 0, 0))
    out = DOCS / f"SAND-PREVIEW-{fam}.png"
    img.save(out)
    return out


def main():
    Z = zipfile.ZipFile(ZIP)
    rep = {}
    for i, (fam, name) in enumerate(FAMILIES.items()):
        var = build_family(Z, fam, name, seed=11 + i)
        s = np.stack([v[2] for v in var])
        rough = s[..., 2].astype(float) / 255
        rep[fam] = {"variants": len(var), "rough_mean": round(float(rough.mean()), 3),
                    "glossy_share(<0.35)": round(float((rough < 0.35).mean()), 4), "metal_share": round(float((s[..., 0] > 25).mean()), 4),
                    "emissive_max": int(s[..., 1].max()), "preview": str(preview(fam, name, var, ROOT / "_build/rp04-144/textures/blocks"))}
        print(fam, rep[fam])
    (DOCS / "SAND-BUILD.json").write_text(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
