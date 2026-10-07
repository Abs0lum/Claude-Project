# SKYWAY ANGLES — requirements for more directions (2026-10-07)

**Status: requirements and a concept image only. Nothing was built, staged or changed.** Builds on
`SKYWAY-OPTIONS-2026-10-06.md` (options A/B/C) and the staged option-C rail family in `_staging/skyway230/README.md`.

**His words (00:23 CT 10-07):** the skyways "look amazing"; later he wants more angles — *"the spiral gives ~360° directions."*

**Image:** `SKYWAY-ANGLES-CONCEPT-2026-10-07.png` (script `src/make_angles.py`). Viewed at full size, twice (the first render
had a one-row gap between two landings and their runs, and a run that left the panel; both fixed). **Camera: every panel is a
plan view straight down, north up, 1 square = 1 block.** What it shows, literally:
- **Panel A:** a 9 × 9 stone tower ring with a round spiral stair inside (32 tread lines), 4 door gaps, 4 grey landings. Four
  runs leave the landings: west, 3 cells wide, rails on both outer edges (0°); east-north-east, rail cells alternating phase 0 / 1
  (26.57°, NEW); north-north-east, phases 0 / 1 (63.43°, NEW); south-east, rail cells marked `d` (45°, the staged diag). Brown
  lines are the rail lines; they touch block corners once per period; yellow squares are newels where each run meets its landing.
- **Panel B:** a compass: 4 blue (0 / 90°), 4 orange (45°), 8 green (2:1 family), 8 purple (3:1 family) heading lines, and dashed
  grey lines at true 22.5 / 30 / 60 / 67.5°.
- **Panel C:** the two 2:1 rail cells at 16 px per block: the rail line rising 8 px per 16 px, 8 red 2 × 2 px barrier boxes per
  cell stepping 1 px per box, 4 green kerb-floor boxes per cell on the walk side; 12 boxes per cell.

---

## 1. Starting point (staged, not installed)

- Option C rail family: `pw:skyway_rail_<wood>` with `pw:shape` = `diag | diag_n0 | diag_n1 | straight | corner` ×
  `cardinal_direction` 4 = 20 permutations per wood; `pw:skyway_bracket_<wood>` 4. Three woods → **72 permutations**.
- Block format 1.26.0 with array `collision_box` (his exception for the skyway rail, extended from the spiral stair).
- Headings today: **8** (0, 45, 90, 135° … as undirected lines: 4 orthogonal + 4 diagonal directions of travel).

## 2. Which angles a block grid can do cheaply — the rule

A straight rail across square cells repeats only when its slope is a ratio of whole numbers **p : q**. Over one period the line
crosses `p + q − 1` cells, and each crossed cell needs its own rail piece (walk side fixed). Rotating a piece 90° (the
`cardinal_direction` state) gives the other quadrants; the mirror angle (90° − θ) needs mirrored pieces. Each family also needs
4 run-end pieces (newel at the left / right end, both hands) to meet a landing.

Computed (Python; in-cell rail length from the exact cell crossings):

| Family | Angle(s) | Cells per period | Run pieces | + end pieces | Shapes per wood | Permutations per wood (× 4 dirs) | × 3 woods | Longest rail inside one cell |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| straight (staged) | 0 / 90° | 1 | 1 | 2 (incl. corner) | 2 | 8 | 24 | 16.0 px |
| diagonal (staged) | 45° | 1 | 1 | 2 | 3 | 12 | 36 | 22.6 px |
| **2 : 1** | **26.57° / 63.43°** | 2 | 4 | 4 | **8** | **32** | **96** | 17.9 px |
| 3 : 1 | 18.43° / 71.57° | 3 | 6 | 4 | 10 | 40 | 120 | 16.9 px |
| 5 : 2 (≈ 22.5° / 67.5°) | 21.80° / 68.20° | 6 | 12 | 4 | 16 | 64 | 192 | 17.2 px |
| 12 : 5 (≈ 22.5°) | 22.62° / 67.38° | 16 | 32 | 4 | 36 | 144 | 432 | 17.3 px |
| 5 : 3 (≈ 30° / 60°) | 30.96° / 59.04° | 7 | 14 | 4 | 18 | 72 | 216 | 18.7 px |
| 7 : 4 (≈ 30° / 60°) | 29.74° / 60.26° | 10 | 20 | 4 | 24 | 96 | 288 | 18.4 px |

**True 22.5°, 30°, 60° and 67.5° do not exist on a block grid.** Their slopes (tan 22.5° = 0.4142…, tan 30° = 0.5774…) are not
whole-number ratios, so the cell pattern never repeats; a long straight run would need a new piece in almost every cell.
Only the approximations above are buildable, and they cost 2–4.5× the 2 : 1 family.

**The 2 : 1 family is the grid's natural "22.5° step":** with it the compass has **16 headings** — 0, 26.6, 45, 63.4, 90° … —
never more than 26.57° apart, and 26.57° / 63.43° each sit within 4.1° of his 22.5 / 30 / 60 / 67.5°.

### Curves (a gallery ring around a tower)
A quarter-circle rail of radius R (centred on a block corner, R = n + ½) crosses **2R cells**, and every one is a different piece
(rotation covers the other 3 quarters):

| Radius (blocks) | Pieces per quarter | Permutations per wood | × 3 woods |
|---:|---:|---:|---:|
| 3.5 | 7 | 28 | 84 |
| 5.5 | 11 | 44 | 132 |
| 7.5 | 15 | 60 | 180 |
- One radius = one block family. The inner side is usually the tower wall, so a ring gallery needs only the outer rail.
- The deck under a curve: full slabs inside the band, and the rail piece's kerb fills the cut cells (as the staged diag does).

## 3. Engine laws each new piece must meet (checked against the numbers above)

| Law | Requirement | Status for the 2 : 1 family |
|---|---|---|
| Geometry ≤ 30 px per axis | rail + fascia + kerb inside 30 px | in-cell rail 17.9 px; the diag (22.6 px, extent 18.5 × 27.5 × 18.5) already fits, 2 : 1 is shorter ✔ |
| uv ≤ 16 px per face | split any beam longer than 16 px | 17.9 px → two 8.9 px halves (as the diag does) ✔ |
| Collision: arrays only by exception (granted for the skyway rail, ≥ 1.21.130) | barrier sealed against a 9.6 px player; ≤ 16 boxes per array | 8 barrier boxes 2 × 2 px stepping 1 px (they overlap, so they seal) + 4 kerb-floor boxes = **12 per cell** (Panel C) ✔ |
| 1.26.60: only array `collision_box` accepted | arrays everywhere | already arrays ✔ |
| A block-state enum holds ≤ 16 values | `pw:shape` 5 today | 5 + 8 = **13** — fits in the same block ids ✔. A second family (3 : 1, 10 shapes) needs **new ids**, not a second state (a second state multiplies permutations) |
| Geometry ids lowercase, format 1.16.0 (P13) | | to apply at build; run `geo_ref_check.py` |
| Selection box y ≥ 0, inside the cell | | full cell, as staged ✔ |
| Arbitrary y-rotation of cubes | 26.565° about y | RP-13 already ships bone rotations at −5.625° … −84.375° (spirals) and cube pitches of 7.12° (ramps-8), and both load; **the angle on PS5 is still a witness item** (L-ROT-DIR) |
| Walk graph (`pw_civ_walk.js`) | rail ids contain no `_slab` / `stairs` / `ramp_` → solid; band of slabs must be 4-connected | each column of a 2 : 1 band holds 2 slab cells and the next column is shifted by 0 or 1 → 4-connected ✔ (villagers zigzag: 3 grid steps per 2 : 1 period vs 2.24 blocks straight, ~34 % longer; the 45° run is ~41 %) |
| Clear width | ≥ the staged 2.65 blocks | rails 3 cells apart across the run → 3 × cos 26.57° = 2.68 blocks rail-to-rail (≈ 2.5 clear) |

## 4. Permutation cost in context

| Set | New permutations (3 woods) | Skyway total |
|---|---:|---:|
| Staged today (0° + 45°, brackets) | — | 72 |
| + 2 : 1 (phase 1) | +96 | 168 |
| + one curve radius 5.5 (phase 2) | +132 | 300 |
| + 3 : 1 (phase 3) | +120 | 420 |
| (instead of 2 : 1) 5 : 2 ≈ 22.5° | +192 | — |
| (instead of 2 : 1) 7 : 4 ≈ 30 / 60° | +288 | — |

- **Context:** BP-02 1.3.229 = 55,948 permutations by this census (handoff: 55,891) + Markers 1,621. On 09-28 his content log
  said *"World with over 65536 block permutations may degrade performance. Current world has 66346"* while BP-02 had 56,482
  (journal D-C265) — so vanilla and the rest added ≈ 9,864. The same arithmetic (assuming vanilla's share has not changed since 09-28)
  puts today's world near 67,400, over the 65,536 figure. Skyway angles are tiny next to that, but every addition lands in the red zone of the PS5 investigation.
- **Pair any angle phase with a removal:** the dead `pw:gvar` values on 31 slabs remove 2,745 permutations with no visual change
  (TEXTURE-VARIANT-REDUCTION doc, table T6) — 28 times the phase-1 cost.

## 5. How angled runs join the spiral stairs

- **What the spiral gives:** our spiral pieces turn through every direction (design C draws a tread every 11.25°; the geometry
  uses bone rotations in 5.625° steps), so a climber faces every heading on the way up. **But the head exit is a door in a
  square wall** (A turret / B tower / C grand all exit on a cardinal side — `_docs/program228/spiral/SITE-*-door-*.png`).
  So a skyway always leaves the tower orthogonally and **turns on a landing outside the door.**
- **Junction rule for a p : q run:** both rail lines must start at block corners on the landing edge. A line touches a corner
  once per period — every cell at 0° and 45°, **every 2 cells at 2 : 1**, every 3 at 3 : 1. So:
  - the landing edge must be at least the band width + 1 cells (2 : 1 band = 3 rows → landing edge ≥ 4, as Panel A's east
    landing, 5 cells);
  - the newels (`*_n0` / `*_n1` for the family) stand on those corners; the landing's `straight` rails end on them (same rule as
    the staged diag, README §7).
- **Headings from one tower:** with phase 1, each of the 4 doors can send a run at 0°, ±26.57° or ±45° from its own axis — 5
  choices per door, 16 headings around the tower. More than 4 runs from one tower needs either more doors (a wider tower) or a
  ring gallery around it (the curve family) from which runs leave anywhere on the ring.
- **Generator rule (CIVITAS / castle / palace):** pick the heading from the target (atan2 of the offset to the far tower),
  snap it to the nearest available heading (16 in phase 1), lay the run in whole periods, and close the remaining offset with
  an orthogonal or 45° leg at the far landing.
- **Not covered:** rising skyways (leaving from a mid-height spiral landing at a slope) need sloped rail cells — a separate
  design, like the ramps.

## 6. Recommended phase-1 set

**Add the 2 : 1 family (26.57° / 63.43°) to the existing `pw:skyway_rail_<wood>` ids.**
- 8 new shapes: `d21_a`, `d21_b` (run, the two cell phases), their mirrors `d12_a`, `d12_b` (63.43°), and 4 ends
  `d21_n0`, `d21_n1`, `d12_n0`, `d12_n1`. `pw:shape` 5 → 13 values. (Names are proposals.)
- Cost: **+96 permutations** (3 woods), **0 new textures** (same kerb / trim / post keys), 8 new geometries.
- Result: **16 headings**, max gap 26.57°, every one within ~4° of 22.5 / 30 / 60 / 67.5°.
- Build list for the builder: 8 geometries (beams split ≤ 16 px uv), 8 collision arrays (12 boxes each), the state table
  (transformation per `cardinal_direction`), generator rule (§5), a test structure (8 shapes × 4 directions on an orientation pad
  + a hub with all 16 headings), and the walk / seal flood test extended to the new pieces
  (`_staging/skyway230/src/validate_skyway230.py`).
- **Phase 2 (if he wants wrap-around galleries):** one curve radius matched to a tower (R 5.5 → +132).
- **Phase 3 (optional):** 3 : 1 (18.43° / 71.57°) → 24 headings (+120, new ids).
- **Not recommended:** exact 22.5° / 30° / 60° — impossible on the grid; their approximations cost 2–4.5× phase 1 for a few
  degrees' difference.

## 7. Witness items and risks (carried from the staged option C, plus new)

1. The staged option C must pass its own PS5 witness first (rotation table, placement trait, kerb below the base, walking
   feel, seams, walk graph — README §8). The 2 : 1 pieces reuse every one of those choices.
2. **New:** the 26.57° beams' rotation sign on PS5 (L-ROT-DIR) — a 4-orientation pad for the 8 new shapes.
3. **New:** walking feel along the stepped barrier: the barrier boxes step 1 px per 2 px; check that the player slides along
   it without catching.
4. **New:** villagers on a 2 : 1 band (BDS civtest with a hub structure).

## 8. Questions for Abs0lum

1. Is "16 directions" (every ~22.5° on average, exact angles 0 / 26.6 / 45 / 63.4 …) enough for "more angles", or do you want
   true 30° / 60° looks (they cost 3× and are still approximations)?
2. Do you want curved galleries around towers (a ring you can leave in any direction), and if so, around which tower size?
3. Should skyways ever climb (leave a spiral at a mid-height landing on a slope)? That is a separate piece family.

## 9. Retro-Sweep (event: new tool `src/make_angles.py`; grid-angle law derived). Suggestions only.

| Subsystem | What changes | Suggestion | Effort | Priority |
|---|---|---|---|---|
| custom blocks / permutations | angle families cost `4 × (2(p + q − 1) + 4)` permutations per wood | use the formula in any future angled-piece plan (roof hips, angled walls, fences) | S | MED |
| worldgen / structures | generators snap headings to the 16-direction compass | CIVITAS road / bridge layout could reuse the same snap (roads at 26.57° read better than 45° zigzags) | M | LOW |
| documentation / lessons | lesson candidate L-GRID-ANGLE: "a straight piece-built line repeats only at whole-number slopes; true 22.5 / 30° never repeat" | add to LESSON-CANDIDATES | S | MED |

**No hit:** terrain caps · trees / canopy · redwood · mobs · atmospherics · PBR / MERS (no new textures) · audio · build tooling
beyond the renderer above.
