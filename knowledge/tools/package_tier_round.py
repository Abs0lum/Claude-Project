#!/usr/bin/env python3
"""package_tier_round.py — the RESOLUTION TIER ROUND (his 19:50 list, 20:23 H1 = yes) + the two sand depth TEST packs
(20:33 S5 = b, S6 = a: one delivery), through package_std_round.pack (archive == build dir proof, never reuses a name
for different bytes)."""
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [
    ("rp04-147", "RP-04-AbsolutRealism-Basic-RP-v1_3_147.mcpack"),
    ("rp10-145", "RP-10-AbsolutRealism-Terrain-RP-v1_3_45.mcpack"),
    ("rp05-53", "RP-05-AbsolutRealism-Flora-RP-v1_3_53.mcpack"),
    ("rp01-109", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_109.mcpack"),
    ("rp03-62", "RP-03-AbsolutRealism-PBR-RP-v1_3_62.mcpack"),
    ("sandtest-a-100", "PW-SandTest-A-RP-v1_0_0.mcpack"),
    ("sandtest-b-100", "PW-SandTest-B-RP-v1_0_0.mcpack"),
]

if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
