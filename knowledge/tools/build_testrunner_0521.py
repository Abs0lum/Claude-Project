#!/usr/bin/env python3
"""build_testrunner_0521.py — PW-TestRunner BP 0.5.21 from 0.5.20 (never touched): the p22 / p23 setup texts name BP-02 1.3.215
(the tree search step, D-C519) — built only as the HELD companion of the 1.3.215 candidate; delivered only if he takes Q6(b). Text-only. Sources of truth:
tools/testrunner_src/pw_testrunner_p22.js / p23.js (patched here first), RUNNER_VERSION + manifest 0.5.20."""
import json
import re
import shutil
import subprocess
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "testrunner-0.5.20", B / "testrunner-0.5.21"
T = Path("/home/claude/tools/testrunner_src")
EDITS = {
    "pw_testrunner_p22.js": [("Packs: BP-02 v1.3.214 (replaces 1.3.207 … 212)", "Packs: BP-02 v1.3.215 (replaces 1.3.207 … 214)"),
                             ("PW-TestRunner BP v0.5.20 at the bottom.", "PW-TestRunner BP v0.5.21 at the bottom.")],
    "pw_testrunner_p23.js": [('title: "P23 TREES: BP-02 1.3.214 + RP-01 1.3.118', 'title: "P23 TREES: BP-02 1.3.215 + RP-01 1.3.118'),
                             ("Packs: BP-02 v1.3.214 (replaces 1.3.207 … 212)", "Packs: BP-02 v1.3.215 (replaces 1.3.207 … 214)"),
                             ("PW-TestRunner BP v0.5.20 at the bottom.", "PW-TestRunner BP v0.5.21 at the bottom."),
                             ("Content log after load: '[PW-VERSION] BP-02 v1.3.214' and '[TREEGROW] BOOT v1.3.214'.", "Content log after load: '[PW-VERSION] BP-02 v1.3.215' and '[TREEGROW] BOOT v1.3.215'.")],
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
    # HELD build: the sources of truth (tools/testrunner_src) keep naming the DELIVERED 1.3.214 — only the copies in DST are patched;
    # if he takes Q6(b) the sources are patched at delivery time
    shutil.copytree(SRC, DST)
    for f, edits in EDITS.items():
        patch(DST / "scripts" / f, edits)
    pr = DST / "scripts/pw_testrunner.js"
    t = pr.read_text()
    for old, new in [('export const RUNNER_VERSION = "0.5.20";', 'export const RUNNER_VERSION = "0.5.21";'),
                     ('label: "P23 TREES (BP-02 1.3.214 + RP-01 1.3.118):', 'label: "P23 TREES (BP-02 1.3.215 + RP-01 1.3.118):')]:
        assert t.count(old) == 1, old
        t = t.replace(old, new)
    pr.write_text(t)
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [0, 5, 21]
    m["header"]["name"] = "PW Test Runner BP v0.5.21"
    desc = re.sub(r"^v[0-9.]+ \([^)]*\)", "", m["header"].get("description", "")).lstrip(" :—-")
    m["header"]["description"] = ("v0.5.21 (2026-10-03) p22 / p23 setup steps name BP-02 1.3.215. Includes all of v0.5.20: " + desc)[:1000]
    for mod in m.get("modules", []):
        mod["version"] = [0, 5, 21]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    for f in ("pw_testrunner.js", "pw_testrunner_p22.js", "pw_testrunner_p23.js"):
        subprocess.run(["node", "--check", str(DST / "scripts" / f)], check=True)
    assert 'RUNNER_VERSION = "0.5.21"' in (DST / "scripts/pw_testrunner.js").read_text()
    print("DONE testrunner-0.5.21 (HELD with 1.3.215): p22/p23 q0 -> BP-02 1.3.215, RUNNER_VERSION == manifest 0.5.21")


if __name__ == "__main__":
    main()
