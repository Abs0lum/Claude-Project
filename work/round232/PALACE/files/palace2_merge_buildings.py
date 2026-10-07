#!/usr/bin/env python3
"""palace2_merge_buildings.py — 1.3.232 (#21, HOOK-PROPOSAL Part C): merge the 16 PALACE II entries into BP-02's building
table. Input: _staging/palace231/palace2_buildings_entries.json (written by tools/palace2_hookdata.py; NOT in the GitHub
mirror — it is generated in the cloud workspace from the piece manifests). Output: scripts/pw_civ_buildings.js.

Rules:
  * the 16 keys pw:mvv_palace2_<r><c>_a_r1 (r, c in 0..3) are added (replaced when present: running it twice changes nothing);
  * the 4 pw:mvv_palace_{sw,se,nw,ne}_a_r1 entries STAY — a saved world's 2 x 2 palace and the clock's FAIL-SAFE fallback
    read them (drop them only once no saved world holds a 2 x 2 palace and the fallback is retired);
  * every new entry is checked as the clock reads it: stem == key without "pw:", size [64, 50, 64], datum_y 15, stages 5,
    door [x, y, z], lids / dir / chests / art lists, bom = 5 stage dicts (the crown's works pay wages by it);
  * the file keeps its form: the generator's comment line, then `export const CIV_BUILDINGS = {...};` (compact JSON).
Without the merge the clock still runs: checkPalaceII finds no table entries, logs one [CIV-PALACE] line and the crown builds
the 2 x 2 palace.
Usage: python3 palace2_merge_buildings.py <pw_civ_buildings.js> <palace2_buildings_entries.json> [--out FILE] [--check]
  --check  validate only (exit 1 on a problem), write nothing
"""
import json
import re
import sys

KEYS = [f"pw:mvv_palace2_{r}{c}_a_r1" for r in range(4) for c in range(4)]
OLD = [f"pw:mvv_palace_{q}_a_r1" for q in ("sw", "se", "nw", "ne")]
HEAD = re.compile(r"^(?P<head>(?://[^\n]*\n)*)export const CIV_BUILDINGS = (?P<json>\{.*\});\s*$", re.S)


def read_table(path):
    text = open(path, encoding="utf-8").read()
    m = HEAD.match(text)
    if not m:
        raise SystemExit(f"{path}: not the generated form (comment lines + export const CIV_BUILDINGS = {{...}};)")
    return m.group("head"), json.loads(m.group("json"))


def check_entry(key, e):
    """the problems of one PALACE II entry ([] = fine)"""
    bad = []
    if e.get("stem") != key.split(":", 1)[1]:
        bad.append(f"stem {e.get('stem')!r}")
    if e.get("size") != [64, 50, 64]:
        bad.append(f"size {e.get('size')}")
    if e.get("datum_y") != 15:
        bad.append(f"datum_y {e.get('datum_y')}")
    if e.get("stages") != 5:
        bad.append(f"stages {e.get('stages')}")
    door = e.get("door")
    if not (isinstance(door, list) and len(door) == 3 and all(isinstance(v, (int, float)) for v in door)):
        bad.append(f"door {door}")
    for k in ("lids", "dir", "chests", "art"):
        if not isinstance(e.get(k), list):
            bad.append(f"{k} not a list")
    bom = e.get("bom")
    if not (isinstance(bom, list) and len(bom) == 5 and all(isinstance(s, dict) for s in bom)):
        bad.append("bom missing or not 5 stage dicts (palace2_hookdata.py without --no-bom)")
    return bad


def merge(table, entries):
    """the merged table + the problems ([] = fine); never drops an existing entry"""
    problems = []
    missing = [k for k in KEYS if k not in entries]
    extra = [k for k in entries if k not in KEYS]
    if missing:
        problems.append(f"entries missing: {', '.join(missing)}")
    if extra:
        problems.append(f"unexpected entries: {', '.join(extra)}")
    for k in KEYS:
        if k in entries:
            for b in check_entry(k, entries[k]):
                problems.append(f"{k}: {b}")
    for k in OLD:
        if k not in table:
            problems.append(f"{k} is not in the table (a saved 2 x 2 palace and the fallback need it)")
    out = dict(table)
    for k in KEYS:
        if k in entries:
            out[k] = entries[k]
    return out, problems


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2:
        raise SystemExit(__doc__)
    table_path, entries_path = args[0], args[1]
    out_path = argv[argv.index("--out") + 1] if "--out" in argv else table_path
    head, table = read_table(table_path)
    entries = json.load(open(entries_path, encoding="utf-8"))
    merged, problems = merge(table, entries)
    for p in problems:
        print("PROBLEM", p)
    if problems:
        return 1
    if "--check" in argv:
        print(f"OK: {len(KEYS)} PALACE II entries valid; table {len(table)} -> {len(merged)} entries (the 4 2 x 2 entries kept)")
        return 0
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(head + "export const CIV_BUILDINGS = " + json.dumps(merged, separators=(",", ":"), ensure_ascii=False) + ";")
    print(f"merged: table {len(table)} -> {len(merged)} entries -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
