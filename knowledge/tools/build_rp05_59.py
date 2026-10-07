#!/usr/bin/env python3
"""build_rp05_59.py — RP-05 Flora 1.3.59 from the frozen 1.3.58 (never rebuilt): VANILLA LEAF TEXTURES (round 1004b, R-52,
AUDIT-TREES-LEAVES-2026-10-04 §5 / §8.1; his 17:38 "fix all the tree issues").
The engine's own trees (swamp oaks, mangroves, grove spruces, old-growth pines, anything a vanilla feature still places) wear
the VANILLA leaf keys. In 1.3.47..1.3.58 those keys pointed at 32 x 256 wind strips without a flipbook entry (frame 0 only,
L-ATLAS-SQUARE) or 128-px tiles, all BLACK under alpha 0, and every key was a "variations" object of one path — so the
engine's opaque leaf pass (fancy leaves off, the far LOD, the phone) had no opaque entry and drew the cut-out black.
Now every vanilla leaf key mirrors vanilla's own shape — [cutout, opaque] pairs (the legacy "leaves" / "leaves2" keys their
4 + 4 / 2 + 2 arrays, the carried keys their cutouts) — on OUR leaf art: pw_leaves2/<species>_f0 (Patrix 26.2 256x tiles,
grey for the biome-tinted species, pre-coloured for cherry / azalea / pale oak; its alpha-0 texels already hold the leaf's
mean colour). cutout = f0 (256), opaque = f0 at alpha 255, downscaled to 128 (seen only at distance / fancy off): atlas
cost 11 x (64 + 16) K = 0.9 Mpx against the 60 Mpx budget (the old files ~0.13 Mpx leave the atlas as nothing refers to them).
Usage: build_rp05_59.py   (rp05-59 must not exist)"""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

B = Path("/home/claude/_build")
SRC, DST, RP1 = B / "rp05-58", B / "rp05-59", B / "rp01-122"
ART = RP1 / "textures/blocks/pw_leaves2"
OUT_REL = "textures/blocks/pw_vanilla_leaves"
SPECIES = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "azalea", "flowering_azalea"]
P = {sp: f"{OUT_REL}/{sp}" for sp in SPECIES}
PO = {sp: f"{OUT_REL}/{sp}_opaque" for sp in SPECIES}


def keys():
    """every vanilla leaf key -> its texture list, exactly vanilla's array shapes (bedrock-samples 1.21.x terrain_texture.json)"""
    k = {}
    pair = lambda sp: [P[sp], PO[sp]]                       # noqa: E731
    carried = lambda sp: [P[sp], P[sp]]                     # noqa: E731
    for sp, key in (("oak", "oak_leaves"), ("spruce", "spruce_leaves"), ("birch", "birch_leaves"), ("jungle", "jungle_leaves"),
                    ("acacia", "acacia_leaves"), ("dark_oak", "big_oak_leaves"), ("mangrove", "mangrove_leaves"),
                    ("cherry", "cherry_leaves"), ("pale_oak", "pale_oak_leaves"), ("azalea", "azalea_leaves"),
                    ("flowering_azalea", "azalea_leaves_flowered")):
        k[key] = pair(sp)
        k[key + "_carried"] = carried(sp)
    k["leaves"] = [P["oak"], P["spruce"], P["birch"], P["jungle"], PO["oak"], PO["spruce"], PO["birch"], PO["jungle"]]
    k["leaves2"] = [P["acacia"], P["dark_oak"], PO["acacia"], PO["dark_oak"]]
    k["leaves_carried"] = [P["oak"], P["spruce"], P["birch"], P["jungle"]] * 2
    k["leaves_carried2"] = [P["acacia"], P["dark_oak"]] * 2
    # RP-05's own older key spellings (1.3.47 era), repointed so nothing still refers to the strips
    for sp, old in (("oak", "leaves_oak"), ("spruce", "leaves_spruce"), ("birch", "leaves_birch"), ("jungle", "leaves_jungle"),
                    ("acacia", "leaves_acacia"), ("dark_oak", "leaves_big_oak"), ("dark_oak", "dark_oak_leaves"),
                    ("mangrove", "leaves_mangrove"), ("cherry", "leaves_cherry"), ("pale_oak", "leaves_pale_oak"),
                    ("azalea", "leaves_azalea"), ("flowering_azalea", "flowering_azalea_leaves")):
        k[old] = pair(sp)
        k[old + "_carried"] = carried(sp)
    return k


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    out = DST / OUT_REL
    out.mkdir(parents=True, exist_ok=True)
    stats = {}
    for sp in SPECIES:
        src = ART / f"{sp}_f0.png"
        im = Image.open(src).convert("RGBA")
        if im.size != (256, 256):
            raise SystemExit(f"{src} is {im.size}")
        a = np.asarray(im).astype(np.uint8)
        op = a[a[..., 3] > 128][:, :3].mean(0)
        tr = a[a[..., 3] == 0][:, :3].mean(0) if (a[..., 3] == 0).any() else op
        if np.abs(tr - op).max() > 40:                     # the fill under alpha 0 must be the leaf's own colour, never black
            raise SystemExit(f"{sp}: alpha-0 fill {tr} far from the leaf colour {op}")
        im.save(out / f"{sp}.png", optimize=True)
        o = a.copy()
        o[..., 3] = 255
        Image.fromarray(o, "RGBA").resize((128, 128), Image.LANCZOS).save(out / f"{sp}_opaque.png", optimize=True)
        stats[sp] = {"opaque_mean": [int(v) for v in op], "alpha0_share": round(float((a[..., 3] == 0).mean()), 2)}
    tp = DST / "textures/terrain_texture.json"
    tt = json.loads(tp.read_text())
    k = keys()
    for key, lst in k.items():
        tt["texture_data"][key] = {"textures": lst}
    tp.write_text(json.dumps(tt, indent=1))
    # every referenced path exists and is square
    for key, lst in k.items():
        for rel in lst:
            f = DST / (rel + ".png")
            if not f.exists():
                raise SystemExit(f"{key}: {rel} missing")
            w, h = Image.open(f).size
            if w != h:
                raise SystemExit(f"{key}: {rel} not square")
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = [1, 3, 59]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 59]
    m["header"]["name"] = m["header"]["name"].replace("1.3.58", "1.3.59") if "1.3.58" in m["header"]["name"] else "AbsolutRealism Flora RP v1.3.59"
    m["header"]["description"] = ("v1.3.59 (2026-10-04) VANILLA LEAVES: every vanilla leaf key (the engine's own swamp oaks, mangroves, grove "
                                  "spruces ...) now wears our 256-px leaf art with a proper opaque pair (no more 32-px strips, no black "
                                  "cubes at distance). Includes all of " + m["header"]["description"])[:1000]
    mp.write_text(json.dumps(m, indent=1))
    print("DONE", DST, json.dumps(stats))
    print("keys written:", len(k))


if __name__ == "__main__":
    main()
