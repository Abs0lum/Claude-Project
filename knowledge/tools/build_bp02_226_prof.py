#!/usr/bin/env python3
"""build_bp02_226_prof.py — BDS-only PROFILED copy of BP-02 1.3.226 (never shipped): tools/prof_src/pw_prof.js is
imported first by main.js and charges every scheduled callback / job step / event handler to its registration site.
Optional overlay: --src DIR copies the changed scripts of DIR (a bp02_src_* tree, against its BASE-226.md5) on top.
Usage: build_bp02_226_prof.py <N> [--src tools/bp02_src_227]   -> _build/bp02-226-prof<N>"""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC = B / "bp02-226"
PROF = Path("/home/claude/tools/prof_src/pw_prof.js")


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def main():
    args = sys.argv[1:]
    n = args[0]
    over = Path(args[args.index("--src") + 1]) if "--src" in args else None
    dst = B / f"bp02-226-prof{n}"
    if dst.exists():
        raise SystemExit(f"never rebuild {dst}")
    shutil.copytree(SRC, dst)
    changed = []
    if over:
        base = dict(line.split()[::-1] for line in (over / "BASE-226.md5").read_text().splitlines())
        for name, h in base.items():
            assert md5(SRC / "scripts" / name) == h, f"226 drifted: {name}"
        for p in sorted(over.rglob("*.js")):
            rel = p.relative_to(over)
            if rel.parts[0] in ("node_modules", "tests"):
                continue
            ref = SRC / "scripts" / rel
            if base.get(str(rel)) != md5(p) and not (ref.exists() and md5(ref) == md5(p)):
                shutil.copy2(p, dst / "scripts" / rel)
                changed.append(str(rel))
    shutil.copy2(PROF, dst / "scripts" / "pw_prof.js")
    mj = dst / "scripts" / "main.js"
    t = mj.read_text()
    assert t.startswith("import {"), "main.js first line changed"
    mj.write_text('import "./pw_prof.js"; // BDS-only profiler (diag build)\n' + t)
    for p in sorted((dst / "scripts").glob("*.js")):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"{p.name}: {r.stderr[:300]}"
    r = subprocess.run([sys.executable, "/home/claude/tools/js_dupcheck.py"] + [str(p) for p in sorted((dst / "scripts").glob("*.js"))], capture_output=True, text=True)
    assert r.returncode == 0, f"duplicate globals: {r.stdout[:600]}"
    print(f"DONE {dst} · overlay: {', '.join(changed) or 'none'} · pw_prof.js first")


if __name__ == "__main__":
    main()
