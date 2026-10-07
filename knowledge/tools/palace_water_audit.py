#!/usr/bin/env python3
"""palace_water_audit.py — where does the water get into the palace block? Reads a civtest log's region dump ([CIVDUMP]
rows + [CIVPAL] palette, written by the probe at the end of a run) and the run's palace record, then reports, for the
128 x 128 block at (x0, z0) with floor y H:
  * per edge (west / east / north / south): the water surface just OUTSIDE (max water y per column, histogram), the
    retaining wall's top in the edge column (highest stone_bricks), and the INFLOW cells — a perimeter cell where water
    stands outside at y >= H - 1 and the cell inside at the same y is water / air / a door (the water's way in);
  * inside: the water surface histogram and the count of water cells at and above the floor;
  * the top rows of the heightmap above the block (water falling from above).
Usage: palace_water_audit.py LOG [OUT.png]   (OUT: a plan of the block + 24 around it: water surface tinted blue, walls grey,
inflow cells red)
Complexity: O(dump cells) once; memory: one 16-bit array per layer."""
import json
import re
import sys
from array import array
from collections import Counter
from pathlib import Path

WATER = ("minecraft:water", "minecraft:flowing_water")
PASS = ("minecraft:air", "minecraft:light_block_14", "minecraft:light_block_15")


def load_dump(log):
    head = pal_rec = None
    rows, pal = {}, {}
    palace = None
    for line in Path(log).read_text(errors="ignore").splitlines():
        if "[CIVTEST]" in line and '"dumphead"' in line:
            head = json.loads(line.split("[CIVTEST] ", 1)[1])
        elif "[CIVTEST]" in line and '"step":"palace"' in line and '"pieces"' in line:
            palace = json.loads(line.split("[CIVTEST] ", 1)[1])["palace"]
        m = re.search(r"\[CIVDUMP\] (-?\d+) (\d+) (.*)$", line)
        if m:
            rows.setdefault(int(m.group(1)), {})[int(m.group(2))] = m.group(3)
        m = re.search(r"\[CIVPAL\] (\d+) (\[.*\])\s*$", line)
        if m:
            for j, e in enumerate(json.loads(m.group(2))):
                pal[int(m.group(1)) + j] = e
    assert head and pal, "no dump in this log"
    x0, x1, z0, z1 = head["x0"], head["x1"], head["z0"], head["z1"]
    nx, nz = x1 - x0 + 1, z1 - z0 + 1
    layers = {}
    for y in rows:
        s = "".join(rows[y][i] for i in sorted(rows[y]))
        a = array("H", [65535]) * (nx * nz)
        i = 0
        for run in s.split(","):
            if not run:
                continue
            k, n = (run.split("*") + ["1"])[:2]
            k, n = int(k), int(n)
            if k >= 0:
                for j in range(i, i + n):
                    a[j] = k
            i += n
        layers[y] = a
    names = {k: v[0] for k, v in pal.items()}
    return head, layers, names, palace, (x0, z0, nx, nz)


def main(log, out=None):
    head, layers, names, palace, (gx0, gz0, nx, nz) = load_dump(log)
    assert palace, "no palace record in this log"
    px0, pz0, H = palace["x0"], palace["z0"], palace["H"]
    ys = sorted(layers)
    print(f"dump x {gx0}..{gx0 + nx - 1} z {gz0}..{gz0 + nz - 1} y {ys[0]}..{ys[-1]}; palace block x {px0}..{px0 + 127} z {pz0}..{pz0 + 127} H {H} rot {palace['rot']}")

    def name_at(x, y, z):
        if not (gx0 <= x < gx0 + nx and gz0 <= z < gz0 + nz) or y not in layers:
            return None
        k = layers[y][(x - gx0) * nz + (z - gz0)]
        return "minecraft:air" if k == 65535 else names.get(k, "?")

    def water_top(x, z):
        best = None
        for y in ys:
            if name_at(x, y, z) in WATER:
                best = y
        return best

    def wall_top(x, z):
        best = None
        for y in ys:
            if name_at(x, y, z) == "minecraft:stone_bricks":
                best = y
        return best

    edges = {"west": [(px0, pz0 + j, -1, 0) for j in range(128)], "east": [(px0 + 127, pz0 + j, 1, 0) for j in range(128)],
             "north": [(px0 + i, pz0, 0, -1) for i in range(128)], "south": [(px0 + i, pz0 + 127, 0, 1) for i in range(128)]}
    inflow = []
    for side, cells in edges.items():
        outs, walls, ins = Counter(), Counter(), Counter()
        for (x, z, dx, dz) in cells:
            wt = water_top(x + dx, z + dz); outs[wt if wt is not None else "dry"] += 1
            wl = wall_top(x, z); walls[wl if wl is not None else "none"] += 1
            wi = water_top(x, z); ins[wi if wi is not None else "dry"] += 1
            for y in ys:
                if y < H - 1:
                    continue
                if name_at(x + dx, y, z + dz) in WATER and (name_at(x, y, z) in WATER or name_at(x, y, z) in PASS or "door" in (name_at(x, y, z) or "")):
                    inflow.append((side, x, y, z, name_at(x, y, z)))
        print(f"\n{side.upper()} edge: outside water surface {dict(sorted(outs.items(), key=lambda kv: str(kv[0])))}")
        print(f"  wall top in the edge column {dict(sorted(walls.items(), key=lambda kv: str(kv[0])))}")
        print(f"  inside edge column water surface {dict(sorted(ins.items(), key=lambda kv: str(kv[0])))}")
    print(f"\nINFLOW cells (outside water at y >= H-1 meets water / air / a door inside): {len(inflow)}")
    bys = Counter((s, y) for s, x, y, z, n in inflow)
    for (s, y), n in sorted(bys.items()):
        print(f"  {s} y {y}: {n} cells; e.g. {[c[1:] for c in inflow if c[0] == s and c[2] == y][:4]}")
    # inside the block
    surf = Counter()
    above = 0
    for i in range(128):
        for j in range(128):
            wt = water_top(px0 + i, pz0 + j)
            surf[wt if wt is not None else "dry"] += 1
            for y in ys:
                if y >= H - 1 and name_at(px0 + i, y, pz0 + j) in WATER:
                    above += 1
    print(f"\nINSIDE: water surface per column {dict(sorted(surf.items(), key=lambda kv: str(kv[0])))}; water cells at y >= H-1: {above}")
    # water above the block's top of dump (falls from the sky?)
    top_y = ys[-1]
    fall = sum(1 for i in range(128) for j in range(128) if name_at(px0 + i, top_y, pz0 + j) in WATER)
    print(f"water cells in the dump's top layer y {top_y} over the block: {fall}")
    if out:
        from PIL import Image
        S = 3
        M = 24
        img = Image.new("RGB", ((128 + 2 * M) * S, (128 + 2 * M) * S), (20, 20, 24))
        px = img.load()
        for i in range(-M, 128 + M):
            for j in range(-M, 128 + M):
                x, z = px0 + i, pz0 + j
                wt = water_top(x, z)
                wl = wall_top(x, z)
                col = (60, 60, 60)
                if wl is not None and wl >= H - 1:
                    col = (170, 170, 175)
                if wt is not None:
                    d = max(0, min(10, wt - (H - 1)))
                    col = (30, 60 + d * 10, 160 + d * 9)
                for a in range(S):
                    for b in range(S):
                        px[(j + M) * S + a, (i + M) * S + b] = col
        for (s, x, y, z, n) in inflow:
            i, j = x - px0, z - pz0
            for a in range(S):
                for b in range(S):
                    px[(j + M) * S + a, (i + M) * S + b] = (255, 60, 60)
        img.save(out)
        print("plan ->", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
