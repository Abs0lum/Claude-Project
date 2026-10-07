#!/usr/bin/env python3
"""wing_bridge.py — the OVERLAP-BRIDGE fix for the wing-contact law (D-C310 addendum 02:00, his question "we can't give the
joint/connection pivots that allow the tip to retain its small extra sideways tilt?").

A rigid outer piece can stay edge-to-edge with the inner piece only while it turns about the shared edge (wing_hinge.py).
To KEEP the Patrix tilt, the joint gets a connector instead: every outer-piece cube at the join gets a BRIDGE cube on the same
bone, reaching `depth` px back from its root face into the inner piece. At rest the bridge sits hidden inside the inner piece;
when the tip tilts and the join would open, the bridge fills the opening. Each bridge face is textured with a 1-texel strip of
the outer piece's own texture at its root edge (the same face of the same cube, or of its partner cube for the Patrix
double-sided plates), so the filled opening continues the tip's own colours.
  * thickness inset 0.03 px each side (no z-fight with the inner piece's faces), hinge-axis inset 0.01 px
  * no face on the bridge's root end (coplanar with the tip's root, interior) and none on its far end (inside the inner piece)
apply(bones, a_root, b_root, spec, depth) -> (new bones, report)."""
import copy, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import wing_contact as W
from bb_truth import truth_face_corners, face_uvs

AXIS_FACES = {0: ("east", "west"), 1: ("up", "down"), 2: ("north", "south")}   # faces whose NORMAL lies on that file axis


def canon(o, s, face):
    """file-frame corners of `face` for the canonical rect (u,v) = (0,0),(1,0),(1,1),(0,1)"""
    pts, _, _ = truth_face_corners(o, s, 0.0, face, [0.0, 0.0, 1.0, 1.0])
    return [np.array(p, float) for p in pts]


def params(p, C):
    P00, P10, P11, P01 = C; M = np.stack([P10 - P00, P01 - P00], 1)
    lx, ly = np.linalg.lstsq(M, np.asarray(p, float) - P00, rcond=None)[0]
    return float(lx), float(ly)


def face_normal_axis(C):
    n = np.cross(C[1] - C[0], C[3] - C[0])
    return int(np.argmax(np.abs(n))) if np.linalg.norm(n) > 1e-9 else None


def strip_uv(src_cube, face, root_axis, root_val, bridge_o, bridge_s):
    """the bridge face's uv spec: a 1-texel strip of src_cube's `face` at its root edge (root_axis == root_val)"""
    o, s = src_cube["origin"], src_cube["size"]
    R = face_uvs(src_cube.get("uv"), s, bool(src_cube.get("mirror")))
    if face not in R: return None
    u1, v1, u2, v2 = R[face]
    Cs = canon(o, s, face); Cb = canon(bridge_o, bridge_s, face)
    # which source param runs along the extension axis, and where its root edge is
    dlx = abs((Cs[1] - Cs[0])[root_axis]); dly = abs((Cs[3] - Cs[0])[root_axis])
    ext = 0 if dlx >= dly else 1
    span = (Cs[1] - Cs[0]) if ext == 0 else (Cs[3] - Cs[0])
    if abs(span[root_axis]) < 1e-9: return None
    r = (root_val - Cs[0][root_axis]) / span[root_axis]                      # root edge in source params (0 or 1)
    r = min(max(r, 0.0), 1.0)
    uv_len = abs((u2 - u1) if ext == 0 else (v2 - v1))
    if uv_len < 1e-9: return None
    inward = (1.0 if r < 0.5 else -1.0) * min(1.0 / uv_len, 1.0)            # 1 texel into the face, from the root edge
    def uv_at(p):
        lx, ly = params(p, Cs)
        at_root = abs(p[root_axis] - root_val) < 1e-3
        lx, ly = min(max(lx, 0.0), 1.0), min(max(ly, 0.0), 1.0)
        if ext == 0: lx = r + (inward if at_root else 0.0)
        else: ly = r + (inward if at_root else 0.0)
        return u1 + lx * (u2 - u1), v1 + ly * (v2 - v1)
    a = uv_at(Cb[0]); b = uv_at(Cb[2]); c10 = uv_at(Cb[1]); c01 = uv_at(Cb[3])
    if abs(c10[0] - b[0]) > 1e-6 or abs(c10[1] - a[1]) > 1e-6 or abs(c01[0] - a[0]) > 1e-6 or abs(c01[1] - b[1]) > 1e-6:
        return {"_skew": True}                                               # the strip is not an axis-aligned rect: skip
    U1, V1, U2, V2 = a[0], a[1], b[0], b[1]
    if face in ("up", "down"): return {"uv": [round(U2, 5), round(V2, 5)], "uv_size": [round(U1 - U2, 5), round(V1 - V2, 5)]}
    return {"uv": [round(U1, 5), round(V1, 5)], "uv_size": [round(U2 - U1, 5), round(V2 - V1, 5)]}


def apply(bones, a_root, b_root, spec, depth):
    bones = copy.deepcopy(bones); by = {b["name"]: b for b in bones}
    aff0 = W.affines(bones, {})
    Bn = set(W.subtree(bones, b_root)); An = (set(W.subtree(bones, a_root)) - Bn) if a_root not in ("body", "body2") else {a_root}
    Ab, Bb = W.boxes(bones, aff0, An), W.boxes(bones, aff0, Bn)
    A_, t_ = aff0[b_root]; hinge = A_ @ np.array(by[b_root].get("pivot", [0, 0, 0]), float) + t_
    frames = W.root_frames(Bb, Ab, hinge)
    report = []
    for fr in frames:
        bone, ci, _ = Bb[fr["k"]]; cube = by[bone]["cubes"][ci]
        o = np.array(cube["origin"], float); s = np.array(cube["size"], float)
        lo, hi = np.minimum(o, o + s), np.maximum(o, o + s)
        ax, side = fr["ax"], fr["side"]
        root_val = hi[ax] if side == 1.0 else lo[ax]
        blo, bhi = lo.copy(), hi.copy()
        if side == 1.0: blo[ax], bhi[ax] = hi[ax], hi[ax] + depth
        else: blo[ax], bhi[ax] = lo[ax] - depth, lo[ax]
        rest = [k for k in range(3) if k != ax]
        w = min(rest, key=lambda k: hi[k] - lo[k]); h = [k for k in rest if k != w][0]
        blo[w] += 0.03; bhi[w] -= 0.03
        if bhi[w] <= blo[w]: mid = (lo[w] + hi[w]) / 2; blo[w], bhi[w] = mid - 0.001, mid + 0.001    # a 0-thick plate
        blo[h] += 0.01; bhi[h] -= 0.01
        bo, bs = [round(float(x), 5) for x in blo], [round(float(x), 5) for x in (bhi - blo)]
        faces = {}
        for fa in (a for a in range(3) if a != ax):
            for face in AXIS_FACES[fa]:
                cands = [cube] + [c for c in by[bone]["cubes"] if c is not cube]
                for src in cands:
                    uv = strip_uv(src, face, ax, root_val, bo, bs)
                    if uv and not uv.get("_skew"): faces[face] = uv; break
        if not faces: report.append((bone, ci, "no textured face - skipped")); continue
        if any(c.get("origin") == bo and c.get("size") == bs for c in by[bone]["cubes"]):
            report.append((bone, ci, "same bridge already on this bone (double-sided plate partner) - skipped")); continue
        bridge = {"origin": bo, "size": bs, "uv": faces}
        if cube.get("rotation"): bridge["pivot"] = cube.get("pivot", [0, 0, 0]); bridge["rotation"] = cube["rotation"]
        by[bone]["cubes"].append(bridge)
        report.append((bone, ci, f"bridge {depth} px on axis {'xyz'[ax]} ({'+' if side == 1.0 else '-'} root), faces {sorted(faces)}"))
    return bones, report
