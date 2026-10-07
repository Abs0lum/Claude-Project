#!/usr/bin/env python3
"""leaf_pilot_render.py — LEAF PROTOCOL step 1 (his 15:27 CT 09-30 GO): the chosen leaf design (C-WH80) converted for ALL 11
Patrix 26.2 leaf species and shown on species-shaped trees, for his OK before anything is built. Read-only: no pack touched.

Design C-WH80 (his picks 14:21-14:32): Patrix model per species (oak family: bottomless cube + 3 cards, cards-only beside the wood;
spruce: open-sided cube + 4 cards, no distance rule) + a SECOND card set turned 90 deg at 80 % size on every leaf NOT touching wood.
Per block: random quarter-turn, random face tile (Patrix CTM list), random card tile (Patrix CTM list, birch weighted 2 1 2 1).
Distance classes follow each species' own Patrix blockstate (acacia + jungle: 2-4 coin flip, 5-7 full; others: 2-3 / 4-7).
Colour: Java tints grey art by biome (oak, jungle, acacia, dark oak, mangrove -> foliage colour; birch #80A755; spruce #619961);
cherry, azalea, flowering azalea (the _t models) and pale oak (no Java colour provider) are drawn as painted. The render bakes one
representative colour per species = the PRE-COLOURED option; the biome-tinted option looks the same inside one biome.
Output: _docs/leaves/pilot/LEAF-PILOT-TREES.png (+ -UNDER.png, + numbers json). Flat-lit (no VV light / shadows)."""
import copy, json, math, random, re, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
import java_leaf_study as J
import leaf_fullness_iter as LF

ROOT = Path("/home/claude/_intake/patrix262_basic/leaves/assets/minecraft")
OUT = Path("/home/claude/_docs/leaves/pilot")
TMP = J.TMP
J.PJ = ROOT                                         # load_java() reads the 26.2 models
N6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
TINT = {"oak": (89, 174, 48), "dark_oak": (89, 174, 48), "jungle": (48, 187, 11), "acacia": (174, 164, 42), "mangrove": (141, 177, 39),
        "birch": (128, 167, 85), "spruce": (97, 153, 97)}          # Java foliage colours (forest / jungle / savanna / swamp-ish; fixed birch + spruce)
UNTINTED = {"cherry", "azalea", "flowering_azalea", "pale_oak"}
LOG = {"azalea": "oak", "flowering_azalea": "oak"}                 # vanilla azalea trees grow oak logs
FULL_BAND = {"acacia": (5, 4), "jungle": (5, 4)}                   # (first 'full' distance, last coin-flip distance); default (4, 3)
SPECIES = ["oak", "birch", "spruce", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "azalea", "flowering_azalea"]


# ---------- Patrix tiles per species (CTM properties are the source of truth)
def tiles(species):
    props = {p.name: p for p in (ROOT / "optifine/ctm/patrix/leaves").glob("**/*.properties")}
    def listing(pfile, default_png):
        txt = pfile.read_text(); t = re.search(r"tiles=([^\n]+)", txt).group(1).split()
        w = re.search(r"weights=([^\n]+)", txt); weights = [int(x) for x in w.group(1).split()] if w else None
        out = []
        for tok in t:
            if tok == "<default>": out.append(default_png)
            elif "-" in tok:
                a, b = map(int, tok.split("-")); out += [pfile.parent / f"{i}.png" for i in range(a, b + 1)]
            else: out.append(pfile.parent / f"{tok}.png")
        return out, weights
    base_default = ROOT / f"textures/block/{species}_leaves.png"
    if species == "spruce":
        sides, _ = listing(props["spruce_leaves1.properties"], base_default)
        tops, _ = listing(props["spruce_leaves2.properties"], base_default)
    else:
        sides, _ = listing(props[f"{species}_leaves.properties"], base_default); tops = []
    cards, cw = listing(props[f"{species}_leaves_extra.properties"], ROOT / f"textures/block/extra/{species}_leaves_extra.png")
    return sides, tops, cards, cw


def colour(p, species):
    im = Image.open(p).convert("RGBA")
    return im if species in UNTINTED else J.tinted(p, TINT[species])


# ---------- species-shaped trees: (logs, leaves) cell sets
def tree(species, rng):
    logs, leaves = set(), set()
    def blob(cx, cy, cz, rx, ry, rz, keep=1.0):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            for y in range(int(cy - ry - 1), int(cy + ry + 2)):
                for z in range(int(cz - rz - 1), int(cz + rz + 2)):
                    d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2
                    if d <= 1.0 and (d < 0.75 or rng.random() < keep): leaves.add((x, y, z))
    def column(x, z, h, y0=0):
        for y in range(y0, y0 + h): logs.add((x, y, z))
    if species in ("oak", "pale_oak", "dark_oak"):
        w = 2 if species != "oak" else 1
        for dx in range(w):
            for dz in range(w): column(dx, dz, 6 if species == "oak" else 7)
        top = 6 if species == "oak" else 7
        for bx, bz in ((1, 1), (-1, 0), (0, -1), (2, 0)): logs.add((bx if species == "oak" else bx + (1 if bx > 0 else 0), top - 1, bz))
        c = 0.5 * (w - 1)
        blob(c, top, c, 3.3 if species == "oak" else 4.2, 2.2, 3.3 if species == "oak" else 4.2, 0.55)
    elif species == "birch":
        column(0, 0, 8); blob(0, 7.5, 0, 2.2, 2.6, 2.2, 0.6)
    elif species == "spruce":
        column(0, 0, 11)
        for i, r in enumerate((3.2, 2.6, 2.1, 1.6, 1.1, 0.6)):
            y = 3 + i * 1.5
            for x in range(-4, 5):
                for z in range(-4, 5):
                    if x * x + z * z <= r * r + 0.3 and (x, round(y), z) not in logs: leaves.add((x, int(round(y)), z))
        leaves.add((0, 11, 0))
    elif species == "jungle":
        column(0, 0, 11); logs |= {(1, 8, 0), (2, 9, 0), (-1, 9, 1), (0, 10, -1)}
        blob(0, 11, 0, 4.0, 2.2, 4.0, 0.5)
    elif species == "acacia":
        column(0, 0, 4); logs |= {(1, 4, 0), (2, 5, 0), (3, 6, 0), (-1, 4, 0), (-2, 5, 1)}
        blob(3, 7, 0, 3.2, 1.1, 3.2, 0.5); blob(-2, 6.4, 1, 2.2, 0.9, 2.2, 0.5)
    elif species == "mangrove":
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)): logs.add((dx, 0, dz))
        column(0, 1, 7); logs |= {(1, 6, 1), (-1, 7, 0)}
        blob(0, 8, 0, 3.4, 2.2, 3.4, 0.55)
    elif species == "cherry":
        column(0, 0, 5); logs |= {(1, 5, 0), (2, 6, 0), (-1, 5, 0), (-2, 6, 0)}
        blob(2.5, 7.2, 0, 3.0, 1.8, 3.0, 0.55); blob(-2.5, 7.0, 0, 2.8, 1.7, 2.8, 0.55)
    else:   # azalea / flowering azalea bush-tree
        column(0, 0, 3); blob(0, 3.6, 0, 2.6, 1.8, 2.6, 0.6)
    leaves -= logs
    leaves = {c for c in leaves if c[1] >= 1}
    return logs, leaves


def distances(logs, leaves):
    dist = {c: 99 for c in leaves}
    fr = [c for c in leaves if any((c[0] + a, c[1] + b, c[2] + e) in logs for a, b, e in N6)]
    for c in fr: dist[c] = 1
    k = 1
    while fr:
        nx = []
        for c in fr:
            for a, b, e in N6:
                n = (c[0] + a, c[1] + b, c[2] + e)
                if n in leaves and dist[n] > k + 1: dist[n] = k + 1; nx.append(n)
        fr = nx; k += 1
    return dist


# ---------- one species -> faces
def species_faces(species, seed=1731):
    rng = random.Random(seed + SPECIES.index(species))
    sides, tops, cards, cw = tiles(species)
    logp = ROOT / f"textures/block/{LOG.get(species, species)}_log.png"
    atl = [colour(p, species) for p in sides] + [colour(p, species) for p in tops] + [colour(p, species) for p in cards] + [Image.open(logp).convert("RGBA")]
    ns, nt, nc = len(sides), len(tops), len(cards); N = len(atl)
    atlas = J.build_atlas(atl, TMP / f"pilot_atlas_{species}.png")
    t = "_t" if species in ("cherry", "azalea", "flowering_azalea") else ""
    full = J.load_java(("leaves_extra2" if species == "spruce" else "leaves_extra1") + ("" if species == "spruce" else t))
    cards_m = None if species == "spruce" else J.load_java("leaves_extra3" + t)
    logs, leaves = tree(species, rng)
    dist = distances(logs, leaves)
    first_full, last_flip = FULL_BAND.get(species, (4, 3))
    logbone = [{"name": "log", "pivot": [0, 0, 0], "cubes": [{"origin": [-8, 0, -8], "size": [16, 16, 16],
               "uv": {n: {"uv": [16 * (N - 1), 0], "uv_size": [16, 16]} for n in ("north", "south", "east", "west", "up", "down")}}]}]
    F = []
    for c in sorted(logs): F += J.block_faces(logbone, 16 * N, 16, c)
    counts = {"cards_only": 0, "full": 0, "second_set": 0}
    for c in sorted(leaves):
        d = dist[c]
        use_cards = cards_m is not None and (d == 1 or (2 <= d <= last_flip and rng.random() < 0.5))
        side = rng.randrange(ns); top = ns + rng.randrange(nt) if nt else side
        card = ns + nt + (rng.choices(range(nc), weights=cw)[0] if cw else rng.randrange(nc))
        bones = J.java_to_bedrock(cards_m if use_cards else full, {"#all": side, "#extra": card})
        if nt:                                                        # spruce: top/bottom faces use their own tiles
            for cube in bones[0]["cubes"]:
                if 0 not in cube["size"] and "up" in cube["uv"]: cube["uv"]["up"]["uv"][0] = cube["uv"]["up"]["uv"][0] % 16 + 16 * top
        q = rng.randrange(4)
        F += J.block_faces(bones, 16 * N, 16, c, quarter=q, dimmed=False)
        counts["cards_only" if use_cards else "full"] += 1
        if d != 1:                                                     # C-WH80: second card set, 80 %, turned 90 deg, not beside the wood
            crd = [LF.scaled(x, 0.8) for x in bones[0]["cubes"] if 0 in x["size"]]
            F += J.block_faces([{"name": "leaves", "pivot": [0, 0, 0], "cubes": crd}], 16 * N, 16, c, quarter=q + 1, dimmed=False)
            counts["second_set"] += 1
    return F, atlas, {"logs": len(logs), "leaves": len(leaves), **counts, "face_tiles": ns + nt, "card_tiles": nc}


def main():
    OUT.mkdir(parents=True, exist_ok=True); TMP.mkdir(parents=True, exist_ok=True)
    W, H = 420, 400; cells, unders, info = [], [], {}
    for sp in SPECIES:
        F, atlas, n = species_faces(sp); info[sp] = n
        e, t = J.cam_for(F, (0.7, 0.35, 0.8), pad=1.05)
        img = J.render(F, atlas, e, t, W, H, floor_y=0.0)
        cells.append(J.label(img, sp.replace("_", " ").upper(), f"{n['leaves']} leaves: {n['full']} full + {n['cards_only']} cards-only beside wood · tiles {n['face_tiles']}+{n['card_tiles']}", (40, 95, 55)))
        P = np.array([p for f in F for p in f.pts]) * np.array([1, 1, -1]); lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2
        eye = [c[0] + (hi[0] - lo[0]) * 0.55 + 20, 26.0, c[2] + (hi[2] - lo[2]) * 0.45 + 20]
        unders.append(J.label(J.render(F, atlas, eye, [c[0], hi[1] * 0.8, c[2]], W, H, floor_y=0.0), sp.replace("_", " ").upper() + " — under the canopy",
                              "standing just outside the crown, eye height, looking up", (40, 95, 55)))
        print(sp, n)
    for name, imgs, title in (("LEAF-PILOT-TREES.png", cells, "LEAF PILOT — the chosen design (C-WH80) on all 11 Patrix 26.2 leaf species, species-shaped trees, three-quarter view from above"),
                              ("LEAF-PILOT-UNDER.png", unders, "LEAF PILOT — the same 11 trees seen from underneath (standing just outside each crown, looking up)")):
        cols = 4; rows = math.ceil(len(imgs) / cols)
        sheet = Image.new("RGB", (cols * (W + 4) - 4, rows * (H + 4) + 44), (255, 255, 255)); d = ImageDraw.Draw(sheet)
        d.text((6, 4), title, fill=(20, 20, 20), font=J.FB)
        d.text((6, 24), "Pre-coloured with one Java foliage colour per species (biome-tinted looks the same inside one biome). Patrix logs. Flat-lit: shape + texture only, no VV light or shadows.", fill=(20, 20, 20), font=J.FR)
        for i, im in enumerate(imgs): sheet.paste(im, ((i % cols) * (W + 4), 44 + (i // cols) * (H + 4)))
        sheet.save(OUT / name); print(OUT / name)
    (OUT / "LEAF-PILOT-NUMBERS.json").write_text(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
