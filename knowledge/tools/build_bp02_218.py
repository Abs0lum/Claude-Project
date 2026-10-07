#!/usr/bin/env python3
"""build_bp02_218.py — BP-02 1.3.218 from the frozen 1.3.217 (never rebuilt): TREES RE-PROPORTIONED (D-C525, his 14:15
TS1 c "mostly a" / TS2 a / TS3 all species). All 544 templates in structures/pw/trees are re-sampled by
tools/tree_rescale.py (crowns pulled in, bare trunks shortened, jungle crowns lowered, birch unchanged); spruce mature / old
spruce mature / old point at their OWN trunk models (pw_spruce_*_log = the old widths) because RP-01 1.3.120 thickens the
oak / jungle trunk models a little (his TS1 c): measured WITH the bark panels, mature 14 -> 15 cubes, old 15 -> 16 (one full
cell; the models stay inside the cell). Needs RP-01 1.3.120. Template names (and so the falling-copy
index) are unchanged."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-217", B / "bp02-218"


def replace_once(text, old, new, what):
    if text.count(old) != 1:
        raise SystemExit(f"{what}: expected 1 match, found {text.count(old)}")
    return text.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    trees = DST / "structures/pw/trees"
    stage = B / "_stage_trees_218"
    if stage.exists():
        raise SystemExit(f"stale stage dir {stage}")
    r = subprocess.run([sys.executable, "/home/claude/tools/tree_rescale.py", str(SRC / "structures/pw/trees"), str(stage)],
                       capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])
    if r.returncode != 0:
        raise SystemExit("rescale failed")
    n = 0
    for p in sorted(stage.glob("*.mcstructure")):
        shutil.copy2(p, trees / p.name)
        n += 1
    if n != 544:
        raise SystemExit(f"expected 544 templates, got {n}")
    shutil.move(str(stage), str(Path("/home/claude/_garbage") / "stage_trees_218"))
    for rel, old, new in [("blocks/spruce_mature.json", "geometry.pw_oak_mature_log", "geometry.pw_spruce_mature_log"),
                          ("blocks/roots/spruce_mature_root.json", "geometry.pw_oak_mature_log", "geometry.pw_spruce_mature_log"),
                          ("blocks/stumps/spruce_mature_stump.json", "geometry.pw_oak_mature_log", "geometry.pw_spruce_mature_log"),
                          ("blocks/spruce_old.json", "geometry.pw_oak_old_log", "geometry.pw_spruce_old_log"),
                          ("blocks/roots/spruce_old_root.json", "geometry.pw_oak_old_log", "geometry.pw_spruce_old_log"),
                          ("blocks/stumps/spruce_old_stump.json", "geometry.pw_oak_old_log", "geometry.pw_spruce_old_log")]:
        p = DST / rel
        t = p.read_text()
        c = t.count(f'"{old}"')
        if c < 1:
            raise SystemExit(f"{rel}: {old} not found")
        p.write_text(t.replace(f'"{old}"', f'"{new}"'))
        print(f"{rel}: {c} reference(s) -> {new}")
    mj = DST / "scripts/main.js"
    mj.write_text(replace_once(mj.read_text(), 'const PW_BUILD = "1.3.217";', 'const PW_BUILD = "1.3.218";', "PW_BUILD"))
    cp = DST / "scripts/pw_companion.js"
    cp.write_text(replace_once(cp.read_text(), "companion v7 LOADED (pack v1.3.217 ", "companion v7 LOADED (pack v1.3.218 ", "C2 label"))
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [1, 3, 218]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 218]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.218"
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.217 (2026-10-03) "):
        raise SystemExit("description prefix")
    m["header"]["description"] = ("v1.3.218 (2026-10-03) TREES re-proportioned: crowns smaller, bare trunks shorter, jungle crowns lower, "
                                  "birch unchanged (needs RP-01 1.3.120). Includes all of " + desc)[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    dep.write_text(replace_once(dep.read_text(), "v1.3.217 (carbon-copy falling tree, needs RP-01 1.3.119;",
                                "v1.3.218 (trees re-proportioned, needs RP-01 1.3.120; carbon-copy falling tree;", "deps"))
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
