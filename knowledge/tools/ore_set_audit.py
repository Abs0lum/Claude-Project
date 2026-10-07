#!/usr/bin/env python3
"""ore_set_audit.py — his O5 (15:42 CT 10-02): "maybe it looked gray because it was a flat image without MERS".
For every ore key in a pack stack (default r1002i = what he has installed), report:
  key -> pack + image -> the texture_set.json the stack serves for that image path (top pack wins) -> the MER(S) and
  normal / heightmap files it names (looked up in the SAME pack as the set) -> channel statistics on rock vs mineral.
Read-only. Output: table on stdout + _docs/ores/ORE-SET-AUDIT-<stack>.json"""
import io
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, "/home/claude/tools")
STACK = sys.argv[1] if len(sys.argv) > 1 else "r1002i"
os.environ["PW_STACK"] = STACK
import stack_now as S  # noqa: E402

KEYS = ["coal_ore", "iron_ore", "copper_ore", "gold_ore", "redstone_ore", "lapis_ore", "emerald_ore", "diamond_ore",
        "deepslate_coal_ore", "deepslate_iron_ore", "deepslate_copper_ore", "deepslate_gold_ore",
        "deepslate_redstone_ore", "deepslate_lapis_ore", "deepslate_emerald_ore", "deepslate_diamond_ore",
        "nether_gold_ore", "quartz_ore", "deepslate", "stone", "netherrack"]


def load(pack, rel):
    return Image.open(io.BytesIO(pack.read(rel)))


def mineral_mask(rgb):
    """Pixels that are mineral, not rock: saturated, or far darker than the rock median (coal)."""
    a = rgb.astype(float) / 255
    mx, mn = a.max(2), a.min(2)
    sat = (mx - mn) / (mx + 1e-6)
    lum = a.mean(2)
    return (sat > 0.25) | (lum < np.median(lum) * 0.55)


def resolve_in_pack(pack, set_dir, name):
    for ext in (".png", ".tga", ".jpg"):
        rel = f"{set_dir}/{name}{ext}"
        if pack.has(rel):
            return rel
    return None


def channel_stats(arr, mask):
    def med(m):
        return [int(np.median(arr[..., c][m])) for c in range(arr.shape[2])] if m.any() else None
    return {"rock": med(~mask), "mineral": med(mask)}


def main():
    packs = S.packs()
    terrain = S.terrain(packs)
    report = []
    for key in KEYS:
        if key not in terrain:
            report.append({"key": key, "error": "no terrain key"})
            continue
        tpack, defn, _ = terrain[key]
        for path in S.paths_of(defn)[:1]:
            ipack, ifile = S.find_image(packs, path)
            row = {"key": key, "terrain_pack": tpack, "path": path, "image_pack": ipack.name if ipack else None}
            if not ipack:
                report.append(row)
                continue
            rgb_img = load(ipack, ifile).convert("RGBA")
            rgb = np.asarray(rgb_img)[..., :3]
            mask = mineral_mask(rgb)
            row.update(size=rgb_img.size, mineral_pct=round(100 * float(mask.mean()), 1),
                       lum_rock=round(float(rgb[~mask].mean()), 1))
            set_pack = next((p for p in packs if p.has(path + ".texture_set.json")), None)
            row["set_pack"] = set_pack.name if set_pack else None
            if set_pack:
                tset = S.jl(set_pack.read(path + ".texture_set.json"))["minecraft:texture_set"]
                row["set"] = tset
                set_dir = path.rsplit("/", 1)[0]
                for field in ("metalness_emissive_roughness", "metalness_emissive_roughness_subsurface", "normal", "heightmap"):
                    value = tset.get(field)
                    if not isinstance(value, str):
                        if value is not None:
                            row[field] = {"uniform": value}
                        continue
                    rel = resolve_in_pack(set_pack, set_dir, value)
                    if not rel:
                        row[field] = {"name": value, "MISSING_IN_SET_PACK": True}
                        continue
                    im = load(set_pack, rel)
                    has_alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
                    arr = np.asarray(im.convert("RGBA" if has_alpha else "RGB")).astype(int)
                    if arr.shape[:2] != mask.shape:
                        m2 = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize(arr.shape[1::-1], Image.NEAREST)) > 0
                    else:
                        m2 = mask
                    entry = {"file": rel, "size": im.size, "mode": im.mode, **channel_stats(arr, m2)}
                    if field == "normal":
                        entry["flat_pct"] = round(100 * float(((abs(arr[..., 0] - 128) < 6) & (abs(arr[..., 1] - 128) < 6)).mean()), 1)
                        entry["xy_std"] = [round(float(arr[..., 0].std()), 1), round(float(arr[..., 1].std()), 1)]
                    row[field] = entry
            report.append(row)
    os.makedirs("/home/claude/_docs/ores", exist_ok=True)
    out = f"/home/claude/_docs/ores/ORE-SET-AUDIT-{STACK}.json"
    json.dump(report, open(out, "w"), indent=1, default=str)
    for r in report:
        mer = r.get("metalness_emissive_roughness") or r.get("metalness_emissive_roughness_subsurface") or {}
        nrm = r.get("normal") or {}
        hm = r.get("heightmap") or {}
        print(f"{r['key']:24s} img {str(r.get('image_pack')):15s} {str(r.get('size')):10s} rockLum {r.get('lum_rock')} "
              f"min% {r.get('mineral_pct')} | set {str(r.get('set_pack')):15s} "
              f"MER rock {mer.get('rock')} min {mer.get('mineral')} {'MISSING' if mer.get('MISSING_IN_SET_PACK') else ''} "
              f"{mer.get('size','')} {mer.get('file','').split('/')[-1]}"
              f" | N {nrm.get('file','-').split('/')[-1]} flat {nrm.get('flat_pct')}% {'MISSING' if nrm.get('MISSING_IN_SET_PACK') else ''}"
              f" | H {hm.get('file','-').split('/')[-1] if hm else '-'}")
    print("->", out)


if __name__ == "__main__":
    main()
