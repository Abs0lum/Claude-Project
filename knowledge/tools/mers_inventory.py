#!/usr/bin/env python3
"""mers_inventory.py — MERS program step 1 (D-C367).

For every entity in the skeleton census, list each colour texture it uses, resolve it through the
live resource-pack stack (top first), and classify it:
  tier1   our colour pixel-matches a Patrix Java colour that ships its own LabPBR _s (and maybe _n)
  derive  colour lives in one of our packs, no Patrix _s -> derived MERS
  vanilla colour only exists in Mojang's pack -> MR2 rule (keep Mojang's MERS unless it is flat)
Also notes any texture_set.json we already ship beside the colour.

Output: _docs/mers/MERS-INVENTORY.json + a summary on stdout.
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
VANILLA = ROOT / "_intake/bedrock-samples/resource_pack"
STACK = [ROOT / "_build" / d for d in os.environ.get(
    "MERS_STACK", "rp08-148,rp07-1438,rp06-1424,rp04-142,rp01-107").split(",")] + [VANILLA]
PATRIX_ROOTS = [ROOT / "_intake/patrix_zips_x/Patrix_26.2_256x_basic/assets/minecraft",
                ROOT / "_intake/patrix262/assets/minecraft",
                ROOT / "_intake/patrix_zips_x/Patrix_1.21.11_128x_mobs/assets/minecraft",
                ROOT / "_intake/patrix12111_128/assets/minecraft"]
EXTS = (".png", ".tga")
MATCH_MAD = 2.0  # mean absolute RGBA difference (0-255) that counts as "the same picture"
MATCH_MAD_SCALED = 8.0  # same picture at another resolution (resampling noise allowed)
LAYOUT_IOU = 0.96  # same-name Patrix sheet whose painted area matches ours -> same layout
# overlays drawn on a base sheet's template inherit the base's layout verdict (thin stripes score low IoU at 128 px)
OVERLAY_BASE = {"textures/entity/fish/tropical_a_pattern_": "textures/entity/fish/tropical_a",
                "textures/entity/fish/tropical_b_pattern_": "textures/entity/fish/tropical_b"}


def resolve(rel):
    """Return (pack_dir, file) for the top-of-stack file holding texture path `rel` (no extension)."""
    for pack in STACK:
        for ext in EXTS:
            f = pack / (rel + ext)
            if f.exists():
                return pack, f
    return None, None


def texture_paths(client_file):
    try:
        d = json.loads(Path(client_file).read_text(encoding="utf-8-sig"))
    except Exception:
        return []
    desc = d.get("minecraft:client_entity", {}).get("description", {})
    out = []
    for v in (desc.get("textures") or {}).values():
        if isinstance(v, str):
            out.append(v[:-4] if v.endswith(EXTS) else v)
    return out


def load_rgba(f):
    return np.asarray(Image.open(f).convert("RGBA"), dtype=np.int16)


def patrix_index():
    """size -> list of (colour file, _s file, _n file or None) for every Patrix entity colour with an _s.
    Both Patrix versions are indexed (their pictures differ in size / content for some mobs)."""
    idx = {}
    for root in PATRIX_ROOTS:
        for s in root.rglob("*_s.png"):
            if "entity" not in s.as_posix():
                continue
            colour = s.with_name(s.name[:-6] + ".png")
            if not colour.exists():
                continue
            n = s.with_name(s.name[:-6] + "_n.png")
            size = Image.open(colour).size
            idx.setdefault(size, []).append((colour, s, n if n.exists() else None))
    return idx


def compare(a, b):
    """(MAD over pixels opaque in either picture, alpha-mask IoU)."""
    ma, mb = a[..., 3] > 0, b[..., 3] > 0
    union = ma | mb
    if not union.any():
        return 999.0, 0.0
    return float(np.abs(a - b)[union].mean()), float((ma & mb).sum() / union.sum())


_SCALED = {}


def candidate_at(c, size):
    """Patrix colour `c` as an int16 RGBA array at `size` (BOX-resampled when its resolution differs); cached."""
    key = (str(c[0]), size)
    if key not in _SCALED:
        pic = Image.open(c[0]).convert("RGBA")
        if pic.size != size:
            pic = pic.resize(size, Image.BOX)
        _SCALED[key] = np.asarray(pic, dtype=np.int16)
    return _SCALED[key]


def best_patrix(f, idx):
    """Closest Patrix colour with the same aspect ratio, compared at OUR size (Patrix resampled when its
    resolution differs). Returns (mad, iou, candidate, scaled) or (None, None, None, None)."""
    img = Image.open(f)
    w, h = img.size
    ours = load_rgba(f)
    best = None
    # cheap pass: every same-aspect candidate at thumbnail size; the full-size compare runs on the 3 closest only
    tw, th = (32, max(1, 32 * h // w)) if w >= h else (max(1, 32 * w // h), 32)
    small = np.asarray(img.convert("RGBA").resize((tw, th), Image.BOX), dtype=np.int16)
    rough = []
    for (cw, ch), cands in idx.items():
        if cw * h != ch * w:
            continue
        for c in cands:
            rough.append((compare(small, candidate_at(c, (tw, th)))[0], c, (cw, ch) != (w, h)))
    for _, c, scaled in sorted(rough, key=lambda r: r[0])[:3]:
        mad, iou = compare(ours, candidate_at(c, (w, h)))
        if best is None or mad < best[0]:
            best = (mad, iou, c, scaled)
    return best if best else (None, None, None, None)


def layout_match(t):
    """Second chance for a 'derive' texture: a Patrix colour with the SAME NAME and an _s, same aspect, whose
    painted area (alpha >= 128, resampled to our size) covers ours (IoU >= LAYOUT_IOU). The picture may differ
    (ours smoothed / downscaled / retouched) — the shine map is placed by layout, so it still lines up.
    Highest-resolution candidate wins. Returns (candidate, iou) or (None, best_iou)."""
    base = Path(t["rel"]).name
    ours = Image.open(t["file"])
    w, h = ours.size
    mine = np.asarray(ours.convert("RGBA"))[..., 3] >= 128
    best, best_iou = None, 0.0
    for root in PATRIX_ROOTS:
        for s in sorted(root.rglob(base + "_s.png")):
            colour = s.with_name(base + ".png")
            if "entity" not in s.as_posix() or not colour.exists():
                continue
            pic = Image.open(colour)
            if pic.size[0] * h != pic.size[1] * w:
                continue
            theirs = np.asarray(pic.convert("RGBA").resize((w, h), Image.BOX))[..., 3] >= 128
            iou = float((mine & theirs).sum() / max(1, (mine | theirs).sum()))
            n = s.with_name(base + "_n.png")
            if iou >= LAYOUT_IOU and (best is None or pic.size[0] > Image.open(best[0]).size[0]):
                best = (colour, s, n if n.exists() else None)
            best_iou = max(best_iou, iou)
    return best, best_iou


def main():
    census = json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())
    idx = patrix_index()
    print("patrix colours with _s:", sum(len(v) for v in idx.values()))
    textures = {}
    for ent in census:
        for rel in texture_paths(ent["file"]):
            t = textures.setdefault(rel, {"rel": rel, "entities": []})
            t["entities"].append(ent["id"])
    for rel, t in textures.items():
        pack, f = resolve(rel)
        t["pack"] = pack.name if pack else None
        t["file"] = str(f) if f else None
        if not f:
            t["class"] = "missing"
            continue
        ts = f.with_name(f.name.rsplit(".", 1)[0] + ".texture_set.json")
        t["existing_set"] = ts.exists() and pack != VANILLA
        if pack == VANILLA:
            t["class"] = "vanilla"
            continue
        mad, iou, cand, scaled = best_patrix(f, idx)
        limit = MATCH_MAD_SCALED if scaled else MATCH_MAD
        if cand is not None and mad <= limit and iou >= 0.97:
            t["class"] = "tier1"
            t["patrix_colour"], t["patrix_s"] = str(cand[0]), str(cand[1])
            t["patrix_n"] = str(cand[2]) if cand[2] else None
            t["mad"], t["iou"], t["patrix_scaled"] = round(mad, 3), round(iou, 4), scaled
            t["tier1_kind"] = "exact"
        else:
            t["class"] = "derive"
            if cand is not None:
                t["nearest_patrix_mad"], t["nearest_patrix_iou"] = round(mad, 2), round(iou, 4)
                t["nearest_patrix"] = str(cand[0])
    for t in textures.values():  # second chance: same-name, same-layout Patrix sheet
        if t["class"] != "derive":
            continue
        cand, iou = layout_match(t)
        base_rel = next((b for pre, b in OVERLAY_BASE.items() if t["rel"].startswith(pre)), None)
        if cand is None and base_rel and textures.get(base_rel, {}).get("class") == "tier1":
            cand, _ = layout_match({**t, "file": textures[base_rel]["file"], "rel": t["rel"]})
            if cand is None:  # name-matched pattern sheet exists but thin-stripe IoU is low: take it by inheritance
                name = Path(t["rel"]).name
                for root in PATRIX_ROOTS:
                    s = next(iter(sorted(root.rglob(name + "_s.png"))), None)
                    if s is not None:
                        n = s.with_name(name + "_n.png")
                        cand = (s.with_name(name + ".png"), s, n if n.exists() else None)
                        break
            t["layout_by"] = base_rel
        if cand is not None:
            t["class"] = "tier1"
            t["tier1_kind"] = "layout"
            t["patrix_colour"], t["patrix_s"] = str(cand[0]), str(cand[1])
            t["patrix_n"] = str(cand[2]) if cand[2] else None
            t["layout_iou"] = round(iou, 4)
    out = ROOT / "_docs/mers/MERS-INVENTORY.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sorted(textures.values(), key=lambda t: t["rel"]), indent=1))
    c = Counter(t["class"] for t in textures.values())
    print("textures:", len(textures), dict(c))
    print("tier1 with _n:", sum(1 for t in textures.values() if t.get("patrix_n")))
    print("existing sets in our packs:", sum(1 for t in textures.values() if t.get("existing_set")))
    print("packs:", dict(Counter(t["pack"] for t in textures.values())))
    print(out)


if __name__ == "__main__":
    sys.exit(main())
