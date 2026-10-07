# CIVITAS 1.3.228 — BATCH B1 NOTES (2026-10-06)

**Scope:** BF1 (heartbeat, slots, budgets, shared bodies cache), the hygiene pass, TR4 (survey heights), EN4 (dynamic-property bytes).
**Source tree:** `/home/claude/tools/bp02_src_228/` only.

**Status:** static checks only.
- `node --check` passes on every changed file.
- `js_dupcheck` is clean.
- All 9 node suites pass.
- The real heartbeat ran 2,400 ticks on the engine stub, all modules loaded, 0 errors.

Nothing here has been verified on BDS or in game.

---

## 1. Files

**New**
- `pw_civ_beat.js`: the heartbeat module.
- `tests/test_beat.mjs`: 91 checks.
- `tests/test_hygiene.mjs`: 15 checks.

**Changed**
- `pw_civ_clock.js`
- `pw_civ_work.js`
- `pw_civ_watch.js`
- `pw_civ_shop.js`
- `pw_civ_walk.js`
- `pw_civ_keys.js`
- `pw_fell_rules.js`

**Build integration (do not skip).**
- The 227 build script asserts that every script already exists in the previous build (`assert ref.exists(), "new script …"`). The new file **`pw_civ_beat.js`** must be allowed as a new script and copied into `scripts/`.
- The tests are globbed (`tests/test_*.mjs`), so the two new suites run without any build change.
- `BASE-226.md5` was not touched.

### pw_civ_beat.js (new)

**Dispatcher core: `createBeat({clock, log, prof, plan})`.** It makes no engine calls, so the tests drive it with a fake clock. It provides:
- `register` and `unregister`;
- `step(t)`;
- `stats()`;
- `dueAt`, `systems`, `state`.

**Plan and timing**
- `PLAN` is the single slot table (§2).
- **Slots.** A beat runs at tick t when `t % max(every, 20)` is one of its slots. Single-slot beats get their repeats automatically: walk at slot 1 runs at 1 and 11.
- **Timing.** Every fn is timed into per-system ms, runs, max, over, skipped, shed and errors. The time is also added to `globalThis.__civProf[name]`, so the old `prof()` totals keep their names.
- **Errors.** Each fn runs in its own try/catch. Errors are counted, and the first 3 plus every 100th are logged.

**Over-budget skip.** A fn that takes more than 2 × `budgetMs` skips its next turn, and the skip is counted. A budget of 0 means it is never skipped (save, schedule start, walktest).

**Load shedding**
- MSPT is measured as the `Date.now` delta between dispatches, averaged over a 20-tick window.
- When the mean is above 70 ms, the `optional` beats are shed and the kit queue runs only every other turn (`halveOnShed`).
- When the mean falls to 60 ms or below, everything returns.

**Logging and status**
- `[CIV-BEAT] {t, ticks, mspt, worstDt, worstMs, worstAt, shed, shedOn, shedTicks, sys:{name:[ms,runs,max,over,skipped,shed,errors]}}` is written every 1,200 ticks, and then the counters reset.
- The exports `CORE`, `register`, `unregister` and `stats` sit on top of one `system.runInterval(…, 1)`.

**Bodies cache**
- `bodiesFrom(fn)` registers the `bodies` beat: one `getEntities({tags:[civ:settlement:<id>], type: villager_v2})` per settlement, every 20 ticks.
- `bodiesOf(st)` returns the cached list filtered to `isValid`, because `hasTag` on a gone entity would throw. The first ask for a settlement reads at once.

### pw_civ_clock.js

**Imports**
- `HB` (`pw_civ_beat.js`).
- `hasNaturalCanopy` from `pw_fell_rules.js`.
- The unused `prof` helper was removed. `PROF` stays because the schedule job's lap uses it.

**Guarded helpers**
- `blockAt`, `topAt` and `groundAt` are now exported.
- `blockAt(dim,x,y,z, loaded=false)`: with `loaded` set, it skips the `isChunkLoaded` ask when the caller found the column loaded in the same tick. The read itself stays in try.
- `groundAt(dim,x,z, t0=null)` accepts a top block the caller has already read. Its walk-down uses `loaded=true`, so each step costs one engine call instead of two.
- New `boxLoaded(dim,x0,z0,x1,z1)`: asks `isChunkLoaded` once for every chunk of a box.

**Saving and EN4**
- `save()` only marks the state dirty unless it is forced; the `save` beat writes. `save(true)` still writes at once.
- `saveNow()` calls the new `dpCheck()` once per write (EN4), using `DP_CEILING` and `dpMark` (§5).

**Loops moved onto the heartbeat** (each `system.runInterval` became an `HB.register`):
- `save`, `flush`, `clock`, `kitqueue`, `room`, `schedule`;
- the walk instrument: `walkTest` now does `HB.register("walktest")` / `HB.unregister`, where it used `system.runInterval` / `clearRun` before.

**Bodies cache**
- `HB.bodiesFrom(() => load().settlements)`.
- Readers: the `hands` callback of `initWork` and `scheduleJob`'s `vs`.

**Guarded readers passed to the modules**
- `initWalk` gets `blockAt`.
- `initWork` gets `blockAt`, `topAt` and the new exported wrapper `naturalCanopy(dim, logs, need)`. The wrapper calls `hasNaturalCanopy` with a `blockAt` reader and is ready for B2's `treeOk`.
- `initKeys`, `initWatch` and `initShops` get `blockAt`.

**Fishery: the cap with a follow-up**
- `FISH_CALL` = 40, with the memory maps `fishOwed` and `fishBusy`.
- `fisheryDay` replaces the direct call in `stepSettlementBody`. `fisheryCall` runs one capped call, and the `fishery` beat continues the day's debt.
- `fishBusyOf` makes the occupancy test lazy and builds it once per settlement and day.
- `surveyFishery(s, st, cap)` reads at most `cap` columns and returns how many it read.
- `waterColumn` now returns `undefined` for a sleeping column, so `fy.asleep` is still counted, and `null` for a dry one.

**TR4:** `surveyJob` (§4).

**Guarded reads (hygiene).** These functions were converted to `blockAt` / `topAt` / `boxLoaded`; the list is in §3.

**Status and commands**
- The player `status` view has a new line: engine throws · dynamic-property bytes · state chars · heartbeat MSPT · SHEDDING · worst beat tick.
- The no-player `status` (`pw:clock_stl`) adds `engineThrows` and `dpBytes`.
- `statesize` adds `dpBytes` and `dpCeiling` to the `[CIV-STATESIZE]` line and to the reply.
- New commands: `dpceiling <MB>` (0 = the 4 MB default) and `beat` (writes the current window as `[CIV-BEAT]`). Both are listed in the header.

### Other modules

**pw_civ_work.js**
- The `work` beat moved to `HB.register("work")`, and the `prof` wrapper was removed.
- The 200-tick sweep of stale `civ:working` tags now reads `HB.bodiesOf`.
- Every block read goes through `API.blockAt`: `nextQuarryFace`, `standBeside`, `regreen` (both loops), `nextTree`, `plantSpot`, `treeLogs`, and in `workBeat` the strike, the sapling, the replant and the deposit chest.
- Mapping to the old flow: `null` (the chunk sleeps) takes the old `catch` path (`return undefined` / `break` / retry the cell tomorrow); `undefined` (outside the world) takes the old `!blk` path.

**pw_civ_watch.js**
- The beat moved to `HB.register("watch")`.
- `postHolders(st)` reads `HB.bodiesOf`, where it ran a query every 10 ticks.
- The 200-tick sweep of stale `civ:watching` tags reads the cache, where it ran a whole-dimension query per settlement.
- `cover()` reads through `API.blockAt`.

**pw_civ_shop.js**
- The beat moved to `HB.register("shop")`.
- The duplicate-keeper check reads each settlement's bodies (`hasTag("civ:keeper")`). The whole-overworld keeper query runs only while a shop *outside* any settlement (the `plot` tool) has a keeper. The keepers it then sends away are only those without a `civ:settlement` tag.
- The two hire probes and the market clerk's probe go through `API.blockAt`.

**pw_civ_walk.js**
- The beat moved to `HB.register("walk")`.
- The stuck walker's feet read goes through `API.blockAt`.

**pw_civ_keys.js**
- The auto-close loop moved to `HB.register("keys")`.
- The cover read goes through `API.blockAt`. A sleeping cover cell now waits and is tried again. Before, it was forgotten when `getBlock` returned undefined instead of throwing; the comment already said "try later".

**pw_fell_rules.js**
- `hasNaturalCanopy(dim, logs, need, read = null)`. With `read`, every cell goes through it; the town passes `blockAt` through `naturalCanopy`. Without it (main.js player felling, one event per break) the old read in try is unchanged.

---

## 2. Final slot table

Slot = tick % 20, or tick % every for beats slower than 20 ticks.

| Beat | Every | Slot(s) | Budget ms | Flags | Before |
|---|---|---|---|---|---|
| clock (day advance) | 40 | 0 | 150 | heavy | its own 40 |
| kitqueue | 2 | 2,4,6,8,12,14,16,18 | 40 | heavy, halves on shed | its own 2 (10 per 20, now 8) |
| bodies cache | 20 | 10 | 10 | heavy | new |
| walk | 10 | 1, 11 | 15 | — | its own 10 |
| work | 10 | 3, 13 | 40 | heavy | its own 10 |
| watch | 10 | 5, 15 | 15 | — | its own 10 |
| fishery follow-up | 20 | 5 | 40 | heavy, optional | new (the 40-column cap) |
| flush | 10 | 7, 17 | 200 (= `FLUSH_MS`) | heavy | its own 5 |
| shop | 100 | 9 | 20 | heavy, optional | its own 100 |
| room | 20 | 17 | 20 | optional | its own 5 (gated 100 / 10 inside) |
| keys | 40 | 17 | 5 | optional | its own 40 |
| walktest (harness) | 20 | 13 | 0 | — | its own 20 (only while a test runs) |
| schedule (job start) | 100 | 19 | 0 | — | its own 100 |
| save check | 20 | 19 | 0 | heavy | its own 20 (writes at most every `SAVE_EVERY` 600) |

How the heavy beats are kept apart:
- **Even ticks:** clock, bodies, kitqueue.
- **Odd ticks:** work, flush, shop, fishery, save.
- No two heavy beats share a tick. `test_beat` checks this over 2,000 ticks, and a mutant plan with the fishery moved onto work's slot is caught (100 clashes).

**Differences from the matrix plan, and why**
- **New beat:** the fishery follow-up. The matrix asked for a 40-column cap; the follow-up keeps the day's 160 columns.
- **room:** moved to 17 of 20, off the heavy flush tick at 7. The accelerated room pace becomes 20 ticks instead of 10. The normal pace stays 100 (its own gate).
- **flush budget:** 200 ms. This is its existing `FLUSH_MS`. A 40 ms budget would make every long placement skip the next flush.
- **save:** the matrix's "600" is the write gate (`SAVE_EVERY`). The check itself runs every 20 ticks, as before.
- **kitqueue:** 8 turns per 20 ticks (was 10). `LAG_EVERY` and `t − lastMainTick ≥ 2` still hold, because the clock is on slot 0.
- **Gallery picture sweep** inside the clock beat (`tick % 100 === 0`): it now fires every 200 ticks, because slot 0 of 40 meets %100 only at %200. Before, it depended on the interval's start tick.

---

## 3. Read-site table

The sites were found by grepping every `getBlock(`, `getTopmostBlock(`, `getBlocks(` and `getBlockPermutation(` call in `pw_civ_*.js` and `pw_fell_rules.js`.

### Hot path, guarded

These now read through `blockAt` / `topAt` / `boxLoaded`, or through `naturalCanopy` / `present` built on them.

**pw_civ_clock.js, repeated or retried:**

| Function | Why it is hot |
|---|---|
| clock beat gallery sweep | every 200 ticks |
| `placeStage` | footprint probe, retried every flush while asleep |
| `stockCounters` | daily |
| `buyAt` | per purchase, in the schedule job |
| `takeFromStores` | per stage, on real days |
| `waterColumn`, `surveyFishery` | daily, plus the follow-up beat |
| `palaceSite` | daily survey until a site is found |
| `palaceWallJob` (`surfaceAt` + the wall), `palaceLandJob`, `palaceDrainJob` | jobs; pump passes daily |
| `processKitQueueBody` | awake probes for outfall2/sealout, gallery, ring wall, road, street; retried every kit beat while asleep, plus the op bodies |
| `layPark` | corner probe retried every kit beat, plus the body |
| `digQuarry`, `clearForest`, `harvestFarm`, `hardenStreets`, `regreen` | daily, and on carried days |
| `treeCells` (template `present`), `fellTree` | every felling: work beat and daily |
| `floodWatch` | daily |
| `kitDrain`, `plotDrain` | thousands of cells per op |
| `leafSweepJob`, `sweepChunk`, `canopyJob` | `getBlocks` behind `boxLoaded`; per-cell reads through `blockAt` |
| `startRoadJob` | the A* ground callback, thousands of cells |
| `noticeBoard` | daily |
| `surveyJob` | TR4 |
| `blockId` | walk instrument |
| `readSiteJob`, `liveSite`, `canopyOf`, `groundAt` | already guarded in 227 |

**Other modules:**
- **pw_civ_work.js:** `nextQuarryFace`, `standBeside`, `regreen`, `nextTree`, `plantSpot`, `treeLogs`, and `workBeat` (strike, sapling, replant, deposit).
- **pw_civ_watch.js:** `cover`.
- **pw_civ_shop.js:** the shop beat's hire probes (2), and `marketBeat`'s clerk probe.
- **pw_civ_walk.js:**
  - The beat's stuck feet read is guarded.
  - `localPath`'s `id()` and `standY` were already guarded in 227.
  - `localPath`'s `half()` permutation read only happens after `id()` found the same cell loaded and valid in the same synchronous call. It is left as it was.
- **pw_civ_keys.js:** the auto-close beat.
- **pw_fell_rules.js:**
  - `hasNaturalCanopy` uses the `read` parameter in the town's calls.
  - `templateFallingSet` uses the `present` option in the town's `treeCells`.

### One-off event or op: OK, left as a raw read in try

These run once per event, placement, command or kit op, after an awake probe.

**pw_civ_clock.js:**

| Function(s) | When it runs |
|---|---|
| `fixDirections` | once per stage placed |
| `stepBerm`, `terrace`, `yardPass`, `stoop`, `clearOver`, `layStreet`, `kitLandPrep` | plot preparation at placement, after `placeStage`'s footprint probe |
| `applyShopMark` | close / reopen, once |
| `clearTreesOver`, `supportUnder` | street, park and wall prep ops |
| `greenCorridor`, `layPlannedStreet`, `paveSquare` | founding and legacy streets |
| `kitPrep`, `carveManhole`, `kitSewerLamps`, `sealWater`, `kitBridge`, `kitCarveOutfall`, `grate`, `kitCarveTrunk`, `kitSealTrunk`, `drainExitOpBody`, `kitWaterTrench`, `kitCarveWellDrain`, `layLaneGallery`, `levelColumn`, `wallColumn`, `carveBranch`, `layRoadOp`, `layWallOp` | kit ops: each runs once, after the queue's awake probe |
| `placeStone`, `liftStone` | one boundary stone per surveyor act |
| `sewerReach` | the `sewers` command |
| `buildWall`, `buildDocks` | tier marks, once |
| `marketStand` | ladder event, once |
| `fellTree_old_unused` | dead code |

**Other modules:**
- **pw_civ_shop.js:** `buildStall`, once at the clerk's hire.
- **pw_civ_keys.js:** `slide` (a `runTimeout` chain per cover move) and `playerInteractWithBlock` (event).
- **pw_civ_coin.js:** `playerInteractWithBlock` (event) and `census` (command / UI).
- **pw_fell_rules.js:**
  - `fellVerdict`, `placeLyingLog`, `dropAttachedBlocks`, `placeStumps` and `crownLean` (`getBlocks`) all run on the player-felling event (main.js and fall physics).
  - `templateCells` reads a structure (`structure.getBlockPermutation`), not the world.
  - `templateFallingSet`'s default reader is used only on the main.js event path.

**Caveat on the one-off kit ops.** A kit op's awake probe checks 2–4 cells. If part of the op's area still sleeps, its raw reads throw once per cell: a burst, not a loop. `ENGINE.throws` counts only the guarded helpers' throws, so these never show in the counter. The server memory sampler is the only witness for them. If the gate's RSS climbs during kit work while the counter stays flat, these are the next candidates.

---

## 4. TR4: survey heights skip vegetation

`surveyJob` now does the following for each column:
1. `topAt`. A sleeping column gives `asleep++`, with no read and no throw.
2. `groundAt(dim, x, z, top)`: the walk down past leaves, logs and plants, reusing the top block.
3. `H` is the ground. `WET` is still decided from the topmost solid plus the cell above it, unchanged.

It now yields every 50 columns (was 100), because a forest column walks about 10–25 cells.

---

## 5. EN4: dynamic-property bytes

**When it runs.** `dpCheck()` runs after every save write: once per save, never in a loop. It calls `world.getDynamicPropertyTotalByteCount()` in try.
- If the method is missing, one `[CIV-DP] … unavailable` line is written and the check switches off.
- **The matrix said "verify" for the method, and this is still open.** Watch for that line.

**What it keeps.**
- `state.dpBytes` is saved: one number.
- `state.dpCeiling` is saved only when set with `dpceiling`.

**What it prints.**
- **On load and on every tier change** of any settlement: `[CIV-DP] {tiers, bytes, stateChars, buildings, tick}`. This is the per-tier number for the probe to collect from the content log.
- **Growth warning:** "+25 % per tier" is read as follows. The bytes at the current tier set are the base. A warning is written when they grow 25 % above it, and the next warning waits for another +25 %.
- **Ceiling warning:** above the ceiling (default 4 MB, or `dpceiling <MB>`), at most once per 6,000 ticks.
- **Where it shows:** `status` (player line and no-player event) and `statesize`.

---

## 6. Could not do, and open issues

1. **Not verified on BDS.** Everything above is static, plus node tests on the stub.
2. **`getDynamicPropertyTotalByteCount` on `World` in 2.3.0** is assumed, not verified. If it is missing, the code degrades to one warning line.
3. **Fishery debt is memory only.** After a reload, that day reads only the first 40 columns. `fishBusy` (plots and roads near the shore) is cached once per day, so a plot added between the day's 4 calls is seen the next day.
4. **The walk module's orphan sweep** (`pw:lead` plus civ villagers over the whole overworld, every 200 ticks) stays a query. Leads are not villagers. The first sweep after a load must also reach villagers without a settlement tag.
5. **Main.js add-on loops** (Kakapo, deer, flutter, homestead, vine …) remain separate intervals, as the matrix intends (outside 228).
6. **Bodies are up to 20 ticks old.** A villager spawned since the last read joins the readers at the next slot 10. Readers see only valid bodies.
7. **Shedding uses the 20-tick window mean** (shed above 70, restore at or below 60), not "20 consecutive ticks above 70". A single fast catch-up tick would otherwise reset the count.
8. **Keys auto-close:** a sleeping cover now waits. Before, it could be forgotten (§1).
9. **The raw one-off sites in §3 are not counted** by `ENGINE.throws`.

---

## 7. BDS gate: signals to check (B1)

**[CIV-BEAT] every 1,200 ticks**
- `errors` = 0 for every system.
- Expected `runs` in a full window, when nothing is skipped or shed:

| Beat | Runs |
|---|---|
| walk, work, watch, flush | 120 each |
| kitqueue | 480 |
| clock, keys | 30 each |
| bodies, room, fishery, save | 60 each |
| shop, schedule | 12 each |

- `worstDt` (the server tick gap): < 1,000 ms from village to M III, target ≤ 250 ms in normal play.
- `worstMs` (the CIVITAS share of the worst tick).
- `over` / `skipped` per system, with the ms totals per system per window. This is the B1 cost table.
- `shedOn` / `shedTicks` should be 0 in normal play.

**Engine throws and memory**
- The `status` line `engine throws …` stays flat across the climb, during the fishery, the survey and kit work.
- Run the RSS sampler too, because one-off raw sites are not counted (§6.9).
- No Hang, no watchdog, no memory warning.

**Dynamic properties**
- One `[CIV-DP]` line per tier change, with bytes per tier.
- No `unavailable` line.
- No ceiling warning below the expected size.

**Fishery and survey**
- No `[CIV-CLOCK] slow: fishery` lines.
- Fishing spots are still found in a town by water (`status` → `fishers`, `st.fishery.spots`).
- `[CIV-SURVEY]`: the same area over forest and over cleared land gives similar relief; engine throws do not move during the survey.

**Behaviour unchanged**
- Keepers: still one per shop (no doubles), the clerk is hired.
- Watch: `rounds` grows at night.
- Work: `workTotal` grows, and quarry and lumberyard deposit.
- Schedule: `walkArrived` grows, builders work sites.
- Saves: about one per 30 s while dirty (the `[CIV-DP]` cadence and the DP bytes move).

**Profiler**
- `status` → `prof` keeps the same keys: `clock`, `kitqueue`, `room`, `shop`, `walk`, `watch`, `work`, `schedule`.
- New keys: `save`, `flush`, `bodies`, `keys`, `fishery`, `walktest`.

---

## 8. Test results (source dir, `node tests/<file>`)

| Suite | Result |
|---|---|
| test_beat (new) | 91/91 |
| test_hygiene (new) | 15/15 |
| test_canopy | 5/5 |
| test_diet | 8/8 |
| test_frontage | 12/12 |
| test_lanes | 14/14 |
| test_market | 16/16 |
| test_occupied | 97,680/97,680 |
| test_route | 468/468 |

**Other checks**
- `node --check`: all changed files pass.
- `js_dupcheck`: rc 0 on all 8 changed scripts.
- Stub smoke: all modules loaded, `CORE.step` for 2,400 ticks, 13 beats registered, 0 errors. This is a scratch run, not shipped.
