#!/usr/bin/env python3
"""res128_candidates.py — his 11:53: candidate block/material families to bring to 128 (like stone) to save atlas space.
Counts the USED scope of atlas_budget (images named by a terrain key some block uses, one square tile each, flipbook = one
frame) on the current stack, keeps every image wider than 128 that is NOT a leaf and NOT the sand family (his locked
256 rulings), groups them by family (stem without _v<n> / digits / map suffix) and reports the Mpx saved if that family
went to 128. Output: _docs/blocks/RES128-CANDIDATES.json (+ printed table). Usage: PW_STACK=r1002h res128_candidates.py"""
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
import stack_now as S  # noqa: E402

SAND = re.compile(r"^pw_(red_)?sand_v\d+$")


def family(path):
    stem = path.rsplit("/", 1)[1]
    if "/pw_planks/" in path:
        return "planks grid (pw_planks) " + stem.split("_")[0]
    s = re.sub(r"^pw_", "", stem)
    s = re.sub(r"(_v\d+|_\d+|\d+)$", "", s)
    s = re.sub(r"_(top|side|bottom|end|front|back|inner|outer|on|off|lit)$", "", s)
    s = re.sub(r"(_v\d+|_\d+|\d+)$", "", s)
    return s


def main():
    P = S.packs()
    T = S.terrain(P)
    used = BC.used_keys(P)
    fam = defaultdict(lambda: {"images": 0, "mpx_now": 0.0, "mpx_128": 0.0, "widths": set(), "keys": set(), "blocks": set()})
    seen = set()
    for k in used:
        if k not in T:
            continue
        for path in S.paths_of(T[k][1]):
            if path in seen:
                continue
            p, f = S.find_image(P, path)
            if not p:
                continue
            w, h = Image.open(io.BytesIO(p.read(f))).size
            seen.add(path)
            stem = path.rsplit("/", 1)[1]
            leaf = "leaves" in path or "leaf" in path or "leaves" in k or "leaf" in k or any("leaves" in b[0] for b in used.get(k, ()))
            if w <= 128 or leaf or SAND.match(stem):
                continue
            t = min(w, h)
            F = fam[family(path)]
            F["images"] += 1
            F["mpx_now"] += t * t / 1e6
            F["mpx_128"] += (128 * 128) / 1e6
            F["widths"].add(w)
            F["keys"].add(k)
            F["blocks"].update(b[0] for b in list(used.get(k, ()))[:3])
    rows = []
    for name, F in fam.items():
        rows.append({"family": name, "images": F["images"], "widths": sorted(F["widths"]),
                     "save_mpx": round(F["mpx_now"] - F["mpx_128"], 3), "now_mpx": round(F["mpx_now"], 3),
                     "keys": sorted(F["keys"])[:6], "blocks": sorted(F["blocks"])[:6]})
    rows.sort(key=lambda r: -r["save_mpx"])
    tot = sum(r["save_mpx"] for r in rows)
    (ROOT / "_docs/blocks/RES128-CANDIDATES.json").write_text(json.dumps({"total_if_all_mpx": round(tot, 2), "rows": rows}, indent=1))
    print(f"families {len(rows)}  images {sum(r['images'] for r in rows)}  saving if ALL went to 128: {tot:.2f} Mpx")
    for r in rows[:70]:
        print(f"{r['save_mpx']:6.3f}  {r['images']:4d}  {r['widths']}  {r['family']:40s} {', '.join(r['blocks'][:3])}")


if __name__ == "__main__":
    main()
