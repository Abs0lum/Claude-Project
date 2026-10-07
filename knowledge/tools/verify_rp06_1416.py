#!/usr/bin/env python3
"""verify_rp06_1416.py — the gate for tools/build_rp06_1416.py (convb_round.verify: diff A/J/K, per-job B/C/D/E/F/G/L, the build's own
verify hooks, the standing Molang gate MLS and the standing animation-name gate ARS). Static checks only rule OUT (P1); his
in-game witness rules IN."""
import sys
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import build_rp06_1416 as B

if __name__ == "__main__":
    import json
    files = json.load(open(f"/home/claude/_docs/convb/build_rp06_1416_files.json"))     # the hooks' file lists, written by the build
    B.CFG["extra_changed"], B.CFG["extra_added"], B.CFG["extra_removed"] = files["changed"], files["added"], files["removed"]
    sys.exit(R.verify(B.CFG))
