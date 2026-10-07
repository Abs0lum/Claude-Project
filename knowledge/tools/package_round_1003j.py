#!/usr/bin/env python3
"""package_round_1003j.py — D-C525 trees re-proportioned: RP-01 1.3.120 + BP-02 1.3.218.
BP-02 1.3.217 (template / lift / turn properties, no lying log: logs drop along the fall line)."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("rp01-120", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_120.mcpack"),
          ("bp02-218", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_218.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
