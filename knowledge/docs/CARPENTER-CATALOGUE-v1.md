# CARPENTER'S CATALOGUE v1 — the pw:furniture family (living list)
**Stamp: 2026-09-22 · rulings 17:19 (GO) · 18:11 · 18:55 (D-C219, D-C222, D-C223) · status: ROUND 2 SHIPPED (witness 19:46, D-C225) — BP-02 v1.3.184 + RP-04 v1.3.138 (+ Markers 0.1.9 unchanged), awaiting witness.**

The rule of the list: every piece a carpenter can be commissioned to make is a row here — its id, the materials it can be ordered in, its geometry, its collision, whether it seats, the workstation that makes it, and its status (preview / shipped / witnessed). New pieces are appended; nothing is removed. The behaviour code's "custom order" list is generated FROM this table (one row = one orderable item).

## Family law (as built; round 2 amendments marked r2)
- Ids `pw:furn_<piece>_<wood>`; one block per material (homestead convention). Round 1 woods: oak · spruce · dark_oak. Materials by material_instances on RP-04's `pw_mat_<wood>_planks` (boards), `pw_mat_stripped_<wood>` (posts), `pw_mat_stripped_<wood>_top` (end grain), `pw_furn_iron` (fittings — wrought iron authored from the Patrix anvil's forged-iron band, with MER).
- Front = the placer (placement_direction trait, y_rotation_offset 180, the roof/homestead rotation table). Wall pieces (wall shelf, coat pegs) sit against the +z face of their cell at head height; the **mantel sits in the bottom half of its cell** so that, placed over a hearth, its corbels stand on the hearth top (ruling 18:55); **r2 (ruling 19:46): mantel board top 5 on two 2×2 corbels; wall shelf top 8 (the r1 mantel height)**.
- **r2 · L-COPLANAR-1:** no two boxes of a piece share a face plane facing the same way (z-fight); allowed only on the floor underside, a wall piece's back, a joined table's joint — gate `tools/coplanar_audit.py` on the shipped geometry. **r2 · L-RENDER-SS:** every instance `alpha_test_single_sided` (`alpha_test` disables backface culling).
- **r2 construction habits that satisfy the gate:** rails/aprons run BETWEEN legs and sit 0.5 behind the leg faces; back panels sit between the top and bottom boards; crossing members are half-lapped 0.5; octagon bands are stepped 0.1.
- Geometry: `models/blocks/pw_furniture.geo.json` — box-projected uv (a face samples the material by its own cube coordinates, 16 cubes = one tile), **in-tile uv law** (every window inside the 16×16 tile; boxes crossing y = 16 are split), authored in `tools/furniture_geo.py`, previewed by `tools/furniture_render.py`, gated by `tools/verify_furniture.py`.
- Collision (ruling 18:11 "low seats a half block like a slab, maybe 3/4"): bench 8 · stool 10 · barrel seat 10 · chair 12 · table 14 · trestle 14 · shelf/cupboard/dresser 16 · wall pieces none (in-cell selection boxes). One box each (L-COLLISION-ONE-BOX).
- Seats are sittable: custom component `pw:seat` → invisible rideable entity `pw:seat` at the seat surface; sneak to stand; riderless seats are swept every second. Seats are also the CIVITAS **seat-station registry** (`SEAT_BLOCKS` in `scripts/pw_furniture.js`), and `pw:station_seat` (Markers 0.1.9) marks seats in authored buildings that have no furniture.
- Tables auto-join (ruling 18:55): world-aligned `pw:n/e/s/w` → 16 geometries; a joined side drops its apron rail, a corner leg stays only when both its sides are free. Neighbour listener on place/break.
- Made at: the joiner's bench (`pw:station_bench` role); barrel seat = cooper. Recipes / custom orders: not yet — creative for the witness round.

## The table (all 36 blocks re-shipped in .184 with the r2 render method; r2 geometry changes: table, shelf, wall shelf, cupboard, dresser, trestle, barrel seat, mantel)
| # | piece | id (×3 woods) | boxes | height | collision | seats | station | status |
|---|---|---|---|---|---|---|---|---|
| 1 | table | pw:furn_table_<wood> | 9 (16 join variants) | 14 | 14 | — | joiner | .184 (r2 render method) |
| 2 | bench | pw:furn_bench_<wood> | 4 | 8 | 8 (slab) | 1 (sit) | joiner | .184 (r2 render method) |
| 3 | stool | pw:furn_stool_<wood> | 7 | 10 | 10 | 1 (sit) | joiner | .184 (r2 render method) |
| 4 | chair (ladder-back) | pw:furn_chair_<wood> | 9 | 22 | 12 (¾) | 1 (sit) | joiner | .184 (r2 render method) |
| 5 | shelf | pw:furn_shelf_<wood> | 7 | 16 | 16 | — | joiner | .184 (r2 render method) |
| 6 | wall shelf | pw:furn_wall_shelf_<wood> | 3 | 8 (r2; was 13) | none | — | joiner | shipped .184 (r2) |
| 7 | cupboard | pw:furn_cupboard_<wood> | 9 | 16 | 16 | — | joiner | .184 (r2 render method) |
| 8 | dresser (1.5 blocks) | pw:furn_dresser_<wood> | 19 | 24 | 16 | — | joiner | .184 (r2 render method) |
| 9 | trestle | pw:furn_trestle_<wood> | 6 | 14 | 14 | — | joiner | .184 (r2 render method) |
| 10 | barrel seat | pw:furn_barrel_seat_<wood> | 12 | 10 | 10 | 1 (sit) | cooper | .184 (r2: bands stepped) |
| 11 | coat pegs | pw:furn_coat_pegs_<wood> | 4 | 14 | none | — | joiner | .184 (r2 render method) |
| 12 | mantel (low) | pw:furn_mantel_<wood> | 4 | 5 (r2; was 8) | none | — | joiner | shipped .184 (r2) |

## Witness lineup for round 1 (install BP-02 .183 + RP-04 .137 + Markers BP/RP 0.1.9)
1. Content log: `[pw_furniture] ready — 12 pieces x 3 woods, seats 12, tables auto-join` and `custom component pw:seat registered`; no `[Blocks]` lines for `pw:furn_*`; no missing-entity line for `pw:seat`.
2. `/give @s pw:furn_<piece>_oak` for each piece: front faces you; planks/stripped-log/end-grain/iron where the previews put them; the dresser's rack rises into the cell above; the mantel over a hearth reads right.
3. Collision: step onto a bench like a slab; a chair needs a jump; walk through a wall shelf / coat pegs / mantel.
4. Sit on a bench/stool/chair/barrel with an empty hand: do you sit at the seat height (float/sink → `SEAT_Y_OFFSET`), facing the chair's front or its backrest (→ yaw table), does sneaking stand you up, and is the seat free again afterwards?
5. Two tables side by side: shared legs and rails vanish; three in a row: the middle has no legs; break one: the neighbour regrows its legs. A chair next to a table: nothing happens (by ruling).
6. `/give @s pw:station_seat` → the SEA marker.

## Backlog (append as ordered)
- **Mantel tiers** (his 19:16 ruling: plain → moulded → carved → stone-and-timber for upgraded homes; he may source CC0 solid-wood reference as a visual target).
- **Barrel seat lid:** one-piece end-grain top (the 4 stepped bands' rings don't line up — visible in the r2 preview, not a flicker).
- **Chair tuck** (ruling 18:55): crouch-interact slides a chair under the table it faces (`pw:tucked` + a translation permutation; witness the rotation+translation composition first).
- Member thickness pass after the in-game witness (posts 2 → 1.5 if the pieces read heavy at 128 px).
- More woods (every plank wood in RP-04's `pw_mat_*` set) once round 1 is witnessed.
- Storage pieces as containers (cupboard, dresser); item frames on shelves.
- First-load join refresh for structure-placed tables.
- Pieces not drawn yet: bed frame (pw: bed, not vanilla) · cradle · chest (our own) · settle (high-backed bench) · lectern/desk · counter · workbench · plate rack · wash stand · ladder+trapdoor pair · shutters · window seat · trunk · hanging rail · candle stand · pew · stall/booth (the inn) · bar counter · sign bracket · spinning wheel (M) · loom (M) · cart (M).

## Sources
`tools/furniture_geo.py` (authoring truth) · `tools/furniture_render.py` (previews) · `tools/build_furniture.py` (the build) · `tools/verify_furniture.py` (the gate) · previews `furniture-preview-r2-{seating,storage,fittings}.png`, `furniture-join-mantel-preview.png`, **`furniture-r2-vs-r1.png`** · `tools/coplanar_audit.py` (L-COPLANAR-1 gate) · `tools/furniture_r2_preview.py`.
