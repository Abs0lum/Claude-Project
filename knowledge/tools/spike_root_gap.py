#!/usr/bin/env python3
"""spike_root_gap.py — D-C285: how far each spike card's nearest OPAQUE texel sits from the pufferfish body (px), as Bedrock draws
the file (bb_truth face placement). His R8 b18 "spikes seem disconnected at fully grown size" = the old geometry's cards carry the
spike art mirrored, so the opaque roots sit on the far edge.  API: gaps(bones, tw, th, texture_png) -> {bone: gap px}"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines
from bb_truth import truth_posed_faces


def _body_box(bones, aff):
    best = None
    for b in bones:
        for c in b.get("cubes", []):
            if min(c["size"]) >= 4 and (best is None or np.prod(c["size"]) > np.prod(best[1]["size"])): best = (b, c)
    b, c = best; A, t = aff[b["name"]]
    o, s = np.array(c["origin"], float), np.array(c["size"], float)
    corners = [o + s * np.array([i, j, k]) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    # the geometry frame is mirrored in x for display; bb_truth faces are in FILE coords, so use file coords here too
    W = np.array([A @ p + t for p in corners])
    return W.min(0), W.max(0)


def gaps(bones, tw, th, tex_png):
    aff = bone_affines(bones)
    lo, hi = _body_box(bones, aff)
    alpha = np.asarray(Image.open(tex_png).convert("RGBA"))[..., 3]
    H, W_ = alpha.shape
    faces = truth_posed_faces(bones, tw, th, aff)
    out = {}
    for f in faces:
        name = f.bone if hasattr(f, "bone") else f[4]
        if "spike" not in name.lower(): continue
        P = np.array(f.pts, float); u0, v0, u1, v1 = f.uv
        x0, x1 = sorted((u0 * W_, u1 * W_)); y0, y1 = sorted((v0 * H, v1 * H))
        best = out.get(name, 1e9)
        for py in range(int(np.floor(y0)), int(np.ceil(y1))):
            for px in range(int(np.floor(x0)), int(np.ceil(x1))):
                if not (0 <= px < W_ and 0 <= py < H) or alpha[py, px] < 128: continue
                s = ((px + 0.5) - u0 * W_) / ((u1 - u0) * W_ or 1); tt = ((py + 0.5) - v0 * H) / ((v1 - v0) * H or 1)
                q = (1 - s) * (1 - tt) * P[0] + s * (1 - tt) * P[1] + s * tt * P[2] + (1 - s) * tt * P[3]
                d = np.linalg.norm(np.maximum(0, np.maximum(lo - q, q - hi)))
                best = min(best, float(d))
        out[name] = best
    return out
