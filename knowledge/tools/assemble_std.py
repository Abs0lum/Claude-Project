#!/usr/bin/env python3
"""assemble_std.py — his 14:35 rule (build in pieces, put together at the end): the frozen BASE groups (_staging/std) are never
edited by a layer. Assembly = a fresh copy of the base in _staging/assembled (the previous assembly is moved to _garbage, his
14:41 rule), then each layer applied ON THE COPY in a fixed order:
  share   std_share.py (same species, other creator; carries the variables a clip reads, molang_carry)
  sharefix std_sharefix.py (p22: loose shared_ copies rebaked through the family retarget, else dropped)
  fam     std_famshare.py (p22: anatomy family, world-space retarget, ground lock) — only with --fam
  parade  std_parade.py (p22: treadmill copies of movement-driven clips, for the pens) — only with --parade The builder reads the assembly. Prints the layer reports."""
import datetime
import shutil
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402

BASE = ROOT / "_staging/std"
ASM = ROOT / "_staging/assembled"


def discard(p):
    if p.exists():
        dst = ROOT / "_garbage" / datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S") / p.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(dst))


def assemble(layers=("share",)):
    import std_groups as G
    if not G.check():
        sys.exit("GUARD FAIL on the base — nothing assembled")
    discard(ASM)
    shutil.copytree(BASE, ASM)
    S.STAGE = ASM                      # every layer below reads and writes the ASSEMBLY, never the base
    import std_share as SH
    SH.S.STAGE = ASM
    SH.main(True)
    import std_sharefix as SF           # p22: a shared_ copy that pulls a part loose is rebaked (family retarget) or dropped
    SF.main(ASM, write=True)
    if "fam" in layers:                 # p22: the FAMILY layer (std_famshare), applied after the share layer, on the copy only
        import std_famshare as FS
        FS.main(ASM, write=True)
    if "parade" in layers:              # p22: treadmill copies of movement-driven clips for the witness pens (std_parade)
        import std_parade as PA
        PA.main(ASM, write=True)
    return ASM


if __name__ == "__main__":
    print("assembled at", assemble(tuple(["share"] + (["fam"] if "--fam" in sys.argv else [])
                                         + (["parade"] if "--parade" in sys.argv else []))))
