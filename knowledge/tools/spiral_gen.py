#!/usr/bin/env python3
"""spiral_gen.py — Program 228: the SPIRAL STAIRCASE, iteration 1 (his 12:47 spec, images first).

His spec (2026-10-06 12:47 CT): "The key to a spiral staircase is the curved spiral railing that's attached to the outer
edge of the stairs; and that the bottom of the stairs curve upward to the top and are set to seamlessly meet the next set.
If they're custom stairs, they'll be 'bent' through the box and need custom collision boxes and geometry, and will need to
be a set of at least 4 to correctly approximate the bend through 4 boxes (maybe even 5 ...) — perhaps 5 or 6 boxes."
Ruling: spiral blocks ONLY may use block format >= 1.21.130 (multi-box collision); everything else stays 1.21.80.

THE MODEL (one design = one continuous helix, cut into block cells):
  * The helix centre sits on a GRID CORNER, so each quarter turn is a square quadrant of cells, all at the same block
    level: quadrant q (q = 0..3) of turn t lies one block above quadrant q-1. A full turn rises 4 blocks (64 px).
    The other three quadrants are the SAME blocks turned 90/180/270 (minecraft:cardinal_direction) — rotating a cell
    about the helix corner lands exactly on another grid cell.
  * 16 treads per turn (4 per quadrant, 22.5 deg each), 4 px rise each (auto-step).
  * Helix line h(theta) = 16 * theta / 90 px within a quadrant; tread k top = 4(k+1).
  * Treads: radial boxes (segments <= SEG px long) from the newel to the outer radius, D px deep, closed risers.
  * Soffit (his "bottom curves upward"): a 1 px plate per tread per radial segment, its top on h(theta) - D, pitched at
    atan(rise / arc) for its own radius — consecutive plates meet end to end, so the underside is one continuous helix
    that runs into the next quadrant / next block level without a step.
  * Outer string: a pitched band at the outer radius from h - D - 1 to h + 1 (a cut string: the tread ends show above).
  * Handrail (his "curved spiral railing attached to the outer edge"): a 2 x 2 px rail pitched along the helix at the
    outer edge, RAIL px above the helix line, carried by 2 balusters per tread.
  * Newel: each quadrant's inner cell carries a quarter of the post (so the 4 quadrants make one whole post).
Every element is ONE cube in ONE bone: bone = y-rotation about the element's own centre, cube = its single-axis pitch
about the same centre (both single-axis, the form our shipped roof hips already use), so every cube's raw origin sits
where it is drawn (bounds checks see the real position whichever way the engine checks).

Coordinates: geometry FILE frame (x mirrored vs world — the hand flips in game; both hands are generated later).
Design frame = file frame, units px (16 = 1 block), helix centre at (0, 0), quadrant 0 = theta 0..90 deg = +x..+z.

Usage: spiral_gen.py OUTDIR   -> geometry files + collision JSON + bounds report + preview renders for each design.
"""
import json, math, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import block_render as BR

TEX = Path("/home/claude/_build/rp04-159/textures/blocks")


def _tex(stem, frame=0):
    key = (stem, frame)
    if key in BR._texcache: return BR._texcache[key]
    rot = 0
    if "@r" in stem: stem, rot = stem.split("@r")[0], int(stem.split("@r")[1])   # a derived texture: the Patrix tile turned
    im = Image.open(TEX / (stem + ".png")).convert("RGBA")
    if rot: im = im.rotate(-rot, expand=True)
    if im.height > im.width: im = im.crop((0, 0, im.width, im.width))
    a = np.asarray(im).astype(np.float32) / 255.0
    BR._texcache[key] = a
    return a


BR.texture = _tex

# ---------------------------------------------------------------- designs
DESIGNS = {
    # name: (r0 newel radius, r1 outer tread radius, quadrant cells n x n)
    "A_turret": dict(r0=3.0, r1=15.0, n=1, label="A · turret (1 block per quarter turn, 2x2 well)"),
    "B_tower": dict(r0=3.5, r1=31.0, n=2, label="B · tower (4 blocks per quarter turn, 4x4 well)"),
    "C_grand": dict(r0=5.0, r1=46.0, n=3, label="C · grand (8 blocks per quarter turn, 6x6 well)"),
}
TREADS_Q = 4            # treads per quadrant
RISE = 4.0              # px per tread
D = 5.0                 # tread depth (top to the soffit line); 5 keeps every cell <= 30 px tall
SEG = 6.0               # max radial segment length
RAIL = 14.5            # rail centre above the helix line (hand height ~0.9 of a 1.8-block player); tops past y 30 carry
OVL = 0.25              # overlap between neighbouring pitched pieces


def helix(th):          # th in degrees, within the quadrant
    return 16.0 * th / 90.0


SOFFIT_SEG = 4.0
SUB = 2                 # v2: soffit + string pieces per tread (32 per turn: smoother underside, no facet kinks)
SOFFIT_T = 2.0


def segs_n(r0, r1, seg):
    n = max(1, math.ceil((r1 - r0) / seg))
    return [(r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n) for i in range(n)]


def segs(r0, r1):
    n = max(1, math.ceil((r1 - r0) / SEG))
    return [(r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n) for i in range(n)]


class El:
    """one element = a box of size (sx radial, sy, sz tangential) centred at c, pitched rx about local x, turned to theta."""
    def __init__(self, part, c, size, theta, rx=0.0, anchor=None, tag=None):
        self.part, self.c, self.size, self.theta, self.rx, self.tag = part, list(c), list(size), theta, rx, tag
        self.anchor = anchor          # uv anchor (radial distance, y) so every tread / soffit board lines up radially


def polar(r, th, y):
    t = math.radians(th)
    return [r * math.cos(t), y, r * math.sin(t)]


def build_quadrant(r0, r1, rail=True, balusters=2, string=True, soffit=True):
    els = []
    dth = 90.0 / TREADS_Q
    for k in range(TREADS_Q):
        ta, tb = k * dth, (k + 1) * dth
        tm = (ta + tb) / 2
        top = RISE * (k + 1)
        for ra, rb in segs(r0, r1):
            rm = (ra + rb) / 2
            w = 2 * rb * math.tan(math.radians(dth / 2)) + 0.2
            els.append(El("tread", polar(rm, tm, top - D / 2), [rb - ra, D, w], tm, anchor=[ra, top, 0]))
        if soffit:                                                   # finer radial AND tangential steps + 2 px plates: the
            for h2 in range(SUB):                                    # helicoid twists with radius, flat plates step at their
                t0, t1 = ta + dth * h2 / SUB, ta + dth * (h2 + 1) / SUB  # edges; the plate thickness hides the step (v2: 2 per tread)
                tc, dsub = (t0 + t1) / 2, dth / SUB
                for ra, rb in segs_n(r0, r1, SOFFIT_SEG):
                    rm = (ra + rb) / 2
                    arc = rm * math.radians(dsub)
                    phi = math.degrees(math.atan2(RISE / SUB, arc))
                    arc_o = 2 * rb * math.tan(math.radians(dsub / 2))      # cover the OUTER edge of the segment (no saw-tooth gaps)
                    L = math.hypot(arc_o, RISE / SUB * arc_o / arc) + OVL
                    yc = helix(tc) - D - SOFFIT_T / 2
                    els.append(El("soffit", polar(rm, tc, yc), [rb - ra + 0.02, SOFFIT_T, L], tc, rx=phi, anchor=[ra, 0, 0]))
        if string:
            rs = r1 + 0.75
            for h2 in range(SUB):
                t0, t1 = ta + dth * h2 / SUB, ta + dth * (h2 + 1) / SUB
                tc, dsub = (t0 + t1) / 2, dth / SUB
                arc = rs * math.radians(dsub)
                phi = math.degrees(math.atan2(RISE / SUB, arc))
                L = math.hypot(arc, RISE / SUB) + OVL
                els.append(El("string", polar(rs, tc, helix(tc) - D / 2), [1.5, D + 2.0, L], tc, rx=phi))
        if rail:
            rr = r1 - 0.25
            for h2 in range(2):                                   # two pitched pieces per tread (the carry law needs short ends)
                t0, t1 = ta + dth * h2 / 2, ta + dth * (h2 + 1) / 2
                tc = (t0 + t1) / 2
                arc = rr * math.radians(dth / 2)
                phi = math.degrees(math.atan2(RISE / 2, arc))
                L = math.hypot(arc, RISE / 2) + 0.6
                els.append(El("rail", polar(rr, tc, helix(tc) + RAIL), [2.5, 2.0, L], tc, rx=phi))
            for j in range(balusters):
                tb_ = ta + dth * (j + 0.5) / balusters
                y0, y1 = top, helix(tb_) + RAIL - 1.0
                els.append(El("baluster", polar(rr, tb_, (y0 + y1) / 2), [1.0, y1 - y0, 1.0], tb_))
    # quarter newel in the inner cell (x 0..r0, z 0..r0), stepped to read round with its 3 neighbours
    a = r0 * 0.62
    els.append(El("post", [r0 / 2, 8.0, a / 2], [r0, 16.0, a], 0.0))
    els.append(El("post", [a / 2, 8.0, r0 / 2], [a, 16.0, r0], 0.0))
    return els


def corners_of(el):
    """the 8 world corners of an element (pitch about local x, then turn about y) — Bedrock law via block_render."""
    sx, sy, sz = el.size
    pts = [[el.c[0] + dx * sx / 2, el.c[1] + dy * sy / 2, el.c[2] + dz * sz / 2] for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    out = []
    for p in pts:
        q = BR.transform(p, el.c, [el.rx, 0, 0]) if el.rx else p
        q = BR.transform(q, el.c, [0, -el.theta, 0]) if el.theta else q
        out.append(q)
    return out


def carry(els, ymax=29.9):
    """an element whose rotated top passes y = 30 (the block limit) belongs to the NEXT quadrant's cell instead: turn it
    back 90 deg about the helix corner and drop it 16 px — the same place in the world, owned by the block one level up
    (its rail end overhangs that cell's edge by a few px, inside the +-30 px law)."""
    out = []
    for el in els:
        if max(p[1] for p in corners_of(el)) > ymax:
            x, y, z = el.c
            el = El(el.part, [z, y - 16.0, -x], el.size, el.theta - 90.0, el.rx, el.anchor, "fwd")   # drawn by the block ABOVE
        out.append(el)
    return out


def carry_back(els, n, limit=30.0):
    """a cell taller than the 30 px law (the 1-block turret holds a whole quarter: soffit -7 .. rail 30) hands its LOWEST
    elements to the PREVIOUS quadrant's cell (turned +90 deg about the helix corner, lifted 16 px) until it fits."""
    els = list(els)
    for _ in range(400):
        span = {}
        for k, el in enumerate(els):
            ys = [p[1] for p in corners_of(el)]
            span.setdefault(cell_of(el, n), []).append((min(ys), max(ys), k))
        bad = [(c, v) for c, v in span.items() if max(x[1] for x in v) - min(x[0] for x in v) > limit]
        if not bad: return els
        c, v = bad[0]
        lo, hi, k = min(v)
        el = els[k]
        x, y, z = el.c
        els[k] = El(el.part, [-z, y + 16.0, x], el.size, el.theta + 90.0, el.rx, el.anchor, "back")   # drawn by the block BELOW
    raise RuntimeError("carry_back did not converge")


def cell_of(el, n):
    # the cell holding the element's centre (quadrant 0: x, z in 0..16n); clamp elements centred just outside the grid
    i = min(n - 1, max(0, int(math.floor(el.c[0] / 16))))
    j = min(n - 1, max(0, int(math.floor(el.c[2] / 16))))
    return i, j


def uv_box(size, wpos, mat):
    """per-face uv inside 0..16, world-anchored where it fits, sized to the face (tiling scale 1 px = 1 texel unit)."""
    sx, sy, sz = [max(0.0, v) for v in size]
    def at(a, s): return max(0.0, min(16.0 - min(s, 16.0), a % 16.0))
    fx = {"north": (sx, sy), "south": (sx, sy), "east": (sz, sy), "west": (sz, sy), "up": (sx, sz), "down": (sx, sz)}
    out = {}
    for f, (u, v) in fx.items():
        u, v = min(u, 16.0), min(v, 16.0)
        out[f] = {"uv": [round(at(wpos[0] + wpos[2], u), 3), round(at(16 - wpos[1], v), 3)], "uv_size": [round(u, 3), round(v, 3)], "material_instance": mat}
    return out


def emit(design, els, n):
    """one geometry per cell: identifier geometry.pw_spiral_<design>_c<i><j>; cell-local coords (cell centre at 0)."""
    cells = {}
    for idx, el in enumerate(els):
        i, j = cell_of(el, n)
        ox, oz = 16 * i + 8, 16 * j + 8
        c = [round(el.c[0] - ox, 4), round(el.c[1], 4), round(el.c[2] - oz, 4)]
        size = [round(v, 4) for v in el.size]
        origin = [round(c[k] - size[k] / 2, 4) for k in range(3)]
        cube = {"origin": origin, "size": size, "uv": uv_box(size, el.anchor or el.c, el.part)}
        if el.rx: cube["pivot"], cube["rotation"] = c, [round(el.rx, 3), 0, 0]
        bone = {"name": f"e{idx}_{el.part}", "pivot": c, "cubes": [cube]}
        if el.theta: bone["rotation"] = [0, round(-el.theta, 3), 0]
        cells.setdefault((i, j), []).append(bone)
    geos = []
    for (i, j), bones in sorted(cells.items()):
        geos.append({"description": {"identifier": f"geometry.pw_spiral_{design}_c{i}{j}", "texture_width": 16, "texture_height": 16,
                                     "visible_bounds_width": 3, "visible_bounds_height": 3, "visible_bounds_offset": [0, 0.75, 0]},
                     "bones": bones})
    return {"format_version": "1.21.0", "minecraft:geometry": geos}


def bounds_report(design, els, n):
    """Bedrock block geometry limits (as researched: each axis extent <= 30 px, every vertex within +-30 px of the
    block origin) per cell, measured on the ROTATED corners."""
    rep = {}
    for el in els:
        i, j = cell_of(el, n)
        ox, oz = 16 * i + 8, 16 * j + 8
        for p in corners_of(el):
            q = (p[0] - ox, p[1], p[2] - oz)
            b = rep.setdefault((i, j), [[1e9] * 3, [-1e9] * 3])
            for k in range(3): b[0][k] = min(b[0][k], q[k]); b[1][k] = max(b[1][k], q[k])
    out = {}
    for key, (lo, hi) in sorted(rep.items()):
        ext = [hi[k] - lo[k] for k in range(3)]
        ok = all(e <= 30.0 for e in ext) and all(abs(v) <= 30.0 for v in lo + hi)
        out[f"c{key[0]}{key[1]}"] = {"min": [round(v, 2) for v in lo], "max": [round(v, 2) for v in hi], "extent": [round(e, 2) for e in ext], "ok": ok}
    return out


def collision(r0, r1, n, grid=2, limit=16, rail_to=None):
    """try a 2 px sample grid, then 4 px, per cell, until the cell fits the 16-box array limit. rail_to: the head piece's
    rail stops at this angle (the exit opening carries no rail wall)."""
    out = {}
    for g in (grid, 4, 8):
        res = _collision(r0, r1, n, g, rail_to)
        for k, v in res.items():
            if k not in out and len(v) <= limit: out[k] = v
    return out


def _collision(r0, r1, n, grid=2, rail_to=None):
    """multi-box collision per cell (format >= 1.21.130 array form). Sample the cell on a grid; height = the tread top
    over the sample (the newel = full height; the rail band at the outer edge = 24, the array ceiling, so nobody steps
    off an open stair); merge equal-height samples into rectangles (greedy). Boxes in Bedrock block coords
    (origin x/z -8..8, y 0..24)."""
    dth = 90.0 / TREADS_Q
    out = {}
    m = 16 // grid
    for i in range(n):
        for j in range(n):
            H = np.zeros((m, m))
            for a in range(m):
                for b in range(m):
                    x, z = 16 * i + (a + 0.5) * grid, 16 * j + (b + 0.5) * grid
                    r, th = math.hypot(x, z), math.degrees(math.atan2(z, x))
                    exitz = rail_to is not None and th > rail_to
                    if r < r0: H[a, b] = 16
                    elif r <= r1 - 2.5: H[a, b] = RISE * (min(TREADS_Q - 1, int(th // dth)) + 1)
                    elif r <= r1 + 1.5 and not exitz: H[a, b] = 24
                    elif r <= r1 + 1.5: H[a, b] = RISE * (min(TREADS_Q - 1, int(th // dth)) + 1)
                    else: H[a, b] = 0
            boxes, used = [], np.zeros_like(H, bool)
            for a in range(m):
                for b in range(m):
                    if used[a, b] or H[a, b] == 0: continue
                    h = H[a, b]; b2 = b
                    while b2 + 1 < m and not used[a, b2 + 1] and H[a, b2 + 1] == h: b2 += 1
                    a2 = a
                    while a2 + 1 < m and all(not used[a2 + 1, bb] and H[a2 + 1, bb] == h for bb in range(b, b2 + 1)): a2 += 1
                    used[a:a2 + 1, b:b2 + 1] = True
                    boxes.append({"origin": [a * grid - 8, 0, b * grid - 8], "size": [(a2 - a + 1) * grid, int(h), (b2 - b + 1) * grid]})
            out[f"c{i}{j}"] = boxes
    return out


# ---------------------------------------------------------------- preview assembly + render
PALETTES = {
    "oak": {"tread": "oak_planks_v0", "soffit": "oak_planks_v2@r90", "string": "stripped_oak_log", "rail": "stripped_dark_oak_log",
            "baluster": "stripped_oak_log", "post": "stripped_oak_log", "_floor": "smooth_stone_v0"},
    "spruce_plaster": {"tread": "spruce_planks_v0", "soffit": "smooth_stone_v1", "string": "stripped_spruce_log", "rail": "stripped_dark_oak_log",
                       "baluster": "stripped_spruce_log", "post": "stripped_spruce_log", "_floor": "smooth_stone_v0"},
    "stone": {"tread": "polished_andesite_v0", "soffit": "stone_bricks", "string": "stone_bricks_v1", "rail": "stripped_oak_log",
              "baluster": "stripped_dark_oak_log", "post": "stone_bricks_v2", "_floor": "smooth_stone_v0"},
}


def tower_faces(geo_doc, n, turns=2):
    """place every cell geometry: quadrant q turned q*90 deg about the helix corner (ascending), lifted 16 px per
    quadrant, 64 px per turn — the same move a cardinal_direction permutation makes on each block."""
    tmp = Path("/tmp/spiral_geo_tmp.json"); tmp.write_text(json.dumps(geo_doc))
    base = []
    for g in geo_doc["minecraft:geometry"]:
        ident = g["description"]["identifier"]
        i, j = int(ident[-2]), int(ident[-1])
        for f in BR.load_faces(tmp, ident):
            f.pts = [[p[0] + 16 * i + 8, p[1], p[2] + 16 * j + 8] for p in f.pts]
            base.append(f)
    faces = []
    for t in range(turns):
        for q in range(4):
            a = math.radians(90 * q)
            ca, sa = math.cos(a), math.sin(a)
            for f in base:
                g = BR.Face([[p[0] * ca - p[2] * sa, p[1] + 16 * (4 * t + q), p[0] * sa + p[2] * ca] for p in f.pts], f.uv, f.mat, f.name, f.bone)
                # the per-face shade follows the turned face (n/s <-> e/w every 90 deg)
                if q % 2 == 1 and f.name in ("north", "south", "east", "west"):
                    g.name = {"north": "east", "east": "south", "south": "west", "west": "north"}[f.name]
                faces.append(g)
    return faces


def floor_faces(half, y=0.0):
    return [BR.Face([[-half, y, -half], [half, y, -half], [half, y, half], [-half, y, half]], (0, 0, 1, 1), "_floor", "up", "_scene")]


def render_views(design, faces, n, pal, out, W=900, H=900):
    R = 16 * n
    mats = {k: {"texture": v} for k, v in PALETTES[pal].items()}
    fl = floor_faces(R + 24)
    rw = (R + 3) * 0.45 if n > 1 else 8.5                 # the walking line
    views = [
        ("outside, 3/4 from below", (2.6 * R + 30, 40, -1.9 * R - 30), (0, 70, 0)),
        ("underneath, looking up from the floor", (-0.45 * R, 3, -0.45 * R), (0.05 * R, 120, 0.1 * R)),
        ("player on the stair (eye 1.62 blocks)", None, None),
        ("from above, 3/4", (2.2 * R + 30, 200, -2.0 * R - 30), (0, 60, 0)),
    ]
    tiles = []
    for name, eye, tgt in views:
        if eye is None:                       # on tread 1 of quadrant 0 at the walking line, facing up the flight
            th = 22.5 * 1.5
            y = RISE * 2 + 26
            t = math.radians(th)
            eye = (rw * math.cos(t), y, rw * math.sin(t))
            d = (-math.sin(t), math.cos(t))                    # the ascending tangent
            inward = (-math.cos(t), -math.sin(t))
            tgt = (eye[0] + 30 * d[0] + 6 * inward[0], y - 2, eye[2] + 30 * d[1] + 6 * inward[1])
        img, _, _ = BR.render(faces + fl, mats, eye, tgt, W, H, fov=70 if "player" in name else 50)
        tiles.append((name, Image.fromarray(img)))
    sheet = Image.new("RGB", (W * 2 + 30, H * 2 + 110), (14, 13, 12))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except Exception:
        font = small = None
    d.text((12, 10), f"SPIRAL STAIR {DESIGNS[design]['label']}  ·  palette: {pal}", fill=(235, 225, 200), font=font)
    for k, (name, im) in enumerate(tiles):
        x, y = 10 + (k % 2) * (W + 10), 60 + (k // 2) * (H + 20)
        sheet.paste(im, (x, y))
        d.text((x + 10, y + 8), name, fill=(255, 240, 160), font=small)
    sheet.save(out)
    return out


# ---------------------------------------------------------------- v2: the foot, the head, the left hand
POST = 2.5              # end-post section (px)


def rail_end_theta(els):
    """the last angle the quadrant's own rail reaches inside its own block (rail pieces not handed to the block above)."""
    dth = 90.0 / TREADS_Q
    return max(el.theta + dth / 4 for el in els if el.part == "rail" and el.tag is None)


def variant(els, r1, kind):
    """mid = every piece; start = the foot (nothing below: pieces owned by the block below are dropped) + a newel post where
    the rail begins; end = the head (nothing above: pieces owned by the block above are dropped, so the rail stops where
    this block's own rail stops) + a newel post there. The last tread top (16) is flush with the landing floor."""
    rr = r1 - 0.25
    dth = 90.0 / TREADS_Q
    out = [el for el in els if not (kind == "start" and el.tag == "fwd") and not (kind in ("end", "door") and el.tag == "back")]
    if kind == "start":
        top = helix(0.0) + RAIL + 2.0
        out.append(El("post", polar(rr, 0.6, top / 2), [POST, top, POST], 0.6))
        out.append(El("post", polar(rr, 0.6, top + 0.5), [POST + 1.0, 1.0, POST + 1.0], 0.6))
    if kind == "door":
        # his 16:30 answer: a MID floor is left through a doorway BESIDE the step level with it. The door piece is a head
        # whose rail stops EARLY — at exit_theta (EXIT_W px of outer edge before the quarter's end, as the top exit) — so
        # the outer face next to the quarter's end is open for a body (>= 10 px; the next quarter is a START piece whose
        # foot newel stands past the boundary). Balusters and rail past that angle go; the last tread top (16) is the floor.
        te = exit_theta(r1)
        out = [el for el in out if not (el.part in ("rail", "baluster") and el.theta > te)]
        dsub = dth / SUB
        keep = []
        for el in out:
            if el.part == "string" and el.tag is None and el.theta > te:
                y0 = helix(el.theta - dsub / 2) - D - 1.0
                keep.append(El("string", [el.c[0], (y0 + 16.0) / 2, el.c[2]], [el.size[0], 16.0 - y0, el.size[2]], el.theta))
            else:
                keep.append(el)
        out = keep
        y0 = RISE * (min(TREADS_Q - 1, int(te // dth)) + 1)
        y1 = min(29.4, helix(te) + RAIL + 1.5)
        out.append(El("post", polar(rr, te, (y0 + y1) / 2), [POST, y1 - y0, POST], te))
        out.append(El("post", polar(rr, te, y1 + 0.25), [POST + 1.0, 0.5, POST + 1.0], te))
    if kind == "end":
        # his 15:06 + answer: the stair exits FORWARD — off the last step, along its own direction of travel — onto a floor
        # in FRONT of it (which may run on as a lengthwise hallway), never off the side. Headroom law (his answer): at least
        # TWO blocks at every point of the ascent (the 3-block rule is vanilla's: its half-block step briefly leaves 1.5);
        # the floor in front lies over the first quarter ahead of the turn below with 2.75 -> 2.0 blocks: legal.
        # The rail runs as far as its own block allows (the piece past y 30 belongs to the block above, which the head
        # does not have) and ends at an end post; the last tread top (16) is flush with the floor in front.
        te = rail_end_theta(els)
        dsub = dth / SUB
        keep = []
        for el in out:                         # the outer string's last pieces must not stand above the floor line (16)
            if el.part == "string" and el.tag is None and el.theta > te:
                y0 = helix(el.theta - dsub / 2) - D - 1.0
                keep.append(El("string", [el.c[0], (y0 + 16.0) / 2, el.c[2]], [el.size[0], 16.0 - y0, el.size[2]], el.theta))
            else:
                keep.append(el)
        out = keep
        y0 = RISE * (min(TREADS_Q - 1, int(te // dth)) + 1)
        y1 = min(29.4, helix(te) + RAIL + 1.5)
        out.append(El("post", polar(rr, te, (y0 + y1) / 2), [POST, y1 - y0, POST], te))
        out.append(El("post", polar(rr, te, y1 + 0.25), [POST + 1.0, 0.5, POST + 1.0], te))
    return out


EXIT_W = 18.0           # px of outer edge left open at the head (a player is ~10 px wide)
EXIT_STEP = 6.0         # the raised floor-edge band (px, radial) on any exit tread below the floor


def exit_theta(r1):
    dth = 90.0 / TREADS_Q
    te = 90.0 - math.degrees(EXIT_W / r1)
    return max(dth / 2, math.floor(te / (dth / 2)) * (dth / 2))


def fit_floors(lower_surface, upper_surface):
    """his 14:44 rule for the generators: a spiral ENDS at the floor. Surfaces in blocks (a slab floor = .5). One quarter
    turn rises exactly 1 block, so the stair runs floor(rise) quarters from the block whose bottom is the lower surface
    rounded down; any remainder (a slab floor above, a floor off the block grid) is closed by a STAIR PIECE at the upper
    floor's first edge (beside the exit). Returns (quarters, foot_block_y, bridge_px) — bridge_px 0 = the head is flush."""
    y0 = math.floor(lower_surface + 1e-9)
    rise = upper_surface - y0
    q = int(math.floor(rise + 1e-9))
    bridge = round((rise - q) * 16)
    if q < 1: raise ValueError(f"floors {lower_surface} -> {upper_surface}: under one quarter turn")
    return q, y0, bridge


def mirror(els):
    """the other hand: reflect across the quadrant's diagonal (x <-> z). The quadrant stays the same n x n cells
    (cell (i, j) -> (j, i)), the climb turns the other way, every tangent flips so every pitch flips."""
    return [El(el.part, [el.c[2], el.c[1], el.c[0]], el.size, 90.0 - el.theta, -el.rx, el.anchor, el.tag) for el in els]


def mirror_collision(col):
    out = {}
    for k, boxes in col.items():
        i, j = k[1], k[2]
        out[f"c{j}{i}"] = [{"origin": [b["origin"][2], 0, b["origin"][0]], "size": [b["size"][2], b["size"][1], b["size"][0]]} for b in boxes]
    return out


def place_faces(geo_doc, ident_pre, q_rot, lift, hand):
    """faces of one quadrant's blocks, turned q_rot x 90 deg about the helix corner (+ for the right hand, - for the left)
    and lifted `lift` px — the move a cardinal_direction permutation makes."""
    tmp = Path("/tmp/spiral_geo_tmp.json"); tmp.write_text(json.dumps(geo_doc))
    a = math.radians(90 * q_rot * (1 if hand == "r" else -1))
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for g in geo_doc["minecraft:geometry"]:
        ident = g["description"]["identifier"]
        if not ident.startswith(ident_pre): continue
        i, j = int(ident[-2]), int(ident[-1])
        for f in BR.load_faces(tmp, ident):
            pts = [[p[0] + 16 * i + 8, p[1], p[2] + 16 * j + 8] for p in f.pts]
            gface = BR.Face([[p[0] * ca - p[2] * sa, p[1] + lift, p[0] * sa + p[2] * ca] for p in pts], f.uv, f.mat, f.name, f.bone)
            if q_rot % 2 == 1 and f.name in ("north", "south", "east", "west"):
                gface.name = {"north": "east", "east": "south", "south": "west", "west": "north"}[f.name]
            out.append(gface)
    return out


def box_faces(x0, y0, z0, x1, y1, z1, mat):
    cs = BR.corners([x0, y0, z0], [x1 - x0, y1 - y0, z1 - z0], 0)
    return [BR.Face(pts, (0, 0, 1, 1), mat, name, "_scene") for name, pts in cs.items()]


LAND_DEPTH = 48          # the hallway beyond the well, in front of the head (px)
HEAD_MIN = 32            # his law (15:1x): at least TWO blocks at every point of the ascent (our treads rise 4 px, not vanilla's 8)


def turn_xz(x, z, q_rot, hand):
    a = math.radians(90 * q_rot * (1 if hand == "r" else -1))
    ca, sa = math.cos(a), math.sin(a)
    return x * ca - z * sa, x * sa + z * ca


def landing_local(n, hand):
    """the floor IN FRONT of the head (his 15:06), in the head quadrant's own frame: the first quarter ahead (theta
    90..180: x -R..0, z 0..R for the right hand) running on as a lengthwise hallway LAND_DEPTH px beyond the well;
    the mirror swaps x and z. The second quarter ahead stays open (1 block over the turn below)."""
    R = 16 * n
    x0, x1, z0, z1 = -R - LAND_DEPTH, 0, 0, R
    return (z0, z1, x0, x1) if hand == "l" else (x0, x1, z0, z1)


def tower2(geo_doc, design, hand, n, turns=2):
    """2 turns: the foot block first, mid blocks, the head block last; the landing BESIDE the well at the head (his 14:28
    headroom law: nothing is laid over the well)."""
    faces = []
    nq = 4 * turns
    for k in range(nq):
        kind = "start" if k == 0 else ("end" if k == nq - 1 else "mid")
        faces += place_faces(geo_doc, f"geometry.pw_spiral_{design}_{hand}_{kind}_c", k % 4, 16 * k, hand)
    top = 16 * nq
    x0, x1, z0, z1 = landing_local(n, hand)
    qh = (nq - 1) % 4
    pts = [turn_xz(x, z, qh, hand) for x, z in ((x0, z0), (x1, z1))]
    X0, X1 = min(p[0] for p in pts), max(p[0] for p in pts)
    Z0, Z1 = min(p[1] for p in pts), max(p[1] for p in pts)
    for gx in range(int(X0), int(X1), 16):                  # one box per block: the preview rasteriser drops a face that
        for gz in range(int(Z0), int(Z1), 16):              # reaches behind the camera, so keep the faces small
            faces += box_faces(gx, top - 16, gz, gx + 16, top, gz + 16, "_landing")
    return faces


# ---------------------------------------------------------------- the headroom law (his 14:28)
def _hull(pts):
    pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in pts))
    if len(pts) < 3: return pts
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def tower_solids(design, hand, turns=2):
    """every element of the 2-turn tower in world px: (part, k, hull polygon in plan, min y, max y)."""
    P = DESIGNS[design]
    base = carry_back(carry(build_quadrant(P["r0"], P["r1"])), P["n"])
    nq = 4 * turns
    out = []
    for k in range(nq):
        kind = "start" if k == 0 else ("end" if k == nq - 1 else "mid")
        els = variant(base, P["r1"], kind)
        if hand == "l": els = mirror(els)
        for el in els:
            cs = corners_of(el)
            plan = [turn_xz(p[0], p[2], k % 4, hand) for p in cs]
            out.append((el.part, k, _hull(plan), min(p[1] for p in cs) + 16 * k, max(p[1] for p in cs) + 16 * k))
    top = 16 * nq
    x0, x1, z0, z1 = landing_local(P["n"], hand)
    pts = [turn_xz(x, z, (nq - 1) % 4, hand) for x, z in ((x0, z0), (x1, z0), (x1, z1), (x0, z1))]
    out.append(("landing", nq, _hull(pts), top - 16, top))
    return out


def _inside(poly, X, Z):
    ok = np.ones_like(X, bool)
    n = len(poly)
    for i in range(n):
        (ax, az), (bx, bz) = poly[i], poly[(i + 1) % n]
        ok &= ((bx - ax) * (Z - az) - (bz - az) * (X - ax)) >= -1e-6
    return ok


def surfaces(design, hand, turns=2, step=2.0):
    """the walkable surfaces: every tread (its centre band, 1 px clear of its edges), the floor round the foot, the landing."""
    P = DESIGNS[design]
    r0, r1, n = P["r0"], P["r1"], P["n"]
    R = 16 * n
    nq = 4 * turns
    dth = 90.0 / TREADS_Q
    S = []                                                     # (x, z, y, what)
    for k in range(nq):
        for t in range(TREADS_Q):
            for r in np.arange(r0 + 1.0, r1 - 2.5, step):
                for f in (0.2, 0.5, 0.8):
                    th = (t + f) * dth
                    x, z = r * math.cos(math.radians(th)), r * math.sin(math.radians(th))
                    if hand == "l": x, z = z, x
                    X, Z = turn_xz(x, z, k % 4, hand)
                    yy = RISE * (t + 1)
                    S.append((X, Z, 16 * k + yy, "stair"))
    for x in np.arange(-R - 30, R + 30, step):
        for z in np.arange(-R - 30, R + 30, step):
            if math.hypot(x, z) < r1 + 3 and math.hypot(x, z) > r0:   # the floor inside the well (under the first turn) + the stair skin
                S.append((x, z, 0.0, "well floor"))
            elif math.hypot(x, z) >= r1 + 3:
                S.append((x, z, 0.0, "floor"))
    x0, x1, z0, z1 = landing_local(n, hand)
    for x in np.arange(x0 + 1, x1, step):
        for z in np.arange(z0 + 1, z1, step):
            X, Z = turn_xz(x, z, (nq - 1) % 4, hand)
            S.append((X, Z, 16.0 * nq, "landing"))
    return S


def clearance(design, hand, turns=2):
    """per walkable sample: the gap from the surface up to the lowest solid whose plan holds the sample (visual geometry,
    conservative: a pitched piece counts from its lowest corner). Law: >= HEAD_MIN (2 blocks) wherever a person walks."""
    solids = tower_solids(design, hand, turns)
    S = surfaces(design, hand, turns)
    X = np.array([s[0] for s in S]); Z = np.array([s[1] for s in S]); Y = np.array([s[2] for s in S])
    gap = np.full(len(S), np.inf); who = np.array([""] * len(S), dtype=object)
    for part, k, poly, ymin, ymax in solids:
        if len(poly) < 3: continue
        above = ymin > Y + 0.5
        if not above.any(): continue
        ins = _inside(poly, X, Z) & above
        g = np.where(ins, ymin - Y, np.inf)
        better = g < gap
        gap[better] = g[better]; who[better] = part
    return S, gap, who


def clearance_report(design, hand, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    S, gap, who = clearance(design, hand)
    kinds = np.array([s[3] for s in S])
    rep = {}
    for kd in ("stair", "landing", "floor", "well floor"):
        m = kinds == kd
        g = gap[m]
        fin = g[np.isfinite(g)]
        rep[kd] = {"samples": int(m.sum()), "min_px": float(fin.min()) if len(fin) else None,
                   "below_law": int((g < HEAD_MIN).sum()), "lowest_by": sorted(set(who[m][g < HEAD_MIN]))[:6]}
    fig, axs = plt.subplots(1, 2, figsize=(15, 7.2), dpi=110)
    for ax, sel, title in ((axs[0], kinds == "stair", "on the treads (every turn, seen from above)"),
                           (axs[1], (kinds == "floor") | (kinds == "well floor") | (kinds == "landing"), "the floor round the foot + the landing")):
        xs = np.array([s[0] for s in S])[sel] / 16; zs = np.array([s[1] for s in S])[sel] / 16
        g = np.clip(gap[sel], 0, 80) / 16
        sc = ax.scatter(xs, zs, c=g, cmap="RdYlGn", vmin=1.0, vmax=4.0, s=7, marker="s")
        bad = gap[sel] < HEAD_MIN
        ax.scatter(xs[bad], zs[bad], facecolors="none", edgecolors="black", s=9, linewidths=0.3)
        ax.set_aspect("equal"); ax.set_title(title); ax.set_xlabel("x (blocks)"); ax.set_ylabel("z (blocks)")
        fig.colorbar(sc, ax=ax, label="headroom (blocks; law >= 2, black ring = below 2)")
    fig.suptitle(f"SPIRAL {design} ({hand}) headroom: treads min {rep['stair']['min_px'] / 16:.2f} blocks · landing "
                 f"{'open' if rep['landing']['min_px'] is None else round(rep['landing']['min_px'] / 16, 2)} · under-stair floor cells below 2 blocks: "
                 f"{rep['well floor']['below_law']} of {rep['well floor']['samples']} (not a walk path)")
    fig.tight_layout(); fig.savefig(out_png); plt.close(fig)
    return rep


def render_v2(design, hand, faces, n, pal, out, W=760, H=760):
    R = 16 * n
    mats = {k: {"texture": v} for k, v in PALETTES[pal].items()}
    mats["_landing"] = {"texture": PALETTES[pal].get("_landing", "spruce_planks_v1")}
    fl = floor_faces(R + 24)
    sgn = 1 if hand == "r" else -1
    rw = (R + 3) * 0.45 if n > 1 else 8.5
    def pol(r, th, y):
        t = math.radians(th)
        return (r * math.cos(t), y, sgn * r * math.sin(t)) if hand == "r" else (r * math.sin(t), y, r * math.cos(t))
    th = 22.5 * 1.5
    eye_p = pol(rw, th, RISE * 2 + 26)
    ahead = pol(rw * 0.9, th + 75, RISE * 2 + 24)
    top = 16 * 8
    views = [
        ("outside, 3/4 from below", (2.6 * R + 30, 40, -1.9 * R - 30), (0, 70, 0)),
        ("underneath, looking up from the floor", (-0.45 * R, 3, -0.45 * R), (0.05 * R, 120, 0.1 * R)),
        ("player on the stair (eye 1.62 blocks)", eye_p, ahead),
        ("the foot: newel post where the rail begins", pol(R * 1.9 + 20, -40, 30), pol(R * 0.6, 20, 10)),
        ("the head: end post + landing", pol(R * 1.7 + 24, 230, top + 40), pol(R * 0.5, 300, top - 10)),
        ("from above, 3/4", (2.2 * R + 30, 200 + top - 128, -2.0 * R - 30), (0, 60, 0)),
    ]
    tiles = []
    for name, eye, tgt in views:
        img, _, _ = BR.render(faces + fl, mats, eye, tgt, W, H, fov=70 if "player" in name else 50)
        tiles.append((name, Image.fromarray(img)))
    sheet = Image.new("RGB", (W * 3 + 40, H * 2 + 110), (14, 13, 12))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except Exception:
        font = small = None
    d.text((12, 10), f"SPIRAL STAIR v3 {DESIGNS[design]['label']}  ·  {'right' if hand == 'r' else 'left'}-hand (file frame)  ·  palette: {pal}", fill=(235, 225, 200), font=font)
    for k, (name, im) in enumerate(tiles):
        x, y = 10 + (k % 3) * (W + 10), 60 + (k // 3) * (H + 20)
        sheet.paste(im, (x, y))
        d.text((x + 10, y + 8), name, fill=(255, 240, 160), font=small)
    sheet.save(out)
    return out


def build_design(name):
    """every geometry of one design: hand r/l x kind start/mid/end x cells; collision per hand; bounds per geometry."""
    P = DESIGNS[name]
    base = carry_back(carry(build_quadrant(P["r0"], P["r1"])), P["n"])
    geos, report, cols = [], {}, {}
    col_r = collision(P["r0"], P["r1"], P["n"])
    cols = {"r": col_r, "l": mirror_collision(col_r)}
    for hand in ("r", "l"):
        for kind in ("start", "mid", "end"):
            els = variant(base, P["r1"], kind)
            if hand == "l": els = mirror(els)
            tag = f"{name}_{hand}_{kind}"
            g = emit(tag, els, P["n"])
            geos += g["minecraft:geometry"]
            for k, v in bounds_report(tag, els, P["n"]).items():
                report[f"{tag}_{k}"] = {**v, "cubes": sum(len(x["bones"]) for x in g["minecraft:geometry"] if x["description"]["identifier"].endswith(f"{tag}_{k}")),
                                         "collision_boxes": len(cols[hand].get(k, []))}
    return {"format_version": "1.21.0", "minecraft:geometry": geos}, report, cols


def main():
    od = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/_docs/program228/spiral")
    od.mkdir(parents=True, exist_ok=True)
    pals = sys.argv[2].split(",") if len(sys.argv) > 2 else ["oak"]
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else list(DESIGNS)
    hands = sys.argv[4].split(",") if len(sys.argv) > 4 else ["r"]
    summary = {}
    for name in only:
        P = DESIGNS[name]
        geo, report, cols = build_design(name)
        (od / f"pw_spiral_{name}.v2.geo.json").write_text(json.dumps(geo, indent=1))
        (od / f"pw_spiral_{name}.v2.collision.json").write_text(json.dumps(cols, indent=1))
        summary[name] = report
        bad = [k for k, v in report.items() if not v["ok"] or v["collision_boxes"] > 16]
        print(name, "geometries", len(geo["minecraft:geometry"]), "bounds/collision failures:", bad, flush=True)
        for hand in hands:
            cr = clearance_report(name, hand, od / f"HEADROOM-{name}-{hand}-v3.png")
            summary[name + "_headroom_" + hand] = cr
            print("headroom", name, hand, json.dumps(cr), flush=True)
            if "--headroom-only" in sys.argv: continue
            faces = tower2(geo, name, hand, P["n"])
            for pal in pals:
                render_v2(name, hand, faces, P["n"], pal, od / f"SPIRAL-{name}-{hand}-{pal}-v3.png")
                print("rendered", name, hand, pal, flush=True)
    (od / "spiral_summary_v3.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
