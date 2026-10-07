#!/usr/bin/env python3
"""atlas_budget.py — Atlas Budget Law estimate (terrain atlas = one 8192^2 sheet; keep referenced block textures under
~60 Mpx). Counts every distinct image the merged terrain_texture keys point at, one square tile each (a flipbook strip
counts one frame), at its real size — two scopes: ALL keys, and USED keys (named by any block: effective blocks.json incl.
vanilla, BP material instances). Then 'what if' scenarios: a = pw_planks tiles 256->192, b = every texture of keys with
16+ variations at 256 -> 192, a+b. Usage: PW_STACK=<stack> atlas_budget.py   -> _docs/blocks/ATLAS-BUDGET.json"""
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import block_pbr_census as BC  # noqa: E402
import stack_now as S  # noqa: E402


def main():
    P = S.packs()
    T = S.terrain(P)
    used = set(BC.used_keys(P))
    size = {}
    key_paths = {}
    for k, (pn, d, _) in T.items():
        key_paths[k] = S.paths_of(d)
        for path in key_paths[k]:
            if path in size:
                continue
            p, f = S.find_image(P, path)
            if not p:
                continue
            try:
                w, h = Image.open(io.BytesIO(p.read(f))).size
            except Exception:  # noqa: BLE001
                continue
            size[path] = (w, min(w, h))
    big = {path for k, ps in key_paths.items() if len(ps) >= 16 for path in ps if path in size and size[path][0] == 256}
    planks = {path for path in size if "/pw_planks/" in path}

    def total(paths, shrink=frozenset()):
        t = 0
        for path in paths:
            w, h = size[path]
            if path in shrink:
                w, h = w * 3 // 4, h * 3 // 4
            t += w * h
        return t / 1e6
    all_p = set(size)
    used_p = {p for k in used if k in key_paths for p in key_paths[k] if p in size}
    out = {}
    for scope, ps in (("all keys", all_p), ("used keys", used_p)):
        all256 = {q for q in ps if size[q][0] == 256}
        out[scope] = {"now": round(total(ps), 1), "a planks 192": round(total(ps, planks), 1),
                      "b 16-variant families 192": round(total(ps, big), 1), "a+b": round(total(ps, planks | big), 1),
                      "a+b + every other 256 texture 192": round(total(ps, planks | big | all256), 1)}
    cat = defaultdict(float)
    for path in used_p:
        w, h = size[path]
        name = path.rsplit("/", 1)[1]
        c = ("planks grid" if "/pw_planks/" in path else "16+ variant families @256" if path in big else
             f"{w}px other")
        cat[c] += w * h / 1e6
    out["used breakdown Mpx"] = {k: round(v, 1) for k, v in sorted(cat.items(), key=lambda x: -x[1])}
    out["counts"] = {"images all": len(all_p), "images used": len(used_p), "planks tiles": len(planks),
                     "16+variant 256 images": len(big)}
    (ROOT / "_docs/blocks/ATLAS-BUDGET.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
