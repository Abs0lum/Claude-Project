#!/usr/bin/env python3
"""road_kit_228.py — program 228 (his 12:20 + 13:40, 10-06): the street RAMP pieces.
  t_ramp8 / v_ramp8 (NEW, 8 long): the road climbs on pw:ramp_cobble_8_e1..e8 over the 8 cells, the sidewalks on
    pw:ramp_smooth_stone_8_e1..e8 one level up, the curbs on pw:ramp_stonebrick_8_e1..e8 over stone bricks; subgrade = his
    ramp_7's low row (x0) repeated. Native: travel +x, climbs one block from x0 to x7 (as ramp7).
  t_ramp7 / v_ramp7 (his piece, kept): only the SIDEWALK slab half-steps become pw:ramp_smooth_stone_4_q1..q4 (cells x1..x4
    at y15 over the low sidewalk), the curbs untouched.
The village widths are made by road_kit.villageify (proved: villageify(t_ramp7) == the shipped v_ramp7, byte for byte).
Outputs: tools/bp02_overlay_228/structures/pw/road/{t,v}_ramp{7,8}.mcstructure"""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402
import road_kit as RK  # noqa: E402

SRC = Path("/home/claude/_build/bp02-227/structures/pw/road")
OUT = Path("/home/claude/tools/bp02_overlay_228/structures/pw/road")
SIDE = (0, 1, 11, 12)
CURB = (2, 10)
ROAD = range(3, 10)


def put(st, x, y, z, name, **states):
    st.set(x, y, z, name, RK.typed_states(states) if states else {})


def ramp7():
    st = M.Structure.from_bytes((SRC / "t_ramp7.mcstructure").read_bytes())
    for z in SIDE:
        for i, x in enumerate(range(1, 5)):
            put(st, x, 15, z, f"pw:ramp_smooth_stone_4_q{i + 1}", **{"minecraft:cardinal_direction": "east", "pw:var": (x * 5 + z) % 8, "pw:snow": 0})
    return st


def ramp8():
    src = M.Structure.from_bytes((SRC / "t_ramp7.mcstructure").read_bytes())
    sx, sy, sz = src.size
    st = M.Structure((8, sy, sz))
    for x in range(8):
        for y in range(sy):
            for z in range(sz):
                e = src.get(0, y, z) if y <= 13 else None          # the low row's subgrade, everything below the surface
                if e is not None:
                    st.set(x, y, z, e[0], e[1])
        for z in SIDE:
            put(st, x, 14, z, "minecraft:smooth_stone")
            put(st, x, 15, z, f"pw:ramp_smooth_stone_8_e{x + 1}", **{"minecraft:cardinal_direction": "east", "pw:var": (x * 3 + z) % 8, "pw:snow": 0})
        for z in CURB:
            put(st, x, 14, z, "minecraft:stone_bricks")
            put(st, x, 15, z, f"pw:ramp_stonebrick_8_e{x + 1}", **{"minecraft:cardinal_direction": "east", "pw:var": (x * 7 + z) % 8, "pw:snow": 0})
        for z in ROAD:
            put(st, x, 13, z, "minecraft:cobblestone")
            put(st, x, 14, z, f"pw:ramp_cobble_8_e{x + 1}", **{"minecraft:cardinal_direction": "east", "pw:var": (x * 5 + z * 3) % 8, "pw:snow": 0})
    return st


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, st in (("ramp7", ramp7()), ("ramp8", ramp8())):
        (OUT / f"t_{name}.mcstructure").write_bytes(st.to_bytes())
        (OUT / f"v_{name}.mcstructure").write_bytes(RK.villageify(st, two_d=st.size[0] == 13).to_bytes())
        print(f"t_{name} {st.size}  v_{name}")
        print(RK.surface_text(st, y_rows=(13, 14, 15)))


if __name__ == "__main__":
    main()
