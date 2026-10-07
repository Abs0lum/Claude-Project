#!/usr/bin/env python3
"""habitat_profiles.py — his 16:47 ruling: "assign mobs to approximate biomes; all of them. No limit on mob per biome.
Expand them to spawn in ANY biome they MIGHT be appropriate in ... I don't want to be looking for one that will never spawn."
Water classes per his SP2: ocean = deep ocean biomes · sea = shallow coastal ocean biomes · river · swamp / lagoon /
mangrove · lake/pond = still fresh water inside land biomes · beach / shore.

PROFILES: a habitat group -> the biomes of a NEW world (SPAWN-VIABILITY-AUDIT meta.biomes, 75 biomes) it covers.
The spawn-rule generator turns each set into a biome filter and proves the filter hits exactly that set."""

TEMPERATE_FOREST = {"minecraft:forest", "minecraft:flower_forest", "minecraft:birch_forest", "minecraft:birch_forest_mutated",
                    "minecraft:dappled_forest", "pw:forest_sparse", "minecraft:roofed_forest", "pw:misty_dark_forest",
                    "minecraft:cherry_grove", "pw:cherry_valley", "minecraft:pale_garden", "pw:pale_hills"}
DARK_FOREST = {"minecraft:roofed_forest", "pw:misty_dark_forest", "minecraft:pale_garden", "pw:pale_hills"}
BOREAL = {"minecraft:taiga", "minecraft:mega_taiga", "minecraft:redwood_taiga_mutated", "minecraft:cold_taiga",
          "pw:boreal_forest", "pw:old_growth_pines", "pw:taiga_sparse", "pw:snowy_taiga_sparse",
          "minecraft:extreme_hills_plus_trees"}
GRASSLAND = {"minecraft:plains", "minecraft:sunflower_plains", "minecraft:meadow", "pw:alpine_meadow"}
MOUNTAIN = {"minecraft:extreme_hills", "minecraft:extreme_hills_mutated", "minecraft:extreme_hills_plus_trees",
            "minecraft:stony_peaks", "pw:coastal_bluff", "minecraft:grove", "minecraft:meadow", "pw:alpine_meadow"}
ALPINE_SNOW = {"minecraft:frozen_peaks", "minecraft:jagged_peaks", "minecraft:snowy_slopes", "minecraft:grove",
               "pw:alpine_peak", "pw:icy_cliffs"}
TUNDRA = {"minecraft:ice_plains", "minecraft:ice_plains_spikes", "pw:icy_cliffs", "minecraft:snowy_slopes",
          "minecraft:cold_taiga", "pw:snowy_taiga_sparse", "minecraft:cold_beach"}
DESERT = {"minecraft:desert", "pw:desert_dunes"}
BADLANDS = {"minecraft:mesa", "minecraft:mesa_bryce", "minecraft:mesa_plateau_stone", "pw:badlands_mesa",
            "pw:amber_wooded_badlands"}
SAVANNA = {"minecraft:savanna", "minecraft:savanna_mutated", "minecraft:savanna_plateau", "pw:river_canyon"}
JUNGLE = {"minecraft:jungle", "minecraft:jungle_edge", "minecraft:bamboo_jungle", "pw:emerald_jungle"}
BAMBOO = {"minecraft:bamboo_jungle", "pw:emerald_jungle"}
SWAMP = {"minecraft:swampland", "pw:swamp_lagoon", "minecraft:mangrove_swamp"}
MANGROVE = {"minecraft:mangrove_swamp"}
MUSHROOM = {"minecraft:mushroom_island"}
BEACH = {"minecraft:beach", "minecraft:cold_beach", "minecraft:stone_beach", "pw:coastal_bluff"}
WARM_BEACH = {"minecraft:beach"}
CAVES = {"minecraft:lush_caves", "minecraft:dripstone_caves", "minecraft:deep_dark", "minecraft:sulfur_caves"}
LUSH_CAVES = {"minecraft:lush_caves"}
NETHER = {"minecraft:hell", "minecraft:crimson_forest", "minecraft:warped_forest", "minecraft:soulsand_valley",
          "minecraft:basalt_deltas"}
END = {"minecraft:the_end"}
# water (his SP2 classes)
SEA_WARM = {"minecraft:warm_ocean", "minecraft:lukewarm_ocean"}
SEA_TEMPERATE = {"minecraft:ocean", "minecraft:lukewarm_ocean"}
SEA_COLD = {"minecraft:cold_ocean", "minecraft:frozen_ocean"}
OCEAN_DEEP = {"minecraft:deep_ocean", "minecraft:deep_lukewarm_ocean", "minecraft:deep_cold_ocean", "minecraft:deep_frozen_ocean"}
OCEAN_DEEP_WARM = {"minecraft:deep_ocean", "minecraft:deep_lukewarm_ocean"}
OCEAN_DEEP_COLD = {"minecraft:deep_cold_ocean", "minecraft:deep_frozen_ocean"}
REEF = {"minecraft:warm_ocean", "minecraft:lukewarm_ocean"}
RIVER = {"minecraft:river", "pw:misty_river", "minecraft:frozen_river"}
WARM_RIVER = {"minecraft:river", "pw:misty_river"}
SWAMP_WATER = SWAMP
# lakes / ponds: still fresh water inside land biomes (pond features are added in the same round)
LAKE_TEMPERATE = GRASSLAND | TEMPERATE_FOREST | {"minecraft:swampland", "pw:swamp_lagoon"}
LAKE_BOREAL = BOREAL
LAKE_WARM = SAVANNA | JUNGLE | {"minecraft:mangrove_swamp"}

PROFILES = {name: value for name, value in globals().items() if name.isupper() and isinstance(value, set)}

# land profiles vs water profiles (decides population + spawns_underwater)
WATER_PROFILES = {"SEA_WARM", "SEA_TEMPERATE", "SEA_COLD", "OCEAN_DEEP", "OCEAN_DEEP_WARM", "OCEAN_DEEP_COLD", "REEF",
                  "RIVER", "WARM_RIVER", "SWAMP_WATER", "LAKE_TEMPERATE", "LAKE_BOREAL", "LAKE_WARM"}
