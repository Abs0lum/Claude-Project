#!/usr/bin/env python3
"""package_round_1002f.py — atlas budget round; complete install set in one folder; 250 MB cap asserted."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [
    ("rp04-151", "RP-04-AbsolutRealism-Basic-RP-v1_3_151.mcpack"),
    ("rp01-114", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_114.mcpack"),
    ("rp10-149", "RP-10-AbsolutRealism-Terrain-RP-v1_3_49.mcpack"),
    ("rp05-56", "RP-05-AbsolutRealism-Flora-RP-v1_3_56.mcpack"),
    ("rp03-65", "RP-03-AbsolutRealism-PBR-RP-v1_3_65.mcpack"),
    ("rp11-138", "RP-11-AbsolutRealism-Ores-RP-v1_3_38.mcpack"),
    ("rp08-1411", "RP-08-AbsolutRealism-Items-RP-v1_4_11.mcpack"),
]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
