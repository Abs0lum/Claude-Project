#!/usr/bin/env python3
"""seam_preview.py — BEFORE/AFTER preview sheet for the seam cuts (D-C207), rendered from the shipped RP-04 v1.3.129
textures + geometry through profile_render.  Nothing in any pack is modified.

Cases (east side, block px, 48 screen px per block px):
  A  roof45_straight (spruce) -> roof45_straight above (course seam)      cut: lower board  forbid z > 8   (plumb)
  A' roof45_straight (spruce) -> roof45_ridge cap above (cap bottom corner) cut: same
  B  pw_ramp_4_q1 -> pw_ramp_4_q2 (cobble) seam                            cuts: q2 board forbid y < 4 (level, plinth top)
                                                                                q1 board forbid z > 7.709 (plumb, cap front)
  C  pw_ramp_2_lo_snow3 (stonebrick) toe                                   cuts: board forbid y < 0 (level) + forbid z < -5.58
                                                                                (plumb at the snow filler's inner plane — Abs0lum: cut the BOARD)
Magenta = fight pixels (two opaque faces within 0.06 px whose colours differ), area printed in px².
"""
import json, sys
sys.path.insert(0, "/home/claude/tools")
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import profile_render as pr

RP = "/home/claude/_build/rp04-129"
OUT = "/home/claude/_design/seam-cuts-preview-v1.png"
SCALE = 48

def geo(stem, ident=None):
    doc = json.load(open(f"{RP}/models/blocks/{stem}.geo.json", encoding="utf-8-sig"))
    for g in doc["minecraft:geometry"]:
        if ident is None or g["description"]["identifier"] == ident:
            return g
    raise KeyError(ident)

def tex(name, alt=None):
    p = f"{RP}/textures/blocks/{name}.png"
    try:
        return pr.load_tex(p)
    except FileNotFoundError:
        return pr.load_tex(alt)

F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)

def case_roof(cap):
    tm = {"*": tex("pw_roof_spruce"), "mitre": tex("pw_mitre_spruce"), "fill": tex("pw_fill_45_spruce"), "deck": tex("pw_deck45_spruce")}
    tmc = dict(tm); tmc["fill"] = tex("pw_fill_ridge_spruce"); tmc["deck"] = tex("pw_deck45h_spruce")
    lower = geo("roof45_straight")
    upper = geo("roof45_ridge") if cap else geo("roof45_straight")
    faces = pr.faces_of(lower, "east", tm, (0, 0), "L.") + pr.faces_of(upper, "east", tmc if cap else tm, (16, 16), "U.")
    win = (5.0, 11.0, 13.0, 20.0)
    before = pr.render(faces, "east", *win, SCALE)
    for f in faces:
        if f.tag == "L.root#0":                       # the lower board
            pr.face_cut_halfplane(f, "z", ">", 8.0)
    after = pr.render(faces, "east", *win, SCALE)
    return before, after, win

def case_ramp_seam():
    tm1 = {"*": tex("pw_rampv4_cobble_0"), "fill": tex("pw_fill14q1_cobble"), "deck": tex("pw_deck14_cobble_0")}
    tm2 = dict(tm1); tm2["fill"] = tex("pw_fill14q2_cobble")
    q1 = geo("pw_ramps", "geometry.pw_ramp_4_q1"); q2 = geo("pw_ramps", "geometry.pw_ramp_4_q2")
    faces = pr.faces_of(q1, "east", tm1, (0, -16), "q1.") + pr.faces_of(q2, "east", tm2, (0, 0), "q2.")
    win = (-11.0, -1.0, 0.5, 7.5)
    before = pr.render(faces, "east", *win, SCALE)
    for f in faces:
        if f.tag == "q2.ramp#2": pr.face_cut_halfplane(f, "y", "<", 4.0)          # level cut at the plinth top
        if f.tag == "q1.ramp#1": pr.face_cut_halfplane(f, "z", ">", 7.709 - 16.0)  # plumb cut at the cap front
    after = pr.render(faces, "east", *win, SCALE)
    return before, after, win

def case_snow_toe():
    tm = {"*": tex("pw_rampv4_stonebrick_0"), "fill": tex("pw_fill26l_stonebrick"), "deck": tex("pw_deck26_stonebrick_0"),
          "snow": pr.load_tex("/home/claude/_intake/snow_v0.png")}
    g = geo("pw_snowcaps", "geometry.pw_ramp_2_lo_snow3")
    faces = pr.faces_of(g, "east", tm, (0, 0), "s3.")
    win = (-9.0, -1.0, -1.5, 7.5)
    before = pr.render(faces, "east", *win, SCALE)
    for f in faces:
        if f.tag == "s3.ramp#3":
            pr.face_cut_halfplane(f, "y", "<", 0.0)        # level cut at the toe (block base)
            pr.face_cut_halfplane(f, "z", "<", -5.58)      # plumb cut at the snow filler's inner plane (board loses)
    after = pr.render(faces, "east", *win, SCALE)
    for f in faces:
        if f.tag == "s3.ramp#5":                       # the snow slab also loses to the nearer filler
            pr.face_cut_halfplane(f, "z", "<", -5.58)
    after2 = pr.render(faces, "east", *win, SCALE)
    return before, after, win, after2

import textwrap
def panel(sheet, x, y, title, renders, notes, cell_w=730):
    """renders = [(label, (img, fight, area, pairs)), ...]"""
    d = ImageDraw.Draw(sheet)
    for i, line in enumerate(textwrap.wrap(title, 96)):
        d.text((x, y + 19 * i), line, fill=(255, 255, 255), font=FB)
    y += 19 * len(textwrap.wrap(title, 96)) + 6
    xx = x; hmax = 0
    for label, (img, fight, area, pairs) in renders:
        im = pr.overlay_fights(img, fight)
        if im.width > 300: im = im.resize((300, int(im.height * 300 / im.width)))
        sheet.paste(im, (xx, y)); hmax = max(hmax, im.height)
        col = (255, 120, 255) if label.startswith("BEFORE") else (120, 255, 160)
        d.text((xx, y + im.height + 4), f"{label} — fight {area:.3f} px²", fill=col, font=F)
        xx += im.width + 12
    yy = y + hmax + 26
    for n in notes:
        for line in textwrap.wrap(n, 118):
            d.text((x, yy), line, fill=(200, 200, 200), font=F); yy += 17
    pb = renders[0][1][3]
    for k, v in sorted(pb.items(), key=lambda kv: -kv[1])[:3]:
        d.text((x, yy), f"  pair {k[0]} vs {k[1]}: {v:.3f} px²", fill=(255, 160, 255), font=F); yy += 17
    return yy

def main():
    A = case_roof(False); A2 = case_roof(True); B = case_ramp_seam(); C = case_snow_toe()
    sheet = Image.new("RGB", (1900, 1250), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    d.text((20, 10), "SEAM CUT PREVIEW v1 — RP-04 v1.3.129 geometry + textures as shipped, east side, 48 px per block px", fill=(255, 255, 255), font=FB)
    d.text((20, 30), "magenta = two opaque faces within 0.06 px painting different texels (Δ > 8/255) — the phone stipples exactly there. Nothing in any pack was modified.", fill=(200, 200, 200), font=F)
    ya = panel(sheet, 20, 60, "A · roof45 course seam (spruce) — the lower board's overshoot inside the upper block's plumb filler",
               [("BEFORE", A[0]), ("AFTER", A[1])],
               ["CUT · roof45 board · east/west · plumb · flush: top-surface corner at z=8 · 135°: underside — in place in the pw_mitre_* strips, all 3 materials. Residual 0.022 = the upper board's own corner, accepted at .127."])
    yb = panel(sheet, 980, 60, "A' · the same seam against the RIDGE CAP — his 'roof caps bottom corners'",
               [("BEFORE", A2[0]), ("AFTER", A2[1])],
               ["Same cut, same board. The cap's plumb filler paints a DIFFERENT texel everywhere over the overshoot (0.612 px², solid) where the straight's filler differs only in spots (0.178) — that is why the cap corners show and the course seams barely do. The cap's own boards already end plumb: untouched."])
    y = max(ya, yb) + 16
    yc = panel(sheet, 20, y, "B · ramp seam q1 → q2 (cobble, 14°) — q2's board dips into its plinth; q1's cap filler covers its board end",
               [("BEFORE", B[0]), ("AFTER", B[1])],
               ["CUT · deck · side · level · flush: top-surface toe corner  +  CUT · deck · side · plumb · flush: top-surface high corner. Same two cuts on all six shapes (base-independent), 26.57° pieces with their own angle."])
    yd = panel(sheet, 980, y, "C · snow toe, pw_ramp_2_lo_snow3 (stonebrick) — the snow toe filler over the board AND over the slab",
               [("BEFORE", C[0]), ("AFTER board cut", C[1]), ("AFTER board+slab cut", C[3])],
               ["Ruling (b): the BOARD loses — plumb cut at the filler's inner plane (z=-5.58 at L3/26.57°, per level) + the level toe cut. Left over: the filler vs the snow SLAB, snow on snow, 3.7 px² by the metric — I saw no stipple there in F9, but it is above the 0.455 bar; the third image also cuts the slab at the same plane (its own snowcut strip). Consequence either way: the filler's snow paints down to the block base at the toe (2.4 × 1.2 px wedge under the deck line)."])
    sheet.save(OUT); print(OUT, sheet.size)
    for name, c in (("A", A), ("A'", A2), ("B", B), ("C", C)):
        print(name, "before %.3f after %.3f" % (c[0][2], c[1][2]), {k: round(v, 3) for k, v in c[0][3].items()})

if __name__ == "__main__":
    main()
