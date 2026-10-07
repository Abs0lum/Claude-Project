#!/usr/bin/env python3
"""verify_rp06_1412.py — gate for RP-06 1.4.12 (build_rp06_1412.py; lines in convb_round.verify + GA1-GA3 + S1)."""
import sys
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
from build_rp06_1412 import CFG
if __name__ == "__main__":
    sys.exit(R.verify(CFG))
