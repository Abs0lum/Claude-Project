#!/usr/bin/env python3
"""r2_tick.py — P10 ledger ticker for the round-2 screenshot intake.
usage: python3 tools/r2_tick.py <stem> [<stem> ...]   -> flips those R2 lines from UNVIEWED to VIEWED (idempotent)
       python3 tools/r2_tick.py --count               -> prints viewed/total for the R2 block
The tick is applied at the moment the image was viewed at full resolution (never before)."""
import re, sys
from pathlib import Path
LEDGER = Path(__file__).resolve().parent.parent / "_logs" / "intake_ledger.md"

def main(argv):
    text = LEDGER.read_text(encoding="utf-8")
    lines = text.split("\n")
    r2 = [i for i, l in enumerate(lines) if l.startswith("- R2 ")]
    if argv and argv[0] != "--count":
        want = set(argv)
        hit = set()
        for i in r2:
            m = re.match(r"- R2 (\d+(?:_\d+)?)\.png ", lines[i])
            if m and m.group(1) in want:
                lines[i] = re.sub(r" — UNVIEWED$", " — VIEWED", lines[i])
                hit.add(m.group(1))
        missing = want - hit
        if missing:
            print("NOT IN LEDGER:", sorted(missing))
    viewed = sum(1 for i in r2 if lines[i].endswith(" — VIEWED"))
    total = len(r2)
    # refresh the summary line if present
    for i, l in enumerate(lines):
        if re.match(r"^\*\*R2 ledger: \d+/\d+ VIEWED", l) or re.match(r"^R2: \d+/\d+ VIEWED", l) or re.match(r"^\d+/\d+ VIEWED", l):
            lines[i] = f"{viewed}/{total} VIEWED"
    LEDGER.write_text("\n".join(lines), encoding="utf-8")
    print(f"R2 ledger: {viewed}/{total} VIEWED")

if __name__ == "__main__":
    main(sys.argv[1:])
