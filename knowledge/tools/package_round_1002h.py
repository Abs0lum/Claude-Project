#!/usr/bin/env python3
"""package_round_1002h.py — vine wind + rustle, RP-04 vine copies dropped, desert owl fix; 250 MB cap asserted."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("rp01-115", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_115.mcpack"),
          ("rp04-153", "RP-04-AbsolutRealism-Basic-RP-v1_3_153.mcpack"),
          ("bp02-203", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_203.mcpack"),
          ("stripmine-bp-1313", "PW-StripMine-BP-v1_3_13.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
