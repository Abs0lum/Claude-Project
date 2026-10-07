#!/usr/bin/env python3
"""sway_flipbooks.py — his 22:55 / 00:53: Patrix-quality plant animations (no Java pack ships plant animations; Java sways
plants with shaders, Bedrock cannot). We bend Patrix 26.2 256x STILLS into 16-frame flipbooks (256 x 4096 strips):
colour + normal + MERS strips, each frame bent the same way, so the depth/shine follow the leaf.

Bend model (per image row; h = height above the block's bottom, 0..1; theta = 2*pi*frame/16):
  land grass      dx = A * h^2 * sin(theta)  + 0.25 A h^2 sin(2 theta + 1.3)          (root fixed, tip sways)
  2-block plants  H = combined height (bottom block 0..0.5, top 0.5..1): dx = A * H^2 * sin(theta - 1.2 H)
                  -> the top block's bottom row moves exactly like the bottom block's top row (no break at the seam)
  seagrass        dx = A * h^1.5 * sin(theta - 2.5 h)   (slower, rolling)   tall: over H like 2-block plants
  kelp stem       ONE Patrix tile (plant/5, best self-overlap) made vertically self-joining (periodic_v) for kelp_a..d;
                  dx = A * sin(theta - 2 pi h)  -> identical at h=0 and h=1, so every stacked kelp block joins its
                  neighbour in every frame (all kelp keys share ONE frame order — no vanilla frame offsets)
  kelp top        same wave as the stem below it, tip free
Rows are shifted with sub-pixel linear sampling on premultiplied colour (no dark fringes); normal/MERS rows use the same
shift. Land grass colour graded onto today's picture (per-channel mean/std) so the biome tint behaves as now;
seagrass and kelp (not tinted in Bedrock) keep Patrix's own colour.
Outputs: _staging/sway/rp05/textures/blocks/sway/<name>.png/_n.png/_mer.png/.texture_set.json + FLIPBOOKS.json (defs)
+ _docs/flora/SWAY-PREVIEW.gif."""
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
__import__("os").environ["PW_STACK"] = "r1002a"   # before any tool imports stack_now
import mers_derive as MD  # noqa: E402
import pbr_round as PR  # noqa: E402
import tier_round as TR  # noqa: E402

import stack_now as S  # noqa: E402

FR = 16
CT = "assets/minecraft/optifine/ctm/patrix/"
OUT = ROOT / "_staging/sway/rp05/textures/blocks/sway"
# key, Patrix still, model, amplitude px (of 256), 2-block part, ticks/frame, today's image (grading reference)
PLANTS = [
    ("short_grass", "grass/plant/short/1", "grass", 9, None, 4, "textures/blocks/short_grass"),
    ("tallgrass", "grass/plant/short/2", "grass", 9, None, 4, "textures/blocks/tallgrass"),
    ("tall_grass_bottom", "grass/plant/tall/2", "tall", 16, "bottom", 4, "textures/blocks/tall_grass_bottom"),
    ("tall_grass_top", "grass/plant/tall/1", "tall", 16, "top", 4, "textures/blocks/tall_grass_top"),
    ("short_dry_grass", "grass/dry/1", "grass", 5, None, 5, "textures/blocks/short_dry_grass"),
    ("tall_dry_grass", "grass/dry/9", "grass", 6, None, 5, "textures/blocks/tall_dry_grass"),
    ("seagrass_short", "seagrass/short/1", "sea", 16, None, 6, "textures/blocks/seagrass_v0"),
    ("seagrass_tall_bot_a", "seagrass/tall/6", "seatall", 28, "bottom", 6, "textures/blocks/seagrass_doubletall_bottom_a"),
    ("seagrass_tall_top_a", "seagrass/tall/2", "seatall", 28, "top", 6, "textures/blocks/seagrass_doubletall_top_a"),
    ("seagrass_tall_bot_b", "seagrass/tall/13", "seatall", 28, "bottom", 6, "textures/blocks/seagrass_doubletall_bottom_a"),
    ("seagrass_tall_top_b", "seagrass/tall/9", "seatall", 28, "top", 6, "textures/blocks/seagrass_doubletall_top_a"),
    ("kelp_a", "kelp/plant/5", "kelp", 12, "stem", 6, "textures/blocks/kelp_a"),
    ("kelp_b", "kelp/plant/5", "kelp", 12, "stem", 6, "textures/blocks/kelp_a"),
    ("kelp_c", "kelp/plant/5", "kelp", 12, "stem", 6, "textures/blocks/kelp_a"),
    ("kelp_d", "kelp/plant/5", "kelp", 12, "stem", 6, "textures/blocks/kelp_a"),
    ("kelp_top", "kelp/top/2", "kelp", 12, "top", 6, "textures/blocks/kelp_top"),
    ("kelp_top_bulb", "kelp/top/3", "kelp", 12, "top", 6, "textures/blocks/kelp_top"),
]


def dx_rows(model, amp, part, frame):
    y = np.arange(256)
    h = (255 - y) / 255.0                       # 0 at the bottom row, 1 at the top row
    th = 2 * np.pi * frame / FR
    if model == "grass":
        return amp * h ** 2 * np.sin(th) + 0.25 * amp * h ** 2 * np.sin(2 * th + 1.3)
    if model in ("tall", "seatall"):
        H = h * 0.5 + (0.5 if part == "top" else 0.0)
        if model == "tall":
            return amp * H ** 2 * np.sin(th - 1.2 * H)
        return amp * H ** 1.5 * np.sin(th - 2.5 * H)
    if model == "sea":
        return amp * h ** 1.5 * np.sin(th - 2.5 * h)
    if model == "kelp":
        return amp * np.sin(th - 2 * np.pi * h)
    raise ValueError(model)


def shift_rows(a, dx):
    """shift each row right by dx[row] (float px) with linear sampling, zero outside."""
    h, w, c = a.shape
    xs = np.arange(w)[None, :] - dx[:, None]
    x0 = np.floor(xs).astype(int)
    f = (xs - x0)[..., None]
    out = np.zeros_like(a, dtype=float)
    for off, wt in ((0, 1 - f), (1, f)):
        xi = x0 + off
        ok = (xi >= 0) & (xi < w)
        samp = np.zeros_like(out)
        rows = np.broadcast_to(np.arange(h)[:, None], xi.shape)
        samp[ok] = a[rows[ok], xi[ok]]
        out += samp * wt
    return out


def _wavy(seed, base, amp):
    """a smooth cut line across the tile: row index per column (low-frequency noise, wraps horizontally)."""
    rng = np.random.default_rng(seed)
    x = np.arange(256) / 256 * 2 * np.pi
    y = sum(rng.uniform(-1, 1) * np.sin(k * x + rng.uniform(0, 6.28)) / k for k in (1, 2, 3))
    return np.round(base + amp * y / 1.8).astype(int)


def periodic_v(layers, seed=5):
    """make a tile join ITSELF vertically (stacked kelp): the original is kept between two wavy cut lines (around rows
    64 and 192); above / below them the copy rolled by half a tile is used (its top and bottom rows are neighbours in the
    original, so it wraps cleanly). Whole fronds come from one source — a clean cut, no speckle. Same cut for all layers."""
    up, lo = _wavy(seed, 64, 18), _wavy(seed + 1, 192, 18)
    y = np.arange(256)[:, None]
    keep = (y >= up[None, :]) & (y < lo[None, :])
    out = [np.where(keep[..., None], L, np.roll(L, 128, axis=0)) for L in layers]
    # drop leaf fragments the cut left floating (pieces not joined to the plant; the tile wraps vertically, so label a
    # 3-high stack and judge the middle copy)
    from scipy.ndimage import label
    a = out[0][..., 3] > 128
    lab, n = label(np.concatenate([a, a, a], 0))
    mid = lab[256:512]
    sizes = np.bincount(lab.ravel())
    small = np.isin(mid, [i for i in range(1, n + 1) if sizes[i] < 1800])
    out[0] = out[0].copy()
    out[0][small, 3] = 0
    return out


def top_from_stem(top_layers, stem_layers, seed=6):
    """kelp top: below a wavy cut line (around row 208) the stem tile's own rows are used, so the stem block underneath
    continues into it; Patrix's top above the line."""
    cut = _wavy(seed, 208, 14)
    y = np.arange(256)[:, None]
    low = y >= cut[None, :]
    out = [np.where(low[..., None], s, t) for t, s in zip(top_layers, stem_layers)]
    from scipy.ndimage import label
    lab, n = label(out[0][..., 3] > 128)
    sizes = np.bincount(lab.ravel())
    small = np.isin(lab, [i for i in range(1, n + 1) if sizes[i] < 1800 and not (lab[-1] == i).any()])
    out[0] = out[0].copy()
    out[0][small, 3] = 0                                 # floating cut fragments (pieces touching the bottom stay)
    return out


def frames(col, nrm, mer, model, amp, part):
    c, n, m = [], [], []
    a = col.astype(float) / 255
    pm = np.concatenate([a[..., :3] * a[..., 3:4], a[..., 3:4]], -1)        # premultiplied
    for t in range(FR):
        d = dx_rows(model, amp, part, t)
        s = shift_rows(pm, d)
        al = s[..., 3:4]
        rgb = np.where(al > 1e-4, s[..., :3] / np.maximum(al, 1e-4), 0)
        c.append(np.concatenate([rgb, al], -1))
        nn = shift_rows(nrm.astype(float), d)
        nn[..., :3] = np.where(nn[..., 3:4] > 0, nn[..., :3], 128)          # outside the plant: flat normal
        n.append(nn)
        mm = shift_rows(mer.astype(float), d)
        m.append(mm)
    to8 = lambda L, s: np.clip(np.round(np.concatenate(L, 0) * s), 0, 255).astype(np.uint8)  # noqa: E731
    return to8(c, 255), to8(n, 1), to8(m, 1)


def main():
    Z = zipfile.ZipFile(PR.PATRIX256)
    P = S.packs()
    OUT.mkdir(parents=True, exist_ok=True)
    defs, rep, gif_rows = [], [], []
    for key, src, model, amp, part, ticks, ref in PLANTS:
        col = np.asarray(Image.open(io.BytesIO(Z.read(CT + src + ".png"))).convert("RGBA"))
        assert col.shape[:2] == (256, 256), (src, col.shape)
        nrm = MD.normal_156(np.asarray(Image.open(io.BytesIO(Z.read(CT + src + "_n.png"))).convert("RGBA")))
        mer = MD.mers_156(np.asarray(Image.open(io.BytesIO(Z.read(CT + src + "_s.png"))).convert("RGBA")))
        nrm = nrm.copy()
        nrm[..., 3] = col[..., 3]                                           # carry the coverage for the flat fill
        if model == "kelp" and part == "stem":
            col, nrm, mer = periodic_v([col, nrm, mer])
            stem = (col, nrm, mer)
        elif model == "kelp" and part == "top":
            col, nrm, mer = top_from_stem([col, nrm, mer], list(stem))
        p, f = S.find_image(P, ref)
        if p is not None and model in ("grass", "tall"):          # tinted land grass: keep today's colour; sea plants
                                                                  # and kelp keep Patrix's own colour (not tinted)
            r = np.asarray(Image.open(io.BytesIO(p.read(f))).convert("RGBA"))
            r = r[: r.shape[1]]                                             # first frame of today's strip
            col = TR.grade_match(col, r)
        c, n, m = frames(col, nrm, mer, model, amp, part)
        n[..., 3] = 255
        name = key
        Image.fromarray(c, "RGBA").save(OUT / f"{name}.png", optimize=True)
        Image.fromarray(n, "RGBA").save(OUT / f"{name}_n.png", optimize=True)
        Image.fromarray(m, "RGBA").save(OUT / f"{name}_mer.png", optimize=True)
        (OUT / f"{name}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
            "color": name, "normal": f"{name}_n", "metalness_emissive_roughness_subsurface": f"{name}_mer"}}, indent=1))
        defs.append({"flipbook_texture": f"textures/blocks/sway/{name}", "atlas_tile": key, "ticks_per_frame": ticks,
                     "frames": list(range(FR)), "blend_frames": True})
        op = c[..., 3] > 128
        rep.append({"key": key, "source": src, "model": model, "amp_px": amp, "strip": list(c.shape[:2][::-1]),
                    "metal_max": int(m[..., 0].max()), "rough_mean": round(float(m[..., 2][op].mean()), 1),
                    "colour_mean": c[op][:, :3].mean(0).round(1).tolist(), "today": f"{p.name if p else None} {ref}"})
        gif_rows.append((key, c))
    (OUT.parent.parent.parent / "FLIPBOOKS.json").write_text(json.dumps(defs, indent=1))
    (ROOT / "_docs/flora").mkdir(parents=True, exist_ok=True)
    (ROOT / "_docs/flora/SWAY-REPORT.json").write_text(json.dumps(rep, indent=1))
    # preview GIF: the 2-block plants stacked, kelp stacked 3 high (a, b, top) to show the joins
    def tile(key, t):
        c = dict(gif_rows)[key]
        fr = c[t * 256:(t + 1) * 256].astype(float) / 255
        bg = np.array([0.55, 0.65, 0.75]) if not key.startswith(("sea", "kelp")) else np.array([0.12, 0.3, 0.42])
        return (fr[..., :3] * fr[..., 3:4] + bg * (1 - fr[..., 3:4])) * 255
    cols = [["short_grass"], ["short_dry_grass"], ["tall_grass_top", "tall_grass_bottom"], ["seagrass_short"],
            ["seagrass_tall_top_a", "seagrass_tall_bot_a"], ["kelp_top", "kelp_b", "kelp_a"]]
    hmax = 3 * 256
    imgs = []
    for t in range(FR):
        canvas = np.zeros((hmax, len(cols) * 256, 3))
        for i, stack in enumerate(cols):
            y0 = hmax - 256 * len(stack)
            for j, k in enumerate(stack):
                canvas[y0 + j * 256: y0 + (j + 1) * 256, i * 256:(i + 1) * 256] = tile(k, t)
        imgs.append(Image.fromarray(canvas.astype(np.uint8)).resize((len(cols) * 128, hmax // 2), Image.LANCZOS))
    imgs[0].save(ROOT / "_docs/flora/SWAY-PREVIEW.gif", save_all=True, append_images=imgs[1:], duration=200, loop=0)
    for r in rep:
        print(r)


if __name__ == "__main__":
    main()
