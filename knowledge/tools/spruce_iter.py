#!/usr/bin/env python3
"""spruce_iter.py — LEAF PROTOCOL read-only iteration on his 15:34 CT 09-30 spruce notes: "middle layers and cap too thin from the top
view ... need a conical, downward sloping effect from the trunk - except at the cap piece - which needs to center on its top face and,
same thing, conical, downsloping, away from center ... maybe another layer of leaf blocks in the gaps right next to the trunk".
  S-A  Patrix spruce leaf as-is, on a vanilla-like spruce (a leaf ring on every layer, tiers widening downward)
  S-B  DROOP leaf: cube (E/W/up faces, as Patrix) + the 2 vertical diagonal cards + 3 cards sloping DOWN and OUTWARD (turned to face
       away from the trunk); CAP leaf on the tree top: two tiers of 4 cards sloping down away from its centre (a cone)
  S-C  S-B + his idea: one extra leaf ring hugging the trunk on every layer between tiers
Views: side (level, facing north), three-quarter from above, straight down, from below. Output _docs/leaves/pilot/SPRUCE-ITER-1.png."""
import copy, json, math, random, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
import java_leaf_study as J
import leaf_pilot_render as P
from bb_truth import truth_posed_faces
from equine_compare import bone_affines

OUT = P.OUT


def droop_model(depth_out=5, slope=32):
    """Java-coord elements: Patrix spruce cube (E/W/up) + its 2 vertical diagonal cards + 3 down-sloping cards (low end toward +x)."""
    base = J.load_java("leaves_extra2")
    els = [e for e in base["elements"] if not (e.get("rotation", {}).get("axis") == "x")]      # drop the two X-tilted cards
    for y, half in ((13.0, 13), (8.5, 12), (4.0, 11)):
        els.append({"from": [8 - half + 2, y, 8 - half], "to": [8 + half + depth_out - 2, y, 8 + half],
                    "rotation": {"angle": -slope, "axis": "z", "origin": [8, y, 8]},
                    "faces": {"up": {"uv": [0, 0, 16, 16], "texture": "#extra"}}})
    return {"elements": els}


def cap_model(slope=38):
    """cone: two tiers of 4 cards, each sloping down away from the block's vertical centre line, + the 2 vertical diagonals."""
    base = J.load_java("leaves_extra2")
    els = [e for e in base["elements"] if e.get("rotation", {}).get("axis") == "y"]
    one = []
    for y, reach in ((17.0, 9), (9.0, 13)):
        one.append({"from": [8, y, 8 - reach], "to": [8 + reach, y, 8 + reach],
                    "rotation": {"angle": -slope, "axis": "z", "origin": [8, y, 8]},
                    "faces": {"up": {"uv": [0, 0, 16, 16], "texture": "#extra"}}})
    return {"elements": els}, {"elements": one}


def low_end_dir(bones, tw):
    """unit xz vector (scene frame) from block centre to the lowest points of the sloped cards (to pick the outward quarter-turn)."""
    fs = J.block_faces(bones, tw, 16, (0, 0, 0), dimmed=False)
    pts = np.array([p for f in fs for p in f.pts]); lo = pts[pts[:, 1] <= np.percentile(pts[:, 1], 8)]
    v = lo[:, [0, 2]].mean(0); return v / (np.linalg.norm(v) + 1e-9)


def spruce_tree(extra_ring=False):
    logs = {(0, y, 0) for y in range(0, 10)}
    radii = {10: 0, 9: 1, 8: 1, 7: 2, 6: 1, 5: 2, 4: 3, 3: 2, 2: 3}   # vanilla-like: tiers widen downward, every layer rings the trunk
    leaves = set()
    for y, r in radii.items():
        for x in range(-3, 4):
            for z in range(-3, 4):
                d2 = x * x + z * z
                if (r == 0 and d2 == 0) or (r > 0 and d2 <= r * r + (0.5 if r > 1 else 1.0) and not (abs(x) == r and abs(z) == r and r > 1)):
                    if (x, y, z) not in logs: leaves.add((x, y, z))
        if extra_ring and y <= 9:
            for x, z in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                leaves.add((x, y, z))
    leaves.add((0, 11, 0))
    return logs, leaves - logs


def build(option, rng):
    sides, tops, cards, cw = P.tiles("spruce")
    atl = [P.colour(p, "spruce") for p in sides] + [P.colour(p, "spruce") for p in tops] + [P.colour(p, "spruce") for p in cards] + \
          [Image.open(P.ROOT / "textures/block/spruce_log.png").convert("RGBA")]
    ns, nt, nc = len(sides), len(tops), len(cards); N = len(atl)
    atlas = J.build_atlas(atl, P.TMP / "spruce_iter_atlas.png")
    logs, leaves = spruce_tree(extra_ring=(option == "S-C"))
    logbone = [{"name": "log", "pivot": [0, 0, 0], "cubes": [{"origin": [-8, 0, -8], "size": [16, 16, 16],
               "uv": {n: {"uv": [16 * (N - 1), 0], "uv_size": [16, 16]} for n in ("north", "south", "east", "west", "up", "down")}}]}]
    F = []
    for c in sorted(logs): F += J.block_faces(logbone, 16 * N, 16, c)
    full = J.load_java("leaves_extra2"); droop = droop_model(); cap_body, cap_card = cap_model()
    top_y = max(y for _, y, _ in leaves)
    for c in sorted(leaves):
        side = rng.randrange(ns); top = ns + rng.randrange(nt); card = ns + nt + rng.randrange(nc)
        def mk(model):
            b = J.java_to_bedrock(model, {"#all": side, "#extra": card})
            for cube in b[0]["cubes"]:
                if 0 not in cube["size"] and "up" in cube["uv"]: cube["uv"]["up"]["uv"][0] = cube["uv"]["up"]["uv"][0] % 16 + 16 * top
            return b
        if option in ("S-A", "S-D") and not (option == "S-D" and c == (0, top_y, 0)):
            b = mk(full); q = rng.randrange(4)
            F += J.block_faces(b, 16 * N, 16, c, quarter=q, dimmed=False)
            crd = [P.LF.scaled(x, 0.8) for x in b[0]["cubes"] if 0 in x["size"]]
            F += J.block_faces([{"name": "l", "pivot": [0, 0, 0], "cubes": crd}], 16 * N, 16, c, quarter=q + 1, dimmed=False)
            if option == "S-D":                                             # + 2 sloped cards facing away from the trunk
                out = np.array([c[0], c[2]], float); out = out / np.linalg.norm(out) if np.linalg.norm(out) > 1e-6 else np.array([1.0, 0.0])
                best = max(range(4), key=lambda qq: float(np.dot(_dir_cache(qq), out)))
                db = mk(droop_model()); sl = [x for x in db[0]["cubes"] if x.get("rotation") and x["rotation"][2] != 0][:2]
                F += J.block_faces([{"name": "l", "pivot": [0, 0, 0], "cubes": sl}], 16 * N, 16, c, quarter=best, dimmed=False)
            continue
        if c == (0, top_y, 0):                                            # the CAP: body + 4 quarter-turned copies of the sloped tier cards
            F += J.block_faces(mk(cap_body), 16 * N, 16, c, dimmed=False)
            for q in range(4): F += J.block_faces(mk(cap_card), 16 * N, 16, c, quarter=q, dimmed=False)
            continue
        out = np.array([c[0], c[2]], float)
        if np.linalg.norm(out) < 1e-6: out = np.array([1.0, 0.0])
        out /= np.linalg.norm(out)
        b = mk(droop)
        best = max(range(4), key=lambda q: float(np.dot(_dir_cache(q), out)))   # low end of the sloped cards points away from the trunk
        F += J.block_faces(b, 16 * N, 16, c, quarter=best, dimmed=False)
    return F, atlas, {"logs": len(logs), "leaves": len(leaves)}


_DIRS = {}
def _dir_cache(q):
    if q not in _DIRS:
        b = J.java_to_bedrock(droop_model(), {"#all": 0, "#extra": 0})
        fs = J.block_faces(b, 16, 16, (0, 0, 0), quarter=q, dimmed=False)
        pts = np.array([p for f in fs for p in f.pts]); lo = pts[pts[:, 1] <= np.percentile(pts[:, 1], 8)]
        v = lo[:, [0, 2]].mean(0); _DIRS[q] = v / (np.linalg.norm(v) + 1e-9)
    return _DIRS[q]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    W, H = 380, 380
    views = [("side, level (camera south, facing north)", (0.0, 0.05, 1.0)), ("three-quarter from above", (0.7, 0.6, 0.7)),
             ("straight down (north at top)", (0.02, 1.0, 0.02)), ("from below, looking up", (0.35, -0.9, 0.3))]
    rows, ref = [], None
    for opt, title in (("S-A", "Patrix spruce leaf as-is, vanilla-like spruce shape"),
                       ("S-B", "DROOP leaf (cards slope down + outward) + CONE cap"),
                       ("S-D", "S-A leaf + 2 outward down-sloping cards + CONE cap")):
        F, atlas, n = build(opt, random.Random(77))
        if ref is None: ref = F
        cells = []
        for vn, d in views:
            e, t = J.cam_for(ref, d, pad=1.05)
            fl = 0.0 if d[1] > -0.5 else None
            cells.append(J.label(J.render(F, atlas, e, t, W, H, floor_y=fl), f"{opt} — {title}"[:58], vn, (40, 95, 55)))
        row = Image.new("RGB", (4 * (W + 4) - 4, H), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * (W + 4), 0))
        rows.append(row); print(opt, n)
    sheet = Image.new("RGB", (rows[0].width, 3 * (H + 4) + 44), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    d.text((6, 4), "SPRUCE — ITERATION 2: his notes (too thin from the side/top; want a cone sloping down from the trunk; a centred cone cap). Same tree cells + random picks per row.", fill=(20, 20, 20), font=J.FB)
    d.text((6, 24), "Flat-lit preview (no VV light / shadows). Row S-A answers 'may fix itself in game': same Patrix leaf, but on a spruce with a leaf ring on every layer.", fill=(20, 20, 20), font=J.FR)
    for i, r in enumerate(rows): sheet.paste(r, (0, 44 + i * (H + 4)))
    sheet.save(OUT / "SPRUCE-ITER-2.png"); print(OUT / "SPRUCE-ITER-2.png")


if __name__ == "__main__":
    main()
