#!/usr/bin/env python3
"""build_rp10_143.py — RP-10 Terrain v1.3.43 for the p22 delivery (backlog: his log 4 warning
`Block name = 'minecraft:snow_layer' | Material "*" texture "snow" is an array of un-weighted textures`).
Mechanism (D-C421 note in the journal): snow_layer is drawn through a data-driven material that reads terrain key `snow`
(our blocks.json `minecraft:snow_layer -> snow_layer_single` is not used for it); `snow` = 8 weighted variations, which that
resolver flattens -> first entry drawn + the warning (L-VAR-1). Nothing of ours reads `snow` (census: 0 refs; the full snow
block reads `snow_single`). Change: terrain key `snow` -> the single path textures/blocks/snow_v0 (= exactly what the layer
draws today; the file is in this pack). Everything else byte-identical to v1.3.42."""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST = ROOT / "_build/rp10-142", ROOT / "_build/rp10-143"
VER = [1, 3, 43]


def main():
    assert not DST.exists(), "rp10-143 exists — never rebuild a build dir"
    shutil.copytree(SRC, DST)
    tf = DST / "textures/terrain_texture.json"
    raw = tf.read_text(encoding="utf-8-sig")
    d = json.loads(re.sub(r"(?m)^\s*//.*$", "", raw))
    old = d["texture_data"]["snow"]
    assert isinstance(old["textures"], dict) and old["textures"]["variations"][0]["path"] == "textures/blocks/snow_v0", old
    assert (DST / "textures/blocks/snow_v0.png").exists()
    d["texture_data"]["snow"] = {"textures": "textures/blocks/snow_v0"}
    tf.write_text(json.dumps(d, indent=1))
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = VER
    for mod in m["modules"]:
        mod["version"] = VER
    m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v1.3.43", m["header"]["name"])
    m["header"]["description"] = ("v1.3.43 (2026-10-01) SNOW LAYER WARNING: terrain key `snow` is one texture (snow_v0, what the "
                                  "snow layer already showed) — the game's snow-layer material reads that key and warned about "
                                  "its 8 variations. Includes all of v1.3.42.")
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    # proof: only the two files differ
    import filecmp
    diff = []
    for p in DST.rglob("*"):
        if p.is_file():
            q = SRC / p.relative_to(DST)
            if not q.exists() or not filecmp.cmp(p, q, shallow=False):
                diff.append(str(p.relative_to(DST)))
    assert sorted(diff) == ["manifest.json", "textures/terrain_texture.json"], diff
    n_src = sum(1 for p in SRC.rglob("*") if p.is_file())
    n_dst = sum(1 for p in DST.rglob("*") if p.is_file())
    assert n_src == n_dst, (n_src, n_dst)
    d2 = json.loads(tf.read_text())
    assert d2["texture_data"]["snow"] == {"textures": "textures/blocks/snow_v0"}
    assert {k: v for k, v in d2["texture_data"].items() if k != "snow"} == {k: v for k, v in d["texture_data"].items() if k != "snow"}
    print("RP-10 1.3.43 built:", diff, n_dst, "files")


if __name__ == "__main__":
    sys.exit(main())
