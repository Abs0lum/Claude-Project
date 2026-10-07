# TEST COMMANDS — witness lineup 0u → 10 (2026-09-23)
**2026-09-27: PW-TestRunner BP v0.1.0 now does all of this for you** (`/scriptevent pw:test start`, then the clicker) — see `TESTRUNNER-GUIDE-v1.md`. This sheet stays as the manual fallback.
Every command below was checked against the shipped packs (BP-02 1.3.186, BP-01 1.3.35, BP-03 1.3.34, Markers 0.2.1) and the vanilla 1.26.50 block list. Type each line in chat on its own (cheats on). `@s` = you.

## Zone blocks → invisible entities
Stand in the middle of the building. `migrate` reaches 64 blocks sideways and 16 up/down (default 32 if the number is left off).
```
/scriptevent civ:markers show
/scriptevent civ:markers migrate 64
/scriptevent civ:markers list 64
/scriptevent civ:markers hide
```
Expected: `migrate r64: N marker blocks -> N entities (0 already there)`. `hide` is world-wide and later-loaded markers follow it; `show` brings them back. Repeat `migrate` in each separate area.
Other marker commands:
```
/scriptevent civ:markers check 32
/scriptevent civ:markers remove
/scriptevent civ:zone status
/scriptevent civ:zone close
/scriptevent civ:station reset
/scriptevent civ:hatch turn
/scriptevent civ:hatch flip
/scriptevent civ:frame reflow
```
`check` = what would also be saved in a structure with Include Entities ON · `remove` = nearest marker within 3 blocks · `hatch turn/flip` = move the lid's hinge 90°/180° · `frame reflow` = re-resolve frame posts after a structure load.

## Set-up (once)
```
/gamemode creative
/gamerule dodaylightcycle false
/gamerule doweathercycle false
```
Content log: Settings → Creator → Enable Content Log GUI. Vibrant Visuals: Settings → Video → Graphics Mode. Undo at the end: `/gamerule dodaylightcycle true` and `/gamerule doweathercycle true`.

## 0u · FIREFLY v2
```
/time set noon
/give @s firefly_bush
/time set midnight
/locate biome swamp
/locate biome mangrove_swamp
```
Teleport with the coordinates `/locate` prints: `/tp @s <x> 120 <z>` (creative: fly down).

## 0v · STABLE-API FIXES
```
/locate biome forest
/time set noon
/time set midnight
/weather rain
/weather thunder
/weather clear
/locate biome plains
/scriptevent pw:diag status
/scriptevent pw:diag verbose
/scriptevent pw:diag brief
/scriptevent pw:diag off
/scriptevent pw:diag on
/scriptevent pw:diag help
```
Content log lines to find: `[PW-VERSION] BP-01 Atmospheric Effects v1.3.35` · `[PW-VERSION] BP-03 Identification Diagnostics v1.3.34` · `MARKER-A v1.3.186` · any `[AbsolutRealism Sky] fog push failed: pw:ar_sky_…` (report it).

## 0w · ROOM SMOKE
```
/give @s pw:hearth_cobblestone
/give @s pw:flue_cobblestone 4
/give @s oak_log 16
/give @s flint_and_steel
/give @s oak_planks 4
/scriptevent pw:home status
```
Hearth, flues stacked above it through the roof, tap the hearth with logs, then flint & steel; put a plank on the chimney top; doors shut. Debug only (skips the wait): `/scriptevent pw:home smoke 12` · after loading a saved structure: `/scriptevent pw:home reflow`. (`/scriptevent pw:home clear` forgets EVERY hearth — only if the ledger is broken.)

## 0x · MARKERS 0.2.1 + HATCH
```
/scriptevent civ:markers migrate 64
/give @s pw:station_seat
/give @s pw:zone_kitchen
/give @s pw:furn_chair_oak
/give @s pw:furn_table_oak
/scriptevent civ:markers hide
/scriptevent civ:markers show
/give @s ladder 4
/give @s pw:hatch_lid
/scriptevent civ:hatch turn
```
Station/zone items place markers: normal tap = the cell in front of the face, SNEAK tap = the tapped block's own cell (the chair). Hit a visible marker to pick it up.

## 0y · ROUND 2
```
/give @s pw:furn_table_oak
/give @s pw:furn_mantel_oak
/give @s pw:furn_wall_shelf_oak
/give @s pw:furn_trestle_oak
/give @s pw:furn_barrel_seat_oak
/give @s pw:furn_shelf_oak
/give @s pw:furn_cupboard_oak
/give @s pw:furn_dresser_oak
/summon trader_llama
/summon wandering_trader
```
Summon the llama 4–6 times for the four coat colours. Plume: light a hearth (0w) and look above the chimney.

## 0z · FURNITURE (all 12 pieces; swap `_oak` for `_spruce` or `_dark_oak`)
```
/give @s pw:furn_bench_oak
/give @s pw:furn_stool_oak
/give @s pw:furn_chair_oak
/give @s pw:furn_barrel_seat_oak
/give @s pw:furn_table_oak 3
/give @s pw:furn_trestle_oak
/give @s pw:furn_shelf_oak
/give @s pw:furn_wall_shelf_oak
/give @s pw:furn_coat_pegs_oak
/give @s pw:furn_cupboard_oak
/give @s pw:furn_dresser_oak
/give @s pw:furn_mantel_oak
/give @s pw:station_seat
```
Sit = empty hand, tap a bench/stool/chair/barrel seat · stand = sneak · tables: place 2 then 3 in a row, break one.

## 0a · PHASE 1b + PURGE
```
/give @s light_gray_wool
/give @s light_gray_carpet
/give @s red_stained_glass
/give @s red_stained_glass_pane
/give @s rail
/give @s golden_rail
/give @s detector_rail
/give @s activator_rail
/give @s redstone_block
/give @s anvil
/give @s chipped_anvil
/give @s damaged_anvil
/give @s quartz_pillar
/give @s chiseled_quartz_block
/give @s potato
/give @s beetroot_seeds
/give @s cocoa_beans
/give @s nether_wart
/give @s torchflower_seeds
/give @s bone_meal 64
/give @s crimson_door
/give @s crimson_trapdoor
/give @s crimson_planks
/give @s crimson_stem
/give @s crimson_sign
/give @s warped_door
/give @s warped_trapdoor
/give @s warped_planks
/give @s warped_stem
/give @s warped_sign
/give @s candle
/give @s mob_spawner
/give @s web
/give @s noteblock
/give @s frame
/give @s packed_ice
/give @s honeycomb_block
/give @s honey_block
/give @s slime
/give @s wet_sponge
/give @s undyed_shulker_box
/give @s light_gray_shulker_box
/give @s chest
/give @s ender_chest
/give @s copper_chest
/give @s chain
/give @s copper_chain
/give @s campfire
/give @s soul_campfire
/give @s dried_ghast
```
The other 15 glass colours: swap `red` for white, orange, magenta, light_blue, yellow, lime, pink, gray, light_gray, cyan, purple, blue, brown, green, black.

## 0 · E2
```
/give @s chest 2
/give @s trapped_chest 2
/give @s copper_chest 2
/give @s ender_chest
/give @s armor_stand
/give @s bell
/give @s banner
/give @s loom
/give @s end_crystal
/give @s conduit
/give @s decorated_pot
/give @s cauldron
/give @s water_bucket
```

## 0b · PHASE 1 + BED
```
/give @s bed 1 8
/give @s bed 1 14
/give @s furnace
/give @s blast_furnace
/give @s smoker
/give @s dispenser
/give @s dropper
/give @s repeater
/give @s comparator
/give @s observer
/give @s lit_pumpkin
/give @s iron_door
/give @s sandstone_slab
/give @s sandstone_stairs
/give @s smooth_stone_slab
/give @s andesite_slab
/give @s andesite_stairs
/give @s granite_slab
/give @s granite_stairs
/give @s diorite_slab
/give @s diorite_stairs
/give @s stone_bricks
/give @s mossy_stone_bricks
/give @s cracked_stone_bricks
/give @s chiseled_stone_bricks
/give @s nether_brick
/give @s red_nether_brick
/give @s end_bricks
/give @s prismarine
/give @s oak_sign
/give @s oak_hanging_sign
/give @s oak_boat
/give @s oak_chest_boat
/give @s light_gray_shulker_box
/give @s undyed_shulker_box
/give @s copper_chest
```
Bed colours: `bed 1 <n>` — 0 white · 1 orange · 2 magenta · 3 light blue · 4 yellow · 5 lime · 6 pink · 7 gray · 8 light gray · 9 cyan · 10 purple · 11 blue · 12 brown · 13 green · 14 red · 15 black. Signs/boats: swap `oak` for spruce, birch, jungle, acacia, dark_oak, mangrove, cherry, pale_oak, bamboo (bamboo boat = `bamboo_raft`), crimson, warped.

## 1–10 · HOMESTEAD
```
/give @s pw:hearth_cobblestone
/give @s pw:flue_cobblestone 6
/give @s pw:wall_oak_planks 16
/give @s oak_log 16
/give @s charcoal 8
/give @s flint_and_steel
/give @s pw:frame_cornerpost
/give @s pw:roof45_ridge_oak 8
/give @s pw:roof_ridge_end_oak 2
/give @s pw:ramp_cobble_2_lo
/give @s pw:ramp_cobble_2_hi
/give @s pw:ramp_cobble_4_q1
/give @s pw:ramp_cobble_4_q2
/give @s pw:ramp_cobble_4_q3
/give @s pw:ramp_cobble_4_q4
/give @s snow_layer 16
/give @s campfire
/scriptevent pw:home status
/scriptevent pw:home reflow
```
Content log startup line: `[pw_homestead] HOMESTEAD runtime up (cycle 40t, puff 4t, chute 1t, rafters 10t)`. Fuel: logs/wood/stems = 2, planks = 1, coal/charcoal = 4 · lighters: flint & steel or fire charge. Ramps also come in `stonebrick` and `smooth_stone` (same `_2_lo/_2_hi/_4_q1…q4` endings).
