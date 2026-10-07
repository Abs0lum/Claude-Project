#!/usr/bin/env python3
"""rollout_render.py — K check for the leaf rollout (D-C345): whole trees drawn from the BUILT BP-02 1.3.196 blocks + RP-01 1.3.105
geometry and tiles, each leaf's variant chosen by a Python copy of main.js pwLeafLook (same hash, same Manhattan wood probe).
Biome-coloured tiles are multiplied by one Java foliage colour (as the game does inside one biome). Output:
_docs/leaves/rollout/ROLLOUT-BUILT-CHECK.png"""
import json, random, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import java_leaf_study as J
import leaf_pilot_render as P
import molang_lint as ML

ROOT = Path("/home/claude"); BP = ROOT / "_build/bp02-196"; RP = ROOT / "_build/rp01-105"
M32 = 0xFFFFFFFF
def imul(a, b): return (a * b) & M32
def cell_hash(x, y, z):
    h = (imul(x & M32, 73856093) ^ imul(y & M32, 19349663) ^ imul(z & M32, 83492791)) & M32
    h ^= h >> 16; h = imul(h, 2246822507); h ^= h >> 13; h = imul(h, 3266489909); h ^= h >> 16
    return h & M32
SHELLS = {d: [(a, b, c) for a in range(-3, 4) for b in range(-3, 4) for c in range(-3, 4) if abs(a) + abs(b) + abs(c) == d] for d in (1, 2, 3)}
BAND = {"jungle": 4, "acacia": 4, "spruce": 0}
def look(s, x, y, z, logs):
    h = cell_hash(x, y, z)
    if s == "spruce": return (h >> 12) % 7
    band = BAND.get(s, 3); d = 99
    for k in range(1, min(band, 3) + 1):
        if any((x + a, y + b, z + c) in logs for a, b, c in SHELLS[k]): d = k; break
    if d == 1: return 5 + h % 2
    if 2 <= d <= band and (h >> 8) & 1: return 5 + (h >> 9) % 2
    return (h >> 12) % 5

geo = {g["description"]["identifier"]: g for g in ML._parse_json((RP / "models/blocks/pw_leaves2.geo.json").read_text())["minecraft:geometry"]}
tt = ML._parse_json((RP / "textures/terrain_texture.json").read_text(encoding="utf-8-sig"))["texture_data"]

def tile(key, tint):
    im = np.asarray(Image.open(RP / (tt[key]["textures"] + ".png")).convert("RGBA")).astype(float)
    if tint is not None: im[..., :3] *= np.array(tint) / 255.0
    return Image.fromarray(im.clip(0, 255).astype(np.uint8), "RGBA").resize((16, 16), Image.NEAREST)

def species_faces(s):
    blk = ML._parse_json((BP / f"blocks/{s}_leaves.json").read_text())["minecraft:block"]
    perms = {int(p["condition"][-1]): p["components"] for p in blk["permutations"]}
    tint = P.TINT.get(s) if any("tint_method" in m for m in perms[0]["minecraft:material_instances"].values()) else None
    logs, leaves = P.tree(s, random.Random(1731 + P.SPECIES.index(s)))
    slots, tiles = {}, []
    def slot(key):
        if key not in slots: slots[key] = len(tiles); tiles.append(tile(key, tint))
        return slots[key]
    logp = P.ROOT / f"textures/block/{P.LOG.get(s, s)}_log.png"
    log_slot = len(tiles); tiles.append(Image.open(logp).convert("RGBA").resize((16, 16)))
    jobs = []; counts = {}
    for c in sorted(leaves):
        v = look(s, *c, logs); counts[v] = counts.get(v, 0) + 1
        comp = perms[v]; mats = comp["minecraft:material_instances"]
        bones = json.loads(json.dumps(geo[comp["minecraft:geometry"]]["bones"]))
        for b in bones:
            for cube in b["cubes"]:
                for f in cube["uv"].values():
                    name = f.get("material_instance", "*"); name = name if name in mats else "*"
                    f["_slot"] = slot(mats[name]["texture"])
        q = (comp.get("minecraft:transformation", {}).get("rotation", [0, 0, 0])[1] // 90) % 4
        jobs.append((bones, c, q))
    N = len(tiles); F = []
    for bones, c, q in jobs:
        for b in bones:
            for cube in b["cubes"]:
                for f in cube["uv"].values(): f["uv"] = [f["uv"][0] % 16 + 16 * f.pop("_slot"), f["uv"][1]]
        F += J.block_faces(bones, 16 * N, 16, c, quarter=q, dimmed=False)
    logbone = [{"name": "log", "pivot": [0, 0, 0], "cubes": [{"origin": [-8, 0, -8], "size": [16, 16, 16],
               "uv": {n: {"uv": [16 * log_slot, 0], "uv_size": [16, 16]} for n in ("north", "south", "east", "west", "up", "down")}}]}]
    for c in sorted(logs): F += J.block_faces(logbone, 16 * N, 16, c)
    atlas = J.build_atlas(tiles, J.TMP / f"rollout_{s}.png")
    return F, atlas, counts, len(leaves)

cells = []
for s in ("oak", "birch", "spruce", "jungle", "cherry", "pale_oak", "azalea", "flowering_azalea"):
    F, atlas, counts, n = species_faces(s)
    e, t = J.cam_for(F, (0.7, 0.35, 0.8), pad=1.05)
    img = J.render(F, atlas, e, t, 330, 320, floor_y=0.0)
    cards = counts.get(5, 0) + counts.get(6, 0) if s != "spruce" else 0
    cells.append(J.label(img, s.replace("_", " ").upper(), f"{n} leaves · {cards} cards-only · built files", (40, 95, 55)))
    print(s, n, dict(sorted(counts.items())))
sheet = Image.new("RGB", (4 * 334, 2 * 324 + 30), (255, 255, 255))
from PIL import ImageDraw
ImageDraw.Draw(sheet).text((6, 6), "ROLLOUT BUILT CHECK — BP-02 1.3.196 + RP-01 1.3.105, looks picked by the main.js rule (position + wood); biome tiles x one Java foliage colour", fill=(20, 20, 20), font=J.FR)
for i, c in enumerate(cells): sheet.paste(c, ((i % 4) * 334, 30 + (i // 4) * 324))
out = ROOT / "_docs/leaves/rollout/ROLLOUT-BUILT-CHECK.png"; sheet.save(out); print(out)
