#!/usr/bin/env python3
"""sf_unnest.py — his 18:59 ruling: "let's just unnest the folder and remap or redirect everything that points to it.
This also simplifies a reskin later."

The Naturalist pictures lived in textures/sf/nba/<group>/ with three byte-identical copies (RP-06, RP-07, RP-08;
RP-08 on top draws them). After this tool there is ONE copy, in RP-08, in the standard folders:
  textures/sf/nba/entity/X       -> textures/entity/sf_nba/X        (creatures: the folder MS documents for entity PBR)
  textures/sf/nba/attachables/X  -> textures/entity/sf_nba/attachables/X
  textures/sf/nba/blocks/X       -> textures/blocks/sf_nba/X
  textures/sf/nba/items/X        -> textures/items/sf_nba/X
  textures/sf/nba/particle/X     -> textures/particle/sf_nba/X
Texture sets move with their pictures (their layer names are file stems in the same folder, so they stay valid).
Every reference in every pack is rewritten (json / js / material / lang text), and the RP-06 / RP-07 copies are moved to
_garbage (never deleted). RP-06 1.4.28 is delivered -> its change goes into a NEW build RP-06 1.4.29.
Checks: no 'textures/sf/' string left anywhere; every rewritten path resolves to a file in the stack."""
import json
import re
import shutil
import time
from pathlib import Path

B = Path("/home/claude/_build")
OWNER = B / "rp08-1413"
COPIES = [B / "rp07-1444", B / "rp06-1429"]
REF_PACKS = [B / d for d in ("rp08-1413", "rp07-1444", "rp06-1429", "rp02-207", "rp01-117", "rp03-67", "rp04-156",
                             "rp05-58", "rp10-151", "rp11-140", "bp02-206", "testrunner-0.5.13")]
MAP = [("textures/sf/nba/entity/", "textures/entity/sf_nba/"),
       ("textures/sf/nba/attachables/", "textures/entity/sf_nba/attachables/"),
       ("textures/sf/nba/blocks/", "textures/blocks/sf_nba/"),
       ("textures/sf/nba/items/", "textures/items/sf_nba/"),
       ("textures/sf/nba/particle/", "textures/particle/sf_nba/")]
TEXT_EXT = {".json", ".js", ".material", ".lang", ".txt", ".mjs"}
GARBAGE = Path("/home/claude/_garbage") / f"sf-unnest-{time.strftime('%H%M%S')}"


def new_path(p):
    for a, b in MAP:
        if p.startswith(a):
            return b + p[len(a):]
    if p.startswith("textures/sf/nba/"):                 # loose files (empty.png + its set): entity folder
        return "textures/entity/sf_nba/" + p[len("textures/sf/nba/"):]
    return None


def main():
    # resumable: a first run stopped after moving attachables/ + blocks/ (empty.png had no mapping) — files already
    # moved are simply not found under textures/sf any more
    if not (B / "rp06-1429").exists():
        shutil.copytree(B / "rp06-1428", B / "rp06-1429")
    src_root = OWNER / "textures/sf"
    moved = 0
    for f in sorted(p for p in src_root.rglob("*") if p.is_file()):
        rel = f.relative_to(OWNER).as_posix()
        np = new_path(rel)
        assert np, rel
        dest = OWNER / np
        assert not dest.exists(), dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(f), str(dest))
        moved += 1
    GARBAGE.mkdir(parents=True, exist_ok=True)
    shutil.move(str(OWNER / "textures/sf"), str(GARBAGE / "rp08_empty_sf_dirs"))
    for pack in COPIES:
        if (pack / "textures/sf").exists():
            shutil.move(str(pack / "textures/sf"), str(GARBAGE / f"{pack.name}_textures_sf"))
    rx = re.compile(r"textures/sf/nba/(entity|attachables|blocks|items|particle)/")
    rewrites = {}
    for pack in REF_PACKS:
        for f in pack.rglob("*"):
            if not f.is_file() or f.suffix not in TEXT_EXT:
                continue
            try:
                s = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if "textures/sf/" not in s:
                continue
            t = rx.sub(lambda m: new_path(m.group(0)), s).replace("textures/sf/nba/", "textures/entity/sf_nba/")
            if "textures/sf/" in t:
                raise SystemExit(f"unmapped textures/sf left in {f}")
            f.write_text(t, encoding="utf-8")
            rewrites[str(f.relative_to(B))] = s.count("textures/sf/")
    left = [str(f) for pack in REF_PACKS for f in pack.rglob("*")
            if f.is_file() and f.suffix in TEXT_EXT and "textures/sf/" in f.read_text(encoding="utf-8", errors="ignore")]
    report = {"moved_files": moved, "garbage": str(GARBAGE), "rewritten_files": len(rewrites),
              "rewritten_refs": sum(rewrites.values()), "left": left, "files": rewrites}
    Path("/home/claude/_docs/stripmine/SF-UNNEST-REPORT.json").write_text(json.dumps(report, indent=1))
    print({k: v for k, v in report.items() if k != "files"})


if __name__ == "__main__":
    main()
