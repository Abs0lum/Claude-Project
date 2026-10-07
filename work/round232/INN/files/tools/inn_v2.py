#!/usr/bin/env python3
"""inn_v2.py — the CIVITAS INN redesigned (BLOCKS round 231; his ruling 00:23 CT 10-07: "two 4 beds to a room, separated by
1 block only, and at least 6 rooms").

1.3.232 (#INN, his ruling D-GH1007-INN 2026-10-07: "mix of 2- and 4-bed rooms; KEEP existing inns"): this inn is now its
OWN family pw:mvv_inn_{a,b,c,d}_r2 (the clock lays it for NEW inns only; pw:mvv_inn_*_r1 stays the 1.3.230 inn), and each
guest floor holds two 4-bed rooms and four 2-bed rooms. Same shell, same 32 guest beds, same bed cells as round 231: a
2-bed room is half of a 4-bed room's span, split by a log partition in the free column between its 2nd and 3rd bed.
  guest floor (feet 4 and 8 alike), seen from above, street (x = 0) on the left, north (z 1) at the top:
    north side z 2..4   x 1..7 FOUR beds (door x 4) | log x 8 | x 9..11 TWO (door x 10) | log x 12 | x 13..15 TWO (door x 14)
    corridor  z 6..7    (walls z 5 / z 8, ladder at x 15 z 6)
    south side z 9..11  x 1..3 TWO (door x 2) | log x 4 | x 5..7 TWO (door x 6) | log x 8 | x 9..15 FOUR beds (door x 12)
  rooms table: 2 floors x (2 four-bed + 4 two-bed) = 12 rooms = 4 x 4 beds + 8 x 2 beds = 32 guest beds.
  (Round 231 was 8 rooms x 4 beds = 32 under the r1 name; the table below is the ruling's test, see check_rooms.)

ASSUMPTION (231, kept): EXACTLY one block of floor between neighbouring beds in a room, and at least 6 guest rooms.
ASSUMPTION (232): the mix is an even split of the beds (16 in 4-bed rooms, 16 in 2-bed rooms), the same on both floors.

Same shell recipe and contracts as tools/civ_roster.py (it reuses its helpers): the front wall is local x = 0 and faces the
street (the door at x = 0, f = 0, z = ZM, datum marker on it), the clearance column z = 0, feet 0 at structure y 15, the
basement / manhole / sewer port from section(), hip roof, ladder + hatch to the cellar. Only the size grows:
    old  11 deep x 9 front (size [11, 30, 10])      new  17 deep x 12 front (size [17, 34, 13])

  feet -5..-2  cellar: stores (barrels, chests), ladder + hatch up at (1, z 3)
  feet  0..2   taproom: front door z 7 · 4 tables with chairs · hearth + mantel + bench on the back wall · bar (5 shelves) with
               2 barrels behind it · the open corridor z 6..7 from the door to the stair ladder at the back (x 15, z 6)
  feet  4..6   guest floor 1 } each: a corridor z 6..7 (x 1..15) between two partition walls (z 5, z 8); 6 rooms off it:
  feet  8..10  guest floor 2 }   north rooms z 2..4, south rooms z 9..11 (SIDE_ROOMS: log partitions between the rooms);
                                 n beds per room at x = x0, x0+2, .. (a 1-block gap between beds), heads against the
                                 outer wall, an aisle at the foot; one door per room into the corridor; one window per gap
  feet  3, 7, 11 plank floor courses · eave 12 · hip roof (top feet 18)
Doors follow the roster's witnessed convention: in an x-normal wall "south" (the front door), in a z-normal wall "east"/"west".
Beds: direction 2 = head north (head cell at the lower z), 0 = head south (as cottage_m / cottage_l).

Outputs (all under /home/claude/_staging/blocks231; 1.3.232: re-pointed by tools/run_inn_offline.py when run elsewhere):
  BP-02/structures/pw/mvv_inn_{a,b,c,d}_r2.mcstructure          the finished buildings (skins via tools/civ_variants.py)
  BP-02/structures/pw/stages/mvv_inn_{a..d}_r2_s0..s4 + _w / _r  the 5 build stages (tools/civ_stages.py) + weather overlays
  civ_inn/manifests/*.json, civ_inn/CIV_BUILDINGS-inn.json       the 4 table entries (civ_village_data rules + art slots)
  renders/INN-V2-PLAN-*.png                                       one top-down plan per floor
Usage: python3 tools/inn_v2.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import civ_roster as R          # noqa: E402
import civ_variants as VAR      # noqa: E402
import civ_stages as STG        # noqa: E402
import civ_village_data as V    # noqa: E402
import art_slots as AS          # noqa: E402
import weather_overlays as WO   # noqa: E402
import mcstructure as M         # noqa: E402

STAGE_ROOT = Path("/home/claude/_staging/blocks231")
BP = STAGE_ROOT / "BP-02/structures/pw"
CIV = STAGE_ROOT / "civ_inn"

X, W, EAVE = 17, 12, 12            # depth (x 0..16), frontage walls z 1..12 (+ clearance column z 0), eave feet
ZM = 7                             # the front door's z
FLOORS = (4, 8)                    # guest floor feet levels
COURSES = (3, 7, 11)               # plank floor courses
LADDER = (15, 6)                   # the stair ladder column (hangs on the back wall x = 16, facing 4)
NORTH, SOUTH = (2, 4), (9, 11)     # room spans along z; corridor z 6..7 between partitions z 5 and z 8
# 1.3.232 (#INN, D-GH1007-INN "mix of 2- and 4-bed rooms"): the rooms of each side of a guest floor, (x0, x1, beds), west to
# east; a spruce-log partition stands in the column between two neighbouring rooms (north x 8 + x 12, south x 4 + x 8)
SIDE_ROOMS = {NORTH: ((1, 7, 4), (9, 11, 2), (13, 15, 2)),
              SOUTH: ((1, 3, 2), (5, 7, 2), (9, 15, 4))}
SIDE_DOOR = {NORTH: (5, "east"), SOUTH: (8, "west")}   # the room door's corridor wall z and facing (roster convention)
SIDE_BED = {NORTH: (2, 3, 2), SOUTH: (11, 10, 0)}      # head z, foot z, bed direction (2 = head north, 0 = head south)


def bed_xs(x0, n):
    """n beds with exactly one free block between neighbours: x0, x0+2, .., x0+2(n-1)."""
    return [x0 + 2 * k for k in range(n)]


def guest_floor(b, f):
    """partitions, doors, beds, windows and lights of one guest floor at feet f (f .. f+2 open, f+3 the next course).
    Returns (beds [(x, f, head z)], rooms [(x0, x1, (z0, z1), n)])."""
    for x in range(1, X - 1):                                            # corridor walls z 5 and z 8
        for ff in range(f, f + 3):
            b.put(x, ff, 5, "minecraft:oak_planks")
            b.put(x, ff, 8, "minecraft:oak_planks")
    beds, rooms, lit = [], [], []
    for side, plan in SIDE_ROOMS.items():
        z0, z1 = side
        wz, facing = SIDE_DOOR[side]
        hz, fz, dirn = SIDE_BED[side]
        win_z = 1 if side == NORTH else W                                 # the outer wall behind the heads
        for i, (x0, x1, n) in enumerate(plan):
            if i + 1 < len(plan):                                         # the log partition east of this room
                px = x1 + 1
                assert plan[i + 1][0] == px + 1, f"rooms {plan[i]} / {plan[i + 1]}: one partition column between rooms"
                for z in range(z0, z1 + 1):
                    for ff in range(f, f + 3):
                        b.put(px, ff, z, "minecraft:spruce_log", pillar_axis="y")
            xs = bed_xs(x0, n)
            assert xs[-1] == x1, f"room x {x0}..{x1}: {n} beds one block apart must fill the span"
            dx = x0 + n - 1                                               # the door: opposite the middle gap
            R.door(b, dx, f, wz, facing, wood="spruce")
            for bx in xs:                                                 # head against the outer wall, foot, aisle beyond
                b.put(bx, f, hz, "minecraft:bed", direction=dirn, head_piece_bit=True, occupied_bit=False)
                b.put(bx, f, fz, "minecraft:bed", direction=dirn, head_piece_bit=False, occupied_bit=False)
                beds.append((bx, f, hz))
            for gx in range(x0 + 1, x1, 2):                               # windows in the gaps (above the floor, beside the heads)
                b.put(gx, f + 1, win_z, "minecraft:glass_pane")
            lit.append((dx, f + 2, (z0 + z1) // 2 if side == NORTH else (z0 + z1 + 1) // 2))   # z 3 / z 10 as round 231
            rooms.append((x0, x1, side, n))
    R.lights(b, lit + [(4, f + 2, 6), (12, f + 2, 7)])
    return beds, rooms


def inn2(name="pw:mvv_inn_a_r2"):
    """The inn, version 2 (see the module docstring for the plan)."""
    b = R.new(name, X, W, EAVE + 6)
    R.section(b, X, W)
    R.walls(b, X, W, EAVE)
    for c in COURSES:
        b.fill(1, c, 2, X - 2, c, W - 1, "minecraft:oak_planks")
    top = R.hip_roof(b, X, W, EAVE)
    R.door(b, 0, 0, ZM, "south", wood="spruce")
    # ground-floor windows (front + sides), guest-floor front windows
    for z in (3, 5, 9, 11):
        b.put(0, 1, z, "minecraft:glass_pane")
    for z in (3, 10):
        for f in FLOORS:
            b.put(0, f + 1, z, "minecraft:glass_pane")
    for x in (3, 6, 10, 13):
        b.put(x, 1, 1, "minecraft:glass_pane")
        b.put(x, 1, W, "minecraft:glass_pane")
    # hearth on the back wall (as the old inn), flue up the wall through the eave
    hx, hz = X - 1, 3
    b.put(hx, 0, hz, "pw:hearth_stone_bricks", **{"minecraft:cardinal_direction": "west", "pw:phase": "cold"})
    for f in range(1, top):
        b.put(hx, f, hz, "pw:flue_stone_bricks", **{"pw:cap": False})
    b.put(hx, top, hz, "pw:flue_stone_bricks", **{"pw:cap": True})
    b.put(hx - 1, 1, hz, "pw:furn_mantel_oak", **{"minecraft:cardinal_direction": "west"})
    b.put(hx - 2, 0, hz, "pw:furn_bench_oak", **{"minecraft:cardinal_direction": "east"})
    # the bar: shelves x 9..13 along z 9 (the counter), the keeper's walk z 10, barrels at z 11
    for x in range(9, 14):
        b.put(x, 0, 9, "pw:furn_shelf_oak", **{"minecraft:cardinal_direction": "north"})
    for x in (9, 11, 13):
        b.put(x, 0, 11, "minecraft:barrel", facing_direction=1, open_bit=False)
    # 4 tables with a chair either side (north side z 2..4 and the front-south corner), the corridor z 5..8 kept clear
    tables = [(3, 3), (7, 3), (11, 3), (4, 10)]
    for (tx, tz) in tables:
        b.put(tx, 0, tz, "pw:furn_table_oak", **{"pw:n": False, "pw:e": False, "pw:s": False, "pw:w": False})
        b.put(tx, 0, tz - 1, "pw:furn_chair_oak", **{"minecraft:cardinal_direction": "south"})
        b.put(tx, 0, tz + 1, "pw:furn_chair_oak", **{"minecraft:cardinal_direction": "north"})
    # the stair ladder: ground floor -> guest floor 2 through the two courses (hangs on the back wall)
    lx, lz = LADDER
    for f in range(0, FLOORS[1] + 3):
        b.put(lx, f, lz, "minecraft:ladder", facing_direction=4)
    # guest floors
    beds, rooms = [], []
    for f in FLOORS:
        bb, rr = guest_floor(b, f)
        beds += bb
        rooms += [(x0, x1, zs, f, n) for (x0, x1, zs, n) in rr]          # 1.3.232 (#INN): + the room's bed count
    # cellar: ladder + hatch (as the old inn), stores
    cx, cz = 1, 3
    for f in range(-5, 0):
        b.put(cx, f, cz, "minecraft:ladder", facing_direction=5)
    b.hatch(cx, -1, cz, ladder_facing=5)
    for x in (3, 4, 5, 6, 7):
        b.put(x, -5, 2, "minecraft:barrel", facing_direction=1, open_bit=False)
    for x in (3, 5, 7):
        b.put(x, -5, W - 1, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    R.lights(b, [(3, 2, 6), (8, 2, 7), (13, 2, 6), (5, -2, 6), (11, -2, 6)])
    # markers: datum + stations
    b.marker("datum", "datum", 0, 0, ZM, n=0)
    b.marker("station", "door", 0, 0, ZM)
    b.marker("station", "hearth", hx, 0, hz)
    b.marker("station", "counter", 11, 0, 9)
    b.marker("station", "seat", hx - 2, 0, hz)
    for (tx, tz) in tables:
        b.marker("station", "table", tx, 0, tz)
        b.marker("station", "seat", tx, 0, tz - 1)
        b.marker("station", "seat", tx, 0, tz + 1)
    for (x, z) in ((9, 11), (13, 11)):
        b.marker("station", "store", x, 0, z)
    b.marker("station", "store", 4, -5, 2)
    b.marker("station", "store", 5, -5, W - 1)
    for (bx, bf, bz) in beds:
        b.marker("station", "bed", bx, bf, bz)
    # zones (one ring per room at floor level, ZONE-GEOMETRY-v2)
    b.zone("threshold", 1, 0, ZM - 1, 2, ZM)
    b.zone("commons", 1, 0, 2, X - 2, 8)
    b.zone("shopfloor", 8, 0, 9, X - 2, W - 1)
    b.zone("cellar", 1, -5, 2, X - 2, W - 1)
    for (x0, x1, (z0, z1), f, _n) in rooms:
        b.zone("quarters", x0, f, z0, x1, z1)
    b.close_air()
    return b


# ------------------------------------------------------------------------------------------------ checks (TDD for the ruling)
def check_rooms(b):
    """The rulings as a test (00:23 + D-GH1007-INN): >= 6 rooms; every room exactly 2 or 4 beds (as SIDE_ROOMS plans it)
    and both kinds present; neighbouring beds exactly one free block apart; every bed's two cells inside its room; a log
    partition (full height) between neighbouring rooms; every room has a door. Returns a list of failures (empty = pass)."""
    fails = []
    rooms = [(x0, x1, zs, f, n) for f in FLOORS for zs in (NORTH, SOUTH) for (x0, x1, n) in SIDE_ROOMS[zs]]
    if len(rooms) < 6:
        fails.append(f"rooms {len(rooms)} < 6")
    if not ({n for *_r, n in rooms} >= {2, 4} and {n for *_r, n in rooms} <= {2, 4}):
        fails.append(f"the mix: room sizes {sorted({n for *_r, n in rooms})} (want 2- and 4-bed rooms only, both)")
    for (x0, x1, (z0, z1), f, n) in rooms:
        heads = sorted(x for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) if b.get(x, f, z) == "minecraft:bed" and
                       b.st.get(x, b.y(f), z)[1]["head_piece_bit"].value)
        if len(heads) != n:
            fails.append(f"room x{x0}-{x1} z{z0}-{z1} f{f}: {len(heads)} beds, planned {n}")
        if x1 + 1 < X - 1:                                               # the partition east of the room (not the outer wall)
            bad = [(x1 + 1, ff, z) for z in range(z0, z1 + 1) for ff in range(f, f + 3) if b.get(x1 + 1, ff, z) != "minecraft:spruce_log"]
            if bad:
                fails.append(f"room x{x0}-{x1} z{z0}-{z1} f{f}: partition x {x1 + 1} open at {bad[:3]}")
        for a, c in zip(heads, heads[1:]):
            if c - a != 2:
                fails.append(f"room x{x0}-{x1} z{z0}-{z1} f{f}: beds at x {a} and {c} are {c - a - 1} blocks apart")
            gap = [b.get(a + 1, f, z) for z in range(z0, z1 + 1)]
            if any(g == "minecraft:bed" for g in gap):
                fails.append(f"room x{x0}-{x1} f{f}: the gap at x {a + 1} holds a bed")
        n_bed_cells = sum(1 for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) if b.get(x, f, z) == "minecraft:bed")
        if n_bed_cells != 2 * len(heads):
            fails.append(f"room x{x0}-{x1} z{z0}-{z1} f{f}: {n_bed_cells} bed cells for {len(heads)} heads")
        wall_z = 5 if z0 == NORTH[0] else 8
        if not any((b.get(x, f, wall_z) or "").endswith("_door") for x in range(x0, x1 + 1)):
            fails.append(f"room x{x0}-{x1} z{z0}-{z1} f{f}: no door")
    # the stair ladder reaches every guest floor; the corridor is clear on every floor
    for f in FLOORS:
        if b.get(LADDER[0], f, LADDER[1]) != "minecraft:ladder":
            fails.append(f"ladder misses floor {f}")
        for x in range(1, X - 1):
            for z in (6, 7):
                n = b.get(x, f, z)
                if n not in ("minecraft:air", "minecraft:ladder", "minecraft:light_block_14"):
                    fails.append(f"corridor blocked at ({x},{f},{z}) by {n}")
    for x in range(1, X - 1):                                            # ground floor: door -> ladder path z 6..7 clear
        for z in (6, 7):
            n = b.get(x, 0, z)
            if n not in ("minecraft:air", "minecraft:ladder", "minecraft:light_block_14"):
                fails.append(f"ground corridor blocked at ({x},0,{z}) by {n}")
    return fails


# ------------------------------------------------------------------------------------------------ plan renders
COL = {"bed_head": (190, 40, 40), "bed_foot": (230, 140, 140), "door": (120, 60, 20), "ladder": (250, 200, 0),
       "planks": (196, 160, 110), "log": (110, 80, 50), "glass": (150, 210, 240), "stone": (140, 140, 140),
       "furn": (90, 140, 70), "store": (60, 90, 160), "hearth": (230, 110, 30), "air": (250, 248, 240), "light": (255, 255, 180),
       "roof": (150, 70, 60), "other": (200, 120, 200)}


def cls(name, states):
    if name == "minecraft:bed":
        return "bed_head" if states["head_piece_bit"].value else "bed_foot"
    if name.endswith("_door"):
        return "door"
    if name == "minecraft:ladder":
        return "ladder"
    if name in ("minecraft:air", "minecraft:structure_void"):
        return "air"
    if name.startswith("minecraft:light_block"):
        return "light"
    if name.endswith("_planks"):
        return "planks"
    if name.endswith("_log"):
        return "log"
    if "glass" in name:
        return "glass"
    if name in ("minecraft:barrel", "minecraft:chest"):
        return "store"
    if name.startswith(("pw:hearth", "pw:flue")):
        return "hearth"
    if name.startswith("pw:furn_"):
        return "furn"
    if name.startswith("pw:roof"):
        return "roof"
    if any(k in name for k in ("stone", "cobble", "brick", "dirt", "grass", "manhole")):
        return "stone"
    return "other"


def render_plan(b, f, title, path, stations):
    """top-down plan of feet level f: camera looking DOWN, north (-z) at the top, the street side (x = 0) on the LEFT."""
    from PIL import Image, ImageDraw, ImageFont
    s = 40
    pad_l, pad_t = 60, 70
    sx, _sy, sz = b.size
    img = Image.new("RGB", (pad_l + sx * s + 280, pad_t + sz * s + 70), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        font = small = ImageFont.load_default()
    d.text((10, 8), title, fill="black", font=font)
    d.text((10, 30), "top-down: camera looking DOWN · local -z (north before rotation) at the top · the street / front door on the LEFT (x = 0)",
           fill=(80, 80, 80), font=small)
    for x in range(sx):
        for z in range(sz):
            p = b.st.get(x, b.y(f), z)
            c = cls(*p[:2]) if p else "air"
            x0, y0 = pad_l + x * s, pad_t + z * s
            d.rectangle([x0, y0, x0 + s - 1, y0 + s - 1], fill=COL[c], outline=(210, 210, 210))
            if c in ("bed_head",):
                d.text((x0 + 12, y0 + 12), "H", fill="white", font=font)
            if c == "door":
                d.text((x0 + 12, y0 + 12), "D", fill="white", font=font)
            if c == "ladder":
                d.text((x0 + 13, y0 + 12), "L", fill="black", font=font)
    for (kind, x, z) in stations:
        x0, y0 = pad_l + x * s, pad_t + z * s
        d.ellipse([x0 + 28, y0 + 2, x0 + 37, y0 + 11], fill=(0, 0, 0))
    for x in range(sx):
        d.text((pad_l + x * s + 14, pad_t - 16), str(x), fill="black", font=small)
    for z in range(sz):
        d.text((pad_l - 22, pad_t + z * s + 14), str(z), fill="black", font=small)
    d.text((pad_l - 52, pad_t + sz * s + 10), "x ->  (depth from the street)", fill="black", font=small)
    ly = pad_t
    for k, c in COL.items():
        d.rectangle([pad_l + sx * s + 20, ly, pad_l + sx * s + 36, ly + 16], fill=c, outline=(0, 0, 0))
        d.text((pad_l + sx * s + 44, ly + 1), {"bed_head": "bed head (H)", "bed_foot": "bed foot"}.get(k, k), fill="black", font=small)
        ly += 22
    d.ellipse([pad_l + sx * s + 22, ly + 4, pad_l + sx * s + 31, ly + 13], fill=(0, 0, 0))
    d.text((pad_l + sx * s + 44, ly + 1), "station marker", fill="black", font=small)
    img.save(path)


def main():
    # 1. the a building + the ruling's test
    R.ROSTER["inn"] = inn2
    b = inn2()
    fails = check_rooms(b)
    print("RULING TEST:", "PASS" if not fails else "FAIL", fails[:10])
    # 1.3.232 (#INN): the rooms table (floor, side, x span, beds)
    for f in FLOORS:
        for zs, side in ((NORTH, "north"), (SOUTH, "south")):
            print(f"  feet {f} {side} z {zs[0]}..{zs[1]}:", "  ".join(f"x {x0}..{x1} {n} beds" for (x0, x1, n) in SIDE_ROOMS[zs]))
    ns = [n for zs in SIDE_ROOMS for (_a, _b, n) in SIDE_ROOMS[zs]] * len(FLOORS)
    print(f"  rooms {len(ns)} = {ns.count(4)} x 4 beds + {ns.count(2)} x 2 beds = {sum(ns)} guest beds")
    if fails:
        raise SystemExit(1)
    # 2. the four skins (a as authored; b/c/d by tools/civ_variants.py rules: the inn keeps its hip form, c -> oak hips)
    builds = [b] + [VAR.build_variant("inn", k) for k in VAR.SKINS]
    (BP / "stages").mkdir(parents=True, exist_ok=True)
    (CIV / "manifests").mkdir(parents=True, exist_ok=True)
    (STAGE_ROOT / "renders").mkdir(parents=True, exist_ok=True)
    for v in builds:
        stem = v.name.split(":")[1]
        v.write(BP / f"{stem}.mcstructure", CIV / "manifests" / f"{stem}.json")
        res, floors = STG.cut(BP / f"{stem}.mcstructure", BP / "stages")
        print(v.name, v.size, "floor rows", floors, [(r[0], r[2]) for r in res])
    # 3. weather overlays (_w / _r) from the new stages
    WO.SRC, WO.OUT = BP / "stages", BP / "stages"
    WO.main()
    # 4. the table entries (civ_village_data rules) + art slots (art_slots rules)
    V.MAN, V.STAGES = CIV / "manifests", BP / "stages"
    tbl = V.table()
    for fam, e in tbl.items():
        st = M.Structure.from_bytes((BP / f"{e['stem']}.mcstructure").read_bytes())
        e["art"] = AS.slots_for(st, e["datum_y"], fam)
    (CIV / "CIV_BUILDINGS-inn.json").write_text(json.dumps(tbl, indent=1))
    for fam, e in tbl.items():
        beds = sum(1 for d in e["dir"] if d[3] == "minecraft:bed") // 2
        print(fam, "size", e["size"], "door", e["door"], "lids", e["lids"], "work", e["work"], "beds", beds,
              "chests", len(e["chests"]), "art", len(e["art"]), "bom", e["bom"])
    # 5. plans per floor (skin a)
    man = json.loads((CIV / "manifests" / "mvv_inn_a_r2.json").read_text())       # 1.3.232 (#INN): the r2 family
    st_by_f = {}
    for e in man["entities"]:
        if e.get("fam") == "station":
            x, f, z = e["cell"]
            st_by_f.setdefault(f, []).append((e["kind"], x, z))
    for f, label in ((-5, "cellar"), (0, "taproom (ground floor)"), (4, "guest floor 1"), (8, "guest floor 2"), (12, "eave / roof ring")):
        render_plan(b, f, f"INN v2 ({b.name}, size {list(b.size)}) — feet {f}: {label}",
                    STAGE_ROOT / "renders" / f"INN-V2-PLAN-f{f}.png", st_by_f.get(f, []))
    print("plans written")


if __name__ == "__main__":
    main()
