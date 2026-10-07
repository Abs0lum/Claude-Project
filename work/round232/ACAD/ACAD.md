# ACAD: Academy II Central Tower moved to the crossing (#23), and the Academy I → II → III upgrade path (#24)

Round 232, GitHub Claude Code session (worker ACAD), 2026-10-07.

- **Workspace:** `w232-ACAD/academy/`. The inputs came from `work/inbox-2026-10-07-1714/academy/`; their md5s were unchanged
  when copied (60848e35… layout, 552dbe80… render).
- **Scope:** design tooling only (Python). **No BP-02 JavaScript was touched.** `diff -rq` of BASE against `w232-ACAD`
  (node_modules and academy/ excluded) is empty, so there is no `ACAD.diff`.
- **Status:** design. Nothing is built or shipped. `academygen` has not been started. Every claim below is static; only his
  eye judges the drawings, and only a future build plus his witness rules anything in.

## Bottom line

- **#23 is done in the layout.** The Central Tower now stands **at the crossing**: x 150–181, z 172–211, the same 32 × 40
  footprint. It sits:
  - between the Entrance Range (gate side) and the Great Hall (lake side) on the gate–lake axis;
  - between two new short arms on the cross axis: **Buttery + Pantry** toward the Hall Garth walk, and **Servery** toward
    the Kitchens.

  The Great Hall keeps its 70 × 72 size and moves 32 rows toward the lake into the slot the tower left (x 182–251). Its
  high table (dais) now faces the lake.
- **7 secrets moved with their hosts** (12, 17, 23, 24, 25, 33, 36) and 2 basement routes (17, 33). No secret changed its
  host room.
- **Checks:**
  - overlaps G / U / B: `[]` / `[]` / `[]`;
  - **0 new problems** against the round-231 baseline;
  - both moved stairs satisfy the spiral law, with headroom ≥ 2 (3 in mid-run, 2.0 at the head landing);
  - every storey's clear height is ≥ 3.
- **24 problems that were already in v2 were found and are listed, not fixed** (§6). These include the Chapel, the Junior
  School and House Towers II–IV, which are not joined to the covered walks, and the Catacombs, which are not joined to the
  tunnels. Each has an exact proposed fix for his OK.
- **#24 is written up** in `ACAD-UPGRADE.md`, with a diagram (`ACAD-files/ACAD-UPGRADE-STAGES.png`):
  - Academy I = 4 × 4 core; Academy II = 6 × 6 (ruled); Academy III proposal A = 6 × 8 along the shore.
  - In-place rules, measured: 0 violations, 6 straddling buildings with 0 blockers, 3 buildings to trim.
  - Two trigger ladders tied to the CIVITAS tiers (recommended: AII-2 at city III, AIII at metropolis I).
  - The land reserve: 448 × 512.
  - 10 questions for him.

## 1. #23: the mechanism and the plan (before any change)

**Where things stood in round 231** (`acad2v2_layout.py`):
- The gate–lake axis runs along x at z 191.5.
- On that axis, in order: Gatehouse (3–22) → Forecourt → Porch Walk → **Entrance Range** (x 110–149, z 172–211) →
  **Great Hall** (x 150–219, z 156–227, ridge along x, dais at the lake end) → **Central Tower** (x 220–251, z 172–211),
  i.e. *behind* the hall.
- The cross axis is the band x 150–219: Schools Wing (z 96–125) – Hall Garth (z 128–153) – hall – Kitchens (z 228–251) –
  Masters' Lodgings (z 252–287).

**What "true to form" means here.** A crossing tower stands where the main axes meet.
- In a cathedral, the tower stands over the crossing of the nave and the transepts.
- At Fonthill Abbey, the great octagon stood where the four arms met.
- In collegiate building, the hall's lower end (the screens) is where the buttery, the pantry and the kitchen way branch off
  across the axis.

So the tower has to sit **between** the Entrance Range and the hall, with arms reaching across to both sides.

**Options weighed:**

| Option | Result | Verdict |
|---|---|---|
| A. Swap the hall and the tower along the axis (tower x 150–181, hall x 182–251) and add two cross arms in the two 32 × 16 gaps beside the tower | The cross is complete: Entrance Range (north arm) / hall (south arm) / Buttery (west arm) / Servery (east arm). No court, cloister or wing moves. The hall's dais goes to the lake end. The kitchen joins the low end through the Servery | **chosen** |
| B. Carve the tower out of the back of the Entrance Range | Displaces the Exam Hall (U), the Porters' cellar (B1) and the routes of secrets 19 and 20. The tower becomes a gate tower, not a crossing tower | rejected |
| C. Carve the tower out of the front of the hall | The hall becomes U-shaped around the tower | rejected |
| D. Move the Entrance Range toward the gate to make room | Breaks the cloister ring: the Gate Cloister is at x 96–99 | rejected |

## 2. #23: what changed (`ACAD-acad2v2_layout.py.diff`, 171 lines)

| Level | Item | Before | After |
|---|---|---|---|
| G | Central Tower | (220, 172, 251, 211) | **(150, 172, 181, 211)** |
| G | GREAT HALL | (150, 156, 219, 227) | **(182, 156, 251, 227)** |
| G | Buttery + Pantry (new arm) | — | (150, 156, 181, 171) |
| G | Servery (new arm) | — | (150, 212, 181, 227) |
| U | GREAT HALL (open roof) | (150, 156, 219, 227) | (182, 156, 251, 227) |
| U | Butler / Servers' loft (new, the arms' upper floors) | — | (150, 156, 181, 171) / (150, 212, 181, 227) |
| U | tower floor: SCR, Exhib., Instr., Clock room, stair-hall void, 4 cross halls | x 220–251 | **x − 70** (x 150–181), same z. The four cross halls now point at the four arms of the building's cross |
| B1 | UNDERCROFT / WINE CELLAR / Serving (under dais) | (150,156,189,227) / (190,156,219,191) / (190,192,219,227) | x + 32: (182,156,221,227) / (222,156,251,191) / (222,192,251,227) |
| B1 | MUNIMENT ARCHIVE (under the tower) | (220, 172, 251, 211) | (150, 172, 181, 211) |
| B1 | Beer cellar / Servery stores (new, under the arms) | — | (150, 156, 181, 171) / (150, 212, 181, 227) |
| B2 | gatehouse → junction tunnel | (23, 191, 235, 192) | (23, 191, 165, 192) |
| B2 | junction → basin tunnel | (236, 192, 295, 193) | (166, 192, 295, 193) |
| B2 | junction → crypt tunnel | (236,193,237,291) + (236,290,282,291) | (166,193,167,291) + (166,290,282,291) |
| MASS | tower / hall / arms | tower (220,…) 60 spire; hall (150,…) 24 gable_x | tower (150,172,181,211) 60 spire; hall (182,156,251,227) 24 gable_x; arms 16 high, `gable_z` (ridges across the axis) |
| data | `STAIRS`, `TOWER_FLOORS`, `TOWER_B1` (new) | — | the stairs whose host moved, as data for the headroom check |

**The B2 junction (secret 36) is still under the tower and still three-way.** Its three tunnels run to the gatehouse, to the
basin / water gate, and to the crypt. The tunnels pass at feet −12 under the B1 rooms, as the old tunnels did. The number of
tunnel × sewer crossings is unchanged at 4: each still needs a culvert when the B2 level is built.

**Secrets relocated** (each moved with its host; host names identical before and after, checked by `acad2v2_check.py`):

| # | Secret | Level | Host | Marker before → after | Route before → after |
|---|---|---|---|---|---|
| 12 | Hall Roof Trusses | U | GREAT HALL (open roof) | (185,192) → (217,192) | (152,192)–(218,192) → (184,192)–(250,192) |
| 17 | Flying High Table | G | GREAT HALL (dais end) | (210,192) → (242,192) | B-route (200,205)→(210,192) → (232,205)→(242,192) |
| 23 | Twin Stair | U | stair-hall void (court) | (236,192) → (166,192) | — |
| 24 | Turning Bridges | U | stair-hall void | (236,186) → (166,186) | (233,186)–(238,197) → (163,186)–(168,197) |
| 25 | Clock-Keeper's Room | U | Clock room | (250,210) → (180,210) | — |
| 33 | Water Stair | G | Central Tower | (248,200) → (178,200) | B-route (248,200)→(248,193)→(296,193) → (178,200)→(178,193)→(296,193) |
| 36 | Tunnel Junction (three ways) | B | junction tunnel under the tower | (236,192) → (166,192) | — |

The other 32 secrets did not move; their hosts are unchanged.

**Stairs and headroom** (`acad2v2_check.py` T1). The spiral law is the one in `tools/spiral_site.py`: one quarter turn rises
1 block, the head tread is flush with the floor, and mid floors satisfy 1 ≤ a < q − 2.
- **Twin Stair (23).** Checked at the largest candidate size, C grand (v1 Q3 is still open; anything smaller fits a
  fortiori).
  - Well x 163–168, z 189–194; wall ring x 162–169, z 188–195.
  - The ring lies inside the tower on G and inside the U stair-hall void (162, 184, 169, 199).
  - It climbs from feet 0 to 54: q = 54 quarters, mid floors at 6 … 48. Law ok.
- **Water Stair (33).** Type A.
  - Well x 177–178, z 199–200, inside the tower on G and inside the MUNIMENT ARCHIVE on B1.
  - It runs from feet −12 to 0 (q = 12) and passes B1 without a door. Law ok.
- **Headroom:** in mid-run, a full turn rises 4, so there are 3 blocks of air over each tread. At the head landing there are
  2.0–2.75 (spiral_site docstring, his ≥ 2 law).
- **Storey clear heights** (all ≥ 3, so vanilla stairs fit too):

  | Level | Clear | How it is set |
  |---|---|---|
  | G | 5 | the U floor slab is at feet 5 |
  | U | 5 | — |
  | B1 | 6 | — |
  | B2 | 4 | design value |
- **The two stairs do not collide:** x 162–169 and x 176–179 are disjoint.

## 3. #23: the checks (`ACAD-files/tools/acad2v2_check.py`, new)

- **What it runs:**
  - overlaps;
  - footprints;
  - covered, paved and open-ground connectivity;
  - U-level clusters;
  - the B2 network;
  - secret hosts and routes;
  - stair fit and headroom;
  - the piece census.
- **Baseline vs now:** run on the untouched round-231 layout (`check-before.txt`) and on the new one, compared against the
  baseline (`check-after.txt`).

```
O1 overlaps(G) = []          O1 overlaps(U) = []          O1 overlaps(B) = []
F1 upper/basement rooms without a G footprint: 0
C4 U-level clusters split: []
T1 storey clear heights: {'G': 5, 'U': 5, 'B1': 6, 'B2': 4} (all >= 2; vanilla stairs need 3: True)
T1 Twin Stair (23) (C, well (163, 189, 168, 194), wall ring (162, 188, 169, 195)): feet 0 -> 54, q = 54 quarters, mid floors [5, 11, 17, 23, 29, 35, 41, 47] law ok; ... hosts ['G:Central Tower=ok', 'U:(162, 184, 169, 199)=ok']
T1 Water Stair (33) (A, well (177, 199, 178, 200), wall ring (176, 198, 179, 201)): feet -12 -> 0, q = 12 quarters, mid floors [] law ok; ... hosts ['G:Central Tower=ok', 'B1:MUNIMENT ARCHIVE=ok']
  secrets changed: 7 [12, 17, 23, 24, 25, 33, 36]; host NAME changed: []
  problems: baseline 24, now 24; NEW 0: []
RESULT: PASS
```

**Connectivity after the move:**
- C1 (covered: buildings + walks): 24 of 35 reached.
- C2 (paved: + courts): 32 of 41 reached.
- The two new arms and the moved tower and hall are all reached in both.
- Everything NOT reached was already unreached in round 231 (§6).

## 4. Images: before and after (all PNG, under `out232/ACAD-files/`)

| File | Size | What it shows |
|---|---|---|
| `ACAD-BA-GROUND.png` | 4842 × 1846 | ground plan: before on the left, after on the right |
| `ACAD-BA-UPPER.png` | 4842 × 1846 | upper plan (feet 6), before / after |
| `ACAD-BA-BASEMENT.png` | 4842 × 1846 | basement (B1 −7, B2 −12, sewer −13), before / after |
| `ACAD-BA-MASSING.png` | 4430 × 1610 | 3/4 massing sketch, before / after |
| `ACAD-BA-CENTRE-GROUND.png`, `-UPPER.png`, `-BASEMENT.png` | 2622 × 1154 each | the central building zoomed (x 88–262, z 84–300, 6 px per block), before / after |
| `before/ACADEMY-II-PLAN-{GROUND,UPPER,BASEMENT}.png`, `before/ACADEMY-II-MASSING.png` | 2406 × 1736 / 2200 × 1500 | round 231, rendered by the untouched scripts (only the output path was swapped, by `run_render.py`) |
| `after/…` (same four names) | same sizes | round 232 #23 |
| `ACAD-UPGRADE-STAGES.png` | 4848 × 1644 | #24: Academy I / II / III-A, buildings coloured by stage |

**Here is what I see. What do you see?**

In the plans the camera looks straight down. The gate side (x 0) is at the TOP, the lake at the bottom, and z 0 on the left.
- **Ground (after), the central part:**
  - Under the Entrance Range there is now a horizontal band of three boxes: "Buttery + Pantry" (orange, narrow, rotated
    label), the brown "Central Tower" (wider), and "Servery" (orange, narrow).
  - The band reaches from the Hall Garth's walk on the left to the Kitchens on the right.
  - Below the band, the GREAT HALL box runs down to the Lake Cloister. Marker 17 is near its bottom (lake) edge; marker 33
    is at the tower's lower right.
  - The old tower slot behind the hall is now the hall's dais end.
  - A white open area remains between the Laboratories and the hall (x 220–251, z 126–155). It was larger before.
- **Upper (after):**
  - The tower's four corner rooms are SCR, Instr., Exhib. and Clock room. Four white cross halls meet at the stair-hall
    void.
  - Markers 23 and 24 sit in the void; they touch each other, as they did before.
  - The left cross hall points at "Butler" and the right one at "Servers' loft". The top one points at the Exam Hall and
    the bottom one into the hall.
  - Route 12 runs down the hall's centre line.
- **Basement (after):**
  - The gate tunnel drops from the Guard cellar to marker 36 in the MUNIMENT ARCHIVE under the tower.
  - From 36, one tunnel runs on down the axis under the Undercroft and the Serving room to the Basin.
  - A second tunnel runs right, under the Servery stores, the Wet larder and the Masters' cellars, then down to the Founders'
    Crypt.
- **Massing (after).**
  - **Camera:** from the gate-side corner. The gate side is nearest; the lake is at the top right.
  - **The tower:** a square brown shaft with a stepped pyramidal spire. It stands at the centre of the composition, with the
    Entrance Range's gable in front of it and the Great Hall's roof behind it (toward the lake).
  - **The arms:** their low transverse gables show on either side of the shaft.
  - **Label fix:** in my first after-render the "Labs" label sat on the tower's spire. The Labs are hidden behind the tower
    from this camera. I fixed the renderer (§5); now "Central Tower" labels the shaft and "Labs" points at the lilac roof
    behind it.

**For your eye:**
- The hall's ridge is about feet 56: 24 plus a roof rise of 32. The tower's shaft top is at 60, so only the spire carries
  the tower clearly above the hall. Should the shaft be taller (Q-C below)?
- Do the two arms read as a crossing to you, or as a bar?

## 5. Render changes (`ACAD-files/ACAD-acad2v2_render.py.diff`, 108 lines)

- `OUT` can be overridden with the environment variable `ACAD_OUT`. The default is still the cloud path.
- Texts:
  - massing subtitle: "(at the crossing, ruling Q3 2026-10-07)" replaces "(v2 position AWAITING ruling)";
  - ground-plan note: "Entrance Range > Central Tower at the crossing > Great Hall; Buttery + Servery = the cross arms".
- **Massing label anchors.** An ID buffer records which box shows at each pixel.
  - If a label's anchor is hidden by a nearer box, its leader moves to that box's nearest visible pixel. That covers the
    spire tips, which are off by 3–4 px of apex rounding.
  - If the visible part is more than 6 px away, the leader goes to the middle of the visible part.
  - This fixed "Labs" sitting on the moved tower's spire.

## 6. Problems already in v2 (found by the new check, NOT changed; proposed fixes for his OK)

| # | Finding | Mechanism (numbers) | Proposed fix (exact) |
|---|---|---|---|
| E1 | The Chapel is not joined to its court | Chapel Court ends at z 290; the Chapel starts at z 292. One open row (z 291) lies between them | Chapel Court → (256, 214, 305, **291**) |
| E2 | Walk to T2, the Junior School, Dorm Range II and House Tower II are off the covered network | The Gate Cloister (96, 80, 99, **291**) starts at z 80 (the T1 side) but stops at z 291. Its mirror image would be z 303 (383 − 80) | Gate Cloister → (96, 80, 99, **303**). It then touches Walk to T2, the Junior School and Dorm Range II |
| E3 | Walk to T3 and Walk to T4 meet their towers only corner to corner and join nothing at the other end | Walk T3 (256, 52, 271, 55) against T3 (272, 20, 303, 51): only the diagonal cells (271, 52)/(272, 51) meet, no shared edge. The Library starts at z 60 (4 rows away). Walk T4 mirrors this (T4 z 332, Chapel ends z 325) | Re-site as bridges: T3 ↔ Library = (276, 52, 283, 59) (to z 63 if the Q5 trim applies); T4 ↔ Chapel = (276, 326, 283, 331). Secret 28's route follows. This is a redesign, so it is his call |
| E4 | The Catacombs (38) are not joined to the B2 tunnels | The crypt tunnel runs at z 290–291; the Catacombs end at z 285 (4 rows) | Stub tunnel (281, 286, 282, 289) |
| E5 | (informational) The Left Cloister runs through the ground floors of the Schools Wing and the Laboratories (z 96–99) | The layout's own `overlaps()` does not count walks | Accept it as an arcade through the range's ground floor (as drawn). Moving the walk is not free: at z 92–95 it would hit the Observatory Wing. This matters for #24: both buildings must be built at the same stage (AI-1) |
| E6 | (informational) An enclosed yard, x 180–219 × z 228–251 (960 m²), can only be reached through buildings | Kitchens / Servery / hall / Infirmary / Masters surround it | Keep it as the kitchen yard |
| E7 | (informational) 4 tunnel × sewer crossings | Tunnels at feet −12 cross the sewer trench at −13 | A culvert at each when B2 is built |

**Trial of E1–E4** (on a throw-away copy, run through the same check; not delivered):
- O1 overlaps stay `[]` on all three levels.
- C2 paved connectivity goes to **41/41**. C5 joins the Catacombs to the B2 network (17/17).
- **16 of the 24 problems clear.**
- One new item is expected: secret 28's marker must move onto the re-sited T3 bridge.
- Still open:
  - The Chapel / T4 / Walk T4 have no COVERED link. They are reached across the open Chapel Court, as drawn; a covered link
    would need one more walk.
  - Informational only: the Gatehouse and the Ice House stand in open courts by design, plus E5 and E6.

## 7. #24: summary (full note in `ACAD-UPGRADE.md`)

- **Footprints:**

  | Stage | Pieces | Blocks | Status |
  |---|---|---|---|
  | Academy I | 4 × 4 = 16 (r1–r4 × c1–c4) | 256 × 256 | ruled |
  | Academy II | 6 × 6 = 36 | 384 × 384 | ruled |
  | Academy III, A (recommended) | 6 × 8 = 48 | 384 × 512, one shore column of pieces each side | PROPOSAL |

  Alternatives for Academy III: B is 8 × 8, which grows into the town square and the lake band; C adds no new footprint.
- **In place.** The frame is fixed at the first stage and never mirrored. Pieces never move. Tier versions only add on open
  ground, raise caps, or make listed re-lays. A new verifier check, R16 "monotone", would diff consecutive versions cell by
  cell. Measured on the v2 layout:
  - 0 violations, after putting the Laboratories in AI-1 (because of E5);
  - 6 straddling buildings with 0 blockers;
  - 3 buildings need a trim to fit Academy I (Q5): Library −4 rows, Observatory Wing −4 rows, Chapel −6 rows.
- **Stages** (ground area added, roles, secrets):

  | Stage | Ground area added | Roles (PROPOSAL) | Secrets |
  |---|---|---|---|
  | AI-1 | 16,396 m² buildings | Rector 1, masters 6, students 24 (staircase lodging in the Masters' range) | 13 |
  | AI-2 | 4,905 m² | — | 9 |
  | AII-1 | 10,754 m² | 4 house towers × 32 = 128 students | 13 |
  | AII-2 | `_t2` only | 192 students | 4 |
  | AIII-1 | shore columns | 288 students | — |
  | AIII-2 | `_t3` only | — | — |
- **Triggers** (TIERS, `pw_civ_clock.js:113`):

  | Ladder | AI-1 | AI-2 | AII-1 | AII-2 | AIII-1 | AIII-2 |
  |---|---|---|---|---|---|---|
  | A (recommended) | town I | town III | city I | **city III** | metropolis I | capital |
  | B (fast) | — | — | — | — | — | **city III** |

  Ladder B brings every stage forward so that Academy III arrives at city III.
  - It is wired like the palace: an `"academy"` step after `tierUpBody`, built as the academy's works.
  - A proposed `/scriptevent pw:academy stage <name>` would let him witness any stage.
- **Land:** reserve the final footprint at the first stage with the palace's reserve helpers.
  - With proposal A: 448 × 512 + 2 margin.
  - Survey: 12 windows of 160 × 160.
- **Name clash:** the `master` role id collides with the craft rank "master" (`pw_civ_people.js:291`), so `fellow` is
  proposed as the internal id.

## 8. What only he can confirm

- **The drawings.** This is a visual, aesthetic call: does the crossing read as the heart of the academy, and is the hall
  better with its dais toward the lake?
- **In game: nothing yet.** There is no generator, so there is no `/scriptevent` to run. The first in-game test comes with
  `academygen` and the witness command proposed in `ACAD-UPGRADE.md` §5.

## 9. Questions (#23-specific; the 10 questions for #24 are in `ACAD-UPGRADE.md` §7)

```
ACADEMY II — crossing tower (round 232 #23) — answers

Q-A  The tower at the crossing as drawn (tower between Entrance Range and hall, hall moved 32 toward the lake,
     dais facing the lake):   a) approved   b) change: ____
     ANSWER: ____

Q-B  The two new cross arms (Buttery + Pantry / Servery, 32 x 16 each, 2 floors + cellar):
     a) keep   b) other uses: ____   c) no arms (leave the two gaps as small yards)
     ANSWER: ____

Q-C  Tower height: shaft 60 + spire (the hall ridge is ~56).   a) keep 60   b) raise the shaft to ____
     ANSWER: ____

Q-D  Fix the problems that were already in v2 (ACAD.md §6) as proposed:
     E1 Chapel Court +1 row  a) yes b) no      E2 Gate Cloister to z303  a) yes b) no
     E3 re-site the T3/T4 bridges  a) yes b) no      E4 catacomb stub tunnel  a) yes b) no
     ANSWERS: E1 __  E2 __  E3 __  E4 __
```

## 10. Deliverables (out232/)

| File | md5 |
|---|---|
| `ACAD.md` (this file) | — |
| `ACAD-UPGRADE.md` | 3a256a226396589746576e555b695601 |
| `ACAD-acad2v2_layout.py.diff` (round-231 inbox copy → `w232-ACAD/academy/acad2v2_layout.py`) | 53b910cbb5c97504c1da028d11ab6283 |
| `ACAD-files/ACAD-acad2v2_render.py.diff` | e6b0078496fbb2612106afe521420ca2 |
| `ACAD-files/tools/acad2v2_layout.py` (new layout) | 1f4109ed700dd31d84dec9930487924d |
| `ACAD-files/tools/acad2v2_render.py` | 4a590a08cde84eecb80e794550680ab0 |
| `ACAD-files/tools/acad2v2_check.py` (new: overlap / connectivity / stairs / secrets / pieces) | af437e01c518a7b050b22936b8325bfc |
| `ACAD-files/tools/acad_stages.py` (new: #24 stage census + diagram) | a01f6000699fb05fb886c53fbf411a0f |
| `ACAD-files/tools/compose_ba.py`, `run_render.py` (new helpers) | 4288246a510253038fc30161784ddacf, 6c001ce014238aebcc5ee21ba9441676 |
| `ACAD-files/check-before.txt`, `check-after.txt`, `stages.txt`, `testrun.txt` | 8954a2f4…, b9e91a1c…, d37b9079…, 10ec6236… |
| images | §4 (16 PNGs) |

**How to re-run:**
```
cd w232-ACAD/academy
python3 acad2v2_check.py . before
ACAD_OUT=<dir> python3 acad2v2_render.py
python3 acad_stages.py . <png>
```

## 11. Full test run (no JS changed; harness on `w232-ACAD`, `node --check` on every script clean, exit 0)

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
test_plateau: test_plateau: 76/76 passed
test_player: test_player: 71/71 passed
test_ramp8: test_ramp8: 7/7 passed
test_rampclear: rampclear force: 9 pass, 0 fail
test_route: test_route: 468/468 passed
test_save: test_save: 40/40 passed
test_shifts: test_shifts: 90/90 passed
test_survey: test_survey: 25/25 passed
test_talk: test_talk: 48/48 passed
test_watch: test_watch: 15/15 passed
test_why: test_why: 33/33 passed
exit=0   (33/33 suites pass; no "SYNTAX FAIL" line, so node --check passed on every *.js)
```
