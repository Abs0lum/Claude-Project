#!/usr/bin/env python3
"""fix_set_sizes_128.py — post-pass for round 1002i (verify G3): a texture set whose layers disagree on 128 vs 192 because a
layer file is SHARED with another set that went to 128 (log tops v4-6 reuse v1-3's normal) or is named only by an orphan set
(pw_oak_elder_log_v0_mer): every 192 member (colour or layer) of a set that already has a 128 member goes to 128.
Usage: fix_set_sizes_128.py <build dir> [...]   (only new, undelivered build dirs)"""
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
            mem = {}
            for k, v in ts.items():
                if not isinstance(v, str) or v.startswith("#"):
                    continue
                p = next((sp.parent / (v + e) for e in EXT if (sp.parent / (v + e)).exists()), None)
                if p is not None:
                    mem[k] = p
            sizes = {k: Image.open(p).size[0] for k, p in mem.items()}
            if 128 not in sizes.values() or 192 not in sizes.values():
                continue
            for k, p in mem.items():
                im = Image.open(p)
                if im.size[0] != 192:
                    continue
                size = (128, im.size[1] * 128 // 192)
                if k == "color":
                    out = PR._bands_resize(im if im.mode in ("RGB", "RGBA") else im.convert("RGBA"), size, Image.LANCZOS)
                else:
                    out = PR.resample(im, size, "normal" if k == "normal" else "mers")
                out.save(p, "TGA", compression=None) if p.suffix == ".tga" else out.save(p, optimize=True)
                print("128:", p.relative_to(d), "(", k, "of", sp.name, ")")
                n += 1
    print("members fixed:", n)


if __name__ == "__main__":
    main(sys.argv[1:])
