# FRONTAGE PLATEAUS — 1.3.230 (PL)

**Status:** source only, in `tools/bp02_src_228`. Not built, not packaged, not run on a server.
Static and node checks only (P1: nothing here is witnessed).

**Backlog item:** owner, "frontage plateau". The gate logs said:

- "23 more cottage_m would fit along 4 streets (475 cells of frontage of 722)"
- "SPRAWL on hills — 9 streets for 22 buildings … houses need flat frontage → terraced platforms / flattening needed. Park not placed (no flat 15-cell frontage)"

**Kept intact:** the Households & Dynasty change (`1.3.230 (HD)`), the dayStep town-posts fix and the stepEconomy ledger guard.

- `pw_civ_people.js` is byte-identical (md5 `0561896d`).
- In `pw_civ_clock.js` the diff against the pre-change copy (`_garbage/plateau-pre/`) touches only the lines listed under "Changed functions".
- The HD tag count is unchanged.
- The `!st.ledger && st.phase !== "built"` guard is still present.

---

## 1. Mechanism

When a street side is too steep for a plot's flat footprint, the planner may cut and fill a level **pad** (a plateau) for that plot.

### Pad height

- The pad stands at the street's height at the door, or one step above it.
- It is never below any sidewalk cell of its frontage: the floor is the highest sidewalk cell, as in the 1.3.225 law.
- A plateau frontage may rise **2** along the house. The old limit is 1.
  - The door must be within **1** of the floor.
  - The house's sewer link (hatch or branch) must be within **1** of the floor. That keeps the existing rule of at least 3 shared rows with the hall.

### The pad itself

- The pad is the house's 1-cell **ring**: both side gaps and the rear row.
- The house box needs no work. The structure does its own cut (air) and fill (subsurface down to feet −15).
- The ring is levelled to P:
  - cut above P, with trees over it felled (clearing stops at a plot's box plus its margin);
  - filled below P with local ground (GB9 palette).

### Downhill: retaining walls and berms

- A ring cell whose outside lies 2 or more below the pad becomes a **stone-brick retaining wall**, from the outside ground + 1 up to P − 1, with the pad's top on it.
- A drop of more than one lift gets **berm lifts** beyond the ring, with tops at P − 3 and then P − 6. This is the R5 rule (walls of 3 or less) and the same rule as `stepBerm`.
- A berm stops where the ground meets the lift within one block.

### Uphill: cut faces in lifts

- The hill beyond the ring is cut in **lifts**: one lift of 3 or less per cell of setback, the same rule as `stepBerm`.
- Row *j* is cut down to P + 3*j*, and its face is clad in stone bricks.
- The first row whose ground lies inside its lift is clad only, not cut. The natural ground continues from there.
- A hill still above the last lift after `faceLifts` (3) rows refuses the plateau. It would overtop the wall.

### Never-into rules

| What a worked cell meets | Ring cell | Face row | Berm |
|---|---|---|---|
| another plot (or the crown's reserve) | refused | the face stops there (the neighbour's box holds the hill) | refused (next to the ring: the neighbour abuts and no berm is needed) |
| a street (corridor, road, tunnel, legacy street) | refused | the face stops there | refused |
| water | refused | refused | refused |
| a protected tree | — | refused | refused |

- A **protected tree** is a trunk standing on the ground *outside the pad*.
- The build job reads trunks from the live world. Plan time sees only the height field, so trees are caught at build time and the job falls back.
- Standing water inside the box is allowed up to the TR2 share (8 %). The existing `plotDrain` seals it.

### Drainage (the water law: "water can't be stopped, only moved")

- A **gravel gutter** on a cobblestone bed runs along the foot of the cut face (the rear ring row, plus a faced far side) and down one side ring to the street.
- At the street end of that side ring sits a **grated drop** (iron bars at P, open shaft below).
- The drop falls to the sewer hall's two top rows, H − 9 .. H − 8.
  - Under some ramp pieces the hall sits one block lower. The two rows cover both cases.
  - The rows lie inside the H − 11 .. H − 8 rows a house branch already carves.
- The drop joins the hall through the corridor's side wall: 4 cells × 2 rows. Only `BRANCH_CUT` materials are carved, the same as `carveBranch`.
- Choosing the drain side, in order:
  1. a street end not above the pad;
  2. an end with a sewer hall (a flat or ramp cell outside every junction window — never a bridge, a dead end or a window);
  3. a gap not shared with a built neighbour;
  4. the lower street end;
  5. q = −1.
- No hall at either end → a **soakaway**: an 8-deep pit with a gravel lower half under the grate. This mirrors the sewer's own soakaway fallback.

### Cost

- **Stone:** retaining walls, clad faces, berm faces, and the gutter (gravel + cobble bed) all count as `stone`. One iron grate counts as `iron`.
- **Earth:** the earth moved (cut + fill volume) becomes labourer days at `earthPerDay` = 80 cells per day, paid at `WAGE.labourer` = 72.
- All of it is added to the plot's **first paid stage bill**, the frame (stage 1). The plot stage itself (0) is labour only and never billed.
  - Stone + iron go into the materials and the builders' block count.
  - The builder days are recomputed.
  - The labourers' wages are added on top.
- The founding wagons (`genesisStock`) also carry the founding plateaus' stone and iron.
- **The park** has no stage bill. Its terrace is paid from the ledger as far as the stores and the treasury allow, and logged.

### Where it is tried: search phase 1

The search runs one phase per beat (1.3.227). The plateau pass is the new phase 1, after the normal street search fails and before anything sprawls. The later phases each moved up by one.

| Phase | Search |
|---|---|
| 0 | the streets (+ a business's conversion in the core) |
| **1** | **plateaus on the existing streets (new)** |
| 2 | lanes (homes) |
| 3 | grow a street |
| 4 | open a new lane (homes) |
| 5 | stilts |
| 6 | side-street job |

- Inside phase 1, the existing land kinds keep every lot they already take: level, stepped, podium, embankment, stilts.
- A plateau is judged only where `slotRelief` says reject, or where the frontage rises 2.
- The one-street path (`kitAddPlot` with `only`, used by the B2 centres) tries the street, then a plateau on it.

### The park

- `kitPark` first tries the old level frontage, unchanged.
- If none exists, it takes a **plateau frontage**: a rise of 2 or less, the gate (the frontage's middle) within one step.
- The park's own box may be filled up to the fill dial, since the park has no subsurface.
- `layPark` lays the green as before, then starts the plateau job for its ring, walls, faces and drain.

### Build time

- After the house's plot stage is placed, `kitLandPrep` skips the old rear bench and stepped face (as it does for stilts), and `placeStage` skips the old `terrace()` ring.
- It starts `plateauJob` instead, a generator for `system.runJob`:
  1. **Read the live ground.** It reads every cell the plan can ask for (the ring, the face and berm rays, ≤ 5 rows out) through the guarded API only (`topAt` / `groundAt` / `blockAt`: chunk-checked, no throws, no `below()`), and yields every 48 reads.
     - A sleeping chunk → it waits up to 20 tries of about 5 s.
     - Still asleep after that → the fallback.
  2. **Plan again.** It re-runs `PLAN.planPlateau` on that live ground (`skipBox`: the house stands).
     - Refused (a tree, changed ground) → the fallback: the old `terrace()` ring.
     - The result is recorded as `b.plateauDone`.
  3. **Apply the operations.** It applies the ops, yielding every 120 ops. It never cuts a worked block (a neighbour's wall, a path), never fills water, and never writes inside the house's box.
- A chronicle line is written when a plateau is planned (`makeKitPlot`) and when it is cut (the job).

### Census

- `pw:clock frontage` now counts a position refused for its rise or its land as a fit when a plateau would take it.
- The reply adds "; N of them on PLATEAUS".

---

## 2. Dials

All dials are in `PLAN.PLATEAU` (`pw_civ_plan.js`).

| Dial | Value | Meaning |
|---|---|---|
| `cutMax` | 6 | the deepest cut of the pad (box + ring) |
| `fillMax` | 6 | the deepest fill of the ring; also the deepest drop just outside a ring cell, and the park's box fill |
| `lift` | 3 | one retaining wall's height (R5) |
| `faceLifts` | 3 | uphill lifts beyond the ring (a face of up to 9) |
| `frontRise` | 2 | the frontage rise a plateau accepts (the old law: 1) |
| `doorStep` | 1 | the door is at most one step below the floor |
| `boxDrop` | 12 | the deepest hollow under a house's box (its subsurface reaches feet −15) |
| `earthPerDay` | 80 | earth cells one labourer moves a day |
| `wageLabour` | 72 | = `ECON.WAGE.labourer` |
| `soakDepth` | 8 | soakaway depth (= `KIT.SOAK_DEPTH`) |
| `hallTop` | 8 | the hall's top row is H − 8 (the link spans H − 9 .. H − 8) |

---

## 3. Tests

The new suite is `tests/test_plateau.mjs`: **76 checks**.

### Red before

There are two layers, both run against the `_garbage/plateau-pre/` sources in a scratch copy:

- Against the pre-change sources, the suite crashes at the first check (`PLATEAU` undefined).
- With the new pure files and the old clock, it crashes in the clock section (`streetRing` is not defined).

### Green after

The suite passes 76/76. What it covers:

| Area | Checks |
|---|---|
| pad height | level; rise 2 with step 0 / 1; door 2 below → refused; rise 3 → refused; an unknown cell → refused |
| planner basics | flat (27 ring cells, nothing in the box, a sewer outlet with a 4 × 2 link, earth 0); the uphill 0.6 lot (the old law's cut over box + ring + bench = 7 → rejected; the plateau takes it with pad cut 5); every lift is 3 or less; every face is cut to min(ground, P + 3·row) |
| volumes and bill | cut and fill volumes and the bill's stone recomputed by hand; labour = ceil(earth / 80) × 72 |
| steep cases | 1.6 per cell → cut; a cut pad under a 2-per-cell hill → cut; an uncut pad under a natural rise → its first step only is clad |
| cross slope | cut 5 / fill 5 (the old law: both > 3 → reject); downhill walls; one berm lift where needed; none where the ground is within one of the lift; an uphill clad face |
| never-into | a berm into a street → refused; into water → refused; a face through a tree → refused; a tree beyond the works → no effect; a face meeting a plot → stops; a wet / plot / unread ring cell → refused; `skipBox` |
| drain | the lower end; the run is contiguous and outside the box; it starts at the face's far corner; the drop + link rows; never toward a higher end; a soakaway when there is no hall; a gap not shared with a neighbour is preferred |
| bill helper | `plateauBillInto` (stone, iron, builder days, wages; a fresh object; no change without a plateau) |
| slot search | `KIT.placeAlong` with `opts.riseMax`: a 1-in-4 street fits 0 houses under the old law and ≥ 4 on plateaus; each slot is marked with rise 2, floor = max, door within 1, sewer link within 1, and carries `Hring`; a gentle street gives the same slot with or without the option |
| park | no level 15-cell frontage, a plateau one exists, and its plan is OK with the box fill dial |
| clock, run on stand-ins | `plateauLand`, `plateauJob` and `stageBillOf` are cut from `pw_civ_clock.js` (as in `test_households`) and run on a fake block world. `plateauLand` gives a compact record (no ops, < 200 chars). `stageBillOf` puts the plateau on the frame only. `plateauJob` finishes over several ticks, writes nothing in the box, levels the rear ring with a gravel gutter on cobble, cuts a clad face at P + 3 / P + 6, lays the grated drop to H − 9 and the 4 × 2 link into the hall, and writes the chronicle line. A trunk in the face → refused, fallback, nothing set. A chunk that never loads → waits (> 1,000 ticks), then the fallback, nothing set. |

### The other suites

All 25 suites pass:

| Suite | Checks |
|---|---|
| beat | 116 |
| canopy | 5 |
| coins | 810 |
| court | 37 |
| diet | 8 |
| econ228 | 1195 |
| fell | 31 |
| frontage | 12 |
| households | 95 |
| hygiene | 15 |
| lanes | 14 |
| market | 16 |
| names | 48 |
| needs | 80 |
| occupied | 97,680 |
| plan | 37 |
| **plateau** | **76** |
| player | 71 |
| ramp8 | 7 |
| route | 468 |
| save | 40 |
| shifts | 90 |
| talk | 48 |
| watch | 15 |
| why | 33 |

The other 24 suites have the same counts as before the change. `test_frontage` is unchanged at 12/12: without `opts`, `placeAlong` keeps the old law.

`node --check` passes on `pw_civ_clock.js`, `pw_civ_plan.js` and `pw_civ_streets.js`. `tools/js_dupcheck.py` passes on all three.

---

## 4. Expected frontage gain (measured offline, read-only, on saved gate logs)

The audit runs offline on a saved log. It needs no server.

### 4a. The frontage rise alone

`street_frontage_audit.py LOG --plateau` is a new opt-in mode; the default output is unchanged. It packs each street, back to back, under three laws:

- rise 0 (level runs);
- rise ≤ 1 (the current law);
- rise ≤ 2 with the door within 1 (the plateau law).

| Log | cottage_m (rise 1 → plateau) | cottage_l | park (15) |
|---|---|---|---|
| civtest-20261006-100113 | 69 → 69 (+0) | 51 → 52 (+2 %) | 34 → 42 (**+24 %**) |
| civtest-20261005-190214 | 122 → 122 (+0) | 88 → 92 (+5 %) | 60 → 73 (**+22 %**) |
| civtest-20261005-154344 | 114 → 115 (+1 %) | 84 → 87 (+4 %) | 58 → 70 (**+21 %**) |

- On 7- and 8-cell ramps, a 9-cell frontage rarely spans two rises, so the rise rule alone gives cottages almost nothing.
- It gives the **park** about +22 % of positions. This directly addresses "Park not placed (no flat 15-cell frontage)".

### 4b. The land behind (the cottage gain)

A scratch node script (not shipped) used the logs' final heightmap, streets, plot boxes and roads. It packed the empty street sides with cottage_m under two laws:

- **(A)** the current rule: rise ≤ 1 and a port of `slotRelief` with the real `PLAN.judgeLot`, without stilts;
- **(B)** rule A first, else `PLAN.planPlateau`.

| Log | (A) houses | (B) houses at dial 6 | (B) at dial 9 (`cutMax` / `fillMax`) |
|---|---|---|---|
| civtest-20261005-190214 | 85 | 89 (+5 %; 10 on plateaus) | 96 (+13 %; 19 on plateaus) |
| civtest-20261005-154344 | 71 | 73 (+3 %; 11 on plateaus) | 80 (+13 %; 19 on plateaus) |
| civtest-20261006-100113 (city, nearly full) | 2 | 3 | 6 |

- At the requested dial (6), most plateau refusals are `cut` (the pad deeper than 6) and box `fill` (a hollow deeper than 12 under the house: stilts country, which phase 5 still offers).
- **Owner decision:** raising `cutMax` / `fillMax` to 9 roughly triples the land-side gain on these hills. That means 3-lift faces at the pad, which is still R5-compliant (lifts of 3).
- These numbers are an estimate, not a gate result:
  - the final heightmaps already contain neighbours' terraces;
  - packing here is greedy, while the real search starts at each street's anchor;
  - stilts are excluded.

**The real measure** is the next gate: run `pw:clock frontage cottage_m` and look for the new "N of them on PLATEAUS". `slotWhy.plateauOk` / `plateauNo` and `st.plateauWhy` are in the evo record, and `st.plateaus` counts the plateau plots built.

---

## 5. Risks and open points

1. **P1: nothing is witnessed.** Wall looks (stone bricks against grass), gutter readability and the grate are designed, not seen.
2. **Shared side gaps.** Two neighbouring pads at different heights share one gap cell. The later job never cuts a worked block and never fills over water. So the higher neighbour's wall survives in the gap, and the lower pad's gutter or top may not be placed there.
3. **Corners.** The faces run straight out from the ring. The diagonal corner beyond a rear corner is not cut, so a natural shoulder of hill stays there. This is a look risk, not a structural one.
4. **The drain's link into the corridor.**
   - It carves only `BRANCH_CUT` materials and only on rows a house branch already carves.
   - A tee laid later over that t would replace it, leaving a dead-end sump. Halls inside junction windows are already avoided.
   - The hall depth under ramp pieces is covered by the 2-row link. It is not witnessed.
5. **Protected trees** are seen only at build time (live reads). A plateau planned over a tree falls back to the old ring terrace at build time. The plot stays and gets no plateau. This is logged.
6. **Search cost.** A family that fails phase 0 now costs one more search phase (phase 1, plateau), one per beat. Positions with a frontage rising 2 now reach the land check (more `slotRelief` calls). Watch the `slot … (plateau)` timings in the next gate.
7. **Saves.** In-flight `it.phase` / `leftCursor.ph` values from an older save map to the renumbered phases. This is harmless: at worst one different search phase runs once. New saved fields:
   - `b.land` (plateau record, under 200 chars);
   - `b.plateauDone`;
   - `st.plateaus`, `st.plateauWhy`;
   - `st.park.at` / `st.park.land`.
8. **Water law.** The old "DRY the plot" step in `kitLandPrep` (water near the box → dirt) still runs for plateau plots too. It predates the water law and was left unchanged; flagged for the owner.
9. **Not done here:** the build (`build_bp02_*.py`), packaging, and BDS gates. No `_build`, `_bds` or pack file was modified. The saved logs in `_bds/logs` were only read.
