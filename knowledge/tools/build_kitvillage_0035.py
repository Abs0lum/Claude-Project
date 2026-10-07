#!/usr/bin/env python3
"""build_kitvillage_0035.py — the gate probe 0.0.35 for BP-02 1.3.225 (GROWTH DIAGNOSIS, his 20:01 "let's fix the city
growth issues"): after every skip from town I on, `scriptevent pw:clock frontage cottage_m` (the census prints a
[CIV-FRONTAGE] line: every street, both sides, packed with a medium cottage, each refused position charged to its first
rule); the BEYOND ladder climbs to METROPOLIS III (grow + skip 24 each). Usage: python3 tools/build_kitvillage_0035.py"""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "kitvillage-0.0.34", B / "kitvillage-0.0.35"


def rep(t, old, new):
    assert t.count(old) == 1, old[:80]
    return t.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["name"] = "PW KitVillage probe 0.0.35 (BDS only)"
    m["header"]["version"] = [0, 0, 35]
    for mod in m["modules"]:
        mod["version"] = [0, 0, 35]
    mp.write_text(json.dumps(m, indent=1))
    p = DST / "scripts/main.js"
    t = p.read_text()
    census = ('    if (cmd.startsWith("skip") && !/^village/.test(expect)) { try { dim.runCommand("scriptevent pw:clock frontage cottage_m"); } catch { /* old clock */ } '
              'await sleep(10); }   // 0.0.35: the frontage census\n')
    t = rep(t, "    await waitQueue(dim, cmd, 200);\n    await readback(dim);\n", "    await waitQueue(dim, cmd, 200);\n    await readback(dim);\n" + census)
    t = rep(t, "      await waitQueue(dim, cmd, 400);\n      await readback(dim);\n", "      await waitQueue(dim, cmd, 400);\n      await readback(dim);\n  " + census)
    t = rep(t, '[["grow", "CITY III"], ["skip 24", "city III built"], ["grow", "METROPOLIS"], ["skip 24", "metropolis built"]]',
            '[["grow", "CITY III"], ["skip 24", "city III built"], ["grow", "METROPOLIS"], ["skip 24", "metropolis built"], '
            '["grow", "METROPOLIS II"], ["skip 24", "metropolis II built"], ["grow", "METROPOLIS III"], ["skip 24", "metropolis III built"]]')
    p.write_text(t)
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
