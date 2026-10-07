# VANILLA-ASSET LIST — 2026-09-22 (after RP-04 v1.3.136 / RP-03 v1.3.59 / RP-01 v1.3.104 / RP-05 v1.3.48)

**What this is.** Every block-texture slot that still resolves to Mojang's own 16x texture with the shipped stack installed, grouped by material family, with what to source (ambientCG / Poly Haven — CC0 only, per the production-source law) or how to derive it from art we already own. Ruling 17:08 CT: "keep them all but make a list of everything that is vanilla for me to find HD assets".

**Scope (P11 premise audit).** CENSUSED: every entry of the effective blocks.json (1,383 vanilla-registered block ids) through the live stack order, terrain_texture + flipbooks, all 13 RPs + vanilla 1.26.50.4. EXCLUSION-VERIFIED (out of scope of this list, stated so you know where the edges are): item icons (`textures/items`, RP-08's domain — no item census has been run), mob textures (RP-06/07 carry their own converted models), UI, particles, environment/sky (RP-02's domain; three housekeeping notes below).

**Census now:** ALL-OURS 1282 · MIXED 16 · ALL-VANILLA 85 (was 1105 / 21 / 257 before phase 1b). Vanilla-resolved slots: 193 → **65 that a modern world can show** (below) + 128 that belong to deprecated / technical block ids (listed at the end, no action).

## How to read a row
`slot` = the texture path under textures/blocks/ the engine looks up — that is the file NAME to save the HD asset as: into RP-03 when it gets a texture set + MER (the PBR pack), into RP-04 when it is colour-only · `vanilla` = Mojang's size · `blocks` = which block ids show it · then what to source and where. Effort S = one sitting, M = a small build with a preview sheet.

## TIER 1 — seen in normal play (source these first)

### Campfire logs (author from our hearth logs)  ·  effort S/M
Bedrock's campfire uses its own log unwrap (campfire_log 16x16; campfire_log_lit / soul_campfire_log_lit = 4-frame 16x64 strips). Patrix has none. Author from pw_hearth_log_{cold,lit} + pw_hearth_log_end_* (already Patrix oak + magma glow) laid onto the vanilla unwrap; the soul variant = the same with the blue soul-fire glow.
**Source / search terms:** — (no photo source needed; our hearth stages are the source)

| slot | vanilla | blocks |
|---|---|---|
| `campfire_log` | 16x16 | campfire, soul_campfire |
| `campfire_log_lit` | 16x64 | campfire |
| `soul_campfire_log_lit` | 16x64 | soul_campfire |

### Grindstone  ·  effort S
The village smith block; Patrix never made it. round = the stone wheel face, side = the wheel's rim, pivot = the dark iron axle plate.
**Source / search terms:** ambientCG: Rock022 / Rock030 (coarse grey stone for the wheel), Metal032 / Metal038 (dark cast iron pivot); Poly Haven: 'rough_concrete', 'rock_face', 'metal_plate' — or derive: wheel from Patrix stone.png, pivot from Patrix iron_block, side from Patrix oak planks end grain

| slot | vanilla | blocks |
|---|---|---|
| `grindstone_pivot` | 16x16 | grindstone |
| `grindstone_round` | 16x16 | grindstone |
| `grindstone_side` | 16x16 | grindstone |

### Composter contents  ·  effort S
Two fill-level textures (alpha = the layer edge). Patrix has the composter box (bottom/side/top, now ours) but not the compost.
**Source / search terms:** ambientCG: Ground037 / Ground054 (mulch), Ground033 (dark soil); Poly Haven: 'forest_leaves_02', 'brown_mud_leaves_01', 'mulch' — compost_ready = the same with a bone-meal white dusting

| slot | vanilla | blocks |
|---|---|---|
| `compost` | 16x16 | composter |
| `compost_ready` | 16x16 | composter |

### Pumpkin / melon stems  ·  effort S
Greyscale, biome-tinted crop stems (alpha silhouette). Patrix ships only extra/stem_extra.png (3 KB) — pull it and check; otherwise author: a curled vine on alpha at 128x, greyscale so the engine tint works.
**Source / search terms:** author (greyscale vine); reference photo only: Poly Haven 'vine', ambientCG 'Bark' for the stalk grain

| slot | vanilla | blocks |
|---|---|---|
| `pumpkin_stem_connected` | 16x16 | pumpkin_stem |
| `pumpkin_stem_disconnected` | 16x16 | pumpkin_stem |
| `melon_stem_connected` | 16x16 | melon_stem |
| `melon_stem_disconnected` | 16x16 | melon_stem |

### Redstone dust  ·  effort S
Greyscale alpha masks tinted by power (white = full). Patrix has only redstone_dust_dot + overlay (Java draws lines from line0/line1 which Patrix left vanilla). Author: HD powder-trail masks, 128x, greyscale on alpha — or leave at 16x (thin trails read fine).
**Source / search terms:** author (procedural powder trail)

| slot | vanilla | blocks |
|---|---|---|
| `redstone_dust_cross` | 16x16 | redstone_wire |
| `redstone_dust_line` | 16x16 | redstone_wire |

### Poplar wood set (1.26 new wood)  ·  effort M
A whole wood family with no Patrix art (post-dates the 128x basic zip). Bark is pale grey-green and smooth; planks pale; leaves come in orange/red/yellow autumn tints (+ _opaque = leaves with the alpha filled, our fill rule from phase 1). Build it like our other woods: bark/planks from CC0 photos, door/trapdoor/shelf cut from the planks with the vanilla alpha layouts, leaves = Patrix birch leaves hue-shifted, sapling = Patrix birch sapling recoloured.
**Source / search terms:** ambientCG: Bark006 / Bark012 (smooth pale bark), Wood051 / Wood066 (pale planks), Planks023; Poly Haven: 'bark_willow_02', 'wood_planks_pale', 'birch_bark' (visual target only)

| slot | vanilla | blocks |
|---|---|---|
| `poplar_log_side` | 16x16 | poplar_log, poplar_wood |
| `poplar_log_top` | 16x16 | poplar_log |
| `stripped_poplar_log_side` | 16x16 | stripped_poplar_log, stripped_poplar_wood |
| `stripped_poplar_log_top` | 16x16 | stripped_poplar_log |
| `poplar_planks` | 16x16 | poplar_button, poplar_double_slab, poplar_fence, poplar_fence_gate, poplar_hanging_sign, poplar_planks, poplar |
| `poplar_door_bottom` | 16x16 | poplar_door |
| `poplar_door_top` | 16x16 | poplar_door |
| `poplar_trapdoor` | 16x16 | poplar_trapdoor |
| `poplar_sapling` | 16x16 | poplar_sapling |
| `poplar_shelf` | 32x32 | poplar_shelf |
| `orange_poplar_leaves` | 16x16 | orange_poplar_leaves |
| `orange_poplar_leaves_opaque` | 16x16 | orange_poplar_leaves |
| `red_poplar_leaves` | 16x16 | red_poplar_leaves |
| `red_poplar_leaves_opaque` | 16x16 | red_poplar_leaves |
| `yellow_poplar_leaves` | 16x16 | yellow_poplar_leaves |
| `yellow_poplar_leaves_opaque` | 16x16 | yellow_poplar_leaves |

## TIER 2 — rare / new 1.26 content / derive-from-ours

### Cinnabar family (1.26 new stone)  ·  effort M
Red-ochre stone (+ chiseled / polished / bricks; slabs, stairs and walls reuse these four).
**Source / search terms:** ambientCG: Rock035 / Rock037 (red rock), Bricks076 (for the bricks); Poly Haven: 'red_laterite_soil_stones', 'red_sandstone', 'brick_wall_006' — polished = the base blurred/flattened, chiseled = the base + a carved emblem

| slot | vanilla | blocks |
|---|---|---|
| `cinnabar` | 16x16 | cinnabar, cinnabar_double_slab, cinnabar_slab, cinnabar_stairs, cinnabar_wall |
| `chiseled_cinnabar` | 16x16 | chiseled_cinnabar |
| `polished_cinnabar` | 16x16 | polished_cinnabar, polished_cinnabar_double_slab, polished_cinnabar_slab, polished_cinnabar_stairs, polished_c |
| `cinnabar_bricks` | 16x16 | cinnabar_brick_double_slab, cinnabar_brick_slab, cinnabar_brick_stairs, cinnabar_brick_wall, cinnabar_bricks |

### Sulfur family (1.26 new stone) + spikes  ·  effort M
Yellow crystalline stone; the 10 spike textures are dripstone-style alpha silhouettes — author the block first, then cut the spikes by multiplying the block texture with the vanilla spike alpha masks (scaled x8), exactly how we would do the dripstone segments.
**Source / search terms:** ambientCG: Rock050 / Rock057 (yellow-ochre rock), Crystal001? (for potent_sulfur), Bricks058; Poly Haven: 'yellow_ochre rock', 'sulphur' has no direct match — 'sandstone_cracks', 'rock_boulder_dry' recoloured

| slot | vanilla | blocks |
|---|---|---|
| `sulfur` | 16x16 | sulfur, sulfur_double_slab, sulfur_slab, sulfur_stairs, sulfur_wall |
| `chiseled_sulfur` | 16x16 | chiseled_sulfur |
| `polished_sulfur` | 16x16 | polished_sulfur, polished_sulfur_double_slab, polished_sulfur_slab, polished_sulfur_stairs, polished_sulfur_wa |
| `sulfur_bricks` | 16x16 | sulfur_brick_double_slab, sulfur_brick_slab, sulfur_brick_stairs, sulfur_brick_wall, sulfur_bricks |
| `potent_sulfur` | 16x16 | potent_sulfur |
| `sulfur_spike_up_base` | 16x16 | sulfur_spike |
| `sulfur_spike_up_frustum` | 16x16 | sulfur_spike |
| `sulfur_spike_up_middle` | 16x16 | sulfur_spike |
| `sulfur_spike_up_tip` | 16x16 | sulfur_spike |
| `sulfur_spike_up_tip_merge` | 16x16 | sulfur_spike |
| `sulfur_spike_down_base` | 16x16 | sulfur_spike |
| `sulfur_spike_down_frustum` | 16x16 | sulfur_spike |
| `sulfur_spike_down_middle` | 16x16 | sulfur_spike |
| `sulfur_spike_down_tip` | 16x16 | sulfur_spike |
| `sulfur_spike_down_tip_merge` | 16x16 | sulfur_spike |

### Pointed dripstone middle segments  ·  effort S
Base and tip are Patrix (ours); the three middle segments are not. A stalactite therefore alternates HD/16x along its length. Derive: Patrix pointed_dripstone_*_base texture x vanilla frustum/middle/merge alpha masks (scaled x8) — no photo needed.
**Source / search terms:** derive from RP-04 pointed_dripstone_{up,down}_base

| slot | vanilla | blocks |
|---|---|---|
| `pointed_dripstone_down_frustum` | 16x16 | pointed_dripstone |
| `pointed_dripstone_down_middle` | 16x16 | pointed_dripstone |
| `pointed_dripstone_down_merge` | 16x16 | pointed_dripstone |
| `pointed_dripstone_up_frustum` | 16x16 | pointed_dripstone |
| `pointed_dripstone_up_middle` | 16x16 | pointed_dripstone |
| `pointed_dripstone_up_merge` | 16x16 | pointed_dripstone |

### Sculk catalyst bloom faces  ·  effort S
The catalyst's brief bloom state (top_bloom is a 16x128 8-frame strip). Derive: Patrix sculk_catalyst_side/top with the cyan speckles brightened + an emissive MER; the strip = 8 copies with a pulsing brightness ramp.
**Source / search terms:** derive from RP-03 sculk_catalyst_side / _top

| slot | vanilla | blocks |
|---|---|---|
| `sculk_catalyst_side_bloom` | 16x128 | sculk_catalyst |
| `sculk_catalyst_top_bloom` | 16x128 | sculk_catalyst |

### Respawn anchor underside  ·  effort S
Java draws a crying-obsidian-like bottom. Patrix has crying_obsidian (RP-03) — alias it, or the anchor's side0 texture.
**Source / search terms:** alias RP-03 crying_obsidian

| slot | vanilla | blocks |
|---|---|---|
| `respawn_anchor_bottom` | 16x16 | respawn_anchor |

### Bell body faces (block part)  ·  effort S/M
Vanilla's bell_top/side/bottom are the GOLD bell faces drawn by the block model (25 % alpha coverage each), separate from the entity bell.png we already ported. Derive from the Patrix bell_body regions (gold) into the vanilla alpha layouts, or leave — the ringing bell entity is HD already.
**Source / search terms:** derive from RP-04 entity/bell/bell.png

| slot | vanilla | blocks |
|---|---|---|
| `bell_top` | 16x16 | bell |
| `bell_side` | 16x16 | bell |
| `bell_bottom` | 16x16 | bell |

### Bamboo single leaf  ·  effort S
One leaf sprite (5 % alpha coverage). Crop a single leaf out of Patrix bamboo_small_leaf (RP-05).
**Source / search terms:** derive from RP-05 bamboo_small_leaf

| slot | vanilla | blocks |
|---|---|---|
| `bamboo_singleleaf` | 16x16 | bamboo |

### Potted flowering azalea (plant cross)  ·  effort S
The side/top faces are aliased already; the flower cross needs Patrix azalea_plant + flowering_azalea flower sprites overlaid.
**Source / search terms:** derive from RP-05 azalea_plant + flowering_azalea_side

| slot | vanilla | blocks |
|---|---|---|
| `potted_flowering_azalea_bush_plant` | 16x16 | flowering_azalea |

### Resin clump (pale garden)  ·  effort S
Amber blobs on alpha (11 % coverage). Derive: Patrix resin_block (in the zip: resin_block.png / resin_bricks.png) cut into the vanilla clump alpha mask.
**Source / search terms:** pull Patrix resin_block + vanilla mask; photo reference: Poly Haven 'amber', ambientCG 'Resin'? (none — use the Patrix block)

| slot | vanilla | blocks |
|---|---|---|
| `resin_clump` | 16x16 | resin_clump |

### Golden dandelion (1.26 flower)  ·  effort S
Recolour of the dandelion. Derive: Patrix dandelion (RP-01 flower_dandelion) with the petals shifted to gold/orange.
**Source / search terms:** derive from RP-01 flower_dandelion

| slot | vanilla | blocks |
|---|---|---|
| `golden_dandelion` | 16x16 | golden_dandelion |

## Also worth doing — not block slots, but the same kind of gap

- **Fire block (fire_0 / fire_1 / soul_fire_0 / soul_fire_1)** — RP-10 owns these in the stack with four 8x256 variations (32 frames of 8x8: the pale blocky flame you saw on the first hearth). Patrix has full 128x3840 30-frame strips for all four (fire_0 112 KB, fire_1 97 KB, soul_fire_0 111 KB — already pulled for the soul campfire —, soul_fire_1 60 KB). RP-10 build, S.
- **Paintings** — Bedrock keeps the 26 classic paintings in one atlas (`textures/painting/kz.png`, 16 px per cell) and the 1.21 ones as single files (backyard, baroque, bouquet, cavebird, changing, cotan, dennis, endboss, fern, finding, humble, lowmist, meditative, orb, owlemons, passage, pond, prairie_ride, sunflowers, tides, unpacked). Patrix ships the 26 classics as single Java files (alban … wither) → compose an HD kz.png (2048x2048). The 1.21 paintings have no Patrix art. RP-04, S/M.
- **Block-breaking cracks** — RP-02 ships 64x64 destroy stages; Patrix's 128x ones (hard-edged alpha) are sitting in RP-03 under textures/blocks/ (kept as UNIQUE); moving them to textures/environment/ would make them live. Aesthetic call — preview first.
- **Entity PBR** — vanilla 1.26 ships `_mers.tga` + texture sets for entity textures; our chests/beds/signs/boats/banners/shulkers are colour-only. Feed for RP-03 from the Patrix `_n/_s` (LabPBR → MER, #156). M.

## Housekeeping found on the way (no action taken — your call)
- RP-04 still ships `textures/environment/rain.png` (128x128): the engine reads `weather.png` now (RP-02 provides a 1024x1024 one) — the rain file is dead by rename; kept, listed.
- RP-04 ships `environment/sun.png`, `moon_phases.png`, `clouds.png` (a 70-byte blank = clouds off) and `end_flash.png` ABOVE RP-02's versions in the world order (RP-04 > RP-03 > RP-02); they differ from RP-02's. Whatever you see in the sky is RP-04's. Intended?
- RP-04 `environment/celestial/moon/*` (8 phases, 2048x2048) + `celestial/sun.png` are not paths this engine version reads (kept — unknown provenance, not re-pullable).
- RP-03 `stripped_crimson_stem` texture set references the warped normal (pre-existing quirk, backlog).

## Deprecated / technical block ids still on vanilla textures — NO ACTION
These block ids cannot be placed in a modern world (flattened to per-colour ids that are already ours: wool → white_wool…, concrete, stained glass, terracotta, shulker boxes, coral, saplings, the legacy stonecutter) or are creative/technical (command blocks, barrier, border, allow/deny, camera, bubble column, reactor core, structure void, end portal/gateway, missing tile).

`barrier`, `border`, `bubble_column_down_top_a`, `bubble_column_down_top_b`, `bubble_column_down_top_c`, `bubble_column_down_top_d`, `bubble_column_inner_a`, `bubble_column_inner_b`, `bubble_column_outer_a`, `bubble_column_outer_b`, `bubble_column_outer_c`, `bubble_column_outer_d`, `bubble_column_outer_e`, `bubble_column_outer_f`, `bubble_column_outer_g`, `bubble_column_outer_h`, `bubble_column_up_top_a`, `bubble_column_up_top_b`, `bubble_column_up_top_c`, `bubble_column_up_top_d`, `build_allow`, `build_deny`, `camera_back`, `camera_front`, `camera_side`, `camera_top`, `chain_command_block_back_mipmap`, `chain_command_block_conditional_mipmap`, `chain_command_block_front_mipmap`, `chain_command_block_side_mipmap`, `command_block_back_mipmap`, `command_block_conditional_mipmap`, `command_block_front_mipmap`, `command_block_side_mipmap`, `concrete_black`, `concrete_blue`, `concrete_brown`, `concrete_cyan`, `concrete_gray`, `concrete_green`, `concrete_light_blue`, `concrete_lime`, `concrete_magenta`, `concrete_orange`, `concrete_pink`, `concrete_powder_black`, `concrete_powder_blue`, `concrete_powder_brown`, `concrete_powder_cyan`, `concrete_powder_gray`, `concrete_powder_green`, `concrete_powder_light_blue`, `concrete_powder_lime`, `concrete_powder_magenta`, `concrete_powder_orange`, `concrete_powder_pink`, `concrete_powder_purple`, `concrete_powder_red`, `concrete_powder_silver`, `concrete_powder_white`, `concrete_powder_yellow`, `concrete_purple`, `concrete_red`, `concrete_silver`, `concrete_white`, `concrete_yellow`, `coral_blue`, `coral_blue_dead`, `coral_fan_blue`, `coral_fan_blue_dead`, `coral_fan_pink_dead`, `coral_fan_purple`, `coral_fan_purple_dead`, `coral_fan_red`, `coral_fan_red_dead`, `coral_fan_yellow`, `coral_fan_yellow_dead`, `coral_pink_dead`, `coral_plant_blue`, `coral_plant_blue_dead`, `coral_plant_pink_dead`, `coral_plant_purple`, `coral_plant_purple_dead`, `coral_plant_red`, `coral_plant_red_dead`, `coral_plant_yellow`, `coral_plant_yellow_dead`, `coral_purple`, `coral_purple_dead`, `coral_red`, `coral_red_dead`, `coral_yellow`, `coral_yellow_dead`, `end_gateway`, `end_portal`, `glowing_obsidian`, `hardened_clay_stained_black`, `hardened_clay_stained_blue`, `hardened_clay_stained_brown`, `hardened_clay_stained_cyan`, `hardened_clay_stained_gray`, `hardened_clay_stained_green`, `hardened_clay_stained_light_blue`, `hardened_clay_stained_lime`, `hardened_clay_stained_magenta`, `hardened_clay_stained_orange`, `hardened_clay_stained_pink`, `hardened_clay_stained_purple`, `hardened_clay_stained_red`, `hardened_clay_stained_silver`, `hardened_clay_stained_white`, `hardened_clay_stained_yellow`, `missing_tile`, `reactor_core_stage_0`, `reactor_core_stage_1`, `reactor_core_stage_2`, `repeating_command_block_back_mipmap`, `repeating_command_block_conditional_mipmap`, `repeating_command_block_front_mipmap`, `repeating_command_block_side_mipmap`, `sapling_acacia`, `sapling_birch`, `sapling_jungle`, `sapling_oak`, `sapling_roofed_oak`, `sapling_spruce`, `stonecutter_bottom`, `structure_void`

## Authoring material kept by the purge (unreferenced, listed so you know it is there)
**RP-04** (118 files incl. companions, 6.2 MB): blocks/acacia_log_top, blocks/acacia_planks, blocks/andesite_2, blocks/andesite_3, blocks/birch_planks, blocks/blue_terracotta, blocks/brown_terracotta, blocks/chain, blocks/cyan_terracotta, blocks/dark_oak_planks, blocks/deepslate, blocks/deepslate_2, blocks/deepslate_3, blocks/deepslate_top_1, blocks/deepslate_top_2, blocks/deepslate_top_3, blocks/diorite, blocks/dirt_path_side, blocks/dirt_path_top, blocks/door_bamboo_lower, blocks/door_bamboo_upper, blocks/door_cherry_lower, blocks/door_cherry_upper, blocks/door_mangrove_lower, blocks/door_mangrove_upper, blocks/farmland, blocks/farmland_moist, blocks/granite_2, blocks/granite_3, blocks/grass_block_top_1, blocks/grass_block_top_2, blocks/grass_block_top_3, blocks/gray_terracotta, blocks/green_terracotta, blocks/jungle_planks, blocks/light_blue_terracotta, blocks/light_gray_terracotta, blocks/lime_terracotta, blocks/magenta_terracotta, blocks/mossy_cobblestone, blocks/orange_terracotta, blocks/pink_terracotta, blocks/purple_terracotta, blocks/red_terracotta, blocks/spruce_planks_0, blocks/spruce_planks_1, blocks/spruce_planks_2, blocks/spruce_planks_3, blocks/stone_2, blocks/stone_3, blocks/stone_bricks, blocks/terracotta, blocks/torch_flame, blocks/waxed_copper_lantern, blocks/waxed_copper_ore, blocks/waxed_exposed_copper_lantern, blocks/waxed_oxidized_copper_lantern, blocks/waxed_weathered_copper_lantern, blocks/yellow_terracotta, entity/bed/light_gray, entity/chest/christmas, entity/chest/christmas_left, entity/chest/christmas_right, entity/chest/copper, environment/celestial/moon/first_quarter, environment/celestial/moon/full_moon, environment/celestial/moon/new_moon, environment/celestial/moon/third_quarter, environment/celestial/moon/waning_crescent, environment/celestial/moon/waning_gibbous, environment/celestial/moon/waxing_crescent, environment/celestial/moon/waxing_gibbous, environment/celestial/sun, environment/rain

**RP-03** (178 files incl. companions, 4.2 MB): blocks/acacia_log_top, blocks/acacia_planks, blocks/andesite_2, blocks/andesite_3, blocks/bamboo_large_leaves, blocks/bamboo_stage0, blocks/big_dripleaf_tip, blocks/birch_planks, blocks/carrots_stage0, blocks/carrots_stage1, blocks/carrots_stage2, blocks/carved_pumpkin, blocks/carved_pumpkin2, blocks/carved_pumpkin3, blocks/carved_pumpkin4, blocks/cave_vines_lit, blocks/cave_vines_plant_lit, blocks/dark_oak_leaves, blocks/dark_oak_planks, blocks/deepslate, blocks/deepslate_2, blocks/deepslate_3, blocks/deepslate_top_1, blocks/deepslate_top_2, blocks/deepslate_top_3, blocks/destroy_stage_0, blocks/destroy_stage_1, blocks/destroy_stage_2, blocks/destroy_stage_3, blocks/destroy_stage_4, blocks/destroy_stage_5, blocks/destroy_stage_6, blocks/destroy_stage_7, blocks/destroy_stage_8, blocks/destroy_stage_9, blocks/diorite, blocks/end_portal_frame_eye, blocks/granite_2, blocks/granite_3, blocks/grass_block_side_overlay, blocks/grass_block_top_1, blocks/grass_block_top_2, blocks/grass_block_top_3, blocks/jack_o_lantern2, blocks/jack_o_lantern3, blocks/jack_o_lantern4, blocks/jungle_planks, blocks/lilac_bottom, blocks/lilac_top, blocks/mossy_cobblestone, blocks/oak_leaves, blocks/open_eyeblossom, blocks/open_eyeblossom_emissive, blocks/pale_moss_carpet_side_small, blocks/peony_bottom, blocks/peony_top, blocks/pumpkin_side2, blocks/pumpkin_side3, blocks/pumpkin_side4, blocks/rose_bush_bottom, blocks/spruce_leaves, blocks/spruce_planks_0, blocks/spruce_planks_1, blocks/spruce_planks_2, blocks/spruce_planks_3, blocks/stone_2, blocks/stone_3, blocks/stone_bricks, blocks/sunflower_back, blocks/sunflower_bottom, blocks/sunflower_front, blocks/sunflower_top, blocks/test_block_accept, blocks/test_block_fail, blocks/test_block_log, blocks/test_block_start, blocks/test_instance_block, blocks/warped_nylium

**RP-01** (72 files incl. companions, 1.3 MB): blocks/acacia_sapling_v0, blocks/acacia_sapling_v1, blocks/acacia_sapling_v2, blocks/azure_bluet_v0, blocks/azure_bluet_v1, blocks/azure_bluet_v2, blocks/birch_sapling_v0, blocks/birch_sapling_v1, blocks/birch_sapling_v2, blocks/cactus_bottom_v0, blocks/cactus_bottom_v1, blocks/cactus_bottom_v2, blocks/cactus_flower_v0, blocks/cactus_flower_v1, blocks/cactus_flower_v2, blocks/cherry_sapling_v0, blocks/cherry_sapling_v1, blocks/cherry_sapling_v2, blocks/cornflower_v0, blocks/cornflower_v1, blocks/cornflower_v2, blocks/dark_oak_sapling_v0, blocks/dark_oak_sapling_v1, blocks/dark_oak_sapling_v2, blocks/deadbush_v0, blocks/deadbush_v1, blocks/deadbush_v2, blocks/jungle_sapling_v0, blocks/jungle_sapling_v1, blocks/jungle_sapling_v2, blocks/lily_of_the_valley_v0, blocks/lily_of_the_valley_v1, blocks/lily_of_the_valley_v2, blocks/oak_sapling_v0, blocks/oak_sapling_v1, blocks/oak_sapling_v2, blocks/oxeye_daisy_v0, blocks/oxeye_daisy_v1, blocks/oxeye_daisy_v2, blocks/pale_oak_sapling_v0, blocks/pale_oak_sapling_v1, blocks/pale_oak_sapling_v2, blocks/pink_petals_v0, blocks/pink_petals_v1, blocks/pink_petals_v2, blocks/pitcher_plant_top_v0, blocks/pitcher_plant_top_v1, blocks/pitcher_plant_top_v10, blocks/pitcher_plant_top_v11, blocks/pitcher_plant_top_v12, blocks/pitcher_plant_top_v13, blocks/pitcher_plant_top_v14, blocks/pitcher_plant_top_v15, blocks/pitcher_plant_top_v16, blocks/pitcher_plant_top_v17, blocks/pitcher_plant_top_v2, blocks/pitcher_plant_top_v3, blocks/pitcher_plant_top_v4, blocks/pitcher_plant_top_v5, blocks/pitcher_plant_top_v6, blocks/pitcher_plant_top_v7, blocks/pitcher_plant_top_v8, blocks/pitcher_plant_top_v9, blocks/spruce_sapling_v0, blocks/spruce_sapling_v1, blocks/spruce_sapling_v2, blocks/wildflowers_v0, blocks/wildflowers_v1, blocks/wildflowers_v2, blocks/wither_rose_v0, blocks/wither_rose_v1, blocks/wither_rose_v2

**RP-05** (16 files incl. companions, 0.2 MB): blocks/bamboo_large_leaves, blocks/carrots_stage0, blocks/carrots_stage1, blocks/carrots_stage2, blocks/kelp_anim, blocks/kelp_plant, blocks/kelp_plant_anim, blocks/lilac_top, blocks/open_eyeblossom, blocks/peony_top

## Purged (for the record)
- **RP-04**: 410 files / 20.7 MB — {'DUP': 109, 'COMPANION-DEAD': 146, 'CONSUMED': 135, 'BACKUP': 2}
- **RP-03**: 460 files / 6.1 MB — {'DUP': 137, 'COMPANION-DEAD': 185}
- **RP-01**: 216 files / 8.3 MB — {'OURS-DEAD': 114}
- **RP-05**: 75 files / 0.9 MB — {'DUP': 28, 'COMPANION-DEAD': 31, 'BACKUP': 2}

Full deleted-file lists: `_logs/purge_report.json` (published with the tools). The pre-purge trees rp04-135 / rp03-58 / rp01-103 / rp05-47 remain on disk and every purged Patrix file is re-pullable from the 128x zip (tools/remote_zip.py).
