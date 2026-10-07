#!/usr/bin/env python3
"""ship_all.py — the SYNC-EVERYWHERE ship (his ruling 2026-10-07 00:39 CT: "always upload our changes to all of these
places when we upload anything").

One command for every ship:
  1. packs (any FILE arguments)        -> Drive ClaudeUploads/            (tools/drive_ship.py, md5-verified)
  2. knowledge mirror                  -> tools/knowledge_bundle.py, then Drive ClaudeUploads/knowledge/
     + the GitHub paste (prompts/claude-code-github-paste.md) beside it, so the zip and its instructions travel together
  3. prints the destination report: Drive packs / Drive knowledge / GitHub / claude.ai Project, one line each.
     GitHub and the Project cannot be written from a session without repo access / with the Project full — the report
     says who does that step (the GitHub Claude Code session via paste B; Project writes are done by Claude in-session
     with project_write when the Project has room).
Writes one phase-log line per destination.

Usage: ship_all.py --headline "text" [--stamp 2026-10-07b] [PACK.mcpack ...]
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/claude")
PHASE_LOG = ROOT / "_logs" / "phase_log.md"


def log(line):
    """Append one phase-log line, stamped in Central Time like the rest of the log."""
    stamp = time.strftime("%H:%M CT %m-%d", time.localtime(time.time() - 5 * 3600))
    with open(PHASE_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {line}\n")


def run(cmd):
    """Run a command, echo its output, raise on failure; returns stdout."""
    p = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    if p.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(cmd)} (exit {p.returncode})")
    return p.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--headline", required=True)
    ap.add_argument("--stamp", default=time.strftime("%Y-%m-%d"))
    ap.add_argument("packs", nargs="*")
    a = ap.parse_args()
    report = []

    if a.packs:
        run([sys.executable, str(ROOT / "tools/drive_ship.py"), *a.packs])
        log(f"SHIP-ALL packs -> Drive ClaudeUploads: {', '.join(Path(p).name for p in a.packs)}")
        report.append(f"Drive packs      : DONE ({len(a.packs)} file(s), md5 verified)")
    else:
        report.append("Drive packs      : none in this ship")

    out = run([sys.executable, str(ROOT / "tools/knowledge_bundle.py"), "--stamp", a.stamp, "--headline", a.headline])
    info = json.loads(out.strip().splitlines()[-1])
    paste = ROOT / "_knowledge/src/prompts/claude-code-github-paste.md"
    run([sys.executable, str(ROOT / "tools/drive_ship.py"), "--folder", "ClaudeUploads/knowledge", info["zip"], str(paste)])
    log(f"SHIP-ALL knowledge mirror {Path(info['zip']).name} {info['bytes']:,} B md5 {info['md5']} ({info['files']} files) "
        f"-> Drive ClaudeUploads/knowledge (+ paste)")
    report.append(f"Drive knowledge  : DONE {Path(info['zip']).name} md5 {info['md5'][:8]}")
    report.append("GitHub repo      : PENDING — upload the zip to _inbox/ on github.com, then paste B in the Claude Code chat "
                  "(or commit directly from a session started with the repo attached)")
    report.append("claude.ai Project: write the handoff with project_write when it has room (FULL as of 2026-10-07)")
    print("\n".join(["", "SYNC REPORT"] + report))


if __name__ == "__main__":
    main()
