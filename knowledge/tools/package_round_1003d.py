#!/usr/bin/env python3
"""package_round_1003d.py — the V6 FIX round (D-C505, 10-03): BP-02 1.3.210 (GS-1: every street run's first cell after a
jog lays its full body + the corner; TREEGROW registry compact + chunked; the [PW-VERSION] banner finally says its own
version) + PW-TestRunner BP 0.5.17 (p22 / p23 setup steps name 1.3.210; the p23 content-log line corrected).
Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-210", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_210.mcpack"),
          ("testrunner-0.5.17", "PW-TestRunner-BP-v0_5_17.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
