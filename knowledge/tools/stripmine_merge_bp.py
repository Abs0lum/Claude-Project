#!/usr/bin/env python3
"""stripmine_merge_bp.py — phase 1 of the StripMine dissolve (his 15:42 S1 + 16:47 SM1 'yes for all', SM2 = a: behaviour
into BP-02). Plan: _docs/stripmine/STRIPMINE-MERGE-CENSUS-2026-10-02.md §4-§7.

BP-02 1.3.206 = BP-02 1.3.205 + every StripMine BP 1.3.13 file, labelled by its source add-on:
  * Naturalist files in path-free folders (entities, spawn_rules, items, blocks, animations, animation_controllers,
    features, feature_rules) move under <folder>/sf_nba/…; menagerie files keep <folder>/pw_menagerie/<source>/….
  * Path-referenced folders keep their paths (loot_tables/**, functions/sf/**, recipes/sf/**, structures/sf_nba/**):
    entity files, feature files and commands name these paths, so moving them would break the references.
  * Naturalist scripts -> scripts/stripmine/sf_nba/** DORMANT (not imported by main.js; D2 = a: exactly today's
    behaviour — StripMine BP never had a script module).
  * NOT moved (archived with the retired pack): manifest.json, pack_icon.png, PW-DEPENDENCIES.md, texts/* (pack name +
    a marketplace content key only), update_recipe_enum.js (a dev script).
  * item_catalog/crafting_item_catalog.json -> BP-02 item_catalog/ (BP-02 has none).
Identifiers are never renamed. A PROVENANCE-STRIPMINE.json at the pack root records every moved file (source pack,
origin add-on, original path, bytes, sha1). Exits non-zero if any destination path already exists in BP-02."""
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC_DIR, BASE_DIR, OUT_DIR = B / "stripmine-bp-1313", B / "bp02-205", B / "bp02-206"
SRC_PACK = "PW StripMine BP 1.3.13"
PATH_FREE = {"entities", "spawn_rules", "items", "blocks", "animations", "animation_controllers", "features",
             "feature_rules"}
NOT_MOVED = {"manifest.json", "pack_icon.png", "PW-DEPENDENCIES.md", "update_recipe_enum.js",
             "texts/en_US.lang", "texts/languages.json"}
MENAGERIE_SOURCES = {"anf": "Animals and Fauna", "wa": "World Animals", "wwa": "WWA", "ysav": "yCreatures Savanna",
                     "ytri": "yCreatures Trial", "ws": "Wildlife Sanctuary", "ifs": "Immersive Fauna Savanna"}


def origin_addon(rel):
    m = re.search(r"pw_menagerie/([a-z]+)/", rel)
    if m:
        return MENAGERIE_SOURCES.get(m.group(1), m.group(1))
    return "Naturalist (sf_nba)"


def destination(rel):
    """StripMine BP relative path -> BP-02 relative path (None = not moved)."""
    if rel in NOT_MOVED:
        return None
    top, _, rest = rel.partition("/")
    if top == "scripts":
        return f"scripts/stripmine/sf_nba/{rest}"
    if top in PATH_FREE and not rest.startswith("pw_menagerie/"):
        return f"{top}/sf_nba/{rest}"
    return rel


def sha1(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def main():
    assert not OUT_DIR.exists(), f"never rebuild {OUT_DIR.name}"
    plan, collisions, skipped = [], [], []
    for path in sorted(SRC_DIR.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(SRC_DIR).as_posix()
        dest = destination(rel)
        if dest is None:
            skipped.append(rel)
            continue
        if (BASE_DIR / dest).exists():
            collisions.append((rel, dest))
        plan.append((rel, dest))
    if collisions:
        print("COLLISIONS:", collisions[:20])
        sys.exit(1)
    shutil.copytree(BASE_DIR, OUT_DIR)
    records = []
    for rel, dest in plan:
        src, out = SRC_DIR / rel, OUT_DIR / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        records.append({"dest_path": dest, "source_pack": SRC_PACK, "origin_addon": origin_addon(rel),
                        "original_path": rel, "bytes": src.stat().st_size, "sha1": sha1(src)})
    (OUT_DIR / "PROVENANCE-STRIPMINE.json").write_text(json.dumps(
        {"note": "Files moved from PW StripMine BP 1.3.13 into BP-02 1.3.206 (his ruling 2026-10-02: dissolve StripMine "
                 "into our packs, labelled by source). Identifiers unchanged. Not moved: " + ", ".join(sorted(NOT_MOVED)),
         "files": records}, indent=1))
    mp = OUT_DIR / "manifest.json"
    man = json.loads(re.sub(r"(?m)^\s*//.*$", "", mp.read_text(encoding="utf-8-sig")))
    man["header"]["version"] = [1, 3, 206]
    for mod in man["modules"]:
        mod["version"] = [1, 3, 206]
    man["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v1.3.206", man["header"]["name"])
    man["header"]["description"] = ("v1.3.206 (2026-10-02) StripMine dissolved into BP-02: every creature, spawn rule, item, "
                                    "block, loot table, recipe and function of PW StripMine BP 1.3.13 (Naturalist, Animals and "
                                    "Fauna, World Animals, WWA, yCreatures Savanna + Trial, Wildlife Sanctuary, Immersive Fauna), "
                                    "labelled by source folder; Naturalist scripts stored dormant. Includes all of v1.3.205.")
    mp.write_text(json.dumps(man, indent=2))
    main_js = OUT_DIR / "scripts/main.js"                     # version-flag law: the boot line names the build
    src_js = main_js.read_text(encoding="utf-8")
    bumped = src_js.replace('const PW_BUILD = "1.3.205";', 'const PW_BUILD = "1.3.206";')
    assert bumped != src_js, "PW_BUILD line not found"
    main_js.write_text(bumped, encoding="utf-8")
    print(json.dumps({"moved": len(records), "not_moved": skipped, "by_origin": {
        k: sum(1 for r in records if r["origin_addon"] == k) for k in sorted({r["origin_addon"] for r in records})}}, indent=1))


if __name__ == "__main__":
    main()
