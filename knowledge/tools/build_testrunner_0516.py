#!/usr/bin/env python3
"""build_testrunner_0516.py — PW-TestRunner BP 0.5.16 from 0.5.15: lineup "p23" TREES (tools/testrunner_src/pw_testrunner_p23.js),
registered in pw_testrunner.js (import + LINEUPS + the boot banner), RUNNER_VERSION + manifest 0.5.16. Never touches 0.5.15."""
import json
import re
import shutil
import subprocess
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "testrunner-0.5.15", B / "testrunner-0.5.16"
P23 = Path("/home/claude/tools/testrunner_src/pw_testrunner_p23.js")


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    shutil.copy2(P23, DST / "scripts/pw_testrunner_p23.js")
    pr = DST / "scripts/pw_testrunner.js"
    t = pr.read_text()
    anchor = 'import { P22_STEPS, P22_INDEX } from "./pw_testrunner_p22.js";'
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + '\nimport { P23_STEPS, P23_INDEX } from "./pw_testrunner_p23.js";')
    old = 'bump: { steps: BUMP_STEPS, index: BUMP_INDEX, label: "BUMP: the bump-map test (same mob with / without the normal map)" } };'
    assert t.count(old) == 1
    t = t.replace(old, 'p23: { steps: P23_STEPS, index: P23_INDEX, label: "P23 TREES (BP-02 1.3.209 + RP-01 1.3.118): forests of our templates, no floating trees, roots, the exact template fall, saplings that grow our trees" }, '
                  + old)
    old = 'export const RUNNER_VERSION = "0.5.15";'
    assert t.count(old) == 1
    t = t.replace(old, 'export const RUNNER_VERSION = "0.5.16";')
    old = 'p22 ${P22_STEPS.length} bump ${BUMP_STEPS.length}`'
    assert t.count(old) == 1
    t = t.replace(old, 'p22 ${P22_STEPS.length} p23 ${P23_STEPS.length} bump ${BUMP_STEPS.length}`')
    pr.write_text(t)
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [0, 5, 16]
    m["header"]["name"] = "PW Test Runner BP v0.5.16"
    desc = re.sub(r"^v[0-9.]+ \([^)]*\)", "", m["header"].get("description", "")).lstrip(" :—-")
    m["header"]["description"] = ("v0.5.16 (2026-10-03) lineup p23 TREES (BP-02 1.3.209 + RP-01 1.3.118): forests of our templates, no floating trees, "
                                  "root blocks, the exact template fall, a grove note, nine saplings planted around you that grow our trees. Includes all of v0.5.15: " + desc)[:1000]
    for mod in m.get("modules", []):
        mod["version"] = [0, 5, 16]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    if dep.exists():
        d = dep.read_text()
        d = d.replace("v0.5.15", "v0.5.16", 1)
        dep.write_text(d)
    for f in ("pw_testrunner.js", "pw_testrunner_p23.js"):
        subprocess.run(["node", "--check", str(DST / "scripts" / f)], check=True)
    # the version-flag law
    assert 'RUNNER_VERSION = "0.5.16"' in (DST / "scripts/pw_testrunner.js").read_text()
    print("DONE testrunner-0.5.16: p23 registered, RUNNER_VERSION == manifest 0.5.16")


if __name__ == "__main__":
    main()
