#!/usr/bin/env python3
"""normal_unit_census.py — D1 = a (his 19:07): every NORMAL layer a texture set points at, in the 7 new block builds, is
checked for the Bedrock format: RGB = a unit vector (length ~1 after decoding, z > 0). A LabPBR map copied raw (RG = XY,
B = ambient occlusion, A = height) decodes to vectors that are too short / too long and a wrong z — the engine then lights
the block as if every pixel were tilted. Report: _docs/blocks/NORMAL-UNIT-CENSUS.json."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
BUILDS = ["rp04-145", "rp05-52", "rp10-144", "rp11-136", "rp01-108", "rp03-61", "rp08-1410"]
EXT = (".tga", ".png", ".jpg", ".jpeg")


def check(img):
    a = np.asarray(img.convert("RGBA")).astype(float) / 255 * 2 - 1
    ln = np.sqrt((a[..., :3] ** 2).sum(-1))
    return float(np.median(ln)), float(np.median(a[..., 2])), float((a[..., 2] <= 0).mean())


def main():
    rows, seen = [], set()
    for b in BUILDS:
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
            if lp is None or lp in seen:
                continue
            seen.add(lp)
            med_len, med_z, neg = check(Image.open(lp))
            status = "OK" if abs(med_len - 1) < 0.08 and med_z > 0.5 else "NOT_UNIT"
            rows.append({"build": b, "file": str(lp.relative_to(D)), "median_len": round(med_len, 3), "median_z": round(med_z, 3),
                         "z_le_0": round(neg, 3), "status": status})
    (ROOT / "_docs/blocks/NORMAL-UNIT-CENSUS.json").write_text(json.dumps(rows, indent=1))
    c = Counter((r["build"], r["status"]) for r in rows)
    print(len(rows), "normal files ·", dict(c))
    bad = [r for r in rows if r["status"] != "OK"]
    for r in bad[:12]:
        print("  ", r)
    return rows


if __name__ == "__main__":
    main()
