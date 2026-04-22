# PatrixWorld Bedrock Modding Project — Full Handoff (v3)

Resuming a long-running Minecraft Bedrock 1.26.x modding project. Prior chat hit context limit. This document supersedes all previous handoffs. **Read fully before responding.**

---

## TURN 1 PROTOCOL

1. Acknowledge briefly. Do NOT restate this document back.
2. Request the files listed under UPLOADS below (abbreviated — don't explain each one again).
3. Ask the user for the **acacia-didn't-fall screenshot** specifically — they have one saved from a tree that failed to fall, needed for the acacia geometry rework that's pending.
4. Ask what the target for this session is (jungle canopy / acacia geometry / continue block ports / etc. — see backlog below).
5. **Wait for all three** before starting any work.

---

## NEW PROCESS RULE — CRITICAL

**No builds without plan-first discussion.** Every iteration starts:

1. Outline what you intend to change
2. Note tradeoffs + what stays as-is
3. Wait for user's green light or additional direction
4. Then build

The user added this rule explicitly to catch wrong assumptions early. Skipping it is a regression. Investigation/diagnostic work (reading files, computing hashes, comparing colors) is fine without asking — just don't write output files, modify source code, or bump manifests until you've confirmed the plan.

---

## UPLOADS TO REQUEST

### Critical — blocks all work
1. **`Patrix_1.21.11_64x_basic.zip`** (~198 MB) — Patrix Java source, 3056 block PNGs at 64×64, massive OptiFine CTM tile library
2. **`PATRIX-WORLD-SAMPLE-v0_2_5.mcpack`** (5.8 MB) — current sampler
3. **`BIGCANOPY-v2_7_1.mcaddon`** (292 KB) — current falling-tree addon
4. **`PatrixCanopyGen-v0_1_1.mcaddon`** (12 KB) — current canopy-enlarge override
5. **`bedrock-server-1.26.14.1.zip`** (~57 MB) — vanilla tree-feature JSON schemas
6. **The acacia screenshot** — user has saved an image of an acacia tree they chopped that didn't fall. Needed for acacia geometry rework planning.

### Nice to have
7. **`Patrix_1.21.11_64x_addon.zip`** (~42 MB) — stained glass ×16, cake variants, moss_carpet_extra
8. **`Patrix_1.21.11_64x_bonus.zip`** (~10 MB) — foodcrate, tudor decorative blocks

### DO NOT request (reference-only, already extracted)
physics-mod-pro, continuity, tectonic, distanthorizons, flowing_fluids, fluidphysics, wpo, Realistic_Fluids, FallingTree-26_1_2-25.jar, SMARTFALL, Better Foliage (BFBP+BFRP), RealSource_VV+, Alacrity, GlowingOres, LOW_RealisticJAVApack, Smooth_Plant_Animations, Waving-Plants-Shaders-Mod

---

## PROJECT SCOPE

### Four original research domains
1. **Java→Bedrock texture port** (Patrix as concrete case) — manifest, terrain_texture.json, flipbook_textures.json, LabPBR→MERS PBR conversion, OptiFine CTM → Bedrock approximations, biome-tint handling
2. **Emulating Java shaders via Vibrant Visuals** — lighting/atmospherics/color_grading/water/fogs JSONs, emulating Complementary/BSL/SEUS aesthetics. PS5 60fps envelope. Can do: PBR, real-time shadows, SSR, volumetric fog, bloom, SSS, water waves, colored point lights. Can't: SSGI, path tracing on PS5, custom GLSL, DOF, LUT import, cascaded shadow maps
3. **Emulating Java fluid physics mods** — custom `ff:water_finite` block with 8 level permutations via Scripting V2, pool-isolation graph, drain-when-cut-from-source. PS5 budget ~3000–6000 simulated blocks. Haubna limited to FLUIDS only (debris/cloth/ragdoll deferred indefinitely)
4. **Tectonic-inspired worldgen** — 10-biome roster (alpine_peak, alpine_meadow, coastal_bluff, river_canyon, badlands_mesa, boreal_forest, pale_hills, cherry_valley, desert_dunes, icy_cliffs). Hard ceilings: no custom dimensions, no 6D multinoise, no data-driven density functions. Tectonic-Bedrock is biome reskin + decoration on vanilla terrain, not terrain rewrite.

### Six-phase roadmap (current status)
| Phase | Scope | Status |
|---|---|---|
| 1 | Patrix base port | **In progress** — sampler at v0.2.5 (255 shortnames, 847 PNGs, 59 variations arrays) |
| 2 | Vibrant Visuals tuning | **Unstarted** — deferred until PS5 access |
| 3 | FallingTree port | **Shipped** as BIGCANOPY v2.7.1 |
| 4 | Finite fluids v1 | **Unstarted** — research done, zero code |
| 5 | Tectonic worldgen | **Unstarted** — user flagged block variance refinement to happen WITH this phase |
| 6 | Polish (subpacks, CI, profiling) | **Unstarted** |

### Scopes added mid-project (not in original plan)
- **PatrixCanopyGen** — new behavior pack overriding vanilla tree-feature JSONs for larger standing canopies. Shipped at v0.1.1. Jungle override still pending as v0.1.2.
- **Animated Patrix lava** — 8-frame still + 48-frame flow flipbook with blend_frames. In v0.2.1.
- **Composite pointed_dripstone shapes** — generated-from-scratch Patrix-colored tapered silhouettes (8 shapes) replacing vanilla low-res stalactites. In v0.2.5.
- **Bark variance per species** — 160 rotation-synthesized log variants (10 species × 2 faces × 8 variants). In v0.2.5.
- **grass_block_side dirt-portion variants** — 16 composites preserving Patrix grass strip, swapping dirt portion. In v0.2.5.

---

## STRATEGIC DECISIONS (baked in)

- **PS5 primary, Android fallback.** Realms delivery.
- **"Aim for perfection, scale back to what works"** — try the most ambitious approach first, document the floor, ship fallback rather than lowering ceiling.
- **Vibrant Visuals + Experimental Voxel Shapes stay on throughout.**
- **Custom biomes** enable at Phase 5 (achievements disabled for world; explicit trade).
- **Naming discipline** — every build gets unique manifest tag `[TAG vX.Y.Z]` so user can verify in-game which loaded.
- **Block variance for worldgen blocks** (stone/dirt/etc.) is deferred to Phase 5 / Tectonic work — don't burn effort there until worldbuilding control lands.
- **Bark color mismatch on BIGCANOPY falling entity** deferred — waiting for VV on PS5 to unify entity/block lighting. Option C accepted.

---

## CURRENT SHIPPED STATE

### 1. PatrixWorld Sampler v0.2.5 DRIPBARK
- **File:** `PATRIX-WORLD-SAMPLE-v0_2_5.mcpack` (5.8 MB)
- **Stats:** 847 PNGs (552 variant), 255 shortnames, 59 variations arrays, 67 blocks.json entries
- **UUIDs LOCKED:** header `7b5e9f01-3a24-4b6c-9d17-8e5f4c2b19a0`, resources `f2c8d9e4-6a51-4f8b-a3c9-1d8e7b4f5c62`, `min_engine_version [1,26,0]`
- **blocks.json `format_version: 1.1.0`** (do NOT bump)
- **Variations coverage (23 surface blocks × 16 variants each, from Patrix CTM):** stone, andesite, granite, diorite, dirt, coarse_dirt, sand, red_sand, gravel, grass_block_top, mycelium_top/side, cobblestone, deepslate, end_stone, netherrack, mud, packed_mud, mud_bricks, muddy_mangrove_roots_top/side, sandstone_top, red_sandstone_top
- **v0.2.5 additions:** 16 grass_block_side composite variants, 8 dripstone_block variants, 8 pointed_dripstone shape textures, 160 bark variants (10 species × 2 faces × 8)
- **Other Patrix ports:** lava flipbook, log/plank/leaves for all 10 species, terracotta ×16, deepslate family ×5, copper oxidation ×4, all 17 ores, amethyst, ice family ×5, purpur ×3, basalt/blackstone/tuff/calcite/dripstone, soul sand/soil, glowstone/shroomlight, nether wart blocks, moss/clay/snow/bone

### 2. BIGCANOPY v2.7.1 ACACIA
- **File:** `BIGCANOPY-v2_7_1.mcaddon` (292 KB) — nested zip-of-zips (BP.mcpack + RP.mcpack)
- **Script:** `/BP/scripts/main.js` at 1031 lines
- **UUIDs LOCKED:** BP header `be7227ad-138a-45a5-9e38-4c2cf4732440`, BP data `a8b6523b-c9ac-4a1b-8586-aea316833b4b`, BP script `6fed24a7-f6c9-47ef-90ec-6b0b20d5ca0c`, RP header `4410d782-8723-40e3-9586-8262cbb9a1f8`, RP resources `95f4efcf-0333-4373-b470-eea36df91034`
- **Script dependency:** `@minecraft/server` v2.0.0
- **Entity atlas (CRITICAL):** 128×128 with 64×64 regions. Bark sides UV `[0,64], uv_size [64,64]`. Up face `[0,0]`, down `[64,0]`. **NEVER use 16×16 UV** — we regressed on this once.
- **Animation molang multipliers (DO NOT touch):** 0.044 / 0.333 / 0.867 / 1.033 / 0.956 / 1.0 at times 0.35 / 0.9 / 1.4 / 1.65 / 1.72 / 1.8
- **4 canopy geometries:** small 5×4×5 conic-down (spruce/crimson/warped), medium 5×4×5 pancake (oak/birch/acacia), large 7×4×7 (jungle/dark_oak/mangrove), huge 11×4×11 (cherry)
- **10 species with LOG_TO_SPECIES map** — idx 0=oak, 1=spruce, 2=birch, 3=jungle, 4=acacia, 5=dark_oak, 6=mangrove, 7=cherry, 8=crimson, 9=warped
- **Current behavior (v2.7.1):**
  - `findConnectedTree(speciesIdx)` — standard 26-adjacency BFS for 9 species. **Acacia (speciesIdx=4) gets a second expanded pass** traversing up to 2 air/leaf blocks between log chunks (handles L-shape branching).
  - `pickFallYaw()` — AWAY_WEIGHT=5.0, TOWARD_PLAYER_VETO=-0.3, picks away from chopper preferring downhill, penalizes obstacles
  - `computeFallAngle(drop) = clamp(-90 - drop*4, -135, -80)`
  - `applyImpactEffects()` — 5♥ damage to ALL players in corridor (chopper NOT exempt per user directive), camerashake 0.9/0.8 positional, perpendicular knockback
  - `smashVegetationAlongFall()` — 43-token allowlist for small veg (grass, flowers, mushrooms, saplings, bamboo, sugar_cane, crops, dead_bush, azalea, pink_petals, dripleaf, vines, nether wart/roots). Explicitly EXCLUDES `_leaves`/`_log`/`_stem`/`_wood`/`_hyphae`/`grass_block` — won't destroy trees.
  - Impact particles UNDER trunk at `stump.y - 0.05` (user-fixed in v2.7.0)
  - Entity pinned every tick to prevent post-rest "scoot"

### 3. PatrixCanopyGen v0.1.1 CANOPYFIX
- **File:** `PatrixCanopyGen-v0_1_1.mcaddon` (12 KB) — single BP.mcpack inside
- **UUIDs LOCKED:** BP header `5923a10b-6552-48a0-9528-d3a33fcf2bdf`, BP data `bca67360-d523-4155-b802-d2bd264fd93b`, `min_engine_version [1,20,20]`
- **8 species covered (shipped):** oak, birch, spruce, cherry, fancy_oak, mangrove, savanna (acacia), roofed (dark_oak)
- **Jungle NOT yet covered** — pending as v0.1.2 JUNGLE
- **Schema notes (corrections from handoff v1):**
  - Dark oak filename is `roofed_tree_feature.json` with identifier `minecraft:roofed_tree_feature` (NOT `dark_oak_tree_feature`)
  - Acacia filename is `savanna_tree_feature.json` with identifier `minecraft:savanna_tree_feature`
  - Vanilla feature JSONs use JSONC with `//` comments — preserve them
- **Per-species feature schemas:**
  - oak/birch: `trunk` + `canopy` with `canopy_offset{min,max}`, `variation_chance[]`
  - spruce: `trunk` + `spruce_canopy` with `lower_offset`/`upper_offset`/`max_radius`
  - cherry: `cherry_trunk` + `cherry_canopy` with `height`, `radius`, `wide_bottom_layer_hole_chance`, `corner_hole_chance`
  - fancy_oak: `fancy_trunk` + `fancy_canopy` with `height`, `radius`
  - mangrove: `mangrove_roots` + `mangrove_trunk` + `mangrove_canopy`
  - savanna (acacia): `acacia_trunk` + `acacia_canopy` with `canopy_size`
  - roofed (dark_oak): `acacia_trunk` + `roofed_canopy` with `core_width`/`outer_radius`/`inner_radius`
- **MUST preserve from originals:** `may_grow_on`, `may_replace`, `may_grow_through` arrays

---

## VERSION HISTORY

### Sampler
| Version | Tag | Summary |
|---|---|---|
| v0.1.0 | initial | 69 blocks, validate pipeline |
| v0.1.5 | LEAFFIX | `dilate_alpha_fill_rgb` for grass/leaves opacity |
| v0.1.6 | LESSDENSE | iterations=1 dilation, 48–64% leaf opacity |
| v0.1.7 | DESERTPORT | desert family |
| v0.1.8 | WATERPORT | sandstone family, sugar cane, carrots, seagrass, fire coral |
| v0.1.9 | MYCOPORT | mushroom blocks, mud family, muddy_mangrove_roots, dirt_path (accidentally introduced phantom `minecraft:dirt_path` block ID) |
| v0.2.0 | VARIATION | First 8-variant attempt (broken per MCPE-165946 research) |
| v0.2.1 | SMOOTH | 16 median-filtered variants, sandstone_top variants, lava flipbook |
| v0.2.2 | VARFIX | **Mistake** — reverted variations to singles based on research saying they don't work. User later contradicted: variations WERE visibly rendering. Also added 70+ new block ports |
| v0.2.3 | BARKFIX | Fixed blocks.json format_version (was wrongly 1.21.120), fixed grass_block_side missing-shortname purple checker, fixed muddy_mangrove_roots incomplete-texture-list warning, added podzol, ported log/plank/leaves for all 10 species. **Regression: raw Patrix leaves at 27% opacity shipped → sparse canopies** |
| v0.2.4 | DENSE+VARS | Restored 16-variant arrays (trusting user observation over MCPE-165946). Dilated leaves to ~50% opacity target |
| v0.2.5 | DRIPBARK | 16 grass_block_side composite variants (dirt portion varies), 8 dripstone_block variants, 8 pointed_dripstone shape textures, 160 bark variants |

### BIGCANOPY
| Version | Tag | Summary |
|---|---|---|
| v2.4.1→v2.6.2 | CANOPYFIX | Small canopy reshaped conic-downward, 4 canopy size tiers, strict isFallCollider, collision sweep during fall |
| v2.7.0 | NODAMAGE | Chopper NOT exempt from damage, camerashake, knockback, impact particles UNDER trunk, 43-token small-veg smasher, away-from-chopper yaw weight 5.0 |
| v2.7.1 | ACACIA | `findConnectedTree` gets speciesIdx-aware bridging pass for acacia — up to 2 air/leaf blocks between log chunks |

### PatrixCanopyGen
| Version | Tag | Summary |
|---|---|---|
| v0.1.0 | LARGEGEN | 8 tree overrides, had bugs (oak/birch offset pushed 5th layer to trunk base on short trunks; spruce lower_offset 2-4 caused mid-trunk canopy) |
| v0.1.1 | CANOPYFIX | oak/birch offset `-3..+1` (5th layer above trunk top), spruce lower_offset reverted to vanilla 1-3 |

---

## CRITICAL RESEARCH FINDINGS (memorize — don't re-research)

### MCPE-165946 — partial truth
- Bug report (open since 2023): "Variations in terrain_texture.json only load first or last texture"
- Microsoft docs: variations require 1.21.110+ experimental + custom blocks with `material_instances`
- Better Foliage (2.2M downloads) uses ZERO variations arrays
- **BUT user's in-game testing of v0.2.1 + v0.2.4 confirmed variations on plain vanilla blocks (dirt, stone, sand, gravel) ARE visibly rendering multiple distinct tiles.** Research was wrong for user's platform.
- What still doesn't work reliably: `grass_block_top` variation (user confirmed this one works somehow, leave alone). Real issue was `grass_block_side` — dirt portion repeated. Fixed in v0.2.5 with 16 composite variants.
- **Practical stance:** trust user visual observation over research doc claims. Variations first; fall back to synthesis or custom-block path only if user reports no variation visible.

### blocks.json format_version MUST be 1.1.0
- NOT 1.21.x — that's for custom block JSON files (`behaviors/blocks/*.json`), a different format
- Bedrock silently downgrades out-of-range format_version to 1.1.0 but some entries don't fully parse → mystery "Invalid or incomplete texture list" warnings
- When in doubt: 1.1.0

### grass_block_side is an OVERLAY block in Bedrock
- Patrix `grass_block_side.png` has grass transition baked into top ~20 rows (of 64)
- Patrix also ships `grass_block_side_overlay.png` — biome-tinted green strip
- Bedrock composites overlay on top of base → changes to dirt portion work independently
- `grass_side` is legacy shortname; modern blocks.json references `grass_block_side`. Alias both.

### Patrix CTM tile library (where authored variants live)
Path: `/home/claude/patrix_ref/basic/assets/minecraft/optifine/ctm/patrix/`

| Material | Subpath | Tiles |
|---|---|---|
| stone | `stone/` | 16 |
| andesite/granite/diorite | `{name}/` | 19 each |
| dirt | `dirt/default/` | 36 |
| coarse_dirt | `dirt/coarse/` | 36 |
| podzol | `dirt/podzol/` | exists |
| farmland | `dirt/farmland/{dry,wet}/` | exists |
| sand | `sand/yellow/` | 36 (212 in full tree) |
| red_sand | `sand/red/` | 36 |
| gravel | `gravel/` | 76 |
| grass top | `grass/block/top/` | 16 |
| grass side | `grass/block/side_default/`, `side_overlay/`, `side_snow/` | ~34 each |
| mycelium top/side | `mycelium/{top,side}/` | 16/35 |
| cobblestone | `cobblestone/default/` | 9 |
| cobblestone mossy | `cobblestone/mossy/` | exists |
| deepslate | `deepslate/stone/` | 16 |
| end_stone | `end/stone/stone/` | 16 |
| netherrack | `nether/rack/` | 16 |
| mud | `mud/wet/` | 36 |
| packed_mud | `mud/packed/` | 16 |
| mud_bricks | `mud/brick/` | 16 |
| muddy mangrove roots | `mangrove/roots/{side,top}/muddy/` | 32/16 |
| sandstone tops | `sandstone/{yellow,red}/top/` | 16 each |
| blackstone | `blackstone/stone/` | 16 |
| dripstone | `dripstone/` | 16 |
| glowstone | `glowstone/` | 16 |
| prismarine | `prismarine/stone/` | exists |

### Patrix has PBR _n + _s maps but we haven't shipped them
- `/home/claude/patrix_ref/basic/assets/minecraft/textures/block/*_n.png` + `*_s.png`
- Vibrant Visuals on PS5 engages these automatically
- Deferred to VV tuning phase — not in any sampler build yet

### Entity vs block lighting mismatch (bark color)
- Minecraft blocks get face-directional shading: UP ~100%, sides 60–80%, DOWN ~50%
- Entities get flat ambient lighting, no face-shading
- Same Patrix oak_log pixels (avg RGB 107,86,56) render:
  - Block side face: ~65–86 per channel (darker)
  - Entity: ~107 per channel (lighter)
- User accepted Option C — wait for VV to unify lighting, no compensation now

### Patrix pointed_dripstone doesn't exist as PNGs
- Patrix basic only has `dripstone_block.png`
- Patrix Java uses JSON models that UV-slice dripstone_block onto pointed shapes
- Bedrock needs dedicated `pointed_dripstone_*` PNGs per shape
- v0.2.5 generated 8 shapes (base/middle/frustum/tip × up/down) from Patrix color + tapered silhouette masks. Test in-game before assuming they look right.

### Small mushroom shortname aliases
- Register BOTH `mushroom_red`/`mushroom_brown` (legacy) AND `red_mushroom`/`brown_mushroom` (modern) pointing to same PNG. Already done.

### Patrix stone.png is a placeholder
- Base `textures/block/stone.png` in Patrix is an "ENABLE CONNECT TEXTURE" OptiFine placeholder, NOT a real stone texture
- Real Patrix stone lives inside `optifine/ctm/patrix/stone/` (16 authored tiles)
- If you ever see stone looking wrong, suspect this

### Legacy shortname aliases for wood
- Register both legacy (log_oak, log_big_oak, planks_big_oak, leaves_jungle etc.) AND modern (oak_log, dark_oak_log, dark_oak_planks, jungle_leaves) pointing to same PNGs
- dark_oak is "big_oak" in legacy filenames
- Already handled in v0.2.3+

---

## WORKSPACE LAYOUT (after re-extraction)

```
/home/claude/patrix_ref/basic/                    # Patrix_1.21.11_64x_basic.zip
  assets/minecraft/textures/block/                # ~3056 PNGs + _n/_s PBR + extra/
  assets/minecraft/optifine/ctm/patrix/           # MASSIVE CTM library (see table above)
  assets/minecraft/blockstates/                   # Java blockstate JSONs (reference)
  assets/minecraft/models/block/                  # Java model JSONs (reference)

/home/claude/patrix_ref/addon/                    # optional
/home/claude/patrix_ref/bonus/                    # optional

/home/claude/patrix_world_pack/                   # extract PATRIX-WORLD-SAMPLE-v0_2_5.mcpack
  manifest.json                                    # format_version 2, version [0,2,5]
  blocks.json                                      # format_version 1.1.0 (DON'T BUMP)
  pack_icon.png
  textures/
    terrain_texture.json                           # 255 shortnames, 59 variations
    flipbook_textures.json                         # lava still+flow
    blocks/*.png                                   # 847 PNGs

/home/claude/bigcanopy/extracted/                 # extract BIGCANOPY-v2_7_1.mcaddon (zip of zips)
  BP/
    manifest.json                                  # v[2,7,1]
    scripts/main.js                                # 1031 lines
  RP/
    manifest.json
    entity/falling_tree.json
    models/entity/falling_tree.geo.json
    animations/falling_tree.animation.json
    render_controllers/falling_tree.json
    animation_controllers/falling_tree.json
    textures/entity/fallingtree/*.png              # 10 species × 128×128 atlases

/home/claude/patrixcanopygen/                     # extract PatrixCanopyGen-v0_1_1.mcaddon
  manifest.json                                    # v[0,1,1]
  pack_icon.png
  features/
    oak_tree_feature.json
    birch_tree_feature.json
    spruce_tree_feature.json
    cherry_tree_feature.json
    fancy_oak_tree_feature.json
    mangrove_tree_feature.json
    savanna_tree_feature.json                      # acacia
    roofed_tree_feature.json                       # dark_oak
  # JUNGLE NOT YET ADDED

/home/claude/bds/                                 # extract bedrock-server-1.26.14.1.zip
  behavior_packs/vanilla_1.21.40/features/        # vanilla tree-feature JSONC files (authoritative source for overrides)
```

---

## PENDING BACKLOG (prioritized)

### Highest priority — user has explicitly flagged

1. **Acacia entity geometry rework** (requires the acacia screenshot)
   - v2.7.1 fixed DETECTION via leaf-bridging BFS. May have solved the problem, may not. **Validate first in-game.**
   - Animation + entity GEOMETRY still straight-trunk. Acacia's L-shape branching should fall/rest differently (sideways drop of the branch portion).
   - Needs: new geometry variant (e.g., `geometry.ft_falling_tree.acacia`), new animation state for kinked L-shape fall, possibly a branched entity model
   - Substantial work — its own iteration plan

2. **PatrixCanopyGen v0.1.2 JUNGLE**
   - Add jungle_tree_feature.json override using BDS source schema
   - Enlarge canopy radius/height/add layers
   - Preserve `may_grow_on`/`may_replace`/`may_grow_through`
   - Straightforward — smallest iteration available

3. **Tectonic worldbuilding groundwork (Phase 5)**
   - User flagged block-variance refinement to happen WITH worldbuilding
   - Start: custom biome JSONs, surface_builder definitions, replace_biomes mappings, 10-biome roster
   - Plan in detail BEFORE writing biomes

### Medium priority — BIGCANOPY 14-item backlog (items NOT yet addressed)

| # | Item | Notes |
|---|---|---|
| 1 | Canopy shape matches actual tree (dynamic sizing tied to log count) | Big refactor — entity canopy is species-only currently |
| 2 | 3–5 sizes per species dynamically | Tied to #1 |
| 8 | Decelerating tail animation (wind resistance) | Tune FALL_KEYS tail 0.956→1.0 to 1.05→1.0→0.92 ease-out |
| 9 | Giant mushroom felling (new species for red/brown_mushroom_block + mushroom_stem) | |
| 11 | 2×2 trunk entity geometry for mega jungle + dark_oak | User noted single-line trunk for wider trees |
| 13 | Slope-aware rest angle (lie flat with terrain) | Previously shelved, user un-shelved |

### Sampler texture expansion
- Stripped logs for all 10 species (not yet ported)
- Wood (6-face log) variants
- Beds, banners, concrete colors, concrete_powder, wool colors, glazed terracotta ×16, candles, sculk family, froglights, chiseled variants, stairs/slabs (if different from base)
- Patrix addon pack: stained glass ×16, cake variants, moss_carpet_extra, seagrass_extra
- Patrix bonus pack: foodcrate, tudor blocks

### Lower priority / deferred
- Vibrant Visuals tuning pack (Phase 2) — unblocked by PS5 access
- Finite fluids (Phase 4) — big scripting project
- Full Patrix port (Phase 1) — 30k files, after sampler validates
- Phase 6 polish — subpack tiers, CI versioning, frame profiling

---

## PACKAGING CONVENTIONS

### Sampler — single `.mcpack`
```bash
cd /home/claude/patrix_world_pack
zip -qr /mnt/user-data/outputs/PATRIX-WORLD-SAMPLE-v0_X_Y.mcpack \
  manifest.json blocks.json pack_icon.png textures/
```

### BIGCANOPY — `.mcaddon` with nested BP + RP mcpacks
```bash
cd /home/claude/bigcanopy/extracted
cd BP && zip -qr /tmp/bigcanopy_bp.mcpack . && cd ..
cd RP && zip -qr /tmp/bigcanopy_rp.mcpack . && cd ..
(cd /tmp && zip -qj BIGCANOPY-v2_X_Y.mcaddon bigcanopy_bp.mcpack bigcanopy_rp.mcpack)
cp /tmp/BIGCANOPY-v2_X_Y.mcaddon /mnt/user-data/outputs/
```

### PatrixCanopyGen — `.mcaddon` with single BP
```bash
cd /home/claude/patrixcanopygen
zip -qr /tmp/canopygen_bp.mcpack manifest.json pack_icon.png features/
(cd /tmp && zip -qj PatrixCanopyGen-v0_X_Y.mcaddon canopygen_bp.mcpack)
cp /tmp/PatrixCanopyGen-v0_X_Y.mcaddon /mnt/user-data/outputs/
```

### Every deliverable
- Validate JSON: `python3 -c "import json; json.load(open('path'))"` on every .json
- Delete superseded version from `/mnt/user-data/outputs/` (avoid user confusion)
- Call `present_files` with all 3 current deliverables
- Mention what to test in-game
- Note what was INTENTIONALLY deferred so user knows it wasn't forgotten

---

## USER CONVENTIONS & TONE

- **Concrete, direct, results-first.** User tests on real hardware (mobile + eventually PS5), sends video frames or screenshots.
- **Believe user observation over research docs** until proven otherwise. They called out MCPE-165946 research as wrong for their platform — own it, don't defend.
- **Scale back when uncertain.** Propose ambitious approach, note it may fail, ship fallback if it does.
- **Every deliverable needs distinctive tag** in manifest display name.
- **Shelved items** — don't touch unless user reopens:
  - Entity foliage color/density mismatch vs standing leaves (SHELVED, wait for VV)
  - Entity bark color mismatch vs standing trunks (SHELVED, wait for VV — Option C)
  - Now in backlog: falling-entity size mismatch vs tree (item #1), slope-based resting roll (item #13, un-shelved)
- **In-progress**: Phase 1 full-pack bulk texture port (incremental)

---

## FIRST RESPONSE TEMPLATE

> Resuming PatrixWorld. Before I do anything, I need:
>
> **Uploads:**
> - `Patrix_1.21.11_64x_basic.zip` (~198MB, primary source)
> - `PATRIX-WORLD-SAMPLE-v0_2_5.mcpack` (current sampler)
> - `BIGCANOPY-v2_7_1.mcaddon` (current falling-tree)
> - `PatrixCanopyGen-v0_1_1.mcaddon` (current canopy-gen)
> - `bedrock-server-1.26.14.1.zip` (vanilla tree schemas)
> - The acacia-didn't-fall screenshot you saved
>
> **Nice to have:**
> - `Patrix_1.21.11_64x_addon.zip` (stained glass, cake)
> - `Patrix_1.21.11_64x_bonus.zip` (foodcrate, tudor)
>
> Once extracted, I'll verify UUIDs match the handoff. Then per the process rule, I'll outline a plan before building anything. What's the target for this session — acacia geometry rework, jungle canopy, or something else from the backlog?

Keep it tight. Do not restate the handoff.
