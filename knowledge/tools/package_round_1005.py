#!/usr/bin/env python3
"""package_round_1005.py — round 1005 (D-C570 the palace, D-C571 the gallery + the Connoisseur's Book, 10-04/05): BP-02 1.3.222
(palace at city II, 6,256 pw:art entities, the gallery + the book) + RP-01 1.3.123 (secret painting tiles, jib panel / painting
sounds) + RP-12 1.0.0 (the Gallery — RP-08 is the Items pack: framed JPEG textures, frame geometries, the book's icon). Version numbers never reused.
Usage: package_round_1005.py [dir ...]"""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("bp02-226", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_226.mcpack"),             # 1.3.226: the land and the core, contour lanes (round 1005d)
          ("bp02-224", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_224.mcpack"),             # 1.3.224: his 16:50 report (round 1005c)
          ("rp01-124", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_124.mcpack"),
          ("rp12-101", "RP-12-AbsolutRealism-Gallery-RP-v1_0_1.mcpack"),
          ("rp12-101-lite", "RP-12-AbsolutRealism-Gallery-LITE-RP-v1_0_1.mcpack"),
          ("bp02-223", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_223.mcpack"),             # 1.3.223: the dry palace (10-05 15:2x)
          ("bp02-222", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_222.mcpack"),
          ("rp01-123", "RP-01-AbsolutRealism-Tectonic-RP-v1_3_123.mcpack"),
          ("rp12-100", "RP-12-AbsolutRealism-Gallery-RP-v1_0_0.mcpack"),            # RP-08 is the Items pack: the gallery is RP-12 (09:1x 10-05)
          ("rp12-100-lite", "RP-12-AbsolutRealism-Gallery-LITE-RP-v1_0_0.mcpack")]
if __name__ == "__main__":
    only = sys.argv[1:] or None
    P.main(only)
    for d, name in P.JOBS:
        if only and d not in only:
            continue
        size = (Path("/mnt/user-data/outputs") / name).stat().st_size
        assert size <= 400 * 1000 * 1000, name
        print(f"SIZE OK {name} {size:,} B")
