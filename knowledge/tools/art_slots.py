#!/usr/bin/env python3
"""art_slots.py — where pictures can hang in a building template (the GALLERY, D-C571 v2): an offline scan of a
template's final stage for interior wall rectangles with free air in front, turned into ART SLOTS the clock fills with
unique works at the furnished stage. Deterministic, zero runtime cost.

A slot = [cx, yb, cz, w, h, facing, subject]: cx / cz the picture's centre in LOCAL float coordinates (cell i spans
[i, i + 1)), yb the bottom row in feet (relative to the datum), w x h in blocks (a frame class), facing = the way the
picture faces (0 north -z, 1 east +x, 2 south +z, 3 west -x; the wall is behind it), subject = a hint for the pick
("any" lets the registry choose). The clock rotates the slot with the building (floats: r1 (X,Z)->(sz-Z, X)).

Rules: a wall cell is a full solid block (WALLS); the front cell (one step toward the room) is air (light blocks count as
air); the front cell is indoors (something solid within 6 above) with a floor under the rectangle's bottom row; the
rectangle's front cells are all air and at least DEPTH(w) cells of air lie in front (room to step back); rectangles are
taken largest first with a one-cell margin; per-building caps by family; subjects by family (SUBJECT_OF).
Usage (module): slots_for(structure, datum_y, family, cap=None, room_of=None) -> list of slots
Usage (CLI):    art_slots.py STRUCTURE.mcstructure DATUM FAMILY   (prints the slots)
Complexity: O(cells) for the masks + O(cells x classes) for the rectangle scan."""
import re
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

WALLS = re.compile(r"^minecraft:(?:[a-z_]+_planks|[a-z_]+_log|[a-z_]+_wood|stone_bricks|chiseled_stone_bricks|mossy_stone_bricks|cobblestone|"
                   r"mossy_cobblestone|smooth_stone|stone|bricks|polished_andesite|polished_granite|polished_diorite|andesite|granite|diorite|"
                   r"deepslate_bricks|deepslate_tiles|polished_deepslate|tuff|sandstone|smooth_sandstone|cut_sandstone|mud_bricks|packed_mud|"
                   r"[a-z]+_terracotta|terracotta|quartz_block|chiseled_quartz_block|smooth_quartz|[a-z]+_concrete)$")
AIRLIKE = ("minecraft:air", "minecraft:light_block_14", "minecraft:light_block_15", "minecraft:light_block_12", "minecraft:light_block_10", "minecraft:structure_void")
CLASSES = [(4, 6), (6, 4), (4, 5), (5, 4), (3, 4), (4, 3), (3, 3), (2, 3), (3, 2), (2, 2), (1, 2), (2, 1), (1, 1)]
# the room is behind the picture's viewer: a w-wide picture wants (w - 1) cells of air in front, 1..3
DEPTH = lambda w: max(1, min(3, w - 1))
DIRS = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}         # facing -> (dx, dz) from the wall INTO the room
CAP = {"cottage": 2, "house": 3, "townhouse": 5, "inn": 8, "tavern": 6, "manor": 16, "chapel": 6, "church": 8, "hall": 10,
       "school": 4, "bakery": 2, "butcher": 1, "smithy": 1, "quarry": 0, "lumberyard": 0, "farm": 0, "well": 0, "market": 2,
       "watch": 3, "palace": 70, "shop": 2, "mill": 1, "stable": 0, "barn": 0}
SUBJECT_OF = {"chapel": "religious", "church": "religious", "inn": "genre", "tavern": "genre", "bakery": "still_life", "butcher": "still_life",
              "manor": "any", "townhouse": "any", "hall": "myth_history", "school": "landscape", "watch": "portrait", "palace": "any"}


def family_word(family):
    s = family.replace("pw:mvv_", "")
    for w in CAP:
        if s.startswith(w):
            return w
    return s.split("_")[0]


def slots_for(st, datum_y, family, cap=None, room_of=None, subject=None):
    sx, sy, sz = st.size
    fam = family_word(family)
    cap = CAP.get(fam, 2) if cap is None else cap
    subj = subject or SUBJECT_OF.get(fam, "any")
    if cap <= 0:
        return []

    def name(x, y, z):
        if not (0 <= x < sx and 0 <= y < sy and 0 <= z < sz):
            return None
        e = st.get(x, y, z)
        return e[0] if e else "minecraft:structure_void"

    def is_air(x, y, z):
        n = name(x, y, z)
        return n in AIRLIKE

    def is_wall(x, y, z):
        n = name(x, y, z)
        return bool(n) and WALLS.match(n) is not None

    def indoors(x, y, z):
        """a roof or ceiling within 6 above the front cell"""
        for k in range(1, 7):
            n = name(x, y + k, z)
            if n is None:
                return False
            if n not in AIRLIKE:
                return True
        return False

    def floor_under(x, y, z):
        """the first solid under (x, y, z) within 4 rows -> its y (or None)"""
        for k in range(1, 5):
            n = name(x, y - k, z)
            if n is None:
                return None
            if n not in AIRLIKE:
                return y - k
        return None

    out, used = [], set()                       # used: (facing, along, y, plane) wall cells already taken (+ margins)
    for facing, (dx, dz) in DIRS.items():
        # the candidate mask: wall cell with an indoor air front cell
        mask = {}
        for x in range(sx):
            for y in range(datum_y, sy):
                for z in range(sz):
                    if not is_wall(x, y, z):
                        continue
                    fx, fz = x + dx, z + dz
                    if not is_air(fx, y, fz) or not indoors(fx, y, fz):
                        continue
                    along, plane = (x, z) if dz else (z, x)
                    mask[(along, y, plane)] = (fx, fz)
        for (w, h) in CLASSES:
            depth = DEPTH(w)
            for (along, y, plane), (fx, fz) in sorted(mask.items(), key=lambda kv: (kv[0][2], kv[0][1], kv[0][0])):
                # the rectangle: along .. along + w - 1, rows y .. y + h - 1 (y = bottom row)
                ok = True
                for a in range(along, along + w):
                    for r in range(y, y + h):
                        if (a, r, plane) not in mask or (facing, a, r, plane) in used:
                            ok = False; break
                        wx, wz = (a, plane) if dz else (plane, a)
                        for d in range(1, depth + 1):            # air to step back
                            if not is_air(wx + dx * d, r, wz + dz * d):
                                ok = False; break
                        if not ok:
                            break
                    if not ok:
                        break
                if not ok:
                    continue
                # a floor under the bottom row's front cells, the picture's bottom at least one row above it
                floors = []
                for a in range(along, along + w):
                    wx, wz = (a, plane) if dz else (plane, a)
                    f = floor_under(wx + dx, y, wz + dz)
                    if f is None:
                        floors = None; break
                    floors.append(f)
                if not floors or y - max(floors) < 2 or y - min(floors) > 3:      # never on the floor: the bottom row is >= 1 above it
                    continue
                # accept: centre of the front cells
                if dz:                                            # wall runs along x; the picture faces +-z
                    cx = along + w / 2.0
                    cz = (plane + dz) + 0.5
                else:                                             # wall runs along z; the picture faces +-x
                    cz = along + w / 2.0
                    cx = (plane + dx) + 0.5
                yb = y - datum_y
                s = subj
                if room_of:
                    s = room_of(cx, y, cz) or s
                out.append([round(cx, 2), yb, round(cz, 2), w, h, facing, s])
                for a in range(along - 1, along + w + 1):
                    for r in range(y - 1, y + h + 1):
                        used.add((facing, a, r, plane))
    # the biggest pictures first (a state room gets its canvases, a corridor its cabinet pieces), then the cap
    out.sort(key=lambda sl: (-(sl[3] * sl[4]), sl[1], sl[0], sl[2]))
    return out[:cap]


if __name__ == "__main__":
    st = M.Structure.from_bytes(Path(sys.argv[1]).read_bytes())
    sl = slots_for(st, int(sys.argv[2]), sys.argv[3])
    print(len(sl), "slots")
    for s in sl:
        print(s)
