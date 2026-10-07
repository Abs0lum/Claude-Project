#!/usr/bin/env python3
"""build_tier_round.py — new versions for the RESOLUTION TIER ROUND (tier_round.py staging, D-C424): copy of the last
DELIVERED build (WeJvidvY, 19:50) + _staging/tier/<key> on top, manifest bumped. Never rebuilds an existing build dir."""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path("/home/claude")
STAGE = ROOT / "_staging/tier"
NOTE = ("RESOLUTION TIERS: dirt family (dirt, coarse dirt, podzol side, rooted dirt, farmland, mud, packed mud, muddy mangrove "
        "roots) and the oak log family at 256 — picture, normal and MERS from the matching Patrix 256 originals, colour-matched "
        "to the previous look; End decor (purpur, end stone bricks, chorus) at 64. Every texture keeps its own set in this pack.")
PACKS = {"rp04": ("rp04-146", "rp04-147", [1, 3, 147]), "rp10": ("rp10-144", "rp10-145", [1, 3, 45]),
         "rp05": ("rp05-52", "rp05-53", [1, 3, 53]), "rp01": ("rp01-108", "rp01-109", [1, 3, 109]),
         "rp03": ("rp03-61", "rp03-62", [1, 3, 62])}


def main():
    out = {}
    for key, (src, dst, ver) in PACKS.items():
        if not (STAGE / key).exists():
            continue
        S, D = ROOT / "_build" / src, ROOT / "_build" / dst
        assert not D.exists(), f"{dst} exists — never rebuild a build dir"
        shutil.copytree(S, D)
        n_new = n_rep = 0
        for f in (STAGE / key).rglob("*"):
            if f.is_file():
                t = D / f.relative_to(STAGE / key)
                n_rep += t.exists()
                n_new += not t.exists()
                t.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, t)
        mf = D / "manifest.json"
        m = json.loads(re.sub(r"(?m)^\s*//.*$", "", mf.read_text(encoding="utf-8-sig")))
        old = ".".join(map(str, m["header"]["version"]))
        v = ".".join(map(str, ver))
        m["header"]["version"] = ver
        for mod in m["modules"]:
            mod["version"] = ver
        m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", f"v{v}", m["header"]["name"])
        m["header"]["description"] = f"v{v} (2026-10-01) {NOTE} Includes all of v{old}."
        mf.write_text(json.dumps(m, indent=1))
        size = sum(p.stat().st_size for p in D.rglob("*") if p.is_file())
        out[key] = {"dir": dst, "new": n_new, "replaced": n_rep, "bytes": size}
        print(f"{key}: {dst} +{n_new} new, {n_rep} replaced, {size / 2**20:.1f} MiB")
    (ROOT / "_docs/blocks/BUILD-TIER-ROUND.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
