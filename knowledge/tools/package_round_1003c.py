#!/usr/bin/env python3
"""package_round_1003c.py — TREES round 2 (D-C503, 10-03): BP-02 1.3.209 (T4 exact template fall + T5 TREEGROW on templates)
+ PW-TestRunner BP 0.5.16 (lineup p23). Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-209", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_209.mcpack"),
          ("testrunner-0.5.16", "PW-TestRunner-BP-v0_5_16.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
