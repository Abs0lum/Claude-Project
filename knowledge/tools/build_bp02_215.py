#!/usr/bin/env python3
"""build_bp02_215.py — BP-02 1.3.215 candidate from the frozen 1.3.214 (never rebuilt): the TREE SEARCH STEP (D-C519, his Q6(b)).
The delivered tree rules place each template at the heightmap; where a grass tuft, fern, flower or thin snow layer sits on that
spot the root lands ON it and `grounded` refuses the tree (pads, civtest-20261003-064535). A minecraft:search_feature wrapper per
pool tries y-2 -> y so the root replaces the plant / layer and stands on the ground. 23 heightmap tree rules -> 10 wrappers;
EVERY template feature untouched (unlike 1.3.213, whose snow allowlist + solid-only intersection added ~nothing: census
0.0.10, identical chunks: 214 48 trees · search-only 91 · 213 92). HELD for his ruling (a visible density change) — built and
gated, not delivered until he says take it. 1.3.213 stays held/undelivered; its number is never reused."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import tree_snowsafe as T  # noqa: E402  (the wrapper() shape only — its template retune is NOT used here)

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-214", B / "bp02-215"


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    changed, wrappers = 0, {}
    for p in sorted((DST / "feature_rules").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8-sig"))
        fr = d["minecraft:feature_rules"]
        feat = fr["description"]["places_feature"]
        y = fr.get("distribution", {}).get("y")
        if not (isinstance(y, str) and "heightmap" in y):
            continue
        if not ("tree" in feat or "mix_" in feat or "bush" in feat):
            continue
        stem = feat.split(":")[1].replace("_feature", "")
        wid = f"pw:snowsafe_{stem}_feature"
        wrappers[wid] = feat
        fr["description"]["places_feature"] = wid
        p.write_text(json.dumps(d, indent=1))
        changed += 1
    for wid, target in wrappers.items():
        (DST / "features" / f"{wid.split(':')[1]}.json").write_text(json.dumps(T.wrapper(wid, target), indent=1))
    if (changed, len(wrappers)) != (23, 10):
        raise SystemExit(f"expected 23 rules / 10 wrappers, got {changed} / {len(wrappers)}")
    mj = DST / "scripts/main.js"
    js = mj.read_text()
    if js.count('const PW_BUILD = "1.3.214";') != 1:
        raise SystemExit("PW_BUILD line not found once")
    mj.write_text(js.replace('const PW_BUILD = "1.3.214";', 'const PW_BUILD = "1.3.215";'))
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [1, 3, 215]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 215]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.215"
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.214 (2026-10-03) "):
        raise SystemExit("description prefix not found")
    m["header"]["description"] = ("v1.3.215 (2026-10-03) trees: a tree whose spot holds a grass tuft, fern, flower or thin snow layer is no longer refused "
                                  "(a 2-block search lets its root replace the plant) — about twice today's forest density. Includes all of " + desc)[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    t = dep.read_text()
    t2 = t.replace("v1.3.214 (light blocks cleared again: flattened ids;", "v1.3.215 (tree search step: plants / snow layers no longer refuse a tree; light blocks cleared again: flattened ids;", 1)
    if t2 == t:
        raise SystemExit("PW-DEPENDENCIES stamp not found")
    dep.write_text(t2)
    print(f"DONE {DST}: {changed} rules -> {len(wrappers)} search wrappers, templates untouched, PW_BUILD + manifest 1.3.215 (HELD)")


if __name__ == "__main__":
    main()
