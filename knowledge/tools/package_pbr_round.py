#!/usr/bin/env python3
"""package_pbr_round.py — the BLOCK PBR ROUND + LIGHTING delivery (his 19:07 D1 = a), through package_std_round.pack
(archive == build dir proof, never reuses a name for different bytes)."""
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [
    ("rp04-146", "RP-04-AbsolutRealism-Basic-RP-v1_3_146.mcpack"),
    ("rp10-144", "RP-10-AbsolutRealism-Terrain-RP-v1_3_44.mcpack"),
    ("rp05-52", "RP-05-AbsolutRealism-Flora-RP-v1_3_52.mcpack"),
    ("rp11-136", "RP-11-AbsolutRealism-Ores-RP-v1_3_36.mcpack"),
    ("rp01-108", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_108.mcpack"),
    ("rp03-61", "RP-03-AbsolutRealism-PBR-RP-v1_3_61.mcpack"),
    ("rp08-1410", "RP-08-AbsolutRealism-Items-RP-v1_4_10.mcpack"),
    ("rp02-206", "RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_6.mcpack"),
    ("lighttest-sat-100", "PW-LightTest-Saturation-NOW-RP-v1_0_0.mcpack"),
]

if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
