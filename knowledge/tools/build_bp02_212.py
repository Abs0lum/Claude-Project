#!/usr/bin/env python3
"""build_bp02_212.py — BP-02 1.3.212 from the frozen 1.3.211 (never rebuilt): the TREEGROW REGISTRY RELOAD fix (D-C511).
The compact registry of 1.3.210 / 211 encoded each sapling's type as `Object.keys(PW_GROW_POOLS).indexOf(type)` — but
PW_GROW_POOLS is a Map, so the table was EMPTY, every type saved as -1, and every pending sapling was dropped on reload
(two-run persistence probe growpersist A/B on 211: 6 pending at stop, 0 restored; the instrumented copy showed t=-1).
1.3.209's long form was fine; 210 / 211 lost pending saplings on every rejoin. Fix: the table is [...PW_GROW_POOLS.keys()].
Scripts: the clock / land / economy sources are unchanged from 211 (copied for byte-identity with tools/bp02_src)."""
import json
import re
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-211", B / "bp02-212"
S = Path("/home/claude/tools/bp02_src")


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    for f in ["pw_civ_clock.js", "pw_civ_land.js", "pw_civ_economy.js"]:
        shutil.copy2(S / f, DST / "scripts" / f)
    mj = DST / "scripts/main.js"
    js = mj.read_text()
    old = "const PW_GROW_TYPES = Object.keys(PW_GROW_POOLS);"
    if js.count(old) != 1:
        raise SystemExit("PW_GROW_TYPES line not found once")
    js = js.replace(old, "const PW_GROW_TYPES = [...PW_GROW_POOLS.keys()];      // a Map: Object.keys() was [] (D-C511: every type saved as -1, nothing restored)")
    if 'const PW_BUILD = "1.3.211";' not in js:
        raise SystemExit("PW_BUILD line not found")
    js = js.replace('const PW_BUILD = "1.3.211";', 'const PW_BUILD = "1.3.212";')
    mj.write_text(js)
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [1, 3, 212]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 212]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.212"
    desc = re.sub(r"^v1\.3\.211 \(2026-10-03\) ", "", m["header"]["description"])
    m["header"]["description"] = ("v1.3.212 (2026-10-03) TREEGROW fix: pending saplings survive a rejoin again (the compact registry of 1.3.210/211 "
                                  "saved every type as -1 and restored nothing). Includes all of v1.3.211: " + desc)[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    t = dep.read_text()
    t2 = t.replace("v1.3.211 (roads vs later streets fix;", "v1.3.212 (TREEGROW registry reload fix; roads vs later streets fix;")
    assert t2 != t, "stamp not found"
    dep.write_text(t2)
    print(f"DONE {DST} (manifest 1.3.212, PW_GROW_TYPES from the Map's keys, PW_BUILD 1.3.212)")


if __name__ == "__main__":
    main()
