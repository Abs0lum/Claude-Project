#!/usr/bin/env python3
"""build_bp02_225_diag.py — a BDS-only diagnosis copy of BP-02 1.3.224 + the changed scripts of tools/bp02_src_225
(never shipped; the real 1.3.225 has its own builder). Usage: build_bp02_225_diag.py <N>  -> _build/bp02-225-diag<N>"""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, JS = B / "bp02-224", Path("/home/claude/tools/bp02_src_225")


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def main():
    dst = B / f"bp02-225-diag{sys.argv[1]}"
    if dst.exists():
        raise SystemExit(f"never rebuild {dst}")
    base = dict(line.split()[::-1] for line in (JS / "BASE-224.md5").read_text().splitlines())
    for name, h in base.items():
        assert md5(SRC / "scripts" / name) == h, f"224 drifted: {name}"
    shutil.copytree(SRC, dst)
    changed = []
    for p in sorted(JS.glob("*.js")):
        if base.get(p.name) != md5(p):
            shutil.copy2(p, dst / "scripts" / p.name)
            changed.append(p.name)
    for p in sorted((dst / "scripts").glob("*.js")):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"{p.name}: {r.stderr[:300]}"
    print(f"DONE {dst} · changed: {', '.join(changed)}")


if __name__ == "__main__":
    main()
