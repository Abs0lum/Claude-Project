#!/usr/bin/env python3
"""verify_rp06_1414.py — gate for RP-06 1.4.14 (D-C280)."""
import json, sys
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import build_rp06_1414 as B
f = json.load(open("/home/claude/_docs/convb/build_rp06_1414_files.json"))
B.CHANGED[:] = f["changed"]; B.ADDED[:] = f["added"]; B.REMOVED[:] = f["removed"]
sys.exit(R.verify(B.CFG))
