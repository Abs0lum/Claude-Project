#!/usr/bin/env python3
"""ramp231_render.py — round 231 (RAMPS): before / after renders of the 8-block street ramp, at player height, with a
low sun and a shadow map (a stand-in for Vibrant Visuals' sun shadows — NOT the engine; a witness decides).

Pieces: the v_ramp8 street piece between v_straight1 pieces, every block from its shipped / staged geometry (BP-02 1.3.230
SLIM block JSONs, RP-13 1.0.1 + RP-04 1.3.159 models and textures, or the staged v9 models), through tools/civ_render.py
(X-mirror law, transformation law, alpha_test 0.5).

  BEFORE  = shipped geometry with the 'fills' planes NOT drawn (what his 02:43 shots show: the planes do not appear from the
            street side) + the terrain left over the lane by a DOWN-ramp placement (structure void, kitPrep from H + 1).
  AFTER   = staged v9 geometry (tooth columns, flush boards) + the fixed structure (air over the lane).
  H-S1    = BEFORE, but the fills planes cast shadows as full 16 x 16 quads (the hypothesis that the VV shadow pass ignores
            their alpha) — shown for comparison with his shadow bands only.
Usage: ramp231_render.py OUTDIR"""
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

os.environ["PW_STACK"] = "final"
sys.path.insert(0, "/home/claude/tools")
import civ_render as CR  # noqa: E402
import block_render as BR  # noqa: E402
import mcstructure as M  # noqa: E402

B = Path("/home/claude/_build")
STAGE = Path("/home/claude/_staging/ramps231")
ROAD = B / "bp02-230/structures/pw/road"
CR.BP = B / "bp02-230/blocks"
SHIPPED_MODELS = [B / "rp13-101/models/blocks", B / "rp04-159/models/blocks"]
V9_MODELS = [STAGE / "rp13/models/blocks", STAGE / "rp04/models/blocks"] + SHIPPED_MODELS
for d in (B / "rp04-159/textures/blocks", B / "rp13-101/textures/blocks"):
    for f in d.glob("pw_*.png"):
        if not f.stem.endswith(("_n", "_mer")):
            CR._tex.setdefault(f.stem, np.asarray(Image.open(f).convert("RGBA")).astype(np.float32) / 255.0)
_gs = Image.open(B / "rp04-159/textures/blocks/grass_block_side_v0.tga").convert("RGBA")
CR._tex["grass_side"] = np.asarray(_gs).astype(np.float32) / 255.0
for _n in ("minecraft:stone_brick_stairs", "pw:seated_stone_brick_stairs", "minecraft:stone_brick_slab", "minecraft:smooth_stone_slab"):
    CR.VCOL[_n] = (120, 120, 124)                     # the renderer has no stair shapes: the curb stairs as grey blocks (layout only)
    if "slab" in _n:
        CR.VTHIN[_n] = (-8, 0, -8, 16, 8, 16)
SUN = np.array([-0.55, 0.42, 0.72]); SUN /= np.linalg.norm(SUN)     # low afternoon sun from the west-south-west (scene frame)


def piece_blocks(path, ox, oy, oz, ylo=10, extra=None):
    st = M.Structure.from_bytes(path.read_bytes()); out = []
    sx, sy, sz = st.size
    for x in range(sx):
        for y in range(ylo, sy):
            for z in range(sz):
                e = st.get(x, y, z)
                if e is None and extra:
                    e2 = extra(x, y, z)
                    if e2:
                        out.append([ox + x, oy + y, oz + z, e2, {}])
                    continue
                if not e or e[0] in ("minecraft:air", "minecraft:structure_void"):
                    continue
                out.append([ox + x, oy + y, oz + z, e[0], {k: getattr(v, "value", v) for k, v in e[1].items()}])
    return out, sx


def street(ramp_path, leftover):
    """lower straights (x 0..3), the ramp (x 4..11) rising +x, upper straights (x 12..15); hill banks beside the corridor.
    leftover: the down-ramp remnant at the ramp's top layer over the lane (grass where the old ground stood at H, dirt where
    it was cut down or drained) — None for the fixed piece."""
    blocks, x = [], 0
    for _ in range(4):
        b, n = piece_blocks(ROAD / "v_straight1.mcstructure", x, 0, 0); blocks += b; x += n
    rem = (lambda px, py, pz: ("minecraft:grass_block" if (px + 2 * pz) % 5 < 2 else "minecraft:dirt") if py == 15 and 4 <= pz <= 8 else None) if leftover else None
    b, n = piece_blocks(ramp_path, x, 0, 0, extra=rem); blocks += b; x += n
    for _ in range(4):
        b, n = piece_blocks(ROAD / "v_straight1.mcstructure", x, 1, 0); blocks += b; x += n
    for bx in range(x):                                  # banks: grass at the sidewalk level beside the corridor
        top = 14 if bx < 4 else 15
        for z in (-2, -1, 13, 14):
            for y in range(11, top + 1):
                blocks.append([bx, y, z, "minecraft:grass_block" if y == top else "minecraft:dirt", {}])
    return blocks


def faces_for(blocks, models, drop_fills):
    CR.RP_MODELS = models
    CR._geo_cache.clear()
    items = CR.scene({"datum_y": 10, "blocks": blocks}, min_feet=0)
    if drop_fills:
        items = [it for it in items if it[0].bone != "fills"]
    return items


def raster(items, proj, W, H, want_world, alpha=True, skip=None):
    """z-buffer raster; proj(p) -> (sx, sy, depth); returns depth, colour, world pos, face-normal index"""
    zbuf = np.full((H, W), np.inf, np.float32)
    col = np.zeros((H, W, 3), np.float32)
    wpos = np.zeros((H, W, 3), np.float32) if want_world else None
    nrm = np.zeros((H, W, 3), np.float32) if want_world else None
    for idx, (f, tex, dim_on) in enumerate(items):
        if skip and skip(f):
            continue
        P = np.array(f.pts, float)
        pr = [proj(p) for p in P]
        if any(z <= 0.5 for _, _, z in pr):
            continue
        n = np.cross(P[1] - P[0], P[3] - P[0]); ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        n /= ln
        th_, tw_ = tex.shape[:2]
        u0, v0, u1, v1 = f.uv
        uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        for tri in ((0, 1, 2), (0, 2, 3)):
            xs = np.array([pr[i][0] for i in tri]); ys = np.array([pr[i][1] for i in tri]); zs = np.array([pr[i][2] for i in tri])
            xmin, xmax = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
            ymin, ymax = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
            if xmin > xmax or ymin > ymax:
                continue
            det = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
            if abs(det) < 1e-9:
                continue
            X, Y = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
            l0 = ((xs[1] - X) * (ys[2] - Y) - (xs[2] - X) * (ys[1] - Y)) / det
            l1 = ((xs[2] - X) * (ys[0] - Y) - (xs[0] - X) * (ys[2] - Y)) / det
            l2 = 1 - l0 - l1
            inside = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
            if not inside.any():
                continue
            w = np.stack([l0 / zs[0], l1 / zs[1], l2 / zs[2]])
            z = 1.0 / w.sum(0)
            us = np.array([uvs[i][0] for i in tri]); vs = np.array([uvs[i][1] for i in tri])
            u = (w * us[:, None, None]).sum(0) * z; v = (w * vs[:, None, None]).sum(0) * z
            tx = np.clip((u * tw_).astype(int), 0, tw_ - 1); ty = np.clip((v * th_).astype(int), 0, th_ - 1)
            texel = tex[ty, tx]
            ok = inside & (z < zbuf[ymin:ymax + 1, xmin:xmax + 1])
            if alpha:
                ok &= texel[..., 3] >= 0.5
            zbuf[ymin:ymax + 1, xmin:xmax + 1][ok] = z[ok]
            dim = BR.DIM[f.name] if dim_on else 1.0
            col[ymin:ymax + 1, xmin:xmax + 1][ok] = (texel[..., :3] * dim)[ok]
            if want_world:
                Pw = np.array([P[i] for i in tri])
                wp = np.einsum("kij,kc->ijc", w, Pw) * z[..., None]
                wpos[ymin:ymax + 1, xmin:xmax + 1][ok] = wp[ok]
                nrm[ymin:ymax + 1, xmin:xmax + 1][ok] = n
    return zbuf, col, wpos, nrm


def shadow_map(items, center, size=2048, extent=30 * 16, full_fills=False):
    """orthographic depth map along -SUN; fills drawn with alpha (normal) or as full quads (H-S1)"""
    fwd = -SUN
    r = np.cross(fwd, [0, 1, 0]); r /= np.linalg.norm(r); up = np.cross(r, fwd)
    c = np.array(center, float)
    s = size / (2 * extent)

    def proj(p):
        d = np.array(p, float) - c
        return (size / 2 + (d @ r) * s, size / 2 - (d @ up) * s, (d @ fwd) + 4000)
    if full_fills:
        solid = np.ones((2, 2, 4), np.float32)
        its = [(f, solid if f.bone == "fills" else t, d) for f, t, d in items]
    else:
        its = items
    zb, _, _, _ = raster(its, proj, size, size, False)
    return zb, proj, s


def shade(items, eye, target, sm, W=1200, H=540, fov=70):
    cam = BR.Cam(eye, target, W, H, fov)
    zb, col, wp, nrm = raster(items, cam.project, W, H, True)
    zmap, sproj, s = sm
    hit = np.isfinite(zb)
    out = np.zeros((H, W, 3), np.float32); out[:] = np.array([150, 185, 220], np.float32) / 255
    ys, xs = np.nonzero(hit)
    P = wp[ys, xs]; N = nrm[ys, xs]
    toward = np.array(eye) - P
    flip = (N * toward).sum(1) < 0
    N[flip] *= -1                                         # double-sided faces: the normal toward the camera
    lam = np.clip(N @ SUN, 0, 1)
    sx = np.array([sproj(p)[0] for p in P]).astype(int); sy = np.array([sproj(p)[1] for p in P]).astype(int)
    sd = np.array([sproj(p)[2] for p in P])
    okm = (sx >= 0) & (sx < zmap.shape[1]) & (sy >= 0) & (sy < zmap.shape[0])
    lit = np.ones(len(P), bool)
    bias = 0.35 + 0.6 * (1 - lam)
    lit[okm] = sd[okm] <= zmap[sy[okm], sx[okm]] + bias[okm]
    light = 0.38 + 0.72 * lam * lit
    out[ys, xs] = np.clip(col[ys, xs] * light[:, None], 0, 1)
    return (out * 255).astype(np.uint8)


def label(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, im.width, 22), fill=(0, 0, 0))
    d.text((8, 5), text, fill=(255, 255, 255))
    return im


def main(outdir):
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    before_blocks = street(ROAD / "v_ramp8.mcstructure", leftover=True)
    after_blocks = street(STAGE / "bp02/structures/pw/road/v_ramp8.mcstructure", leftover=False)
    before = faces_for(before_blocks, SHIPPED_MODELS, drop_fills=True)
    geo_blocks = after_blocks                            # symptom 2 views: the same (fixed) blocks, only the geometry differs
    geo_before = faces_for(geo_blocks, SHIPPED_MODELS, drop_fills=True)
    before_full = faces_for(geo_blocks, SHIPPED_MODELS, drop_fills=False)
    after = faces_for(after_blocks, V9_MODELS, drop_fills=False)
    assert not any(f.bone == "fills" for f, _, _ in after), "v9 still has fills"
    center = (10 * 16, 15 * 16, 6 * 16)
    sm_b = shadow_map(before, center); sm_a = shadow_map(after, center); sm_g = shadow_map(geo_before, center)
    sm_h = shadow_map(before_full, center, full_fills=True)
    # scene frame: +x = travel up the ramp, lane z 4..8, curbs z 3 / 9, sidewalks z 0..2 / 10..12 (v width)
    shots = {
        "dirt": ("player at the ramp's foot on the lane, eye 1.62, facing up the ramp (+x)",
                 (1.5 * 16, (14 + 1.62) * 16, 6.5 * 16), (12 * 16, 15.2 * 16, 6.5 * 16)),
        "curb": ("on the lane 2 blocks from the curb, eye 1.62, facing the curb wall (-z, oblique +x)",
                 (9.5 * 16, (14.7 + 1.62) * 16, 6.2 * 16), (12.0 * 16, 15.3 * 16, 3.9 * 16)),
        "seams": ("on the low sidewalk looking up the sidewalk ramp (+x), eye 1.62",
                  (2.0 * 16, (15 + 1.62) * 16, 11.5 * 16), (12 * 16, 15.9 * 16, 11.0 * 16)),
    }
    made = []
    for key, (desc, eye, tgt) in shots.items():
        bf, bsm = (before, sm_b) if key == "dirt" else (geo_before, sm_g)
        b = label(Image.fromarray(shade(bf, eye, tgt, bsm)), f"BEFORE (shipped 1.3.230 + RP-13 1.0.1) - {desc}")
        a = label(Image.fromarray(shade(after, eye, tgt, sm_a)), f"AFTER (staged ramps231: air over the lane, v9 tooth columns, flush boards) - {desc}")
        sheet = Image.new("RGB", (b.width, b.height * 2 + 6), (20, 20, 24)); sheet.paste(b, (0, 0)); sheet.paste(a, (0, b.height + 6))
        p = outdir / f"RAMPS231-{key}-before-after.png"; sheet.save(p); made.append(p)
    desc, eye, tgt = shots["curb"]
    h = label(Image.fromarray(shade(geo_before, eye, tgt, sm_h)), "HYPOTHESIS H-S1: the fills planes cast shadows as full 16x16 quads (alpha ignored in the shadow pass)")
    b = label(Image.fromarray(shade(geo_before, eye, tgt, sm_g)), "BEFORE, fills cast nothing (alpha respected) - same camera")
    sheet = Image.new("RGB", (h.width, h.height * 2 + 6), (20, 20, 24)); sheet.paste(b, (0, 0)); sheet.paste(h, (0, h.height + 6))
    p = outdir / "RAMPS231-shadow-hypothesis.png"; sheet.save(p); made.append(p)
    for p in made:
        print(p)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/_staging/ramps231/renders")
