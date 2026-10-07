#!/usr/bin/env python3
"""splice_inn_table.py — 1.3.232 (#INN): rewrite the inn entries of BP-02 scripts/pw_civ_buildings.js as TEXT (every other
entry stays byte for byte):
  pw:mvv_inn_{a,b,c,d}_r1   <- the exact text of the same entries in the 1.3.230 table (the inn as it stands in his worlds)
  pw:mvv_inn_{a,b,c,d}_r2   <- the new mixed-room inn (inn_v2.py's CIV_BUILDINGS-inn.json, json.dumps compact, the format
                               civ_village_data.py writes and round 231 spliced), inserted right after pw:mvv_inn_d_r1
Usage: splice_inn_table.py TABLE_231_JS TABLE_230_JS INN_R2_JSON OUT_JS"""
import json
import sys
from pathlib import Path

DEC = json.JSONDecoder()


def span(txt, key):
    """(start, end) of the text `"key":{...}` inside the one-line table (end = just past the value)."""
    tag = f'"{key}":'
    i = txt.find(tag)
    assert i >= 0 and txt.find(tag, i + 1) < 0, f"{key}: found {txt.count(tag)} times"
    _obj, end = DEC.raw_decode(txt, i + len(tag))
    return i, end


def main():
    t231, t230, r2json, out = sys.argv[1:5]
    txt = Path(t231).read_text()
    old = Path(t230).read_text()
    r2 = json.loads(Path(r2json).read_text())
    keys = [f"pw:mvv_inn_{k}_r1" for k in "abcd"]
    for key in keys:                                        # r1 <- 1.3.230, verbatim
        a, b = span(txt, key)
        c, d = span(old, key)
        txt = txt[:a] + old[c:d] + txt[b:]
    _a, b = span(txt, keys[-1])                             # r2 after the last r1 entry
    ins = "".join(f',"{k}":{json.dumps(v, separators=(",", ":"))}' for k, v in sorted(r2.items()))
    assert all(k.endswith("_r2") for k in r2) and len(r2) == 4, sorted(r2)
    txt = txt[:b] + ins + txt[b:]
    Path(out).write_text(txt)
    print(f"{out}: {len(txt):,} B; r1 x4 from 1.3.230, r2 x4 inserted ({len(ins):,} B)")


if __name__ == "__main__":
    main()
