#!/usr/bin/env python3
"""build_round_1002f.py — ATLAS BUDGET round (his 09:56 Q3 = a + 09:59 Q4 = d 'for today'):
  * leaves stay 256 (all three maps)          * the sand family stays 256 (pw_sand_v1-24 + pw_red_sand_v1-24, colour,
    normal, MERS — "very fine grain when viewing the specular light")
  * every OTHER texture that a terrain key points at and that is 256 wide drops to 192 — its colour AND every layer of
    its texture set (normal re-normalised, MERS / heightmap box-filtered per channel — no premultiply), flipbook strips
    keep their frames (256x4096 -> 192x3072 = 16 frames of 192).
  * no extra sacrifice today (Q4 = d); estimate before: 80.3 Mpx used -> ~60.8.
Only the copy the stack actually uses (the top pack holding the path) and the set layers beside it are rewritten; names,
keys and texture-set JSON stay the same. Packs touched get new build dirs (never rebuilt). Report _docs/blocks/BUILD-1002F.json."""
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

os.environ["PW_STACK"] = "r1002e"
import pbr_round as PR  # noqa: E402
import stack_now as S  # noqa: E402
import block_pbr_census as BC  # noqa: E402

B = ROOT / "_build"
SRC = {"RP-01": "rp01-113", "RP-03": "rp03-64", "RP-04": "rp04-150", "RP-05": "rp05-55", "RP-10": "rp10-148",
       "RP-11": "rp11-137", "RP-08": "rp08-1410"}
VER = {"RP-01": [1, 3, 114], "RP-03": [1, 3, 65], "RP-04": [1, 3, 151], "RP-05": [1, 3, 56], "RP-10": [1, 3, 49],
       "RP-11": [1, 3, 38], "RP-08": [1, 4, 11]}
SAND = re.compile(r"^pw_(red_)?sand_v\d+$")
EXT = (".png", ".tga", ".jpg")


def is_leaf(key, path, who):
    return ("leaves" in path or "leaf" in path or "leaves" in key or "leaf" in key
            or any("leaves" in w[0] for w in who))


def main():
    P = S.packs()
    T = S.terrain(P)
    used = BC.used_keys(P)
    todo = {}                                        # (pack name, path) -> image rel
    kept = Counter()
    for key, (kp, d, _) in T.items():
        who = used.get(key, set())
        for path in S.paths_of(d):
            p, f = S.find_image(P, path)
            if p is None or not p.name.startswith("RP-"):
                continue
            w, h = Image.open(io.BytesIO(p.read(f))).size
            if w != 256:
                continue
            stem = path.rsplit("/", 1)[1]
            if SAND.match(stem):
                kept["sand"] += 1
                continue
            if is_leaf(key, path, who):
                kept["leaf"] += 1
                continue
            todo[(p.name, path)] = f
    packs = sorted({pn[:5] for pn, _ in todo})
    assert set(packs) <= set(SRC), packs
    dst = {}
    for pk in packs:
        d = B / {"RP-01": "rp01-114", "RP-03": "rp03-65", "RP-04": "rp04-151", "RP-05": "rp05-56", "RP-10": "rp10-149",
                  "RP-11": "rp11-138", "RP-08": "rp08-1411"}[pk]
        assert not d.exists(), f"never rebuild {d}"
        dst[pk] = d
    for pk in packs:
        shutil.copytree(B / SRC[pk], dst[pk])
    rep = defaultdict(Counter)
    done = set()
    for (pn, path), f in sorted(todo.items()):
        pk = pn[:5]
        root = dst[pk]
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
            w, h = im.size
            if w != 256:
                rep[pk]["layer not 256 (left)"] += 1
                continue
            size = (192, h * 192 // 256)
            if kind == "color":
                mode = im.mode
                out = PR._bands_resize(im.convert("RGBA") if mode not in ("RGB", "RGBA") else im, size, Image.LANCZOS)
                if mode == "RGB":
                    out = out.convert("RGB")
            else:
                out = PR.resample(im, size, kind)
            if fp.suffix == ".tga":
                out.save(fp, "TGA", compression=None)
            else:
                out.save(fp, optimize=True)
            rep[pk][kind] += 1
    for pk in packs:
        mp = dst[pk] / "manifest.json"
        m = json.loads(re.sub(r"(?m)^\s*//.*$", "", mp.read_text(encoding="utf-8-sig")))
        old = ".".join(map(str, m["header"]["version"]))
        m["header"]["version"] = VER[pk]
        for mod in m["modules"]:
            mod["version"] = VER[pk]
        vs = ".".join(map(str, VER[pk]))
        m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, m["header"]["name"])
        m["header"]["description"] = (f"v{vs} (2026-10-02) Atlas budget: block textures at 256 drop to 192 (colour + depth "
                                      f"+ shine), except leaves and the sand family which stay 256. Includes all of v{old}.")
        assert "pbr" in (m.get("capabilities") or [])
        mp.write_text(json.dumps(m, indent=2))
    out = {"kept_256": dict(kept), "rewritten": {k: dict(v) for k, v in rep.items()},
           "build_dirs": {k: str(v.name) for k, v in dst.items()}}
    (ROOT / "_docs/blocks/BUILD-1002F.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
