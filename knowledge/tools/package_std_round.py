#!/usr/bin/env python3
"""package_std_round.py — packages the STANDARD ROUND delivery (10-01) into /mnt/user-data/outputs and proves each archive ==
its build dir. Refuses a name that already exists with different bytes (never reuse a version number for different bytes).
Never deletes (his 14:41 rule): a refused temp archive is MOVED to _garbage. Log times are Chicago time (the workspace clock
is UTC — the old packager wrote UTC hours labelled "CT")."""
import datetime
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path("/home/claude")
OUT = Path("/mnt/user-data/outputs")
JOBS = [   # 16:3x 10-01: content-log fix 3 (his log 3 + R1 = a)
    ("rp07-1443", "RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_43.mcpack"),
    ("rp04-144", "RP-04-AbsolutRealism-Basic-RP-v1_3_144.mcpack"),
    ("testrunner-0.5.11", "PW-TestRunner-BP-v0_5_11.mcpack"),
]


def ct():
    return datetime.datetime.now(ZoneInfo("America/Chicago")).strftime("%H:%M CT %m-%d")


def md5b(b):
    return hashlib.md5(b).hexdigest()


def pack(src, out):
    tmp = out.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, str(p.relative_to(src)).replace("\\", "/"))
    with zipfile.ZipFile(tmp) as z:
        zh = {n: md5b(z.read(n)) for n in z.namelist() if not n.endswith("/")}
    th = {str(p.relative_to(src)).replace("\\", "/"): md5b(p.read_bytes()) for p in src.rglob("*") if p.is_file()}
    assert zh == th and "manifest.json" in zh, f"{out.name}: archive != build dir"
    if out.exists() and md5b(out.read_bytes()) != md5b(tmp.read_bytes()):
        g = ROOT / "_garbage" / datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S") / "refused" / tmp.name
        g.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp), str(g))
        raise SystemExit(f"REFUSED: {out.name} already exists with different bytes")
    tmp.replace(out)
    return out.stat().st_size, md5b(out.read_bytes()), len(th)


def main(only=None):
    for d, name in JOBS:
        if only and d not in only:
            continue
        size, md5, n = pack(ROOT / "_build" / d, OUT / name)
        line = f"PACKAGED {name} {size:,} B md5 {md5} ({n} files, archive == build dir)"
        print(line, flush=True)
        with open(ROOT / "_logs/phase_log.md", "a") as f:
            f.write(f"[{ct()}] {line}\n")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
