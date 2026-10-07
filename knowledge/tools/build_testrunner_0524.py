#!/usr/bin/env python3
"""build_testrunner_0524.py — PW-TestRunner BP 0.5.24 from 0.5.23 (never touched): the 50 TEST BLOCKS LEAVE THE PACK
(his 21:18 content log: hundreds of 'Missing referenced asset geometry.pw_pilot_* / pw_pilot_*_f0 …' on every load).
Those blocks (24 pw:pilot_* leaf-pilot blocks of lineup p15, 22 pw:t256 / t256m blocks of p17, the culling probe and the
3 xprobes) only resolve with PW-TestRunner RP 0.7.x attached — which carries ~400 extra leaf textures and would eat the
60 Mpx atlas budget, so it is NOT part of the play stack. The experiments concluded (the 256 leaves shipped 10-02), so the
blocks go; lineups p15 / p17 keep their steps and report a missing block type if ever run. Scripts unchanged otherwise."""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "testrunner-0.5.23", B / "testrunner-0.5.24"


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns("blocks"))
    assert not (DST / "blocks").exists()
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [0, 5, 24]
    for mod in m["modules"]:
        mod["version"] = [0, 5, 24]
    m["header"]["name"] = m["header"]["name"].replace("0.5.23", "0.5.24")
    m["header"]["description"] = ("v0.5.24 (2026-10-04) the 50 test blocks (leaf pilot, t256, probes) removed — they needed the TestRunner RP and "
                                  "spammed 'missing asset' errors on every load without it. Includes all of " + m["header"]["description"])[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    js = DST / "scripts/pw_testrunner.js"
    t = js.read_text()
    if t.count("PW Test Runner BP v0.5.23") == 1:
        t = t.replace("PW Test Runner BP v0.5.23", "PW Test Runner BP v0.5.24")
        js.write_text(t)
    dep = DST / "PW-DEPENDENCIES.md"
    dep.write_text(dep.read_text() + "\n\n_v0.5.24: no test blocks any more — the TestRunner RP is only needed for the P0 probe entity and the bump-test mob._\n")
    print("DONE", DST)


if __name__ == "__main__":
    main()
