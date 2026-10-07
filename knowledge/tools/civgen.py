#!/usr/bin/env python3
"""civgen.py — CIVITAS building generator: a building spec -> a Bedrock .mcstructure (blocks + marker entities)
+ a manifest (what the in-game / BDS verifier checks). Phase B of CIVITAS-STRUCTURE-BUILD-PLAN-2026-10-02.

COORDINATES (local, his cottage r0 is the reference save):
  x = depth from the street: x = 0 is the FRONT wall (the door is in it), x grows away from the street.
  z = frontage: z = 0 is the one clearance column (his r0 keeps it at z = 0); the building is z = 1 .. W.
  y = box index; DATUM_Y (= 15, as in r0) is feet 0 = the sidewalk = the ground floor. y - DATUM_Y = 'feet' level.
  The box runs from feet -15 (two dirt rows under the -13/-12 smooth-stone foundation, as r0) to the top of the roof.
SECTION (BUILD-PLAN 09-07, as built in r0): basement floor course -6 (stone bricks) with the manhole, basement clear
  -5..-2, ground floor course -1, shaft ladder -12..-7 beside the manhole, the sewer port at -10 in the front cell.
MARKERS are pw:marker ENTITIES inside the file (MARKER-ENTITIES-v1: properties pw:fam / pw:icon / pw:n / pw:vis +
  tags civ:marker, civ:<fam>, civ:kind:<kind>, civ:n:<n>), cloned from the engine's own NBT (BDS probe 2026-10-02,
  tools/civ_templates/engine_entities_probe.nbt). Zone corners: one ring per room, counter-clockwise seen from above
  (NW -> SW -> SE -> NE), n = ring * 16 + corner. The ladder hatch is the pw:hatch_lid entity on the top ladder.
STATE TYPES: python bool -> TAG_Byte, int -> TAG_Int, str -> TAG_String (matches his saves and the engine read-back)."""
import copy
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

DATUM_Y = 15
TEMPLATES = Path("/home/claude/tools/civ_templates/engine_entities_probe.nbt")
ICON = {  # MARKER-ENTITIES-v1 frozen icon table (append-only)
    "zone:threshold": 0, "zone:stable": 1, "zone:cellar": 2, "zone:storeroom": 3, "zone:kitchen": 4, "zone:quarters": 5,
    "zone:chamber": 6, "zone:workfloor": 7, "zone:shopfloor": 8, "zone:yard": 9, "zone:garden": 10, "zone:commons": 11,
    "station:anvil": 12, "station:bed": 13, "station:bench": 14, "station:counter": 15, "station:desk": 16,
    "station:door": 17, "station:field": 18, "station:hearth": 19, "station:oven": 20, "station:pen": 21,
    "station:post": 22, "station:prep": 23, "station:rack": 24, "station:seat": 25, "station:stall": 26,
    "station:store": 27, "station:table": 28, "station:yard": 29, "port:passage": 30, "port:sewer": 31,
    "port:stair": 32, "port:well": 33, "datum:datum": 34}
FAM = {"zone": 0, "station": 1, "port": 2, "datum": 3}
HINGE_FROM_LADDER = {2: 0, 5: 1, 3: 2, 4: 3}       # pw_markers.js: ladder facing_direction -> world hinge side


def _typed(states):
    out = {}
    for k, v in (states or {}).items():
        if isinstance(v, M.Tag):
            out[k] = v
        elif isinstance(v, bool):
            out[k] = M.b(v)
        elif isinstance(v, int):
            out[k] = M.i(v)
        else:
            out[k] = M.s(v)
    return out


def wall_ring(b, cells, feet, name="minecraft:stone_brick_wall"):
    """a run / ring of WALL blocks with their connection states written out: Bedrock walls carry their connections as
    block states (wall_connection_type_<dir>: none / short / tall, wall_post_bit) and a structure-placed wall is never
    re-evaluated against its neighbours — four lone posts never close into a parapet (his 08:55 CT 10-05, the well).
    cells: (x, z) pairs at `feet`; a cell connects to every listed 4-neighbour; a corner or an end is a post."""
    cs = set(cells)
    for (x, z) in cells:
        e, w, s_, n = (x + 1, z) in cs, (x - 1, z) in cs, (x, z + 1) in cs, (x, z - 1) in cs
        straight = (e and w and not s_ and not n) or (s_ and n and not e and not w)
        b.put(x, feet, z, name, wall_connection_type_east="short" if e else "none", wall_connection_type_west="short" if w else "none",
              wall_connection_type_south="short" if s_ else "none", wall_connection_type_north="short" if n else "none",
              wall_post_bit=not straight)


def _entity_templates():
    st = M.Structure.from_bytes(TEMPLATES.read_bytes())
    by_id = {e.value["identifier"].value: e for e in st.entities}
    return by_id["pw:marker"], by_id["pw:hatch_lid"]


class Building:
    """A save box being filled. put() takes FEET levels (relative to the datum), not box indices."""

    def __init__(self, name, depth, width, top_feet, bottom_feet=-15):
        self.name = name
        self.depth, self.width = depth, width
        self.bottom = bottom_feet
        self.size = (depth, top_feet - bottom_feet + 1, width + 1)     # + the clearance column z = 0
        self.st = M.Structure(self.size)
        self.markers = []            # manifest records
        self._uid = 0
        self._ring = {}              # zone kind -> next ring
        self._station_n = {}         # station / port role -> next index
        self._marker_tpl, self._lid_tpl = _entity_templates()

    # ---------------------------------------------------------------- blocks
    def y(self, feet):
        return feet - self.bottom

    def put(self, x, feet, z, name, waterlogged=False, **states):
        self.st.set(x, self.y(feet), z, name, _typed(states), waterlogged)

    def fill(self, x0, f0, z0, x1, f1, z1, name, **states):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for f in range(min(f0, f1), max(f0, f1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.put(x, f, z, name, **states)

    def get(self, x, feet, z):
        p = self.st.get(x, self.y(feet), z)
        return None if p is None else p[0]

    # ---------------------------------------------------------------- entities
    def _next_uid(self):
        self._uid += 1
        return -(0x5057 << 32) - self._uid                         # 'PW' high word; unique inside the file

    def _entity(self, tpl, pos, props, tags, definitions):
        e = copy.deepcopy(tpl)
        v = e.value
        v["Pos"] = M.lst(M.FLOAT, [M.f(c) for c in pos])
        v["UniqueID"] = M.Tag(M.LONG, self._next_uid())
        v["Tags"] = M.lst(M.STRING, [M.s(t) for t in tags])
        v["definitions"] = M.lst(M.STRING, [M.s(d) for d in definitions])
        p = v["properties"].value
        for k, val in props.items():
            p[k] = M.b(val) if isinstance(val, bool) else M.i(val)
        self.st.entities.append(e)

    def marker(self, fam, kind, x, feet, z, n=None):
        """One pw:marker at the cell's floor centre. n: zone corner number (given) or the next station/port index."""
        if n is None:
            key = f"{fam}:{kind}"
            n = self._station_n.get(key, 0)
            self._station_n[key] = n + 1
        icon = ICON[f"{fam}:{kind}"]
        pos = (x + 0.5, self.y(feet), z + 0.5)
        self._entity(self._marker_tpl, pos, {"pw:fam": FAM[fam], "pw:icon": icon, "pw:n": n, "pw:vis": True},
                     ["civ:marker", f"civ:{fam}", f"civ:kind:{kind}", f"civ:n:{n}"], ["+pw:marker", "+pw:hittable"])
        self.markers.append({"id": "pw:marker", "fam": fam, "kind": kind, "n": n, "cell": [x, feet, z]})

    def zone(self, kind, x0, feet, z0, x1, z1):
        """A rectangular room's ring: corners counter-clockwise seen from above, NW -> SW -> SE -> NE."""
        ring = self._ring.get(kind, 0)
        self._ring[kind] = ring + 1
        xa, xb, za, zb = min(x0, x1), max(x0, x1), min(z0, z1), max(z0, z1)
        assert xb > xa and zb > za, f"zone {kind}: a ring needs at least 2 x 2 cells (V6), got x {xa}..{xb} z {za}..{zb}"
        for idx, (x, z) in enumerate([(xa, za), (xa, zb), (xb, zb), (xb, za)]):
            self.marker("zone", kind, x, feet, z, n=ring * 16 + idx)

    def hatch(self, x, feet, z, ladder_facing):
        """The ladder-hatch lid (entity) closing the top of the ladder cell at (x, feet, z)."""
        hinge = HINGE_FROM_LADDER[ladder_facing]
        self._entity(self._lid_tpl, (x + 0.5, self.y(feet) + 0.8125, z + 0.5), {"pw:hinge": hinge, "pw:open": False},
                     [], ["+pw:hatch_lid", "+pw:lid_closed"])
        self.markers.append({"id": "pw:hatch_lid", "hinge": hinge, "cell": [x, feet, z]})

    def close_air(self):
        """Every cell nothing was put in becomes air: the save box always clears its whole volume (no stray trees,
        snow or terrain left inside a placed building)."""
        sx, sy, sz = self.size
        for x in range(sx):
            for y in range(sy):
                for z in range(sz):
                    if self.st.get(x, y, z) is None:
                        self.st.set(x, y, z, "minecraft:air", {})

    # ---------------------------------------------------------------- output
    def manifest(self):
        blocks = []
        sx, sy, sz = self.size
        for x in range(sx):
            for y in range(sy):
                for z in range(sz):
                    p = self.st.get(x, y, z)
                    if p is not None:
                        blocks.append([x, y, z, p[0], {k: v.value for k, v in p[1].items()}])
        return {"name": self.name, "size": list(self.size), "datum_y": -self.bottom, "blocks": blocks,
                "entities": self.markers}

    def write(self, mcstructure_path, manifest_path):
        Path(mcstructure_path).parent.mkdir(parents=True, exist_ok=True)
        Path(mcstructure_path).write_bytes(self.st.to_bytes())
        Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)
        Path(manifest_path).write_text(json.dumps(self.manifest(), separators=(",", ":")))


# ==================================================================================================== the cottage
def cottage(name="pw:mvv_cottage_s_a_r1", depth=8, width=6, seed=1):
    """Cottage S (his r0 at the +1 rule: 5 x 7 -> 6 frontage x 8 deep). One storey + loft under a 45-degree gable roof
    (ridge along the depth), basement with the ladder hatch, manhole, shaft and sewer port. Canonical palette: spruce
    log corner posts, oak plank walls, stone-brick basement, cobblestone footing, spruce 45 roof. Heights as his r0
    (ground floor clear 0..2, loft floor course +3, loft from +4, eaves +5)."""
    rnd = random.Random(seed)
    X, W = depth, width
    xf, xb, zl, zr = 0, X - 1, 1, W                     # front wall, back wall, left (north) wall, right (south) wall
    zmid = 1 + W // 2 - 1                               # the door column (z = 3 for W = 6)
    eave = 5
    half = W // 2                                       # slope rows per side
    top = eave + half                                   # one row above the roof peak (the peak is at eave + half - 1)
    b = Building(name, X, W, top_feet=top)

    # ---- ground below everything (box bottom -15 .. -14 dirt, -13 .. -12 smooth stone foundation, as r0)
    b.fill(0, -15, 0, X - 1, -14, W, "minecraft:dirt")
    b.fill(0, -13, 0, X - 1, -12, W, "minecraft:smooth_stone")
    b.fill(0, -11, 0, X - 1, -7, W, "minecraft:dirt")
    # basement shell: floor course -6, walls -6 .. -2 (stone bricks), clear -5 .. -2
    b.fill(0, -6, 0, X - 1, -1, 0, "minecraft:dirt")                       # clearance column, below grade
    b.fill(xf, -6, zl, xb, -6, zr, "minecraft:stone_bricks")
    b.fill(xf, -5, zl, xb, -2, zr, "minecraft:stone_bricks")
    b.fill(xf + 1, -5, zl + 1, xb - 1, -2, zr - 1, "minecraft:air")
    # ground floor course -1: oak planks inside, cobblestone footing ring; grass in the clearance column
    b.fill(xf, -1, zl, xb, -1, zr, "minecraft:cobblestone")
    b.fill(xf + 1, -1, zl + 1, xb - 1, -1, zr - 1, "minecraft:oak_planks")
    b.fill(0, -1, 0, X - 1, -1, 0, "minecraft:grass_block")
    # the clearance column above grade stays open air
    b.fill(0, 0, 0, X - 1, top, 0, "minecraft:air")

    # ---- shaft, manhole, sewer port (front of the basement, r0 layout)
    sx, sz = xf + 1, zmid
    b.put(sx, -6, sz, "pw:manhole_cover", **{"pw:phase": 0, "pw:skin": 0})
    for f in range(-12, -6):
        b.put(sx, f, sz, "minecraft:ladder", facing_direction=4)
    b.put(xf, -10, sz, "minecraft:air")
    b.put(xf, -9, sz, "minecraft:air")
    b.marker("port", "sewer", xf, -10, sz)

    # ---- walls: posts at the four corners, oak plank infill, from feet 0 to the eave course (+4)
    for f in range(0, eave):
        for x in range(xf, xb + 1):
            b.put(x, f, zl, "minecraft:oak_planks")
            b.put(x, f, zr, "minecraft:oak_planks")
        for z in range(zl, zr + 1):
            b.put(xf, f, z, "minecraft:oak_planks")
            b.put(xb, f, z, "minecraft:oak_planks")
        for (x, z) in [(xf, zl), (xf, zr), (xb, zl), (xb, zr)]:
            b.put(x, f, z, "minecraft:spruce_log", pillar_axis="y")
    b.fill(xf + 1, 0, zl + 1, xb - 1, eave - 1, zr - 1, "minecraft:air")
    # loft floor course +3 (oak planks), loft clear from +4
    b.fill(xf + 1, 3, zl + 1, xb - 1, 3, zr - 1, "minecraft:oak_planks")

    # ---- gable roof, ridge along the depth: slope rows step up one per cell from each side wall
    for k in range(half):
        f = eave + k
        for x in range(xf, xb + 1):
            b.put(x, f, zl + k, "pw:roof45_spruce", **{"minecraft:cardinal_direction": "north", "minecraft:vertical_half": "bottom"})
            b.put(x, f, zr - k, "pw:roof45_spruce", **{"minecraft:cardinal_direction": "south", "minecraft:vertical_half": "bottom"})
        # under the slope: gable wall cells at both ends, attic air inside
        for z in range(zl + k + 1, zr - k):
            for x in (xf, xb):
                b.put(x, f, z, "minecraft:oak_planks")
            for x in range(xf + 1, xb):
                b.put(x, f, z, "minecraft:air")
    # gable windows (loft light), front and back
    b.put(xf, eave, zmid, "minecraft:glass_pane")
    b.put(xb, eave, zmid + 1, "minecraft:glass_pane")

    # ---- door, windows
    b.put(xf, 0, zmid, "minecraft:wooden_door", door_hinge_bit=False, open_bit=False, upper_block_bit=False,
          **{"minecraft:cardinal_direction": "south"})
    b.put(xf, 1, zmid, "minecraft:wooden_door", door_hinge_bit=False, open_bit=False, upper_block_bit=True,
          **{"minecraft:cardinal_direction": "south"})
    for (x, z) in [(3, zl), (X - 3, zr), (2, zr), (xb, zmid + 1)]:      # (back window kept off the ladder's wall cell)
        b.put(x, 1, z, "minecraft:glass_pane")
    b.put(xf, 1, zmid + 2, "minecraft:glass_pane")                 # front window beside the door

    # ---- hearth + flue in the left (north) wall, mantel in front, cap above the roof
    hx = X - 3
    b.put(hx, 0, zl, "pw:hearth_oak_planks", **{"minecraft:cardinal_direction": "south", "pw:phase": "cold"})
    for f in range(1, eave + 1):
        b.put(hx, f, zl, "pw:flue_oak_planks", **{"pw:cap": False})
    b.put(hx, eave + 1, zl, "pw:flue_oak_planks", **{"pw:cap": True})
    b.put(hx, 1, zl + 1, "pw:furn_mantel_oak", **{"minecraft:cardinal_direction": "south"})

    # ---- ground floor furniture: table + two chairs, cupboard, stool by the hearth, coat pegs by the door
    tx, tz = 3, zr - 1
    b.put(tx, 0, tz, "pw:furn_table_oak", **{"pw:n": False, "pw:e": False, "pw:s": False, "pw:w": False})
    b.put(tx - 1, 0, tz, "pw:furn_chair_oak", **{"minecraft:cardinal_direction": "east"})
    b.put(tx + 1, 0, tz, "pw:furn_chair_oak", **{"minecraft:cardinal_direction": "west"})
    b.put(xb - 1, 0, zr - 1, "pw:furn_cupboard_oak", **{"minecraft:cardinal_direction": "west"})
    b.put(hx - 1, 0, zl + 1, "pw:furn_stool_oak", **{"minecraft:cardinal_direction": "south"})
    b.put(xf + 1, 1, zl + 1, "pw:furn_coat_pegs_oak", **{"minecraft:cardinal_direction": "east"})

    # ---- ladder to the loft (against the back wall), through the loft floor course
    lx, lz = xb - 1, zl + 2
    for f in range(0, 4):
        b.put(lx, f, lz, "minecraft:ladder", facing_direction=4)

    # ---- ladder + hatch to the basement (against the back wall, other side), top ladder in the floor course -1
    cx, cz = xb - 1, zr - 2
    for f in range(-5, 0):
        b.put(cx, f, cz, "minecraft:ladder", facing_direction=4)
    b.hatch(cx, -1, cz, ladder_facing=4)

    # ---- basement: barrels + chests along the walls
    b.put(xf + 2, -5, zl + 1, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(xf + 3, -5, zl + 1, "minecraft:barrel", facing_direction=1, open_bit=False)
    b.put(xf + 2, -5, zr - 1, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})
    b.put(xf + 3, -5, zr - 1, "minecraft:chest", **{"minecraft:cardinal_direction": "north"})

    # ---- loft: bed (head toward the front gable), chest, wall shelf, chair
    bx, bz = xf + 1, zmid
    b.put(bx, 4, bz, "minecraft:bed", direction=1, head_piece_bit=True, occupied_bit=False)
    b.put(bx + 1, 4, bz, "minecraft:bed", direction=1, head_piece_bit=False, occupied_bit=False)
    b.put(bx, 4, bz + 1, "minecraft:chest", **{"minecraft:cardinal_direction": "east"})
    b.put(bx, 4, bz - 1, "pw:furn_wall_shelf_oak", **{"minecraft:cardinal_direction": "east"})

    # ---- light (level 14 light blocks, like r0): one per room at its ceiling
    for (x, f, z) in [(3, 2, zmid), (X - 3, 2, zmid + 1), (3, -2, zmid), (X - 3, 5, zmid + 1)]:
        if b.get(x, f, z) == "minecraft:air":
            b.put(x, f, z, "minecraft:light_block_14")

    # ---- markers: datum, stations, zones
    b.marker("datum", "datum", xf, 0, zmid, n=0)
    b.marker("station", "door", xf, 0, zmid)
    # STATION LAW (MARKER-ENTITIES-v1 "sneak-tap = the block's OWN cell"; AUTHORING-WORKFLOW §6.2 "place it where the
    # oven is"; D-C493): a fixture station sits IN its fixture's cell; the villager's standing cell is derived from it.
    b.marker("station", "hearth", hx, 0, zl)
    b.marker("station", "table", tx, 0, tz)
    b.marker("station", "seat", tx - 1, 0, tz)
    b.marker("station", "seat", tx + 1, 0, tz)
    b.marker("station", "seat", hx - 1, 0, zl + 1)                 # the stool by the hearth
    b.marker("station", "store", xb - 1, 0, zr - 1)                # the cupboard
    b.marker("station", "store", xf + 2, -5, zl + 1)               # the cellar barrels
    b.marker("station", "store", xf + 2, -5, zr - 1)               # the cellar chests
    b.marker("station", "bed", bx, 4, bz)
    b.marker("station", "store", bx, 4, bz + 1)                    # the loft chest
    b.zone("threshold", xf + 1, 0, zmid, xf + 2, zmid + 1)
    b.zone("kitchen", xf + 1, 0, zl + 1, xb - 1, zr - 1)
    b.zone("cellar", xf + 1, -5, zl + 1, xb - 1, zr - 1)
    b.zone("quarters", xf + 1, 4, zl + 1, xb - 1, zr - 1)
    _ = rnd
    b.close_air()
    return b


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/_staging/civ")
    c = cottage()
    c.write(out / "structures/pw/mvv_cottage_s_a_r1.mcstructure", out / "manifests/mvv_cottage_s_a_r1.json")
    m = c.manifest()
    print(c.name, "size", c.size, "blocks", len(m["blocks"]), "palette", len(c.st.palette), "entities", len(c.st.entities))
