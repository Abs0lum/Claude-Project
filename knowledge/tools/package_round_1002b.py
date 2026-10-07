#!/usr/bin/env python3
"""package_round_1002b.py — round 1002b (plant sway flipbooks)."""
import sys
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [
    ("rp05-55", "RP-05-AbsolutRealism-Flora-RP-v1_3_55.mcpack"),
    ("rp10-147", "RP-10-AbsolutRealism-Terrain-RP-v1_3_47.mcpack"),
    ("rp01-111", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_111.mcpack"),
    ("rp03-64", "RP-03-AbsolutRealism-PBR-RP-v1_3_64.mcpack"),
]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
