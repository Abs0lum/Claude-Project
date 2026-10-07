#!/usr/bin/env python3
"""vine3d_preview.py — round 4 STUDY (no pack touched): Patrix 26.2 256x 3D vine models converted to Bedrock block geometry
(Blockbench Java->Bedrock mapping, java_leaf_study.java_to_bedrock; single-face cards) and rendered beside today's flat vine.
Textures: our RP-04 1.3.148 vine_v0 (256) for 'vine', Patrix vine_extra graded onto our vine colour for 'extra'.
Flat-lit renderer: shape / texture reads only (L-RENDER-1).
Writes _docs/vines/VINE3D-PREVIEW.png and _staging/vine3d/geo/*.geo.json (12 base models) + _docs/vines/VINE3D-NUMBERS.json."""
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import java_leaf_study as J  # noqa: E402
import pbr_round as PR  # noqa: E402
import tier_round as TR  # noqa: E402

MODELS = ["vine_1", "vine_1u", "vine_2", "vine_2u", "vine_2_opposite", "vine_2u_opposite", "vine_3", "vine_3u", "vine_4",
          "vine_4u", "vine_cross", "vine_u"]
OUT = ROOT / "_docs/vines"
GEO = ROOT / "_staging/vine3d/geo"
TMP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad")


def main():
    Z = zipfile.ZipFile(PR.PATRIX256)
    OUT.mkdir(parents=True, exist_ok=True)
    GEO.mkdir(parents=True, exist_ok=True)
    vine = np.asarray(Image.open(ROOT / "_build/rp04-148/textures/blocks/vine_v0.png").convert("RGBA"))
    extra = np.asarray(Image.open(io.BytesIO(Z.read("assets/minecraft/textures/block/extra/vine_extra.png"))).convert("RGBA"))
    extra = TR.grade_match(extra, vine)
    atlas = TMP / "vine3d_atlas.png"
    J.build_atlas([Image.fromarray(vine), Image.fromarray(extra)], atlas)
    nums = {}
    bones_of = {}
    for name in MODELS:
        model = json.loads(Z.read(f"assets/minecraft/models/block/{name}.json"))
        bones = J.java_to_bedrock(model, {"#vine": 0, "#cross": 0, "#extra": 1}, mat_names={"#extra": "extra"})
        bones_of[name] = bones
        geo = {"format_version": "1.12.0", "minecraft:geometry": [{
            "description": {"identifier": f"geometry.pw_{name}", "texture_width": 16, "texture_height": 16,
                            "visible_bounds_width": 2, "visible_bounds_height": 2.5, "visible_bounds_offset": [0, 0.75, 0]},
            "bones": bones}]}
        (GEO / f"pw_{name}.geo.json").write_text(json.dumps(geo, indent=1))
        lo, hi, size = J.bounds(bones, 32, 16)
        nums[name] = {"cubes": len(bones[0]["cubes"]), "bounds_lo": lo, "bounds_hi": hi}
    # scene A: one wall of vines 3 x 3 (vine_1 on a south-facing wall), flat today vs 3D Patrix
    def wall(model_name, flat=False):
        fs = []
        for x in range(3):
            for y in range(3):
                if flat:
                    b = [{"name": "f", "pivot": [0, 0, 0], "cubes": [{"origin": [-8, 0, 7.2], "size": [16, 16, 0],
                          "uv": {"north": {"uv": [0, 0], "uv_size": [16, 16]}}}]}]
                else:
                    b = bones_of[model_name]
                fs += J.block_faces(b, 32, 16, (x, y, 0), dimmed=False)
        # the wall the vine hangs on (stone-grey cube row behind), drawn as a backdrop by bg colour
        return fs
    views = []
    for title, faces in (("TODAY: flat vine (one card on the wall)", wall("vine_1", flat=True)),
                         ("PATRIX 3D: vine_1 (6 leaf cards, tilted 22.5 deg)", wall("vine_1"))):
        for d in ((0.35, 0.25, -1.0), (1.0, 0.2, -0.35)):
            eye, tgt = J.cam_for(faces, d, pad=1.15)
            img = J.render(faces, atlas, eye, tgt, 420, 420, bg=(120, 120, 118))
            views.append(J.label(img, title, f"view {d}", (60, 60, 70)))
    # scene B: corner + opposite + cross singles
    singles = []
    for nm in ("vine_2", "vine_4", "vine_1u", "vine_cross"):
        faces = J.block_faces(bones_of[nm], 32, 16, (0, 0, 0), dimmed=False)
        eye, tgt = J.cam_for(faces, (0.8, 0.5, -1.0), pad=1.3)
        singles.append(J.label(J.render(faces, atlas, eye, tgt, 420, 420, bg=(120, 120, 118)), nm, "one block", (60, 60, 70)))
    W = 420
    sheet = Image.new("RGB", (4 * W, 2 * W), (20, 20, 22))
    for i, im in enumerate(views + singles):
        sheet.paste(im, ((i % 4) * W, (i // 4) * W))
    sheet.save(OUT / "VINE3D-PREVIEW.png")
    (OUT / "VINE3D-NUMBERS.json").write_text(json.dumps(nums, indent=1))
    print(json.dumps(nums))


if __name__ == "__main__":
    main()
