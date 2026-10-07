#!/usr/bin/env python3
"""vine_stage.py — his 22:51 / 00:53: vines next to 256x leaves must be 256x (texture step; the 3D pw:vine is later).
Our RP-04 vine_v0..v11 (128) are Patrix 'ctm/patrix/vine' 1..12 (alpha-mask correlation 0.887-0.911, 10-01).
Each Patrix 256 source is colour-graded onto our current picture (per-channel mean/std, opaque pixels — keeps today's
colour), its _n converted by mers_derive.normal_156 and its _s by Lesson #156 (mers_156). Every variant gets its own set
(today all 12 share one 128 vine_n / vine_mer). Output: _staging/vine/rp04/textures/blocks/ + _docs/blocks/VINE-STAGE.json."""
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import mers_derive as MD  # noqa: E402
import pbr_round as PR  # noqa: E402
import tier_round as TR  # noqa: E402

OURS = ROOT / "_build/rp04-147/textures/blocks"
OUT = ROOT / "_staging/vine/rp04/textures/blocks"


def main():
    Z = zipfile.ZipFile(PR.PATRIX256)
    OUT.mkdir(parents=True, exist_ok=True)
    rep = []
    for i in range(12):
        b = f"assets/minecraft/optifine/ctm/patrix/vine/{i + 1}"
        ours = np.asarray(Image.open(OURS / f"vine_v{i}.png").convert("RGBA"))
        src = np.asarray(Image.open(io.BytesIO(Z.read(b + ".png"))).convert("RGBA"))
        col = TR.grade_match(src, ours)
        nrm = MD.normal_156(np.asarray(Image.open(io.BytesIO(Z.read(b + "_n.png"))).convert("RGBA")))
        mer = MD.mers_156(np.asarray(Image.open(io.BytesIO(Z.read(b + "_s.png"))).convert("RGBA")))
        Image.fromarray(col, "RGBA").save(OUT / f"vine_v{i}.png")
        Image.fromarray(nrm, "RGBA").save(OUT / f"vine_v{i}_n256.png")
        Image.fromarray(mer, "RGBA").save(OUT / f"vine_v{i}_mer256.png")
        (OUT / f"vine_v{i}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
            "color": f"vine_v{i}", "normal": f"vine_v{i}_n256",
            "metalness_emissive_roughness_subsurface": f"vine_v{i}_mer256"}}, indent=1))
        op = col[..., 3] > 128
        n = nrm[..., :3].astype(float) / 255 * 2 - 1
        rep.append({"variant": i, "source": b.split("/minecraft/")[1], "size": list(col.shape[:2]),
                    "colour_ours": ours[ours[..., 3] > 128][:, :3].mean(0).round(1).tolist(),
                    "colour_new": col[op][:, :3].mean(0).round(1).tolist(),
                    "normal_len": round(float(np.linalg.norm(n, axis=-1).mean()), 3),
                    "rough_mean": round(float(mer[..., 2][op].mean()), 1), "metal_max": int(mer[..., 0].max()),
                    "alpha_match": round(float(np.corrcoef((ours[..., 3] > 128).ravel(),
                        (np.asarray(Image.fromarray(col).resize((128, 128), Image.NEAREST))[..., 3] > 128).ravel())[0, 1]), 3)})
    (ROOT / "_docs/blocks/VINE-STAGE.json").write_text(json.dumps(rep, indent=1))
    for r in rep:
        print(r)


if __name__ == "__main__":
    main()
