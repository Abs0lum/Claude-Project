#!/usr/bin/env python3
"""build_testrunner_0515.py — PW-TestRunner BP 0.5.15 from 0.5.14: lineup "p22" CIVITAS (tools/testrunner_src/pw_testrunner_p22.js),
registered in pw_testrunner.js (import + LINEUPS + the boot banner), RUNNER_VERSION + manifest 0.5.15. Never touches 0.5.14."""
import json
import re
import shutil
import subprocess
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "testrunner-0.5.14", B / "testrunner-0.5.15"
P22 = Path("/home/claude/tools/testrunner_src/pw_testrunner_p22.js")


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    shutil.copy2(P22, DST / "scripts/pw_testrunner_p22.js")
    pr = DST / "scripts/pw_testrunner.js"
    t = pr.read_text()
    anchor = 'import { P21_STEPS, P21_INDEX } from "./pw_testrunner_p21.js";'
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + '\nimport { P22_STEPS, P22_INDEX } from "./pw_testrunner_p22.js";')
    old = 'bump: { steps: BUMP_STEPS, index: BUMP_INDEX, label: "BUMP: the bump-map test (same mob with / without the normal map)" } };'
    assert t.count(old) == 1
    t = t.replace(old, 'p22: { steps: P22_STEPS, index: P22_INDEX, label: "P22 CIVITAS (BP-02 1.3.207 + RP-07 1.4.45 + RP-08 1.4.14): the living town on the land — founding, terraces, growth, market, decline, city wall, daughter + road, trade, snapshot" }, '
                  + old)
    old = 'export const RUNNER_VERSION = "0.5.14";'
    assert t.count(old) == 1
    t = t.replace(old, 'export const RUNNER_VERSION = "0.5.15";')
    old = 'p21 ${P21_STEPS.length} bump ${BUMP_STEPS.length}`'
    assert t.count(old) == 1
    t = t.replace(old, 'p21 ${P21_STEPS.length} p22 ${P22_STEPS.length} bump ${BUMP_STEPS.length}`')
    pr.write_text(t)
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [0, 5, 15]
    m["header"]["name"] = "PW Test Runner BP v0.5.15"
    desc = re.sub(r"^v[0-9.]+ \([^)]*\)", "", m["header"].get("description", "")).lstrip(" :—-")
    m["header"]["description"] = ("v0.5.15 (2026-10-03) lineup p22 CIVITAS: the living town on the land (BP-02 1.3.207 + RP-07 1.4.45 + RP-08 1.4.14) — "
                                  "founding where you stand, terraces, yards, growth to a city, market, decline, wall, daughter + road, trade, snapshot. Includes all of v0.5.14: " + desc)[:1000]
    for mod in m.get("modules", []):
        mod["version"] = [0, 5, 15]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    if dep.exists():
        d = dep.read_text()
        d = d.replace("v0.5.14", "v0.5.15", 1)
        dep.write_text(d)
    for f in ("pw_testrunner.js", "pw_testrunner_p22.js"):
        subprocess.run(["node", "--check", str(DST / "scripts" / f)], check=True)
    # the version-flag law
    assert 'RUNNER_VERSION = "0.5.15"' in (DST / "scripts/pw_testrunner.js").read_text()
    print("DONE testrunner-0.5.15: p22 registered, RUNNER_VERSION == manifest 0.5.15")


if __name__ == "__main__":
    main()
