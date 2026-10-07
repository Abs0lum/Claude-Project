# B-VILLAGES — civ mods studied for CIVITAS (2026-10-06)

Group B-VILLAGES. Seven items: Millénaire, TekTopia, Tale of Kingdoms, Civilians, Smart Villagers, Kingdoms: Villager
Retaliation and Arc Quest. Every number below comes from a file I opened (named inline). "Not found" means I looked and it
is not there. I also checked the CIVITAS sources (pw_civ_people.js header, pw_civ_clock.js `planDay`) so the
recommendations don't propose things CIVITAS already does. CIVITAS already has births, marriage, mood, trust learning,
rumours, migration and a newcomer faucet (`DIALS`, `LEARN` in pw_civ_people.js). It picks the next building from fixed
tier lists and "leftover" queues in `planDay`.

---

### Millénaire (Java, NeoForge 1.21.1 fork "Leviaria/Millenaire" @ea7d6b4; licence GPL-3.0 (LICENSE file); files examined: see list — Java source + norman/byzantine culture data; curseforge jar not needed)

**What it does.** Living NPC villages from 7 historical cultures. Each village grows by itself: it picks its next building or
upgrade from a layout in the culture data, buys and saves materials into the town-hall chests, and builders put the
building up block by block. Villagers come from births, take the jobs that buildings provide, trade, and move between
villages.

**Mechanisms found**

- **Growth loop: what to build next** (village/VillageGrowthManager.java, called every 20 ticks from `Village.tick`):
  1. Skip if a "no projects" cache is set: 600 ticks after an empty search. The cache clears when a building completes.
  2. Check the active-construction limit `max_simultaneous_constructions`. tradingvillage.json uses 2. Blocked tasks and wall
     segments don't count toward it.
  3. Order of attempts: launch the **pending project** if it is now affordable, then a planned sub-building, then a new pick.
  4. **Tier gating.** The layout slots have roles `start → player → core → secondary → extra`. Only the lowest tier that still
     has unbuilt slots is eligible (`findLowestUnsatisfiedTier`). A slot counts as open when the count of that plan built so
     far is ≤ the number of earlier layout slots for the same plan (so a plan listed twice gets built twice), and below
     `max_count`.
  5. **Weighted random pick.** New buildings get weight `slot.priority × tier multiplier`, where the multipliers are
     start/centre/player 6, core 4, secondary 2, extra 1. **Upgrades of finished buildings compete in the same pool** with
     weight = the next level's `priority`. The plans set priority per level and it falls with level: carpenterhouse.json uses
     800, 80, 75, 60, 55; manor.json uses 600 … 440.
  6. Affordability is checked against the **town-hall inventory only**. If the chosen project can't be afforded, it is stored
     as the single `PendingProject` and an **affordable fallback** is built instead (`tryAffordableFallback`, tier gating
     off). The village therefore never stalls waiting for one expensive item.
  7. Upgrades have conditions (`checkBuildConditions`): runtime tags on the building, tags on the parent building, tags
     forbidden anywhere in the village, and tags required in the village.
  8. If no site is found, that plan gets a 1600-tick placement cooldown. A "rush" mode places buildings instantly (used for
     world-gen).
- **Cost comes from the template** (building/BuildingCostCalculator.java):
  - Block counts are read from the NBT palette. Terrain, flowers, air and path blocks are free.
  - Wood conversions: planks → `ceil(planks/4)` logs ("anywood" = any log type); some wood blocks cost planks ×7 or ×16.
  - Stone and metal blocks each map to their own resource; one entry costs cobblestone ×8.
  - Glass panes → `ceil(panes·6/16)` glass; half-tile slabs → `max(ceil(halves/2),1)`.
  - Village designers never type costs by hand.
- **Resident slots are jobs** (building json `male:["carpenter"]`, `female:["wife"]`; ChildBecomeAdultGoal.java;
  ResidentSlotManager.java):
  - A building declares which villager types live in it.
  - A child reaching size 20 looks for an operational building with a free slot of its gender. It skips buildings that hold
    an opposite-gender adult of its own family name. It then takes the slot whose building has the lowest
    `priority_move_in` (loader default 10; carpenterhouse 20), walks there (arrive ≤3 blocks) and **becomes that slot's
    villager type**.
  - Building a forge creates a smith once someone comes of age. Growth-built houses are not filled by spawning: only rush
    and world-gen call `spawnBuildingOccupants`.
- **Nightly family actions** (village/NightActionHelper.java). They run once per night when dayTime ≥ 13000:
  - **Conception:** the mother needs fewer than 2 children in her home and the village must be below `maxChildren` (config
    default 10, range 2–20). Above 5 children, it also needs a free adult slot of either gender. There must be an adult male
    within 4 blocks. Base chance is 2/10, plus the best conception food in the home: wine, cake or calva +4, sake +3
    (villager_config/default.json; one item per night). Child gender: `maleChance = clamp(3 + females − males, 0, 6)` out
    of 6 for the household.
  - **Child growth:** +2 per night. An egg in the home adds 1+rand(5); each food from `food_growth` adds value+rand(value)
    (bread 2, cooked beef 4, tripes 6, …). Growth is capped at 10 per night; adulthood is at size 20. Children eat the
    household's food.
  - **Teen migration:** a grown child with no slot goes to another village of the same culture whose relation is > 90, if it
    has both a matching free slot and an inn with fewer than 2 residents. Both towns log a MIGRATION chronicle entry.
  - **Visitors** leave after more than 5 nights. Foreign merchants leave early once their stock is empty.
- **Goal scheduler: villager AI** (goal/GoalScheduler.java, VillagerGoal.java):
  - Each goal declares `computePriority`, `canStart`, `isLeisure`, `canBeDoneAtNight`, `canBeDoneInDayTime` and
    `reoccurDelayTicks`.
  - The best goal wins, but **work always beats leisure**. A leisure task is interrupted as soon as any work goal can start.
  - If nothing can start, idle backoff doubles from 1 to 20 ticks.
  - **Watchdog:** a task that reports no progress for 6000 ticks is force-stopped. Builders give up after 3 failed attempts
    (BuildGoal).
  - Priorities found: Build 1500, LightHearth 2000 (window 1000–3000), ChildBecomeAdult 100, Chat 10 (leisure, partner
    within 5), Socialise 5 (leisure, waits 200–400 ticks), Idle 0.
  - Rest = `50 + min(200, sleepDebt/30)`, night only.
  - GetGoodsForHousehold priority = missing×20. It is throttled to every 2000 ticks unless more than 16 goods are missing.
    "Missing" means the home holds less than half of what its residents need (`required_goods`, e.g. farmer: 100 seeds).
  - Per-villager throttle record expiry is 12000 ticks.
- **Data-driven visits and leisure** (visit_goal/*.json, 43 shipped):
  - Schema: `type` (visitBuilding / observeVillager / play), `buildingTag`, `basePriority`, `priorityRandom`,
    `durationTicks`, `reoccurDelayTicks`, `minimumHour`/`maximumHour` (dayTime ticks), `maxSimultaneousInBuilding`,
    `heldItems`, `goalKey` (the sentence key).
  - drink_cider: tag drinking, priority 50+rand30, 400 ticks, every 12000, after 10000.
  - **give_speech:** the leader goes to the `balcony` 9000–10000, priority 10000.
  - **listen_to_speech:** observeVillager of `give_speech`, priority 100, same window. This makes a town assembly.
  - patrol: tag patrol, 40 ticks, every 1200.
  - observe_construction: watch whoever is building, priority 5+rand10.
- **Data-driven work** (gathering_type/chop_trees.json): handler `chopping`, priority 125+rand10 minus a penalty when
  carrying logs, scanRadius 48, batchRadius 5, ≤20 actions per task, 15-tick cooldown, stuck timeout 4000, hours 0–12500,
  **`townhallLimit: {#logs: 4096}`** (stops producing at the cap), at most 1 per building.
- **Construction pace** (BuildGoal.java): one builder reserves a site. The reservation is released if the builder entity is
  missing for 200 ticks (Village.java `RESERVATION_EXPIRY_TICKS`). Each block takes 7–16 ticks depending on shovel tier;
  soft blocks take /4.
- **Economy** (traded_goods.json, shops/*.json, GoodAvailabilityHelper.java, TradeMenu.java):
  - Each good has `selling_price`, `buying_price`, `reserved_quantity` (the village never sells below this; e.g. oak log
    128) and `target_quantity` (it buys up to this; oak log 1024).
  - Shops list `sells`, `buys` and `deliver_to`; e.g. bakery: sells bread, buys wheat.
  - Goods available to a shop = stock − reserved − residents' needs.
  - Prices are fixed per good, with per-village-type overrides; no supply and demand.
  - Player reputation rises by the money spent; selling gives revenue × multiplier, ×4 in "donation" mode
    (ReputationConstants).
  - Reputation ladder (norman reputation.json): −1024 public enemy … 0 stranger … 8192 friend of the village … 32768 one of
    us. Below −1024 the village boycotts the player.
- **Markets and merchants:**
  - MarketManager.java: at night, a market with `stall` points spawns one foreign merchant per empty stall. If other-culture
    villages with relation > 70 and a market exist, the chance of a foreign type is `min(1+n,5)/11`.
  - LocalMerchantHelper.java: an inn's merchant moves after ≥2 nights at that inn. Destination: a town with relation ≥0 within
    2000 blocks that needs the goods in the inn chest; an inn with no merchant counts ×3 in the pick. He carries the whole
    inn chest, recorded as imports and exports, or swaps with the other merchant. After >3 nights any inn is a backup target.
- **Diplomacy between towns** (VillageDiplomacyHelper.java, VillageRelations.java):
  - Relations run −100…100 with labels at 90/70/50/30/10/0/−10/−30/−50/−70/−90.
  - Nightly, each pair has a 10% chance to drift by ±10–19. The chance of improving depends on the current value: <−90 never;
    <−50 30%; <0 40%; 0–50 60%; >50 70%; >90 always. Nearby players are told.
- **Placement on terrain** (world/BuildingLocationFinder.java, PlacementConstraints.java, VillageTerrainMap.java,
  TerrainReachability.java):
  - Ring search from `minDist` to `maxDist`. These are fractions of the village radius (default 90 if unset), with defaults
    5 and 60 blocks. Each ring is scanned on 4 sides, starting from a random side.
  - The building's door faces the village centre unless the plan fixes the orientation.
  - Tag constraints `far_from` / `close_to`. Default clear margin 5 (config 0–10).
  - **Footprint error budget:** 10 bad cells for buildings ≤200 m², 5% for 200–2000 m², 10% above 2000 m². A cell is bad if
    its altitude is outside **baseline ±10**, or it is dangerous or forbidden. Occupied cells reject the site outright.
  - Build Y = average ground height over the footprint plus margins. The terrain is then flattened (Java can do this).
  - **Reachability:** a flood fill over passable cells (step ±1 needs 3 blocks of headroom). The site must be in the town
    hall's region; the class defines `MIN_REACHABLE_RATIO = 0.7` (70% of the footprint).
- **Chronicle** (VillageEventType.java; Village.java `MAX_CHRONICLE_SIZE = 500`): FOUNDED, BUILDING_STARTED/COMPLETED,
  UPGRADE_STARTED, VILLAGER_SPAWNED, BIRTH, DEATH, CAME_OF_AGE, MERCHANT_ARRIVED, MIGRATION.
- **Chat:**
  - Sentences use `role.goalKey=text`. The villager speaks about the goal it is doing (norman_sentences.txt, e.g.
    `farmer.plantseeds=…`).
  - Dialogues are 2-person scripts. Header `newchat;key:…;weigth:10`, lines `v1;0;…` / `v2;30;…` (speaker; tick offset), with
    optional tags/relations filters (norman_dialogues.txt, ChatGoal.java).
- **Chief and town hall:** ControlledProjectsService.java lists projects and allows or forbids upgrades per building, for
  player-controlled villages. Players buy `player_buildings` with money and reputation (BuildingPurchaseService.java; buyer
  must be within 64 blocks).

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| **Weighted growth chooser**: tier-gated candidates (role × multiplier 6/4/2/1) + upgrades in the same pool + one pending project + affordable fallback + no-candidate cache + per-plan site-fail cooldown | Replace the fixed leftover order in `planDay` with a chooser over plan slots (by tier) and next-level conversions/taller rebuilds. Pending project + cooldowns are 3 small fields in the town's dynamic-property state. Pure function → node-testable | M | 5 |
| **Cost from the template** | Build-time Python reads each .mcstructure palette/block counts (same rules: planks/4 → logs, panes 6/16, slabs ½, terrain free) → `costs.json` baked into the script; ledger checks stock before launch | S | 5 |
| **Buildings declare job/resident slots; people who come of age take the slot with the lowest move-in priority; no slot → migrate to a friendly town** | Add `slots:{m:[…],f:[…]}` per template in the building catalogue; `people` daily pass assigns comers-of-age/newcomers to free slots; job = slot type. Feeds the Immigrant Faucet with real demand | M | 5 |
| Footprint **error budget** + **altitude window** + **reachability to the route graph** for plot acceptance | In the land survey, score plots: bad-cell count vs budget (10 / 5% / 10%); reject if not connected to the street graph (BFS on survey grid). No terraforming needed — only accept/reject | M | 4 |
| Goal scheduler pattern: work beats leisure, leisure interrupted by work, reoccur cooldowns, exponential idle backoff (1→20 ticks), **no-progress watchdog** | CIVITAS bodies already have schedules; add per-person `goal`, `goalSince`, `lastProgress` and a 6000-tick no-progress abort in pw_civ_walk/work | S | 4 |
| **Data-driven visits** (time window, building tag, duration, cooldown, held item) incl. **leader's dusk speech + listeners** | A JSON table in the BP script (`visits.js`); clock picks a visit for idle people; the speech = the palace/town-hall reserved block at 9000–10000 with listeners gathering in the square (can read the day's ledger/rumours) | M | 4 |
| Production caps per good (`townhallLimit`) and **reserved / target** stock levels | Two numbers per good in pw_civ_economy: workers stop when stock ≥ cap; the market never sells below reserved and buys up to target | S | 4 |
| Child growth fed by household food; conception boosted by luxury food; max 2 children per home | Link `DIALS.birthChance` to the household's food/luxury stock in the ledger (base 0.2 → +0.4 with wine/cake) | S | 3 |
| Inter-town merchants that carry an inn chest to a town that needs it; foreign merchants per market stall leaving after 5 nights | Needs 2+ CIVITAS towns: nightly script moves a "merchant" record + goods between town ledgers (no entity travel) | M | 3 |
| Nightly diplomacy drift (10% per pair, ±10–19, biased by level) | One loop over town pairs at dusk; feeds migration/merchant eligibility | S | 2 |
| **Chronicle** (capped event log by type) | `st.log` already exists; cap to ~500 typed entries, expose in a written book or at the town hall | S | 3 |
| Builder reservation released after the builder is absent 200 ticks | Builder site claims in pw_civ_work get an age counter | S | 3 |

---

### TekTopia (Java, Forge 1.12.2, v1.1.0; licence: no licence file in the jar; it bundles a `com/websina/license` licence tracker, so treat it as closed/all rights reserved; files examined: decompiled classes listed below + lang)

**What it does.** The player designates structures by placing item frames holding "structure tokens" (home, storage,
tavern, …). Professions do real block work: chopping, farming, mining. Villagers have hunger, happiness and intelligence;
their skills grow with work; nomads and merchants arrive daily.

**Mechanisms found**

- **Schedule** (entities/EntityVillagerTek.java):
  - Work 500–11500, cancelled by rain.
  - Sleep starts at 16000 and lasts 8000. Each villager has a personal `sleepOffset` of ±200 ticks (`genOffset(400)`), and
    sleep starts +4000 later if the villager wants the tavern.
  - Learning window: `sleepOffset+2500 … +8000`.
- **Needs:**
  - Hunger 0–100. Walking costs −1 with chance 1/50 per movement update. Below 30 = hungry, 0 = starving. Hunger doesn't
    drop if the village has no storage.
  - Happiness 0–100. Below 20% max the villager walks with a "SULK" gait.
  - Eating takes 80 ticks. Food table (`EntityAIEatFood`, hunger/happy): raw apple 12/−1, bread 55/+4, cooked beef 70/+14,
    pumpkin pie 70/+20, cake 7/+25, …
  - **Variety:** the same food eaten again gets penalties `[+2, 0, −3, −7, −12, −18]` by count among recent meals (floor −3
    on the result). Food not made by villagers gives half the hunger value and no happiness.
  - Food choice score = hunger + 5×happy×(missing happiness fraction).
- **Happiness sources:**
  - Waking at the right time: +10–29.
  - Tavern: wanted when happy < 70 outside work (30% daily random wish), or when < 10.
  - **Crowding** (`VillageStructure.getCrowdedFactor`): floor tiles per villager below the type's `tilesPerVillager` (12 for
    homes, storage, school, …) gives penalty −5×factor; average ceiling < 2.5 halves the factor.
  - Being on a lead: −1 per 30–50 ticks.
- **Thought bubbles** (`EntityVillagerTek$VillagerThought`): BED, HUNGRY, PICK, HOE, AXE, SWORD, BOOKSHELF, *_FOOD, BUCKET,
  SHEARS, TAVERN, NOTEBLOCK, TEACHER, TORCH, INSOMNIA, CROWDED. One is sent at most every 80 ticks. Missing bed → BED;
  already slept → INSOMNIA (EntityAISleep).
- **Births** (`checkSpawnHeart`): on waking with happiness ≥ 70%, chance 1/(15 + N + N·happyFactor·2), where
  happyFactor = (max−happy)/(max−70%). Happier and smaller towns get more children. A village-wide `isChildReady` cooldown
  also applies. Children become adults after 4–5 days (EntityChild `daysForAdult`).
- **Skills 0–100 per profession:**
  - `tryAddSkill`: gapMod = 1/(skill/intel)²; it succeeds if roll×rate/100 ≤ min(gapMod×0.2, 1) and also 1/chance. Low
    intelligence caps skill growth.
  - Intelligence rises by reading, with chance `2·rand(100) > intel`.
  - **Proximity learning:** when an adult gains a point, children within 12 blocks (not in school) with less than half that
    skill gain one with chance 1/max(childSkill/2, 1).
  - Skill speeds up work: chop success 1/lerp(6→2).
- **Structures by frame and floor scan** (VillageStructure.java):
  - A frame next to a wooden door; flood-fill floor tiles with headroom ≥2 (max 500 tiles), revalidated every 50–100 ticks.
  - Homes cap beds (HOME2/4/6). Bed colour shows its state: red = unclaimed, green = this resident's, yellow = someone
    else's.
  - The town hall spawns vendors (architect, tradesman) every 200 ticks; max 1 town hall.
  - Professions are gated by structures: e.g. the lumberjack crafts tools at STORAGE (EntityLumberjack task list).
- **Block claims:** `village.requestBlock(log)` gives each worker an exclusive tree/ore, released when done (Village.java),
  so two workers never pick the same tree.
- **Market prices drift, zero-sum** (economy/ItemEconomy.java, ItemValue.java):
  - Each sale appends to a sales history of size `lerp(30, 50, residents/100)`.
  - On refresh, each historic sale marks that item down by lerp(10%→30%) of its current value (newer sales hit harder).
    That amount is spread as a mark-up over all other items in proportion to base value.
  - An item disappears from offers after 8 sales in the window.
  - Offers: 8 + 2×stallLevel trades, chosen by appearance weight × currentValue/baseValue, and only for professions present
    in the village.
- **Nomads** (NomadScheduler.java, EntityNomad.java):
  - Checked once per day. Spawn if residents ≤ 3, else with chance 1/⌊√N⌋. They arrive at a village edge node: 1 nomad,
    2 if residents ≤ 1, plus up to 5 more at 50% each.
  - Each nomad brings 1–2 random profession skills of 3–25.
  - Nomads leave at night unless the player converts them; they despawn if stuck (<20 blocks moved in 300 ticks).
- **Merchant** (MerchantScheduler.java): one per day, replacing the previous one, delivering the animals the player ordered.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| **Need bubbles** over bodies (no bed, hungry, no tool, crowded, insomnia, wants tavern) | Script sets a 2nd nameTag line with an icon glyph, or spawns a custom RP particle above the villager every ~4 s for its top unmet need from the census. Directly serves the observation-first rule: he can *see* why a person is unhappy | S | 5 |
| **Zero-sum price drift** from a rolling sales window | The market clerk's prices in pw_civ_economy: keep a ring buffer of last N sale ids (N = 30–50 by population) in the town state; recompute prices once a day | S | 4 |
| Personal **sleep/work offsets** (±200 ticks) so the town doesn't move in lock-step | Per-person offset from id hash in the walk scheduler; no storage | S | 4 |
| Food variety penalty and "villager-made food" bonus | Household meals from the ledger; repeated staple → mood −; market food made in town → mood + | S | 3 |
| **Exclusive block claims** for workers (tree, quarry face) | Claim map in memory (not saved) keyed by block pos; woodcutters/quarrymen request → release | S | 4 |
| Crowding (floor tiles per person < 12 → mood −) | Use template floor area from the catalogue ÷ residents; daily mood term | S | 3 |
| Birth chance rising with happiness, falling with town size | Plug into `DIALS.birthChance` as 1/(15+N+N·k) style term | S | 3 |
| Nomads with prior skills; children learning near skilled adults | Faucet newcomers get 1–2 random skills 3–25; apprentices near a master gain skill faster (work site co-presence already tracked) | S | 3 |

---

### Tale of Kingdoms: A New Conquest (Java, Fabric; source SamB440/Tale-of-Kingdoms @50fd40e; licence GPL-3.0 (repo LICENSE), Modrinth ledger says LGPL-3.0-only for the 1.0.5 jar; manual taleofkingdoms-1.0.0.jar = MC 1.16.x; files examined: listed below)

**What it does.** An adventure mod. The player earns "worthiness" from a guild by killing mobs. At 1500 worthiness a city
builder founds the player's kingdom. The player pays wood and stone to have pre-made buildings pasted in, and upgrades the
kingdom from tier 1 to tier 2.

**Mechanisms found**

- **Growth stages** (kingdom/KingdomTier.java):
  - TIER_ONE and TIER_TWO only. Each tier is one whole-town schematic; tier 2 is offset (16,0,49) from the origin.
  - The upgrade re-pastes the tier schematic, then re-pastes every built building of that tier at its POI
    (`CityBuilderEntity.fixKingdom`). This needs the builder to hold 320 wood and 320 stone.
- **Build menu** (kingdom/builds/BuildCosts.java): fixed wood/stone costs, e.g. small house 192/128, large house 192/320,
  item shop 256/256, block shop 256/320, barracks 320/320. Each entry is tied to a tier, a schematic, a rotation and a POI.
  Building = instant schematic paste (`CityBuilderEntity.build`).
- **POI markers** (kingdom/poi/KingdomPOI.java): named marker blocks inside schematics (e.g. "CityBuilderWellPOI",
  "TierOneBlacksmith") are resolved at paste time into positions where NPCs are teleported or spawned.
- **Taxes** (PlayerKingdom.tryTaxCollection): at most once per real hour (3,600,000 ms). Small house 50 gold, large house 125,
  tier-2 small house 175, tier-2 large house 250.
- **Workers are faked** (GatherResourcesPassivelyGoal.java): a worker inside the kingdom has a 1/100 chance per tick to
  swing its arm, and a 2% chance per tick to add 1 cobblestone or 1 oak log to its foreman's inventory. No blocks are mined
  or felled. Buying a worker costs 1500 coins (ForemanEntity).
- **Stock market** (StockMarketEntity.java): once per game day, every shop item gets a random price modifier of 0.75–3.0.
- **Worthiness:** rises per mob kill (mob value × difficulty multiplier; CoinListener.java), and from guarding (+2) and lone
  villagers (+6 each).
- NPCs wander (WanderAroundKingdomGoal: chance 50, range 30/7).

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| POI marker blocks inside structures resolved at placement into NPC/counter/seat positions | CIVITAS already has markers (build_markers_*); confirms the pattern — extend to "speech balcony", "stall", "bench" POIs for the visit table above | S | 3 |
| Per-building tax (rent) by house class | Daily rent into the town ledger by template class (house S/M/L) — a coin sink/source for the economy | S | 2 |
| Counter-example: passive "fake" gathering and random daily price swings | Keep CIVITAS's real work + ledger-driven prices; don't copy | — | 1 |

---

### Civilians (Java, Fabric 1.21.5 v1.4.2 + manual 1.21.1 build (same class list); licence MIT (LICENSE_civiliansmod); files examined: listed below)

**What it does.** Player-skinned NPCs with editable dialogue. Sneak-using an NPC totem on a jobless vanilla villager converts
it into an NPC. They wander, open doors and talk.

**Mechanisms found**

- **Goals are minimal** (entity/NPCEntity.java `initGoals`): wander (speed 0.7), look around, and `CustomDoorGoal`. There is
  **no building entry or leave logic beyond doors** and no schedules (not found).
- **Doors** (entity/goal/CustomDoorGoal.java):
  - Look for a door within ±2 blocks and open it.
  - Walk to 2 blocks past the door along its facing.
  - Close it once no longer navigating and stuck for 20 ticks.
  - Cooldown 100 ticks.
- **When hit:** speaks a random HURT line and flees 12× the attacker→NPC vector at speed 1.2.
- **On interact:** turns to face the player for 60 ticks and speaks a random INTERACT line.
- **Chat** (chat/NpcChat.java): ChatReason HURT / INTERACT. Lines are kept per player language and editable in a GUI.
- **Conversion** (NPCConversionHandler.java): only jobless villagers (profession `minecraft:none`) can be converted.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| "Turn to face the player for 3 s and speak a line" on interact; flee-and-complain when hit | `playerInteractWithEntity` → set rotation toward player, pause the lead for 60 ticks, show a line from the person's mood/rumours; on hurt, a complaint + rumour | S | 2 |
| Doors: open on approach, close behind after passing | Bedrock navigation can open doors natively (`can_open_doors`); only needed if the lead path crosses doors — close-behind via script | S | 2 |

---

### Smart Villagers (Java, Forge 1.21.11 v0.24.2; licence All Rights Reserved (META-INF/mods.toml); files examined: listed below)

**What it does.** Vanilla villagers get jobs that change the world: farmers harvest, fletchers chop, masons mine and build
from a bell-planner blueprint, shepherds garden, fishermen act as couriers. It adds markets, restaurants and labs, a mayor,
festivals, prosperity stages and expeditions.

**Mechanisms found**

- **Fair batching** (work/FairVillagerScheduler.java): candidates are sorted by UUID. Each pass updates
  `min(limit, n)` villagers starting at offset `(pass mod n)×batch mod n`. Config `maxWorkersPerPass` defaults to 16
  (range 1–64), "a pass occurs twice per second" (`PASS_INTERVAL_TICKS = 10` in VillageWorkManager). Work is skipped for
  players more than 56 blocks away.
- **Per-villager task state in NBT** (VillageWorkManager.java):
  - Stored fields: task, target, started, progress time, best distance, repaths.
  - **Stall rule:** no improvement in best distance for 80 ticks → repath, at most 3 repaths. A hard cap of 1200 ticks per
    task. Blocked targets are remembered with an expiry.
  - Cargo is delivered at `maxCargo` (12).
  - **Natural-tree test:** ≥6 natural leaves, log within 7 horizontal / 32 vertical, ≤64 logs. This stops villagers felling
    player buildings.
  - Couriers leave `courierReserve` (8) items in the source chest and move the surplus to other village storage.
  - Search radii: work 14, garden 12, storage 24.
- **Mayor** (work/VillageMayorManager.java):
  - Every 400 ticks around each bell; needs ≥3 adults within 32 blocks. Elected = the highest villager XP; the incumbent is
    kept while eligible.
  - During the day (<12000) the mayor walks to the bell.
  - Every 1200 ticks the mayor decides a priority from the chests within ±20/±6 of the bell:
    - **expand (1)** if a construction job is active and wood ≥ 48 and stone ≥ 64;
    - **gather (2)** if wood < 24 or stone < 40;
    - otherwise 0.
  - The priority is announced to players within 64 blocks.
- **Festivals** (work/VillageFestivalManager.java):
  - Next festival is 3–5 days after the last one, only between dayTime 1000 and 9000, with ≥3 villagers near the bell.
  - Type: wedding with chance 1/3 if ≥2 adults, otherwise a fair. A "victory" festival follows the last raider's death.
  - Lasts 1800 ticks. Participants stand on a ring around the bell: angle = id·47 mod 360°, radius 3 + (id mod 3), the
    couple at 1.4. Particles every 40 ticks; the host plays a sound every 200.
  - Prosperity +2 fair / +4 wedding / +6 victory.
- **Prosperity and stages** (VillageConstructionData.java; lang en_us):
  - Points capped at 9999. Stage 0 Settlement, ≥50 Village, ≥100 Town, ≥240 City.
  - Building limit = base (2) + 2×stage, capped at 8.
  - Points come from finished houses (+25 / +15 in VillageWorkManager), festivals and quests (+12).
- **Businesses** (work/BusinessWork.java; CivicBlueprints.java builds the market, restaurant and lab rooms 11×9 or 9×9):
  - Customers are villagers with a **wallet** of 0–64 coins (players gift up to 4 at a time) within 14 blocks of the desk.
    A customer can't revisit for 1200 ticks.
  - Each sale: −1 wallet coin, +1 SALES, **+1 DIRT**, +1 clerk experience.
  - Credit points = carried credit + clerk skill, where skill = min(5, 1+exp/8). At ≥6 points the sale counts as INCOME
    (6 points are spent); otherwise as CASH.
  - **DIRT ≥ 8 closes the shop ("dirty")** until a janitor cleans: −min(3, 1+exp/12) every 80 ticks.
  - Clerk cooldown between sales is max(40, 140−exp) ticks. Shops close at dayTime ≥ 12000 and stop at 4096 coins held.
  - Restaurant: a waiter carries one meal from the serving station to a seated customer, who is "fed" for 2400 ticks.
- **Community** (VillageCommunityManager.java):
  - Healers give +4 HP with a 100-tick cooldown. Rescuers help villagers at ≤35% HP (+3 HP).
  - **Expeditions:** a cartographer walks 28–48 blocks out by day (chance 1/40 per check, only before 10000). The trip ends
    on arrival or after 900 ticks. It returns with 4–12 items or 1–2 emeralds, then waits 2–3 days (48000 + rand 24000).
- **LLM chat:** CloudAiClient.java posts to `https://api.openai.com/v1/responses` (overridable via env
  `SMART_VILLAGERS_AI_URL`); HTTPS only.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| **Round-robin batch of N people per pass** (sorted ids, rotating offset) | In pw_civ_clock/walk: update ≤N bodies per tick-slot with a rotating cursor; bounds script time per tick (watchdog) regardless of population | S | 5 |
| **Stall/repath rule** (no distance gain 80 ticks → repath, ≤3, hard cap 1200) | Lead-walker in pw_civ_walk keeps bestDist/lastGain; on stall re-run A* from current node; give up → task back to the job board | S | 4 |
| **Festivals in the square** (fair / wedding tied to an actual marriage / victory after a raid), ring formation, 3–5 day cadence | Clock event: gather present adults to ring slots around the square centre (angle = id·47°); wedding uses the census marriage; mood + to attendees | M | 4 |
| Mayor/council decision from stock thresholds, announced | The palace/town-hall leader reads the ledger daily: "expand" vs "gather timber/stone" changes worker allotment and is spoken at the dusk speech | S | 3 |
| Shop **dirt counter** (≥8 closes until cleaned) and staff experience → faster service | Counters in pw_civ_shop: per-shop dirt +1 per sale, a sweeper job, clerk exp shortens service time | M | 3 |
| Natural-tree test before felling (≥6 natural leaves, ≤64 logs) | Guard in woodcutter `nextTree` against felling planted/park/player trees (BIGCANOPY area applies) | S | 3 |
| Courier reserve (leave 8, move the surplus) between stores | Ledger-level transfers between district stores; a porter body walks the route | M | 2 |
| Expeditions (out 28–48 blocks, back with goods, 2–3 day cooldown) | A scout/forager job that leaves town on the route graph and returns; goods appear in the ledger | M | 2 |

---

### Kingdoms: Villager Retaliation! (Java, NeoForge 1.21.1, 1.0.0-beta.13-hotfix.1; licence All Rights Reserved (mods.toml + ledger); files examined: decompiled classes listed below)

**What it does.** Overhauls vanilla villagers. Each villager has a persistent profile (5 social attributes and 18 skills),
moods that decay, a family tree and romance stages, per-villager reputation with gossip, village event memory, and
retaliation or fleeing. It also has a large dialogue and quest layer.

**Mechanisms found**

- **Social attributes** (profile/VillagerSocialAttribute*.java, VillagerProfileGenerator.java):
  - KNOWLEDGE, GUTS, PROFICIENCY, KINDNESS, CHARM, each 1–100. Ranks: poor 1–19, modest, average, strong, exceptional 80+.
  - New villager: 35–65 each, plus a profession bias (e.g. librarian +16 knowledge +6 charm; armorer +13 guts
    +10 proficiency), plus jitter of ±5. An 8% outlier gets ±15–25 on one attribute.
  - **Child:** round(parentAvg×0.55 + generated×0.30 + environmentRoll(35–65)×0.15) ± 6.
  - Effect on behaviour: `scaledOffset = round((value−50)/50 × maxOffset)`.
- **Moods** (mood/VillagerMoodService.java, VillagerMoodState.java):
  - **One primary mood**: GRATEFUL, CONTENT, HOPEFUL, AFRAID, ANGRY, PROTECTIVE, SUSPICIOUS, GRIEVING, STRESSED, PROUD,
    LONELY or NEUTRAL. It stores intensity 0–100, a cause tag, the source and a decay length.
  - **Lazy decay:** on read, intensity −= 100·elapsed/decayTicks. Nothing ticks.
  - **Merge rule:** the same mood becomes max(new, old + new/4); a different mood replaces the current one only if
    new ≥ current.
  - Decay lengths: SHORT 4800, MEDIUM 14400, LONG 36000.
  - Triggers: player attack ANGRY 62/long; hostile attack 44/medium; damage STRESSED 32/short; a villager's death makes
    witnesses GRIEVING 50 or PROTECTIVE 64 if a player did it (long); fleeing AFRAID 38/short; surviving a raid PROUD 46.
  - Attributes change intensity and decay. Kindness lengthens good moods by up to +18%; guts shortens fear by up to −25%.
- **Skills** (skill/VillagerSkill*.java, VillagerSkillProgressionService.java):
  - 18 skills (farming … diplomacy, survival). Start values: primary 44–72, secondary 26–58, unrelated 8–35, with
    1–3 standouts and a 14% outlier (+18–40).
  - **XP for the next point** = 2 + (skill/20)^1.35.
  - **Daily soft cap:** the first 6 XP per skill per day count fully; the rest ×0.2.
  - **Repetition:** the same action more than 8 times per day counts ×0.35 (up to 64 repetition keys per skill).
- **Family and romance** (social/VillagerSocialGraphSavedData.java, VillagerRelationshipStage.java,
  VillagerBreedingPolicy.java):
  - Stages: CRUSH, DATING, ENGAGED, MARRIED (exclusive), SEPARATED, WIDOWED.
  - **Compatibility is a deterministic hash** of the two UUIDs: 35 + floorMod(h, 66), so nothing is stored.
  - Default affection by stage: crush max(15, c/3), dating max(35, c/2), engaged max(65, c), married max(80, c).
  - Family tree goes 10 generations up and 10 down. Breeding is blocked for close relatives, for villagers that are hired,
    in a party, working, in combat, panicking or downed. Vanilla breeding can be turned off.
- **Reputation and gossip** (reputation/*.java):
  - Per-villager levels: TRUSTED ≥35, RESPECTED ≥70, REVERED ≥100, ROYALTY ≥150, SUSPICIOUS ≤−20, HOSTILE ≤−50, plus
    DESPISED and FEARED.
  - Event types: direct hit, witnessed hit/kill/baby kill/golem kill, container break, trade, dialogue, gift, heal, save,
    gossip. Config keys exist for each; the default numbers are **not found** (bound by name in VillagerRetaliationConfig,
    no defaults file in the jar).
  - **Gossip:** a source spreads at most once per 600 ticks to its nearest 4 (+0–2 with charm, max 6) same-community
    villagers within `gossipRadius` (+0–4 with charm). Amount = original × multiplier × (1 ± charm/knowledge influence,
    clamped 0.75–1.25), at least ±1.
  - High reputation gives a trade discount of (0.3 + 0.0625·amplifier) × base cost.
- **Village event memory** (village/VillageEventMemory.java): events tagged (gift, cure, theft, kill, retaliation…) with a
  TTL of 12000 ticks, deduplicated within a 48-block radius, at most 80 per bucket. Dialogue refers back to them.
- **Traffic** (villager/VillagerTrafficService.java):
  - A conflict is a villager within 1.7 blocks ahead (lateral < 0.85, forward 0.05–1.65).
  - **Same direction** (dot ≥ 0.65): the follower slows to ×0.25.
  - **Head-on:** the higher UUID yields. It sidesteps 0.9 blocks to its right, or to the left if blocked, for 10 ticks; if
    neither is free it holds for 5 ticks. Cooldown 10 ticks.
- Doors: VillagerDoorCoordinator closes the doors a villager opened, using a reach of 2.25 blocks.

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| **Lazy-decaying single primary mood** (mood, intensity, cause, since, decay) | 5 small fields per person in the census; decay computed when read (no daily loop), merge rule as above. Cheap for dynamic-property budget; the cause tag gives the "why" for bubbles and dialogue | S | 4 |
| **Skill XP curve with daily soft cap and repetition decay** | Replace linear `skillDays` with XP = 2+(s/20)^1.35 per point, 6 XP/day full rate then ×0.2 — masters emerge slowly, spam doesn't help | S | 3 |
| **Deterministic pair compatibility** from the two ids | `compat(a,b) = 35 + hash(a,b) mod 66` — gates `marryFond`; no storage | S | 3 |
| Five personality attributes with child = 0.55 parents + 0.30 roll + 0.15 environment | Per person 5 bytes; kindness/charm scale rumour spread (receivers 4–6) and mood decay | M | 3 |
| **Street traffic yielding** (follow ×0.25; head-on: higher id sidesteps right 0.9 for 10 ticks) | Lead entities on 13-wide streets: a keep-right lane offset in the route graph handles most; the yield rule handles the rest in pw_civ_walk | M | 3 |
| Gossip: nearest 4–6 receivers, once per 600 ticks per source | CIVITAS rumours already pass friend to friend; cap receivers and rate per source to bound cost | S | 2 |
| Village event memory with TTL and dedupe radius | Already covered by rumours (`rumourDays: 30`); add a dedupe radius for repeated events | S | 2 |

---

### Arc Quest (Java, NeoForge 1.21.1 v1.0.8; requires Ponder, optional Xaero minimap; licence All Rights Reserved (mods.toml); files examined: listed below)

**What it is.** A **player quest framework**, not a village mod. It provides quest journal, tracking HUD, quest markers,
NPC dialogue (credits P1nero's dialogue lib), trade shops with "gacha", a collection codex and guides. Its built-in content
is a demo "epic mainline": prologue *defend the village* (slay 10 besieging zombies), chapter 1 caves, chapter 2 nether or
ocean branch, finale ender dragon. NPCs: epic_village_elder, epic_village_guard, epic_blacksmith, merchants
(lang en_us.json).

**Mechanisms found**

- **Quest spec** (quest/spec/*.java, field lists via javap):
  - QuestSpec: id, category, repeatable, allowAbandon, mode, initialPhaseId(s), **phases**, unlockConditions,
    completionRewards.
  - PhaseSpec: objectives, **transitions**, **choices**, phaseRewards, flags to set on enter/complete, guides to grant,
    related/tracking marks, tradeShopId, intelSceneId.
  - ObjectiveSpec: id, type, targetId, requiredCount, hidden, optional, npcId, itemTag, x/y/z/radius,
    countMode/countBase/countPerLevel (scaling counts).
  - TransitionSpec: target phase(s) plus a condition.
  - ChoiceSpec: text, flagToSet, targetPhaseId, visibleCondition.
  - ConditionSpec: type, flag, questId, variable, compareOp, value, left/right (a boolean tree).
- **Cooldowns** (core/time/CooldownMode, CooldownPolicy): NONE, REAL_TIME, GAME_DAY, GAME_TICK, plus value and resetTick.
- No quest data files ship in the jar. The demo content is defined in code (registry/EpicMainlineDemo, CollectionCodexDemo).

**Usable for CIVITAS**

| Idea | How on Bedrock | Effort | Value |
|---|---|---|---|
| CIVITAS "threads" as tiny phase graphs (phase → objectives → transitions on conditions → choices that set flags) with GAME_DAY cooldowns | A JSON thread table in the BP; the town's needs generate objectives (bring 64 stone to the quarry store; meet the surveyor at X,Y,Z r 5); flags feed rumours/mood | M | 2 |
| Objective counts that scale with level (`countBase + countPerLevel·tier`) | Town requests scale with tier (village → metropolis) | S | 2 |

---

## Top ideas from this group (ranked)

1. **Weighted growth chooser** (Millénaire): tier-gated plan slots (multipliers 6/4/2/1) and upgrade conversions compete in
   one weighted pool. One stored pending project; an affordable fallback when it can't be paid for; a no-candidate cache
   (600 ticks); a per-plan site-fail cooldown (1600 ticks); max 2 simultaneous works. Replaces the fixed leftover order in
   `planDay`. M / 5.
2. **Building cost computed from the .mcstructure palette at pack build time** (Millénaire BuildingCostCalculator rules:
   planks/4 → logs, panes 6/16, slabs ½, terrain free), with ledger gating before launch. S / 5.
3. **Buildings declare resident and job slots** (Millénaire). People coming of age or arriving take free slots by move-in
   priority; with no slot they migrate to a friendly town. Jobs follow construction. M / 5.
4. **Round-robin batching of N bodies per pass plus a no-progress watchdog and stall/repath rule** (Smart Villagers
   FairVillagerScheduler; Millénaire 6000-tick watchdog; stall 80 ticks, ≤3 repaths, cap 1200). Bounds script time per
   tick. S / 5.
5. **Need bubbles** over bodies (TekTopia thoughts: no bed, hungry, no tool, crowded, insomnia, wants tavern), shown as a
   nameTag glyph or RP particle from the census's top unmet need. Serves observation-first testing. S / 5.
6. **Plot acceptance by footprint error budget + altitude window + reachability to the street graph** (Millénaire:
   10 cells / 5% / 10%, baseline ±10, flood fill). Accept or reject only; no terraforming needed. M / 4.
7. **Data-driven visits with time windows**, including the **leader's dusk speech** (9000–10000) with listeners in the
   square and tavern drinking after 10000 (Millénaire visit_goal). M / 4.
8. **Lazy-decaying single primary mood** with cause tag and merge rule (Villager Retaliation: decay 4800/14400/36000).
   Small state, no daily loop. S / 4.
9. **Zero-sum market price drift** from a rolling sales window of 30–50 sales (TekTopia ItemEconomy): sold item −10–30%,
   others marked up by base value. S / 4.
10. **Production caps and reserved/target stock levels per good** (Millénaire `townhallLimit` 4096 logs;
    `reserved_quantity` 128 / `target_quantity` 1024). S / 4.
11. **Festivals in the square** (Smart Villagers: every 3–5 days, fair / wedding tied to a real marriage / victory, ring
    slots at angle id·47°, 1800 ticks). M / 4.
12. **Exclusive worker block claims** for trees and quarry faces (TekTopia `requestBlock`). S / 4.
13. **Personal schedule offsets** of ±200 ticks per person so the town doesn't move in lock-step (TekTopia `sleepOffset`).
    S / 4.
14. **Skill XP curve** 2+(s/20)^1.35 with a daily soft cap (6 XP, then ×0.2) and repetition decay (×0.35 after 8 per day)
    (Villager Retaliation). S / 3.
15. **Food-linked births and child growth** (Millénaire: base 2/10 + luxury food bonus, max 2 children per home, growth fed by
    household food) and a **birth chance rising with happiness and falling with size** (TekTopia 1/(15+N+…)). S / 3.
16. **Street traffic yielding** on 13-wide streets (Villager Retaliation: follower ×0.25; head-on, higher id sidesteps right
    0.9 for 10 ticks). M / 3.
17. **Typed, capped town chronicle** (Millénaire, 500 entries: founded, building, upgrade, birth, death, came of age,
    merchant, migration), readable in-game. S / 3.
18. **Inter-town merchants and nightly diplomacy drift** (Millénaire: inn merchants move after ≥2 nights within
    2000 blocks; drift 10%/pair ±10–19). Only once CIVITAS runs 2+ towns. M / 3.

## Files examined

Brief and ledgers
- /home/claude/_docs/research/civmods/BRIEF.md
- /home/claude/_intake/civmods/source/LEDGER.json
- /home/claude/_intake/civmods/modrinth/LEDGER.json
- /home/claude/_intake/civmods/curseforge/LEDGER.json
- /home/claude/_intake/civmods/manual/list.tsv

Millénaire (source/Leviaria__Millenaire.tar.gz)
- README.md
- LICENSE
- src/main/java/org/millenaire/TickConstants.java
- src/main/java/org/millenaire/ReputationConstants.java
- src/main/java/org/millenaire/village/VillageGrowthManager.java
- src/main/java/org/millenaire/village/Village.java
- src/main/java/org/millenaire/village/VillageManager.java
- src/main/java/org/millenaire/village/NightActionHelper.java
- src/main/java/org/millenaire/village/ResidentSlotManager.java
- src/main/java/org/millenaire/village/BuildingFinalizer.java
- src/main/java/org/millenaire/village/GoodsRestockHelper.java
- src/main/java/org/millenaire/village/MarketManager.java
- src/main/java/org/millenaire/village/VillageDiplomacyHelper.java
- src/main/java/org/millenaire/village/LocalMerchantHelper.java
- src/main/java/org/millenaire/village/VillageRelations.java
- src/main/java/org/millenaire/village/ControlledProjectsService.java
- src/main/java/org/millenaire/village/BuildingPurchaseService.java
- src/main/java/org/millenaire/village/VillageEventType.java
- src/main/java/org/millenaire/village/path/VillagePathManager.java
- src/main/java/org/millenaire/building/BuildingCostCalculator.java
- src/main/java/org/millenaire/building/GoodAvailabilityHelper.java
- src/main/java/org/millenaire/culture/BuildingPlanSetLoader.java
- src/main/java/org/millenaire/commerce/TradeMenu.java
- src/main/java/org/millenaire/commerce/TradeGoodsLoader.java
- src/main/java/org/millenaire/config/MillenaireServerConfig.java
- src/main/java/org/millenaire/goal/GoalScheduler.java
- src/main/java/org/millenaire/goal/VillagerGoal.java
- src/main/java/org/millenaire/goal/GoalRegistry.java
- src/main/java/org/millenaire/goal/PerVillagerThrottle.java
- src/main/java/org/millenaire/goal/impl/BuildGoal.java
- src/main/java/org/millenaire/goal/impl/ChildBecomeAdultGoal.java
- src/main/java/org/millenaire/goal/impl/RestGoal.java
- src/main/java/org/millenaire/goal/impl/ChatGoal.java
- src/main/java/org/millenaire/goal/impl/SocialiseGoal.java
- src/main/java/org/millenaire/goal/impl/GetGoodsForHouseholdGoal.java
- src/main/java/org/millenaire/goal/impl/IdleGoal.java
- src/main/java/org/millenaire/goal/impl/SellerGoal.java
- src/main/java/org/millenaire/goal/impl/GetResourcesForShopsGoal.java
- src/main/java/org/millenaire/goal/impl/DeliverResourcesToShopGoal.java
- src/main/java/org/millenaire/goal/impl/BringBackHomeGoal.java
- src/main/java/org/millenaire/goal/impl/LightHearthGoal.java
- src/main/java/org/millenaire/goal/impl/PlayGoal.java
- src/main/java/org/millenaire/goal/impl/VisitBuildingGoal.java
- src/main/java/org/millenaire/world/BuildingLocationFinder.java
- src/main/java/org/millenaire/world/PlacementConstraints.java
- src/main/java/org/millenaire/world/VillageTerrainMap.java
- src/main/java/org/millenaire/world/TerrainReachability.java
- src/main/resources/millenaire/docs/content-guide.en.md
- src/main/resources/millenaire/templates/_template_village_type.json
- src/main/resources/millenaire/cultures/byzantines/villages/tradingvillage.json
- src/main/resources/millenaire/cultures/norman/buildings/houses/carpenterhouse.json
- src/main/resources/millenaire/cultures/norman/buildings/houses/farm.json
- src/main/resources/millenaire/cultures/norman/buildings/townhalls/manor.json
- src/main/resources/millenaire/cultures/norman/villagers/normalvillagers/farmer.json
- src/main/resources/millenaire/cultures/norman/traded_goods.json
- src/main/resources/millenaire/cultures/norman/shops/bakery.json
- src/main/resources/millenaire/cultures/norman/shops/townhall.json
- src/main/resources/millenaire/cultures/norman/reputation.json
- src/main/resources/millenaire/cultures/norman/culture_reputation.json
- src/main/resources/millenaire/visit_goal/drink_cider.json
- src/main/resources/millenaire/visit_goal/observe_construction.json
- src/main/resources/millenaire/visit_goal/give_speech.json
- src/main/resources/millenaire/visit_goal/listen_to_speech.json
- src/main/resources/millenaire/visit_goal/patrol.json
- src/main/resources/millenaire/gathering_type/chop_trees.json
- src/main/resources/millenaire/villager_config/default.json
- src/main/resources/millenaire/languages/en_us/norman_sentences.txt
- src/main/resources/millenaire/languages/en_us/norman_dialogues.txt

TekTopia (curseforge/tektopia__tektopia-1.1.0.jar)
- net/tangotek/tektopia/entities/EntityVillagerTek.class (decompiled)
- net/tangotek/tektopia/entities/EntityVillagerTek$VillagerThought.class (javap)
- net/tangotek/tektopia/entities/EntityNomad.class (decompiled)
- net/tangotek/tektopia/entities/EntityChild.class (decompiled)
- net/tangotek/tektopia/entities/EntityLumberjack.class (decompiled)
- net/tangotek/tektopia/entities/EntityFarmer.class (decompiled)
- net/tangotek/tektopia/entities/ai/EntityAIEatFood.class (decompiled)
- net/tangotek/tektopia/entities/ai/EntityAISleep.class (decompiled)
- net/tangotek/tektopia/entities/ai/EntityAIChopTree.class (decompiled)
- net/tangotek/tektopia/structures/VillageStructure.class (decompiled)
- net/tangotek/tektopia/structures/VillageStructureType.class (decompiled)
- net/tangotek/tektopia/structures/VillageStructureHome.class (decompiled)
- net/tangotek/tektopia/structures/VillageStructureTownHall.class (decompiled)
- net/tangotek/tektopia/economy/ItemEconomy.class (decompiled)
- net/tangotek/tektopia/economy/ItemValue.class (decompiled)
- net/tangotek/tektopia/Village.class (decompiled)
- net/tangotek/tektopia/ProfessionType.class (decompiled)
- net/tangotek/tektopia/NomadScheduler.class (decompiled)
- net/tangotek/tektopia/MerchantScheduler.class (decompiled)

Tale of Kingdoms (source/SamB440__Tale-of-Kingdoms.tar.gz; manual/taleofkingdoms-1.0.0.jar)
- LICENSE
- src/main/java/com/convallyria/taleofkingdoms/common/kingdom/KingdomTier.java
- src/main/java/com/convallyria/taleofkingdoms/common/kingdom/builds/BuildCosts.java
- src/main/java/com/convallyria/taleofkingdoms/common/kingdom/poi/KingdomPOI.java
- src/main/java/com/convallyria/taleofkingdoms/common/kingdom/PlayerKingdom.java
- src/main/java/com/convallyria/taleofkingdoms/common/entity/guild/CityBuilderEntity.java
- src/main/java/com/convallyria/taleofkingdoms/common/entity/kingdom/ForemanEntity.java
- src/main/java/com/convallyria/taleofkingdoms/common/entity/kingdom/StockMarketEntity.java
- src/main/java/com/convallyria/taleofkingdoms/common/entity/ai/goal/GatherResourcesPassivelyGoal.java
- src/main/java/com/convallyria/taleofkingdoms/common/entity/ai/goal/WanderAroundKingdomGoal.java
- src/main/java/com/convallyria/taleofkingdoms/common/listener/MobDeathListener.java
- src/main/java/com/convallyria/taleofkingdoms/common/listener/CoinListener.java
- src/main/java/com/convallyria/taleofkingdoms/common/entity/guild/GuildGuardEntity.java
- src/main/java/com/convallyria/taleofkingdoms/common/entity/guild/LoneEntity.java
- taleofkingdoms-1.0.0.jar: fabric.mod.json

Civilians (modrinth/civilians__civiliansmod-v1.4.2+1.21.5.jar; manual/civiliansmod-v1.4.2+1.21.1.jar listing only)
- LICENSE_civiliansmod
- net/asian/civiliansmod/entity/NPCEntity.class (decompiled)
- net/asian/civiliansmod/entity/goal/CustomDoorGoal.class (decompiled)
- net/asian/civiliansmod/chat/NpcChat.class (decompiled)
- net/asian/civiliansmod/NPCConversionHandler.class (decompiled)

Smart Villagers (manual/smart-villagers-0.24.2-forge-1.21.11.jar)
- META-INF/mods.toml
- assets/smartvillagers/lang/en_us.json
- ru/user/smartvillagers/work/FairVillagerScheduler.class (decompiled)
- ru/user/smartvillagers/work/VillageMayorManager.class (decompiled)
- ru/user/smartvillagers/work/VillageFestivalManager.class (decompiled)
- ru/user/smartvillagers/work/VillageProgressManager.class (decompiled)
- ru/user/smartvillagers/work/VillageConstructionData.class (decompiled)
- ru/user/smartvillagers/work/BusinessWork.class (decompiled)
- ru/user/smartvillagers/work/VillageWorkManager.class (decompiled)
- ru/user/smartvillagers/work/CivicBlueprints.class (decompiled)
- ru/user/smartvillagers/work/CloudAiClient.class (decompiled)
- ru/user/smartvillagers/work/VillageCommunityManager.class (decompiled)
- ru/user/smartvillagers/config/SmartVillagersConfig.class (decompiled)

Kingdoms: Villager Retaliation (modrinth/villager-retaliation__villager_retaliation-neoforge-1.21.1-1.0.0-beta.13-hotfix.1.jar)
- META-INF/neoforge.mods.toml
- com/jvn/villagerretaliation/profile/VillagerSocialAttribute.class (decompiled)
- com/jvn/villagerretaliation/profile/VillagerSocialAttributeRank.class (decompiled)
- com/jvn/villagerretaliation/profile/VillagerProfileGenerator.class (decompiled)
- com/jvn/villagerretaliation/profile/VillagerSocialAttributeBehavior.class (decompiled)
- com/jvn/villagerretaliation/mood/VillagerMoodService.class (decompiled)
- com/jvn/villagerretaliation/mood/VillagerMoodState.class (decompiled)
- com/jvn/villagerretaliation/social/VillagerRelationshipStage.class (decompiled)
- com/jvn/villagerretaliation/social/VillagerSocialGraphSavedData.class (decompiled)
- com/jvn/villagerretaliation/social/VillagerBreedingPolicy.class (decompiled)
- com/jvn/villagerretaliation/skill/VillagerSkill.class (decompiled)
- com/jvn/villagerretaliation/skill/VillagerSkillGenerator.class (decompiled)
- com/jvn/villagerretaliation/skill/VillagerSkillGrowthService.class (decompiled)
- com/jvn/villagerretaliation/skill/VillagerSkillRank.class (decompiled)
- com/jvn/villagerretaliation/skill/VillagerSkillProgressionService.class (decompiled)
- com/jvn/villagerretaliation/reputation/VillagerReputationLevel.class (decompiled)
- com/jvn/villagerretaliation/reputation/VillagerReputationTradePricing.class (decompiled)
- com/jvn/villagerretaliation/reputation/ReputationEventType.class (decompiled)
- com/jvn/villagerretaliation/reputation/VillagerGossipHooks.class (decompiled)
- com/jvn/villagerretaliation/reputation/VillagerReputationManager.class (decompiled)
- com/jvn/villagerretaliation/village/VillageEventMemory.class (decompiled)
- com/jvn/villagerretaliation/villager/VillagerTrafficService.class (decompiled)
- com/jvn/villagerretaliation/villager/VillagerDoorCoordinator.class (decompiled)
- com/jvn/villagerretaliation/villager/VillagerSleepHealingService.class (decompiled)
- com/jvn/villagerretaliation/config/VillagerRetaliationConfig.class (javap)

Arc Quest (manual/arc_quest-neoforge1.21.1-1.0.8.jar)
- META-INF/neoforge.mods.toml
- assets/arc_quest/lang/en_us.json
- org/arcadia/arc_quest/quest/spec/QuestSpec.class (javap)
- org/arcadia/arc_quest/quest/spec/PhaseSpec.class (javap)
- org/arcadia/arc_quest/quest/spec/ObjectiveSpec.class (javap)
- org/arcadia/arc_quest/quest/spec/TransitionSpec.class (javap)
- org/arcadia/arc_quest/quest/spec/ChoiceSpec.class (javap)
- org/arcadia/arc_quest/quest/spec/RewardSpec.class (javap)
- org/arcadia/arc_quest/quest/spec/ConditionSpec.class (javap)
- org/arcadia/arc_quest/core/time/CooldownMode.class (javap)
- org/arcadia/arc_quest/core/time/CooldownPolicy.class (javap)
- org/arcadia/arc_quest/quest/registry/ObjectiveTypeRegistry.class (javap)

CIVITAS (read for context only)
- /home/claude/tools/bp02_src_227/pw_civ_people.js (header: DIALS, LEARN)
- /home/claude/tools/bp02_src_227/pw_civ_clock.js (planDay)
- /home/claude/_docs/GROWTH-PROGRAM-2026-10-05.md (headings)
