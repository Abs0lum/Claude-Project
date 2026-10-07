#!/usr/bin/env python3
"""package_sandglint.py — sand glint test packs G1 / G2 (his 00:07 ruling: 8 directions, 12.5 % each)."""
import sys
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("sandtest-g1-100", "PW-SandTest-G1-RP-v1_0_0.mcpack"), ("sandtest-g2-100", "PW-SandTest-G2-RP-v1_0_0.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
