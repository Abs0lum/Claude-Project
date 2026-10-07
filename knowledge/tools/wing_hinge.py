#!/usr/bin/env python3
"""wing_hinge.py — the TRUE-HINGE fix for the wing-contact law (D-C309): an outer wing piece may only turn about the line it
shares with the inner piece, so that line never leaves the inner piece.

For a hinge (outer bone B, own axis k = the join line's direction in B's own frame):
  1. a helper bone  B + "_hinge"  is inserted as B's only child: pivot ON the join line, rotation 0 (the bind pose is unchanged);
     B's cubes and B's children move under it;
  2. B's animated rotation is removed (B keeps its bind orientation), and the helper turns about its own axis k by what B's
     channel k did (the flap);  every other rotation component of B's channel (the part that swung the join open) is dropped;
  3. optional: `shift` (world px, bind pose) moves the whole outer piece onto the inner piece first (a designed gap).
Everything else (B's position / scale channels, other bones) is untouched.
apply(geo_bones, anim_bones, B, k, pivot=None, shift=None) -> (geo_bones, anim_bones) new copies."""
import copy, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import wing_contact as W


def subtree(bones, root):
    return W.subtree(bones, root)


def apply(bones, anim_bones, B, k, pivot=None, shift=None):
    bones = copy.deepcopy(bones); anim_bones = copy.deepcopy(anim_bones)
    by = {b["name"]: b for b in bones}
    H = B + "_hinge"; assert H not in by, H
    if shift is not None:
        aff0 = W.affines(bones, {})
        par = by[B].get("parent"); A_par = aff0[par][0] if par else np.eye(3)
        d = np.linalg.solve(A_par, np.asarray(shift, float))          # model-space move that shows as `shift` in the world
        for n in subtree(bones, B):
            b = by[n]
            b["pivot"] = [round(float(v + dv), 5) for v, dv in zip(b.get("pivot", [0, 0, 0]), d)]
            for c in b.get("cubes", []) or []:
                c["origin"] = [round(float(v + dv), 5) for v, dv in zip(c["origin"], d)]
                if "pivot" in c: c["pivot"] = [round(float(v + dv), 5) for v, dv in zip(c["pivot"], d)]
            for loc, val in list((b.get("locators") or {}).items()):
                p = val if isinstance(val, list) else val.get("offset")
                np_ = [round(float(v + dv), 5) for v, dv in zip(p, d)]
                if isinstance(val, list): b["locators"][loc] = np_
                else: val["offset"] = np_
    b = by[B]
    hp = [float(v) for v in (pivot if pivot is not None else b.get("pivot", [0, 0, 0]))]
    helper = {"name": H, "parent": B, "pivot": [round(v, 5) for v in hp], "rotation": [0.0, 0.0, 0.0]}
    if b.get("cubes"):
        helper["cubes"] = b.pop("cubes")
    for c in bones:
        if c.get("parent") == B: c["parent"] = H
    if b.get("mirror") is not None: helper["mirror"] = b["mirror"]
    bones.insert([x["name"] for x in bones].index(B) + 1, helper)
    ch = anim_bones.get(B, {})
    rot = ch.pop("rotation", None)
    if rot is not None:
        ax = rot[k] if isinstance(rot, list) else rot
        anim_bones[H] = {"rotation": [ax if i == k else 0.0 for i in range(3)]}
    if B in anim_bones and not anim_bones[B]: anim_bones.pop(B)
    return bones, anim_bones


def join_axis_own(bones, a_root, b_root, spec):
    """(k, pivot on the join line in B's model space): the own-frame axis the join line runs along + a point of that line"""
    aff0 = W.affines(bones, {})
    c0, u0, hinge, L = W.join_line(spec, a_root, b_root, bones, aff0)
    Rb = W.polar_rot(aff0[b_root][0]); u_own = Rb.T @ u0
    k = int(np.argmax(np.abs(u_own)))
    return k, u_own, c0, L


def best_axis(bones, a_root, b_root, spec, k=None):
    """the hinge LINE: parallel to the join line's own-frame axis k, through the outer piece's root region, chosen so it stays
    on / inside the inner piece along its whole length (the smallest worst distance; ties -> nearest the root face).
    Returns (k, pivot in model space for a child of b_root, worst distance px)."""
    aff0 = W.affines(bones, {})
    Bn = set(subtree(bones, b_root)); An = (set(subtree(bones, a_root)) - Bn) if a_root not in ("body", "body2") else {a_root}
    Ab, Bb = W.boxes(bones, aff0, An), W.boxes(bones, aff0, Bn)
    by = {x["name"]: x for x in bones}; A_, t_ = aff0[b_root]
    hinge = A_ @ np.array(by[b_root].get("pivot", [0, 0, 0]), float) + t_
    fr = W.root_frames(Bb, Ab, hinge)[0]
    box = Bb[fr["k"]][2]; o = box[0]; axes = [box[4] - o, box[2] - o, box[1] - o]
    rest = [a for a in range(3) if a != fr["ax"]]
    h = max(rest, key=lambda a: np.linalg.norm(axes[a])); w = [a for a in rest if a != h][0]
    Rb = W.polar_rot(A_); u_own = Rb.T @ (axes[h] / np.linalg.norm(axes[h]))
    kk = int(np.argmax(np.abs(u_own))) if k is None else k
    best = None
    ext_n = np.linalg.norm(axes[fr["ax"]])
    for e in np.linspace(0, min(1.0, 1.0 / max(ext_n, 1e-6)), 5):
        ee = (1 - e) if fr["side"] == 1.0 else e
        for wv in np.linspace(0, 1, 21):
            P = []
            for hv in np.linspace(0, 1, 41):
                p = [0, 0, 0]; p[fr["ax"]] = ee; p[h] = hv; p[w] = wv; P.append(p)
            pts = W.params_to_pts(box, P); d = float(W.dist_to(pts, Ab).max())
            score = (round(d, 3), round(e, 3), abs(wv - 0.5))
            if best is None or score < best[0]: best = (score, pts[0])
    (d, _, _), w0 = best
    piv = np.linalg.solve(A_, w0 - t_)
    return kk, [round(float(v), 5) for v in piv], d


def close_gap_shift(bones, a_root, b_root, spec, margin=0.05):
    """the world move (bind pose) that puts the outer piece's root line (mid thickness) onto the inner piece: the mean of
    the nearest-point vectors from the 21 root stations, lengthened by `margin` px (a hair of overlap, no seam)"""
    aff0 = W.affines(bones, {})
    Bn = set(subtree(bones, b_root)); An = (set(subtree(bones, a_root)) - Bn) if a_root not in ("body", "body2") else {a_root}
    Ab, Bb = W.boxes(bones, aff0, An), W.boxes(bones, aff0, Bn)
    by = {x["name"]: x for x in bones}; A_, t_ = aff0[b_root]
    hinge = A_ @ np.array(by[b_root].get("pivot", [0, 0, 0]), float) + t_
    fr = W.root_frames(Bb, Ab, hinge)[0]; box = Bb[fr["k"]][2]
    vecs = []
    for i in range(21):
        P = W.params_to_pts(box, [fr["fib"][(i, 2)][0]])[0]
        best = None
        for _, _, Bx in Ab:
            o = Bx[0]; M = np.stack([Bx[4] - o, Bx[2] - o, Bx[1] - o], 1)
            q = np.clip(np.linalg.pinv(M) @ (P - o), 0, 1); near = M @ q + o
            if best is None or np.linalg.norm(near - P) < np.linalg.norm(best): best = near - P
        vecs.append(best)
    v = np.mean(vecs, 0); n = float(np.linalg.norm(v))
    return (v * (1 + margin / n)).tolist() if n > 1e-9 else [0.0, 0.0, 0.0], n


def apply_split(bones, anim_bones, B, k, twist_pivot, swing_pivot):
    """keep the WHOLE Patrix motion, but re-seat it: B -> B_swing (the tilt / sweep components, about the MIDDLE of the join
    line) -> B_hinge (the flap about the join line itself). B keeps its bind orientation; its cubes / children move under
    B_hinge. A sideways tilt about the middle of the edge moves each end half as far as one about a corner, and the half that
    retreats stays over the inner piece, where an overlap bridge (wing_bridge.py) covers it."""
    bones = copy.deepcopy(bones); anim_bones = copy.deepcopy(anim_bones)
    by = {b["name"]: b for b in bones}
    S, H = B + "_swing", B + "_hinge"; assert S not in by and H not in by
    b = by[B]
    sw = {"name": S, "parent": B, "pivot": [round(float(v), 5) for v in swing_pivot], "rotation": [0.0, 0.0, 0.0]}
    hg = {"name": H, "parent": S, "pivot": [round(float(v), 5) for v in twist_pivot], "rotation": [0.0, 0.0, 0.0]}
    if b.get("cubes"): hg["cubes"] = b.pop("cubes")
    for c in bones:
        if c.get("parent") == B: c["parent"] = H
    i = [x["name"] for x in bones].index(B)
    bones[i + 1:i + 1] = [sw, hg]
    ch = anim_bones.get(B, {}); rot = ch.pop("rotation", None)
    if rot is not None:
        rot = rot if isinstance(rot, list) else [rot] * 3
        anim_bones[S] = {"rotation": [rot[i2] if i2 != k else 0.0 for i2 in range(3)]}
        anim_bones[H] = {"rotation": [rot[i2] if i2 == k else 0.0 for i2 in range(3)]}
    if B in anim_bones and not anim_bones[B]: anim_bones.pop(B)
    return bones, anim_bones


def line_midpoint(bones, a_root, b_root, spec, pivot):
    """the join line's middle: the hinge pivot moved to the centre of the root cube along the line's own axis"""
    aff0 = W.affines(bones, {})
    Bn = set(subtree(bones, b_root)); An = (set(subtree(bones, a_root)) - Bn) if a_root not in ("body", "body2") else {a_root}
    Ab, Bb = W.boxes(bones, aff0, An), W.boxes(bones, aff0, Bn)
    by = {x["name"]: x for x in bones}; A_, t_ = aff0[b_root]
    hinge = A_ @ np.array(by[b_root].get("pivot", [0, 0, 0]), float) + t_
    fr = W.root_frames(Bb, Ab, hinge)[0]; bone, ci, box = Bb[fr["k"]]
    c = by[bone]["cubes"][ci]; o = np.array(c["origin"], float); s = np.array(c["size"], float)
    lo, hi = np.minimum(o, o + s), np.maximum(o, o + s)
    L = hi - lo; rest = [a for a in range(3) if a != fr["ax"]]; h = max(rest, key=lambda a: L[a])
    mid = np.array(pivot, float); mid[h] = (lo[h] + hi[h]) / 2
    return mid.tolist(), h


def shift_subtree(bones, B, shift):
    """move the whole outer piece (B and everything under it) by `shift` world px in the bind pose (a pure translation)"""
    bones = copy.deepcopy(bones); by = {b["name"]: b for b in bones}
    aff0 = W.affines(bones, {})
    par = by[B].get("parent"); A_par = aff0[par][0] if par else np.eye(3)
    d = np.linalg.solve(A_par, np.asarray(shift, float))
    for n in subtree(bones, B):
        b = by[n]
        b["pivot"] = [round(float(v + dv), 5) for v, dv in zip(b.get("pivot", [0, 0, 0]), d)]
        for c in b.get("cubes", []) or []:
            c["origin"] = [round(float(v + dv), 5) for v, dv in zip(c["origin"], d)]
            if "pivot" in c: c["pivot"] = [round(float(v + dv), 5) for v, dv in zip(c["pivot"], d)]
    return bones, [round(float(x), 5) for x in d]


def hinge_fix(bones, anim_bones, a_root, b_root, spec, close_gap=False):
    """the his-pick-A fix (D-C310): [seat the outer piece on the inner one] + turn it only about the shared line"""
    rep = {"outer": b_root}
    if close_gap:
        sh, gap = close_gap_shift(bones, a_root, b_root, spec)
        bones, dmodel = shift_subtree(bones, b_root, sh)
        rep.update(gap_px=round(gap, 3), shift_world=[round(x, 4) for x in sh], shift_model=dmodel)
    k, piv, worst = best_axis(bones, a_root, b_root, spec)
    bones, anim_bones = apply(bones, anim_bones, b_root, k, pivot=piv)
    rep.update(axis="xyz"[k], pivot=piv, line_worst_px=round(worst, 3))
    return bones, anim_bones, rep
