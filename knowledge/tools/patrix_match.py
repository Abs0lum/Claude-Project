#!/usr/bin/env python3
"""patrix_match.py — for block texture paths with NO texture set (block_pbr_census NO_SET), find the Patrix 26.2 256x
source image (base block textures + OptiFine CTM tiles that carry LabPBR _n / _s) by PIXELS: 24x24 RGB thumbnails, mean
absolute difference; the alpha pattern must agree too. Writes _docs/blocks/PATRIX-MATCH.json:
{path: {"best": zip member, "d": distance, "d2": second best, "pack": top pack holding the colour}}"""
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import stack_now as SN  # noqa: E402

ZIP = ROOT / "_intake/patrix262_256/Patrix_26.2_256x_basic.zip"
T = 24


def thumb(im):
    """first frame of a strip, 24x24 RGBA float."""
    im = im.convert("RGBA")
    w, h = im.size
    if h > w and h % w == 0:
        im = im.crop((0, 0, w, w))
    return np.asarray(im.resize((T, T), Image.BOX)).astype(np.float32)


def index():
    Z = zipfile.ZipFile(ZIP)
    names = set(Z.namelist())
    keys, th = [], []
    for n in sorted(names):
        if not n.endswith(".png") or n.endswith(("_n.png", "_s.png")):
            continue
        if not ("textures/block/" in n or "/ctm/" in n):
            continue
        if n[:-4] + "_n.png" not in names and n[:-4] + "_s.png" not in names:
            continue
        try:
            th.append(thumb(Image.open(io.BytesIO(Z.read(n)))))
            keys.append(n)
        except Exception:  # noqa: BLE001
            pass
    return keys, np.stack(th)


def main():
    census = json.loads((ROOT / "_docs/blocks/BLOCK-PBR-CENSUS.json").read_text())["rows"]
    todo = sorted({r["path"] for r in census if r["status"] == ["NO_SET"] and r["img_packs"]})
    P = SN.packs()
    keys, th = index()
    print("patrix sources", len(keys), "· paths", len(todo))
    out = {}
    for path in todo:
        p, f = SN.find_image(P, path)
        if not p:
            continue
        a = thumb(Image.open(io.BytesIO(p.read(f))))
        d = np.abs(th[..., :3] - a[None, ..., :3]).mean(axis=(1, 2, 3)) + np.abs(th[..., 3] - a[None, ..., 3]).mean(axis=(1, 2)) * 0.5
        o = np.argsort(d)[:2]
        out[path] = {"best": keys[o[0]], "d": round(float(d[o[0]]), 2), "second": keys[o[1]], "d2": round(float(d[o[1]]), 2),
                     "pack": p.name, "file": f}
    (ROOT / "_docs/blocks/PATRIX-MATCH.json").write_text(json.dumps(out, indent=1))
    ds = np.array([v["d"] for v in out.values()])
    print("matched", len(out), "· d percentiles 10/50/90:", np.percentile(ds, [10, 50, 90]).round(1),
          "· d<4", int((ds < 4).sum()), "· d<8", int((ds < 8).sum()), "· d<12", int((ds < 12).sum()))


if __name__ == "__main__":
    main()
