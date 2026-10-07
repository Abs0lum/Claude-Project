# CIVITAS 1.3.228 — FIT MATRIX (2026-10-06)

Every idea from the civ-mod study, tested against CIVITAS as it is in `/home/claude/tools/bp02_src_228/`.
The dropped groups (raids, militia, new violence, random town events, sickness, chance-based harm, and the four cost
patterns) are not listed again. Where a kept idea brushes against one of them, the CONFLICT line says so.

This is a planning document built from a static read of the code. It has not been verified in game. Nothing here is built.

**Sources read**

| Source | Size |
|---|---|
| BRIEF.md | 3,858 B |
| A-COLONIES.md | 57,010 B |
| B-VILLAGES.md | 56,455 B |
| C-PEOPLE.md | 65,081 B |
| D-ECONOMY-GUARDS.md | 75,015 B |
| E-BEDROCK.md | 67,203 B |
| F-TOWNS-ROADS.md | 64,014 B |

Code read:
- `pw_civ_people.js`, `pw_civ_economy.js`, `pw_civ_shop.js`, `pw_civ_work.js` and `pw_civ_watch.js`, in full.
- `pw_civ_walk.js`: send, route, beat, sweep.
- `pw_civ_clock.js`:
  - header, state and save (1–215)
  - stage placement and census (576–1130)
  - growth, economy and the plan day (1474–2085)
  - DISTRICT, kitSlot and conversions (3885–4105)
  - walls (5244–5320) and slotRelief (3798)
  - fishery and survey (795–880, 6527–6575)
  - board, trade and ladder (6386–6500)
  - schedule (6940–7296)
- The `pw_fell_rules.js` exports, `pw_civ_coin.js` / `pw_civ_keys.js` / `pw_civ_lanes.js` (indexes), the catalogue fields of `pw_civ_buildings.js` (read through node), `tools/civ_stages.py`, and the stubs in `tests/`.

Idea ids used below:

| Id | Group |
|---|---|
| BF | Build first |
| EN | Engine |
| PE | People |
| WE | Work and economy |
| GB | Growth and building |
| TR | Towns and roads |
| WP | Watch and player |

---

## 0. CIVITAS today: the facts the verdicts rest on

**Loops (engine-side cost).** CIVITAS runs **11 separate `system.runInterval` loops**:

| Loop | Every (ticks) | Where |
|---|---|---|
| save check | 20 | clock:197 |
| flush | 5 | clock:2010 |
| clock (advance) | 40 | clock:2043 |
| kitqueue | 2 | clock:2068 |
| room | 100 | clock:4859 |
| schedule starter (the pass itself is a job) | 100 | clock:7206 |
| shop | 100 | shop:71 |
| walk | 10 | walk:561 |
| watch | 10 | watch:112 |
| work | 10 | work:373 |
| keys | 40 | keys:105 |

Several of them run their own entity queries:
- **watch:** `postHolders` runs `getEntities` per settlement **every 10 ticks** (watch:78).
- **work:** the `hands` cache per settlement, every work beat (clock:6999).
- **schedule:** per settlement, every 100 ticks (clock:7222).
- **shop:** a whole-overworld keeper query every 100 ticks (shop:81).
- **walk:** orphan sweeps every 200 ticks (walk:514).

Budgets already exist inside some systems:

| Budget | Value |
|---|---|
| `SEND_BUDGET_MS` | 40 |
| `FACE_BUDGET_MS` | 40 |
| `FLUSH_MS` | 200 |
| `SLOW_MS` warning | 150 |
| route jobs | 3 × 500 expansions |

There is no common slot plan, so two heavy beats can still land in one tick.

**Engine-read hazards still in the code.** These are calls that can throw on an unloaded chunk. Each thrown engine error leaks about 650 B.
- `waterColumn` and the shore walk in `surveyFishery` (clock:807 and :838) call `getTopmostBlock` / `getBlock` raw. A fishery survey day reads up to 160 columns × 40 blocks, about 6,400 reads, inside one day tick.
- `surveyJob` (clock:6535) calls `getTopmostBlock` raw, and it reads leaves as ground.
- `hasNaturalCanopy` (fell_rules:121) and the getBlock calls in the work module (`standBeside`, `treeLogs`, `nextQuarryFace`) use try/catch instead of `isChunkLoaded`.
- `blockAt` / `topAt` / `groundAt` (clock:302–329) are the safe versions, but they are not exported to the work and watch modules.
- No `Block.below()` / `above()` / `offset()` calls remain (grep clean).

**Saved state.** One JSON (`pw:civ_clock`, chunked in 30k pieces) is written whole at most every 600 ticks (`saveNow`, clock:198).
- At save time the chronicle `st.log` is cut to 60 lines and `ledger.history` to 30.
- The 226-2 profile listed: knows 160 K, buildings 83 K, streets 30 K.
- Diagnostics are saved with the town: `st.marketGate`, `st.counters.shops`, `st.market.homes` and `st.marketTry.shoppers`, written on every market-hour pass (clock:7231, :673, :692, :7180).

**The census** (`pw_civ_people.js`).
- Person fields: `{id, name, sex, born, home, job, trade, spouse, parents, kids, friends{id:fond}, mood, alive, knows[], grief, lowDays, playerFond, trust{key:{v,n,day}}, skill{trade:days}, explore, keeper}`.
- Mood is 50 plus additive terms, smoothed 0.7/0.3.
- Leaving happens after `leaveDays` = 10 days below mood 25. This is deterministic.
- Births use the seeded `birthChance` 0.03. Marriage happens at fondness ≥ 60.
- Rumours pass friend to friend (`tellChance` 0.5, seeded) and expire after 30 days.
- Threads are open situations with a deadline and a default course.
- **Sickness (F7) is in `dayStep`:** poor sanitation raises the chance of death by up to +60 % (people:190). This is a chance-based negative effect, so it is open question Q4.

**Schedule.**
- One town-wide `SCHED` = work [1000, 11000), dusk [11000, 13000) (clock:7028).
- `goalFor` (clock:7142) works in this order:
  1. fisher → spot
  2. surveyor → stone
  3. household shopper → counter (MARKET [5000, 7000))
  4. builders and the jobless → the labour site
  5. job → station
  6. rain → home
  7. leisure
- `leisureGoal` (clock:7099) chooses home, a square-ring cell, the centre or a shop front. At dusk it adds the inn twice.
- Keepers, the clerk, the watch and the workers each have their own beats (shop / work / watch).
- At most `SENDS_PER_BEAT` = 6 walks start per settlement per pass.

**Jobs.**
- `jobPosts` (clock:882) lists builders, surveyor, sewer keeper, civic posts, healer, fisher, watch and the shops' stations.
- In `dayStep`, people take the first open vacancy. Distance plays no part.
- Quarrymen and woodcutters work real blocks (`workBeat`). Builders add work at the site, and the town crew's share is added every day, real or skipped (`advanceOnce` 1.3.226).

**Ledger** (`pw_civ_economy.js`).
- Pennies; 12 p = 1 gold coin. `BASE`, `BAND` [0.5, 3].
- Prices are set daily by `sqrt(need/stock)`.
- `PRODUCE` gives the abstract rate. `REAL` says which real production replaces it (D-C542: a real day's stone is what the hands carried).
- `EAT` = bread 1, meat 0.5 per person. **Fish is stocked but never eaten.**
- Wages are paid by `STATION_WAGE` over the shops' stations. **The watch, surveyor and sewer keeper are not on the payroll.**
- Tolls, stallage, rent, the 30-day hearth tax, imports, the mint, lean-day closures, and the invariant `money = minted + playerNet + tradeIn − sunk` with a `LEDGER DRIFT` event.

**Growth.**
- `TIER_ADDS` gives each tier's charter (fixed list), laid by `tierWorkStep` one item per beat. Unplaced items become leftovers (`planDay` / `leftoverStep`, one search phase per tick).
- Shortages charter a shop after 10 days (`CHARTER`). The ladder adds branches.
- Gates: `TIER_DAYS` + `allRoofed` + `prosperityOk` (0.8) + `moodOk` (45) + `civicWorks` + `representationOk`.
- `kitSlot` (clock:3901) orders streets by `DISTRICT` (prestige / craft / homes outward / edge last).
- `convertForBusiness` (clock:4071) runs from town II. `GREENBELT` 24.

**Templates.** Each catalogue entry is `{stem, size, datum_y, stages, lids, door, work (stations), dir, bom (per-stage materials, from the stage files), chests, art}`.
- `civ_stages.py` already cuts each building by block class:
  - s0: ground
  - s1: logs and floors
  - s2: walls, windows, **doors**, ladders
  - s3: roof
  - s4: furniture, **beds**, lights, and the station / zone / datum **markers** (`pw:marker` entities)
- Stages k > 0 are placed with `StructureAnimationMode.Layers`, lowest layer first.
- There are four skins per family (`_a.._d_r1`), chosen by seed.

**Streets.** The kit corridors are 13 wide.
- `kitPrep` (clock:2711) cuts H+1 .. max(g, H)+3 and calls `clearTreesOver` up to 30 above.
- Lanes are 7 wide. `roads7` holds the gate stubs and the daughter roads (`LAND.findRoadJob`, A* with `ROAD_SLOPE` 3).
- Wall gates are placed where a street axis meets the ring (`queueWall`, clock:5256).

**Tests** (`tests/`) are node `.mjs` files against the do-nothing engine stub (`node_modules/@minecraft/server/index.js`). Pure modules (people, economy, lanes, the shop's market table) are tested directly.

---

## 1. Rulings applied to every row

**Kept vs dropped**
- Deterministic consequences of how the town is run are kept.
- Any roll that harms the town is replaced by a threshold, or dropped.
- Positive chances (a birth) may stay seeded.

**Form**
- Every design is said in CIVITAS terms: census fields, `goalFor`/`SCHED`, the ledger goods, catalogue fields, kit streets and `roads7`.

**Engine law for every design**
- No `Block.below()` / `above()` / `offset()` / `north()`.
- Block reads go through `blockAt` / `topAt` / `groundAt`, which check `isChunkLoaded` + `isValid`. This means exporting them to the other modules.
- No call that can throw in a beat.
- A budget per system per tick: target < 50 ms.
- New per-person fields are stored only while non-zero.
- Diagnostics live in memory, not in the save.

Save estimates assume about 1,000 living people and about 400 buildings at metropolis.

---

## 2. The ideas

### BUILD FIRST

#### BF1 — One heartbeat with per-system tick slots and budgets
- **FIT:**
  - Replaces the 11 `system.runInterval` loops listed in §0.
  - Keeps every `runJob` generator as it is: schedule pass, walk graph, routes, side, bench, leg, canopy, sweep, accel.
  - Absorbs the existing per-system budgets: walk `SEND_BUDGET_MS`, work `FACE_BUDGET_MS`, clock `FLUSH_MS`, and the `prof()` wrappers with `globalThis.__civProf`.
- **CONFLICT:** none. Directly answers "dozens of separate fast loops". Leaves main.js add-on loops (Kakapo, deer, flutter) outside 228. The registry can host them later.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - New `pw_civ_beat.js` with one `system.runInterval(dispatch, 1)` and `register(name, {every, slot, budgetMs, fn, optional})`.
  - Slot plan in a 20-tick frame (slot = tick % 20):

    | Slot(s) | System | Every (ticks) | Budget (ms) |
    |---|---|---|---|
    | 0 | clock advance | 40 | 150 |
    | 2–18 even, not 10 | kitqueue | 2 | 40 |
    | 10 | **bodies cache** (one `getEntities` per settlement) | 20 | 10 |
    | 1, 11 | walk | 10 | 15 |
    | 3, 13 | work | 10 | 40 |
    | 5, 15 | watch | 10 | 15 |
    | 7 | flush / room | 10 / 100 | 40 |
    | 9 | shop | 100 | 20 |
    | 17 | keys | 40 | 5 |
    | 19 | schedule-job start | 100 | — |
    | 19 | save | 600 | — |

  - The bodies cache is shared: watch `postHolders`, work `hands`, the schedule's `vs` and the shop keeper check read it instead of querying. That is 4–6 queries per settlement per 20 ticks today, cut to 1.
  - The dispatcher times each fn. Over 2× its budget, the system skips its next turn (counted).
  - It keeps a measured MSPT (`Date.now` deltas between dispatches). When that MSPT stays above 70 ms for 20 ticks, `optional` systems (shop, room, keys) skip and kitqueue halves.
  - Every fn runs in try/catch. JS errors are cheap; engine reads stay behind `blockAt`.
  - **Hygiene** in the same build:
    - export `blockAt`/`topAt`/`groundAt` through `initWork`/`initWatch`;
    - route `waterColumn`, the shore walk, `hasNaturalCanopy` (a wrapper in clock), `standBeside` and `treeLogs` through them;
    - cap `surveyFishery` to 40 columns per call.
- **SAVE:** 0. The cache and timings stay in memory.
- **TEST:**
  - Node `test_beat.mjs`: register fakes, run 2,000 synthetic ticks, assert that no two systems marked heavy share a tick, that slot periods hold, that an over-budget fn skips once, and that an optional system is shed at simulated MSPT 80.
  - BDS gate:
    - `[CIV-BEAT]` per-system ms per 1,200 ticks;
    - worst tick < 1 s from village to M III (target ≤ 250 ms in normal play);
    - `pw:clock status` engine throws flat;
    - no Hang;
    - fishery survey no longer listed slow.
- **EFFORT:** M.
- **DEPENDS:** —

#### BF2 — Save only changed sections
- **FIT:** `saveNow` / `putText` / `getText` (clock:151–211). `kitTouch()` already bumps `st.kitVer` on street changes. `statesize` (clock:6690) already measures parts.
- **CONFLICT:** atomicity. Sections written in one tick are as atomic as today's write. Sections written across ticks could pair stale parts, so the design writes in one tick.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - Keys:
    - `pw:civ:meta` (paused, speed, simDays, lastWorld, nextId, lag, accel, tick slots, pace);
    - `pw:civ:b:<stId>` (that settlement's buildings);
    - `pw:civ:st:<stId>:core` (scalars and small fields);
    - `:streets` (streets, profile, roads7, walls, kitQueue, parked);
    - `:people` (the census);
    - `:ledger` (ledger + log);
    - `pw:civ:index` = `{v: 3, keys, gen}`.
  - On save (slot 19, every 600 ticks), all in ONE tick:
    1. Stringify each section. Skip `:streets` when `kitVer` and the `kitQueue` length are unchanged.
    2. Compare each string with its last-written copy, kept in memory.
    3. `putText` only the changed sections.
    4. Write the index last.
  - Load reads the index, else falls back to the legacy `pw:civ_clock`. The first save after a legacy load writes the sections and `dropText`s the legacy key.
  - Snapshots keep using the assembled state.
- **SAVE:** the same total. Writes fall to the changed sections; most saves touch only meta + people + ledger + core.
- **TEST:**
  - Node `test_save.mjs`:
    - `assemble(split(state))` deep-equals `state`;
    - one stage change dirties only its `b:` section;
    - a legacy JSON loads and is migrated.
  - BDS: `[CIV-SAVE] wrote k/n sections, chars`. Dynamic-property writes per minute fall from 18–23 MB (226-2) to under 2 MB. No save failure through M III. `statesize` per-key sizes.
- **EFFORT:** M.
- **DEPENDS:** BF1 (save slot), EN4.

#### BF3 — Why-idle reason codes and icons
- **FIT:** reasons already exist in pieces:
  - `b.waiting` (missing materials);
  - `st.slotWhy`;
  - the walk's `stuckBy` and BACKOFF `tries`;
  - `st.marketTry.noShop`;
  - the worker states and `skipFaces`;
  - the `pw:clock frontage` refusal census.

  There is no person-level reason and no readout.
- **CONFLICT:** none.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - A pure `whyOf(person, ctx)` in `pw_civ_people.js` returns one code from:
    - `NO_HOME`, `NO_JOB`, `SITE_WAITS:<good>`, `NO_STOCK` (counter empty);
    - `NO_FACE` (pit worked out / no tree), `UNREACHABLE` (walk backoff), `NO_ROUTE` (graph pending), `SLOTS_FULL` (lead slots);
    - `RAIN`, `OFF_SHIFT`, `ASLEEP_CHUNK`;
    - `HOME_FAR` (see PE5), `UNPAID`, `STOCK_FULL` (WE9).
  - The schedule pass keeps `whyNow: Map pid→code` in memory and a saved tally `st.why = {code: n}` (at most 16 keys).
  - **Icon:** for bodies within 24 blocks of a player, the nameTag gets a second line with a glyph (`⌂ ✗ ⚒ ⌛ ☂ …`), written only on change.
  - Command `pw:clock why [name|code]`. The probe prints the tally at every tier.
- **SAVE:** about 200 chars per town.
- **TEST:**
  - Node `test_why.mjs`: whyOf over a table of synthetic people gives the expected code. Priority order: home > food > site > route.
  - BDS: the tally appears per tier, and idle-unknown ("—") is 0 at the M III census.
  - PS5 witness: the two-line nameTag renders. If it does not, a one-line suffix is the fallback.
- **EFFORT:** S–M.
- **DEPENDS:** BF1.

#### BF4 — Needs that grow (hunger and fatigue pressure, escalating unmet needs, mood tiers set output)
- **FIT:**
  - The `dayStep` mood terms: fed ±, home ±, job ±, paid, friends, grief, council trust, sanitation.
  - `lowDays` → leave (people:304–317).
  - `outputFactor` (skill only, people:92) feeds `API.skill` → `MINE_TICKS` / `CHOP_TICKS` (work:429).
  - `ECON.dayStep` production runs have no people factor.
- **CONFLICT:**
  - A strike tier (zero output) is a hard negative. It is deterministic if it runs on a threshold for N days → **Q2**.
  - Per-person hunger 0..100 does not fit our model: food is town-wide (`fed` share), so there is no per-household larder.
- **VERDICT:** **IMPLEMENT** (deterministic; strike tier waits for Q2).
- **DESIGN:**
  - **Escalation.** Day counters `p.hd` (hungry: town fed < 0.7), `p.hl` (homeless), `p.jl` (jobless adult), stored only while > 0. The matching negative term is ×1.25 from day 7 and ×1.5 from day 14 (MineColonies' escalation, on our additive scale).
  - **Fatigue** in census terms: `p.wd` = consecutive work days. Mood −1 for each day over 6, reset by a rest day of the shift plan (BF5).
  - **Mood tier → output:**

    | Mood | Factor |
    |---|---|
    | ≥ 75 | 1.10 |
    | 50–74 | 1.00 |
    | 30–49 | 0.85 |
    | < 30 | 0.70 (0 only if Q2 = yes, after 3 days) |

  - The factor applies in two places:
    - `ECON.dayStep` gets `ctx.moodBy[shopId]` from the keeper's and workers' mean and multiplies the abstract runs;
    - `API.skill` (clock:7019) returns `outputFactor × moodFactor` for real work pace.
- **SAVE:** ≤ 4 small ints per person while non-zero, about 10–20 KB at 1,000 people. Within budget.
- **TICK:** daily census only (+ a lookup per work beat).
- **TEST:**
  - Node `test_needs.mjs`: with fed 0.5 for 14 days, mood on day 14 is lower than on day 7, which is lower than on day 1. The factor bands are exact. A rest day resets `wd`. No `Math.random`.
  - BDS: the census line "mood tiers a/b/c/d" per tier. Production falls on a starved test town and recovers when it is fed.
- **EFFORT:** S–M.
- **DEPENDS:** BF5 (rest days).

#### BF5 — Personal shift templates and ±200-tick offsets
- **FIT:** the one-town `SCHED` (clock:7028). The shop `WORK`, work `WORK` and watch `NIGHT` windows are hard-coded in three modules.
- **CONFLICT:** none. The watch's night window becomes a template instead of a constant.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `SHIFTS` table in clock: 24-letter strings per template (`W` work, `M` market/meet, `I` idle, `R` rest/home).
    - Templates: `standard`, `early` (fishers, farmers), `late` (keepers, inn), `night` (watch), `day` (sewer keeper), `child`.
    - Hour = `floor(((tod + 6000) % 24000) / 1000)`.
  - Template from the job, so nothing is stored. `p.shift` is set only by a command override.
  - **Offset** = `hash(p.id) % 401 − 200` ticks, applied to tod inside `goalFor`, so the stored value is 0.
  - **Week plan:** rest day = `(p.id + st.seed) % 7`, or the town's market day for keepers.
  - `goalFor`, the shop beat, `workBeat` and the watch call `shiftAt(person, tod, day)` (pure, in people).
  - PE5's "leave in time" rides here: the work slot ends `ceil(manhattan(home, work) × 6 / 1000)` hours early when that is ≥ 1.
- **SAVE:** 0 (hash-derived).
- **TEST:**
  - Node `test_shifts.mjs`: `shiftAt` table checks; offsets uniform in [−200, 200]; one rest day in 7; the watch works only at night; a far home ends its shift earlier.
  - BDS: the histogram of walk starts per beat at tod 11000 is spread over ≥ 4 beats (it was 1–2). Keepers stay at the station until the late shift ends.
- **EFFORT:** M.
- **DEPENDS:** BF1.

#### BF6 — Weighted choice of the next building, costs from templates, stock check
- **FIT:**
  - `tierUpBody` → `st.tierWork.items` in fixed order (clock:1595).
  - `st.leftover` with the manor ranked first (`planDay`, clock:1886).
  - `CHARTER` shortages (clock:1841).
  - Costs already come from the templates: the catalogue's `bom` per stage (from the stage files) → `ECON.stageBill` / `missing`.
- **CONFLICT:**
  - The **tier charter's lot counts are the gate law** (76 at Town III, about 380 at M III). The pick may change the **order** and fill gaps, never the counts.
  - **"Max 2 simultaneous works" is dropped.** It contradicts 1.3.226's crew-share law (every labour site worked every day), which ended the freeze.
- **VERDICT:** **IMPLEMENT** (order and choice inside the charter; max-2 dropped).
- **DESIGN:**
  - `pickNext(items, ctx)`: a pure function in a new `pw_civ_plan.js` (node-testable).
  - Weight = role weight × urgency × affordability:
    - Role weights (Millénaire's 6/4/2/1, in our terms): civic works 6 · a business that cures a shortage (`st.shortDays`) 4 · homes when `homeRoom` < 2 rooms 4 · other homes 2 · other businesses 1.
    - Affordability: `ECON.missing` of `bom` s1..s4 against stock + 5 days of production. Short → × 0.3.
  - Choice is the deterministic **max** (ties by seeded hash), not a roll.
  - One `st.pending` big project (manor, town hall) is kept until affordable; meanwhile an affordable item goes first. That is Millénaire's fallback, matching our manor rank.
  - After a failed slot search a family rests: `st.failCool[family] = day + 2` (Millénaire's 1600-tick cooldown, in village days).
  - Priority bump `pw:clock prio <family|id>` → `st.prio[]` (absorbs GB5).
- **SAVE:** `pending` + `failCool` (≤ 10 keys) + `prio`, under 300 chars.
- **TICK:** one call per plan item, inside the existing one-phase-per-tick cursor.
- **TEST:**
  - Node `test_pick.mjs`: the counts of a tier's charter are preserved; a shortage business beats a home; an unaffordable manor waits and an affordable cottage goes first; a resting family is skipped; the result is deterministic per seed.
  - BDS: lots still meet the charter at every tier through M III. Stalls with "waits for" lines drop.
- **EFFORT:** M.
- **DEPENDS:** —

#### BF7 — Beds and work places per building; take a place or move
- **FIT:**
  - `homeRoom` (clock:782): capacity = `HOUSEHOLD × DENSITY`.
  - `jobPosts` (clock:882): `def.work` stations.
  - `dayStep` §3 takes the first vacancy (people:256).
  - Arrivals take the first home with room ≥ 2. Grown children move out. Conversions re-home.
- **CONFLICT:** a strict bed count contradicts `DENSITY` (D-C535: tenements raise people per dwelling with tier). Beds become the base and `DENSITY` still multiplies.
- **VERDICT:** **MERGE** into `homeRoom` / `jobPosts` / `dayStep`.
- **DESIGN:**
  - The catalogue gains `beds` (the build tool counts bed blocks in s4; see GB7). Base = `beds || HOUSEHOLD`.
  - `dayStep` takes `homes[].x,z` and `jobs[].x,z` from the clock:
    - a jobless person takes the vacancy **nearest the home**;
    - an arrival takes the room **nearest a vacancy**;
    - **move:** an adult whose home↔work manhattan > 160 takes a room ≤ 80 from work when one is free. One move per town per day, deterministic by id.
- **SAVE:** 0 (the coordinates come in ctx).
- **TEST:**
  - Node: extend `dayStep` tests with coordinates: nearest assignment, one move per day, children never move alone.
  - BDS: mean home↔work distance per tier falls against 227. The `HOME_FAR` tally (BF3) falls.
- **EFFORT:** S–M.
- **DEPENDS:** GB7 (beds field; optional), BF3.

#### BF8 — Town notice board with real shortages, and a clerk
- **FIT:**
  - `noticeBoard` (clock:6422): a sign with the top rumour and the last log lines.
  - The market clerk and `openMarket` (shop:417).
  - Real shortages already exist: `b.waiting` (stage bills), `L.shortDays`, `L.orders`, the `short:` day events.
  - Pay goes through `COIN.issue` from the treasury, as the market does.
- **CONFLICT:** none. This is the player helping the town's real growth, never random fetch quests.
- **VERDICT:** **IMPLEMENT** (absorbs WE13).
- **DESIGN:**
  - `slipsOf(L, waiting, seed, day, roll)`: a pure function in economy.
    - 3–6 slips from real gaps: the next waiting stage bill's materials, food short of 10 days' need, a tool shortage.
    - qty = min(gap, 64). Reward = qty × `L.prices[g]` × 1.1 coins, only while the treasury covers it.
    - Easy-to-hard ladder by qty. Bountiful's worth matching keeps the reward within ±25 % of value.
  - Saved: `st.slips = {day, roll, done: [idx]}` (seed + counter, WE14).
  - The clerk's form gains "Notices". Delivering = `COIN.takeItem` → `L.stock[g] += qty` → `COIN.issue(reward)`, logged.
  - Player cap: 10 per day (memory per player per day).
  - The sign shows the top 2 slips and the rumour.
- **SAVE:** under 100 chars.
- **TICK:** computed only when the form opens and at the daily sign update.
- **TEST:**
  - Node `test_board.mjs`: slips only for real gaps; deterministic per `(seed, day, roll)`; reward ≤ treasury; the ledger invariant holds after a delivery.
  - BDS: `pw:clock board` lists slips at village II with a waiting bill. The probe delivers one: the stage starts and the coins are logged in the mint.
- **EFFORT:** M.
- **DEPENDS:** WE14, WE12.

#### BF9 — Market stalls with villager customers, drifting prices
- **FIT:** already largely there:
  - each household's **shopper** walks to a trusted counter at MARKET [5000, 7000) and takes one item from the shop chest (`buyAt`, `shopFor`, clock:690–717);
  - `stockCounters` fills chests daily;
  - prices drift daily with stock (`ECON.dayStep` §5).

  Missing: the **market clerk's stall** gets no villager customers, and there is no per-counter price.
- **CONFLICT:** TekTopia's zero-sum mark-up contradicts our stock-ratio price law. Only modifiers inside `BAND` are allowed.
- **VERDICT:** **MERGE** into `buyAt` / `shopFor` / `ECON` (absorbs WE6, WE7).
- **DESIGN:**
  - A shopper whose trusted counter was empty (`learn` outcome 0) is offered the clerk's stall next (`shopFor` options + `marketStation`). The sale comes from ledger stock into the purse → tills as a ration.
  - `counterPrice(L, g, counterId, day)` = town price × wobble × slope:
    - wobble = `1 + 0.10 × (2·hash(day, counterId, g) − 1)`, seeded and unsaved (WE7);
    - slope = 1.15 at chest stock ≤ 2, falling linearly to 1.0 at ≥ 16 (Lightman's DemandPricing on the chest).
  - The shop window and the market quote use `counterPrice` and stay inside `BAND`.
  - Sales feed `L.sold[g]` (one counter per good). The daily demand term adds `0.5 × sold[g]` to the need in the §5 price law (WE6, deterministic).
- **SAVE:** 13 numbers.
- **TICK:** none new (in the existing schedule pass).
- **TEST:**
  - Node: `counterPrice` stays within the band, is deterministic per day, and the slope is monotonic. The `sold` term raises the price of a good that sells out.
  - BDS: `st.market.buys` at the stall > 0 by village III; `empty` falls.
- **EFFORT:** S–M.
- **DEPENDS:** —

#### BF10 — Real-tree-only felling and site claims
- **FIT:**
  - `nextTree` (work:280) accepts **any** `TREE_LOG` 1–2 above ground.
  - The clock's `fellTree` → `treeCells` (clock:5664) checks for a pw root template, but a **rootless** tree has no natural-canopy test and no placed-log ledger test.
  - `pw_fell_rules.js` already has `touchesPlacedLog` (R4) and `hasNaturalCanopy` (R5).
  - The work map has no claims: two hands of one yard can take the same tree or face.
- **CONFLICT:** today's code contradicts his BIGCANOPY rule ("player-placed logs must never trigger"). This fixes it.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `treeOk(dim, base)` in clock, exported through `initWork`:
    - `treeCells` logs;
    - R4 `!touchesPlacedLog`;
    - R5 = root present OR `hasNaturalCanopy(logs, 3)`, rewritten to read through `blockAt`;
    - at most 64 logs.
  - Verdict cache in memory: `Map("x,y,z" → {ok, until: +6000})`.
  - `nextTree` skips `!ok`. `clearForest` (skipped days) uses the same predicate.
  - **Claims:** `claims: Map("x,z" → {vid, until})` in the work module. Taken in `nextTree` / `nextQuarryFace`, released on fell, dig, off-duty or a missing body. Expiry 1200 ticks.
- **SAVE:** 0.
- **TICK:** inside `FACE_BUDGET_MS` (the canopy test is ≤ about 27 reads per log, and it is cached).
- **TEST:**
  - Node `test_fell.mjs`, with a fake dim (block map) injected through the exported predicate: a player log cabin is refused; a log with only persistent leaves is refused; a natural tree is accepted; a rooted template tree is accepted. Two workers never get the same claim.
  - BDS: a scripted log cabin inside a yard's radius stands after 5 days, with a `refused` counter. Felled > 0 continues.
- **EFFORT:** S.
- **DEPENDS:** BF1 hygiene (`blockAt` export).

#### BF11 — Petitioners
- **FIT:**
  - Bodies, `WALK.send`, `openTalk` (shop:168) and `PEOPLE.openThread`.
  - Need data: BF3/BF4 counters, `b.waiting`, `L.arrears`, an empty counter.
- **CONFLICT:** Talking Colonists picks by chance (`0.5 × weight`). Ours picks the deterministic **max**.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `urgencyOf(p, ctx)` (pure): homeless days ×3 + hungry days ×2 + jobless days + the site waiting on that person's trade + unpaid ×2. The threshold is 6.
  - Heartbeat slot 9, every 200 ticks: for each player inside a town (`inInfluence`), take the **max-urgency body within 30 blocks** whose cooldown `p.pet` (a day number, saved while set) has passed. Per-player cooldown 2,400 ticks (memory).
  - The petitioner walks to the player (≤ 3 blocks), stands and faces the player, and shows the line (BF12 bubble + chat).
  - The talk form gains "I'll see to it" → `openThread(kind: "petition", deadline + 5 days, default course "nothing was done")`.
  - Rumour on close.
- **SAVE:** one int per person who has petitioned.
- **TICK:** ≤ 1 `getPlayers` per 200 ticks plus a scan of cached bodies.
- **TEST:**
  - Node `test_petition.mjs`: max pick, threshold, cooldown, no randomness.
  - BDS: a starved test town with the probe standing on the square gets `petitions` > 0 and a thread opened. A fed town gets 0.
- **EFFORT:** M.
- **DEPENDS:** BF3, BF4, BF12, PE11.

#### BF12 — Speech lines and overheard two-villager talk
- **FIT:**
  - Today's lines: `openTalk` (stage, trade, mood word, greeting tier, rumour), `greeting`, `board`.
  - `nameTrades` (clock:6442) rewrites nameTags daily.
- **CONFLICT:** none. The nameTag restore must win over `nameTrades`.
- **VERDICT:** **IMPLEMENT** (absorbs PE9).
- **DESIGN:**
  - New `pw_civ_talk.js`, mostly pure:
    - `LINES`: a data table keyed by situation — mood band, why code, rumour kind, price moved, building finished, rain.
    - Templates are filled from census and ledger fact functions (the fact-appender pattern).
  - **Bubble:** `v.nameTag = line` for `min(360, 40 + 1.5·chars)` ticks, then restore. Memory map `vid → {until, name}`, restored in the walk slot.
  - **Overheard:**
    - When: at dusk, every 400 ticks, a player within 16 blocks, on the square or a centre.
    - Who: two cached bodies ≤ 5 apart, chosen as the most-fond friend pair (deterministic).
    - What: a 2–4-line script (`{who: 0|1, text, delay}`) chosen by situation.
    - Cooldown: per pair 18,000 ticks (memory).
  - Nothing is saved.
- **SAVE:** 0.
- **TICK:** ≤ 2 nameTag writes per 20 ticks per town.
- **TEST:**
  - Node `test_talk.mjs`: template fill, duration formula, deterministic pair pick, cooldown.
  - BDS: bubbles shown > 0 at dusk with the probe present; after 400 ticks every nameTag is the name again.
  - PS5 witness: readability.
- **EFFORT:** M.
- **DEPENDS:** BF1, PE8.

### ENGINE

#### EN1 — Script API 2.10 features (TextPrimitive / PrimitiveShapes, TickingAreaManager, LocatorBar waypoints, container events, item pickup)
- **FIT:**
  - `ensureTicking` uses `runCommand("tickingarea add …")` (clock:3475). A command that fails throws, which is the leak path. `TickingAreaManager` (stable from 2.6.0, per SLABFORGE-v2 research) answers with a promise.
  - Speech bubbles (BF12) could become text primitives.
  - LocatorBar (2.9.0, per E-BEDROCK) could mark towns and the guide's goal (WP12).
  - Container events could reconcile store chests with the ledger (WE2/EN5).
- **CONFLICT:** the manifest targets `@minecraft/server` 2.3.0, and PS5 must run the newer version. Exact 2.10 class names are not verified here: the bp02 typings are stubs.
- **VERDICT:** **IMPLEMENT, engine-gated (last batch)**, after Q10 (upgrade) and a PS5 version read.
- **DESIGN:** a thin `pw_civ_engine.js` capability layer that feature-detects each API (`typeof world.tickingAreaManager`). The old path stays as the fallback. Order: TickingAreaManager → LocatorBar → text primitives → container/pickup events.
- **SAVE:** 0.
- **TEST:** BDS probe on the upgraded manifest: each feature's detect line plus one use. The 2.3.0 fallback still passes the 227 gate. PS5 witness.
- **EFFORT:** M after the upgrade.
- **DEPENDS:** Q10, BF1.

#### EN2 — Structure integrity + seed for weathered variants
- **FIT:**
  - `placeStage` places `pw:stages/<stem>_s<k>` with rotation and Layers (clock:599).
  - Closed shops get cobwebs (`applyShopMark`).
  - Conversions demolish homes (`clearLot`).
- **CONFLICT:** aging lived-in houses in a thriving town is an aesthetic call → **Q9**. `integrity` / `integritySeed` are believed to be in 2.3.0's `StructurePlaceOptions`; verify on BDS.
- **VERDICT:** **IMPLEMENT** (scope per Q9; absorbs GB11).
- **DESIGN:**
  - The build tool emits `<stem>_w` weathered overlays: moss for cobble, cracked for stone brick, cobweb, broken pane. Only blocks that differ; everything else structure void.
  - Placed after s4 with `{integrity: 0.25–0.6 by age band, integritySeed: String(b.id)}`. Deterministic per building.
  - When: a building closed ≥ 20 days, or a building older than N days (Q9). One placement per building per age band (`b.wx` = band, saved).
- **SAVE:** one int per weathered building.
- **TEST:** BDS: place the same overlay twice with the same seed → an identical block census (`block_census` on the box). A different seed differs. Witness the look.
- **EFFORT:** S–M (with the build tool).
- **DEPENDS:** Q9.

#### EN3 — placeJigsaw
- **FIT:** none. Our planner places by frontage, district and slot law (`kitSlot`, lanes, benches).
- **CONFLICT:** needs 2.5.0+. It imports the jigsaw architecture, which runs against "their code fits our model". Villages Plus itself shows that streets follow terrain and houses stay rigid, which our kit already does.
- **VERDICT:** **DROP.**

#### EN4 — `getDynamicPropertyTotalByteCount` warning
- **FIT:** `statesize` (clock:6690) and `state.bytes` (clock:208).
- **CONFLICT:** none. The method is believed to be on `World` in stable 2.x; verify.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - After each save write: `n = world.getDynamicPropertyTotalByteCount()` in try (outside any beat loop).
  - Keep `s.dpBytes`. Warn at +25 % per tier, or above the configured ceiling (default 4 MB).
  - Print it in `status` and `statesize`. The probe logs it at every tier.
- **SAVE:** one number.
- **TEST:** BDS: the number is printed per tier and grows sub-linearly with lots after BF2.
- **EFFORT:** S.
- **DEPENDS:** BF2.

#### EN5 — Native hauling `minecraft:behavior.transport_items`
- **FIT:** none today. Our civs run with vanilla AI stripped (`pw:civ_on`) and move only by the lead.
- **CONFLICT:**
  - **The ledger is the truth.** Items moved natively between chests never reach `L.stock` unless container events (EN1) reconcile them.
  - Component groups on `villager_v2` interact with `pw:civ_on`.
- **VERDICT:** **MERGE** into EN1's gate, as a BDS test only (no ship).
- **DESIGN:** a probe-only entity group `pw:porter_test` (copper chest → chest, search [32, 8]). Measure items moved per minute and MSPT. Decide after EN1.
- **TEST:** BDS only.
- **EFFORT:** S (test).
- **DEPENDS:** EN1.

### PEOPLE

#### PE1 — Varied work beats
- **FIT:**
  - Keepers stand at `b.station` under slowness 255 (shop:137).
  - The clerk does the same.
  - Builders stand at the site door.
  - The catalogue already lists `chests` (secondary spots) and `door`.
- **CONFLICT:** none.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `beatOf(pid, tick)` (pure): a weighted deterministic pick over `floor(tick / 600)`:

    | Beat | Weight |
    |---|---|
    | station | 8 |
    | look-at a chest / secondary mark | 5 |
    | door step | 5 |
    | counter side | 6 |

  - The shop beat walks the keeper ≤ 4 blocks to the beat's spot and faces it (`setRotation`). Builders at a site alternate between its door and a corner of its box.
- **SAVE:** 0.
- **TICK:** inside the shop beat, ≤ 2 sends per beat (SEND budget).
- **TEST:** Node: weights over 10,000 draws. BDS: a keeper's distance from the station varies 0–4 over a work day; the shop beat stays < 20 ms.
- **EFFORT:** S.
- **DEPENDS:** GB7 (marks; chests already work).

#### PE2 — Inn visits for sadness
- **FIT:** `leisureGoal` already adds the inn twice at dusk (clock:7108). Mood is in the census.
- **CONFLICT:** none.
- **VERDICT:** **MERGE** into `leisureGoal` + `dayStep` (absorbs WP6's tavern half).
- **DESIGN:**
  - A body with mood < 40 picks the inn first at dusk and in idle hours.
  - `dayStep` gives +3 (capped at 55) to people of mood < 40 when an inn exists and has room. Capacity = 3 × inns × stations; the lowest moods first, deterministic.
- **SAVE:** 0.
- **TEST:** Node: mood recovery with and without an inn. BDS: inn arrivals at dusk are counted.
- **EFFORT:** S.
- **DEPENDS:** —

#### PE3 — Grief by closeness
- **FIT:** the `dayStep` death branch sets `grief = 20` for spouse and kids (people:195).
- **CONFLICT:** none (deterministic).
- **VERDICT:** **MERGE** into `dayStep`.
- **DESIGN:**

  | Mourner | Grief |
  |---|---|
  | spouse, children | 20 |
  | parents | 15 |
  | siblings | 10 |
  | friends with fondness ≥ 70 | 8 |
  | friends with fondness ≥ 40 | 4 |

  The existing −1 per day decay stays.
- **SAVE:** the existing field.
- **TEST:** Node: a death applies the table exactly.
- **EFFORT:** S.
- **DEPENDS:** —

#### PE4 — House level gates diet and skill (absorbs PE7, the skill curve)
- **FIT:**
  - `rankOf` / `outputFactor` (people:90–92) count days in a trade.
  - `EAT` is bread and meat only.
  - Conversions and taller rebuilds (GROWTH-PROGRAM §5) have no payoff in people's terms.
- **CONFLICT:** adding fish to the diet changes `prosperity` (a gate). It is added as **variety only**, not as need.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `HOME_LEVEL` by kind in clock:

    | Kind | Level |
    |---|---|
    | cottage_s, cottage_m | 1 |
    | cottage_l, inn rooms | 2 |
    | townhouse, rooms over the shop (a keeper) | 3 |
    | manor | 4 |
    | palace | 5 |

  - Passed to `dayStep` as `homes[].lvl`.
  - **Skill gate:** journeyman needs lvl ≥ 1, master needs lvl ≥ 2. The days still count while gated.
  - **Curve (PE7):** `outputFactor = 1 + 0.5 × (1 − e^(−days/60))`. Concave: early gains, slow mastery. The daily cap of 1 is kept (one day = one point).
  - **Diet:** diversity = the number of food goods with stock > 1 day of need, among bread, meat, fish and grain.
    - Mood +4 when diversity ≥ 1 + ⌈lvl/2⌉.
    - Mood −4 when it is below that and lvl ≥ 3.
    - Deterministic, town-level (no per-household larder).
- **SAVE:** 0.
- **TEST:** Node: gate holds; curve values at 15/60/120 days; the diet term by level and stock.
- **EFFORT:** S–M.
- **DEPENDS:** BF7 (homes context).

#### PE5 — Leave work in time, home-distance complaint, rain idles outdoor trades
- **FIT:**
  - The fixed `SCHED` end.
  - Rain → home in `goalFor` (clock:7195). But builders (site branch) and quarry/lumber workers (`workBeat`, no weather check) keep working in rain.
  - Fishers fish in rain by design (1.3.225).
- **CONFLICT:** rain lowering real-day output is a weather-driven negative → **Q5**.
- **VERDICT:** **MERGE**: leave-in-time into BF5; the complaint into BF3 (`HOME_FAR`) + BF11 + BF7 (move); rain per Q5 into `goalFor` + `workBeat`.
- **DESIGN:**
  - Rain (if Q5 = stop): `ctx.wet` gates the site branch and `workBeat`'s duty. Outdoor real production that day falls to what was carried.
  - Rain (if Q5 = shelter only): bodies shelter, and the day takes the abstract rate for those shops.
- **SAVE:** 0.
- **TEST:** Node (shift end). BDS: rain at tod 3000 → `civ:working` count 0 within 2 beats (if stop).
- **EFFORT:** S.
- **DEPENDS:** BF5, Q5.

#### PE6 — Births fed by food and happiness
- **FIT:** `dayStep` births: `birthChance` 0.03, needs fed ≥ 0.9 and room (people:216).
- **CONFLICT:** none. A positive, seeded chance is allowed.
- **VERDICT:** **MERGE** into `dayStep`.
- **DESIGN:**
  - chance = 0.03 × (0.5 + mood/100) × min(1.5, foodDays/10) × (1 − 0.5 × fullness), where `foodDays` = the town's food stock in days of need (ctx) and fullness = people/capacity.
  - At most 2 children per home (Millénaire).
- **TEST:** Node: rates by mood and food with a seed; a full town slows.
- **EFFORT:** S.
- **DEPENDS:** —

#### PE7 — Skill XP curve with a daily cap
- **VERDICT:** **MERGE** into PE4 (one change to the skill law).
- The daily cap already holds at one point per day. Repetition decay is dropped: a CIVITAS person has one trade.

#### PE8 — Personality archetypes, temperament, interest
- **FIT:** nothing today. `openTalk` stranger lines use `Math.random` (shop:192).
- **CONFLICT:** none.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `temperOf(p) = p.tm ?? hash(p.id) % 8` over a CIVITAS list: cheerful, dour, talkative, shy, proud, worrier, steady, curious.
  - `interestOf(p) = hash2(p.id) % 8`: building, trade, food, family, the sea, the woods, the town, news.
  - Children store `p.tm` from a parent (½ chance by seeded hash), so the field is saved only for town-born people.
  - Uses:
    - line choice (BF12, PE10);
    - which rumour is retold (interest);
    - beat cadence ±10 % (PE1);
    - petition threshold ±1 (shy +1).
- **SAVE:** 1 int for town-born people only.
- **TEST:** Node: stable per id, distribution, inheritance.
- **EFFORT:** S.
- **DEPENDS:** —

#### PE9 — Speech duration
- **VERDICT:** **MERGE** into BF12 (`40 + 1.5·chars`, ≤ 360 ticks).

#### PE10 — Data-driven dialogue (priority, conditions, memory keys, server forms)
- **FIT:** `openTalk` (shop:168) is a fixed `ActionFormData` body. `PEOPLE.greeting` / `board` exist.
- **CONFLICT:** MCA's weighted random results → our pick is the deterministic highest priority (ties by hash).
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `DIALOGUE` table in `pw_civ_talk.js`: `{id, pri, when: [cond], text, once: "day"|"ever", mem}`.
  - Conditions read census and ledger: mood band, home, job, why code, fond tier, open thread, known rumour, time, temper.
  - Priorities: CRITICAL (open thread / petition) 100 · first meeting 10 · news 5 · idle 1.
  - **Memory keys:** `p.mem = {key: expiryDay}`, at most 4 per person, pruned daily ("asked_way", "gave_gift", "saw_deed").
  - Form buttons map to actions: Notices (BF8), Show me the way (WP12), Give (WP10), Leave.
  - `ModalFormData` text input only for naming (rename the town or a street).
- **SAVE:** ≤ 4 keys for people with memories, about 5–20 KB at 1,000 people.
- **TEST:** Node `test_dialogue.mjs`: selection by priority and conditions, `once` limits, memory expiry. BDS: the talk form shows a condition-specific line (homeless person → "I've had no roof for N days").
- **EFFORT:** M.
- **DEPENDS:** PE8, BF3.

#### PE11 — Talk stops and look-at
- **FIT:** `beforeEvents.playerInteractWithEntity` (shop:147) opens forms. Walkers keep walking. `setRotation` is already used (`fishAt`).
- **CONFLICT:** none.
- **VERDICT:** **MERGE** into the shop.js interact handler.
- **DESIGN:**
  - In `system.run` after the cancel: `WALK.cancel(v)`, `civState(v, "stand")`, `setRotation` toward the player, and a memory flag `talkUntil = tick + 200`.
  - The schedule pass skips flagged bodies. Next pass, the walk is re-sent.
- **TEST:** BDS / PS5 witness: the villager stops, faces the player, then resumes.
- **EFFORT:** S.
- **DEPENDS:** —

#### PE12 — Rumours start when first told; cap 10 per person
- **FIT:** `dayStep` §6 makes every event a rumour known by its people plus 2 random witnesses. `knows` is bounded only by 30 days.
- **CONFLICT:** none. The random witnesses go away.
- **VERDICT:** **MERGE** into `dayStep` §6.
- **DESIGN:**
  - A rumour record is created known by its participants only, with `heard` = 0. `heard` counts tellings.
  - `p.knows` keeps the newest 10.
  - Proximity (Talking Colonists' 12 blocks) maps onto our contacts: household, workmates and fond friends. That is the existing `friends` graph.
- **SAVE:** less (knows was 160 K at city II).
- **TEST:** Node: ≤ 10 per person; `heard` grows only by tellings. BDS: the `statesize` knows share falls.
- **EFFORT:** S.
- **DEPENDS:** —

### WORK & ECONOMY

#### WE1 — Builders lowest layer first, fetch, doors and beds last; stage cut by block kind
- **FIT:**
  - **Already there.** `civ_stages.py` cuts by block class: ground → logs and floors → walls, doors and windows → roof → furniture, beds, lights and markers.
  - Stages k > 0 animate with `StructureAnimationMode.Layers` (lowest first).
  - `takeFromStores` takes materials when labour starts.
- **CONFLICT:** doors sit in s2 (walls), not last. Keep it: moving them to s4 leaves a doorway open for days.
- **VERDICT:** **MERGE** (exists; nothing to build). The visible fetch is WE2.

#### WE2 — Visible carters (courier score)
- **FIT:**
  - Materials leave the store chests instantly (`takeFromStores`, clock:759).
  - `BODY_POSTS` (clock:913) lists the embodied posts.
  - The walk carries anyone. `st.workToday` counts the deposits.
- **CONFLICT:**
  - Making a stage **wait** for hauling would bring back the 1.3.226 freeze and would break skipped days.
  - Hauling is visible plus a bonus only, never a gate.
- **VERDICT:** **IMPLEMENT** (absorbs WE3).
- **DESIGN:**
  - Census post `carter` (in `BODY_POSTS`): `min(4, ceil(laborSites/3))` from town I.
  - Queue `st.haul = [{from, to, g, n, age}]`, at most 12, filled when `takeFromStores` takes (from store b.id to site b.id).
  - Carter pick = the best `pri + age − √manhattan` (the MineColonies courier score). Same-destination loads are batched, up to 1 + rank (apprentice 1, journeyman 2, master 3). Skipped entries age +1 (cap 14).
  - On arrival: `b.labor.done += 200 × n_loads` (a small speed-up), and a sound.
  - **Porter rounds (WE3):** off-peak the carter runs a fixed round — bakery → market stall → centres — with `TAKE`/`PUT` steps as ledger moves (no item entities). The round finishes before home (Workers' `isSafeToGoHome`).
- **SAVE:** ≤ 12 short records per town.
- **TICK:** in the work slot, ≤ 2 sends per beat.
- **TEST:** Node `test_haul.mjs`: score order, aging, batching, cap. BDS: `haul delivered` > 0 per day from town I; stage pace not slower than the 227 baseline.
- **EFFORT:** M.
- **DEPENDS:** BF1, BF5.

#### WE3 — Porter rounds
- **VERDICT:** **MERGE** into WE2.

#### WE4 — Far-from-player statistical days
- **FIT:** **already there.**
  - `produceDaily`: the real catch or carry where the world worked, the `PRODUCE` abstract rate otherwise.
  - Skipped days queue world work in `accelWorker` (clock:1754–1808).
- **CONFLICT:** "the same roll near and far" contradicts D-C542 (a real day's stone is the stone carried).
- **VERDICT:** **MERGE** (exists; no change).

#### WE5 — Player-owned stall
- **FIT:**
  - `buyAt` (shoppers), the clerk and market forms.
  - `COIN.issue` (coins go to a player's inventory) and `L.purse` (citizens' money).
- **CONFLICT:** coins paid by villagers must stay inside the mint ledger. That needs an `issueTo(container)` variant, so the coin census counts coins in the stall's barrel.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - The player places a barrel with a sign `[stall]` inside a town. `playerPlaceBlock` registers it as `st.pstalls = [{x, y, z, owner}]`, at most 3 per town.
  - Price setting cheap / normal / dear (the sign's second line) → sale factor 1.2 / 1 / 0.6 vs `counterPrice`.
  - In the market pass, a shopper whose counter lacks a good buys from a stall that has it when the stall's price ≤ town price × 1.1. Deterministic order: cheapest first.
  - Pay: `L.purse` → coins into the barrel (`issueTo`) → `L.playerNet` −, keeping the invariant.
- **SAVE:** ≤ 3 small records per town.
- **TEST:** Node: invariant and choice. BDS: a stocked stall sells ≥ 1 per market hour while the town is short.
- **EFFORT:** M.
- **DEPENDS:** BF9, WE12.

#### WE6 — Prices drift with sales
- **VERDICT:** **MERGE** into BF9 (the `sold` demand term).

#### WE7 — Per-counter wobble
- **VERDICT:** **MERGE** into BF9 (seeded ±10 %, unsaved).

#### WE8 — Scarcity-first production
- **FIT:** `ECON.dayStep` §1 runs every output of a workshop at fixed ratios: lumberyard timber + planks, quarry stone + lime, smithy tools + iron.
- **CONFLICT:** none.
- **VERDICT:** **MERGE** into `ECON.dayStep`.
- **DESIGN:**
  - For multi-output kinds, split the runs by score = `value + max(0, 8 − 1.5·daysOfStock) − 2.5·daysOfStock` (Townstead). Shares are proportional to positive scores.
  - Deterministic: the jitter is a hash, not a roll.
- **TEST:** Node: a scarce output gets the larger share; the totals are conserved.
- **EFFORT:** S.
- **DEPENDS:** —

#### WE9 — Caps and reserves per good
- **FIT:** stock is uncapped. The shop and market sell to 0. The wagons in `tradeAlong` export up to ¼ of stock.
- **CONFLICT:** none.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `ECON.CAP` (stone 4096, timber 2048, grain 1024, …) and `ECON.RESERVE` (food 3 days of need, materials = the next 3 waiting bills).
  - Production stops at the cap. The abstract runs are clipped. `workBeat` checks `L.stock[g] ≥ cap` → why code `STOCK_FULL`, and the hands rest.
  - `quote` / `counterPrice` sell `n ≤ stock − reserve`. `tradeAlong` never exports below the reserve.
- **SAVE:** 0 (constants).
- **TEST:** Node: caps clip; reserves hold against player buys and wagons.
- **EFFORT:** S.
- **DEPENDS:** BF3.

#### WE10 — Small coins
- **FIT:** one coin item `pw:gold_coin` = 12 p. Odd sums round in the windows (`Math.floor` / `ceil`).
- **CONFLICT:** a new item and texture (RP). The mint ledger must count denominations.
- **VERDICT:** **IMPLEMENT**, pending **Q7**.
- **DESIGN:**
  - `pw:silver_penny` (1 p) item and pile.
  - `COIN.issue` / `takeCoins` pay in gold, then pennies (greedy split). The ledger gets `issuedP` / `returnedP`.
  - Windows show exact prices.
- **TEST:** Node: split and combine; the invariant. BDS: buying a 36 p ration pays exactly.
- **EFFORT:** M.
- **DEPENDS:** Q7.

#### WE11 — Tax dial (deterministic only)
- **FIT:** `HEARTH` 12 p every 30 days (economy:187). The mood council-trust term.
- **CONFLICT:** MCA's riot roll is chance-based harm → dropped. Only fixed effects remain.
- **VERDICT:** **MERGE** into the ECON hearth tax.
- **DESIGN:**
  - `L.tax` ∈ low / normal / high → HEARTH × 0.75 / 1 / 1.25.
  - A `dayStep` mood term +3 / 0 / −3.
  - Command `pw:clock tax <level>` (council gate per Q11).
- **TEST:** Node: the effects are exact.
- **EFFORT:** S.
- **DEPENDS:** —

#### WE12 — Ledger audit and money supply
- **FIT:** **already there.**
  - The invariant and `LEDGER DRIFT` (economy:250).
  - `COIN.ledger` lines (200) with issued, returned, destroyed and in circulation.
  - `L.history` (60 days).
- **CONFLICT:** none.
- **VERDICT:** **MERGE** (exists). Add `pw:clock audit`: the invariant terms, the mint census and the last 8 coin lines. The probe calls it per tier.
- **EFFORT:** S.

#### WE13 — Notice-board quests as data
- **VERDICT:** **MERGE** into BF8.

#### WE14 — Seed and counter instead of saved lists
- **FIT:** saved lists that are diagnostics or recomputable:
  - `st.marketGate`, written every market pass (clock:7231);
  - `st.counters.shops` (:673);
  - `st.market.homes` (:692) — a list that grows per buy;
  - `st.marketTry.shoppers` (:7180).
- **CONFLICT:** none.
- **VERDICT:** **IMPLEMENT** (as a principle and these conversions).
- **DESIGN:**
  - Move the diagnostics to a memory `DIAG` map, readable in `status`.
  - `st.market.homes` → a count + a memory Set of today's homes. After a reload a household may shop twice in one day, which is harmless.
  - New features use seeds:
    - board `{day, roll}` (BF8);
    - wobble `hash(day, counter)` (BF9);
    - shift offset `hash(id)` (BF5);
    - temperament `hash(id)` (PE8).
- **SAVE:** less (a few KB per town at city sizes).
- **TEST:** BDS: `statesize` before and after; `status` still shows the market gate.
- **EFFORT:** S.
- **DEPENDS:** BF2.

### GROWTH & BUILDING

#### GB1 — Weighted next-building pick with cooldowns, max 2 works
- **VERDICT:** **MERGE** into BF6. The cooldowns are kept. "Max 2 works" is dropped: it contradicts the 1.3.226 crew-share law and the charter pace.

#### GB2 — Template costs
- **VERDICT:** **MERGE** (exists): the catalogue's `bom` per stage is read from the stage files by the build tool.
- Millénaire's unit rules are not needed: our bill counts blocks by class (stone, timber, planks, thatch, glass), the same class the ledger stocks.

#### GB3 — Places per building
- **VERDICT:** **MERGE** into BF7.

#### GB4 — Tier gates including happiness
- **VERDICT:** **MERGE** (exists): `moodOk` (MOOD_GATE 45), `prosperityOk`, `allRoofed`, `civicWorks` (the required set), `representationOk`, `TIER_DAYS`, and the charter lots (clock:1973).
- Village Ruler's population and building table adds nothing we lack.

#### GB5 — Work-order queue
- **VERDICT:** **MERGE** into BF6 (`st.prio` + `pw:clock prio`).
- The queue itself exists: `tierWork.items`, `leftover`, `kitQueue`, `b.labor`.

#### GB6 — Town titles
- **FIT:** `tierLabel` gives the class (village … capital, PORT CITY). There is no character title.
- **CONFLICT:** none.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `spiritOf(plots)`: points per family, derived daily and not saved:

    | Family | Points |
    |---|---|
    | fishery spot | nautical 5 |
    | quarry | mining 5 |
    | lumberyard | woodland 5 |
    | bakery, butcher | market 3 |
    | inn | travel 4 |
    | farms | pastoral 4 |
    | smithy | craft 4 |
    | palace / manor | crown 8 |

  - Tier thresholds 25 / 60 / 140 / 300 / 600. A dominant spirit needs a 0.4 share.
  - Title = a word from our own list per spirit and tier ("Fishing Hamlet → Harbour Town → Port"), plus `tierLabel`.
  - Shown on the board sign, in `status`, and on "Now entering" (TR10). A chat line when it changes (`st.titleSaid`).
- **SAVE:** one short string.
- **TEST:** Node: points → title table.
- **EFFORT:** S.
- **DEPENDS:** TR10.

#### GB7 — Marker blocks in templates (counters, beds, workstations self-register)
- **FIT:**
  - Station markers already ride in s4 as `pw:marker` entities.
  - `stationOf` scans the entities in the footprint at hire time (shop:33), a `getEntities` call.
  - The catalogue has `chests`, `door` and `lids`, but no beds or seats.
- **CONFLICT:** none. Positions are precomputed offline, so there is no runtime block scan.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - The build tool that writes `pw_civ_buildings.js` also emits `marks: {station: [[x,y,z]], bed: [...], counter: [...], seat: [...], look: [...]}`.
    - Read from the s4 palette (bed blocks, `pw:marker` tags) and from the marker blocks civgen places.
    - It also writes `beds: n` for BF7.
  - Runtime: `rotXZ` to world, cached on `b.marks` (memory). `stationOf` reads the catalogue first and keeps the entity scan as the fallback.
- **SAVE:** 0 (code, not save). The catalogue grows by a few KB.
- **TEST:** Node: the catalogue has `marks` for every family, and the rotation law gives the same cell as the marker entity in a test placement. BDS: hires use the catalogue (the entity-scan count is 0).
- **EFFORT:** M (build tool).
- **DEPENDS:** —

#### GB8 — Pillar-to-ground marker
- **FIT:** `slotRelief` `kind: "stilts"` and `kitLandPrep` (clock:4313) build posts. `terrace` is skipped for stilts (clock:591).
- **VERDICT:** **MERGE** into `kitLandPrep`.
- **DESIGN:**
  - The catalogue gains `marks.pillar` (corner posts).
  - The job sets the post block from the floor down to ground at the computed cells through `blockAt`, at most 24 (`STILTS_MAX`), and stops at the first solid block. No `below()`.
  - Spread over the plot's land job.
- **TEST:** BDS: a stilts house has every post reaching the ground (`sewers`-style counter `posts ok`).
- **EFFORT:** S–M.
- **DEPENDS:** GB7.

#### GB9 — Fill with local ground
- **FIT:** `terrace` / `kitLandPrep` / `levelColumn` fill with fixed `FILL_IN` dirt, `FILL_OUT` cobble, `GROUND_TOP` grass (clock:393, 4270).
- **VERDICT:** **MERGE.**
- **DESIGN:**
  - `localGround(x, z)` = the top block id at `groundAt` of the nearest unworked neighbour column, read once per plot through `blockAt`.
  - Mapped: grass/dirt → grass + dirt; sand → sand + sandstone; snow → snow + dirt; stone → stone. Used for the top and fill.
- **TEST:** BDS: a beach plot's berm is sand.
- **EFFORT:** S.
- **DEPENDS:** —

#### GB10 — Hidden marker entity runs a one-time script
- **FIT:** `placeStage` already runs a post-place hook (`post()`, clock:603) and knows exactly when each stage lands.
- **CONFLICT:** entity markers add entity loads and an `entitySpawn` path for something our own placement already knows.
- **VERDICT:** **DROP.** Our post-place hook is the one-time script.

#### GB11 — Weathered variants via integrity
- **VERDICT:** **MERGE** into EN2.

#### GB12 — District palettes
- **FIT:** four skins per family (`_a.._d`), picked by seeded random (`familyOf` / `skinsOf`, clock:2122).
- **CONFLICT:** a post-placement block swap would be thousands of `setType` per building. Skins do the same thing for free.
- **VERDICT:** **MERGE** into the skin choice.
- **DESIGN:**
  - The skin is chosen by `DISTRICT` and tier class: prestige → `d` (stone), craft → `c`, homes → `a`/`b` by street parity, edge → `a`.
  - The table is to be confirmed against what each skin looks like.
- **TEST:** Node: deterministic skin per district.
- **EFFORT:** S.
- **DEPENDS:** —

#### GB13 — Small-slot fillers (well, cart, lamp) and about 30 % gardens
- **FIT:** `KIT.placeAlong` leaves stretches shorter than a house bare. The frontage census (clock:4005) counts them.
- **CONFLICT:** **gardens**: frontage is the measured growth bottleneck (26 % legal at Town III, GROWTH-PROGRAM §0). Holding 15–30 % empty works against the charter → **Q8**.
- **VERDICT:** **IMPLEMENT** fillers; gardens per Q8.
- **DESIGN:**
  - After a street's houses are placed, each leftover stretch from 4 up to (cottage_s width − 1) gets a filler template (`well` exists; `cart`, `lamp`, `bench` from civgen). One per stretch, deterministic by t.
  - Fillers are not lots and do not count toward the charter.
  - Gardens (if Q8 = yes): a district "empty" share (core 0 %, homes 15 %, edge 30 %), applied only after the tier's charter is met.
- **SAVE:** a filler is a building record (small).
- **TEST:** BDS: the frontage census counts `filler` stretches; the lots still meet the charter.
- **EFFORT:** S–M (templates).
- **DEPENDS:** —

#### GB14 — Clear headroom over streets
- **FIT:** **already there.** `kitPrep` cuts H+1 .. max(g, H)+3 and `clearTreesOver` up to 30 (clock:2711, 2279). `sweepDaily` / `canopyDaily` clear floating leaves.
- **VERDICT:** **MERGE.** Add one check in `sweepDaily`: leaves or trunks inside the corridor's headroom (H+1 .. H+4) are cleared. Clearing is not felling (BIGCANOPY).
- **EFFORT:** S.

### TOWNS & ROADS

#### TR1 — District lot rules (merchants by the square, rich by parks, poor outward, unlock order)
- **FIT:**
  - `DISTRICT` + `kitSlot` order (clock:3887–3942): prestige on the main streets; homes outermost first (1.3.226); edge trades at the far ends.
  - Unlock order is the tier charter + `CIVIC`. `st.park` exists.
- **VERDICT:** **MERGE** into `kitSlot`.
- **DESIGN:**
  - Manor: prefer slots within 40 of `st.park` and ≥ 60 from edge trades.
  - A second bakery or butcher (not a centre) never takes a slot within 30 of another of its kind.
  - Town hall and inn: prefer frontage facing the square (`streetDist` minimum).
  - Watabou's ladder confirms our tier order. No queue import.
- **TEST:** Node over a synthetic street set: rule preferences.
- **EFFORT:** S.
- **DEPENDS:** —

#### TR2 — Lot score by water share and percentile heights
- **FIT:** `slotRelief` (clock:3798) uses max − min; **any** water cell → reject.
- **VERDICT:** **MERGE** into `slotRelief`.
- **DESIGN:**
  - Over the sampled cells: water share ≤ 8 % (not 0).
  - Cut and fill measured on the 20th–80th percentile heights instead of lo/hi. The extreme cells still go through the existing cut/fill classes.
- **TEST:** Node `test_relief.mjs` with a synthetic site: one boulder or one wet cell no longer vetoes a lot; a real slope still does. BDS: the frontage `fits` count rises against 227 (more lots at Town III).
- **EFFORT:** S.
- **DEPENDS:** —

#### TR3 — Accept plots with a few bad cells
- **VERDICT:** **MERGE** into TR2.
- Error budget: ≤ 10 bad cells, or 5 % for boxes over 200 m². Bad = outside H ± 10 or wet. Over budget → reject.

#### TR4 — Survey heights skipping vegetation
- **FIT:** `surveyJob` (clock:6528) reads raw `getTopmostBlock`, so leaves count as ground (forests read as hills), and it **throws on unloaded columns** (the leak path). `groundAt` (clock:313) already skips trees and plants. `readSiteJob` already does it right.
- **VERDICT:** **MERGE** into `surveyJob`, in B1 as a hygiene fix.
- **DESIGN:** use `topAt` + the `groundAt` walk-down. Unloaded → `asleep++` with no throw.
- **TEST:** BDS: a survey over a forest gives the same relief as over cleared land; engine throws 0 during the survey.
- **EFFORT:** S.
- **DEPENDS:** —

#### TR5 — Wall and gate rules
- **FIT:** `queueWall` (clock:5256): gates where a street axis meets the ring (13 wide) plus stub roads. `GREENBELT` keeps 24 outside the wall unbuilt.
- **VERDICT:** **MERGE** into `queueWall`.
- **DESIGN:**
  - Two gate centres closer than 26 cells merge into one (no adjacent gates).
  - A tower piece on each ring corner and every 48 cells between gates.
  - Gate suburbs: lots touching a gate's stub road are exempt from `GREENBELT` (watabou's suburbs at the gates), for homes only.
- **TEST:** Node: ring with gates → merged gates, towers. BDS: the wall count and gate count are printed.
- **EFFORT:** S.
- **DEPENDS:** —

#### TR6 — Country-road costs (contour discount, grade penalties, slabs, smoothing, 80 % partial)
- **FIT:** `LAND.findRoadJob` (land:279): A* with `ROAD_SLOPE` 3, a water cost, `ROAD_MAX_NODES` 60,000. `KIT.planProfile` and `layRoadOp` lay `roads7`.
- **VERDICT:** **MERGE** into `findRoadJob` / `layRoadOp`.
- **DESIGN:**
  - Cost × (1 − 0.45·alignment·min(1, 2|∇h|)) with a floor of 0.3, the gradient from the site field.
  - Grade over 8 % + 600·(g − 0.08)/0.08; over 15 % + 6000·…
  - Median-5 + forward/backward ±1 clamp + de-spike on the laid profile.
  - A bottom slab where the next cell is 1 higher.
  - When the node cap is hit and the best node has made ≥ 80 % progress, accept it and finish with a second search.
- **TEST:** Node `test_road.mjs` on synthetic hills: the contour route beats the fall line; the profile never steps by more than 1; partial acceptance. BDS: daughter roads are laid with fewer `ROAD_TRIES`.
- **EFFORT:** M.
- **DEPENDS:** —

#### TR7 — Network rules (mutual near towns, 30° separation, T-junctions)
- **FIT:** daughters (`maybeFoundDaughter`) connect only to the mother (`startRoadJob`, clock:6320). `findRoadJob` already joins existing streets through `fixedH`.
- **VERDICT:** **MERGE** into `startRoadJob`.
- **DESIGN:**
  - A new town connects to its nearest town. It adds a second link only if the bearing differs ≥ 30° from the first, and only if the link is mutual (each is in the other's 2 nearest).
  - The target may be a `roads7` cell (a T-junction: add road cells to `fixedH`).
- **TEST:** Node: graph rules on synthetic points.
- **EFFORT:** S–M.
- **DEPENDS:** TR6.

#### TR8 — Roadside hamlets
- **FIT:** contour lanes (`openLane`, `LN.planLane`) start from a street's dead end. Gate stub roads and daughter roads (`roads7`) exist.
- **CONFLICT:** the influence ring and `GREENBELT`. Hamlets stay inside influence.
- **VERDICT:** **MERGE** into the lane planner: a lane may depart from a `roads7` cell outside the wall (the growth program's backlog "lanes from released windows and lane ends", extended to roads).
- **DESIGN:**
  - `departures(st)` adds `roads7` cells every 24 cells.
  - Lots along a lane by the existing `laneSlot`.
  - Only after the streets, lanes and benches inside have failed (`laneBlocked`).
- **TEST:** BDS: at metropolis, lots on road lanes > 0 when the core is full.
- **EFFORT:** M.
- **DEPENDS:** TR5.

#### TR9 — Trade caravans and relations (2+ towns)
- **FIT:** `tradeAlong` (clock:6386) moves goods by price difference along `st.roads`. `ladder` turns days of inbound trade into a stand, then a branch. `representation`.
- **CONFLICT:**
  - Millénaire's nightly 10 % ±10–19 relation drift is chance-based → dropped.
  - Village Ruler's ambush rolls → dropped (violence and chance).
- **VERDICT:** **MERGE** into `tradeAlong` / `ladder`.
- **DESIGN:**
  - Relation = `st.inbound[partner].days` + the partner's days (deterministic, already saved).
  - A visible caravan: when a player is within 64 blocks of a road with today's wagons, one cart body (villager + pace) walks 64 cells of the road and despawns. It uses the walk graph's road cells. No body is kept far from players.
- **SAVE:** 0.
- **TEST:** BDS (two towns): the cart appears when the probe stands by the road and the ladder still ticks.
- **EFFORT:** M.
- **DEPENDS:** TR7.

#### TR10 — Names and "Now entering" titles
- **FIT:** `st.name` exists. `inInfluence(st, x, z)` (clock:2788). The actionbar is already used (keys:97).
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - **District names:** `st.names = {sid: name}`, first-free from a CIVITAS word list (prefix by the street's role or the area's biome + suffix, "Millgate", "Lower Steps"). Unique per town; saved once.
  - **Zone:** heartbeat slot 9, every 20 ticks per player: town (influence box) → district (nearest street, within 20) → `setActionBar("Now entering <Town> · <District>")` on change. Title on entering the town, with the GB6 title.
  - Memory `zone` per player.
- **SAVE:** about 20 chars per street.
- **TEST:** Node: name uniqueness. BDS: walk the probe across two districts → 2 actionbar lines, ≤ 1 ms per player.
- **EFFORT:** S.
- **DEPENDS:** BF1.

#### TR11 — Villagers give way on streets
- **FIT:** walkers follow a lead along graph cells (corridor cells at sidewalk height). There is no traffic rule; bodies push each other.
- **CONFLICT:** none.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - Keep right: when `sendNow` builds a path over a kit corridor, cells are shifted to the travel-right side (w 8–11 or 1–4 by direction) where the graph holds those cells.
  - Head-on: in the walk beat, two walkers within 1.7 heading opposite → the higher id's lead shifts 1 cell right for 10 ticks.
  - No new entity queries: walkers are known.
- **SAVE:** 0.
- **TEST:** BDS walktest: 8 crossing walkers, stuck count ≤ 227's, arrival time within +10 %.
- **EFFORT:** M.
- **DEPENDS:** BF1.

### WATCH & PLAYER

#### WP1 — Paid watch and morale (desertion?)
- **FIT:** the watch is a census post (`jobPosts`, `WATCH_POSTS`) but is **not on the payroll** (`STATION_WAGE` covers shops only, economy:45). Mood has `paid` (town-wide arrears).
- **CONFLICT:** desertion (leaving the census) is a deterministic negative → **Q1**.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - Payroll: `ctx.posts` adds watch × `WAGE.watch` (96 p) and the sewer keeper.
  - **Priority order:** watch first, then station workers. Shortfalls fall on the last in order (Lightman's all-or-nothing replaced by an order).
  - `p.mor` (watch only, starts at 60): unpaid day × 0.7; paid, housed and fed day +2 (cap 100).
  - Morale < 40: the round skips every other stop (`stopsOf`).
  - Morale < 20: per Q1, deserts (leaves like `lowDays`), or just stays at half rounds.
- **SAVE:** 1 int per watchman.
- **TEST:** Node: pay order; morale math. BDS: an unpaid test town shows falling `st.watch.rounds`.
- **EFFORT:** S–M.
- **DEPENDS:** Q1.

#### WP2 — The bell sends civilians home (non-violent)
- **FIT:** `goalFor` already has `homeInside`. The watch counts `seen` monsters. There is a bell on the square or town hall.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - Trigger (deterministic): a player rings a bell inside a town (`playerInteractWithBlock` on `minecraft:bell`), or the watch saw ≥ 3 monsters on its round in one beat.
  - → `st.alarm = tick + 1200` (memory) → `goalFor` returns `homeInside` for everyone except the watch.
  - A line "The bell! Everyone indoors."
- **SAVE:** 0.
- **TEST:** BDS: ring → ≥ 80 % of bodies are `civ:state:home` within 60 s.
- **EFFORT:** S.
- **DEPENDS:** BF1.

#### WP3 — Watch rules as data (no new violence)
- **FIT:** the `HOSTILE` list and the inline target logic (watch:28, 143).
- **VERDICT:** **MERGE** into `pw_civ_watch.js`.
- **DESIGN:**
  - `RULES = {target: [...HOSTILE], ignore: [villager, golem, player], avoid: [creeper: step back 10], prio: [witch, pillager family, zombie family, rest]}`. Ignores win.
  - After a chase, resume at the nearest stop (`stopsOf`), not the next index.
  - Targets stay monsters only (Utopia-first).
- **TEST:** Node: rule resolution; nearest-stop pick.
- **EFFORT:** S.
- **DEPENDS:** —

#### WP4 — Night-watch light
- **FIT:** the watch beat moves watchmen at night.
- **CONFLICT:** the orphan-light lesson (Human Companions) → positions must be saved.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - For at most 6 watchmen within 32 of a player: place `minecraft:light_block` (level 10) at the head cell only when it is air, through `blockAt`. Move it only when the cell changes.
  - The previous cell is cleared only if it is still a light block.
  - `st.lights` (≤ 6 cells) is saved and cleared at load and at dawn.
- **SAVE:** ≤ 6 cells per town.
- **TICK:** ≤ 12 setType per 10 ticks.
- **TEST:** BDS: no light blocks left after dawn or a reload (scan of the patrol stops).
- **EFFORT:** S–M.
- **DEPENDS:** BF1.

#### WP5 — Festivals (fair, wedding, feast)
- **FIT:**
  - The dusk square (`leisureGoal`) and `squareSlot` (the ring cells).
  - Census weddings (`dayStep` events).
  - Tier-ups (`tierUpBody`).
- **CONFLICT:** frequency and type are his call → **Q3**. Our gathering is the dusk slot, not work hours (Smart Villagers holds festivals 1000–9000).
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - `festivalOf(st, day)` (pure, deterministic):
    - wedding = a census wedding yesterday;
    - feast = a tier laid out yesterday;
    - fair = every N-th day (Q3), on the market day.
  - At dusk, bodies go to ring slots `angle = id·47°` around the well (an existing square ring cell when close).
  - Particles every 40 ticks near players. +3 mood for everyone that day (census).
  - The log line becomes a rumour.
- **SAVE:** 0 (derived).
- **TEST:** Node: `festivalOf` schedule. BDS: dusk on a wedding day has bodies in the ring.
- **EFFORT:** M.
- **DEPENDS:** BF5, BF12, Q3.

#### WP6 — Leader's dusk speech and tavern visits
- **FIT:** the town hall keeper (clerk), the palace, the dusk square. The tavern half is PE2.
- **VERDICT:** **IMPLEMENT** (speech). Tavern visits → PE2.
- **DESIGN:**
  - Leader = the town hall keeper, or the eldest master.
  - 11000–11600: the leader stands at the square's north edge (or the palace gate) and speaks 3 bubble lines built from yesterday's ledger and chronicle (a shortage, a building finished, the tier).
  - Bodies on the square face the leader.
  - Only when a player is within 32.
- **SAVE:** 0.
- **TEST:** BDS: speech lines are logged per dusk with the probe present.
- **EFFORT:** S–M.
- **DEPENDS:** BF12, BF5.

#### WP7 — Chronicle readable in game
- **FIT:** `st.log` (cut to 60 at save), the `log` command, the board sign's last lines.
- **CONFLICT:** Millénaire's 500 typed entries would break the save budget.
- **VERDICT:** **MERGE** into `st.log` + the BF8 clerk form.
- **DESIGN:**
  - A "Chronicle" button: the last 20 lines, paged.
  - A compact `st.annals` (≤ 40 milestones `{d, k, n}`: founding, tiers, palace, first masters, daughters) kept for life.
- **SAVE:** about 1–2 KB per town.
- **TEST:** BDS: the form lists the annals.
- **EFFORT:** S.
- **DEPENDS:** BF8.

#### WP8 — Witnessed deeds → memory, rumour, trust; settle in goods
- **FIT:**
  - `playerBreakBlock` is already subscribed (coin, fell rules).
  - Trust key `"player"` and `playerFond`. Rumours and threads. Clerk forms.
- **CONFLICT:**
  - Default on vs the narrative phase → **Q6**.
  - Observant Villagers' line-of-sight raycast is costly; ours uses distance and height (deterministic).
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - Deeds: breaking a block inside a plot box, taking from a counter or store chest (`playerInteractWithBlock` + a chest-count check at close), breaking a station.
  - Law table: `{deed: hit, amends}` (counter −2, station −3, wall −1).
  - Witnesses: cached bodies ≤ 12 blocks and |dy| ≤ 4.
  - Effects: `learn(p, "player", 0)`, `playerFond −hit×5`, a `mem` key `saw_deed`, and a rumour (kind `deed`).
  - Amends via the clerk: pay the goods or coins of the damage × 1.5 → memory keys cleared, rumour closed.
- **SAVE:** inside existing fields.
- **TEST:** Node: law table, amends math. BDS: the probe breaks a counter block in view → a rumour exists; amends clears it.
- **EFFORT:** M.
- **DEPENDS:** PE10, BF8, Q6.

#### WP9 — Standing sets prices
- **FIT:** `ECON.quote` / `sell`, `SHOP_RATE` / `MARKET_RATE`, `playerFond`, `playerNet`.
- **VERDICT:** **MERGE** into `quote` / `marketOffer` / `openShop`.
- **DESIGN:**
  - `st.standing` = the mean `playerFond` of people who know the player, computed daily.

    | Standing | Buy | Sell |
    |---|---|---|
    | friend (≥ 40) | × 0.9 | × 1.05 |
    | hero (≥ 75) | × 0.8 | × 1.1 |
    | unfriendly (≤ −20, only via WP8) | × 1.2 | — |

  - The invariant is unchanged (coins in and out through the same calls).
- **SAVE:** 1 number.
- **TEST:** Node: factor bands; the invariant.
- **EFFORT:** S.
- **DEPENDS:** —

#### WP10 — Gift saturation and talk fatigue
- **FIT:** every `openTalk` calls `playerContact(person, 1)`, so standing can be farmed by clicking. There are no gifts.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - **Talk:** contact counts only for the first 3 talks per person per day (`p.td` = day, `p.tn` = count, saved while set).
  - **Gift:** a "Give" button with the held item. Value = `BASE` price → fond `+min(10, √value)` × 0.5^(gifts to this person today); +2 on interest match (PE8).
- **SAVE:** 2 small ints for people talked to today.
- **TEST:** Node: diminishing curve.
- **EFFORT:** S.
- **DEPENDS:** PE8, PE10.

#### WP11 — Player title ladder and council votes
- **FIT:** nothing today. Council-like effects exist: trust `town:council`, the tax dial (WE11), `prio` (BF6).
- **CONFLICT:** whether commands become council-gated → **Q11**.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - **Ladder** per town `st.ptitle[player]`, from deterministic requirements:
    - stranger → citizen: standing ≥ 20 + 10 trades;
    - burgher: 10 board slips or a stall;
    - alderman: standing ≥ 50 + town II;
    - councillor: city + 30 slips.
  - **Votes:** each adult votes yes if `playerFond` ≥ 40, no if < 0, else abstains. Passes on yes > no. Recall needs 2/3. Votes are counted on the census in one daily pass.
  - Unlocks: the tax dial, the build priority, naming a district (ModalForm).
- **SAVE:** a small map per town.
- **TEST:** Node: vote math; ladder.
- **EFFORT:** M.
- **DEPENDS:** WP9, BF8, Q11.

#### WP12 — A guide who walks you to a place
- **FIT:** the walk graph and `WALK.send`. The talk form (PE10). Door fronts.
- **CONFLICT:** TuDiGong teleports the guide when the player is more than 30 away. Our walk law: "nothing is ever teleported here" except the stuck rescue. The guide waits instead.
- **VERDICT:** **IMPLEMENT.**
- **DESIGN:**
  - "Show me the way to…" (inn, market, smithy, the town hall, my last bought shop).
  - The asker's nearest body becomes the guide. `WALK.send` to the door front.
  - Every walk beat: player more than 6 behind → the lead holds in place (pause). Player ahead of the guide → pace 35. Within 4 of the door → particles and a line, then the guide returns to its goal.
  - Cancelled after 2,400 ticks.
- **SAVE:** 0.
- **TEST:** BDS: the probe follows → arrival logged.
- **EFFORT:** M.
- **DEPENDS:** PE10, BF1.

---

## 3. Verdict tally (80 ideas)

**IMPLEMENT — 36**

| Group | Ideas |
|---|---|
| Build first (10) | BF1, BF2, BF3, BF4, BF5, BF6, BF8, BF10, BF11, BF12 |
| Engine (3) | EN1 (gated), EN2, EN4 |
| People (4) | PE1, PE4, PE8, PE10 |
| Work & economy (5) | WE2, WE5, WE9, WE10 (pending Q7), WE14 |
| Growth & building (3) | GB6, GB7, GB13 |
| Towns & roads (2) | TR10, TR11 |
| Watch & player (9) | WP1, WP2, WP4, WP5, WP6, WP8, WP10, WP11, WP12 |

**MERGE into existing CIVITAS code or another idea — 42**

| Group | Ideas |
|---|---|
| Build first | BF7, BF9 |
| Engine | EN5 |
| People | PE2, PE3, PE5, PE6, PE7, PE9, PE11, PE12 |
| Work & economy | WE1, WE3, WE4, WE6, WE7, WE8, WE11, WE12, WE13 |
| Growth & building | GB1, GB2, GB3, GB4, GB5, GB8, GB9, GB11, GB12, GB14 |
| Towns & roads | TR1, TR2, TR3, TR4, TR5, TR6, TR7, TR8, TR9 |
| Watch & player | WP3, WP7, WP9 |

**DROP — 2**
- **EN3** placeJigsaw: a foreign architecture that needs API 2.5+.
- **GB10** marker entity: our post-place hook already does it.

**Parts dropped inside kept ideas:**
- "max 2 works" (GB1 → BF6);
- random relation drift and ambushes (TR9);
- the riot roll (WE11);
- random witnesses (PE12);
- the guide's teleport (WP12);
- per-person hunger 0..100 (BF4: food is town-wide in our model).

**Already in CIVITAS, so no work needed:** WE1, WE4, GB2, GB4, plus most of GB14 and WE12.

---

## 4. Batch plan

Every batch ends with: node suites (old + new) → `js_dupcheck` → BDS gate climbing to M III (no Hang, no memory warning, no tick > 1 s, sewers all linked, lots meet the charter) → the batch's own signals below.

| Batch | Ideas | Gate signals |
|---|---|---|
| **B1: heartbeat and engine hygiene** | BF1 heartbeat + shared bodies cache; the hygiene pass (`blockAt` exported; fishery reads; `hasNaturalCanopy` wrapper; work reads); TR4 survey heights; EN4 dynamic-property bytes | per-system ms per 1,200 ticks; engine throws flat; worst tick; DP bytes per tier |
| **B2: saves, reasons, safe felling** | BF2 sectioned saves; WE14 diagnostics out of the save; BF3 why-idle codes + icons + `why` command; BF10 real-tree felling + claims | DP writes per minute < 2 MB; `statesize` per key; why-tally per tier; player log cabin untouched |
| **B3: people I (census law, pure)** | BF4 needs that grow + mood-tier output; PE3 grief; PE6 births; PE12 rumours (cap 10); PE4 + PE7 house level / skill curve / diet; PE8 temperament; (Q4 sickness change if approved) | mood-tier histogram; knows share of the save falls; births per 10 days |
| **B4: people II (bodies and the day)** | BF5 shifts + offsets (+ PE5 leave-in-time; rain per Q5); PE1 work beats; PE2 inn visits; BF7 places per building (nearest job / home, move) | walk starts spread at shift ends; mean home↔work distance; keepers' beat variety |
| **B5: people III (voice)** | BF12 speech + overheard (+ PE9); PE10 dialogue table + memory keys; PE11 talk stop + look-at; BF11 petitioners | bubbles restored; petitions in a starved test town; PS5 witness of nameTag lines |
| **B6: growth and building** | BF6 weighted pick (+ GB1, GB5; GB2 and GB4 exist); GB7 catalogue marks + beds (build tool); GB8 pillars; GB9 local ground; GB12 district skins; GB13 fillers (gardens per Q8); GB14 headroom check; TR1 district rules; TR2 + TR3 lot score; EN2 weathering (per Q9) | lots meet the charter at every tier; frontage fits up; stilt posts reach the ground |
| **B7: economy core (ledger, pure)** | BF9 stall customers + counter prices (+ WE6, WE7); WE8 scarcity-first; WE9 caps / reserves; WE11 tax dial; WE12 audit command; BF8 notice board + clerk (+ WE13) | invariant 0 drift; board slips deliver; stall buys > 0 |
| **B8: economy bodies** | WE2 carters + porter rounds (+ WE3); WE5 player stall; WE10 small coins (if Q7 = yes) | haul delivered per day; stage pace ≥ the 227 baseline; coin census exact |
| **B9: towns and roads** | TR5 walls / gates; TR6 road costs; TR7 network; TR8 road lanes; TR9 caravans + relation; TR10 names + "Now entering" (+ GB6 titles); TR11 give way | daughter roads laid in fewer tries; walktest stuck ≤ 227; zone lines per player ≤ 1 ms |
| **B10: the watch** | WP1 paid watch + morale (desertion per Q1); WP2 bell → home; WP3 rules as data; WP4 night light; WP7 chronicle + annals | payroll order; bell → 80 % home in 60 s; no light blocks after dawn or reload |
| **B11: player** | WP9 standing prices; WP10 gift / talk fatigue; WP8 deeds (default per Q6); WP5 festivals (frequency per Q3); WP6 dusk speech; WP12 guide; WP11 titles + votes (gating per Q11) | festival ring at dusk on a wedding day; guide arrival; deed rumour + amends |
| **B12: engine-gated (last)** | EN1 after the manifest upgrade + PS5 version read (TickingAreaManager → LocatorBar → text primitives → container / pickup events); EN5 transport_items BDS test | each feature's detect line; the 2.3.0 fallback still passes |

**Order rationale.**
- B1 and B2 remove the measured cost and leak sources and make every later batch observable (why codes, per-system ms, DP bytes).
- B3 is pure census law: node-testable and cheap to gate.
- B4 and B5 put the new law on the bodies.
- B6 touches the growth law and needs the build tool, so it goes after the people are stable.
- The economy follows growth, because board slips and carters read real waiting bills.
- Towns, watch and player features layer on top.
- Engine features wait for his upgrade decision.

---

## 5. Open questions for Abs0lum (decisions only)

1. **Q1, desertion.** When the treasury cannot pay the watch, its morale falls by a fixed rule. At very low morale (< 20 for several days), should a watchman **leave the town** (a deterministic desertion), or only walk half his rounds until paid?
2. **Q2, strike tier.** Mood already sets output (1.1 / 1.0 / 0.85 / 0.7). Should a workshop whose workers stay miserable (< 15 for 3 days) **stop producing entirely** (a deterministic strike), or should output never fall below 0.7?
3. **Q3, festivals.** Which ones, and how often?
   - A **wedding** gathering the dusk after every census wedding?
   - A **feast** after every tier is laid out?
   - A **fair** every N days (7? 10?)?

   On those days, should the festival replace the ordinary dusk on the square?
4. **Q4, existing sickness.** CIVITAS today raises the **chance of death by up to +60 %** in a town with poor sanitation (F7, `pw_civ_people.js` dayStep). That is sickness and a chance-based harm, both on the drop list. Remove it, keeping sanitation only as a fixed mood term? Or keep it?
5. **Q5, rain.** Should quarrymen, woodcutters and builders **stop working in rain**? Real-day output then falls, and weather is chance. Or should they only take shelter while the day keeps its output? Fishermen keep fishing in rain either way.
6. **Q6, witnessed deeds.** Breaking a counter or station, or taking from a store chest, while villagers watch costs trust and starts a rumour, with amends paid through the clerk. **On from 1.3.228**, or built but switched off until the narrative phase?
7. **Q7, small coins.** Add a **silver penny** (1/12 of a gold coin; a new item and texture) so rations (36 p) and stallage (6 p) are paid exactly? Or keep gold only, with prices rounded to whole coins?
8. **Q8, gardens.** Leave a share of outer-street frontage empty on purpose (gardens: about 15 % on home streets, 30 % at the edge, only after a tier's charter is met)? Frontage is the measured growth bottleneck. Or use fillers (well, cart, lamp) only on stretches too short for a house?
9. **Q9, weathering.** Should **lived-in houses age visibly** (moss, cracked brick) after N days? Or only closed and abandoned buildings and demolitions?
10. **Q10, API upgrade.** Move BP-02 from `@minecraft/server` 2.3.0 to a newer version? That gives TickingAreaManager (2.6), LocatorBar waypoints (2.9) and text primitives / container events (2.10). It needs the Minecraft version on his PS5 (title screen) and a PS5 test.
11. **Q11, council gating.** Should the new town levers (the tax dial, build priority, naming districts) need a **council title** the player earns in town? Or stay free `/scriptevent` tools like today's commands?
