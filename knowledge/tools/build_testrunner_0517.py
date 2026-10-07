#!/usr/bin/env python3
"""build_testrunner_0517.py — PW-TestRunner BP 0.5.17 from 0.5.16 (never touched): the q0 texts of lineups p22 (CIVITAS)
and p23 (TREES) name BP-02 1.3.210 — and p23's content-log line is corrected: it said '[PW-VERSION] BP-02 v1.3.209'
while every BP-02 since 1.3.206 printed v1.3.206 there (the in-script PW_BUILD constant was never bumped; 1.3.210 prints
v1.3.210). Sources of truth: tools/testrunner_src/pw_testrunner_p22.js / p23.js (patched here first), RUNNER_VERSION +
manifest 0.5.17. Then: node tools/testrunner_src/test_testrunner.mjs _build/testrunner-0.5.17/scripts (the mock suite)."""
import json
import re
import shutil
import subprocess
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "testrunner-0.5.16", B / "testrunner-0.5.17"
T = Path("/home/claude/tools/testrunner_src")

P22_EDITS = [
    ("Packs: BP-02 v1.3.207 + RP-07 v1.4.45 + RP-08 v1.4.14 (they replace 1.3.206 / 1.4.44 / 1.4.13), PW-TestRunner BP v0.5.15 at the bottom. ",
     "Packs: BP-02 v1.3.210 (replaces 1.3.207 / 208 / 209) + RP-07 v1.4.45 + RP-08 v1.4.14 (they replace 1.4.44 / 1.4.13), PW-TestRunner BP v0.5.17 at the bottom. "),
]
P23_EDITS = [
    ('title: "P23 TREES: BP-02 1.3.209 + RP-01 1.3.118', 'title: "P23 TREES: BP-02 1.3.210 + RP-01 1.3.118'),
    ("Packs: BP-02 v1.3.209 (replaces 1.3.207 / 208) + RP-01 v1.3.118 (replaces 1.3.117); PW-TestRunner BP v0.5.16 at the bottom. ",
     "Packs: BP-02 v1.3.210 (replaces 1.3.207 / 208 / 209) + RP-01 v1.3.118 (replaces 1.3.117); PW-TestRunner BP v0.5.17 at the bottom. "),
    ("Content log after load: '[PW-VERSION] BP-02 v1.3.209' and '[TREEGROW] BOOT'.",
     "Content log after load: '[PW-VERSION] BP-02 v1.3.210' and '[TREEGROW] BOOT v1.3.210'."),
]


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
    patch(T / "pw_testrunner_p22.js", P22_EDITS)
    patch(T / "pw_testrunner_p23.js", P23_EDITS)
    shutil.copytree(SRC, DST)
    for f in ("pw_testrunner_p22.js", "pw_testrunner_p23.js"):
        shutil.copy2(T / f, DST / "scripts" / f)
    pr = DST / "scripts/pw_testrunner.js"
    t = pr.read_text()
    old = 'export const RUNNER_VERSION = "0.5.16";'
    assert t.count(old) == 1
    t = t.replace(old, 'export const RUNNER_VERSION = "0.5.17";')
    old = 'label: "P23 TREES (BP-02 1.3.209 + RP-01 1.3.118):'
    assert t.count(old) == 1
    t = t.replace(old, 'label: "P23 TREES (BP-02 1.3.210 + RP-01 1.3.118):')
    pr.write_text(t)
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [0, 5, 17]
    m["header"]["name"] = "PW Test Runner BP v0.5.17"
    desc = re.sub(r"^v[0-9.]+ \([^)]*\)", "", m["header"].get("description", "")).lstrip(" :—-")
    m["header"]["description"] = ("v0.5.17 (2026-10-03) p22 / p23 setup steps name BP-02 1.3.210; the p23 content-log line corrected "
                                  "(the BP printed v1.3.206 until 1.3.210). Includes all of v0.5.16: " + desc)[:1000]
    for mod in m.get("modules", []):
        mod["version"] = [0, 5, 17]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    if dep.exists():
        dep.write_text(dep.read_text().replace("v0.5.16", "v0.5.17", 1))
    for f in ("pw_testrunner.js", "pw_testrunner_p22.js", "pw_testrunner_p23.js"):
        subprocess.run(["node", "--check", str(DST / "scripts" / f)], check=True)
    assert 'RUNNER_VERSION = "0.5.17"' in (DST / "scripts/pw_testrunner.js").read_text()
    print("DONE testrunner-0.5.17: p22/p23 q0 -> BP-02 1.3.210, RUNNER_VERSION == manifest 0.5.17")


if __name__ == "__main__":
    main()
