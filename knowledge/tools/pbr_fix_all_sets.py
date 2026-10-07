#!/usr/bin/env python3
"""pbr_fix_all_sets.py — PHASE 6 of the block PBR round (his 18:55 "fix this immediately"): every texture set in the 7 new
builds that fails verify_pbr_round G3 (a layer's size != the colour's) or G4 (MERS all zero = mirror-shiny, or roughness mean
< 20 on a material that is not metal / glass / ice) is repaired IN THE NEW BUILD (none delivered yet) and mirrored into
_staging/pbr:
  MERS   -> Patrix's own _s by Lesson #156 when the picture matches a Patrix source (thumbnail distance < 10; Patrix 26.2
            256x first, 128x when the 256x member lacks a map); else derived from the picture by material (pbr_round CLASSES)
  sizes  -> per-channel resample (strips: one frame tiled down the strip)
New layer names end in _fix (old files are left where they are). Report: _docs/blocks/PBR-PHASE6.json."""
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import mers_derive as MD  # noqa: E402
import patrix_match as PM  # noqa: E402
import pbr_round as PR  # noqa: E402

KEY = {"rp04-145": "rp04", "rp05-52": "rp05", "rp10-144": "rp10", "rp11-136": "rp11", "rp01-108": "rp01",
       "rp03-61": "rp03", "rp08-1410": "rp08"}
P128 = ROOT / "_intake/patrix262_basic/Patrix_26.2_128x_basic.zip"


def main():
    fails = json.loads((ROOT / "_docs/blocks/VERIFY-PBR-ROUND.json").read_text())
    todo = sorted({(f[1], f[2]) for f in fails if f[0] in ("G3", "G4")})
    Z256, Z128 = zipfile.ZipFile(PR.PATRIX256), zipfile.ZipFile(P128)
    n256, n128 = set(Z256.namelist()), set(Z128.namelist())
    keys, th = PM.index()
    report = []
    for b, rel in todo:
        D = ROOT / "_build" / b
        f = D / rel
        full = json.loads(f.read_text())
        ts = full["minecraft:texture_set"]
        if not isinstance(ts.get("color"), str):
            continue
        col_p = next((f.parent / (ts["color"] + e) for e in PR.EXT if (f.parent / (ts["color"] + e)).exists()), None)
        if col_p is None:
            continue
        col = Image.open(col_p)
        rgba = np.asarray(col.convert("RGBA"))
        size = col.size
        path = rel[: -len(".texture_set.json")]
        base_dir, stem = path.rsplit("/", 1)
        fixes = []

        def put(name, im):
            data = PR.png_bytes(im)
            for root in (D, ROOT / "_staging/pbr" / KEY[b]):
                out = root / base_dir / f"{name}.png"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
            return name
        for k, v in list(ts.items()):
            if k == "color" or not isinstance(v, str) or v.startswith("#"):
                continue
            lp = next((f.parent / (v + e) for e in PR.EXT if (f.parent / (v + e)).exists()), None)
            if lp is None:
                continue
            im = Image.open(lp)
            if k.startswith("metalness"):
                a = np.asarray(im.convert("RGBA")).astype(float)
                bad = (a[..., :3].max() == 0 and a[..., 3].max() == 0) or (
                    a[..., 2].mean() < 20 and a[..., 0].mean() < 128 and PR.material_of(path)[0] not in PR.SHINY_OK)
                if bad:
                    t = PM.thumb(col)
                    d = np.abs(th[..., :3] - t[None, ..., :3]).mean(axis=(1, 2, 3)) + np.abs(th[..., 3] - t[None, ..., 3]).mean(axis=(1, 2)) * 0.5
                    i = int(np.argmin(d))
                    src = keys[i][:-4] + "_s.png"
                    spec = None
                    if d[i] < PR.MATCH_MAX:
                        if src in n256:
                            spec, how = Z256.read(src), "patrix256"
                        elif src in n128:
                            spec, how = Z128.read(src), "patrix128"
                    if spec is not None:
                        mer = MD.mers_156(np.asarray(Image.open(io.BytesIO(spec)).convert("RGBA")))
                        mer_im = PR.resample(Image.fromarray(mer, "RGBA"), size, "mers")
                    else:
                        mer, _ = PR.derive_mers(rgba, path)
                        mer_im, how = Image.fromarray(mer.astype(np.uint8), "RGBA"), "derived " + PR.material_of(path)[0]
                    if k != "metalness_emissive_roughness_subsurface":
                        ts.pop(k)
                    ts["metalness_emissive_roughness_subsurface"] = put(stem + "_mer_fix", mer_im)
                    fixes.append(f"MERS blank/mirror -> {how}")
                    continue
            if im.size != size and not (im.size[0] == size[0] and size[1] % im.size[1] == 0):
                ts[k] = put(f"{v}_{size[0]}x{size[1]}", PR.resample(im, size, "normal" if k == "normal" else "mers"))
                fixes.append(f"{k.split('_')[0]} resampled")
        if fixes:
            if "metalness_emissive_roughness_subsurface" in ts:
                full["format_version"] = "1.21.30"
            txt = json.dumps(full, indent=1)
            for root in (D, ROOT / "_staging/pbr" / KEY[b]):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(txt)
            report.append({"build": b, "set": rel, "fixes": fixes})
    (ROOT / "_docs/blocks/PBR-PHASE6.json").write_text(json.dumps(report, indent=1))
    print("phase 6 repaired sets:", len(report), Counter(x for r in report for x in r["fixes"]).most_common(10))


if __name__ == "__main__":
    main()
