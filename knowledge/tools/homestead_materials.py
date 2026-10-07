#!/usr/bin/env python3
"""homestead_materials.py — the single source of truth for the HOMESTEAD block families.

Ruling 2026-09-21 (Abs0lum): one block per material ("it's a unique block per material");
"across all build materials — not nature, except dirt variants".

Every OUTER material below resolves to a 128-px Patrix/PBR texture key that RP-04 v1.3.127
defines (census: _logs/rp04_material_keys.txt).  `side` / `top` are terrain_texture keys,
`item` is the vanilla item id used by the recipes, `name` is the display name.
1 cube = 1/16 block = 8 px at this resolution.
"""

# id -> (display name, vanilla item id, side key, top key)
OUTER = {
    # ---- planks (10) ----
    "oak_planks":        ("Oak Planks",        "minecraft:oak_planks",        "oak_planks",        "oak_planks"),
    "spruce_planks":     ("Spruce Planks",     "minecraft:spruce_planks",     "spruce_planks",     "spruce_planks"),
    "birch_planks":      ("Birch Planks",      "minecraft:birch_planks",      "birch_planks",      "birch_planks"),
    "jungle_planks":     ("Jungle Planks",     "minecraft:jungle_planks",     "jungle_planks",     "jungle_planks"),
    "acacia_planks":     ("Acacia Planks",     "minecraft:acacia_planks",     "acacia_planks",     "acacia_planks"),
    "dark_oak_planks":   ("Dark Oak Planks",   "minecraft:dark_oak_planks",   "dark_oak_planks",   "dark_oak_planks"),
    "mangrove_planks":   ("Mangrove Planks",   "minecraft:mangrove_planks",   "mangrove_planks",   "mangrove_planks"),
    "cherry_planks":     ("Cherry Planks",     "minecraft:cherry_planks",     "cherry_planks",     "cherry_planks"),
    "bamboo_planks":     ("Bamboo Planks",     "minecraft:bamboo_planks",     "bamboo_planks",     "bamboo_planks"),
    "pale_oak_planks":   ("Pale Oak Planks",   "minecraft:pale_oak_planks",   "pale_oak_planks",   "pale_oak_planks"),
    # ---- stone family (26) ----
    "stone":                    ("Stone",                    "minecraft:stone",                    "stone",                    "stone"),
    "cobblestone":              ("Cobblestone",              "minecraft:cobblestone",              "cobblestone",              "cobblestone"),
    "stone_bricks":             ("Stone Bricks",             "minecraft:stone_bricks",             "stone_bricks",             "stone_bricks"),
    "mossy_stone_bricks":       ("Mossy Stone Bricks",       "minecraft:mossy_stone_bricks",       "mossy_stone_bricks",       "mossy_stone_bricks"),
    "cracked_stone_bricks":     ("Cracked Stone Bricks",     "minecraft:cracked_stone_bricks",     "cracked_stone_bricks",     "cracked_stone_bricks"),
    "chiseled_stone_bricks":    ("Chiseled Stone Bricks",    "minecraft:chiseled_stone_bricks",    "chiseled_stone_bricks",    "chiseled_stone_bricks"),
    "smooth_stone":             ("Smooth Stone",             "minecraft:smooth_stone",             "smooth_stone",             "smooth_stone"),
    "andesite":                 ("Andesite",                 "minecraft:andesite",                 "andesite",                 "andesite"),
    "polished_andesite":        ("Polished Andesite",        "minecraft:polished_andesite",        "polished_andesite",        "polished_andesite"),
    "diorite":                  ("Diorite",                  "minecraft:diorite",                  "diorite",                  "diorite"),
    "polished_diorite":         ("Polished Diorite",         "minecraft:polished_diorite",         "polished_diorite",         "polished_diorite"),
    "granite":                  ("Granite",                  "minecraft:granite",                  "granite",                  "granite"),
    "polished_granite":         ("Polished Granite",         "minecraft:polished_granite",         "polished_granite",         "polished_granite"),
    "tuff":                     ("Tuff",                     "minecraft:tuff",                     "tuff",                     "tuff"),
    "tuff_bricks":              ("Tuff Bricks",              "minecraft:tuff_bricks",              "tuff_bricks",              "tuff_bricks"),
    "polished_tuff":            ("Polished Tuff",            "minecraft:polished_tuff",            "polished_tuff",            "polished_tuff"),
    "deepslate":                ("Deepslate",                "minecraft:deepslate",                "deepslate",                "deepslate"),
    "cobbled_deepslate":        ("Cobbled Deepslate",        "minecraft:cobbled_deepslate",        "cobbled_deepslate",        "cobbled_deepslate"),
    "deepslate_bricks":         ("Deepslate Bricks",         "minecraft:deepslate_bricks",         "deepslate_bricks",         "deepslate_bricks"),
    "deepslate_tiles":          ("Deepslate Tiles",          "minecraft:deepslate_tiles",          "deepslate_tiles",          "deepslate_tiles"),
    "polished_deepslate":       ("Polished Deepslate",       "minecraft:polished_deepslate",       "polished_deepslate",       "polished_deepslate"),
    "blackstone":               ("Blackstone",               "minecraft:blackstone",               "blackstone",               "blackstone"),
    "polished_blackstone":      ("Polished Blackstone",      "minecraft:polished_blackstone",      "polished_blackstone",      "polished_blackstone"),
    "polished_blackstone_bricks": ("Polished Blackstone Bricks", "minecraft:polished_blackstone_bricks", "polished_blackstone_bricks", "polished_blackstone_bricks"),
    "calcite":                  ("Calcite",                  "minecraft:calcite",                  "calcite",                  "calcite"),
    "dripstone_block":          ("Dripstone Block",          "minecraft:dripstone_block",          "dripstone_block",          "dripstone_block"),
    # ---- bricks / clay / adobe / misc build (15) ----
    "brick":            ("Bricks",              "minecraft:brick_block",       "brick",              "brick"),
    "mud_bricks":       ("Mud Bricks",          "minecraft:mud_bricks",        "mud_bricks",         "mud_bricks"),
    "packed_mud":       ("Packed Mud",          "minecraft:packed_mud",        "packed_mud",         "packed_mud"),
    "mud":              ("Mud",                 "minecraft:mud",               "mud",                "mud"),
    "hardened_clay":    ("Terracotta",          "minecraft:hardened_clay",     "hardened_clay",      "hardened_clay"),
    "white_terracotta": ("White Terracotta",    "minecraft:white_terracotta",  "white_terracotta",   "white_terracotta"),
    "sandstone":        ("Sandstone",           "minecraft:sandstone",         "sandstone_normal",   "sandstone_top"),
    "red_sandstone":    ("Red Sandstone",       "minecraft:red_sandstone",     "red_sandstone",      "red_sandstone"),
    "nether_brick":     ("Nether Bricks",       "minecraft:nether_brick",      "nether_brick",       "nether_brick"),
    "end_bricks":       ("End Stone Bricks",    "minecraft:end_bricks",        "end_bricks",         "end_bricks"),
    "purpur_block":     ("Purpur Block",        "minecraft:purpur_block",      "purpur_block",       "purpur_block"),
    "quartz_block":     ("Quartz Block",        "minecraft:quartz_block",      "quartz_block_side",  "quartz_block_top"),
    "white_concrete":   ("White Concrete",      "minecraft:white_concrete",    "white_concrete",     "white_concrete"),
    "copper_block":     ("Copper Block",        "minecraft:copper_block",      "copper_block",       "copper_block"),
    "clay":             ("Clay",                "minecraft:clay",              "clay",               "clay"),
    # ---- dirt variants (2) — "not nature, except dirt variants; some of my friends build adobes" ----
    "dirt":             ("Dirt",                "minecraft:dirt",              "dirt",               "dirt"),
    "coarse_dirt":      ("Coarse Dirt",         "minecraft:coarse_dirt",       "coarse_dirt",        "coarse_dirt"),
}

# The 16 interior finishes a dual wall can show on its inner face (16-value state law).
# Order = cycle order when a player taps the wall with an empty hand.
INNER16 = [
    "oak_planks", "spruce_planks", "birch_planks", "dark_oak_planks",
    "smooth_stone", "stone_bricks", "cobblestone", "brick",
    "mud_bricks", "packed_mud", "white_terracotta", "hardened_clay",
    "calcite", "polished_tuff", "quartz_block", "polished_deepslate",
]

# Rafter woods: (display name, planks item for the recipe, side key, end key)
RAFTER_WOODS = {
    "oak":    ("Oak",    "minecraft:oak_planks",    "stripped_oak_log",    "stripped_oak_log_top"),
    "spruce": ("Spruce", "minecraft:spruce_planks", "stripped_spruce_log", "stripped_spruce_log_top"),
}

# Fuel table (Abs0lum 17:12): planks 1/4 day, logs 1/2 day, coal a full day.  UNIT = 1/4 day = 6000 ticks.
FUEL_UNIT_TICKS = 6000
FUEL_UNITS = {"planks": 1, "log": 2, "coal": 4}
EMBER_FACTOR = 2            # embers last twice as long as the lit phase (one log -> 1/2 day lit -> 1 day embers)
MAX_AHEAD_UNITS = 16        # fuel stockpile cap: 4 days of burn queued ahead

assert len(INNER16) == 16 and all(i in OUTER for i in INNER16)
assert len(OUTER) == 53
