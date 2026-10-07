#!/usr/bin/env python3
"""package_round_1002i.py — 128 round (rows 1,2,3,4,7,9,10) + sand grains non-metal; 250 MB cap asserted."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("rp04-154", "RP-04-AbsolutRealism-Basic-RP-v1_3_154.mcpack"),
          ("rp01-116", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_116.mcpack"),
          ("rp10-151", "RP-10-AbsolutRealism-Terrain-RP-v1_3_51.mcpack"),
          ("rp05-58", "RP-05-AbsolutRealism-Flora-RP-v1_3_58.mcpack"),
          ("rp03-66", "RP-03-AbsolutRealism-PBR-RP-v1_3_66.mcpack"),
          ("rp08-1412", "RP-08-AbsolutRealism-Items-RP-v1_4_12.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
