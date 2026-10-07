#!/usr/bin/env python3
"""leaf_fullness_iter.py — LEAF PROTOCOL read-only iteration on his 14:13 CT 09-30 idea: extend the Patrix-style cards so each
leaf block reaches just past its box and interlocks with its neighbours ("branches reaching out, splitting into more branches").
Study renders only; no pack touched. Builds on tools/java_leaf_study.py (its Java->Bedrock mapping, atlases, scene, cameras).

Options rendered (same 11-log / 59-leaf oak, same cameras):
  A  Patrix as-is: bottomless cube + 3 cards (cards reach 2.6-6 px past the faces; the Bedrock limit is 7 px = 30 px total)
  B  MAX REACH: every card scaled about its own pivot until its box touches the 30-px limit (x,z within +-15, y within -7..23)
  C  MAX REACH + a second card set turned 90 deg (6 cards): the extra diagonals fill the gaps between neighbours
  D  as C, plus the cube keeps its bottom face (6-face cube)
  E  "BARELY PAST": every card scaled so its tips end 0.1 px past the block faces (his literal wording)
Output: _docs/leaves/java_study/LEAF-FULLNESS-ITER-1.png (+ the per-option bounds in LEAF-FULLNESS-ITER-1.json)."""
import copy, json, math, random, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import java_leaf_study as J
from bb_truth import truth_posed_faces
from equine_compare import bone_affines
from block_render import Face

OUT = J.OUT; TMP = J.TMP
FB = J.FB; FR = J.FR
LIM_XZ, LIM_Y = 15.0, (-7.0, 23.0)          # Bedrock custom-block geometry bounds (Microsoft Learn 2025-06-10; 30x30x30, base-centred)


def cube_aabb(c):
    b = [{"name": "b", "pivot": [0, 0, 0], "cubes": [c]}]
    fs = truth_posed_faces(b, 16, 16, bone_affines(b)); P = np.array([p for f in fs for p in f.pts])
    return P.min(0), P.max(0)


def scaled(c, s):
    c = copy.deepcopy(c); piv = c.get("pivot", [0, 0, 0])
    c["origin"] = [round(piv[i] + (c["origin"][i] - piv[i]) * s, 4) for i in range(3)]
    c["size"] = [round(c["size"][i] * s, 4) for i in range(3)]
    return c


def fits(c):
    lo, hi = cube_aabb(c)
    return lo[0] >= -LIM_XZ and hi[0] <= LIM_XZ and lo[2] >= -LIM_XZ and hi[2] <= LIM_XZ and lo[1] >= LIM_Y[0] and hi[1] <= LIM_Y[1]


def scale_to_limit(c):
    """largest s (binary search) whose scaled card still fits the engine bounds."""
    lo, hi = 1.0, 3.0
    if not fits(scaled(c, 1.0)): return c, 1.0
    for _ in range(30):
        m = (lo + hi) / 2
        if fits(scaled(c, m)): lo = m
        else: hi = m
    return scaled(c, lo), lo


def scale_to_barely(c, past=0.1):
    """largest s whose scaled card stays within 8+past of the block faces on x/z (tips 0.1 px past the box)."""
    def ok(cc):
        lo, hi = cube_aabb(cc); r = 8 + past
        return lo[0] >= -r and hi[0] <= r and lo[2] >= -r and hi[2] <= r
    if ok(scaled(c, 1.0)):
        lo, hi = 1.0, 3.0
        for _ in range(30):
            m = (lo + hi) / 2
            if ok(scaled(c, m)): lo = m
            else: hi = m
        return scaled(c, lo), lo
    lo, hi = 0.2, 1.0
    for _ in range(30):
        m = (lo + hi) / 2
        if ok(scaled(c, m)): lo = m
        else: hi = m
    return scaled(c, lo), lo


def variant_bones(model_full, model_cards, mode):
    """returns (bones_full, bones_cards, notes) for one option; card cubes are size-0 on one axis."""
    out = []
    notes = {}
    for tag, model in (("full", model_full), ("cards", model_cards)):
        bones = J.java_to_bedrock(model, {"#all": 0, "#extra": 6})
        cubes = []
        for c in bones[0]["cubes"]:
            if 0 in c["size"]:
                if mode in ("B", "C", "D"): c, s = scale_to_limit(c); notes.setdefault(tag, []).append(round(s, 3))
                elif mode == "E": c, s = scale_to_barely(c); notes.setdefault(tag, []).append(round(s, 3))
            else:
                if mode == "D" and tag == "full":            # bottom face back on (same tile as the top)
                    c = copy.deepcopy(c); c["uv"]["down"] = dict(c["uv"]["up"])
            cubes.append(c)
        out.append([{"name": "leaves", "pivot": [0, 0, 0], "cubes": cubes}])
    return out[0], out[1], notes


def bounds(bones):
    fs = truth_posed_faces(bones, 16, 16, bone_affines(bones)); P = np.array([p for f in fs for p in f.pts])
    return [round(float(v), 2) for v in P.min(0)], [round(float(v), 2) for v in P.max(0)]


def main():
    OUT.mkdir(parents=True, exist_ok=True); TMP.mkdir(parents=True, exist_ok=True)
    PJ = J.PJ
    base = [PJ / "textures/block/oak_leaves.png"] + [PJ / f"optifine/ctm/patrix/leaves/oak/{i}.png" for i in range(2, 7)]
    extra = [PJ / f"optifine/ctm/patrix/leaves/oak/extra/{i}.png" for i in range(1, 5)]
    log = Image.open(J.RP / "textures/blocks/oak_log.png").convert("RGBA")
    atlas = J.build_atlas([J.tinted(p) for p in base] + [J.tinted(p) for p in extra] + [log], TMP / "atlas_java.png"); NJ = 11
    full = J.load_java("leaves_extra1"); cards = J.load_java("leaves_extra3")

    # the same tree as java_leaf_study (same seed -> same cells, same distance classes, same random picks per cell)
    logs = {(0, y, 0) for y in range(0, 6)} | {(1, 4, 0), (2, 5, 0), (-1, 5, 1), (0, 6, -1), (-1, 6, -1)}
    leaves = set()
    for x in range(-3, 4):
        for y in range(3, 9):
            for z in range(-3, 4):
                if (x * x) / 7.5 + ((y - 6) ** 2) / 4.2 + (z * z) / 7.5 <= 1.0 and (x, y, z) not in logs: leaves.add((x, y, z))
    N6 = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    dist = {c: 99 for c in leaves}; frontier = [c for c in leaves if any((c[0]+a, c[1]+b, c[2]+e) in logs for a, b, e in N6)]
    for c in frontier: dist[c] = 1
    k = 1
    while frontier:
        nxt = []
        for c in frontier:
            for a, b, e in N6:
                n = (c[0]+a, c[1]+b, c[2]+e)
                if n in leaves and dist[n] > k + 1: dist[n] = k + 1; nxt.append(n)
        frontier = nxt; k += 1
    random.seed(1731)
    picks = {}
    for c in sorted(leaves):
        dd = dist[c]
        use_cards = dd == 1 or (dd in (2, 3) and random.random() < 0.5)
        picks[c] = (use_cards, random.randrange(6), 6 + random.randrange(4), random.randrange(4))
    logbone = [{"name": "log", "pivot": [0, 0, 0], "cubes": [{"origin": [-8, 0, -8], "size": [16, 16, 16], "uv": {n: {"uv": [16 * (NJ - 1), 0], "uv_size": [16, 16]} for n in ("north", "south", "east", "west", "up", "down")}}]}]

    def retile(bones, face_slot, card_slot):
        bones = copy.deepcopy(bones)
        for c in bones[0]["cubes"]:
            for f in c["uv"].values():
                slot = card_slot if f["uv"][0] >= 96 else face_slot          # card faces were mapped to slot 6, cube faces to slot 0
                f["uv"] = [f["uv"][0] % 16 + 16 * slot, f["uv"][1]]
        return bones

    OPTS = [("A", "PATRIX AS-IS: bottomless cube + 3 cards (reach 2.6-6 px past the faces)"),
            ("B", "MAX REACH: the 3 cards grown to the 30-px engine limit (7 px past every face)"),
            ("C", "MAX REACH + a 2nd card set turned 90 deg = 6 cards"),
            ("D", "as C + the cube's bottom face back on"),
            ("E", "BARELY PAST: card tips end 0.1 px past the faces (his wording, literal)")]
    info = {}
    W2, H2 = 500, 420
    ref_faces = None
    rows = []
    for key, title in OPTS:
        bf, bc, notes = variant_bones(full, cards, key)
        info[key] = {"title": title, "scale": notes, "full_bounds": bounds(bf), "cards_bounds": bounds(bc),
                     "quads": {"full": sum(len(c["uv"]) for c in bf[0]["cubes"]) * (2 if key in ("C", "D") else 1) - (0 if key in ("C", "D") else 0),
                               "cards": sum(len(c["uv"]) for c in bc[0]["cubes"]) * (2 if key in ("C", "D") else 1)}}
        F = []
        for c in sorted(logs): F += J.block_faces(logbone, 16 * NJ, 16, c)
        for c in sorted(leaves):
            use_cards, fs_, cs_, q = picks[c]
            bones = retile(bc if use_cards else bf, fs_, cs_)
            F += J.block_faces(bones, 16 * NJ, 16, c, quarter=q, dimmed=False)
            if key in ("C", "D"):                                             # second card set: the cards only, turned a further 90 deg
                cards_only = [{"name": "leaves", "pivot": [0, 0, 0], "cubes": [x for x in bones[0]["cubes"] if 0 in x["size"]]}]
                F += J.block_faces(cards_only, 16 * NJ, 16, c, quarter=q + 1, dimmed=False)
        if ref_faces is None: ref_faces = F
        cells = []
        for vname, d in (("three-quarter, from above-south-east", (0.7, 0.45, 0.8)), ("standing UNDER the canopy (3 blocks out, eye height), looking up", None)):
            e, t = J.cam_for(ref_faces, d, pad=1.0) if d else ([52.0, 24.0, 44.0], [0.0, 100.0, 0.0])
            cells.append(J.label(J.render(F, atlas, e, t, W2, H2, floor_y=0.0), f"{key} — {title}", vname, (40, 95, 55) if key != "A" else (70, 70, 70)))
        row = Image.new("RGB", (2 * (W2 + 4) - 4, H2), (255, 255, 255))
        for i, c2 in enumerate(cells): row.paste(c2, (i * (W2 + 4), 0))
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, len(rows) * (H2 + 4) + 44), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    d.text((6, 4), "LEAF FULLNESS — ITERATION 1: the same small oak (11 logs, 59 leaf cells, same cameras) under five card-reach options. Flat-lit, no VV light / shadows.", fill=(20, 20, 20), font=FB)
    d.text((6, 24), "Engine limit: the whole block model must fit 30 x 30 x 30 px (7 px past each face). Row A is Patrix's own reach; B-D push to that limit; E is the literal 'barely past the box'.", fill=(20, 20, 20), font=FR)
    for i, r in enumerate(rows): sheet.paste(r, (0, 44 + i * (H2 + 4)))
    p = OUT / "LEAF-FULLNESS-ITER-1.png"; sheet.save(p); (OUT / "LEAF-FULLNESS-ITER-1.json").write_text(json.dumps(info, indent=1))
    print(p); print(json.dumps(info, indent=1))




# ---------------- ITERATION 2 (his 14:21 CT pick: C, but open the underside) ----------------
def iter2(opts=None, tag="2", headline=None):
    """C kept on the outside; three ways to open it underneath. Same tree / cameras / random picks as iteration 1.
      C    reference (6 cards on every leaf)
      C-W  no 2nd card set on the cards-only leaves beside the wood (branches stay visible)
      C-S  C-W + no 2nd set on the bottom third of each canopy column (our classifier's section 0)
      C-H  2nd card set at 60 % size everywhere (a finer twig layer instead of a second full layer)"""
    PJ = J.PJ
    base = [PJ / "textures/block/oak_leaves.png"] + [PJ / f"optifine/ctm/patrix/leaves/oak/{i}.png" for i in range(2, 7)]
    extra = [PJ / f"optifine/ctm/patrix/leaves/oak/extra/{i}.png" for i in range(1, 5)]
    log = Image.open(J.RP / "textures/blocks/oak_log.png").convert("RGBA")
    atlas = J.build_atlas([J.tinted(p) for p in base] + [J.tinted(p) for p in extra] + [log], TMP / "atlas_java.png"); NJ = 11
    full = J.load_java("leaves_extra1"); cards = J.load_java("leaves_extra3")
    bf, bc, _ = variant_bones(full, cards, "C")
    logs = {(0, y, 0) for y in range(0, 6)} | {(1, 4, 0), (2, 5, 0), (-1, 5, 1), (0, 6, -1), (-1, 6, -1)}
    leaves = set()
    for x in range(-3, 4):
        for y in range(3, 9):
            for z in range(-3, 4):
                if (x * x) / 7.5 + ((y - 6) ** 2) / 4.2 + (z * z) / 7.5 <= 1.0 and (x, y, z) not in logs: leaves.add((x, y, z))
    N6 = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    dist = {c: 99 for c in leaves}; frontier = [c for c in leaves if any((c[0]+a, c[1]+b, c[2]+e) in logs for a, b, e in N6)]
    for c in frontier: dist[c] = 1
    k = 1
    while frontier:
        nxt = []
        for c in frontier:
            for a, b, e in N6:
                n = (c[0]+a, c[1]+b, c[2]+e)
                if n in leaves and dist[n] > k + 1: dist[n] = k + 1; nxt.append(n)
        frontier = nxt; k += 1
    random.seed(1731)
    picks = {}
    for c in sorted(leaves):
        dd = dist[c]; use_cards = dd == 1 or (dd in (2, 3) and random.random() < 0.5)
        picks[c] = (use_cards, random.randrange(6), 6 + random.randrange(4), random.randrange(4))
    def section(c):                                   # BP-02 detectSectionAndExposure: column walk through leaves
        x, y, z = c; top = y; bot = y
        while (x, top + 1, z) in leaves: top += 1
        while (x, bot - 1, z) in leaves: bot -= 1
        h = top - bot + 1
        if h <= 1: return 1
        r = (y - bot) / (h - 1)
        return 0 if r < 0.34 else (1 if r < 0.67 else 2)
    logbone = [{"name": "log", "pivot": [0, 0, 0], "cubes": [{"origin": [-8, 0, -8], "size": [16, 16, 16], "uv": {n: {"uv": [16 * (NJ - 1), 0], "uv_size": [16, 16]} for n in ("north", "south", "east", "west", "up", "down")}}]}]
    def retile(bones, fs_, cs_):
        bones = copy.deepcopy(bones)
        for c in bones[0]["cubes"]:
            for f in c["uv"].values():
                slot = cs_ if f["uv"][0] >= 96 else fs_
                f["uv"] = [f["uv"][0] % 16 + 16 * slot, f["uv"][1]]
        return bones
    OPTS = opts or [("C", "reference: 6 cards on every leaf"),
            ("C-W", "no 2nd card set beside the wood"),
            ("C-S", "C-W + no 2nd set on each canopy's bottom third"),
            ("C-H", "2nd card set at 60 % size (twig layer)")]
    info = {}; W2, H2 = 500, 420; rows = []; ref = None
    for key, title in OPTS:
        F = []; n2 = 0
        for c in sorted(logs): F += J.block_faces(logbone, 16 * NJ, 16, c)
        for c in sorted(leaves):
            use_cards, fs_, cs_, q = picks[c]
            bones = retile(bc if use_cards else bf, fs_, cs_)
            F += J.block_faces(bones, 16 * NJ, 16, c, quarter=q, dimmed=False)
            second = True
            if key.startswith(("C-W", "C-S")) and use_cards: second = False
            if key == "C-S" and section(c) == 0: second = False
            if second:
                crd = [x for x in bones[0]["cubes"] if 0 in x["size"]]
                if key == "C-H" or key == "C-WH60": crd = [scaled(x, 0.6) for x in crd]
                elif key == "C-WH80": crd = [scaled(x, 0.8) for x in crd]
                F += J.block_faces([{"name": "leaves", "pivot": [0, 0, 0], "cubes": crd}], 16 * NJ, 16, c, quarter=q + 1, dimmed=False); n2 += 1
        info[key] = {"title": title, "leaves_with_2nd_set": n2, "of": len(leaves)}
        if ref is None: ref = F
        cells = []
        for vname, d in (("three-quarter, from above-south-east", (0.7, 0.45, 0.8)), ("standing UNDER the canopy (3 blocks out, eye height), looking up", None)):
            e, t = J.cam_for(ref, d, pad=1.0) if d else ([52.0, 24.0, 44.0], [0.0, 100.0, 0.0])
            cells.append(J.label(J.render(F, atlas, e, t, W2, H2, floor_y=0.0), f"{key} — {title} ({n2}/{len(leaves)} with 2nd set)", vname, (40, 95, 55)))
        row = Image.new("RGB", (2 * (W2 + 4) - 4, H2), (255, 255, 255))
        for i, c2 in enumerate(cells): row.paste(c2, (i * (W2 + 4), 0))
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, len(rows) * (H2 + 4) + 44), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    d.text((6, 4), headline or "LEAF FULLNESS — ITERATION 2: keep C's full outside, open its underside. Same oak, same cameras, same random picks as iteration 1.", fill=(20, 20, 20), font=FB)
    d.text((6, 24), "Flat-lit (no VV light / shadows): judge shape and openness only. Light through the canopy is a witness question for the in-game pilot.", fill=(20, 20, 20), font=FR)
    for i, r in enumerate(rows): sheet.paste(r, (0, 44 + i * (H2 + 4)))
    p = OUT / f"LEAF-FULLNESS-ITER-{tag}.png"; sheet.save(p); (OUT / f"LEAF-FULLNESS-ITER-{tag}.json").write_text(json.dumps(info, indent=1))
    print(p); print(info)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "iter3":
        # the reference row must come first: it fixes the shared camera
        iter2([("C-W", "his pick: no 2nd card set beside the wood"),
               ("C-H", "his pick: 2nd card set at 60 % size"),
               ("C-WH60", "COMBINED: none beside the wood + 2nd set at 60 %"),
               ("C-WH80", "COMBINED: none beside the wood + 2nd set at 80 %")], "3",
              "LEAF FULLNESS — ITERATION 3: his two picks (C-W, C-H) and their combination at two sizes. Same oak, cameras and picks.")
    elif len(sys.argv) > 1 and sys.argv[1] == "iter2": iter2()
    else: main()
