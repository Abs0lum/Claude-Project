# Furniture import options (2026-10-06)

Research and preview only. I changed nothing under `_build`, `_bds`, `tools` or any pack, and started no server. Follows `_docs/program228/FURNITURE-AND-STAIRS.md` (Program 228, Furniture row).

**How to answer:** reply with the numbers you want, e.g. *"take 3, 7, 12, 57, 127"*. You can add a wood or cloth per number ("127 dark oak + red"). The O-numbers on sheet 00 are pieces we already own. They are shown only for comparison.

## Contact sheets (`/home/claude/_docs/furniture/`)

| Sheet | Room group | Numbers | Re-skin wood shown |
|---|---|---|---|
| `FURN-00-owned.png` | What we already own (`pw:furn_*`) | O1–O12 | dark oak (inset: oak) |
| `FURN-01-bedchamber.png` | Bedchamber | 1–12 | oak |
| `FURN-02-nursery.png` | Nursery and children | 13–18 | oak |
| `FURN-03-hall.png` | Great hall and dining | 19–36 | dark oak |
| `FURN-04-kitchen.png` | Kitchen, pantry, buttery | 37–56 | spruce |
| `FURN-05-study-library.png` | Study and library | 57–75 | dark oak |
| `FURN-06-classroom-lab.png` | Classroom and laboratory | 76–90 | oak |
| `FURN-07-chapel.png` | Chapel | 91–95 | dark oak |
| `FURN-08-shop-market.png` | Shop and market | 96–112 | spruce |
| `FURN-09-tavern.png` | Tavern and feast | 113–126 | spruce |
| `FURN-10-palace.png` | Palace state rooms | 127–138 | dark oak |
| `FURN-11-workshop-yard.png` | Workshop, yard, armoury | 139–155 | spruce |

**155 candidates** in 11 groups, plus the 12 pieces we own. `candidates.json` in the same folder holds the machine-readable list: number, pack, id, cubes, true rendered span, source file and texture.

### How to read a cell
- **Large image.** The piece re-skinned in OUR RP-04 textures, in a 3/4 view from the front-right and above. The textures are `<wood>_planks_v0` for boards, `stripped_<wood>_log` for posts with the grain along the post, `stripped_<wood>_log_top` for end grain, `pw_furn_iron`, `stone_bricks_v13`, and `wool_colored_<colour>` for cloth. The floor grid is 1 block.
- **Small inset.** The source pack's own look. If the inset is grey and labelled *"source: geometry"*, that piece's texture is not in either RP on his Drive (see the audit below), so only the shape is shown.
- **Label.** Source pack, original id, cube count, true rendered size in blocks (W×D×H) and flags. A count in red means more than 24 cubes. `dips below y0` means part of the model hangs below the floor plane. Such a piece must be re-based on import, because of the selection-box y ≥ 0 law and the touch-own-cell law.
- **The re-skin is automatic and approximate.** Materials were assigned per face, from the source texture colour where one exists and otherwise from the shape (wood). On import every bone or cube gets its material by hand (board / post / end / iron / cloth / stone). Book spines, food and cushions get proper textures at that point. Treat the sheets as shape previews.
- The renderer uses the Blockbench sign convention, so it shows what Blockbench and the game show: X mirrored, X and Y rotation negated, Z passed through, rotation order Z·Y·X about each pivot. This matches the codec-extracted Blockbench Sign Law in engine-laws. The facing on the sheets is a preview. Each imported piece's in-game facing is witnessed on first placement (X-mirror and Orientation laws).

---

## TOP 12 (my recommendation)

| Pick | # | Piece | Cubes | Why it earns a slot |
|---|---|---|---|---|
| 1 | **127** | Feudal `trono1` throne | 10 | The palace and castle hall have no seat of state. Cheap, 2 blocks tall, reads well in dark oak with a red wool seat and back. |
| 2 | **32 + 33** | Feudal `fireplace1-1` hearth + `fireplace-top1-1` chimney breast | 15 + 6 | A proper stone hearth for hall, kitchen, inn and manor. Our `mantel` (O11) is only a shelf. Re-skins to `pw_mat_stone_bricks` (or cobble) with its own fire. |
| 3 | **57** | Feudal `estante4` library bookcase | 24 | A 2 × 2-block bookcase face that holds the library wall and the castle academy. Within the 30 px cap as one overhanging block, or split into 4 cells. |
| 4 | **61** | Craftopia `libreriarust1` 1-block bookcase | 15 | A modular book wall that tiles in any room size. Use #62–#64 as variants to break up repetition. |
| 5 | **71** | Craftopia `libro_cocina1` book on stand | 16 | The lectern top we lack, for the chapel, library and classroom. Mount it on our post or an O3-style pedestal. |
| 6 | **76** | Rustic `globe` | 8 | Classroom and study. Its own texture is a stylised map; we would paint a period map (Patrix style) as a 64 px texture. |
| 7 | **78** | Craftopia `telescopio` on tripod | 8 | The academy observatory and the palace study. Brass tube (gold or iron) on wooden legs. |
| 8 | **79** | Craftopia `pizarra` wall blackboard, 2 wide | 8 | The classroom anchor. A slate face in a wooden frame. |
| 9 | **1 + 3 + 4** | Rustic `classic_nightstand` + joinable L / M chest-of-drawers | 19 / 14 / 9 | Bedchambers have nothing between bed and wall. The L/M/R set joins like our tables. Add #2 (open state, 26) only if an `open` state is wanted. |
| 10 | **38** | Feudal `barril2` cask on cradle | 11 | Cellar, buttery, tavern and market. Shows the tapped-cask silhouette our barrel seat (O4) does not. Iron hoops are added as cubes. |
| 11 | **96 + 101** | Feudal `carpa1` awning + Craftopia `mesaplegable` X-trestle table | 6 + 10 | A complete market-stall kit: cloth awning in any wool colour over a folding trestle. |
| 12 | **131 / 132** | Craftopia `cortina_cerrada` / `cortina_abierta` curtains | 22 / 20 | Bed hangings, door drapes and window curtains, and as a stand-in for tapestry (a woven-image texture on the closed curtain). Closed and open states pair as a toggle. |

**Next tier** (strong, smaller need):
- **133** `luz3` iron ring, 8 cubes. Becomes a chandelier with vanilla-candle textures on 4–8 pricket cubes.
- **22** `mesa` trestle table with stretcher, 11. **24** `mesa4` refectory table, 19.
- **31** `sillarus` X-frame faldstool, 9. A period official's chair.
- **35** fire irons, 19.
- **8** cloak tree, 22. **9** cheval mirror, 4.
- **13** child's chair, 10. **6/7** coffer, 2/6.
- **146** library step ladder, 14.
- **88** anatomical figure, 7.
- **86** apothecary jar, 22.
- **105 / 107** signpost and shop sign, 21 / 21.
- **116–124** feast props, 1–10 each.
- **139** anvil, 6.

---

## Recommended pick list by room (all ≤ 24 cubes unless noted)

| Room | Take | Why |
|---|---|---|
| Bedchamber | 1, 3, 4, 6, 7, 8, 9, 131 | Bedside and drawer chests, coffer for linen, cloak tree, mirror, bed hangings (#131 doubles as a canopy-bed curtain). The bed itself is a gap (below). |
| Nursery | 13, 14 | A child's chair and a low stool are the only child-scale pieces in the three packs. Cradle and child bed are gaps. |
| Hall | 22 or 24, 26, 31, 32, 33, 35, 127 | Trestle or refectory table (see the "own" note on joinable tables), long bench, faldstool, hearth and chimney, fire irons, throne. |
| Kitchen | 37, 38, 39, 41, 44, 45, 47, 48, 52, 53 | Casks, bucket, potato basket, chopping block, pan, pot, plates, utensil rack, bracket shelf. |
| Study / library | 57, 61 (+62–64), 65, 66, 67, 70, 71, 73 | Library wall, narrow case, wall shelf, books, scroll, lectern top, writing table with under-shelf. |
| Classroom / lab | 76, 78, 79, 82, 86, 88, 89 | Globe, telescope, blackboard, easel, apothecary jar, figure, pupil bench-desk. |
| Chapel | 71 (lectern), 91, 92 | Statue on plinth, pricket post. The chapel needs authored pieces (gaps). |
| Shop / market | 96, 98, 101, 102, 105, 107, 109, 110 | Awning, crate, stall table, display table, signpost, shop sign, coins, broom. |
| Tavern / feast | 113, 114, 115, 116, 117, 119, 120, 121, 122, 123 | Plank table, turned stool, bar stool, drink and roast props for set tables. |
| Palace | 127, 131, 132, 133, 134, 137 | Throne, curtains, chandelier ring, panel painting (re-painted), rug. |
| Workshop / yard | 139, 143, 144, 146, 147, 148, 151, 155 | Anvil, saw-in-stump, log pile, step ladder, drying frame, archery butt, hay trough, shuttered window. |

**Skip or low value** (shown so you can overrule):
- **Too many cubes:** #42, #43, #99, #100 baskets (37–75 cubes; re-author at about 12 with a contents-texture top), #75 (35), #84 (34), #87 (44), #90 (55), #108 (32), #126 (29), #130 (52).
- **Modern looks:** #55 and #56 (modern kitchen joinery, but they could pass as plain cupboards), #128 and #129 (club armchairs), #138 (keyboard on a stand; not a virginal without re-authoring).
- **Shape reads poorly:** #97 (its canopy is a single angled plane), #154 (gate parts read as loose posts).

---

## What we ALREADY own that covers a need (sheet 00)
- **Long joinable tables are covered.** `pw:furn_table` (O5) already has the 16 auto-join masks `pw:n/e/s/w`. Rustic's `dinner_table` L/M/R (#19–21) is a 3-state subset of the same idea. **Recommendation:** do not import #19–21. Instead, add a *trestle-leg* and a *refectory-leg* variant of our own join masks, taking the leg shapes from #22 (`mesa`) and #24 (`mesa4`). That gives long hall tables that join and also look medieval.
- **Chairs and seating:** O1 chair (ladder-back), O2 bench, O3 stool, O4 barrel seat (still 0 placements). New seating worth adding: throne #127, faldstool #31, child's chair #13, and optionally spindle-back #29 for variety.
- **Storage:** O7 shelf, O8 wall shelf, O9 cupboard, O10 dresser, O12 coat pegs. These cover the kitchen dresser and cupboard. What is missing is drawers (#1/#3/#4), coffers (#6/#7) and bookcases (#57, #61).
- **Trestle and mantel:** O6 is a sawhorse trestle, so #101 is the stall version. O11 is a mantel shelf, which sits above the new hearth #32.
- **Vanilla blocks that stay vanilla because they carry behaviour:** bed (sleep, villager claims), chest, barrel, lectern, bell, ladder (climb). These are engine constraints from Program 228. A pw: replacement must be script-backed, so the imported shapes above are decor pieces next to them, not replacements.

## Gaps: nothing usable in the three packs
These are confirmed by the P11 audit below. My suggestion is to author them ourselves (new `pw:` geometry, same pipeline), or to source them from a Java furniture set (Handcrafted, Another Furniture, Conquest Reforged; Program 228 §d) and convert the Java model JSON.
- **Beds of every size.** Adult single and double, a four-poster with posts for #131 curtains, a **child's bed**, a **cradle**, and a truckle bed. The only "beds" are Craftopia pet beds. Vanilla beds stay where sleeping matters. A pw: bed frame is decor around them or needs script backing.
- **Wardrobe / armoire / press cupboard.** None, so a 1 × 2 tall press is to be authored.
- **Large chest (dower chest / strongbox).** Only the small coffer #6/#7 exists.
- **Candlesticks, candelabra, a true chandelier.** Only #133 (a ring) and lamp posts #11 and #36. RP-04 already carries Patrix candle textures for the flame and wax.
- **Lectern with a slope and stand.** #71 is only the book on a stand.
- **Pew with a back, altar, font, kneeler.**
- **Wash stand with basin and ewer, chamber screen (folding), true tapestry.**
- **Astrolabe, armillary sphere, alchemy bench with alembic, specimen shelves** (only #84–#87, which are heavy and modern-ish).
- **Spinning wheel, loom, writing slope / scriptorium desk.**

---

## Licences as shown (personal use; RESTRICTED-ASSETS lines)
None of the three packs contains a licence file or a licence statement. I searched all files for *licen / copyright / all rights / terms of use* and found none. Their manifests state only authorship:

| Pack (Drive file, md5 of download) | Author as shown | Licence as shown | Status |
|---|---|---|---|
| Feudal Furniture WE 8.7 RP (`1p6ryv2DV-RE7kZAjApYbpIcw1suja5Q_`, `5bb46852…7843`) | "Created by Trotamundos872, More Add-Ons at www.trmc-addons.com" | none stated | RESTRICTED |
| Craftopia Furniture WE 2.5 RP (`1NeQ5GqzPlPn0jeXK0Tkq-wxYReXP3AKu`, `80568766…a8617`) | the same author, Trotamundos872 (it ships Feudal's set inside) | none stated | RESTRICTED |
| Rustic Furnture.mcaddon (`15fWCV4wh-AcHsIRdeB62Dbs7aUBRzdnc`, `d4384d6b…b441`) | "Mrs Trader" (BP + RP) | none stated | RESTRICTED |

**Draft lines** (added to BOTH copies of RESTRICTED-ASSETS.md in the build that first uses a piece, with the chosen piece list filled in):
- `BP-02/RP-04 · models/blocks/pw_furniture2.geo.json + blocks/pw_furn_* · furniture geometry (cubes/pivots only; UVs and textures not copied) · Feudal Furniture WE 8.7 RP (Trotamundos872, trmc-addons.com / mcpedl.com/feudal-furniture) · <ids> · none stated · <date> · owner Trotamundos872 · purchase route: none`
- `… · Craftopia Furniture WE 2.5 RP (Trotamundos872) · <ids> · none stated · <date> · owner Trotamundos872 · purchase route: none`
- `… · Rustic Furniture (Mrs Trader) · <ids> · none stated · <date> · owner Mrs Trader · purchase route: none`
- Any piece keeping a SOURCE texture (food, globe map, paintings, if chosen): add the PNG name to the same line. My default is to re-texture, so no source PNG enters our RPs.

---

## Import method (for the build after you choose; not started)
1. **Read geometry only.** Keep every cube's `origin`, `size`, `pivot` and `rotation`, and every bone's pivot, rotation and parent. Flatten parent bone rotations into cubes where Bedrock blocks need it (block geometry allows one rotation per cube; nested bone rotations are kept as bones, the same as our roof hips). Drop all UVs, `texture_width/height` and source textures.
2. **Re-UV per face to our textures.** Each face gets per-face UV sized to its world size, with 16 px = 1 tile and an offset by world position so planks line up across pieces. The `material_instance` per face is one of `board` / `post` / `end` / `iron` (our existing four keys), plus new `cloth`, `stone`, `glass`, `book` and `food` keys where a piece needs them. Grain direction follows the long axis, as on the sheets.
3. **Ids and format.**
   - Geometry ids are lowercase `geometry.pw_furn_<piece>`, in `pw_furniture.geo.json` or a sibling `pw_furniture2.geo.json`, at **format 1.16.0** (the same as the current file).
   - Blocks are `pw:furn_<piece>_<wood>` (oak / spruce / dark_oak, as now) at block format **1.21.80**, with the mandatory `minecraft:geometry`.
   - Source ids appear only in the provenance ledger and the RESTRICTED-ASSETS list.
4. **Joinable tables** reuse our table auto-join masks (`pw:n/e/s/w`, 16 geometries). The new leg styles (#22 trestle, #24 refectory) become additional mask sets keyed by a `pw:style` state, or a separate family `pw:furn_trestle_table_<wood>`. Rustic's L/M/R pattern is not needed. The drawer chest #3/#4 uses a 3-state E–W join the same way.
5. **Bounds** (engine laws):
   - ≤ 30 px per axis, and the geometry must touch its own unit cube.
   - Pieces flagged `dips below y0` are re-based so the floor is y = 0.
   - Two-wide pieces (#22–27, #32, #57–60, #79, #96, #113, #127 …) either stay one overhanging block within 30 px, or are split into L/R cells with a companion placement rule (preferred where collision matters).
6. **Collision.** One box per block at the current format (single box, y ≥ 0): seats at 12 px, tables full height, wall pieces thin. Stepped arrays wait for the 1.21.130+ format ruling (Program 228 contradiction, still open).
7. **Behaviour.**
   - Throne, faldstool, child's chair and stools join `SEAT_BLOCKS`.
   - Curtains, coffer, drawers and shutters get an `open` state through a custom component (closed/open geometry pairs already exist for #6/7, #131/132 and #1/2).
8. **Gates before ship.** `verify_furniture.py` (bounds, materials resolve, permutations parse), the coplanar audit, the BDS load gate, then a second preview round of the converted `pw:` geometry (rendered with this same renderer) **for your markup before any block JSON ships**. Every piece stays "shipped, awaiting verification" until you witness it on PS5.
9. **Atlas budget.** The re-skin reuses existing RP-04 textures, so it adds 0 px to the terrain atlas. Each new painted texture (globe map, slate, book spines, tapestry) is ≤ 64–128 px and is counted against the ~60 Mpx budget.

---

## Rendering and sourcing notes (honest limits)
- **Source textures missing for most Feudal and Craftopia furniture.** Their geometries use 128² or 64² own-painted atlases (for example `trono1`, `estante4`, `mesa*`, `silla*`), but those PNGs are not in either RP on the Drive. Feudal's RP has 221 files under `textures/`: mainly baskets, awnings, stands, lintels and trapdoors. A texture was accepted only when its file name equals the geometry id (or differs by a number) AND ≥ 85 % of the model's UV rectangles land on opaque texels. A wrong same-prefix match (`mesa` → `mesaofis.png`) was rejected by that rule. The missing atlases probably ship in Feudal's BP or an add-on pack we do not have. This does not affect the import, because we re-texture anyway.
- **Rustic** textures resolve through its own BP `material_instances` → RP `terrain_texture.json`. Most furniture points at the vanilla key `stripped_oak_log_side`, which the inset shows with our RP-04 `stripped_oak_log.png`.
- The cube counts are the source counts. A re-authored piece can usually drop 20–40 % (merged co-planar boards).

### P11 audit: where furniture could be and is not
| Space | Status |
|---|---|
| Feudal 8.7 RP: all 178 geometries (`models/entity/**`) | CENSUSED (indexed + clay-rendered, 8 survey sheets viewed) |
| Rustic mcaddon: RP 132 geometries + BP 790 block files | CENSUSED (modern kitchen, bath and fast food excluded by name after viewing) |
| Craftopia 2.5 RP: 780 geometries (Home / Modern / Pet / feudal) | CENSUSED by id list. About 150 period-plausible ids were rendered and viewed. Home (electronics), traffic lights, pools and the pet set were EXCLUSION-VERIFIED by name. |
| Texture search for missing atlases | CENSUSED: all PNGs in the Feudal + Craftopia RPs, matched by name + UV coverage |
| Umsoea Funky Models v27 (local) | CENSUSED by model name (442 JSON): architecture, candles and lanterns only, no furniture |
| Bed / cradle / wardrobe / chest / candle / lectern / altar / astrolabe keywords across all three packs | CENSUSED by file name: only pet beds (`camaperro*`), `cofremini`, `globe`/`mundo`, `telescopio` |
| Drive `OldPacks` and `Mine` subfolders | NOT listed. They are still open from Program 228. |

### Retro-Sweep (external artifacts studied: Feudal 8.7, Rustic, Craftopia 2.5)
These are backlog suggestions only. Nothing was implemented.

| Subsystem | Hit | Suggestion | Effort | Priority |
|---|---|---|---|---|
| custom blocks | Our table join masks cover joining but have only one leg style | Add trestle and refectory leg variants (#22, #24 shapes) as a `pw:style` state | S | med |
| worldgen / mcstructures | Templates place no drawers, bookcases, hearths, throne or market kit | After his picks, a generator pass places them per room type (palace, inn, market, academy) | M | med |
| build / verification tooling | `_docs/furniture/renderer/geo_render.py` renders any Bedrock geo.json with the Blockbench sign convention, our textures and per-face materials | Reuse it as the planned `furniture_render.py` preview step, and for pre-witness sheets of converted pieces | S | med |
| documentation | The source-texture gap is a property of the WE RPs (atlases absent) | Note it in the provenance ledger so nobody hunts for them again | S | low |

No hits: terrain caps · trees / canopy / falling-tree · redwood biome · mobs · atmospherics · PBR / MERS (except: new pieces reuse existing `_mer` sets) · scripts (except `SEAT_BLOCKS` additions, which belong to the import) · audio.

---

## Full candidate index (numbers match the sheets)

#### 00-owned  (FURN-00-owned.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| O1 | OURS | `pw_furn_chair` | 11 | 1x1x2 |  | pw:furn_chair_<wood> | (geometry only) |
| O2 | OURS | `pw_furn_bench` | 4 | 1x1x1 |  | pw:furn_bench_<wood> | (geometry only) |
| O3 | OURS | `pw_furn_stool` | 7 | 1x1x1 |  | pw:furn_stool_<wood> | (geometry only) |
| O4 | OURS | `pw_furn_barrel_seat` | 12 | 1x1x1 |  | pw:furn_barrel_seat_<wood> | (geometry only) |
| O5 | OURS | `pw_furn_table_0000` | 9 | 1x1x1 |  | pw:furn_table_0000_<wood> | (geometry only) |
| O6 | OURS | `pw_furn_trestle` | 6 | 1x1x1 |  | pw:furn_trestle_<wood> | (geometry only) |
| O7 | OURS | `pw_furn_shelf` | 7 | 1x1x1 |  | pw:furn_shelf_<wood> | (geometry only) |
| O8 | OURS | `pw_furn_wall_shelf` | 3 | 1x1x1 |  | pw:furn_wall_shelf_<wood> | (geometry only) |
| O9 | OURS | `pw_furn_cupboard` | 9 | 1x1x1 |  | pw:furn_cupboard_<wood> | (geometry only) |
| O10 | OURS | `pw_furn_dresser` | 23 | 1x1x2 |  | pw:furn_dresser_<wood> | (geometry only) |
| O11 | OURS | `pw_furn_mantel` | 4 | 1x1x1 |  | pw:furn_mantel_<wood> | (geometry only) |
| O12 | OURS | `pw_furn_coat_pegs` | 4 | 1x1x1 |  | pw:furn_coat_pegs_<wood> | (geometry only) |

#### 01-bedchamber  (FURN-01-bedchamber.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 1 | Rustic | `classic_nightstand` | 19 | 1x1x1 |  | bedside cabinet, 2 drawers | stripped_oak_log.png |
| 2 | Rustic | `classic_nightstand_open` | 26 | 1x2x1 |  | same, drawer open state | stripped_oak_log.png |
| 3 | Rustic | `classic_nightstand_left` | 14 | 1x1x1 |  | joinable chest-of-drawers end (L/M/R set) | stripped_oak_log.png |
| 4 | Rustic | `classic_nightstand_middle` | 9 | 1x1x1 |  | joinable chest-of-drawers middle | stripped_oak_log.png |
| 5 | Rustic | `foot_stool` | 14 | 1x1x1 |  | bed-foot bench / ottoman | smallchairbeige.png |
| 6 | Craftopia | `cofremini` | 2 | 1x1x1 |  | small coffer (closed) | (geometry only) |
| 7 | Craftopia | `cofremini_open` | 6 | 1x1x1 |  | small coffer (lid open) | (geometry only) |
| 8 | Craftopia | `perchero3` | 22 | 1x1x2 |  | standing coat / cloak tree | (geometry only) |
| 9 | Craftopia | `espejo2` | 4 | 1x1x2 |  | cheval (standing) mirror | espejo2.png |
| 10 | Craftopia | `toalla` | 8 | 1x1x1 |  | towel rail (wash-stand companion) | (geometry only) |
| 11 | Craftopia | `lampara` | 8 | 1x1x2 |  | floor lamp -> candle stand shape | (geometry only) |
| 12 | Feudal | `alfombra_enrollada1` | 6 | 2x2x1 |  | rolled rug (storage prop) | alfombra_enrollada1.png |

#### 02-nursery  (FURN-02-nursery.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 13 | Rustic | `small_chair` | 10 | 1x1x1 |  | child's chair (12 px seat height) | smallchairbeige.png |
| 14 | Rustic | `simple_stool` | 5 | 1x1x1 |  | low stool (12 px) | stripped_oak_log.png |
| 15 | Craftopia | `taburete` | 6 | 1x1x1 |  | splay-leg stool (child height) | taburete.png |
| 16 | Feudal | `sit_tronco2` | 2 | 1x1x1 |  | log seat (7 px) | (geometry only) |
| 17 | Craftopia | `ajedrez` | 10 | 1x1x1 |  | board game (chess) on table | (geometry only) |
| 18 | Craftopia | `casapajaro2` | 22 | 1x1x1 |  | birdhouse (window / garden toy) | (geometry only) |

#### 03-hall  (FURN-03-hall.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 19 | Rustic | `dinner_table` | 5 | 1x1x1 |  | long table, single (L/M/R auto-join set) | stripped_oak_log.png |
| 20 | Rustic | `dinner_table_left` | 3 | 1x1x1 |  | long table end piece | stripped_oak_log.png |
| 21 | Rustic | `dinner_table_middle` | 1 | 1x1x1 |  | long table middle piece (top only) | stripped_oak_log.png |
| 22 | Feudal | `mesa` | 11 | 2x1x1 |  | trestle table with stretcher, 2 wide | (geometry only) |
| 23 | Feudal | `mesa1` | 23 | 2x2x2 | dips below y0 | heavy trestle with clutter, 2 wide | (geometry only) |
| 24 | Feudal | `mesa4` | 19 | 2x2x1 |  | refectory table, carved legs | (geometry only) |
| 25 | Feudal | `mesa2` | 11 | 2x1x1 |  | X-leg trestle table | (geometry only) |
| 26 | Feudal | `banco` | 8 | 2x1x1 |  | long bench, 2 wide | (geometry only) |
| 27 | Feudal | `banco2` | 8 | 2x1x1 |  | splayed-leg bench, 2 wide | (geometry only) |
| 28 | Rustic | `chair_dinner` | 10 | 1x1x2 |  | ladder-back dining chair | (geometry only) |
| 29 | Rustic | `chair_classic` | 13 | 1x1x2 |  | spindle-back chair | stripped_oak_log.png |
| 30 | Feudal | `silla2` | 9 | 1x1x2 |  | rustic slat-back chair | (geometry only) |
| 31 | Craftopia | `sillarus` | 9 | 1x1x2 |  | X-frame folding chair (faldstool) | (geometry only) |
| 32 | Feudal | `fireplace1-1` | 15 | 2x2x1 |  | hearth / fireplace, 2 wide | fireplace.png |
| 33 | Feudal | `fireplace-top1-1` | 6 | 1x1x1 |  | chimney breast above hearth | fireplace.png |
| 34 | Craftopia | `chim1` | 9 | 2x2x1 |  | small fireplace | chim1.png |
| 35 | Feudal | `herramienta_fuego` | 19 | 1x1x1 |  | fire irons rack | (geometry only) |
| 36 | Feudal | `paloantorcha-pro` | 17 | 1x1x2 |  | torch / candle post | (geometry only) |

#### 04-kitchen  (FURN-04-kitchen.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 37 | Feudal | `barril` | 7 | 1x1x2 |  | upright cask | barril.png |
| 38 | Feudal | `barril2` | 11 | 2x2x2 |  | cask on cradle | barril.png |
| 39 | Feudal | `cubo` | 14 | 1x1x1 |  | wooden bucket | (geometry only) |
| 40 | Feudal | `caja1` | 17 | 1x1x1 |  | crate, small | (geometry only) |
| 41 | Feudal | `cesta_patatas` | 20 | 1x1x1 |  | basket of potatoes | cesta_patatas.png |
| 42 | Feudal | `cesta_manzana` | 37 | 1x1x1 |  | basket of apples | (geometry only) |
| 43 | Feudal | `cesta_zanahoria` | 38 | 1x2x1 |  | basket of carrots | (geometry only) |
| 44 | Feudal | `tocon2` | 11 | 2x2x1 |  | chopping block (stump) | (geometry only) |
| 45 | Rustic | `pan` | 7 | 2x2x1 |  | frying pan | pan.png |
| 46 | Rustic | `teapot` | 8 | 1x1x1 |  | kettle / pot | teapot.png |
| 47 | Craftopia | `olla1` | 3 | 1x1x1 |  | cooking pot | olla1.png |
| 48 | Craftopia | `platos` | 6 | 1x1x1 |  | stack of plates | (geometry only) |
| 49 | Rustic | `basic_plate` | 1 | 1x1x1 |  | plate | quartz_block_side.png |
| 50 | Rustic | `cutlery` | 7 | 1x1x1 |  | knife and fork | quartz_block_side.png |
| 51 | Rustic | `cup_stg_0` | 6 | 1x1x1 |  | cup / tankard | cup.png |
| 52 | Craftopia | `decoracioncocina1` | 15 | 1x1x1 |  | hanging utensil rack | (geometry only) |
| 53 | Craftopia | `estant1` | 6 | 1x1x1 |  | bracketed wall shelf | (geometry only) |
| 54 | Craftopia | `estant5` | 10 | 1x1x1 |  | wall shelf with crocks | (geometry only) |
| 55 | Rustic | `kitchen_drawer` | 7 | 1x1x1 |  | drawer cupboard (counter) | stripped_oak_log.png |
| 56 | Rustic | `kitchen_cabinet` | 6 | 1x1x1 |  | wall cupboard, 2 doors | stripped_oak_log.png |

#### 05-study-library  (FURN-05-study-library.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 57 | Feudal | `estante4` | 24 | 2x1x2 |  | library bookcase, 30x30 px face (overhangs) | (geometry only) |
| 58 | Feudal | `estante5` | 13 | 2x1x1 |  | low bookcase, 30 px wide | (geometry only) |
| 59 | Feudal | `estante3` | 15 | 2x1x2 |  | low shelf with jars | (geometry only) |
| 60 | Feudal | `estante6` | 9 | 2x1x1 |  | low open shelf | (geometry only) |
| 61 | Craftopia | `libreriarust1` | 15 | 1x1x1 |  | bookcase, 1 block, 2 bays | (geometry only) |
| 62 | Craftopia | `libreriarust3` | 15 | 1x1x1 |  | bookcase, 1 block, cube | (geometry only) |
| 63 | Craftopia | `libreriarust5` | 14 | 1x1x1 |  | bookcase, 1 block, 4 bays | (geometry only) |
| 64 | Craftopia | `libreriarust6` | 11 | 1x1x1 |  | bookcase, 1 block, mixed | (geometry only) |
| 65 | Craftopia | `libre1r` | 11 | 1x1x2 |  | tall narrow bookcase | (geometry only) |
| 66 | Craftopia | `estant3` | 10 | 1x1x1 |  | wall shelf with books | (geometry only) |
| 67 | Feudal | `libros1` | 4 | 1x1x1 |  | pile of books | (geometry only) |
| 68 | Feudal | `libros2` | 3 | 1x1x1 |  | books, stacked | (geometry only) |
| 69 | Feudal | `libro_abierto` | 8 | 1x1x1 |  | open book | (geometry only) |
| 70 | Feudal | `pergamino1` | 7 | 1x1x1 |  | scroll | (geometry only) |
| 71 | Craftopia | `libro_cocina1` | 16 | 1x1x1 |  | open book on stand (lectern top) | libro_cocina1.png |
| 72 | Craftopia | `escritorio1` | 20 | 2x1x2 |  | writing desk with books | (geometry only) |
| 73 | Rustic | `template_shelf_table` | 11 | 1x1x1 |  | writing table with under-shelf | stripped_oak_log.png |
| 74 | Rustic | `shelf_table_left` | 9 | 1x1x1 |  | joinable writing table end | stripped_oak_log.png |
| 75 | Craftopia | `organizadordehojas` | 35 | 1x1x1 |  | letter / paper rack | (geometry only) |

#### 06-classroom-lab  (FURN-06-classroom-lab.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 76 | Rustic | `globe` | 8 | 1x1x1 |  | terrestrial globe on stand | globe.png |
| 77 | Craftopia | `mundo` | 7 | 1x1x1 |  | globe, desk size | mundo.png |
| 78 | Craftopia | `telescopio` | 8 | 1x1x2 |  | telescope on tripod | (geometry only) |
| 79 | Craftopia | `pizarra` | 8 | 2x1x2 |  | wall blackboard, 2 wide | pizarra1.png |
| 80 | Craftopia | `pizarra_bar1` | 24 | 1x1x2 |  | framed board | (geometry only) |
| 81 | Craftopia | `tablon_corcho1` | 5 | 2x1x2 |  | notice board | tablon_corcho1.png |
| 82 | Craftopia | `lienzo1` | 7 | 1x1x2 |  | easel | (geometry only) |
| 83 | Craftopia | `lienzo2` | 12 | 1x1x2 |  | easel with canvas | (geometry only) |
| 84 | Craftopia | `geoda` | 34 | 1x1x1 |  | specimen display (geode) | (geometry only) |
| 85 | Craftopia | `capsula_amatista` | 5 | 1x1x1 |  | specimen pedestal | (geometry only) |
| 86 | Craftopia | `botes2` | 22 | 1x1x1 |  | apothecary jar | (geometry only) |
| 87 | Craftopia | `botes1` | 44 | 1x1x1 |  | jars on stand (alchemy shelf) | (geometry only) |
| 88 | Craftopia | `estatua` | 7 | 1x1x2 |  | anatomical figure / statue | estatua.png |
| 89 | Craftopia | `mesasalonr1` | 9 | 2x1x1 |  | pupil bench-desk | (geometry only) |
| 90 | Craftopia | `damas1` | 55 | 2x2x1 |  | draughts board | damas.png |

#### 07-chapel  (FURN-07-chapel.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 91 | Craftopia | `estatua2` | 11 | 1x1x1 |  | statue on plinth | (geometry only) |
| 92 | Feudal | `paloantorcha` | 1 | 1x1x1 |  | plain pricket post (candle) | paloantorcha.png |
| 93 | Feudal | `lampara-piedra` | 10 | 1x1x1 |  | stone lamp bracket | (geometry only) |
| 94 | Craftopia | `trofeo` | 19 | 1x1x1 |  | chalice / urn shape | trofeo.png |
| 95 | Feudal | `cavern_cup` | 10 | 1x1x1 |  | cup / font shape | (geometry only) |

#### 08-shop-market  (FURN-08-shop-market.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 96 | Feudal | `carpa1` | 6 | 1x2x2 | dips below y0 | market awning | carpa1.png |
| 97 | Feudal | `tent2` | 5 | 2x2x2 |  | tall tent / stall canopy | (geometry only) |
| 98 | Feudal | `caja` | 18 | 1x1x1 |  | crate, large | (geometry only) |
| 99 | Feudal | `cesta_cana` | 49 | 1x1x1 |  | crate of cane / produce | caja_cana1.png |
| 100 | Feudal | `cesta_pescado` | 75 | 1x1x2 |  | fish crate | (geometry only) |
| 101 | Craftopia | `mesaplegable` | 10 | 1x1x1 |  | X-trestle stall table | (geometry only) |
| 102 | Feudal | `mesa5` | 6 | 1x1x1 |  | pedestal display table | (geometry only) |
| 103 | Feudal | `soporte2` | 18 | 1x1x1 |  | heavy stall counter | (geometry only) |
| 104 | Feudal | `soporte` | 7 | 1x1x1 |  | bracket shelf | (geometry only) |
| 105 | Feudal | `senal` | 21 | 2x1x1 |  | directional signpost | (geometry only) |
| 106 | Feudal | `senal2` | 11 | 1x1x1 |  | signpost, single arm | (geometry only) |
| 107 | Feudal | `cartel_2` | 21 | 1x1x1 |  | hanging shop sign on post | (geometry only) |
| 108 | Feudal | `cartel_1` | 32 | 2x1x1 |  | hanging shop sign, emblem | (geometry only) |
| 109 | Feudal | `dinero1` | 8 | 1x1x1 |  | coin piles | dinero1.png |
| 110 | Craftopia | `escoba1` | 3 | 1x1x2 |  | broom | escoba1.png |
| 111 | Craftopia | `papelera_madera` | 5 | 1x1x1 |  | wooden bin / tub | papelera_madera.png |
| 112 | Craftopia | `pumpkin_stack` | 7 | 1x1x1 |  | stacked pumpkins | (geometry only) |

#### 09-tavern  (FURN-09-tavern.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 113 | Feudal | `mesarustica1` | 7 | 2x1x1 |  | rustic plank table, 2 wide | (geometry only) |
| 114 | Feudal | `taburete1` | 13 | 1x1x1 |  | turned stool | taburete.png |
| 115 | Rustic | `classic_stool` | 10 | 1x1x2 |  | tall bar stool | stripped_oak_log.png |
| 116 | Rustic | `beer` | 8 | 1x1x1 |  | beer tankards | beer.png |
| 117 | Rustic | `wine` | 4 | 1x1x1 |  | wine bottle | wine.png |
| 118 | Craftopia | `taza` | 10 | 1x1x1 |  | mug | (geometry only) |
| 119 | Rustic | `roast` | 8 | 1x1x1 |  | roast on board | roast.png |
| 120 | Rustic | `roasted_turkey` | 7 | 1x1x1 | dips below y0 | roast fowl | turkey.png |
| 121 | Rustic | `glazed_ham` | 4 | 1x1x1 |  | ham | glazed_ham.png |
| 122 | Rustic | `baguette` | 1 | 1x1x1 |  | loaf | baguette.png |
| 123 | Rustic | `egg_basket` | 2 | 1x1x1 |  | egg basket | egg_basket.png |
| 124 | Craftopia | `plato-manzanas` | 10 | 1x1x1 |  | fruit platter | (geometry only) |
| 125 | Craftopia | `pizarra_bar3` | 23 | 1x1x1 |  | tavern slate on wall | (geometry only) |
| 126 | Feudal | `mesapicknic` | 29 | 2x2x1 | dips below y0 | table with fixed benches, ~2x2 | (geometry only) |

#### 10-palace  (FURN-10-palace.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 127 | Feudal | `trono1` | 10 | 2x1x2 |  | throne | (geometry only) |
| 128 | Craftopia | `sillonm` | 9 | 2x1x2 |  | upholstered armchair | (geometry only) |
| 129 | Craftopia | `sillon` | 11 | 2x2x2 |  | armchair, low | (geometry only) |
| 130 | Feudal | `silla3` | 52 | 2x1x1 |  | hanging swing seat on chains | (geometry only) |
| 131 | Craftopia | `cortina_cerrada` | 22 | 2x1x2 | dips below y0 | curtains, closed (tapestry / bed hangings) | (geometry only) |
| 132 | Craftopia | `cortina_abierta` | 20 | 2x1x2 | dips below y0 | curtains, tied open | (geometry only) |
| 133 | Craftopia | `luz3` | 8 | 2x2x1 |  | hanging ring frame -> chandelier | luz3.png |
| 134 | Craftopia | `cuadro1` | 5 | 1x1x2 |  | tall painting / panel | cuadro1.png |
| 135 | Craftopia | `cuadro3` | 3 | 2x1x2 |  | triptych of panels | cuadro3.png |
| 136 | Craftopia | `espejo` | 1 | 1x1x2 |  | wall mirror | espejo1.png |
| 137 | Craftopia | `alfombra` | 1 | 2x2x1 |  | flat rug (1 cube) | alfombra.png |
| 138 | Craftopia | `piano2` | 18 | 2x1x1 |  | keyboard on X-stand (virginal) | piano1.png |

#### 11-workshop-yard  (FURN-11-workshop-yard.png)

| # | Pack | Source id | Cubes | Blocks WxDxH | Flags | What it is | Source texture |
|---|---|---|---|---|---|---|---|
| 139 | Feudal | `yunque` | 6 | 1x1x1 |  | anvil | (geometry only) |
| 140 | Feudal | `almadena` | 4 | 1x1x2 |  | sledgehammer | (geometry only) |
| 141 | Feudal | `martillo` | 6 | 1x1x1 |  | hammer and blocks | (geometry only) |
| 142 | Feudal | `tool1` | 5 | 1x1x2 |  | pitchfork | (geometry only) |
| 143 | Feudal | `tocon-sierra` | 4 | 2x1x2 |  | saw in stump | tocon-sierra.png |
| 144 | Feudal | `troncos` | 5 | 1x1x1 |  | log pile | (geometry only) |
| 145 | Feudal | `tablas` | 3 | 2x2x1 |  | plank offcuts | (geometry only) |
| 146 | Feudal | `escalera6` | 14 | 1x1x1 |  | step ladder | (geometry only) |
| 147 | Feudal | `tendedero` | 5 | 2x1x2 |  | drying / clothes frame | (geometry only) |
| 148 | Feudal | `diana1` | 6 | 2x1x2 |  | archery target | (geometry only) |
| 149 | Feudal | `arrow_stand1` | 21 | 1x1x2 |  | arrow barrel | (geometry only) |
| 150 | Feudal | `ff_weapon_stand` | 24 | 2x1x1 |  | weapon rack | (geometry only) |
| 151 | Craftopia | `heno1` | 9 | 2x1x1 |  | hay trough | (geometry only) |
| 152 | Craftopia | `jaula_chicken` | 23 | 2x1x2 |  | poultry cage | (geometry only) |
| 153 | Craftopia | `valla_ganado1` | 5 | 1x1x1 |  | hitching post | (geometry only) |
| 154 | Feudal | `puertavalla` | 16 | 1x1x2 |  | field gate, 2 wide | (geometry only) |
| 155 | Feudal | `ventana_cerrada` | 17 | 1x1x1 |  | window with shutters | (geometry only) |
