#!/usr/bin/env python3
"""civ_render.py — TRUE-GEOMETRY render of a generated CIVITAS building (his 14:13: "triple check each roof — we're not
using Minecraft's stepped roofs"; the flat review sheet drew roof blocks as cubes).

Every pw: block is drawn from its SHIPPED geometry (RP models) with its BP material instances, its permutation's
minecraft:transformation rotation and its texture from our pack stack; full vanilla cubes are drawn with our pack's
textures; small vanilla shapes (door, ladder, pane, bed, chest, barrel) as simple textured/flat boxes. Rasterizer and
rotation law: tools/block_render.py (z-buffer, alpha_test 0.5, Bedrock face dimming).
Usage: civ_render.py MANIFEST.json OUT.png"""
import io
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, "/home/claude/tools")
os.environ.setdefault("PW_STACK", "r1002i")
import block_render as BR  # noqa: E402
import stack_now as S  # noqa: E402
from entity_render import transform  # noqa: E402

BP = Path("/home/claude/_build/bp02-205/blocks")
RP_MODELS = [Path("/home/claude/_build/rp04-154/models/blocks"), Path("/home/claude/_build/rp01-116/models/blocks")]
P = S.packs()
T = S.terrain(P)
_tex = {}


def tex_by_key(key):
    if key in _tex:
        return _tex[key]
    a = None
    if key in T:
        paths = S.paths_of(T[key][1])
        for path in paths:
            p, f = S.find_image(P, path)
            if p:
                im = Image.open(io.BytesIO(p.read(f))).convert("RGBA")
                if im.height > im.width and im.height % im.width == 0:
                    im = im.crop((0, 0, im.width, im.width))
                a = np.asarray(im).astype(np.float32) / 255.0
                break
    if a is None:
        a = np.ones((2, 2, 4), np.float32) * np.array([1, 0, 1, 1], np.float32)
    _tex[key] = a
    return a


def solid(rgb):
    a = np.ones((2, 2, 4), np.float32)
    a[..., :3] = np.array(rgb, np.float32) / 255
    return a


# full vanilla cubes: (side key, top key)
VANILLA = {
    "minecraft:oak_planks": ("planks_oak", "planks_oak"), "minecraft:spruce_log": ("log_spruce", "log_top_spruce"),
    "minecraft:stone_bricks": ("stonebrick", "stonebrick"), "minecraft:cobblestone": ("cobblestone", "cobblestone"),
    "minecraft:grass_block": ("grass_side", "grass_top"), "minecraft:dirt": ("dirt", "dirt"),
    "minecraft:smooth_stone": ("stone_slab_top", "stone_slab_top"), "minecraft:stone": ("stone", "stone"),
}
VCOL = {  # vanilla blocks the sheets need, drawn as flat-coloured cubes (layout review only, not their real textures)
    "minecraft:spruce_planks": (115, 85, 52), "minecraft:hay_block": (196, 160, 40), "minecraft:smoker": (90, 80, 70),
    "minecraft:furnace": (110, 110, 110), "minecraft:blast_furnace": (95, 95, 100), "minecraft:bricks": (150, 75, 60),
    "minecraft:coarse_dirt": (110, 80, 55), "minecraft:farmland": (90, 60, 40), "minecraft:grass_path": (150, 130, 80),
    "minecraft:oak_log": (120, 95, 60), "minecraft:birch_log": (210, 205, 195), "minecraft:stonecutter_block": (130, 130, 130),
    "minecraft:composter": (120, 90, 50), "minecraft:lectern": (150, 115, 70), "minecraft:anvil": (60, 60, 64),
    "minecraft:grindstone": (140, 140, 140), "minecraft:cauldron": (55, 55, 60), "minecraft:bell": (220, 180, 40),
    "minecraft:water": (60, 90, 200), "minecraft:wall_sign": (150, 115, 70), "minecraft:spruce_door": (100, 70, 45)}
VTHIN = {"minecraft:oak_fence": (-2, 0, -2, 4, 16, 4), "minecraft:spruce_fence": (-2, 0, -2, 4, 16, 4),
         "minecraft:stone_brick_wall": (-4, 0, -4, 8, 14, 8), "minecraft:chain": (-1, 0, -1, 2, 16, 2),
         "minecraft:oak_fence_gate": (-8, 0, -1, 16, 15, 2), "minecraft:fence_gate": (-8, 0, -1, 16, 15, 2), "minecraft:wheat": (-6, 0, -6, 12, 12, 12),
         "minecraft:wall_sign": (-8, 4, 6, 16, 8, 2), "minecraft:bell": (-4, 4, -4, 8, 8, 8)}
FLAT = {"minecraft:glass_pane": (150, 200, 225), "minecraft:wooden_door": (130, 90, 55), "minecraft:ladder": (170, 130, 80),
        "minecraft:bed": (170, 40, 40), "minecraft:chest": (150, 100, 40), "minecraft:barrel": (120, 85, 50)}
THIN = {"minecraft:glass_pane": (-8, 0, -1, 16, 16, 2), "minecraft:ladder": (-8, 0, 6.5, 16, 16, 1),
        "minecraft:wooden_door": (-8, 0, -8, 16, 16, 3), "minecraft:bed": (-8, 0, -8, 16, 9, 16),
        "minecraft:chest": (-7, 0, -7, 14, 14, 14)}
_geo_cache, _blk_cache = {}, {}


def geo_faces(gid):
    if gid in _geo_cache:
        return _geo_cache[gid]
    for d in RP_MODELS:
        for f in d.glob("*.json"):
            txt = f.read_text(encoding="utf-8-sig")
            if f'"{gid}"' in txt:
                _geo_cache[gid] = BR.load_faces(f, gid)
                return _geo_cache[gid]
    _geo_cache[gid] = None
    return None


def block_def(name):
    if name in _blk_cache:
        return _blk_cache[name]
    hit = None
    for f in BP.glob("*.json"):
        if f'"{name}"' in f.read_text():
            d = BR.load_json(f)["minecraft:block"]
            if d["description"]["identifier"] == name:
                hit = d
                break
    _blk_cache[name] = hit
    return hit


def eval_cond(cond, states):
    expr = cond
    for k, v in states.items():
        val = f"'{v}'" if isinstance(v, str) else ("1" if v is True else "0" if v is False else str(v))
        expr = expr.replace(f"q.block_state('{k}')", val).replace(f"query.block_state('{k}')", val)
    expr = expr.replace("&&", " and ").replace("||", " or ").replace("!=", " != ").replace("!", " not ").replace(" not  = ", " != ")
    try:
        return bool(eval(expr, {}, {}))
    except Exception:  # noqa: BLE001
        return False


def pw_faces(name, states):
    d = block_def(name)
    if not d:
        return None, None
    comps = dict(d["components"])
    for perm in d.get("permutations", []):
        if eval_cond(perm["condition"], states):
            comps.update(perm["components"])
    gid = comps.get("minecraft:geometry")
    bvis = {}
    if isinstance(gid, dict):
        bvis = gid.get("bone_visibility", {}) or {}
        gid = gid.get("identifier")
    mats = comps.get("minecraft:material_instances", {})
    if gid in (None, "minecraft:geometry.full_block"):
        return "cube", mats
    faces = geo_faces(gid)
    if faces is None:
        return None, mats
    rot = comps.get("minecraft:transformation", {}).get("rotation", [0, 0, 0])
    out = []
    hidden = {b for b, v in bvis.items() if (v is False) or (isinstance(v, str) and not eval_cond(v, states))}
    for f in faces:
        if f.bone in hidden:                              # bone_visibility (BP geometry component), evaluated per state
            continue
        pts = [[-q[0], q[1], q[2]] for q in f.pts]        # X-mirror law: model +x renders at world -x
        if any(rot):
            pts = [xform_world(p, rot) for p in pts]      # D-C487: transformation = world RH, X then Y then Z
        out.append(BR.Face(pts, f.uv, f.mat, {"east": "west", "west": "east"}.get(f.name, f.name), f.bone))
    return out, mats


def xform_world(p, rot, pivot=(0, 8, 0)):
    """minecraft:transformation rotation, MEASURED in BDS 1.26.52 (D-C487 rotprobe): standard right-handed rotations
    in WORLD coordinates (x east, y up, z south) about the block centre, applied X first, then Y, then Z.
    (The 0.9x renderer used the file-space bone law here, which mirrored every east/west piece.)"""
    x, y, z = p[0] - pivot[0], p[1] - pivot[1], p[2] - pivot[2]
    a, b, c = (math.radians(v) for v in rot)
    y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
    x, z = x * math.cos(b) + z * math.sin(b), -x * math.sin(b) + z * math.cos(b)
    x, y = x * math.cos(c) - y * math.sin(c), x * math.sin(c) + y * math.cos(c)
    return [x + pivot[0], y + pivot[1], z + pivot[2]]


def cube_faces(o, s, mats):
    cs = BR.corners(o, s, 0)
    return [BR.Face(pts, (0, 0, 1, 1), n, n, "cube") for n, pts in cs.items()]


def scene(man, min_feet=-1, cut_feet=None):
    """world-space faces (16 units per block) + a texture per face, culling faces between two full cubes."""
    datum = man["datum_y"]
    cells = {}
    for x, y, z, name, st in man["blocks"]:
        f = y - datum
        if f < min_feet or (cut_feet is not None and f > cut_feet) or name in ("minecraft:air", "minecraft:light_block_14"):
            continue
        cells[(x, y, z)] = (name, st)
    full = {k for k, (n, _) in cells.items() if n in VANILLA}
    out = []                                           # (Face, texture array, dim_on)
    nb = {"north": (0, 0, -1), "south": (0, 0, 1), "east": (1, 0, 0), "west": (-1, 0, 0), "up": (0, 1, 0), "down": (0, -1, 0)}
    for (x, y, z), (name, st) in cells.items():
        ox, oy, oz = x * 16 + 8, y * 16, z * 16 + 8
        def shift(face):
            return BR.Face([[p[0] + ox, p[1] + oy, p[2] + oz] for p in face.pts], face.uv, face.mat, face.name, face.bone)
        if name in VANILLA:
            side, top = VANILLA[name]
            for fc in cube_faces([-8, 0, -8], [16, 16, 16], None):
                d = nb[fc.name]
                if (x + d[0], y + d[1], z + d[2]) in full:
                    continue
                out.append((shift(fc), tex_by_key(top if fc.name in ("up", "down") else side), True))
            continue
        if name in THIN:
            o = THIN[name]
            for fc in cube_faces(o[:3], o[3:], None):
                out.append((shift(fc), solid(FLAT[name]), True))
            continue
        if name in FLAT:
            for fc in cube_faces([-8, 0, -8], [16, 16, 16], None):
                out.append((shift(fc), solid(FLAT[name]), True))
            continue
        if name in VTHIN or name in VCOL:
            o = VTHIN.get(name, (-8, 0, -8, 16, 16, 16))
            col = VCOL.get(name, (120, 95, 60) if "fence" in name else (130, 130, 130))
            for fc in cube_faces(o[:3], o[3:], None):
                out.append((shift(fc), solid(col), True))
            continue
        faces, mats = pw_faces(name, st)
        if faces == "cube":
            key = (mats.get("*") or next(iter(mats.values()), {})).get("texture", "stone")
            for fc in cube_faces([-8, 0, -8], [16, 16, 16], None):
                m = mats.get(fc.name, mats.get("*", {}))
                out.append((shift(fc), tex_by_key(m.get("texture", key)), True))
            continue
        if not faces:
            for fc in cube_faces([-8, 0, -8], [16, 16, 16], None):
                out.append((shift(fc), solid((255, 0, 255)), True))
            continue
        for fc in faces:
            m = mats.get(fc.mat, mats.get("*", {}))
            out.append((shift(fc), tex_by_key(m.get("texture", "stone")), m.get("face_dimming", True)))
    return out


def render(items, eye, target, W=900, H=640, fov=55, bg=(150, 185, 220)):
    cam = BR.Cam(eye, target, W, H, fov)
    zbuf = np.full((H, W), np.inf, np.float32)
    img = np.zeros((H, W, 3), np.float32)
    img[:] = np.array(bg, np.float32) / 255
    for f, tex, dim_on in items:
        dim = BR.DIM[f.name] if dim_on else 1.0
        pr = [cam.project(p) for p in f.pts]
        if any(z <= 0.5 for _, _, z in pr):
            continue
        th_, tw_ = tex.shape[:2]
        u0, v0, u1, v1 = f.uv
        uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        for tri in ((0, 1, 2), (0, 2, 3)):
            xs = np.array([pr[i][0] for i in tri]); ys = np.array([pr[i][1] for i in tri]); zs = np.array([pr[i][2] for i in tri])
            us = np.array([uvs[i][0] for i in tri]); vs = np.array([uvs[i][1] for i in tri])
            xmin, xmax = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
            ymin, ymax = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
            if xmin > xmax or ymin > ymax:
                continue
            det = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
            if abs(det) < 1e-9:
                continue
            X, Y = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
            l0 = ((xs[1] - X) * (ys[2] - Y) - (xs[2] - X) * (ys[1] - Y)) / det
            l1 = ((xs[2] - X) * (ys[0] - Y) - (xs[0] - X) * (ys[2] - Y)) / det
            l2 = 1 - l0 - l1
            inside = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
            if not inside.any():
                continue
            z = 1.0 / (l0 / zs[0] + l1 / zs[1] + l2 / zs[2])
            u = (l0 * us[0] / zs[0] + l1 * us[1] / zs[1] + l2 * us[2] / zs[2]) * z
            v = (l0 * vs[0] / zs[0] + l1 * vs[1] / zs[1] + l2 * vs[2] / zs[2]) * z
            tx = np.clip((u * tw_).astype(int), 0, tw_ - 1); ty = np.clip((v * th_).astype(int), 0, th_ - 1)
            texel = tex[ty, tx]
            ok = inside & (texel[..., 3] >= 0.5) & (z < zbuf[ymin:ymax + 1, xmin:xmax + 1])
            zbuf[ymin:ymax + 1, xmin:xmax + 1][ok] = z[ok]
            img[ymin:ymax + 1, xmin:xmax + 1][ok] = (texel[..., :3] * dim)[ok]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def views(man_path, out):
    man = json.loads(Path(man_path).read_text())
    sx, sy, sz = man["size"]
    dy = man["datum_y"]
    cx, cz = sx * 8, sz * 8 + 8
    top = (sy - 1) * 16
    items = scene(man)
    shots = [
        ("street front, standing on the sidewalk", (-14 * 16, (dy + 1.6) * 16, cz + 9 * 16), (cx, (dy + 3) * 16, cz)),
        ("front corner, from above", (-10 * 16, top + 5 * 16, -6 * 16), (cx, (dy + 4) * 16, cz)),
        ("front gable + ridge, close", (-5 * 16, (dy + 10) * 16, cz + 2 * 16), (3 * 16, (dy + 7) * 16, cz)),
        ("back corner", ((sx + 9) * 16, top + 2 * 16, (sz + 8) * 16), (cx, (dy + 4) * 16, cz)),
    ]
    tiles = []
    for label, eye, tgt in shots:
        im = Image.fromarray(render(items, eye, tgt, W=640, H=460))
        ImageDraw.Draw(im).text((8, 6), label, fill=(0, 0, 0))
        tiles.append(im)
    sheet = Image.new("RGB", (1290, 940), (20, 20, 24))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * 650, (i // 2) * 470))
    sheet.save(out)
    return out


if __name__ == "__main__":
    print(views(sys.argv[1], sys.argv[2]))
