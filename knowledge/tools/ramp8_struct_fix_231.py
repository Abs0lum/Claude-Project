#!/usr/bin/env python3
"""ramp8_struct_fix_231.py — round 231 (RAMPS): the 8-block street ramp pieces leave the TOP layer over the lane as
STRUCTURE VOID, so a DOWN ramp keeps whatever terrain stood at the upper street level over its lane (his "dirt above the
street ramps", 10-07 00:23 + 02:54).

Mechanism (read-only sources):
  * tools/road_kit_228.py ramp8(): copies ramp7's rows only for y <= 13 (line 42) and writes y 14 (lane ramps) and y 15 only
    for the sidewalks / curbs (lines 45-50) -> the lane cells at y 15 are never set = void (-1). Every other road piece
    (straight1, ramp7, access3, dead13, tee13, cross13, elbow13) writes explicit minecraft:air there.
  * pw_civ_clock.js 3177: a piece's H = p.y + 14 (+1 for a DOWN ramp) = the ENTRY level; kitPrep (3222) cuts the corridor
    only from H + 1 upward. A down ramp's structure y 15 is world H itself -> never cut, never overwritten.
Fix: the void lane cells of the top layer become minecraft:air (exactly what ramp7 carries there). Nothing else changes.

Input : _build/bp02-230/structures/pw/road/{t,v}_ramp8.mcstructure  (the SLIM 1.3.230 palette, no pw:var)
Output: _staging/ramps231/bp02/structures/pw/road/{t,v}_ramp8.mcstructure
Checks (all must pass, else exit 1): void cells after = 0; every non-void cell identical to the input; the changed cells
are exactly the input's void cells, all in the top layer, all inside the lane; re-decode of the output byte-identical.
Usage: ramp8_struct_fix_231.py"""
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

SRC = Path("/home/claude/_build/bp02-230/structures/pw/road")
OUT = Path("/home/claude/_staging/ramps231/bp02/structures/pw/road")
LANE = {"t": range(3, 10), "v": range(4, 9)}          # t: lane z 3..9 (7 wide); v: lane z 4..8 (5 wide)


def plain(entry):
    """a palette entry with its typed states compared by (tag type, value) — Tag objects compare by identity"""
    if entry is None:
        return None
    name, states, version = entry
    return name, tuple(sorted((k, v.type, v.value) for k, v in states.items())), version


def fix(width):
    src = M.Structure.from_bytes((SRC / f"{width}_ramp8.mcstructure").read_bytes())
    st = M.Structure.from_bytes((SRC / f"{width}_ramp8.mcstructure").read_bytes())
    sx, sy, sz = st.size
    voids = [(x, y, z) for x in range(sx) for y in range(sy) for z in range(sz) if st.layer0[st.index(x, y, z)] < 0]
    air = next((k for k, (n, s, _) in enumerate(st.palette) if n == "minecraft:air" and not s), None)   # reuse the piece's own air entry
    for x, y, z in voids:
        if air is None:
            st.set(x, y, z, "minecraft:air")
        else:
            st.layer0[st.index(x, y, z)] = air
    errs = []
    if any(y != sy - 1 or z not in LANE[width] for _, y, z in voids):
        errs.append(f"void outside the lane's top layer: {[v for v in voids if v[1] != sy - 1 or v[2] not in LANE[width]][:5]}")
    if len(voids) != sx * len(LANE[width]):
        errs.append(f"expected {sx * len(LANE[width])} void lane cells, found {len(voids)}")
    vs = set(voids)
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                a, b = plain(src.get(x, y, z)), plain(st.get(x, y, z))
                if (x, y, z) in vs:
                    if b is None or b[0] != "minecraft:air":
                        errs.append(f"{(x, y, z)} not air after the fix")
                elif a != b:
                    errs.append(f"{(x, y, z)} changed: {a} -> {b}")
    if any(v < 0 for v in st.layer0):
        errs.append("void cells remain")
    buf = st.to_bytes()
    if M.Structure.from_bytes(buf).to_bytes() != buf:
        errs.append("re-encode not byte-identical")
    return st, buf, len(voids), errs


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bad = 0
    for w in ("t", "v"):
        st, buf, n, errs = fix(w)
        if errs:
            bad += 1
            print(f"FAIL {w}_ramp8: " + "; ".join(errs[:6]))
            continue
        (OUT / f"{w}_ramp8.mcstructure").write_bytes(buf)
        print(f"PASS {w}_ramp8 {st.size}: {n} void lane cells of the top layer -> minecraft:air; {len(buf):,} B")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
