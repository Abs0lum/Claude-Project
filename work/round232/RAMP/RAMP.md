# RAMP — BP-02 1.3.232: #7 plateau dial 9 and #5 8-part road ramps laid block by block

**Base:** round-231 source (`work/inbox-2026-10-07-1714/bp02-231-src`).
**Workspace:** `scratchpad/w232-RAMP`.
**Status:** source only. Nothing is built, packaged or witnessed. Static checks and node tests can only rule things out (P1).
**Result:** 34 of 34 suites pass (33 old + the new `test_roadramp8`), `node --check` passes on all 46 scripts, and `js_dupcheck` is clean on the 3 changed scripts. The full run is pasted at the end.

**Changed files** (md5 prefix; the diff is `RAMP.diff`):

| File | md5 |
|---|---|
| `pw_civ_plan.js` | 3376e2f6 |
| `pw_civ_streets.js` | 41dfc8f0 |
| `pw_civ_clock.js` | 47484cb3 |
| `tests/test_plateau.mjs` | 4946fdbd |
| `tests/test_roadramp8.mjs` (new) | a741e463 |
| `tests/fixtures/ramp_cobble_230.json` (new) | 15425db2 |

**Other workers:** `w232-HOMES`, `w232-INN`, `w232-ACAD` and `w232-PALACE` also edit `pw_civ_clock.js`. My hunks are small and local, but the lead has to merge them.

---

## 1. #7 — the frontage plateau dial `cutMax` / `fillMax` is now 9

Ruling: D-GH1007-PLATEAU (2026-10-07). It was 6.

### Mechanism, before the change (round-231 line numbers)

- `PLAN.PLATEAU` is at `pw_civ_plan.js` l.126.
- Where `planPlateau` uses the two dials:
  - l.191–192: the ring's cut and fill (and the box's cut is folded into the same `cut`).
  - l.230, 245, 263: the first outside drop, the berm drop and the exposure.
  - l.232: `K = floor(fillMax / lift)`. At 9 this goes from 2 to 3, so the berm lifts are now P−3, P−6 and P−9.
- The uphill faces use `faceLifts` (3) and `lift` (3). Each clad face is still at most 3 high.
- The clock's `plateauJob` reads `R = faceLifts + 2 = 5` rows out. The deepest berm ray needs K + 1 = 4 rows and the deepest face ray needs 4, so 5 covers both. No change was needed there; a test now checks it.

### Finding: headroom over the house

- The plateau measures the box's cut but never works the box. The house's plot stage (`stages/<stem>_s0`) is expected to clear it.
- I read all 43 s0 templates in BP-02 1.3.230 (`RAMP-files/s0_all.py`). Every one is air from the floor up to its top row, which is `size_y − 1 − datum_y` rows above the floor:

  | Families | s0 clears up to |
  |---|---|
  | cottage_s, butcher, farm_wheat, farm_terrace | +8 |
  | quarry, well | +6 |
  | lumberyard, cottage_l | +9 |
  | cottage_m, bakery, smithy, farm_cattle | +10 |
  | town_hall | +11 |
  | inn | +14 |
  | manor | +21 |

- `clearOver` only clears leaves, logs, vines and `pw:` blocks above that. It does not clear dirt, grass or stone.
- So at dial 6 every family was safe: 6 ≤ +6. At dial 9, a box cut of 9 would leave 1 to 3 layers of hill sitting on the roofs of cottage_s, butcher, the farms, quarry and well.
- **Fix:** the box's cut is capped at `min(cutMax, the house's s0 rows)`.

### Changes (current line numbers)

`pw_civ_plan.js`:
- l.129–130: `PLATEAU.cutMax = 9`, `fillMax = 9`.
- l.111–118: the header comment now says 9, P−9, and explains the box cap.
- l.145–150: new `boxClearOf(def)` = `size[1] − 1 − datum_y`.
- l.173: new optional `g.boxCutMax`; the effective cap is `min(cutMax, g.boxCutMax)`.
- l.188: a box cell above the cap fails with `"cut"` at that cell.

`pw_civ_clock.js`:
- l.4442: `kitFree(…, def = null)` computes `boxCut = PLAN.boxClearOf(def)`.
- l.4474: `plateauLand(…, false, boxCut)`.
- l.4529 and 4541: `plateauLand(…, boxCut)` → `planPlateau({ boxCutMax })`.
- The callers now pass `def`: `kitSlot` l.4568, `frontageCensus` l.4688–4689, `laneSlotFor` l.4877.
- `kitFree` is also the path for the ramp-door plateau (#6), whatever `allowPlateau` is, so the cap has to apply there too.
- The park keeps no cap. `layPark` fills its box and clears up to ground + 4.

### Tests (TDD: red first, 25 FAIL)

`test_plateau.mjs` went from 76 to **109/109**:
- The dial assertion now expects 9. Two test names that said 6 were reworded.
- New pure checks:
  - An uphill lot with pad cut 8 is taken, and the same lot is refused at dial 6.
  - Clad faces are at most 3 high, and every face cell is cut to `min(g, P + 3·row)`.
  - A drop of 9 behind the pad is taken (refused at 6), with three berm lifts at P−3, P−6 and P−9.
  - Ring walls are at most one lift. Berm faces are at most 3 courses plus the top.
  - A drop of 10 is still refused.
  - **Protected trees:** a tree on the new third berm lift → refused (`tree`). A tree beyond the last lift → no effect. A tree in the deeper face → refused.
  - **Box cap:** `boxClearOf` gives cottage_s 8, cottage_m 10 and quarry 6, read from the real `CIV_BUILDINGS`. A box cut of 9 is refused under cottage_s (cap 8) and taken under cottage_m (cap 10). A box cut of 10 is refused by the dial. The cap never applies to the ring.
  - **Door landing (#6):** a raised ramp-door slot (floor 62) plans a pad over ground 8 below at dial 9 (refused at 6). None of the plateau's works touches a landing cell (`K.landingCells`). The landing's top equals the pad P.
- New clock checks on stand-ins:
  - The read radius covers the berm and face rays.
  - `plateauLand` takes and applies the box cap.
  - `kitFree` passes `def` at all 4 callers.
  - A 0.9-per-cell lot (pad cut 8) is cut with no fallback.
  - **Headroom:** all 27 ring cells are solid at P with air at P+1..P+3.
  - Clad lifts sit at P+1..3, P+4..6 and P+7..9, with air above each.
  - Nothing is written inside the box.
  - A trunk on the deeper face's third lift → refused, fallback, nothing set.
- `test_doorramp.mjs` is unchanged at 14/14. Its regexes on `kitFree` still match.

---

## 2. #5 — 8-part ramps on mild ROADS, laid block by block

Rulings:
- 04:12: "8-part on mild roads, 4-part only on steep; switchback legs stay 4-part".
- D-GH1007-RAMP8: "one by one".

### Facts, read from BP-02 1.3.230 (fixture `tests/fixtures/ramp_cobble_230.json`, made by `RAMP-files/make_fixture.py`)

- **Block ids:** `pw:ramp_cobble_8_e1` … `e8`.
- **States:** `minecraft:cardinal_direction`, through the `placement_direction` trait, plus `pw:snow` 0–4. There is no `pw:var`; round 230/231 are SLIM.
- **Collision:** the top of e_k is 2k px, so e8 is a full block. The 4-part q1..q4 tops are 2, 6, 10 and 14 px.
- **Rotation table** (identical for e and q): south 0, east 90, north 180, west 270.
- **1.3.231:** the handoff (#10) re-skinned the same 266 `pw_ramp_*` blocks. 266 × 20 = 5,320 permutation slots matches cardinal × snow, so no new ids and no state change.
- **The model, from the street piece `t_ramp8.mcstructure`:** it lays its cobble lane (y14, z3..9) as e1..e8 from the low end x0 to the high end x7, every block `cardinal_direction = east`, which is its uphill direction (travel +x).
  - The road's 4-part follows the same rule: q1 at the low end, `CARD4[uphill]`.
- **Material:** narrow roads are cobblestone (`lay` sets `minecraft:cobblestone` at H), so the ramp blocks are `pw:ramp_cobble_*`.

### Mechanism, before the change

- `planProfile` gated the 8-ramp with `with8 = !!opts.ramp8 && R === RAMP` (round-231 l.118).
- Roads pass `ramp: ROAD_RAMP` (4) at round-231 l.1049 (shapes) and l.1229 (terrain search), so the 8-ramp was always off for them.
- Road records stored `ramps: [[a, dir]]` with `rampLen: 4` on the record (bench and leg) or none (gate stubs → the old 7).
- `layRoadOp` (round-231 l.6077–6127) laid only `pw:ramp_cobble_4_q*`.

### Changes

`pw_civ_streets.js`:
- l.125: `with8 = … (R === RAMP || R === ROAD_RAMP)`.
- l.26–30: new dial `ROAD4_EXTRA = 48`. This is the 4-part's extra cost when the 8-part is on. The streets keep `RAMP7_EXTRA = 12`. Used at l.171.
- l.957 and l.1072: `planRoadShapesJob` and `planRoadJob` take `opts = null` and pass `ramp8: !!(opts && opts.ramp8)` to both exact `planProfile` calls.

`pw_civ_clock.js`:
- l.3133–3136: `ROAD_OPTS = { ramp8: true }`.
- Who gets the 8-part:
  - **Bench roads:** `benchJob` passes it (l.5904).
  - **Gate stubs:** use it too (l.6226).
  - **Climbing legs:** `legJob` (l.5983) and the band leg (`planBandLegJob`, then its `planRoadJob` fallback) do **not**, so they stay 4-part.
- Ramp lengths: every road record keeps `[a, dir, len]` (`commitBench` l.5942, `commitLeg` l.6007, gate stub l.6230). The record-level `rampLen` remains as the fallback for old saves.
- `layRoadOp` (l.6083–6139):
  - A ramp with `len === 8` puts `8_e{k}` on all 8 cells: e1 at the low end, and for a descending ramp e8 at its first cell.
  - Every part is `CARD4[uphill]`, the same as the street piece.
  - Each block is set with `BlockPermutation.resolve("pw:ramp_cobble_" + part, { cardinal_direction })` at H+1, on the cobble at H, k = −2..2. These are the same rows and kerbs as the 4-part.
  - 4-part and old records lay exactly as before. A test checks this byte for byte.
- Witness tools:
  - New `roadRampList(rec)` (l.6157).
  - New `/scriptevent pw:clock roadramps` (l.8313).
  - The bench-road chronicle line now ends "(N 8-part ramp(s), M 4-part)" (l.5950).
- Nothing references `r_ramp8` or `road/r_`. A test scans every script for it.

### Choosing the road dial (evidence, not taste)

- Synthetic straight profiles with the road's law (ends fixed, 7 flat cells at each end, cut ≤ 6, fill ≤ 4):
  - 1 in 16, 1 in 12 and 1 in 10 → all 8-part.
  - 1 in 8 → mostly 8.
  - 1 in 6 → a 4/8 mix that stays within 1 block of the ground.
  - 1 in 4 → 19 of 20 are 4-part.
- On the gate world's real heightmap (`civheight-20261005-190214`, 40 roads, `RAMP-files/realroads.mjs`), share of 8-part ramps by end-to-end grade:

  | Grade (end to end) | `ROAD4_EXTRA` 12 (the street value) | 48 (shipped) |
  |---|---|---|
  | ≤ 1 in 8 (mild) | 129/176 = 73 % | 157/166 = 95 % |
  | 1 in 8 to 1 in 5 | 40 % | 59 % |
  | 1 in 5 to 1 in 4 | 24 % | 29 % |
  | > 1 in 4 (steep) | 6 % | 6 % |
  | Earthwork Σ\|H−g\|, vs 4-only 12,117 | 12,927 (+6.7 %) | 14,514 (+19.8 %) |

- At 48, cells cut 5 or deeper went from 108 to 132, out of about 6,800.
- A road's ends are fixed. With the streets' 12, a quarter of the ramps on mild roads would still be 4-part. 48 gets the outcome the streets already have (mild → 8) without touching steep roads.
- Everything stays inside the road's cut/fill law. **This is a visual trade-off: more 8-parts in exchange for somewhat deeper cuttings. It is his call** (see open questions).

### Tests (TDD: red first, 14 FAIL)

New `tests/test_roadramp8.mjs`, **61/61**:
1. **The fixture:**
   - The real ids exist.
   - The states are cardinal + snow only (no `pw:var`).
   - The e_k tops are 2k px.
   - The rotation table matches the 4-part's.
   - The `t_ramp8` lane is e1..e8 low → high, all east.
2. **The profile:**
   - Mild 1 in 16 / 12 / 10: all 8-part. Without `ramp8` (the legs' law): all 4-part.
   - 1 in 8: at least 2/3 are 8-part.
   - Steep 1 in 4: at least 90 % are 4-part.
   - 1 in 6: a mix, within 1 block of the ground.
   - Descending: all 8-part with dir −1.
   - The law holds everywhere: steps ≤ 1, the 8-ramp's cells at the lower level, the cut/fill caps.
   - Streets are unchanged.
3. **`planRoadJob`:**
   - With `opts.ramp8` on mild 1 in 10 / 12 / 14 / 12-long: at least 2/3 are 8-part, and any 4-part stands within 2 cells of a landing (a turn or end window). Measured: within 1 cell.
   - Without opts: all 4-part.
   - Steep with opts: at least 90 % 4-part.
4. **Static wiring:**
   - The gate in `planProfile`, the two dials and the opts plumbing.
   - The band leg and `legJob` stay without `ramp8`.
   - The bench road and gate stubs use `ROAD_OPTS`.
   - All 3 records carry `len`.
   - No script references `r_ramp8`.
5. **`layRoadOp`, cut from the clock and run on a stand-in world**, with `BlockPermutation.resolve` held to the real block table (an unknown id, state or value throws):
   - In each of the 4 travel directions, climbing and descending, every 8-ramp cell has the right e_k and the right uphill facing, every flat cell has none, and there is cobble under all of them.
   - The walking surface is continuous, measured in eighths: every cell's far edge meets the next cell's near edge, on the climbing, descending, mixed and steep roads.
   - **Headroom:** every ramp cell's column is levelled at its H with 3 cleared above, so at least 2 stay free over the full e8.
   - A steep 4-part road is unchanged.
   - An old `[a, dir]` + `rampLen 4` record lays byte-identically.
   - An old 7-cell gate record still puts q1..q4 on its first 4 cells.
   - A mixed road lays each ramp by its own length.
6. **The witness list:** `roadRampList` gives one row per ramp (first cell, y = H+1, parts, facing), old records list as 4-part, and the scriptevent and chronicle counts are wired.

`test_band` (51/51), `test_ramp8` (7/7) and `test_landclock` (25/25) are unchanged.

---

## 3. What only he can confirm (in-game)

Use a new world, or an existing kit town. Roads that are already laid are not re-laid; only roads planned after the update get 8-parts.

1. **Road ramps (#5):**
   - Run `/scriptevent pw:clock bench`. It looks for a bench and a road to it.
   - When the chronicle says "a new bench … (N 8-part ramp(s), M 4-part)", run `/scriptevent pw:clock roadramps`. It lists each road's ramps as `x y z 8-part up <facing>`.
   - Go to the 8-part ramps and check:
     - the slope rises toward the listed facing over 8 blocks, smoothly, with no step at either end;
     - it is cobble, matching the road;
     - there is headroom at the top end;
     - there are kerbs on both sides;
     - civs and horses walk over it.
   - On a steep stretch the 4-part remains.
   - Also note any VV shadow bands (#11). These are the same blocks as the street ramps.
2. **Plateaus (#7):**
   - On a hill town, run `/scriptevent pw:clock frontage cottage_m`. The "N of them on PLATEAUS" count should be higher than under 1.3.231 in the same world.
   - The chronicle lines "gets a PLATEAU at y … (cut c, fill f …)" can now show values up to 9.
   - At such a plot, check:
     - the uphill face climbs in clad steps of at most 3 per row;
     - a deep downhill side has berm steps at −3, −6 and −9;
     - the grate and drain are there;
     - **no hill block sits on the roof**, especially on cottage_s and butcher;
     - a door at a ramp (#6) has its raised landing flush with the pad.

## 4. Open questions for Abs0lum

1. **Road dial.** With `ROAD4_EXTRA` at 48, mild roads are 95 % 8-part, at the cost of 20 % more earthwork. Setting it to 12 (the street value) gives 73 % with less digging, and 24 gives 86 %. Which does he want?
2. **Which roads count as "roads".** ASSUMPTION: bench roads and gate stubs are "roads" (8-part allowed). The climbing legs between parallel streets (`legJob`, D-C546) and the band legs are "switchback legs" (4-part only). Contour lanes are flat. Is that right?
3. **Box cap.** ASSUMPTION: a plateau may not cut a house's box deeper than its plot stage clears: cottage_s / butcher / farms 8, quarry / well 6, the rest 9. The alternative is to clear the box above the stage top in the plateau job, which would let those houses take a full 9. Keep the cap?

## 5. Risks and Retro-Sweep hits (not implemented; backlog for his approval)

- **`pw_civ_walk.js` l.179.** `half()` treats every `ramp_` block except `_q4` as a half block, so e7 (14 px) and the full e8 (16 px) count as "half". This has been true for the street ramp8 since 1.3.228; road 8-parts add more of them. Suggested fix: treat q4 / e7 / e8 as full. Effort S.
- **Corners and the fallback get taller.** The plateau's diagonal corner shoulder, which is never cut, can now stand up to about 9 above the pad (it was about 6). The fallback `terrace()`, used after a tree or an unloaded chunk, can now clad a hill face up to 9 high beside the house. Both are look risks only.
- **Docs and journal still say 6.** `knowledge/docs/program228/FRONTAGE-PLATEAU-NOTES.md` §2 still has the dial table at 6, and the decision journal needs these entries:
  - D-GH1007-PLATEAU applied, plus the box-cap ASSUMPTION;
  - D-GH1007-RAMP8 applied, plus the road-kind ASSUMPTION and the `ROAD4_EXTRA` dial.
  
  Update both at the next mirror build. I did not edit the repo.

## 6. Files

**Tools** (new, read-only analysis; no change to `knowledge/tools`), in `out232/RAMP-files/`:
- `make_fixture.py`: builds the fixture from bp02-230.
- `s0_all.py`: the s0 air rows.
- `ramp_cells.py`: the ramp blocks in a road piece.
- `realroads.mjs`: the real-heightmap road experiment.

**Evidence:**
- `out232/RAMP-realroads-48.txt`
- `out232/RAMP.status`

## 7. Final full test run (`work/test-harness/run_civ_tests.sh w232-RAMP`, exit 0; `node --check` passed on all 46 scripts)

```
test_alarm: test_alarm (b): 17 pass, 0 fail
test_band: test_band: 51/51 passed
test_beat: test_beat: 116/116 passed
test_canopy: test_canopy: 5/5 passed
test_coins: test_coins: 810/810 passed
test_court: test_court: 37/37 passed
test_diet: test_diet: 8/8 passed
test_doorramp: 14/14 PASS
test_econ228: test_econ228: 1195/1195 passed
test_fell: test_fell: 31/31 passed
test_frontage: test_frontage: 12/12 passed (houses: ramp-aware 13, flat-only 0, cesspit 13, ramps 13)
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
test_plateau: test_plateau: 109/109 passed
test_player: test_player: 71/71 passed
test_ramp8: test_ramp8: 7/7 passed
test_rampclear: rampclear force: 9 pass, 0 fail
test_roadramp8: test_roadramp8: 61/61 passed
test_route: test_route: 468/468 passed
test_save: test_save: 40/40 passed
test_shifts: test_shifts: 90/90 passed
test_survey: test_survey: 25/25 passed
test_talk: test_talk: 48/48 passed
test_watch: test_watch: 15/15 passed
test_why: test_why: 33/33 passed
js_dupcheck (clock, plan, streets): exit 0
```
