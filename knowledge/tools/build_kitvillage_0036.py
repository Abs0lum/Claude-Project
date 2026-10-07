#!/usr/bin/env python3
"""build_kitvillage_0036.py — the gate probe 0.0.36 for BP-02 1.3.225 (STREETS UNLOCKED, every home on the sewer,
fishermen): after every census (0.0.35) also `scriptevent pw:clock sewers` ([CIV-SEWERS]: finished houses that reach the
sewer hall, by hatch / branch, blocked, none); every BEYOND record carries the fishery (spots, fishermen, fish caught,
fish in stock) and the windows given back. Usage: python3 tools/build_kitvillage_0036.py"""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "kitvillage-0.0.35", B / "kitvillage-0.0.36"


def rep(t, old, new, n=1):
    assert t.count(old) == n, (old[:80], t.count(old))
    return t.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["name"] = "PW KitVillage probe 0.0.36 (BDS only)"
    m["header"]["version"] = [0, 0, 36]
    for mod in m["modules"]:
        mod["version"] = [0, 0, 36]
    mp.write_text(json.dumps(m, indent=1))
    p = DST / "scripts/main.js"
    t = p.read_text()
    t = rep(t, 'dim.runCommand("scriptevent pw:clock frontage cottage_m"); } catch { /* old clock */ } ',
            'dim.runCommand("scriptevent pw:clock frontage cottage_m"); dim.runCommand("scriptevent pw:clock sewers"); } catch { /* old clock */ } ', 2)
    t = rep(t, 'log({ step: "beyond", cmd, expect, tier: st && st.tier, plots: blds.size,',
            'log({ step: "beyond", cmd, expect, tier: st && st.tier, plots: blds.size, fishery: st && st.fishery ? { spots: st.fishery.spots.length, cursor: st.fishery.cursor, asleep: st.fishery.asleep || 0 } : null, fishCaught: st && st.fishCaught, fishStock: st && st.ledger && st.ledger.stock ? st.ledger.stock.fish : null, winReleased: st && st.winReleased, branchesLaid: st && st.branchesLaid,')
    p.write_text(t)
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
