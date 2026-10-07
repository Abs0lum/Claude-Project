#!/usr/bin/env python3
"""ridge_trapezoid.py — the cut applied to the ridge cap: two 45° boards become two TRAPEZOIDAL PRISMS meeting at the
centre with the long side up (Abs0lum 2026-09-20 09:39), by a PLUMB cut on the centre plane (z = 0) and a LEVEL cut on
the block's bottom plane (y = 0).  Geometry stays the rectangles (ghost); only the texture is forbidden past the planes.
Units: cubes.  Board = 15.96 wide x 1.2 thick (RP-04 roof45_ridge numbers).  Output: _design/ridge-trapezoid-v1.png
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT = "/home/claude/_design/ridge-trapezoid-v1.png"
BG = "#f4f0ea"; BOARD = "#a97a48"; BOARD_E = "#5a3a1e"; GHOST = "#c0392b"; OK = "#1e8449"
W, T = 15.96, 1.2          # board width (x) and thickness

def profile(side):
    """Side profile (z, y) of one ridge board rectangle BEFORE any cut: top surface through the apex (0, 8)
    and through the block's lower corner (side*8, 0) — rising at 45° — extended past both saw planes.
    (The shipped ridge has its apex at 9.65 with corner teeth; same cut, 1.65 higher.)"""
    s = side
    d = np.array([-s, 1.0]) / math.sqrt(2)          # direction up the slope toward the apex
    n = np.array([-1.0, -s]) / math.sqrt(2)         # downward normal (into the board)
    n = n if n[1] < 0 else -n
    apex = np.array([0.0, 8.0])                    # top surface through BOTH lower block corners (±8, 0) — his "flush" case
    top0 = apex + d * (-(8 + 2.5) * math.sqrt(2))   # top surface, 2.5 cubes past the corner (overshoot)
    top1 = apex + d * (1.6 * math.sqrt(2))          # 1.6 cubes past the centre plane (the 1.13 mitre extension + a bit)
    return np.array([top0, top1, top1 + n * T, top0 + n * T])

def clip(poly, keep):
    """Sutherland–Hodgman against a half-plane keep(p) -> bool (linear)."""
    out = []; n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ia, ib = keep(a), keep(b)
        if ia: out.append(a)
        if ia != ib:
            # find the crossing by bisection on the segment (keep is a linear half-plane)
            lo, hi = 0.0, 1.0
            for _ in range(40):
                m = (lo + hi) / 2; pm = a + (b - a) * m
                if keep(pm) == ia: lo = m
                else: hi = m
            out.append(a + (b - a) * ((lo + hi) / 2))
    return np.array(out)

fig = plt.figure(figsize=(20, 9), dpi=100, facecolor=BG)
fig.suptitle("The cut on the ridge cap: rectangle boards → two trapezoidal prisms meeting at the centre, long side up\n"
             "(plumb cut on z = 0, level cut on y = 0). Geometry unchanged — the texture is forbidden past the planes.", fontsize=14, y=0.99)

# ---------------- left: 2-D profile ----------------
ax = fig.add_subplot(1, 2, 1); ax.set_facecolor(BG); ax.set_aspect("equal"); ax.set_axis_off(); ax.set_xlim(-14, 14); ax.set_ylim(-5, 14)
ax.add_patch(Rectangle((-8, 0), 16, 16, facecolor="none", edgecolor="#333", lw=1.4, ls=":"))
ax.text(-7.8, 12.4, "the ridge block", fontsize=10, color="#333")
ax.plot([-14, 14], [0, 0], color=GHOST, lw=1.8); ax.text(13.8, 0.3, "level saw line (block bottom)", color=GHOST, ha="right", fontsize=10)
ax.plot([0, 0], [-4, 13.5], color=GHOST, lw=1.8); ax.text(0.3, 13.0, "plumb saw line (centre plane)", color=GHOST, fontsize=10)
for side in (+1, -1):
    full = profile(side)
    ax.add_patch(Polygon(full, closed=True, facecolor="none", edgecolor=GHOST, lw=1.2, ls="--", hatch="///"))
    kept = clip(full, lambda p: p[1] >= 0)
    kept = clip(kept, (lambda p: p[0] <= 0) if side == -1 else (lambda p: p[0] >= 0))
    # side = +1 is the board on the +z half (its apex end is cut at z = 0 keeping z >= 0)
    ax.add_patch(Polygon(kept, closed=True, facecolor=BOARD, edgecolor=BOARD_E, lw=1.6))
ax.text(0, 11.2, "long side (top surface) meets at the apex; the underside stops short → a TRAPEZOID each side.\nAt the eave: top plane edge flush with the block corner, underside cut to 135°.", ha="center", va="bottom", fontsize=10.5, color=OK)
ax.text(0, -3.2, "hatched = the rectangle the geometry still has;\nsolid = what the texture is allowed to show", ha="center", va="top", fontsize=10.5, color=GHOST)

# ---------------- right: 3-D prisms ----------------
ax3 = fig.add_subplot(1, 2, 2, projection="3d"); ax3.set_facecolor(BG)
def prism(poly2d, x0, x1, color, alpha=1.0, edge=BOARD_E, lw=0.6):
    """Extrude a (z, y) polygon across x0..x1 into a prism; matplotlib axes (X=x, Y=z, Z=y)."""
    pts0 = [(x0, z, y) for z, y in poly2d]; pts1 = [(x1, z, y) for z, y in poly2d]
    faces = [pts0, pts1]
    n = len(poly2d)
    for i in range(n):
        j = (i + 1) % n
        faces.append([pts0[i], pts0[j], pts1[j], pts1[i]])
    pc = Poly3DCollection(faces, facecolors=matplotlib.colors.to_rgba(color, alpha), edgecolors=edge, linewidths=lw)
    ax3.add_collection3d(pc)
for side in (+1, -1):
    full = profile(side)
    kept = clip(full, lambda p: p[1] >= 0)
    kept = clip(kept, (lambda p: p[0] <= 0) if side == -1 else (lambda p: p[0] >= 0))
    prism(kept, -W / 2, W / 2, BOARD)
    # ghost of the forbidden parts (full rectangle minus kept) — draw the full rectangle as a transparent red shell
    prism(full, -W / 2, W / 2, GHOST, alpha=0.08, edge=GHOST, lw=0.8)
# cell wireframe
for (a, b) in [((-8,-8,0),(8,-8,0)),((8,-8,0),(8,8,0)),((8,8,0),(-8,8,0)),((-8,8,0),(-8,-8,0)),
               ((-8,-8,16),(8,-8,16)),((8,-8,16),(8,8,16)),((8,8,16),(-8,8,16)),((-8,8,16),(-8,-8,16)),
               ((-8,-8,0),(-8,-8,16)),((8,-8,0),(8,-8,16)),((8,8,0),(8,8,16)),((-8,8,0),(-8,8,16))]:
    ax3.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color="#444", lw=0.8, ls=":")
ax3.set_xlim(-11, 11); ax3.set_ylim(-13, 13); ax3.set_zlim(-3, 19); ax3.set_box_aspect((22, 26, 22))
ax3.view_init(elev=22, azim=-48)
ax3.set_xlabel("x (along the ridge)"); ax3.set_ylabel("z"); ax3.set_zlabel("y")
ax3.set_title("two trapezoidal prisms (solid) inside the rectangles the geometry keeps (red shell)", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(OUT, facecolor=BG); print("wrote", OUT)
