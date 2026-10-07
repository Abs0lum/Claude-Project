#!/usr/bin/env python3
"""build_rp04_159.py — RP-04 1.3.159 from the frozen 1.3.158 (never rebuilt): program 228 RAMPS (his 12:20 / 13:40 / 13:45):
  - the 8-BLOCK RAMP (one block over 8 cells, ~7 deg): models/blocks/pw_ramps8.geo.json (8) + pw_snowcaps_ramps8.geo.json (32),
    built by tools/ramp_v8.py (whose code rebuilds the 30 shipped ramp geometries exactly — the self-check);
  - 16 NEW RAMP STONES (andesite, diorite, granite, tuff, tuff brick, calcite, blackstone, blackstone brick, cobbled
    deepslate, deepslate brick, deepslate tile, brick, mud brick, mossy cobble, mossy stone brick, stone): Patrix 26.2 128x
    variant tiles (4 variants each — his answer on the block-permutation limit) + #156 normal / MERS maps, deck / fill / cut
    textures for the 2-, 4- and 8-block families;
  - terrain_texture.json: the new keys added (no existing key changed).
Every existing file stays byte-identical (asserted)."""
import filecmp
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "rp04-158", B / "rp04-159"
ST = Path("/home/claude/_staging/ramps228/rp")
COIN_ST = Path("/home/claude/_staging/coin228/rp")              # B7 (WE10): the silver nickel's icon
SPIRAL_ST = Path("/home/claude/_staging/spiral228/rp")          # program 228: the spiral stairs (tools/spiral_pack.py --main)
EXTRA_EDITED = ("textures/item_texture.json", "texts/en_US.lang")


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")   # (159 was rebuilt only before it ever shipped: 283 MB > his 250 MB cap)
    shutil.copytree(SRC, DST)
    added = 0
    # his 250 MB rule (the 8-block ramps' 16 stones took RP-04 to 283 MB): the ramps + the spiral stairs live in RP-13
    # AbsolutRealism Architecture RP 1.0.0 (tools/build_rp13_100.py); RP-04 159 = 158 + the silver nickel
    # program 228 B7 (his 12:20 "add a SILVER NICKEL"): the item icon, its item_texture key, its name
    for f in sorted((COIN_ST / "textures/items").glob("*.png")):
        rel = f.relative_to(COIN_ST)
        assert not (DST / rel).exists(), f"would overwrite {rel}"
        shutil.copy2(f, DST / rel)
        added += 1
    it_path = DST / "textures/item_texture.json"
    it = json.loads(it_path.read_text(encoding="utf-8-sig"))
    assert "pw_silver_nickel" not in it["texture_data"]
    it["texture_data"]["pw_silver_nickel"] = {"textures": "textures/items/pw_silver_nickel"}
    it_path.write_text(json.dumps(it, indent=1, ensure_ascii=False))
    lang = DST / "texts/en_US.lang"
    txt = lang.read_text(encoding="utf-8-sig")
    assert "pw:silver_nickel" not in txt
    lang.write_text(txt.rstrip("\n") + "\nitem.pw:silver_nickel.name=Silver Nickel\n", encoding="utf-8")
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [1, 3, 159]
    m["header"]["name"] = "AbsolutRealism Basic RP v1.3.159"
    for mod in m["modules"]:
        mod["version"] = [1, 3, 159]
    m["header"]["description"] = ("v1.3.159 (2026-10-06) the silver nickel coin (the 8-block ramps and the spiral stairs are in RP-13 Architecture). Includes 1.3.158. "
                                  "Needs BP-02 1.3.228. Personal use.")
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    # every file of 158 except the two edited is byte-identical
    diff = []
    for f in SRC.rglob("*"):
        if f.is_file():
            rel = f.relative_to(SRC)
            if str(rel) in ("manifest.json",) + EXTRA_EDITED:
                continue
            if not filecmp.cmp(f, DST / rel, shallow=False):
                diff.append(str(rel))
    assert not diff, diff[:5]
    print(f"DONE {DST}: {added} files added, 158 files byte-identical")


if __name__ == "__main__":
    main()
