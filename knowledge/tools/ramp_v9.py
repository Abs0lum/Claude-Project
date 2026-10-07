#!/usr/bin/env python3
"""ramp_v9.py — round 231 (RAMPS): the ramp family's sides closed by SOLID TOOTH COLUMNS and the boards made flush.

Witness (his 02:43 CT 10-07, -146 65 125, VV on; full-res reads in the RAMPS report):
  * dark WEDGES under the board edge at the high end of every cell: lower edge parallel to the brick courses (the base
    box's flat top), upper edge along the board, about a third of the cell long or more (perspective) — the region
    [base .. board underside] that only the zero-thickness alpha 'fills' planes were meant to close. Those planes do not
    show from the street side (the law "thin alpha-quad gable fill side pieces failed four orientation witnesses";
    sloped road pieces are built from full-width axis-aligned tooth columns, 1 px rise per 2 or 4 px run).
    8-ramp numbers: underside u(z) = base - 1.2093 + (z + 8) / 8 rises above the base for z > -0.33 (the last 52 % of
    the cell... 40 % where it clears 0.13 px), max 0.79 px at the high end; 4-part and 2-part pieces: up to 2 px.
  * dark dashed lines along every cell seam: the board is 15.96 wide (INSET 0.02 each side) -> a 0.04-px slot between
    neighbouring boards down to the dark interior (about 1 screen pixel at 2 blocks on his phone).
Construction v9 (per piece, every snow level):
  * base box, cap filler, snow filler / snow cap: as shipped (base box and cap stay full width; the board's cut texture
    is already transparent below the base and beyond the cap, so nothing coplanar shows).
  * step cubes -> TOOTH COLUMNS: run r = 1 / slope px (1 px rise per column: 8 px for the 8-ramp, 4 for the 4-part, 2 for
    the 2-part), top = the board's underside at the column's HIGH end (the column overlaps the board, never pokes through
    it: rise per column 1 px < the board's vertical thickness 1.21..1.34 px), x -7.98..7.98 (behind the board's cut face,
    so the visible cut texels are never coplanar with a column).
  * the 'fills' bone (two 16 x 16 zero-thickness alpha planes) is removed.
  * the deck board and the snow board span x -8..8 (flush): no seam slot between cells.
The deck, its cut UVs, the cap, the snow cubes and every identifier / texture size are those of the shipped geometry
(test_ramp_v9.py T6 compares them cube by cube).
Inputs : RP-13 1.0.1 pw_ramps8.geo.json + pw_snowcaps_ramps8.geo.json; RP-04 1.3.159 pw_ramps.geo.json + pw_snowcaps.geo.json
Outputs: _staging/ramps231/rp13/models/blocks/{pw_ramps8,pw_snowcaps_ramps8}.geo.json
         _staging/ramps231/rp04/models/blocks/{pw_ramps,pw_snowcaps}.geo.json   (non-ramp geometries copied unchanged)
Usage: ramp_v9.py [--check-only]   (the v8 generator is first re-run against the shipped files: it must rebuild all 70)"""
import copy
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import ramp_v8 as R8  # noqa: E402

ROOT = Path("/home/claude")
RP04 = ROOT / "_build/rp04-159/models/blocks"
RP13 = ROOT / "_build/rp13-101/models/blocks"
STAGE = ROOT / "_staging/ramps231"
DECK_T = R8.DECK_T
TOOTH_INSET = 0.02
ALL_PIECES = dict(R8.PIECES, **R8.PIECES8)
FILES = {  # staged path -> (source file, pieces it holds, snow levels)
    "rp13/models/blocks/pw_ramps8.geo.json": (RP13 / "pw_ramps8.geo.json", R8.PIECES8, (0,)),
    "rp13/models/blocks/pw_snowcaps_ramps8.geo.json": (RP13 / "pw_snowcaps_ramps8.geo.json", R8.PIECES8, (1, 2, 3, 4)),
    "rp04/models/blocks/pw_ramps.geo.json": (RP04 / "pw_ramps.geo.json", R8.PIECES, (0,)),
    "rp04/models/blocks/pw_snowcaps.geo.json": (RP04 / "pw_snowcaps.geo.json", R8.PIECES, (1, 2, 3, 4)),
}
IDENT = re.compile(r"geometry\.pw_ramp_(.+?)(?:_snow(\d))?$")


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def shipped_all():
    """identifier -> shipped geometry, for every ramp geometry in the four files"""
    out = {}
    for src, pieces, _ in FILES.values():
        for g in load(src)["minecraft:geometry"]:
            m = IDENT.match(g["description"]["identifier"])
            if m and m.group(1) in pieces:
                out[g["description"]["identifier"]] = g
    return out


def v8_rebuilds_shipped():
    """the v8 code must reproduce all 70 shipped ramp geometries (6 + 8 pieces x 5 snow levels) before v9 edits them"""
    ship = shipped_all()
    bad = []
    for piece in ALL_PIECES:
        ang = "7" if piece.startswith("8_") else ("14" if piece.startswith("4_") else "26")
        slots = R8.cut_slots(("7",) if ang == "7" else ("14", "26"))
        for lvl in range(5):
            g = R8.ramp_geometry(piece, ALL_PIECES, lvl)
            R8.apply_cut(g, slots[(ang, lvl)])
            ident = g["description"]["identifier"]
            r = R8.close(g, ship.get(ident), ident) if ident in ship else f"{ident}: not shipped"
            if r:
                bad.append(r)
    return len(ALL_PIECES) * 5, bad


def tooth_columns(base, rise, run):
    """1 px rise per column; top = the board underside at the column's high end; behind the cut face (x +-7.98)"""
    theta = math.atan2(rise, run)
    k = rise / run
    under = DECK_T / math.cos(theta)
    r = 1.0 / k
    cols, z0 = [], -8.0
    while z0 < 8 - 1e-9:
        z1 = min(8.0, z0 + r)
        top = min(base + rise, base - under + k * (z1 + 8))
        if top > base + 1e-4:
            o = [R8.r4(-8 + TOOTH_INSET), R8.r4(base), R8.r4(z0)]
            s = [R8.r4(16 - 2 * TOOTH_INSET), R8.r4(top - base), R8.r4(z1 - z0)]
            cols.append({"origin": o, "size": s, "uv": R8.box_uv(o, s)})
        z0 = z1
    return cols


def is_step(c, base):
    """a v8 step cube: axis-aligned, full width, standing on the base, not the base box (z from -8) nor the cap"""
    return (not c.get("rotation") and c["origin"][0] == -8 and c["size"][0] == 16 and c["origin"][2] > -8 + 1e-6
            and abs((c["origin"][1] - base) % R8.STEP_RISE) < 1e-3 and c["size"][1] == R8.STEP_RISE
            and all(f.get("material_instance", "*") == "*" for f in c["uv"].values()))


def v9_geometry(shipped, piece):
    """the shipped geometry with: fills bone removed, step cubes replaced by tooth columns, boards flush"""
    base, rise, run = ALL_PIECES[piece]
    g = copy.deepcopy(shipped)
    g["bones"] = [b for b in g["bones"] if b["name"] != "fills"]
    ramp = [b for b in g["bones"] if b["name"] == "ramp"][0]
    kept = [c for c in ramp["cubes"] if not is_step(c, base)]
    for c in kept:
        if c.get("rotation"):                      # the deck board and the snow board: full cell width
            c["origin"][0] = -8
            c["size"][0] = 16
    first_board = next(i for i, c in enumerate(kept) if c.get("rotation"))
    ramp["cubes"] = kept[:first_board] + tooth_columns(base, rise, run) + kept[first_board:]
    return g


def build_all(write=True):
    """identifier -> (v9 geometry, piece, snow level); writes the four staged files when asked"""
    out = {}
    for rel, (src, pieces, levels) in FILES.items():
        doc = load(src)
        geos = []
        for g in doc["minecraft:geometry"]:
            m = IDENT.match(g["description"]["identifier"])
            if m and m.group(1) in pieces:
                lvl = int(m.group(2) or 0)
                assert lvl in levels, (rel, g["description"]["identifier"])
                ng = v9_geometry(g, m.group(1))
                out[g["description"]["identifier"]] = (ng, m.group(1), lvl)
                geos.append(ng)
            else:
                geos.append(g)                     # pw_snowcaps.geo.json also carries the slab snow caps: untouched
        if write:
            p = STAGE / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"format_version": doc["format_version"], "minecraft:geometry": geos}, indent=1))
    return out


def main():
    n, bad = v8_rebuilds_shipped()
    print(f"v8 generator vs shipped (RP-04 1.3.159 + RP-13 1.0.1): {n} geometries rebuilt, {len(bad)} differ")
    for b in bad[:8]:
        print("   ", b)
    if bad:
        sys.exit(1)
    out = build_all(write="--check-only" not in sys.argv)
    nc = sum(len(b.get("cubes", [])) for g, _, _ in out.values() for b in g["bones"])
    print(f"v9: {len(out)} ramp geometries ({nc} cubes) -> {STAGE}")


if __name__ == "__main__":
    main()
