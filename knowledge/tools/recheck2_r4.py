#!/usr/bin/env python3
"""recheck2_r4.py — RECHECK-WEEK 2 (10-03 install set) R4: the standing STATIC gates, re-run on the delivered install set (PW_STACK=w2).
Each gate is a shipped tool, run as a subprocess with a timeout; rc + the last lines go to _docs/recheck/W2-R4-static.json
as they finish (poll the file). Nothing is written to any build dir."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/claude")
B = ROOT / "_build"
ENV = dict(os.environ, PW_STACK="w2")
RPS = [B / d for d in ("rp01-118", "rp02-207", "rp03-67", "rp04-156", "rp05-58", "rp06-1429", "rp07-1445", "rp08-1414",
                       "rp10-151", "rp11-140", "markers-0.2.2-rp/RP")]
BPS = [B / d for d in ("bp01-135", "bp02-210", "bp03-134", "markers-0.2.1/BP", "testrunner-0.5.17")]
MOBS = [B / d for d in ("rp06-1429", "rp07-1445", "rp08-1414")]
T = ROOT / "tools"
GATES = [
    ("molang_lint (every Molang string in every RP + BP)", [sys.executable, T / "molang_lint.py", *RPS, *BPS], 900),
    ("entity_schema_lint FMT (client entity sections vs format_version)", [sys.executable, T / "entity_schema_lint.py", *MOBS], 300),
    ("anim_resolve_lint (every animation an entity plays exists)", [sys.executable, T / "anim_resolve_lint.py", *MOBS], 300),
    ("rc_visibility_lint RCV (render controllers leave models visible)", [sys.executable, T / "rc_visibility_lint.py", *MOBS], 300),
    ("attachables_lint ATT (enable_attachables like vanilla)", [sys.executable, T / "attachables_lint.py", *MOBS], 300),
    ("game_log_gates (FMT/EMPTY/... from his content logs)", [sys.executable, T / "game_log_gates.py", *MOBS], 600),
    ("verify_ownership O1 (key + image + texture set in ONE pack)", [sys.executable, T / "verify_ownership.py"], 600),
    ("block_state_census (permutations; every state enum <= 16)", [sys.executable, T / "block_state_census.py"], 600),
    ("api_audit L-API-STABLE (scripts touch only pinned-API members)", [sys.executable, T / "api_audit.py", *BPS], 600),
]


def main():
    out = ROOT / "_docs/recheck/W2-R4-static.json"
    rows = []
    for label, cmd, tmo in GATES:
        t0 = time.time()
        try:
            p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, timeout=tmo, env=ENV, cwd=ROOT)
            rc, so, se = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as e:
            rc, so, se = "TIMEOUT", (e.stdout or b"").decode(errors="ignore") if isinstance(e.stdout, bytes) else (e.stdout or ""), ""
        rows.append({"gate": label, "cmd": " ".join(str(c) for c in cmd)[:300], "rc": rc, "seconds": round(time.time() - t0, 1),
                     "tail": (so[-6000:] + ("\nSTDERR: " + se[-3000:] if se.strip() else ""))})
        out.write_text(json.dumps(rows, indent=1))
        print(f"[{rows[-1]['seconds']:6.1f}s] rc={rc} {label}", flush=True)
    print("R4 DONE")


if __name__ == "__main__":
    main()
