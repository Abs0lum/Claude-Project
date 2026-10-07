#!/usr/bin/env python3
"""res128_variants.py — his 12:02 R2: the families ALREADY at 128 (used scope of atlas_budget) ranked by atlas space, with
their variant counts and what cutting variants would save (to 12 and to 8 per key family). Leaves + sand excluded (256
rulings). Output _docs/blocks/RES128-VARIANTS.json. Usage: PW_STACK=<stack> res128_variants.py"""
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import block_pbr_census as BC  # noqa: E402
import res128_candidates as RC  # noqa: E402
import stack_now as S  # noqa: E402


def main():
    P = S.packs()
    T = S.terrain(P)
    used = BC.used_keys(P)
    fam = defaultdict(lambda: {"images": set(), "keys": set(), "blocks": set()})
    for k in used:
        if k not in T:
            continue
        for path in S.paths_of(T[k][1]):
            p, f = S.find_image(P, path)
            if not p:
                continue
            w, h = Image.open(io.BytesIO(p.read(f))).size
            if w != 128 or "leaves" in path or "leaf" in path:
                continue
            F = fam[RC.family(path)]
            F["images"].add(path)
            F["keys"].add(k)
            F["blocks"].update(b[0] for b in list(used.get(k, ()))[:4])
    tile = 128 * 128 / 1e6
    rows = []
    for name, F in fam.items():
        n = len(F["images"])
        rows.append({"family": name, "images": n, "mpx": round(n * tile, 3),
                     "save_to_12": round(max(0, n - 12) * tile, 3), "save_to_8": round(max(0, n - 8) * tile, 3),
                     "keys": len(F["keys"]), "blocks": sorted(F["blocks"])[:4]})
    rows.sort(key=lambda r: -r["mpx"])
    tot = sum(r["mpx"] for r in rows)
    out = {"families": len(rows), "images": sum(r["images"] for r in rows), "mpx_total": round(tot, 2),
           "save_all_to_12": round(sum(r["save_to_12"] for r in rows), 2), "save_all_to_8": round(sum(r["save_to_8"] for r in rows), 2),
           "rows": rows}
    (ROOT / "_docs/blocks/RES128-VARIANTS.json").write_text(json.dumps(out, indent=1))
    print({k: v for k, v in out.items() if k != "rows"})
    for r in rows[:45]:
        print(f"{r['images']:4d} img {r['mpx']:6.3f}  ->12 saves {r['save_to_12']:5.3f}  ->8 saves {r['save_to_8']:5.3f}  {r['family']:34s} {', '.join(r['blocks'][:3])}")


if __name__ == "__main__":
    main()
