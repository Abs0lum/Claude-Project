#!/usr/bin/env python3
"""build_kitvillage_0039.py — the gate probe 0.0.39 for BP-02 1.3.227 (the 226-2 hang and the 3.6-million-character saved
town): after every skip census it also asks `pw:clock statesize`, so the saved town's size is logged at every tier
([CIV-STATESIZE] lines). Everything else as 0.0.38. Usage: python3 tools/build_kitvillage_0039.py"""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "kitvillage-0.0.38", B / "kitvillage-0.0.39"


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["name"] = "PW KitVillage probe 0.0.39 (BDS only)"
    m["header"]["version"] = [0, 0, 39]
    for mod in m["modules"]:
        mod["version"] = [0, 0, 39]
    mp.write_text(json.dumps(m, indent=1))
    p = DST / "scripts/main.js"
    t = p.read_text()
    old = 'dim.runCommand("scriptevent pw:clock sewers");'
    assert t.count(old) == 2, t.count(old)
    t = t.replace(old, old + ' dim.runCommand("scriptevent pw:clock statesize");')
    p.write_text(t)
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
