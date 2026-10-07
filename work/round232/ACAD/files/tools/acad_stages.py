#!/usr/bin/env python3
"""acad_stages.py — round 232 #24: the Academy I -> II -> III upgrade path as data, measured on the Academy II layout.

Usage: acad_stages.py <layout dir> <out png>
Prints: each G building's stage (PROPOSAL), ground area per stage, the in-place test (a building added at a later stage
may only take ground that was OPEN at every earlier stage, and an earlier building may never be cut by a later one),
the stage at which each of the 39 secrets opens (all of its hosts standing), and draws the stage diagram.

Frame as acad2v2_layout.py: x = depth from the gate (x 0 = gate side, faces the town), z = frontage; pieces of 64.
Academy I = core pieces r1..r4 x c1..c4 (x/z 64..319); Academy II = r0..r5 x c0..c5 (0..383); Academy III (proposal A) =
two more frontage columns c-1 (z -64..-1) and c6 (z 384..447), i.e. 6 x 8 pieces = 384 x 512, the gate axis z 191.5 kept.
"""
import importlib.util
import os
import sys

from PIL import Image, ImageDraw, ImageFont

d, png = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("L", os.path.join(d, "acad2v2_layout.py"))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)

ORDER = ["AI-1", "AI-2", "AII-1", "AII-2", "AIII-1", "AIII-2"]
# PROPOSAL (ACAD-UPGRADE.md §3): which stage builds each ground-plan building of the v2 layout
STAGE = {
    # AI-1 the founding college (core only)
    "Entrance Range": "AI-1", "Central Tower": "AI-1", "GREAT HALL": "AI-1", "Buttery + Pantry": "AI-1", "Servery": "AI-1",
    "Kitchens": "AI-1", "Schools Wing": "AI-1", "Masters' Lodgings": "AI-1", "Rector's Lodge": "AI-1",
    "Laboratories": "AI-1",          # the Left Cloister runs THROUGH the Labs' ground floor (z96-99): same stage
    "SCHOLARS' COURT": "AI-1", "MASTERS' COURT": "AI-1", "HALL GARTH": "AI-1",
    "Porch Walk": "AI-1", "Gate Cloister": "AI-1", "Left Cloister (z0 side)": "AI-1", "Right Cloister (z383 side)": "AI-1",
    "Lake Cloister": "AI-1", "CLIFF": "AI-1",
    # AI-2 the completed college (core only; three buildings need a 4-6 row trim to sit inside the core, Q5)
    "Observatory Wing": "AI-2", "Library": "AI-2", "LIBRARY COURT": "AI-2", "Ice House": "AI-2",
    "Infirmary": "AI-2", "Chapel": "AI-2", "CHAPEL COURT": "AI-2",
    # AII-1 the ring
    "Gatehouse": "AII-1", "FORECOURT": "AII-1", "Stables + Stores": "AII-1", "House Tower I": "AII-1",
    "Dorm Range I": "AII-1", "House Tower II": "AII-1", "Dorm Range II": "AII-1", "House Tower III": "AII-1",
    "House Tower IV": "AII-1", "Junior School": "AII-1", "Walk to T1": "AII-1", "Walk to T2": "AII-1",
    "Walk to T3": "AII-1", "Walk to T4": "AII-1",
}
UNLABELLED = {"passage": "AI-1", "wall": "AII-1"}                 # the garth link strips (AI-1); the precinct wall (ring)
# secrets that are `_t2` features of a standing building (as in the v1 growth table, D-C1006-ACAD2 doc §6)
OVERRIDE = {13: ("AII-2", "Long Gallery + Map Room are the Schools Wing's _t2 upper floor"),
            23: ("AII-2", "Twin Stair = the tower's _t2 stair hall"),
            24: ("AII-2", "one Turning Bridge at AII-2, all at AIII-2"),
            38: ("AII-2", "catacombs dug at AII-2 (v1 table)")}
# trims proposed so the three small straddlers sit inside the core (Q5): label -> trimmed rect
TRIM = {"Observatory Wing": (220, 64, 251, 95), "Library": (256, 64, 305, 99), "Chapel": (260, 292, 303, 319)}


def stage_of(item):
    c, r, l = item
    if l in STAGE:
        return STAGE[l]
    return UNLABELLED.get(c)


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def ov(a, b):
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def area(r):
    return (r[2] - r[0] + 1) * (r[3] - r[1] + 1)


def core_part(r):
    return (max(r[0], 64), max(r[1], 64), min(r[2], 319), min(r[3], 319))


G = [(c, TRIM.get(l, r), l) for (c, r, l) in L.G]
missing = [l for (c, r, l) in G if stage_of((c, r, l)) is None]
print("buildings without a stage:", missing)

# ---- area per stage + core / ring rule
print("\n== ground area added per stage (m2, roofed buildings / courts / walks)")
for st in ORDER[:4]:
    b = sum(area(r) for (c, r, l) in G if stage_of((c, r, l)) == st and c not in ("court", "passage", "wall", "cliff"))
    co = sum(area(r) for (c, r, l) in G if stage_of((c, r, l)) == st and c == "court")
    p = sum(area(r) for (c, r, l) in G if stage_of((c, r, l)) == st and c == "passage")
    print(f"  {st:6}: buildings {b:6}  courts {co:6}  covered walks {p:5}")

print("\n== Academy I stages must lie in the core (x/z 64..319):")
bad = []
for (c, r, l) in G:
    st = stage_of((c, r, l))
    if st in ("AI-1", "AI-2") and c not in ("wall",) and l != "CLIFF":
        if not (r[0] >= 64 and r[1] >= 64 and r[2] <= 319 and r[3] <= 319):
            bad.append((l, r))
print("  outside the core:", bad or "none", "(with the Q5 trims applied)" if TRIM else "")

print("\n== in-place test: a later building may only take ground that was open at every earlier stage")
viol = []
for (c, r, l) in G:
    s = stage_of((c, r, l))
    if c in ("court", "wall", "cliff", "passage"):
        continue
    for (c2, r2, l2) in G:
        s2 = stage_of((c2, r2, l2))
        if c2 in ("court", "wall", "cliff") or l2 == l:
            continue
        if ORDER.index(s2) < ORDER.index(s) and ov(r, r2):
            viol.append(f"{l} ({s}) over {l2 or c2} ({s2})")
print("  violations:", viol or "none")
print("  straddlers (core part laid by the core piece's tier version, on ground open until then):")
for (c, r, l) in G:
    if c in ("wall", "cliff"):
        continue
    pcs = {(i, j) for i in range(r[0] // 64, r[2] // 64 + 1) for j in range(r[1] // 64, r[3] // 64 + 1)}
    core = {p for p in pcs if 1 <= p[0] <= 4 and 1 <= p[1] <= 4}
    if core and core != pcs:
        cp = core_part(r)
        blockers = [l2 for (c2, r2, l2) in G if c2 not in ("court", "wall", "cliff") and l2 != l and ov(cp, r2)
                    and ORDER.index(stage_of((c2, r2, l2))) < ORDER.index(stage_of((c, r, l)))]
        print(f"    {l:20} {stage_of((c, r, l)):6} core part {cp} in pieces {sorted('r%dc%d' % p for p in core)}; "
              f"earlier buildings in the way: {blockers or 'none'}")

# ---- secrets
print("\n== secrets: the stage at which each opens (all hosts standing)")
lv = {"G": L.G, "U": L.U, "B": L.B}


def g_host(p):
    best = None
    for (c, r, l) in G:
        if inside(p, r) and c not in ("court", "wall", "cliff", "passage"):
            best = (c, r, l) if best is None or area(r) < area(best[1]) else best
    if best is None:
        for (c, r, l) in G:
            if inside(p, r) and c in ("passage", "court", "wall", "cliff"):
                return (c, r, l)
    return best


per = {s: [] for s in ORDER}
rows = []
for n, (nm, level, mk, route) in sorted(L.SECRETS.items()):
    pts = [mk] + list(route) + list(L.B_ROUTES.get(n, []))
    sts, why = [], []
    for p in pts:
        if p[0] >= 312:                    # quay / canal / water gate (ring row r5, B2 level)
            sts.append("AII-1"); why.append("quay/canal")
            continue
        h = g_host(p)
        if h is None:
            if level == "B" or n in L.B_ROUTES:
                sts.append("AII-1"); why.append("B2 tunnel")
            elif 64 <= p[0] <= 319 and 64 <= p[1] <= 319:
                sts.append("AI-1"); why.append("open ground in the core")
            else:
                sts.append("AII-1"); why.append("open ground of the ring")
            continue
        sts.append(stage_of(h)); why.append(h[2] or h[0])
    if level == "B" and n not in (29,):    # B2 network (tunnels, junction, crypt way) opens with the ring
        if n in (34, 36, 39):
            sts.append("AII-1"); why.append("B2 network")
    st = max(sts, key=ORDER.index)
    note = ""
    if n in OVERRIDE:
        st, note = OVERRIDE[n]
    per[st].append(n)
    rows.append((n, nm, level, st, sorted(set(why)), note))
for n, nm, level, st, why, note in rows:
    print(f"  {n:>2} {nm:44} {level}  {st:6} hosts {why} {note}")
for s in ORDER:
    print(f"  {s:6}: {len(per[s]):2} secrets {per[s]}")

# ---- diagram
SC = 3
PAD = 40
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f12, f14, f18, f22 = (ImageFont.truetype(FONT, 12), ImageFont.truetype(FONT, 14), ImageFont.truetype(FB, 18),
                      ImageFont.truetype(FB, 22))
COL = {"AI-1": (214, 120, 60), "AI-2": (240, 186, 120), "AII-1": (70, 110, 180), "AII-2": (150, 90, 190),
       "AIII-1": (60, 150, 70), "AIII-2": (190, 225, 120)}
ZMIN, ZMAX = -64, 447
PW = (ZMAX - ZMIN + 1) * SC + 2 * PAD
PH = (384 + 64) * SC + 2 * PAD + 70
panels = [("ACADEMY I (4 x 4 = 256 x 256)", ("AI-1", "AI-2"), (64, 64, 319, 319)),
          ("ACADEMY II (6 x 6 = 384 x 384)", ("AI-1", "AI-2", "AII-1"), (0, 0, 383, 383)),
          ("ACADEMY III proposal A (6 x 8 = 384 x 512)", ("AI-1", "AI-2", "AII-1"), (0, -64, 383, 447))]
img = Image.new("RGB", (PW * 3, PH + 150), (252, 251, 247))
dr = ImageDraw.Draw(img)


def P(ox, x, z):
    return ox + PAD + (z - ZMIN) * SC, PAD + 60 + x * SC


for k, (title, sts, box) in enumerate(panels):
    ox = k * PW
    dr.text((ox + PAD, 14), title, fill=(20, 20, 20), font=f22)
    # town side + lake band
    a, b = P(ox, 384, ZMIN), P(ox, 447, ZMAX + 1)
    dr.rectangle([a, b], fill=(170, 205, 236))
    dr.text((a[0] + 8, a[1] + 8), "LAKE band x 384..447 (reserved, land job)", fill=(30, 70, 120), font=f14)
    dr.text((P(ox, 0, 120)[0], PAD + 38), "x 0 = gate side -> viaduct + town square", fill=(90, 50, 20), font=f14)
    # reserve (final land) outline
    a, b = P(ox, 0, -64), P(ox, 448, 448)
    dr.rectangle([a, b], outline=(200, 0, 0), width=2)
    # piece grid
    for j in range(-1, 8):
        z = j * 64
        dr.line([P(ox, 0, z), P(ox, 384, z)], fill=(200, 200, 220), width=1)
    for i in range(7):
        dr.line([P(ox, i * 64, -64), P(ox, i * 64, 448)], fill=(200, 200, 220), width=1)
    # stage box
    a, b = P(ox, box[0], box[1]), P(ox, box[2] + 1, box[3] + 1)
    dr.rectangle([a, b], outline=(30, 30, 30), width=4)
    if k == 2:
        for zc0, lab in ((-64, ["c-1 z -64..-1", "NEW QUAD:", "hall + 2 house", "towers V-VI;", "physic garden", "+ observatory"]),
                         (384, ["c6 z 384..447", "UNIVERSITY", "CHURCH +", "Senate House;", "printing house;", "boathouse"])):
            a, b = P(ox, 0, zc0), P(ox, 384, zc0 + 64)
            w = b[0] - a[0]
            for t in range(a[1], b[1], 14):
                k2 = min(w, b[1] - t)
                dr.line([(a[0], t), (a[0] + k2, t + k2)], fill=(150, 205, 150), width=1)
            dr.rectangle([a, b], outline=COL["AIII-1"], width=3)
            dr.rectangle([a[0] + 6, a[1] + 380, b[0] - 6, a[1] + 380 + 18 * len(lab) + 8], fill=(255, 255, 255))
            for i, t in enumerate(lab):
                dr.text((a[0] + 10, a[1] + 384 + i * 18), t, fill=(20, 80, 20), font=f14)
    for (c, r, l) in G:
        s = stage_of((c, r, l))
        if s not in sts or c == "cliff":
            continue
        fill = COL[s]
        if c == "court":
            fill = tuple(int(v * 0.35 + 255 * 0.65) for v in fill)
        a, b = P(ox, r[0], r[1]), P(ox, r[2] + 1, r[3] + 1)
        dr.rectangle([a, (b[0] - 1, b[1] - 1)], fill=fill, outline=(60, 60, 60))
    t = P(ox, 150, 172)
    dr.text((t[0] + 22, t[1] + 34), "TOWER", fill=(255, 255, 255), font=f14)
# legend
ly = PH + 10
lx = PAD
for s in ORDER:
    dr.rectangle([lx, ly, lx + 22, ly + 14], fill=COL[s], outline=(60, 60, 60))
    dr.text((lx + 28, ly - 1), s, fill=(20, 20, 20), font=f14)
    lx += 110
dr.text((PAD, ly + 26), "Black box = the stage's footprint; red outline = the land reserved at the first stage (Academy III proposal A: "
        "448 deep incl. the lake band x 512 frontage). Light tints = courts. Top-down: gate side at the top, lake at the bottom, z 0 at the left.",
        fill=(40, 40, 40), font=f14)
dr.text((PAD, ly + 48), "AI-2 shows Library / Observatory Wing / Chapel with the proposed 4-6 row trims (Q5). AII-2 / AIII-2 are tier "
        "versions of standing pieces (no new ground). PROPOSAL - not ruled.", fill=(40, 40, 40), font=f14)
img.save(png)
print("\nwrote", png, img.size)
