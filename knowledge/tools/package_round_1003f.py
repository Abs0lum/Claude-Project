#!/usr/bin/env python3
"""package_round_1003f.py — the TREEGROW RELOAD fix (D-C511, 10-03): BP-02 1.3.212 (pending saplings survive a rejoin again)
+ PW-TestRunner BP 0.5.19 (p22 / p23 setup steps name 1.3.212). Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-212", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_212.mcpack"),
          ("testrunner-0.5.19", "PW-TestRunner-BP-v0_5_19.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
