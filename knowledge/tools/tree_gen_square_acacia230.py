#!/usr/bin/env python3
"""tree_gen_square.py — tree program T1, the SQUARE species (his T1 rule: every ELDER + acacia, cherry, mangrove keep
square logs with fancy branches; TC = 32 per square species, D-C484). Branches are LOG LINES (3-D Bresenham runs of
the trunk block; vanilla logs carry pillar_axis along the run), leaves are clumps at the limb ends, baked final like
tree_gen.py (pw:variant from pwCellHash, pw:off, rseed). Rules: _docs/trees/TREE-ARCHITECTURE-RESEARCH-2026-10-02.md
§6 dark oak, §7 pale oak (veteran), §8 acacia, §9 cherry, §10 mangrove, §2/§4/§5 "old giant" rows for the oak /
spruce / jungle elders. Output: _staging/trees/<species>/<species>_elder_nn.mcstructure (+ REPORT.json) and
outputs/TREE-SQUARE-<species>.png.  Usage: tree_gen_square.py [species ...]

acacia230 (2026-10-07): copy of tools/tree_gen_square.py (md5 7d871a93). ACACIA ONLY — every limb ends inside its plate:
  * the main limb is the same line as before, ending one layer UNDER its plate (LIMB_DROP; the plate stays where it was,
    so its full 1-2 leaf layers cover the wood and survive tree_rescale's vertical squeeze); a main tip that sat on the
    plate's rim steps back along its own line inside the plate;
  * the 2-4 secondary limbs (same draws: direction, length) rise from the main limb's cell under the plate's CENTRE (they
    used to start at the tip, 0.3 x reach off-centre, and run outwards past the rim) to one layer under the plate, stop
    LIMB_RIM_MARGIN in from the rim, and their end is at least 1 in from it where tree_rescale puts it (end_inside);
  * the old trees' dead limb stops before it leaves the canopy's shadow (DEAD_LIMB_UNDER_CANOPY).
RNG-free: the same draws in the same order, so every plate, the stem / fork and every other species are unchanged.
Pipeline / install: _staging/acacia_230/README.md."""
import json
import math
import random
import sys
import zlib
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402
import tree_gen as T  # noqa: E402

OUT = Path("/home/claude/_staging/trees")
PER = 32
SPEC = {   # species: (trunk block, leaf block, root block or None, trunk width, vanilla axis state?)
    "oak_elder": ("pw:oak_elder", "pw:oak_leaves", "pw:oak_elder_root", 2, False),
    "spruce_elder": ("pw:spruce_elder", "pw:spruce_leaves", "pw:spruce_elder_root", 2, False),
    "jungle_elder": ("pw:jungle_elder", "pw:jungle_leaves", "pw:jungle_elder_root", 2, False),
    "dark_oak_elder": ("pw:dark_oak_elder", "pw:dark_oak_leaves", "pw:dark_oak_elder_root", 2, False),
    "pale_oak_elder": ("pw:pale_oak_elder", "pw:pale_oak_leaves", "pw:pale_oak_elder_root", 2, False),
    "acacia": ("minecraft:acacia_log", "pw:acacia_leaves", "pw:acacia_root", 1, True),      # T2b (10-03): the root carries tpl + rotation
    "cherry": ("minecraft:cherry_log", "pw:cherry_leaves", "pw:cherry_root", 1, True),      # T2b (10-03): the root carries tpl + rotation
    "mangrove": ("minecraft:mangrove_log", "pw:mangrove_leaves", "pw:mangrove_root", 1, True),      # T2b (10-03): the root carries tpl + rotation
}


# v4 (10-06): the stem's tip under the crown apex (tree_gen.sink_tip), per species. The oak / pale oak elders' dead stag
# limbs keep their RNG draws but are drawn AFTER the cut: not at all (False), or from the stem's new top (True, as before)
STAG_OVER_CROWN = False
TRUNK_TIP_DEPTH = {"oak_elder": 5, "spruce_elder": 4, "jungle_elder": 3, "dark_oak_elder": 3, "pale_oak_elder": 3,
                   "acacia": 3, "cherry": 3, "mangrove": 3}


def sink_stem(logs, leaves, species, w, anchor="stem"):
    """the stem = logs over the w x w footprint, contiguous from the ground; cut by tree_gen.sink_tip. Mutates logs /
    leaves; returns the stem's new top y."""
    foot = {(x, z) for x in range(w) for z in range(w)}
    stem = set()
    for (x, z) in foot:
        y = 0
        while (x, y, z) in logs:
            stem.add((x, y, z))
            y += 1
    kept, core, gone = T.sink_tip(sorted(stem), leaves, TRUNK_TIP_DEPTH[species], anchor)
    for c in core + gone:
        logs.discard(c)
    leaves |= set(core)
    return max(c[1] for c in kept)


# acacia230 (the limb-end fix; acacia only)
LIMB_RIM_MARGIN = 1     # columns of plate every limb cell keeps between itself and the plate's rim, every direction (diagonals
                        # too), so it stays covered from the sky through the rescale's rounding
LIMB_DROP = 1           # the main limb's end and its secondary limbs run this many layers under the plate's base layer
COVER_LAYERS = 2        # plate layers wanted straight over a limb cell (the plate's own thickness where it has two): the
                        # rescale squeezes acacia crowns by up to 1.75 layers per layer, which can drop a single cover layer
END_HEADROOM = 3        # an END's 3 x 3 columns must reach as high over it as the plate does over the end itself, up to this
                        # many layers: the rounded (raddiana) templates are squeezed 1.5-1.75 x, which can fold 2 layers
RESCALE_SW = 0.8        # tools/tree_rescale.py TARGETS["acacia"][0]: the pipeline shrinks the crown to 0.8 about the trunk;
                        # a limb END is tested where the rescale will put it (end_inside), so it is >= 1 inside the rim there
DEAD_LIMB_UNDER_CANOPY = True   # the old trees' dead limb stops before it leaves the canopy's shadow (False: as before)


def plate_cover(plate):
    """acacia230: (x, z) -> sorted y values of the plate's cells in that column."""
    cols = {}
    for x, y, z in plate:
        cols.setdefault((x, z), []).append(y)
    for ys in cols.values():
        ys.sort()
    return cols


def covered(cover, col, y, head=1):
    """acacia230: the plate's highest cell in column col is at least `head` layers above height y."""
    ys = cover.get(col)
    return bool(ys) and ys[-1] >= y + head


def inside_plate(c, cover, margin=LIMB_RIM_MARGIN, layers=COVER_LAYERS):
    """acacia230: a log cell is inside its plate when every column within `margin` of it (its own included) has plate
    above the cell (covered from the sky and at least `margin` cells in from the rim), and its own column has
    min(layers, the plate's thickness in that column) plate cells above the cell."""
    x, y, z = c
    if not all(covered(cover, (x + dx, z + dz), y) for dx in range(-margin, margin + 1) for dz in range(-margin, margin + 1)):
        return False
    return sum(v > y for v in cover[(x, z)]) >= min(layers, len(cover[(x, z)]))


def _fwd(v):
    """tree_rescale.fwdh for the 1-wide acacia trunk (centre 0, unscaled ring 1): where a log at old offset v goes."""
    return v if abs(v) <= 1 else math.copysign(1 + (abs(v) - 1) * RESCALE_SW, v)


def _inv(v):
    """tree_rescale.inv: the old offset a new leaf column v is sampled from."""
    return v if abs(v) <= 1 else math.copysign(1 + (abs(v) - 1) / RESCALE_SW, v)


def end_inside(c, cover, layers=COVER_LAYERS):
    """acacia230: a limb END is inside its plate when it is inside_plate (margin 1) AND, where tree_rescale moves it, the
    3 x 3 columns around it are sampled from old columns that all have plate above it (the rescale's own arithmetic:
    wood forward-mapped and rounded, leaves inverse-sampled and rounded, the trunk's own column skipped outwards), each
    reaching as high over the end as its own column does (at least `layers`, at most END_HEADROOM): the rescale's
    vertical squeeze can fold the layers just over the end into the end's own layer."""
    if not inside_plate(c, cover, 1, layers):
        return False
    x, y, z = c
    head = max(1, min(END_HEADROOM, max(layers, cover[(x, z)][-1] - y)))
    xn, zn = int(round(_fwd(x))), int(round(_fwd(z)))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            a, b = xn + dx, zn + dz
            xo, zo = int(round(_inv(a))), int(round(_inv(b)))
            if (xo, zo) == (0, 0):                       # tree_rescale: next to the trunk, sample one cell further out
                xo += (a > 0.25) - (a < -0.25)
                zo += (b > 0.25) - (b < -0.25)
            if not covered(cover, (xo, zo), y, head):
                return False
    return True


def limb_inside(logs, a, b, cover, margin=LIMB_RIM_MARGIN, layers=COVER_LAYERS):
    """acacia230: draw the limb a -> b (3-D Bresenham, as limb()) only up to the last cell before the first one that is not
    inside_plate, then step its end back to the last of those cells that is end_inside; the start cell is always kept
    (it is already wood). RNG-free. Returns the cells drawn."""
    cells = line(a, b)
    kept = cells[:1]
    for c in cells[1:]:
        if not inside_plate(c, cover, margin, layers):
            break
        kept.append(c)
    while len(kept) > 1 and not end_inside(kept[-1], cover, layers):
        kept.pop()
    logs.update(kept)
    return kept


def main_limb_inside(logs, a, b, cover, max_y, layers=COVER_LAYERS):
    """acacia230: the main limb a -> b exactly as before (3-D Bresenham, as limb()), minus its cells above max_y (the end
    that sat in the plate's base layer), and when that end is not end_inside it ends instead at the LAST cell of the line
    that is (a tip on the plate's rim steps back inside); no cell inside: kept up to max_y. Every cell drawn is a cell of
    the old limb, so the fork and the limb's lean are unchanged. RNG-free. Returns (the cells drawn, cells cut)."""
    cells = line(a, b)
    keep = [c for c in cells if c[1] <= max_y]           # the line climbs (b is above a), so this is a prefix of it
    k = next((k for k in range(len(keep) - 1, -1, -1) if end_inside(keep[k], cover, layers)), len(keep) - 1)
    logs.update(keep[:k + 1])
    return keep[:k + 1], len(cells) - (k + 1)


def line(a, b):
    """3-D Bresenham (integer cells) from a to b inclusive."""
    a = tuple(int(round(v)) for v in a)
    b = tuple(int(round(v)) for v in b)
    n = max(abs(b[i] - a[i]) for i in range(3))
    return [tuple(int(round(a[i] + (b[i] - a[i]) * k / max(1, n))) for i in range(3)) for k in range(n + 1)]


def limb(logs, a, b, thick=1):
    cells = line(a, b)
    for c in cells:
        logs.add(c)
        if thick > 1:               # a 2-wide run near the trunk: add the +x/+z neighbour for the first part
            logs.add((c[0] + 1, c[1], c[2]))
    return cells[-1]


def column(logs, w, h, x0=0, z0=0, y0=0):
    for x in range(x0, x0 + w):
        for z in range(z0, z0 + w):
            for y in range(y0, y0 + h):
                logs.add((x, y, z))


def oak_elder(rnd, idx):
    """§2.6 old oak / §7: 2x2 trunk, 18-24 tall, fork 3-6, 3-6 scaffold limbs reaching 7-11, clumps r 3-4, 1-2 stag limbs."""
    logs, leaves, extra = set(), set(), set()
    H = rnd.randint(18, 24); fork = rnd.randint(3, 6); R = rnd.uniform(8, 11); heavy = rnd.uniform(0, 2 * math.pi)
    column(logs, 2, fork + 2)
    column(logs, 1, H - 4 - fork, x0=rnd.randint(0, 1), z0=rnd.randint(0, 1), y0=fork + 2)   # the leader thins to 1
    n = rnd.randint(3, 6)
    for i in range(n):
        az = heavy + 2 * math.pi * i / n + rnd.uniform(-0.4, 0.4)
        reach = R * rnd.uniform(0.7, 1.0) * (1 + 0.2 * math.cos(az - heavy))
        y0 = rnd.uniform(fork, fork + 3)
        ang = math.radians(rnd.uniform(40, 80))
        tip = (0.5 + math.cos(az) * reach, y0 + reach / math.tan(ang) * 0.6, 0.5 + math.sin(az) * reach)
        tip = (tip[0], min(tip[1], H - 2), tip[2])
        mid = (0.5 + (tip[0] - 0.5) * 0.5, y0 + (tip[1] - y0) * 0.65, 0.5 + (tip[2] - 0.5) * 0.5)
        limb(logs, (0.5, y0, 0.5), mid); limb(logs, mid, tip)
        rc = rnd.uniform(3.0, 4.0)
        T.ellipsoid(leaves, tip, rc, rc * 0.75, rc, shell=2.0, rnd=rnd)
    stags = []
    for _ in range(rnd.randint(1, 2)):                     # stag limbs: bare logs above the crown
        az = rnd.uniform(0, 2 * math.pi)
        stags.append((0.5 + math.cos(az) * 3, H + rnd.randint(0, 2), 0.5 + math.sin(az) * 3))
    T.ellipsoid(leaves, (0.5, H - 4, 0.5), R * 0.5, R * 0.3, R * 0.5, shell=2.0, rnd=rnd)
    top = sink_stem(logs, leaves, "oak_elder", 2)          # v4
    for tip in stags if STAG_OVER_CROWN else ():
        limb(logs, (0.5, min(H - 5, top), 0.5), tip)
    return logs, leaves, extra, {"H": H, "fork": fork, "radius": round(R, 1), "limbs": n, "trunk_top": top}


def spruce_elder(rnd, idx):
    """§4.6 old spruce: 2x2 trunk, 28-34 (capped), radius 6-8, tiers every 2 with LOG tier branches on the lower
    half, tips dropping 2, 1-3 lowest tiers missing on one side, blunt top on 1 in 4."""
    logs, leaves, extra = set(), set(), set()
    H = rnd.randint(28, 34); R0 = rnd.uniform(6, 8); base = rnd.randint(0, 2)
    column(logs, 2, int(H * 0.6)); column(logs, 1, H - int(H * 0.6) - 1, x0=0, z0=0, y0=int(H * 0.6))
    dead = rnd.uniform(0, 2 * math.pi); missing = rnd.randint(1, 3)
    tiers = list(range(base, H - 2, 2))
    for ti, y in enumerate(tiers):
        t = (y - base) / max(1, H - 2 - base)
        r = R0 * (1 - t) + 0.8
        n = max(4, int(2 * math.pi * r / 1.8))
        for i in range(n):
            az = 2 * math.pi * i / n + rnd.uniform(-0.2, 0.2)
            if ti < missing and math.cos(az - dead) > 0.2:
                continue
            L = r * rnd.uniform(0.85, 1.05)
            tip = (0.5 + math.cos(az) * L, y - (2 if t < 0.5 else 1), 0.5 + math.sin(az) * L)
            if t < 0.5 and i % 2 == 0:                   # log branch on the lower half, every other one
                limb(logs, (0.5, y, 0.5), (0.5 + math.cos(az) * L * 0.6, y, 0.5 + math.sin(az) * L * 0.6))
            T.strand(leaves, (0.5, y, 0.5), tip)
            T.ellipsoid(leaves, tip, 1.0, 0.8, 1.0, rnd=rnd, rough=0.3)
        T.ellipsoid(leaves, (0.5, y, 0.5), min(r, 2.2), 0.8, min(r, 2.2), rnd=rnd, rough=0.2)
    for y in range(H - 2, H + 1):
        leaves.add((0, y, 0))
    if idx % 4 == 0:
        T.ellipsoid(leaves, (0.5, H - 1, 0.5), 1.6, 1.6, 1.6, rnd=rnd, rough=0.2)
    top = sink_stem(logs, leaves, "spruce_elder", 2)       # v4: the leader is leaves
    return logs, leaves, extra, {"H": H, "radius": round(R0, 1), "tiers": len(tiers), "missing_low": missing, "trunk_top": top}


def jungle_elder(rnd, idx):
    """§5.6 old giant (capped): 2x2 trunk 34-40, buttress fins 4-6 (log runs 4-6 up / 4-6 out), clear bole 0.6 H,
    4-6 log limbs reaching 8-12, clumps r 3-4, crown radius 12-14, 1-2 broken limbs."""
    logs, leaves, extra = set(), set(), set()
    H = rnd.randint(34, 40); bole = int(H * rnd.uniform(0.55, 0.68)); R = rnd.uniform(11, 14)
    column(logs, 2, bole + 3)
    for i in range(rnd.randint(4, 6)):                     # buttress fins
        az = 2 * math.pi * i / 6 + rnd.uniform(-0.3, 0.3)
        up, out = rnd.randint(4, 6), rnd.randint(4, 6)
        limb(logs, (0.5 + math.cos(az) * out, 0, 0.5 + math.sin(az) * out), (0.5, up, 0.5))
    n = rnd.randint(4, 6); heavy = rnd.uniform(0, 2 * math.pi); dead = set(rnd.sample(range(n), rnd.randint(1, 2)))
    for i in range(n):
        az = heavy + 2 * math.pi * i / n + rnd.uniform(-0.3, 0.3)
        reach = rnd.uniform(8, 12) * min(1, R / 13); rise = rnd.uniform(3, 6)
        base = (0.5, bole + rnd.uniform(0, 2), 0.5)
        tip = (0.5 + math.cos(az) * reach, base[1] + rise, 0.5 + math.sin(az) * reach)
        mid = (0.5 + (tip[0] - 0.5) * 0.5, base[1] + rise * 0.7, 0.5 + (tip[2] - 0.5) * 0.5)
        limb(logs, base, mid); limb(logs, mid, tip)
        if i in dead:
            continue
        rc = rnd.uniform(3, 4)
        T.ellipsoid(leaves, tip, rc, rc * 0.6, rc, shell=2.0, rnd=rnd)
    dome = R * 0.6
    T.ellipsoid(leaves, (0.5, bole + 4.5, 0.5), dome, dome * 0.4, dome, shell=2.0, rnd=rnd)
    sink_stem(logs, leaves, "jungle_elder", 2)             # v4
    return logs, leaves, extra, {"H": H, "bole": bole, "radius": round(R, 1), "limbs": n, "dead": len(dead)}


def dark_oak_elder(rnd, idx):
    """§6.4 mature/old live oak: 2x2 trunk splitting at 2-4 into 2-4 thick leaders, H 12-18, crown radius 8-12 dense
    dome 6-9 deep, crown base 2-3, 0-3 limbs dipping to 1 block above ground before curving up."""
    logs, leaves, extra = set(), set(), set()
    H = rnd.randint(12, 18); split = rnd.randint(2, 4); R = min(12.0, rnd.uniform(1.0, 1.5) * H / 2)
    column(logs, 2, split)
    n = rnd.randint(2, 4); heavy = rnd.uniform(0, 2 * math.pi)
    for i in range(n):
        az = heavy + 2 * math.pi * i / n + rnd.uniform(-0.4, 0.4)
        reach = R * rnd.uniform(0.6, 0.95); top = rnd.uniform(H * 0.6, H - 1)
        mid = (0.5 + math.cos(az) * reach * 0.45, split + (top - split) * 0.6, 0.5 + math.sin(az) * reach * 0.45)
        tip = (0.5 + math.cos(az) * reach, top, 0.5 + math.sin(az) * reach)
        limb(logs, (0.5, split, 0.5), mid, thick=2); limb(logs, mid, tip)
        rc = rnd.uniform(3.5, 4.5)
        T.ellipsoid(leaves, tip, rc, rc * 0.7, rc, shell=2.0, rnd=rnd)
    for _ in range(rnd.randint(0, 3)):                     # ground-sweeping limbs
        az = rnd.uniform(0, 2 * math.pi); out = rnd.uniform(4, 7)
        low = (0.5 + math.cos(az) * out * 0.6, 1, 0.5 + math.sin(az) * out * 0.6)
        tip = (0.5 + math.cos(az) * out, 3, 0.5 + math.sin(az) * out)
        limb(logs, (0.5, split, 0.5), low); limb(logs, low, tip)
        T.ellipsoid(leaves, tip, 2.5, 2.0, 2.5, shell=1.5, rnd=rnd)
    T.ellipsoid(leaves, (0.5, H * 0.65, 0.5), R * 0.8, (H * 0.5) * 0.45, R * 0.8, shell=2.5, rnd=rnd)
    sink_stem(logs, leaves, "dark_oak_elder", 2)           # v4
    return logs, leaves, extra, {"H": H, "split": split, "radius": round(R, 1), "leaders": n}


def pale_oak_elder(rnd, idx):
    """§7.4 veteran: 2x2 trunk 10-16 (split into 2-3 columns on 1 in 3), first limbs at 2-4, live crown radius 5-9
    sitting low, 2-4 dead stag limbs rising 2-5 above the leaves, epicormic tufts on the trunk, 20-40 % holes."""
    logs, leaves, extra = set(), set(), set()
    H = rnd.randint(10, 16); R = rnd.uniform(5, 9); first = rnd.randint(2, 4)
    split = idx % 3 == 0
    if split:
        column(logs, 2, first)
        for (x, z) in rnd.sample([(0, 0), (1, 0), (0, 1), (1, 1)], rnd.randint(2, 3)):
            column(logs, 1, H - first - rnd.randint(0, 3), x0=x, z0=z, y0=first)
    else:
        column(logs, 2, H - 2)
    crown_top = H * rnd.uniform(0.5, 0.8)
    n = rnd.randint(3, 5)
    for i in range(n):
        az = 2 * math.pi * i / n + rnd.uniform(-0.4, 0.4)
        reach = R * rnd.uniform(0.6, 1.0)
        tip = (0.5 + math.cos(az) * reach, min(crown_top, first + reach * 0.5), 0.5 + math.sin(az) * reach)
        limb(logs, (0.5, first + rnd.uniform(0, 2), 0.5), tip)
        rc = rnd.uniform(2.5, 3.5)
        T.ellipsoid(leaves, tip, rc, rc * 0.7, rc, shell=2.0, rnd=rnd, rough=0.35)
    stags = []
    for _ in range(rnd.randint(2, 4)):                     # stag limbs
        az = rnd.uniform(0, 2 * math.pi); up = rnd.randint(2, 5)
        stags.append((0.5 + math.cos(az) * rnd.uniform(2, 5), crown_top + up, 0.5 + math.sin(az) * rnd.uniform(2, 5)))
    for _ in range(rnd.randint(2, 4)):                     # epicormic tufts on the trunk
        y = rnd.randint(2, max(3, H - 3)); az = rnd.uniform(0, 2 * math.pi)
        leaves.add((int(round(0.5 + math.cos(az) * 1.5)), y, int(round(0.5 + math.sin(az) * 1.5))))
    holes = rnd.uniform(0.2, 0.4)
    leaves = {c for c in leaves if rnd.random() > holes * 0.5}
    top = sink_stem(logs, leaves, "pale_oak_elder", 2, "crown")  # v4: open centre -> anchored at the crown's top
    for tip in stags if STAG_OVER_CROWN else ():
        limb(logs, (0.5, min(H - 4, top), 0.5), tip)
    return logs, leaves, extra, {"H": H, "radius": round(R, 1), "split": split, "crown_top": round(crown_top, 1), "trunk_top": top}


def acacia(rnd, idx):
    """§8.4 mature/old umbrella thorn: trunk 1, fork at 1-3 into 2-4 limbs leaning 25-45 deg, flat canopy 1-2 thick,
    radius 5-9, underside 5-9 up; 1-3 plates at slightly different heights; 1 in 6 rounded (raddiana); old: 2 leaners + dead limb.
    acacia230: every limb ends inside its plate — the main limb ends one layer under the plate (LIMB_DROP), stepped back
    inside when its tip sat on the rim (main_limb_inside); the secondaries rise from the main limb under the plate's centre
    and stop inside the plate's covered interior (limb_inside); the dead limb stays in the canopy's shadow."""
    logs, leaves, extra = set(), set(), set()
    old = idx % 3 == 2
    H = rnd.randint(9, 14) if old else rnd.randint(7, 12); fork = rnd.randint(1, 3); R = min(9.0, rnd.uniform(1.2, 2.5) * H / 2)
    column(logs, 1, fork + 1)
    n = 2 if old else rnd.randint(2, 4); plates = rnd.randint(1, 3); rounded = idx % 6 == 1
    heavy = rnd.uniform(0, 2 * math.pi)
    for i in range(n):
        az = heavy + 2 * math.pi * i / n + rnd.uniform(-0.5, 0.5)
        ang = math.radians(rnd.uniform(25, 45)); top = H - rnd.randint(0, 2) - (i % plates)
        reach = (top - fork) * math.tan(ang)
        tip = (math.cos(az) * reach, top, math.sin(az) * reach)
        # the plate: a flat disc around the limb end, 1-2 thick
        pr = R * rnd.uniform(0.5, 0.8)
        plate = set()                                      # acacia230: the plate kept apart so its limbs can be fitted to it
        T.ellipsoid(plate, (tip[0] * 0.7, top + 0.5, tip[2] * 0.7), pr, rnd.uniform(0.8, 1.4) if not rounded else pr * 0.45, pr, rnd=rnd, rough=0.25)
        leaves |= plate
        # acacia230: the main limb is drawn after its plate (limb drawing takes no random numbers, so every draw keeps its
        # place): the same line, ending LIMB_DROP under the plate's base layer (was: in it), stepped back inside the plate
        # when its tip sat on the rim
        cover = plate_cover(plate)
        low = top - LIMB_DROP if top - LIMB_DROP > fork else top
        drawn, _cut = main_limb_inside(logs, (0, fork, 0), tip, cover, low)
        cx, cz = tip[0] * 0.7, tip[2] * 0.7                 # the plate's centre
        hub = min(drawn, key=lambda c: ((c[0] - cx) ** 2 + (c[2] - cz) ** 2, -c[1]))
        for _ in range(rnd.randint(2, 4)):                 # secondary limbs under the plate
            a2 = az + rnd.uniform(-1.0, 1.0); L2 = pr * rnd.uniform(0.5, 0.9)
            # acacia230: same draws, read from the plate's centre instead of the limb tip. They used to run from the tip
            # (0.3 x reach outside the centre) pr x 0.5-0.9 further out, i.e. up to 1.39 plate radii from the centre, past
            # the rim. Now each rises from the main limb's cell under the plate's centre (the hub) to LIMB_DROP under the
            # plate, towards centre + L2 in the same direction, and stops before it leaves the plate's covered interior
            limb_inside(logs, hub, (cx + math.cos(a2) * L2, low, cz + math.sin(a2) * L2), cover)
    if old:
        az = rnd.uniform(0, 2 * math.pi)
        dead_end = (math.cos(az) * 4, fork + 3, math.sin(az) * 4)
        if DEAD_LIMB_UNDER_CANOPY:                         # acacia230: the dead limb stays in the canopy's shadow
            limb_inside(logs, (0, fork, 0), dead_end, plate_cover(leaves), LIMB_RIM_MARGIN, 1)
        else:
            limb(logs, (0, fork, 0), dead_end)
    sink_stem(logs, leaves, "acacia", 1)                   # v4
    return logs, leaves, extra, {"H": H, "fork": fork, "radius": round(R, 1), "limbs": n, "plates": plates, "old": old}


def cherry(rnd, idx):
    """§9.5 mature/old: fork at 2 into 3-5 scaffolds rising 3-4 then bending out near-horizontal, radius 5-6 (old 7-10,
    sagging outer limbs to 2-3 above ground), blossom clouds 2-3 thick in 1-3 layers with a 1-block gap, 1 dead limb on old."""
    logs, leaves, extra = set(), set(), set()
    old = idx % 3 == 2
    H = rnd.randint(9, 12) if old else rnd.randint(8, 11); R = rnd.uniform(7, 10) if old else rnd.uniform(5, 6)
    column(logs, 1, 2)
    n = rnd.randint(3, 5); layers = rnd.randint(1, 3); heavy = rnd.uniform(0, 2 * math.pi)
    for i in range(n):
        az = heavy + 2 * math.pi * i / n + rnd.uniform(-0.4, 0.4)
        rise = rnd.randint(3, 4); reach = R * rnd.uniform(0.7, 1.0)
        knee = (math.cos(az) * rise * 0.5, 2 + rise, math.sin(az) * rise * 0.5)
        sag = rnd.uniform(1, 3) if old else rnd.uniform(0, 1)
        tip = (math.cos(az) * reach, max(2.5, 2 + rise - sag), math.sin(az) * reach)
        limb(logs, (0, 2, 0), knee); limb(logs, knee, tip)
        for k in range(layers):
            T.ellipsoid(leaves, (tip[0] * (0.75 + 0.1 * k), tip[1] + 1 + k * 3.5, tip[2] * (0.75 + 0.1 * k)), R * 0.45, 1.3, R * 0.45, rnd=rnd, rough=0.3)
    T.ellipsoid(leaves, (0, 2 + 4 + 1, 0), R * 0.5, 1.4, R * 0.5, rnd=rnd, rough=0.3)
    if old:
        az = rnd.uniform(0, 2 * math.pi)
        limb(logs, (0, 2, 0), (math.cos(az) * 3, 5, math.sin(az) * 3))
    sink_stem(logs, leaves, "cherry", 1)                   # v4
    return logs, leaves, extra, {"H": H, "radius": round(R, 1), "scaffolds": n, "layers": layers, "old": old}


def mangrove(rnd, idx):
    """§10.4 mature/old red mangrove: trunk 8-14 (old 14-18), prop roots from 2-4 up arching 2-3 out then stepping
    down (6-12 roots, root cage radius 3-6), 2-4 drop roots from limbs, round dense crown radius 4-6 from 5-7 up.
    Roots are minecraft:mangrove_roots blocks; the trunk and limbs mangrove logs."""
    logs, leaves, extra = set(), set(), set()
    old = idx % 3 == 2
    H = rnd.randint(14, 18) if old else rnd.randint(8, 14); R = rnd.uniform(6, 8) if old else rnd.uniform(4, 6)
    start = max(2, int(H * rnd.uniform(0.1, 0.33)))
    column(logs, 1, H - 2)
    nroots = rnd.randint(10, 14) if old else rnd.randint(6, 12)
    for i in range(nroots):
        az = 2 * math.pi * i / nroots + rnd.uniform(-0.2, 0.2)
        y0 = rnd.randint(start, start + 2); out1 = rnd.uniform(2, 3)
        p1 = (math.cos(az) * out1, y0 - 1, math.sin(az) * out1)
        for c in line((0, y0, 0), p1):
            extra.add(c)
        cur = p1
        for _ in range(rnd.randint(1, 2)):                  # second / third order arches, lower and further out
            out2 = rnd.uniform(1, 2)
            nxt = (cur[0] + math.cos(az) * out2, max(1, cur[1] - rnd.randint(1, 2)), cur[2] + math.sin(az) * out2)
            for c in line(cur, nxt):
                extra.add(c)
            cur = nxt
        for c in line(cur, (cur[0], 0, cur[2])):            # down to the ground
            extra.add(c)
    cb = rnd.randint(5, 7)
    n = rnd.randint(3, 5)
    for i in range(n):
        az = 2 * math.pi * i / n + rnd.uniform(-0.4, 0.4); reach = R * rnd.uniform(0.6, 0.9)
        tip = (math.cos(az) * reach, cb + rnd.uniform(1, 3), math.sin(az) * reach)
        limb(logs, (0, cb, 0), tip)
        T.ellipsoid(leaves, tip, R * 0.5, R * 0.4, R * 0.5, shell=1.8, rnd=rnd)
        if rnd.random() < 0.5:                              # drop root from the limb
            for c in line(tip, (tip[0], 0, tip[2])):
                if c not in logs:
                    extra.add(c)
    T.ellipsoid(leaves, (0, cb + 2.5, 0), R, R * (0.6 if old else 0.75), R, shell=2.0, rnd=rnd)
    sink_stem(logs, leaves, "mangrove", 1)                 # v4
    return logs, leaves, extra, {"H": H, "radius": round(R, 1), "roots": nroots, "root_start": start, "old": old}


GEN = {"oak_elder": oak_elder, "spruce_elder": spruce_elder, "jungle_elder": jungle_elder, "dark_oak_elder": dark_oak_elder,
       "pale_oak_elder": pale_oak_elder, "acacia": acacia, "cherry": cherry, "mangrove": mangrove}


def axis_of(prev, c, nxt):
    d = [abs((nxt or c)[i] - (prev or c)[i]) for i in range(3)]
    return "xyz"[max(range(3), key=lambda i: d[i])] if max(d) else "y"


def build(species, idx):
    rnd = random.Random(zlib.crc32(f"{species}/elder/{idx}".encode()))
    log_id, leaf_id, root_id, w, vanilla = SPEC[species]
    logs, leaves, extra, info = GEN[species](rnd, idx)
    logs = {(int(x), int(y), int(z)) for x, y, z in logs if y >= 0}
    extra = {(int(x), int(y), int(z)) for x, y, z in extra if y >= 0} - logs
    leaves = {c for c in leaves if c[1] >= 1 and c not in logs and c not in extra}
    allc = leaves | logs | extra
    leaves = {c for c in leaves if any((c[0] + dx, c[1] + dy, c[2] + dz) in allc
                                       for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)))}
    cells = logs | leaves | extra
    xs = [c[0] for c in cells]; zs = [c[2] for c in cells]; ys = [c[1] for c in cells]
    x0, z0 = min(xs), min(zs)
    size = (max(xs) - x0 + 1, max(ys) + 1, max(zs) - z0 + 1)
    st = M.Structure(size)
    root = (-x0, 0, -z0)
    logs_local = {(x - x0, y, z - z0) for x, y, z in logs}
    for (x, y, z) in logs_local:
        if (x, y, z) == root and root_id:
            st.set(x, y, z, root_id, {"pw:tpl": M.i(idx % 16), "pw:tpl_hi": M.i(idx // 16), "minecraft:cardinal_direction": M.s("north")})
            continue
        if vanilla:
            nb = [(dx, dy, dz) for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)) if (x + dx, y + dy, z + dz) in logs_local]
            ax = "y"
            if nb and not any(d[1] for d in nb):
                ax = "x" if any(d[0] for d in nb) else "z"
            st.set(x, y, z, log_id, {"pillar_axis": M.s(ax)})
        else:
            st.set(x, y, z, log_id, {"pw:variant": M.i(T.cell_hash(x, y, z) % 5), "pw:rseed": M.b(1),
                                     "pw:top_variant": M.i((T.cell_hash(x, y, z) >> 5) % 7)})
    for (x, y, z) in extra:
        st.set(x - x0, y, z - z0, "minecraft:mangrove_roots")
    for x, y, z in leaves:
        lx, lz = x - x0, z - z0
        d = min((abs(lx - a) + abs(y - b) + abs(lz - c) for a, b, c in logs_local), default=99)
        st.set(lx, y, lz, leaf_id, {"pw:variant": M.i(T.leaf_look(lx, y, lz, d)), "pw:off": M.i((lx + 2 * y + 4 * lz) % 7),
                                    "pw:rseed": M.b(1), "pw:section": M.i(0), "pw:exposure": M.i(0), "pw:section_rolled": M.b(1)})
    info.update({"size": size, "root_local": root, "logs": len(logs_local), "leaves": len(leaves), "extra": len(extra)})
    return st, info, logs, leaves, extra


def main():
    species = sys.argv[1:] or list(SPEC)
    for sp in species:
        report, rows = [], []
        for idx in range(PER):
            st, info, logs, leaves, extra = build(sp, idx)
            p = OUT / sp / f"{sp}_elder_{idx:02d}.mcstructure"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(st.to_bytes())
            rows.append((logs | extra, leaves, info))
            report.append({"id": f"{sp}_elder_{idx:02d}", **{k: (list(v) if isinstance(v, tuple) else v) for k, v in info.items()}})
        (OUT / sp / "REPORT.json").write_text(json.dumps(report, indent=1))
        size = T.render_sheet(sp, [("elder", rows)], f"/mnt/user-data/outputs/TREE-SQUARE-{sp}.png")
        print(sp, "templates", len(report), "sheet", size, report[0])


if __name__ == "__main__":
    main()
