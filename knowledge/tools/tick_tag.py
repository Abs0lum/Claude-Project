#!/usr/bin/env python3
"""tick_tag.py <TAG> <file name> "<literal read>" — flips exactly that file's UNVIEWED line in the newest <TAG> intake section.
(D-C319: tick_intake.py ticks the LAST unviewed line of a tag, which ticked two shots unseen when called in a loop; this one
needs the file name.)"""
import re, sys
tag, name, note = sys.argv[1], sys.argv[2], sys.argv[3]
p = "/home/claude/_logs/intake_ledger.md"; s = open(p).read()
i = s.rfind(f"## INTAKE {tag} ")
if i < 0: sys.exit("no section " + tag)
head, body = s[:i], s[i:]
m = re.search(r"^- %s %s \([^)]*\) — UNVIEWED$" % (re.escape(tag), re.escape(name)), body, re.M)
if not m: sys.exit(f"no UNVIEWED line for {name}")
body = body[:m.start()] + m.group(0).replace("— UNVIEWED", f"— VIEWED ({note})") + body[m.end():]
open(p, "w").write(head + body)
print(f"{name}: {body.count('— VIEWED')}/{len(re.findall(r'^- %s ' % re.escape(tag), body, re.M))} viewed")
