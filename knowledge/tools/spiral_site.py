#!/usr/bin/env python3
"""spiral_site.py — program 228: lay a SPIRAL STAIR of our custom blocks into a generator's model (palacegen / castlegen:
any civgen.Building — put(x, feet, z, name, **states), get(x, feet, z)).

His rules carried here:
  * 14:21  sizes: A turret (2 x 2 well) for tight defensive towers, B tower (4 x 4) for ordinary stairs, C grand (6 x 6) for
           palaces' main towers, castles, manors (16:30: palace = C in the main towers, B on the back stairs).
  * 14:44  the stair ENDS at the floor: one quarter turn rises exactly 1 block, so a stair from walking level f0 to a floor
           whose walking level is S runs S - f0 quarters and the head tread is flush with the floor (no remainder on the
           block grid; spiral_gen.fit_floors guards it).
  * 15:06  the TOP floor lies IN FRONT of the head: the first quarter ahead of the last step (over the turn below: 2.0 to
           2.75 blocks of headroom, his >= 2-block law, 15:1x) running on as a hallway LAND_DEPTH beyond the well; the
           second quarter ahead stays open.
  * 16:30  MID floors: a doorway BESIDE the step — the quarter level with that floor is an END piece (its rail stops at its
           end post), the next quarter a START piece (its newel post); the opening is cut through the well's outer side at
           that step and floored at the storey's level.
  * engine (16:22 probe): the structure is rotated by the town, never mirrored; ids are lowercase.

Frames: the generator's model frame is the structure frame (x east, z south, feet up). The helix centre is the grid
CORNER at (x0 + n, z0 + n), x0, z0 = the NW cell of the 2n x 2n well. A quarter k sits at feet f0 + k and turns
b = +90 (k0 + k) for the ccw hand (seen from above while climbing), -90 (k0 + k) for cw (spiral_pack's pad, witnessed on
BDS as the engine-law render). k0 picks which way the foot faces.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import spiral_gen as SG  # noqa: E402

CELLS_OF = json.loads(Path("/home/claude/_staging/spiral228/rp/cells_of.json").read_text())
DIR_OF_B = {0: "south", 90: "east", 180: "north", 270: "west"}
AIR = "minecraft:air"


def block_id(design, pal):
    return f"pw:spiral_stairs_{design.lower()}_{pal}"


def rw(x, z, b):
    a = math.radians(b)
    return x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)


def to_cell(cx, cz, px, pz, b):
    """a design-frame point (px, pz, in px from the helix centre) -> the model cell, through M (file x mirrored) then Rw(b)"""
    wx, wz = rw(-px, pz, b)
    return cx + math.floor(wx / 16), cz + math.floor(wz / 16)


def plan(x0, z0, f0, floors, design, hand="ccw", k0=0):
    """the stair as data (pure). floors = the walking levels (feet) of the storeys above f0, the last = the top.
    Returns {cells: [(x, feet, z, states)], well: (x0, z0, x1, z1), quarters, doors: [{feet, cell, step}], landing: [(x, feet, z)],
    top}; doors[i].cell = the cell just outside the well beside the step level with a mid floor; landing = the floor in front."""
    n = SG.DESIGNS[design]["n"]
    floors = sorted(floors)
    top = floors[-1]
    q, yfoot, bridge = SG.fit_floors(f0, top)
    assert yfoot == f0 and bridge == 0 and q == top - f0, (f0, top, q, yfoot, bridge)
    mids = [S - f0 - 1 for S in floors[:-1]]
    for a in mids:
        assert 1 <= a < q - 2, f"a mid floor too close to the foot or the top: {floors} from {f0}"
    sgn = 1 if hand == "ccw" else -1
    dh = "r" if hand == "ccw" else "l"
    cx, cz = x0 + n, z0 + n
    cells, doors = [], []
    for k in range(q):
        part = "start" if (k == 0 or (k - 1) in mids) else ("end" if k == q - 1 else ("door" if k in mids else "mid"))
        b = (sgn * 90 * (k0 + k)) % 360
        for ci, cell in enumerate(CELLS_OF[design]):
            i, j = int(cell[0]), int(cell[1])
            bx, bz = to_cell(cx, cz, 16 * i + 8, 16 * j + 8, b)
            states = {"pw:part": part, "pw:hand": hand, "minecraft:cardinal_direction": DIR_OF_B[b]}
            if len(CELLS_OF[design]) > 1:
                states["pw:cell"] = ci
            cells.append((bx, f0 + k, bz, states))
        if k in mids:
            # the rail gap lies at the END of this quarter on the outer face: design point just outside the well there
            ex, ez = (8, 16 * n + 8) if dh == "r" else (16 * n + 8, 8)
            doors.append({"feet": f0 + k + 1, "cell": to_cell(cx, cz, ex, ez, b), "step": k})
    # the top: the floor in front of the head (spiral_gen.landing_local, in the head quarter's frame; as spiral_pack's pad)
    lx0, lx1, lz0, lz1 = SG.landing_local(n, dh)
    bh = (sgn * 90 * (k0 + q - 1)) % 360
    landing = []
    for lx in range(int(lx0) + 8, int(lx1), 16):
        for lz in range(int(lz0) + 8, int(lz1), 16):
            landing.append((*to_cell(cx, cz, lx, lz, bh), top - 1))
    landing = [(x, f, z) for (x, z, f) in landing]
    well = (x0, z0, x0 + 2 * n - 1, z0 + 2 * n - 1)
    for (x, f, z, _s) in cells:
        assert well[0] <= x <= well[2] and well[1] <= z <= well[3], ("a stair cell outside the well", x, z, well)
    return {"cells": cells, "well": well, "quarters": q, "doors": doors, "landing": landing, "top": top, "f0": f0, "design": design, "hand": hand}


def lay(b, P, pal, floor_mat, ceiling=None, door_h=3, protect=("pw:roof",)):
    """write plan P into building b: clear the well (f0 .. top - 1, and the top storey's headroom up to the ceiling), the
    blocks, the mid-floor doorways (air door_h high beside the step + a floor course under it), the landing in front.
    Nothing at or above `ceiling`; no cell whose block starts with a `protect` prefix is written. Returns a report."""
    rep = {"overwritten": {}, "skipped_protected": 0}

    def safe(x, f, z, name, **st):
        if ceiling is not None and f >= ceiling:
            return False
        cur = b.get(x, f, z)
        if cur and any(cur.startswith(p) for p in protect):
            rep["skipped_protected"] += 1
            return False
        if cur and cur not in (AIR, name) and name == AIR:
            rep["overwritten"][cur] = rep["overwritten"].get(cur, 0) + 1
        b.put(x, f, z, name, **st)
        return True

    x0, z0, x1, z1 = P["well"]
    hi = (ceiling - 1) if ceiling is not None else P["top"] + 3
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for f in range(P["f0"], hi + 1):
                safe(x, f, z, AIR)
    name = block_id(P["design"], pal)
    for (x, f, z, st) in P["cells"]:
        safe(x, f, z, name, **st)
    for d in P["doors"]:
        x, z = d["cell"]
        cur = b.get(x, d["feet"] - 1, z)
        if not cur or cur == AIR:
            safe(x, d["feet"] - 1, z, floor_mat)
        for h in range(door_h):
            safe(x, d["feet"] + h, z, AIR)
    for (x, f, z) in P["landing"]:
        cur = b.get(x, f, z)
        if not cur or cur == AIR or (x0 <= x <= x1 and z0 <= z <= z1):
            safe(x, f, z, floor_mat)
    return rep


if __name__ == "__main__":
    # self-check: every design, both hands, a 3-storey stair — cells inside the well, the doors outside it, one block per
    # cell per level, the landing at the top level and never on a stair cell
    for design in SG.DESIGNS:
        n = SG.DESIGNS[design]["n"]
        for hand in ("ccw", "cw"):
            for k0 in range(4):
                P = plan(10, 10, 0, [6, 12, 17], design, hand, k0)
                occ = {(x, f, z) for (x, f, z, _s) in P["cells"]}
                assert len(occ) == len(P["cells"]), "two blocks in one cell"
                x0, z0, x1, z1 = P["well"]
                for d in P["doors"]:
                    x, z = d["cell"]
                    assert not (x0 <= x <= x1 and z0 <= z <= z1), ("door inside the well", design, hand, d)
                    assert (x == x0 - 1 or x == x1 + 1 or z == z0 - 1 or z == z1 + 1), ("door not beside the well", d)
                    # the step it serves stands beside it at feet - 1
                    near = [(cx_, cz_) for (cx_, f, cz_, _s) in P["cells"] if f == d["feet"] - 1]
                    assert min(abs(cx_ - x) + abs(cz_ - z) for cx_, cz_ in near) == 1, ("door not beside its step", design, hand, k0, d)
                for (x, f, z) in P["landing"]:
                    assert f == P["top"] - 1 and (x, f, z) not in occ, ("landing on a stair cell", design, hand, (x, f, z))
                inwell = [(x, z) for (x, f, z) in P["landing"] if x0 <= x <= x1 and z0 <= z <= z1]
                assert len(inwell) == n * n, ("the landing must cover exactly the quarter ahead inside the well", design, hand, len(inwell))
    print("spiral_site self-check OK: 3 designs x 2 hands x 4 facings, doors beside their steps, landings in front")


# ------------------------------------------------------------------------------------------------ the exit solver
FREE = (None, AIR, "minecraft:light_block_14", "minecraft:structure_void")


def _get(b, x, f, z):
    try: return b.get(x, f, z)
    except IndexError: return "OUT"                  # outside the model: never walkable


def _walkable(b, x, f, z, well):
    """a cell a person can stand in at walking level f: something solid under it (or the well's own floor-in-front), air at f and f+1"""
    inwell = well[0] <= x <= well[2] and well[1] <= z <= well[3]
    if inwell: return True
    below = _get(b, x, f - 1, z)
    passable = lambda n: n in FREE or (n not in (None, "OUT") and n.endswith("_carpet"))   # a carpet is 1 px: walked over
    return below not in FREE and below != "OUT" and passable(_get(b, x, f, z)) and _get(b, x, f + 1, z) in FREE


def check(b, P, door_ok=None):
    """the exits of plan P against building b (the old stair not laid): every door leads onto walkable floor of its storey
    (door_ok(x, f, z) may narrow it, e.g. 'the corridor'), the landing's hallway cells outside the well are walkable at the
    top, and the foot can be reached from outside the well at f0. Returns (ok, reasons)."""
    why = []
    well = P["well"]
    for d in P["doors"]:
        x, z = d["cell"]; f = d["feet"]
        if not _walkable(b, x, f, z, well): why.append(f"door {d['cell']} @ {f}: not walkable ({_get(b, x, f - 1, z)}, {_get(b, x, f, z)}, {_get(b, x, f + 1, z)})")
        elif door_ok and not door_ok(x, f, z): why.append(f"door {d['cell']} @ {f}: not where it should open")
    # the floor in front: its quarter inside the well always; the hallway beyond it when that is walkable floor, else the
    # quarter alone, stepped off onto walkable floor beside it (his 15:06: "that exit can turn into a lengthwise hallway")
    inq = [(x, f, z) for (x, f, z) in P["landing"] if well[0] <= x <= well[2] and well[1] <= z <= well[3]]
    hall = [(x, f, z) for (x, f, z) in P["landing"] if not (well[0] <= x <= well[2] and well[1] <= z <= well[3])]
    if all(_walkable(b, x, f + 1, z, well) for (x, f, z) in hall):
        P["landing_mode"] = "hallway"
    else:
        side = {(x + dx, z + dz) for (x, f, z) in inq for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))}
        side = [c for c in side if not (well[0] <= c[0] <= well[2] and well[1] <= c[1] <= well[3])]
        T = P["top"]
        if any(_walkable(b, x, T, z, well) for (x, z) in side):
            P["landing"] = inq; P["landing_mode"] = "quarter"
        else:
            why.append(f"the floor in front: no walkable floor beyond or beside it at {T}")
    # the foot: a free, floored cell beside the well at f0 next to the quadrant before the first step
    f0 = P["f0"]
    foot = [(x, z) for (x, f, z, _s) in P["cells"] if f == f0]
    ring = {(x + dx, z + dz) for (x, z) in foot for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    ring = [c for c in ring if not (well[0] <= c[0] <= well[2] and well[1] <= c[1] <= well[3])]
    outside = [(x + dx, z + dz) for x in range(well[0], well[2] + 1) for z in range(well[1], well[3] + 1)
               for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    outside = {c for c in outside if not (well[0] <= c[0] <= well[2] and well[1] <= c[1] <= well[3])}
    if not any(_walkable(b, x, f0, z, well) for (x, z) in outside):
        why.append("the foot: no walkable cell beside the well at the ground")
    return (not why), why


def solve(b, x0, z0, f0, floors, design, door_ok=None, hands=("ccw", "cw")):
    """every hand x facing; the plans whose exits all check, best first (fewest landing cells over existing floor work)"""
    out = []
    for hand in hands:
        for k0 in range(4):
            P = plan(x0, z0, f0, floors, design, hand, k0)
            ok, why = check(b, P, door_ok)
            out.append((ok, len(why), hand, k0, why, P))
    out.sort(key=lambda t: (not t[0], t[1], 0 if t[5].get("landing_mode") == "hallway" else 1))
    return out
