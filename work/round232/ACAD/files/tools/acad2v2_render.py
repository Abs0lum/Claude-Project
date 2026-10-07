#!/usr/bin/env python3
"""Render the Academy II plans (ground / upper / basement) and the 3/4 massing sketch from acad2_layout.py.
Writes /home/claude/_docs/castle/ACADEMY-II-PLAN-{GROUND,UPPER,BASEMENT}.png and ACADEMY-II-MASSING.png."""
import math
from PIL import Image, ImageDraw, ImageFont

import acad2v2_layout as L

import os
# 1.3.232 (#23): ACAD_OUT overrides the cloud path so the GitHub session can render into its scratchpad
OUT = os.environ.get("ACAD_OUT", "/home/claude/_docs/castle/academy2_v2")
os.makedirs(OUT, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SCALE = 4                     # px per block
MX, MY = 70, 110              # map origin on the canvas
LEG_W = 760
SECRET = (205, 0, 140)


def font(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size)


def px(x, z):
    """block (x, z) -> canvas (cx, cy); z runs left->right, x runs top (gate) -> bottom (lake)"""
    return MX + z * SCALE, MY + x * SCALE


def fit_label(d, text, w, h):
    """largest font 16..8 whose text fits in w x h, trying wrap on ' | ' and spaces; returns (font, lines) or None"""
    for size in range(16, 7, -1):
        f = font(size, bold=size >= 12)
        cands = [[text]]
        if " | " in text:
            cands.append(text.split(" | "))
        words = text.replace(" | ", " ").split()
        if len(words) > 1:
            for k in range(1, len(words)):
                cands.append([" ".join(words[:k]), " ".join(words[k:])])
        for lines in cands:
            lw = max(d.textlength(t, font=f) for t in lines)
            lh = (size + 2) * len(lines)
            if lw <= w - 4 and lh <= h - 2:
                return f, lines
    return None


def draw_rect(d, cat, r, label, rot_labels, dash=False):
    fill, line = L.CAT[cat]
    x0, z0, x1, z1 = r
    a, b = px(x0, z0), px(x1 + 1, z1 + 1)
    d.rectangle([a, (b[0] - 1, b[1] - 1)], fill=fill, outline=line, width=2 if cat not in ("court", "garden") else 1)
    if cat == "cliff":
        for k in range(a[0] - (b[1] - a[1]), b[0], 10):            # hatch
            d.line([(max(a[0], k), a[1] + max(0, a[0] - k)), (min(b[0], k + (b[1] - a[1])), a[1] + min(b[1] - a[1], b[0] - k))],
                   fill=line, width=1)
    if cat == "catacomb":
        for gx in range(a[0] + 8, b[0], 16):
            d.line([(gx, a[1]), (gx, b[1])], fill=line, width=3)
        for gy in range(a[1] + 8, b[1], 16):
            d.line([(a[0], gy), (b[0], gy)], fill=line, width=3)
    if label:
        rot_labels.append((label, a, b))


def draw_rot_labels(img, rot_labels):
    """all labels, drawn after every rectangle; a tall narrow room gets its label rotated when that fits a bigger font"""
    d = ImageDraw.Draw(img)
    for label, a, b in rot_labels:
        w, h = b[0] - a[0], b[1] - a[1]
        flat = fit_label(d, label, w, h)
        tmp = Image.new("RGBA", (h, w), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        turned = fit_label(td, label, h, w) if h > w else None
        if turned and (not flat or turned[0].size > flat[0].size + 2):
            f, lines = turned
            lh = f.size + 2
            for i, t in enumerate(lines):
                tw = td.textlength(t, font=f)
                td.text((h / 2 - tw / 2, w / 2 - lh * len(lines) / 2 + i * lh), t, fill=(20, 20, 20, 255), font=f)
            tmp = tmp.rotate(90, expand=True)
            img.paste(tmp, (a[0], a[1]), tmp)
        elif flat:
            f, lines = flat
            lh = f.size + 2
            cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            for i, t in enumerate(lines):
                tw = d.textlength(t, font=f)
                d.text((cx - tw / 2, cy - lh * len(lines) / 2 + i * lh), t, fill=(20, 20, 20), font=f)
        else:
            print("  LABEL DOES NOT FIT:", label, (w, h))


def draw_route(d, pts, width=5):
    cp = [px(x, z) for (x, z) in pts]
    cp = [(c[0] + SCALE // 2, c[1] + SCALE // 2) for c in cp]
    for i in range(len(cp) - 1):
        (xa, ya), (xb, yb) = cp[i], cp[i + 1]
        n = max(1, int(math.hypot(xb - xa, yb - ya) // 10))
        for k in range(n):                                              # dashed
            if k % 2 == 0:
                t0, t1 = k / n, min(1, (k + 1) / n)
                d.line([(xa + (xb - xa) * t0, ya + (yb - ya) * t0), (xa + (xb - xa) * t1, ya + (yb - ya) * t1)], fill=SECRET, width=width)


def draw_marker(d, n, x, z):
    cx, cy = px(x, z)
    cx, cy = cx + SCALE // 2, cy + SCALE // 2
    r = 12
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SECRET, outline=(255, 255, 255), width=2)
    f = font(12, True)
    t = str(n)
    tw = d.textlength(t, font=f)
    d.text((cx - tw / 2, cy - 8), t, fill=(255, 255, 255), font=f)


def plan(level_key, rooms, title, subtitle, fname, extra_notes):
    W = MX + L.SIZE * SCALE + 40 + LEG_W
    H = MY + L.SIZE * SCALE + 90
    img = Image.new("RGB", (W, H), (252, 251, 247))
    d = ImageDraw.Draw(img)
    d.text((MX, 18), title, fill=(20, 20, 20), font=font(26, True))
    d.text((MX, 54), subtitle, fill=(60, 60, 60), font=font(15))
    # lake beyond the box (land job) and the town side
    if level_key in ("G", "B"):
        d.rectangle([px(384, 0)[0] - 0, px(384, 0)[1], px(384, 384)[0], px(384, 384)[1] + 34], fill=(170, 205, 236))
        d.text((MX + 10, px(384, 0)[1] + 8), "LAKE (land job, outside the box; surface about feet -13)", fill=(30, 70, 120), font=font(14, True))
    d.text((px(0, 120)[0], MY - 26), "x 0 = GATE SIDE: viaduct + town square", fill=(90, 50, 20), font=font(14, True))
    vx = px(0, 188)
    d.polygon([(vx[0], vx[1] - 2), (vx[0] + 8 * SCALE, vx[1] - 2), (vx[0] + 4 * SCALE, vx[1] - 18)], fill=(120, 80, 40))
    # piece grid
    for k in range(7):
        a, b = px(0, k * 64), px(384, k * 64)
        for y in range(a[1], b[1], 12):
            d.line([(a[0], y), (a[0], min(b[1], y + 6))], fill=(170, 170, 200), width=1)
        a, b = px(k * 64, 0), px(k * 64, 384)
        for x in range(a[0], b[0], 12):
            d.line([(x, a[1]), (min(b[0], x + 6), a[1])], fill=(170, 170, 200), width=1)
    for k in range(6):
        d.text((px(0, k * 64 + 26)[0], MY + L.SIZE * SCALE + 40), f"c{k}", fill=(110, 110, 150), font=font(13, True))
        d.text((MX - 30, px(k * 64 + 28, 0)[1]), f"r{k}", fill=(110, 110, 150), font=font(13, True))
    rot = []
    order = ["court", "garden", "wall", "cliff"]
    for pass_cats in (order, None):
        for cat, r, label in rooms:
            if (pass_cats is not None and cat in pass_cats) or (pass_cats is None and cat not in order):
                draw_rect(d, cat, r, label, rot)
    draw_rot_labels(img, rot)
    d = ImageDraw.Draw(img)
    # secrets
    here = []
    for n, (name, lv, mk, route) in L.SECRETS.items():
        if lv == level_key:
            if route:
                draw_route(d, route)
            here.append(n)
    if level_key == "B":
        for k, route in L.B_ROUTES.items():
            draw_route(d, route)
    for n, (name, lv, mk, route) in L.SECRETS.items():
        if lv == level_key:
            draw_marker(d, n, *mk)
    if level_key == "B":   # markers of multi-level secrets whose deep end lies here
        for n in (3, 17, 20, 26, 27, 32, 33):
            pts = L.B_ROUTES[n]
            draw_marker(d, n, *pts[-1])
        here += [3, 17, 20, 26, 27, 32, 33]
    # scale bar
    sx, sy = MX, MY + L.SIZE * SCALE + 62
    d.rectangle([sx, sy, sx + 64 * SCALE, sy + 6], fill=(40, 40, 40))
    d.text((sx + 64 * SCALE + 8, sy - 6), "64 blocks = one structure piece (1 block = 1 m)", fill=(40, 40, 40), font=font(13))
    # legend
    lx = MX + L.SIZE * SCALE + 40
    ly = MY
    d.text((lx, ly), "KEY", fill=(20, 20, 20), font=font(17, True))
    ly += 26
    used = []
    for cat, r, label in rooms:
        if cat not in used:
            used.append(cat)
    for cat in used + ([] if "secret" in used else ["secret"]):
        if cat == "passage":
            continue
        fill, line = L.CAT[cat]
        d.rectangle([lx, ly, lx + 22, ly + 14], fill=fill, outline=line, width=2)
        d.text((lx + 30, ly - 1), L.CAT_NAMES.get(cat, cat), fill=(30, 30, 30), font=font(13))
        ly += 20
    d.line([(lx, ly + 8), (lx + 22, ly + 8)], fill=SECRET, width=5)
    d.text((lx + 30, ly), "secret route (player discovery; household only)", fill=SECRET, font=font(13, True))
    ly += 30
    d.text((lx, ly), "SECRETS SHOWN ON THIS LEVEL", fill=(20, 20, 20), font=font(17, True))
    ly += 26
    for n in sorted(set(here)):
        d.text((lx, ly), f"{n:>2}  {L.SECRETS[n][0]}", fill=SECRET if L.SECRETS[n][1] == level_key else (120, 60, 100), font=font(13))
        ly += 18
    ly += 14
    for t in extra_notes:
        d.text((lx, ly), t, fill=(50, 50, 50), font=font(13))
        ly += 18
    img.save(f"{OUT}/{fname}")
    print("wrote", fname, img.size)


# ------------------------------------------------------------------ massing
def massing():
    CELL = 2
    N = 384 // CELL + 24                                   # include a lake band beyond x 383
    a, b, k = 5.0, 2.5, 2.4
    hmap = {}
    col = {}
    own = {}                      # 1.3.232 (#23): which MASS box (index + 1) shows at a cell; 0 = ground

    def setc(u, v, h, c, o=0):
        if (u, v) not in hmap or h > hmap[(u, v)]:
            hmap[(u, v)] = h
            col[(u, v)] = c
            own[(u, v)] = o

    for zi in range(384 // CELL):
        for xi in range(N):
            x = xi * CELL
            if x >= 384:
                setc(zi, xi, -13, (120, 170, 220))
            elif x >= 320:
                setc(zi, xi, -12, (215, 210, 190))
            elif 48 <= x and False:
                pass
            else:
                setc(zi, xi, 0, (200, 214, 170))
    # dry ditch
    for zi in range(0):   # v2: no dry ditch
        for xi in range(67 // CELL, 312 // CELL):
            setc(zi, xi, -12, (170, 160, 140)) if False else None
            hmap[(zi, xi)] = -12
            col[(zi, xi)] = (165, 155, 135)
    # courts paved
    for cat, r, label in L.G:
        if cat == "court" and r[0] < 320:
            for zi in range(r[1] // CELL, r[3] // CELL + 1):
                for xi in range(r[0] // CELL, r[2] // CELL + 1):
                    if hmap.get((zi, xi), 0) == 0:
                        col[(zi, xi)] = (226, 222, 205)
    for zi in range(188 // CELL, 196 // CELL):     # canal
        for xi in range(312 // CELL, N):
            hmap[(zi, xi)] = -13
            col[(zi, xi)] = (110, 160, 215)
    labels = []
    for mk, (x0, z0, x1, z1, h, roof, cat, label) in enumerate(L.MASS):
        base = -12 if x0 >= 320 else 0
        fill = L.CAT[cat][0] if cat != "water" else (200, 225, 240)
        cx, cz = (x0 + x1 + 1) / 2, (z0 + z1 + 1) / 2
        hx, hz = (x1 - x0 + 1) / 2, (z1 - z0 + 1) / 2
        top = base + h
        for zi in range(z0 // CELL, z1 // CELL + 1):
            for xi in range(x0 // CELL, x1 // CELL + 1):
                x, z = xi * CELL + 1, zi * CELL + 1
                hh = top
                if roof == "gable_x":
                    hh = top + max(0, hz - abs(z - cz)) * 0.9
                elif roof == "gable_z":
                    hh = top + max(0, hx - abs(x - cx)) * 0.9
                elif roof == "spire":
                    dd = min(hx - abs(x - cx), hz - abs(z - cz))
                    hh = top + max(0, dd) * 2.6
                elif roof == "cone":
                    rr = math.hypot(x - cx, z - cz)
                    if rr > max(hx, hz) + 0.5:
                        continue
                    hh = top + max(0, max(hx, hz) - rr) * 1.6
                setc(zi, xi, hh, fill, mk + 1)
        if label:
            labels.append((label, cx, cz, top + (max(hx, hz) * 2.6 if roof == "spire" else 0), mk + 1))
    labels += [("Water-gate canal", 350, 191, -13, 0), ("Quay (feet -12)", 332, 120, -12, 0), ("Forecourt", 60, 150, 0, 0), ("Hall Garth", 185, 140, 0, 0)]
    W, H = 2200, 1500
    img = Image.new("RGB", (W, H), (246, 244, 238))
    d = ImageDraw.Draw(img)
    ox, oy = W / 2 + 20, 330
    NZ = 384 // CELL

    def scr(zc, vc, hgt):     # zc = z cell, vc = (N-1 - xi) so the gate side is nearest the viewer
        return ox + (zc - vc) * a, oy + (zc + vc) * b - hgt * k

    cells = sorted(hmap.keys(), key=lambda t: t[0] + (N - 1 - t[1]))
    idimg = Image.new("I", (W, H), 0)          # 1.3.232 (#23): which box is visible at each pixel (leader anchors)
    idd = ImageDraw.Draw(idimg)
    for (zi, xi) in cells:
        h = hmap[(zi, xi)]
        c = col[(zi, xi)]
        v = N - 1 - xi
        floor = -16
        p_top = [scr(zi, v, h), scr(zi + 1, v, h), scr(zi + 1, v + 1, h), scr(zi, v + 1, h)]
        lit = tuple(min(255, int(ch * 1.05)) for ch in c)
        left = tuple(int(ch * 0.78) for ch in c)
        right = tuple(int(ch * 0.62) for ch in c)
        d.polygon([scr(zi, v + 1, h), scr(zi + 1, v + 1, h), scr(zi + 1, v + 1, floor), scr(zi, v + 1, floor)], fill=left)
        d.polygon([scr(zi + 1, v, h), scr(zi + 1, v + 1, h), scr(zi + 1, v + 1, floor), scr(zi + 1, v, floor)], fill=right)
        d.polygon(p_top, fill=lit)
        o = own.get((zi, xi), 0)
        idd.polygon([scr(zi, v + 1, h), scr(zi + 1, v + 1, h), scr(zi + 1, v + 1, floor), scr(zi, v + 1, floor)], fill=o)
        idd.polygon([scr(zi + 1, v, h), scr(zi + 1, v + 1, h), scr(zi + 1, v + 1, floor), scr(zi + 1, v, floor)], fill=o)
        idd.polygon(p_top, fill=o)
    import numpy as np
    ids = np.array(idimg)
    f = font(16, True)
    placed = []
    for label, cx, cz, top, o in labels:
        sx, sy = scr(cz / CELL, N - 1 - cx / CELL, top)
        # 1.3.232 (#23): a box hidden behind a nearer one (the Labs behind the moved Central Tower) gets its leader moved
        # to its nearest VISIBLE pixel, so no label sits on another building's roof
        if o and not (0 <= int(sy) < H and 0 <= int(sx) < W and ids[int(sy), int(sx)] == o):
            ys, xs = np.nonzero(ids == o)
            if len(xs):
                dist2 = (xs - sx) ** 2 + (ys - sy) ** 2
                j = int(np.argmin(dist2))
                if dist2[j] > 36:          # not just the apex rounding of a spire: point at the middle of what shows
                    mx, my = xs.mean(), ys.mean()
                    j = int(np.argmin((xs - mx) ** 2 + (ys - my) ** 2))
                print(f"  massing label '{label}': anchor hidden at ({sx:.0f},{sy:.0f}) -> visible ({xs[j]},{ys[j]})")
                sx, sy = float(xs[j]), float(ys[j])
        ty = sy - 34
        while any(abs(ty - py) < 20 and abs(sx - px_) < 150 for (px_, py) in placed):
            ty -= 22
        placed.append((sx, ty))
        tw = d.textlength(label, font=f)
        d.line([(sx, sy), (sx, ty + 18)], fill=(60, 60, 60), width=1)
        d.rectangle([sx - tw / 2 - 4, ty - 2, sx + tw / 2 + 4, ty + 19], fill=(255, 255, 255), outline=(90, 90, 90))
        d.text((sx - tw / 2, ty), label, fill=(20, 20, 20), font=f)
    d.text((40, 24), "ACADEMY II — 3/4 MASSING SKETCH (6 x 6 pieces = 384 x 384, seen from the gate-side corner)", fill=(20, 20, 20), font=font(26, True))
    d.text((40, 62), "Heights in blocks over the court: central tower 60 + spire (at the crossing, ruling Q3 2026-10-07) · house towers 34 + spires · observatory 30 + cone · great hall 24 to the plate · chapel 20 · cloisters 5", fill=(60, 60, 60), font=font(15))
    d.text((40, 84), "Viewer at the gate side looking toward the lake. Back: cliff (feet 0 -> -12), quay row, lake. Left: schools, labs, observatory, library. Right: masters, Rector, junior school, chapel. Sketch only.", fill=(60, 60, 60), font=font(15))
    img.save(f"{OUT}/ACADEMY-II-MASSING.png")
    print("wrote ACADEMY-II-MASSING.png", img.size)


if __name__ == "__main__":
    plan("G", L.G, "ACADEMY II — GROUND LEVEL (feet 0)", "6 x 6 pieces = 384 x 384 blocks · v2 (D-C1006-ACAD2): one central building + wings, courts between, covered walks joining all · lake row r5 = quay (feet -12)",
         "ACADEMY-II-PLAN-GROUND.png",
         ["Spiral stairs: C grand in the central tower and", "house towers' cores; B in ranges; A (narrow) on", "every secret stair. Headroom >= 2 everywhere.",
          "", "v2: one central building (Entrance Range >", "Central Tower at the crossing > Great Hall;", "Buttery + Servery = the cross arms) with wings; white", "strips = covered cloister walks joining every", "building; Walk to T3 = covered bridge (28)."])
    plan("U", L.U, "ACADEMY II — UPPER LEVEL (feet 6; towers at a dormitory floor)", "Upper floors of the ranges; the great hall and chapel rise through this level (open roof / void); central tower floor with its four arms and the stair-hall void",
         "ACADEMY-II-PLAN-UPPER.png",
         ["Mural passage (4) runs in the precinct wall", "at feet 6 (Passetto: walk above, way below).",
          "Proctors' Way (19) climbs the Entrance Range:", "lock-up (B1, Pozzi) > stair > Proctors >", "wardrobe door (18) > Council.",
          "", "Abbrev.: Vice = Rector's vice stair,", "Dbl hide = Owen double hide (11),", "Night A/B = night nurseries, Wash = washing",
          "chamber + jakes. Supper = 4 x 4 supper", "closet turret (14).", "Central tower corners: SCR = senior common", "room, Exhib. = exhibition room,", "Instr. = instrument cabinet."])
    plan("B", L.B, "ACADEMY II — BASEMENT (B1 rooms feet -7 · B2 tunnels feet -12 · sewer trench -13)", "B1 rooms are filled blocks; B2 tunnels are the narrow grey strips; sewers green; the quay is at the B2 level",
         "ACADEMY-II-PLAN-BASEMENT.png",
         ["Underground law: every building drains by gully", "/ chute to culverts at -6, then the trench at -13,", "then the outfall cascade on the quay (water law).",
          "", "B2 junction (36) under the central tower: three", "tunnels - to the gatehouse (3), the basin", "and water gate (33/34), and the crypt (37).",
          "Dry well (26, Hall Garth): tunnel to a hidden", "door on the quay; ice well (32) joins it.", "Countermine (39) twists under the gate front.", "Sewer hide (27) under Dorm Range I."])
    massing()
