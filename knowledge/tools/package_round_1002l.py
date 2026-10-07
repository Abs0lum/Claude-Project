#!/usr/bin/env python3
"""package_round_1002l.py — ores rebuilt: RP-11 1.3.39 (all 18 ores, maps in-pack) + RP-04 1.3.155 (ore copies removed)."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("rp11-139", "RP-11-AbsolutRealism-Ores-RP-v1_3_39.mcpack"),
          ("rp04-155", "RP-04-AbsolutRealism-Basic-RP-v1_3_155.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
