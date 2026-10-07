#!/usr/bin/env python3
"""build_round_1002g.py — his 10:11: "bring our dirt variants to 128, that should clear the last of it".
Measured (used-textures count, r1002f = 60.81 Mpx): dirt + coarse dirt alone -> 60.12 (still over); with the rest of the
dirt family — rooted dirt, podzol (top + side), dirt path — -> 59.40. So the whole dirt family 192 -> 128: colour + every
set layer (normal re-normalised, MERS per channel), only the copy the stack uses and the layers beside it.
New build dirs from the round-1002f dirs: rp04-152, rp05-57, rp10-150 (whichever hold the images)."""
import io
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import os  # noqa: E402

os.environ["PW_STACK"] = "r1002f"
import pbr_round as PR  # noqa: E402
import stack_now as S  # noqa: E402

B = ROOT / "_build"
SRC = {"RP-04": "rp04-151", "RP-05": "rp05-56", "RP-10": "rp10-149"}
DST = {"RP-04": ("rp04-152", [1, 3, 152]), "RP-05": ("rp05-57", [1, 3, 57]), "RP-10": ("rp10-150", [1, 3, 50])}
FAMILY = re.compile(r"^(dirt(_v\d+)?|coarse_dirt(_v\d+)?|rooted_dirt.*|dirt_podzol.*|grass_path.*|dirt_path.*)$")
EXT = (".png", ".tga", ".jpg")


def main():
    P = S.packs()
    T = S.terrain(P)
    todo = {}
    for key, (kp, d, _) in T.items():
        for path in S.paths_of(d):
            if not FAMILY.match(path.rsplit("/", 1)[1]):
                continue
            p, f = S.find_image(P, path)
            if p is None or p.name[:5] not in SRC:
                continue
            if Image.open(io.BytesIO(p.read(f))).size[0] != 192:
                continue
            todo[(p.name[:5], path)] = f
    packs = sorted({pk for pk, _ in todo})
    for pk in packs:
        assert not (B / DST[pk][0]).exists(), f"never rebuild {DST[pk][0]}"
    for pk in packs:
        shutil.copytree(B / SRC[pk], B / DST[pk][0])
    rep = defaultdict(Counter)
    done = set()
    for (pk, path), f in sorted(todo.items()):
        root = B / DST[pk][0]
        files = [(f, "color")]
        sp = root / (path + ".texture_set.json")
        if sp.exists():
            ts = json.loads(sp.read_text())["minecraft:texture_set"]
            base = path.rsplit("/", 1)[0]
            for k, v in ts.items():
                if k == "color" or not isinstance(v, str) or v.startswith("#"):
                    continue
                lf = next((f"{base}/{v}{e}" for e in EXT if (root / f"{base}/{v}{e}").exists()), None)
                if lf:
                    files.append((lf, "normal" if k == "normal" else "mers"))
        for rel, kind in files:
            if (pk, rel) in done:
                continue
            done.add((pk, rel))
            fp = root / rel
            im = Image.open(fp)
            if im.size[0] != 192:
                rep[pk]["skipped (not 192)"] += 1
                continue
            size = (128, im.size[1] * 128 // 192)
            if kind == "color":
                out = PR._bands_resize(im if im.mode in ("RGB", "RGBA") else im.convert("RGBA"), size, Image.LANCZOS)
            else:
                out = PR.resample(im, size, kind)
            out.save(fp, "TGA", compression=None) if fp.suffix == ".tga" else out.save(fp, optimize=True)
            rep[pk][kind] += 1
    for pk in packs:
        d, ver = DST[pk]
        mp = B / d / "manifest.json"
        m = json.loads(re.sub(r"(?m)^\s*//.*$", "", mp.read_text(encoding="utf-8-sig")))
        old = ".".join(map(str, m["header"]["version"]))
        m["header"]["version"] = ver
        for mod in m["modules"]:
            mod["version"] = ver
        vs = ".".join(map(str, ver))
        m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, m["header"]["name"])
        m["header"]["description"] = (f"v{vs} (2026-10-02) Atlas budget: the dirt family (dirt, coarse dirt, rooted dirt, "
                                      f"podzol, dirt path) at 128 with its maps. Includes all of v{old}.")
        assert "pbr" in (m.get("capabilities") or [])
        mp.write_text(json.dumps(m, indent=2))
    out = {"images": len(todo), "rewritten": {k: dict(v) for k, v in rep.items()}, "dirs": {k: DST[k][0] for k in packs}}
    (ROOT / "_docs/blocks/BUILD-1002G.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
