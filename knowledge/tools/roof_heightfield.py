#!/usr/bin/env python3
"""roof_heightfield.py — task #174 numbers (P2): the TOP SURFACE of a roof piece or an assembly, as a height field.

For every sample column (4 per block pixel by default, i.e. 1/4 px... default 1 sample per pixel, 16 per block) a ray
is cast straight down through the true-geometry faces (tools/civ_render.py: shipped RP geometry, BP permutation,
X-mirror law, the D-C487 measured transformation law) and the highest hit is kept. Output: a numpy array of heights in
block pixels (NaN = nothing under the ray), plus helpers to print it as text and to sample piece edges.

Library use:  hf = heightfield(items, x0, z0, nx, nz, step)   (items = civ_render.scene(...) output)
CLI:          roof_heightfield.py BLOCK STATE_JSON      -> prints the 16x16 top heights of one block in one state"""
import json
import os
import sys

import numpy as np

os.environ.setdefault("PW_STACK", "final")
sys.path.insert(0, "/home/claude/tools")
import civ_render as CR  # noqa: E402
from pathlib import Path  # noqa: E402

CR.BP = Path("/home/claude/_build/bp02-206/blocks")
CR.RP_MODELS = [Path("/home/claude/_build/rp04-156/models/blocks"), Path("/home/claude/_build/rp01-117/models/blocks")]


def _tris(items):
    T = []
    for f, _tex, _dim in items:
        p = np.array(f.pts, float)
        if len(p) < 3:
            continue
        for k in range(1, len(p) - 1):
            T.append((p[0], p[k], p[k + 1]))
    return T


def heightfield(items, x0, z0, nx, nz, step=1.0):
    """highest face hit for a downward ray at (x0 + (i+0.5)*step, z0 + (j+0.5)*step); returns hf[j, i] (z rows, x cols)."""
    T = _tris(items)
    A = np.array([t[0] for t in T]); B = np.array([t[1] for t in T]); C = np.array([t[2] for t in T])
    hf = np.full((nz, nx), np.nan)
    xs = x0 + (np.arange(nx) + 0.5) * step
    zs = z0 + (np.arange(nz) + 0.5) * step
    # barycentric in the xz plane, vectorised over triangles
    ax, az, bx, bz, cx, cz = A[:, 0], A[:, 2], B[:, 0], B[:, 2], C[:, 0], C[:, 2]
    det = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
    good = np.abs(det) > 1e-9
    A, B, C, det = A[good], B[good], C[good], det[good]
    ax, az, bx, bz, cx, cz = A[:, 0], A[:, 2], B[:, 0], B[:, 2], C[:, 0], C[:, 2]
    for j, z in enumerate(zs):
        for i, x in enumerate(xs):
            l1 = ((bz - cz) * (x - cx) + (cx - bx) * (z - cz)) / det
            l2 = ((cz - az) * (x - cx) + (ax - cx) * (z - cz)) / det
            l3 = 1 - l1 - l2
            m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if m.any():
                y = l1[m] * A[m, 1] + l2[m] * B[m, 1] + l3[m] * C[m, 1]
                hf[j, i] = y.max()
    return hf


def block_items(name, states):
    man = {"datum_y": 0, "blocks": [[0, 0, 0, name, states]]}
    return CR.scene(man, min_feet=-99)


def show(hf, every=2):
    rows = []
    for j in range(0, hf.shape[0], every):
        rows.append(" ".join("  ." if np.isnan(v) else f"{v:3.0f}" for v in hf[j, ::every]))
    return "\n".join(rows)


if __name__ == "__main__":
    name, st = sys.argv[1], json.loads(sys.argv[2])
    hf = heightfield(block_items(name, st), 0, 0, 16, 16)
    print(f"{name} {st}  (rows = north->south, cols = west->east, block pixels above the block floor)")
    print(show(hf, 1))
