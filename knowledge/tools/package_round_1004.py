#!/usr/bin/env python3
"""package_round_1004.py — the CIVITAS CITY delivery (D-C533..D-C554, 10-04): BP-02 1.3.219 (city planning: StreetKit
streets that grow, side streets, blocks, benches + switchback roads, the drainage networks and trunks, manholes + keys,
walking villagers, real work, the market, the watch, the census, civic works, the manor, the boundary stones, the mob
size pass) + RP-04 1.3.158 (the villager / lead render) + PW-Civitas-Markers BP 0.2.3 + PW-TestRunner 0.5.23 (lineup p24).
Version numbers never reused."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-219", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_219.mcpack"),
          ("rp04-158", "RP-04-AbsolutRealism-Basic-RP-v1_3_158.mcpack"),
          ("markers-0.2.3-bp", "PW-Civitas-Markers-BP-v0_2_3.mcpack"),
          ("testrunner-0.5.23", "PW-TestRunner-BP-v0_5_23.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
    for _, name in P.JOBS:
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 250 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
