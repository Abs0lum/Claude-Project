#!/usr/bin/env python3
"""package_round_1002e.py — 3D vines; refuses any archive over the 250 MB cap."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-202", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_202.mcpack"),
          ("rp01-113", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_113.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
