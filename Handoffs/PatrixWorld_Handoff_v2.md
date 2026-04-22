# PatrixWorld + BIGCANOPY + PatrixCanopyGen — Full Project Handoff (v2)

Resuming a Minecraft Bedrock 1.26.x modding project. Previous chat hit context limit. This document is authoritative — it supersedes the v1 handoff. Read it fully before responding.

---

## TURN 1 — WHAT TO DO FIRST

1. Acknowledge this handoff briefly. Do NOT restate it.
2. **Ask the user to upload the files listed in the UPLOADS REQUEST section below.** These must be re-uploaded because prior session files rolled off disk.
3. Wait for uploads and the specific **acacia-didn't-fall screenshot** before starting any work.
4. **Follow the NEW PROCESS RULE:** ask clarifying questions BEFORE every build. Outline what you'll change, what tradeoffs exist, what you're leaving alone — wait for the user's green light. No "fire and check" iterations.

---

## NEW PROCESS RULE (critical, added mid-project)

The user added this rule explicitly: **no builds without a plan-first discussion.** Every iteration starts with:

1. Outline what you intend to change
2. Note tradeoffs / what stays as-is
3. Wait for green light (or additional direction)
4. Then build

This catches wrong assumptions early. Do not skip it. The user will tell you "yes" or add constraints, then you build.

Investigation/diagnostic work (reading files, computing pixel averages, comparing hashes) is fine without asking — just don't write output files or bump manifests until you've confirmed the plan.

---

## UPLOADS REQUEST

At start of chat, ask the user to upload these. Be concise (abbreviated list, not full explanation):

### Critical — blocks everything
1. **`Patrix_1.21.11_64x_basic.zip`** (~198 MB) — primary Patrix Java source. Contains 3056 block PNGs at 64×64 + the OptiFine CTM tile library we rely on heavily for block variants.
2. **`PATRIX-WORLD-SAMPLE-v0_2_5.mcpack`** — current shipped sampler (our last build). Your starting point for sampler iteration.
3. **`BIGCANOPY-v2_7_1.mcaddon`** — current shipped tree-falling addon. Your starting point for BIGCANOPY iteration.
4. **`PatrixCanopyGen-v0_1_1.mcaddon`** — current shipped worldgen tree-size override.
5. **`bedrock-server-1.26.14.1.zip`** (~57 MB) — Bedrock Dedicated Server. Its `behavior_packs/vanilla_1.21.40/features/` folder contains authoritative vanilla tree-feature JSONs needed for PatrixCanopyGen iteration.
6. **The acacia screenshot** — user has a specific screenshot showing an acacia tree they chopped that did NOT fall. Critical reference for the acacia geometry/detection rework that's pending.

### Probably needed for next phases
7. **`Patrix_1.21.11_64x_addon.zip`** (~42 MB) — stained glass (all 16 colors), cake variants, moss_carpet_extra, seagrass_extra.
8. **`Patrix_1.21.11_64x_bonus.zip`** (~10 MB) — foodcrate.png, tudor1/2.png, misc niche textures.

### Reference material — DO NOT request
The user has uploaded these previously; reference content has been extracted. Don't ask again:
- physics-mod-pro (all variants), continuity, tectonic, distanthorizons
- flowing_fluids, fluidphysics, wpo, Realistic_Fluids JARs
- FallingTree-26_1_2-25.jar, SMARTFALL-v2_4_0.mcaddon
- BFBP1.5.mcpack + BFRP1.5.mcpack (Better Foliage; inspection done)
- RealSource_VibrantVisuals_PLUS_2.0.zip (future VV tuning reference)
- Smooth_Plant_Animations, Waving-Plants-Shaders-Mod, Alacrity, GlowingOres-RealisticRTXpack, LOW_RealisticJAVApack

---

## PROJECT SCOPE — THE FOUR DOMAINS (original research)

### Domain 1 — Java → Bedrock texture pack port, Patrix case
Manifest authoring, terrain_texture.json / item_texture.json / flipbook_textures.json assembly, LabPBR 1.3 → Bedrock MERS channel conversion, DirectX vs OpenGL normal map convention, OptiFine CTM → Bedrock approximations, biome-tinted foliage handling, sound definition translation, .mcpack/.mcaddon packaging, Realms deployment.

### Domain 2 — Emulating Java shaders (Complementary / BSL / SEUS) via Vibrant Visuals
Full JSON authoring: `lighting/global.json`, `atmospherics/*.json`, `color_grading/*.json`, `water/water.json`, `fogs/*.json`, `shadows/global.json`, `local_lighting/local_lighting.json`, `cubemaps/*.json`. What Bedrock VV can do (PBR, real-time shadows, SSR, volumetric fog, atmospheric scattering, bloom, tone mapping, color grading, subsurface scattering, water waves/caustics, colored point lights). What it can't (SSGI, path tracing on PS5, custom GLSL, DOF, LUT import, cascaded shadow maps). PS5 60 FPS performance envelope.

### Domain 3 — Emulating Java fluid physics mods
Research of Haubna Physics Mod, flowing_fluids, wpo, Realistic Fluids. Design for a custom `ff:water_finite` block with 8 level permutations, Bedrock Scripting V2 tick loop (`minecraft:tick[10,14]` callbacks), pool-isolation graph via runJob generators, drain-when-cut-from-source logic. Ocean waves via VV image displacement. Swim visuals (splash, ripples, wake). Realms budget: ~3000–6000 simulated water blocks on PS5. Haubna scope limited to FLUIDS only (debris/cloth/ragdoll deferred indefinitely).

### Domain 4 — Tectonic-inspired worldgen in Bedrock
Custom biome JSONs with `minecraft:climate`, `minecraft:surface_builder`, `minecraft:surface_material_adjustments`, `minecraft:mountain_parameters`, `minecraft:replace_biomes`. 10-biome "Tectonic-Bedrock" roster: alpine_peak, alpine_meadow, coastal_bluff, river_canyon, badlands_mesa, boreal_forest, pale_hills, cherry_valley, desert_dunes, icy_cliffs. Custom features (twisted-pine trees, rock outcrops, wildflowers). Hard ceilings acknowledged: no custom dimensions, no 6D multinoise for custom biomes, no data-driven density functions. Tectonic-Bedrock is a biome reskin + decoration layer on vanilla terrain shape.

### SIX-PHASE ROADMAP (original plan, we've diverged)
| Phase | Scope | Status |
|---|---|---|
| 1 | Patrix base port | **In progress** — sampler at v0.2.5, ~234+ shortnames, ~850 PNGs. Not yet at full-pack level but well past the minimal-sampler validation |
| 2 | Vibrant Visuals tuning | Unstarted (paused until PS5 access) |
| 3 | FallingTree port | **Shipped** as BIGCANOPY v2.7.1 ACACIA |
| 4 | Finite fluids v1 | Unstarted (research done, zero code) |
| 5 | Tectonic-Bedrock worldgen | Unstarted (research done, zero code) |
| 6 | Polish (subpacks, CI, profiling) | Unstarted |

### ADDITIONAL SCOPES added mid-project (not in original plan)
- **PatrixCanopyGen** (NEW): behavior pack overriding vanilla tree-feature JSONs to produce larger standing canopies. Shipped at v0.1.1 CANOPYFIX, 8 species overrides. Jungle override still pending as v0.1.2.
- **Animated Patrix lava** (flipbook): 8-frame `lava_still` + 48-frame `lava_flow` with blend_frames. Ported in v0.2.1.
- **Composite pointed_dripstone shapes**: generated from-scratch Patrix-colored tapered silhouettes for 8 shape variants (base/middle/frustum/tip × up/down), replacing vanilla low-res stalactites. Added in v0.2.5.
- **Bark variance per species**: 8 rotation-synthesized variants per log side + end-grain for all 10 species. Added in v0.2.5.
- **grass_block_side dirt-portion variants**: 16 composite variants preserving Patrix grass strip, swapping dirt portion with 16 different Patrix dirt CTM tiles. Added in v0.2.5.

---

## STRATEGIC DECISIONS BAKED IN

- **PS5 primary, Android fallback.** Realms delivery.
- **"Aim for perfection, scale back to what works"** — always try the most ambitious approach first; document the floor and ship fallback when needed rather than lowering the ceiling.
- **Vibrant Visuals + Experimental Voxel Shapes stay on throughout.**
- **Custom biomes** will enable in Phase 5 (achievements disabled for world; explicit trade).
- **Naming discipline:** every build gets a unique manifest tag `[TAG vX.Y.Z]` so the user can verify in-game which version loaded.
- **Block variance for world-gen blocks** (stone/dirt/etc.) is DEFERRED to Phase 5 / tectonic work. Don't pour effort into this area until worldbuilding control lands.
- **Bark color mismatch on BIGCANOPY falling entity** is DEFERRED — waiting for Vibrant Visuals on PS5 to unify entity/block lighting. Option C chosen (no compensation now).

---

## WHAT'S SHIPPED — CURRENT STATE

### 1. PatrixWorld Sampler v0.2.5 DRIPBARK
- **File:** `PATRIX-WORLD-SAMPLE-v0_2_5.mcpack` (~5.8 MB)
- **Stats:** ~850 PNGs, 255 shortnames, 59 variations arrays, 67 blocks.json entries
- **Key features:**
  - 23 surface blocks with 16 authored Patrix CTM tile variants (stone, andesite, granite, diorite, dirt, coarse_dirt, sand, red_sand, gravel, grass_block_top, mycelium_top/side, cobblestone, deepslate, end_stone, netherrack, mud, packed_mud, mud_bricks, muddy_mangrove_roots_top/side, sandstone_top, red_sandstone_top)
  - 16 `grass_block_side` composite variants (grass strip preserved, dirt portion varies)
  - 8 `dripstone_block` rotation-synthesized variants
  - 8 `pointed_dripstone_*` shape textures (fresh Patrix-colored silhouettes)
  - 160 bark variant PNGs (10 species × 2 faces × 8 variants)
  - Patrix lava flipbook (still 8 frames @ 4 ticks + flow 48 frames @ 1 tick, blend_frames)
  - Foliage dilation applied to 8 leaf species at ~50% opacity target (was 27–41% raw Patrix)
  - Patrix log/plank textures for all 10 wood species
  - 70+ non-variant block ports: terracotta ×16, deepslate family ×5, copper oxidation ×4, all 17 ores, amethyst, ice family, purpur, basalt/blackstone family, soul sand/soil, glowstone/shroomlight, nether wart blocks, moss, clay, snow, bone_block
- **UUIDs (LOCKED):** header `7b5e9f01-3a24-4b6c-9d17-8e5f4c2b19a0`, resources module `f2c8d9e4-6a51-4f8b-a3c9-1d8e7b4f5c62`, `min_engine_version [1,26,0]`
- **blocks.json format_version:** `1.1.0` (do NOT bump to 1.21.x — earlier session did this mistakenly and caused silent parse fallback)
- **Tag pattern:** `[TAG vX.Y.Z]` in manifest display name

### 2. BIGCANOPY v2.7.1 ACACIA
- **File:** `BIGCANOPY-v2_7_1.mcaddon` (~292 KB)
- **Contains:** BP.mcpack + RP.mcpack nested
- **Script:** `/BP/scripts/main.js` (~1000 lines)
- **Key features:**
  - 4 canopy geometry variants: small (5×4×5 conic-down, spruce/crimson/warped), medium (5×4×5 pancake, oak/birch/acacia), large (7×4×7, jungle/dark_oak/mangrove), huge (11×4×11, cherry)
  - 10 species with LOG_TO_SPECIES map
  - Animation: 7-keyframe fall (0.35s→0.9s→1.4s→1.65s overshoot→1.72s bounce→1.8s terminal)
  - `computeFallAngle(drop) = clamp(-90 - drop*4, -135, -80)`
  - `pickFallYaw()` with `AWAY_WEIGHT=5.0`, `TOWARD_PLAYER_VETO=-0.3` — picks direction away from chopper, considers downhill, counts obstacles
  - `applyImpactEffects()` — 5♥ damage to ALL players in corridor (chopper NOT exempt per user directive), camerashake 0.9/0.8 positional, knockback perpendicular
  - `smashVegetationAlongFall()` — 43-token allowlist: grass, flowers, mushrooms, saplings, bamboo, sugar_cane, wheat/carrots/potatoes/beetroots, pumpkin/melon stems, dead_bush, azalea, pink_petals, dripleaf, vines, crimson/warped_roots, nether_sprouts/wart. Explicitly excludes `_leaves`, `_log`, `_stem`, `_wood`, `_hyphae`, `grass_block` (won't destroy other trees).
  - Impact particles UNDER trunk at `stump.y - 0.05` (v2.7.0 fix)
  - `findConnectedTree(speciesIdx)` — standard 26-neighbor BFS for 9 species; **acacia (speciesIdx=4) gets a second expanded pass** that traverses up to 2 air/leaf blocks between log chunks (v2.7.1)
- **UUIDs (LOCKED):** BP header `be7227ad-138a-45a5-9e38-4c2cf4732440`, BP data `a8b6523b-c9ac-4a1b-8586-aea316833b4b`, BP script `6fed24a7-f6c9-47ef-90ec-6b0b20d5ca0c`, RP header `4410d782-8723-40e3-9586-8262cbb9a1f8`, RP resources `95f4efcf-0333-4373-b470-eea36df91034`
- **Script dependency:** `@minecraft/server` v2.0.0
- **Entity atlas layout (CRITICAL, we regressed once):** 128×128 atlas with 64×64 regions. Bark sides all UV `[0,64], uv_size [64,64]`. Up face `[0,0]`, down face `[64,0]`. NEVER use 16×16 UV.
- **Animation molang multipliers:** 0.044 / 0.333 / 0.867 / 1.033 / 0.956 / 1.0 at times 0.35 / 0.9 / 1.4 / 1.65 / 1.72 / 1.8. DO NOT touch these.

### 3. PatrixCanopyGen v0.1.1 CANOPYFIX
- **File:** `PatrixCanopyGen-v0_1_1.mcaddon` (~12 KB)
- **Contains:** single BP.mcpack with `features/` directory
- **Covers 8 species** — oak, birch, spruce, cherry, fancy_oak, mangrove, savanna/acacia, roofed/dark_oak
- **Schema notes (corrections from original handoff):**
  - Dark oak filename is `roofed_tree_feature.json` with identifier `minecraft:roofed_tree_feature` (NOT `dark_oak_tree_feature`)
  - Acacia filename is `savanna_tree_feature.json` with identifier `minecraft:savanna_tree_feature`
  - Vanilla feature JSONs use JSONC with `//` line comments — preserve them
- **Schemas per species:**
  - oak/birch: `trunk` + `canopy` with `canopy_offset{min,max}`, `variation_chance[]`
  - spruce: `trunk` + `spruce_canopy` with `lower_offset` / `upper_offset` / `max_radius`
  - cherry: `cherry_trunk` + `cherry_canopy` with `height`, `radius`, `wide_bottom_layer_hole_chance`, `corner_hole_chance`
  - fancy_oak: `fancy_trunk` + `fancy_canopy`
  - mangrove: `mangrove_roots` + `mangrove_trunk` + `mangrove_canopy`
  - savanna/acacia: `acacia_trunk` + `acacia_canopy` with `canopy_size`
  - roofed/dark_oak: `acacia_trunk` + `roofed_canopy` with `core_width` / `outer_radius` / `inner_radius`
- **Preserve from originals:** `may_grow_on`, `may_replace`, `may_grow_through` arrays (MUST preserve)
- **Jungle NOT yet covered.** Pending as v0.1.2 JUNGLE.
- **UUIDs (LOCKED):** BP header `5923a10b-6552-48a0-9528-d3a33fcf2bdf`, BP data `bca67360-d523-4155-b802-d2bd264fd93b`, `min_engine_version [1,20,20]`

---

## VERSION HISTORY (comprehensive, every iteration)

### Sampler
| Version | Tag | Summary |
|---|---|---|
| v0.1.0 | initial | 69 blocks, validate pipeline |
| v0.1.5 | LEAFFIX | `dilate_alpha_fill_rgb` algorithm on grass/leaves |
| v0.1.6 | LESSDENSE | iterations=1 on dilation, 48–64% leaf opacity |
| v0.1.7 | DESERTPORT | desert biome blocks |
| v0.1.8 | WATERPORT | sandstone family, sugar cane, carrots, seagrass, fire coral |
| v0.1.9 | MYCOPORT | giant mushroom blocks, mud family, muddy_mangrove_roots, dirt_path (accidentally added phantom `minecraft:dirt_path` block ID — fixed in v0.2.1) |
| v0.2.0 | VARIATION | 8-variant system attempted for 21 blocks (broken — MCPE-165946) |
| v0.2.1 | SMOOTH | Bumped to 16 median-filtered variants, added sandstone_top variants, added lava flipbook |
| v0.2.2 | VARFIX | Reverted variations to singles (research said bug made them nonfunctional). Added 70+ new blocks. **User later contradicted: variations WERE visibly rendering. Research incorrect for this platform.** |
| v0.2.3 | BARKFIX | Fixed blocks.json format_version (had been wrongly 1.21.120), fixed grass_block_side missing-shortname purple-checker issue, fixed muddy_mangrove_roots "incomplete texture list" warning, added podzol, ported log/plank/leaves for all 10 species (58 PNGs). **REGRESSION: raw Patrix leaves shipped at 27% opacity — canopies looked sparse.** |
| v0.2.4 | DENSE+VARS | Restored 16-variant arrays for 23 blocks (trusting user observation over MCPE-165946 research). Dilated leaves to ~50% opacity target. |
| v0.2.5 | DRIPBARK | 16 grass_block_side composite variants (dirt portion varies), 8 dripstone_block variants, 8 pointed_dripstone shape textures (Patrix-colored silhouettes), 160 bark variant PNGs (10 species × 2 faces × 8). |

### BIGCANOPY
| Version | Tag | Summary |
|---|---|---|
| v2.4.1→v2.6.2 | CANOPYFIX | Small canopy reshaped conic-downward, 4 canopy size tiers, strict isFallCollider, collision sweep during fall |
| v2.7.0 | NODAMAGE | Chopper NOT exempt from damage (all players in corridor take 5♥), camerashake, knockback, impact particles UNDER trunk (stump.y-0.05), 43-token small-veg smasher, away-from-chopper yaw weight 5.0, toward-player veto -0.3 |
| v2.7.1 | ACACIA | `findConnectedTree` extended with speciesIdx-aware bridging pass for acacia — traverses up to 2 air/leaf blocks between log chunks |

### PatrixCanopyGen
| Version | Tag | Summary |
|---|---|---|
| v0.1.0 | LARGEGEN | 8 tree overrides shipped then replaced (had oak/birch offset bug pushing 5th layer to trunk base on short trunks; spruce lower_offset 2-4 caused mid-trunk canopy) |
| v0.1.1 | CANOPYFIX | oak/birch offset `-3..+1` (5th layer above trunk top), spruce lower_offset reverted to vanilla 1-3 |

---

## CRITICAL RESEARCH FINDINGS (memorize; don't re-research)

### MCPE-165946 variations bug — PARTIAL TRUTH
- Bug report (open since 2023): "When adding texture variations with a resource pack via terrain_texture.json only the first or last texture loads."
- Microsoft docs: variations require 1.21.110+ experimental + custom blocks with `material_instances`.
- Fused Bolt Better Foliage (2.2M downloads) uses ZERO variations arrays.
- **HOWEVER: user's in-game testing of v0.2.1 + v0.2.4 confirmed that variations on plain vanilla blocks (dirt, stone, sand, gravel) ARE visibly rendering multiple distinct tiles** — at least on current Bedrock as of test date. Research was not fully correct for this platform.
- What still doesn't work reliably: grass_block_top variation. User observed this varied, then said the broader issue was grass_block_side (dirt portion under grass).
- Practical stance: **trust user visual observation over research doc claims**. Try variations first; fall back to synthesis/custom-block path only if user reports no variation visible.

### blocks.json format_version must be 1.1.0
- Not 1.21.x — that's for individual custom block JSON files (`behaviors/blocks/*.json`), a DIFFERENT file format
- Bedrock silently downgrades out-of-range format_version to 1.1.0 but some entries don't fully parse → mystery "Invalid or incomplete texture list" warnings
- When in doubt, leave it at 1.1.0

### grass_block_side is an OVERLAY block in Bedrock
- Patrix `grass_block_side.png` has grass transition BAKED into top ~20 rows (of 64)
- Patrix also ships `grass_block_side_overlay.png` (1007 of 4096 pixels opaque = top 25%) — the biome-tinted green strip
- Bedrock composites overlay on top of base, so changes to the dirt portion work independently
- `grass_side` is the legacy shortname; modern blocks.json references `grass_block_side`. Alias both in terrain_texture.json.

### Patrix CTM tile library — where authored variants live
`/home/claude/patrix_ref/basic/assets/minecraft/optifine/ctm/patrix/`:
| Material | Path | Tiles |
|---|---|---|
| stone | `stone/` | 16 |
| andesite/granite/diorite | `{name}/` | 19 each |
| dirt (default/coarse/podzol/farmland/path) | `dirt/{subtype}/` | 36 each |
| sand (yellow + red) | `sand/{yellow,red}/` | 36 each + separately 212 for full yellow set |
| gravel | `gravel/` | 76 |
| grass top | `grass/block/top/` | 16 |
| mycelium (top+side) | `mycelium/{top,side}/` | 16+35 |
| cobblestone (default + mossy) | `cobblestone/{default,mossy}/` | 9 each |
| deepslate | `deepslate/stone/` | 16 |
| end_stone | `end/stone/stone/` | 16 |
| netherrack | `nether/rack/` | 16 |
| mud family | `mud/{wet,packed,brick}/` | 36/16/16 |
| muddy mangrove roots | `mangrove/roots/{side,top}/muddy/` | 32/16 |
| sandstone (yellow+red) tops | `sandstone/{yellow,red}/top/` | 16 each |

### Patrix has OK `_n` normal + `_s` specular PBR maps but we haven't shipped them
- All surface blocks' PBR maps sit in `/home/claude/patrix_ref/basic/assets/minecraft/textures/block/*_n.png` + `*_s.png`
- Vibrant Visuals on PS5 will engage these automatically when shipped
- Currently not included in any sampler build — deferred to VV tuning phase

### Entity vs block lighting mismatch (bark color issue)
- Minecraft blocks get face-directional shading: UP 100%, sides 60–80%, DOWN 50%
- Entities get flat ambient lighting, no face-shading
- Same Patrix `oak_log` texture (avg RGB 107,86,56) renders:
  - Standing block side face: ~65–86 per channel (darker)
  - Falling entity: ~107 per channel (lighter)
- User accepted Option C: **wait for VV to unify lighting**, don't compensate texture now
- No fix planned until PS5 + VV testing begins

### Patrix pointed_dripstone doesn't exist as PNGs
- Patrix basic has only `dripstone_block.png` (+_n +_s)
- Patrix Java uses JSON models that UV-slice the dripstone_block texture onto pointed shapes
- Bedrock needs dedicated `pointed_dripstone_*` PNGs per shape
- **v0.2.5 generated 8 shape textures** (base/middle/frustum/tip × up/down) from Patrix dripstone color + tapered silhouette masks. Test these in-game before assuming they look right.

### Small mushroom shortname aliases needed
- Shortnames `mushroom_red` / `mushroom_brown` (legacy) and `red_mushroom` / `brown_mushroom` (modern) must both be registered pointing to same PNG — Bedrock's lookup path depends on which name the flora block internally uses
- Already done in v0.2.1+

---

## WORKSPACE DIRECTORY LAYOUT

After uploads, extract to these paths:

```
/home/claude/patrix_ref/basic/                    # Patrix_1.21.11_64x_basic.zip
  ├── assets/minecraft/textures/block/            # ~3056 flat block PNGs + _n/_s PBR
  ├── assets/minecraft/textures/block/extra/      # authored "_extra" variant PNGs
  ├── assets/minecraft/optifine/ctm/patrix/       # MASSIVE CTM tile library (see above)
  ├── assets/minecraft/blockstates/               # Java blockstate JSONs
  └── assets/minecraft/models/block/              # Java model JSONs

/home/claude/patrix_ref/addon/                    # Patrix_1.21.11_64x_addon.zip (if provided)
/home/claude/patrix_ref/bonus/                    # Patrix_1.21.11_64x_bonus.zip (if provided)

/home/claude/patrix_world_pack/                   # Extracted sampler v0.2.5
  ├── manifest.json
  ├── blocks.json                                  # format_version 1.1.0
  ├── pack_icon.png
  └── textures/
      ├── terrain_texture.json
      ├── flipbook_textures.json                   # lava animations
      └── blocks/*.png                              # ~850 PNGs

/home/claude/bigcanopy/extracted/                 # Extracted BIGCANOPY v2.7.1
  ├── BP/
  │   ├── manifest.json
  │   └── scripts/main.js                          # ~1000 lines, v2.7.1 ACACIA
  └── RP/
      ├── manifest.json
      ├── entity/falling_tree.json
      ├── models/entity/falling_tree.geo.json
      ├── animations/falling_tree.animation.json
      ├── render_controllers/falling_tree.json
      ├── animation_controllers/falling_tree.json
      └── textures/entity/fallingtree/*.png         # 10 species × 128×128 atlas

/home/claude/patrixcanopygen/                     # Extracted PatrixCanopyGen v0.1.1
  ├── manifest.json
  ├── pack_icon.png
  └── features/
      ├── oak_tree_feature.json
      ├── birch_tree_feature.json
      ├── spruce_tree_feature.json
      ├── cherry_tree_feature.json
      ├── fancy_oak_tree_feature.json
      ├── mangrove_tree_feature.json
      ├── savanna_tree_feature.json                # acacia
      └── roofed_tree_feature.json                 # dark_oak
  # Note: NO jungle_tree_feature.json yet

/home/claude/bds/                                 # Bedrock server zip
  └── behavior_packs/vanilla_1.21.40/features/     # authoritative tree-feature JSONs
```

---

## PENDING BACKLOG (prioritized)

### Highest priority — user has explicitly flagged

1. **Acacia entity geometry rework**
   - User provided a screenshot of an acacia that didn't fall (need to see this before anything else)
   - Current v2.7.1 fixed DETECTION via leaf-bridging BFS — that may have been enough, OR tree still fails. Validate first.
   - The animation + entity GEOMETRY are still straight-trunk. Acacia's L-shape branches should fall/rest differently (sideways drop of the branch portion).
   - Likely needs: new geometry variant (e.g., `geometry.ft_falling_tree.acacia`), new animation state for the kinked L-shape fall, possibly a branched entity model.
   - This is substantial work — should be its own iteration plan.

2. **PatrixCanopyGen v0.1.2 JUNGLE**
   - Add jungle_tree_feature.json override using BDS source schema
   - Enlarge canopy radius/height/add layers
   - Preserve `may_grow_on` / `may_replace` / `may_grow_through` arrays

3. **Tectonic worldbuilding groundwork**
   - User flagged block-variance refinement to happen WITH the worldbuilding domain
   - Start Phase 5 research: custom biome JSONs, surface_builder definitions, replace_biomes mappings, 10-biome roster
   - Don't start writing biomes until we plan the reskin approach in detail first

### Medium priority

4. **BIGCANOPY backlog items from 14-item list (not yet addressed)**
   | # | Item | Notes |
   |---|---|---|
   | 1 | Canopy shape matches actual tree (dynamic sizing tied to log count) | Big refactor — entity's canopy size is currently species-only, not tree-size |
   | 2 | 3-5 sizes per species dynamically | Tied to #1 |
   | 8 | Decelerating tail animation (wind resistance) | Tune FALL_KEYS tail from 0.956→1.0 to 1.05→1.0→0.92 ease-out |
   | 9 | Giant mushroom felling (new species for red/brown_mushroom_block + mushroom_stem) | |
   | 11 | 2×2 trunk entity geometry for mega jungle + dark_oak | User noted single-line trunk for wider trees |
   | 13 | Slope-aware rest angle (lie flat with terrain) | Previously shelved, user un-shelved |

5. **Sampler texture expansion**
   - Stripped logs for all species (not yet ported)
   - Wood (6-face log) variants
   - More block types: beds, banners, concrete, concrete_powder, wool colors, glazed terracotta colors, candles, sculk family, froglights, chiseled variants, stairs/slabs (if they differ from base)
   - Patrix addon pack contents: stained glass ×16, cake variants, moss_carpet_extra, seagrass_extra
   - Patrix bonus pack: foodcrate, tudor decorative blocks

### Low priority / deferred

6. **Vibrant Visuals tuning pack** (Phase 2) — unblocked by PS5 access
7. **Finite fluids Phase 4** — big scripting project
8. **Full Patrix port Phase 1** — 30k files, after sampler fully validated
9. **Phase 6 polish** — subpack tiers, CI versioning, frame profiling

---

## BUILD / PACKAGING CONVENTIONS

### Sampler
- Single `.mcpack`:
  ```bash
  cd /home/claude/patrix_world_pack
  zip -qr /mnt/user-data/outputs/PATRIX-WORLD-SAMPLE-v0_X_Y.mcpack manifest.json blocks.json pack_icon.png textures/
  ```

### BIGCANOPY — nested `.mcaddon` (zip of zips)
```bash
cd /home/claude/bigcanopy/extracted
cd BP && zip -qr /tmp/bigcanopy_bp.mcpack . && cd ..
cd RP && zip -qr /tmp/bigcanopy_rp.mcpack . && cd ..
(cd /tmp && zip -qj BIGCANOPY-v2_X_Y.mcaddon bigcanopy_bp.mcpack bigcanopy_rp.mcpack)
cp /tmp/BIGCANOPY-v2_X_Y.mcaddon /mnt/user-data/outputs/
```

### PatrixCanopyGen — `.mcaddon` containing single BP
```bash
cd /home/claude/patrixcanopygen
zip -qr /tmp/canopygen_bp.mcpack manifest.json pack_icon.png features/
(cd /tmp && zip -qj PatrixCanopyGen-v0_X_Y.mcaddon canopygen_bp.mcpack)
cp /tmp/PatrixCanopyGen-v0_X_Y.mcaddon /mnt/user-data/outputs/
```

### After packaging
- Always validate JSON: `python3 -c "import json; json.load(open('path'))"` on every .json
- Delete superseded version from `/mnt/user-data/outputs/` to avoid user confusion
- Call `present_files` tool with all three current deliverables
- Mention what to test in-game
- Note anything NOT in scope for that iteration (so user knows what was intentionally deferred)

---

## USER CONTEXT & CONVENTIONS

- **Tone:** concrete, direct, results-first. User tests on real hardware (mobile + eventually PS5) and sends video frames or screenshots.
- **Acknowledge visual diagnostics, don't speculate.** If user reports X, believe X over research docs until proven otherwise.
- **Scale back when uncertain.** If something's ambitious and may not work, propose it, note it may fail, ship the fallback if it does.
- **Be honest about research wrong-ness.** User called out that MCPE-165946 research was wrong for their platform. Own it, don't defend.
- **Every deliverable needs distinctive tag** in manifest display name so user can verify which loaded.
- **Shelved items:** never touch unless user explicitly reopens them. Current shelved list (some unshelved along the way):
  - Entity foliage color/density mismatch vs standing leaves — SHELVED (Option C, wait for VV)
  - Entity bark color mismatch vs standing trunks — SHELVED (Option C, wait for VV)
  - BIGCANOPY falling-entity size mismatch vs tree size — now in backlog as item #1
  - Phase 2D slope-based resting roll — UN-SHELVED (backlog item #13)
  - Phase 1 full-pack bulk texture port — IN PROGRESS incrementally

---

## FIRST-RESPONSE TEMPLATE (example)

When starting next chat, reply something like:

> Got it — resuming the PatrixWorld project. Before I can do anything, I need you to upload:
>
> **Critical:**
> - `Patrix_1.21.11_64x_basic.zip` (~198 MB — primary source)
> - `PATRIX-WORLD-SAMPLE-v0_2_5.mcpack` (current sampler)
> - `BIGCANOPY-v2_7_1.mcaddon` (current falling tree)
> - `PatrixCanopyGen-v0_1_1.mcaddon` (current canopy gen)
> - `bedrock-server-1.26.14.1.zip` (vanilla tree schemas for PatrixCanopyGen iteration)
> - The **acacia-didn't-fall screenshot** you mentioned
>
> **Nice to have:**
> - `Patrix_1.21.11_64x_addon.zip` (stained glass, cake)
> - `Patrix_1.21.11_64x_bonus.zip` (foodcrate, tudor)
>
> Once those are up, I'll verify extraction + UUIDs match the handoff, then ask you for direction on next iteration (acacia geometry rework, jungle canopy, or something else). Per the process rule, I'll outline plans before building from here on.
>
> What's the target for this session?

Keep it tight. No restating the full handoff.
