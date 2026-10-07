#!/usr/bin/env python3
"""weather_overlays.py — program 228 B6 / EN2 (his 12:20: "lived-in houses age too; past a bad level the city fines the
household and repairs the house").

For every DWELLING family (cottages, townhouse, manor, farms, inn — the families a household lives in) this writes two
overlay structures the size of the family's stage files, structure void everywhere except the weatherable cells:
  <stem>_w  the WEATHERED block for each cell: stone bricks -> cracked (60 %) or mossy (40 %) stone bricks (by a cell hash),
            cobblestone -> mossy cobblestone. The clock places it with integrity 0.25 / 0.45 / 0.6 by age band and
            integritySeed = the building id, so the same house ages the same way every time (and more cells each band).
  <stem>_r  the REPAIR: the ORIGINAL block for each of those cells (placed whole when the council repairs the house) —
            never the stage files themselves, which would re-place a foundation's air and dirt.
The cells are the merged stages s0..s3 (a later stage wins), only blocks that are weatherable. Rotation and origin are the
stage files' (the clock places the overlays exactly as it places a stage).
Outputs: tools/bp02_overlay_228/structures/pw/stages/<stem>_w.mcstructure / _r.mcstructure + a JSON summary on stdout."""
import json
import sys
import zlib
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

SRC = Path("/home/claude/_build/bp02-228/structures/pw/stages")
OUT = Path("/home/claude/tools/bp02_overlay_228/structures/pw/stages")
DWELLINGS = ("cottage_s", "cottage_m", "cottage_l", "townhouse", "manor", "farm_wheat", "farm_terrace", "farm_cattle", "inn")
WEATHER = {"minecraft:stone_bricks": [("minecraft:cracked_stone_bricks", 60), ("minecraft:mossy_stone_bricks", 40)],
           "minecraft:cobblestone": [("minecraft:mossy_cobblestone", 100)]}


def weathered(name, x, y, z):
    opts = WEATHER[name]
    h = zlib.crc32(f"{x},{y},{z}".encode()) % 100
    acc = 0
    for n, w in opts:
        acc += w
        if h < acc:
            return n
    return opts[-1][0]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stems = sorted({f.name[:-len("_s4.mcstructure")] for f in SRC.glob("mvv_*_s4.mcstructure")})
    summary = {}
    for stem in stems:
        if not any(f"mvv_{d}_" in stem + "_" for d in DWELLINGS):
            continue
        stages = [SRC / f"{stem}_s{k}.mcstructure" for k in range(4)]
        if not all(p.exists() for p in stages):
            continue
        sts = [M.Structure.from_bytes(p.read_bytes()) for p in stages]
        size = sts[0].size
        if any(s.size != size for s in sts):
            print(f"SKIP {stem}: stage sizes differ {[s.size for s in sts]}")
            continue
        merged = {}
        for s in sts:
            sx, sy, sz = s.size
            for x in range(sx):
                for y in range(sy):
                    for z in range(sz):
                        e = s.get(x, y, z)
                        if e is not None:
                            merged[(x, y, z)] = e
        w = M.Structure(size)
        r = M.Structure(size)
        n = 0
        for (x, y, z), (name, states, _v) in merged.items():
            if name not in WEATHER:
                continue
            w.set(x, y, z, weathered(name, x, y, z), {})
            r.set(x, y, z, name, dict(states))
            n += 1
        if not n:
            continue
        (OUT / f"{stem}_w.mcstructure").write_bytes(w.to_bytes())
        (OUT / f"{stem}_r.mcstructure").write_bytes(r.to_bytes())
        summary[stem] = n
    print(json.dumps({"families": len(summary), "cells": summary}, indent=1))


if __name__ == "__main__":
    main()
