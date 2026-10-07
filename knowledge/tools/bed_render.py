#!/usr/bin/env python3
"""bed_render.py — software render of Bedrock's built-in bed (geometry.bed, models/mobs.json) wearing a bed texture.

Purpose: reproduce Abs0lum's 2026-09-22 13:50 witness frames (Patrix Java-layout bed texture on the Bedrock model)
and preview the fix candidates, from a player-like camera.  Painter's algorithm, perspective-correct per face,
double-sided (the engine shows the bed's interior through transparent texels — witnessed in B1/B2/B3).

World units = texture px (16 per block).  The bed lies flat: L (0 = head end, 32 = foot end) along +x, width z 0..16,
mattress y 3..9, legs y 0..3.  Texture regions are given on the 64-texel grid and scaled to the texture's own size.

Face records: (corners3d[4], texcorners64[4]) with the SAME winding, so the perspective map is exact.
"""
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

# ------------------------------------------------------------------ geometry.bed (mobs.json) as it lies in the world
# The standing box (16 x 32 x 6, uv 0,0) is laid flat by the engine: standing y = 32 - L, standing z = 9 - y.
# Bedrock unwrap of the standing box: up [6,22]x[0,6] · down [22,38]x[0,6] · east [0,6]x[6,38] · north [6,22]x[6,38]
#   · west [22,28]x[6,38] · south [28,44]x[6,38].  Orientation checks (both vanilla and Patrix agree):
#   side strips: u 0..3 wood / 3..6 blanket (left strip: u grows upward); right strip mirrored (22..25 blanket, 25..28 wood)
#   head end [6,22]x[0,6]: rows 0..3 wood, 3..6 pillow -> v grows upward
#   top strip [6,22]x[6,38]: pillow at rows 6..12 -> v grows head -> foot

def quad(p0, p1, p2, p3, t0, t1, t2, t3, tag=""):
    return {"p": [p0, p1, p2, p3], "t": [t0, t1, t2, t3], "tag": tag}

def mattress_faces_single_box(vmap):
    """Faces of the one-box mattress.  vmap(L) -> texture row for a bed-length position L (0..32) on the 32-row strip."""
    F = []
    y0, y1 = 3, 9
    # top: u = 6 + z (z 0..16), v = vmap(L)
    F.append(quad((0, y1, 0), (32, y1, 0), (32, y1, 16), (0, y1, 16),
                  (6, vmap(0)), (6, vmap(32)), (22, vmap(32)), (22, vmap(0)), "top"))
    # underside (south strip [28,44]): u = 28 + (16 - z)
    F.append(quad((0, y0, 0), (32, y0, 0), (32, y0, 16), (0, y0, 16),
                  (44, vmap(0)), (44, vmap(32)), (28, vmap(32)), (28, vmap(0)), "underside"))
    # left side z = 0 (east strip [0,6]): u = 0 + (y - 3)
    F.append(quad((0, y0, 0), (32, y0, 0), (32, y1, 0), (0, y1, 0),
                  (0, vmap(0)), (0, vmap(32)), (6, vmap(32)), (6, vmap(0)), "side_z0"))
    # right side z = 16 (west strip [22,28]): u = 22 + (9 - y)
    F.append(quad((0, y0, 16), (32, y0, 16), (32, y1, 16), (0, y1, 16),
                  (28, vmap(0)), (28, vmap(32)), (22, vmap(32)), (22, vmap(0)), "side_z16"))
    return F

def end_face(x, y0, y1, region, tag):
    """End face at bed position x; region = (u0, u1, v0, v1) with v0 = bottom row, v1 = top row (v grows upward)."""
    u0, u1, vb, vt = region
    return quad((x, y0, 0), (x, y0, 16), (x, y1, 16), (x, y1, 0), (u0, vb), (u1, vb), (u1, vt), (u0, vt), tag)

def box_faces(o, s, uv, tag):
    """A Bedrock-unwrapped box lying in bed space (o = origin (x, y, z), s = size).  Returns 6 faces with the
    standard unwrap (up/down top row, east north west south side row); orientation good enough for legs/rails."""
    x0, y0, z0 = o; w, h, d = s; u, v = uv
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    F = []
    F.append(quad((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1), (u + d, v), (u + d + w, v), (u + d + w, v + d), (u + d, v + d), tag + ".up"))
    F.append(quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), (u + d + w, v), (u + d + 2 * w, v), (u + d + 2 * w, v + d), (u + d + w, v + d), tag + ".down"))
    F.append(quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (u, v + d + h), (u + d, v + d + h), (u + d, v + d), (u, v + d), tag + ".x0"))
    F.append(quad((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (u + d, v + d + h), (u + d + w, v + d + h), (u + d + w, v + d), (u + d, v + d), tag + ".z0"))
    F.append(quad((x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0), (u + d + w, v + d + h), (u + 2 * d + w, v + d + h), (u + 2 * d + w, v + d), (u + d + w, v + d), tag + ".x1"))
    F.append(quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), (u + 2 * d + w, v + d + h), (u + 2 * d + 2 * w, v + d + h), (u + 2 * d + 2 * w, v + d), (u + 2 * d + w, v + d), tag + ".z1"))
    return F

def bedrock_bed_as_is():
    """geometry.bed with the texture read exactly as the engine reads it (Java-layout Patrix texture as shipped)."""
    F = mattress_faces_single_box(lambda L: 6 + L)                     # one 32-row strip, rows 6..38
    F.append(end_face(0, 3, 9, (6, 22, 0, 6), "head_end"))             # up face of the standing box
    F.append(end_face(32, 3, 9, (38, 22, 0, 6), "foot_end"))           # down face -> Patrix leaves it EMPTY
    # legs (3x3x3) at the corners: standing (13,29,6)->head right, (0,29,6)->head left, (13,0,6)->foot, (0,0,6)->foot
    F += box_faces((0, 0, 13), (3, 3, 3), (12, 38), "leg1")
    F += box_faces((0, 0, 0), (3, 3, 3), (0, 38), "leg0")
    F += box_faces((29, 0, 13), (3, 3, 3), (12, 44), "leg3")
    F += box_faces((29, 0, 0), (3, 3, 3), (0, 44), "leg2")
    # rails under the mattress (invisible in vanilla: their uv regions are empty)
    F += box_faces((0, 0, 3), (1, 3, 10), (38, 2), "rail_head")        # standing (3,31,6) size (10,1,3)
    F += box_faces((31, 0, 3), (1, 3, 10), (38, 38), "rail_foot")      # standing (3,0,6)
    F += box_faces((3, 0, 15), (26, 3, 1), (52, 6), "rail_z16")        # standing (15,3,6) size (1,26,3)
    F += box_faces((3, 0, 0), (26, 3, 1), (44, 6), "rail_z0")          # standing (0,3,6)
    return F

def java_layout_bed():
    """What the same texture shows on a two-piece Java-layout model (= Patrix's intent) — also what option A
    (re-laid-out texture on the engine box) and option B (two-box geometry override) both produce."""
    F = []
    # head piece rows 6..22, foot piece rows 28..44 — two 16-row strips
    for (L0, v0) in ((0, 6), (16, 28)):
        vm = lambda L, v0=v0, L0=L0: v0 + (L - L0)
        y0, y1 = 3, 9
        F.append(quad((L0, y1, 0), (L0 + 16, y1, 0), (L0 + 16, y1, 16), (L0, y1, 16), (6, vm(L0)), (6, vm(L0 + 16)), (22, vm(L0 + 16)), (22, vm(L0)), "top"))
        F.append(quad((L0, y0, 0), (L0 + 16, y0, 0), (L0 + 16, y0, 16), (L0, y0, 16), (44, vm(L0)), (44, vm(L0 + 16)), (28, vm(L0 + 16)), (28, vm(L0)), "underside"))
        F.append(quad((L0, y0, 0), (L0 + 16, y0, 0), (L0 + 16, y1, 0), (L0, y1, 0), (0, vm(L0)), (0, vm(L0 + 16)), (6, vm(L0 + 16)), (6, vm(L0)), "side_z0"))
        F.append(quad((L0, y0, 16), (L0 + 16, y0, 16), (L0 + 16, y1, 16), (L0, y1, 16), (28, vm(L0)), (28, vm(L0 + 16)), (22, vm(L0 + 16)), (22, vm(L0)), "side_z16"))
    F.append(end_face(0, 3, 9, (6, 22, 0, 6), "head_end"))
    F.append(end_face(32, 3, 9, (38, 22, 22, 28), "foot_end"))         # Patrix footboard [22,38]x[22,28]
    # legs: Java leg unwraps at (50,0) (50,6) (50,12) (50,18)
    # corner -> Patrix leg, the same assignment bed_relayout.MOVES uses for the engine's leg slots
    F += box_faces((0, 0, 0), (3, 3, 3), (50, 0), "leg")
    F += box_faces((0, 0, 13), (3, 3, 3), (50, 6), "leg")
    F += box_faces((29, 0, 0), (3, 3, 3), (50, 12), "leg")
    F += box_faces((29, 0, 13), (3, 3, 3), (50, 18), "leg")
    return F

# ------------------------------------------------------------------ camera + painter's renderer
class Camera:
    def __init__(self, eye, target, W, H, fov_deg=70):
        self.eye = np.array(eye, float); t = np.array(target, float)
        f = t - self.eye; f /= np.linalg.norm(f)
        r = np.cross(f, np.array([0, 1, 0.0])); r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u
        self.W, self.H = W, H
        self.focal = (W / 2) / math.tan(math.radians(fov_deg) / 2)
    def project(self, p):
        d = np.array(p, float) - self.eye
        z = d @ self.f
        if z <= 0.05: return None
        return (self.W / 2 + self.focal * (d @ self.r) / z, self.H / 2 - self.focal * (d @ self.u) / z, z)

def find_coeffs(dst, src):
    """PIL perspective coefficients mapping output points dst -> input points src (4 pairs)."""
    A = []
    for (x, y), (X, Y) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -X * x, -X * y]); A.append([0, 0, 0, x, y, 1, -Y * x, -Y * y])
    A = np.array(A, float); b = np.array([c for pt in src for c in pt], float)
    return np.linalg.solve(A, b)

def render(faces, tex, cam, bg=(52, 44, 36, 255), floor=None):
    """faces: list of quads; tex: PIL RGBA (any multiple of 64); returns RGBA canvas."""
    s = tex.width / 64
    canvas = Image.new("RGBA", (cam.W, cam.H), bg)
    if floor is not None: canvas.alpha_composite(floor)
    order = []
    for f in faces:
        c = np.mean(np.array(f["p"], float), axis=0)
        order.append((np.linalg.norm(c - cam.eye), f))
    order.sort(key=lambda t: -t[0])
    for _, f in order:
        pts = [cam.project(p) for p in f["p"]]
        if any(p is None for p in pts): continue
        dst = [(p[0], p[1]) for p in pts]
        src = [(u * s, v * s) for (u, v) in f["t"]]
        try: coeffs = find_coeffs(dst, src)
        except np.linalg.LinAlgError: continue
        layer = tex.transform((cam.W, cam.H), Image.PERSPECTIVE, tuple(coeffs), Image.NEAREST)
        # clip to the quad (the perspective map is only valid inside it)
        mask = Image.new("L", (cam.W, cam.H), 0); ImageDraw.Draw(mask).polygon(dst, fill=255)
        a = np.array(layer)[..., 3] * (np.array(mask) > 0)
        a = np.where(a > 0, 255, 0).astype(np.uint8)                       # alpha test, as the engine does
        layer.putalpha(Image.fromarray(a))
        canvas.alpha_composite(layer)
    return canvas

def floor_layer(cam, planks, y=0, extent=((-40, 72), (-40, 56))):
    """A plank floor at height y so see-through texels read like the witness frames."""
    (x0, x1), (z0, z1) = extent
    faces = []
    for x in range(x0, x1, 16):
        for z in range(z0, z1, 16):
            faces.append(quad((x, y, z), (x + 16, y, z), (x + 16, y, z + 16), (x, y, z + 16), (0, 0), (64, 0), (64, 64), (0, 64), "floor"))
    return render(faces, planks, cam, bg=(0, 0, 0, 0))

if __name__ == "__main__":
    import sys
    tex = Image.open(sys.argv[1]).convert("RGBA")
    cam = Camera((16, 44, 46), (16, 4, 8), 900, 520)
    render(bedrock_bed_as_is(), tex, cam).save(sys.argv[2])
