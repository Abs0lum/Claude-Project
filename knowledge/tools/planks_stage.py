#!/usr/bin/env python3
"""planks_stage.py — his 00:07 / 00:53: Patrix 256 planks as a SEAMLESS 4 x 4 grid (16 tiles per species, all 11 Patrix
species). RP side: colour (Patrix's own colour — 'go back to using the Patrix planks'), normal (mers_derive.normal_156)
and MERS (Lesson #156 mers_156) for every tile, one texture set each, terrain keys pw_planks_<species>_<1..16>.
Output: _staging/planks/rp04/textures/blocks/pw_planks/* + _staging/planks/rp04/TERRAIN.json (key -> def)
+ _docs/planks/PLANKS-STAGE.json."""
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

SPECIES = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "crimson", "warped"]
OUT = ROOT / "_staging/planks/rp04/textures/blocks/pw_planks"


def main():
    Z = zipfile.ZipFile(PR.PATRIX256)
    OUT.mkdir(parents=True, exist_ok=True)
    terrain, rep = {}, []
    for sp in SPECIES:
        base = f"assets/minecraft/optifine/ctm/patrix/planks/{sp}/"
        for i in range(1, 17):
            stem = f"{sp}_{i}"
            col = Image.open(io.BytesIO(Z.read(base + f"{i}.png"))).convert("RGBA")
            nrm = MD.normal_156(np.asarray(Image.open(io.BytesIO(Z.read(base + f"{i}_n.png"))).convert("RGBA")))
            mer = MD.mers_156(np.asarray(Image.open(io.BytesIO(Z.read(base + f"{i}_s.png"))).convert("RGBA")))
            assert col.size == (256, 256) and nrm.shape[:2] == (256, 256) and mer.shape[:2] == (256, 256), stem
            col.save(OUT / f"{stem}.png", optimize=True)
            Image.fromarray(nrm, "RGBA").save(OUT / f"{stem}_n.png", optimize=True)
            Image.fromarray(mer, "RGBA").save(OUT / f"{stem}_mer.png", optimize=True)
            (OUT / f"{stem}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
                "color": stem, "normal": f"{stem}_n", "metalness_emissive_roughness_subsurface": f"{stem}_mer"}}, indent=1))
            terrain[f"pw_planks_{stem}"] = {"textures": f"textures/blocks/pw_planks/{stem}"}
            n = nrm[..., :3].astype(float) / 255 * 2 - 1
            rep.append({"tile": stem, "rough_mean": round(float(mer[..., 2].mean()), 1), "metal_max": int(mer[..., 0].max()),
                        "normal_len": round(float(np.linalg.norm(n, axis=-1).mean()), 3)})
    (OUT.parent.parent.parent / "TERRAIN.json").write_text(json.dumps(terrain, indent=1))
    (ROOT / "_docs/planks").mkdir(parents=True, exist_ok=True)
    (ROOT / "_docs/planks/PLANKS-STAGE.json").write_text(json.dumps(rep, indent=1))
    r = np.array([x["rough_mean"] for x in rep])
    print(len(rep), "tiles; roughness mean range", r.min(), r.max(), "metal max", max(x["metal_max"] for x in rep),
          "normal len", min(x["normal_len"] for x in rep))


if __name__ == "__main__":
    main()
