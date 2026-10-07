#!/usr/bin/env python3
"""tick_intake.py <TAG> "<literal read>" — flips the newest ledger line for TAG from UNVIEWED to VIEWED (read)."""
import sys, re
tag, note = sys.argv[1], sys.argv[2]
p = "_logs/intake_ledger.md"
s = open(p).read()
# find the LAST occurrence of the tag line marked UNVIEWED
idx = [m.start() for m in re.finditer(r"^- %s .*— UNVIEWED$" % re.escape(tag), s, re.M)]
if not idx:
    sys.exit("no UNVIEWED line for %s" % tag)
i = idx[-1]
j = s.index("— UNVIEWED", i)
s = s[:j] + "— VIEWED (" + note + ")" + s[j+len("— UNVIEWED"):]
open(p, "w").write(s)
tot = len(re.findall(r"^- F\d\d .*$", s.split("## INTAKE 2026-09-22 19:46")[-1], re.M))
done = len(re.findall(r"^- F\d\d .*— VIEWED", s.split("## INTAKE 2026-09-22 19:46")[-1], re.M))
print(f"{tag} ticked — {done}/{tot} viewed")
