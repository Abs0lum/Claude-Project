#!/usr/bin/env python3
"""tree_stumps.py — his F9 = yes: pw:<tier>_stump blocks (BP-02 1.3.206 blocks/stumps/) + their cut-face textures
(RP-01 1.3.117 textures/blocks/stumps/, terrain keys pw_<species>_<age>_stump_top). A stump looks like its trunk
(same geometry, bark variant 0) with the age's growth-ring face on top (tools/stump_textures.py). No states (1
permutation each); drops the trunk's vanilla log; never part of a fall (it is not in any species' log list)."""
import copy
import json
import re
import shutil
from pathlib import Path

BP = Path("/home/claude/_build/bp02-206")
RP = Path("/home/claude/_build/rp01-117")
STAGE = Path("/home/claude/_staging/stumps")
TIERS = ["oak_young", "oak_mature", "oak_old", "oak_elder", "spruce_young", "spruce_mature", "spruce_old", "spruce_elder",
         "birch_young", "birch_mature", "birch_old", "jungle_young", "jungle_mature", "jungle_old", "jungle_elder",
         "dark_oak_elder", "pale_oak_elder"]


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def main():
    root = jl(BP / "blocks/roots/oak_young_root.json")                 # roots already carry the variant-0 materials
    (BP / "blocks/stumps").mkdir(parents=True, exist_ok=True)
    tex_dir = RP / "textures/blocks/stumps"
    tex_dir.mkdir(parents=True, exist_ok=True)
    tt_path = RP / "textures/terrain_texture.json"
    tt = jl(tt_path)
    added = 0
    for tier in TIERS:
        sp, age = tier.rsplit("_", 1)
        src = jl(BP / f"blocks/roots/{tier}_root.json")["minecraft:block"]
        comps = copy.deepcopy(src["components"])
        comps.pop("tag:pw_tree_root", None)
        key = f"pw_{sp}_{age}_stump_top"
        mats = comps["minecraft:material_instances"]
        top_slot = "log_top" if "log_top" in mats else "up"
        base_render = mats.get("*", {}).get("render_method", "opaque")
        mats[top_slot] = {"texture": key, "render_method": base_render}
        comps["tag:pw_stump"] = {}
        doc = {"format_version": "1.21.10", "minecraft:block": {
            "description": {"identifier": f"pw:{tier}_stump", "menu_category": {"category": "none"}},
            "components": comps}}
        (BP / f"blocks/stumps/{tier}_stump.json").write_text(json.dumps(doc, indent=2))
        for f in STAGE.glob(f"{key}*"):
            shutil.copy(f, tex_dir / f.name)
        tt["texture_data"][key] = {"textures": f"textures/blocks/stumps/{key}"}
        added += 1
    tt_path.write_text(json.dumps(tt, indent=1))
    print(f"{added} stump blocks + terrain keys; textures in {tex_dir}")


if __name__ == "__main__":
    main()
