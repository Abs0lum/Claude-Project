#!/usr/bin/env python3
"""package_round_1002j.py — BP-02 1.3.204 (plank neighbour rule); 250 MB cap asserted."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-204", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_204.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
