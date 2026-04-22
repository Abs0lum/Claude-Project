# PatrixWorld Unified Pack — AI Continuity Handoff

**Purpose of this document**: If this chat hits its context limit and the user starts a new one, this is the single source of truth you (the next AI instance) need to resume without asking the user to re-explain the project. The user will upload this file to the new chat along with source assets. Read it fully before responding.

**Growth rule**: This document is append-only. Each iteration adds to relevant sections. Never remove historical context. The only content stripped is user-only material (testing instructions, observation prompts, human-readable language) — that lives in the per-iteration `UNIFIED_PACK_HANDOFF-v{X}.md` instead.

**Last updated**: 2026-04-19, iteration v0.5.1-ZOMBIE-PROOF.

**Document structure:**
- **§0** — Historical handoff archive (prior docs, verbatim). Skim before §1 for full context.
- **§1–§14** — Current continuity knowledge (the live, actively-maintained sections).

---

## §0. Historical handoff archive

This section preserves prior handoff documents from earlier phases of the project, verbatim (headers demoted 2 levels to avoid colliding with this doc's numbering). They precede the current architecture (pre-unification phase where 4 separate packs shipped independently) but contain locked knowledge, design decisions, and technical gotchas still relevant.

**Reading order for fastest onboarding**: skim §0.1 first (most recent pre-unification state), then §0.4 for the texture-source audit. §0.2 and §0.3 are historical reference, useful for deep questions about early design choices.

**Contents:**
- **§0.1** — `PatrixWorld Bedrock Port Handoff v0.4.0 → v0.5.0` (most recent pre-unification). Parts 3-5 lost to transcript truncation; Parts 1, 2, 6-11 preserved. Missing parts covered a v0.5.0 phase plan since superseded by the current unified/variants architecture.
- **§0.2** — `PatrixWorld Handoff v3` (v0.2.5 era).
- **§0.3** — `PatrixWorld Handoff v2` (v0.2.5 predecessor of v3).
- **§0.4** — `NON_PATRIX_TEXTURES.md` (v0.4.0 texture-source audit).

---

### §0.1 — Handoff: v0.4.0 → v0.5.0 (most recent pre-unification)

*Preserved from prior Claude Opus 4.7 session transcript. Parts 3–5 were lost to transcript truncation.*

**<<< BEGIN ARCHIVED DOCUMENT >>>**

### PatrixWorld Bedrock Port — Handoff Document: v0.4.0 → v0.5.0

**Handoff date**: 2026-04-19  
**Current pack version**: v0.4.0 PAT+ALAC BLEND (shipped)  
**Next pack version**: v0.5.0 BLEND (to be built)  
**Author of this handoff**: Claude Opus 4.7 (session transcript exists; request if needed)

---

#### ⚠ First action for the receiving Claude instance

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

#### Part 1: Project Identity (LOCKED)

##### Scope

Minecraft Bedrock 1.26.x comprehensive port of Patrix aesthetic (Java 64x/128x) with FallingTree mechanics (BIGCANOPY), Tectonic worldgen (PatrixWorld-Tectonic), and Vibrant Visuals activation. Future: fluid physics.

##### Platform targets

- **Primary**: PlayStation 5 (user's main test platform)
- **Secondary**: Mobile (Android)
- **Delivery**: Realms world (user ships to their Realms account for testing)
- **Settings**: Vibrant Visuals enabled + Experimental Voxel Shapes enabled

##### User

Sole tester. Self-funded hobby project targeting eventual commercial release. Clear directive: nothing in this project should compromise ability to produce/sell.

---

#### Part 2: Current State — What's Built and Shipped

##### Pack architecture (4 packs currently; being consolidated)

| Pack | Version | Status | File |
|------|---------|--------|------|
| PatrixWorld Sampler | v0.4.0 PAT+ALAC BLEND | **CURRENT** | `PATRIX-WORLD-SAMPLE-v0_4_0-PAT_ALAC_BLEND.mcpack` |
| PatrixWorld-Tectonic | v0.7.2 VV TEST RUN | Stable, don't touch | `PatrixWorld-Tectonic-v0_7_2-VV_TEST_RUN.mcaddon` |
| BIGCANOPY | v2.8.1 VV TEST RUN | Stable, don't touch | `BIGCANOPY-v2_8_1-VV_TEST_RUN.mcaddon` |
| PatrixCanopyGen | v0.1.2 VV TEST RUN | Stable, don't touch | `PatrixCanopyGen-v0_1_2-VV_TEST_RUN.mcaddon` |

##### v0.4.0 Sampler accomplishments (shipped)

- **Pack PNGs**: 1029 (v0.3.0) → **3206** (v0.4.0)
- **Pack size**: 12 MB → **34 MB**
- **blocks.json entries**: 90 → **225** (format_version 1.1.0 LOCKED)
- **terrain_texture shortnames**: 421 → **961**
- **Shortnames with variations arrays**: ~60 → **279**
- Zero broken references

##### Phases completed in v0.4.0

1. **Phase 1**: 216 uniform-surface variants with 80/20 weighted arrays (grass, sand, dirt, terracotta family, moss, snow, podzol, mycelium)
2. **Phase 2**: log_top CTM-standalone bug fix + plank staggering (72 variants × 12 woods, vertical-offset compositing, NO isotropic per user directive)
3. **Phase 3**: log_side grain direction fix (15 misoriented rotated) + 80 log variants expanded + 220 stripped log variants + 285 brick/smooth material variants with 80/20 weighted distribution
4. **Phase 4**: 276 missing block PNGs + 119 missing mob files + sheep wool layered fix + villager full layered system + Hyper Realistic Sky environment textures
5. **Phase 5**: Mob audit side-by-side renders; squid/glow_squid ported; user chose "Patrix everywhere"
6. **Vegetation pass**: 79 new plant shortnames with variations arrays; foliage opacity −7%; cherry 7-shade fix; Patrix-everywhere swap (sheep/zombie/phantom reverted to Patrix)

##### Working directories

```
/home/claude/work/sampler_v0_4_0/          ← ACTIVE, all v0.4.0 work
/home/claude/work/sampler_v0_3_0/          ← v0.3.0 baseline (preserved)
/home/claude/work/tectonic_v0_7_2/         ← Tectonic stable
/home/claude/work/bigcanopy_vv_test/       ← BIGCANOPY stable
/home/claude/work/canopygen_vv_test/       ← PatrixCanopyGen stable
```

##### Source texture locations

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

##### Critical source PNGs already ported (vs still available)

**Already in sampler v0.4.0**:
- Patrix 64 base blocks (1000+ files)
< truncated lines 136-334 >

---

#### Part 6: Deferred / Shelved Items (NOT forgotten)

##### Immediate post-test items

- Fix bugs reported from v0.4.0 in-game test (solicit from user)
- Mob UV fixes for Patrix-everywhere swap consequences (user accepted this tradeoff knowing bugs might return)

##### v0.5.0 explicit deferrals

- **Color normalization**: savannah/canyon/badlands palette harmonization
- **128x subpack**: full population with Patrix 128x
- **PBR/MERS**: marble-reflective quartz, .tga MERS from Faithful 128x
- **VV per-biome**: pw_* biome lighting/atmospherics/fogs JSON

##### Post-v0.5.0 shelved

- **Fluid physics** (Track G): `ff:water_finite`, ~3000-6000 block budget for PS5 (user-locked phase ordering — don't start until VV complete)
- **Physics Mod Pro Haubna fluids-only** (after fluid physics)
- **BIGCANOPY acacia atlas rework**: awaiting user recording to show issue; user has said grid SIZE is wrong, NOT canopy size
- **BIGCANOPY slope-based resting roll**: Phase 2D of BIGCANOPY, deferred
- **Patrix models pack 3D geometry**: stalactites, crystals, extra grass, hanging roots (3D block models)
- **Lava animation boost**: reduce ticks_per_frame 4→2 on lava_still, keep blend_frames true. User confirmed lava animates mildly; they want more motion
- **Villager Patrix re-authoring**: 84 files (documented in NON_PATRIX_TEXTURES.md). User will do this manually on their own time
- **Commercial release + handoff prep**: final doc sweep for v1.0

---

#### Part 7: Known Bug Risks from Patrix-Everywhere Swap

User in last session directed a swap back to Patrix for sheep/sheep_wool/sheep_wool_undercoat/phantom/zombie/drowned/husk — reversing earlier Alacrity swaps that had been made to fix UV mismatches.

**Expected bugs that may reappear in v0.4.0 testing**:
- Sheep may render with wool issue (Patrix 64 sheep = 256×128, Bedrock UV is 64×32 × 4 = 256×128 — SHOULD work but earlier testing showed issues)
- Phantom may show stretched/compressed texture (Patrix phantom = 256×256, Bedrock UV is 64×32, so ratio mismatch)
- Zombie/drowned/husk may show UV issues

**User's stance**: "fix mapping issues later." Do not propose re-swapping to Alacrity unless user explicitly asks.

---

#### Part 8: Technical gotchas (LOCKED knowledge)

##### Bedrock worldgen constraints (for Tectonic work if any)

- 15 noise_types; 6 surface_builder types; 8 valid `placement_pass` values
- `multinoise_generation_rules` is pre-caves-and-cliffs legacy; MUST be removed from custom biomes
- `minecraft:village_type` is schema-rejected on custom biomes
- `minecraft:terracotta` bare name DOES NOT EXIST — use `minecraft:hardened_clay`
- `minecraft:snow_layer` DOES NOT EXIST — use `minecraft:snow` for layer, `snow_block` for cube
- Legacy biome naming: `mesa` (not `badlands`), `savanna_mutated` (not `windswept_savanna`), `stony_peaks` (not `stony_shore`), `ice_plains_spikes` (not `ice_spikes`), `taiga_mutated` (not `old_growth_spruce_taiga`)

##### CTM-as-standalone discoveries (v0.4.0 bug fixes)

- **log_top bug**: Patrix `optifine/ctm/patrix/log/<wood>/top/` tiles are Java OptiFine CTM tiles meant to connect into one 2×2 ring. On Bedrock (no CTM), each tile shows a PARTIAL ring cut at edges. FIX applied: use `block/<wood>_log_top.png` basic tile + synthesize 8 variants via rotation + subtle tint/brightness.
- **log_side grain bug**: v1, v3, v5 variants in oak/acacia/dark_oak were 90°-rotated wrong (horizontal-grain when vertical needed). Fixed by 90° rotation. Birch/cherry have NATURAL horizontal bark features (stripes/lenticels); horizontal grain IS correct for those species.

##### Sheep layered-texture fix (v0.4.0 Phase 4)

Bedrock sheep model uses 3 texture files as layers:
- `sheep.png` — base body
- `sheep_wool.png` — primary wool coat
- `sheep_wool_undercoat.png` — undercoat for wool tinting

Pre-Phase 4, only `sheep.png` was ported. This was THE root cause of persistent sheep bug. Fix is complete in v0.4.0 (Patrix sources used).

##### Villager layered system (v0.4.0 Phase 4)

Bedrock villager = base + profession + profession_level + type_biome, 4 layers.
Patrix ships NO villager textures anywhere (64 basic, 128 basic, 128 mobs all lack).
Currently sourced from Alacrity. 42 files under `villager2/` directory covering base + 14 professions + 5 profession_levels + 7 biome types, with BOTH Alacrity naming (`profession_level/`, `type/`) AND Faithful naming (`levels/`, `biomes/`) conventions since different Bedrock versions/mods lookup differently.

##### Track C closed (Tectonic water)

v0.7.1 4 per-biome water profiles loaded without `[Lighting][error]`:
- Alpine: gentle, depth 0.6 power 3
- Cherry: MS-canonical
- Desert: energetic, depth 1.8 sediment 6 frequency 1.3
- Forest: calm-green chlorophyll 2.0 depth 0.8

Per-biome variation confirmed working. v0.7.2 preserves verbatim.

---

#### Part 9: What I (outgoing Claude) would do differently

Self-critique for future Claude to learn from:

1. **Should have done the vegetation variant pass in Phase 1, not retroactively**. User's observation about uniform-with-break applies to ALL materials, and treating vegetation separately made the v0.4.0 build larger than necessary.
2. **Should have investigated `sheep_wool.png` layer requirement in v0.2.x not v0.4.0**. 5+ iterations of "sheep still broken" could have been 1 if root cause investigation was deeper earlier.
3. **Mob audit Phase 5 was over-engineered**. 66 per-mob grids was more than user could review. Category sheets were right; individual grids were not needed. Scale accordingly.
4. **Patrix-everywhere swap could have been offered at Phase 4 instead of last-minute Phase 5 override**. User directive was knowable from their consistent "Patrix realism quality is stark" comments.

---

#### Part 10: Receiving Claude — Operating Checklist

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

#### Part 11: Source data for referencing

These files are useful starting points when v0.5.0 begins:

- Atmospherics VV reference JSON: `/home/claude/mods_round3/atmospherics/assets/atmospherics/presets/source_biome_fog.json`
- Realsource VV template: `/home/claude/refpacks/realsource_vv/`
- Faithful 128x PBR .tga samples: `/home/claude/uploads_round2/faithful_128/`
- Tectonic biome definitions: `/home/claude/work/tectonic_v0_7_2/behavior_pack/biomes/`
- Vanilla BDS biome reference: `/home/claude/bds/behavior_packs/vanilla_1.26.*/biomes/`

---

#### Closing note

v0.4.0 represents the first "near-complete" aesthetic pass — 3206 PNGs, Patrix-dominant, variations active across 279 shortnames, all major mob renderings working, layered sheep/villager/zombie systems fixed, environment sky from Hyper Realistic Sky, cherry-blossom double-shade mystery solved. v0.5.0 is about depth: higher resolution subpack, PBR activation, VV per-biome environmental effects, and polish. Approach it incrementally. Ask the user clarifying questions early. Don't break what's working.

Good luck. The user is a thoughtful collaborator who tests in-game and knows what they want. Trust their observations.



**<<< END ARCHIVED DOCUMENT >>>**

---

### §0.2 — Handoff v3 (v0.2.5 era)

*Full document, uploaded by user. Earlier state before 4-pack architecture consolidation.*

**<<< BEGIN ARCHIVED DOCUMENT >>>**

### PatrixWorld Bedrock Modding Project — Full Handoff (v3)

Resuming a long-running Minecraft Bedrock 1.26.x modding project. Prior chat hit context limit. This document supersedes all previous handoffs. **Read fully before responding.**

---

#### TURN 1 PROTOCOL

1. Acknowledge briefly. Do NOT restate this document back.
2. Request the files listed under UPLOADS below (abbreviated — don't explain each one again).
3. Ask the user for the **acacia-didn't-fall screenshot** specifically — they have one saved from a tree that failed to fall, needed for the acacia geometry rework that's pending.
4. Ask what the target for this session is (jungle canopy / acacia geometry / continue block ports / etc. — see backlog below).
5. **Wait for all three** before starting any work.

---

#### NEW PROCESS RULE — CRITICAL

**No builds without plan-first discussion.** Every iteration starts:

1. Outline what you intend to change
2. Note tradeoffs + what stays as-is
3. Wait for user's green light or additional direction
4. Then build

The user added this rule explicitly to catch wrong assumptions early. Skipping it is a regression. Investigation/diagnostic work (reading files, computing hashes, comparing colors) is fine without asking — just don't write output files, modify source code, or bump manifests until you've confirmed the plan.

---

#### UPLOADS TO REQUEST

##### Critical — blocks all work
1. **`Patrix_1.21.11_64x_basic.zip`** (~198 MB) — Patrix Java source, 3056 block PNGs at 64×64, massive OptiFine CTM tile library
2. **`PATRIX-WORLD-SAMPLE-v0_2_5.mcpack`** (5.8 MB) — current sampler
3. **`BIGCANOPY-v2_7_1.mcaddon`** (292 KB) — current falling-tree addon
4. **`PatrixCanopyGen-v0_1_1.mcaddon`** (12 KB) — current canopy-enlarge override
5. **`bedrock-server-1.26.14.1.zip`** (~57 MB) — vanilla tree-feature JSON schemas
6. **The acacia screenshot** — user has saved an image of an acacia tree they chopped that didn't fall. Needed for acacia geometry rework planning.

##### Nice to have
7. **`Patrix_1.21.11_64x_addon.zip`** (~42 MB) — stained glass ×16, cake variants, moss_carpet_extra
8. **`Patrix_1.21.11_64x_bonus.zip`** (~10 MB) — foodcrate, tudor decorative blocks

##### DO NOT request (reference-only, already extracted)
physics-mod-pro, continuity, tectonic, distanthorizons, flowing_fluids, fluidphysics, wpo, Realistic_Fluids, FallingTree-26_1_2-25.jar, SMARTFALL, Better Foliage (BFBP+BFRP), RealSource_VV+, Alacrity, GlowingOres, LOW_RealisticJAVApack, Smooth_Plant_Animations, Waving-Plants-Shaders-Mod

---

#### PROJECT SCOPE

##### Four original research domains
1. **Java→Bedrock texture port** (Patrix as concrete case) — manifest, terrain_texture.json, flipbook_textures.json, LabPBR→MERS PBR conversion, OptiFine CTM → Bedrock approximations, biome-tint handling
2. **Emulating Java shaders via Vibrant Visuals** — lighting/atmospherics/color_grading/water/fogs JSONs, emulating Complementary/BSL/SEUS aesthetics. PS5 60fps envelope. Can do: PBR, real-time shadows, SSR, volumetric fog, bloom, SSS, water waves, colored point lights. Can't: SSGI, path tracing on PS5, custom GLSL, DOF, LUT import, cascaded shadow maps
3. **Emulating Java fluid physics mods** — custom `ff:water_finite` block with 8 level permutations via Scripting V2, pool-isolation graph, drain-when-cut-from-source. PS5 budget ~3000–6000 simulated blocks. Haubna limited to FLUIDS only (debris/cloth/ragdoll deferred indefinitely)
4. **Tectonic-inspired worldgen** — 10-biome roster (alpine_peak, alpine_meadow, coastal_bluff, river_canyon, badlands_mesa, boreal_forest, pale_hills, cherry_valley, desert_dunes, icy_cliffs). Hard ceilings: no custom dimensions, no 6D multinoise, no data-driven density functions. Tectonic-Bedrock is biome reskin + decoration on vanilla terrain, not terrain rewrite.

##### Six-phase roadmap (current status)
| Phase | Scope | Status |
|---|---|---|
| 1 | Patrix base port | **In progress** — sampler at v0.2.5 (255 shortnames, 847 PNGs, 59 variations arrays) |
| 2 | Vibrant Visuals tuning | **Unstarted** — deferred until PS5 access |
| 3 | FallingTree port | **Shipped** as BIGCANOPY v2.7.1 |
| 4 | Finite fluids v1 | **Unstarted** — research done, zero code |
| 5 | Tectonic worldgen | **Unstarted** — user flagged block variance refinement to happen WITH this phase |
| 6 | Polish (subpacks, CI, profiling) | **Unstarted** |

##### Scopes added mid-project (not in original plan)
- **PatrixCanopyGen** — new behavior pack overriding vanilla tree-feature JSONs for larger standing canopies. Shipped at v0.1.1. Jungle override still pending as v0.1.2.
- **Animated Patrix lava** — 8-frame still + 48-frame flow flipbook with blend_frames. In v0.2.1.
- **Composite pointed_dripstone shapes** — generated-from-scratch Patrix-colored tapered silhouettes (8 shapes) replacing vanilla low-res stalactites. In v0.2.5.
- **Bark variance per species** — 160 rotation-synthesized log variants (10 species × 2 faces × 8 variants). In v0.2.5.
- **grass_block_side dirt-portion variants** — 16 composites preserving Patrix grass strip, swapping dirt portion. In v0.2.5.

---

#### STRATEGIC DECISIONS (baked in)

- **PS5 primary, Android fallback.** Realms delivery.
- **"Aim for perfection, scale back to what works"** — try the most ambitious approach first, document the floor, ship fallback rather than lowering ceiling.
- **Vibrant Visuals + Experimental Voxel Shapes stay on throughout.**
- **Custom biomes** enable at Phase 5 (achievements disabled for world; explicit trade).
- **Naming discipline** — every build gets unique manifest tag `[TAG vX.Y.Z]` so user can verify in-game which loaded.
- **Block variance for worldgen blocks** (stone/dirt/etc.) is deferred to Phase 5 / Tectonic work — don't burn effort there until worldbuilding control lands.
- **Bark color mismatch on BIGCANOPY falling entity** deferred — waiting for VV on PS5 to unify entity/block lighting. Option C accepted.

---

#### CURRENT SHIPPED STATE

##### 1. PatrixWorld Sampler v0.2.5 DRIPBARK
- **File:** `PATRIX-WORLD-SAMPLE-v0_2_5.mcpack` (5.8 MB)
- **Stats:** 847 PNGs (552 variant), 255 shortnames, 59 variations arrays, 67 blocks.json entries
- **UUIDs LOCKED:** header `7b5e9f01-3a24-4b6c-9d17-8e5f4c2b19a0`, resources `f2c8d9e4-6a51-4f8b-a3c9-1d8e7b4f5c62`, `min_engine_version [1,26,0]`
- **blocks.json `format_version: 1.1.0`** (do NOT bump)
- **Variations coverage (23 surface blocks × 16 variants each, from Patrix CTM):** stone, andesite, granite, diorite, dirt, coarse_dirt, sand, red_sand, gravel, grass_block_top, mycelium_top/side, cobblestone, deepslate, end_stone, netherrack, mud, packed_mud, mud_bricks, muddy_mangrove_roots_top/side, sandstone_top, red_sandstone_top
- **v0.2.5 additions:** 16 grass_block_side composite variants, 8 dripstone_block variants, 8 pointed_dripstone shape textures, 160 bark variants (10 species × 2 faces × 8)
- **Other Patrix ports:** lava flipbook, log/plank/leaves for all 10 species, terracotta ×16, deepslate family ×5, copper oxidation ×4, all 17 ores, amethyst, ice family ×5, purpur ×3, basalt/blackstone/tuff/calcite/dripstone, soul sand/soil, glowstone/shroomlight, nether wart blocks, moss/clay/snow/bone

##### 2. BIGCANOPY v2.7.1 ACACIA
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

##### 3. PatrixCanopyGen v0.1.1 CANOPYFIX
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

#### VERSION HISTORY

##### Sampler
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

##### BIGCANOPY
| Version | Tag | Summary |
|---|---|---|
| v2.4.1→v2.6.2 | CANOPYFIX | Small canopy reshaped conic-downward, 4 canopy size tiers, strict isFallCollider, collision sweep during fall |
| v2.7.0 | NODAMAGE | Chopper NOT exempt from damage, camerashake, knockback, impact particles UNDER trunk, 43-token small-veg smasher, away-from-chopper yaw weight 5.0 |
| v2.7.1 | ACACIA | `findConnectedTree` gets speciesIdx-aware bridging pass for acacia — up to 2 air/leaf blocks between log chunks |

##### PatrixCanopyGen
| Version | Tag | Summary |
|---|---|---|
| v0.1.0 | LARGEGEN | 8 tree overrides, had bugs (oak/birch offset pushed 5th layer to trunk base on short trunks; spruce lower_offset 2-4 caused mid-trunk canopy) |
| v0.1.1 | CANOPYFIX | oak/birch offset `-3..+1` (5th layer above trunk top), spruce lower_offset reverted to vanilla 1-3 |

---

#### CRITICAL RESEARCH FINDINGS (memorize — don't re-research)

##### MCPE-165946 — partial truth
- Bug report (open since 2023): "Variations in terrain_texture.json only load first or last texture"
- Microsoft docs: variations require 1.21.110+ experimental + custom blocks with `material_instances`
- Better Foliage (2.2M downloads) uses ZERO variations arrays
- **BUT user's in-game testing of v0.2.1 + v0.2.4 confirmed variations on plain vanilla blocks (dirt, stone, sand, gravel) ARE visibly rendering multiple distinct tiles.** Research was wrong for user's platform.
- What still doesn't work reliably: `grass_block_top` variation (user confirmed this one works somehow, leave alone). Real issue was `grass_block_side` — dirt portion repeated. Fixed in v0.2.5 with 16 composite variants.
- **Practical stance:** trust user visual observation over research doc claims. Variations first; fall back to synthesis or custom-block path only if user reports no variation visible.

##### blocks.json format_version MUST be 1.1.0
- NOT 1.21.x — that's for custom block JSON files (`behaviors/blocks/*.json`), a different format
- Bedrock silently downgrades out-of-range format_version to 1.1.0 but some entries don't fully parse → mystery "Invalid or incomplete texture list" warnings
- When in doubt: 1.1.0

##### grass_block_side is an OVERLAY block in Bedrock
- Patrix `grass_block_side.png` has grass transition baked into top ~20 rows (of 64)
- Patrix also ships `grass_block_side_overlay.png` — biome-tinted green strip
- Bedrock composites overlay on top of base → changes to dirt portion work independently
- `grass_side` is legacy shortname; modern blocks.json references `grass_block_side`. Alias both.

##### Patrix CTM tile library (where authored variants live)
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

##### Patrix has PBR _n + _s maps but we haven't shipped them
- `/home/claude/patrix_ref/basic/assets/minecraft/textures/block/*_n.png` + `*_s.png`
- Vibrant Visuals on PS5 engages these automatically
- Deferred to VV tuning phase — not in any sampler build yet

##### Entity vs block lighting mismatch (bark color)
- Minecraft blocks get face-directional shading: UP ~100%, sides 60–80%, DOWN ~50%
- Entities get flat ambient lighting, no face-shading
- Same Patrix oak_log pixels (avg RGB 107,86,56) render:
  - Block side face: ~65–86 per channel (darker)
  - Entity: ~107 per channel (lighter)
- User accepted Option C — wait for VV to unify lighting, no compensation now

##### Patrix pointed_dripstone doesn't exist as PNGs
- Patrix basic only has `dripstone_block.png`
- Patrix Java uses JSON models that UV-slice dripstone_block onto pointed shapes
- Bedrock needs dedicated `pointed_dripstone_*` PNGs per shape
- v0.2.5 generated 8 shapes (base/middle/frustum/tip × up/down) from Patrix color + tapered silhouette masks. Test in-game before assuming they look right.

##### Small mushroom shortname aliases
- Register BOTH `mushroom_red`/`mushroom_brown` (legacy) AND `red_mushroom`/`brown_mushroom` (modern) pointing to same PNG. Already done.

##### Patrix stone.png is a placeholder
- Base `textures/block/stone.png` in Patrix is an "ENABLE CONNECT TEXTURE" OptiFine placeholder, NOT a real stone texture
- Real Patrix stone lives inside `optifine/ctm/patrix/stone/` (16 authored tiles)
- If you ever see stone looking wrong, suspect this

##### Legacy shortname aliases for wood
- Register both legacy (log_oak, log_big_oak, planks_big_oak, leaves_jungle etc.) AND modern (oak_log, dark_oak_log, dark_oak_planks, jungle_leaves) pointing to same PNGs
- dark_oak is "big_oak" in legacy filenames
- Already handled in v0.2.3+

---

#### WORKSPACE LAYOUT (after re-extraction)

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

#### PENDING BACKLOG (prioritized)

##### Highest priority — user has explicitly flagged

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

##### Medium priority — BIGCANOPY 14-item backlog (items NOT yet addressed)

| # | Item | Notes |
|---|---|---|
| 1 | Canopy shape matches actual tree (dynamic sizing tied to log count) | Big refactor — entity canopy is species-only currently |
| 2 | 3–5 sizes per species dynamically | Tied to #1 |
| 8 | Decelerating tail animation (wind resistance) | Tune FALL_KEYS tail 0.956→1.0 to 1.05→1.0→0.92 ease-out |
| 9 | Giant mushroom felling (new species for red/brown_mushroom_block + mushroom_stem) | |
| 11 | 2×2 trunk entity geometry for mega jungle + dark_oak | User noted single-line trunk for wider trees |
| 13 | Slope-aware rest angle (lie flat with terrain) | Previously shelved, user un-shelved |

##### Sampler texture expansion
- Stripped logs for all 10 species (not yet ported)
- Wood (6-face log) variants
- Beds, banners, concrete colors, concrete_powder, wool colors, glazed terracotta ×16, candles, sculk family, froglights, chiseled variants, stairs/slabs (if different from base)
- Patrix addon pack: stained glass ×16, cake variants, moss_carpet_extra, seagrass_extra
- Patrix bonus pack: foodcrate, tudor blocks

##### Lower priority / deferred
- Vibrant Visuals tuning pack (Phase 2) — unblocked by PS5 access
- Finite fluids (Phase 4) — big scripting project
- Full Patrix port (Phase 1) — 30k files, after sampler validates
- Phase 6 polish — subpack tiers, CI versioning, frame profiling

---

#### PACKAGING CONVENTIONS

##### Sampler — single `.mcpack`
```bash
cd /home/claude/patrix_world_pack
zip -qr /mnt/user-data/outputs/PATRIX-WORLD-SAMPLE-v0_X_Y.mcpack \
  manifest.json blocks.json pack_icon.png textures/
```

##### BIGCANOPY — `.mcaddon` with nested BP + RP mcpacks
```bash
cd /home/claude/bigcanopy/extracted
cd BP && zip -qr /tmp/bigcanopy_bp.mcpack . && cd ..
cd RP && zip -qr /tmp/bigcanopy_rp.mcpack . && cd ..
(cd /tmp && zip -qj BIGCANOPY-v2_X_Y.mcaddon bigcanopy_bp.mcpack bigcanopy_rp.mcpack)
cp /tmp/BIGCANOPY-v2_X_Y.mcaddon /mnt/user-data/outputs/
```

##### PatrixCanopyGen — `.mcaddon` with single BP
```bash
cd /home/claude/patrixcanopygen
zip -qr /tmp/canopygen_bp.mcpack manifest.json pack_icon.png features/
(cd /tmp && zip -qj PatrixCanopyGen-v0_X_Y.mcaddon canopygen_bp.mcpack)
cp /tmp/PatrixCanopyGen-v0_X_Y.mcaddon /mnt/user-data/outputs/
```

##### Every deliverable
- Validate JSON: `python3 -c "import json; json.load(open('path'))"` on every .json
- Delete superseded version from `/mnt/user-data/outputs/` (avoid user confusion)
- Call `present_files` with all 3 current deliverables
- Mention what to test in-game
- Note what was INTENTIONALLY deferred so user knows it wasn't forgotten

---

#### USER CONVENTIONS & TONE

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

#### FIRST RESPONSE TEMPLATE

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


**<<< END ARCHIVED DOCUMENT >>>**

---

### §0.3 — Handoff v2 (v0.2.5 era predecessor)

*Full document, uploaded by user. Superseded by v3 but preserved for completeness.*

**<<< BEGIN ARCHIVED DOCUMENT >>>**

### PatrixWorld + BIGCANOPY + PatrixCanopyGen — Full Project Handoff (v2)

Resuming a Minecraft Bedrock 1.26.x modding project. Previous chat hit context limit. This document is authoritative — it supersedes the v1 handoff. Read it fully before responding.

---

#### TURN 1 — WHAT TO DO FIRST

1. Acknowledge this handoff briefly. Do NOT restate it.
2. **Ask the user to upload the files listed in the UPLOADS REQUEST section below.** These must be re-uploaded because prior session files rolled off disk.
3. Wait for uploads and the specific **acacia-didn't-fall screenshot** before starting any work.
4. **Follow the NEW PROCESS RULE:** ask clarifying questions BEFORE every build. Outline what you'll change, what tradeoffs exist, what you're leaving alone — wait for the user's green light. No "fire and check" iterations.

---

#### NEW PROCESS RULE (critical, added mid-project)

The user added this rule explicitly: **no builds without a plan-first discussion.** Every iteration starts with:

1. Outline what you intend to change
2. Note tradeoffs / what stays as-is
3. Wait for green light (or additional direction)
4. Then build

This catches wrong assumptions early. Do not skip it. The user will tell you "yes" or add constraints, then you build.

Investigation/diagnostic work (reading files, computing pixel averages, comparing hashes) is fine without asking — just don't write output files or bump manifests until you've confirmed the plan.

---

#### UPLOADS REQUEST

At start of chat, ask the user to upload these. Be concise (abbreviated list, not full explanation):

##### Critical — blocks everything
1. **`Patrix_1.21.11_64x_basic.zip`** (~198 MB) — primary Patrix Java source. Contains 3056 block PNGs at 64×64 + the OptiFine CTM tile library we rely on heavily for block variants.
2. **`PATRIX-WORLD-SAMPLE-v0_2_5.mcpack`** — current shipped sampler (our last build). Your starting point for sampler iteration.
3. **`BIGCANOPY-v2_7_1.mcaddon`** — current shipped tree-falling addon. Your starting point for BIGCANOPY iteration.
4. **`PatrixCanopyGen-v0_1_1.mcaddon`** — current shipped worldgen tree-size override.
5. **`bedrock-server-1.26.14.1.zip`** (~57 MB) — Bedrock Dedicated Server. Its `behavior_packs/vanilla_1.21.40/features/` folder contains authoritative vanilla tree-feature JSONs needed for PatrixCanopyGen iteration.
6. **The acacia screenshot** — user has a specific screenshot showing an acacia tree they chopped that did NOT fall. Critical reference for the acacia geometry/detection rework that's pending.

##### Probably needed for next phases
7. **`Patrix_1.21.11_64x_addon.zip`** (~42 MB) — stained glass (all 16 colors), cake variants, moss_carpet_extra, seagrass_extra.
8. **`Patrix_1.21.11_64x_bonus.zip`** (~10 MB) — foodcrate.png, tudor1/2.png, misc niche textures.

##### Reference material — DO NOT request
The user has uploaded these previously; reference content has been extracted. Don't ask again:
- physics-mod-pro (all variants), continuity, tectonic, distanthorizons
- flowing_fluids, fluidphysics, wpo, Realistic_Fluids JARs
- FallingTree-26_1_2-25.jar, SMARTFALL-v2_4_0.mcaddon
- BFBP1.5.mcpack + BFRP1.5.mcpack (Better Foliage; inspection done)
- RealSource_VibrantVisuals_PLUS_2.0.zip (future VV tuning reference)
- Smooth_Plant_Animations, Waving-Plants-Shaders-Mod, Alacrity, GlowingOres-RealisticRTXpack, LOW_RealisticJAVApack

---

#### PROJECT SCOPE — THE FOUR DOMAINS (original research)

##### Domain 1 — Java → Bedrock texture pack port, Patrix case
Manifest authoring, terrain_texture.json / item_texture.json / flipbook_textures.json assembly, LabPBR 1.3 → Bedrock MERS channel conversion, DirectX vs OpenGL normal map convention, OptiFine CTM → Bedrock approximations, biome-tinted foliage handling, sound definition translation, .mcpack/.mcaddon packaging, Realms deployment.

##### Domain 2 — Emulating Java shaders (Complementary / BSL / SEUS) via Vibrant Visuals
Full JSON authoring: `lighting/global.json`, `atmospherics/*.json`, `color_grading/*.json`, `water/water.json`, `fogs/*.json`, `shadows/global.json`, `local_lighting/local_lighting.json`, `cubemaps/*.json`. What Bedrock VV can do (PBR, real-time shadows, SSR, volumetric fog, atmospheric scattering, bloom, tone mapping, color grading, subsurface scattering, water waves/caustics, colored point lights). What it can't (SSGI, path tracing on PS5, custom GLSL, DOF, LUT import, cascaded shadow maps). PS5 60 FPS performance envelope.

##### Domain 3 — Emulating Java fluid physics mods
Research of Haubna Physics Mod, flowing_fluids, wpo, Realistic Fluids. Design for a custom `ff:water_finite` block with 8 level permutations, Bedrock Scripting V2 tick loop (`minecraft:tick[10,14]` callbacks), pool-isolation graph via runJob generators, drain-when-cut-from-source logic. Ocean waves via VV image displacement. Swim visuals (splash, ripples, wake). Realms budget: ~3000–6000 simulated water blocks on PS5. Haubna scope limited to FLUIDS only (debris/cloth/ragdoll deferred indefinitely).

##### Domain 4 — Tectonic-inspired worldgen in Bedrock
Custom biome JSONs with `minecraft:climate`, `minecraft:surface_builder`, `minecraft:surface_material_adjustments`, `minecraft:mountain_parameters`, `minecraft:replace_biomes`. 10-biome "Tectonic-Bedrock" roster: alpine_peak, alpine_meadow, coastal_bluff, river_canyon, badlands_mesa, boreal_forest, pale_hills, cherry_valley, desert_dunes, icy_cliffs. Custom features (twisted-pine trees, rock outcrops, wildflowers). Hard ceilings acknowledged: no custom dimensions, no 6D multinoise for custom biomes, no data-driven density functions. Tectonic-Bedrock is a biome reskin + decoration layer on vanilla terrain shape.

##### SIX-PHASE ROADMAP (original plan, we've diverged)
| Phase | Scope | Status |
|---|---|---|
| 1 | Patrix base port | **In progress** — sampler at v0.2.5, ~234+ shortnames, ~850 PNGs. Not yet at full-pack level but well past the minimal-sampler validation |
| 2 | Vibrant Visuals tuning | Unstarted (paused until PS5 access) |
| 3 | FallingTree port | **Shipped** as BIGCANOPY v2.7.1 ACACIA |
| 4 | Finite fluids v1 | Unstarted (research done, zero code) |
| 5 | Tectonic-Bedrock worldgen | Unstarted (research done, zero code) |
| 6 | Polish (subpacks, CI, profiling) | Unstarted |

##### ADDITIONAL SCOPES added mid-project (not in original plan)
- **PatrixCanopyGen** (NEW): behavior pack overriding vanilla tree-feature JSONs to produce larger standing canopies. Shipped at v0.1.1 CANOPYFIX, 8 species overrides. Jungle override still pending as v0.1.2.
- **Animated Patrix lava** (flipbook): 8-frame `lava_still` + 48-frame `lava_flow` with blend_frames. Ported in v0.2.1.
- **Composite pointed_dripstone shapes**: generated from-scratch Patrix-colored tapered silhouettes for 8 shape variants (base/middle/frustum/tip × up/down), replacing vanilla low-res stalactites. Added in v0.2.5.
- **Bark variance per species**: 8 rotation-synthesized variants per log side + end-grain for all 10 species. Added in v0.2.5.
- **grass_block_side dirt-portion variants**: 16 composite variants preserving Patrix grass strip, swapping dirt portion with 16 different Patrix dirt CTM tiles. Added in v0.2.5.

---

#### STRATEGIC DECISIONS BAKED IN

- **PS5 primary, Android fallback.** Realms delivery.
- **"Aim for perfection, scale back to what works"** — always try the most ambitious approach first; document the floor and ship fallback when needed rather than lowering the ceiling.
- **Vibrant Visuals + Experimental Voxel Shapes stay on throughout.**
- **Custom biomes** will enable in Phase 5 (achievements disabled for world; explicit trade).
- **Naming discipline:** every build gets a unique manifest tag `[TAG vX.Y.Z]` so the user can verify in-game which version loaded.
- **Block variance for world-gen blocks** (stone/dirt/etc.) is DEFERRED to Phase 5 / tectonic work. Don't pour effort into this area until worldbuilding control lands.
- **Bark color mismatch on BIGCANOPY falling entity** is DEFERRED — waiting for Vibrant Visuals on PS5 to unify entity/block lighting. Option C chosen (no compensation now).

---

#### WHAT'S SHIPPED — CURRENT STATE

##### 1. PatrixWorld Sampler v0.2.5 DRIPBARK
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

##### 2. BIGCANOPY v2.7.1 ACACIA
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

##### 3. PatrixCanopyGen v0.1.1 CANOPYFIX
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

#### VERSION HISTORY (comprehensive, every iteration)

##### Sampler
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

##### BIGCANOPY
| Version | Tag | Summary |
|---|---|---|
| v2.4.1→v2.6.2 | CANOPYFIX | Small canopy reshaped conic-downward, 4 canopy size tiers, strict isFallCollider, collision sweep during fall |
| v2.7.0 | NODAMAGE | Chopper NOT exempt from damage (all players in corridor take 5♥), camerashake, knockback, impact particles UNDER trunk (stump.y-0.05), 43-token small-veg smasher, away-from-chopper yaw weight 5.0, toward-player veto -0.3 |
| v2.7.1 | ACACIA | `findConnectedTree` extended with speciesIdx-aware bridging pass for acacia — traverses up to 2 air/leaf blocks between log chunks |

##### PatrixCanopyGen
| Version | Tag | Summary |
|---|---|---|
| v0.1.0 | LARGEGEN | 8 tree overrides shipped then replaced (had oak/birch offset bug pushing 5th layer to trunk base on short trunks; spruce lower_offset 2-4 caused mid-trunk canopy) |
| v0.1.1 | CANOPYFIX | oak/birch offset `-3..+1` (5th layer above trunk top), spruce lower_offset reverted to vanilla 1-3 |

---

#### CRITICAL RESEARCH FINDINGS (memorize; don't re-research)

##### MCPE-165946 variations bug — PARTIAL TRUTH
- Bug report (open since 2023): "When adding texture variations with a resource pack via terrain_texture.json only the first or last texture loads."
- Microsoft docs: variations require 1.21.110+ experimental + custom blocks with `material_instances`.
- Fused Bolt Better Foliage (2.2M downloads) uses ZERO variations arrays.
- **HOWEVER: user's in-game testing of v0.2.1 + v0.2.4 confirmed that variations on plain vanilla blocks (dirt, stone, sand, gravel) ARE visibly rendering multiple distinct tiles** — at least on current Bedrock as of test date. Research was not fully correct for this platform.
- What still doesn't work reliably: grass_block_top variation. User observed this varied, then said the broader issue was grass_block_side (dirt portion under grass).
- Practical stance: **trust user visual observation over research doc claims**. Try variations first; fall back to synthesis/custom-block path only if user reports no variation visible.

##### blocks.json format_version must be 1.1.0
- Not 1.21.x — that's for individual custom block JSON files (`behaviors/blocks/*.json`), a DIFFERENT file format
- Bedrock silently downgrades out-of-range format_version to 1.1.0 but some entries don't fully parse → mystery "Invalid or incomplete texture list" warnings
- When in doubt, leave it at 1.1.0

##### grass_block_side is an OVERLAY block in Bedrock
- Patrix `grass_block_side.png` has grass transition BAKED into top ~20 rows (of 64)
- Patrix also ships `grass_block_side_overlay.png` (1007 of 4096 pixels opaque = top 25%) — the biome-tinted green strip
- Bedrock composites overlay on top of base, so changes to the dirt portion work independently
- `grass_side` is the legacy shortname; modern blocks.json references `grass_block_side`. Alias both in terrain_texture.json.

##### Patrix CTM tile library — where authored variants live
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

##### Patrix has OK `_n` normal + `_s` specular PBR maps but we haven't shipped them
- All surface blocks' PBR maps sit in `/home/claude/patrix_ref/basic/assets/minecraft/textures/block/*_n.png` + `*_s.png`
- Vibrant Visuals on PS5 will engage these automatically when shipped
- Currently not included in any sampler build — deferred to VV tuning phase

##### Entity vs block lighting mismatch (bark color issue)
- Minecraft blocks get face-directional shading: UP 100%, sides 60–80%, DOWN 50%
- Entities get flat ambient lighting, no face-shading
- Same Patrix `oak_log` texture (avg RGB 107,86,56) renders:
  - Standing block side face: ~65–86 per channel (darker)
  - Falling entity: ~107 per channel (lighter)
- User accepted Option C: **wait for VV to unify lighting**, don't compensate texture now
- No fix planned until PS5 + VV testing begins

##### Patrix pointed_dripstone doesn't exist as PNGs
- Patrix basic has only `dripstone_block.png` (+_n +_s)
- Patrix Java uses JSON models that UV-slice the dripstone_block texture onto pointed shapes
- Bedrock needs dedicated `pointed_dripstone_*` PNGs per shape
- **v0.2.5 generated 8 shape textures** (base/middle/frustum/tip × up/down) from Patrix dripstone color + tapered silhouette masks. Test these in-game before assuming they look right.

##### Small mushroom shortname aliases needed
- Shortnames `mushroom_red` / `mushroom_brown` (legacy) and `red_mushroom` / `brown_mushroom` (modern) must both be registered pointing to same PNG — Bedrock's lookup path depends on which name the flora block internally uses
- Already done in v0.2.1+

---

#### WORKSPACE DIRECTORY LAYOUT

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

#### PENDING BACKLOG (prioritized)

##### Highest priority — user has explicitly flagged

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

##### Medium priority

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

##### Low priority / deferred

6. **Vibrant Visuals tuning pack** (Phase 2) — unblocked by PS5 access
7. **Finite fluids Phase 4** — big scripting project
8. **Full Patrix port Phase 1** — 30k files, after sampler fully validated
9. **Phase 6 polish** — subpack tiers, CI versioning, frame profiling

---

#### BUILD / PACKAGING CONVENTIONS

##### Sampler
- Single `.mcpack`:
  ```bash
  cd /home/claude/patrix_world_pack
  zip -qr /mnt/user-data/outputs/PATRIX-WORLD-SAMPLE-v0_X_Y.mcpack manifest.json blocks.json pack_icon.png textures/
  ```

##### BIGCANOPY — nested `.mcaddon` (zip of zips)
```bash
cd /home/claude/bigcanopy/extracted
cd BP && zip -qr /tmp/bigcanopy_bp.mcpack . && cd ..
cd RP && zip -qr /tmp/bigcanopy_rp.mcpack . && cd ..
(cd /tmp && zip -qj BIGCANOPY-v2_X_Y.mcaddon bigcanopy_bp.mcpack bigcanopy_rp.mcpack)
cp /tmp/BIGCANOPY-v2_X_Y.mcaddon /mnt/user-data/outputs/
```

##### PatrixCanopyGen — `.mcaddon` containing single BP
```bash
cd /home/claude/patrixcanopygen
zip -qr /tmp/canopygen_bp.mcpack manifest.json pack_icon.png features/
(cd /tmp && zip -qj PatrixCanopyGen-v0_X_Y.mcaddon canopygen_bp.mcpack)
cp /tmp/PatrixCanopyGen-v0_X_Y.mcaddon /mnt/user-data/outputs/
```

##### After packaging
- Always validate JSON: `python3 -c "import json; json.load(open('path'))"` on every .json
- Delete superseded version from `/mnt/user-data/outputs/` to avoid user confusion
- Call `present_files` tool with all three current deliverables
- Mention what to test in-game
- Note anything NOT in scope for that iteration (so user knows what was intentionally deferred)

---

#### USER CONTEXT & CONVENTIONS

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

#### FIRST-RESPONSE TEMPLATE (example)

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


**<<< END ARCHIVED DOCUMENT >>>**

---

### §0.4 — NON_PATRIX_TEXTURES.md (v0.4.0 texture-source audit)

*Documents which textures in v0.4.0 come from non-Patrix sources (Alacrity, Faithful, Hyper Realistic Sky, synthesized variants). Relevant when auditing texture provenance or planning Patrix replacement.*

**<<< BEGIN ARCHIVED DOCUMENT >>>**

### PatrixWorld v0.4.0 — Non-Patrix Texture Audit

Document of every sampler texture not sourced from Patrix directly. User directive: recreate these in Patrix style for full aesthetic consistency when time permits.

Generated: 2026-04-18 — after v0.4.0 "Patrix-everywhere swap" (sheep/zombie/phantom reverted to Patrix).

---

#### Category 1 — Villager System (Alacrity-sourced)

**Reason**: Patrix ships no villager textures anywhere — 64x basic, 128x basic, and 128x mobs all lack villager textures. We use Alacrity (128×128 Bedrock-vanilla UV) for the full layered system.

**What to recreate in Patrix style:**

##### Base villagers
- `textures/entity/villager2/villager.png` (128×128 base body)
- `textures/entity/villager2/villager2.png` (alt base)
- `textures/entity/villager2/villager3.png` (alt base)
- `textures/entity/villager2/villager_baby.png` (baby variant)
- `textures/entity/villager2/hair.png` (hair overlay)
- `textures/entity/villager.png` (top-level fallback, duplicate of villager2/villager.png)

##### Profession overlays (14 overlays + base)
- `textures/entity/villager2/profession/armorer.png`
- `textures/entity/villager2/profession/butcher.png`
- `textures/entity/villager2/profession/cartographer.png`
- `textures/entity/villager2/profession/cleric.png`
- `textures/entity/villager2/profession/farmer.png`
- `textures/entity/villager2/profession/fisherman.png`
- `textures/entity/villager2/profession/fletcher.png`
- `textures/entity/villager2/profession/leatherworker.png`
- `textures/entity/villager2/profession/librarian.png`
- `textures/entity/villager2/profession/mason.png`
- `textures/entity/villager2/profession/nitwit.png`
- `textures/entity/villager2/profession/shepherd.png`
- `textures/entity/villager2/profession/toolsmith.png`
- `textures/entity/villager2/profession/weaponsmith.png`

##### Profession level overlays (5 tiers, both naming conventions)
- `textures/entity/villager2/profession_level/stone.png`
- `textures/entity/villager2/profession_level/iron.png`
- `textures/entity/villager2/profession_level/gold.png`
- `textures/entity/villager2/profession_level/emerald.png`
- `textures/entity/villager2/profession_level/diamond.png`
- `textures/entity/villager2/levels/level_stone.png` (Faithful naming convention)
- `textures/entity/villager2/levels/level_iron.png`
- `textures/entity/villager2/levels/level_gold.png`
- `textures/entity/villager2/levels/level_emerald.png`
- `textures/entity/villager2/levels/level_diamond.png`

##### Type/biome overlays (7 biomes, both naming conventions)
- `textures/entity/villager2/type/plains.png`
- `textures/entity/villager2/type/desert.png`
- `textures/entity/villager2/type/jungle.png`
- `textures/entity/villager2/type/savanna.png`
- `textures/entity/villager2/type/snow.png`
- `textures/entity/villager2/type/swamp.png`
- `textures/entity/villager2/type/taiga.png`
- `textures/entity/villager2/biomes/biome_plains.png` (Faithful naming)
- `textures/entity/villager2/biomes/biome_desert.png`
- `textures/entity/villager2/biomes/biome_jungle.png`
- `textures/entity/villager2/biomes/biome_savanna.png`
- `textures/entity/villager2/biomes/biome_snow.png`
- `textures/entity/villager2/biomes/biome_swamp.png`
- `textures/entity/villager2/biomes/biome_taiga.png`

##### Zombie Villager — full layered system (Alacrity-sourced)
Everything under `textures/entity/zombie_villager2/` follows the same structure as villager2 above. Replace analogously.

**Total villager textures to recreate: 42 files × 2 (villager + zombie_villager) = 84 files**

---

#### Category 2 — Squid + Glow Squid (Alacrity-sourced)

**Reason**: Patrix ships no squid or glow_squid textures in any pack.

- `textures/entity/squid.png` (128×64, Alacrity)
- `textures/entity/glow_squid.png` (128×64, Alacrity — if present)

**Total: 2 files**

---

#### Category 3 — Environment Textures (Hyper Realistic Sky-sourced)

**Reason**: Patrix doesn't ship sky/weather textures. We used Hyper Realistic Sky v3.8 by UsernameGeri for the sun, moon, clouds, rain, snow. Not Patrix aesthetic but unavoidable — no Patrix sky alternative exists.

- `textures/environment/sun.png`
- `textures/environment/moon_phases.png`
- `textures/environment/clouds.png`
- `textures/environment/rain.png`
- `textures/environment/snow.png`
- `textures/environment/celestial/moon/new_moon.png`
- `textures/environment/celestial/moon/waxing_crescent.png`
- `textures/environment/celestial/moon/first_quarter.png`
- `textures/environment/celestial/moon/waxing_gibbous.png`
- `textures/environment/celestial/moon/full_moon.png`
- `textures/environment/celestial/moon/waning_gibbous.png`
- `textures/environment/celestial/moon/third_quarter.png`
- `textures/environment/celestial/moon/waning_crescent.png`
- `textures/environment/celestial/sun.png`
- `textures/environment/celestial/end_flash.png`
- `textures/environment/colormap/fog0.png`

**Total: 16 files**

---

#### Category 4 — Synthesized variants (derived from Patrix)

These are algorithmically derived from Patrix sources via rotation / hue-shift / brightness / vertical-shift / horizontal-shift. They preserve the Patrix aesthetic but aren't direct copies — you may want to re-author some by hand for natural variation rather than mathematical.

##### Log top variants (112 files)
- `oak_log_top_v0` through `_v7` through legacy alias `log_top_oak_v0` through `_v7`
- Same for birch, spruce, jungle, acacia, dark_oak (big_oak legacy), cherry, mangrove
- 8 woods × 8 variants × 2 naming (modern+legacy) = 112 files (some overlap)

##### Log side variants beyond v0-v7 (80 files)
- `oak_log_v8` through `_v11` — 8 existing woods × 4 = 32 synthesized
- `bamboo_block_v0-v11`, `pale_oak_log_v0-v11`, `crimson_log_v0-v11`, `warped_log_v0-v11` — 4 new woods × 12 = 48 from scratch

##### Stripped log variants (220 files)
- All 11 woods (oak, spruce, birch, jungle, acacia, dark_oak, cherry, mangrove, pale_oak, crimson, warped)
- Each: 12 side variants + 8 top variants = 20 per wood × 11 = 220

##### Plank variants (72 files)
- 12 woods × 6 joint-offset variants each

##### Smooth/polished material synthetic variants
- `smooth_stone_v0-v7`, `smooth_sandstone_v0-v7`, `smooth_red_sandstone_v0-v7`, `smooth_quartz_v0-v7`
- `basalt_top_v0-v5`, `polished_basalt_top_v0-v5`
- `polished_andesite_v0-v7`, `polished_diorite_v0-v7`, `polished_granite_v0-v7`, `polished_deepslate_v0-v7`, `polished_tuff_v0-v7`, `tuff_bricks_v0-v7`
- `end_bricks_v0-v7`, `chiseled_stone_bricks_v0-v5`
- `polished_blackstone_v0-v7`, `polished_blackstone_bricks_v0-v7`, `cracked_polished_blackstone_bricks_v0-v7`, `chiseled_polished_blackstone_v0-v5`
- `chiseled_nether_bricks_v0-v5`, `cracked_nether_bricks_v0-v7`
- `red_nether_brick_v0-v7`

**Total synthetic variants: approximately 485 files**

These hold up algorithmically but if you want them to look hand-authored-varied (each tree has unique authored grain rather than color-shifted duplicates), they'd need manual re-creation.

---

#### Category 5 — 100% Patrix-Sourced (NO action needed)

Everything else in the sampler — which is the vast majority:
- All block textures (2,000+ PNGs)
- All log side v0-v7 for existing woods (direct Patrix CTM-derived)
- All vegetation variants (leaves, flowers, bushes, vines, grass, cactus, kelp, seagrass, lily_pad, saplings, etc.)
- All mob textures except those listed in Categories 1-2
  - Including sheep/sheep_wool/sheep_wool_undercoat (Patrix 64 basic, swapped back this turn)
  - phantom.png (Patrix 64 basic, swapped back this turn)
  - zombie/zombie.png, zombie/drowned.png, zombie/husk.png (Patrix 64, swapped back this turn)
  - cat breeds, chicken biome variants, cow biome variants (Patrix 128 mobs scaled 50% to 64x)
  - copper_golem, creaking, breeze (Patrix 128 mobs scaled)

---

#### Summary Counts

| Category | Files to recreate |
|----------|-------------------|
| Villager system (both villager + zombie_villager) | ~84 |
| Squid + glow_squid | 2 |
| Environment (Hyper Sky) | 16 |
| Synthesized variants (Patrix-derived, optional re-authoring) | ~485 |
| **Hard requirements (Categories 1-3)** | **~102 files** |
| **Optional re-authoring (Category 4)** | **~485 files** |

---

#### How to prioritize

If recreating in priority order for v1.0:
1. **Villager base + main professions** (farmer, librarian, cleric) — highest visibility NPCs
2. **Environment sun/moon/clouds** — constantly visible sky
3. **Squid** — low priority, underwater and minimal
4. **Villager biome types + levels** — subtle variation, lower impact
5. **Zombie villager parallel** — even lower impact
6. **Synthesized block variants** — optional polish; the math-generated ones already look reasonable

#### Source Locations (for reference)

Current non-Patrix sources:
- Alacrity: `/refpacks/alacrity/assets/minecraft/textures/entity/`
- Hyper Realistic Sky v3.8: `/mods_round3/hyper_sky/assets/minecraft/textures/environment/`
- Faithful R13 naming (for villager2/levels alias paths): `/uploads_all/faithful_64_r13/textures/entity/villager2/`


**<<< END ARCHIVED DOCUMENT >>>**

---

## 1. First actions on resume

Before writing anything:

1. Read this entire document.
2. Check `/mnt/transcripts/` for prior session transcripts and `journal.txt` for their catalog. Don't read all transcripts — read the most recent and reference others only for specific questions.
3. Verify the user has re-uploaded the component assets. Expected uploads when session resumes:
   - `Unified-Abs0lut-Claude-v{latest}.mcaddon` (current build, rollback target)
   - Patrix 128x source packs (`Patrix_1_21_11_128x_*.zip`) — the 5 files, each 26 MB to 487 MB
   - `bedrock-server-1_26_14_1.zip` (for vanilla entity JSON references)
   - `Alacrity.zip` (Bedrock-native UV reference)
   - The four current standalone packs: Sampler v0.4.0 `.mcpack`, BIGCANOPY v2.8.1 `.mcaddon`, PatrixCanopyGen v0.1.2 `.mcaddon`, PatrixWorld-Tectonic v0.7.2 `.mcaddon`
4. Ask the user what the next iteration target is before building. **Do not write files without a plan-first discussion** (user process rule, see §3).

---

## 2. Project identity

**Name**: PatrixWorld (umbrella) → current unified deliverable: `Unified-Abs0lut-Claude-v{X}.mcaddon`  
**Platform primary**: Minecraft Bedrock 1.26.x on **PlayStation 5**  
**Platform secondary**: Android mobile  
**Delivery**: Realms world the user loads the unified `.mcaddon` into  
**Engine settings user keeps on**: Vibrant Visuals (VV) + Experimental Voxel Shapes  
**min_engine_version**: `[1, 26, 0]` across all packs we author  
**User role**: sole developer and sole tester. Targets eventual commercial release. Nothing in scope should compromise sellability.

**Aesthetic doctrine**: "Patrix everywhere." Where Patrix has a texture, we use it. Alacrity fills gaps (Bedrock-native UV layouts). User values Patrix's visual fidelity above perfect UV correctness — they explicitly accepted known UV bugs to keep Patrix quality.

**Scope spans four original research domains** (from prior session handoffs):
1. Java→Bedrock texture port (Patrix as concrete case)
2. Vibrant Visuals shader emulation (lighting/atmospherics/water/fogs JSON authoring)
3. Emulated fluid physics (deferred — `ff:water_finite` block via Scripting v2)
4. Tectonic-style worldgen (biome reskin + decoration, not terrain rewrite)

---

## 3. User process rules (non-negotiable)

1. **Plan first, build second.** Every iteration: outline what will change, note tradeoffs, note what's untouched, **wait for green light**, then build. Skipping this is a regression.
2. **Investigation/diagnostics don't need approval.** Reading files, computing hashes, comparing pixels — fine without asking. Only writing output files, modifying source, or bumping manifests requires the plan-first exchange.
3. **User answers numbered questions in order.** If you ask 6 questions, expect 6 answers. If answers seem to miss some, re-check — you probably mis-parsed.
4. **Scale back ambition when uncertain.** Propose the ambitious approach, note failure modes, ship the fallback if it fails. Don't lower the ceiling preemptively.
5. **Believe user observations over research docs.** They test on real hardware. "Research says X" loses to "I saw Y in-game." Own being wrong.
6. **Every iteration gets a distinct manifest tag** so they can verify in-game which version loaded. Format: `[TAG vX.Y.Z]` in manifest.header.name.
7. **Each iteration produces a paired deliverable**: the `.mcaddon/.mcpack` + a per-iteration handoff MD + this continuity doc. All three land in `/mnt/user-data/outputs/`.
8. **Each iteration bumps version**. Never ship two builds with the same version string.
9. **Deferred ≠ forgotten**. When something gets pushed to "later," list it in §11 so it resurfaces.

---

## 4. Chronological iteration history (append-only)

### Pre-unification (prior sessions, summarized from transcripts)

- **PatrixWorld Sampler** grew v0.1.1 → v0.2.7 → v0.3.x → v0.4.0 across many iterations. v0.4.0 "PAT+ALAC BLEND" is the shipped RP with 3206 PNGs, 225 `blocks.json` entries, 961 `terrain_texture` shortnames, 279 variations arrays. Declared `"capabilities": ["pbr"]`. This is the current baseline.
- **BIGCANOPY** (custom falling-tree behavior pack) shipped v1.2.0 → v2.8.1. Current is v2.8.1 VV TEST RUN. Scripted falling-tree entity `ft:falling_tree` with species-specific geometries, fall animations, impact effects, vegetation smashing.
- **PatrixCanopyGen** (tree feature overrides for larger standing canopies) shipped v0.1.0 → v0.1.2. Current is v0.1.2. BP-only.
- **PatrixWorld-Tectonic** (biome reskin + per-biome water profiles) shipped v0.7.1 → v0.7.2. Current is v0.7.2. 4 per-biome water profiles (alpine, cherry, desert, forest) confirmed working.

### Haiku 4.5 era (same conversation, earlier turns) — **discarded, documented so not redone**

A Claude Haiku instance generated **10,320 texture files** across 43 species, 16 variants each, 5 resolution tiers. All architecturally broken:
- Filenames `zombie_000001.png` through `zombie_000016.png` don't match any Bedrock convention; would not display in-game
- "16 variants" were saturation/brightness tweaks of the same source (no genuine visual difference)
- "5 resolution tiers" via pack.mcmeta dropdown is a Java Edition feature; Bedrock uses native subpacks (slider UI)
- PBR maps as `_n.png` / `_s.png` follow LabPBR convention; Bedrock VV uses MER (`_mer.png`) + `_normal.png` + `.texture_set.json` sidecar

**Salvage result**: 41 of 43 species' "variant 1" files were pixel-identical to Patrix source (PIL re-encoding, no content change). The only meaningfully-different file was a Haiku zombie Patrix/Alacrity composite — architecturally questionable (Alacrity 128×128 upscaled 4× with Patrix blended 30%). Archived for reference, not reused.

**Archived at** `/home/claude/_reference_archive/` (see §6): 1 zombie composite + 86 LabPBR maps + README.

**Outputs deleted**: `PATRIX-WORLD-v0_4_1-ZOMBIE-TEST.mcpack`, `PATRIX-WORLD-v0_5_0-COMPLETE.mcpack` (both inert).  
**Outputs kept**: `CREATURE_CUSTOMIZATION_GUIDE.md`, `MINECRAFT_ANIMAL_INVENTORY.md`, `PATRIXWORLD-TESTING-GUIDE.md` (docs have content value despite flawed implementation premise).

### v0.5.0 (Turn 1 of unification) — Infrastructure scaffold

- Built `Unified-Abs0lut-Claude-v0.5.0.mcaddon` (34 MB) bundling 8 `.mcpack` files: the 6 existing packs unchanged + 2 new `pw_variants` BP+RP scaffolds.
- New UUIDs locked for `pw_variants` (see §7).
- `pw_variants` BP at v0.1.0 has: manifest + empty `entities/` + `scripts/main.js` stub that logs `[pw_variants] scaffold v0.1.0 loaded`. Declares `@minecraft/server` v2.0.0 dependency, both `data` and `script` modules.
- `pw_variants` RP at v0.1.0 has: manifest + empty `entity/` + empty `render_controllers/` + empty `textures/entity/`. Solid-color placeholder pack icon.
- All 18 UUIDs across 8 packs verified unique. All manifest.json files validated.
- Handoff doc: `UNIFIED_PACK_HANDOFF.md` (overwrite style — this was before the per-iteration naming convention started).

### v0.5.1-ZOMBIE-PROOF (Turn 2) — First working variant mob

- `pw_variants` BP bumped 0.1.0 → 0.1.1:
  - Added `entities/zombie.json` (BDS `vanilla_1.26.0/entities/zombie.json` verbatim + `pw:variant` int property added, range 0–15, `client_sync: true`).
  - Updated `scripts/main.js` to subscribe to `world.afterEvents.entitySpawn` and call `entity.setProperty("pw:variant", Math.floor(Math.random()*16))` for identifier `minecraft:zombie`.
  - Keeps `VARIANT_SPECIES` JS dict as the registration point for future species. Adding a mob = one dict entry + corresponding entity JSON + RP assets.
- `pw_variants` RP bumped 0.1.0 → 0.1.1:
  - Added `entity/zombie.entity.json` — full vanilla zombie client entity (format 1.26.0, 186-line canonical from ZtechNetwork MCB Vanilla Resource Pack mirror) preserving all scripts/animations/animation_controllers/enable_attachables, with `textures` extended to 16 `variant_N` slots, and `render_controllers` replaced with `["controller.render.pw_zombie"]`.
  - Added `render_controllers/pw_zombie.render.json` — controller selects texture via molang ternary: `query.is_baby ? Texture.baby : Array.variants[math.clamp(query.property('pw:variant'), 0, 15)]`.
  - Added 5 textures in `textures/entity/zombie/`: `zombie_v0..v3.png` (4 distinct, 256×256) and `zombie_baby.png` (fallback copy of v0 — no baby source in any uploaded pack).
- Slot mapping (per user directive, 4 distinct variants padded to 16 slots):

  | variant index | PNG | Source |
  |---|---|---|
  | 0–3 | `zombie_v0.png` | Sampler's `zombie.png` (unmodified Patrix baseline) |
  | 4–7 | `zombie_v1.png` | Sampler's `drowned.png` (reused as zombie variant) |
  | 8–11 | `zombie_v2.png` | Sampler's `husk.png` (reused as zombie variant) |
  | 12–15 | `zombie_v3.png` | v0 with brightness 0.55, contrast 1.15, saturation 0.75 |

- **Test results**: {pending user report}
- Output: `Unified-Abs0lut-Claude-v0.5.1-ZOMBIE-PROOF.mcaddon` (32.55 MB), `UNIFIED_PACK_HANDOFF-v0.5.1.md`.

---

## 5. Architecture (current)

```
Unified-Abs0lut-Claude-v{X}.mcaddon        ← single outer zip
├── 01-PatrixWorld-Sampler-v0.4.0.mcpack        RP, 33 MB — bulk visual content
├── 02-BIGCANOPY-BP-v2.8.1.mcpack               BP, has data + script modules
├── 03-BIGCANOPY-RP-v2.8.1.mcpack               RP
├── 04-PatrixCanopyGen-BP-v0.1.2.mcpack         BP, data module only
├── 05-PatrixWorld-Tectonic-BP-v0.7.2.mcpack    BP, data module
├── 06-PatrixWorld-Tectonic-RP-v0.7.2.mcpack    RP, water profiles
├── 07-pw-variants-BP-v{0.1.X}.mcpack           BP, our variant system
└── 08-pw-variants-RP-v{0.1.X}.mcpack           RP, our variant assets
```

The outer `.mcaddon` is the single install unit. When imported, Bedrock installs all 8 component packs. User enables all 8 in a world.

**pw_variants BP components (current):**
- `manifest.json` — both `data` and `script` module types
- `entities/zombie.json` — vanilla override with `pw:variant` added
- `scripts/main.js` — entitySpawn handler, grows mob-by-mob

**pw_variants RP components (current):**
- `manifest.json` — `resources` module
- `entity/zombie.entity.json` — vanilla override with 16 variant texture slots
- `render_controllers/pw_zombie.render.json` — variant selector
- `textures/entity/zombie/zombie_v0..v3.png` + `zombie_baby.png`

---

## 6. Persistent file locations

**Always present** on `/home/claude/` unless the container is fresh:

```
/home/claude/
├── patrix_128_basic/                  Patrix 128x blocks/environment (unzipped)
├── patrix_128_addon/                  Patrix 128x stained glass/variants
├── patrix_128_bonus/                  Patrix 128x scifi/road decorative
├── patrix_128_items/                  Patrix 128x items/equipment
├── patrix_128_mobs/                   Patrix 128x all mobs + LabPBR _n/_s
├── alacrity_ref/                      Alacrity (Java format, Bedrock-correct UV — texture-only, no entity JSON)
├── v0_4_0_extracted/                  Sampler v0.4.0 unzipped — THE current baseline
├── bds_extract/                       BDS 1.26.14.1 extracted subset (vanilla entity JSONs)
├── pack_audit/                        Extracted existing mcaddon contents
├── work/unified_v0_5_0/               Active build tree. Reused for each iteration.
└── _reference_archive/
    ├── haiku_salvage/                 1 file (zombie Patrix/Alacrity composite)
    ├── haiku_labpbr_maps/             86 _n/_s maps (reference only, not valid Bedrock PBR)
    ├── pw_variants_uuids.json         UUID registry for pw_variants packs
    └── README.md                      What was discarded and why
```

If the container is wiped and paths are missing, user must re-upload source zips. The unified `.mcaddon` itself is sufficient as a rollback target since it contains all 8 component mcpacks.

---

## 7. UUID registry (all locked)

**Source of truth**: `/home/claude/_reference_archive/pw_variants_uuids.json` for the new ones; each existing pack's manifest.json for the others.

| Pack | Role | UUID |
|---|---|---|
| PatrixWorld Sampler | header | `7b5e9f01-3a24-4b6c-9d17-8e5f4c2b19a0` |
| PatrixWorld Sampler | resources | `f2c8d9e4-6a51-4f8b-a3c9-1d8e7b4f5c62` |
| BIGCANOPY BP | header | `be7227ad-138a-45a5-9e38-4c2cf4732440` |
| BIGCANOPY BP | data | `a8b6523b-c9ac-4a1b-8586-aea316833b4b` |
| BIGCANOPY BP | script | `6fed24a7-f6c9-47ef-90ec-6b0b20d5ca0c` |
| BIGCANOPY RP | header | `4410d782-8723-40e3-9586-8262cbb9a1f8` |
| BIGCANOPY RP | resources | `95f4efcf-0333-4373-b470-eea36df91034` |
| PatrixCanopyGen BP | header | `5923a10b-6552-48a0-9528-d3a33fcf2bdf` |
| PatrixCanopyGen BP | data | `bca67360-d523-4155-b802-d2bd264fd93b` |
| PatrixWorld-Tectonic BP | header | `2a8f6b14-7e9c-4d3a-a1b5-c8e7f2d4a690` |
| PatrixWorld-Tectonic BP | data | `d14e8c23-6f5a-4b9e-8c2d-7a3b5e9f1c40` |
| PatrixWorld-Tectonic RP | header | `3b9a4c26-8d1e-4f7b-a5c3-2e8d6b4a1f70` |
| PatrixWorld-Tectonic RP | resources | `e25f9d34-7b6c-4d8a-9e1f-3c5b8d7a2e50` |
| pw_variants BP | header | `3e884770-759a-4a80-81fc-9b7a6e22fec0` |
| pw_variants BP | data | `99da2689-d1f9-47fa-b8ba-ea9a3b4cd1d7` |
| pw_variants BP | script | `d7609a19-bf82-44d9-9b6f-3b68b70ad510` |
| pw_variants RP | header | `bccd3b03-ba64-4862-9879-9c7c7e2216e2` |
| pw_variants RP | resources | `15d85bb0-8386-4c93-9c94-2daf763395c2` |

**Never regenerate these. Always reuse.** If a new subsystem needs UUIDs, generate fresh and add to this table.

---

## 8. Canonical reference sources

When overriding vanilla, always start from a verified canonical source. Locked references:

- **BP entity JSONs**: `bedrock-server-1_26_14_1.zip` → `behavior_packs/vanilla_1.26.0/entities/<mob>.json`. These are in JSONC format (comments + trailing commas); strip with regex `re.sub(r'//[^\n]*', '', s)` then `re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL)` then `re.sub(r',(\s*[}\]])', r'\1', s)` before parsing.
- **RP client entity JSONs**: Community mirror `https://github.com/ZtechNetwork/MCBVanillaResourcePack/blob/master/entity/<mob>.entity.json`. BDS ships its RP as opaque `.brarchive` binaries we can't extract, so this community mirror is the workaround. Verify format_version matches our target (1.26.0).
- **Vanilla render controllers**: Same GitHub mirror, `render_controllers/` directory. We typically don't need these directly — we write our own and reference them from our client entity JSON override.
- **PBR format**: MER encoding (R=metalness, G=emissive, B=roughness) in `<tex>_mer.png`, plus `<tex>_normal.png`, plus `<tex>.texture_set.json` sidecar describing both. **Not** LabPBR's separate `_n`/`_s` files.

---

## 9. Technical gotchas (locked knowledge)

### Bedrock entity override rule
Entity JSON overrides **fully replace** vanilla for the same identifier. No merging. To add a property, you must ship the full entity JSON with your property added. If Mojang updates vanilla behavior in a future release, your override pins you to the old version.

### Properties must be declared in `description.properties`
You can't add properties dynamically via events. The property block must exist in the BP entity JSON at load time. `client_sync: true` is required for render controllers to read the property via `query.property('name')`.

### Render controller swap
Vanilla zombie uses `controller.render.zombie.v2`. Our override references `controller.render.pw_zombie` instead. The vanilla controller is gone for this entity (not executed). Any vanilla rendering logic it had (layer textures, etc.) must be re-implemented in our controller or accepted as broken.

### Molang property reference
Inside a render controller, read a custom entity property with `query.property('pw:variant')`. Namespace is part of the string. Use `math.clamp(query.property('pw:variant'), 0, 15)` to defensively bound it.

### Bedrock subpacks = the "slider"
The resolution tier UI is **a slider, not a dropdown** (user corrected this — their word choice matters). Declare `subpacks` array in a single RP's manifest.json, ordered lowest-to-highest. Minecraft renders the list as a slider. `memory_tier` (0-3) sets auto-select based on device RAM; user slider overrides. Subpacks only work within **one** RP — can't span multiple packs in an mcaddon.

### pack.mcmeta dropdown is Java only
Don't propose it for Bedrock.

### `_n.png`/`_s.png` don't work with VV
Bedrock Vibrant Visuals reads MER + normal via `.texture_set.json` sidecar. Old LabPBR files are inert and silently ignored. Setting `"capabilities": ["pbr"]` in manifest just enables reading of `.texture_set.json` files; doesn't convert old format.

### JSONC in Bedrock entity files
Bedrock's parser accepts `//` line comments and `/* */` block comments and trailing commas in entity JSONs. Python's `json` module does not. Strip before parsing; write clean JSON back (Bedrock reads clean JSON too).

### Bedrock blocks.json format_version is locked at 1.1.0
Sampler v0.4.0's `blocks.json` uses `format_version: "1.1.0"`. Bumping to anything higher caused silent parse fallback in a prior session. Do not change.

### Custom biomes have schema constraints
- `multinoise_generation_rules` is legacy, remove from custom biomes
- `minecraft:village_type` is schema-rejected on custom biomes
- `minecraft:terracotta` doesn't exist as bare name → use `minecraft:hardened_clay`
- `minecraft:snow_layer` doesn't exist → use `minecraft:snow` for layer, `snow_block` for cube
- Legacy biome names required: `mesa` (not badlands), `savanna_mutated` (not windswept_savanna), `stony_peaks` (not stony_shore), `ice_plains_spikes` (not ice_spikes), `taiga_mutated` (not old_growth_spruce_taiga)

### Worldgen engine constraints
15 noise_types available, 6 surface_builder types, 8 valid `placement_pass` values. No custom dimensions, no 6D multinoise for custom biomes, no data-driven density functions.

### BIGCANOPY entity atlas UV
`128×128` atlas with `64×64` regions. Bark sides at UV `[0, 64]` size `[64, 64]`. Up face `[0, 0]`, down `[64, 0]`. **Never** use `16×16` UV — we regressed on this once.

### BIGCANOPY animation multipliers (do not touch)
Molang keys in FALL_KEYS: 0.044 / 0.333 / 0.867 / 1.033 / 0.956 / 1.0 at times 0.35 / 0.9 / 1.4 / 1.65 / 1.72 / 1.8. Hand-tuned.

### Sheep texture layering
Bedrock sheep model uses 3 layered texture files: `sheep.png` + `sheep_wool.png` + `sheep_wool_undercoat.png`. All three must be present or sheep renders broken. The persistent "sheep bug" through v0.2.x was root-caused to only shipping `sheep.png`.

### Villager is 4 layers
`villager.png` base + profession + profession_level + type_biome. Patrix ships none of these; currently sourced from Alacrity. User is re-authoring Patrix-style villager manually on their own time.

### log_side grain direction per species
Oak / acacia / dark_oak have **vertical** bark grain → variants rotated 90° are wrong. Birch / cherry have **horizontal** lenticels/stripes — horizontal grain is correct for them. Don't rotate birch or cherry log_side variants.

### CTM tiles as standalone
Patrix OptiFine `optifine/ctm/patrix/log/<wood>/top/` tiles are 2×2 ring connection sets meant to blend. On Bedrock (no CTM), each tile shows a partial ring cut at edges. Fix: use `block/<wood>_log_top.png` basic tile + synthesized rotation/tint variants.

---

## 10. Build & packaging conventions

### Package unified mcaddon
```python
import zipfile, os
WORK = '/home/claude/work/unified_v0_5_0'
OUTER = '/mnt/user-data/outputs/Unified-Abs0lut-Claude-v{X}.mcaddon'
mcpacks = sorted([f for f in os.listdir(WORK) if f.endswith('.mcpack')])
with zipfile.ZipFile(OUTER, 'w', zipfile.ZIP_DEFLATED) as z:
    for mp in mcpacks: z.write(f'{WORK}/{mp}', mp)
```

### Package a component mcpack from a folder
```python
def zip_folder_to_mcpack(folder, output):
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(folder):
            for fn in files:
                fp = os.path.join(root, fn)
                arc = os.path.relpath(fp, folder)
                z.write(fp, arc)
```

### Validation rituals (run before every ship)
1. `json.loads(z.read('manifest.json'))` on every mcpack
2. UUID uniqueness check across all 18 UUIDs in all 8 packs (no duplicates)
3. For entity overrides: `json.loads()` the entity JSON specifically
4. For render controllers: parse JSON, spot-check molang syntax for balanced brackets

### Versioning discipline
- Bump manifest `version` array on every build: `[0, 1, 0] → [0, 1, 1]` etc.
- Add a TAG to manifest.header.name: `[SCAFFOLD v0.1.0]` → `[ZOMBIE-PROOF v0.1.1]`
- Outer `.mcaddon` filename uses `v{X.Y.Z}-TAG`: e.g. `Unified-Abs0lut-Claude-v0.5.1-ZOMBIE-PROOF.mcaddon`
- Never overwrite a previous `.mcaddon` or handoff in outputs — keep both, user decides when to delete

---

## 11. Backlog (deferred items, still not forgotten)

**High priority (scheduled):**
- Turn 3: Subpack tier system on the Sampler pack (32x/64x/128x/256x/512x slider). Declare in Sampler manifest. Populate all 5 tiers for zombie textures as validation.
- Turn 4+: Expand pw_variants mob-by-mob. Candidate order: drowned, husk (already have Patrix textures), then cow/pig/chicken (biome variants already in vanilla), then wild species.

**Ongoing/incremental:**
- Real hand-authored variant textures to replace 4 placeholders per species
- Real PBR (MER + normal + texture_set sidecars) per variant texture
- Proper `zombie_baby.png` authoring (no source currently exists in Patrix or Alacrity)

**Deferred — tied to future domains:**
- Vibrant Visuals tuning pack (lighting/atmospherics/color_grading/water/fogs JSONs) — unblocked by PS5 testing access
- Finite fluids (`ff:water_finite` block, ~3000-6000 block budget on PS5) — big Scripting v2 project
- Full Patrix port Phase 1 beyond sampler (~30k files)
- Color normalization (savannah/canyon/badlands palette harmonization)
- VV per-biome lighting/atmospherics JSON (pw_* biome files)

**BIGCANOPY backlog (14-item list, these remain):**
- #1: Canopy shape matches actual tree (dynamic sizing tied to log count)
- #2: 3-5 sizes per species dynamically (tied to #1)
- #8: Decelerating tail animation (tune FALL_KEYS tail to ease-out)
- #9: Giant mushroom felling (new species for red/brown_mushroom_block + mushroom_stem)
- #11: 2×2 trunk entity geometry for mega jungle + dark_oak
- #13: Slope-aware rest angle (un-shelved)
- Acacia entity geometry rework (awaiting validation of v2.8.1 leaf-bridging BFS fix)

**User-accepted tradeoffs (do not reopen unless user explicitly asks):**
- Mob UV bugs from "Patrix-everywhere swap" — user chose Patrix quality over UV correctness for sheep/phantom/zombie/drowned/husk
- Entity bark color mismatch on BIGCANOPY falling entity vs standing trunks — waiting for VV on PS5 to unify entity/block lighting (Option C)
- Entity foliage color/density mismatch vs standing leaves — same reason, waiting for VV

**User is doing manually (do not touch):**
- Villager full Patrix re-author (84 files, documented in `NON_PATRIX_TEXTURES.md`)

---

## 12. Terminology & user preferences

- **"Slider" not "dropdown"** for the resource pack tier selector. Bedrock's UI is a slider.
- **"Unified-Abs0lut-Claude"** is the exact naming (stylized "0" in Abs0lut). Preserve capitalization and the zero.
- **User's numbered answers** are always in order. If they say "answers to your questions," match them 1:1 to what you asked.
- **User is a "thoughtful collaborator."** They solve problems well when given options. When asking questions, structure as options A/B/C so they can decide concretely.
- **User's ambition is high**; they accept iteration as the path. They said explicitly: "'loads successfully without errors' for us to test" is today's bar, "zero conflicts" is an abstract future goal.
- **"Keep nothing worth keeping otherwise"** — be willing to delete Claude-generated artifacts that don't serve the project. Don't hoard broken work.
- **Persistent docs framework** user defined:
  - `UNIFIED_PACK_HANDOFF-v{X}.md` — per-iteration, user-facing testing + recovery
  - `AI-CONTINUITY-HANDOFF.md` — this doc, AI-facing, append-only
  - Both ship with every iteration in `/mnt/user-data/outputs/`

---

## 13. What NOT to redo

Things that have been tried and failed, documented so the next AI doesn't burn time re-attempting:

- **Generating 16 "variants" via saturation/brightness tweaks**. Does nothing visually meaningful and doesn't connect to Bedrock's variant system anyway.
- **`pack.mcmeta` dropdown for resolution tiers**. Java-only feature, inert in Bedrock. Use native subpacks.
- **Filenames like `zombie_000001.png`**. No Bedrock reader looks for these. Use vanilla-compatible names + texture short-names in client entity JSON.
- **Upscaling Alacrity 4× to use as UV template for Patrix blend**. Architecturally backwards — upscaling low-res doesn't give you a high-res UV template, it gives you a blurry map. Correct approach: downsample Patrix to match Alacrity layout, then upsample the result if high-res is needed.
- **Assuming Bedrock merges entity JSONs**. It doesn't. Full replace, not merge.
- **Treating LabPBR `_n`/`_s` files as Bedrock PBR**. They're Java/OptiFine convention; Bedrock wants MER + normal + texture_set sidecar.

---

## 14. Inter-iteration checklist for the next AI

When the user says "ready for Turn {X}":

1. Confirm you have this doc + per-iteration handoff + transcripts loaded
2. Outline the Turn {X} plan in the response, concretely (specific file paths, specific decisions)
3. Flag any technical risks before writing (user values this)
4. Wait for explicit green light (user's preferred phrasing: "Correct", "Continue", "Yes", "I'm ready for turn X")
5. Execute in small phases with status prints after each
6. Run validation rituals (§10) before packaging
7. Ship three files to `/mnt/user-data/outputs/`:
   - `Unified-Abs0lut-Claude-v{X.Y.Z}-TAG.mcaddon`
   - `UNIFIED_PACK_HANDOFF-v{X.Y.Z}.md`
   - `AI-CONTINUITY-HANDOFF.md` (updated version of this doc)
8. Update section §4 of this doc with the iteration summary before shipping
9. Note any new gotchas in §9, new backlog items in §11, new forbidden patterns in §13
10. Wait for user test report. Do not assume success.

---

*End of AI continuity handoff. Any Claude instance inheriting this project: you are working on behalf of a thoughtful, technical user on a long-running passion project. Respect the history. Don't regress known-good decisions. When in doubt, ask.*
