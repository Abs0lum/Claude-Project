#!/usr/bin/env python3
"""build_bp02_213.py — BP-02 1.3.213 from the frozen 1.3.212 (never rebuilt): TREES ON SNOW (D-C513) — every heightmap
tree rule places a search_feature wrapper that also tries the snow-layer cell (tools/tree_snowsafe.py). Scripts unchanged
(clock / land / economy copied from tools/bp02_src for byte-identity). PW_BUILD + manifest 1.3.213."""
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import tree_snowsafe  # noqa: E402

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-212", B / "bp02-213"
S = Path("/home/claude/tools/bp02_src")


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    for f in ["pw_civ_clock.js", "pw_civ_land.js", "pw_civ_economy.js"]:
        shutil.copy2(S / f, DST / "scripts" / f)
    tree_snowsafe.apply(DST)
    mj = DST / "scripts/main.js"
    js = mj.read_text()
    if 'const PW_BUILD = "1.3.212";' not in js:
        raise SystemExit("PW_BUILD line not found")
    mj.write_text(js.replace('const PW_BUILD = "1.3.212";', 'const PW_BUILD = "1.3.213";'))
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [1, 3, 213]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 213]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.213"
    desc = re.sub(r"^v1\.3\.212 \(2026-10-03\) ", "", m["header"]["description"])
    m["header"]["description"] = ("v1.3.213 (2026-10-03) TREES ON SNOW: our trees now grow on snow-covered ground (the root replaces the snow layer; "
                                  "snowy biomes had none of ours). Includes all of v1.3.212: " + desc)[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    t = dep.read_text()
    t2 = t.replace("v1.3.212 (TREEGROW registry reload fix;", "v1.3.213 (trees on snow; TREEGROW registry reload fix;")
    assert t2 != t, "stamp not found"
    dep.write_text(t2)
    print(f"DONE {DST} (manifest 1.3.213)")


if __name__ == "__main__":
    main()
