# Furniture skins check + import plan (2026-10-07, round 231, worker FURNITURE)

Answers his 00:23 CT ruling: *"wants them all, but check the skins — books on shelves render as wood; cosmetic
accessories (books, pinned notes, lampshades) need their own textures. He will test tinting after."*

Research, textures and previews only. **Nothing is staged into any pack.** No build, no server, no Drive upload.

---

## 1. What he saw, and why (mechanism)

He is right: on the 10-06 sheets every book is wood. The cause is the automatic re-skin in
`_docs/furniture/renderer/geo_render.py` (10-06 version, backup `_garbage/FURNITURE-pre/renderer/geo_render.py`,
md5 `35e20b5d…`), `classify_face()` lines 231–270:

| Line (10-06 file) | Rule | Effect on the sheets |
|---|---|---|
| 252 `if mean_rgb is None or 'wood' in toks: return woodish` | A face whose source texture is missing gets wood | **95 of 155 pieces have no source PNG** (Feudal/Craftopia atlases are not in the RPs), so every face of them, books, pages, cushions, lampshades, chalk, statues, became board / post / end |
| 257 `if 'stone' in mode` comes AFTER line 252 | Stone mode only works when a source PNG exists | #93 stone lamp bracket rendered as **wood** |
| 236–240 `iron` / `thin_iron` modes | Every thin cube is iron | #142 pitchfork shaft, #138 virginal case and stand became iron |
| 261–263 `s < 0.16, v < 0.42 → iron` | Dark source colours read as iron | #15 and #114 stool legs/seats became iron |
| 244 `keep` / mode `prop` | Keeps the SOURCE texture | 32 pieces kept source-PNG faces (#9, 32, 34, 37, 38, 41, 45–47, 49–51, 71, 76, 77, 79, 88, 94, 99, 109, 116, 117, 119–123, 134–136, 138, 143): they would have shipped third-party PNGs |
| `allcloth=red` | Every face cloth | #131/#132 curtain **pole, brackets and finials** became red cloth |

So the 10-06 previews were "shape previews" (as that doc said), but the default they showed for accessories was wrong.

---

## 2. The table (all 155 candidates)

Every candidate was rendered with one flat colour + number per cube (`skins-1007/partid/PARTID-01..26.png`,
26/26 pages viewed). For each part: the texture the 10-06 plan gives it **now**, and the texture it **needs**.

**Summary**
- **121 pieces have accessory parts** that need their own texture (2 of them, #35 fire irons and #139 anvil,
  are already correct iron).
- **3 pieces need only a wood fix** (#15, #114, #142: misread as iron).
- **31 pieces are all wood** and correct as they are: 8, 14, 18, 19, 20, 21, 22, 24, 25, 26, 27, 30, 40, 53, 73,
  74, 82, 89, 98, 101, 102, 103, 104, 111, 113, 115, 126, 145, 146, 147, 153.
- Pieces per needed texture: iron 21 · **book 15** · **cloth 14** · food 14 · **brass 12** · paint 7 ·
  **paper 6** · ceramic 5 · log 4 · flame 4 · wicker 4 · glass 4 · stone 4 · chain 4 · candle 3 · ivory 3 ·
  hearth 3 · leaf 3 · **slate 3** · chalk 3 · straw 3 · mirror 2 · rug 2 · game 2 · cask 2 · **globe 2** ·
  amethyst 2 · gold 2 · leather 1 · copper 1 · cork 1 · target 1 · arrow 1 (and 23 pieces with a wood fix on some part).

The full per-part table is in **Appendix A** (229 rows) and machine-readable in `skins-1007/skin_table.json`.
Cube numbers `k` are the numbers printed on the PARTID sheets.

**Rows for the 12 recommended picks** (all correct in the new previews, section 4):

| Pick | # | Accessory parts (k) | Now | Needed |
|---|---|---|---|---|
| 1 | 127 throne | seat 7, back panel 4 | wood | cloth (tint, red shown) |
| 2 | 32 hearth | firewood 8–10, embers 1–3, ash 4, back wall 7 (inner face) | stone | HEARTH v2 keys: log_lit / log_end_lit / embers / ash / soot, + 2 ADDED flame planes |
| 2 | 33 chimney | flue opening 3 | stone | soot |
| 3 | 57 library bookcase | books 8–11, open-book boards 12–13, pages 14–19 | wood | book, paper |
| 4 | 61–64 bookcases | books (all 2×6×5 cubes: 8 / 8 / 7 / 5 books) | wood | book |
| 5 | 71 book on stand | boards 0, 4; pages 1–3, 5–7; clips 10–11 | SOURCE PNG | book, paper, brass |
| 6 | 76 globe | globe 7; meridian + pin 3–6; stand 0–2 | SOURCE PNG | globe, brass, wood |
| 7 | 78 telescope | tube 0, sleeve 1 | wood | brass (+ lens on the ends) |
| 8 | 79 blackboard | writing surface 5; frame 2, 3, 6, 7; back 4; chalk 0–1 | wood / SOURCE PNG | slate, chalk, wood |
| 9 | 1 / 3 / 4 drawers | pulls 17–18 / 12–13 / 7–8 | wood | brass |
| 10 | 38 cask | staves 2–5 (hoops were painted in the source); heads 0, 1, 6 | wood / cloth:silver | cask (staves + iron hoops); heads planks |
| 11 | 96 awning | canopy 0, valance 2, flaps 3–5 | wool yellow / white | cloth (2 tints) |
| 11 | 101 X-trestle | none | wood | wood (correct) |
| 12 | 131 / 132 curtains | pleats; pole 4–5 / 0, 19; brackets 0–1 / 2–3; finials 6–7 / 17–18 | all red cloth | cloth; pole = wood; brackets = iron; finials = brass |

---

## 3. Texture plan

### 3.1 How the UVs map (what custom blocks allow)

- Our furniture geometry already uses **per-face `material_instance` keys** (`board / post / end / iron`, 924
  per-face keys in `rp04-159/models/blocks/pw_furniture.geo.json`), and each block's `minecraft:material_instances`
  maps each key to **one** texture (engine law: one texture per key; variation arrays collapse to the first).
- The candidates' cubes are separate per part (every book, pull, page, pleat is its own cube), so **every
  accessory face can get its own key**. Nothing in the geometry forces sharing.
- **Chosen method: both, combined.** One key per material class (`book`, `paper`, `cloth`, `brass`, `slate`,
  `globe`, `cask`, hearth keys), and **per-face UV into a small 128 px atlas** inside that key's texture to pick the
  region (which spine colour, cover, page edge, written page, lens, chalk). One key gives eight book colours.
- Per-face UV units: the geometry keeps `texture_width/height = 16` (as now), so a region of a 128 px atlas is
  1/8 of 16 units per 16 px. Example book spine colour *i*: `uv [2i, 0]`, `uv_size [2, 8]`.
- Book faces by local cube axes: faces across the thinnest axis = **cover**, across the middle axis = **spine**,
  across the longest axis = **page block** (`book_faces()` in `_staging/furniture231/tools/skin_sheets.py`).
- Render methods: all new keys `alpha_test_single_sided` like the existing ones; `flame` adds
  `face_dimming: false, ambient_occlusion: false` (copied from `pw:hearth_*`). Glass (later, for jars/bottles) is
  the only key that needs `blend`.

### 3.2 Textures

| Key | Texture | Source | Size | Regions | New atlas px |
|---|---|---|---|---|---|
| `book` | `pw_furn_book` | Claude-generated (placeholder now) | 128² | 8 spines (oxblood, green, navy, calf, tan, black, plum, vellum) · 8 covers · page block · dark leather | 16,384 |
| `paper` | `pw_furn_parchment` | Claude-generated | 128² | written page · pinned note · plain · scroll end · ink lines | 16,384 |
| `cloth` | `pw_furn_cloth` (near-white twill) + one **tinted key per colour** | Claude-generated | 128² | whole | 16,384 (+? per tint, see 3.3) |
| `brass` | `pw_furn_brass` | Claude-generated | 128² | brass · dark brass · lens | 16,384 |
| `slate` | `pw_furn_slate` | Claude-generated | 128² | board · chalk · chalk writing | 16,384 |
| `globe` | `pw_furn_globe` | Claude-generated | 128² | 4 map panels (sepia) | 16,384 |
| `cask` | `pw_furn_cask_spruce` | made FROM our `spruce_planks_v0` + `pw_furn_iron` | 128² | staves + 2 hoops | 16,384 per wood |
| `log` / `log_end` / `embers` / `bed` / `soot` / `flame` | `pw_hearth_log_lit`, `pw_hearth_log_end_lit`, `pw_hearth_embers`, `pw_hearth_ash`, `pw_hearth_soot`, `pw_hearth_flame` (flipbook) | **RP-04, already shipped (HEARTH v2)** | — | — | 0 |
| `stone` | `pw_mat_stone_bricks` (or any `pw_mat_*`) | RP-04, have | — | — | 0 |
| `iron` | `pw_furn_iron` | RP-04, have | — | — | 0 |

**Top-12 cost:** 7 new 128² colour maps = 114,688 px (0.11 Mpx); with MERS + normal companions at import ≈
0.34 Mpx. Last measured atlas use: **56.2 Mpx used keys** (`_docs/blocks/ATLAS-BUDGET.json`, 10-02/10-07 mirror)
against the ~60 Mpx budget, so it fits, but every new texture is counted in the build gate.

**Later, for the other candidates** (about 10 more 128² maps): `pw_furn_glass` (blend) · `pw_furn_mirror` ·
`pw_furn_wicker` · `pw_furn_food` (one atlas: potatoes, apples, carrots, bread, roast, ham, eggs, stew) ·
`pw_furn_paint` (emblems, canvas) · `pw_furn_rug` · `pw_furn_game` (chequer, ivory/ebony men, keys) ·
`pw_furn_target` · `pw_furn_arrow` · a cork region. Zero-cost reuses from RP-04: `chain1`, `hay_block_side/top`,
`amethyst_block`, `copper_block`, `white_candle_lit`, oak leaves, `pw_mat_white_terracotta` / `pw_mat_hardened_clay`
(ceramic), `pw_mat_calcite` (marble statues). **Paintings #134/#135** should go through the existing `pw:artwork`
entity system (D-C571: per-work texture, no atlas cost) instead of a block texture.

**Every placeholder is labelled.** Files: `_staging/furniture231/textures_placeholder/` (7 PNGs + `regions.json`),
contact sheet `skins-1007/PLACEHOLDER-TEXTURES.png`. Made by `tools/gen_accessory_textures.py` (procedural, seed 231).
They are colour maps only; MERS (4-value) + normal companions are made at import. Provenance ledger line:
"Claude-generated, recipe = gen_accessory_textures.py seed 231" (no restricted source).

### 3.3 Tinting (his test)

What Bedrock offers (Bedrock Wiki, block tinting):
- `minecraft:material_instances` → `tint_method` is **biome-only** (`grass`, `default_foliage`, `birch_foliage`,
  `evergreen_foliage`, `dry_foliage`, `water`). It cannot pick a cloth colour; a red curtain would change colour
  by biome. Not useful for cloth.
- `terrain_texture.json` → `"tint_color": "#rrggbb"` on a texture entry: a fixed multiply tint. **This is the one
  to test**: one near-white `pw_furn_cloth` registered as `pw_furn_cloth_red`, `…_blue`, `…_green`, `…_cream`, each
  with its own `tint_color`.
- What his test should answer: (1) does `tint_color` apply on a custom-block material instance on PS5; (2) does it
  still apply when the texture has a `texture_set.json` (PBR); (3) does each tinted key cost its own atlas tile.
- Fallback with zero risk and zero px: the RP-04 `wool_colored_<colour>` keys (they read as knitted wool).
- The preview sheets show tint as a plain multiply (labelled "multiply-tint preview").

---

## 4. Corrected preview sheets (viewed)

`_docs/furniture/skins-1007/FURN-SKIN-A.png`, `-B.png`, `-C.png`: 20 geometries (the 12 picks with their variants).
Each cell: left = 10-06 re-skin, middle = accessory keys applied (camera: front-right 3/4 from above, yaw 35°),
right = back-left view (yaw −145°). Per-cube assignments: `skins-1007/skin_assignments.json`. **No source PNG is
sampled in any "after" view** (checked per piece: `source_texture_leak: false` for all 20).

What I see on them (my reading; please check):
- **A:** throne with red seat and back panel; hearth with burning logs and flame inside the stone surround;
  chimney with a black flue opening; library bookcase with coloured standing books and an open written book;
  book on stand with written pages, green boards and wood stand; globe with a sepia map and brass meridian;
  telescope with a brass tube.
- **B:** four 1-block bookcases with mixed-colour books (some bays are empty in the source geometry);
  blackboard with a slate face, chalk lettering and an oak frame (the lettering reads mirrored in the preview,
  see 6.3); cask with two dark iron hoops; nightstand with two brass pulls.
- **C:** drawer chests with brass pulls; awning red with cream flaps; X-trestle unchanged; curtains red with a dark
  oak pole, iron brackets and brass finials.

Renderer change (needed for this, backward compatible, 10-06 sheets unaffected): `geo_render.py` md5 `3ca8139e…`
adds `cube_mat` overrides, `rgb:/tile:/fit:` accessory materials, per-cube material and centre output, and skips the
source alpha cut-out for overridden faces (that cut-out had hidden the blackboard surface in a first pass). Regression: #57, #79, #32, #76 render pixel-identical to the 10-06 renderer without overrides (max diff 0).

---

## 5. Import plan (nothing staged; for the build after his picks)

Ids follow the 10-06 convention `pw:furn_<piece>_<wood|colour>`, block format 1.21.80, mandatory `minecraft:geometry`,
geometry ids lowercase in `pw_furniture2.geo.json` at format **1.16.0** (P13), `minecraft:cardinal_direction`
placement like `pw:furn_chair_*`. Accessory keys added to `material_instances` per piece.

### 5.1 The 12 picks (one wood / one colour each)

| Pick | Geometry | Block id | Extra state | Permutations | New keys |
|---|---|---|---|---|---|
| 1 | #127 | `pw:furn_throne_dark_oak` | — | 4 | cloth |
| 2 | #32 (+2 flame planes) | `pw:furn_hearth_stone_bricks` | — (static, lit look) | 4 | log, log_end, embers, bed, soot, flame, stone |
| 2 | #33 | `pw:furn_chimney_stone_bricks` | — | 4 | soot, stone |
| 3 | #57 | `pw:furn_bookcase_tall_dark_oak` | — | 4 | book, paper |
| 4 | #61–64 | `pw:furn_bookcase_dark_oak` | `pw:variant` ×4 | 16 | book |
| 5 | #71 | `pw:furn_book_stand_dark_oak` | — | 4 | book, paper, brass |
| 6 | #76 | `pw:furn_globe_oak` | — | 4 | globe, brass |
| 7 | #78 | `pw:furn_telescope_oak` | — | 4 | brass |
| 8 | #79 | `pw:furn_blackboard_oak` | — | 4 | slate |
| 9 | #1 | `pw:furn_nightstand_oak` | — | 4 | brass |
| 9 | #3 / #4 (+ R = mirrored L geometry) | `pw:furn_drawers_oak` | `pw:join` L/M/R ×3 | 12 | brass |
| 10 | #38 | `pw:furn_cask_cradle_spruce` | — | 4 | cask |
| 11 | #96 | `pw:furn_awning_red` | — | 4 | cloth (2 tints) |
| 11 | #101 | `pw:furn_stall_table_spruce` | — | 4 | — |
| 12 | #131 / #132 | `pw:furn_curtains_red` | `pw:open` ×2 | 8 | cloth, brass |
| | | **15 block ids** | | **84** | |

Options: hearth with the `pw:hearth` phases (5) → 20 instead of 4 (+16); nightstand drawer `pw:open` (#2) → +4;
each extra wood for a wood piece = +4 per id (bookcase +16, drawers +12); each extra cloth colour = +4 (curtains +8).
**Top-12 range: 84 to about 150.**

### 5.2 All 155 ("wants them all")

Folding states into families (nightstand + open, coffer + open, curtains closed/open, drawers L/M/R, shelf-table
join, bookcase variants 61–64, book piles 67/68, signposts 105/106, easels 82/83) and dropping #19–21 (covered by our
own joining table): **about 141 block ids → about 624 permutations** with one wood/colour each (+16 with hearth
phases). If every wooden piece came in 3 woods: about 1,900. Our BPs defined **57,512** at 1.3.229 (already above
the 50,000 red flag; ramps 21,760 are the driver); furniture adds 0.1–3.3 % of the 65,536 limit. Recommendation:
one wood per piece unless he asks, colours by tinted keys rather than by states.

### 5.3 Per-piece work at import (beyond the texture keys)
- Re-base pieces that dip below y0 (#96 awning, #131/#132 curtains; also #23, #120, #126).
- #32/#34/#36 need 2 ADDED crossed flame planes; #133 needs 4–8 ADDED candle cubes; #11 / #92 a candle cube.
- #76 globe is a cube in the source; to read round, re-author as 3 intersecting boxes (+2 cubes).
- Over 24 cubes (#42, #43, #75, #84, #87, #90, #99, #100, #108, #130) need re-authoring with a contents texture.
- Thin-plane pieces (#57 open pages, #71 pages, curtain pleats, chalk marks) stay planes, single-sided like now.
- Gates as in the 10-06 plan (verify_furniture, coplanar audit, `geo_ref_check.py`, permutation count, BDS load),
  then a converted-geometry preview round for his markup, then PS5 witness of facing and of handed textures.

---

## 6. Honest limits

1. **Placeholders.** The 7 textures are procedural stand-ins to judge placement and colour, not final art.
2. **#23 table clutter** (12 small cubes) was not resolved from the ID sheet; it is marked "identify at import".
3. **Handed textures.** Lettering on the slate reads mirrored in the preview (north face). Engine X-mirror law:
   model +x renders world west. Globe map, slate writing and painted signs are checked on PS5 at first placement and
   flipped with a negative `uv_size` if needed.
4. `tint_color` on custom blocks, with PBR, and its atlas cost are **untested** (his test).
5. Mixed render methods in one block (glass `blend` + wood `alpha_test`) are untested; only needed for jars/bottles.
6. Flipbook animation on a custom-block key with per-face UV (hearth flame) is believed to work (the `pw:hearth_*`
   blocks already use `pw_hearth_flame`); the added flame planes still need a witness.
7. Incident: running `tools/atlas_budget.py` to read the budget rewrote `_docs/blocks/ATLAS-BUDGET.json` with a
   wrong-stack result (no `PW_STACK`). Restored at once from the knowledge mirror (md5 `ca96453a…`, identical in both
   10-07 mirrors); the accidental copy is in `_garbage/FURNITURE-pre/`.

## 7. Questions for him
1. **Cloth colours:** which colours per piece? (Shown: throne red, curtains red, awning red with cream flaps.)
   Period palette suggestion: red, blue, green, cream, ochre.
2. **Tint test:** will you test `tint_color` keys yourself, or do you want a TestRunner lineup that places the same
   curtain in 4 tints + the wool fallback side by side?
3. **Hearth:** decor only (always lit, 4 permutations) or the full `pw:hearth` fuel/light cycle (20)?
4. **Woods:** one wood per piece (as shown), or 3 woods for bookcases and drawers (+28 permutations)?
5. **Books:** fill the empty bays of #62–#64 with extra book cubes (+3–6 cubes each)?
6. **Globe:** keep the source cube shape, or round it with 2 extra boxes?
7. **Food / props group** (14 pieces): new food atlas (our art), or keep their source PNGs as RESTRICTED lines?

## 8. Retro-Sweep (failed assumption corrected: automatic re-skin hides accessories)
| Subsystem | Hit | Suggestion | Effort | Priority |
|---|---|---|---|---|
| build / verification tooling | Auto material classification defaulted missing-source faces to wood, `stone` was ignored without a PNG, `keep` leaked source PNGs | Furniture preview gate: fail any sheet whose pieces still sample a source PNG (`source_texture_leak`) or have an accessory part on a wood key; use `cube_mat` assignments as the import truth | S | high |
| custom blocks | Accessory keys need per-face UV regions | Converter writes per-face `uv`/`uv_size` from `regions.json` (one source of truth with the texture generator) | S | high |
| PBR / MERS | New accessory maps need companions | Generate MERS (4-value) + normal for the 7 maps in the import build; book/brass get metal/roughness variation | S | med |
| documentation / lessons | Lesson candidate: "A preview that defaults unknown parts to the dominant material hides the parts he cares about; render part-ID sheets before any re-skin claim" | Add to LESSON-CANDIDATES | S | med |
| worldgen / structures | Libraries, classrooms, markets will place these | Generator room kits should pick bookcase `pw:variant` at random for variety | S | low |

No hits: terrain caps · trees / canopy / falling tree · redwood biome · mobs · atmospherics / sky / fog · scripts
(no new behaviour beyond the 10-06 `SEAT_BLOCKS` / `open` plan) · audio.

---

## Files
- `_docs/furniture/FURNITURE-SKINS-CHECK-2026-10-07.md` (this file)
- `_docs/furniture/skins-1007/FURN-SKIN-A.png`, `-B.png`, `-C.png`, `skin_assignments.json`, `skin_table.json`,
  `PLACEHOLDER-TEXTURES.png`, `partid/PARTID-01..26.png` + `partid.json`
- `_docs/furniture/renderer/geo_render.py` (extended; backup in `_garbage/FURNITURE-pre/renderer/`)
- `_staging/furniture231/tools/` (part_census, part_id_sheets, gen_accessory_textures, skin_sheets,
  build_skin_table, furnlib) and `_staging/furniture231/textures_placeholder/` (7 PNG + regions.json), README.md

---

## Appendix A — every candidate, every accessory part
(Bold numbers = in the 12 picks. "whole piece" = the part is the whole model.)
| # | piece | part | cubes (k on PARTID sheet) | texture NOW (10-06 re-skin) | texture NEEDED | note |
|---|---|---|---|---|---|---|
| **1** | classic_nightstand | drawer pulls | 17,18 | post/end | **brass** |  |
| 2 | classic_nightstand_open | drawer pulls | 24,25 | post/end | **brass** |  |
| **3** | classic_nightstand_left | drawer pulls | 12,13 | post/end | **brass** |  |
| **4** | classic_nightstand_middle | drawer pulls | 7,8 | post/end | **brass** |  |
| 5 | foot_stool | upholstered body + top | 0,1 | board | **cloth** | source smallchairbeige = beige upholstery |
| 5 | foot_stool | skirt panels | 2,4,6,8 | board | **cloth** |  |
| 5 | foot_stool | trim strips | 3,5,7,9 | post | **wood** | or brass nails |
| 6 | cofremini | lock plate | 1 | board | **iron** |  |
| 7 | cofremini_open | lock plate | 5 | board | **iron** |  |
| 7 | cofremini_open | lid lining (optional) | lid inner face | whole piece: board/post | **cloth** |  |
| 8 | perchero3 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 9 | espejo2 | mirror glass | 0 | keep | **mirror** | was source PNG (keep) |
| 9 | espejo2 | frame | 1,2,3 | keep/post | **wood** | was source PNG |
| 10 | toalla | towel | 5,7 | board | **cloth** | linen |
| 11 | lampara | lampshade | 2,4,6,7 | board | **cloth** | linen or parchment shade |
| 11 | lampara | candle/flame | none in model | whole piece: board/iron | **candle** | add 1 candle cube if it is to read lit |
| 12 | alfombra_enrollada1 | rug roll | 0,3 | cloth:yellow | **rug** | source alfombra_enrollada1 |
| 12 | alfombra_enrollada1 | roll ends | 1,2,4,5 | board | **rug** | spiral end |
| 13 | small_chair | seat cushion | 9 | board | **cloth** | source smallchairbeige |
| 14 | simple_stool | - | - | wood (board/post/end) | none | all wood: correct as is |
| 15 | taburete | seat top | 5 | iron | **wood** | misread as iron from the source colour |
| 16 | sit_tronco2 | log seat | 0,1 | board | **log** | bark sides + ring top |
| 17 | ajedrez | board top | 0 | board | **game** | chequer |
| 17 | ajedrez | pieces | 1,2,3,4,5,6,7,8,9 | board | **ivory** | two colours |
| 18 | casapajaro2 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 19 | dinner_table | - | - | wood (board/post/end) | none | all wood: correct as is |
| 20 | dinner_table_left | - | - | wood (board/post/end) | none | all wood: correct as is |
| 21 | dinner_table_middle | - | - | wood (board/post/end) | none | all wood: correct as is |
| 22 | mesa | - | - | wood (board/post/end) | none | all wood: correct as is |
| 23 | mesa1 | table-top clutter | 4,5,6,7,8,9,10,11,16,17,18,19 | post/board | **food** | small props (mugs / plates / papers?) - identify at import; not resolved from the ID sheet |
| 24 | mesa4 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 25 | mesa2 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 26 | banco | - | - | wood (board/post/end) | none | all wood: correct as is |
| 27 | banco2 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 28 | chair_dinner | seat pad (optional) | 0 | board | **cloth** | or leather |
| 29 | chair_classic | seat pad (optional) | 0 | board | **cloth** | or leather |
| 30 | silla2 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 31 | sillarus | sling seat | 6 | board | **leather** |  |
| 31 | sillarus | back strap | 7 | board | **leather** |  |
| **32** | fireplace1-1 | firewood | 8,9,10 | stone/keep | **hearth** | log_lit + log_end_lit |
| **32** | fireplace1-1 | embers | 1,2,3 | stone | **hearth** |  |
| **32** | fireplace1-1 | ash bed | 4 | stone | **hearth** |  |
| **32** | fireplace1-1 | back wall inner face | 7 | stone | **hearth** | soot |
| **32** | fireplace1-1 | flame | none in model | whole piece: stone/keep | **flame** | ADD 2 crossed planes |
| **33** | fireplace-top1-1 | flue opening | 3 | stone | **hearth** | soot |
| 34 | chim1 | firewood | 1,2,3 | stone/keep | **hearth** |  |
| 34 | chim1 | hearth floor / back | 0 | stone | **hearth** | ash / soot |
| 34 | chim1 | flame | none in model | whole piece: stone/keep | **flame** | ADD 2 crossed planes |
| 35 | herramienta_fuego | fire irons | cubes 1-16 | whole piece: iron/board/post | **iron** | already iron; rack 17-18 wood |
| 36 | paloantorcha-pro | brazier slats | cubes 1-16 | whole piece: iron/post/end | **iron** | already iron |
| 36 | paloantorcha-pro | flame | none in model | whole piece: iron/post/end | **flame** | ADD planes |
| 37 | barril | staves | 2,3,4,5 | board | **cask** | source hoops were painted, lost in re-skin |
| 37 | barril | heads | 0,1,6 | board/keep/cloth:silver | **wood** | was cloth:silver |
| **38** | barril2 | staves | 2,3,4,5 | board | **cask** | source hoops were painted, lost in re-skin |
| **38** | barril2 | heads | 0,1,6 | board/keep/cloth:silver | **wood** | was cloth:silver |
| 39 | cubo | hoops | 6,7,8,9,10,11,12,13 | post/end | **iron** |  |
| 40 | caja1 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 41 | cesta_patatas | potatoes | bones item_1..15 | whole piece: board/keep | **food** | source cesta_patatas.png |
| 41 | cesta_patatas | basket | bone structure | whole piece: board/keep | **wicker** |  |
| 42 | cesta_manzana | apples | bones item_* (3x3x3) | whole piece: board/post/end | **food** |  |
| 42 | cesta_manzana | stalks / leaves | item_* planes | whole piece: board/post/end | **leaf** |  |
| 42 | cesta_manzana | basket | bone structure | whole piece: board/post/end | **wicker** |  |
| 43 | cesta_zanahoria | carrots | bones item_* (2x2x4) | whole piece: board/post/end | **food** |  |
| 43 | cesta_zanahoria | tops | item_* planes | whole piece: board/post/end | **leaf** |  |
| 43 | cesta_zanahoria | basket | bone structure | whole piece: board/post/end | **wicker** |  |
| 44 | tocon2 | stump | 0,1,2,4,6,7,10 | board | **log** | bark + rings |
| 44 | tocon2 | split billets | 3,5,8,9 | board | **wood** |  |
| 45 | pan | pan | bone dd | whole piece: keep/post/end | **iron** | was source pan.png |
| 45 | pan | handle | bone bone | whole piece: keep/post/end | **wood** |  |
| 46 | teapot | kettle | all | whole piece: keep/iron | **copper** | was source teapot.png |
| 47 | olla1 | pot | 0,2 | keep/post/end | **iron** | was source |
| 47 | olla1 | contents | 1 | keep/board | **food** | stew surface |
| 48 | platos | plates | 4,5 | board | **ceramic** |  |
| 48 | platos | rack | 0,1,2,3 | post/end | **wood** |  |
| 49 | basic_plate | plate | 0 | keep | **ceramic** | was source quartz |
| 50 | cutlery | blades / tines | 0,1,2,3,4 | keep | **iron** | was source quartz |
| 50 | cutlery | handles | 5,6 | keep | **wood** |  |
| 51 | cup_stg_0 | cup | all | whole piece: keep | **ceramic** | or pewter (iron) |
| 52 | decoracioncocina1 | hanging utensils | 1,2,3,4,5,6,7,8,9,10,11,12,13,14 | post/end/board | **iron** |  |
| 52 | decoracioncocina1 | rail | 0 | board | **wood** |  |
| 53 | estant1 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 54 | estant5 | crocks | 0,1,2,3 | board | **ceramic** |  |
| 55 | kitchen_drawer | drawer pulls | 3,4 | post/end | **brass** | or iron |
| 56 | kitchen_cabinet | door knobs | 2,4 | post/end | **brass** | or iron |
| **57** | estante4 | books | 8,9,10,11 | board | **book** |  |
| **57** | estante4 | open-book boards | 12,13 | board | **book** |  |
| **57** | estante4 | open-book pages | 14,15,16,17,18,19 | board | **paper** |  |
| 58 | estante5 | books | 5,6,7,8 | board | **book** |  |
| 59 | estante3 | books (sheet said jars) | 0,1,2,3,4,5,6 | board | **book** | 3x8x6 = the Feudal book size |
| 60 | estante6 | books | 3,4,5,6 | board | **book** |  |
| **61** | libreriarust1 | books | 5,6,7,8,9,10,11,12 | board | **book** |  |
| **62** | libreriarust3 | books | 2,3,4,5,6,10,11,12 | board | **book** |  |
| **63** | libreriarust5 | books | 3,4,7,8,9,10,11 | board | **book** |  |
| **64** | libreriarust6 | books | 3,4,6,7,8 | board | **book** |  |
| 65 | libre1r | books | 3,4,7,8 | board | **book** |  |
| 66 | estant3 | books | 6,7,8,9 | board | **book** |  |
| 67 | libros1 | books | 0,1,2 | board | **book** |  |
| 67 | libros1 | loose sheet | 3 | board | **paper** |  |
| 68 | libros2 | books | 0,1,2 | board | **book** |  |
| 69 | libro_abierto | pages | 0,1,2,3,4,5 | board | **paper** |  |
| 69 | libro_abierto | boards | 6,7 | board | **book** |  |
| 70 | pergamino1 | scroll rolls | 0,3 | post/end | **paper** | scroll_end on the ends |
| 70 | pergamino1 | sheet | 4 | board | **paper** | written |
| 70 | pergamino1 | roller knobs | 1,2,5,6 | board | **wood** |  |
| **71** | libro_cocina1 | boards | 0,4 | keep | **book** | was source PNG |
| **71** | libro_cocina1 | pages | 1,2,3,5,6,7 | keep | **paper** | was source PNG |
| **71** | libro_cocina1 | page clips | 10,11 | board | **brass** |  |
| 72 | escritorio1 | books | 0,1,2,3,4,5,6 | board | **book** |  |
| 73 | template_shelf_table | - | - | wood (board/post/end) | none | all wood: correct as is |
| 74 | shelf_table_left | - | - | wood (board/post/end) | none | all wood: correct as is |
| 75 | organizadordehojas | paper sheets | planes 7x0x10 / 7x1x10 | whole piece: post/board | **paper** | 35 cubes - skip list |
| **76** | globe | globe | 7 | keep | **globe** | cube-shaped in the source |
| **76** | globe | meridian + pin | 3,4,5,6 | keep | **brass** |  |
| **76** | globe | stand | 0,1,2 | keep | **wood** | was source quartz-white |
| 77 | mundo | globe | 5 | keep | **globe** |  |
| 77 | mundo | stand / axis | 0,1,2,3,4,6 | iron | **brass** | now iron |
| **78** | telescopio | tube | 0 | post/end | **brass** | lens region on the ends |
| **78** | telescopio | draw sleeve | 1 | post/end | **brass** |  |
| **79** | pizarra | writing surface | 5 | board | **slate** | was wood (board) |
| **79** | pizarra | back panel | 4 | keep | **wood** | was source PNG |
| **79** | pizarra | frame | 2,3,6,7 | keep | **wood** | was source PNG |
| **79** | pizarra | chalk + duster | 0,1 | keep | **chalk** |  |
| 80 | pizarra_bar1 | board | 1 | board | **slate** |  |
| 80 | pizarra_bar1 | chalk marks | cubes 2-20 | whole piece: post/board/end | **chalk** |  |
| 81 | tablon_corcho1 | board face | 0 | board | **cork** | pinned notes |
| 82 | lienzo1 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 83 | lienzo2 | canvas | 10 | board | **paint** |  |
| 84 | geoda | crystals | planes 9-33 | whole piece: board/post/end | **amethyst** | 34 cubes - skip list |
| 85 | capsula_amatista | case | 4 | board | **glass** |  |
| 85 | capsula_amatista | specimen | 2,3 | board | **amethyst** |  |
| 86 | botes2 | jar | all planes | whole piece: post/board | **glass** | plus cork lid |
| 87 | botes1 | jars | all | whole piece: post/board | **glass** | 44 cubes - skip list |
| 88 | estatua | figure | 0,1,2,3,4,5 | keep | **stone** | was source PNG; or painted |
| 88 | estatua | base | 6 | keep/iron | **wood** | now iron |
| 89 | mesasalonr1 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 90 | damas1 | board | base | whole piece: board/post/end | **game** |  |
| 90 | damas1 | men | cubes 3x1x3 / 2x1x2 | whole piece: board/post/end | **ivory** | 55 cubes - skip list |
| 91 | estatua2 | statue | 1,2,3,4,5,6,7,8,9,10 | board/post/end | **stone** | now wood |
| 91 | estatua2 | plinth | 0 | board | **stone** | now wood |
| 92 | paloantorcha | post top | 0 | post/end | **candle** | flame painted in source; add candle cube or flame |
| 93 | lampara-piedra | stone body | 0,1,2 | board | **stone** | now WOOD: stone mode ignored when the source PNG is missing |
| 93 | lampara-piedra | lamp bowl | 3 | board | **iron** |  |
| 93 | lampara-piedra | flame | 4,5,6,7,8,9 | board/post | **flame** | now wood |
| 94 | trofeo | cup / urn | all | whole piece: keep/board | **gold** | was source trofeo.png |
| 95 | cavern_cup | cup / font | all | whole piece: board/post/end | **stone** | or pewter |
| **96** | carpa1 | canopy + valance | 0,2 | cloth:yellow | **cloth** |  |
| **96** | carpa1 | flaps | 3,4,5 | cloth:white | **cloth** | second tint |
| 97 | tent2 | canopy | 3,4 | board/post | **cloth** | now WOOD |
| 98 | caja | - | - | wood (board/post/end) | none | all wood: correct as is |
| 99 | cesta_cana | produce | bones item_* | whole piece: keep/post/end | **food** | 49 cubes - skip list |
| 100 | cesta_pescado | fish | bones item_* | whole piece: board/post | **food** | 75 cubes - skip list |
| 101 | mesaplegable | - | - | wood (board/post/end) | none | all wood: correct as is |
| 102 | mesa5 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 103 | soporte2 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 104 | soporte | - | - | wood (board/post/end) | none | all wood: correct as is |
| 105 | senal | lettering / arrow relief | small cubes on the arms | whole piece: board | **paint** | optional dark paint |
| 106 | senal2 | lettering relief | small cubes | whole piece: board | **paint** | optional |
| 107 | cartel_2 | chains | 0,1 | (not drawn) | **chain** |  |
| 107 | cartel_2 | emblem relief | 4,5,6,7,8,9,10,11 | board/post/end | **paint** |  |
| 108 | cartel_1 | chains | 0,1 | post/end | **chain** |  |
| 108 | cartel_1 | emblem relief | small cubes | whole piece: post/end/board | **paint** | 32 cubes - skip list |
| 109 | dinero1 | coins | all | whole piece: keep | **gold** | was source dinero1.png |
| 110 | escoba1 | broom head | 0 | board | **straw** |  |
| 110 | escoba1 | binding | 1 | post/end | **iron** | or twine |
| 111 | papelera_madera | - | - | wood (board/post/end) | none | all wood: correct as is |
| 112 | pumpkin_stack | pumpkins | bones item_1..3 | whole piece: board | **food** | vanilla pumpkin colours |
| 113 | mesarustica1 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 114 | taburete1 | legs | 5,6,7,8,9,10,11,12 | iron | **wood** | misread as iron from the source colour |
| 115 | classic_stool | - | - | wood (board/post/end) | none | all wood: correct as is |
| 116 | beer | tankards | all | whole piece: keep | **iron** | pewter; foam top cream - was source beer.png |
| 117 | wine | bottle | all | whole piece: keep/end | **glass** | dark green - was source wine.png |
| 118 | taza | mug | all | whole piece: board/post/end | **ceramic** |  |
| 119 | roast | roast | 1,2,3,4,5,6,7 | keep | **food** | was source roast.png |
| 119 | roast | board | 0 | keep | **wood** |  |
| 120 | roasted_turkey | fowl | all | whole piece: keep | **food** | was source turkey.png |
| 121 | glazed_ham | ham | all | whole piece: keep | **food** | was source glazed_ham.png |
| 122 | baguette | loaf | 0 | keep | **food** | was source baguette.png |
| 123 | egg_basket | basket | 0 | board | **wicker** |  |
| 123 | egg_basket | eggs | 1 | keep | **food** | was source egg_basket.png |
| 124 | plato-manzanas | apples | 0,5,8 | board | **food** |  |
| 124 | plato-manzanas | leaves | 1,2,3,4,6,7 | board | **leaf** |  |
| 124 | plato-manzanas | platter | 9 | board | **wood** |  |
| 125 | pizarra_bar3 | slate | 0 | board | **slate** |  |
| 125 | pizarra_bar3 | chalk marks | cubes 1-19 small planes | whole piece: board/post/end | **chalk** |  |
| 126 | mesapicknic | - | - | wood (board/post/end) | none | all wood: correct as is |
| **127** | trono1 | seat cushion | 7 | board | **cloth** |  |
| **127** | trono1 | back panel | 4 | board | **cloth** |  |
| 128 | sillonm | upholstery | 3,4,5,8 | board | **cloth** | seat / back / arm pads (exact split at import) |
| 129 | sillon | upholstery | 7,8,9,10 | board | **cloth** |  |
| 130 | silla3 | chains | planes 0x1x1 / 0x1x3 | whole piece: board/post | **chain** | 52 cubes - skip list |
| **131** | cortina_cerrada | pleats + heading | 2,3,8,9,10,11,12,13,14,15,16,17,18,19,20,21 | cloth:red | **cloth** |  |
| **131** | cortina_cerrada | pole | 4,5 | cloth:red | **wood** | was cloth:red |
| **131** | cortina_cerrada | brackets | 0,1 | cloth:red | **iron** | was cloth:red |
| **131** | cortina_cerrada | finials | 6,7 | cloth:red | **brass** | was cloth:red |
| **132** | cortina_abierta | pleats + heading | 1,4,5,6,7,8,9,10,11,12,13,14,15,16 | cloth:red | **cloth** |  |
| **132** | cortina_abierta | pole | 0,19 | cloth:red | **wood** | was cloth:red |
| **132** | cortina_abierta | brackets | 2,3 | cloth:red | **iron** | was cloth:red |
| **132** | cortina_abierta | finials | 17,18 | cloth:red | **brass** | was cloth:red |
| 133 | luz3 | chains | 2,3,4,5 | iron | **chain** |  |
| 133 | luz3 | candles | none in model | whole piece: iron | **candle** | ADD 4-8 candle cubes |
| 134 | cuadro1 | painting | 4 | keep | **paint** | was source cuadro1.png |
| 134 | cuadro1 | frame | 0,1,2,3 | keep | **wood** | was source |
| 135 | cuadro3 | panels | 0,1,2 | keep | **paint** | was source cuadro3.png |
| 136 | espejo | mirror | 0 | keep | **mirror** | was source espejo1.png |
| 137 | alfombra | rug | 0 | cloth:red | **rug** | now plain red wool |
| 138 | piano2 | keys | cubes 7-17 | whole piece: iron/keep | **ivory** | now iron |
| 138 | piano2 | case / stand | 0,1,2,3,4,5,6 | iron/keep | **wood** | now iron |
| 139 | yunque | anvil | all | whole piece: iron | **iron** | already iron - correct as is |
| 140 | almadena | head | 0,2,3 | board | **iron** | now wood |
| 141 | martillo | hammer head | 0 | board | **iron** | now wood |
| 142 | tool1 | shaft | 0 | iron | **wood** | now iron (all thin parts were set to iron) |
| 143 | tocon-sierra | saw blade | 3 | keep | **iron** | was source PNG |
| 143 | tocon-sierra | stump | 0 | board | **log** |  |
| 144 | troncos | logs | 0,1,2,3,4 | post/end | **log** | now stripped-log post/end |
| 145 | tablas | - | - | wood (board/post/end) | none | all wood: correct as is |
| 146 | escalera6 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 147 | tendedero | - | - | wood (board/post/end) | none | all wood: correct as is |
| 148 | diana1 | target face | 0 | board | **target** | now wood |
| 149 | arrow_stand1 | arrows | planes 0-17 | whole piece: board | **arrow** | now wood |
| 149 | arrow_stand1 | barrel | 18,19,20 | board | **wood** |  |
| 150 | ff_weapon_stand | sword / trident blades | bones sword + trident | whole piece: board/post/end | **iron** | now wood |
| 151 | heno1 | hay | 5 | board | **straw** | now wood |
| 152 | jaula_chicken | floor | 21,22 | board | **straw** | bars already iron |
| 153 | valla_ganado1 | - | - | wood (board/post/end) | none | all wood: correct as is |
| 154 | puertavalla | hinges | 0,1 | board | **iron** |  |
| 154 | puertavalla | latch | 14,15 | board | **iron** |  |
| 155 | ventana_cerrada | hinges | 8,9,10,11 | board | **iron** |  |
