#!/usr/bin/env python3
"""verify_rp07_1417.py — gate for RP-07 1.4.17 (build_rp07_1417.py; lines in convb_round.verify)."""
import sys
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
from build_rp07_1417 import CFG
if __name__ == "__main__":
    sys.exit(R.verify(CFG))
