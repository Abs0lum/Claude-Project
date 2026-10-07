# Furniture and stairs: what we have, what his packs carry, the spiral staircase, what to download (Program 228)

Research only, 2026-10-06. I changed no pack, build, process or Drive file. I listed Drive titles. Three small Bedrock furniture packs (3.8 to 7.4 MB) were pulled to the scratchpad so their block lists could be read, then deleted. For the 1.38 GB Medievalism v7 zip I fetched only the zip central directory (about 112 KB, by HTTP range) plus its 270-byte `Copyright.txt`.

His question (Program 228 decisions, Furniture row): *"is there a pack, or packs, I can download to provide you with advanced furniture and/or things like an ACTUAL spiral staircase (or do we already have that?) … Are there item and object blocks we haven't been using that might help now within the packs we already have? If they have the correct concept, but perhaps need a Patrix texture replaced over the geometry, and the original texture removed, we can do that."*

**Short answers**
- **Spiral staircase: no, we do not have one.** `palacegen.spiral()` and `castlegen.spiral()` build a 3 x 3 ring of FULL blocks (spruce planks in the palace, curtain-wall stone in castles) that rises one block per ring cell around a log post. It is a "newel stair" made of cubes, with no stair geometry.
- **His packs do contain one real spiral staircase:** **Umsoea Funky Models v27** (local `_intake/newpacks-1001/`, also on his Drive), models `u_spiral_stairs_l` and `u_spiral_stairs_r`. Each is 83 elements with y-rotations of ±22.5° and ±45°: a quarter turn per block, 4 wedge treads rising 4 px each, a helical handrail, and a newel post at the block corner. Four blocks around a shared post make one full turn per 4 blocks of height. It converts mechanically to Bedrock block geometry. No other pack in his set, local or on Drive, has a helical stair.
- **Ready Bedrock furniture is already on his Drive and unused:** *Feudal Furniture WE 8.7 RP* (178 geometries, medieval and rustic), *Rustic Furnture.mcaddon* (790 blocks, BP + RP, format 1.26.0), and *Craftopia Furniture WE 2.5 RP* (mostly modern; it contains Feudal's set).
- **Our own unused piece:** `pw:furn_barrel_seat_{oak,spruce,dark_oak}` has 0 placements in any template. `wall_shelf` appears only in `cottage_s`.

---

## (a) What WE have, used vs unused

Source: BP-02 v227 `blocks/` (459 files) and RP-04 v158 `models/blocks/` (43 geo files). Usage is a census of every `.mcstructure` under `bp02-227/structures/pw`, read-only through `tools/mcstructure.py`. The numbers below are the 41 composite `mvv_*` templates only; the stage files `s0..s4` repeat the same blocks.

### Furniture family `pw:furn_<piece>_<wood>` (12 pieces × oak / spruce / dark_oak = 36 blocks; geometry `RP-04 models/blocks/pw_furniture.geo.json`, 27 geometries incl. 16 table auto-join masks)

| Piece | Cubes | Script role | Template cells (oak / spruce / dark oak) | Families |
|---|---|---|---|---|
| chair | 11 | seat (`pw:seat`) | 10 / 23 / **108** | cottages, inn, manor, palace ×4 |
| table (16 join variants) | 1–9 | auto-join (`pw:n/e/s/w`) | 7 / 17 / **63** | cottages, inn, manor, palace |
| bench | 4 | seat | 1 / 40 / 9 | cottage_l, inn, manor, palace, town hall |
| shelf | 7 | — | 12 / 39 / 17 | bakery, butcher, inn, smithy, town hall |
| cupboard | 9 | — | 2 / 10 / 5 | cottages, manor, town hall |
| trestle | 6 | — | 2 / 9 / 3 | bakery, butcher, manor, lumberyard |
| mantel | 4 | — | 3 / 9 / 4 | cottages, inn |
| stool | 7 | seat | 4 / 8 / 3 | bakery, cottages, farms, quarry |
| coat pegs | 4 | — | 1 / 6 / 2 | cottages, farm_wheat |
| dresser | 23 | — | 1 / 5 / 2 | cottage_l, cottage_m |
| wall shelf | 3 | — | 1 / 2 / 1 | **cottage_s only** |
| **barrel seat** | 12 | seat | **0 / 0 / 0** | **UNUSED** (registered in `SEAT_BLOCKS`, never placed) |

### Stairs and vertical circulation we own
- `pw:ramp_{cobble,smooth_stone,stonebrick}_{2_hi,2_lo,4_q1..q4}` (18 blocks): road ramps. Only `cobble_4_q*` is placed (road `ramp7`). The Program-228 ruling adds the 8-block ramp and all stones.
- `pw:seated_<stair>` (≈60): a vanilla stair resting on a bottom slab, a snow-seat family. It is not a new stair shape.
- `pw:snowcap_stairs`: a snow overlay.
- Roof family (`roof45*`, `roof63*`, `roof_hip`, `roof_gusset*`, `roof_pyramidion`, `roof_ridge_end`, `pw:rafter45_*`): roofs. These are not stairs, though the vaulted-ceiling idea reuses them.
- **None of the following exists:** a stair block, a spiral or newel-stair piece, a railing or balustrade, a ladder.
- **Vertical circulation in the templates is still vanilla:** `minecraft:ladder` ×438 cells (bakery, butcher, cottages, cattle farm, inn, manor, palace_sw, quarry, town hall), `spruce_stairs` ×27 (palace se/sw), `stone_brick_stairs` ×15 (palace nw). The palace spiral wells are full `spruce_planks`.

### Vanilla object blocks the templates lean on (candidates for our own versions)
glass_pane 2340 · red_carpet 493 (palace) · ladder 438 · spruce_door 359 · bed 315 cells · spruce/oak fence 411 · chest 174 · barrel 135 · bookshelf 85 · lantern 76 · iron_bars 59 · lectern 26 · bell 15 · cauldron 15 · furnace/smoker/blast 30 · anvil 6 · grindstone 5 · wall_sign 4 · composter 3 · spruce_trapdoor 1.

**Constraints on replacing these** (engine behaviour, not taste):
- **Ladder.** `pw_civ_walk.js` climbs any id containing `"ladder"` with scripted rungs. A custom block has no climbable component, so a `pw:` ladder would be decor for the player. Keep vanilla ladders where people climb. A pw: ladder fits only for scripted climbing or decoration.
- **Bed, chest, barrel, lectern, bell.** Sleeping, villager bed and job-site claims, and containers are vanilla behaviours. Replace them only with a script-backed piece. The catalogue backlog has "storage pieces as containers" and "pw bed frame".
- **Stairs or ramps in the walk graph.** `pw_civ_walk.js` treats ids containing `_slab`, `stairs` or `ramp_` as half floors, with |dH| ≤ 1 between neighbours. **Any new stair block must keep `stairs` in its id** (e.g. `pw:spiral_stairs_oak`) or the civ walk graph will not path over it.

### Vanilla decor blocks the templates never use (no cost, Patrix-textured where RP-04 carries them)
Candles (all colours, RP-04 has Patrix candles) · chain / copper chain / copper lantern (RP-04 has them; `iron_chain` appears only in the butcher) · chiseled bookshelf (Patrix textures present) · campfire (Patrix 3D model in the Java pack; RP-04 has `campfire.png`) · trapdoors used as shutters (one spruce trapdoor in all templates) · hanging signs · decorated pots · flower pots · carpets other than red (rugs in cottages and the inn) · banners · item frames and armor stands (entities) · loom / fletching / cartography / smithing tables (single uses). These are free set-dressing for the inn, market and palace. The template generators simply never place them.

---

## (b) Candidates from packs he has ALREADY given us, ranked

Censused spaces (P11 audit):

| Space | Status |
|---|---|
| `_intake/civmods/{curseforge,modrinth,manual}` (63 archives, all scanned in memory) | CENSUSED |
| `_intake/newpacks-1001`, `newpacks-1002` | CENSUSED (Umsoea scanned; Stratum, GFT and RenderingStuff are texture packs, excluded by type) |
| `_intake/addons-0930` | CENSUSED by title (mob add-ons) |
| `_intake/patrix*` (models zip + 26.2 basic) | CENSUSED |
| `_packs`, `_intake/stack-*` | Our own packs, CENSUSED by name |
| `_ref`, `_work`, `src`, `_archive` | CENSUSED by listing (no third-party packs) |
| Drive packs folder `1ZHhqcLbhW…` (3 pages listed) | CENSUSED by title |
| Drive `OldPacks` and `Mine` subfolders | **NOT listed**; a follow-up if he wants |
| `Prominence II Hasturian Era` (397 MB) | NOT opened (size); an RPG port, unlikely to contain furniture |
| Medievalism v7 x2048 | Central directory read by range (819 entries) |
| `Abs0lutMedievalism.mcaddon` (302 MB) | Central directory read: it is only a bundle of our own RP-01/03/04/05/10, BP-02 173 and StreetKit; nothing new |

**Platform key:** **B** = Bedrock geometry, directly usable as a `pw:` block. **J** = Java block model JSON (axis-aligned plus single-axis rotations), a mechanical conversion. **OBJ** = a true mesh; block geometry is cubes only, so it must be re-authored.

| Rank | Pack (where) | Plat. | What is in it for us | Geometry quality | Patrix re-skin | Licence as shown | Template families |
|---|---|---|---|---|---|---|---|
| **1** | **Umsoea Funky Models v27 256x** (local `_intake/newpacks-1001/`, Drive) | J | **Real spiral stair** `u_spiral_stairs_l/_r` (83 el.); `u_arches_spiral_stairs`/`2` (spiral stair under an arch, 84 el., 2 blocks wide); `u_column_base/shaft/top`; arches (`u_arches*`, `u_archalt*`); brackets and corbels (`u_bracket_*` ×36); windows (`u_win_*` ×60: arch, round, corner, half); rect doors 2/2.5/3 tall; `u_wall_*` | High: 22.5° rotations give round treads and rails; a single 512² atlas | Medium: atlas UVs must be re-mapped to tiling `pw_mat_*` faces (per face, size-proportional UV) | **None in the pack**; umsoea.com: "© 2019-2026 UMSOEA. ALL RIGHTS RESERVED." → RESTRICTED | castle towers, palace private stairs, chapel, manor |
| **2** | **Feudal Furniture WE 8.7 RP** (Drive `1p6ryv2D…`, Trotamundos872) | B | Tables `mesa`, `mesa1-5`, `mesarustica1`, picnic `nesapicknik`; seats `banco`, `banco2`, `silla2`, `silla3`, `taburete`, `taburete2`, `sit_tronco`; **throne** `trono1`; shelves `estante1-6` (`estante4` is a 53 px tall bookcase), `estante_luz1`; `barril`, `barril2`; crates `caja`, `caja1`; **produce baskets** `cesta_{manzana,patatas,pescado,zanahoria,cana}`; **fireplace** `fireplace1-1` + chimney top; stone lamp `lampara-piedra`; torch posts `paloantorcha`, `-pro`; **market awnings and tents** `carpa1`, `tent2`; clothesline `tendedero`, `2`; rolled rugs `alfombra_enrollada1/2`; **shuttered windows** `ventana_abierta/cerrada`; trapdoors; **gutters and downspouts** `canalon1-9`; lintels `dintel1/2`; anvil `yunque`; **waterwheel** `noria1-1..7` (7 frames); rope, chain; signposts `senal1-3`; `Puertavalla` gate; `modular_fence`; plank piles `tablas`; books `libros`; scroll `pergamino`; archery `diana`, arrow, axe and weapon stands | Good: 6–75 cubes, many rotated; 128² or 64² own-painted atlases | Medium: same atlas-to-tile remap; bones are single-material, so `material_instances` per bone works | **None stated** in pack or on MCPEDL page → RESTRICTED | inn, market, cottages, smithy, farm, palace (throne), mill (noria) |
| **3** | **Rustic Furnture.mcaddon** (Drive `15fWCV4w…`, "Mrs Trader") | B (BP + RP, `format_version 1.26.0`, `min_engine 1.21.80`) | 790 blocks in 13 woods. Medieval fit: `classic_chair`, `dinner_table` (L/M/R auto-join), `shelf_table` (L/M/R), `classic_nightstand` (+open), `stool`, `simple_stool`, `foot_stool`, `simple_ladder` (decor), `egg_basket`; **food props** `roast`, `roasted_turkey`, `glazed_ham`, `baguette`, `wine`, `beer`, `teapot`, `cup`, `pan`, `basic_plate`, `cutlery`, `fish_chips` (feast and inn tables). Modern pieces to skip: fridge, toilet, microwave, sofa, air conditioner | Simple and clean (2–14 cubes) | **Easiest re-skin**: `material_instances` point at vanilla keys (`stripped_acacia_log_side`, planks) with 16-px UVs, so swapping the key to `pw_mat_*` is a one-line change per block | **None stated** → RESTRICTED | inn and feasts, cottages, kitchens (bakery, butcher), market |
| 4 | **Domum Ornamentum** 1.20.1 (local civmods) | J | Texture-agnostic architectural shapes: **turned, heavy, pinched, quad and double posts** (balusters, newels); **pillars with base, column and octagonal capital**; **panels and trapdoors** (coffer, boss, moulding, roundel, waffle); doors (full, port-manteau); timber frames; paper walls; barrel deco; floating carpets | Simple (2–11 elements) but well proportioned | **Ideal**: models carry no texture ("materially_textured" loader), so Patrix materials apply directly | `mods.toml`: **LGPLv3** | palace coffered ceilings and colonnades, great hall, stair balusters |
| 5 | **Medievalism v7 x2048** (Drive, 1.38 GB; central directory only) | OBJ (120 meshes) + J | **No furniture, no spiral.** Has `wooden_stairs` + `wooden_stairs_fence01/02_{l,r}[_extended]` (a balustraded straight flight), `wooden_wall_01_window_1_{open,closed}` (shutters), beams with supports, corbels, knee braces, `stone_corbel01`, merlons, arrow slits, arches | High (designed overhang), but true meshes: no poly_mesh for blocks, so re-author as cubes (as the roof family already did) | n/a (re-authored) | `Copyright.txt`: "You may not redistribute this pack anywhere." → RESTRICTED (personal use OK under §9) | castle (merlons, slits), staircase railings, timber halls |
| 6 | **Jerry's Colonies 2.15.7** (civmods, Bedrock) | B | `market_stall`, `stall`, `tavern_sign`, `food_crate`, `mayor_table`, `taxation_table`, `bounty_board`, `ballot_box`, `blueprint_workbench`, 9 job workstations (cook, craft, farm, hunter, knight, logger, miner, builder, research) | Not viewed visually; geometry files present | per-atlas remap | Not read (CurseForge project) → RESTRICTED until read | market, town hall, workshops (CIVITAS stations) |
| 7 | **Empire Expansion 2.0.10** (civmods, Bedrock) | B | `army_table`, `infirmary_table`, `workshop_table`, `altar`, coin stacks, crates | Not viewed | remap | Not read → RESTRICTED | palace (war room), chapel (altar) |
| 8 | **Millénaire 9.0.2** (civmods) | J | `tapestry`, `mock_decor_wall_carpet_{small,medium,large}`, `hide_hanging`, banners, `fire_pit`, beds `charpoy` / `futon` (non-European) | Basic | yes | `mods.toml`: **All Rights Reserved** → RESTRICTED | palace wall hangings |
| 9 | **Townstead 0.7.6** (civmods) | J | Kitchen workstations, `butcher_shop_counters`, `field_post` (11 woods) | Small set | yes | GPL-3.0 (README) | butcher, kitchens, farms |
| 10 | **Patrix 26.2 basic** (our art source) | J | 3D models of vanilla blocks: lectern (rotated top), bell, lantern / hanging lantern, campfire, cauldron, grindstone, scaffolding, ladder (5 el.), bed head/foot, doors, trapdoors, fence gates | Modest (mostly texture-led) | native | FreshLX permission | A Bedrock RP **cannot** change vanilla block geometry, so these help only as `pw:` replacements; low priority |
| — | Craftopia Furniture WE 2.5 RP (Drive) | B | Superset of Feudal plus modern items (sofas, consoles, monitors). Extras worth having: `barandilla0-2` (railings, straight and stepped), `andamio` (scaffold), `chim1` + `chim-top1`, `mueble rustico`, `perchero1-3`, `espejo` | — | — | none stated | only for railings and chimneys |
| — | Kingdom Constructor, Villages Plus, Village Generator, guard and companion add-ons, mob add-ons | — | No furniture (guard posts, spawners, vanilla-block structures) | — | — | — | — |

---

## (c) The spiral staircase

### Do we have one? No.
`tools/palacegen.py:143` and `tools/castlegen.py:171` place full blocks around a ring of 8 cells: `[(0,0),(1,0),(2,0),(2,1),(2,2),(1,2),(0,2),(0,1)]` around a `spruce_log` post. They rise 1 block per cell, which is 8 blocks per turn, and clear 3 cells of headroom (the cause of finding F2, the roof holes). The result reads as a stepped stone or plank helix, not a staircase.

### Does any pack have a real one? Yes, exactly one: Umsoea `u_spiral_stairs_l/_r`
What the model is (read element by element):
- **Footprint.** One block per quarter turn. The newel post stands at the block corner (16, 16), so **2 × 2 blocks around one shared post make a full turn**, and each block sits 1 block higher than the previous one. That gives one full turn per 4 blocks of height and about 3 blocks of headroom under the turn above.
- **Treads.** 4 per block at y ≈ 0.6 / 4.6 / 8.6 / 12.6 px (4 px rise each), each a 22.5° wedge. Each tread is made of stacked thin planes (y + 0.0 / 0.1 / 0.35 / 0.4) with risers 4 px tall.
- **Newel post.** 16 vertical planes in a ring (rotations 0, ±22.5, ±45) about origin (12.6, 7.21, 12.79), plus a cap ring.
- **Handrail and stringer.** Rotated planes rising 4 px per tread segment.
- **L and R variants** set the hand (clockwise or counter-clockwise).
- **In Java** it is visual only: it is hung on `piglin_head` rotation states 0–15 (12 L, 4 R) and has no stepping collision. Umsoea also ships `u_arches_spiral_stairs`, a 2-block-wide flight under an arch, with 4-element fans at 5° increments.
- **Bounds:** x −0.3…18.8, y −3.1…16.2, z 0…21.6 px (a little overhang). This is inside Bedrock's limits: 30 × 30 × 30 px, at least 1 px inside the unit cube, ±30 px from the origin.
- **Conversion to Bedrock** is mechanical. Each element becomes a cube with `origin = from − (8, 0, 8)`, `size = to − from`, `pivot = rotation.origin − (8, 0, 8)` and `rotation [0, −angle, 0]` (Java's y-angle sign flips; check against our D-C197 rotation rule). Zero-thickness planes are valid cube sizes. Our shipped geometry already uses non-90° angles (14.04, 26.57, 63.44, 22, 15, 135), so arbitrary single-axis rotation is proven on PS5.

### Our own design: `pw:spiral_stairs_<mat>`

Two layouts. I recommend **A** because it drops into the existing generators.

**A. 3 × 3 newel ring, a drop-in for `spiral()`** (same footprint, same 8 cells per turn, same walk graph |dH| = 1)
- **Pieces.** One block family, `pw:spiral_stairs_<mat>`, with states:
  - `pw:seg` ∈ {edge, corner}
  - `minecraft:cardinal_direction` (4)
  - `pw:hand` ∈ {cw, ccw}
  - optional `pw:rail` (0/1)

  That is 2 shapes × 4 rotations × 2 hands = 16 permutations, with mirroring done in geometry. Each ring cell spans 45° of arc about the centre post, so an edge cell and a corner cell differ only in radius and offset.
- **Post.** A new `pw:newel_<mat>` (an octagonal post of ±22.5° and 45° cubes, after Umsoea and DO `pillar_column`) replaces the `spruce_log` column. Its cap meets the floor above.
- **Treads.** 4 per cell at 4 / 8 / 12 / 16 px, each an 11.25° wedge built as 2–3 rotated cubes. The tread nose carries a 1 px moulding. Risers are 4 px. Material instances are `tread`, `riser`, `post` and `rail`, mapped to `pw_mat_*` (oak, spruce, dark oak, stone bricks, cobble and smooth stone for castles).
- **Collision.**
  - `minecraft:collision_box` as an **array**. Sample the cell on a 4 × 4 px grid, take each sample's polar angle about the post, set its height to the tread above it, and merge the samples into rectangles. That gives at most 16 boxes, inside the wiki-documented array limit of 16.
  - Each step is 4 px, so players and villagers auto-step.
  - The selection box stays a single full cell.
- **Engine requirement.** Arrays need `format_version` ≥ **1.21.130**. They are experiment-free from 1.26.0, and from **1.26.60 only the array form** is accepted. Box range is (−8, 0, −8)…(8, 24, 8).
  - PS5 runs 26.52, so the stair block file would be authored at `1.26.50`.
  - ⚠ **CONTRADICTION TO SURFACE:** FOUNDATION locks custom blocks at `format_version 1.21.80`. Raising one block family's format is a locked-invariant change and needs Abs0lum's ruling before any build. The fallback is a single box per cell at the tread mid-height (8 px), which walks as a half-step ladder of slabs.
- **Walk graph.** The id contains `stairs`, so `pw_civ_walk.js` already treats it as a half floor. Ring cells rise 1 block each, so the existing |dH| ≤ 1 graph is unchanged. (ASSUMPTION: villager navigation steps onto multi-box custom collision the way it does onto vanilla stairs. **Witness item:** a villager led up 2 turns on BDS plus on PS5.)
- **Generator change.** `spiral(..., mat="pw:spiral_stairs_<mat>")` puts `seg`, `facing` and `hand` per ring index (even index = corner, odd = edge, facing = tangent). The 3-cell headroom clear is kept but stops at the eave, which fixes F2 in the same edit.
- **Optional handrail** on the outer edge. The `rail` state draws a rising rail made of rotated cubes at atan(16 / (2πr / 8)) ≈ 25° for r = 1.5 blocks. Bedrock geometry carries per-cube rotation on one axis, so the rail is built as a bone with a z-tilt and an inner y-rotation. Verify that the nesting renders; the roof hips already use x and z tilts.

**B. 2 × 2 quarter-turn (the Umsoea layout)** for tight turrets (a 2 × 2 well inside a d-tower)
- `pw:spiral_stairs_tight_<mat>`. Each block is one quarter turn with the post at a corner, 4 per turn, a 1 block rise per block.
- Port the Umsoea treads and rail, re-UV them to `pw_mat_*`, and use the same collision method. Rise per block is 1 and 4 treads at 4 px, so walking is identical to A.
- Its catch: the post is shared by four blocks. Either draw a quarter of the post in each block, or place a separate `pw:newel` thin post with collision against the corner.

**Placement sugar (both).** A companion rule in the `pw_companion.js` pattern. Placing a spiral piece next to (one up from) another piece auto-picks the segment, facing and hand that continue the helix. A builder then holds the item and clicks upward, the same way the 63-roof companion teaches continuation.

**Multi-block note.** `minecraft:multi_block` (vertical, up to 4 parts) is stable from format 1.26.40 and horizontal from 1.26.50. It could place a whole 4-block turn as one item, but breaking any part breaks the whole stack. Per-cell blocks plus a companion are the better fit.

---

## (d) Download recommendations (medieval-realism fit only)

| Pack | Platform | Why | Licence as shown | Link |
|---|---|---|---|---|
| **Feudal Furniture WE 8.8 (RP + BP)** | Bedrock | Newer than his Drive copy (8.7, RP only). 800+ rustic and medieval pieces. The BP gives the original block definitions (states and collision) as a reference | Not stated (MCPEDL) | https://mcpedl.com/feudal-furniture/ |
| **Medieval Furniture Add-On** (EndXenocMC) | Bedrock 1.21.8x–1.21.9x | Built for "castles, taverns, and villages". Has a helmet and armour stand system and a **portcullis gate up to 15 × 16** (castle gatehouse) | All Rights Reserved | https://www.curseforge.com/minecraft-bedrock/addons/medieval-furniture-add-on |
| **Handcrafted** | Java (Fabric / Forge / NeoForge, to 1.21.1) | 250+ pieces including a medieval style. Clean blocky models, so Java JSON converts mechanically. The best furniture geometry library to mine | Terrarium Licence | https://modrinth.com/mod/handcrafted |
| **Conquest Reforged** | Java (Forge / Fabric 1.20.1) | "Thousands of new blocks, models" for medieval realism: baskets, stools, cushions, chests, lanterns, cooking vessels, scroll stand. Large; take only what is needed | All Rights Reserved | https://modrinth.com/mod/conquest-reforged |
| **Macaw's Stairs** | Java | Stair railings and balconies for vanilla stairs (balustrades on our flights). **No spiral** | All Rights Reserved | https://modrinth.com/mod/macaws-stairs |
| **Aesthetic Stairs** | Java | Connected stair rails in all woods. The author notes it is used for spiral staircases. **No spiral block** | MIT | https://modrinth.com/project/hG4v10WD |
| Another Furniture | Java (to 1.21.1) | "Vanilla-styled, consistently sized" furniture; a simple, sound reference set. The page lists no items, so read the pack itself | Custom (GitHub) | https://modrinth.com/mod/another-furniture |
| NXCustomBlocks | Bedrock | Stairs, slabs, columns, big blocks. **Not inspected**; check for columns and stairs before use | not read | https://www.curseforge.com/minecraft-bedrock/addons/nxcustomblocks |

No dedicated spiral-staircase pack exists on Modrinth or CurseForge for Java or Bedrock; the searches returned only generators and tutorials. **Umsoea (already in hand) is the only real helical model found**, and our own design in (c) is the long-term answer.

---

## (e) Plan to fit chosen pieces into our model

1. **Namespacing.** Every imported piece becomes `pw:<family>_<piece>_<mat>`, for example `pw:furn_throne_dark_oak`, `pw:furn_basket_apples`, `pw:furn_fireplace_stone_bricks`, `pw:spiral_stairs_spruce`. Source identifiers (`trono1`, `rf:dinner_table`, `u_spiral_stairs_l`) appear only in the provenance ledger. Geometry ids become `geometry.pw_furn_<piece>`. Files go into BP-02 `blocks/` and RP-04 `models/blocks/pw_furniture.geo.json` (or a sibling `pw_furniture2.geo.json`). Per the furniture ruling there are no new packs.
2. **Conversion tool.** Add `tools/import_geo.py`, two front ends feeding one writer (`furniture_geo.to_bedrock_geometry()`):
   - **Bedrock geo.json** (Feudal, Rustic): keep cubes and pivots, drop the UV.
   - **Java model JSON** (Umsoea, DO, Handcrafted): `from`/`to` become origin and size with (−8, 0, −8); the rotation origin becomes the pivot; flip the y-angle sign per D-C197.
   - Then **re-UV every face** to its world size (16 px = one tile, offset by world position so planks line up across pieces). Assign a `material` per bone (`board`, `post`, `end`, `iron`, `cloth`, `food`), the same keys as our 12 pieces.
3. **Patrix re-skin with the original texture removed.**
   - `material_instances` map to `pw_mat_<wood>_planks`, `pw_mat_stripped_<wood>`, `pw_mat_stripped_<wood>_top`, `pw_furn_iron`, and stone `pw_mat_*`. No source PNG is copied into our RPs.
   - Exceptions are props with no Patrix equivalent: food, baskets, books, cloth. Each needs either a Patrix item texture (the RP-08 items set) projected onto the prop, or the source texture recorded as RESTRICTED.
4. **Behaviour.**
   - Seats join `SEAT_BLOCKS` (throne, settle, pew).
   - Long tables reuse the table auto-join masks; Rustic's L/M/R `dinner_table` and `shelf_table` already follow that pattern.
   - Gates and shutters get an `open` state through a custom component.
   - Collision follows our furniture law: low seats get a 12 px box; stairs get the array (pending the format ruling).
5. **Gates.** `verify_furniture.py` (geometry bounds 30³ and 1 px in the unit, materials resolve, permutations parse), `coplanar_audit.py`, the BDS load gate, then preview sheets (`furniture_render.py`) **for his markup before any block JSON ships** (the catalogue's round rule). Everything stays "shipped, awaiting verification" until he witnesses it on PS5.
6. **RESTRICTED-ASSETS lines.** Add each line to both copies (Drive `AR-Licensing/RESTRICTED-ASSETS.md` and the workspace copy) **in the build that first uses the asset**. Ready-to-paste drafts:
   - `BP-02/RP-04 · models/blocks/pw_furniture*.geo.json + blocks/pw_spiral_stairs_* · spiral stair geometry · Umsoea Funky Models v27 256x (umsoea.com / Patreon) · u_spiral_stairs_l, u_spiral_stairs_r · none in pack; site "© UMSOEA. ALL RIGHTS RESERVED." · <date> · owner Umsoea · purchase route: Patreon / ask author`
   - `BP-02/RP-04 · pw_furniture*.geo.json · furniture geometry · Feudal Furniture WE 8.7 RP (Trotamundos872, mcpedl.com/feudal-furniture) · <piece list> · none stated · <date> · owner Trotamundos872 (trmc-addons.com) · purchase route: none`
   - `BP-02/RP-04 · pw_furniture*.geo.json · furniture/food geometry · Rustic Furniture ("Mrs Trader") · <piece list> · none stated · <date> · owner Mrs Trader · purchase route: none`
   - `… · Medievalism v7 (stairs balustrade / shutters / corbels re-authored as cubes) · "You may not redistribute this pack anywhere." · owner Medievalism (medievalismmc@gmail.com)` (only if a re-authored shape is traced from it)
   - Domum Ornamentum is **LGPLv3**, Aesthetic Stairs is **MIT**, and Townstead is **GPL-3**. These still get provenance-ledger lines. LGPL and GPL would allow a public release only with source obligations, so mark them restricted-for-release as well.
7. **Suggested order** (for his ruling, not started):
   1. `pw:spiral_stairs` (layout A) + `pw:newel`, palace and castle spirals switched over, F2 fixed in the same edit (format ruling first).
   2. Inn and feast set from Rustic and Feudal: long dinner table, food props, baskets, barrels, fireplace.
   3. Market set: awnings and tents, baskets, crates, signposts, Jerry's stalls.
   4. Palace set: throne, tall bookcase, DO coffered panels and columns, wall carpets.
   5. Shutters, window and balustrade set for all houses.
   6. Place the unused `barrel_seat` in the inn and farms.

---

## Retro-Sweep (external artifacts studied: Umsoea, Feudal, Rustic, Craftopia, Medievalism CD, DO, Bedrock collision docs)

Hits are backlog suggestions only; nothing was implemented.

| Subsystem | What changes | Suggestion | Effort | Priority |
|---|---|---|---|---|
| custom blocks / permutations | `collision_box` arrays exist (format 1.21.130+; array-only from 1.26.60) | Roofs, ramps, `roof63` and furniture could get true stepped collision. Note: a 1.26.60 bump would **break every single-box `collision_box`** in BP-02, so plan a migration | M | high (the 1.26.60 break) |
| custom blocks | `minecraft:multi_block` stable (1.26.40 vertical, 1.26.50 horizontal) | The `roof63` upper/lower pair and doors could be one item | S–M | low |
| worldgen / mcstructures | Templates use 438 ladder cells, red carpet only, no candles or chains, 1 trapdoor | Generator pass: rug colours, candles, chains, shutters, unused `barrel_seat` | S | med |
| scripts (BP-02) | Walk graph keys on id substrings (`stairs`, `ramp_`, `ladder`) | Naming law for new blocks; document it in ARCHITECTURE | S | high |
| build / verification tooling | Java-model and Bedrock-geo importer + re-UV | `tools/import_geo.py` (above) | M | med |
| documentation / lessons | Candidate: "Bedrock RP cannot alter vanilla block geometry; Patrix 3D vanilla models need pw: replacements" and "custom blocks cannot be climbable; keep vanilla ladders where civs and players climb" | Lesson candidates | S | med |

No hit: terrain caps · trees / canopy / falling-tree · redwood biome · mobs (RP-07) · atmospherics / sky / fog · PBR / MERS (except the re-skinned pieces later needing `_mer`) · audio.
