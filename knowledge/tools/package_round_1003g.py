#!/usr/bin/env python3
"""package_round_1003g.py — the LIGHT-BLOCK fix (D-C515, 10-03): BP-02 1.3.214 (mob lights + golden-crown light are removed again:
1.26 reports minecraft:light_block_<level>) + PW-TestRunner BP 0.5.20 (p22 / p23 setup steps name 1.3.214).
1.3.213 is NOT delivered (held for his question 6); version numbers are never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-214", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_214.mcpack"),
          ("testrunner-0.5.20", "PW-TestRunner-BP-v0_5_20.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
