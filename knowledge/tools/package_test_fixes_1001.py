#!/usr/bin/env python3
"""package_test_fixes_1001.py — his 21:05: test packs re-issued Vibrant-Visuals capable (1.0.1) + grass tint test T1/T2."""
import sys
sys.path.insert(0, "/home/claude/tools")
import package_std_round as P  # noqa: E402

P.JOBS = [
    ("sandtest-a-101", "PW-SandTest-A-RP-v1_0_1.mcpack"),
    ("sandtest-b-101", "PW-SandTest-B-RP-v1_0_1.mcpack"),
    ("lighttest-sat-101", "PW-LightTest-Saturation-NOW-RP-v1_0_1.mcpack"),
    ("grasstint-t1-100", "PW-GrassTint-T1-RP-v1_0_0.mcpack"),
    ("grasstint-t2-100", "PW-GrassTint-T2-RP-v1_0_0.mcpack"),
]
if __name__ == "__main__":
    P.main(sys.argv[1:] or None)
