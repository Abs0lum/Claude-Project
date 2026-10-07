#!/usr/bin/env python3
"""biome_fixes_206b.py — the two remaining SPAWN-VIABILITY-AUDIT biome tag fixes (SP1 fix set, his 16:47 'yes'), BP-02 1.3.206:
  * pw:misty_river replaces 60 % of River but lacked vanilla River's 'spawns_river_mobs' -> added (river mob rules reach it).
  * pw:swamp_lagoon replaces 60 % of Swamp but lacked 'slime' + 'spawns_slimes_on_surface' -> added (swamp slimes return).
Not added (not in the approved set; logged for him): River's 'spawns_more_frequent_drowned' / 'spawns_reduced_water_ambient_mobs'."""
import json
import re
from pathlib import Path

BIOMES = Path("/home/claude/_build/bp02-206/biomes")
ADD = {"misty_river": ["spawns_river_mobs"], "swamp_lagoon": ["slime", "spawns_slimes_on_surface"]}

for name, tags in ADD.items():
    path = BIOMES / f"{name}.biome.json"
    doc = json.loads(re.sub(r"(?m)^\s*//.*$", "", path.read_text(encoding="utf-8-sig")))
    current = doc["minecraft:biome"]["components"]["minecraft:tags"]["tags"]
    added = [t for t in tags if t not in current]
    current.extend(added)
    path.write_text(json.dumps(doc, indent=2))
    print(name, "added", added, "->", current)
