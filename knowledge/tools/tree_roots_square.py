#!/usr/bin/env python3
"""tree_roots_square.py — tree program T2b (backlog "root blocks ×3", D-C501 easier-now): root blocks for the three
SQUARE species whose trunks are VANILLA logs (acacia, cherry, mangrove — tools/tree_gen_square.py SPEC). Writes
pw:acacia_root / pw:cherry_root / pw:mangrove_root into a NEW build dir (bp02-208 from bp02-207; never the frozen 207):
  * a full cube (minecraft:geometry.full_block) wearing the vanilla log's own texture keys (<sp>_log_side, <sp>_log_top —
    the keys vanilla's blocks.json maps for that log, so whichever pack retextures the log retextures the root too),
  * the same hardness / resistance / flammability / sound / loot (the vanilla log item) as the log,
  * the T2 states pw:tpl 0..15 + pw:tpl_hi 0..1 and the cardinal_direction trait (template index + rotation),
  * tag:pw_tree_root (+ log / wood tags).
Then: tree_gen_square.py SPEC gets the root ids (the 96 acacia / cherry / mangrove templates are regenerated with the
root at their base by tools/tree_gen_square.py, installed by the 208 build), and pw_fell_rules.registerRootLogs learns
the vanilla-log species' roots (VANILLA_ROOTS). Prints a checklist; the BDS load gate is the proof afterwards."""
import json
import shutil
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-207", B / "bp02-208"
SPECIES = {  # species: (vanilla log, side key, top key, sound, map colour)
    "acacia": ("minecraft:acacia_log", "acacia_log_side", "acacia_log_top", "wood", "#6f6a5f"),
    "cherry": ("minecraft:cherry_log", "cherry_log_side", "cherry_log_top", "cherry_wood", "#3a2a2e"),
    "mangrove": ("minecraft:mangrove_log", "mangrove_log_side", "mangrove_log_top", "wood", "#5a3a2a"),
}


def root_block(sp, log, side, top, colour):
    return {
        "format_version": "1.21.10",
        "minecraft:block": {
            "description": {
                "identifier": f"pw:{sp}_root",
                "menu_category": {"category": "none", "is_hidden_in_commands": False},
                "states": {"pw:tpl": list(range(16)), "pw:tpl_hi": [0, 1]},
                "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"]}},
            },
            "components": {
                "minecraft:geometry": "minecraft:geometry.full_block",
                "minecraft:destructible_by_mining": {"seconds_to_destroy": 2.0},
                "minecraft:destructible_by_explosion": {"explosion_resistance": 2.5},
                "minecraft:flammable": {"catch_chance_modifier": 5, "destroy_chance_modifier": 5},
                "minecraft:light_dampening": 15,
                "minecraft:map_color": colour,
                "minecraft:loot": f"loot_tables/blocks/{sp}_log.json",
                "minecraft:collision_box": {"origin": [-8, 0, -8], "size": [16, 16, 16]},
                "minecraft:selection_box": {"origin": [-8, 0, -8], "size": [16, 16, 16]},
                "tag:log": {}, "tag:wood": {}, "tag:pw_tree_root": {},
                "minecraft:material_instances": {
                    "*": {"texture": side, "render_method": "opaque"},
                    "up": {"texture": top, "render_method": "opaque"},
                    "down": {"texture": top, "render_method": "opaque"},
                },
            },
        },
    }


def loot(log):
    return {"pools": [{"rolls": 1, "entries": [{"type": "item", "name": log, "weight": 1}]}]}


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    for sp, (log, side, top, sound, colour) in SPECIES.items():
        (DST / "blocks/roots" / f"{sp}_root.json").write_text(json.dumps(root_block(sp, log, side, top, colour), indent=1))
        lt = DST / "loot_tables/blocks" / f"{sp}_log.json"
        if not lt.exists():
            lt.write_text(json.dumps(loot(log), indent=1))
        print(f"DONE pw:{sp}_root -> blocks/roots/{sp}_root.json (loot {lt.name}, keys {side} / {top})")
    # the RP side: the three roots need a blocks.json sound entry in RP-01 (next RP-01 build) — noted, not done here
    print("NOTE RP-01: add pw:acacia_root / pw:cherry_root (cherry_wood) / pw:mangrove_root to blocks.json sounds in the next RP-01 build")


if __name__ == "__main__":
    main()
