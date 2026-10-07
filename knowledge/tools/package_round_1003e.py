#!/usr/bin/env python3
"""package_round_1003e.py — the REVIEW-WINDOW fix round (D-C508 / D-C509, 10-03): BP-02 1.3.211 (roads laid against the
current street map; a street surface is never re-laid over its own deck; every surface supported from below) + PW-TestRunner
BP 0.5.18 (p22 / p23 setup steps name 1.3.211). Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-211", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_211.mcpack"),
          ("testrunner-0.5.18", "PW-TestRunner-BP-v0_5_18.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
