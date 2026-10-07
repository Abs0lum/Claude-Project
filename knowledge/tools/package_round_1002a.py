#!/usr/bin/env python3
"""package_round_1002a.py — round 1002a (bark ownership + sand B+G2 + vines 256)."""
import sys
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [
    ("rp01-110", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_110.mcpack"),
    ("rp04-148", "RP-04-AbsolutRealism-Basic-RP-v1_3_148.mcpack"),
    ("rp10-146", "RP-10-AbsolutRealism-Terrain-RP-v1_3_46.mcpack"),
    ("rp05-54", "RP-05-AbsolutRealism-Flora-RP-v1_3_54.mcpack"),
    ("rp11-137", "RP-11-AbsolutRealism-Ores-RP-v1_3_37.mcpack"),
    ("rp03-63", "RP-03-AbsolutRealism-PBR-RP-v1_3_63.mcpack"),
]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
