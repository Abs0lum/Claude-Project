#!/usr/bin/env python3
"""geo_preview.py — quick isometric preview of block geometries (boxes + rotations) coloured by material instance.
Usage: geo_preview.py GEO.json OUT.png id1[:elev,azim] id2 ...   (angles in degrees; default elev 28, azim -50)
Reads: format 1.16.0 geometry files (origin/size/pivot/rotation in cubes).  Local -z = toward the placer.
"""
import json, math, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

COLORS = {"*": "#9a9a9a", "top": "#8a8a8a", "soot": "#2f2a27", "bed": "#c8551e", "log": "#6b4526", "log_end": "#a8865a",
          "flame": "#ff9a1f", "end": "#b89a6a"}
ALPHA = {"flame": 0.55}

def rot_x(p, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x, y, z = p; return [x, y * c - z * s, y * s + z * c]
def rot_y(p, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x, y, z = p; return [x * c + z * s, y, -x * s + z * c]
def rot_z(p, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x, y, z = p; return [x * c - y * s, x * s + y * c, z]

def transform(p, pivot, rot):
    # Bedrock cube/bone rotation — the VERIFIED law L-ROT-DIR (D-C255, 2026-09-27; vanilla wolf_armor/cow/llama files,
    # Blockbench codec algebra, witnessed cow/wolf/roofs): in file coordinates a rotation [rx, ry, rz] acts as
    # Rz(-rz) . Ry(+ry) . Rx(-rx) with right-handed matrices, X applied first.  +90 X: y' = py + (z - pz),
    # z' = pz - (y - py).  +90 Y: x' = px + (z - pz), z' = pz - (x - px).  +rz tips the top toward file +x.
    # (The pre-09-27 version negated all three angles and applied Z first — correct for X-only pieces, MIRRORED for
    # Y rotations, and wrong for compound rotations; see D-C255 RETRO-SWEEP.)
    q = [p[i] - pivot[i] for i in range(3)]
    q = rot_x(q, -rot[0]); q = rot_y(q, rot[1]); q = rot_z(q, -rot[2])
    return [q[i] + pivot[i] for i in range(3)]

def faces_of(cube):
    o, s = cube["origin"], cube["size"]
    infl = cube.get("inflate", 0)
    x0, y0, z0 = o[0] - infl, o[1] - infl, o[2] - infl
    x1, y1, z1 = o[0] + s[0] + infl, o[1] + s[1] + infl, o[2] + s[2] + infl
    P = {"a": [x0, y0, z0], "b": [x1, y0, z0], "c": [x1, y1, z0], "d": [x0, y1, z0], "e": [x0, y0, z1], "f": [x1, y0, z1], "g": [x1, y1, z1], "h": [x0, y1, z1]}
    F = {"north": ["a", "b", "c", "d"], "south": ["e", "f", "g", "h"], "west": ["a", "d", "h", "e"], "east": ["b", "c", "g", "f"], "up": ["d", "c", "g", "h"], "down": ["a", "b", "f", "e"]}
    piv, rot = cube.get("pivot", [0, 0, 0]), cube.get("rotation", [0, 0, 0])
    out = []
    for name, keys in F.items():
        if "uv" in cube and name not in cube["uv"]: continue   # omitted face
        inst = cube.get("uv", {}).get(name, {}).get("material_instance", "*")
        pts = [transform(P[k], piv, rot) for k in keys]
        out.append((name, inst, pts))
    return out

def main():
    geo_path, out_path, specs = sys.argv[1], sys.argv[2], sys.argv[3:]
    doc = json.load(open(geo_path))
    geos = {g["description"]["identifier"]: g for g in doc["minecraft:geometry"]}
    n = len(specs)
    fig = plt.figure(figsize=(6 * n, 6), dpi=110)
    for i, spec in enumerate(specs):
        gid, _, ang = spec.partition(":")
        elev, azim = (28, -50) if not ang else map(float, ang.split(","))
        ax = fig.add_subplot(1, n, i + 1, projection="3d")
        polys, cols = [], []
        for b in geos[gid]["bones"]:
            for c in b["cubes"]:
                for name, inst, pts in faces_of(c):
                    # matplotlib axes: X = local x, Y = local z, Z = local y  (so "up" is up)
                    polys.append([(p[0], p[2], p[1]) for p in pts])
                    col = matplotlib.colors.to_rgba(COLORS.get(inst, "#d070d0"), ALPHA.get(inst, 1.0))
                    cols.append(col)
        pc = Poly3DCollection(polys, facecolors=cols, edgecolors=(0, 0, 0, 0.25), linewidths=0.4)
        ax.add_collection3d(pc)
        # cell wireframe
        for (a, b) in [((-8,-8,0),(8,-8,0)),((8,-8,0),(8,8,0)),((8,8,0),(-8,8,0)),((-8,8,0),(-8,-8,0)),
                       ((-8,-8,16),(8,-8,16)),((8,-8,16),(8,8,16)),((8,8,16),(-8,8,16)),((-8,8,16),(-8,-8,16)),
                       ((-8,-8,0),(-8,-8,16)),((8,-8,0),(8,-8,16)),((8,8,0),(8,8,16)),((-8,8,0),(-8,8,16))]:
            ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color="#444", lw=0.8, ls=":")
        ax.set_xlim(-10, 10); ax.set_ylim(-12, 12); ax.set_zlim(-1, 19)
        ax.set_box_aspect((20, 24, 20))
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel("x"); ax.set_ylabel("z  (−z = toward the placer)"); ax.set_zlabel("y")
        ax.set_title(gid, fontsize=11)
    fig.tight_layout(); fig.savefig(out_path); print("wrote", out_path)

if __name__ == "__main__":
    main()
