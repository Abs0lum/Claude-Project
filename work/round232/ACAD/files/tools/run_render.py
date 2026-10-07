#!/usr/bin/env python3
"""Run an acad2v2_render.py copy against the acad2v2_layout.py next to it, writing into OUTDIR instead of the hard-coded
cloud path. Usage: run_render.py <dir holding the two scripts> <out dir>.
The render source is exec'd with only its OUT line swapped (asserted: exactly one match), so the BEFORE images come from the
untouched round-231 scripts."""
import os
import sys

src_dir, out_dir = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(src_dir, "acad2v2_render.py")
src = open(path).read()
old = 'OUT = "/home/claude/_docs/castle/academy2_v2"'
n = src.count(old)
if n == 1:
    src = src.replace(old, f"OUT = {out_dir!r}")
elif 'OUT = os.environ.get("ACAD_OUT"' in src:
    os.environ["ACAD_OUT"] = out_dir
else:
    raise SystemExit(f"OUT line not found exactly once in {path} (count {n})")
sys.path.insert(0, src_dir)
os.chdir(out_dir)
exec(compile(src, path, "exec"), {"__name__": "__main__", "__file__": path})
