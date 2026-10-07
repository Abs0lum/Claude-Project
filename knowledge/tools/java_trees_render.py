#!/usr/bin/env python3
"""java_trees_render.py — J1 renders (D-C339): Java-rule trees (tools/java_trees.py) beside a MODEL of today's BP-02 trees.

One sheet per species family (_docs/trees/j1/J1-<FAMILY>.png):
  per Java feature: a row of 6 seeds (full) + the same 6 with the leaves hidden (the branch skeleton);
  last row: today's BP-02 tree for each age (a model: Bedrock's fancy_trunk source is not public, so the legacy
  BigTree rules + BP-02's own numbers stand in; labelled MODEL on the sheet).
Orthographic view from the south-east, 30 deg up, one scale per sheet (sizes compare within a sheet), flat shading:
top 100 %, east 80 %, south 64 %; sideways logs show their end grain on the ends; ground = one grass layer.
"""
import json, math, random, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import java_trees as JT

OUT = Path("/home/claude/_docs/trees/j1"); BP2 = Path("/home/claude/_build/bp02-195/features")
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)

BARK = {"oak": (109, 85, 50), "birch": (216, 212, 200), "spruce": (62, 44, 28), "jungle": (87, 67, 42), "acacia": (103, 97, 87),
        "dark_oak": (59, 42, 23), "pale_oak": (82, 76, 72), "cherry": (59, 31, 40), "mangrove": (90, 42, 34), "poplar": (138, 125, 106)}
GRAIN = {"oak": (177, 144, 86), "birch": (200, 180, 120), "spruce": (120, 90, 55), "jungle": (170, 125, 80), "acacia": (175, 95, 55),
         "dark_oak": (95, 70, 40), "pale_oak": (230, 220, 215), "cherry": (225, 170, 160), "mangrove": (120, 55, 45), "poplar": (215, 200, 170)}
LEAF = {"oak_leaves": (89, 174, 48), "birch_leaves": (128, 167, 85), "spruce_leaves": (97, 153, 97), "jungle_leaves": (48, 187, 11),
        "acacia_leaves": (174, 164, 42), "dark_oak_leaves": (89, 174, 48), "pale_oak_leaves": (160, 166, 156), "cherry_leaves": (242, 182, 200),
        "mangrove_leaves": (141, 177, 39), "azalea_leaves": (108, 138, 47), "flowering_azalea_leaves": (190, 120, 175),
        "orange_poplar_leaves": (224, 137, 43), "red_poplar_leaves": (200, 70, 40), "yellow_poplar_leaves": (225, 190, 50)}
ROOT = (78, 52, 38); GROUND = (96, 142, 64)
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))


def jitter(p, k=0.07):
    h = (p[0] * 73856093 ^ p[1] * 19349663 ^ p[2] * 83492791) & 0xffff
    return 1.0 + k * ((h / 0xffff) * 2 - 1)


def shade(c, f): return tuple(max(0, min(255, int(v * f))) for v in c)


def iso(x, y, z, s):                                  # orthographic, camera to the south-east (+x, +z), 30 deg up
    return ((x - z) * C30 * s, -y * s + (x + z) * S30 * s)


def colour_of(cell, wood, face):
    kind = cell[0]
    if kind == "leaf": return LEAF.get(cell[1], (90, 160, 60))
    if kind == "root": return ROOT
    axis = cell[1]
    end = (face == "top" and axis == "y") or (face == "east" and axis == "x") or (face == "south" and axis == "z")
    return GRAIN[wood] if end else BARK[wood]


def draw_tree(blocks, wood, s, W, H, bare=False, ground=True):
    """blocks: {(x,y,z): cell}. Returns an RGB panel W x H with the trunk base near the bottom centre."""
    B = {p: c for p, c in blocks.items() if not (bare and c[0] == "leaf")}
    img = Image.new("RGB", (W, H), (214, 226, 238)); d = ImageDraw.Draw(img)
    if not B: return img
    xs = [p[0] for p in B]; zs = [p[2] for p in B]; ext = max(3, max(abs(v) for v in xs + zs) + 1)
    ox, oy = W / 2, H - 6 - (ext + 1) * 2 * S30 * s
    faces = []
    if ground:
        g = min(ext, 4)                                   # a small grass patch: scale reference only
        for gx in range(-g, g + 2):
            for gz in range(-g, g + 2):
                if (gx - 0.5) ** 2 + (gz - 0.5) ** 2 <= g * g + 1: faces.append((gx + gz - 2, (gx, -1, gz), "top", ("ground",)))
    for p, c in B.items():
        x, y, z = p
        for face, n in (("top", (x, y + 1, z)), ("east", (x + 1, y, z)), ("south", (x, y, z + 1))):
            if n not in B: faces.append((x + y + z, p, face, c))
    faces.sort(key=lambda f: f[0])
    for _, (x, y, z), face, c in faces:
        if face == "top": q = [(x, y + 1, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)]; f = 1.0
        elif face == "east": q = [(x + 1, y, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x + 1, y, z + 1)]; f = 0.80
        else: q = [(x, y, z + 1), (x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)]; f = 0.64
        col = GROUND if c[0] == "ground" else colour_of(c, wood, face)
        col = shade(col, f * jitter((x, y, z)))
        pts = [(ox + a, oy + b) for a, b in (iso(*v, s) for v in q)]
        d.polygon(pts, fill=col, outline=shade(col, 0.82) if s >= 7 else None)
    return img


def tree_extent(blocks):
    """(iso width, iso height) in blocks for the scale choice."""
    if not blocks: return 1, 1
    P = list(blocks); ext = max(3, max(max(abs(p[0]), abs(p[2])) for p in P) + 1)
    top = max(p[1] for p in P) + 1
    return 4 * ext * C30 + 2, top + 4 * ext * S30 + 2          # x - z and x + z each span 2 * ext


# ---------------------------------------------------------------- today's BP-02 trees: a MODEL (legacy BigTree + BP-02 numbers)
def bp02_model(feature_file, seed):
    j = json.loads(re.sub(r"//.*", "", (BP2 / feature_file).read_text()))["minecraft:tree_feature"]
    t, cn = j["fancy_trunk"], j["fancy_canopy"]; rng = random.Random(seed)
    h = t["trunk_height"]["base"] + rng.randint(0, t["trunk_height"]["variance"])
    ws = t.get("width_scale", 1.0); slope = t["branches"]["slope"] or 0.381; maf = t["branches"]["min_altitude_factor"]
    faf = t.get("foliage_altitude_factor", 0.618); tw = t.get("trunk_width", 1); R = cn["radius"]; CH = cn["height"]
    leaf = cn["leaf_block"]["name"].split(":")[1]
    th = math.floor(h * faf); B = {}
    for y in range(th + 1):
        for a in range(tw):
            for b in range(tw): B[(a, y, b)] = ("log", "y")
    coords = [((0, h - CH, 0), th)]
    for ry in range(h - CH, -1, -1):
        if ry < h * maf: continue
        shape = JT.fancy_shape(h, ry)
        if shape < 0: continue
        r = ws * shape * (rng.random() + 0.328); ang = rng.random() * 2 * math.pi
        tip = (math.floor(r * math.sin(ang) + 0.5), ry - 1, math.floor(r * math.cos(ang) + 0.5))
        bh = tip[1] - math.hypot(tip[0], tip[2]) * slope
        coords.append((tip, th if bh > th else int(bh)))
    for tip, by in coords:
        if (0, by, 0) != tip and by >= h * 0.2:
            a, b = (0, by, 0), tip; dd = [b[i] - a[i] for i in range(3)]; st = max(abs(v) for v in dd)
            for k in range(st + 1):
                p = tuple(a[i] + math.floor(0.5 + k * dd[i] / st) for i in range(3)); m = max(abs(p[0]), abs(p[2]))
                B[p] = ("log", "y" if m == 0 else ("x" if abs(p[0]) == m else "z"))
    for tip, by in coords:
        if by < h * 0.2: continue
        for yo in range(CH):
            cr = R if 0 < yo < CH - 1 else R - 1
            for dx in range(-cr, cr + 1):
                for dz in range(-cr, cr + 1):
                    if (abs(dx) + 0.5) ** 2 + (abs(dz) + 0.5) ** 2 > cr * cr: continue
                    p = (tip[0] + dx, tip[1] + yo, tip[2] + dz)
                    if p not in B and p[1] >= 0: B[p] = ("leaf", leaf)
    return B


FAMILIES = [
    ("OAK", "oak", [("oak", "OAK (small, straight)"), ("fancy_oak", "FANCY OAK")],
     [("pw_oak_young_tree_feature.json", "YOUNG"), ("pw_oak_mature_tree_feature.json", "MATURE"), ("pw_oak_old_tree_feature.json", "OLD"), ("pw_oak_elder_tree_feature_v2.json", "ELDER")]),
    ("BIRCH", "birch", [("birch", "BIRCH"), ("super_birch_bees", "TALL BIRCH")],
     [("pw_birch_young_tree_feature.json", "YOUNG"), ("pw_birch_mature_tree_feature.json", "MATURE"), ("pw_birch_old_tree_feature.json", "OLD")]),
    ("SPRUCE", "spruce", [("spruce", "SPRUCE"), ("pine", "PINE"), ("mega_spruce", "MEGA SPRUCE (2x2)"), ("mega_pine", "MEGA PINE (2x2)")],
     [("pw_spruce_young_tree_feature.json", "YOUNG"), ("pw_spruce_mature_tree_feature.json", "MATURE"), ("pw_spruce_old_tree_feature.json", "OLD"), ("pw_spruce_elder_tree_feature_v2.json", "ELDER")]),
    ("JUNGLE", "jungle", [("jungle_tree", "JUNGLE"), ("mega_jungle_tree", "MEGA JUNGLE (2x2)")],
     [("pw_jungle_young_tree_feature.json", "YOUNG"), ("pw_jungle_mature_tree_feature.json", "MATURE"), ("pw_jungle_old_tree_feature.json", "OLD"), ("pw_jungle_elder_tree_feature_v2.json", "ELDER")]),
    ("ACACIA", "acacia", [("acacia", "ACACIA (forking)")], [("acacia_tree_feature.json", "TODAY")]),
    ("DARK-OAK", "dark_oak", [("dark_oak", "DARK OAK (2x2)")], [("pw_dark_oak_elder_tree_feature_v2.json", "ELDER")]),
    ("PALE-OAK", "pale_oak", [("pale_oak", "PALE OAK (2x2)")], [("pw_pale_oak_elder_tree_feature_v2.json", "ELDER")]),
    ("CHERRY", "cherry", [("cherry", "CHERRY (arching branches)")], [("cherry_tree_feature.json", "TODAY")]),
    ("MANGROVE", "mangrove", [("mangrove", "MANGROVE (roots)"), ("tall_mangrove", "TALL MANGROVE")], [("mangrove_tree_feature.json", "TODAY")]),
    ("AZALEA", "oak", [("azalea_tree", "AZALEA (bending, oak log)")], []),
    ("POPLAR", "poplar", [("orange_poplar", "POPLAR (26.4 snapshot; orange / red / yellow share one shape)")], []),
]
SEEDS = [1, 2, 3, 4, 5, 6]


def family_sheet(fam, wood, java, bp2):
    PW, ncol = 300, 6
    rows = []                                                      # (title, [(blocks, caption)], bare)
    for feat, lab in java:
        trees = [JT.grow(feat, s) for s in SEEDS]
        cells = [(w.b, f"seed {s} · h{i['tree_height']} · {i['logs']} logs") for s, (w, i) in zip(SEEDS, trees)]
        rows.append((f"JAVA {lab} — 6 trees (full)", cells, False)); rows.append((f"JAVA {lab} — the same 6, leaves hidden (branches)", cells, True))
    if bp2:
        cells = [(bp02_model(f, 11), f"BP-02 {age}") for f, age in bp2]
        rows.append(("TODAY'S BP-02 (MODEL: Bedrock's fancy_trunk code is not public; legacy BigTree rules + BP-02's numbers)", cells, False))
        rows.append(("TODAY'S BP-02 (MODEL) — leaves hidden", cells, True))
    ew = max(tree_extent(b)[0] for _, cells, _ in rows for b, _ in cells); eh = max(tree_extent(b)[1] for _, cells, _ in rows for b, _ in cells)
    s = max(3.0, min(13.0, (PW - 8) / ew, 420 / eh))
    rh = [int(max(tree_extent(b)[1] for b, _ in cells) * s) + 30 for _, cells, _ in rows]     # each row only as tall as its tallest tree
    title_h, row_t = 46, 22
    sheet = Image.new("RGB", (ncol * (PW + 4) - 4, title_h + sum(h + row_t + 4 for h in rh)), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    d.text((8, 4), f"J1 — {fam.replace('-', ' ')}: the Java 26.3 rules ported to our tool, vs today's BP-02", fill=(20, 20, 20), font=FB)
    d.text((8, 24), f"Orthographic from the south-east, 30 deg up, same scale on this sheet ({s:.1f} px per block). Flat colours: shape only. Sideways logs show end grain.",
           fill=(60, 60, 60), font=FR)
    y = title_h
    for (title, cells, bare), PH in zip(rows, rh):
        d.rectangle([0, y, sheet.width, y + row_t - 2], fill=(40, 70, 50) if not title.startswith("TODAY") else (90, 60, 30))
        d.text((6, y + 3), title, fill=(255, 255, 255), font=FR); y += row_t
        for k, (blocks, cap) in enumerate(cells):
            im = draw_tree(blocks, wood, s, PW, PH, bare=bare)
            ImageDraw.Draw(im).text((5, 4), cap, fill=(30, 30, 30), font=FS)
            sheet.paste(im, (k * (PW + 4), y))
        y += PH + 4
    OUT.mkdir(parents=True, exist_ok=True); p = OUT / f"J1-{fam}.png"; sheet.save(p); return p, s


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for fam, wood, java, bp2 in FAMILIES:
        if only and fam not in only: continue
        p, s = family_sheet(fam, wood, java, bp2); print(p, f"{s:.1f} px/block")
