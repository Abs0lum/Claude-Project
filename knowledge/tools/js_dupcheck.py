#!/usr/bin/env python3
"""js_dupcheck.py — top-level duplicate declarations in ES modules (QuickJS, the Bedrock script engine, refuses them with
"invalid redefinition of global identifier"; node --check lets duplicate function declarations and some redefinitions
through). Usage: js_dupcheck.py FILE.js [...] ; exit 1 when any file has a duplicate (prints name: lines)."""
import re
import sys

PAT = re.compile(r"^(?:export\s+)?(?:async\s+)?(?:function\*?\s+(\w+)|(?:const|let|var)\s+(\w+)|class\s+(\w+))", re.M)
DESTR = re.compile(r"^(?:export\s+)?(?:const|let|var)\s+\{([^}]*)\}\s*=", re.M)


def dups(text):
    names = {}
    for m in PAT.finditer(text):
        n = m.group(1) or m.group(2) or m.group(3)
        names.setdefault(n, []).append(text[:m.start()].count("\n") + 1)
    for m in DESTR.finditer(text):
        for part in m.group(1).split(","):
            n = part.split(":")[-1].strip()
            if n:
                names.setdefault(n, []).append(text[:m.start()].count("\n") + 1)
    for m in re.finditer(r"^import\s+\*\s+as\s+(\w+)|^import\s+\{([^}]*)\}", text, re.M):
        for n in ([m.group(1)] if m.group(1) else [p.split(" as ")[-1].strip() for p in m.group(2).split(",") if p.strip()]):
            names.setdefault(n, []).append(text[:m.start()].count("\n") + 1)
    return {k: v for k, v in names.items() if len(v) > 1}


def main():
    bad = 0
    for f in sys.argv[1:]:
        d = dups(open(f, encoding="utf-8").read())
        if d:
            bad += 1
            print(f"{f}: " + "; ".join(f"{k}: lines {v}" for k, v in d.items()))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
