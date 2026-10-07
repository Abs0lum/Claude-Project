#!/usr/bin/env python3
"""biome_fixes_206.py — SPAWN-VIABILITY-AUDIT fixes to our custom biomes (his 16:47: "also fix these now"), applied to BP-02
1.3.206 (undelivered build):
  * pw:alpine_peak replaces Frozen + Jagged Peaks completely but lacked their own tags -> + frozen_peaks, jagged_peaks
    (goats and every vanilla rule keyed on them get their habitat back).
  * pw:emerald_jungle replaces 70 % of Jungle + Bamboo Jungle but lacked 'bamboo' and 'spawns_jungle_mobs' -> added
    (pandas, parrots, ocelots and the five AnF bamboo animals).
  * pw:taiga_sparse targeted two hill biomes the game no longer places (never generated) -> retargeted to the unclaimed
    Windswept Forest (minecraft:extreme_hills_plus_trees, sparse conifers on hills), amount 0.5.
  * Wooded Badlands (mesa_plateau_stone + _mutated) was claimed by BOTH pw:amber_wooded_badlands (0.85) and
    pw:badlands_mesa (0.9) -> only amber_wooded_badlands keeps it; it also gets the vanilla Wooded Badlands tags it lacked
    (plateau, stone, spawns_mesa_mobs, spawns_warm_variant_farm_animals, surface_mineshaft) so wolves / armadillos /
    mesa mobs keep spawning there."""
import json
import re
from pathlib import Path

BIOMES = Path("/home/claude/_build/bp02-206/biomes")


def load(name):
    path = BIOMES / f"{name}.biome.json"
    return path, json.loads(re.sub(r"(?m)^\s*//.*$", "", path.read_text(encoding="utf-8-sig")))


def add_tags(doc, tags):
    current = doc["minecraft:biome"]["components"]["minecraft:tags"]["tags"]
    for tag in tags:
        if tag not in current:
            current.append(tag)


def main():
    changes = {}
    path, doc = load("alpine_peak")
    add_tags(doc, ["frozen_peaks", "jagged_peaks"])
    path.write_text(json.dumps(doc, indent=2)); changes["alpine_peak"] = "tags + frozen_peaks, jagged_peaks"
    path, doc = load("emerald_jungle")
    add_tags(doc, ["bamboo", "spawns_jungle_mobs"])
    path.write_text(json.dumps(doc, indent=2)); changes["emerald_jungle"] = "tags + bamboo, spawns_jungle_mobs"
    path, doc = load("taiga_sparse")
    reps = doc["minecraft:biome"]["components"]["minecraft:replace_biomes"]["replacements"]
    assert len(reps) == 1
    reps[0]["targets"] = ["minecraft:extreme_hills_plus_trees"]
    path.write_text(json.dumps(doc, indent=2)); changes["taiga_sparse"] = "targets -> minecraft:extreme_hills_plus_trees (0.5)"
    path, doc = load("badlands_mesa")
    for rep in doc["minecraft:biome"]["components"]["minecraft:replace_biomes"]["replacements"]:
        rep["targets"] = [t for t in rep["targets"] if t not in ("minecraft:mesa_plateau_stone", "minecraft:mesa_plateau_stone_mutated")]
    path.write_text(json.dumps(doc, indent=2)); changes["badlands_mesa"] = "no longer claims Wooded Badlands"
    path, doc = load("amber_wooded_badlands")
    add_tags(doc, ["plateau", "stone", "spawns_mesa_mobs", "spawns_warm_variant_farm_animals", "surface_mineshaft"])
    path.write_text(json.dumps(doc, indent=2)); changes["amber_wooded_badlands"] = "tags + plateau, stone, spawns_mesa_mobs, spawns_warm_variant_farm_animals, surface_mineshaft"
    print(json.dumps(changes, indent=1))


if __name__ == "__main__":
    main()
