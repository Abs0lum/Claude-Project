#!/usr/bin/env python3
"""coplanar_audit.py — L-COPLANAR-1 gate: within one furniture piece, no two boxes may put a face in the same plane,
facing the same way, with overlapping area (> 0.01 cube^2). Such pairs z-fight (flicker) in game — F01 table legs vs
apron, F04 mantel shelf end vs corbel end. Rotations: handles boxes rotated about ONE axis (x or y or z) — the face
normal to that axis stays in its plane and is compared as a polygon; other faces of rotated boxes are compared by full
3D plane test (normal + offset) and polygon overlap in the plane."""
import sys, math, json
sys.path.insert(0, "/home/claude/tools")
import numpy as np
from shapely.geometry import Polygon

def box_faces_world(b):
    (x, y, z), (w, h, d) = b["o"], b["s"]
    X0, X1, Y0, Y1, Z0, Z1 = x, x + w, y, y + h, z, z + d
    faces = {
        "west":  [(X0, Y0, Z0), (X0, Y0, Z1), (X0, Y1, Z1), (X0, Y1, Z0)],
        "east":  [(X1, Y0, Z0), (X1, Y1, Z0), (X1, Y1, Z1), (X1, Y0, Z1)],
        "down":  [(X0, Y0, Z0), (X1, Y0, Z0), (X1, Y0, Z1), (X0, Y0, Z1)],
        "up":    [(X0, Y1, Z0), (X0, Y1, Z1), (X1, Y1, Z1), (X1, Y1, Z0)],
        "north": [(X0, Y0, Z0), (X0, Y1, Z0), (X1, Y1, Z0), (X1, Y0, Z0)],
        "south": [(X0, Y0, Z1), (X1, Y0, Z1), (X1, Y1, Z1), (X0, Y1, Z1)],
    }
    normals = {"west": (-1, 0, 0), "east": (1, 0, 0), "down": (0, -1, 0), "up": (0, 1, 0), "north": (0, 0, -1), "south": (0, 0, 1)}
    R = np.eye(3); piv = np.zeros(3)
    if b.get("rot"):
        rx, ry, rz = [math.radians(a) for a in b["rot"]]
        # Bedrock applies rotation about the pivot; D-C197 sign convention mirrors geo_preview.transform (apply -rot)
        rx, ry, rz = -rx, -ry, -rz
        Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
        Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
        Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
        R = Rz @ Ry @ Rx; piv = np.array(b["piv"], float)
    out = []
    for k, pts in faces.items():
        P = np.array(pts, float)
        P = (P - piv) @ R.T + piv
        n = R @ np.array(normals[k], float)
        out.append((k, P, n))
    return out

def plane_poly(P, n):
    # project onto 2 axes orthogonal to n
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(n, a); u /= np.linalg.norm(u); v = np.cross(n, u)
    return Polygon([(p @ u, p @ v) for p in P])

def audit(boxes, tol=1e-3):
    F = []
    for i, b in enumerate(boxes):
        for k, P, n in box_faces_world(b):
            F.append((i, k, P, n))
    hits = []
    for a in range(len(F)):
        ia, ka, Pa, na = F[a]
        for c in range(a + 1, len(F)):
            ic, kc, Pc, nc = F[c]
            if ia == ic: continue
            if na @ nc < 0.999: continue                      # must face the same way
            if abs(na @ Pa[0] - nc @ Pc[0]) > tol: continue    # same plane
            ov = plane_poly(Pa, na).intersection(plane_poly(Pc, na)).area
            if ov > 0.01:
                hits.append((ia, ka, ic, kc, round(ov, 3)))
    return hits

WALL_PIECES = {"wall_shelf", "coat_pegs", "mantel"}

def allowed(piece, box, face, P, n):
    """planes nobody can see: the floor underside (y = 0, facing down) for every piece, and for wall pieces the back
    plane pressed on the wall (z = 16, facing +z; single-sided rendering culls it from the room side)."""
    if abs(n[1] + 1) < 1e-6 and abs(P[0][1]) < 1e-6: return True
    if piece in WALL_PIECES and abs(n[2] - 1) < 1e-6 and abs(P[0][2] - 16) < 1e-6: return True
    return False

def allowed_join(name, P, n):
    """table#nesw: on a JOINED side the joint plane is covered by the neighbour table's mirrored top + rail."""
    if not name.startswith("table#"): return False
    nb, eb, sb, wb = (c == "1" for c in name.split("#")[1])
    x, z = P[0][0], P[0][2]
    if nb and abs(n[2] + 1) < 1e-6 and abs(z) < 1e-6: return True
    if sb and abs(n[2] - 1) < 1e-6 and abs(z - 16) < 1e-6: return True
    if wb and abs(n[0] + 1) < 1e-6 and abs(x) < 1e-6: return True
    if eb and abs(n[0] - 1) < 1e-6 and abs(x - 16) < 1e-6: return True
    return False

def gate(pieces):
    """pieces: {name: boxes}. Returns {name: [exposed hits]}."""
    out = {}
    for name, boxes in pieces.items():
        base = name.split("#")[0]
        hits = []
        for (ia, ka, ic, kc, ov) in audit(boxes):
            fa = {k: (P, nn) for k, P, nn in box_faces_world(boxes[ia])}[ka]
            if allowed(base, boxes[ia], ka, fa[0], fa[1]) or allowed_join(name, fa[0], fa[1]): continue
            hits.append((ia, ka, ic, kc, ov))
        out[name] = hits
    return out

if __name__ == "__main__":
    import importlib, furniture_geo as G, build_furniture as BF
    pieces = {n: G.PIECES[n]["boxes"] for n in G.ORDER if n != "table"}
    for m in BF.MASKS: pieces["table#" + BF.mask_name(m)] = BF.table_variant(m)
    res = gate(pieces)
    raw = sum(len(audit(b)) for b in pieces.values())
    total = sum(len(v) for v in res.values())
    for name, hits in res.items():
        if hits or "-v" in sys.argv:
            print(f"{name:14s} {len(hits)} exposed", hits[:6])
    print(f"GATE L-COPLANAR-1: {len(pieces)} geometries, raw pairs {raw}, exposed {total} -> {'PASS' if total == 0 else 'FAIL'}")
    sys.exit(0 if total == 0 else 1)
