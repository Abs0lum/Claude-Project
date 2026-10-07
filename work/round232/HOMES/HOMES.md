# HOMES — BP-02 1.3.232 worker report: #29 home sizes for a family of 4, #28 crossroads + wooded city parks

Worker TAG `HOMES`, 2026-10-07 (19:37–20:20 UTC). Base: `work/inbox-2026-10-07-1714/bp02-231-src` (round 231, 33 suites green).
Workspace `scratchpad/w232-HOMES`. Diff: `out232/HOMES.diff` (5 files). Generator proposal: `out232/HOMES-tools-civgen.diff`,
`out232/HOMES-tools-civ_roster.diff`. Evidence: `out232/HOMES-files/`. Full test run: §6 (35/35 suites, `node --check` clean).

## 0. Bottom line

- **#29 home sizes.** The starter cottages are short of **beds**. They are not short of places.
  - `cottage_s` and `cottage_m` have **1 bed**. `cottage_l` has **2 beds**.
  - By his own sleeping law (the palace: "a double bed sleeps two", "the children's bed sleeps two"), only `cottage_l` sleeps
    a family of 4.
  - Births still fill a 1-bed cottage up to 4 people, and no rule ever moved a family on.
  - **Script change (done, tested):** the census has a new FAMILY ROOM rule. A family whose beds cannot sleep it moves to a
    free home that can. If there is none, it swaps homes with a smaller household that lives in such a home.
  - Simulation, 8 towns: the share of family-of-4 days spent in beds that fit rose from **18.8 % to 38.4 %** on average.
  - **The rest needs structures (design only, stopped there):** one children's bed in the loft of `cottage_s` and
    `cottage_m`. The footprint does not change, so street frontage and the 8-part ramps are not affected.
  - With that bed, the simulated share reaches **77–88 %**. Exact cells are given; the generator diffs were checked in memory.
- **#28 crossroads.** Done and tested. The side-street search used to open every +1 street of a street before any -1 street,
  so a crossroads only happened by chance. Now a window that completes a crossroads comes first. This applies inside each base
  street, with the main street still first. Block closing works the same way.
- **#28 wooded city park.** Design note and questions only. It needs land work and laying code that only a BDS gate can check,
  and his word "leave" can be read two ways (§4.3).

---

## 1. #29 — what I measured

### 1.1 The starter homes (shipped round-231 table `pw_civ_buildings.js`, checked in `tests/test_homes.mjs` §0)
| kind | size (x deep × y × z front) | beds (two bed blocks = 1) | places = HOUSEHOLD × DENSITY (village / town / city / metro / capital) | founders (moveIn) | sleeps (2 to a bed) |
|---|---|---|---|---|---|
| cottage_s (a–d) | 8 × 24 × 7 | **1** (loft) | 2 / 3 / 6 / 12 / 20 | 2 | 2 |
| cottage_m (a–d) | 8 × 26 × 9 | **1** (ground alcove) | 2 / 3 / 6 / 12 / 20 | 2 | 2 |
| cottage_l (a–d) | 10 × 25 × 12 | **2** (chamber + loft) | 3 / 5 / 9 / 18 / 30 | 3 | **4** |
| farm_wheat / terrace | 16–21 × 24 × 10 | 1 | 1 / 2 / 3 / 6 / 10 | 1 | 2 |
| farm_cattle | 16 × 26 × 9 | **0** | 1 / 2 / 3 / 6 / 10 | 1 | 0 |
| manor | 20 × 37 × 22 | 11 | 4 / 6 / 12 / 24 / 40 | 4 | 22 |
| inn (r1, 231) | 17 × 34 × 13 | 32 (guest beds) | 1 / 2 / 3 / 6 / 10 | 1 | — |

- Sources:
  - `HOUSEHOLD` is at `pw_civ_clock.js:147` and `DENSITY = [1, 1.5, 3, 6, 10]` at `:120`.
  - Places are computed in `homeRoom` (`:893–901`). Founders come from `moveIn` → `censusMoveIn` (`:719`, `:1124`).
- Plans of the loft and ground floor (built in memory by the repo's own generators): `HOMES-files/COTTAGE-PLANS-before-after.txt`.
- His sleeping law is `COURT.sleepers = 2` (`pw_civ_court.js:24`, "a double bed sleeps 2"; his 17:52 "the children's bed
  sleeps two"). The new rule uses `FAMILY.perBed = 2`, and the test asserts that it equals `COURT.sleepers`.

### 1.2 Mechanism (base file:line)
- **Births fill a home past its places.**
  - `dayStep` births (`pw_civ_people.js:577–611`) allow a child while `room > 0` or `over < DIALS.crowd (2)`.
  - At most `BIRTH.kidsPerHome = 2` children are allowed per home.
  - So a couple in a 2-place, 1-bed cottage becomes a **family of 4: two places over, and twice what its one bed sleeps**.
- **Nothing moved a family that had outgrown its home.** The only moves were:
  - the grown child at 25 (`:613–653`);
  - homeless people taking the nearest room (`:654–662`);
  - too far from work (`:680–702`), which moves `household()`, i.e. children only (§5 finding);
  - the heir's better house (`houseAfterDeath`).
- **Beds were counted but never used.** `PLACES.BEDS_BASE = false` (`:1246`; B4-NOTES: "needs a ruling first").

### 1.3 The household-size distribution (real `dayStep`, simulated town)
- **Method.** `HOMES-files/homes_sim_seeds.mjs`, and the same logic in `tests/test_homes.mjs` §7.
  - The founding village, then `TIER_ADDS` dwellings at `TIER_DAYS`, 2 furnished per day.
  - Places come from `HOUSEHOLD × DENSITY`; founders follow `censusMoveIn`; everyone can find work.
  - 260 days, which reaches city I.
- **Base results:**
  - 70–74 % of home-days have more residents than beds.
  - Families of 4+ spend **13–31 % (mean 18.8 %)** of their days in a home whose beds sleep them.
- An earlier variant over 300 days and 5 seeds: 81–95 % of family-of-4 days were short of beds, and 40–62 % were over places.

## 2. #29 — the script change (done)

### 2.1 FAMILY ROOM (`pw_civ_people.js`, block at `:1408–1555`; hook `:654–656`; result `:928`)
- **Who moves: a family.** That is a parent, the spouse living at the same home, and their *dependants*.
  - Dependants are the children at home who are under `DIALS.moveOutAge` (25) and unmarried (`familyOf`, `:1433`).
  - A married child is a separate household. A grown child moves out under the existing rule.
- **When it moves:** when its home's beds cannot sleep the family itself, i.e. `beds × 2 < size` (`sleeps`, `:1446`).
  - A lodger never sets a family moving.
  - Unknown beds never trigger the rule, so old callers and old tests are unchanged.
- **Where it moves.** The classes are tried in this order; nearest work is used only inside the last class:
  1. **A free home whose beds sleep the family together with whoever already lives there.**
     - The rule keeps the move-out law's order: the best level the family can afford (`affordLevel`), then an empty house
       before a shared one, then nearest work.
     - Deeds follow HD: the family buys the new home, and sells the old one if it is left empty.
     - Both homes are queued for restoration (his 21:47 law).
  2. **An exchange.** The family swaps homes with a smaller household that lives alone in a home whose beds sleep the family.
     All of these must hold:
     - the family also lives alone;
     - the family's old beds sleep that household;
     - each home's places hold its newcomers;
     - the family can afford the level.
     - Order: a household that cannot grow first (no married woman of fertile age), then the smallest, then nearest the
       family's work, then by id.
     - No deeds, because both pay from the one purse (ASSUMPTION). Both homes are restored.
- **Guards:**
  - Never the inn's guest beds (`FAMILY.guestBeds = ["inn"]`; the clock now passes each home's `kind`).
  - Never a home more than `COMMUTE.far` (160 blocks) from the work of anyone who moves. Otherwise the far-from-work rule would
    send them straight back.
  - The town's ranks at work never fall (`SKILL.gate` by house level).
    - A move must keep the family's sum of ranks.
    - An exchange must keep the sum over both households, so a master leaves his level-2 house only for a family whose own
      master it frees.
    - A strict "nobody's rank falls" version blocked almost every exchange in the sim: everyone there is a master builder
      after 60 days.
  - At most `FAMILY.perDay = 2` families per town per day. The most short of beds go first, then the larger family, then by id.
  - Kill switch: `FAMILY.on`.
- **Result:** `dayStep` now returns `family: { moved, swapped }`.

### 2.2 Clock (`pw_civ_clock.js`)
- `homeRoom` (`:895–904`): each home now also carries `kind: short(b)`. This is memory only; the save is unchanged.
- `censusDay` (`:1295`): `diagOf(st).family = { day, moved, swapped }`. Memory only.
- **New command** `/scriptevent pw:clock homes` (`:8196–8210`; header `:59–60`). For the town you stand in, it prints:
  - each dwelling kind: count, beds, places and people;
  - families by size, how many sleep in their own beds and how many are short (of 4 or more: sleep / short);
  - the last day's family moves and exchanges.
  - It also writes a `[CIV-HOMES]` line to the content log.

### 2.3 Tests (`tests/test_homes.mjs`, new, 57 checks)
- **Measure (§0):**
  - beds for every skin;
  - places read from the clock source;
  - `FAMILY.perBed === COURT.sleepers`;
  - only `cottage_l` sleeps 4.
- **familyOf** — included: an apprentice, and an unmarried son of 22. Excluded: a married daughter and her husband, a
  30-year-old son, a child living elsewhere, and a widow alone.
- **sleeps** — the inn is excluded; homes with no beds or unknown beds sleep nobody.
- **Move:**
  - the whole family moves; the event names it;
  - buy and sell deeds, the money is conserved, restorations are queued;
  - places and over-counts follow the move.
  - Class order: sleeping before nearest; best level, then empty before shared, then nearest.
  - Afford, far, inn, per-day order, no-family, lodger-doesn't-trigger, nobody-split.
- **Exchange:**
  - plain case; no deeds; places follow;
  - a free home is preferred over an exchange;
  - a partner that cannot grow is preferred over a nearer young couple.
  - 8 guards: partner smaller; the family's old beds sleep the partner; the family lives alone; places on both sides; beds;
    not the inn; afford; ranks at work (blocked when the family has no master; allowed 1+2 → 2+1).
- Kill switch; old callers (no beds) unchanged.
- **Clock:**
  - `homeRoom` cut from the source and run on stand-ins: it carries `kind` and `beds`, and a shop is not a home;
  - the `homes` command exists;
  - `familyCensus` counts correctly.
- **Simulation (§7), 4 seeds to city I:** the share **15.7 % → 44.4 %**. Population within ±8 % per seed (actual: −2 to +1 %).

### 2.4 The simulation in full (8 seeds, 260 days; `HOMES-files/homes_sim_seeds.mjs`)
| seed | rule off: family-of-4+ days in beds that sleep them | rule on | moves / exchanges | population off → on |
|---|---|---|---|---|
| 3 | 51 / 391 (13.0 %) | 247 / 486 (50.8 %) | 5 / 25 | 180 → 177 |
| 7 | 94 / 533 (17.6 %) | 200 / 468 (42.7 %) | 2 / 17 | 184 → 185 |
| 11 | 95 / 612 (15.5 %) | 166 / 600 (27.7 %) | 5 / 24 | 197 → 196 |
| 23 | 78 / 499 (15.6 %) | 220 / 492 (44.7 %) | 4 / 17 | 187 → 188 |
| 31 | 114 / 549 (20.8 %) | 228 / 608 (37.5 %) | 5 / 22 | 197 → 197 |
| 47 | 126 / 610 (20.7 %) | 231 / 613 (37.7 %) | 6 / 21 | 202 → 206 |
| 59 | 93 / 585 (15.9 %) | 233 / 582 (40.0 %) | 1 / 24 | 174 → 175 |
| 71 | 164 / 529 (31.0 %) | 128 / 485 (26.4 %) | 1 / 23 | 186 → 187 |

- Seed 71 is lower with the rule on. The rule itself never leaves anyone short at the moment it moves them: both households
  sleep in their beds after a move or an exchange.
  - The difference comes from the run diverging. Once one family moves, the people who meet differ, so the marriages and
    births differ.
  - Its rule-off run also started unusually high (31 %).
  - The test therefore asserts on the **sum** of 4 seeds, not on any single seed.
- Churn is about 1 move or exchange every 10–15 days per town. Each one queues 2 restorations (HD law).
- **Variants tried and rejected:**
  - `HOUSEHOLD.cottage_l` 3 → 4: no gain, because the large cottage is filled by founders.
  - A places-only fallback: more churn, and no beds gained.
  - The strict rank guard: it blocked almost every exchange.

## 3. #29 — the structure part (DESIGN ONLY: generated in the cloud workspace)

### 3.1 What exactly: one CHILDREN'S BED in the loft of `cottage_s` and `cottage_m`
The footprint stays the same, so frontage, slots and the 8-part ramp planning are untouched. `cottage_l` already has 2 beds
and is unchanged. Local coordinates follow civgen's convention: x = depth from the street (0 = front wall), z = frontage,
feet 0 = ground floor.

| family | new bed blocks (feet 4 = the loft) | direction | why there |
|---|---|---|---|
| `cottage_s` (`civgen.cottage`) | head (1, 4, 5), foot (2, 4, 5) | 1 (head west, toward the front gable) | **Gap:** one block from the parents' bed at z 3, with the existing loft chest at (1, 4, 4) between the heads (his inn ruling: beds one block apart). **Path:** the ladder top at (6, 4, 3) reaches both bed feet along z 3–5. **Headroom:** feet 5 above is air. |
| `cottage_m` (`civ_roster.cottage_m`) | head (1, 4, W−2 = 6), foot (2, 4, 6) | 1 | **Clearance:** clear of the store (3–4, 4, 3) and the ladder top (6, 4, 6). **Path:** from the ladder along z 6. **Headroom:** feet 5 above is air. |

- **Diffs against `knowledge/tools/`:**
  - `HOMES-tools-civgen.diff`: 2 bed blocks + a `station:bed` marker.
  - `HOMES-tools-civ_roster.diff`: the same.
- **Checked in memory** by building both cottages with the patched generators:
  - 4 bed blocks = 2 beds each;
  - every bed cell was air before;
  - feet 5 above every bed cell is air.
  - Before/after plans: `HOMES-files/COTTAGE-PLANS-before-after.txt`.
- **Pipeline (cloud), as for inn_v2:**
  1. `civ_roster` / `civgen`, then `civ_variants` (skins a–d), then `civ_stages` (s0–s4) and `weather_overlays` (_w / _r),
     then `civ_village_data`.
  2. That regenerates the table, where the cottages' `dir` lists 4 bed blocks.
  3. Then: `geo_ref_check`, the permutation count (beds are vanilla: +0), and the BDS gate.
- **Expected effect** (same sim, `BEDS='{"cottage_m":2,"cottage_s":2}'`): the share is 69–90 % with the rule off and
  77–88 % with it on. The rule then mostly sits idle: 3–10 moves in 260 days.
- Adding the bed only to `cottage_m` gives 35–51 % off and 65–86 % on.

### 3.2 Already-built cottages (his call)
- **(A) Same family names; existing cottages are furnished in place.**
  - The table counts 2 beds for every cottage at once, but the old ones physically still have 1 bed.
  - Needed in the clock:
    - a per-building flag (`b.kb`): `homeRoom` counts `beds − 1` for a cottage without it;
    - a one-time furnish job that places the 2 bed blocks at the rotated local cells when the chunk loads, then sets `b.kb`.
      This reuses `rotXZ` and the clock's own directional fix.
  - Optionally the `_r` restoration overlay could carry the bed, so every restoration furnishes the cottage.
  - My recommendation, if he wants every cottage fixed.
- **(B) New revision for new plots only** (the inn precedent, D-GH1007-INN: "keep existing inns").
  - `pw:mvv_cottage_{s,m}_{a..d}_r2`. The INN worker's `short()` / `familyOf` change to `_r<n>` makes this possible.
  - Old cottages keep 1 bed. The table is truthful per family, and the FAMILY rule handles the old ones.
- **(C) A bigger family cottage.**
  - Only if "small" meant floor area rather than beds, e.g. a new kind `cottage_f`, 9 deep × 9 front, two full storeys with
    a parents' chamber and a children's room.
  - It costs frontage and changes the tier charter (`TIER_ADDS`), which is "law" and needs his OK. No numbers yet.

## 4. #28 — crossroads and the wooded city park

### 4.1 Mechanism (base file:line)
- **Where a crossroads comes from.** A crossroads is the `cross13` piece. `queueJunction` (`pw_civ_clock.js:5492–5503`) lays
  it only when a tee already stands at the same t on the other side of the street.
- **The search order.**
  - `sideStreetJob` (`:5577–5578`) lists jobs `for base … for side of [1, -1] … junctionWindows` (main street first, nearest
    the middle first).
  - It opens **one** street per run and returns. The next run starts again from the main street's +1 side.
  - So a town opened every +1 side street of its main street before the first −1 one.
- **Shown in `tests/test_cross.mjs` §2,** with `junctionWindows` cut from the clock and run on stand-ins: after a +1 tee at
  t 94, the old order's next job is another +1 window. The old order made no crossroads.

### 4.2 The change (done)
- **`PLAN.crossFirst(jobs, completes, groupOf)`** (`pw_civ_plan.js:99–114`). Pure and stable:
  - grouped by base street in first-seen order, so the base order (main first) is kept;
  - inside a group, the jobs that complete a crossroads come first;
  - the rest keep their order.
  - D-C1006-WATCH law: keep the priority classes, choose within them. The town does not run away along one line.
- **Wired:**
  - `sideStreetJob` (`pw_civ_clock.js:5581–5585`): a window completes a crossroads when a tee already stands at that t on the
    other side.
    - This also puts each new side street's outward reserved window first in that street's list. That window is straight on
      through the street's own junction, so cross streets run on through the parallels.
  - `closeBlocks` (`:5745–5760`): a connector counts the crossroads it completes at both of its ends.
- **Tests:** `tests/test_cross.mjs`, new, 13 checks.
  - `crossFirst` order, stability, the closeBlocks scoring, empty input.
  - The clock's windows: the old order has no crossroads. The new order completes the cross at the same t, the square's
    frontage is still never used, the side street's outward window comes first, and the main street is still first.
  - The wiring in both functions.
- **Not measured:** how many more crossroads a real town gets. Only a BDS ladder or his world can show that (P1).
  - The 0.0.13 probe had 3 crossroads by town II.
  - The log line "a cross street joins street A and street B (…); crossroads N" counts them.

### 4.3 The wooded park — design note (NOT implemented) and questions
- **Today.** One park per town at **town I**: `kitPark` / `layPark` (`pw_civ_clock.js:6352–6450`).
  - 12 deep × 15 along a street, or a plateau park on a hill.
  - Gravel cross paths, 4 oak benches, 2 lanterns, a fence, and 4 young trees from `PARK_TREE_SET`.
  - `PARK_TREE_SET` holds young oak / birch / cherry, ≤ 9 × 9.
  - Leisure sends idle people to its benches (weight 3).
- **Proposed "Central Park" (a planner rule, using pieces we already have):**
  - **Tier:** city I (TIER_CLASS 2). Grow it by one block at metropolis I.
  - **Where:** a whole grid block next to the main street, the nearest one to the square on its open side.
    - A grid block is bounded by two parallels (pitch 60) and two connectors (pitch 56): **43 × 47 cells** inside.
    - Central-Park-like (≈ 3:1): two blocks merged along the main axis, with the connector between them left out
      = **99 × 47**.
    - It is reserved like the crown's land: `parkReserve` and `boxInReserve`. No house may take its frontage on any of its
      streets. It must never overlap the palace reserve.
    - The block's four corridors are its frame, so the junctions around it are crossroads. That ties in with §4.2.
  - **Content (existing pieces only):**
    - a loop path 3 cells inside the edge, plus a cross path (gravel on cobble, as in `layPark`);
    - an oak bench every 12 cells facing the path;
    - lanterns on spruce fence posts at the path crossings;
    - an oak fence with gates where the paths meet the streets.
  - **Trees:** young templates on a jittered 7-cell grid, kept 2 cells clear of the paths. That is about 24 per block.
    Vanilla saplings go between them, and TREEGROW grows them into our templates, so the park becomes woods over the days.
  - **Leisure:** `parkSpot` works over several parks, and its benches are added to the park options.
- **Why I stopped at a design:**
  - The pure layout (tree spots, paths, benches) is easy to write and test.
  - But staking, reserving and laying a 43×47 or 99×47 park on hills is engine work that only a BDS gate can check:
    - the land, the paths on slopes, `plateauLand` at that size;
    - the felling guards (the lumberyard, `kitPrep` leaf clearing);
    - the chunk loading.
  - And his "**leave** wooded park(s)" has two readings (below).

---

## 5. Findings and assumptions (for the decision journal)

**Assumptions:**
- ASSUMPTION (#29): `FAMILY.perBed = 2`, his palace sleeping law (`COURT.sleepers`, his 17:52). If he wants a bed for every
  person, set it to 1; then no starter home sleeps 4.
- ASSUMPTION (#29): an exchange of homes carries no deeds (both households pay from the one purse); both homes are restored.
- ASSUMPTION (#29): `FAMILY.perDay = 2`; the ranks-at-work guard is a sum (family; family + partner); the far guard is
  `COMMUTE.far`.
- ASSUMPTION (#28): crossroads-first sits *inside* each base street (main first). It is not a global class above centrality.

**Pre-existing findings, not changed:**
- FINDING (not changed, outside this scope): the far-from-work move (`pw_civ_people.js` 3c) and the move to another town use
  `household()`. That includes **child-stage** kids only, so a parent's apprentices (10–19) stay behind in the old home. The
  new `familyOf` keeps dependants together. Should the far move and the town move use it too? A question for the lead.
- FINDING: `farm_cattle` has **0 beds**. Its farmer's family is always "short", and the FAMILY rule may move it to a home with
  beds within 160 blocks of the farm. A bed in the barn's loft would fix that (generator, cloud).
- FINDING: the inn counts as a home (`HOUSEHOLD.inn = 1`). The innkeeper's family is outside the FAMILY rule (guest beds).

**Integration:**
- The INN worker (r2 inn) keeps the kind `inn` through its generalised `short()`, so `FAMILY.guestBeds = ["inn"]` still holds.
- No line conflicts are expected. INN's edits are at `short` / `familyOf` (~2518–2636); mine are at 59, 902, 1295, 5583,
  5757 and 8196.

**RETRO-SWEEP hits** (for the lead to log; not implemented):
- worldgen/structures: every dwelling generator should state "sleeps n (2 to a bed)" in its manifest, and the table should
  carry it. (S, MED)
- scripts: `PLACES.BEDS_BASE` remains off. Places (`HOUSEHOLD × DENSITY`) and beds are two different laws; this round adds the
  beds law for families only. (doc, S)
- documentation: FOUNDATION should state the sleeping law (2 to a bed) once he confirms it. (S)
- NO-HIT: terrain caps · trees · redwood · mobs · atmospherics · PBR/MERS · custom blocks/permutations (vanilla beds only) ·
  audio.

## 6. In-game tests (only he can confirm; P1)
1. **Homes (new world, or his town at town tier or above).**
   - `/scriptevent pw:clock homes` → the families line ("N sleep in their own beds, M short").
   - Repeat after some days, for example after `/scriptevent pw:clock skip 20`. The "short" count should fall.
   - `/scriptevent pw:clock log` should show lines like "Ada's family of 4 outgrew the beds of #12 and moved to #30" or
     "… exchanged homes (#12 <-> #31): beds for the family".
   - Content log: `[CIV-HOMES]`.
2. **Crossroads (a NEW world; the order acts on new side streets).**
   - Grow to town II / city I with `/scriptevent pw:clock grow` and `skip`.
   - The log should show cross streets at the same junction on both sides of the main street. Look for "crossroads N" in
     "a cross street joins …" lines.
   - From the air, side streets should line up across the main street (4-way crossings) instead of all on one side first.
3. **Physical check (after the cloud builds the new cottages):** climb into a new `cottage_s` / `cottage_m` loft. There should
   be two beds, one block apart, with nothing blocking the ladder top.

## 7. Questions for Abs0lum (copy-paste)
```
Q1 (#29) "seemed small for a family of 4" — what felt small?
   (a) too few BEDS (1 bed in the small and medium cottages)   (b) the ROOMS / floor area   (c) both
   -> (a): a children's bed in the loft of cottage_s and cottage_m, same footprint (designed, ready for the cloud build)
   -> (b)/(c): a bigger "family cottage" (new kind, ~9 x 9, two full storeys) — costs street frontage
Answer:
Q2 (#29) Sleeping law: two to a bed (as in your palace ruling) — OK for ordinary homes too?   yes / no (a bed each)
Answer:
Q3 (#29) Existing cottages: furnish them in place with the new bed (A), or keep them and only new cottages get it (B, like the inn)?
Answer:
Q4 (#28) "leave wooded park(s)": (a) LEAVE natural woods standing inside the city as parks (no felling; paths + benches added),
   (b) PLANT a wooded park on open land, (c) both (keep woods where they stand, plant where open)?
Answer:
Q5 (#28) Park size at city I: one block (43 x 47) or a Central-Park-like strip of two blocks (99 x 47), +1 block at metropolis?
Answer:
Q6 (#28) Park on a hill: paths follow the land (steps/ramps on the paths) or level terraces?  A pond: yes / no?
Answer:
Q7 (#28) "more crossroads": is completing 4-way crossings enough, or do you also want SMALLER blocks (more cross streets;
   today 43 x 47 inside, which costs house frontage)?
Answer:
```

## 8. Files
| file | what | md5 |
|---|---|---|
| `w232-HOMES/pw_civ_people.js` | FAMILY block + hook + result | `6994b41d480ab5c44f78b9b7db5813be` |
| `w232-HOMES/pw_civ_clock.js` | homeRoom kind; diag; `homes` command; crossFirst wiring (sideStreetJob, closeBlocks) | `fd2466e348c623be836282c4cfcf97fb` |
| `w232-HOMES/pw_civ_plan.js` | `crossFirst` | `84f8e8b2e04404e3b2d1a7195b09a51f` |
| `w232-HOMES/tests/test_homes.mjs` | new suite, 57 checks | `190cc2b65be9dd7b1c7ed58e07dc800d` |
| `w232-HOMES/tests/test_cross.mjs` | new suite, 13 checks | `24a88e9e48c320b4387702b1098125fe` |
| `out232/HOMES.diff` | the 5 files vs base | |
| `out232/HOMES-tools-civgen.diff`, `HOMES-tools-civ_roster.diff` | PROPOSAL: the children's bed (not built) | |
| `out232/HOMES-files/tools/{civgen,civ_roster}.py` | the patched generators (proposal) | |
| `out232/HOMES-files/tools/cottage_plans.py`, `COTTAGE-PLANS-before-after.txt` | the in-memory plan check | |
| `out232/HOMES-files/homes_sim_seeds.mjs` | the 8-seed simulation (`BEDS='{"cottage_m":2}'` overrides beds) | |

## 9. Final full test run (`work/test-harness/run_civ_tests.sh w232-HOMES`, rc 0 = every `node --check` passed)
```
test_alarm: test_alarm (b): 17 pass, 0 fail
test_band: test_band: 51/51 passed
test_beat: test_beat: 116/116 passed
test_canopy: test_canopy: 5/5 passed
test_coins: test_coins: 810/810 passed
test_court: test_court: 37/37 passed
test_cross: test_cross: 13/13 passed
test_diet: test_diet: 8/8 passed
test_doorramp: 14/14 PASS
test_econ228: test_econ228: 1195/1195 passed
test_fell: test_fell: 31/31 passed
test_frontage: test_frontage: 12/12 passed (houses: ramp-aware 13, flat-only 0, cesspit 13, ramps 13)
test_homes: test_homes: 57/57 passed
test_households: test_households: 95/95 passed
test_hygiene: test_hygiene: 15/15 passed
test_inn24: test_inn24: 57/57 passed
test_landclock: test_landclock: 25/25 passed
test_lanes: test_lanes: 14/14 passed (lane 101 cells, 5 legs, turns 4)
test_leisure: test_leisure: 27/27 passed
test_market: 16/16 passed
test_names: test_names: 48/48 passed
test_needs: test_needs: 80/80 passed
test_occupied: test_occupied: 97680/97680 passed
test_plan: test_plan: 37/37 passed
test_plateau: test_plateau: 76/76 passed
test_player: test_player: 71/71 passed
test_ramp8: test_ramp8: 7/7 passed
test_rampclear: rampclear force: 9 pass, 0 fail
test_route: test_route: 468/468 passed
test_save: test_save: 40/40 passed
test_shifts: test_shifts: 90/90 passed
test_survey: test_survey: 25/25 passed
test_talk: test_talk: 48/48 passed
test_watch: test_watch: 15/15 passed
test_why: test_why: 33/33 passed
```
