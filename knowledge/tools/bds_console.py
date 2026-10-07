#!/usr/bin/env python3
"""bds_console.py — send console commands to the workspace BDS and print what the console answers (fresh pristine world).
Usage: bds_console.py [--wait-ready] [--keep-world] [--gap SECONDS] DIR [DIR ...] -- CMD [CMD ...]
Each CMD is one console line (quote it). --wait-ready waits for a "[CIVTEST] {"step":"ready"}" line before sending
(a probe BP that logs it); otherwise it waits for "Server started". Output: the console lines after each command."""
import re
import subprocess
import sys
import time

sys.path.insert(0, "/home/claude/tools")
import bds_load as B  # noqa: E402


def main():
    args = sys.argv[1:]
    wait_ready, gap, keep = False, 3.0, False
    while args and args[0].startswith("--") and args[0] != "--":
        if args[0] == "--wait-ready":
            wait_ready = True
            args = args[1:]
        elif args[0] == "--keep-world":                 # read the world the previous run saved (no pristine reinstall)
            keep = True
            args = args[1:]
        elif args[0] == "--gap":
            gap = float(args[1])
            args = args[2:]
        else:
            raise SystemExit(f"unknown flag {args[0]}")
    if "--" not in args:
        raise SystemExit("need -- before the commands")
    k = args.index("--")
    dirs, cmds = args[:k], args[k + 1:]
    B.install(dirs, keep)
    B.LOGS.mkdir(parents=True, exist_ok=True)
    out = B.LOGS / f"console-{time.strftime('%Y%m%d-%H%M%S')}.txt"
    with open(out, "w") as f:
        p = subprocess.Popen(["./bedrock_server"], cwd=B.SRV, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT,
                             env={"LD_LIBRARY_PATH": "."}, text=True)
        needle = '"step":"ready"' if wait_ready else "Server started"
        t0 = time.time()
        while time.time() - t0 < 180 and needle not in out.read_text(errors="ignore"):
            time.sleep(1)
        time.sleep(2)
        for c in cmds:
            before = len(out.read_text(errors="ignore"))
            p.stdin.write(c + "\n")
            p.stdin.flush()
            time.sleep(gap)
            tail = out.read_text(errors="ignore")[before:]
            print(f"> {c}")
            for line in tail.splitlines():
                line = re.sub(r"^\[[^\]]*\] ", "", line)
                if line.strip():
                    print("  " + line[:300])
        p.stdin.write("stop\n")
        p.stdin.flush()
        try:
            p.wait(timeout=90)
        except subprocess.TimeoutExpired:
            p.kill()
    print(f"log {out}")


if __name__ == "__main__":
    main()
