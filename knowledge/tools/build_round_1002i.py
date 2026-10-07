#!/usr/bin/env python3
"""build_round_1002i.py — his 12:02:
  S7 = a2: sand glint grains become NON-METAL (quartz-like): MERS [128,0,12,12] -> [0,0,26,12] (metalness 0,
           roughness 0.10). His S8 = dark dots at noon = the predicted mechanism (metal grains get no diffuse light).
           Only pw_sand_v1-24 carry grains (red sand never had them). Colour + normal untouched; sand stays 256.
  R1 = rows 1,2,3,4,7,9,10 of the 128 candidate table (tools/res128_candidates.py groups, same order of rules):
       plank grids, nether nylium, mud family, logs / bark, workstations, mycelium, copper chains + lanterns
       -> 128 (colour + every texture-set layer; normal re-normalised, MERS per channel; strips keep their frames).
Only the copy the stack uses (r1002h) and the layers beside it are rewritten. New build dirs, never rebuilt.
Report _docs/blocks/BUILD-1002I.json."""
import io
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import os  # noqa: E402

os.environ["PW_STACK"] = "r1002h"
import block_pbr_census as BC  # noqa: E402
import pbr_round as PR  # noqa: E402
import res128_candidates as RC  # noqa: E402
import stack_now as S  # noqa: E402

B = ROOT / "_build"
EXT = (".png", ".tga", ".jpg")
SRC = {"RP-01": "rp01-115", "RP-03": "rp03-65", "RP-04": "rp04-153", "RP-05": "rp05-57", "RP-10": "rp10-150",
       "RP-11": "rp11-138", "RP-08": "rp08-1411"}
DST = {"RP-01": ("rp01-116", [1, 3, 116]), "RP-03": ("rp03-66", [1, 3, 66]), "RP-04": ("rp04-154", [1, 3, 154]),
       "RP-05": ("rp05-58", [1, 3, 58]), "RP-10": ("rp10-151", [1, 3, 51]), "RP-11": ("rp11-139", [1, 3, 39]),
       "RP-08": ("rp08-1412", [1, 4, 12])}
WORK = ("furnace", "smoker", "stonecutter", "lectern", "anvil", "enchant", "crafting", "loom", "barrel", "cartography",
        "fletching", "smithing", "grindstone", "composter", "bookshelf", "beehive", "bee_nest")
PLANTS = ("bamboo", "petal", "propagule", "firefly", "tall_grass", "flower", "fern", "bush", "sapling", "dandelion", "poppy",
          "tulip", "orchid", "allium", "azure", "daisy", "cornflower", "lily", "rose", "peony", "lilac", "sunflower",
          "mushroom", "vine", "sugar", "cactus", "dripleaf", "azalea", "moss", "grass", "berry", "wheat", "carrot", "potato",
          "beet", "melon", "pumpkin", "cocoa", "wart", "seagrass", "kelp", "coral", "spore", "roots")
# the SAME ordered rules as the 11:53 table (first match wins)
RULES = [(1, lambda f: f.startswith("planks grid")),
         (6, lambda f: f == "grass_block" or f == "grass"),
         (2, lambda f: "nylium" in f),
         (3, lambda f: "mud" in f),
         (9, lambda f: f == "mycelium"),
         (11, lambda f: f == "snow"),
         (4, lambda f: f.endswith("_log") or "log" in f or "stem" in f or "hyphae" in f),
         (8, lambda f: "ore" in f and "core" not in f),
         (7, lambda f: any(x in f for x in WORK)),
         (5, lambda f: any(x in f for x in PLANTS)),
         (10, lambda f: "copper" in f),
         (12, lambda f: f in ("ice", "blue_ice", "packed_ice", "obsidian", "crying_obsidian") or "farmland" in f)]
CHOSEN = {1, 2, 3, 4, 7, 9, 10}
SAND = re.compile(r"^pw_(red_)?sand_v\d+$")
GRAIN_OLD = np.array([128, 0, 12, 12], np.uint8)
GRAIN_NEW = np.array([0, 0, 26, 12], np.uint8)


def row_of(fam):
    for r, fn in RULES:
        if fn(fam):
            return r
    return 13


def main():
    P = S.packs()
    T = S.terrain(P)
    used = BC.used_keys(P)
    todo = {}                                  # (pack, path) -> (image rel, row)
    sand = {}
    seen = set()
    for k in used:
        if k not in T:
            continue
        for path in S.paths_of(T[k][1]):
            if path in seen:
                continue
            seen.add(path)
            p, f = S.find_image(P, path)
            if p is None or p.name[:5] not in SRC:
                continue
            stem = path.rsplit("/", 1)[1]
            if SAND.match(stem):
                sand[(p.name[:5], path)] = f
                continue
            w, h = Image.open(io.BytesIO(p.read(f))).size
            leaf = "leaves" in path or "leaf" in path or "leaves" in k or "leaf" in k or any("leaves" in b[0] for b in used.get(k, ()))
            if w <= 128 or leaf:
                continue
            r = row_of(RC.family(path))
            if r in CHOSEN:
                todo[(p.name[:5], path)] = (f, r)
    packs = sorted({pk for pk, _ in todo} | {pk for pk, _ in sand})
    for pk in packs:
        assert not (B / DST[pk][0]).exists(), f"never rebuild {DST[pk][0]}"
    for pk in packs:
        shutil.copytree(B / SRC[pk], B / DST[pk][0])
    rep = defaultdict(Counter)
    rows = Counter()
    done = set()
    for (pk, path), (f, r) in sorted(todo.items()):
        root = B / DST[pk][0]
        files = [(f, "color")]
        sp = root / (path + ".texture_set.json")
        if sp.exists():
            ts = json.loads(sp.read_text())["minecraft:texture_set"]
            base = path.rsplit("/", 1)[0]
            for kk, v in ts.items():
                if kk == "color" or not isinstance(v, str) or v.startswith("#"):
                    continue
                lf = next((f"{base}/{v}{e}" for e in EXT if (root / f"{base}/{v}{e}").exists()), None)
                if lf:
                    files.append((lf, "normal" if kk == "normal" else "mers"))
        rows[r] += 1
        for rel, kind in files:
            if (pk, rel) in done:
                continue
            done.add((pk, rel))
            fp = root / rel
            im = Image.open(fp)
            w, h = im.size
            if w <= 128:
                rep[pk]["layer already <=128 (left)"] += 1
                continue
            size = (128, h * 128 // w)
            assert (h * 128) % w == 0, (rel, im.size)            # strips keep whole frames
            if kind == "color":
                mode = im.mode
                out = PR._bands_resize(im if mode in ("RGB", "RGBA") else im.convert("RGBA"), size, Image.LANCZOS)
            else:
                out = PR.resample(im, size, kind)
            out.save(fp, "TGA", compression=None) if fp.suffix == ".tga" else out.save(fp, optimize=True)
            rep[pk][kind] += 1
    # sand grains -> non-metal
    gpx = 0
    for (pk, path), f in sorted(sand.items()):
        root = B / DST[pk][0]
        sp = root / (path + ".texture_set.json")
        if not sp.exists():
            continue
        ts = json.loads(sp.read_text())["minecraft:texture_set"]
        mv = ts.get("metalness_emissive_roughness_subsurface")
        if not isinstance(mv, str):
            continue
        base = path.rsplit("/", 1)[0]
        mp = next((root / f"{base}/{mv}{e}" for e in EXT if (root / f"{base}/{mv}{e}").exists()), None)
        a = np.asarray(Image.open(mp).convert("RGBA")).copy()
        g = (a == GRAIN_OLD).all(-1)
        if g.any():
            a[g] = GRAIN_NEW
            Image.fromarray(a, "RGBA").save(mp, optimize=True)
            gpx += int(g.sum())
            rep[pk]["sand MERS grains -> non-metal"] += 1
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
        m["header"]["description"] = (f"v{vs} (2026-10-02) Atlas space: plank grids, nylium, mud family, logs/bark, "
                                      f"workstations, mycelium, copper chains/lanterns at 128 with their maps; sand glint "
                                      f"grains non-metal (no dark dots at noon). Includes all of v{old}.")
        assert "pbr" in (m.get("capabilities") or [])
        mp.write_text(json.dumps(m, indent=2))
    out = {"images_128": len(todo), "per_row": dict(sorted(rows.items())), "sand_grain_px": gpx,
           "rewritten": {k: dict(v) for k, v in rep.items()}, "dirs": {k: DST[k][0] for k in packs}}
    (ROOT / "_docs/blocks/BUILD-1002I.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
