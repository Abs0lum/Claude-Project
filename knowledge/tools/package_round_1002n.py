#!/usr/bin/env python3
"""package_round_1002n.py — the COMPLETE-SET delivery of round 1002n (D-C470..D-C491): 10 undelivered build dirs."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-206", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_206.mcpack"),
          ("rp01-117", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_117.mcpack"),
          ("rp02-207", "RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_7.mcpack"),
          ("rp03-67", "RP-03-AbsolutRealism-PBR-RP-v1_3_67.mcpack"),
          ("rp04-156", "RP-04-AbsolutRealism-Basic-RP-v1_3_156.mcpack"),
          ("rp06-1429", "RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_29.mcpack"),
          ("rp07-1444", "RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_44.mcpack"),
          ("rp08-1413", "RP-08-AbsolutRealism-Items-RP-v1_4_13.mcpack"),
          ("rp11-140", "RP-11-AbsolutRealism-Ores-RP-v1_3_40.mcpack"),
          ("testrunner-0.5.13", "PW-TestRunner-BP-v0_5_13.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
