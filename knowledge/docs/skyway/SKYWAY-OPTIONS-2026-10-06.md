# Diagonal skyways (45-degree catwalks): options, pieces, recommendation (2026-10-06)

**Status: concept images only. Nothing was built, staged or shipped.** No file under `_build`, `_bds`, `tools` or any pack was changed, and no server was started. Everything here lives in `/home/claude/_docs/skyway/`.

His ruling (17:58): *"45-degree pieces, structures only; images first: a castle hall with an open floor and a diagonal skyway overhead."*
Castle reference: `_docs/castle/CASTLE-DESIGN-COMPLETE-2026-10-06.md` §4.2 (the great hall: open roof, mural galleries at feet 7–8, ONE 45-degree skyway "depends on the catwalk block set").
Furniture reference: `_docs/program228/FURNITURE-AND-STAIRS.md`. **We own no railing, balustrade or stair block today.** The rail pieces below would be the first. Any new walkable id must keep the civ walk-graph substrings in mind (`_slab`, `stairs`, `ramp_`).

---

## 1. The images (each one was viewed at full size and corrected before it was finished)

| File | What it shows |
|---|---|
| `OPTION-A-voxel-zigzag.png` | **Option A, plain voxels.** Left: plan, north up, 1 grid square = 1 block, with the collision boxes in red and the walkable area in green. Top right: a 3/4 view from the south, above. Bottom right: an eye-level view standing on the deck. The sample is an 8-column run of vanilla spruce top slabs with a spruce-fence rail. |
| `OPTION-B-custom-diagonal-deck.png` | **Option B, all custom.** Same layout. It uses diagonal-plank deck blocks, a half-deck triangle on each edge, and a diagonal rail one layer up. The red boxes are the stepped multi-box collision that this option needs. |
| `OPTION-C-hybrid-rail.png` | **Option C, hybrid (recommended).** Same layout. Vanilla top slabs are the walking cells, and ONE custom rail cell carries the kerb, fascia, posts, balusters and handrail on the cell diagonal. The red boxes are its single full-cell collision box, which is legal at format 1.21.80. |
| `HERO-castle-hall-skyway.png` | **The great hall with option C.** Interior 12 × 30, walls 13 high to the tie beams, open king-post trusses every 4 blocks, a stone floor, and a dais with a high table. Top: from the floor in the south-east, looking north-west and up. Bottom: from above, with the roof and truss tops removed (tie beams kept) and the south wall cut away. The skyway runs at walking level 8 from the west corner gallery (z 0–11) to an east landing in front of a door. It hangs from the tie beams on 4 iron chains. |
| `EXTERIOR-towers-skyway-bridge.png` | **Two square towers** (8 × 8, heights 22 and 25) joined at walking level 14 by a 10-column option-C bridge that runs at 45 degrees in plan. Each tower has a 2-deep landing on brackets in front of its door, and a 2 × 2 stone pier carries mid-span. Top: from the ground. Bottom: steeply from above, north up. |
| `DETAIL-gallery-junction.png` | **The diagonal-to-orthogonal transition** (hall, west gallery). Left: plan with the collision box of every rail cell and the two newels (yellow) where the rail turns 135 degrees. Right: eye level on the gallery, looking into the skyway. |

Supporting files:
- `geo/pw_skyway_concept.geo.json`: the 9 concept geometries. Format 1.16.0, lowercase ids, all within 30 × 30 × 30 px; bounds are in §4.
- `src/`: the scripts that made every image.
  - `skygeo.py` writes the geometry and checks its bounds.
  - `skylib.py` builds the scenes and renders them. It reuses `tools/block_render.py` (`corners`, `load_faces`) and the verified rotation law in `tools/entity_render.py`; neither file was modified.
  - `make_options.py`, `make_hall.py`, `make_towers.py`, `make_detail.py` make the sheets.

**How the images are made.** Textures come from RP-04 v159 and RP-13 v101. Custom pieces are drawn from the geometry file through `block_render.load_faces`. They are placed with the measured placement law: the file's x axis is mirrored into the world, then the block is turned in quarter turns. Faces get the Bedrock dimming (up 1.0, north/south 0.8, east/west 0.6, down 0.5), taken from each face's true normal so 45-degree cubes shade correctly. There are no shadows and no PBR.

**One concept texture was generated:** `_diag_spruce`, used only in option B. It is `spruce_planks_v1` resampled along the diagonal with dark board seams added. Recipe: `skylib.tex()`.

---

## 2. The geometry problem and the common layout

- **Why a 45-degree walkway steps.** Blocks are axis-aligned, so a 45-degree run is a staircase of cells.
- **The coordinate used throughout.** Number the cells by `d = x − z`; the centreline is d = 0.
  - **Walking band:** cells d ∈ {−1, 0, 1}, three cells per row. The band is 4-connected, so both players and the civ walk graph can cross it.
  - **Rail cells:** d = ±2. The diagonal of each rail cell lies exactly on the straight lines `x − z = ±2` (in block units). So rails drawn on those cell diagonals join end to end into two straight lines.
- **Walking is smooth in every option.** The deck is one flat plane, so a player walking a straight 45-degree line never touches a step. What differs between the options is only the **edge**: what is drawn there and what stops you.
- **Collision boxes are axis-aligned.** A straight diagonal barrier can only be approximated in two ways:
  - (a) whole cells, which gives a zigzag wall;
  - (b) a chain of small boxes touching corner to corner. A 0.6-block player cannot pass a zero-width corner contact, so the chain seals. Arrays of boxes need format ≥ 1.21.130.

| | A: voxel zigzag | B: custom diagonal deck | C: hybrid rail cell (recommended) |
|---|---|---|---|
| Deck | vanilla top slabs on d ∈ {−3..3} | `pw:skyway_deck` (diagonal planks) on d ∈ {−1, 0, 1} + `pw:skyway_deck_half` (alpha-cut triangle) on d = ±2 | vanilla top slabs on d ∈ {−1, 0, 1} |
| Rail | vanilla fence on d = ±2 **and** ±3. Fences and walls join only N/S/E/W, so a diagonal line of single posts leaves walk-through gaps, and each rail step costs 2 cells | `pw:skyway_rail_open` one layer up, on the cell diagonal | `pw:skyway_rail` one layer up, on the cell diagonal, hanging 10 px: a kerb triangle fills the deck notch, a 45-degree fascia covers the kerb's cut edge, then toe board, posts, balusters and handrail |
| Collision | vanilla, exact | decks: one slab box. Rail: **4 stepped 4 × 4 px columns, 24 px tall, touching corner to corner** (within 1.1 px of the drawn rail) → **needs ≥ 1.21.130** | **one full-cell box (−8, 0, −8)…(8, 24, 8) at 1.21.80.** It coincides exactly with the kerb's two visible faces |
| At format 1.21.80 | fine | broken. The rail box is either a full cell (an invisible wall over visible deck) or absent (you walk through the rail and fall) | fine |
| Clear straight-line width | ~2.5 blocks (the fence arms reach x − z = ±1.75) | ~2.5 | **1.41** (the zigzag kerb edge swings out to 2.83). **~2.5** if the array ruling is given (§5) |
| New block ids | 0 | 3 families: deck, deck_half, rail_open (+ straight / corner / bracket) | **1 family `pw:skyway_rail_<wood>` + `pw:skyway_bracket_<wood>`** |
| Geometries | 0 | ~8 | 6 (diag, diag_n0, diag_n1, straight, corner, bracket) |
| New textures | 0 | diagonal-plank set (+ `_mer`, `_n`) and its triangle cut | 0. The kerb's triangle top can reuse the roof gusset `pw_fill_tri_<wood>` alpha-cut texture |
| Look | sawtooth deck edge and sawtooth rail from every angle; reads as a staircase in plan | straight in plan, from below and on the deck; diagonal planking | straight rail, fascia and soffit from below and from outside (how a hall skyway is mostly seen); on the deck, a 2 px zigzag kerb at your feet under a straight handrail |

**About the 1.41 width in C.** Clear width is set by the narrowest straight strip a player can walk. In C at 1.21.80 that is the band d ∈ {−1, 0, 1}: 1.41 blocks, about 1.4 m, a normal medieval gallery width. To make it wider, add a row: d ∈ {−2..2} with rails on d = ±3 gives 2.83.

---

## 3. Pieces list (option C, as drawn in the hero, exterior and detail images)

| # | Piece | Id / geometry (concept) | States | Collision at 1.21.80 | Notes |
|---|---|---|---|---|---|
| 1 | **Straight diagonal deck** | vanilla `minecraft:spruce_slab` (top), or any of our slabs, on d ∈ {−1, 0, 1} | — | vanilla slab | 0 new. Walk graph: `_slab` = half floor, already supported |
| 2 | **Diagonal rail cell** | `pw:skyway_rail_<wood>` / `geometry.pw_skyway_rail_diag` (7 cubes) | `pw:shape = diag`, `minecraft:cardinal_direction` ×4 (which corner is the walkway side: SW / NW / NE / SE) | full cell, 24 px | Placed one layer above the slabs (its base = the walking surface), so the 24 px box stands 1.5 blocks above the deck, the same as a fence. Hangs to −10 px. Bounds 18.5 × 29.5 × 18.5 px |
| 3 | **Diagonal-to-orthogonal transition / rail end** | same family, `geometry.pw_skyway_rail_diag_n0` / `_n1` (9 cubes) | `pw:shape = diag_n0` (newel at the run's start corner) / `diag_n1` (end corner) | full cell | The 135-degree turn happens at a 5 × 5 px newel on the cell corner. The orthogonal landing rail stops at that same point (detail image). The same newel ends a free rail. Bounds 20.5 × 29.5 × 20.5 px |
| 4 | **Landing / gallery edge rail** | same family, `geometry.pw_skyway_rail_straight` (5 cubes) | `pw:shape = straight` ×4 | thin box (5, 0, −8)…(8, 24, 8) | The first railing block we own. Also usable on any straight gallery, stair well or balcony |
| 5 | **Landing corner** | same family, `geometry.pw_skyway_rail_corner` (10 cubes) | `pw:shape = corner` ×4 | **full cell** at 1.21.80 (an L needs 2 boxes); 2 boxes with the array | Landing ends. At 1.21.80 the corner cell is not walkable |
| 6 | **Landing deck** | vanilla top slabs | — | slab | — |
| 7 | **Supports: wall bracket** | `pw:skyway_bracket_<wood>` / `geometry.pw_skyway_bracket` (wall post, bearer, 45-degree strut about z) | `cardinal_direction` ×4 | ⚠ open: a full-cell box would block the cell under the deck; probably no collision, or a box at the post only | Under landings and galleries (hall and towers). Bounds 15.4 × 24 × 4 px |
| 8 | **Supports: hangers** | vanilla `minecraft:chain` from a tie beam down to a rail post | — | vanilla | Each rail cell's post stands at the cell centre, on the rail line. So a chain dropped straight above any rail cell lands on a post. The hall uses 4, where the rails pass under the trusses at z 6, 10 and 14 |
| 9 | **Supports: pier** | stone bricks under four walking cells | — | — | Exterior bridge mid-span. An axis-aligned 2 × 2 pier sits naturally under the diagonal |

- **Count for option C:** 2 new block families per wood.
  - `pw:skyway_rail_<wood>`: 5 shapes × 4 directions = 20 permutations.
  - `pw:skyway_bracket_<wood>`: 4 permutations.
  - Woods to start with: spruce, oak, dark oak. That is 6 ids and 6 geometries.
- **Materials:** `kerb` and `kerb_tri` use the deck's wood (`kerb_tri` = the alpha-cut triangle); `fascia` and `rail` use dark oak planks; `post` uses stripped dark oak log; everything maps to `pw_mat_*`.
- **Placement sugar (later):** a `pw_companion.js`-style rule. Placing a rail cell next to a diagonal run picks the direction automatically, and placing one where the run meets an orthogonal rail picks `_n0` / `_n1`.

---

## 4. Concept geometry bounds (`geo/pw_skyway_concept.geo.json`; all ≤ 30 px per axis)

| Geometry | Cubes | Extent x × y × z (px) | y range |
|---|---|---|---|
| `geometry.pw_skyway_rail_diag` | 7 | 18.47 × 29.5 × 18.47 | −10 … 19.5 |
| `geometry.pw_skyway_rail_diag_n0` / `_n1` | 9 | 20.49 × 29.5 × 20.49 | −10 … 19.5 |
| `geometry.pw_skyway_rail_straight` | 5 | 3.5 × 17.5 × 16 | 0 … 17.5 |
| `geometry.pw_skyway_rail_corner` | 10 | 16.5 × 18.5 × 16.5 | 0 … 18.5 |
| `geometry.pw_skyway_bracket` | 3 | 15.42 × 24 × 4 | 0 … 24 |
| `geometry.pw_skyway_rail_open` (B) | 5 | 18.47 × 17.5 × 18.47 | 0 … 17.5 |
| `geometry.pw_skyway_deck_half` (B) | 2 | 18.12 × 12.5 × 18.12 | 4 … 16.5 |
| `geometry.pw_skyway_deck_diag` (B) | 1 | 16 × 8 × 16 | 8 … 16 |

- **Rotations used:** `[0, 45, 0]` on the diagonal cubes and `[0, 0, 45]` on the bracket strut. Each sign was chosen numerically against `entity_render.transform` plus the x-mirror placement law, then confirmed in the plan renders: the rails lie on the cell diagonals and the kerb sits on the walkway side in all 4 orientations.

---

## 5. Recommendation

**Option C**, with its collision tied to the format ruling.

1. **Build it at 1.21.80 now.**
   - Only one new block family does the work; the deck is plain slabs, so the walk graph, PBR and the existing generators need nothing new.
   - Collision is exact: one full-cell box per rail cell, matching the visible kerb faces. Nothing is invisible and nothing can be walked through.
   - It reads straight where a hall skyway is mostly seen: from the floor (straight fascia, soffit and handrail) and from outside. The only zigzag is a 2 px kerb at your feet.
2. **Ask Abs0lum whether the spiral-stair exception (≥ 1.21.130 multi-box collision) may extend to `pw:skyway_rail`.** With it, the same block takes B's stepped boxes and the kerb becomes walkable deck:
   - clear width rises from 1.41 to ~2.5;
   - the corner piece gets its proper L-shaped collision;
   - the block id and geometry stay the same; only the kerb's height and the collision change.

**Why not B:** it looks best (straight on the deck too), but it needs 3 new families, a new texture set, and the array format just to stop players walking through the rail. Everything it adds on top of C is the diagonal planking.

**Why not A:** it costs nothing, but the 2-cells-per-step fence and the sawtooth deck read as a staircase from every angle. It is not what was asked.

---

## 6. Risks and open items (all for his ruling or a witness test; nothing was decided or built)

1. **⚠ Locked invariant.** Custom blocks are locked at format 1.21.80. C works inside the lock. The upgrade in §5 needs the same exception already granted to the spiral stair. **The 1.26.60 break** noted in Program 228's Retro-Sweep also applies: from 1.26.60, only array `collision_box` is accepted.
2. **Geometry below the block base.** The rail cell draws 10 px below y = 0, into the empty notch cell under it.
   - It is within the 30 px bounds, but the only precedent seen is Umsoea's −3.1 px.
   - **Witness item:** confirm on PS5 that it renders, and that it is not culled when the cell below is air.
   - Fallback: split the kerb and fascia into a second block in the deck layer, `pw:skyway_kerb`.
3. **Rotation sign (L-ROT-DIR / D-C197).** The 45-degree signs were derived from our tools, not seen on hardware. The first build needs a 4-orientation test pad viewed on PS5. The alpha-cut kerb triangle must also show on the walkway side in every orientation (the UV turns with the block).
4. **UV beyond 16 px.** The 22.6 px rotated rail and fascia faces use a `uv_size` up to 22.63. Verify how Bedrock tiles block UVs past the texture edge; otherwise split each long cube into two 11.3 px halves.
5. **Collision feel at 1.21.80.** The player stops at the kerb face, between 0 and 0.7 blocks short of the handrail. The kerb is the visual cue. **Witness item:** does this feel like a wall or like a rail?
6. **Walk graph.** The rail ids contain none of `_slab`, `stairs`, `ramp_`, so they are solid, and the 3-cell band is 4-connected. **ASSUMPTION:** `pw_civ_walk.js` paths across it in N/S/E/W steps; a villager then zigzags along the band, which costs about √2 more path length. **Witness item:** a villager crossing the hall skyway on BDS.
7. **Coplanar faces.** At the notch, the kerb's leg faces meet the neighbouring slab faces back to back. They face opposite ways, so they should not z-fight. Run `coplanar_audit.py` anyway.
8. **Bracket collision** is undecided (pieces table, row 7).
9. **Not covered:**
   - a rising diagonal (a sloped skyway would need diagonal ramp cells);
   - angles other than 45 degrees (2 : 1 runs at 26.57 degrees);
   - widening by 2 rows (5-cell band, rails on d = ±3) needs no new pieces and is a generator choice.
10. **Hall clearances** as drawn:
    - walking level 8, tie beams at 12: 4 blocks of headroom, chains in the cells above the rail;
    - the truss knee braces start at y 10.4: 2.4 blocks of headroom on the gallery;
    - **the hall template must keep the trusses' bottoms above y 10.**

---

## 7. Retro-Sweep (new tool or pipeline built: `skylib.py`; findings). Backlog suggestions only, nothing implemented

| Subsystem | What changes | Suggestion | Effort | Priority |
|---|---|---|---|---|
| build / verification tooling | `tools/block_render.render` drops every face that has a vertex behind the camera (there is no near-plane clipping). Interior renders lose long faces such as roof decks, purlins and ridge beams that pass behind the eye. This happened in the first hero render here and was fixed in `skylib.render` | Port the polygon near-plane clip (~20 lines) into `block_render.render`, then re-check earlier interior previews (palace, castle, spiral) for missing long faces | S | med |
| build / verification tooling | `block_render.render` clamps UVs and does not wrap them, so one big face cannot tile | Optional wrap flag (as in `skylib`) | S | low |
| custom blocks / permutations | A rail family is the first railing or balustrade we own | `rail_straight` / `rail_corner` also serve gallery, stair-well and balcony edges in palace, castle and manor templates | S | med |
| worldgen / mcstructures | The castle §4.2 hall currently has a hip roof and no galleries | The hero layout gives concrete numbers for the hall generator: 12 × 30, trusses every 4, galleries at walking level 8 on brackets, the skyway band d = x − z + 4 | M | per castle program |
| documentation / lessons | Lesson candidates: (1) "vanilla fences and walls never join diagonally, so a voxel diagonal rail costs 2 cells per step"; (2) "a diagonal barrier is legal at 1.21.80 only as whole-cell boxes; a straight diagonal needs corner-touching stepped boxes (≥ 1.21.130)" | Add both to the lesson candidates for his confirmation | S | med |

**No hit:** terrain caps · trees / canopy / falling tree · redwood biome · mobs (RP-07) · atmospherics / sky / fog · PBR / MERS (C adds no texture; B would) · scripts (BP-01 / 02 / 03; walk-graph naming already covered in §6.6) · audio.
