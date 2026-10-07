#!/usr/bin/env python3
"""wing_gap.py — WING-CONTACT measurement for standardized wings: for every pair of NEIGHBOURING wing pieces (inner ->
primary 1 -> 2 -> 3, flight wing), the corners of the face they share in the bind pose are carried by EACH piece's own
pose transform; the distance between the two copies of a corner is the gap. Max over corners x moments = the wing's gap."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/home/claude/tools")
import posed_preview as PP  # noqa: E402
from equine_compare import bone_affines  # noqa: E402
import std_cube as CU  # noqa: E402


def shared_corners(bones, a, b):
    """bind-pose world points where piece a's box touches piece b's box (corners of their contact face)."""
    aff = bone_affines(bones)
    by = {x["name"]: x for x in bones}

    def boxes(n):
        A, t = aff[n]
        out = []
        for c in by[n].get("cubes") or []:
            out.append([A @ p + t for p in CU.corners(c)])   # cube rotation applied
        return out
    pa = [p for bx in boxes(a) for p in bx]
    pb = [p for bx in boxes(b) for p in bx]
    shared = [p for p in pa if any(np.linalg.norm(p - q) < 1e-3 for q in pb)]
    return shared


def gap(bones_bind, anim_bones, env_list, pairs, separating_only=True):
    """max gap (px) over pairs and env moments. separating_only: a corner pair counts only when the two copies move
    APART along the span (an opening gap); corners pressing together (the closing side of a hinge) do not."""
    worst = 0.0
    contacts = {(a, b): shared_corners(bones_bind, a, b) for a, b in pairs}
    aff0 = bone_affines(bones_bind)
    for env in env_list:
        posed = PP.posed_bones(bones_bind, anim_bones, dict(env))
        aff = bone_affines(posed)
        for (a, b), pts in contacts.items():
            for p in pts:
                # p in bind world -> each piece's file frame -> posed world
                for n in (a, b):
                    pass
                A0a, t0a = aff0[a]
                A0b, t0b = aff0[b]
                la = np.linalg.solve(A0a, p - t0a)
                lb = np.linalg.solve(A0b, p - t0b)
                Aa, ta = aff[a]
                Ab, tb = aff[b]
                # a position channel shifts the posed subtree's pivots + cubes in file coordinates (posed_preview); the
                # bind-pose local point is shifted with them, or the hinge rotations would count the slide again
                byp = {x["name"]: x for x in posed}
                bya = {x["name"]: x for x in bones_bind}
                da = np.array(byp[a].get("pivot", [0, 0, 0]), float) - np.array(bya[a].get("pivot", [0, 0, 0]), float)
                db = np.array(byp[b].get("pivot", [0, 0, 0]), float) - np.array(bya[b].get("pivot", [0, 0, 0]), float)
                pa_, pb_ = Aa @ (la + da) + ta, Ab @ (lb + db) + tb
                d = float(np.linalg.norm(pa_ - pb_))
                if separating_only:
                    # opening = b's copy lies OUTSIDE a's posed box (farther from a's centre than a's own copy)
                    ca = np.mean([Aa @ CU.centre(c) + ta
                                  for c in {x["name"]: x for x in posed}[a]["cubes"]], axis=0)
                    if np.linalg.norm(pb_ - ca) <= np.linalg.norm(pa_ - ca) + 1e-6:
                        d = 0.0
                worst = max(worst, d)
    return worst
