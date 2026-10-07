# HOUSEHOLDS & DYNASTY — 1.3.230 (HD) notes

Source tree: `/home/claude/tools/bp02_src_228/` (BP-02, `@minecraft/server` 2.10.0). Every change carries the comment `1.3.230 (HD)`.
Owner's rulings implemented: 2026-10-06 21:39 (move out at adulthood, dynasty, sell old homes, upgrade) and 21:47 (every move out of or into a home restores it to fresh; this creates jobs and spends money; home sales pay those costs back).

Status: **shipped to source, not yet checked in-game.** Static checks and node tests can only rule problems out. A gate run and his witness are still needed. Nothing was built or packaged. `_build`, `_bds` and other packs were not touched.

## What existed (confirmed by reading)

- `DIALS`: child 10, apprentice 20, moveOutAge 25, elder 120, death 130 + deathSpan 30, fertile 100. Births need a married woman in a home with room, with fewer than BIRTH.kidsPerHome (2) young children and no more than DIALS.crowd (2) over capacity.
- Grown children moved out **only** when the parents' home was over-full. They went to the free room nearest their work.
- `inherit()` order: spouse → eldest child → closest friend → escheat. A shop (numeric job id) passed to the heir; an office never did. The house "passed" only as an event: no sale and no move.
- EN2 weathering (`weatherDaily`, B6): a lived-in dwelling ages one band every 40 days (`b.built`, `b.wx`). From band 3 the household is fined (purse → treasury) and the house is repaired by placing `pw:stages/<stem>_r`.
- Economy: one citizens' **purse** for the whole town (there are no per-person purses), the **treasury**, and pennies (12 = 1 coin). `ECON.pay` takes materials from stock and moves wages from treasury to purse. The money invariant is treasury + purse + tills = minted + player + trade in − sunk.

## What changed

### Pure law — `pw_civ_people.js`

| Function | Change |
|---|---|
| `dayStep` §2 grown children | **Replaced** the crowded-only rule with MOVE OUT AT ADULTHOOD. Any adult aged moveOutAge or more (elders too) who still lives with a parent leaves whenever a free home can hold the household: him, a spouse wherever she lives, and their young children. He takes the **best level the household can afford**. Within that level an empty house comes before a place in another household's house, then the house nearest his work. At most `HOUSING.moveOutPerDay` (3) households leave per town per day, crowded homes first, then the eldest. The household **buys** the free home (a `buy` deed). Both homes are queued for restoration. |
| `dayStep` §2 deaths | The dead person's place is freed the same day (`room++`, or `over--` if the home was over capacity). `inherit` now gets the line's kin. `houseAfterDeath` handles the sale or the move-in. When the last living member of a named line dies, a `line` event is added and the name leaves `P.lines`. |
| `dayStep` births | The child gets `p.dyn` = the father's line (`birthLine`). A line's name is registered in `P.lines` with its first town-born child. When the father is himself town-born, the chronicle adds ", of the line of X". |
| `dayStep` moves | Every move adds the homes involved to `restore`. This covers marriage moves, homeless people finding a home, moves nearer work, arrivals, all three kinds of departure, move-outs, sales and heirs moving in. |
| `dayStep` return | Adds `deeds: [{kind: "sell" or "buy", home, lvl, price, pid}]` and `restore: [home ids]`. Every 10 days, lines with no living member are pruned from `P.lines`. |
| `inherit` | Order is now spouse → eldest child → **the line's kin** (same `dyn`; grown before children, then eldest) → closest friend → escheat. A shop never passes to a child heir: the orphan keeps the house and the shop's station is hired out. Returns `{passed, heir}`. Text: "… passes to X (of Y's line)". |
| `houseAfterDeath` (new, internal) | Applies when the house's last resident dies. No heir: the town takes the house and it is queued for restoration. The heir lives elsewhere and the house is **better** than the heir's (higher level) and holds the heir's whole household (heir not a child): they move in, and the old house is **sold** if they left it empty. Otherwise the heir **sells** the inherited house. |
| `adopt` | Lines move with a family that moves to another town. A line whose founder moved keeps him as founder. A line whose founder stayed behind is founded again by the moving father (or another moving parent). A lone mover founds his own line. |
| New exports | `HOUSING`, `priceOf`, `dynOf`, `birthLine`, `lineName`, `affordLevel`, `restoreBill`, `queueRestore`, `restoreDay`, `settleDeeds` |
| `INTEREST_KINDS` / rumour kinds | Added `sold` (interests: trade) and `line` (interests: family). |

### Clock — `pw_civ_clock.js` (all touchpoints)

1. `jobPostsBody`: the builders' crew is 2 + 2 × labour sites **+ restorations in progress**, so restorations create builders' posts.
2. `moveTownIn`: the home a moving family takes in the other town is queued there (`o.restore`).
3. `wageOfPerson` (new): the trade's wage (`ECON.WAGE` through `STATION_WAGE`; a post uses its own wage; builders use the builder's wage). A master earns at least the master's wage. A person with no job earns 0.
4. `censusDay`: passes `wageOf` in the context. After the step it calls `PEOPLE.settleDeeds(L, r.deeds)`, writes one chronicle line per deed (with the coins actually paid, and a note when the payer was short), stores `diag.deeds`, and runs `PEOPLE.queueRestore(st.restore, r.restore)`. `sold` and `line` events now also go to chat.
5. `stepEconomy`: adds `deferDay("restore", restoreDaily)` right after the weather step.
6. `restoreDaily` (new): runs `PEOPLE.restoreDay` on `st.restore`. A plot that is no longer a standing dwelling leaves the queue. When a restoration is done on a weathered house (`b.wx > 0`), EN2's `_r` structure is placed. If the chunk is not loaded, it retries the next day. If placement throws, it gives up without retrying (EN2's own repair still comes at band 3). Then `b.built = today` and `b.wx` is deleted. Chronicle lines are written when the work starts and when it ends. Stores `diag.restore`.

Tonight's fixes are untouched: dayStep §3 still fills town posts before shops, and stepEconomy's guard (`!st.ledger && st.phase !== "built"`) is unchanged.

## Dials (`PEOPLE.HOUSING`)

| Dial | Value | Meaning |
|---|---|---|
| `moveOutPerDay` | 3 | households leaving the family home per town per day |
| `price` | [0, 1440, 2880, 4320, 8640, 17280] p | price by house level 0..5 (a level-1 cottage costs 120 coins; a palace 1,440) |
| `sellShare` / `buyShare` | 1 / 1 | the share of the price the town pays a seller / the share a buyer pays the town (`buyShare` 0 makes free homes free) |
| `affordDays` | 20 | a household can afford a level when its earners' daily wages × 20 ≥ that level's price |
| `wage` | 72 | an earner's daily wage when the clock does not supply one |
| `minLevel` | 1 | the lowest level is open to everyone (a jobless adult included) |
| `restore` | perDay 2, queueMax 64, wage 120, freshDays 1, perBand {stone 12, planks 4} | bill = stone 12 × band × level, planks 4 × (1 + band) × level, builder-days 1 + band at 120 p |

Affordability examples: a single labourer (72 p/day) affords level 1. A keeper plus a woodcutter (168 p/day) afford level 2. A master plus a keeper (288 p/day) afford level 3. A manor (level 4) needs 432 p/day.

The price of every level covers that level's worst restoration (band 3, wages plus materials at base prices). This is tested, and it is what "selling of homes replenishes those costs" means in this model.

## Money model — decision for Abs0lum to confirm

The economy has **one** citizens' purse, not one per person. Under that model:

- **Sale:** an heir sells to the town. The money moves treasury → purse; the chronicle names the heir. If the treasury is short, the town pays only what it has, with no debt.
- **Purchase:** a household moving out pays for its free home, purse → treasury. **This is the money that pays the restorations back.**
- **Restoration:** the treasury pays the bill (builders' wages go to the purse, which creates jobs; materials come from stock). If the treasury is empty or materials are missing, the restoration waits in the queue. Nothing goes negative.
- All transfers are between treasury and purse, so the LEDGER DRIFT invariant cannot move. This is tested.
- **Not done (per-person money):** giving each household its own purse would add bytes to every person and would change ECON's rations, rent and tax rules. "Afford" therefore uses the household's wage income, not its savings.
- **Alternative reading of 21:47, if he meant it differently:** the heir's sale proceeds could pay for the restoration directly (heir receives the price minus the restoration). That is a one-line change in `houseAfterDeath` / `settleDeeds`.

## Edge cases (all covered by tests)

| Case | Outcome |
|---|---|
| No free home | stays; no deed; nothing queued |
| Only an unaffordable home free | stays |
| A couple and a one-place home | they do not split up |
| The spouse lives with her own parents | she goes along; her parents' house gets her place back and is queued |
| An elder still living with a parent | moves out too |
| A moved-out daughter whose parents' home already holds 2 young children | has children in her own home |
| Not the last resident (a widow lives on) | no sale |
| A homeless heir | moves into the inherited house (nothing to sell) |
| The heir lived with his in-laws | moves into the better house; the in-laws' house is not sold |
| The better house cannot hold the household | sold instead |
| Two heirs | the eldest sells; if the eldest is dead, the next child |
| An orphan living in the house | keeps it; the shop does not pass to the child |
| An orphan child living elsewhere | the house is sold; the child does not move |
| The line's kin (a grandson) and a close friend both alive | the grandson inherits |
| A line with no living members | `line` event; the name leaves the register; escheat (no deed, house queued) |
| Restoration with an empty treasury | waits with no debt; starts once the treasury can pay |
| Restoration without materials | waits |
| More than perDay restorations ready | perDay cap applies |
| A queued plot that is no longer a home | dropped from the queue |
| A sale with an empty treasury | pays 0 (no debt) |
| No ledger yet | deeds move no money |

## Tests

`tests/test_households.mjs` was written first and was **red** against the 1.3.229 law: 5 FAIL lines, then a TypeError crash at the first missing export. It is now **green: 95/95**.

- 1 move-out: 25 checks
- 2 dynasty: 10
- 3 inheritance and sales: 27
- 4 restoration and money: 22 (includes the every-move queue checks)
- 5 third generation: 4
- 6 save bytes: 1
- 7 the clock's `restoreDaily` / `wageOfPerson`: 6. This section was written after the clock wiring (not test-first). It cuts the functions out of `pw_civ_clock.js` and runs them on stand-ins.

Rule 5 (the children of adult children): no blocker was found. 500 days from 12 founders produces 139 weddings involving a town-born person and 197 third-generation births, 18 named lines, and 126 people alive.

All suites green after the change (24 files, 100,971 checks): beat 116, canopy 5, coins 810, court 37, diet 8, econ228 1195, fell 31, frontage 12, **households 95**, hygiene 15, lanes 14, market 16, names 48, needs 80, occupied 97,680, plan 37, player 71, ramp8 7, route 468, save 40, shifts 90, talk 48, watch 15, why 33. The other 23 suites match their counts before the change.

`node --check` passes on `pw_civ_people.js` and `pw_civ_clock.js`.

## Save size (the owner wants towns of 5,000–10,000 people)

| Saved field | Cost |
|---|---|
| `p.dyn` | town-born people only: about 10 characters (`"dyn":1234,`). Founders, newcomers and moved-in founders store nothing (`dynOf` falls back to the id). |
| `P.lines` | `{founder id: name}`, only for lines with a living town-born member; pruned every 10 days and at a line's end. About 13 characters per line. |
| `st.restore` | per town, not per person: at most 64 entries × about 12 characters (`{"h":123,"l":2}`); deleted when empty. |
| Deeds, `restore` lists, residents, line index | memory only, never saved |

Test 6 measured +9.3 characters per person with two-thirds of 600 people town-born, register included (98,964 → 104,546). A 10,000-person town that is mostly town-born adds roughly 90–100 KB to the people section.

Speed (scratch benchmark, 10,000 people, 10 census days, node): the 1.3.229 law takes 897 ms per day and 1.3.230 takes 822 ms. That is the same within noise; the move-out scans only free homes. Separate from this work, about 0.85 s per census day at 10,000 people is already a scaling concern for the existing census.

## Known limits and follow-ups (backlog, not done)

- Bodies do not walk to a house being restored. The restoration is abstract labour plus extra crew posts plus the structure placement, like the EN2 repair.
- Arrivals, marriage moves and moves nearer work queue restorations but do **not** buy or sell. Only move-outs buy and only heirs sell.
- `resAt` (residents per home) is kept current for deaths and move-outs. Marriage moves made earlier the same day are not reflected in it, so the "empty house first" preference can be one day stale.
- Lines are patrilineal (father first) as specified; a matrilineal variant would be a dial.
- Gate checks still to add: the `[CIV-…]` diag fields `deeds` and `restore` are stored but not yet logged to a console line, so `gate_check.py` cannot read them yet.
