# CIVITAS 1.3.228 — BATCH B4 NOTES (2026-10-06)

**Scope:** People II. BF5 (personal shifts + a 7-day plan), PE5 (leave work in time, home too far), the RAIN ruling (quarrymen, woodcutters and builders shelter and keep half their output), PE1 (varied work beats and look-at spots), PE2 (the inn for the unhappy), BF7 (nearest free job / home; a move to another town when none is free).
**Source tree:** `/home/claude/tools/bp02_src_228/` only. `_build`, `_bds`, `tools/bp02_overlay_228`, the running gate and Drive were not touched.

**Status:** static checks, node tests and stub smoke runs only.
- `node --check` passes on every changed file.
- `js_dupcheck` is clean (rc 0) on the changed files and on all root scripts.
- All 14 node suites pass (1 of them new).
- Stub smoke runs (scratch copy, outside the tree):
  - the heartbeat ran 2,400 ticks with the CIVITAS modules loaded: 13 beats, 0 errors;
  - `goalFor`, `homeRoom`, `jobPosts`, `censusDay` (a household moving from T1 to T2), the inn goal and `produceDaily` in rain ran on a synthetic two-town state.

Nothing here has been verified on BDS or in game.

**His rulings applied:** RAIN = shelter + half output for the three trades. No random negatives: every rule below is deterministic (from the id, the seed and the world day).

---

## 1. Files

**Changed**
- `pw_civ_people.js`: the B4 block (pure law), `dayStep` (BF7), `whyOf` (2 codes).
- `pw_civ_clock.js`: places, shifts, the schedule, the inn, rain, moving town, the `shift` command, the gate lines.
- `pw_civ_work.js`: each hand's own shift; rain shelter.
- `pw_civ_shop.js`: the keeper's own shift; PE1 beats.
- `pw_civ_watch.js`: the watch and the sewer keeper follow their shift.

**New (test only)**
- `tests/test_shifts.mjs`: 86 checks.

**No new scripts.** No build script was edited. `NEW_SCRIPTS` stays `{pw_civ_beat.js, pw_civ_save.js}`; the test is globbed.

`pw_civ_economy.js` and `pw_weather.js` are unchanged. The rain reads the existing `weatherIn` (`pw_weather.js`), which the clock already imported.

---

## 2. Changes per function

### pw_civ_people.js (pure)

**The B4 block** sits above WHY-IDLE and holds every constant of the batch (§3).

| Function | What it does |
|---|---|
| `hourOf(tod)` | The hour 0..23 (tod 0 = 06:00, tod 18000 = midnight). |
| `shiftOffset(id)` | The start offset, −200..+200 ticks, from `hash32(id)`. Never stored. |
| `shiftTemplate(p, o)` | The template id. `p.shift` (the override) first, then by job (§3). |
| `restStart(p, seed, keeper)`, `dayOff(p, day, o)` | The 7-day plan. Consecutive days off; the first from the id + the town seed; keepers rest on the town's day (`seed % 7`). |
| `shiftAt(p, tod, day, o)` | `{slot W/M/I/R, tpl, hour, off, home, toRest}`. The offset is applied, a day off turns W into I, and PE5's walk home turns W/M/I into R `travel` ticks before the next rest block. |
| `onShift(p, tod, day, o)` | `slot === "W"`. |
| `travelTicks(a, b)` | `ceil(6 × hypot(dx, dz, 1.5·dy))`, capped at 3,000. |
| `homeWorkDist`, `homeFar` | Level distance; a complaint above 160 blocks. |
| `rainKeep(trade, wet)` | `1 − 0.5 × wet` for quarry / lumberyard / builders; 1 for every other trade. |
| `rainOutput(trade, carried, wet, abstract)` | A real day's carried output in rain: the dry hours' rate carried over the wet hours at half; if under 25 % of the day was dry, half the abstract rate over the wet hours. |
| `beatOf(pid, tick)` | PE1: the weighted beat of a 600-tick window, from a hash of (pid, window). |
| `lookCells(kind, blocks)` | PE1: the trade's look-at cells among a template's blocks (`dir` + `chests`), split into main and second. |
| `workSpot(beat, sp, salt)` | PE1: `{beat, stand, look}`. Never more than 4 blocks from the station (the store 6), on the same floor. A beat with nothing to do falls back to the main task. |
| `yawTo(from, to)` | The facing yaw (the fisherman's formula). |
| `wantsInn(p)`, `innStep(acc, dt, mood)` | PE2: mood < 40 seeks the inn; +1 per 1,200 ticks there; at most 400 ticks a step; never above 55. |
| `nearestFree(list, at, ok)` | BF7: the nearest item that passes `ok`. Unknown places come last; list order breaks ties. |
| `bedsOf(dir)` | BF7: beds of a template (two bed blocks = one bed). |
| `household(P, p, day)` | BF7: p, a spouse at the same home, the children living there. |
| `adopt(P, movers, day, home)` | BF7: the movers enter another town's census. New ids; names, sex, birth, trade and skill are kept; marriage and parent/child links are kept among the movers; mood is at least 45. |

**`dayStep` (BF7)**
- `ctx.homes[]` and `ctx.jobs[]` may carry `x, z` (the clock passes them). Without coordinates the old first-free order holds (`test_needs` 80/80 unchanged).
- **§2, grown children moving out of a crowded home:** they take the room nearest their work (it was the first room free).
- **§2, the homeless (a house bought for the core):** they take the room nearest their work.
- **§3, jobs:** a jobless person takes the vacancy **nearest his home** (it was the first listed).
- **§3c (new), a far home.** An adult whose home is more than 160 blocks from his work:
  - his household takes a free room within 80 blocks of the work, at most `MOVE.far` (1) household per town per day, in id order;
  - if no such room is free, he **complains**: a `far` event every 10 days (`(day + id) % 10`).
- **§5b (new), moving town.** A person moves when either holds:
  - no home for `MOVE.homeless` (3) days, and no room free here;
  - an adult with no job for `MOVE.jobless` (5) days, and no vacancy here.

  Then `ctx.elsewhere({people, job, why})` is asked for a town. The household leaves like any departure: `alive = false`, `left = day`, its room and job are freed, and a `left` event names the town. The movers are returned in `r.movers`. With no other town, nobody moves, and the existing unhappy-leave law still applies. At most `MOVE.perDay` (1) household per town per day.
- **§5, the faucet:** a newcomer takes the room (with ≥ 2 places) **nearest an open job**.
- **Return** adds `movers`, `far` and `farMoved`.

**`whyOf` and `WHY`**
- `HOME_FAR` is now emitted. It comes after the work module's own reason and before `WORKING`.
- New code `SHELTER`, before `WORKING`.

### pw_civ_clock.js

**Places and shifts (new section, after `homeRoom`)**

| Function | What it does |
|---|---|
| `homeRoom` | Each home now carries `x, y, z` (its door front) and `beds`. Capacity is unchanged (`HOUSEHOLD × DENSITY`); `PLACES.BEDS_BASE` is off. |
| `jobPosts` | Now a wrapper over the old body (`jobPostsBody`). It adds each post's place: a workplace's door front, or the square for the town posts. |
| `bedsOfFamily`, `placeOf`, `squarePlace`, `buildingById` | Helpers. `buildingById` is an index rebuilt when the list changes, or every 100 ticks. |
| `worldDay` | `world.getDay()`, in try. |
| `workPlaceOf` | The workplace's front, a fisherman's spot, or the square. |
| `travelOf` | PE5 ticks. Cached per person in memory and remade when the home or the job changes. |
| `jobKindOf`, `shiftOpts`, `shiftNow`, `homeFarOf` | Shift helpers. |

**Moving town (BF7, before `censusDay`)**

| Function | What it does |
|---|---|
| `placesOf` | Each town's rooms and posts, read once per census day (memory) and booked as households arrive. |
| `moveTarget` | The nearest other built town in the same dimension with a home that holds the household, plus an open post for a job-seeker. |
| `moveTownIn` | The room nearest an open post. `PEOPLE.adopt`, both towns' logs, an event, and a `[CIV-MOVE]` line. |

**`censusDay`**
- Passes `restOf`: a day off by the world day carries no fatigue (B3's hook).
- Passes `elsewhere` (`moveTarget`) and processes `r.movers`.
- `diagOf(st).moves` = `{day, out, far, farMoved}`.

**The schedule**
- `schedCtx` adds `wday`, `innSent` and `innCap` (`INN.perStation` × the inn's stations).
- **`goalFor`**
  - The slot is the person's own shift (`shiftNow`). A body with no census person keeps the old `SCHED`, which stays only for those bodies.
  - **W:** fisher, surveyor, shopper, builder / jobless site, then the job. The job goal is now **`workGoal`** (PE1: the beat's stand plus `g.look`).
  - **W + I:** the shopper at market hours.
  - **Rain, a builder with a site:** `kind = "shelter"`; the goal is home, with `shelterSite`.
  - **I:** leisure. Rain sends a person home unless he is going to the inn.
  - **M:** leisure. In rain: the inn for the unhappy, else home.
  - **R:** home.
  - `ctx.homeFar` is set for job holders on shift.
- **`leisureGoal`** calls `innGoal` first: the inn's inside-door cell for mood < 40 while the inn has room.
- **`workSpotsOf(b)`** (exported) builds and caches (memory) the station, the main and second look-at cells, the store and the door. The cells come from the template's `dir` + `chests`, rotated with `rotXZ`.
- **`scheduleJob`**
  - Samples the rain once per pass in the town's work hours (`wetLog`, memory).
  - The why phase is each person's own slot. `HOME_FAR` and `SHELTER` are fed in.
  - Site, fish and survey actions need the person's own W.
  - A sheltering builder adds 50 (`100 × RAIN.keep`) to his site per pass, also kept in `b.labor.rainDone`.
  - At the inn (within 3 blocks): `innStay`, mood +1 per 1,200 ticks.
  - On arrival, a body faces `g.look` (`setRotation`, in try).
  - `shiftDiag` runs per pass.
- New memory maps: `innAcc`, `wetLog` / `wetShareOf`, `shiftSeen` / `shiftDiag`.

**Rain and production**
- `produceDaily` (real day): quarry and lumberyard output = `rainOutput(kind, carried, wet, abstract × stations)`. The wet share is read and cleared. `diagOf(st).rain` is set.
- `advanceOnce`: the builders' crew share × `rainKeep("builders", wet)` on real days. Skipped days are unchanged.

**Module APIs**
- **`initWork`:** `onShift` (`bodyOnShift`), `wet` (`weatherIn`), `shelterOf` (`insideDoor`).
- **`initWatch`:** `onShift(p, st, tod)`.
- **`initShops`:** `onShift`, plus `workSpot(b, v, st, tick)`.
- `personOfBody` caches a body's pid by entity id, so there is no `getTags` per beat after the first.

**Commands and logs**
- New command `pw:clock shift [name] [template|default]`. It is in the header and the help line.
- Why icons: `SHELTER` "sheltering", `HOME_FAR` "home too far".
- The no-player status `census` gains `shift`, `inn`, `rain` and `moves`.

### pw_civ_work.js
- Each hand's duty is `API.onShift(v, st)`. Off duty, `state = "off"`: the tag goes, the claim goes, and the face is dropped (as before).
- The 200-tick sweep removes a `civ:working` tag when the hand has no record or his record is `off`. It no longer uses the town-wide hours.
- **Rain:** `state = "shelter"`. Claims and the face are released, the barrow stays loaded, and he walks to the workshop's inside-door cell and stands. When the rain stops he goes back to `idle`.
- `whyOf` returns `SHELTER`.

### pw_civ_shop.js
- A keeper's duty is `API.onShift(v, st, tod)`: the late template, the id's offset, and the town's rest day.
- **PE1.**
  - On duty the keeper stands at `API.workSpot(...)`'s stand and faces its look-at block.
  - A move inside the shop is one straight `WALK.sendPath` leg; slowness is removed first, because the anchor would hold him. From outside the shop, the old routed `WALK.send` is used.
  - `BEAT_SENDS` = 2 beat moves per shop beat.

### pw_civ_watch.js
- `duty = API.onShift(p, st, tod)`: the night template (19:00..05:00, i.e. the old `NIGHT` 13000..23000), the day template for the sewer keeper. The old constants remain the fallback.

---

## 3. Constants (all in `pw_civ_people.js`, the B4 block)

### `SHIFT.T` (W work, M meet, I idle, R rest; hour 0 = midnight, hour 6 = tod 0)

| Template | Who | Hours |
|---|---|---|
| standard | everyone else | `RRRRRRRWWWWWWWWWWMMRRRRR` — work 07..17 (= the old `SCHED`), meet 17..19 |
| early | fishers, farmers | `RRRRRRWWWWWWWWWWIMMRRRRR` — work 06..16 |
| late | keepers (not quarry / lumberyard), the inn's people | `RRRRRRRRIWWWWWWWWWWMRRRR` — work 09..19 |
| night | the watch | `WWWWWRRRRRRRRRRRRMMWWWWW` — work 19..05 (= the old `NIGHT`) |
| day | the sewer keeper | as standard (its own id, so a command can move him alone) |
| child | children | `RRRRRRRIIIIIIIIIIMMRRRRR` |

**Other shift constants**
- `SHIFT.off` (days off in 7): standard 1, early 1, late 1, night 2, day 1, child 0.
- `SHIFT.offset` 200.
- The week day is `world.getDay()`, so a day off is a whole game day at any clock speed.

### Other tables

| Table | Values |
|---|---|
| `COMMUTE` | `perBlock` 6, `climb` 1.5, `far` 160, `near` 80, `max` 3000 ticks, `sayEvery` 10 days |
| `RAIN` | `keep` 0.5; `trades` quarry, lumberyard, builders; `measureMin` 0.25 |
| `WORKBEAT` | `window` 600 ticks, `reach` 4; weights main 8, near 5, second 5, store 6, door 7 (Liberty's pool: primary 8 / near station 5 / secondary spot 5 / side tasks 6, 7) |
| `LOOK` | bakery (furnace, hearth \| barrels, shelves, chests); butcher (smoker, trestle); smithy (anvil, blast furnace \| grindstone, hearth); inn (barrel \| tables, hearth); town_hall (lectern \| chests, bell); lumberyard (stonecutter, trestle); quarry (chest \| barrel); farm (barrel); any (chest, barrel) |
| `INN` | `mood` 40, `per` 1200, `cap` 55, `perStation` 3, `stepMax` 400 |
| `MOVE` | `homeless` 3 days, `jobless` 5 days, `perDay` 1, `far` 1 |
| `PLACES.BEDS_BASE` | false |

---

## 4. Save cost

**Per person:** 0 bytes by default.
- Template, offset, rest days, travel, beats and inn time are all derived from the id, the job, the seed and the world day, or kept in memory.
- The only new saved person field is `p.shift` (a template id), written only by `pw:clock shift <name> <template>`. `test_shifts` checks that a full set of shift calls writes nothing to the census.

**Small saved additions**
- `b.labor.rainDone` (one number, while a site is under labour).
- The `far` events in `st.log` (cut to 60 lines at save).

**Memory only** (`spotsCache` is capped at 4,096 and `travelCache` at 8,192):
- `innAcc`, `wetLog`, `shiftSeen`, `travelCache`, `spotsCache`, `bodyPid`, `placesToday`, `bIdx`, `bedsCache`;
- `diagOf(st).shift / .inn / .rain / .moves`.

After a reload, the day's wet share and the inn time restart. Both are harmless: the wet share starts dry, and the inn time catches up at most 400 ticks.

---

## 5. BDS gate signals (B4)

**`[CIV-SHIFT]`** — one line per town per world day, after tod 13000: `{st, day, startBeats, starts: [[tod, sends] …], now: {W, M, I, R, off, leaving, far, inn, shelter}, wet, inn}`.
- **BF5 target:** `startBeats` ≥ 4. The schedule passes from tod 10000 to 13000 that start walks; before this batch it was 1–2.
- `off` ≈ 1/7 of the working people on a normal day. All keepers are off on the town's day.

**`[CIV-MOVE]`** — `{from, to, why, n, home, day}` when a household changes town. Expect it only when a town has no room or work and another town has.

**Status:** `pw:clock_stl` → `census.shift`, `inn` (mood points given), `rain` (`{day, wet}`), `moves` (`{out, far, farMoved}`).

**Why tally (`pw:clock why`)**
- `HOME_FAR` > 0 only in towns with homes more than 160 blocks from work; it should fall as rooms near work free up (`farMoved`).
- `SHELTER` > 0 only in rain.
- `RAIN` is the jobless and idle sent home.

**Rain** (`/weather rain` at tod ~3000, then clear at ~6000)
- Quarry and lumberyard hands walk to their workshop door and stand.
- `work.sample` states show `shelter`, and the hands return to work after the rain.
- That day's `L.sales` for the quarry: about 75 % of a dry day.
- Builders go home, and the sites still advance (`labor.rainDone` > 0).
- Fishers keep fishing.

**PE1**
- Keepers stand at varied spots within about 4 blocks of the station and face their oven, smoker, anvil or lectern.
- Shop beat < 20 ms (`[CIV-BEAT] sys.shop`); no `[CIV-SHOP] slow beat`.
- Station workers (household members at shops) spread over the beat spots instead of stacking on the station.

**PE2**
- Unhappy people (mood < 40) gather inside the inn at dusk and in idle hours (`now.inn`).
- The `inn` counter in status grows.
- `[CIV-MOOD]` `t30` / `t0` shrink in a town with an inn compared with one without.

**PE5**
- Far-housed workers leave earlier (`now.leaving` > 0 before tod 11000).
- `pw:clock shift <name>` shows `walk home N ticks` and `home too far`.

**BF7**
- New hires go to the nearest workplace: mean home↔work distance falls against 227.
- Newcomers take rooms near open jobs.

**Unchanged:** 0 `LEDGER DRIFT`; no `[CIV-CLOCK] census:` errors; `[CIV-BEAT]` errors 0 for shop, work, watch and schedule.

---

## 6. Open issues and readings to rule on

1. **Not verified on BDS or in game.** Static checks, node tests and stub smoke runs only.
2. **Keepers' rest day.** The matrix says "the town's market day for keepers"; CIVITAS has no market day, so keepers all rest on the town's day (`seed % 7`). **Every shop's keeper is off that day.** Their windows still open on a click, but the stations stand empty. If he wants the shops always attended, set keepers to id-based rest days: a one-line change in `restStart`.
3. **Beds are counted, not used.** `PLACES.BEDS_BASE` is off. Using beds as the base would change capacities: cottage_s 1 bed vs `HOUSEHOLD` 2, cottage_l 2 vs 3, inn 4 vs 1, manor 11 vs 4. `population()` (the ledger's) would also have to follow. This needs a ruling first.
4. **Distances are straight-line** (`hypot`), not manhattan as the matrix wrote. The 6-ticks-per-block walk uses the same length plus the climb.
5. **Leave-in-time** is "home when the rest block starts" (MineColonies). A near home only shortens the evening at the square; a home more than 2,000 ticks away (> 333 blocks) cuts into the work hours. Capped at 3,000 ticks.
6. **The rain output uses the dry hours' carried rate.** A day that was more than 75 % wet uses half the abstract rate over the wet hours.
   - The wet share is sampled once per schedule pass (about every 100 ticks) in the town's 1000–11000 window, not per hand.
   - Skipped (accelerated) days ignore rain.
7. **PE1 limits.**
   - The walk module ends a walk within 2.6 blocks (`REACH`), so spots closer than that to the station only change the facing.
   - The beat move inside a shop is a straight `sendPath` leg: no pathfinding inside the building, so a counter between the keeper and the spot may stop him (the walk module's stuck handling applies).
   - **Builders' door / corner alternation (matrix) is not done.** Corner cells may be in the foundation pit; the site credit logic is unchanged.
8. **Inn capacity** is counted in pass order, not "lowest moods first". The cap is 3 per station (inn_a: 5 stations → 15).
9. **Moving town** is limited to the same dimension and to built towns with a kit and a square. The arriving household has no job: it takes the nearest free one at that town's next census day. A move is booked against the destination's places for that census day only.
10. **The `far` complaint is a log line,** not a rumour kind. It is not added to the rumour kinds.
11. **The why phase is per person now.** A night watchman on his round counts as on duty; a standard worker on a day off counts as `OFF_SHIFT`.
12. **Build integration:** none. There are no new scripts.

---

## 7. Test results (source dir, `node tests/<file>`)

| Suite | Result |
|---|---|
| test_shifts (new) | 86/86 |
| test_beat | 91/91 |
| test_canopy | 5/5 |
| test_diet | 8/8 |
| test_fell | 31/31 |
| test_frontage | 12/12 |
| test_hygiene | 15/15 |
| test_lanes | 14/14 |
| test_market | 16/16 |
| test_needs | 80/80 |
| test_occupied | 97,680/97,680 |
| test_route | 468/468 |
| test_save | 40/40 |
| test_why | 33/33 |

**What `test_shifts` covers**
1. **Offsets:** stable per id; within −200..+200 and reaching both ends; mean ≈ 0; even over 8 bins (40,000 ids).
2. **Templates:**
   - all 24 hours of W/M/I/R;
   - `hourOf`;
   - the template by job;
   - the override, with an unknown id ignored;
   - standard = the old `SCHED` shifted by the offset;
   - the watch works only at night.
3. **The week:**
   - standard has one day off in 7; the watch has 2 consecutive; children none;
   - rest days spread over the week;
   - keepers all rest on the town's day;
   - a day off turns W into I.
4. **The walk home:**
   - 600 ticks per 100 level blocks; a climb counts ×1.5; the cap;
   - home by night (leaves the square at 12400 with a 600-tick walk);
   - a 2,500-tick walk ends the shift 500 ticks early;
   - the watch leaves to be home by 05:00;
   - `homeFar` at 160 / 161;
   - `HOME_FAR` in the why priority.
5. **Rain:**
   - half kept for quarry, lumberyard and builders, ¾ when half the day is wet;
   - 8 other trades lose nothing;
   - `rainOutput` math, including a steady 60-a-day quarry at 60 / 45 / 30;
   - the `SHELTER` code.
6. **Work beats:**
   - the weights;
   - 40,000 draws within 1 % of them;
   - a beat lasts its window and changes between windows;
   - look-at cells from the real bakery and smithy templates;
   - the spots for main, near, second (within 4, the far one never chosen), store and door, plus the fallbacks;
   - the yaw.
7. **Inn:**
   - +1 per 1,200 ticks, +3 per 3,600;
   - the 400-tick step cap and the cap at 55;
   - only mood < 40 seeks the inn;
   - a week of evenings gives about +11.
8. **Places:**
   - the nearest vacancy to home, not the first listed;
   - the homeless take the room nearest work;
   - a newcomer takes the room nearest an open job;
   - with no home free for 3 days, a household of 3 moves to the named town (departure, event, `movers`), and `adopt` keeps the marriage, the child, names and births;
   - with no other town they stay, and nobody moves before 3 days;
   - a free room here: taken, no move;
   - jobless 5 days with no vacancy: moves for work; with a vacancy: takes it;
   - a far household moves into the room near work, one per day, and the other one complains with the distance;
   - children never move alone;
   - beds per template; `BEDS_BASE` off;
   - a day off carries no fatigue (B3 hook).
9. **Save:** shifts, offsets, plans and beats write nothing to the census.

**Mutation checks** (scratch copies). Each of these mutants is caught by at least one failing test:
- the wrong night template;
- nearest → first;
- a changed weight;
- no leave-in-time;
- no day off;
- no offset.

**Other checks**
- `node --check`: `pw_civ_people.js`, `pw_civ_clock.js`, `pw_civ_work.js`, `pw_civ_shop.js`, `pw_civ_watch.js` and `tests/test_shifts.mjs` all pass.
- `js_dupcheck`: rc 0 on the changed files and on all root scripts. It caught a name clash (`moveIn`, an existing function) that `node --check` misses; the new one is `moveTownIn`.
