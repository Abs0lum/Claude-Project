#!/usr/bin/env python3
"""chest_e2.py — Java 1.15+ chest textures -> Bedrock's (classic) chest layout, derived and render-verified.

Facts (2026-09-22, journal D-C216/217):
  * Bedrock's chest is hardcoded; its texture layout = the classic 64x64 unwrap: knob 2x4x1 @ (0,0), lid 14x5x14 @ (0,0),
    base 14x10x14 @ (0,19); Bedrock box-UV orientation (y-up): UP square 1 (top row <-> back z+, left <-> +x),
    DOWN square 2 (top row <-> front z-, left <-> +x), sides east(u..u+d) north west south, top row <-> y max,
    east: left <-> z+ ; north: left <-> +x ; west: left <-> z- ; south: left <-> -x.  Front (knob) = NORTH.
  * Java 1.15+ ChestModel (y-up, NO mirror/flip; front = SOUTH, z max): polygons as in ModelPart.Cube —
    DOWN square 1 (top <-> z2, left <-> x1), UP square 2 (top <-> z2, left <-> x1), WEST u..u+d (top <-> y1,
    left <-> z2), NORTH (top <-> y1, left <-> x1), EAST (top <-> y1, left <-> z1), SOUTH (top <-> y1, left <-> x2).
  * The Java chest therefore sits rotated 180 deg about y relative to Bedrock's; per face the copy is:
      Bedrock NORTH <- Java SOUTH flipV     Bedrock SOUTH <- Java NORTH flipV
      Bedrock EAST  <- Java WEST  rot180    Bedrock WEST  <- Java EAST  rot180
      Bedrock UP    <- Java UP    flipV     Bedrock DOWN  <- Java DOWN  id
    The witnessed-good double (RP-04 v1.3.41, 07-03) used exactly north<-south flipV, south<-north flipV,
    squares swapped; its end faces were copied without the rot180 (small, unnoticed) — the E2 doubles get the rot180.
  * Double chests: Bedrock double = one 30-wide body (128x64); Bedrock's LEFT 15 columns of a 30-wide face come from
    Java's RIGHT half texture and vice versa (the 180 deg turn swaps sides); each Java half is a 15x?x14 body with the
    seam-side face unused.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import bed_render as br

# ---------------------------------------------------------------- unwrap region tables (64-grid units)
def box_regions(u, v, w, h, d):
    """standard box unwrap regions (both conventions share the rectangles)."""
    return {"sq1": (u + d, v, u + d + w, v + d), "sq2": (u + d + w, v, u + d + 2 * w, v + d),
            "s_a": (u, v + d, u + d, v + d + h), "s_b": (u + d, v + d, u + d + w, v + d + h),
            "s_c": (u + d + w, v + d, u + 2 * d + w, v + d + h), "s_d": (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h)}

OPS = {"id": lambda a: a, "flipV": lambda a: a[::-1], "flipH": lambda a: a[:, ::-1], "rot180": lambda a: a[::-1, ::-1]}
# Bedrock face -> (Java face, op)   (faces named by unwrap slot: sq1/sq2 = top-row squares, s_a..s_d = side row)
# Bedrock: sq1=UP sq2=DOWN s_a=EAST s_b=NORTH s_c=WEST s_d=SOUTH ; Java: sq1=DOWN sq2=UP s_a=WEST s_b=NORTH s_c=EAST s_d=SOUTH
FACE_MAP = {"sq1": ("sq2", "flipV"), "sq2": ("sq1", "id"), "s_a": ("s_a", "rot180"), "s_b": ("s_d", "flipV"), "s_c": ("s_c", "rot180"), "s_d": ("s_b", "flipV")}

def convert_single(src: Image.Image) -> Image.Image:
    src = src.convert("RGBA"); s = src.width // 64; a = np.array(src); out = np.zeros_like(a)
    for (u, v, w, h, d) in ((0, 0, 14, 5, 14), (0, 19, 14, 10, 14), (0, 0, 2, 4, 1)):     # lid, base, knob (knob last: overlaps the lid's empty corner)
        B = box_regions(u, v, w, h, d); J = box_regions(u, v, w, h, d)
        for bf, (jf, op) in FACE_MAP.items():
            ju0, jv0, ju1, jv1 = J[jf]; bu0, bv0, bu1, bv1 = B[bf]
            out[bv0 * s:bv1 * s, bu0 * s:bu1 * s] = OPS[op](a[jv0 * s:jv1 * s, ju0 * s:ju1 * s])
    return Image.fromarray(out)

def convert_double(left: Image.Image, right: Image.Image, single: Image.Image) -> Image.Image:
    """Bedrock double_*.png (128x64 grid): one 30-wide body (lid 30x5x14 @ (0,0), base 30x10x14 @ (0,19)) + knob.
    Java 1.15+ doubles are two 15-wide half textures (normal_left = the LEFT half as seen from the FRONT).
    Per Bedrock face, texture-left = the front viewer's left, so:
      north <- [L.south flipV | R.south flipV]   south <- [R.north flipV | L.north flipV]
      up    <- [L.up    flipV | R.up    flipV]   down  <- [L.down  id    | R.down  id   ]
      east (+x end = the front viewer's left end) <- L.west rot180 ; west <- R.east rot180 ; knob <- single (FACE_MAP).
    Versus the 07-03 witnessed-good double: front and back identical to this; up/down/ends differ (that build copied
    them unflipped/unturned — invisible on symmetric art, but wrong by the derivation the trapped-chest marks confirm)."""
    L = np.array(left.convert("RGBA")); R = np.array(right.convert("RGBA")); N = np.array(single.convert("RGBA"))
    s = L.shape[1] // 64; out = np.zeros((64 * s, 128 * s, 4), np.uint8)
    for (v, h) in ((0, 5), (19, 10)):
        B = box_regions(0, v, 30, h, 14); JH = box_regions(0, v, 15, h, 14)
        def half(H, jf, op): ju0, jv0, ju1, jv1 = JH[jf]; return OPS[op](H[jv0 * s:jv1 * s, ju0 * s:ju1 * s])
        plan = {"s_b": ((L, "s_d", "flipV"), (R, "s_d", "flipV")), "s_d": ((R, "s_b", "flipV"), (L, "s_b", "flipV")),
                "sq1": ((L, "sq2", "flipV"), (R, "sq2", "flipV")), "sq2": ((L, "sq1", "id"), (R, "sq1", "id"))}
        for bf, (p0, p1) in plan.items():
            bu0, bv0, bu1, bv1 = B[bf]; hw = 15 * s
            out[bv0 * s:bv1 * s, bu0 * s:bu0 * s + hw] = half(*p0); out[bv0 * s:bv1 * s, bu0 * s + hw:bu0 * s + 2 * hw] = half(*p1)
        bu0, bv0, bu1, bv1 = B["s_a"]; out[bv0 * s:bv1 * s, bu0 * s:bu1 * s] = half(L, "s_a", "rot180")     # east <- L.west rot180
        bu0, bv0, bu1, bv1 = B["s_c"]; out[bv0 * s:bv1 * s, bu0 * s:bu1 * s] = half(R, "s_c", "rot180")     # west <- R.east rot180
    Bk = box_regions(0, 0, 2, 4, 1)
    for bf, (jf, op) in FACE_MAP.items():
        bu0, bv0, bu1, bv1 = Bk[bf]; ju0, jv0, ju1, jv1 = Bk[jf]
        out[bv0 * s:bv1 * s, bu0 * s:bu1 * s] = OPS[op](N[jv0 * s:jv1 * s, ju0 * s:ju1 * s])
    return Image.fromarray(out)

# ---------------------------------------------------------------- renderer faces (quads with explicit corner->texcoord order)
def face_quad(corners, region, orient, tag):
    """corners: dict with keys of the 3D corner labels; region (u0,v0,u1,v1); orient: which corner sits at the
    texture's (u0,v0) top-left, going clockwise in texture space: [TL, TR, BR, BL] corner labels."""
    u0, v0, u1, v1 = region
    tl, tr, brr, bl = orient
    return br.quad(corners[tl], corners[tr], corners[brr], corners[bl], (u0, v0), (u1, v0), (u1, v1), (u0, v1), tag)

def chest_faces(convention, lid_open_deg=0.0):
    """Faces of a chest (lid 14x5x14 at y 9..14 hinged at the back, base 14x10x14, knob) in world space x 0..16,
    z 0..16 with the FRONT at z = 1 (Bedrock: north).  For the Java convention the model is turned 180 deg (its
    front is z max), so its faces are generated in its own frame and rotated into the same world."""
    F = []
    def box(x0, y0, z0, w, h, d, u, v, front_is_zmax):
        # corners in the model's own frame
        X0, X1, Y0, Y1, Z0, Z1 = x0, x0 + w, y0, y0 + h, z0, z0 + d
        def P(x, y, z):
            if front_is_zmax:          # Java frame -> turn 180 deg about y around the block centre (8, *, 8)
                return (16 - x, y, 16 - z)
            return (x, y, z)
        c = {"x0y0z0": P(X0, Y0, Z0), "x1y0z0": P(X1, Y0, Z0), "x0y1z0": P(X0, Y1, Z0), "x1y1z0": P(X1, Y1, Z0),
             "x0y0z1": P(X0, Y0, Z1), "x1y0z1": P(X1, Y0, Z1), "x0y1z1": P(X0, Y1, Z1), "x1y1z1": P(X1, Y1, Z1)}
        R = box_regions(u, v, w, h, d)
        if convention == "bedrock":
            # texture TL,TR,BR,BL -> corners (derived orientation table in the module docstring)
            F.append(face_quad(c, R["sq1"], ("x1y1z1", "x0y1z1", "x0y1z0", "x1y1z0"), "up"))       # top<->z+, left<->+x
            F.append(face_quad(c, R["sq2"], ("x1y0z0", "x0y0z0", "x0y0z1", "x1y0z1"), "down"))     # top<->z-, left<->+x
            F.append(face_quad(c, R["s_a"], ("x1y1z1", "x1y1z0", "x1y0z0", "x1y0z1"), "east"))     # left<->z+
            F.append(face_quad(c, R["s_b"], ("x1y1z0", "x0y1z0", "x0y0z0", "x1y0z0"), "north"))    # left<->+x
            F.append(face_quad(c, R["s_c"], ("x0y1z0", "x0y1z1", "x0y0z1", "x0y0z0"), "west"))     # left<->z-
            F.append(face_quad(c, R["s_d"], ("x0y1z1", "x1y1z1", "x1y0z1", "x0y0z1"), "south"))    # left<->-x
        else:   # java 1.15+ ModelPart.Cube polygons (model frame; y-up, no mirror)
            F.append(face_quad(c, R["sq1"], ("x0y0z1", "x1y0z1", "x1y0z0", "x0y0z0"), "down"))     # top<->z2, left<->x1
            F.append(face_quad(c, R["sq2"], ("x0y1z1", "x1y1z1", "x1y1z0", "x0y1z0"), "up"))       # top<->z2, left<->x1
            F.append(face_quad(c, R["s_a"], ("x0y0z1", "x0y0z0", "x0y1z0", "x0y1z1"), "west"))     # top<->y1, left<->z2
            F.append(face_quad(c, R["s_b"], ("x0y0z0", "x1y0z0", "x1y1z0", "x0y1z0"), "north"))    # top<->y1, left<->x1
            F.append(face_quad(c, R["s_c"], ("x1y0z0", "x1y0z1", "x1y1z1", "x1y1z0"), "east"))     # top<->y1, left<->z1
            F.append(face_quad(c, R["s_d"], ("x1y0z1", "x0y0z1", "x0y1z1", "x1y1z1"), "south"))    # top<->y1, left<->x2
    jf = convention == "java"
    box(1, 0, 1, 14, 10, 14, 0, 19, jf)                     # base
    box(1, 9, 1, 14, 5, 14, 0, 0, jf)                       # lid (closed)
    # knob on the front: Bedrock front = z 1 -> knob at z 0..1 ; Java front = z 15..16 (before the turn)
    if jf: box(7, 7, 15, 2, 4, 1, 0, 0, True)
    else: box(7, 7, 0, 2, 4, 1, 0, 0, False)
    return F

if __name__ == "__main__":
    pass
