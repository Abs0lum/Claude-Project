# HISTORY ADDENDUM — week 41 (2026-10-04 → 10-05) — append point for HISTORY-v4

## 2026-10-04 — round 1004b (D-C563..D-C569) — BP-02 1.3.220 · RP-01 1.3.122 · RP-05 1.3.59 · Markers BP 0.2.4 / RP 0.2.3 · TestRunner BP 0.5.24
- Felling by template, the floating-foliage sweep, flooding (drain / seal / watch), mob clearing from placed structures,
  civ restructure (our window only, states, children never trade, flue avoidance), lectern east, vine shake-off, PHYSICS
  falling trees + the yaw law (D-C565), birch v2, RP-05 vanilla leaf textures, manhole lift-then-slide (his 19:06 ruling).
- His 19:35: civs halved to movement 0.25 (+ brisk watch, the `pace` command). 19:36: leaf placement + Patrix detail
  verified (544 templates, 229,918 leaf cells, 100 % pw:*_leaves).
- 21:18: his content log (hundreds of `Missing referenced asset geometry.pw_pilot_*`) = TestRunner BP test blocks without
  the TestRunner RP → TestRunner BP 0.5.24 without the blocks.

## 2026-10-04 21:03 → 10-05 — round 1005 (D-C570..D-C572) — BP-02 1.3.221 → 1.3.222 · RP-01 1.3.123 · RP-12 1.0.0 (+ LITE)
- D-C570 THE CITY PALACE (his P1 city II, P2 life-size and grand, P3 jib doors AND painting doors): palacegen.py
  (128 × 128, 363 markers, the hidden world), four 64 × 64 pieces in lockstep as the crown's works, the crown's survey
  (held ticking area), light plot stages, the land job (retaining walls → clear naturals → fill hollows → margin ring).
- D-C571 THE GALLERY + THE CONNOISSEUR'S BOOK (his 21:30 / 21:39 / 22:01): 6,256 CC0 paintings (NGA, the Met, Cleveland),
  one entity type per work, frames in quarter-block classes, art slots scanned offline for every template, the no-repeat
  registry, the book (artist's life · the work · a reading · a critique), 155 writer jobs → 6,256 essays + 1,791 lives.
- D-C572 CASTLES (his 23:02 / 23:11): both period skins with forced variety, 256+ castle-palaces, both founding modes,
  an ORIGINAL academy-castle (never Hogwarts); castlegen.py v0.1 + an eight-castle variety sheet for his review.
- Engine lessons (LESSON-CANDIDATES-2026-10-05): the 10 s watchdog vs QuickJS loops; ~40 µs per placed cell (light
  stages < 150k cells); Block reads of unloaded chunks throw; spawns need TICKING chunks; `structureManager.place` skips
  unloaded chunks silently (every chunk of a footprint is probed now); `getTopmostBlock` skips liquids (climb to the
  surface for any water height); a timed-out tool shell kills background runs (setsid).
- Sources: the Met retired /v1/search on 2026-10-01 (v1.1 paginated); AIC's IIIF sits behind Cloudflare.
- Gates: palace 221 runs 1–3 (search thrash → multi-day held survey; watchdog hangs → chunk occupancy, light s0, one piece
  per beat, LAG_SLICES 3); gallery 222 runs 1–8 (resumable hanging, 0 repeats, 334 pictures + 280 in the palace; the
  "flooded palace" chased from the wet test to unloaded chunks to a mountain lake over the wall).
- 10-05 07:5x–09:xx: gate runs 8–10 of 222 (the lake site → stricter site rules → run 9 "no site in 80 days" = samples
  outside the holdable area, LC-1005-11 → run 10 with the survey fixed); the FLOOR-HOLE finding (light blocks have no
  collision; palacegen v2 puts them in the air, LC-1005-10; 52 templates censused clean). CASTLES offline: castlegen v0.2 +
  castle_verify.py (eight checks; all sheet castles "constructed correctly"; diagonal walks two wide, LC-CASTLE-1);
  CASTLE-VARIETY-SHEET-v0_2. His 08:43 answers: Q36 b, Q37 a, A3 a, K1 b, K2 b (guards recruited over time), K3 a, K4 c,
  K5 a, K6 a, K7 b (a rare academy city), K8 b, Q32 a, Q33 a, Q35 b (R-55 re-bake next).
