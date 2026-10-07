#!/usr/bin/env python3
"""tick_r17.py <shot-stem> "<literal read>" — flips the R17 ledger line for that screenshot from UNVIEWED to VIEWED (read)."""
import re, sys
stem, note = sys.argv[1], sys.argv[2]
p = "_logs/intake_ledger.md"; s = open(p).read()
sec = s.rfind("## INTAKE R17 ")
head, body = s[:sec], s[sec:]
m = re.search(r"^- R17 %s\.png \([^)]*\) — UNVIEWED$" % re.escape(stem), body, re.M)
if not m: sys.exit("no UNVIEWED line for " + stem)
line = m.group(0).replace("— UNVIEWED", "— VIEWED (" + note + ")")
body = body[:m.start()] + line + body[m.end():]
open(p, "w").write(head + body)
tot = len(re.findall(r"^- R17 ", body, re.M)); done = len(re.findall(r"^- R17 .*— VIEWED", body, re.M))
print(f"{stem} ticked — R17 {done}/{tot} viewed")
