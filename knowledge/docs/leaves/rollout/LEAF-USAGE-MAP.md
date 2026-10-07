# LEAF USAGE MAP — today's leaves (pw:<species>_leaves) vs the pilot leaves (pw:pilot_<species>_leaves)

Task L, 2026-09-30. READ-ONLY investigation: no pack, build dir, tool or log was changed. This file is the only thing written.

## 0. Sources read (all line numbers below refer to these exact files)

| Pack / build | Path | Version / check |
|---|---|---|
| BP-02 Tectonic | `/home/claude/_build/bp02-195` | 1.3.195; packaged md5 b2fe3ed9… == delivery_ledger.md:154 (delivered 14:50 CT 09-30) |
| RP-01 Tectonic | `/home/claude/_build/rp01-104` | 1.3.104 = newest delivered (delivery_ledger.md:22/59). Leaf files md5-compared against `/mnt/user-data/outputs/RP-01-…-v1_3_104.mcpack`: terrain_texture, flipbook_textures, blocks.json, both leaf geo files, falling_tree entity + render controller all IDENTICAL; 308 `pw_*leaves*` files in both |
| RP-05 Flora | `/home/claude/_build/rp05-51` | 1.3.51 = newest delivered (delivery_ledger.md:86); terrain_texture md5 == delivered mcpack |
| RP-02/03/04/06/07/08/10 | `_build/rp02-205`, `rp03-60`, `rp04-142`, `rp06-1424`, `rp07-1431`, `rp08-148`, `rp10-142` | newest build dirs |
| RP-11, StripMine RP | `/home/claude/_packs/RP-11-v1_3_35.mcpack`, `PW-StripMine-RP-v3_0_1.mcpack` | no build dir exists; zip listings + terrain/blocks files read (extract in scratchpad/leafmap) |
| BP-01 / BP-03 / StripMine BP / Civitas Markers | `_build/bp01-135`, `bp03-134`, `stripmine-bp-136`, `markers-0.2.1`, `markers-0.2.2-rp`; `_packs/PW-StreetKit-BP-v0_1_4.mcpack` | newest build dirs |
| Pilot | `_build/leaf-pilot-blocks` (24 files) == `_build/testrunner-0.4.9/blocks/pw_pilot_*.json` (24/24 md5 SAME); RP `_build/testrunner-rp-0.4.0`; generator `/home/claude/tools/build_leaf_pilot_rp.py` (14,735 B) | |

---

## 1. BP-02 leaf blocks — `bp02-195/blocks/*_leaves.json`

Nine files, all 203 lines, same layout (line numbers identical in every file):

| Species | Identifier (line 5) | map_color | seconds_to_destroy | loot (line 48) |
|---|---|---|---|---|
| oak | `pw:oak_leaves` | #3a5a25 | 2.0 | loot_tables/blocks/oak_leaves.json |
| spruce | `pw:spruce_leaves` | #4a6f30 | 2.0 | …/spruce_leaves.json |
| birch | `pw:birch_leaves` | #75a02f | 2.0 | …/birch_leaves.json |
| jungle | `pw:jungle_leaves` | #42741b | 2.2 | …/jungle_leaves.json |
| acacia | `pw:acacia_leaves` | #8eb152 | 2.0 | …/acacia_leaves.json |
| dark_oak | `pw:dark_oak_leaves` | #3a5a25 | 2.0 | …/dark_oak_leaves.json |
| mangrove | `pw:mangrove_leaves` | #7da750 | 2.1 | …/mangrove_leaves.json |
| cherry | `pw:cherry_leaves` | #e5a8d6 | 1.9 | …/cherry_leaves.json |
| pale_oak | `pw:pale_oak_leaves` | #a8c293 | 2.0 | …/pale_oak_leaves.json |

- `format_version` "1.21.80" (line 2). No `traits`, no `menu_category`.
- **States (lines 6–33)** — the FIRST value of each list is the default permutation:
  - `pw:variant` [0,1,2,3,4,5,6] (7–15)
  - `pw:rseed` [false,true] (16–19)
  - `pw:section` [0,1,2] (20–24)
  - `pw:exposure` [0,1] (25–28)
  - `pw:section_rolled` [false,true] (29–32)
  - State space per block = 7 × 2 × 3 × 2 × 2 = **168**; 9 blocks = **1,512**.
- **Base components (35–53)**, the same in all nine:
  - `destructible_by_mining` (36–38)
  - `destructible_by_explosion` 0.2 (39–41)
  - `flammable` catch 30 / destroy 60 (42–45)
  - `light_dampening` 1 (46)
  - `map_color` (47)
  - `loot` (48)
  - `custom_components` ["pw:randomize_variant"] (49–51)
  - `tag:plant` (52)
  - None of them has collision_box, selection_box, light_emission, `transformation` or `tint_method` other than "none".
- **Permutations (54–202): 7 per block, 63 in total**, and every one is keyed ONLY on `q.block_state('pw:variant') == N` (lines 56, 71, 93, 115, 137, 159, 181). Each sets only `minecraft:geometry` and `minecraft:material_instances`:
  - v0 (56–69): `geometry.pw_leaves_v0`, material `*` = `pw_<s>_leaves_v0`, **render_method opaque** (line 62), AO true, face_dimming true, tint_method none.
  - v1–v5: `geometry.pw_leaves_v1..v5` (jungle: `geometry.pw_leaves_jungle_v1..v5`), `*` = `pw_<s>_leaves_vN`, plus `inner_core` = `pw_<s>_leaves_vN_inner`, both alpha_test, AO true, face_dimming true, tint none.
  - v6 (181–200): `geometry.pw_leaves_v6` (jungle `…jungle_v6`), and it **reuses the v5 textures** (`pw_<s>_leaves_v5` / `_v5_inner`, lines 186 and 193).
  - No permutation reads `pw:rseed`, `pw:section`, `pw:exposure` or `pw:section_rolled`. Those four are read and written only by scripts (§3).
  - After 1.3.195 there is no Molang inside the permutation components; `bone_visibility` was removed together with `pw:open_*` (phase_log.md:1312).
- **Permutation-count history:**
  - phase_log.md:275 (09-27): load warning "66,343 block permutations (>65,536)".
  - phase_log.md:395 / decision_journal.md:1375 (09-28): "World with over 65536 block permutations … Current world has 66346"; leaves = 48,384.
  - decision_journal.md:1450: the census puts leaves at 48,384 = 9 × 5,376, which is 75 % of our custom permutations.
  - decision_journal.md:1453 (D-C312): `pw:open_*` were read by bone_visibility, so 1.3.194 dropped `pw:far` only and leaves fell to 24,192.
  - phase_log.md:1203: his pick "drop pw:far + open_* (leaves 48,384 -> 1,512)".
  - phase_log.md:1312 / 1315: 1.3.195 removed `pw:open_n/e/s/w` and bone_visibility → "168 perms/leaf; ours 17,850, world ~19,468".
  - manifest.json description: "block permutations down to about 19,500".
- **Save-migration note:** decision_journal.md:1462 logs an ASSUMPTION: a saved leaf whose state set no longer matches is reset to the default permutation. The test for it was p12 t01. The p12 result (decision_journal.md:1511) lists only h01/h02 as FAIL. His t01 note "replace variant 0" is at decision_journal.md:1525.

## 2. BP-02 features / feature_rules — which leaf ids and states are placed

**No feature sets a leaf state.** Every `leaf_block` is `{ "name": … }` with no `states` key, so worldgen places the default permutation: variant 0, rseed false, section 0, exposure 0, section_rolled false. The code comments agree at main.js:2039–2041 ("Worldgen-placed leaves will all be at variant=0") and main.js:2187.

All 22 `minecraft:tree_feature` files are format 1.13.0 and use `fancy_canopy`. The leaf `name` is at line 29, except pw_jungle_bush_feature.json at line 20.

| Feature file | Places | Trunk | Canopy h/r | Branch density | pw leaves in may_replace (lines) |
|---|---|---|---|---|---|
| pw_oak_young / mature / old_tree_feature | pw:oak_leaves | pw:oak_young/mature/old | 3/3, 3/3, 4/3 | 0 | oak, spruce, birch, jungle, dark_oak, pale_oak (58–63) |
| pw_oak_elder_tree_feature_v2 | pw:oak_leaves | pw:oak_elder | 4/5 | 0.4 | same six (58–63) |
| pw_spruce_young / mature / old | pw:spruce_leaves | pw:spruce_* | 4/3, 4/3, 5/3 | 0 | six (58–63) |
| pw_spruce_elder_tree_feature_v2 | pw:spruce_leaves | pw:spruce_elder | 5/4 | 0.4 | six (58–63) |
| pw_birch_young / mature / old | pw:birch_leaves | pw:birch_* | 3/3, 3/3, 4/3 | 0 | six (58–63) |
| pw_jungle_young | pw:jungle_leaves | pw:jungle_young | 4/3 | 0 | all nine (58–66) |
| pw_jungle_mature / old | pw:jungle_leaves | pw:jungle_* | 3/3, 4/3 | 0 | six (58–63) |
| pw_jungle_elder_tree_feature_v2 | pw:jungle_leaves | pw:jungle_elder | 5/4 | 0.4 | six (58–63) |
| pw_jungle_bush_feature | pw:jungle_leaves | pw:jungle_young (`trunk`, h 2) | 2/2 | — | none |
| pw_dark_oak_elder_tree_feature_v2 | pw:dark_oak_leaves | pw:dark_oak_elder | 5/4 | 0.4 | six (58–63) |
| pw_pale_oak_elder_tree_feature_v2 | pw:pale_oak_leaves | pw:pale_oak_elder | 5/4 | 0.4 | six (58–63) |
| acacia_tree_feature (overrides minecraft:acacia_tree_feature) | pw:acacia_leaves | minecraft:acacia_log | 2/4 | 0 | acacia only (45) |
| cherry_tree_feature (overrides minecraft:) | pw:cherry_leaves | minecraft:cherry_log | 5/5 | 0 | cherry only (45) |
| mangrove_tree_feature (overrides minecraft:) | pw:mangrove_leaves | minecraft:mangrove_log | 4/4 | 0 | mangrove only (48) |

- There are no pw birch-elder or pale_oak young/mature/old features.
- **Aggregate and weighted wrappers** (they contain no leaf ids; they route to the features above):
  - `minecraft:oak_tree_feature`, `birch_tree_feature`, `spruce_tree_feature`, `jungle_tree_feature`: weighted young / mature / mature+vines / old / old+vines.
  - `fancy_oak`, `overgrown_oak`, `swamp_oak` → oak elder+branches.
  - `bee_oak*`, `oak_tree_bees` → oak mature.
  - `roofed_tree*`, `dark_oak_tree_feature` → dark_oak elder.
  - `pale_oak_tree_feature` → pale_oak elder.
  - `mega_spruce`, `mega_pine` → spruce elder.
  - `pine_tree_feature` → spruce old.
  - `mega_jungle`, `tall_jungle` → jungle elder.
  - `undecorated_jungle*`, `jungle_bush*` → jungle young / bush.
  - `super_birch`, `birch_tree_bees` → birch old.
  - `savanna_tree`, `large_acacia`, `acacia_tree_bees` → `minecraft:acacia_tree_feature`.
  - `fallen_oak/birch/spruce_tree_feature` → the young features.
  - The `*_with_vines` aggregates add `pw:vine_overlay_scatter` → `pw:vine_block_feature`, which places `minecraft:vine` attached to pw log tiers only. No leaves are involved.
- **feature_rules** that place trees (`places_feature`), all surface_pass:
  - emerald_jungle_canopy_rule → minecraft:tall_jungle_tree_feature
  - forest_sparse_birch_rule → birch_tree_feature
  - forest_sparse_oak_rule → oak_tree_feature
  - misty_dark_canopy_rule → roofed_tree_feature
  - old_growth_pines_rule, snowy_taiga_sparse_spruce_rule, taiga_sparse_spruce_rule → spruce_tree_feature
  - The other 19 rules place no trees.
  - `biomes/` (19 files) contains no leaf ids and no tree features.
- `structures/pw/s1…s8.mcstructure` contain no leaf ids (grep of the NBT returned 0).

## 3. BP-02 scripts — `bp02-195/scripts/main.js` (5,180 lines)

The other script files contain no leaf ids: pw_codex, pw_companion, pw_furniture, pw_ground (only `minecraft:leaf_litter`), pw_homestead*, pw_mob_light, pw_weather.

### 3.1 Id sets and tables

| Name | Lines | Content |
|---|---|---|
| `SPECIES` | 54–89 | Per-species `logs` and `leaves`. Leaves = vanilla id + `pw:<s>_leaves` (60, 67, 70, 74, 75, 78, 79, 80, 86). Oak also lists `pw:oak_leaves_a…_f` (61–63), which are not defined in bp02-195/blocks. Index order: 0 oak, 1 spruce, 2 birch, 3 jungle, 4 acacia, 5 dark_oak, 6 mangrove, 7 cherry, 8 crimson, 9 warped, 10 pale_oak, 11 mushroom |
| `EXTRA_LEAF_IDS` | 211–214 | minecraft:azalea_leaves, flowering_azalea_leaves, pale_oak_leaves |
| `PW_VARIANT_COUNT` | 2053–2064 | 9 leaf ids → 7; log tiers → 5 |
| `PW_LEAF_VARIANT_POOLS` | 2089–2098 | key `${section}_${exposure}`: "0_1" [1,1,2,3], "1_0" [3], "1_1" [3,4,4], "2_1" [3,5,5,6,6], "0_0" [3], "2_0" [3] |
| `PW_RANDOMIZE_TYPES` = `PW_LEAF_TYPES` | 2208–2222 | 9 leaf ids **plus 17 log-tier ids** (pw:oak_young … pw:pale_oak_elder) |
| `PW_TA_LOG_TYPES` | 2235–2255 | vanilla logs/stems + 17 pw log tiers |
| `PW_LEAF_TYPES_DECAY` | 3543–3547 | the 9 leaf ids |
| `PW_LEAF_TO_WOOD_TYPE` | 3550–3560 | oak 0, spruce 1, birch 2, jungle 3, dark_oak 4, pale_oak 5, acacia 6, cherry 7, mangrove 8 (leaf_litter `pw:wood_type`) |
| `PW_LOG_TYPES` | 3563–3581 | decay "connected" set: vanilla logs + stripped + wood + 17 pw tiers |

### 3.2 onPlace custom component `pw:randomize_variant`

- **Registration:** `system.beforeEvents.startup` → `blockComponentRegistry.registerCustomComponent("pw:randomize_variant", { onPlace: pwRandomizeVariant })` at 2172–2181. It is declared by every leaf block at line 49.
- **`pwRandomizeVariant`** (2124–2170):
  - Reads `pw:section_rolled` (2148), then calls `pickVariantForBlock`.
  - Writes `pw:variant` = pick (2152). It also writes `pw:rseed` = true (2154), but only if section_rolled was already true.
  - For log tiers it also writes `pw:top_variant` (2157–2165). One `setPermutation` at 2166.
  - The comments at 2033–2041 say worldgen leaves do not reach it: "onPlace only. Worldgen-placed leaves will all be at variant=0". The same comments record that `minecraft:random_ticking` on leaves broke registration on PS5/Android (also 3529–3531).
- **`pickVariantForBlock`** (2105–2122):
  - Leaves: reads `pw:section_rolled`, `pw:section` and `pw:exposure` (2111–2113). Returns 0 if not rolled (2115); otherwise returns `Math.random()` over `PW_LEAF_VARIANT_POOLS[key]` (2116–2118). The pick is random, not position-based.
  - Non-leaf ids: uniform 0..N-1 (2120–2121).
  - The leaf test is `typeId.endsWith("_leaves")` (2107).

### 3.3 Classify: `detectSectionAndExposure` and `_markLeaf`

- **`detectSectionAndExposure(dim,x,y,z,leafType)`** (2597–2662):
  - Walks up and down (at most 32 each way) through blocks whose typeId equals `leafType` (2600–2614).
  - Section: canopy height 1 → 1; otherwise relY < 0.34 → 0, < 0.67 → 1, else 2 (2616–2625).
  - Exposure: any of the 6 face neighbours that is not `…_leaves` / `…_wart_block` → 1 (2631–2641). Otherwise it reads the neighbours' `pw:section_rolled` + `pw:exposure` (2650–2652) and sets 1 if any flagged neighbour has exposure 1.
- **`_markLeaf`** (2666–2686) WRITES `pw:section`, `pw:exposure`, `pw:section_rolled`=true and `pw:rseed`=false (2669–2674). It counts `_scanStats.perSpecies[typeId]` (2678–2680). The whole body is in try/catch and returns false on any throw.
- **`_treeCompletionBFS`** (2695–2731): a 6-face flood through blocks with typeId equal to the seed's. It reads `pw:section_rolled` (2716) and marks unrolled leaves. Caps: `budget` and `PW_BFS_MAX_LEAVES` = 1500 (2555); optional deadline.

### 3.4 Process A — trunk association (log-first classifier)

- **Job:** `_treeAssociationJob` (2916–2963). Kicked by runInterval `PW_TA_INTERVAL` = 30 t (2965–2974), and on playerSpawn (3274), playerJoin (3284) and dimension change (3289).
- **Cadence and radius:**
  - Radius 35 XZ, ±70 Y (2265–2266), nearest-first shells via `pwOffsetIterator` (2316).
  - At most 3 trees per player per cycle, ×3 while the SlabForge key is out (2939). Yield every 400 cells or 8 ms (2267, 2274).
  - Per tree: 300 marks and a 40 ms deadline (2275–2277). Skipped while a player is in the teleport cooldown (2451–2473; >32 blocks in one tick → 60 t).
- **Reads:**
  - Logs by `PW_TA_LOG_TYPES`. `_findTreeTop` climbs `PW_TA_LOG_TYPES` (2857–2867).
  - `_findAdjacentLeaf` takes the first of 6 faces with `typeId.endsWith("_leaves")` (2845–2855).
  - Fallback (v1.3.147 oak fix): radius-2 shell around the tip and up to 3 logs down, accepting any id with `indexOf("leaves") >= 0` (2875–2890).
  - `pw:section_rolled` of the found leaf (2893).
- **Writes:** only through `_markLeaf` / `_treeCompletionBFS` (2896, 2902). It never writes `pw:variant`.

### 3.5 Phase-1 job — classify-once + variant apply (the "forward randomizer")

- **Job:** `_phase1ScanJob` (2987–3095), kicked by runInterval `PW_SCAN_INTERVAL` = 22 t (2517, 3097–3106).
- **Radius:** `pwOffsetIterator(25, 42)` (3008) with a dy guard of −40…+42 (2824, 2834, 3013). Yield every 400 cells or 8 ms (2822).
- **Filter:** `PW_LEAF_TYPES.has(typeId)` (3023). This includes the 17 log tiers. For those, `getState("pw:section_rolled")` is undefined, `_markLeaf` fails, and the loop moves on (3029–3042).
- **Step 1, classify** (3025–3043): if `pw:section_rolled` !== true, `_markLeaf`, then re-read.
- **Step 2, distance toggle** (3045–3088), reads `pw:variant` (3048):
  - distSq > `PW_FAR_OUTER_SQ` (72² = 5,184): write `pw:variant` 0 (3053).
  - distSq < `PW_FAR_INNER_SQ` (64² = 4,096) and variant 0: `pickVariantForBlock` (3061) → write `pw:variant` = target + `pw:rseed` = true (3064–3067). It records `_appliedRegistry[x,y,z,dim] = {v: target}` (cap 30,000, 2830; 3076–3079) and counts `perVariant` (3073–3074).
  - The farthest cell this iterator visits has distSq 25²+25²+42² = 3,014, below 4,096. So every visited classified leaf takes the "inner" branch, and the >72 branch at 3050 is never reached from this job. The code comment at 2826–2828 says the same.
- **`_appliedRegistry`** (2833) is an in-memory Map. It is not persisted across reloads.

### 3.6 Far reverter and re-applicator (today's "reverse randomizer / far shell")

- **Far reverter:** runInterval 39 t (`PW_REVERT_INTERVAL`, 2831; 3152–3182), at most 300 per pass (2832).
  - Walks only `_appliedRegistry` entries.
  - When every player is more than 72 blocks away: reads `pw:variant` and, if it is not 0, writes 0 (3174–3176). Marks the entry dormant.
  - Checks `PW_LEAF_TYPES.has(typeId)` (3172).
- **Re-applicator (HOTFIX-2 v1.3.59):** runInterval 17 t (3187–3218), at most 300 per pass.
  - For dormant entries when a player is within 64 blocks: if `pw:variant` == 0, writes the stored `e.v` back (3211–3212).
- **The old v1.2.51 50–62-block reverse randomizer has been removed.** It is documented at 3108–3130 and 3143–3146. Its constants (2531–2538) and `_reverseStats` (3131–3137) remain but are not used. `_isLeafPwBlock` (3139) is unused. `_runLayeredScan` / `_runScanBox` (2745–2790) have no callers. `_scheduleVerticalExtensions` (2796) is a no-op.

### 3.7 Invalidation triggers (state writers outside the scanner)

- **playerBreakBlock** on an id that ends with `_leaves` and is in `PW_LEAF_TYPES` (3245–3256): `_enqueueCascade` + `_forceKickScanner`. The kick only clears the `_p1JobActive` guard (3231–3243).
- **explosion:** every impacted block is enqueued (3259–3267).
- **Felling:** each removed leaf is enqueued (770).
- **Cascade flush:** runInterval 4 t, 50 keys per tick (3224–3225, 3296–3326). For the 6 face neighbours in `PW_LEAF_TYPES`, it WRITES `pw:section_rolled`=false and `pw:rseed`=false (3318–3320).
- **`reValidateExposure`** (3610–3665), called from the decay job (3796):
  - Reads `pw:exposure` and `pw:section_rolled` (3612, 3617) and recomputes the edge from the 6 faces (3623–3635).
  - On mismatch it WRITES section_rolled=false and rseed=false (3658–3660).
- **Heartbeat:** runInterval 600 t (3332–3347), force-kick only.
- **Verify job:** runInterval 200 t (3438–3467); ±30 XZ; layers y+0…y+42 (2543–2550). It reads `pw:section_rolled` + `pw:rseed` (3420–3421) and only counts "stranded" leaves; it writes nothing.
- **Diagnostics:** chat ping at 3350–3369 is disabled (`PW_DIAGNOSTICS_ENABLED` false, 2526).

### 3.8 Leaf decay (non-felling) + leaf litter

- **Job:** `_decaySweepJob` (3748–3830), runInterval 200 t (3583, 3742–3746).
- **Area:** ±10 XZ, ±8 Y; at most 8 decays per run; early exit after 1,000 cells with no leaf (3583–3588, 3766, 3776).
- **Per leaf:**
  - Filter `PW_LEAF_TYPES_DECAY` (3788).
  - `reValidateExposure` (3796).
  - Connectivity cache TTL 600 t (3593, 3799–3803).
  - `isLeafConnectedToLog` (3669–3711): BFS of at most 50 steps, distance ≤ 6, only through blocks with the same typeId. "Connected" = reaches `PW_LOG_TYPES`.
  - Orphan → `spawnLeafLitter` (3714–3735): spawns `pw:leaf_litter` with `pw:wood_type` = `PW_LEAF_TO_WOOD_TYPE[typeId]` (3718–3726), then sets the block to air (3730).
- **Litter lifecycle:** runInterval 20 t (3843–3902). Entity property ranges are in `entities/leaf_litter.json`: wood_type 0–11, lifetime 0–600, on_ground 0–1.

### 3.9 BIGCANOPY felling — how leaves are found and removed

- **Trigger:** `world.afterEvents.playerBreakBlock` (1208).
  - The species comes from the broken LOG id (`LOG_TO_SPECIES`, 91–94, 1218). Creative players are skipped.
  - `findConnectedTree` (264–383): its "rooted" test treats `…_leaves` as not-ground (300). The acacia bridge pass walks through `…_leaves`/air (366–367).
- **Tree gate:** `hasAdjacentLeaves` (407–433, called at 1301) — at least one log with any 26-neighbour where `isAnyLeaves` is true: species list, OR `id.endsWith("_leaves")`, wart blocks, azalea or mushroom blocks (410–422).
- **Fall path helpers:** `…_leaves` counts as "not ground" in `groundYAt` (841), as a minor obstacle in `pickFallYaw` (871), as not a collider (150), and as not small vegetation (1073).
- **Canopy measure for the entity** (1418–1458):
  - 8 rays, r 1–7, y top−1…top+3; stops at the first block in `PW_LEAF_TYPES` (1435). That set also includes log tiers.
  - Reads `pw:variant` of the hit leaves (1441) → tally → `ft:leaf_variant` = mode (1460–1462).
  - The entity property range is 0–6 (bp02 `entities/falling_tree.json` 100–107). RP-01 selects the texture with `Array.leaf_textures[wood_type*7 + leaf_variant]` (rp01 `render_controllers/falling_tree.json`:628, array 648–733).
- **Leaf removal:** `cleanOrphanLeavesJob` (629–803), started +1 t after the logs are cleared (1395–1409).
  - Candidate ids = `SPECIES[idx].leaves` + `EXTRA_LEAF_IDS` (632–634). This is an exact id match; no states are read.
  - AABB = felled logs ±9, capped at 40,000 cells (630–673).
  - "Owned" leaves: a BFS of range 8 from the felled logs (675–709).
  - "Protected" leaves: a BFS from standing logs, excluding owned leaves (711–748).
  - Unprotected leaves, at most `MAX_LEAVES` = 260 (218, 754–759), are removed in fall-vector order. The pace follows the fall curve between ticks 15 and 92 (238–240, 778–798), with a safety flush at 171 t (800–802).
  - Each removal (762–772): `setPermutation(air)` (767), `_rollLeafLoot` (586–623: sapling/stick/apple rolls per species; no leaf item), `_enqueueCascade` (770).
  - Felling never reads a tag. No script reads any block tag (no `hasTag`/`getTags` in scripts), so `tag:plant` is unused by scripts.
- **Shedding:** `leafTypeId = pw:${speciesKey}_leaves` → `PW_LEAF_TO_WOOD_TYPE` → `pw:leaf_litter` bursts (1573–1612). Also the `pw:leaf_fall` particle (1805) and the sound `block.azalea_leaves.fall` (1874).

### 3.10 TREEGROW (G2)

- 4895–5090. A placed `minecraft:<s>_sapling` / mangrove_propagule (5028–5036) is registered. After 2,400 + hash-jitter ticks (4901–4902) the job runs `structure load "pw:test_<s>_young" … <rot> none true` (4907–4917, 5070).
- **No leaf ids or states are handled in script.** The structures `pw:test_*_young` are NOT in `bp02-195/structures` (only s1–s8 there) or anywhere under `_build`/`_structures`, so their leaf content is unknown from files.

### 3.11 Other leaf readers

- **Ambient leaf drift:** runInterval 40 t (5132–5180), radius 22, 26 samples, at most 4 particles. It matches any id where `indexOf("leaves") > 0` (5146–5149) over air and reads no states.
- **Stats** `emitStats` (3481–3506), runInterval 1,200 t plus `/scriptevent pw:stats` (3507–3513). It prints `perSpecies` by typeId (`replace("pw:","").replace("_leaves","")`, 3492) and `perVariant` v1–v6 (3497–3501).
- **`/scriptevent pw:variant_audit`** (3919–3968): ±32 cube, filter `PW_LEAF_TYPES`. It reads `pw:variant`, `pw:section_rolled` and `pw:rseed` (3943–3945) and prints v0–v6.
- **`/scriptevent pw:diag_status`** (3971–3991): counters only.
- **`/scriptevent pw:variant_dump`** (3994–4051): every `pw:*` block with a `pw:variant` state; prints v0–v4 only (4043).

## 4. Resource packs — leaf geometry, textures and stack winner

**RP-01 Tectonic 1.3.104 is the ONLY pack that defines any `pw:*_leaves` render data.** No other RP in the stack defines a `pw_*leaves*` terrain key, a leaf geometry id, a `pw:*_leaves` blocks.json key or a pw leaf flipbook. Checked: RP-11 1.3.35, RP-10 1.3.42, RP-08 1.4.8, RP-07 1.4.31, RP-06 1.4.24, RP-05 1.3.51, RP-04 1.3.142, RP-03 1.3.60, RP-02 2.0.5, StripMine RP 3.0.1, Civitas Markers RP. So under the stack order RP-11 → RP-01 (top wins), **RP-01 wins uncontested**. The TestRunner RP 0.4.0 pilot keys are all `pw_pilot_*`; their overlap with RP-01's 484 terrain keys is 0.

- **Geometry** (format 1.21.0, texture 16×16):
  - `models/blocks/pw_leaves_variants.geo.json` (87,353 B / 6,455 lines):

    | Geometry | Line | Bones | Cubes |
    |---|---|---|---|
    | `geometry.pw_leaves_v0` | 6 | leaves + pw_nf/ef/sf/wf | 1 |
    | `v1` | 138 | core, pw_nf/sf/ef/wf, inner_core | 14 |
    | `v2` | 1243 | same bones as v1 | 14 |
    | `v3` | 2348 | same bones as v1 | 8 |
    | `v4` | 3005 | same bones as v1 | 16 |
    | `v5` | 4258 | same bones as v1 | 16 |
    | `v6` | 5511 | no inner_core | 12 |

  - `pw_leaves_jungle_variants.geo.json` (82,701 B / 5,209 lines): `geometry.pw_leaves_jungle_v1` (6, 10 cubes), `v2` (813, 12), `v3` (1770, 8), `v4` (2427, 12), `v5` (3384, 11), `v6` (4265, 12).
  - **None of these cubes carries a face-level `material_instance`.** The BP's `inner_core` material instance therefore binds no face, as flagged in decision_journal.md:1566(b). The `pw_nf/ef/sf/wf` bones remain in the geometry, but since 1.3.195 no bone_visibility drives them.
- **terrain_texture.json** (130,233 B / 5,552 lines; 484 keys): **180 pw leaf keys**. Every referenced PNG exists.
  - `pw_<s>_leaves_v0…v5` for the 9 species (oak 212–224 + 602; birch 227–239 + 608; spruce 242–254 + 605; jungle 257–269 + 611; dark_oak 272–284 + 614; pale_oak 287–299 + 617; acacia 557–569 + 620; mangrove 572–584 + 623; cherry 587–599 + 626).
  - `…_v0…v5_inner` (1037–1196).
  - `…_n` (629–824 block) and `…_mer` (647–824, not oak). Some v1–v3 `_mer` keys point at the v0 file (e.g. birch 689–701, pale_oak 797–809).
  - Legacy aliases `pw_oak_leaves` (28), `pw_spruce_leaves` (115), `pw_jungle_leaves` (118), `pw_birch_leaves` (121), `pw_dark_oak_leaves` (124), `pw_pale_oak_leaves` (127) → the v0 PNGs.
- **Texture sets:** 96 `pw_*leaves*.texture_set.json` (format 1.21.30; color + normal + MERS; all references resolve). That is 12 per species for 8 species. **Oak has no texture sets**: oak has `_n` PNGs but no `_mer` and no `.texture_set.json`.
- **Flipbooks** (`textures/flipbook_textures.json`, 163 entries): 156 leaf entries, all 8 frames with blend_frames on and 4–6 ticks per frame. That is 54 colour tiles (v0–v5 × 9, lines 116–964), 48 `_mer` (980–1732) and 54 `_n` (1748–2596). The `_inner` tiles are not animated.
- **blocks.json:** `pw:<s>_leaves` → `"sound": "grass"` for all 9 (lines 12, 30, 45, 57, 63, 69, 72, 75, 78). No lang names for pw leaves exist in any RP.
- **Other RP-01 uses of the leaf block textures:**
  - `entity/falling_tree.json` references `textures/blocks/pw_<s>_leaves_v0/v1/v2` in 60 lines (54–65, 114–197…) for the falling canopy. The render controller selects them by `ft:wood_type*7 + ft:leaf_variant` (628, 648–733).
  - `particles/pw_leaf_fall.json`:8 uses `textures/blocks/pw_oak_leaves_v0`.
- **Vanilla leaf keys (context, not pw):**
  - RP-05 defines 46 vanilla leaf terrain keys (`leaves`, `leaves2`, `oak_leaves`, `…_carried`, azalea …).
  - RP-04 blocks.json defines the 10 `minecraft:*_leaves` entries.
  - RP-02 has cherry/pale_oak leaf particles.

## 5. Other references to leaf ids

- **BP-02 loot** `loot_tables/blocks/<s>_leaves.json` (9 files): shears → `minecraft:<s>_leaves` item (line 14). Plus sapling 0.05 (jungle 0.025), stick 0.02 (1–2), apple 0.005 (oak). The block's `minecraft:loot` points here (block line 48).
- **Recipes / spawn_rules / items / biomes in BP-02:** no leaf ids.
- **BP-01 1.3.135:** only the sound name `pw:ambient.wind.wind_in_leaves` (scripts/main.js 138–456). No block ids.
- **BP-03 1.3.134:** none.
- **StripMine BP 1.3.6 (stripmine-bp-136):** vanilla ids only, no `pw:*_leaves`.
  - `spawn_rules/*` `spawns_on_block_filter` "minecraft:leaves"/"leaves2" (e.g. canary 14–15, 49–50; vulture 15–16 …).
  - 13 bird/insect entities list vanilla leaf names (e.g. finch.behavior.json:1031–1035).
  - `scripts/entity/Sloth.js`:50, 66–67 check `minecraft:jungle_leaves` / `minecraft:leaves`.
- **Civitas Markers BP 0.2.1 / RP 0.2.2, StreetKit BP 0.1.4:** none.
- **TestRunner BP 0.4.9 (noted only):**
  - p1.js:71 does `setblock pw:oak_leaves ["pw:variant"=3]` and `pw:spruce_leaves ["pw:variant"=5]`.
  - p12.js:70 / p14.js:76 fill `pw:oak_leaves` boxes.
  - p15.js:21–31 lists today's ids per species (incl. `pw:oak_leaves_a…f`). It places pilot `pw:pv` with `cellHash` + nearest-log distance `pickShape` (52–64, 203–206).
  - It references no `pw:section*`/`rseed` state.

## 6. Today vs pilot, per species

The pilot BP blocks are `testrunner-0.4.9/blocks/pw_pilot_*.json` (== leaf-pilot-blocks). The pilot RP is `testrunner-rp-0.4.0`.

| Species | Today id | Pilot ids (0.4.9) | Pilot tint | Today tint |
|---|---|---|---|---|
| oak | pw:oak_leaves | pw:pilot_oak_leaves (+ `_bt`, `_iso`, `_far`, `_farp`) | `_pc` pre-coloured; `_bt` default_foliage | none (pre-coloured PNG) |
| spruce | pw:spruce_leaves | pw:pilot_spruce_leaves (+ `_bt`, `_iso`, `_far`, `_farp`) | `_pc`; `_bt` evergreen_foliage | none |
| birch | pw:birch_leaves | pw:pilot_birch_leaves (+ `_bt`) | `_pc`; `_bt` birch_foliage | none |
| jungle | pw:jungle_leaves | pw:pilot_jungle_leaves (+ `_bt`) | `_pc`; `_bt` default_foliage | none |
| acacia | pw:acacia_leaves | pw:pilot_acacia_leaves (+ `_bt`) | `_pc`; `_bt` default_foliage | none |
| dark_oak | pw:dark_oak_leaves | pw:pilot_dark_oak_leaves (+ `_bt`) | `_pc`; `_bt` default_foliage | none |
| mangrove | pw:mangrove_leaves | pw:pilot_mangrove_leaves (+ `_bt`) | `_pc`; `_bt` default_foliage | none |
| cherry | pw:cherry_leaves | pw:pilot_cherry_leaves | untinted tiles (no `_pc`/`_bt`) | none |
| pale_oak | pw:pale_oak_leaves | pw:pilot_pale_oak_leaves | untinted tiles | none |
| azalea | — (vanilla only; in EXTRA_LEAF_IDS) | pw:pilot_azalea_leaves | untinted | — |
| flowering_azalea | — (vanilla only) | pw:pilot_flowering_azalea_leaves | untinted | — |

The tint table is at build_leaf_pilot_rp.py:30–32. `tint_method` is set only on the `_bt` blocks.

**States:**
- Today: `pw:variant` 0–6, `pw:rseed`, `pw:section` 0–2, `pw:exposure` 0–1, `pw:section_rolled` (168 combinations per block).
- Pilot: `pw:pv` 0–8 only (9 per block). All 24 pilot blocks together = 216.
- The pilot has no `traits`.

**Component differences** (today block line → pilot):

| Item | Today | Pilot |
|---|---|---|
| geometry | pw_leaves_v0…v6 / jungle_v1…v6 | pv0 `pw_pilot_far`; pv1–5 + 8 `pw_pilot_full`; pv6–7 `pw_pilot_cards`; spruce pv1–8 `pw_pilot_spruce` |
| material instance names | `*`, `inner_core` (binds no face) | `*` face tile, `extra` card tile, `top` (spruce) |
| render_method | v0 opaque, v1–v6 alpha_test | pv0 opaque, pv1–8 alpha_test (`_far`/`_farp`: alpha_test_to_opaque) |
| AO / face_dimming | true / true | false / false (`_iso` adds `isotropic: true`) |
| transformation | none | per-pv quarter turn (rotation y 0/90/180/270) |
| destroy time | 1.9–2.2 s | 0.2 s |
| flammable | 30 / 60 | absent |
| loot | per-species table | absent (so the block drops itself as an item; engine default) |
| custom_components | pw:randomize_variant | absent |
| tag:plant | yes | absent |
| map_color | per species (§1) | #3f6b2a on all 24 |
| menu_category | absent | nature |
| textures | `pw_<s>_leaves_vN(+_inner)`, 8-frame flipbooks, texture sets for 8 of 9 species (not oak) | static `pw_pilot_<s>_f0…f5` / `c0…c3` (+`_pc`, `_farp`); 200 texture sets with `_n` + `_mers`; no flipbook file in the pilot RP |
| RP blocks.json sound | grass | the pilot RP has no blocks.json |

**States today's scripts depend on that the pilot lacks:**

| State | Read at (main.js) | Written at (main.js) |
|---|---|---|
| `pw:variant` | 1441, 3048, 3174, 3211, 3943, 4019 | 2152, 3053, 3064–3067, 3176, 3212 |
| `pw:rseed` | 3421, 3945 | 2154, 2673, 3067, 3320, 3660 |
| `pw:section` | 2112 | 2670 |
| `pw:exposure` | 2113, 2652, 3612 | 2671 |
| `pw:section_rolled` | 2111, 2148, 2650, 2716, 2767, 2893, 3029, 3041, 3420, 3617, 3944 | 2672, 3319, 3659 |

The pilot's `pw:pv` is read and written by no BP-02 code. Only TestRunner p15.js:206 writes it.

---

## Constraints for the replacement

Facts only, each with a file:line reference (`main.js` = `bp02-195/scripts/main.js`).

1. **Worldgen places default permutations.** All 22 BP-02 tree features place their leaf by `leaf_block.name` with no `states` (`features/*_tree_feature*.json`:29; `pw_jungle_bush_feature.json`:20). The placed permutation is the block's first-listed state values (today: `pw:variant` 0 etc., block lines 7–33).
2. **Feature ids must exist.** Feature `leaf_block` names and `may_replace` lists reference the exact ids `pw:oak/spruce/birch/jungle/dark_oak/pale_oak/acacia/cherry/mangrove_leaves` (§2 table; e.g. `pw_oak_mature_tree_feature.json`:29, 58–63). A block id that does not exist would break these features.
3. **Vanilla features are overridden.** Wrapper and vanilla-id features route all 9 species through the files in constraint 2: `oak/birch/spruce/jungle_tree_feature` (weighted), `acacia/cherry/mangrove_tree_feature` (direct overrides), and feature_rules `forest_sparse_oak/birch`, `taiga*/old_growth_pines`, `misty_dark_canopy`, `emerald_jungle_canopy`.
4. **onPlace does not cover worldgen.** The only placement hook is the `pw:randomize_variant` onPlace component, declared at block line 49 and registered at main.js:2172–2181. Code comments state worldgen leaves never get it (main.js:2039–2041, 2187). Adding `minecraft:random_ticking` to leaves broke block registration on PS5/Android (main.js:2033–2037, 3529–3531).
5. **Variety today is script-applied, random and not persisted.**
   - Scripts give variety after placement: Process A (main.js:2916–2974, 30 t, r 35) classifies, and phase-1 (main.js:2987–3106, 22 t, r 25, dy −40…+42) writes `pw:variant` from `Math.random()` pools (main.js:2118).
   - The pick is not position-seeded.
   - The applied map `_appliedRegistry` is in memory only (main.js:2833).
6. **Scripts read and write states the pilot does not declare.** The table in §6 lists every call. All are inside try/catch: `_markLeaf` (main.js:2666–2686), `pickVariantForBlock` (main.js:2110–2114), the cascade flush (main.js:3316–3321) and `reValidateExposure` (main.js:3612–3619, 3657–3662).
7. **`pw:pv` is unknown to BP-02.** No BP-02 code reads or writes it. The only writer is TestRunner p15.js:206.
8. **Far-render code works on `pw:variant` 0.** The far reverter (main.js:3152–3182) and re-applicator (main.js:3189–3218) write `pw:variant` 0 or a stored value for registry entries only. The phase-1 ">72 → v0" branch (main.js:3050–3057) is unreachable at its 25/42 radius (distSq ≤ 3,014 < 4,096). Separately, witness L-FAR-1 records that `alpha_test_to_opaque` switches to opaque in the distance on its own (decision_journal.md:1605).
9. **Felling finds leaves by exact id, not state or tag.**
   - Leaves are found by typeId: `SPECIES[i].leaves` + `EXTRA_LEAF_IDS` (main.js:60–86, 211–214, 632–634).
   - Tree gate: `endsWith("_leaves")` (main.js:413).
   - Leaves are removed with `setPermutation(air)` + manual loot rolls (main.js:767–769). No state is read except `pw:variant` for `ft:leaf_variant` (main.js:1441, 1462).
10. **Suffixed pilot ids fail the leaf-type checks.** `ft:leaf_variant` has range 0–6 (bp02 `entities/falling_tree.json`:100–107), and RP-01 picks the falling-canopy texture by `wood_type*7 + leaf_variant` (rp01 `render_controllers/falling_tree.json`:628, 648–733). Separately, many checks test `typeId.endsWith("_leaves")`: main.js:150, 300, 367, 413, 841, 871, 1073, 2107, 2139, 2636, 2851, 3248, 3631. An id with a suffix after `_leaves` (e.g. `pw:pilot_oak_leaves_bt`, `_far`, `_farp`, `_iso`) does not match these. The looser `indexOf("leaves")` checks (main.js:2885, 5148) would match it.
11. **Leaf-type sets are keyed on today's 9 ids.**
    - `PW_LEAF_TYPES` (main.js:2208–2222, which also contains 17 log tiers)
    - `PW_LEAF_TYPES_DECAY` (main.js:3543–3547)
    - `PW_LEAF_TO_WOOD_TYPE` (main.js:3550–3560; also used for felling shed at main.js:1581–1582)
    - `PW_VARIANT_COUNT` (main.js:2053–2064)
12. **Decay walks same-id leaves only.** Decay connectivity walks only through blocks with the same typeId as the start leaf (main.js:3704) and needs a `PW_LOG_TYPES` block within 6 steps (main.js:3563–3581, 3683–3701).
13. **RP-01 is the only pack with render data for today's ids.** It holds leaf geometry (`models/blocks/pw_leaves_variants.geo.json`, `pw_leaves_jungle_variants.geo.json`), 180 terrain keys, 96 texture sets, 156 flipbook entries and blocks.json sound "grass" (lines 12–78). No other RP in the RP-11…RP-01 stack defines any of these keys (§4).
14. **RP-01 leaf textures are also used by the falling-tree entity.** The entity (rp01 `entity/falling_tree.json`:54–65, 114–197) and the `pw_leaf_fall` particle (rp01 `particles/pw_leaf_fall.json`:8) use `textures/blocks/pw_<s>_leaves_v0…v2`.
15. **Leaf item behaviour comes from the block's loot table.** Leaf item and sapling drops on a manual break come from the block's `minecraft:loot` (block line 48 → `loot_tables/blocks/<s>_leaves.json`:14). The pilot declares no loot, flammable, `tag:plant` or `custom_components`, and uses a destroy time of 0.2 s against today's 1.9–2.2 s (§6).
16. **Permutation budget.**
    - Today: 168 per leaf block, 1,512 for the nine (block lines 6–33).
    - With `pw:pv` 0–8 alone the nine ids would carry 81.
    - History: >65,536 warnings at 66,343 / 66,346 (phase_log.md:275, 395); 1,512 after 1.3.195 (phase_log.md:1312–1315).
17. **Changed state sets in existing worlds are an unverified assumption.** Saved leaves in an existing world carry today's 5 states. The behaviour when a block's state set changes is logged as an ASSUMPTION ("reset to default permutation"; decision_journal.md:1462) and was exercised by p12 t01 (decision_journal.md:1511, 1525).
18. **TREEGROW structures are missing from the packs.** The saplings load `pw:test_<s>_young` (main.js:4907–4917, 5070), and those structures are not in any BP-02 build dir. Their leaf ids and states cannot be checked from files.
19. **Other packs only name vanilla leaves.** StripMine BP spawn rules, entities and scripts name vanilla leaves only (e.g. `spawn_rules/canary.spawn_rule.json`:14–15; `scripts/entity/Sloth.js`:50, 66–67). BP-01, BP-03 and Civitas reference no leaf block ids.
