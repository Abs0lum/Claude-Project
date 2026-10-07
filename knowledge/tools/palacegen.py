#!/usr/bin/env python3
"""palacegen.py — the CITY PALACE ("Seat of Government"), phase D of the CIVITAS city program (D-C570; his 21:07 rulings:
city II, life-size, both jib doors and painting-covered openings). Built from R3 §5.4 (Versailles / Hampton Court / Doge's
Palace / Kerr) as ONE 128 x 128 model in the civgen frame, then cut into the four 64 x 64 pieces the engine can place
(NW NE SW SE as seen from the street side), each a plot with the usual five build stages.

FRAME (civgen): x = depth from the street (x 0 = the gate range on the street side), z = frontage 0..127, feet = height
over the court (feet 0 = standing on the paving; the ground floor course lies at feet -1). Storeys: ground 0..4 (clear 5),
slab 5, étage noble 6..13 (clear 8), slab 14, attic 15..18 (clear 4), roofs from the eave at 19.

MASSING (x ranges):  gate range 0..9 (gatehouse tower z 57..70 rising to 15; public offices either side) · court of honour
10..63 (54 deep, z 26..101) between the wings (z 8..25 west, 102..119 east; 3 storeys, a 2-wide spine corridor down each
wing's centre) · corps de logis 64..81 (112 wide z 8..119: court wall 64, state rooms 65..77 (13 deep), jib-door partition
78, the HIDDEN SPINE CORRIDOR 79..80, rear wall 81) · alley 82..85 · service court 86..127 (kitchen block west, little
commons north, laundry, stables east, smithy; a well; the baize door from the east wing).
THE HIDDEN WORLD: the spine corridor (3 high, slit windows, a bell behind every state room's button), jib doors (a spruce
door in a spruce-panelled wall, no frame) into every state room, three back stairs (3 x 3 spirals), the Tesoretto
strongroom behind a PAINTING (pw:secret_painting: a walk-through block that looks like a framed canvas), the judges'
wardrobe door (barrels), the Duke-of-Athens private stair from the garde-robe to the alley, the prison tower (Pozzi cells at
ground, Piombi under the roof, the bridge of sighs from the judges' room), the baize door (a warped door in green wool).
Outputs: _staging/civ/palace/mvv_palace_<q>_a_r1.mcstructure + manifests (+ renders in _docs/palace/)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import civgen as G  # noqa: E402
import mcstructure as M  # noqa: E402

OUT = Path("/home/claude/_staging/civ/palace")
DOCS = Path("/home/claude/_docs/palace")
TOP = 32                                   # highest feet level in the box (the corps roof peaks at 28, the tower at 29)

# ------------------------------------------------------------------------------------------------ materials (the kit's palette)
STONE, SMOOTH, CHISEL, COBBLE = "minecraft:stone_bricks", "minecraft:smooth_stone", "minecraft:chiseled_stone_bricks", "minecraft:cobblestone"
PANEL, FLOOR, ATTIC_FLOOR, STATE_FLOOR = "minecraft:spruce_planks", "minecraft:oak_planks", "minecraft:spruce_planks", "minecraft:polished_andesite"
POST, GLASS, LIGHT, AIR, VOID = "minecraft:spruce_log", "minecraft:glass_pane", "minecraft:light_block_14", "minecraft:air", "minecraft:structure_void"
GRASS, PATH, GRAVEL, DIRT, WATER = "minecraft:grass_block", "minecraft:grass_path", "minecraft:gravel", "minecraft:dirt", "minecraft:water"
JIB_PANEL, SECRET_PAINTING = "pw:jib_panel", "pw:secret_painting"     # BP-02 1.3.221 blocks (walk-through)
GROUND_CLEAR, NOBLE_CLEAR, ATTIC_CLEAR = 5, 8, 4
F_GROUND, F_SLAB1, F_NOBLE, F_SLAB2, F_ATTIC, F_EAVE = 0, 5, 6, 14, 15, 19

# ------------------------------------------------------------------------------------------------ program 228 switches (10-06)
# VAULTS: the great hall gets a barrel vault of UPSIDE-DOWN pw:roof45 wedges (vertical_half = top: a state every roof45
# already declares, BP-02 227 roof45_*.json permutations [180, +-90 / 0 / 180, 0]) springing at the old ceiling line (feet
# 14) and rising one course per cell to the crown; the attic floor is laid level with the vault's topmost course and the
# corps' hipped roof stands above it, so the stepped back of the vault is never seen. Static only: the top state has never
# been witnessed in-game (P1).
# VAULT_CROWN: what closes an ODD span's centre column. "beam" = a spruce log ridge beam in the top course (existing blocks);
# "ridge" = an inverted ridge piece pw:vault_ridge_<wood> one course higher (DOES NOT EXIST yet: RP/BP block work, see
# _docs/program228/PALACE-NOTES.md); an even span needs no crown piece (the two top wedges meet).
VAULTS = True
VAULT_CROWN = "beam"
VAULT_RIDGE = "pw:vault_ridge_{wood}"         # the future inverted-ridge block (not defined in any pack)
# PASSAGE_ROOF: the covered passage along the alley. "lean" = a one-slope run of pw:roof45_spruce (two courses falling
# east, away from the corps) with a spruce log head plate on the high edge; "slab" = the old flat spruce-slab canopy.
PASSAGE_ROOF = "lean"

# directions in the local frame: +x = "east" (deeper), -x = "west" (toward the street), +z = "south", -z = "north"
VEC = {"east": (1, 0), "west": (-1, 0), "south": (0, 1), "north": (0, -1)}
OPP = {"east": "west", "west": "east", "south": "north", "north": "south"}
BED_DIR = {"south": 0, "west": 1, "north": 2, "east": 3}            # the head lies that way from the foot
STAIR_DIR = {"east": 0, "west": 1, "south": 2, "north": 3}           # spruce_stairs weirdo_direction: the HIGH side


class Palace(G.Building):
    """the 128 x 128 model; z = 0 is an ordinary column here (the palace block is not a street plot)"""

    def __init__(self):
        super().__init__("pw:mvv_palace", 128, 127, top_feet=TOP)
        self.lights = 0
        self.beds = 0
        self.child_bed_clash = []    # his 17:52 children's beds: any that would land on furniture / over air
        self.bed_roles = []          # 1.3.229 ROLE BEDS (his 14:07): every bed's room role (the structures are unchanged)
        self.notes = []

    # ---------------------------------------------------------------- primitives
    def solid(self, x0, x1, z0, z1, f0, f1, mat):
        self.fill(x0, f0, z0, x1, f1, z1, mat)

    def shell(self, x0, x1, z0, z1, f0, f1, mat):
        """the four walls of a box (no floor / ceiling)"""
        self.fill(x0, f0, z0, x0, f1, z1, mat)
        self.fill(x1, f0, z0, x1, f1, z1, mat)
        self.fill(x0, f0, z0, x1, f1, z0, mat)
        self.fill(x0, f0, z1, x1, f1, z1, mat)

    def clear(self, x0, x1, z0, z1, f0, f1):
        self.fill(x0, f0, z0, x1, f1, z1, AIR)

    def slab(self, x0, x1, z0, z1, feet, mat, light_every=6):
        """a floor / ceiling course with light blocks in the AIR just above it every few cells (lit interiors, no spawns).
        v2 (10-05): the lights stood IN the course before — a light block has no collision, so every one was a hole a
        player or villager fell through on the first floors, the attics and the gatehouse's rooms."""
        self.fill(x0, feet, z0, x1, feet, z1, mat)
        for x in range(x0 + 2, x1 - 1, light_every):
            for z in range(z0 + 2, z1 - 1, light_every):
                self.put(x, feet + 1, z, LIGHT)
                self.lights += 1

    def door(self, x, feet, z, facing, mat="minecraft:spruce_door", hinge=0):
        self.put(x, feet, z, mat, **{"minecraft:cardinal_direction": facing, "door_hinge_bit": hinge, "open_bit": 0, "upper_block_bit": 0})
        self.put(x, feet + 1, z, mat, **{"minecraft:cardinal_direction": facing, "door_hinge_bit": hinge, "open_bit": 0, "upper_block_bit": 1})

    def opening(self, x0, x1, z0, z1, f0, f1):
        self.clear(x0, x1, z0, z1, f0, f1)

    def window(self, x, feet, z, dx, dz, w=2, h=3):
        """a window in a wall: panes w wide (along dx, dz) and h high, from feet"""
        for i in range(w):
            for j in range(h):
                self.put(x + dx * i, feet + j, z + dz * i, GLASS)

    def windows_along(self, x, z0, z1, feet, h=3, pitch=4, w=2, axis="z"):
        """windows along a wall that runs along z (axis z, x fixed) or along x (axis x, z fixed)"""
        if axis == "z":
            for z in range(z0 + 1, z1 - w, pitch):
                self.window(x, feet, z, 0, 1, w, h)
        else:
            for xx in range(z0 + 1, z1 - w, pitch):
                self.window(xx, feet, x, 1, 0, w, h)

    def bed(self, x, feet, z, head_dir, kind="minecraft:bed", role="staff"):
        """role: lord (the state bedchamber) | noble (officials' apartments: top families + district representatives) |
        servant (garrets, commons, quarters: the town's best cooks + tradesmen) | guard (guard rooms, the porter) |
        clerk (the clerks' lodgings) | cell (the piombi: never a home)"""
        self.bed_roles.append({"x": x, "feet": feet, "z": z, "role": role})
        dx, dz = VEC[head_dir]
        if role == "child":                    # his 17:52: children's beds go only into EMPTY floor (never over furniture)
            for (cx_, cz_) in ((x, z), (x + dx, z + dz)):
                cur = self.get(cx_, feet, cz_)
                if cur not in (None, AIR) or self.get(cx_, feet - 1, cz_) in (None, AIR):
                    self.child_bed_clash.append({"cell": [cx_, feet, cz_], "was": cur, "below": self.get(cx_, feet - 1, cz_)})
        d = BED_DIR[head_dir]
        self.put(x, feet, z, kind, direction=d, head_piece_bit=False, occupied_bit=False)
        self.put(x + dx, feet, z + dz, kind, direction=d, head_piece_bit=True, occupied_bit=False)
        self.beds += 1
        self.marker("station", "bed", x, feet, z)

    def lectern(self, x, feet, z, facing, station=True):
        self.put(x, feet, z, "minecraft:lectern", **{"minecraft:cardinal_direction": facing, "powered_bit": False})
        if station:
            self.marker("station", "desk", x, feet, z)

    def chest(self, x, feet, z, facing):
        self.put(x, feet, z, "minecraft:chest", **{"minecraft:cardinal_direction": facing})

    def barrel(self, x, feet, z):
        self.put(x, feet, z, "minecraft:barrel", facing_direction=1, open_bit=False)

    def table(self, x, feet, z, wood="dark_oak"):
        self.put(x, feet, z, f"pw:furn_table_{wood}", **{"pw:n": 0, "pw:e": 0, "pw:s": 0, "pw:w": 0})

    def chair(self, x, feet, z, facing, wood="dark_oak"):
        self.put(x, feet, z, f"pw:furn_chair_{wood}", **{"minecraft:cardinal_direction": facing})

    def stairs(self, x, feet, z, high_side, mat="minecraft:spruce_stairs"):
        self.put(x, feet, z, mat, weirdo_direction=STAIR_DIR[high_side], upside_down_bit=False)

    def flight(self, x, z, feet, length, along, mat="minecraft:spruce_stairs", width=1, across=(0, 1)):
        """a straight flight rising 1 per step toward `along` ('east' = deeper x ...), `width` cells wide (across = unit vector)"""
        dx, dz = VEC[along]
        for i in range(length):
            for w in range(width):
                self.stairs(x + dx * i + across[0] * w, feet + i, z + dz * i + across[1] * w, along, mat)
                # a solid riser under each step so the flight reads as a staircase from below
                for f in range(feet, feet + i):
                    self.put(x + dx * i + across[0] * w, f, z + dz * i + across[1] * w, PANEL)

    def spiral(self, x0, z0, f0, f1, mat=PANEL, post=POST, ceiling=None):
        """a 3 x 3 spiral stair (x0, z0 = the NW cell of the 3 x 3), rising one block per cell around a central post, from
        feet f0 (first step at f0) to f1; every step is a full block (villagers climb 1-block steps); the open cells above each
        step stay air (the well is cleared first by the caller).
        ceiling (program 228, STRUCTURE-AUDIT F2): the first feet level the stair must never touch (the eave / the course
        above the top floor). Steps, headroom and the newel post all stop below it, and no cell already holding a pw:roof*
        piece is ever overwritten. Before: a flight to feet 18 cleared feet 19..21 (and ran the post to 20) out of a roof
        laid earlier — the 9 ROOF-GAP holes.
        Split (228) into the GEOMETRY (spiral_plan, pure) and the ONE place the stair is laid (self.spiral_lay): the future
        custom spiral-stair block replaces spiral_lay only (FURNITURE-AND-STAIRS / his 12:47 brief)."""
        self.spiral_lay(spiral_plan(x0, z0, f0, f1, ceiling), mat, post)

    def spiral2(self, x0, z0, f0, floors, design, pal, ceiling=None, door_ok=None, label="", want=None):
        """program 228 (his 14:21 / 14:44 / 15:06 / 16:30 / 18:0x 'rework rooms now'): a spiral of our custom blocks
        (tools/spiral_site.py) — x0, z0 = the NW cell of the 2n x 2n well; floors = the walking levels it serves (the last
        = the top: floor in front; the others: a doorway beside the step). The hand and facing are SOLVED so every exit
        lands on walkable floor (door_ok narrows where a door may open); want = (hand, k0) forces one. Raises when no
        plan exits cleanly — the site must be reworked, never a stair into a wall."""
        import spiral_site as SS
        cands = SS.solve(self, x0, z0, f0, floors, design, door_ok)
        if want: cands = [c for c in cands if (c[2], c[3]) == tuple(want)]
        ok = [c for c in cands if c[0]]
        if not ok:
            raise SystemExit(f"spiral2 {label}: no clean exits at ({x0},{z0}) {design}: " + " | ".join(f"{c[2]}/{c[3]}: {c[4][:2]}" for c in cands[:4]))
        _, _, hand, k0, _, P = ok[0]
        rep = SS.lay(self, P, pal, ATTIC_FLOOR, ceiling=ceiling)
        self.spirals = getattr(self, "spirals", [])
        self.spirals.append({"label": label, "design": design, "pal": pal, "hand": hand, "k0": k0, "well": P["well"], "f0": f0,
                             "floors": floors, "doors": P["doors"], "landing": P["landing"], "cut": rep["overwritten"]})
        return P

    def spiral_lay(self, plan, mat=PANEL, post=POST):
        """THE STAIR HOOK: lays one spiral_plan. Today: the newel post column (`post`), one full block (`mat`) per step and
        3 cells of headroom (air) over each step, in the plan's order. A custom spiral-stair block replaces this body: each
        step carries its ring index (0..7 clockwise from the NW cell), the travel direction to the next step and the
        rise. Rules every replacement keeps: nothing at or above plan['ceiling'], and no cell holding a pw:roof* piece is
        ever written (put_safe)."""
        ceiling = plan["ceiling"]

        def put_safe(x, f, z, name):
            if ceiling is not None and f >= ceiling:
                return
            cur = self.get(x, f, z)
            if cur and cur.startswith("pw:roof"):
                return
            self.put(x, f, z, name)

        for (x, f, z) in plan["post"]:
            put_safe(x, f, z, post)
        for st in plan["steps"]:
            x, f, z = st["cell"]
            put_safe(x, f, z, mat)
            for (hx, hf, hz) in st["headroom"]:
                put_safe(hx, hf, hz, AIR)

    def column(self, x, z, f0, f1, mat=POST):
        self.fill(x, f0, z, x, f1, z, mat)

    def roof_hip(self, x0, x1, z0, z1, eave, wood="spruce"):
        """a hipped roof over the rectangle (walls x0..x1, z0..z1 inclusive): 45-degree wedges rising one row per cell inward
        from the eave course; hip blocks on the diagonals; a ridge of facing wedges (or a ridge block) at the top"""
        r45, hip, ridge = f"pw:roof45_{wood}", f"pw:roof_hip_{wood}", f"pw:roof45_ridge_{wood}"
        depth, width = x1 - x0 + 1, z1 - z0 + 1
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                dw, de, dn, ds = x - x0, x1 - x, z - z0, z1 - z            # distances to the west (street-side), east, north, south edges
                k = min(dw, de, dn, ds)
                f = eave + k
                # which edge is nearest decides the slope's facing (down-slope direction)
                if k == dw and k == dn and dw == dn and depth != width:
                    self.put(x, f, z, hip, **{"minecraft:cardinal_direction": "north", "minecraft:vertical_half": "bottom"}); continue
                nearest = sorted([(dw, "west"), (de, "east"), (dn, "north"), (ds, "south")])
                (k0, s0), (k1, s1) = nearest[0], nearest[1]
                if k0 == k1 and {s0, s1} not in ({"west", "east"}, {"north", "south"}):
                    # a hip cell: the corner diagonal — faces the outer corner direction (the long axis' slope wins visually)
                    facing = s0 if s0 in ("west", "east") else s1
                    self.put(x, f, z, hip, **{"minecraft:cardinal_direction": facing, "minecraft:vertical_half": "bottom"})
                elif k0 == k1:
                    # the ridge line (two opposite edges equidistant): a ridge block
                    self.put(x, f, z, ridge, **{"minecraft:cardinal_direction": "north" if s0 in ("west", "east") else "west"})
                else:
                    self.put(x, f, z, r45, **{"minecraft:cardinal_direction": s0, "minecraft:vertical_half": "bottom"})
        # under the roof: fill the attic void above the eave between the slopes with air (already air) — nothing to do

    def roof_pyramid(self, x0, x1, z0, z1, eave, wood="spruce"):
        """a square tower roof: a pyramid with a pyramidion at the apex"""
        self.roof_hip(x0, x1, z0, z1, eave, wood)
        cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
        k = min(cx - x0, cz - z0)
        if (x1 - x0) % 2 == 0 and (z1 - z0) % 2 == 0:
            self.put(cx, eave + k, cz, f"pw:roof_pyramidion_{wood}", **{"minecraft:cardinal_direction": "north", "minecraft:vertical_half": "bottom"})

    def panel_room(self, x0, x1, z0, z1, f0, f1):
        """spruce panelling on the inside faces of a room's walls (the étage noble look)"""
        self.fill(x0, f0, z0, x0, f1, z1, PANEL)
        self.fill(x1, f0, z0, x1, f1, z1, PANEL)
        self.fill(x0, f0, z0, x1, f1, z0, PANEL)
        self.fill(x0, f0, z1, x1, f1, z1, PANEL)

    def carpet(self, x0, x1, z0, z1, feet, colour="red"):
        self.fill(x0, feet, z0, x1, feet, z1, f"minecraft:{colour}_carpet")

    def secret_painting(self, x, feet, z, facing):
        """a 2 x 2 framed canvas (pw:secret_painting, walk-through) covering a 2-wide, 2-high opening in a wall that runs
        along x (facing north / south) or along z (facing east / west); (x, z) = the canvas' left column seen from the
        canvas side, feet = its lower row. Tiles: 0 upper-left, 1 upper-right, 2 lower-left, 3 lower-right (as seen)."""
        if facing in ("north", "south"):
            right = (x - 1, z) if facing == "north" else (x + 1, z)       # looking south from the north side, +x is on the LEFT
        else:
            right = (x, z + 1) if facing == "east" else (x, z - 1)        # looking west from the east side, +z is on the left
        left = (x, z)
        for (cx, cz), col in ((left, 0), (right, 1)):
            self.put(cx, feet + 1, cz, SECRET_PAINTING, **{"minecraft:cardinal_direction": facing, "pw:tile": col})
            self.put(cx, feet, cz, SECRET_PAINTING, **{"minecraft:cardinal_direction": facing, "pw:tile": col + 2})

    def jib_panel(self, x, feet, z):
        """a 1 x 2 opening closed by the walk-through panel block (looks like the spruce panelling)"""
        self.put(x, feet, z, JIB_PANEL)
        self.put(x, feet + 1, z, JIB_PANEL)

    def bell(self, x, feet, z, facing):
        self.put(x, feet, z, "minecraft:bell", attachment="standing", direction={"south": 0, "west": 1, "north": 2, "east": 3}[facing], toggle_bit=False)

    def button(self, x, feet, z, facing):
        self.put(x, feet, z, "minecraft:stone_button", facing_direction={"west": 4, "east": 5, "north": 2, "south": 3}[facing], button_pressed_bit=False)

    def lantern(self, x, feet, z, hanging=False):
        self.put(x, feet, z, "minecraft:lantern", hanging=hanging)

    def fence_line(self, x0, x1, z0, z1, feet, mat="minecraft:spruce_fence"):
        self.fill(x0, feet, z0, x1, feet, z1, mat)


# ================================================================================================= spiral stair geometry (228)
SPIRAL_RING = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1)]     # (dx, dz) from the NW cell, clockwise from above
_RING_DIR = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}


def spiral_plan(x0, z0, f0, f1, ceiling=None, headroom=3):
    """the geometry of a 3 x 3 spiral stair (pure: no blocks). x0, z0 = the NW cell; steps at feet f0..f1, one per ring cell,
    climbing clockwise (seen from above) around the newel at (x0 + 1, z0 + 1). The post runs from f0 - 1 to f1 + 2, cut
    below `ceiling` (the first feet level the stair must never touch: the eave / the course over the top floor).
    Returns {x0, z0, f0, f1, ceiling, post: [(x, f, z)], steps: [{cell, ring, travel, headroom: [(x, f, z)]}]}; `travel`
    = the direction from this step to the next ring cell (the way a climber faces), for a custom stair block's facing."""
    if ceiling is not None:
        assert f1 < ceiling, f"spiral at ({x0},{z0}): last step {f1} at/above the ceiling {ceiling}"
    top = (f1 + 2) if ceiling is None else min(f1 + 2, ceiling - 1)
    post = [(x0 + 1, f, z0 + 1) for f in range(f0 - 1, top + 1)]
    steps = []
    for i, f in enumerate(range(f0, f1 + 1)):
        dx, dz = SPIRAL_RING[i % 8]
        nx, nz = SPIRAL_RING[(i + 1) % 8]
        steps.append({"cell": (x0 + dx, f, z0 + dz), "ring": i % 8, "travel": _RING_DIR[(nx - dx, nz - dz)],
                      "headroom": [(x0 + dx, f + h, z0 + dz) for h in range(1, headroom + 1)]})
    return {"x0": x0, "z0": z0, "f0": f0, "f1": f1, "ceiling": ceiling, "post": post, "steps": steps}


# ================================================================================================= reusable roof-kit helpers (228)
# Module-level so castlegen / civgen can import them: they only need a civgen.Building (put / fill / get in FEET).
# Facing law (D-C487 measured transformation, checked on the shipped RP-04 158 geometry with civ_render.pw_faces):
#   roof45 vertical_half = bottom: the deck is LOW on the cardinal_direction side (the downhill side);
#   roof45 vertical_half = top:    the deck (now the underside) is HIGH on the cardinal_direction side.
# So a roof cell faces AWAY from its ridge and a vault cell faces TOWARD its crown.
_AXIS_DIRS = {"z": ("east", "west"), "x": ("south", "north")}       # (facing of the low-coordinate half, of the high half)
_RIDGE_FACING = {"z": "west", "x": "north"}                          # roof45_ridge: a ridge line along z = "west" (civ_roster, witnessed)


def _is_roof(b, x, f, z):
    n = b.get(x, f, z)
    return bool(n) and n.startswith("pw:roof")


def vault(b, x0, x1, z0, z1, spring, axis="z", wood="spruce", crown="beam", fill=ATTIC_FLOOR, deck=ATTIC_FLOOR,
          end_mat=STONE, deck_lights=6):
    """A BARREL VAULT of upside-down pw:roof45_<wood> wedges over the room x0..x1 / z0..z1 (inclusive, the room's inside),
    springing at feet `spring` against the two long walls and rising one course per cell to the crown.
      axis "z": the vault runs along z (its crown line is parallel to z; the rings step across x); axis "x": the reverse.
      ring k (k = cells from the nearer long wall) = one wedge at feet spring + k, vertical_half top, facing the crown;
      crown (odd span only): "beam" = a <wood>_log ridge beam in the top course (spring + K - 1, K = span // 2);
                             "ridge" = air there and the inverted ridge piece VAULT_RIDGE one course up (spring + K);
      an even span closes on its own (the two top wedges meet at the crown line).
    Above the vault: every cell between a wedge's flat back and the DECK course is `fill`; the deck course is the top
    course of the vault (the attic floor is levelled with the vault's topmost block: walking surface = deck + 1), lit every
    `deck_lights` cells like Palace.slab. The two short ends are closed by `end_mat` walls (z0-1 / z1+1 for axis z) from
    the springing up to the deck where the cell is air. The caller lays the REAL ROOF above the deck (eave >= deck + 1),
    so the stepped back is never visible. Never overwrites a pw:roof* cell. Returns the deck feet."""
    lo, hi = (x0, x1) if axis == "z" else (z0, z1)          # the span (across the crown line)
    a0, a1 = (z0, z1) if axis == "z" else (x0, x1)          # the run (along the crown line)
    span = hi - lo + 1
    K = span // 2
    odd = span % 2 == 1
    top = spring + K - 1                                    # the top wedge course
    deck_f = top + (1 if (odd and crown == "ridge") else 0)
    d_lo, d_hi = _AXIS_DIRS[axis]
    r45, ridge = f"pw:roof45_{wood}", VAULT_RIDGE.format(wood=wood)

    def cell(s, a):                                         # (span coord, run coord) -> (x, z)
        return (s, a) if axis == "z" else (a, s)

    def put(s, f, a, name, **st):
        x, z = cell(s, a)
        if not _is_roof(b, x, f, z):                       # an outer-roof cell inside the box is never touched
            b.put(x, f, z, name, **st)
    for a in range(a0, a1 + 1):
        for s in range(lo, hi + 1):
            for f in range(spring, deck_f + 1):
                put(s, f, a, AIR)
            k = min(s - lo, hi - s)
            if odd and k == K:                              # the crown column
                if crown == "ridge":
                    put(s, deck_f, a, ridge, **{"minecraft:cardinal_direction": _RIDGE_FACING[axis]})
                else:
                    put(s, top, a, f"minecraft:{wood}_log", pillar_axis=axis)
                continue
            f = spring + k
            put(s, f, a, r45, **{"minecraft:cardinal_direction": d_lo if s - lo < hi - s else d_hi,     # toward the crown
                                 "minecraft:vertical_half": "top"})
            for ff in range(f + 1, deck_f):
                put(s, ff, a, fill)
            if f < deck_f:
                put(s, deck_f, a, deck)
    # deck lights (the loft under the real roof is dark and enclosed)
    if deck_lights:
        for s in range(lo + 2, hi - 1, deck_lights):
            for a in range(a0 + 2, a1 - 1, deck_lights):
                x, z = cell(s, a)
                if b.get(x, deck_f + 1, z) in (None, AIR):
                    b.put(x, deck_f + 1, z, LIGHT)
    # the end walls (gable-shaped section of the vault, closed flat)
    for a in (a0 - 1, a1 + 1):
        for s in range(lo, hi + 1):
            for f in range(spring, deck_f + 1):
                x, z = cell(s, a)
                if b.get(x, f, z) in (None, AIR, LIGHT):
                    b.put(x, f, z, end_mat)
    return deck_f


def roof_lean(b, x0, x1, z0, z1, eave, downhill="east", wood="spruce", head=None):
    """A ONE-SLOPE (lean-to / mono-pitch) roof of pw:roof45_<wood> over x0..x1 / z0..z1: one course per cell rising away
    from the `downhill` side (the eave course at feet `eave` on that side), every wedge facing `downhill`. The high edge is
    closed by a `head` plate (default <wood>_log laid along the edge) one cell beyond the top course, level with it, so the
    top course's uphill side is solid. The run's two open ends close with the wedge's own gable fill (the kit has no
    mono-pitch verge / head piece). Returns the feet of the top course."""
    head = head or f"minecraft:{wood}_log"
    r45 = f"pw:roof45_{wood}"
    dx, dz = VEC[downhill]
    across = range(x0, x1 + 1) if dx else range(z0, z1 + 1)
    along = range(z0, z1 + 1) if dx else range(x0, x1 + 1)
    order = sorted(across, key=lambda c: c * (dx or dz), reverse=True)     # the downhill (eave) cell first
    for i, c in enumerate(order):
        for a in along:
            x, z = (c, a) if dx else (a, c)
            b.put(x, eave + i, z, r45, **{"minecraft:cardinal_direction": downhill, "minecraft:vertical_half": "bottom"})
    hc = order[-1] - (dx or dz)                                            # one beyond the top course, uphill
    for a in along:
        x, z = (hc, a) if dx else (a, hc)
        b.put(x, eave + len(order) - 1, z, head, pillar_axis="z" if dx else "x")
    return eave + len(order) - 1


# ================================================================================================= the layout
# the gate range / wings / corps / service court as x ranges (depth from the street)
GATE = (0, 9)
COURT = (10, 63)
CORPS = (64, 81)
ALLEY = (82, 85)
SERVICE = (86, 127)
Z0, Z1 = 8, 119                        # the main block's frontage (112 wide); the service court spans 0..127
WW = (8, 25)                           # west wing z range
EW = (102, 119)                        # east wing z range
CENTER = 63                            # the axis of symmetry lies between z 63 and 64
HALL_BAY = (43, 84)                    # the great hall's z range incl. its two end walls (inside: z 44..83, x 65..77)


def ground_and_foundations(p):
    """everything below feet 0: dirt, foundations under every building range, the paving of the courts"""
    p.fill(0, -15, 0, 127, -3, 127, DIRT)
    p.fill(0, -2, 0, 127, -2, 127, DIRT)
    p.fill(0, -1, 0, 127, -1, 127, GRASS)                          # the block's own ground: lawn
    # the court of honour: gravel field, stone-brick paths in a cross, lawn quadrants
    p.fill(COURT[0], -1, 26, COURT[1], -1, 101, GRAVEL)
    p.fill(COURT[0], -1, 60, COURT[1], -1, 67, STONE)              # the central avenue, gate -> corps door (8 wide)
    p.fill(34, -1, 26, 39, -1, 101, STONE)                        # the cross path between the wings
    for (xa, xb, za, zb) in ((12, 32, 28, 58), (12, 32, 69, 99), (41, 61, 28, 58), (41, 61, 69, 99)):
        p.fill(xa, -1, za, xb, -1, zb, GRASS)                     # four lawns
        p.fill(xa + 1, -1, za + 1, xb - 1, -1, zb - 1, GRASS)
    # a basin at the crossing (the court's fountain-to-be): a 6 x 6 stone ring with water
    p.fill(34, -1, 61, 39, -1, 66, STONE)
    p.fill(35, -1, 62, 38, -1, 65, WATER)
    p.fill(34, 0, 61, 39, 0, 66, "minecraft:stone_brick_slab", **{"minecraft:vertical_half": "bottom"})
    p.fill(35, 0, 62, 38, 0, 65, AIR)
    p.fill(35, -1, 62, 38, -1, 65, WATER)
    # the alley and the service court: cobbles / gravel
    p.fill(ALLEY[0], -1, 0, ALLEY[1], -1, 127, COBBLE)
    p.fill(SERVICE[0], -1, 0, SERVICE[1], -1, 127, GRAVEL)
    # foundations (feet -2 .. -1 stone) under every building footprint are laid by the buildings themselves


def gate_stair(p, x0, x1):
    """228 (his 16:30 'C in the main towers' + 18:0x 'rework rooms now'): the gatehouse's ground floor is two 3-deep guard
    rooms either side of the carriage passage — no room for a 6 x 6 well — so an A TURRET (stone) rises in the south guard
    room's west corner (x 1..2, z 67..68) to the porter's lodge (6), and the C GRAND spiral (stone) stands in the tower body
    (x 3..8, z 59..64) from the lodge to the top room (door beside the step at 11, the floor in front at 16).
    Laid after everything (see build)."""
    p.spiral2(x0 + 1, 67, 0, [6], "A_turret", "stone", ceiling=10, label="gatehouse turret")
    p.spiral2(x0 + 3, 59, 6, [11, 16], "C_grand", "stone", ceiling=19, label="gatehouse tower", want=("ccw", 2))


def gate_range(p):
    """x 0..9: the south range on the street — public offices either side, the gatehouse tower in the centre"""
    x0, x1 = GATE
    # offices: two storeys (ground clear 5 + first clear 4), stone, windows to the street
    for (za, zb) in ((Z0, 56), (71, Z1)):
        p.fill(x0, -2, za, x1, -1, zb, STONE)                     # footing
        p.fill(x0 + 1, -1, za + 1, x1 - 1, -1, zb - 1, SMOOTH)    # ground floor
        p.shell(x0, x1, za, zb, 0, 9, STONE)
        p.clear(x0 + 1, x1 - 1, za + 1, zb - 1, 0, 4)
        p.slab(x0, x1, za, zb, 5, FLOOR)                           # first floor
        p.shell(x0, x1, za, zb, 5, 5, STONE)
        p.clear(x0 + 1, x1 - 1, za + 1, zb - 1, 6, 9)
        p.slab(x0, x1, za, zb, 10, STONE, light_every=8)           # the eave course / attic floor (a flat lead roof)
        p.fill(x0, 10, za, x1, 10, zb, CHISEL)
        p.fill(x0, 11, za, x1, 11, zb, "minecraft:stone_brick_slab", **{"minecraft:vertical_half": "bottom"})   # parapet
        # street windows (ground 1..3, first 6..8) and court windows
        p.windows_along(x0, za, zb, 1, h=3, pitch=4)
        p.windows_along(x0, za, zb, 6, h=3, pitch=4)
        p.windows_along(x1, za, zb, 1, h=3, pitch=6)
        p.windows_along(x1, za, zb, 6, h=3, pitch=6)
        # counters along the street side: the public offices (toll, notary, court clerk) — partitions every 10
        for zc in range(za + 10, zb - 4, 10):
            p.fill(x0 + 1, 0, zc, x1 - 1, 4, zc, STONE)
            p.door(x0 + 1 + 4, 0, zc, "south")                    # a door between the offices
        for zc in range(za + 4, zb - 4, 10):
            p.lectern(x0 + 2, 0, zc, "west")                      # the clerk faces the street window
            p.table(x0 + 3, 0, zc + 1); p.chair(x0 + 4, 0, zc + 1, "west")
            p.chest(x0 + 7, 0, zc, "west"); p.barrel(x0 + 7, 0, zc + 1)
        p.zone("shopfloor", x0 + 1, 0, za + 1, x1 - 1, zb - 1)
        # the court-side doors of the offices (into the court of honour)
        p.door(x1, 0, za + 6, "east"); p.door(x1, 0, zb - 6, "east")
        # first floor: lodgings for the clerks (two-room lodgings along a corridor on the court side)
        p.fill(x0 + 1, 6, za + 1, x0 + 5, 9, zb - 1, AIR)
        p.fill(x0 + 5, 6, za + 1, x0 + 5, 9, zb - 1, PANEL)      # the corridor wall (corridor x 6..8)
        for zc in range(za + 1, zb - 6, 6):
            p.fill(x0 + 1, 6, zc + 5, x0 + 4, 9, zc + 5, PANEL)   # lodging partitions every 6
            p.door(x0 + 5, 6, zc + 2, "east")
            p.bed(x0 + 2, 6, zc + 1, "south", role="clerk"); p.chest(x0 + 1, 6, zc + 3, "east")
        p.zone("quarters", x0 + 1, 6, za + 1, x0 + 4, zb - 1)
        # a stair up at the inner end (toward the gatehouse), 2 wide against the court wall
        zs = zb - 3 if za == Z0 else za + 2
        p.flight(x1 - 1, zs, 0, 5, "west", width=2, across=(0, 1) if za == Z0 else (0, -1))
    # the GATEHOUSE: z 57..70, a tower rising to 15 with the carriage arch (z 62..65, 5 high) through it
    gz0, gz1 = 57, 70
    p.fill(x0, -2, gz0, x1, -1, gz1, STONE)
    p.fill(x0, -1, 62, x1, -1, 65, STONE)                          # the passage paving
    p.shell(x0, x1, gz0, gz1, 0, 19, STONE)
    p.fill(x0, 0, gz0, x1, 19, gz0, STONE); p.fill(x0, 0, gz1, x1, 19, gz1, STONE)
    p.clear(x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 0, 18)
    p.fill(x0 + 1, 5, gz0 + 1, x1 - 1, 5, gz1 - 1, STONE)          # the vault over the passage / first floor
    p.fill(x0 + 1, 10, gz0 + 1, x1 - 1, 10, gz1 - 1, FLOOR)        # second floor of the tower
    p.put(x0 + 4, 6, 59, LIGHT); p.put(x0 + 4, 6, 68, LIGHT); p.put(x0 + 4, 11, 63, LIGHT); p.put(x0 + 4, 11, 64, LIGHT)
    # the carriage arch: open front and back, 4 wide (62..65), 5 high; passage walls either side
    p.fill(x0, 0, 62, x1, 4, 65, AIR)
    p.fill(x0 + 1, 0, 61, x1 - 1, 4, 61, STONE); p.fill(x0 + 1, 0, 66, x1 - 1, 4, 66, STONE)
    p.fill(x0, 0, 62, x0, 4, 65, AIR); p.fill(x1, 0, 62, x1, 4, 65, AIR)
    p.fill(x0, 5, 62, x0, 5, 65, CHISEL)                            # the arch's keystone course
    # the portcullis: iron bars hanging in the vault at x 2 (lowered 2 blocks — theatre)
    p.fill(x0 + 2, 3, 62, x0 + 2, 4, 65, "minecraft:iron_bars")
    # guard rooms either side of the passage (z 58..60 west: 3 wide, 8 deep; east z 67..69), 4 beds each (bunks on two levels)
    for (za, zb, side) in ((gz0 + 1, 60, "north"), (67, gz1 - 1, "south")):
        p.clear(x0 + 1, x1 - 1, za, zb, 0, 4)
        p.bed(x0 + 1, 0, za if side == "north" else zb, "east" if False else "east") if False else None
        for i in range(2):
            p.bed(x0 + 1 + i * 4, 0, za + (0 if side == "north" else 2), "east", role="guard")
        p.chest(x0 + 7, 0, za + 1, "west")
        p.door(x0 + 1 if side == "north" else x0 + 1, 0, 61 if side == "north" else 66, "south" if side == "north" else "north")
        p.zone("quarters", x0 + 1, 0, za, x1 - 1, zb)
    # the porter's lodge: the room over the passage's east bay (first floor), with the stair down into the passage wall
    p.clear(x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 6, 9)
    p.windows_along(x0, gz0, gz1, 6, h=3, pitch=4)
    p.windows_along(x1, gz0, gz1, 6, h=3, pitch=4)
    p.lectern(x0 + 2, 6, 63, "west")                               # the porter's desk
    p.marker("station", "door", x0 + 4, 0, 60)                     # the porter's post at the arch
    p.marker("station", "post", x0 + 4, 0, 67); p.marker("station", "post", x0 + 4, 0, 60)
    p.bed(x0 + 6, 6, 58, "east", role="guard"); p.bed(x0 + 6, 6, 68, "east", role="guard")
    p.fill(x0 + 1, 15, gz0 + 1, x1 - 1, 15, gz1 - 1, FLOOR)        # the top room's floor (a watch room under the roof)
    p.put(x0 + 4, 16, 63, LIGHT)
    p.clear(x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 11, 14)
    p.clear(x0 + 1, x1 - 1, gz0 + 1, gz1 - 1, 16, 18)
    # the tower stair (west side, rises to the top room). 228: laid AFTER the floor at 15 and the clears at 11..14 / 16..18,
    # which erased its steps 11..18 before (the stair ended at the second floor); the last step is the top room's floor
    # course (15: step off at 16); nothing at or above the chisel course 19
    p.later = getattr(p, "later", [])
    p.later.append(lambda: gate_stair(p, x0, x1))
    p.windows_along(x0, gz0, gz1, 11, h=2, pitch=3)
    p.windows_along(x1, gz0, gz1, 11, h=2, pitch=3)
    p.windows_along(x0, gz0, gz1, 16, h=2, pitch=3)
    p.windows_along(x1, gz0, gz1, 16, h=2, pitch=3)
    p.fill(x0, 19, gz0, x1, 19, gz1, CHISEL)
    p.roof_pyramid(x0, x1, gz0 - 1, gz1 + 1, 20)
    # the two CELLS beneath the gatehouse (feet -5 .. -2), reached by a ladder from the west guard room
    p.fill(x0 + 1, -6, 58, x1 - 1, -6, 61, STONE)
    p.fill(x0 + 1, -5, 58, x1 - 1, -2, 61, STONE)
    p.clear(x0 + 2, x0 + 4, 59, 60, -5, -3); p.clear(x0 + 6, x0 + 8, 59, 60, -5, -3)
    p.fill(x0 + 5, -5, 59, x0 + 5, -3, 60, "minecraft:iron_bars")
    p.fill(x0 + 1, -5, 59, x0 + 1, 0, 59, "minecraft:ladder", facing_direction=5)
    p.put(x0 + 1, -1, 59, "minecraft:ladder", facing_direction=5)
    p.put(x0 + 1, 0, 59, "minecraft:spruce_trapdoor", direction=0, open_bit=False, upside_down_bit=False)
    p.zone("cellar", x0 + 2, -5, 59, x0 + 8, 60)
    p.notes.append("gate range: offices x2 (lecterns 3 each), gatehouse tower 15 high, arch 4 x 5, portcullis, 2 guard rooms (4 bunks), porter's lodge, tower stair, 2 cells below")


def wing(p, zw0, zw1, west):
    """a wing x 10..63 (54 long), z zw0..zw1 (18 wide): 3 storeys; the spine corridor along the wing's centre (2 wide) with
    rooms either side (7 deep); the west wing holds the guard room (ground), treasury + chancery + judges (first), the archive
    (attic) and the PRISON TOWER at its street end; the east wing the household offices (ground), officials' apartments (first
    + attic) and the chapel at the corps end"""
    x0, x1 = COURT
    p.fill(x0, -2, zw0, x1, -1, zw1, STONE)
    p.fill(x0 + 1, -1, zw0 + 1, x1 - 1, -1, zw1 - 1, SMOOTH if west else STATE_FLOOR)
    p.shell(x0, x1, zw0, zw1, 0, 18, STONE)
    p.clear(x0 + 1, x1 - 1, zw0 + 1, zw1 - 1, 0, 18)
    p.slab(x0, x1, zw0, zw1, F_SLAB1, FLOOR); p.shell(x0, x1, zw0, zw1, F_SLAB1, F_SLAB1, STONE)
    p.slab(x0, x1, zw0, zw1, F_SLAB2, ATTIC_FLOOR); p.shell(x0, x1, zw0, zw1, F_SLAB2, F_SLAB2, STONE)
    p.fill(x0, F_SLAB2, zw0, x1, F_SLAB2, zw1, CHISEL)                # a string course
    p.roof_hip(x0, x1, zw0, zw1, F_EAVE)
    # the spine corridor on every floor: z zc0..zc1 = the two centre columns; room partitions either side
    zc0, zc1 = zw0 + 8, zw0 + 9
    inner_z = (zw0 + 1, zw0 + 7)            # the court-side rooms (toward the court for the east wing: zw0 side is the court side only for the EAST wing)
    outer_z = (zw0 + 10, zw1 - 1)
    for f0, f1, floor_mat in ((F_GROUND, F_GROUND + GROUND_CLEAR - 1, SMOOTH), (F_NOBLE, F_NOBLE + NOBLE_CLEAR - 1, FLOOR), (F_ATTIC, F_ATTIC + ATTIC_CLEAR - 1, ATTIC_FLOOR)):
        p.fill(x0 + 1, f0, zc0 - 1, x1 - 1, f1, zc0 - 1, PANEL if f0 == F_NOBLE else STONE)   # corridor walls
        p.fill(x0 + 1, f0, zc1 + 1, x1 - 1, f1, zc1 + 1, PANEL if f0 == F_NOBLE else STONE)
        p.clear(x0 + 1, x1 - 1, zc0, zc1, f0, f1)
        for xx in range(x0 + 4, x1 - 2, 8):
            p.lantern(xx, f0 + 3 if f0 != F_NOBLE else f0 + 5, zc0, hanging=True)
    # windows: the long outer walls every 4 on the ground (1..2) and étage noble (7..10, tall), the attic small (16..17)
    for (zz, pitch) in ((zw0, 4), (zw1, 4)):
        p.windows_along(zz, x0, x1, 1, h=2, pitch=pitch, axis="x")
        p.windows_along(zz, x0, x1, 7, h=4, pitch=pitch, axis="x")
        p.windows_along(zz, x0, x1, 16, h=2, pitch=pitch, axis="x")
    # the back stair of the wing: a 3 x 3 spiral at the corps end, in the corridor's far bay (serves all floors)
    sx = x1 - 4                                                    # 228: the well + stair are laid LAST (end of wing())
    # the wing's grand end door into the court (street end) and its door into the corps (corps end, corridor level)
    p.opening(x0, x0, zc0, zc1, 0, 3)                              # the open arch at the street end of the corridor (gate side)
    p.opening(x1, x1, zc0, zc1, 0, 2); p.opening(x1, x1, zc0, zc1, F_NOBLE, F_NOBLE + 2)   # into the corps (both floors)
    # rooms: partitions every `pitch` along x, on both sides of the corridor; doors from the corridor
    if west:
        # GROUND: guard room & armoury (x 22..41, court side), the prison tower at the street end (x 10..21, whole width)
        p.fill(x0 + 1, 0, zw0 + 1, x0 + 11, 4, zw1 - 1, STONE)       # the tower's solid base block (rooms carved below)
        tower(p, x0, x0 + 11, zw0, zw1)
        # guard room: x 22..41, z inner (court side = zw1 side for the west wing: the court lies at z > zw1)
        p.fill(x0 + 12, 0, zw0 + 1, x0 + 12, 4, zw1 - 1, STONE)      # wall against the tower
        p.fill(x0 + 32, 0, outer_z[0], x0 + 32, 4, outer_z[1], STONE)
        p.door(zc1 + 1 and x0 + 20, 0, zc1 + 1, "south")            # corridor -> guard room
        for i in range(6):
            p.bed(x0 + 14 + i * 3, 0, zw1 - 2, "north", role="guard")
        p.put(x0 + 30, 0, zw1 - 2, "minecraft:grindstone", attachment="standing", direction=0)
        p.put(x0 + 30, 0, zw1 - 3, "minecraft:blast_furnace", **{"minecraft:cardinal_direction": "north"})
        p.marker("station", "anvil", x0 + 30, 0, zw1 - 4)
        p.put(x0 + 30, 0, zw1 - 4, "minecraft:anvil", **{"minecraft:cardinal_direction": "north", "damage": "undamaged"})
        p.chest(x0 + 14, 0, zw1 - 4, "south"); p.chest(x0 + 15, 0, zw1 - 4, "south")
        p.zone("quarters", x0 + 13, 0, outer_z[0], x0 + 31, outer_z[1])
        # ground, other side (z inner = zw0 side, the outside of the palace): stores + the smiths' lodging
        for xx in range(x0 + 12, x1 - 6, 10):
            p.fill(xx, 0, inner_z[0], xx, 4, inner_z[1], STONE)
            p.door(xx + 5, 0, zc0 - 1, "north")
            p.barrel(xx + 2, 0, inner_z[0] + 1); p.barrel(xx + 3, 0, inner_z[0] + 1); p.chest(xx + 7, 0, inner_z[0] + 1, "south")
        p.zone("storeroom", x0 + 13, 0, inner_z[0], x1 - 5, inner_z[1])
        # ÉTAGE NOBLE: treasury (x 42..55 corps end, court side), chancery hall (x 12..41 court side, 30 long), judges' room (outer side x 42..51)
        p.panel_room(x0 + 1, x1 - 1, zw0 + 1, zw1 - 1, F_NOBLE, F_NOBLE + 7)
        p.fill(x0 + 1, F_NOBLE - 1, zw0 + 1, x1 - 1, F_NOBLE - 1, zw1 - 1, STATE_FLOOR)
        p.fill(x0 + 32, F_NOBLE, outer_z[0], x0 + 32, F_NOBLE + 7, outer_z[1], PANEL)     # chancery | treasury
        p.door(x0 + 20, F_NOBLE, zc1 + 1, "south"); p.door(x0 + 40, F_NOBLE, zc1 + 1, "south")
        # chancery: 8 lecterns in two rows, a seal table, the pigeon-hole wall (bookshelves)
        for i in range(4):
            p.lectern(x0 + 15 + i * 4, F_NOBLE, zw1 - 3, "south")
            p.lectern(x0 + 15 + i * 4, F_NOBLE, zw1 - 6, "north")
        p.table(x0 + 29, F_NOBLE, zw1 - 4); p.table(x0 + 30, F_NOBLE, zw1 - 4)
        p.fill(x0 + 13, F_NOBLE, zw1 - 1, x0 + 31, F_NOBLE + 2, zw1 - 1, "minecraft:bookshelf")
        p.carpet(x0 + 14, x0 + 31, zw1 - 7, zw1 - 2, F_NOBLE)
        p.zone("workfloor", x0 + 13, F_NOBLE, outer_z[0], x0 + 31, outer_z[1])
        # treasury / exchequer: the chequered table (3 x 2 of black / white wool on a dais), coffers, the STRONGROOM 6 x 6
        # with 2-thick walls and an iron door
        tx0 = x0 + 33
        p.fill(tx0 + 2, F_NOBLE, zw1 - 6, tx0 + 4, F_NOBLE, zw1 - 5, "minecraft:white_wool")
        p.put(tx0 + 3, F_NOBLE, zw1 - 6, "minecraft:black_wool"); p.put(tx0 + 2, F_NOBLE, zw1 - 5, "minecraft:black_wool"); p.put(tx0 + 4, F_NOBLE, zw1 - 5, "minecraft:black_wool")
        p.lectern(tx0 + 3, F_NOBLE, zw1 - 4, "north")                  # the treasurer
        for i in range(4):
            p.barrel(tx0 + 1 + i, F_NOBLE, zw1 - 2)
        p.fill(tx0 + 9, F_NOBLE, zw1 - 9, tx0 + 16, F_NOBLE + 7, zw1 - 2, STONE)          # strongroom block (8 x 8 outer, 2-thick walls)
        p.clear(tx0 + 11, tx0 + 14, zw1 - 7, zw1 - 4, F_NOBLE, F_NOBLE + 3)
        p.door(tx0 + 9, F_NOBLE, zw1 - 5, "west", mat="minecraft:iron_door")
        p.put(tx0 + 10, F_NOBLE, zw1 - 5, AIR); p.put(tx0 + 10, F_NOBLE + 1, zw1 - 5, AIR)
        for i in range(4):
            p.chest(tx0 + 11 + i, F_NOBLE, zw1 - 7, "south")
        p.put(tx0 + 12, F_NOBLE, zw1 - 5, "minecraft:gold_block"); p.put(tx0 + 13, F_NOBLE, zw1 - 5, "minecraft:gold_block")
        p.zone("storeroom", tx0 + 11, F_NOBLE, zw1 - 7, tx0 + 14, zw1 - 4)
        # the judges' room ("Council of Ten", outer side x 42..51) with the wardrobe door: a barrel wall hiding a door
        # into the corridor and the enclosed bridge to the prison tower runs along the outer wall at the attic level
        p.fill(x0 + 32, F_NOBLE, inner_z[0], x0 + 32, F_NOBLE + 7, inner_z[1], PANEL)
        p.fill(x0 + 42, F_NOBLE, inner_z[0], x0 + 42, F_NOBLE + 7, inner_z[1], PANEL)
        p.door(x0 + 37, F_NOBLE, zc0 - 1, "north")
        p.table(x0 + 36, F_NOBLE, inner_z[0] + 3); p.table(x0 + 37, F_NOBLE, inner_z[0] + 3); p.table(x0 + 38, F_NOBLE, inner_z[0] + 3)
        for i in range(3):
            p.chair(x0 + 36 + i, F_NOBLE, inner_z[0] + 2, "south"); p.chair(x0 + 36 + i, F_NOBLE, inner_z[0] + 4, "north")
        p.fill(x0 + 41, F_NOBLE, inner_z[0] + 1, x0 + 41, F_NOBLE + 1, inner_z[1] - 1, "minecraft:barrel", facing_direction=1, open_bit=False)
        p.put(x0 + 41, F_NOBLE, inner_z[0] + 3, AIR); p.put(x0 + 41, F_NOBLE + 1, inner_z[0] + 3, AIR)
        p.jib_panel(x0 + 42, F_NOBLE, inner_z[0] + 3)                   # the wardrobe's back = the secret way to the treasury side
        p.zone("chamber", x0 + 33, F_NOBLE, inner_z[0], x0 + 41, inner_z[1])
        # the bridge of sighs: an enclosed 2-wide bridge at the attic level along the outer wall from the judges' bay to the tower
        p.fill(x0 + 12, F_ATTIC - 1, zw0 - 2, x0 + 41, F_ATTIC + 3, zw0 - 1, STONE)
        p.clear(x0 + 13, x0 + 41, zw0 - 2, zw0 - 2, F_ATTIC, F_ATTIC + 2)
        p.fill(x0 + 12, F_ATTIC, zw0 - 2, x0 + 12, F_ATTIC + 2, zw0 - 2, AIR)                  # into the tower
        p.windows_along(zw0 - 3, x0 + 12, x0 + 41, F_ATTIC + 1, h=1, pitch=3, axis="x")
        p.put(zw0 - 3, F_ATTIC + 1, x0 + 13, STONE) if False else None
        p.fill(x0 + 12, F_ATTIC - 1, zw0 - 3, x0 + 41, F_ATTIC + 3, zw0 - 3, STONE)
        p.fill(x0 + 41, F_ATTIC, zw0 - 1, x0 + 41, F_ATTIC + 2, zw0 - 1, AIR)                  # stair head from the judges' room
        p.flight(x0 + 38, inner_z[0] + 1, F_NOBLE, 7, "east", width=1)                        # judges' room -> bridge level
        p.fill(x0 + 41, F_NOBLE + 7, inner_z[0] + 1, x0 + 41, F_NOBLE + 7, inner_z[0] + 1, AIR)
        p.fill(x0 + 41, F_ATTIC, inner_z[0] + 1, x0 + 41, F_ATTIC + 2, inner_z[0] + 1, AIR)
        p.fill(x0 + 41, F_ATTIC, zw0, x0 + 41, F_ATTIC + 2, zw0, AIR)
        # ATTIC: the archive / muniment room (x 42..51), servants' garrets (men) 3 x 4 along the corridor
        p.fill(x0 + 32, F_ATTIC, zw0 + 1, x0 + 32, F_ATTIC + 3, zw1 - 1, STONE)
        p.door(x0 + 40, F_ATTIC, zc1 + 1, "south", mat="minecraft:iron_door")
        p.fill(x0 + 33, F_ATTIC, zw1 - 2, x0 + 40, F_ATTIC + 1, zw1 - 2, "minecraft:bookshelf")
        for i in range(4):
            p.chest(x0 + 34 + i * 2, F_ATTIC, zw1 - 5, "north")
        p.zone("storeroom", x0 + 33, F_ATTIC, outer_z[0], x0 + 41, outer_z[1])
        garrets(p, x0 + 13, x0 + 31, zw0, zw1, zc0, zc1)
    else:
        # EAST WING. GROUND: the household offices (court side = zw0 side): steward's room, servants' hall, butler's pantry
        # with the plate safe, housekeeper / still room / stores; the baize door to the service alley at the corps end
        rooms = [(x0 + 1, x0 + 9, "steward"), (x0 + 10, x0 + 22, "servants_hall"), (x0 + 23, x0 + 28, "butler"), (x0 + 29, x0 + 34, "housekeeper"), (x0 + 35, x0 + 40, "still"), (x0 + 41, x0 + 46, "stores")]
        for (ra, rb, kind) in rooms:
            p.fill(rb + 1, 0, inner_z[0], rb + 1, 4, inner_z[1], STONE) if rb + 1 < x1 else None
            p.door(ra + 2, 0, zc0 - 1, "north")
            if kind == "steward":
                p.lectern(ra + 2, 0, inner_z[0] + 1, "north"); p.table(ra + 4, 0, inner_z[0] + 3); p.chair(ra + 5, 0, inner_z[0] + 3, "west")
                p.zone("chamber", ra, 0, inner_z[0], rb, inner_z[1])
            elif kind == "servants_hall":
                for i in range(4):
                    p.table(ra + 3 + i * 2, 0, inner_z[0] + 3)
                    p.chair(ra + 3 + i * 2, 0, inner_z[0] + 2, "south"); p.chair(ra + 3 + i * 2, 0, inner_z[0] + 4, "north")
                for i in range(6):
                    p.bell(ra + 2 + i * 2, 1, inner_z[0] + 1, "south")     # the bell board (theatre)
                p.marker("station", "seat", ra + 6, 0, inner_z[0] + 3)
                p.zone("commons", ra, 0, inner_z[0], rb, inner_z[1])
            elif kind == "butler":
                p.chest(ra + 1, 0, inner_z[0] + 1, "south"); p.chest(ra + 2, 0, inner_z[0] + 1, "south")
                p.fill(ra + 4, 0, inner_z[0] + 1, rb, 4, inner_z[0] + 2, STONE)              # the plate safe (iron door)
                p.door(ra + 4, 0, inner_z[0] + 3, "west", mat="minecraft:iron_door") if False else None
                p.put(ra + 4, 0, inner_z[0] + 2, AIR); p.put(ra + 4, 1, inner_z[0] + 2, AIR)
                p.door(ra + 4, 0, inner_z[0] + 2, "west", mat="minecraft:iron_door")
                p.chest(rb, 0, inner_z[0] + 1, "west")
                p.marker("station", "store", ra + 2, 0, inner_z[0] + 3)
                p.zone("storeroom", ra, 0, inner_z[0], rb, inner_z[1])
            elif kind == "housekeeper":
                p.lectern(ra + 1, 0, inner_z[0] + 1, "north"); p.chest(ra + 3, 0, inner_z[0] + 1, "south"); p.chest(ra + 4, 0, inner_z[0] + 1, "south")
                p.marker("station", "store", ra + 3, 0, inner_z[0] + 3)
                p.zone("chamber", ra, 0, inner_z[0], rb, inner_z[1])
            elif kind == "still":
                p.put(ra + 2, 0, inner_z[0] + 1, "minecraft:brewing_stand", brewing_stand_slot_a_bit=False, brewing_stand_slot_b_bit=False, brewing_stand_slot_c_bit=False)
                p.put(ra + 4, 0, inner_z[0] + 1, "minecraft:furnace", **{"minecraft:cardinal_direction": "south"})
                p.marker("station", "oven", ra + 4, 0, inner_z[0] + 2)
                p.zone("kitchen", ra, 0, inner_z[0], rb, inner_z[1])
            else:
                for i in range(5):
                    p.barrel(ra + 1 + i, 0, inner_z[0] + 1)
                p.zone("storeroom", ra, 0, inner_z[0], rb, inner_z[1])
        # the BAIZE DOOR: a warped door in green wool at the corps end of the corridor's outer wall -> the alley side
        p.fill(x1 - 6, 0, zw1 - 1, x1 - 6, 2, zw1 - 1, "minecraft:green_wool")
        p.fill(x1 - 8, 0, zw1 - 1, x1 - 8, 2, zw1 - 1, "minecraft:green_wool")
        p.fill(x1 - 7, 3, zw1 - 1, x1 - 7, 3, zw1 - 1, "minecraft:green_wool")
        p.door(x1 - 7, 0, zw1 - 1, "south", mat="minecraft:warped_door")
        p.door(x1 - 7, 0, zc1 + 1, "south")
        p.marker("port", "passage", x1 - 7, 0, zw1 - 2)
        # ground, outer side (z zw1 side = the palace's east face): the CHAPEL at the corps end (x 44..61, two-level), stables' office
        chapel(p, x1 - 18, x1 - 1, outer_z[0], outer_z[1], zc1 + 1)
        for xx in (x0 + 1, x0 + 12, x0 + 24):
            p.fill(xx + 10, 0, outer_z[0], xx + 10, 4, outer_z[1], STONE) if xx + 10 < x1 - 18 else None
            p.door(xx + 4, 0, zc1 + 1, "south")
            p.bed(xx + 1, 0, outer_z[0] + 1, "east", role="servant"); p.bed(xx + 5, 0, outer_z[0] + 1, "east", role="servant"); p.chest(xx + 8, 0, outer_z[0] + 1, "west")
        p.zone("quarters", x0 + 1, 0, outer_z[0], x0 + 34, outer_z[1])
        # ÉTAGE NOBLE: officials' apartments x 8 (19 x 7 each: antechamber 6, bedchamber 7, cabinet 4 + closet) along both sides
        p.panel_room(x0 + 1, x1 - 1, zw0 + 1, zw1 - 1, F_NOBLE, F_NOBLE + 7)
        p.fill(x0 + 1, F_NOBLE - 1, zw0 + 1, x1 - 1, F_NOBLE - 1, zw1 - 1, FLOOR)
        apartments(p, x0 + 1, x1 - 5, inner_z, zc0 - 1, "north", F_NOBLE, 7)
        apartments(p, x0 + 1, x1 - 19, outer_z, zc1 + 1, "south", F_NOBLE, 7)
        p.carpet(x0 + 1, x1 - 5, zc0, zc1, F_NOBLE)
        # the chapel's upper level (family gallery) opens from the corridor at the corps end
        # ATTIC: officials' apartments (height 4) on the court side, women's garrets on the outer side
        apartments(p, x0 + 1, x1 - 5, inner_z, zc0 - 1, "north", F_ATTIC, 3)
        garrets(p, x0 + 1, x1 - 19, zw0, zw1, zc0, zc1, side="outer")
    # the back stair, laid LAST (228): the noble floor fill at feet 5 and the west wing's strongroom block (x 52..59) used to
    # be laid over its well after it (headroom blocked at 5..9: the stair never reached the attic); it ends at the attic
    # floor course (step off at 15) and never touches the roof (ceiling = the eave)
    p.clear(sx, sx + 2, zc0 - 1, zc1 + 1, 0, 18)
    # 228 (his 18:0x 'rework rooms now'): a B tower spiral (spruce + plaster), the well widened east over the panel line
    # x 62 (x 59..62, z 15..18): a door beside the step at the noble floor, the floor in front at the attic
    p.spiral2(sx, zc0 - 1, 0, [F_NOBLE, F_ATTIC], "B_tower", "spruce_plaster", ceiling=F_EAVE, label=f"{'west' if west else 'east'} wing back stair")
    p.notes.append(f"{'west' if west else 'east'} wing: corridor z {zc0}..{zc1}, back stair at x {sx}")


def garrets(p, xa, xb, zw0, zw1, zc0, zc1, side="both"):
    """servants' garrets 3 x 4 (two beds each) along the attic corridor"""
    for (za, zb, dz) in (((zw0 + 1, zw0 + 4, "north"),) if side in ("both", "inner") else ()) + (((zw1 - 4, zw1 - 1, "south"),) if side in ("both", "outer") else ()):
        wallz = zw0 + 5 if dz == "north" else zw1 - 5
        p.fill(xa, F_ATTIC, wallz, xb, F_ATTIC + 3, wallz, PANEL)
        for xx in range(xa, xb - 2, 4):
            p.fill(xx + 3, F_ATTIC, za, xx + 3, F_ATTIC + 3, zb, PANEL)
            p.door(xx + 1, F_ATTIC, wallz, dz)
            p.bed(xx, F_ATTIC, za + (0 if dz == "north" else 2), "east", role="servant")
            p.bed(xx, F_ATTIC, za + (2 if dz == "north" else 0), "east", role="servant")
        p.zone("quarters", xa, F_ATTIC, za, xb, zb)


def apartments(p, xa, xb, zr, zdoor, door_facing, f0, clear):
    """officials' apartments: 19 long each = antechamber 6 | bedchamber 7 | cabinet 4 (+ a 2 x 2 closet), rooms zr deep"""
    za, zb = zr
    x = xa
    n = 0
    while x + 18 <= xb:
        p.fill(x + 6, f0, za, x + 6, f0 + clear - 1, zb, PANEL)        # antechamber | bedchamber
        p.fill(x + 14, f0, za, x + 14, f0 + clear - 1, zb, PANEL)      # bedchamber | cabinet
        p.fill(x + 19, f0, za, x + 19, f0 + clear - 1, zb, PANEL) if x + 19 <= xb else None
        p.door(x + 2, f0, zdoor, door_facing)                          # corridor -> antechamber
        p.door(x + 6, f0, za + 3, "east")                              # antechamber -> bedchamber
        p.door(x + 14, f0, za + 3, "east")                             # bedchamber -> cabinet
        p.table(x + 2, f0, za + 3); p.chair(x + 3, f0, za + 3, "west"); p.chair(x + 1, f0, za + 3, "east")
        p.bed(x + 9, f0, za + 1, "east", role="noble")
        p.bed(x + 9, f0, zb - 1, "east", role="child")                # his 17:52: the children's bed, the bedchamber's far side
        p.fill(x + 7, f0 + 1, za + 2, x + 7, f0 + 2, za + 4, "minecraft:spruce_fence")      # the alcove's balustrade
        p.chest(x + 13, f0, za + 1, "west")
        p.lectern(x + 16, f0, za + 2, "west", station=False); p.chair(x + 17, f0, za + 2, "west")
        if clear > 4:
            p.fill(x + 1, f0 + clear - 1, za + 1, x + 1, f0 + clear - 1, za + 1, LIGHT)
        n += 1
        x += 19
    p.zone("chamber", xa, f0, za, min(xb, x - 1), zb)
    return n


def prison_stair(p, tx0, tx1, zw0, zw1):
    """228 (his 16:30 'C in the main towers' + 18:0x 'rework rooms now'): a C GRAND spiral (stone) in the tower's
    interior (x tx1-8..tx1-3, z zw1-11..zw1-6), laid after the wings (see build): its doors beside the step open into the
    tower at the interrogation floor (6: the wing's noble floor course at 5 is its floor) and the upper floor (11), and the
    floor in front lands at the piombi (17); the pozzi (ground) and the piombi's front wall (z zw1-5) stay clear of it"""
    p.spiral2(tx1 - 8, zw1 - 11, 0, [6, 11, 17], "C_grand", "stone", ceiling=22, label="prison tower", want=("ccw", 2))


def tower(p, tx0, tx1, zw0, zw1):
    """the prison tower 12 x 12 x 20 at the west wing's street end: Pozzi cells at ground (no windows), the interrogation
    room between, Piombi cells under the roof; its own spiral stair; battlemented top with a pyramid roof"""
    p.clear(tx0 + 1, tx1 - 1, zw0 + 1, zw1 - 1, 0, 21)
    p.shell(tx0, tx1, zw0, zw1, 0, 21, STONE)
    p.fill(tx0, 0, zw1, tx1, 21, zw1, STONE)
    p.shell(tx0 + 1, tx1 - 1, zw0 + 1, zw1 - 1, 0, 21, STONE)        # 2-thick walls
    p.clear(tx0 + 2, tx1 - 2, zw0 + 2, zw1 - 2, 0, 20)
    # floors: ground (pozzi) 0..3, slab 4, interrogation 5..9, slab 10, upper 11..15 (the bridge arrives at 15), slab 16,
    # piombi 17..19 under the roof
    for f in (4, 10, 16):
        p.fill(tx0 + 2, f, zw0 + 2, tx1 - 2, f, zw1 - 2, FLOOR)
        p.put(tx0 + 5, f + 1, zw0 + 5, LIGHT)
    # pozzi: 4 cells 3 x 2 along the north and south walls, iron bars
    for (cx, cz) in ((tx0 + 2, zw0 + 2), (tx0 + 6, zw0 + 2), (tx0 + 2, zw1 - 3), (tx0 + 6, zw1 - 3)):
        p.fill(cx, 0, cz, cx + 2, 3, cz + 1, AIR)
        p.fill(cx, 0, cz + (2 if cz == zw0 + 2 else -1), cx + 2, 2, cz + (2 if cz == zw0 + 2 else -1), "minecraft:iron_bars")
        p.fill(cx + 3, 0, cz, cx + 3, 3, cz + 1, STONE) if cx == tx0 + 2 else None
    p.zone("cellar", tx0 + 2, 0, zw0 + 2, tx1 - 2, zw1 - 2)
    # the stair: a spiral in the SE corner column of the tower, ground to the piombi
    p.later = getattr(p, "later", [])
    p.later.append(lambda: prison_stair(p, tx0, tx1, zw0, zw1))
    # interrogation room (5..9): a table, chairs, a lectern
    p.table(tx0 + 5, 5, zw0 + 5); p.chair(tx0 + 4, 5, zw0 + 5, "east"); p.chair(tx0 + 6, 5, zw0 + 5, "west")
    p.lectern(tx0 + 5, 5, zw0 + 3, "south", station=False)
    p.window(tx0, 7, zw0 + 5, 0, 1, 1, 1); p.window(tx0, 7, zw1 - 5, 0, 1, 1, 1)
    # piombi: 4 cells 3 x 3 under the roof (17..19), doors of iron
    for (cx, cz) in ((tx0 + 2, zw0 + 2), (tx0 + 6, zw0 + 2), (tx0 + 2, zw1 - 4), (tx0 + 6, zw1 - 4)):
        p.fill(cx + 3, 17, cz, cx + 3, 19, cz + 2, STONE) if cx == tx0 + 2 else None
        p.fill(cx, 17, cz + (3 if cz == zw0 + 2 else -1), cx + 2, 19, cz + (3 if cz == zw0 + 2 else -1), STONE)
        p.door(cx + 1, 17, cz + (3 if cz == zw0 + 2 else -1), "south" if cz == zw0 + 2 else "north", mat="minecraft:iron_door")
        p.bed(cx, 17, cz + 1, "east", role="cell")
    p.zone("cellar", tx0 + 2, 17, zw0 + 2, tx1 - 2, zw1 - 2)
    # the top: a battlemented parapet at 22 and a pyramid roof
    p.fill(tx0, 22, zw0, tx1, 22, zw1, CHISEL)
    for i in range(tx0, tx1 + 1, 2):
        p.put(i, 23, zw0, STONE); p.put(i, 23, zw1, STONE)
    for j in range(zw0, zw1 + 1, 2):
        p.put(tx0, 23, j, STONE); p.put(tx1, 23, j, STONE)
    p.roof_pyramid(tx0 + 1, tx1 - 1, zw0 + 1, zw1 - 1, 23)
    p.notes.append("prison tower: pozzi 4 cells, interrogation room, piombi 4 cells, spiral stair, bridge of sighs at the attic level")


def chapel(p, xa, xb, za, zb, zdoor):
    """the two-level chapel at the corps end of the east wing's outer side: nave with the altar at the corps end, the family
    gallery above (reached from the étage noble corridor), servants below"""
    p.clear(xa, xb, za, zb, 0, 13)
    p.fill(xa - 1, 0, za, xa - 1, 13, zb, STONE)
    p.fill(xa + 2, 13, za, xb, 13, zb, FLOOR)                       # the gallery floor (4 deep at the far end) — a balcony
    p.fill(xa + 2, 9, za, xa + 5, 9, zb, FLOOR)
    p.fill(xa + 5, 10, za, xa + 5, 10, zb, "minecraft:spruce_fence")
    p.door(xa + 1, 0, zdoor, "south")
    p.door(xa + 3, F_NOBLE, zdoor, "south")                         # gallery door from the corridor (its floor at 9 — steps)
    p.flight(xa + 2, zdoor - 1, F_NOBLE, 3, "east", width=1) if False else None
    p.fill(xb - 2, 0, za + 1, xb - 2, 1, zb - 1, "minecraft:smooth_stone")   # the altar dais
    p.fill(xb - 1, 1, za + 2, xb - 1, 3, zb - 2, "minecraft:chiseled_quartz_block")
    for i in range(4):
        for zz in (za + 1, za + 3):
            p.put(xa + 6 + i * 2, 0, zz, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "east"})
    p.fill(xb - 1, 4, za + 2, xb - 1, 6, zb - 2, GLASS)
    p.put(xb - 3, 2, za + 3, "minecraft:lantern", hanging=False)
    p.put(xa + 1, 1, zb - 1, "minecraft:brewing_stand", brewing_stand_slot_a_bit=False, brewing_stand_slot_b_bit=False, brewing_stand_slot_c_bit=False)
    p.marker("station", "seat", xa + 8, 0, za + 2)
    p.zone("commons", xa, 0, za, xb, zb)


def great_hall_vault(p):
    """228 (his idea, 10-06): the great hall's VAULTED CEILING. The hall (x 65..77, z 44..83, double height 0..13) keeps its
    walls, windows, trusses and gallery; its flat ceiling (the attic floor course at 14) is replaced by a barrel vault of
    upside-down pw:roof45_spruce running along the hall (z), springing at feet 14 against the court wall (x 64) and the
    jib partition (x 78): 13 cells across = rings 0..5 at feet 14..19 and the crown column x 71 (a spruce ridge beam at 19,
    VAULT_CROWN "beam"). The attic floor over the hall (the DECK) is the vault's topmost course, 19 (walk at 20); the corps'
    hipped roof (eave 19, x 65 at 20 ... peak 27) is the real roof above it. The attic bay over the hall (its 3 apartments,
    z 45..80) is not built; the court wall's attic windows in the bay (16..17) are bricked (they faced the vault's back)."""
    x0 = CORPS[0]
    deck = vault(p, x0 + 1, 77, HALL_BAY[0] + 1, HALL_BAY[1] - 1, F_SLAB2, axis="z", wood="spruce", crown=VAULT_CROWN)
    bricked = 0
    for z in range(HALL_BAY[0] + 1, HALL_BAY[1]):
        for f in range(F_SLAB2 + 1, deck + 1):
            if p.get(x0, f, z) == GLASS:
                p.put(x0, f, z, STONE)
                bricked += 1
    p.notes.append(f"great hall vault: barrel of inverted roof45_spruce, rings at feet {F_SLAB2}..{deck}, crown {VAULT_CROWN}, "
                   f"deck (attic floor) at {deck}, {bricked} attic window panes bricked")
    return deck


def corps(p):
    """the corps de logis x 64..81, z 8..119: court wall 64, state rooms 65..77, the jib-door partition 78, the hidden spine
    corridor 79..80, rear wall 81. Ground: the entrance hall + grand staircase (west of centre), the great hall (double
    height, centre), offices east; étage noble: antechamber, council chamber, audience / bedchamber, cabinet + Tesoretto,
    garde-robe + private stair at the east end; attic: officials' apartments; every state room with its jib door and bell"""
    x0, x1 = CORPS
    p.fill(x0, -2, Z0, x1, -1, Z1, STONE)
    p.fill(x0 + 1, -1, Z0 + 1, x1 - 1, -1, Z1 - 1, STATE_FLOOR)
    p.shell(x0, x1, Z0, Z1, 0, 18, STONE)
    p.clear(x0 + 1, x1 - 1, Z0 + 1, Z1 - 1, 0, 18)
    p.slab(x0, x1, Z0, Z1, F_SLAB1, FLOOR); p.shell(x0, x1, Z0, Z1, F_SLAB1, F_SLAB1, STONE)
    p.slab(x0, x1, Z0, Z1, F_SLAB2, ATTIC_FLOOR); p.shell(x0, x1, Z0, Z1, F_SLAB2, F_SLAB2, STONE)
    p.fill(x0, F_SLAB2, Z0, x1, F_SLAB2, Z1, CHISEL)
    p.fill(x0, F_SLAB1, Z0, x1, F_SLAB1, Z1, CHISEL)
    p.roof_hip(x0, x1, Z0, Z1, F_EAVE)
    # the hidden spine corridor on the ground and the noble floors (3 high), its partition x 78 with jib doors; above the
    # corridor the wall mass is solid stone; slit windows in the rear wall every 6
    xc0, xc1, xp = 79, 80, 78
    for f0 in (F_GROUND, F_NOBLE):
        p.fill(xp, f0, Z0 + 1, xp, f0 + (GROUND_CLEAR if f0 == F_GROUND else NOBLE_CLEAR) - 1, Z1 - 1, PANEL if f0 == F_NOBLE else STONE)
        p.clear(xc0, xc1, Z0 + 1, Z1 - 1, f0, f0 + 2)
        p.fill(xc0, f0 + 3, Z0 + 1, xc1, f0 + (GROUND_CLEAR if f0 == F_GROUND else NOBLE_CLEAR) - 1, Z1 - 1, STONE)
        for zz in range(Z0 + 4, Z1 - 3, 6):
            p.put(x1, f0 + 1, zz, GLASS)                               # slit windows
            p.lantern(xc0, f0 + 2, zz + 3, hanging=True)
    # the attic over the corridor: solid (the roof's rear slope)
    p.fill(xp, F_ATTIC, Z0 + 1, x1 - 1, F_ATTIC + 3, Z1 - 1, STONE)
    # windows: court side (x 64) ground 1..3 and noble 7..11 (tall), rear slits only; attic court side small
    p.windows_along(x0, Z0, Z1, 1, h=3, pitch=4)
    p.windows_along(x0, Z0, Z1, 7, h=5, pitch=4)
    p.windows_along(x0, Z0, Z1, 16, h=2, pitch=4)
    # ---- GROUND FLOOR (0..4): entrance hall centre (z 56..71) through to the great hall; grand staircase west (z 42..55);
    # the service lobby + back stairs at both ends and the centre; offices (registry, constable) east
    p.opening(x0, x0, 62, 65, 0, 4)                                   # the great door (4 wide, 5 high, open arch)
    p.fill(x0, 0, 61, x0, 4, 61, CHISEL); p.fill(x0, 0, 66, x0, 4, 66, CHISEL)
    p.fill(x0, 5, 62, x0, 5, 65, CHISEL)
    # the great hall: z 44..83 (40 wide), x 65..77, DOUBLE HEIGHT (0..13): remove the first-floor slab over it
    p.clear(x0 + 1, xp - 1, 44, 83, 0, 13)
    p.fill(x0 + 1, F_SLAB1, 44, xp - 1, F_SLAB1, 83, AIR)
    p.fill(x0 + 1, 0, 43, xp - 1, 13, 43, STONE); p.fill(x0 + 1, 0, 84, xp - 1, 13, 84, STONE)      # the hall's end walls
    p.fill(x0 + 1, 0, 44, xp - 1, 0, 83, STATE_FLOOR)
    p.fill(x0 + 1, 0, 44, xp - 1, 0, 83, STATE_FLOOR)
    p.fill(x0 + 1, -1, 44, xp - 1, -1, 83, STATE_FLOOR)
    p.carpet(x0 + 2, xp - 2, 62, 65, 0)
    p.fill(x0 + 1, 0, 80, xp - 1, 0, 83, SMOOTH)                      # the dais at the east end (1 high)
    p.put(x0 + 7, 1, 82, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "west"})      # the seat of judgement
    p.table(x0 + 6, 1, 81); p.table(x0 + 6, 1, 82); p.table(x0 + 6, 1, 83) if False else None
    # hammerbeam trusses: spruce log beams across the hall every 5 at 11 and posts against the walls
    for zz in range(46, 83, 5):
        p.fill(x0 + 1, 11, zz, xp - 1, 11, zz, POST)
        p.fill(x0 + 1, 8, zz, x0 + 1, 10, zz, POST); p.fill(xp - 1, 8, zz, xp - 1, 10, zz, POST)
        p.put(x0 + 7, 12, zz, "minecraft:lantern", hanging=True)
    # tall court-side windows of the hall (every 4, 7..11 already); the hall's rear jib doors at 50 and 77
    p.jib_door = None
    for zz in (50, 77):
        p.door(xp, 0, zz, "east")                                     # jib doors: a spruce door in the panelled rear wall
        p.fill(xp, 0, zz - 2, xp, 4, zz + 2, PANEL); p.door(xp, 0, zz, "east")
        p.button(xp - 1, 2, zz + 1, "west"); p.bell(xc0, 0, zz + 1, "west")
    p.zone("commons", x0 + 1, 0, 44, xp - 1, 83)
    p.marker("station", "seat", x0 + 7, 1, 82)
    # the grand staircase: an open well z 30..41 (12 wide), x 65..77; two flights up to the noble floor (6)
    p.clear(x0 + 1, xp - 1, 30, 41, 0, 13)
    p.fill(x0 + 1, F_SLAB1, 30, xp - 1, F_SLAB1, 41, AIR)
    p.fill(x0 + 1, 0, 29, xp - 1, 4, 29, STONE); p.fill(x0 + 1, 0, 42, xp - 1, 4, 42, STONE)
    p.door(x0 + 1 + 3, 0, 42, "south"); p.door(x0 + 1 + 3, 0, 29, "north")
    p.opening(x0 + 6, x0 + 9, 43, 43, 0, 4)                            # from the hall into the stair hall
    p.opening(x0 + 6, x0 + 9, 42, 42, 0, 4)
    p.flight(x0 + 2, 32, 0, 6, "east", width=3, across=(0, 1), mat="minecraft:stone_brick_stairs")          # first flight up along x
    p.fill(x0 + 8, 5, 32, x0 + 11, 5, 34, STONE)                        # the half landing
    p.fill(x0 + 8, 6, 30, x0 + 11, 6, 41, FLOOR)                       # the landing floor at the noble level (x 72..75 across the well)
    p.fill(x0 + 8, 6, 35, x0 + 11, 6, 41, AIR)
    p.flight(x0 + 11, 35, 5, 1, "south", width=3, across=(-1, 0), mat="minecraft:stone_brick_stairs") if False else None
    p.fill(x0 + 8, F_NOBLE - 1, 35, x0 + 11, F_NOBLE - 1, 41, STONE)   # the upper landing slab (feet 5) continuing to the noble floor
    p.fill(x0 + 1, 5, 30, x0 + 7, 5, 41, AIR)                         # the open well
    p.fill(x0 + 1, 6, 30, x0 + 1, 6, 41, "minecraft:iron_bars")        # the gallery railing around the well (noble level)
    p.fill(x0 + 1, 6, 30, x0 + 7, 6, 30, "minecraft:iron_bars"); p.fill(x0 + 1, 6, 41, x0 + 7, 6, 41, "minecraft:iron_bars")
    p.fill(x0 + 8, 6, 30, x0 + 11, 6, 34, FLOOR)
    p.put(x0 + 4, 12, 35, "minecraft:lantern", hanging=True)
    p.zone("threshold", x0 + 1, 0, 30, xp - 1, 41)
    # ground west of the stair (z 9..28): the registry (cartography) and a waiting room; east of the hall (z 85..118): the
    # constable's office, the guard post, and the service lobby with the centre back stair
    p.fill(x0 + 1, 0, 28, xp - 1, 4, 28, STONE)
    p.put(x0 + 3, 0, 12, "minecraft:cartography_table"); p.lectern(x0 + 3, 0, 14, "west"); p.marker("station", "desk", x0 + 3, 0, 12)
    p.fill(x0 + 1, 0, 18, xp - 1, 4, 18, STONE); p.door(x0 + 4, 0, 18, "south")
    for i in range(4):
        p.put(x0 + 2 + i * 2, 0, 22, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "south"})
    p.zone("shopfloor", x0 + 1, 0, 9, xp - 1, 17); p.zone("threshold", x0 + 1, 0, 19, xp - 1, 27)
    p.door(x0, 0, 13, "west"); p.door(x0, 0, 23, "west")             # court doors of the registry and the waiting room
    p.fill(x0 + 1, 0, 95, xp - 1, 4, 95, STONE); p.fill(x0 + 1, 0, 106, xp - 1, 4, 106, STONE)
    p.door(x0 + 4, 0, 95, "south"); p.door(x0 + 4, 0, 106, "south"); p.door(x0, 0, 90, "west"); p.door(x0, 0, 112, "west")
    p.lectern(x0 + 3, 0, 88, "west"); p.marker("station", "post", x0 + 6, 0, 100); p.marker("station", "post", x0 + 6, 0, 110)
    for i in range(4):
        p.bed(x0 + 2 + i * 3, 0, 108, "south", role="guard")
    p.zone("chamber", x0 + 1, 0, 85, xp - 1, 94); p.zone("quarters", x0 + 1, 0, 107, xp - 1, 118)
    # back stairs x3: laid LAST (228, end of corps())
    # ---- ÉTAGE NOBLE (6..13): the appartement from west to east along the court: landing (30..41) | antechamber 42..53 |
    # (the hall's void 44..83 is double height — the noble rooms east of it) council chamber 85..102 | audience /
    # bedchamber 103..112 | cabinet 113..118 with the Tesoretto behind a painting; the garde-robe + the private stair in the
    # corps' east end bay; west of the landing: the waiting gallery 9..29
    p.panel_room(x0 + 1, xp, Z0 + 1, Z1 - 1, F_NOBLE, F_NOBLE + 7)
    p.fill(x0 + 1, F_NOBLE - 1, Z0 + 1, xp - 1, F_NOBLE - 1, 29, FLOOR)
    p.fill(x0 + 1, F_NOBLE - 1, 85, xp - 1, F_NOBLE - 1, Z1 - 1, FLOOR)
    p.fill(x0 + 1, F_NOBLE, 85, xp - 1, F_NOBLE + 7, 85, PANEL)          # hall end wall above the slab is already stone; the suite begins at 85
    p.fill(x0 + 1, F_NOBLE, 102, xp - 1, F_NOBLE + 7, 102, PANEL)
    p.fill(x0 + 1, F_NOBLE, 112, xp - 1, F_NOBLE + 7, 112, PANEL)
    # the hall's gallery: a 2-deep balcony along the court wall at the noble level over the hall (x 65..66, z 44..83)
    p.fill(x0 + 1, F_NOBLE - 1, 44, x0 + 2, F_NOBLE - 1, 83, FLOOR)
    p.fill(x0 + 3, F_NOBLE, 44, x0 + 3, F_NOBLE, 83, "minecraft:spruce_fence")
    p.opening(x0 + 1, x0 + 2, 43, 43, F_NOBLE, F_NOBLE + 2); p.opening(x0 + 1, x0 + 2, 84, 84, F_NOBLE, F_NOBLE + 2)
    # antechamber (west of the hall, z 42..43 is a wall; the antechamber is the landing's east neighbour: use z 29..41 as
    # the landing itself; the suite east of the hall:)
    rooms = [("council", 86, 101), ("audience", 103, 111), ("cabinet", 113, 118)]
    for (kind, za, zb) in rooms:
        p.carpet(x0 + 2, xp - 2, za + 1, zb - 1, F_NOBLE)
        zj = (za + zb) // 2
        p.door(xp, F_NOBLE, zj, "east")                                 # the JIB DOOR into the spine corridor
        p.button(xp - 1, F_NOBLE + 1, zj + 1, "west"); p.bell(xc0, F_NOBLE, zj + 1, "west")
        p.lantern(x0 + 7, F_NOBLE + 6, zj, hanging=True)
        if kind == "council":
            for i in range(8):
                p.chair(x0 + 3, F_NOBLE, za + 2 + i * 2, "east"); p.chair(xp - 3, F_NOBLE, za + 2 + i * 2, "west")
            for i in range(8):
                p.chair(x0 + 4 + i, F_NOBLE, zb - 2, "north")
            p.table(x0 + 7, F_NOBLE, zj - 1); p.table(x0 + 7, F_NOBLE, zj); p.table(x0 + 7, F_NOBLE, zj + 1)
            p.lectern(x0 + 7, F_NOBLE, za + 2, "south")
            p.marker("station", "seat", x0 + 7, F_NOBLE, zb - 3)
            p.zone("chamber", x0 + 1, F_NOBLE, za, xp - 1, zb)
            p.door(x0 + 4, F_NOBLE, za, "north"); p.door(x0 + 4, F_NOBLE, zb + 1, "south")
        elif kind == "audience":
            # the alcove 4 deep at the rear with its balustrade; the bed; the jib door is IN the alcove wall
            p.fill(xp - 4, F_NOBLE + 1, za + 1, xp - 4, F_NOBLE + 1, zb - 1, "minecraft:spruce_fence")
            p.put(xp - 4, F_NOBLE + 1, zj, AIR)
            p.bed(xp - 2, F_NOBLE, zj - 2, "east", role="lord")
            p.bed(xp - 2, F_NOBLE, zj + 2, "east", role="child")       # his 17:52: the children's bed in the alcove
            p.put(x0 + 3, F_NOBLE, zj, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "east"})   # the chair of state
            p.chest(xp - 2, F_NOBLE, za + 1, "west")
            p.zone("chamber", x0 + 1, F_NOBLE, za, xp - 1, zb)
            p.door(x0 + 4, F_NOBLE, zb + 1, "south")
        else:
            p.lectern(x0 + 4, F_NOBLE, zj, "west")                       # the ruler's desk
            p.fill(x0 + 1, F_NOBLE + 1, za + 1, x0 + 1, F_NOBLE + 3, zb - 1, "minecraft:bookshelf")   # the map / book wall (court side)
            # the TESORETTO: a 3 x 3 strongroom behind a PAINTING in the room's east (end) wall
            p.fill(x0 + 1, F_NOBLE, zb, xp, F_NOBLE + 7, zb, PANEL)
            p.secret_painting(x0 + 5, F_NOBLE, zb, "north")                # the canvas' left column (seen from the cabinet) at x0 + 5, its right at x0 + 4
            p.clear(x0 + 3, x0 + 5, zb + 1, zb + 3, F_NOBLE, F_NOBLE + 2)
            p.fill(x0 + 2, F_NOBLE, zb + 1, x0 + 2, F_NOBLE + 3, zb + 3, STONE); p.fill(x0 + 6, F_NOBLE, zb + 1, x0 + 6, F_NOBLE + 3, zb + 3, STONE)
            p.fill(x0 + 3, F_NOBLE, zb + 4, x0 + 5, F_NOBLE + 3, zb + 4, STONE) if zb + 4 <= Z1 - 1 else None
            p.chest(x0 + 3, F_NOBLE, zb + 3, "north"); p.chest(x0 + 5, F_NOBLE, zb + 3, "north"); p.put(x0 + 4, F_NOBLE, zb + 3, "minecraft:gold_block")
            p.zone("chamber", x0 + 1, F_NOBLE, za, xp - 1, zb - 1)
    # the garde-robe + the private stair: the corps' east end bay beyond the cabinet's end wall (z 119 is the outer wall —
    # the Duke-of-Athens stair goes down inside the rear corridor's east spiral to the alley door)
    p.door(x1, 0, Z1 - 2, "east")                                     # the alley door at the foot of the east back stair
    # ---- ATTIC (15..18): officials' apartments over the hall and council (court side; the corridor side is roof mass)
    p.fill(x0 + 1, F_ATTIC, Z0 + 1, xp - 1, F_ATTIC + 3, Z1 - 1, AIR)
    p.fill(xp - 2, F_ATTIC, Z0 + 1, xp - 2, F_ATTIC + 3, Z1 - 1, PANEL)   # the attic corridor runs along the rear (x 76..77)
    p.clear(xp - 1, xp - 1, Z0 + 1, Z1 - 1, F_ATTIC, F_ATTIC + 3)
    n = apartments(p, Z0 + 1, Z1 - 4, (x0 + 1, xp - 3), xp - 2, "east", F_ATTIC, 4) if False else 0
    # (apartments() lays rooms along x; the attic rooms run along z, so lay them directly)
    for zz in range(Z0 + 1, Z1 - 12, 12):
        if VAULTS and HALL_BAY[0] <= zz and zz + 11 <= HALL_BAY[1]:
            continue                                                  # 228: the great hall's vault fills this attic bay
        if VAULTS and zz <= HALL_BAY[1] < zz + 5:
            # 228: the vault's end wall (z 84) cuts this apartment's front room down to one row: lay it as ONE room behind
            # the end wall (no partition), its front-room furniture moved in beside the bed
            zr = HALL_BAY[1] + 1
            p.fill(x0 + 1, F_ATTIC, zz + 11, xp - 3, F_ATTIC + 3, zz + 11, PANEL)
            p.door(xp - 2, F_ATTIC, zz + 5, "east")
            p.bed(x0 + 2, F_ATTIC, zz + 7, "south", role="noble"); p.table(x0 + 3, F_ATTIC, zr + 1); p.chair(x0 + 4, F_ATTIC, zr + 1, "west"); p.chest(x0 + 2, F_ATTIC, zr, "east")
            p.bed(xp - 3, F_ATTIC, zz + 7, "south", role="child")      # his 17:52 + 18:02: the children's bed, against the east wall
            n += 1
            continue
        p.fill(x0 + 1, F_ATTIC, zz + 11, xp - 3, F_ATTIC + 3, zz + 11, PANEL)
        p.door(xp - 2, F_ATTIC, zz + 5, "east")
        p.fill(x0 + 1, F_ATTIC, zz + 5, xp - 3, F_ATTIC + 3, zz + 5, PANEL); p.door(x0 + 5, F_ATTIC, zz + 5, "south")
        p.bed(x0 + 2, F_ATTIC, zz + 7, "south", role="noble"); p.table(x0 + 3, F_ATTIC, zz + 2); p.chair(x0 + 4, F_ATTIC, zz + 2, "west"); p.chest(x0 + 2, F_ATTIC, zz + 1, "east")
        p.bed(xp - 3, F_ATTIC, zz + 7, "south", role="child")          # his 17:52 + 18:02: the children's bed, against the east wall
        n += 1
    if VAULTS:
        p.zone("quarters", x0 + 1, F_ATTIC, Z0 + 1, xp - 3, HALL_BAY[0] - 1)
        p.zone("quarters", x0 + 1, F_ATTIC, HALL_BAY[1] + 1, xp - 3, Z1 - 1)
        great_hall_vault(p)
    else:
        p.zone("quarters", x0 + 1, F_ATTIC, Z0 + 1, xp - 3, Z1 - 1)
    # back stairs x3 (3 x 3 spirals in the corridor line: west end z 9..11, centre z 85..87, east end z 116..118) ground -> attic.
    # 228: laid LAST — the étage noble panelling (panel_room at x 78, feet 6..13) used to fill their wells after them
    # (headroom blocked at 6..10: they never reached the attic); they end at the attic floor course (step off at 15) and
    # never touch the roof (ceiling = the eave)
    for zs in (Z0 + 1, 85, Z1 - 3):
        p.clear(xc0 - 1, xc1, zs, zs + 2, 0, 18)
        # 228 (his 18:0x 'rework rooms now'): a B tower spiral (spruce + plaster), the well widened west over the panel
        # line (x 77..80) and to 4 rows (the masonry under the rear roof slope is cleared in the well only: the roof stays)
        z4 = zs if zs < 100 else zs - 1
        p.clear(xc0 - 2, xc1, max(Z0 + 1, z4 - 1), min(Z1 - 1, z4 + 4), F_ATTIC, 18)   # the well + one row each side (a step-off bay)
        p.spiral2(xc0 - 2, z4, 0, [F_NOBLE, F_ATTIC], "B_tower", "spruce_plaster", ceiling=F_EAVE, label=f"corps back stair z {z4}")
        if zs > 100:
            # the east well takes the cabinet's jib door (z 115): the cabinet keeps a door to the spine corridor one row north,
            # and the stair's door beside the step opens into the cabinet itself (the private stair)
            p.door(xc0 - 1, F_NOBLE, z4 - 1, "east")
    p.notes.append(f"corps: great hall 40 x 13 x 14 (double height), grand stair, council / audience / cabinet + Tesoretto, hidden corridor 110 long, 3 back stairs, attic apartments {n}")


def service_court(p):
    """x 86..127: the kitchen block along the west edge (40 x 14), the little commons on the north edge (40 x 14 x 3 storeys),
    the laundry / brewhouse, the stables + coach house along the east edge, the smithy; a well in the court"""
    x0, x1 = SERVICE
    # kitchen block: x 86..125, z 0..13 — the great kitchen (16 x 12, 3 hearths), scullery, 3 larders, the bakehouse;
    # the buttery hatch + covered passage toward the corps' east back-stair door (alley side)
    kz0, kz1 = 0, 13
    p.fill(x0, -2, kz0, x1 - 2, -1, kz1, STONE)
    p.fill(x0 + 1, -1, kz0 + 1, x1 - 3, -1, kz1 - 1, SMOOTH)
    p.shell(x0, x1 - 2, kz0, kz1, 0, 5, STONE)
    p.clear(x0 + 1, x1 - 3, kz0 + 1, kz1 - 1, 0, 5)
    p.slab(x0, x1 - 2, kz0, kz1, 6, STONE); p.roof_hip(x0, x1 - 2, kz0, kz1, 7)
    p.windows_along(kz1, x0, x1 - 2, 1, h=2, pitch=4, axis="x")
    p.windows_along(kz0, x0, x1 - 2, 1, h=2, pitch=4, axis="x")
    # great kitchen x 86..103 with 3 hearths on the west (outer) wall
    p.fill(x0 + 18, 0, kz0 + 1, x0 + 18, 5, kz1 - 1, STONE); p.door(x0 + 18, 0, kz0 + 6, "east")
    for zz in (3, 7, 10):
        p.put(x0 + 1, 0, zz, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": "east", "pw:phase": "cold"})
        p.fill(x0 + 1, 1, zz, x0 + 1, 8, zz, "pw:flue_stone_bricks", **{"pw:cap": 0}); p.put(x0 + 1, 9, zz, "pw:flue_stone_bricks", **{"pw:cap": 1})
        p.marker("station", "hearth", x0 + 2, 0, zz)
    for i in range(3):
        p.put(x0 + 6 + i * 4, 0, kz1 - 2, "minecraft:smoker", **{"minecraft:cardinal_direction": "north"})
        p.marker("station", "prep", x0 + 6 + i * 4, 0, kz1 - 3)
    p.table(x0 + 8, 0, 6); p.table(x0 + 9, 0, 6); p.table(x0 + 10, 0, 6); p.put(x0 + 12, 0, 6, "minecraft:composter", composter_fill_level=0)
    p.marker("station", "table", x0 + 9, 0, 7)
    p.zone("kitchen", x0 + 1, 0, kz0 + 1, x0 + 17, kz1 - 1)
    # scullery (floor one lower), larders x3, bakehouse east of the kitchen
    p.fill(x0 + 19, 0, kz0 + 1, x0 + 24, 0, kz1 - 1, AIR); p.fill(x0 + 19, -1, kz0 + 1, x0 + 24, -1, kz1 - 1, SMOOTH)
    p.put(x0 + 21, 0, kz0 + 2, "minecraft:cauldron", cauldron_liquid="water", fill_level=6)
    p.fill(x0 + 25, 0, kz0 + 1, x0 + 25, 5, kz1 - 1, STONE); p.door(x0 + 25, 0, kz0 + 6, "east")
    for i in range(3):
        p.fill(x0 + 26 + i * 4, 0, kz0 + 1, x0 + 26 + i * 4, 5, kz0 + 5, STONE) if i else None
        p.barrel(x0 + 27 + i * 4, 0, kz0 + 2); p.barrel(x0 + 28 + i * 4, 0, kz0 + 2); p.chest(x0 + 27 + i * 4, 0, kz0 + 4, "south")
    p.put(x0 + 33, 0, kz1 - 2, "minecraft:furnace", **{"minecraft:cardinal_direction": "north"}); p.put(x0 + 35, 0, kz1 - 2, "minecraft:furnace", **{"minecraft:cardinal_direction": "north"})
    p.marker("station", "oven", x0 + 34, 0, kz1 - 3)
    p.zone("storeroom", x0 + 26, 0, kz0 + 1, x0 + 37, kz0 + 5); p.zone("kitchen", x0 + 26, 0, kz0 + 7, x0 + 37, kz1 - 1)
    p.door(x0 + 5, 0, kz1, "south"); p.door(x0 + 30, 0, kz1, "south")       # doors into the court
    # the covered passage: from the kitchen's court door along the alley to the corps' east back-stair door (x 82..85 is the
    # alley; the passage is a 2-wide roofed walk along the alley's north edge from z 13 to z 117, 3 high)
    if PASSAGE_ROOF == "lean":
        # 228 (his ruling 10-06: "one-slope roof of our spruce roof blocks"): two pw:roof45_spruce courses falling EAST, away
        # from the corps (x 86 eave at feet 3 over the posts, x 85 at 4), a spruce log head plate on the high edge (x 84, 4)
        # carried by its own post line (x 84, feet 0..3) at the same z as the eave posts: a two-post pentice, nothing floats
        roof_lean(p, x0 - 1, x0, 14, Z1 - 1, 3, downhill="east", wood="spruce")
        for zz in range(16, Z1 - 1, 4):
            p.column(x0 - 2, zz, 0, 3)
    else:
        p.fill(x0 - 1, 3, 14, x0, 3, Z1 - 1, "minecraft:spruce_slab", **{"minecraft:vertical_half": "top"})
    for zz in range(16, Z1 - 1, 4):
        p.column(x0, zz, 0, 2)
    # LITTLE COMMONS: x 114..127, z 30..69 (40 wide, 14 deep), 3 storeys: dining halls on the ground, 24 two-room lodgings above
    cx0, cx1, cz0, cz1 = x1 - 13, x1, 30, 69
    p.fill(cx0, -2, cz0, cx1, -1, cz1, STONE); p.fill(cx0 + 1, -1, cz0 + 1, cx1 - 1, -1, cz1 - 1, FLOOR)
    p.shell(cx0, cx1, cz0, cz1, 0, 13, STONE); p.clear(cx0 + 1, cx1 - 1, cz0 + 1, cz1 - 1, 0, 13)
    p.slab(cx0, cx1, cz0, cz1, 5, FLOOR); p.shell(cx0, cx1, cz0, cz1, 5, 5, STONE)
    p.slab(cx0, cx1, cz0, cz1, 10, FLOOR); p.shell(cx0, cx1, cz0, cz1, 10, 10, STONE)
    p.roof_hip(cx0, cx1, cz0, cz1, 14)
    p.windows_along(cx0, cz0, cz1, 1, h=2, pitch=4); p.windows_along(cx0, cz0, cz1, 6, h=2, pitch=4); p.windows_along(cx0, cz0, cz1, 11, h=2, pitch=4)
    p.door(cx0, 0, 40, "west"); p.door(cx0, 0, 59, "west")
    p.fill(cx0 + 1, 0, 49, cx1 - 1, 4, 49, STONE); p.fill(cx0 + 1, 0, 50, cx1 - 1, 4, 50, STONE)
    for zz in (34, 38, 42, 55, 59, 63):
        p.table(cx0 + 6, 0, zz); p.table(cx0 + 7, 0, zz); p.chair(cx0 + 5, 0, zz, "east"); p.chair(cx0 + 8, 0, zz, "west")
    p.marker("station", "seat", cx0 + 6, 0, 36); p.marker("station", "seat", cx0 + 6, 0, 57)
    p.zone("commons", cx0 + 1, 0, cz0 + 1, cx1 - 1, 48); p.zone("commons", cx0 + 1, 0, 51, cx1 - 1, cz1 - 1)
    for f0 in (6, 11):                                                  # lodgings: a 2-wide corridor along the court side, rooms behind
        p.fill(cx0 + 3, f0, cz0 + 1, cx0 + 3, f0 + 3, cz1 - 1, PANEL)
        for zz in range(cz0 + 1, cz1 - 4, 5):
            p.fill(cx0 + 4, f0, zz + 4, cx1 - 1, f0 + 3, zz + 4, PANEL)
            p.door(cx0 + 3, f0, zz + 2, "east")
            p.bed(cx0 + 5, f0, zz + 1, "east", role="servant"); p.bed(cx0 + 5, f0, zz + 3, "east", role="servant") if False else None
            p.chest(cx1 - 2, f0, zz + 1, "west")
        p.zone("quarters", cx0 + 4, f0, cz0 + 1, cx1 - 1, cz1 - 1)
    # the commons' stair (south end). 228: the well is opened in the floors at 5 and 10 FIRST (those clears used to erase the
    # steps at 5 and 10: two 2-block gaps), the last step is the top floor's course (10: step off at 11), ceiling = the eave 14
    # 228 (his 18:0x 'rework rooms now'): a STAIR HALL at the commons' south end on both lodging floors (x 115..126,
    # z 61..68: the last lodging and the end room give way) and a B tower spiral (spruce + plaster) standing in it
    # (x 119..122, z 64..67, clear of the dining hall's tables at z 63): a 4-block step-off on every side, so the door
    # beside the step (first floor) and the floor in front (second floor) both land in the hall; the corridor runs into it
    for f0 in (6, 11):
        p.clear(cx0 + 1, cx1 - 1, cz1 - 8, cz1 - 1, f0, min(f0 + 3, 13))       # up to the slab / under the eave (no floating partitions)
    p.spiral2(cx0 + 5, cz1 - 5, 0, [6, 11], "B_tower", "spruce_plaster", ceiling=14, label="little commons")
    # LAUNDRY / BREWHOUSE: x 118..127, z 14..27 (10 deep along x, 14 along z), cauldrons, a drying yard beside
    lx0, lx1, lz0, lz1 = x1 - 9, x1, 14, 27
    p.fill(lx0, -2, lz0, lx1, -1, lz1, STONE); p.fill(lx0 + 1, -1, lz0 + 1, lx1 - 1, -1, lz1 - 1, SMOOTH)
    p.shell(lx0, lx1, lz0, lz1, 0, 5, STONE); p.clear(lx0 + 1, lx1 - 1, lz0 + 1, lz1 - 1, 0, 5)
    p.slab(lx0, lx1, lz0, lz1, 6, STONE); p.roof_hip(lx0, lx1, lz0, lz1, 7)
    p.door(lx0, 0, lz0 + 6, "west")
    for i in range(3):
        p.put(lx0 + 3, 0, lz0 + 3 + i * 3, "minecraft:cauldron", cauldron_liquid="water", fill_level=6)
    p.marker("station", "prep", lx0 + 4, 0, lz0 + 6)
    p.zone("workfloor", lx0 + 1, 0, lz0 + 1, lx1 - 1, lz1 - 1)
    p.fill(x0 + 2, 1, 15, x0 + 2, 1, 27, "minecraft:spruce_fence")      # drying lines (fence posts with lanterns)
    # STABLES + COACH HOUSE: x 86..125, z 116..127 (40 long along x, 12 deep), 12 stalls 3 wide, the grooms' loft above
    sx0, sx1, sz0, sz1 = x0, x1 - 2, 116, 127
    p.fill(sx0, -2, sz0, sx1, -1, sz1, STONE); p.fill(sx0 + 1, -1, sz0 + 1, sx1 - 1, -1, sz1 - 1, COBBLE)
    p.shell(sx0, sx1, sz0, sz1, 0, 8, STONE); p.clear(sx0 + 1, sx1 - 1, sz0 + 1, sz1 - 1, 0, 8)
    p.slab(sx0, sx1, sz0, sz1, 5, FLOOR); p.shell(sx0, sx1, sz0, sz1, 5, 5, STONE)
    p.roof_hip(sx0, sx1, sz0, sz1, 9)
    for xx in range(sx0 + 1, sx1 - 2, 3):
        p.fill(xx + 2, 0, sz1 - 4, xx + 2, 1, sz1 - 1, "minecraft:spruce_fence")   # stall partitions on the far side
        p.put(xx + 1, 0, sz1 - 1, "minecraft:hay_block", pillar_axis="y")
    p.marker("station", "pen", sx0 + 6, 0, sz1 - 2); p.marker("station", "pen", sx0 + 20, 0, sz1 - 2)
    for zz in (sz0 + 2, sz0 + 4):
        p.door(sx0 + 20, 0, sz0, "north") if zz == sz0 + 2 else None
    p.opening(sx0 + 5, sx0 + 8, sz0, sz0, 0, 4); p.opening(sx0 + 30, sx0 + 33, sz0, sz0, 0, 4)   # coach doors (open arches)
    for i in range(4):
        p.bed(sx0 + 3 + i * 4, 6, sz0 + 2, "east", role="servant")
    # 228 (his 18:0x): the coach house's stair is a B tower spiral (oak) in the SE corner (the last stall's partition goes)
    p.spiral2(sx1 - 4, sz1 - 4, 0, [6], "B_tower", "oak", ceiling=9, label="coach house")
    p.zone("stable", sx0 + 1, 0, sz0 + 1, sx1 - 1, sz1 - 1); p.zone("quarters", sx0 + 1, 6, sz0 + 1, sx1 - 1, sz1 - 1)
    # SMITHY 8 x 8: x 118..125, z 104..111
    mx0, mx1, mz0, mz1 = x1 - 9, x1 - 2, 104, 111
    p.fill(mx0, -2, mz0, mx1, -1, mz1, STONE); p.fill(mx0 + 1, -1, mz0 + 1, mx1 - 1, -1, mz1 - 1, COBBLE)
    p.shell(mx0, mx1, mz0, mz1, 0, 4, STONE); p.clear(mx0 + 1, mx1 - 1, mz0 + 1, mz1 - 1, 0, 4)
    p.slab(mx0, mx1, mz0, mz1, 5, STONE); p.roof_hip(mx0, mx1, mz0, mz1, 6)
    p.opening(mx0, mx0, mz0 + 3, mz0 + 4, 0, 3)
    p.put(mx1 - 1, 0, mz0 + 2, "minecraft:blast_furnace", **{"minecraft:cardinal_direction": "west"})
    p.put(mx1 - 1, 0, mz0 + 4, "minecraft:anvil", **{"minecraft:cardinal_direction": "west", "damage": "undamaged"})
    p.put(mx1 - 1, 0, mz0 + 6, "minecraft:smithing_table")
    p.marker("station", "anvil", mx1 - 2, 0, mz0 + 4)
    p.zone("workfloor", mx0 + 1, 0, mz0 + 1, mx1 - 1, mz1 - 1)
    # the service court's WELL: a stone ring with water, in the middle of the court (x 100, z 70)
    p.fill(99, -1, 69, 101, -1, 71, STONE); p.put(100, -1, 70, WATER); p.fill(99, 0, 69, 101, 0, 71, "minecraft:stone_brick_slab", **{"minecraft:vertical_half": "bottom"}); p.put(100, 0, 70, AIR)
    p.marker("port", "well", 100, 0, 72)
    p.zone("yard", x0 + 1, 0, 15, x1 - 1, 115)
    p.notes.append("service court: great kitchen (3 hearths, 3 smokers), scullery, larders, bakehouse, little commons (2 dining halls + lodgings), laundry, stables (grooms' loft), smithy, well")


# ================================================================================================= pieces, stages, renders
def build():
    p = Palace()
    ground_and_foundations(p)
    gate_range(p)
    wing(p, WW[0], WW[1], west=True)
    wing(p, EW[0], EW[1], west=False)
    corps(p)
    service_court(p)
    # 228: the tower stairs are laid LAST (the west wing's noble floor fill at feet 5 is laid after tower() and used to
    # overwrite the prison stair's step at 5 — harmless for full-block steps, fatal for the spiral blocks)
    for fn in getattr(p, "later", []):
        fn()
    p.close_air()
    return p


PIECES = {"sw": (0, 0), "se": (0, 64), "nw": (64, 0), "ne": (64, 64)}    # (x origin, z origin) of each 64 x 64 piece


def cut(p):
    """the four pieces: 64 x H x 64 structures with their markers (entity positions re-based)"""
    out = {}
    sx, sy, sz = p.size
    for q, (ox, oz) in PIECES.items():
        st = M.Structure((64, sy, 64))
        for x in range(64):
            for y in range(sy):
                for z in range(64):
                    e = p.st.get(ox + x, y, oz + z)
                    if e is None:
                        st.set(x, y, z, AIR, {})
                    else:
                        # 10-05 15:2x: e is the palette tuple (name, states, VERSION) — e[2] is the block version (an int), and
                        # passing it as `waterlogged` waterlogged EVERY cell of the pieces (layer1 = water source): every pane,
                        # door, ladder, roof wedge and slab became a spring. The cause of 18 "flooded palace" gate runs.
                        st.set(x, y, z, e[0], e[1], False)
        ents = []
        for e in p.st.entities:
            pos = [c.value for c in e.value["Pos"].value]
            if ox <= pos[0] < ox + 64 and oz <= pos[2] < oz + 64:
                ee = M.copy.deepcopy(e) if hasattr(M, "copy") else __import__("copy").deepcopy(e)
                ee.value["Pos"] = M.lst(M.FLOAT, [M.f(pos[0] - ox), M.f(pos[1]), M.f(pos[2] - oz)])
                ents.append(ee)
        st.entities = ents
        marks = [dict(m, cell=[m["cell"][0] - ox, m["cell"][1], m["cell"][2] - oz]) for m in p.markers if ox <= m["cell"][0] < ox + 64 and oz <= m["cell"][2] < oz + 64]
        out[q] = (st, marks)
    return out


def write_pieces(p, pieces):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "manifests").mkdir(exist_ok=True); (OUT / "structures").mkdir(exist_ok=True)
    for q, (st, marks) in pieces.items():
        stem = f"mvv_palace_{q}_a_r1"
        (OUT / "structures" / f"{stem}.mcstructure").write_bytes(st.to_bytes())
        sx, sy, sz = st.size
        blocks = []
        for x in range(sx):
            for y in range(sy):
                for z in range(sz):
                    e = st.get(x, y, z)
                    if e is not None and e[0] != AIR:
                        blocks.append([x, y, z, e[0], {k: v.value for k, v in e[1].items()}])
        man = {"name": f"pw:{stem}", "size": [sx, sy, sz], "datum_y": 15, "blocks": blocks, "entities": marks}
        (OUT / "manifests" / f"{stem}.json").write_text(json.dumps(man, separators=(",", ":")))
        print(f"  {stem}: {len(blocks)} blocks, {len(marks)} markers")


# ---------------------------------------------------------------- renders (plans per storey, the south elevation, sections)
COL = {
    STONE: (150, 150, 155), SMOOTH: (190, 190, 190), CHISEL: (120, 120, 130), COBBLE: (120, 115, 110), DIRT: (110, 80, 50),
    PANEL: (160, 120, 70), FLOOR: (200, 160, 100), ATTIC_FLOOR: (170, 130, 80), STATE_FLOOR: (175, 175, 180), POST: (100, 70, 40),
    GLASS: (160, 220, 255), LIGHT: (255, 255, 200), GRASS: (90, 150, 70), PATH: (170, 150, 90), GRAVEL: (150, 150, 140), WATER: (60, 110, 200),
    "minecraft:spruce_door": (230, 60, 60), "minecraft:iron_door": (90, 90, 120), "minecraft:warped_door": (40, 170, 160), JIB_PANEL: (255, 120, 0),
    SECRET_PAINTING: (255, 0, 200), "minecraft:bed": (220, 100, 160), "minecraft:lectern": (240, 200, 60), "minecraft:chest": (200, 150, 60),
    "minecraft:barrel": (150, 110, 60), "minecraft:iron_bars": (90, 90, 90), "minecraft:bookshelf": (120, 80, 40), "minecraft:gold_block": (255, 215, 0),
    "minecraft:spruce_stairs": (190, 140, 80), "minecraft:stone_brick_stairs": (165, 165, 170), "minecraft:spruce_fence": (140, 100, 60),
    "minecraft:lantern": (255, 230, 120), "minecraft:bell": (240, 190, 40), "minecraft:stone_button": (200, 200, 200), "minecraft:green_wool": (40, 150, 40),
    "minecraft:red_carpet": (190, 40, 40), "minecraft:white_wool": (240, 240, 240), "minecraft:black_wool": (30, 30, 30), "minecraft:cauldron": (70, 70, 80),
}


def colour(name):
    if name in COL:
        return COL[name]
    if name.startswith("pw:roof"):
        return (110, 60, 50)
    if name.startswith("pw:furn"):
        return (120, 90, 60)
    if "hearth" in name or "flue" in name:
        return (90, 60, 50)
    if name in (AIR, VOID):
        return None
    return (200, 120, 200)


def render(p):
    from PIL import Image, ImageDraw
    DOCS.mkdir(parents=True, exist_ok=True)
    S = 6
    sx, sy, sz = p.size

    def plan(feet, title):
        # a storey plan: for each (x, z) the block at `feet` (walls / furniture), else the floor below (feet - 1) dimmed
        img = Image.new("RGB", (sz * S, sx * S), (20, 20, 25))
        d = ImageDraw.Draw(img)
        for x in range(sx):
            for z in range(sz):
                e = p.st.get(x, p.y(feet), z); c = colour(e[0]) if e else None
                if c is None:
                    e2 = p.st.get(x, p.y(feet - 1), z); c2 = colour(e2[0]) if e2 else None
                    c = tuple(int(v * 0.55) for v in c2) if c2 else (20, 20, 25)
                # north (z = 0) at the LEFT of the picture? No: draw z across (left -> right) and x down (street at the top)
                d.rectangle([z * S, x * S, z * S + S - 1, x * S + S - 1], fill=c)
        d.text((4, 4), f"{title} — feet {feet}: street side at the TOP (x = 0), z 0..127 left to right", fill=(255, 255, 255))
        for xx in (GATE[1], COURT[1], CORPS[1], ALLEY[1]):
            d.line([(0, (xx + 1) * S), (sz * S, (xx + 1) * S)], fill=(255, 255, 255), width=1)
        d.line([(64 * S, 0), (64 * S, sx * S)], fill=(255, 255, 255), width=1)
        return img

    plans = [plan(0, "GROUND FLOOR"), plan(F_NOBLE, "ÉTAGE NOBLE"), plan(F_ATTIC, "ATTIC"), plan(-4, "CELLS (below the gatehouse)")]
    for i, im in enumerate(plans):
        im.save(DOCS / f"palace-plan-{i}.png")
    # the south elevation: looking at the street front (x = 0 side): for each (z, feet) the first block from x = 0 inward
    H = TOP + 16
    el = Image.new("RGB", (sz * S, H * S), (120, 170, 230))
    d = ImageDraw.Draw(el)
    for z in range(sz):
        for feet in range(-15, TOP + 1):
            for x in range(sx):
                e = p.st.get(x, p.y(feet), z)
                c = colour(e[0]) if e else None
                if c is not None:
                    shade = max(0.45, 1 - x / 100)
                    d.rectangle([z * S, (TOP - feet) * S, z * S + S - 1, (TOP - feet) * S + S - 1], fill=tuple(int(v * shade) for v in c))
                    break
    d.text((4, 4), "SOUTH ELEVATION (from the street): gate range + gatehouse in front, the wings and the corps behind", fill=(0, 0, 0))
    el.save(DOCS / "palace-elevation-south.png")
    # a cross-section at z = 70 (through the gatehouse's east bay, the court, the great hall and the hidden corridor)
    def section(zc, title, fname):
        im = Image.new("RGB", (sx * S, H * S), (120, 170, 230))
        d = ImageDraw.Draw(im)
        for x in range(sx):
            for feet in range(-15, TOP + 1):
                e = p.st.get(x, p.y(feet), zc)
                c = colour(e[0]) if e else None
                if c is not None:
                    d.rectangle([x * S, (TOP - feet) * S, x * S + S - 1, (TOP - feet) * S + S - 1], fill=c)
        d.text((4, 4), f"{title}: street at the LEFT (x = 0) -> service court at the right; feet 0 = the court", fill=(0, 0, 0))
        im.save(DOCS / fname)
    section(70, "SECTION at z 70 (gatehouse east bay, court, great hall, hidden corridor, alley, service court)", "palace-section-z70.png")
    section(108, "SECTION at z 108 (east wing's outer rooms, the audience chamber, the attic)", "palace-section-z108.png")
    section(16, "SECTION at z 16 (west wing corridor line: prison tower, chancery, back stair)", "palace-section-z16.png")
    print("renders in", DOCS)


if __name__ == "__main__":
    p = build()
    print("model", p.size, "lights", p.lights, "beds", p.beds, "markers", len(p.markers))
    for n in p.notes:
        print("  -", n)
    if "--render" in sys.argv or True:
        render(p)
    if "--write" in sys.argv:
        pieces = cut(p)
        write_pieces(p, pieces)
