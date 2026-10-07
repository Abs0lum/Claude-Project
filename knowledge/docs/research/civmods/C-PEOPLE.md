# C-PEOPLE — villager-life mods studied for CIVITAS (2026-10-06)

Group: C-PEOPLE. 22 items studied (MCA Reborn + 21 smaller mods), following BRIEF.md (3858 bytes).
Every number below was read from a named file (source, decompiled class, or data/lang file). Where something was
looked for and not present, it says "not found". Licences are recorded as shown in each mod's own metadata.
Personal-use law (project §9): every licence below is fine to STUDY; CIVITAS writes its own Bedrock code.

Already in CIVITAS, so not proposed again (read in `pw_civ_people.js` / `pw_civ_clock.js` 1.3.227): the census with a
lifecycle (child 10 / apprentice 20 / elder 120 / death 130 days), friends with fondness and fade, trust 0..1 that learns
(a = 1/(n+2)), rumours that pass friend to friend, threads, mood 0..100, grief, `playerFond`, migration and the
immigrant faucet, skill ranks (apprentice, journeyman at 15 days, master at 60), 20 male + 20 female names, and one
town-wide schedule by time of day (work, then the square at dusk, then home).

---

### MCA Reborn — Minecraft Comes Alive (source, GPL-3.0; files examined: see list; the Modrinth jar was not needed)
- **What it does:** it replaces vanilla villagers with people who have a gender, genes, traits, a personality, a mood, a
  "hearts" score for each player, long-term memories, a family tree, marriage and children, a dialogue tree, gifts, and
  village management (buildings found by scanning, taxes, guards, an inn, ranks for the player).
- **Mechanisms found:**
  - **Mood** (`MoodGroup.java`, `VillagerBrain.java`): one integer from -15 to +15, mapped to 7 named bands by
    `(m+15)*7/30`: depressed -15..-11, sad -10..-7, unhappy -6..-3, passive -2..2, fine 3..6, happy 7..10,
    overjoyed 11..15. A new villager starts at a random mood in that range. Each band can name a **building it is drawn
    to**: depressed and sad go to the `inn`, unhappy goes to the `music_store` (`MoodBuilder.building`).
    `EnterFavoredBuildingTask` gives +1 mood every 1200 ticks while a sad villager stays inside that building.
    Sound and particle cues: sad villagers cry every 8 ticks with splash particles every 50; depressed ones every 4 and
    20; overjoyed villagers laugh.
  - **Hearts per player** (`Memories.java`): each villager stores `{hearts, interactionFatigue, dialogueType, lastSeen(day)}`
    for each player. Every interaction adds +1 fatigue. Fatigue falls by 1 every `interactionFatigueCooldown` = 4800
    ticks. In each dialogue result, fatigue is subtracted from the success weight (`Result.getChances`, factor 1.0).
    `rewardHearts` doubles a loss for the SENSITIVE personality, and the change in hearts is also applied to mood.
    Thresholds (`Config.java`): friend 40, bouquet 10, engagement 50, marriage 100, greeting 75 (|hearts| at or above 75,
    after 1 day away; `GreetPlayerTask`), child starts at 100, pardon for a hit at 30, bounty hunters at -150.
  - **Long-term memory** (`LongTermMemory.java`): a map of string key to expiry game-tick. Dialogue can
    `remember {id, var:"player", time}`, and conditions read the remaining ticks with a divisor (for example, "asked me
    to stay recently").
  - **Personalities** (`Personality.java`): 15 of them — friendly, flirty (adults only), playful, gloomy, sensitive
    (double heart loss), greedy (finds less on chores), odd, crabby, extroverted, introverted, relaxed, anxious,
    peaceful, upbeat, plus unassigned. They are used as prefixes for dialogue keys, so each personality gets its own lines.
  - **Traits** (`Traits.java`): 21 traits, each with `chance` and `inherit` weights. Each trait's chance is
    `traitChance(0.25) / Σchance × chance`; a child inherits with probability `inherit × 0.5`. Rare examples: rainbow
    hair 0.05, sirben 0.025. Dwarfism scales height ×0.65.
  - **Dialogue engine** (`dialogues/*.json`, `Dialogues.selectAnswer`, `Result.java`, `Actions.java`,
    `GiftPredicate.java`): a question holds answers; an answer holds results; each result has `baseChance` plus a list of
    conditions, each worth `chance × test()`. The engine picks one result by weighted random over `max(0,total)`.
    Actions: `next` (go to a question; "auto" questions fire a random answer), `say`, `remember`, `positive n`,
    `negative n` (changes hearts and mood), `command`, `quit`. There are about 30 condition types, including
    hearts_min/max, `hearts {add,max,dividend}` (a scaled value), memory, mood, personality, profession, trait,
    is_married, has_home, village_has_building, rank, time_min/max, biome, emeralds and advancement.
    Example (`rumors.json`): `location` with weight 10 + 5 if hearts ≥ 20; `failed` with weight 5 + 5 if hearts ≤ -5.
  - **Gifts** (`BreedableRelationship.java`, `GiftSaturation.java`, `gifts/*.json`): the satisfaction from a data file
    (an item list plus conditions such as "profession farmer +5") falls to fail, good, better or best. **Diminishing
    returns:** the last 16 gifts are remembered, and the penalty is
    `occurrences × 0.5 × satisfaction^0.85`. Hearts change by `satisfaction × 0.33`; mood changes by
    `sat × 0.5 + 2 × sign`. The gift memory resets every 24000 ticks. When an item has no file entry, its value comes
    from its stats (food: `nutrition + saturation × 3`; sword: `dmg^1.25 × 2`).
  - **Village managers** (`Village.java` + `villageComponents/`): every 1200 ticks (offset by village id to spread the
    load) the village runs guards, inn, marriage and procreation in turn; taxes run every 168000 ticks (7 days).
    - Guards: `ceil(pop × 0.175)`, alternating guard and archer. Their gear level is 0..2 (+1 for an armory, +1 for a
      blacksmith).
    - Inn: 0.05 chance a minute; 1/10 wandering trader, 1/10 cultist, otherwise an adventurer who stays 48000 ticks.
    - Marriage: 0.05 a minute, only while more than `pop × (1 - 0.5)` are single. The suitor is the single person with
      the **lowest best-hearts score**, and the partner is the first one attracted to the suitor who is not a blood
      relative.
    - Procreation: 0.05 a minute while `pop < beds × 0.75`. A woman is chosen with probability `1/(children + 0.1)`.
      Twins 0.05 (repeatable up to 8). The baby grows in 24000 ticks.
    - Taxes: `0.5 × pop × taxRate + rand`. The reaction roll is `r = rate + (rand-0.5)·rand`: below 0.1 they pay extra
      (+pop × 0.25); below 0.3 they are happy (+5 mood); below 0.7 normal; below 0.8 sad (-5); below 0.9 angry (-10);
      otherwise a **riot** (they pay nothing). A library multiplies taxes by 1.5. Taxes need a `storage` building.
  - **Buildings by block census** (`building_types/*.json`): a building type is a set of required blocks — inn = 4 beds
    + jukebox + smoker; library = 32 bookshelves + lectern; storage = lectern + 4 chests; prison = 8 iron bars + an iron
    door + a bed; big_house = 4 beds. A village needs at least 3 buildings, and its border margin is 48 blocks.
  - **Player ranks** (`Rank.java`, `Tasks.java`, `tasks/*.json`): outlaw, peasant, merchant, noble, mayor, monarch.
    Each rank is a list of tasks: merchant = reputation 400 + big_house + storage; noble = 800 + graveyard + inn +
    infirmary; mayor = 1200 + population 20 + library + armory; monarch = 2500 + 30 + prison + blacksmith + an
    advancement. Reputation is the sum of hearts across the village.
  - **Death and grief** (`Relationship.onTragedy`, `RelationshipType`): every villager within 32 blocks loses
    `5 × proximity` mood (stranger 1, self/sibling 2, spouse/parent 3, child 4). Seeing a player commit murder costs
    -20 hearts toward that player. Family members get the GRIEVE activity at the burial site, with a grief cooldown of
    7 days.
  - **Family tree** (`FamilyTreeNode.java`): it stores father, mother, partner, children and a deceased flag.
    `isBloodRelative` tests whether the two people share an ancestor (and blocks such marriages). A family too small to
    be remembered is pruned when its members die.
  - **Regional names** (`Nationality.java`, `mca_names/<55 countries>/{male,female}.json` with weights such as Abigail
    1600, Ada 400): the world is cut into 128-block cells. A new cell takes the id of an already-seeded neighbour among
    its 8, otherwise a random id, and that region id picks the name pool. Neighbouring towns therefore share a "nation".
  - **Schedules** (`SchedulesMCA.java`): a default day (idle 10, work 2000, meet 9000, idle 11000, rest 12500), a
    night-owl day (chance 0.5 when allowed), a day guard, a night guard, and inn guests.
  - **Chat-AI prompt** (`chatAI/modules/*`): fact sentences are added module by module.
    - Personality and mood ("$villager is gloomy and sad").
    - Age and profession.
    - Relation: married/engaged/parent, and hearts as words (below -25 "hates", below 0 "dislikes", below 33 "barely
      knows", below 66 "knows well", below 100 "likes", otherwise "likes really well").
    - Village size (more than 45 huge, more than 30 large, more than 15 …).
    - Weather and night.
    - Player advancements.
- **Usable for CIVITAS:**
  - **Mood bands that pull people to a building** → add a `band(p.mood)` map in `pw_civ_people.js`. Low-mood people
    walk to the inn or square in their free time, using the existing walk graph. While there, the census step gives
    +mood (MCA: +1 per 1200 ticks, at most up to "passive"). Effort S. Value 4.
  - **Hearts with interaction fatigue and diminishing gifts** → in `playerFond`, keep a short log of the last ~16 gift
    item ids per person (dynamic property, ids only). Gift gain = `base × (1 - 0.5·k·…)`; daily reset. Talking to the
    same person again and again lowers the chance of a good result. Effort S. Value 4.
  - **Data-driven dialogue with weighted results** → a JSON table in the BP script: question → answers → results
    `{base, conds:[{type, value, w}], actions}`. Show it with `@minecraft/server-ui` ActionFormData. The conditions read
    census fields (mood band, fond, trade, has home, building present, time). Effort M. Value 5.
  - **Long-term memory keys with expiry** → `p.mem = {key: expiresDay}`, for example "asked_to_stay:player" or
    "saw_theft". It is cheap and drives repeat lines ("You asked me that already"). Effort S. Value 4.
  - **Grief by proximity amplifier** → apply `-5 × amp` mood to kin and neighbours at a death (CIVITAS sets grief only
    for spouse and kids). Add a walk to the graveyard for kin. Effort S. Value 3.
  - **Marriage pick = lowest best-fondness single, no blood relative** → CIVITAS pairs on fondness ≥ `marryFond`. Add the
    shared-ancestor test (parents are stored, so walk up 2–3 generations). Effort S. Value 3.
  - **Tax reaction roll with riot** → a council or tax event in the economy ledger: the rate the player sets → a
    happy/normal/angry/riot roll → mood for everyone. Effort S. Value 4.
  - **Player rank ladder from reputation + population + required buildings** → give the player a civic title in each
    town (merchant, noble, mayor) that unlocks palace or council actions. Effort M. Value 4.
  - **Regional name pools by 128-block cells** → a weighted name file per culture (Norse, Anglo, …). The land survey
    picks a culture per region, so neighbouring towns get related names; the weights make common names common.
    Effort S. Value 3.
  - **Prompt from fact modules** → only for the existing `!claude` bridge (laptop): a `civ facts` export per person in
    the same style. Effort S. Value 2.

### Townstead (Modrinth jar 0.7.6+1.20.1, GPL-3.0; an add-on for MCA)
- **What it does:** it gives MCA villagers needs (hunger, fatigue, thirst), real work loops (harvest, butcher,
  fisherman, cook with Farmer's Delight), editable 24-hour shift schedules with weekly plans, a calendar, emote
  "reactions", and a village **spirit** (identity) built up from its buildings.
- **Mechanisms found:**
  - **Hunger** (`hunger/HungerData`, `tick/HungerVillagerTicker`): 0..100, starting at 80, saturation 0..100 starting
    at 5. Exhaustion is added per tick of `dayTimeDelta`: movement 0.01 a block, combat or panic 0.02, chore 0.012,
    guard patrol 0.008, awake baseline 0.0003. Each 4 exhaustion removes 1 saturation, or 1 hunger once saturation is 0.
    Passive drain is 1 point per 500 ticks while not resting (400 when drowsy). Food restores
    `nutrition × 3.5` hunger and `nutrition × satMod × 3.5` saturation.
    States: well-fed ≥ 80, adequate 50–79, hungry 25–49, famished 1–24 (speed -25 %), starving 0 (no work).
    Meal thresholds: breakfast 80, lunch 70, dinner 60, emergency 25.
    Search order for food: own inventory → dropped items → containers near home → ripe crops (lang page 4).
  - **Mood drift accumulator** (same ticker): every 2400 ticks a state pressure is added to a float `moodDrift`
    (well-fed +0.15, adequate 0, hungry -0.33, famished -0.5, starving -0.75). Only whole units move MCA mood, and the
    rest is carried (clamped to ±4). Fatigue has the same pattern with its own drift.
  - **Fatigue** (`fatigue/FatigueData`): 0..20. Rate per 500 ticks: work 0.5, meet 0.25, idle 0.1, ×2 in combat.
    Recovery: bed in the person's chronotype window -1.25, bed outside it -0.6, rest without a bed -0.05, collapsed
    -0.4. States: rested < 4, alert < 8, tired ≥ 8 (-10 % speed), drowsy ≥ 12 (-20 %, ×1.25 hunger), exhausted ≥ 20
    (collapse). Once a villager collapses, it may only wake below 18.
  - **Blocked-reason enums** (HungerData): each job writes why it is idle, for example the farmer's NO_FIELD_POST /
    NO_SEEDS / NO_TOOL / NO_WATER_PLAN / UNREACHABLE / OUT_OF_SCOPE; there are similar lists for butcher and fisherman.
    The UI shows them.
  - **Shift templates and week plans** (`data/townstead/shift_templates/*.json`, `week_plans/*.json`,
    `shift/ShiftScheduleApplier`): 24 hourly slots (slot 0 = tick 0), each one of `0 idle, 1 work, 2 meet, 3 rest`.
    Templates: vanilla, standard, early_bird, night_owl, day_off. A week plan is 7 template ids, for example
    standard_week = 5 × standard + 2 × day_off, or every_other_day. The weekday comes from Townstead's calendar.
    A template can be applied to many villagers at once in a grid screen (lang "shifts.page3–5").
  - **Personality → work cadence** (`hunger/FarmerPersonalityProfile`): `(idleBackoffScale, requestIntervalScale)`
    per personality. Examples: grumpy 1.2/1.4, lazy 1.1/1.2, confident 0.9/0.75, peppy 0.85/0.85, greedy 0.85/0.95.
  - **Harvest numbers** (`HarvestWorkTask`, javap constants): anchor search radius 24 (vertical 3), cluster radius 6
    held for 200 ticks, stuck after 60 ticks and then blacklisted for 200, maximum task length 1200, rescan every 20
    ticks, stock interval 400.
  - **Cook choice** (`compat/farmersdelight/cook/RecipeScoring`):
    `score = nutrition×3.5 + saturation×7 + complexity + scarcity(8 - stock×1.5) + chain(≤4) + unlock(≤12) - stock×2.5
    (- extra above 2) + jitter(seed)×1.5`.
    Scarce goods are made first, with a small per-cook randomness.
  - **Village spirit** (`spirit/SpiritRegistry`, `VillageSpiritAggregator`, `extended_buildings/*.json`): 12 spirits —
    nautical, pastoral, martial, scholar, industrious, commercial, tourism, magical, spiritual, haunted, mining and
    natural. Each finished building adds points (bakery: pastoral 5 + commercial 2; kitchen L2: pastoral 8 +
    commercial 4). Tier thresholds are 25 / 60 / 140 / 300 / 600. A spirit dominates with a 0.4 share; two blend at
    0.25 each. Each tier has a title (lang): nautical "Dockside → Fishing Hamlet → Harbor Town → Seafaring Port →
    Thalassocracy"; commercial "Trading Post → Market Town → Mercantile Hub → Trade Republic → Emporium"; and so on.
    A message is sent when a town grows a tier.
  - **Reactions** (`townstead/reactions/wave.json`): a trigger (a player gesture within 6 blocks), a 10 s cooldown, a
    `mirror_radius 6, mirror_chance 0.25` (bystanders copy the wave), +1 heart, and choices weighted by personality
    (friendly ×2, introverted ×0.3).
  - **Disposition** (`disposition/townsfolk.json`): a schema with members, friendly and hostile groups.
- **Usable for CIVITAS:**
  - **Needs as census numbers with a carried drift** → hunger 0..100 and fatigue 0..20 per person, advanced in
    `dayStep` (no per-tick work). Meals come from the town ledger (food goods) at fixed beats; band pressure is added
    to a float drift; whole points move mood. This ties the economy to happiness without entity ticks. Effort M.
    Value 5.
  - **Blocked-reason codes per job** → each job beat writes `why` (`no_site`, `no_tool`, `no_stock`, `unreachable`, …)
    to the census. A `!civ why <name>` command and the notice board read it. It speeds up witness debugging a great
    deal. Effort S. Value 5.
  - **Shift templates + week plans** → replace the single town schedule with a 24-slot array per person (template id
    only, so it stays small), and add a day off on the town's rest day (market day). Shopkeepers get a "late" template;
    watchmen get night_owl. The walk module reads the slot by hour. Effort M. Value 5.
  - **Town spirit / identity titles from building points** → a JSON table of points per CIVITAS building family. The
    tiered title ("Harbor Town", "Market Town") appears on border stones and the notice board, and could bias which
    buildings the planner adds next. Effort S. Value 4.
  - **Scarcity-first production scoring** → counters and workshops pick today's product by
    `value + max(0, 8 - 1.5·stock) - 2.5·stock + jitter`. Effort S. Value 4.
  - **Personality scales on work cadence** → multiply idle backoff and beat intervals per personality. Effort S. Value 3.
  - **Mirror reactions** → when the player waves (crouch twice nearby, as the gesture), the person waves back
    (`playAnimation`), and others within 6 copy it with chance 0.25 by personality. Effort S. Value 3.

### Townstead Factions (Modrinth jar 0.1.2, MIT)
- **What it does:** it groups villager "species/roots" into factions, takes a census of which faction controls each MCA
  village, and runs leadership elections where villagers vote from their hearts.
- **Mechanisms found:**
  - **Rotating census** (`territory/VillageCensusTicker`): every N seconds (10 in the defaults model, 120 as a
    fallback) **one** village is processed, using a round-robin token. Faction population is weighted: villager 1,
    guard or archer 2, noble or monarch 5 (`computeVillagerWeight`). The highest count controls the village; a tie
    marks it "contested" (`VillageControlManager`). Each change writes an activity-log line (log cap 2000).
  - **Villager voting** (`voting/LeadershipManager.computeVillagerVote`): only adults vote.
    `effective = hearts(target) + 10 if same root`. A vote is YES at or above the friend threshold (40); NO below the
    dislike threshold (0); otherwise the villager ABSTAINS. A demotion is the inverse. An election passes with
    yes > no; a demotion needs ≥ 0.66. Votes last 48 h; checks run every 300 s. Maximum leaders =
    `max(1, round(participants/10))`. Monarchs are raised automatically up to 2 per faction
    (`MonarchElevationTicker`).
- **Usable for CIVITAS:**
  - **Round-robin census** → process one settlement (or one district) per beat with a token index. This matches the
    watchdog limit. Effort S. Value 4.
  - **Council or mayor elections from census fondness** → each adult votes for a candidate (or for the player) with
    fondness + 10 for the same district or kin. Abstain in the middle band; 2/3 to remove. The results feed threads and
    the palace. Effort M. Value 4.

### Liberty's Villagers (source, CC0-1.0 in fabric.mod.json; the README mentions MIT for one borrowed UI file)
- **What it does:** it tunes vanilla villager AI (search ranges, pathing, nightly behaviour) and gives each profession
  visible work behaviour at the job site.
- **Mechanisms found:**
  - **Tuned ranges** (`config/*.java`):
    - Pathing: POI search 128, pathfinding range 256, minimum POI search distance 3, walk task maximum 2400 ticks, safe
      fall 2. Villagers avoid cactus, water, rails, trapdoors, powdered snow and glass panes, and do not climb.
    - No workstation search at night; no crop trampling.
    - Golem: aggro 48, stays within 128 of the bell, spawn limit 10 per 128.
    - Farmer: crop search 10 (vertical 3), prefers to plant the same crop.
    - Feeding: animals within 20, stops at 30 animals.
    - Fisherman: finds water within 10, fishes within 5.
    - Armorer heals golems and cleric throws potions, each within 32.
  - **Weighted work-task pool** (`mixin/VillagerTaskListProviderMixin`): during WORK, one random task from
    `{primary job task: 8, wander near job site (radius 3..10): 5, go to secondary POI: 5, secondary task: 6,
    third task: 7}` runs at a time. Trade-offer holding runs for 400–1600 ticks. Profession examples: the butcher feeds
    chickens/cows/pigs/rabbits (random), the farmer composts + uses bone meal, the fisherman fishes + cooks fish, the
    armorer heals golems, the cleric throws regen potions.
  - **Secondary job sites** (`mixin/VillagerProfessionMixin`): the librarian also walks to BOOKSHELVES and the
    fisherman to WATER.
  - **Fishing** (`tasks/GoFishingTask`): scans outward up to 5 for still water with air above, never "up", not at its
    own feet. It ray-checks the bobber path at 3 edges and skips if an entity is in the way. It turns for 60 ticks
    before casting; the run lasts 800 ticks at most.
  - **Plant-same-crop** (`mixin/FarmerVillagerTaskMixin`): it replants the seed of the crop just harvested, otherwise
    copies a crop within ±4.
  - **Path fix** (`mixin/WanderAroundTaskMixin`): up to 3 fuzzy retries, then a last-ditch path; completion distance at
    least 1 for block targets, because Manhattan and straight-line distance differ.
- **Usable for CIVITAS:**
  - **Weighted work-task pool per job** → while at work, a CIVITAS worker picks a weighted beat: primary (8) /
    stand-and-look at the station (5) / walk to a secondary spot (5) / side task (6–7). This gives visible variety
    instead of standing at one block. Effort S. Value 5.
  - **Secondary spots per trade** → per building template, mark 1–3 "look-at" blocks (shelves for a scribe, water for a
    fisherman, an anvil for a smith) in the structure metadata. Effort S. Value 4.
  - **Fisherman rules** → stand on the dock edge, look at still water with air above (not under its feet), hold a rod
    item, a 60-tick turn then a "cast" animation, 40 s sessions. Effort S. Value 3.
  - **Replant the same crop / copy a neighbour within 4** → for the farmer's plots. Effort S. Value 3.
  - **Range table** → the A* and POI search caps (128/256, walk task 2400 ticks) are sane caps for CIVITAS walk timeouts.
    Effort S. Value 2.

### Villager Timetable (Modrinth jar 1.0.0, LGPL-3.0) and Villager Schedules (source, MIT)
- **What it does:** both are client HUD readouts that show what villagers are doing at this time of day.
- **Mechanisms found:**
  - `Timetable.getCurrentActivity` reads the vanilla schedule at `time % 24000` for three types: CHILD (the baby
    schedule), EMPLOYED (the default schedule), and UNEMPLOYED (default, with WORK shown as IDLE). Labels (lang): Sleep,
    Wander, Work, Socialize, Play; time shown as 12 h, 24 h or ticks; 6 HUD positions.
  - `VSHud.drawLabels` hard-codes the thresholds: employed Wander ≤ 2000, Work ≤ 9000, Gather ≤ 11000,
    Wander ≤ 12000, then Sleeping. Child: Wander ≤ 3000, Play ≤ 6000, Wander ≤ 10000, Play ≤ 12000.
- **Usable for CIVITAS:**
  - **Schedule readout** → an actionbar line when the player holds a "town ledger" item (or uses `!civ when`):
    "Market — workers at stalls until 17:00, then the square". With per-person shifts (Townstead idea), it shows the
    looked-at person's current slot. Effort S. Value 3.

### Easy Villagers (source, "All rights reserved" in src/main/resources/META-INF/neoforge.mods.toml)
- **What it does:** it lets you pick villagers up as items and place them in blocks (trader, farmer, breeder, iron
  farm, converter, incubator), where they work as a block entity without walking.
- **Mechanisms found:**
  - `VillagerTileentity`: the villager is kept as an ItemStack and turned into a cached "EasyVillagerEntity" only on
    demand. Age advances by +1 per tick inside the block.
  - `FarmerTileentity`: every 20 ticks, a 1-in-`farmSpeed` (10) chance to grow the stored crop one stage; at full
    age it harvests the drops into the inventory (only for an adult farmer).
  - `TraderTileentityBase`: restocks after a random `min + rand(max-min)` of 1200–3600 ticks, only if the villager's
    profession matches the workstation.
  - `IronFarmTileentity`: a timer with a golem spawn time (default 4800) and kill time, then rolls the golem loot table.
  - `ServerConfig`: breeding 1200 ticks, converting 6000 ticks, auto-trader cooldown 20 ticks.
- **Usable for CIVITAS:**
  - **"Person in a box" abstraction for unloaded work** → CIVITAS already counts output in the census. The idea to
    borrow: when a workshop is not ticking (far chunks), produce by a statistical roll
    (`every beat: chance 1/k → +1 good`) instead of simulating the walk. Use the same roll when loaded, so the ledger
    does not jump when the player arrives. Effort S. Value 4.
  - **Restock window with a random interval and a profession match** → counters restock at `base + rand` and only if
    the keeper's trade matches the counter. Effort S. Value 3.

### Villager Names (source, "All Rights Reserved")
- **What it does:** it gives every villager a name tag and shows "Name — Profession" on the trade screen.
- **Mechanisms found:**
  - `util/Names.getRandomName`: picks one from custom names (`config/villagernames/customnames.txt`, split on commas
    and newlines) or the default female/male lists, then capitalizes. The **default lists are not in this repository**:
    they live in the Collective library (`GlobalVariables.femaleNames/maleNames`), so the lists were not found here.
  - `events/VillagerEvent`: the profession label is parsed from the registry id (strip the namespace, cut at "-",
    otherwise title-case the id).
  - Config flags: mix custom with default, name modded villagers, show or swap or hide the profession on the trade
    screen.
- **Usable for CIVITAS:**
  - **External name file** → keep the names in a JSON in the BP (the MCA weighted format is better, see above), with
    "Name the Trade" in the nameTag (CIVITAS can set `nameTag = "Greta · Baker"`). Effort S. Value 2.

### Easy NPC (source, MIT for code; assets excluded)
- **What it does:** a full NPC builder with dialogs, buttons, conditions, action chains, objectives and factions.
- **Mechanisms found:**
  - **Dialog choice by priority** (`DialogDataSet`, `DialogPriority`): the dialog shown is the highest-priority one
    whose conditions all pass, with ties broken by label. Default priorities by label: greeting/welcome/intro = HIGH
    10; main/question/help/talk = NORMAL 5; bye/thanks/idle/random = LOW 1; other = FALLBACK 0; MANUAL_ONLY -1;
    CRITICAL 100. A dialog may hold several texts and one is picked at random
    (`DialogDataEntry`, `ThreadLocalRandom`).
  - **Conditions** (`ConditionType`): SCOREBOARD, EXECUTION_LIMIT (per minute/hour/day/week/month/lifetime), CHANCE,
    item in inventory or hand, advancement, XP level, player/NPC health, player tag, team, game mode, player idle,
    TIME_OF_DAY, WEATHER, NPC_STATE, RELATIONSHIP (owner, same/other/friendly/hostile faction), FALLBACK.
  - **Action types** (`ActionDataType`): command, close dialog, interact block, open trading, open named dialog (also
    conditional), scoreboard, NPC state, set pose, play/stop animation, message (scope NEARBY/INITIATOR/OWNER), sound,
    **WAIT**, move to, move to and wait, opacity. Action chains can pause.
  - **Event hooks** (`ActionEventType`): button click, dialog open/close, death, hurt, interaction, trade, spawn,
    time change, weather change, state change. Distance rings at touch 1.25 / very close 4 / close 8 / near 16 /
    far 32. Interval hooks at 1 / 10 / 60 / 300 / 900 seconds.
  - **Speech bubbles** (`SpeechBubbleManager`): reading time = `40 + (chars×3+1)/2` ticks, at most 360, with a 10-tick
    fade.
- **Usable for CIVITAS:**
  - **Priority + condition dialog selection with an execution limit** → the greeting a person gives is the
    highest-priority entry whose conditions pass ("thread open" CRITICAL, "first meeting" HIGH, "rumour" NORMAL, idle
    LOW), and "once per day" is an execution limit kept in the person's memory keys. Effort S. Value 5.
  - **Distance rings as triggers** → a passer-by line at 4 blocks, a shop call at 8, a watchman challenge at 16. Run
    them from the existing walk beat, not every tick. Effort S. Value 4.
  - **Speech bubble = a temporary nameTag** → set `nameTag` to the line for `40 + 1.5·chars` ticks (≤ 360), then
    restore the name. This works on PS5 with no UI. Effort S. Value 5.

### Custom NPCs (CurseForge jar 1.16.5, closed; mods.toml licence "CC BY-NC")
- **What it does:** an NPC toolkit with roles and jobs (trader, bank, transporter, follower, guard, healer, bard,
  conversation, farmer, builder, puppet, spawner), factions with player points, dialogs and quests with availability
  rules, and moving paths.
- **Mechanisms found:**
  - **Factions** (`controllers/data/Faction`): points per player per faction. Default 1000; neutral at 500, friendly
    at 1500. Below 500 the faction is aggressive. `attackFactions` lists the factions it attacks on sight.
  - **Availability** (`controllers/data/Availability`): one gate shared by dialogs and quests. Day/night (cut at tick
    12000), up to 4 dialog states (read/unread), up to 4 quest states, 2 faction stances, 2 scoreboard comparisons,
    and a minimum player level. Every check must pass.
  - **Conversation job** (`roles/JobConversation`): a scripted multi-NPC talk. Lines are `{npc name, text, delay}`,
    with a general delay of 400 ticks between runs. The named NPCs must be within 10 blocks. Mode 1 runs only when a
    player is within range 20. At the end it can start a quest for the players in range.
  - **Moving path** (`ai/EntityAIMovingPath`, `entity/data/DataAI`): a list of waypoints with a pattern — 0 loops,
    1 goes back and forth (index modulo `2n-1`). With "pause" on, a 1/40 chance per tick to start the next leg.
    Arrival at distance² < 3; 3 retries. `walkingRange` defaults to 10.
- **Usable for CIVITAS:**
  - **Overheard conversations** → a small table of 2–4-line scripts with roles (`{role:"baker", text, delay}`), cast
    from people standing together on the square at dusk. Lines go out as nameTag bubbles with delays; it runs only when
    the player is within 20. Effort S. Value 5.
  - **Patrol waypoint patterns** → watchmen use loop or ping-pong with a random pause (1/40 per tick → in CIVITAS a
    per-beat chance). Effort S. Value 3.
  - **Faction point bands** (neutral/friendly/hostile cuts) → the same three-band model for districts or guilds.
    Effort S. Value 2.

### Taterzens (manual jar 1.16.2, MIT)
- **What it does:** player-like NPCs with commands, path nodes, messages, professions as plug-ins, and presets.
- **Mechanisms found:**
  - **Path nodes** (`npc/TaterzenNPC`, `NPCData`): an ordered list of path targets. Advance when distance² < 5, wrap
    around to 0. Movement modes: NONE, FORCED_LOOK, PATH, FORCED_PATH (`DirectPathGoal` vs `LazyPathGoal`).
  - **Messages per player** (`TaterzenNPC.tick`): each player has their own cursor into the message list. When a player
    is within `speakDistance` 3 and that message's delay (default 100 ticks) has passed since the last one, the NPC
    sends `"%s -> you: %s"` and moves that player's cursor on, wrapping round (`TaterConfig.messages`).
  - **Professions as hooks** (`api/professions/TaterzenProfession`): `tick`, `tickMovement`, `interactAt`,
    `handleAttack`, `tryPickupItem`, `onPlayersNearby`, `onMovementSet`. Each returns PASS / SUCCESS to override the
    default behaviour.
- **Usable for CIVITAS:**
  - **Per-player message cursor** → a shopkeeper or clerk says lines in order to each player (stored as
    `{personId: idx}` on the player's dynamic property) when the player is within 3, at most one line per 5 s. Effort S.
    Value 4.
  - **Job behaviour as a hook table** → the CIVITAS job beat calls `JOBS[trade].beat / .onNear / .onTalk`, each able to
    return "handled". This matches the existing `WORKMOD` split. Effort S. Value 3.

### Observant Villagers (Modrinth jar 1.20.1-1.5, "All Rights Reserved")
- **What it does:** village "laws". Crimes that villagers witness cost reputation, can be repaid, raise bounties, and
  the village has a chief.
- **Mechanisms found:**
  - **Witness rule** (`ObVille.upsetNearby`): villagers (and the chief) within **16** blocks who can see the player
    (line of sight, with an extra looking-at check for the chief) and who have not just taken a bribe from that player
    each blacklist the player. A "Crime" with the law broken and the **reparation items** is recorded. The `angerOnlyIfCanSee`
    flag lets some crimes count unseen.
  - **Law table** (`Laws.java`, `config/ReputationAmountConfig`): 60+ laws with reputation hits.
    - Killing: villager -8, golem -8, guard -8, chief -10.
    - Breaking things: torch -1, crops -1, beds -1, job site -1, bell -1, waystone -3.
    - Opening containers -2.
    - Sleeping in a villager's bed -1; kicking one out of bed -1.
    - Positive: raid defence +5, bounty +5, max trade +2, building a golem +1.
    - Reputation floor -20.
  - **Reparation** (`Crime.frogive`): the repayment is a trade offer (for example 2 carrots for broken carrots, 1 iron
    for a killed guard) that hands back a "forgive" paper worth the hit.
  - **Settings** (`config/ModConfig`): recovery 12000 ticks, blacklist 24000, bribe window 400, a village needs ≥ 4
    villagers, 20 emeralds per reputation point.
  - **Bounties** (`dat/VillageData`): a "Bounty On <player>" item for each village.
- **Usable for CIVITAS:**
  - **Witnessed deeds only** → when the player breaks a block or opens a container inside a CIVITAS plot
    (`playerBreakBlock`, `playerInteractWithBlock`), census people within 16 who can see the player (check entity
    `getBlockFromViewDirection`, or a simple ray) record a memory key and lose trust/fond. The deed also becomes a
    rumour that spreads at foot speed (existing). Effort M. Value 5.
  - **Reparation as a trade** → the market clerk offers "pay N coin / return the goods" to clear a deed (a thread with a
    default course). Effort S. Value 4.
  - **Law table as data** → a JSON of `{deed: hit, reparation}` per building family (taking from a counter -2, breaking
    a station -1, harming a person -8). Effort S. Value 4.

### Reputated Villagers (Modrinth jar 1.0.0, MIT)
- **What it does:** one reputation score per player per village, with tiers that change trade prices, and decay.
- **Mechanisms found:**
  - `config/VillageRepConfig`:
    - Gains: trade +2, zombie +5, pillager +8, vindicator +10, evoker +15, ravager +20, cure +100, breed +15,
      ring the bell in a raid +10, defend a raid +50.
    - Losses: attack a villager -25, kill -100, steal from a chest -15, break a bed -30, start a raid -200, hit a
      golem -20, break a workstation -20.
    - Tiers: hero ≥ 750, friendly ≥ 400, unfriendly ≤ -400, enemy ≤ -750.
    - Event radius 64. Negative reputation recovers 1 point every 7 days.
  - Clamp -1000..1000 (`VillageReputationSavedData`).
  - **Pricing** (`event/ReputationEventHandler.applyTradePricing`, `TradePricingEventHandler`): applied when the trade
    screen opens. Hero cost ×0.5; friendly ×0.75; unfriendly ×1.5 (capped at 64); enemy ×2, and every offer after the
    first two is **blocked** by setting its cost to 64.
- **Usable for CIVITAS:**
  - **Town standing tiers → coin price factor** at the counters/market: `price × (1 - 0.25·friendly - 0.5·hero
    + 0.5·unfriendly)`, and an enemy is only sold the basics. CIVITAS prices already go through `SHOP_RATE`, so this
    adds one multiplier. Effort S. Value 5.
  - **Gain/loss table + slow negative recovery** → the starting numbers for CIVITAS's player standing (cures, defence,
    theft). Effort S. Value 4.

### Villager Reputation (manual jar 1.1 for NeoForge 26.3, "All Rights Reserved")
- **What it does:** it shows and sets the vanilla gossip reputation.
- **Mechanisms found:**
  - `ReputationTable`: vanilla gossip weights — major positive ×5, minor positive ×1, trading ×1, minor negative ×-1,
    major negative ×-5.
  - `ReputationService`: range -700..150. It writes an exact value by composing gossip counts, because amounts below 2
    cannot be stored.
  - `ReputationTicker`: every 10 ticks, the villager the player looks at (raycast 8 blocks) gets an overlay
    `value + category`: excellent ≥ 100, positive > 0, neutral 0, negative > -100, hostile.
- **Usable for CIVITAS:**
  - **Look-at standing readout** → every 10 ticks (or on a slower beat), `player.getEntitiesFromViewDirection({maxDistance:8})`
    → an actionbar line with "Greta · Baker — fond: friend". Make it optional (it costs one query per player).
    Effort S. Value 4.
  - **Five-weight deed types** → classify CIVITAS deeds as major/minor ± and trading, each with its own decay rate
    (vanilla gossip decays at different speeds per type; the decay values were not in this jar). Effort S. Value 3.

### P1nero's Dialogue Lib 2.3.0 + jellycarbonara fork (manual jars, both "All Rights Reserved"; the two fork files are
byte-identical, md5 db5365e9…)
- **What it does:** a client dialogue screen built from a tree of nodes, with a typewriter effect, for entities and
  blocks.
- **Mechanisms found:**
  - `api/component/DialogNode`: a node is `answer` (the NPC's text) + `option` (the player's button label) + child
    nodes. A leaf (`FinalNode`) returns an int `executeValue`, which the client sends back to the server as
    `finishChat(id)`. Helpers: `addChild`, `addLeaf`, and `foreachAdd` (append the same node under every option).
  - `DialogueLibConfig`: typewriter on, speed 2, interval 2; dialog width 300; HUD hidden during dialog.
  - Fork difference: a new `TextInputNode(answer, placeholder, onSubmit(String))` and a `TextInputDialogueScreen`; the
    package was renamed `com.jelly`. No other class was added.
- **Usable for CIVITAS:**
  - **Server-UI mapping** → a node tree maps 1:1 onto `@minecraft/server-ui`. Each node is an `ActionFormData`
    (body = answer, buttons = options); a leaf returns an action id; a TextInputNode becomes a `ModalFormData` text
    field (for example "name your town", "petition the council"). Effort S. Value 4.

### Speaking Villagers (CurseForge jar 0.6.1, "Speaking Villagers Mod License"; 40 MB, mostly Vosk native libraries,
which were not extracted)
- **What it does:** players talk to villagers through OpenAI or Mistral (typed or by voice through Vosk), with text to
  speech, small fetch quests, and befriending.
- **Mechanisms found:**
  - **Prompt build** (`textgeneration/TextGenerator.generateResponse`): the system prompt is built from **toggleable
    fact appenders**, each behind a config flag: villager context, style, quest, player details, gifts,
    reputation/friendship, potion effects, vehicle, sleeping, standing block, height, light level, nearby lava, trade
    offers, rare blocks, nearby entities, environment, nearby structure, difficulty. After those come the fixed rules
    (first person, no `*actions*`, at most N words and finish the sentence, language rule).
  - **Reputation words** (`appendReputationAndFriendship`): befriended → "trusted friend"; ≥ 20 "legendary saviour";
    ≥ 10 "revered hero"; ≥ 1 "welcome ally"; 0 "neutral outsider"; > -5 "unwelcome troublemaker"; > -10 "feared
    menace"; otherwise "sworn enemy".
  - **Styles** (`handlers/StyleDefinitions`, `VillagerStyleManager`): each villager gets one weighted personality from
    ~70 (Comedian 4, Optimist 5, Pessimist 5, Grumbler 3, …) and one weighted interest from ~80 (Builder 6, Animal
    Lover 6, "No Particular Interest" 7, …). The pick is saved per UUID per world.
  - **Memory** (`handlers/ConversationManager`): an append-only text file per villager with "User:/Villager:" lines,
    sent back as history.
  - Quests: a chance of `questChancePercentage` to offer "bring N of item X for reward Y"; progress counts items in the
    player's inventory.
- **Usable for CIVITAS:**
  - **Personality + interest pair as flavour** → a weighted list of ~20 temperaments × ~20 interests, kept as two
    small ints per person. Interests pick which rumours a person repeats and what they comment on (a builder talks
    about the construction site). Effort S. Value 4.
  - **Fact-appender pattern for lines** → CIVITAS lines are built from fact functions (mood band, need state, job
    blocked-reason, newest rumour, weather) that each return an optional clause; a template joins two of them. No LLM
    on PS5. For the laptop `!claude` bridge, the same facts can form a prompt. Effort S. Value 4.
  - **Fetch requests** → a shop with low stock asks the player "bring 8 wheat, 3 coin". This links to Townstead's
    scarcity score. Effort S. Value 4.

### More Villagers Re-employed (CurseForge jar 1.26.9.4 for 26.3, MIT)
- **What it does:** it adds 10 professions with their own job blocks, trades and village houses.
- **Mechanisms found** (`villagers/poi_types/*.json`, `professions/*.json`, lang):

  | Profession | Job block | Work sound |
  |---|---|---|
  | Oceanographer | oceanography_table | cartographer |
  | Forester (woodworker) | woodworking_table | leatherworker |
  | Netherologist | decayed_workbench | butcher |
  | Enderologist | purpur_altar | butcher |
  | Engineer | blueprint_table | toolsmith |
  | Florist | gardening_table | farmer |
  | Hunter | hunting_post | fletcher |
  | Miner | mining_bench | armorer |
  | Iceman | chiller | toolsmith |
  | Explorer | minecraft:decorated_pot | leatherworker |

  - Trade schema (`trades/*.json`): `levels{1..5}{trade_list_amount:2, trades:[{wants, additional_wants?, gives,
    max_uses, xp, trade_list_weight}]}`, so 2 weighted picks per level. Examples: miner 20 deepslate → 1 emerald;
    forester 6 oak saplings → 1 emerald.
  - Village houses are added to the vanilla pools with weight 10. A new badlands villager type copies the desert type.
- **Usable for CIVITAS:**
  - **Trade schema: per-level weighted pool, pick k** → CIVITAS counter stock lists per trade and rank (apprentice /
    journeyman / master unlock better goods), choosing 2 of a weighted list each restock for variety. Effort S. Value 4.
  - **Profession ideas** → forester (fits the woodcutters + coppices), miner (fits the quarrymen), hunter, florist,
    engineer. Effort S. Value 2.

### VillagersPlus (manual jar 4.0.0 for 1.21.8, CC0-1.0)
- **What it does:** 5 professions with functional workstations (alchemist table and ore grinder have their own
  screens).
- **Mechanisms found:**
  - Job sites (`acquirable_job_site.json`, lang): Alchemist → Alchemist Table; Miner → Ore Grinder; Occultist →
    Enchanted Basin; Oceanographer → Aquarium; Horticulturist → a Flower Tub in 12 wood variants.
  - Trade files `default_villager_trades/<prof>.json`: `{type: buy_item/sell_item, buy/sell, reward/priceIn,
    max_uses, villager_experience}` under novice and higher levels. Example miner: 15 coal → 1 emerald,
    20 cobblestone → 1, 1 emerald → 8 torches.
  - It also adds a mineshaft attachment and an ore-vein processor (`VanillaMineshaftAttachment`, `OreVeinProcessor`;
    names only, not decompiled).
- **Usable for CIVITAS:** **job block in variants per wood or material** → the same station family placed in the
  district's material palette (as the Flower Tub does). Effort S. Value 2.

### More Professions (manual jar 1.5.3, MIT; a datapack inside a mod jar, pack_format 61)
- **What it does:** 6 extra professions (lumberjack, miner, hunter, beekeeper, explorer, "circut_board"/redstone),
  made with no new blocks.
- **Mechanisms found:**
  - `internal/tick.mcfunction` reschedules itself every **4 ticks**. It verifies villagers that have a job site and
    wipes those with XP 0 that lost it.
  - `verify_2nd_stage.mcfunction`: the **profession is chosen by an item frame directly above the vanilla job
    site** — wooden_axe → lumberjack, wooden_pickaxe → miner, wooden_sword → hunter, honeycomb → beekeeper, compass →
    explorer, redstone_block → circuit. It applies only at XP 0, before 2 trades.
  - `jobs/lumber_jack/change_to_profession.mcfunction`: tags the villager, puts the tool on its **head slot** as a
    visible cue (drop chance 0), and replaces its trades through scoreboards.
- **Usable for CIVITAS:**
  - **"Sign of the trade" over a station** → a shop's trade is set by an item frame or hanging sign above the counter,
    so the player can re-purpose a building, and the keeper wears or holds the tool (`equippable`/`replaceitem`) as a
    visual cue. Effort S. Value 3.

### More Villager Professions: Vanilla (manual jar, MIT)
- **What it does:** 4 professions on **vanilla blocks** as job sites.
- **Mechanisms found** (`villager/ModVillagers.class`, decompiled):
  - Lumberjack → stripped spruce log; Engineer → crafter; Botanist → dried kelp block; Beekeeper → honeycomb block.
  - The POI holds 1 ticket within 1 block.
  - Trades are per level 1..5 in `villager_trade/<prof>/<level>/*.json`
    `{wants, gives, max_uses 16, xp, reputation_discount 0.05}` (for example 1 emerald → 8 oak logs).
- **Usable for CIVITAS:** **vanilla blocks as station markers** → stations in CIVITAS templates can be vanilla blocks
  that are distinctive within a plot (stripped log = woodcutter's yard, honeycomb = apiary), which keeps templates free
  of custom blocks. Effort S. Value 2.

### Better Wandering Trader (Modrinth jar 1.8.0, CC0-1.0)
- **What it does:** it replaces the wandering trader's offer tables, with an optional third tier from the config.
- **Mechanisms found:**
  - `mixin/TraderOffersMixin`: tier 1 has 46 cheap offers (1–8 emeralds, 1–64 uses); tier 2 has 17 rare offers
    (12–64 emeralds, 1–4 uses). The items are obfuscated field ids, so the names were not resolved.
  - `SellItemFactory(price, count, maxUses, xp, multiplier 0.05)`.
  - Tier 3 comes from the config `{identifier, price, count, maxUses, experience}`; `trades_to_choose` (default 1)
    are picked at random (`WanderingTraderEntityMixin.add_new_list`).
- **Usable for CIVITAS:**
  - **Visiting merchant with common, rare and special tiers** → a trader who arrives at the inn or market on market
    day (MCA's inn spawner: 1/10 trader, stays 2 days) with k common + 1 rare offers from the CIVITAS goods table.
    Effort S. Value 3.

---

## Top ideas from this group (ranked)

1. **Speech-bubble nameTags + overheard scripted conversations** (Easy NPC reading time `40+1.5·chars` ≤ 360 ticks;
   Custom NPCs conversation lines with delays, only when a player is within 20). Cheap, works on PS5, and makes the
   town feel alive. S / 5.
2. **Per-person shift templates + week plans with a day off** (Townstead: 24 slots of idle/work/meet/rest, a 7-day plan
   of template ids). Replaces the single town schedule; store only a template id per person. M / 5.
3. **Needs (hunger 0..100, fatigue 0..20) in the census with a carried mood drift** (Townstead pressures +0.15…-0.75
   every 2400 ticks; meals at 80/70/60; food comes from the ledger). Ties the economy to mood and migration. M / 5.
4. **Blocked-reason codes for every job + a `why` readout** (Townstead enums). Speeds up witness-round debugging.
   S / 5.
5. **Weighted work-task pool + secondary look-at spots per trade** (Liberty: primary 8 / near station 5 / secondary
   spot 5 / side tasks 6–7; librarian→shelves, fisher→water). Visible work instead of standing still. S / 5.
6. **Witnessed deeds → memory + rumour + trust loss, with reparation through the clerk** (Observant Villagers: only
   viewers within 16 who can see the player; a law table; repay with goods). M / 5.
7. **Standing tiers → price factor at counters** (Reputated Villagers: hero ×0.5, friendly ×0.75, unfriendly ×1.5,
   enemy ×2 and only the basics; slow recovery of negative standing). S / 5.
8. **Data-driven dialogue: priority + conditions + weighted results + memory keys with expiry** (Easy NPC priority
   selection with execution limits; MCA `baseChance + Σ cond.chance` and `remember{id,time}`; server-ui
   ActionForm/ModalForm from the Dialogue Lib node tree). M / 5.
9. **Mood bands that pull people to a building** (MCA: depressed/sad → inn, unhappy → music; +1 per 1200 ticks while
   there) + **grief by proximity amplifier** (5 × 1/2/3/4). S / 4.
10. **Town spirit titles from building points** (Townstead: 12 spirits, tiers 25/60/140/300/600, "Market Town",
    "Harbor Town"; a message when a tier is reached). S / 4.
11. **Scarcity-first production/restock scoring** (Townstead cook score: value + (8-1.5·stock) - 2.5·stock + jitter)
    + **weighted trade pools per rank, pick 2** (MoreVillagers schema). S / 4.
12. **Council/mayor votes from fondness** (Townstead Factions: yes ≥ 40, no < 0, abstain between, 2/3 to remove, same
    district +10) + **round-robin one-settlement-per-beat census** for the watchdog. M / 4.
13. **Gift memory with diminishing returns + interaction fatigue** (MCA: last 16 gifts, penalty
    `k·0.5·sat^0.85`, fatigue -1 per 4800 ticks). S / 4.
14. **Tax reaction roll with riot + player civic rank ladder** (MCA taxes every 7 days; peasant→merchant→noble→mayor
    from standing + population + required buildings). M / 4.
15. **Personality × interest flavour pair and per-personality work cadence** (Speaking Villagers weighted styles;
    Townstead farmer profile scales). S / 4.

## Notes for the caller
- Not assigned to C-PEOPLE and not opened: `manual/more-villagers-profession-behaviour.mcpack` and
  `manual/more-villagers-profession-resources.mcpack`. These are **Bedrock** packs next to "More Professions" in
  `manual/` and are likely worth a look by whichever group owns Bedrock add-ons.
- The MCA Modrinth jar (7.7.1-beta.3) was not opened; the source tarball covered every mechanism.
- Villager Names' default name lists live in the Collective library (not in the tarball), so they were not found.
- Extracts were made only under the scratchpad `study/C-PEOPLE/` and have been removed.

## Files examined
/home/claude/_docs/research/civmods/BRIEF.md
/home/claude/tools/bp02_src_227/pw_civ_people.js
/home/claude/tools/bp02_src_227/pw_civ_clock.js (lines 6755-6800 + grep)
/home/claude/tools/bp02_src_227/pw_civ_shop.js (grep)
/home/claude/tools/bp02_src_227/pw_civ_walk.js (grep)
source/Luke100000__minecraft-comes-alive.tar.gz:
  LICENSE
  common/src/main/java/net/conczin/mca/Config.java
  common/src/main/java/net/conczin/mca/CommonConfig.java (grep)
  .../entity/ai/Memories.java
  .../entity/ai/LongTermMemory.java
  .../entity/ai/Mood.java
  .../entity/ai/MoodGroup.java
  .../entity/ai/MoodBuilder.java
  .../entity/ai/Traits.java
  .../entity/ai/BreedableRelationship.java
  .../entity/ai/Pregnancy.java
  .../entity/ai/Relationship.java
  .../entity/ai/SchedulesMCA.java
  .../entity/ai/ConversationManager.java
  .../entity/ai/Residency.java (grep)
  .../entity/ai/brain/VillagerBrain.java
  .../entity/ai/brain/VillagerTasksMCA.java (grep)
  .../entity/ai/brain/tasks/EnterFavoredBuildingTask.java
  .../entity/ai/brain/tasks/GreetPlayerTask.java (grep)
  .../entity/ai/relationship/Personality.java
  .../entity/ai/relationship/AgeState.java
  .../entity/ai/relationship/RelationshipType.java
  .../entity/ai/chatAI/modules/EnvironmentModule.java
  .../entity/ai/chatAI/modules/PersonalityModule.java
  .../entity/ai/chatAI/modules/PlayerModule.java
  .../entity/ai/chatAI/modules/RelationModule.java
  .../entity/ai/chatAI/modules/TraitsModule.java
  .../entity/ai/chatAI/modules/VillageModule.java
  .../entity/interaction/InteractionPredicate.java (line count only)
  .../entity/interaction/gifts/GiftPredicate.java
  .../entity/interaction/gifts/GiftSaturation.java
  .../entity/interaction/gifts/GiftType.java (grep)
  .../resources/Dialogues.java
  .../resources/Rank.java
  .../resources/Tasks.java
  .../resources/data/dialogue/Result.java
  .../resources/data/dialogue/Actions.java
  .../server/world/data/Village.java
  .../server/world/data/FamilyTreeNode.java
  .../server/world/data/Nationality.java
  .../server/world/data/villageComponents/VillageGuardsManager.java
  .../server/world/data/villageComponents/VillageInnManager.java
  .../server/world/data/villageComponents/VillageMarriageManager.java
  .../server/world/data/villageComponents/VillageProcreationManager.java
  .../server/world/data/villageComponents/VillageTaxesManager.java
  common/src/main/resources/data/mca/tasks/mayor.json, merchant.json, monarch.json, noble.json, peasant.json
  common/src/main/resources/data/mca/building_types/inn.json, house.json, big_house.json, town_center.json, storage.json, library.json, graveyard.json, bakery.json, prison.json, blocked.json, building.json
  common/src/main/resources/data/mca/dialogues/main.json, rumors.json, chat.topic.json
  common/src/main/resources/data/mca/gifts/food.json
  common/src/main/resources/data/mca/mca_names/usa/female.json, male.json
modrinth/townstead__townstead-0.7.6+1.20.1.jar:
  META-INF/mods.toml
  com/aetherianartificer/townstead/hunger/HungerData.class
  com/aetherianartificer/townstead/hunger/VillagerConsumptionManager.class (javap)
  com/aetherianartificer/townstead/hunger/FarmerPersonalityProfile.class
  com/aetherianartificer/townstead/hunger/VillagerSearchCadence.class (javap)
  com/aetherianartificer/townstead/hunger/HarvestWorkTask.class (javap)
  com/aetherianartificer/townstead/fatigue/FatigueData.class
  com/aetherianartificer/townstead/tick/HungerVillagerTicker.class
  com/aetherianartificer/townstead/tick/FatigueVillagerTicker.class (decompiled, not used)
  com/aetherianartificer/townstead/TownsteadConfig.class (decompiled, not used)
  com/aetherianartificer/townstead/spirit/SpiritRegistry.class
  com/aetherianartificer/townstead/spirit/VillageSpiritAggregator.class
  com/aetherianartificer/townstead/shift/ShiftScheduleApplier.class
  com/aetherianartificer/townstead/shift/ShiftData.class (decompiled, not used)
  com/aetherianartificer/townstead/compat/farmersdelight/cook/*.class (javap constants)
  com/aetherianartificer/townstead/compat/farmersdelight/cook/RecipeScoring.class
  data/townstead/shift_templates/day_off.json, early_bird_default.json, night_owl_default.json, standard_default.json, vanilla.json
  data/townstead/week_plans/every_other_day.json, night_owl_week.json, standard_week.json
  data/townstead/disposition/townsfolk.json
  data/townstead/extended_buildings/bakery.json
  data/townstead/extended_buildings/compat/farmersdelight/kitchen_l2.json
  data/townstead/townstead/reactions/wave.json
  data/mca/building_types/dock_l2.json
  assets/townstead/patchouli_books/guide/en_us/entries/professions/shifts.json
  assets/townstead/lang/en_us.json
modrinth/townsteadfactions__townsteadfactions-0.1.2.jar:
  META-INF/neoforge.mods.toml
  com/drultralux/townsteadfactions/config/FactionConfigModel.class
  com/drultralux/townsteadfactions/config/CommonConfigModel.class
  com/drultralux/townsteadfactions/territory/VillageControlManager.class
  com/drultralux/townsteadfactions/territory/VillageCensusTicker.class
  com/drultralux/townsteadfactions/factions/TitleManager.class (decompiled, not used)
  com/drultralux/townsteadfactions/factions/voting/VoteManager.class
  com/drultralux/townsteadfactions/factions/voting/VoteType.class
  com/drultralux/townsteadfactions/factions/voting/LeadershipManager.class
  com/drultralux/townsteadfactions/factions/voting/MonarchElevationTicker.class
source/gitsh01__libertyvillagers.tar.gz:
  README.md
  fabric.mod.json
  src/main/java/com/gitsh01/libertyvillagers/config/VillagerPathfindingConfig.java
  src/main/java/com/gitsh01/libertyvillagers/config/VillagersProfessionConfig.java
  src/main/java/com/gitsh01/libertyvillagers/config/VillagersGeneralConfig.java
  src/main/java/com/gitsh01/libertyvillagers/config/GolemsConfig.java
  src/main/java/com/gitsh01/libertyvillagers/tasks/GoFishingTask.java
  src/main/java/com/gitsh01/libertyvillagers/tasks/FeedTargetTask.java
  src/main/java/com/gitsh01/libertyvillagers/mixin/VillagerTaskListProviderMixin.java
  src/main/java/com/gitsh01/libertyvillagers/mixin/WanderAroundTaskMixin.java
  src/main/java/com/gitsh01/libertyvillagers/mixin/FarmerVillagerTaskMixin.java
  src/main/java/com/gitsh01/libertyvillagers/mixin/VillagerProfessionMixin.java
modrinth/villagertimetable__villagertimetable-1.0.0.jar:
  fabric.mod.json
  winniethedampoeh/villagertimetable/Timetable.class
  winniethedampoeh/villagertimetable/Timetable$VillagerType.class
  winniethedampoeh/villagertimetable/gui/VillagerScheduleOverlay.class
  assets/villagertimetable/lang/en_us.json
source/LynixPlayz__villager-schedules.tar.gz:
  LICENSE
  src/main/java/me/lynix/villagerschedules/hud/VSHud.java
source/henkelmax__easy-villagers.tar.gz:
  src/main/resources/META-INF/neoforge.mods.toml (licence line)
  src/main/java/de/maxhenkel/easyvillagers/ServerConfig.java
  src/main/java/de/maxhenkel/easyvillagers/blocks/tileentity/VillagerTileentity.java
  src/main/java/de/maxhenkel/easyvillagers/blocks/tileentity/TraderTileentityBase.java
  src/main/java/de/maxhenkel/easyvillagers/blocks/tileentity/FarmerTileentity.java
  src/main/java/de/maxhenkel/easyvillagers/blocks/tileentity/IronFarmTileentity.java
source/Serilum__Villager-Names.tar.gz:
  license.md
  Common/src/main/java/com/serilum/villagernames/util/Names.java
  Common/src/main/java/com/serilum/villagernames/config/ConfigHandler.java
  Common/src/main/java/com/serilum/villagernames/events/VillagerEvent.java
source/MarkusBordihn__BOs-Easy-NPC.tar.gz:
  LICENSE.md
  core/Common/src/main/java/de/markusbordihn/easynpc/data/action/ActionDataType.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/action/ActionEventType.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/action/MessageRecipientScope.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/action/SpeechBubbleManager.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/condition/ConditionType.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/condition/DurationType.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/condition/RelationshipType.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/dialog/DialogType.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/dialog/DialogButtonType.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/dialog/DialogPriority.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/dialog/DialogDataSet.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/dialog/DialogTextData.java
  core/Common/src/main/java/de/markusbordihn/easynpc/data/dialog/DialogDataEntry.java
curseforge/custom-npcs__CustomNPCs-1.16.5.20220515.jar:
  META-INF/mods.toml
  noppes/npcs/controllers/data/Faction.class
  noppes/npcs/controllers/data/Availability.class
  noppes/npcs/controllers/data/PlayerFactionData.class (decompiled, not used)
  noppes/npcs/roles/JobConversation.class
  noppes/npcs/ai/EntityAIMovingPath.class
  noppes/npcs/entity/data/DataAI.class
manual/taterzens-1.16.2.jar:
  fabric.mod.json
  org/samo_lego/taterzens/common/npc/TaterzenNPC.class
  org/samo_lego/taterzens/common/npc/NPCData.class
  org/samo_lego/taterzens/common/storage/TaterConfig.class
  org/samo_lego/taterzens/common/api/professions/TaterzenProfession.class
  org/samo_lego/taterzens/common/npc/ai/goal/DirectPathGoal.class
  org/samo_lego/taterzens/common/npc/ai/goal/LazyPathGoal.class
modrinth/observant-villagers__Observant Villagers-1.20.1-1.5.jar:
  META-INF/mods.toml
  com/stereowalker/obville/ObVille.class
  com/stereowalker/obville/Crime.class
  com/stereowalker/obville/Law.class
  com/stereowalker/obville/Laws.class
  com/stereowalker/obville/config/ReputationAmountConfig.class
  com/stereowalker/obville/config/ModConfig.class
  com/stereowalker/obville/dat/VillageData.class
  com/stereowalker/obville/dat/Reput.class
  com/stereowalker/obville/dat/VillagerReputation.class
  com/stereowalker/obville/events/ModEvents.class
  com/stereowalker/obville/mixins/BlockMixin.class
  com/stereowalker/obville/mixins/VillagerMixin.class (decompiled, not used)
modrinth/reputated-villagers__villagereputation-1.0.0.jar:
  META-INF/mods.toml
  com/villagerep/config/VillageRepConfig.class
  com/villagerep/reputation/ReputationTier.class
  com/villagerep/event/TradePricingEventHandler.class
  com/villagerep/event/ReputationEventHandler.class
  com/villagerep/event/BellEventHandler.class (decompiled, not used)
  com/villagerep/util/VillageLocator.class (decompiled, not used)
  com/villagerep/data/VillageReputationSavedData.class
manual/villager-reputation_1.1_neoforge_26.3.jar:
  META-INF/neoforge.mods.toml
  com/hafnermichl/villagerreputation/ReputationService.class
  com/hafnermichl/villagerreputation/ReputationTable.class
  com/hafnermichl/villagerreputation/ReputationTicker.class
manual/p1neros-dialogue-lib-2.3.0-mc1.20.1-forge.jar:
  META-INF/mods.toml
  com/p1nero/dialog_lib/api/component/DialogNode.class
  com/p1nero/dialog_lib/api/component/DialogueComponentBuilder.class
  com/p1nero/dialog_lib/client/screen/DialogueScreen.class
  com/p1nero/dialog_lib/client/screen/builder/StreamDialogueScreenBuilder.class
  com/p1nero/dialog_lib/DialogueLibConfig.class
manual/p1nero-dialogue-lib-jellycarbonara-fork-2.3.0-mc1.20.1-forge.jar (and the identical "(1)" copy; md5 compared):
  META-INF/mods.toml
  com/jelly/dialog_lib/api/component/TextInputNode.class
  (full file list diffed against the original)
curseforge/speaking-villagers__SpeakingVillagers-0.6.1-Fabric-1.21.jar:
  fabric.mod.json
  speakingvillagers/sv/textgeneration/TextGenerator.class
  speakingvillagers/sv/textgeneration/RareBlockDetection.class (decompiled, not used)
  speakingvillagers/sv/textgeneration/StructureMessages.class (decompiled, not used)
  speakingvillagers/sv/handlers/StyleDefinitions.class
  speakingvillagers/sv/handlers/VillagerStyleManager.class
  speakingvillagers/sv/handlers/VillagerFriendshipManager.class
  speakingvillagers/sv/handlers/ConversationManager.class
  speakingvillagers/sv/quest/QuestManager.class (decompiled, not used)
curseforge/more-villagers-re-employed__MoreVillagers-Re-26.3-neoforge-1.26.9.4.jar:
  META-INF/neoforge.mods.toml
  assets/morevillagers/lang/en_us.json
  data/minecraft/tags/point_of_interest_type/acquirable_job_site.json
  villagers/poi_types/*.json (10)
  villagers/professions/*.json (10)
  villagers/gifts/*.json (10)
  villagers/trades/*.json (10, headers)
  villagers/structure_tags/*.json (16)
  villagers/village_structures/*/*.json (6)
  villagers/village_types/badlands/village_badlands.json
  villagers/biome_mappings/badlands.json
  villagers/types/badlands.json
manual/villagersplus-neoforge-mc1.21.8-4.0.0.jar:
  META-INF/neoforge.mods.toml
  data/minecraft/tags/point_of_interest_type/acquirable_job_site.json
  assets/villagersplus/lang/en_us.json
  data/villagersplus/default_villager_trades/miner.json
manual/more-professions-1.5.3.jar:
  fabric.mod.json
  META-INF/mods.toml
  pack.mcmeta
  data/more_professions/function/internal/tick.mcfunction
  data/more_professions/function/internal/init.mcfunction
  data/more_professions/function/verify.mcfunction
  data/more_professions/function/verify_2nd_stage.mcfunction
  data/more_professions/function/jobs/lumber_jack/change_to_profession.mcfunction
manual/more-villager-professions-vanilla.jar:
  fabric.mod.json
  data/minecraft/tags/point_of_interest_type/acquirable_job_site.json
  data/more_villager_professions_vanilla/tags/villager_trade/beekeeper/level_1.json
  data/more_villager_professions_vanilla/villager_trade/lumberjack/1/emerald_oak_logs.json
  com/junaidsultan/morevillagers/villager/ModVillagers.class
modrinth/better-wandering-trader__better-wandering-trader-1.8.0.jar:
  fabric.mod.json
  net/hyper_pigeon/better_wandering_trader/BetterWanderingTraderConfig.class
  net/hyper_pigeon/better_wandering_trader/mixin/TraderOffersMixin.class
  net/hyper_pigeon/better_wandering_trader/mixin/WanderingTraderEntityMixin.class
  net/hyper_pigeon/better_wandering_trader/mixin/BetterWanderingTraderMixin.class
