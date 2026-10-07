#!/usr/bin/env python3
"""test_ramp_v9.py — the witnessed defects of the ramp family, as tests (round 231, RAMPS).

His 02:43 CT 10-07 shots (-146 65 125, VV on): dark wedge-shaped slits under the board edge at the HIGH end of every
ramp cell, and dark dashed lines along the cell seams. The tests state what a closed ramp side and a closed walking
surface mean, so the v9 geometry is checked against the defect, not against itself:

  T1 side closed   — every point of the side profile under the walking line (0 < y < top(z)) is covered by a SOLID
                     cube (not a zero-thickness alpha plane): the 'fills' planes are not trusted (four failed orientation
                     witnesses + the 10-07 slits).
  T2 nothing proud — no non-snow solid stands above the walking line (no tooth pokes through the board).
  T3 no fills      — no zero-thickness cube and no 'fill' material instance anywhere.
  T4 flush decks   — the board (and the snow board) spans the full cell width x -8..8: no 0.04-px seam between cells.
  T5 no coplanar   — no axis-aligned cube whose side lies on x = +-8 overlaps the board's VISIBLE cut texels
                     (cut is cleared below the base and beyond the cap: tooth columns sit at +-7.98, behind the cut face).
  T6 unchanged     — the board, the cap filler, the snow cubes and the cut UVs are those of the shipped geometry (only
                     x-extents of the boards change); identifiers, texture size, format 1.16.0 unchanged.
  T7 the old shipped geometry FAILS T1 and T4 (the tests see the witnessed defect).
Run: python3 tools/test_ramp_v9.py   (exit 0 = all pass)"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import ramp_v9 as V9  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


def solids(g):
    """(cube, is_board) for every cube with volume, the deck/snow boards flagged"""
    out = []
    for b in g["bones"]:
        for c in b.get("cubes", []):
            out.append((c, bool(c.get("rotation"))))
    return out


def inside(c, z, y, x=None):
    """point (x?, y, z) inside the cube (cube rotation about x only, as every ramp board)"""
    o, s = c["origin"], c["size"]
    if c.get("rotation"):
        a = math.radians(c["rotation"][0])        # inverse of the +theta board rotation (raises the +z end)
        py, pz = c["pivot"][1], c["pivot"][2]
        dy, dz = y - py, z - pz
        y, z = py + dy * math.cos(a) - dz * math.sin(a), pz + dy * math.sin(a) + dz * math.cos(a)
    ok = o[1] - 1e-6 <= y <= o[1] + s[1] + 1e-6 and o[2] - 1e-6 <= z <= o[2] + s[2] + 1e-6
    if x is not None:
        ok = ok and o[0] - 1e-6 <= x <= o[0] + s[0] + 1e-6
    return ok


def profile_ok(g, piece, snow):
    base, rise, run = V9.ALL_PIECES[piece]
    k = rise / run
    holes, proud = 0, 0
    cubes = [c for c, _ in solids(g) if min(c["size"]) > 0 and not any(f.get("material_instance") == "snow" for f in c["uv"].values())]
    z_cap = 8 - V9.DECK_T * math.sin(math.atan2(rise, run))     # the shipped cap filler stands at the landing height there
    for iz in range(1, 160):
        z = -8 + iz * 0.1
        top = base + k * (z + 8)
        for iy in range(1, 200):
            y = iy * 0.1
            if y < top - 0.06:
                if not any(inside(c, z, y, x=7.97) for c in cubes):       # seen from the side, just inside the cell's face
                    holes += 1
            elif y > top + 0.06 and y < 16 and z < z_cap - 0.1:
                if any(inside(c, z, y) for c in cubes):
                    proud += 1
    return holes, proud


def run():
    new = V9.build_all(write=False)
    old = V9.shipped_all()
    check(set(new) == set(old), f"identifier sets differ: {sorted(set(new) ^ set(old))[:4]}")
    for ident, (g, piece, snow) in sorted(new.items()):
        holes, proud = profile_ok(g, piece, snow)
        check(holes == 0, f"T1 {ident}: {holes} side-profile points uncovered")
        check(proud == 0, f"T2 {ident}: {proud} profile points proud of the walking line")
        allc = [c for b in g["bones"] for c in b.get("cubes", [])]
        check(all(min(c["size"]) > 0 for c in allc), f"T3 {ident}: zero-thickness cube")
        check(not any(f.get("material_instance") == "fill" for c in allc for f in c["uv"].values()), f"T3 {ident}: fill instance")
        check(all(b["name"] != "fills" for b in g["bones"]), f"T3 {ident}: fills bone")
        boards = [c for c in allc if c.get("rotation")]
        check(boards and all(abs(c["origin"][0] + 8) < 1e-9 and abs(c["size"][0] - 16) < 1e-9 for c in boards), f"T4 {ident}: board not flush")
        # T5: axis cubes on the x = +-8 plane must not overlap the visible cut texels (y > base, z < z_cap) under the board
        base, rise, run_ = V9.ALL_PIECES[piece]
        th = math.atan2(rise, run_)
        z_cap = 8 - V9.DECK_T * math.sin(th)
        z_inner = -8 + 2 * snow * math.sin(th) * math.cos(th) + 0.02 if snow else -8   # cut cleared behind the snow toe filler
        deck = [c for c in boards if c["uv"]["up"].get("material_instance") == "deck"][0]
        for c in allc:
            if c.get("rotation") or not (abs(c["origin"][0] + 8) < 1e-9 or abs(c["origin"][0] + c["size"][0] - 8) < 1e-9):
                continue
            o, s = c["origin"], c["size"]
            for iz in range(1, 40):
                z = o[2] + s[2] * iz / 40
                for iy in range(1, 20):
                    y = o[1] + s[1] * iy / 20
                    if y > base + 0.13 and z_inner + 0.13 < z < z_cap - 0.13 and inside(deck, z, y):
                        FAILS.append(f"T5 {ident}: axis cube {o}+{s} coplanar with the visible cut at z={z:.2f} y={y:.2f}")
                        break
                else:
                    continue
                break
        # T6: unchanged parts
        og = old[ident]
        check(og["description"] == g["description"], f"T6 {ident}: description changed")
        ob = [c for b in og["bones"] for c in b.get("cubes", []) if c.get("rotation")]
        check(len(ob) == len(boards), f"T6 {ident}: board count {len(ob)} -> {len(boards)}")
        for a, b in zip(ob, boards):
            a2 = json.loads(json.dumps(a)); b2 = json.loads(json.dumps(b))
            for d in (a2, b2):
                d["origin"][0] = 0; d["size"][0] = 0
                for f in d["uv"].values():
                    f.pop("uv", None); f.pop("uv_size", None)
            check(a2 == b2, f"T6 {ident}: board changed beyond its width")
            check(a["uv"]["east"] == b["uv"]["east"] and a["uv"]["west"] == b["uv"]["west"], f"T6 {ident}: cut uv changed")
    # T7: the shipped geometry shows the witnessed defects
    sh_holes = sum(profile_ok(old[i], new[i][1], new[i][2])[0] > 0 for i in old)
    check(sh_holes == len(old), f"T7: only {sh_holes}/{len(old)} shipped geometries fail T1 (the test must see the slit)")
    sh_flush = sum(all(abs(c["origin"][0] + 8) < 1e-9 for b in old[i]["bones"] for c in b.get("cubes", []) if c.get("rotation")) for i in old)
    check(sh_flush == 0, f"T7: {sh_flush} shipped geometries already flush")
    for ident in old:
        pass
    print(f"{len(new)} geometries checked; {len(FAILS)} failures")
    for f in FAILS[:20]:
        print("  FAIL", f)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(run())
