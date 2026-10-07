#!/usr/bin/env python3
"""seam_figure.py — the 0.02-px seam mechanism, drawn from the shipped geometry (RP-04 v1.3.129).

Left  : ramp toe, pw_ramp_2_lo_snow3 (26.57 deg, snow L3) — the snow toe filler (x=+-8) sits 0.02 px in
        front of the deck board (x=+-7.98) over the triangle UNDER the slope line.
Middle: ramp seam, pw_ramp_4_q2 (14 deg) — the board's perpendicular toe cut dips into the plinth (x=+-8).
Right : roof course junction, roof45_straight -> next course / roof45_ridge cap — the lower board's
        overshoot (x=+-7.98) sits inside the upper block's plumb filler (x=+-8).
All overlaps hatched; numbers in block px (16 per block).  Witness crops from the 10:35 round beside them.
"""
import math
from PIL import Image, ImageDraw, ImageFont

OUT = "/home/claude/_design/seam-mechanism-v1.png"
S = 40            # screen px per block px
W, H = 1900, 1140
img = Image.new("RGB", (W, H), (28, 28, 32))
d = ImageDraw.Draw(img)
PW, PH = 610, 560
def new_panel():
    global img, d
    img = Image.new("RGB", (PW, PH), (28, 28, 32)); d = ImageDraw.Draw(img)
    return img
MAIN = Image.new("RGB", (W, H), (28, 28, 32))
try:
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
except Exception:
    F = FB = ImageFont.load_default()

def panel(ox, oy, title):
    d.rectangle([0, 0, PW - 1, PH - 1], outline=(70, 70, 76))
    d.text((10, 8), title, fill=(255, 255, 255), font=FB)

def P(ox, oy, z, y, z0, y0):
    """block (z,y) px -> screen; z0,y0 = block coords shown at the panel origin (bottom-left)."""
    return ox + (z - z0) * S, oy - (y - y0) * S

def poly(ox, oy, pts, z0, y0, fill=None, outline=(230, 230, 230), width=2):
    d.polygon([P(ox, oy, z, y, z0, y0) for z, y in pts], fill=fill, outline=outline, width=width)

def hatch(ox, oy, pts, z0, y0, color=(255, 80, 80)):
    xs = [P(ox, oy, z, y, z0, y0) for z, y in pts]
    minx = min(x for x, _ in xs); maxx = max(x for x, _ in xs); miny = min(y for _, y in xs); maxy = max(y for _, y in xs)
    mask = Image.new("L", img.size, 0); ImageDraw.Draw(mask).polygon(xs, fill=255)
    lay = Image.new("RGB", img.size, (28, 28, 32)); ld = ImageDraw.Draw(lay)
    x = minx - (maxy - miny)
    while x < maxx + 1:
        ld.line([(x, maxy), (x + (maxy - miny), miny)], fill=color, width=2); x += 7
    img.paste(lay, (0, 0), mask)
    d.polygon(xs, outline=color, width=2)

def label(ox, oy, z, y, z0, y0, text, color=(255, 255, 255), dx=6, dy=-8):
    x, yy = P(ox, oy, z, y, z0, y0); d.text((x + dx, yy + dy), text, fill=color, font=F)

def rot(pt, piv, deg):
    """JSON +deg about x lifts the +z end (SIGN -1 calibration): (y,z) in the profile plane."""
    y, z = pt[0] - piv[0], pt[1] - piv[1]
    a = math.radians(deg)
    return (y * math.cos(a) + z * math.sin(a) + piv[0], -y * math.sin(a) + z * math.cos(a) + piv[1])

def board_profile(o, s, deg, piv):
    ys = (o[1], o[1] + s[1]); zs = (o[2], o[2] + s[2])
    c = [rot((y, z), (piv[1], piv[2]), deg) for y in ys for z in zs]      # (y,z)
    tl, th, bl, bh = c[3], c[2], c[1], c[0]   # top-low? order: (y0,z0)(y0,z1)(y1,z0)(y1,z1)
    return c

# ---------------------------------------------------------------- panel 1: ramp toe, 2_lo_snow3
new_panel(); ox, oy = 60, 470; z0, y0 = -8.6, -1.9
panel(ox, oy, "1 · ramp toe · pw_ramp_2_lo_snow3 (26.57°, snow L3)")
d.text((10, 30), "snow toe filler x=±8 sits 0.02 px in front of the deck board x=±7.98", fill=(200,200,200), font=F)
th = math.radians(26.5651)
# deck board: o [-7.98,-1.2,-8] s [.,1.2,17.2885] rot +26.57 piv (0,0,-8)
c = board_profile([-7.98, -1.2, -8.0], [15.96, 1.2, 17.2885], 26.5651, [0, 0, -8])
bpts = [(c[0][1], c[0][0]), (c[1][1], c[1][0]), (c[3][1], c[3][0]), (c[2][1], c[2][0])]   # (z,y)
poly(ox, oy, bpts, z0, y0, fill=(95, 90, 85), outline=(200, 200, 200))
# snow slab: o [-7.98,0.02,-5.3067] s [.,5.3666,15.2053]
c = board_profile([-7.98, 0.02, -5.3067], [15.96, 5.3666, 15.2053], 26.5651, [0, 0, -8])
spts = [(c[0][1], c[0][0]), (c[1][1], c[1][0]), (c[3][1], c[3][0]), (c[2][1], c[2][0])]
poly(ox, oy, spts, z0, y0, fill=(225, 230, 240), outline=(200, 200, 200))
# toe filler: o [-8,0.02,-8] s [16,6.0024,2.42]
fz0, fz1, fy0, fy1 = -8.0, -5.58, 0.02, 6.0224
poly(ox, oy, [(fz0, fy0), (fz1, fy0), (fz1, fy1), (fz0, fy1)], z0, y0, fill=None, outline=(120, 170, 255), width=3)
# overlap: filler rect ∩ board face = under the slope line, above y=0.02, z<-5.58
k = math.tan(th)
tri = [(fz0, fy0), (fz1, fy0), (fz1, fy0 + k * (fz1 - fz0))]
hatch(ox, oy, tri, z0, y0)
# cell + ground
d.line([P(ox, oy, -8, -1.4, z0, y0), P(ox, oy, -8, 7.5, z0, y0)], fill=(90, 90, 90), width=1)
d.line([P(ox, oy, -8.6, 0, z0, y0), P(ox, oy, 0.5, 0, z0, y0)], fill=(90, 90, 90), width=1)
label(ox, oy, -8.0, 7.6, z0, y0, "boundary z=-8", (150, 150, 150), dx=-30, dy=-22)
label(ox, oy, -5.4, 5.6, z0, y0, "snow toe FILLER (axis box, x=±8)", (120, 170, 255))
label(ox, oy, -3.8, 4.6, z0, y0, "snow slab (x=±7.98)", (60, 60, 80))
label(ox, oy, -2.4, 1.6, z0, y0, "deck board (x=±7.98)", (220, 200, 180))
label(ox, oy, -8.4, -0.55, z0, y0, "FIGHT: 2.42 × 1.21 px triangle = 1.46 px², snow vs stone", (255, 120, 120))
label(ox, oy, -8.4, -1.0, z0, y0, "(L3 @ 14°: 1.43 × 0.36 = 0.26 px²)   witness F3_A · F4_A · F9_A2", (255, 120, 120))
label(ox, oy, -8.4, -1.45, z0, y0, "ground block below (hides the R-4 dip)", (110, 110, 110), dy=4)
d.rectangle([0,0,PW-1,28],fill=(28,28,32)); panel(ox, oy, "1 · ramp toe · pw_ramp_2_lo_snow3 (26.57°, snow L3)")
MAIN.paste(img, (20, 20))

# ---------------------------------------------------------------- panel 2: ramp seam, q2 toe
new_panel(); ox, oy = 60, 470; z0, y0 = -8.6, 1.3
panel(ox, oy, "2 · ramp seam · pw_ramp_4_q2 toe (14.04°)")
d.text((10, 30), "the board's square-cut toe dips into its own plinth (x=±8), 0.02 px behind it", fill=(200,200,200), font=F)
th2 = math.radians(14.0362)
poly(ox, oy, [(-8, 0), (0.5, 0), (0.5, 4), (-8, 4)], z0, y0, fill=(78, 78, 78), outline=(200, 200, 200))
c = board_profile([-7.98, 2.8, -8.0], [15.96, 1.2, 16.1924], 14.0362, [0, 4, -8])
bpts = [(c[0][1], c[0][0]), (c[1][1], c[1][0]), (c[3][1], c[3][0]), (c[2][1], c[2][0])]
poly(ox, oy, bpts, z0, y0, fill=(95, 90, 85), outline=(200, 200, 200))
# dip triangle: end face (-8,4)->(-7.709,2.836), underside to (-3.05,4)
hatch(ox, oy, [(-8, 4.0), (-7.709, 2.836), (-3.05, 4.0)], z0, y0)
d.line([P(ox, oy, -8, 1.5, z0, y0), P(ox, oy, -8, 8.5, z0, y0)], fill=(90, 90, 90), width=1)
label(ox, oy, -8.0, 9.6, z0, y0, "seam z=-8", (150, 150, 150), dx=-25, dy=-22)
label(ox, oy, -5.0, 2.4, z0, y0, "plinth / body (x=±8)", (200, 200, 200))
label(ox, oy, -3.0, 5.6, z0, y0, "deck board (x=±7.98)", (220, 200, 180))
label(ox, oy, -8.4, 8.6, z0, y0, "FIGHT: 4.95 × 1.16 px triangle = 2.88 px² per side", (255, 120, 120))
label(ox, oy, -8.4, 8.1, z0, y0, "(26.57° pieces: 2.68 × 1.07 = 1.44 px²)   witness F6_B2 · F6_C", (255, 120, 120))
label(ox, oy, -8.4, 7.6, z0, y0, "base-0 pieces (q1, 2_lo): same dip, inside the ground block (R-4)", (200, 200, 200))
# high end cap
label(ox, oy, -8.4, 1.0, z0, y0, "high end (not drawn): cap filler x=±8 over the board", (200, 200, 200))
label(ox, oy, -8.4, 0.55, z0, y0, "= 0.29 × 1.17 px = 0.17 px² (26.57°: 0.54 × 1.34 = 0.36 px²)", (200, 200, 200))
d.rectangle([0,0,PW-1,28],fill=(28,28,32)); panel(ox, oy, "2 · ramp seam · pw_ramp_4_q2 toe (14.04°)")
MAIN.paste(img, (650, 20))

# ---------------------------------------------------------------- panel 3: roof junction
new_panel(); ox, oy = 60, 470; z0, y0 = -9.6, -2.9
panel(ox, oy, "3 · roof junction · lower roof45 → next course / ridge cap")
d.text((10, 30), "the lower board's overshoot (x=±7.98) inside the upper block's plumb filler (x=±8)", fill=(200,200,200), font=F)
# upper block frame: filler o [-8,0,-8] s [16,1.6971,0.8485]; its own board low end plumb-cut
poly(ox, oy, [(-8, 0), (-7.1515, 0), (-7.1515, 1.6971), (-8, 1.6971)], z0, y0, fill=None, outline=(120, 170, 255), width=3)
# upper board (roof45_straight cube 0) — draw its low part
c = board_profile([-7.98, 6.471, -9.563], [15.96, 1.2, 22.627], 45, [0, 6.571, -1.571])
bpts = [(c[0][1], c[0][0]), (c[1][1], c[1][0]), (c[3][1], c[3][0]), (c[2][1], c[2][0])]
poly(ox, oy, bpts, z0, y0, fill=(95, 90, 85), outline=(200, 200, 200))
# lower board overshoot, in the upper cell's frame: triangle (-8,0) (-8,1.697) (-7.152,0.849)
poly(ox, oy, [(-9.4, -1.4), (-8, 0), (-8, 1.697), (-9.4, 0.297)], z0, y0, fill=(80, 75, 70), outline=(200, 200, 200))
hatch(ox, oy, [(-8, 0), (-8, 1.697), (-7.152, 0.849)], z0, y0)
d.line([P(ox, oy, -8, -1.4, z0, y0), P(ox, oy, -8, 6.5, z0, y0)], fill=(90, 90, 90), width=1)
label(ox, oy, -8.0, 7.0, z0, y0, "upper cell: z=-8, y=0", (150, 150, 150), dx=-50, dy=-22)
label(ox, oy, -7.0, 0.5, z0, y0, "upper PLUMB FILLER (x=±8)", (120, 170, 255))
label(ox, oy, -5.2, 3.2, z0, y0, "upper board (x=±7.98)", (220, 200, 180))
label(ox, oy, -5.2, 2.75, z0, y0, "(its own low corner: cropped at .127)", (200, 200, 200))
label(ox, oy, -9.5, -1.0, z0, y0, "lower board", (220, 200, 180))
label(ox, oy, -9.5, -1.7, z0, y0, "FIGHT: the overshoot past z=8 — 0.85 × 1.70 px triangle", (255, 120, 120))
label(ox, oy, -9.5, -2.15, z0, y0, "= 0.72 px² per side, every course seam + both cap corners", (255, 120, 120))
label(ox, oy, -9.5, -2.6, z0, y0, "witness F8_C2 · F8_B2 · F2_C — not in the per-block R-5 census", (200, 200, 200))
d.rectangle([0,0,PW-1,70],fill=(28,28,32)); panel(ox, oy, "3 · roof junction · lower roof45 → next course / ridge cap")
d.text((10, 30), "lower board's overshoot (x=±7.98) inside the upper block's", fill=(200,200,200), font=F); d.text((10, 48), "plumb filler (x=±8) — the cap is just the nearest such seam", fill=(200,200,200), font=F)
MAIN.paste(img, (1280, 20))
img = MAIN; d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- witness strip
crops = [("F9_A2 · snow toe (9×)", "/home/claude/_intake/frames-1035/crops/F9_A2_toe_9x.png"),
         ("F4_A · snow toe (3×)", "/home/claude/_intake/frames-1035/crops/F4_A_toe.png"),
         ("F6_B2 · q-seam streak (6×)", "/home/claude/_intake/frames-1035/crops/F6_B2_seam_patch_6x.png"),
         ("F8_C2 · cap bottom corner (6×)", "/home/claude/_intake/frames-1035/crops/F8_C2_right_junction_6x.png"),
         ("F2_C · top course junction (2×)", "/home/claude/_intake/frames-1035/crops/F2_C_rake_top.png")]
x = 40; y = 640
d.text((x, y - 30), "WITNESS 2026-09-22 10:35 (new world, BP-02 .181 / RP-04 .129) — crops at native scale × k", fill=(255, 255, 255), font=FB)
for name, p in crops:
    im = Image.open(p).convert("RGB"); im.thumbnail((360, 420))
    img.paste(im, (x, y)); d.text((x, y + im.height + 6), name, fill=(220, 220, 220), font=F)
    x += im.width + 14
img.save(OUT); print(OUT, img.size)
