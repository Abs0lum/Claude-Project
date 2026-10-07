#!/usr/bin/env python3
"""recheck_r5.py — RECHECK-WEEK R5: every SCRIPT test the week built, re-run against the DELIVERED scripts.
  1. node --check on every .js in the 5 installed behaviour packs (syntax) + the undelivered bp02-207
  2. fell rules mock (tools/bp02_src/test_fell) on bp02-206 AND bp02-207 scripts/pw_fell_rules.js
  3. TestRunner mock (tools/testrunner_src/test_testrunner.mjs) on testrunner-0.5.13/scripts
  4. homestead fog mock (tools/testrunner_src/test_homestead_fog.mjs) on bp02-206/scripts
  5. mob light mock (tools/bp02_src/test_mob_light.mjs) on bp02-206/scripts/pw_mob_light.js
  6. planks + vine mocks (preserved from the scratchpad into tools/bp02_src/test_planks_vine) on bp02-206
  7. stack API tests (tools/stack_src/test_stack.mjs) on bp01-135 / bp02-206 / bp03-134
Each suite's rc + tail -> _docs/recheck/R5-scripts.json. Read-only on the builds (suites copy into temp dirs)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path("/home/claude")
B = ROOT / "_build"
T = ROOT / "tools"
SP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad")
OUT = ROOT / "_docs/recheck/R5-scripts.json"
rows = []


def rec(label, rc, text, seconds):
    rows.append({"suite": label, "rc": rc, "seconds": round(seconds, 1), "tail": text[-5000:]})
    OUT.write_text(json.dumps(rows, indent=1))
    print(f"[{seconds:6.1f}s] rc={rc} {label}", flush=True)


def sh(cmd, cwd=None, tmo=600, env=None):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=tmo, env=env)
        return p.returncode, p.stdout + ("\nSTDERR: " + p.stderr if p.stderr.strip() else ""), time.time() - t0
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "", time.time() - t0


def node_check():
    bad, n = [], 0
    for d in ("bp01-135", "bp02-206", "bp03-134", "markers-0.2.1/BP", "testrunner-0.5.13", "bp02-207"):
        for f in sorted((B / d / "scripts").rglob("*.js")):
            n += 1
            p = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
            if p.returncode:
                bad.append(f"{f.relative_to(B)}: {p.stderr.strip()[:200]}")
    return (1 if bad else 0), f"{n} scripts checked, {len(bad)} syntax errors\n" + "\n".join(bad)


def fell(build):
    td = Path(tempfile.mkdtemp(prefix="fell_"))
    mod = td / "node_modules/@minecraft/server"
    mod.mkdir(parents=True)
    shutil.copy(T / "bp02_src/test_fell/mock_server.js", mod / "index.js")
    (mod / "package.json").write_text('{"name":"@minecraft/server","type":"module","main":"index.js"}')
    shutil.copy(T / "bp02_src/test_fell/test.mjs", td / "test.mjs")
    shutil.copy(B / build / "scripts/pw_fell_rules.js", td / "pw_fell_rules.js")
    return sh(["node", "test.mjs"], cwd=td)


def planks_vine(build):
    src = T / "bp02_src/test_planks_vine"
    if not src.exists():                           # preserve the scratchpad tests (D-C466 / 1002e were ad hoc)
        src.mkdir(parents=True)
        for f in ("test.mjs", "test2.mjs", "testvine.mjs", "testvine2.mjs"):
            shutil.copy(SP / "plktest" / f, src / f)
        shutil.copytree(SP / "plktest/node_modules", src / "node_modules")
    outs = []
    rc_all = 0
    for f in ("test.mjs", "test2.mjs", "testvine.mjs", "testvine2.mjs"):
        td = Path(tempfile.mkdtemp(prefix="plk_"))
        shutil.copytree(src / "node_modules", td / "node_modules")
        shutil.copy(src / f, td / f)
        shutil.copy(B / build / "scripts/pw_planks.js", td / "pw_planks.js")
        shutil.copy(B / build / "scripts/pw_vine.js", td / "pw_vine.js")
        rc, out, _ = sh(["node", f], cwd=td)
        rc_all = rc_all or (rc if isinstance(rc, int) else 1)
        outs.append(f"--- {f} rc={rc}\n{out[-1200:]}")
    return rc_all, "\n".join(outs), 0


def main():
    t0 = time.time()
    rc, out = node_check()
    rec("node --check (every shipped script + bp02-207)", rc, out, time.time() - t0)
    for build in ("bp02-206", "bp02-207"):
        rc, out, s = fell(build)
        rec(f"fell rules mock on {build}", rc, out, s)
    rc, out, s = sh(["node", str(T / "testrunner_src/test_testrunner.mjs"), str(B / "testrunner-0.5.13/scripts")], cwd=T / "testrunner_src")
    rec("TestRunner mock on testrunner-0.5.13", rc, out, s)
    rc, out, s = sh(["node", str(T / "testrunner_src/test_homestead_fog.mjs"), str(B / "bp02-206/scripts")], cwd=T / "testrunner_src")
    rec("homestead fog mock on bp02-206", rc, out, s)
    rc, out, s = sh(["node", str(T / "bp02_src/test_mob_light.mjs"), str(B / "bp02-206/scripts/pw_mob_light.js")], cwd=T / "bp02_src")
    rec("mob light mock on bp02-206", rc, out, s)
    t1 = time.time()
    rc, out, _ = planks_vine("bp02-206")
    rec("planks + vine mocks on bp02-206", rc, out, time.time() - t1)
    # stack API tests exactly as verify_stack_api stages them (mock_mc + bp01 / bp02 main+weather / bp03 copies)
    td = Path(tempfile.mkdtemp(prefix="stack_"))
    nm = td / "node_modules/@minecraft/server"
    nm.mkdir(parents=True)
    shutil.copy(T / "stack_src/mock_mc.mjs", nm / "index.js")
    (nm / "package.json").write_text('{"name":"@minecraft/server","type":"module","main":"index.js"}')
    for sub, src in (("bp01", B / "bp01-135"), ("bp03", B / "bp03-134")):
        (td / sub).mkdir()
        for f in (src / "scripts").glob("*.js"):
            shutil.copy(f, td / sub / f.name)
    (td / "bp02").mkdir()
    shutil.copy(B / "bp02-206/scripts/main.js", td / "bp02/main.js")
    shutil.copy(B / "bp02-206/scripts/pw_weather.js", td / "bp02/pw_weather.js")
    shutil.copy(T / "stack_src/test_stack.mjs", td / "test_stack.mjs")
    for mode in ("bp01", "bp01-reload", "weather", "bp02", "bp03"):
        rc, out, s = sh(["node", "test_stack.mjs", mode], cwd=td, tmo=120)
        rec(f"stack API tests mode={mode} (bp01-135 / bp02-206 / bp03-134)", rc, out, s)
    print("R5 DONE")


if __name__ == "__main__":
    main()
