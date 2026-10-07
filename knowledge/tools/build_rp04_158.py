#!/usr/bin/env python3
"""build_rp04_158.py — RP-04 1.3.158 from the frozen 1.3.157 (never rebuilt): C2.1 THE LEAD — the client entity of
pw:lead (the invisible waypoint the villagers follow; an empty geometry) so the engine renders nothing for it."""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "rp04-157", B / "rp04-158"
C2 = Path("/home/claude/_staging/c2")


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    shutil.copy(C2 / "pw_lead.entity.json", DST / "entity/pw_lead.entity.json")
    shutil.copy(C2 / "pw_empty.geo.json", DST / "models/entity/pw_empty.geo.json")
    # F4: the sewer key's icon
    shutil.copy(C2 / "keys/pw_sewer_key.png", DST / "textures/items/pw_sewer_key.png")
    it = DST / "textures/item_texture.json"
    d = json.loads(it.read_text())
    d["texture_data"]["pw_sewer_key"] = {"textures": "textures/items/pw_sewer_key"}
    it.write_text(json.dumps(d, indent=1))
    lang = DST / "texts/en_US.lang"
    lang.write_text(lang.read_text().rstrip("\n") + "\nitem.pw:sewer_key.name=Sewer Key\n")
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = [1, 3, 158]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 158]
    m["header"]["name"] = m["header"]["name"].replace("1.3.157", "1.3.158")
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.157 "):
        raise SystemExit(f"description prefix: {desc[:40]}")
    m["header"]["description"] = ("v1.3.158 (2026-10-04) THE LEAD: the invisible waypoint entity the villagers walk after (CIVITAS C2.1). THE SEWER KEY: its icon (F4). "
                                  "Includes all of " + desc)[:1000]
    mp.write_text(json.dumps(m, indent=1))
    print("DONE", DST)


if __name__ == "__main__":
    main()
