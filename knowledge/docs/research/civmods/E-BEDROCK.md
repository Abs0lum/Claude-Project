# E-BEDROCK: Bedrock add-ons studied for CIVITAS (2026-10-06)

Group E-BEDROCK. Every item here runs on the same engine as CIVITAS (Bedrock, Script API, entity JSON). Each mechanism below was read from the file named next to it. "Not found" means I looked and it was not there.

Baseline CIVITAS facts I compared against (read in `/home/claude/tools/bp02_src_227/`):
- `pw_civ_clock.js` already has a dirty flag, saves the whole state as chunked JSON at most once per `SAVE_EVERY` (lines 188-197), and places staged buildings with `world.structureManager.place` (line 577).
- It runs about 11 separate `system.runInterval` loops (clock, kitqueue, room, walk, work, shop, watch …), each wrapped in `prof()`.
- It does not use `integrity`, `placeJigsaw`, `locatorBar` or scoreboards.

Version note: CIVITAS uses `@minecraft/server` 2.3.0. Some ideas below rely on APIs that these packs declare at higher versions (2.5.0, 2.9.0, 2.10.0, server-ui 2.2.0). Those ideas are marked **[needs version check]**.

---

### Jerry's Colonies 2.15.7 (Bedrock add-on, CurseForge; licence: none stated in the pack; `main.js` is deliberately obfuscated. Personal-use study only. Files examined: listed at the end)

- **What it does:** a player-run colony. The player places a flag (territory) and recruits NPC citizens. Citizens are assigned jobs at custom workstation blocks. There is a Mayor's Table UI, a player marketplace with treasury and customs, a research tree, blueprints placed from `.mcstructure`, plus alliances, war, elections, seasons, ageing, mood and hunger.
- **Manifest and size:**
  - BP 2.15.7: `min_engine_version` [1,21,0], `@minecraft/server` **1.5.0**, `@minecraft/server-ui` 1.3.0. RP: `min_engine_version` [1,16,0].
  - 34 entity files, 38 block files, 27 `.mcstructure`, 6 functions.
  - 51 JS files, about 1.94 MB in total. `main.js` alone is 658 KB on one line. It uses javascript-obfuscator's base64 string array; I decoded it locally for study (31,574 lines once pretty-printed).

**Mechanisms found**

- **Tick architecture**
  - `module/masterHeartbeatEngine.js` runs one `system.runInterval(…, 20)`. It increments `secondCounter` and fires task maps at 1 s, 5 s, 10 s, 30 s, 60 s, 5 min and 10 min (`secondCounter % N`).
  - It also detects day changes through `world.getDay()` and runs `tasksDayChange(currentDay, previousDay)`.
  - Every task runs inside its own try/catch (`executeTasksSafely`).
  - Registered tasks (decoded `main.js` around line 2739) include: hunger check (10 s), births (10 s), NPC taxes (60 s), the `save*` flushers (60 s), and food-crate validation (5 min).
  - `main.js` *also* keeps about 40 other `runInterval`s. Periods range from 2 ticks (knight sync, line 29513), 3 ticks (balloon ride), 5 ticks (balloon), 20, 40, 60, 100, 200, 400, 600, 1200, 6000 and 36000 up to 72000 (`processElections`, line 28615).
  - Many of these call `dimension.getEntities({type: …})` across the whole overworld.
  - A TPS/MSPT estimator runs every 20 ticks (line 305): `tps = min(20, 20*1000/(Date.now()-last))`, `mspt = delta/20`. It is only displayed in admin diagnostics (line 20244) and never used to throttle work.
- **Persistence (main.js 15377-15560)**
  - Each colony is saved under its own dynamic property `colony_data_<id>`, plus an index key holding the list of ids.
  - `saveColonyData(id)` only adds the id to `dirtyColonyIds`. A 20-tick flusher writes only those colonies, deletes keys of removed colonies, and rewrites the index.
  - It warns when one colony's JSON exceeds 30,000 characters ("close to the 32,767 limit") and messages the owner if a write fails.
  - `pruneStaleColonyRecords` trims `electionHistory` to the last 20 entries and drops tax and activity entries for non-members before each write.
  - Loading reads 10 colonies per tick, chained with `system.run(j)`.
  - `module/persistenceManager.js`: named dirty flags plus `executeIfDirty(flag, saveFn)`.
- **Per-citizen state on the entity itself**
  - `citizen.getDynamicProperty("stats")` holds JSON stats (`module/citizenStats.js:185`). Age and birth properties are in `agingSystem.js` (`age`, `jerry:birth_year`, `jerry:birth_day_of_year`).
  - Colony membership is stored as entity tags: `colony_id:<id>`, `colony_name:`, `colony_owner:`, `citizen_type:<job>`.
- **Citizen entity** (`entities/humanoid/citizen_male.json`, format 1.21.50)
  - Properties `jerrys:skin/hair/eyes/top/bottom` are ints with `math.random_integer` defaults and `client_sync`.
  - `minecraft:dweller`: village, inhabitant, `can_find_poi`, `first_found_penalty` 4.
  - Group `jerrys:dweller_logic`: `update_interval_base` 60 / `variant` 40, plus `minecraft:home` with `restriction_radius` 100.
  - `minecraft:scheduler` (5-10 s) and an `environment_sensor` on `is_daytime`. At night they add the `sleep` group: `behavior.sleep` p0, `move_to_poi` bed p1, `move_to_block` bed (range 48, height 12, tick_interval 10) p2.
  - `preferred_path` costs: stone/andesite/planks 0, grass_path 2, bed/lectern 50, default 10, jump 5.
  - Ages: `baby` (scale 0.5, ageable 1200 s), then `child` 0.7, `teen` 0.85, `adult` 1.0.
  - Job groups `jerrys:farm_work` / `builder_work` are just `move_to_block` toward that job's station block (range 32, goal radius 2, speed 0.8).
- **"Go here" pointer entity**
  - `entities/other/work_target.json`: gravity-free, 0.5 box, immune to damage, family `work_target`, despawns after 60 s while `idle`.
  - The citizen group `logger_work` points `nearest_attackable_target` (radius 64, `must_see:false`, tag `target_logger`), then `move_towards_target`, then `melee_box_attack` at it. This is the same idea as the CIVITAS lead carrot, driven by targeting goals instead of follow goals.
- **Routine switch (dead code)**
  - `tickCitizenRoutines()` (main.js 31274): time 12000-23000 = sleep, 5000-7000 = meeting, otherwise work. It fires `jerrys:start_work_<job>` events and stores `routine_state_key` on the entity so the same event is not re-fired.
  - It is defined but never called (grep finds only the definition).
- **Jobs are abstract, not bodily**
  - `ui/workstation/loggerStationUI.js:816` `tickLoggerPassive` runs every 600 ticks (skipped while raining). It harvests once per Minecraft day when `day > lastHarvestDay && timeOfDay >= 12000`.
  - Per worker, it rolls `max(1, stat)` d10s and keeps the best. The sum is multiplied by season × mood.
  - Each log consumes one tool "use"; axes keep vanilla durabilities (wood 59 … netherite 2031); tools are a FIFO.
  - Output goes to a linked chest, otherwise to `accumulated` (cap 500). The log type depends on biome; desert biomes produce nothing.
  - `module/stationConfig.js`: each station has `baseProductionMs` 15 min (research 25 min) and `maxWorkers` 2.
  - `citizenStats.js:323` `getProductionCooldown`: `mult = max(0.5, 1 - 0.4*primary/20 - 0.1*secondary/20) × seasonMultiplier`. `JOB_STATS` maps each job to a primary and secondary stat (logger force/endurance …). Stats run 1-20.
- **Farm zones** (`ui/workstation/farmerZoneManager.js:476`)
  - The player marks a zone (golden hoe, at most 16×16, station link at most 64 blocks).
  - A harvest is due every 2 days at `timeOfDay >= 5000`, or immediately if `day > lastDay + 2` (catch-up after sleeping).
  - Chunk guard: `dim.getBlock(centre)` must succeed.
  - It snapshots the ids of item entities already in the zone, harvests the blocks for real (`FARM_CROPS` table: growth state 7, beetroot mature at 3), then collects only the *new* item entities.
  - The zone count per station is capped by the number of workers.
- **Construction** (main.js 13662 `confirmBlueprintPlacement`, 31208 `tickConstructionSites`)
  - Before showing a preview, it saves the ground under the footprint with `/structure save` as a backup and restores it if cancelled.
  - On confirm it fills a coarse_dirt base, places a `construction_mark` block, and removes animals and NPCs from the site.
  - `structureScanner.js` builds a bill of materials: it scans the loaded preview at `SCAN_BATCH_SIZE` 500 blocks per tick (`runTimeout(scanBatch, 1)`), resolves colour states, excludes air, liquids, torches, signs, rails and plants, and caches the result per structure name in a dynamic property `building_scan_<name>`.
  - The site timer (every 200 ticks) adds real elapsed milliseconds **only while the colony has a builder** (`hasBuilderInColony`). The build finishes when `elapsedTime >= totalBuildTime*1000` (default `buildTime` 1200 s).
  - Blueprint size is clamped to 48³; the default cost is 10 emeralds.
- **Recruiting** (main.js about 4720)
  - Interacting with a free citizen checks the civilian cap: `flagLocations.length × getMaxCitizensForLevel(level)`.
  - Stages (`module/leveling.js`): COLONY lv1-10 = 10 citizens, CITY 11-20 = 15, KINGDOM 21-30 = 30.
  - The XP curve is base 100 × 1.15^level, up to level 30. `XP_REWARDS` include CLAIM_CITIZEN 10, BUILD_STRUCTURE 30, CITIZEN_DEATH −10, HUNGRY_CITIZEN −2.
  - The recruited citizen gets Resistance, is teleported to the flag, has `jerrys:reset_home` fired (re-adds the dweller group so it re-homes), gets tagged, and has its nameTag prefixed with the colony.
- **Mayor's Table** (main.js about 21144): a custom block. Interacting finds the nearest colony flag whose protection radius contains the player.
  - Capital radius is 50, raised by research to 65/80/100/120. City flags have their own ladder up to 80.
  - It then opens `showColonyManagementForm` (ActionFormData). There is a 1 s interaction cooldown per player.
- **Mood** (`module/moodSystem.js`): 0-1000, starting at 500.
  - Event deltas: WAR_WIN +150, FESTIVAL +200, BANQUET +50, NEW_BUILDING +25, FOOD_SATISFACTION +5, WAR_DECLARED −100, ASSAULT_LOSS −75, EPIDEMIC −25, FOOD_INSUFFICIENT −10, CITIZEN_DEATH −5.
  - Tiers: golden ≥800, satisfied ≥600, neutral ≥400, discontented ≥200, revolt <200.
  - Yield multipliers by tier: 1.20 / 1.10 / 1.00 / 0.75 / **0.0 (strike)**.
  - After a festival (3 days) yield is ×0.5; after a banquet (2 days) ×0.8.
  - Tier effects: Speed I at the top tiers; Weakness/Slowness II in revolt, IV below 10%.
  - Transitions are checked every 200 ticks.
- **Seasons** (`module/seasonSystem.js`): `DAYS_PER_YEAR` 120. Temperate seasons last 30 days; tropical biome set has dry/rainy seasons of 60 days. An admin day offset is kept in a dynamic property.
- **Hunger** (main.js 2551)
  - Checked twice per Minecraft day (periods `<12000` / `>=12000`), with the last day and period persisted.
  - Levels 0 FULL … 4 MALNOURISHED, 5 = death. Citizens eat from the nearest food crate.
  - Only colonies with an online member are simulated (`hasOnlineColonyMembers`).
- **Marketplace** (`module/marketplaceLogic.js`)
  - Keys: `marketplace_listings`, `…pending_money` (seller is paid while offline), `…colony_treasury`, `…customs_taxes[buyerColony][sellerColony]` (0-100%).
  - Currencies are a value-weighted list (iron 1, gold 5, emerald 10, diamond 20, netherite 100). `deductCurrency` and `giveCurrency` are greedy, highest denomination first. Coins convert at copper 0.5 / iron 1 / gold 2 emerald.
- **Market stall** (`module/market_stall.js`): a merchant spawns every 2 h real time and is removed after 15 min. Its spawn time is stored on the entity as dynamic property `spawned_time`.
- **Diplomacy and war**
  - `module/diplomacy.js`: relations ally/nap/neutral/enemy. Requests expire after 24 h real time. Default ally permissions: interact yes, place no, break no.
  - `module/warSystem.js`: war cooldown 200 real minutes, assault 1800 s, prestige 5 per win and 10 to conquer, vassal tax 5, `TERRITORY_RADIUS` 100.
  - Elections: plurality vote every 72000 ticks.
- **Research** (`ui/workstation/knowledgeTreeUI.js`): four DAG trees (military, production, logistics, defense). Nodes look like `{cost, requires:[…]}`. At most 3 active buffs. Research station base time is 25 min.
- **Cross-pack API**
  - `module/colonyEventEmitter.js` sends `system.sendScriptEvent("jcsu:colony_event", JSON)` on lifecycle events.
  - main.js listens for `jerrys_colonies:register_expansion` / `register_branch` / `register_node` script events (used by Empire Expansion, below).

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Per-town split save with a dirty-id set | Key `civ:town:<id>` plus an index (chunked like today). Flush only dirty town ids every 20 ticks. Prune histories (rumours, opinions, event logs) to the last N before writing. Warn at about 30k characters. Load N per tick. Replaces the whole-state write. | M | 4 |
| Abstract daily production with catch-up | When a worker's town is not near a player (or the job site's chunk is not loaded), settle output once per game day at a fixed time (`day > lastDay`). Roll per worker, scaled by skill/rank × mood × season, and consume tool "uses". Real-block work (felling, harvest) stays for near-player sites. | M | 5 |
| Mood tier → yield multiplier, strike at the bottom | Town-level mood 0-1000 with an event-delta table; yield multiplier 0/0.75/1/1.1/1.2; post-festival fatigue. Feeds our ledger. | S | 4 |
| Construction time accrues only while a builder is on site | Site timer adds elapsed time only if a builder body is present or assigned. | S | 3 |
| Bill of materials per template | Better done **offline**: compute block counts from our `.mcstructure` stage files in the Python build tool and ship them as data. The site then requires real goods from the ledger. | S | 4 |
| Terrain backup before a provisional placement | `structureManager.createFromWorld` (or `/structure save`) the footprint before a palace or district preview, and restore on cancel. | S | 2 |
| Script-event bus | `system.sendScriptEvent("civ:event", JSON)` for town lifecycle, so the gallery, codex or bridge can listen without imports. | S | 3 |
| Customs/tariff per town pair; pending payouts for absent parties | Fields in the town ledger. | S | 3 |
| Seasons calendar (120-day year) | A season multiplier on farm and wood output. | S | 3 |

---

### Empire Expansion 2.0.10 (Bedrock add-on for Jerry's Colonies, author "captainePro"; licence: none stated)

- **What it does:** an expansion pack for Jerry's Colonies. It adds 15 blueprint structures (bank, town hall, forge, hospital, houses, walls, gate, tower, barracks, church, storages, paved path), soldiers, cannons, an infirmary, random epidemics, resource boxes and a bank.
- **Manifest:** BP `min_engine_version` [1,21,0], `@minecraft/server` 1.15.0, server-ui 1.3.0. It depends on the Jerry BP uuid at version 2.15.7. 11 entity files, 12 block files, 15 `.mcstructure`, about 37 game JS files plus a bundled `node_modules` typings folder.

**Mechanisms found**

- **Registration into the host pack** (`scripts/structures.js`)
  - Blueprints are a JSON list (`typeId, structure, size {width,height,depth}, frontSide "max_z", requiredLevel, cost {item, amount}`). They are sent with `runCommandAsync("scriptevent jerrys_colonies:register_expansion …")` after 20 ticks.
  - The research branch and its nodes follow after 40 ticks (`register_branch` / `register_node`).
  - Other cross-pack calls: `scriptevent jc:add_xp`, `jc:reduce_food`, `jc:set_food`.
- **Database helper** (`features/dynamic_properties.js`): `Database.set` only writes when the value changed (`if (current === value) return`). It also has `updateJson(key, fn)` and `getJson` with a default.
- **Money** (`database/economy_config.js`): `MONEY_VALUES` copper coin 1, iron coin 24, gold coin 192, stacks 9/216/486, bags 72/1728/3888, diamond 192.
- **Resource boxes** (`database/resource_config.js`): containers that turn items into points by category, matched by item id or item **tag** (e.g. `minecraft:logs` = 1, `minecraft:is_food` = 2).
- **Epidemics** (`features/random_events.js`): `EVENT_PROBABILITY` 0.3 (marked as a test value).
  - Black plague: weakness + slowness, `spreadRadius` 6, `spreadChance` 0.35, `mortality` 0.06 per contagion cycle, 1 initial case.
  - Tuberculosis: radius 4, chance 0.12, 2 initial cases.
  - Dysentery: radius 2, chance 0.2, 4 initial cases.
  - Leprosy: not contagious, 3 initial cases, 24000-tick effect.
- **Performance:** `ui/war_table_ui.js` has several intervals doing `dim.getEntities({tags:["citizen_type:knight"]})` per dimension.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Building catalogue as data (size, front side, required tier, cost) | We have similar; adopt `frontSide` and `requiredLevel` fields per template. | S | 2 |
| Write-only-if-changed guard on dynamic properties | Compare the serialized string before `setDynamicProperty`. | S | 3 |
| Contagion events | Census-level: pick an index case, spread inside the household and to friends at chance p, mortality m. This uses our social graph instead of physical radius. | M | 3 |

---

### Village Ruler v2 (internal 23.0.2) (Bedrock add-on; licence: none stated)

- **What it does:** turns vanilla villages into managed settlements.
  - A "core" villager is the persistent anchor. Villagers get roles. The village gains tiers from Village to Capital, a government (tax, rationing, immigration, trade policy), build orders placed block by block by a builder villager, caravans between owned settlements, events, diplomacy and army marches.
  - It disables vanilla trading for managed villagers.
- **Manifest:** BP/RP 23.0.2, `min_engine_version` **[1,26,30]**, `@minecraft/server` **2.9.0**, server-ui 2.1.0. One `scripts/main.js` (81 KB, 720 lines), one item, three functions, no custom entities (uses `minecraft:villager_v2`).

**Mechanisms found** (`scripts/main.js`)

- **State lives on an anchor entity.** The settlement JSON is stored on the core villager: `core.setDynamicProperty("living_ai:settlement_v23", …)` plus a stable id `"<dim>_<x>_<z>_<rand>"`, with an in-memory cache.
  - Workers carry `living_ai:worker_settlement_v23` as an entity dynamic property and role tags `living_ai_role_<role>`.
  - A world index of up to 128 cores is kept in `living_ai:core_index_v2301`.
  - Only *loaded* settlements are simulated: `loadedCores(r)` = `getEntities` around each player at radius 190-260, filtered for the core tag.
- **Core protection:** `beforeEvents.entityHurt` is cancelled for the core, and it gets Resistance 255. `beforeEvents.playerInteractWithEntity` is cancelled for managed villagers, which blocks the vanilla trade UI and opens the planner menu instead.
- **Locator Bar** **[needs version check: 2.9.0]**: `player.locatorBar.removeAllWaypoints()`, then `addWaypoint(new EntityWaypoint(entity, {textureBoundsList:[{lowerBound:0, texture:WaypointTexture.SmallStar}]}, {showDead:false, …}, color))`, or `LocationWaypoint` for unloaded cores. Runs every 80 ticks.
- **Tier ladder** (`TIER_REQUIREMENTS`):

  | Tier | Population | Happiness | Buildings required |
  |---|---|---|---|
  | large_village | 8 | 40 | 1 home + 1 farm |
  | town | 15 | 45 | 2 farms + a meeting/trade building |
  | large_town | 25 | 50 | defense + forge |
  | city | 40 | 60 | City Hall + market + barracks |
  | capital | 60 | 70 | City Hall + Trade Exchange + 2 trade routes |

  - Territory radius by tier: 96/112/128/144/160/192.
- **Needs model** (`recalcSettlement`):
  - `food = resources.food/(pop*2)`, `housing = capacity/pop`, `employment = employed/pop` (all ×100, clamped).
  - `security = 25 + guards*7 + towers*8 + guardBudget*0.25 − warWeariness`.
  - `prosperity = (happiness + food + security + min(100, tradePower*12))/4`.
- **Economy tick** (every 600 ticks):
  - Production: food += farmers×2 + farm×3; wood += lumberjacks×2 + builders + camp×5; and so on.
  - Consumption: `ceil(pop*0.18*rationing)`, with rationing generous 1.35 / strict 0.65.
  - Tax income: `floor(pop*tax/100*0.35)`.
  - Happiness delta: +1 if quality ≥75, −2 if <40, −1 if <55; minus `(tax−15)/10`; ±1 for rationing.
  - Every 10 economy ticks, if immigration is open, happiness ≥72, food ≥ pop×2 and capacity > pop, a new family spawns.
- **Events** (every 1200 ticks):
  - Base chance 0.16, +0.12 if happiness <35, +0.1 if security <35, +0.05 if emeralds >40, clamped to 0.1-0.42. Cooldown 2-5 ticks of the event loop.
  - Event table by roll: bandit raid with stolen emeralds, festival, crop blight, mine collapse, wealthy merchant, tax revolt, community project.
- **Caravans:**
  - Profit: `max(2, floor((tpA+tpB+2)*(1+min(2, dist/300))*(0.6+safety/200)))`.
  - Safety: `clamp(round((security + roads*4 + (protected?20:0))/1.2), 10, 100)`.
  - Ambush roll every 10 steps: `random > 0.92 + safety/1250` spawns pillagers.
  - A failed route goes to cooldown 10 and costs −3 happiness.
- **Builder** (`tickBuild` every 6 ticks): the blueprint is a script-generated block list (`makeBlueprint`). The builder walks to each block with `teleport` steps of 0.42 blocks per tick and `facingLocation`. If not closer after 12 checks it is teleported. Then `setblock` places the block, and the state is saved every 20 blocks.
- **Worker "lives"** (every 40 ticks): during work hours (time 1000-11500) each role steps toward the matching building, otherwise toward a hashed spot near the core. Movement is a teleport step of 0.28-0.38. Particles mark work.
- **Cost profile:** six or more tickers each call `loadedCores()`, which does `getEntities` per player at radius up to 260. `tickBuild` rebuilds the entire blueprint list every 6 ticks.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Tier gates = population + happiness + required building set | Formalise our I→III growth gates as a table checked once per day. | S | 4 |
| Needs model (food/housing/employment/security → prosperity) | Derive from the census and ledger each day; drive migration and growth. | S | 4 |
| Caravans between towns (route safety from security and roads) | A trade route record in the ledger; a caravan entity walks our route graph between towns; profit and ambush formulas as above. | M | 4 |
| Government knobs (tax, rationing, immigration, trade policy) | Town fields that scale existing ledger flows and mood. | S | 3 |
| Locator Bar waypoints for towns and palace | **[needs version check: 2.9.0]** `LocationWaypoint` per town for players. | S (after upgrade) | 3 |
| Lesson: keep town state off a single anchor entity | Theirs is lost if the core dies and is only visible when loaded. Our world-level state is the right choice. | – | (lesson) |

---

### Hardworking Villagers 1.0.4 (Bedrock behaviour pack, author ItsMeXD; licence: none stated)

- **What it does:** overrides vanilla `villager_v2` to lengthen work hours. Three subpacks: Normal, No Afternoon Break, No Break At All.
- **Manifest:** `min_engine_version` [1,14,0]; data module only; 3 subpacks (`memory_tier` 0); each holds one `entities/villager_v2.json` (format 1.21.20).

**Mechanisms found** (vanilla schedule format, from `subpacks/*/entities/villager_v2.json`)

- The scheduler `scheduled_events` use `hourly_clock_time` windows; `min_delay_secs` 0, `max_delay_secs` 10.
- Work windows per subpack:

  | Subpack | Work | Gather (mingle) | Work | Home | Bed |
  |---|---|---|---|---|---|
  | Normal | 0-8000 | 8000-10000 | 10000-11000 | 11000-12000 | 12000-24000 |
  | No afternoon break | 0-11000 | – | – | 11000-12000 | 12000-24000 |
  | No break at all | 0-24000 work | – | – | – | – |

  - Applies to `work_schedule`, `farmer_schedule`, `fisher_schedule` and `librarian_schedule`.
- Other schedules: jobless wanders 2000-13000, goes home 13000-14000, sleeps otherwise. Children play 0-11000.
- Each `minecraft:schedule_*` event swaps component groups:
  - `work_schedule_farmer` = `behavior.work_composter` (p9, active_time 250, goal_cooldown 200, `can_work_in_rain` false) + `harvest_farm_block` p7 + `fertilize_farm_block` p8, plus shareables (bread want 3; wheat crafts into bread).
  - `work_schedule_villager` = `behavior.work` (p7, active_time 250, goal_cooldown 200, sound delay 100-200).
  - `gather_schedule_villager` = `behavior.mingle` (duration 30, cooldown 10, distance 2).
  - `bed_schedule_villager` = `behavior.sleep` (p3, goal radius 1.5).

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| A cheap engine-side "market hour" | If our `villager_v2` groups keep any vanilla goals, a `hourly_clock_time` scheduler can switch component groups with zero script. Our script clock already owns schedules, so this is a fallback for distant, unscripted villagers. | S | 2 |

---

### Guard Villagers 1.1.0 ("GuardVillager12", Bedrock add-on; licence: none stated)

- **What it does:** whenever a villager spawns from village generation, a soldier or crossbow guard also spawns next to it. Also adds medics, a juggernaut, shields and tameable guards.
- **Manifest:** BP `min_engine_version` [1,21,130], `@minecraft/server` **2.7.0**, server-ui 2.0.0. 11 entity files; `scripts/main.js` (import only) and `scripts/custom/soldierspawn.js`.

**Mechanisms found**

- **Spawn hook** (`soldierspawn.js`): `world.afterEvents.dataDrivenEntityTrigger` filtered on `eventId === "minecraft:spawn_from_village"` and `minecraft:villager_v2`.
  - Up to 18 attempts at random offsets of about ±8.
  - A position is accepted when the feet and head blocks are air/light_block, the floor is not air, and neither the floor nor the feet block contains `bed` / `carpet` / `slab` (avoids heads stuck in ceilings).
- **Guard AI** (`entities/villager_soldier.json`, format 1.17.0)
  - `alert_for_attack_targets`: illager/zombie/monster except phantom and enderman, radius 40, max distance 20, `must_see`.
  - `minecraft:raid_configuration` group: dweller role **defender**, `move_towards_dwelling_restriction` p4, `move_through_village` p4 (`only_at_night` false), `random_stroll` xz 36, `preferred_path` (grass_path 0, stone family 1, default 1.5).
  - Stand-post versus patrol: event `set_home_here` adds `go_home` (interval 200, goal radius 4, speed 0.6); event `patrol` removes it.
  - Biome variants are chosen in `entity_spawned` by `has_biome_tag`. Shield logic uses `environment_sensor has_equipment shield` and a 1-2 s cooldown timer.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Safe-spawn test (no bed/slab/carpet under or at the feet; 2-high air) | Reuse in our spawn and arrival placement. | S | 3 |
| Post / patrol toggle via home + `go_home` group | Watchman "stand at gate" versus "walk round" as two component groups switched by event. Cheap when the body is far from players and the script is not driving it. | S | 3 |

---

### Village Guards 1.16.1 (Bedrock add-on, author Deedubbs; licence: none stated)

- **What it does:** some villagers spawned with villages become guards or archers; players can hire them with a hoe.
- **Manifest:** BP `min_engine_version` [1,13,0]; data only, no scripts. Entities `villageguards:guard`, `villageguards:archer`, and an edited `villager_v2`. The archive also contains a stale `bridge/cache` copy.

**Mechanisms found**

- **Conversion** (`entities/villager_v2.json` `minecraft:spawn_from_village`): randomize weight 15 = guard, 85 = normal. Inside the 15: guard 75 / archer 25. Groups `become_guard`/`become_archer` = `minecraft:transformation` (delay 0.5) + regeneration 100.
- **Guard** (`villageguard.guard.json`, health 80): group `guard_village` = dweller **defender** (`can_migrate`), `move_through_village` p3 with **`only_at_night: true`**, `move_towards_dwelling_restriction` p4, target radius 12 (monster/illager/zombie, not creeper), `preferred_path`.
- **Hire:** `on_hire` replaces `guard_village` with `hired` (`is_tamed`, `follow_owner` 10→2, `owner_hurt_*`, `sittable`). Triggered by interaction holding any hoe.
- **Archer:** health 60, `ranged_attack` interval 1-3, radius 15; ranged/melee mode events.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Night watch with no script | A watchman component group with `behavior.move_through_village {only_at_night:true}` plus defender dweller. The engine walks village paths at night. Use it when no player is near (script patrol off). | S | 3 |

---

### Village Generator 2.4.0 (Bedrock function pack, author Th3Emilis)

- **Licence (`bp/LICENSE.md`):** attribution required; **no redistribution**; non-commercial; **no derivatives shared**; "remix … for your own private use" allowed; "not … use any part … in other add-ons". So: study ideas only, copy no files.
- **What it does:** places vanilla-style villages instantly on flat worlds, or piece by piece (streets, terminators, town centres, houses) via `/function`.
- **Manifest:** `min_engine_version` [1,21,80]; data only. 822 `.mcfunction`, 469 `.mcstructure`, no scripts.

**Mechanisms found**

- **Turtle cursor:** `summon epicth3emilis:vg_helper … minecraft:entity_spawned <name>`, then `spreadplayers ~ ~ 0 1` snaps it to the ground (`bp/functions/vg/instant/plains_1.mcfunction`).
  - Every step reads the helper's yaw quadrant (`ry=-45,rym=-135` etc.) and does a rotation-specific relative `tp`, then calls a piece function.
  - Sub-rotations summon a temporary helper at `~90`.
- **Rotation anchor table** (`bp/functions/vg/plains/houses/accessory.mcfunction`, `vg_technical/instant/plains_1/street_1.mcfunction`): a footprint of size X×Z loads at
  - 0°: (0, 0)
  - 90°: (−(Z−1), 0)
  - 180°: (−(X−1), −(Z−1))
  - 270°: (0, −(X−1))

  This keeps the helper as the same corner. Example: street_1 is 3×14, giving (0,0) / (−13,0) / (−2,−13) / (0,−2).
- **Weathering by integrity** (`bp/functions/vg/taiga/zombie/houses/weaponsmith_1.mcfunction`):
  1. Load the house.
  2. `structure save temp` the volume.
  3. `fill … mossy_cobblestone replace cobblestone`, or web, broken panes, potatoes/pumpkin stems for wheat.
  4. `structure load temp … 0_degrees none true true false <integrity>` with integrity 20 / 50 / 70 / 80 / 92. This restores only that percentage of the original blocks, so the rest stay changed.
  5. Repeat per material, `structure delete temp`.
  6. Finally load a `_part` overlay (pieces that must stay intact).

  Plains houses mossify cobblestone the same way.
- **Population** (`bp/functions/vg/populate.mcfunction`): 6 villagers `spawn_from_village` + `spreadplayers 4 48`; 3 cats `spreadplayers 8 48`; 1 golem within 12.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Age and weathering by integrity | After a stage places, call `world.structureManager.place(id, dim, loc, {integrity: 0.2-0.9, integritySeed: <buildingId>})` with a **weathered variant** of the template, over the clean one. Older buildings, conversions and ruins get deterministic per-building decay (moss, cracked bricks, broken panes, cobwebs in abandoned houses). | S | 4 |
| Rotation anchor formula | Cross-check our `ROTS` placement offsets against the table above. | S | 2 |

---

### Human Companions 1.7.0 (Bedrock add-on; licence: none stated)

- **What it does:** human NPC classes (viking, archer, lancer, crossbowman, explorer, gentleman, general assistant …) as tameable companions, with banners as base points, torches and lights, shields, water handling and pets.
- **Manifest:** BP `min_engine_version` [1,21,23], `@minecraft/server` 1.5.0, server-ui 1.2.0. 27 script files, 9 human entity files of about 70-98 KB each, plus projectiles and items.

**Mechanisms found**

- **Dynamic light** (`scripts/LightHuman.js`): every 2 ticks, for `survivor_human:general_assistant` with tag `light_15` / `light_10` / `light_8`, it places a light block at the head position. It only places in air or water, avoids gravity blocks around, and remembers the last position per entity in `entityLights` to clear it when the entity moves.
- **One-shot decisions persisted by tag** (`scripts/SpawnHumans.js`): every 15 ticks, `getEntities({families:["villager"], excludeTags:[PROCESSED_TAG]})`. Each villager is tagged immediately and gets a single 10% roll to spawn a human. The engine filter means each villager is evaluated once, ever.
- **Gender by a borrowed component** (`main.js`): `entity.getComponents().some(c => c.typeId === "minecraft:is_ignited")` selects the male or female name list (a JSON-side flag reused as a marker).
- **Cost profile (anti-patterns):**
  - Many 1-tick intervals over all three dimensions: `WaterDrop.js` (unfiltered `dimension.getEntities()` every tick), `PreCompanion.js`, `RunAndJumps.js`, `SneakCompanion.js`, `Spiderwebs.js`, `WolfCompanion.js` ×2, `CatCompanion.js`, `EntityEquippableComponent.js`.
  - Also `DistanceMovement.js` every 2 ticks and `BannerBase.js` every 5.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Watchmen carry lanterns at night | Move a `minecraft:light_block` (level about 10) with each *nearby* watchman every 4-10 ticks. Only place into air, clear the previous block, cap the number of lit carriers. | S | 3 |
| `excludeTags` processed-tag pattern | For one-time census registration of vanilla villagers that wander in: the engine filters, script work happens once. | S | 3 |
| Lesson | Never run per-tick, all-dimension `getEntities()`. | – | (lesson) |

---

### Kingdom Constructor: Iron Age 1.1 (Bedrock add-on, CurseForge; licence: none stated)

- **What it does:** four factions (woodsman, stoneguard, ironguard, barbarian) with camps and towers generated in the world. Units are recruited with items and commanded (follow / guard post / tower / patrol) by holding command items and placing faction blocks.
- **Manifest:** BP `min_engine_version` [1,16,0], data only (no scripts). 10 entity files, 25 block files (flags, guardposts, towers, 2 patrol points per faction), 48 `.mcstructure`, feature + feature_rule pairs, 17 spawn functions.

**Mechanisms found**

- **JSON-only patrol** (`entities/woodsman.behavior.json`):
  - `kingdom:on_patrol_1` = `move_to_block` toward `kingdom:woodsman_patrol_point_1` (search range 64, height 32, `tick_interval` 1, goal radius 1, speed 0.5), with `on_reach` firing event `kingdom:on_patrol_2`, and the mirror group back. The unit ping-pongs between two marker blocks with no script.
  - `is_guard` = `move_to_block` toward the guardpost (`tick_interval` 20, goal radius 5) + `random_stroll`.
  - `is_tower` = `move_to_block` toward the tower block (goal radius 1).
  - `idle_behavior` = `move_to_block` toward the faction flag, goal radius 10.
- **Loyalty tiers:** `is_loyal` / `_weak` / `_mid` / `_strong` raise the targeting radius 16/18/20/22 and tempt speed 0.5-1.0, unlocked by interacting with an `upgrade` item.
- **Worldgen** (`feature_rules/woodsman16x16_4_feature_rule.json` + `features/woodsman16x16_4_feature_mcstructure.json`):
  - `surface_pass`, biome filter forest (and not ocean/river/…).
  - `scatter_chance` 0.15, iterations 1, `y = query.heightmap(...) − 4`.
  - `structure_template_feature` with `adjustment_radius` 8 and constraints `grounded` + `unburied`.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Waypoint ping-pong with `move_to_block` + `on_reach` | A JSON fallback patrol for watchmen between gate and tower marker blocks. **Use `tick_interval` ≥ 10 and a small search range:** their `tick_interval` 1 with range 64×32 is a heavy block search. | S | 2 |
| Satellite hamlets by world feature (`adjustment_radius`, grounded/unburied) | For new chunks only; CIVITAS grows on existing terrain. | M | 1 |

---

### Smart Villager Addon v1.0.2 and v1.0.3 (Bedrock add-on, "Renderphoenix Creatives")

- **Licence (manifest metadata):** "all rights are reserved, no permission for third party distribution". Study only.
- **What it does:** vanilla villagers perform their jobs physically.
  - Fishermen walk to water and cast an animated bobber; farmers harvest, replant, compost and plant flowers or saplings; shepherds shear; butchers hunt and smoke; fletchers shoot targets; clerics heal; armorers repair golems; librarians buff.
  - All villagers collect dropped items, sort chests, and place beds and workstations to expand the village.
- **Manifest (both archives):** header version **[1,0,2] in both** (v1.0.3 did not bump it). `min_engine_version` [1,21,0], `@minecraft/server` **1.13.0**, no server-ui.
- **Size:** 28 JS files (1.0.3: about 650 KB). Entities: `villager_v2.json` (147 KB → 151 KB), `iron_golem.json`, `fishing_bobber.json`.

**Mechanisms found** (v1.0.3 unless stated)

- **Central staggered loop** (`scripts/main.js`):
  - One `runInterval(…, 2)` with `phase = tick % 4`.
    - Phase 0: fisherman + farmer.
    - Phase 1: shepherd + expansion + population.
    - Phase 2: butcher + fletcher + weaponsmith.
    - Phase 3: cleric + armorer + librarian.
  - So each manager updates every 8 game ticks, and never two heavy groups in the same tick. Each manager is wrapped in try/catch.
  - Extra loops: occupation sync every 100 ticks over all overworld villagers (`getEntities({type:"minecraft:villager_v2"})`), which also consumes `rpc:event_*` tags as a command channel; unreachable-target prune every 100 ticks.
- **Per-villager state machines** (`fishermanManager.js`): `records` Map keyed by entity id, with states IDLE / APPROACHING_* / FISHING / COOKING_CAMPFIRE / FEEDING_CAT / RESTOCKING_POND / SLEEPING / COOLDOWN.
  - New fishermen are found every 30 manager updates.
  - IDLE re-plans every `SEARCH_INTERVAL_TICKS` 20 updates. It rotates a 5-step search (near water → stray cat r14 → campfire r18 → pond r14 → river or water within 48) and takes the first hit.
  - At night it stops and fires `minecraft:schedule_bed_villager`.
- **Movement, three methods**
  1. **Native goals switched by component group** (`entities/villager_v2.json`):
     - `rpc:approach_smoker` = `move_to_block` [smoker, lit_smoker] (range 32, height 12, goal 2, `tick_interval` 1).
     - `rpc:approach_target` = `move_to_block` target block (range 24).
     - `rpc:shepherd_approach_sheep` = `follow_mob` sheep (range 32, stop 1.8).
     - `rpc:butcher_hunt_prey` = `nearest_attackable_target` cow/pig r24 + `melee_attack`.
     - `rpc:fishing_mode` = `minecraft:movement 0.0` (pins the villager while fishing) + mainhand drop chance 0.
  2. **Impulse steering** (`utils.js:94 smoothMoveTowards`): face the target, read `getVelocity()`, and `applyImpulse` of `clamp(maxSpeed − dot, 0.012, 0.045)` toward the target. Max speed 0.13, stop distance 1.2. Straight line, no pathfinding.
  3. **Progress watchdog** (`pathfinder.js`): reached when water is within 2.8 blocks; stuck if it moved less than 0.04 for 120 checks; timeout 600 checks.
- **Unreachable blacklist** (`utils.js:154`): `markTargetUnreachable(target, 400 ticks)` keyed by entity id or block x,y,z. Searches skip blacklisted targets; it is pruned every 100 ticks.
- **Scan costs** (computed from `waterScanner.js:186` and `config.js` `SCAN_CONFIG` radius 48, step 4):
  - `findBestFishingSpot` samples rings r = 6…46: 9+15+21+26×8 = **253 columns**. Each `findWaterSurfaceY` reads up to 23 blocks (y −16…+6).
  - In v1.0.3, each water column also costs `isFarmWater` (26 reads) plus a stand-spot search (8 neighbours × 3 dy × 3 reads).
  - Worst case is about **5,800+ `getBlock` calls in one tick**, with an early exit once a river is found at r ≥ 16.
  - Farmer searches are cheaper (`farmerBehavior.js:58`): concentric squares to radius 14 on a **stride-2 grid** (every other column), dy −2…+2, first match wins (about 300 reads worst case).
- **Real block work** (`farmerBehavior.js:290 performHarvest`): face the crop (`teleport` with rotation), `playAnimation("animation.villager.raise_arms")`, spawn 1-2 produce and 1-2 seeds, `setPermutation(growth 0)` (replant in place).
- **Village expansion** (`villageExpansionManager.js`):
  - Beds, chests and workstations are placed by villagers with randomized cooldowns: bed and chest 18000-30000 ticks, workstation 3600-6000.
  - Search radii 64; item pickup radius 12.
  - Placements are throttled per **48×48 sector** (`key = dim:floor(x/48),floor(z/48)`, real-time expiry, default 20 min).
  - A shared POI cache Map `dim:x,y,z → typeId` speeds up 64-block scans.
- **Population** (`villagePopulationManager.js`): a world dynamic property `rpc:populated_villages` holds village centres. A new village needs at least 100 blocks of separation.
- **v1.0.2 → v1.0.3 diff** (`diff -r`):
  - Radii and cooldowns shrank in `config.js`, all reductions in per-tick search and effect area:
    - weaponsmith buff radius 12→4, cooldown 200→300
    - cleric ally search 28→14, heal distance 8→2.5
    - raid search 24→20, offensive search 16→12, throw distance 12→8
    - zombie-villager search 28→20, sanctuary 8→4.5
    - armorer buff 10→4, cooldown 300→350
    - librarian inspiration 12→3.5, dispel 12→8
  - Fishing: farm-irrigation water rejection, a strict forward cast cone (±0.8 rad instead of ±π), near casts first (3-7) then 8-12, and a proper stand-on-ground search.
  - Logistics: caught and cooked fish now go into a virtual `carriedItems` list on the expansion record (deposited to a chest later) instead of being dropped as item entities.
  - `professionHelper.js`: explicit `rpc:<job>` tags now outrank the vanilla `variant`. A new `isVillagerBusyWithProfession()` stops expansion chores from interrupting job states.
  - `main.js`: also fires `rpc:become_<job>` for farmer, weaponsmith, cleric, armorer and librarian.
  - Entity: 5 new `rpc:become_*` events; `fishing_mode` changed.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Phase-staggered dispatcher | One dispatcher assigns each CIVITAS subsystem (clock, walk, work, shop, watch, kitqueue, room) a fixed phase slot, so no two heavy systems share a tick. Today several 20/40-tick intervals can coincide. | S | 5 |
| Pin a worker in place with `movement 0` | A component group `civ:at_post` (shopkeeper at counter, clerk on square, fisherman on bank). Stops drift without per-tick teleports. | S | 4 |
| Unreachable-target blacklist with expiry | `Map key → expiryTick` for build sites, trees and water spots that failed A* or stalled. Skip them in planning. | S | 4 |
| Busy-arbitration between job state and chores | One `isBusy(person)` check before any secondary task is assigned. | S | 3 |
| Virtual carried inventory, deposited at a chest or counter | Matches our ledger: goods are counted on the person record, then moved into stock on arrival. No item entities. | S | 3 |
| Sector-keyed cooldowns (48-block cells) for world edits | For conversions and park trees, so edits cluster less. | S | 2 |
| Lessons | Big ring scans (thousands of `getBlock`) must go into `runJob` generators or be precomputed (e.g. a shoreline list from the land survey). Use stride sampling and early exit for small searches. | – | (lesson) |

---

### Lively Villagers 1.8.0 (Bedrock add-on, author ShowdownMan; Data + Resources packs; licence: none stated)

- **What it does:** replaces vanilla villagers, wandering traders and witches with custom male and female humanoids. Adds names, personalities, favourites, gifts, relationship scores, chat/joke/compliment/flirt dialogue and a custom-styled form UI.
- **Manifest:** Data `min_engine_version` [1,20,0], `@minecraft/server` **1.15.0-beta**, server-ui 1.4.0-beta. RP `min_engine_version` [1,20,20]. 4 JS files, 5 entity files.

**Mechanisms found**

- **Replacement** (`scripts/Main.js`): on `entitySpawn` of `minecraft:villager_v2`, it summons `bca:villager_female` or `_male` and `tp @s ~ ~-100 ~` (pushes the original into the void).
- **Identity:** on spawn of a custom villager, a random name, one personality tag from `shy / energetic / rude / flirty / vain`, and scoreboard randoms `favorite_food 0-6` and `favorite_color 0-15` (`LVGlobalVariables.js`).
- **Relationship** (`LVFunctions.js:459 give_gift`):
  - One **scoreboard objective per player** (`relationship_<playerName>`, `flirt_<playerName>`), with the villager as participant.
  - Gift points by category table (golden apple 5, cooked meat 2, raw 1 …), +1 if the category matches `favorite_food`.
  - Friends at ≥25; can "ask out" at flirt ≥5.
  - Dialogue lines are chosen by personality.
- **Freeze during conversation:** event `cant_move` = `minecraft:movement 0`; `can_move` on hurt or close.
- **Form theming by title flags** (`VillagerGUI.js` + RP `ui/server_form.json`):
  - The title is `'custom_ui' + 'villager_ui' + is_friends + can_ask_out`.
  - The RP's server_form binding tests `(#title_text - 'custom_ui') = #title_text` and swaps to `lively_villagers_ui.villager_ui`, which shows or hides buttons from the flags embedded in the title.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Personality + favourite + gift affinity per person | Add `personality` and `favourite` fields to census records. A gift raises opinion of the giver by a table amount, +1 on favourite. Use our census, **not** per-player scoreboard objectives (those scale badly and use player names). | S | 3 |
| Conversation freeze | Same `movement 0` group as the Smart Villager pin. | S | 3 |
| Title-flag JSON UI theming | An RP `server_form.json` override keyed on a title prefix such as `civ_ui:` to give ledger and census forms a custom layout. | M | 2 |

---

### Quests & Guards 0.0.1 (Bedrock add-on, "KZBMM, part of Better Adventures"; licence: none stated)

- **What it does:** a quest board block gives gather or hunt quests. Fletchers can be promoted to archer guards. Villagers get biome-specific names.
- **Manifest:** server BP `min_engine_version` [1,20,30], `@minecraft/server` **1.10.0-beta**, server-ui 1.2.0-beta. 18 JS files, 5 entity files.

**Mechanisms found**

- **Quests** (`scripts/quests.js`, `libraries/quest/QuestClass.js`, `questConstants.js`):
  - Gather 2-6 of a random item from 17, or hunt 2-6 of 6 mob types. Quest text comes from 6 templates.
  - State lives on **player dynamic properties**: `better:activeGatherQuest` (JSON), `better:is_questing_*`, `better:hunt_quest_killed_entities` (incremented in `entityDie`).
  - Completion is checked against the inventory and pays a "complete" token item.
- **Board block** (`blocks/questboard.json`): state `has:quests` [1,0]; a `give_quest` event with randomize.
- **Names** (`entity_names/villager_names.js`): male or female from `skin_id`. The **village type** comes from `minecraft:mark_variant` (1 desert, 2 jungle, 3 savanna, 4 snow, 5 swamp, 6 taiga, default plains) and selects a regional name pool.
- **Guards:** `villager_v2` events `minecraft:promote_to_archer` (weight 99) transform fletchers. Warrior entity: dweller defender, `move_towards_dwelling_restriction`, tempt by gold/diamond/netherite sword or emerald.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Town notice board = requests generated from real shortages | Our ledger knows which goods are short, so the "gather N X" text comes from actual needs. Reward is coin from the town treasury. Store the active quest on the player dynamic property. | S | 3 |
| Regional name pools by biome or village style | A `townStyle` field picks a name list. | S | 2 |

---

### Villages Plus v0.7 (Bedrock add-on, author JERA; three BP/RP pairs: base, Increased Structures, Classic plugin; licence: none stated)

- **What it does:** adds 19 data-driven jigsaw structures (14 village styles plus illager camps) to world generation, with self-ticking "spawner" marker blocks that populate them.
- **Manifest:** each BP `min_engine_version` [1,21,120], `@minecraft/server` **2.5.0**. Each RP declares `capabilities: ["pbr"]`. 1,897 `.mcstructure` across the three packs.

**Mechanisms found**

- **Jigsaw structures** (`worldgen/structures/*.json`, format 1.21.20):
  - `step: surface_structures`, `heightmap_projection: world_surface`, `start_height` 0 (beach −34, mangrove/swamp −30).
  - `max_depth` 16-20.
  - `terrain_adaptation`: `beard_box` for 18 of 19, `bury` for beach.
- **Structure set** (`worldgen/structure_sets/villages_plus_set.json`): `random_spread`, triangular, salt 48392015.
  - Base: spacing 46 / separation 18.
  - Increased: spacing 25 / separation 12.
  - Weight 2 each.
- **Template pools** (`worldgen/template_pools/village/timber/*.json`):
  - The `street_initial` piece and T-junction pieces use **`projection: terrain_matching`** (each column follows the ground).
  - Long streets and all houses and buildings are **`rigid`**.
  - Fallback pools exist for streets and houses.
- **Processor lists** (`worldgen/processors/*.json`): present but with empty `rule` lists.
- **Self-ticking spawner blocks** (`scripts/main.js` + `blocks/villages_plus/*.json`):
  - The block has `minecraft:tick {interval_range:[20,20], looping:true}` and a custom component registered in `system.beforeEvents.startup` → `blockComponentRegistry.registerCustomComponent`.
  - On tick: if `doMobSpawning` is on and a player is within 20 blocks (45 for the miniboss), spawn the entity or entities. The villager spawns with `spawnEvent: 'minecraft:spawn_from_village'`. Then `block.setType('minecraft:air')`.
  - The miniboss block calls **`world.structureManager.placeJigsaw('rev:illager_miniboss', '', 1, dimension, location)`** from script.
  - Pillagers spawned this way carry a tag that drops 1-3 emeralds on death.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Marker blocks inside templates | Put invisible `civ:mark_*` blocks (counter, bed, workstation, door, NPC spawn, lamp post) in our stage `.mcstructure`. After `structureManager.place`, scan only the stage volume (or let a ticking custom component report itself), register positions in the town record, then replace the marker with air or the real block. Removes hand-kept per-template coordinates. | M | 4 |
| `placeJigsaw` from script | **[needs version check: declared at 2.5.0, we are on 2.3.0]** Grow a district or hamlet from a jigsaw pool at runtime. Street pieces use `terrain_matching`, houses stay `rigid`. A possible future engine for outer districts; our kit planner stays primary. | L | 3 |
| Street-vs-building projection split | Our contour lanes already follow terrain. Keep houses rigid on levelled pads, streets column-matched. The vanilla jigsaw system makes the same choice. | – | (confirms our design) |

---

### More Villager Professions V2 2.0.1 (Bedrock add-on, "Panda Craft Game"; behaviour + resources; licence: none stated)

- **What it does:** 10 extra "profession" NPCs (lumberjack, miner, chef, doctor, botanist, beekeeper, butcher, builder "constructicons", enchanter, police) with trade tables and food items.
- **Manifest:** BP `min_engine_version` [1,19,30], data only.

**Mechanisms found**

- These are **not** villager professions: each is a separate entity (e.g. `the:lumberjack`, format 1.8.0) with `runtime_identifier: "minecraft:witch"` (police uses `pa:villager_with_player_model`). Each has `minecraft:trade_table` + `behavior.trade_with_player`, wandering-trader families, and `random_stroll`.
- **There is no POI, workstation or dweller job logic** (not found).
- Spawn rules (`spawn_rules/the_lumberjack.json`): surface + underground, weight 80, herd 1, density 8, overworld tag. Population control `animal`.
- Trades (`trades/entities/the_lumberjack_trades.json`): `tiers[{total_exp_required, groups[{num_to_select, trades[{wants, gives, trader_exp, max_uses -1}]}]}]`.
- Police: `nearest_attackable_target` radius 35 with `must_reach`, `melee_attack` speed 2, and owner-follow.

**Usable for CIVITAS:** low. Our shops are ledger-driven. One small point: the trade-tier format (`total_exp_required`) could, at most, unlock goods at a counter as the shopkeeper's rank rises. Effort S, value 1.

---

### Moneyz Economy 2.0.0 (Bedrock add-on; licence: none stated)

- **What it does:** a full economy platform: player balances, virtual accounts, treasury, shops, jobs payroll, property and hotel rent, quests, escrow, invoices, games, NPC dialogue shops, and a public API.
- **Manifest:** `min_engine_version` [1,21,50], `@minecraft/server` **2.10.0**, server-ui **2.2.0**. 105 JS files (`item_data.js` alone is 352 KB), 616 `.mcfunction` (legacy), 63 `.mcstructure`, `dialogue/*.dialogue.json`.

**Mechanisms found**

- **Money storage** (`scripts/core/economy.js`): player balance = **scoreboard objective `Moneyz`** (integer score; `setScore`/`getScore`). Every change is recorded through `commit(...)` → `transactions.record`.
- **Virtual accounts** (`core/accounts.js`): one dynamic property `moneyz:accounts:v1` = `{id: {balance, type, metadata}}`. Ids are validated `/^[a-z0-9_.:-]{3,80}$/`. Balances cannot go below 0. `beforeAccountChange` is a cancelable event.
- **Treasury** (`core/treasury.js`): modes classic (infinite source), treasury (must hold funds) or reserve. It tracks `balance`, `issued`, `destroyed`, `inflow` and `outflow`, so the money supply is auditable.
- **Transactions** (`core/transactions.js`): a ring buffer of the last **150** records `{id, at, type, actor, from, to, amount, balanceBefore, balanceAfter, metadata}` in `moneyz:transactions`, with filters by player, type and date.
- **Saga transactions** (`core/transaction_scope.js`): `transaction(work)` gives `tx.withdraw/deposit/accountWithdraw/accountDeposit`, each pushing its inverse to an undo stack. On a throw, undo runs in reverse ("compensating rollback").
- **Escrow** (`core/escrow.js`): hold, then release or refund (in-memory Map).
- **Persistent scheduler** (`core/scheduler.js`): jobs `{id, handlerId, intervalMs, nextRun, data}` in the `moneyz:schedules:v1` property. Handlers are re-registered by code at startup. A 100-tick interval runs due jobs and saves when dirty. Real-time based.
- **Storage namespaces** (`core/storage.js`): `moneyz:ext:<ns>:<key>`, with world and player variants and key validation.
- **Schema migrations:** a versioned key (`core/migrations.js`), plus a legacy shop import from `shop_*` keys to `moneyz:shop:v3:*` (`repositories/shops.js`).
- **Rent** (`core/properties.js`): `rent`, `rentInterval` (minimum 60 s, default 86400), paid per interval.
- **Payroll** (`core/jobs.js`): a banker-run payroll paid from the treasury.
- **UI** (`scripts/ui/ddui.js`): wraps **server-ui 2.2 `CustomForm`** with `ObservableBoolean/Number/String` (reactive form values) **[needs version check]**.
- **NPC dialogue:** `minecraft:npc_dialogue` scene files whose buttons run `/dialogue open @s @initiator <scene>` (data-driven menus with no script).

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| Ledger audit trail | A ring buffer of the last N money/goods movements per town (before/after, actor, reason) for the codex, debugging and rumours ("the baker raised prices"). | S | 4 |
| Money-supply accounting in the treasury (issued, destroyed, inflow, outflow) | Detects coin inflation or leaks in our economy tests. | S | 3 |
| Compensating multi-step transactions | Wrap market buy/sell and wage payment, which touch several ledgers, so a mid-way failure rolls back. | S | 3 |
| Persistent real-time or game-time scheduler with handler ids | Stage timers, rent and wage day as saved jobs with `nextRun`, re-bound to code at startup. | S | 3 |
| Do not keep CIVITAS coin on a scoreboard | Scoreboards are 32-bit ints, per-player, and need named objectives. Our dynamic-property ledger is better. Keep it. | – | (lesson) |

---

## Top ideas from this group (ranked)

1. **Phase-staggered dispatcher** (Smart Villager `tick % 4` on a 2-tick loop; Jerry cadence buckets with per-task try/catch). Give each CIVITAS subsystem its own tick phase so no two heavy loops coincide, and add a measured-MSPT readout (Jerry's `Date.now()` delta) that shrinks per-tick budgets when the server is slow. S / 5.
2. **Abstract (statistical) daily production for workers away from players, with catch-up** (Jerry logger/farm passives: once per day at a fixed time, best-of-N rolls by skill, tool uses consumed, season × mood multiplier, overdue → run now). Keep real block work for near-player sites. M / 5.
3. **Per-town split save with a dirty-id set** (Jerry `colony_data_<id>` + index, 20-tick flush of dirty ids only, history pruning, 30k-character warning, 10-per-tick load). Replaces the whole-state write. M / 4.
4. **Marker blocks inside stage templates** (Villages Plus self-ticking spawner blocks). Counters, beds, workstations and spawn points are registered from the template on placement instead of hand-kept coordinates. M / 4.
5. **Weathering and age by structure integrity** (Village Generator save → replace → reload at integrity N). Use `structureManager.place` with `integrity` + `integritySeed=buildingId` and weathered template variants for old houses, conversions and ruins. S / 4.
6. **Mood tier → yield multiplier with a strike at the bottom, plus festival fatigue** (Jerry: 0 / 0.75 / 1.0 / 1.1 / 1.2; festival ×0.5, banquet ×0.8) and an event-delta table. S / 4.
7. **Tier gates and a needs model** (Village Ruler: population + happiness + required buildings per tier; food/housing/employment/security → prosperity; immigration rule at happiness ≥72 with food and housing surplus). S / 4.
8. **Trade caravans between towns** (Village Ruler profit and safety formulas, ambush roll per 10 steps) on our route graph. M / 4.
9. **Worker pinning and native goal toggles** (`movement 0` "at post" group; `move_to_block`/`follow_mob` groups switched by event) plus an **unreachable-target blacklist with expiry** and a busy-arbitration check (Smart Villager 1.0.3). S / 4.
10. **Ledger audit ring buffer and treasury money-supply accounting** (Moneyz), plus a precomputed bill of materials per template (Jerry scanner idea, done offline in our build tool). S / 4.
11. **Lantern-carrying night watch** (light block at head, Human Companions) and **JSON night-patrol fallback** (`move_through_village only_at_night`, Village Guards) for watchmen when the script patrol is idle. S / 3.
12. **Town notice board with requests generated from real ledger shortages** (Quests & Guards), and personality, favourite and gift affinity in census records (Lively Villagers). S / 3.
13. **Version-gated extras:** Locator Bar waypoints for towns (server 2.9.0), runtime `placeJigsaw` for outer districts (2.5.0), reactive `CustomForm` UIs (server-ui 2.2.0). Check our 2.3.0 target first.

**Cost lessons from this group:**
- Never run per-tick, whole-dimension `getEntities()` (Human Companions, Jerry).
- Big ring scans are thousands of `getBlock` calls in one tick; Smart Villager's fishing search is about 5,800. Precompute (land survey) or use `runJob`.
- Village Ruler rebuilds a whole blueprint list every 6 ticks and searches for anchors around every player in six loops.
- Smart Villager 1.0.3 itself shrank most radii (for example 28→14, 12→4).

## Files examined

All paths are inside the named archive. Nested `.mcpack` entries show the extracted folder name.

**curseforge/jerrys-colonies__Jerrys_Colonies_2.15.7.MCADDON**
- Jerry'sColBP/manifest.json
- Jerry'sColRP/manifest.json
- Jerry'sColBP/scripts/main.js (deobfuscated locally for reading)
- Jerry'sColBP/scripts/module/masterHeartbeatEngine.js
- Jerry'sColBP/scripts/module/persistenceManager.js
- Jerry'sColBP/scripts/module/colonyEventEmitter.js
- Jerry'sColBP/scripts/module/marketplaceLogic.js
- Jerry'sColBP/scripts/module/moodSystem.js
- Jerry'sColBP/scripts/module/leveling.js
- Jerry'sColBP/scripts/module/seasonSystem.js
- Jerry'sColBP/scripts/module/agingSystem.js
- Jerry'sColBP/scripts/module/citizenStats.js
- Jerry'sColBP/scripts/module/structureScanner.js
- Jerry'sColBP/scripts/module/stationConfig.js
- Jerry'sColBP/scripts/module/diplomacy.js
- Jerry'sColBP/scripts/module/warSystem.js
- Jerry'sColBP/scripts/module/market_stall.js
- Jerry'sColBP/scripts/module/housingClaim.js
- Jerry'sColBP/scripts/module/knowledgeBuffsEngine.js
- Jerry'sColBP/scripts/ui/workstation/loggerStationUI.js
- Jerry'sColBP/scripts/ui/workstation/farmerZoneManager.js
- Jerry'sColBP/scripts/ui/workstation/knowledgeTreeUI.js
- Jerry'sColBP/scripts/ui/workstation/*.js (grep for exported tick functions)
- Jerry'sColBP/entities/humanoid/citizen_male.json
- Jerry'sColBP/entities/other/work_target.json
- Jerry'sColBP/functions/spawn_citizen.mcfunction
- Jerry'sColRP/texts/*.lang (licence grep)

**curseforge/empire-expansion__EMPIRE_EXPANSION_2.0.10.mcaddon**
- EMPIRE EXPANSION BP/manifest.json
- EMPIRE EXPANSION RP/manifest.json
- EMPIRE EXPANSION BP/scripts/main.js
- EMPIRE EXPANSION BP/scripts/structures.js
- EMPIRE EXPANSION BP/scripts/features/dynamic_properties.js
- EMPIRE EXPANSION BP/scripts/features/random_events.js
- EMPIRE EXPANSION BP/scripts/database/economy_config.js
- EMPIRE EXPANSION BP/scripts/database/resource_config.js
- EMPIRE EXPANSION BP/scripts/** (grep for runInterval/getEntities/scriptevent)
- EMPIRE EXPANSION BP/entities/citizen/citizen_worker.json

**curseforge/village-ruler__Village_Ruler_v2.mcaddon**
- Living_AI_World_BP/manifest.json
- Living_AI_World_RP/manifest.json
- Living_AI_World_BP/scripts/main.js
- Living_AI_World_BP/functions/convert_nearby_village.mcfunction
- Living_AI_World_BP/functions/give_planner.mcfunction
- Living_AI_World_BP/functions/spawn_living_settlement.mcfunction

**curseforge/hardworking-villagers__work.mcpack**
- manifest.json
- subpacks/normal/entities/villager_v2.json
- subpacks/no_afternoon_break/entities/villager_v2.json
- subpacks/no_break_at_all/entities/villager_v2.json

**curseforge/guard-villager-add-on__GuardVillager12.mcaddon**
- Guard villager_behavior_pack/manifest.json
- Guard villager_behavior_pack/scripts/main.js
- Guard villager_behavior_pack/scripts/custom/soldierspawn.js
- Guard villager_behavior_pack/entities/villager_soldier.json

**manual/village-guards_1614659323.mcaddon**
- behaviour.mcpack/manifest.json
- behaviour.mcpack/entities/villageguard.guard.json
- behaviour.mcpack/entities/villageguard.archer.json
- behaviour.mcpack/entities/villager_v2.json

**curseforge/village-generator-function-pack__Village_Generator_2.4.0.mcaddon**
- bp/manifest.json
- bp/LICENSE.md
- bp/README.md
- bp/CHANGELOG.md
- bp/functions/vg/instant/plains_1.mcfunction
- bp/functions/vg/populate.mcfunction
- bp/functions/vg/plains/houses/accessory.mcfunction
- bp/functions/vg/plains/houses/small_house_1.mcfunction (grep)
- bp/functions/vg/plains/terminators/terminator_1.mcfunction
- bp/functions/vg_technical/instant/plains_1/street_1.mcfunction
- bp/functions/vg/taiga/zombie/houses/weaponsmith_1.mcfunction
- bp/functions/village.mcfunction

**curseforge/human-companions__Human Companions (2).mcaddon**
- Person Behavior/manifest.json
- Person Behavior/scripts/main.js
- Person Behavior/scripts/LightHuman.js
- Person Behavior/scripts/SpawnHumans.js
- Person Behavior/scripts/BannerBase.js
- Person Behavior/scripts/*.js (interval/getEntities survey of all 27)

**curseforge/kingdom-constructor__KingdomConstructor_IronAge1.1.zip**
- kingdom_constructor_BP/manifest.json
- kingdom_constructor_BP/entities/woodsman.behavior.json
- kingdom_constructor_BP/blocks/woodsman_patrol_point_1.block.json
- kingdom_constructor_BP/feature_rules/woodsman16x16_4_feature_rule.json
- kingdom_constructor_BP/features/woodsman16x16_4_feature_mcstructure.json
- kingdom_constructor_BP/functions/spawn4woodsman.mcfunction

**manual/SmartVillagerAddon_v1.0.2.mcaddon and manual/SmartVillagerAddon_v1.0.3.mcaddon**
- BP/manifest.json (both)
- BP/scripts/main.js (both, diffed)
- BP/scripts/config.js (both, diffed)
- BP/scripts/waterScanner.js (both, diffed)
- BP/scripts/fishingBehavior.js (diff)
- BP/scripts/professionHelper.js (diff)
- BP/scripts/pathfinder.js
- BP/scripts/utils.js
- BP/scripts/fishermanManager.js
- BP/scripts/farmerBehavior.js
- BP/scripts/farmerManager.js (grep)
- BP/scripts/villageExpansionManager.js
- BP/scripts/villagePopulationManager.js
- BP/scripts/*.js (grep for movement methods)
- BP/entities/villager_v2.json (both, compared)

**manual/LivelyVillagersData.mcaddon and manual/LivelyVillagersResources.mcaddon**
- LivelyVillagersData/manifest.json
- LivelyVillagersResources/manifest.json
- LivelyVillagersData/scripts/Main.js
- LivelyVillagersData/scripts/LVGlobalVariables.js
- LivelyVillagersData/scripts/LVFunctions.js
- LivelyVillagersData/scripts/VillagerGUI.js
- LivelyVillagersData/entities/villager_male.json
- LivelyVillagersResources/ui/server_form.json

**manual/quests_and_guards.mcaddon**
- server/manifest.json
- server/scripts/Main.js
- server/scripts/quests.js
- server/scripts/libraries/quest/QuestClass.js
- server/scripts/libraries/quest/questConstants.js
- server/scripts/entityNameTag.js
- server/scripts/entity_names/villager_names.js
- server/blocks/questboard.json
- server/entities/villager_v2.json
- server/entities/warrior.json

**manual/Villages-Plus-v-0-7.mcaddon**
- all six manifest.json (base, Increased, Classic BP/RP)
- Villages-Plus-BP/scripts/main.js
- Villages-Plus-BP/blocks/villages_plus/villager_spawner.json
- Villages-Plus-BP/worldgen/structures/*.json (all 19 surveyed; timber_village.json read in full)
- Villages-Plus-BP/worldgen/structure_sets/villages_plus_set.json
- Villages-Plus-Increased-Structures-BP/worldgen/structure_sets/villages_plus_set.json
- Villages-Plus-BP/worldgen/template_pools/village/timber/*.json (7 pools)
- Villages-Plus-BP/worldgen/processors/generic_path_processor.json
- Villages-Plus-BP/worldgen/processors/worndown_street_processor.json
- Villages-Plus-BP/midtions/plus_villagers.mcfunction

**manual/more-villagers-profession-behaviour.mcpack and manual/more-villagers-profession-resources.mcpack**
- More Villagers Profession Behaviour/manifest.json
- More Villagers Profession Behaviour/entities/the_lumberjack.json
- More Villagers Profession Behaviour/entities/police_villager.json
- More Villagers Profession Behaviour/spawn_rules/the_lumberjack.json
- More Villagers Profession Behaviour/trades/entities/the_lumberjack_trades.json
- More Villagers Profession Behaviour/functions/candy_food.mcfunction

**manual/Moneyz Economy 2.0.0.mcpack**
- manifest.json
- scripts/core/economy.js
- scripts/core/accounts.js
- scripts/core/treasury.js
- scripts/core/transactions.js
- scripts/core/transaction_scope.js
- scripts/core/escrow.js
- scripts/core/scheduler.js
- scripts/core/storage.js
- scripts/core/properties.js (grep)
- scripts/core/jobs.js
- scripts/core/metrics.js
- scripts/core/dev.js
- scripts/core/migrations.js
- scripts/core/notifications.js
- scripts/core/health.js
- scripts/core/events.js
- scripts/core/api.js
- scripts/core/games.js
- scripts/repositories/shops.js
- scripts/repositories/custom_shop.js
- scripts/services/instruments.js
- scripts/services/rewards.js
- scripts/ui/ddui.js
- scripts/npcInteract.js
- scripts/quest/engine.js (grep)
- dialogue/farmer.dialogue.json

**Ledgers and CIVITAS baseline**
- curseforge/LEDGER.json
- manual/list.tsv
- /home/claude/tools/bp02_src_227/pw_civ_*.js (grep: setDynamicProperty, runInterval, structureManager, dirty)
