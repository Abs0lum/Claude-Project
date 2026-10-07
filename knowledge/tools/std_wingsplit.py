#!/usr/bin/env python3
"""std_wingsplit.py — Standardization Phase 2, step B: cut each stiff one-piece wing into the TEMPLATE-BIRD v1.1 chain
(his T3 = b, T5 = b):   shoulder (the old wing bone: keeps pivot, bind rotation, animation, children)
                          ├─ wing_inner          piece  (0 … 47 % of the span — the parrot's inner / outer ratio)
                          └─ elbow  → wrist      joints on the cut line (true hinge position)
                               └─ primary_base_1 → primary_1  (47 … 64.7 %)
                                    └─ primary_base_2 → primary_2  (64.7 … 82.3 %)
                                         └─ primary_base_3 → primary_3  (82.3 … 100 %)
Every new joint has rotation 0, so the bind pose and every pose of the old animations stay IDENTICAL; the new joints only
move once the standard flight animation drives them (Phase 3 / 4).

Cutting a cube: the span axis = the cube's longest LOCAL axis (cube rotation / pivot are kept on every piece, so a rotated
cube is cut in its own frame); box UV is resolved to per-face UV first (bb_truth.face_uvs) and every face that crosses a
cut gets the matching sub-rectangle of its UV — the texture stays exactly where it was. Faces on the cut planes are not
created (they did not exist before; they would only show while a joint bends).
Gate: UV-sample correspondence — on every face of the OLD posed rig, a 5 x 5 grid of texture points must land at the same
3D position on some face of the NEW posed rig that shows the same texel, and vice versa (no extra visible surface).
"""
import copy
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
from bb_truth import face_uvs, truth_posed_faces  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

FRACTIONS = (0.47, 0.6467, 0.8233)  # cut planes as fractions of the wing span measured from the shoulder
FACES = ("north", "east", "south", "west", "up", "down")


def perface_uv(rect, face):
    """display rect [u1, v1, u2, v2] (bb_truth convention) -> Bedrock per-face {uv, uv_size}."""
    u1, v1, u2, v2 = rect
    if face in ("up", "down"):  # face_uvs: [a + c, b + d, a, b]
        return {"uv": [u2, v2], "uv_size": [u1 - u2, v1 - v2]}
    return {"uv": [u1, v1], "uv_size": [u2 - u1, v2 - v1]}


def face_corners(cube, face, rect):
    from bb_truth import truth_face_corners
    pts, _, _ = truth_face_corners(cube["origin"], cube["size"], 0, face, rect)
    return [np.array(p, float) for p in pts]


def cut_cube(cube, axis, cuts):
    """Split one cube along local axis `axis` (0 x, 1 y, 2 z) at file coordinates `cuts` (sorted, inside the cube).
    Returns [(lo, hi, new_cube)] slabs in increasing coordinate order."""
    infl = cube.get("inflate") or 0
    if infl:
        # an inflated cube draws its UV (sized by `size`) over a box grown by `inflate` on every side: the same picture
        # as a plain cube of the grown box with the per-face UV resolved from the original size
        rects0 = face_uvs(cube.get("uv", [0, 0]), list(cube["size"]), bool(cube.get("mirror", False)))  # as the renderer
        plain = {k: copy.deepcopy(v) for k, v in cube.items() if k not in ("uv", "mirror", "inflate", "origin", "size")}
        plain["origin"] = [cube["origin"][k] - infl for k in range(3)]
        plain["size"] = [cube["size"][k] + 2 * infl for k in range(3)]
        plain["uv"] = {f: perface_uv(r, f) for f, r in rects0.items()}
        return cut_cube(plain, axis, cuts)
    o, s = list(cube["origin"]), list(cube["size"])
    # sizes may be NEGATIVE (an inverted box): everything is computed with the signed size, exactly as the renderer does
    lo_all, hi_all = sorted((o[axis], o[axis] + s[axis]))
    rects = face_uvs(cube.get("uv", [0, 0]), s, bool(cube.get("mirror", False)))
    bounds = [lo_all] + [c for c in cuts if lo_all < c < hi_all] + [hi_all]
    out = []
    for lo, hi in zip(bounds, bounds[1:]):
        nc = {k: copy.deepcopy(v) for k, v in cube.items() if k not in ("uv", "mirror", "origin", "size")}
        no, ns = list(o), list(s)
        if s[axis] >= 0:
            no[axis], ns[axis] = lo, hi - lo
        else:  # keep the inversion: origin at the high end, negative size
            no[axis], ns[axis] = hi, lo - hi
        nc["origin"], nc["size"] = no, ns
        uv = {}
        for face, rect in rects.items():
            P = face_corners(cube, face, rect)
            du, dv = P[1] - P[0], P[3] - P[0]
            # which uv direction runs along the cut axis (file frame: x is mirrored in the display frame, use |du|)
            if abs(du[axis]) > 1e-9 or abs(dv[axis]) > 1e-9:
                d, which = (du, "u") if abs(du[axis]) > abs(dv[axis]) else (dv, "v")
                t0 = (lo - P[0][axis]) / d[axis]
                t1 = (hi - P[0][axis]) / d[axis]
                t0, t1 = sorted((max(0.0, min(1.0, t0)), max(0.0, min(1.0, t1))))
                u1, v1, u2, v2 = rect
                if which == "u":
                    # u(t) = u1 + t (u2 - u1) runs from P0 (t = 0) to P1 (t = 1): the sub-rect keeps that direction
                    a, b = u1 + t0 * (u2 - u1), u1 + t1 * (u2 - u1)
                    nr = [a, v1, b, v2]
                else:
                    a, b = v1 + t0 * (v2 - v1), v1 + t1 * (v2 - v1)
                    nr = [u1, a, u2, b]
                uv[face] = perface_uv(nr, face)
            else:
                # a cap face perpendicular to the axis: it belongs to the slab at its end
                pos = P[0][axis]
                if abs(pos - lo) < 1e-9 and lo == lo_all or abs(pos - hi) < 1e-9 and hi == hi_all:
                    uv[face] = perface_uv(rect, face)
        nc["uv"] = uv
        out.append((lo, hi, nc))
    return out


def span_axis(cubes, pivot):
    """the wing's span axis = the axis along which its cubes reach FARTHEST from the joint pivot (a broad plate can be
    deeper than it is long, so its longest side is not always the span — the WA duck's outer wing: 5 long, 7 deep)."""
    reach = []
    for k in range(3):
        ends = [e for c in cubes for e in (c["origin"][k], c["origin"][k] + c["size"][k])]
        reach.append(max(abs(e - pivot[k]) for e in ends))
    return int(np.argmax(reach))


def split_wing(bones, wing, side, fractions=FRACTIONS):
    """bones: list (already renamed: the wing bone is called `wing`). Returns new bone list with the chain inserted."""
    bones = copy.deepcopy(bones)
    by = {b["name"]: b for b in bones}
    W = by[wing]
    cubes = W.pop("cubes", [])
    assert cubes, f"{wing} has no cubes"
    piv = np.array(W.get("pivot", [0, 0, 0]), float)
    # step B keeps the rule of the APPROVED preview (his P1 10:58): a FOLDED wing's span is its longest side
    # (span_axis — reach from the joint — is used where a piece must be cut outward from its joint: step C)
    ext = np.array([max(abs(c["size"][k]) for c in cubes) for k in range(3)])
    axis = int(np.argmax(ext))
    lo = min(min(c["origin"][axis], c["origin"][axis] + c["size"][axis]) for c in cubes)
    hi = max(max(c["origin"][axis], c["origin"][axis] + c["size"][axis]) for c in cubes)
    near_lo = abs(piv[axis] - lo) <= abs(piv[axis] - hi)
    cuts = [lo + f * (hi - lo) if near_lo else hi - f * (hi - lo) for f in fractions]
    # slab index from the shoulder outward
    edges = sorted([lo, hi] + cuts)
    pieces = [[] for _ in range(4)]
    for c in cubes:
        cs = copy.deepcopy(c)
        cs.setdefault("mirror", bool(W.get("mirror", False)))  # a bone-level mirror applies to cubes without their own
        for a, b, nc in cut_cube(cs, axis, sorted(cuts)):
            mid = (a + b) / 2
            k = sum(1 for e in edges[1:-1] if mid > e) if near_lo else sum(1 for e in edges[1:-1] if mid < e)
            pieces[k].append(nc)
    # cross-section centre for joint pivots
    others = [k for k in range(3) if k != axis]
    centre = {k: (min(c["origin"][k] for c in cubes) + max(c["origin"][k] + c["size"][k] for c in cubes)) / 2 for k in others}

    def at(coord):
        p = [0.0, 0.0, 0.0]
        p[axis] = coord
        for k in others:
            p[k] = centre[k]
        return p
    s = side
    new = [
        {"name": f"wing_inner_{s}", "parent": wing, "pivot": list(piv), "cubes": pieces[0]},
        {"name": f"elbow_{s}", "parent": wing, "pivot": at(cuts[0])},
        {"name": f"wrist_{s}", "parent": f"elbow_{s}", "pivot": at(cuts[0])},
        {"name": f"primary_base_{s}_1", "parent": f"wrist_{s}", "pivot": at(cuts[0])},
        {"name": f"primary_{s}_1", "parent": f"primary_base_{s}_1", "pivot": at(cuts[0]), "cubes": pieces[1]},
        {"name": f"primary_base_{s}_2", "parent": f"primary_base_{s}_1", "pivot": at(cuts[1])},
        {"name": f"primary_{s}_2", "parent": f"primary_base_{s}_2", "pivot": at(cuts[1]), "cubes": pieces[2]},
        {"name": f"primary_base_{s}_3", "parent": f"primary_base_{s}_2", "pivot": at(cuts[2])},
        {"name": f"primary_{s}_3", "parent": f"primary_base_{s}_3", "pivot": at(cuts[2]), "cubes": pieces[3]},
    ]
    i = bones.index(W)
    return bones[:i + 1] + new + bones[i + 1:]


# ------------------------------------------------------------------ gate: UV-sample correspondence
def _samples(faces, n=5):
    out = []
    for f in faces:
        P = [np.array(p, float) for p in f.pts]
        u1, v1, u2, v2 = f.uv
        for i in range(n):
            for j in range(n):
                a, b = (i + 0.5) / n, (j + 0.5) / n
                pos = P[0] + a * (P[1] - P[0]) + b * (P[3] - P[0])
                out.append((u1 + a * (u2 - u1), v1 + b * (v2 - v1), pos))
    return out


def _covered(samples, faces, tol=1e-3):
    """every sample (u, v, pos) lies on some face that shows texel (u, v) at the same position (vectorised)."""
    if not faces:
        return len(samples)
    P0 = np.array([f.pts[0] for f in faces], float)
    PU = np.array([f.pts[1] for f in faces], float) - P0
    PV = np.array([f.pts[3] for f in faces], float) - P0
    UV = np.array([f.uv for f in faces], float)
    umin, umax = np.minimum(UV[:, 0], UV[:, 2]) - 1e-9, np.maximum(UV[:, 0], UV[:, 2]) + 1e-9
    vmin, vmax = np.minimum(UV[:, 1], UV[:, 3]) - 1e-9, np.maximum(UV[:, 1], UV[:, 3]) + 1e-9
    du = np.where(UV[:, 2] == UV[:, 0], 1.0, UV[:, 2] - UV[:, 0])
    dv = np.where(UV[:, 3] == UV[:, 1], 1.0, UV[:, 3] - UV[:, 1])
    miss = 0
    for u, v, pos in samples:
        m = (umin <= u) & (u <= umax) & (vmin <= v) & (v <= vmax)
        if not m.any():
            miss += 1
            continue
        a = ((u - UV[m, 0]) / du[m])[:, None]
        b = ((v - UV[m, 1]) / dv[m])[:, None]
        q = P0[m] + a * PU[m] + b * PV[m]
        if not (np.linalg.norm(q - pos, axis=1) < tol).any():
            miss += 1
    return miss


def uv_gate(bones_old, bones_new, tw, th):
    f_old = truth_posed_faces(bones_old, tw, th, bone_affines(bones_old))
    f_new = truth_posed_faces(bones_new, tw, th, bone_affines(bones_new))
    s_old, s_new = _samples(f_old), _samples(f_new)
    return _covered(s_old, f_new), _covered(s_new, f_old), len(s_old), len(s_new)
