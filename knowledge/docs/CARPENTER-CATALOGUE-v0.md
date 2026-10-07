# CARPENTER'S CATALOGUE v0 — the pw:furniture family (living list)
**Stamp: 2026-09-22 · ruling 17:19 CT (D-C219: "enough custom furniture to keep a carpenter busy as a trade with custom orders; we'll need to continuously add to this list") · status: PREVIEW ROUND 1 — nothing shipped, no block JSON written.**

The rule of the list: every piece a carpenter can be commissioned to make is a row here — its name, the materials it can be ordered in, its geometry, its size/collision, the workstation that makes it, and the status (preview / witnessed / shipped). New pieces are appended; nothing is removed. The behaviour code's "custom order" recipe list is generated FROM this table (one row = one orderable item).

## Family law (proposed, not yet ruled)
- Namespace `pw:furn_<piece>` with a `pw:material` state (oak / spruce / dark_oak first; every plank wood later); one geometry per piece, materials by material_instances on the RP-04 `pw_mat_*` keys (same mechanism as the homestead families — no new art, Patrix planks + stripped logs).
- Front = the placer (cardinal_direction + y_rotation_offset 180, the roof-family convention). Wall pieces (wall shelf, coat pegs, mantel) sit against the +z face of their cell.
- Collision: the cell (1 block) for floor pieces, `collision_box false` + the cell's top for the low seats? (question below). Dresser = 1.5 blocks tall, collision 1 block (visual overhang, like the flue cap).
- Fittings (handles, hoops, pegs): a single dark-iron stem shared by the family (stand-in in the previews = polished deepslate).
- Made at: the joiner's bench (`pw:station_bench` role) / sawmill tier per the TOOL-LADDER; the trestle and barrel come from the cooper/wheelwright side later.

## The table (round 1 — the medieval set)
| # | piece | id | materials | boxes | height | sits / holds | station | status |
|---|---|---|---|---|---|---|---|---|
| 1 | table | pw:furn_table | oak · spruce · dark oak | 9 | 14 | — (auto-joins with neighbours later) | joiner | preview r1 |
| 2 | bench | pw:furn_bench | oak · spruce · dark oak | 4 | 8 | 2 seats | joiner | preview r1 |
| 3 | stool | pw:furn_stool | oak · spruce · dark oak | 7 | 10 | 1 seat | joiner | preview r1 |
| 4 | chair | pw:furn_chair | oak · spruce · dark oak | 9 | 22 | 1 seat | joiner | preview r1 |
| 5 | shelf | pw:furn_shelf | oak · spruce · dark oak | 7 | 16 | display (later: item frames) | joiner | preview r1 |
| 6 | wall shelf | pw:furn_wall_shelf | oak · spruce · dark oak | 3 | 13 | display | joiner | preview r1 |
| 7 | cupboard | pw:furn_cupboard | oak · spruce · dark oak | 9 | 16 | storage (later: container) | joiner | preview r1 |
| 8 | dresser | pw:furn_dresser | oak · spruce · dark oak | 19 | 24 | storage + plate rack | joiner | preview r1 |
| 9 | trestle | pw:furn_trestle | oak · spruce · dark oak | 6 | 14 | pairs under a board = trestle table | joiner | preview r1 |
| 10 | barrel seat | pw:furn_barrel_seat | oak · spruce · dark oak | 12 | 10 | 1 seat | cooper | preview r1 |
| 11 | coat pegs | pw:furn_coat_pegs | oak · spruce · dark oak | 4 | 14 | 3 hooks | joiner | preview r1 |
| 12 | mantel | pw:furn_mantel | oak · spruce · dark oak | 4 | 16 | over pw:hearth | joiner | preview r1 |

## Backlog of pieces (not drawn yet — add as ordered)
bed frame (pw: bed, not the vanilla bed) · cradle · chest (our own, not the vanilla chest) · settle (high-backed bench) · lectern/desk · counter · workbench · plate rack · wash stand · ladder (the pw: ladder+trapdoor pair) · door (pw: doors exist) · shutters · window seat · trunk · hanging rail · candle stand · table 2-wide / 3-long auto-join · pew · stall/booth (the inn) · bar counter · sign bracket · spinning wheel (M) · loom (M) · cart (M, cooper/wheelwright).

## Sources
Geometry: `tools/furniture_geo.py` (the authoring truth; `to_bedrock_geometry()` writes the shipped file). Previews: `tools/furniture_render.py` → `furniture-preview-{seating,storage,fittings}.png`. Draft geometry export: `pw_furniture.geo.DRAFT.json`.
