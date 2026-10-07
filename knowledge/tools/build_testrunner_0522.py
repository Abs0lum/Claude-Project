#!/usr/bin/env python3
"""build_testrunner_0522.py — PW-TestRunner BP 0.5.22 from 0.5.21 (never touched): lineup p24 CIVITAS CITY (BP-02 1.3.219
build 24 + RP-04 1.3.158 + Markers BP 0.2.3) — the town that works: StreetKit founding, edge guards, boundary stones, the
sewer below (manhole + the test key, the running hall, the exit or soakaway), real-time quarry hands and builders, the
midday counters, town II (watch, manor, neighbourhood market, civic works, bench), the night watch above and below with
three zombies, city I (wall, greenbelt, infirmary, the old pit greening), the daughter and the fenced green-corridor road,
the mob size pass. p22 / p23 setup texts now name BP-02 1.3.219 (the 1.3.215 candidate they named is inside it).
Sources of truth: tools/testrunner_src/pw_testrunner_p24.js."""
import json
import re
import shutil
import subprocess
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "testrunner-0.5.21", B / "testrunner-0.5.22"
T = Path("/home/claude/tools/testrunner_src")
EDITS = {
    "pw_testrunner_p22.js": [("Packs: BP-02 v1.3.215 (replaces 1.3.207 … 214)", "Packs: BP-02 v1.3.219 (replaces 1.3.207 … 215)"),
                             ("PW-TestRunner BP v0.5.21 at the bottom.", "PW-TestRunner BP v0.5.22 at the bottom.")],
    "pw_testrunner_p23.js": [('title: "P23 TREES: BP-02 1.3.215 + RP-01 1.3.118', 'title: "P23 TREES: BP-02 1.3.219 + RP-01 1.3.118'),
                             ("Packs: BP-02 v1.3.215 (replaces 1.3.207 … 214)", "Packs: BP-02 v1.3.219 (replaces 1.3.207 … 215)"),
                             ("PW-TestRunner BP v0.5.21 at the bottom.", "PW-TestRunner BP v0.5.22 at the bottom."),
                             ("Content log after load: '[PW-VERSION] BP-02 v1.3.215' and '[TREEGROW] BOOT v1.3.215'.", "Content log after load: '[PW-VERSION] BP-02 v1.3.219' and '[TREEGROW] BOOT v1.3.219'.")],
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
    for old, new in [('export const RUNNER_VERSION = "0.5.21";', 'export const RUNNER_VERSION = "0.5.22";'),
                     ('label: "P23 TREES (BP-02 1.3.215 + RP-01 1.3.118):', 'label: "P23 TREES (BP-02 1.3.219 + RP-01 1.3.118):'),
                     ('import { P23_STEPS, P23_INDEX } from "./pw_testrunner_p23.js";',
                      'import { P23_STEPS, P23_INDEX } from "./pw_testrunner_p23.js";\nimport { P24_STEPS, P24_INDEX } from "./pw_testrunner_p24.js";'),
                     (' bump: { steps: BUMP_STEPS, index: BUMP_INDEX,',
                      ' p24: { steps: P24_STEPS, index: P24_INDEX, label: "P24 CIVITAS CITY (BP-02 1.3.219 + RP-04 1.3.158 + Markers 0.2.3): the town that works — sewers + the key, real-time hands, builders, counters, the night watch, the manor, markets, works, wall + greenbelt, green-corridor road, mob sizes" }, bump: { steps: BUMP_STEPS, index: BUMP_INDEX,'),
                     ('p23 ${P23_STEPS.length} bump', 'p23 ${P23_STEPS.length} p24 ${P24_STEPS.length} bump')]:
        assert t.count(old) == 1, old
        t = t.replace(old, new)
    pr.write_text(t)
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [0, 5, 22]
    m["header"]["name"] = "PW Test Runner BP v0.5.22"
    desc = re.sub(r"^v[0-9.]+ \([^)]*\)", "", m["header"].get("description", "")).lstrip(" :—-")
    m["header"]["description"] = ("v0.5.22 (2026-10-04) lineup p24 CIVITAS CITY (BP-02 1.3.219 + RP-04 1.3.158 + Markers 0.2.3): the town that works; p22 / p23 name BP-02 1.3.219. Includes all of v0.5.21: " + desc)[:1000]
    for mod in m.get("modules", []):
        mod["version"] = [0, 5, 22]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    for f in ("pw_testrunner.js", "pw_testrunner_p22.js", "pw_testrunner_p23.js", "pw_testrunner_p24.js"):
        subprocess.run(["node", "--check", str(DST / "scripts" / f)], check=True)
    assert 'RUNNER_VERSION = "0.5.22"' in (DST / "scripts/pw_testrunner.js").read_text()
    print("DONE testrunner-0.5.22: lineup p24 CIVITAS CITY; p22/p23 -> BP-02 1.3.219; RUNNER_VERSION == manifest 0.5.22")


if __name__ == "__main__":
    main()
