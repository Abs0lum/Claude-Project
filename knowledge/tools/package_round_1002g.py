#!/usr/bin/env python3
"""package_round_1002g.py — dirt family 128; 250 MB cap asserted."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("rp04-152", "RP-04-AbsolutRealism-Basic-RP-v1_3_152.mcpack"),
          ("rp10-150", "RP-10-AbsolutRealism-Terrain-RP-v1_3_50.mcpack"),
          ("rp05-57", "RP-05-AbsolutRealism-Flora-RP-v1_3_57.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
