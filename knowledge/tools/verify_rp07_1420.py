#!/usr/bin/env python3
"""verify_rp07_1420.py — gate for RP-07 1.4.20 (D-C278): convb_round.verify + the U/S/M/H/Q/T lines of build_rp07_1420."""
import json, sys
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import build_rp07_1420 as B
f = json.load(open("/home/claude/_docs/convb/build_1420_files.json"))
B.CHANGED[:] = f["changed"]; B.ADDED[:] = f["added"]; B.REMOVED[:] = f["removed"]
sys.exit(R.verify(B.CFG))
