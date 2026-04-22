# PatrixWorld Bedrock Port — Handoff Document: v0.4.0 → v0.5.0

**Handoff date**: 2026-04-19  
**Current pack version**: v0.4.0 PAT+ALAC BLEND (shipped)  
**Next pack version**: v0.5.0 BLEND (to be built)  
**Author of this handoff**: Claude Opus 4.7 (session transcript exists; request if needed)

---

## ⚠ First action for the receiving Claude instance

Before writing any code or touching any files, request the following documents from the user in a single message:

1. **Previous session transcripts** — the user stores these at `/mnt/transcripts/`. The most recent is the full v0.4.0 build session. A `journal.txt` catalog exists in the same directory. Ask the user to confirm which transcripts they want you to read and load them incrementally as needed.

2. **128x-resolution texture packs** the user will upload for v0.5.0:
   - Patrix 128x basic (already in `/home/claude/uploads_all/patrix_128_basic/`)
   - Patrix 128x addon (already in `/home/claude/uploads_all/patrix_128_addon/`)
   - Patrix 128x bonus (already in `/home/claude/uploads_all/patrix_128_bonus/`)
   - Patrix 128x items (already in `/home/claude/uploads_all/patrix_128_items/`)
   - Patrix 128x mobs (already in `/home/claude/uploads_all/patrix_128_mobs/`)
   - Faithful 128x PBR (partial, in `/home/claude/uploads_round2/faithful_128/`)
   - **Confirm with user** if they want to re-upload Patrix 256x as an alternative source to scale to 128x

3. **The shipped v0.4.0 .mcpack** for reference — should still be at `/mnt/user-data/outputs/PATRIX-WORLD-SAMPLE-v0_4_0-PAT_ALAC_BLEND.mcpack` from last session; if not available, ask user to re-upload

4. **The `NON_PATRIX_TEXTURES.md`** audit doc — path `/mnt/user-data/outputs/NON_PATRIX_TEXTURES.md`

5. **In-game test observations** from v0.4.0 — ask the user what they saw in-game after testing the shipped build. This is the most important information to solicit at handoff. Common observation categories:
   - Broken mobs (mobs with wrong-UV renderings)
   - Plank/log/brick staggering effectiveness
   - Cherry blossom 7-shade variation appearance
   - Foliage opacity reduction felt right
   - Color normalization issues (savannah, canyon, etc.)
   - Any crashes, missing blocks, performance issues

6. **Confirmation on v0.5.0 scope priority** — the user has indicated v0.5.0 will be "environmental effects + import rest of texture packs in entirety". Ask for clarification:
   - Which environmental effects first (VV per-biome lighting? Atmospherics? Fogs? Foliage animation? Water physics?)
   - Full population of 128x subpack, or just scaffolding with selective content?
   - Is PBR/MERS activation (quartz-as-marble) in scope for v0.5.0 or deferred?

**Do not proceed without user green-light after delivering the above request.**

---

## Part 1: Project Identity (LOCKED)

### Scope

Minecraft Bedrock 1.26.x comprehensive port of Patrix aesthetic (Java 64x/128x) with FallingTree mechanics (BIGCANOPY), Tectonic worldgen (PatrixWorld-Tectonic), and Vibrant Visuals activation. Future: fluid physics.

### Platform targets

- **Primary**: PlayStation 5 (user's main test platform)
- **Secondary**: Mobile (Android)
- **Delivery**: Realms world (user ships to their Realms account for testing)
- **Settings**: Vibrant Visuals enabled + Experimental Voxel Shapes enabled

### User

Sole tester. Self-funded hobby project targeting eventual commercial release. Clear directive: nothing in this project should compromise ability to produce/sell.

---

## Part 2: Current State — What's Built and Shipped

### Pack architecture (4 packs currently; being consolidated)

| Pack | Version | Status | File |
|------|---------|--------|------|
| PatrixWorld Sampler | v0.4.0 PAT+ALAC BLEND | **CURRENT** | `PATRIX-WORLD-SAMPLE-v0_4_0-PAT_ALAC_BLEND.mcpack` |
| PatrixWorld-Tectonic | v0.7.2 VV TEST RUN | Stable, don't touch | `PatrixWorld-Tectonic-v0_7_2-VV_TEST_RUN.mcaddon` |
| BIGCANOPY | v2.8.1 VV TEST RUN | Stable, don't touch | `BIGCANOPY-v2_8_1-VV_TEST_RUN.mcaddon` |
| PatrixCanopyGen | v0.1.2 VV TEST RUN | Stable, don't touch | `PatrixCanopyGen-v0_1_2-VV_TEST_RUN.mcaddon` |

### v0.4.0 Sampler accomplishments (shipped)

- **Pack PNGs**: 1029 (v0.3.0) → **3206** (v0.4.0)
- **Pack size**: 12 MB → **34 MB**
- **blocks.json entries**: 90 → **225** (format_version 1.1.0 LOCKED)
- **terrain_texture shortnames**: 421 → **961**
- **Shortnames with variations arrays**: ~60 → **279**
- Zero broken references

### Phases completed in v0.4.0

1. **Phase 1**: 216 uniform-surface variants with 80/20 weighted arrays (grass, sand, dirt, terracotta family, moss, snow, podzol, mycelium)
2. **Phase 2**: log_top CTM-standalone bug fix + plank staggering (72 variants × 12 woods, vertical-offset compositing, NO isotropic per user directive)
3. **Phase 3**: log_side grain direction fix (15 misoriented rotated) + 80 log variants expanded + 220 stripped log variants + 285 brick/smooth material variants with 80/20 weighted distribution
4. **Phase 4**: 276 missing block PNGs + 119 missing mob files + sheep wool layered fix + villager full layered system + Hyper Realistic Sky environment textures
5. **Phase 5**: Mob audit side-by-side renders; squid/glow_squid ported; user chose "Patrix everywhere"
6. **Vegetation pass**: 79 new plant shortnames with variations arrays; foliage opacity −7%; cherry 7-shade fix; Patrix-everywhere swap (sheep/zombie/phantom reverted to Patrix)

### Working directories

```
/home/claude/work/sampler_v0_4_0/          ← ACTIVE, all v0.4.0 work
/home/claude/work/sampler_v0_3_0/          ← v0.3.0 baseline (preserved)
/home/claude/work/tectonic_v0_7_2/         ← Tectonic stable
/home/claude/work/bigcanopy_vv_test/       ← BIGCANOPY stable
/home/claude/work/canopygen_vv_test/       ← PatrixCanopyGen stable
```

### Source texture locations

```
/home/claude/patrix_ref/basic/             ← Patrix 64x (3056 PNGs + 24344 CTM tiles across 134 cats)
/home/claude/patrix_ref/addon/             ← Patrix 64x supplementary
/home/claude/patrix_ref/bonus/             ← Patrix 64x supplementary
/home/claude/refpacks/alacrity/            ← Alacrity 32x (306 blocks + 674 entities + CTM)
/home/claude/refpacks/low_realistic/       ← 2028 Java block PNGs
/home/claude/refpacks/glowing_ores/        ← Bedrock PBR ore MER maps
/home/claude/refpacks/realsource_vv/       ← Microsoft VV template
/home/claude/uploads_all/patrix_128_basic/ ← Patrix 128x (3084 blocks + 24344 CTM, with _n/_s PBR maps)
/home/claude/uploads_all/patrix_128_addon/ ← Patrix 128x supplementary (58 blocks + 7253 CTM)
/home/claude/uploads_all/patrix_128_bonus/ ← Patrix 128x supplementary (3 blocks + 1948 CTM, scifi/road)
/home/claude/uploads_all/patrix_128_items/ ← Patrix 128x (1801 items, 204 equipment)
/home/claude/uploads_all/patrix_128_mobs/  ← Patrix 128x (795 entities, 84 blocks, 102 CTM)
/home/claude/uploads_all/faithful_64_r11/  ← Faithful 64x R11 (Bedrock-native) — SUPERSEDED BY R13
/home/claude/uploads_all/faithful_64_r13/  ← Faithful 64x R13 (Bedrock-native, 1186 blocks + 587 entities + 857 items + flipbook)
/home/claude/uploads_round2/faithful_128/  ← Faithful 128x PBR (partial, 110 blocks + MERS .tga maps)
/home/claude/bds/behavior_packs/vanilla_*/ ← Vanilla BDS 1.26.14 reference
/home/claude/mods_round3/                  ← Java mods inventory (reference only, NOT usable on Bedrock):
   ambient_fabric/                          ← AmbientSounds 6.3.5 (audio)
   atmospherica/                            ← AtmosphericA 1.0.0 (fog per biome)
   atmospherics/                            ← Atmospherics 2.6 (biome-based fog/sky/clouds/stars editor)
   efalling/                                ← Enhanced Falling Trees 0.6.0
   dramatic_skys/                           ← Dramatic Skys Demo 1.5.3
   hyper_sky/                               ← Hyper Realistic Sky v3.8 (sky PNGs ALREADY ported)
```

### Critical source PNGs already ported (vs still available)

**Already in sampler v0.4.0**:
- Patrix 64 base blocks (1000+ files)
- Patrix 64 CTM variants (selectively imported: leaves, flowers, bushes, vines, grass, kelp, seagrass, cactus, lily_pad, mushroom, saplings, dead_bush, hanging_roots, glow_lichen, stone_bricks, bricks, nether_bricks, quartz_bricks, calcite, dripstone, podzol, moss_block, snow, terracotta, etc.)
- Mobs: Patrix 64 (primary) + Patrix 128 mobs scaled 50% (cat breeds, chicken/cow biome variants, copper_golem, creaking, breeze)
- Alacrity: villager layered system, zombie_villager layered system, squid, glow_squid
- Hyper Realistic Sky: sun, moon_phases, clouds, rain, snow + 8 moon phase celestial files

**Available but NOT YET ported** (v0.5.0 scope):
- Patrix 128x basic blocks at full 128 resolution (3084 PNGs)
- Patrix 128x CTM at full resolution (24344 tiles)
- Patrix 128x items (1801 PNGs) — items not yet in sampler at all
- Patrix 128x mobs at full resolution (scale-up from current 64x)
- Patrix 128x PBR normal/specular maps (_n.png, _s.png throughout)
- Faithful 128x PBR MERS maps (.tga format)

---

## Part 3: LOCKED Values (never change)

### UUIDs (memorize; do not regenerate)

**Sampler (current pack)**
- Header UUID: `7b5e9f01-3a24-4b6c-9d17-8e5f4c2b19a0`
- Resources module UUID: `f2c8d9e4-6a51-4f8b-a3c9-1d8e7b4f5c62`
- min_engine_version: `[1, 26, 0]`

**BIGCANOPY**
- BP header: `be7227ad-138a-45a5-9e38-4c2cf4732440`
- BP data module: `a8b6523b-c9ac-4a1b-8586-aea316833b4b`
- BP script module: `6fed24a7-f6c9-47ef-90ec-6b0b20d5ca0c`
- RP header: `4410d782-8723-40e3-9586-8262cbb9a1f8`
- RP resources module: `95f4efcf-0333-4373-b470-eea36df91034`

**PatrixCanopyGen**
- BP header: `5923a10b-6552-48a0-9528-d3a33fcf2bdf`
- BP data module: `bca67360-d523-4155-b802-d2bd264fd93b`
- min_engine_version: `[1, 20, 20]`

**Tectonic**
- BP header: `2a8f6b14-7e9c-4d3a-a1b5-c8e7f2d4a690`
- BP data module: `d14e8c23-6f5a-4b9e-8c2d-7a3b5e9f1c40`
- RP header: `3b9a4c26-8d1e-4f7b-a5c3-2e8d6b4a1f70`
- RP resources module: `e25f9d34-7b6c-4d8a-9e1f-3c5b8d7a2e50`

### Format versions (LOCKED)

- **blocks.json** `format_version`: `1.1.0` — **NEVER change**. User confirmed this value works on Bedrock 1.26.x. Other format versions (1.19.60, 1.21.10) have been tried and have subtle rendering regressions.
- **terrain_texture.json** `num_mip_levels`: `4`
- **manifest.json** `format_version`: `2`
- **feature_rules / features** `format_version`: `1.13.0` for most; some specific features use higher

### Naming conventions

- **Manifest name must include a `[TAG vX.Y.Z]`** block for in-game visual identification (e.g. `[PAT+ALAC BLEND v0.4.0]`). User relies on this to confirm a pack is the newest one they loaded.
- **Future version naming**: `v#.#.# Blend` until next major integration
- **Modern vs legacy block names**: Register BOTH shortname aliases. Patrix uses modern Java names (`acacia_planks`, `oak_log`). Bedrock engine still looks up legacy names (`planks_acacia`, `log_oak`, `log_big_oak` for dark_oak, `wool_colored_black` for black_wool, `flower_rose` for poppy, etc.). terrain_texture.json must register both pointing to same variant arrays.

### Isotropic strategy

- `isotropic: true` → noise/uniform materials (terracotta, dirt, sand, gravel, clay, leaves, wool, concrete, carpet)
- `isotropic: {up: true, down: true}` → grain-bearing side blocks (stone_bricks family, polished_blackstone family, end_stone_bricks, nether_bricks, sandstone variants, stone/granite/andesite/deepslate/cobblestone/netherrack/blackstone/smooth_basalt/packed_mud/mud_bricks)
- **NO isotropic** → directional blocks (quartz_block, quartz_pillar, basalt, polished_basalt) — all faces locked
- **NO isotropic on PLANKS** — user directive LOCKED. Grain direction stays horizontal, staggering comes purely from variant selection. Never isotropic on planks.
- **NO isotropic on LOGS** — grain direction per species (vertical for oak/acacia/dark_oak, horizontal-featured for birch/cherry). Species consistency matters more than within-tree consistency.

### Weighted-variations philosophy (user Observation 1, LOCKED)

"Uniform with occasional break" — keep 16 variant slots but weight them. Algorithm:
- Rank variants by RGB stddev (low variance = uniform, high = break)
- Bottom 70% = uniform pool → 80% aggregate weight (distributed inverse-rank)
- Top 30% = break pool → 20% aggregate weight (distributed inverse-rank)
- All variants remain in the array (no pruning); weight distribution controls frequency

Exception: vegetation uses **flat uniform weights** (all variants equally likely) because user wants "free form and natural" variety rather than weighted pattern-break.

### Capabilities flag

- **`"capabilities": ["pbr"]`** on RP manifest ONLY (BP does NOT take it)
- Required for VV activation even when no PBR maps are shipped yet

### Debug flags

- **BIGCANOPY `[BIGCANOPY] broke <block>` warnings**: KEEP ENABLED. User uses these to identify unknown block IDs during PS5 testing.

---

## Part 4: v0.5.0 Scope (tentative — await user confirmation)

User said: "environmental effects and import the rest of the texture packs in their entirety."

**Most likely v0.5.0 work breakdown**:

### Track 1 — 128x subpack population (high priority)

1. Manifest `subpacks` array scaffolding: `64x` (default) + `128x` (tier 1) selectable via pack settings slider
2. Copy Patrix 128x basic blocks → `subpacks/128x/textures/blocks/`
3. Copy Patrix 128x mobs (full res, no scaling) → `subpacks/128x/textures/entity/`
4. Copy Patrix 128x items → `subpacks/128x/textures/items/` (items not ported yet at any res)
5. Re-import Patrix 128 CTM at full resolution for variations arrays
6. Subpack-specific terrain_texture.json / item_texture.json if needed
7. In-game validation via subpack slider toggle

### Track 2 — Environmental effects via VV

User has provided atmospherics v2.6 `source_biome_fog.json` as authoring reference. Port its JSON parameters to Bedrock VV:

- Per-biome `lighting.json` (sun/moon scattering parameters)
- Per-biome `atmospherics.json` (haze colors, star amounts, cloud density)
- Per-biome `fogs.json` (fog gradients, horizon blending)
- Pack all 10 Tectonic biomes (pw_peak, pw_alpine, pw_boreal, pw_coast, pw_cherry, pw_dunes, pw_cliffs, pw_canyon, pw_badlands, pw_pale) with VV profiles

**Reference JSON** to adapt from:
`/home/claude/mods_round3/atmospherics/assets/atmospherics/presets/source_biome_fog.json`

Known parameters (already copied into handoff notes for reference):
- `fogDensity: 0.3`
- `haze.color: 15398143`, `haze.nightColor: 3866805`
- `stars.amount: 1500`, `brightness: 0.999`, `twinkle: 0.5`
- `clouds.storeModeCloudHeight: 2.5`, `storeModeCloudOpacity: 1.0`
- `caustics.framesPerSecond: 24` (water caustics — Bedrock VV has 64 caustic frames native)

### Track 3 — PBR/MERS activation (maybe)

- Patrix 128x ships `_n.png` (normal) + `_s.png` (specular) maps throughout
- Faithful 128x ships MERS as `.tga` files (metalness/emissive/roughness/subsurface)
- Bedrock PBR uses `texture_set.json` per-texture with fields like:
  ```json
  {
    "format_version": "1.16.100",
    "minecraft:texture_set": {
      "color": "stone",
      "normal": "stone_normal",
      "heightmap": "stone_height",
      "metalness_emissive_roughness": "stone_mers"
    }
  }
  ```
- Marble-reflective quartz would be the first PBR hero test
- Requires VV enabled + capabilities:["pbr"] (already set)

### Track 4 — Animated foliage (deferred/optional)

- Vanilla Bedrock ALREADY applies wave-on-wind to leaves/grass/flowers automatically (hardcoded in block definitions, inherited by texture-only packs)
- User noticed tree shadows moving during test — was sun arc, not wave animation (confirmed during session)
- If user wants MORE visible sway, options are:
  - (a) Flipbook animations supplementing vanilla vertex wave (for hero plants: eyeblossom open/close, torchflower blooming, spore_blossom pulse)
  - (b) VV shader-based sway — post-VV activation complex
- Clarify with user whether vanilla sway is enough or augmentation needed

### Track 5 — Color normalization pass (v0.5.0 BLEND polish)

User observations shelved from earlier phases:
- Savannah stark orange/red color shift
- Canyon/badlands terracotta look "flat" — Patrix authored smooth, stands out against richer neighboring stones
- General palette harmonization across Patrix/Faithful/Alacrity sources where still used

---

## Part 5: Operating Protocol (USER PREFERENCES — LOCKED)

### Plan-before-build

**STRICT**: Before creating files / editing code / bumping manifests, outline:
1. What you intend to change
2. Tradeoffs / side effects
3. Ask for green light

Investigation (reading files, running scans, analyzing assets) is fine without asking. File changes require explicit approval.

### Single-build-per-iteration

One .mcpack output per iteration. Don't produce intermediate builds.

### In-game observation priority

User trusts in-game observations over research/documentation when they conflict. If user reports something's broken and you've read docs saying it should work, user wins. Investigate the discrepancy.

### Response length calibration

- **Simple questions**: 1-2 sentences
- **How-to**: short list, no intro
- **Substantive**: 2-3 short paragraphs (one screenful)
- **Complex**: max 2 screenfuls

Start with the answer. No preamble. No "Great question!" No restating the question.

### User directive-style decisions (DO NOT second-guess)

- Patrix textures preferred over everything, even if UV mismatches exist. User will fix UV mappings manually later. Do not propose Alacrity/Faithful swaps unless Patrix source literally doesn't exist.
- Quality over quantity — user defaults to "most comprehensive/quality option" always
- User will toggle 64x vs 128x via subpack slider (planned v0.5.0)
- Single texture pack consolidation — everything eventually in one sampler
- PLANKS non-isotropic (grain direction locked) — this is permanent, don't offer to change

### Observations user has articulated (memorize these)

- **Observation 1 (weighted variance)**: uniform with occasional break — keep 16 variants weighted 80/20
- **Observation 2 (log individuality)**: each tree unique, but grain direction locked per species
- **Observation 3 (plank stagger)**: joints must line up when placed — composite vertical offsets, NO isotropic
- **Vegetation directive**: free-form natural variety, equal weights across variants
- **Foliage opacity**: reduce by 7% to prevent solid-green dense clusters (already applied in v0.4.0)

---

## Part 6: Deferred / Shelved Items (NOT forgotten)

### Immediate post-test items

- Fix bugs reported from v0.4.0 in-game test (solicit from user)
- Mob UV fixes for Patrix-everywhere swap consequences (user accepted this tradeoff knowing bugs might return)

### v0.5.0 explicit deferrals

- **Color normalization**: savannah/canyon/badlands palette harmonization
- **128x subpack**: full population with Patrix 128x
- **PBR/MERS**: marble-reflective quartz, .tga MERS from Faithful 128x
- **VV per-biome**: pw_* biome lighting/atmospherics/fogs JSON

### Post-v0.5.0 shelved

- **Fluid physics** (Track G): `ff:water_finite`, ~3000-6000 block budget for PS5 (user-locked phase ordering — don't start until VV complete)
- **Physics Mod Pro Haubna fluids-only** (after fluid physics)
- **BIGCANOPY acacia atlas rework**: awaiting user recording to show issue; user has said grid SIZE is wrong, NOT canopy size
- **BIGCANOPY slope-based resting roll**: Phase 2D of BIGCANOPY, deferred
- **Patrix models pack 3D geometry**: stalactites, crystals, extra grass, hanging roots (3D block models)
- **Lava animation boost**: reduce ticks_per_frame 4→2 on lava_still, keep blend_frames true. User confirmed lava animates mildly; they want more motion
- **Villager Patrix re-authoring**: 84 files (documented in NON_PATRIX_TEXTURES.md). User will do this manually on their own time
- **Commercial release + handoff prep**: final doc sweep for v1.0

---

## Part 7: Known Bug Risks from Patrix-Everywhere Swap

User in last session directed a swap back to Patrix for sheep/sheep_wool/sheep_wool_undercoat/phantom/zombie/drowned/husk — reversing earlier Alacrity swaps that had been made to fix UV mismatches.

**Expected bugs that may reappear in v0.4.0 testing**:
- Sheep may render with wool issue (Patrix 64 sheep = 256×128, Bedrock UV is 64×32 × 4 = 256×128 — SHOULD work but earlier testing showed issues)
- Phantom may show stretched/compressed texture (Patrix phantom = 256×256, Bedrock UV is 64×32, so ratio mismatch)
- Zombie/drowned/husk may show UV issues

**User's stance**: "fix mapping issues later." Do not propose re-swapping to Alacrity unless user explicitly asks.

---

## Part 8: Technical gotchas (LOCKED knowledge)

### Bedrock worldgen constraints (for Tectonic work if any)

- 15 noise_types; 6 surface_builder types; 8 valid `placement_pass` values
- `multinoise_generation_rules` is pre-caves-and-cliffs legacy; MUST be removed from custom biomes
- `minecraft:village_type` is schema-rejected on custom biomes
- `minecraft:terracotta` bare name DOES NOT EXIST — use `minecraft:hardened_clay`
- `minecraft:snow_layer` DOES NOT EXIST — use `minecraft:snow` for layer, `snow_block` for cube
- Legacy biome naming: `mesa` (not `badlands`), `savanna_mutated` (not `windswept_savanna`), `stony_peaks` (not `stony_shore`), `ice_plains_spikes` (not `ice_spikes`), `taiga_mutated` (not `old_growth_spruce_taiga`)

### CTM-as-standalone discoveries (v0.4.0 bug fixes)

- **log_top bug**: Patrix `optifine/ctm/patrix/log/<wood>/top/` tiles are Java OptiFine CTM tiles meant to connect into one 2×2 ring. On Bedrock (no CTM), each tile shows a PARTIAL ring cut at edges. FIX applied: use `block/<wood>_log_top.png` basic tile + synthesize 8 variants via rotation + subtle tint/brightness.
- **log_side grain bug**: v1, v3, v5 variants in oak/acacia/dark_oak were 90°-rotated wrong (horizontal-grain when vertical needed). Fixed by 90° rotation. Birch/cherry have NATURAL horizontal bark features (stripes/lenticels); horizontal grain IS correct for those species.

### Sheep layered-texture fix (v0.4.0 Phase 4)

Bedrock sheep model uses 3 texture files as layers:
- `sheep.png` — base body
- `sheep_wool.png` — primary wool coat
- `sheep_wool_undercoat.png` — undercoat for wool tinting

Pre-Phase 4, only `sheep.png` was ported. This was THE root cause of persistent sheep bug. Fix is complete in v0.4.0 (Patrix sources used).

### Villager layered system (v0.4.0 Phase 4)

Bedrock villager = base + profession + profession_level + type_biome, 4 layers.
Patrix ships NO villager textures anywhere (64 basic, 128 basic, 128 mobs all lack).
Currently sourced from Alacrity. 42 files under `villager2/` directory covering base + 14 professions + 5 profession_levels + 7 biome types, with BOTH Alacrity naming (`profession_level/`, `type/`) AND Faithful naming (`levels/`, `biomes/`) conventions since different Bedrock versions/mods lookup differently.

### Track C closed (Tectonic water)

v0.7.1 4 per-biome water profiles loaded without `[Lighting][error]`:
- Alpine: gentle, depth 0.6 power 3
- Cherry: MS-canonical
- Desert: energetic, depth 1.8 sediment 6 frequency 1.3
- Forest: calm-green chlorophyll 2.0 depth 0.8

Per-biome variation confirmed working. v0.7.2 preserves verbatim.

---

## Part 9: What I (outgoing Claude) would do differently

Self-critique for future Claude to learn from:

1. **Should have done the vegetation variant pass in Phase 1, not retroactively**. User's observation about uniform-with-break applies to ALL materials, and treating vegetation separately made the v0.4.0 build larger than necessary.
2. **Should have investigated `sheep_wool.png` layer requirement in v0.2.x not v0.4.0**. 5+ iterations of "sheep still broken" could have been 1 if root cause investigation was deeper earlier.
3. **Mob audit Phase 5 was over-engineered**. 66 per-mob grids was more than user could review. Category sheets were right; individual grids were not needed. Scale accordingly.
4. **Patrix-everywhere swap could have been offered at Phase 4 instead of last-minute Phase 5 override**. User directive was knowable from their consistent "Patrix realism quality is stark" comments.

---

## Part 10: Receiving Claude — Operating Checklist

Before ANY work, confirm with user:
- [ ] Transcripts available at `/mnt/transcripts/`? Which ones to read?
- [ ] v0.4.0 in-game test results available? What broke, what worked?
- [ ] 128x source packs still at `/home/claude/uploads_all/patrix_128_*/`? Or re-upload needed?
- [ ] v0.5.0 scope priorities locked in (environmental effects order, 128x fill depth)?
- [ ] PBR/MERS activation in scope or deferred?
- [ ] Foliage animation augmentation wanted beyond vanilla Bedrock's built-in sway?

After confirmation:
- [ ] Read the transcripts user provides, build mental model
- [ ] Read this handoff doc end-to-end
- [ ] Read `NON_PATRIX_TEXTURES.md`
- [ ] Spot-check the v0.4.0 sampler state (manifest, blocks.json, terrain_texture.json, pack size)
- [ ] THEN propose a v0.5.0 phase plan
- [ ] Wait for green light before writing files

---

## Part 11: Source data for referencing

These files are useful starting points when v0.5.0 begins:

- Atmospherics VV reference JSON: `/home/claude/mods_round3/atmospherics/assets/atmospherics/presets/source_biome_fog.json`
- Realsource VV template: `/home/claude/refpacks/realsource_vv/`
- Faithful 128x PBR .tga samples: `/home/claude/uploads_round2/faithful_128/`
- Tectonic biome definitions: `/home/claude/work/tectonic_v0_7_2/behavior_pack/biomes/`
- Vanilla BDS biome reference: `/home/claude/bds/behavior_packs/vanilla_1.26.*/biomes/`

---

## Closing note

v0.4.0 represents the first "near-complete" aesthetic pass — 3206 PNGs, Patrix-dominant, variations active across 279 shortnames, all major mob renderings working, layered sheep/villager/zombie systems fixed, environment sky from Hyper Realistic Sky, cherry-blossom double-shade mystery solved. v0.5.0 is about depth: higher resolution subpack, PBR activation, VV per-biome environmental effects, and polish. Approach it incrementally. Ask the user clarifying questions early. Don't break what's working.

Good luck. The user is a thoughtful collaborator who tests in-game and knows what they want. Trust their observations.

