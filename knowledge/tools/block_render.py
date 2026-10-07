#!/usr/bin/env python3
"""block_render.py — textured player-POV render of a SHIPPED block geometry (RP-04 file + BP-02 permutation materials).

Why: a witness question ("I didn't see embers in the fire") has to be answered against what the FILES draw, from the
player's eye — not from an isometric sketch.  This is a small z-buffered rasterizer (perspective-correct, nearest-texel,
alpha_test at 0.5, Bedrock face dimming up 1.0 / n-s 0.8 / e-w 0.6 / down 0.5, `face_dimming:false` honoured) that
takes the geometry exactly as the engine reads it: cubes -> per-cube pivot/rotation -> bone pivot/rotation, under the
VERIFIED rotation law (tools/entity_render.transform / geo_preview.transform, L-ROT-DIR D-C255).

Coordinates: the geometry's own (16 units = 1 block; the cell is x,z in -8..8, y in 0..16; -z = toward the placer for
our placement_direction blocks with y_rotation_offset 180).  Camera: eye + target in the same units.

API:
  faces = load_faces(geo_path, identifier)            -> [Face] (world-space corners, uv rect, material name, face name)
  mats  = materials(bp_block_path, phase)             -> {instance: {"texture": stem, "face_dimming": bool, ...}}
  img, ids = render(faces, mats, eye, target, W, H, fov=70, tex_dir=..., frame=0, only=None)
      ids = per-pixel material-instance index (0 = background) for visibility counts
Usage (demo): block_render.py OUT.png   -> the lit hearth from 2.5 blocks in front at eye height + a low angle.
"""
import json, math, re, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
from entity_render import transform

RP04_TEX = Path("/home/claude/_build/rp04-138/textures/blocks")
TERRAIN = Path("/home/claude/_build/rp04-138/textures/terrain_texture.json")
DIM = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "east": 0.6, "west": 0.6}


def load_json(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


class Face:
    __slots__ = ("pts", "uv", "mat", "name", "bone")

    def __init__(self, pts, uv, mat, name, bone):
        self.pts, self.uv, self.mat, self.name, self.bone = pts, uv, mat, name, bone


def corners(o, s, infl):
    x0, y0, z0 = o[0] - infl, o[1] - infl, o[2] - infl
    x1, y1, z1 = o[0] + s[0] + infl, o[1] + s[1] + infl, o[2] + s[2] + infl
    # per face: 4 corners in the order TL, TR, BR, BL as seen from OUTSIDE the cube (u to the right, v down)
    return {
        "north": [[x1, y1, z0], [x0, y1, z0], [x0, y0, z0], [x1, y0, z0]],
        "south": [[x0, y1, z1], [x1, y1, z1], [x1, y0, z1], [x0, y0, z1]],
        "east": [[x1, y1, z1], [x1, y1, z0], [x1, y0, z0], [x1, y0, z1]],
        "west": [[x0, y1, z0], [x0, y1, z1], [x0, y0, z1], [x0, y0, z0]],
        "up": [[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]],
        "down": [[x0, y0, z1], [x1, y0, z1], [x1, y0, z0], [x0, y0, z0]],
    }


def load_faces(geo_path, ident):
    d = load_json(geo_path)
    g = [x for x in d["minecraft:geometry"] if x["description"]["identifier"] == ident][0]
    tw, th = g["description"].get("texture_width", 16), g["description"].get("texture_height", 16)
    by = {b["name"]: b for b in g["bones"]}
    faces = []
    for b in g["bones"]:
        chain = []
        n = b["name"]; seen = set()
        while n and n in by and n not in seen:
            seen.add(n); chain.append((by[n].get("pivot", [0, 0, 0]), by[n].get("rotation", [0, 0, 0]))); n = by[n].get("parent")
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]; infl = c.get("inflate", 0) or 0
            cs = corners(o, s, infl)
            piv, rot = c.get("pivot", [0, 0, 0]), c.get("rotation", [0, 0, 0])
            uvspec = c.get("uv", [0, 0])
            for name, pts in cs.items():
                if isinstance(uvspec, dict):
                    if name not in uvspec: continue          # omitted face
                    f = uvspec[name]; u0, v0 = f["uv"]; us, vs = f.get("uv_size", [s[0], s[1]])
                    mat = f.get("material_instance", "*")
                else:                                        # box uv (not used by our block files; approximate)
                    u0, v0 = uvspec; us, vs = s[0], s[1]; mat = "*"
                # zero-thickness quads: skip the degenerate edge faces
                if (name in ("east", "west") and s[0] == 0 and infl == 0) or (name in ("up", "down") and s[1] == 0 and infl == 0) or (name in ("north", "south") and s[2] == 0 and infl == 0):
                    continue
                P = [transform(p, piv, rot) for p in pts] if any(rot) else [list(p) for p in pts]
                for bpiv, brot in chain:
                    if any(brot): P = [transform(p, bpiv, brot) for p in P]
                faces.append(Face(P, (u0 / tw, v0 / th, (u0 + us) / tw, (v0 + vs) / th), mat, name, b["name"]))
    return faces


def materials(bp_block_path, phase=None):
    d = load_json(bp_block_path)["minecraft:block"]
    mats = dict(d["components"].get("minecraft:material_instances", {}))
    if phase is not None:
        for perm in d.get("permutations", []):
            if perm.get("condition", "") == f"q.block_state('pw:phase') == '{phase}'":
                mats = dict(perm["components"].get("minecraft:material_instances", mats))
    return mats


_texcache = {}


def texture(stem, frame=0):
    """RGBA float array of the texture behind a terrain_texture stem; flipbook strips -> the given frame (square)."""
    key = (stem, frame)
    if key in _texcache: return _texcache[key]
    tt = load_json(TERRAIN)["texture_data"]
    path = tt[stem]["textures"] if stem in tt else "textures/blocks/" + stem
    if isinstance(path, list): path = path[0]
    if isinstance(path, dict): path = path["path"]
    p = Path("/home/claude/_build/rp04-138") / (path + ".png")
    im = Image.open(p).convert("RGBA")
    if im.height > im.width and im.height % im.width == 0:      # flipbook strip
        n = im.height // im.width
        im = im.crop((0, (frame % n) * im.width, im.width, (frame % n + 1) * im.width))
    a = np.asarray(im).astype(np.float32) / 255.0
    _texcache[key] = a
    return a


class Cam:
    def __init__(self, eye, target, W, H, fov=70):
        self.eye = np.array(eye, float); t = np.array(target, float)
        f = t - self.eye; f /= np.linalg.norm(f)
        r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
        self.f, self.r, self.u, self.W, self.H = f, r, u, W, H
        # Bedrock's FOV setting is the VERTICAL fov (70 default)
        self.focal = (H / 2) / math.tan(math.radians(fov) / 2)

    def project(self, p):
        d = np.array(p, float) - self.eye; z = d @ self.f
        return (self.W / 2 + self.focal * (d @ self.r) / z, self.H / 2 - self.focal * (d @ self.u) / z, z)


def render(faces, mats, eye, target, W=960, H=540, fov=70, frame=0, only=None, bg=(24, 22, 20), shade=True):
    cam = Cam(eye, target, W, H, fov)
    zbuf = np.full((H, W), np.inf, np.float32)
    img = np.zeros((H, W, 3), np.float32); img[:] = np.array(bg, np.float32) / 255.0
    ids = np.zeros((H, W), np.int32)
    matnames = sorted({f.mat for f in faces}); matid = {m: i + 1 for i, m in enumerate(matnames)}
    for f in faces:
        if only is not None and f.mat not in only: continue
        m = mats.get(f.mat, mats.get("*", {}))
        stem = m.get("texture", "stone"); tex = texture(stem, frame); th_, tw_ = tex.shape[:2]
        dim = 1.0 if (not shade or m.get("face_dimming", True) is False) else DIM[f.name]
        pr = [cam.project(p) for p in f.pts]
        if any(z <= 0.5 for _, _, z in pr): continue
        u0, v0, u1, v1 = f.uv
        uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        for tri in ((0, 1, 2), (0, 2, 3)):
            xs = np.array([pr[i][0] for i in tri]); ys = np.array([pr[i][1] for i in tri]); zs = np.array([pr[i][2] for i in tri])
            us = np.array([uvs[i][0] for i in tri]); vs = np.array([uvs[i][1] for i in tri])
            xmin, xmax = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
            ymin, ymax = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
            if xmin > xmax or ymin > ymax: continue
            X, Y = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
            det = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
            if abs(det) < 1e-9: continue
            # barycentric weights: w0 = area(P,V1,V2)/area, w1 = area(P,V2,V0)/area, w2 = the rest
            # (checked against a big floor triangle: a mislabelled weight set silently corrupts depth + uv)
            l0 = ((xs[1] - X) * (ys[2] - Y) - (xs[2] - X) * (ys[1] - Y)) / det
            l1 = ((xs[2] - X) * (ys[0] - Y) - (xs[0] - X) * (ys[2] - Y)) / det
            l2 = 1 - l0 - l1
            inside = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
            if not inside.any(): continue
            iz = l0 / zs[0] + l1 / zs[1] + l2 / zs[2]
            z = 1.0 / iz
            u = (l0 * us[0] / zs[0] + l1 * us[1] / zs[1] + l2 * us[2] / zs[2]) * z
            v = (l0 * vs[0] / zs[0] + l1 * vs[1] / zs[1] + l2 * vs[2] / zs[2]) * z
            tx = np.clip((u * tw_).astype(int), 0, tw_ - 1); ty = np.clip((v * th_).astype(int), 0, th_ - 1)
            texel = tex[ty, tx]
            ok = inside & (texel[..., 3] >= 0.5) & (z < zbuf[ymin:ymax + 1, xmin:xmax + 1])
            sub = zbuf[ymin:ymax + 1, xmin:xmax + 1]; sub[ok] = z[ok]
            col = texel[..., :3] * dim
            imgsub = img[ymin:ymax + 1, xmin:xmax + 1]; imgsub[ok] = col[ok]
            idsub = ids[ymin:ymax + 1, xmin:xmax + 1]; idsub[ok] = matid[f.mat]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8), ids, matid


def scene_floor(y=0.0, half=64.0, stem="stone", z0=-8.0):
    """a stone floor plane at the hearth's base level in front of / around it (so the eye height reads right)."""
    pts = [[-half, y, z0 - 2 * half], [half, y, z0 - 2 * half], [half, y, half], [-half, y, half]]
    return [Face(pts, (0, 0, 8, 8), "_floor", "up", "_scene")]


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hearth.png"
    geo = "/home/claude/_build/rp04-138/models/blocks/pw_homestead.geo.json"
    bp = "/home/claude/_build/bp02-187/blocks/pw_hearth_stone.json"
    faces = load_faces(geo, "geometry.pw_hearth_lit")
    mats = materials(bp, "lit"); mats["_floor"] = {"texture": "pw_mat_stone"}
    img, ids, mid = render(faces + scene_floor(), mats, eye=(0, 26, -48), target=(0, 8, 0))
    Image.fromarray(img).save(out); print("wrote", out, mid)
