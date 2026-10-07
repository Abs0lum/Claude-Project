#!/usr/bin/env python3
"""inn_v2.py — the CIVITAS INN redesigned (BLOCKS round 231; his ruling 00:23 CT 10-07: "two 4 beds to a room, separated by
1 block only, and at least 6 rooms").

ASSUMPTION (stated in the report): every guest room holds 2..4 beds with EXACTLY one block of floor between neighbouring beds,
and the inn has at least 6 guest rooms. This design: 8 rooms x 4 beds (32 guest beds) on two guest floors.

Same shell recipe and contracts as tools/civ_roster.py (it reuses its helpers): the front wall is local x = 0 and faces the
street (the door at x = 0, f = 0, z = ZM, datum marker on it), the clearance column z = 0, feet 0 at structure y 15, the
basement / manhole / sewer port from section(), hip roof, ladder + hatch to the cellar. Only the size grows:
    old  11 deep x 9 front (size [11, 30, 10])      new  17 deep x 12 front (size [17, 34, 13])

  feet -5..-2  cellar: stores (barrels, chests), ladder + hatch up at (1, z 3)
  feet  0..2   taproom: front door z 7 · 4 tables with chairs · hearth + mantel + bench on the back wall · bar (5 shelves) with
               2 barrels behind it · the open corridor z 6..7 from the door to the stair ladder at the back (x 15, z 6)
  feet  4..6   guest floor 1 } each: a corridor z 6..7 (x 1..15) between two partition walls (z 5, z 8); 4 rooms off it:
  feet  8..10  guest floor 2 }   north rooms z 2..4, south rooms z 9..11, each x 1..7 or x 9..15 (partition x 8);
                                 4 beds per room at x = r+0, r+2, r+4, r+6 (a 1-block gap between beds), heads against the
                                 outer wall, an aisle at the foot; one door per room into the corridor; one window per gap
  feet  3, 7, 11 plank floor courses · eave 12 · hip roof (top feet 18)
Doors follow the roster's witnessed convention: in an x-normal wall "south" (the front door), in a z-normal wall "east"/"west".
Beds: direction 2 = head north (head cell at the lower z), 0 = head south (as cottage_m / cottage_l).

Outputs (all under /home/claude/_staging/blocks231):
  BP-02/structures/pw/mvv_inn_{a,b,c,d}_r1.mcstructure          the finished buildings (skins via tools/civ_variants.py)
  BP-02/structures/pw/stages/mvv_inn_{a..d}_r1_s0..s4 + _w / _r  the 5 build stages (tools/civ_stages.py) + weather overlays
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
ROOMS_X = ((1, 7), (9, 15))        # room spans along x (partition at x = 8)
NORTH, SOUTH = (2, 4), (9, 11)     # room spans along z; corridor z 6..7 between partitions z 5 and z 8
BEDS_PER_ROOM = 4


def bed_xs(x0):
    """4 beds with exactly one free block between neighbours: x0, x0+2, x0+4, x0+6."""
    return [x0 + 2 * k for k in range(BEDS_PER_ROOM)]


def guest_floor(b, f):
    """partitions, doors, beds, windows and lights of one guest floor at feet f (f .. f+2 open, f+3 the next course)."""
    for x in range(1, X - 1):                                            # corridor walls z 5 and z 8
        for ff in range(f, f + 3):
            b.put(x, ff, 5, "minecraft:oak_planks")
            b.put(x, ff, 8, "minecraft:oak_planks")
    for (z0, z1) in (NORTH, SOUTH):                                      # the partition between the two rooms of a side
        for z in range(z0, z1 + 1):
            for ff in range(f, f + 3):
                b.put(8, ff, z, "minecraft:spruce_log", pillar_axis="y")
    beds, rooms = [], []
    for (x0, x1) in ROOMS_X:
        dx = x0 + 3                                                       # the room door: opposite the 2nd gap
        R.door(b, dx, f, 5, "east", wood="spruce")                        # north room door in the z-normal wall z 5
        R.door(b, dx, f, 8, "west", wood="spruce")                        # south room door in the z-normal wall z 8
        for bx in bed_xs(x0):
            # north room: head against the north wall (z 2), foot z 3, aisle z 4
            b.put(bx, f, 2, "minecraft:bed", direction=2, head_piece_bit=True, occupied_bit=False)
            b.put(bx, f, 3, "minecraft:bed", direction=2, head_piece_bit=False, occupied_bit=False)
            # south room: head against the south wall (z 11), foot z 10, aisle z 9
            b.put(bx, f, 11, "minecraft:bed", direction=0, head_piece_bit=True, occupied_bit=False)
            b.put(bx, f, 10, "minecraft:bed", direction=0, head_piece_bit=False, occupied_bit=False)
            beds += [(bx, f, 2), (bx, f, 11)]
        for gx in (x0 + 1, x0 + 3, x0 + 5):                              # windows in the gaps (above the floor, beside the heads)
            b.put(gx, f + 1, 1, "minecraft:glass_pane")
            b.put(gx, f + 1, W, "minecraft:glass_pane")
        rooms += [(x0, x1, NORTH), (x0, x1, SOUTH)]
    R.lights(b, [(x0 + 3, f + 2, 3) for (x0, _x1) in ROOMS_X] + [(x0 + 3, f + 2, 10) for (x0, _x1) in ROOMS_X]
             + [(4, f + 2, 6), (12, f + 2, 7)])
    return beds, rooms


def inn2(name="pw:mvv_inn_a_r1"):
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
        rooms += [(x0, x1, zs, f) for (x0, x1, zs) in rr]
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
    for (x0, x1, (z0, z1), f) in rooms:
        b.zone("quarters", x0, f, z0, x1, z1)
    b.close_air()
    return b


# ------------------------------------------------------------------------------------------------ checks (TDD for the ruling)
def check_rooms(b):
    """The ruling as a test: >= 6 rooms; each room 2..4 beds; neighbouring beds exactly one free block apart; every bed's
    two cells inside its room; every room has a door. Returns a list of failures (empty = pass)."""
    fails = []
    rooms = [(x0, x1, zs, f) for f in FLOORS for (x0, x1) in ROOMS_X for zs in (NORTH, SOUTH)]
    if len(rooms) < 6:
        fails.append(f"rooms {len(rooms)} < 6")
    for (x0, x1, (z0, z1), f) in rooms:
        heads = sorted(x for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) if b.get(x, f, z) == "minecraft:bed" and
                       b.st.get(x, b.y(f), z)[1]["head_piece_bit"].value)
        if not 2 <= len(heads) <= 4:
            fails.append(f"room x{x0}-{x1} z{z0}-{z1} f{f}: {len(heads)} beds")
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
    man = json.loads((CIV / "manifests" / "mvv_inn_a_r1.json").read_text())
    st_by_f = {}
    for e in man["entities"]:
        if e.get("fam") == "station":
            x, f, z = e["cell"]
            st_by_f.setdefault(f, []).append((e["kind"], x, z))
    for f, label in ((-5, "cellar"), (0, "taproom (ground floor)"), (4, "guest floor 1"), (8, "guest floor 2"), (12, "eave / roof ring")):
        render_plan(b, f, f"INN v2 (pw:mvv_inn_a_r1, size {list(b.size)}) — feet {f}: {label}",
                    STAGE_ROOT / "renders" / f"INN-V2-PLAN-f{f}.png", st_by_f.get(f, []))
    print("plans written")


if __name__ == "__main__":
    main()
