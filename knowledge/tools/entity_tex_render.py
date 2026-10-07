#!/usr/bin/env python3
"""entity_tex_render.py — TEXTURED player-POV render of a Bedrock ENTITY geometry (legacy 1.8.0 or 1.12+ format),
box-UV or per-face UV, bone hierarchy + rotations under the verified law (entity_render.transform), z-buffered
nearest-texel rasterizer (block_render.render), so a witness screenshot can be laid next to what the FILES draw.

Box-UV layout (Bedrock/Java skin convention, texture units of the geometry's texture_width/height, scaled to the
real image at draw time exactly as the engine does):
      row v      : [u+d .. u+d+w] = up      [u+d+w .. u+d+2w] = down
      row v+d    : [u .. u+d] = -x side (file "west")   [u+d .. u+d+w] = front (-z, "north")
                   [u+d+w .. u+2d+w] = +x side ("east")  [u+2d+w .. u+2d+2w] = back (+z, "south")
`mirror: true` swaps the two side strips and flips every face's u.

API:
  faces = load_entity_faces(geo_path, ident)              -> [Face] in FILE coordinates (16 = 1 block)
  img   = render_entity(faces, texture_png, eye, target, W, H, fov=70, world=True)
      world=True mirrors file z -> world for a mob facing SOUTH (file -z front -> world +z), same as p0_compare.to_world
"""
import json, math, re, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
from entity_render import transform
from block_render import Face, corners, Cam, DIM


def load_json(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


def _geometry(doc, ident):
    if "minecraft:geometry" in doc:
        g = next(x for x in doc["minecraft:geometry"] if x["description"]["identifier"] == ident)
        desc = g["description"]
        return g["bones"], desc.get("texture_width", 64), desc.get("texture_height", 64)
    g = doc[ident]                                           # legacy 1.8.0: top-level key
    return g["bones"], g.get("texturewidth", 64), g.get("textureheight", 32)


def box_uv(u, v, s, mirror=False):
    w, h, d = s
    strips = {"up": (u + d, v, u + d + w, v + d), "down": (u + d + w, v, u + d + 2 * w, v + d),
              "west": (u, v + d, u + d, v + d + h), "north": (u + d, v + d, u + d + w, v + d + h),
              "east": (u + d + w, v + d, u + 2 * d + w, v + d + h), "south": (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h)}
    if mirror:
        strips["west"], strips["east"] = strips["east"], strips["west"]
    out = {}
    for name, (a, b, c, e) in strips.items():
        out[name] = (c, b, a, e) if mirror else (a, b, c, e)   # flipped u when mirrored
    return out


def load_entity_faces(geo_path, ident):
    bones, tw, th = _geometry(load_json(geo_path), ident)
    by = {b["name"]: b for b in bones}
    faces = []
    for b in bones:
        chain = []; n = b["name"]; seen = set()
        while n and n in by and n not in seen:
            seen.add(n); chain.append((by[n].get("pivot", [0, 0, 0]), by[n].get("rotation", [0, 0, 0]))); n = by[n].get("parent")
        bmirror = bool(b.get("mirror", False))
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]; infl = c.get("inflate", 0) or 0
            cs = corners(o, s, infl)
            piv, rot = c.get("pivot", [0, 0, 0]), c.get("rotation", [0, 0, 0])
            uvspec = c.get("uv", [0, 0])
            mirror = bool(c.get("mirror", bmirror))
            if isinstance(uvspec, dict):
                rects = {}
                for name, f in uvspec.items():
                    u0, v0 = f["uv"]; us, vs = f.get("uv_size", [s[0], s[1]])
                    rects[name] = (u0, v0, u0 + us, v0 + vs)
            else:
                rects = box_uv(uvspec[0], uvspec[1], s, mirror)
            for name, pts in cs.items():
                if name not in rects: continue
                # zero-thickness planes: keep the two coincident faces (double-sided), drop the degenerate edges
                if infl == 0:
                    if s[0] == 0 and name not in ("east", "west"): continue
                    if s[1] == 0 and name not in ("up", "down"): continue
                    if s[2] == 0 and name not in ("north", "south"): continue
                a, bb, cc, e = rects[name]
                P = [transform(p, piv, rot) for p in pts] if any(rot) else [list(p) for p in pts]
                for bpiv, brot in chain:
                    if any(brot): P = [transform(p, bpiv, brot) for p in P]
                faces.append(Face(P, (a / tw, bb / th, cc / tw, e / th), "*", name, b["name"]))
    return faces


def to_world_faces(faces):
    out = []
    for f in faces:
        out.append(Face([[p[0], p[1], -p[2]] for p in f.pts], f.uv, f.mat, {"north": "south", "south": "north"}.get(f.name, f.name), f.bone))
    return out


def render_entity(faces, texture_png, eye, target, W=560, H=420, fov=70, bg=(214, 224, 236), floor_y=None, world=True):
    tex = np.asarray(Image.open(texture_png).convert("RGBA")).astype(np.float32) / 255.0
    th_, tw_ = tex.shape[:2]
    if world: faces = to_world_faces(faces)
    cam = Cam(eye, target, W, H, fov)
    zbuf = np.full((H, W), np.inf, np.float32)
    img = np.zeros((H, W, 3), np.float32); img[:] = np.array(bg, np.float32) / 255.0
    if floor_y is not None:   # checker floor
        for gx in range(-96, 96, 16):
            for gz in range(-96, 96, 16):
                pts = [[gx, floor_y, gz], [gx + 16, floor_y, gz], [gx + 16, floor_y, gz + 16], [gx, floor_y, gz + 16]]
                pr = [cam.project(p) for p in pts]
                if any(z <= 0.5 for _, _, z in pr): continue
                shade = 0.93 if ((gx // 16 + gz // 16) % 2 == 0) else 0.88
                _fill(img, zbuf, pr, None, None, np.array([shade, shade, shade + 0.02], np.float32), W, H)
    for f in faces:
        # winding: corners() gives TL,TR,BR,BL as seen from outside; the mirror flips nothing about geometry
        pr = [cam.project(p) for p in f.pts]
        if any(z <= 0.5 for _, _, z in pr): continue
        u0, v0, u1, v1 = f.uv
        uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        _fill(img, zbuf, pr, uvs, tex, None, W, H, dim=DIM[f.name])
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def _fill(img, zbuf, pr, uvs, tex, flat, W, H, dim=1.0):
    for tri in ((0, 1, 2), (0, 2, 3)):
        xs = np.array([pr[i][0] for i in tri]); ys = np.array([pr[i][1] for i in tri]); zs = np.array([pr[i][2] for i in tri])
        xmin, xmax = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
        ymin, ymax = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
        if xmin > xmax or ymin > ymax: continue
        X, Y = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
        det = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
        if abs(det) < 1e-9: continue
        l0 = ((xs[1] - X) * (ys[2] - Y) - (xs[2] - X) * (ys[1] - Y)) / det
        l1 = ((xs[2] - X) * (ys[0] - Y) - (xs[0] - X) * (ys[2] - Y)) / det
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
        if not inside.any(): continue
        iz = l0 / zs[0] + l1 / zs[1] + l2 / zs[2]
        z = 1.0 / iz
        sub = zbuf[ymin:ymax + 1, xmin:xmax + 1]
        if flat is not None:
            ok = inside & (z < sub)
            sub[ok] = z[ok]
            imgsub = img[ymin:ymax + 1, xmin:xmax + 1]; imgsub[ok] = flat
            continue
        us = np.array([uvs[i][0] for i in tri]); vs = np.array([uvs[i][1] for i in tri])
        u = (l0 * us[0] / zs[0] + l1 * us[1] / zs[1] + l2 * us[2] / zs[2]) * z
        v = (l0 * vs[0] / zs[0] + l1 * vs[1] / zs[1] + l2 * vs[2] / zs[2]) * z
        th_, tw_ = tex.shape[:2]
        tx = np.clip((u * tw_).astype(int), 0, tw_ - 1); ty = np.clip((v * th_).astype(int), 0, th_ - 1)
        texel = tex[ty, tx]
        ok = inside & (texel[..., 3] >= 0.5) & (z < sub)
        sub[ok] = z[ok]
        col = texel[..., :3] * dim
        imgsub = img[ymin:ymax + 1, xmin:xmax + 1]; imgsub[ok] = col[ok]


def frame_camera(faces, view, world=True, dist=None):
    """eye/target (in cubes) for a named side, backed off to fit — same conventions as p0_compare.CAMS."""
    pts = [p for f in faces for p in f.pts]
    if world: pts = [[p[0], p[1], -p[2]] for p in pts]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
    cx, cy, cz = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2
    span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    dirs = {"front": (0, 0.35, 1), "west": (-1, 0.35, 0), "east": (1, 0.35, 0), "top": (0, 1, 0.05), "back": (0, 0.35, -1),
            "front-east": (0.7, 0.35, 0.7), "front-west": (-0.7, 0.35, 0.7)}
    d = np.array(dirs[view], float); d /= np.linalg.norm(d)
    dist = dist if dist is not None else max(28.0, span * 1.35)
    eye = [cx + d[0] * dist, cy + d[1] * dist, cz + d[2] * dist]
    return eye, [cx, cy, cz]
