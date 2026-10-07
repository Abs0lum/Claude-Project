#!/usr/bin/env python3
"""bds_civtest.py — run pack dirs in the workspace Bedrock Dedicated Server until a script prints "[CIVTEST] {...DONE...}"
(or the timeout), then return every [CIVTEST] JSON line. Reuses bds_load.install (fresh pristine world each run).
Usage: bds_civtest.py [--seconds N] [--keep-world] DIR [DIR ...]
Output: _bds/logs/civtest-<stamp>.txt (full console) + _bds/logs/civtest-<stamp>.json (parsed [CIVTEST] records)."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import bds_load as B  # noqa: E402


def run(dirs, seconds=240, keep_world=False):
    B.install(dirs, keep_world)
    B.LOGS.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = B.LOGS / f"civtest-{stamp}.txt"
    with open(out, "w") as f:
        p = subprocess.Popen(["./bedrock_server"], cwd=B.SRV, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT,
                             env={"LD_LIBRARY_PATH": "."}, text=True)
        t0 = time.time()
        while time.time() - t0 < seconds:
            time.sleep(2)
            txt = out.read_text(errors="ignore")
            if '"step":"DONE"' in txt or "Crash" in txt:
                break
        time.sleep(3)
        try:
            p.stdin.write("stop\n")
            p.stdin.flush()
        except Exception:
            pass
        try:
            p.wait(timeout=60)
        except subprocess.TimeoutExpired:
            p.kill()
    recs = []
    for line in out.read_text(errors="ignore").splitlines():
        m = re.search(r"\[CIVTEST\] (\{.*\})\s*$", line)
        if m:
            try:
                recs.append(json.loads(m.group(1)))
            except json.JSONDecodeError:
                recs.append({"unparsed": m.group(1)[:300]})
    errs = [l for l in out.read_text(errors="ignore").splitlines() if re.search(r"\b(ERROR)\b|\[error\]", l)]
    (B.LOGS / f"civtest-{stamp}.json").write_text(json.dumps({"records": recs, "errors": errs}, indent=1))
    return out, recs, errs


if __name__ == "__main__":
    args = sys.argv[1:]
    secs = 240
    if args[:1] == ["--seconds"]:
        secs = int(args[1])
        args = args[2:]
    keep = False
    if args[:1] == ["--keep-world"]:
        keep = True
        args = args[1:]
    out, recs, errs = run(args, secs, keep)
    print(f"log {out} · {len(recs)} [CIVTEST] records · {len(errs)} ERROR lines")
    for r in recs:
        s = json.dumps(r)
        print(s if len(s) < 600 else s[:600] + " …")
    for e in errs[:20]:
        print("ERR", e[-200:])
