#!/usr/bin/env python3
"""normal_reencode.py — every normal layer named by a texture set in the 7 block-round builds is re-encoded as a true unit
vector from its own RG (the tilt): x, y = RG decoded; if x² + y² > 0.995² they are scaled down to that; z = sqrt(1 - x² - y²);
B = (z + 1) / 2 * 255; alpha 255. Files whose median length is already within 0.02 of 1 are left alone. Written into the
build (not yet delivered) and mirrored into _staging/pbr."""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
KEY = {"rp04-145": "rp04", "rp05-52": "rp05", "rp10-144": "rp10", "rp11-136": "rp11", "rp01-108": "rp01",
       "rp03-61": "rp03", "rp08-1410": "rp08"}
EXT = (".tga", ".png", ".jpg", ".jpeg")


def reencode(a):
    v = a[..., :2].astype(float) / 255 * 2 - 1
    r2 = (v ** 2).sum(-1)
    s = np.where(r2 > 0.995 ** 2, 0.995 / np.sqrt(np.maximum(r2, 1e-9)), 1.0)
    v = v * s[..., None]
    z = np.sqrt(np.clip(1 - (v ** 2).sum(-1), 0, 1))
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    out[..., 0] = np.round((v[..., 0] + 1) / 2 * 255)
    out[..., 1] = np.round((v[..., 1] + 1) / 2 * 255)
    out[..., 2] = np.round((z + 1) / 2 * 255)
    out[..., 3] = 255
    return out


def main():
    done, n_fix = set(), 0
    for b, key in KEY.items():
        D = ROOT / "_build" / b
        for f in D.rglob("*.texture_set.json"):
            try:
                ts = json.loads(re.sub(r"(?m)^\s*//.*$", "", f.read_text(encoding="utf-8-sig")))["minecraft:texture_set"]
            except Exception:  # noqa: BLE001
                continue
            n = ts.get("normal")
            if not isinstance(n, str):
                continue
            lp = next((f.parent / (n + e) for e in EXT if (f.parent / (n + e)).exists()), None)
            if lp is None or lp in done:
                continue
            done.add(lp)
            a = np.asarray(Image.open(lp).convert("RGBA"))
            v = a[..., :3].astype(float) / 255 * 2 - 1
            if abs(np.median(np.sqrt((v ** 2).sum(-1))) - 1) <= 0.02:
                continue
            out = Image.fromarray(reencode(a), "RGBA")
            target = lp if lp.suffix == ".png" else lp.with_suffix(".png")
            out.save(target, optimize=True)
            st = ROOT / "_staging/pbr" / key / target.relative_to(D)
            st.parent.mkdir(parents=True, exist_ok=True)
            out.save(st, optimize=True)
            n_fix += 1
    print("re-encoded normal files:", n_fix)


if __name__ == "__main__":
    main()
