#!/usr/bin/env python3
"""package_round_1003b.py — the TREES round (D-C502, 10-03): BP-02 1.3.208 (square roots, legacy tree rules, grounded
templates) + RP-01 1.3.118 (root sounds). Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-208", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_208.mcpack"),
          ("rp01-118", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_118.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
