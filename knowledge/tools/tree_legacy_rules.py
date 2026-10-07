#!/usr/bin/env python3
"""tree_legacy_rules.py — tree program T2c: close the LEGACY TREE HOLE (spruce census 10-03, D-C502).
Vanilla's overworld trees are placed by feature RULES whose feature is `minecraft:legacy:<biome>_tree_feature` — engine
hardcoded generators that no JSON feature override can touch. Our pack overrides every JSON tree feature (oak / spruce /
birch / jungle / acacia / cherry / mangrove / dark oak / pale oak pools of templates) but the legacy rules kept firing in
every biome carrying a vanilla tag (taiga, forest, birch, jungle, savanna, plains, ice, extreme_hills, flower_forest,
mesa+stone) — including OUR biomes, which carry those tags. The census area c2 held 448 vanilla spruce trunks and none
of ours. This writes an override of each legacy rule (SAME identifier -> replaces vanilla's) that keeps vanilla's
biome filter and places OUR features at a Java-like density (ASSUMPTION, his witness decides the numbers):
  taiga 8 · mega taiga 6 (elder 1 : old 2 : mature 2) · forest 8 (oak 4 : birch 1) · birch 8 · flower forest 4 (oak 1 : birch 1)
  extreme hills 3 (spruce 1 : oak 1) · plains 1 @ 5 % · savanna 1 (acacia 4 : oak 1) · savanna mutated 2 · ice 1 @ 12 %
  jungle 12 + 6 bushes · jungle edge 2 · bamboo jungle 2 · mesa stone (wooded badlands) 4
Placement: x / z uniform over the chunk, y = query.heightmap (the first air cell above the ground: the template's root is
its lowest log, so it stands on the ground like a vanilla tree). The netherwart_forest rule (Nether) is left alone.
Writes into _build/bp02-208 (feature_rules/ + features/pw_mix_*.json). The census probe at c2 is the regression test."""
import json
from pathlib import Path

B = Path("/home/claude/_build/bp02-208")
FR, FE = B / "feature_rules", B / "features"


def tag(value, op="=="):
    return {"test": "has_biome_tag", "operator": op, "value": value}


def rule(ident, feature, filt, iterations, chance=None):
    dist = {"iterations": iterations, "coordinate_eval_order": "zxy",
            "x": {"distribution": "uniform", "extent": [0, 16]},
            "y": "query.heightmap(variable.worldx, variable.worldz)",
            "z": {"distribution": "uniform", "extent": [0, 16]}}
    if chance is not None:
        dist["scatter_chance"] = {"numerator": chance[0], "denominator": chance[1]}
    return {"format_version": "1.21.40", "minecraft:feature_rules": {
        "description": {"identifier": ident, "places_feature": feature},
        "conditions": {"placement_pass": "surface_pass", "minecraft:biome_filter": filt},
        "distribution": dist}}


def mix(ident, members):
    return {"format_version": "1.21.40", "minecraft:weighted_random_feature": {
        "description": {"identifier": ident}, "features": [[f, w] for f, w in members]}}


MIXES = {
    "pw:mix_forest_feature": [("minecraft:oak_tree_feature", 4), ("minecraft:birch_tree_feature", 1)],
    "pw:mix_flower_forest_feature": [("minecraft:oak_tree_feature", 1), ("minecraft:birch_tree_feature", 1)],
    "pw:mix_hills_feature": [("minecraft:spruce_tree_feature", 1), ("minecraft:oak_tree_feature", 1)],
    "pw:mix_mega_taiga_feature": [("pw:spruce_elder_with_branches_tree_feature", 1), ("pw:spruce_old_tree_feature", 2), ("pw:spruce_mature_tree_feature", 2)],
    "pw:mix_savanna_feature": [("minecraft:acacia_tree_feature", 4), ("minecraft:oak_tree_feature", 1)],
    "pw:mix_jungle_feature": [("minecraft:jungle_tree_feature", 10), ("minecraft:mega_jungle_tree_feature", 1)],
}

# (vanilla rule file / identifier, feature, filter, iterations, chance)
RULES = [
    ("taiga_surface_trees_feature", "minecraft:spruce_tree_feature", [tag("taiga"), tag("mega", "!=")], 8, None),
    ("mega_taiga_surface_trees_feature", "pw:mix_mega_taiga_feature", [tag("taiga"), tag("mega"), tag("mutated", "!=")], 6, None),
    ("redwood_taiga_mutated_surface_trees_feature", "pw:mix_mega_taiga_feature", [tag("taiga"), tag("mega"), tag("hills", "!="), tag("mutated")], 6, None),
    ("redwood_taiga_hills_mutated_surface_trees_feature", "pw:mix_mega_taiga_feature", [tag("taiga"), tag("mega"), tag("hills"), tag("mutated")], 6, None),
    ("forest_surface_trees_feature", "pw:mix_forest_feature",
     [{"any_of": [tag("forest"), tag("forest_generation")]}, tag("birch", "!="), tag("roofed", "!="), tag("extreme_hills", "!="), tag("taiga", "!=")], 8, None),
    ("birch_forest_surface_trees_feature", "minecraft:birch_tree_feature", [tag("forest"), {"all_of": [tag("birch"), tag("mutated", "!=")]}], 8, None),
    ("birch_forest_mutated_surface_trees_feature", "minecraft:birch_tree_feature", [tag("forest"), tag("birch"), tag("mutated")], 8, None),
    ("flower_forest_surface_trees_feature", "pw:mix_flower_forest_feature", [tag("flower_forest")], 4, None),
    ("extreme_hills_plus_trees_surface_trees_feature", "pw:mix_hills_feature", [{"any_of": [tag("forest"), tag("edge")]}, tag("extreme_hills")], 3, None),
    ("plains_surface_trees_feature", "minecraft:oak_tree_feature", [tag("plains")], 1, (1, 20)),
    ("savanna_surface_trees_feature", "pw:mix_savanna_feature", [tag("savanna"), tag("mutated", "!=")], 1, None),
    ("savanna_mutated_surface_trees_feature", "pw:mix_savanna_feature", [tag("savanna"), tag("mutated")], 2, None),
    ("ice_surface_trees_feature", "minecraft:spruce_tree_feature", [tag("ice"), tag("mutated", "!=")], 1, (1, 8)),
    ("jungle_surface_trees_feature", "pw:mix_jungle_feature", [tag("bamboo", "!="), tag("jungle"), tag("edge", "!=")], 12, None),
    ("jungle_edge_surface_trees_feature", "pw:mix_jungle_feature", [tag("bamboo", "!="), tag("jungle"), tag("edge")], 2, None),
    ("bamboo_jungle_surface_trees_feature", "pw:mix_jungle_feature", [tag("bamboo"), tag("jungle")], 2, None),
    ("mesa_plateau_stone_surface_trees_feature", "minecraft:oak_tree_feature", [tag("mesa"), tag("stone")], 4, None),
]
BUSH = ("pw:jungle_bushes_rule", "minecraft:jungle_bush_tree_feature", [tag("jungle"), tag("bamboo", "!=")], 6, None)


def main():
    for ident, members in MIXES.items():
        (FE / f"{ident.split(':')[1]}.json").write_text(json.dumps(mix(ident, members), indent=1))
    n = 0
    for name, feature, filt, it, chance in RULES:
        (FR / f"{name}.json").write_text(json.dumps(rule(f"minecraft:{name}", feature, filt, it, chance), indent=1))
        n += 1
    ident, feature, filt, it, chance = BUSH
    (FR / "jungle_bushes_rule.json").write_text(json.dumps(rule(ident, feature, filt, it, chance), indent=1))
    print(f"DONE {n} legacy tree rules overridden (+ jungle bushes), {len(MIXES)} mix features -> {B}")


if __name__ == "__main__":
    main()
