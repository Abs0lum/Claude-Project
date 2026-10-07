#!/usr/bin/env python3
"""r3_tick.py STEM [STEM ...] — flip the R3 intake-ledger lines for these screenshots from UNVIEWED to VIEWED; --count prints the tally."""
import re, sys
from pathlib import Path
L = Path("/home/claude/_logs/intake_ledger.md")
t = L.read_text(encoding="utf-8")
head, sep, block = t.rpartition("## INTAKE 20:44 CT 09-28 — R3 shots")
for s in sys.argv[1:]:
    if s == "--count": continue
    block, n = re.subn(rf"(- R3 {s}\.png [^\n]*?) — UNVIEWED", r"\1 — VIEWED", block)
    if n != 1: print("no UNVIEWED line for", s)
v = len(re.findall(r"- R3 \d+\.png[^\n]* — VIEWED", block)); u = len(re.findall(r"- R3 \d+\.png[^\n]* — UNVIEWED", block))
block = re.sub(r"  -> \d+/27 VIEWED[^\n]*", f"  -> {v}/27 VIEWED, {u} UNVIEWED", block)
L.write_text(head + sep + block, encoding="utf-8"); print(f"{v}/27 VIEWED, {u} UNVIEWED")
