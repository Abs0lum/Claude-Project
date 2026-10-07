#!/usr/bin/env python3
"""attachables_lint.py — ATT standing gate (D-C288): a client entity whose VANILLA counterpart sets
"enable_attachables": true must set it too.

Why (his R10 p7 d02, 17:52 CT 09-29: the bogged "has no bow"): attachable items (bow, crossbow, trident, shield, spyglass, wolf
armor, ...) are drawn only when the holder's client entity enables attachables. Our Converter-B rebuilds (format 1.26.0) dropped the
flag, so the bogged's bow was never bound or drawn. The log stays SILENT in that case (no binding is attempted), which is why the
R9 binding error belonged to the stray, not the bogged. Swords and axes are plain items (not attachables); they still show,
which hides the gap on piglins and wither skeletons.
Vanilla table = Mojang bedrock-samples resource_pack/entity (sparse clone at _ref/bs_sparse).
API: vanilla_table() -> {identifier: [files]} ; lint_pack(pack) -> (n_entities, [(entity file, identifier)])"""
import glob, os, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

VANILLA = Path("/home/claude/_ref/bs_sparse/resource_pack/entity")


def _desc(p):
    try: d = ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))
    except Exception: return None
    if not isinstance(d, dict): return None
    return (d.get("minecraft:client_entity") or {}).get("description")


def vanilla_table():
    out = {}
    for p in sorted(glob.glob(str(VANILLA / "*.json"))):
        de = _desc(p)
        if de and de.get("enable_attachables") is True:
            out.setdefault(de["identifier"], []).append(os.path.basename(p))
    return out


def lint_pack(pack, table=None):
    table = table if table is not None else vanilla_table()
    n = 0; finds = []
    root = Path(pack) / "entity"
    for p in sorted(root.rglob("*.json")) if root.exists() else []:
        de = _desc(p)
        if not de or "identifier" not in de: continue
        n += 1
        if de["identifier"] in table and de.get("enable_attachables") is not True:
            finds.append((p.relative_to(pack).as_posix(), de["identifier"]))
    return n, finds


def _selftest():
    t = vanilla_table()
    assert len(t) >= 20 and "minecraft:bogged" in t and "minecraft:skeleton" in t and "minecraft:wolf" in t, sorted(t)
    assert "minecraft:cow" not in t
    print(f"attachables_lint self-test OK ({len(t)} vanilla ids enable attachables)")


if __name__ == "__main__":
    _selftest()
    bad = 0
    for a in sys.argv[1:]:
        n, f = lint_pack(a)
        print(f"{Path(a).name}: {n} client entities; {len(f)} missing enable_attachables")
        for x in f: print("  ", x)
        bad += len(f)
    sys.exit(1 if bad else 0)
