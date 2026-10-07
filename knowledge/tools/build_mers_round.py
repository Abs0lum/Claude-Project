#!/usr/bin/env python3
"""build_mers_round.py — MERS round builds (D-C367, his M1 = (c) for every mob).

Copies each source build to a NEW version dir (refuses an existing one: never rebuild a version) and adds the
staged texture sets from _staging/mers. A staged set goes into EVERY target pack that holds a byte-identical
colour at the same path (sf/nba sheets are identical in RP-06 / RP-07 / RP-08), so the pack order never decides
whether a mob gets its map (H-18: set, MERS and colour always in one pack). Flat-vanilla derivations carry their
own colour copy and go to RP-07 only.

Usage: build_mers_round.py            (all four packs)
Writes _logs/mers_round_manifest.json (every file added, per pack).
"""
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path("/home/claude")
STAGE = ROOT / "_staging/mers"
DATE = time.strftime("%Y-%m-%d")
TARGETS = {  # source dir -> (new dir, version, name prefix)
    "rp07-1438": ("rp07-1439", [1, 4, 39], "AbsolutRealism Neutral Mobs RP"),
    "rp06-1424": ("rp06-1425", [1, 4, 25], "AbsolutRealism Hostile Mobs RP"),
    "rp08-148": ("rp08-149", [1, 4, 9], "AbsolutRealism Items RP"),
    "rp04-142": ("rp04-143", [1, 3, 143], None),
}
NOTE = ("MERS ROUND (D-C367): Vibrant Visuals shine maps for every mob texture — Patrix's own LabPBR maps (#156) "
        "+ normals where Patrix has them, derived body-part maps for the rest; Mojang's own maps kept where they "
        "are authored.")


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f:
        f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD {m}\n")


def staged_sets():
    """[(staging pack, rel path without extension, [companion files])] for every staged texture_set.json."""
    out = []
    for pack_dir in sorted(STAGE.iterdir()):
        for ts in sorted(pack_dir.rglob("*.texture_set.json")):
            rel = ts.relative_to(pack_dir).as_posix()[: -len(".texture_set.json")]
            stem = ts.parent
            name = Path(rel).name
            files = [ts] + [p for p in (stem / f"{name}_mers.png", stem / f"{name}_n.png") if p.exists()]
            colour_copy = [p for p in (stem / f"{name}.png", stem / f"{name}.tga") if p.exists()]
            out.append((pack_dir.name, rel, files, colour_copy))
    return out


def colour_file(pack, rel):
    for ext in (".png", ".tga"):
        p = pack / (rel + ext)
        if p.exists():
            return p
    return None


def main():
    sets = staged_sets()
    added, replaced = {}, {}
    for src, (dst, ver, name) in TARGETS.items():
        s, d = ROOT / "_build" / src, ROOT / "_build" / dst
        if d.exists():
            sys.exit(f"REFUSED: {d} exists (a version is never rebuilt)")
        shutil.copytree(s, d)
        added[dst] = []
        for spack, rel, files, colour_copy in sets:
            src_colour = colour_file(ROOT / "_build" / spack, rel) if not colour_copy else None
            if colour_copy:
                if src != "rp07-1438":
                    continue
                for c in colour_copy:
                    tgt = d / c.relative_to(STAGE / spack)
                    tgt.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(c, tgt)
                    added[dst].append(tgt.relative_to(d).as_posix())
            else:
                mine = colour_file(d, rel)
                if mine is None or src_colour is None or md5(mine) != md5(src_colour):
                    continue
            for f in files:
                tgt = d / f.relative_to(STAGE / spack)
                if tgt.exists() and tgt.read_bytes() != f.read_bytes():
                    stem_set = tgt.with_name(Path(rel).name + ".texture_set.json")
                    raw_normal = tgt.name.endswith("_n.png") and not (s / stem_set.relative_to(d)).exists()
                    if not raw_normal:
                        sys.exit(f"REFUSED: {dst}/{tgt.relative_to(d)} already exists with other bytes")
                    replaced.setdefault(dst, []).append(tgt.relative_to(d).as_posix())  # unreferenced raw LabPBR _n
                tgt.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, tgt)
                added[dst].append(tgt.relative_to(d).as_posix())
        m = json.loads((d / "manifest.json").read_text(encoding="utf-8-sig"))
        old = m["header"].get("version")
        m["header"]["version"] = ver
        v = ".".join(map(str, ver))
        if name:
            m["header"]["name"] = f"{name} v{v}"
        m["header"]["description"] = f"v{v} ({DATE}) {NOTE} | " + str(m["header"].get("description", ""))[:400]
        for mod in m.get("modules", []):
            mod["version"] = ver
        (d / "manifest.json").write_text(json.dumps(m, indent=1))
        sets_n = sum(1 for a in added[dst] if a.endswith(".texture_set.json"))
        log(f"MERS ROUND {dst} v{v} (from {src} {old}): +{len(added[dst])} files, {sets_n} texture sets")
    (ROOT / "_logs/mers_round_manifest.json").write_text(json.dumps({"added": added, "replaced_raw_normals": replaced}, indent=1))
    print("replaced unreferenced raw normals:", {k: len(v) for k, v in replaced.items()})


if __name__ == "__main__":
    main()
