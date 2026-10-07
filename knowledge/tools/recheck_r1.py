#!/usr/bin/env python3
"""recheck_r1.py — RECHECK-WEEK R1 (his 21:45 10-02 "recheck all our work for the week"): delivery integrity of the
CURRENT INSTALL SET (HANDOFF-2026-10-02-ROUND-1002n-DELIVERED):
  a) the delivered archive still exists in /mnt/user-data/outputs with the md5 the delivery ledger recorded
  b) the archive == its build dir, file by file (the build dir is FROZEN: nothing changed since delivery)
  c) every pack is <= 250 MB (his cap)
Writes _docs/recheck/R1-delivery.json. Read-only."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path("/home/claude")
OUT = Path("/mnt/user-data/outputs")
LEDGER = ROOT / "_logs/delivery_ledger.md"
# install set: (archive name, build dir)
SET = [
    ("BP-02-AbsolutRealism-Tectonic-BP-v1_3_206.mcpack", "bp02-206"),
    ("RP-01-AbsolutRealism-Tectonic-RP-v1_3_117.mcpack", "rp01-117"),
    ("RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_7.mcpack", "rp02-207"),
    ("RP-03-AbsolutRealism-PBR-RP-v1_3_67.mcpack", "rp03-67"),
    ("RP-04-AbsolutRealism-Basic-RP-v1_3_156.mcpack", "rp04-156"),
    ("RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_29.mcpack", "rp06-1429"),
    ("RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_44.mcpack", "rp07-1444"),
    ("RP-08-AbsolutRealism-Items-RP-v1_4_13.mcpack", "rp08-1413"),
    ("RP-11-AbsolutRealism-Ores-RP-v1_3_40.mcpack", "rp11-140"),
    ("PW-TestRunner-BP-v0_5_13.mcpack", "testrunner-0.5.13"),
    ("RP-05-AbsolutRealism-Flora-RP-v1_3_58.mcpack", "rp05-58"),
    ("RP-10-AbsolutRealism-Terrain-RP-v1_3_51.mcpack", "rp10-151"),
    ("BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_35.mcpack", "bp01-135"),
    ("BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_34.mcpack", "bp03-134"),
    ("PW-Civitas-Markers-BP-v0_2_1.mcpack", "markers-0.2.1/BP"),
    ("PW-Civitas-Markers-RP-v0_2_2.mcpack", "markers-0.2.2-rp/RP"),
]


def md5b(b):
    return hashlib.md5(b).hexdigest()


def ledger_md5(name):
    """the LAST ledger line that names this archive (a re-delivery supersedes)."""
    hit = None
    for line in LEDGER.read_text().splitlines():
        if name in line:
            m = re.search(r"md5 ([0-9a-f]{32})", line)
            if m:
                hit = (m.group(1), line.strip()[:160])
    return hit


def main():
    rows = []
    for name, bdir in SET:
        r = {"archive": name, "build": bdir}
        arc = OUT / name
        if not arc.exists():
            cands = sorted(ROOT.glob(f"_bundles/**/{name}")) + sorted(ROOT.glob(f"**/{name}"))
            r["archive_found"] = str(cands[0]) if cands else None
            arc = cands[0] if cands else None
        if arc is None:
            r["status"] = "ARCHIVE MISSING"
            rows.append(r)
            continue
        b = arc.read_bytes()
        r["size"] = len(b)
        r["md5"] = md5b(b)
        led = ledger_md5(name)
        r["ledger_md5"] = led[0] if led else None
        r["ledger_line"] = led[1] if led else None
        r["md5_matches_ledger"] = bool(led) and led[0] == r["md5"]
        r["under_cap"] = len(b) <= 250 * 1000 * 1000
        src = ROOT / "_build" / bdir
        if src.exists():
            with zipfile.ZipFile(arc) as z:
                zh = {n: md5b(z.read(n)) for n in z.namelist() if not n.endswith("/")}
            th = {str(p.relative_to(src)).replace("\\", "/"): md5b(p.read_bytes()) for p in src.rglob("*") if p.is_file()}
            only_zip = sorted(set(zh) - set(th))
            only_dir = sorted(set(th) - set(zh))
            diff = sorted(k for k in zh if k in th and zh[k] != th[k])
            r["files"] = len(zh)
            r["build_frozen"] = not (only_zip or only_dir or diff)
            r["only_in_archive"] = only_zip[:10]
            r["only_in_build_dir"] = only_dir[:10]
            r["changed_since_delivery"] = diff[:10]
        else:
            r["build_frozen"] = None
            r["build_note"] = "build dir not in workspace (older delivery)"
        r["status"] = "PASS" if (r["md5_matches_ledger"] and r["under_cap"] and r["build_frozen"] in (True, None)) else "FAIL"
        rows.append(r)
        print(f"{r['status']:5} {name:60} {r['size']:>12,} B md5 {r['md5'][:8]} ledger {'==' if r['md5_matches_ledger'] else '!='} "
              f"frozen {r['build_frozen']}", flush=True)
    Path(ROOT / "_docs/recheck").mkdir(parents=True, exist_ok=True)
    (ROOT / "_docs/recheck/R1-delivery.json").write_text(json.dumps(rows, indent=1))
    print(sum(1 for r in rows if r["status"] == "PASS"), "/", len(rows), "PASS")


if __name__ == "__main__":
    main()
