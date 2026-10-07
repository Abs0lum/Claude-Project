#!/usr/bin/env python3
"""package_r16a.py — packages R16a (D-C310 / D-C312): RP-06 1.4.22 + RP-07 1.4.28 + BP-02 1.3.194 into /mnt/user-data/outputs and proves each archive == its build dir.
Refuses a name that already exists with different bytes (never reuse a version number for different bytes)."""
import hashlib, sys, time, zipfile
from pathlib import Path

ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs")
JOBS = [("rp06-1422", "RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_22.mcpack"), ("rp07-1428", "RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_28.mcpack"),
        ("bp02-194", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_194.mcpack")]


def md5b(b):
    return hashlib.md5(b).hexdigest()


def pack(src, out):
    tmp = out.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:     # D-C301: deterministic (fixed entry dates)
        for p in sorted(src.rglob("*")):
            if p.is_file():
                zi = zipfile.ZipInfo(str(p.relative_to(src)).replace("\\", "/"), date_time=(2026, 9, 29, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16
                z.writestr(zi, p.read_bytes(), compresslevel=6)
    with zipfile.ZipFile(tmp) as z:
        zh = {n: md5b(z.read(n)) for n in z.namelist() if not n.endswith("/")}
    th = {str(p.relative_to(src)).replace("\\", "/"): md5b(p.read_bytes()) for p in src.rglob("*") if p.is_file()}
    assert zh == th and "manifest.json" in zh, f"{out.name}: archive != build dir"
    if out.exists() and md5b(out.read_bytes()) != md5b(tmp.read_bytes()):
        tmp.unlink(); raise SystemExit(f"REFUSED: {out.name} already exists with different bytes")
    tmp.replace(out)
    return out.stat().st_size, md5b(out.read_bytes()), len(th)


def main():
    for d, name in JOBS:
        size, md5, n = pack(ROOT / "_build" / d, OUT / name)
        line = f"PACKAGED {name} {size:,} B md5 {md5} ({n} files, archive == build dir)"
        print(line)
        with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT 09-30] {line}\n")


if __name__ == "__main__":
    main()
