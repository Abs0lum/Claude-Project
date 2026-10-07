# CIV-LAND notes for the next slice (written 04:13 CT 10-07)

## Where things stand
- APPLIED + green: kitPrep unread-cell cut (pw_civ_clock.js ~l.3281, street.prepBlind) and rampclear
  (KIT.rampClear in pw_civ_streets.js ~l.1290-1338; 1-line call in clock pw:clock handler; tests/test_rampclear.mjs 9/9).
- All 31 suites were 0 FAIL after those two applies. test_band.mjs is now INTENTIONALLY RED (43/51) because of 3 new
  checks per hill (tests/test_band.mjs l.117-141) encoding his ruling:
  "because of the width of the roads, we have to do more short runs, and run them contiguously to get the correct
  height jump, THEN make the switchback."
  1. links (segments along f.v, i.e. uphill) are flat: linkRise === 0
  2. on every run (segments along f.u, contour) ramps chained: consecutive rise indices differ by exactly KIT.ROAD_RAMP (4); runs >= 2
  3. |road H - ground| <= KIT.ROAD_CUT (4) for cells i in [7, L-7)
  Failures measured: 0.3 + 0.35 hills: link rise 6, 1 break, cut 6; 0.45: link rise 3, cut 6.
- Backups: _garbage/CIV-LAND-pre/*.0406 (pre-slice-4 copies of streets/clock).
- NO band-leg generator code written yet (this slice had ~9 minutes; spent on reading + notes).

## Code map (pw_civ_streets.js, 1338 lines)
- l.744 ROAD_W 7, ROAD_CUT 4, ROAD_HALF 3; l.746 ROAD_RAMP 4
- l.750 roadShapes, l.802 switchbackShapes, l.846 hairpinShapes (returns {cells, dirs, turns} l.910)
- l.912ff shape pass (planRoadShapesJob), height DP ~l.960-1010
- l.1030 planRoadJob(ground, blocked, P0, d0, P1, d1, H0, H1, maxDP, stats) -> returns
  { cells, dirs, turns, H, segs, cost, legs } (l.1204). segs: [{kind:"ramp"|..., len,...}]; legFacts (l.~1280) reads H, turns, segs.
- l.1230 bandMouths(f, tj, side, f2, half) -> {P0, d0, P1, d1}
- l.1245 planBandStreetJob — calls planRoadJob at l.~1272 (`const road = yield* planRoadJob(ground2, blocked, P0, d0, P1, d1, Hb, Hn, BAND.maxDP, legStats)`).
- Clock caller: pw_civ_clock.js l.5640 (KIT.planBandStreetJob), commit at l.6012.

## Exact next steps
1. Add `export function* planBandLegJob(ground2, blocked, f, P0, d0, P1, d1, H0, H1, stats)` in streets.js just above
   planBandStreetJob:
   - rise = H1 - H0; ramps needed = |rise|; a run of length Lr along +-f.u holds floor((Lr - 2*landing)/4) chained ramps.
   - landing = 3 flat cells each side of a turn (legFacts requires 3 before/after flat), link (along f.v) = ROAD_W+gap
     cells, FLAT.
   - Run spacing along v ≈ link length; each run's ramp count k chosen so the road tracks the ground: k ≈ slope x spacing
     (≈ 4 at 0.45) — compute from ground2 sampled at the run's centre line, clamp so |H - g| <= ROAD_CUT.
   - Build cells/dirs/turns by walking: P0 straight out along d0 (mouth landing 7 flat), turn onto +-u run (chained ramps),
     flat hairpin link along d0 (=v), reverse u run, ... last link arrives at P1 heading d1; alternate run direction.
     Run lengths: choose between 12 and ~40 cells; try a few (width of leg area between mouths in u) and pick min cost.
   - Veto every cell + ROAD_HALF either side with `blocked`; yield every run.
   - Emit H array + segs in the same shape as planRoadJob (segs kind "ramp" len 4 per ramp, "flat" otherwise) so
     legFacts/commitBand/piecesOf keep working — CHECK how commitBand (clock l.6012) consumes road.segs/H before choosing.
2. In planBandStreetJob replace the planRoadJob call with: `let road = yield* planBandLegJob(...); if (!road) road = yield* planRoadJob(...)`.
3. Run `node tests/test_band.mjs` -> target 51/51 (note the 0.45 "limit" check at test l.~145 expects null for a
   house-row bank — if the new generator succeeds there, ask whether that check should flip; do NOT silently change it).
4. Run all suites: `cd tools/bp02_src_228 && for t in tests/*.mjs; do node $t || echo FAIL $t; done`; node --check streets.js.
5. Re-render: `node tests/test_band.mjs --dump` -> evidence/hill045.json, then `python3 _staging/CIV-LAND/evidence/render_band.py`
   (check its args) and VIEW the png (north/+z up) before claiming anything.
6. Stage changed pw_civ_streets.js under _staging/CIV-LAND/ + README line; md5s; status DONE line; phase_log line.

## Slice 04:15-04:25 (written ~04:21 CT 10-07) — findings, NO code changed (old path intact; suites as before: test_band 43/51 intentionally red, rest green)
- Working tree = /home/claude/tools/bp02_src_228 (NOT _knowledge/... copies). streets.js now 82,752 B.
- For (B) slope-driven ramp choice, ALREADY PRESENT for STREETS: planProfile (streets.js l.18-23, l.118-254) has
  opts.ramp8 -> 8-ramp (RAMP8=8, how 3/4) preferred by cost, ramp7 (4-part + landing) costs RAMP7_EXTRA=12 more,
  used only where 8 can't fit / earthwork far higher. Clock STREET_OPTS l.3131 sets ramp8:true.
  NOT slope-driven elsewhere: narrow roads + band legs go through planRoadJob with ROAD_RAMP=4 only (l.746).
  => (B) work = (1) make the street choice explicitly grade-driven (test: mild slope -> all ramp8 segs; steep -> ramp7)
     — mostly a TEST of existing behaviour; (2) add 8-ramp option to planRoadJob height DP (~l.960-1010) for
     roads/legs where grade allows, keeping 4 for steep; check piecesOf/commit can emit road ramp8 pieces (piece name
     `${pre}ramp${len}` l.292 already parametric) and that legFacts (l.1278) tolerates len-8 ramps.
  Ask/flag: band legs are by definition steep (switchbacks) -> 4-part there is consistent with his ruling.
- (A) unchanged: implement planBandLegJob per steps above; planBandStreetJob call site is l.1266 (`road = yield* planRoadJob(ground2, ...)`).
  Wire as `let road = yield* planBandLegJob(...) ; if (!road) road = yield* planRoadJob(...)` (change `const` to `let`).
- (C) not started (crossroads + wooded park; family-of-4 home sizes = proposal only).

## Slice 04:21-04:37 (written 04:27 CT 10-07) — (A) APPLIED
- planBandLegJob(ground, blocked, P0, d0, P1, d1, H0, H1, stats) added in pw_civ_streets.js just above planBandStreetJob
  (scratch source also at scratchpad leg.js). Model: mouth flat along d0, then EVEN count of runs along +-u all of length Lr
  (11..47 step 4), alternating (zig-zag back to P0's u; bandMouths always gives P1 at the same u), 4 pad cells after each
  turn, k chained 4-part ramps, >=3 pad before next turn; links along d0 FLAT, >= ROAD_W+1; last link >= 3 cells.
  DP per (Lr, first dir) over states (z, h, parity), cost sum|H-g|+cells. Cut law: fill <= ROAD_CUT 4, cut <= ROAD_CUT_MAX 6
  (planRoadJob's own law); mouth 7 cells / last 7 cells loose fill 6. segs rebuilt from H steps (ramp len 4).
- Wired: planBandStreetJob `let road = yield* planBandLegJob(...); if (!road) road = yield* planRoadJob(...)`.
- Result: test_band 44/51 (was 43). 0.45 open: new leg used — 8 turns, 27 ramps, linkRise 0, chained PASS; only FAIL 48
  worstCut 5. 0.3/0.35 with houses: new gen returns null -> fallback planRoadJob -> FAILS 20-22, 33-35 unchanged.
  All other suites 0 FAIL. node --check OK.
- WHY the 7 remaining FAILs are infeasible as literally written (numbers, hill(s) = 64 + floor(s*z)):
  * 0.45 open, check "|H-g| <= 4 for i in [7, L-7)": H0 = Hb = 66 (ground at z 6). The first run must sit at world z >= 16
    (its 7-wide deck z+-3 must clear the base street z <= 12); ground there >= 64+floor(7.2) = 71 -> cut >= 5 at the run's
    first cells (index >= 7 since mouth 3 + pad 4). So worst >= 5 for ANY flat-link leg. Achieved 5 (the minimum).
  * 0.3 / 0.35 with houses: houses z 13..24 except x 45..67; a run or link inside that zone is boxed to x 48..64, too short
    for even one ramp with pads (3+4+3 = 10 > 8 from x 56). So the first run must be at world z >= 28 (deck clears z 24);
    the mouth must stay FLAT (linkRise = 0) at Hb 65 from z 13 to 28 where ground = 64+floor(8.4) = 72: cut 7 > ROAD_CUT_MAX 6
    (and > 4). No flat-mouth leg exists; the old planRoadJob only manages it by climbing the mouth (link rise 6).
- QUESTIONS for the lead (do NOT change the test silently):
  Q1. May the MOUTH (the straight exit through the window, along d0) carry chained 4-part ramps (a "run" up the slope) —
      i.e. exempt the first segment from linkRise=0? That makes the house banks feasible.
  Q2. Cut check: use the narrow-road law (fill <= 4, cut <= 6 = ROAD_CUT_MAX) instead of |H-g| <= 4, or widen the
      exempt mouth zone to the first run? 0.45 open then passes.
- NEXT: on ruling, (Q1) add a climbing mouth option to planBandLegJob (mouth ramps chained from cell 7, flat 3 before the
  first turn); adjust test per ruling; re-render (test_band --dump -> evidence/hill045.json; render_band.py) and VIEW;
  then (B) grade tests + ramp8 option in planRoadJob.

## Slice 04:27-04:37 (written 04:30 CT 10-07) — (A) DONE per lead rulings Q1 YES / Q2 YES
- planBandLegJob: climbing mouth — loop k0 = 0..|rise|; mouth heights mH(z) = runH(H0, sgn*k0, z - 3) (ramps from cell 7),
  first run needs z1 >= 7 + 4*k0 + 3; first chain state carries st.k0; reconstruction emits mouth ramps. Pre-edit copy:
  scratchpad streets.pre_mouth.js.
- tests/test_band.mjs: rulings documented in a comment above the check block; mouth segment (k 0) exempt from linkRise;
  cut check now fill (H-g) <= ROAD_CUT 4 AND cut (g-H) <= ROAD_CUT_MAX 6. Result 51/51 (0.45 limit check still null: unchanged).
- All 31 suites green. streets md5 25ad1194 (91,772 B); test_band md5 d864fb5f. Staged _staging/CIV-LAND/pw_civ_streets.js
  + _staging/CIV-LAND/tests/test_band.mjs.
- Renders VIEWED (top = +z uphill): evidence/hill045_v2.png — flat mouth y66, 4 runs (y66->73->79->86->93), flat links,
  8 turns. evidence/hill03_v2.png — mouth climbs y65->69 (4 ramp marks), 2 runs y69->76->83, flat link, 4 turns.
  Renderer does not draw houses (0.3 is the house-row bank) — the "no touch" test check covers that.
- NEXT = (B), not started: (1) test: mild grade street -> all ramp8 segs, steep -> ramp7/4-part (planProfile opts.ramp8,
  streets l.18-23/118-254, clock STREET_OPTS l.3131); (2) planRoadJob: add 8-part option in its height DP / planProfile call
  (l.~1014 and l.~1194 pass ramp: ROAD_RAMP — check whether planProfile's ramp8 opt can be passed there: ramp8:true) for
  mild grades; band legs (planBandLegJob) stay 4-part. Check legFacts (rampLens) + piecesOf `${pre}ramp${len}` accept len 8.
- (B) finding 04:30: planProfile's 8-ramp is gated `with8 = !!opts.ramp8 && R === RAMP` (l.118) — i.e. only when the ramp is the
  7-cell street ramp; roads pass ramp: ROAD_RAMP 4 so ramp8 is silently off for them. (B)(2) needs: lift that gate for R 4
  (8-ramp vs 4-part cost choice), and a 7-wide ROAD 8-ramp piece/commit path — check how roads are committed (not the street
  pieces at l.288) and whether a road-width ramp8 block set exists; if not, that is a question for the lead.

## Slice 04:30-04:40 (written 04:38 CT) — (B) structures PARTIAL, no JS changed
- Staged _staging/CIV-LAND/structures/pw/road/r_ramp8.mcstructure (8x16x7, lane z3..9 of staged t_ramp8, y15 air, 0 void) +
  generator _staging/CIV-LAND/tools/road_kit_ramp8_road.py. README section added.
- OPEN (fix first): 56 cells at y14 differ from t_ramp8 on round-trip — staged t_ramp8 deck has no pw:var; road_kit_228 ramp8()
  sets pw:var on ramp_cobble_8. Check blocks/pw_ramp_cobble_8_e*.json states; make r_ramp8 match the shipped/staged deck exactly.
- KEY FINDING for the lead: roads are NOT kit pieces. layRoadOp (clock l.6064-6110) places pw:ramp_cobble_4_q1..q4 per cell;
  commitBench/commitLeg/lane recs pin rampLen: KIT.ROAD_RAMP (clock l.4844, 5924, 5988). So the 8-part road ramp can be laid
  per-cell with pw:ramp_cobble_8_e1..e8 inside layRoadOp (no structure needed) — or via r_ramp8 placement. Ask lead which.
- NEXT: (1) resolve pw:var; (2) planProfile l.118 `with8 = !!opts.ramp8 && (R === RAMP || R === ROAD_RAMP)`, pass ramp8:true
  at l.1014/l.1194 (not in planBandLegJob — legs stay 4); segs then carry len 8; (3) per-ramp rampLen (seg.len) instead of
  rec-level rampLen in commit*/layRoadOp; legFacts rampLens; (4) tests mild->8 / steep->4 for streets + roads; all suites.
