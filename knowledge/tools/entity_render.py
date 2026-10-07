#!/usr/bin/env python3
"""entity_render.py — perspective render of a Bedrock ENTITY geometry (bones + hierarchy + rotations) with PIL.

Why: to compare what a geometry file MUST look like in-game against Abs0lum's screenshots (witness rule: his
screen is truth; this shows what the file predicts so the two can be laid side by side).

Bedrock rotation convention (D-C197 for X; D-C255 for the full triple, verified against vanilla wolf_armor.geo.json,
the Java->Bedrock cow conversion, the vanilla llama chests / horse bags and Blockbench's codec algebra): in file
coordinates a bone rotation [rx, ry, rz] about its pivot acts as Rz(-rz) . Ry(+ry) . Rx(-rx) (right-handed matrices,
X first), i.e. for +90 about X:  y' = py + (z - pz);  z' = pz - (y - py);  for +90 about Y:  x' = px + (z - pz);
z' = pz - (x - px).  Children inherit the parent's rotation.

Usage (module):  from entity_render import load_geo, render
  cubes = load_geo(path, identifier)           -> list of (bone, corners[8] in world cubes)
  img   = render(cubes, eye, target, fov=70, size=(W, H), colours={bone: (r,g,b)})
"""
import json, math, re
from pathlib import Path
from PIL import Image, ImageDraw


def _load(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


def rot_x(p, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x, y, z = p; return [x, y * c - z * s, y * s + z * c]


def rot_y(p, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x, y, z = p; return [x * c + z * s, y, -x * s + z * c]


def rot_z(p, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x, y, z = p; return [x * c - y * s, x * s + y * c, z]


def transform(p, pivot, rot):
    """Bedrock bone/cube rotation [rx, ry, rz] about a pivot, evaluated in FILE coordinates (D-C255, verified):
    v' = Rz(-rz) . Ry(+ry) . Rx(-rx) . (v - pivot) + pivot  with standard right-handed matrices, X applied first
    (Blockbench Euler order 'ZYX'; the file frame is the world frame with x mirrored, which flips the sense of the
    X and Z rotations but not Y — vanilla llama chests / horse bags [0,90,0] land on the flank only this way)."""
    q = [p[i] - pivot[i] for i in range(3)]
    q = rot_x(q, -rot[0]); q = rot_y(q, rot[1]); q = rot_z(q, -rot[2])
    return [q[i] + pivot[i] for i in range(3)]


def load_geo(path, identifier, extra_rot=None):
    """Return [(bone_name, [8 corners]), ...] in world cubes (1 block = 16). extra_rot = {bone: [rx,ry,rz]} adds
    an animation-style rotation on a bone (applied after its geometry rotation)."""
    doc = _load(path)
    geo = next(g for g in doc["minecraft:geometry"] if g["description"]["identifier"] == identifier)
    bones = {b["name"]: b for b in geo["bones"]}
    extra_rot = extra_rot or {}

    def chain(name):
        out = []
        while name:
            b = bones[name]
            r = list(b.get("rotation", [0, 0, 0]))
            if name in extra_rot: r = [r[i] + extra_rot[name][i] for i in range(3)]
            out.append((b.get("pivot", [0, 0, 0]), r))
            name = b.get("parent")
        return out  # innermost first

    cubes = []
    for b in geo["bones"]:
        ch = chain(b["name"])
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]; infl = c.get("inflate", 0)
            x0, y0, z0 = o[0] - infl, o[1] - infl, o[2] - infl
            x1, y1, z1 = o[0] + s[0] + infl, o[1] + s[1] + infl, o[2] + s[2] + infl
            P = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]]
            if "rotation" in c:
                piv = c.get("pivot", [0, 0, 0]); P = [transform(p, piv, c["rotation"]) for p in P]
            for piv, r in ch:
                if any(r): P = [transform(p, piv, r) for p in P]
            cubes.append((b["name"], P))
    return cubes


def cubes_from_bones(bones, extra_rot=None):
    """Same as load_geo but from an in-memory Bedrock bone list [{name,parent,pivot,rotation,cubes:[{origin,size,inflate?}]}]."""
    by = {b["name"]: b for b in bones}
    extra_rot = extra_rot or {}

    def chain(name):
        out = []; seen = set()
        while name and name in by and name not in seen:
            seen.add(name); b = by[name]
            r = list(b.get("rotation", [0, 0, 0]))
            if name in extra_rot: r = [r[i] + extra_rot[name][i] for i in range(3)]
            out.append((b.get("pivot", [0, 0, 0]), r)); name = b.get("parent")
        return out

    cubes = []
    for b in bones:
        ch = chain(b["name"])
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]; infl = c.get("inflate", 0) or 0
            x0, y0, z0 = o[0] - infl, o[1] - infl, o[2] - infl
            x1, y1, z1 = o[0] + s[0] + infl, o[1] + s[1] + infl, o[2] + s[2] + infl
            P = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]]
            for piv, r in ch:
                if any(r): P = [transform(p, piv, r) for p in P]
            cubes.append((b["name"], P))
    return cubes


FACES = [([0, 1, 2, 3], "north"), ([4, 5, 6, 7], "south"), ([0, 3, 7, 4], "west"), ([1, 2, 6, 5], "east"), ([3, 2, 6, 7], "up"), ([0, 1, 5, 4], "down")]


def _sub(a, b): return [a[i] - b[i] for i in range(3)]
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def _dot(a, b): return sum(a[i] * b[i] for i in range(3))
def _norm(a):
    l = math.sqrt(_dot(a, a)) or 1.0; return [a[i] / l for i in range(3)]


def render(cubes, eye, target, fov=70.0, size=(800, 800), colours=None, bg=(214, 224, 236), ground=None, light=(-0.4, 0.8, -0.45), outline=True):
    """Pinhole perspective; painter's algorithm on face centroid depth; flat shading by normal. eye/target in cubes."""
    W, H = size
    colours = colours or {}
    f = _sub(target, eye); f = _norm(f)
    up = [0, 1, 0]
    r = _norm(_cross(f, up)); u = _cross(r, f)
    focal = (H / 2) / math.tan(math.radians(fov) / 2)

    def project(p):
        d = _sub(p, eye)
        x, y, z = _dot(d, r), _dot(d, u), _dot(d, f)
        if z < 0.05: return None
        return (W / 2 + focal * x / z, H / 2 - focal * y / z, z)

    L = _norm(light)
    polys = []
    if ground is not None:  # a flat ground plane at y = ground, drawn first
        gy = ground
        for gx in range(-64, 64, 16):
            for gz in range(-64, 64, 16):
                pts = [[gx, gy, gz], [gx + 16, gy, gz], [gx + 16, gy, gz + 16], [gx, gy, gz + 16]]
                pr = [project(p) for p in pts]
                if any(q is None for q in pr): continue
                shade = 236 if ((gx // 16 + gz // 16) % 2 == 0) else 226
                polys.append((1e9 - 0, [(q[0], q[1]) for q in pr], (shade, shade, shade + 6), False))
    for bone, P in cubes:
        base = colours.get(bone, (200, 190, 170))
        for idx, name in FACES:
            pts = [P[i] for i in idx]
            n = _norm(_cross(_sub(pts[1], pts[0]), _sub(pts[3], pts[0])))
            c = [sum(p[i] for p in pts) / 4 for i in range(3)]
            # outward normal: for an axis-aligned box the face winding above gives outward normals except we
            # check against the box centre to be safe
            ctr = [sum(q[i] for q in P) / 8 for i in range(3)]
            if _dot(n, _sub(c, ctr)) < 0: n = [-v for v in n]
            view = _sub(eye, c)
            if _dot(n, view) <= 0: continue  # back face
            pr = [project(p) for p in pts]
            if any(q is None for q in pr): continue
            depth = _dot(_sub(c, eye), f)
            lam = 0.55 + 0.45 * max(0.0, _dot(n, L))
            col = tuple(int(min(255, v * lam)) for v in base)
            polys.append((depth, [(q[0], q[1]) for q in pr], col, outline))
    polys.sort(key=lambda t: -t[0])
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    for depth, pts, col, ol in polys:
        d.polygon(pts, fill=col, outline=(60, 50, 40) if ol else None)
    return im


def extents(cubes, bone=None):
    P = [p for b, corners in cubes if bone is None or b == bone for p in corners]
    return [(min(p[i] for p in P), max(p[i] for p in P)) for i in range(3)]


if __name__ == "__main__":
    import sys
    cubes = load_geo(sys.argv[1], sys.argv[2])
    for b in sorted({b for b, _ in cubes}):
        e = extents(cubes, b); print(f"{b:12s} x {e[0][0]:6.1f}..{e[0][1]:6.1f}  y {e[1][0]:6.1f}..{e[1][1]:6.1f}  z {e[2][0]:6.1f}..{e[2][1]:6.1f}")
