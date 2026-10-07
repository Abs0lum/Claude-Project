#!/usr/bin/env python3
"""tick15.py <name fragment> "<literal read>" — flips the R15 ledger line for that item from UNVIEWED to VIEWED (read); prints the R15 count."""
import re, sys
frag, note = sys.argv[1], sys.argv[2]
p = "/home/claude/_logs/intake_ledger.md"; s = open(p).read()
head = s.rindex("## INTAKE 01:4x CT 09-30 — R15")
sec = s[head:]
m = re.search(r"^- R15 [^\n]*%s[^\n]*— UNVIEWED$" % re.escape(frag), sec, re.M)
if not m: sys.exit("no UNVIEWED R15 line for " + frag)
line = m.group(0); new = line.replace("— UNVIEWED", "— VIEWED (" + note.replace("\n", " ") + ")")
sec = sec.replace(line, new, 1); s = s[:head] + sec; open(p, "w").write(s)
tot = len(re.findall(r"^- R15 ", sec, re.M)); done = len(re.findall(r"^- R15 .*— VIEWED", sec, re.M))
print(f"{frag} ticked — R15 {done}/{tot} viewed")
