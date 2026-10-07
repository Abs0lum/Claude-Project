#!/usr/bin/env python3
"""package_grasstint_t34.py — grass side tint tests T3 + T4 (his 23:41)."""
import sys
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [("grasstint-t3-100", "PW-GrassTint-T3-RP-v1_0_0.mcpack"), ("grasstint-t4-100", "PW-GrassTint-T4-RP-v1_0_0.mcpack")]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
