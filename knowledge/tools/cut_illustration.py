#!/usr/bin/env python3
"""cut_illustration.py — the three verbs on a 45° board: shift the TEXTURE (pixels) · move the PLANE (cubes) ·
CUT at the block boundary (Abs0lum's skill-saw cut: run the board past the boundary, then forbid it past the
boundary -> the cut lands exactly on the block edge).  Section view, units = cubes (1 cube = 8 px at 128 px/block).
Output: _design/cut-illustration-v1.png
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Arc, FancyArrowPatch

OUT = "/home/claude/_design/cut-illustration-v1.png"
BG = "#f4f0ea"; BOARD = "#a97a48"; BOARD_E = "#5a3a1e"; GRAIN = "#7d5a34"; CUT = "#c0392b"; OK = "#1e8449"; CELL = "#333"
T = 1.5   # board thickness (cubes)

def board_poly(z0, y0, length, t=T, ang=45):
    """Rectangle of a board whose TOP-surface low end starts at (z0, y0) and rises inward (+z) at `ang`."""
    a = math.radians(ang); d = (math.cos(a), math.sin(a)); n = (math.sin(a), -math.cos(a))   # n = downward normal
    p0 = (z0, y0); p1 = (z0 + d[0] * length, y0 + d[1] * length)
    p2 = (p1[0] + n[0] * t, p1[1] + n[1] * t); p3 = (z0 + n[0] * t, y0 + n[1] * t)
    return [p0, p1, p2, p3]

def draw_cell(ax, z=0, y=0, w=16, h=16, label=None):
    ax.add_patch(Rectangle((z, y), w, h, facecolor="none", edgecolor=CELL, lw=1.6, ls=":"))
    if label: ax.text(z + w / 2, y + h + 0.6, label, ha="center", va="bottom", fontsize=10, color=CELL)

def grain(ax, poly, offset_px=0, step=1.0, color=GRAIN):
    """Grain lines along the board, offset by `offset_px` texture pixels (8 px = 1 cube)."""
    (z0, y0), (z1, y1), (z2, y2), (z3, y3) = poly
    L = math.hypot(z1 - z0, y1 - y0); d = ((z1 - z0) / L, (y1 - y0) / L); n = ((z3 - z0) / T, (y3 - y0) / T)
    s = (offset_px / 8.0) % step
    while s < L:
        a = (z0 + d[0] * s, y0 + d[1] * s); b = (a[0] + n[0] * T, a[1] + n[1] * T)
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=0.9, alpha=0.8)
        s += step

def angle_mark(ax, corner, deg_from, deg_to, r, label, color, lofs=(0, 0)):
    ax.add_patch(Arc(corner, 2 * r, 2 * r, theta1=deg_from, theta2=deg_to, color=color, lw=1.6))
    mid = math.radians((deg_from + deg_to) / 2)
    ax.text(corner[0] + (r + 1.2) * math.cos(mid) + lofs[0], corner[1] + (r + 1.2) * math.sin(mid) + lofs[1], label,
            ha="center", va="center", fontsize=11, color=color, weight="bold")

fig, axes2 = plt.subplots(2, 2, figsize=(20, 16), dpi=100, facecolor=BG)
axes = [axes2[0][0], axes2[0][1], axes2[1][0], axes2[1][1]]
fig.suptitle("Three different verbs on the same 45° board — section view, units in CUBES (1 cube = 8 px at 128 px per block)", fontsize=18, y=0.985)

# ---------- panel 1: shift the TEXTURE (pixels) ----------
ax = axes[0]; ax.set_facecolor(BG); ax.set_aspect("equal"); ax.set_axis_off(); ax.set_xlim(-8, 20); ax.set_ylim(-9, 21)
ax.set_title("1 · \"move the TEXTURE one pixel\"\n(UV shift — geometry untouched)", fontsize=13)
draw_cell(ax, 0, 0, 16, 16, "the block")
P = board_poly(-2.5, -2.5, 22)          # board poking past the block's lower-outer corner
ax.add_patch(Polygon(P, closed=True, facecolor=BOARD, edgecolor=BOARD_E, lw=1.4))
grain(ax, P, offset_px=0)
ax.text(6, -6.5, "the board END does not move.\nOnly WHICH texels show on the face changes:\n1 px = 1/8 cube — invisible at arm's length", ha="center", va="top", fontsize=10.5)
ax.annotate("grain slid 1 px\nalong the board", xy=(9, 9.2), xytext=(-6, 15.5), fontsize=10, arrowprops=dict(arrowstyle="-|>", color="#222"))
ax.plot([-2.5, -2.5], [-3.5, -1.5], color=CUT, lw=2); ax.text(-3.2, -0.6, "end still\npokes out", ha="right", va="bottom", fontsize=10, color=CUT)

# ---------- panel 2: move the PLANE (cubes) ----------
ax = axes[1]; ax.set_facecolor(BG); ax.set_aspect("equal"); ax.set_axis_off(); ax.set_xlim(-8, 20); ax.set_ylim(-9, 21)
ax.set_title("2 · \"move the PLANE one cube\"\n(the box end moves — still a square end)", fontsize=13)
draw_cell(ax, 0, 0, 16, 16, "the block")
P0 = board_poly(-2.5, -2.5, 22); ax.add_patch(Polygon(P0, closed=True, facecolor="none", edgecolor=BOARD_E, lw=1.0, ls="--"))
P = board_poly(-2.5 + math.cos(math.radians(45)), -2.5 + math.sin(math.radians(45)), 21)
ax.add_patch(Polygon(P, closed=True, facecolor=BOARD, edgecolor=BOARD_E, lw=1.4)); grain(ax, P)
ax.annotate("whole end face moved\n1 cube (= 8 px) up the slope", xy=(P[0][0], P[0][1]), xytext=(4, -6.5), fontsize=10.5, ha="center", arrowprops=dict(arrowstyle="-|>", color="#222"))
ax.text(6, 18.5, "the end is still 90° to the board —\nnothing is cut, it just sits elsewhere", ha="center", va="bottom", fontsize=10.5)

# ---------- panel 3: THE CUT (your method) ----------
ax = axes[2]; ax.set_facecolor(BG); ax.set_aspect("equal"); ax.set_axis_off(); ax.set_xlim(-7, 15); ax.set_ylim(-8, 13)
T_SAVED = T; T = 2.5   # thickness exaggerated in this zoomed panel so the two corners read
ax.set_title("3 · the CUT — run the board PAST the boundary, then forbid it past the boundary\n(zoomed on the block's lower-outer corner; thickness exaggerated)", fontsize=13)
draw_cell(ax, 0, 0, 16, 16); ax.text(0.4, 12.2, "the block", ha="left", va="bottom", fontsize=10, color=CELL)
draw_cell(ax, 0, -16, 16, 16); ax.text(0.4, -7.6, "the next block (below)", ha="left", va="bottom", fontsize=10, color="#777")
# board whose TOP surface passes exactly through the block's lower-outer corner (0,0) and runs on past it
Pfull = board_poly(-4, -4, 22, t=T)
# split into the kept part (y >= 0, i.e. inside this block) and the forbidden part (below the block's bottom plane)
def clip_below(poly, y0=0.0):
    """Sutherland–Hodgman clip of a convex polygon against y >= y0 (kept) — the level cut."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ina, inb = a[1] >= y0, b[1] >= y0
        if ina: out.append(a)
        if ina != inb:
            t = (y0 - a[1]) / (b[1] - a[1]); out.append((a[0] + t * (b[0] - a[0]), y0))
    return out
def clip_above(poly, y0=0.0):
    return clip_below([(z, -y) for z, y in poly], -y0) and [(z, -y) for z, y in clip_below([(z, -y) for z, y in poly], -y0)]
kept = clip_below(Pfull, 0.0); gone = clip_above(Pfull, 0.0)
ax.add_patch(Polygon(gone, closed=True, facecolor="none", edgecolor=CUT, lw=1.4, ls="--", hatch="///"))
ax.add_patch(Polygon(kept, closed=True, facecolor=BOARD, edgecolor=BOARD_E, lw=1.6))
ax.plot([-7, 15], [0, 0], color=CUT, lw=2.2); ax.text(14.6, 0.35, "block boundary = the saw line", color=CUT, fontsize=10.5, va="bottom", ha="right")
# the corners: top surface hits the corner (0,0)?  top surface passes through (-4,-4)+(t,t) -> at z=0, y=0 ✓
ax.plot([0], [0], marker="o", color=OK, ms=7); ax.text(-0.6, 2.2, "top plane edge FLUSH\nwith the block corner", color=OK, fontsize=10.5, va="bottom", ha="right")
# bottom corner of the kept piece: where the underside meets y=0
under = [p for p in kept if abs(p[1]) < 1e-9 and p[0] > 0.1][0]
# kept material at the block corner: top surface (45°) and the cut segment running right (0°) -> 45°
angle_mark(ax, (0, 0), 0, 45, 1.3, "45°", CUT, lofs=(0.9, -0.2))
# kept material at the underside corner: the cut segment running left (180°) and the underside (45°) -> 135° = HIS bottom cut
angle_mark(ax, under, 45, 180, 1.6, "135°", OK, lofs=(0.2, 0.6))
ax.annotate("the bottom, cut to 135°", xy=(under[0] + 0.2, under[1] + 0.2), xytext=(8.5, 4.2), fontsize=10.5, color=OK, arrowprops=dict(arrowstyle="-|>", color=OK))
ax.text(7.5, -4.5, "what lies past the boundary is FORBIDDEN (alpha 0):\nthe geometry box still reaches down there,\nbut the texture stops ON the line —\na straight saw cut exactly at the block edge", ha="center", va="center", fontsize=10.5, color=CUT, bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
ax.text(-6.8, 10.0, "level cut (bottom plane): 45° at the top-surface corner,\n135° at the underside — your words exactly.\nplumb cut (side plane): the same two angles swap ends.", ha="left", va="bottom", fontsize=10)
T = T_SAVED

# ---------- panel 4: the texture, in pixels ----------
ax = axes[3]; ax.set_facecolor(BG); ax.set_aspect("equal"); ax.set_axis_off(); ax.set_xlim(-45, 200); ax.set_ylim(-90, 80)
ax.set_title("4 · the same cut on the board's SIDE-FACE texture — in PIXELS\n(the carpenter's trapezoid; rectangle 181 × 12 px = 22.6 × 1.5 cubes)", fontsize=13)
W, H = 181, 12   # board side face at 8 px per cube
ax.add_patch(Rectangle((0, 0), W, H, facecolor="#e6d3b8", edgecolor=BOARD_E, lw=1.2))
ax.text(-2, 0, "top-surface edge", ha="right", va="center", fontsize=9.5, color="#555"); ax.text(-2, H, "underside edge", ha="right", va="center", fontsize=9.5, color="#555")
for x in range(0, W, 8): ax.plot([x, x], [0, H], color="#bbb", lw=0.5)
ax.text(W - 2, H + 4, "one cube = 8 px ticks", ha="right", va="bottom", fontsize=10, color="#666")
# cut line: 45° in world space becomes a line with slope H/H... the boundary plane crosses the face along a line
# running one board-thickness (12 px) of height over 12 px of length: a 45° line in texture space too
x0 = 32
tri = [(0, 0), (x0, 0), (x0 + H, H), (0, H)]
ax.add_patch(Polygon(tri, closed=True, facecolor=CUT, alpha=0.25, edgecolor=CUT, lw=1.4, hatch="///"))
ax.plot([x0, x0 + H], [0, H], color=CUT, lw=2.4)
ax.text(x0 + 6, -6, "alpha = 0 left of this line\n(the forbidden part)", ha="center", va="top", fontsize=10.5, color=CUT)
ax.text(x0 + 30, H + 22, "the cut line climbs 8 px per 8 px (45°):\none board thickness (12 px) of run", ha="left", va="bottom", fontsize=10)
ax.annotate("", xy=(x0 + H + 2, H + 2), xytext=(x0 + 30, H + 21), arrowprops=dict(arrowstyle="-|>", color="#222"))
ax.annotate("", xy=(x0 + H, H), xytext=(x0, 0), arrowprops=dict(arrowstyle="-|>", color=CUT, lw=1.5))
ax.text(W / 2, -34, "Shifting this whole rectangle 1 px = verb 1.\nMoving the box 1 cube = verb 2 (8 px of rectangle).\nCutting the corner off along the boundary line = verb 3 — your skill-saw cut.", ha="center", va="top", fontsize=11)
ax.text(W / 2, -70, "(this is exactly the crop-cut shipped in RP-04 .126/.127:\nboxes byte-identical, only alpha and UVs change)", ha="center", va="top", fontsize=9.5, color="#555")

fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(OUT, facecolor=BG); print("wrote", OUT)
