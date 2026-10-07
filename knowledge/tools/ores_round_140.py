#!/usr/bin/env python3
"""ores_round_140.py — ore round 1.3.40 (his 15:02 O1/O3, 15:12 Stratum quartz, 15:42 O5/O6, 16:47 NG = Patrix).

Builds:
  RP-11 1.3.40  from rp11-138 (the last DELIVERED RP-11): every ore = Patrix 26.2 256 mineral on OUR plain rock, with the
                plain block's own MERS + normal under the rock (ORE-SET-AUDIT: the shipped sets were broken — subsurface 255
                on whole blocks, metal rock, glowing rock, borrowed normals). 4 variations per ore:
                  Patrix ores: the default image + 3 of Patrix's own CTM repeat tiles, each on a different plain-rock
                  variation (stone / stone_v1 / stone_v2 / stone_v3, deepslate_0 / _v1.., netherrack_v0 / _v1..).
                  Nether quartz: Stratum 256x chips (his 15:12 choice) on our netherrack; the 4 variations are the chips
                  as drawn, flipped left-right, flipped top-bottom, turned 180 degrees (normal vectors flipped to match —
                  these four are correct whichever green-channel convention the engine uses).
                Minerals: HIGH reflectivity (gems roughness 8/255, quartz 10, metals 20, coal 60), tiny glow (8/255 ~ 3 %),
                sand-recipe glint grains (6 %); metals metallic (gold/copper/nether gold 200, iron 140), gems/quartz/coal 0.
  RP-04 1.3.156 from rp04-155 (identical ore removal; 1.3.155 was uploaded to the DO-NOT-USE folder, so its number is spent).
  RP-03 1.3.67  from rp03-66: every ore file removed (incl. the Patrix BONE 'quartz_ore' your game shows today) — the ore
                keys, images and sets live ONLY in RP-11 (ownership rule).
Usage: ores_round_140.py preview OUT.png | ores_round_140.py build"""
import io
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_opening, gaussian_filter, label

sys.path.insert(0, "/home/claude/tools")
os.environ["PW_STACK"] = "r1002i"           # his installed stack: plain rock comes from RP-04 1.3.154 (= 1.3.155/156)
import mers_derive as MD  # noqa: E402
import ores_compose as OC  # noqa: E402
import stack_now as S  # noqa: E402

B = Path("/home/claude/_build")
SZ = 256
PATRIX = zipfile.ZipFile("/home/claude/_intake/patrix262_256/Patrix_26.2_256x_basic.zip")
STRATUM = zipfile.ZipFile("/home/claude/_intake/newpacks-1001/Stratum 256x.zip")
PB = "assets/minecraft/textures/block/"
CTM = "assets/minecraft/optifine/ctm/patrix/"
# key -> (Patrix stem, CTM folder, base key, mineral class)
ORES = {
    "coal_ore": ("coal_ore", "ore/coal", "stone", "coal"),
    "iron_ore": ("iron_ore", "ore/iron", "stone", "iron"),
    "copper_ore": ("copper_ore", "ore/copper", "stone", "copper"),
    "gold_ore": ("gold_ore", "ore/gold", "stone", "gold"),
    "redstone_ore": ("redstone_ore", "ore/redstone", "stone", "gem"),
    "emerald_ore": ("emerald_ore", "ore/emerald", "stone", "gem"),
    "lapis_ore": ("lapis_ore", "ore/lapis", "stone", "gem"),
    "diamond_ore": ("diamond_ore", "ore/diamond", "stone", "gem"),
    "deepslate_coal_ore": ("deepslate_coal_ore", "ore/coal/deepslate", "deepslate", "coal"),
    "deepslate_iron_ore": ("deepslate_iron_ore", "ore/iron/deepslate", "deepslate", "iron"),
    "deepslate_copper_ore": ("deepslate_copper_ore", "ore/copper/deepslate", "deepslate", "copper"),
    "deepslate_gold_ore": ("deepslate_gold_ore", "ore/gold/deepslate", "deepslate", "gold"),
    "deepslate_redstone_ore": ("deepslate_redstone_ore", "ore/redstone/deepslate", "deepslate", "gem"),
    "deepslate_emerald_ore": ("deepslate_emerald_ore", "ore/emerald/deepslate", "deepslate", "gem"),
    "deepslate_lapis_ore": ("deepslate_lapis_ore", "ore/lapis/deepslate", "deepslate", "gem"),
    "deepslate_diamond_ore": ("deepslate_diamond_ore", "ore/diamond/deepslate", "deepslate", "gem"),
    "nether_gold_ore": ("nether_gold_ore", "nether/gold", "netherrack", "ngold"),
    "quartz_ore": ("nether_quartz_ore", None, "netherrack", "quartz"),       # Stratum
}
MINERAL = {  # metalness, roughness, glint metalness   (HIGH reflectivity: low roughness)
    "gold": (200, 20, 200), "copper": (200, 20, 200), "ngold": (200, 20, 200), "iron": (140, 20, 140),
    "gem": (0, 8, 0), "quartz": (0, 10, 0), "coal": (0, 60, 0)}
EMISSIVE = 8
GLINT = 0.06
GLINT_ROUGH = 10
CTM_TILES = (6, 11, 16)                     # + the default image = 4 variations, spread over Patrix's 4x4 repeat set
QUARTZ_FLIPS = ("none", "h", "v", "hv")


def png(zf, name):
    return np.asarray(Image.open(io.BytesIO(zf.read(name))).convert("RGBA"))


def base_variants(packs, terrain, key, count=4):
    """The first `count` variation images of a plain block + their own normal + MERS, upscaled to 256 (nearest)."""
    out = []
    for path in S.paths_of(terrain[key][1])[:count]:
        pack, fname = S.find_image(packs, path)
        stem = fname.rsplit(".", 1)[0]
        tset = json.loads(pack.read(stem + ".texture_set.json"))["minecraft:texture_set"]
        folder = stem.rsplit("/", 1)[0]

        def layer(name):
            for ext in (".png", ".tga"):
                rel = f"{folder}/{name}{ext}"
                if pack.has(rel):
                    return Image.open(io.BytesIO(pack.read(rel))).convert("RGBA")
            raise FileNotFoundError(f"{pack.name}: {folder}/{name}")
        col = Image.open(io.BytesIO(pack.read(fname))).convert("RGBA")
        maps = [col, layer(tset["normal"]), layer(tset["metalness_emissive_roughness_subsurface"])]
        out.append(tuple(np.asarray(m.resize((SZ, SZ), Image.NEAREST)) for m in maps) + (f"{pack.name} {fname}",))
    return out


def quartz_mask(col):
    rgb = col[..., :3].astype(float) / 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    m = (lum > 0.50) & (sat < 0.35)
    m = binary_dilation(m, iterations=1)
    lab, n = label(m)
    sizes = np.bincount(lab.ravel())
    return m & np.isin(lab, [k for k in range(1, n + 1) if sizes[k] >= 6])


def coal_mask(col):
    """Coal = dark, unsaturated BLOBS. A blob test (darker than 0.62 x the tile median, then opened twice) keeps the coal
    patches and drops the thin dark crevices of Patrix's layered deepslate, which the old local-darkness test picked up
    instead of the coal (deepslate coal came out almost plain in the first 1.3.40 preview)."""
    rgb = col[..., :3].astype(float) / 255
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    m = (lum < np.median(lum) * 0.62) & (sat < 0.3)
    m = binary_opening(m, iterations=2)
    return binary_dilation(m, iterations=1)


def mineral_layers(key, variant):
    """(colour, mask, normal-vectors) of the mineral for one variation (0 = default image)."""
    stem, ctm, _, cls = ORES[key]
    if cls == "quartz":
        col = png(STRATUM, PB + "nether_quartz_ore.png")
        nrm = MD.normal_156(png(STRATUM, PB + "nether_quartz_ore_n.png"))
        mask = quartz_mask(col)
        vec = nrm[..., :3].astype(float) / 255 * 2 - 1
        flip = QUARTZ_FLIPS[variant]
        if "h" in flip:
            col, mask, vec = col[:, ::-1], mask[:, ::-1], vec[:, ::-1] * np.array([-1, 1, 1])
        if "v" in flip:
            col, mask, vec = col[::-1], mask[::-1], vec[::-1] * np.array([1, -1, 1])
        return np.ascontiguousarray(col), np.ascontiguousarray(mask), np.ascontiguousarray(vec)
    if variant == 0:
        name = PB + stem
    else:
        name = f"{CTM}{ctm}/{CTM_TILES[variant - 1]}"
    col = png(PATRIX, name + ".png")
    spec_name = name + "_s.png" if (name + "_s.png") in PATRIX.namelist() else PB + stem + "_s.png"
    nrm_name = name + "_n.png" if (name + "_n.png") in PATRIX.namelist() else PB + stem + "_n.png"
    spec = png(PATRIX, spec_name)
    nrm = MD.normal_156(png(PATRIX, nrm_name))
    mask = coal_mask(col) if cls == "coal" else OC.mineral_mask(stem, cls, col, spec)
    return col, mask, nrm[..., :3].astype(float) / 255 * 2 - 1


def compose(key, variant, base, seed):
    _, _, _, cls = ORES[key]
    col_m, mask, vec_m = mineral_layers(key, variant)
    alpha = np.clip(gaussian_filter(mask.astype(float), 0.6) * 1.25, 0, 1)
    alpha[mask] = np.maximum(alpha[mask], 0.85)
    bcol, bnrm, bmer, src = base
    a3 = alpha[..., None]
    colour = np.empty((SZ, SZ, 4), np.uint8)
    colour[..., :3] = np.round(bcol[..., :3] * (1 - a3) + col_m[..., :3] * a3).astype(np.uint8)
    colour[..., 3] = 255
    vec_b = bnrm[..., :3].astype(float) / 255 * 2 - 1
    vec = vec_b * (1 - a3) + vec_m * a3
    mer = bmer.astype(float).copy()                                   # the plain block's own MERS: rock stays rock
    metal, rough, glint_metal = MINERAL[cls]
    inside = alpha > 0.5
    mer[inside, 0], mer[inside, 1], mer[inside, 2], mer[inside, 3] = metal, EMISSIVE, rough, 0
    rng = np.random.default_rng(seed)
    ys, xs = np.nonzero(inside)
    pick = rng.random(len(ys)) < GLINT
    gy, gx = ys[pick], xs[pick]
    ang = np.radians(rng.integers(0, 8, len(gy)) * 45.0)
    tilt = np.radians(rng.uniform(8, 14, len(gy)))
    vec[gy, gx] = np.stack([np.sin(tilt) * np.cos(ang), np.sin(tilt) * np.sin(ang), np.cos(tilt)], -1)
    mer[gy, gx, 0], mer[gy, gx, 2] = glint_metal, GLINT_ROUGH
    vec /= np.maximum(np.linalg.norm(vec, axis=-1, keepdims=True), 1e-6)
    normal = np.empty((SZ, SZ, 4), np.uint8)
    normal[..., :3] = np.clip(np.round((vec + 1) / 2 * 255), 0, 255).astype(np.uint8)
    normal[..., 3] = 255
    info = {"mineral_pct": round(float(inside.mean() * 100), 1), "glints": int(len(gy)), "rock": src,
            "mineral_src": "Stratum 256x nether_quartz_ore " + QUARTZ_FLIPS[variant] if cls == "quartz" else
            ("Patrix default" if variant == 0 else f"Patrix CTM {ORES[key][1]}/{CTM_TILES[variant - 1]}")}
    return colour, normal, np.clip(np.round(mer), 0, 255).astype(np.uint8), info


def all_ores():
    packs = S.packs()
    terrain = S.terrain(packs)
    bases = {k: base_variants(packs, terrain, k) for k in ("stone", "deepslate", "netherrack")}
    out = {}
    for i, key in enumerate(ORES):
        out[key] = [compose(key, v, bases[ORES[key][2]][v], 9000 + i * 10 + v) for v in range(4)]
    return out


def preview(path, res=None):
    res = res or all_ores()
    tile = 128
    sheet = Image.new("RGB", (tile * 4 * 3 + 40, (tile + 16) * len(res) + 10), (16, 16, 20))
    draw = ImageDraw.Draw(sheet)
    for row, (key, variants) in enumerate(res.items()):
        y = row * (tile + 16)
        draw.text((4, y + 2), key, fill=(255, 220, 120))
        for v, (c, n, m, info) in enumerate(variants):
            x = v * (tile * 3 + 10)
            sheet.paste(Image.fromarray(c).resize((tile, tile), Image.LANCZOS), (x, y + 14))
            sheet.paste(Image.fromarray(n[..., :3]).resize((tile, tile), Image.LANCZOS), (x + tile, y + 14))
            sheet.paste(Image.fromarray(m[..., :3]).resize((tile, tile), Image.LANCZOS), (x + 2 * tile, y + 14))
    sheet.save(path)


def is_ore_file(name):
    keys = sorted(set(ORES) | {"nether_quartz_ore"}, key=len, reverse=True)
    return any(re.match(rf"^{k}(_[a-z0-9_]+)?\.(png|tga|jpg|texture_set\.json)$", name) for k in keys)


def bump_manifest(folder, ver, desc):
    mp = B / folder / "manifest.json"
    man = json.loads(re.sub(r"(?m)^\s*//.*$", "", mp.read_text(encoding="utf-8-sig")))
    old = ".".join(map(str, man["header"]["version"]))
    man["header"]["version"] = ver
    for mod in man["modules"]:
        mod["version"] = ver
    vs = ".".join(map(str, ver))
    man["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, man["header"]["name"])
    man["header"]["description"] = f"v{vs} (2026-10-02) {desc} Includes all of v{old}."
    assert "pbr" in (man.get("capabilities") or []), folder
    mp.write_text(json.dumps(man, indent=2))


def copy_without_ores(src, dst, report_key, rep):
    """Copy a pack, leaving out every ore image / map / set anywhere under textures/blocks (and, for RP-11, its old
    orphan textures/blocks/deepslate/ folder, which no terrain key names)."""
    def ignore(dirp, names):
        rel = os.path.relpath(dirp, B / src).replace("\\", "/")
        if not rel.startswith("textures/blocks"):
            return []
        out = [n for n in names if is_ore_file(n)]
        if src.startswith("rp11") and rel == "textures/blocks" and "deepslate" in names:
            out.append("deepslate")
        rep[report_key].extend(f"{rel}/{n}" for n in out)
        return out
    shutil.copytree(B / src, B / dst, ignore=ignore)


def drop_keys(folder, rep, report_key):
    tp = B / folder / "textures/terrain_texture.json"
    if not tp.exists():
        return
    t = json.loads(tp.read_text())
    rep[report_key] = [k for k in list(t["texture_data"]) if k in ORES and t["texture_data"].pop(k, None) is not None]
    tp.write_text(json.dumps(t, indent=1))
    tl = B / folder / "textures/textures_list.json"
    if tl.exists():
        lst = json.loads(tl.read_text())
        kept = [p for p in lst if not is_ore_file(p.rsplit("/", 1)[-1] + ".png")]
        tl.write_text(json.dumps(kept, indent=1))


def build():
    for d in ("rp11-140", "rp04-156", "rp03-67"):
        assert not (B / d).exists(), f"never rebuild {d}"
    res = all_ores()
    rep = {"rp11_dropped": [], "rp04_dropped": [], "rp03_dropped": [], "keys": {}}
    copy_without_ores("rp11-138", "rp11-140", "rp11_dropped", rep)
    copy_without_ores("rp04-155", "rp04-156", "rp04_dropped", rep)
    copy_without_ores("rp03-66", "rp03-67", "rp03_dropped", rep)
    drop_keys("rp04-156", rep, "rp04_keys_removed")
    drop_keys("rp03-67", rep, "rp03_keys_removed")
    ore_dir = B / "rp11-140/textures/blocks/ores"
    ore_dir.mkdir(parents=True)
    tp = B / "rp11-140/textures/terrain_texture.json"
    terrain = json.loads(tp.read_text())
    for key, variants in res.items():
        paths = []
        for v, (c, n, m, info) in enumerate(variants):
            name = f"{key}_{v}"
            Image.fromarray(c, "RGBA").save(ore_dir / f"{name}.png", optimize=True)
            Image.fromarray(n, "RGBA").save(ore_dir / f"{name}_n.png", optimize=True)
            Image.fromarray(m, "RGBA").save(ore_dir / f"{name}_mer.png", optimize=True)
            (ore_dir / f"{name}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
                "color": name, "normal": f"{name}_n", "metalness_emissive_roughness_subsurface": f"{name}_mer"}}, indent=1))
            paths.append({"path": f"textures/blocks/ores/{name}", "weight": 1})
            rep["keys"][name] = info
        terrain["texture_data"][key] = {"textures": {"variations": paths}}
    tp.write_text(json.dumps(terrain, indent=1))
    tl = B / "rp11-140/textures/textures_list.json"
    if tl.exists():
        lst = [p for p in json.loads(tl.read_text()) if not is_ore_file(p.rsplit("/", 1)[-1] + ".png")]
        lst += [f"textures/blocks/ores/{k}_{v}" for k in res for v in range(4)]
        tl.write_text(json.dumps(lst, indent=1))
    bump_manifest("rp11-140", [1, 3, 40], "Ores: Patrix minerals on OUR stone / deepslate / netherrack with the plain blocks' own "
                  "shine and depth maps (the old sets were broken: milky deepslate, metal or glowing rock, borrowed depth maps); "
                  "4 variations per ore; Nether quartz = Stratum quartz chips (not bones); minerals highly reflective, tiny glow, "
                  "glints; every ore file lives in this pack only.")
    bump_manifest("rp04-156", [1, 3, 156], "Ore textures removed (they live in RP-11).")
    bump_manifest("rp03-67", [1, 3, 67], "Ore textures removed (they live in RP-11), including the bone 'quartz ore'.")
    Path("/home/claude/_docs/blocks/BUILD-ORES-140.json").write_text(json.dumps(rep, indent=1))
    preview("/home/claude/_docs/ores/ORES-140-preview.png", res)
    return rep


if __name__ == "__main__":
    if sys.argv[1] == "preview":
        preview(sys.argv[2])
    elif sys.argv[1] == "build":
        r = build()
        print(json.dumps({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in r.items()}, indent=1))


# ---- his 17:39 QZ: Patrix bones + Stratum quartz chips together on our netherrack ("make them our own") -------------
BONE_ROUGH, BONE_METAL = 170, 0          # bone: matte, non-metal


def bone_layers(variant):
    """Patrix nether quartz ore (the bone bed) for one variation: default image or CTM tile 6 / 11 / 16."""
    name = PB + "nether_quartz_ore" if variant == 0 else f"{CTM}nether/quartz_ore/{CTM_TILES[variant - 1]}"
    col = png(PATRIX, name + ".png")
    spec = png(PATRIX, (name + "_s.png") if (name + "_s.png") in PATRIX.namelist() else PB + "nether_quartz_ore_s.png")
    nrm = MD.normal_156(png(PATRIX, (name + "_n.png") if (name + "_n.png") in PATRIX.namelist() else PB + "nether_quartz_ore_n.png"))
    mask = OC.mineral_mask("nether_quartz_ore", "quartz", col, spec)    # bright, unsaturated = bone on red rock
    return col, mask, nrm[..., :3].astype(float) / 255 * 2 - 1


def compose_bones_and_quartz(variant, base, seed):
    """our netherrack -> Patrix bones (matte) -> Stratum quartz chips on top (glossy, tiny glow, glints)."""
    bcol, bnrm, bmer, src = base
    colour = bcol[..., :3].astype(float)
    vec = bnrm[..., :3].astype(float) / 255 * 2 - 1
    mer = bmer.astype(float).copy()
    for col_m, mask, vec_m, metal, emissive, rough in (
            (*bone_layers(variant), BONE_METAL, 0, BONE_ROUGH),
            (*mineral_layers("quartz_ore", variant), MINERAL["quartz"][0], EMISSIVE, MINERAL["quartz"][1])):
        alpha = np.clip(gaussian_filter(mask.astype(float), 0.6) * 1.25, 0, 1)
        alpha[mask] = np.maximum(alpha[mask], 0.85)
        a3 = alpha[..., None]
        colour = colour * (1 - a3) + col_m[..., :3] * a3
        vec = vec * (1 - a3) + vec_m * a3
        inside = alpha > 0.5
        mer[inside, 0], mer[inside, 1], mer[inside, 2], mer[inside, 3] = metal, emissive, rough, 0
        last_inside = inside
    rng = np.random.default_rng(seed)                                   # glints on the quartz chips only
    ys, xs = np.nonzero(last_inside)
    pick = rng.random(len(ys)) < GLINT
    gy, gx = ys[pick], xs[pick]
    ang = np.radians(rng.integers(0, 8, len(gy)) * 45.0)
    tilt = np.radians(rng.uniform(8, 14, len(gy)))
    vec[gy, gx] = np.stack([np.sin(tilt) * np.cos(ang), np.sin(tilt) * np.sin(ang), np.cos(tilt)], -1)
    mer[gy, gx, 2] = GLINT_ROUGH
    vec /= np.maximum(np.linalg.norm(vec, axis=-1, keepdims=True), 1e-6)
    out_c = np.empty((SZ, SZ, 4), np.uint8)
    out_c[..., :3] = np.clip(np.round(colour), 0, 255).astype(np.uint8)
    out_c[..., 3] = 255
    out_n = np.empty((SZ, SZ, 4), np.uint8)
    out_n[..., :3] = np.clip(np.round((vec + 1) / 2 * 255), 0, 255).astype(np.uint8)
    out_n[..., 3] = 255
    return out_c, out_n, np.clip(np.round(mer), 0, 255).astype(np.uint8), {
        "rock": src, "mineral_src": f"Patrix bones {'default' if variant == 0 else 'CTM ' + str(CTM_TILES[variant - 1])} + "
                                     f"Stratum quartz chips {QUARTZ_FLIPS[variant]}", "glints": int(len(gy))}


def rebuild_quartz(folder="rp11-140"):
    """Overwrite quartz_ore_0..3 in an UNDELIVERED RP-11 build with the bones + quartz composition."""
    packs = S.packs()
    terrain = S.terrain(packs)
    bases = base_variants(packs, terrain, "netherrack")
    ore_dir = B / folder / "textures/blocks/ores"
    infos = {}
    for v in range(4):
        c, n, m, info = compose_bones_and_quartz(v, bases[v], 9900 + v)
        Image.fromarray(c, "RGBA").save(ore_dir / f"quartz_ore_{v}.png", optimize=True)
        Image.fromarray(n, "RGBA").save(ore_dir / f"quartz_ore_{v}_n.png", optimize=True)
        Image.fromarray(m, "RGBA").save(ore_dir / f"quartz_ore_{v}_mer.png", optimize=True)
        infos[f"quartz_ore_{v}"] = info
    return infos


if __name__ == "__main__" and sys.argv[1] == "quartz":
    print(json.dumps(rebuild_quartz(), indent=1))
