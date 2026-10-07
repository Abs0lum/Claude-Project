#!/usr/bin/env python3
"""java_trees.py — J1 (D-C339, his GO 16:24 CT 09-30): the Java 26.3 tree rules, ported to our own Python.

Source of the RULES (read, not shipped): the unobfuscated Java 26.3 server jar, decompiled to
_intake/java-26.3-trees/decompiled (TreeFeature, 12 trunk placers, 14 foliage placers, the mangrove root placer) and the
vanilla feature JSON of 26.4-snapshot-2 (_intake/java-26.3-trees/features). This file is our own code: the same steps and
numbers, written in Python, so we can render, compare and later write .mcstructure trees with OUR blocks.

Java details kept on purpose (they change shapes):
  * Java int division truncates toward zero (jdiv), not Python's floor division.
  * (int) casts truncate; Mth.floor floors.
  * logs are placed first; a leaf only goes where the cell is air or leaves (TreeFeature.validTreePos),
    so leaves never replace wood; the ground (y < 0) is solid and refuses both.
  * the random calls follow Java's order inside each placer (the numbers differ from Java: Python's random, not Xoroshiro),
    so each seed is a valid Java-rule tree, not the same tree Java would grow for that seed.

World model: dict (x, y, z) -> ("log", axis) | ("leaf", leaf_id) | ("root", id). Origin (0, 0, 0) = the block the sapling
stands in; the ground fills y < 0.
"""
import json, math, random
from pathlib import Path

FEATURES = Path("/home/claude/_intake/java-26.3-trees/features")
HORIZONTAL = [(0, 0, -1), (0, 0, 1), (-1, 0, 0), (1, 0, 0)]      # north, south, west, east (Java Plane.HORIZONTAL order)
AXIS_OF = {(0, 0, -1): "z", (0, 0, 1): "z", (-1, 0, 0): "x", (1, 0, 0): "x", (0, 1, 0): "y", (0, -1, 0): "y"}


def jdiv(a, b):
    """Java integer division (truncates toward zero)."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


class Rng:
    """The RandomSource calls the placers make (nextInt / nextFloat / nextBoolean), on Python's Mersenne Twister."""
    def __init__(self, seed): self.r = random.Random(seed)
    def next_int(self, n): return self.r.randrange(n) if n > 0 else 0
    def next_float(self): return self.r.random()
    def next_bool(self): return self.r.random() < 0.5
    def direction(self): return HORIZONTAL[self.r.randrange(4)]
    def shuffled_horizontal(self):
        d = list(HORIZONTAL); self.r.shuffle(d); return d


def sample(p, rng):
    """IntProvider.sample: constant int, uniform, weighted_list (the kinds the tree features use)."""
    if isinstance(p, int): return p
    t = p.get("type", "minecraft:uniform")
    if t in ("minecraft:uniform", "uniform") or ("min_inclusive" in p and "type" not in p):
        return p["min_inclusive"] + rng.next_int(p["max_inclusive"] - p["min_inclusive"] + 1)
    if t == "minecraft:constant": return p["value"]
    if t == "minecraft:weighted_list":
        dist = p["distribution"]; tot = sum(e["weight"] for e in dist); k = rng.next_int(tot)
        for e in dist:
            k -= e["weight"]
            if k < 0: return sample(e["data"], rng)
    raise ValueError(f"IntProvider {t} not ported")


class World:
    def __init__(self): self.b = {}
    def get(self, p): return self.b.get(p)
    def valid_tree_pos(self, p):                       # TreeFeature.validTreePos: air or replaceable_by_trees (leaves)
        if p[1] < 0: return False
        c = self.b.get(p); return c is None or c[0] == "leaf"
    def is_free(self, p):                              # TrunkPlacer.isFree: valid or already a log
        c = self.b.get(p); return self.valid_tree_pos(p) or (c is not None and c[0] == "log")
    def air_or_leaves(self, p): return self.valid_tree_pos(p)


def add(p, d, k=1): return (p[0] + d[0] * k, p[1] + d[1] * k, p[2] + d[2] * k)


class Attach:
    """FoliagePlacer.FoliageAttachment(pos, radiusOffsetXZ, foliageHeightOffset, sizeX, sizeZ)."""
    def __init__(self, pos, radius_offset=0, double=False, height_offset=0):
        self.pos = pos; self.radius_offset = radius_offset; self.height_offset = height_offset; self.double = double


# ------------------------------------------------------------------------------------------------ trunk placers
class Trunk:
    def __init__(self, cfg, world, rng, can_grow_through=()):
        self.c = cfg; self.w = world; self.rng = rng; self.grow_through = can_grow_through
    def tree_height(self):
        c = self.c; return c["base_height"] + self.rng.next_int(c["height_rand_a"] + 1) + self.rng.next_int(c["height_rand_b"] + 1)
    def valid(self, p):
        c = self.w.get(p); return self.w.valid_tree_pos(p) or (c is not None and c[0] in self.grow_through)
    def place_log(self, p, axis="y"):
        if self.valid(p): self.w.b[p] = ("log", axis); return True
        return False
    def place_log_if_free(self, p):
        if self.w.is_free(p): self.place_log(p)

    def place(self, h, o):
        return getattr(self, "t_" + self.c["type"].split(":")[1])(h, o)

    def t_straight_trunk_placer(self, h, o):
        for y in range(h): self.place_log(add(o, (0, 1, 0), y))
        return [Attach(add(o, (0, 1, 0), h), 0, False)]

    def t_forking_trunk_placer(self, h, o):
        rng = self.rng; att = []
        lean = rng.direction(); lean_h = h - rng.next_int(4) - 1; lean_steps = 3 - rng.next_int(3)
        tx, tz = o[0], o[2]; ey = None
        for yo in range(h):
            yy = o[1] + yo
            if yo >= lean_h and lean_steps > 0: tx += lean[0]; tz += lean[2]; lean_steps -= 1
            if self.place_log((tx, yy, tz)): ey = yy + 1
        if ey is not None: att.append(Attach((tx, ey, tz), 1, False))
        tx, tz = o[0], o[2]
        br = rng.direction()
        if br != lean:
            bpos = lean_h - rng.next_int(2) - 1; steps = 1 + rng.next_int(3); ey = None; yo = bpos
            while yo < h and steps > 0:
                if yo >= 1:
                    yy = o[1] + yo; tx += br[0]; tz += br[2]
                    if self.place_log((tx, yy, tz)): ey = yy + 1
                yo += 1; steps -= 1
            if ey is not None: att.append(Attach((tx, ey, tz), 0, False))
        return att

    def t_bending_trunk_placer(self, h, o):
        rng = self.rng; d = rng.direction(); log_h = h - 1; p = o; pts = []
        for i in range(log_h + 1):
            if i + 1 >= log_h + rng.next_int(2): p = add(p, d)
            if self.w.valid_tree_pos(p): self.place_log(p)
            if i >= self.c["min_height_for_leaves"]: pts.append(Attach(p, 0, False))
            p = add(p, (0, 1, 0))
        n = sample(self.c["bend_length"], rng)
        for i in range(n + 1):
            if self.w.valid_tree_pos(p): self.place_log(p)
            pts.append(Attach(p, 0, False)); p = add(p, d)
        return pts

    def t_dark_oak_trunk_placer(self, h, o):
        rng = self.rng; att = []
        lean = rng.direction(); lean_h = h - rng.next_int(4); lean_steps = 2 - rng.next_int(3)
        x, y, z = o; tx, tz = x, z; ey = y + h - 1
        for dy in range(h):
            if dy >= lean_h and lean_steps > 0: tx += lean[0]; tz += lean[2]; lean_steps -= 1
            bp = (tx, y + dy, tz)
            if self.w.air_or_leaves(bp):
                for off in ((0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1)): self.place_log(add(bp, off))
        att.append(Attach((tx, ey, tz), 0, True))
        for ox in range(-1, 3):
            for oz in range(-1, 3):
                if (ox < 0 or ox > 1 or oz < 0 or oz > 1) and rng.next_int(3) <= 0:
                    ln = rng.next_int(3) + 2
                    for by in range(ln): self.place_log((x + ox, ey - by - 1, z + oz))
                    att.append(Attach((x + ox, ey, z + oz), 0, False))
        return att

    def t_fancy_trunk_placer(self, tree_h, o):
        rng = self.rng; height = tree_h + 2; trunk_h = math.floor(height * 0.618)
        clusters = min(1, math.floor(1.382 + (1.0 * height / 13.0) ** 2))
        trunk_top = o[1] + trunk_h; rel = height - 5
        coords = [(add(o, (0, 1, 0), rel), trunk_top)]
        while rel >= 0:
            shape = fancy_shape(height, rel)
            if not shape < 0.0:
                for _ in range(clusters):
                    radius = 1.0 * shape * (rng.next_float() + 0.328); ang = rng.next_float() * 2.0 * math.pi
                    x = radius * math.sin(ang) + 0.5; z = radius * math.cos(ang) + 0.5
                    cs = (o[0] + math.floor(x), o[1] + rel - 1, o[2] + math.floor(z)); ce = add(cs, (0, 1, 0), 5)
                    if self.limb(cs, ce, False):
                        dx = o[0] - cs[0]; dz = o[2] - cs[2]
                        bh = cs[1] - math.sqrt(dx * dx + dz * dz) * 0.381
                        btop = trunk_top if bh > trunk_top else int(bh)
                        base = (o[0], btop, o[2])
                        if self.limb(base, cs, False): coords.append((cs, base[1]))
            rel -= 1
        self.limb(o, add(o, (0, 1, 0), trunk_h), True)
        for tip, bb in coords:                                                 # makeBranches
            base = (o[0], bb, o[2])
            if base != tip and (bb - o[1]) >= height * 0.2: self.limb(base, tip, True)
        return [Attach(tip, 0, False) for tip, bb in coords if (bb - o[1]) >= height * 0.2]

    def limb(self, a, b, do_place):
        if not do_place and a == b: return True
        d = (b[0] - a[0], b[1] - a[1], b[2] - a[2]); steps = max(abs(d[0]), abs(d[1]), abs(d[2]))
        if steps == 0:
            if do_place: self.place_log(a, "y")
            return True
        fx, fy, fz = d[0] / steps, d[1] / steps, d[2] / steps
        for i in range(steps + 1):
            p = (a[0] + math.floor(0.5 + i * fx), a[1] + math.floor(0.5 + i * fy), a[2] + math.floor(0.5 + i * fz))
            if do_place:
                xd, zd = abs(p[0] - a[0]), abs(p[2] - a[2]); m = max(xd, zd)
                self.place_log(p, "y" if m == 0 else ("x" if xd == m else "z"))
            elif not self.w.is_free(p): return False
        return True

    def t_cherry_trunk_placer(self, h, o):
        rng = self.rng; c = self.c
        so = c["branch_start_offset_from_top"]; so2 = {"min_inclusive": so["min_inclusive"], "max_inclusive": so["max_inclusive"] - 1}
        first = max(0, h - 1 + sample(so, rng)); second = max(0, h - 1 + sample(so2, rng))
        if second >= first: second += 1
        n = sample(c["branch_count"], rng); middle = n == 3; both = n >= 2
        trunk_h = h if middle else (max(first, second) + 1 if both else first + 1)
        for y in range(trunk_h): self.place_log(add(o, (0, 1, 0), y))
        att = [Attach(add(o, (0, 1, 0), trunk_h), 0, False)] if middle else []
        d = rng.direction(); side = AXIS_OF[d]
        att.append(self.cherry_branch(h, o, side, d, first, first < trunk_h - 1))
        if both: att.append(self.cherry_branch(h, o, side, (-d[0], 0, -d[2]), second, second < trunk_h - 1))
        return att

    def cherry_branch(self, h, o, side_axis, d, off, middle_up):
        rng = self.rng; c = self.c; p = add(o, (0, 1, 0), off)
        end_off = h - 1 + sample(c["branch_end_offset_from_top"], rng)
        away = middle_up or end_off < off
        dist = sample(c["branch_horizontal_length"], rng) + (1 if away else 0)
        end = (o[0] + d[0] * dist, o[1] + end_off, o[2] + d[2] * dist)
        for _ in range(2 if away else 1): p = add(p, d); self.place_log(p, side_axis)
        vd = (0, 1, 0) if end[1] > p[1] else (0, -1, 0)
        while True:
            dist_m = abs(p[0] - end[0]) + abs(p[1] - end[1]) + abs(p[2] - end[2])
            if dist_m == 0: return Attach(add(end, (0, 1, 0)), 0, False)
            vert = rng.next_float() < abs(end[1] - p[1]) / dist_m
            p = add(p, vd if vert else d); self.place_log(p, "y" if vert else side_axis)

    def t_upwards_branching_trunk_placer(self, h, o):
        rng = self.rng; c = self.c; att = []
        for hp in range(h):
            cy = o[1] + hp; lp = (o[0], cy, o[2])
            if self.place_log(lp) and hp < h - 1 and rng.next_float() < c["place_branch_per_log_probability"]:
                d = rng.direction(); bl = sample(c["extra_branch_length"], rng)
                bpos = max(0, bl - sample(c["extra_branch_length"], rng) - 1); steps = sample(c["extra_branch_steps"], rng)
                self.upward_branch(h, att, lp, cy, d, bpos, steps)
            if hp == h - 1: att.append(Attach((o[0], cy + 1, o[2]), 0, False))
        return att

    def upward_branch(self, h, att, lp, cy, d, bpos, steps):
        along = cy + bpos; lx, lz = lp[0], lp[2]; i = bpos
        while i < h and steps > 0:
            if i >= 1:
                ph = cy + i; lx += d[0]; lz += d[2]; along = ph
                if self.place_log((lx, ph, lz)): along = ph + 1
                att.append(Attach((lx, ph, lz), 0, False))
            i += 1; steps -= 1
        if along - cy > 1:
            fp = (lx, along, lz); att.append(Attach(fp, 0, False)); att.append(Attach(add(fp, (0, -1, 0), 2), 0, False))

    def t_giant_trunk_placer(self, h, o):
        for hh in range(h):
            self.place_log_if_free(add(o, (0, hh, 0)))
            if hh < h - 1:
                for off in ((1, hh, 0), (1, hh, 1), (0, hh, 1)): self.place_log_if_free(add(o, off))
        return [Attach(add(o, (0, 1, 0), h), 0, True)]

    def t_mega_jungle_trunk_placer(self, h, o):
        rng = self.rng; att = list(self.t_giant_trunk_placer(h, o))
        bh = h - 2 - rng.next_int(4)
        while bh > jdiv(h, 2):
            ang = rng.next_float() * math.pi * 2; bx = bz = 0
            for b in range(5):
                bx = int(1.5 + math.cos(ang) * b); bz = int(1.5 + math.sin(ang) * b)
                self.place_log(add(o, (bx, bh - 3 + jdiv(b, 2), bz)))
            att.append(Attach(add(o, (bx, bh, bz)), -2, False))
            bh -= 2 + rng.next_int(4)
        return att

    def t_poplar_trunk_placer(self, h, o):
        rng = self.rng; up_to = h - sample(self.c["trunk_height_above_branches"], rng)
        for y in range(h):
            self.place_log(add(o, (0, 1, 0), y)); dirs = rng.shuffled_horizontal()
            if up_to - 1 == y:
                for k in range(sample(self.c["branch_amount"], rng)):
                    d = dirs[k]; self.place_log(add(add(o, (0, 1, 0), y), d), AXIS_OF[d])
        return [Attach(add(o, (0, 1, 0), up_to), 0, False)]


def fancy_shape(height, y):
    if y < height * 0.3: return -1.0
    radius = height / 2.0; adjacent = radius - y
    distance = math.sqrt(max(0.0, radius * radius - adjacent * adjacent))
    if adjacent == 0.0: distance = radius
    elif abs(adjacent) >= radius: return 0.0
    return distance * 0.5


# ------------------------------------------------------------------------------------------------ foliage placers
class Foliage:
    def __init__(self, cfg, world, rng, leaf):
        self.c = cfg; self.w = world; self.rng = rng; self.leaf = leaf; self.t = cfg["type"].split(":")[1]
    # ---- sizes
    def foliage_height(self, tree_h):
        c = self.c; t = self.t
        if t in ("blob_foliage_placer", "fancy_foliage_placer", "bush_foliage_placer", "jungle_foliage_placer"): return c["height"]
        if t == "acacia_foliage_placer": return 0
        if t == "dark_oak_foliage_placer": return 4
        if t == "spruce_foliage_placer": return max(4, tree_h - sample(c["trunk_height"], self.rng))
        if t == "pine_foliage_placer": return sample(c["height"], self.rng)
        if t == "mega_pine_foliage_placer": return sample(c["crown_height"], self.rng)
        if t in ("cherry_foliage_placer", "poplar_foliage_placer"): return sample(c["height"], self.rng)
        if t == "random_spread_foliage_placer": return sample(c["foliage_height"], self.rng)
        raise ValueError(t)
    def foliage_radius(self, trunk_h):
        r = sample(self.c["radius"], self.rng)
        if self.t == "pine_foliage_placer": r += self.rng.next_int(max(trunk_h + 1, 1))
        return r
    # ---- the shared row + leaf rules
    def try_leaf(self, p):
        if self.w.valid_tree_pos(p):
            leaf = self.leaf(self.rng) if callable(self.leaf) else self.leaf
            self.w.b[p] = ("leaf", leaf); return True
        return False
    def skip_signed(self, dx, y, dz, r, dbl):
        if self.t == "dark_oak_foliage_placer" and y == 0 and dbl and (dx == -r or dx >= r) and (dz == -r or dz >= r): return True
        if dbl: mdx, mdz = min(abs(dx), abs(dx - 1)), min(abs(dz), abs(dz - 1))
        else: mdx, mdz = abs(dx), abs(dz)
        return self.skip(mdx, y, mdz, r, dbl)
    def skip(self, dx, y, dz, r, dbl):
        t = self.t; rng = self.rng; c = self.c
        if t in ("blob_foliage_placer",): return dx == r and dz == r and (rng.next_int(2) == 0 or y == 0)
        if t == "fancy_foliage_placer": return (dx + 0.5) ** 2 + (dz + 0.5) ** 2 > r * r
        if t == "bush_foliage_placer": return dx == r and dz == r and rng.next_int(2) == 0
        if t == "acacia_foliage_placer": return ((dx > 1 or dz > 1) and dx != 0 and dz != 0) if y == 0 else (dx == r and dz == r and r > 0)
        if t in ("spruce_foliage_placer", "pine_foliage_placer"): return dx == r and dz == r and r > 0
        if t in ("mega_pine_foliage_placer", "jungle_foliage_placer"): return True if dx + dz >= 7 else dx * dx + dz * dz > r * r
        if t == "dark_oak_foliage_placer":
            if y == -1 and not dbl: return dx == r and dz == r
            return dx + dz > r * 2 - 2 if y == 1 else False
        if t == "cherry_foliage_placer":
            if y == -1 and (dx == r or dz == r) and rng.next_float() < c["wide_bottom_layer_hole_chance"]: return True
            corner = dx == r and dz == r
            return (corner or dx + dz > r * 2 - 2 and rng.next_float() < c["corner_hole_chance"]) if r > 2 else (corner and rng.next_float() < c["corner_hole_chance"])
        raise ValueError(t)
    def row(self, origin, r, y, dbl):
        off = 1 if dbl else 0
        for dx in range(-r, r + off + 1):
            for dz in range(-r, r + off + 1):
                if not self.skip_signed(dx, y, dz, r, dbl): self.try_leaf((origin[0] + dx, origin[1] + y, origin[2] + dz))
    def row_hanging(self, origin, r, y, dbl, chance, ext):
        self.row(origin, r, y, dbl); off = 1 if dbl else 0; log_pos = add(origin, (0, -1, 0))
        # Plane.HORIZONTAL = N, E, S, W for this loop (alongEdge), toEdge = clockwise
        for along in ((0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0)):
            to = {(0, 0, -1): (1, 0, 0), (1, 0, 0): (0, 0, 1), (0, 0, 1): (-1, 0, 0), (-1, 0, 0): (0, 0, -1)}[along]
            k = r + off if (to[0] + to[2]) > 0 else r
            p = add(add(add(origin, (0, y - 1, 0)), to, k), along, -r)
            for _ in range(-r, r + off):
                if self.w.get(add(p, (0, 1, 0))) is not None and self.w.get(add(p, (0, 1, 0)))[0] == "leaf":
                    if self.try_ext(chance, log_pos, p): self.try_ext(ext, log_pos, add(p, (0, -1, 0)))
                p = add(p, along)
    def try_ext(self, chance, log_pos, p):
        if abs(p[0] - log_pos[0]) + abs(p[1] - log_pos[1]) + abs(p[2] - log_pos[2]) >= 7: return False
        return False if self.rng.next_float() > chance else self.try_leaf(p)

    # ---- createFoliage (offset sampled once per attachment, as FoliagePlacer.createFoliage does)
    def create(self, tree_h, a, fh, lr):
        off = sample(self.c.get("offset", 0), self.rng); t = self.t; dbl = a.double; P = a.pos
        if t == "blob_foliage_placer":
            fho = fh + a.height_offset
            for yo in range(off, off - fho - 1, -1): self.row(P, max(lr + a.radius_offset - 1 - jdiv(yo, 2), 0), yo, dbl)
        elif t == "fancy_foliage_placer":
            for yo in range(off, off - fh - 1, -1): self.row(P, lr + (1 if yo != off and yo != off - fh else 0), yo, dbl)
        elif t == "bush_foliage_placer":
            fho = fh + a.height_offset
            for yo in range(off, off - fho - 1, -1): self.row(P, lr + a.radius_offset - 1 - yo, yo, dbl)
        elif t == "acacia_foliage_placer":
            fp = add(P, (0, 1, 0), off); fho = fh + a.height_offset
            self.row(fp, lr + a.radius_offset, -1 - fho, dbl); self.row(fp, lr - 1, -fho, dbl); self.row(fp, lr + a.radius_offset - 1, 0, dbl)
        elif t == "spruce_foliage_placer":
            cur = self.rng.next_int(2); mx = 1; mn = 0; fho = fh + a.height_offset
            for yo in range(off, -fho - 1, -1):
                self.row(P, cur, yo, dbl)
                if cur >= mx: cur = mn; mn = 1; mx = min(mx + 1, lr + a.radius_offset)
                else: cur += 1
        elif t == "pine_foliage_placer":
            cur = 0; fho = fh + a.height_offset
            for yo in range(off, off - fho - 1, -1):
                self.row(P, cur, yo, dbl)
                if cur >= 1 and yo == off - fho + 1: cur -= 1
                elif cur < lr + a.radius_offset: cur += 1
        elif t == "mega_pine_foliage_placer":
            prev = 0; fho = fh + a.height_offset
            for yy in range(P[1] - fho + off, P[1] + off + 1):
                yo = P[1] - yy; smooth = lr + a.radius_offset + math.floor(yo / fho * 3.5)
                jag = smooth + 1 if (yo > 0 and smooth == prev and (yy & 1) == 0) else smooth
                self.row((P[0], yy, P[2]), jag, 0, dbl); prev = smooth
        elif t == "jungle_foliage_placer":
            lh = (fh if dbl else 1 + self.rng.next_int(2)) + a.height_offset
            for yo in range(off, off - lh - 1, -1): self.row(P, lr + a.radius_offset + 1 - yo, yo, dbl)
        elif t == "dark_oak_foliage_placer":
            p = add(P, (0, 1, 0), off)
            if dbl:
                self.row(p, lr + 2, -1, dbl); self.row(p, lr + 3, 0, dbl); self.row(p, lr + 2, 1, dbl)
                if self.rng.next_bool(): self.row(p, lr, 2, dbl)
            else:
                self.row(p, lr + 2, -1, dbl); self.row(p, lr + 1, 0, dbl)
        elif t == "cherry_foliage_placer":
            fp = add(P, (0, 1, 0), off); cr = lr + a.radius_offset - 1; fho = fh + a.height_offset; c = self.c
            self.row(fp, cr - 2, fho - 3, dbl); self.row(fp, cr - 1, fho - 4, dbl)
            for y in range(fho - 5, -1, -1): self.row(fp, cr, y, dbl)
            self.row_hanging(fp, cr, -1, dbl, c["hanging_leaves_chance"], c["hanging_leaves_extension_chance"])
            self.row_hanging(fp, cr - 1, -2, dbl, c["hanging_leaves_chance"], c["hanging_leaves_extension_chance"])
        elif t == "random_spread_foliage_placer":
            for _ in range(self.c["leaf_placement_attempts"]):
                r = self.rng
                p = (P[0] + r.next_int(lr) - r.next_int(lr), P[1] + r.next_int(fh) - r.next_int(fh), P[2] + r.next_int(lr) - r.next_int(lr))
                self.try_leaf(p)
        elif t == "poplar_foliage_placer":
            self.poplar(P, a, fh, lr, off, dbl)
        else:
            raise ValueError(t)

    # ---- poplar (26.4 snapshot): rhombus layers + log spokes inside the crown
    def poplar(self, P, a, fh, lr, off, dbl):
        fp = add(P, (0, 1, 0), off); cr = lr + a.radius_offset - 1; flip = self.rng.next_bool(); fho = fh + a.height_offset
        self.prow(fp, cr - 2, fho - 1, dbl, fho, flip); self.prow(fp, cr - 1, fho - 2, dbl, fho, flip); self.prow(fp, cr - 1, fho - 3, dbl, fho, flip)
        for y in range(fho - 4, 0, -1): self.prow(fp, cr, y, dbl, fho, flip)
        self.poplar_logs(fp, cr, fho - 4, dbl, fho, flip)
        self.prow(fp, cr - 1, 0, dbl, fho, flip); self.prow(fp, max(1, min(2, cr - 2)), -1, dbl, fho, flip)
    @staticmethod
    def _partial(fh, y): return fh - 1 == y or fh - 2 == y
    @staticmethod
    def _corner_cut(dx, dz, r, partial, flip):
        small = (dx > 0 and dz > 0 or dz < 0 and dx < 0) if flip else (dx > 0 and dz < 0 or dz > 0 and dx < 0)
        return r - 1 if small else (r + 1 if partial else r)
    @staticmethod
    def _in_rhombus(r, adx, adz, cut, extra): return adx + adz <= r * 2 - (cut + extra)
    def prow(self, origin, r, y, dbl, fh, flip):
        off = 1 if dbl else 0
        for dx in range(-r, r + off + 1):
            for dz in range(-r, r + off + 1):
                partial = self._partial(fh, y); cut = self._corner_cut(dx, dz, r, partial, flip)
                adx, adz = abs(dx), abs(dz)
                if partial and (adx == r or adz == r): continue
                extra = 1 if self.rng.next_float() <= self.c["side_hole_chance"] else 0
                if self._in_rhombus(r, adx, adz, cut, extra): self.try_leaf((origin[0] + dx, origin[1] + y, origin[2] + dz))
    def poplar_logs(self, origin, r, y, dbl, fh, flip):
        off = 1 if dbl else 0
        for dx in range(-r, r + off + 1):
            for dz in range(-r, r + off + 1):
                adx, adz = abs(dx), abs(dz)
                if self._in_rhombus(r, adx, adz, self._corner_cut(dx, dz, r, self._partial(fh, y), flip), 2) and (adz == 0 and r - adx >= 4 or adx == 0 and r - adz >= 4):
                    p = (origin[0] + dx, origin[1] + y, origin[2] + dz); c = self.w.get(p)
                    if c is not None and c[0] == "leaf": self.w.b[p] = ("log", "x" if adz == 0 else "z")


# ------------------------------------------------------------------------------------------------ mangrove roots
def mangrove_roots(cfg, w, rng, origin, trunk_origin):
    mp = cfg["mangrove_root_placement"]; max_len = mp["max_root_length"]; max_w = mp["max_root_width"]; skew = mp["random_skew_chance"]
    def can(p): c = w.get(p); return p[1] >= 0 and (c is None or c[0] == "leaf" or c[0] == "root")
    def potential(p, d):
        below = add(p, (0, -1, 0)); nxt = add(p, d); width = abs(p[0] - trunk_origin[0]) + abs(p[1] - trunk_origin[1]) + abs(p[2] - trunk_origin[2])
        if max_w - 3 < width <= max_w: return [below, add(nxt, (0, -1, 0))] if rng.next_float() < skew else [below]
        if width > max_w: return [below]
        if rng.next_float() < skew: return [below]
        return [nxt] if rng.next_bool() else [below]
    def simulate(p, d, out, layer):
        if layer == max_len or len(out) > max_len: return False
        for q in potential(p, d):
            if can(q):
                out.append(q)
                if not simulate(q, d, out, layer + 1): return False
        return True
    col = origin
    while col[1] < trunk_origin[1]:
        if not can(col): return False
        col = add(col, (0, 1, 0))
    roots = [add(trunk_origin, (0, -1, 0))]
    for d in ((0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0)):
        out = []
        if not simulate(add(trunk_origin, d), d, out, 0): return False
        roots += out; roots.append(add(trunk_origin, d))
    for p in roots:
        if p[1] >= 0: w.b[p] = ("root", "mangrove_roots")
    return True


# ------------------------------------------------------------------------------------------------ the feature
def load(name):
    return json.loads((FEATURES / f"{name}.json").read_text())


def leaf_provider(fp):
    if "id" in fp: return fp["id"].split(":")[1]
    ents = fp["entries"]; tot = sum(e["weight"] for e in ents)
    def pick(rng):
        k = rng.next_int(tot)
        for e in ents:
            k -= e["weight"]
            if k < 0: return (e["data"] if isinstance(e["data"], str) else e["data"]["id"]).split(":")[1]
    return pick


def grow(name, seed, tries=40):
    """One Java-rule tree of feature <name> (e.g. 'fancy_oak'). Returns (World, info). Retries a few seeds if the
    feature refuses (Java refuses too: mangrove roots that run out of length, etc.)."""
    j = load(name)
    for k in range(tries):
        rng = Rng(seed * 1000 + k); w = World()
        root = j.get("root_placer")
        tp = Trunk(j["trunk_placer"], w, rng, can_grow_through=("root", "leaf") if root else ())
        fp = Foliage(j["foliage_placer"], w, rng, leaf_provider(j["foliage_provider"]))
        th = tp.tree_height(); fh = fp.foliage_height(th); lr = fp.foliage_radius(th - fh)
        origin = (0, 0, 0); trunk_origin = origin
        if root:
            trunk_origin = (0, sample(root["trunk_offset_y"], rng), 0)
            if not mangrove_roots(root, w, rng, origin, trunk_origin): continue
        atts = tp.place(th, trunk_origin)
        for a in atts: fp.create(th, a, fh, lr)
        logs = sum(1 for v in w.b.values() if v[0] == "log")
        if logs == 0: continue
        return w, {"feature": name, "seed": seed, "try": k, "tree_height": th, "foliage_height": fh, "leaf_radius": lr,
                   "logs": logs, "leaves": sum(1 for v in w.b.values() if v[0] == "leaf"), "roots": sum(1 for v in w.b.values() if v[0] == "root"),
                   "attachments": len(atts)}
    raise RuntimeError(f"{name}: no tree in {tries} tries")


# the Java trees J1 renders (feature file -> label); poplar = the 26.4 snapshot tree
SPECIES = [("oak", "OAK (small)"), ("fancy_oak", "FANCY OAK"), ("birch", "BIRCH"), ("super_birch_bees", "TALL BIRCH"),
           ("spruce", "SPRUCE"), ("pine", "PINE"), ("mega_spruce", "MEGA SPRUCE"), ("mega_pine", "MEGA PINE"),
           ("jungle_tree", "JUNGLE"), ("mega_jungle_tree", "MEGA JUNGLE"), ("acacia", "ACACIA"), ("dark_oak", "DARK OAK"),
           ("pale_oak", "PALE OAK"), ("cherry", "CHERRY"), ("mangrove", "MANGROVE"), ("tall_mangrove", "TALL MANGROVE"),
           ("azalea_tree", "AZALEA"), ("orange_poplar", "POPLAR (26.4 snapshot)")]

if __name__ == "__main__":
    for name, lab in SPECIES:
        stats = [grow(name, s)[1] for s in range(1, 41)]
        print(f"{lab:24s} height {min(x['tree_height'] for x in stats)}-{max(x['tree_height'] for x in stats)}  logs {min(x['logs'] for x in stats)}-{max(x['logs'] for x in stats)}"
              f"  leaves {min(x['leaves'] for x in stats)}-{max(x['leaves'] for x in stats)}  roots {max(x['roots'] for x in stats)}  retries {sum(x['try'] for x in stats)}")
