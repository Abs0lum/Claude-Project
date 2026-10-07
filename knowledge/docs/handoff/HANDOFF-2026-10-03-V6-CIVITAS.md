# HANDOFF — 2026-10-03 — V6 CIVITAS: the living town on the land (BP-02 1.3.207 + fix round + TestRunner 0.5.15)

SUPPLEMENT to `HANDOFF-2026-10-02-ROUND-1002n-DELIVERED.md` (authoritative for everything not listed here). This file is authoritative for V6 until the next handoff. Journal: `_logs/decision_journal.md` D-C495 (recheck) … D-C499 (runs 0.0.12–0.0.15) + the delivery entry. Phase log: `_logs/phase_log.md` 22:xx 10-02 → 00:xx 10-03.

## 1. What V6 is
His 22:24 directive: *"very VERY EXPANSIVE — it LITERALLY creates the actual world. Take your time, use unconventional methods."* The village clock no longer lays a straight street on flat ground: it **reads the land** and shapes a settlement into it, then the settlement shapes the land back. Everything below ran in the workspace dedicated server (BDS 1.26.52.3) through the evolution probe (`tools/civ_evo_probe.py`, runs 0.0.6 → 0.0.16) — static + server proof only; **his witness run (lineup p22) decides** (P1).

| Step | What the world gets | Server proof |
|---|---|---|
| 1 Founding on the land | site field 160 × 160 (ground + water, a `system.runJob`), the flattest 12 × 12 knoll = the SQUARE (paved, lanterns, well, notice board), the MAIN STREET walked along the contour from the square's edge on **either axis** (the hill decides), snapped to runs + jogs, profile smoothed ≤ 1 block/cell | runs 0.0.6+ (E–W), 0.0.13+ (N–S: 9 plots at founding, 30 at town2) |
| 2 Houses in the hill | plot floor = street + 1 .. + 3; footprint TERRACED (cobble ring, dirt core); hill side CLAD; **2-cell FRONT YARD** levelled to the street row by row, cobble edges, path; STOOP steps in the yard; hillside FIELD (4 climbing strips, retaining walls, channel, stair) | 0.0.14–0.0.16: floating 0, bigStep 0, stoop failures 0 (dump-read) |
| 3 Bridges + cuttings | a street ≥ 4 above the ground = plank deck on log piers + rails; ≥ 3 below = clad cutting | laid when the land asks (0.0.9+) |
| 4 Living marks | quarry pit (stepped, grows per tier), lumberyard clearing (flood-fell, stumps), daily harvests → grain, streets path → gravel → cobble, trees over streets/square/yards felled | 0.0.9+ (quarry 34 stone, gravelled 376), 0.0.16 (trees over streets) |
| 5 Water | docks: plank pier on fence posts, barrel, boat when water lies within 40 of the square | 0.0.14/15: the granddaughter's pier (docks 9) |
| 6 City | tiers village → village2 (25 d) → town (60) → town2 (120) → city (200), gated on roofs + prosperity ≥ 0.8; stone-brick WALL 4 high with gates where streets cross, never through a foreign plot | 0.0.14/15: two cities, walls 2,187 + 2,047 blocks |
| 7 Daughters + roads + trade | pop ≥ 24 fed 30 days → settlers 170–230 away; the daughter founds herself; **A\* road** over the real ground (around every plot, across streets at grade; `LAND.findRoadJob`, node tests 9/9); goods trade along it | 0.0.14/15: roads 103 cells / 300 blocks (5,952 nodes) and 153 / 450; daughter → city → granddaughter |
| 8 Threads + ladder | notice board (sign, last chronicle lines), villagers named "Ada the Farmer", market stand after 5 days of inbound goods, branch after 20; `log`, `market`, `buy`, `sell` | 0.0.11+ |
| Economy (V5) | goods, prices in a band, meals, inn trade, charters for 10-day shortages, closures only among ≥ 2 shops of a kind, households move in / leave / return | 20–21/21 node tests; server runs |
| State | the whole state in **chunked** dynamic properties (`pw:civ_clock:n` + `:i`, 30,000 chars each) — a city's state passed 32,767 chars (45 silent save failures in 0.0.14); snapshots likewise; `status` reports `stateBytes` | 0.0.15: 53,992 chars, 0 failures |

## 2. The delivery (one gofile folder; never rebuild these dirs)
| Pack | Build dir | Contents |
|---|---|---|
| BP-02 1.3.207 | `_build/bp02-207` | the clock above (`scripts/pw_civ_clock.js`, `pw_civ_land.js`, `pw_civ_economy.js`, `pw_civ_buildings.js`) · 38 roster buildings (14 kinds × skins a–d where they exist) with 5 stages each (`structures/pw/`, `structures/pw/stages/`) · farm_terrace (hillside field, earth under the whole plot) · recipe fix (planks wall ≠ room wall) · cottage_s station law |
| RP-07 1.4.45 | `_build/rp07-1445` | RECHECK A1 cave spider `min_engine_version` pin (ours wins over vanilla) · A2 the 13 Naturalist block texture keys moved out · A3 walrus / whale dangling animation names removed |
| RP-08 1.4.14 | `_build/rp08-1414` | A2 the 13 keys with their images + texture sets (one-pack ownership) |
| TestRunner BP 0.5.15 | `_build/testrunner-0.5.15` | lineup **p22 CIVITAS** (12 steps) · banner == manifest (A6) · mock suite 348/348 |
Packager: `tools/package_round_1003a.py` (archive == build dir, md5 in the ledger, < 250 MB).

## 3. TEST BRIEF v4 — lineup p22 (phone hosts, PS5 joins, Vibrant Visuals on)
Install BP-02 1.3.207 + RP-07 1.4.45 + RP-08 1.4.14 (they replace 1.3.206 / 1.4.44 / 1.4.13) and PW-TestRunner BP 0.5.15 at the bottom. Content log after load: `[CIV-CLOCK] village clock loaded — 38 staged building(s)` and `PW Test Runner BP v0.5.15`.
Then `/scriptevent pw:test start p22` and follow the steps; every step sends the clock command for you and tells you what to look for. Simulation distance as high as the console allows (8+ chunks). Stand on a **hillside** with 100 blocks of land each way.

| Step | What happens | Look for |
|---|---|---|
| q0 | setup | versions in the content log |
| c01 | `village 7` + `pause` — the land is read (10–20 s), the square paved, the contour street laid, the first plots staked | square (border, lanterns, well, sign at the SW corner), the street along the contour (either axis), terraced plots with a 2-cell yard and stoop |
| c02 | `skip 6` | first houses finished, doors to the street, stoops in the yards, families inside |
| c03 | `skip 14` + `log` | the whole village; walk the street end to end: no hole, no 2-block step; the sign's chronicle |
| c04 | `skip 10` | village2: a second terrace street, the hillside field, gravel streets, the quarry pit |
| c05 | `skip 40` | town: third street, houses cut into the slope, bridges / cuttings where the land asks, the lumberyard's stumps |
| c06 | `skip 70` + `market` (+16 emeralds, 16 cobblestone) | town2, cobbled streets; `buy bread 4`, `sell cobblestone 8` |
| c07 | `decline on 1`, `skip 45`, `immigrate cottage_s 1`, `decline off 1` | two shops closed (webs, stations gone, families left), one reopened |
| c08 | `skip 80`, `skip 80` | CITY: the wall + gates; "settlers set out for X Z" → **walk there**, wait for the daughter to found, **walk back along the line** for the road |
| c09 | `skip 30` | wagon lines in `log`, a market stand on the square, villagers named by trade |
| c10 | `snapshot save v6` / `load v6` | the town re-placed as it was |
| q9 | `resume` | leave the towns standing; upload the content log |

Report as always: PASS / FAIL + note per step; shots of the square, a street end to end, the town from above, a gate, the daughter, the road.

## 4. Known limits (ASSUMPTIONS logged, his call)
- Daughters 170–230 blocks away (his ruling said 120–200): two site fields never overlap. Say if closer is wanted.
- The road needs its corridor loaded: in play it retries up to 8 days until you have walked the way (p22 c08 tells you to).
- A tree whose trunk stands on a street / square / yard cell is felled without a stump; the lumberyard's clearings keep theirs.
- Yards follow the street row by row; a house's floor is at most street + 3 (deeper into the hill beyond that).
- Settlement tools without an index act on the settlement nearest you (without a player: the first).

## 5. Backlog from V6 (not in this build)
snapRuns should merge ±1 contour drifts (a wavy contour gives 6 short runs) · walkContour hysteresis · stairs / ramps in the yard · cross-lanes between terrace streets (the A\* finder is ready) · wagons as entities (V4b marker walking) · split-level cellars · ruins · the wall box hugs the plots (one far plot stretches it) · wider / marked roads.

## 6. Tools new this round (all in `tools/`)
`bp02_src/pw_civ_land.js` (site field, contour planner on both axes, streetBody, slotVeto, A\* findRoadJob; tests `test_land.mjs` 14/14, `test_land_z.mjs` 13/13, `test_road.mjs` 9/9) · `bp02_src/pw_civ_economy.js` (+ `test_economy.mjs` 21/21) · `civ_evo_probe.py` (the evolution probe: founding → city → daughters, per-plot elevation attribution, dump) · `civ_dump_render.py` (crop) · `civ_dump_map.py` (plan view) · `civ_variants.py` (skins) · `civ_roster.py` farm_terrace · `build_fix_round_1002.py` · `build_testrunner_0515.py` · `testrunner_src/pw_testrunner_p22.js` · `package_round_1003a.py` · `recheck_r1..r6.py` (the week's recheck).
