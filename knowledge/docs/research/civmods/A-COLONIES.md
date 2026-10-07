# A-COLONIES — MineColonies and its family (study for CIVITAS, 2026-10-06)

Group items: MineColonies (main study object), Structurize, Domum Ornamentum, MineColonies War N Taxes, Mind Of The Colony,
Talking Colonists.
Every mechanism below comes from a file I opened (named inline). "Not found" is stated where I looked and found nothing.
Licences are as shown in the files (LICENSE / META-INF/mods.toml) and in the intake LEDGER.json. All are fine to STUDY for
personal use; we write our own Bedrock code and copy no code.

Effort: S = under a day of script work, M = a few days, L = a week or more. Value: 1 (nice) to 5 (changes how towns look or play).
"Verify" marks a Bedrock API feature I did not confirm in a file here (the typings in bp02_src_227/node_modules are stubs).

Where CIVITAS already does something, I say so, from the file I read:
- `pw_civ_people.js`: mood 0..100 smoothed 0.7/0.3; leaving after `leaveDays`; the faucet; rumours told friend to friend; trust learning.
- `pw_civ_economy.js`: the ledger in pennies, `WAGE`, `stageBill`, `pay`.
- `pw_civ_clock.js` around line 577: stage templates `pw:stages/<stem>_s<k>`, placed with `StructureAnimationMode.Layers`.

---

### MineColonies (Forge 1.20.1 source, branch with forgeVersion 47.1.3, commit 503b5fd; licence GPL-3.0 (LICENSE); files examined: see list. The 1.21.1 jar in manual/ and the 1.18.2 jar in modrinth/ were NOT opened — the source covered every topic)

- **What it does:** the player places "huts". Builder citizens construct and upgrade them (levels 1–5) from blueprints.
  - Citizens live in residences, work in huts, eat, sleep and fall sick.
  - A request system moves items from warehouses to whoever needs them, carried by couriers.
  - A research tree, raids and guards add progression and threat.

#### Mechanisms found

**1. Citizen happiness (0–10)** (`CitizenHappinessHandler.java`, `HappinessConstants.java`, `ModHappinessFactorTypeInitializer.java`, `TimeBasedHappinessModifier.java`)
- **Formula:** happiness = min(10, 10 × Σ(factorᵢ·weightᵢ) / Σ weightᵢ × (1 + research HAPPINESS)).
  - **Factors that equal exactly 1.0 are SKIPPED** (both numerator and denominator), so only the factors that actually deviate decide the score.
  - The result is cached until a modifier changes.
- **Static factors** (weight → function):

| Factor | Weight | Function |
|---|---|---|
| school | 1.0 | child pupil 2.0, other child 0, adult 1.0 |
| security | 4.0 | min(guards/(workers·2/3), 2); both counts start at 1 |
| social | 2.0 | (total − unemployed − homeless − sick − hungry(saturation ≤ 1)) / total |
| mysticalsite | 1.0 | max(1, maxMysticalSiteLevel/2) |
| food | 3.0 | see below |

- **Time-based factors.** These escalate with days spent below 1.0:

| Factor | Weight | Base function | Escalation |
|---|---|---|---|
| homelessness | 3.0 | home level / 3, or 0 with no home | ×0.75 after 7 days, ×0.5 after 14 |
| unemployment | 2.0 | no job 0.5; work hut > level 3 → 2.0; else 1.0 | ×0.75 after 7 days, ×0.5 after 14 |
| health | 2.0 | sick 0.5 | ×0.5 after 7 days, ×0.1 after 14 |
| idleatjob | 1.0 | 0.5 when idle | ×0.5 after 7 days, ×0.1 after 14 |
| slepttonight | 1.5 | guards 1, others 0.5 | 0 days → ×2, 2 days → ×1.6, 3 → ×1 |

  - `TimeBasedHappinessModifier.getFactor`: the multiplier applies only while the base is < 1; the day counter rises at `dayEnd`.
  - `EntityAISleep` resets "slepttonight" when the citizen sleeps.
- **Expiring factors** (`ExpirationBasedHappinessModifier`, fixed value for N days):

| Event | Weight | Value | Days | Set in |
|---|---|---|---|---|
| ate great food | 2.0 | 2.0 | 5 | `ItemStackUtils` |
| damaged | 2.0 | 0.0 | 1 | `EntityCitizen` |
| a death in the colony, applied to all | 3.0 | 0.0 | 3 | `EntityCitizen` |
| raid ended with no deaths | 1.0 | 2.0 | 3 | `RaidManager` |
| quest reward | 2.0 | qty | N | `HappinessRewardTemplate` |

- **Food factor** (`getFoodFactor`, `CitizenFoodHandler`):
  - The last **10** foods eaten are kept (an EvictingQueue).
  - diversity = number of unique foods; quality = number of mod "quality" foods.
  - factor = (min(5, diversity/homeLevel) + min(5, quality/max(1, homeLevel−2))) / 2.
  - The factor is neutral (1.0) until the history is full or while homeless.
  - A better house therefore DEMANDS a more varied, better diet.
  - Disease chance × 0.5·min(2.5, 5/diversity).
- **Where happiness acts:**
  - Colony overall = mean of the citizens (`Colony.getOverallHappiness`), 5.5 when empty.
  - New citizens' random skill cap = overall×2, at least 5 while below the initial 4 (`CitizenData.initForNewCivilian`).
  - Children get a cap of overall happiness + 25–49 bonus points split by the parents' skills (`CitizenSkillHandler.init`).
  - Intelligence can only level while < happiness×9 (`tryLevelUpIntelligence`).
  - Daily, `processDailyHappiness` fires chat "complaints" (NO+id) and "demands" (DEMANDS+id) as citizen interactions.

**2. Needs: food, sleep, housing**
- **Food** (`CitizenAI.shouldEat`, `EntityAIEatTask`, `CitizenConstants`):
  - MAX_SATURATION 60; AVERAGE 10; LOW 6; RESTAURANT_LIMIT 2.5.
  - A citizen eats when saturation ≤ 10 AND (≤ 2.5, or < 6 with health < 6).
  - Order: home hut → restaurant (staffed cook) → wait 2 min → fetch it themselves (GET_YOURSELF_SATURATION 30); re-check every 5 min.
  - Work drains saturation 0.02 per continuous action and 0.2 per "big" action (`EntityCitizen`).
- **Sleep and schedule** (`CitizenAI.calculateNextState`, `CitizenSleepHandler`, `WorldUtil`):
  - NIGHT = 12600 ticks of day time; NOON = 6000.
  - A citizen goes to bed when (NIGHT + research "work longer" ×1000 − now) < travelTime.
    - travelTime = (√(dx² + dz² + (1.5·dy)²) + distance to work) × **6 ticks per block**.
    - So people leave work EARLY enough to arrive home by night; a far home means an earlier walk.
  - If home↔work > **160 blocks** the citizen complains "home too far".
- **State priority** each decision (every 10 ticks):
  1. guards: eat / sick / work
  2. sick at hospital
  3. **raid → everyone sleeps (hides)**
  4. night → sleep
  5. sick or hurt
  6. eat
  7. mourning
  8. **rain → idle**, unless the hut "can work in rain" or the research is done
  9. pupils go home after noon
  10. work, unless leisure time > 0
  11. idle
- **Leisure** (`CitizenData.update`): each tick a random roll gives on average one leisure period per 60/(homeLevel/2) minutes, and the period lasts **3 min**.
  - A better house → more free time.
- **Housing** (`LivingBuildingModule`, `CitizenManager.calculateMaxCitizens`, `ReproductionManager`, `RegisteredStructureManager.getHouseWithSpareBed`):
  - Beds = **house level** (1–5).
  - Colony capacity = Σ beds of residences (a locked house counts only its residents), then clamped:
    - research CITIZEN_CAP: default 25; the "outpost/hamlet/village/city" research raises it to 50/100/150/500 (`effects/citizencapaddition.json` levels 25, 50, 100, 150, 500);
    - config maxCitizenPerColony 250.
- **Choosing a home** (not found: any preference, distance or quality rule): each colony tick every non-full house "captures" homeless citizens in iteration order. Births go to the FIRST house with a spare bed.
- **Skill cap by house** (`CitizenSkillHandler.addXpToSkill`):
  - A skill stops gaining XP at **(homeLevel + 1) × 10** while the home is below its max level; the hard cap is 99.
  - XP to the next level = 1 + mult·5·L + 0.005·L³ (`ExperienceUtils`).
  - **Housing quality gates expertise.**

**3. Births** (`ReproductionManager`)
- **Timer:** (5 min + rand(10 min)) × (pop / max(4, maxPop)). Fuller colonies breed slower.
- **Needs:** a spare bed, a male and a female present, and pop ≥ min(2, initial 4).
- **Parents:**
  1. A random adult of the bed's house.
  2. Their partner; else a non-related unpartnered housemate (50 %).
  3. Else someone from another house **within 50 blocks**.
- The two parents become partners.
- **The child:** joins the parents' sibling lists, inherits a skin suffix, and is named from the colony name file (`citizennames/*.json`: parts, order, first names, surnames).

**4. Request system** (`api/colony/requestsystem/*`, `RequestHandler.assignRequestDefault`, `RSConstants`)
- **A request** moves through these states:
  - CREATED → REPORTED → ASSIGNING → ASSIGNED → IN_PROGRESS → RESOLVED → FOLLOWUP_IN_PROGRESS → COMPLETED / RECEIVED;
  - also CANCELLED, OVERRULED, FAILED and FINALIZING (`RequestState.java`).
- **Assignment:**
  1. All resolvers registered for the request's type are sorted by **priority**:
     - building 200
     - warehouse 150
     - crafting 125
     - default 100
     - retrying 50 (3 retries, 1200 ticks apart)
     - player 0
  2. The first resolver whose `canResolveRequest` passes makes an attempt.
  3. Among resolvers of the SAME priority, the one with the lowest **suitability metric** wins; the loser's child requests are cancelled.
  4. The scan stops at the first lower priority tier.
  5. `attemptResolveRequest` returns **child requests**, so a request becomes a dependency tree. Example: the warehouse has 40 of 64 → a child request for 24 goes on to crafters or the player.
- **Warehouse** (`AbstractWarehouseRequestResolver`):
  - It refuses requests from itself.
  - It sums its stock across all warehouses and accepts if ≥ the count or ≥ the minimum count.
  - Suitability = **max(distance/10, 1) + length of its delivery queue**.
  - On completion it creates **Delivery** requests: one per stack location, from the rack position to the requester.
  - The default delivery priority is 13.
- **Couriers** (`DeliverymenRequestResolver`, `JobDeliveryman.getCurrentTask`, `AbstractDeliverymanRequestable`):
  - Deliveries and pickups queue at the warehouse.
  - A free courier scores every queued task: priority = task priority + (queueLength − index) − √(manhattan(source, target)).
    - Unloaded target −1000.
    - A pickup scheduled for a future day −100.
  - It takes the best task, then **batches** other tasks with the SAME target, up to **1 + secondarySkill/5** in parallel.
  - **Aging:** every task it skipped that was older gets +1 priority, up to 14.
  - Scale: building priority ≤ 10, default delivery 13, aging cap 14, player action 15.
  - Courier speed bonus 0.003 per level; inactivity limit 600.
- **Pickups** (`AbstractBuilding.createPickupRequest`):
  - When a worker dumps its inventory, its hut asks for a pickup.
  - pickUpDay = today + max(0, (10 − hutPickupPriority) − qty/16). Fuller and more important huts are emptied sooner.

**5. Builder AI and build order** (`AbstractEntityAIStructure`, `BuildingProgressStage`, `BuildingResourcesModule`, `WorkManager`, `WorkOrderBuilding`)
- **Stages:**

| Job | Stages |
|---|---|
| New hut | CLEAR → BUILD_SOLID → WEAK_SOLID → CLEAR_WATER → CLEAR_NON_SOLIDS → DECORATE → SPAWN (6 counted) |
| Upgrade | the same without CLEAR |
| Removal | REMOVE_WATER → REMOVE |

- **What each stage does:**
  - CLEAR and the removals iterate DOWNWARD (top layer first); the others go UPWARD.
  - BUILD_SOLID: blocks that can float in air, except decorations.
  - WEAK_SOLID: weak-solid blocks.
  - CLEAR_NON_SOLIDS: puts the blueprint's air where the world isn't empty.
  - DECORATE: the non-solid / decoration items (torches, panes, beds…).
  - SPAWN: blueprint entities.
- **Materials** come in **buckets**:
  - Needed resources are packed into buckets of at most (inventory slots − 9) stacks.
  - Only the current bucket is requested, × a batch multiplier, and only for the shortfall after the hut's and the builder's own stock.
  - The request is skipped if that item is already requested.
  - MISSING_ITEMS stops the step with NEEDS_ITEM.
- **Pace:** delay per block = 15 × 10 / (primarySkill/2 + 10) ticks × (1 − research BLOCK_PLACE_SPEED). That is 15 ticks at skill 0 and ~4.3 at skill 50.
- **Resume point:** progress (iterator position + stage) is saved, so a builder resumes where it stopped.
- **Work orders:**
  - Each colony tick, orders are sorted: claimed first, then **priority** (player-set) descending, then ID.
  - Each order goes to the first idle builder that passes `canBuild`:
    - builder hut level ≥ the target level, OR builder hut at max level (5), OR the order is the builder's own hut;
    - AND within **100 blocks** of the builder hut (MAX_DISTANCE_SQ 100²).
  - Builders set to "manual" only take orders assigned to them.
  - One open order per building (`requestWorkOrder`).
- **Upgrades** (`AbstractBuilding.requestUpgrade`):
  - Level < 5 (CONST_DEFAULT_MAX_BUILDING_LEVEL).
  - The hut's research unlock must be ≥ the next level.
  - A child building may not pass its parent unless the parent is maxed.
  - The building must be inside the world height and needs a builder in range.
- **Claim radius** (chunks) by level:
  - huts: 1, 1, 1, 2, 2 (`AbstractBuilding.getClaimRadius`);
  - town hall: 1, 1, 2, 3, 5 (`BuildingTownHall`).

**6. Hut / job levels and "colony level"**
- A **colony level** (as a single number) was NOT found. Progression is:
  - hut levels 1–5;
  - research requirements of the form "building X at level N" or "town hall (single-building) at level N";
  - the citizen cap research.
- Worker slots per hut (`BuildingModules`): most huts 1 worker; school students 2×level; university researchers = level.

**7. Research tree** (`datagen/.../researches/*.json`, 217 research files; `GlobalResearchBranch`, `ResearchConstants`)
- Four branches, each with 6 depths:

| Branch | Researches per depth 1–6 |
|---|---|
| civilian | 6/16/14/13/10/9 |
| combat | 5/11/15/13/13/11 |
| technology | 7/20/24/11/8/7 |
| unlockable | 4 |

- **Each research JSON holds:**
  - item costs, e.g. hamlet = 128 cooked beef;
  - requirements (building:level);
  - a parent research;
  - effects ("id": level);
  - an optional `exclusiveChildResearch`.
- **Time** = BASE_RESEARCH_TIME (72) × branch base-time × **2^(depth−1)**.
- **Effect tables** in `effects/*.json`:
  - happinessmultiplier 0.05/0.1/0.15/0.2/0.5
  - walkingmultiplier 0.05…0.25
  - workingdayhaddition 1/2 (hours of extra work before night)

**8. Raids and guards** (`RaidManager.java`, `ServerConfiguration.java`, `AbstractBuildingGuards.java`, `IGuardBuilding`)
- **Raid level** = Σ adults (5 + Σskills/100) + Σ built huts (5 + level²/5) + 3 × completed researches, × min(1, pop/maxPop).
- No raid below **75**.
- **Raiders** = 1 + min(maxRaiders 80, level/60 × difficultyMod × (1 + 0.05 × players nearby)).
  - difficultyMod = (difficulty/10 + 0.2) × configDifficulty × worldDifficulty/2.
- **Adaptive difficulty 1–14** (start 7), adjusted at nightfall after a raid:
  - lost > 15 % of max pop → difficulty − (lost%/15 %) and the next raid is delayed by 40 % of the average gap;
  - lost < 5 % → +1.
- **Losses:** a guard death counts 1, a civilian death 2.
- **Mercy rule:** losses > 50 % end the raid and the next one waits 2 × average.
- **Timing:**
  - At least 10 nights between raids (config), average 14.
  - Forced after average + 2 nights.
  - Otherwise each night has chance 1/(avg − min) = 1/4.
- **Spawn:** a random bearing on a 500-block circle from the centre of the loaded buildings, then walking in from the closest building (8 tries).
- **Raider targeting:** a random building, changed every max(6, raiders/3) uses. Up to 4 guards within 75 blocks are redirected to the last target building.
- **Guards:**
  - Patrol radius 50 + 30 × level; vision 15 + 3 × level; health +2/level.
  - Tasks: PATROL, GUARD, FOLLOW, PATROL_MINE.
  - Auto patrol: either a random reachable spot 20–40 blocks away or a random built building; returns to the hut if beyond the patrol radius.
- **Civilians hide** (sleep state) during raids (`CitizenAI`).

**9. Tavern visitors** (`TavernBuildingModule`)
- Up to **3 × tavern level** visitors.
- Next visitor after rand(3000) + (6000/level) × pop/maxPop (timer units).
- Each visitor carries a random recruit cost item (scaled by tavern level, +0..2) and a recruit skill level; the player pays to hire them.

**10. Quests** (`data/minecolonies/colony/quests/questschema.txt`, `quests/general/hungrycourier.json`)
- Data-driven.
- **Triggers:**
  - random (rarity, e.g. 50 000 000);
  - state match (path `buildingManager/buildings`, `{type, level}`);
  - citizen match (`{job}`);
  - unlock;
  - reputation;
  - `triggerOrder` boolean expressions.
- **Objectives:**
  - a dialogue tree: text + answers → dialogue / advanceobjective (go-to N) / cancel / return;
  - delivery (item, qty);
  - …
- **Rewards:** item; happiness (target, qty, days).
- `max-occurrences` and `parents` chain quests together.

**11. Diseases** (`colony/diseases/*.json`): a name, a rarity (influenza 100) and the cure items (carrot + potato).

#### Usable for CIVITAS

1. **Courier freight with aging + batching (visible porters)**
   - **Idea:** goods move in CIVITAS's ledger instantly today. Make the HAUL visible and paced.
     - A town "warehouse queue" of delivery jobs: quarry → site, lumberyard → site, fishery → market.
     - A carter picks the job with the best score = priority + age bonus − √(manhattan distance).
     - The carter carries up to 1 + skill/5 jobs that share a destination; skipped jobs age +1 (cap).
   - **How on Bedrock:** pure script data in the ledger (a small array of `{from, to, good, qty, pri}`).
     - The carter is a villager_v2 body with a lead entity on the existing route graph (A* in `pw_civ_walk.js`).
     - The stage only starts when its delivery arrives (extends `missing()`/`pay()`).
     - Keep at most N carters per town to bound walking cost.
   - **Effort:** M. **Value:** 4.
2. **Escalating need factors + expiring events in the mood formula**
   - **Idea:** in `pw_civ_people.js` mood is a sum of fixed terms. Borrow three things from MineColonies:
     - **days-without escalation:** homeless or jobless for 7 days → the term ×0.75 worse, 14 days → ×0.5;
     - **expiring event modifiers:** a death in town −X for 3 days to everyone; a repelled raid with no deaths +X for 3 days; a feast +X for 5 days; a quest/thread success +X for N days;
     - **"neutral factors don't count"**, so one problem is felt fully in a town otherwise fine.
   - **How on Bedrock:** person fields `homelessDays`, `joblessDays`, plus `mods: [{id, v, until}]`. They are tiny, so they fit the dynamic-property budget.
   - **Effort:** S. **Value:** 4.
3. **House quality gates rank and diet**
   - **Idea 1:** skill/rank growth caps at (homeLevel+1)×10 → in CIVITAS, a journeyman/master rank requires a better home.
     - The conversion/taller-rebuild program then pays off for the people, not only the charter.
   - **Idea 2:** the food factor scales with the home: a richer house demands diet diversity ≥ homeLevel.
     - CIVITAS has FISH, grain, meat goods.
     - Keep each household's last-10 market purchases → diversity → mood.
   - **How on Bedrock:** a homeLevel per house record (cottage 1, townhouse 2, tenement/shop-house 3, palace 5); clamp in `outputFactor`/`rankOf`; a household `diet` ring buffer of 10 good ids.
   - **Effort:** S. **Value:** 4.
4. **Leave-for-home timing and "home too far"**
   - **Idea:** the dusk walk starts when (nightTick − now) < (path length × 6 ticks + 1.5 × climb); people complain if home↔work > 160 blocks.
   - This feeds the core/outskirts rule: a far-housed worker asks to move closer, and a conversion frees a closer room.
   - **How on Bedrock:** the route graph gives the path length; schedule per person in `pw_civ_clock` instead of one town-wide dusk bell.
   - **Effort:** S. **Value:** 3.
5. **Rain idles outdoor trades; raid → everyone indoors**
   - **How on Bedrock:** `world.getDimension().getWeather()` (verify on 2.3.0), or the existing `pw_weather.js` state.
   - Farmers, quarrymen and builders go to the "home" schedule; shopkeepers keep working. On a raid alarm, civilians walk home and watchmen muster.
   - **Effort:** S. **Value:** 3.
6. **Work-order queue with priority and guild gating**
   - **Idea:** one sorted list of construction orders (claimed first, then priority, then age).
   - A builder crew may only take an order whose tier ≤ the crew's guild rank: only a master builder may raise the castle; a far crew (> N blocks) cannot claim.
   - The player can bump a priority with `/scriptevent pw:clock prio <id>`.
   - **Effort:** S. **Value:** 3.
7. **Raid level from town wealth, adaptive difficulty, mercy rule** (if he wants raids)
   - **Idea:** raid strength grows with people, skills and building levels (formula above). Difficulty walks 1–14 by the share lost, and a >50 % loss ends the raid and grants a long peace.
   - **How on Bedrock:** spawn pillager bands (vanilla entities) at a wall gate on a 500-block bearing, reduced to the loaded area. Watchmen (`pw_civ_watch.js`) redirect to the attacked building, max 4.
   - **Effort:** M–L. **Value:** 3.
8. **Data-driven quests (threads with dialogue)**
   - **Idea:** CIVITAS has THREADS. Adopt the quest schema shape:
     - triggers: rarity + state match + citizen match;
     - objectives: dialogue tree → delivery → dialogue;
     - rewards: coin + happiness for N days;
     - max-occurrences and parents.
   - **How on Bedrock:** JSON in the BP scripts (a JS object table); `@minecraft/server-ui` ActionFormData for the answers; deliveries checked from the player inventory.
   - **Effort:** M. **Value:** 4.
9. **Births need a spare bed; the partner is found within 50 blocks**
   - **Idea:** CIVITAS already keeps one room free for a birth (`pw_civ_people.js` 0.0.22). Borrow the birth timer that slows as the town fills: × pop/maxPop.
   - **Effort:** S. **Value:** 2.
10. **Inn visitors as recruitable migrants**
    - **Idea:** up to 3 × inn level travellers lodge at the inn. The player (or the council, automatically) can hire one for a cost in goods/coin; otherwise they move on.
    - This complements the mood "faucet".
    - **Effort:** M. **Value:** 3.
11. **Research tree:** low fit (CIVITAS growth is tier-driven). One borrowable piece: tier upgrades (village I → … → metropolis III) as "research" with building:level requirements and time doubling per depth.
    - **Effort:** S. **Value:** 2.

---

### Structurize (Forge 1.20.1 source commit 7dd863c + curseforge jar structurize-1.20.1-1.0.821-snapshot; licence GPL-3.0 (LICENSE, mods.toml "GPL 3.0"); files examined: see list)

- **What it does:** the blueprint library under MineColonies. It holds the `.blueprint` format, the scan/paste tools, and the placer that builds a blueprint step by step with a configurable iterator.

#### Mechanisms found

- **Blueprint format** (`BlueprintUtil.writeBlueprintToNBT`):
  - Fields: `version` 1; `size_x/y/z` (shorts); `palette` (list of block states); `blocks` (int array).
  - The `blocks` array holds the palette indices as shorts, in Y → Z → X order, two shorts packed per int (hi << 16 | lo).
  - Other fields: `tile_entities`, `entities`, `required_mods`, `name`, `architects`, `mcversion`, and `optional_data.structurize.primary_offset` (the anchor).
- **Iterators** (`StructureIterators`): "default", "inwardcircle", "inwardcircleheight1–4", "hilbert", "random". The config key `iteratorType` defaults to "default".
  - **default** (`BlueprintIteratorDefault`): layer by layer. Within a layer it walks X forward on even Z rows and backward on odd rows (serpentine). Up for building, down for clearing.
  - **inwardcircle** (`BlueprintIteratorInwardCircle`): the perimeter first, spiralling inward, per layer.
- **Skipping** (`AbstractBlueprintIterator.iterateWithCondition`):
  - A position is skipped if the stage's predicate says so, OR (when not removing) if the world block already matches the blueprint and it has no entities. That counts as "success".
  - Each call checks at most `maxBlocksChecked` (1000) positions.
- **Placer step** (`StructurePlacer.executeStructureStep`):
  - Places up to `getStepsPerCall` blocks, then returns LIMIT_REACHED with the resume position.
  - Removal in survival returns BREAK_BLOCK, so the worker mines it.
  - MISSING_ITEMS, FAIL and BREAK_BLOCK end the step.
  - Operations: BLOCK_PLACEMENT, BLOCK_REMOVAL, WATER_REMOVAL, GET_RES_REQUIREMENTS, SPAWN_ENTITY.
  - Config `maxOperationsPerTick` 1000.
- **Substitution blocks** (`ModBlocks`):
  - `blockSubstitution`: keep whatever is in the world.
  - `blockSolidSubstitution`: fill with a solid "ground".
  - `blockFluidSubstitution`.
  - `blockTagSubstitution`.
- **Solid fill rule** (`BlockUtils.getSubstitutionBlockAtWorld`):
  1. The worldgen block at that spot.
  2. Powder snow → snow block.
  3. If it is not solid or is bedrock → the level's default block.
  4. If that is stone or not solid → dirt.
  - MineColonies overrides this with the builder hut's "fill block" setting (`AbstractEntityAIStructure.getSolidSubstitution`).
- **Tags in blueprints:** `groundlevel` (`SchematicTagConstants.TAG_GROUNDLEVEL`, `BlueprintTagUtils`) marks the ground line of a blueprint; `invisible` hides the hut block.

#### Usable for CIVITAS

1. **Stage split rule for templates (civgen)**
   - **Idea:** CIVITAS already places `_s<k>` stage templates with `StructureAnimationMode.Layers`. If the civgen stage cutter does not already split by block class, cut the stages as Structurize does:
     1. solids
     2. weak/attached
     3. air-clearing
     4. decoration (torches, panes, doors, beds)
     5. entities
   - Then a half-built house never shows floating torches.
   - **Effort:** S (civgen.py). **Value:** 3.
2. **"Fill with local ground" marker for hillside houses**
   - **Idea:** a marker block in foundation templates (a `pw:` marker, or a chosen rare block) that is replaced after placement by the column's own surface/sub-surface block. Grass/dirt on a meadow, sand on a beach, snow up high.
   - Stepped San-Francisco foundations then blend into the slope instead of showing a fixed fill.
   - **How on Bedrock:** after `structureManager.place`, a runJob pass over the template's marker cells. Read the block 1 below the original terrain height from the land survey, then `setType`.
   - **Effort:** S–M. **Value:** 4.
3. **Idempotent re-lay:** skip cells that already match. CIVITAS re-lays pieces (sewer branches are "cut again").
   - A per-cell "already matches" check in script passes avoids needless `setBlock` calls, which counts against the watchdog.
   - **Effort:** S. **Value:** 2.
4. The binary blueprint format itself: no use (we use `.mcstructure`).

---

### Domum Ornamentum (Forge 1.20.1 source commit 82729d6 + curseforge jar 1.20.1-1.0.304 (not opened); licence GPL-3.0 (LICENSE); files examined: see list)

- **What it does:** "architect's cutter" blocks (timber frames, shingles, pillars, panels, doors…) whose textures are taken from OTHER blocks the player feeds in.

#### Mechanisms found

- **Components:** each block type declares N **components**, each a texture slot (`SimpleRetexturableComponent(id, validSkinsTag, defaultBlock, optional)`):
  - TimberFrameBlock: frame (tag `timber_frames_frame`, default oak planks) + center (tag `timber_frames_center`, default white terracotta).
  - ShingleBlock: roof (tag `shingles_roof`) + support (`shingles_support`, oak planks).
- **Storage:** the chosen blocks are stored per placed block in a block entity as NBT `textureData` (componentId → block id) (`MaterialTextureData`, `MateriallyTexturedBlockEntity`).
- **Allowed materials** are block TAGS. Example `timber_frames_center.json`: bricks, deepslate variants, polished blackstone, planks, cobblestone, stone, end stone, netherrack, obsidian, sandstone, dirt.
- **Cutter yield:** components × 2 items per recipe (`TimberFrameBlock`, `json.addProperty("count", COMPONENTS.size() * 2)`).
- **Variants:** 10 timber-frame patterns (`TimberFrameType`): plain, double crossed, framed, side framed, up/down gated, crossed LR/RL, horizontal plain, side framed horizontal.
- **DynamicTimberFrame** (`DynamicTimberFrameBlockEntity`):
  - It checks 14 neighbour offsets: 6 faces + 8 up/down diagonals.
  - It turns individual beam pieces on or off by which neighbours are also frames, like connected textures.

#### Usable for CIVITAS

1. **Town material palettes by district or by the ledger**
   - **Idea:** the same house template, re-skinned by what the town actually has: timber + wattle in a village, timber + brick at Town II, stone at City.
   - **How on Bedrock:** a per-block texture slot is not possible on Bedrock custom blocks (no block-entity texturing). The equivalent is a **palette swap after placement**:
     - a small table maps template "slot" blocks (e.g. stripped oak = frame, white terracotta = infill) to the district's materials;
     - a runJob pass replaces them after `structureManager.place` (or `fillBlocks` with a block filter — verify on 2.3.0).
   - The AbsolutRealism custom timber-frame blocks with a `material` state (permutations) are the RP side.
   - **Effort:** M. **Value:** 3.
2. **Connected timber frames** (neighbour-aware beams): only via custom-block permutations + a script neighbour pass.
   - **Effort:** L. **Value:** 2.

---

### MineColonies War N Taxes (Forge 1.20.1 jar WarNTaxes-5.0.9, decompiled with CFR; licence MIT (mods.toml); the manual/ copy is byte-identical (cmp); files examined: see list)

- **What it does:** adds taxes to MineColonies colonies, paid hourly into a claimable balance, with maintenance, debt and tax policies.
  - Also random colony events, war/raid/siege between player colonies, militia, vassalage, spies.

#### Mechanisms found

**1. Tax cycle** (`TaxManager.generateTaxesForAllColonies`; defaults from `TaxConfig`)
- **Cycle:** every **60 min** (TaxIntervalMinutes).
- **Per built building:**
  - raw = baseTax + upgradeTax × level;
  - generated = raw × happinessMult × max(0.3, raidPenalty × warExhaustion × policy × eventMult).
- **happinessMult** = 0.5 + (avgAdultHappiness/10) × (1.5 − 0.5): linear 0.5 → 1.5 (`TaxConfig.calculateHappinessTaxMultiplier`).
  - avgAdultHappiness includes event and policy modifiers, clamped 0–10.
- **Base taxes, examples** (base + per level):

| Building | Tax |
|---|---|
| town hall | 20 + 8 |
| blacksmith | 18 + 8 |
| hospital | 20 |
| university | 20 |
| tavern | 14 |
| library | 13 |
| cook | 12 + 5 |
| deliveryman | 12 + 5 |
| lumberjack | 11 + 5 |
| farmer | 11 + 5 |
| warehouse | 10 |
| builder | 8 + 4 |
| composter | 6 + 2 |
| **home** | 5 |

- **Maintenance per hour, military only:**
  - barracks 15 + 5/level
  - guard tower 10 + 3
  - barracks tower 14 + 6
  - archery 12 + 6
  - combat academy 14 + 6
- **Caps and debt:**
  - Stored revenue cap **10 000**: generation stops at the cap.
  - Debt limit **2000**: the balance never goes below −2000.
- **Post-steps**, in order:
  - tax-efficiency upgrade bonus (+5 % per level, a level costs 4000 from the treasury);
  - spy costs / sabotage;
  - **guard tower boost**: towers beyond the required number × % each, capped at 80 %;
  - vassal tribute;
  - treasury auto-deposit %;
  - faction pool;
  - occupation diversion;
  - then a chat report.
- **Inactivity:** a colony with no contact for N hours generates nothing.

**2. Debt consequences** (`processDebtConsequences`)
- Each cycle in debt: every citizen gets an expiring happiness modifier "wnt_debt_misery" (weight 1.5, value **0.6**, 5 days).
- After **3** consecutive debt cycles (and every 3 after): BANDIT_HARASSMENT + GUARD_DESERTION are forced.
- After N cycles at max debt the colony is abandoned (when the abandonment system is on).
- Escalating warnings: DEBT WARNING → ESCALATION → CRISIS → BANKRUPTCY IMMINENT.

**3. Tax policies** (`TaxPolicy`, `TaxConfig`)

| Policy | Revenue | Happiness |
|---|---|---|
| NORMAL | 0 | 0 |
| LOW | −25 % | +0.2 |
| HIGH | +25 % | −0.15 |
| WAR_ECONOMY | +50 % | −0.25 |

- The happiness part enters MineColonies as a static modifier "warntax", weight 2.0, factor clamp(1 + policy + events, 0.1, 2.0) (`ColonyHappinessModifierManager`).

**4. Random events** (`RandomEventType`, `RandomEventManager`, `EventTriggerSystem`)
- 16 types. Each has a tax multiplier, a happiness modifier, a duration (cycles), a base probability per cycle, a cooldown (cycles) and a condition:

| Event | Tax mult | Happiness | Duration | Prob. | Cooldown | Condition / effect |
|---|---|---|---|---|---|---|
| Merchant Caravan | 1.15 | +0.3 | 2 | 0.08 | 4 | counts restaurant/tavern |
| Bountiful Harvest | 1.2 | +0.4 | 1 | 0.06 | 5 | sets saturation 20 for all |
| Cultural Festival | 0.95 | +0.5 | 1 | 0.07 | 6 | — |
| Food Shortage | 0.85 | −0.3 | 2 | 0.06 | 4 | happiness < 5; saturation 6 |
| Disease Outbreak | 0.8 | −0.4 | 3 | 0.05 | 8 | ≥ 40 citizens & happiness < 5 & hospital < 3; 10–15 % sick |
| Bandit Harassment | 0.9 | −0.2 | 2 | 0.07 | 4 | < 3 guard towers; 2–4 bandits spawn |
| Successful Recruitment | 1.1 | +0.2 | 3 | 0.06 | 5 | happiness > 5.5 & > 15 citizens |
| Corrupt Official | 0.75 | −0.1 | 1 | 0.04 | 10 | HIGH or WAR policy |
| Wandering Trader Offer | 1.2 | +0.1 | 1 | 0.05 | 6 | — |
| Neighboring Alliance | 1.05 | +0.3 | 2 | 0.04 | 8 | — |
| War Profiteering | 1.35 | −0.5 | 3 | 0.15 | 6 | — |
| Guard Desertion | 0.8 | −0.4 | 2 | 0.08 | 8 | strongest guard leaves |
| Labor Strike | 0.7 | −0.5 | 2 | 0.12 | 6 | 30–50 % of citizens stop work |
| Plague Outbreak | 0.75 | −0.6 | 3 | 0.05 | 10 | 20–40 % sick |
| Royal Feast | 1.1 | +0.6 | 1 | 0.06 | 8 | saturation 20 |
| Crop Blight | 0.75 | −0.5 | 2 | 0.04 | 8 | saturation 3 |

- **Probability** = base × global × **size** × policy × **context**:
  - size: 0.5 below 20 citizens, 1.0 below 50, 1.2 below 100, 1.3 above;
  - context: 0 while being raided; 0.5 at war, except war profiteering at 1.0; negative events ×0.5 during post-war recovery.
- At most N simultaneous events; a **global cooldown of 2 cycles** after any event; new colonies are protected for N hours.
- The summed event happiness is clamped to ±2.

**5. War economy** (`WarExhaustionManager`)
- At war, tax ×(1 − **0.3**).
- After a war, recovery is linear back to 1.0 over **48 h**.
- Reparations ×(1 − 0.2).
- The combined war penalty is capped at 50 %, with the global floor 0.3.

**6. Raids, militia, war** (`CitizenMilitiaManager`, `TaxConfig`, `PlantTheBannerObjective`)
- **Militia:** when a raid starts, **30 %** of eligible citizens are armed with militia AI.
  - Eligible = not a guard, not a courier ("critical worker"), entity loaded.
  - The upgrade multiplier applies.
- **Tax theft:**
  - Raiders steal **10 % of the stored tax per guard/militia killed**, max **25 %**.
  - Legacy mode instead transfers 5/10/15/25 % at 60 s intervals.
- **Raid eligibility:** a colony needs ≥ 2 guards and ≥ 1 guard tower to be raidable.
- **War:**
  - 120 min long, 5 min join phase, **5 lives** per player.
  - Victory/defeat move 20 % of balances.
  - A loss can mean vassalage (tribute 15 % for N hours) or occupation (the occupier collects the taxes).
  - Experimental siege objectives: 5 explosive hits on the town hall, or holding a planted **siege banner** inside the town hall for N minutes (the defender breaks it to cancel; limited replants).

#### Usable for CIVITAS

1. **Random town-event table with conditions, cooldowns and size scaling**
   - **Idea:** CIVITAS THREADS are "live situations with a default course". Give them a WNT-style table: each row has
     - a condition on the census (mood, fed, guards, hospital, size),
     - a probability per day × size factor,
     - an effect on ledger/mood/jobs for N days,
     - a per-type cooldown + a global cooldown,
     - "no bad events during a raid".
   - Examples: Labour Strike (low mood → 30–50 % of workers idle 2 days), Bountiful Harvest, Merchant Caravan (market prices), Crop Blight, Fever (needs a physician/infirmary).
   - **How on Bedrock:** a JS table + one roll per sim-day in `pw_civ_clock`; effects reuse `pw_civ_people` mods and the ledger.
   - **Effort:** S–M. **Value:** 4.
2. **Tax policy dial + upkeep + debt unrest**
   - **Idea:** the council sets LOW/NORMAL/HIGH hearth tax. Revenue ±25 %, mood +0.2/−0.15 (on CIVITAS's 0–100 scale, about +4/−3).
   - Buildings have upkeep (watch posts, walls).
   - A treasury in debt for 3 days → unrest events (bandits, a watchman deserts); mood −.
   - Tax income scales 0.5 → 1.5 with mean mood (a happy town pays better).
   - **How on Bedrock:** ledger fields (`policy`, `debtDays`) and a scriptevent `pw:clock tax low|normal|high`.
   - **Effort:** S. **Value:** 3.
3. **Militia on alarm:** 30 % of able adults (not carters, not the market clerk) take up arms when the bell rings; the watch is the core.
   - **How on Bedrock:** switch a component group on villager_v2 (melee AI) for the raid, then switch back.
   - **Effort:** M. **Value:** 2 (only if raids come).
4. **War-weariness curve** (−30 % at war, linear recovery over 48 h): reusable for ANY shock (fire, flood, siege). The town's output recovers linearly instead of snapping back.
   - **Effort:** S. **Value:** 2.

---

### Mind Of The Colony (Forge 1.20.1 jar 20250806, decompiled with CFR; licence MIT (mods.toml); files examined: see list)

- **What it does:** every MineColonies citizen becomes an LLM chat agent.
  - Player chat within 16 blocks is queued to nearby citizens.
  - Replies are generated through a LOCAL "Player2" app API and spoken in chat.

#### Mechanisms found

- **Endpoint** (`HTTPUtils`, `Player2APIService`): `http://127.0.0.1:4315/v1/chat/completions`; `/v1/health` heartbeat every 60 s.
- **Prompt** (`CitizenAIBridge.INITIAL_PROMPT_TEMPLATE`):
  - The persona is "{name}, a {job} in the colony of {colony}, feeling {mood}".
  - Mood words from happiness: > 8 "very happy", > 6 "content", > 4 "a bit down", else "unhappy".
  - The reply must be JSON `{reason, message}`, with message < 250 characters; an empty message means stay silent.
  - "If the player asks another colonist by name, don't reply."
- **What state is fed in.** Each user turn is wrapped with fresh snapshots (`copyThenWrapLatestWithStatus`):
  - **agentStatus** (`CitizenStatus`, `MinecoloniesStatusUtils`):
    - name, id, gender, child flag, health, saturation;
    - sick + disease, status key, asleep, mourning;
    - location, bed;
    - job info;
    - **current needs** = the open requests of the work building in the ASSIGNED/REPORTED states;
    - **social status** = partner, children, siblings, parents;
    - skills;
    - happiness + **each happiness modifier** as Positive/Negative/Neutral with value and weight;
    - inventory, equipment.
  - **colonyStatus** (`ColonyStatus`): name, style pack, centre, day, under attack, population, buildings, overall happiness, owner, players, mourning info.
  - **systemMessages:** a ring buffer of the last 10 events.
- **Concurrency** (`CitizenAIManager`):
  - One global mutex: only ONE LLM request in flight across all citizens; the others wait in a FIFO speaking queue.
  - A citizen's own reply is broadcast to players within 16 blocks and added to the context of other citizens within 16 blocks (256 sq).
  - History is capped at **64** messages (the oldest after the system prompt is dropped) and saved in the citizen NBT through a mixin.

#### Usable for CIVITAS

1. **A per-villager status snapshot for the Bridge**
   - **Idea:** the AbsolutRealism Bridge (`!claude`, laptop) can answer "talk to Edda the fishwife" if the BP can export one compact JSON per person:
     - job/rank, home, mood + the reasons (the mood terms), friends/family, current errand, the town's state (day, tier, fed, under attack).
   - The happiness-modifier list with Positive/Negative labels is the key part: it gives the model the *why*.
   - **How on Bedrock:** `/scriptevent pw:clock who <name>` → `console.info(JSON)`; the bridge reads the BDS log (BDS-side only; Realms has no bridge).
   - **Effort:** S. **Value:** 3.
2. **Mood → words thresholds** (8/6/4 on a 10 scale = 80/60/40 on CIVITAS's 100): for templated greetings and the census text.
   - **Effort:** S. **Value:** 2.
3. **One-speaker-at-a-time mutex:** if any LLM voice is ever added, queue requests globally (cost and latency).
   - **Effort:** S. **Value:** 1.

---

### Talking Colonists (Forge 1.20.1 jar mc_talking-2.0.0-beta.1, decompiled with CFR; licence "All rights reserved" (mods.toml) — study only, no reuse of text or code; files examined: see list)

- **What it does:** voice conversations with MineColonies citizens through Google Gemini Live.
  - It also runs offline social systems: a **rumour mill**, colony **broadcasts**, citizens who **approach the player when they have urgent needs**, citizen–citizen chats, personality archetypes, and per-citizen memories and relationships.

#### Mechanisms found

- **Rumour mill** (`rumor/RumorMillService`, `McTalkingConfig`):
  - Runs every **600 ticks**. For each pair of citizens within **12 blocks** (both not busy), with chance **0.4**:
    - A tells B the first rumour B hasn't heard;
    - else A turns one of its own **first-hand events** (memory events not prefixed "Rumor:") into a NEW rumour (id, originator, content), removing it from A's events;
    - then the reverse direction.
  - Max **3** propagations per tick.
  - With chance 0.5, and if a player is within 12 blocks, the teller voices it ("tell them a piece of news you heard…").
  - Max **10** rumours stored per citizen, 3 put into the prompt.
- **Broadcasts** (`broadcast/BroadcastPropagationService`, `ColonyBroadcast`):
  - A player's message to the colony is stored as {id, originator, message, createdAt, senderPlayer}.
  - Every **300 ticks** a carrier shares ALL its unheard broadcasts with every citizen within **24 blocks**: 5 propagations per tick, max 20 stored, 3 in the prompt.
  - If a player is within 24 blocks the carrier "spreads the word" aloud (low-priority session).
- **Urgent contact** (`util/CitizenNeedAssessor`, `handler/UrgentContactHandler`):
  - urgency weight = sum of:
    - happiness < 3: +1.5 (< 5: +0.6)
    - sick: +0.8
    - homeless (non-guard): +0.7
    - saturation ≤ 1: +1.0 (≤ 3: +0.4)
    - health < 25 %: +1.0 (< 50 %: +0.4)
    - job STUCK: + config multiplier
  - then addon urgency modifiers.
  - Every **80 ticks**, chance = 0.5 × weight.
  - The citizen **walks to a player within 30 blocks** and speaks (player cooldown 60 s; citizen cooldown 120 s).
  - Casual greetings get weight 0.1 even for content citizens.
  - A "need signature" string (stuck, sick, starving/hungry, homeless, very_unhappy/unhappy, low/medium_health) de-duplicates repeats.
- **Citizen–citizen chats** (`handler/RandomConversationHandler`):
  - Every 400 ticks, near a player (2 × 10 blocks), each eligible citizen has a 5 % chance to start a conversation with a random eligible partner nearby.
  - Mumbling: 5 % every 200 ticks.
- **Personality** (`config/PersonalityArchetype`): 15 archetypes, each a short behaviour script:
  - optimist, grump, stoic, gossip, anxious, boastful, timid, philosophical, sarcastic, dramatic, nurturing, competitive, curious, nostalgic, superstitious.
- **Memory** (`conversations/memory/data/CitizenMemories`, `CitizenRelationshipMemory`, `api/memory/*`):
  - Facts and events (with provenance); a summarised memory (LLM compaction once > **15** entries).
  - Relationships = per-target UUID × **27 dimensions** (friendliness, trust, respect, affection, jealousy, anger, loyalty, greed, work ethic…) as a float that accumulates changes.
  - Plus broadcasts and rumours.
- **Colony events → memory** (`listener/ColonyEventSubscriber`): founded, citizen died (cause), born / hired from the tavern / resurrected, job changed (from → to), building placed / upgraded (level) / destroyed.

#### Usable for CIVITAS

1. **Petitioners (urgent contact)**
   - **Idea:** the villager with the highest need weight walks up to the player and states the need once (cooldowns).
     - "I've had no roof for six days." "The bakery's empty." "My shop has no stock."
   - This turns the census into something the player MEETS in the street.
   - **How on Bedrock:**
     - weights from CIVITAS fields (mood, home, fed, the job's blocked state, e.g. a shop counter with no stock or a site waiting for goods);
     - every N ticks pick at most one petitioner within 30 blocks of a player;
     - path the lead entity to the player (the existing walk);
     - then a chat line or an ActionForm with "I'll see to it" (opens a THREAD).
   - **Effort:** S–M. **Value:** 5.
2. **Rumours by proximity + "first-hand events become rumours"**
   - **Idea:** CIVITAS rumours already travel friend to friend. Add Talking Colonists' rule:
     - a witness's own event is converted into a rumour the first time it is told (originator kept);
     - per-person stores are capped at 10;
     - telling happens only between bodies actually near each other (12 blocks) at most every 600 ticks.
   - The square at market time becomes the rumour hub.
   - Keep the cap: the 1.3.227 save-size lesson (trust entries) applies to rumours too.
   - **Effort:** S. **Value:** 3.
3. **Notices / the town crier (broadcast)**
   - **Idea:** the player posts a notice (e.g. at the market clerk: "Builders wanted", "Feast on Sunday"). It spreads body to body within 24 blocks.
   - A carrier near the player cries it aloud.
   - Who has heard can be counted, and that can drive behaviour: more people at the square for a feast; migrants answering "builders wanted".
   - **Effort:** M. **Value:** 3.
4. **Personality archetypes for templated lines:** assign one of ~15 archetypes at birth (a 1-byte field) and pick greeting/complaint/rumour templates by archetype.
   - Cheap colour without an LLM; also usable as the persona seed for the Bridge.
   - **Effort:** S. **Value:** 3.
5. **Colony event list as the rumour source:** the event kinds above (death with cause, birth, job change with from→to, building upgraded to level N) are the exact set CIVITAS should emit as `rumour()` kinds if any are missing.
   - **Effort:** S. **Value:** 2.
6. The 27-dimension relationship model: too heavy for dynamic properties. CIVITAS's single fondness + trust is the right size.
   - **Value:** 1 (reject).

---

## Top ideas from this group (ranked)

1. **Petitioners** — the neediest villager walks up to the player and states the need (Talking Colonists urgency weights + MineColonies complaint/demand interactions) — S–M, value 5.
2. **Escalating needs + expiring event modifiers in the mood formula** (MineColonies: homeless/jobless ×0.75 after 7 days, ×0.5 after 14; a death −3 days; a repelled raid +3 days; neutral factors don't count) — S, value 4.
3. **House quality gates rank and diet** (MineColonies: skill cap (homeLevel+1)×10; diet diversity ≥ homeLevel from the last 10 foods) — gives conversions and taller rebuilds a reason in people terms — S, value 4.
4. **Visible freight: carters with the MineColonies courier score** (priority + aging − √distance; batch same-destination loads up to 1 + skill/5); a stage starts when its delivery arrives — M, value 4.
5. **Random town-event table** (WNT: condition + probability × size factor + duration + per-type and global cooldown + "none during a raid"; strike/harvest/caravan/blight/fever) driving CIVITAS THREADS — S–M, value 4.
6. **Data-driven quests/threads with dialogue** (MineColonies quest schema: triggers, a dialogue tree, a delivery objective, rewards incl. happiness for N days) via server-ui forms — M, value 4.
7. **"Fill with local ground" marker for hillside foundations** (Structurize solid-substitution rule: worldgen block → snow for powder snow → dirt fallback) — S–M, value 4.
8. **Leave-for-home timing + "home too far" (> 160 blocks) + rain idles outdoor trades + raid sends civilians indoors** (MineColonies schedule) — S, value 3.
9. **Tax policy dial, building upkeep and debt unrest; tax income × 0.5–1.5 by mean mood** (WNT) — S, value 3.
10. **Work-order queue with priority and guild-rank gating** (MineColonies WorkManager: claimed → priority → id; builder level ≥ target; 100-block reach) — S, value 3.
11. **Stage cutting by block class** (Structurize: solid → weak → clear air → decoration → entities) for the civgen stage templates — S, value 3.
12. **District material palettes** by a post-placement swap (Domum Ornamentum's idea, done the Bedrock way) — M, value 3.
13. **Rumours by proximity with first-hand events becoming rumours, capped at 10 per person** (Talking Colonists) — S, value 3.
14. **Personality archetypes (15) for templated lines and as the Bridge persona seed** — S, value 3.
15. **Raid strength from town wealth with adaptive difficulty and a mercy rule; militia 30 %** (MineColonies RaidManager + WNT) — M–L, value 3 (only if he wants raids).

## Files examined

Archives (opened):
- /home/claude/_intake/civmods/source/ldtteam__minecolonies.tar.gz (extracted only src/main/java, src/main/resources/data, src/datagen/generated/minecolonies/data, LICENSE, README; gradle.properties read from the archive)
- /home/claude/_intake/civmods/source/ldtteam__Structurize.tar.gz (src/main/java, LICENSE, README)
- /home/claude/_intake/civmods/source/ldtteam__Domum-Ornamentum.tar.gz (src/main/java, src/api MaterialTextureData, datagen tags/blocks, LICENSE, readme.md)
- /home/claude/_intake/civmods/source/LEDGER.json
- /home/claude/_intake/civmods/curseforge/structurize__structurize-1.20.1-1.0.821-snapshot.jar (listing + META-INF/mods.toml)
- /home/claude/_intake/civmods/curseforge/minecolonies-war-n-taxes__WarNTaxes-5.0.9.jar (listing, mods.toml, 91 classes decompiled)
- /home/claude/_intake/civmods/manual/WarNTaxes-5.0.9.jar (cmp only: identical to the curseforge jar)
- /home/claude/_intake/civmods/curseforge/mindofthecolony__Mind-Of-The-Colony-1.20.1.20250806.jar (listing, mods.toml, all classes decompiled)
- /home/claude/_intake/civmods/curseforge/talking-colonists-minecolonies-addon__mc_talking-2.0.0-beta.1-forge+1.20.1.jar (listing, mods.toml, selected classes decompiled)

NOT opened (the source covered everything): manual/minecolonies-1.1.1403-1.21.1.jar, modrinth/minecolonies__minecolonies-1.18.2-1.1.29-BETA.jar, curseforge/domum-ornamentum__domum_ornamentum-1.20.1-1.0.304-snapshot-universal.jar.

MineColonies (com/minecolonies/…):
- LICENSE
- gradle.properties
- core/entity/citizen/citizenhandlers/CitizenHappinessHandler.java
- api/util/constant/HappinessConstants.java
- apiimp/initializer/ModHappinessFactorTypeInitializer.java
- api/entity/citizen/happiness/TimeBasedHappinessModifier.java
- api/util/ItemStackUtils.java (grep: HADGREATFOOD modifier)
- core/quests/rewards/HappinessRewardTemplate.java (grep)
- core/entity/citizen/EntityCitizen.java (grep: DAMAGE/DEATH modifiers, saturation decrease)
- core/colony/Colony.java (getOverallHappiness)
- core/colony/CitizenData.java (initForNewCivilian, update/leisure)
- core/entity/citizen/citizenhandlers/CitizenSkillHandler.java
- core/entity/citizen/citizenhandlers/CitizenFoodHandler.java
- core/entity/citizen/citizenhandlers/CitizenSleepHandler.java
- core/entity/citizen/citizenhandlers/CitizenDiseaseHandler.java (grep: SEEK_DOCTOR_HEALTH)
- core/colony/managers/CitizenManager.java
- core/colony/managers/ReproductionManager.java
- core/colony/managers/RegisteredStructureManager.java (getHouseWithSpareBed)
- core/colony/buildings/modules/LivingBuildingModule.java
- core/colony/buildings/modules/WorkerBuildingModule.java
- core/colony/buildings/modules/BuildingModules.java (worker size limits)
- core/colony/buildings/modules/BuildingResourcesModule.java
- core/colony/buildings/modules/TavernBuildingModule.java
- core/colony/buildings/modules/settings/GuardTaskSetting.java (grep)
- core/colony/buildings/AbstractBuilding.java (createPickupRequest, requestUpgrade, requestWorkOrder, getClaimRadius, getMaxBuildingLevel)
- core/colony/buildings/AbstractBuildingStructureBuilder.java
- core/colony/buildings/AbstractBuildingGuards.java
- core/colony/buildings/workerbuildings/BuildingTownHall.java (getClaimRadius)
- api/colony/buildings/IGuardBuilding.java
- api/colony/requestsystem/request/RequestState.java
- api/util/constant/RSConstants.java
- core/colony/requestsystem/management/handlers/RequestHandler.java
- core/colony/requestsystem/resolvers/core/AbstractWarehouseRequestResolver.java
- core/colony/requestsystem/resolvers/DeliverymenRequestResolver.java
- core/colony/requestsystem/resolvers/StandardRetryingRequestResolver.java (grep)
- api/colony/requestsystem/requestable/deliveryman/AbstractDeliverymanRequestable.java
- core/colony/jobs/JobDeliveryman.java
- core/entity/ai/workers/AbstractEntityAIStructure.java
- core/entity/ai/workers/util/BuildingProgressStage.java
- core/entity/ai/workers/util/BuildingStructureHandler.java
- core/entity/ai/workers/builder/EntityAIStructureBuilder.java
- core/colony/workorders/WorkManager.java
- core/colony/workorders/WorkOrderBuilding.java
- core/colony/workorders/AbstractWorkOrder.java (grep)
- api/colony/workorders/IWorkOrder.java
- api/util/constant/BuildingConstants.java
- api/util/constant/CitizenConstants.java
- api/util/constant/SchematicTagConstants.java
- api/util/WorldUtil.java
- api/research/util/ResearchConstants.java
- core/research/GlobalResearchBranch.java
- core/colony/events/raid/RaidManager.java
- api/configuration/ServerConfiguration.java
- core/entity/ai/workers/CitizenAI.java
- core/entity/ai/minimal/EntityAIEatTask.java
- ExperienceUtils (getXPNeededForNextLevel)
- data: src/datagen/generated/minecolonies/data/minecolonies/researches/civilian.json, combat.json, technology.json, unlockable.json + all 217 research JSONs (parsed) + effects/citizencapaddition.json, happinessmultiplier.json, workingdayhaddition.json, walkingmultiplier.json
- data: src/main/resources/data/minecolonies/citizennames/english.json, colony/diseases/influenza.json, colony/quests/questschema.txt, colony/quests/general/hungrycourier.json (folder listings of quests, structures, visitors)

Structurize (com/ldtteam/structurize/…):
- LICENSE
- placement/AbstractBlueprintIterator.java
- placement/BlueprintIteratorDefault.java
- placement/BlueprintIteratorInwardCircle.java
- placement/StructureIterators.java
- placement/StructurePlacer.java
- config/ServerConfiguration.java
- blueprints/v1/BlueprintUtil.java
- blueprints/v1/BlueprintTagUtils.java (grep)
- blocks/ModBlocks.java
- placement/handlers/placement/PlacementHandlers.java (grep)
- util/BlockUtils.java
- util/TagManager.java (grep)

Domum Ornamentum (com/ldtteam/domumornamentum/…):
- LICENSE
- readme.md
- block/components/SimpleRetexturableComponent.java
- block/decorative/TimberFrameBlock.java
- block/decorative/ShingleBlock.java
- block/decorative/DynamicTimberFrameBlock.java
- block/types/TimberFrameType.java
- util/MaterialTextureDataUtil.java
- (src/api) client/model/data/MaterialTextureData.java
- entity/block/DynamicTimberFrameBlockEntity.java
- datagen tags/blocks/timber_frames_center.json (+ the tags/blocks folder listing)

War N Taxes (net/machiavelli/minecolonytax/…, CFR):
- META-INF/mods.toml
- TaxManager
- TaxConfig
- events/random/RandomEventType
- events/random/RandomEventManager
- events/random/EventTriggerSystem
- economy/WarExhaustionManager
- economy/policy/TaxPolicy
- militia/CitizenMilitiaManager
- siege/PlantTheBannerObjective
- happiness/ColonyHappinessModifierManager

Mind Of The Colony (com/goodbird/mindofthecolony/…, CFR):
- META-INF/mods.toml
- CitizenAIManager
- aibridge/CitizenAIBridge
- aibridge/ConversationHistory
- status/AgentStatus
- status/ColonyStatus
- status/CitizenStatus
- status/MinecoloniesStatusUtils
- player2/HTTPUtils
- player2/Player2APIService

Talking Colonists (me/sshcrack/mc_talking/…, CFR):
- META-INF/mods.toml
- rumor/RumorMillService
- rumor/Rumor
- broadcast/BroadcastPropagationService
- broadcast/ColonyBroadcast
- util/CitizenNeedAssessor
- handler/UrgentContactHandler
- handler/MinecraftUrgentContactAdapter
- handler/RandomConversationHandler
- config/PersonalityArchetype
- config/McTalkingConfig
- conversations/memory/data/CitizenMemories
- conversations/memory/data/CitizenRelationshipMemory
- api/memory/CitizenRelationshipDimension
- api/memory/MemoryEntryType
- listener/ColonyEventSubscriber

CIVITAS (read for comparison):
- /home/claude/_docs/research/civmods/BRIEF.md
- /home/claude/_docs/GROWTH-PROGRAM-2026-10-05.md
- /home/claude/tools/bp02_src_227/pw_civ_people.js (header, learn/trust, mood, migration, rumours)
- /home/claude/tools/bp02_src_227/pw_civ_economy.js (header, WAGE, stageBill/pay)
- /home/claude/tools/bp02_src_227/pw_civ_work.js (grep)
- /home/claude/tools/bp02_src_227/pw_civ_clock.js (lines 570–582, stage placement)
