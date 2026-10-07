#!/usr/bin/env python3
"""build_bp02_223.py — BP-02 1.3.223 from 1.3.222 (build 21): THE PALACE WITHOUT HIDDEN SPRINGS (10-05 15:2x).
1.3.222 shipped the palace's 4 pieces + 20 stage files with EVERY cell waterlogged (palacegen.cut passed the palette tuple's
block version as the waterlogged flag): every pane, door, ladder, slab and roof wedge was a water source. 1.3.223 = 1.3.222
with the regenerated palace files (layer1 empty, verified) and the version bump. Nothing else changes.
Usage: python3 tools/build_bp02_223.py   (bp02-223 must not exist; bp02-222 must be built from the regenerated staging)"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-222", B / "bp02-223"


def rep(text, old, new, what):
    assert text.count(old) == 1, f"{what}: {text.count(old)} matches"
    return text.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    # the palace files must carry no waterlog layer (the reason for this version)
    n = 0
    for p in sorted((DST / "structures").rglob("mvv_palace_*.mcstructure")):
        st = M.Structure.from_bytes(p.read_bytes())
        wl = sum(1 for k in st.layer1 if k >= 0)
        assert wl == 0, f"{p.name}: {wl} waterlogged cells"
        n += 1
    assert n == 24, n
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = [1, 3, 223]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.223"
    for mod in m["modules"]:
        mod["version"] = [1, 3, 223]
    m["header"]["description"] = ("v1.3.223 (2026-10-05) THE PALACE WITHOUT HIDDEN SPRINGS: 1.3.222's palace pieces were saved with every cell "
                                  "waterlogged (a generator bug) — regenerated dry. Everything of 1.3.222: the city palace, the gallery "
                                  "(6,256 CC0 paintings), the Connoisseur's Book, the well's parapet. Needs RP-01 1.3.123 + RP-12 1.0.0. Personal use.")
    mp.write_text(json.dumps(m, indent=1))
    main_js = (DST / "scripts/main.js").read_text()
    main_js = rep(main_js, 'const PW_BUILD = "1.3.222";', 'const PW_BUILD = "1.3.223";', "PW_BUILD")
    (DST / "scripts/main.js").write_text(main_js)
    comp_p = DST / "scripts/pw_companion.js"
    if comp_p.exists():
        comp = comp_p.read_text()
        if "companion v7 LOADED (pack v1.3.222" in comp:
            comp_p.write_text(comp.replace("companion v7 LOADED (pack v1.3.222", "companion v7 LOADED (pack v1.3.223"))
    print(f"DONE {DST} (24 palace files verified dry; manifest + PW_BUILD 1.3.223)")


if __name__ == "__main__":
    main()
