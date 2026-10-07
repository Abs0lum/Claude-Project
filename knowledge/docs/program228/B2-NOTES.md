# CIVITAS 1.3.228 — BATCH B2 NOTES (2026-10-06)

**Scope:** BF2 (sectioned saves), WE14 (diagnostics out of the save), BF3 (why-idle codes, `why` command, icons), BF10 (real-tree-only felling and work-site claims).
**Source tree:** `/home/claude/tools/bp02_src_228/` only.

**Status:** static checks only.
- `node --check` passes on every changed file.
- `js_dupcheck` is clean (rc 0) on the 5 changed and new scripts.
- All 12 node suites pass (3 of them new).
- The real heartbeat ran 2,400 ticks on the engine stub with all modules loaded: 13 beats, 0 errors (a scratch run, not shipped).

Nothing here has been verified on BDS or in game.

---

## 1. Files

**New (the integrator must add them)**
- `pw_civ_save.js`: the sectioned save. It is a **new script**, so the build script must allow it and copy it into `scripts/`, the same way B1 did for `pw_civ_beat.js`. It is pure: it has no engine import.
- `tests/test_save.mjs`: 40 checks.
- `tests/test_fell.mjs`: 31 checks.
- `tests/test_why.mjs`: 33 checks.

The tests are globbed (`tests/test_*.mjs`), so they need no build change. No build script was edited.

**Changed**
- `pw_civ_clock.js`
- `pw_civ_work.js`
- `pw_civ_walk.js`
- `pw_civ_people.js`

`pw_fell_rules.js` is unchanged. The town reaches its ledger test through the clock's `fellPlaced`, which the tests replace with `__setPlacedTest`.

### pw_civ_save.js (new, BF2)

**Chunked texts**
- `putText(store, key, txt, old)`, `getText`, `dropText` and `hasText` moved here from the clock. The clock keeps wrappers with the old names, so the snapshots and the site fields are unchanged.
- When the old text is known, `putText` writes only the 30,000-char chunks that changed. It writes `:n` only when the chunk count changes, and clears a legacy single key only if one exists.

**Building the sections**
- `split(state)` builds a `Map(key → JSON)`.
- `assemble(read)` builds `{state, problems, index}`, or returns `null` when there is no v3 index.
- Both are deterministic. `assemble(split(x))` deep-equals `x`, and `split(assemble(t))` gives back `t` text for text.

**The saver: `createSaver(store)`**
- **`load()`** reads the index. If there is none, it reads the legacy `pw:civ_clock`. It returns `{state, from: index|legacy|none, problems}`.
- **`write(state)`** runs in one call, so in one tick:
  1. the changed sections;
  2. the index, last;
  3. drops of keys the new index no longer lists;
  4. a drop of the legacy key (on the first save after a legacy load).
- **Memory.** The saver keeps the last-written text per key in memory, about the size of the state. A string compare is native; hashing megabytes in QuickJS is not.
- **After a load,** it remembers only the sections that the assembled town reproduces exactly. A broken or unreadable section is never dropped as "stale": it stays in the store and can be recovered.

### pw_civ_clock.js

**BF2: save and load**
- `load(raw)` loads through `SAVER`. `raw` lets a snapshot be loaded directly.
- The load logs `[CIV-SAVE] load (…): problems` and a legacy notice.
- **Save hold.** If a saved town was there but could not be read, saving stops, so an empty town never overwrites it. `[CIV-SAVE] HOLD` is logged, and `pw:clock savehold off` releases it.
- `saveNow()` calls `SAVER.write`. `state.bytes` is now the total of all section texts.
- One line per save: `[CIV-SAVE] {wrote, of, chars, total, chunks, gen, tick, migrated?, dropped?, keys}`.
- `snapshot load` now parses the snapshot first and refuses a broken one. It then loads it through `load(raw)`; before, it wrote it over `pw:civ_clock` and read it back. The next save writes its sections.
- `KEY` is now `SAVE.LEGACY` and is unused in the clock.

**WE14: diagnostics in memory**
- `DIAG: Map stId → {counters, marketGate, marketTry}`, read through `diagOf(st)`.
- `stockCounters`, the market-hour gate, and `goalFor`'s shopper tally write to `DIAG`, no longer to `st`.
- `st.market.homes` is now the **count** of distinct homes that bought today. Today's homes are kept in a memory Set (`homesToday`).
- `diagOutOfSave(st)` runs on every load. It moves an old save's `marketGate`, `counters` and `marketTry` into memory and turns an old `homes` list into a count.
- The no-player status (`pw:clock_stl`) still carries `market`, `counters`, `marketTry` and `marketGate`, now read from memory.

**BF10: real trees only**
- `treeCells` now also returns `rooted`, `unknown` (a cell in a sleeping chunk), `big` (the flood hit its 400-log cap) and `flood`.
- **A pre-existing crown bug, fixed.** `crownOf`, the rootless crown flood, skipped every cell the log flood had looked at. That is the whole 14-neighbourhood of every log, so the leaves touching the trunk were skipped. A felled rootless tree left its inner crown standing until the leaf sweep came. The flood now starts from the log cells only.
- **`treeVerdict(dim, tree)`** checks, in order:
  1. not asleep;
  2. R4: no log of the flood is on the placed-log ledger (always fresh);
  3. not `big`;
  4. a root is present (R3a), or R5: `naturalCanopy` over the top 64 logs finds at least 3 natural leaves.
- **`treeOk(dim, x, y, z, occupied, now)`** is used when choosing a tree.
  - The verdict is cached for 6,000 ticks for **every log of the flood**, so a cabin's other wall columns and a 2x2 trunk's partner columns are not judged again.
  - Asleep verdicts are never cached.
  - The cache is capped at 8,192 entries, pruned to 6,000.
- `treeKnown(x, y, z)` returns the cached verdict, or undefined.
- `treeWhy(x, y, z)` returns the cached reason.
- **`fellTree`** (now exported) judges the tree again at the fell, with R4 fresh. If the tree is refused, nothing is removed and 0 is returned (`FELL.refusedAtFell`).
- **`clearForest`** skips a column that a hand has claimed (`WORKMOD.claimHeld`) and any tree that is not `treeOk`.
- **`clearTreesOver`**, the clearing over streets, yards and walls:
  - it reads through `blockAt` (it was a raw read);
  - a refused tree ends that column, so a player's logs and a bare pole stay;
  - it no longer `setType(air)`s the start log after `fellTree`. That call removed a player log even when nothing was felled.
- **`digQuarry`** leaves a column standing if a log stands on it, so the pit never undermines or cuts a log.
- `canopyDaily` is unchanged. It still takes down only trees with under 30 % of their crown, and it still skips any tree that touches a placed log.
- The work API gains `treeOk` and `treeKnown`.

**BF3: why-idle**
- `goalFor` sets `ctx.kind` (`fish | survey | shop | site | job | rain | leisure | off`), `ctx.noShop` and `ctx.builderIdle`.
- **Each schedule pass gives every person one code** (`PEOPLE.whyOf`):
  - bodies tagged keeper, watching or working are scored as busy, with the work module's own reason for working hands;
  - the other bodies are scored from their goal;
  - census people with no body seen get `ASLEEP_CHUNK`, `CHILD` or `NO_HOME`.
- `whyNow` (in memory) holds `"stId:pid" → code`.
- `st.why` is saved: at most 16 keys, about 200 chars.
- `[CIV-WHY]` is logged on the first pass and on every tier change.
- **Icons:** see §2.
- `plainName(tag)` strips the icon. `nameTrades` uses it, so the trade suffix never stacks on the icon.

**Status and statesize**
- Player `status` gains two lines:
  - last save `k/n sections, chars of total`, `HELD`, trees felled, and the refusals (player logs, bare, at the fell);
  - per settlement, `why:` with its tally.
- The no-player status adds `fell` (the `FELL` counters) and `save` (the saver totals and the last write). `why` is already in it, because the event spreads `st`.
- `statesize` adds `sections` (chars per key, as last written) and `save` to `[CIV-STATESIZE]`. The reply lists the 6 largest sections.

### pw_civ_work.js

**Claims**
- `createClaims(ttl = 1200)` and the module instance `CLAIMS`.
- A claim is keyed by the site's column, `"x,z"`, and holds `{vid, until}`.
- The other calls: `take`, `free`, `renew`, `release`, `releaseAll`, `order` and `prune`.
- `order` puts **the longest-untouched site first**. A site never claimed counts as the oldest. Ties keep the caller's order, which is nearest first.
- `claimHeld(x, z)` is exported for the clock.

**When a claim is taken, renewed and released**
- It is taken in `nextTree` and `nextQuarryFace` when a `vid` is passed. The work beat passes `v.id`, and each hand holds one claim at a time.
- It is renewed every beat while the hand walks to the site or works it.
- It is released on any of these:
  - the dig;
  - the fell (or a refusal at the fell);
  - an unreachable site (6 walks);
  - off duty;
  - a body that is gone (the 200-tick sweep);
  - expiry after 1,200 ticks without being worked.

**`nextTree(dim, b, st, vid)`**
- The candidates in a ring are sorted by distance, then by claim age.
- A cached refusal costs nothing.
- At most 8 **fresh** verdicts are asked per call (`TREE_JUDGE`). After that, the scan resumes at the same ring on the next beat.
- Claimed trees are skipped.

**`nextQuarryFace(…, near, vid)`**
- It skips faces that another hand holds.
- It picks among the free faces, longest-untouched first, then by the old nearest score.
- A log at g+1 or g+2 is no longer struck as a "plant". The column is left as a pillar and the pit cursor moves past it.

**Why codes and stats**
- `whyOf(vid)` returns `STOCK_FULL` (the last deposit left part of the load in the barrow), `NO_FACE` (the last search found nothing) or null.
- `stats()` adds `claims` and `treeRefused`.

### pw_civ_walk.js
- `refused: Map vid → {why, tick}` is written whenever a send is refused:
  - `UNREACHABLE`: a BACKOFF rest after stuck walks;
  - `NO_ROUTE`: no graph yet, a route still being searched, or no lead because the first waypoint sleeps;
  - `SLOTS_FULL`: no free lead slot.
- A successful send clears it.
- `whyNot(v)` reads it for 400 ticks.
- The map is pruned above 512 entries.

### pw_civ_people.js (pure)
- `WHY` maps each code to its description.
- `whyOf(person, facts)` returns one code.
- `capTally(t, 16)` keeps 15 codes plus `other`.

---

## 2. New commands

| Command | What it does |
|---|---|
| `pw:clock why` | Each town's tally, plus a `[CIV-WHY]` line per town. |
| `pw:clock why <name>` | The reason of every living person whose name contains `<name>` (up to 8 per town). |
| `pw:clock why <CODE>` | Who has that code, e.g. `why NO_HOME` or `why SITE_WAITS:stone` (up to 20 names). |
| `pw:clock why icons on\|off` | **OFF by default.** When on, villagers within 24 blocks of a player get a one-line nameTag suffix with their reason, for example `Ada §8[§cno home§8]`. |
| `pw:clock savehold [off]` | Shows the save hold. `off` releases it and writes the town in memory. |

The header comment and the help reply list them.

**Icons in detail**
- Script API 2.3.0 has no TextPrimitive, so the matrix's fallback is used: a one-line suffix (not the two-line form, which still needs the PS5 witness).
- No icon is shown for `WORKING`, `OFF_SHIFT`, `CHILD` or `ASLEEP_CHUNK`, so normal life adds no clutter.
- A name is written only when it changes.
- When icons are turned off, every suffix is stripped at once.
- Any pass that runs while icons are off also strips a leftover suffix, for example one from before a crash.
- The suffix pattern is ` §8[…§8]`, so it can always be recognised and removed.
- The toggle is saved as `state.whyIcons` (only while on).

---

## 3. Save key layout (v3)

| Key | Holds | Dirty when |
|---|---|---|
| `pw:civ:index` | `{v: 3, keys: [...], gen}`. A plain property, not chunked: about 30 chars per key. | Every save. It is written last. |
| `pw:civ:meta` | `{m: all top-level fields except buildings/settlements (paused, speed, simDays, lastWorld, nextId, lag, accel*, tick, pace, bytes, dpBytes, dpCeiling, whyIcons), st: [settlement tokens], b: [[group, count], …] (the building order)}` | Nearly every save. |
| `pw:civ:b:<stId>` | That settlement's buildings, in order. `pw:civ:b:_` holds buildings of no settlement (the plot tool). | A building of that settlement changes. |
| `pw:civ:st:<stId>:core` | Every settlement field not listed below, including `why`. | Most days. |
| `pw:civ:st:<stId>:streets` | streets, profile, roads7, walls, kitQueue, parked | Kit work. |
| `pw:civ:st:<stId>:people` | The census. | Census and trust changes. |
| `pw:civ:st:<stId>:ledger` | ledger, log | Most days. |

- **Chunking.** Each section is chunked as `<key>:n` plus `<key>:<i>`, 30,000 chars each, below the 32,767 limit. The test store throws on any value above 32,767.
- **Repeated ids.** A repeated settlement id gets the token `<id>~<position>`.
- **Legacy.** `pw:civ_clock` (chunked, or the single key of 1.3.206) is read once. The first save writes every section, then the index, then drops it.
- **Not done: skipping the stringify of `:streets` when `kitVer` and the queue length are unchanged** (in the matrix). Every section is stringified and compared on each save. Streets, profile, roads7, walls and parked can change without a `kitVer` bump, and a skipped stringify would lose them. The streets string is about 30 K, so the cost is small.

---

## 4. Why codes (BF3)

Priority runs from the top of this table down. The first code that applies is the person's code.

| Code | Meaning |
|---|---|
| `—` | No census person on the body, or idle for no known reason. The gate wants 0. |
| `CHILD` | A child. |
| `NO_HOME` | No home. This comes before everything else, including work. |
| `ASLEEP_CHUNK` | No body seen this pass: it is in sleeping land or not spawned. |
| `OFF_SHIFT` | Outside work hours (1000–11000). |
| `NO_STOCK` | The household's shopper found no shop to buy from (`shopFor` was null). |
| `SITE_WAITS:<good>` | A builder or jobless person with no labour site, while sites wait for a material. The good is the one with the largest shortage in `b.waiting`. |
| `UNREACHABLE` / `NO_ROUTE` / `SLOTS_FULL` | Walk refusals from `WALK.whyNot`, read when the person is not walking and is more than 3 blocks from the goal. |
| `NO_FACE` / `STOCK_FULL` | Woodcutters and quarrymen, from the work module. |
| `WORKING` | At work or on the way: fisher, surveyor, shopper, site, station, keeper or watch. |
| `RAIN` | Sent home by the rain. |
| `NO_SITE` | A builder or jobless person with no site, and nothing waiting. |
| `NO_JOB` | No job. |
| `HOME_FAR`, `UNPAID` | Defined but reserved (PE5 / WP1). They are not emitted yet. |

**Two extra codes.** The matrix's list was missing `WORKING`, `CHILD` and `NO_SITE`; `WORKING` and `CHILD` were needed so that nobody falls into `—`.

---

## 5. BDS gate signals (B2)

**Saves (BF2)**
- One `[CIV-SAVE]` line per save. In normal play `wrote` is well below `of`, mostly meta, core, ledger and people.
- **DP writes per minute < 2 MB** (226-2: 18–23 MB). That is the sum of `chars` over 2 saves; `chunks` counts the property writes.
- On the first save of an old world: `migrated: 1` and `wrote == of`. After that, no `pw:civ_clock` key remains.
- After a restart, the first save writes nothing but the index (`wrote: 0`).
- No `[CIV-SAVE] load … problems` lines and no `HOLD`.
- `statesize` → `sections`: chars per key.
- The town survives a restart: same `simDays`, same building stages, same census count.

**WE14**
- `statesize` before and after: the `core` sections shrink (no `marketGate`, `counters` or `marketTry`).
- `status` still shows the market gate and counters.

**Why (BF3)**
- `[CIV-WHY]` once per tier, per settlement.
- `—` is 0 (or near 0) at the M III census.
- `pw:clock why` answers in game.
- **PS5 witness for icons (only if he turns them on):** the suffix renders, and the names are plain again after `why icons off`.

**Felling (BF10)**
- A scripted player log cabin inside a yard's radius **stands after 5 days**.
- Status `fell.placed` > 0 if the cabin was judged.
- `fell.felled` > 0 continues, and `workTotal` and the lumberyard deposits keep growing.
- `work.claims.refused` and `held`: no two hands at one tree or face. Watch `stats.sample`.
- Engine throws stay flat. `[CIV-WORK] slow beat` lines no more often than in the 227 / B1 baseline: the fresh verdicts sit inside the face budget, at most 8 per call.

---

## 6. Not done and open issues

1. **Not verified on BDS or in game.** Everything above is static checks plus node tests on the stub.
2. **Save atomicity.** The sections and the index are written in one call, so in one tick, with the index last. If a `setDynamicProperty` throws in the middle (for example a world quota), the sections written before the throw are newer than the index that still points at them. The next save rewrites them. Not expected at the sizes measured.
3. **The index is one plain property,** about 30 chars per key and 5 keys per settlement: about 7 KB at 50 settlements. Above about 200 settlements it would need chunking. It is not guarded.
4. **Memory.** The saver keeps the last-written text of every section, about the size of the state (a few MB at metropolis).
5. **The 64-log cap reads differently from the matrix.** The matrix says "at most 64 logs" for `treeOk`. Here, R5 examines only the **top 64 logs**, and only a flood that hits the 400-log cap is refused as `big`. Refusing every rootless tree above 64 logs would leave real vanilla mega trees (2x2 jungle and spruce, about 100–130 logs) standing forever. A cabin with no natural leaves is still refused by R5, and by R4 when it is in the ledger.
6. **Logs missing from the ledger.** Logs a player placed before the ledger existed, or more than about 2,000 per chunk, are not in it. Such a structure is still refused by R5 (no natural leaves) unless a natural crown touches it. `canopyDaily`, the bare-trunk rule, can still take down a ledger-less bare pole, because that is its job. It was unchanged as instructed.
7. **"Longest-untouched first" is my reading.** Among free candidates, the site whose last claim ended longest ago (never claimed = oldest) goes first; ties keep nearest-first. If he meant something else (for example rotating whole yards or pits), it needs a ruling.
8. **Off duty, a hand's face is now dropped** (`face.done`) together with its claim. The next morning he searches again and usually takes the same tree. A half-chopped tree restarts its hit count.
9. **Quarry columns with a log** are left as pillars, both in the worker's pit and in `digQuarry`. A real tree standing inside a pit site is not felled by the quarrymen. The woodcutters or `canopyDaily` deal with it.
10. **Why codes not covered:**
    - `NO_STOCK` is set only when the shopper has no shop to go to. An empty counter at purchase (`st.market.empty`) does not set it.
    - `HOME_FAR`, `UNPAID` and the `STOCK_FULL` of WE9 caps wait for their batches.
    - The walk refusal is the last one within 400 ticks, so a send skipped by the 40 ms send budget shows no new code.
11. **`whyNow` is never pruned** (one entry per person ever seen, dead ones included). This is negligible, a few thousand short strings.
12. **The no-player status event** grows by about 0.5 KB (`fell`, `save`, `why`). The code warns that an event is capped at 2 KB, and this one already carried far more than that (streets, roads and the rest of the settlement), so a size problem would already have shown up. Its real limit was not checked.
13. **Build integration:** add `pw_civ_save.js` as a new script (as `pw_civ_beat.js` was in B1).

---

## 7. Test results (source dir, `node tests/<file>`)

| Suite | Result |
|---|---|
| test_save (new) | 40/40 |
| test_fell (new) | 31/31 |
| test_why (new) | 33/33 |
| test_beat | 91/91 |
| test_hygiene | 15/15 |
| test_canopy | 5/5 |
| test_diet | 8/8 |
| test_frontage | 12/12 |
| test_lanes | 14/14 |
| test_market | 16/16 |
| test_occupied | 97,680/97,680 |
| test_route | 468/468 |

**What the new suites cover**
- **test_save:**
  - the round trip and stable texts;
  - interleaved building order;
  - the first save writes all sections, and an unchanged save writes only the index, last;
  - a stage change dirties only `b:<st>`;
  - a mood change rewrites one chunk of the census;
  - a day dirties meta, ledger and core;
  - after a reload, an unchanged save writes 0 sections;
  - a removed settlement's keys are dropped after the index;
  - legacy chunked and single-key saves migrate, with WE14 cleanup and a distinct-homes count;
  - a broken section is reported and never dropped;
  - a fresh world is not a hold;
  - the chunk law.
- **test_fell:**
  - a natural oak is felled (crown and stump);
  - a player log cabin is refused at the search and at the fell, with nothing removed;
  - R4 beats a root;
  - a bare log pole is refused and still stands;
  - persistent (player) leaves do not count, pw leaves do;
  - a tree touching a player's log is refused;
  - a rooted structure tree is accepted;
  - a sleeping neighbour gives "asleep" and is not cached;
  - the cache holds within its TTL and is judged again after it;
  - claims: exclusive, release, expiry, renew, releaseAll, longest-untouched order;
  - through the real `nextTree`: the cabin and the pole are passed by, two hands get two different real oaks, a third gets none, and `claimHeld` sees both claims.
- **test_why:** the priority table, every code described, and the tally cap.

**Other checks**
- `node --check`: `pw_civ_clock.js`, `pw_civ_work.js`, `pw_civ_walk.js`, `pw_civ_people.js` and `pw_civ_save.js` all pass.
- `js_dupcheck`: rc 0 on the same 5 files.
