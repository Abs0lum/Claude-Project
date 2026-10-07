#!/usr/bin/env python3
"""verify_pbr_round.py — static gates for the block PBR round builds (P1: these only rule OUT):
 G1 every *.texture_set.json in each new build parses; G2 every layer it names exists IN THE SAME PACK (H-18);
 G3 layer sizes equal the colour (strips: same width, height a multiple); G4 no MERS layer is all zero, no block MERS has
 roughness mean < 20 unless metal / glass / ice / smooth quartz; G5 every JSON file parses; G6 the census on the new stack
 shows 0 SHADOWED; G7 manifests: name version == header version == module version."""
import io
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
BUILDS = ["rp04-146", "rp05-52", "rp10-144", "rp11-136", "rp01-108", "rp03-61", "rp08-1410"]
import os as _os
if _os.environ.get("PW_STACK") == "r1002m":
    BUILDS = ["rp04-156", "rp05-58", "rp10-151", "rp11-140", "rp01-116", "rp03-67", "rp08-1412"]
elif _os.environ.get("PW_STACK") == "r1002l":
    BUILDS = ["rp04-155", "rp05-58", "rp10-151", "rp11-139", "rp01-116", "rp03-66", "rp08-1412"]
elif _os.environ.get("PW_STACK") == "r1002i":
    BUILDS = ["rp04-154", "rp05-58", "rp10-151", "rp11-138", "rp01-116", "rp03-66", "rp08-1412"]
elif _os.environ.get("PW_STACK") == "r1002h":
    BUILDS = ["rp04-153", "rp05-57", "rp10-150", "rp11-138", "rp01-115", "rp03-65", "rp08-1411"]
elif _os.environ.get("PW_STACK") == "r1002g":
    BUILDS = ["rp04-152", "rp05-57", "rp10-150", "rp11-138", "rp01-114", "rp03-65", "rp08-1411"]
elif _os.environ.get("PW_STACK") == "r1002f":
    BUILDS = ["rp04-151", "rp05-56", "rp10-149", "rp11-138", "rp01-114", "rp03-65", "rp08-1411"]
elif _os.environ.get("PW_STACK") == "r1002e":
    BUILDS = ["rp04-150", "rp05-55", "rp10-148", "rp11-137", "rp01-113", "rp03-64", "rp08-1410"]
elif _os.environ.get("PW_STACK") == "r1002d":
    BUILDS = ["rp04-150", "rp05-55", "rp10-148", "rp11-137", "rp01-112", "rp03-64", "rp08-1410"]
elif _os.environ.get("PW_STACK") == "r1002c":
    BUILDS = ["rp04-149", "rp05-55", "rp10-147", "rp11-137", "rp01-111", "rp03-64", "rp08-1410"]
elif _os.environ.get("PW_STACK") == "r1002b":
    BUILDS = ["rp04-148", "rp05-55", "rp10-147", "rp11-137", "rp01-111", "rp03-64", "rp08-1410"]
elif _os.environ.get("PW_STACK") == "r1002a":
    BUILDS = ["rp04-148", "rp05-54", "rp10-146", "rp11-137", "rp01-110", "rp03-63", "rp08-1410"]
elif _os.environ.get("PW_STACK") == "tier":
    BUILDS = ["rp04-147", "rp05-53", "rp10-145", "rp11-136", "rp01-109", "rp03-62", "rp08-1410"]
EXT = (".tga", ".png", ".jpg", ".jpeg")
OK_SHINY = re.compile(r"(iron|gold|copper|netherite|chain|lantern|anvil|rail|glass|ice|quartz|water|amethyst|diamond|emerald|"
                      r"prismarine|experience_orb|obsidian|glazed|slime|honey|magma|lava|sculk|end_rod|beacon|conduit)", re.I)


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def main():
    fails, n_sets = [], 0
    for b in BUILDS:
        D = ROOT / "_build" / b
        for f in D.rglob("*.json"):
            try:
                jl(f)
            except Exception as e:  # noqa: BLE001
                if not f.name.endswith(".texture_set.json"):
                    fails.append(("G5", b, str(f.relative_to(D)), str(e)[:60]))
        m = jl(D / "manifest.json")
        v = ".".join(map(str, m["header"]["version"]))
        if f"v{v}" not in m["header"]["name"] or any(mod["version"] != m["header"]["version"] for mod in m["modules"]):
            fails.append(("G7", b, m["header"]["name"], v))
        for f in D.rglob("*.texture_set.json"):
            n_sets += 1
            rel = str(f.relative_to(D))
            try:
                ts = jl(f)["minecraft:texture_set"]
            except Exception as e:  # noqa: BLE001
                fails.append(("G1", b, rel, str(e)[:60]))
                continue
            sizes = {}
            for k, v in ts.items():
                if not isinstance(v, str) or v.startswith("#"):
                    continue
                cand = [f.parent / (v + e) for e in EXT if (f.parent / (v + e)).exists()]
                if not cand:
                    fails.append(("G2", b, rel, f"{k}={v}"))
                    continue
                im = Image.open(cand[0])
                sizes[k] = im.size
                if k.startswith("metalness"):
                    a = np.asarray(im.convert("RGBA")).astype(float)
                    if a[..., :3].max() == 0 and a[..., 3].max() == 0 and not re.search(r"(glass|portal)", rel):
                        # (a perfectly smooth dielectric is right for glass / the portal; everywhere else it is the
                        #  premultiplied-resize bug)
                        fails.append(("G4", b, rel, "MERS all zero"))
                    elif a[..., 2].mean() < 20 and a[..., 0].mean() < 128 and not OK_SHINY.search(rel):
                        fails.append(("G4", b, rel, f"roughness mean {a[..., 2].mean():.0f}"))
            c = sizes.get("color")
            for k, s in sizes.items():
                if c and s != c and not (s[0] == c[0] and c[1] % s[1] == 0):
                    fails.append(("G3", b, rel, f"{k} {s} vs colour {c}"))
    import os
    os.environ["PW_STACK"] = os.environ.get("PW_STACK") or "pbr"
    import importlib
    import stack_now
    importlib.reload(stack_now)
    import block_pbr_census as BC
    importlib.reload(BC)
    rows, _ = BC.main()
    sh = {r["path"] for r in rows if any(s.startswith("SHADOWED") for s in r["status"])}
    if sh:
        fails.append(("G6", "stack", f"{len(sh)} shadowed", sorted(sh)[:3]))
    from collections import Counter
    print(f"sets checked {n_sets} · fails {len(fails)}", dict(Counter(x[0] for x in fails)))
    for x in fails[:40]:
        print("  ", x)
    (ROOT / "_docs/blocks/VERIFY-PBR-ROUND.json").write_text(json.dumps(fails, indent=1, default=str))
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
