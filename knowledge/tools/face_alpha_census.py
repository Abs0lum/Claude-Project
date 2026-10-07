#!/usr/bin/env python3
"""face_alpha_census.py — "missing PARTS of their textures" (his 09-28 19:20 report on FAIL parts? mobs): for every client
entity in RP-06 / RP-07 / RP-08, walk the geometry the entity actually uses and measure, per cube face, how much of the
face's UV rectangle lands on OPAQUE texels (alpha >= 0.5 — the alphatest cut) of the texture the entity actually binds.

A face whose rectangle is mostly transparent renders as a HOLE (alphatest/cutout materials) — the mob looks like it is
missing part of its skin, and you can see into the box. A rectangle that runs off the texture sheet is reported too.

Usage:  python3 tools/face_alpha_census.py [mob ...]      (no args = every entity)
Output: one line per entity with the flagged faces (bone.face opaque% area) — worst first; totals at the end.
"""
import glob, json, os, re, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
from entity_tex_render import box_uv

ROOT = Path("/home/claude")
RPS = [("RP-06", ROOT / "_build/rp06-149"), ("RP-07", ROOT / "_build/rp07-1414"), ("RP-08", ROOT / "_build/rp08-147")]
TEX_SEARCH = [ROOT / "_build/rp08-147", ROOT / "_build/rp07-1414", ROOT / "_build/rp06-149", ROOT / "_build/rp05-51",
              ROOT / "_intake/bedrock-samples/resource_pack"]          # stack order (top first); vanilla last
FLAG_OPAQUE = 0.5      # a face with less than half of its texels opaque renders mostly as a hole
MIN_AREA = 2.0         # texture units^2 — ignore sliver faces


def jl(p):
    try:
        return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))
    except Exception:
        return None


def all_geometries():
    geos = {}
    for _, rp in RPS + [("vanilla", ROOT / "_intake/bedrock-samples/resource_pack")]:
        for f in glob.glob(str(rp / "models/entity/**/*.json"), recursive=True):
            d = jl(f)
            if not d: continue
            if "minecraft:geometry" in d:
                for g in d["minecraft:geometry"]:
                    ds = g["description"]
                    geos.setdefault(ds["identifier"], (f, g.get("bones", []), ds.get("texture_width", 64), ds.get("texture_height", 64)))
            else:
                for k, v in d.items():
                    if k.startswith("geometry.") and isinstance(v, dict):
                        geos.setdefault(k.split(":")[0], (f, v.get("bones", []), v.get("texturewidth", 64), v.get("textureheight", 64)))
    return geos


def resolve_texture(stem):
    for base in TEX_SEARCH:
        for ext in (".png", ".tga", ".jpg"):
            p = base / (stem + ext)
            if p.exists(): return p
    return None


def face_rects(cube, bone_mirror):
    s = cube["size"]; uvspec = cube.get("uv", [0, 0])
    if isinstance(uvspec, dict):
        out = {}
        for name, f in uvspec.items():
            u0, v0 = f["uv"]; us, vs = f.get("uv_size", [s[0], s[1]])
            out[name] = (u0, v0, u0 + us, v0 + vs)
        return out
    return box_uv(uvspec[0], uvspec[1], s, bool(cube.get("mirror", bone_mirror)))


def opaque_fraction(alpha, rect, tw, th):
    h, w = alpha.shape
    u0, v0, u1, v1 = rect
    x0, x1 = sorted((u0 * w / tw, u1 * w / tw)); y0, y1 = sorted((v0 * h / th, v1 * h / th))
    off = x0 < -0.01 or y0 < -0.01 or x1 > w + 0.01 or y1 > h + 0.01
    xi0, xi1 = int(np.floor(max(0, x0))), int(np.ceil(min(w, x1))); yi0, yi1 = int(np.floor(max(0, y0))), int(np.ceil(min(h, y1)))
    if xi1 <= xi0 or yi1 <= yi0: return 0.0, off
    return float((alpha[yi0:yi1, xi0:xi1] >= 128).mean()), off


def census(only=None):
    geos = all_geometries(); rows = []
    for tag, rp in RPS:
        for f in sorted(glob.glob(str(rp / "entity/*.json"))):
            d = jl(f)
            if not d or "minecraft:client_entity" not in d: continue
            desc = d["minecraft:client_entity"]["description"]; ident = desc["identifier"]
            mob = ident.split(":")[-1]
            if only and mob not in only and Path(f).stem.split(".")[0] not in only: continue
            gid = (desc.get("geometry") or {}).get("default"); tstem = (desc.get("textures") or {}).get("default")
            if not gid or not tstem or gid not in geos: continue
            gf, bones, tw, th = geos[gid]
            tp = resolve_texture(tstem)
            if tp is None: rows.append((tag, ident, gid, None, [], 0)); continue
            alpha = np.asarray(Image.open(tp).convert("RGBA"))[..., 3]
            flagged = []; nfaces = 0
            for b in bones:
                for ci, c in enumerate(b.get("cubes", [])):
                    s = c["size"]
                    for name, rect in face_rects(c, b.get("mirror", False)).items():
                        # the face's geometric area (skip degenerate faces of zero-thickness planes)
                        dims = {"north": (s[0], s[1]), "south": (s[0], s[1]), "east": (s[2], s[1]), "west": (s[2], s[1]), "up": (s[0], s[2]), "down": (s[0], s[2])}[name]
                        if dims[0] * dims[1] < MIN_AREA: continue
                        nfaces += 1
                        op, off = opaque_fraction(alpha, rect, tw, th)
                        if op < FLAG_OPAQUE or off:
                            flagged.append((b["name"], ci, name, round(op * 100), round(dims[0] * dims[1], 1), "OFF-SHEET" if off else "", [round(x, 2) for x in rect]))
            rows.append((tag, ident, gid, os.path.relpath(tp, ROOT), flagged, nfaces))
    return rows


def main():
    only = set(sys.argv[1:]) or None
    rows = census(only)
    rows.sort(key=lambda r: -sum(x[4] for x in r[4]) if r[4] else 0)
    for tag, ident, gid, tp, flagged, n in rows:
        if tp is None: print(f"{tag} {ident:34s} {gid:36s} TEXTURE NOT FOUND"); continue
        if not flagged and only is None: continue
        area = sum(x[4] for x in flagged)
        print(f"{tag} {ident:34s} {gid:36s} {len(flagged):3d}/{n:3d} faces flagged, {area:7.1f} tex-units² — {tp}")
        for x in sorted(flagged, key=lambda x: -x[4])[:14]:
            print(f"      {x[0]}[{x[1]}].{x[2]:5s} opaque {x[3]:3d}%  area {x[4]:6.1f} {x[5]} uv {x[6]}")


if __name__ == "__main__":
    main()
