#!/usr/bin/env python3
"""build_rp04_146.py — RP-04 Basic 1.3.146 = 1.3.145 (never delivered) + G3 = a (his 19:15): the vanilla grass block's side
keys `grass_block_side` and `grass_side` carry an `overlay_color` next to their variations, as Mojang's own `grass_side`
does ({"path": "textures/blocks/grass_side", "overlay_color": …}): it marks the texture's alpha as the tint mask (the 16 new
.tga sides: fringe alpha 255 = tinted, dirt alpha 0). Fallback colour #79c05a = Mojang's grass_carried (the biome colour
replaces it in the world). Everything else byte-identical to 1.3.145."""
import filecmp
import json
import re
import shutil
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST = ROOT / "_build/rp04-145", ROOT / "_build/rp04-146"


def main():
    assert not DST.exists(), "never rebuild a build dir"
    shutil.copytree(SRC, DST)
    tf = DST / "textures/terrain_texture.json"
    d = json.loads(re.sub(r"(?m)^\s*//.*$", "", tf.read_text(encoding="utf-8-sig")))
    for k in ("grass_block_side", "grass_side"):
        t = d["texture_data"][k]["textures"]
        assert isinstance(t, dict) and "variations" in t
        d["texture_data"][k]["textures"] = {"overlay_color": "#79c05a", "variations": t["variations"]}
    tf.write_text(json.dumps(d, indent=1))
    st = ROOT / "_staging/pbr/rp04/textures/terrain_texture.json"
    st.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tf, st)
    mf = DST / "manifest.json"
    m = json.loads(mf.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [1, 3, 146]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 146]
    m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v1.3.146", m["header"]["name"])
    m["header"]["description"] = m["header"]["description"].replace("v1.3.145 (2026-10-01)", "v1.3.146 (2026-10-01) grass sides: overlay_color marks the tint mask (as Mojang's grass_side). v1.3.145:", 1)
    mf.write_text(json.dumps(m, indent=1))
    diff = sorted(str(p.relative_to(DST)) for p in DST.rglob("*") if p.is_file()
                  and not filecmp.cmp(p, SRC / p.relative_to(DST), shallow=False))
    assert diff == ["manifest.json", "textures/terrain_texture.json"], diff
    print("RP-04 1.3.146 built; differs from 1.3.145 in", diff, "|", m["header"]["name"])


if __name__ == "__main__":
    main()
