# CIVITAS 1.3.228 — BATCH B3 NOTES (2026-10-06)

**Scope:** People I, the census law. BF4 (needs that grow, mood tiers set output), PE3 (grief by closeness), PE6 (births), PE12 (rumours), PE4 + PE7 (house level gates skill and diet, the skill XP curve), PE8 (temperament and interest). Q4 and Q2 use Abs0lum's defaults.
**Source tree:** `/home/claude/tools/bp02_src_228/` only. `_build`, `_bds` and the running gate were not touched.

**Status:** static checks and node tests only.
- `node --check` passes on every changed file.
- `js_dupcheck` is clean (rc 0) on all root scripts of the source tree.
- All 13 node suites pass (1 of them new).
- A scratch smoke run used a copy of the clock outside the tree, against the engine stub. The real `censusDay` ran 12 days and `stepEconomy` ran 2 days. `[CIV-MOOD]` lines were written, house levels mapped, skill and acts were counted, and there were 0 errors.

Nothing here has been verified on BDS or in game.

---

## 1. Files

**Changed**
- `pw_civ_people.js`: the law (pure).
- `pw_civ_clock.js`: the census context, the gate signals, and the economy's `moodBy`, `API.skill` and `API.act`.
- `pw_civ_economy.js`: mood scales the abstract runs.
- `pw_civ_work.js`: two `API.act` calls.

**New (test only)**
- `tests/test_needs.mjs`: 80 checks.
- `tests/fixtures/pw_civ_people_b2.js`: a frozen copy of the pre-B3 people module, used for the A/B save measurement.
  - It is under `tests/`, and the build skips that folder (`rel.parts[0] in ("node_modules", "tests")`), so it never ships.
  - It is not a new script for `NEW_SCRIPTS`.

**No new scripts.** `build_bp02_228.py` needs no change: `NEW_SCRIPTS` stays `{pw_civ_beat.js, pw_civ_save.js}`, and the tests are globbed. Build scripts were not edited.

---

## 2. Changes per function

### pw_civ_people.js

**The B3 block (new).** It sits directly above `skillOf` and holds every constant and flag (§3):
- `FLAGS`, `NEEDS`, `OUTPUT`, `GRIEF`, `BIRTH`, `RUMOUR`, `SKILL`;
- `HOME_LEVEL` and `HOME_LEVEL_SHOP`;
- `TEMPERS`, `INTERESTS`, `TEMPER_TELL`, `INTEREST_KINDS`.

**New pure functions**

| Function | What it does |
|---|---|
| `hash32(n, salt)` | A murmur3-finaliser integer hash. |
| `temperOf(p)`, `interestOf(p)`, `temperName`, `interestName` | PE8, from the id. `p.tm` is used only if it is present. |
| `homeLevel(kind)` | PE4. The table, palace* = 5, any other building = 3 (a keeper's rooms over the shop). |
| `levelOf(p)`, `noteLevel(p, lvl)` | Each person's last census-day house level, in a **WeakMap**: memory only, never saved. |
| `escalation(days)` | 1, then ×0.75 from day 7, ×0.5 from day 14. |
| `carry(prev, pressure)` | Returns `[whole points, fraction carried]`, with the fraction kept to 2 decimals. |
| `hungerPressure(fed, foodDays)` | The town's daily hunger band (§3). |
| `fatiguePressure(holders, vacancies)` | `−rate × min(loadMax, (holders + vacancies) / holders − 1)`. |
| `dietVariety(stock, population)` | The number of bread, meat, fish and grain goods with stock above one day of need. |
| `foodDaysOf(stock, population)` | (bread + meat + fish) / (1.5 × population). |
| `moodParts(p, c)` | The 10 factors (§3). |
| `moodTarget(parts)` | 50 × the weighted mean of the **non-neutral** factors. All neutral gives 50. |
| `moodFactor(mood)` | The tiers, with the 0.70 floor. |
| `moodTiers(P)` | The histogram `{t90, t75, t50, t30, t0}`. |
| `workMood(P)` | Each workplace's factor from its people's mean mood (job id, or `"fisher"`). It is 0 only with `FLAGS.STRIKE` and a 3-day strike counter. |
| `birthChance({mood, foodDays, fullness})` | PE6. |
| `skillGain(acts)` | PE7. |
| `rawRank(d)` | The rank from days alone. |
| `mourn(P, dead, people)` | PE3. |
| `know(p, id)`, `capKnows(p)` | PE12. |

**Changed functions**

`rankOf(person, trade, lvl = levelOf(person))`
- Gated by the house level: journeyman needs level ≥ 1, master needs level ≥ 2.
- `lvl` undefined means the level is not known yet, and the rank is ungated. This is the case only between a reload and the first census day.

`outputFactor(person, trade, lvl)`
- The curve is `1 + 0.5 × (1 − e^(−d/60))`. It was `1 + min(0.5, d/120)`.
- `d` is cut at the gated rank's ceiling: 15 days for an apprentice, 60 for a journeyman.

`newPerson`
- It no longer writes `grief: 0`, `lowDays: 0` or `playerFond: 0`. These are stored only while non-zero, and every reader treats a missing one as 0.

`rumour()`
- It is known by `who` only, and starts with `heard: 0`. It was `heard: who.length`.
- It goes through `know()`, which keeps the cap.

`diet()`
- The dead and departed also drop `hl`, `jl`, `grief`, `lowDays` and `playerFond` after a day.

**`dayStep` (the census day)**

New context:
- `levels`: a Map or `{id: lvl}`;
- `foodDays`;
- `diet` (the variety count);
- `acts`: a Map of pid → real acts today;
- `restOf(p)`: optional, the B4 hook.

Step by step:
- **§2 Death.** The death chance has `(FLAGS.SANITATION_DEATH ? 1 + 0.6(1 − san) : 1) × (1 − 0.3 care)`. The healers' benefit stays. Grief comes from `mourn()`, which replaces "spouse and kids = 20".
- **§2 Births.**
  - `fullness` = housed / (housed + free places).
  - At most `BIRTH.kidsPerHome` children in a home.
  - The household mood is the mean of the couple.
  - The roll is `r() < birthChance(...)`. The `fed ≥ 0.9` gate (`BIRTH.fedMin`) and the crowd rule stay.
  - If `TEMPER_INHERIT` is on, a baby may store `tm`.
- **§3b Skill.**
  - The rank "before" uses yesterday's level (memory), so a better home that opens the gate is news that day.
  - The gain is `skillGain(acts)`, kept to 1 decimal.
- **§4 Mood (rewritten).**
  1. The town's hungry-day counter `P.need.hd`.
  2. The hunger carry `P.need.h`.
  3. The fatigue carry per understaffed workplace, `P.need.f[job]`. A workplace that is fully staffed drops its drift.
  4. Per person: the `hl` / `jl` counters, `noteLevel`, then `moodParts` → `moodTarget`, smoothed 0.7 / 0.3 as before.
  5. Then **+ the whole hunger points + the whole fatigue points of the person's job**, clamped 0..100.
  6. Grief −1 a day, as before.
  7. `lowDays`, `grief` and `playerFond` are deleted at 0.
  8. The strike counter `P.need.sk` runs only with `FLAGS.STRIKE`.
  9. `P.need` is deleted when empty.
- **§5 Leave.** It reads `(p.lowDays || 0)`. This is required now that `lowDays` is stored only while non-zero.
- **§6 Rumours (PE12 + PE8).**
  - The day's events start rumours known by **their own people only**: the two random witnesses are removed.
  - `ctx.events` rumours are known by `e.people`, or by the first living person when the event names nobody. Before, it was the first 3 living plus the people.
  - Fresh-filter plus `capKnows` (newest 10). An old save's long lists are cut on the first day.
  - A teller passes **at most 3 new rumours a day to each friend**. Rumours of his interest's kinds go first, then the newest. The telling chance is `0.5 × TEMPER_TELL` (talkative 1.5, curious 1.2, dour 0.8, shy 0.6; clamped to 1).
  - `know()` refuses a rumour older than everything a full memory holds, so there is no daily re-learn and no false `heard`.
- **Return.** Adds `parts` (the mean factor per name), `hungerW`, `tired` and `fullness`, for the clock's diagnostics.

### pw_civ_clock.js

**`homeLevels(s, st)` (new).** A Map of building id → `PEOPLE.homeLevel(short(b))` over the settlement's plots.

**`ACTS` and `noteAct(v, st)` (new).** In memory: settlement → Map pid → real acts today. It resolves the pid from the `civ:person:` tag, in try.

**`censusDay`**
- Passes `levels`, `foodDays` (from `L.stock` and `population()`), `diet` (`dietVariety`) and `acts` (taken and cleared).
- Writes `diagOf(st).mood`, in memory: `{day, n, mean, tiers, births10, knows, fed, foodDays, diet, hungerW, need, fullness, parts}`.
  - `births10` is derived from the census: living people with parents, born in the last 10 days.
- Logs **`[CIV-MOOD] {...}`** every 10 census days and on the first census day after a load.

**`stepEconomy`.** `moodBy` comes from `PEOPLE.workMood(st.people)`, with `"fisher"` mapped to `fishery:<st.id>`. It is passed to `ECON.dayStep`.

**The work API**
- `skill` returns `outputFactor(p, kind)` (level-gated) × `moodFactor(p.mood)`, with a minimum of 0.05 as a guard.
- New: `act: (v, st) => noteAct(v, st)`.

**The no-player status (`pw:clock_stl`).** `census.needs` = `diagOf(st).mood`.

### pw_civ_economy.js

`dayStep` production:
- `runs = max(1, stations) × ctx.moodBy[shop.id]` (1 when absent). The input bound `floor(stock / n)` is unchanged.
- A real day's carried production (`REAL` + `ctx.produced`) is **not** scaled again: mood is already in the hands' pace through `API.skill`.
- A factor of 0 (strike flag only) gives no production.
- Without `moodBy`, behaviour is identical to before (`test_market` 16/16).

### pw_civ_work.js

`API.act(v, st)` is called at:
- the quarry strike, when a block was actually dug;
- each chop hit.

Both are guarded by `if (API.act)`.

---

## 3. Constants and flags (all in `pw_civ_people.js`, the B3 block)

### Flags

| Flag | Default | Meaning |
|---|---|---|
| `FLAGS.SANITATION_DEATH` | **false** | Q4 default. Poor sanitation no longer raises the death chance (the old rule went up to +60 %). Sanitation is a mood factor only. `true` restores the old rule exactly. |
| `FLAGS.STRIKE` | **false** | Q2 default. No full strike. A workshop's factor never falls below `OUTPUT.floor`. `true`: a workplace whose mean mood is below 15 for 3 census days produces 0. |
| `FLAGS.TEMPER_INHERIT` | **false** | PE8. `true`: a town-born child takes a parent's temperament (½ chance, seeded by id). That stores `p.tm` only when it differs from the id's own. Off means id only, with no save cost (as asked). |

### BF4: the mood sum (`NEEDS`)

Target = 50 × Σ(wᵢ·fᵢ) / Σwᵢ over the factors with fᵢ ≠ 1. Mood = round(0.7 · mood + 0.3 · target) + whole pressure points.

| Factor | Weight | Values |
|---|---|---|
| food | 4 | fed ≥ 1: **1.8**; 0.7 ≤ fed < 1: neutral; fed < 0.7: **0.2**, escalating by the town's hungry days |
| home | 3 | housed: **1.4 + 0.1 × (level − 1)** (level 1 = 1.4, level 5 = 1.8); homeless: **0.2**, escalating by `p.hl` |
| job | 2 | adult or elder with a job: **1.8**; jobless adult: **0.5**, escalating by `p.jl`; child or jobless elder: neutral |
| paid | 2 | job holder with wages in arrears: **0.5**; else neutral |
| friends | 2 | 0 / 1 / 2+ friends (fondness ≥ 40): **0.8 / 1.4 / 1.8** |
| family | 1 | married **1.6** (+0.2 with children); children, no spouse **1.3**; else neutral |
| grief | 3 | 1 − grief/25 (grief 20 → 0.2) |
| council | 1 | 1 + 2 × (trust − 0.5), clamped 0..2 (D-C550 learned trust) |
| sanitation | 1 | Q4: 1 + 1.5 × (s − 0.7), clamped 0..2 (0.7 = neutral) |
| diet | 1 | PE4: variety ≥ 1 + ⌈lvl/2⌉ → **1.3**; below it at level ≥ 3 → **0.7**; else (or homeless) neutral |

**Escalation (`NEEDS.escalate`).** A factor below 1 is ×0.75 from day 7 and ×0.5 from day 14.

**Day counters**
- `P.need.hd`: the town's hungry days.
- `p.hl`: homeless days.
- `p.jl`: jobless adult days.
- All are saved only while > 0.

**Pressure (carried drift; only whole points move mood)**

| Hunger band (town) | When | Per day |
|---|---|---|
| well fed | fed ≥ 1 and food ≥ 5 days | +0.5 |
| adequate | fed ≥ 1 | 0 |
| hungry | 0.7 ≤ fed < 1 | −1.5 |
| famished | 0.4 ≤ fed < 0.7 | −3 |
| starving | fed < 0.4 | −5 |

- **Fatigue (per workplace, all its holders):** `−1 × min(2, (holders + vacancies)/holders − 1)` while vacancies stay open after the day's hiring. A fully staffed day drops the drift.
- **Hook:** `ctx.restOf(p)` true gives no fatigue that day (for B4 / BF5).

Other `NEEDS` values: `fedFull` 1, `fedLow` 0.7, `fedFamished` 0.4, `dietPer` {bread 1, meat 0.5, fish 0.5, grain 0.5}, `foodPerDay` 1.5, `keep` 0.7.

### BF4: output (`OUTPUT`)

| Mood | Factor |
|---|---|
| ≥ 90 | 1.2 |
| 75–89 | 1.1 |
| 50–74 | 1.0 |
| 30–49 | 0.85 |
| < 30 | **0.70 (floor)** |

`strikeMood` 15 and `strikeDays` 3 are used only with `FLAGS.STRIKE`.

### Other tables

| Table | Values |
|---|---|
| `GRIEF` (PE3) | spouse 20, child 20, parent 15, sibling 10; friend whose fondness for the dead ≥ 70: 8; ≥ 40: 4. The mourner keeps the largest, and any larger grief already held. |
| `BIRTH` (PE6) | `base 0.03 × (0.5 + mood/100) × min(1.5, foodDays/10) × (1 − 0.5 × fullness)`; `fedMin` 0.9; `kidsPerHome` 2 |
| `RUMOUR` (PE12) | `cap` 10 (newest by id); `tellPerDay` 3 per friend |
| `SKILL` (PE4 + PE7) | `cap` 0.5, `tau` 60, `dayCap` 1.5, `actXP` 0.05, `repFree` 8, `repX` 0.35; `gate` {journeyman: level 1, master: level 2} |
| `HOME_LEVEL` (PE4) | cottage_s / cottage_m / farms 1; cottage_l / inn 2; townhouse 3; manor 4; palace* 5; any other building (a keeper's shop) 3 |
| `TEMPERS` (PE8) | cheerful, dour, talkative, shy, proud, worrier, steady, curious |
| `INTERESTS` (PE8) | building, trade, food, family, the sea, the woods, the town, news |

**Skill gain per day worked:** `min(1.5, 1 + 0.05 × min(acts, 8) + 0.05 × 0.35 × max(0, acts − 8))`.

**Rumour kinds told first, by interest:** family → wedding, birth, death; trade → inherit, escheat, first, grumble; the town → arrival, left, news, thread. The other interests have no event kinds yet.

`DIALS.birthChance` is superseded by `BIRTH.base`; the dial is left in place.

---

## 4. Deviations from the matrix rows, and why

1. **Escalation is multiplicative on the factor (×0.75 / ×0.5),** as the brief says. This is MineColonies' law on a mean of factors. The matrix had ×1.25 / ×1.5 on an additive negative term. The additive mood sum became the factor mean ("neutral factors leave the average").
2. **Fatigue comes from understaffing, not from consecutive work days.** The matrix's `p.wd` needs BF5's rest days, which are in B4. Without them every worker's `wd` would only grow.
   - The load an understaffed workplace puts on its holders is a real CIVITAS quantity: vacancies are still open after the day's hiring, and the abstract runs assume full stations.
   - It costs no per-person field: the drift is kept per workplace.
   - B4 can add the work-day rule through `ctx.restOf`.
3. **Hunger is town-wide** (a town carry `P.need.h` and a town counter `P.need.hd`), as the matrix's conflict note says. There is no per-person hunger 0..100.
4. **The repetition penalty is kept** (the brief), though the matrix dropped it. "Repetition" means real work acts beyond 8 a day (a dug block, a chop) counting ×0.35, inside a daily cap of 1.5.
   - Everyone else earns the 1 point a day as before.
   - Skill now keeps 1 decimal.
5. **Five output tiers** (the brief: 0.70 / 0.85 / 1.0 / 1.1 / 1.2). The matrix had four; 1.2 starts at mood 90.
6. **Temperament: id only** (the brief: no save cost). The matrix's inheritance is behind `TEMPER_INHERIT`, off.
7. **PE8 uses in this batch:** the telling chance by temperament, and which rumours are told first by interest. Lines, cadence and petitions wait for B4 and B5.
8. **The house level is memory only** (a WeakMap filled by the census day). `API.skill` and `rankOf` read it. Between a reload and the first census day the rank is ungated: the old ranks apply for under a day.
9. **Births "falling with town size"** use fullness (housed / (housed + free places)), as the matrix's formula says, plus at most 2 children per home (the matrix, from Millénaire).

---

## 5. Calibration (node, a 40-person town, mean mood on days 1 / 7 / 14 / 40)

| Scenario | Old law (B2) | New law (B3) |
|---|---|---|
| fed (fed 1) | 74 92 94 94 | 65 74 74 80 |
| hungry (fed 0.8) | 63 70 70 86 | 57 59 59 69 |
| famished (fed 0.5) | 48 41 41 62 | 47 40 38 44 |
| starving (fed 0.3) | 48 41 41 62 | 44 33 31 40 |
| wages unpaid | 70 86 87 94 | 63 69 70 75 |
| sanitation 0.2 | 67 78 79 90 | 63 70 70 76 |
| understaffed (6 vacancies per shop) | 77 97 99 97 | 65 75 75 82 |
| level 3 homes, variety 2 | 74 92 94 94 | 65 74 74 80 |

**What this means for the gates**
- A fed town sits at about **74–82** (it was 92–94, mostly the old 100 clamp).
- `MOOD_GATE` (45) and the faucet (60) still hold for a fed town.
- A starving town now falls to about **31–40**, where its output tier is 0.85. Before, it recovered to 62.
- **Gate risk:** if the BDS climb sees the faucet (mean ≥ 60) fire less often, growth by immigration slows. Watch the mean in `[CIV-MOOD]` against `faucetMood`.

**Births (40 seeds × 5 days × 20 couples)**

| Homes | Food | Births |
|---|---|---|
| roomy | 12 days | 143 |
| nearly full | 12 days | 112 |
| roomy | 3 days | 37 |
| roomy | 20 days | 173 |

The old flat 0.03 gives about 120.

---

## 6. Save cost (measured in `test_needs`, a synthetic 600-person census)

**(a) Field cost.** A city-shaped census (8 friends, 8 trust entries, 10 rumours known, skill) in the B2 shape: **389,632 chars**.

The same census was then given the B3 fields at their worst plausible incidence:
- 10 % homeless with `hl`;
- 10 % jobless with `jl`;
- every skill fractional;
- `tm` on half the town-born;
- a full `P.need` with 30 workplace drifts and 30 strike counters.

| Variant | Chars | Change |
|---|---|---|
| With the zero-field compaction | **370,837** | **−4.8 %** |
| Without the compaction | 393,037 | +0.9 % |

Both are within the +10 % budget.

**(b) A/B over 30 days.** The same 600-person census from a 227-era save (40 rumours known each), run under the B2 law and the B3 law:

| Law | Chars | Knows entries |
|---|---|---|
| B2 | 1,495,964 | 158,742 |
| B3 | 665,271 | 5,530 |
| Change | **−55.5 %** | |

The knows share falls.

**Census-day time (node, 600 people, 60 days)**

| Law | Median | Max |
|---|---|---|
| B2 | 75.5 ms | 383 ms |
| B3 | 55.6 ms | 121 ms |

The knows cap does most of this. It runs inside the clock beat (budget 150).

**New saved per-person fields:** `hl` and `jl`, only while > 0. Settlement-level: `P.need`, only while non-empty. Everything else is derived (temperament, interest), in memory (levels, acts, `DIAG.mood`) or an existing field.

---

## 7. BDS gate signals (B3)

**`[CIV-MOOD]` per settlement every 10 census days** (and the first day after a load):
- `tiers`, `{t90, t75, t50, t30, t0}`: the mood-tier histogram for each tier the town reaches.
- `births10`.
- `mean`: compare with `faucetMood` 60 and `MOOD_GATE` 45.
- `fed`, `foodDays`, `diet` (variety 0–4).
- `hungerW` and `need`: `h`, `hd`, and the `f` workplace drifts.
- `fullness`.
- `parts`: the mean factor per name. Expect sanitation below 1 in towns missing works.

**`statesize`.** The `st:<id>:people` sections should shrink after the first census day on a 227/B2 world, because of the knows cap. Section chars per key, before and after.

**Status.** `pw:clock_stl` → `census.needs` carries the same object.

**Behaviour to see**
- Bread and grain production falls on a starved test town and recovers when it is fed (`L.sales`, `L.stock` per day).
- Quarrymen and woodcutters work a little slower in a miserable town: `work.total` per day falls, but never below 0.70 × skill.

**Unchanged**
- 0 `LEDGER DRIFT`.
- The climb to M III passes `moodOk` at every tier.
- No `[CIV-CLOCK] census:` errors.

**Talk form (PS5 witness, optional).** After the first census day, the `Works as … (rank)` line shows the gated rank: a cottage-dwelling veteran shows "journeyman".

---

## 8. Not done and open issues

1. **Not verified on BDS or in game.** Static checks, node tests and a stub smoke run only.
2. **Calibration is a judgement.** The factor values in §3 were tuned in node so that a fed town lands near 75–80 and a starving one near 30–40. The faucet (mean ≥ 60) and the tier gate (45) are untouched. If the gate climb shows slower immigration, raise `NEEDS.food.full`, `home.base` or `job.has`; all are in one block.
3. **Rank titles change.** With the PE4 gate, people in cottages (level 1) never become masters, which is the matrix's design. The "first master" chronicle events will now come from level-2+ homes (cottage_l, inn, shop keepers, manors). Expect fewer master events than in the 227 baseline.
4. **Acts are memory only.** After a reload, that day's acts are lost: the day still gives 1 point. Acts on carried (skipped) days are 0, which gives the base gain.
5. **The strike counter (`FLAGS.STRIKE`) counts census days in `dayStep`; `workMood` only reads it.** `API.skill` (the per-person pace) never strikes: it floors at 0.70.
6. **Fatigue keys on the job id.** Builders, the watch and other posts count as workplaces, so a short builders' crew grows tired too. A new hire inherits the workplace's carried fraction (under 1 point).
7. **News without people** (`ctx.events`; the clock passes none today) starts known by the first living person.
8. **`rankOf` without a known level** (the talk form right after a reload) shows the ungated rank until the first census day.
9. **Build integration:** none. There are no new scripts, the fixture lives under `tests/`, and the tests are globbed.

---

## 9. Test results (source dir, `node tests/<file>`)

| Suite | Result |
|---|---|
| test_needs (new) | 80/80 |
| test_beat | 91/91 |
| test_canopy | 5/5 |
| test_diet | 8/8 |
| test_fell | 31/31 |
| test_frontage | 12/12 |
| test_hygiene | 15/15 |
| test_lanes | 14/14 |
| test_market | 16/16 |
| test_occupied | 97,680/97,680 |
| test_route | 468/468 |
| test_save | 40/40 |
| test_why | 33/33 |

**What `test_needs` covers**
1. Pressure → mood steps:
   - the carry sequences −1, −2, −1, −2 and 0, 1, 0, 1;
   - the hunger bands and the fatigue formula;
   - two identical towns, well fed vs adequate: equal on day 1, every mood exactly +1 on day 2;
   - understaffed holders are moodier, and the drift is kept only for understaffed workplaces.
2. Escalation:
   - the exact multipliers at days 6, 7, 13 and 14;
   - the food, home and job factors escalate;
   - fed 0.5 for 14 days gives mood on day 14 < day 7 < day 1;
   - `hd` counts and is cleared; `hl` counts and is cleared on housing.
3. Neutral factors leave the average; the weights; the 0..100 range; children have no job factor; the unpaid factor.
4. Tiers:
   - the exact bands;
   - the 0.70 floor with no strike, even below mood 15;
   - with the strike flag: still 0.70 on day 2, 0 on day 3, and the floor again when the flag is off;
   - the ledger: a farm gives 48 / 33.6 / 57.6 / 0; a real catch is not scaled; a converter is still bound by its inputs; a content shop gives 1.1.
5. Q4:
   - deaths are identical at sanitation 0 and 1 (30 seeds);
   - with the flag on, the old rule kills more;
   - sanitation stays a mood factor.
6. Grief: the full table (mourn); the 69/70 and 39/40 edges; a larger grief is kept; through `dayStep`, the table − 1.
7. Births:
   - monotonic in mood and food (capped at 15 days), falling with fullness;
   - roomy > full;
   - a home with 2 children has none.
8. Rumours:
   - participants only, `heard` 0;
   - cap 10, newest kept, no churn;
   - no witness code;
   - 3 a day per friend with the interest first;
   - Σ heard = what listeners learned;
   - a busy town stays ≤ 10 for 30 days;
   - an old long list is cut.
9. Skill and diet:
   - the gate by level, and ungated when the level is unknown;
   - the curve at 15 / 60 / 120 days, and the gated ceilings;
   - the daily gain with repetition and the cap;
   - the days count while gated (59 → 66), and a level-2 home gives "master" news that day;
   - the variety count, the food days, the diet factor by level, the house levels.
10. Temperament and interest: stable per id; an even spread over 8,000 ids; independent of each other; a stored `tm` wins; no `Math.random` in the law.
11. The save budget (§6) and the A/B knows cap.

**Other checks**
- `node --check`: `pw_civ_people.js`, `pw_civ_clock.js`, `pw_civ_economy.js`, `pw_civ_work.js` and the fixture all pass.
- `js_dupcheck`: rc 0 on all root scripts.
