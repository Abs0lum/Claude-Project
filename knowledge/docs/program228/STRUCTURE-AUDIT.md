# STRUCTURE AUDIT — every BP-02 template, block by block (2026-10-06)

Abs0lum's ruling: *"every structure checked to be using our unique blocks (sloped roof ridges instead of stepped roofs
like regular Minecraft creates; our trees and make sure we don't import worse versions; etc.)"*.

This is a static read of the files. Nothing was changed in the pack. Every number below comes from
`tools/structure_block_audit.py` (new, 969 lines) run over the built pack, or from a file named beside it.
**Static checks can only rule things out. Every finding here is waiting for an in-game check (P1).**

- **Pack audited:** `/home/claude/_build/bp02-227/structures/`. That is 833 `.mcstructure` files. The pack was only read.
- **Also audited (not in the pack yet):** the staged castle in `_staging/civ/castle/mvv_castle_bl1/`: 4 pieces and 24 stage files.
- **Our blocks:**
  - the pack's `blocks/`: 522 ids (the JSON-with-comments parser reads all 522 files, including the 15 sf_nba egg files that strict JSON rejects)
  - the CIVITAS markers BP `markers-0.2.4-bp/blocks/`: 38 ids, including `pw:manhole_cover`
- **Vanilla ids:**
  - `_intake/bedrock-samples/resource_pack/blocks.json` from 1.26.50.4 (1,353 keys)
  - If an id is missing there, the tool looks for the exact string `minecraft:<id>` in the BDS 1.26.52.3 binary. Two ids passed this way: `minecraft:grass_block`, whose blocks.json key is the legacy `grass`, and `minecraft:iron_chain`.
- **Machine output:** `_docs/program228/STRUCTURE-AUDIT.json`. It holds per-file counts by class, every finding with its local x, y, z, and the stair and slab use census.

Command (about 100 s):

```
python3 tools/structure_block_audit.py --scripts --root _build/bp02-227/structures _staging/civ/castle/mvv_castle_bl1 \
        --json _docs/program228/STRUCTURE-AUDIT.json
python3 tools/structure_block_audit.py --selftest      # synthetic structures: all 11 detector checks PASS
```

**Premise audit (P11).** These spaces were censused or deliberately left out:

| Space | Status |
|---|---|
| All 833 files under `bp02-227/structures` (`pw/`, `pw/stages`, `pw/trees`, `pw/road`, `pw/ponds`, `sf_nba/`) | CENSUSED: every cell of layer 0 |
| The staged castle (28 files) | CENSUSED |
| Runtime placements: every `setType`, `BlockPermutation.resolve`, `fillBlocks` call in `bp02-227/scripts/*.js`, plus the `CIV_BUILDINGS.dir` re-placement table | CENSUSED. The gallery data and text files are excluded: they hold no placements (checked by grep) |
| Layer 1 of block_indices (waterlogging) | EXCLUSION-VERIFIED: empty (every index is -1) in all 833 files |
| Other packs' structures (BP-01, BP-03, StripMine) | EXCLUSION-VERIFIED: outside this brief, which is BP-02 only |
| Java `.nbt` structures from the studied mods | Not present as `.mcstructure`. They must be converted first, then checked with `--root` (see §8) |

---

## 1. Summary by structure family (the pack's 833 files)

| Family | Files | Files with findings | Cells: OURS / RULED / NO_EQUIV / TECH | Findings |
|---|---:|---:|---|---|
| Buildings, finished (`pw/mvv_*_r1`, 39 village roster) | 39 | **0** | 3,704 / 8,374 / 57,530 / 42,104 | none |
| Building stages (`pw/stages/mvv_*_s0..s4`, 39 × 5) | 195 | **0** | 3,704 / 8,374 / 57,530 / 58,047 | none |
| Palace pieces (`pw/mvv_palace_{ne,nw,se,sw}_a_r1`) | 4 | 4 | 6,110 / 17,921 / 276,493 / 485,726 | **FLAT-SLAB-ROOF 182, ROOF-GAP 9** |
| Palace stages (4 × 5) | 20 | 6 | the same cells, split by stage | the same 182 + 9: canopy in s4, gaps in s3 |
| Road pieces (`pw/road/{t,v}_*`) | 14 | 2 | 52 / 98 / 17,520 / 7,052 | **RAMP 30** (t_ramp7 12, v_ramp7 18) |
| Trees (`pw/trees/*`) | 544 | 12 | 252,931 / 4,839 / 0 / 0 | **TREE-ROOT 12** (jungle_young even numbers) |
| Ponds (`pw/ponds/*`) | 6 | 0 | 0 / 264 / 2,428 / 614 | none |
| Roof kit + test pads (`roof_kit`, `s1..s8`) | 9 | 3 | 244 / 16 / 506 / 210 | **STATE 32** (vertical_half on ridge / roof63) |
| sf_nba add-on (`ant_hill_big/small`) | 2 | 0 | 25 / 0 / 0 / 2 | none |
| **Pack total** | **833** | **27** | | **265 finding cells; 191 are distinct defects once stage copies are removed** |
| *Staged castle (not shipped)* | *28* | *8* | *1,279 OURS, 145 UNKNOWN* | ***UNKNOWN 145: `pw:roof_hip_thatch` does not exist*** |

**What the classes mean:**
- **OURS:** the id is defined in our packs.
- **RULED:** a vanilla id that has an equivalent of ours, but a standing ruling or runtime converter keeps it vanilla in templates (§3).
- **NO_EQUIV:** a vanilla id with no equivalent of ours for that use.
- **TECH:** air, structure void, light blocks, water.
- **UNKNOWN:** defined nowhere.

**Headline: stepped roofs.**
- **There are none in any of the 833 templates.** No vanilla stair, slab or cube roof course exists anywhere (§4).
- **Every roof in the 39 village buildings, the 4 palace pieces and the castle uses the pw roof kit.**
  - The village has no vanilla stairs or slabs at all.
  - The palace has 42 vanilla stairs. All 42 are covered interior flights.
- **Trees use our blocks** (§5):
  - 0 vanilla leaves.
  - Vanilla wood appears only where D-C337 allows it.
  - 0 blocks carry an older generation's states.
  - 12 templates have a doubled root, a defect from the rescale tool.

**Worst offenders** (each one counted once, finished file plus its stages):
1. `mvv_palace_ne_a_r1`: 94 flat spruce-slab canopy cells and 4 roof holes.
2. `mvv_palace_nw_a_r1`: 88 canopy cells and 3 roof holes.
3. `road/v_ramp7`: 18 slab half-steps.
4. `road/t_ramp7`: 12 slab half-steps.
5. The 12 `jungle_young_{00,02,…,22}` templates: one extra root each.
6. The staged castle, before it ships: 145 undefined `pw:roof_hip_thatch` cells across all 4 pieces. Its stables are always roofed with hipped thatch (castlegen line 487). This seed also chose thatch for every other roof (1,246 `roof45_thatch` cells).

---

## 2. Inventory: our unique blocks by family, and the vanilla blocks each one replaces

The counts come from `bp02-227/blocks/` (522 ids) plus the markers BP (38 ids).

| Family (count) | Ids | Vanilla it stands in for | Templates using it |
|---|---|---|---|
| **Roof kit** (33) | `pw:roof45_{oak,spruce,thatch}` · `roof45_ridge_{oak,spruce,thatch}` · `roof_hip_{oak,spruce}` · `roof_ridge_end_{oak,spruce}` · `roof_pyramidion_{oak,spruce}` · `roof63_{lower,upper}_{oak,spruce}` · `roof_gusset_{lower,upper}_{oak,spruce}` · `crown_ring_{oak,spruce,stone}` · `rafter45_{oak,spruce}` · `sweep_s0..s7` (+5 `uv_probe_*` test blocks) | **any `*_stairs` / `*_slab` / full block laid as a roof course, eave trim or ridge**. Hips, ridge ends and pyramidions exist in oak and spruce only; thatch has only the slope and the ridge. `pw_companion.js` `AM_MATS = ["oak","spruce"]` | buildings 3,704 roof+other ours cells; palace 5,675 roof45 + 252 hips; castle 1,246 roof45_thatch |
| **Dual wall** (53) | `pw:wall_<material>`: a full block whose outer face is the material; `pw:inner` picks one of 16 interior finishes | a **2-thick wall**: vanilla masonry outside + a plank or plaster lining inside. **Not** vanilla `*_wall` (the fence-like wall). `minecraft:stone_brick_wall` → `pw:wall_stone_bricks` is a WRONG mapping | none (opportunities only, §6) |
| Wall pieces (4) | `pw:angled_wall`, `pw:room_wall`, `pw:room_wall_corner`, `pw:wall_prism` | half-thickness partitions, angled walls | roof-kit pads only |
| **Hearth / flue** (53 + 53) | `pw:hearth_<m>`, `pw:flue_<m>` | `minecraft:campfire` / `soul_campfire` fireplaces; chimney stacks of plain masonry | buildings, palace, castle (flues + hearths) |
| **Furniture** (36) | `pw:furn_{barrel_seat,bench,chair,coat_pegs,cupboard,dresser,mantel,shelf,stool,table,trestle,wall_shelf}_{oak,spruce,dark_oak}` | stair "chairs/benches", fence + carpet or pressure-plate "tables", trapdoor shelves | buildings, palace, castle |
| **Tree wood** (17 + 20 + 17) | logs `pw:{oak,spruce,jungle}_{young,mature,old,elder}`, `pw:birch_{young,mature,old}`, `pw:dark_oak_elder`, `pw:pale_oak_elder`; roots `pw:<tier>_root` + `pw:{acacia,cherry,mangrove}_root`; stumps `pw:<tier>_stump` | `minecraft:<species>_log` / `_wood` in trees. **Exception, D-C337:** acacia, cherry and mangrove keep vanilla square trunks and mangrove roots (AUDIT-TREES-LEAVES-2026-10-04 §2) | all 544 tree templates |
| **Leaves** (11) + vine (1) | `pw:{oak,spruce,birch,jungle,acacia,dark_oak,mangrove,cherry,pale_oak,azalea,flowering_azalea}_leaves`, `pw:vine` | `minecraft:*_leaves`, `minecraft:vine` | trees (236k leaf cells) |
| Ground (5) | `pw:grass_block`, `pw:podzol`, `pw:mycelium`, `pw:crimson_nylium`, `pw:warped_nylium` | the vanilla ground blocks, **at a terrace riser only** (`pw_ground.js` CONVERSION SCOPE ruling) | none, by ruling |
| Terrain slabs (40) + snowcaps (2) | `pw:slab_<terrain>`, `pw:snowcap_{slab,stairs}` | placed on terrain by the smoother (the `main.js` slab map), never in templates | none |
| **Seated** (64 stairs + 22 plants/snow) | `pw:seated_<stair>`, `pw:seated_<plant>` | a vanilla stair or plant **resting on a bottom slab** (the `main.js` SEATED STAIRS rule and `PW_VEG_SEAT`) | road ramp pieces (4 `pw:seated_stone_brick_stairs`) |
| Planks grid (11) | `pw:<species>_planks_grid` | `minecraft:<species>_planks` (swapped at runtime, §3) | none in templates, by ruling |
| **Ramps** (18) | `pw:ramp_{cobble,smooth_stone,stonebrick}_{2_lo,2_hi,4_q1..q4}` | slab and stair **climbs in a road or walk surface** | road ramps (48 `pw:ramp_cobble_4_q*`) |
| Terracotta tiles (17) | `pw:<colour>_terracotta_tiles`, `pw:terracotta_tiles` | not documented (grep of `_docs` and `tools` finds no mention) | none |
| Markers BP (38) | `pw:manhole_cover`, `pw:frame_post`/`cornerpost`, ports, stations, zones, datum | CIVITAS markers and hatch | buildings (29 manhole covers) |
| Misc (11) | `pw:secret_painting`, `pw:jib_panel`, `pw:gold_coin_pile`, `pw:builders_table`, `pw:held_light`, probes (`compass_ref`, `rotation_probe`, `disc_*`, `fcube_*`) | — | palace (painting, jib), kit pads |
| sf_nba add-on (29) | eggs, ant hill, chrysalis, starfish, shellstone | — | `sf_nba/ant_hill_*` |

**Gaps in our block model** (vanilla used where we have nothing to offer):
- **Timber posts and frames.** The buildings place 930 vanilla logs: spruce 457, oak 296, dark oak 173, birch 4.
  - Our tree logs must **not** stand in for them. `pw_fell_rules.isTreeLogId` treats every `pw:*_{young,mature,old,elder}` as a fellable tree.
  - Timber would need its own `pw:` post or beam family.
- **Thatch hips, ridge ends and pyramidions.**
- **Stone roof pieces.** The palace and castle stone roofs are flat (lead roofs and parapets). Our kit has no stone slope.
- Glass panes, doors, ladders, lanterns, beds, chests, barrels.

---

## 3. The rule set the audit enforces

The rule set below applies to all templates: present ones, future ones, and imports from studied mods.

**Classification of every placed block**, in order:

1. **OURS:** defined in the pack's `blocks/` or a companion pack's `blocks/`.
   - **STATE:** every state name and value must be declared by the block's CURRENT definition. A template baked against an older definition is flagged.
2. **TECH:** air, structure void, `light_block*`, water.
3. **RULED:** vanilla, an equivalent of ours exists, and a ruling or converter keeps it vanilla:
   - `minecraft:<11 species>_planks` → `pw:<s>_planks_grid`. The `pw_planks.js` scanner swaps them near players, and the CIVITAS placer re-flows grid planks after a load.
   - `minecraft:vine` → `pw:vine`. Swapped once by the `pw_vine.js` scanner.
   - `minecraft:{grass_block,podzol,mycelium,*_nylium}`. `pw_ground.js` CONVERSION SCOPE ruling: only the riser at an elevation change converts.
   - Inside `pw/trees/{acacia,cherry,mangrove}_nn`: the species' vanilla log, plus `mangrove_roots`, under D-C337.
4. **NO_EQUIV:** vanilla with no pw equivalent for this use.
5. **UNKNOWN:** defined nowhere. This is a finding: the engine has nothing to place.

**Detectors** (vanilla). Geometry is read from the **composite**: a stage file is judged inside the union of its stem's s0..s4. The finding is filed against the stage that places the block.

| Kind | Rule | Replacement our model uses |
|---|---|---|
| STEPPED-STAIR-ROOF | a vanilla stair at least 3 above ground level G, with open air above it (or directly under a roof cell), AND one of: (a) part of a rising diagonal course: a stair or roof cell one up and one across in its ascent direction; (b) touching a pw roof cell; (c) on a wall top at the edge. An upside-down stair touching a roof is eave trim. **Not roofs:** stairs with a ceiling (interior flights) and stairs below G+3 (steps, curbs) | `pw:roof45_<oak\|spruce\|thatch>`, `cardinal_direction` = the downhill side = the opposite of the stair's high side. `weirdo_direction` 0 E, 1 W, 2 S, 3 N is the HIGH side (palacegen.py:47) |
| STEPPED-SLAB-ROOF | a vanilla slab above G+3 with sky above, on a 1:2 half-step line (surface height in half blocks rising +1 per cell for 2 or more cells), or touching a roof cell | `pw:roof45_<mat>` |
| STEPPED-BLOCK-ROOF | full vanilla blocks on the skyline above G+3 rising 1:1 for 3 or more steps, each step solid below | `pw:roof45_<mat>` courses + ridge |
| FLAT-SLAB-ROOF | a vanilla slab with sky above, roofing a walkable space: air under it, a floor 3–5 below | a `pw:roof45` lean-to, or a ruling to keep it flat |
| SEATED | an upright vanilla stair or plant resting on a bottom slab | `pw:seated_<id>`. The runtime conversion fires on `playerPlaceBlock` only, which a structure load never triggers |
| RAMP | a walk surface below G+3 that climbs a full block as two half steps (lower → a landing of 1–4 bottom slabs → higher), where `pw:ramp_<mat>` exists. Materials: smooth stone, stone brick, cobble | `pw:ramp_<mat>_2_lo/_2_hi` (1–2 cells) or `_4_q1..q4` (3–4 cells) |
| CHAIR / TABLE | an isolated stair (no flight) on a floor under a ceiling; a fence capped by a carpet or pressure plate | `pw:furn_{chair,bench,table}_<oak\|spruce\|dark_oak>` |
| HEARTH | `campfire` / `soul_campfire` | `pw:hearth_<m>` + `pw:flue_<m>` |
| DECOR-TREE | vanilla leaves, or a vanilla log touching leaves, outside the tree templates | a pw tree template |
| TREE-VANILLA | a vanilla log, wood or leaves in a tree template, beyond D-C337 | `pw:<stem>` / `pw:<species>_leaves` |

**pw-block checks:**
- **TREE-TIER:** the logs in `pw/trees/<stem>_nn` must be `pw:<stem>`.
- **TREE-LEAF-SPECIES:** the leaves must be `pw:<species>_leaves`.
- **TREE-ROOT:** exactly one root, `pw:<stem>_root`, with `pw:tpl + 16·pw:tpl_hi == nn`. This is the template `pw_fell_rules.templateName` replays.
- **ROOF-MAT:** one material per connected roof.
- **ROOF-GAP:** a `pw:roof45` slope whose uphill side opens onto air with no roof piece above. Kit and test pads are exempt. The uphill side of a 64×64 piece's outer edge is in the neighbouring piece and is not judged.

**Opportunity (counted, not a finding):**
- **DUAL-WALL:** vanilla M outside + a vanilla finish N inside + interior air, where `pw:wall_M` exists and N is one of its `pw:inner` values.

**Self-test** (`--selftest`):
- It builds a synthetic house with a stepped oak-stair roof, a cobble cube-stepped gable, a half-step slab roof, an interior flight, a chair, a fence table, a campfire, a seated stair, a sidewalk half-step, a vanilla oak tree and an undefined id.
- All 10 detectors fire.
- The interior flight is **not** called a roof.

---

## 4. Stepped roofs: what the audit found

**STEPPED-STAIR-ROOF / STEPPED-SLAB-ROOF / STEPPED-BLOCK-ROOF: 0 in all 833 pack templates and in the 28 castle files.**

Every vanilla stair or slab in the pack was given a use verdict (`stair_slab_uses` in the JSON):

| Where | Vanilla stair / slab | Verdict |
|---|---|---|
| 39 village buildings (and their 195 stages) | **none** | every roof is pw: 976 `roof45_oak`, 1,366 `roof45_spruce`, 329 `roof45_thatch`, plus hips, ridges, ridge ends and 1 pyramidion |
| Palace (4 pieces) | 27 `spruce_stairs`, 15 `stone_brick_stairs` | all covered: interior flights (`palacegen.flight`) |
| | 960 + 25 slabs (stone_brick + spruce) high and open | parapet coping on the flat lead roofs (`palacegen` line 289 "parapet") and similar; flat, not stepped |
| | 20 stone_brick_slab covered, 28 near the ground | floors and the basin rim (line 266) |
| | **182 `spruce_slab` (top half), sky above, air below, floor 4 below** | **FLAT-SLAB-ROOF**: the covered passage (palacegen.py:874, "a 2-wide roofed walk along the alley's north edge"). NE 94 cells, NW 88, at local x 21–22, y 18 |
| Road (14 pieces) | 284 `stone_brick_stairs` near the ground | curbs (no pw curb exists) |
| | 42 + 4 stone_brick_slab, 2 stairs | substructure and steps |
| | **30 `smooth_stone_slab`** | **RAMP**: the sidewalks of `t_ramp7` / `v_ramp7` climb one block as half step → 3-cell slab landing → half step. Example `t_ramp7` (2..4, 15, 0..1 and 11..12). The road bed beside them already uses `pw:ramp_cobble_4_q1..q4` |
| Castle (staged) | 206 stone_brick_slab high and open, 1 smooth_stone_slab covered | parapets; flat |

**Roof integrity findings** (pw pieces, not vanilla):

- **ROOF-GAP: 9 holes in the palace roofs.** All 9 are placed by the s3 stage files.
  - Cells: NE (17,34,21), (17,34,52), (51,30,3), (52,30,4) · NW (15,34,8), (16,34,8), (17,34,9) · SE (62,35,45) · SW (62,35,15).
  - At every gap the uphill column holds a spruce-plank step 1–2 cells below, then air, and a `spruce_log` stands within 2 cells.
  - **Mechanism, traced for NE (16,35,21):**
    1. `palacegen.spiral()` (lines 143–158) clears 3 cells of headroom above every step: `put(x, f+h, z, AIR)` for h = 1..3. It also fills the newel post up to `f1 + 2`.
    2. `wing()` lays `roof_hip(..., F_EAVE)` at line 387 BEFORE `spiral(sx, zc0-1, 0, 18)` at line 406.
    3. `corps()` does the same: roof at line 678, spiral at line 762.
    4. The commons does the same: roof at feet 14 (line 883), spiral to 13 (line 899).
    5. The header puts the attic at feet 15..18 and the eave at 19. So a spiral to feet 18 clears feet 19..21 out of the finished roof.
    6. The post (15, 32..35, 22) runs to feet 20 = f1 + 2, and a roof45 sits on top of it at y 36.
  - The other 8 gaps match the same column pattern; their spiral calls were not traced one by one.
  - **Two further NE edge cells** ((56,34,0), (57,34,0)) slope uphill into the neighbouring piece. They are not judged and not counted.
- **ROOF-MAT:** 0. No connected roof mixes materials.
- **The castle's thatch hips do not exist** (staged castle only).
  - `castlegen.ROOFS = ["spruce","oak","thatch"]` (line 60).
  - `roof_hip()` (lines 187–207) writes `pw:roof_hip_{wood}` and, for odd squares, `pw:roof_pyramidion_{wood}`.
  - The stables always pass `"thatch"` (line 487).
  - Result: 145 `pw:roof_hip_thatch` cells across all 4 pieces (22 / 26 / 51 / 46). Those hip cells would be missing from the roof, and how the engine handles the undefined id on load is unverified.
  - `pw:roof_pyramidion_thatch` is equally undefined. This seed drew no odd square, so no cell carries it.

---

## 5. Trees: what the audit found

The 544 templates were checked against our blocks and against older or "worse" versions.

| Check | Result |
|---|---|
| Vanilla leaves in tree templates | **0** |
| Vanilla wood in tree templates | 4,839 cells, all D-C337: `mangrove_roots` 1,986, `acacia_log` 1,291, `cherry_log` 799, `mangrove_log` 763 (the same numbers as the 10-04 tree audit, §2) |
| Leaf species = template species | 0 mismatches |
| Log tier = template stem (no older or other tier mixed in) | 0 mismatches |
| States not declared by the current block definitions (an older generation baked in) | **0** across 252,931 pw cells |
| Root index `pw:tpl + 16·tpl_hi == nn` | 544 / 544 correct |
| Exactly one root | **532 / 544. The 12 even `jungle_young_{00..22}` have TWO roots, at (x,0,z) and (x,1,z)** |
| Falling-tree index `FT_TPL_NAMES` ↔ templates | 544 / 544 both ways |
| Park trees (`PARK_TREE_SET`, 65) and TREEGROW pools (9 `_pool` calls in main.js) | all names resolve |
| Decorative trees inside buildings, palace, castle, roads, ponds | 0 vanilla leaves; no vanilla log touches leaves |

**Double root: the mechanism.**
- **In staging, before the rescale,** `_staging/trees/jungle/jungle_young_00` has one root at (3,0,3).
- **In the pack,** `jungle_young_00` has `pw:jungle_young_root` at (3,0,3) AND (3,1,3).
- **The rescale stretched these trunks.** `_docs/trees/rescale_report.json` gives jungle_young_00 a crown base CBH of 3 → 5. That is a vertical stretch of the bare trunk; the odd templates shrink instead (01: 8 → 5).
- **The stretch copies the root block upward.**
  1. `tree_rescale.py`'s BRANCH WOOD pass (the line join, about lines 176–191) forward-maps every pair of touching old wood cells.
  2. It fills the cells between them with `pi`, which is the **lower** cell's block.
  3. The root at y0 and the first log at y1 map to y0 and y2, so the join writes the root block into y1.

**Effect:**
- The felling walk still ends on the lowest root, so the replayed template index is right.
- A root block sits one block up the trunk. A second root flare is expected to show there; this has not been witnessed.

---

## 6. Other findings and opportunities

- **STATE: 32 cells in 3 test structures.**
  - `roof_kit.mcstructure` carries `minecraft:vertical_half` on `roof45_ridge_oak` (4), `roof63_lower_oak` (12) and `roof63_upper_oak` (12). `s2_hip_junction` (1) and `s4_ridge_run` (3) do the same on ridges.
  - The current definitions of those blocks have no `placement_position` trait.
  - Sources:
    - `roof_fix_174.py` `setb()` (line 318): the prefix test `startswith(("roof45", …))` also matches `roof45_ridge`.
    - `roof_kit.py` lines 30–31 (roof63).
- **DUAL-WALL opportunity:** this is a design change, needs a ruling, and is never auto-applied.
  - Palace: 1,079 cells (1,069 `pw:wall_stone_bricks [pw:inner=spruce_planks]`, 9 oak, 1 chiseled).
  - Castle: 57 cells (55 mossy).
  - These are 2-thick stone + plank-lining walls (`palacegen.shell` + `panel_room`).
  - Merging them changes the wall thickness and therefore every room plan.
- **No** SEATED, CHAIR, TABLE, HEARTH, DECOR-TREE or UNKNOWN finding in the pack.

---

## 7. Runtime placements that should use our blocks (scripts)

Literal vanilla ids that the pack's scripts place, where our model has an equivalent:

| Script : line (built 227, the same lines in `tools/bp02_src_228`) | Placement | Our block | Verdict |
|---|---|---|---|
| `pw_civ_clock.js:5488` (park builder) | `setType("minecraft:oak_stairs")`: four park **benches** | `pw:furn_bench_oak` + `minecraft:cardinal_direction` facing the path | **FINDING**. Also, `setType` with no states gives the type's default permutation, so all four benches share one facing. That is inferred from the code and has not been witnessed |
| `pw_civ_clock.js:2421, 3016, 6231, 6232` | `spruce_planks` bridge and pier decks | `pw:spruce_planks_grid` | RULED: the plank scanner swaps them near players |
| `pw_civ_clock.js:2420, 3013, 4384, 4390` | `spruce_log` piers and corridor posts | none (timber gap, §2) | NO_EQUIV. Not a tree log of ours: that would make them fellable |
| `pw_civ_clock.js:2543, 5484, 5489`, `pw_civ_shop.js:358` | oak and spruce fences, lanterns, barrel (park, stall, square) | none | NO_EQUIV |
| `pw_civ_clock.js:2736, 2777, 5203` | cobblestone and mossy walls (kerbs, markers) | none (vanilla `*_wall` ≠ `pw:wall_*`) | NO_EQUIV |
| `CIV_BUILDINGS.dir` (`pw_civ_buildings.js`): blocks the clock re-places after a rotated stage | 71 ids (23 vanilla), the same as the templates (e.g. 457 spruce_log posts, 1,366 roof45_spruce) | — | adds no vanilla that the templates do not already have |

No script places vanilla leaves, campfires, roof stairs or slabs. Trees are always placed from our templates (TREEGROW, park trees, the woodcutters' saplings).

---

## 8. Where each fix belongs, and the recommended design

Fix each one at its source, then regenerate. Never hand-edit an output.

| # | Family → source | Function / line | Fix design | Regenerate |
|---|---|---|---|---|
| F1 | **Castle** → `tools/castlegen.py` | `ROOFS` (line 60); `roof_hip()` (lines 187–207); stables `roof_hip(..., "thatch")` (line 487) | **Ruling needed.** **(a)** A thatch roof over a rectangle becomes a GABLE: `roof45_thatch` + `roof45_ridge_thatch` both exist. Hips stay oak or spruce only. **Or (b)** author `pw:roof_hip_thatch`, `pw:roof_ridge_end_thatch`, `pw:roof_pyramidion_thatch` (BP definition + RP-04 geometry and texture) and add `"thatch"` to `pw_companion.js` `AM_MATS` | re-run `castlegen.py --write --verify` + staging; then make `castle_verify.py` run `structure_block_audit.py --root <castle dir>` and fail on UNKNOWN |
| F2 | **Palace roof holes** → `tools/palacegen.py` | `spiral()` (lines 143–158) and its callers `wing()` 406, `corps()` 762, the commons 899 (also gate 351 and tower 619) | `spiral(..., ceiling=None)`: never clear headroom, or run the post, at or above the eave. Equivalent alternative: skip any cell already holding `pw:roof*`. Stop the attic flights at the attic floor (feet 15) rather than 18 | `palacegen.py` → `palace_light_s0.py` → `civ_stages` cut → BP build |
| F3 | **Palace covered passage** → `tools/palacegen.py` | the slab canopy at line 874 | **Ruling needed:** keep a flat walk roof, or roof it with a new `p.roof_lean(x0,x1,z0,z1,eave,downhill,wood)` helper. The helper would lay one `pw:roof45_spruce` course falling away from the alley wall, plus a ridge-less high edge against it. Note that `civ_stages.stage_of` files the slabs in s4; roof45 pieces would move to s3 automatically | same as F2 |
| F4 | **Road ramp sidewalks** → `tools/road_kit.py` | the surface remap (pieces at y ≥ 13). `t_*` surfaces are **Abs0lum's own StreetKit** | **His call (his authored piece).** Replace each sidewalk "half step → 3-cell slab landing → half step" with `pw:ramp_smooth_stone_4_q1..q4` rising along x, matching the road bed's `pw:ramp_cobble_4_q*` | `road_kit.py`; the BP build copies `_docs/road_kit/` into `structures/pw/road/` |
| F5 | **Jungle young double root** → `tools/tree_rescale.py` | BRANCH WOOD line join (about lines 176–191): `new[c] = pi` | When the lower cell `k` is a `*_root`, fill with the upper cell's block (`old_wood[k2]`). Or exclude `*_root` cells from the joins: the trunk column is already vertically mapped and line 197 re-sets the root | re-run on `_staging/trees/jungle` for the 12 files (as `build_bp02_218.py` does), then `ft_tpl_gen.py` for their RP-01 falling-tree geometries. The index order is unchanged |
| F6 | **Test structures** → `tools/roof_fix_174.py`, `tools/roof_kit.py` | `setb()` line 318; `roof_kit.py` lines 30–31 | Derive the states from the block definition (the audit's `state_space`), not from an id prefix | re-run both (test pads only) |
| F7 | **Runtime park benches** → `tools/bp02_src_228/pw_civ_clock.js` | line 5488 | `BlockPermutation.resolve("pw:furn_bench_oak", {"minecraft:cardinal_direction": <facing the crossing path>})` | next BP-02 build |
| — | **Village buildings** → `civ_roster.py` / `civgen.py` / `civ_stages.py` / `civ_village_data.py` | — | **No finding.** Keep the audit as the gate | — |
| — | Ponds (`lake_features.py`), sf_nba (add-on), trees other than the 12 | — | no finding | — |

**Gate for every future template, including structures imported from the studied mods:**
1. Convert Java `.nbt` to `.mcstructure` first.
2. Run `python3 tools/structure_block_audit.py --root <dir> --json <out>`. It exits 1 on any FINDING, UNKNOWN, STATE, TREE-* or ROOF-* result.
3. Wire it into the build scripts, after structures are copied and before packaging. Wire it into `castle_verify.py` as well.
4. An imported structure must also pass the stepped-roof detectors. Its vanilla stair, slab or cube roofs are re-authored in `pw:roof45`, and its vanilla trees are swapped for pw templates.

---

## 9. Retro-Sweep (a new tool built)

- **Hits:**
  - build/verification tooling: add the audit as a build gate (F1 and the gate above). Effort S. High priority.
  - trees: F5. Effort S. High priority.
  - custom blocks: thatch hip, ridge end and pyramidion (F1 b). Effort M. Medium priority.
  - worldgen/mcstructures: F2–F4. Effort S–M. Medium priority.
  - scripts (BP-02): F7. Effort S. Low priority.
  - documentation/lessons: there is a lesson candidate. Any generator that clears headroom must run before the roofs, or respect them (F2).
- **No-hit** (walked): terrain caps · redwood biome · mobs (RP-07) · atmospherics/sky/fog · PBR/MERS textures · audio.
