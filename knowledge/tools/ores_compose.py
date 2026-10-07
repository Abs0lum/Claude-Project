#!/usr/bin/env python3
"""ores_compose.py — his 14:13 ore ruling: every ore = the Patrix ore MINERAL on OUR base block (stone / deepslate /
netherrack as our packs draw them), highly reflective, very low emissive, sand-like glint grains, colour + normal + MERS
in ONE pack (RP-11).

Why (measured 2026-10-02): the deepslate ore keys live in RP-04 and point at RP-04 images (RP-11's own deepslate copies
are orphans in a sub-folder no key names); the shipped sets are inconsistent — deepslate_diamond_ore subsurface 255 on
the whole block (milky grey), deepslate_iron_ore metalness 130 on 67 % of the block (the rock itself 'metal' = half the
diffuse light, dark grey) and the COAL normal map, gold_ore roughness ~4 on the whole block and the coal normal.

Recipe per ore (256 px, so our 128 base doubles pixel-for-pixel = it matches the plain blocks beside it):
  mask   = the mineral pixels of the Patrix 26.2 256 ore: metals -> Patrix F0 = 255 pixels (LabPBR metal flag) + saturated
           pixels; gems -> saturation; coal -> darker than the local rock; quartz -> bright + unsaturated; nether gold ->
           yellow hue. Dilated 1 px (keeps Patrix's painted outline), feathered.
  colour = our base x2 (nearest) under the Patrix mineral (alpha = mask).
  normal = our base normal x2 outside; Patrix mineral normal (Lesson #156) inside.
  MERS   = our base MERS x2 outside (rock stays rock); inside: metals M 200 (gold, copper) / 140 (iron), gems + coal +
           quartz M 0; roughness LOW (gems 0.06, metals 0.12, coal 0.30); emissive VERY LOW (8 / 255 ~ 3 %) on the
           mineral only; subsurface 0.
  glint  = 6 % of the mineral pixels: grains tilted 8-14 deg in 8 directions (the sand recipe), roughness 0.08,
           the mineral's own metalness (non-metal grains on gems + coal + quartz).
Usage: ores_compose.py preview OUT.png | ores_compose.py build OUT_DIR"""
import io
import json
import os
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, gaussian_filter, uniform_filter

sys.path.insert(0, "/home/claude/tools")
os.environ.setdefault("PW_STACK", "r1002i")
import mers_derive as MD  # noqa: E402
import pbr_round as PR  # noqa: E402
import stack_now as S  # noqa: E402

PB = "assets/minecraft/textures/block/"
# key (our terrain key) -> (Patrix file stem, base key, mineral class)
ORES = {
    "coal_ore": ("coal_ore", "stone", "coal"), "iron_ore": ("iron_ore", "stone", "iron"),
    "copper_ore": ("copper_ore", "stone", "copper"), "gold_ore": ("gold_ore", "stone", "gold"),
    "redstone_ore": ("redstone_ore", "stone", "gem"), "emerald_ore": ("emerald_ore", "stone", "gem"),
    "lapis_ore": ("lapis_ore", "stone", "gem"), "diamond_ore": ("diamond_ore", "stone", "gem"),
    "deepslate_coal_ore": ("deepslate_coal_ore", "deepslate", "coal"), "deepslate_iron_ore": ("deepslate_iron_ore", "deepslate", "iron"),
    "deepslate_copper_ore": ("deepslate_copper_ore", "deepslate", "copper"), "deepslate_gold_ore": ("deepslate_gold_ore", "deepslate", "gold"),
    "deepslate_redstone_ore": ("deepslate_redstone_ore", "deepslate", "gem"), "deepslate_emerald_ore": ("deepslate_emerald_ore", "deepslate", "gem"),
    "deepslate_lapis_ore": ("deepslate_lapis_ore", "deepslate", "gem"), "deepslate_diamond_ore": ("deepslate_diamond_ore", "deepslate", "gem"),
    "nether_gold_ore": ("nether_gold_ore", "netherrack", "ngold"), "quartz_ore": ("nether_quartz_ore", "netherrack", "quartz"),
}
MINERAL = {  # metalness, roughness, glint metal
    "gold": (200, 30, 200), "copper": (200, 30, 200), "ngold": (200, 30, 200), "iron": (140, 30, 140),
    "gem": (0, 15, 0), "quartz": (0, 15, 0), "coal": (0, 76, 0)}
EMISSIVE = 8
GLINT = 0.06
SZ = 256


def _z():
    return zipfile.ZipFile(PR.PATRIX256)


def _png(z, name):
    return np.asarray(Image.open(io.BytesIO(z.read(PB + name))).convert("RGBA"))


def mineral_mask(stem, cls, col, spec):
    rgb = col[..., :3].astype(float) / 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    if cls in ("iron", "copper", "gold"):
        m = (spec[..., 1] >= 230) | (sat > 0.28)
    elif cls == "gem":
        m = sat > 0.24
    elif cls == "coal":
        local = uniform_filter(lum, 25, mode="wrap")
        m = (lum < local - 0.10) & (sat < 0.25)
    elif cls == "quartz":                                                     # Patrix draws a bone fossil here
        m = (sat < 0.40) & (lum > 0.16)
    else:                                                                     # nether gold: yellow on red rock
        r, g = rgb[..., 0], rgb[..., 1]
        m = (g > 0.45) & (g > 0.62 * r) & (sat > 0.35)
    m = binary_dilation(m, iterations=1)
    from scipy.ndimage import label
    lab, n = label(m)
    sizes = np.bincount(lab.ravel())
    m &= np.isin(lab, [k for k in range(1, n + 1) if sizes[k] >= 6])          # drop single-pixel noise
    return m


def base_maps(P, T, key):
    path = S.paths_of(T[key][1])[0]
    p, f = S.find_image(P, path)
    col = Image.open(io.BytesIO(p.read(f))).convert("RGBA")
    stem = f.rsplit(".", 1)[0]
    ts = json.loads(p.read(stem + ".texture_set.json"))["minecraft:texture_set"]
    folder = stem.rsplit("/", 1)[0]

    def layer(name):
        for e in (".png", ".tga"):
            if p.has(f"{folder}/{name}{e}"):
                return Image.open(io.BytesIO(p.read(f"{folder}/{name}{e}"))).convert("RGBA")
        return None
    nrm = layer(ts["normal"]) if isinstance(ts.get("normal"), str) else None
    mer = layer(ts["metalness_emissive_roughness_subsurface"]) if isinstance(ts.get("metalness_emissive_roughness_subsurface"), str) else None
    up = lambda im: np.asarray(im.resize((SZ, SZ), Image.NEAREST)) if im is not None else None  # noqa: E731
    return up(col), up(nrm), up(mer), f"{p.name[:12]} {f}"


def compose(stem, cls, base, z, seed):
    col_p = _png(z, stem + ".png")
    spec = _png(z, stem + "_s.png")
    nrm_p = MD.normal_156(_png(z, stem + "_n.png"))
    m = mineral_mask(stem, cls, col_p, spec)
    a = gaussian_filter(m.astype(float), 0.6)
    a = np.clip(a * 1.25, 0, 1)
    a[m] = np.maximum(a[m], 0.85)
    bcol, bnrm, bmer, src = base
    colour = np.empty((SZ, SZ, 4), np.uint8)
    colour[..., :3] = np.round(bcol[..., :3] * (1 - a[..., None]) + col_p[..., :3] * a[..., None]).astype(np.uint8)
    colour[..., 3] = 255
    # normal: blend as vectors, re-normalise
    nb = bnrm[..., :3].astype(float) / 255 * 2 - 1 if bnrm is not None else np.dstack([np.zeros((SZ, SZ)), np.zeros((SZ, SZ)), np.ones((SZ, SZ))])
    nm = nrm_p[..., :3].astype(float) / 255 * 2 - 1
    n = nb * (1 - a[..., None]) + nm * a[..., None]
    # MERS: rock stays rock outside; mineral values inside
    mer = (bmer.astype(float) if bmer is not None else np.dstack([np.zeros((SZ, SZ)), np.zeros((SZ, SZ)), np.full((SZ, SZ), 200.0), np.zeros((SZ, SZ))])).copy()
    metal, rough, gmetal = MINERAL[cls]
    inside = a > 0.5
    mer[inside, 0] = metal
    mer[inside, 1] = EMISSIVE
    mer[inside, 2] = rough
    mer[inside, 3] = 0
    # glint grains (the sand recipe) on the mineral
    rng = np.random.default_rng(seed)
    ys, xs = np.nonzero(inside)
    pick = rng.random(len(ys)) < GLINT
    gy, gx = ys[pick], xs[pick]
    ang = np.radians(rng.integers(0, 8, len(gy)) * 45.0)
    tilt = np.radians(rng.uniform(8, 14, len(gy)))
    n[gy, gx] = np.stack([np.sin(tilt) * np.cos(ang), np.sin(tilt) * np.sin(ang), np.cos(tilt)], -1)
    mer[gy, gx, 0] = gmetal
    mer[gy, gx, 2] = 20
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
    normal = np.empty((SZ, SZ, 4), np.uint8)
    normal[..., :3] = np.clip(np.round((n + 1) / 2 * 255), 0, 255).astype(np.uint8)
    normal[..., 3] = 255
    return colour, normal, np.clip(np.round(mer), 0, 255).astype(np.uint8), {
        "mineral_pct": round(float(inside.mean() * 100), 1), "glint_px": int(len(gy)), "base": src}


def all_ores():
    P = S.packs()
    T = S.terrain(P)
    z = _z()
    bases = {k: base_maps(P, T, k) for k in ("stone", "deepslate", "netherrack")}
    out = {}
    for i, (key, (stem, bkey, cls)) in enumerate(ORES.items()):
        out[key] = compose(stem, cls, bases[bkey], z, 7000 + i)
    return out


def preview(path):
    res = all_ores()
    W = 160
    sheet = Image.new("RGB", (W * 6, (W + 16) * len(res) // 2 + 10), (16, 16, 20))
    d = ImageDraw.Draw(sheet)
    for i, (k, (c, n, m, info)) in enumerate(res.items()):
        x0, y0 = (i % 2) * 3 * W, (i // 2) * (W + 16)
        d.text((x0 + 4, y0 + 2), f"{k} · mineral {info['mineral_pct']}% · glints {info['glint_px']}", fill=(230, 230, 230))
        sheet.paste(Image.fromarray(c).resize((W, W), Image.NEAREST), (x0, y0 + 14))
        sheet.paste(Image.fromarray(n[..., :3]).resize((W, W), Image.NEAREST), (x0 + W, y0 + 14))
        sheet.paste(Image.fromarray(m[..., :3]).resize((W, W), Image.NEAREST), (x0 + 2 * W, y0 + 14))
    sheet.save(path)
    return {k: v[3] for k, v in res.items()}


if __name__ == "__main__":
    if sys.argv[1] == "preview":
        print(json.dumps(preview(sys.argv[2]), indent=1))


ORE_FILE = None


def _is_ore_file(name):
    """an ore image / map / set file of one of the 18 keys (any suffix), never a non-ore block."""
    import re
    keys = sorted(set(ORES) | {"nether_quartz_ore"}, key=len, reverse=True)
    return any(re.match(rf"^{k}(_[a-z0-9_]+)?\.(png|tga|jpg|texture_set\.json)$", name) for k in keys)


def build(rp11_src, rp11_dst, ver11, rp04_src, rp04_dst, ver04):
    import re
    import shutil
    B = Path("/home/claude/_build")
    for d in (rp11_dst, rp04_dst):
        assert not (B / d).exists(), f"never rebuild {d}"
    res = all_ores()
    rep = {"rp11_dropped": [], "rp04_dropped": [], "keys": {}}

    def ign11(dirp, names):
        if Path(dirp).name == "deepslate" and "textures/blocks" in dirp:
            rep["rp11_dropped"].extend(f"deepslate/{n}" for n in names)
            return names
        if dirp.endswith("textures/blocks"):
            out = [n for n in names if _is_ore_file(n)] + (["deepslate"] if "deepslate" in names else [])
            rep["rp11_dropped"].extend(n for n in out if n != "deepslate")
            return out
        return []
    shutil.copytree(B / rp11_src, B / rp11_dst, ignore=ign11)

    def ign04(dirp, names):
        if dirp.endswith("textures/blocks"):
            out = [n for n in names if _is_ore_file(n)]
            rep["rp04_dropped"].extend(out)
            return out
        return []
    shutil.copytree(B / rp04_src, B / rp04_dst, ignore=ign04)
    od = B / rp11_dst / "textures/blocks/ores"
    od.mkdir(parents=True)
    tt_path = B / rp11_dst / "textures/terrain_texture.json"
    tt = json.loads(tt_path.read_text())
    for key, (c, n, m, info) in res.items():
        Image.fromarray(c, "RGBA").save(od / f"{key}.png", optimize=True)
        Image.fromarray(n, "RGBA").save(od / f"{key}_n.png", optimize=True)
        Image.fromarray(m, "RGBA").save(od / f"{key}_mer.png", optimize=True)
        (od / f"{key}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
            "color": key, "normal": f"{key}_n", "metalness_emissive_roughness_subsurface": f"{key}_mer"}}, indent=1))
        tt["texture_data"][key] = {"textures": f"textures/blocks/ores/{key}"}
        rep["keys"][key] = info
    tt_path.write_text(json.dumps(tt, indent=1))
    t4p = B / rp04_dst / "textures/terrain_texture.json"
    t4 = json.loads(t4p.read_text())
    rep["rp04_keys_removed"] = [k for k in ORES if t4["texture_data"].pop(k, None) is not None]
    t4p.write_text(json.dumps(t4, indent=1))
    tl = B / rp04_dst / "textures/textures_list.json"
    if tl.exists():
        L = json.loads(tl.read_text())
        L2 = [p for p in L if not _is_ore_file(p.rsplit("/", 1)[-1] + ".png")]
        tl.write_text(json.dumps(L2, indent=1))
        rep["rp04_textures_list_removed"] = len(L) - len(L2)
    for d, ver, desc in ((rp11_dst, ver11, "Ores rebuilt: every ore's mineral (Patrix 26.2) on OUR stone / deepslate / netherrack, "
                          "256 px; minerals highly reflective (metals metallic, gems glossy), very low glow, glint grains; colour + depth + "
                          "shine maps all in this pack (deepslate ores moved here from RP-04)."),
                         (rp04_dst, ver04, "Ore textures removed (they live in RP-11 now).")):
        mp = B / d / "manifest.json"
        man = json.loads(re.sub(r"(?m)^\s*//.*$", "", mp.read_text(encoding="utf-8-sig")))
        old = ".".join(map(str, man["header"]["version"]))
        man["header"]["version"] = ver
        for mod in man["modules"]:
            mod["version"] = ver
        vs = ".".join(map(str, ver))
        man["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, man["header"]["name"])
        man["header"]["description"] = f"v{vs} (2026-10-02) {desc} Includes all of v{old}."
        assert "pbr" in (man.get("capabilities") or [])
        mp.write_text(json.dumps(man, indent=2))
    (Path("/home/claude/_docs/blocks") / "BUILD-ORES-1002L.json").write_text(json.dumps(rep, indent=1))
    return rep


if __name__ == "__main__" and sys.argv[1] == "build":
    r = build("rp11-138", "rp11-139", [1, 3, 39], "rp04-154", "rp04-155", [1, 3, 155])
    print(json.dumps({k: (v if k != "keys" else len(v)) for k, v in r.items()}, indent=1)[:3000])
