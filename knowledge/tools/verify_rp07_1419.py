#!/usr/bin/env python3
"""verify_rp07_1419.py — gate for RP-07 1.4.19 (build_rp07_1419.py; lines in convb_round.verify + S1)."""
import sys
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
from build_rp07_1419 import CFG
if __name__ == "__main__":
    sys.exit(R.verify(CFG))
