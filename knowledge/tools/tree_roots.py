#!/usr/bin/env python3
"""tree_roots.py — tree program T2 (SCANNER-AND-FALLING-TREES §6.1 option A; T0 probes P-1 / P-3 passed, D-C477).
For every pw trunk block (17: oak / spruce / birch / jungle young-mature-old + 5 elders) writes pw:<log>_root into
BP-02 1.3.206 blocks/roots/: the SAME geometry, textures (variant 0 bark, top 0), hardness, loot, tags and map colour as
the trunk block, so a player cannot tell it apart; it sits at the base of every structure tree and carries
  pw:tpl 0..15 + pw:tpl_hi 0..1  template index = tpl + 16*tpl_hi (engine law: a state enum holds at most 16 values)
  minecraft:cardinal_direction       'north' in the template file; worldgen / structure rotation turns it (P-3), so the
                                     tree's rotation = the turn from north
No randomize component (no pw:variant / rseed / top_variant): 32 x 4 = 128 permutations per root, 2,176 in total.
The template id is pw:trees/<log>_<nn> (e.g. pw:trees/oak_mature_07)."""
import copy
import json
import re
from pathlib import Path

BP = Path("/home/claude/_build/bp02-206")
TIERS = ["oak_young", "oak_mature", "oak_old", "oak_elder", "spruce_young", "spruce_mature", "spruce_old", "spruce_elder",
         "birch_young", "birch_mature", "birch_old", "jungle_young", "jungle_mature", "jungle_old", "jungle_elder",
         "dark_oak_elder", "pale_oak_elder"]


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def main():
    out_dir = BP / "blocks/roots"
    out_dir.mkdir(parents=True, exist_ok=True)
    for tier in TIERS:
        src = jl(BP / f"blocks/{tier}.json")
        b = src["minecraft:block"]
        comps = copy.deepcopy(b["components"])
        comps.pop("minecraft:custom_components", None)
        mats = None
        for perm in b.get("permutations", []):
            cond = perm.get("condition", "")
            if "== 0" in cond and cond.count("== 0") >= (2 if "top_variant" in cond else 1):
                mats = perm["components"].get("minecraft:material_instances")
                if mats:
                    break
        assert mats, tier
        comps["minecraft:material_instances"] = mats
        # display name: the trunk block's own (kept by deepcopy when it has one) — the root reads as the same log
        comps["tag:pw_tree_root"] = {}
        doc = {"format_version": src.get("format_version", "1.21.10"), "minecraft:block": {
            "description": {"identifier": f"pw:{tier}_root",
                            "menu_category": {"category": "none", "is_hidden_in_commands": False},
                            "states": {"pw:tpl": list(range(16)), "pw:tpl_hi": [0, 1]},
                            "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"]}}},
            "components": comps}}
        (out_dir / f"{tier}_root.json").write_text(json.dumps(doc, indent=2))
    print(f"{len(TIERS)} root blocks -> {out_dir}")


if __name__ == "__main__":
    main()
