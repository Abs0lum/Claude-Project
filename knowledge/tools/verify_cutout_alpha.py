#!/usr/bin/env python3
"""verify_cutout_alpha.py — D-C469 gate: every cut-out custom texture (pw_*.png colour images with transparent texels) whose
alpha was HARD (only 0 / 255) in the witnessed reference must still be hard, and at its reference size.
Reference: RP-04 1.3.150 as restored from the Drive archive (_restore/a214903/_build/rp04-150/textures/blocks).
Usage: verify_cutout_alpha.py <rp04 build dir>     exit 1 on any failure."""
import glob
import re
import sys

import numpy as np
from PIL import Image

REF = "/home/claude/_restore/a214903/_build/rp04-150/textures/blocks/"


def hard(path):
    alpha = np.asarray(Image.open(path).convert("RGBA"))[..., 3]
    return not ((alpha > 0) & (alpha < 255)).any(), alpha.shape


def is_cutout(path):
    """A cut-out texture has transparent texels (alpha 0) — fully opaque images are not cut-outs."""
    return bool((np.asarray(Image.open(path).convert("RGBA"))[..., 3] == 0).any())


def main(build):
    fails, checked = [], 0
    for ref in sorted(glob.glob(REF + "pw_*.png")):
        name = ref.rsplit("/", 1)[1]
        if re.search(r"_(mer|mers|n|e|w)\.png$", name):
            continue
        ref_hard, ref_shape = hard(ref)
        if not ref_hard or not is_cutout(ref):
            continue
        checked += 1
        cur = f"{build}/textures/blocks/{name}"
        try:
            cur_hard, cur_shape = hard(cur)
        except FileNotFoundError:
            fails.append(f"{name}: missing")
            continue
        if not cur_hard or cur_shape != ref_shape:
            fails.append(f"{name}: hard={cur_hard} size={cur_shape} (ref {ref_shape})")
    print(f"cut-out alpha gate: {checked - len(fails)}/{checked} PASS")
    for f in fails:
        print("  FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
