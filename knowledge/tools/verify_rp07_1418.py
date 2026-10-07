#!/usr/bin/env python3
"""verify_rp07_1418.py — gate for RP-07 1.4.18 (build_rp07_1418.py; lines in convb_round.verify)."""
import sys
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
from build_rp07_1418 import CFG
if __name__ == "__main__":
    sys.exit(R.verify(CFG))
