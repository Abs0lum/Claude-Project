#!/usr/bin/env python3
"""build_round_1002h.py — his 11:23: Q5 = c (vanilla vines sway in the wind AND move when walked into), Q6 = c (build both;
"drop the old vines to pay for it"), Q7 = yes (desert owl 'sane' -> 'sand').

pw:vine is a custom block: no engine motion. So:
  WIND   — every pw:vine key becomes a 16-frame flipbook (always playing): a gentle ripple travelling DOWN the vine.
  RUSTLE — new keys pw_vine_r{i} / pw_vine_extra_r: a fast, bigger shake; BP-02 pw_vine.js flips state pw:r on the
           touched vine + neighbours for 2 s and the block's material permutation switches to the rustle key.
Wave model (h = 0 bottom row .. 1 top row, x = 0..1 across, theta = 2 pi frame / 16; px of the 256 source):
  wind   dx(h) = 4 * [sin(theta + 2 pi h) + 0.3 sin(2 theta + 4 pi h + 1.1)]      dy(x) = 1.2 sin(theta + 2 pi x)
  rustle dx(h) = 10 * [sin(2 theta + 2 pi h) + 0.45 sin(3 theta - 4 pi h + 0.7)]   dy(x) = 3.5 sin(3 theta + 4 pi x)
Every term is a whole number of periods in h and in x, and sampling wraps both ways, so stacked / side-by-side vine
blocks join in every frame (same idea as the kelp stem). Colour sampled premultiplied (no dark fringes); normal + MERS
moved by the same map. Built from the 256 sources (rp01-113), each frame downscaled to 192 (the atlas ruling):
strips 192 x 3072, colour + normal + MERS + texture set.
Build dirs (new, never rebuilt): rp01-115 (RP-01 1.3.115), rp04-153 (RP-04 1.3.153), bp02-203 (BP-02 1.3.203),
stripmine-bp-1313 (StripMine BP 1.3.13). Report _docs/blocks/BUILD-1002H.json + _docs/flora/VINE-SWAY-PREVIEW.gif."""
import json
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import pbr_round as PR  # noqa: E402

B = ROOT / "_build"
SRC256 = B / "rp01-113/textures/blocks/pw_vine"
FR, SZ, OUT_SZ = 16, 256, 192
VARS = [f"vine_v{i}" for i in range(12)] + ["vine_extra"]
LAYERS = {"vine_extra": ("vine_extra_n", "vine_extra_mer")}
for i in range(12):
    LAYERS[f"vine_v{i}"] = (f"vine_v{i}_n256", f"vine_v{i}_mer256")
MODES = {  # suffix: (dx amp, dx fn, dy amp, dy fn, ticks per frame)
    "w": (4.0, lambda t, h: np.sin(t + 2 * np.pi * h) + 0.3 * np.sin(2 * t + 4 * np.pi * h + 1.1),
          1.2, lambda t, x: np.sin(t + 2 * np.pi * x), 5),
    "r": (10.0, lambda t, h: np.sin(2 * t + 2 * np.pi * h) + 0.45 * np.sin(3 * t - 4 * np.pi * h + 0.7),
          3.5, lambda t, x: np.sin(3 * t + 4 * np.pi * x), 2),
}
DST = {"RP-01": ("rp01-114", "rp01-115", [1, 3, 115]), "RP-04": ("rp04-152", "rp04-153", [1, 3, 153]),
       "BP-02": ("bp02-202", "bp02-203", [1, 3, 203]), "SM-BP": ("stripmine-bp-1312", "stripmine-bp-1313", [1, 3, 13])}
MAT = {"render_method": "alpha_test", "tint_method": "default_foliage", "ambient_occlusion": False, "face_dimming": False}


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig")))


def warp(a, dxa, dxf, dya, dyf, t):
    """out(y, x) = a(y - dy(x), x - dx(y)), bilinear, wrapping both ways. a: float HxWxC."""
    y = np.arange(SZ)
    h = (SZ - 1 - y) / (SZ - 1)
    x = np.arange(SZ) / SZ
    dx = dxa * dxf(t, h)                       # per row
    dy = dya * dyf(t, x)                       # per column
    Y = y[:, None] - dy[None, :]
    X = np.arange(SZ)[None, :] - dx[:, None]
    out = np.empty_like(a)
    for c in range(a.shape[2]):
        out[..., c] = map_coordinates(a[..., c], [Y, X], order=1, mode="grid-wrap")
    return out


def down_colour(fr):
    """256 -> 192 premultiplied (alpha-weighted colour, no fringes)."""
    pm = fr.copy()
    pm[..., :3] *= pm[..., 3:4]
    bands = [np.asarray(Image.fromarray(pm[..., c].astype(np.float32), "F").resize((OUT_SZ, OUT_SZ), Image.LANCZOS))
             for c in range(4)]
    o = np.stack(bands, -1).clip(0, 1)
    al = o[..., 3:4]
    o[..., :3] = np.where(al > 1e-4, o[..., :3] / np.maximum(al, 1e-4), 0).clip(0, 1)
    return np.round(o * 255).astype(np.uint8)


def strips(name):
    col = np.asarray(Image.open(SRC256 / f"{name}.png").convert("RGBA")).astype(float) / 255
    nn, mm = LAYERS[name]
    nrm = np.asarray(Image.open(SRC256 / f"{nn}.png").convert("RGBA")).astype(float)
    mer = np.asarray(Image.open(SRC256 / f"{mm}.png").convert("RGBA")).astype(float)
    assert col.shape[:2] == nrm.shape[:2] == mer.shape[:2] == (SZ, SZ), name
    pm = col.copy()
    pm[..., :3] *= pm[..., 3:4]
    res = {}
    for mode, (dxa, dxf, dya, dyf, _) in MODES.items():
        C, N, M = [], [], []
        for f in range(FR):
            t = 2 * np.pi * f / FR
            s = warp(pm, dxa, dxf, dya, dyf, t)
            al = s[..., 3:4]
            s[..., :3] = np.where(al > 1e-4, s[..., :3] / np.maximum(al, 1e-4), 0)
            C.append(down_colour(s))
            n8 = Image.fromarray(np.clip(np.round(warp(nrm, dxa, dxf, dya, dyf, t)), 0, 255).astype(np.uint8), "RGBA")
            m8 = Image.fromarray(np.clip(np.round(warp(mer, dxa, dxf, dya, dyf, t)), 0, 255).astype(np.uint8), "RGBA")
            N.append(np.asarray(PR.resample(n8, (OUT_SZ, OUT_SZ), "normal")))
            M.append(np.asarray(PR.resample(m8, (OUT_SZ, OUT_SZ), "mers")))
        res[mode] = tuple(np.concatenate(L, 0) for L in (C, N, M))
    return res


def manifest(d, ver, desc):
    mp = d / "manifest.json"
    m = jl(mp)
    old = ".".join(map(str, m["header"]["version"]))
    m["header"]["version"] = ver
    for mod in m["modules"]:
        mod["version"] = ver
    vs = ".".join(map(str, ver))
    m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, m["header"]["name"])
    m["header"]["description"] = f"v{vs} (2026-10-02) {desc} Includes all of v{old}."
    mp.write_text(json.dumps(m, indent=2))
    return m


def main():
    for k, (s, d, _) in DST.items():
        assert (B / s).is_dir(), s
        assert not (B / d).exists(), f"never rebuild {d}"
    rep = {}

    # ---------------- RP-01 1.3.115
    s, d, ver = DST["RP-01"]
    keep_still = {"vine_v0.png", "vine_v0_n256.png", "vine_v0_mer256.png", "vine_v0.texture_set.json"}

    def ign01(dirp, names):
        if Path(dirp).name != "pw_vine":
            return []
        return [n for n in names if n not in keep_still]       # other stills: no key uses them any more
    shutil.copytree(B / s, B / d, ignore=ign01)
    R1 = B / d
    vd = R1 / "textures/blocks/pw_vine"
    tt = jl(R1 / "textures/terrain_texture.json")
    td = tt["texture_data"]
    fb = jl(R1 / "textures/flipbook_textures.json")
    gif = {}
    for name in VARS:
        st = strips(name)
        for mode, (c, n, m) in st.items():
            stem = f"{name}_{mode}"
            Image.fromarray(c, "RGBA").save(vd / f"{stem}.png", optimize=True)
            Image.fromarray(n, "RGBA").save(vd / f"{stem}_n.png", optimize=True)
            Image.fromarray(m, "RGBA").save(vd / f"{stem}_mer.png", optimize=True)
            (vd / f"{stem}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
                "color": stem, "normal": f"{stem}_n", "metalness_emissive_roughness_subsurface": f"{stem}_mer"}}, indent=1))
            if name == "vine_extra":
                key = "pw_vine_extra" if mode == "w" else "pw_vine_extra_r"
            else:
                i = name[6:]
                key = f"pw_vine_v{i}" if mode == "w" else f"pw_vine_r{i}"
            td[key] = {"textures": f"textures/blocks/pw_vine/{stem}"}
            fb.append({"flipbook_texture": f"textures/blocks/pw_vine/{stem}", "atlas_tile": key,
                       "ticks_per_frame": MODES[mode][4], "frames": list(range(FR)), "blend_frames": True})
            gif[(name, mode)] = c
    # vanilla vine keys move here from RP-04 (ownership: key + image + set in ONE pack); vanilla vines only show for
    # the moment before the swap (and as the item), one still is enough
    td["vine"] = {"textures": "textures/blocks/pw_vine/vine_v0"}
    td["vine_single"] = {"textures": "textures/blocks/pw_vine/vine_v0"}
    (R1 / "textures/terrain_texture.json").write_text(json.dumps(tt, indent=1))
    (R1 / "textures/flipbook_textures.json").write_text(json.dumps(fb, indent=1))
    manifest(R1, ver, "Vines move: a gentle wind ripple always (16-frame flipbooks) and a quick rustle when you walk "
                      "into them (with BP-02 1.3.203); vanilla vine keys now live here.")
    rep["RP-01"] = {"dir": d, "strips": 2 * len(VARS), "flipbooks": len(fb), "stills_kept": sorted(keep_still)}

    # ---------------- RP-04 1.3.153: drop the old flat-vine copies
    s, d, ver = DST["RP-04"]
    dropped = []

    def ign04(dirp, names):
        if Path(dirp).as_posix().endswith("textures/blocks"):
            out = [n for n in names if re.match(r"^vine(_v\d+)?(_n|_mer|_n256|_mer256)?(\.png|\.texture_set\.json)$", n)]
            dropped.extend(out)
            return out
        return []
    shutil.copytree(B / s, B / d, ignore=ign04)
    R4 = B / d
    tt = jl(R4 / "textures/terrain_texture.json")
    for k in ("vine", "vine_single"):
        del tt["texture_data"][k]
    (R4 / "textures/terrain_texture.json").write_text(json.dumps(tt, indent=1))
    tl = R4 / "textures/textures_list.json"
    if tl.exists():
        L = jl(tl)
        L2 = [p for p in L if not re.match(r"^textures/blocks/vine(_v\d+)?(_n|_mer|_n256|_mer256)?$", p)]
        tl.write_text(json.dumps(L2, indent=1))
        rep["RP-04_textures_list_removed"] = len(L) - len(L2)
    manifest(R4, ver, "The old flat-vine textures are gone (vines are 3D pw:vine now; their keys live in RP-01).")
    rep["RP-04"] = {"dir": d, "files_dropped": len(dropped), "keys_removed": ["vine", "vine_single"]}

    # ---------------- BP-02 1.3.203: pw:r state + 24 material permutations + rustle script
    s, d, ver = DST["BP-02"]
    shutil.copytree(B / s, B / d)
    RB = B / d
    bp = RB / "blocks/pw_vine.json"
    blk = jl(bp)
    b = blk["minecraft:block"]
    b["description"]["states"]["pw:r"] = [False, True]
    geo = [p for p in b["permutations"] if "minecraft:geometry" in p["components"]]
    assert len(geo) == 16 and len(b["permutations"]) == 28
    mats = []
    for i in range(12):
        for r in (False, True):
            cond = f"q.block_state('pw:v') == {i} && " + ("q.block_state('pw:r')" if r else "!q.block_state('pw:r')")
            mats.append({"condition": cond, "components": {"minecraft:material_instances": {
                "*": dict(texture=f"pw_vine_r{i}" if r else f"pw_vine_v{i}", **MAT),
                "extra": dict(texture="pw_vine_extra_r" if r else "pw_vine_extra", **MAT)}}})
    b["permutations"] = geo + mats
    bp.write_text(json.dumps(blk, indent=1))
    shutil.copy2(ROOT / "_staging/vine3d/pw_vine.js", RB / "scripts/pw_vine.js")
    mj = RB / "scripts/main.js"
    t = mj.read_text()
    t2 = t.replace('const PW_BUILD = "1.3.202";', 'const PW_BUILD = "1.3.203";').replace(
        'import "./pw_vine.js"; // v1.3.202: 3D vines, swap once + scripted climbing (his Q1 = a, 10-02)',
        'import "./pw_vine.js"; // v1.3.202: 3D vines, swap once + scripted climbing (his Q1 = a, 10-02); v1.3.203 rustle on touch')
    assert t2.count('PW_BUILD = "1.3.203"') == 1 and "v1.3.203 rustle" in t2, "main.js edit did not land"
    mj.write_text(t2)
    manifest(RB, ver, "Vines rustle when you walk into them (state pw:r, 2 s) and sway in the wind (RP-01 1.3.115).")
    rep["BP-02"] = {"dir": d, "permutations": len(b["permutations"]), "states": {k: len(v) for k, v in b["description"]["states"].items()}}

    # ---------------- StripMine BP 1.3.13: desert owl spawn filter typo
    s, d, ver = DST["SM-BP"]
    shutil.copytree(B / s, B / d)
    RS = B / d
    f = RS / "spawn_rules/pw_menagerie/ws/skinscraft_desert_owl.json"
    t = f.read_text(encoding="utf-8-sig")
    assert t.count('"minecraft:sane"') == 1
    f.write_text(t.replace('"minecraft:sane"', '"minecraft:sand"'))
    assert '"minecraft:sane"' not in f.read_text() and '"minecraft:sand"' in f.read_text()
    manifest(RS, ver, "Desert owl spawn rule: block filter typo minecraft:sane fixed to minecraft:sand (content-log error).")
    rep["SM-BP"] = {"dir": d, "fixed": str(f.relative_to(RS))}

    # ---------------- preview GIF: 2 x 2 tiles of v0 (wind) beside 2 x 2 of v3 (rustle), green wall
    frames = []
    for t_ in range(FR):
        row = []
        for name, mode in (("vine_v0", "w"), ("vine_v3", "r")):
            c = gif[(name, mode)][t_ * OUT_SZ:(t_ + 1) * OUT_SZ].astype(float) / 255
            bg = np.array([0.42, 0.40, 0.36])
            tile = c[..., :3] * c[..., 3:4] * np.array([0.55, 0.85, 0.4]) / 0.7 + bg * (1 - c[..., 3:4])
            row.append(np.tile(tile.clip(0, 1), (2, 2, 1)))
        frames.append(Image.fromarray((np.concatenate(row, 1) * 255).astype(np.uint8)))
    (ROOT / "_docs/flora").mkdir(parents=True, exist_ok=True)
    frames[0].save(ROOT / "_docs/flora/VINE-SWAY-PREVIEW.gif", save_all=True, append_images=frames[1:], duration=150, loop=0)
    (ROOT / "_docs/blocks/BUILD-1002H.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
