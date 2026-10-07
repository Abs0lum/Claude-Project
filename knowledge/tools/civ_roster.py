#!/usr/bin/env python3
"""civ_roster.py — CIVITAS phase D: the MINIMUM VILLAGE roster, every building generated from one shell recipe
(tools/civgen.Building, the cottage r1 section law) with its own plan, stations and zones. His rulings: +1 rule,
ladder hatch, canonical palette, "every building slightly different from the last, in layout AND in how fancy",
stations/zones/datum by me (CT1 = d), sparse decor for the minimum village (CT2 = a). Roofs: gable (ridge along the
depth) or hipped (the #174 hips: state = the corner it sits at, n NW / w SW / s SE / e NE; pyramidion for a square).
Roster (pw:mvv_<type>_<variant>_r1):
  cottage_s / cottage_m / cottage_l   homes (S = the r1 pilot, M wider with a hip roof, L two rooms + stable)
  bakery   hearth + 2 furnaces (ovens), counter, store         butcher  smoker, prep table, hooks (chains), store
  smithy   anvil, blast furnace, grindstone, forge hearth, yard   inn    2 storeys: bar counter, 3 tables, 4 beds up
  town_hall  hall with lectern desk, bell post, notice board, benches, records store
  farm_wheat  shed + fenced field (farmland, water, composter)   farm_cattle  barn + fenced pen (hay, trough)
  lumberyard  open shed, log racks, sawbench (stonecutter stand-in), yard   quarry  stepped stone pit, ladders, shed
  well        stone well with a roof, commons zone
Output: _staging/civ/structures/pw/<name>.mcstructure + manifests; a REPORT.json with stations/zones per building."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import civgen as G  # noqa: E402

OUT = Path("/home/claude/_staging/civ")
DOOR = ("minecraft:wooden_door", "minecraft:spruce_door")
HIP = {"NW": "north", "SW": "west", "SE": "south", "NE": "east"}


# ------------------------------------------------------------------------------------------------ the shell recipe
def section(b, X, W, basement=True, bz1=None):
    """ground below everything (r0 section): dirt, smooth-stone foundation, basement shell + manhole/shaft/sewer.
    bz1: the basement (and the house floor) ends at this z (default W): a lean-to beyond it has no cellar."""
    xf, xb, zl, zr = 0, X - 1, 1, (W if bz1 is None else bz1)
    b.fill(0, -15, 0, X - 1, -14, W, "minecraft:dirt")
    b.fill(0, -13, 0, X - 1, -12, W, "minecraft:smooth_stone")
    b.fill(0, -11, 0, X - 1, -7, W, "minecraft:dirt")
    b.fill(0, -6, 0, X - 1, -1, 0, "minecraft:dirt")
    if basement:
        b.fill(xf, -6, zl, xb, -6, zr, "minecraft:stone_bricks")
        b.fill(xf, -5, zl, xb, -2, zr, "minecraft:stone_bricks")
        b.fill(xf + 1, -5, zl + 1, xb - 1, -2, zr - 1, "minecraft:air")
        zm = 1 + W // 2 - 1
        b.put(xf + 1, -6, zm, "pw:manhole_cover", **{"pw:phase": 0, "pw:skin": 0})
        for f in range(-12, -6):
            b.put(xf + 1, f, zm, "minecraft:ladder", facing_direction=4)
        b.put(xf, -10, zm, "minecraft:air")
        b.put(xf, -9, zm, "minecraft:air")
        b.marker("port", "sewer", xf, -10, zm)
    else:
        b.fill(xf, -6, zl, xb, -2, zr, "minecraft:dirt")
    b.fill(xf, -1, zl, xb, -1, W, "minecraft:cobblestone")
    b.fill(xf + 1, -1, zl + 1, xb - 1, -1, zr - 1, "minecraft:oak_planks" if basement else "minecraft:cobblestone")
    if zr < W:                                       # beyond the basement: solid ground under the lean-to
        b.fill(xf, -6, zr + 1, xb, -2, W, "minecraft:dirt")
    b.fill(0, -1, 0, X - 1, -1, 0, "minecraft:grass_block")


def walls(b, X, W, eave, wall="minecraft:oak_planks", post="minecraft:spruce_log", x0=0, x1=None, z0=1, z1=None):
    x1 = X - 1 if x1 is None else x1
    z1 = W if z1 is None else z1
    for f in range(0, eave):
        for x in range(x0, x1 + 1):
            b.put(x, f, z0, wall); b.put(x, f, z1, wall)
        for z in range(z0, z1 + 1):
            b.put(x0, f, z, wall); b.put(x1, f, z, wall)
        for (x, z) in [(x0, z0), (x0, z1), (x1, z0), (x1, z1)]:
            b.put(x, f, z, post, pillar_axis="y")
    b.fill(x0 + 1, 0, z0 + 1, x1 - 1, eave - 1, z1 - 1, "minecraft:air")


def gable_roof(b, X, W, eave, roof="pw:roof45_spruce", gable="minecraft:oak_planks", x0=0, x1=None, z0=1, z1=None):
    """ridge along the depth (x); slope rows step up one per cell from each side wall. Returns the top feet level."""
    x1 = X - 1 if x1 is None else x1
    z1 = W if z1 is None else z1
    w = z1 - z0 + 1
    half = w // 2
    for k in range(half):
        f = eave + k
        for x in range(x0, x1 + 1):
            b.put(x, f, z0 + k, roof, **{"minecraft:cardinal_direction": "north", "minecraft:vertical_half": "bottom"})
            b.put(x, f, z1 - k, roof, **{"minecraft:cardinal_direction": "south", "minecraft:vertical_half": "bottom"})
        for z in range(z0 + k + 1, z1 - k):
            for x in (x0, x1):
                b.put(x, f, z, gable)
            for x in range(x0 + 1, x1):
                b.put(x, f, z, "minecraft:air")
    if w % 2 == 1:                                   # odd width: a ridge cap row on top
        f = eave + half
        for x in range(x0, x1 + 1):
            b.put(x, f, z0 + half, roof.replace("roof45", "roof45_ridge"), **{"minecraft:cardinal_direction": "north"})
    return eave + half


def hip_roof(b, X, W, eave, mat="spruce", x0=0, x1=None, z0=1, z1=None):
    """rings of roof45 with #174 hips at the corners, climbing until the ring is 1 wide (ridge) or 1x1 (pyramidion)."""
    x1 = X - 1 if x1 is None else x1
    z1 = W if z1 is None else z1
    r45, hip, ridge, cap, rend = (f"pw:roof45_{mat}", f"pw:roof_hip_{mat}", f"pw:roof45_ridge_{mat}",
                                  f"pw:roof_pyramidion_{mat}", f"pw:roof_ridge_end_{mat}")
    k, f = 0, eave
    while True:
        xa, xb_, za, zb = x0 + k, x1 - k, z0 + k, z1 - k
        if xa > xb_ or za > zb:
            break
        if xa == xb_ and za == zb:
            b.put(xa, f, za, cap, **{"minecraft:cardinal_direction": "north", "minecraft:vertical_half": "bottom"})
            break
        if za == zb:                                 # a ridge along x with hipped ends
            for x in range(xa, xb_ + 1):
                if x == xa:
                    b.put(x, f, za, rend, **{"minecraft:cardinal_direction": "west", "minecraft:vertical_half": "bottom"})
                elif x == xb_:
                    b.put(x, f, za, rend, **{"minecraft:cardinal_direction": "east", "minecraft:vertical_half": "bottom"})
                else:
                    b.put(x, f, za, ridge, **{"minecraft:cardinal_direction": "north"})
            break
        if xa == xb_:                                # a ridge along z
            for z in range(za, zb + 1):
                if z == za:
                    b.put(xa, f, z, rend, **{"minecraft:cardinal_direction": "north", "minecraft:vertical_half": "bottom"})
                elif z == zb:
                    b.put(xa, f, z, rend, **{"minecraft:cardinal_direction": "south", "minecraft:vertical_half": "bottom"})
                else:
                    b.put(xa, f, z, ridge, **{"minecraft:cardinal_direction": "west"})
            break
        for x in range(xa + 1, xb_):
            b.put(x, f, za, r45, **{"minecraft:cardinal_direction": "north", "minecraft:vertical_half": "bottom"})
            b.put(x, f, zb, r45, **{"minecraft:cardinal_direction": "south", "minecraft:vertical_half": "bottom"})
        for z in range(za + 1, zb):
            b.put(xa, f, z, r45, **{"minecraft:cardinal_direction": "west", "minecraft:vertical_half": "bottom"})
            b.put(xb_, f, z, r45, **{"minecraft:cardinal_direction": "east", "minecraft:vertical_half": "bottom"})
        b.put(xa, f, za, hip, **{"minecraft:cardinal_direction": HIP["NW"], "minecraft:vertical_half": "bottom"})
        b.put(xa, f, zb, hip, **{"minecraft:cardinal_direction": HIP["SW"], "minecraft:vertical_half": "bottom"})
        b.put(xb_, f, zb, hip, **{"minecraft:cardinal_direction": HIP["SE"], "minecraft:vertical_half": "bottom"})
        b.put(xb_, f, za, hip, **{"minecraft:cardinal_direction": HIP["NE"], "minecraft:vertical_half": "bottom"})
        for x in range(xa + 1, xb_):
            for z in range(za + 1, zb):
                b.put(x, f, z, "minecraft:air")
        k += 1
        f += 1
    return f


def door(b, x, f, z, facing, wood="wooden"):
    name = "minecraft:wooden_door" if wood == "wooden" else f"minecraft:{wood}_door"
    b.put(x, f, z, name, door_hinge_bit=False, open_bit=False, upper_block_bit=False, **{"minecraft:cardinal_direction": facing})
    b.put(x, f + 1, z, name, door_hinge_bit=False, open_bit=False, upper_block_bit=True, **{"minecraft:cardinal_direction": facing})


def lights(b, cells):
    for (x, f, z) in cells:
        if b.get(x, f, z) == "minecraft:air":
            b.put(x, f, z, "minecraft:light_block_14")


SUPPORT = {2: (0, 1), 3: (0, -1), 4: (1, 0), 5: (-1, 0)}       # ladder facing_direction -> the cell it hangs on


def secure_ladders(b):
    """BDS law (civtest 20:30): a ladder whose support cell is a glass pane / air is not kept. Put the wall material back."""
    sx, sy, sz = b.size
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                p = b.st.get(x, y, z)
                if p and p[0] == "minecraft:ladder":
                    fd = p[1]["facing_direction"].value
                    dx, dz = SUPPORT[fd]
                    q = b.st.get(x + dx, y, z + dz)
                    if q is None or q[0] in ("minecraft:glass_pane", "minecraft:air"):
                        wall = next((r[0] for r in (b.st.get(x + dx, y - 1, z + dz), b.st.get(x + dx, y + 1, z + dz))
                                     if r and r[0].endswith(("_planks", "stone_bricks", "cobblestone"))), "minecraft:oak_planks")
                        b.st.set(x + dx, y, z + dz, wall, {})


_close = G.Building.close_air


def _close_secure(self):
    secure_ladders(self)
    _close(self)


G.Building.close_air = _close_secure


def new(name, X, W, top):
    return G.Building(name, X, W, top_feet=top)


# ------------------------------------------------------------------------------------------------ buildings
def cottage_m(name="pw:mvv_cottage_m_a_r1"):
    """Cottage M: 8 deep x 8 wide, hipped roof, hearth on the back wall, bed alcove downstairs, loft store."""
    X, W, eave = 8, 8, 5
    b = new(name, X, W, eave + 5)
    section(b, X, W)
    walls(b, X, W, eave)
    b.fill(1, 3, 2, X - 2, 3, W - 1, "minecraft:oak_planks")          # loft floor
    top = hip_roof(b, X, W, eave)
    zm = 4
    door(b, 0, 0, zm, "south")
    for (x, z) in [(2, 1), (5, 1), (2, W), (5, W), (X - 1, 2), (X - 1, 6)]:
        b.put(x, 1, z, "minecraft:glass_pane")
    hx, hz = X - 1, 5
    b.put(hx, 0, hz, "pw:hearth_oak_planks", **{"minecraft:cardinal_direction": "west", "pw:phase": "cold"})
    for f in range(1, top):
        b.put(hx, f, hz, "pw:flue_oak_planks", **{"pw:cap": False})
    b.put(hx, top, hz, "pw:flue_oak_planks", **{"pw:cap": True})
    b.put(hx - 1, 1, hz, "pw:furn_mantel_oak", **{"minecraft:cardinal_direction": "west"})
    tx, tz = 3, 3
    b.put(tx, 0, tz, "pw:furn_table_oak", **{"pw:n": False, "pw:e": True, "pw:s": False, "pw:w": False})
    b.put(tx + 1, 0, tz, "pw:furn_table_oak", **{"pw:n": False, "pw:e": False, "pw:s": False, "pw:w": True})
    b.put(tx, 0, tz - 1, "pw:furn_chair_oak", **{"minecraft:cardinal_direction": "south"})
    b.put(tx + 1, 0, tz + 1, "pw:furn_chair_oak", **{"minecraft:cardinal_direction": "north"})
    b.put(1, 0, W - 1, "pw:furn_cupboard_oak", **{"minecraft:cardinal_direction": "east"})
    b.put(1, 0, 2, "pw:furn_dresser_oak", **{"minecraft:cardinal_direction": "east"})
    b.put(X - 2, 0, 2, "minecraft:bed", direction=2, head_piece_bit=True, occupied_bit=False)      # bed alcove
    b.put(X - 2, 0, 3, "minecraft:bed", direction=2, head_piece_bit=False, occupied_bit=False)
    b.put(hx - 2, 0, hz + 1, "pw:furn_stool_oak", **{"minecraft:cardinal_direction": "west"})
    lx, lz = X - 2, W - 2                                                 # loft ladder (not under a zone corner)
    for f in range(0, 4):
        b.put(lx, f, lz, "minecraft:ladder", facing_direction=4)
    cx, cz = 1, W - 2                                                     # cellar ladder + hatch
    for f in range(-5, 0):
        b.put(cx, f, cz, "minecraft:ladder", facing_direction=5)
    b.hatch(cx, -1, cz, ladder_facing=5)
    b.put(3, 4, 3, "minecraft:chest", **{"minecraft:cardinal_direction": "south"})
    b.put(4, 4, 3, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(2, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(2, -5, W - 1, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    lights(b, [(3, 2, 4), (X - 3, 2, 4), (3, -2, 4), (3, 5, 4)])
    b.marker("datum", "datum", 0, 0, zm, n=0)
    b.marker("station", "door", 0, 0, zm)
    b.marker("station", "hearth", hx, 0, hz)
    b.marker("station", "table", tx, 0, tz)
    b.marker("station", "seat", tx, 0, tz - 1)
    b.marker("station", "seat", tx + 1, 0, tz + 1)
    b.marker("station", "seat", hx - 2, 0, hz + 1)
    b.marker("station", "store", 1, 0, W - 1)
    b.marker("station", "store", 1, 0, 2)
    b.marker("station", "store", 3, 4, 3)
    b.marker("station", "bed", X - 2, 0, 2)
    b.zone("threshold", 1, 0, zm, 2, zm + 1)
    b.zone("kitchen", 1, 0, 2, X - 2, W - 1)
    b.zone("cellar", 1, -5, 2, X - 2, W - 1)
    b.zone("storeroom", 1, 4, 2, X - 2, W - 1)
    b.close_air()
    return b


def cottage_l(name="pw:mvv_cottage_l_a_r1"):
    """Cottage L: 10 deep x 7 wide gable house + a 4-wide lean-to stable on the right (south) side; two rooms."""
    X, W, eave = 10, 11, 5
    b = new(name, X, W, eave + 4)
    section(b, X, W, bz1=7)
    walls(b, X, W, eave, x0=0, x1=X - 1, z0=1, z1=7)                     # the house 7 wide (z 1..7)
    b.fill(1, 3, 2, X - 2, 3, 6, "minecraft:oak_planks")
    top = gable_roof(b, X, W, eave, x0=0, x1=X - 1, z0=1, z1=7)
    # lean-to stable z 8..11: fence walls, a plank roof sloping down to the south (roof45 south at eave-1)
    b.fill(0, -1, 8, X - 1, -1, 11, "minecraft:cobblestone")             # the stable floor at grade (feet -1), not a step up
    b.fill(1, -1, 8, X - 2, -1, 10, "minecraft:coarse_dirt")
    for x in range(0, X):
        for f in range(0, 3):
            b.put(x, f, 11, "minecraft:oak_fence")
    for z in range(8, 12):
        for f in range(0, 3):
            b.put(0, f, z, "minecraft:oak_fence"); b.put(X - 1, f, z, "minecraft:oak_fence")
    for (x, z) in [(0, 8), (0, 11), (X - 1, 8), (X - 1, 11)]:
        for f in range(0, 4):
            b.put(x, f, z, "minecraft:spruce_log", pillar_axis="y")
    for k, z in enumerate((8, 9, 10, 11)):
        for x in range(0, X):
            b.put(x, 4 - k, z, "pw:roof45_spruce", **{"minecraft:cardinal_direction": "south", "minecraft:vertical_half": "bottom"})
    b.put(0, 0, 9, "minecraft:fence_gate", open_bit=False, in_wall_bit=False, **{"minecraft:cardinal_direction": "east"})
    b.put(0, 1, 9, "minecraft:air")
    b.put(X - 3, 0, 9, "minecraft:hay_block", pillar_axis="y")
    b.put(X - 2, 0, 10, "minecraft:hay_block", pillar_axis="y")
    # house interior: hall (front) + chamber (back) split by a plank wall at x = 5
    for z in range(2, 7):
        for f in range(0, 3):
            b.put(5, f, z, "minecraft:oak_planks")
    door(b, 5, 0, 4, "east", wood="spruce")                                # the chamber door in the partition
    zm = 4
    door(b, 0, 0, zm, "south", wood="spruce")
    for (x, z) in [(2, 1), (7, 1), (3, 7), (8, 7), (X - 1, 3), (X - 1, 5)]:
        b.put(x, 1, z, "minecraft:glass_pane")
    hx, hz = 3, 1
    b.put(hx, 0, hz, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": "south", "pw:phase": "cold"})
    for f in range(1, top + 1):
        b.put(hx, f, hz, "pw:flue_stone_bricks", **{"pw:cap": False})
    b.put(hx, top + 1, hz, "pw:flue_stone_bricks", **{"pw:cap": True})
    b.put(hx, 1, hz + 1, "pw:furn_mantel_spruce", **{"minecraft:cardinal_direction": "south"})
    b.put(2, 0, 5, "pw:furn_table_spruce", **{"pw:n": False, "pw:e": False, "pw:s": False, "pw:w": False})
    b.put(2, 0, 6, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "north"})
    b.put(2, 0, 4, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "south"})
    b.put(4, 0, 6, "pw:furn_cupboard_spruce", **{"minecraft:cardinal_direction": "north"})
    b.put(1, 1, 2, "pw:furn_coat_pegs_spruce", **{"minecraft:cardinal_direction": "east"})
    b.put(7, 0, 2, "minecraft:bed", direction=0, head_piece_bit=False, occupied_bit=False)
    b.put(7, 0, 3, "minecraft:bed", direction=0, head_piece_bit=True, occupied_bit=False)
    b.put(8, 0, 6, "pw:furn_dresser_spruce", **{"minecraft:cardinal_direction": "north"})
    b.put(7, 0, 6, "pw:furn_chair_spruce", **{"minecraft:cardinal_direction": "north"})
    lx, lz = X - 2, 3                                                     # loft ladder (not under a zone corner)
    for f in range(0, 4):
        b.put(lx, f, lz, "minecraft:ladder", facing_direction=4)
    cx, cz = 3, 6                                                         # cellar ladder (not under a zone corner)
    for f in range(-5, 0):
        b.put(cx, f, cz, "minecraft:ladder", facing_direction=2)
    b.hatch(cx, -1, cz, ladder_facing=2)
    b.put(2, 4, 3, "minecraft:bed", direction=2, head_piece_bit=True, occupied_bit=False)
    b.put(2, 4, 4, "minecraft:bed", direction=2, head_piece_bit=False, occupied_bit=False)
    b.put(6, 4, 5, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    b.put(2, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(3, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(2, -5, 6, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    lights(b, [(3, 2, 4), (7, 2, 4), (3, -2, 4), (4, 5, 4), (5, 2, 9)])
    b.marker("datum", "datum", 0, 0, zm, n=0)
    b.marker("station", "door", 0, 0, zm)
    b.marker("station", "hearth", hx, 0, hz)
    b.marker("station", "table", 2, 0, 5)
    b.marker("station", "seat", 2, 0, 6)
    b.marker("station", "seat", 2, 0, 4)
    b.marker("station", "seat", 7, 0, 6)
    b.marker("station", "store", 4, 0, 6)
    b.marker("station", "store", 8, 0, 6)
    b.marker("station", "store", 2, -5, 6)
    b.marker("station", "store", 2, -5, 2)
    b.marker("station", "store", 6, 4, 5)
    b.marker("station", "bed", 7, 0, 3)
    b.marker("station", "bed", 2, 4, 3)
    b.marker("station", "pen", X - 3, 0, 9)
    b.zone("threshold", 1, 0, zm, 2, zm + 1)
    b.zone("kitchen", 1, 0, 2, 4, 6)
    b.zone("chamber", 6, 0, 2, X - 2, 6)
    b.zone("cellar", 1, -5, 2, X - 2, 6)
    b.zone("quarters", 1, 4, 2, X - 2, 6)
    b.zone("stable", 1, 0, 8, X - 2, 10)
    b.close_air()
    return b


def bakery(name="pw:mvv_bakery_a_r1"):
    X, W, eave = 9, 8, 5
    b = new(name, X, W, eave + 5)
    section(b, X, W)
    walls(b, X, W, eave)
    b.fill(1, 3, 2, X - 2, 3, W - 1, "minecraft:oak_planks")
    top = hip_roof(b, X, W, eave)
    zm = 3
    door(b, 0, 0, zm, "south")
    for (x, z) in [(3, 1), (6, 1), (3, W), (6, W), (0, 6), (0, 7)]:
        b.put(x, 1, z, "minecraft:glass_pane")
    # ovens on the back wall: two furnaces flanking the hearth, flue up
    hx, hz = X - 1, 4
    b.put(hx, 0, hz, "pw:hearth_brick", **{"minecraft:cardinal_direction": "west", "pw:phase": "cold"})
    for f in range(1, top):
        b.put(hx, f, hz, "pw:flue_brick", **{"pw:cap": False})
    b.put(hx, top, hz, "pw:flue_brick", **{"pw:cap": True})
    b.put(X - 2, 0, 2, "minecraft:furnace", **{"minecraft:cardinal_direction": "west"})
    b.put(X - 2, 0, 6, "minecraft:furnace", **{"minecraft:cardinal_direction": "west"})
    # (no masonry blocks beside the ovens: they stood inside the workfloor ring as obstructions)
    # counter across the shop front (x = 3), a gap at the door column
    for z in range(2, W):
        if z != zm:
            b.put(3, 0, z, "pw:furn_shelf_oak", **{"minecraft:cardinal_direction": "west"})
    b.put(5, 0, 2, "pw:furn_trestle_oak", **{"minecraft:cardinal_direction": "north"})      # prep table
    b.put(1, 0, W - 1, "minecraft:barrel", facing_direction=1, open_bit=False)              # flour
    b.put(2, 0, W - 1, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(1, 0, 2, "pw:furn_stool_oak", **{"minecraft:cardinal_direction": "east"})
    cx, cz = 5, W - 1                                                     # cellar ladder (not under a zone corner)
    for f in range(-5, 0):
        b.put(cx, f, cz, "minecraft:ladder", facing_direction=2)
    b.hatch(cx, -1, cz, ladder_facing=2)
    lx, lz = 1, 4
    for f in range(0, 4):
        b.put(lx, f, lz, "minecraft:ladder", facing_direction=5)
    b.put(4, 4, 3, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False)
    b.put(5, 4, 3, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
    b.put(4, 4, 6, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    b.put(2, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(3, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(2, -5, W - 1, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    lights(b, [(2, 2, 4), (6, 2, 4), (4, -2, 4), (4, 5, 4)])
    b.marker("datum", "datum", 0, 0, zm, n=0)
    b.marker("station", "door", 0, 0, zm)
    b.marker("station", "oven", X - 2, 0, 2)
    b.marker("station", "oven", X - 2, 0, 6)
    b.marker("station", "hearth", hx, 0, hz)
    b.marker("station", "prep", 5, 0, 2)
    b.marker("station", "counter", 3, 0, 2)
    b.marker("station", "counter", 3, 0, 5)
    b.marker("station", "seat", 1, 0, 2)
    b.marker("station", "store", 1, 0, W - 1)
    b.marker("station", "store", 2, -5, W - 1)
    b.marker("station", "store", 2, -5, 2)
    b.marker("station", "store", 4, 4, 6)
    b.marker("station", "bed", 4, 4, 3)
    b.zone("threshold", 1, 0, zm, 2, zm + 1)
    b.zone("shopfloor", 1, 0, 2, 2, W - 1)
    b.zone("workfloor", 3, 0, 2, X - 2, W - 1)                            # the counter line belongs to the staff side
    b.zone("cellar", 1, -5, 2, X - 2, W - 1)
    b.zone("quarters", 1, 4, 2, X - 2, W - 1)
    b.close_air()
    return b


def butcher(name="pw:mvv_butcher_a_r1"):
    X, W, eave = 8, 7, 4
    b = new(name, X, W, eave + 4)
    section(b, X, W)
    walls(b, X, W, eave, wall="minecraft:spruce_planks", post="minecraft:oak_log")
    b.fill(1, 3, 2, X - 2, 3, W - 1, "minecraft:spruce_planks")
    top = gable_roof(b, X, W, eave, roof="pw:roof45_oak", gable="minecraft:spruce_planks")
    zm = 3
    door(b, 0, 0, zm, "south", wood="spruce")
    for (x, z) in [(3, 1), (3, W), (0, 5), (X - 1, 4)]:
        b.put(x, 1, z, "minecraft:glass_pane")
    b.put(X - 2, 0, 2, "minecraft:smoker", **{"minecraft:cardinal_direction": "west"})
    b.put(X - 2, 0, 3, "minecraft:smoker", **{"minecraft:cardinal_direction": "west"})
    b.put(4, 0, 4, "pw:furn_trestle_spruce", **{"minecraft:cardinal_direction": "north"})       # cutting block
    b.put(4, 0, 5, "pw:furn_trestle_spruce", **{"minecraft:cardinal_direction": "north"})
    for z in (2, 3, 4, 5):                                                                    # hooks: chains from the loft beam
        b.put(5, 2, z, "minecraft:iron_chain", pillar_axis="y")
    for z in range(2, W):
        if z != zm:
            b.put(3, 0, z, "pw:furn_shelf_spruce", **{"minecraft:cardinal_direction": "west"})  # counter
    b.put(X - 2, 0, W - 1, "minecraft:barrel", facing_direction=1, open_bit=False)              # salt
    b.put(X - 2, 0, W - 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    cx, cz = 1, W - 2                                                     # cellar ladder (not under a zone corner)
    for f in range(-5, 0):
        b.put(cx, f, cz, "minecraft:ladder", facing_direction=5)
    b.hatch(cx, -1, cz, ladder_facing=5)
    lx, lz = X - 2, 4
    for f in range(0, 4):
        b.put(lx, f, lz, "minecraft:ladder", facing_direction=4)
    b.put(2, 4, 3, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False)
    b.put(3, 4, 3, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
    b.put(2, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)      # cold store
    b.put(3, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(2, -5, W - 1, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    lights(b, [(2, 2, 4), (5, 2, 5), (4, -2, 4), (4, 5, 4)])
    b.marker("datum", "datum", 0, 0, zm, n=0)
    b.marker("station", "door", 0, 0, zm)
    b.marker("station", "oven", X - 2, 0, 2)
    b.marker("station", "oven", X - 2, 0, 3)
    b.marker("station", "prep", 4, 0, 4)
    b.marker("station", "rack", 5, 0, 4)
    b.marker("station", "counter", 3, 0, 2)
    b.marker("station", "counter", 3, 0, 5)
    b.marker("station", "store", X - 2, 0, W - 1)
    b.marker("station", "store", 2, -5, 2)
    b.marker("station", "store", 2, -5, W - 1)
    b.marker("station", "bed", 2, 4, 3)
    b.zone("threshold", 1, 0, zm, 2, zm + 1)
    b.zone("shopfloor", 1, 0, 2, 2, W - 1)
    b.zone("workfloor", 3, 0, 2, X - 2, W - 1)
    b.zone("cellar", 1, -5, 2, X - 2, W - 1)
    b.zone("quarters", 1, 4, 2, X - 2, W - 1)
    b.close_air()
    return b


def smithy(name="pw:mvv_smithy_a_r1"):
    """forge hall (stone footing, open front bay) + a walled yard at the back with the quench trough."""
    X, W, eave = 10, 8, 5
    b = new(name, X, W, eave + 5)
    section(b, X, W, basement=False)
    walls(b, X, W, eave, x0=0, x1=6, wall="minecraft:stone_bricks", post="minecraft:spruce_log")
    top = hip_roof(b, 7, W, eave, mat="oak", x0=0, x1=6)
    # open front bay: a 3-wide arch instead of a door
    for z in (3, 4, 5):
        b.put(0, 0, z, "minecraft:air"); b.put(0, 1, z, "minecraft:air")
    b.put(0, 2, 4, "minecraft:spruce_log", pillar_axis="z")
    for (x, z) in [(3, 1), (3, W), (6, 3), (6, 5)]:
        b.put(x, 1, z, "minecraft:glass_pane")
    # forge: hearth + blast furnace + anvil + grindstone + water
    b.put(5, 0, 2, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": "south", "pw:phase": "cold"})
    b.put(5, 0, 1, "minecraft:stone_bricks")
    for f in range(1, top + 1):
        b.put(5, f, 1, "pw:flue_stone_bricks", **{"pw:cap": False})
    b.put(5, top + 1, 1, "pw:flue_stone_bricks", **{"pw:cap": True})
    b.put(4, 0, 2, "minecraft:blast_furnace", **{"minecraft:cardinal_direction": "south"})
    b.put(3, 0, 4, "minecraft:anvil", **{"minecraft:cardinal_direction": "north"})
    b.put(5, 0, 6, "minecraft:grindstone", attachment="standing", direction=2)
    b.put(2, 0, 6, "minecraft:cauldron", fill_level=6, cauldron_liquid="water")
    b.put(1, 0, 2, "pw:furn_shelf_oak", **{"minecraft:cardinal_direction": "east"})
    b.put(1, 0, 7, "minecraft:barrel", facing_direction=1, open_bit=False)
    # yard x 7..9: cobble floor, fence, trough, log pile
    b.fill(7, -1, 1, X - 1, -1, W, "minecraft:cobblestone")
    for z in range(1, W + 1):
        for f in range(0, 2):
            b.put(X - 1, f, z, "minecraft:stone_brick_wall")
    for x in (7, 8, 9):
        for f in range(0, 2):
            b.put(x, f, 1, "minecraft:stone_brick_wall"); b.put(x, f, W, "minecraft:stone_brick_wall")
    door(b, 6, 0, 4, "east")                                                                 # back door to the yard
    b.put(7, 0, 6, "minecraft:spruce_log", pillar_axis="x"); b.put(8, 0, 6, "minecraft:spruce_log", pillar_axis="x")
    b.put(7, 0, 7, "minecraft:cauldron", fill_level=6, cauldron_liquid="water")
    lights(b, [(3, 3, 4), (3, 3, 2)])
    b.marker("datum", "datum", 0, 0, 4, n=0)
    b.marker("station", "door", 0, 0, 4)
    b.marker("station", "hearth", 5, 0, 2)
    b.marker("station", "oven", 4, 0, 2)
    b.marker("station", "anvil", 3, 0, 4)
    b.marker("station", "bench", 5, 0, 6)
    b.marker("station", "counter", 1, 0, 2)
    b.marker("station", "store", 1, 0, 7)
    b.marker("station", "yard", 7, 0, 3)
    b.zone("threshold", 0, 0, 3, 1, 5)                                    # the open bay in the front wall + its approach
    b.zone("workfloor", 1, 0, 2, 5, W - 1)
    b.marker("station", "door", 6, 0, 4)
    b.zone("threshold", 7, 0, 3, 8, 5)                                    # outside the back door, in the yard
    b.zone("yard", 7, 0, 2, X - 2, W - 1)
    b.close_air()
    return b


def inn(name="pw:mvv_inn_a_r1"):
    """two storeys: taproom with bar + 3 tables below, 4 beds above, hipped roof, hearth."""
    X, W, eave = 11, 9, 8
    b = new(name, X, W, eave + 6)
    section(b, X, W)
    walls(b, X, W, eave)
    b.fill(1, 3, 2, X - 2, 3, W - 1, "minecraft:oak_planks")             # first floor course
    b.fill(1, 7, 2, X - 2, 7, W - 1, "minecraft:oak_planks")             # attic course
    top = hip_roof(b, X, W, eave)
    zm = 4
    door(b, 0, 0, zm, "south", wood="spruce")
    for (x, z) in [(2, 1), (5, 1), (8, 1), (2, W), (5, W), (8, W), (0, 2), (0, 7), (X - 1, 3), (X - 1, 6),
                   (3, 1), (7, 1), (3, W), (7, W), (0, 3), (0, 6)]:
        b.put(x, 1 if (x, z) in [(2, 1), (5, 1), (8, 1), (2, W), (5, W), (8, W), (0, 2), (0, 7), (X - 1, 3), (X - 1, 6)] else 5, z, "minecraft:glass_pane")
    hx, hz = X - 1, 7
    b.put(hx, 0, hz, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": "west", "pw:phase": "cold"})
    for f in range(1, top):
        b.put(hx, f, hz, "pw:flue_stone_bricks", **{"pw:cap": False})
    b.put(hx, top, hz, "pw:flue_stone_bricks", **{"pw:cap": True})
    b.put(hx - 1, 1, hz, "pw:furn_mantel_oak", **{"minecraft:cardinal_direction": "west"})
    # bar along the right (south) wall, x 2..7 at z = 7, keeper behind at z = 8
    for x in range(2, 8):
        b.put(x, 0, 7, "pw:furn_shelf_oak", **{"minecraft:cardinal_direction": "north"})
    b.put(1, 0, 8, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(8, 0, 8, "minecraft:barrel", facing_direction=1, open_bit=False)
    for i, (tx, tz) in enumerate([(2, 3), (5, 3), (8, 3)]):
        b.put(tx, 0, tz, "pw:furn_table_oak", **{"pw:n": False, "pw:e": False, "pw:s": False, "pw:w": False})
        b.put(tx, 0, tz - 1, "pw:furn_chair_oak", **{"minecraft:cardinal_direction": "south"})
        b.put(tx, 0, tz + 1, "pw:furn_chair_oak", **{"minecraft:cardinal_direction": "north"})
    b.put(hx - 1, 0, hz - 1, "pw:furn_bench_oak", **{"minecraft:cardinal_direction": "west"})
    # stair to the first floor (ladder + hatch), beds above
    lx, lz = X - 2, 3                                                     # stair ladder (not under a zone corner)
    for f in range(0, 4):
        b.put(lx, f, lz, "minecraft:ladder", facing_direction=4)
    for i, (bx, bz) in enumerate([(2, 2), (2, 7), (6, 2), (6, 7)]):
        b.put(bx, 4, bz, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False)
        b.put(bx + 1, 4, bz, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
        b.put(bx, 4, bz + (1 if bz == 2 else -1), "minecraft:chest", **{"minecraft:cardinal_direction": "east"})
    b.put(5, 4, 5, "pw:furn_table_oak", **{"pw:n": False, "pw:e": False, "pw:s": False, "pw:w": False})
    cx, cz = 1, 3                                                         # cellar ladder (not under a zone corner)
    for f in range(-5, 0):
        b.put(cx, f, cz, "minecraft:ladder", facing_direction=5)
    b.hatch(cx, -1, cz, ladder_facing=5)
    for x in (2, 3, 4, 5):
        b.put(x, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(2, -5, W - 1, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    lights(b, [(3, 2, 4), (8, 2, 4), (3, 6, 4), (8, 6, 4), (4, -2, 4), (5, 9, 4)])
    b.marker("datum", "datum", 0, 0, zm, n=0)
    b.marker("station", "door", 0, 0, zm)
    b.marker("station", "hearth", hx, 0, hz)
    b.marker("station", "counter", 4, 0, 7)
    b.marker("station", "seat", hx - 1, 0, hz - 1)
    for (tx, tz) in [(2, 3), (5, 3), (8, 3)]:
        b.marker("station", "table", tx, 0, tz)
        b.marker("station", "seat", tx, 0, tz - 1)
        b.marker("station", "seat", tx, 0, tz + 1)
    b.marker("station", "store", 1, 0, 8)
    b.marker("station", "store", 8, 0, 8)
    b.marker("station", "store", 3, -5, 2)
    b.marker("station", "store", 2, -5, W - 1)
    for (bx, bz) in [(2, 2), (2, 7), (6, 2), (6, 7)]:
        b.marker("station", "bed", bx, 4, bz)
    b.zone("threshold", 1, 0, zm, 2, zm + 1)
    b.zone("commons", 1, 0, 2, X - 2, 6)
    b.zone("shopfloor", 1, 0, 7, X - 2, W - 1)
    b.zone("cellar", 1, -5, 2, X - 2, W - 1)
    b.zone("quarters", 1, 4, 2, X - 2, W - 1)
    b.zone("storeroom", 1, 8, 2, X - 2, W - 1)
    b.close_air()
    return b


def town_hall(name="pw:mvv_town_hall_a_r1"):
    X, W, eave = 12, 9, 6
    b = new(name, X, W, eave + 5)
    section(b, X, W)
    walls(b, X, W, eave, wall="minecraft:stone_bricks", post="minecraft:spruce_log")
    top = gable_roof(b, X, W, eave, roof="pw:roof45_spruce", gable="minecraft:stone_bricks")
    zm = 5
    door(b, 0, 0, zm, "south", wood="spruce")
    door(b, 0, 0, zm - 1, "south", wood="spruce")                     # double door
    for (x, z) in [(3, 1), (6, 1), (9, 1), (3, W), (6, W), (9, W), (X - 1, 3), (X - 1, 7)]:
        b.put(x, 1, z, "minecraft:glass_pane"); b.put(x, 2, z, "minecraft:glass_pane")
    # dais at the back with the desk (lectern) and records chests; benches in rows
    b.fill(X - 3, 0, 3, X - 2, 0, 7, "minecraft:spruce_planks")
    b.put(X - 3, 1, 5, "minecraft:lectern", **{"minecraft:cardinal_direction": "west", "powered_bit": False})
    b.put(X - 2, 1, 3, "minecraft:chest", **{"minecraft:cardinal_direction": "west"})
    b.put(X - 2, 1, 7, "minecraft:chest", **{"minecraft:cardinal_direction": "west"})
    for x in (3, 5, 7):
        for z in (3, 7):
            b.put(x, 0, z, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "east"})
    b.put(1, 0, 2, "pw:furn_shelf_spruce", **{"minecraft:cardinal_direction": "south"})    # notice board stand
    b.put(1, 1, 2, "minecraft:wall_sign", facing_direction=3)
    b.put(1, 0, W - 1, "pw:furn_cupboard_spruce", **{"minecraft:cardinal_direction": "north"})
    # the bell on a post beside the door (outside, in the clearance column)
    # the hall bell stands on a stone-brick block inside, by the door (the clearance column z = 0 stays open, save-box law)
    b.put(2, 0, W - 1, "minecraft:stone_bricks"); b.put(2, 1, W - 1, "minecraft:bell", attachment="standing", direction=0, toggle_bit=False)
    hx, hz = 6, W
    b.put(hx, 0, hz, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": "north", "pw:phase": "cold"})
    for f in range(1, top + 1):
        b.put(hx, f, hz, "pw:flue_stone_bricks", **{"pw:cap": False})
    b.put(hx, top + 1, hz, "pw:flue_stone_bricks", **{"pw:cap": True})
    cx, cz = 1, 7                                                         # archive ladder (not under a zone corner)
    for f in range(-5, 0):
        b.put(cx, f, cz, "minecraft:ladder", facing_direction=5)
    b.hatch(cx, -1, cz, ladder_facing=5)
    for x in (2, 3, 4, 5, 6):
        b.put(x, -5, 2, "minecraft:chest", **{"minecraft:cardinal_direction": "south"})     # the archive
    lights(b, [(3, 4, 5), (8, 4, 5), (4, -2, 4)])
    b.marker("datum", "datum", 0, 0, zm, n=0)
    b.marker("station", "door", 0, 0, zm)
    b.marker("station", "desk", X - 3, 1, 5)
    b.marker("station", "post", 1, 0, 2)
    b.marker("station", "hearth", hx, 0, hz)
    for x in (3, 5, 7):
        for z in (3, 7):
            b.marker("station", "seat", x, 0, z)
    b.marker("station", "store", X - 2, 1, 3)
    b.marker("station", "store", X - 2, 1, 7)
    b.marker("station", "store", 1, 0, W - 1)
    b.marker("station", "store", 4, -5, 2)
    b.zone("threshold", 1, 0, zm - 1, 2, zm + 1)
    b.zone("commons", 1, 0, 2, X - 2, W - 1)
    b.zone("chamber", X - 3, 1, 3, X - 2, 7)                              # the dais: its floor is the raised planks
    b.zone("cellar", 1, -5, 2, X - 2, W - 1)
    b.close_air()
    return b


def farm_wheat(name="pw:mvv_farm_wheat_a_r1"):
    """a 5x6 shed at the street (tools, composter, bed) + a fenced 9-wide field behind it: farmland + water channel."""
    X, W, eave = 16, 9, 4
    b = new(name, X, W, eave + 4)
    section(b, X, W, basement=False)
    walls(b, 5, W, eave, x0=0, x1=4, z0=3, z1=7, wall="minecraft:spruce_planks", post="minecraft:oak_log")
    top = gable_roof(b, 5, W, eave, x0=0, x1=4, z0=3, z1=7, roof="pw:roof45_thatch", gable="minecraft:spruce_planks")
    door(b, 0, 0, 5, "south", wood="spruce")
    b.put(2, 1, 3, "minecraft:glass_pane"); b.put(2, 1, 7, "minecraft:glass_pane")
    b.put(4, 0, 5, "minecraft:air"); b.put(4, 1, 5, "minecraft:air")                       # back door to the field
    b.put(1, 0, 4, "minecraft:composter", composter_fill_level=0)
    b.put(1, 0, 6, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(3, 0, 4, "minecraft:bed", direction=2, head_piece_bit=True, occupied_bit=False)
    b.put(3, 0, 5, "minecraft:bed", direction=2, head_piece_bit=False, occupied_bit=False)
    b.put(2, 0, 6, "pw:furn_stool_spruce", **{"minecraft:cardinal_direction": "north"})
    b.put(1, 1, 7, "pw:furn_coat_pegs_spruce", **{"minecraft:cardinal_direction": "north"})
    # the field x 6..15, z 1..9: grass path border, fence, farmland with a water channel at z = 5
    b.fill(5, -1, 1, X - 1, -1, W, "minecraft:farmland", moisturized_amount=7)
    for x in range(5, X):
        b.put(x, -1, 5, "minecraft:water", liquid_depth=0)
    for x in range(5, X):
        b.put(x, -1, 1, "minecraft:grass_block"); b.put(x, -1, W, "minecraft:grass_block")   # under the fence rows
    b.fill(5, -1, 2, 5, -1, W - 1, "minecraft:grass_path")
    for x in range(5, X):
        b.put(x, 0, 1, "minecraft:oak_fence"); b.put(x, 0, W, "minecraft:oak_fence")
    for z in range(1, W + 1):
        b.put(X - 1, 0, z, "minecraft:oak_fence")
        b.put(X - 1, -1, z, "minecraft:grass_block")
    for x in range(6, X - 1):
        for z in (2, 3, 4, 6, 7, 8):
            b.put(x, 0, z, "minecraft:wheat", growth=7)
    b.put(1, 0, 2, "minecraft:hay_block", pillar_axis="y")
    b.put(1, 0, 1, "minecraft:hay_block", pillar_axis="y")
    lights(b, [(2, 2, 5)])
    b.marker("datum", "datum", 0, 0, 5, n=0)
    b.marker("station", "door", 0, 0, 5)
    b.marker("station", "store", 1, 0, 6)
    b.marker("station", "bed", 3, 0, 4)
    b.marker("station", "field", 8, 0, 3)
    b.marker("station", "field", 12, 0, 7)
    b.marker("station", "prep", 1, 0, 4)
    b.marker("station", "seat", 2, 0, 6)
    b.marker("station", "store", 1, 0, 2)
    b.zone("threshold", 1, 0, 5, 2, 6)
    b.zone("storeroom", 1, 0, 4, 3, 6)
    b.zone("garden", 5, 0, 2, X - 2, W - 1)
    b.zone("yard", 0, 0, 1, 4, W)                                         # the farmyard around the shed
    b.close_air()
    return b


def farm_terrace(name="pw:mvv_farm_terrace_a_r1"):
    """step 2b (his 22:23/22:24): the HILLSIDE FIELD — the same shed at the street, then four strips of farmland climbing
    away from it, each one block higher than the last, a cobblestone retaining wall between strips (the terrace face), a
    water channel down the middle, wheat on every strip, a cobblestone stair up one side. 21 deep x 9 wide; the plot's
    terrace pass fills the downhill side and the structure's own air cuts the uphill side."""
    X, W, eave = 21, 9, 4
    b = new(name, X, W, eave + 4)
    section(b, X, W, basement=False)                                       # earth under the WHOLE plot (run 0.0.11: the strips' 13-deep air pocket flooded)
    walls(b, 5, W, eave, x0=0, x1=4, z0=3, z1=7, wall="minecraft:spruce_planks", post="minecraft:oak_log")
    top = gable_roof(b, 5, W, eave, x0=0, x1=4, z0=3, z1=7, roof="pw:roof45_thatch", gable="minecraft:spruce_planks")
    door(b, 0, 0, 5, "south", wood="spruce")
    b.put(2, 1, 3, "minecraft:glass_pane"); b.put(2, 1, 7, "minecraft:glass_pane")
    b.put(4, 0, 5, "minecraft:air"); b.put(4, 1, 5, "minecraft:air")
    b.put(1, 0, 4, "minecraft:composter", composter_fill_level=0)
    b.put(1, 0, 6, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(3, 0, 4, "minecraft:bed", direction=2, head_piece_bit=True, occupied_bit=False)
    b.put(3, 0, 5, "minecraft:bed", direction=2, head_piece_bit=False, occupied_bit=False)
    b.put(2, 0, 6, "pw:furn_stool_spruce", **{"minecraft:cardinal_direction": "north"})
    b.put(1, 0, 2, "minecraft:hay_block", pillar_axis="y")
    # four strips, 3 deep each + the retaining wall row: strip k spans x = 6 + 4k .. 8 + 4k at feet k - 1 (the slab level
    # of strip 0 is the shed's feet -1); the wall row at x = 9 + 4k stands one higher than the strip it holds back
    for k in range(4):
        f = k - 1
        x0 = 6 + 4 * k
        for x in range(x0, x0 + 3):
            for z in range(1, W + 1):
                for ff in range(-1, f):                                   # earth under the strip, down to the shed's slab level
                    b.put(x, ff, z, "minecraft:dirt")
                b.put(x, f, z, "minecraft:farmland", moisturized_amount=7)
            b.put(x, f, 5, "minecraft:water", liquid_depth=0)              # the channel down the middle
            b.put(x, f, 1, "minecraft:grass_block"); b.put(x, f, W, "minecraft:grass_block")
            b.put(x, f + 1, 1, "minecraft:oak_fence"); b.put(x, f + 1, W, "minecraft:oak_fence")
            for z in (2, 3, 4, 6, 7, 8):
                b.put(x, f + 1, z, "minecraft:wheat", growth=7)
        if k < 3:                                                          # the retaining wall between this strip and the next
            xw = x0 + 3
            for z in range(1, W + 1):
                for ff in range(-1, f + 1):
                    b.put(xw, ff, z, "minecraft:cobblestone")
                b.put(xw, f + 1, z, "minecraft:cobblestone")
            b.put(xw, f + 1, 1, "minecraft:cobblestone"); b.put(xw, f + 2, 1, "minecraft:air")
    # the stair up the north edge (z = 1): one cobblestone step per terrace
    for k in range(4):
        b.put(5 + 4 * k, k - 1, 1, "minecraft:cobblestone")
    b.fill(5, -1, 1, 5, -1, W, "minecraft:grass_path")                    # the path column behind the shed, full width
    for z in range(1, W + 1):
        b.put(X - 1, 2, z, "minecraft:oak_fence"); b.put(X - 1, 1, z, "minecraft:grass_block")
        for ff in range(-1, 1):
            b.put(X - 1, ff, z, "minecraft:dirt")
    lights(b, [(2, 2, 5), (12, 3, 5)])
    b.marker("datum", "datum", 0, 0, 5, n=0)
    b.marker("station", "door", 0, 0, 5)
    b.marker("station", "store", 1, 0, 6)
    b.marker("station", "bed", 3, 0, 4)
    b.marker("station", "field", 7, 0, 3)
    b.marker("station", "field", 11, 1, 7)
    b.marker("station", "field", 15, 2, 3)
    b.marker("station", "prep", 1, 0, 4)
    b.marker("station", "seat", 2, 0, 6)
    b.marker("station", "store", 1, 0, 2)
    b.zone("threshold", 1, 0, 5, 2, 6)
    b.zone("storeroom", 1, 0, 4, 3, 6)
    b.zone("garden", 6, 0, 2, 8, W - 1)
    b.zone("yard", 0, 0, 1, 5, W)                                         # the farmyard: the shed and the path column behind it
    b.close_air()
    return b


def farm_cattle(name="pw:mvv_farm_cattle_a_r1"):
    """a barn (7 x 7, open-fronted stalls) + a fenced pen 9 deep behind, hay and a trough."""
    X, W, eave = 16, 8, 5
    b = new(name, X, W, eave + 5)
    section(b, X, W, basement=False)
    walls(b, 7, W, eave, x0=0, x1=6, wall="minecraft:spruce_planks", post="minecraft:oak_log")
    top = hip_roof(b, 7, W, eave, mat="oak", x0=0, x1=6)
    # barn door (double, front) and the stall gate to the pen at the back
    door(b, 0, 0, 4, "south", wood="spruce"); door(b, 0, 0, 5, "south", wood="spruce")
    b.put(6, 0, 4, "minecraft:fence_gate", open_bit=False, in_wall_bit=False, **{"minecraft:cardinal_direction": "west"}); b.put(6, 1, 4, "minecraft:air")
    for z in (2, 3, 6, 7):
        b.put(3, 0, z, "minecraft:oak_fence")                                  # stall dividers
    b.put(1, 0, 2, "minecraft:hay_block", pillar_axis="y"); b.put(1, 0, 3, "minecraft:hay_block", pillar_axis="y")
    b.put(1, 1, 2, "minecraft:hay_block", pillar_axis="y")
    b.put(1, 0, 7, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(5, 0, 7, "minecraft:cauldron", fill_level=6, cauldron_liquid="water")
    b.fill(1, 3, 2, 5, 3, W - 1, "minecraft:spruce_planks")                     # hay loft
    b.fill(2, 4, 3, 4, 4, 6, "minecraft:hay_block", pillar_axis="y")
    lx, lz = 5, 3                                                         # hay-loft ladder (not under a zone corner)
    for f in range(0, 4):
        b.put(lx, f, lz, "minecraft:ladder", facing_direction=4)
    # the pen x 7..15: grass, fence, trough, a shelter corner
    b.fill(7, -1, 1, X - 1, -1, W, "minecraft:grass_block")
    for x in range(7, X):
        b.put(x, 0, 1, "minecraft:oak_fence"); b.put(x, 0, W, "minecraft:oak_fence")
    for z in range(1, W + 1):
        b.put(X - 1, 0, z, "minecraft:oak_fence")
    b.put(X - 1, 0, 4, "minecraft:fence_gate", open_bit=False, in_wall_bit=False, **{"minecraft:cardinal_direction": "west"})
    b.put(9, 0, 7, "minecraft:cauldron", fill_level=6, cauldron_liquid="water")
    b.put(13, 0, 2, "minecraft:hay_block", pillar_axis="y"); b.put(14, 0, 2, "minecraft:hay_block", pillar_axis="y")
    lights(b, [(3, 2, 5)])
    b.marker("datum", "datum", 0, 0, 4, n=0)
    b.marker("station", "door", 0, 0, 4)
    b.marker("station", "store", 1, 0, 7)
    b.marker("station", "store", 1, 0, 2)
    b.marker("station", "pen", 2, 0, 5)
    b.marker("station", "pen", 11, 0, 4)
    b.marker("station", "yard", 13, 0, 3)
    b.zone("threshold", 1, 0, 4, 2, 5)
    b.zone("stable", 1, 0, 2, 5, W - 1)
    b.zone("storeroom", 1, 4, 2, 5, W - 1)
    b.zone("yard", 7, 0, 2, X - 2, W - 1)
    b.close_air()
    return b


def lumberyard(name="pw:mvv_lumberyard_a_r1"):
    """an open shed (posts + roof, no walls) over the sawbench, log racks and plank stacks; a yard with log piles."""
    X, W, eave = 14, 9, 4
    b = new(name, X, W, eave + 5)
    section(b, X, W, basement=False)
    b.fill(0, -1, 1, X - 1, -1, W, "minecraft:coarse_dirt")
    b.fill(0, -1, 1, 7, -1, W, "minecraft:cobblestone")
    for (x, z) in [(0, 1), (0, W), (7, 1), (7, W), (3, 1), (3, W)]:
        for f in range(0, eave):
            b.put(x, f, z, "minecraft:spruce_log", pillar_axis="y")
    for x in range(0, 8):
        for z in (1, W):
            b.put(x, eave - 1, z, "minecraft:spruce_log", pillar_axis="x")
    top = hip_roof(b, 8, W, eave, mat="oak", x0=0, x1=7)
    b.put(3, 0, 5, "minecraft:stonecutter_block", **{"minecraft:cardinal_direction": "north"})   # sawbench stand-in
    for z in (3, 4):
        b.put(1, 0, z, "minecraft:oak_log", pillar_axis="x"); b.put(2, 0, z, "minecraft:oak_log", pillar_axis="x")
        b.put(1, 1, z, "minecraft:oak_log", pillar_axis="x")
    for z in (6, 7):
        b.put(5, 0, z, "minecraft:oak_planks"); b.put(6, 0, z, "minecraft:oak_planks"); b.put(5, 1, z, "minecraft:oak_planks")
    b.put(6, 0, 2, "pw:furn_trestle_oak", **{"minecraft:cardinal_direction": "north"})
    b.put(1, 0, 8, "minecraft:barrel", facing_direction=1, open_bit=False)
    # yard: log piles and a chopping block
    for x in (9, 10, 11):
        b.put(x, 0, 2, "minecraft:spruce_log", pillar_axis="x"); b.put(x, 0, 3, "minecraft:spruce_log", pillar_axis="x")
        b.put(x, 1, 2, "minecraft:spruce_log", pillar_axis="x")
    for x in (9, 10):
        b.put(x, 0, 7, "minecraft:birch_log", pillar_axis="x"); b.put(x, 0, 8, "minecraft:birch_log", pillar_axis="x")
    b.put(12, 0, 5, "minecraft:oak_log", pillar_axis="y")
    for x in range(0, X):
        for z in (1, W):
            if b.get(x, 0, z) != "minecraft:spruce_log":
                b.put(x, 0, z, "minecraft:spruce_fence")
    for z in range(1, W + 1):
        b.put(X - 1, 0, z, "minecraft:spruce_fence")
    lights(b, [(4, 3, 5)])
    b.marker("datum", "datum", 0, 0, 5, n=0)
    b.marker("station", "door", 0, 0, 5)
    b.marker("station", "bench", 3, 0, 5)
    b.marker("station", "rack", 1, 0, 3)
    b.marker("station", "store", 1, 0, 8)
    b.marker("station", "prep", 6, 0, 2)
    b.marker("station", "yard", 10, 0, 5)
    b.marker("station", "yard", 12, 0, 4)
    b.zone("workfloor", 0, 0, 2, 7, W - 1)                                # under the open shed (post rows excluded)
    b.zone("yard", 0, 0, 2, X - 2, W - 1)                                 # the whole working ground inside the fence
    b.close_air()
    return b


def quarry(name="pw:mvv_quarry_a_r1"):
    """a stepped stone pit (3 benches down to -6) with ladders, a hut at the street with the tool store."""
    X, W = 14, 11
    b = new(name, X, W, 6)
    section(b, X, W, basement=False)
    b.fill(0, -11, 1, X - 1, -1, W, "minecraft:stone")
    b.fill(0, -1, 1, X - 1, -1, W, "minecraft:grass_block")
    # hut x 0..3, z 4..8
    walls(b, 4, W, 3, x0=0, x1=3, z0=4, z1=8, wall="minecraft:cobblestone", post="minecraft:spruce_log")
    gable_roof(b, 4, W, 3, x0=0, x1=3, z0=4, z1=8, roof="pw:roof45_oak", gable="minecraft:cobblestone")
    door(b, 0, 0, 6, "south")
    b.put(3, 0, 6, "minecraft:air"); b.put(3, 1, 6, "minecraft:air")
    b.put(1, 0, 5, "minecraft:chest", **{"minecraft:cardinal_direction": "east"})
    b.put(1, 0, 7, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(2, 0, 7, "pw:furn_stool_oak", **{"minecraft:cardinal_direction": "north"})
    # the pit: benches x 5..12 / z 2..10, each 2 deep
    for k, depth in enumerate((-2, -4, -6)):
        xa, xb_, za, zb = 5 + k, X - 2 - k, 2 + k, W - 1 - k
        b.fill(xa, -1, za, xb_, -1, zb, "minecraft:air")
        b.fill(xa, depth + 1, za, xb_, -1, zb, "minecraft:air")
        b.fill(xa, depth, za, xb_, depth, zb, "minecraft:stone")
        for x in range(xa, xb_ + 1):
            for z in range(za, zb + 1):
                if (x + z) % 3 == 0:
                    b.put(x, depth, z, "minecraft:cobblestone")
    for f in (-3, -2):                                                    # bench 0 -> bench 1
        b.put(6, f, 6, "minecraft:ladder", facing_direction=5)
    for f in (-5, -4):                                                    # bench 1 -> bench 2
        b.put(7, f, 6, "minecraft:ladder", facing_direction=5)
    b.put(8, -6, 6, "minecraft:stone"); b.put(9, -6, 5, "minecraft:cobblestone")
    b.put(7, -4, 3, "minecraft:barrel", facing_direction=1, open_bit=False)
    lights(b, [(1, 2, 6), (8, -5, 6), (8, -3, 4)])
    b.marker("datum", "datum", 0, 0, 6, n=0)
    b.marker("station", "door", 0, 0, 6)
    b.marker("station", "store", 1, 0, 5)
    b.marker("station", "store", 1, 0, 7)
    b.marker("station", "seat", 2, 0, 7)
    b.marker("station", "yard", 8, -5, 6)
    b.marker("station", "yard", 7, -3, 8)
    b.marker("station", "yard", 6, -1, 4)
    b.zone("storeroom", 1, 0, 5, 2, 7)
    b.zone("yard", 0, 0, 1, X - 1, W)                                     # the site at grade
    for k, walk in enumerate((-1, -3, -5)):                               # one ring per bench, at its walking level
        b.zone("yard", 5 + k, walk, 2 + k, X - 2 - k, W - 1 - k)
    b.close_air()
    return b


def well(name="pw:mvv_well_a_r1"):
    """a 5 x 5 stone well with a shingle roof on four posts; the commons zone around it."""
    X, W = 5, 5
    b = new(name, X, W, 6)
    section(b, X, W, basement=False)
    b.fill(0, -1, 1, X - 1, -1, W, "minecraft:cobblestone")
    # D-C533 (his 19:48): the well's water is a stone-lined shaft that goes down to the SEWER level — feet -14 is the
    # street trench's water level (box y1); the hollow is water source blocks all the way; a floor of stone bricks below
    b.fill(1, -15, 2, 3, -15, 4, "minecraft:stone_bricks")
    b.fill(1, -14, 2, 3, -2, 4, "minecraft:stone_bricks")
    b.fill(2, -14, 3, 2, -1, 3, "minecraft:water", liquid_depth=0)
    for (x, z) in [(1, 2), (1, 4), (3, 2), (3, 4)]:
        b.put(x, -1, z, "minecraft:stone_bricks")
    # his 08:55 CT 10-05 (Q34): four lone wall posts never read as a parapet — the ring closes through the posts' feet:
    # eight walls with their connection states (G.wall_ring), the spruce posts rising from the four corners
    G.wall_ring(b, [(1, 2), (2, 2), (3, 2), (3, 3), (3, 4), (2, 4), (1, 4), (1, 3)], 0)
    for (x, z) in [(1, 2), (1, 4), (3, 2), (3, 4)]:
        for f in range(1, 3):
            b.put(x, f, z, "minecraft:spruce_fence")
    hip_roof(b, 5, W, 3, mat="spruce", x0=0, x1=4, z0=1, z1=5)
    b.put(2, 2, 3, "minecraft:spruce_fence")
    b.put(2, 1, 3, "minecraft:cauldron", fill_level=6, cauldron_liquid="water")
    b.marker("datum", "datum", 0, 0, 3, n=0)
    b.marker("port", "well", 2, 0, 3)
    b.marker("station", "yard", 0, 0, 3)
    b.zone("commons", 0, 0, 1, 4, 5)
    b.close_air()
    return b



def manor(name="pw:mvv_manor_a_r1"):
    """D (his C3, R3 §5 at town scale): the MANOR HOUSE of town II — the lord's family, the steward, the cook, the
    housekeeper, the groom — with R3's hidden world: the RECEPTION rooms in front (parlour, entrance hall, dining hall),
    a SERVICE CORRIDOR 2 wide behind them running the whole width with JIB DOORS (doors of the partition's own spruce, no
    frame) into each room and a BAIZE DOOR (warped = green) from the hall, the BACK RANGE behind it (kitchen with hearth
    and ovens, the BACK STAIR, the steward's office with the lectern and the estate chests, the pantry), the family's
    chambers on the first floor with the service corridor continuing above, and the servants' GARRETS in the roof.
    20 deep x 21 wide, stone-brick ground floor, oak-plank upper storey on spruce posts (the roster's palette), spruce hip roof."""
    X, W = 20, 21
    eave = 9                                                             # ground floor 0..3, course 4, first floor 5..8
    b = new(name, X, W, eave + 12)
    section(b, X, W)
    # ---- shell: stone-brick ground floor, oak upper storey, posts
    walls(b, X, W, 4, wall="minecraft:stone_bricks", post="minecraft:spruce_log")
    for f in range(4, eave):
        for x in range(0, X):
            b.put(x, f, 1, "minecraft:oak_planks"); b.put(x, f, W, "minecraft:oak_planks")
        for z in range(1, W + 1):
            b.put(0, f, z, "minecraft:oak_planks"); b.put(X - 1, f, z, "minecraft:oak_planks")
        for (x, z) in [(0, 1), (0, W), (X - 1, 1), (X - 1, W), (0, 11), (X - 1, 11), (10, 1), (10, W)]:
            b.put(x, f, z, "minecraft:spruce_log", pillar_axis="y")
    b.fill(1, 0, 2, X - 2, eave - 1, W - 1, "minecraft:air")
    b.fill(1, 4, 2, X - 2, 4, W - 1, "minecraft:spruce_planks")         # first floor course
    # ---- the plan (x = depth from the street; z = frontage)
    XP, XC0, XC1, XB = 10, 11, 12, 13                                  # partition, service corridor, partition to the back range
    for f in list(range(0, 4)) + list(range(5, eave)):
        for z in range(2, W):
            b.put(XP, f, z, "minecraft:spruce_planks"); b.put(XB, f, z, "minecraft:spruce_planks")
    # front rooms: parlour z 2..7 | hall z 9..13 | dining z 15..20 (partitions z 8 and 14, x 1..9)
    for f in range(0, 4):
        for x in range(1, XP):
            b.put(x, f, 8, "minecraft:spruce_planks"); b.put(x, f, 14, "minecraft:spruce_planks")
    # back range: kitchen z 2..8 | back stair z 10..11 | office z 13..16 | pantry z 18..20 (partitions z 9, 12, 17, x 14..18)
    for f in range(0, 4):
        for x in range(XB + 1, X - 1):
            for zz in (9, 12, 17):
                b.put(x, f, zz, "minecraft:spruce_planks")
    zm = 11
    # the front door (double, spruce), the hall's doors into the parlour and the dining hall
    door(b, 0, 0, zm, "south", wood="spruce"); door(b, 0, 0, zm - 1, "south", wood="spruce")
    door(b, 5, 0, 8, "west", wood="spruce"); door(b, 5, 0, 14, "east", wood="spruce")
    # JIB doors from the service corridor (x 11..12) into the reception rooms (spruce in spruce, no frame) + the BAIZE door
    door(b, XP, 0, 4, "north", wood="spruce"); door(b, XP, 0, 18, "north", wood="spruce")
    door(b, XP, 0, 11, "north", wood="warped")                          # the baize door: the hall <-> the service side
    # the back range's doors off the corridor
    for zz in (5, 10, 14, 19):
        door(b, XB, 0, zz, "north", wood="spruce")
    # windows: ground floor front + sides, first floor all round
    for z in (3, 5, 16, 18):                                              # the façade mirrors about the door (z 10.5)
        b.put(0, 1, z, "minecraft:glass_pane"); b.put(0, 2, z, "minecraft:glass_pane")
    for x in (3, 6, 15, 17):
        b.put(x, 1, 1, "minecraft:glass_pane"); b.put(x, 1, W, "minecraft:glass_pane")
    for z in (3, 6, 9, 12, 15, 18):
        if z == 11: continue
        b.put(0, 6, z, "minecraft:glass_pane"); b.put(0, 7, z, "minecraft:glass_pane"); b.put(X - 1, 6, z, "minecraft:glass_pane")
    for x in (3, 7, 15):
        b.put(x, 6, 1, "minecraft:glass_pane"); b.put(x, 6, W, "minecraft:glass_pane")
    # ---- the PARLOUR: hearth on the left wall, two chairs, a cupboard
    b.put(4, 0, 1, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": "south", "pw:phase": "cold"})
    b.put(3, 0, 3, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "north"})
    b.put(5, 0, 3, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "north"})
    b.put(8, 0, 2, "pw:furn_cupboard_dark_oak", **{"minecraft:cardinal_direction": "south"})
    # ---- the DINING HALL: a long table with chairs both sides, a hearth on the right wall
    for x in range(3, 8):
        b.put(x, 0, 17, "pw:furn_table_dark_oak", **{"pw:n": False, "pw:e": False, "pw:s": False, "pw:w": False})
        b.put(x, 0, 16, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "south"})
        b.put(x, 0, 18, "pw:furn_chair_dark_oak", **{"minecraft:cardinal_direction": "north"})
    b.put(5, 0, W, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": "north", "pw:phase": "cold"})
    # ---- the HALL: a bench either side
    b.put(2, 0, 9, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "south"})
    b.put(2, 0, 13, "pw:furn_bench_spruce", **{"minecraft:cardinal_direction": "north"})
    # ---- the KITCHEN: the hearth on the back wall, two ovens, the prep table, barrels
    hx, hz = X - 1, 5
    b.put(hx, 0, hz, "pw:hearth_brick", **{"minecraft:cardinal_direction": "west", "pw:phase": "cold"})
    b.put(X - 2, 0, 3, "minecraft:furnace", **{"minecraft:cardinal_direction": "west"})
    b.put(X - 2, 0, 7, "minecraft:furnace", **{"minecraft:cardinal_direction": "west"})
    b.put(15, 0, 5, "pw:furn_trestle_spruce", **{"minecraft:cardinal_direction": "west"})
    b.put(14, 0, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    # ---- the STEWARD'S OFFICE: the lectern desk, the estate chests
    b.put(16, 0, 14, "minecraft:lectern", **{"minecraft:cardinal_direction": "west", "powered_bit": False})
    b.put(18, 0, 13, "minecraft:chest", **{"minecraft:cardinal_direction": "west"})
    b.put(18, 0, 16, "minecraft:chest", **{"minecraft:cardinal_direction": "west"})
    # ---- the PANTRY: barrels
    for z in (18, 19, 20):
        b.put(18, 0, z, "minecraft:barrel", facing_direction=1, open_bit=False)
    # ---- the BACK STAIR: one ladder from the cellar to the garrets (x 14, z 10), on the stair room's partition
    lx, lz = XB + 1, 10
    for f in range(-5, eave + 1):
        b.put(lx, f, lz, "minecraft:ladder", facing_direction=5)
    # ---- FIRST FLOOR: the lord's chamber (front left), the guest chamber (front right), the corridor continues behind
    for f in range(5, eave):
        for x in range(1, XP):
            b.put(x, f, 11, "minecraft:spruce_planks")
    door(b, XP, 5, 6, "north", wood="spruce"); door(b, XP, 5, 16, "north", wood="spruce")      # jib doors above
    b.put(3, 5, 4, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False); b.put(4, 5, 4, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
    b.put(3, 5, 5, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False); b.put(4, 5, 5, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
    b.put(2, 5, 8, "minecraft:chest", **{"minecraft:cardinal_direction": "east"})
    b.put(3, 5, 17, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False); b.put(4, 5, 17, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
    b.put(2, 5, 19, "minecraft:chest", **{"minecraft:cardinal_direction": "east"})
    # the steward's and the housekeeper's rooms over the back range
    for x in range(XB + 1, X - 1):
        for f in range(5, eave):
            b.put(x, f, 12, "minecraft:spruce_planks")
    door(b, XB, 5, 6, "north", wood="spruce"); door(b, XB, 5, 16, "north", wood="spruce")
    b.put(16, 5, 4, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False); b.put(17, 5, 4, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
    b.put(16, 5, 18, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False); b.put(17, 5, 18, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
    # ---- the ROOF and the GARRETS inside it
    top = hip_roof(b, X, W, eave, mat="spruce")
    b.fill(1, eave, 2, X - 2, eave, W - 1, "minecraft:spruce_planks")    # the garret floor
    b.put(lx, eave, lz, "minecraft:ladder", facing_direction=5)           # the stair comes up through it
    for (bx, bz) in [(5, 6), (5, 9), (5, 13), (5, 16), (13, 6), (13, 16)]:
        b.put(bx, eave + 1, bz, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False)
        b.put(bx + 1, eave + 1, bz, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
    # chimneys: the parlour's and the dining hall's flues up the side walls, the kitchen's up the back wall
    # (preview 04:2x: flues run to the ROOF LINE at their own cell + 3, not to the ridge — 11-high poles at the eaves read wrong)
    for (fx, fz) in [(4, 1), (5, W), (hx, hz)]:
        k = min(fx, X - 1 - fx, fz - 1, W - fz)                         # the hip ring over this cell
        ftop = eave + k + 3
        for f in range(1, ftop):
            if b.get(fx, f, fz) in (None, "minecraft:air", "minecraft:stone_bricks", "minecraft:oak_planks", "pw:roof45_spruce", "pw:roof_hip_spruce", "minecraft:spruce_log"):
                b.put(fx, f, fz, "pw:flue_stone_bricks", **{"pw:cap": False})
        b.put(fx, ftop, fz, "pw:flue_stone_bricks", **{"pw:cap": True})
    # the cellar: the wine store (barrels) and the plate chest
    for x in (3, 4, 5, 6):
        b.put(x, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(2, -5, W - 1, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    lights(b, [(4, 3, 5), (4, 3, 17), (3, 3, 11), (11, 3, 6), (11, 3, 16), (16, 3, 5), (16, 3, 14), (4, 8, 6), (4, 8, 17), (11, 8, 11), (16, 8, 6), (9, eave + 3, 11), (4, -2, 10)])
    # ---- markers
    b.marker("datum", "datum", 0, 0, zm, n=0)
    b.marker("station", "door", 0, 0, zm)
    b.marker("station", "desk", 16, 0, 14)                               # the steward
    b.marker("station", "hearth", hx, 0, hz)                             # the cook
    b.marker("station", "oven", X - 2, 0, 3)
    b.marker("station", "oven", X - 2, 0, 7)
    b.marker("station", "hearth", 4, 0, 1)                               # the parlour's fire
    b.marker("station", "hearth", 5, 0, W)                               # the dining hall's fire
    b.marker("station", "store", 14, 0, 2)
    b.marker("station", "prep", 15, 0, 5)
    b.marker("station", "store", 18, 0, 19)                              # the housekeeper's pantry
    b.marker("station", "store", 18, 0, 13)
    b.marker("station", "store", 3, -5, 2)
    b.marker("station", "table", 5, 0, 17)
    for x in range(3, 8):
        b.marker("station", "seat", x, 0, 16); b.marker("station", "seat", x, 0, 18)
    b.marker("station", "seat", 3, 0, 3); b.marker("station", "seat", 5, 0, 3)
    b.marker("station", "seat", 2, 0, 9); b.marker("station", "seat", 2, 0, 13)
    for (bx, bf, bz) in [(3, 5, 4), (3, 5, 5), (3, 5, 17), (16, 5, 4), (16, 5, 18), (5, eave + 1, 6), (5, eave + 1, 9), (5, eave + 1, 13), (5, eave + 1, 16), (13, eave + 1, 6), (13, eave + 1, 16)]:
        b.marker("station", "bed", bx, bf, bz)
    b.zone("threshold", 1, 0, zm - 1, 2, zm + 1)
    b.zone("commons", 1, 0, 9, XP - 1, 13)                               # the hall
    b.zone("chamber", 1, 0, 2, XP - 1, 7)                                # the parlour
    b.zone("commons", 1, 0, 15, XP - 1, W - 1)                           # the dining hall
    b.zone("storeroom", XC0, 0, 2, XC1, W - 1)                           # the service corridor (the hidden world)
    b.zone("kitchen", XB + 1, 0, 2, X - 2, 8)
    b.zone("storeroom", XB + 1, 0, 13, X - 2, 16)                        # the office
    b.zone("storeroom", XB + 1, 0, 18, X - 2, W - 1)                     # the pantry
    b.zone("quarters", 1, 5, 2, XP - 1, 10)
    b.zone("quarters", 1, 5, 12, XP - 1, W - 1)
    b.zone("quarters", 2, eave + 1, 3, X - 3, W - 2)                     # the garrets
    b.zone("cellar", 1, -5, 2, X - 2, W - 1)
    b.close_air()
    return b

ROSTER = {"cottage_s": lambda: G.cottage(), "cottage_m": cottage_m, "cottage_l": cottage_l, "bakery": bakery, "butcher": butcher,
          "smithy": smithy, "inn": inn, "town_hall": town_hall, "farm_wheat": farm_wheat, "farm_cattle": farm_cattle,
          "lumberyard": lumberyard, "quarry": quarry, "well": well, "farm_terrace": farm_terrace, "manor": manor}


def main():
    names = sys.argv[1:] or list(ROSTER)
    report = {}
    for n in names:
        b = ROSTER[n]()
        stem = b.name.split(":")[1]
        b.write(OUT / "structures/pw" / f"{stem}.mcstructure", OUT / "manifests" / f"{stem}.json")
        m = b.manifest()
        st = [x for x in m["entities"] if x.get("fam") == "station"]
        zn = {x["kind"] for x in m["entities"] if x.get("fam") == "zone"}
        report[b.name] = {"size": m["size"], "blocks": len(m["blocks"]), "stations": sorted({f"{x['kind']}" for x in st}),
                          "n_stations": len(st), "zones": sorted(zn), "entities": len(b.st.entities)}
        print(b.name, m["size"], "blocks", len(m["blocks"]), "stations", len(st), "zones", sorted(zn))
    (OUT / "ROSTER-REPORT.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
