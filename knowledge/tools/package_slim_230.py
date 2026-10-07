#!/usr/bin/env python3
"""package_slim_230.py — BP-02 1.3.230 SLIM (PS5 join-crash isolation test). Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-230", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_230.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        print(f"SIZE {name} {(Path('/mnt/user-data/outputs') / name).stat().st_size:,} B")
