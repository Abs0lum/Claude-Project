#!/usr/bin/env python3
"""parrot_gap_scaled.py — R14 f02 ("the wings might still have minor gaps in flight; but HUGELY improved"), D-C306/D-C307.
parrot_wing_check.py posed the bones WITHOUT their non-zero scale channels (it used scale only to hide a subtree). The flight
wing's middle joint `…_wing_fly_rot` carries scale (1, sy, sz) from the JEM; the outer feathers (…_fly2) hang under it.
Here every bone's world affine = parent · T(pivot) · R · S · T(-pivot) (Java ModelPart / Bedrock bone order: scale in the
bone's own rotated frame, about its pivot), then per flight moment:
  gap  = the smallest distance between the outer-segment boxes and the inner-segment boxes (0 = touching / overlapping)
  mirror = left vs right mirrored IN THE BODY FRAME (not world x = 0)
Numbers only rule OUT (P1)."""
import sys, json
sys.path.insert(0, "/home/claude/tools")
from pathlib import Path
import numpy as np
import posed_preview as PP
import parrot_wing_check as PW
from equine_compare import rot_matrix
from entity_render import transform

DST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/claude/_build/rp07-1426")


def affines(bones, scales):
    by = {b["name"]: b for b in bones}; out = {}
    def get(n):
        if n in out: return out[n]
        b = by[n]; p = np.array(b.get("pivot", [0, 0, 0]), float)
        Rm = rot_matrix(list(b.get("rotation", [0, 0, 0]) or [0, 0, 0]))
        S = np.diag([float(v) for v in scales.get(n, [1.0, 1.0, 1.0])])
        L = Rm @ S; lt = p - L @ p
        par = b.get("parent")
        A0, t0 = get(par) if par and par in by else (np.eye(3), np.zeros(3))
        out[n] = (A0 @ L, A0 @ lt + t0); return out[n]
    for b in bones: get(b["name"])
    return out


def boxes(bones, aff, names):
    res = []
    for b in bones:
        if b["name"] not in names: continue
        A, t = aff[b["name"]]
        for c in b.get("cubes", []):
            o, s = np.array(c["origin"], float), np.array(c["size"], float); inf = c.get("inflate", 0) or 0
            lo, hi = o - inf, o + s + inf
            pts = [np.array([x, y, z]) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
            if any(c.get("rotation", [0, 0, 0]) or []): pts = [np.array(transform(list(q), c.get("pivot", [0, 0, 0]), c["rotation"])) for q in pts]
            res.append(np.array([A @ q + t for q in pts]))
    return res


def samples(B, n=7):
    o = B[0]; ex, ey, ez = B[4] - o, B[2] - o, B[1] - o
    g = np.linspace(0, 1, n)
    return np.array([o + ex * i + ey * j + ez * k for i in g for j in g for k in g])


def obb_dist(P, B):
    o = B[0]; M = np.stack([B[4] - o, B[2] - o, B[1] - o], 1)
    try: Minv = np.linalg.pinv(M)
    except Exception: return np.full(len(P), np.inf)
    q = (Minv @ (P - o).T).T; qc = np.clip(q, 0, 1)
    return np.linalg.norm((M @ (q - qc).T).T, axis=1)


def gap(A_boxes, B_boxes):
    if not A_boxes or not B_boxes: return None
    return float(min(obb_dist(samples(a), b).min() for a in A_boxes for b in B_boxes))


def main():
    env_fly = {"q.is_on_ground": 0.0, "q.modified_move_speed": 0.4}
    rows = []
    for k in range(40):
        t = round(0.05 * k, 2)
        bones, tw, th = PP.pose(DST, "parrot", PW.GID, t, extra_env=env_fly)
        sc = PW.scales(DST, env_fly, t)
        aff = affines(bones, sc); aff0 = affines(bones, {n: ([1.0] * 3 if min(abs(x) for x in v) > 1e-6 else v) for n, v in sc.items()})
        row = {"t": t}
        for s in ("left", "right"):
            outer = set(PW.subtree(bones, PW.OUTER[s])); inner = set(PW.subtree(bones, PW.FLIGHT[s])) - outer
            row[f"{s}_gap_scaled"] = gap(boxes(bones, aff, outer), boxes(bones, aff, inner))
            row[f"{s}_gap_unscaled"] = gap(boxes(bones, aff0, outer), boxes(bones, aff0, inner))
            row[f"{s}_rot_scale"] = [round(float(x), 3) for x in sc.get(f"{s}_wing_fly_rot", [1, 1, 1])]
        rows.append(row)
    for r in rows[::4]: print(r)
    for s in ("left", "right"):
        gs = [r[f"{s}_gap_scaled"] for r in rows if r[f"{s}_gap_scaled"] is not None]
        gu = [r[f"{s}_gap_unscaled"] for r in rows if r[f"{s}_gap_unscaled"] is not None]
        print(f"{s}: outer<->inner gap WITH scale: max {max(gs):.2f} px, median {np.median(gs):.2f} px | WITHOUT scale (old checker): max {max(gu):.2f} px")
    json.dump(rows, open("/home/claude/_docs/r14/parrot_gap_scaled.json", "w"), indent=0)


if __name__ == "__main__":
    main()
