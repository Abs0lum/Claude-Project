#!/usr/bin/env python3
"""package_fix_229.py — BP-02 1.3.229 + RP-13 1.0.1 (the spiral geometry fix). Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-229", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_229.mcpack"),
          ("rp13-101", "RP-13-AbsolutRealism-Architecture-RP-v1_0_1.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
