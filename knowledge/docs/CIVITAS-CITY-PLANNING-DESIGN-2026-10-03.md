# CIVITAS — CITY PLANNING DESIGN v1 (2026-10-03, 20:5x CT)

**Status:** design for the C1–C6 + D-C533 program (his 19:05 and 19:48 rulings). Built from four research reports in `_docs/civitas_research/` (R1 terrain planning, R2 economy and wages, R3 palaces, R4 Bedrock capacity) and a study of the shipped code (BP-02 1.3.219 draft: `pw_civ_clock.js`, `kit_block.js`, `pw_civ_streets.js`, `pw_civ_economy.js`, `pw_civ_land.js`, `civgen.py`). Everything marked **ASSUMPTION** is my call under "continue until all is ready"; each is logged in the decision journal and can be overridden by a word from Abs0lum. Nothing ships until the whole program is built and probed (his C6).

## 0. Scope echo

**In scope (built in this program):** sewer water + well shaft (D-C533); land preparation per plot (terrace, flatten, clear; stepped cuttings; stilted houses; no-build rule); hill benches joined by switchback roads (narrow, no sidewalks, no buildings); grid growth by tier with crossroads, corners and city blocks; districts; street widths 7 main / 5 side; the full tier ladder to metropolis II with very large, very expensive top tiers; a real material economy (quarried stone and felled timber actually consumed by construction; regional palettes; buying and selling; wages; a mint backed by production; imports along roads); a manor (town II), a city palace and a metropolis palace with hidden servant corridors, jib doors, back stairs, servants' quarters and apartments; public-servant jobs with wages; TestRunner witness commands; full BDS probe; packaging and delivery of complete packs.

**Out of scope (unchanged this round):** mob conversions, textures, trees, the thatch deck textures (flagged), the sewer lighting question (S1) until he answers — the design leaves room for either answer.

## 1. The growth ladder (C1, "very large and expensive")

Real anchors are in R1 §4.9; game targets are scaled by a compressive power law so that a metropolis II is ~450 buildings (the engine holds hundreds to low thousands of structures as records; only the loaded 144×144 window near a player is ever physical — R4 §3). Days are village days (the clock's `simDays`).

| Tier | Day ≥ | Buildings (cum.) | Streets (13-wide) | Grid | Citizens (record) | Embodied cap (PS5 / phone) | Civic additions |
|---|---|---|---|---|---|---|---|
| village | 0 | 12 | 1 main (+1 side by T when the main is full) | — | 24 | 24 / 16 | square, well, notice board |
| village II | 25 | 20 | 2–3 | T junctions | 40 | 24 / 16 | park |
| town | 60 | 35 | 4–6 | first **crossroads** at the square → first city blocks; streets widened to 7 | 70 | 32 / 20 | market stalls, guildhall-as-town-hall |
| town II | 120 | 60 | 6–8 | second parallel streets both sides, pitch 60 | 120 | 36 / 24 | **manor house**, chapel |
| city | 200 | 100 | 8–10 | 3×3 grid; **wall + gates** | 200 | 40 / 24 | church, 2nd market, stone town hall |
| upgraded city | 350 | 165 | 10–12 | 4×4 grid | 330 | 44 / 24 | **city palace** (seat of government), bridge, keep |
| metropolis I | 600 | 265 | 12–14 | 5×5 grid | 530 | 48 / 24 | cathedral, palace wing, inns, 2nd wall ring |
| metropolis II | 1000 | 450 | 14–16 | 6×6 grid | 900 | 48 / 24 | **metropolis palace** + commons + stables + guard/prison, 2nd bridge |

- **Citizens vs embodied.** Population becomes a ledger number (records per dwelling, `b.people`); villager *entities* are spawned only up to the embodied cap, nearest the player first, and keepers keep their stations (teleport when unseen). This is R4 §6.2's "embody few, simulate many" and is what makes a 450-building city possible on a Realm (sim distance 4). **ASSUMPTION A1.**
- **Expense.** Tier-up requires the tier's day AND the tier's *bill* paid: materials in stock and the construction wages affordable (section 4). The top three tiers need imported labour lodged at inns (R2 §5.7): a metropolis cannot be built from local hands alone, which is the intended expense. Cumulative cost to metropolis II ≈ 2.9 million coins' worth of wages and materials at R2's prices (ASSUMPTION A2: R2's tables, scaled to our 13-kind roster plus the new kinds).

## 2. Land preparation (C3, C5)

Units: blocks. H = the plot's sidewalk/floor level (the street's H at the slot). Relief is read from the settlement's site field (`pw_civ_land.js`), live ground where the field is unknown.

### 2.1 Plot rule (every slot, before it is taken)

For the plot box + a 1-block margin on the three non-street sides: `cut = max(ground) − H`, `fill = H − min(ground)`.

| Case | Rule | What is built |
|---|---|---|
| cut ≤ 3 and fill ≤ 3 | **accept** (one level) | existing terrace(): cobble retaining ring, dirt core, hill side clad; plus a 3-wide **back bench** levelled at H behind the house with its own retaining wall (ASSUMPTION A3: bench width 3 = Inca/Cinque Terre terrace width) |
| 3 < cut ≤ 6 | **stepped cutting** | first wall 3 high at the margin, a 3-wide bench at H+3, second wall up to the ground; the bench is grass with a fence line |
| 3 < fill ≤ 6 | **stilts** (his C5 b) | the house's 15-block subsurface box is kept, but every subsurface cell that stands above the real ground outside the basement shell is cut to air except log posts at the corners and every 4th cell; the basement shell (stone bricks) stays as the undercroft; a stair of stone-brick stairs from the street side |
| cut > 6 or fill > 6 | **no build** | the slot is skipped; that stretch of street is road only (his C5 a) |

The cut/fill limits are R1 §4.5 (single retaining wall ≤ 3; stepped above that; stilts for 4–6 of drop; nothing beyond). Every rejected slot is written to the chronicle with its numbers.

### 2.2 Clearing and flattening

- Trees over the plot and bench are felled (existing `clearOver`), floating leaves swept (existing job), snow layers and plants removed; the ground under a fill is never replaced where it is already solid (R4 §5.1: solid substitution).
- Street corridors keep the existing `kitPrep` (cut 3 above, fill below, cladding), with the uphill cladding extended to a stepped wall when the cut exceeds 3 (same rule as plots).

### 2.3 Benches and switchback roads (his C5 a)

- A **bench** is a stretch of land where a kit street of ≥ 46 cells can be laid (the DP profile finds a finite cost). The founding bench holds the square. When a settlement can neither grow a street nor open a side street (both planners fail), it looks for a **new bench** within 40–140 blocks of its edge at a different height and joins it with a **switchback road**.
- **Switchback road** = a narrow road (ASSUMPTION A4: 7-wide corridor — 1 curb + 5 road + 1 curb — his "thinner roads, no sidewalks"), scripted on the ground (cobblestone surface, his q1–q4 quarter ramps for every rise, cut/fill with cobblestone retaining faces ≤ 3), **no sewer, no buildings**. Its path is an axis-aligned polyline of legs joined by flat 7×7 corners; the planner enumerates L / Z / S shapes with legs from {14, 21, 28, 35, 42, 56} cells and scores each with the existing DP profile (ramps at 1 in 7; if nothing fits, 1 in 4 continuous quarter ramps as the "steep" option, logged). Leg separation ≥ 20 (R1 §4.6). The road starts at a street's dead end (the end curb opened) and ends at the new bench's first dead end.
- The new bench gets its own street system (main street, dead ends, outfalls, side streets) exactly like the founding bench — a hill town is several benches joined by switchbacks.

### 2.4 Switchback vs stair

Stair streets (walkers only) are not built this round: his C5 chose switchback roads or stilts. Logged as a later option.

## 3. The grid and the districts (C1, C4; C2 answered by research)

- **Street widths (C4):** main and through streets at town width (7 road), side streets at village width (5 road). Both are the same 13-wide corridor, so a side street can be widened later by re-laying pieces (existing `widenKit`).
- **Pitch between parallel streets: 60 centre to centre** (R1 §4.1: two 20-deep plots + yards + the 13 corridor = 59; inside the 35–80 m band of real pre-industrial blocks; his C2 was blank → **ASSUMPTION A5 = 60**, with 73 and 47 as fallbacks when 60 is blocked).
- **Cross streets every 60–90 cells** along a street; the first one opens at **town** at the junction opposite the square as a 4-way **crossroads** (the `cross13` piece), making the first city blocks; from then on the generator opens cross streets when a stretch's frontage is ≥ 80 % taken and longer than 90.
- **Corners:** a street that cannot continue (water, relief) and cannot dead-end usefully turns with the `elbow13` piece (ASSUMPTION A6: corners only on side streets and roads out; main streets stay straight).
- **Order of additions (R1 §4.2):** extend the main street → parallel street at pitch 60 → cross streets → second main street (grid) → faubourg beyond a gate.
- **Districts (from town):** assigned by a slot score, not hard zoning: *prestige ring* (within 60 of the square: town hall, inn, bakery, chapel/church, manor), *craft ring* (60–150: smithy, butcher, lumberyard, brickworks), *gate ring / noxious band* (the last 60 before the edge and outside: quarry, lime kiln, tannery-class trades, cattle), *fields* (farms outside the last street on the downhill side, one farm plot per 6 dwellings). Each family carries a `district` tag; `kitSlot` prefers frontage in that ring and falls back outward.
- **Walls and gates:** at city the wall ring is built around the grid's bounding box + 8 with a gate on every street that leaves it (adapting the legacy `buildWall` to kit streets); metropolis I adds the second ring.

## 4. The material economy and wages (C3)

Adopted from R2 §5 and reduced to what the shipped roster can consume. All pure functions in `pw_civ_economy.js` (node-testable), the clock calls `dayStep` once per village day as now.

### 4.1 Units
- Ledger unit = **penny (p)**; 12 p = 1 gold coin item (`pw:gold_coin`); a game day of work = 24 historical labour-days ("a game day is a working month").
- **Materials:** stone, lime, timber, planks, thatch, clay/brick (from town II), iron, glass (city+), food (raw), rations, tools.

### 4.2 What a building really costs
- The **bill of materials is read from the template itself**: `civ_village_data.py` counts each template's blocks by class (stone-class: cobblestone, stone bricks, smooth stone; timber-class: logs; plank-class: planks, doors, stairs of wood; thatch/roof-class: pw:thatch*, pw:roof*; glass; iron) and divides by 8 (ASSUMPTION A7: one material unit = 8 blocks = one cartload). Labour = R2 §5.6 worker-days per class of building (cottage 5 WD … palace wing 5,000 + 30,000 finishing).
- Each stage consumes its share when it is placed: s1 frame = timber; s2 walls = planks or stone; s3 roof = thatch/planks; s4 furnishing = planks + iron + glass; and pays that stage's wages. **A stage whose materials or wages are not on hand waits** (the chronicle says why), which is the whole point: cities are slow because stone and coin are.

### 4.3 Production, wages, prices (per game day)
From R2 §5.3–5.5: quarryman 48 stone/day, woodcutter 24 timber, sawyer pair 96 planks, farmer 16 raw food, baker/butcher 96 rations, lime kiln 100 lime from 100 stone + 50 timber, smith 8 toolsets. Wages: labourer/carter 72 p (6 coins), farmer 60, quarryman 84, baker/butcher/innkeeper/sawyer 96, mason/carpenter/smith 120, clerk/finisher 144, master mason 192, hired outsider ×1.5 lodged at an inn (10 beds per inn). Ration 36 p/day per person. Prices move by `base × clamp(sqrt(target/stock), 0.5, 3)`.

### 4.4 Regional materials (mountains → stone, forests → wood)
Nothing is scripted by biome. Every building has **palette variants** (timber/thatch, stone/thatch, stone/plank, brick later) and the settlement builds the **cheapest delivered variant**: local stone is 2 p at the quarry and doubles every 12 game-miles (1,200 blocks) of carting; timber likewise (R2 §5.2). A quarry on stony/mountain ground produces more (the existing `digQuarry` pit grows); a lumberyard in forest produces more (trees actually felled by the existing `clearForest` / BIGCANOPY counts). So a mountain village turns stone and a forest village turns timber by cost, and a settlement that opens a road to a quarry town changes its look. Palettes are applied at placement by editing the template in memory (`Structure.setBlockPermutation`, R4 §1.3) with a wall-class map (planks → stone bricks / cobblestone), never touching framing or roof blocks (ASSUMPTION A8).

### 4.5 The money loop
Pay wages (treasury → citizens) → households buy rations and tools (→ tills) → shops buy inputs (→ farms, quarry, lumberyard) → treasury takes a 2 % toll + stallage + hearth tax → construction buys materials and pays site wages → the **mint** issues pennies against real production (≤ 50 % of the last 10 days' output value, ≤ 5 % of money in circulation per day; every minting is a ledger line; the player's `pw:gold_coin` purse is the only coin that exists as an item). Anti-deadlock (R2 §5.9): batched bills per site, two stock lines (consumption vs construction reserve), imports by caravan along roads when a material is short 3 days (delivered price by distance), wage-arrears pause after 3 days with a reserve sale, statute labour (4 WD/household/year) for walls, roads and bridges only, hired labour gated by inns, a hard ledger invariant checked daily.

### 4.6 Public servants and jobs
Town hall (clerk), manor (steward, bailiff), palace (treasurer, chancery clerks, constable, porter, steward, butler, housekeeper, cook, grooms, guards) — keeper-style villagers at stations, paid from the treasury, buying rations like everyone: symbolic offices that move money (his words). Their stations are markers inside the structures; the economy pays by role.

## 5. The palace program (C3)

From R3 §5 (dimensioned from Versailles, Hampton Court, the Doge's Palace, Kerr 1865). Built with `civgen.py` as 64×64 pieces, each a plot with the usual five stages, placed as a group on a reserved block of the grid (the palace block = highest ground within 150 of the square, else the square's long side).

| Building | Tier | Footprint | Pieces | Hidden world | Jobs (stations) |
|---|---|---|---|---|---|
| Manor house | town II | 56×44 | 1 | rear service corridor 2 wide with jib doors to hall, parlour, dining; back stair; baize door; 6 attic servants' rooms | steward (lectern), cook, housekeeper, groom, smith |
| City palace | upgraded city | 128×128 | 4 | 110-long hidden spine corridor behind the state rooms, jib door into every room, 3 back stairs, Tesoretto strongroom behind a painting, prison tower (Pozzi / Piombi), judges' wardrobe door, 16 garrets, 18 three-room apartments + 24 two-room lodgings | treasurer, 4 chancery clerks, constable, guards, porter, cook ×2, laundry, smith, steward, butler, housekeeper |
| Metropolis palace | metropolis II (wings from metropolis I) | 256×192 + 3 annexes (commons 64×64, stables 64×24, guard & prison 64×32) | 12 + 3 | 73×11×12 grand gallery, the 1789 escape route (jib door left of the consort's bed → private cabinets → 2-wide passage → ruler's bedchamber), 128-long spine corridors on 3 floors, 40 three-room apartments, ~100 lodgings in the commons, 128 garrets, exchequer with the chequered table and strongroom, chancery with 12 lecterns, courts, chapel, theatre | ~25 stations (R3 §5.7) |

Jib doors = a door of the wall's own plank species with no frame; the baize door = a warped door in green wool; bells = buttons → redstone in the spine → bell blocks on a board in the servants' hall (R3 §5.2). ASSUMPTION A9: rooms are generated from the R3 tables by a room-program builder (walls, floors, doors, corridors, stairs, furniture by room type) rather than hand-placed block by block; the output is checked by renders and the probe.

## 6. Sewer water and the well (D-C533)

Baked into every well template: a stone-brick-lined 1×1 shaft of water sources from the well bottom to y1 of the box (the sewer trench level). Scripted: a 1-wide lined water channel at trench level from the shaft to the nearest street trench; every laid street piece gets a water source in the lower trench cell along its length (ramps: the cell above the trench floor at each t); the outfall tunnel re-cut as a 1-wide water channel between two 1-wide ledges; the exit opening 1×2 with a stand-in iron-bar grate if the BDS shows water passing through bars (else bars in the upper cell only). The sewer-lighting question (S1) stays open; the pieces are not changed until he answers.

## 7. Engine architecture (R4)

- **Records + materialisation.** Every physical change is a queued op bound to a 16×16 cell; ops run only when the cell's chunk is loaded (existing `kitQueue` + stage placement extended to plots' land-prep, roads, walls and palaces), under budgets: ≤ 1 structure placement per tick, ≤ 120 block edits per tick on PS5 (40 on a phone), one master job. Catch-up on load replays the net state, not every intermediate stage.
- **Time** from `world.getDay()` as now; elapsed days computed from the world clock so unloaded time counts.
- **State** in chunked dynamic properties (30,000 chars each); a 450-building city ≈ 100 KB.
- **Entities** per the embodied cap; keepers teleport when unseen (existing); citizens are records.

## 8. Phased build plan with tests (stopping points)

| Phase | Work | Tests | Stopping point |
|---|---|---|---|
| A0 | sewer water + well shaft + outfall channel + grate stand-in | BDS: water in every trench cell, outfall spilling, iron-bar flow test | topmap + section renders |
| A1 | plot rule (cut/fill), back bench, stepped cuttings, stilts, no-build | node tests on synthetic slopes; BDS hill site: every plot's cut/fill within limits, 0 floating | renders of a stilt house and a stepped cutting |
| A2 | benches + switchback roads (polyline planner, narrow road, corners) | node tests (profile, grades ≤ 1:7, legs ≥ 20 apart); BDS: a second bench reached and built | topmap with the switchback |
| B | pitch 60, crossroads at town, blocks, districts, corners, kit walls + gates, tiers 6–8 tables | node tests; BDS ladder village → city with the grid and wall | topmap at city |
| C | economy v2 (pennies, wages, BOM from templates, stage consumption, mint, imports, palettes) | `test_economy.mjs` v2: invariant holds 100 days; BDS: stages wait for stone, a mountain village turns stone | ledger printout + renders |
| D | manor, city palace, metropolis palace generators; public servants | structure audits (markers, doors, corridors connected); BDS placement; render walkthrough | renders of the palace |
| E | TestRunner witness commands, full ladder probe to metropolis II (accelerated), packaging, md5 delivery, handoff | the whole ladder in one BDS run; 0 ERROR; molang 0 | delivery |

Progress messages every few minutes; a journal entry per decision; the design is re-read at every phase start.

## 9. Open questions for Abs0lum (answers change nothing already built)

```
S1. Sewer lighting: lanterns baked into the pieces so nothing spawns inside / leave dark (monsters in the sewers are a feature) / other:
S2. Stand-in grate until yours exists: iron bars = ok / leave the opening empty:
C2. Block size between parallel streets: 60 (research) = ok / other number:
A4. Switchback road width: 7 (curb + 5 road + curb) = ok / other:
A8. Regional look by cost (mountain villages turn stone because stone is cheap there) = ok / hard biome rule instead:
```

---

# v1.1 ADDENDUM (2026-10-03, 23:1x CT) — rulings D-C535 … D-C543 folded into the program

## 10. The 13-tier ladder and representation (D-C535)
- Tiers: village I–III → town I–III → city I–III → metropolis I–III → **Port City / Capital City** (the role a top city holds; 5–10 thousand people). Plural: metropolises.
- Day / cumulative-building / population gates: 0/12/24 · 25/20/40 · 50/28/60 · 80/40/100 · 120/55/160 · 170/75/250 · 230/100/400 · 300/135/650 · 380/175/1000 · 480/230/1600 · 600/300/2600 · 750/380/4000 · 950/500/5000–10000. People per dwelling rise with the tier (tenements, apartments) — DENSITY by class.
- **Representation** (the city condition): partners with a stand or branch on OUR square (presence ladder rung ≥ 2). city I ≥ 2 partners · city II ≥ 3 · city III ≥ 4 (≥ 1 town+) · metropolis I ≥ 6 (≥ 1 city) · II ≥ 8 (≥ 2 cities) · III ≥ 10 (≥ 3 cities) · port/capital ≥ 14 with ≥ 2 metropolises. Higher-income towns (their goods in demand elsewhere) open stands in other towns; caravans up to 3 hops carry the goods.
- The tier-up is an **unlock**, never an appearance (§13).

## 11. The census: relationships, happiness, gossip (D-C536)
- `pw_civ_people.js` (pure, 16 node checks): people as records per settlement — name, sex, born, home, job, spouse, parents, children, friends with fondness, mood, rumours known. Daily: aging dials (child 10, apprentice 20, elder 120, death 130 + span 30), contacts (household, workmates, the square) raise fondness, decay otherwise; weddings at fondness ≥ 60, births in homes with room, deaths of elders, inheritance kin → closest friend → the town; mood from fed / housed / employed / paid / friends / family / grief; migration (10 low-mood days → leaves; the Immigrant Faucet brings newcomers to a happy town with room); rumours spread at foot speed; threads with a default course on their deadline; the keeper greets the player by fondness tier (stranger / customer / friend); a notice board.
- Utopia-First: no crime, theft or doctored books in this set.

## 12. The background law — real ticking, not records (D-C537 → D-C542)
- Every settlement advances with the WORLD's clock. Days are processed in **whole-day slices** (the budget, wages and hiring are daily): at most 5 per clock beat, the rest carried in `s.lag` and worked off one per beat (also how `skip` works in the harness; a paused clock still owes its skipped days).
- D-C542 supersedes the "abstract rate while unloaded" compromise: **no abstract production anywhere**. Work only happens where chunks tick. The clock keeps each working settlement's **core** (pit, wood stand, storehouse, active build sites, bakery) in a ticking area (engine limit: 10 areas, ≤ 100 chunks each); settlements beyond the slots wait their turn by day. Slot counts per host (PS5 single-player vs Realm/BDS) are MEASURED on the test server before they become law. 1 settlement day = 1 world day; acceleration is a harness command only.

## 13. The embodied economy — hands vs census (D-C541, D-C542)
- Throughput is exactly what embodied workers do: 1 block per swing at the quarry face, 1 load per trip to the storehouse chests (the chests are the stock; the ledger mirrors their sum), 1 loaf per bake, stage slices laid only while a builder stands at the site in working hours.
- Day schedule for every embodied villager (home at night, workplace by day, market at midday, square/inn at dusk). Purchases at counters (bread leaves the bakery's chest, coins move).
- A tier-up = the unlock of the next plan + new posts + new households; nothing appears until built.
- Embodied = the posts whose work has visible output now, up to the device cap; the census (§11) produces nothing by itself.
- Engine route (ASSUMPTION): a `pw:citizen` entity with task component groups driven by `minecraft:behavior.move_to_block` toward task-marker blocks (quarry face, storehouse chest, build-site flag), `on_reach` → the clock does the work beat (break the block → the citizen's inventory → the chest → the ledger).

## 14. Phase F — planning research, stewardship, manholes, the key, patrols (D-C538, D-C539)
- F1 research R5: medieval→Renaissance planning + conservation (greenbelts, coppice cycles, wetlands, dark-sky lighting, wildlife crossings) → addendum v1.2.
- F2 stewardship: spent quarry strata re-green; a sapling per felled tree (forester job); a greenbelt ring outside the walls stays unbuilt; cut spoil spread, no heaps.
- F3 manholes: a `pw:manhole_cover` in the sidewalk about every 26 cells of straight street over a 1×1 ladder shaft to the hall floor (a scripted op like the well drain; kit pieces untouched); cellar manholes keep working.
- F4 the key: `pw:sewer_key` — **tracked register assets, not craftable** (D-C539): one record per key {id, settlement, holder, issued, custody}; minted only when a sewer-trade post is filled, returned on death/retirement, reassigned by the register (never to kin); the hatch law: from above opens only with a key registered to that settlement ("The lock doesn't know this key." otherwise), from below as today, auto-close ~15 s with an empty shaft. No purchase path for the player; keys reach the player only through the world's own events — quest-driven items without quests. Observation mode first: the cities develop without the player.
- F5 patrols: `pw:watch` guards from town I, more per tier; routes = street cells (night) + sewer hall cells; the lamplighter lights the hall every 8 cells; patrol density as the spawn-pressure dial.

## 15. Phase F6 — roads between settlements as green corridors (D-C540)
- A fence 3 high along both curbs of every inter-settlement road, joined to gates/walls: a closed channel gate to gate.
- Wildlife crossings about every 80 cells and where the road cuts a forest or skirts water: in a cutting → a grass-topped **overpass** 5 wide, 5 above the road, 4-part dirt/grass ramps, 3-high fences on its edges; on an embankment / flat land → a grass-floored **underpass** 5 wide × 4 high (stone-brick abutments), the road ramping 5 over 20 cells where flat. Alternate when the relief is indifferent.
- Economic tie-in: caravans and representation traders travel the fenced roads; a safe-road factor in the ledger (no attrition).

## 16. Phase G — mob scaling and damage (D-C543)
- Census (680 entity files; `_docs/mobs/MOB-SCALE-CENSUS-2026-10-03.json`): 60 giants at median 8.0× (2.4–24.7×) their base; 389 of 427 hostile-flagged mobs are shorter than the player, 121 of them hit for ≥ 5.
- Rule: every giant = 2.5× its base's effective height (the 10 without a base: 2.5× the smallest same-species base), giant damage = base + 2; every hostile shorter than the player: damage ≤ 2, attack cooldown doubled; nothing changes at or above player height. Shells scale with the body (verify RP-07 has no separate shell bone). Before/after table shown before shipping.
- Hardness scale (blocks vs tool tiers): backlog audit, not now.

## 17. Phase order (revised)
A0 ✓ → A1 ✓ → A2 (bench roads: hairpin family, in test) → B (grid: side streets ✓, blocks closing, walls at city I) → C (economy v2 ✓ ledger) → **C2 embodied economy** → D (manor, palaces, public servants) → **F** (stewardship, manholes, key register, patrols) → **F6** (green corridors) → **G** (mob pass) → E (TestRunner, full ladder probe, delivery, handoff). Research R5 runs alongside.

## 18. Roads, streets and the hill (D-C544 … D-C547, 23:1x–23:5x)
- **Narrow roads climb 1 in 4** (his 4-part ramp over 4 cells; `ROAD_RAMP`), cut ≤ 6, fill ≤ 4 and beyond that a **deck** (a viaduct that may itself slope), spans unlimited by the profile, 24 in the shape pass. The planner = a shape pass (straight / L / Z / U / switchback / hairpin families, cheap filters, exact profile) then a **lattice A\*** over (cell, heading, road height) on the 4-cell ramp unit with turns priced as flat elbows, the result profiled exactly. Offline harness: `test_road_site.mjs` + `civ_height_render.py` on the run's exported heightmap (`[CIVHEIGHT]`).
- **Streets are capped** at cut 6 / fill 6 (0.0.14 cut a parallel 50 deep through a mountain with stepped faces 60 cells out). A street that cannot be held inside the caps is not opened; benches, climbing legs, stilts and podiums carry growth onto the hill.
- **Grid pitch 56**, parallels opened as long as the land allows (halves 70 / 55 / 40) so a fresh parallel already carries the next cross-line windows; block closing then has pairs to join. Neighbourhood centres from town II (B2).
- **The stepped town (B3)**: terrace streets along the contour one per storey, 7-wide 1-in-4 climbing legs between their windows (the switchback along the main road), stair alleys mid-block, uphill parcels cut in / downhill parcels on podiums or stilts.
- **Benches**: either end of a bench street may receive the road; an end whose 7 approach cells stand more than 6 above it is not offered; a departure facing a hillside is skipped.
- **Sewer exits v2 (A0.2)**: the drainage graph per settlement, exits at its low points, targets ranked water > lower face > soakaway, one trunk per network minimum, the rest sealed, the trunk floor falling toward the mouth, re-solved on growth.

---

# v1.2 ADDENDUM (2026-10-04, 04:1x CT) — built for build 23 (rulings D-C547 … D-C554)

## 19. Sewer exits v2 (A0.2; D-C547, D-C549)
- **Networks**: streets whose corridors touch share one sewer (tees, crossroads, connectors); a bridge splits it (no
  substructure); a bench is its own network; climbing legs carry none. Floor of a cell = sidewalk H − 13.
- **Low points**: every local-minimum plateau of the floor gets ONE exit; all other dead ends stay sealed. A low point
  with a dead end: a TRUNK from the dead end — open water within 120 (surface below the floor) is preferred, then a
  hillside face within 72, shortest first; the trunk never runs through house frontage (16 cells beside a flat stretch).
  A low point inside a street (a valley), or one with no daylight in reach: a SOAKAWAY pit under the trench (3 × 3,
  8 deep, gravel in its lower half, cobblestone lining).
- **The trunk**: its floor falls toward the mouth in one-block steps at least 7 cells apart, never below one above the
  water or the ground at the mouth; a source at the head of every level stretch (water spreads 7 cells on Bedrock),
  so the water runs; lanterns every 12 cells; a manhole every 26 cells where open ground stands 2+ above the vault; the
  mouth framed in stone bricks with a waterlogged grate (plain bars stop water; waterlogged ones spill — R-1).
- **Re-solved** after every change (one decision op at the back of the queue); an exit that no longer serves a low point
  is back-filled. Tests: `test_drain.mjs` (23 checks); BDS 0.0.22: 4 trunks + 5 soakaways, 3/4 mouths spill, pits wet.

## 20. Walking v2 / v3 (C2.1)
- Off the street graph a villager follows a straight leg to the nearest graph cell (v2), now a LOCAL PATH over the real
  blocks (v3: A* on feet cells, steps of 1, doors yes, fences and walls no; 7 node checks). A walker stuck at the same
  target backs off (0 / 0 / 1 / 2 / 4 minutes); each stuck walk is classified (direct / below / above / level).
- Streets guard their downhill edge: a drop of 2–3 becomes a berm, a deeper one a retaining wall + parapet (R-6).

## 21. People that live on (D-C536)
- Households arrive with two adults (20–59) and children (0–14); a family home may hold 2 more than its places for
  children; grown children move out to free rooms; newcomers need two free places (one cradle stays free). Keepers
  live at their shops. 600 simulated days: 20–34 people on 28 places, steady.
- Bodies follow the census: the dead and the departed leave the world; post holders without a body (watch, sewer
  keeper, surveyor, builders) are embodied at their door (3 a day, 48 per settlement).

## 22. Patrols (F5; D-C538)
- The WATCH (village III 1, town I 2, town II 3, town III 4, city I 6, then +2 per tier) walks the streets at night stop to
  stop (every 24 cells + the square), and goes BELOW where a street has two laid manholes: it opens the cover with its
  registered key (the watch is a key post), climbs down the shaft (scripted rungs: villagers don't path on ladders), walks
  the hall's side lane to the next manhole, climbs up and locks behind it; a round below that stalls walks back.
  The SEWER KEEPER does the rounds below by day. Monsters within 3 are struck (6 every second), within 16 chased (above
  ground). Counters: rounds, below, climbs, seen, strikes, kills (the spawn-pressure dial).

## 23. Civic works and sanitation (F7; D-C549)
- Works by tier: village base (well, sewer) · village III midden carter (office) · town I latrine + cistern · town III
  bathhouse + lamplighter (office) · city I well-house + infirmary · city III hospital + fountain · metropolis
  waterworks + ward. Built with the tier's plots as stand-ins (no households live in them) until real designs exist (Q12).
- The next natural tier waits until the works stand. SANITATION = works standing / works due: mood ± ((s − 0.7) × 20),
  death chance × (1 + 0.6 (1 − s)); an infirmary with a healer × 0.7.

## 24. Stewardship (F2)
- The quarry's spent rim re-greens from its spoil (grass, now and then a flower), a few cells a day; a sapling beside
  every felled tree (C2.2); once the wall stands, a 24-wide GREENBELT outside it stays unbuilt (benches excepted).

## 25. Neighbourhood centres (B2; his 23:30) and the counter (C2.4)
- From town II every parallel street grows a small market: a well near its middle, a bakery and a butcher beside it;
  its households take midday and dusk there instead of the main square.
- At midday one person of each household walks to the food shop it trusts most for its distance (its own
  neighbourhood's first) and buys one loaf or cut from the shop's chest (stocked each real morning from the day's
  bread / meat); an empty counter lowers that trust and makes a rumour (D-C550's learning, now with a body).

## 26. The boundary ring follows need (B4)
- Each tier carries the ring at least 32 further out; a street or side street held back by the stones three times
  makes the council send the surveyor out one more step of 16 (R-13: a ring larger than its schedule froze growth).

---
# v1.3 addendum (2026-10-04, 05:00–07:00 — runs 0.0.24 … 0.0.26; RESULTS R-22 … R-41)

## 27. Walking v4: every walker follows ITS OWN lead (R-31)
- A walker holds a SLOT (0–47, the embodied cap). Its lead entity carries the slot as the int property `pw:slot`; the
  villager's follow group `pw:lead_<slot>` follows only a lead whose `pw:slot` equals it (`int_property` filter). Before
  this, follow_mob took any lead within 48 blocks: with a dozen walkers at once they chased each other's carrots.
- Route heights are checked against the blocks (the standing place within 3 of each waypoint) the first time the lead
  goes there; the walker joins the graph at a cell within 2 of its own height first; a walker with no progress for 30 s
  is helped once onto its current route cell (a two-deep hollow cannot be jumped out of); leads no walk owns are removed
  every 10 s (a reload empties the walk table, the leads persisted).
- The walk instrument (`clock walktest`) traces chosen walks and dumps the blocks at every stall — the tool that found
  the three causes above.

## 28. Room for the plots (R-22, R-33, R-36)
- The side-street search is a background JOB (system.runJob, a yield after every profile): no tick carries more than one
  plan; a town with plots waiting keeps one job going (one new street a day at most). A full scan that opens nothing
  rests 3 days, lifted when the boundary stones move.
- Up to 3 waiting plots a day; the MANOR jumps the queue; the tier's CIVIC WORKS are laid out FIRST at a tier-up and a
  work without room is retried every day (never lost); the neighbourhood centres are retried every 4 days.
- Narrow roads (7 wide) are in the plot veto; a street end with a bench road leaving it no longer grows.

## 29. Building economy (R-41, R-42)
- A crew with its whole day free takes on a stage bigger than its day and works it off over the next days (a debt from
  the next budgets) — two founders can raise an 86-block cottage.
- The settlers' wagons carry the bill of the WHOLE founding plan (the plots that fit and the ones still waiting).

## 30. Quarry pits and the coppice (R-24, R-38)
- A quarry digs on up to six pit SITES around it (behind, beside, further behind), each judged before it opens (no plot
  or street in it; the most rock above its floor; its top = the median ground); sleeping land is asked for and waited
  for; one change a day; all six spent → the quarry is WORKED OUT and the shortage charters a new one.
- A woodcutter with no tree in reach plants a COPPICE: saplings on a 3-block grid on free grass 6–16 from the yard (24
  standing at most), the kind of the last tree he felled.

## 31. Ticking areas (R-30, R-32)
- Laid on chunk edges, at most 10 × 10 chunks (an unaligned 160-block box is 11 × 11 = 121 chunks — refused silently by
  the engine); the refusal is detected; a job keeps an area busy only when the area covers the whole box it needs; a
  sewer job whose land stays asleep 600 beats waits outside the queue and comes back every 3 days.

## 32. Bodies (R-26, R-35)
- Bodies go to the posts first (watch, sewer keeper, surveyor, builders), then one SHOPPER per household (its first grown
  member with no post and no shop), 12 bodies held in reserve for the posts; a post holder needing a body takes a
  shopper's. The counters are filled each real morning, or at the first market hour after skipped days.
