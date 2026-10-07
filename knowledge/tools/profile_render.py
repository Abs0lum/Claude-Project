#!/usr/bin/env python3
"""profile_render.py — textured side-view (gable/profile plane) renderer + coplanar-fight detector + crop-cut simulator.

Why: the R-5 census tools (census.py / opacity.py) never reached project knowledge; this rebuilds the part that
matters for the seam work and adds what they lacked — CROSS-BLOCK pairs (a neighbour placed at an offset) and a
what-if CUT (alpha-0 polygons on chosen faces) so a fix can be previewed before any pack is touched.

Model (matches fill_sim / crop_cut2 / seam_figure): cubes rotate about x only (the boards); the east/west faces stay
planar at constant x.  JSON +deg about x lifts the +z end (SIGN -1 calibration, D-C197).  A face samples its texture
through its own uv rect, scaled from the geometry's declared texture size to the atlas (file) size — L-DECL-PER-GEOM.
West face: fu = 0 at -z.  East face: fu = 0 at +z (Bedrock box-uv convention, same as crop_cut.face_world).

Fight rule (phone depth buffer): two opaque samples on the same side whose planes are within PROUD_MAX (0.06 px) and
whose colours differ by > 8/255 -> a fight pixel.  Areas are reported in block px².
"""
import math
import numpy as np
from PIL import Image

SIGN = -1
PROUD_MAX = 0.06
DIFF = 8

def rot_yz(y, z, piv_y, piv_z, deg):
    a = math.radians(SIGN * deg)
    y, z = y - piv_y, z - piv_z
    return (y * math.cos(a) - z * math.sin(a) + piv_y, y * math.sin(a) + z * math.cos(a) + piv_z)

def unrot_yz(y, z, piv_y, piv_z, deg):
    return rot_yz(y, z, piv_y, piv_z, -deg)

class Face:
    """One east/west face of one cube, in the profile plane."""
    def __init__(self, cube, side, tex, decl, off=(0.0, 0.0), tag=""):
        o, s = cube["origin"], cube["size"]
        self.side, self.tag = side, tag
        self.x = (o[0] + s[0]) if side == "east" else o[0]
        self.rot = (cube.get("rotation") or [0, 0, 0])[0]
        piv = cube.get("pivot") or [0, 0, 0]
        self.piv = (piv[1] + off[0], piv[2] + off[1])
        self.o = (o[1] + off[0], o[2] + off[1]); self.s = (s[1], s[2])
        spec = cube["uv"][side]
        self.uv = spec["uv"]; self.uvs = spec["uv_size"]
        self.inst = spec.get("material_instance", "*")
        self.tex = tex          # np RGBA array
        self.decl = decl        # (w, h) declared units
        self.cuts = []          # polygons in world (z, y) -> alpha 0
        c = [(self.o[0] + dy * self.s[0], self.o[1] + dz * self.s[1]) for dy, dz in ((0, 0), (0, 1), (1, 1), (1, 0))]
        self.poly = [rot_yz(y, z, *self.piv, self.rot) for y, z in c]           # (y, z)
        ys = [p[0] for p in self.poly]; zs = [p[1] for p in self.poly]
        self.bbox = (min(zs), min(ys), max(zs), max(ys))

    def sample(self, z, y):
        """RGBA at world (z, y) or None when outside / transparent / cut."""
        yl, zl = unrot_yz(y, z, *self.piv, self.rot)
        fz = (zl - self.o[1]) / self.s[1]; fy = (self.o[0] + self.s[0] - yl) / self.s[0]
        if not (0.0 <= fz <= 1.0 and 0.0 <= fy <= 1.0):
            return None
        for poly in self.cuts:
            if point_in(poly, z, y):
                return None
        fu = fz if self.side == "west" else 1.0 - fz
        u = self.uv[0] + fu * self.uvs[0]; v = self.uv[1] + fy * self.uvs[1]
        h, w = self.tex.shape[:2]
        tx = min(w - 1, max(0, int(u * w / self.decl[0]))); ty = min(h - 1, max(0, int(v * h / self.decl[1])))
        px = self.tex[ty, tx]
        return None if px[3] == 0 else px

def point_in(poly, z, y):
    sign = 0
    for i in range(len(poly)):
        z0, y0 = poly[i]; z1, y1 = poly[(i + 1) % len(poly)]
        cr = (z1 - z0) * (y - y0) - (y1 - y0) * (z - z0)
        if abs(cr) < 1e-12:
            continue
        s = 1 if cr > 0 else -1
        if sign == 0:
            sign = s
        elif s != sign:
            return False
    return True

def faces_of(geo, side, texmap, off=(0.0, 0.0), tag="", only=None):
    decl = (geo["description"].get("texture_width", 16), geo["description"].get("texture_height", 16))
    out = []
    for b in geo["bones"]:
        for ci, c in enumerate(b.get("cubes", [])):
            if only is not None and (b["name"], ci) not in only:
                continue
            uv = c.get("uv")
            if not isinstance(uv, dict) or side not in uv:
                continue
            inst = uv[side].get("material_instance", "*")
            if inst not in texmap:
                raise KeyError(f"no texture for instance {inst} ({tag} {b['name']}#{ci})")
            f = Face(c, side, texmap[inst], decl, off, tag=f"{tag}{b['name']}#{ci}")
            out.append(f)
    return out

def render(faces, side, z0, z1, y0, y1, scale, bg=(24, 24, 28), mark_fights=True, sub=1):
    """Paint nearest-opaque per pixel; return (RGB image, fight mask, fight area px², per-pair areas)."""
    W, H = int((z1 - z0) * scale), int((y1 - y0) * scale)
    img = np.zeros((H, W, 3), np.uint8); img[:] = bg
    fight = np.zeros((H, W), bool)
    pairs = {}
    order = sorted(faces, key=lambda f: -f.x if side == "east" else f.x)   # nearest first
    for r in range(H):
        y = y1 - (r + 0.5) / scale
        for cidx in range(W):
            z = z0 + (cidx + 0.5) / scale
            hits = []
            for f in order:
                bz0, by0, bz1, by1 = f.bbox
                if not (bz0 - 1e-6 <= z <= bz1 + 1e-6 and by0 - 1e-6 <= y <= by1 + 1e-6):
                    continue
                px = f.sample(z, y)
                if px is not None:
                    hits.append((f, px))
                    if len(hits) == 2:
                        break
            if not hits:
                continue
            f0, p0 = hits[0]
            img[r, cidx] = p0[:3]
            if mark_fights and len(hits) == 2:
                f1, p1 = hits[1]
                if abs(f0.x - f1.x) <= PROUD_MAX and np.abs(p0[:3].astype(int) - p1[:3].astype(int)).max() > DIFF:
                    fight[r, cidx] = True
                    key = (f0.tag, f1.tag); pairs[key] = pairs.get(key, 0) + 1
    area = fight.sum() / (scale * scale)
    pairs = {k: v / (scale * scale) for k, v in pairs.items()}
    return Image.fromarray(img), fight, area, pairs

def overlay_fights(img, fight, color=(255, 0, 255)):
    a = np.array(img.convert("RGB")); a[fight] = color
    return Image.fromarray(a)

def load_tex(path):
    return np.array(Image.open(path).convert("RGBA"))

def face_cut_halfplane(face, axis, op, value):
    """Add a cut = the half-plane {axis op value} in world coords (axis 'z' or 'y'), as a big polygon."""
    big = 1e3
    if axis == "z":
        poly = [(value, -big), (big if op == ">" else -big, -big), (big if op == ">" else -big, big), (value, big)]
    else:
        poly = [(-big, value), (-big, big if op == ">" else -big), (big, big if op == ">" else -big), (big, value)]
    face.cuts.append(poly)
