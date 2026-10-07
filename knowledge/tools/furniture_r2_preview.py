#!/usr/bin/env python3
"""furniture_r2_preview.py — round-1 vs round-2 comparison sheet for the 19:46 witness items.
Row 1 mantel over a hearth-height block (r1 | r2 | r2 side view), row 2 wall shelf (r1 | r2 | r2 side), row 3 table
leg/rail corner (r1 | r2 | r2 joined pair), row 4 trestle crossing + barrel top (r1 | r2)."""
import sys, importlib.util, copy
sys.path.insert(0, "/home/claude/tools")
import furniture_render as R, furniture_geo as G2, build_furniture as BF
from PIL import Image, ImageDraw, ImageFont
spec = importlib.util.spec_from_file_location("g1", "/home/claude/_build/furniture_geo_r1_backup.py"); G1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(G1)
MATS = {**R.WOODS["oak"], "iron": R.IRON, "stone": "cobblestone"}

def shift(boxes, dx=0, dy=0, dz=0):
    out = []
    for b in boxes:
        c = copy.deepcopy(b); c["o"] = [b["o"][0] + dx, b["o"][1] + dy, b["o"][2] + dz]
        if "piv" in c: c["piv"] = [c["piv"][0] + dx, c["piv"][1] + dy, c["piv"][2] + dz]
        out.append(c)
    return out

def hearth_block():
    # stand-in for the homestead hearth cell under the mantel: stone frame with a dark opening (front face at z = 0)
    return [G2.B([0, 0, 0], [16, 16, 16], "stone")]

def shot(boxes, cam, wall=True):
    base = R.scene_faces(MATS, wall=wall)
    pf = [f for b in boxes for f in R.box_faces(b, MATS, boxes)]
    return R.render(base + pf, cam)

C = 300
def cams_front(h, y0=0): return R.Camera((-10, y0 + 22, -26), (8, y0 + h / 2, 8), C, C, 40)
def cam_side(h, y0=0):   return R.Camera((-26, y0 + 18, -6), (4, y0 + h / 2, 10), C, C, 40)

rows = []
# mantel on the hearth block
m1 = hearth_block() + shift(G1.PIECES["mantel"]["boxes"], dy=16); m2 = hearth_block() + shift(G2.PIECES["mantel"]["boxes"], dy=16)
rows.append(("mantel on a hearth-height block (cobble stand-in): r1 board top 8, corbels 3x4 | r2 board top 5 (down 3 cubes), corbels 2x2 inset 1",
             [shot(m1, cams_front(8, 16)), shot(m2, cams_front(5, 16)), shot(m2, cam_side(5, 16))], ["r1", "r2", "r2 left end (F04 angle)"]))
w1 = shift(G1.PIECES["wall_shelf"]["boxes"], dy=16); w2 = shift(G2.PIECES["wall_shelf"]["boxes"], dy=16)
rows.append(("wall shelf one cell up the wall: r1 top 13 | r2 top 8 (= r1 mantel height)",
             [shot(w1, cams_front(13, 16)), shot(w2, cams_front(8, 16)), shot(w2, cam_side(8, 16))], ["r1", "r2", "r2 left end"]))
t1 = G1.PIECES["table"]["boxes"]; t2 = BF.table_variant((False, False, False, False))
pair = BF.table_variant((False, True, False, False)) + shift(BF.table_variant((False, False, False, True)), dx=16)
cl = R.Camera((-6, 14, -14), (4, 9, 4), C, C, 34)
rows.append(("table leg + apron corner (F01): r1 rail face flush with the leg face (z-fight) | r2 rail 0.5 behind, between the legs | r2 two tables joined",
             [shot(t1, cl, wall=False), shot(t2, cl, wall=False), shot(pair, R.Camera((-8, 26, -30), (16, 7, 8), C, C, 46), wall=False)], ["r1 close", "r2 close", "r2 joined e|w"]))
tr1 = G1.PIECES["trestle"]["boxes"]; tr2 = G2.PIECES["trestle"]["boxes"]; b2 = G2.PIECES["barrel_seat"]["boxes"]
rows.append(("trestle crossing legs half-lapped 0.5 (r1 shared side planes) | barrel seat bands stepped 0.1 (r1: 4 tops in one plane)",
             [shot(tr1, R.Camera((-20, 12, 2), (8, 7, 8), C, C, 44), wall=False), shot(tr2, R.Camera((-20, 12, 2), (8, 7, 8), C, C, 44), wall=False),
              shot(b2, R.Camera((8, 30, -2), (8, 8, 8), C, C, 40), wall=False)], ["trestle r1", "trestle r2", "barrel r2 top"]))

try: font = R.ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
except Exception: font = ImageFont.load_default()
W = 3 * (C + 6) + 6; H = len(rows) * (C + 48) + 30
img = Image.new("RGBA", (W, H), (18, 18, 20, 255)); d = ImageDraw.Draw(img)
for r, (title, shots, labels) in enumerate(rows):
    y = 26 + r * (C + 48)
    d.text((6, y - 20), title, fill=(255, 220, 140, 255), font=font)
    for c, (im, lab) in enumerate(zip(shots, labels)):
        x = 6 + c * (C + 6); img.paste(im, (x, y)); d.text((x + 4, y + C + 4), lab, fill=(225, 225, 225, 255), font=font)
d.text((8, H - 20), "pw:furniture ROUND 2 vs ROUND 1 — oak, Patrix stems; painter's preview (no z-buffer): coplanar pairs show here as seams, in game they flicker", fill=(170, 170, 170, 255), font=font)
out = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/furniture-r2-vs-r1.png"
img.save(out); print(out, img.size)
