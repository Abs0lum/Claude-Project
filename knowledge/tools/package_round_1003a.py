#!/usr/bin/env python3
"""package_round_1003a.py — the V6 CIVITAS delivery (D-C498/D-C499, 10-03): BP-02 1.3.207 (the living town on the land) +
the RECHECK fix round RP-07 1.4.45 / RP-08 1.4.14 + PW-TestRunner 0.5.15 (lineup p22). Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-207", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_207.mcpack"),
          ("rp07-1445", "RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_45.mcpack"),
          ("rp08-1414", "RP-08-AbsolutRealism-Items-RP-v1_4_14.mcpack"),
          ("testrunner-0.5.15", "PW-TestRunner-BP-v0_5_15.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
