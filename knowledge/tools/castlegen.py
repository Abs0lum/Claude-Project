#!/usr/bin/env python3
"""castlegen.py — CASTLES for CIVITAS (D-C572; his 23:02 / 23:11 CT 10-04, K1-K8 08:43 CT 10-05, WATER law): to-scale
castles in two period SKINS with FORCED VARIETY by seed, cut into 64 x 64 pieces the clock lays as one rotated group (the
palace's way) and into five HEIGHT-BAND stages per piece (light plot stage).

  skin A  "concentric" (13th c., Beaumaris / Harlech type): an outer curtain (3 thick) and an inner curtain (5 thick, an
          intra-mural passage), the inner higher, D / round / square towers <= 32 apart, twin-towered gatehouses (the outer
          one holds the constable, the inner one the lord's apartments), no keep; a wet / dry / no moat by seed with a
          berm; barbican; posterns through both rings; bailey buildings in the outer ward.
  skin B  "Bodiam quadrangle" (14th c.): a compact quadrangle (56..64 square, 5-thick curtain with a mural passage) whose
          ranges stand against the curtain round a ~28 court — hall, kitchen, chapel, lodgings, the gatehouse — round corner
          towers, square mid towers, the donjon (Hedingham-size, double-height hall) at the keep corner; the quadrangle
          stands in a lake (wet) or a dry ditch inside a walled BASE COURT (stables, smithy, granary, bakehouse, garrison).
  size    "lord" (town III) · "grand" (city III; the palace program is NOT built yet — a bigger lord program, 60 men)

FRAME (civgen): x = depth from the town side (x 0 = the gate side, K6: the gate faces the square), z = frontage, feet =
height over the ward (feet 0 = standing on the ward; feet -1 the paving). The box is a multiple of 64 (v0.3, F1): the
seed's content is CENTRED in it, so every piece is written whole.

UNDERGROUND (WATER law, "ALL structures include subsurface infrastructure"; the 1006 sewer contract): the trench is the
street trench's level — channel feet -14..-13 (y1..y2 of the box), bed -15. Levels: paving -1 · cellars and basements
-4..-2 (floor -5) · culverts -8..-7 (floor -9) · trench -14..-13. Every ward gully (16 x 16), garderobe chute, kitchen /
stable / smithy gully and the dry ditch's gullies fall by culvert to the castle's ring trench, which leaves by a trunk
under the gate to the TOWN junction (port:sewer marker) and by a trunk to the rear OUTFALL (iron-bar grate in the upper
cell). The well is a lined 1 x 1 shaft of water sources from the well head to the trench level with a feeder to the
trench (D-C533). A wet moat / lake overflows through the SLUICE TOWER (Caerphilly): a 1-wide lip at water level -> a
3-step race -> a basin with a fountain jet -> a drop shaft -> a culvert at trench level -> the outfall; its upstream end
carries the FEED PORT (a lined race to the box edge closed by a sluice board) for the clock's captured water.

Usage: castlegen.py --skin=A|B --size=lord|grand --seed=N [--write] [--render] [--verify] [--out=DIR]
       castlegen.py --all  [--out=DIR]      (the ten varieties: build, verify, write pieces + stages, render, sheet)
Outputs: <out>/<stem>/{structures,manifests,stages}/ + <stem>/castle.json; renders in _docs/castle/v0_4/."""
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import civgen as G  # noqa: E402
import mcstructure as M  # noqa: E402

VERSION = "0.4 (castle 231)"
STG = Path("/home/claude/_staging/castle231")
DOCS = Path("/home/claude/_docs/castle")
RENDERS = DOCS / "v0_4"
AIR, VOID, WATER = "minecraft:air", "minecraft:structure_void", "minecraft:water"
DIRT, GRASS, GRAVEL, COBBLE, PATH = "minecraft:dirt", "minecraft:grass_block", "minecraft:gravel", "minecraft:cobblestone", "minecraft:grass_path"
GLASS, LIGHT, POST, PANEL, FLOOR = "minecraft:glass_pane", "minecraft:light_block_14", "minecraft:spruce_log", "minecraft:spruce_planks", "minecraft:oak_planks"
BARS, LINING, SMOOTH, STONEBR = "minecraft:iron_bars", "minecraft:stone_bricks", "minecraft:smooth_stone", "minecraft:stone_bricks"
RAIL, DECK = "minecraft:oak_fence", "minecraft:spruce_planks"
VEC = {"east": (1, 0), "west": (-1, 0), "south": (0, 1), "north": (0, -1)}
OPP = {"east": "west", "west": "east", "south": "north", "north": "south"}
DIRNAME = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}
BED_DIR = {"south": 0, "west": 1, "north": 2, "east": 3}
STAIR_DIR = {"east": 0, "west": 1, "south": 2, "north": 3}
F_TRENCH, F_CULVERT, F_CELLAR = -14, -8, -4          # the lower cell of each channel / the cellar's standing level
DATUM_Y = 15


def arg(name, default):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return default if v is None else type(default)(v)


def ceil64(n):
    return ((n + 63) // 64) * 64


# ------------------------------------------------------------------------------------------------ the variety
MATERIALS = [  # (curtain, dressing, tower, parapet) — stone families the kit knows
    ("minecraft:stone_bricks", "minecraft:chiseled_stone_bricks", "minecraft:stone_bricks", "minecraft:stone_brick_slab"),
    ("minecraft:cobblestone", "minecraft:stone_bricks", "minecraft:cobblestone", "minecraft:cobblestone_slab"),
    ("minecraft:mossy_stone_bricks", "minecraft:stone_bricks", "minecraft:stone_bricks", "minecraft:stone_brick_slab"),
    ("minecraft:polished_andesite", "minecraft:chiseled_stone_bricks", "minecraft:andesite", "minecraft:andesite_slab"),
    ("minecraft:stone_bricks", "minecraft:polished_diorite", "minecraft:mossy_stone_bricks", "minecraft:stone_brick_slab"),
]
ROOFS = ["spruce", "oak", "thatch"]


class Variety:
    """everything the seed decides, drawn once and kept (two castles never share a seed; a town keeps its seed + skin).
    v0.3 draws are APPENDED after the v0.2 draws, so a seed keeps its v0.2 character (plan, towers, heights, stone)."""

    def __init__(self, skin, size, seed):
        r = random.Random(seed * 7919 + (1 if skin == "A" else 2) * 104729 + len(size))
        self.skin, self.size_name, self.seed = skin, size, seed
        base = r.choice([128, 144, 160]) if size == "lord" else r.choice([224, 256, 288])
        self.CW = base                                                  # the seed's content width (v0.2's box)
        self.plan = r.choice(["square", "rect", "poly5", "poly6", "poly7"]) if skin == "A" else r.choice(["square", "rect", "rect", "poly5"])
        self.towers = r.choice([4, 6, 8]) if skin == "A" else r.choice([4, 4, 5, 6])
        self.tower_shape = r.choice(["round", "d", "square"]) if skin == "A" else r.choice(["round", "square"])
        self.outer_h = r.choice([8, 9, 10])
        self.inner_h = self.outer_h + r.choice([4, 5, 6])
        self.keep_corner = r.choice([0, 1, 2, 3])
        self.gate_offset = r.choice([-0.18, -0.08, 0.0, 0.08, 0.18])
        self.moat = r.random() < (0.8 if skin == "A" else 0.6)
        self.barbican = r.random() < 0.5 and self.moat
        self.mat = r.choice(MATERIALS)
        self.roof = r.choice(ROOFS)
        self.hall_roof = r.choice(["hip", "gable"])
        self.rect_long_x = r.random() < 0.5
        self.tower_caps = r.random() < 0.5
        # ---- v0.3 draws
        self.moat_kind = "wet" if self.moat else r.choice(["dry", "none"])
        self.moat_w = r.choice([5, 6, 7])
        self.sluice_side = r.choice([-1, 1])                            # the downhill rear corner: z small (-1) / z large (+1)
        self.portcullises = 2 if size == "lord" else 3
        self.quad = r.choice([56, 60, 64]) if size == "lord" else r.choice([76, 80])
        self.lake_w = r.choice([9, 10, 12]) if size == "lord" else r.choice([12, 14])
        self.rng = r
        lord = size == "lord"
        if skin == "A":
            need = 16 if (self.moat_kind != "none" or self.barbican) else 0
            self.W = ceil64(self.CW + 2 * need)
        else:
            self.W = 192 if lord else (256 if base < 288 else 320)
        self.o = (self.W - self.CW) // 2 if skin == "A" else 0

    def describe(self):
        return (f"skin {self.skin} {self.size_name} seed {self.seed}: box {self.W} (content {self.CW if self.skin == 'A' else 'quad ' + str(self.quad)}), plan {self.plan}, "
                f"{self.tower_shape} towers, curtain {str(self.outer_h) + '/' + str(self.inner_h)} high, "
                f"moat {self.moat_kind}{' w' + str(self.moat_w if self.skin == 'A' else self.lake_w) if self.moat_kind != 'none' else ''}, barbican {self.barbican}, "
                f"stone {self.mat[0].split(':')[1]}, roof {self.roof}, keep corner {self.keep_corner if self.skin == 'B' else '-'}")


# ------------------------------------------------------------------------------------------------ a building's local frame
class Frame:
    """a rectangle with a door side: u = depth from the door wall (u 0) inward, v = along the door wall. Builders write
    in (u, v) once and the frame turns it to the world for any of the four door sides."""
    IN = {"x0": "east", "x1": "west", "z0": "south", "z1": "north"}
    ALONG = {"x0": "south", "x1": "south", "z0": "east", "z1": "east"}

    def __init__(self, rect, side):
        self.rect, self.side = rect, side
        x0, x1, z0, z1 = rect
        self.D, self.L = (x1 - x0 + 1, z1 - z0 + 1) if side in ("x0", "x1") else (z1 - z0 + 1, x1 - x0 + 1)

    def w(self, u, v):
        x0, x1, z0, z1 = self.rect
        return {"x0": (x0 + u, z0 + v), "x1": (x1 - u, z0 + v), "z0": (x0 + v, z0 + u), "z1": (x0 + v, z1 - u)}[self.side]

    def d(self, name):
        """local direction -> world: in (u+), out (u-), vp (v+), vm (v-)"""
        return {"in": self.IN[self.side], "out": OPP[self.IN[self.side]], "vp": self.ALONG[self.side], "vm": OPP[self.ALONG[self.side]]}[name]

    def axis(self, along):
        """the world axis ('x' / 'z') of local 'u' or 'v'"""
        ux = self.side in ("x0", "x1")
        return ("x" if ux else "z") if along == "u" else ("z" if ux else "x")

    def wrect(self, u0, u1, v0, v1):
        a, b = self.w(u0, v0), self.w(u1, v1)
        return min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])


# ------------------------------------------------------------------------------------------------ the model
class Castle(G.Building):
    def __init__(self, v):
        self.v = v
        self.TOP = 44 if v.size_name == "lord" else 52
        super().__init__("pw:mvv_castle", v.W, v.W - 1, top_feet=self.TOP)
        self.lights = 0
        self.beds = 0
        self.bed_roles = []
        self.notes = []
        self.curtain, self.dress, self.tower_mat, self.parapet = v.mat
        self.poi = {"gate_out": None, "ward": [], "rooms": {}, "beds": [], "towers": [], "walk": set(), "mural": set(), "sealed": set(),
                    "inside_poly": [], "footprints": [], "gates": [], "posterns": [], "hidden": []}
        self._room_n = {}
        self.spirals = []
        self.occ = set()                       # cells (x, z) no range may stand on (walls, towers, footprints + margin)
        # the underground and the water law
        self.channel = set()                   # every carved underground channel cell (lined at the end)
        self.heads = []                        # drain heads: (x, f, z, kind) — the top cell of each head's fall
        self.trench = set()                    # trench cells (x, z) at F_TRENCH
        self.water_ok = set()                  # cells where a water SOURCE is allowed (moat, lake, well shaft, fountain jet)
        self.infra = {"junction": None, "outfall": None, "feed": None, "sluice": None, "well": None, "fountain": [], "chutes": 0, "gullies": 0}
        self.skyway = []
        self.reserved = set()                  # underground columns no culvert may cross (the well shaft and its lining)

    # ---------------------------------------------------------------- clipped block writes
    def inbox(self, x, z):
        return 0 <= x < self.v.W and 0 <= z < self.v.W

    def put(self, x, feet, z, name, waterlogged=False, **states):
        if self.inbox(x, z) and self.bottom <= feet <= self.TOP:
            if name == WATER and not states:
                states = {"liquid_depth": 0}
            super().put(x, feet, z, name, waterlogged, **states)

    def get(self, x, feet, z):
        if not (self.inbox(x, z) and self.bottom <= feet <= self.TOP):
            return None
        return super().get(x, feet, z)

    def fill(self, x0, f0, z0, x1, f1, z1, name, **states):
        xa, xb = max(0, min(x0, x1)), min(self.v.W - 1, max(x0, x1))
        za, zb = max(0, min(z0, z1)), min(self.v.W - 1, max(z0, z1))
        fa, fb = max(self.bottom, min(f0, f1)), min(self.TOP, max(f0, f1))
        if xa > xb or za > zb or fa > fb:
            return
        if name == WATER and not states:
            states = {"liquid_depth": 0}
        super().fill(xa, fa, za, xb, fb, zb, name, **states)

    def room(self, kind, x0, x1, z0, z1, feet):
        n = self._room_n.get(kind, 0)
        self._room_n[kind] = n + 1
        self.poi["rooms"][f"{kind}_{n}"] = (min(x0, x1), max(x0, x1), min(z0, z1), max(z0, z1), feet)

    def block_occ(self, x0, x1, z0, z1, margin=2):
        for x in range(x0 - margin, x1 + margin + 1):
            for z in range(z0 - margin, z1 + margin + 1):
                self.occ.add((x, z))

    # ---------------------------------------------------------------- primitives
    def shell(self, x0, x1, z0, z1, f0, f1, mat):
        self.fill(x0, f0, z0, x0, f1, z1, mat); self.fill(x1, f0, z0, x1, f1, z1, mat)
        self.fill(x0, f0, z0, x1, f1, z0, mat); self.fill(x0, f0, z1, x1, f1, z1, mat)

    def clear(self, x0, x1, z0, z1, f0, f1):
        self.fill(x0, f0, z0, x1, f1, z1, AIR)

    def light(self, x, feet, z):
        self.put(x, feet, z, LIGHT); self.lights += 1

    def slab(self, x0, x1, z0, z1, feet, mat, light_every=6, light_up=3):
        self.fill(x0, feet, z0, x1, feet, z1, mat)
        for x in range(min(x0, x1) + 2, max(x0, x1) - 1, light_every):
            for z in range(min(z0, z1) + 2, max(z0, z1) - 1, light_every):
                self.light(x, feet + light_up, z)

    def door(self, x, feet, z, facing, mat="minecraft:spruce_door", hinge=0):
        self.put(x, feet, z, mat, **{"minecraft:cardinal_direction": facing, "door_hinge_bit": hinge, "open_bit": 0, "upper_block_bit": 0})
        self.put(x, feet + 1, z, mat, **{"minecraft:cardinal_direction": facing, "door_hinge_bit": hinge, "open_bit": 0, "upper_block_bit": 1})

    def window(self, x, feet, z, dx, dz, w=1, h=2):
        for i in range(w):
            for j in range(h):
                self.put(x + dx * i, feet + j, z + dz * i, GLASS)

    def bed(self, x, feet, z, head_dir, role="servant", step=None, office=None):
        """role: lord | noble | servant | guard | clerk | child (the palace's ROLE BEDS, his 14:07); step: the garrison step
        G1..G4 a guard bed belongs to (K2: beds are built at tier time, men are recruited later); office: the household post"""
        dx, dz = VEC[head_dir]; d = BED_DIR[head_dir]
        self.put(x, feet, z, "minecraft:bed", direction=d, head_piece_bit=False, occupied_bit=False)
        self.put(x + dx, feet, z + dz, "minecraft:bed", direction=d, head_piece_bit=True, occupied_bit=False)
        self.beds += 1; self.marker("station", "bed", x, feet, z)
        self.poi["beds"].append((x, feet, z))
        self.bed_roles.append({"x": x, "feet": feet, "z": z, "role": role, "step": step, "office": office})

    def barrel(self, x, feet, z):
        self.put(x, feet, z, "minecraft:barrel", facing_direction=1, open_bit=False)

    def table(self, x, feet, z, wood="dark_oak"):
        self.put(x, feet, z, f"pw:furn_table_{wood}", **{"pw:n": False, "pw:e": False, "pw:s": False, "pw:w": False})

    def furn(self, kind, x, feet, z, facing, wood="spruce"):
        self.put(x, feet, z, f"pw:furn_{kind}_{wood}", **{"minecraft:cardinal_direction": facing})

    def hearth(self, x, feet, z, facing, flue_to=None):
        self.put(x, feet, z, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": facing, "pw:phase": "cold"})
        if flue_to is not None:
            self.fill(x, feet + 1, z, x, flue_to, z, "pw:flue_stone_bricks")
        self.marker("station", "hearth", x, feet, z)

    def stairs(self, x, feet, z, high_side, mat="minecraft:spruce_stairs"):
        self.put(x, feet, z, mat, weirdo_direction=STAIR_DIR[high_side], upside_down_bit=False)

    def lantern(self, x, feet, z, hanging=False):
        self.put(x, feet, z, "minecraft:lantern", hanging=hanging); self.lights += 1

    def punch(self, x0, z0, x1, z1, feet, h=2):
        """an axis-aligned 1-wide passage `h` high from (x0, z0) to (x1, z1) inclusive at `feet` (through walls)"""
        if x0 != x1 and z0 != z1:
            raise ValueError("punch: axis-aligned only")
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for z in range(min(z0, z1), max(z0, z1) + 1):
                self.fill(x, feet, z, x, feet + h - 1, z, AIR)

    # ---------------------------------------------------------------- frame helpers
    def fput(self, F, u, f, v, name, **st):
        x, z = F.w(u, v); self.put(x, f, z, name, **st)

    def ffill(self, F, u0, f0, v0, u1, f1, v1, name, **st):
        x0, x1, z0, z1 = F.wrect(u0, u1, v0, v1); self.fill(x0, f0, z0, x1, f1, z1, name, **st)

    def fbed(self, F, u, f, v, head, role, step=None, office=None):
        x, z = F.w(u, v); self.bed(x, f, z, F.d(head), role=role, step=step, office=office)

    def fdoor(self, F, u, f, v, facing_local, mat="minecraft:spruce_door", hinge=0):
        x, z = F.w(u, v); self.fill(x, f, z, x, f + 1, z, AIR); self.door(x, f, z, F.d(facing_local), mat=mat, hinge=hinge)

    def fmark(self, F, fam, kind, u, f, v):
        x, z = F.w(u, v); self.marker(fam, kind, x, f, z)

    def fzone(self, F, kind, u0, u1, f, v0, v1):
        x0, x1, z0, z1 = F.wrect(u0, u1, v0, v1)
        if x1 > x0 and z1 > z0:
            self.zone(kind, x0, f, z0, x1, z1)

    def froom(self, F, kind, u0, u1, v0, v1, f):
        x0, x1, z0, z1 = F.wrect(u0, u1, v0, v1); self.room(kind, x0, x1, z0, z1, f)

    def fgully(self, F, u, v, kind):
        x, z = F.w(u, v); self.put(x, -1, z, BARS); self.heads.append((x, -2, z, kind))

    def fbox(self, F, top, mat=None, floor=None):
        """walls u 0 / D-1, v 0 / L-1 from feet 0..top, the inside cleared, a floor course at -1"""
        mat = mat or self.curtain
        x0, x1, z0, z1 = F.rect
        if floor:
            self.fill(x0, -1, z0, x1, -1, z1, floor)
        self.fill(x0, -1, z0, x1, -1, z0, mat); self.fill(x0, -1, z1, x1, -1, z1, mat)
        self.fill(x0, -1, z0, x0, -1, z1, mat); self.fill(x1, -1, z0, x1, -1, z1, mat)
        self.shell(x0, x1, z0, z1, 0, top, mat)
        self.clear(x0 + 1, x1 - 1, z0 + 1, z1 - 1, 0, top)

    def fspiral(self, F, design, cands, f0, floors, ceiling, label):
        """spiral2 at local well corners (u0, v0) of an n x n well; falls back to the old newel stair"""
        import spiral_gen as SG
        n = 2 * SG.DESIGNS[design]["n"]
        sites = []
        for (u0, v0) in cands:
            x0, x1, z0, z1 = F.wrect(u0, u0 + n - 1, v0, v0 + n - 1)
            sites.append((design, x0, z0))
        fx0, fx1, fz0, fz1 = F.wrect(cands[0][0], cands[0][0] + 2, cands[0][1], cands[0][1] + 2)
        return self.spiral2(sites, f0, floors, "stone", ceiling=ceiling, label=label,
                            fallback=lambda: self.spiral(fx0, fz0, f0, floors[-1] - 1))

    # ---------------------------------------------------------------- stairs (program 228)
    def spiral2(self, sites, f0, floors, pal, ceiling=None, label="", fallback=None, caphouse=False):
        """the first (design, x0, z0) of `sites` whose exits all land on walkable floor is laid (tools/spiral_site.py);
        none fits -> `fallback()` (the old full-block newel stair) and a note"""
        import spiral_site as SS
        for design, x0, z0 in sites:
            ok = [c for c in SS.solve(self, x0, z0, f0, floors, design) if c[0]]
            if ok:
                _, _, hand, k0, _, P = ok[0]
                SS.lay(self, P, pal, FLOOR, ceiling=ceiling)
                if caphouse:
                    x0_, z0_, x1_, z1_ = P["well"]; T = P["top"]
                    for (px, pz) in ((x0_ - 1, z0_ - 1), (x1_ + 1, z0_ - 1), (x0_ - 1, z1_ + 1), (x1_ + 1, z1_ + 1)):
                        if self.get(px, T - 1, pz) not in (None, AIR):
                            self.fill(px, T, pz, px, T + 2, pz, self.tower_mat)
                    self.fill(x0_ - 1, T + 3, z0_ - 1, x1_ + 1, T + 3, z1_ + 1, self.dress)
                self.spirals.append({"label": label, "design": design, "hand": hand, "k0": k0, "well": P["well"], "floors": floors, "f0": f0})
                return P
        why = []
        try:
            best = SS.solve(self, sites[0][1], sites[0][2], f0, floors, sites[0][0])[0]
            why = best[4][:2]
        except Exception as e:  # noqa: BLE001
            why = [repr(e)]
        self.notes.append(f"spiral2 {label}: no clean exits for {sorted({s_[0] for s_ in sites})} — the old newel stair stays ({'; '.join(why)})")
        self.spirals.append({"label": label, "design": "newel", "fallback": True})
        if fallback:
            fallback()
        return None

    def spiral(self, x0, z0, f0, f1, mat=None, post=POST):
        """the old newel stair in a 3 x 3 (fallback)"""
        mat = mat or self.curtain
        ring = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1)]
        self.fill(x0 + 1, f0 - 1, z0 + 1, x0 + 1, f1 + 2, z0 + 1, post)
        f, i = f0, 0
        while f <= f1:
            dx, dz = ring[i % 8]
            self.put(x0 + dx, f, z0 + dz, mat)
            for h in range(1, 4):
                self.put(x0 + dx, f + h, z0 + dz, AIR)
            f += 1; i += 1

    # ---------------------------------------------------------------- roofs
    def roof_hip(self, x0, x1, z0, z1, eave, wood=None):
        wood = wood or self.v.roof
        if wood == "thatch":
            return self.roof_gable(x0, x1, z0, z1, eave, wood)        # his 12:20: thatch roofs are GABLES
        r45, hip, ridge = f"pw:roof45_{wood}", f"pw:roof_hip_{wood}", f"pw:roof45_ridge_{wood}"
        depth, width = x1 - x0 + 1, z1 - z0 + 1
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                dw, de, dn, ds = x - x0, x1 - x, z - z0, z1 - z
                k = min(dw, de, dn, ds)
                f = eave + k
                nearest = sorted([(dw, "west"), (de, "east"), (dn, "north"), (ds, "south")])
                (k0, s0), (k1, s1) = nearest[0], nearest[1]
                if k0 == k1 and {s0, s1} not in ({"west", "east"}, {"north", "south"}):
                    facing = s0 if s0 in ("west", "east") else s1
                    self.put(x, f, z, hip, **{"minecraft:cardinal_direction": facing, "minecraft:vertical_half": "bottom"})
                elif k0 == k1:
                    self.put(x, f, z, ridge, **{"minecraft:cardinal_direction": "north" if s0 in ("west", "east") else "west"})
                else:
                    self.put(x, f, z, r45, **{"minecraft:cardinal_direction": s0, "minecraft:vertical_half": "bottom"})
        if depth == width and depth % 2 == 1:
            self.put((x0 + x1) // 2, eave + depth // 2, (z0 + z1) // 2, f"pw:roof_pyramidion_{wood}", **{"minecraft:cardinal_direction": "north", "minecraft:vertical_half": "bottom"})

    def roof_gable(self, x0, x1, z0, z1, eave, wood):
        r45, ridge = f"pw:roof45_{wood}", f"pw:roof45_ridge_{wood}"
        along_x = (x1 - x0) >= (z1 - z0)
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                a, b = (z - z0, z1 - z) if along_x else (x - x0, x1 - x)
                k = min(a, b)
                f = eave + k
                if a == b:
                    self.put(x, f, z, ridge, **{"minecraft:cardinal_direction": "west" if along_x else "north"})
                else:
                    down = ("north" if a < b else "south") if along_x else ("west" if a < b else "east")
                    self.put(x, f, z, r45, **{"minecraft:cardinal_direction": down, "minecraft:vertical_half": "bottom"})
                end = (x in (x0, x1)) if along_x else (z in (z0, z1))
                if end and k > 0:
                    self.fill(x, eave, z, x, f - 1, z, self.curtain)

    def froof(self, F, eave, wood=None, kind="hip"):
        x0, x1, z0, z1 = F.rect
        if kind == "gable" or (wood or self.v.roof) == "thatch":
            self.roof_gable(x0, x1, z0, z1, eave, wood or self.v.roof)
        else:
            self.roof_hip(x0, x1, z0, z1, eave, wood)

    # ---------------------------------------------------------------- fortification primitives
    def parapet_run(self, cells, feet):
        """crenellation, merlon 3 : crenel 1 (Battlement: the crenel ~ one third of the merlon); merlons 2 high (2 above the
        walk), the crenel a bottom slab sill; an arrow slit in the middle of every second merlon"""
        for i, (x, z) in enumerate(cells):
            k, g = i % 4, i // 4
            if k == 3:
                self.put(x, feet, z, self.parapet, **{"minecraft:vertical_half": "bottom"})
                self.put(x, feet + 1, z, AIR)
            else:
                self.put(x, feet, z, self.curtain); self.put(x, feet + 1, z, self.curtain)
                if k == 1 and g % 2 == 1:
                    self.put(x, feet, z, AIR)                                  # the slit (1 high, under the merlon cap)

    def wall_segment(self, a, b, h, thick=3, mural=False, loops=True):
        """a straight curtain from cell a to cell b (inclusive), `thick` wide toward the inside, h high (feet 0..h-1);
        the wall-walk at h-2 on the inner courses (standing h-1), the parapet at h on the outer skin. mural (a 5-thick
        inner curtain, Beaumaris): a 1 x 2 passage at t = 1 standing at feet 5 (floor 4), slits out every 5."""
        (x0, z0), (x1, z1) = a, b
        n = max(abs(x1 - x0), abs(z1 - z0))
        cells = [(round(x0 + (x1 - x0) * i / max(1, n)), round(z0 + (z1 - z0) * i / max(1, n))) for i in range(n + 1)]
        if x0 != x1 and z0 != z1:
            thick += 1
        cx, cz = self.v.W / 2, self.v.W / 2
        mx, mz = (x0 + x1) / 2, (z0 + z1) / 2
        nx, nz = (1 if cx > mx else -1) if abs(cx - mx) > abs(cz - mz) else 0, (1 if cz > mz else -1) if abs(cz - mz) >= abs(cx - mx) else 0
        diag = x0 != x1 and z0 != z1
        mural_t = (1, 2) if diag else (1,)
        for i, (x, z) in enumerate(cells):
            for t in range(thick):
                xx, zz = x + nx * t, z + nz * t
                self.fill(xx, -2, zz, xx, h - 1, zz, self.curtain)
                self.occ.add((xx, zz))
                if t >= 1:
                    self.put(xx, h - 2, zz, self.dress)
                    self.put(xx, h - 1, zz, AIR); self.put(xx, h, zz, AIR); self.put(xx, h + 1, zz, AIR)
                    if self.inbox(xx, zz):
                        self.poi["walk"].add((xx, h - 1, zz))
                    if t == 1 and i % 6 == 3:
                        self.light(xx, h, zz)
                if mural and t in mural_t:
                    self.fill(xx, 5, zz, xx, 6, zz, AIR)
                    if self.inbox(xx, zz):
                        self.poi["mural"].add((xx, 5, zz))
                    if i % 8 == 4:
                        self.light(xx, 6, zz)
        self.parapet_run(cells, h)
        if loops:
            for i, (x, z) in enumerate(cells):
                if i % 5 == 2:
                    self.put(x, h - 3, z, AIR)
                    if mural:
                        self.put(x, 5, z, AIR)                     # a loop from the mural passage
        seg = {"cells": cells, "n": (nx, nz), "thick": thick, "h": h, "mural": mural, "mural_w": len(mural_t)}
        self.segments = getattr(self, "segments", [])
        self.segments.append(seg)
        return cells

    def tower(self, cx, cz, r, h, shape="round", walk=None, mural=False, floors=None, check=True, door=True, toward=None, kind="tower"):
        """a tower at (cx, cz) radius r, feet -5..h (foundations to the moat bed): round / d / square; floors every 5 (or the
        given list), an A_turret spiral (r >= 3), openings where the wall-walk (and the mural passage) arrive, a flat lead
        roof with a 3 : 1 parapet. `toward`: the point its ground door faces (the door is cut later, door_pass)."""
        cells = []
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                d = math.hypot(x - cx, z - cz)
                tx, tz = toward if toward else (self.v.W / 2, self.v.W / 2)
                if shape == "d":
                    # the D: round on the outside (away from `toward`), square on the ward side
                    ux, uz = tx - cx, tz - cz
                    inside = (d <= r + 0.4) or (abs(x - cx) <= r and abs(z - cz) <= r and (x - cx) * ux + (z - cz) * uz > 0)
                elif shape == "round":
                    inside = d <= r + 0.4
                else:
                    inside = abs(x - cx) <= r and abs(z - cz) <= r
                if inside:
                    cells.append((x, z))
        cellset = set(cells)
        rim = [c for c in cells if any((c[0] + dx, c[1] + dz) not in cellset for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        rimset = set(rim)
        inner = [c for c in cells if c not in rimset]
        for (x, z) in cells:
            self.fill(x, -5, z, x, -1, z, self.tower_mat)
            self.occ.add((x, z))
        for (x, z) in rim:
            self.fill(x, 0, z, x, h, z, self.tower_mat)
        for (x, z) in inner:
            self.fill(x, 0, z, x, h, z, AIR)
        self.poi["walk"] = {w for w in self.poi["walk"] if (w[0], w[2]) not in cellset}
        self.poi["mural"] = {w for w in self.poi["mural"] if (w[0], w[2]) not in cellset}
        if floors is None:
            floor_feet = [f for f in range(4, h - 1, 5) if walk is None or abs(f - walk) > 2]
            if mural and 4 not in floor_feet:
                floor_feet.append(4)
            if walk is not None and 0 < walk < h - 1:
                floor_feet.append(walk)
        else:
            floor_feet = list(floors)
        floor_feet = sorted({f for f in floor_feet if 1 <= f <= h - 3})
        # mids at least 3 apart (the spiral's door / start pieces) — a floor too close to the one below is dropped
        must = {walk, 4 if mural else None}
        kept = []
        for f in floor_feet:
            if kept and f - kept[-1] < 3:
                if f in must:
                    kept[-1] = f
                continue
            kept.append(f)
        floor_feet = kept
        for f in floor_feet:
            for (x, z) in inner:
                self.put(x, f, z, FLOOR)
            if inner:
                lx, lz = max(inner, key=lambda c: (c[0] - cx) * 3 + (c[1] - cz))
                self.lantern(lx, f + 1, lz)
        for (x, z) in inner:
            self.put(x, h, z, self.dress)
        ring = sorted(rim, key=lambda c: math.atan2(c[1] - cz, c[0] - cx))
        for i, (x, z) in enumerate(ring):
            if i % 4 != 3:
                self.put(x, h + 1, z, self.tower_mat)
        if self.v.tower_caps and r >= 2 and kind == "tower":
            self.roof_hip(cx - r, cx + r, cz - r, cz + r, h + 2)
        rec = {"cx": cx, "cz": cz, "r": r, "floors": sorted(floor_feet), "inner": inner, "h": h, "check": check and r >= 3,
               "door": door, "toward": toward, "walk": walk, "mural": mural, "rim": rim, "kind": kind}
        if r >= 3:
            mids = sorted({f + 1 for f in floor_feet})
            P = self.spiral2([("A_turret", cx - 1, cz - 1), ("A_turret", cx, cz - 1), ("A_turret", cx - 1, cz), ("A_turret", cx, cz)],
                             0, mids + [h + 1], "stone", ceiling=h + 2, label=f"{kind} {cx},{cz}", caphouse=True,
                             fallback=lambda: self.spiral(cx - 1, cz - 1, 0, h - 1))
            rec["spiral"] = "A_turret" if P else "newel"
        # loops on each storey (1-high slits in the rim, never at an opening level)
        for f in range(2, h - 2, 5):
            if any(abs(f - (lv + 1)) <= 1 for lv in floor_feet):
                continue
            for (x, z) in rim[::max(1, len(rim) // 6)]:
                self.put(x, f, z, AIR)
        # the walk and the mural passage arrive: open the rim at their level
        for key, lv in (("walk", None if walk is None else walk + 1), ("mural", 5 if mural else None)):
            if lv is None:
                continue
            for (wx, wf, wz) in list(self.poi[key]):
                if wf != lv:
                    continue
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        rc = (wx + dx, wz + dz)
                        if rc in rimset:
                            self.fill(rc[0], lv, rc[1], rc[0], lv + 1, rc[1], AIR)
                            if dx and dz:
                                for (ax, az) in ((wx + dx, wz), (wx, wz + dz)):
                                    if (ax, az) in rimset or (ax, az) not in cellset:
                                        self.fill(ax, lv, az, ax, lv + 1, az, AIR)
        self.poi["towers"].append(rec)
        self.poi["footprints"].append(cellset)
        return rec

    def door_pass(self, only=None):
        """v0.3: every tower's ground door — from the rim toward its `toward` point, a 2-high passage cut through the wall
        courses (masonry only) to the first open, floored cell (<= 8 cells); a spruce door in the rim"""
        masonry = {self.curtain, self.dress, self.tower_mat, PANEL, SMOOTH, STONEBR, "minecraft:cobblestone", "minecraft:mossy_stone_bricks",
                   "minecraft:polished_andesite", "minecraft:andesite", "minecraft:polished_diorite", "minecraft:chiseled_stone_bricks"}
        for t in (only if only is not None else self.poi["towers"]):
            if not t["door"] or t["r"] < 2 or t.get("door_done"):
                continue
            t["door_done"] = True
            cx, cz = t["cx"], t["cz"]
            tx, tz = t["toward"] if t["toward"] else (self.v.W / 2, self.v.W / 2)
            vx, vz = tx - cx, tz - cz
            dirs = sorted([(1, 0), (-1, 0), (0, 1), (0, -1)], key=lambda d: -(d[0] * vx + d[1] * vz))[:2]
            inner = set(t["inner"])
            done = False
            for (dx, dz) in dirs:
                if dx * vx + dz * vz <= 0:
                    continue
                # start at the inner cell nearest the rim in this direction
                x, z = cx, cz
                while (x + dx, z + dz) in inner:
                    x += dx; z += dz
                path = []
                ok = False
                for k in range(1, 10):
                    px, pz = x + dx * k, z + dz * k
                    a, b, below = self.get(px, 0, pz), self.get(px, 1, pz), self.get(px, -1, pz)
                    if a in (None, AIR) and b in (None, AIR) and below not in (None, AIR, WATER):
                        ok = bool(path); break
                    if (a not in masonry and a not in (None, AIR)) or (b not in masonry and b not in (None, AIR)):
                        break
                    path.append((px, pz))
                if not ok:
                    continue
                for (px, pz) in path:
                    self.fill(px, 0, pz, px, 1, pz, AIR)
                    if self.get(px, -1, pz) in (None, AIR, WATER):
                        self.put(px, -1, pz, self.tower_mat)
                self.door(path[0][0], 0, path[0][1], DIRNAME[(dx, dz)])
                t["door_cell"] = path[0]
                done = True
                break
            if not done:
                # a corner tower: a diagonal archway (no door leaf) with the two pinch cells of every step opened
                dx, dz = (1 if vx > 0 else -1), (1 if vz > 0 else -1)
                x, z = cx, cz
                while (x + dx, z + dz) in inner:
                    x += dx; z += dz
                path = []
                for k in range(1, 10):
                    px, pz = x + dx * k, z + dz * k
                    a, b, below = self.get(px, 0, pz), self.get(px, 1, pz), self.get(px, -1, pz)
                    if a in (None, AIR) and b in (None, AIR) and below not in (None, AIR, WATER) and path:
                        done = True; break
                    cells = [(px, pz), (px - dx, pz), (px, pz - dz)]
                    if any(self.get(qx, f, qz) not in masonry and self.get(qx, f, qz) not in (None, AIR) for (qx, qz) in cells for f in (0, 1)):
                        break
                    path += cells
                if done:
                    for (px, pz) in path:
                        if (px, pz) in inner:
                            continue
                        self.fill(px, 0, pz, px, 1, pz, AIR)
                        if self.get(px, -1, pz) in (None, AIR, WATER):
                            self.put(px, -1, pz, self.tower_mat)
                    t["door_cell"] = path[0]
                else:
                    self.notes.append(f"{t['kind']} {cx},{cz}: no ground door could be cut toward {tx:.0f},{tz:.0f}")

    def gatehouse(self, gx, gz, T, h, storeys, role="constable", pit=True, n_port=2, bed_step="G1"):
        """the gatehouse (Harlech / Caernarfon / Bodiam): a block straddling the curtain at x = gx (the wall's outer face),
        passage 4 wide x (h - 2) high along +x, 2 (lord) / 3 (grand) portcullis grooves, outer + inner door leaves, the
        drawbridge PIT at the outer end (deck lowered), guard rooms either side (door off the passage, loops into it; an
        upper guard room on 5-thick curtains), the winch chamber over the passage at the wall-walk level with MURDER HOLES
        (iron grates), one or two lodging storeys above (constable / lord), a roof deck, twin round flank towers (r 4, F3)
        joined to every storey. role: 'constable' (outer / B) or 'lord' (A inner: the lord's apartments)."""
        xa, xb = gx - 3, gx + T + 4
        za, zb = gz - 10, gz + 9
        span = range(gz - 2, gz + 2)
        top = h + 3 + 5 * storeys
        upper_guard = T >= 5 and h >= 11
        # the block, solid, then carved
        self.fill(xa, -5, za, xb, -1, zb, self.curtain)
        self.fill(xa, 0, za, xb, top, zb, self.curtain)
        self.block_occ(xa, xb, za, zb, margin=1)
        self.poi["footprints"].append({(x, z) for x in range(xa, xb + 1) for z in range(za, zb + 1)})
        # ground: the passage
        for x in range(xa, xb + 1):
            for z in span:
                self.fill(x, 0, z, x, h - 3, z, AIR)
                self.put(x, -1, z, COBBLE)
        # the guard rooms
        g_top = 3 if upper_guard else h - 3
        for (z0, z1, side) in ((za + 1, gz - 5, "north"), (gz + 4, zb - 1, "south")):
            self.clear(xa + 2, xb - 1, z0, z1, 0, g_top)
            self.room("guardroom", xa + 2, xb - 1, z0, z1, 0)
            self.zone("quarters", xa + 2, 0, z0, xb - 1, z1)
            # the door off the passage (through the 2-thick passage wall), loops into the passage
            zd = gz - 3 if side == "north" else gz + 2
                # the wall cells next to the passage: zd and zd -/+ 1
            z2 = zd - 1 if side == "north" else zd + 1
            self.fill(xb - 2, 0, z2, xb - 2, 1, z2, AIR)
            self.door(xb - 2, 0, zd, side)
            for xl in (xa + 3, xa + 6):
                if xl < xb - 3:
                    self.fill(xl, 1, min(zd, z2), xl, 1, max(zd, z2), AIR)
            # G1 bunks: three beds along the outer wall (on the upper floor when there is one)
            bf = 5 if upper_guard else 0
            zb_ = z0 if side == "north" else z1
            head = "north" if side == "north" else "south"
            for i in range(3):
                bx = xa + 3 + i * 2
                if bx <= xb - 2:
                    self.bed(bx, bf, zb_ + (1 if side == "north" else -1), head, role="guard", step=bed_step, office="men-at-arms")
            self.marker("station", "post", xb - 3, 0, (z0 + z1) // 2)
            self.light(xa + 4, g_top - 1 if g_top >= 3 else 2, (z0 + z1) // 2)
            if upper_guard:
                self.fill(xa + 2, 4, z0, xb - 1, 4, z1, FLOOR)
                self.clear(xa + 2, xb - 1, z0, z1, 5, h - 3)
                self.room("guardroom", xa + 2, xb - 1, z0, z1, 5)
                self.light(xa + 5, 7, (z0 + z1) // 2)
        # the portcullis grooves (raised) — the first one is the gate's seal (R6)
        grooves = [gx, gx + T, xb - 1][:n_port]
        for gi, xg in enumerate(grooves):
            for zz in (gz - 3, gz + 2):
                self.fill(xg, 0, zz, xg, h - 3, zz, AIR)
            for z in span:
                self.put(xg, h - 3, z, BARS)
                if gi == 0:
                    for f in range(0, h - 2):
                        self.poi["sealed"].add((xg, f, z))
        # door leaves: outer (behind the first portcullis) and inner (the ward end)
        for xd, face in ((gx + 1, "east"), (xb, "east")):
            for i, z in enumerate(span):
                self.door(xd, 0, z, face, hinge=i % 2)
        # the drawbridge pit (turning bridge: the counterweight sinks into a pit in the passage) with the deck lowered
        if pit:
            self.fill(xa - 1, -5, gz - 3, xa + 3, -1, gz + 2, COBBLE)
            self.fill(xa, -4, gz - 2, xa + 2, -2, gz + 1, AIR)
            self.fill(xa, -1, gz - 2, xa + 2, -1, gz + 1, DECK)
        # the winch chamber: floor at the wall-walk level (h - 2), murder holes over the passage
        self.fill(xa + 1, h - 2, za + 1, xb - 1, h - 2, zb - 1, FLOOR)
        self.clear(xa + 1, xb - 1, za + 1, zb - 1, h - 1, h + 2)
        for x in range(gx + 2, xb - 1, 3):
            for z in span:
                self.put(x, h - 2, z, BARS)
        for xg in grooves:
            for z in span:
                self.put(xg, h - 2, z, BARS); self.put(xg, h - 1, z, BARS)       # the raised grille hangs in the chamber
        self.room("gatechamber", xa + 1, xb - 1, za + 1, zb - 1, h - 1)
        self.marker("station", "post", xb - 2, h - 1, gz + 4)                  # the winch
        self.zone("workfloor", xa + 1, h - 1, za + 1, xb - 1, zb - 1)
        self.light(xa + 3, h + 1, gz); self.light(xb - 3, h + 1, gz - 6); self.light(xb - 3, h + 1, gz + 6)
        # lodging storeys
        for s in range(storeys):
            f0 = h + 3 + 5 * s
            self.fill(xa + 1, f0, za + 1, xb - 1, f0, zb - 1, FLOOR)
            self.clear(xa + 1, xb - 1, za + 1, zb - 1, f0 + 1, f0 + 4)
            # a partition across z at gz with a doorway
            self.fill(xa + 1, f0 + 1, gz, xb - 1, f0 + 4, gz, PANEL)
            self.fill((xa + xb) // 2, f0 + 1, gz, (xa + xb) // 2, f0 + 2, gz, AIR)
            for z in range(za + 3, zb - 2, 4):
                if z != gz:
                    self.window(xb, f0 + 2, z, 0, 1, 1, 2)
            self.room("gatelodging", xa + 1, xb - 1, za + 1, gz - 1, f0 + 1)
            self.room("gatelodging", xa + 1, xb - 1, gz + 1, zb - 1, f0 + 1)
            self.light(xa + 4, f0 + 4, gz - 5); self.light(xa + 4, f0 + 4, gz + 5)
            if role == "porter":
                # the gate-ward's lodging over the base court's gate: one bunk, the table
                self.bed(xb - 2, f0 + 1, za + 2, "north", role="guard", step=bed_step, office="gate-ward")
                self.table(xa + 4, f0 + 1, za + 4)
                self.zone("quarters", xa + 1, f0 + 1, za + 1, xb - 1, gz - 1)
                self.marker("station", "post", xa + 4, f0 + 1, gz + 4)
            elif role == "constable":
                self.bed(xb - 2, f0 + 1, za + 2, "north", role="noble", office="constable")
                self.table(xa + 4, f0 + 1, za + 4); self.furn("chair", xa + 5, f0 + 1, za + 4, "west")
                self.marker("station", "desk", xa + 4, f0 + 1, za + 5)
                self.zone("chamber", xa + 1, f0 + 1, za + 1, xb - 1, gz - 1)
                self.table(xa + 4, f0 + 1, gz + 4); self.furn("bench", xa + 4, f0 + 1, gz + 6, "north")
                self.zone("commons", xa + 1, f0 + 1, gz + 1, xb - 1, zb - 1)
            elif role == "lord" and s == 0:
                # the lord's great chamber (Beaumaris: the gatehouse hall) — table, chairs, the seat of state
                self.table(xa + 4, f0 + 1, gz - 5); self.table(xa + 4, f0 + 1, gz - 6)
                self.marker("station", "seat", xa + 6, f0 + 1, gz - 5)
                self.zone("chamber", xa + 1, f0 + 1, za + 1, xb - 1, gz - 1)
                self.bed(xb - 2, f0 + 1, zb - 2, "south", role="noble", office="lord's guest")
                self.zone("quarters", xa + 1, f0 + 1, gz + 1, xb - 1, zb - 1)
            else:
                # the lord's bedchamber + the children's bed (his 17:52), and the wardrobe
                self.bed(xb - 2, f0 + 1, za + 2, "north", role="lord", office="lord")
                self.bed(xa + 2, f0 + 1, za + 2, "north", role="child", office="lord's children")
                self.zone("quarters", xa + 1, f0 + 1, za + 1, xb - 1, gz - 1)
                for z in range(gz + 2, zb - 1, 2):
                    self.barrel(xb - 1, f0 + 1, z)
                self.zone("storeroom", xa + 1, f0 + 1, gz + 1, xb - 1, zb - 1)
        # the roof deck + its parapet
        self.fill(xa + 1, top, za + 1, xb - 1, top, zb - 1, self.dress)
        self.clear(xa, xb, za, zb, top + 1, top + 3)
        edge = [(x, za) for x in range(xa, xb + 1)] + [(xb, z) for z in range(za + 1, zb + 1)] + [(x, zb) for x in range(xb - 1, xa - 1, -1)] + [(xa, z) for z in range(zb - 1, za, -1)]
        self.parapet_run(edge, top + 1)
        # the flank towers (r 4: the A turret fits, F3) at the outer corners, joined to every storey
        tfl = sorted({h - 2, top} | {h + 3 + 5 * s for s in range(storeys)} | ({4} if upper_guard else set()))
        tw = []
        for tz, side in ((za - 3, -1), (zb + 3, 1)):
            rec = self.tower(gx - 1, tz, 4, top + 3, "round", walk=h - 2, mural=upper_guard, floors=tfl, door=False,
                             toward=(gx + 10, gz), kind="gatetower")
            tw.append(rec)
            zin, zout = (za + 1, za - 1) if side < 0 else (zb - 1, zb + 1)
            for lv in [0] + [f + 1 for f in tfl]:
                if lv == 0:
                    self.punch(gx - 1, zout, gx - 1, zin, 0)
                elif lv <= top + 1:
                    self.punch(gx - 1, zout, gx - 1, zin, lv)
        self.poi["gates"].append({"gx": gx, "gz": gz, "xa": xa, "xb": xb, "za": za, "zb": zb, "top": top, "towers": [(t["cx"], t["cz"]) for t in tw],
                                  "grooves": grooves, "role": role})
        return (xa, xb, za, zb, top)

    def postern(self, inside, outside, axis, seal=False, label="postern"):
        """a postern (sally port): a 1-wide, 3-high passage on `axis` from the open cell `inside` to the open cell `outside`,
        a door at the first wall cell, a portcullis (raised: bars in the top cell) at the last; seal -> R6 seals it"""
        (x0, z0), (x1, z1) = inside, outside
        dx, dz = axis
        n = abs(x1 - x0) + abs(z1 - z0)
        cells = [(x0 + dx * i, z0 + dz * i) for i in range(n + 1)]
        walls = [c for c in cells if self.get(c[0], 0, c[1]) not in (None, AIR)]
        for (x, z) in cells:
            self.fill(x, 0, z, x, 2, z, AIR)
            if self.get(x, -1, z) in (None, AIR, WATER, GRASS, DIRT):
                self.put(x, -1, z, COBBLE)
        if walls:
            fx, fz = walls[0]
            self.door(fx, 0, fz, DIRNAME[(dx, dz)])
            lx, lz = walls[-1]
            self.put(lx, 2, lz, BARS)
            if seal:
                for f in range(0, 3):
                    self.poi["sealed"].add((lx, f, lz))
        self.poi["posterns"].append({"label": label, "cells": cells, "seal": seal})
        return cells

    def moat_cells(self, poly, berm, width):
        """cells outside the ring polygon whose distance to it lies in (berm, berm + width] (rounded corners)"""
        out = []
        xs = [p[0] for p in poly]; zs = [p[1] for p in poly]
        pad = int(math.ceil(berm + width)) + 1
        lo_x, hi_x = int(min(xs)) - pad, int(max(xs)) + pad
        lo_z, hi_z = int(min(zs)) - pad, int(max(zs)) + pad
        for x in range(max(0, lo_x), min(self.v.W, hi_x + 1)):
            for z in range(max(0, lo_z), min(self.v.W, hi_z + 1)):
                if point_in_poly(poly, x, z):
                    continue
                d = poly_dist(poly, x, z)
                if berm < d <= berm + width:
                    out.append((x, z))
        return out

    def dig_moat(self, cells, kind):
        """wet: water at -2..-1 over a cobble bed at -3 (Bodiam 1.5-2.1 m); dry: a ditch 4 deep, grass bed at -5"""
        for (x, z) in cells:
            if kind == "wet":
                self.put(x, -3, z, COBBLE)
                self.put(x, -2, z, WATER); self.put(x, -1, z, WATER)
                self.water_ok.add((x, -2, z)); self.water_ok.add((x, -1, z))
            else:
                self.put(x, -5, z, GRASS)
                self.fill(x, -4, z, x, -1, z, AIR)
            self.occ.add((x, z))
        return set(cells)

    def bridge(self, x0, x1, z0, z1, posts=True):
        """a timber deck at -1 (the moat / lake surface) with post piers every 4 under it"""
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                self.put(x, -1, z, DECK)
                if posts and (x - x0) % 4 == 0 and z in (z0, z1):
                    self.fill(x, -4, z, x, -2, z, POST, pillar_axis="y")

    def barbican(self, x_back, gz, w=14, d=16, h=7):
        """a walled forecourt in front of the gate (Bodiam / Conwy / Alnwick): side and front walls 3 thick, h high, a
        walk (stand h-1) reached by a flight, its own gate passage with one raised portcullis and doors"""
        x0, x1 = x_back - d + 1, x_back
        z0, z1 = gz - w // 2, gz + w // 2 - 1
        span = range(gz - 2, gz + 2)
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                edge_t = min(x - x0, z - z0, z1 - z)
                if edge_t <= 2:
                    self.fill(x, -2, z, x, h - 1, z, self.curtain)
                    if edge_t >= 1:
                        self.put(x, h - 2, z, self.dress); self.fill(x, h - 1, z, x, h + 1, z, AIR)
                        self.poi["walk"].add((x, h - 1, z))
                else:
                    self.put(x, -1, z, COBBLE)
                self.occ.add((x, z))
        self.parapet_run([(x0, z) for z in range(z0, z1 + 1)], h)
        self.parapet_run([(x, z0) for x in range(x0 + 1, x1 + 1)], h)
        self.parapet_run([(x, z1) for x in range(x0 + 1, x1 + 1)], h)
        for x in range(x0, x0 + 3):                                         # the gate passage
            for z in span:
                self.fill(x, 0, z, x, 4, z, AIR); self.put(x, -1, z, COBBLE)
                self.poi["walk"].discard((x, h - 1, z))
        for z in span:
            self.put(x0, 4, z, BARS)
        for i, z in enumerate(span):
            self.door(x0 + 2, 0, z, "east", hinge=i % 2)
        # the flight to the walk along the north flank (rises toward the front, x-)
        for k in range(h - 2):
            x = x1 - 1 - k
            self.stairs(x, k, z0 + 3, "west", mat="minecraft:stone_brick_stairs")
            self.fill(x, 0, z0 + 3, x, k - 1, z0 + 3, self.curtain) if k >= 1 else None
        self.marker("station", "post", x0 + 4, 0, gz + 3)
        self.poi["footprints"].append({(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)})
        return (x0, x1, z0, z1)

    # ---------------------------------------------------------------- the ranges (each in its own Frame)
    def hall(self, F, h, kind_roof):
        """the GREAT HALL (R3: 1.5-3 x as long as wide and higher than wide; Bodiam / Caernarfon / Hedingham): interior
        12 x 30 (lord) / 17 x 44 (grand), walls to the plate at h, an OPEN TIMBER ROOF (tie beams + king posts every 4, no
        ceiling); the service end (buttery | steward's chamber | pantry) + the steward's counting room over it; the SCREENS
        passage with the main doors, the screens with two openings; the minstrels' gallery over the screens joined to two
        3-wide WALL GALLERIES at walking level 8 (a flight up); the dais, the high table, the hearth; the lord's door; the
        CELLAR under the hall (-4..-2) from the buttery; and the marked SKYWAY SLOT (his 17:58): a 2-wide 45-degree band at
        walking level 8 from gallery A's upper-end corner across the open floor to gallery B, landings at both ends."""
        D, L = F.D, F.L
        Ui = D - 2                                              # last interior u
        self.ffill(F, 0, -1, 0, D - 1, -1, L - 1, SMOOTH)
        self.fbox(F, h - 1)
        # the service end (v 1..5): three rooms, ceiling 4, solid to 6, the counting room floor at 7
        third = (Ui - 2) // 3
        rooms = [(1, third), (third + 2, 2 * third + 1), (2 * third + 3, Ui)]
        self.ffill(F, 1, 4, 1, Ui, 7, 5, self.curtain)
        self.ffill(F, 1, 0, 6, Ui, 6, 6, self.curtain)                # the service wall (v 6), 0..6
        for (ua, ub) in rooms[:-1]:
            self.ffill(F, ub + 1, 0, 1, ub + 1, 3, 5, PANEL)
        names = ["buttery", "steward", "pantry"]
        for (ua, ub), nm in zip(rooms, names):
            um = (ua + ub) // 2
            self.fdoor(F, um, 0, 6, "vm")
            self.froom(F, nm, ua, ub, 1, 5, 0)
            self.fput(F, um, 2, 3, LIGHT); self.lights += 1
        # buttery: barrels + the cellar flight (down along v- at u = rooms[0][0])
        ub0 = rooms[0][0]
        for v in range(1, 5):
            self.fput(F, rooms[0][1], 0, v, "minecraft:barrel", facing_direction=1, open_bit=False)
        self.fzone(F, "storeroom", rooms[0][0], rooms[0][1], 0, 1, 5)
        # steward: bed (clerk), desk
        su0, su1 = rooms[1]
        self.fbed(F, su0, 0, 2, "vm", role="clerk", office="steward")
        self.fput(F, su1, 0, 4, "minecraft:barrel", facing_direction=1, open_bit=False)
        self.fzone(F, "chamber", su0, su1, 0, 1, 5)
        # pantry
        for v in range(1, 5, 2):
            self.fput(F, rooms[2][1], 0, v, "minecraft:barrel", facing_direction=1, open_bit=False)
        self.fzone(F, "storeroom", rooms[2][0], rooms[2][1], 0, 1, 5)
        # the counting room over the service end (stand 8) with a door to the minstrels' gallery
        self.ffill(F, 1, 8, 6, Ui, h - 1, 6, PANEL)
        self.fdoor(F, (1 + Ui) // 2, 8, 6, "vm")
        x, z = F.w(3, 2)
        self.put(x, 8, z, "minecraft:lectern", **{"minecraft:cardinal_direction": F.d("vp"), "powered_bit": False})
        self.marker("station", "desk", x, 8, z)
        self.froom(F, "countingroom", 1, Ui, 1, 5, 8)
        self.fput(F, 2, 10, 3, LIGHT); self.lights += 1
        # the screens: passage v 7..8, the screens partition at v 9 (0..6) with two 2-wide openings
        self.ffill(F, 1, 0, 9, Ui, 6, 9, PANEL)
        for ua in (3, Ui - 3):
            self.ffill(F, ua, 0, 9, ua + 1, 2, 9, AIR)
        # the main doors (u 0, v 7..8) and the back doors (u D-1)
        for i, v in enumerate((7, 8)):
            self.fdoor(F, 0, 0, v, "in", hinge=i)
            self.fdoor(F, D - 1, 0, v, "out", hinge=i)
        # the minstrels' gallery (v 7..9) and the wall galleries (u 1..3, u Ui-2..Ui) at floor 7
        self.ffill(F, 1, 7, 7, Ui, 7, 9, FLOOR)
        self.ffill(F, 1, 7, 10, 3, 7, L - 2, FLOOR)
        self.ffill(F, Ui - 2, 7, 10, Ui, 7, L - 2, FLOOR)
        rail = [(u, 9) for u in range(4, Ui - 2)] + [(3, v) for v in range(10, L - 1)] + [(Ui - 2, v) for v in range(10, L - 1)]
        # the flight: u 4, rising toward v+ from v 11 (steps at feet 0..6), arriving beside gallery A at v 17
        fv0 = 11
        for k in range(7):
            v = fv0 + k
            self.fput(F, 4, k, v, "minecraft:spruce_stairs", weirdo_direction=STAIR_DIR[F.d("vp")], upside_down_bit=False)
            if k >= 1:
                self.ffill(F, 4, 0, v, 4, k - 1, v, PANEL)
        gaps = {(3, fv0 + 6)}
        # the skyway slot (45 degrees, 2 wide, walking level 8): from (3, L-3) / (3, L-4) on gallery A to gallery B
        n = (Ui - 2) - 3
        slot = []
        for i in range(n + 1):
            for dv in (0, 1):
                slot.append((3 + i, L - 3 - i - dv))
        for (u, v) in slot:
            self.ffill(F, u, 8, v, u, 10, v, AIR)
            if u in (3, Ui - 2):
                gaps.add((u, v))
        for (u, v) in rail:
            if (u, v) not in gaps:
                self.fput(F, u, 8, v, RAIL)
        land_a, land_b = (2, L - 3), (Ui - 1, L - 3 - n)
        self.fmark(F, "port", "passage", land_a[0], 8, land_a[1]); self.fmark(F, "port", "passage", land_b[0], 8, land_b[1])
        wa, wb = F.w(*land_a), F.w(*land_b)
        self.skyway.append({"from": [wa[0], 8, wa[1]], "to": [wb[0], 8, wb[1]], "level": 8, "width": 2,
                            "cells": [list(F.w(u, v)) for (u, v) in slot], "status": "SLOT ONLY — the catwalk/skyway blocks are made separately"})
        # the dais (v L-4..L-2), the high table, the hearth on the end wall, the lord's door
        self.ffill(F, 1, 0, L - 4, Ui, 0, L - 2, DECK)
        for u in range(4, Ui - 2):
            self.fput(F, u, 1, L - 4, "pw:furn_trestle_dark_oak", **{"minecraft:cardinal_direction": F.d("vm")})
        self.fmark(F, "station", "seat", D // 2, 1, L - 3)
        um = D // 2
        x, z = F.w(um, L - 2)
        self.hearth(x, 1, z, F.d("vm"), flue_to=h - 1)
        self.fdoor(F, 0, 1, L - 3, "out")
        # the hall's furniture: trestles down the long sides of the open floor
        for v in range(20, L - 6, 4):
            self.fput(F, Ui - 4, 0, v, "pw:furn_trestle_spruce", **{"minecraft:cardinal_direction": F.d("in")})
            self.fput(F, Ui - 5, 0, v, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": F.d("out")})
        # windows: below the galleries (2..4) and above them (9..11) on the door side; the back side when it is free
        for v in range(12, L - 4, 4):
            for uw in (0, D - 1):
                if uw == D - 1 and not getattr(F, "back_windows", True):
                    continue
                x, z = F.w(uw, v)
                if v not in (7, 8, L - 3):
                    self.fill(x, 2, z, x, 4, z, GLASS)
                    self.fill(x, 9, z, x, min(11, h - 2), z, GLASS)
        # the open timber roof: trusses every 4 (tie beam at the plate, king post to the ridge)
        self.froof(F, h, kind="gable" if kind_roof == "gable" else "hip")
        ridge = h + (D - 1) // 2
        axis_u = F.axis("u")
        for v in range(11, L - 2, 4):
            self.ffill(F, 1, h, v, Ui, h, v, POST, pillar_axis=axis_u)
            self.ffill(F, D // 2, h + 1, v, D // 2, ridge - 1, v, POST, pillar_axis="y")
        for v in range(12, L - 4, 6):
            self.fput(F, D // 2, h - 2, v, LIGHT); self.lights += 1
        # the cellar (Conwy: hall and chapel "on top of the cellars")
        self.ffill(F, 0, -5, 0, D - 1, -2, L - 1, LINING)
        self.ffill(F, 1, -4, 1, Ui, -2, L - 2, AIR)
        for u in (D // 2,):
            for v in range(7, L - 3, 7):
                self.ffill(F, u, -4, v, u, -2, v, LINING)
        for k, v in enumerate((4, 3, 2)):
            self.ffill(F, ub0, -1 - k, v, ub0, 3, v, AIR)
            self.fput(F, ub0, -2 - k, v, "minecraft:stone_brick_stairs", weirdo_direction=STAIR_DIR[F.d("vp")], upside_down_bit=False)
        self.ffill(F, ub0, -1, 1, ub0, 3, 1, AIR)
        for v in range(4, L - 3, 6):
            self.fput(F, 3, -2, v, LIGHT); self.fput(F, Ui - 2, -2, v, LIGHT); self.lights += 2
        self.froom(F, "cellar", 1, Ui, 1, L - 2, -4)
        self.fzone(F, "cellar", 1, Ui, -4, 2, L - 2)
        # zones / rooms
        self.froom(F, "hall", 1, Ui, 10, L - 2, 0)
        self.froom(F, "screens", 1, Ui, 7, 8, 0)
        self.fzone(F, "commons", 1, Ui, 0, 10, L - 2)
        return F

    def kitchen(self, F, h=7):
        """the kitchen (Bodiam: two hearths, bread ovens): two hearths + flues on the back wall, two smokers (ovens), the
        table, barrels, a drain GULLY to the sewer, the COOKS' room behind a partition (two beds)"""
        D, L = F.D, F.L
        self.fbox(F, h - 1, floor=COBBLE)
        Ui = D - 2
        kl = L - 6                                    # the cooks' room: v kl+1 .. L-2
        self.ffill(F, 1, 0, kl, Ui, h - 1, kl, PANEL)
        self.fdoor(F, 2, 0, kl, "vp")
        for v in (2, 6):
            x, z = F.w(Ui, v)
            self.hearth(x, 0, z, F.d("out"), flue_to=h)
        for v in (3, 5):
            self.fput(F, Ui, 0, v + 6 if v + 6 < kl else v + 1, "minecraft:smoker", **{"minecraft:cardinal_direction": F.d("out")})
        self.fmark(F, "station", "oven", Ui - 1, 0, 9 if 9 < kl else 4)
        x, z = F.w(4, 4); self.table(x, 0, z)
        self.fmark(F, "station", "prep", 4, 0, 5)
        dv = L // 2 if L // 2 < kl else kl // 2
        for v in range(1, kl - 1, 2):
            if abs(v - dv) > 1:
                self.fput(F, 1, 0, v, "minecraft:barrel", facing_direction=1, open_bit=False)
        self.fgully(F, Ui - 1, kl - 2, "kitchen")
        self.fdoor(F, 0, 0, L // 2 if L // 2 < kl else kl // 2, "in")
        self.fbed(F, 2, 0, kl + 2, "in", role="servant", office="cook")
        self.fbed(F, 2, 0, L - 2, "in", role="servant", office="cook")
        self.fput(F, 3, 3, (kl + 1 + L - 2) // 2, LIGHT); self.fput(F, 3, h - 2, kl // 2, LIGHT); self.lights += 2
        self.froom(F, "kitchen", 1, Ui, 1, kl - 1, 0)
        self.froom(F, "cooksroom", 1, Ui, kl + 1, L - 2, 0)
        self.fzone(F, "kitchen", 1, Ui, 0, 1, kl - 1)
        self.fzone(F, "quarters", 1, Ui, 0, kl + 1, L - 2)
        self.froof(F, h)

    def chapel(self, F, h=10):
        """the chapel (Krak 21.5 x 8.5 m, barrel vault; Bodiam: an oratory): a long nave, the altar step, the east window,
        benches; the CHAPLAIN's room at the west end behind a partition (bed)"""
        D, L = F.D, F.L
        Ui = D - 2
        self.fbox(F, h - 1, floor=SMOOTH)
        self.ffill(F, 1, 0, 4, Ui, h - 1, 4, PANEL)
        self.fdoor(F, 2, 0, 4, "vm")
        self.fbed(F, Ui - 1, 0, 2, "in", role="clerk", office="chaplain")
        self.fput(F, 1, 0, 1, "minecraft:barrel", facing_direction=1, open_bit=False)
        self.fput(F, 3, 3, 2, LIGHT); self.lights += 1
        self.froom(F, "chaplain", 1, Ui, 1, 3, 0)
        self.fzone(F, "quarters", 1, Ui, 0, 1, 3)
        self.ffill(F, 1, 0, L - 3, Ui, 0, L - 2, SMOOTH)
        self.fput(F, D // 2, 1, L - 2, "minecraft:smooth_stone_slab", **{"minecraft:vertical_half": "bottom"})
        self.ffill(F, 2, 2, L - 1, Ui - 1, h - 3, L - 1, GLASS)
        for v in range(7, L - 4, 2):
            for u in (2, 3, Ui - 2, Ui - 1):
                self.fput(F, u, 0, v, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": F.d("vp")})
        for v in range(8, L - 3, 6):
            self.fput(F, D // 2, h - 2, v, LIGHT); self.lights += 1
        for v in range(7, L - 3, 4):
            x, z = F.w(D - 1, v)
            if getattr(F, "back_windows", True):
                self.fill(x, 2, z, x, h - 4, z, GLASS)
        self.fdoor(F, 0, 0, 6, "in")
        self.fmark(F, "station", "seat", D // 2, 1, L - 4)
        self.froom(F, "chapel", 1, Ui, 5, L - 2, 0)
        self.fzone(F, "commons", 1, Ui, 0, 5, L - 2)
        self.froof(F, h)

    def lodgings(self, F, storeys=2, clear=4, beds_per_bay=1, role="servant", step=None, office="retainer", label="lodgings"):
        """a range of lodgings: a corridor along the door side (u 1), bays off it (partitions every 6), beds per bay, a
        B_tower spiral at the far end, doors at both ends of the corridor. Returns the number of beds."""
        D, L = F.D, F.L
        Ui = D - 2
        top = storeys * (clear + 1) - 1
        self.fbox(F, top, floor=FLOOR)
        nb = 0
        stair_v = L - 6                                    # the stair bay: v L-6..L-2 (4 x 4 well at u 1..4 or Ui-3..Ui)
        for s in range(storeys):
            f0 = s * (clear + 1)
            if s:
                self.ffill(F, 1, f0 - 1, 1, Ui, f0 - 1, L - 2, FLOOR)
            for v in range(1, stair_v - 1, 6):
                self.ffill(F, 3, f0, v, Ui, f0 + clear - 1, v, PANEL)
                if v > 1:
                    pass
                for b in range(beds_per_bay):
                    vb = v + 2 + b * 2
                    if vb <= min(v + 5, stair_v - 2):
                        self.fbed(F, Ui - 1, f0, vb, "in", role=role, step=step, office=office); nb += 1
                if s == 0:
                    x, z = F.w(0, v + 2)
                    if self.get(x, 1, z) not in (None, AIR):
                        self.fill(x, 1, z, x, 2, z, GLASS)
                else:
                    x, z = F.w(0, v + 2)
                    self.fill(x, f0 + 1, z, x, f0 + 2, z, GLASS)
                self.fput(F, 4, f0 + 2, v + 3, LIGHT); self.lights += 1
            self.ffill(F, 3, f0, stair_v - 1, Ui, f0 + clear - 1, stair_v - 1, PANEL)
            self.fput(F, 1, f0 + 2, 3, LIGHT); self.lights += 1
            self.fzone(F, "quarters", 1, Ui, f0, 1, stair_v - 2)
            self.froom(F, label, 1, Ui, 1, stair_v - 2, f0)
        if storeys > 1:
            self.fspiral(F, "B_tower", [(Ui - 3, L - 5), (1, L - 5), (Ui - 3, stair_v)], 0, [s_ * (clear + 1) for s_ in range(1, storeys)],
                         ceiling=top + 1, label=label)
        self.fdoor(F, 0, 0, 1, "in"); self.fdoor(F, 0, 0, L - 3, "in")
        self.froof(F, top + 1)
        return nb

    def garrison(self, F, beds, step):
        """a garrison range (Conwy: 30 men; Berwick's barracks are 18th c. — so a two-storey lodging range, not a barracks):
        ground = mess hall (trestles, benches) + armoury (barrels, the store station); upper = a dormitory of `beds` beds,
        a B_tower spiral; doors on the door side"""
        D, L = F.D, F.L
        Ui = D - 2
        top = 9
        self.fbox(F, top, floor=FLOOR)
        self.ffill(F, 1, 4, 1, Ui, 4, L - 2, FLOOR)
        ar = 6                                                 # the armoury: v 1..5
        self.ffill(F, 1, 0, ar, Ui, 3, ar, PANEL)
        self.fdoor(F, 2, 0, ar, "vm")
        for v in range(1, ar):
            self.fput(F, Ui, 0, v, "minecraft:barrel", facing_direction=1, open_bit=False)
        self.fmark(F, "station", "store", Ui - 1, 0, 3)
        self.froom(F, "armoury", 1, Ui, 1, ar - 1, 0)
        self.fzone(F, "storeroom", 1, Ui, 0, 1, ar - 1)
        self.fput(F, 3, 0, L - 3, "pw:furn_trestle_spruce", **{"minecraft:cardinal_direction": F.d("in")})
        self.fput(F, 3, 0, L - 2, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": F.d("vm")})
        self.fmark(F, "station", "table", 2, 0, L - 3)
        self.froom(F, "mess", 1, Ui, ar + 1, L - 2, 0)
        self.fzone(F, "commons", 1, Ui, 0, ar + 1, L - 2)
        for v in range(3, L - 2, 5):
            self.fput(F, 3, 3, v, LIGHT); self.fput(F, 3, 8, v, LIGHT); self.lights += 2
            x, z = F.w(0, v)
            self.fill(x, 1, z, x, 2, z, GLASS); self.fill(x, 6, z, x, 7, z, GLASS)
        # the dormitory: beds along the back wall and the end walls, heads to the wall
        n = 0
        for v in range(1, L - 6, 2):
            if n < beds:
                self.fbed(F, Ui - 1, 5, v, "in", role="guard", step=step, office="men-at-arms"); n += 1
        for v in range(1, L - 6, 2):
            if n < beds and Ui - 1 >= 6:
                self.fbed(F, 2, 5, v, "out", role="guard", step=step, office="men-at-arms"); n += 1
        self.froom(F, "dormitory", 1, Ui, 1, L - 2, 5)
        self.fzone(F, "quarters", 1, Ui, 5, 1, L - 7)
        self.fspiral(F, "B_tower", [(Ui - 3, L - 5), (1, L - 5)], 0, [5], ceiling=top, label="garrison")
        self.fdoor(F, 0, 0, ar + 2, "in"); self.fdoor(F, 0, 0, 3, "in")
        self.froof(F, top + 1, kind="gable")
        if n < beds:
            self.notes.append(f"garrison {step}: {n} of {beds} beds fit")
        return n

    def stables(self, F):
        """stables (Conwy / Caerphilly / Alnwick): stalls (hay + fences), a drain gully, the MARSHAL's chamber at one end and
        the GROOMS' room at the other (beds), a thatch gable (his 12:20)"""
        D, L = F.D, F.L
        Ui = D - 2
        self.fbox(F, 4, mat=PANEL, floor=GRAVEL)
        self.ffill(F, 1, 0, 4, Ui, 4, 4, PANEL); self.fdoor(F, 1, 0, 4, "vm")
        self.ffill(F, 1, 0, L - 5, Ui, 4, L - 5, PANEL); self.fdoor(F, 1, 0, L - 5, "vp")
        self.fbed(F, Ui - 1, 0, 1, "vp", role="servant", office="marshal")
        self.fput(F, 1, 0, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
        self.fbed(F, Ui - 1, 0, L - 4, "vp", role="servant", office="groom")
        if Ui >= 5:
            self.fbed(F, Ui - 3, 0, L - 4, "vp", role="servant", office="groom")
        self.froom(F, "marshal", 1, Ui, 1, 3, 0); self.fzone(F, "quarters", 1, Ui, 0, 1, 3)
        self.froom(F, "grooms", 1, Ui, L - 4, L - 2, 0)
        for v in range(6, L - 6, 3):
            self.fput(F, Ui, 0, v, "minecraft:hay_block", pillar_axis="y")
            self.fput(F, Ui - 1, 0, v, "minecraft:oak_fence")
        self.fgully(F, 2, L // 2, "stable")
        self.fput(F, 2, 3, L // 2 - 2, LIGHT); self.fput(F, 2, 3, 2, LIGHT); self.fput(F, 2, 3, L - 3, LIGHT); self.lights += 3
        self.fdoor(F, 0, 0, L // 2, "in")
        self.fdoor(F, 0, 0, L // 2 + 1, "in", hinge=1)
        self.froom(F, "stables", 1, Ui, 5, L - 6, 0)
        self.fzone(F, "stable", 1, Ui, 0, 5, L - 6)
        self.froof(F, 5, wood="thatch")

    def workshop(self, F, kind):
        """the working bailey (Conwy's smith, Harlech's bakehouse and granary): smithy (hearth, anvil, trough, drain) ·
        bakehouse (smokers = ovens) · granary (barrels, hay) — timber boxes, thatch gables"""
        D, L = F.D, F.L
        Ui = D - 2
        self.fbox(F, 4, mat=PANEL if kind != "smithy" else self.curtain, floor=COBBLE if kind != "granary" else FLOOR)
        self.fdoor(F, 0, 0, L // 2, "in")
        if kind == "smithy":
            x, z = F.w(Ui, 2); self.hearth(x, 0, z, F.d("out"), flue_to=5)
            self.fput(F, Ui - 2, 0, 3, "minecraft:anvil", direction=0, damage="undamaged")
            self.fmark(F, "station", "anvil", Ui - 2, 0, 4)
            self.fput(F, 1, 0, L - 2, "minecraft:cauldron")
            self.fgully(F, 2, L - 3, "smithy")
            self.fzone(F, "workfloor", 1, Ui, 0, 1, L - 2)
        elif kind == "bakehouse":
            for v in range(2, L - 1, 2):
                self.fput(F, Ui, 0, v, "minecraft:smoker", **{"minecraft:cardinal_direction": F.d("out")})
            self.fmark(F, "station", "oven", Ui - 1, 0, 2)
            x, z = F.w(2, 2); self.table(x, 0, z)
            self.fzone(F, "kitchen", 1, Ui, 0, 1, L - 2)
        else:
            for v in range(1, L - 1):
                if v != L // 2:
                    self.fput(F, Ui, 0, v, "minecraft:barrel", facing_direction=1, open_bit=False)
            self.fput(F, 1, 0, 1, "minecraft:hay_block", pillar_axis="y"); self.fput(F, 1, 0, L - 2, "minecraft:hay_block", pillar_axis="y")
            self.fmark(F, "station", "store", Ui - 1, 0, 2)
            self.fzone(F, "storeroom", 1, Ui, 0, 1, L - 2)
        self.fput(F, D // 2, 3, L // 2, LIGHT); self.lights += 1
        self.froom(F, kind, 1, Ui, 1, L - 2, 0)
        self.froof(F, 5, wood="thatch" if kind != "smithy" else None, kind="gable")

    def keep(self, cx, cz, half, h, toward, door_off=0):
        """the DONJON (Hedingham 16 x 18 m, walls 3.4 m, five floors, the hall two storeys high; Vincennes' corner turrets
        and latrine tower; Dover's mural chambers): walls 3, a BASEMENT (-4..-2), ground store, the GREAT CHAMBER double
        height (stand 5, clear to 13) with a 3-wide balcony gallery at stand 10, the SOLAR (lord + children), the
        TREASURY behind a jib panel, the roof deck; a B_tower spiral in an interior corner from the basement to the roof;
        GARDEROBES on every storey (recess + chute in the wall, offset per storey) to the culverts; corner turrets."""
        x0, x1, z0, z1 = cx - half, cx + half, cz - half, cz + half
        self.fill(x0, -5, z0, x1, -1, z1, self.tower_mat)
        self.fill(x0, 0, z0, x1, h, z1, self.tower_mat)
        i0, i1, k0, k1 = x0 + 3, x1 - 3, z0 + 3, z1 - 3
        self.clear(i0, i1, k0, k1, -4, -2)
        self.clear(i0, i1, k0, k1, 0, h - 1)
        self.fill(i0, -1, k0, i1, -1, k1, FLOOR)
        slabs = [4, 14, 19]
        for f in slabs:
            self.slab(i0, i1, k0, k1, f, FLOOR, light_up=2)
        # the gallery at stand 10 (floor 9), 3 wide round the great chamber
        for x in range(i0, i1 + 1):
            for z in range(k0, k1 + 1):
                if min(x - i0, i1 - x, z - k0, k1 - z) <= 2:
                    self.put(x, 9, z, FLOOR)
        self.fill(i0, h, k0, i1, h, k1, self.dress)
        self.light(i0 + 2, -3, k0 + 2); self.light(i1 - 2, -3, k1 - 2)
        self.light((i0 + i1) // 2, 8, (k0 + k1) // 2); self.light((i0 + i1) // 2, 12, (k0 + k1) // 2)
        # windows (slits low, two-light windows in the great chamber and solar)
        for z in range(k0 + 1, k1, 4):
            for xw in (x0, x1):
                self.fill(xw, 6, z, xw, 8, z, GLASS); self.fill(xw, 16, z, xw, 17, z, GLASS)
        # the door: a wooden double door 3 deep on the ward side
        tdx, tdz = toward
        if tdx:
            wx = x1 if tdx > 0 else x0
            dz_ = cz + door_off
            for i in range(3):
                self.fill(wx - tdx * i, 0, dz_, wx - tdx * i, 1, dz_ + 1, AIR)
            self.door(wx, 0, dz_, "east" if tdx < 0 else "west", mat="minecraft:dark_oak_door")
            self.door(wx, 0, dz_ + 1, "east" if tdx < 0 else "west", mat="minecraft:dark_oak_door", hinge=1)
        else:
            wz = z1 if tdz > 0 else z0
            dx_ = cx + door_off
            for i in range(3):
                self.fill(dx_, 0, wz - tdz * i, dx_ + 1, 1, wz - tdz * i, AIR)
            self.door(dx_, 0, wz, "south" if tdz < 0 else "north", mat="minecraft:dark_oak_door")
            self.door(dx_ + 1, 0, wz, "south" if tdz < 0 else "north", mat="minecraft:dark_oak_door", hinge=1)
        # the spiral: an interior corner away from the door
        far = [(i1 - 4, k1 - 4), (i0 + 1, k1 - 4), (i1 - 4, k0 + 1), (i0 + 1, k0 + 1)]
        far.sort(key=lambda c: -((c[0] + 1.5 - cx) * -tdx + (c[1] + 1.5 - cz) * -tdz))
        mids = [0, 5, 10, 15, 20]
        P = self.spiral2([("B_tower", fx, fz) for fx, fz in far], -4, mids + [h + 1], "stone", ceiling=h + 2, label="keep", caphouse=True,
                         fallback=lambda: self.spiral(far[0][0], far[0][1], -4, h - 1))
        well = P["well"] if P else (far[0][0], far[0][1], far[0][0] + 2, far[0][1] + 2)
        # the gallery rail (never beside the stair well)
        for x in range(i0, i1 + 1):
            for z in range(k0, k1 + 1):
                if min(x - i0, i1 - x, z - k0, k1 - z) == 3:
                    if not (well[0] - 2 <= x <= well[2] + 2 and well[1] - 2 <= z <= well[3] + 2):
                        self.put(x, 10, z, RAIL)
        # the solar (stand 15): the lord and the children (his 17:52)
        free = [(x, z) for x in range(i0 + 1, i1) for z in range(k0 + 1, k1) if not (well[0] - 2 <= x <= well[2] + 2 and well[1] - 2 <= z <= well[3] + 2)]
        def bed_in(fl, role, office):
            for (x, z) in free:
                for hd in ("south", "east", "north", "west"):
                    dx, dz = VEC[hd]
                    if (x + dx, z + dz) in free and self.get(x, fl, z) == AIR and self.get(x + dx, fl, z + dz) == AIR \
                            and self.get(x, fl - 1, z) == FLOOR and self.get(x + dx, fl - 1, z + dz) == FLOOR \
                            and all(self.get(x + ax, fl, z + az) in (AIR, None) for ax in (-1, 0, 1) for az in (-1, 0, 1) if (ax, az) != (dx, dz) and (ax, az) != (0, 0)):
                        self.bed(x, fl, z, hd, role=role, office=office)
                        free.remove((x, z))
                        return True
            return False
        bed_in(15, "lord", "lord"); bed_in(15, "child", "lord's children")
        self.marker("station", "seat", (i0 + i1) // 2, 5, (k0 + k1) // 2 + 2)
        self.zone("chamber", i0, 5, k0, i1, k1)
        self.zone("quarters", i0, 15, k0, i1, k1)
        self.zone("storeroom", i0, -4, k0, i1, k1)
        # the treasury (stand 20): a panelled partition along one side, entered by a JIB PANEL (R12 hidden)
        tz_ = k1 - 3 if well[1] < (k0 + k1) / 2 else k0 + 3
        side_z = range(tz_, k1 + 1) if tz_ > (k0 + k1) / 2 else range(k0, tz_ + 1)
        wall_z = tz_
        self.fill(i0, 20, wall_z, i1, 23, wall_z, PANEL)
        jx = (i0 + i1) // 2
        self.put(jx, 20, wall_z, "pw:jib_panel"); self.put(jx, 21, wall_z, "pw:jib_panel")
        for x in range(i0, i1 + 1, 2):
            zz = k1 if tz_ > (k0 + k1) / 2 else k0
            self.barrel(x, 20, zz)
        hi_side = tz_ > (k0 + k1) / 2
        self.room("treasury", i0, i1, (tz_ + 1) if hi_side else k0, k1 if hi_side else (tz_ - 1), 20)
        self.poi["hidden"].append({"what": "keep treasury", "panel": [jx, 20, wall_z], "inside": [jx, 20, wall_z + (1 if tz_ > (k0 + k1) / 2 else -1)]})
        # rooms
        self.room("keep_basement", i0, i1, k0, k1, -4)
        self.room("keep_ground", i0, i1, k0, k1, 0)
        self.room("keep_greatchamber", i0, i1, k0, k1, 5)
        self.room("keep_solar", i0, i1, k0, k1, 15)
        # garderobes: a recess in the inner layer + a chute in the middle layer, offset per storey, on the side of the door
        gside_z = z0 if tdz >= 0 else z1                     # a wall away from the door when the door faces z
        for n_, st in enumerate((0, 5, 15, 20)):
            gx = i0 + 1 + 2 * n_
            if gx > i1 - 1:
                break
            zi = gside_z + (2 if gside_z == z0 else -2)       # the inner layer cell
            zm = gside_z + (1 if gside_z == z0 else -1)       # the middle layer
            self.fill(gx, st, zi, gx, st + 1, zi, AIR)
            self.put(gx, st, zi, "minecraft:smooth_stone_slab", **{"minecraft:vertical_half": "bottom"})
            self.fill(gx, -7, zm, gx, st, zm, AIR)
            for f in range(-7, st + 1):
                self.channel.add((gx, f, zm))
            self.heads.append((gx, st, zm, "garderobe"))
            self.infra["chutes"] += 1
        # corner turrets (Vincennes 6.6 m): r 2 rising 5 over the parapet
        for (tx, tz) in ((x0, z0), (x0, z1), (x1, z0), (x1, z1)):
            for x in range(tx - 2, tx + 3):
                for z in range(tz - 2, tz + 3):
                    if math.hypot(x - tx, z - tz) <= 2.4:
                        self.fill(x, h - 6, z, x, h + 4, z, self.tower_mat)
            for (x, z) in ((tx - 2, tz), (tx + 2, tz), (tx, tz - 2), (tx, tz + 2)):
                self.put(x, h + 5, z, self.tower_mat)
        edge = [(x, z0) for x in range(x0, x1 + 1)] + [(x1, z) for z in range(z0 + 1, z1 + 1)] + [(x, z1) for x in range(x1 - 1, x0 - 1, -1)] + [(x0, z) for z in range(z1 - 1, z0, -1)]
        self.parapet_run(edge, h + 1)
        fp = {(x, z) for x in range(x0 - 2, x1 + 3) for z in range(z0 - 2, z1 + 3)}
        self.poi["footprints"].append(fp)
        self.poi["towers"].append({"cx": cx, "cz": cz, "r": half, "floors": [-5, 4, 9, 14, 19], "inner": [(x, z) for x in range(i0, i1 + 1) for z in range(k0, k1 + 1)],
                                   "h": h, "check": True, "door": False, "kind": "keep", "spiral": "B_tower" if P else "newel"})
        for (x, z) in fp:
            self.occ.add((x, z))
        self.poi["walk"] = {w for w in self.poi["walk"] if (w[0], w[2]) not in fp}
        self.poi["mural"] = {w for w in self.poi["mural"] if (w[0], w[2]) not in fp}
        return (x0, x1, z0, z1)

    # ---------------------------------------------------------------- beds in tower floors (garrison G2 / G4)
    def tower_beds(self, want, step, kinds=("tower",)):
        """bunks on tower floors that carry no through-route (not the walk, not the mural passage, not the roof deck)"""
        n = 0
        for t in self.poi["towers"]:
            if n >= want or t.get("kind") not in kinds or t["r"] < 4:
                continue
            sp = next((s for s in self.spirals if s.get("label") == f"{t['kind']} {t['cx']},{t['cz']}" and "well" in s), None)
            well = sp["well"] if sp else (t["cx"] - 1, t["cz"] - 1, t["cx"], t["cz"])
            bad_lv = {t.get("walk"), 4 if t.get("mural") else None, t["h"]}
            for fl in t["floors"]:
                if n >= want or fl in bad_lv:
                    continue
                f = fl + 1
                inner = set(t["inner"])
                cands = sorted(inner, key=lambda c: -math.hypot(c[0] - t["cx"], c[1] - t["cz"]))
                per = 0
                for (x, z) in cands:
                    if n >= want or per >= (2 if t["r"] == 4 else 4):
                        break
                    if well[0] - 2 <= x <= well[2] + 2 and well[1] - 2 <= z <= well[3] + 2:
                        continue
                    for hd in ("north", "south", "east", "west"):
                        dx, dz = VEC[hd]
                        b = (x + dx, z + dz)
                        if b not in inner or (well[0] - 2 <= b[0] <= well[2] + 2 and well[1] - 2 <= b[1] <= well[3] + 2):
                            continue
                        if all(self.get(cx_, f, cz_) == AIR and self.get(cx_, f + 1, cz_) == AIR and self.get(cx_, f - 1, cz_) == FLOOR for (cx_, cz_) in ((x, z), b)):
                            # keep the floor's ring passable: no bed beside another bed
                            if any(self.get(x + ax, f, z + az) == "minecraft:bed" for ax in (-2, -1, 0, 1, 2) for az in (-2, -1, 0, 1, 2)):
                                continue
                            # (231) the foot needs a free, floored orthogonal neighbour (a D-tower's corner cells are
                            # boxed in by the rim: the bed was there but its marker could not be reached, A lord 3)
                            if not any((x + ax, z + az) != b and self.get(x + ax, f, z + az) == AIR and self.get(x + ax, f + 1, z + az) == AIR
                                       and self.get(x + ax, f - 1, z + az) == FLOOR for ax, az in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                                continue
                            self.bed(x, f, z, OPP[hd] if False else hd, role="guard", step=step, office="men-at-arms")
                            n += 1; per += 1
                            break
        return n


# ------------------------------------------------------------------------------------------------ geometry
def ring_points(v, inset, front=0):
    """the corner points of a curtain ring inset from the box edge; the FIRST EDGE is on the gate side (x small) and
    always runs along z (v0.3: even polygons are turned so an edge, not a vertex, faces the gate)"""
    W = v.W
    a, b = inset, W - 1 - inset
    if v.plan == "square":
        return [(a, b), (a, a), (b, a), (b, b)]
    if v.plan == "rect" and v.skin == "A":
        d = int((W - 2 * v.o) * 0.12)
        e = min(d, 8) if v.rect_long_x else min(d, 14)            # x: the gate side keeps room for the bridge + barbican
        return [(a - e, b), (a - e, a), (b + e, a), (b + e, b)] if v.rect_long_x else [(a, b + e), (a, a - e), (b, a - e), (b, b + e)]
    if v.plan == "rect":
        d = int((W - 2 * v.o) * 0.12) if v.skin == "A" else int(W * 0.08)
        return [(a + d, b), (a + d, a), (b - d, a), (b - d, b)] if v.rect_long_x else [(a, b - d), (a, a + d), (b, a + d), (b, b - d)]
    n = int(v.plan[-1])
    cx, cz, R = W / 2, W / 2, (W / 2 - inset)
    R = R / math.cos(math.pi / n) * 0.93                     # the flat gate edge sits near the inset line
    pts = []
    for i in range(n):
        ang = math.pi + math.pi / n + 2 * math.pi * i / n
        pts.append((int(round(cx + R * math.cos(ang))), int(round(cz + R * math.sin(ang)))))
    pts = [(max(a, min(b, x)), max(a, min(b, z))) for (x, z) in pts]
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2) for i in range(n)]
    i = mids.index(min(mids))
    return pts[i:] + pts[:i]


def point_in_poly(poly, x, z):
    inside = False
    n = len(poly)
    for i in range(n):
        (x0, z0), (x1, z1) = poly[i], poly[(i + 1) % n]
        if (z0 > z) != (z1 > z):
            xi = x0 + (z - z0) * (x1 - x0) / (z1 - z0)
            if x < xi:
                inside = not inside
    return inside


def seg_dist(px, pz, a, b):
    (x0, z0), (x1, z1) = a, b
    dx, dz = x1 - x0, z1 - z0
    L2 = dx * dx + dz * dz
    t = 0 if L2 == 0 else max(0, min(1, ((px - x0) * dx + (pz - z0) * dz) / L2))
    return math.hypot(px - (x0 + t * dx), pz - (z0 + t * dz))


def poly_dist(poly, x, z):
    return min(seg_dist(x, z, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def shrink(poly, k, cx, cz):
    out = []
    for (x, z) in poly:
        vx, vz = cx - x, cz - z
        L = math.hypot(vx, vz) or 1
        out.append((x + vx / L * k, z + vz / L * k))
    return out


def inscribed_rect(poly, cx, cz, margin=0):
    def ok(hx, hz):
        return all(point_in_poly(poly, cx + sx * hx, cz + sz * hz) for sx in (-1, 1) for sz in (-1, 1))
    best = None
    for hx in range(4, 200, 1):
        if not ok(hx, 4):
            break
        hz = 4
        while ok(hx, hz + 1):
            hz += 1
        if best is None or hx * hz > best[0] * best[1]:
            best = (hx, hz)
    hx, hz = best or (8, 8)
    hx -= margin; hz -= margin
    return int(cx - hx), int(cx + hx), int(cz - hz), int(cz + hz)


def tower_spots(c, pts, spacing=32, skip=()):
    """corners + intermediate points so no curtain run between towers is longer than `spacing` (Carcassonne 18-30 m);
    spots within the `skip` (x, z, radius) discs (gatehouses, posterns) are left out"""
    spots = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        spots.append(a)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, math.ceil(L / spacing))
        for j in range(1, k):
            spots.append((round(a[0] + (b[0] - a[0]) * j / k), round(a[1] + (b[1] - a[1]) * j / k)))
    out = []
    for (x, z) in spots:
        if any(math.hypot(x - sx, z - sz) <= sr for (sx, sz, sr) in skip):
            continue
        if any(math.hypot(x - ox, z - oz) < 6 for (ox, oz) in out):
            continue
        out.append((x, z))
    return out


def between_spots(a, b, spacing=32):
    """the z of a point on edge a-b midway between two of its tower spots (a postern never displaces a tower)"""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    k = max(1, math.ceil(L / spacing))
    j0 = (k - 1) // 2
    t = (j0 + 0.5) / k
    return int(round(a[1] + (b[1] - a[1]) * t))


def place_search(c, kinds, region_ok, prefer, notes_tag=""):
    """the scored search (v0.2) generalised to four door sides: each (kind, D, L, builder) takes the best clear rect whose
    corners pass region_ok, whose cells avoid c.occ, and whose door side has 3 clear cells of ward in front"""
    placed = []
    for kind, D, L, build_fn, score_fn in kinds:
        best = None
        for side in ("x0", "x1", "z0", "z1"):
            dx, dz = (D, L) if side in ("x0", "x1") else (L, D)
            for x0 in range(0, c.v.W - dx, 2):
                for z0 in range(0, c.v.W - dz, 2):
                    rect = (x0, x0 + dx - 1, z0, z0 + dz - 1)
                    if not all(region_ok(px, pz) for px in (rect[0], rect[1]) for pz in (rect[2], rect[3])):
                        continue
                    if any((x, z) in c.occ for x in range(rect[0], rect[1] + 1) for z in (rect[2], rect[3])) or \
                       any((x, z) in c.occ for z in range(rect[2], rect[3] + 1) for x in (rect[0], rect[1])) or \
                       (rect[0] + rect[1]) // 2 in () or any((x, z) in c.occ for x in range(rect[0], rect[1] + 1, 3) for z in range(rect[2], rect[3] + 1, 3)):
                        continue
                    F = Frame(rect, side)
                    fx, fz = F.w(-3, F.L // 2)
                    if not region_ok(fx, fz):
                        continue
                    if any(F.w(-du, vv) in c.occ for du in (1, 2) for vv in range(1, F.L - 1, 2)):
                        continue
                    sc = score_fn(rect, side)
                    if best is None or sc < best[0]:
                        best = (sc, rect, side)
        if best is None:
            c.notes.append(f"{kind} SKIPPED (no clear spot{notes_tag})")
            continue
        _, rect, side = best
        F = Frame(rect, side)
        build_fn(F)
        c.poi["footprints"].append({(x, z) for x in range(rect[0], rect[1] + 1) for z in range(rect[2], rect[3] + 1)})
        c.block_occ(*rect, margin=2)
        for du in range(1, 4):
            for vv in range(0, F.L):
                c.occ.add(F.w(-du, vv))
        placed.append((kind, rect, side))
    return placed


# ------------------------------------------------------------------------------------------------ the underground
def infrastructure(c, ward_rect, gate_z, rear_z, ward_cells_fn):
    """the WATER law: the ring trench under the ward edge, trunks to the town junction (under the gate) and the outfall
    (rear box edge), the well shaft + feeder, every drain head by culvert, gullies every 16 x 16 of open ward"""
    W = c.v.W
    tx0, tx1, tz0, tz1 = ward_rect
    F = F_TRENCH

    def carve(x, f, z):
        if c.inbox(x, z):
            c.put(x, f, z, AIR); c.channel.add((x, f, z))

    # the ring
    ring = [(x, tz0) for x in range(tx0, tx1 + 1)] + [(x, tz1) for x in range(tx0, tx1 + 1)] + \
           [(tx0, z) for z in range(tz0, tz1 + 1)] + [(tx1, z) for z in range(tz0, tz1 + 1)]
    for (x, z) in ring:
        carve(x, F, z); carve(x, F + 1, z); c.trench.add((x, z))
    # the trunk to the town junction (under the gate passage, x 0) and to the outfall (x W-1)
    zj = max(tz0, min(tz1, gate_z))
    zo = max(tz0, min(tz1, rear_z))
    trunk_j = lpath((tx0, zj), (tx0 - 3, zj), "x") + lpath((tx0 - 3, zj), (tx0 - 3, gate_z), "z")[1:] + lpath((tx0 - 3, gate_z), (0, gate_z), "x")[1:]
    trunk_o = lpath((tx1, zo), (tx1 + 3, zo), "x") + lpath((tx1 + 3, zo), (tx1 + 3, rear_z), "z")[1:] + lpath((tx1 + 3, rear_z), (W - 1, rear_z), "x")[1:]
    for (x, z) in trunk_j + trunk_o:
        carve(x, F, z); carve(x, F + 1, z); c.trench.add((x, z))
    c.put(W - 1, F + 1, rear_z, BARS)                         # the outfall grate (upper cell; D-C533 stand-in)
    c.infra["junction"] = [0, F, gate_z]
    c.infra["outfall"] = [W - 1, F, rear_z]
    c.marker("port", "sewer", 0, F, gate_z)
    return ring


def well(c, wx, wz):
    """the ward well (D-C533 well law): a 3 x 3 head, a lined 1 x 1 shaft of water SOURCES from the head to the trench
    level, a lined feeder at trench level to the nearest trench cell"""
    c.fill(wx - 1, -1, wz - 1, wx + 1, -1, wz + 1, COBBLE)
    G.wall_ring(c, [(wx - 1, wz - 1), (wx, wz - 1), (wx + 1, wz - 1), (wx + 1, wz), (wx + 1, wz + 1), (wx, wz + 1), (wx - 1, wz + 1), (wx - 1, wz)], 0)
    c.put(wx, 0, wz, AIR)
    for f in range(F_TRENCH, 0):
        c.put(wx, f, wz, WATER); c.water_ok.add((wx, f, wz))
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c.reserved.add((wx + dx, wz + dz))
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for f in range(F_TRENCH, -1):
            if c.get(wx + dx, f, wz + dz) in (DIRT, GRASS, None):
                c.put(wx + dx, f, wz + dz, LINING)
    c.marker("port", "well", wx + 2, 0, wz)
    c.infra["well"] = [wx, F_TRENCH, wz]
    # the feeder: from beside the shaft bottom to the nearest trench cell
    tgt = min(c.trench, key=lambda t: abs(t[0] - wx) + abs(t[1] - wz))
    path = lpath((wx, wz), tgt, first="x")
    for (x, z) in path[1:]:
        c.put(x, F_TRENCH, z, AIR); c.put(x, F_TRENCH + 1, z, AIR); c.channel.add((x, F_TRENCH, z)); c.channel.add((x, F_TRENCH + 1, z))
    c.reserved -= {(x, z) for (x, z) in path[1:]}


def lpath(a, b, first="x"):
    (x0, z0), (x1, z1) = a, b
    out = [(x0, z0)]
    x, z = x0, z0
    order = ("x", "z") if first == "x" else ("z", "x")
    for ax in order:
        if ax == "x":
            while x != x1:
                x += 1 if x1 > x else -1; out.append((x, z))
        else:
            while z != z1:
                z += 1 if z1 > z else -1; out.append((x, z))
    return out


def route_heads(c):
    """every drain head falls by its shaft to the culvert level and runs by an L-shaped culvert (-8..-7) to the nearest
    trench cell, where a drop shaft takes it down to the trench (-14..-13); culverts never cross the well's columns"""
    tr = sorted(c.trench)
    for (x, f, z, kind) in c.heads:
        for ff in range(F_CULVERT, f + 1):
            c.put(x, ff, z, AIR); c.channel.add((x, ff, z))
        tgt = min(tr, key=lambda t: abs(t[0] - x) + abs(t[1] - z))
        path = None
        for first in ("x", "z"):
            p = lpath((x, z), tgt, first)
            if not any(q in c.reserved for q in p):
                path = p; break
        if path is None:
            # a dog-leg around the reserved columns
            for off in (3, -3, 5, -5):
                p = lpath((x, z), (x + off, z), "x") + lpath((x + off, z), tgt, "z")[1:]
                if not any(q in c.reserved for q in p):
                    path = p; break
        if path is None:
            c.notes.append(f"drain {kind} at {x},{z}: no culvert route"); continue
        for (px, pz) in path:
            c.put(px, F_CULVERT, pz, AIR); c.put(px, F_CULVERT + 1, pz, AIR)
            c.channel.add((px, F_CULVERT, pz)); c.channel.add((px, F_CULVERT + 1, pz))
        ex, ez = path[-1]
        for ff in range(F_TRENCH + 2, F_CULVERT):
            c.put(ex, ff, ez, AIR); c.channel.add((ex, ff, ez))


def gullies(c, cells_ok, step=16):
    """a gully every 16 x 16 of open ward: an iron grate in the paving over the head"""
    n = 0
    for x in range(step // 2, c.v.W, step):
        for z in range(step // 2, c.v.W, step):
            if not cells_ok(x, z):
                continue
            if c.get(x, -1, z) in (STONEBR, GRASS, GRAVEL, COBBLE, c.curtain) and c.get(x, 0, z) in (None, AIR) and \
                    all(c.get(x + dx, 0, z + dz) in (None, AIR) for dx in (-1, 0, 1) for dz in (-1, 0, 1)) and (x, z) not in c.reserved:
                c.put(x, -1, z, BARS); c.heads.append((x, -2, z, "gully")); n += 1
    c.infra["gullies"] += n


def sluice(c, corner, out_dir, outfall_z):
    """the SLUICE TOWER (Caerphilly, Felton's Tower) + the CASCADE (the 15:0x 10-05 test: a dammed body + a 1-wide lip feeds
    a stepped race forever): from the moat cell `corner`, a lip at water level, a 3-step race, a basin with a fountain jet,
    a drop shaft, a culvert at trench level to the outfall trunk. A square tower (r 3) stands over the lip."""
    mx, mz = corner
    dx, dz = out_dir
    px, pz = -dz, dx
    x, z = mx, mz
    cells = []
    # the lip (feet -1) and the race steps at -2, -3, -4 (2 long each)
    k = 1
    for depth, ln in ((-1, 2), (-2, 2), (-3, 2), (-4, 2)):
        for _ in range(ln):
            cx_, cz_ = mx + dx * k, mz + dz * k
            c.put(cx_, depth - 1, cz_, SMOOTH)
            c.fill(cx_, depth, cz_, cx_, 0, cz_, AIR)
            for s in (-1, 1):
                c.fill(cx_ + px * s, depth - 1, cz_ + pz * s, cx_ + px * s, 0, cz_ + pz * s, LINING)
            cells.append((cx_, depth, cz_))
            k += 1
    # the basin: 3 x 3, floor -7, open to the sky; the fountain jet on a pillar in its middle
    bx, bz = mx + dx * (k + 1), mz + dz * (k + 1)
    c.fill(bx - 2, -7, bz - 2, bx + 2, 0, bz + 2, LINING)
    c.fill(bx - 1, -6, bz - 1, bx + 1, 0, bz + 1, AIR)
    c.fill(mx + dx * (k - 1), -5, mz + dz * (k - 1), mx + dx * k, -4, mz + dz * k, AIR)
    c.fill(bx, -6, bz, bx, -5, bz, LINING)
    c.put(bx, -4, bz, WATER); c.water_ok.add((bx, -4, bz))
    c.infra["fountain"].append([bx, -4, bz])
    # the drop shaft at the basin's far side, down to the trench level, and the culvert to the outfall trunk
    sx, sz = bx + dx, bz + dz
    for ff in range(F_TRENCH, -6):
        c.put(sx, ff, sz, AIR); c.channel.add((sx, ff, sz))
    path = lpath((sx, sz), (sx, outfall_z), "z")
    for (qx, qz) in path:
        c.put(qx, F_TRENCH, qz, AIR); c.put(qx, F_TRENCH + 1, qz, AIR); c.channel.add((qx, F_TRENCH, qz)); c.channel.add((qx, F_TRENCH + 1, qz))
    c.infra["sluice"] = {"lip": [mx + dx, -1, mz + dz], "basin": [bx, -6, bz], "drop": [sx, F_TRENCH, sz], "race": len(cells)}
    # the sluice tower over the race head (beside it, on the counterscarp)
    side = 1
    for s_ in (1, -1):
        tx, tz = mx + dx * 3 + px * 4 * s_, mz + dz * 3 + pz * 4 * s_
        if c.inbox(tx + 3, tz + 3) and c.inbox(tx - 3, tz - 3) and all(c.get(tx + ax, -1, tz + az) not in (WATER, AIR, None) for ax in (-3, 0, 3) for az in (-3, 0, 3)):
            side = s_; break
    tx, tz = mx + dx * 3 + px * 4 * side, mz + dz * 3 + pz * 4 * side
    rec = c.tower(tx, tz, 3, 9, "square", floors=[4], toward=(tx + px * side * 10, tz + pz * side * 10), kind="sluicetower")
    c.door_pass(only=[rec])                                  # (231) the sluice is built after the castle's door pass
    c.marker("station", "post", tx, 5, tz)
    return rec


def moat_feed(c, corner, out_dir):
    """the FEED PORT (water law capture): a lined race from the moat's upstream corner to the box edge, closed at the moat
    by a sluice board (spruce planks) the clock lifts when it joins captured water"""
    mx, mz = corner
    dx, dz = out_dir
    x, z = mx + dx, mz + dz
    n = 0
    while c.inbox(x, z) and c.get(x, 0, z) in (AIR, None) and c.get(x, -1, z) not in (WATER,):
        c.put(x, -3, z, LINING); c.fill(x, -2, z, x, -1, z, AIR)
        for s in (-1, 1):
            c.fill(x - dz * s, -3, z + dx * s, x - dz * s, -1, z + dx * s, LINING)
        x += dx; z += dz; n += 1
    c.fill(mx + dx, -2, mz + dz, mx + dx, -1, mz + dz, DECK)        # the sluice board
    c.infra["feed"] = {"from": [mx + dx, -2, mz + dz], "to": [x - dx, -2, z - dz], "length": n, "closed": "sluice board (spruce planks)"}


def garderobes(c, every=12):
    """garderobes off the mural passage (Bodiam's 28; Conwy's town-wall latrines): a recess at t 2 with a stone seat at the
    passage level, its chute in t 3 down to the culvert level — routed to the SEWER, not the moat (the water law)"""
    fps = set()
    for fp in c.poi["footprints"]:
        fps |= fp
    n = 0
    for seg in getattr(c, "segments", []):
        if not seg["mural"]:
            continue
        nx, nz = seg["n"]
        cells = seg["cells"]
        for i in range(6, len(cells) - 6, every):
            x, z = cells[i]
            mw = seg.get("mural_w", 1)
            p1, p2, p3 = [(x + nx * t, z + nz * t) for t in (mw, mw + 1, mw + 2)]
            if mw + 2 >= seg["thick"]:
                continue
            if any(q in fps for q in (p1, p2, p3)) or (p1[0], 5, p1[1]) not in c.poi["mural"]:
                continue
            if not all(c.get(q[0], f, q[1]) == c.curtain for q in (p2, p3) for f in (5, 6)):
                continue
            c.fill(p2[0], 5, p2[1], p2[0], 6, p2[1], AIR)
            c.put(p2[0], 5, p2[1], "minecraft:smooth_stone_slab", **{"minecraft:vertical_half": "bottom"})
            for f in range(F_CULVERT, 6):
                c.put(p3[0], f, p3[1], AIR); c.channel.add((p3[0], f, p3[1]))
            c.heads.append((p3[0], 5, p3[1], "garderobe"))
            n += 1
    c.infra["chutes"] += n


def line_channels(c):
    for (x, f, z) in list(c.channel):
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0), (0, 1, 0)):
            q = (x + dx, f + dy, z + dz)
            if q in c.channel:
                continue
            nm = c.get(*q)
            if nm in (DIRT, GRASS) and q[1] <= -2:
                c.put(*q, LINING)


# ------------------------------------------------------------------------------------------------ hidden ways (231)
F_TUNNEL = -11                                       # the sally tunnel's standing level (floor -12, ceiling -9): between the
                                                     # culverts (-8..-7) and the trench (-14..-13), crossing neither
SALLY_MAT = "minecraft:stone_brick_stairs"


def _flight_cells(start, d, f_top, f_bot):
    """a straight flight from standing f_top (at `start`) down to standing f_bot along d: [(x, z, standing)] k = 1.."""
    (x, z), (dx, dz) = start, d
    return [(x + dx * k, z + dz * k, f_top - k) for k in range(1, f_top - f_bot + 1)]


def sally_tunnel(c, room_key, toward, keep_out, label="sally tunnel"):
    """the SALLY TUNNEL (Dover's 13th-c. tunnels to the northern entrance [KENT-DOVER]; Harlech's Way from the Sea; the
    10-06 inventory #25): from the cellar / basement `room_key` (standing -4) through a JIB PANEL in its wall, a flight of
    stone stairs (3 clear over every tread, the stair law) down to the tunnel at standing -11 (1 wide, 2 high, lined, lit),
    under the ward, the curtains and the moat to beyond `keep_out` (a predicate: cells the exit may NOT use), then a flight
    up into a small CONDUIT HOUSE outside the walls (Dover's rain-water / conduit precedent: a plain stone hut with a door);
    the stair head there is a closet behind a second JIB PANEL. Both panels are SEALED for R6 and recorded for R12.
    Routes avoid every drain channel (R9) and the well's columns. Returns the record or None (a note says why)."""
    import heapq
    if room_key not in c.poi["rooms"]:
        c.notes.append(f"{label}: no room {room_key}"); return None
    x0, x1, z0, z1, rf = c.poi["rooms"][room_key]
    W = c.v.W
    tx, tz = toward
    chan_cols = {}
    for (x, f, z) in c.channel:
        if -13 <= f <= -3:
            chan_cols.setdefault((x, z), set()).add(f)

    def near_channel(x, z, f_lo, f_hi):
        for ax in (-1, 0, 1):
            for az in (-1, 0, 1):
                fs = chan_cols.get((x + ax, z + az))
                if fs and any(f_lo <= f <= f_hi for f in fs):     # the trench may run UNDER the tunnel floor (-13 vs -12)
                    return True
        return False

    def solid_ground(x, z, f_lo, f_hi):
        """every cell f_lo..f_hi of the column is earth / masonry (no void, water, cellar)"""
        if not (2 <= x < W - 2 and 2 <= z < W - 2) or (x, z) in c.reserved:
            return False
        for f in range(f_lo, f_hi + 1):
            nm = c.get(x, f, z)
            if nm in (None, AIR, WATER) or (x, f, z) in c.channel:
                return False
        return not near_channel(x, z, f_lo, f_hi)

    # 1. the panel: a wall cell of the room on the side facing `toward`, the passage behind it to open earth
    sides = []
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if dx:
            xs = x1 if dx > 0 else x0
            cand = [(xs, z) for z in range(z0 + 1, z1)]
        else:
            zs = z1 if dz > 0 else z0
            cand = [(x, zs) for x in range(x0 + 1, x1)]
        sides.append(((dx, dz), cand))
    sides.sort(key=lambda sd: -((sd[0][0] * (tx - (x0 + x1) / 2)) + sd[0][1] * (tz - (z0 + z1) / 2)))
    start = None
    for (d, cand) in sides:
        dx, dz = d
        cand.sort(key=lambda q: abs(q[0] - (x0 + x1) / 2) + abs(q[1] - (z0 + z1) / 2))
        for (ix, iz) in cand:
            if c.get(ix, rf, iz) != AIR or c.get(ix, rf + 1, iz) != AIR or c.get(ix, rf - 1, iz) in (None, AIR, WATER):
                continue
            # through the wall: masonry cells (<= 4) then the flight in solid earth
            wall = []
            k = 1
            while k <= 5 and c.get(ix + dx * k, rf, iz + dz * k) not in (None, AIR, WATER, DIRT, GRASS):
                wall.append((ix + dx * k, iz + dz * k)); k += 1
            if not wall or k > 5:
                continue
            head = (ix + dx * (k - 1), iz + dz * (k - 1))
            fl = _flight_cells(head, d, rf, F_TUNNEL)
            if all(solid_ground(x, z, f - 1, f + 3) for (x, z, f) in fl) and not any((x, z) in c.occ and c.get(x, 0, z) not in (AIR,) and False for (x, z, f) in fl):
                start = (d, wall, fl)
                break
        if start:
            break
    if not start:
        c.notes.append(f"{label}: no clear wall + flight out of {room_key}"); return None
    d, wall, fl_down = start
    bottom = (fl_down[-1][0], fl_down[-1][1])

    # 2. the exits: a flight up (11) + the conduit house (7 long, 5 wide) on open grass beyond keep_out
    up_n = 0 - F_TUNNEL
    exits = {}
    for x in range(4, W - 4, 2):
        for z in range(4, W - 4, 2):
            for e in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ex, ez = e
                px, pz = -ez, ex
                T = (x + ex * up_n, z + ez * up_n)
                hut = [(T[0] + ex * a + px * b, T[1] + ez * a + pz * b) for a in range(-3, 7) for b in range(-2, 3)]
                if any(not (2 <= hx < W - 2 and 2 <= hz < W - 2) or keep_out(hx, hz) or (hx, hz) in c.occ for (hx, hz) in hut):
                    continue
                if any(c.get(hx, -1, hz) != GRASS or any(c.get(hx, f, hz) not in (AIR, None) for f in range(0, 5)) for (hx, hz) in hut):
                    continue
                fl = [(x + ex * k, z + ez * k, F_TUNNEL + k) for k in range(1, up_n + 1)]
                if all(solid_ground(qx, qz, f - 1, min(f + 2, -2)) for (qx, qz, f) in fl if f <= -3):
                    exits[(x, z)] = e
    if not exits:
        c.notes.append(f"{label}: no exit site beyond the walls"); return None

    # 3. the tunnel: A* at F_TUNNEL from the flight's foot to the nearest exit foot (orthogonal steps)
    def ok(x, z):
        return solid_ground(x, z, F_TUNNEL - 1, F_TUNNEL + 2)
    goal = set(exits)
    gl = list(goal)
    def hfun(x, z):
        return min(abs(x - gx) + abs(z - gz) for (gx, gz) in gl[:400]) if len(gl) <= 400 else 0
    used_fl = {(x, z) for (x, z, f) in fl_down}
    openq = [(0, 0, bottom)]
    came = {bottom: None}
    gcost = {bottom: 0}
    found = None
    n_iter = 0
    while openq and n_iter < 200000:
        n_iter += 1
        _, g, cur = heapq.heappop(openq)
        if cur in goal and cur != bottom:
            found = cur; break
        cx_, cz_ = cur
        for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = cx_ + dx, cz_ + dz
            if (nx, nz) in came or (nx, nz) in used_fl or not ok(nx, nz):
                continue
            came[(nx, nz)] = cur
            gcost[(nx, nz)] = g + 1
            heapq.heappush(openq, (g + 1 + hfun(nx, nz), g + 1, (nx, nz)))
    if not found:
        c.notes.append(f"{label}: no tunnel route ({n_iter} steps searched)"); return None
    path = []
    q = found
    while q is not None:
        path.append(q); q = came[q]
    path.reverse()
    e = exits[found]
    ex, ez = e
    px, pz = -ez, ex
    fl_up = [(found[0] + ex * k, found[1] + ez * k, F_TUNNEL + k) for k in range(1, up_n + 1)]
    T = (fl_up[-1][0], fl_up[-1][1])

    carved = []

    def carve(x, f, z):
        c.put(x, f, z, AIR); carved.append((x, f, z))

    # the panel + the passage through the wall (2 high at the room's level)
    (wx0, wz0) = wall[0]
    for (x, z) in wall:
        carve(x, rf, z); carve(x, rf + 1, z)
    c.put(wx0, rf, wz0, "pw:jib_panel"); c.put(wx0, rf + 1, wz0, "pw:jib_panel")
    # the flight down: the tread at standing - 1, 3 clear over it
    hi_down = DIRNAME[(-d[0], -d[1])]
    for (x, z, f) in fl_down:
        c.stairs(x, f - 1, z, hi_down, mat=SALLY_MAT)
        for ff in range(f, f + 3):
            carve(x, ff, z)
        # the step behind needs the same 3 over its tread: the cell above this tread's predecessor stays clear
    # the tunnel
    for i, (x, z) in enumerate(path):
        carve(x, F_TUNNEL, z); carve(x, F_TUNNEL + 1, z)
        c.put(x, F_TUNNEL - 1, z, LINING)
        if i % 8 == 4:
            c.light(x, F_TUNNEL + 1, z); carved.append((x, F_TUNNEL + 1, z))
    # the flight up
    hi_up = DIRNAME[e]
    for (x, z, f) in fl_up:
        c.stairs(x, f - 1, z, hi_up, mat=SALLY_MAT)
        for ff in range(f, f + 3):
            carve(x, ff, z)
    # line everything carved underground
    cs = set(carved) | {(x, f - 1, z) for (x, z, f) in fl_down + fl_up}
    for (x, f, z) in list(carved):
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)):
            q = (x + dx, f + dy, z + dz)
            if q in cs:
                continue
            if c.get(*q) in (DIRT, GRASS) and q[1] <= -1:
                c.put(*q, LINING)
    # the conduit house: the flight's last cells under a stone hood, the closet, the panel, the room, the door
    def at(a, b):
        return (T[0] + ex * a + px * b, T[1] + ez * a + pz * b)
    mat = c.curtain
    for a in range(-3, 2):                                  # the hood over the flight head + closet: walls at b +-1
        for b in (-1, 1):
            hx, hz = at(a, b); c.fill(hx, 0, hz, hx, 3, hz, mat)
        hx, hz = at(a, 0)
        c.put(hx, 4, hz, mat)
        if a >= -2:
            c.fill(hx, 0, hz, hx, 3, hz, AIR) if a >= 0 else None
    for a in range(-3, 0):                                  # over the treads: clear to 3, roofed at 4
        hx, hz = at(a, 0)
        c.fill(hx, 0, hz, hx, 3, hz, AIR)
    hx, hz = at(-4, 0); c.fill(hx, 0, hz, hx, 4, hz, mat)  # the hood's back
    for b in (-1, 0, 1):
        hx, hz = at(-4, b); c.fill(hx, 0, hz, hx, 4, hz, mat)
    hx, hz = at(1, 0); c.put(hx, -1, hz, LINING)           # the closet floor
    pnl = at(2, 0)
    for b in (-2, -1, 1, 2):                                # the partition with the jib panel
        hx, hz = at(2, b); c.fill(hx, 0, hz, hx, 4, hz, mat)
    c.put(pnl[0], 0, pnl[1], "pw:jib_panel"); c.put(pnl[0], 1, pnl[1], "pw:jib_panel"); c.fill(pnl[0], 2, pnl[1], pnl[0], 4, pnl[1], mat)
    for a in range(2, 8):                                   # the room a 3..6, walls b +-2, door at a 7
        for b in range(-2, 3):
            hx, hz = at(a, b)
            if a in (2, 7) or abs(b) == 2:
                if a != 2:
                    c.fill(hx, 0, hz, hx, 3, hz, mat)
            else:
                c.put(hx, -1, hz, SMOOTH); c.fill(hx, 0, hz, hx, 3, hz, AIR)
            c.put(hx, 4, hz, mat)
    dx_, dz_ = at(7, 0)
    c.door(dx_, 0, dz_, DIRNAME[e])
    lx, lz = at(4, 1); c.light(lx, 3, lz)
    rx0, rz0 = at(3, -1); rx1, rz1 = at(6, 1)
    c.room("conduithouse", rx0, rx1, rz0, rz1, 0)
    c.marker("station", "post", *at(5, 0)[:1], 0, at(5, 0)[1]) if False else c.marker("station", "post", at(5, 0)[0], 0, at(5, 0)[1])
    c.poi["footprints"].append({at(a, b) for a in range(-4, 8) for b in range(-2, 3)})
    for a in range(-4, 8):
        for b in range(-2, 3):
            c.occ.add(at(a, b))
    # sealing (R6) + the hidden record (R12)
    for f in (0, 1):
        c.poi["sealed"].add((pnl[0], f, pnl[1]))
    for f in (rf, rf + 1):
        c.poi["sealed"].add((wx0, f, wz0))
    mid = path[len(path) // 2]
    rec = {"what": label, "panel": [wx0, rf, wz0], "panels": [[wx0, rf, wz0], [pnl[0], 0, pnl[1]]],
           "inside": [mid[0], F_TUNNEL, mid[1]], "length": len(path) + len(fl_down) + len(fl_up),
           "from": room_key, "exit": [T[0], 0, T[1]], "tunnel_cells": [[x, F_TUNNEL, z] for (x, z) in path]}
    c.poi["hidden"].append(rec)
    c.infra.setdefault("sally", []).append({k: rec[k] for k in ("from", "exit", "length")})
    c.tunnel = getattr(c, "tunnel", set()) | {(x, f, z) for (x, f, z) in carved if f <= -2}
    return rec


def lockup(c, gate):
    """the LOCK-UP (Dungeon: castle prisons "often served only a temporary need", "simply a single plain room with a heavy
    door" [W-DUNG]; the constable is responsible for the prisoners, R3 §4): in the north guard room of a gatehouse whose
    guards sleep upstairs, a 3-deep cell behind a stone partition with an IRON door (villagers cannot open it: custody)"""
    xa, xb, za, gz = gate["xa"], gate["xb"], gate["za"], gate["gz"]
    z0, z1 = za + 1, gz - 5
    xp = xa + 5
    if xp >= xb - 3 or z1 - z0 < 3:
        return None
    c.fill(xp, 0, z0, xp, 3, z1, c.curtain)
    zd = (z0 + z1) // 2
    c.fill(xp, 0, zd, xp, 1, zd, AIR)
    c.door(xp, 0, zd, "west", mat="minecraft:iron_door")
    c.light(xa + 3, 2, zd)
    c.room("lockup", xa + 2, xp - 1, z0, z1, 0)
    c.notes.append("lock-up: iron door — architecture only (CIVITAS has no crime / custody yet, his 10:15 drop list)")
    return (xa + 2, xp - 1, z0, z1)


# ------------------------------------------------------------------------------------------------ skin A
def ground(c):
    W = c.v.W
    c.fill(0, -15, 0, W - 1, -2, W - 1, DIRT)
    c.fill(0, -1, 0, W - 1, -1, W - 1, GRASS)


def build_A(c):
    v = c.v
    W = v.W
    lord = v.size_name == "lord"
    moat_w = v.moat_w if v.moat_kind != "none" else 0
    berm = 4
    inset_outer = v.o + 6 + (berm + moat_w if v.moat_kind != "none" else 0)
    outer = ring_points(v, inset_outer)
    inner = ring_points(v, inset_outer + 22)
    # the gate: on the first (gate-side) edge, offset along it
    a, b = outer[0], outer[1]
    gz = int((a[1] + b[1]) / 2 + v.gate_offset * abs(b[1] - a[1]) * 0.6)
    gx = a[0]
    a2 = inner[0]
    gx2 = a2[0]
    # the rear: the edge whose midpoint lies furthest from the gate side
    def rear_edge(pts):
        n = len(pts)
        best = max(range(n), key=lambda i: (pts[i][0] + pts[(i + 1) % n][0]) / 2 - 0.001 * i)
        p, q = pts[best], pts[(best + 1) % n]
        return p, q
    rp, rq = rear_edge(outer)
    rz = int((rp[1] + rq[1]) / 2)
    # the curtains: outer 3 thick, inner 5 thick with the mural passage
    for i in range(len(outer)):
        c.wall_segment(outer[i], outer[(i + 1) % len(outer)], v.outer_h, thick=3)
    for i in range(len(inner)):
        c.wall_segment(inner[i], inner[(i + 1) % len(inner)], v.inner_h, thick=5, mural=True)
    c.poi["rings"] = [outer, inner]
    moat = set()
    if v.moat_kind != "none":
        moat = c.dig_moat(c.moat_cells(outer, berm, moat_w), v.moat_kind)
    # the gatehouses (outer: the constable; inner: the lord's apartments, two storeys)
    c.gatehouse(gx, gz, 3, v.outer_h, 1, role="constable", pit=v.moat_kind != "none", n_port=v.portcullises)
    c.gatehouse(gx2, gz, 5, v.inner_h, 2, role="lord", pit=False, n_port=v.portcullises, bed_step="G2")
    # posterns: their spots (the rear edges' midpoints along x)
    rxi = max(p[0] for p in inner)
    rxo = max(p[0] for p in outer)
    rz_o = between_spots(*rear_edge(outer))
    rz_i = between_spots(*rear_edge(inner))
    skip_o = [(gx, gz, 17), (rxo, rz_o, 6)]
    skip_i = [(gx2, gz, 17), (rxi, rz_i, 6)]
    for (x, z) in tower_spots(c, outer, 32, skip_o):
        c.tower(x, z, 4, v.outer_h + 5, v.tower_shape, walk=v.outer_h - 2)
    for (x, z) in tower_spots(c, inner, 32, skip_i):
        c.tower(x, z, 5, v.inner_h + 6, v.tower_shape, walk=v.inner_h - 2, mural=True)
    # the posterns: inner (inner ward -> outer ward) and outer (outer ward -> berm), on the rear axis at z = rz
    def open_at(x, z):
        return c.get(x, 0, z) in (None, AIR) and c.get(x, 1, z) in (None, AIR) and c.get(x, -1, z) not in (None, AIR, WATER)
    def scan(x, z, dx=1, lim=40):
        """from the open cell (x, z) step +x to the first wall, then on to the first open cell beyond it"""
        while open_at(x + dx, z) and lim > 0:
            x += dx; lim -= 1
        x2 = x + dx
        while not open_at(x2, z) and lim > 0:
            x2 += dx; lim -= 1
        return x, x2
    xi_in, xi_out = scan(int(W / 2), rz_i)
    c.postern((xi_in, rz_i), (xi_out, rz_i), (1, 0), seal=False, label="inner postern")
    c.block_occ(xi_in - 5, xi_out + 1, rz_i - 1, rz_i + 1, margin=2)
    c.poi["footprints"].append({(x, rz_i) for x in range(xi_in, xi_out + 1)})
    grown = shrink(inner, -2, W / 2, W / 2)
    xs = next(x for x in range(int(W / 2), W) if not point_in_poly(grown, x, rz_o) and open_at(x, rz_o))
    xo_in, xo_out = scan(xs, rz_o)
    c.postern((xo_in, rz_o), (xo_out, rz_o), (1, 0), seal=True, label="outer postern")
    c.block_occ(xo_in - 3, xo_out + 1, rz_o - 1, rz_o + 1, margin=2)
    c.poi["footprints"].append({(x, rz_o) for x in range(xo_in, xo_out + 1)})
    if moat:
        mz_cells = sorted(x for (x, z) in moat if z == rz_o and x > xo_in)
        if mz_cells:
            c.bridge(mz_cells[0] - 1, mz_cells[-1] + 1, rz_o - 1, rz_o, posts=True)
            c.fill(mz_cells[-1] + 2, -1, rz_o - 1, mz_cells[-1] + 4, -1, rz_o, DECK)   # the landing beyond (the 'sea stair' foot)
    # the bridge over the moat at the gate, the barbican, the approach
    span = (gz - 2, gz + 1)
    out_x = gx - berm - moat_w - 1
    if v.moat_kind != "none":
        c.bridge(out_x, gx - berm - 1, span[0], span[1])
    if v.barbican:
        bx0, bx1, bz0, bz1 = c.barbican(out_x - 1, gz)
        c.poi["gate_out"] = (max(0, bx0 - 3), 0, gz)
        approach_to = bx0 - 1
    else:
        c.poi["gate_out"] = (max(0, out_x - 2), 0, gz)
        approach_to = out_x
    for x in range(0, approach_to + 1):
        for z in range(span[0], span[1] + 1):
            if c.get(x, -1, z) == GRASS:
                c.put(x, -1, z, PATH)
    # the enclosure polygon (outer curtain interior, shrunk) for the verifier; the ward paving
    cx, cz = W / 2, W / 2
    c.poi["inside_poly"] = shrink(outer, 3 + 3, cx, cz)
    inner_poly = shrink(inner, 5, cx, cz)
    for x in range(W):
        for z in range(W):
            if point_in_poly(c.poi["inside_poly"], x, z) and c.get(x, -1, z) == GRASS and not point_in_poly(inner_poly, x, z):
                c.put(x, -1, z, GRAVEL)
    ix0, ix1, iz0, iz1 = inscribed_rect(shrink(inner, 6, cx, cz), cx, cz, margin=1)
    for x in range(ix0, ix1 + 1):
        for z in range(iz0, iz1 + 1):
            if point_in_poly(inner_poly, x, z) and c.get(x, -1, z) in (GRASS, GRAVEL):
                c.put(x, -1, z, GRASS if (ix0 + 8 <= x <= ix1 - 8 and iz0 + 8 <= z <= iz1 - 8) else STONEBR)
    # the inner ward's ranges (scored search, any door side): hall, kitchen, chapel, household lodgings
    wx, wz = (ix0 + ix1) // 2, (iz0 + iz1) // 2
    c.reserved |= {(wx + dx, wz + dz) for dx in range(-3, 4) for dz in range(-3, 4)}
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            c.occ.add((wx + dx, wz + dz))
    def in_inner(x, z):
        return ix0 <= x <= ix1 and iz0 <= z <= iz1 and point_in_poly(inner_poly, x, z)
    hD, hL = (14, 38) if lord else (19, 52)
    hall_h = 13 if lord else 16
    def hall_b(F):
        F.back_windows = True
        c.hall(F, hall_h, v.hall_roof)
    kinds = [("hall", hD, hL, hall_b, lambda r, s: (ix1 - r[1]) * 2 + abs((r[2] + r[3]) / 2 - wz) + (0 if s in ("x0",) else 20)),
             ("kitchen", 11, 17, lambda F: c.kitchen(F), lambda r, s: (r[0] - ix0) + abs(r[2] - iz0)),
             ("chapel", 11, 25 if lord else 29, lambda F: c.chapel(F, 10 if lord else 13), lambda r, s: (ix1 - r[1]) + abs(r[3] - iz1)),
             ("lodgings", 11, 20 if lord else 26, lambda F: c.lodgings(F, 2, beds_per_bay=2, role="noble", office="household / guests"),
              lambda r, s: abs((r[0] + r[1]) / 2 - wx) + abs(r[2] - iz0))]
    placed = place_search(c, kinds, in_inner, None, " in the inner ward")
    # the outer ward: the working bailey + the garrison (G3; grand G4 a second range)
    outer_poly_in = shrink(outer, 4, cx, cz)
    inner_grown = shrink(inner, -6, cx, cz)
    def in_outer_ward(x, z):
        return point_in_poly(outer_poly_in, x, z) and not point_in_poly(inner_grown, x, z)
    bk = [("garrison", 9, 13, lambda F: c.garrison(F, 6, "G3"), lambda r, s: 0),
          ("garrison_b", 9, 13, lambda F: c.garrison(F, 6, "G3"), lambda r, s: abs((r[0] + r[1]) / 2 - W / 2)),
          ("stables", 9, 13, lambda F: c.stables(F), lambda r, s: -r[0]),
          ("smithy", 7, 9, lambda F: c.workshop(F, "smithy"), lambda r, s: -r[0]),
          ("granary", 7, 11, lambda F: c.workshop(F, "granary"), lambda r, s: -r[0]),
          ("bakehouse", 7, 9, lambda F: c.workshop(F, "bakehouse"), lambda r, s: -r[0])]
    if not lord:
        bk.insert(2, ("garrison_c", 9, 13, lambda F: c.garrison(F, 6, "G3"), lambda r, s: 0))
        bk.insert(3, ("garrison_d", 9, 17, lambda F: c.garrison(F, 8, "G4"), lambda r, s: 0))
        bk.insert(1, ("garrison2", 9, 17, lambda F: c.garrison(F, 8, "G4"), lambda r, s: abs((r[0] + r[1]) / 2 - W / 2) + abs((r[2] + r[3]) / 2 - W / 2)))
    placed += place_search(c, bk, in_outer_ward, None, " in the outer ward")
    missing = [k[0] for k in bk if k[0] not in [p[0] for p in placed]]
    if missing:
        # what the outer ward could not hold goes into the inner ward
        placed += place_search(c, [k for k in bk if k[0] in missing], in_inner, None, " (inner ward fallback)")
    missing = [k for k in bk if k[0] not in [p[0] for p in placed]]
    if missing:
        # (231) a lean-to: 2 shallower (>= 7), 4 longer, against the curtain where the ring is tight (Bodiam's ranges)
        slim = [(k[0], max(7, k[1] - 2), k[2] + 4, k[3], k[4]) for k in missing]
        placed += place_search(c, slim, in_outer_ward, None, " (lean-to, outer ward)")
        left = [k for k in slim if k[0] not in [p[0] for p in placed]]
        if left:
            placed += place_search(c, left, in_inner, None, " (lean-to, inner ward)")
        c.notes = [n for n in c.notes if not any(n.startswith(p[0] + " SKIPPED") for p in placed)]
    c.poi["placed"] = [p[0] for p in placed]
    # the well; the ward's lamps
    well_pos = (wx, wz)
    return {"ward_rect": (ix0 + 2, ix1 - 2, iz0 + 2, iz1 - 2), "gate_z": gz, "rear_z": rz, "well": well_pos, "moat": moat,
            "outer": outer, "inner": inner, "in_ward": lambda x, z: point_in_poly(c.poi["inside_poly"], x, z),
            "sluice_ring": outer, "berm": berm, "moat_w": moat_w}


# ------------------------------------------------------------------------------------------------ skin B (Bodiam)
def build_B(c):
    v = c.v
    W = v.W
    lord = v.size_name == "lord"
    cx, cz = W / 2, W / 2
    inset_outer = 6 + (16 if v.barbican else 0)
    outer = ring_points(v, inset_outer)
    a, b = outer[0], outer[1]
    gz = int(W / 2)
    gx = a[0]
    rxo = max(p[0] for p in outer)
    rz = gz
    # the base court's curtain (3 thick, outer_h), its gatehouse, towers, postern
    for i in range(len(outer)):
        c.wall_segment(outer[i], outer[(i + 1) % len(outer)], v.outer_h, thick=3)
    # the quadrangle
    Q = v.quad
    q0 = int(cx - Q / 2)
    q1 = q0 + Q - 1
    quad = [(q0, q1), (q0, q0), (q1, q0), (q1, q1)]
    c.poi["rings"] = [outer, quad]
    # the lake / dry ditch round the quadrangle (Bodiam's moat-lake), dug before the quadrangle
    lake = set()
    if v.moat_kind != "none":
        lake = c.dig_moat(c.moat_cells(quad, 0.5, v.lake_w), v.moat_kind)
    for i in range(4):
        c.wall_segment(quad[i], quad[(i + 1) % 4], v.inner_h, thick=5, mural=True)
    c.gatehouse(gx, gz, 3, v.outer_h, 1, role="porter", pit=False, n_port=1, bed_step="G2")
    c.gatehouse(q0, gz, 5, v.inner_h, 1, role="constable", pit=v.moat_kind != "none", n_port=v.portcullises + (1 if lord else 0))
    # the keep at the keep corner (replaces that corner tower), towers: round corners, square mids
    kc = quad[v.keep_corner]
    if kc[0] == q0 and abs(kc[1] - gz) < 20:
        kc = quad[(v.keep_corner + 2) % 4]
    half = 9 if lord else 10
    ix_, iz_ = (1 if kc[0] == q0 else -1), (1 if kc[1] == q0 else -1)
    toward = (0, iz_)
    door_off = (half - 4) if ix_ > 0 else -(half - 3)
    keep_h = 24 if lord else 29
    # the postern: the rear mid (through a square postern tower)
    skip = [(q0, gz, 17), (kc[0], kc[1], 6)]
    rear_spots = [(x, z) for (x, z) in tower_spots(c, quad, 32, skip) if x == q1 and z not in (q0, q1)]
    for (x, z) in tower_spots(c, quad, 32, skip):
        if (x, z) in rear_spots:
            continue                                         # the rear side waits for the hall (the postern tower)
        corner = (x, z) in quad
        if corner:
            c.tower(x, z, 5, v.inner_h + 6, "round", walk=v.inner_h - 2, mural=True, toward=(cx, cz))
        else:
            nx = 1 if x == q1 else (-1 if x == q0 else 0)
            nz = 1 if z == q1 else (-1 if z == q0 else 0)
            c.tower(x + nx * 1, z + nz * 1, 3, v.inner_h + 5, "square", walk=v.inner_h - 2, mural=True, toward=(cx, cz))
    c.keep(kc[0], kc[1], half, keep_h, toward, door_off)
    # the base court towers + its postern
    n_o = len(outer)
    ri = max(range(n_o), key=lambda i: (outer[i][0] + outer[(i + 1) % n_o][0]) / 2 - 0.001 * i)
    rz_o = between_spots(outer[ri], outer[(ri + 1) % n_o])
    skip_o = [(gx, gz, 17), (rxo, rz_o, 6)]
    for (x, z) in tower_spots(c, outer, 32, skip_o):
        c.tower(x, z, 4, v.outer_h + 5, v.tower_shape if v.tower_shape != "d" else "round", walk=v.outer_h - 2, toward=(cx, cz))
    # the base court's postern (sealed for R6) at the rear, between two towers
    def open_at(x, z):
        return c.get(x, 0, z) in (None, AIR) and c.get(x, 1, z) in (None, AIR) and c.get(x, -1, z) not in (None, AIR, WATER)
    xs = q1 + v.lake_w + 6
    while not open_at(xs, rz_o) and xs < W - 2:
        xs += 1
    x_in = xs
    while open_at(x_in + 1, rz_o):
        x_in += 1
    x_out = x_in + 1
    while not open_at(x_out, rz_o) and x_out < W - 1:
        x_out += 1
    c.postern((x_in, rz_o), (x_out, rz_o), (1, 0), seal=True, label="base court postern")
    c.block_occ(x_in - 3, x_out, rz_o - 1, rz_o + 1, margin=2)
    c.poi["footprints"].append({(x, rz_o) for x in range(x_in, x_out + 1)})
    # the ranges against the curtain (fixed plan), clipped by the corner towers / keep
    T = 5
    lo, hi = q0 + T, q1 - T                       # the first / last free cell inside the curtain
    def clip(rect):
        x0, x1, z0, z1 = rect
        # shrink along the long axis until no cell is occupied by a tower / keep / gatehouse
        longx = (x1 - x0) >= (z1 - z0)
        def bad(r):
            return any((x, z) in occ_hard for x in range(r[0], r[1] + 1) for z in range(r[2], r[3] + 1))
        r = [x0, x1, z0, z1]
        for _ in range(60):
            if not bad(r):
                return tuple(r)
            if longx:
                if any((r[0], z) in occ_hard or (r[0] + 1, z) in occ_hard for z in range(r[2], r[3] + 1)):
                    r[0] += 1
                else:
                    r[1] -= 1
            else:
                if any((x, r[2]) in occ_hard or (x, r[2] + 1) in occ_hard for x in range(r[0], r[1] + 1)):
                    r[2] += 1
                else:
                    r[3] -= 1
        return tuple(r)
    occ_hard = set()
    for fp in c.poi["footprints"]:
        for (x, z) in fp:
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    occ_hard.add((x + dx, z + dz))
    placed = []
    hD = 14 if lord else 19
    hall_h = 13 if lord else 16
    hL = 38 if lord else 52
    # the far range: the hall (back wall against the curtain; the screens' back door leads to the postern)
    far = clip((hi - hD + 1, hi, lo, hi))
    zlen = far[3] - far[2] + 1
    hL = min(hL, zlen)
    if zlen >= 30:
        # the hall's service end toward the kitchen side (z small)
        hz0 = far[2] if (far[2] - lo) <= (hi - far[3]) else far[3] - hL + 1
        Fh = Frame((far[0], far[1], hz0, hz0 + hL - 1), "x0")
        Fh.back_windows = False
        c.hall(Fh, hall_h, v.hall_roof)
        c.poi["footprints"].append({(x, z) for x in range(Fh.rect[0], Fh.rect[1] + 1) for z in range(Fh.rect[2], Fh.rect[3] + 1)})
        placed.append("hall")
        screens_z = hz0 + 7
        c.block_occ(*Fh.rect, margin=1)
    else:
        c.notes.append(f"hall SKIPPED (far range {zlen} < {hL})"); screens_z = gz
    # the postern through the rear curtain at the screens (Bodiam's postern tower: a square tower over it); the rest of the
    # rear side gets square mid towers so no run is longer than 32
    c.tower(q1 + 2, screens_z, 3, v.inner_h + 5, "square", walk=v.inner_h - 2, mural=True, door=False, toward=(cx, screens_z), kind="posterntower")
    stops = sorted([q0, screens_z, q1])
    for za_, zb_ in zip(stops, stops[1:]):
        k = math.ceil((zb_ - za_) / 32)
        for j in range(1, k):
            zt = round(za_ + (zb_ - za_) * j / k)
            c.tower(q1 + 1, zt, 3, v.inner_h + 5, "square", walk=v.inner_h - 2, mural=True, toward=(cx, cz))
    c.postern((far[1], screens_z), (q1 + 7, screens_z), (1, 0), seal=False, label="quadrangle postern")
    # the side ranges (depth 11): z-small side = kitchen + household lodgings; z-large side = chapel + lodgings
    gate_rng = c.poi["gates"][-1]
    xs0, xs1 = gate_rng["xb"] + 2, (far[0] - 2 if "hall" in placed else hi - 12)
    for side, zr in (("z0", (lo, lo + 10)), ("z1", (hi - 10, hi))):
        seg = clip((xs0, xs1, zr[0], zr[1]))
        L = seg[1] - seg[0] + 1
        Fside = "z1" if side == "z0" else "z0"           # the door faces the court
        if side == "z0":
            kL = 17
            if L >= kL:
                Fk = Frame((seg[0], seg[0] + kL - 1, seg[2], seg[3]), Fside); Fk.back_windows = False
                c.kitchen(Fk); placed.append("kitchen")
                rest = (seg[0] + kL + 1, seg[1], seg[2], seg[3])
                if rest[1] - rest[0] + 1 >= 13:
                    Fl = Frame(rest, Fside); Fl.back_windows = False
                    c.lodgings(Fl, 2, beds_per_bay=2, role="servant", office="household (retainers)"); placed.append("lodgings")
        else:
            cL = 25 if lord else 29
            if L >= cL:
                Fc = Frame((seg[1] - cL + 1, seg[1], seg[2], seg[3]), Fside); Fc.back_windows = False
                c.chapel(Fc, 10 if lord else 13); placed.append("chapel")
                rest = (seg[0], seg[1] - cL - 1, seg[2], seg[3])
                if rest[1] - rest[0] + 1 >= 13:
                    Fl = Frame(rest, Fside); Fl.back_windows = False
                    c.lodgings(Fl, 2, beds_per_bay=2, role="noble", office="household / guests"); placed.append("lodgings")
    for (x0, x1, z0, z1) in []:
        pass
    # the gate range either side of the gatehouse: lodgings (household offices: the castellan's clerks + guests)
    for zr in ((lo + 12, gate_rng["za"] - 2), (gate_rng["zb"] + 2, hi - 12)):
        seg = clip((lo, lo + 8, zr[0], zr[1]))
        if seg[3] - seg[2] + 1 >= 13 and seg[1] - seg[0] >= 7:
            Fg = Frame(seg, "x1"); Fg.back_windows = False
            c.lodgings(Fg, 2, beds_per_bay=1, role="clerk", office="castellan's clerks", label="gatelodgings"); placed.append("gatelodgings")
    # the court
    court = (lo + 10, (far[0] - 2 if "hall" in placed else hi - 12), lo + 12, hi - 12)
    for x in range(court[0] - 1, court[1] + 2):
        for z in range(court[2] - 1, court[3] + 2):
            if c.get(x, -1, z) == GRASS:
                c.put(x, -1, z, STONEBR)
    for x in range(lo, hi + 1):
        for z in range(lo, hi + 1):
            if c.get(x, -1, z) == GRASS and c.get(x, 0, z) in (None, AIR):
                c.put(x, -1, z, STONEBR)
    # the bridges over the lake: front (to the quadrangle's pit) and rear (from the postern)
    if v.moat_kind != "none":
        c.bridge(q0 - 1 - v.lake_w - 1, q0 - 4, gz - 2, gz + 1)
        c.bridge(q1 + 2, q1 + 2 + v.lake_w + 1, screens_z, screens_z, posts=False)
    # the base court: enclosure poly, gate approach, bailey buildings
    c.poi["inside_poly"] = shrink(outer, 6, cx, cz)
    span = (gz - 2, gz + 1)
    if v.barbican:
        bx0, bx1, bz0, bz1 = c.barbican(gx - 5, gz)
        c.poi["gate_out"] = (max(0, bx0 - 3), 0, gz)
        approach_to = bx0 - 1
    else:
        c.poi["gate_out"] = (max(0, gx - 6), 0, gz)
        approach_to = gx - 4
    for x in range(0, approach_to + 1):
        for z in range(span[0], span[1] + 1):
            if c.get(x, -1, z) == GRASS:
                c.put(x, -1, z, PATH)
    qpoly = [(q0 - 1 - v.lake_w - 3, q0 - 1 - v.lake_w - 3), (q0 - 1 - v.lake_w - 3, q1 + v.lake_w + 4), (q1 + v.lake_w + 4, q1 + v.lake_w + 4), (q1 + v.lake_w + 4, q0 - 1 - v.lake_w - 3)]
    if v.moat_kind == "none":
        qpoly = [(q0 - 8, q0 - 8), (q0 - 8, q1 + 8), (q1 + 8, q1 + 8), (q1 + 8, q0 - 8)]
    inpoly = shrink(outer, 5, cx, cz)
    for x in range(W):
        for z in range(W):
            if point_in_poly(c.poi["inside_poly"], x, z) and c.get(x, -1, z) == GRASS and (abs(x - cx) < 3 or abs(z - cz) < 3):
                c.put(x, -1, z, GRAVEL)
    def in_base(x, z):
        return point_in_poly(inpoly, x, z) and not point_in_poly(qpoly, x, z)
    bk = [("garrison", 9, 13, lambda F: c.garrison(F, 6, "G3"), lambda r, s: 0),
          ("garrison_b", 9, 13, lambda F: c.garrison(F, 6, "G3"), lambda r, s: abs((r[0] + r[1]) / 2 - cx) * 0.2),
          ("stables", 9, 13, lambda F: c.stables(F), lambda r, s: (r[0] + r[1]) / 2),
          ("smithy", 7, 9, lambda F: c.workshop(F, "smithy"), lambda r, s: (r[0] + r[1]) / 2),
          ("granary", 7, 11, lambda F: c.workshop(F, "granary"), lambda r, s: -(r[0] + r[1]) / 2),
          ("bakehouse", 7, 9, lambda F: c.workshop(F, "bakehouse"), lambda r, s: -(r[0] + r[1]) / 2)]
    if not lord:
        bk.insert(2, ("garrison_c", 9, 13, lambda F: c.garrison(F, 6, "G3"), lambda r, s: 0))
        bk.insert(3, ("garrison_d", 9, 17, lambda F: c.garrison(F, 8, "G4"), lambda r, s: 0))
        bk.insert(1, ("garrison2", 9, 17, lambda F: c.garrison(F, 8, "G4"), lambda r, s: -abs((r[2] + r[3]) / 2 - cz)))
    placed += [p[0] for p in place_search(c, bk, in_base, None, " in the base court")]
    c.poi["placed"] = placed
    wx, wz = (court[0] + court[1]) // 2, (court[2] + court[3]) // 2
    c.reserved |= {(wx + dx, wz + dz) for dx in range(-3, 4) for dz in range(-3, 4)}
    return {"ward_rect": (court[0], court[1], court[2], court[3]), "gate_z": gz, "rear_z": screens_z if False else rz, "well": (wx, wz), "moat": lake,
            "outer": outer, "inner": quad, "in_ward": lambda x, z: point_in_poly(c.poi["inside_poly"], x, z), "sluice_ring": quad, "berm": 1,
            "moat_w": v.lake_w, "rxo": rxo, "qpoly": qpoly}


# ------------------------------------------------------------------------------------------------ the whole castle
def build(v):
    c = Castle(v)
    ground(c)
    S = build_A(c) if v.skin == "A" else build_B(c)
    W = v.W
    # garrison G2: bunks on tower floors (12); grand G4: the rest of the 60 on tower floors
    lord = v.size_name == "lord"
    have_g2 = sum(1 for b in c.bed_roles if b["step"] == "G2")
    c.tower_beds(max(0, 12 - have_g2), "G2")
    if not lord:
        have = sum(1 for b in c.bed_roles if b["role"] == "guard")
        have_g4 = sum(1 for b in c.bed_roles if b["step"] == "G4")
        c.tower_beds(max(0, 60 - have, 26 - have_g4), "G4")          # (231) G4 >= 26 (Krak's 60 by steps), not only 60 in all
    # the tower doors (after the ranges exist), the garderobes of the mural passages
    c.door_pass()
    garderobes(c)
    # the underground
    infrastructure(c, S["ward_rect"], S["gate_z"], S["rear_z"], None)
    well(c, *S["well"])
    # gullies over the open ward (inside the enclosure, never under a building)
    fps = set()
    for fp in c.poi["footprints"]:
        fps |= fp
    gullies(c, lambda x, z: S["in_ward"](x, z) and (x, z) not in fps)
    # the dry ditch: a gully every 24 along its bed
    if v.moat_kind == "dry":
        cells = sorted(S["moat"])
        for i, (x, z) in enumerate(cells):
            if i % 97 == 0 and c.get(x, -5, z) == GRASS and (x, z) not in c.reserved:
                c.put(x, -5, z, BARS); c.heads.append((x, -6, z, "ditch"))
    # the wet moat / lake: sluice at the downhill rear corner, the feed port at the upstream front corner
    if v.moat_kind == "wet":
        ring = S["sluice_ring"]
        sgn = v.sluice_side
        mc = max(S["moat"], key=lambda q: q[0] + sgn * q[1] * 0.999)
        fc = min(S["moat"], key=lambda q: q[0] - sgn * q[1] * 0.999)
        if v.skin == "A":
            sluice(c, mc, (1, 0), S["rear_z"])
            moat_feed(c, fc, (-1, 0))
        else:
            # inside the base court: the race runs along z away from the lake's rear corner
            sluice(c, mc, (0, sgn), S["rear_z"])
            moat_feed(c, fc, (0, -sgn))
    route_heads(c)
    line_channels(c)
    # (231) the hidden ways and the lock-up (inventory #25 / #26)
    gates = [g for g in c.poi["gates"] if g["top"] - g["xa"] >= 0]
    up = [g for g in c.poi["gates"] if g["role"] in ("lord", "constable") and (g["xb"] - g["xa"]) >= 12]
    if up:
        lockup(c, up[-1])
    outer = S["outer"]
    band = S["berm"] + S["moat_w"] + 4 if v.moat_kind != "none" else 6
    def keep_out(x, z):
        if v.skin == "B":
            # B: from the donjon under the lake to the BASE COURT (Raby / Kenilworth: the base court holds the horses) —
            # the box holds no ground beyond the base court's own curtain
            return point_in_poly(S["qpoly"], x, z) or not point_in_poly(c.poi["inside_poly"], x, z)
        return point_in_poly(outer, x, z) or poly_dist(outer, x, z) <= band
    src = next((k for k in ("keep_basement_0", "cellar_0") if k in c.poi["rooms"]), None)
    if src:
        sally_tunnel(c, src, (W - 1, S["rear_z"]), keep_out)
    # the well shaft's lining was laid; re-assert the sources (lining never replaces water)
    c.close_air()
    # the walk / mural cells that later work buried
    w = c
    def standing(x, f, z):
        return c.get(x, f, z) == AIR and c.get(x, f + 1, z) in (AIR, LIGHT) and c.get(x, f - 1, z) not in (None, AIR, LIGHT, WATER)
    c.poi["walk"] = {p for p in c.poi["walk"] if standing(*p)}
    c.poi["mural"] = {p for p in c.poi["mural"] if standing(*p)}
    # the ward cells for the verifier
    ward = []
    for x in range(W):
        for z in range(W):
            if c.get(x, -1, z) in (STONEBR, GRASS, GRAVEL, PATH) and c.get(x, 0, z) == AIR and c.get(x, 1, z) == AIR and point_in_poly(c.poi["inside_poly"], x, z):
                ward.append((x, z))
    c.poi["ward"] = ward
    c.S = S
    return c


# ------------------------------------------------------------------------------------------------ pieces, stages
def piece_spans(n, P=64):
    """F1 (castle 231): the 64-grid spans of a box edge n long — [(offset, length)], offsets on the grid, every index
    0..n-1 in exactly one span, the last span short when n is not a multiple of 64. (The v0.2 cut used n // 64 spans:
    144 -> 2 spans covering 128, so the far 16 rows / columns — towers, moat, curtain — were never written.)"""
    return [(o, min(P, n - o)) for o in range(0, n, P)]


def piece_key(i, j):
    return f"{i}{j}" if i < 10 and j < 10 else f"{i}_{j}"


def piece_ij(q):
    return tuple(int(t) for t in q.split("_")) if "_" in q else (int(q[0]), int(q[1]))


def cut(c):
    """F1: every cell of the model lands in exactly one 64 x sy x 64 piece, for ANY box width / depth (the castle box is
    also padded to the 64 grid by Variety, so this is the belt to that brace). A short edge piece keeps the full 64 size
    (the clock's rotated-group placement assumes uniform pieces); its overhang is structure void (-1), which never
    overwrites the world. Pieces share the model's palette (rows copied by slices). Returns {key: (Structure, markers)}."""
    sx, sy, sz = c.size
    st0 = c.st
    out = {}
    import copy
    for i, (ox, lx) in enumerate(piece_spans(sx)):
        for j, (oz, lz) in enumerate(piece_spans(sz)):
            st = M.Structure((64, sy, 64))
            st.palette = list(st0.palette); st._pal_index = dict(st0._pal_index)
            L0, L1 = st.layer0, st.layer1
            for x in range(lx):
                for y in range(sy):
                    s = ((ox + x) * sy + y) * sz + oz
                    d = (x * sy + y) * 64
                    L0[d:d + lz] = st0.layer0[s:s + lz]
                    L1[d:d + lz] = st0.layer1[s:s + lz]
            ents = []
            for e in getattr(st0, "entities", []):
                pos = [cc.value for cc in e.value["Pos"].value]
                if ox <= pos[0] < ox + lx and oz <= pos[2] < oz + lz:
                    ee = copy.deepcopy(e)
                    ee.value["Pos"] = M.lst(M.FLOAT, [M.f(pos[0] - ox), M.f(pos[1]), M.f(pos[2] - oz)])
                    ents.append(ee)
            st.entities = ents
            marks = [dict(m, cell=[m["cell"][0] - ox, m["cell"][1], m["cell"][2] - oz]) for m in c.markers
                     if ox <= m["cell"][0] < ox + lx and oz <= m["cell"][2] < oz + lz]
            out[piece_key(i, j)] = (st, marks)
    return out


def pieces_equal_model(c, pieces):
    """R13 (F1's test): the union of the cut pieces == the model, cell for cell (both layers); the overhang of short edge
    pieces is void; every marker lands in exactly one piece. Returns (ok, model_nonair, pieces_nonair, mismatches, markers)."""
    sx, sy, sz = c.size
    st0 = c.st
    air = {k for k, p in enumerate(st0.palette) if p[0] in (AIR,)}
    bad = 0
    n_model = sum(1 for k in st0.layer0 if k >= 0 and k not in air)
    n_pieces = 0
    for q, (st, marks) in pieces.items():
        i, j = piece_ij(q)
        ox, oz = i * 64, j * 64
        lx, lz = min(64, sx - ox), min(64, sz - oz)
        n_pieces += sum(1 for k in st.layer0 if k >= 0 and st.palette[k][0] != AIR)
        for x in range(64):
            for y in range(sy):
                d = (x * sy + y) * 64
                if x < lx:
                    s = ((ox + x) * sy + y) * sz + oz
                    if st.layer0[d:d + lz] != st0.layer0[s:s + lz] or st.layer1[d:d + lz] != st0.layer1[s:s + lz]:
                        bad += 1
                    if any(k != -1 for k in st.layer0[d + lz:d + 64]):
                        bad += 1
                elif any(k != -1 for k in st.layer0[d:d + 64]):
                    bad += 1
    n_marks = sum(len(m) for (_, m) in pieces.values())
    want = len(piece_spans(sx)) * len(piece_spans(sz))
    ok = bad == 0 and n_model == n_pieces and n_marks == len(c.markers) and len(pieces) == want
    return ok, n_model, n_pieces, bad, n_marks


FURNISH = ("minecraft:bed", "minecraft:lantern", "minecraft:light_block", "pw:furn_", "minecraft:barrel", "minecraft:hay_block", "minecraft:anvil",
           "minecraft:cauldron", "minecraft:lectern", "minecraft:smoker", "minecraft:furnace", "minecraft:chest", "minecraft:bell", "pw:hearth")
ROOFISH = ("pw:roof", "pw:rafter")
STAGES = ["plot", "masonry to feet 4", "masonry to the walk", "parapets roofs caps", "furnished"]


def stage_of(name, feet, walk_top):
    """the HEIGHT-BAND cutter (10-05 §3b, LC-1005-2), the palace's five stages by height:
    s0 plot = everything below grade (feet < 0: foundations, cellars, culverts, the trench, the moat; the dirt at feet <= -3
    is the land job's) · s1 masonry feet 0..4 · s2 masonry feet 5..walk_top-1 (the walk floor) · s3 everything from the walk
    level up (parapets, merlons, tower tops, upper storeys) + every pw:roof* / rafter · s4 furnishings + markers"""
    if feet < 0:
        return 0
    if name.startswith(FURNISH):
        return 4
    if name.startswith(ROOFISH):
        return 3
    if feet <= 4:
        return 1
    if feet < walk_top:
        return 2
    return 3


def stage_cut(c, st, walk_top):
    """cut one piece into s0..s4. Cells the land job provides (air at feet >= 0, dirt at feet <= -3) are structure void
    in every stage (the palace's light s0). Returns (stages, counts, implied)."""
    sx, sy, sz = st.size
    stages = []
    for _ in STAGES:
        s = M.Structure(st.size); s.palette = list(st.palette); s._pal_index = dict(st._pal_index)
        stages.append(s)
    counts = [0] * 5
    implied = 0
    cls = {}
    for k, p in enumerate(st.palette):
        cls[k] = p[0]
    for x in range(sx):
        for y in range(sy):
            feet = y - DATUM_Y
            base = (x * sy + y) * sz
            row = st.layer0[base:base + sz]
            for z, k in enumerate(row):
                if k < 0:
                    continue
                nm = cls[k]
                if (nm == AIR and feet >= 0) or (nm == DIRT and feet <= -3):
                    implied += 1
                    continue
                s = stage_of(nm, feet, walk_top)
                stages[s].layer0[base + z] = k
                counts[s] += 1
    for e in st.entities:
        stages[4].entities.append(e)
    # proof: stacking s0..s4 gives the piece except the land job's cells
    for x in range(sx):
        for y in range(sy):
            base = (x * sy + y) * sz
            for z in range(sz):
                want = st.layer0[base + z]
                got = [s.layer0[base + z] for s in stages if s.layer0[base + z] >= 0]
                if want < 0:
                    assert not got
                    continue
                nm = cls[want]
                if (nm == AIR and (y - DATUM_Y) >= 0) or (nm == DIRT and (y - DATUM_Y) <= -3):
                    assert not got, (x, y, z)
                else:
                    assert got == [want], (x, y, z, got, want)
    return stages, counts, implied


def write_all(c, stem, out_dir):
    d = Path(out_dir) / stem
    for sub in ("manifests", "structures", "stages"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    pieces = cut(c)
    ok, nm, npc, bad, nmk = pieces_equal_model(c, pieces)
    assert ok, f"R13 pieces != model: model {nm} pieces {npc} mismatched rows {bad} markers {nmk}/{len(c.markers)}"
    walk_top = (c.v.inner_h if c.v.skin == "A" else c.v.inner_h) - 1
    per = {}
    for q, (st, marks) in pieces.items():
        pstem = f"{stem}_{q}_a_r1"
        (d / "structures" / f"{pstem}.mcstructure").write_bytes(st.to_bytes())
        sx, sy, sz = st.size
        blocks = []
        for x in range(sx):
            for y in range(sy):
                for z in range(sz):
                    e = st.get(x, y, z)
                    if e is not None and e[0] != AIR:
                        blocks.append([x, y, z, e[0], {k: vv.value for k, vv in e[1].items()}])
        man = {"name": f"pw:{pstem}", "size": [sx, sy, sz], "datum_y": DATUM_Y, "blocks": blocks, "entities": marks}
        (d / "manifests" / f"{pstem}.json").write_text(json.dumps(man, separators=(",", ":")))
        stages, counts, implied = stage_cut(c, st, walk_top)
        for i, s in enumerate(stages):
            (d / "stages" / f"{pstem}_s{i}.mcstructure").write_bytes(s.to_bytes())
        beds = {}
        for b in c.bed_roles:
            if q == piece_key(b['x'] // 64, b['z'] // 64):
                key = b["role"] + (f"/{b['step']}" if b["step"] else "")
                beds[key] = beds.get(key, 0) + 1
        per[q] = {"blocks": len(blocks), "markers": len(marks), "stages": counts, "implied_by_land_job": implied, "beds": beds}
    return pieces, per, (ok, nm, npc, bad, nmk)


# ------------------------------------------------------------------------------------------------ renders
COL = {"minecraft:stone_bricks": (150, 150, 155), "minecraft:chiseled_stone_bricks": (120, 120, 130), "minecraft:cobblestone": (120, 115, 110),
       "minecraft:mossy_stone_bricks": (120, 150, 120), "minecraft:polished_andesite": (165, 165, 170), "minecraft:andesite": (140, 140, 140),
       "minecraft:polished_diorite": (220, 220, 220), DIRT: (110, 80, 50), GRASS: (90, 150, 70), GRAVEL: (150, 150, 140), WATER: (60, 110, 200),
       PANEL: (160, 120, 70), FLOOR: (200, 160, 100), POST: (100, 70, 40), GLASS: (160, 220, 255), LIGHT: None, SMOOTH: (190, 190, 190),
       BARS: (40, 40, 40), "minecraft:iron_door": (90, 90, 120), "minecraft:spruce_door": (230, 60, 60), "minecraft:dark_oak_door": (230, 60, 60),
       "minecraft:bed": (220, 100, 160), "minecraft:lantern": (255, 230, 120), "minecraft:hay_block": (220, 190, 80), RAIL: (140, 100, 60),
       "minecraft:barrel": (150, 110, 60), PATH: (170, 150, 90), "pw:jib_panel": (255, 120, 0)}


def colour(name):
    if name in COL:
        return COL[name]
    if name.endswith("_slab"):
        return (170, 170, 175)
    if name.startswith("pw:spiral"):
        return (255, 200, 0)
    if name.startswith("pw:roof"):
        return (120, 70, 50)
    if name.startswith("pw:"):
        return (120, 90, 60)
    if name in (AIR, VOID):
        return None
    return (200, 120, 200)


def plan_image(c, feet, title, S=3, reach=None):
    from PIL import Image, ImageDraw
    sx, sy, sz = c.size
    img = Image.new("RGB", (sz * S, sx * S), (20, 20, 24))
    px = img.load()
    reach_cols = {(x, z) for (x, f, z) in reach if f == feet} if reach else set()
    for x in range(sx):
        for z in range(sz):
            col = None
            for f in range(feet, -16, -1):
                e = c.st.get(x, DATUM_Y + f, z)
                if e is None:
                    continue
                cc = colour(e[0])
                if cc:
                    col = cc if f == feet else tuple(int(vv * 0.55) for vv in cc)
                    break
            if (x, z) in reach_cols:
                col = (60, 220, 90)
            if col:
                for i in range(S):
                    for j in range(S):
                        px[z * S + i, x * S + j] = col
    d = ImageDraw.Draw(img)
    for k in range(64, sx, 64):
        d.line([(0, k * S), (sz * S, k * S)], fill=(255, 0, 0), width=1)
    for k in range(64, sz, 64):
        d.line([(k * S, 0), (k * S, sx * S)], fill=(255, 0, 0), width=1)
    if title:
        d.text((4, 4), title, fill=(255, 255, 255))
    return img


def under_image(c, title, S=3):
    """the underground plan: trench (cyan), culverts (blue), drop shafts / chutes (white), cellars and basements (orange),
    water (deep blue), the well shaft (light blue)"""
    from PIL import Image, ImageDraw
    sx, sy, sz = c.size
    img = Image.new("RGB", (sz * S, sx * S), (30, 26, 22))
    px = img.load()
    for x in range(sx):
        for z in range(sz):
            col = None
            names = [c.get(x, f, z) for f in range(-15, 0)]
            def at(f):
                return names[f + 15]
            if at(-1) == WATER and at(-6) == WATER:
                col = (120, 180, 255)
            elif at(-14) == AIR or at(-13) == AIR:
                col = (0, 220, 220)
            elif at(-8) == AIR or at(-7) == AIR:
                col = (40, 90, 255)
            elif any(at(f) == AIR for f in (-4, -3, -2)) and at(-5) not in (AIR, None):
                col = (230, 140, 40)
            elif any(at(f) == AIR for f in range(-12, -8)):
                col = (255, 255, 255)
            elif at(-1) == WATER or at(-2) == WATER:
                col = (40, 70, 160)
            elif at(-1) not in (GRASS, DIRT, AIR, None):
                col = (70, 66, 60)
            if col:
                for i in range(S):
                    for j in range(S):
                        px[z * S + i, x * S + j] = col
    d = ImageDraw.Draw(img)
    for k in range(64, sx, 64):
        d.line([(0, k * S), (sz * S, k * S)], fill=(255, 0, 0), width=1)
    for k in range(64, sz, 64):
        d.line([(k * S, 0), (k * S, sx * S)], fill=(255, 0, 0), width=1)
    d.text((4, 4), title, fill=(255, 255, 255))
    return img


def elevation_image(c, S=3, title=""):
    from PIL import Image, ImageDraw
    sx, sy, sz = c.size
    img = Image.new("RGB", (sz * S, sy * S), (20, 20, 24))
    px = img.load()
    for z in range(sz):
        for y in range(sy):
            for x in range(sx):
                e = c.st.get(x, y, z)
                if e and colour(e[0]):
                    cc = colour(e[0])
                    shade = max(0.45, 1 - x / sx * 0.6)
                    cc = tuple(int(vv * shade) for vv in cc)
                    for i in range(S):
                        for j in range(S):
                            px[z * S + i, (sy - 1 - y) * S + j] = cc
                    break
    d = ImageDraw.Draw(img)
    d.line([(0, (sy - 1 - DATUM_Y) * S + S), (sz * S, (sy - 1 - DATUM_Y) * S + S)], fill=(255, 255, 0))
    if title:
        d.text((4, 4), title, fill=(255, 255, 255))
    return img


def render(c, stem, reach=None):
    RENDERS.mkdir(parents=True, exist_ok=True)
    S = 3 if c.v.W <= 192 else 2
    wf = c.v.inner_h - 1
    plan_image(c, 0, f"{stem} GROUND (feet 0) — gate side at the TOP; red = 64 grid; green = reached", S, reach).save(RENDERS / f"{stem}-plan-0.png")
    plan_image(c, wf, f"{stem} WALL-WALK (feet {wf})", S, reach).save(RENDERS / f"{stem}-plan-{wf}.png")
    plan_image(c, 8, f"{stem} GALLERY LEVEL (feet 8)", S, reach).save(RENDERS / f"{stem}-plan-8.png")
    under_image(c, f"{stem} UNDERGROUND: cyan trench -14, blue culverts -8, white drops, orange cellars, blue water", S).save(RENDERS / f"{stem}-under.png")
    elevation_image(c, S, f"{stem} ELEVATION from the gate side").save(RENDERS / f"{stem}-elevation.png")


VARIETIES = [("A", "lord", 2), ("A", "lord", 3), ("A", "lord", 4), ("A", "lord", 5), ("B", "lord", 1), ("B", "lord", 5), ("B", "lord", 3), ("B", "lord", 4),
             ("A", "grand", 1), ("B", "grand", 1)]


def plan_signature(v):
    """the ground-plan draws that make a castle read as a different castle from above: (plan, quad, keep corner, moat kind)"""
    return (v.plan, v.quad, v.keep_corner, v.moat_kind)


def variety_collisions(varieties=None):
    """FORCED VARIETY enforced: every pair of varieties whose plan_signature is the same (empty list = all distinct)"""
    varieties = VARIETIES if varieties is None else varieties
    sigs = [(t, plan_signature(Variety(*t))) for t in varieties]
    return [(a, b, sa) for i, (a, sa) in enumerate(sigs) for (b, sb) in sigs[i + 1:] if sa == sb]


def stem_of(v):
    return f"mvv_castle_{v.skin.lower()}{v.size_name[0]}{v.seed}"


def sheet(results, name="CASTLE-VARIETY-SHEET-v0_4.png"):
    """every variety on one sheet: ground plan (reached cells green), underground plan, elevation, the verdict"""
    from PIL import Image, ImageDraw
    S = 1
    tiles = []
    for (c, ok, rep, reach) in results:
        p0 = plan_image(c, 0, "", S + 1 if c.v.W <= 192 else S, reach)
        pu = under_image(c, "", S + 1 if c.v.W <= 192 else S)
        el = elevation_image(c, S + 1 if c.v.W <= 192 else S)
        verdict = ("CONSTRUCTED CORRECTLY" if ok else "NOT YET") + " — " + rep.get("summary", "")
        tiles.append((c.v.describe(), verdict, p0, pu, el))
    tw = max(t[2].width + t[3].width + t[4].width + 30 for t in tiles)
    rows = [max(t[2].height, t[4].height) + 44 for t in tiles]
    img = Image.new("RGB", (tw, sum(rows)), (10, 10, 12))
    d = ImageDraw.Draw(img)
    y = 0
    for (desc, verdict, p0, pu, el), rh in zip(tiles, rows):
        d.text((6, y + 4), desc, fill=(255, 255, 255))
        d.text((6, y + 18), verdict, fill=(120, 255, 140) if verdict.startswith("CONSTRUCTED") else (255, 160, 120))
        img.paste(p0, (6, y + 36)); img.paste(pu, (12 + p0.width, y + 36)); img.paste(el, (18 + p0.width + pu.width, y + 36 + p0.height - el.height))
        y += rh
    img.save(DOCS / name)
    print("sheet ->", DOCS / name)


def pack_castle(stem, out_dir, keep_raw=False):
    """(231) disk law (~2 GB free, 120 MB per raw 192 castle): the written castle is re-laid in BP-02's pack layout and
    tar-gzipped (~60x smaller): structures/pw/<stem>_<ij>_a_r1.mcstructure, structures/pw/stages/<...>_s0..s4.mcstructure,
    and the per-piece manifests under _manifests/ (tool side, not pack content). Returns (tgz path, bytes, md5, files)."""
    import hashlib
    import tarfile
    d = Path(out_dir) / stem
    tgz = Path(out_dir) / f"{stem}.tgz"
    n = 0
    with tarfile.open(tgz, "w:gz") as tf:
        for f in sorted((d / "structures").glob("*.mcstructure")):
            tf.add(f, arcname=f"structures/pw/{f.name}"); n += 1
        for f in sorted((d / "stages").glob("*.mcstructure")):
            tf.add(f, arcname=f"structures/pw/stages/{f.name}"); n += 1
        for f in sorted((d / "manifests").glob("*.json")):
            tf.add(f, arcname=f"_manifests/{stem}/{f.name}"); n += 1
        tf.add(d / "castle.json", arcname=f"_manifests/{stem}/castle.json"); n += 1
    if not keep_raw:
        import shutil
        for sub in ("structures", "stages", "manifests"):
            shutil.rmtree(d / sub, ignore_errors=True)
    data = tgz.read_bytes()
    return str(tgz), len(data), hashlib.md5(data).hexdigest(), n


def sheet_from_renders(rows, name="CASTLE-VARIETY-SHEET-v0_4.png", scale=0.5):
    """the variety sheet composed from the per-variety renders already on disk (one castle model in memory at a time):
    rows = [(stem, description, verdict)] -> ground plan | underground | elevation per row"""
    from PIL import Image, ImageDraw
    tiles = []
    for stem, desc, verdict in rows:
        ims = []
        for suf in ("plan-0", "under", "elevation"):
            im = Image.open(RENDERS / f"{stem}-{suf}.png").convert("RGB")
            ims.append(im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale)))))
        tiles.append((desc, verdict, ims))
    tw = max(sum(i.width for i in t[2]) + 30 for t in tiles)
    rows_h = [max(i.height for i in t[2]) + 44 for t in tiles]
    img = Image.new("RGB", (tw, sum(rows_h)), (10, 10, 12))
    d = ImageDraw.Draw(img)
    y = 0
    for (desc, verdict, ims), rh in zip(tiles, rows_h):
        d.text((6, y + 4), desc, fill=(255, 255, 255))
        d.text((6, y + 18), verdict, fill=(120, 255, 140) if verdict.startswith("CONSTRUCTED") else (255, 160, 120))
        x = 6
        for im in ims:
            img.paste(im, (x, y + 36 + (max(i.height for i in ims) - im.height))); x += im.width + 6
        y += rh
    img.save(DOCS / name)
    return DOCS / name


def castle_manifest(c, stem, per, r13, rep):
    beds = {}
    for b in c.bed_roles:
        beds[b["role"]] = beds.get(b["role"], 0) + 1
    steps = {}
    for b in c.bed_roles:
        if b["step"]:
            steps[b["step"]] = steps.get(b["step"], 0) + 1
    offices = {}
    for b in c.bed_roles:
        if b["office"]:
            offices[b["office"]] = offices.get(b["office"], 0) + 1
    n = c.v.W // 64
    return {"stem": stem, "version": VERSION, "variety": c.v.describe(), "box": [c.v.W, c.size[1], c.v.W], "datum_y": DATUM_Y,
            "grid": [n, n], "pieces": {q: dict(p, family=f"pw:{stem}_{q}_a_r1") for q, p in per.items()},
            "gate": {"side": "x0 (faces the square, K6)", "z": c.S["gate_z"]}, "beds": {"by_role": beds, "garrison_steps": steps, "by_office": offices,
                                                                                           "list": c.bed_roles},
            "infrastructure": c.infra, "skyway_slots": [{k: s[k] for k in ("from", "to", "level", "width", "status")} | {"cells": len(s["cells"])} for s in c.skyway],
            "spirals": [{k: s.get(k) for k in ("label", "design", "fallback")} for s in c.spirals], "notes": c.notes,
            "R13": {"ok": r13[0], "model_nonair": r13[1], "pieces_nonair": r13[2], "mismatched_rows": r13[3], "markers": [r13[4], len(c.markers)]},
            "verify": rep}


def run_one(skin, size, seed, out_dir, write=True, do_render=True, verbose=False):
    import castle_verify as V
    v = Variety(skin, size, seed)
    c = build(v)
    stem = stem_of(v)
    ok, rep, reach = V.verify(c, verbose=verbose)
    per, r13 = {}, (None, 0, 0, 0, 0)
    if write:
        pieces, per, r13 = write_all(c, stem, out_dir)
        rep["R13_pieces"] = [r13[1], r13[2], r13[3]]
        man = castle_manifest(c, stem, per, r13, rep)
        (Path(out_dir) / stem / "castle.json").write_text(json.dumps(man, indent=1, default=list))
    if do_render:
        render(c, stem, reach)
    return c, ok, rep, reach, per


def main():
    out_dir = Path(arg("out", str(STG)))
    if "--all" in sys.argv:
        results = []
        for skin, size, seed in VARIETIES:
            c, ok, rep, reach, per = run_one(skin, size, seed, out_dir)
            print(f"{stem_of(c.v)}: {'CONSTRUCTED CORRECTLY' if ok else 'NOT YET'} — {rep['summary']}")
            results.append((c, ok, rep, reach))
        sheet(results)
        return
    skin, size, seed = arg("skin", "B"), arg("size", "lord"), arg("seed", 1)
    v = Variety(skin, size, seed)
    print(v.describe())
    c = build(v)
    stem = stem_of(v)
    print(f"model {c.size}: {len(c.markers)} markers, {c.beds} beds, {c.lights} lights; placed {c.poi.get('placed')}; notes {c.notes}")
    reach = None
    if "--verify" in sys.argv:
        import castle_verify as V
        ok, rep, reach = V.verify(c)
        print("CONSTRUCTED CORRECTLY" if ok else "NOT YET")
    if "--render" in sys.argv:
        render(c, stem, reach)
        print("renders ->", RENDERS)
    if "--write" in sys.argv:
        pieces, per, r13 = write_all(c, stem, out_dir)
        print("R13", r13, json.dumps(per)[:600])


if __name__ == "__main__":
    main()
