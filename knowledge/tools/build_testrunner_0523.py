#!/usr/bin/env python3
"""build_testrunner_0523.py — PW-TestRunner BP 0.5.23 from 0.5.22 (never touched): lineup p24 texts after the 0.0.25/26
runs (pit sites + worked-out quarries, the coppice, counters stocked at the first market hour, walkers on their own
leads; the pack line names RP-04 1.3.156/157 and Markers 0.2.1 as replaced). p22 / p23 name TestRunner 0.5.23.
Sources of truth: tools/testrunner_src/pw_testrunner_p24.js."""
import json
import re
import shutil
import subprocess
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "testrunner-0.5.22", B / "testrunner-0.5.23"
T = Path("/home/claude/tools/testrunner_src")
EDITS = {
    "pw_testrunner_p22.js": [("PW-TestRunner BP v0.5.22 at the bottom.", "PW-TestRunner BP v0.5.23 at the bottom.")],
    "pw_testrunner_p23.js": [("PW-TestRunner BP v0.5.22 at the bottom.", "PW-TestRunner BP v0.5.23 at the bottom.")],
}


def patch(path, edits):
    t = path.read_text()
    for old, new in edits:
        if t.count(old) != 1:
            raise SystemExit(f"{path.name}: expected exactly one '{old[:50]}…' ({t.count(old)} found)")
        t = t.replace(old, new)
    path.write_text(t)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    for f, edits in EDITS.items():
        patch(DST / "scripts" / f, edits)
    shutil.copy(T / "pw_testrunner_p24.js", DST / "scripts/pw_testrunner_p24.js")
    pr = DST / "scripts/pw_testrunner.js"
    t = pr.read_text()
    old, new = 'export const RUNNER_VERSION = "0.5.22";', 'export const RUNNER_VERSION = "0.5.23";'
    assert t.count(old) == 1, old
    pr.write_text(t.replace(old, new))
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [0, 5, 23]
    m["header"]["name"] = "PW Test Runner BP v0.5.23"
    desc = re.sub(r"^v[0-9.]+ \([^)]*\)", "", m["header"].get("description", "")).lstrip(" :—-")
    m["header"]["description"] = ("v0.5.23 (2026-10-04) lineup p24 texts after the city runs (pit sites, the coppice, the counters, own leads). Includes all of v0.5.22: " + desc)[:1000]
    for mod in m.get("modules", []):
        mod["version"] = [0, 5, 23]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    for f in ("pw_testrunner.js", "pw_testrunner_p22.js", "pw_testrunner_p23.js", "pw_testrunner_p24.js"):
        subprocess.run(["node", "--check", str(DST / "scripts" / f)], check=True)
    assert 'RUNNER_VERSION = "0.5.23"' in (DST / "scripts/pw_testrunner.js").read_text()
    print("DONE testrunner-0.5.23: p24 texts; RUNNER_VERSION == manifest 0.5.23")


if __name__ == "__main__":
    main()
