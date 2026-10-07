#!/usr/bin/env python3
"""verify_inn_r2.py — 1.3.232 (#INN): read the WRITTEN inn r2 structure files back and check the rooms independently of the
generator's own plan (inn_v2.SIDE_ROOMS is not used here).

Per skin (mvv_inn_{a,b,c,d}_r2.mcstructure, and the same cells re-assembled from its stages s0..s4):
  beds      every bed cell pairs with a bed cell of the same direction one step along z (head / foot by head_piece_bit)
  rooms     flood fill of the open cells (air, light, bed) on each guest-floor feet level, bounded by every other block
            (walls, logs, doors, glass): each region holding beds is a room. Count beds per room.
  ruling    >= 6 rooms; every room 2 or 4 beds; both kinds present; inside a room the bed heads stand in one row and
            neighbouring heads are exactly 2 apart (one free block) with the gap cells free at feet f..f+2 (walkable)
  doors     every room touches a door cell (its own door) on its boundary
  markers   one pw:marker 'bed' station entity on every bed head (the clock and the census read these)
Complexity: O(cells) per file. Usage: verify_inn_r2.py STRUCTURES_DIR (holds mvv_inn_*_r2.mcstructure + stages/)"""
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mcstructure as M  # noqa: E402

DATUM_Y = 15
FLOORS = (4, 8)
OPEN = ("minecraft:air", "minecraft:bed")


def is_open(name):
    return name is None or name in OPEN or name.startswith("minecraft:light_block")


def merged_stages(stage_dir, stem):
    """the cells after placing s0..s4 in order (structure void = keep): {(x, y, z): (name, states)}"""
    cells = {}
    size = None
    for k in range(5):
        st = M.Structure.from_bytes((stage_dir / f"{stem}_s{k}.mcstructure").read_bytes())
        size = st.size
        sx, sy, sz = st.size
        for x in range(sx):
            for y in range(sy):
                for z in range(sz):
                    e = st.get(x, y, z)
                    if e is not None:
                        cells[(x, y, z)] = (e[0], {a: v.value for a, v in e[1].items()})
    return size, cells


def finished(path):
    st = M.Structure.from_bytes(path.read_bytes())
    sx, sy, sz = st.size
    cells = {}
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                e = st.get(x, y, z)
                if e is not None:
                    cells[(x, y, z)] = (e[0], {a: v.value for a, v in e[1].items()})
    return st, cells


def rooms_of(size, cells, f):
    sx, _sy, sz = size
    y = DATUM_Y + f
    name = lambda x, z: cells.get((x, y, z), (None,))[0]
    seen, rooms = set(), []
    for x in range(sx):
        for z in range(sz):
            if (x, z) in seen or not is_open(name(x, z)) or name(x, z) is None:
                continue
            reg, q = [], deque([(x, z)])
            seen.add((x, z))
            while q:
                a, c = q.popleft()
                reg.append((a, c))
                for da, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (a + da, c + dc)
                    if 0 <= n[0] < sx and 0 <= n[1] < sz and n not in seen and is_open(name(*n)) and name(*n) is not None:
                        seen.add(n)
                        q.append(n)
            heads = sorted((a, c) for (a, c) in reg if name(a, c) == "minecraft:bed" and cells[(a, y, c)][1]["head_piece_bit"])
            if not heads:
                continue
            doors = {(a + da, c + dc) for (a, c) in reg for da, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                     if (name(a + da, c + dc) or "").endswith("_door")}
            rooms.append({"cells": reg, "heads": heads, "doors": sorted(doors)})
    return rooms


def check(size, cells, label):
    fails, table = [], []
    beds = {k: v for k, v in cells.items() if v[0] == "minecraft:bed"}
    for (x, y, z), (_n, s) in beds.items():
        d = s["direction"]
        dz = {2: 1, 0: -1}.get(d)                                  # head north (2): the foot is at z + 1; head south (0): z - 1
        if dz is None:
            fails.append(f"bed at {(x, y, z)}: direction {d} (expected 0 or 2)")
            continue
        mate = (x, y, z + dz) if s["head_piece_bit"] else (x, y, z - dz)
        m = beds.get(mate)
        if not m or m[1]["direction"] != d or m[1]["head_piece_bit"] == s["head_piece_bit"]:
            fails.append(f"bed at {(x, y, z)}: no matching {'foot' if s['head_piece_bit'] else 'head'} at {mate}")
    n_heads = sum(1 for v in beds.values() if v[1]["head_piece_bit"])
    all_rooms = []
    for f in FLOORS:
        y = DATUM_Y + f
        for r in rooms_of(size, cells, f):
            xs = [a for (a, _c) in r["heads"]]
            zs = {c for (_a, c) in r["heads"]}
            n = len(xs)
            all_rooms.append(n)
            x0, x1 = min(a for a, _ in r["cells"]), max(a for a, _ in r["cells"])
            z0, z1 = min(c for _, c in r["cells"]), max(c for _, c in r["cells"])
            table.append((f, x0, x1, z0, z1, n, xs, r["doors"]))
            if n not in (2, 4):
                fails.append(f"{label} feet {f} room x {x0}..{x1} z {z0}..{z1}: {n} beds")
            if len(zs) != 1:
                fails.append(f"{label} feet {f} room x {x0}..{x1}: heads in {len(zs)} rows")
            hz = next(iter(zs))
            for a, b in zip(xs, xs[1:]):
                if b - a != 2:
                    fails.append(f"{label} feet {f} room x {x0}..{x1}: heads x {a} and {b} are {b - a - 1} blocks apart")
                for ff in range(f, f + 3):
                    for cz in {hz, hz + (1 if hz < 6 else -1)}:          # the gap beside the head and beside the foot
                        g = cells.get((a + 1, DATUM_Y + ff, cz), (None,))[0]
                        if not is_open(g) or g == "minecraft:bed":
                            fails.append(f"{label} feet {f}: the gap ({a + 1}, {ff}, {cz}) holds {g}")
            if not r["doors"]:
                fails.append(f"{label} feet {f} room x {x0}..{x1} z {z0}..{z1}: no door")
            _ = y
    if len(all_rooms) < 6:
        fails.append(f"{label}: {len(all_rooms)} rooms < 6")
    if not ({2, 4} <= set(all_rooms)):
        fails.append(f"{label}: no mix (room sizes {sorted(set(all_rooms))})")
    if n_heads != 32 or sum(all_rooms) != 32:
        fails.append(f"{label}: {n_heads} bed heads, {sum(all_rooms)} in rooms (want 32)")
    return fails, table, n_heads


def main():
    root = Path(sys.argv[1])
    stage_dir = root / "stages"
    ok = True
    tables = {}
    for skin in "abcd":
        stem = f"mvv_inn_{skin}_r2"
        st, fin = finished(root / f"{stem}.mcstructure")
        size, stg = merged_stages(stage_dir, stem)
        same = {k: v for k, v in fin.items()} == stg
        f1, table, n = check(st.size, fin, f"{stem} (finished)")
        f2, table2, _n2 = check(size, stg, f"{stem} (stages s0..s4)")
        ents = [e.value for e in st.entities]
        bed_marks = sorted((round(e["Pos"].value[0].value - 0.5), round(e["Pos"].value[1].value) - DATUM_Y, round(e["Pos"].value[2].value - 0.5))
                           for e in ents if e["identifier"].value == "pw:marker" and "civ:kind:bed" in [t.value for t in e["Tags"].value])
        head_cells = sorted((x, y - DATUM_Y, z) for (x, y, z), v in fin.items() if v[0] == "minecraft:bed" and v[1]["head_piece_bit"])
        marks_ok = bed_marks == head_cells
        tables[skin] = [(t[0], t[1], t[2], t[3], t[4], t[5]) for t in table]
        print(f"{stem}: size {list(st.size)} bed heads {n} rooms {len(table)} (2-bed {sum(1 for t in table if t[5] == 2)}, "
              f"4-bed {sum(1 for t in table if t[5] == 4)}) stages==finished {same} bed markers on heads {marks_ok} ({len(bed_marks)}) "
              f"-> {'PASS' if not (f1 or f2) and same and marks_ok else 'FAIL'}")
        for msg in (f1 + f2)[:10]:
            print("   FAIL", msg)
        ok = ok and not (f1 or f2) and same and marks_ok
    print("rooms identical across the 4 skins:", len({str(v) for v in tables.values()}) == 1)
    print("rooms (skin a): feet | room x span | z span | beds | head x | doors")
    st, fin = finished(root / "mvv_inn_a_r2.mcstructure")
    _f, table, _n = check(st.size, fin, "a")
    for (f, x0, x1, z0, z1, n, xs, doors) in table:
        print(f"  feet {f:2d} | x {x0:2d}..{x1:2d} | z {z0:2d}..{z1:2d} | {n} | {xs} | {doors}")
    print("VERIFY:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
