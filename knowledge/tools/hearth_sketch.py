#!/usr/bin/env python3
"""hearth_sketch.py — discussion sketch for the 2026-09-21 16:21 design thread.

Panels (all in CUBES: 1 block = 16 x 16 x 16 cubes):
  A  pw:hearth plan (from above): 2-cube back wall in the wall line, open front.
  B  section through the wall: flue chute + auto-cap exhaust  vs  no chute -> room smoke.
  C  pw:wall_dual plan: outer / inner materials, one cell.
  D  roof ridge section: current lower-half collision vs proposed upper-half (numbers from
     BP-02 v1.3.177 collision boxes + RP-04 v1.3.127 geometry AABBs).

Output: _design/hearth-flue-dualwall-v2.png  (no engine claims beyond what the caption states).
"""
import textwrap, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

OUT = "/home/claude/_design/hearth-flue-dualwall-v2.png"
random.seed(7)

STONE = "#8d8d8d"; STONE_D = "#6f6f6f"; SOOT = "#2f2a27"; FLOOR = "#ddd3c3"
EMBER = "#b6461a"; LOG = "#5b3b1f"; LOG2 = "#74502c"; FLAME = "#ff9a1f"
TAN = "#c9a063"; SMOKE = "#7a7a7a"; VOID = "#2b2724"; BG = "#f4f0ea"
RED = "#c0392b"; GREEN = "#1e8449"; BOARD = "#7a5230"

fig = plt.figure(figsize=(24, 21), dpi=100, facecolor=BG)
gs = fig.add_gridspec(2, 2, left=0.03, right=0.985, top=0.955, bottom=0.075,
                      wspace=0.10, hspace=0.50, height_ratios=[1.0, 1.2])
fig.suptitle("AbsolutRealism — hearth / flue / dual wall / ridge collision — discussion sketch v2 (units: cubes, 16 per block)",
             fontsize=20, y=0.99)

def rect(ax, x, y, w, h, fc, ec="#333", lw=1.2, **kw):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, **kw))

def caption(ax, text, width=95, y=-0.02):
    ax.text(0.0, y, textwrap.fill(text, width), transform=ax.transAxes, fontsize=12.5,
            va="top", ha="left", family="DejaVu Sans", linespacing=1.35)

def arrow(ax, p, q, text=None, color="#222", lw=1.6, fs=12, tpos=None, ha="center"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, color=color, lw=lw))
    if text:
        tx, ty = tpos if tpos else ((p[0]+q[0])/2, (p[1]+q[1])/2)
        ax.text(tx, ty, text, fontsize=fs, color=color, ha=ha, va="center")

# ───────────────────────────── A · hearth plan ─────────────────────────────
axA = fig.add_subplot(gs[0, 0]); axA.set_aspect("equal"); axA.set_axis_off()
axA.set_xlim(-6, 27); axA.set_ylim(-5.0, 19.5)
axA.set_title("A · pw:hearth — plan from above (one cell, the wall line runs left–right)", fontsize=16, loc="left")
# neighbouring wall cells
rect(axA, -4, 0, 4, 16, STONE); rect(axA, 16, 0, 4, 16, STONE)
axA.text(-2, 8, "wall\nblock", ha="center", va="center", fontsize=11, color="white")
axA.text(18, 8, "wall\nblock", ha="center", va="center", fontsize=11, color="white")
# cell outline
rect(axA, 0, 0, 16, 16, "none", ec="#222", lw=2.2)
# back wall 2 cubes
rect(axA, 0, 14, 16, 2, STONE_D)
axA.text(8, 15, "back wall · 2 cubes · exterior face = wall material", ha="center", va="center", fontsize=10.5, color="white")
# soot liner (fire face of the back wall)
rect(axA, 1, 13.4, 14, 0.6, SOOT, ec=SOOT)
# floor
rect(axA, 0, 0, 16, 14, FLOOR, ec="none")
rect(axA, 0, 0, 16, 14, "none", ec="#222", lw=2.2)
# ember bed
rect(axA, 2, 3, 12, 8, EMBER, ec="#7a2d0e")
for _ in range(60):
    axA.add_patch(Circle((2 + random.random()*12, 3 + random.random()*8), 0.18, color="#ffb347", alpha=0.7, lw=0))
# logs: lower pair along x, upper pair along z
rect(axA, 2, 4, 12, 2.5, LOG); rect(axA, 2, 7.5, 12, 2.5, LOG)
rect(axA, 4, 2.5, 2.5, 9, LOG2); rect(axA, 9.5, 2.5, 2.5, 9, LOG2)
# flames = crossed quads
axA.plot([5, 11], [3.5, 10.5], color=FLAME, lw=9, alpha=0.85, solid_capstyle="round")
axA.plot([5, 11], [10.5, 3.5], color=FLAME, lw=9, alpha=0.85, solid_capstyle="round")
# annotations
axA.annotate("soot liner = the fire face of the back wall (texture only, no extra box)", xy=(8, 13.7), xytext=(8, 18.3),
             fontsize=11, ha="center", arrowprops=dict(arrowstyle="-|>", color="#222"))
axA.annotate("ember bed 12 × 8 (emissive)", xy=(3, 3.5), xytext=(-5.5, -2.2), fontsize=11, arrowprops=dict(arrowstyle="-|>", color="#222"))
axA.annotate("two crossed log pairs (4 boxes)", xy=(13.5, 8), xytext=(20.5, 12.5), fontsize=11, arrowprops=dict(arrowstyle="-|>", color="#222"))
axA.annotate("flames = 2 crossed alpha-test quads\non the vanilla fire_0 flipbook key", xy=(9.5, 8.5), xytext=(20.5, 4.5), fontsize=11,
             arrowprops=dict(arrowstyle="-|>", color="#222"))
arrow(axA, (8, -0.4), (8, -2.6), None)
axA.text(8, -3.1, "FRONT · open · faces the placer (minecraft:cardinal_direction, y_rotation_offset 180 — the roof family's convention)",
         ha="center", va="top", fontsize=11)
axA.text(-2, 17.2, "the neighbours' inner faces are the cheeks — free", fontsize=10.5, ha="left", color="#333")
caption(axA, "Reads: the hearth REPLACES one wall block. Its 2 back cubes carry the exterior skin; the other 14 cubes are the "
             "firebox, open to the room. Side cheeks come from the neighbouring wall blocks (their faces are visible because "
             "the hearth is not a full cube). Collision proposal: the FULL cell — the wall must stay impassable where the hearth "
             "sits, and a full box also keeps players/villagers out of the fire without any damage script.", y=-0.01)

# ───────────────────────────── C · dual wall plan ─────────────────────────────
axC = fig.add_subplot(gs[0, 1]); axC.set_aspect("equal"); axC.set_axis_off()
axC.set_xlim(-2, 44); axC.set_ylim(-4, 19.5)
axC.set_title("C · pw:wall_dual — plan from above (one cell): outer material / inner material", fontsize=16, loc="left")
rect(axC, 0, 8, 16, 8, STONE); rect(axC, 0, 0, 16, 8, TAN)
rect(axC, 0, 0, 16, 16, "none", ec="#222", lw=2.2)
axC.plot([0, 16], [8, 8], ls="--", color="#222", lw=2)
axC.text(8, 12, "OUTER half · pw:outer (≤16 materials)", ha="center", va="center", fontsize=12, color="white")
axC.text(8, 4, "INNER half · pw:inner (≤16 materials)", ha="center", va="center", fontsize=12, color="#222")
axC.text(8, 8.0, "  shared plane: both faces omitted", ha="center", va="bottom", fontsize=10, color="#222",
         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
arrow(axC, (8, 16.3), (8, 18.6)); axC.text(8, 19.0, "away from the placer (exterior)", ha="center", va="bottom", fontsize=11)
arrow(axC, (8, -0.3), (8, -2.6)); axC.text(8, -3.0, "toward the placer (the room)", ha="center", va="top", fontsize=11)
# variant thumbnails
axC.text(21, 17.8, "how to build it — two candidates", fontsize=12, va="bottom")
# v1: one full box, per-face materials
rect(axC, 21, 9, 8, 8, "#e9e4dc"); axC.plot([21, 29], [17, 17], color=STONE, lw=7); axC.plot([21, 29], [9, 9], color=TAN, lw=7)
axC.plot([21, 21], [9, 17], color="#bbb", lw=5); axC.plot([29, 29], [9, 17], color="#bbb", lw=5)
axC.text(30.5, 13, "V1 (recommended): ONE full box,\nmaterial per FACE (north/south/\neast/west/up/down keys).\n6 faces, full-cube culling + light\ndampening for free. Side faces hidden\nby neighbours; top shows outer.", fontsize=10.5, va="center")
# v2: two boxes
rect(axC, 21, 0, 8, 4, STONE); rect(axC, 21, -0, 8, 0, TAN)
rect(axC, 21, 0, 8, 4, STONE); rect(axC, 21, 0, 8, 0.01, TAN)
rect(axC, 21, 0, 8, 4, STONE); rect(axC, 21, -3.2, 8, 3.2, TAN)
axC.text(30.5, 0.5, "V2: TWO 16×8×16 boxes (what the big\nsquare shows). 10 faces after omitting\nthe shared plane; top face is split\nouter/inner. Costs a real geometry;\nwalls are our most numerous block.", fontsize=10.5, va="center")
caption(axC, "Permutations: pw:outer × pw:inner = up to 16 × 16 = 256, each one only a material_instances swap — no new art, every "
             "material is an existing block texture (its MER/normal texture_set rides along). Orientation: cardinal_direction from "
             "the placer, or set by the assembler from the building envelope (it knows outside from inside).", y=-0.01)

# ───────────────────────────── B · section: chute vs no chute ─────────────────────────────
axB = fig.add_subplot(gs[1, 0]); axB.set_aspect("equal"); axB.set_axis_off()
axB.set_xlim(-20, 118); axB.set_ylim(-6, 100)
axB.set_title("B · section through the wall — smoke has a chute (left) / no chute (right)", fontsize=16, loc="left")

def hearth_section(ax, x0):
    # room x0-16..x0+16 ; wall x0+16..x0+32 ; exterior beyond
    rect(ax, x0+16, 0, 14, 16, FLOOR)                     # firebox
    rect(ax, x0+30, 0, 2, 16, STONE_D)                    # back skin
    rect(ax, x0+29.4, 0, 0.6, 16, SOOT, ec=SOOT)          # soot liner
    rect(ax, x0+18, 0, 10, 1.5, EMBER, ec="#7a2d0e")      # ember bed
    rect(ax, x0+18, 1.5, 10, 2.5, LOG)                    # lower log
    rect(ax, x0+19.5, 4, 2.5, 2.5, LOG2); rect(ax, x0+24.5, 4, 2.5, 2.5, LOG2)   # upper logs end-on
    ax.add_patch(Polygon([(x0+19, 4.5), (x0+27, 4.5), (x0+25.5, 9), (x0+23, 14), (x0+20.5, 9)], closed=True,
                         facecolor=FLAME, edgecolor="none", alpha=0.75))
    rect(ax, x0+20, 14, 8, 2, VOID, ec=VOID)              # throat
    rect(ax, x0+16, 0, 16, 16, "none", ec="#222", lw=2.2)

def smoke_puffs(ax, pts, r0=1.4, r1=3.6, a0=0.55, a1=0.12):
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i/(n-1) if n > 1 else 0
        ax.add_patch(Circle((x, y), r0 + (r1-r0)*t, color=SMOKE, alpha=a0 + (a1-a0)*t, lw=0))

# ---- case 1: with chute
x0 = 0
hearth_section(axB, x0)
for k in range(1, 4):
    rect(axB, x0+16, 16*k, 16, 16, STONE, ec="#222", lw=1.2)
    rect(axB, x0+20, 16*k, 8, 16, VOID, ec="#444", lw=0.8, ls="--")
# ceiling band across the room + attic floor line
rect(axB, x0-16, 40, 32, 2, "#a89f92", ec="#222", lw=1)
rect(axB, x0-16, 0, 32, 40, "none", ec="#222", lw=1.2, ls=":")
# cap on the top flue
rect(axB, x0+13, 62, 22, 3, STONE_D, ec="#222")
rect(axB, x0+14.5, 65, 19, 1.5, STONE_D, ec="#222")
smoke_puffs(axB, [(x0+24, 69), (x0+25, 74), (x0+23.5, 79.5), (x0+25.5, 85.5), (x0+23, 92)])
axB.text(x0+30, 84, "exhaust: pw:chimney_smoke\nparticle from the CAPPED\nflue while lit", ha="left", va="center", fontsize=10.5)
axB.text(x0+0, 20, "ROOM\n(zone)\nstays clear", ha="center", va="center", fontsize=12, color="#444")
axB.text(x0+24, 8, "hearth", ha="center", va="center", fontsize=10, color="#333", bbox=dict(fc="white", ec="none", alpha=0.7, pad=1.5))
for k in range(1, 4):
    axB.text(x0+33.5, 16*k+8, "pw:flue" + ("  · pw:cap = true (nothing above)" if k == 3 else ""), fontsize=10.5, va="center")
axB.text(x0+8, -4.5, "floor (feet 0)", ha="center", va="top", fontsize=10.5)
axB.plot([x0-18, x0+50], [0, 0], color="#222", lw=1.5)
axB.text(x0-19, 42.5, "ceiling", fontsize=10, va="bottom")

# ---- case 2: no chute
x1 = 66
hearth_section(axB, x1)
for k in range(1, 3):
    rect(axB, x1+16, 16*k, 16, 16, STONE, ec="#222", lw=1.2)
rect(axB, x1-16, 40, 32, 2, "#a89f92", ec="#222", lw=1)
rect(axB, x1-16, 0, 32, 40, "none", ec=RED, lw=2, ls="--")
axB.plot([x1-18, x1+50], [0, 0], color="#222", lw=1.5)
# room smoke: denser towards the ceiling
pts = []
for _ in range(70):
    y = 40 - abs(random.gauss(0, 12)); y = max(4, min(38.5, y))
    pts.append((x1-15 + random.random()*30, y))
for (x, y) in pts:
    axB.add_patch(Circle((x, y), 1.2 + random.random()*1.6, color=SMOKE, alpha=0.18 + 0.32*(y/40), lw=0))
axB.text(x1+34, 24, "plain wall block\nabove → chute\ncheck FAILS", fontsize=10.5, va="center")
axB.text(x1+0, -4.5, "registered zone (the ring you place) = the fill volume", ha="center", va="top", fontsize=10.5, color=RED)
axB.text(x1-16, 58, "smoke LEVEL 0→15 per room:\n  +1 per smoke tick while blocked, −1 when clear\n"
                   "if level ≥ 1: emit pw:room_smoke (block-colliding,\n  slow rise, 10–20 s life), count ∝ level, ceiling-biased\n"
                   "if level ≥ 8: push a smoke fog on players in the zone\n"
                   "if level ≥ 12: cough sound + (optional) effects",
         ha="left", va="bottom", fontsize=10.5, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#999"))
caption(axB, "Chute check = a walk UP from the hearth: every cell must be pw:flue until air/sky → exhaust at the last flue (auto-capped). "
             "Any other block ends the walk → blocked → the room's smoke level climbs. Nothing is tracked per particle: particles are "
             "client-side and fire-and-forget in Bedrock, so the model is a state number per room and re-emission each tick.", y=-0.03)

# ───────────────────────────── D · ridge / 45° collision — as built ─────────────────────────────
axD = fig.add_subplot(gs[1, 1]); axD.set_aspect("equal"); axD.set_axis_off()
axD.set_xlim(-30, 52); axD.set_ylim(-19, 36)
axD.set_title("D · roof section AS BUILT (RP-04 .127 geometry · BP-02 .177 collision): solid wedges, mean-plane boxes", fontsize=15, loc="left")
FILL = "#9c8468"
# cells (dotted)
for (x, y) in [(-24, 0), (8, 0), (-8, 16), (-24, -16), (-8, -16), (8, -16), (-8, 0)]:
    rect(axD, x, y, 16, 16, "none", ec="#999", lw=1, ls=":")
def wedge(ax, x0, mirror=False):
    # stepped fill under the board; rises toward the ridge. x0 = cell's outer (thin) edge.
    pts = []
    sgn = -1 if mirror else 1
    # thin edge at x0, tall edge at x0+16*sgn
    xt = x0 + 16*sgn
    poly = [(x0 + 2*sgn, 0), (xt, 0), (xt, 14)]
    for k in range(7, 0, -1):          # layer k spans y 2(k-1)..2k and x from x0+2k*sgn to the tall edge (RP-04 .127 fill layers)
        poly.append((x0 + 2*k*sgn, 2*k)); poly.append((x0 + 2*k*sgn, 2*k - 2))
    ax.add_patch(Polygon(poly, closed=True, facecolor=FILL, edgecolor="#5a4a3a", lw=1))
    ax.plot([x0, xt], [0.6, 16.6], color=BOARD, lw=8, solid_capstyle="butt")   # the rotated board on the hypotenuse
wedge(axD, -24); wedge(axD, 24, mirror=True)
# ridge: low solid triangle, peak 9.65 above its cell base (y 16)
tri = [(-6, 16), (6, 16), (6, 18), (4, 18), (4, 20), (2, 20), (2, 22), (-2, 22), (-2, 20), (-4, 20), (-4, 18), (-6, 18)]
axD.add_patch(Polygon(tri, closed=True, facecolor=FILL, edgecolor="#5a4a3a", lw=1))
axD.plot([-7.15, 0], [16.85, 25.2], color=BOARD, lw=8, solid_capstyle="butt")
axD.plot([7.15, 0], [16.85, 25.2], color=BOARD, lw=8, solid_capstyle="butt")
# collision boxes (red hatch): wedges y 0..8, ridge y 16..24
for (x, y) in [(-24, 0), (8, 0), (-8, 16)]:
    axD.add_patch(Rectangle((x, y), 16, 8, facecolor="none", edgecolor=RED, hatch="//", lw=1.8))
# annotations
axD.annotate("box without solid:\nyou FLOAT here from outside", xy=(-21, 5), xytext=(-29, 12.5), fontsize=10, color=RED,
             arrowprops=dict(arrowstyle="-|>", color=RED))
axD.annotate("solid without box\n(y 8..14 on the tall side):\nyou CLIP into it from the loft", xy=(-9.5, 11), xytext=(-29, 27), fontsize=10, color="#5a4a3a",
             arrowprops=dict(arrowstyle="-|>", color="#5a4a3a"))
axD.text(0, 34, "ridge = 9.65-cube solid triangle · box y 0..8 of its cell ≈ tight already", ha="center", va="center", fontsize=10.5,
         bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
axD.annotate("", xy=(0, 25.5), xytext=(0, 31.5), arrowprops=dict(arrowstyle="-|>", color="#333"))
axD.text(0, 8, "LOFT slot\n(1 cell wide)", ha="center", va="center", fontsize=10.5, color="#555")
axD.text(0, -10, "LOFT — the ceiling you see = the wedges' flat bottoms\n+ 14-cube risers: a STAIRCASE, not a slope",
         ha="center", va="center", fontsize=10.5, color="#555", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
axD.text(-16, -3.5, "box y 0..8 = the board's MEAN height\n(error ±8 instead of 0..16)", ha="center", va="center", fontsize=9.5, color=RED,
         bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
# numbers box (rotation-aware solid extents)
axD.text(27.5, 34.5, "piece · collision box · solid extent", fontsize=10.5, va="top", weight="bold")
rows = [
    ("roof45 straight", "16×8×16 @ y0",  "y 0..17.7, z −8..8.9"),
    ("roof45 ridge",    "16×8×16 @ y0",  "y 0..9.65 (peak)"),
    ("ridge end",       "16×8×16 @ y0",  "y 0..10"),
    ("roof63 lower",    "16×16×8 @ z0",  "y −1.4..16.5, z −9.1..8"),
    ("roof63 upper",    "16×16×8 @ z0",  "y 0..16.5, z −1.1..8"),
    ("hip",             "16×8×16 @ y0",  "y −1.4..16.5"),
    ("pyramidion (cap?)", "14×8×14 @ y0", "y −3.55..9.2, x/z ±9.25"),
    ("gusset lower",    "16×16×16",      "y 0..17.5, x ±11.3"),
    ("gusset upper",    "16×16×16",      "y 0..16"),
]
yy = 31.5
for a, b, c in rows:
    axD.text(27.5, yy, f"{a}\n   {b} · {c}", fontsize=9.4, va="top", family="DejaVu Sans Mono"); yy -= 4.9
caption(axD, "Engine law: ONE axis-aligned collision box per custom block — no slopes, no compound hulls. The roof pieces are SOLID "
             "wedges (stepped fill under a 45°-rotated board), and their boxes already sit on the board's mean plane; the ridge and "
             "the cap (pyramidion) boxes are already close to their solid extents. Any smaller box trades a float for a clip. So "
             "before proposing anything: what did you run into — walking the ridge, building from the loft, head-bumps? And rafters "
             "only make sense on HOLLOW interior-facing pieces (route A) — see the reply.", y=-0.03)

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
