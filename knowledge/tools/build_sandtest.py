#!/usr/bin/env python3
"""build_sandtest.py — his 20:33 S5 = b: two in-game TEST packs for the sand depth fix, used like the saturation test
(put ONE on top of the stack, compare with it off). Each pack holds the 24 sand texture sets complete — colour + MERS
copied byte-for-byte from RP-04 1.3.147 (unchanged since 1.3.146) and the NEW normal map — because a texture set only
applies inside its own pack (H-18). Only the normal map differs from what he has now.
  A = current depth with the small lumps removed (seamless, mean slope 3 deg; today 7.4)
  B = depth from the colour's own soft mottling (seamless, mean slope 3 deg)
Normals come from tools/sand_vv_preview.py (_staging/sand_vv/<A|B>/)."""
import json
import shutil
import uuid
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
SRC = ROOT / "_build/rp04-147"
ICON = ROOT / "_build/lighttest-sat-100/pack_icon.png"
DESC = {"A": "A = today's sand depth with the small lumps removed (smooth, seamless).",
        "B": "B = sand depth made from the colour's own soft cloudy pattern (smooth, seamless)."}


def build(kind):
    dst = ROOT / f"_build/sandtest-{kind.lower()}-100"
    assert not dst.exists(), "never rebuild a build dir"
    tb = dst / "textures/blocks"
    tb.mkdir(parents=True)
    for v in range(1, 25):
        stem = f"pw_sand_v{v}"
        shutil.copy2(SRC / f"textures/blocks/{stem}.png", tb / f"{stem}.png")
        shutil.copy2(SRC / f"textures/blocks/{stem}_mers.png", tb / f"{stem}_mers.png")
        n = Image.open(ROOT / f"_staging/sand_vv/{kind}/{stem}_n.png")
        assert n.size == Image.open(tb / f"{stem}.png").size == (256, 256)
        a = np.asarray(n).astype(float) / 255 * 2 - 1
        assert abs(np.linalg.norm(a, axis=-1).mean() - 1) < 0.02, f"{stem} normal not unit"
        shutil.copy2(ROOT / f"_staging/sand_vv/{kind}/{stem}_n.png", tb / f"{stem}_n.png")
        (tb / f"{stem}.texture_set.json").write_text(json.dumps({
            "format_version": "1.21.30",
            "minecraft:texture_set": {"color": stem, "normal": f"{stem}_n",
                                      "metalness_emissive_roughness_subsurface": f"{stem}_mers"}}, indent=2))
    (dst / "manifest.json").write_text(json.dumps({"format_version": 2, "header": {
        "name": f"PW-SandTest {kind} v1.0.0",
        "description": f"TEST ONLY (10-01): {DESC[kind]} Put it at the TOP of the stack; take it off = today's sand. "
                       "Colour and shine maps identical to RP-04. Not for normal play.",
        "uuid": str(uuid.uuid4()), "version": [1, 0, 0], "min_engine_version": [1, 21, 120]},
        "modules": [{"description": f"sand depth test {kind}", "type": "resources", "uuid": str(uuid.uuid4()),
                     "version": [1, 0, 0]}]}, indent=2))
    shutil.copy2(ICON, dst / "pack_icon.png")
    print("built", dst.name, sum(1 for _ in dst.rglob("*") if _.is_file()), "files")


if __name__ == "__main__":
    for k in ("A", "B"):
        build(k)
