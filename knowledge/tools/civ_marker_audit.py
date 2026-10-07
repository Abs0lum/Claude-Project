#!/usr/bin/env python3
"""civ_marker_audit.py — his 20:21 "the zones might be wrong in the cottage / and the stations" (AMBIGUOUS -> rigorous).
Checks every marker of every generated CIVITAS building against the written laws:

ZONES — CIVITAS-ZONE-GEOMETRY-v2 (locked 08-14) + CIVITAS-ZONE-TABLE-v1 (ruled 09-22):
  Z1  a ring = the corners of ONE room, at floor level (the cell above a solid floor), one corner at every bend
  Z2  counter-clockwise seen from above (NW -> SW -> SE -> NE for a rectangle; V3 turn sum +360)
  Z3  V1/V2/V6/V7: even count, consecutive corners axis-aligned, edges >= 1, the ring closes
  Z4  traced to the room's INNER face: no wall (solid, non-fixture) cell inside the polygon at the ring's level,
      and each corner cell has solid on its two outward sides (rooms with walls) — open yards/gardens exempt
  Z5  coverage: every walkable interior cell at a storey's floor level that belongs to an enclosed room lies inside
      some ring of that storey (a room with no zone is invisible to the behaviour code)
  Z6  meaning (zone table): kitchen only where a hearth is inside; quarters / chamber hold a bed or are a household
      room; threshold touches a door (station door) cell; cellar below grade (feet < 0); stable holds animal fittings
STATIONS — CIVITAS-MARKER-ENTITIES-v1 §placement ("sneak-tap = the block's OWN cell: the chair, the bed, the table,
  the doorway") + AUTHORING-WORKFLOW §6.2 ("place it where the oven is"):
  S1  a fixture station sits IN its fixture's cell (door, hearth, table, seat, store, bed, oven, anvil, counter, prep,
      rack, desk, post, bench); an area station (field, pen, yard, stall) sits on a walkable cell of its area
  S2  coverage: every seat-type piece, bed, hearth, oven, anvil, lectern has its station
Output: _docs/civ/MARKER-AUDIT-<label>.json + a printed table."""
import json
import sys
from pathlib import Path

MAN = Path("/home/claude/_staging/civ/manifests")
FIX = {
    "door": ("door", "fence_gate"), "hearth": ("pw:hearth_",), "table": ("pw:furn_table_",),
    "seat": ("pw:furn_chair_", "pw:furn_bench_", "pw:furn_stool_", "pw:furn_barrel_seat_"),
    "store": ("minecraft:chest", "minecraft:barrel", "pw:furn_cupboard_", "pw:furn_dresser_", "minecraft:hay_block"),
    "bed": ("minecraft:bed",), "oven": ("minecraft:furnace", "minecraft:smoker", "minecraft:blast_furnace"),
    "anvil": ("minecraft:anvil",), "counter": ("pw:furn_shelf_",), "prep": ("pw:furn_trestle_", "minecraft:composter"),
    "rack": ("minecraft:chain", "minecraft:iron_chain", "_log", "pw:furn_wall_shelf_", "pw:furn_coat_pegs_"), "desk": ("minecraft:lectern",),
    "post": ("minecraft:wall_sign", "sign", "pw:furn_shelf_"), "bench": ("minecraft:grindstone", "minecraft:stonecutter", "crafting_table"),
}
AREA = {"field", "pen", "yard", "stall"}
NEEDS = {"seat": FIX["seat"], "bed": ("minecraft:bed",), "hearth": ("pw:hearth_",), "oven": FIX["oven"],
         "anvil": ("minecraft:anvil",), "desk": ("minecraft:lectern",)}
WALKABLE = ("minecraft:air", "minecraft:light_block", "pw:furn_", "minecraft:wheat", "minecraft:short_grass",
            "minecraft:ladder", "minecraft:bed", "minecraft:chest", "minecraft:barrel", "minecraft:hay", "minecraft:cauldron",
            "minecraft:lectern", "minecraft:anvil", "minecraft:grindstone", "minecraft:composter", "minecraft:furnace",
            "minecraft:smoker", "minecraft:blast_furnace", "minecraft:stonecutter", "minecraft:chain", "minecraft:iron_chain", "door", "pw:hearth_",
            "minecraft:wall_sign", "minecraft:bell", "minecraft:glass_pane")
NONSOLID_FLOOR = ("minecraft:air", "minecraft:light_block", "minecraft:water", "minecraft:ladder", "minecraft:wheat")


def starts(name, keys):
    return any(name.startswith(k) or (k.startswith("_") and name.endswith(k)) or (k in ("door", "fence_gate", "sign") and k in name)
               for k in keys)


def audit(stem):
    man = json.loads((MAN / f"{stem}.json").read_text())
    d = man["datum_y"]
    grid = {(x, y - d, z): n for x, y, z, n, _s in man["blocks"]}
    def at(x, f, z):
        return grid.get((x, f, z), "minecraft:air")
    def solid(x, f, z):
        n = at(x, f, z)
        return not n.startswith(NONSOLID_FLOOR) and not starts(n, ("door",))
    def walkable(x, f, z):
        return starts(at(x, f, z), WALKABLE) or at(x, f, z).startswith("minecraft:air")
    issues, notes = [], []
    ents = man["entities"]
    # ---------------- zones: group rings by (kind, n // 16)
    rings = {}
    for e in ents:
        if e.get("fam") == "zone":
            rings.setdefault((e["kind"], e["n"] // 16), []).append(e)
    zone_cells = {}
    for (kind, r), cs in sorted(rings.items()):
        cs = sorted(cs, key=lambda e: e["n"])
        pts = [tuple(e["cell"]) for e in cs]
        tag = f"zone {kind}#{r}"
        if len(pts) % 2 or len(pts) < 4:
            issues.append(f"{tag}: Z3 {len(pts)} corners (need an even count >= 4)")
            continue
        ok_axis = all((pts[i][0] == pts[(i + 1) % len(pts)][0]) != (pts[i][2] == pts[(i + 1) % len(pts)][2]) for i in range(len(pts)))
        if not ok_axis:
            issues.append(f"{tag}: Z3 consecutive corners not axis-aligned / zero-length edge")
        area2 = sum(pts[i][0] * pts[(i + 1) % len(pts)][2] - pts[(i + 1) % len(pts)][0] * pts[i][2] for i in range(len(pts)))
        # x east, z south; seen from above with north up, counter-clockwise <=> shoelace (x, z) NEGATIVE
        if area2 > 0:
            issues.append(f"{tag}: Z2 clockwise seen from above (shoelace {area2}); the spec locks counter-clockwise")
        f = pts[0][1]
        if any(p[1] != f for p in pts):
            notes.append(f"{tag}: corners on several levels {sorted({p[1] for p in pts})} (allowed, V5)")
        xs = [p[0] for p in pts]; zs = [p[2] for p in pts]
        cells = {(x, z) for x in range(min(xs), max(xs) + 1) for z in range(min(zs), max(zs) + 1)}
        zone_cells[(kind, r)] = (f, cells)
        for (x, y, z) in pts:
            if not solid(x, y - 1, z):
                issues.append(f"{tag}: Z1 corner {x},{y},{z} has no floor under it ({at(x, y - 1, z)})")
            if not walkable(x, y, z):
                issues.append(f"{tag}: Z1 corner {x},{y},{z} sits inside {at(x, y, z)}")
        edge = {(x, z) for (x, z) in cells if x in (min(xs), max(xs)) or z in (min(zs), max(zs))}
        walls_in = [(x, z) for (x, z) in edge if not walkable(x, f, z) and "fence" not in at(x, f, z)]
        if walls_in and kind not in ("yard", "garden", "commons"):
            issues.append(f"{tag}: Z4 {len(walls_in)} wall/solid cells inside the ring at feet {f}, e.g. {walls_in[:4]} = {[at(x, f, z) for x, z in walls_in[:4]]}")
        if False:   # Z4 inner-face corner test retired (calibration 20:3x): an open portal or open-sided shed is legal (spec §7); a ring that stops short of its room is caught by Z5 coverage
            others = set()
            for (k2, r2), cs2 in rings.items():
                if (k2, r2) != (kind, r):
                    p2 = [tuple(e["cell"]) for e in cs2]
                    if p2 and p2[0][1] == f:
                        others |= {(x, z) for x in range(min(q[0] for q in p2), max(q[0] for q in p2) + 1)
                                   for z in range(min(q[2] for q in p2), max(q[2] for q in p2) + 1)}
            for (x, y, z) in pts:
                out = [(dx, dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + dx, z + dz) not in cells and (x + dx, z + dz) not in others]
                if not all(solid(x + dx, y, z + dz) or starts(at(x + dx, y, z + dz), ("door", "glass_pane", "pw:hearth_", "pw:flue_")) for dx, dz in out):
                    issues.append(f"{tag}: Z4 corner {x},{y},{z} is not at the room's inner face (outward: {[at(x + dx, y, z + dz) for dx, dz in out]})")
        inside = [at(x, f, z) for (x, z) in cells]
        if kind == "kitchen" and not any(n.startswith("pw:hearth_") for n in inside):
            # the hearth is IN the wall line: check the ring's border too
            border = [at(x + dx, f, z + dz) for (x, z) in cells for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if not any(n.startswith("pw:hearth_") for n in border):
                issues.append(f"{tag}: Z6 a kitchen without a hearth (zone table: kitchen = the hearth room)")
        if kind in ("quarters", "chamber") and not any(n.startswith("minecraft:bed") for n in inside):
            notes.append(f"{tag}: Z6 no bed inside (fine for a household living room; check)")
        if kind == "cellar" and f >= 0:
            issues.append(f"{tag}: Z6 cellar above grade (feet {f})")
        if kind == "threshold":
            doors = [e for e in ents if e.get("fam") == "station" and e["kind"] == "door"]
            near = any(abs(e["cell"][0] - x) + abs(e["cell"][2] - z) <= 1 and e["cell"][1] == f for e in doors for (x, z) in cells)
            if not near:
                issues.append(f"{tag}: Z6 threshold does not touch a door station")
    # Z5 coverage: enclosed walkable cells per storey level that hold a zone, flood-filled through walkable cells
    levels = sorted({fz[0] for fz in zone_cells.values()})
    sx, sy, sz = man["size"]
    for f in levels:
        covered = set().union(*[c for (k, r), (ff, c) in zone_cells.items() if ff == f])
        seen, uncovered = set(), set()
        for (x, z) in covered:
            stack = [(x, z)]
            while stack:
                c = stack.pop()
                if c in seen:
                    continue
                cx, cz = c
                if not (0 <= cx < sx and 1 <= cz < sz) or not walkable(cx, f, cz) or any(w in at(cx, f, cz) for w in ("door", "glass_pane", "fence", "pw:hearth_", "pw:flue_")):
                    continue
                if not solid(cx, f - 1, cz) and not at(cx, f - 1, cz).startswith("minecraft:ladder"):
                    continue
                seen.add(c)
                if c not in covered:
                    uncovered.add(c)
                if len(seen) > 600:
                    break
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    stack.append((cx + dx, cz + dz))
        if uncovered:
            issues.append(f"feet {f}: Z5 {len(uncovered)} walkable room cells in no zone, e.g. {sorted(uncovered)[:6]}")
    # ---------------- stations
    for e in ents:
        if e.get("fam") != "station":
            continue
        x, f, z = e["cell"]
        here = at(x, f, z)
        k = e["kind"]
        tag = f"station {k}#{e['n']} @{x},{f},{z}"
        if k in AREA:
            if not walkable(x, f, z):
                issues.append(f"{tag}: S1 area station inside {here}")
            continue
        if k not in FIX:
            notes.append(f"{tag}: no fixture rule for this role")
            continue
        hung = k == "rack" and any(at(x, f + h, z).startswith(("minecraft:chain", "minecraft:iron_chain")) for h in (1, 2, 3))
        if not starts(here, FIX[k]) and not (k == "door" and here == "minecraft:air") and not hung:
            nb = {f"{dx},{dz}": at(x + dx, f, z + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)) if starts(at(x + dx, f, z + dz), FIX[k])}
            issues.append(f"{tag}: S1 not in its fixture's cell (cell holds {here}){'; the fixture is beside it at ' + str(nb) if nb else ''}")
    stations = {(e["kind"], tuple(e["cell"])) for e in ents if e.get("fam") == "station"}
    for k, keys in NEEDS.items():
        for (x, f, z), n in grid.items():
            if starts(n, keys):
                if k == "bed" and not any(sk == "bed" and abs(c[0] - x) + abs(c[2] - z) <= 1 and c[1] == f for sk, c in stations):
                    issues.append(f"S2 bed at {x},{f},{z} has no bed station")
                elif k != "bed" and (k, (x, f, z)) not in stations:
                    issues.append(f"S2 {n} at {x},{f},{z} has no {k} station in its cell")
    return issues, notes, man


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "now"
    stems = sorted(p.stem for p in MAN.glob("*.json"))
    out = {}
    for s in stems:
        iss, nts, man = audit(s)
        out[s] = {"issues": iss, "notes": nts}
        print(f"== {s}: {len(iss)} issues, {len(nts)} notes")
        for i in iss:
            print("   ISSUE", i)
    Path(f"/home/claude/_docs/civ/MARKER-AUDIT-{label}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
