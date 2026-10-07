#!/usr/bin/env python3
"""garbage_to_drive.py — his rule (10-01): when the workspace allowance is tight, _garbage goes to his Drive:
copy -> md5 verify (Drive's md5Checksum == local, via gdrive_upload's ledger) -> only then remove the local copy.
Usage: garbage_to_drive.py DIR [DIR ...]   (each a folder directly under _garbage)"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import gdrive_upload as GU  # noqa: E402

ROOT = Path("/home/claude/_garbage")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main(dirs):
    for name in dirs:
        d = ROOT / name
        if not d.is_dir():
            continue
        summary = GU.upload_tree(str(d), f"AR-Garbage-{name}")
        led = json.loads(GU.LEDGER.read_text())
        files = [p for p in d.rglob("*") if p.is_file()]
        top = f"AR-Garbage-{name}"
        ok = bool(files) and all(led.get(f"{top}/{p.relative_to(d).as_posix()}", {}).get("md5") == md5(p) for p in files)
        print(name, "files", len(files), "verified" if ok else "NOT VERIFIED", {k: v for k, v in summary.items() if k != "files"} if isinstance(summary, dict) else "")
        if ok:
            shutil.rmtree(d)          # inside _garbage: a real removal, only after Drive holds identical bytes
            print("  local copy removed")


if __name__ == "__main__":
    main(sys.argv[1:])
