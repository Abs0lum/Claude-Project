#!/usr/bin/env python3
"""tick_r6.py STEM "literal read" [STEM "read" ...] — flips the R6 ledger line for each STEM from UNVIEWED to VIEWED (read)."""
import re, sys
p = "_logs/intake_ledger.md"; s = open(p).read()
args = sys.argv[1:]
for stem, note in zip(args[0::2], args[1::2]):
    pat = re.compile(r"^(- R6 %s\.png \([^\n]*?\)) — UNVIEWED$" % re.escape(stem), re.M)
    s, n = pat.subn(lambda m: f"{m.group(1)} — VIEWED: {note}", s, count=1)
    if n != 1: sys.exit(f"no UNVIEWED R6 line for {stem}")
open(p, "w").write(s)
blk = s.split("## INTAKE 11:4x CT 09-29 — R6")[-1]
tot = len(re.findall(r"^- R6 \d+[a-z]?\.png", blk, re.M)); done = len(re.findall(r"^- R6 \d+[a-z]?\.png .*— VIEWED", blk, re.M))
print(f"R6 screenshots {done}/{tot} viewed")
