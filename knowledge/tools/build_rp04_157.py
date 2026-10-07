#!/usr/bin/env python3
"""build_rp04_157.py — RP-04 1.3.157 from the frozen 1.3.156 (never rebuilt): THATCH FIX + (rebuild 18:5x, 157 never
delivered) the GOLD COIN's resources (tools/coin_assets.py -> _docs/coin: the pile block's model, texture + texture set,
the coin item's icon in a new item_texture.json — the coin is block + item, kept together in the blocks pack).
Earlier text: THATCH FIX (D-C527, his 16:4x screenshots
S163858 / S164055 / S164821 / S164856: thatch roofs render as rainbow streak noise). The five thatch colour textures are
rebuilt from our own hay straw by tools/thatch_rebuild.py; sizes, alpha and texture sets unchanged."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "rp04-156", B / "rp04-157"


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    r = subprocess.run([sys.executable, "/home/claude/tools/thatch_rebuild.py", str(DST / "textures/blocks")], capture_output=True, text=True)
    print(r.stdout, r.stderr[-800:])
    if r.returncode:
        raise SystemExit("thatch rebuild failed")
    # the gold coin (his G1-G4, D-C529)
    C = Path("/home/claude/_docs/coin")
    for rel in ["textures/blocks/pw_gold_coin_pile.png", "textures/blocks/pw_gold_coin_pile_mer.png", "textures/blocks/pw_gold_coin_pile.texture_set.json",
                "textures/items/pw_gold_coin.png", "models/blocks/pw_gold_coin_pile.geo.json"]:
        (DST / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(C / rel, DST / rel)
    tt = DST / "textures/terrain_texture.json"
    d = json.loads(tt.read_text())
    if "pw_gold_coin_pile" in d["texture_data"]:
        raise SystemExit("coin texture already registered")
    d["texture_data"]["pw_gold_coin_pile"] = {"textures": "textures/blocks/pw_gold_coin_pile"}
    tt.write_text(json.dumps(d, indent=1))
    it = DST / "textures/item_texture.json"
    if it.exists():
        raise SystemExit("RP-04 has an item_texture.json already: merge by hand")
    it.write_text(json.dumps({"resource_pack_name": "pw_rp04", "texture_name": "atlas.items",
                              "texture_data": {"pw_gold_coin": {"textures": "textures/items/pw_gold_coin"}}}, indent=1))
    bj = DST / "blocks.json"
    b = json.loads(bj.read_text())
    b["pw:gold_coin_pile"] = {"sound": "metal"}
    bj.write_text(json.dumps(b, indent=1))
    lang = DST / "texts/en_US.lang"
    lang.write_text(lang.read_text().rstrip("\n") + "\ntile.pw:gold_coin_pile.name=Gold Coins\nitem.pw:gold_coin.name=Gold Coin\n")
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = [1, 3, 157]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 157]
    m["header"]["name"] = m["header"]["name"].replace("1.3.156", "1.3.157")
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.156 "):
        raise SystemExit(f"description prefix: {desc[:40]}")
    m["header"]["description"] = ("v1.3.157 (2026-10-03) THATCH FIX: thatch roofs were rainbow streak noise; rebuilt as laid straw. GOLD COIN: "
                                  "the coin pile block's model + gold texture (PBR) and the coin's icon. "
                                  "Includes all of " + desc)[:1000]
    mp.write_text(json.dumps(m, indent=1))
    print("DONE", DST, m["header"]["name"])


if __name__ == "__main__":
    main()
