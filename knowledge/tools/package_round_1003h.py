#!/usr/bin/env python3
"""package_round_1003h.py — his 12:21 ruling (door recipe Option A, D-C523): BP-02 1.3.216 = frozen 1.3.214 + the oak plank wall
at the Builder's Table only + the [PW-C2] label fix. 1.3.215 stays HELD; numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-216", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_216.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
