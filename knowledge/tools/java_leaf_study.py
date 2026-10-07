#!/usr/bin/env python3
"""java_leaf_study.py — READ-ONLY study of how the Patrix Java pack builds its leaves, and what a Bedrock conversion would look like
(his 12:22 CT 09-30 question: "unwrap how Java creates such beautiful branches and leaves and if there is ANY way to come close").
LEAF PROTOCOL: nothing here touches a shipped pack. Inputs: the Patrix 1.21.11 128x basic zip members range-read into
_intake/patrix128/leaf_pull (blockstates, models/block/leaves_extra*, textures, OptiFine CTM random tiles) + RP-01 1.3.104 (ours).
Outputs (_docs/leaves/java_study/):
  pw_leaves_java_oak.geo.json      — the Java oak model converted to Bedrock block geometry (study file: cube 5 faces + 3 single-face cards,
                                      card faces bound to a custom material instance "extra"); pw_leaves_java_oak_cards.geo.json (near a log)
  JAVA-LEAF-ONE-BLOCK.png           — one leaf block: Patrix-in-Bedrock vs ours, 3 camera angles
  JAVA-LEAF-TREE.png                — a small oak: Patrix-in-Bedrock (distance rule + random turn + random tiles) vs ours (live pools)
  STUDY-NUMBERS.json                — bounds vs the 30x30x30 limit, quad counts, texture coverage
The renderer is flat-lit (no VV light, no shadows): trusted for shape / texture reads only, never for engine semantics (L-RENDER-1)."""
import copy, json, math, random, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
from bb_truth import truth_posed_faces
from equine_compare import bone_affines
from entity_tex_render import Cam, _fill, to_world_faces
from block_render import Face, DIM

PJ = Path("/home/claude/_intake/patrix128/leaf_pull/assets/minecraft")
RP = Path("/home/claude/_build/rp01-104")
OUT = Path("/home/claude/_docs/leaves/java_study")
TMP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/java_leaf")
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
FOLIAGE = (89, 174, 48)          # vanilla Java forest foliage colour #59AE30 (Patrix's grey leaf art is multiplied by it: tintindex 0)
FOV = 50.0


# ---------- textures -> one atlas (the renderer takes one texture; the real block would use two material instances)
def tinted(p, tint=FOLIAGE):
    a = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)
    a[..., :3] *= np.array(tint, np.float32) / 255.0
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def ours_frame0(name):
    im = Image.open(RP / "textures/blocks" / (name + ".png")).convert("RGBA")
    return im.crop((0, 0, im.width, im.width)).resize((128, 128), Image.NEAREST)   # a flipbook shows one square frame at a time


def build_atlas(tiles, path):
    at = Image.new("RGBA", (128 * len(tiles), 128), (0, 0, 0, 0))
    for i, t in enumerate(tiles): at.paste(t.resize((128, 128), Image.NEAREST), (128 * i, 0))
    at.save(path); return path


# ---------- Java element -> Bedrock cube (Blockbench's Java->Bedrock-block mapping)
def jface_uv(face, name, slot):
    u1, v1, u2, v2 = face.get("uv", [0, 0, 16, 16])
    if face.get("rotation", 0) == 180: u1, v1, u2, v2 = u2, v2, u1, v1
    if name in ("up", "down"): u1, v1, u2, v2 = u2, v2, u1, v1      # Bedrock stores up/down per-face UVs flipped (Blockbench export)
    return {"uv": [round(u1 + 16 * slot, 4), round(v1, 4)], "uv_size": [round(u2 - u1, 4), round(v2 - v1, 4)]}


def java_to_bedrock(model, slots, single_face_cards=True, mat_names=None):
    """model: Java block model dict (elements); slots: {"#all": atlas slot, "#extra": slot}. Returns Bedrock bones (one bone)."""
    cubes = []
    for el in model["elements"]:
        fr, to = el["from"], el["to"]
        size = [round(to[i] - fr[i], 4) for i in range(3)]
        cube = {"origin": [round(8 - to[0], 4), fr[1], round(fr[2] - 8, 4)], "size": size}
        r = el.get("rotation")
        if r and r.get("angle", 0):
            ox, oy, oz = r["origin"]; a = r["angle"]
            cube["pivot"] = [round(8 - ox, 4), oy, round(oz - 8, 4)]
            cube["rotation"] = {"x": [-a, 0, 0], "y": [0, -a, 0], "z": [0, 0, a]}[r["axis"]]
        uv = {}
        zero = [i for i in range(3) if size[i] == 0]
        for n, f in el["faces"].items():
            if zero and single_face_cards and uv: break          # SINGLE-FACE QUAD LAW: one face per zero-thickness card
            e = jface_uv(f, n, slots[f["texture"]])
            if mat_names and f["texture"] in mat_names: e["material_instance"] = mat_names[f["texture"]]
            uv[n] = e
        cube["uv"] = uv
        cubes.append(cube)
    return [{"name": "leaves", "pivot": [0, 0, 0], "cubes": cubes}]


def load_java(name):
    return json.loads((PJ / "models/block" / (name + ".json")).read_text())


# ---------- scene assembly
def block_faces(bones, tw, th, pos, quarter=0, dimmed=True):
    fs = truth_posed_faces(bones, tw, th, bone_affines(bones))
    out = []
    c, s = [(1, 0), (0, 1), (-1, 0), (0, -1)][quarter % 4]
    for f in fs:
        P = []
        for x, y, z in f.pts:                                     # quarter turn about the block's vertical centre line (file frame)
            P.append([x * c - z * s + pos[0] * 16, y + pos[1] * 16, x * s + z * c + pos[2] * 16])
        out.append(Face(P, f.uv, f.mat, f.name if dimmed else "up", f.bone))
    return out


def render(faces, atlas, eye, target, W, H, bg=(206, 222, 238), floor_y=None):
    tex = np.asarray(Image.open(atlas).convert("RGBA")).astype(np.float32) / 255.0
    faces = to_world_faces(faces); cam = Cam(eye, target, W, H, FOV)
    zbuf = np.full((H, W), np.inf, np.float32); img = np.zeros((H, W, 3), np.float32); img[:] = np.array(bg, np.float32) / 255.0
    if floor_y is not None:
        for gx in range(-128, 128, 16):
            for gz in range(-128, 128, 16):
                pr = [cam.project(p) for p in ([gx, floor_y, gz], [gx + 16, floor_y, gz], [gx + 16, floor_y, gz + 16], [gx, floor_y, gz + 16])]
                if any(z <= 0.5 for _, _, z in pr): continue
                sh = 0.62 if ((gx // 16 + gz // 16) % 2 == 0) else 0.58
                _fill(img, zbuf, pr, None, None, np.array([sh * 0.8, sh, sh * 0.7], np.float32), W, H)
    for f in faces:
        pr = [cam.project(p) for p in f.pts]
        if any(z <= 0.5 for _, _, z in pr): continue
        u0, v0, u1, v1 = f.uv
        _fill(img, zbuf, pr, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], tex, None, W, H, dim=DIM[f.name])
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def cam_for(faces, d, pad=1.2):
    P = np.array([p for f in faces for p in f.pts]) * np.array([1, 1, -1])
    lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2; r = float(np.linalg.norm(hi - lo)) / 2
    d = np.array(d, float); d /= np.linalg.norm(d)
    dist = max(20.0, r / math.sin(math.radians(FOV / 2)) * pad * 0.92)
    return list(c + d * dist), list(c)


def label(img, title, sub, col):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, img.width, 34], fill=col)
    d.text((6, 2), title, fill=(255, 255, 255), font=FB); d.text((6, 19), sub, fill=(230, 235, 240), font=FR); return img


def bounds(bones, tw, th):
    fs = truth_posed_faces(bones, tw, th, bone_affines(bones))
    P = np.array([p for f in fs for p in f.pts]); lo, hi = P.min(0), P.max(0)
    return [round(float(v), 2) for v in lo], [round(float(v), 2) for v in hi], [round(float(v), 2) for v in hi - lo]


def main():
    OUT.mkdir(parents=True, exist_ok=True); TMP.mkdir(parents=True, exist_ok=True)
    random.seed(1731)
    # atlas J: 0..5 oak face tiles (default + CTM random 2-6), 6..9 oak card tiles (CTM random 1-4), 10 oak log (ours, both scenes)
    base = [PJ / "textures/block/oak_leaves.png"] + [PJ / f"optifine/ctm/patrix/leaves/oak/{i}.png" for i in range(2, 7)]
    extra = [PJ / f"optifine/ctm/patrix/leaves/oak/extra/{i}.png" for i in range(1, 5)]
    log = Image.open(RP / "textures/blocks/oak_log.png").convert("RGBA")
    atlasJ = build_atlas([tinted(p) for p in base] + [tinted(p) for p in extra] + [log], TMP / "atlas_java.png")
    NJ = 11
    # atlas O (ours): 0..5 v1..v6 (v6 aliases v5, as shipped), 6 = log
    ours_tex = ["pw_oak_leaves_v1", "pw_oak_leaves_v2", "pw_oak_leaves_v3", "pw_oak_leaves_v4", "pw_oak_leaves_v5", "pw_oak_leaves_v5"]
    atlasO = build_atlas([ours_frame0(n) for n in ours_tex] + [log], TMP / "atlas_ours.png")
    NO = 7

    full = load_java("leaves_extra1"); cards = load_java("leaves_extra3")
    def jbones(model, b, e): return java_to_bedrock(model, {"#all": b, "#extra": e})
    # the study geometry files (real texture units 16x16, card faces on the custom material instance "extra")
    for gid, model, fname in (("geometry.pw_leaves_java_oak", full, "pw_leaves_java_oak.geo.json"),
                              ("geometry.pw_leaves_java_oak_cards", cards, "pw_leaves_java_oak_cards.geo.json")):
        bones = java_to_bedrock(model, {"#all": 0, "#extra": 0}, mat_names={"#extra": "extra"})
        doc = {"format_version": "1.21.0", "minecraft:geometry": [{"description": {"identifier": gid, "texture_width": 16, "texture_height": 16,
               "visible_bounds_width": 3, "visible_bounds_height": 3, "visible_bounds_offset": [0, 0.5, 0]}, "bones": bones}]}
        (OUT / fname).write_text(json.dumps(doc, indent=1))

    # our geometry
    geo = {g["description"]["identifier"]: g for g in ML._parse_json((RP / "models/blocks/pw_leaves_variants.geo.json").read_text())["minecraft:geometry"]}
    def obones(v):
        g = copy.deepcopy(geo[f"geometry.pw_leaves_v{v}"])
        for b in g["bones"]:
            for c in b.get("cubes", []):
                uv = c.get("uv")
                if isinstance(uv, dict):
                    for f in uv.values(): f["uv"] = [f["uv"][0] + 16 * (v - 1), f["uv"][1]]
        return g["bones"]

    nums = {}
    jb = jbones(full, 0, 6); cb = jbones(cards, 0, 6)
    nums["java_full_bounds_px"] = dict(zip(("min", "max", "size"), bounds(jb, 16 * NJ, 16)))
    nums["java_cards_bounds_px"] = dict(zip(("min", "max", "size"), bounds(cb, 16 * NJ, 16)))
    nums["bedrock_limit"] = "whole model <= 30x30x30 px, every point within +-30 of the bottom-centre origin, >= 1 px inside the base block per axis (Microsoft Learn, custom block oversized geometry, 2025-06-10)"
    nums["fits_30"] = all(s <= 30 for s in nums["java_full_bounds_px"]["size"]) and all(s <= 30 for s in nums["java_cards_bounds_px"]["size"])
    quads = lambda bones: sum(len(c["uv"]) if isinstance(c["uv"], dict) else 6 for b in bones for c in b.get("cubes", []))
    nums["quads"] = {"java cube+cards": quads(jb), "java cards only": quads(cb)}
    for v in range(1, 7): nums["quads"][f"ours v{v}"] = quads(obones(v))
    def cov(p):
        a = np.asarray(Image.open(p).convert("RGBA"))[..., 3]; return round(100 * float((a >= 128).mean()), 1)
    nums["drawn_pixels_pct"] = {"patrix oak face tiles (128px)": [cov(p) for p in base], "patrix oak card tiles (128px)": [cov(p) for p in extra],
                                "ours v1..v5 (32px frame 0)": [round(100 * float((np.asarray(ours_frame0(n))[..., 3] >= 128).mean()), 1) for n in ours_tex[:5]]}
    (OUT / "STUDY-NUMBERS.json").write_text(json.dumps(nums, indent=1)); print(json.dumps(nums, indent=1))

    # ---------- sheet 1: one block
    W, H = 330, 300
    views = [("from the north side, level", (0, 0.05, 1)), ("three-quarter, from above", (0.75, 0.6, 0.75)), ("from BELOW, looking up", (0.35, -0.8, 0.5))]
    rows = []
    jb_ref = block_faces(jb, 16 * NJ, 16, (0, 0, 0), dimmed=False)
    for title, col, faces, atlas in (
            ("PATRIX -> BEDROCK: cube + 3 cards, 8 quads", (40, 95, 55), block_faces(jb, 16 * NJ, 16, (0, 0, 0), dimmed=False), atlasJ),
            ("PATRIX beside a log: cards only, 4 quads", (70, 90, 40), block_faces(cb, 16 * NJ, 16, (0, 0, 0), dimmed=False), atlasJ),
            ("OURS today: oak v1, 14 cubes = 84 quads, 32 px", (120, 70, 25), block_faces(obones(1), 16 * NO, 16, (0, 0, 0)), atlasO)):
        cells = []
        for vname, d in views:
            e, t = cam_for(jb_ref, d, pad=1.05)                      # the SAME camera for every row (Patrix full-block extents)
            cells.append(label(render(faces, atlas, e, t, W, H), title, vname, col))
        row = Image.new("RGB", (3 * (W + 4) - 4, H), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * (W + 4), 0))
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, len(rows) * (H + 4) + 44), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    d.text((6, 4), "ONE LEAF BLOCK — Patrix's Java model converted to Bedrock geometry (top two rows) vs our oak v1 (bottom). Flat-lit preview: shape + texture only.", fill=(20, 20, 20), font=FB)
    d.text((6, 24), "Patrix: grey art x forest foliage colour (Java tints it by biome), no side shading (shade:false). Ours: pre-coloured 32-px frame, side shading on.", fill=(20, 20, 20), font=FR)
    for i, r in enumerate(rows): sheet.paste(r, (0, 44 + i * (H + 4)))
    sheet.save(OUT / "JAVA-LEAF-ONE-BLOCK.png")

    # ---------- sheet 2: a small oak (same cells, two leaf systems)
    logs = {(0, y, 0) for y in range(0, 6)} | {(1, 4, 0), (2, 5, 0), (-1, 5, 1), (0, 6, -1), (-1, 6, -1)}
    leaves = set()
    for x in range(-3, 4):
        for y in range(3, 9):
            for z in range(-3, 4):
                if (x * x) / 7.5 + ((y - 6) ** 2) / 4.2 + (z * z) / 7.5 <= 1.0 and (x, y, z) not in logs: leaves.add((x, y, z))
    dist = {c: 99 for c in leaves}; frontier = [c for c in leaves if any((c[0] + a, c[1] + b, c[2] + e) in logs for a, b, e in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)))]
    for c in frontier: dist[c] = 1
    k = 1
    while frontier:                                               # vanilla leaf 'distance' = steps to the nearest log through leaves
        nxt = []
        for c in frontier:
            for a, b, e in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
                n = (c[0] + a, c[1] + b, c[2] + e)
                if n in leaves and dist[n] > k + 1: dist[n] = k + 1; nxt.append(n)
        frontier = nxt; k += 1
    logbone = [{"name": "log", "pivot": [0, 0, 0], "cubes": [{"origin": [-8, 0, -8], "size": [16, 16, 16], "uv": {n: {"uv": [16 * (NJ - 1), 0], "uv_size": [16, 16]} for n in ("north", "south", "east", "west", "up", "down")}}]}]
    logboneO = copy.deepcopy(logbone)
    for f in logboneO[0]["cubes"][0]["uv"].values(): f["uv"] = [16 * (NO - 1), 0]
    JF, OF = [], []
    counts = {"cards_only": 0, "cube_cards": 0}
    ys = [c[1] for c in leaves]; ylo, yhi = min(ys), max(ys)
    pools = {0: [1, 1, 2, 3], 1: [3, 4, 4], 2: [3, 5, 5, 6, 6]}
    for c in sorted(logs):
        JF += block_faces(logbone, 16 * NJ, 16, c); OF += block_faces(logboneO, 16 * NO, 16, c)
    for c in sorted(leaves):
        dd = dist[c]
        use_cards = dd == 1 or (dd in (2, 3) and random.random() < 0.5)       # Patrix multipart: d1 cards, d2-3 random 1-of-8, d4+ full
        counts["cards_only" if use_cards else "cube_cards"] += 1
        bones = jbones(cards if use_cards else full, random.randrange(6), 6 + random.randrange(4))
        JF += block_faces(bones, 16 * NJ, 16, c, quarter=random.randrange(4), dimmed=False)
        rel = (c[1] - ylo) / max(1, yhi - ylo); sec = 0 if rel < 0.34 else (1 if rel < 0.67 else 2)
        OF += block_faces(obones(random.choice(pools[sec])), 16 * NO, 16, c)
    nums["tree"] = {"logs": len(logs), "leaves": len(leaves), **counts}
    (OUT / "STUDY-NUMBERS.json").write_text(json.dumps(nums, indent=1))
    W2, H2 = 500, 420
    tviews = [("three-quarter, from above-south-east", (0.7, 0.45, 0.8)), ("standing UNDER the canopy (3 blocks out, eye height), looking up", None)]
    rows = []
    for title, col, faces, atlas in (("PATRIX-STYLE IN BEDROCK: beside the wood = cards only", (40, 95, 55), JF, atlasJ),
                                     ("OURS TODAY: shaped cube variants (live pools), 32 px", (120, 70, 25), OF, atlasO)):
        cells = []
        for vname, d in tviews:
            e, t = cam_for(JF, d, pad=1.0) if d else ([52.0, 24.0, 44.0], [0.0, 100.0, 0.0])   # same camera for both systems
            cells.append(label(render(faces, atlas, e, t, W2, H2, floor_y=0.0), title, vname, col))
        row = Image.new("RGB", (2 * (W2 + 4) - 4, H2), (255, 255, 255))
        for i, c2 in enumerate(cells): row.paste(c2, (i * (W2 + 4), 0))
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, 2 * (H2 + 4) + 44), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    d.text((6, 4), f"A SMALL OAK — same {len(logs)} logs and {len(leaves)} leaf cells, two leaf systems, same cameras. Flat-lit (no VV light / shadows).", fill=(20, 20, 20), font=FB)
    d.text((6, 24), f"Patrix rule: touching a log -> cards only; 2-3 steps from a log -> coin flip; farther -> cube + cards. Here {counts['cards_only']} cards-only, {counts['cube_cards']} cube+cards.", fill=(20, 20, 20), font=FR)
    for i, r in enumerate(rows): sheet.paste(r, (0, 44 + i * (H2 + 4)))
    sheet.save(OUT / "JAVA-LEAF-TREE.png")
    print(OUT / "JAVA-LEAF-ONE-BLOCK.png"); print(OUT / "JAVA-LEAF-TREE.png"); print(nums["tree"])


if __name__ == "__main__":
    main()
