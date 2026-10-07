#!/usr/bin/env python3
"""package_round_1004b.py — round 1004b (D-C563..D-C568, 10-04): BP-02 1.3.220 (felling by template, foliage sweep, flooding,
mob clearing, civs: states / our window / children / flue avoidance / half speed, lectern, vines, PHYSICS falling trees, birch v2)
+ RP-01 1.3.122 (physics fall animation, leading-edge pivots, birch copies) + RP-05 1.3.59 (vanilla leaf textures) + Markers
RP 0.2.3 / BP 0.2.4 (manhole lift-then-slide). Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-220", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_220.mcpack"),
          ("rp01-122", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_122.mcpack"),
          ("rp05-59", "RP-05-AbsolutRealism-Flora-RP-v1_3_59.mcpack"),
          ("markers-0.2.4-bp", "PW-Civitas-Markers-BP-v0_2_4.mcpack"),
          ("markers-0.2.3-rp", "PW-Civitas-Markers-RP-v0_2_3.mcpack")]
if __name__ == "__main__":
    only = sys.argv[1:] or None
    P.main(only)
    for d, name in P.JOBS:
        if only and d not in only:
            continue
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
