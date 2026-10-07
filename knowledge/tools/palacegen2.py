#!/usr/bin/env python3
"""palacegen2.py — PALACE II (his 2026-10-06 rulings): the CIVITAS city palace as ONE 256 x 256 model cut into SIXTEEN
64 x 64 pieces (4 x 4), each a plot with the usual five build stages. Successor of tools/palacegen.py (left untouched);
it reuses that module's Palace primitives (doors, beds, jib panels, secret paintings, vaults, roofs, spiral2) and
spiral_site's solver/layer for every spiral stair. Design brief: _docs/palace/PALACE-II-RESEARCH-2026-10-06.md.

HIS DECISIONS (10-06): footprint 4 x 4 pieces; secret stairs = the NARROW spiral A; a royal nursery for 4 children on the
model of Prince Edward's 1537 lodgings at Hampton Court (watching chamber, presence chamber, night nursery, rocking/day
nursery, nurses' lodging, washing chamber + jakes; the governess on the same floor; the schoolroom in the attic); every
noble family a children's room (2 beds) + a nurse's closet; the hidden passages and escape tunnels serve the lord, the
family, the guards and the servants (never ordinary townsfolk) and are player-discovery content; every hidden element
names the real feature it imitates (myths are not built); ALL structures drain to sewers ~12 below the street and the
court's water runs through a fountain and a cascade into the sewers; two basements (cellars ~ -7, tunnels ~ -12).

FRAME (civgen, as palacegen): x = depth from the street (x 0 = the gate range's street face), z = frontage 0..255,
feet = height over the court (0 = standing on the paving; the ground floor course is feet -1). The box runs feet -15..34.
LEVELS: B2 tunnels/sewers walk -12 (clear -12..-9, floor course -13, the gutter: water at -14 under iron bars at -13);
B1 cellars walk -7 (clear -7..-2, floor course -8); ground 0..4, slab 5; étage noble 6..13 (the cabinet zone's
ENTRESOL: lower 6..9, slab 10, upper 11..13), slab 14; attic 15..18; eaves 19.
MASSING (x ranges): gate range 0..11 (gatehouse z 114..141) · court of honour 12..119 (z 40..215, the fountain + cascade
grotto at its centre) between the WEST WING (government, z 16..39) and the EAST WING (16 noble families' ranges,
z 216..239) · CORPS DE LOGIS 120..159 (z 16..239): court wall 120 | state rooms 121..132 | jib partition 133 | HIDDEN
SPINE 134..135 | wall 136 | cabinet zone 137..144 | stoking wall 145..147 (passage 146) | garden range 148..156 | rear
wall 157..159 (3 thick: the stair in the wall) · ALLEY 160..162 · CANAL 163..170 (water feet -3..-1) · REAR 171..255:
prison tower (NW), privy garden (ice house, the escape pavilion), service court (kitchen, little commons, laundry,
smithy, stables + coach house).
PIECES: mvv_palace2_<r><c>_a_r1, r = x // 64 (0 = the gate side), c = z // 64 (0 = z 0..63): 00 .. 33.
Outputs: _staging/civ/palace2/{structures,stages,manifests}/ + palace2_group.json.
Usage: palacegen2.py [--write]   (the verification and the renders: tools/palace2_check.py)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import civgen as G  # noqa: E402
import mcstructure as M  # noqa: E402
import palacegen as PG  # noqa: E402

OUT = Path("/home/claude/_staging/civ/palace2")
N, PIECE, TOP = 256, 64, 34

STONE, SMOOTH, CHISEL, COBBLE = PG.STONE, PG.SMOOTH, PG.CHISEL, PG.COBBLE
PANEL, FLOOR, ATTIC_FLOOR, STATE_FLOOR = PG.PANEL, PG.FLOOR, PG.ATTIC_FLOOR, PG.STATE_FLOOR
POST, GLASS, LIGHT, AIR, VOID = PG.POST, PG.GLASS, PG.LIGHT, PG.AIR, PG.VOID
GRASS, GRAVEL, DIRT, WATER = PG.GRASS, PG.GRAVEL, PG.DIRT, PG.WATER
JIB, PAINTING = PG.JIB_PANEL, PG.SECRET_PAINTING
BARS, IRON_DOOR = "minecraft:iron_bars", "minecraft:iron_door"
BRICK = "minecraft:stone_bricks"            # every basement shell (a GROUND block: civ_stages puts it in the plot stage)
F_B2, F_B1 = -12, -7
F_GROUND, F_SLAB1, F_NOBLE, F_ENT_SLAB, F_ENT, F_SLAB2, F_ATTIC, F_EAVE = 0, 5, 6, 10, 11, 14, 15, 19

# ---------------------------------------------------------------------------------------------------- the plan (x, z)
GATE = (0, 11); GATE_Z = (24, 231); GH_Z = (114, 141); ARCH_Z = (126, 129)
COURT = (12, 119); COURT_Z = (40, 215)
WW, EW = (16, 39), (216, 239)                 # wing z ranges (west = government, east = noble families)
CORPS = (120, 159); CZ = (16, 239)            # the corps incl. the chapel bay (z 216..239)
GOV = (17, 40)                                 # the government bay at the corps' west end (full depth)
CHAPEL = (216, 239)
XS, XP, XC, XW, XK, XST, XG, XR = (121, 132), 133, (134, 135), 136, (137, 144), (145, 147), (148, 156), (157, 159)
ALLEY, CANAL, REAR = (160, 162), (163, 170), (171, 255)
TOWER = (171, 186, 17, 32)
SPINE_L, SPINE_C = (42, 126), (136, 214)      # the hidden spine's two runs (the cross salon z 128..134 between)


class Palace2(PG.Palace):
    """the 256 x 256 model (z 0 is an ordinary column here)"""

    def __init__(self):
        G.Building.__init__(self, "pw:mvv_palace2", N, N - 1, top_feet=TOP)
        self.lights = 0
        self.beds = 0
        self.child_bed_clash = []
        self.bed_roles = []
        self.notes = []
        self.rooms = []          # {name, level, box: [x0, x1, z0, z1], f, imitates, hidden}
        self.secrets = []        # the hidden network: {id, element, precedent, how, public, hidden, mode}
        self.hidden = []         # boxes of the hidden network (renders): {label, box: [x0, x1, z0, z1, f0, f1]}
        self.spirals = []
        self.later = []
        self.oneway = []         # iron doors: {cells: [(x, f, z) x2], open_from: [(x, f, z)]}
        self.drains = []         # {building, gully: [x, z], sewer}
        self.below = []          # basement spaces to dig: {level, box, clear, gutter, kind}
        self.keep = set()        # exit cells of spirals already laid (a later ring never closes them)

    # ---------------------------------------------------------------- fast fill (one palette lookup per call)
    def fill(self, x0, f0, z0, x1, f1, z1, name, **states):
        xa, xb = sorted((x0, x1)); fa, fb = sorted((f0, f1)); za, zb = sorted((z0, z1))
        sx, sy, sz = self.size
        assert 0 <= xa and xb < sx and 0 <= za and zb < sz and self.bottom <= fa and fb <= self.bottom + sy - 1, (x0, f0, z0, x1, f1, z1, name)
        st = self.st
        k = st._pal(name, G._typed(states))
        n = zb - za + 1
        row, neg = [k] * n, [-1] * n
        L0, L1 = st.layer0, st.layer1
        for x in range(xa, xb + 1):
            for f in range(fa, fb + 1):
                base = (x * sy + (f - self.bottom)) * sz
                L0[base + za: base + zb + 1] = row
                L1[base + za: base + zb + 1] = neg

    def close_air(self):
        k = self.st._pal(AIR, {})
        self.st.layer0 = [k if v < 0 else v for v in self.st.layer0]

    def free(self, x, f, z):
        n = self.get(x, f, z)
        return n in (None, AIR, LIGHT)

    # ---------------------------------------------------------------- registries
    def room(self, name, level, x0, x1, z0, z1, f, imitates="", zone=None, hidden=False):
        self.rooms.append({"name": name, "level": level, "box": [x0, x1, z0, z1], "f": f, "imitates": imitates, "hidden": hidden})
        if zone and x1 > x0 and z1 > z0:
            self.zone(zone, x0, f, z0, x1, z1)

    def hide(self, label, x0, x1, z0, z1, f0, f1):
        self.hidden.append({"label": label, "box": [min(x0, x1), max(x0, x1), min(z0, z1), max(z0, z1), f0, f1]})

    def secret(self, sid, element, precedent, how, public, hidden, mode="hidden"):
        """mode: hidden = the hidden side must NOT be reachable from the gate with every secret block shut;
        disguised = a secret door into a service space that servants reach by ordinary doors too;
        oneway = an iron door that opens from its inner side only; lore = no way through"""
        self.secrets.append({"id": sid, "element": element, "precedent": precedent, "how": how,
                             "public": list(public) if public else None, "hidden": list(hidden) if hidden else None, "mode": mode})

    def jib2(self, x, f, z):
        self.put(x, f, z, JIB)
        self.put(x, f + 1, z, JIB)

    def iron_gate(self, x, f, z, facing, inside):
        """an iron door that opens from `inside` only (a stone button there, at head height); records the one-way pair"""
        self.door(x, f, z, facing, mat=IRON_DOOR)
        ix, iz = inside
        self.put(ix, f + 1, iz, "minecraft:stone_button", facing_direction=1, button_pressed_bit=False)
        self.oneway.append({"cells": [[x, f, z], [x, f + 1, z]], "open_from": [[ix, f, iz]]})

    def lights_in(self, x0, x1, z0, z1, f, every=6):
        for x in range(x0 + 1, x1, every):
            for z in range(z0 + 1, z1, every):
                if self.free(x, f, z):
                    self.put(x, f, z, LIGHT)
                    self.lights += 1

    def dig(self, level, x0, x1, z0, z1, f0, f1, gutter=None, kind="tunnel", label=""):
        """register a basement space (dug in build_below: shells first, then every interior, then gutters)"""
        self.below.append({"level": level, "box": (x0, x1, z0, z1, f0, f1), "gutter": gutter, "kind": kind, "label": label})

    def spiral3(self, x0, z0, f0, floors, design, pal, ceiling, label, door_ok=None, want=None, ring=STONE, ring_lo=None,
                ring_hi=None, secret_exits=(), door_blocks=()):
        """palacegen.spiral2 (solve + lay with spiral_site) + an ENCLOSURE: the ring of cells round the well is walled with
        `ring` from ring_lo to ring_hi wherever it is free, except the exits (the foot, every door beside a step, the floor
        in front at the top). secret_exits: exits (floor levels; 'foot' / 'top') closed by pw:jib_panel (walk-through);
        door_blocks: exits given a real spruce door."""
        P = self.spiral2(x0, z0, f0, floors, design, pal, ceiling=ceiling, door_ok=door_ok, label=label, want=want)
        sp = self.spirals[-1]
        wx0, wz0, wx1, wz1 = P["well"]
        top = P["top"]
        lo = f0 if ring_lo is None else ring_lo
        hi = (ceiling - 1) if ring_hi is None else ring_hi
        exits = {}                                                    # (x, z) -> (feet, tag)
        for d in P["doors"]:
            exits[tuple(d["cell"])] = (d["feet"], d["feet"])
        for (x, f, z) in P["landing"]:
            if not (wx0 <= x <= wx1 and wz0 <= z <= wz1):
                exits[(x, z)] = (top, "top")
        foot = [(x, z) for (x, f, z, _s) in P["cells"] if f == f0]
        for (x, z) in foot:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c = (x + dx, z + dz)
                if not (wx0 <= c[0] <= wx1 and wz0 <= c[1] <= wz1):
                    exits.setdefault(c, (f0, "foot"))
        # a landing that is only the quarter inside the well steps off sideways: keep the ring open beside it at the top
        if P.get("landing_mode") == "quarter":
            inq = [(x, z) for (x, f, z) in P["landing"]]
            for (x, z) in inq:
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    c = (x + dx, z + dz)
                    if not (wx0 <= c[0] <= wx1 and wz0 <= c[1] <= wz1) and self.free(c[0], top, c[1]) and not self.free(c[0], top - 1, c[1]):
                        exits.setdefault(c, (top, "top"))
        ringcells = [(x, z) for x in range(wx0 - 1, wx1 + 2) for z in range(wz0 - 1, wz1 + 2)
                     if not (wx0 <= x <= wx1 and wz0 <= z <= wz1)]
        for (x, z) in ringcells:
            ex = exits.get((x, z))
            for f in range(lo, hi + 1):
                if ex and ex[0] <= f <= ex[0] + 2:
                    continue
                if (x, f, z) in self.keep:
                    continue
                if self.free(x, f, z):
                    self.put(x, f, z, ring)
        for (x, z), (fe, tag) in exits.items():
            if tag in secret_exits or fe in secret_exits:
                if self.free(x, fe, z) and self.free(x, fe + 1, z):
                    self.jib2(x, fe, z)
                    if self.free(x, fe + 2, z):
                        self.put(x, fe + 2, z, ring)
            elif tag in door_blocks or fe in door_blocks:
                facing = "east" if x > wx1 else "west" if x < wx0 else "south" if z > wz1 else "north"
                if self.free(x, fe, z) and self.free(x, fe + 1, z):
                    self.door(x, fe, z, facing)
        sp["exits"] = [[x, fe, z, str(tag)] for (x, z), (fe, tag) in exits.items()]
        for (x, z), (fe, tag) in exits.items():
            for ff in range(fe - 1, fe + 3):
                self.keep.add((x, ff, z))
        return P


# ==================================================================================================== ground + below grade
def ground(p):
    p.fill(0, -15, 0, N - 1, -2, N - 1, DIRT)
    p.fill(0, -1, 0, N - 1, -1, N - 1, GRASS)
    # the court of honour: gravel field, stone avenues (gate -> corps door, and a cross walk), four lawns; the raised
    # MARBLE COURT before the lord's state bedchamber (Versailles: the Cour de Marbre is centred on the King's chamber)
    p.fill(COURT[0], -1, COURT_Z[0], COURT[1], -1, COURT_Z[1], GRAVEL)
    p.fill(COURT[0], -1, 124, COURT[1], -1, 131, STONE)
    p.fill(COURT[0], -1, 40, COURT[1], -1, 215, GRAVEL)
    p.fill(COURT[0], -1, 124, COURT[1], -1, 131, STONE)
    p.fill(60, -1, COURT_Z[0], 63, -1, COURT_Z[1], STONE)
    for (xa, xb, za, zb) in ((20, 54, 50, 116), (20, 54, 139, 205), (86, 104, 50, 116), (86, 104, 139, 205)):
        p.fill(xa, -1, za, xb, -1, zb, GRASS)
    p.fill(105, -1, 66, 119, -1, 83, "minecraft:polished_diorite")       # the marble court (in front of z 70..79)
    p.fill(105, 0, 66, 105, 0, 83, "minecraft:polished_diorite_slab", **{"minecraft:vertical_half": "bottom"})
    p.put(105, 0, 74, AIR); p.put(105, 0, 75, AIR)
    # the alley (cobbles) and the rear zone
    p.fill(ALLEY[0], -1, 16, ALLEY[1], -1, 239, COBBLE)
    p.fill(REAR[0], -1, 128, REAR[1] - 4, -1, 239, GRAVEL)             # the service court
    p.fill(REAR[0], -1, 33, REAR[1] - 4, -1, 127, GRASS)               # the privy garden
    for zz in range(44, 124, 16):
        p.fill(REAR[0] + 4, -1, zz, REAR[1] - 8, -1, zz + 1, GRAVEL)   # garden walks
    p.fill(200, -1, 33, 201, -1, 127, GRAVEL)
    p.fill(0, -1, 0, N - 1, -1, 15, GRASS)                             # the lanes round the block (lawn)
    p.fill(0, -1, 240, N - 1, -1, N - 1, GRASS)


def canal(p):
    """the 'Rio di Palazzo' (Doge's Palace: the palace wall rises from the canal; the Bridge of Sighs crosses it): water at
    feet -3..-1 between stone walls, floor -4, both ends closed. ALL palace water lies below feet 0 (the clock's pumps drain
    everything at feet >= 0 inside a palace piece)."""
    x0, x1 = CANAL
    p.fill(x0 - 1, -5, 15, x1 + 1, -1, 240, STONE)
    p.fill(x0, -3, 16, x1, -1, 239, WATER)
    p.fill(ALLEY[0], -1, 16, ALLEY[1], -1, 239, COBBLE)
    p.fill(x0 - 1, -1, 16, x0 - 1, -1, 239, SMOOTH)                    # the quay edges
    p.fill(x1 + 1, -1, 16, x1 + 1, -1, 239, SMOOTH)
    # bridges at ground level (decks at feet 0 over the water; a one-block step up from the quays)
    for (za, zb, name) in ((88, 91, "garden bridge"), (200, 203, "service bridge")):
        p.fill(x0 - 1, 0, za, x1 + 1, 0, zb, "minecraft:spruce_planks")
        p.fill(x0 - 1, 1, za - 1, x1 + 1, 1, za - 1, "minecraft:spruce_fence")
        p.fill(x0 - 1, 1, zb + 1, x1 + 1, 1, zb + 1, "minecraft:spruce_fence")
        p.fill(x0 - 1, 0, za - 1, x1 + 1, 0, za - 1, "minecraft:spruce_planks")
        p.fill(x0 - 1, 0, zb + 1, x1 + 1, 0, zb + 1, "minecraft:spruce_planks")
        p.notes.append(f"canal: {name} z {za}..{zb}")
    # U6 (no source for a palace-to-stables tunnel): the service bridge carries a covered passage at ground level
    PG.roof_lean(p, x0 - 1, x1 + 1, 199, 199, 4, downhill="north", wood="spruce")
    PG.roof_lean(p, x0 - 1, x1 + 1, 204, 204, 4, downhill="south", wood="spruce")
    for xx in range(x0 - 1, x1 + 2, 3):
        p.column(xx, 199, 1, 3); p.column(xx, 204, 1, 3)
    p.fill(x0 - 1, 5, 199, x1 + 1, 5, 204, "minecraft:spruce_slab", **{"minecraft:vertical_half": "bottom"})


def build_below(p):
    """dig every registered basement space: (1) shells of stone bricks where the ground is still dirt (floor course, walls,
    ceiling course; under a gutter also the two courses below), (2) every interior air, (3) gutters: water at -14 under
    iron bars at -13, (4) lights at head height every 6"""
    for s in p.below:
        x0, x1, z0, z1, f0, f1 = s["box"]
        lo = f0 - 1 if not s["gutter"] else -15
        for x in range(x0 - 1, x1 + 2):
            for f in range(lo, f1 + 2):
                for z in range(z0 - 1, z1 + 2):
                    if p.get(x, f, z) in (DIRT, None):
                        p.put(x, f, z, BRICK)
    for s in p.below:
        x0, x1, z0, z1, f0, f1 = s["box"]
        p.fill(x0, f0, z0, x1, f1, z1, AIR)
    for s in p.below:
        x0, x1, z0, z1, f0, f1 = s["box"]
        if s["gutter"] == "x":
            zm = (z0 + z1) // 2
            p.fill(x0, -14, zm, x1, -14, zm, WATER); p.fill(x0, -13, zm, x1, -13, zm, BARS)
        elif s["gutter"] == "z":
            xm = (x0 + x1) // 2
            p.fill(xm, -14, z0, xm, -14, z1, WATER); p.fill(xm, -13, z0, xm, -13, z1, BARS)
    for s in p.below:
        x0, x1, z0, z1, f0, f1 = s["box"]
        for x in range(x0, x1 + 1, 6):
            for z in range(z0, z1 + 1, 6):
                if p.free(x, f0 + 1, z) and p.get(x, f0 - 1, z) not in (AIR, None):
                    p.put(x, f0 + 1, z, LIGHT); p.lights += 1


def plan_below(p):
    """the two basements. B2 (walk -12): the SEWERS (3 wide, a grated gutter on the centre line) under the court's four
    sides + the TRUNK across the court to the street outfall + the REAR sewer under the alley + the service sewers;
    the JUNCTION J1 under the court centre (Dover Castle: three passages meet under the redan); the corps link; the
    tower tunnel (to the prison tower under the canal); J2 under the corps' rear (the escape junction); the ESCAPE TUNNEL
    under the canal and the privy garden to the garden pavilion. B1 (walk -7): cellars, the Pozzi, the crypt, the serving
    room, the service tunnel under the canal, the cascade grotto."""
    # ---- B2 sewers (gutter) and tunnels
    p.dig("B2", 1, 117, 126, 128, -12, -9, gutter="x", kind="sewer", label="trunk sewer")
    p.dig("B2", 13, 15, 40, 215, -12, -9, gutter="z", kind="sewer", label="gate sewer")
    p.dig("B2", 13, 117, 41, 43, -12, -9, gutter="x", kind="sewer", label="west sewer")
    p.dig("B2", 13, 117, 212, 214, -12, -9, gutter="x", kind="sewer", label="east sewer")
    p.dig("B2", 115, 117, 41, 214, -12, -9, gutter="z", kind="sewer", label="corps sewer")
    p.dig("B2", ALLEY[0], ALLEY[1], 17, 238, -12, -9, gutter="z", kind="sewer", label="rear sewer")
    p.dig("B2", 163, 238, 145, 147, -12, -9, gutter="x", kind="sewer", label="service sewer (kitchen)")
    p.dig("B2", 163, 238, 215, 217, -12, -9, gutter="x", kind="sewer", label="service sewer (laundry, smithy, stables)")
    p.dig("B2", 236, 238, 148, 214, -12, -9, gutter="z", kind="sewer", label="service sewer (little commons)")
    p.dig("B2", 60, 79, 120, 135, -12, -9, kind="tunnel", label="J1 junction")
    p.dig("B2", 64, 66, 44, 119, -12, -9, kind="tunnel", label="U4 north passage")
    p.dig("B2", 118, 159, 126, 128, -12, -9, kind="tunnel", label="corps link")
    p.dig("B2", 118, 176, 41, 43, -12, -9, kind="tunnel", label="tower tunnel")
    p.dig("B2", 174, 176, 31, 40, -12, -9, kind="tunnel", label="tower tunnel (north)")
    p.dig("B2", 173, 184, 19, 30, -12, -9, kind="tunnel", label="prison tower vault")
    p.dig("B2", 150, 159, 70, 81, -12, -9, kind="tunnel", label="J2 escape junction")
    p.dig("B2", 143, 149, 73, 75, -12, -9, kind="tunnel", label="garderobe-shaft foot")
    p.dig("B2", 163, 239, 74, 76, -12, -9, kind="tunnel", label="escape tunnel")
    p.dig("B2", 1, 6, 129, 141, -12, -9, kind="tunnel", label="gatehouse tunnel")
    # ---- B1 cellars (walk -7)
    p.dig("B1", 134, 136, 42, 214, -7, -2, kind="cellar", label="corps cellar corridor")
    p.dig("B1", 121, 132, 44, 49, -7, -2, kind="cellar", label="wine cellar")
    p.dig("B1", 121, 132, 51, 56, -7, -2, kind="cellar", label="cellar passage")
    p.dig("B1", 121, 128, 58, 65, -7, -2, kind="cellar", label="lower exchequer")
    p.dig("B1", 121, 132, 136, 160, -7, -2, kind="cellar", label="consort cellars")
    p.dig("B1", 137, 158, 44, 46, -7, -2, kind="cellar", label="wall-stair foot passage")
    p.dig("B1", 148, 156, 100, 109, -7, -2, kind="cellar", label="serving room")
    p.dig("B1", 137, 147, 104, 106, -7, -2, kind="cellar", label="serving passage")
    p.dig("B1", 157, 182, 104, 106, -7, -5, kind="cellar", label="service tunnel (U5)")
    p.dig("B1", 180, 182, 107, 130, -7, -5, kind="cellar", label="service tunnel (U5) south")
    p.dig("B1", 176, 190, 131, 141, -7, -2, kind="cellar", label="kitchen cellar")
    p.dig("B1", 121, 158, 217, 238, -7, -2, kind="cellar", label="crypt")
    p.dig("B1", 134, 136, 215, 216, -7, -2, kind="cellar", label="crypt passage")
    p.dig("B1", 121, 156, 18, 39, -7, -2, kind="cellar", label="pozzi")
    p.dig("B1", 13, 111, 27, 28, -7, -2, kind="cellar", label="west wing cellar corridor")
    p.dig("B1", 13, 111, 29, 38, -7, -2, kind="cellar", label="west wing cellars")
    p.dig("B1", 112, 118, 17, 38, -7, -2, kind="cellar", label="west wing stair cellar")
    p.dig("B1", 13, 111, 227, 228, -7, -2, kind="cellar", label="east wing cellar corridor")
    p.dig("B1", 13, 111, 217, 226, -7, -2, kind="cellar", label="east wing cellars")
    p.dig("B1", 112, 118, 217, 238, -7, -2, kind="cellar", label="east wing stair cellar")
    p.dig("B1", 58, 79, 116, 139, -7, -3, kind="grotto", label="cascade grotto")


def fit_below(p):
    """after the dig: partitions, doors, gates, the Pozzi, the cascade, the outfall, rooms"""
    # ---- the trunk's OUTFALL at the street (the cottage's sewer port: air at feet -10 / -9 in the front cell, a port marker)
    p.put(0, -10, 127, AIR); p.put(0, -9, 127, AIR)
    p.marker("port", "sewer", 0, -10, 127)
    for (x0, x1, z0, z1, f, name, imit, hid) in (
            (1, 117, 126, 128, -12, "trunk sewer", "Hampton Court: brick culverts to the Thames", True),
            (13, 15, 40, 215, -12, "gate sewer", "Hampton Court culverts", True),
            (13, 117, 41, 43, -12, "west sewer", "Hampton Court culverts", True),
            (13, 117, 212, 214, -12, "east sewer", "Hampton Court culverts", True),
            (115, 117, 41, 214, -12, "corps sewer", "Hampton Court culverts", True),
            (160, 162, 17, 238, -12, "rear sewer", "Baddesley Clinton: sewers 'run the length of the building'", True),
            (163, 238, 145, 147, -12, "kitchen sewer", "Kerr: service drains", True),
            (163, 238, 215, 217, -12, "yard sewer", "Kerr: service drains", True),
            (236, 238, 148, 214, -12, "commons sewer", "Kerr: service drains", True),
            (60, 79, 120, 135, -12, "J1 junction", "Dover Castle: three passages meet in a junction under the redan", True),
            (150, 159, 70, 81, -12, "J2 escape junction", "Baddesley Clinton sewer hide (6-7 people)", True),
            (163, 239, 74, 76, -12, "escape tunnel (U1)", "Kremlin Tainitskaya: hidden exit to the river [composite]", True),
            (173, 184, 19, 30, -12, "prison tower vault", "Dover Castle tower passages", True)):
        p.room(name, "B2", x0, x1, z0, z1, f, imit, hidden=hid)
        p.hide(name, x0, x1, z0, z1, f, f + 3)
    for (x0, x1, z0, z1, label) in ((64, 66, 44, 119, "U4 north passage"), (118, 159, 126, 128, "corps link"),
                                    (118, 176, 41, 43, "tower tunnel"), (174, 176, 31, 40, "tower tunnel"),
                                    (143, 149, 73, 75, "garderobe-shaft foot"), (1, 6, 129, 141, "gatehouse tunnel")):
        p.hide(label, x0, x1, z0, z1, -12, -9)
    # ---- ESCAPE TUNNEL (U1): an iron door at its palace end opens from the junction side only; its far end climbs a ladder
    # shaft into the GARDEN PAVILION (a trapdoor in the floor) outside the palace walls
    p.fill(163, -12, 74, 163, -9, 76, BRICK)
    p.iron_gate(163, -12, 75, "east", inside=(162, 75))
    p.secret("U1", "Escape tunnel (B2) to the garden pavilion", "Kremlin Tainitskaya Tower: 'a hidden exit to the Moskva River'; Passetto di Borgo (escape route) [the long tunnel is a composite]",
             "from J2 under the corps through an iron door (button on the palace side only); out by a ladder and a trapdoor in the pavilion floor",
             (162, -12, 75), (164, -12, 75), "oneway")
    # the ladder shaft at the far end (x 239, z 75) up to the pavilion floor
    for f in range(-12, 0):
        p.put(239, f, 75, "minecraft:ladder", facing_direction=4)     # against the wall at x 240
    p.fill(240, -12, 74, 240, -1, 76, BRICK)
    p.fill(238, -8, 74, 238, -2, 76, BRICK); p.fill(239, -8, 74, 239, -2, 74, BRICK); p.fill(239, -8, 76, 239, -2, 76, BRICK)
    p.put(239, 0, 75, "minecraft:spruce_trapdoor", direction=0, open_bit=False, upside_down_bit=False)
    # ---- J2: the H12 garderobe shaft arrives at x 144 z 73 (the foot passage x 143..149) ----
    # ---- the gatehouse tunnel stair foot area and the J1 / U4 passages are open spaces (dug)
    # ---- POZZI (B1, the corps' government bay): 4 cells of 3 x 3 behind iron bars, iron doors; the guard walk between
    x0, x1 = 121, 156
    p.fill(x0, -7, 18, x1, -2, 25, BRICK); p.fill(x0, -7, 32, x1, -2, 39, BRICK)
    p.fill(150, -7, 32, 155, -2, 36, AIR)                               # the narrow stair's foot room
    for (cx, cz, side) in ((124, 22, "n"), (130, 22, "n"), (124, 33, "s"), (130, 33, "s")):
        p.fill(cx, -7, cz, cx + 2, -5, cz + 2, AIR)
        fz = cz + 3 if side == "n" else cz - 1
        p.fill(cx, -7, fz, cx + 2, -5, fz, BARS)
        p.put(cx + 1, -7, fz, AIR); p.put(cx + 1, -6, fz, AIR)
        p.door(cx + 1, -7, fz, "south" if side == "n" else "north", mat=IRON_DOOR)
        p.bed(cx, -7, cz + 1, "east", role="cell")
        p.put(cx + 2, -7, cz + (2 if side == "n" else 0), "minecraft:barrel", facing_direction=1, open_bit=False)   # the bucket
        p.room(f"pozzo cell {cx},{cz}", "B1", cx, cx + 2, cz, cz + 2, -7, "Doge's Palace, the Pozzi ('small wet cells… a wood litter… a bucket')", hidden=True)
    p.room("pozzi guard walk", "B1", x0, x1, 26, 31, -7, "Doge's Palace, the Pozzi", zone="cellar", hidden=True)
    p.hide("pozzi", x0, x1, 18, 39, -7, -2)
    p.fill(x0, -6, 26, x0, -6, 31, BRICK) if False else None
    # ---- corps cellars: partition walls + doors off the corridor (x 134..136)
    p.fill(133, -7, 44, 133, -2, 65, BRICK)
    p.door(133, -7, 47, "west"); p.door(133, -7, 53, "west"); p.door(133, -7, 61, "west")
    p.fill(129, -7, 58, 129, -2, 65, BRICK)
    p.fill(121, -7, 50, 132, -2, 50, BRICK); p.fill(121, -7, 57, 132, -2, 57, BRICK)
    p.fill(129, -7, 58, 132, -2, 65, BRICK)
    p.door(133, -7, 61, "west")
    p.fill(130, -7, 61, 132, -6, 61, AIR)
    p.put(129, -7, 61, AIR); p.put(129, -6, 61, AIR)
    p.iron_gate(129, -7, 61, "west", inside=(130, 61))
    for i in range(6):
        p.barrel(122 + i * 2, -7, 44); p.barrel(122 + i * 2, -7, 49)
        p.barrel(122 + i * 2, -6, 44)
    p.room("wine cellar", "B1", 121, 132, 44, 49, -7, "Whitehall Palace: Henry VIII's vaulted wine cellar", zone="cellar")
    PG.vault(p, 121, 132, 44, 49, -4, axis="x", wood="spruce", crown="beam", fill=BRICK, deck=BRICK, end_mat=BRICK, deck_lights=0)
    p.room("cellar passage", "B1", 121, 132, 51, 56, -7, "", zone="storeroom")
    for i in range(3):
        p.chest(122 + i, -7, 58, "south"); p.put(124, -7, 62, "minecraft:gold_block")
    p.room("lower exchequer strongroom", "B1", 121, 128, 58, 65, -7, "Exchequer (R3 §5.4): the Lower Exchequer strongroom", zone="storeroom")
    p.room("corps cellar corridor", "B1", 134, 136, 42, 214, -7, "Kerr: the basement service passage", zone="cellar")
    p.fill(133, -7, 136, 133, -2, 160, BRICK); p.door(133, -7, 148, "west")
    for i in range(10):
        p.barrel(122 + i, -7, 137); p.chest(122 + i, -7, 159, "north")
    p.room("consort's cellars", "B1", 121, 132, 136, 160, -7, "", zone="storeroom")
    # the wall-stair foot passage (z 44..46) from the corridor: an iron door (button on the stair side only)
    p.fill(137, -7, 44, 137, -2, 46, BRICK)
    p.iron_gate(137, -7, 45, "west", inside=(138, 45))
    p.room("wall-stair foot", "B1", 138, 158, 44, 46, -7, "Palazzo Vecchio: the Duke of Athens' stair", hidden=True)
    p.hide("wall-stair foot", 138, 158, 44, 46, -7, -2)
    # the serving room (flying table) + its passage to the corridor
    p.room("serving room", "B1", 148, 156, 100, 109, -7, "Petit Trianon: the 'flying table' service floor below the dining room", zone="kitchen")
    p.table(150, -7, 102); p.table(151, -7, 102); p.chest(155, -7, 101, "west"); p.barrel(155, -7, 108)
    p.room("serving passage", "B1", 137, 147, 104, 106, -7, "")
    p.room("service tunnel (U5)", "B1", 157, 182, 104, 106, -7, "Kerr: the dinner route 'must not cross the track of family traffic' [tunnel = design]")
    p.room("service tunnel (U5) south", "B1", 180, 182, 107, 130, -7, "Kerr's dinner route [tunnel = design]")
    # the crypt: B1 under the chapel (Hofburg: the Herzgruft under the palace church); urns on a shelf
    p.fill(134, -7, 215, 136, -2, 215, BRICK); p.fill(134, -7, 216, 136, -2, 216, BRICK)
    p.fill(135, -7, 215, 135, -6, 216, AIR)
    p.door(135, -7, 216, "south")
    for i in range(12):
        p.put(123 + i * 3, -7, 237, "minecraft:decorated_pot", direction=0)
    p.room("crypt", "B1", 121, 158, 217, 238, -7, "Hofburg Augustinian church: the Herzgruft ('the hearts of 54 members of the imperial family')", zone="cellar")
    PG.vault(p, 121, 158, 217, 238, -6, axis="x", wood="spruce", crown="beam", fill=BRICK, deck=BRICK, end_mat=BRICK, deck_lights=0) if False else None
    # wings' cellars: corridor walls + doors
    for (zc0, zc1, zr0, zr1, name) in ((27, 28, 29, 38, "west"), (227, 228, 217, 226, "east")):
        wz = zc1 + 1 if name == "west" else zc0 - 1
        p.fill(13, -7, wz, 111, -2, wz, BRICK)
        for xx in range(20, 110, 12):
            p.door(xx, -7, wz, "south" if name == "west" else "north")
            p.fill(xx + 6, -7, zr0, xx + 6, -2, zr1, BRICK)
            for i in range(3):
                p.barrel(xx - 3 + i, -7, zr1 if name == "west" else zr0)
        p.room(f"{name} wing cellar corridor", "B1", 13, 111, zc0, zc1, -7, "", zone="cellar")
        p.room(f"{name} wing cellars", "B1", 13, 111, zr0, zr1, -7, "", zone="storeroom")
    # the kitchen cellar
    p.room("kitchen cellar", "B1", 176, 190, 131, 141, -7, "", zone="storeroom")
    for i in range(6):
        p.barrel(177 + i * 2, -7, 141)
    # ---- the CASCADE GROTTO + the court fountain (see fountain())
    fountain(p)


def fountain(p):
    """the court fountain (basin water at feet -1) and its CASCADE: a chute from the basin into a water staircase of five
    pools stepping down 1 block each along the grotto's spine (x 68..77, z 127), lipped so every pool is still water, then a
    chute through the grotto floor and J1 into the trunk sewer's gutter (z 127 at -14). Public grotto stairs from the court
    (two flights). All water cells are walled by stone (plot-stage blocks), so nothing can run while the stages rise."""
    # the basin: x 62..69, z 124..131 (ring of stone, water 6 x 6 at -1 on a floor at -2)
    p.fill(62, -2, 124, 69, -1, 131, STONE)
    p.fill(63, -1, 125, 68, -1, 130, WATER)
    p.fill(62, 0, 124, 69, 0, 131, "minecraft:stone_brick_slab", **{"minecraft:vertical_half": "bottom"})
    p.fill(63, 0, 125, 68, 0, 130, AIR)
    p.put(65, 0, 127, "minecraft:chiseled_stone_bricks"); p.put(65, 1, 127, "minecraft:stone_brick_wall", wall_post_bit=True,
          wall_connection_type_east="none", wall_connection_type_west="none", wall_connection_type_north="none", wall_connection_type_south="none")
    p.put(65, 2, 127, "minecraft:lantern", hanging=False)
    # the grotto's WATER STAIRCASE x 67..78 on the centre line z 127: a plinth 3 wide (z 126..128) stepping down with the
    # pools; pool k (k = 0..4) = water at level -3-k in x 68+2k, 69+2k with stone rims at z 126 / 128 at that level and a LIP
    # (stone) at level -2-k in the first cell of pool k+1; everything above a pool is open (visible from the grotto)
    p.put(68, -2, 127, WATER)
    p.fill(67, -7, 126, 78, -7, 128, STONE)
    pools = []
    for k in range(5):
        lvl = -3 - k
        xa = 68 + 2 * k
        for xx in (xa, xa + 1):
            p.fill(xx, -7, 126, xx, lvl - 1, 128, STONE)              # the plinth under the pool
            p.put(xx, lvl, 126, STONE); p.put(xx, lvl, 128, STONE)     # rims
            p.put(xx, lvl, 127, WATER)
        if k > 0:
            p.put(xa, lvl + 1, 127, STONE)                            # the lip
        pools.append((xa, lvl))
    p.fill(67, -7, 126, 67, -3, 128, STONE)                           # the head block under the basin edge
    p.fill(78, -7, 126, 78, -6, 128, STONE)                           # the foot block
    # chute B: from pool 4 (x 77, level -7) down through the floor course, J1 and the gutter course into the gutter
    for f in range(-8, -14 - 1, -1):
        p.put(77, f, 127, WATER)
    p.fill(76, -12, 126, 78, -9, 128, STONE)       # the pier round chute B inside J1
    p.put(77, -12, 127, WATER); p.put(77, -11, 127, WATER); p.put(77, -10, 127, WATER); p.put(77, -9, 127, WATER)
    p.put(76, -13, 127, BARS); p.put(78, -13, 127, BARS)
    p.room("cascade grotto", "B1", 58, 79, 116, 139, -7, "Garden water staircases (catena d'acqua) [design]; Hampton Court culverts carry it on", zone="commons")
    # public stairs down from the court (two flights x 49..55 falling east, z 118..119 and 136..137), railed wells
    for zz in (118, 136):
        p.fill(48, -1, zz, 57, 3, zz + 1, AIR)
        p.fill(48, -8, zz, 57, -2, zz + 1, AIR)
        for i in range(7):
            x = 55 - i
            for w in range(2):
                p.put(x, -7 + i, zz + w, "minecraft:stone_brick_stairs", weirdo_direction=PG.STAIR_DIR["west"], upside_down_bit=False)
                for ff in range(-8, -7 + i):
                    p.put(x, ff, zz + w, STONE)
        p.fill(56, -8, zz, 57, -8, zz + 1, STONE)
        p.fill(48, -8, zz, 48, -1, zz + 1, STONE); p.fill(48, -1, zz, 48, -1, zz + 1, STONE)
        p.fill(49, -1, zz - 1, 57, -1, zz - 1, STONE); p.fill(49, -1, zz + 2, 57, -1, zz + 2, STONE)
        G.wall_ring(p, [(x, zz - 1) for x in range(49, 58)], 0)
        G.wall_ring(p, [(x, zz + 2) for x in range(49, 58)], 0)
        p.fill(56, -7, zz, 57, -3, zz + 1, AIR)
        p.fill(56, -2, zz, 57, -1, zz + 1, STONE)
        p.fill(48, -8, zz - 1, 57, -2, zz - 1, STONE); p.fill(48, -8, zz + 2, 57, -2, zz + 2, STONE)
        for ff in range(-8, -1):
            for xx in range(49, 56):
                pass
    p.notes.append("fountain: basin 6 x 6 (feet -1) -> chute -> 5 lipped pools (-3..-7) -> chute through J1 -> the trunk gutter (-14)")


# ==================================================================================================== gate range
def gate_range(p):
    x0, x1 = GATE
    for (za, zb) in ((GATE_Z[0], GH_Z[0] - 1), (GH_Z[1] + 1, GATE_Z[1])):
        p.fill(x0, -2, za, x1, -1, zb, STONE)
        p.fill(x0 + 1, -1, za + 1, x1 - 1, -1, zb - 1, SMOOTH)
        p.shell(x0, x1, za, zb, 0, 9, STONE)
        p.clear(x0 + 1, x1 - 1, za + 1, zb - 1, 0, 4)
        p.slab(x0, x1, za, zb, 5, FLOOR); p.shell(x0, x1, za, zb, 5, 5, STONE)
        p.clear(x0 + 1, x1 - 1, za + 1, zb - 1, 6, 9)
        p.fill(x0, 10, za, x1, 10, zb, CHISEL)
        p.fill(x0, 11, za, x1, 11, zb, "minecraft:stone_brick_slab", **{"minecraft:vertical_half": "bottom"})
        p.windows_along(x0, za, zb, 1, h=3, pitch=4); p.windows_along(x0, za, zb, 6, h=3, pitch=4)
        p.windows_along(x1, za, zb, 1, h=3, pitch=6); p.windows_along(x1, za, zb, 6, h=3, pitch=6)
        # ground: the public offices (toll, notary, court clerk), partitions every 15, doors into the court
        for zc in range(za + 15, zb - 4, 15):
            p.fill(x0 + 1, 0, zc, x1 - 1, 4, zc, STONE); p.door(x0 + 5, 0, zc, "south")
        for zc in range(za + 4, zb - 6, 15):
            p.lectern(x0 + 2, 0, zc, "west"); p.table(x0 + 3, 0, zc + 1); p.chair(x0 + 4, 0, zc + 1, "west")
            p.chest(x0 + 8, 0, zc, "west"); p.door(x1, 0, zc + 4, "east")
        p.room(f"public offices z {za}", "G", x0 + 1, x1 - 1, za + 1, zb - 1, 0, "Doge's Palace: offices on the ground floor", zone="shopfloor")
        # first floor: the clerks' lodgings (6 a side) along a corridor on the court side, then the registry
        p.fill(x0 + 6, 6, za + 1, x0 + 6, 9, zb - 1, PANEL)
        l0 = za + 1 if za == GATE_Z[0] else zb - 36
        for i in range(6):
            zc = l0 + i * 6
            p.fill(x0 + 1, 6, zc + 5, x0 + 5, 9, zc + 5, PANEL)
            p.door(x0 + 6, 6, zc + 2, "east")
            p.bed(x0 + 2, 6, zc + 1, "south", role="clerk"); p.chest(x0 + 1, 6, zc + 4, "east")
        p.room(f"clerks' lodgings z {za}", "N", x0 + 1, x0 + 5, l0, l0 + 35, 6, "R3 §5.4 clerks' lodgings", zone="quarters")
        p.room(f"registry z {za}", "N", x0 + 7, x1 - 1, za + 1, zb - 1, 6, "Chancery registry", zone="workfloor")
        zs = zb - 3 if za == GATE_Z[0] else za + 2
        p.flight(x0 + 2, zs, 0, 5, "east", width=2, across=(0, 1))
        p.clear(x0 + 2, x0 + 6, zs, zs + 1, 5, 9)
        p.fill(x0 + 6, 6, zs - 1, x0 + 6, 9, zs + 2, AIR)
        p.lights_in(x0 + 1, x1 - 1, za + 1, zb - 1, 0); p.lights_in(x0 + 1, x1 - 1, za + 1, zb - 1, 6)
    # the GATEHOUSE (z 114..141): a tower to the eave 19, the carriage arch z 126..129, guard rooms either side
    gz0, gz1 = GH_Z
    p.fill(x0, -2, gz0, x1, -1, gz1, STONE)
    p.shell(x0, x1, gz0, gz1, 0, 19, STONE)
    p.clear(x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 0, 18)
    p.fill(x0 + 1, 5, gz0 + 1, x1 - 1, 5, gz1 - 1, STONE)
    p.fill(x0 + 1, 10, gz0 + 1, x1 - 1, 10, gz1 - 1, FLOOR)
    p.fill(x0 + 1, 15, gz0 + 1, x1 - 1, 15, gz1 - 1, FLOOR)
    p.fill(x0, -1, ARCH_Z[0], x1, -1, ARCH_Z[1], STONE)
    p.fill(x0, 0, ARCH_Z[0], x1, 4, ARCH_Z[1], AIR)
    p.fill(x0 + 1, 0, ARCH_Z[0] - 1, x1 - 1, 4, ARCH_Z[0] - 1, STONE); p.fill(x0 + 1, 0, ARCH_Z[1] + 1, x1 - 1, 4, ARCH_Z[1] + 1, STONE)
    p.fill(x0, 5, ARCH_Z[0], x0, 5, ARCH_Z[1], CHISEL)
    p.fill(x0 + 2, 3, ARCH_Z[0], x0 + 2, 4, ARCH_Z[1], BARS)            # the portcullis (raised 2 blocks)
    for (za, zb, side) in ((gz0 + 1, ARCH_Z[0] - 2, "north"), (ARCH_Z[1] + 2, gz1 - 1, "south")):
        p.bed(x0 + 5, 0, za + 1 if side == "north" else zb - 1, "east", role="guard")
        p.bed(x0 + 5, 0, za + 3 if side == "north" else zb - 3, "east", role="guard")
        p.bed(x0 + 8, 0, za + 1 if side == "north" else zb - 1, "east", role="guard")
        p.chest(x0 + 9, 0, za + 5 if side == "north" else zb - 5, "west")
        dz = ARCH_Z[0] - 1 if side == "north" else ARCH_Z[1] + 1
        p.door(x0 + 6, 0, dz, "south" if side == "north" else "north")
        p.room(f"gatehouse guard room {side}", "G", x0 + 1, x1 - 1, za, zb, 0, "Hampton Court: the guard at every door", zone="quarters")
    p.marker("station", "door", x0 + 4, 0, ARCH_Z[0]); p.marker("station", "post", x0 + 4, 0, ARCH_Z[1])
    p.lights_in(x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 0, 5)
    # porter's lodge (6..9), the second floor (11..14), the watch room (16..18)
    p.lectern(x0 + 9, 6, 127, "west")
    p.bed(x0 + 9, 6, gz0 + 3, "west", role="guard"); p.bed(x0 + 9, 6, gz1 - 3, "west", role="guard")
    p.room("porter's lodge", "N", x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 6, "the porter's lodge over the gate", zone="chamber")
    p.lights_in(x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 6, 5); p.lights_in(x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 11, 5); p.lights_in(x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 16, 5)
    p.room("gatehouse second floor", "N", x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 11, "")
    p.room("gatehouse watch room", "A", x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 16, "")
    for f in (6, 11, 16):
        p.windows_along(x0, gz0, gz1, f, h=2, pitch=4); p.windows_along(x1, gz0, gz1, f, h=2, pitch=4)
    p.fill(x0, 19, gz0, x1, 19, gz1, CHISEL)
    p.roof_pyramid(x0, x1, gz0 - 1, gz1 + 1, 20)
    p.later.append(lambda: gate_stairs(p))


def gate_stairs(p):
    x0 = GATE[0]
    p.spiral3(x0 + 1, GH_Z[0] + 1, 0, [6], "A_turret", "stone", ceiling=10, label="gatehouse turret (lodge)")
    p.spiral3(x0 + 3, GH_Z[0] + 3, 6, [11, 16], "C_grand", "stone", ceiling=19, label="gatehouse tower")
    # the TUNNEL STAIR (U4: the gatehouse branch of the Dover junction): an A turret from the trunk's gatehouse tunnel (B2) to
    # the south guard room, its top exit a jib panel (guards only)
    p.spiral3(x0 + 2, GH_Z[1] - 3, -12, [0], "A_turret", "stone", ceiling=5, label="gatehouse tunnel stair (U4)",
              secret_exits=("top",), ring_lo=-12)
    sp = p.spirals[-1]
    tx = [e for e in sp["exits"] if e[3] == "top"]
    pub = (tx[0][0] + (1 if tx[0][0] > x0 + 3 else -1 if tx[0][0] < x0 + 2 else 0), 0, tx[0][2] + (1 if tx[0][2] > GH_Z[1] - 2 else -1 if tx[0][2] < GH_Z[1] - 3 else 0)) if tx else None
    p.secret("U4a", "Gatehouse tunnel stair (A turret) to the Dover junction", "Dover Castle: 13th-c. tunnels, passages to the towers meeting in a junction",
             "a jib panel in the turret's enclosure in the south guard room; down 12 to the trunk sewer and J1",
             pub, (3, -12, 135), "hidden")
    p.hide("gatehouse tunnel stair", x0 + 1, x0 + 4, GH_Z[1] - 4, GH_Z[1] - 1, -12, 4)


# ==================================================================================================== the wings
def wing(p, zw0, zw1, west):
    x0, x1 = COURT
    zc0, zc1 = zw0 + 11, zw0 + 12                       # the spine corridor (2 wide)
    court_z = (zc1 + 2, zw1 - 1) if west else (zw0 + 1, zc0 - 2)     # rooms on the court side
    outer_z = (zw0 + 1, zc0 - 2) if west else (zc1 + 2, zw1 - 1)
    p.fill(x0, -2, zw0, x1, -1, zw1, STONE)
    p.fill(x0 + 1, -1, zw0 + 1, x1 - 1, -1, zw1 - 1, SMOOTH if west else STATE_FLOOR)
    p.shell(x0, x1, zw0, zw1, 0, 18, STONE)
    p.clear(x0 + 1, x1 - 1, zw0 + 1, zw1 - 1, 0, 18)
    p.slab(x0, x1, zw0, zw1, F_SLAB1, FLOOR); p.shell(x0, x1, zw0, zw1, F_SLAB1, F_SLAB1, CHISEL)
    p.slab(x0, x1, zw0, zw1, F_SLAB2, ATTIC_FLOOR); p.shell(x0, x1, zw0, zw1, F_SLAB2, F_SLAB2, CHISEL)
    p.roof_hip(x0, x1, zw0, zw1, F_EAVE)
    name = "west" if west else "east"
    # corridor walls on every floor (x 13..109); the stair hall x 110..118 is open the full width
    for f0, f1 in ((0, 4), (6, 13), (15, 18)):
        mat = PANEL if f0 == 6 else STONE
        p.fill(x0 + 1, f0, zc0 - 1, 109, f1, zc0 - 1, mat); p.fill(x0 + 1, f0, zc1 + 1, 109, f1, zc1 + 1, mat)
        p.fill(110, f0, zw0 + 1, 110, f1, zw1 - 1, mat)
        p.clear(110, 110, zc0, zc1, f0, f0 + 2)
        p.lights_in(x0 + 1, 109, zc0, zc1 + 1, f0, 6)
        p.lights_in(110, 118, zw0 + 1, zw1 - 1, f0, 5)
        p.room(f"{name} wing corridor f{f0}", {0: "G", 6: "N", 15: "A"}[f0], x0 + 1, 109, zc0, zc1, f0, "")
        p.room(f"{name} wing stair hall f{f0}", {0: "G", 6: "N", 15: "A"}[f0], 111, 118, zw0 + 1, zw1 - 1, f0, "")
    for (zz, pitch) in ((zw0, 4), (zw1, 4)):
        p.windows_along(zz, x0, x1, 1, h=2, pitch=pitch, axis="x")
        p.windows_along(zz, x0, x1, 7, h=4, pitch=pitch, axis="x")
        p.windows_along(zz, x0, x1, 16, h=2, pitch=pitch, axis="x")
    # doors: the court end of the corridor and the corps end (into the corps at x 120, ground + noble)
    p.opening(x0, x0, zc0, zc1, 0, 2)
    p.opening(x1, x1, zc0, zc1, 0, 2); p.opening(x1, x1, zc0, zc1, F_NOBLE, F_NOBLE + 2)
    p.door(x1 - 3, 0, zw1 if west else zw0, "south" if west else "north") if False else None
    cdoor = court_z[1] + 1 if west else court_z[0] - 1     # the wing's court-facing wall
    for xx in (x0 + 20, x0 + 60):
        p.door(xx, 0, cdoor, "south" if west else "north")
    if west:
        west_wing_rooms(p, zw0, zw1, zc0, zc1, court_z, outer_z)
    else:
        east_wing_rooms(p, zw0, zw1, zc0, zc1, court_z, outer_z)
    # the back stair (B tower) in the stair hall, laid last
    p.later.append(lambda: p.spiral3(112, zc0 - 1, -7, [0, 6, 15], "B_tower", "spruce_plaster", ceiling=F_EAVE,
                                     label=f"{name} wing back stair", ring=PANEL, ring_lo=-7))


def west_wing_rooms(p, zw0, zw1, zc0, zc1, cz, oz):
    x0, x1 = COURT
    # GROUND, court side: guard room + armoury (x 13..32), stores (x 34..78), the GREAT HALL x 80..109 (double height)
    p.fill(33, 0, cz[0], 33, 4, cz[1], STONE); p.fill(79, 0, cz[0], 79, 13, cz[1], STONE)
    p.door(20, 0, zc1 + 1, "south"); p.door(50, 0, zc1 + 1, "south")
    for i in range(6):
        p.bed(14 + i * 3, 0, cz[1] - 1, "north", role="guard")
    p.put(30, 0, cz[0] + 1, "minecraft:grindstone", attachment="standing", direction=0)
    p.put(31, 0, cz[0] + 1, "minecraft:anvil", **{"minecraft:cardinal_direction": "north", "damage": "undamaged"})
    p.marker("station", "anvil", 31, 0, cz[0] + 2)
    p.room("west guard room + armoury", "G", 13, 32, cz[0], cz[1], 0, "R3: guard room + armoury 20 x 8", zone="quarters")
    for i in range(10):
        p.barrel(35 + i * 4, 0, cz[1])
    p.room("west wing stores", "G", 34, 78, cz[0], cz[1], 0, "", zone="storeroom")
    # the GREAT HALL (court sittings): x 80..109, z cz (10 wide), feet 0..13 (no first floor over it), a dais, trusses
    p.fill(80, 5, cz[0], 109, 5, cz[1], AIR)
    p.fill(80, 6, cz[0], 109, 13, cz[1], AIR)
    p.fill(80, 6, zc1 + 1, 109, 13, zc1 + 1, STONE)
    p.fill(80, 0, cz[0], 109, 0, cz[1], AIR)
    p.fill(106, 0, cz[0], 109, 0, cz[1], SMOOTH)
    p.put(108, 1, (cz[0] + cz[1]) // 2, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "west"})
    p.marker("station", "seat", 108, 1, (cz[0] + cz[1]) // 2)
    for xx in range(82, 108, 5):
        p.fill(xx, 11, cz[0], xx, 11, cz[1], POST, pillar_axis="z")
        p.put(xx, 12, (cz[0] + cz[1]) // 2, "minecraft:lantern", hanging=True)
    p.door(85, 0, zc1 + 1, "south")
    p.room("GREAT HALL (court sittings)", "G", 80, 109, cz[0], cz[1], 0, "Hampton Court Great Hall 32 x 12 x 14", zone="commons")
    # GROUND, outer side: stores + the smiths' lodging + the registry of deeds
    for xx in range(13, 109, 12):
        p.fill(xx + 11, 0, oz[0], xx + 11, 4, oz[1], STONE) if xx + 11 < 110 else None
        p.door(xx + 5, 0, zc0 - 1, "north")
        p.barrel(xx + 2, 0, oz[0]); p.chest(xx + 4, 0, oz[0], "south")
    p.room("west wing outer stores", "G", 13, 109, oz[0], oz[1], 0, "", zone="storeroom")
    # NOBLE: the chancery hall (x 13..42, 8 lecterns), the Upper Exchequer (x 44..57: the chequered table) + strongroom
    p.fill(43, 6, cz[0], 43, 13, cz[1], PANEL); p.fill(58, 6, cz[0], 58, 13, cz[1], PANEL)
    p.fill(67, 6, cz[0], 67, 13, cz[1], PANEL); p.fill(79, 6, cz[0], 79, 13, cz[1], STONE)
    p.door(25, 6, zc1 + 1, "south"); p.door(50, 6, zc1 + 1, "south"); p.door(62, 6, zc1 + 1, "south"); p.door(72, 6, zc1 + 1, "south")
    for i in range(4):
        p.lectern(16 + i * 6, 6, cz[0] + 2, "south"); p.lectern(16 + i * 6, 6, cz[1] - 1, "north")
    p.fill(14, 6, cz[1], 42, 8, cz[1], "minecraft:bookshelf")
    p.room("chancery hall", "N", 13, 42, cz[0], cz[1], 6, "R3 §5.4 chancery hall 30 x 8 (clerks' lectern stations)", zone="workfloor")
    p.fill(48, 6, cz[0] + 3, 52, 6, cz[0] + 5, "minecraft:white_wool")
    for (ax, az) in ((48, 0), (50, 0), (52, 0), (49, 1), (51, 1), (48, 2), (50, 2), (52, 2)):
        p.put(ax, 6, cz[0] + 3 + az, "minecraft:black_wool")
    p.lectern(50, 6, cz[0] + 7, "north")
    p.room("Upper Exchequer (audit room)", "N", 44, 57, cz[0], cz[1], 6, "the Exchequer's chequered table (R3 §5.4)", zone="workfloor")
    p.fill(59, 6, cz[0], 66, 13, cz[1], STONE); p.clear(61, 64, cz[0] + 2, cz[1] - 2, 6, 9)
    p.fill(60, 6, cz[0] + 4, 60, 7, cz[0] + 4, AIR)
    p.door(60, 6, cz[0] + 4, "east", mat=IRON_DOOR) if False else None
    p.fill(59, 6, zc1 + 2, 66, 9, zc1 + 3, AIR)
    p.door(62, 6, cz[0] + 1, "south", mat=IRON_DOOR)
    p.put(62, 7, cz[0], "minecraft:stone_button", facing_direction=1, button_pressed_bit=False)
    for i in range(4):
        p.chest(61 + i, 6, cz[1] - 2, "north")
    p.room("exchequer strongroom", "N", 61, 64, cz[0] + 2, cz[1] - 2, 6, "", zone="storeroom")
    p.room("exchequer lobby", "N", 59, 66, zc1 + 2, zc1 + 3, 6, "")
    for i in range(3):
        p.table(70 + i, 6, cz[0] + 4)
    p.room("clerks' writing room", "N", 68, 78, cz[0], cz[1], 6, "", zone="workfloor")
    # noble outer side: the registry of deeds and the archive rooms
    for xx in range(13, 109, 16):
        p.fill(xx + 15, 6, oz[0], xx + 15, 13, oz[1], PANEL) if xx + 15 < 110 else None
        p.door(xx + 7, 6, zc0 - 1, "north")
        p.fill(xx + 1, 6, oz[0], xx + 13, 8, oz[0], "minecraft:bookshelf")
    p.room("archive rooms", "N", 13, 109, oz[0], oz[1], 6, "the Chancellery lockers (Doge's Palace, from 1268)", zone="storeroom")
    # ATTIC: servants' garrets (men) both sides, 4 wide x 2 beds
    garrets(p, 13, 105, zw0, zw1, zc0, zc1)


def garrets(p, xa, xb, zw0, zw1, zc0, zc1):
    for side in ("inner", "outer"):
        if side == "inner":
            za, zb, wallz, dz = zw0 + 1, zc0 - 2, zc0 - 1, "north"
        else:
            za, zb, wallz, dz = zc1 + 2, zw1 - 1, zc1 + 1, "south"
        for xx in range(xa, xb - 3, 4):
            p.fill(xx + 3, F_ATTIC, za, xx + 3, F_ATTIC + 3, zb, PANEL)
            p.door(xx + 1, F_ATTIC, wallz, dz)
            p.bed(xx, F_ATTIC, za + (0 if side == "inner" else zb - za - 1), "east" if False else "south" if side == "inner" else "north", role="servant")
            p.bed(xx + 2, F_ATTIC, za + (0 if side == "inner" else zb - za - 1), "south" if side == "inner" else "north", role="servant")
        p.room(f"garrets {side} z {za}", "A", xa, xb, za, zb, F_ATTIC, "Versailles chambermaids' rooms 8-12 m² (R3)", zone="quarters")


def east_wing_rooms(p, zw0, zw1, zc0, zc1, cz, oz):
    x0, x1 = COURT
    # GROUND court side: the household offices
    rooms = [(13, 24, "steward"), (26, 44, "servants' hall"), (46, 54, "butler's pantry"), (56, 64, "housekeeper's room"),
             (66, 74, "still room"), (76, 90, "stores"), (92, 108, "servants' dining")]
    for (ra, rb, kind) in rooms:
        p.fill(rb + 1, 0, cz[0], rb + 1, 4, cz[1], STONE)
        p.door(ra + 3, 0, zc0 - 1, "south")
        if kind == "steward":
            p.lectern(ra + 2, 0, cz[0] + 1, "south"); p.table(ra + 5, 0, cz[0] + 3)
        elif kind == "servants' hall":
            for i in range(5):
                p.table(ra + 3 + i * 3, 0, cz[0] + 4); p.chair(ra + 3 + i * 3, 0, cz[0] + 3, "south"); p.chair(ra + 3 + i * 3, 0, cz[0] + 5, "north")
            for i in range(8):
                p.bell(ra + 2 + i * 2, 1, cz[0], "south")
            p.marker("station", "seat", ra + 6, 0, cz[0] + 4)
        elif kind == "butler's pantry":
            p.chest(ra + 1, 0, cz[0], "south"); p.chest(ra + 2, 0, cz[0], "south"); p.marker("station", "store", ra + 2, 0, cz[0] + 2)
        elif kind == "still room":
            p.put(ra + 2, 0, cz[0], "minecraft:furnace", **{"minecraft:cardinal_direction": "south"}); p.marker("station", "oven", ra + 2, 0, cz[0] + 1)
        else:
            for i in range(4):
                p.barrel(ra + 1 + i, 0, cz[0])
        p.room(kind, "G", ra, rb, cz[0], cz[1], 0, "Kerr / R3 §2.3 household offices",
               zone={"steward": "chamber", "servants' hall": "commons", "butler's pantry": "storeroom", "housekeeper's room": "chamber",
                     "still room": "kitchen", "stores": "storeroom", "servants' dining": "commons"}[kind])
    # GROUND outer side: servants' quarters (2 beds per room)
    for xx in range(13, 105, 8):
        p.fill(xx + 7, 0, oz[0], xx + 7, 4, oz[1], STONE)
        p.door(xx + 3, 0, zc1 + 1, "north")
        p.bed(xx, 0, oz[1] - 1, "north", role="servant"); p.bed(xx + 2, 0, oz[1] - 1, "north", role="servant")
        p.chest(xx + 5, 0, oz[1], "north")
    p.room("servants' quarters (east)", "G", 13, 108, oz[0], oz[1], 0, "Kerr: servants' bedrooms", zone="quarters")
    # the BAIZE DOOR at the stair hall: a warped door in green wool between the offices and the family stair
    p.fill(110, 0, zc0 - 1, 110, 3, zc1 + 1, "minecraft:green_wool")
    p.fill(110, 0, zc0, 110, 1, zc1, AIR)
    p.door(110, 0, zc0, "east", mat="minecraft:warped_door")
    p.secret("H16", "Baize door", "R3 §2.3: the green baize door between the service and the family sides",
             "a warped door framed in green wool where the offices corridor meets the back stair", (109, 0, zc0), (111, 0, zc0), "lore")
    # NOBLE + ATTIC: six family apartments on each (3 per side)
    for (f0, clear, lvl) in ((F_NOBLE, 8, "N"), (F_ATTIC, 4, "A")):
        for xa in (13, 40, 67):
            family(p, f"east wing {lvl} court x {xa}", "x", xa, cz[0], cz[1], zc0 - 1, f0, clear, lvl, toward=-1)
            family(p, f"east wing {lvl} outer x {xa}", "x", xa, oz[0], oz[1], zc1 + 1, f0, clear, lvl, toward=+1)
    # the tribune door: the corridor's corps end at noble level opens onto the chapel's tribune (x 121..)
    p.notes.append("east wing: 7 offices, 12 servants' rooms, 12 family apartments (noble + attic), the baize door")


def family(p, label, axis, a0, d0, d1, dwall, f0, clear, lvl, toward):
    """ONE NOBLE FAMILY'S APARTMENT (brief §4.4: Versailles courtier lodging + the nursery rule 'nurse… within earshot'),
    26 long along `axis` from a0, rooms d0..d1 deep across it, the corridor wall at dwall (toward = +1 when the rooms lie on
    the + side of the corridor). antechamber 6 | bedchamber 8 (the couple's bed + alcove balustrade) | children's chamber 5
    (2 beds against the far wall) with the NURSE'S CLOSET 3 x 3 (1 bed) at its corridor end | cabinet 4."""
    def P(u, v):                                 # (along, across) -> (x, z)
        return (u, v) if axis == "x" else (v, u)

    def put(u, f, v, name, **st):
        x, z = P(u, v); p.put(x, f, z, name, **st)

    def wall_u(u):                               # a partition across the rooms at along = u
        for v in range(min(d0, d1), max(d0, d1) + 1):
            for f in range(f0, f0 + clear):
                put(u, f, v, PANEL)

    def door_u(u, v, facing):
        x, z = P(u, v); p.door(x, f0, z, facing)

    vs = sorted((d0, d1))
    near = dwall + toward                         # the row against the corridor wall
    far = d0 if abs(d0 - dwall) > abs(d1 - dwall) else d1
    step = 1 if toward > 0 else -1
    a = a0
    wall_u(a + 6); wall_u(a + 15); wall_u(a + 21); wall_u(a + 26)
    along_pos = "east" if axis == "x" else "south"
    across_in = ("south" if toward > 0 else "north") if axis == "x" else ("east" if toward > 0 else "west")
    # corridor -> antechamber
    x, z = P(a + 2, dwall); p.door(x, f0, z, across_in)
    mid = near + step * 3
    door_u(a + 6, mid, along_pos); door_u(a + 15, mid, along_pos); door_u(a + 21, mid + step * 2, along_pos)
    # antechamber: table + chairs
    tx, tz = P(a + 3, mid); p.table(tx, f0, tz)
    # bedchamber: the couple's bed (one double bed: couples sleep 2 to a bed) + the alcove balustrade
    bx, bz = P(a + 10, far)
    head = "east" if axis == "z" and toward > 0 else "west" if axis == "z" else "south" if toward > 0 else "north"
    hu, hv = P(a + 10, far - step)
    p.bed(hu, f0, hv, head, role="noble")
    for u in (a + 8, a + 12):
        x, z = P(u, far - step * 2)
        if clear > 4:
            p.put(x, f0, z, "minecraft:spruce_fence")
    cx, cz = P(a + 13, near); p.chest(cx, f0, cz, "north" if axis == "x" else "west")
    # children's chamber a+16..a+20: the nurse's closet = a+18..a+20 x the 3 rows at the corridor end, its wall at a+17 and
    # at row near + 3*step; door from the children's chamber at (a+17, near + step)
    for v in range(near, near + step * 3, step):
        for f in range(f0, f0 + clear):
            put(a + 17, f, v, PANEL)
    vw = near + step * 3
    for u in range(a + 17, a + 21):
        for f in range(f0, f0 + clear):
            put(u, f, vw, PANEL)
    door_u(a + 17, near + step, along_pos)
    # the nurse's bed inside the closet (head against the corridor wall)
    nu, nv = P(a + 19, near + step)
    p.bed(nu, f0, nv, {("x", 1): "north", ("x", -1): "south", ("z", 1): "west", ("z", -1): "east"}[(axis, toward)], role="servant")
    # two children's beds against the far wall, heads to the wall
    chead = {("x", 1): "south", ("x", -1): "north", ("z", 1): "east", ("z", -1): "west"}[(axis, toward)]
    for u in (a + 16, a + 19):
        cu, cv = P(u, far - step)
        p.bed(cu, f0, cv, chead, role="child")
    # cabinet: lectern + chair
    lx, lz = P(a + 23, mid); p.lectern(lx, f0, lz, "west" if axis == "x" else "north", station=False)
    # light
    for u in (a + 3, a + 11, a + 18, a + 24):
        x, z = P(u, mid + step)
        if p.free(x, f0 + clear - 1, z):
            p.put(x, f0 + clear - 1, z, LIGHT)
    for (u0, u1, nm) in ((a, a + 5, "antechamber"), (a + 7, a + 14, "bedchamber"), (a + 16, a + 20, "children's chamber"), (a + 22, a + 25, "cabinet")):
        X0, Z0 = P(u0, vs[0]); X1, Z1 = P(u1, vs[1])
        p.room(f"{label} {nm}", lvl, min(X0, X1), max(X0, X1), min(Z0, Z1), max(Z0, Z1), f0,
               "Versailles courtier lodging (antechamber + bedchamber + cabinet); the nursery rule 'nurse… within earshot'",
               zone="chamber" if nm != "children's chamber" else "quarters")
    X0, Z0 = P(a + 18, near); X1, Z1 = P(a + 20, near + step * 2)
    p.room(f"{label} nurse's closet", lvl, min(X0, X1), max(X0, X1), min(Z0, Z1), max(Z0, Z1), f0, "nurse 'within earshot' (Wikipedia: Nursery)")


# ==================================================================================================== the corps de logis
def corps(p):
    x0, x1 = CORPS
    z0, z1 = CZ[0], CHAPEL[0] - 1                      # the main block z 16..215 (the chapel bay is its own block)
    p.fill(x0, -2, z0, x1, -1, z1, STONE)
    p.fill(x0 + 1, -1, z0 + 1, x1 - 1, -1, z1 - 1, STATE_FLOOR)
    p.shell(x0, x1, z0, z1, 0, 18, STONE)
    p.clear(x0 + 1, x1 - 1, z0 + 1, z1 - 1, 0, 18)
    p.slab(x0, x1, z0, z1, F_SLAB1, FLOOR); p.slab(x0, x1, z0, z1, F_SLAB2, ATTIC_FLOOR)
    p.fill(x0, F_SLAB1, z0, x1, F_SLAB1, z0, CHISEL); p.fill(x0, F_SLAB1, z1, x1, F_SLAB1, z1, CHISEL)
    p.fill(x0, F_SLAB1, z0, x0, F_SLAB1, z1, CHISEL); p.fill(x1, F_SLAB1, z0, x1, F_SLAB1, z1, CHISEL)
    p.fill(x0, F_SLAB2, z0, x1, F_SLAB2, z0, CHISEL); p.fill(x0, F_SLAB2, z1, x1, F_SLAB2, z1, CHISEL)
    p.fill(x0, F_SLAB2, z0, x0, F_SLAB2, z1, CHISEL); p.fill(x1, F_SLAB2, z0, x1, F_SLAB2, z1, CHISEL)
    # roofs: a hipped roof over the court half (x 120..136), a flat lead roof with a balustrade over the garden half
    p.roof_hip(x0, XW, z0, z1, F_EAVE)
    p.fill(XK[0], F_EAVE, z0, x1, F_EAVE, z1, "minecraft:smooth_stone")
    G.wall_ring(p, [(x1, z) for z in range(z0, z1 + 1)] + [(x, z0) for x in range(XK[0], x1)] + [(x, z1) for x in range(XK[0], x1)], F_EAVE + 1)
    p.lights_in(XK[0], x1 - 1, z0 + 1, z1 - 1, F_EAVE + 1, 8)
    # the rear wall is 3 thick (x 157..159); the stoking wall 145..147
    p.fill(XR[0], 0, z0 + 1, XR[1], 18, z1 - 1, STONE)
    p.fill(XST[0], 0, z0 + 1, XST[1], 13, z1 - 1, STONE)
    # the government bay z 17..40 and the gov/lord wall z 41
    p.fill(x0 + 1, 0, GOV[1] + 1, XR[0] - 1, 18, GOV[1] + 1, STONE)
    p.clear(x0 + 1, XST[0] - 1, GOV[0], GOV[1], 0, 4); p.clear(x0 + 1, XR[0] - 1, GOV[0], GOV[1], 6, 13); p.clear(x0 + 1, XR[0] - 1, GOV[0], GOV[1], 15, 18)
    p.fill(XST[0], 0, GOV[0], XR[0] - 1, 4, GOV[1], STONE)
    # the jib partition x 133, the spine 134..135, wall 136 — on the ground and noble floors, z 42..214
    for (f0, f1, mat) in ((0, 4, STONE), (6, 13, PANEL)):
        p.fill(XP, f0, 42, XP, f1, z1 - 1, mat)
        p.fill(XW, f0, 42, XW, f1, z1 - 1, STONE)
        p.fill(XC[0], f0 + 3, 42, XC[1], f1, z1 - 1, STONE)
        p.clear(XC[0], XC[1], 42, z1 - 1, f0, f0 + 2)
        for zz in range(45, z1 - 3, 8):
            p.lantern(XC[0], f0 + 2, zz, hanging=True)
    p.fill(XC[0], 0, 42, XC[1], 4, 42, STONE)
    for (za, zb) in (SPINE_L, SPINE_C):
        p.room(f"hidden spine G z {za}", "G", XC[0], XC[1], za + 1, zb, 0, "Versailles: the service rooms behind the Queen's apartment; Kerr's service separation", hidden=True)
        p.room(f"hidden spine N z {za}", "N", XC[0], XC[1], za + 1, zb, 6, "Versailles: service rooms behind the state apartment", hidden=True)
        p.hide("hidden spine", XC[0], XC[1], za, zb, 0, 2); p.hide("hidden spine", XC[0], XC[1], za, zb, 6, 8)
    # the stoking passage (noble, x 146) behind the cabinet zone and the gallery
    p.clear(146, 146, 42, z1 - 1, 6, 8)
    p.fill(146, 6, 127, 146, 8, 135, STONE)
    p.room("stoking passage (lord)", "N", 146, 146, 42, 126, 6, "Schönbrunn: stoves 'stoked… from a passage running behind the walls'", hidden=True)
    p.room("stoking passage (consort)", "N", 146, 146, 136, 214, 6, "Schönbrunn stoking passage", hidden=True)
    p.hide("stoking passage", 146, 146, 42, 214, 6, 8)
    p.secret("H2", "Stoking passage behind the gallery and the lord's rooms", "Schönbrunn: every stove 'stoked… from a passage running behind the walls of the rooms'",
             "from the garde-robe and the consort's cabinets by the crossings of the 3-thick wall (servants)", (144, 6, 77), (146, 6, 90), "disguised")
    # windows: court wall (ground 1..3, noble 7..11 tall, attic 16..17), rear wall (glass in the outer skin)
    p.windows_along(x0, z0, z1, 1, h=3, pitch=4); p.windows_along(x0, z0, z1, 7, h=5, pitch=4); p.windows_along(x0, z0, z1, 16, h=2, pitch=4)
    p.notes.append("corps: shell x 120..159 z 16..215, partition 133, spine 134..135, cabinet 137..144, stoking wall 145..147, garden 148..156, rear wall 157..159")


def corps_ground(p):
    """GROUND FLOOR (0..4). Lord's half: the Lower Gallery along the court wall (x 121..123, Versailles' Lower Gallery
    between the Dauphin and the Dauphine) and behind it (x 125..132) the ROYAL CHILDREN'S LODGING on the model of Prince
    Edward's 1537 lodgings at Hampton Court + the LORD'S WARDROBE directly under the state bedchamber (Hampton Court: the
    king's Wardrobe lay below his bedchamber). Centre: the entrance + grand stair hall. Consort's half: guard post, offices,
    the consort's wardrobe."""
    x0 = XS[0]
    p.fill(124, 0, 42, 124, 4, 119, STONE)                                   # Lower Gallery | lodging
    p.room("Lower Gallery", "G", 121, 123, 42, 119, 0, "Versailles: the Lower Gallery between the Dauphin's and the Dauphine's apartments; 'Lower Gallery' 30 x 3", zone="threshold")
    p.lights_in(121, 123, 42, 119, 0, 6)
    walls = [41, 48, 54, 60, 69, 80, 86, 95, 104, 111, 120]
    for w in walls[1:-1]:
        p.fill(125, 0, w, 132, 4, w, STONE)
    rooms = [(42, 47, "governess's room"), (49, 53, "washing chamber"), (55, 59, "jakes (privy)"), (61, 68, "nursery kitchen + laundry"),
             (70, 79, "LORD'S WARDROBE"), (81, 85, "nurses' lodging"), (87, 94, "NIGHT NURSERY"), (96, 103, "rocking chamber / day nursery"),
             (105, 110, "presence chamber"), (112, 119, "watching chamber")]
    imit = {"governess's room": "Versailles: the Governess of the Children of France's apartment (same floor as the children)",
            "washing chamber": "Hampton Court 1537: 'The Prince's Washing Chamber'",
            "jakes (privy)": "Hampton Court 1537: 'My Lord Prince's Jakes' (chute to the culverts)",
            "nursery kitchen + laundry": "Hampton Court 1537: the household floor 'probably a kitchen and laundry'",
            "LORD'S WARDROBE": "Hampton Court: the king's Wardrobe directly below his bedchamber, the spiral stair beside it",
            "nurses' lodging": "Hampton Court 1537: 'The Lodging Next to the Nursery' (nurse + nursemaid + rocker within earshot)",
            "NIGHT NURSERY": "Hampton Court 1537: 'The Nursery'; the night nursery (Wikipedia: Nursery)",
            "rocking chamber / day nursery": "Hampton Court 1537: 'The Rocking Chamber'; the day nursery",
            "presence chamber": "Hampton Court 1537: 'The Prince's Presence Chamber'",
            "watching chamber": "Hampton Court 1537: 'The Prince's Watching Chamber' (controlled access)"}
    for (za, zb, nm) in rooms:
        zm = (za + zb) // 2
        p.door(124, 0, zm, "east")                                             # from the Lower Gallery
        p.room(nm, "G", 125, 132, za, zb, 0, imit[nm], zone="quarters" if nm in ("NIGHT NURSERY", "nurses' lodging", "governess's room") else "chamber")
        p.lights_in(125, 132, za, zb, 0, 4)
    # governess (servant role: no new role names), nurses x 3, the night nursery x 4 children, the watching chamber's guards
    p.bed(126, 0, 43, "south", role="servant"); p.lectern(131, 0, 46, "west", station=False)
    p.put(127, 0, 50, "minecraft:cauldron", cauldron_liquid="water", fill_level=6); p.put(130, 0, 52, "minecraft:cauldron", cauldron_liquid="water", fill_level=6)
    # the jakes: a seat over a garderobe chute (1 x 1, down to the west... the corps sewer is under the court: the chute runs in
    # the court wall's footing to a gully) — here a trapdoor seat over a sealed chute
    p.put(131, 0, 57, "minecraft:spruce_trapdoor", direction=1, open_bit=False, upside_down_bit=True)
    p.put(131, -1, 57, AIR); p.put(131, -2, 57, AIR); p.put(131, -3, 57, AIR)
    p.put(126, 0, 62, "minecraft:furnace", **{"minecraft:cardinal_direction": "south"}); p.marker("station", "oven", 126, 0, 63)
    p.put(130, 0, 62, "minecraft:cauldron", cauldron_liquid="water", fill_level=6)
    p.bed(130, 0, 71, "south", role="servant")                                # the valet in the wardrobe
    for i in range(3):
        p.chest(126 + i, 0, 79, "north")
    p.bed(126, 0, 82, "south", role="servant"); p.bed(128, 0, 82, "south", role="servant"); p.bed(130, 0, 82, "south", role="servant")
    for (bx, bz) in ((126, 88), (126, 92), (131, 88), (131, 92)):
        p.bed(bx, 0, bz, "east" if bx == 131 else "west", role="child")
    p.put(129, 0, 97, "pw:furn_chair_oak", **{"minecraft:cardinal_direction": "west"})
    p.put(126, 0, 99, "minecraft:note_block") if False else None
    p.table(128, 0, 100); p.chair(129, 0, 100, "west")
    p.put(131, 0, 107, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "west"})
    p.bed(126, 0, 113, "south", role="guard"); p.bed(126, 0, 117, "north", role="guard")
    p.door(120, 0, 115, "west")                                                # the lodging's own entrance from the court
    p.door(124, 0, 115, "east")
    # the Lower Gallery's only public door is the watching chamber's: make the watching chamber -> gallery door the one
    # at 115 and the court door the lodging's entrance (Henry 'strictly controlled access')
    # the night nursery's jib door into the spine: the family's way to the children's stair (H5)
    p.jib2(XP, 0, 90)
    p.fill(XW, 0, 89, XW, 1, 90, AIR)
    p.door(XW, 0, 89, "east")
    # ---- centre: the entrance + grand stair hall z 121..134 (the court door 4 wide at z 126..129)
    p.fill(x0, 0, 120, XS[1], 4, 120, STONE); p.fill(x0, 0, 135, XS[1], 4, 135, STONE)
    p.opening(CORPS[0], CORPS[0], 126, 129, 0, 4)
    p.fill(CORPS[0], 0, 125, CORPS[0], 4, 125, CHISEL); p.fill(CORPS[0], 0, 130, CORPS[0], 4, 130, CHISEL)
    p.room("entrance + grand stair hall", "G", x0, XS[1], 121, 134, 0, "Versailles: the Queen's Staircase serves both apartments", zone="threshold")
    p.door(122, 0, 120, "north"); p.door(122, 0, 135, "south")
    p.lights_in(x0, XS[1], 121, 134, 0, 5)
    # ---- consort's half (state zone)
    for w in (147, 161, 174, 186, 198):
        p.fill(x0, 0, w, XS[1], 4, w, STONE)
    crooms = [(136, 146, "consort's guard post"), (148, 160, "constable's office"), (162, 173, "waiting room"),
              (175, 185, "CONSORT'S WARDROBE"), (187, 197, "consort's household office"), (199, 214, "east lobby")]
    for (za, zb, nm) in crooms:
        p.door(CORPS[0], 0, (za + zb) // 2, "west")
        p.door(123, 0, za - 1, "south") if za > 136 else None
        p.room(nm, "G", x0, XS[1], za, zb, 0, "Versailles: the Queen's wardrobe below" if "WARDROBE" in nm else "", zone="chamber")
        p.lights_in(x0, XS[1], za, zb, 0, 5)
    for i in range(4):
        p.bed(122 + i * 3, 0, 145, "north", role="guard")
    p.lectern(126, 0, 150, "west")
    for i in range(4):
        p.put(122 + i * 2, 0, 166, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "south"})
    p.bed(130, 0, 176, "south", role="servant")
    # ---- the cabinet zone + garden range at ground: the valets' and servants' rooms, the buttery under the dining room,
    # reached from the spine (doors in wall 136) and through the stoking wall (door tunnels)
    gz = [(42, 56), (58, 68), (70, 82), (84, 98), (100, 112), (114, 126), (136, 160), (162, 186), (188, 214)]
    for (za, zb) in gz:
        p.fill(XK[0], 0, zb + 1, XK[1], 4, zb + 1, STONE) if zb < 214 else None
        p.fill(XG[0], 0, zb + 1, XG[1], 4, zb + 1, STONE) if zb < 214 else None
        zm = (za + zb) // 2
        p.door(XW, 0, zm, "east")
        p.fill(XST[0], 0, zm, XST[1], 1, zm, AIR)
        p.door(XST[0], 0, zm, "east")
        p.room(f"cabinet-zone room G z {za}", "G", XK[0], XK[1], za, zb, 0, "", zone="storeroom")
        p.room(f"garden-range room G z {za}", "G", XG[0], XG[1], za, zb, 0, "", zone="storeroom")
        p.lights_in(XK[0], XK[1], za, zb, 0, 5); p.lights_in(XG[0], XG[1], za, zb, 0, 5)
    p.fill(XK[0], 0, 127, XG[1], 4, 135, STONE)
    for i in range(4):
        p.bed(150 + i * 2, 0, 160, "north", role="servant"); p.bed(150 + i * 2, 0, 186, "north", role="servant")
    for i in range(3):
        p.bed(139 + i * 2, 0, 160, "north", role="servant")
    # the SERVANTS' DOOR: from the alley through the rear wall into the garden range room at z 198 (the service entrance)
    p.fill(XR[0], 0, 198, XR[1], 1, 198, AIR)
    p.door(XR[1], 0, 198, "east")
    p.lights_in(XC[0], XC[1], 42, 214, 0, 8)
    p.notes.append("corps ground: Lower Gallery, children's lodging (10 rooms), wardrobe, stair hall, consort's offices, servants' rooms")


def corps_noble(p):
    """ÉTAGE NOBLE (6..13): the LORD's enfilade west of the grand stair (Versailles King's sequence: guard room ->
    antechambers -> state bedchamber -> council cabinet -> cabinets), the CONSORT's to the east (Versailles Queen's:
    guard room -> antechamber -> salon of nobles -> bedchamber with a jib door each side of the bed), every state room
    with a jib door into the hidden spine (bell + button), the cross salon to the gallery."""
    x0 = XS[0]
    # lord: walls (z) and rooms
    L = [(42, 48, "wig cabinet", "Versailles: the King's wig cabinet"), (50, 56, "lord's cabinet", "Versailles: cabinet (public)"),
         (58, 68, "COUNCIL CABINET", "Versailles: Cabinet du Conseil"), (70, 79, "LORD'S STATE BEDCHAMBER", "Versailles: Chambre du Roi (private bedchamber 1738 ~89 m², >10 m high)"),
         (81, 93, "grand antechamber (Œil-de-Bœuf)", "Versailles: the Œil-de-Bœuf"), (95, 106, "first antechamber (Grand Couvert)", "Versailles: first antechamber / public dining"),
         (108, 119, "lord's guard room", "Versailles: Salle des Gardes du Roi (petitions)")]
    C = [(136, 147, "consort's guard room", "Versailles: the Queen's guard room"), (149, 161, "consort's antechamber (Grand Couvert)", "Versailles: Antichambre du Grand Couvert"),
         (163, 173, "salon of nobles", "Versailles: Salon des Nobles"), (175, 184, "CONSORT'S STATE BEDCHAMBER", "Versailles: Chambre de la Reine (two doors under hangings, 6 Oct 1789)"),
         (186, 196, "consort's inner cabinet", "Versailles: the Queen's inner cabinet"), (198, 214, "east stair lobby", "")]
    for seq in (L, C):
        for (za, zb, nm, im) in seq:
            if za > 42 and za != 136:
                p.fill(x0, F_NOBLE, za - 1, XS[1], F_NOBLE + 7, za - 1, PANEL)
                p.door(122, F_NOBLE, za - 1, "south")                      # the enfilade door (near the court windows)
            p.carpet(x0 + 1, XS[1] - 1, za + 1, zb - 1, F_NOBLE, "red" if seq is L else "blue")
            p.room(nm, "N", x0, XS[1], za, zb, F_NOBLE, im, zone="chamber")
            p.lantern(126, F_NOBLE + 6, (za + zb) // 2, hanging=True)
            p.lights_in(x0, XS[1], za, zb, F_NOBLE, 5)
            if nm in ("east stair lobby",):
                continue
            zj = (za + zb) // 2 + (2 if "BEDCHAMBER" in nm else 0)
            if "CONSORT'S STATE" in nm:
                continue
            p.jib2(XP, F_NOBLE, zj)
            p.button(XP - 1, F_NOBLE + 1, zj + 1, "west"); p.bell(XC[0], F_NOBLE, zj + 1, "west") if zj + 1 <= 214 else None
            p.secret(f"H1-{nm[:24]}", f"Jib door: {nm} -> hidden spine", "Versailles: doors in the panelling to the service rooms behind the state apartment",
                     "a pw:jib_panel (looks like the panelling) in the room's rear wall; a bell in the spine answers the room's button",
                     (XP - 1, F_NOBLE, zj), (XC[0], F_NOBLE, zj), "disguised")
    p.fill(x0, F_NOBLE, 120, XS[1], F_NOBLE + 7, 120, PANEL); p.door(122, F_NOBLE, 120, "south")
    p.fill(x0, F_NOBLE, 135, XS[1], F_NOBLE + 7, 135, PANEL); p.door(122, F_NOBLE, 135, "south")
    # the lord's guard room: 4 camp beds; council chairs; the bedchamber's alcove + balustrade + the bricked-up arch (H14)
    for i in range(4):
        p.bed(129, F_NOBLE, 110 + i * 2, "east", role="guard")
    for i in range(5):
        p.chair(122, F_NOBLE, 59 + i * 2, "east"); p.chair(131, F_NOBLE, 59 + i * 2, "west")
    p.table(126, F_NOBLE, 62); p.table(126, F_NOBLE, 63); p.table(126, F_NOBLE, 64)
    p.marker("station", "seat", 126, F_NOBLE, 66)
    p.fill(128, F_NOBLE, 70, 128, F_NOBLE, 79, "minecraft:spruce_fence"); p.put(128, F_NOBLE, 76, AIR); p.put(128, F_NOBLE, 77, AIR)
    p.bed(130, F_NOBLE, 75, "east", role="lord")
    p.put(123, F_NOBLE, 75, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "east"})
    # H14: the bricked-up arch in the alcove's end wall (z 80): a chiselled frame, stone-brick infill (lore, not a way)
    p.fill(129, F_NOBLE, 80, 131, F_NOBLE + 3, 80, CHISEL); p.fill(130, F_NOBLE, 80, 130, F_NOBLE + 2, 80, "minecraft:mossy_stone_bricks")
    p.secret("H14", "Bricked-up arch in the lord's alcove", "Hampton Court: 'a bricked-up doorway… once connected the king's secret lodgings directly with Wolsey's gallery'",
             "visible blocked Tudor arch in the alcove wall (lore only — no way through)", (130, F_NOBLE, 79), None, "lore")
    # the consort's bedchamber: the bed against the rear (x 132), a jib door each side under hangings (H3)
    p.fill(128, F_NOBLE, 175, 128, F_NOBLE, 184, "minecraft:spruce_fence"); p.put(128, F_NOBLE, 179, AIR); p.put(128, F_NOBLE, 180, AIR)
    p.bed(131, F_NOBLE, 179, "east", role="lord")
    for zj in (177, 182):
        p.jib2(XP, F_NOBLE, zj)
        p.fill(XP - 1, F_NOBLE + 2, zj, XP - 1, F_NOBLE + 2, zj, "minecraft:purple_carpet") if False else None
    p.secret("H3", "The consort's escape: jib doors either side of her bed -> spine -> the lord's bedchamber", "Versailles 6 Oct 1789: 'two doors under hangings on either side of the bed'; Marie-Antoinette 'took the door on the left'",
             "two pw:jib_panel doors in the alcove wall beside the bed; along the spine 100 blocks west to the lord's jib door", (131, F_NOBLE, 177), (XC[0], F_NOBLE, 177), "disguised")
    # the grand stair hall (noble) z 121..134 opens into the CROSS SALON z 128..134 across the spine to the gallery
    p.clear(XP, XG[1], 128, 134, F_NOBLE, F_NOBLE + 7)
    p.fill(XP, F_NOBLE, 127, XG[1], F_NOBLE + 7, 127, PANEL); p.fill(XK[0], F_NOBLE, 135, XG[1], F_NOBLE + 7, 135, PANEL)
    p.jib2(XC[0], F_NOBLE, 127); p.jib2(XC[1], F_NOBLE, 127); p.jib2(XC[0], F_NOBLE, 135); p.jib2(XC[1], F_NOBLE, 135)
    p.fill(XP, F_NOBLE, 121, XP, F_NOBLE + 7, 127, PANEL)
    p.fill(XP, F_NOBLE, 135, XP, F_NOBLE + 7, 135, PANEL)
    p.clear(150, 154, 135, 135, F_NOBLE, F_NOBLE + 4)
    p.carpet(XP + 1, XG[1] - 1, 129, 133, F_NOBLE, "red")
    p.room("grand stair hall (noble)", "N", x0, XS[1], 121, 134, F_NOBLE, "Versailles: Queen's Staircase landing", zone="threshold")
    p.room("cross salon (Salon de la Paix)", "N", XP, XG[1], 128, 134, F_NOBLE, "Versailles: Salon de la Paix at the gallery's end", zone="threshold")
    p.lights_in(XP, XG[1], 128, 134, F_NOBLE, 5); p.lights_in(x0, XS[1], 121, 134, F_NOBLE, 5)
    p.fill(XST[0], F_NOBLE, 128, XST[1], F_NOBLE + 7, 134, AIR)
    p.fill(XST[0], F_NOBLE + 5, 128, XST[1], F_NOBLE + 7, 134, STONE)
    # the CONSORT's spine end (z 214) -> the chapel tribune: a jib panel through the end wall (H15)
    p.secret("H15", "Royal tribune door: the spine's east end -> the chapel's tribune", "Versailles: the royal family entered the chapel's tribune from the state floor; Hofburg: the palace church 'engulfed' by the palace",
             "a jib panel at the spine's end opens onto the tribune balcony (the nobles use the east wing's door)", (XC[0], F_NOBLE, 214), (XC[0], F_NOBLE, 218), "disguised")


def cabinet_zone(p):
    """the CABINET ZONE x 137..144 behind the spine (the lord's petits cabinets + garde-robe; the consort's private
    cabinets on TWO entresol floors — Versailles: Marie-Antoinette's private chambers 'spread over two floors'), the stoking
    wall crossings, and the GARDEN RANGE x 148..156 (the lord's private study, Studiolo, Tesoretto + inner hide, garden
    cabinet with the water stair, private bedchamber, private dining room with the flying table; the GALLERY; the consort's
    garden rooms)."""
    k0, k1 = XK
    g0, g1 = XG
    f = F_NOBLE
    # ---- lord side, cabinet zone (single tall level 6..13)
    for w in (57, 69, 96):
        p.fill(k0, f, w, k1, f + 7, w, PANEL)
    K = [(42, 56, "lord's petits cabinets (arrière-cabinet)", "Versailles: the King's arrière-cabinet with 'secret drawers and compartments'"),
         (58, 68, "chaise closet + private lobby", "Versailles: 'cabinet de la chaise… communicated directly with the degré du roi'"),
         (70, 95, "GARDE-ROBE", "Versailles: garde-robe behind the King's chamber"),
         (97, 126, "dispatch room", "Versailles: the inner study 'where… he received his spies and confidential informers'")]
    for (za, zb, nm, im) in K:
        zm = (za + zb) // 2
        p.door(XW, f, zm if nm != "GARDE-ROBE" else 92, "east")
        p.room(nm, "N", k0, k1, za, zb, f, im, zone="chamber")
        p.lights_in(k0, k1, za, zb, f, 5)
    # H12: the garderobe-shaft closet in the garde-robe's corner (x 142..144, z 71..73): the closet door is a jib panel;
    # a 1 x 1 shaft (vanilla ladder) from the noble floor to the B2 junction (Baddesley Clinton 1591)
    p.fill(141, f, 70, 141, f + 7, 74, PANEL); p.fill(141, f, 74, k1, f + 7, 74, PANEL)
    p.jib2(141, f, 72)
    p.room("garderobe-shaft closet", "N", 142, k1, 70, 73, f, "Baddesley Clinton: priests 'slid down… through the old garderobe shaft into the house's sewers'", hidden=True)
    p.hide("garderobe-shaft closet + shaft", 142, 144, 71, 73, -12, f + 2)
    for ff in range(-12, f):
        p.put(144, ff, 72, "minecraft:ladder", facing_direction=4)
    p.put(144, f, 72, "minecraft:spruce_trapdoor", direction=0, open_bit=False, upside_down_bit=False)
    # enclose the shaft on the ground floor (a stone pier round x 143..144 z 71..73) and through B1
    for ff in range(-8, 5):
        for (sx, sz) in ((143, 71), (143, 72), (143, 73), (144, 71), (144, 73)):
            if p.free(sx, ff, sz) or p.get(sx, ff, sz) in (DIRT,):
                p.put(sx, ff, sz, STONE)
    p.secret("H12", "Garderobe-shaft drop", "Baddesley Clinton 1591: down 'the old garderobe shaft into the house's sewers'",
             "a jib panel into a closet in the garde-robe; a trapdoor over a ladder shaft 18 blocks down to the escape junction",
             (140, f, 72), (144, -12, 73) if False else (145, -12, 73), "hidden")
    # the link garde-robe <-> garden cabinet through the stoking wall (z 77) and the dispatch room <-> private dining (z 104)
    for zl in (60, 77, 115):
        p.fill(XST[0], f, zl, XST[1], f + 1, zl, AIR)
        p.door(XST[0], f, zl, "east"); p.door(XST[1], f, zl, "east")
    # ---- lord side, GARDEN RANGE (the private apartment — Versailles' petit appartement du roi)
    for w in (48, 64, 68, 71, 82, 93, 99, 110):
        p.fill(g0, f, w, g1, f + 7, w, PANEL)
    p.fill(g0, f, 120, g1, f + 7, 127, PANEL)
    GR = [(49, 63, "lord's private study (Scrittoio)", "Palazzo Vecchio: the Scrittoio of Cosimo I, 'accessible only thanks to passages concealed behind paintings'"),
          (72, 81, "garden cabinet (water stair)", "Tower of London, St Thomas's Tower: the stair past the bedchamber down to the water"),
          (83, 92, "lord's private bedchamber", "Versailles: Louis XV's private bedchamber (1738)"),
          (94, 98, "cabinet intérieur", "Versailles: the King's inner cabinet"),
          (100, 109, "PRIVATE DINING ROOM (flying table)", "Choisy / Petit Trianon: the 'tables volantes' (trace of a trapdoor in the parquet)"),
          (111, 119, "buffet (pantry)", "")]
    for (za, zb, nm, im) in GR:
        p.room(nm, "N", g0, g1, za, zb, f, im, zone="chamber")
        p.lights_in(g0, g1, za, zb, f, 4)
        if za > 72:
            p.door(150, f, za - 1, "south")
    p.door(150, f, 71, "south") if False else None
    p.door(150, f, 82, "south"); p.door(150, f, 93, "south"); p.door(150, f, 99, "south"); p.door(150, f, 110, "south")
    p.bed(155, f, 87, "east", role="lord") if False else None
    p.lectern(152, f, 56, "west"); p.chair(153, f, 56, "west")
    p.fill(g0, f + 1, 50, g0, f + 3, 62, "minecraft:bookshelf")
    # H6: the STAIR IN THE WALL lands at x 158 z 62..63 -> a jib panel at x 157 z 62 into the study
    # H7: the STUDIOLO (z 43..46, x 150..155) behind a jib panel in the study's wall z 48; the TESORETTO 3 x 3 behind a painting
    p.fill(g0, f, 42, g1, f + 7, 47, STONE)
    p.clear(150, 155, 43, 46, f, f + 3)
    PG.vault(p, 150, 155, 43, 46, f + 2, axis="x", wood="spruce", crown="beam", fill=STONE, deck=STONE, end_mat=STONE, deck_lights=0)
    p.fill(150, f, 47, 155, f + 3, 47, STONE)
    p.fill(152, f, 47, 152, f + 1, 48, AIR)
    p.jib2(152, f, 48); p.put(152, f, 47, AIR); p.put(152, f + 1, 47, AIR)
    for (cx, cz) in ((150, 43), (155, 43), (150, 46), (155, 46)):
        p.chest(cx, f, cz, "south" if cz == 43 else "north")
    p.put(153, f, 43, LIGHT); p.table(152, f, 45); p.put(153, f, 45, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "west"})
    p.room("STUDIOLO", "N", 150, 155, 43, 46, f, "Studiolo of Francesco I: windowless, barrel-vaulted, 'part-office, part-laboratory, part-hiding place'", hidden=True)
    p.hide("studiolo", 150, 155, 43, 47, f, f + 3)
    p.secret("H7a", "Studiolo behind the panelling", "Studiolo of Francesco I (1570-72): 'small painting-encrusted barrel-vaulted room'",
             "a jib panel in the private study's west wall (z 48) opens into the vaulted Studiolo; cupboards = chests", (152, f, 49), (152, f, 45), "hidden")
    # the Tesoretto (z 65..67, x 150..152) behind a secret painting in the wall z 64; the INNER HIDE (z 69..70, x 150..151)
    # behind a second painting in the Tesoretto's wall z 68 (Nicholas Owen: an outer hide concealing an inner one)
    p.fill(g0, f, 64, g1, f + 7, 70, STONE)
    p.clear(150, 152, 65, 67, f, f + 2)
    p.secret_painting(151, f, 64, "north") if False else None
    p.put(151, f, 64, AIR); p.put(150, f, 64, AIR); p.put(151, f + 1, 64, AIR); p.put(150, f + 1, 64, AIR)
    p.secret_painting(151, f, 64, "north")
    p.chest(150, f, 67, "north"); p.chest(152, f, 67, "north"); p.put(152, f, 65, "minecraft:gold_block")
    p.put(151, f + 2, 66, LIGHT)
    p.clear(150, 151, 69, 70, f, f + 2)
    p.secret_painting(151, f, 68, "north")
    p.chest(150, f, 70, "north"); p.put(151, f + 2, 69, LIGHT)
    p.room("TESORETTO", "N", 150, 152, 65, 67, f, "Palazzo Vecchio: the Tesoretto, 'hidden compartments… two hidden doorways'", hidden=True)
    p.room("inner hide", "N", 150, 151, 69, 70, f, "Nicholas Owen: 'a more easily discovered outer hiding place, which concealed an inner hiding place'", hidden=True)
    p.hide("tesoretto + inner hide", 150, 152, 64, 70, f, f + 2)
    p.secret("H7b", "Tesoretto behind a painting", "Palazzo Vecchio: Cosimo's Scrittoio 'accessible only thanks to passages concealed behind paintings'; the Tesoretto",
             "a pw:secret_painting (walk-through framed canvas) in the study's south wall", (151, f, 63), (151, f, 66), "hidden")
    p.secret("H7c", "Inner hide behind a second painting", "Nicholas Owen's double hide (outer hide concealing an inner one)",
             "a second pw:secret_painting in the Tesoretto's far wall", (151, f, 67), (151, f, 70) if False else (150, f, 70), "hidden")
    # H13: the FLYING TABLE — a 3 x 1 shaft from the serving room (B1) to the dining room floor, trapdoors flush in the
    # parquet, the table parked on its platform at the bottom (Choisy/Trianon; the lift is cancelled theatre, as at Versailles)
    for xx in (151, 152, 153):
        for ff in range(-2, f - 1):
            p.put(xx, ff, 104, AIR)
        p.put(xx, f - 1, 104, "minecraft:spruce_trapdoor", direction=0, open_bit=False, upside_down_bit=True)
        p.put(xx, -7, 104, "minecraft:spruce_slab", **{"minecraft:vertical_half": "top"}) if False else None
    for ff in range(-1, f - 1):
        for (sx, sz) in [(150, 104), (154, 104)] + [(xx, 103) for xx in range(150, 155)] + [(xx, 105) for xx in range(150, 155)]:
            if p.free(sx, ff, sz) or p.get(sx, ff, sz) in (DIRT,):
                p.put(sx, ff, sz, PANEL if ff >= 0 else STONE)
    p.table(152, -7, 104); p.table(151, -7, 104); p.table(153, -7, 104)
    p.table(151, f, 102); p.table(152, f, 102); p.table(153, f, 102)
    for xx in (151, 152, 153):
        p.chair(xx, f, 101, "south"); p.chair(xx, f, 106, "north")
    p.hide("flying table shaft", 151, 153, 104, 104, -7, f - 1)
    p.secret("H13", "Flying table (table volante)", "Choisy / Petit Trianon: tables laid below 'could appear in the center of the first-floor dining room'; 'Traces of a trapdoor remain'",
             "trapdoors flush in the dining-room floor over a 3 x 1 shaft to the serving room (B1)", (152, f, 103), (152, -7, 103), "hidden")
    # ---- the GARDEN CABINET's H11 water stair (laid later) and the garden-range doors
    # ---- consort side, cabinet zone: the ENTRESOL (lower 6..9, slab 10, upper 11..13) z 168..197
    e0, e1 = 168, 197
    p.fill(k0, F_ENT_SLAB, e0, k1, F_ENT_SLAB, e1, FLOOR)
    for w in (167, 174, 180, 186, 192, 198):
        p.fill(k0, f, w, k1, f + 7, w, PANEL)
    lower = [(168, 173, "méridienne", "Versailles: Marie-Antoinette's Méridienne"), (175, 179, "consort's library", "Versailles: the Queen's library"),
             (181, 185, "gold room (Cabinet Doré)", "Versailles: the Cabinet Doré"), (187, 191, "entresol stair", ""), (193, 197, "bath closet", "")]
    upper = [(168, 173, "billiard room", "Versailles: the Queen's billiard room (upper floor)"), (175, 179, "consort's private dining", "Versailles: the upper dining room"),
             (181, 185, "chambermaid's room 1", "Versailles: 'Six other rooms… reserved for the First Chambermaids' (8-12 m²)"),
             (187, 191, "chambermaid's room 2", "Versailles chambermaids"), (193, 197, "chambermaid's room 3", "Versailles chambermaids")]
    for (za, zb, nm, im) in lower:
        p.door(XW, f, (za + zb) // 2, "east")
        p.room(nm, "E", k0, k1, za, zb, f, im, zone="chamber", hidden=False)
        p.lights_in(k0, k1, za, zb, f, 3)
    for (za, zb, nm, im) in upper:
        p.room(nm, "E", k0, k1, za, zb, F_ENT, im, zone="chamber" if "chambermaid" not in nm else "quarters")
        p.lights_in(k0, k1, za, zb, F_ENT, 3)
        if za > 168:
            p.door(k1 - 1, F_ENT, za - 1, "south")
    for zb in (183, 189, 195):
        p.bed(142, F_ENT, zb - 1, "east", role="servant")
    p.table(140, F_ENT, 170); p.table(141, F_ENT, 170)
    # the entresol stair (straight flight 6 -> 11 along +z at x 139..140, z 187..191) through the slab
    p.flight(139, 187, f, 5, "south", width=2, across=(1, 0), mat="minecraft:spruce_stairs")
    p.clear(139, 140, 187, 191, F_ENT_SLAB, F_ENT_SLAB)
    p.clear(139, 140, 186, 186, F_ENT, F_ENT + 1) if False else None
    p.fill(k0, F_ENT, 192, k1, F_ENT + 2, 192, PANEL)
    p.clear(141, 142, 192, 192, F_ENT, F_ENT + 1); p.door(141, F_ENT, 192, "south")
    # the SUPPER CLOSET 4 x 4 (Holyrood: Mary's 'cabinet… just 12ft by 12ft') opens off the billiard room at x 141..144
    p.fill(k0, F_ENT, 167, k1, F_ENT + 2, 167, PANEL)
    p.notes.append("consort's entresol: méridienne, library, gold room, stair, bath | billiard, dining, 3 chambermaids")
    # H3 continued: the consort's private cabinets open off the spine (doors at x 136 above)
    # ---- consort side cabinet zone z 136..166 and 199..214: the consort's bath + wardrobe rooms
    for (za, zb, nm) in ((137, 151, "consort's bath"), (153, 166, "consort's wardrobe room"), (199, 214, "east back-stair lobby")):
        p.fill(k0, f, za - 1, k1, f + 7, za - 1, PANEL)
        p.door(XW, f, (za + zb) // 2, "east")
        p.room(nm, "N", k0, k1, za, zb, f, "", zone="chamber")
        p.lights_in(k0, k1, za, zb, f, 5)
    # ---- the GALLERY (garden range z 136..175, vaulted through the attic; furnaces in the stoking wall's gallery skin)
    p.fill(g0, f, 176, g1, f + 7, 176, PANEL)
    PG.vault(p, g0, g1, 136, 175, F_SLAB2, axis="z", wood="spruce", crown="beam", fill=ATTIC_FLOOR, deck=ATTIC_FLOOR, end_mat=STONE)
    p.carpet(g0 + 1, g1 - 1, 137, 174, f, "red")
    for zz in range(140, 175, 8):
        p.put(XST[1], f, zz, "minecraft:furnace", **{"minecraft:cardinal_direction": "west"})
        p.put(150, f + 6, zz, "minecraft:lantern", hanging=True) if False else None
    p.room("THE GALLERY", "N", g0, g1, 136, 175, f, "Hampton Court Great Gallery 36 x 7 x 8.5; Schönbrunn Great Gallery >40 x ~10", zone="commons")
    p.lights_in(g0, g1, 136, 175, f, 5)
    for (za, zb, nm) in ((177, 195, "music room"), (197, 214, "consort's garden cabinet")):
        p.fill(g0, f, za - 1, g1, f + 7, za - 1, PANEL)
        p.door(150, f, za - 1, "south")
        p.room(nm, "N", g0, g1, za, zb, f, "", zone="chamber")
        p.lights_in(g0, g1, za, zb, f, 5)
    for zl in (190, 205):
        p.fill(XST[0], f, zl, XST[1], f + 1, zl, AIR)
        p.door(XST[0], f, zl, "east"); p.door(XST[1], f, zl, "east")
    # the rear windows (gallery: tall glass in the rear wall's outer skin, the embrasure open)
    for zz in range(138, 175, 4):
        p.fill(XR[0], f + 1, zz, XR[1] - 1, f + 4, zz + 1, AIR)
        p.fill(XR[1], f + 1, zz, XR[1], f + 4, zz + 1, GLASS)
    for zz in list(range(84, 92, 4)) + list(range(101, 109, 4)) + list(range(179, 213, 6)):
        p.fill(XR[0], f + 1, zz, XR[1] - 1, f + 3, zz, AIR)
        p.fill(XR[1], f + 1, zz, XR[1], f + 3, zz, GLASS)


def wall_stair(p):
    """H6 — the STAIR IN THE WALL (Palazzo Vecchio: the Duke of Athens' 'small door in the alleyway, with a narrow
    staircase leading to the upper floors'; the Brienne stair 'carved into the thickness of the medieval wall'): a 1-wide
    straight stair inside the 3-thick rear wall (x 158) from the B1 passage (z 44..46) up to the ground landing (the alley
    door, an iron door opening from inside only) and on to the noble landing (a jib panel into the private study)."""
    x = 158
    p.fill(x, -8, 47, x, -8, 63, STONE)
    for i in range(7):                                         # -7 .. -1 rising +z at z 47..53
        z = 47 + i
        p.put(x, -7 + i, z, "minecraft:stone_brick_stairs", weirdo_direction=PG.STAIR_DIR["south"], upside_down_bit=False)
        for ff in range(-7 + i + 1, -7 + i + 4):
            p.put(x, ff, z, AIR)
    for z in (54, 55):                                         # the ground landing (feet 0)
        p.put(x, -1, z, STONE)
        for ff in (0, 1, 2):
            p.put(x, ff, z, AIR)
    for i in range(6):                                         # 0 .. 5 rising +z at z 56..61
        z = 56 + i
        p.put(x, i, z, "minecraft:stone_brick_stairs", weirdo_direction=PG.STAIR_DIR["south"], upside_down_bit=False)
        for ff in range(i + 1, i + 4):
            p.put(x, ff, z, AIR)
    for z in (62, 63):                                         # the noble landing (feet 6)
        p.put(x, 5, z, STONE)
        for ff in (6, 7, 8):
            p.put(x, ff, z, AIR)
    for z in (44, 45, 46):
        for ff in range(-7, -4):
            p.put(x, ff, z, AIR)
    p.put(x, -7 + 7, 54, STONE) if False else None
    p.iron_gate(XR[1], 0, 54, "east", inside=(x, 55))
    p.jib2(XR[0], F_NOBLE, 62)
    p.put(x, 7, 63, LIGHT); p.put(x, 1, 55, LIGHT) if False else None
    p.room("stair in the wall", "B1", x, x, 44, 63, -7, "Palazzo Vecchio: the Brienne stair 'carved into the thickness of the medieval wall'", hidden=True)
    p.hide("stair in the wall", x, x, 44, 63, -7, 8)
    p.secret("H6", "Stair in the wall (Duke of Athens / Brienne)", "Palazzo Vecchio 1342: the Duke's 'small door in the alleyway, with a narrow staircase leading to the upper floors'",
             "from the private study through a jib panel (x 157 z 62); down inside the rear wall to the alley door (iron, opens from inside) and on to the B1 cellars (iron door, opens from the stair side)",
             (156, F_NOBLE, 62), (158, F_NOBLE, 62), "hidden")
    p.secret("H6b", "Alley door of the wall stair", "Palazzo Vecchio: the Duke's door in the alleyway", "iron door in the rear wall's outer skin, button inside only",
             (158, 0, 55), (160, 0, 54), "oneway")
    p.secret("H6c", "Cellar door of the wall stair", "Palazzo Vecchio (the stair to the lower floor) [B1 link = design]", "iron door from the cellar corridor, button on the stair side only",
             (138, -7, 45), (136, -7, 45), "oneway")


def gov_bay(p):
    """the GOVERNMENT BAY (corps z 17..40, full depth) — the Doge's Palace SECRET ITINERARY in the museum's order:
    Pozzi (B1) -> the narrow stair (A turret) -> the Ducal Notary + Deputy (G) -> the Great Chancellor -> the Chamber of
    the Secret Chancellery (noble) -> the Torture Chamber -> the Piombi (attic, under the roof) -> the attic armoury ->
    'two long flights of stairs' down to the Chamber of the Inquisitors -> through the WARDROBE to the Council of Ten;
    the BRIDGE OF SIGHS from the Inquisitors' chamber to the prison tower across the canal."""
    x0, x1 = CORPS
    z0, z1 = GOV
    # ---- GROUND: the vestibule from the west wing (x 121..124), the notary, the deputy, the Great Chancellor, the archive
    p.fill(125, 0, z0, 125, 4, z1, STONE)
    p.fill(126, 0, 29, 144, 4, 29, STONE)
    p.room("government vestibule (G)", "G", 121, 124, z0, z1, 0, "", zone="threshold")
    for (xa, xb, nm, im) in ((126, 131, "Ducal Notary", "Doge's Palace: the two small rooms of the Ducal Notary"),
                             (133, 137, "Deputy to the Secret", "Doge's Palace: the Deputato alla Segreta"),
                             (139, 144, "Great Chancellor's office", "Doge's Palace: the Great Chancellor's office")):
        p.fill(xb + 1, 0, z0, xb + 1, 4, 28, STONE) if xb < 144 else None
        p.door(125, 0, 23, "east") if xa == 126 else p.door(xa - 1, 0, 23, "east")
        p.lectern(xa + 1, 0, 19, "south"); p.chest(xb, 0, 19, "west")
        p.room(nm, "G", xa, xb, z0, 28, 0, im, zone="workfloor")
        p.lights_in(xa, xb, z0, 28, 0, 3)
    for i in range(8):
        p.chest(127 + i * 2, 0, 39, "north")
    p.door(125, 0, 34, "east")
    p.room("chancellery archive (G)", "G", 126, 144, 30, z1, 0, "Doge's Palace: the Chancellery lockers 'from 1268'", zone="storeroom")
    p.lights_in(121, 144, z0, z1, 0, 5)
    # the H9 lobby (x 151..156 z 30..39 at ground) reached from the archive (the "narrow door on the ground floor")
    p.fill(XST[0], 0, 30, XST[1] + 3, 4, z1, STONE)
    p.clear(149, 156, 30, 39, 0, 4)
    p.fill(145, 0, 34, 148, 1, 34, AIR); p.door(145, 0, 34, "east")
    p.room("itinerary lobby (G)", "G", 149, 156, 30, 39, 0, "Doge's Palace: 'a narrow door on the ground floor'", hidden=False)
    p.fill(XST[0], 0, z0, XR[0] - 1, 4, 28, STONE)
    p.clear(CORPS[0], CORPS[0], 27, 28, 0, 2); p.clear(CORPS[0], CORPS[0], 27, 28, F_NOBLE, F_NOBLE + 2)
    # ---- NOBLE: vestibule | Council of Ten | WARDROBE wall | Inquisitors; Secret Chancellery | torture | itinerary zone
    f = F_NOBLE
    p.fill(125, f, z0, 125, f + 7, z1, PANEL)
    p.fill(126, f, 29, XR[0] - 1, f + 7, 29, PANEL)
    p.fill(137, f, z0, 137, f + 7, 28, PANEL)
    p.fill(144, f, 30, 144, f + 7, z1, PANEL); p.fill(150, f, 30, 150, f + 7, z1, PANEL)
    p.room("government vestibule (N)", "N", 121, 124, z0, z1, f, "", zone="threshold")
    p.door(125, f, 23, "east"); p.door(125, f, 34, "east")
    p.lights_in(121, 124, z0, z1, f, 5)
    for i in range(5):
        p.chair(127, f, 19 + i * 2, "east"); p.chair(135, f, 19 + i * 2, "west")
    p.table(131, f, 22); p.table(131, f, 23); p.table(131, f, 24)
    p.room("COUNCIL OF TEN", "N", 126, 136, z0, 28, f, "Doge's Palace: the Council of Ten", zone="chamber")
    p.lights_in(126, 136, z0, 28, f, 4)
    # the WARDROBE DOOR (H8): a wall of barrels (2 high) on the Inquisitors' side of x 137, one 'wardrobe door' = jib panels
    p.fill(138, f, 19, 138, f + 1, 27, "minecraft:barrel", facing_direction=5, open_bit=False)
    p.put(138, f, 23, AIR); p.put(138, f + 1, 23, AIR)
    p.jib2(137, f, 23)
    p.secret("H8", "The wardrobe door: Inquisitors -> Council of Ten", "Doge's Palace: the Inquisitors' room 'has a secret entrance behind a wooden wardrobe'",
             "a gap in the barrel wardrobe, its back a jib panel", (135, f, 23), (139, f, 23), "hidden")
    for i in range(3):
        p.table(146 + i, f, 20); p.chair(146 + i, f, 21, "north")
    p.room("CHAMBER OF THE INQUISITORS", "N", 138, 156, z0, 28, f, "Doge's Palace: the Chamber of the Inquisitors", zone="chamber", hidden=True)
    p.lights_in(139, 156, z0, 28, f, 4)
    p.fill(127, f, 39, 142, f + 2, 39, "minecraft:bookshelf")
    for i in range(6):
        p.chest(128 + i * 2, f, 31, "south")
    p.door(125, f, 34, "east")
    p.room("CHAMBER OF THE SECRET CHANCELLERY", "N", 126, 143, 30, z1, f, "Doge's Palace: 'the large and beautiful Chamber of the Secret Chancellery'", zone="workfloor")
    p.lights_in(126, 143, 30, z1, f, 4)
    p.door(144, f, 35, "east")
    p.put(147, f, 37, "minecraft:grindstone", attachment="standing", direction=0)
    p.fill(146, f + 2, 33, 148, f + 2, 33, "minecraft:chain") if False else None
    p.room("Torture Chamber", "N", 145, 149, 30, z1, f, "Doge's Palace: the Torture Chamber", zone="chamber", hidden=True)
    p.door(150, f, 35, "east")
    p.room("itinerary stair zone (N)", "N", 151, 156, 30, z1, f, "", hidden=True)
    p.lights_in(145, 156, 30, z1, f, 3)
    # the 'two long flights' from the attic armoury down into the Inquisitors' chamber (x 147..151 then x 153 along -z)
    p.flight(147, 27, f, 5, "east", width=1, mat="minecraft:spruce_stairs")
    p.fill(152, f + 4, 26, 153, f + 4, 27, PANEL)
    for ff in range(f + 5, f + 8):
        p.put(152, ff, 26, AIR); p.put(153, ff, 26, AIR); p.put(152, ff, 27, AIR); p.put(153, ff, 27, AIR)
    for i in range(4):
        z = 25 - i
        p.put(153, f + 5 + i, z, "minecraft:spruce_stairs", weirdo_direction=PG.STAIR_DIR["north"], upside_down_bit=False)
        for ff in range(f + 4, f + 5 + i):
            p.put(153, ff, z, PANEL)
        for ff in range(f + 6 + i, f + 9 + i):
            p.put(153, ff, z, AIR)
    p.fill(152, F_SLAB2, 22, 154, F_SLAB2, 27, AIR)
    p.fill(151, F_ATTIC, 22, 151, F_ATTIC, 27, "minecraft:spruce_fence"); p.fill(155, F_ATTIC, 22, 155, F_ATTIC, 27, "minecraft:spruce_fence")
    p.fill(152, F_ATTIC, 28, 154, F_ATTIC, 28, "minecraft:spruce_fence")
    # the BRIDGE OF SIGHS (H10): two parallel 1-wide corridors (z 22 and z 24) from the Inquisitors' rear wall across the
    # alley and the canal (x 160..170 = 11 long) to the prison tower's interrogation floor
    p.fill(ALLEY[0], f - 1, 21, CANAL[1], f + 3, 25, STONE)
    p.fill(ALLEY[0], f - 2, 21, CANAL[1], f - 2, 25, CHISEL)
    for zz in (22, 24):
        p.clear(XR[0], CANAL[1] + 2, zz, zz, f, f + 1)
        p.put(XR[0], f + 2, zz, STONE)
    for xx in range(ALLEY[0] + 1, CANAL[1], 3):
        p.put(xx, f + 1, 21, BARS); p.put(xx, f + 1, 25, BARS)
    p.fill(ALLEY[0], f + 4, 21, CANAL[1], f + 4, 25, "minecraft:stone_brick_slab", **{"minecraft:vertical_half": "bottom"})
    p.put(165, f + 1, 22, LIGHT); p.put(165, f + 1, 24, LIGHT)
    p.room("BRIDGE OF SIGHS (corridor 1)", "N", ALLEY[0], CANAL[1], 22, 22, f, "Doge's Palace 1600: arch span 11 m, 'two separate corridors that run next to each other'", hidden=True)
    p.room("BRIDGE OF SIGHS (corridor 2)", "N", ALLEY[0], CANAL[1], 24, 24, f, "Bridge of Sighs, second corridor", hidden=True)
    p.hide("bridge of sighs", XR[0], CANAL[1] + 2, 22, 24, f, f + 1)
    p.secret("H10", "Bridge of Sighs", "Doge's Palace 1600: enclosed stone bridge, span 11 m, two parallel corridors, to the New Prisons across the Rio di Palazzo",
             "from the Chamber of the Inquisitors (behind the wardrobe) across the alley and the canal to the tower's interrogation floor", (156, f, 22), (174, f, 22), "hidden")
    # ---- ATTIC: Piombi (4 cells under the lead roof, iron doors) | attic armoury | the H9 stair head
    a = F_ATTIC
    p.fill(126, a, 29, XR[0] - 1, a + 3, 29, STONE)
    p.fill(125, a, z0, 125, a + 3, z1, STONE)
    p.door(125, a, 38, "east")
    p.room("government attic vestibule", "A", 121, 124, z0, z1, a, "")
    for (cx, i) in ((127, 0), (131, 1), (135, 2), (139, 3)):
        p.fill(cx + 3, a, 30, cx + 3, a + 3, 35, STONE)
        p.fill(cx, a, 35, cx + 2, a + 3, 35, STONE)
        p.door(cx + 1, a, 35, "south", mat=IRON_DOOR)
        p.bed(cx, a, 31, "south", role="cell")
        p.room(f"Piombi cell {i + 1}", "A", cx, cx + 2, 30, 34, a, "Doge's Palace: the Piombi, 'in the attic, directly under the roof… covered with slabs of lead' (1591)", hidden=True)
    p.fill(126, a, 30, 126, a + 3, 35, STONE)
    p.room("Piombi walk", "A", 126, 143, 36, z1, a, "Doge's Palace: the Piombi", hidden=True)
    p.fill(144, a, 30, 144, a + 3, z1, STONE); p.door(144, a, 37, "east")
    for i in range(4):
        p.chest(146 + i * 2, a, z0 + 1, "south")
    p.put(150, a, 27, "minecraft:anvil", **{"minecraft:cardinal_direction": "west", "damage": "undamaged"})
    p.room("ATTIC ARMOURY", "A", 145, 156, z0, 28, a, "Doge's Palace: 'directly under the roof to the attic' (weapons)", hidden=True)
    p.fill(145, a, 29, 156, a + 3, 29, STONE); p.clear(152, 154, 29, 29, a, a + 2)
    p.room("itinerary stair head (A)", "A", 145, 156, 30, z1, a, "", hidden=True)
    p.lights_in(121, 156, z0, z1, a, 4)
    p.hide("secret itinerary (gov bay)", 138, 156, z0, z1, f, a + 3)
    p.secret("H9", "The Secret Itinerary (Pozzi -> notary -> Secret Chancellery -> torture -> Piombi -> armoury -> Inquisitors)",
             "Doge's Palace 'Itinerari segreti' leaflet: the museum's own order", "the narrow A-turret stair from the ground-floor lobby (a spruce door) to the Pozzi below and the itinerary rooms above",
             (149, 0, 34), (140, -7, 28), "disguised")
    p.later.append(lambda: p.spiral3(152, 33, -7, [0, 6, 15], "A_turret", "stone", ceiling=F_EAVE, label="H9 itinerary stair (narrow)",
                                     ring=STONE, ring_lo=-7, door_blocks=(0,)))


def chapel(p):
    """the CHAPEL (x 120..159, z 216..239): nave double height on the ground (Versailles: the Royal Chapel at the end of
    the north wing), a barrel vault, the ROYAL TRIBUNE at the noble level over the entrance end (x 121..136), reached from
    the spine (H15, jib) and from the east wing's noble corridor; the crypt below (B1)."""
    x0, x1 = CORPS
    z0, z1 = CHAPEL
    p.fill(x0, -2, z0, x1, -1, z1, STONE)
    p.fill(x0 + 1, -1, z0 + 1, x1 - 1, -1, z1 - 1, "minecraft:polished_andesite")
    p.shell(x0, x1, z0, z1, 0, 20, STONE)
    p.clear(x0 + 1, x1 - 1, z0 + 1, z1 - 1, 0, 20)
    deck = PG.vault(p, x0 + 1, x1 - 1, z0 + 1, z1 - 1, 10, axis="x", wood="spruce", crown="beam", fill=STONE, deck=STONE, end_mat=STONE)
    # gable roof along x (ridge along x) eave = deck + 1
    eave = deck + 1
    for k in range(12):
        f = eave + k
        if f > TOP:
            break
        p.fill(x0, f, z0 + k, x1, f, z0 + k, "pw:roof45_spruce", **{"minecraft:cardinal_direction": "north", "minecraft:vertical_half": "bottom"})
        p.fill(x0, f, z1 - k, x1, f, z1 - k, "pw:roof45_spruce", **{"minecraft:cardinal_direction": "south", "minecraft:vertical_half": "bottom"})
        for zz in range(z0 + k + 1, z1 - k):
            p.put(x0, f, zz, STONE); p.put(x1, f, zz, STONE)
    p.fill(x0 + 1, deck + 1, z0 + 1, x1 - 1, deck + 1, z1 - 1, AIR) if False else None
    for zz in range(z0 + 2, z1 - 1, 4):
        p.fill(x0, 2, zz, x0, 7, zz + 1, GLASS) if zz not in (226, 227, 228, 229) else None
    for xx in range(x0 + 20, x1 - 2, 4):
        p.fill(xx, 2, z0, xx + 1, 7, z0, GLASS) if False else None
        p.fill(xx, 2, z1, xx + 1, 7, z1, GLASS)
    # the entrance from the court (x 120, z 226..229) and from the east wing's corridor at ground (x 120, z 227..228)
    p.opening(x0, x0, 225, 230, 0, 4) if False else None
    p.door(x0, 0, 222, "west")
    # the tribune (noble level) x 121..136, the floor course at 5, a balustrade at x 137
    p.fill(x0 + 1, F_SLAB1, z0 + 1, 136, F_SLAB1, z1 - 1, FLOOR)
    p.fill(137, F_NOBLE, z0 + 1, 137, F_NOBLE, z1 - 1, "minecraft:spruce_fence")
    p.lights_in(x0 + 1, 136, z0 + 1, z1 - 1, F_NOBLE, 5)
    # the altar at the garden end, benches in the nave
    p.fill(x1 - 3, 0, z0 + 3, x1 - 1, 0, z1 - 3, SMOOTH)
    p.fill(x1 - 1, 1, z0 + 6, x1 - 1, 3, z1 - 6, "minecraft:chiseled_quartz_block")
    for xx in range(140, 152, 2):
        for zz in (220, 223, 232, 235):
            p.put(xx, 0, zz, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "east"})
    p.marker("station", "seat", 145, 0, 226)
    p.lights_in(x0 + 1, x1 - 1, z0 + 1, z1 - 1, 0, 6)
    p.room("CHAPEL (nave)", "G", 121, 158, 217, 238, 0, "Versailles Royal Chapel; Hofburg court church", zone="commons")
    p.room("ROYAL TRIBUNE", "N", 121, 136, 217, 238, F_NOBLE, "Versailles: the royal tribune facing the altar", zone="chamber")
    # the east wing corridor arrives at x 119 (ground: into the nave via a door; noble: onto the tribune)
    p.door(x0, 0, 227, "west"); p.door(x0, F_NOBLE, 227, "west")
    # a crypt stair? (U2: the crypt is reached from B1 only)


def attic(p):
    """the corps ATTIC (15..18): the attic corridor x 134..135 over the spine; four noble families over the state rooms;
    the lord's PETITS CABINETS + the SUPPER CLOSET 4 x 4 at the head of the vice stair (Versailles: Louis XV's 'even more
    private bedroom in the Petits Cabinets on the top of the palace'; Holyrood: the 12 x 12 ft supper cabinet); the
    SCHOOLROOM over the cabinet zone at the head of the children's stair; servants' garrets."""
    a = F_ATTIC
    x0 = XS[0]
    p.fill(XP, a, 42, XP, a + 3, 214, STONE); p.fill(XW, a, 42, XW, a + 3, 214, STONE)
    p.clear(XC[0], XC[1], 42, 214, a, a + 2)
    p.room("attic corridor", "A", XC[0], XC[1], 42, 214, a, "")
    p.lights_in(XC[0], XC[1] + 1, 42, 214, a, 6)
    # four families over the state rooms (along z, depth x 121..132), corridor wall x 133
    for za in (42, 84, 140, 182):
        family(p, f"corps attic z {za}", "z", za, XS[1], x0, XP, a, 4, "A", toward=-1)
    # the lord's petits cabinets (z 70..79 over the bedchamber's... the vice stair H4 lands here) + the supper closet
    p.fill(x0, a, 69, XS[1], a + 3, 69, STONE); p.fill(x0, a, 80, XS[1], a + 3, 80, STONE)
    p.fill(x0, a, 70, x0 + 3, a + 3, 70, AIR)
    p.fill(x0 + 4, a, 70, x0 + 4, a + 3, 74, PANEL); p.fill(x0, a, 75, x0 + 4, a + 3, 75, PANEL)
    p.clear(x0 + 4, x0 + 4, 72, 72, a, a + 1)
    p.door(x0 + 4, a, 72, "west")
    p.table(x0 + 1, a, 72); p.chair(x0 + 2, a, 72, "west")
    p.bed(126, a, 77, "east", role="lord") if False else None
    p.lights_in(x0, XS[1], 70, 79, a, 3)
    p.room("LORD'S PETITS CABINETS (attic)", "A", x0 + 5, XS[1], 70, 79, a, "Versailles: Louis XV's 'even more private bedroom in the Petits Cabinets on the top of the palace'", hidden=True)
    p.room("SUPPER CLOSET (4 x 4)", "A", x0, x0 + 3, 71, 74, a, "Holyrood: Mary's supper 'cabinet… just 12ft by 12ft' at the head of the vice stair", hidden=True)
    p.hide("lord's petits cabinets", x0, XS[1], 70, 79, a, a + 3)
    # the schoolroom over the cabinet zone (x 137..144, z 80..95) at the head of the children's stair (H5)
    p.fill(XK[0], a, 79, XK[1], a + 3, 79, STONE); p.fill(XK[0], a, 96, XK[1], a + 3, 96, STONE)
    p.door(XW, a, 92, "east")
    for i in range(3):
        p.table(139 + i * 2, a, 90); p.chair(139 + i * 2, a, 91, "north")
    p.lectern(141, a, 94, "north", station=False)
    p.room("SCHOOLROOM", "A", XK[0], XK[1], 80, 95, a, "John Jay Homestead: the day nursery 'for play and lessons'; brief: schoolroom in the attic", zone="workfloor")
    p.lights_in(XK[0], XK[1], 80, 95, a, 4)
    # servants' garrets over the cabinet zone, off the attic corridor; the back stairs' landing rooms at both ends
    p.fill(XK[0], a, 57, XK[1], a + 3, 57, PANEL); p.fill(XK[0], a, 198, XK[1], a + 3, 198, PANEL)
    p.door(XW, a, 45, "east"); p.door(XW, a, 202, "east")
    p.room("west back-stair landing (A)", "A", XK[0], XK[1], 42, 56, a, "")
    p.room("east back-stair landing (A)", "A", XK[0], XK[1], 199, 214, a, "")
    p.lights_in(XK[0], XK[1], 42, 56, a, 4); p.lights_in(XK[0], XK[1], 199, 214, a, 4)
    p.fill(XK[0], a, 127, XK[1], a + 3, 136, STONE)
    for (g0, g1) in ((58, 77), (97, 126), (137, 197)):
        for za in range(g0, g1 - 2, 4):
            p.fill(XK[0], a, za + 3, XK[1], a + 3, za + 3, PANEL)
            p.door(XW, a, za + 1, "east")
            p.bed(XK[1] - 1, a, za, "east", role="servant")
        p.room(f"garrets over the cabinet zone z {g0}", "A", XK[0], XK[1], g0, g1, a, "Versailles: chambermaids' rooms (8-12 m²)", zone="quarters")
    p.fill(XST[0], a, 42, XST[0], a + 3, 214, STONE)
    # the loft over the garden half (x 145..159) is sealed: lit, not entered (the gallery's vault rises through it)
    p.lights_in(XST[0], XR[1], 42, 214, a, 6)


def tower(p):
    """the PRISON TOWER ('New Prisons', Doge's Palace) x 171..186, z 17..32: 2-thick walls; floors at 5 / 10 / 16;
    ground = the gaolers' room (2 guard beds, a door to the privy garden), 6 = the interrogation floor (the Bridge of Sighs
    arrives), 11 = the new cells, 17 = the top; a C GRAND spiral from the B2 vault (the tower tunnel) to the top."""
    tx0, tx1, tz0, tz1 = TOWER
    p.fill(tx0, -2, tz0, tx1, -1, tz1, STONE)
    p.shell(tx0, tx1, tz0, tz1, 0, 21, STONE); p.shell(tx0 + 1, tx1 - 1, tz0 + 1, tz1 - 1, 0, 21, STONE)
    p.clear(tx0 + 2, tx1 - 2, tz0 + 2, tz1 - 2, 0, 21)
    for f in (5, 10, 16):
        p.fill(tx0 + 2, f, tz0 + 2, tx1 - 2, f, tz1 - 2, FLOOR)
    for f in (0, 6, 11, 17):
        p.lights_in(tx0 + 2, tx1 - 2, tz0 + 2, tz1 - 2, f, 4)
    p.bed(tx0 + 3, 0, tz0 + 3, "south", role="guard"); p.bed(tx0 + 3, 0, tz1 - 4, "north", role="guard")
    p.fill(tx1 - 1, 0, 28, tx1, 1, 28, AIR); p.door(tx1, 0, 28, "east")
    p.room("prison tower gaolers' room", "G", tx0 + 2, tx1 - 2, tz0 + 2, tz1 - 2, 0, "Doge's Palace: the New Prisons", zone="quarters")
    p.room("prison tower interrogation floor", "N", tx0 + 2, tx1 - 2, tz0 + 2, tz1 - 2, 6, "Doge's Palace: the New Prisons (the bridge arrives)", hidden=False)
    p.room("prison tower cells floor", "N", tx0 + 2, tx1 - 2, tz0 + 2, tz1 - 2, 11, "")
    p.room("prison tower top", "A", tx0 + 2, tx1 - 2, tz0 + 2, tz1 - 2, 17, "")
    for (cx, cz) in ((174, 19), (180, 19)):
        p.fill(cx, 11, cz + 2, cx + 2, 13, cz + 2, BARS)
    p.window(tx0, 8, 26, 0, 1, 1, 1); p.window(tx1, 8, 22, 0, 1, 1, 1); p.window(tx1, 13, 22, 0, 1, 1, 1); p.window(tx1, 19, 22, 0, 1, 1, 1)
    p.fill(tx0, 22, tz0, tx1, 22, tz1, CHISEL)
    for i in range(tx0, tx1 + 1, 2):
        p.put(i, 23, tz0, STONE); p.put(i, 23, tz1, STONE)
    for j in range(tz0, tz1 + 1, 2):
        p.put(tx0, 23, j, STONE); p.put(tx1, 23, j, STONE)
    p.roof_pyramid(tx0 + 1, tx1 - 1, tz0 + 1, tz1 - 1, 23)
    # the bridge arrives through the west walls at z 22 / 24
    for zz in (22, 24):
        p.clear(tx0, tx0 + 1, zz, zz, 6, 7)
    p.later.append(lambda: p.spiral3(176, 22, -12, [0, 6, 11, 17], "C_grand", "stone", ceiling=22, label="prison tower", ring=STONE, ring_lo=-12, ring_hi=-1))
    p.hide("prison tower vault + stair", 173, 184, 19, 30, -12, -1)


# ==================================================================================================== rear zone
def rear(p):
    """the privy garden (ice house, the escape pavilion, parterres) and the service court (kitchen block, little commons,
    laundry, smithy, stables + coach house, the well)."""
    # ---- ICE HOUSE (Hampton Court: 'a brick-lined well, 30 feet deep and 16 feet wide' under a thatched timber house):
    # well x 206..210, z 81..85, 9 deep (feet -9..-1), a drain from its floor to the escape tunnel; 2-door entrance passage
    ix0, ix1, iz0, iz1 = 204, 212, 79, 87
    p.fill(ix0 + 1, -10, iz0 + 1, ix1 - 1, -1, iz1 - 1, "minecraft:bricks")
    p.fill(ix0 + 2, -9, iz0 + 2, ix1 - 2, -1, iz1 - 2, AIR)
    p.fill(ix0 + 2, -9, iz0 + 2, ix1 - 2, -8, iz1 - 2, "minecraft:packed_ice")
    for ff in range(-7, 0):
        p.put(ix0 + 2, ff, iz0 + 4, "minecraft:ladder", facing_direction=5)
    # the drain (Nesvizh: the icehouse melt-water hole, mistaken for a secret passage): 1 x 1 from the well floor to the tunnel
    p.put(208, -10, 83, AIR); p.put(208, -11, 83, AIR)
    for zz in range(77, 83):
        p.put(208, -11, zz, AIR)
    p.drains.append({"building": "ice house (melt drain)", "gully": [208, 83], "sewer": "escape tunnel"})
    # the house: timber walls, a hay ('thatch') roof, the 2-door passage from the garden walk (west side)
    p.fill(ix0, 0, iz0, ix1, 3, iz1, "minecraft:spruce_planks")
    p.fill(ix0 + 1, 0, iz0 + 1, ix1 - 1, 3, iz1 - 1, AIR)
    p.fill(ix0 + 1, -1, iz0 + 1, ix1 - 1, -1, iz1 - 1, "minecraft:spruce_planks")
    p.fill(ix0 + 2, -1, iz0 + 2, ix1 - 2, -1, iz1 - 2, AIR)
    p.fill(ix0, 4, iz0, ix1, 4, iz1, "minecraft:hay_block", pillar_axis="y")
    p.fill(ix0 + 1, 5, iz0 + 1, ix1 - 1, 5, iz1 - 1, "minecraft:hay_block", pillar_axis="y")
    p.fill(ix0 - 3, -1, iz0 + 3, ix0 - 1, -1, iz0 + 5, "minecraft:spruce_planks")
    p.fill(ix0 - 3, 0, iz0 + 3, ix0 - 1, 3, iz0 + 5, "minecraft:spruce_planks")
    p.fill(ix0 - 3, 0, iz0 + 4, ix0 - 1, 1, iz0 + 4, AIR)
    p.door(ix0 - 3, 0, iz0 + 4, "east"); p.door(ix0, 0, iz0 + 4, "east")
    p.fill(ix0 - 3, 4, iz0 + 3, ix0 - 1, 4, iz0 + 5, "minecraft:hay_block", pillar_axis="y")
    p.put(ix0 + 1, 2, iz0 + 1, LIGHT)
    p.room("ICE HOUSE", "G", ix0 + 1, ix1 - 1, iz0 + 1, iz1 - 1, 0, "Hampton Court ice house: brick well 9.1 m deep x 4.9 m wide under a thatched house", zone="storeroom")
    p.room("ice well", "B1", ix0 + 2, ix1 - 2, iz0 + 2, iz1 - 2, -7, "Hampton Court ice house (9 deep)")
    # ---- the GARDEN PAVILION over the escape tunnel's exit (x 236..243, z 70..79): an open-sided pavilion, the trapdoor at
    # x 239 z 75 in its floor
    px0, px1, pz0, pz1 = 235, 243, 70, 80
    p.fill(px0, -1, pz0, px1, -1, pz1, "minecraft:polished_andesite")
    p.put(239, -1, 75, "minecraft:ladder", facing_direction=4)
    for (cx, cz) in ((px0, pz0), (px0, pz1), (px1, pz0), (px1, pz1), (px0, 75), (px1, 75)):
        p.column(cx, cz, 0, 4, "minecraft:stone_brick_wall") if False else p.fill(cx, 0, cz, cx, 4, cz, "minecraft:quartz_pillar", pillar_axis="y")
    p.fill(px0, 5, pz0, px1, 5, pz1, "minecraft:smooth_quartz")
    p.roof_pyramid(px0, px1, pz0, pz1, 6, wood="spruce") if False else p.roof_hip(px0, px1, pz0, pz1, 6)
    p.put(237, 0, 72, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "east"})
    p.room("GARDEN PAVILION (escape exit)", "G", px0 + 1, px1 - 1, pz0 + 1, pz1 - 1, 0, "Kremlin Tainitskaya: the hidden exit [composite]", zone="garden")
    p.secret("U1x", "Pavilion trapdoor (the escape tunnel's outer end)", "Kremlin Tainitskaya 'hidden exit'; Nesvizh myth NOT built (that hole was an icehouse drain)",
             "a spruce trapdoor in the pavilion floor over a ladder shaft 12 down into the escape tunnel (player-discovery from the garden)",
             (238, 0, 75), (239, -12, 75), "disguised")
    # parterres: low spruce-fence edges round the lawns (no leaves: the land job clears natural blocks)
    for (xa, xb, za, zb) in ((178, 196, 48, 58), (178, 196, 64, 74), (178, 196, 96, 122), (214, 232, 96, 122), (214, 230, 48, 58)):
        G.wall_ring(p, [(x, za) for x in range(xa, xb + 1)] + [(x, zb) for x in range(xa, xb + 1)] + [(xa, z) for z in range(za + 1, zb)] + [(xb, z) for z in range(za + 1, zb)], 0, "minecraft:mossy_stone_brick_wall")
    p.room("privy garden", "G", 172, 250, 36, 126, 0, "Hampton Court: the Privy Garden", zone="garden")
    # ---- KITCHEN BLOCK x 175..226, z 129..143 (great kitchen, scullery, larders, bakehouse), the U5 stair to its cellar
    kx0, kx1, kz0, kz1 = 175, 226, 129, 143
    p.fill(kx0, -2, kz0, kx1, -1, kz1, STONE); p.fill(kx0 + 1, -1, kz0 + 1, kx1 - 1, -1, kz1 - 1, SMOOTH)
    p.shell(kx0, kx1, kz0, kz1, 0, 6, STONE); p.clear(kx0 + 1, kx1 - 1, kz0 + 1, kz1 - 1, 0, 6)
    p.slab(kx0, kx1, kz0, kz1, 7, STONE); p.roof_hip(kx0, kx1, kz0, kz1, 8)
    p.windows_along(kz1, kx0, kx1, 1, h=2, pitch=4, axis="x")
    for xx in (194, 201, 213):
        p.fill(xx, 0, kz0 + 1, xx, 6, kz1 - 1, STONE); p.door(xx, 0, kz0 + 7, "east")
    for zz in (132, 136, 140):
        p.put(kx0 + 1, 0, zz, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": "east", "pw:phase": "cold"})
        p.fill(kx0 + 1, 1, zz, kx0 + 1, 9, zz, "pw:flue_stone_bricks", **{"pw:cap": 0}); p.put(kx0 + 1, 10, zz, "pw:flue_stone_bricks", **{"pw:cap": 1})
        p.marker("station", "hearth", kx0 + 2, 0, zz)
    for i in range(3):
        p.put(kx0 + 6 + i * 4, 0, kz1 - 1, "minecraft:smoker", **{"minecraft:cardinal_direction": "north"}); p.marker("station", "prep", kx0 + 6 + i * 4, 0, kz1 - 2)
    p.table(kx0 + 8, 0, 136); p.table(kx0 + 9, 0, 136); p.table(kx0 + 10, 0, 136); p.marker("station", "table", kx0 + 9, 0, 137)
    p.room("GREAT KITCHEN", "G", kx0 + 1, 193, kz0 + 1, kz1 - 1, 0, "Hampton Court kitchens; R3 §2.4 (Kerr) kitchen proportions", zone="kitchen")
    p.put(197, 0, kz0 + 2, "minecraft:cauldron", cauldron_liquid="water", fill_level=6)
    p.room("scullery", "G", 195, 200, kz0 + 1, kz1 - 1, 0, "", zone="kitchen")
    for i in range(3):
        p.barrel(203 + i * 3, 0, kz0 + 1); p.chest(203 + i * 3, 0, kz0 + 3, "south")
    p.room("larders", "G", 202, 212, kz0 + 1, kz1 - 1, 0, "", zone="storeroom")
    p.put(222, 0, kz1 - 1, "minecraft:furnace", **{"minecraft:cardinal_direction": "north"}); p.put(224, 0, kz1 - 1, "minecraft:furnace", **{"minecraft:cardinal_direction": "north"})
    p.marker("station", "oven", 223, 0, kz1 - 2)
    p.room("bakehouse", "G", 214, kx1 - 1, kz0 + 1, kz1 - 1, 0, "", zone="kitchen")
    for xx in (180, 207, 220):
        p.door(xx, 0, kz1, "south")
    p.lights_in(kx0 + 1, kx1 - 1, kz0 + 1, kz1 - 1, 0, 5)
    # the kitchen's cellar stair (to the U5 tunnel): a straight flight down from the kitchen floor at x 186..187
    for i in range(7):
        x = 182 + i
        for w in (139, 140):
            p.put(x, -7 + i, w, "minecraft:stone_brick_stairs", weirdo_direction=PG.STAIR_DIR["east"], upside_down_bit=False)
            for ff in range(-7 + i + 1, -7 + i + 4):
                p.put(x, ff, w, AIR)
    p.fill(181, -8, 139, 189, -8, 140, BRICK)
    p.fill(181, -1, 138, 189, 3, 138, STONE) if False else None
    p.fill(182, 0, 138, 189, 0, 138, "minecraft:spruce_fence"); p.fill(182, 0, 141, 189, 0, 141, "minecraft:spruce_fence")
    p.put(189, 0, 138, AIR); p.put(189, 0, 141, AIR)
    # ---- LITTLE COMMONS x 239..252, z 150..209: dining hall + 2 floors of lodgings (one servant each), B stair
    cx0, cx1, cz0, cz1 = 239, 252, 150, 209
    p.fill(cx0, -2, cz0, cx1, -1, cz1, STONE); p.fill(cx0 + 1, -1, cz0 + 1, cx1 - 1, -1, cz1 - 1, FLOOR)
    p.shell(cx0, cx1, cz0, cz1, 0, 14, STONE); p.clear(cx0 + 1, cx1 - 1, cz0 + 1, cz1 - 1, 0, 14)
    p.slab(cx0, cx1, cz0, cz1, 5, FLOOR); p.slab(cx0, cx1, cz0, cz1, 10, FLOOR)
    p.roof_hip(cx0, cx1, cz0, cz1, 15)
    p.windows_along(cx0, cz0, cz1, 1, h=2, pitch=4); p.windows_along(cx0, cz0, cz1, 6, h=2, pitch=4); p.windows_along(cx0, cz0, cz1, 11, h=2, pitch=4)
    p.door(cx0, 0, 160, "west"); p.door(cx0, 0, 190, "west")
    for zz in range(154, 199, 4):
        p.table(cx0 + 6, 0, zz); p.table(cx0 + 7, 0, zz); p.chair(cx0 + 5, 0, zz, "east"); p.chair(cx0 + 8, 0, zz, "west")
    p.marker("station", "seat", cx0 + 6, 0, 160)
    p.room("little commons (servants' hall)", "G", cx0 + 1, cx1 - 1, cz0 + 1, cz1 - 1, 0, "Versailles: the Grand Commun (service town)", zone="commons")
    p.lights_in(cx0 + 1, cx1 - 1, cz0 + 1, cz1 - 1, 0, 5)
    for f0 in (6, 11):
        p.fill(cx0 + 3, f0, cz0 + 1, cx0 + 3, f0 + 3, cz1 - 10, PANEL)
        for zz in range(cz0 + 1, cz1 - 13, 5):
            p.fill(cx0 + 4, f0, zz + 4, cx1 - 1, f0 + 3, zz + 4, PANEL)
            p.door(cx0 + 3, f0, zz + 2, "east")
            p.bed(cx0 + 5, f0, zz + 1, "east", role="servant"); p.chest(cx1 - 1, f0, zz + 1, "west")
        p.room(f"little commons lodgings f{f0}", "N" if f0 == 6 else "E", cx0 + 4, cx1 - 1, cz0 + 1, cz1 - 13, f0, "Versailles Grand Commun lodgings", zone="quarters")
        p.room(f"little commons corridor f{f0}", "N" if f0 == 6 else "E", cx0 + 1, cx0 + 2, cz0 + 1, cz1 - 1, f0, "")
        p.room(f"little commons stair hall f{f0}", "N" if f0 == 6 else "E", cx0 + 1, cx1 - 1, cz1 - 9, cz1 - 1, f0, "")
        p.clear(cx0 + 1, cx1 - 1, cz1 - 9, cz1 - 1, f0, min(f0 + 3, 14))
        p.lights_in(cx0 + 1, cx1 - 1, cz0 + 1, cz1 - 1, f0, 5)
    p.later.append(lambda: p.spiral3(cx0 + 5, cz1 - 6, 0, [6, 11], "B_tower", "spruce_plaster", ceiling=15, label="little commons", ring=PANEL))
    # ---- LAUNDRY x 175..186, z 200..212; SMITHY x 200..207, z 205..212; the WELL
    lx0, lx1, lz0, lz1 = 175, 186, 200, 212
    p.fill(lx0, -2, lz0, lx1, -1, lz1, STONE); p.fill(lx0 + 1, -1, lz0 + 1, lx1 - 1, -1, lz1 - 1, SMOOTH)
    p.shell(lx0, lx1, lz0, lz1, 0, 5, STONE); p.clear(lx0 + 1, lx1 - 1, lz0 + 1, lz1 - 1, 0, 5)
    p.slab(lx0, lx1, lz0, lz1, 6, STONE); p.roof_hip(lx0, lx1, lz0, lz1, 7)
    p.door(lx1, 0, 206, "east")
    for i in range(3):
        p.put(lx0 + 3, 0, lz0 + 3 + i * 3, "minecraft:cauldron", cauldron_liquid="water", fill_level=6)
    p.marker("station", "prep", lx0 + 4, 0, lz0 + 6)
    p.room("laundry", "G", lx0 + 1, lx1 - 1, lz0 + 1, lz1 - 1, 0, "Hampton Court 1537: the household's laundry", zone="workfloor")
    p.lights_in(lx0 + 1, lx1 - 1, lz0 + 1, lz1 - 1, 0, 4)
    mx0, mx1, mz0, mz1 = 200, 207, 205, 212
    p.fill(mx0, -2, mz0, mx1, -1, mz1, STONE); p.fill(mx0 + 1, -1, mz0 + 1, mx1 - 1, -1, mz1 - 1, COBBLE)
    p.shell(mx0, mx1, mz0, mz1, 0, 4, STONE); p.clear(mx0 + 1, mx1 - 1, mz0 + 1, mz1 - 1, 0, 4)
    p.slab(mx0, mx1, mz0, mz1, 5, STONE); p.roof_hip(mx0, mx1, mz0, mz1, 6)
    p.opening(mx0, mx0, mz0 + 3, mz0 + 4, 0, 3)
    p.put(mx1 - 1, 0, mz0 + 2, "minecraft:blast_furnace", **{"minecraft:cardinal_direction": "west"})
    p.put(mx1 - 1, 0, mz0 + 4, "minecraft:anvil", **{"minecraft:cardinal_direction": "west", "damage": "undamaged"})
    p.marker("station", "anvil", mx1 - 2, 0, mz0 + 4)
    p.room("smithy", "G", mx0 + 1, mx1 - 1, mz0 + 1, mz1 - 1, 0, "", zone="workfloor")
    p.lights_in(mx0 + 1, mx1 - 1, mz0 + 1, mz1 - 1, 0, 3)
    p.fill(209, -1, 174, 211, -1, 176, STONE); p.put(210, -1, 175, WATER)
    p.fill(209, 0, 174, 211, 0, 176, "minecraft:stone_brick_slab", **{"minecraft:vertical_half": "bottom"}); p.put(210, 0, 175, AIR)
    p.put(210, -2, 175, STONE)
    p.marker("port", "well", 210, 0, 177)
    p.room("service court", "G", 172, 234, 146, 198, 0, "", zone="yard")
    # ---- STABLES + COACH HOUSE x 190..235, z 220..231 (12 stalls, the grooms' loft over, a B stair in the coach house)
    sx0, sx1, sz0, sz1 = 190, 235, 220, 231
    p.fill(sx0, -2, sz0, sx1, -1, sz1, STONE); p.fill(sx0 + 1, -1, sz0 + 1, sx1 - 1, -1, sz1 - 1, COBBLE)
    p.shell(sx0, sx1, sz0, sz1, 0, 9, STONE); p.clear(sx0 + 1, sx1 - 1, sz0 + 1, sz1 - 1, 0, 9)
    p.slab(sx0, sx1, sz0, sz1, 5, FLOOR); p.roof_hip(sx0, sx1, sz0, sz1, 10)
    for xx in range(sx0 + 1, sx1 - 8, 3):
        p.fill(xx + 2, 0, sz1 - 4, xx + 2, 1, sz1 - 1, "minecraft:spruce_fence")
        p.put(xx + 1, 0, sz1 - 1, "minecraft:hay_block", pillar_axis="y")
    p.marker("station", "pen", sx0 + 6, 0, sz1 - 2); p.marker("station", "pen", sx0 + 20, 0, sz1 - 2)
    p.opening(sx0 + 5, sx0 + 8, sz0, sz0, 0, 4); p.opening(sx0 + 30, sx0 + 33, sz0, sz0, 0, 4)
    for i in range(4):
        p.bed(sx0 + 3 + i * 5, 6, sz0 + 2, "east", role="servant")
    p.room("stables + coach house", "G", sx0 + 1, sx1 - 1, sz0 + 1, sz1 - 1, 0, "Kedleston: the stables reached at ground level (U6: no palace-to-stables tunnel is documented)", zone="stable")
    p.room("grooms' loft", "N", sx0 + 1, sx1 - 1, sz0 + 1, sz1 - 1, 6, "", zone="quarters")
    p.lights_in(sx0 + 1, sx1 - 1, sz0 + 1, sz1 - 1, 0, 5); p.lights_in(sx0 + 1, sx1 - 1, sz0 + 1, sz1 - 1, 6, 5)
    p.later.append(lambda: p.spiral3(sx1 - 5, sz1 - 5, 0, [6], "B_tower", "oak", ceiling=10, label="coach house", ring=PANEL))


# ==================================================================================================== drains
def drains(p):
    """every structure drains to a sewer: a GULLY (iron bars flush in the paving at feet -1) over a 1 x 1 shaft through the
    ground into the sewer vault below (Hampton Court: chutes into 'brick culverts which ran under the moat and into the
    river'). The gully must stand over a dug sewer (checked)."""
    def gully(x, z, building, sewer):
        p.put(x, -1, z, BARS)
        for f in range(-8, -1):
            p.put(x, f, z, AIR)
        p.drains.append({"building": building, "gully": [x, z], "sewer": sewer})
    for zz in range(40, 216, 24):
        gully(14, zz if zz > 40 else 44, "gate range (court side)", "gate sewer")
    for xx in range(20, 116, 24):
        gully(xx, 42, "west wing (court side)", "west sewer")
        gully(xx, 213, "east wing (court side)", "east sewer")
    for zz in range(50, 214, 24):
        gully(116, zz, "corps (court side)", "corps sewer")
    for zz in range(24, 238, 24):
        gully(161, zz, "corps (rear) + canal quay", "rear sewer")
    gully(161, 228, "chapel (rear)", "rear sewer")
    gully(14, 127, "gatehouse", "trunk sewer") if False else gully(20, 127, "gatehouse (court side)", "trunk sewer")
    gully(175, 34, "prison tower", "tower tunnel (north)")
    for xx in (180, 200, 220):
        gully(xx, 146, "kitchen block", "kitchen sewer")
    gully(237, 152, "little commons", "commons sewer"); gully(237, 205, "little commons (south)", "commons sewer")
    gully(180, 216, "laundry", "yard sewer"); gully(204, 216, "smithy", "yard sewer"); gully(212, 216, "stables", "yard sewer"); gully(230, 216, "stables (east)", "yard sewer")
    gully(232, 75, "garden pavilion", "escape tunnel")
    gully(210, 172, "service court well overflow", "service sewer") if False else None


# ==================================================================================================== build
def build():
    p = Palace2()
    ground(p)
    gate_range(p)
    wing(p, WW[0], WW[1], west=True)
    wing(p, EW[0], EW[1], west=False)
    corps(p)
    corps_ground(p)
    corps_noble(p)
    cabinet_zone(p)
    gov_bay(p)
    chapel(p)
    attic(p)
    tower(p)
    rear(p)
    canal(p)
    plan_below(p)
    build_below(p)
    fit_below(p)
    wall_stair(p)
    drains(p)
    p.later.insert(0, lambda: secret_stairs(p))
    for fn in p.later:
        fn()
    finish(p)
    p.close_air()
    return p


def secret_stairs(p):
    """the A-turret secret stairs + the corps' back stairs + the grand stair (laid after every room)"""
    f = F_NOBLE
    # GRAND STAIR (C grand, stone) 0 -> 6 in the stair hall (open well; landing in front at the noble floor)
    p.spiral3(124, 125, 0, [6], "C_grand", "stone", ceiling=14, label="grand stair (C)", ring="minecraft:spruce_fence", ring_lo=6, ring_hi=6)
    # corps back stairs (B tower) in the cabinet zone beside the spine ends; doors open into the spine (x 136)
    for (za, zb) in ((49, 54), (206, 211)):                           # the spine-side wall opened where a door may go
        for fe in (0, 6):
            p.clear(XW, XW, za, zb, fe, fe + 2)
    p.spiral3(137, 50, -7, [0, 6, 15], "B_tower", "spruce_plaster", ceiling=F_EAVE, label="corps west back stair",
              door_ok=lambda x, fe, z: fe != 0 or x == XW, ring=PANEL, ring_lo=-7)
    p.spiral3(137, 207, -7, [0, 6, 15], "B_tower", "spruce_plaster", ceiling=F_EAVE, label="corps east back stair",
              door_ok=lambda x, fe, z: fe != 0 or x == XW, ring=PANEL, ring_lo=-7)
    # H4: the VICE STAIR (A turret) wardrobe (G) -> state bedchamber alcove (N) -> the petits cabinets / supper closet (attic)
    p.spiral3(131, 70, 0, [6, 15], "A_turret", "stone", ceiling=F_EAVE, label="H4 vice stair (narrow)", ring=PANEL,
              secret_exits=("foot", 6))
    p.secret("H4", "The vice stair: wardrobe -> state bedchamber -> petits cabinets + supper closet", "Holyrood 1566: 'the small vice stair' between the King's and the Queen's floors; Hampton Court: 'a spiral stone staircase rising from the ground floor' beside the bedchamber",
             "a jib panel in the turret's casing in the wardrobe and in the bedchamber's alcove; the top opens only into the attic cabinets",
             (129, F_NOBLE, 72), (126, F_ATTIC, 76), "hidden")
    p.hide("H4 vice stair", 130, 133, 69, 72, 0, 18)
    # H5: the CHILDREN'S STAIR (B tower) children's lodging (G, via the spine) -> garde-robe (N) -> schoolroom (A)
    p.spiral3(137, 84, 0, [6, 15], "B_tower", "spruce_plaster", ceiling=F_EAVE, label="H5 children's stair", ring=PANEL,
              door_ok=lambda x, fe, z: (fe != 0) or x == XW)
    p.secret("H5", "The children's stair: the night nursery -> the lord's garde-robe -> the schoolroom", "Hampton Court: Princess Mary lodged one floor below the king; Versailles: the Dauphin under the King [the link stair = design]",
             "a jib panel from the night nursery into the spine, the stair beside it; the family's only way between the nursery and the lord's garde-robe",
             (132, 0, 90), (139, F_NOBLE, 80), "disguised")
    p.hide("H5 children's stair", 136, 141, 83, 88, 0, 18)
    # H11: the WATER STAIR (A turret) J2 (B2) -> the water door (G, the alley/canal) -> the garden cabinet (N)
    p.clear(XR[0], XR[0], 74, 77, 0, 2)
    p.spiral3(155, 75, -12, [0, 6], "A_turret", "stone", ceiling=14, label="H11 water stair (narrow)", ring=STONE, ring_lo=-12,
              door_ok=lambda x, fe, z: (fe != 0) or x == XR[0])
    sp = p.spirals[-1]
    d0 = [e for e in sp["exits"] if e[1] == 0 and e[3] != "foot"]
    if d0:
        dz = d0[0][2]
        p.fill(XR[0] + 1, 0, dz, XR[1], 1, dz, AIR)
        p.put(XR[0] + 1, -1, dz, STONE); p.put(XR[1], -1, dz, STONE)
        p.iron_gate(XR[1], 0, dz, "east", inside=(XR[0] + 1, dz))
        p.fill(CANAL[0], -1, dz - 1, CANAL[0], -1, dz + 1, STONE)                 # the landing stage at the water's edge
        p.put(CANAL[0], 0, dz - 1, "minecraft:spruce_fence"); p.put(CANAL[0], 1, dz - 1, "minecraft:lantern", hanging=False)
        p.fill(XR[1], 2, dz, XR[1], 3, dz, BARS)
        p.secret("H11", "The water stair and the water gate", "Tower of London, St Thomas's Tower: 'The spiral staircase that leads past Edward's bedchamber goes all the way down to the river'; Traitors' Gate; Whitehall river steps",
                 "the garden cabinet's corner turret down past the water door (iron, opens from inside; a landing stage on the canal) to the escape junction J2",
                 (153, F_NOBLE, 74), (155, -12, 72) if False else (152, -12, 75), "hidden")
        p.secret("U3", "Water gate (iron door + landing stage on the canal)", "Tower of London: St Thomas's Tower water gate / Traitors' Gate",
                 "iron door in the rear wall at the canal's edge, button inside only", (XR[0] + 1, 0, dz), (160, 0, dz), "oneway")
    p.hide("H11 water stair", 154, 157, 74, 77, -12, 8)
    p.secret("U2", "Crypt passage", "Hofburg: the Augustinian church 'engulfed' by the palace, its Herzgruft", "the cellar corridor's east end through a door into the crypt under the chapel",
             (135, -7, 214), (135, -7, 218), "disguised")
    p.secret("U4", "The Dover junction J1 (three passages meet under the court)", "Dover Castle: 'three passages to three towers meet in a junction under the redan'",
             "the trunk (to the gatehouse stair), the north passage (to the west sewer -> the tower tunnel -> the prison tower) and the corps link (to the rear sewer -> J2)",
             (64, -12, 120), (70, -12, 127), "disguised")
    p.secret("U5", "Service tunnel kitchen -> serving room", "Kerr: the dinner route 'must not cross the track of family traffic'; basement 'Dinner-Stair… or… a Lift' [tunnel = design]",
             "down the kitchen's cellar stair, under the canal (3 high below the canal bed) to the serving room under the dining room",
             (183, -7, 130), (152, -7, 105), "disguised")
    p.secret("U7", "Wine cellar + ice house", "Whitehall: Henry VIII's vaulted wine cellar; Hampton Court ice house", "the cellar off the corps' cellar corridor; the ice house in the privy garden (2 doors)",
             (135, -7, 47), (125, -7, 46), "disguised")
    p.secret("H1", "The hidden spine corridor", "Versailles service rooms behind the state apartment; Kerr's service separation (R3 §2.3)",
             "2 wide x 3 high behind the state rooms on the ground and noble floors; servants enter by the back stairs and the servants' door; every state room opens to it by a jib panel",
             (136, 0, 120), (134, 6, 100), "disguised")


def finish(p):
    """last touches laid after every block: the royal tribune door through the chapel's end wall (H15)"""
    p.clear(XC[0], XC[1], 215, 216, F_NOBLE, F_NOBLE + 1)
    p.jib2(XC[0], F_NOBLE, 215); p.jib2(XC[1], F_NOBLE, 215)
    p.fill(XC[0], F_NOBLE + 2, 215, XC[1], F_NOBLE + 2, 216, STONE)


# ==================================================================================================== pieces, stages, manifests
def piece_name(r, c):
    return f"mvv_palace2_{r}{c}_a_r1"


def cut(p):
    out = {}
    sx, sy, sz = p.size
    L0 = p.st.layer0
    pal = p.st.palette
    for r in range(4):
        for c in range(4):
            ox, oz = r * PIECE, c * PIECE
            st = M.Structure((PIECE, sy, PIECE))
            cache = {}
            for x in range(PIECE):
                for y in range(sy):
                    base = ((ox + x) * sy + y) * sz + oz
                    for z in range(PIECE):
                        k = L0[base + z]
                        if k not in cache:
                            if k < 0:
                                cache[k] = st._pal(AIR, {})
                            else:
                                name, states, ver = pal[k]
                                cache[k] = st._pal(name, states, ver)
                        st.layer0[(x * sy + y) * PIECE + z] = cache[k]
            ents = []
            import copy as _copy
            for e in p.st.entities:
                pos = [cc.value for cc in e.value["Pos"].value]
                if ox <= pos[0] < ox + PIECE and oz <= pos[2] < oz + PIECE:
                    ee = _copy.deepcopy(e)
                    ee.value["Pos"] = M.lst(M.FLOAT, [M.f(pos[0] - ox), M.f(pos[1]), M.f(pos[2] - oz)])
                    ents.append(ee)
            st.entities = ents
            marks = [dict(m, cell=[m["cell"][0] - ox, m["cell"][1], m["cell"][2] - oz]) for m in p.markers
                     if ox <= m["cell"][0] < ox + PIECE and oz <= m["cell"][2] < oz + PIECE]
            out[(r, c)] = (st, marks)
    return out


def light_s0(path, keep_from=-14):
    """the palace II LIGHT plot stage (palace_light_s0's rule, extended for the basements): keep every non-air cell at
    feet >= keep_from and every AIR cell below grade (feet -14..-2: the cellars, tunnels, sewers and shafts must be dug by
    the stage); everything else becomes structure void (the land job clears the sky over the box)."""
    st = M.Structure.from_bytes(path.read_bytes())
    full = path.with_name(path.stem + "_full.mcstructure")
    if not full.exists():
        full.write_bytes(path.read_bytes())
    sx, sy, sz = st.size
    kept = 0
    for x in range(sx):
        for y in range(sy):
            feet = y - 15
            for z in range(sz):
                i = st.index(x, y, z)
                k = st.layer0[i]
                if k < 0:
                    continue
                name = st.palette[k][0]
                if name == VOID:
                    st.layer0[i] = -1; st.layer1[i] = -1; continue
                if (feet >= keep_from and name != AIR) or (keep_from <= feet <= -2 and name == AIR):
                    kept += 1
                    continue
                st.layer0[i] = -1; st.layer1[i] = -1
    path.write_bytes(st.to_bytes())
    return kept


def write_all(p):
    import civ_stages as CS
    OUT.mkdir(parents=True, exist_ok=True)
    for d in ("structures", "manifests", "stages"):
        (OUT / d).mkdir(exist_ok=True)
    pieces = cut(p)
    group = {"name": "palace2", "grid": "r = x // 64 (0 = gate side), c = z // 64", "size": [N, p.size[1], N], "datum_y": 15, "pieces": [], "spirals": p.spirals,
             "secrets": p.secrets, "drains": p.drains, "oneway": p.oneway}
    for (r, c), (st, marks) in pieces.items():
        stem = piece_name(r, c)
        ox, oz = r * PIECE, c * PIECE
        sp = (OUT / "structures" / f"{stem}.mcstructure")
        sp.write_bytes(st.to_bytes())
        sx, sy, sz = st.size
        blocks = []
        for x in range(sx):
            for y in range(sy):
                for z in range(sz):
                    e = st.get(x, y, z)
                    if e is not None and e[0] != AIR:
                        blocks.append([x, y, z, e[0], {k: v.value for k, v in e[1].items()}])
        beds = [dict(b, x=b["x"] - ox, z=b["z"] - oz) for b in p.bed_roles
                if ox <= b["x"] < ox + PIECE and oz <= b["z"] < oz + PIECE and str(p.get(b["x"], b["feet"], b["z"])).endswith(":bed")]
        spirals = [dict(s, well=[s["well"][0] - ox, s["well"][1] - oz, s["well"][2] - ox, s["well"][3] - oz])
                   for s in p.spirals if ox <= s["well"][0] < ox + PIECE and oz <= s["well"][1] < oz + PIECE]
        man = {"name": f"pw:{stem}", "size": [sx, sy, sz], "datum_y": 15, "blocks": blocks, "entities": marks,
               "bed_roles": beds, "spirals": spirals, "group": "pw:mvv_palace2", "grid": [r, c]}
        (OUT / "manifests" / f"{stem}.json").write_text(json.dumps(man, separators=(",", ":")))
        res, _floors = CS.cut(str(sp), str(OUT / "stages"))
        kept = light_s0(OUT / "stages" / f"{stem}_s0.mcstructure")
        roles = {}
        for b in beds:
            roles[b["role"]] = roles.get(b["role"], 0) + 1
        group["pieces"].append({"stem": stem, "grid": [r, c], "origin": [ox, oz], "blocks": len(blocks), "markers": len(marks),
                                "beds": roles, "s0_light_cells": kept, "stages": [list(x) for x in res]})
        print(f"  {stem}: {len(blocks)} blocks, {len(marks)} markers, beds {roles}, s0 light {kept}")
    (OUT / "palace2_group.json").write_text(json.dumps(group, indent=1, default=str))
    return group


if __name__ == "__main__":
    import time
    t = time.time()
    p = build()
    print("model", p.size, "lights", p.lights, "beds", p.beds, "markers", len(p.markers), "rooms", len(p.rooms),
          "secrets", len(p.secrets), "spirals", len(p.spirals), f"{time.time() - t:.1f}s")
    if p.child_bed_clash:
        print("CHILD BED CLASH", p.child_bed_clash[:6])
    for n in p.notes:
        print("  -", n)
    if "--write" in sys.argv:
        write_all(p)
