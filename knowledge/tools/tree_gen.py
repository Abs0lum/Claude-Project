#!/usr/bin/env python3
"""tree_gen.py — tree program T1 (his 13:31 + 14:13 rulings, D-C457 / D-C460): 16 unique trees per dodecagon species PER
AGE (young / mature / old), trunk + accurate canopy, NO log branches (dodecagon logs only stack vertically), built from
_docs/trees/TREE-ARCHITECTURE-RESEARCH-2026-10-02.md. PILOT = oak (§2): Rauh 'fruit-tree' model, decurrent when mature,
foliage as an outer shell of clumps at the ends of (hidden) scaffold limbs, retrenched + stag-headed when old.

Per tree (all numbers in blocks, 1 block = 1 m; research §2.6):
  young   H 7–12, crown base 2–3, crown radius 2–3, ovoid: one leader + 3–5 small side clumps at 45–60° from vertical
  mature  H 16–22, fork 0.15–0.35 H, crown base 3–5, 3–6 scaffold clumps at 40–80° from vertical reaching 0.7–1.0 of a
          crown radius = (0.8–1.1 H) / 2 (capped 10), clumps radius 2.5–3.5, vertically flattened, hollow beyond 2 blocks
          of shell; thin leaf 'limb strands' tie each clump to the trunk top so nothing floats
  old     H 14–19 (shorter than mature, §1.5), wider and lower crown, radius 8–11, 4–7 clumps, 1 heavy side; the trunk's
          dead leader stands 2–4 blocks above the live crown (stag head)
Leaves are baked FINAL (T0 P-1: worldgen keeps custom states): pw:variant = the game's own look rule (pwLeafLook: hash of
the cell; 5–6 near the wood by Manhattan distance within band 3) on LOCAL coordinates; pw:off = (x+2y+4z) mod 7 (local;
unique for every neighbour pair under all 4 rotations, CALC 10-02); pw:rseed / pw:section_rolled = true (assigned).
The lowest trunk cell is kept as 'root' (the T2 root block replaces it). Deterministic: seed = species/age/index.
Usage: tree_gen.py oak  -> _staging/trees/oak/<oak_age_nn>.mcstructure + TREE-PILOT-oak.png"""
import json
import math
from collections import Counter
import random
import sys
import zlib
from pathlib import Path

import numpy as np

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

OUT = Path("/home/claude/_staging/trees")
LOG = {sp: {age: f"pw:{sp}_{age}" for age in ("young", "mature", "old")} for sp in ("oak", "birch", "spruce", "jungle")}
LEAF = {sp: f"pw:{sp}_leaves" for sp in ("oak", "birch", "spruce", "jungle")}
PER_AGE = 24          # his TC = a + "add more ... 16 or 32 ... defer" -> 24 per age (D-C484)
BAND = 3


def cell_hash(x, y, z):
    """pwCellHash (main.js 2119) in Python, exact 32-bit."""
    def imul(a, b):
        return (a * b) & 0xFFFFFFFF
    h = (imul(x & 0xFFFFFFFF, 73856093) ^ imul(y & 0xFFFFFFFF, 19349663) ^ imul(z & 0xFFFFFFFF, 83492791)) & 0xFFFFFFFF
    h ^= h >> 16
    h = imul(h, 2246822507)
    h ^= h >> 13
    h = imul(h, 3266489909)
    h ^= h >> 16
    return h


def leaf_look(x, y, z, wood_d):
    h = cell_hash(x, y, z)
    if wood_d == 1:
        return 5 + (h % 2)
    if 2 <= wood_d <= BAND and ((h >> 8) & 1) == 1:
        return 5 + ((h >> 9) % 2)
    return (h >> 12) % 5


def ellipsoid(cells, c, rx, ry, rz, shell=None, rnd=None, rough=0.18):
    cx, cy, cz = c
    for x in range(int(cx - rx - 1), int(cx + rx + 2)):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for z in range(int(cz - rz - 1), int(cz + rz + 2)):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2
                if d > 1.0:
                    continue
                if shell is not None:
                    inner = ((x - cx) / max(0.5, rx - shell)) ** 2 + ((y - cy) / max(0.5, ry - shell)) ** 2 + \
                            ((z - cz) / max(0.5, rz - shell)) ** 2
                    if inner < 1.0:
                        continue
                if rnd is not None and d > 0.72 and rnd.random() < rough:   # ragged outer edge
                    continue
                cells.add((x, y, z))


def strand(cells, a, b):
    """1-wide leaf line from a to b (the hidden scaffold limb's foliage)."""
    n = int(max(abs(b[i] - a[i]) for i in range(3))) + 1
    for k in range(n + 1):
        t = k / max(1, n)
        cells.add(tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)))


def oak(age, idx):
    rnd = random.Random(zlib.crc32(f"oak/{age}/{idx}".encode()))
    leaves, trunk = set(), []
    heavy = rnd.uniform(0, 2 * math.pi)                         # azimuth of the heavy side (§2.6 variation 4)
    if age == "young":
        H = rnd.randint(7, 12)
        cb = rnd.randint(2, 3)
        R = rnd.uniform(2.0, 3.0)
        top = H - 1
        trunk = [(0, y, 0) for y in range(0, top)]
        mid = cb + (H - cb) * 0.55
        ellipsoid(leaves, (0, mid, 0), R, (H - cb) / 2 + 0.3, R * rnd.uniform(0.85, 1.1), rnd=rnd)
        for _ in range(rnd.randint(3, 5)):
            az = rnd.uniform(0, 2 * math.pi)
            ang = math.radians(rnd.uniform(45, 60))
            y0 = rnd.uniform(cb + 1, H - 2)
            L = R * rnd.uniform(0.7, 1.0)
            c = (math.cos(az) * math.sin(ang) * L, y0 + math.cos(ang) * L * 0.5, math.sin(az) * math.sin(ang) * L)
            ellipsoid(leaves, c, rnd.uniform(1.2, 1.8), rnd.uniform(1.0, 1.5), rnd.uniform(1.2, 1.8), rnd=rnd)
        info = {"H": H, "crown_base": cb, "radius": round(R, 1)}
    else:
        old = age == "old"
        H = rnd.randint(14, 19) if old else rnd.randint(16, 22)
        spread = rnd.uniform(0.9, 1.25) * H if old else rnd.uniform(0.8, 1.1) * H
        R = min(11.0 if old else 10.0, spread / 2)
        cb = rnd.randint(2, 4) if old else rnd.randint(3, 5)
        fork = int(round(H * rnd.uniform(0.15, 0.35)))
        fork = max(fork, cb + 1)
        crown_top = H - (rnd.randint(2, 4) if old else 1)       # old: dead leader stands above the live crown
        trunk_top = H - 1 if old else max(fork + 2, int(H * rnd.uniform(0.6, 0.75)))
        trunk = [(0, y, 0) for y in range(0, trunk_top + 1)]
        n = rnd.randint(6, 9) if old else rnd.randint(5, 8)
        tip = (0, trunk_top, 0)
        for i in range(n):
            az = heavy + (2 * math.pi * i / n) + rnd.uniform(-0.45, 0.45)
            bias = 1.0 + 0.25 * math.cos(az - heavy)            # the heavy side reaches further
            ang = math.radians(rnd.uniform(55, 85) if old else rnd.uniform(40, 80))
            L = R * rnd.uniform(0.55, 0.85) * bias
            base = (0, rnd.uniform(fork, min(trunk_top, crown_top - 2)), 0)
            c = (base[0] + math.cos(az) * math.sin(ang) * L,
                 min(crown_top - 1.5, base[1] + math.cos(ang) * L * (0.55 if old else 0.75)),
                 base[2] + math.sin(az) * math.sin(ang) * L)
            rx = rnd.uniform(3.0, 4.2) * (1.1 if old else 1.0)
            ry = rx * (rnd.uniform(0.55, 0.7) if old else rnd.uniform(0.7, 0.9))
            ellipsoid(leaves, c, rx, ry, rx * rnd.uniform(0.85, 1.15), shell=2.0, rnd=rnd)
            strand(leaves, (0, base[1], 0), c)
            strand(leaves, (0, base[1] + 1, 0), (c[0], c[1] + 1, c[2]))
        # crown cap over the trunk top (mature only: the leader is lost among the limbs)
        dome_r = R * (0.55 if old else 0.5)
        ellipsoid(leaves, (0, (trunk_top + 1) if not old else crown_top - 2, 0), dome_r, dome_r * (0.4 if old else 0.5),
                  dome_r * rnd.uniform(0.85, 1.15), shell=2.0, rnd=rnd)
        info = {"H": H, "crown_base": cb, "fork": fork, "radius": round(R, 1), "clumps": n, "trunk_top": trunk_top}
    trunk, core, _gone = sink_tip(trunk, leaves, TRUNK_TIP_DEPTH["oak"][age])     # v4: the tip under the apex
    leaves |= set(core)
    info["trunk_top"] = max(c[1] for c in trunk)
    trunk_set = set(trunk)
    leaves = {c for c in leaves if c not in trunk_set and c[1] >= 1}
    # drop leaves that touch nothing (no face neighbour among leaves or trunk): no single floating cubes
    allc = leaves | trunk_set
    leaves = {c for c in leaves if any((c[0] + dx, c[1] + dy, c[2] + dz) in allc
                                       for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)))}
    return trunk, leaves, info


def finish(trunk, leaves):
    trunk_set = set(trunk)
    leaves = {c for c in leaves if c not in trunk_set and c[1] >= 1}
    allc = leaves | trunk_set
    leaves = {c for c in leaves if any((c[0] + dx, c[1] + dy, c[2] + dz) in allc
                                       for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)))}
    return leaves


# v4 (10-06, his "make sure the trunk isn't sticking out too high and that it's not noticeable at the top of the tree"):
# EVERY species' trunk tip sits TRUNK_TIP_DEPTH crown layers under the crown's own apex over the stem (birch v3's rule,
# anchored at the apex instead of the crown base so conifers / emergents keep their visible stems); never cut lower than
# one block into the crown (birch v3's floor). RNG-free: applied after the crown is built, so every crown keeps its cells.
TRUNK_TIP_DEPTH = {"oak": {"young": 4, "mature": 5, "old": 5},
                   "spruce": {"young": 3, "mature": 4, "old": 4},
                   "jungle": {"young": 4, "mature": 3, "old": 3}}


def crown_base_of(leaves):
    """the lowest leaf layer with >= 4 leaves (tree_rescale / tree_proportions' CBH)."""
    per = Counter(c[1] for c in leaves)
    return min((y for y, c in per.items() if c >= 4), default=min(per) if per else 1)


def sink_tip(trunk, leaves, depth, anchor="stem"):
    """-> (kept, core, gone). apex = the highest leaf over the trunk's top cells (their column and the 8 around it), never
    above the crown's own top (a tuft on a bare leader does not count); the crown's top when nothing is over the stem or
    anchor == "crown" (an open-centred crown: pale oak); cut = max(crown base + 1, apex - depth). Trunk cells above the
    cut leave the trunk: at or under the apex they become leaves (the crown's core, as birch v3), above the apex they are
    dropped (no bare leader / stag head over the crown)."""
    trunk = list(trunk)
    if not trunk or not leaves:
        return trunk, [], []
    top = max(c[1] for c in trunk)
    cols = {(c[0] + dx, c[2] + dz) for c in trunk if c[1] == top for dx in (-1, 0, 1) for dz in (-1, 0, 1)}
    over = [c[1] for c in leaves if (c[0], c[2]) in cols]
    crown_top = max(c[1] for c in leaves)
    apex = crown_top if (anchor == "crown" or not over) else min(max(over), crown_top)
    cut = max(crown_base_of(leaves) + 1, apex - depth)
    kept = [c for c in trunk if c[1] <= cut]
    core = [c for c in trunk if cut < c[1] <= apex]
    gone = [c for c in trunk if c[1] > max(cut, apex)]
    return kept, core, gone


BIRCH_TRUNK_INTO_CROWN = 1     # v3 (10-05, his 16:50): the trunk ends this many blocks above the crown's base (was: to the top)


def birch(age, idx):
    """v2 (1004b, his 15:27 "birches look incomplete and broken - not fully created"; D-C566). §3.6 kept: slim crown never
    wider than ~0.5 H (radius <= 0.25 H), crown base 2 (young) / 4-7 (mature) / 5-8 (old), pendulous outer twigs, 4 of 24
    mature/old = 2-4-stem clumps (paper birch), trunk lean 0-8° as an S-curve. NEW: the crown is a CONTINUOUS egg (a
    hollow shell 2.2 thick: wider shoulder low, a solid cap over the leader, a leafy sheath wrapping the trunk so every
    stem touches leaves), with 6-10 hanging curtains 1-2 blocks below the shoulder rim; the old tree keeps a 1-2 block dead
    leader above a lopsided (shifted, never thinned-out) crown. v1 (strands + r 1.2 droop clumps, rough 0.3) left 26 /
    157 / 138 scattered leaves per age and bare tops — the 'broken' look."""
    rnd = random.Random(zlib.crc32(f"birch/{age}/{idx}".encode()))
    leaves, trunk = set(), []
    core = []                                                       # v3: the trunk column above the cut -> leaves (the crown's core)
    if age == "young":
        H = rnd.randint(6, 9); cb = 2
        R = rnd.uniform(1.6, 2.3)
        cut = cb + BIRCH_TRUNK_INTO_CROWN
        trunk = [(0, y, 0) for y in range(0, min(H - 1, cut + 1))]
        core = [(0, y, 0) for y in range(cut + 1, H - 1)]
        ch = H + 1 - cb                                             # crown height, the tip one above the last log
        body_c = (0, cb + ch * 0.45, 0)
        ellipsoid(leaves, body_c, R, ch * 0.5 + 0.3, R * rnd.uniform(0.9, 1.1), rnd=rnd, rough=0.12)
        ellipsoid(leaves, (0, cb + ch * 0.3, 0), R * 1.1, ch * 0.28, R * 1.1, rnd=rnd, rough=0.12)     # the shoulder
        ellipsoid(leaves, (0, H - 0.5, 0), R * 0.55, 1.6, R * 0.55, rnd=rnd, rough=0.1)                 # the cap
        for i in range(rnd.randint(3, 5)):                          # a few hanging twigs at the rim
            az = rnd.uniform(0, 2 * math.pi); rr = R * rnd.uniform(0.7, 1.0)
            x, z = int(round(math.cos(az) * rr)), int(round(math.sin(az) * rr))
            y0 = int(round(cb + ch * 0.3))
            for k in range(rnd.randint(1, 2) + 1):
                leaves.add((x, y0 - k, z))
        info = {"H": H, "crown_base": cb, "radius": round(R, 1)}
    else:
        old = age == "old"
        H = rnd.randint(16, 22) if old else rnd.randint(14, 20)
        R = min(rnd.uniform(3.4, 4.8) if old else rnd.uniform(3.0, 4.2), 0.25 * H)
        cb = rnd.randint(5, 8) if old else rnd.randint(4, 7)
        clump = idx % 6 == 5                                        # 4 of 24: a 2-4 stem clump
        stems = [(0, 0)]
        if clump:
            for _ in range(rnd.randint(1, 3)):
                stems.append((rnd.choice((-1, 1)), rnd.choice((-1, 0, 1))))
        lean = math.radians(rnd.uniform(0, 8)); laz = rnd.uniform(0, 2 * math.pi)
        heavy = rnd.uniform(0, 2 * math.pi)                         # the old tree's crown leans to one side
        tops = []
        for si, (sx, sz) in enumerate(stems):
            h = H - (0 if si == 0 else rnd.randint(2, 5))
            dead = rnd.randint(1, 2) if old else 0                  # the dead leader stands above the live crown
            top = h - 1
            cut = cb + BIRCH_TRUNK_INTO_CROWN                       # v3 (his 16:50): the white trunk stops at the crown's base
            last = None
            for y in range(0, top + 1):
                k = math.sin(math.pi * y / max(1, top)) * math.tan(lean) * y * 0.5     # S-curve lean: out, then back
                x = int(round(sx + math.cos(laz) * k)); z = int(round(sz + math.sin(laz) * k))
                (trunk if y <= cut else core).append((x, y, z))
                last = (x, y, z)
            tops.append((last[0], top, last[2], dead))
        for (tx, ty, tz, dead) in tops:
            live_top = ty - dead                                    # the crown's apex sits at the live top (+1)
            ch = max(4, live_top + 1 - cb)
            rr = R if len(tops) == 1 else R * rnd.uniform(0.6, 0.8)  # clump stems carry smaller crowns that merge
            ox = oz = 0.0
            if old:                                                 # lopsided: the whole crown shifts, nothing is thinned out
                ox, oz = math.cos(heavy) * rr * 0.3, math.sin(heavy) * rr * 0.3
            cx, cz = tx + ox, tz + oz
            rz = rr * rnd.uniform(0.9, 1.1)
            ry = ch * (0.46 if old else 0.5)
            ellipsoid(leaves, (cx, cb + ch * 0.45, cz), rr, ry + 0.4, rz, shell=2.2, rnd=rnd, rough=0.14)        # the egg
            ellipsoid(leaves, (cx, cb + ch * 0.32, cz), rr * 1.08, ch * 0.3, rz * 1.08, shell=2.2, rnd=rnd, rough=0.14)  # the shoulder
            ellipsoid(leaves, (tx, live_top + 0.5, tz), rr * 0.5, 1.8, rr * 0.5, rnd=rnd, rough=0.1)                   # the cap over the leader
            for y in range(cb, live_top + 1):                       # the sheath: every stem log inside the crown touches leaves
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    leaves.add((tx + dx, y, tz + dz))
            for i in range(rnd.randint(6, 10)):                     # pendulous curtains below the shoulder rim
                az = rnd.uniform(0, 2 * math.pi); d = rr * rnd.uniform(0.72, 1.0)
                x, z = int(round(cx + math.cos(az) * d)), int(round(cz + math.sin(az) * d * (rz / rr)))
                y0 = int(round(cb + ch * 0.18))
                for k in range(rnd.randint(1, 2) + 1):
                    leaves.add((x, y0 - k, z))
                    if rnd.random() < 0.5:
                        leaves.add((x + rnd.choice((-1, 1)), y0 - k, z))
        info = {"H": H, "crown_base": cb, "radius": round(R, 1), "stems": len(stems)}
    leaves |= set(core)                                             # v3: the hidden leader is leaves now (a leafy core, no hollow)
    info["trunk_top"] = max(c[1] for c in trunk)
    return trunk, finish(trunk, leaves), info


def spruce(age, idx):
    """§4.6: tiers to the ground (lowest 0-2 up), tier every 1 block (young) / 2 blocks (mature, old), bottom radius
    0.3-0.5 H (young) / 5-7 (mature, spread 0.5 H) / 6-8 (old), tapering linearly to the leader; outer half of each tier
    drops 1 block (lower third 1-2; old 2), top fifth angled up; 1 in 12 a blunt double leader; forest variants (crown
    base 0.4-0.6 H, bare log + dead stubs) 1 in 4 of mature; narrow Engelmann (spread 0.25 H) 1 in 6."""
    rnd = random.Random(zlib.crc32(f"spruce/{age}/{idx}".encode()))
    leaves, trunk = set(), []
    old = age == "old"
    if age == "young":
        H = rnd.randint(6, 10); R0 = rnd.uniform(0.3, 0.5) * H; base = rnd.randint(0, 1); step = 1; forest = False
    elif old:
        H = rnd.randint(22, 30); R0 = rnd.uniform(6.0, 8.0); base = rnd.randint(0, 2); step = 2; forest = False
    else:
        H = rnd.randint(18, 26); forest = idx % 4 == 3
        R0 = rnd.uniform(5.0, 7.0) if not forest else rnd.uniform(3.0, 4.0)
        base = int(H * rnd.uniform(0.4, 0.6)) if forest else rnd.randint(0, 2); step = 2
    if idx % 6 == 2:                                     # narrow Engelmann
        R0 = min(R0, 0.25 * H)
    R0 = min(R0, 9.0)
    leader = rnd.randint(1, 2)
    top = H - leader
    trunk = [(0, y, 0) for y in range(0, top + 1)]
    double = idx % 12 == 7
    if double:
        trunk.append((1, top, 0)); trunk.append((1, top - 1, 0))
    dead_side = rnd.uniform(0, 2 * math.pi) if old else None
    tiers = list(range(base, top + 1, step))
    for ti, y in enumerate(tiers):
        t = (y - base) / max(1, top - base)
        r = R0 * (1.0 - t) + 0.6
        up = t > 0.8
        drop = 2 if (old or t < 0.33) and not up else (1 if not up else -1)
        if old and ti < 3 and dead_side is not None:
            pass
        n = max(4, int(2 * math.pi * r / 1.6))
        for i in range(n):
            az = 2 * math.pi * i / n + rnd.uniform(-0.2, 0.2)
            if old and ti < rnd.randint(1, 3) and math.cos(az - dead_side) > 0.3:
                continue                                  # dead or missing lowest tiers on one side
            L = r * rnd.uniform(0.85, 1.05)
            inner = (math.cos(az) * L * 0.5, y, math.sin(az) * L * 0.5)
            tip = (math.cos(az) * L, y - drop, math.sin(az) * L)
            strand(leaves, (0, y, 0), inner); strand(leaves, inner, tip)
            ellipsoid(leaves, tip, 0.9, 0.7, 0.9, rnd=rnd, rough=0.3)
            ellipsoid(leaves, inner, 0.9, 0.6, 0.9, rnd=rnd, rough=0.3)
        ellipsoid(leaves, (0, y, 0), min(r, 1.8), 0.7, min(r, 1.8), rnd=rnd, rough=0.2)
    if forest:                                           # dead stubs below the crown
        for y in range(2, base, 2):
            az = rnd.uniform(0, 2 * math.pi)
            leaves.add((int(round(math.cos(az))), y, int(round(math.sin(az)))))
    for y in range(top + 1, H + 1):                      # the leader: a thin spire of leaves
        leaves.add((0, y, 0))
    if old:                                              # blunter top
        ellipsoid(leaves, (0, H - 1, 0), 1.5, 1.5, 1.5, rnd=rnd, rough=0.2)
    trunk, core, _gone = sink_tip(trunk, leaves, TRUNK_TIP_DEPTH["spruce"][age])  # v4: the leader is leaves
    leaves |= set(core)
    info = {"H": H, "crown_base": base, "radius": round(R0, 1), "tiers": len(tiers), "forest": forest, "double": double,
            "trunk_top": max(c[1] for c in trunk)}
    return trunk, finish(trunk, leaves), info


def jungle(age, idx):
    """§5.6: young = cacao-like (4-7, jorquette of 3-5 branches at ~2 blocks fanning to radius 2-3) or pole emergent
    (12-20, small tiers in the top half); mature = emergent 26-34 (capped for a 1-wide trunk), clear bole 0.55-0.72 H,
    4-6 limbs rising 3-6 and reaching 6-10, clumps radius 3-4, crown radius 9-13 (capped 11), dome or umbrella;
    old = taller 30-38, wider, 1-2 broken dead limbs. Buttresses/vines belong to the square elder (not here)."""
    rnd = random.Random(zlib.crc32(f"jungle/{age}/{idx}".encode()))
    leaves, trunk = set(), []
    if age == "young":
        if idx % 2 == 0:                                 # cacao-like
            H = rnd.randint(4, 7); j = 2
            trunk = [(0, y, 0) for y in range(0, j + 1)]
            for i in range(rnd.randint(3, 5)):
                az = rnd.uniform(0, 2 * math.pi); L = rnd.uniform(2.0, 3.0)
                tip = (math.cos(az) * L, j + L * 0.7, math.sin(az) * L)
                strand(leaves, (0, j, 0), tip)
                ellipsoid(leaves, tip, 1.4, 1.0, 1.4, rnd=rnd, rough=0.25)
            if rnd.random() < 0.5:                       # chupon: a second small fan
                trunk += [(0, y, 0) for y in range(j + 1, j + 3)]
                ellipsoid(leaves, (0, j + 3.5, 0), 1.8, 1.2, 1.8, rnd=rnd, rough=0.25)
            info = {"H": H, "crown_base": j, "radius": 2.5, "form": "cacao"}
        else:                                            # pole emergent
            H = rnd.randint(12, 20); R = rnd.uniform(2.0, 3.0)
            trunk = [(0, y, 0) for y in range(0, H - 1)]
            for k in range(rnd.randint(3, 5)):
                y = int(H * (0.55 + 0.4 * k / 4)) + rnd.randint(-1, 1)
                for i in range(rnd.randint(2, 4)):
                    az = rnd.uniform(0, 2 * math.pi); L = R * rnd.uniform(0.6, 1.0)
                    tip = (math.cos(az) * L, y + 0.3, math.sin(az) * L)
                    strand(leaves, (0, y, 0), tip); ellipsoid(leaves, tip, 1.2, 0.8, 1.2, rnd=rnd, rough=0.3)
            ellipsoid(leaves, (0, H - 1, 0), 1.6, 1.4, 1.6, rnd=rnd, rough=0.2)
            info = {"H": H, "crown_base": int(H * 0.55), "radius": round(R, 1), "form": "pole"}
    else:
        old = age == "old"
        H = rnd.randint(30, 38) if old else rnd.randint(26, 34)
        bole = int(H * rnd.uniform(0.55, 0.72))
        R = min(13.0 if old else 11.0, rnd.uniform(10.0, 14.0) if old else rnd.uniform(9.0, 12.0))
        trunk = [(0, y, 0) for y in range(0, bole + rnd.randint(2, 4))]
        n = rnd.randint(4, 6)
        umbrella = idx % 3 == 0
        heavy = rnd.uniform(0, 2 * math.pi)
        dead = set(rnd.sample(range(n), rnd.randint(1, 2))) if old else set()
        for i in range(n):
            az = heavy + 2 * math.pi * i / n + rnd.uniform(-0.3, 0.3)
            rise = rnd.uniform(3, 6); reach = rnd.uniform(6, 10) * min(1.0, R / 11)
            base = (0, bole + rnd.uniform(0, 2), 0)
            tip = (math.cos(az) * reach, base[1] + rise, math.sin(az) * reach)
            mid = (tip[0] * 0.5, base[1] + rise * 0.7, tip[2] * 0.5)
            strand(leaves, base, mid); strand(leaves, mid, tip)
            strand(leaves, (0, base[1] + 1, 0), (mid[0], mid[1] + 1, mid[2]))
            if i in dead:
                continue                                  # broken limb: the strand stays, no clump
            rc = rnd.uniform(3.0, 4.0)
            ellipsoid(leaves, tip, rc, rc * (0.45 if umbrella else 0.7), rc, shell=2.0, rnd=rnd)
        dome = R * 0.6
        ellipsoid(leaves, (0, bole + 4.5, 0), dome, dome * (0.35 if umbrella else 0.5), dome, shell=2.0, rnd=rnd)
        info = {"H": H, "crown_base": bole, "radius": round(R, 1), "limbs": n, "umbrella": umbrella, "dead": len(dead)}
    trunk, core, _gone = sink_tip(trunk, leaves, TRUNK_TIP_DEPTH["jungle"][age])  # v4: the tip under the apex
    leaves |= set(core)
    info["trunk_top"] = max(c[1] for c in trunk)
    return trunk, finish(trunk, leaves), info


SPECIES = {"oak": oak, "birch": birch, "spruce": spruce, "jungle": jungle}


def build(species, age, idx):
    trunk, leaves, info = SPECIES[species](age, idx)
    xs = [c[0] for c in trunk] + [c[0] for c in leaves]
    zs = [c[2] for c in trunk] + [c[2] for c in leaves]
    ys = [c[1] for c in trunk] + [c[1] for c in leaves]
    x0, z0 = min(xs), min(zs)
    size = (max(xs) - x0 + 1, max(ys) + 1, max(zs) - z0 + 1)
    st = M.Structure(size)
    log_id = LOG[species][age]
    trunk_local = {(x - x0, y, z - z0) for x, y, z in trunk}
    root = (-x0, 0, -z0)
    for x, y, z in trunk_local:
        if (x, y, z) == root:     # T2 root block: same look, carries the template index + rotation (north = as saved)
            st.set(x, y, z, f"{log_id}_root", {"pw:tpl": M.i(idx % 16), "pw:tpl_hi": M.i(idx // 16), "minecraft:cardinal_direction": M.s("north")})
            continue
        st.set(x, y, z, log_id, {"pw:variant": M.i(cell_hash(x, y, z) % 5), "pw:rseed": M.b(1),
                                 "pw:top_variant": M.i((cell_hash(x, y, z) >> 5) % 7)})
    for x, y, z in leaves:
        lx, lz = x - x0, z - z0
        d = min((abs(lx - a) + abs(y - b) + abs(lz - c) for a, b, c in trunk_local), default=99)
        st.set(lx, y, lz, LEAF[species], {"pw:variant": M.i(leaf_look(lx, y, lz, d)), "pw:off": M.i((lx + 2 * y + 4 * lz) % 7),
                                          "pw:rseed": M.b(1), "pw:section": M.i(0), "pw:exposure": M.i(0),
                                          "pw:section_rolled": M.b(1)})
    info.update({"size": size, "root_local": root, "logs": len(trunk_local), "leaves": len(leaves)})
    return st, info, trunk_local, leaves, (x0, z0)


def render_sheet(species, rows, out_png):
    """Isometric voxel thumbnails, 8 per row (2 rows per age), seen from the south-east; a 2-block player stands 9
    blocks to the right of each trunk for scale."""
    from PIL import Image, ImageDraw, ImageFont
    S = 8
    cw, ch = 340, 330
    flat = [(age, i, t) for age, trees in rows for i, t in enumerate(trees)]
    nrows = (len(flat) + 7) // 8
    img = Image.new("RGB", (8 * cw + 40, nrows * (ch + 26) + 50), (188, 210, 230))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((14, 10), f"TREES - {species}: young / mature / old x {PER_AGE}, seen from the south-east, 1 block = {S} px; the dark "
           "figure is a player (2 blocks) standing 9 blocks to the right.", fill=(20, 20, 20), font=font)
    for k, (age, i, (trunk, leaves, info)) in enumerate(flat):
        r, col = divmod(k, 8)
        ox = 20 + col * cw + cw // 2 - 40
        base_y = 40 + r * (ch + 26) + ch - 10

        def P(x, y, z):
            return (ox + (x - z) * S * 0.866, base_y - y * S - (x + z) * S * 0.5)

        def cube(x, y, z, top, left, right):
            a, b, c_, e = P(x, y + 1, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)
            d.polygon([a, b, c_, e], fill=top)
            d.polygon([e, c_, P(x + 1, y, z + 1), P(x, y, z + 1)], fill=left)
            d.polygon([b, c_, P(x + 1, y, z + 1), P(x + 1, y, z)], fill=right)
        for py in (0, 1):
            cube(9, py, -9, (40, 40, 52), (28, 28, 36), (20, 20, 28))
        vox = [(c, "log") for c in trunk] + [(c, "leaf") for c in leaves]
        vox.sort(key=lambda v: (v[0][0] + v[0][2], v[0][1]))
        for (x, y, z), kind in vox:
            if kind == "log":
                cube(x, y, z, (140, 100, 62), (104, 72, 44), (86, 58, 36))
            else:
                g = 120 + (cell_hash(x, y, z) % 30)
                cube(x, y, z, (70, g, 52), (52, g - 28, 40), (40, g - 42, 32))
        d.text((ox - cw // 2 + 46, base_y + 6), f"{age} {i:02d}  H{info['H']}  radius {info['radius']}", fill=(20, 20, 20),
               font=font)
    img.save(out_png)
    return img.size


def main():
    species = sys.argv[1] if len(sys.argv) > 1 else "oak"
    rows, report = [], []
    for age in ("young", "mature", "old"):
        trees = []
        for idx in range(PER_AGE):
            st, info, trunk, leaves, _ = build(species, age, idx)
            p = OUT / species / f"{species}_{age}_{idx:02d}.mcstructure"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(st.to_bytes())
            trees.append(({(x + _[0], y, z + _[1]) for x, y, z in trunk}, leaves, info))   # both in tree coords (root at 0,0)
            report.append({"id": f"{species}_{age}_{idx:02d}", **{k: (list(v) if isinstance(v, tuple) else v) for k, v in info.items()}})
        rows.append((age, trees))
    (OUT / species / "REPORT.json").write_text(json.dumps(report, indent=1))
    size = render_sheet(species, rows, f"/mnt/user-data/outputs/TREE-PILOT-{species}.png")
    print("templates", len(report), "sheet", size)
    for r in report[::8]:
        print(r)


if __name__ == "__main__":
    main()
