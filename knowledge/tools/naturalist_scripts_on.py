#!/usr/bin/env python3
"""naturalist_scripts_on.py — his NS1 = b (19:02 10-02): the Naturalist (sf_nba) scripts run inside BP-02 1.3.206.
* The Naturalist code imports from the scripts ROOT ("entity/Ant.js", "@minecraft/ReplaceableBlocks.js"), so its tree
  moves from scripts/stripmine/sf_nba/ to scripts/ (entity/, block/, item/, registry/, utils/, @minecraft/,
  compatability.js, info_book_page_names.json); its main.js becomes scripts/sf_nba_main.js, imported by BP-02 main.js.
  (BDS feasibility 18:56: without @minecraft/ the WHOLE BP-02 script engine crashed; with it 0 errors.)
* The 14 blocks / items whose "minecraft:custom_components" StripMine had dropped get them back, copied from the original
  Naturalist Add-On 26.1 BP (inside the archived StripMine RP 3.0.1): ant hill, chrysalis block + stages, whistle, tooth
  dagger, antivenom, stinky balloon, fat, queen ant, baby skunks (flamethrower).
* fix_info_book_entity_order.js (a developer script, never imported) moves to _docs/stripmine/."""
import json
import re
import shutil
import zipfile
from pathlib import Path

BP = Path("/home/claude/_build/bp02-206")
SRC = BP / "scripts/stripmine/sf_nba"
Z = zipfile.ZipFile("/home/claude/_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack")
PRE = "Naturalist Add-On 26.1 BP/"


def jl(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    t = re.sub(r'("(?:\\.|[^"\\])*")|//[^\n]*', lambda m: m.group(1) or "", t)
    t = re.sub(r",(\s*[}\]])", r"\1", t)
    return json.loads(t)


def main():
    scripts = BP / "scripts"
    assert SRC.exists(), "already moved?"
    for name in ["entity", "block", "item", "registry", "utils", "@minecraft", "compatability.js", "info_book_page_names.json"]:
        assert not (scripts / name).exists(), name
        shutil.move(str(SRC / name), str(scripts / name))
    shutil.move(str(SRC / "main.js"), str(scripts / "sf_nba_main.js"))
    shutil.move(str(SRC / "fix_info_book_entity_order.js"), "/home/claude/_docs/stripmine/fix_info_book_entity_order.js")
    shutil.move(str(SRC / "deno.json"), "/home/claude/_docs/stripmine/sf_nba_deno.json")
    left = [p for p in SRC.rglob("*") if p.is_file()]
    assert not left, left
    shutil.rmtree(BP / "scripts/stripmine")
    main_js = scripts / "main.js"
    s = main_js.read_text(encoding="utf-8")
    anchor = 'import "./pw_civ_clock.js";'
    assert anchor in s and "sf_nba_main" not in s
    s = s.replace(anchor, anchor + '\nimport "./sf_nba_main.js"; // v1.3.206 his NS1 = b: the Naturalist add-on scripts run (ants from hills, '
                  'variants, buckets, info book, eggs, chrysalis …)', 1)
    main_js.write_text(s, encoding="utf-8")
    # custom components back
    ours = {}
    for f in list((BP / "blocks").rglob("*.json")) + list((BP / "items").rglob("*.json")):
        try:
            d = jl(f.read_text(encoding="utf-8-sig"))
        except Exception:  # noqa: BLE001
            continue
        root = d.get("minecraft:block") or d.get("minecraft:item") if isinstance(d, dict) else None
        if root:
            ours[root["description"]["identifier"]] = (f, d)
    restored = []
    for n in Z.namelist():
        if not (n.startswith(PRE) and n.endswith(".json") and ("/blocks/" in n or "/items/" in n)):
            continue
        d = jl(Z.read(n).decode("utf-8-sig"))
        root = d.get("minecraft:block") or d.get("minecraft:item")
        if not root:
            continue
        cc = root.get("components", {}).get("minecraft:custom_components")
        if not cc:
            continue
        ident = root["description"]["identifier"]
        f, od = ours[ident]
        oroot = od.get("minecraft:block") or od.get("minecraft:item")
        if oroot.setdefault("components", {}).get("minecraft:custom_components") != cc:
            oroot["components"]["minecraft:custom_components"] = cc
            f.write_text(json.dumps(od, indent=2))
            restored.append((ident, cc))
    print("moved scripts tree; restored custom components:", len(restored))
    for r in restored:
        print("  ", r)


if __name__ == "__main__":
    main()
