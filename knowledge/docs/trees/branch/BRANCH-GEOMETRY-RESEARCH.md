# BRANCH-GEOMETRY-RESEARCH — engine limits for dodecagon branches, forks and collars
**Date:** 2026-09-30 · **Type:** READ-ONLY research (Task B). Nothing in any pack was changed.
**Status of every claim:** DOC = quoted from Microsoft Learn or the Bedrock Wiki (URL given) · PROJECT-WITNESSED = shipped in our packs and confirmed in-game by Abs0lum (record cited) · SHIPPED = in our packs, but I found no witness record for that exact feature · TOOL = Blockbench source (not an official rule) · **UNVERIFIED** = no source found; needs an in-game probe before anyone relies on it.

---

## 0 · Sources read (with snapshot dates)

| Source | How read | Snapshot / date |
|---|---|---|
| Microsoft Learn creator docs | git clone of `MicrosoftDocs/minecraft-creator` (the source of learn.microsoft.com/minecraft/creator); key pages re-checked live over HTTPS (all return 200 and contain the quoted text) | repo HEAD `ba7a3b48`, 2026-09-30. Per-page `ms.date` quoted below. **Several pages carry an old `ms.date` (02/11/2025) but contain notes up to 1.26.30, so `ms.date` is not a reliable "last edited" date.** |
| Bedrock Wiki (wiki.bedrock.dev) | git clone of `Bedrock-OSS/bedrock-wiki`; key pages re-checked live | repo HEAD `ed49e244`, 2026-09-27 |
| Blockbench source (`JannisX11/blockbench`, `js/formats/bedrock/bedrock.js`, `lang/en.json`) | git clone | HEAD `e2ede080`, 2026-09-21 |
| Our geometry | `/home/claude/_build/rp01-104/models/blocks/` (newest RP-01 build dir; matches the v1_3_104 mcpack, so no unzip was needed) | 7 files, see §2 |
| Our BP blocks | `/home/claude/_build/bp02-195/blocks/` | see §2.3 |
| Java | `/home/claude/_intake/java-26.3-trees/decompiled/.../trunkplacers/FancyTrunkPlacer.java` (206 lines, 8,065 bytes; first line `package net.minecraft.world.level.levelgen.feature.trunkplacers;`) plus Forking / Cherry / UpwardsBranching / DarkOak placers | — |

Calculation scripts (scratch, re-runnable): `/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/calc/branch_fit.py` (bounding-box fit) and `euler.py` (compound angles).

---

## 1 · HARD ENGINE RULES (quoted, with URL)

### 1.1 Geometry size and position (the "30 px box")

**Microsoft Learn — "Advanced Block Visuals: Sizing and Culling"** (`ms.date: 06/10/2025`)
https://learn.microsoft.com/en-us/minecraft/creator/documents/customblockoversized
> 1. Your block is limited to 30x30x30 pixels in size.
> 2. The absolute bounds of the position of your 30x30x30 block are 30 pixels in each direction from the origin. The origin is in the middle at the bottom of the base 16x16x16 block. … Your block can be placed in any position within these bounds, as long as it adheres to rule #3.
> 3. At least 1 pixel of your block on each axis must be contained by the base 16x16x16 block.
> …parts of the block that are outside of that 16x16x16 range will overlap with other blocks.

**Bedrock Wiki — Block Components › Geometry** (snapshot 2026-09-27)
https://wiki.bedrock.dev/blocks/block-components#geometry
> 1. Your block is limited to 30×30×30 pixels in size.
> 2. At least 1 pixel of your block on each axis must be contained within 16×16×16 block unit.
> 3. The absolute bounds of the position of your 30×30×30 block are 30 pixels in each direction from the origin.

**Sources disagree on one detail (list both):**
- MS Learn / Wiki: the 30-px box may sit anywhere within ±30 px of the origin `(0,0,0)` (bottom-centre of the cell), as long as ≥1 px on each axis is inside the cell.
- Blockbench (TOOL, `lang/en.json` `format.bedrock_block.info.size_limit`): *"Size total size of a block is limited to 30 pixels in all dimensions. The limit can be off-centered in all directions by 7 pixels from the block center."* Its size checker (`cube_size_limiter`, `rotation_affected: true`) measures the **rotated** corner positions of every cube. Under Blockbench's rule the 30-px box always contains the whole cell.
- Our own witnessed laws (engine-laws memory): *"Block geometry ≤30px cap"* and *"Block geometry must touch its own unit cube on every axis (a cap dropped wholly below the cell is refused)"*.
- **UNVERIFIED:** whether the engine measures the box before or after cube/bone rotation. Treat the **post-rotation** box as binding (Blockbench's conservative reading). Every number in §3 is post-rotation.

### 1.2 Cube and bone rotation inside block geometry

**Microsoft Learn — geometry schema 1.21.0** (no `ms.date`; repo 2026-09-30)
https://learn.microsoft.com/en-us/minecraft/creator/reference/content/schemasreference/schemas/minecraftschema_geometry_1.21.0
- Bone: `"rotation"[3]` — *"This is the initial rotation of the bone around the pivot, pre-animation (in degrees, x-then-y-then-z order)."*; `"parent"` — *"Bone that this bone is relative to."*
- Cube: `"rotation"[3]` — *"The cube is rotated by this amount (in degrees, x-then-y-then-z order) around the pivot."*; `"pivot"[3]` — *"If this field is specified, rotation of this cube occurs around this point, otherwise its rotation is around the center of the box."*
- Also in this schema: `inflate`, `mirror`, per-face `uv` / `uv_size` / `material_instance`, and `uv_rotation` (§1.4). `poly_mesh` is listed as ***EXPERIMENTAL***.

**What the docs do NOT say:** neither MS Learn nor the Bedrock Wiki gives any block-specific limit on rotation angle (no 22.5° grid, no ±45° clamp), on how many axes one cube may rotate on, or on whether bone rotation and bone parenting are honoured in block geometry. The schema is shared by entities and blocks.
- **Java-style limits do not apply to Bedrock blocks.** Blockbench's Bedrock Block format sets `rotate_cubes: true` and `bone_rig: true`, and defines no `rotation_limit` or `rotation_snap`. Those two flags exist only in its Java block format (`java_block.ts`: single axis, ±45°, 22.5° snap).
- **What we have in-game** (census of our shipped block geometry, RP-01 .104 + RP-02..RP-08 latest):

| Feature | Evidence | Status |
|---|---|---|
| Single-axis cube rotation at non-22.5° angles: 63.435° (roof63), 26.5651° / 14.0362° (ramps, snowcaps), 15° / 22° (furniture) | 65 cubes | 63.435 PROJECT-WITNESSED (FINDINGS-DECK-INVESTIGATION-2026-08-15: *"arbitrary float rotations already witnessed shipping at 63.435"*; roof family witnessed complete 2026-09-20). Others SHIPPED. |
| Single-axis cube rotation on X, Y or Z at ±45° | 80 cubes (roof45, hip = Z, pyramidion = X and Z) | PROJECT-WITNESSED (roof arc, HANDOFF 2026-09-20) |
| Bone rotation about Y, including 30° steps | dodecagon logs: 96 off-grid bone rotations | PROJECT-WITNESSED (dodecagon trunks locked v1.2.19+ / v1.2.26) |
| Bone `parent` in block geometry | leaf variant geometries, parents with **no** rotation | SHIPPED |
| **A cube or bone rotated on 2 or 3 axes at once** | **none anywhere in our packs** | **UNVERIFIED** |
| **A rotated parent bone carrying rotated child bones** | **none** | **UNVERIFIED** |

Rotation sign conventions are already project law: **L-ROT-DIR** (verified 2026-09-27, D-C255): a file rotation `[rx, ry, rz]` acts on points as `Rz(−rz)·Ry(+ry)·Rx(−rx)`, X first. Also the **X-mirror law** (model +x renders world west) and **L-ROT-1**. These two laws decide which way a branch leans.

### 1.3 `minecraft:transformation` (whole-block rotate / scale / translate)

**Microsoft Learn** (`ms.date: 02/11/2025`)
https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_transformation
> The block's translation, rotation and scale with respect to the center of its world position.
> Added in 1.19.80 … May be added to the whole block and/or to individual block permutations.
> Added rotation_pivot and scale_pivot attributes in 1.21.0.
> | rotation | [0, 0, 0] | Array of numbers | The block's rotation in increments of 90 degrees |
> | scale | [1, 1, 1] | … The block's scale | translation | [0, 0, 0] | … The block's translation |

**Bedrock Wiki** (2026-09-27) https://wiki.bedrock.dev/blocks/block-components#transformation
> Determines the transformation of the block's geometry, collision box and selection box.
> **Transformed models must not exceed the block geometry limits.**
> `rotation` … Must be in increments of 90 (negative for anticlockwise rotation).
> `rotation_pivot` … By default, rotation is around the center of the block. `scale` — The factor to scale the geometry by on each axis. `translation` — The number of block units to offset the geometry by on each axis.

- **Rotation:** multiples of 90° only, on any of the 3 axes (both sources agree).
- **Scale and translation:** any value. Neither source states a step or range beyond "must not exceed the geometry limits".
- **Driven by permutations:** yes. The MS note says it can be added per permutation; the MS placement_position example rotates a torch per `minecraft:block_face` state.
- **Culling follows the rotation:** *"if a `minecraft:transform` component rotates the block, the directions rotate as well"* (MS Block Culling, link in §1.6).
- **UVs rotate with the geometry by default.** `uv_lock` (see §1.5) is the opt-out.

### 1.4 Per-face UV, `uv_rotation`, material instances

- **Per-face UV** (schema 1.21.0, URL above): each face has `uv`, `uv_size` and optional `material_instance`. *"Omitting a face will cause that face to not get drawn."*
- **`uv_rotation`:** *"Specifies an optional rotation for the specified UV rect in 90-degree clockwise increments before applying it to a geometry cube face."* The schema-1.21.0 page states: *"with a new uv_rotation attribute"*. Blockbench writes geometry `format_version` **1.21.0** as soon as any face has a UV rotation (`getFormatVersion()`).
  - Our log geometries are `format_version 1.16.0` → any branch that needs `uv_rotation` must be authored at geometry format ≥ 1.21.0. The Wiki's glazed-terracotta example uses `uv_rotation` in a 1.26.50 block geometry: https://wiki.bedrock.dev/blocks/custom-glazed-terracotta
- **Rotated cubes:** no doc gives a special UV rule. The face UV rides with the face.
  - Our own UV-proportion law applies: a face reads undistorted iff `uv_size.u : uv_size.v = face width : face height` (FINDINGS-DECK-INVESTIGATION-2026-08-15 §2).
  - A 45° branch face is 22.6 px long, not 16. Its bark band must be sampled ×1.414 longer, or the bark stretches. This is exactly the deck45 case.
- **`minecraft:material_instances`** (`ms.date: 02/11/2025`)
  https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_material_instances
  > Maps face or material_instance names in a geometry file to an actual material instance… **Limited to 64 instances.** From 1.21.80 onward, when using a minecraft:geometry component or minecraft:material_instances component, you must include both. In format version 1.26.20, `ambient_occlusion` no longer accepts boolean values…

  Keys are `*`, `up`, `down`, `north`, `south`, `east`, `west`, or any custom name set per face in the geometry (our logs use `*` + `log_top`).
  - Project laws still stand: *permutations replace material instances wholesale*, and *custom-block material_instances take one texture per key*.

### 1.5 `minecraft:geometry` extras: bone_visibility, culling, uv_lock, n_way_visual_rotation

**Microsoft Learn — minecraft:geometry** (`ms.date: 02/11/2025`, content includes 1.26.30 notes)
https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_geometry
- *"The description identifier … must either match an existing geometry identifier … or be one of … `minecraft:geometry.full_block` or `minecraft:geometry.cross`."*
  - `minecraft:geometry.full_cube` was *"added in 1.20.60 to provide the most efficient rendering path for 1x1x1 blocks"*.
  - From format 1.26.0, `full_block` renders its DOWN face rotated 180°. `full_block_v1` keeps the old orientation.
- **`bone_visibility`:** *"An optional list of true/false values that define the visibility of individual bones … As of 1.20.10, bone visibility values support Molang expressions."*
  - The Wiki adds that the Molang *"must adhere to permutation condition limitations"* (only `q.block_state()`).
  - This lets **one geometry carry several optional stubs/collars**, switched per state.
  - **UNVERIFIED:** whether hidden bones still count toward the 30-px box. Assume they do: the box is a property of the geometry file.
- **`culling`:** *"identifier of a culling definition"* (1.20.60+). **`culling_shape`:** voxel shape used to cull neighbours (format 1.26.30). **`culling_layer`:** experimental.
- **`uv_lock`** (format ≥ 1.21.100): *"A Boolean locking UV orientation of all bones … or an array of strings locking UV orientation of specific bones. … for cubes using Box UVs … only supported if the cube faces are square."*
- **`n_way_visual_rotation`** (format ≥ 1.26.30): *"The name of a block state that drives visual-only rotation of this block. … rotates the geometry accordingly without changing collision or interaction. Supported states are `minecraft:cardinal_direction`, `minecraft:sixteen_way_rotation`, and any custom integer state."*

**Bedrock Wiki — N-Way Rotation** (2026-09-27) https://wiki.bedrock.dev/blocks/n-way-rotation
> **KNOWN ISSUE (MCPE-241952):** N-way rotation is only visible to the player hosting the world, not remote players joining. **For servers, this means it is not visible to any players.**
> …only targets block geometry [collision and selection are NOT rotated]. …can only be defined in the root `components` object … cannot be specified per permutation. …not supported by multi-blocks.
> The angle of rotation increases by 360/N degrees … for each subsequent state value. …a single block state can have a maximum of 16 values, meaning 16-way rotation is as precise as your block can get.
> Keys (`x`, `y` or `z`) … Other keys (`x` and `z`) can also be defined here if you would like those axes to have N-way rotation too.

**Bedrock Wiki — Block Format History** https://wiki.bedrock.dev/blocks/block-format-history
- **1.26.30:** `n_way_visual_rotation` added under *Upcoming Creator Features* (experimental). *"defined as an object where keys are axes (`x`, `y` or `z`) and values are state names"*.
- **1.26.40:** *"Released `n_way_visual_rotation` parameter from experimental"*; `minecraft:sixteen_way_rotation` released; `y_rotation_offset` allowed with it.

**Sources disagree:** MS Learn types `n_way_visual_rotation` as a **String** (a single state name). The Wiki and its format history describe an **object keyed by axis** (`{"x": …, "y": …, "z": …}`). **UNVERIFIED** which one the engine accepts. The Wiki's examples and format history are the more specific source.

**Consequence for us:** we deliver to PS5 through a **Realm**, which is a server. Per MCPE-241952, N-way rotation would be invisible to every player there.
- **UNVERIFIED:** the bug's current status (bugs.mojang.com not checked).
- **UNVERIFIED:** whether our Realm and clients run ≥ 1.26.40. Our manifests declare `min_engine_version [1,21,120]`; blocks are format 1.21.80 / 1.21.10.

Until both are witnessed, N-way rotation is **not usable for branches**.

### 1.6 Culling
**MS Block Culling** (no `ms.date`) https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/definitions/blockculling
> A face or bone culls (becomes invisible) if the neighbor in the "direction" direction is full and opaque (a full cube, and drawing using the "opaque" render-method…). Note that if a `minecraft:transform` component rotates the block, the directions rotate as well.

Bedrock Wiki https://wiki.bedrock.dev/blocks/block-culling:
> `"face"` … This is usually the same as the rule's "direction" unless your cube is rotated.

Culling works per cube face and per neighbour direction. It is **never automatic** for custom geometry. A diagonal branch has no faces that line up with a neighbour, so it simply never culls. That is harmless: branch neighbours are air or leaves.

### 1.7 Placement traits
**MS placement_direction** (`ms.date: 11/05/2025`) https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/traits/placement_direction
> The valid values for `y_rotation_offset` are `0.0` (the default, no rotation), `90.0`, `180.0`, and `270.0`. The offset only applies to horizontal (Y-axis) directions.

States listed there: `cardinal_direction` (4), `facing_direction` (6), `corner_and_cardinal_direction`.

**Wiki block traits** (2026-09-27) https://wiki.bedrock.dev/blocks/block-traits#placement-direction
> `y_rotation_offset` … Only axis-aligned angles may be specified (e.g. 90, 180). Requires format version 1.26.0.

The Wiki also lists a `minecraft:sixteen_way_rotation` state (22.5° steps, released 1.26.40). The MS trait page (dated 11/2025) predates it — **the sources disagree by date**.

**MS placement_position** (`ms.date: 11/06/2025`) https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/traits/placement_position gives `minecraft:block_face` (6 values) and `minecraft:vertical_half` (2).

**45° steps from a trait?** No.
- `y_rotation_offset` accepts only 0 / 90 / 180 / 270.
- The only sub-90° placement state is `sixteen_way_rotation` (22.5° about Y). Its only visual consumer is `n_way_visual_rotation` (§1.5).
- Worldgen- and script-placed branches do not need traits anyway: the placer sets the state directly.

### 1.8 States and permutation budgets
- **MS "Block States and Permutations"** (no `ms.date`) https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockstatesandpermutations
  > A cap of 65,536 permutations that all blocks on a map can generate has been placed due to performance concerns. … "Worlds with over 65536 block permutations may degrade performance. Current world has XXXXXX permutations." This warning will block marketplace ingestion…

  (The same page still says custom states need the Holiday Creator Features experiment. That is stale.)
- **Wiki "Block Permutations › Permutation Limits"** https://wiki.bedrock.dev/blocks/block-permutations#permutation-limits
  > A block *cannot* have more than 65,536 permutations (equivalent to 4 states with 16 values each). This is because a block permutation must be representable by 16 bits. Exceeding this limit will result in some states being absent… A world *shouldn't* have more than a total of 65,536 **custom** block permutations registered (not necessarily placed). Exceeding this limit should not affect block functionality, however will result in the following content log warning…

  Also: *"The number of permutations your block has is based on the states it has, not the number of items in the `permutations` array"* — the full cartesian product of state values.
- **Wiki "Avoiding State Limit"** https://wiki.bedrock.dev/blocks/avoiding-state-limit
  > Blocks have a limit of 16 valid values per state that cannot be exceeded.

  This matches our engine law *"A block-state enum array may hold at most 16 values"*.
- **Our current budget** (my static count of `bp02-195`, states × traits): **439 blocks ≈ 17,592 registered permutations** (largest: sand slabs 320, leaves 168; each dodecagon trunk block 70). That leaves **≈ 47,900 below the 65,536 world warning**. The warning is a performance advisory, not a hard stop. Other BPs (StreetKit etc.) were not counted; the number is approximate.

### 1.9 Things that do not exist or are out of date
- **`minecraft:unit_cube`** — MS: *"This type is now deprecated, and no longer in use."* https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_unit_cube
- **Stand-alone `minecraft:bone_visibility`** — MS: deprecated; use the `bone_visibility` field of `minecraft:geometry`. https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_bone_visibility
- **Maximum number of cubes or bones per block geometry: NOT DOCUMENTED** (UNVERIFIED). The largest geometry we ship has 54 cubes (roof_gusset_lower). The dodecagon logs have 25.
- **Minimum cube size: NOT DOCUMENTED** (UNVERIFIED). Sizes are floats in the schema. We ship sub-pixel sizes (0.4 px gusset strips, 1 px panels, 3.2154 px panels).
- **`poly_mesh`** (true triangle meshes) — schema marks it EXPERIMENTAL. Blockbench's Bedrock Block format does not offer meshes. **Treat as unavailable for blocks** (UNVERIFIED).

---

## 2 · Our round logs today (RP-01 v1.3.104 build dir, BP-02 .195)

### 2.1 File facts (echo)
| File | Bytes | First line |
|---|---|---|
| pw_oak_young_log.geo.json | 50,700 | `{` (`"format_version": "1.16.0"`) |
| pw_oak_mature_log.geo.json | 50,713 | same |
| pw_oak_old_log.geo.json | 50,818 | same |
| pw_birch_young_log.geo.json | 51,062 | same |
| pw_birch_mature_log.geo.json | 51,039 | same |
| pw_birch_old_log.geo.json | 51,168 | same |
| pw_simple_log.geo.json | 2,331 | same |

All seven are geometry `format_version 1.16.0`, `texture_width/height 16`, visible bounds 1.5 × 1.5 (simple: 1 × 1).

### 2.2 Construction
The six dodecagon geometries share one recipe. Each has **25 bones, 25 cubes**, and every bone pivots at `[0,0,0]` with no parents:

| Bone(s) | Cube | Rotation |
|---|---|---|
| `heartwood` ×1 | axis-aligned square core, full 16 px tall | none |
| `spoke_0..11` ×12 | `origin [−w/2, 0, r0]`, depth 2–2.5 px | **bone** rotation `[0, 30·k, 0]` (Y only, 30° steps) |
| `panel_0..11` ×12 | the outer bark flat: `origin [−c/2, 0, a−1]`, size `[c, 16, 1]` | **bone** rotation `[0, 30·k, 0]` |

Every panel's chord `c = 2·a·tan15°`, so neighbouring panels meet flush.
- **No cube carries its own rotation.** Every rotation is a single-axis Y bone rotation.

| Geometry | Heartwood | Spoke (w×d, at r0) | Panel chord c | Apothem a (flat) | Circumradius R | Across flats |
|---|---|---|---|---|---|---|
| oak_young / birch_young | 6×16×6 | 3×2 @ 3 | 3.20 (oak) / 3.2154 (birch) | **6.0** | 6.21 | 12 px |
| oak_mature / birch_mature | 8×16×8 | 4×2 @ 4 | 3.75 / 3.7513 | **7.0** | 7.25 | 14 px |
| oak_old / birch_old | 8×16×8 | 4×2.5 @ 4 | 4.00 / 4.0192 | **7.5** | 7.76 | 15 px |
| simple_log | one 16×16×16 cube | — | — | (square) | — | 16 px |

- **Textures and material slots:** side faces use the default `*` instance (bark). `up` and `down` of every cube use the custom instance **`log_top`** (end grain).
  - Panels map UV bands `[4k, 0]` size `4×16` on a 16-wide sheet, so 12 panels walk the bark texture. Heartwood sides use `8×16`; tops use `16×16`.
  - No `uv_rotation` is used.
- **Block edges:** the dodecagons touch the **top and bottom** faces of the cell (y 0 → 16), so they stack seamlessly. Horizontally they stay inside: max radius 6.2 / 7.25 / 7.76 px against the 8 px half-cell. Across flats they leave 2 / 1 / 0.5 px of air to each side face. `pw_simple_log` fills the cell.

### 2.3 BP blocks (`bp02-195/blocks/*_young|mature|old|elder.json`)

| Block | Bytes | Format | Geometry |
|---|---|---|---|
| oak_young | 14,173 | 1.21.10 | `geometry.pw_oak_young_log` |
| oak_mature | 14,210 | 1.21.10 | `geometry.pw_oak_mature_log` |
| oak_old | 14,099 | 1.21.10 | `geometry.pw_oak_old_log` |
| birch_young | 14,321 | 1.21.10 | `geometry.pw_birch_young_log` |
| birch_mature | 14,358 | 1.21.10 | `geometry.pw_birch_mature_log` |
| birch_old | 14,247 | 1.21.10 | `geometry.pw_birch_old_log` |
| oak_elder | 14,171 | 1.21.10 | `geometry.pw_simple_log` |

- **States:** `pw:variant` [0–4] (bark) × `pw:rseed` [false,true] × `pw:top_variant` [0–6] (end grain) = **70 registered permutations per block**. No traits.
- **Permutations array:** 35 entries (`variant × top_variant`). Each sets only `minecraft:material_instances`: `*` → `pw_<sp>_<tier>_log_vN`, `log_top` → `pw_<sp>_log_top_vM`, both `opaque`. `pw:rseed` is not read by any condition. Custom component `pw:randomize_variant`.
- **Axis:** **no pillar axis, no `minecraft:transformation`, no placement trait.** Every trunk block is vertical-only. Collision and selection are the full cell.
- **Existing branch asset:** RP-01 still ships `geometry.pw_branch` (one 16×4×4 horizontal box, uv 16-wide). FOUNDATION §6.12 describes branch blocks that use it with `pw:direction` 0–3 → `minecraft:transformation` `[0, 0/90/180/270, 0]`. **No block in bp02-195 references it today.** I did not search other BPs.

---

## 3 · ANSWERS

Conventions: 1 block = 16 px. Every piece is centred on the block centre `(0, 8, 0)` unless stated. "Extent" = post-rotation axis-aligned bounding box, worst case over the dodecagon's spin (from `branch_fit.py`).

### 3a · Can a dodecagon log segment be rotated 45° (about X or Z) and stay legal? What length joins corner-to-corner?

**Required axis lengths** (centre of one cell to the centre of the next along the line):
- one-axis diagonal (e.g. up + north) = **16·√2 = 22.63 px**
- full 3-axis diagonal (up + north + east) = **16·√3 = 27.71 px**

A piece of exactly that length, centred on the block centre, ends on the shared corner edge (or corner point). There it butts the next block's identical piece end-to-end on the same axis. The two end faces are coplanar, so the joint has no gap.

| 45° piece, L = 22.63 | R | Extent (post-rotation) | 30-px box | Max L that still fits 30 | Max L inside the strict 16-px cell |
|---|---|---|---|---|---|
| young (a = 6) | 6.21 | 24.78 | **fits** | 30.0 | 10.2 |
| mature (a = 7) | 7.25 | 26.25 | **fits** | 27.9 | 8.1 |
| old (a = 7.5) | 7.76 | 26.98 | **fits** | 26.9 | 7.1 |
| branch a = 5 / 4 / 3 / 2 | 5.18 / 4.14 / 3.11 / 2.07 | 23.3 / 21.9 / 20.4 / 18.9 | fits | 32.1 / 34.1 / 36.2 / 38.3 | 12.3 / 14.4 / 16.4 / 18.5 |

| 3-axis diagonal, L = 27.71 | Extent |
|---|---|
| young | 26.1 |
| mature | 27.8 |
| old | 28.7 (1.3 px margin) |
| a = 5 → 2 | 24.5 → 19.4 |

All fit 30.

Because the pieces are centred, they satisfy both the MS/Wiki rule (inside ±30 px, ≥1 px in the cell) and Blockbench's stricter "box centre within ±7 px" rule.

**The real answers:**
1. **"Stays inside its block space" — only in the 30-px sense, never the 16-px sense.**
   - A 45° tube that joins its neighbour must cross the shared corner edge, and a tube of radius R around that edge sticks into the two side cells (above and to the side) by up to R.
   - To stay inside the 16-px cell, a mature 45° piece could be at most 8.1 px long, far short of the 22.6 px needed.
   - So a 45° branch always overhangs into the cells beside it. The engine allows this (the "oversized block" rule). Those side cells should be air or leaves; a solid block there would show the tube passing through it.
2. **The 25-bone recipe cannot simply be tilted with single-axis rotations.**
   - Each panel is spun 30·k° about the log axis. Tilting the log by 45° means *spin, then tilt*, and for every panel except k = 0 and 6 that is a genuine 2- or 3-axis orientation.
   - Example (`euler.py`, L-ROT-DIR form; signs to be confirmed by probe): the panel spun 30° then tilted 45° about X needs about `[−49.1, 20.7, −22.2]`; the 60° panel about `[−63.4, 37.8, −50.8]`.
   - There are two ways to author it:
     - (i) per-bone 3-axis rotations, which the schema allows;
     - (ii) one parent bone `tilt` rotated `[45,0,0]` about the block centre, with the 25 existing Y-spun bones as its children.
   - **Both are UNVERIFIED on blocks.** We have never shipped a multi-axis rotation or a rotated parent in a block (§1.2).
   - **Exception:** a **horizontal cardinal** log needs only single-axis rotations — spin about X (`[30k,0,0]`) for an east–west log, spin about Z for a north–south log. So it is safe with what we have already witnessed.
3. **Rotating a finished 45° block by `minecraft:transformation`** (90° steps, any axis) gives every other 45° line with no new geometry. The 90° rotations map a dodecagon onto itself, because 90 is a multiple of 30.

### 3b · Which branch directions can be represented, and how many geometries / permutations

**Angles available:**
- Inside geometry: **any angle, any axis.** Single-axis float angles are PROJECT-WITNESSED; multi-axis angles are UNVERIFIED.
- Per placed block: **only multiples of 90°** via `minecraft:transformation`, on X, Y and Z, per permutation.
- N-way visual rotation (360/N, N ≤ 16 per axis) is ruled out on a Realm by MCPE-241952 (§1.5).
- So every non-90° angle has to be **baked into a geometry file**. The 90° group (24 orientations) then copies each baked direction to its symmetric siblings.

**Pick lattice slopes, not 22.5° steps.**
- A branch must re-enter each new cell at the same offset, or every block needs a unique piece.
- tan 22.5° is irrational: a 22.5° line drifts **6.63 px per block** and never returns to the grid.
- Directions made of whole-block steps repeat after a short period:

| Lattice direction (dx, dy, dz) | Elevation | Period (distinct phase pieces) | Line orientations generated by 90° transformations from one piece | Java analogue |
|---|---|---|---|---|
| (0,1,0) axis | 90° / 0° horizontal | 1 | 3 (Y, X, Z) — horizontal ones need the X/Z-spin build (§3a.2) | straight trunk; `getLogAxis` X/Z limbs |
| (0,1,1) edge diagonal | **45°** | 1 | **6**: 4 cardinal 45° up/down lines + 2 horizontal ordinal (NE–SW, NW–SE) | acacia lean, mangrove branches (cardinal + up per step) |
| (1,1,1) body diagonal | **35.26°** | 1 | 4 | fancy oak diagonal limbs |
| (0,1,2) knight | **26.57°** shallow and **63.43°** steep, plus horizontal 1:2 | 2 (same as roof63 lower/upper) | 12 | cherry walk, fancy oak (Java slope 0.381 = 20.9°) |
| (1,1,2)/(2,1,2) ordinal knight | **19.47°** (2,1,2), **41.81°** (1,2,2), 24.09°/54.74° (1,1,2) | 2 | 12 each family | fancy oak limbs at ordinal azimuths |

Arithmetic for the 2-period families: a 26.57° line crosses one cell centred (L = 17.89 px, extent mature 22.5 px), then passes through a cell edge. The two alternating pieces each carry 17.89 px of axis; the second is offset 8 px along the rise. That is the same trick as roof63_lower/upper, and it fits the box (extent ≤ 23 px, AABB y 4.8–27.2).

**Recommended minimal set** (one branch thickness):

| Family | Geometries | Oriented lines |
|---|---|---|
| E (45°) | 1 | 6 |
| B (35.26°) | 1 | 4 |
| K (26.57/63.43) | 2 phases | 24 |
| Horizontal axis log | 1 | 2 |
| Vertical | reuse the trunk recipe at branch radius | 1 |
| **Total** | **6 geometries** | 37 orientation–phase combinations |

- 3 thicknesses → **18 branch geometries**; 4 thicknesses → 24.
- Up vs down needs no extra geometry: the pieces are symmetric, so the line is the same.
- The (2,1,2) 19.47° ordinal family is the closest match to fancy oak's 20.9°. It would add 2 geometries per thickness if Abs0lum wants ordinal shallow limbs.

**Permutation cost** — states multiply, so split families into separate blocks to avoid wasted combinations:
- Per species × thickness, with 5 bark variants:
  - E block: 6 × 5 = 30
  - B block: 4 × 5 = 20
  - K block: 12 × 2 phases × 5 = 120 (states: orient 12 × phase 2 × variant 5)
  - Horizontal block: 2 × 5 = 10
  - **Total ≈ 180**
- 9 species × 3 thicknesses = 27 → **≈ 4,860 permutations** (doubled if `rseed`-style states are kept → ≈ 9,720). That fits the ≈ 47,900 headroom (§1.8).
- If all families were folded into one block (e.g. `fam 4 × orient 12 × phase 2 × variant 5 = 480`), the count would be **12,960**. Unused combinations still count.
- Every state stays ≤ 16 values. The 24 K-family orientations must be split (orient 12 × phase 2).
- `material_instances` stays ≤ 64 per block.
- **Scale via `minecraft:transformation` is not a substitute for thickness geometries on tilted pieces.** Scale applies along world axes. On a 45° piece it would squash the dodecagon into an ellipse and change the length, and the bark texel density would stretch. Scale is only clean on axis-aligned pieces, and even there it scales the length unless the scale on the log axis is 1.

### 3c · Thinner dodecagons — size limits

- **No documented minimum** cube size or count (§1.9, UNVERIFIED). Sizes are floats, and we already ship 0.4 px strips and 1 px panels.
- Panel chord `2a·tan15°`: a = 5 → 2.68 px · a = 4 → 2.14 · a = 3 → 1.61 · a = 2 → **1.07 px**. At our 256-px textures (texture_width 16 → 16 texels per px) a 1.07 px panel still maps about 17 texels.
- **Practical limits** from our own witnessed laws, not from docs:
  - **Depth-fight:** faces within about 0.02 px of each other flicker on the phone (HANDOFF 2026-09-22 seam mechanism). Thin branches should overlap panels generously rather than sit near-coplanar.
  - **Proportional UVs:** 16-px-long, 1-px-wide faces must sample 1:16 bands, or the bark smears.
  - **Cost:** a dodecagon is 25 cubes / ~150 quads per block, against 6 quads for a full cube. Below a ≈ 3 px a 12-sided section is hard to tell from 8 or 6 sides at viewing distance. An octagon (8 panels + core = 9 bones) or a hexagon for twigs would cut the cost roughly in half. This is a design choice, not an engine rule.
- All thin sizes fit the 30-px box at every tested angle (table in §3a).

### 3d · Junction / collar pieces (a branch visibly leaving the trunk)

All allowed within the rules (boxes only, ≤ 30 px box, ≥ 1 px in the cell):
1. **Trunk-with-stub block:** trunk dodecagon (25 cubes) + a short branch-radius dodecagon along the branch direction, from the trunk axis out to about the cell boundary.
   - One geometry per direction family. `minecraft:transformation` Y-90° steps give 4 azimuths, with X/Z steps as needed.
   - Budget: trunk 16 × ±7.8 ∪ stub → mature 45° stub stays under 27 px.
2. **Collar (flare):** 2–3 stacked short dodecagon rings on the stub root, each 1–2 px long, stepping down in apothem (e.g. branch a + 1.5 → a + 0.75 → a) where the stub leaves the bark.
   - Boxes cannot taper, so a smooth fillet is impossible. A stepped ring profile, plus bark whose UV bands continue across the rings, reads as a collar.
   - Cost: 12 cubes per ring. Trunk + stub + 2 rings ≈ 74 cubes, above our biggest shipped geometry (54). **UNVERIFIED performance / cube cap** → probe.
3. **Knuckle / mitre between two straight pieces at a bend** (trunk → 45° branch, or 45° → 26.57°):
   - With square-cut ends, a bend of Δθ opens a wedge gap on the outside of the bend about `2R·tan(Δθ/2)` wide. For a mature trunk at Δθ = 45° that is ≈ 6 px, and it overlaps on the inside.
   - Fill it with a short dodecagon at the **bisector angle** (22.5° for a 45° bend), about `2R·tan(Δθ/2)` long, centred on the joint. This is where a 22.5° piece earns its place: as a joint filler, not as a chain direction.
4. **Several stubs in one trunk block** (forks, cherry/acacia splits): one geometry holding all candidate stubs as named bones, switched by `bone_visibility` Molang on states (documented, §1.5).
   - The whole file must still fit 30 px, including hidden bones (UNVERIFIED either way — assume they count).
   - States multiply fast (4 azimuth bits = 16 combinations × bark 5 = 80 per block).
5. **Collision:** one axis-aligned box per block, y ≥ 0 (engine law). Stubs get the trunk's box or a clipped AABB. Collision cannot follow the diagonal.

### 3e · What block geometry cannot do (needs an entity or a multi-block structure)

| Wanted | Why blocks can't | Alternative |
|---|---|---|
| Arbitrary per-tree angles (e.g. Java fancy oak's random azimuth and 20.9° slope at any heading) | Per-block rotation is 90° steps only; N-way is invisible on Realms (MCPE-241952); every other angle must be a pre-baked geometry | Snap limbs to the lattice families in §3b (Java itself snaps limbs to block steps). For truly free angles, an entity (arbitrary bone rotation and scale via animation / `q.property`), at a per-entity render and tick cost |
| Continuous taper along a limb, smooth fillets, curved limbs | Cubes only (`poly_mesh` experimental, not offered for blocks); 30-px box per block | Stepped rings and discrete thickness tiers per block; entity for curves |
| A branch longer than one piece without cell overlap | 30-px box: a 45° mature piece ≤ 27.9 px | Chain one piece per block, as Java does |
| Per-instance scale or thickness without new permutations | Scale is per permutation, applied along world axes | Thickness tiers as separate geometries or blocks |
| Collision following a diagonal branch | One AABB per block, y ≥ 0 | Accept an AABB approximation, or no collision on thin twigs |
| Animation (sway) of standing branches | Block geometry is static (bone_visibility only toggles) | The falling-tree entity path we already use |
| Multi-cell single parts | `minecraft:multi_block` only stacks parts in a straight line (vertical; horizontal released 1.26.50) and forbids `n_way_visual_rotation` | Worldgen / script structures of ordinary branch blocks |

---

## 4 · What Java branches actually are (for comparison)

`FancyTrunkPlacer` (206 lines):
- **`makeLimb(start, end)`** walks a 3-D DDA line. `steps = max(|dx|,|dy|,|dz|)`, and each step places a **full log block** at `start + floor(0.5 + i·d/steps)`.
- **`getLogAxis`** sets `RotatedPillarBlock.AXIS`: `Y` when the block is directly above the start (no horizontal offset); otherwise `X` if |dx| is the largest horizontal difference, else `Z`.
- **So a Java limb is a staircase of axis-aligned full logs.** It has no diagonal geometry at all; the diagonal is purely in the block pattern.
- **Limb slope:** the branch base sits `horizontal distance × 0.381` below the foliage node, capped at the trunk top, so limbs rise at ≥ atan 0.381 = **20.86°** toward a **random azimuth** (`angle = random·2π`).
- **Other trees:** acacia (`ForkingTrunkPlacer`) and mangrove (`UpwardsBranchingTrunkPlacer`) step one cardinal block **and** one block up per log, and place ordinary vertical logs that touch only along edges: a 45° line in a vertical plane. Cherry places 1–2 sideways logs (axis = branch direction), then a random face-adjacent walk of sideways and vertical logs. Dark oak adds vertical 2–4-long stubs hanging below the crown around the 2×2 trunk.

**Comparison:**
- Java needs 3 log orientations and zero special geometry, because its logs are square and a staircase of squares reads as a branch.
- Our round logs cannot use that trick: a staircase of cylinders shows every step.
- The lattice families in §3b are the "round" equivalent of Java's DDA line. Java's limb directions all live on the same block lattice, so a Java limb from (0,0,0) to (dx,dy,dz) can be redrawn with our pieces whenever its direction falls in a family we build. Otherwise snap it to the nearest one: fancy oak's 20.9° → 19.47° ordinal or 26.57° cardinal.

---

## 5 · UNVERIFIED items and suggested probe (for approval, not built)

1. **Multi-axis cube rotation in a block** (`[rx,ry,rz]` all nonzero).
2. **Rotated parent bone carrying rotated child bones** in a block.
3. **Whether the 30-px box is measured before or after rotation**, and whether bones hidden by `bone_visibility` count.
4. **Cube-count ceiling or performance** at about 75 cubes per block on PS5 and the phone.
5. **`n_way_visual_rotation` on our Realm:** engine version, the MCPE-241952 status, and the String vs axis-object format.
6. **Minimum practical cube size** on hardware (1 px panels, 0.5 px rings).

A single probe block family could settle items 1–4 in one witness round: a 45° mature piece built two ways (compound-angle bones vs a parent tilt bone), plus one 75-cube junction. It would need the L-ROT-DIR sign check and a Perspective-Check photo set.

Mechanism note: nothing in this doc changes a locked lesson. The only conflict found is between documents (MS vs Wiki on `n_way_visual_rotation` format and `placement_direction` states), not with our laws.
