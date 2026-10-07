#!/usr/bin/env python3
"""ledgerprobe_copy.py — D-C514/515: make a JOB-ONLY ledger-probe copy of a BP-02 build (same uuid on purpose: dynamic properties are
keyed per pack uuid). The probe hooks are taken byte-for-byte from the first probe copy (bp02-212-ledgerprobe minus bp02-212), so
every probe copy carries identical hooks. Usage: ledgerprobe_copy.py SRC_BUILD_DIR DST_DIR. Never deliver a *-ledgerprobe dir."""
import shutil, sys
from pathlib import Path
B = Path("/home/claude/_build")
REF_ORIG, REF_PROBE = B / "bp02-212", B / "bp02-212-ledgerprobe"
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
if dst.exists():
    raise SystemExit(f"exists: {dst}")
shutil.copytree(src, dst)
for f in ("scripts/pw_homestead.js", "scripts/pw_mob_light.js", "scripts/main.js"):
    o, p = (REF_ORIG / f).read_bytes(), (REF_PROBE / f).read_bytes()
    assert p.startswith(o), f"reference probe copy of {f} does not extend the original"
    hook = p[len(o):]
    t = (dst / f).read_bytes()
    (dst / f).write_bytes(t + hook)
    assert (dst / f).read_bytes() == t + hook
    print(f"{f}: +{len(hook)} B of probe hooks")
(dst / "PROBE-ONLY-NEVER-DELIVER.txt").write_text(f"{dst.name}: job-only ledger-probe copy of {src.name} (hooks from bp02-212-ledgerprobe). Same uuid on purpose. NEVER deliver.\n")
