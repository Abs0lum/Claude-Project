#!/usr/bin/env python3
"""tier_round.py — RESOLUTION TIER ROUND (his 19:18 proposal, 19:50 rulings, 19:52 "start that build now"; D-C424).

UP to 256 (colour + normal + MERS all 256 — a set's layers must match its colour):
    dirt family: dirt, coarse dirt, podzol side, rooted dirt, farmland, mud, packed mud, muddy mangrove roots side
    common wood: oak / spruce / birch / dark oak planks + logs (+ log tops)
  Source: the matching Patrix 26.2 256x picture (thumbnail match against every Patrix block texture + OptiFine CTM tile that
  carries LabPBR maps), its own _n / _s by Lesson #156 (normal z encoding fixed 19:1x). The 256 picture is COLOUR-MATCHED to
  what he sees today (per-channel mean and spread of our current 128 picture), so the block keeps its look and gains detail.
DOWN to 64: End decor (purpur block / pillar / pillar top, end stone bricks + variants, chorus plant / flower).
Stone family, Nether decor, redstone / technical, small decor: unchanged (his 19:50).

Placement (his R2: any way within the size limits, nothing may supersede and lose a map): every file goes into the pack that
already draws that texture (the top pack holding the picture), with its set beside it — the same 'own your maps' rule the
block PBR round shipped; verified afterwards by block_pbr_census (0 shadowed) + verify_pbr_round + pack sizes.
Writes _staging/tier/<pack key>/… and _docs/blocks/TIER-ROUND.json."""
import io
import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import mers_derive as MD  # noqa: E402
import patrix_match as PM  # noqa: E402
import pbr_round as PR  # noqa: E402

STAGE = ROOT / "_staging/tier"
UP = re.compile(r"/(dirt|coarse_dirt|dirt_podzol|podzol|mud(?!_bricks)|packed_mud|grass_path|dirt_path|farmland|rooted_dirt|"
                r"muddy_mangrove_roots|planks_(oak|spruce|birch|big_oak)|(oak|spruce|birch|dark_oak)_planks|"
                r"log_(oak|spruce|birch|big_oak)|(oak|spruce|birch|dark_oak)_log)")
DOWN = re.compile(r"/(purpur|end_bricks|end_stone_brick|chorus)")
UP_MATCH_MAX = 12.0
ACCEPT = {"oak_log_v1": 13.5}        # matched by eye 19:5x (UNMATCHED sheet): the Patrix oak_log, graded
# families without a true Patrix 256 for EVERY member stay 128 (19:5x: our own birch log composites, our staggered spruce planks)
KEEP_128 = re.compile(r"/(birch_log|log_birch|spruce_planks|planks_spruce)")
KEY = {"RP-04": "rp04", "RP-10": "rp10", "RP-05": "rp05", "RP-01": "rp01", "RP-03": "rp03", "RP-11": "rp11", "RP-08": "rp08"}
BUILD = {"rp04": "rp04-146", "rp10": "rp10-144", "rp05": "rp05-52", "rp01": "rp01-108", "rp03": "rp03-61", "rp11": "rp11-136",
         "rp08": "rp08-1410"}


def png(im):
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return b.getvalue()


ROT_M = {0: np.eye(2), 1: np.array([[0, 1], [-1, 0]]), 2: -np.eye(2), 3: np.array([[0, -1], [1, 0]])}
FLIP_M = np.array([[-1, 0], [0, 1]])        # measured 19:5x on a synthetic bump with derive_normal's own convention


def dihedral(a, k, flip):
    """image transform T: optional left-right flip, then rot90 k times."""
    if flip:
        a = np.fliplr(a)
    return np.rot90(a, k).copy()


def dihedral_normal(n, k, flip):
    """the same transform for a normal map: move the pixels AND turn the XY vectors (M measured, not assumed)."""
    out = dihedral(n, k, flip).astype(float)
    v = out[..., :2] / 255 * 2 - 1
    M = ROT_M[k] @ (FLIP_M if flip else np.eye(2))
    v = v @ M.T
    out[..., :2] = np.round((v + 1) / 2 * 255).clip(0, 255)
    return out.astype(np.uint8)


CORR_MIN = 0.6          # 20:0x: wrong picks scored < 0.40, right ones >= 0.57 (TIER-CORR.json)
LEGACY = {"log_oak": "oak_log", "planks_oak": "oak_planks", "log_big_oak": "dark_oak_log", "log_big_oak_top": "dark_oak_log", "dark_oak_log_top": "dark_oak_log",   # a log block = sides + tops: one resolution
          "planks_big_oak": "dark_oak_planks", "log_spruce": "spruce_log", "planks_spruce": "spruce_planks",
          "log_birch": "birch_log", "planks_birch": "birch_planks"}


def layout_corr(new_col, ours):
    """blurred-luminance correlation of the new 256 picture (shrunk) against ours: the same LAYOUT or not."""
    from scipy import ndimage
    a = np.asarray(Image.fromarray(ours, "RGBA").convert("L")).astype(float)
    b = np.asarray(Image.fromarray(new_col, "RGBA").convert("L").resize(a.shape[::-1], Image.BOX)).astype(float)
    a, b = ndimage.gaussian_filter(a, 2), ndimage.gaussian_filter(b, 2)
    a, b = (a - a.mean()) / (a.std() + 1e-6), (b - b.mean()) / (b.std() + 1e-6)
    return round(float((a * b).mean()), 3)


def family(path):
    stem = path.rsplit("/", 1)[1]
    stem = re.sub(r"(_v\d+|_\d+)$", "", stem)
    return LEGACY.get(stem, stem)


def grade_match(src, ref):
    """per-channel mean / spread of `src` (Patrix 256) moved onto `ref`'s (our current picture), opaque pixels only."""
    s = src.astype(float)
    r = ref.astype(float)
    ms, mr = s[..., 3] > 0, r[..., 3] > 0
    out = s.copy()
    for c in range(3):
        a, b = s[..., c][ms], r[..., c][mr]
        if a.size and b.size:
            out[..., c] = (s[..., c] - a.mean()) / max(a.std(), 1e-3) * b.std() + b.mean()
    out[..., 3] = s[..., 3]
    return out.clip(0, 255).round().astype(np.uint8)


def put(key, rel, data, report_files):
    p = STAGE / key / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    report_files.append(rel)


def main():
    inv = json.loads((ROOT / "_docs/blocks/RES-INVENTORY.json").read_text())
    Z = zipfile.ZipFile(PR.PATRIX256)
    names = set(Z.namelist())
    keys, th = PM.index()
    rep = []
    for x in inv:
        path = x["path"]
        is_up = bool(UP.search(path)) and x["w"] <= 128 and not KEEP_128.search(path)
        is_down = bool(DOWN.search(path)) and x["w"] > 64
        if not (is_up or is_down):
            continue
        key = KEY[x["pack"][:5]]
        D = ROOT / "_build" / BUILD[key]
        base_dir, stem = path.rsplit("/", 1)
        col_p = next((D / (path + e) for e in (".tga", ".png") if (D / (path + e)).exists()), None)
        col = Image.open(col_p)
        rgba = np.asarray(col.convert("RGBA"))
        files = []
        row = {"path": path, "pack": x["pack"], "from": list(col.size)}
        if is_up:
            # 19:5x: rotated / mirrored variants (birch logs, spruce planks) — try the 8 orientations; the Patrix source is
            # then turned the same way (pixels + normal vectors)
            best = None
            for k in range(4):
                for flip in (False, True):
                    # our picture = T(patrix)  <=>  T^-1(ours) ~ patrix ; search with T^-1 applied to ours
                    inv_img = Image.fromarray(np.rot90(rgba, -k).copy() if not flip else np.fliplr(np.rot90(rgba, -k)).copy(), "RGBA")
                    t = PM.thumb(inv_img)
                    d = np.abs(th[..., :3] - t[None, ..., :3]).mean(axis=(1, 2, 3)) + np.abs(th[..., 3] - t[None, ..., 3]).mean(axis=(1, 2)) * 0.5
                    i = int(np.argmin(d))
                    if best is None or d[i] < best[0]:
                        best = (float(d[i]), i, k, flip)
                if best[0] < 4:
                    break
            dval, i, rot_k, rot_flip = best
            d = {i: dval}
            b = keys[i][:-4]
            if d[i] >= ACCEPT.get(stem, UP_MATCH_MAX) or b + "_n.png" not in names or b + "_s.png" not in names:
                row["skipped"] = f"no Patrix 256 source (best d {float(d[i]):.1f})"
                rep.append(row)
                continue
            src = np.asarray(Image.open(io.BytesIO(Z.read(b + ".png"))).convert("RGBA"))
            if src.shape[0] != src.shape[1] or src.shape[1] != 256:
                row["skipped"] = f"Patrix source is {src.shape[1]}x{src.shape[0]}"
                rep.append(row)
                continue
            src = dihedral(src, rot_k, rot_flip)
            new_col = grade_match(src, rgba)
            row["corr"] = layout_corr(new_col, rgba)
            nrm = dihedral_normal(MD.normal_156(np.asarray(Image.open(io.BytesIO(Z.read(b + "_n.png"))).convert("RGBA"))), rot_k, rot_flip)
            mer = dihedral(MD.mers_156(np.asarray(Image.open(io.BytesIO(Z.read(b + "_s.png"))).convert("RGBA"))), rot_k, rot_flip)
            ext = col_p.suffix
            if ext == ".tga":
                b2 = io.BytesIO()
                Image.fromarray(new_col, "RGBA").save(b2, "TGA", compression=None)
                put(key, path + ".tga", b2.getvalue(), files)
            else:
                put(key, path + ".png", png(Image.fromarray(new_col, "RGBA")), files)
            put(key, f"{base_dir}/{stem}_n256.png", png(Image.fromarray(nrm, "RGBA")), files)
            put(key, f"{base_dir}/{stem}_mer256.png", png(Image.fromarray(mer, "RGBA")), files)
            ts = {"format_version": "1.21.30", "minecraft:texture_set": {
                "color": stem, "normal": f"{stem}_n256", "metalness_emissive_roughness_subsurface": f"{stem}_mer256"}}
            put(key, path + ".texture_set.json", json.dumps(ts, indent=1).encode(), files)
            row.update({"to": [256, 256], "source": b.split("/minecraft/")[1], "d": round(float(d[i]), 2),
                        "orientation": {"rot90": rot_k, "mirror": rot_flip}})
        else:
            set_p = D / (path + ".texture_set.json")
            ts = json.loads(set_p.read_text())["minecraft:texture_set"] if set_p.exists() else {"color": stem}
            w, h = col.size
            size = (64, 64 * h // w)
            small = PR._bands_resize(col.convert("RGBA"), size, Image.LANCZOS)
            put(key, path + col_p.suffix if col_p.suffix == ".png" else path + ".png", png(small), files)
            new = {"color": stem}
            for k, v in ts.items():
                if k == "color" or not isinstance(v, str) or v.startswith("#"):
                    if k != "color":
                        new[k] = v
                    continue
                lp = next((col_p.parent / (v + e) for e in (".tga", ".png") if (col_p.parent / (v + e)).exists()), None)
                if lp is None:
                    continue
                kind = "normal" if k == "normal" else "mers"
                im2 = PR.resample(Image.open(lp), size, kind)
                put(key, f"{base_dir}/{v}_64.png", png(im2), files)
                new[k] = f"{v}_64"
            out = {"format_version": "1.21.30" if "metalness_emissive_roughness_subsurface" in new else "1.16.100",
                   "minecraft:texture_set": new}
            put(key, path + ".texture_set.json", json.dumps(out, indent=1).encode(), files)
            row.update({"to": list(size)})
        row["files"] = files
        rep.append(row)
    # a family goes to 256 only when EVERY member is a true match (same layout) — no mixed resolution on one block
    fams = {}
    for r in rep:
        if UP.search(r["path"]):
            fams.setdefault(family(r["path"]), []).append(r)
    for fam, rows in fams.items():
        bad = [r for r in rows if "skipped" in r or r.get("corr", 1.0) < CORR_MIN]
        if bad:
            for r in rows:
                for rel in r.get("files", []):
                    f = STAGE / KEY[r["pack"][:5]] / rel
                    if f.exists():
                        f.unlink()          # staging only; the never-delete hook moves it to _garbage
                r["files"] = []
                r.pop("to", None)
                r["skipped"] = r.get("skipped") or f"family '{fam}' stays 128 ({len(bad)} member(s) have no same-layout Patrix 256)"
    (ROOT / "_docs/blocks/TIER-ROUND.json").write_text(json.dumps(rep, indent=1))
    up = [r for r in rep if r.get("to") == [256, 256]]
    dn = [r for r in rep if r.get("to") and r["to"][0] == 64]
    sk = [r for r in rep if "skipped" in r]
    print(f"UP {len(up)} · DOWN {len(dn)} · skipped {len(sk)}", [(r["path"][16:], r["skipped"]) for r in sk][:20])


if __name__ == "__main__":
    main()
