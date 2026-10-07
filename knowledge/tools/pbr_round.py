#!/usr/bin/env python3
"""pbr_round.py — the BLOCK PBR ROUND (his 17:38 report + 17:52 "fix all of these now", D-C421 / D-C422).

Everything is written into a STAGING tree, one folder per pack that will get a new version:
    _staging/pbr/<PACK>/textures/blocks/...      (only new / replaced files; colour images are NEVER changed except the
                                                 16 grass sides of phase 2, which are new .tga files)
The pack builders (build_pbr_round.py) copy the last delivered build of each pack and lay the staging on top.

Phase 1  SHADOW   a higher pack ships a plain image at a path whose texture set lives in a LOWER pack (797 paths): the game
                  takes the top pack's image and the set below is never used. The TOP pack gets its own <path>.texture_set.json
                  (colour = its own image, so what he sees does not change) + copies of the lower set's normal / heightmap /
                  MERS layers next to it (resampled to the colour's size when they differ). A layer name the top pack already
                  uses for different bytes gets a `_pbr` suffix (never overwrites).
Report: _docs/blocks/PBR-ROUND.json (one line per path per phase)."""
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import stack_now as SN  # noqa: E402

STAGE = ROOT / "_staging/pbr"
CENSUS = ROOT / "_docs/blocks/BLOCK-PBR-CENSUS.json"
REPORT = ROOT / "_docs/blocks/PBR-ROUND.json"
EXT = (".tga", ".png", ".jpg", ".jpeg")
LAYERS = ("normal", "heightmap", "metalness_emissive_roughness", "metalness_emissive_roughness_subsurface")
PACK_KEY = {"RP-04 1.3.144": "rp04", "RP-05 1.3.51": "rp05", "RP-10 1.3.42": "rp10", "RP-11 1.3.35": "rp11",
            "RP-01 1.3.107": "rp01", "RP-03 1.3.60": "rp03", "RP-08 1.4.9": "rp08"}


def find_layer(p, base_dir, name):
    for e in EXT:
        rel = f"{base_dir}/{name}{e}"
        if p.has(rel):
            return rel
    return None


def image_of(p, path):
    for e in EXT:
        if p.has(path + e):
            return path + e
    return None


def resample(im, size, kind):
    """layer -> colour size. Normal: bilinear then re-normalised; MERS / height: box (down) or nearest (up)."""
    if im.size == size:
        return im
    w, h = size
    if w != h and h % w == 0 and im.size[0] == im.size[1]:
        # a flipbook strip (frames stacked vertically, e.g. blast_furnace_front_on 256x768) with one square layer:
        # the layer is scaled to one frame and TILED down the strip (stretching it would smear one frame over all)
        frame = resample(im, (w, w), kind)
        strip = Image.new(frame.mode, size)
        for k in range(h // w):
            strip.paste(frame, (0, k * w))
        return strip
    if kind == "normal":
        a = np.asarray(_bands_resize(im.convert("RGBA"), size, Image.BILINEAR)).astype(float)
        v = a[..., :3] / 255 * 2 - 1
        n = np.linalg.norm(v, axis=-1, keepdims=True)
        n[n == 0] = 1
        a[..., :3] = np.round((v / n + 1) / 2 * 255)
        return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    res = Image.BOX if im.size[0] > size[0] else Image.NEAREST
    return _bands_resize(im.convert("RGBA"), size, res)


def _bands_resize(im, size, res):
    """18:1x: PIL resizes RGBA PREMULTIPLIED by alpha — a MERS whose alpha (subsurface) is 0 came out ALL ZERO (the bug in 157
    shipped block MERS maps too). Every channel is resized on its own as a plain grey band.
    D-C469 (2026-10-02): a band that is BINARY (only 0 and 255, e.g. the alpha of a cut-out roof crop, or an on/off
    subsurface) stays binary — it is resized, then thresholded at 128. Resizing the 35 roof / ramp crop textures with a
    soft alpha (round 1002f) moved every witnessed cut line under alpha_test."""
    bands = []
    for band in im.split():
        out = band.resize(size, res)
        if not any(band.histogram()[1:255]):                  # only 0 / 255 in the source band
            out = out.point(lambda v: 255 if v >= 128 else 0)
        bands.append(out)
    return Image.merge(im.mode, bands)


class Stage:
    def __init__(self):
        self.files = {}          # (pack_key, rel) -> bytes

    def put(self, key, rel, data):
        self.files[(key, rel)] = data

    def has(self, key, rel):
        return (key, rel) in self.files

    def get(self, key, rel):
        return self.files.get((key, rel))

    def write(self):
        for (key, rel), data in self.files.items():
            out = STAGE / key / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
        return len(self.files)


def png_bytes(im):
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return b.getvalue()


def place_layer(top, tk, stage, base_dir, name, ext, data):
    """put a layer file into the top pack's staging under `name` (never overwrite different bytes). -> final name"""
    for cand in (name, f"{name}_pbr", f"{name}_pbr2", f"{name}_pbr3"):
        rel = f"{base_dir}/{cand}{ext}"
        existing = image_of(top, f"{base_dir}/{cand}")
        staged = stage.get(tk, rel)
        if existing and top.read(existing) == data and staged is None:
            return cand                                   # the top pack already holds exactly this layer
        if staged is not None:
            if staged == data:
                return cand
            continue
        if existing:
            continue                                      # different bytes under that name in the top pack
        stage.put(tk, rel, data)
        return cand
    raise RuntimeError(f"no free layer name for {base_dir}/{name}")


def phase1(P, stage, report):
    by = {p.name: p for p in P}
    rows = json.loads(CENSUS.read_text())["rows"]
    done = set()
    for r in rows:
        if r["path"] in done or not any(s.startswith("SHADOWED_PNG") for s in r["status"]):
            continue
        done.add(r["path"])
        path = r["path"]
        top, src = by[r["img_packs"][0]], by[r["set_pack"]]
        tk = PACK_KEY[top.name]
        src_set = src.json(path + ".texture_set.json")
        ts = src_set["minecraft:texture_set"]
        base_dir, stem = path.rsplit("/", 1)
        col_rel = image_of(top, path)
        col = Image.open(io.BytesIO(top.read(col_rel)))
        new = {"color": stem}
        notes = []
        for layer in LAYERS:
            v = ts.get(layer)
            if v is None:
                continue
            if not isinstance(v, str) or v.startswith("#"):
                new[layer] = v                     # a uniform value travels as it is
                continue
            lrel = find_layer(src, base_dir, v)
            if not lrel:
                notes.append(f"{layer} {v} missing in {src.name}")
                continue
            raw = src.read(lrel)
            im = Image.open(io.BytesIO(raw))
            if im.size == col.size:
                data, ext, name = raw, "." + lrel.rsplit(".", 1)[1], v
            else:
                notes.append(f"{layer} resampled {im.size}->{col.size}")
                im2 = resample(im, col.size, "normal" if layer == "normal" else "mers")
                data, ext, name = png_bytes(im2), ".png", f"{v}_{col.size[0]}x{col.size[1]}"
            new[layer] = place_layer(top, tk, stage, base_dir, name, ext, data)
        out = {"format_version": src_set.get("format_version", "1.21.30"), "minecraft:texture_set": new}
        stage.put(tk, path + ".texture_set.json", json.dumps(out, indent=1).encode())
        src_col = image_of(src, path)
        report.append({"phase": 1, "path": path, "pack": top.name, "from": src.name, "set": new, "notes": notes,
                       "colour_identical": bool(src_col) and top.read(col_rel) == src.read(src_col)})
    return len(done)


PATRIX256 = ROOT / "_intake/patrix262_256/Patrix_26.2_256x_basic.zip"
GRASS_CTM = "assets/minecraft/optifine/ctm/patrix/grass/block/"
DROP = {}                      # pack_key -> set of files the new build must NOT carry (moved aside, never deleted)


def tga_bytes(im):
    b = io.BytesIO()
    im.save(b, "TGA", compression=None)
    return b.getvalue()


def phase2(P, stage, report):
    """GRASS SIDES (G1 = a: the vanilla grass block). Mojang's grass_side.tga (bedrock-samples, fetched 17:56): the ALPHA channel
    is the biome-tint mask — fringe pixels grey with alpha 255 (tinted), dirt pixels brown with alpha 0 (drawn as they are).
    Our RP-04 grass_block_side_v0..v15 are the Java BASE only (alpha 255 everywhere, Java's overlay never merged).
    v_k matches Patrix CTM side_default tile k+1 (mean |diff| 11.5–18.5 vs >= 24.8 for the next best) -> rebuilt as
    grass_block_side_v{k}.tga: RGB = our base, the Patrix overlay tile k+1 laid on its alpha (binary in the source); alpha =
    255 on the overlay, 0 elsewhere. Texture set per variant: Patrix tile k+1 _n / _s, overlay _n / _s on the fringe, by #156."""
    import zipfile
    import mers_derive as MD
    Z = zipfile.ZipFile(PATRIX256)

    def zrgba(name):
        return np.asarray(Image.open(io.BytesIO(Z.read(GRASS_CTM + name))).convert("RGBA"))
    top = next(p for p in P if p.name.startswith("RP-04"))
    for v in range(16):
        k = v + 1
        rel = f"textures/blocks/grass_block_side_v{v}"
        base = np.asarray(Image.open(io.BytesIO(top.read(rel + ".png"))).convert("RGBA")).copy()
        ov = zrgba(f"side_overlay/{k}.png")
        mask = ov[..., 3] >= 128
        out = base.copy()
        out[mask, :3] = ov[mask, :3]
        out[..., 3] = np.where(mask, 255, 0).astype(np.uint8)
        stage.put("rp04", rel + ".tga", tga_bytes(Image.fromarray(out, "RGBA")))
        DROP.setdefault("rp04", set()).add(rel + ".png")
        n_base, n_ov = MD.normal_156(zrgba(f"side_default/{k}_n.png")), MD.normal_156(zrgba(f"side_overlay/{k}_n.png"))
        s_base, s_ov = MD.mers_156(zrgba(f"side_default/{k}_s.png")), MD.mers_156(zrgba(f"side_overlay/{k}_s.png"))
        nrm = np.where(mask[..., None], n_ov, n_base)
        mer = np.where(mask[..., None], s_ov, s_base)
        stem = rel.rsplit("/", 1)[1]
        stage.put("rp04", rel + "_n.png", png_bytes(Image.fromarray(nrm.astype(np.uint8), "RGBA")))
        stage.put("rp04", rel + "_mer.png", png_bytes(Image.fromarray(mer.astype(np.uint8), "RGBA")))
        ts = {"format_version": "1.21.30", "minecraft:texture_set": {
            "color": stem, "normal": stem + "_n", "metalness_emissive_roughness_subsurface": stem + "_mer"}}
        stage.put("rp04", rel + ".texture_set.json", json.dumps(ts, indent=1).encode())
        report.append({"phase": 2, "path": rel, "pack": "RP-04", "tint_px": int(mask.sum()),
                       "tint_share": round(float(mask.mean()), 3), "patrix_tile": k})
    return 16


# ---------------------------------------------------------------- phase 3: textures that never had maps
MATCH = ROOT / "_docs/blocks/PATRIX-MATCH.json"
MATCH_MAX = 10.0             # thumbnail distance accepted as "this is the Patrix picture" (d < 4: identical; 4–10: graded copy)
# material classes: (token set, metal 0-255, roughness 0-255, subsurface 0-255, target mean normal slope)
#   slopes calibrated on Patrix's own _n: cobblestone 0.42 · dirt 0.55 · stone bricks 0.35 · oak planks 0.11 · leaves 0.47 ·
#   poppy 0.43 · iron block 0.31
CLASSES = [
    ("metal", {"iron", "gold", "copper", "netherite", "chain", "lantern", "anvil", "rail", "rails", "cauldron", "hopper",
               "bell", "lightning", "rod", "grate", "bulb"}, 255, 115, 0, 0.30),
    ("glass", {"glass", "pane"}, 0, 25, 0, 0.05),
    ("ice", {"ice"}, 0, 40, 60, 0.12),
    ("snow", {"snow", "powder"}, 0, 230, 110, 0.20),
    ("plant", {"leaf", "leaves", "flower", "plant", "grass", "fern", "vine", "vines", "sapling", "mushroom", "crop",
               "carrots", "carrot", "potatoes", "potato", "wheat", "beetroot", "beetroots", "bush", "kelp", "seagrass",
               "moss", "lily", "waterlily", "azalea", "dripleaf", "roots", "reeds", "sugar", "bamboo", "cactus",
               "torchflower", "petals", "peony", "lilac", "rose", "tulip", "orchid", "allium", "daisy", "poppy",
               "dandelion", "cornflower", "tallgrass", "skirt", "sprouts", "wart", "berry", "berries", "pitcher",
               "spore", "blossom", "pickle", "melon", "pumpkin", "stem", "cocoa", "hay", "chorus", "eyeblossom"},
     0, 190, 140, 0.40),
    ("wool", {"wool", "carpet", "bed"}, 0, 245, 40, 0.25),
    ("wood", {"log", "planks", "plank", "wood", "bark", "hyphae", "door", "trapdoor", "barrel", "bookshelf",
              "crafting", "chest", "deck", "ramp", "fence", "sign", "lectern", "loom", "composter", "beehive",
              "scaffolding", "ladder", "jukebox", "noteblock", "table", "shelf", "smithing", "fletching"},
     0, 205, 10, 0.15),
    ("soil", {"dirt", "sand", "gravel", "soil", "podzol", "mycelium", "nylium", "path", "farmland", "mud", "clay",
              "coarse", "rooted", "suspicious"}, 0, 235, 5, 0.50),
    ("stone", {"stone", "cobble", "cobblestone", "brick", "bricks", "deepslate", "andesite", "diorite", "granite",
               "tuff", "basalt", "blackstone", "ore", "terracotta", "concrete", "sandstone", "prismarine", "quartz",
               "purpur", "end", "netherrack", "obsidian", "calcite", "dripstone", "bedrock", "furnace", "smoker",
               "magma", "glowstone", "lantern"}, 0, 215, 0, 0.40),
]
EMISSIVE = {"fire", "lava", "magma", "glowstone", "sea_lantern", "shroomlight", "torch", "lit", "on", "froglight",
            "campfire", "candle", "lamp", "glow", "redstone_torch", "soul_fire", "beacon", "conduit", "respawn"}
SKIP_PACKS = {"Markers RP 0.2.1", "StripMine RP 3.0.1"}   # debug marker blocks; third-party pack we do not rebuild


def tokens_of(path):
    import re
    stem = path.rsplit("/", 1)[1]
    return set(t for t in re.split(r"[^a-z]+", stem.lower()) if t), stem


def material_of(path):
    toks, stem = tokens_of(path)
    for name, keys, m, r, sss, slope in CLASSES:
        if toks & keys:
            return name, m, r, sss, slope
    return "default", 0, 200, 10, 0.35


def derive_normal(rgba, slope):
    """height = luminance (alpha-masked), slopes scaled so their mean magnitude = the class's Patrix-calibrated slope.
    Convention measured on Patrix _n (cobblestone / dirt corr 0.46): R ~ -dh/dcolumn, G ~ -dh/drow."""
    from scipy import ndimage
    a = rgba.astype(float)
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]) / 255
    lum = ndimage.gaussian_filter(lum, max(0.6, rgba.shape[1] / 256))
    gx, gy = ndimage.sobel(lum, 1), ndimage.sobel(lum, 0)
    op = a[..., 3] > 0
    mag = np.sqrt(gx * gx + gy * gy)
    k = slope / max(1e-6, float(mag[op].mean() if op.any() else mag.mean()))
    x, y = -gx * k, -gy * k
    n = np.stack([x, y, np.ones_like(x)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    out = np.zeros(rgba.shape, np.uint8)
    out[..., :3] = np.round((n + 1) / 2 * 255).clip(0, 255)
    out[..., 3] = 255
    return out


def derive_mers(rgba, path):
    name, m, r, sss, _ = material_of(path)
    toks, stem = tokens_of(path)
    a = rgba.astype(float)
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]) / 255
    out = np.zeros(rgba.shape, np.uint8)
    if name == "metal":   # metal where the picture is bright metal; dark gaps / rust / wood parts stay dielectric
        out[..., 0] = np.where(lum > 0.35, 255, 0)
    rough = np.full(lum.shape, float(r))
    local = np.asarray(Image.fromarray((lum * 255).astype(np.uint8)).resize((max(1, lum.shape[1] // 4), max(1, lum.shape[0] // 4)),
                                                                          Image.BOX).resize(lum.shape[::-1], Image.BILINEAR)) / 255
    rough += np.clip((local - lum) * 255 * 0.3, -20, 20)       # crevices rougher (same nudge as the mob derive)
    out[..., 2] = rough.clip(0, 255).round()
    out[..., 3] = sss
    if toks & EMISSIVE or any(e in stem for e in ("fire", "lava", "glowstone", "lantern", "froglight", "shroomlight")):
        out[..., 1] = np.where(lum > 0.55, np.round((lum - 0.55) / 0.45 * 255), 0).clip(0, 255)
    return out, name


def phase3(P, stage, report):
    import zipfile
    import mers_derive as MD
    Z = zipfile.ZipFile(PATRIX256)
    names = set(Z.namelist())
    by = {p.name: p for p in P}
    match = json.loads(MATCH.read_text())
    n_done = 0
    for path, mt in sorted(match.items()):
        if mt["pack"] in SKIP_PACKS:
            report.append({"phase": 3, "path": path, "pack": mt["pack"], "skipped": "debug marker / third-party pack"})
            continue
        top = by[mt["pack"]]
        tk = PACK_KEY[top.name]
        col_rel = mt["file"]
        col_im = Image.open(io.BytesIO(top.read(col_rel)))
        rgba = np.asarray(col_im.convert("RGBA"))
        size = col_im.size
        base_dir, stem = path.rsplit("/", 1)
        src = "derived"
        nrm = mer = None
        if mt["d"] < MATCH_MAX:
            b = mt["best"][:-4]
            if b + "_n.png" in names:
                nrm = MD.normal_156(np.asarray(Image.open(io.BytesIO(Z.read(b + "_n.png"))).convert("RGBA")))
                nrm = np.asarray(resample(Image.fromarray(nrm, "RGBA"), size, "normal"))
            if b + "_s.png" in names:
                mer = MD.mers_156(np.asarray(Image.open(io.BytesIO(Z.read(b + "_s.png"))).convert("RGBA")))
                mer = np.asarray(resample(Image.fromarray(mer, "RGBA"), size, "mers"))
            src = "patrix " + mt["best"].split("/minecraft/")[1]
        cls = material_of(path)
        if nrm is None:
            nrm = derive_normal(rgba, cls[4])
        if mer is None:
            mer, _ = derive_mers(rgba, path)
        ln = place_layer(top, tk, stage, base_dir, stem + "_n", ".png", png_bytes(Image.fromarray(nrm.astype(np.uint8), "RGBA")))
        lm = place_layer(top, tk, stage, base_dir, stem + "_mer", ".png", png_bytes(Image.fromarray(mer.astype(np.uint8), "RGBA")))
        ts = {"format_version": "1.21.30", "minecraft:texture_set": {
            "color": stem, "normal": ln, "metalness_emissive_roughness_subsurface": lm}}
        stage.put(tk, path + ".texture_set.json", json.dumps(ts, indent=1).encode())
        report.append({"phase": 3, "path": path, "pack": top.name, "source": src, "d": mt["d"], "class": cls[0]})
        n_done += 1
    return n_done


# ---------------------------------------------------------------- phase 4: repair what the sets point at
SET_PACKS = {"RP-04 1.3.144", "RP-05 1.3.51", "RP-10 1.3.42", "RP-11 1.3.35", "RP-01 1.3.107", "RP-03 1.3.60", "RP-08 1.4.9"}
SHINY_OK = {"metal", "glass", "ice"}


def effective_set(P, stage, path):
    """(pack, set dict, staged?) of the set the game will use for `path` after this round: the top pack holding the image
    (or, if none of ours, the top pack holding a set)."""
    for p in P:
        if p.name not in PACK_KEY:
            continue
        k = PACK_KEY[p.name]
        st = stage.get(k, path + ".texture_set.json")
        if st is not None:
            return p, json.loads(st)["minecraft:texture_set"], True
        if image_of(p, path) or p.has(path + ".texture_set.json"):
            if p.has(path + ".texture_set.json"):
                return p, p.json(path + ".texture_set.json")["minecraft:texture_set"], False
            return p, None, False
    return None, None, False


def read_layer(p, stage, base_dir, name):
    k = PACK_KEY[p.name]
    for e in EXT:
        st = stage.get(k, f"{base_dir}/{name}{e}")
        if st is not None:
            return Image.open(io.BytesIO(st))
    rel = find_layer(p, base_dir, name)
    return Image.open(io.BytesIO(p.read(rel))) if rel else None


def phase4(P, stage, report):
    """for every block path drawn in his stack: the set the game will use (after phases 1–3) is checked and repaired —
    MERS all zero / roughness mean < 20 on a material that is not metal / glass / ice (the premultiplied-resize bug: mirror
    shine) -> rebuilt from Patrix #156 (picture match d < 10) else derived; normal flat (std < 2) -> rebuilt the same way;
    a layer of another size than the colour -> resampled per channel (strips tiled per frame). New layer files get a
    `_fix` name in the set's own pack; the set is re-written there."""
    import zipfile
    import mers_derive as MD
    import patrix_match as PM
    Z = zipfile.ZipFile(PATRIX256)
    names = set(Z.namelist())
    keys, th = PM.index()
    rows = json.loads(CENSUS.read_text())["rows"]
    seen, n_fix = set(), 0
    for r in rows:
        path = r["path"]
        if path in seen:
            continue
        seen.add(path)
        p, ts, staged = effective_set(P, stage, path)
        if p is None or ts is None or p.name not in SET_PACKS:
            continue
        base_dir, stem = path.rsplit("/", 1)
        col_name = ts.get("color") if isinstance(ts.get("color"), str) else None
        col = read_layer(p, stage, base_dir, col_name) if col_name else None
        if col is None:
            continue
        rgba = np.asarray(col.convert("RGBA"))
        size = col.size
        cls = material_of(path)
        mk = next((k for k in ts if k.startswith("metalness")), None)
        fixes = []
        new = dict(ts)
        patrix = None

        def patrix_maps():
            nonlocal patrix
            if patrix is None:
                a = PM.thumb(col)
                d = np.abs(th[..., :3] - a[None, ..., :3]).mean(axis=(1, 2, 3)) + np.abs(th[..., 3] - a[None, ..., 3]).mean(axis=(1, 2)) * 0.5
                i = int(np.argmin(d))
                patrix = (keys[i][:-4], float(d[i])) if d[i] < MATCH_MAX else (None, float(d[i]))
            return patrix
        # MERS
        if mk and isinstance(ts[mk], str) and not ts[mk].startswith("#"):
            m = read_layer(p, stage, base_dir, ts[mk])
            ma = np.asarray(m.convert("RGBA")).astype(float) if m is not None else None
            op = rgba[..., 3] > 0
            broken = ma is None or (ma[..., :3].max() == 0 and ma[..., 3].max() == 0)
            if ma is not None and not broken and ma.shape[:2] == rgba.shape[:2]:
                broken = cls[0] not in SHINY_OK and ma[..., 2][op].mean() < 20 and ma[..., 0][op].mean() < 128
            elif ma is not None and not broken:
                broken = cls[0] not in SHINY_OK and ma[..., 2].mean() < 20 and ma[..., 0].mean() < 128
            if broken:
                b, d = patrix_maps()
                if b and b + "_s.png" in names:
                    mer = MD.mers_156(np.asarray(Image.open(io.BytesIO(Z.read(b + "_s.png"))).convert("RGBA")))
                    mer = np.asarray(resample(Image.fromarray(mer, "RGBA"), size, "mers"))
                    how = "patrix"
                else:
                    mer, _ = derive_mers(rgba, path)
                    how = "derived"
                new[mk] = place_layer(p, PACK_KEY[p.name], stage, base_dir, stem + "_mer_fix", ".png",
                                      png_bytes(Image.fromarray(mer.astype(np.uint8), "RGBA")))
                fixes.append(f"MERS {'missing' if ma is None else 'blank/mirror'} -> {how}")
            elif m is not None and m.size != size:
                im2 = resample(m, size, "mers")
                new[mk] = place_layer(p, PACK_KEY[p.name], stage, base_dir, f"{ts[mk]}_{size[0]}x{size[1]}", ".png", png_bytes(im2))
                fixes.append(f"MERS resampled {m.size}->{size}")
        # normal
        if isinstance(ts.get("normal"), str):
            n = read_layer(p, stage, base_dir, ts["normal"])
            na = np.asarray(n.convert("RGB")).astype(float) if n is not None else None
            flat = na is None or (na[..., 0].std() < 2 and na[..., 1].std() < 2)
            if flat:
                b, d = patrix_maps()
                if b and b + "_n.png" in names:
                    nrm = MD.normal_156(np.asarray(Image.open(io.BytesIO(Z.read(b + "_n.png"))).convert("RGBA")))
                    nrm = np.asarray(resample(Image.fromarray(nrm, "RGBA"), size, "normal"))
                    how = "patrix"
                else:
                    nrm, how = derive_normal(rgba, cls[4]), "derived"
                new["normal"] = place_layer(p, PACK_KEY[p.name], stage, base_dir, stem + "_n_fix", ".png",
                                            png_bytes(Image.fromarray(nrm.astype(np.uint8), "RGBA")))
                fixes.append(f"normal {'missing' if na is None else 'flat'} -> {how}")
            elif n.size != size:
                im2 = resample(n, size, "normal")
                new["normal"] = place_layer(p, PACK_KEY[p.name], stage, base_dir, f"{ts['normal']}_{size[0]}x{size[1]}", ".png",
                                            png_bytes(im2))
                fixes.append(f"normal resampled {n.size}->{size}")
        elif "heightmap" not in ts:
            b, d = patrix_maps()
            if b and b + "_n.png" in names:
                nrm = MD.normal_156(np.asarray(Image.open(io.BytesIO(Z.read(b + "_n.png"))).convert("RGBA")))
                nrm = np.asarray(resample(Image.fromarray(nrm, "RGBA"), size, "normal"))
                how = "patrix"
            else:
                nrm, how = derive_normal(rgba, cls[4]), "derived"
            new["normal"] = place_layer(p, PACK_KEY[p.name], stage, base_dir, stem + "_n_fix", ".png",
                                        png_bytes(Image.fromarray(nrm.astype(np.uint8), "RGBA")))
            fixes.append(f"no depth layer -> {how}")
        if fixes:
            full = {"format_version": "1.21.30", "minecraft:texture_set": new}
            stage.put(PACK_KEY[p.name], path + ".texture_set.json", json.dumps(full, indent=1).encode())
            report.append({"phase": 4, "path": path, "pack": p.name, "fixes": fixes, "class": cls[0]})
            n_fix += 1
    return n_fix


def main(phases=(1,)):
    P = SN.packs()
    stage, report = Stage(), []
    if 1 in phases:
        print("phase 1 SHADOW:", phase1(P, stage, report), "paths")
    if 2 in phases:
        print("phase 2 GRASS SIDES:", phase2(P, stage, report))
    if 3 in phases:
        print("phase 3 NEW MAPS:", phase3(P, stage, report))
    if 4 in phases:
        print("phase 4 REPAIR:", phase4(P, stage, report))
    n = stage.write()
    REPORT.write_text(json.dumps(report, indent=1))
    (STAGE / "DROP.json").write_text(json.dumps({k: sorted(v) for k, v in DROP.items()}, indent=1))
    print("staged files", n)


if __name__ == "__main__":
    main(tuple(int(x) for x in sys.argv[1:]) or (1,))
