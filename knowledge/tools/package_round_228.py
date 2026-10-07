#!/usr/bin/env python3
"""package_round_228.py — the program 228 COMBINED delivery (his 15:23: test every new implementation at once): BP-02 1.3.228
(B1–B12 civ mods, role beds, palace spirals + children's beds, fillers, Script API 2.10.0) + RP-04 1.3.159 (silver nickel) + RP-13 1.0.0
(8-block ramps, spiral stairs: split from RP-04 by the 250 MB rule) + RP-01 1.3.125 (tree trunk tips). Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-228", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_228.mcpack"),
          ("rp04-159", "RP-04-AbsolutRealism-Basic-RP-v1_3_159.mcpack"),
          ("rp13-100", "RP-13-AbsolutRealism-Architecture-RP-v1_0_0.mcpack"),
          ("rp01-125", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_125.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
