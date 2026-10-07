#!/usr/bin/env python3
"""structure_block_audit.py — Abs0lum's ruling (10-06): "every structure checked to be using our unique blocks (sloped roof
ridges instead of stepped roofs like regular Minecraft creates; our trees and make sure we don't import worse versions;
etc.)".  Block-level audit of every .mcstructure template (BP-02 structures/ by default, any extra folder on request) and
of the runtime placements in the pack's scripts.

Every placed block (layer 0 of block_indices) is classified:
  OURS            id defined in the pack's blocks/ (or in a companion pack's blocks/, e.g. the CIVITAS markers BP)
  RULED           vanilla, an equivalent of ours exists, but a standing ruling / runtime converter keeps vanilla in
                  templates (RULED_VANILLA below, each row cites its source)  -> counted, never a finding
  FINDING         vanilla where our model has an equivalent for THIS use (a detector below decided the use) -> finding
  NO_EQUIV        vanilla with no equivalent of ours for this use (stone, glass, doors, ladders, curbs, interior stairs ...)
  TECH            air, structure_void, light_block*, water (technical / fluid)
  UNKNOWN         neither ours nor vanilla (vanilla = bedrock-samples RP blocks.json 1.26.50.4, or failing that the exact
                  string "minecraft:<id>" inside the BDS 1.26.52.3 binary) -> finding (the engine places nothing / errors)
pw-block checks (finding when violated):
  STATE           a state name or value that the block's CURRENT definition does not declare (a template baked against an
                  older generation of the block; how the engine resolves it on load is NOT verified here — static finding, P1)
  TREE-*          tree templates pw/trees/<stem>_<nn>: logs are pw:<stem> (D-C337: acacia / cherry / mangrove keep vanilla
                  square trunks + mangrove roots), leaves pw:<species>_leaves of the SAME species, exactly one root
                  pw:<stem>_root whose pw:tpl + 16*pw:tpl_hi == nn (pw_fell_rules.templateName replays THAT template)
  ROOF-GAP        a pw:roof45 slope whose uphill side opens onto air with no roof piece above (a hole in the roof or an
                  unridged top; roof-kit / test pads exempt)
  ROOF-MAT        a roof whose pieces mix materials (e.g. thatch slopes + oak hips); pw_companion.js AM_MATS = oak, spruce
                  only, so a thatch roof gets no fold / ridge-end / pyramidion rule
Detectors for vanilla (geometry from the composite: a stage file s<k> is read inside the union of its stem's s0..s4, so
'sky above' and 'ground level' are the finished building's; the finding is filed to the stage that places the block):
  STEPPED-STAIR-ROOF   vanilla *_stairs used as a roof course: at least 3 above the ground level G, AND (sky above it, or
                       directly under a roof/stair-roof cell) AND one of: part of a rising diagonal run (another stair / roof
                       cell one up and one across in its ascent direction, or one down and one across against it),
                       touching a pw roof cell, or sitting on a wall top at the building's edge. Upside-down stairs
                       touching a roof cell = eave trim. Stairs with a ceiling above (interior flights), ground steps
                       (y < G+3) and road curbs are NOT roofs.   -> pw:roof45_<mat>, state = downhill side
  STEPPED-SLAB-ROOF    vanilla slabs above G+3 with sky above that step a half block along a line (slab / full block
                       neighbours rising) or touch a roof cell  -> pw:roof45_<mat>
  FLAT-SLAB-ROOF       vanilla slabs with sky above roofing a walkable space (air under them, a floor 3..5 below): a flat
                       vanilla canopy -> pw:roof45_<mat> lean-to, or a ruling that keeps it
  STEPPED-BLOCK-ROOF   full vanilla blocks on the skyline above G+3 that rise 1:1 for >= 3 steps along one axis (a stair-
                       stepped gable made of cubes)  -> pw:roof45_<mat> courses + ridge
  SEATED               a vanilla stair (not upside down) or flower resting on a BOTTOM slab -> pw:seated_<id> (main.js
                       SEATED STAIRS / PW_VEG_SEAT convert only on playerPlaceBlock, which a structure load never fires)
  RAMP                 a half-step climb in an open walking surface (y < G+3) of bottom slabs between a lower and a higher
                       full surface, where pw:ramp_<mat>_* exists for that material -> pw:ramp_<mat>_2_lo / _2_hi
  CHAIR / TABLE        an isolated vanilla stair (no flight) standing on a floor under a ceiling = a chair stand-in ->
                       pw:furn_chair_<wood>; a fence post capped by a carpet / pressure plate = a table stand-in ->
                       pw:furn_table_<wood>   (pw furniture woods: oak, spruce, dark_oak)
  HEARTH               vanilla campfire / soul_campfire in a building -> pw:hearth_<mat>
  DECOR-TREE           vanilla leaves (or a vanilla log touching leaves) outside the tree templates -> a pw tree template
  TREE-VANILLA         vanilla log / leaves inside a tree template beyond the D-C337 exemption -> pw:<stem> / pw leaves
  DUAL-WALL (opportunity, not a finding)   a 2-thick wall: vanilla M outside + vanilla N inside where pw:wall_<M> exists
                       and N is one of its pw:inner finishes -> one pw:wall_<M> with pw:inner=N
Runtime (--scripts): literal setType / BlockPermutation.resolve of vanilla ids in the pack's scripts that our model
covers (stairs, logs, leaves, planks, slabs, campfire, vine), plus the CIV_BUILDINGS 'dir' re-placement table.

Usage: structure_block_audit.py [--pack DIR] [--extra-blocks DIR ...] [--root DIR ...] [--json OUT] [--scripts] [--quiet]
       (defaults: --pack /home/claude/_build/bp02-227, --extra-blocks the newest markers BP blocks/, --root <pack>/structures)
Exit status 1 when any FINDING / UNKNOWN / STATE / TREE-* / ROOF-MAT is present (a gate for future builds and for
structures imported from studied mods).  Read-only: it never writes into the pack.
Complexity: O(cells) per structure (numpy columns); the BDS string lookup is one mmap scan per unknown id."""
import argparse
import collections
import json
import mmap
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

HOME = Path("/home/claude")
VANILLA_BLOCKS_JSON = HOME / "_intake/bedrock-samples/resource_pack/blocks.json"     # 1.26.50.4 (version.json)
BDS_BINARY = HOME / "_bds/srv/bedrock_server"                                         # 1.26.52.3

# ------------------------------------------------------------------ the rule set (data; cite the source of each row)
TECH = {"minecraft:air", "minecraft:structure_void", "minecraft:water", "minecraft:flowing_water", "minecraft:light_block"}
PASSABLE_PREFIX = ("minecraft:air", "minecraft:structure_void", "minecraft:light_block", "minecraft:water",
                   "minecraft:flowing_water")
FURN_WOODS = ("oak", "spruce", "dark_oak")                         # blocks/pw_furn_*_<wood>.json
ROOF_MATS = ("oak", "spruce", "thatch")                            # pw:roof45_<m>; hips / ends / pyramidion: oak, spruce
COMPANION_MATS = ("oak", "spruce")                                 # pw_companion.js AM_MATS
SQUARE_TRUNK_SPECIES = {"acacia", "cherry", "mangrove"}            # D-C337 (AUDIT-TREES-LEAVES-2026-10-04 §2)
TREE_SPECIES = ("pale_oak", "dark_oak", "oak", "spruce", "birch", "jungle", "acacia", "cherry", "mangrove")
FLOWERS_SEATABLE = None                                            # filled from the pack: every pw:seated_<flower> id
# vanilla ids that have an equivalent of ours but stay vanilla in templates by ruling / runtime conversion
RULED_VANILLA = [
    (re.compile(r"^minecraft:(oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry|pale_oak|crimson|warped)_planks$"),
     "pw:{0}_planks_grid", "pw_planks.js: the scanner swaps vanilla planks near players (set once) and the CIVITAS placer "
     "reflows grid planks after a load"),
    (re.compile(r"^minecraft:vine$"), "pw:vine", "pw_vine.js: vanilla vines are swapped once to pw:vine near players"),
    (re.compile(r"^minecraft:(grass_block|podzol|mycelium|crimson_nylium|warped_nylium)$"), "pw:{0}",
     "pw_ground.js CONVERSION SCOPE (his ruling): only the riser at an elevation change converts, never open ground"),
]
# vanilla block family -> roof material our kit offers (nearest), None = no pw roof in that material (a gap)
def roof_mat_of(vid):
    n = vid.split(":", 1)[1]
    if "spruce" in n or "dark_oak" in n:
        return "spruce"
    if any(w in n for w in ("oak", "birch", "jungle", "acacia", "mangrove", "cherry", "bamboo", "crimson", "warped", "pale")):
        return "oak"
    if "hay" in n:
        return "thatch"
    return None


RAMP_MAT = {"smooth_stone": "smooth_stone", "stone_brick": "stonebrick", "cobblestone": "cobble", "stone_stairs": "cobble",
            "mossy_cobblestone": "cobble"}
FACING = {0: "east", 1: "west", 2: "south", 3: "north"}            # stairs weirdo_direction = the HIGH side (palacegen.py:47)
VEC = {"east": (1, 0), "west": (-1, 0), "south": (0, 1), "north": (0, -1)}
OPP = {"east": "west", "west": "east", "north": "south", "south": "north"}
ROOF_RE = re.compile(r"^pw:(roof45|roof45_ridge|roof_hip|roof_ridge_end|roof_pyramidion|roof63_lower|roof63_upper|"
                     r"roof_gusset_lower|roof_gusset_upper|crown_ring|rafter45|sweep_s)")


def strip_jsonc(t):
    out, i, n, ins = [], 0, len(t), False
    while i < n:
        c = t[i]
        if ins:
            out.append(c)
            if c == "\\":
                out.append(t[i + 1]); i += 2; continue
            if c == '"':
                ins = False
            i += 1; continue
        if c == '"':
            ins = True; out.append(c); i += 1; continue
        if t.startswith("//", i):
            j = t.find("\n", i); i = n if j < 0 else j; continue
        if t.startswith("/*", i):
            j = t.find("*/", i + 2); i = n if j < 0 else j + 2; continue
        out.append(c); i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def load_jsonc(p):
    return json.loads(strip_jsonc(Path(p).read_text(encoding="utf-8-sig")))


# ------------------------------------------------------------------ registries
def state_space(desc):
    sp = {k: list(v) if isinstance(v, list) else v for k, v in desc.get("states", {}).items()}
    tr = desc.get("traits", {})
    if "minecraft:placement_direction" in tr:
        for s in tr["minecraft:placement_direction"].get("enabled_states", []):
            sp[s] = ["north", "south", "east", "west"] if s == "minecraft:cardinal_direction" else ["down", "up", "north", "south", "east", "west"]
    if "minecraft:placement_position" in tr:
        for s in tr["minecraft:placement_position"].get("enabled_states", []):
            sp[s] = ["bottom", "top"] if s == "minecraft:vertical_half" else ["down", "up", "north", "south", "east", "west"]
    return sp


def load_blocks(dirs):
    """id -> (pack label, state space) for every block definition under the given blocks/ dirs"""
    reg = {}
    for label, d in dirs:
        for f in sorted(Path(d).rglob("*.json")):
            try:
                desc = load_jsonc(f)["minecraft:block"]["description"]
            except Exception as e:  # noqa: BLE001
                print(f"WARN unreadable block file {f}: {e}", file=sys.stderr)
                continue
            reg.setdefault(desc["identifier"], (label, state_space(desc), str(f)))
    return reg


class Vanilla:
    def __init__(self):
        self.ids = {"minecraft:" + k for k in load_jsonc(VANILLA_BLOCKS_JSON) if k != "format_version"}
        self.extra, self._mm = {}, None

    def has(self, vid):
        if vid in self.ids:
            return "blocks.json"
        if vid not in self.extra:
            self.extra[vid] = None
            if BDS_BINARY.exists():
                if self._mm is None:
                    self._fh = open(BDS_BINARY, "rb")
                    self._mm = mmap.mmap(self._fh.fileno(), 0, access=mmap.ACCESS_READ)
                if self._mm.find(b"\0" + vid.encode() + b"\0") >= 0:
                    self.extra[vid] = "bds-binary-string"
        return self.extra[vid]


# ------------------------------------------------------------------ structure model
class Grid:
    """names[x, y, z] -> palette index into `pal` (list of (name, states dict)); -1 = structure void"""

    def __init__(self, st):
        self.size = st.size
        self.pal = [(n, {k: v.value for k, v in s.items()}) for n, s, _v in st.palette]
        self.idx = np.array(st.layer0, dtype=np.int32).reshape(st.size)

    @staticmethod
    def composite(sts):
        g = Grid(sts[0])
        pal_index = {}
        newpal = []
        def remap(grid):
            m = np.full(len(grid.pal) + 1, -1, dtype=np.int32)
            for i, (n, s) in enumerate(grid.pal):
                key = (n, json.dumps(s, sort_keys=True))
                if key not in pal_index:
                    pal_index[key] = len(newpal); newpal.append((n, s))
                m[i] = pal_index[key]
            return m
        acc = np.full(g.size, -1, dtype=np.int32)
        for st in sts:
            gg = Grid(st)
            m = remap(gg)
            vals = np.where(gg.idx >= 0, m[gg.idx], -1)
            acc = np.where(vals >= 0, vals, acc)
        g.pal, g.idx = newpal, acc
        return g


def passable_name(n):
    return n.startswith(PASSABLE_PREFIX) or n in ("minecraft:ladder", "minecraft:vine", "pw:vine") or n.endswith("_carpet") \
        or n.endswith("_button") or n.endswith("pressure_plate") or n == "minecraft:wheat" or n.startswith("pw:seated_") and \
        not n.endswith("_stairs")


class Ctx:
    """geometry helpers over a (composite) grid"""

    def __init__(self, g):
        self.g = g
        sx, sy, sz = g.size
        self.sx, self.sy, self.sz = sx, sy, sz
        names = [n for n, _ in g.pal]
        solid_pal = np.array([not passable_name(n) for n in names] + [False], dtype=bool)
        idx = g.idx
        self.solid = solid_pal[np.where(idx >= 0, idx, len(names))]
        # top[x, z] = highest solid y (-1 = none)
        ys = np.arange(sy)[None, :, None]
        self.top = np.where(self.solid, ys, -1).max(axis=1)
        self.G = self.ground_level()

    def name(self, x, y, z):
        if not (0 <= x < self.sx and 0 <= y < self.sy and 0 <= z < self.sz):
            return None
        k = self.g.idx[x, y, z]
        return None if k < 0 else self.g.pal[k][0]

    def states(self, x, y, z):
        k = self.g.idx[x, y, z]
        return {} if k < 0 else self.g.pal[k][1]

    def is_solid(self, x, y, z):
        return 0 <= x < self.sx and 0 <= y < self.sy and 0 <= z < self.sz and bool(self.solid[x, y, z])

    def sky(self, x, y, z):
        return self.top[x, z] <= y

    def h(self, x, z):
        """surface height of column (x, z) in half blocks: 2 * (top + 1), minus 1 when the top cell is a bottom slab"""
        if not (0 <= x < self.sx and 0 <= z < self.sz):
            return None
        t = int(self.top[x, z])
        if t < 0:
            return None
        n = self.name(x, t, z) or ""
        return 2 * (t + 1) - (1 if is_bottom_slab(n, self.states(x, t, z)) else 0)

    def ground_level(self):
        """modal top-solid y over the perimeter columns (the terrain / pavement the structure stands on)"""
        sx, sz = self.sx, self.sz
        tops = []
        for x in range(sx):
            for z in (0, sz - 1):
                tops.append(int(self.top[x, z]))
        for z in range(sz):
            for x in (0, sx - 1):
                tops.append(int(self.top[x, z]))
        tops = [t for t in tops if t >= 0]
        if not tops:
            return 0
        return collections.Counter(tops).most_common(1)[0][0]


# ------------------------------------------------------------------ the audit of one structure
def is_roof_cell(n):
    return bool(n) and bool(ROOF_RE.match(n))


def stair_high(states):
    return FACING.get(int(states.get("weirdo_direction", 0)))


def audit_structure(rel, fam, own_grid, ctx, reg, van, cache, seated_ids, ramp_ids, wall_inner, offsets=None):
    """own_grid: the file's own cells (what it places); ctx: geometry of the composite. Returns a report dict."""
    counts = collections.Counter()
    by_class = collections.defaultdict(collections.Counter)
    findings, opps = [], collections.Counter()
    idx = own_grid.idx
    pal = own_grid.pal
    used = collections.Counter(idx[idx >= 0].tolist())
    cls_of, state_bad, unknown = {}, {}, {}
    for k, n_cells in used.items():
        n, s = pal[k]
        c = classify_id(n, reg, van, cache)
        cls_of[k] = c
        by_class[c][n] += n_cells
        counts[c] += n_cells
        if c == "OURS":
            bad = check_states(n, s, reg)
            if bad:
                key = (n, json.dumps(bad, sort_keys=True))
                state_bad[key] = state_bad.get(key, 0) + n_cells
        if c == "UNKNOWN":
            unknown[n] = unknown.get(n, 0) + n_cells
    for n, n_cells in unknown.items():
        findings.append(F("UNKNOWN", n, None, f"{n_cells} cells: id defined nowhere (not in the pack, the companion packs, "
                          "vanilla blocks.json 1.26.50.4 nor the BDS 1.26.52.3 binary)", None, count=n_cells))
    for (n, bad), n_cells in state_bad.items():
        findings.append(F("STATE", n, None, f"{n_cells} cells carry {bad}: not declared by the current definition "
                          f"({Path(reg[n][2]).name})", f"{n} without those states", count=n_cells))
    # ---- per-cell detectors (vanilla only, plus tree checks)
    tree = fam == "trees"
    stem_m = re.match(r"(.+)_(\d\d)$", Path(rel).stem) if tree else None
    stem, nn = (stem_m.group(1), int(stem_m.group(2))) if stem_m else (None, None)
    species = next((s for s in TREE_SPECIES if stem and stem.startswith(s)), None) if tree else None
    roots, tree_bad, census = [], collections.Counter(), collections.Counter()
    roof_mats = collections.Counter()
    cells = np.argwhere(idx >= 0)
    for x, y, z in cells:
        k = int(idx[x, y, z])
        n, s = pal[k]
        c = cls_of[k]
        if c == "TECH":
            continue
        if n.startswith("pw:"):
            if is_roof_cell(n):
                m = n.rsplit("_", 1)[1]
                roof_mats[m] += 1
                if fam != "roof-kit/test" and re.match(r"^pw:roof45_(oak|spruce|thatch)$", n):
                    gap = roof_gap(ctx, (int(x), int(y), int(z)), s)
                    if gap:
                        findings.append(F("ROOF-GAP", n, (int(x), int(y), int(z)), gap, "close the course: the next roof45 "
                                          "course / a pw:roof45_ridge_<mat> / pw:roof_ridge_end_<mat> on the uphill side"))
            if tree:
                tree_check_pw(n, s, (x, y, z), stem, nn, species, roots, tree_bad)
            continue
        if not n.startswith("minecraft:") or c == "UNKNOWN":
            continue
        base = n.split(":", 1)[1]
        p = (int(x), int(y), int(z))
        # trees
        if tree:
            if base.endswith("_log") or base.endswith("_wood") or base == "mangrove_roots":
                if species in SQUARE_TRUNK_SPECIES and (base.startswith(species) or base == "mangrove_roots"):
                    reclass(by_class, counts, n, c, "RULED", note="D-C337 square trunk")
                    continue
                findings.append(F("TREE-VANILLA", n, p, "vanilla wood in a tree template", f"pw:{stem}"))
                reclass(by_class, counts, n, c, "FINDING")
                continue
            if base.endswith("_leaves"):
                findings.append(F("TREE-VANILLA", n, p, "vanilla leaves in a tree template", f"pw:{species}_leaves"))
                reclass(by_class, counts, n, c, "FINDING")
                continue
        else:
            if base.endswith("_leaves") or base.endswith("azalea_leaves_flowered"):
                findings.append(F("DECOR-TREE", n, p, "vanilla leaves outside the tree templates",
                                  "a pw tree template (pw:trees/<species>_<age>_nn) or pw:<species>_leaves"))
                reclass(by_class, counts, n, c, "FINDING")
                continue
            if base.endswith("_log") and touches(ctx, p, lambda q: q and q.endswith("_leaves")):
                findings.append(F("DECOR-TREE", n, p, "vanilla log carrying leaves (a decorative tree)", "a pw tree template"))
                reclass(by_class, counts, n, c, "FINDING")
                continue
        if base in ("campfire", "soul_campfire"):
            findings.append(F("HEARTH", n, p, "vanilla fire in a building", "pw:hearth_<material> (+ pw:flue_<material>)"))
            reclass(by_class, counts, n, c, "FINDING")
            continue
        if base.endswith("_stairs"):
            r = stair_use(ctx, p, n, s, seated_ids)
            if r:
                findings.append(r)
                reclass(by_class, counts, n, c, "FINDING")
                census[(n, r["kind"])] += 1
            else:
                census[(n, use_verdict(ctx, p, stair=True))] += 1
            continue
        if base.endswith("_slab") or base.endswith("double_slab"):
            r = slab_use(ctx, p, n, s, ramp_ids)
            if r:
                findings.append(r)
                reclass(by_class, counts, n, c, "FINDING")
                census[(n, r["kind"])] += 1
            else:
                census[(n, use_verdict(ctx, p, stair=False))] += 1
            continue
        if base.endswith("_fence") and not base.endswith("_gate"):
            above = ctx.name(p[0], p[1] + 1, p[2]) or ""
            below = ctx.name(p[0], p[1] - 1, p[2]) or ""
            if (above.endswith("_carpet") or above.endswith("pressure_plate")) and ctx.is_solid(p[0], p[1] - 1, p[2]) \
                    and not below.endswith("_fence") and not ctx.sky(*p):
                wood = next((w for w in FURN_WOODS if base.startswith(w + "_")), None) or "oak"
                findings.append(F("TABLE", n, p, f"fence + {above.split(':')[1]} = a table stand-in", f"pw:furn_table_{wood}"))
                reclass(by_class, counts, n, c, "FINDING")
            continue
        if base in FLOWERS_SEATABLE_BASES:
            below = ctx.name(p[0], p[1] - 1, p[2])
            if below and is_bottom_slab(below, ctx.states(p[0], p[1] - 1, p[2])) and f"pw:seated_{base}" in seated_ids:
                findings.append(F("SEATED", n, p, "plant on a bottom slab (pops off in vanilla)", f"pw:seated_{base}"))
                reclass(by_class, counts, n, c, "FINDING")
            continue
        # full blocks: stepped cube roofs + dual-wall opportunities
        if c in ("NO_EQUIV",) and bool(ctx.solid[p]):
            r = block_step_roof(ctx, p, n)
            if r:
                findings.append(r)
                reclass(by_class, counts, n, c, "FINDING")
                continue
            w = dual_wall(ctx, p, n, wall_inner)
            if w:
                opps[w] += 1
    # tree template totals
    if tree:
        if stem and species:
            if len(roots) != 1:
                findings.append(F("TREE-ROOT", f"pw:{stem}_root", roots[0][1] if roots else None,
                                  f"{len(roots)} root cells (exactly 1 required) at {[r[1] for r in roots]}", f"pw:{stem}_root"))
            for rid, rp, tpl in roots:
                if rid != f"pw:{stem}_root":
                    findings.append(F("TREE-ROOT", rid, rp, f"root id does not match the template stem {stem}", f"pw:{stem}_root"))
                elif tpl != nn:
                    findings.append(F("TREE-ROOT", rid, rp, f"root index pw:tpl+16*tpl_hi = {tpl}, file is _{nn:02d}: the "
                                      f"felling replays pw:trees/{stem}_{tpl:02d}", f"pw:tpl={nn % 16}, pw:tpl_hi={nn // 16}"))
        for (kind, ident), cnt in tree_bad.items():
            findings.append(F(kind, ident, None, f"{cnt} cells", None, count=cnt))
    # roof material mix, per connected roof (26-neighbour components of roof cells)
    for comp_mats, first in roof_components(idx, pal):
        mats = {m for m in comp_mats if m in ROOF_MATS}
        if len(mats) > 1:
            findings.append(F("ROOF-MAT", ",".join(sorted(mats)), first, f"one roof mixes materials {dict(comp_mats)}",
                              "one material per roof (thatch has no hip / ridge end / pyramidion piece and no companion rule)"))
    return {"file": rel, "family": fam, "size": list(own_grid.size), "G": int(ctx.G), "counts": dict(counts),
            "by_class": {k: dict(v) for k, v in by_class.items()}, "findings": findings, "opportunities": dict(opps),
            "stair_slab_uses": {f"{k[0]} | {k[1]}": v for k, v in sorted(census.items())}}


def roof_components(idx, pal):
    roof_k = [k for k, (n, _s) in enumerate(pal) if is_roof_cell(n)]
    if not roof_k:
        return []
    mask = np.isin(idx, roof_k)
    seen = np.zeros_like(mask)
    out = []
    for start in map(tuple, np.argwhere(mask)):
        if seen[start]:
            continue
        stack, mats = [start], collections.Counter()
        seen[start] = True
        while stack:
            c = stack.pop()
            mats[pal[idx[c]][0].rsplit("_", 1)[1]] += 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        q = (c[0] + dx, c[1] + dy, c[2] + dz)
                        if all(0 <= q[i] < mask.shape[i] for i in range(3)) and mask[q] and not seen[q]:
                            seen[q] = True
                            stack.append(q)
        out.append((dict(mats), [int(v) for v in start]))
    return out


def roof_gap(ctx, p, s):
    """a 45° slope whose uphill side opens onto air with no roof piece above it: a hole or an unridged top"""
    d = s.get("minecraft:cardinal_direction")
    if d not in VEC:
        return None
    x, y, z = p
    ux, uz = VEC[OPP[d]]
    if not (0 <= x + ux < ctx.sx and 0 <= z + uz < ctx.sz):
        return None                         # the uphill side is in the next piece of a cut model: not judged here
    if ctx.is_solid(x + ux, y, z + uz):
        return None
    if is_roof_cell(ctx.name(x + ux, y + 1, z + uz)) or is_roof_cell(ctx.name(x, y + 1, z)):
        return None
    return f"slope (downhill {d}) ends open on its uphill side ({ctx.name(x + ux, y, z + uz) or 'structure void'} beside, " \
           f"{ctx.name(x + ux, y + 1, z + uz) or 'structure void'} above it)"


def use_verdict(ctx, p, stair):
    x, y, z = p
    if not ctx.sky(x, y, z):
        return "covered (ceiling above: interior flight / floor / soffit)"
    if y < ctx.G + 3:
        return "open, near the ground (steps, curbs, walk surface)"
    return "open, high, not a stepped course (coping / parapet / terrace)"


FLOWERS_SEATABLE_BASES = set()


def F(kind, ident, pos, why, repl, count=1):
    return {"kind": kind, "id": ident, "pos": list(pos) if pos is not None else None, "why": why, "replace_with": repl,
            "count": count}


def reclass(by_class, counts, n, old, new, note=None):
    by_class[old][n] -= 1
    if by_class[old][n] <= 0:
        del by_class[old][n]
    by_class[new][n] += 1
    counts[old] -= 1
    counts[new] += 1


def classify_id(n, reg, van, cache):
    if n in cache:
        return cache[n]
    if n in reg:
        c = "OURS"
    elif n in TECH or n.startswith("minecraft:light_block"):
        c = "TECH"
    elif n.startswith("minecraft:") and van.has(n):
        c = "RULED" if any(rx.match(n) for rx, _r, _w in RULED_VANILLA) else "NO_EQUIV"
    else:
        c = "UNKNOWN"
    cache[n] = c
    return c


def check_states(n, s, reg):
    space = reg[n][1]
    bad = {}
    for k, v in s.items():
        if k not in space:
            bad[k] = v
            continue
        allowed = space[k]
        if isinstance(allowed, dict):        # integer range {"values": {"min":..,"max":..}}
            vals = allowed.get("values", allowed)
            if isinstance(vals, dict) and not (vals.get("min", -1e9) <= v <= vals.get("max", 1e9)):
                bad[k] = v
            continue
        norm = [(1 if a is True else 0 if a is False else a) for a in allowed]
        vv = 1 if v is True else 0 if v is False else v
        if vv not in norm:
            bad[k] = v
    return bad


def tree_check_pw(n, s, p, stem, nn, species, roots, tree_bad):
    if n.endswith("_root"):
        roots.append((n, list(map(int, p)), int(s.get("pw:tpl", 0)) + 16 * int(s.get("pw:tpl_hi", 0))))
        return
    if n.endswith("_leaves"):
        sp = n[3:-7]
        if species and sp != species and not (species == "azalea"):
            tree_bad[("TREE-LEAF-SPECIES", f"{n} in a {species} template")] += 1
        return
    m = re.match(r"^pw:([a-z_]+)_(young|mature|old|elder)$", n)
    if m and stem and n != f"pw:{stem}":
        tree_bad[("TREE-TIER", f"{n} in pw:trees/{stem}_nn (expected pw:{stem})")] += 1


def touches(ctx, p, pred):
    x, y, z = p
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if (dx, dy, dz) != (0, 0, 0) and pred(ctx.name(x + dx, y + dy, z + dz)):
                    return True
    return False


def is_bottom_slab(n, s):
    if n.startswith("pw:slab_"):
        return s.get("minecraft:vertical_half", "bottom") == "bottom"
    if n.startswith("minecraft:") and n.endswith("_slab"):
        if "minecraft:vertical_half" in s:
            return s["minecraft:vertical_half"] == "bottom"
        if "top_slot_bit" in s:
            return not s["top_slot_bit"]
        return True
    return False


def roofish(n):
    return bool(n) and (is_roof_cell(n) or (n.startswith("minecraft:") and (n.endswith("_stairs") or n.endswith("_slab"))))


def stair_use(ctx, p, n, s, seated_ids):
    x, y, z = p
    base = n.split(":", 1)[1]
    ud = bool(s.get("upside_down_bit", 0))
    below = ctx.name(x, y - 1, z)
    # SEATED: an upright stair on a bottom slab
    if not ud and below and is_bottom_slab(below, ctx.states(x, y - 1, z)):
        sid = f"pw:seated_{base}"
        return F("SEATED", n, p, f"stair resting on a bottom slab ({below})", sid if sid in seated_ids else f"{sid} (not defined yet)")
    high = stair_high(s)
    dx, dz = VEC[high]
    above_name = ctx.name(x, y + 1, z)
    exposed = ctx.sky(x, y, z) or is_roof_cell(above_name)
    mat = roof_mat_of(n)
    repl = (f"pw:roof45_{mat} [minecraft:cardinal_direction={OPP[high]}]" if mat else
            f"no pw roof in this material (stone / brick): pw:roof45_<new material> needed, or re-material to oak/spruce/thatch")
    if ud:
        if y >= ctx.G + 3 and touches(ctx, p, is_roof_cell):
            return F("STEPPED-STAIR-ROOF", n, p, "upside-down stair as eave trim under a roof",
                     "drop it (the pw roof45 eave overhang) or pw:rafter45_<oak|spruce> under the eave")
        return None
    if not exposed:
        # a flight under a ceiling = interior staircase; an isolated stair under a ceiling on a floor = a chair stand-in
        run = any((ctx.name(x + dx * k, y + k, z + dz * k) or "").endswith("_stairs") for k in (1, -1))
        side = any((ctx.name(x + ax, y, z + az) or "").endswith("_stairs") for ax, az in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if not run and ctx.is_solid(x, y - 1, z) and not ctx.is_solid(x, y + 1, z):
            wood = next((w for w in FURN_WOODS if base.startswith(w + "_")), None)
            if wood or roof_mat_of(n):
                return F("CHAIR", n, p, f"isolated stair on a floor under a ceiling{' (in a row)' if side else ''} = a seat stand-in",
                         f"pw:furn_{'bench' if side else 'chair'}_{wood or 'oak'} [minecraft:cardinal_direction={OPP[high]}]")
        return None
    if y < ctx.G + 3:
        return None                                                # ground steps, curbs (sky above, near the ground)
    rising = (roofish(ctx.name(x + dx, y + 1, z + dz)) or roofish(ctx.name(x - dx, y - 1, z - dz)))
    on_roof = touches(ctx, p, is_roof_cell)
    edge = any(ctx.sky(x + ax, y - 1, z + az) if 0 <= x + ax < ctx.sx and 0 <= z + az < ctx.sz else True
               for ax, az in ((1, 0), (-1, 0), (0, 1), (0, -1))) and ctx.is_solid(x, y - 1, z)
    if rising or on_roof or edge:
        why = "rising diagonal stair course" if rising else ("against our roof pieces" if on_roof else "on a wall top at the edge")
        return F("STEPPED-STAIR-ROOF", n, p, why + f" (sky above, {y - ctx.G} above ground)", repl)
    return None


def slab_use(ctx, p, n, s, ramp_ids):
    """surface height h in half blocks (Ctx.h); a slab on a 1:2 half-step line = a stepped slope"""
    x, y, z = p
    if not ctx.sky(x, y, z):
        return None
    base = n.split(":", 1)[1]
    hc = ctx.h(x, z)
    line = None
    for ax, az in ((1, 0), (0, 1)):
        for sg in (1, -1):
            dx, dz = ax * sg, az * sg
            up, dn = ctx.h(x + dx, z + dz), ctx.h(x - dx, z - dz)
            if up == hc + 1 and dn == hc - 1:
                more = ctx.h(x + 2 * dx, z + 2 * dz) == hc + 2 or ctx.h(x - 2 * dx, z - 2 * dz) == hc - 2
                line = ({(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(dx, dz)], more)
    covers = (not ctx.is_solid(x, y - 1, z)) and any(ctx.is_solid(x, y - k, z) for k in range(3, 6)) and \
        not any(ctx.is_solid(x, y - k, z) for k in (1, 2))
    if covers and y >= ctx.G + 2 and not (line and line[1]):
        mat = roof_mat_of(n)
        return F("FLAT-SLAB-ROOF", n, p, f"slab roofing a walkable space (air under it, floor {next(k for k in range(3, 6) if ctx.is_solid(x, y - k, z))} below)",
                 (f"pw:roof45_{mat} as a lean-to (one slope) or a ruling that flat slab canopies stay" if mat else
                  "no pw roof in this material; flat stone roofs are a design choice (ruling needed)"))
    if y >= ctx.G + 3:
        on_roof = touches(ctx, p, is_roof_cell)
        if on_roof or (line and line[1]):
            mat = roof_mat_of(n)
            why = "slab against our roof pieces" if on_roof else f"half-step slab course rising {line[0]}"
            return F("STEPPED-SLAB-ROOF", n, p, why + f" (sky above, {y - ctx.G} above ground)",
                     (f"pw:roof45_{mat}" + (f" [minecraft:cardinal_direction={OPP[line[0]]}]" if line else "")) if mat else
                     "no pw roof in this material: pw:roof45_<new material> or re-material")
        return None
    rm = next((v for k, v in RAMP_MAT.items() if base.startswith(k)), None)
    if not rm or f"pw:ramp_{rm}_2_lo" not in ramp_ids or hc is None or hc % 2 == 0:
        return None
    # a half-step landing: walking along an axis, the surface goes hc-1 -> (hc on slab cells) x k -> hc+1, k <= 4
    for ax, az in ((1, 0), (0, 1)):
        for sg in (1, -1):
            dx, dz = ax * sg, az * sg
            k_up = next((k for k in range(1, 5) if ctx.h(x + dx * k, z + dz * k) != hc), None)
            k_dn = next((k for k in range(1, 5) if ctx.h(x - dx * k, z - dz * k) != hc), None)
            if k_up is None or k_dn is None:
                continue
            if ctx.h(x + dx * k_up, z + dz * k_up) == hc + 1 and ctx.h(x - dx * k_dn, z - dz * k_dn) == hc - 1:
                span = k_up + k_dn - 1
                d = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(dx, dz)]
                kit = f"pw:ramp_{rm}_2_lo + _2_hi" if span <= 2 else f"pw:ramp_{rm}_4_q1..q4"
                return F("RAMP", n, p, f"half-step slab landing ({span} cells) climbing {d} in an open walking surface "
                         f"(a full block rise taken as two half steps)", f"{kit} over the climb (cells rising {d})")
    return None


def block_step_roof(ctx, p, n):
    """a 1:1 cube staircase on the skyline above G+3 (>= 3 steps rising toward a peak)"""
    x, y, z = p
    if y < ctx.G + 3 or not ctx.sky(x, y, z):
        return None
    base = n.split(":", 1)[1]
    if base.endswith(("_fence", "_wall", "_pane", "door", "_bars")) or base in ("lantern", "bell", "chain", "iron_chain"):
        return None
    for ax, az in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        steps = 0
        for k in range(1, 4):
            xx, yy, zz = x + ax * k, y + k, z + az * k
            if not (0 <= xx < ctx.sx and 0 <= zz < ctx.sz and yy < ctx.sy):
                break
            nn = ctx.name(xx, yy, zz)
            if not (nn and nn.startswith("minecraft:") and ctx.is_solid(xx, yy, zz) and ctx.top[xx, zz] == yy):
                break
            # the cell under a step must be solid (a stepped mass, not a floating merlon)
            if not ctx.is_solid(xx, yy - 1, zz):
                break
            steps += 1
        if steps >= 3:
            d = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(ax, az)]
            mat = roof_mat_of(n)
            return F("STEPPED-BLOCK-ROOF", n, p, f"cube staircase rising {d} for {steps} steps on the skyline",
                     (f"pw:roof45_{mat} [minecraft:cardinal_direction={OPP[d]}]" if mat else
                      "no pw roof in this material (stone): pw:roof45_<new material> or re-material"))
    return None


def dual_wall(ctx, p, n, wall_inner):
    """exterior vanilla M (sky-side air beside it) backed by a vanilla N finish with interior air behind -> pw:wall_M"""
    base = n.split(":", 1)[1]
    if f"pw:wall_{base}" not in wall_inner:
        return None
    x, y, z = p
    for ax, az in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        out = (x - ax, y, z - az)
        inn = (x + ax, y, z + az)
        beyond = (x + 2 * ax, y, z + 2 * az)
        if not (0 <= out[0] < ctx.sx and 0 <= out[2] < ctx.sz) or ctx.is_solid(*out) or not ctx.sky(*out):
            continue
        nn = ctx.name(*inn)
        if not nn or not nn.startswith("minecraft:"):
            continue
        fin = nn.split(":", 1)[1]
        if fin != base and fin in wall_inner[f"pw:wall_{base}"] and \
                0 <= beyond[0] < ctx.sx and 0 <= beyond[2] < ctx.sz and not ctx.is_solid(*beyond) and not ctx.sky(*beyond):
            return f"pw:wall_{base} [pw:inner={fin}]"
    return None


# ------------------------------------------------------------------ families
def family_of(rel):
    r = "/" + rel.replace("\\", "/")
    if "/trees/" in r:
        return "trees"
    if "/road/" in r:
        return "road"
    if "/ponds/" in r:
        return "ponds"
    if "/sf_nba/" in r:
        return "sf_nba"
    if "/stages/" in r:
        return "palace-stages" if "palace" in r else ("castle-stages" if "castle" in r else "building-stages")
    if "mvv_palace" in r:
        return "palace-pieces"
    if "castle" in r:
        return "castle-pieces"
    if "mvv_" in r:
        return "buildings"
    return "roof-kit/test"


# ------------------------------------------------------------------ runtime placements
RUNTIME_RX = re.compile(r'(setType|BlockPermutation\.resolve|fillBlocks|setBlockType)\(\s*([^)]{0,120})')
COVERED = re.compile(r'"minecraft:([a-z_0-9]*(_stairs|_log|_wood|_leaves|_slab|_planks|campfire)|vine)"')


def audit_scripts(scripts_dir):
    out = []
    for f in sorted(Path(scripts_dir).glob("*.js")):
        if f.name in ("pw_gallery_data.js", "pw_gallery_text.js", "pw_civ_buildings.js"):
            continue
        lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        consts = {}
        for ln in lines:
            for m in re.finditer(r'\b([A-Z_][A-Z0-9_]*)\s*=\s*"(minecraft:[a-z_0-9]+)"', ln):
                consts[m.group(1)] = m.group(2)
        for i, ln in enumerate(lines, 1):
            for m in RUNTIME_RX.finditer(ln):
                arg = m.group(2)
                ids = re.findall(r'"(minecraft:[a-z_0-9]+)"', arg) + [consts[c] for c in re.findall(r"\b([A-Z_][A-Z0-9_]*)\b", arg) if c in consts]
                for vid in ids:
                    if COVERED.search(f'"{vid}"'):
                        out.append({"file": f.name, "line": i, "id": vid, "code": ln.strip()[:220]})
    # the CIVITAS building table: blocks the clock re-places after a rotated stage
    cb = Path(scripts_dir) / "pw_civ_buildings.js"
    tab = collections.Counter()
    if cb.exists():
        t = cb.read_text(encoding="utf-8")
        d, _ = json.JSONDecoder().raw_decode(t, t.index("{"))
        for b, e in d.items():
            for row in e.get("dir", []):
                tab[row[3]] += 1
    return out, dict(tab)


# ------------------------------------------------------------------ self-test (synthetic structures: every detector must fire)
def selftest(reg, van, seated_ids, ramp_ids, wall_inner):
    S = lambda **kw: {k: (M.i(v) if isinstance(v, bool) or isinstance(v, int) else M.s(v)) for k, v in kw.items()}
    st = M.Structure((24, 16, 24))
    for x in range(24):
        for z in range(24):
            st.set(x, 0, z, "minecraft:grass_block")                         # ground G = 0
    # house A: walls x 2..8, z 2..8, height 1..4, stepped oak_stairs roof rising north->south and south->north
    for y in range(1, 5):
        for x in range(2, 9):
            for z in range(2, 9):
                if x in (2, 8) or z in (2, 8):
                    st.set(x, y, z, "minecraft:stone_bricks")
    for k in range(4):                                                      # courses k: z = 1+k (north side) / 9-k (south)
        for x in range(1, 10):
            st.set(x, 5 + k, 1 + k, "minecraft:oak_stairs", S(weirdo_direction=2, upside_down_bit=0))   # high side south
            st.set(x, 5 + k, 9 - k, "minecraft:oak_stairs", S(weirdo_direction=3, upside_down_bit=0))   # high side north
    for x in range(1, 10):
        st.set(x, 9, 5, "minecraft:oak_planks")                             # the ridge row
    # interior: a flight under the roof (no sky) + an isolated chair + a fence table
    for k in range(3):
        st.set(3 + k, 1 + k, 4, "minecraft:spruce_stairs", S(weirdo_direction=0, upside_down_bit=0))
    st.set(6, 1, 7, "minecraft:spruce_stairs", S(weirdo_direction=1, upside_down_bit=0))
    st.set(4, 1, 7, "minecraft:oak_fence"); st.set(4, 2, 7, "minecraft:red_carpet")
    st.set(7, 1, 3, "minecraft:campfire")
    # house B: cube-stepped gable of cobblestone on walls x 12..18, z 2..8
    for y in range(1, 5):
        for x in range(12, 19):
            for z in (2, 8):
                st.set(x, y, z, "minecraft:cobblestone")
    for k in range(4):
        for x in range(12, 19):
            st.set(x, 5 + k, 2 + k, "minecraft:cobblestone"); st.set(x, 4 + k, 2 + k, "minecraft:cobblestone")
    # house C: half-step slab roof (spruce slabs / planks alternating) on posts x 2..6, z 14..20
    for y in range(1, 5):
        for (x, z) in ((2, 14), (6, 14), (2, 20), (6, 20)):
            st.set(x, y, z, "minecraft:spruce_log")
    for k in range(6):
        y = 5 + k // 2
        for x in range(2, 7):
            if k % 2 == 0:
                st.set(x, y, 14 + k, "minecraft:spruce_slab", {"minecraft:vertical_half": M.s("bottom")})
            else:
                st.set(x, y, 14 + k, "minecraft:spruce_planks")
                if y > 5:
                    pass
    # a seated stair (on a bottom slab), a walk ramp (smooth stone slab half step), a vanilla-leaf tree, an unknown id
    st.set(12, 1, 14, "minecraft:stone_brick_slab", {"minecraft:vertical_half": M.s("bottom")})
    st.set(12, 2, 14, "minecraft:stone_brick_stairs", S(weirdo_direction=0, upside_down_bit=0))
    st.set(16, 1, 14, "minecraft:smooth_stone_slab", {"minecraft:vertical_half": M.s("bottom")})
    st.set(17, 1, 14, "minecraft:smooth_stone")
    st.set(16, 0, 14, "minecraft:smooth_stone")
    st.set(15, 0, 14, "minecraft:smooth_stone")
    for y in range(1, 4):
        st.set(20, y, 20, "minecraft:oak_log")
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            st.set(20 + dx, 4, 20 + dz, "minecraft:oak_leaves")
    st.set(22, 1, 22, "pw:not_a_block")
    g = Grid(st)
    rep = audit_structure("selftest", "buildings", g, Ctx(g), reg, van, {}, seated_ids, ramp_ids, wall_inner)
    kinds = collections.Counter(f["kind"] for f in rep["findings"])
    want = ["STEPPED-STAIR-ROOF", "STEPPED-BLOCK-ROOF", "STEPPED-SLAB-ROOF", "SEATED", "RAMP", "CHAIR", "TABLE", "HEARTH",
            "DECOR-TREE", "UNKNOWN"]
    ok = True
    for w in want:
        print(f"  {'PASS' if kinds.get(w) else 'FAIL'} {w}: {kinds.get(w, 0)}")
        ok &= bool(kinds.get(w))
    interior = [f for f in rep["findings"] if f["kind"] == "STEPPED-STAIR-ROOF" and f["id"] == "minecraft:spruce_stairs"]
    print(f"  {'PASS' if not interior else 'FAIL'} interior flight not called a roof ({len(interior)})")
    ok &= not interior
    return ok


# ------------------------------------------------------------------ main
def newest_markers_blocks():
    c = sorted((HOME / "_build").glob("markers-*-bp/blocks"))
    return [c[-1]] if c else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default=str(HOME / "_build/bp02-227"))
    ap.add_argument("--extra-blocks", nargs="*", default=None)
    ap.add_argument("--root", nargs="*", default=None, help="folders of .mcstructure files (default <pack>/structures)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--scripts", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    pack = Path(a.pack)
    extra = [Path(p) for p in (a.extra_blocks if a.extra_blocks is not None else newest_markers_blocks())]
    reg = load_blocks([("pack", pack / "blocks")] + [(p.parent.name, p) for p in extra])
    van = Vanilla()
    seated_ids = {i for i in reg if i.startswith("pw:seated_")}
    FLOWERS_SEATABLE_BASES.update(i[len("pw:seated_"):] for i in seated_ids if not i.endswith("_stairs"))
    ramp_ids = {i for i in reg if i.startswith("pw:ramp_")}
    wall_inner = {i: set(v[1].get("pw:inner", [])) for i, v in reg.items() if i.startswith("pw:wall_")}
    if a.selftest:
        return 0 if selftest(reg, van, seated_ids, ramp_ids, wall_inner) else 1
    roots = [Path(r) for r in (a.root or [pack / "structures"])]
    files = []
    for r in roots:
        files += [(r, f) for f in sorted(r.rglob("*.mcstructure"))]
    # stage groups: <stem>_s<k>  (composite = s0..s4 in order; `_s0_full` is a record copy, audited on its own)
    groups = collections.defaultdict(dict)
    for r, f in files:
        m = re.match(r"(.+)_s(\d)$", f.stem)
        if m:
            groups[(f.parent, m.group(1))][int(m.group(2))] = f
    cache, reports = {}, []
    loaded = {}
    def load(f):
        if f not in loaded:
            loaded.clear() if len(loaded) > 12 else None
            loaded[f] = M.Structure.from_bytes(f.read_bytes())
        return loaded[f]
    comp_cache = {}
    for r, f in files:
        rel = str(f.relative_to(r.parent if r.name == "structures" else r))
        st = load(f)
        own = Grid(st)
        m = re.match(r"(.+)_s(\d)$", f.stem)
        if m and (f.parent, m.group(1)) in groups:
            key = (f.parent, m.group(1))
            if key not in comp_cache:
                comp_cache.clear()
                sts = [M.Structure.from_bytes(groups[key][k].read_bytes()) for k in sorted(groups[key])]
                comp_cache[key] = Ctx(Grid.composite(sts))
            ctx = comp_cache[key]
        else:
            ctx = Ctx(own)
        rep = audit_structure(rel, family_of(rel), own, ctx, reg, van, cache, seated_ids, ramp_ids, wall_inner)
        reports.append(rep)
        if not a.quiet and rep["findings"]:
            kinds = collections.Counter(x["kind"] for x in rep["findings"])
            print(f"{rel}: {dict(kinds)}")
    out = {"pack": str(pack), "extra_blocks": [str(p) for p in extra], "roots": [str(r) for r in roots],
           "vanilla_source": {"blocks_json": str(VANILLA_BLOCKS_JSON), "bds_binary": str(BDS_BINARY),
                              "ids_found_only_in_bds_binary": {k: v for k, v in van.extra.items() if v}},
           "id_classes": cache, "structures": reports}
    if a.scripts:
        rt, tab = audit_scripts(pack / "scripts")
        out["runtime"] = rt
        out["civ_buildings_dir_table"] = tab
    # summary
    fam = collections.defaultdict(lambda: {"files": 0, "cells": collections.Counter(), "findings": collections.Counter(),
                                           "files_with_findings": 0})
    for rep in reports:
        s = fam[rep["family"]]
        s["files"] += 1
        s["cells"].update(rep["counts"])
        fk = collections.Counter()
        for x in rep["findings"]:
            fk[x["kind"]] += x.get("count", 1)
        s["findings"].update(fk)
        s["files_with_findings"] += bool(rep["findings"])
    for rep in reports:
        fam[rep["family"]].setdefault("opps", collections.Counter()).update(rep["opportunities"])
    out["summary"] = {k: {"files": v["files"], "files_with_findings": v["files_with_findings"], "cells": dict(v["cells"]),
                          "findings": dict(v["findings"]), "opportunities": dict(v.get("opps", {}))}
                      for k, v in sorted(fam.items())}
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(out, indent=1, default=str))
    print("\nFAMILY SUMMARY")
    for k, v in out["summary"].items():
        print(f"  {k:16s} files {v['files']:4d}  with findings {v['files_with_findings']:4d}  cells {v['cells']}  findings {v['findings']}")
    if a.scripts:
        print(f"\nRUNTIME placements of covered vanilla ids: {len(out['runtime'])}")
        for x in out["runtime"]:
            print(f"  {x['file']}:{x['line']}  {x['id']}  | {x['code'][:140]}")
    bad = sum(sum(v["findings"].values()) for v in out["summary"].values())
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
