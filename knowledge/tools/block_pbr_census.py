#!/usr/bin/env python3
"""block_pbr_census.py — his 17:38 report (grass / dirt "no depth": separated from its MERS / normal maps — "check for this kind
of error across all blocks"). For EVERY texture a block draws in his installed stack:
  USED KEYS  vanilla blocks: the effective blocks.json (top pack's entry per block, else vanilla 1.21 blocks.json) — every
             face key, every variation path (blocks.json draws variations); custom blocks (BP-02, StripMine BP, Markers BP):
             every material_instances texture key in components + permutations — FIRST variation only (L-VAR-1: the
             custom-block resolver flattens variations and draws the first).
  RESOLVE    texture path -> the effective texture set = the TOP pack holding <path>.texture_set.json (Microsoft: "Texture
             Set definitions for the same texture resource don't get merged. The higher priority pack's Texture Set
             definition will override the lower priority one"; "Texture Set definitions can only reference images that exist
             in the same resource pack as the definition").
  STATUS     OK             set found; color + normal/heightmap + MER layers all exist IN THE SET'S OWN PACK, sizes match
             NO_SET         no pack has a set for this path (flat: no depth, no MERS)
             MEMBER_MISSING the set names a layer its own pack does not hold (that layer is lost)
             SIZE_MISMATCH  a layer's size differs from the color layer's
             FLAT_NORMAL    the normal layer is (near) uniform (no depth)
             SHADOWED_PNG   a HIGHER pack ships a plain image at the same path without a set (per the docs the set keeps its
                            own color; the higher image is unused — or, if the engine resolves the image first, the set is
                            lost: UNVERIFIED engine order, reported both ways)
Writes _docs/blocks/BLOCK-PBR-CENSUS.json + .md."""
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import stack_now as SN  # noqa: E402

BPS = [ROOT / "_build/bp02-206", ROOT / "_build/markers-0.2.1/BP"]   # 10-02: StripMine BP merged into BP-02 1.3.206
VANILLA_BLOCKS = ROOT / "_intake/vanilla-1.21/blocks.json"
FACES = ("up", "down", "side", "north", "south", "east", "west")
EXT = (".tga", ".png", ".jpg", ".jpeg")


def jl(p):
    return SN.jl(Path(p).read_bytes())


def keys_of_blockjson_entry(e):
    t = e.get("textures")
    out = []
    if isinstance(t, str):
        out.append(t)
    elif isinstance(t, dict):
        out += [v for v in t.values() if isinstance(v, str)]
    for k in ("carried_textures",):
        v = e.get(k)
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, dict):
            out += [x for x in v.values() if isinstance(x, str)]
    return out


def used_keys(P):
    """{key: set of (who, mode)} — mode 'all' (blocks.json, every variation) or 'first' (custom block)."""
    used = defaultdict(set)
    eff = {}
    for p in reversed(P):                          # bottom first; top overrides per block
        d = p.json("blocks.json") or {}
        for k, v in d.items():
            if k == "format_version" or not isinstance(v, dict):
                continue
            eff[k[len("minecraft:"):] if k.startswith("minecraft:") else k] = (p.name, v)   # pw:vine != vine (10-02 fix)
    van = jl(VANILLA_BLOCKS)
    for k, v in van.items():
        if k == "format_version" or not isinstance(v, dict):
            continue
        eff.setdefault(k, ("vanilla", v))
    for blk, (src, e) in eff.items():
        for key in keys_of_blockjson_entry(e):
            used[key].add((f"minecraft:{blk}" if ":" not in blk else blk, "all"))
    for bp in BPS:
        for f in (bp / "blocks").rglob("*.json") if (bp / "blocks").exists() else []:
            try:
                d = jl(f)
            except Exception:  # noqa: BLE001
                continue
            blk = (d.get("minecraft:block") or {})
            ident = (blk.get("description") or {}).get("identifier", f.stem)
            comps = [blk.get("components") or {}] + [pm.get("components") or {} for pm in blk.get("permutations") or []]
            for c in comps:
                for inst in (c.get("minecraft:material_instances") or {}).values():
                    if isinstance(inst, dict) and isinstance(inst.get("texture"), str):
                        used[inst["texture"]].add((ident, "first"))
    return used


def img(p, rel):
    return Image.open(io.BytesIO(p.read(rel)))


def find_layer(p, base_dir, name):
    for e in EXT:
        rel = f"{base_dir}/{name}{e}"
        if p.has(rel):
            return rel
    return None


def check_path(P, path):
    """-> dict status for one texture path."""
    holders_img = [i for i, p in enumerate(P) if any(p.has(path + e) for e in EXT)]
    holders_set = [i for i, p in enumerate(P) if p.has(path + ".texture_set.json")]
    r = {"path": path, "img_packs": [P[i].name for i in holders_img], "set_packs": [P[i].name for i in holders_set]}
    if not holders_set:
        r["status"] = ["NO_SET"]
        return r
    si = holders_set[0]
    p = P[si]
    r["set_pack"] = p.name
    try:
        ts = p.json(path + ".texture_set.json")["minecraft:texture_set"]
    except Exception as e:  # noqa: BLE001
        r["status"] = [f"SET_UNREADABLE {e}"]
        return r
    r["set"] = ts
    base_dir = path.rsplit("/", 1)[0]
    st = []
    sizes = {}
    for layer in ("color", "normal", "heightmap", "metalness_emissive_roughness", "metalness_emissive_roughness_subsurface"):
        v = ts.get(layer)
        if v is None or not isinstance(v, str):
            continue                               # a uniform value (list / hex) is fine
        if v.startswith("#"):
            continue
        rel = find_layer(p, base_dir, v)
        if not rel:
            st.append(f"MEMBER_MISSING {layer}={v}")
            continue
        try:
            im = img(p, rel)
            sizes[layer] = im.size
            if layer == "normal":
                a = np.asarray(im.convert("RGB")).astype(float)
                if a[..., 0].std() < 2 and a[..., 1].std() < 2:
                    st.append("FLAT_NORMAL")
            if layer == "heightmap":
                a = np.asarray(im.convert("L")).astype(float)
                if a.std() < 2:
                    st.append("FLAT_HEIGHTMAP")
        except Exception as e:  # noqa: BLE001
            st.append(f"LAYER_UNREADABLE {layer} {e}")
    if "normal" not in ts and "heightmap" not in ts:
        st.append("NO_DEPTH_LAYER")
    if not any(k.startswith("metalness") for k in ts):
        st.append("NO_MERS_LAYER")
    if "color" in sizes:
        for k, s in sizes.items():
            if s != sizes["color"]:
                st.append(f"SIZE_MISMATCH {k} {s} vs color {sizes['color']}")
    r["sizes"] = {k: list(v) for k, v in sizes.items()}
    higher = [P[i].name for i in holders_img if i < si and not P[i].has(path + ".texture_set.json")]
    if higher:
        st.append("SHADOWED_PNG by " + ", ".join(higher))
    r["status"] = st or ["OK"]
    return r


def main():
    P = SN.packs()
    T = SN.terrain(P)
    used = used_keys(P)
    rows, missing_keys = [], []
    for key, users in sorted(used.items()):
        if key not in T:
            missing_keys.append((key, sorted(u for u, _ in users)[:5]))
            continue
        pack, defn, _ = T[key]
        paths = SN.paths_of(defn)
        modes = {m for _, m in users}
        draw = paths if "all" in modes else paths[:1]
        for path in draw:
            r = check_path(P, path)
            r.update({"key": key, "key_pack": pack, "blocks": sorted(u for u, _ in users)[:6], "n_blocks": len(users)})
            rows.append(r)
    out = ROOT / "_docs/blocks"
    out.mkdir(parents=True, exist_ok=True)
    (out / "BLOCK-PBR-CENSUS.json").write_text(json.dumps({"rows": rows, "keys_not_in_terrain": missing_keys}, indent=1))
    c = Counter(s.split(" ")[0] for r in rows for s in r["status"])
    print(f"keys used {len(used)} · paths checked {len(rows)} · keys not in any terrain_texture {len(missing_keys)}")
    print(dict(c))
    return rows, missing_keys


if __name__ == "__main__":
    main()
