#!/usr/bin/env python3
"""bb_truth.py — face-UV placement exactly as Bedrock shows it (D-C278).

The previews since D-C255 placed every face by its NAME in the geometry FILE frame (east = file +x, the up face with v
running north->south). Bedrock does not: the file frame is the display frame with x mirrored, and Blockbench — whose
display is what the game shows — reads a Bedrock cube like this (bedrock.js parseCube / compileCube, cube.js UVToLocal):
    display from = (-(o.x + s.x), o.y, o.z)   display to = (-o.x, o.y + s.y, o.z + s.z)
    per-face uv (a, b) size (c, d):  N/E/S/W -> [a, b, a+c, b+d]    up/down -> [a+c, b+d, a, b]   (the 180 deg turn)
    box uv (u, v): Blockbench's box layout (cube.js updateUV face_list), mirror swaps east/west and flips u
then places the texture on each face with UVToLocal. This module does the same, and hands the corners back in FILE
coordinates so the existing pose chain (entity_render.transform, bone_affines) and render_entity stay unchanged.

API: truth_face_corners(o, s, infl, face, uvspec, mirror) -> (pts[4] in file coords, (u0, v0, u1, v1) in texels, dim_name)
     truth_posed_faces(bones, tw, th, aff) -> [Face]   (drop-in for equine_compare.posed_faces)"""
import sys
import numpy as np
sys.path.insert(0, "/home/claude/tools")
from block_render import Face
from entity_render import transform

FACES = ("north", "east", "south", "west", "up", "down")


def _lerp(p, q, t):
    return p + (q - p) * t


def box_face_uvs(u, v, s, mirror=False):
    """Blockbench cube.js updateUV (box_uv): {face: [u1, v1, u2, v2]} in texels."""
    w, h, d = s
    fl = [["east", [0, d], [d, h]], ["west", [d + w, d], [d, h]], ["up", [d + w, d], [-w, -d]],
          ["down", [d + 2 * w, 0], [-w, d]], ["south", [2 * d + w, d], [w, h]], ["north", [d, d], [w, h]]]
    if mirror:
        for f in fl:
            f[1][0] += f[2][0]; f[2][0] *= -1
        fl[0][1], fl[1][1] = fl[1][1][:], fl[0][1][:]
        fl[0][2], fl[1][2] = fl[1][2][:], fl[0][2][:]
    return {n: [fr[0] + u, fr[1] + v, fr[0] + sz[0] + u, fr[1] + sz[1] + v] for n, fr, sz in fl}


def face_uvs(uvspec, s, mirror):
    """{face: [u1, v1, u2, v2]} (Blockbench display convention) for a Bedrock cube's `uv`."""
    if isinstance(uvspec, dict):
        out = {}
        for name, f in uvspec.items():
            if name not in FACES or not isinstance(f, dict) or "uv" not in f: continue
            a, b = f["uv"]; c, d = f.get("uv_size", [s[0], s[1]])
            out[name] = [a + c, b + d, a, b] if name in ("up", "down") else [a, b, a + c, b + d]
        return out
    u, v = (uvspec or [0, 0])[:2]
    return box_face_uvs(u, v, s, mirror)


def _local(face, fr, to, uv, U, V):
    """cube.js UVToLocal: display-frame point of texel (U, V) on `face` (rotation 0)."""
    lx = 0.0 if uv[2] == uv[0] else (U - uv[0]) / (uv[2] - uv[0])
    ly = 0.0 if uv[3] == uv[1] else (V - uv[1]) / (uv[3] - uv[1])
    x, y, z = fr[0], fr[1], fr[2]
    if face == "east": x = to[0]; y = _lerp(to[1], fr[1], ly); z = _lerp(to[2], fr[2], lx)
    elif face == "west": y = _lerp(to[1], fr[1], ly); z = _lerp(fr[2], to[2], lx)
    elif face == "up": y = to[1]; z = _lerp(fr[2], to[2], ly); x = _lerp(fr[0], to[0], lx)
    elif face == "down": z = _lerp(to[2], fr[2], ly); x = _lerp(fr[0], to[0], lx)
    elif face == "south": z = to[2]; y = _lerp(to[1], fr[1], ly); x = _lerp(fr[0], to[0], lx)
    elif face == "north": y = _lerp(to[1], fr[1], ly); x = _lerp(to[0], fr[0], lx)
    return [x, y, z]


# the file-frame side each display face lies on (only used for the renderer's per-side shading)
FILE_SIDE = {"east": "west", "west": "east", "north": "north", "south": "south", "up": "up", "down": "down"}


def truth_face_corners(o, s, infl, face, uv):
    fr = [-(o[0] + s[0]) - infl, o[1] - infl, o[2] - infl]
    to = [-o[0] + infl, o[1] + s[1] + infl, o[2] + s[2] + infl]
    u1, v1, u2, v2 = uv
    pts = []
    for U, V in ((u1, v1), (u2, v1), (u2, v2), (u1, v2)):
        p = _local(face, fr, to, uv, U, V)
        pts.append([-p[0], p[1], p[2]])              # display -> file frame
    return pts, (u1, v1, u2, v2), FILE_SIDE[face]


def truth_posed_faces(bones, tw, th, aff):
    faces = []
    for b in bones:
        A, t = aff[b["name"]]; bmirror = bool(b.get("mirror", False))
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]; infl = c.get("inflate", 0) or 0
            piv, rot = c.get("pivot", [0, 0, 0]), c.get("rotation", [0, 0, 0]) or [0, 0, 0]
            mirror = bool(c.get("mirror", bmirror))
            for name, uv in face_uvs(c.get("uv", [0, 0]), s, mirror).items():
                if infl == 0:
                    if s[0] == 0 and name not in ("east", "west"): continue
                    if s[1] == 0 and name not in ("up", "down"): continue
                    if s[2] == 0 and name not in ("north", "south"): continue
                pts, (a, bb, cc, e), side = truth_face_corners(o, s, infl, name, uv)
                P = [transform(p, piv, rot) if any(rot) else list(p) for p in pts]
                P = [list(A @ np.array(p, float) + t) for p in P]
                faces.append(Face(P, (a / tw, bb / th, cc / tw, e / th), "*", side, b["name"]))
    return faces


if __name__ == "__main__":
    # self-test against the three places Blockbench defines the convention (bedrock codec round trip + UVToLocal)
    o, s = [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]
    pts, uv, side = truth_face_corners(o, s, 0, "up", face_uvs({"up": {"uv": [10, 20], "uv_size": [4, 6]}}, s, False)["up"])
    # Blockbench import of that up face: internal uv [14, 26, 10, 20]; texel (14, 26) sits at internal (from.x, top, from.z)
    # = display (-5, 7, 3) = file (5, 7, 3)
    assert pts[0] == [5.0, 7.0, 3.0], pts
    pts, uv, side = truth_face_corners(o, s, 0, "east", face_uvs({"east": {"uv": [10, 20], "uv_size": [4, 6]}}, s, False)["east"])
    assert all(p[0] == 1.0 for p in pts) and side == "west", pts          # display east = file min x
    print("bb_truth self-test OK")
