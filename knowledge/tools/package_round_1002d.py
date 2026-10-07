#!/usr/bin/env python3
"""package_round_1002d.py — size-cap fix; refuses to keep any archive over his 250 MB per-pack cap."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [
    ("rp04-150", "RP-04-AbsolutRealism-Basic-RP-v1_3_150.mcpack"),
    ("rp01-112", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_112.mcpack"),
    ("rp10-148", "RP-10-AbsolutRealism-Terrain-RP-v1_3_48.mcpack"),
]
CAP = 250 * 1000 * 1000
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        print(("SIZE OK " if size <= CAP else "SIZE OVER CAP ") + f"{name} {size:,} B")
        assert size <= CAP, name
