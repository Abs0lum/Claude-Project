#!/usr/bin/env python3
"""p0_ledger.py — tick P0 screenshot ledger lines VIEWED (P10) and keep the count line current.
usage: p0_ledger.py <stem> "<literal read>"  [<stem> "<read>" ...]
       p0_ledger.py --count
Also appends the read to _intake/p0-shots/reads.md (the on-disk notebook, survives turn death)."""
import re, sys, time

LEDGER = "_logs/intake_ledger.md"
READS = "_intake/p0-shots/reads.md"

def main():
    txt = open(LEDGER).read()
    args = sys.argv[1:]
    if args and args[0] == "--count":
        pass
    else:
        pairs = list(zip(args[0::2], args[1::2]))
        now = time.strftime("%H:%M")
        with open(READS, "a") as f:
            for stem, read in pairs:
                pat = re.compile(rf"^(- S\d{{3}} {re.escape(stem)}\.png \([^)]*\)) — UNVIEWED$", re.M)
                if not pat.search(txt):
                    print("no UNVIEWED line for", stem); continue
                txt = pat.sub(rf"\1 — VIEWED: {read}", txt, count=1)
                f.write(f"[{now}] {stem}: {read}\n")
    # recount the P0 block only
    head = txt.rfind("## INTAKE") if "P0 run screenshots" not in txt else txt.rfind("P0 run screenshots")
    block = txt[head:]
    n_all = len(re.findall(r"^- S\d{3} ", block, re.M))
    n_viewed = len(re.findall(r"^- S\d{3} .*— VIEWED", block, re.M))
    txt = re.sub(r"  -> \d+/\d+ VIEWED", f"  -> {n_viewed}/{n_all} VIEWED", txt)
    open(LEDGER, "w").write(txt)
    print(f"{n_viewed}/{n_all} VIEWED")

if __name__ == "__main__":
    main()
