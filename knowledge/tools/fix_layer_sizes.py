#!/usr/bin/env python3
"""fix_layer_sizes.py — post-pass for round 1002f: a texture set whose COLOUR is 192 but whose layer is still 256
(the layer file was named only by a set whose own path no terrain key uses, e.g. pw_oak_elder_log_v0.texture_set.json ->
colour pw_oak_elder_log) gets that layer resampled to the colour's size (normal re-normalised, MERS per channel).
Usage: fix_layer_sizes.py <build dir> [...]   (only new, undelivered build dirs)"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "/home/claude/tools")
import pbr_round as PR  # noqa: E402

EXT = (".png", ".tga", ".jpg")


def main(dirs):
    n = 0
    for d in dirs:
        for sp in Path(d).rglob("*.texture_set.json"):
            ts = json.loads(sp.read_text())["minecraft:texture_set"]
            col = ts.get("color")
            if not isinstance(col, str) or col.startswith("#"):
                continue
            cp = next((sp.parent / (col + e) for e in EXT if (sp.parent / (col + e)).exists()), None)
            if cp is None:
                continue
            cs = Image.open(cp).size
            if cs[0] != 192:
                continue
            for k, v in ts.items():
                if k == "color" or not isinstance(v, str) or v.startswith("#"):
                    continue
                lp = next((sp.parent / (v + e) for e in EXT if (sp.parent / (v + e)).exists()), None)
                if lp is None:
                    continue
                im = Image.open(lp)
                if im.size[0] == 256:
                    out = PR.resample(im, (192, im.size[1] * 192 // 256), "normal" if k == "normal" else "mers")
                    out.save(lp) if lp.suffix != ".tga" else out.save(lp, "TGA", compression=None)
                    print("resized", lp.relative_to(d), "for", sp.name)
                    n += 1
    print("layers fixed:", n)


if __name__ == "__main__":
    main(sys.argv[1:])
