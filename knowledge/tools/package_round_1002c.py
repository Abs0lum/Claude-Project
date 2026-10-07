#!/usr/bin/env python3
"""package_round_1002c.py — round 1002c (plank grids)."""
import sys
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [
    ("bp02-201", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_201.mcpack"),
    ("rp04-149", "RP-04-AbsolutRealism-Basic-RP-v1_3_149.mcpack"),
]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
