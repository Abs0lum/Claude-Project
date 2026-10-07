#!/usr/bin/env python3
"""contact_gate.py — CONNECTION gate (his 12:38 report: legs coming apart from the body / feet from the legs).
Every pair of cube-carrying bones whose cubes touch in the bind pose (surface distance < TOUCH) must still touch in a
posed state. Distance = min over sample points on A's cube faces (5x5 per face, cube rotation applied) of the distance
to B's nearest cube (point -> oriented box, exact)."""
import sys

import numpy as np

sys.path.insert(0, "/home/claude/tools")
import std_cube as CU  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

TOUCH = 0.05


def _samples(c, A, t, n=5):
    lo, hi = CU.box(c)
    Rc, tc = CU.cube_affine(c)
    pts = []
    g = np.linspace(0, 1, n)
    for k in range(3):
        o = [i for i in range(3) if i != k]
        for side in (lo[k], hi[k]):
            for a in g:
                for b in g:
                    p = np.empty(3)
                    p[k] = side
                    p[o[0]] = lo[o[0]] + a * (hi[o[0]] - lo[o[0]])
                    p[o[1]] = lo[o[1]] + b * (hi[o[1]] - lo[o[1]])
                    pts.append(A @ (Rc @ p + tc) + t)
    return np.array(pts)


def _boxes(c, A, t):
    lo, hi = CU.box(c)
    Rc, tc = CU.cube_affine(c)
    M = A @ Rc
    return M, A @ tc + t, lo, hi


def dist(bones, a, b, aff=None):
    aff = aff or bone_affines(bones)
    by = {x["name"]: x for x in bones}
    best = np.inf
    for ca in by[a].get("cubes") or []:
        P = _samples(ca, *aff[a])
        for cb in by[b].get("cubes") or []:
            M, t, lo, hi = _boxes(cb, *aff[b])
            L = np.linalg.solve(M, (P - t).T).T            # into B's box frame (M is a rotation: lengths kept)
            d = np.linalg.norm(L - np.clip(L, lo, hi), axis=1)
            best = min(best, float(d.min()))
    return best


def touching_pairs(bones, names):
    aff = bone_affines(bones)
    by = {x["name"]: x for x in bones}
    cubed = [n for n in names if by.get(n, {}).get("cubes")]
    others = [x["name"] for x in bones if x.get("cubes")]
    pairs = set()
    for a in cubed:
        for b in others:
            if a != b and (b, a) not in pairs and min(dist(bones, a, b, aff), dist(bones, b, a, aff)) < TOUCH:
                pairs.add((a, b))
    return sorted(pairs)


def worst(posed_bones, pairs):
    aff = bone_affines(posed_bones)
    out = 0.0, None
    for a, b in pairs:
        d = min(dist(posed_bones, a, b, aff), dist(posed_bones, b, a, aff))
        if d > out[0]:
            out = d, (a, b)
    return out
