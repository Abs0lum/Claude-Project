#!/usr/bin/env python3
"""mob_normals.py — his 17:47 directive: "Make sure [MERS + normal maps are] applied to each mob correctly across all mobs."
Census (tools/mob_pbr_reach.py, PW_STACK=final): 1,754 creature textures have a MERS but NO normal, 277 have no set,
22 are shadowed (D-C460). This tool stages, for every such texture, the missing layers IN THE PACK THAT DRAWS IT:

  NO_NORMAL  -> <stem>_n.png  (Patrix LabPBR _n via #156 when the MERS inventory has one; else derived) + the set gains "normal"
  NO_SET     -> <stem>_mers.png (mers_derive material model) + <stem>_n.png + a new texture set
  SHADOWED   -> Mojang's MERS copied beside our picture + <stem>_n.png + a set (vanilla zombie villagers)
  vanilla-drawn NO_NORMAL -> Mojang's colour + Mojang's MERS copied into RP-07 + <stem>_n.png + set (H-18: one pack)

Derived normal: height = luminance, gradients taken INSIDE each cube face's UV rectangle (edges replicated, so no false
ridges across UV seams), scaled so the median tilt (tan) equals the class target calibrated on Patrix's own creature
normals at 128 px (fur / feather / skin / chitin 0.585, wet 0.639, scale 0.313, wood 0.216, metal 0.48 — measured
10-02 18:0x). Convention as the witnessed block derive (pbr_round.derive_normal): R ~ -dh/dx, G ~ -dh/dy, encoded (n+1)/2.
Skipped: Markers debug entities, the falling-tree entity textures (rebuilt in the F10 tree rewrite), item-path refs.
Output: _staging/mobnormals/<pack name>/<rel>... + _docs/mers/MOB-NORMALS-REPORT.json"""
import json
import zlib
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
os.environ.setdefault("PW_STACK", "final")
import stack_now as SN  # noqa: E402
import mers_derive as MD  # noqa: E402

REACH = ROOT / "_docs/mers/MOB-PBR-REACH-final.json"
STAGE = ROOT / "_staging/mobnormals"
VANILLA_TARGET = "RP-07 1.4.44"          # vanilla-drawn creatures get their set in RP-07 (derive_vanilla precedent)
TAN = {"fur": 0.585, "feather": 0.585, "skin": 0.585, "chitin": 0.585, "wet": 0.639, "scale": 0.313, "wood": 0.216,
       "metal": 0.48, "jelly": 0.12, "cloth": 0.35, "stone": 0.45, "eggshell": 0.2, "default": 0.45}
SKIP_ENTITIES = {"pw:marker", "ft:falling_tree"}
HP_SIGMA = 1.5          # px at 64 wide (scaled with the picture): relief keeps detail smaller than ~3 px
STRAND_LEN = 2.2        # px at 64 wide: strand length (vertical correlation) of the fur streaks
STRAND_TAN = 0.40       # median tilt of the strands alone (fur class is 0.585 overall)
K_MAX = 16.0             # 18:0x: median gain 12.5 over 1,514 pictures; 95th pct 52.8 (buffalo 102 = flat-painted hide)
EXT = (".png", ".tga", ".jpg")
# NO_SET objects that are not creatures: their material by entity
OBJECT_MATERIAL = {"minecraft:decorated_pot": "stone", "pw:seat": "wood", "pw:leaf_litter": "default",
                   "pw:hatch_lid": "wood"}


def rgba_of(p, rel):
    return np.asarray(Image.open(__import__("io").BytesIO(p.read(rel))).convert("RGBA"))


def geo_index(P):
    idx = {}
    for p in P:
        for f in sorted(p.files):
            if not (f.startswith("models/") and f.endswith(".json")):
                continue
            try:
                d = p.json(f)
            except Exception:  # noqa: BLE001
                continue
            if not isinstance(d, dict):
                continue
            for g in d.get("minecraft:geometry", []) or []:
                gid = (g.get("description") or {}).get("identifier")
                if gid and gid not in idx:
                    idx[gid] = g
            for k, g in d.items():
                if k.startswith("geometry.") and isinstance(g, dict):
                    gid, _, parent = k.partition(":")
                    if gid not in idx:
                        idx[gid] = {"description": {"identifier": gid, "texture_width": g.get("texturewidth", 64),
                                                    "texture_height": g.get("textureheight", 64)},
                                    "bones": g.get("bones") or [], "_parent": parent or None}
    for g in idx.values():
        if not g.get("bones") and g.get("_parent") in idx:
            g["bones"] = idx[g["_parent"]].get("bones") or []
    return idx


def client_geos(P):
    out = {}
    for p in P:
        for f in sorted(p.files):
            if not (f.startswith("entity/") and f.endswith(".json")):
                continue
            try:
                d = p.json(f)["minecraft:client_entity"]["description"]
            except Exception:  # noqa: BLE001
                continue
            i = d.get("identifier")
            if i and i not in out:
                out[i] = [g for g in (d.get("geometry") or {}).values() if isinstance(g, str)]
    return out


def face_rect_list(geo, size):
    """every cube face's pixel rectangle (x0, y0, x1, y1) on a texture of `size`."""
    w, h = size
    desc = geo.get("description") or {}
    tw, th = desc.get("texture_width", 64) or 64, desc.get("texture_height", 64) or 64
    sx, sy = w / tw, h / th
    rects = []
    for b in geo.get("bones") or []:
        for c in b.get("cubes") or []:
            try:
                fr = MD.face_rects(c)
            except Exception:  # noqa: BLE001
                continue
            for u0, v0, u1, v1 in fr:
                x0, x1 = max(0, int(np.floor(u0 * sx))), min(w, int(np.ceil(u1 * sx)))
                y0, y1 = max(0, int(np.floor(v0 * sy))), min(h, int(np.ceil(v1 * sy)))
                if x1 - x0 >= 1 and y1 - y0 >= 1:
                    rects.append((x0, y0, x1, y1))
    return rects


def pick_geo(size, gids, idx):
    w, h = size
    for gid in gids:
        g = idx.get(gid)
        if not g or not g.get("bones"):
            continue
        d = g.get("description") or {}
        tw, th = d.get("texture_width", 64) or 64, d.get("texture_height", 64) or 64
        if tw * h == th * w:
            return gid, g
    return None, None


def derive_normal(colour, rects, tan, fur=False, seed=0):
    a = colour.astype(float)
    hgt = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]) / 255
    if colour.shape[1] > 128:
        hgt = ndimage.gaussian_filter(hgt, colour.shape[1] / 256)
    gx, gy = np.zeros_like(hgt), np.zeros_like(hgt)
    covered = np.zeros(hgt.shape, bool)
    regions = rects or [(0, 0, hgt.shape[1], hgt.shape[0])]
    for x0, y0, x1, y1 in sorted(regions, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]), reverse=True):
        crop = hgt[y0:y1, x0:x1]
        # high-pass inside the face: painted large-scale shading (a belly fading to the back) is colour, not slope
        crop = crop - ndimage.gaussian_filter(crop, HP_SIGMA * hgt.shape[1] / 64, mode="nearest")
        if crop.shape[0] >= 2 or crop.shape[1] >= 2:
            gx[y0:y1, x0:x1] = ndimage.sobel(crop, 1, mode="nearest") / 8 if crop.shape[1] >= 2 else 0
            gy[y0:y1, x0:x1] = ndimage.sobel(crop, 0, mode="nearest") / 8 if crop.shape[0] >= 2 else 0
        covered[y0:y1, x0:x1] = True
    op = (a[..., 3] > 0) & covered
    mag = np.sqrt(gx * gx + gy * gy)
    live = op & (mag > 1e-6)
    k = tan / max(1e-6, float(np.median(mag[live]))) if live.any() else 0.0
    flat = k > K_MAX
    k = min(k, K_MAX)        # smooth (painted-flat) pictures: never amplify compression noise into fake relief
    x, y = np.where(op, -gx * k, 0), np.where(op, -gy * k, 0)
    if fur and flat:         # his N2 = b: a flat-painted hide gets fine fur strands (hair running down each face)
        rng = np.random.default_rng(seed)
        sc = max(1.0, hgt.shape[1] / 64)
        sx_, sy_ = np.zeros_like(hgt), np.zeros_like(hgt)
        for x0, y0, x1, y1 in regions:
            hh, ww = y1 - y0, x1 - x0
            if hh < 2 or ww < 2:
                continue
            st = ndimage.gaussian_filter(rng.normal(size=(hh, ww)), (STRAND_LEN * sc, 0.45 * sc), mode="wrap")
            st /= max(1e-6, st.std())
            sx_[y0:y1, x0:x1] = ndimage.sobel(st, 1, mode="nearest") / 8
            sy_[y0:y1, x0:x1] = ndimage.sobel(st, 0, mode="nearest") / 8
        smag = np.sqrt(sx_ * sx_ + sy_ * sy_)
        ks = STRAND_TAN / max(1e-6, float(np.median(smag[op]))) if op.any() else 0.0
        x, y = x + np.where(op, -sx_ * ks, 0), y + np.where(op, -sy_ * ks, 0)
    n = np.stack([x, y, np.ones_like(x)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    out = np.zeros(colour.shape, np.uint8)
    out[..., :3] = np.round((n + 1) / 2 * 255).clip(0, 255)
    out[..., 3] = 255
    return out, float(k)


def main():
    P = SN.packs()
    by_name = {p.name: p for p in P}
    vanilla = P[-1]
    reach = json.loads(REACH.read_text())
    census = {c["id"]: c for c in json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())}
    inv = {t["rel"]: t for t in json.loads(MD.INV.read_text())}
    idx, cg = geo_index(P), client_geos(P)
    todo = {}
    for r in reach["rows"]:
        if r["status"] not in ("NO_NORMAL", "NO_SET", "SHADOWED") or r["entity"] in SKIP_ENTITIES \
                or r.get("draw_pack", "").startswith("Markers"):
            continue
        if r["path"].startswith("textures/items/"):      # item-path refs (potions, fireballs): not creature skins
            continue
        t = todo.setdefault(r["path"], {"path": r["path"], "status": r["status"], "draw_pack": r["draw_pack"], "entities": []})
        t["entities"].append(r["entity"])
    if STAGE.exists():
        shutil.move(str(STAGE), str(ROOT / "_garbage" / f"mobnormals-stage-{os.getpid()}"))
    report, counts = [], Counter()
    for path, t in sorted(todo.items()):
        draw = by_name[t["draw_pack"]]
        target = VANILLA_TARGET if draw is vanilla else draw.name
        _, img_rel = SN.find_image(P, path)
        colour = rgba_of(draw, img_rel)
        ents = t["entities"]
        ent = next((e for e in ents if e in census), ents[0])
        plan = census[ent]["body_plan"] if ent in census else "object"
        mat = OBJECT_MATERIAL.get(ent) or MD.material_class(plan, ent)
        gids = [g for e in ents for g in cg.get(e, [])]
        gid, geo = pick_geo(colour.shape[1::-1], gids, idx)
        rects = face_rect_list(geo, colour.shape[1::-1]) if geo else []
        rel_noext = path
        stem = Path(path).name
        src = "derived"
        inv_t = inv.get(path)
        if inv_t and inv_t.get("patrix_n") and Path(inv_t["patrix_n"]).exists():
            normal = MD.normal_156(MD.rgba(inv_t["patrix_n"], colour.shape[1::-1]))
            src, k = "patrix_n", None
        else:
            normal, k = derive_normal(colour, rects, TAN.get(mat, 0.45), fur=(mat == "fur"),
                                      seed=zlib.crc32(path.encode()))
        out_dir = STAGE / target / Path(path).parent
        out_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(normal, "RGBA").save(out_dir / f"{stem}_n.png")
        set_rel = path + ".texture_set.json"
        if t["status"] == "NO_NORMAL" and draw is not vanilla:
            ts = draw.json(set_rel)
        elif t["status"] == "NO_SET":
            mers_t = {"file": None}
            mers = MD.MATERIALS.get(mat, MD.MATERIALS["default"])
            m = np.zeros(colour.shape, np.uint8)
            m[..., 0], m[..., 2], m[..., 3] = mers[0], np.clip(mers[2] + MD.crevice(colour), 0, 255), mers[3]
            Image.fromarray(m, "RGBA").save(out_dir / f"{stem}_mers.png")
            ts = {"format_version": "1.21.30", "minecraft:texture_set": {
                "color": stem, "metalness_emissive_roughness_subsurface": stem + "_mers"}}
            del mers_t
        else:   # SHADOWED by our plain picture, or vanilla-drawn: Mojang's MERS (and colour when vanilla draws) beside it
            vts = vanilla.json(set_rel)["minecraft:texture_set"]
            mers_name = vts.get("metalness_emissive_roughness_subsurface") or vts.get("metalness_emissive_roughness")
            vdir = path.rsplit("/", 1)[0]
            mers_rel = next(f"{vdir}/{mers_name}{e}" for e in EXT if vanilla.has(f"{vdir}/{mers_name}{e}"))
            (out_dir / Path(mers_rel).name).write_bytes(vanilla.read(mers_rel))
            if draw is vanilla:
                (out_dir / Path(img_rel).name).write_bytes(vanilla.read(img_rel))
            ts = {"format_version": "1.21.30", "minecraft:texture_set": dict(vts)}
        ts["minecraft:texture_set"]["normal"] = f"{stem}_n"
        ts["minecraft:texture_set"].pop("heightmap", None)
        ts["format_version"] = "1.21.30"
        (out_dir / f"{stem}.texture_set.json").write_text(json.dumps(ts, indent=1))
        counts[(target, t["status"], src)] += 1
        report.append({"path": path, "status": t["status"], "draw_pack": draw.name, "target_pack": target,
                       "entities": sorted(set(ents)), "material": mat, "geometry": gid, "face_rects": len(rects),
                       "normal_source": src, "k": k, "size": list(colour.shape[1::-1])})
    (ROOT / "_docs/mers/MOB-NORMALS-REPORT.json").write_text(json.dumps(report, indent=1))
    for kk, v in sorted(counts.items()):
        print(kk, v)
    print("textures", len(report), "with face map", sum(1 for r in report if r["face_rects"]),
          "materials", Counter(r["material"] for r in report))


if __name__ == "__main__":
    main()
