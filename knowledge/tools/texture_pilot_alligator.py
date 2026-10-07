#!/usr/bin/env python3
"""texture_pilot_alligator.py — TEXTURE PILOT (his "Go on all" item 4, D-C309 / D-C315): one creature re-textured from licensed
sources, painted onto ITS OWN UV layout, with a per-asset provenance ledger. PREVIEW ONLY — nothing goes into a pack until his eye
says so. Creature: the alligator (sf_nba:alligator, StripMine creature drawn by RP-07; box UV, 128 x 128).

Method (every colour is computed; from the old sheet we keep only its CUT-OUT SHAPE (alpha) and the eye / tooth / mouth LOCATIONS):
  0 the SHAPE: the old sheet's alpha, x4 nearest, everywhere. The model is built around it: the back crest and tail crest are
    thin boxes whose sides are cut into spikes, the teeth are cut out of two thin boxes around the jaws, and the feet are flat
    cut-out claws. (v1 of this pilot painted every face solid and lost all of that — the crest became a slab.)
  1 the texel's place on the model: every cube face of the rest geometry is rasterised in UV space; a texel's centre maps to a
    point on the model surface (Bedrock's face placement, bb_truth) and gets that face's outward direction.
  2 the material by body region + direction: DORSAL armour (upward faces of body / tail), CREST (the spiked crest boxes), FLANK
    (sideways faces, pale below a wavy line like a real alligator's countershading), BELLY (downward), HEAD (skull / snout),
    THROAT (lower jaw underside), LIMBS (legs / feet).
  3 the pattern is sampled in MODEL space (the face's own plane, model px), so scales keep one size across every box face:
      - belly / flank / limb / throat scales = ambientCG Leather008 (CC0; alligator-style belly leather) height map, pre-filtered
        to the texel size (v1 point-sampled it: the grooves aliased into a "cracked plaster" look) + a groove mask so the plate
        edges stay crisp at 4 texels per model pixel
      - dorsal armour = procedural keeled scutes in straight transverse rows (the keels line up into ridges along the back, as on a
        real alligator); Leather008 as fine grain
      - head = procedural small tubercles + Leather008 grain
    colour = a two-tone ramp per region by height (grooves dark, crowns light) — tones picked by eye from reference photos of
    American alligators (visual targets only, never sampled).
  4 eyes / teeth / mouth: their places come from the old sheet's colours; repainted (yellow iris + black slit pupil, cream teeth,
    pale pink-cream mouth with palate ridges), not copied.
Outputs (_docs/texture_pilot/): alligator_pilot.png (512 x 512), ALLIGATOR-PILOT.png (old vs pilot, 3 views + the flat sheets),
ALLIGATOR-PILOT-CLOSE.png (front-east, large). The ledger: PROVENANCE.md."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV
from equine_compare import bone_affines

ROOT = Path("/home/claude"); RP = ROOT / "_build/rp07-1429"; OUT = ROOT / "_docs/texture_pilot"
SRC = ROOT / "_intake/texture_pilot/ambientcg/Leather008"
SCALE = 4                                    # 128 -> 512
UVW = 128
PLATE_SRC = 100.0                            # a Leather008 plate is ~100 source px wide (1024 px map; measured on the colour map)
GROOVE_T = 0.5                               # displacement below this = the groove between plates (~7 % of the map)


def load_geo():
    d = ML._parse_json((RP / "models/entity/sf/nba/alligator.geo.json").read_text(encoding="utf-8"))
    return d["minecraft:geometry"][0]


H = None
MIPS = {}


def height_map():
    h = np.asarray(Image.open(SRC / "Leather008_1K-JPG_Displacement.jpg").convert("L")).astype(float) / 255.0
    return (h - h.min()) / (np.ptp(h) or 1.0)


def mip(f):
    """the height map and its groove mask, box-filtered so one texel sees f source px (no aliasing)"""
    key = round(max(f, 1.0), 2)
    if key not in MIPS:
        n = max(16, int(round(H.shape[0] / key)))
        hs = np.asarray(Image.fromarray((H * 255).astype(np.uint8)).resize((n, n), Image.BOX)).astype(float) / 255.0
        gs = np.asarray(Image.fromarray(((H < GROOVE_T) * 255).astype(np.uint8)).resize((n, n), Image.BOX)).astype(float) / 255.0
        lo, hi = np.percentile(hs, 5), np.percentile(hs, 95)
        MIPS[key] = (np.clip((hs - lo) / ((hi - lo) or 1.0), 0, 1), gs, n / H.shape[0])
    return MIPS[key]


def bilinear(m, x, y):
    n = m.shape[0]
    x0 = np.floor(x).astype(int) % n; y0 = np.floor(y).astype(int) % n; x1 = (x0 + 1) % n; y1 = (y0 + 1) % n
    fx = x - np.floor(x); fy = y - np.floor(y)
    return m[y0, x0] * (1 - fx) * (1 - fy) + m[y0, x1] * fx * (1 - fy) + m[y1, x0] * (1 - fx) * fy + m[y1, x1] * fx * fy


def leather(a, b, plate):
    """Leather008 plates `plate` model px wide (a = across the plate columns, b = along them); crisp grooves"""
    k = PLATE_SRC / plate                    # source px per model px
    hs, gs, s = mip(k / SCALE)               # source px per texel
    x, y = a * k * s, b * k * s
    h = bilinear(hs, x, y); g = bilinear(gs, x, y)
    return np.clip(h * (1.0 - np.clip(g * 2.2, 0, 1) * 0.85), 0, 1)


def hash2(i, j, s):
    v = np.sin(i * 12.9898 + j * 78.233 + s * 37.719) * 43758.5453
    return v - np.floor(v)


def vnoise1(z, period, seed):
    i = np.floor(z / period); f = z / period - i; f = f * f * (3 - 2 * f)
    return hash2(i, 0.0, seed) * (1 - f) + hash2(i + 1, 0.0, seed) * f


def vnoise2(a, b, cell, seed):
    i = np.floor(a / cell); j = np.floor(b / cell); fa = a / cell - i; fb = b / cell - j
    fa = fa * fa * (3 - 2 * fa); fb = fb * fb * (3 - 2 * fb)
    return (hash2(i, j, seed) * (1 - fa) * (1 - fb) + hash2(i + 1, j, seed) * fa * (1 - fb)
            + hash2(i, j + 1, seed) * (1 - fa) * fb + hash2(i + 1, j + 1, seed) * fa * fb)


def countershade(h_dark, h_pale, yy, zz, ybot, hgt, level, seed):
    """dark above, pale below an irregular line at `level` of the face height; the edge breaks into blotches (reptile skin)"""
    line = ybot + hgt * (level + 0.10 * (2 * vnoise1(zz, 3.0, seed) - 1) + 0.05 * (2 * vnoise1(zz, 1.1, seed + 1) - 1))
    m = 2 * vnoise2(yy, zz, 1.2, seed + 2) - 1                                          # blotches ~1 px, not drips
    k = np.clip(((yy - line) + 0.7 * m) / 0.55 + 0.5, 0, 1)[..., None]                   # 0 = pale, 1 = dark
    shade = (1.08 - 0.25 * np.clip((yy - ybot) / max(hgt, 1.0), 0, 1))[..., None]
    return ramp("pale", h_pale) * (1 - k) + ramp("flank", h_dark) * shade * k


def scutes(a, b):
    """dorsal armour: keeled scutes in straight transverse rows (b = along the body, a = across; model px). The columns are
    centred on the midline so the middle keel runs under the crest; the keels line up into ridges along the back."""
    row, colw = 2.4, 2.2
    j = np.floor(b / row)
    ab = a + (hash2(j, 0, 5) - 0.5) * 0.25                        # a slight sideways jitter per row
    i = np.floor(ab / colw + 0.5)
    da = (ab - i * colw) / (colw * 0.5); db = (b - (j + 0.5) * row) / (row * 0.5)
    plate = np.clip(1.0 - (np.abs(da) ** 4 + np.abs(db) ** 3), 0, 1) ** 0.45
    keel = np.clip(1.0 - np.abs(da) * 3.2, 0, 1) * np.clip(1.15 - np.abs(db) * 0.9, 0, 1)
    big = 0.75 + 0.25 * np.clip(1.0 - np.abs(i) / 3.0, 0, 1)      # the middle columns carry the tallest keels
    return np.clip(0.6 * plate + 0.45 * keel * plate * big * (0.75 + 0.25 * hash2(i, j, 3)), 0, 1)


def tubercles(a, b):
    """head skin: small round bumps, offset rows, jittered"""
    row = 1.7; col = 1.5
    j = np.floor(b / row); off = (j % 2) * 0.5
    i = np.floor(a / col + off)
    ca = (i + 0.5 - off) * col + (hash2(i, j, 1) - 0.5) * 0.4; cb = (j + 0.5) * row + (hash2(i, j, 2) - 0.5) * 0.3
    da = (a - ca) / (col * 0.5); db = (b - cb) / (row * 0.5)
    return np.clip(1.0 - (da ** 2 + db ** 2), 0, 1) ** 0.6


PAL = {  # region: (groove, crown) RGB — by eye from reference photos of adult American alligators (dark armour, cream belly)
    "dorsal": ((18, 21, 15), (80, 86, 60)),
    "crest": ((8, 9, 6), (44, 48, 33)),
    "flank": ((24, 27, 19), (90, 92, 64)),
    "pale": ((128, 120, 88), (206, 198, 164)),       # the lower flank below the countershading line
    "belly": ((142, 132, 96), (228, 220, 188)),
    "head": ((22, 25, 18), (86, 90, 63)),
    "throat": ((150, 140, 104), (230, 222, 192)),
    "limb": ((22, 24, 17), (80, 82, 58)),
}
CREST = {"body": 11.99, "tail": 7.99, "tail2": 7.99}          # crest boxes sit on top of these bones' main boxes


def region(bone, up, down, ymin, ymax):
    # a crest face lies wholly above the main box's top AND rises above it (the main box's own top face is flat AT that height)
    if bone in CREST and ymin >= CREST[bone] and ymax >= CREST[bone] + 0.5: return "crest"
    if bone == "lower_jaw": return "throat" if down else "head"
    if bone in ("skull", "snout"): return "head"
    if bone in ("left_arm", "right_arm", "left_leg", "right_leg", "left_hand", "right_hand", "left_foot", "right_foot"): return "limb"
    if up: return "dorsal"
    if down: return "belly"
    return "flank"


def ramp(reg, h):
    lo, hi = (np.array(c, float) for c in PAL[reg])
    return lo[None, None] + (hi - lo)[None, None] * np.clip(h, 0, 1)[..., None] ** 1.2


def paint(geo, old):
    global H
    H = height_map()
    tw, th = geo["description"]["texture_width"], geo["description"]["texture_height"]
    faces = truth_posed_faces(geo["bones"], tw, th, bone_affines(geo["bones"]))
    N = UVW * SCALE
    col = np.zeros((N, N, 3)); owner = np.full((N, N), -1)
    oldA = np.asarray(old.convert("RGBA").resize((N, N), Image.NEAREST)).astype(float)
    for fi, f in enumerate(faces):
        u0, v0, u1, v1 = [q * N for q in f.uv]
        ua, ub = sorted((u0, u1)); va, vb = sorted((v0, v1))
        if ub - ua < 0.5 or vb - va < 0.5: continue
        xs = np.arange(int(np.floor(ua)), int(np.ceil(ub))); ys = np.arange(int(np.floor(va)), int(np.ceil(vb)))
        X, Y = np.meshgrid(xs + 0.5, ys + 0.5)
        inside = (X >= ua) & (X <= ub) & (Y >= va) & (Y <= vb)
        s = (X - u0) / (u1 - u0); t = (Y - v0) / (v1 - v0)
        P = np.array(f.pts, float)                         # corners at (u0,v0) (u1,v0) (u1,v1) (u0,v1)
        pos = (P[0][None, None] * ((1 - s) * (1 - t))[..., None] + P[1][None, None] * (s * (1 - t))[..., None]
               + P[2][None, None] * (s * t)[..., None] + P[3][None, None] * ((1 - s) * t)[..., None])
        nrm = np.cross(P[1] - P[0], P[3] - P[0]); nn = np.linalg.norm(nrm)
        nrm = nrm / nn if nn > 1e-9 else np.array([0.0, 1.0, 0.0])
        up, down = nrm[1] > 0.7, nrm[1] < -0.7
        reg = region(f.bone, up, down, float(P[:, 1].min()), float(P[:, 1].max()))
        # the plane's own axes in model px: up/down faces (x across, z along), sides (y height, z along), ends (x, y)
        if abs(nrm[1]) > 0.7: a_, b_ = pos[..., 0], pos[..., 2]
        elif abs(nrm[0]) > 0.7: a_, b_ = pos[..., 1], pos[..., 2]
        else: a_, b_ = pos[..., 0], pos[..., 1]
        if reg == "dorsal": c = ramp(reg, 0.85 * scutes(a_, b_) + 0.15 * leather(a_, b_, 0.8))
        elif reg == "crest":                                 # the spikes: darkest armour, the tips a touch lighter
            tip = np.clip((pos[..., 1] - float(P[:, 1].min())) / max(float(np.ptp(P[:, 1])), 1.0), 0, 1)
            c = ramp(reg, 0.12 + 0.5 * tip ** 1.5 + 0.15 * leather(a_, b_, 0.8))
        elif reg == "belly": c = ramp(reg, leather(a_, b_, 2.6))                   # ~5 plate columns across the belly
        elif reg == "throat": c = ramp(reg, 0.35 + 0.65 * leather(a_, b_, 2.0))
        elif reg == "head":
            h = 0.5 * leather(a_, b_, 1.4) + 0.5 * tubercles(a_, b_)
            side = abs(nrm[1]) < 0.7 and f.bone in ("skull", "lower_jaw") and float(P[:, 1].max()) <= 7.01
            if side:                                         # the jaw line: pale lower half, like the old art and a real alligator
                c = countershade(h, leather(a_, b_, 2.0), pos[..., 1], pos[..., 0] + pos[..., 2], float(P[:, 1].min()),
                                 float(np.ptp(P[:, 1])), 0.5, 21)
            else: c = ramp(reg, h)
        elif reg == "limb": c = ramp(reg, 0.55 * leather(b_, a_, 1.8) + 0.45 * tubercles(a_ * 0.8, b_ * 0.8))
        else:                                                # flank: dark above, pale below an irregular line (countershading)
            along = pos[..., 2] if abs(nrm[0]) > 0.7 else pos[..., 0]
            h = leather(along, pos[..., 1], 2.4)             # plate columns upright: transverse bands down the side
            c = countershade(h, h, pos[..., 1], along, float(P[:, 1].min()), float(np.ptp(P[:, 1])), 0.32, 11)
        take = inside & (owner[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1] < 0)
        sl = (slice(ys[0], ys[-1] + 1), slice(xs[0], xs[-1] + 1))
        col[sl][take] = c[take]; owner[sl][take] = fi
    # 0 the SHAPE: the old cut-outs, exactly
    alpha = oldA[..., 3].copy()
    orphan = (alpha > 0) & (owner < 0)                       # old texels on no face (never drawn): a neutral dark
    col[orphan] = (40, 42, 30)
    # 4 eyes / teeth / mouth: LOCATIONS from the old colours, repainted
    r, g, b = oldA[..., 0], oldA[..., 1], oldA[..., 2]
    eye = (r > 170) & (g > 140) & (b < 90) & (alpha > 0)
    mouth = (r > g + 40) & (r > 120) & (alpha > 0)
    tooth = (r > 180) & (g > 170) & (b > 120) & (alpha > 0) & ~eye
    yy = np.mgrid[0:N, 0:N][0].astype(float)
    ridge = 0.9 + 0.1 * np.cos(2 * np.pi * yy / (1.0 * SCALE))                # palate ridges, one per model px
    col[mouth] = (np.array([214, 172, 148])[None] * ridge[mouth][:, None])
    col[tooth] = (234, 228, 204)
    col[eye] = (208, 164, 36)
    # the slit pupil: one per eye patch on each face (the eye wraps from the front face onto the side face)
    for fi in sorted(set(owner[eye].tolist())):
        if fi < 0: continue
        m = eye & (owner == fi)
        ys_, xs_ = np.nonzero(m)
        rows = np.arange(ys_.min(), ys_.max() + 1)
        gap = [x for x in range(xs_.min(), xs_.max() + 1) if not m[rows, x].any()]
        if gap:                              # the old eye leaves a texel between two yellow ones: that is where the pupil goes
            g0, g1 = min(gap), max(gap) + 1
            for x in range(g0, g1): col[rows, x] = (208, 164, 36)
            cx = (g0 + g1) // 2
            m = m.copy(); m[rows, g0:g1] = True; eye[rows, g0:g1] = True
        else:
            cx = int(round((xs_.min() + xs_.max() + 1) / 2.0))
        for x in (cx - 1, cx):
            if 0 <= x < N: col[m[:, x], x] = (18, 14, 8)
        top = ys_.min()
        col[top, xs_.min():xs_.max() + 1] = np.where(m[top, xs_.min():xs_.max() + 1, None],
                                                    np.minimum(col[top, xs_.min():xs_.max() + 1] * 1.15, 255), col[top, xs_.min():xs_.max() + 1])
    img = np.dstack([np.clip(col, 0, 255), alpha]).astype(np.uint8)
    return Image.fromarray(img, "RGBA"), faces


def render(geo, texp, view, W=520, H_=360, faces_all=None, pad=1.1):
    tw, th = geo["description"]["texture_width"], geo["description"]["texture_height"]
    faces = truth_posed_faces(geo["bones"], tw, th, bone_affines(geo["bones"]))
    e, t = camera(faces_all or faces, view, pad=pad)
    return render_entity(faces, texp, e, t, W, H_, fov=FOV, floor_y=0.0).convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    geo = load_geo(); oldp = RP / "textures/sf/nba/entity/alligator/alligator.png"
    pilot, _ = paint(geo, Image.open(oldp)); pp = OUT / "alligator_pilot.png"; pilot.save(pp)
    oa = np.asarray(Image.open(oldp).convert("RGBA").resize((512, 512), Image.NEAREST))[..., 3]
    na = np.asarray(pilot)[..., 3]
    print("alpha identical to the old sheet x4:", bool((oa == na).all()))
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    views = [("front-east", "front-east"), ("east", "side (east)"), ("top", "from above")]
    W, H_ = 520, 360
    sheet = Image.new("RGB", (3 * (W + 4) - 4, 2 * (H_ + 24) + 24 + 512 + 30), (240, 240, 240)); d = ImageDraw.Draw(sheet)
    for r, (lab, tp) in enumerate((("NOW (StripMine sheet, 128 px)", oldp), ("PILOT v4 (CC0 scales + procedural armour, 512 px)", pp))):
        for c, (v, vn) in enumerate(views):
            x0, y0 = c * (W + 4), r * (H_ + 24)
            d.text((x0 + 4, y0 + 4), f"{lab} — {vn}", fill=(10, 10, 10), font=F)
            sheet.paste(render(geo, tp, v, W, H_), (x0, y0 + 22))
    y0 = 2 * (H_ + 24) + 6
    d.text((4, y0), "the flat sheets: now (x4 nearest) | pilot v4   (checker = transparent: the same cut-outs in both)", fill=(10, 10, 10), font=F)
    yy, xx = np.mgrid[0:512, 0:512]; chk = (((yy // 8) + (xx // 8)) % 2 * 40 + 200).astype(np.uint8)
    bg = Image.fromarray(np.dstack([chk, chk, chk, np.full_like(chk, 255)]), "RGBA")
    sheet.paste(Image.alpha_composite(bg, Image.open(oldp).convert("RGBA").resize((512, 512), Image.NEAREST)).convert("RGB"), (0, y0 + 24))
    sheet.paste(Image.alpha_composite(bg, pilot).convert("RGB"), (520, y0 + 24))
    sheet.save(OUT / "ALLIGATOR-PILOT.png")
    close = Image.new("RGB", (2 * 900 + 8, 560 + 24), (240, 240, 240)); d = ImageDraw.Draw(close)
    for c, (lab, tp) in enumerate((("NOW", oldp), ("PILOT v4", pp))):
        d.text((c * 908 + 4, 4), f"{lab} — front-east, close", fill=(10, 10, 10), font=F)
        close.paste(render(geo, tp, "front-east", 900, 560, pad=0.8), (c * 908, 22))
    close.save(OUT / "ALLIGATOR-PILOT-CLOSE.png")
    print(pp, OUT / "ALLIGATOR-PILOT.png", OUT / "ALLIGATOR-PILOT-CLOSE.png")


if __name__ == "__main__":
    main()
