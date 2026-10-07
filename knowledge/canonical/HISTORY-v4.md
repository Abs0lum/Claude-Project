# AbsolutRealism History — v4

> **Authoritative per-version chronicle of AbsolutRealism, v1.0.0 → 2026-07-07 (+ post-07-07 gap note).**
> This document supersedes and fully absorbs:
> - `HISTORY-v3.md` (preserved verbatim in substance inside Parts I and V)
> - The v1.2.37 → v1.3.33 era archive: `HANDOFF-v1_2_36-through-v1_2_48.md`, `HANDOFF-v1_2_49.md`, `HANDOFF-v1_2_49-through-v1_2_52.md`, `HANDOFF-v1_3_x-SKY-ROOTCAUSE-and-PHASE1-SCANNER.md`, `SKY-Phase1-Spike-Protocol.md`, `SKY-MCPACK-INVESTIGATION-v2-ADDENDUM.md`, `HANDOFF-v1_3_6-through-v1_3_9-ALPHASKY-SCRIPTEDSKY.md`, `HANDOFF-v1_3_21-through-v1_3_27.md`, `HANDOFF-v1_3_28.md`
> - The v1.3.35 state docs: `CURRENT-STATE-v1_3_35-patch8.md`, `HANDOFF-SunSkip-and-BP-02-v1_3_35-TPS-Fix.md`
> - The post-v1.3.35 session handoffs: `HANDOFF-v1_3_36-through-v1_3_47.md`, `HANDOFF-SESSION-2026-07-04-v1_3_48-through-v1_3_54.md`, `HANDOFF-SESSION-2026-07-05-06-CROWN-ROOFS-MEDIEVALISM.md`, and the *history content* of `HANDOFF-SESSION-2026-07-06-07-ROOFS-PLANKS-PROVENANCE-MIGRATION.md`
>
> **Two documents absorbed here remain ALIVE in project knowledge and are NOT retired by this synthesis:**
> - `HANDOFF-SESSION-2026-07-06-07-ROOFS-PLANKS-PROVENANCE-MIGRATION.md` — the live CURRENT-STATE (newest handoff = authoritative state, per custom instructions §2.5).
> - `AbsolutRealism-FOG-LIGHTING-Stacking-Dossier.md` — remains the **canonical living technical reference** for the VV fog/lighting/atmosphere/color-grading stacking model (Abs0lum ruling, 2026-07-10). Part III.3 chronicles its creation and influence only. Flagged for future absorption into ARCHITECTURE.
>
> Companion documents: `OPERATING-MANUAL-v4.md` (read FIRST), `FOUNDATION-v3.md`, `ARCHITECTURE-v3.md`, latest `HANDOFF-*` (CURRENT-STATE), `JEM-TO-BEDROCK-CONVERSION-STANDARD.md`, `AR-Tree-Structure-Building-Guide.txt`.
>
> Synthesized 2026-07-10 from the 17-document source set, on Abs0lum's approved outline. Coverage audit: `COVERAGE-VERIFICATION.md`.

---

## PART 0 — CONVENTIONS FOR READING THIS CHRONICLE

**0.1 — Version lines.** Three versioning regimes appear in this history:

1. **Unified-stack versions (v1.0.0 → v1.3.35):** one version number stamped across the whole pack suite per release. A "version" here = a full-suite ship.
2. **Per-pack versions (2026-07-03 onward):** each pack advances independently (e.g., RP-01 v1.3.54 alongside BP-02 v1.3.46). A "ship" here = a per-pack version, chronicled by session with a version ledger. The transition is recorded at Part VI.1.
3. **The `am:` line (Abs0lutMedievalism, v0.x):** the private study/companion pack suite, born 2026-07-03/04 at v0.3.0, with its own v0.x sequence.

Auxiliary numbering: test/spike packs used v0.x numbers outside the main line (SKY-Spike v0.1.0, SKYTEST/SKYCAL, RP-97 Armor Pilot v0.1.0→v0.2.2). **SKYDIAG BP-01** consumed version numbers **v1.3.36→38 in May 2026 as logging-only diagnostic builds** (UUID preserved) — these are distinct from the July 2026 per-pack v1.3.36+ numbers. See Part V.3.

**0.2 — Decision-journal citations.** D-numbers are **session-scoped, not one global sequence.** Proven collision: **D-108** = square-oak-vine deferral in the sky root-cause session (D-094→D-136 range) *and* the overhang-license supersession in the 2026-07-05/06 session. Every D-number in this chronicle is cited with its session; Part VII.D indexes them the same way.

**0.3 — Record gaps (explicit, deliberate).** This chronicle states what its sources support and marks what they do not. Four gaps are marked in place rather than filled: **v1.2.53/v1.2.54** (attested by reference only), **v1.3.0→v1.3.4** (no ship attested; the sky-era test packs were v0.x), **v1.3.10→v1.3.20** (Part IV.1 — reference reconstruction only), **v1.3.29→v1.3.33** (Part IV.4 — fragments only), plus the **post-2026-07-07 gap** (Part VI.6). Gap entries append when their handoffs are uploaded; nothing here is invented.

**0.4 — Lesson identifiers.** Numbered lessons (#1–#206) live in FOUNDATION; this chronicle records when each was born, promoted, falsified, or superseded. Era-archive lessons carried letter-series IDs (L1–L10, L-SKY-*, L-SCAN-*, L-ATMO-*, L-PKG-*, L-METHOD-*, L-API-*, L-FX-*, L-WORLDGEN-*, L-WITNESS-*, L-PROCESS-*, L-SCHEMA-*, L-VV-*, L-ANIM-*, L-PARTICLE-*, L-ENTITY-*, L-VAR-*, L-TOOL-*, L-ATTACH-*, L-PERF-*, L-GEO-*, L-TEX-*, L-DIAG-*, L-ICON-*, L-ROT-*, L-RENDER-*, L-DIR-*, L-PATH-*) pending FOUNDATION absorption; because the archive documents retire after this synthesis, **their full text is preserved in the chapters below** — this document is now their carrier of record. Note also a v3-internal numbering collision, preserved as-is with editorial flags: **#154/#155 were used twice** (v1.2.31 candidates: iteration-order / decision-journals; v1.2.32 lessons: MERS alpha-sampling / string-deps). See VII.B.

**0.5 — Format of entries.** Parts I–V use v3's per-version entry format (`### vX.Y.Z — date (theme)` with Type / What shipped / Lessons / Status). Part VI uses per-session chapters with per-pack version ledgers, matching how the project itself began recording ships in that era.

---

# PART I — THE UNIFIED-VERSION ERA: v1.0.0 → v1.2.36
*Source: HISTORY-v3.md, preserved verbatim in substance. §1–§6 below are v3's original sections with their original numbering; §7–§8 are v3's appended post-v1.2.31 sections, renumbered only to repair the duplicate-§3/§4 quirk (editorial notes mark the repair in place). Sections §2–§5 are **era snapshots as of v1.2.31** (lessons-library status, backlog, authorization audit, process evolution as they stood when v3's core was frozen); §7 extends the chronicle to v1.2.36. Later parts of this document update all of them.*

*v3's original document header, preserved for the record:*

> # AbsolutRealism History — v2 (current through v1.2.36)
> 
> > **Authoritative per-version chronicle and changelog.** This document supersedes:
> > - `ABSOLUTREALISM-HISTORY-AND-BACKLOG-v1_2_31.md` (per-version § preserved verbatim below)
> > - `HANDOFF-v1_2_32.md`, `HANDOFF-v1_2_32-1.md`
> > - `README-v1_2_32.md`, `README-v1_2_32-1.md`
> > - All per-version handoffs v1.2.32 → v1.2.36
> >
> > Companion documents:
> > - `OPERATING-MANUAL-v2.md` — How to work on this project. Read FIRST.
> > - `FOUNDATION-v2.md` — Project identity, locked invariants, all lessons
> > - `ARCHITECTURE-v2.md` — Technical schema, scanner, geometry, formats, scripts
> > - `CURRENT-STATE-v1_2_36.md` — Current ship status, candidate lessons, queued work, file index
> 
---

## §1. PER-VERSION CHANGELOG

### v1.0.0 (PatrixWorld) — 2026-05-06

**Type**: Initial production ship. The original v0.18.4 stabilized into v1.0.0.

**Identity**: PatrixWorld (renamed at v1.0.1).

**What shipped**:
- 17 packs total (v0.18.4 baseline)
- 9 custom leaf species with 6 variants each, all rendering via permutation system + `pw:randomize_variant`
- 17 trunk types (oak, spruce, birch, jungle, acacia, dark_oak, mangrove, cherry, crimson, warped, pale_oak, mushroom, plus elder variants)
- 12 species in BIGCANOPY SPECIES roster
- All 16 sand variants on disk; only 4 registered (lesson #62 — over-variance produced "checkered" appearance)
- VV format_version table locked: atmospherics 1.21.40, lighting 1.26.0, color_grading 1.21.90, water 1.26.0, client_biome 1.21.120
- min_engine_version 1.21.120 floor (Lesson #20)
- Reserved filenames locked: `atmospherics/atmospherics.json`, `lighting/global.json`, `color_grading/color_grading.json`, `water/water.json`

**Lessons established (#1-#125)**:
- Foundation lesson library for all subsequent work
- Notable: #20 (1.21.120 floor for VV), #21 (format_version table), #23 (water sampleWidth deprecated), #24 (reserved filenames), #28 (1.21.90 client_biome wrong), #44 (south face after +90X = world top), #62 (4-variant sand cap), #69 (canopy spec for Android crash safety), #70 (custom blocks DO support per-instance variation via permutations — superseded later), #77 (parse-OK ≠ runtime-OK), #78 (VV directory reserved filenames), #94 + #95 (working permutation + custom-component pattern)

**10 post-ship diagnostic findings logged** (see `ABSOLUTREALISM-DIAGNOSTICS-v1_2_31.md` §1):
1. Moon shows as white ball, no detail visible
2. Sun disc invisible due to luminosity
3. Falling trees not working right (vague)
4. Ore glow projection (overworld emissive too aggressive)
5. Deepslate ore variants don't match deepslate matrix
6. Bed texture not rendering correctly
7. Armor looks vanilla when equipped (in-hand correct)
8. Deep Dark doesn't summon Warden when triggered
9. Custom biome ambient missing
10. Mob spawn rules incomplete (zombie/spider/skeleton/creeper only)

---

### v1.0.1 — 2026-05-07 (Project rename)

**Type**: Bug fix + project identity transition.

**Identity transition**: PatrixWorld → **Abs0lutRealism** (note "0" matching gamertag).

**What changed**:
- 14 non-`pw-`-prefixed pack folder names renamed
- All 17 manifest `header.name` fields rebranded
- All 17 manifest `header.description` prefixes updated
- Manifest UUIDs PRESERVED (save-compatibility invariant)
- Internal `pw:` namespace PRESERVED (block IDs, biome IDs, sound events all stable)

**Atmospheric tuning (cinematic baseline)**:
| Setting | v1.0.0 | v1.0.1 | Direction |
|---|---|---|---|
| atmospherics.moon_mie_strength peak (overworld) | 0.5 | **0.15** | -70% |
| moon_mie_strength peak (end) | 0.2 | **0.06** | -70% |
| lighting.directional_lights.orbital.moon.illuminance peak | 1.0 | **0.5** | -50% |
| sun.illuminance peak | 220-246 | **130** | -41% to -47% |
| sun.illuminance noon | 135-151 | **100** | -26% to -34% |
| lighting.sky.intensity (10 biomes) | 0.10 | **0.90** | +800% |
| color_grading.highlights.gain (10 biomes) | 1.05-1.15 | **1.00** | -5% to -13% |

**Pack identity transition**: from "128x" → "128/256x blend" (selective 256x integration started with furnace family).

**Lessons added (#126-#152)**:
- #126: RP-03 PBR amethyst MER values nontrivial
- #127: Cross-pack PBR layering — RP-03 ships sidecars; color PNGs in OTHER packs (FALSIFIED v1.2.6)
- #128: Patrix 256x source ships color in palette mode (P) — convert to RGBA
- #129: Idle MER from active MER: zero G channel
- #130: Sand and red_sand PBR sidecars referenced nonexistent files — cleaned up
- #131: Foundation backlog can drift from pack reality (the "7 dormant branch geometries" claim was inaccurate)
- #132-#149: Carry-forward from prior session investigation (ONNX unportable, BiomeClassifier deltas, sparse-tree variants high-ROI, replace_biomes audit, identity reuse, audio mod licenses, Atmosfera schema, pack inventory verification, DEFINED vs WIRED sound events, categorical Bedrock impossibilities, ARR license = independent reimplementation only, audio > waypoints ROI, WITNESS RULE extended to factual claims, naming similarity ≠ functional similarity, mid-investigation reframing normal, foundation lesson numbers reconcile across patches, pack rename without UUID change, server biome without client_biome → vanilla colors)
- #150: Custom block state declaration alone doesn't activate randomization
- #151: Randomize component handlers must be type-aware about variant count
- #152: Custom block loot tables shipped at v1.0.0 dropped block items at 100% with NO conditions — non-vanilla; audit pattern established

**Items resolved in v1.0.1** (from v1.0.0 conflict notes):
- 12 superseded claims (blended leaves, custom-block variation impossibility, format_version 1.21.40 for blocks, min_engine 1.21.90 sufficient, atmospherics 1.21.90, atmospherics/global.json filename, water sampleWidth, client_biome 1.21.90, subpack tier shipped, all 16 sand variants registered, only variant 0 renders, tint_method must be none)
- 6 conflict resolutions queued for user decisions (acacia L-shape, slope-aware rest angle, BIGCANOPY dynamic canopy, branches worldgen, etc.)

---

### v1.1.0 — 2026-05-07 (Performance pass)

**Type**: Performance optimization without feature changes.

**What changed**:
- Leaf cube budget locked: ≤7 cubes per variant, target ≤6.5 average. v1.1.0 conformed: v0=7, v1=6, v2=6, v3=6.
- BIGCANOPY constants tightened:

| Constant | v1.0.1 | v1.1.0 |
|---|---|---|
| LEAF_SCAN_INTERVAL | 30 ticks | **60 ticks (3.0s)** |
| LEAF_SCAN_RADIUS_XZ | 12 | **8** (~70% scan volume reduction) |
| LEAF_SCAN_DOWN | 8 | **6** |
| LEAF_SCAN_UP | 14 | **10** |
| LEAF_MAX_PER_TICK | 100 | **40** (smaller per-tick CPU spike) |

- Chunk-load gate added (~1474 bytes of new code) — defers leaf scanning during first ~2 seconds after chunk load. Eliminated post-teleport CPU burst that caused PS5 forest crashes in v1.0.1.
- Volumetric fog ceilings tightened: max_density 0.06 → **0.05**; zero_density_height 320 → **250**. (v1.1.0 §6.7)
- Sand sun-glint MERS authoring locked (Lesson §6.8) — sparkle = R=0/G=240/B=30/A=12; non-sparkle = R=0/G=0/B=240/A=12.
- 1,151 64x foliage PNGs upscaled to 128x; 594 deleted (anomalous-state mutation flagged for follow-up).

**Performance results**:
- v1.0.0: ~50-55 fps with frequent dips to 40s
- v1.1.0: ~55-60 fps stable

**Lessons added**:
- §6.8 Sand sun-glint paired G+B authoring (CONFIRMED candidate)
- §6.9 Leaf cube budget (LOCKED INVARIANT)
- §6.10 BIGCANOPY constant table (LOCKED INVARIANT)

**Process notes**:
- Anomalous file mutations during build — 4 categories of state modifications occurred without Claude executing the code. Investigated; net effect matched specs. Logged as suspicious for future sessions.
- New backlog item: snapshot-and-diff infrastructure at session checkpoints to defend against state mutation surprises.

---

### v1.1.1 — 2026-05-07 (Bug fix + aesthetic correction)

**Type**: `[ContentLog]` error closure + sand sun-glint redesign.

**Bug fixes (4 categories of [ContentLog] errors closed)**:
1. **Feature rules — invalid `tree_pass` placement_pass**: 4 sparse-tree feature rules used `placement_pass: "tree_pass"`. Replaced with `surface_pass`.
2. **Feature rules — Molang heightmap arg error**: same files used `y: "query.heightmap(x,z)"`. Replaced with `{distribution: "uniform", extent: [60, 100]}`.
3. **local_lighting — invalid block identifiers**: 4 entries in local_lighting.json referenced non-blocks (`minecraft:end_crystal`, `minecraft:portal`, `minecraft:end_gateway`, `minecraft:jack_o_lantern`). Removed. Total: 91 → 87 entries.
4. **snow_layer un-weighted variations warning**: snow_layer was registered with `variations` array but Render Dragon's partial-block path doesn't honor variations on partial blocks. Fixed via single-texture binding.

**Aesthetic correction**:
- Sand sun-glint redesigned from emissive (G=240) to true specular (R=128 + B=12). Sparkle now flashes only when sun aligns with view direction; matte sand otherwise.

**Lessons added (LOCKED INVARIANTS)**:
- §6.6 Bedrock feature_rules placement_pass enum is closed
- §6.6 Bedrock Molang query.heightmap takes no arguments
- §6.11 local_lighting validity rules (block identifiers only, Bedrock namespace, must exist)
- §6.11 local_lighting validation cascades misleading errors (light_type out of range)
- §6.13 snow_layer rendering constraint (no variations arrays on partial blocks)
- §6.13 Emissive vs specular sparkle is an artistic distinction worth surfacing
- §6.13 Locatebiome returns surface column, not biome Y position

---

### v1.1.2 — 2026-05-07 (Tree feature canopy fixes)

**Type**: Bug fix targeting v1.1.1 user-reported issues.

**Fixes**:
- **A**: Jungle young trees with random_spread_canopy → fancy_canopy (eliminated scattered ground-level leaves)
- **B**: Jungle young trees min_altitude_factor 0.4 → 1.0 (matches all other young/mature/old features; eliminated branches on young trees)
- **C-1**: Solid green wall through canopy gaps — root cube shrunk from 16×16×16 to 14×14×14 with origin (-7, 1, -7); UV [1,1] size [14,14]
- **D**: Pitch-black canopies — all 9 leaves species `light_dampening: 7 → 1` (matches vanilla)
- **E**: wing_flap Molang variable error — added `variable.wing_flap = math.sin(query.anim_time * 360 * 3);` to chicken.entity.json + parrot.entity.json pre_animation

**Lessons added (LOCKED INVARIANTS)**:
- §6.14 Tree feature canopy types must match per-tier (fancy_canopy for structured trees, never random_spread_canopy)
- §6.15 Branches min_altitude_factor must be 1.0 for non-elder tree tiers
- §6.16 Leaf root cube size 14×14×14 (1-voxel inset from block boundary)
- §6.17 light_dampening for foliage blocks (leaves=1, logs=0, saplings=0)
- §6.18 Bird entity pre_animation must initialize wing_flap

**Deferred to v1.1.3**:
- Setup/swim "can't find animation X" log warnings (need runtime testing)
- Jungle leaves color B=0 yellow-green tint (aesthetic decision pending)
- Jungle leaves animation strip waste (~880 KB)

---

### v1.1.3 — 2026-05-08 (Sun visibility + canopy light)

**Type**: Render-method fix + atmospherics conservative tuning + sun texture swap.

**Phase F (render_method)**: All 9 leaves species changed from `alpha_test_to_opaque` → `alpha_test`. Sun rays now scatter through transparent pixels, producing dappled light effect under canopy. Tradeoff: leaves no longer cast crisp self-shadow.

**Conservative atmospherics tuning** (out of 3 options offered):
- Sun visibility tuning across mie + glare + rayleigh
- Sun texture swap (different cross pattern for less aggressive disc)

**Lessons added**:
1. `light_dampening` and VV deferred shadow are SEPARATE light systems — both must be addressed for true canopy light penetration
2. `alpha_test_to_opaque` was a VV stability optimization with hidden cost (solid shadow casting through transparent pixels)
3. Sun visibility is a three-knob problem (mie + glare + rayleigh interact)
4. Sun textures with painted-in glare stack with engine mie — pick one approach

**Process error logged**: Selected the Conservative tier without explicit user approval in a prior incomplete turn. Recovery via amnesia check + user confirmation. Standing protocol established: every "please continue" turn starts with phase log tail, output state check, recently modified files, and `_logs/v1_X_Y*` evidence search.

---

### v1.2.0 — 2026-05-08 (Cinematic mood + lens flare)

**Type**: Major aesthetic upgrade — cinematic mood pass + scripted lens flare.

**What shipped**:
- 27 sun illuminance keyframes (was 6)
- 22 sun color stops painterly progression (was 6)
- sun_mie_strength 0.3 → 7.0; sun_glare 6.0 → 8.5
- Moon illuminance 0.5 → 0.85, color [200, 225, 255], moon_mie 0.15 → 2.0
- Ambient illuminance 0.02 → 0.12 with time-keyframed colors
- highlightsMin: 2.5 → 20 in all 10 color_grading files
- midtonesMax: ADDED at 55 in all 10 color_grading files
- Color grading bumps (gain 1.30, contrast 1.25, saturation 1.55, gamma 2.05)
- Per-biome lighting variation: 7 biomes (forest, cherry, coastal, desert_dunes, alpine, pale, river_canyon)
- BP-06 Lens Flare BP — entity-billboard particle system, 4 lens flare particles (anamorphic, ghost ring, sun ray, sun corona)

**Lessons added (G-family — cinematic mood)**:
- G-01 Keyframe density 25-40+ (later superseded v1.2.1 → 13 sufficient)
- G-02 Painterly color progression
- G-03 highlightsMin/midtonesMax color grading isolation (later superseded v1.2.1 → hMin=5/mMax=35 for cinematic-realism)
- G-04 sun_mie golden-hour sweet spot 7-15 (later superseded v1.2.2 → 2.5-3.5 + system coordination)
- G-05 Moon visibility via paired illuminance + mie + cool color
- G-06 Per-biome lighting variation routes via biomes_client.json
- G-07 Sky intensity tradeoffs (0.7 cinematic baseline)

**Performance**: ~60 fps target on PS5 18-chunk deferred (cinematic mood adds <1ms/frame; lens flare BP <0.1ms/tick).

---

### v1.2.1 → v1.2.5 — Iterative refinement

**v1.2.1 (mood superseding)**: Reduced keyframe density (G-01 → 13 sufficient). Tightened color grading (G-03 → hMin=5/mMax=35). Sun_mie reduced (G-04 → 2.5-3.5).

**v1.2.2-v1.2.5**: Various tuning — sun coordination across system, fog harmonization, atmospheric refinements. Many candidates promoted/falsified across the H-01 to H-17 family.

---

### v1.2.6 — 2026-05-08 (Major texture pipeline repair)

**Type**: Architectural fix for magenta missing-texture cubes.

**Trigger**: User reported magenta cubes when breaking dirt + magenta tree trunks + stone "looks low resolution" + sky too dark + two stars (lens flare duplication).

**Diagnostic findings**:
| Issue | Count | Severity |
|---|---|---|
| RP-03 texture_set.json with missing color | 676 | CRITICAL |
| RP-04 terrain_texture entries with missing files | 444 | LOW (vanilla fallback) |
| RP-09 terrain_texture entries with missing files | 113 | CRITICAL |

**Architectural fix (Lesson H-18 PROMOTED)**:
- 595 missing color PNGs copied into RP-03 to make it self-contained
- 68 log/leaf textures copied into RP-09 with 36 PBR companions
- 871 PBR companions created for variations (stone v0..v7, dirt v0..v15, etc.)
- RP-03 size grew from ~50MB to ~117MB

**Lessons added/promoted**:
- H-18 (CONFIRMED → PROMOTED): Bedrock PBR requires color PNG to be in same pack as texture_set.json companion
- H-19 (CONFIRMED): Block variations need own PBR companions
- H-20 (CONFIRMED): pw: namespace blocks need vanilla textures co-located
- H-21 (CANDIDATE): sky.intensity sweet spot 0.85-0.95 for cinematic-dark sky colors

**Sky brightness boost**: sky.intensity bumped ~30% across 8 overworld biomes (forest 0.65 → 0.845, alpine 0.85 → 1.00, etc.).

---

### v1.2.7 — 2026-05-08 (RealismCraft research integration)

**Type**: Deep RealismCraft (RC) inspired retune — water/sky/atmospherics/fogs.

**Phase Q research** (~30 turns): Inventoried RC's water files, atmospherics, lighting, fogs, color_grading. Pulled MS Learn authoritative VV 1.26.0 schema. Built improvement matrix.

**Files modified (80+)**:
- Water (Path A complete): caustics.png softened (Gaussian sigma=2.5, gamma 1.4), all 22 water/*.json overhauled — particle_concentrations rebalanced, waves bumped to RC range, caustics.power floats → INT, caustics.scale 0.6 → 0.25-0.5, caustics.texture ADDED
- 8 overworld atmospherics — sky_horizon_color noon `[3,15,38]` → `[50,175,235]`; sky_zenith_color noon `[3,15,38]` → `[30,90,175]`; 25 keyframes rebuilt; sun_mie 0 at noon, 0.75 peak at sunrise/sunset (RC pattern); sun_glare_shape 0 at noon, 0.07 peak
- 8 overworld lighting — sky.intensity pulled back to RC 0.6-0.7 range
- 42 fog files retuned — render_distance_type "fixed" → "render"; fog_start/fog_end percentages; volumetric.density.air.uniform: ADDED true; max_density 0.080 → 0.04-0.05; henyey_greenstein_g 0.85-0.92 → 0.5-0.7
- Manifests stamped to [1, 2, 7]

**Lessons added (H-22, H-23)**:
- H-22 (PROMOTED CANDIDATE): caustics.power INT 1-6 schema (clamp at 6)
- H-23 (PROMOTED CANDIDATE): water_settings.json 1.26.0 has no surface/foam/subsurface blocks

---

### v1.2.8 — 2026-05-08 (Visual fix series)

**Type**: User-reported issue resolution.

**Issues fixed**:
- Sun + godrays + sky harmony
- Color grading further refinement
- Various atmospheric details

**Lessons (H-26 to H-30)**: Visual fixes confirmed.

---

### v1.2.9 — 2026-05-08 (Water/sand/ice PBR + jungle vine fix)

**Type**: PBR pass on water surface, sand variants, ice family.

**Sources used (license-clean)**:
- Water normals: OGA CC-BY 3.0 (Keith333 / Benkyou Studio) — RP-02/credits.md created
- Sand: ambientCG `Ground033` (CC0)
- Ice: ambientCG `Ice002`, `Ice004` (CC0)

**Issues resolved**:
- Issue A: Jungle vine cubic canopy (Phase F routing change)
- Issue B: Sand transition harshness (Phase C — Ground033 replacement) — discovered macro_std diagnostic
- Water surface PBR (Phase A)
- packed_ice + blue_ice PBR (Phase G)
- Waterlily / lily_pad PBR (Phase D)
- Caustic softening v2 (Phase B — sigma 1.8 / gamma 1.2 / power +1)

**Lessons added**:
- H-31 (PROMOTED-CANDIDATE): License-clean source rule (CC0/CC-BY only; never RC binary archives)
- H-32 (PROMOTED-CANDIDATE): Sand transition harshness root cause = macro_std > 8 in variant tiles. Diagnostic threshold: downsample to 16×16 luminance via Lanczos, take std. <8 = natural; >8 = visible boundaries.

**Backlog items added**:
- Cauldron water PBR (need cauldron_water.png authored first)
- Regular ice PBR (Ice003 source available; user said "ice is fine")
- Splash decals (Decals 10/11/13 from new_water.zip)
- Red sand uniformity check (macro_std 6.7-10.3 borderline)
- Wet rocks effect (Leaking019C from new_water.zip)

---

### v1.2.10-v1.2.12 — Various refinements

(Brief versions; no major architectural changes.)

---

### v1.2.13-v1.2.14 — Manifest corrections

**v1.2.14**: Manifest fixes (min_engine_version → 1.21.120, metadata.product_type=addon, pbr cap added). Ice texture fixes (alpha=255 for packed_ice/blue_ice, lower subsurface).

---

### v1.2.15 — DISASTER (manifest stamping bug)

**Type**: Failed release. Subsumed by v1.2.16 fix.

**What broke**:
- Phase 3 manifest stamping code blindly bumped EVERY `version` field, including `@minecraft/server` API dependency
- Overwrote `@minecraft/server` from valid string `"2.0.0"` to invalid array `[1, 2, 15]` on three behavior packs (BP-01, BP-02, BP-03)
- Bedrock can't find a v1.2.15 of `@minecraft/server` → import returns undefined
- Tectonic BP script tries to call `system.beforeEvents.startup.subscribe(...)` → crashes with `TypeError: cannot read property 'startup' of undefined`
- `pw:randomize_variant` custom block component never registers
- 23 leaf-block JSONs reference `pw:randomize_variant` → fail to parse with `child 'pw:randomize_variant' not valid here`
- 14 deferred `BlockDescriptor` errors for `pw:oak_leaves` and family

**Pre-existing H-18 violations also surfaced** (had been silent before — 81 violations across RP-04 and RP-05):
- RP-04: 24 violations (powder_snow + 16 candles + 4 chains + comparator + repeater)
- RP-05: 57 violations (entire flora pack)

**Lesson learned (H-53 PROMOTED)**: When stamping manifests, NEVER touch `dependencies[].version` if `module_name` starts with `@minecraft/`. Those are API module versions, NOT pack versions.

---

### v1.2.16 — 2026-05-09 (Critical fix release)

**Type**: Recovery from v1.2.15 disaster.

**Critical fixes**:
- API dependency versions restored (BP-01="1.16.0", BP-02="2.0.0", BP-03="2.0.0")
- Manifest stamping logic fixed (forward-compatible)
- All 81 H-18 violations cleaned (24 in RP-04, 57 in RP-05)

**Lessons promoted**:
- H-53 (PROMOTED): Never touch @minecraft/* string deps when stamping manifests
- H-54 (PROMOTED): Manifest diff gate after stamping (acceptable diff: header.version, modules[].version, dependencies[].version for UUID-deps only; FAIL if anything else changes)
- H-55 (PROMOTED): H-18 violations must be cleaned, not deferred (the v1.2.15 deferral of "24 broken candle color refs" cost the release cycle)

---

### v1.2.17-v1.2.18 — Iteration

(Refinements; no major architecture changes.)

---

### v1.2.19 — 2026-05-09 (Phase 1 of 3 — Trunk authoring)

**Type**: Checkpoint release (not for testing) — first phase of dodecagon trunk overhaul.

**What shipped**:
- Dodecagon log UV grouping (4-4-4 with 1px shared edges) for oak/spruce/jungle/birch young/mature/old logs
- 7 Patrix end-grain log-top variants per species (9 species × 7 variants = 63 unique end grains)
- Variants 2, 4, 6, 7, 8 inpainted to remove cracks; variants 3, 5 retain cracks for variety
- Heartwood enlarged to fill dodecagon interior (no visible gaps through panel edges)
- Independent randomization: bark variant + log-top variant pick separately per tree
- Vines on dodecagon mature/old worldgen: 15% in oak forests, 30% in jungles

---

### v1.2.20 — 2026-05-09 (Phase 2 of 3 — Falling-tree visual rebuild)

**Type**: Checkpoint release.

**What shipped**:
- Trunk visibility fix: rebuilt all 9 species' falling-tree entity textures by compositing bark + leaf imagery from standing-tree atlas
- Dodecagon trunks for oak/spruce/jungle/birch × young/mature/old falling-trees (12 geometries)
- 2×2 square trunks preserved for elder species + dark_oak + pale_oak + acacia + cherry + mangrove
- Multi-cube puff canopies for all 23 falling-tree geometries (1 LOD anchor + 4 corner puffs + 1 top crown each)
- Falling-tree branches for 8 species (oak_elder, spruce_elder, jungle_elder, dark_oak, pale_oak, acacia, cherry, mangrove)
- Animation polish: branch sway during fall + canopy squash-and-stretch on impact

---

### v1.2.21 — 2026-05-09 (Phase 3 of 3 — Standing branches + sounds + particles, FINAL TESTING RELEASE)

**Type**: Phase 3 of 3 (USER TESTS NOW).

**What shipped**:
- 8 branch BLOCKS placed by worldgen at canopy attachment points (oak_elder, spruce_elder, jungle_elder, dark_oak_elder, pale_oak_elder, acacia, cherry, mangrove)
- 48 branch features (8 species × 6 features each)
- 5 elder species: aggregate features `pw:{species}_elder_with_branches_tree_feature` combining tree_feature_v2 + branch_scatter
- 10 biome container files updated to reference with_branches variants
- 14 .ogg tree-fall sound files copied from efallingtrees Java mod
- 8 sound events registered (`pw.tree_fall.{small,medium,big,generic}` + `pw.tree_impact.*`)
- Sound size matches species tier: young → small, mature → medium, old/elder → big; nether → generic
- New `pw:leaf_fall` particle (5 leaves per spawn, 3-second lifetime)
- 5 timed bursts at 15%, 30%, 50%, 70%, 85% through fall arc

---

### v1.2.22-v1.2.26 — Iterative refinement

**v1.2.26**: Dodecagon chord-flush fix. Standing dodecagon panel widths locked: young 3.2, mature 3.75, old 4.0. Falling-tree end-grain UV mapping locked: 792 panels.

---

### v1.2.27 — 2026-05-10 (Phase 1+2+3 leaf overhaul, Option C)

**Type**: Major leaf system overhaul — section flag scanner + 7 sectional variant geometries + section-aware variant randomizer.

**What shipped**:
- Section flag scanner (50 horizontal radius, ±20/-12 vertical, every 100 ticks, MAX 120 flags/tick)
- 9 leaf JSONs gain 3 storage states: pw:section, pw:exposure, pw:section_rolled
- 7 leaf variant geometries (cube counts 11/10/9/1/5/9/7 = 52 total)
- 9 leaf species × 7 permutations = 63 perms
- Variant_3 originally 1-cube core (lightest); rewritten to 8-corner-puffs in v1.2.29
- Section-aware variant pool keyed on `${section}_${exposure}`
- Texture twin: v6 twins to v5 (since v6 art unauthored)
- Per-canopy cube budget reduction: ~53% (650 → 303 cubes for 100-leaf canopy)

**Cascade (Phase 4)**: deferred to v1.2.28.

---

### v1.2.28 — 2026-05-10 (Phase 4 cascade)

**Type**: playerBreakBlock cascade integration.

**What shipped**:
- `_pendingCascades` Set with composite-key dedup (Lesson #147)
- `world.afterEvents.playerBreakBlock` cascade
- Cascade flush every 4 ticks, 50 cascades per tick budget
- Bounded recursion (verified V21 — cascade flush body does NOT call `_enqueueCascade`)

**Lessons promoted/added**:
- #144 (CONFIRMED): Cross-version state migration via flag reset
- #146 (CONFIRMED): Multi-stage cascade architecture — three-stage architecture: cascade event → scanner re-flag → variant re-roll
- #147 (CANDIDATE): Event-queue dedup via Set with composite key
- #148 (CANDIDATE): Cascade coverage gaps from event-API limits — `playerBreakBlock` only catches tool break, not explosion/setPermutation/decay

---

### v1.2.29 — 2026-05-10 (Architecture release — cascade closure)

**Type**: Closure of cascade architecture gaps.

**What shipped**:
- Explosion cascade hook
- BIGCANOPY-inline cascade for tree felling
- Decay-scanner exposure re-validation (Tier 4 catchall via reValidateExposure)
- Depth-2 inner detection (variant_3 reserved for depth ≥ 2)
- Variant_3 redesigned: 1-cube core → 8 corner puffs only (truly empty interior)
- Asymmetric scanner extent: UP=20 → 35 (mega-jungle coverage); DOWN=12 → 4
- Bark seam audit (read-only — passed)

**Surprises discovered during research** (filed for v1.2.30):
- Surprise 1: Vanilla decay non-gap (informational, no fix)
- Surprise 2: MERS subsurface scaling — leaves at S avg 35-65 vs spec 100. Scale ×2 in v1.2.30.
- Surprise 3: Mega-jungle scanner gap — fixed in v1.2.29 via UP=35.

**Lessons promoted/added**:
- #148 (CONFIRMED): Four-tier cascade for event-API gaps (architecture)
- #149 (CANDIDATE): Flag-based depth detection with multi-cycle convergence (first cycle over-classifies; corrects in 2-3 cycles)
- #150 (CANDIDATE): Asymmetric scan volume for vertically-skewed content

**29/29 verification PASSED.**

---

### v1.2.30 — 2026-05-10 (Polish + asset, TEST VERSION)

**Type**: Polish layer on top of v1.2.29 architecture.

**What shipped**:
- C-1: Phase-offset flipbook ticks_per_frame (alive-canopy effect) — 162 flipbook entries varied per variant: v0=4, v1=5, v2=6, v3=5, v4=4, v5=6
- C-10: Mid-fall leaf shedding — 3 bursts of 2-4 leaf_litter entities at 30%, 55%, 80% of fall arc
- C-14: Settling bounce animation — 5-keyframe damped oscillation over 600ms (4° amplitude)
- MERS subsurface ×2 (Surprise 2 fix) — all 54 leaf MER textures scaled. Per-species results:
  - pw_oak: avg S 35 → 69
  - pw_jungle: 59 → 121
  - pw_birch: 64 → 123
  - pw_dark_oak: 51 → 103
  - pw_acacia: 35 → 100
  - pw_cherry: 59 → 118
  - pw_mangrove: 48 → 96
  - pw_pale_oak: 54 → 107
  - pw_spruce: 51 → 103

**Lessons promoted/added**:
- #149 (CONFIRMED): Flag-based depth detection — pre-promoted on architecture confidence
- #150 (CONFIRMED): Asymmetric scan volume — pre-promoted on automated verification
- #151 (CANDIDATE): Asset-side bulk processing via PIL+numpy
- #152 (CANDIDATE): Phase-offset flipbook for alive-canopy effect
- #153 (CANDIDATE): Molang keyframes with per-entity dynamic base

**25/25 verification PASSED.**

---

### v1.2.31 — 2026-05-10 (Scanner fix + variant_0 redesign + MERS asymmetric bump)

**Type**: Bug fix + visual refinement based on v1.2.30 in-game testing.

**User report from v1.2.30**:
- ✓ Loaded and looked amazing (visual fixes worked)
- ✗ Leaf scanner/replacer not working — leaves stuck at variant_0
- ✗ Canopies appearing unusually large
- → User wanted variant_0 redesigned to 8-cube directional model
- → User wanted slight MERS S bump

**Scanner fix (combined options 2+3)**:
- Bug root cause: v1.2.29's UP=35 + existing `SECTION_EARLY_EXIT_THRESHOLD = 3000` caused scanner to bail in empty sky before reaching canopy
- Fix 1: Inverted dy iteration to BOTTOM-UP (`for dy = -DOWN; dy <= UP; dy++`)
- Fix 2: Added `leavesFound` counter; smart early-exit only when `leavesFound > 0 && leavesUnflagged === 0`
- Fix 3: SECTION_EARLY_EXIT_THRESHOLD raised 3000 → 50000 as belt-and-suspenders

**variant_0 redesign — directional 8-cube +X model**:
- Spec: 1 core + 4 corner puffs all on +X side + top + bottom + +X face slab = 8 cubes
- Cube count signature changed: [11, 10, 9, 8, 5, 9, 7] → **[8, 10, 9, 8, 5, 9, 7]**
- Geometric clever bit: every leaf orients identically; +X corners overlap with adjacent block's missing -X corners → illusion of complete coverage
- Edge cubes left for v1.2.32 iteration if needed

**MERS asymmetric bump (option C)**:
- Pass 1: uniform ×1.15 across all 54 leaf MER textures
- Pass 2: additional ×1.5 on oak only (6 textures)
- IMPORTANT FINDING: v1.2.30's ×2 had already saturated 72-94% of leaf-area pixels to 255. v1.2.31 bump pushed remaining intermediates to 255. Image-wide averages barely moved (background pixels at alpha=0 dominate); leaf-area S values 244-254 → 250-255. Oak fully at 100% saturation.

**Lessons added (CANDIDATES)**:
- #154 (CANDIDATE v1.2.31): Iteration order matters with bounded early-exit. When a scan loop has "early exit on no work" optimization, iteration ORDER determines whether that optimization fires legitimately (finished work) or spuriously (haven't reached work yet). Top-down sweep with bail-on-empty fails when scan extent reaches into typically-empty regions. Bottom-up + "found anything yet" check is more robust.
- #155 (CANDIDATE v1.2.31): Decision journals are required complement to phase logs. Phase log = "what shipped, when." Decision journal = "what we thought, when." Both needed for amnesia recovery, especially when intermediate workspaces get cleaned up.

**Decision-journal protocol adopted**: First build to use journal. Located at `/home/claude/build/v1231/_logs/decision_journal.md`. 7 entries capturing scope, scanner-bug observation, variant_0 design rationale, MERS asymmetric decision, MERS saturation-ceiling discovery, MERS coverage-expansion deferral, ship verification.

**49/49 verification PASSED.**

---
## §2. CUMULATIVE LESSONS LIBRARY STATUS

### Promoted (PROMOTED status — reproving cost a release cycle)
- H-18 (v1.2.6): Bedrock PBR requires color PNG in same pack as texture_set.json
- H-53 (v1.2.16): Never touch @minecraft/* string deps when stamping manifests
- H-54 (v1.2.16): Manifest diff gate after stamping
- H-55 (v1.2.16): H-18 violations must be cleaned, not deferred
- H-14 (v1.2.6): max_density 0.150 crashes Android Bedrock
- H-22 (v1.2.9): caustics.power INT 1-6 schema
- H-23 (v1.2.9): water_settings.json 1.26.0 has no surface/foam/subsurface blocks
- H-31 (v1.2.9): License-clean source rule
- H-32 (v1.2.9): Sand transition harshness root cause (macro_std)

### Confirmed
- #144 (v1.2.28): Cross-version state migration via flag reset (2 corroborations)
- #146 (v1.2.28): Multi-stage cascade architecture
- #148 (v1.2.29): Four-tier cascade for event-API gaps
- #149 (v1.2.30): Flag-based depth detection with multi-cycle convergence
- #150 (v1.2.30): Asymmetric scan volume for vertically-skewed content
- H-19 (v1.2.6): Block variations need own PBR companions
- H-20 (v1.2.6): pw: namespace blocks need vanilla textures co-located

### Candidate (1+ corroboration but not yet confirmed)
- #147 (v1.2.28): Event-queue dedup via Set with composite key
- #151 (v1.2.30): Asset-side bulk processing via PIL+numpy
- #152 (v1.2.30): Phase-offset flipbook for alive-canopy effect
- #153 (v1.2.30): Molang keyframes with per-entity dynamic base
- #154 (v1.2.31): Iteration order matters with bounded early-exit
- #155 (v1.2.31): Decision journals required complement to phase logs
- H-21 (v1.2.6): sky.intensity sweet spot 0.85-0.95 for cinematic-dark sky
- H-26 to H-30 (v1.2.8): Various visual fixes confirmed standing
- H-32 to H-35 (v1.2.9-v1.2.12): PBR material category lessons (consolidation candidate for v2.0.0)

### Falsified (preserved for historical lineage; do not revive)
- #29 (v1.0.0 → SUPERSEDED v1.0.1): Custom blocks DON'T support per-instance variation — superseded by working permutation system
- #34 (v1.0.0 → UPDATED v1.0.1): "blended leaves" preference — superseded; user happy with alpha_test
- #70 (v1.0.0 → SUPERSEDED v1.0.1): Custom-block variation impossibility
- #72 (v1.0.0 → UPDATED v1.0.1): Z-fighting concerns moot under alpha_test_to_opaque (later v1.1.3 changed to alpha_test)
- #127 (v1.0.1 → FALSIFIED v1.2.6): Cross-pack PBR layering (RP-03 sidecars only) — actually requires same-pack color PNGs

### Superseded (not falsified, just improved upon)
- G-01 (v1.2.0 → SUPERSEDED v1.2.1): keyframe density 25-40+ → 13 sufficient
- G-03 (v1.2.0 → SUPERSEDED v1.2.1): hMin=20/mMax=55 → hMin=5/mMax=35 for cinematic-realism
- G-04 (v1.2.0 → SUPERSEDED v1.2.1, v1.2.2): sun_mie 7-15 → 2.5-3.5; v1.2.2 added system coordination requirement

---

## §3. BACKLOG (queued work, organized by priority)

### HIGH (user-driven action items)

**v1.2.31 in-game verification (PRIMARY)**:
- Stand near canopy, wait 10-15 sec — scanner should populate variants 1-6 across canopy
- Failure mode: leaves stuck uniform after 30+ sec → scanner still broken
- Secondary: canopy size proportional, less puffy
- Tertiary: oak backlight matches jungle/birch translucency

**Scanner architectural follow-up (if v1.2.31 fixes confirm)**:
- Promote Lesson #149 (flag-based depth detection) from CONFIRMED to PROMOTED if reproving costs another cycle
- Promote Lesson #154 (iteration order with bounded early-exit) CANDIDATE → CONFIRMED with corroboration #1
- Promote Lesson #155 (decision journals) CANDIDATE → CONFIRMED with corroboration #1

**v1.0.0 diagnostic priorities** (10 items; status as of v1.2.31 in `ABSOLUTREALISM-DIAGNOSTICS-v1_2_31.md`):
- Several closed (local_lighting cascade, branches/canopy/light/cube/wing_flap fixes, lush_caves doc, render_method)
- ~5 still pending (moon detail, sun disc visibility verification, ore glow projection, deepslate ore matrix, bed texture, armor attachables, Warden summoning, custom biome ambient, mob spawn rules)

### MEDIUM

**Snapshot-and-diff infrastructure**:
- Snapshot pack-stack hashes at session start, after every phase, before ship
- Direct-compare against snapshots to detect mutations early (driven by v1.1.0 anomalous-state events)
- Implementation: shell script + manifest of file MD5s

**PNG batch optimization**:
- Add oxipng + pngquant to build environment
- Could save 5-10% on shipping size with no quality loss

**Manifest diff gate automation (Lesson H-54)**:
- Implement `verify_manifest_diffs.py` step before .mcpack assembly
- Until automated, manual review of stamped manifests is the safety net

**Variant_6 texture authoring**:
- Currently twin to v5 (since v6 art isn't authored)
- If visual diversity insufficient, author dedicated v6 art

**Bark seam audit**:
- Verify all 9 species × 3 tiers = 27 bark textures are seamless (top edge matches bottom)
- v1.2.29 audit ruled "no action" — but if user reports horizontal banding, fix textures

**Section column noise**:
- Adjacent column heights may give noisy section assignment between neighboring leaves
- If user reports, switch to BBox-based detection

**v1.2.27 first-cycle migration cost profiling**:
- Initial 50-radius scan covers ~330k cells
- Budget 120/tick → 138 sec for nearby trees
- Profile in-game

### LOW (nice-to-have, deferred)

**Cherry leaves animation chain** (Phase 1 of older plan)
**All-species leaf flipbook audit** (Phase 1)
**Foliage wind sway investigation** (Phase 2)
**Guide Book** (Phase 3)
**Setup/swim "can't find animation X" log warnings** (need runtime testing — silent fallback works)
**Jungle leaves color B=0** (aesthetic decision: A algorithmic / B re-extract / C color matrix)
**Jungle leaves animation strip waste** (~880 KB recovery)
**54 vanilla orphan terrain_texture entries** (cleanup, v2.0.0 architecture pass)
**Acacia entity geometry rework (L-shape)** (3-option resolution still pending user)
**Slope-aware rest angle for falling trees** (current despawn-after-fall is simpler)
**BIGCANOPY 14-item backlog #1, #2 dynamic canopy sizing** (vs v1.0.0 leaf-volume budget)
**Custom branch worldgen for acacia/cherry/mangrove** (vanilla biome integration deferred)

### POST-COMMERCIAL / POST-MARKETPLACE

**Subpack tier system** (Resolution slider 32x/64x/128x/256x/512x):
- Single-RP-bound, memory_tier auto-selection
- Subpacks declared in manifest
- Held until after marketplace publish

**256x source integration** (Patrix_26_1_256x_basic_zip.001..005):
- Major resolution upgrade pass
- Backlogged

**ff:water_finite finite-water mechanics**:
- Haubna-style fluid simulation
- Big Scripting v2 budget management (~3,000-6,000 simulated water blocks on PS5)
- Scripted fluid propagation
- Locked as post-commercial-release priority

**AmbientSounds 6.3.5 port**:
- 122 dormant `pw:ambient.*` sound events declared but not wired
- ~38 ambient definition JSONs + scripted modifier evaluator
- Audio domain priority (Lesson #143 CANDIDATE: audio > waypoints for ROI)

**Cubemap re-enablement**:
- Currently disabled
- Future End/Nether visual work

**Marketplace publishing prep**:
- Bedrock Marketplace submission requirements
- Content packaging standards
- World template authoring
- Marketplace metadata

**Custom UI/HUD**:
- HUD overlays via `@minecraft/server-ui`
- Custom inventory screens
- Form-based dialogs
- Stats displays

**Achievement/scoring systems**:
- Scoreboard objectives
- Custom achievement triggers
- Progression systems via scripts

**Multiplayer/realm tuning**:
- Realm-specific performance considerations
- Network-bounded scripting
- Client-server state sync

**Vanilla mood subpack** (less-stylized alternative for users who prefer original look)

**Per-biome color grading variation** (currently per-biome temperature only; could vary saturation/contrast per biome too)

**Time-keyframed sky intensity** (currently static per biome; could keyframe through day for dramatic transitions)

### v1.2.32+ candidates (queued for next iteration)

**Backlit leaves enhancement** (if v1.2.31 oak still under-translucent — would require shader tuning, not texture S)

**variant_0 edge cubes** (add 2 -X edge cubes for backside detail if user wants more pokeyness):
- Bumps cube count 8 → 10
- Easy iteration

**Per-biome leaf tints** (C-5):
- Author leaf textures with biome-specific color baked in
- jungle saturated greens, autumn yellow-greens, taiga blue-greens
- Combined with existing biome color_grading

**Enhanced normal maps** (C-9):
- Re-author bark normal maps with stronger relief for deeper grooves

**Mid-fall break for tall trees** (C-13):
- mature/old trees > 16 tall hitting hard ground break at midpoint
- Spawns TWO falling-tree entities with split geometry
- High asset effort

**Knot/branch panel variants** (C-7):
- Author 1-2 panel-width "knot" textures per species
- ~10% of dodecagon panels use knot variant

**Bark debris particles on impact** (C-11):
- Dust/wood-chip particle cloud at falling tree impact point

**Branch-break item entities** (C-12):
- Spawn 1-3 small wood-item entities flying outward at impact
- Players pick up as gameplay reward

**onPlayerInteract leaf rustle**:
- Block component lifecycle hook fires sound + small particle
- Tactile forest feel

**Local lighting on outer leaves** (C-3) — test PS5 perf first

**Canopy ambient particles** (C-4) — 1-in-200 chance during outer-leaf classification

### v2.0.0 ASPIRATIONAL

**Lesson library consolidation (Rosetta Stone structure)**:
- Lesson families (parent-child) — when delta repeats across many children, suspect parent is incomplete; fewer rules with closer-to-root truth is the goal
- Promote Lesson #146 to confirmed Rosetta Stone parent: state-driven block variation system (snow accumulation, biome blooms, damage propagation, wetness/dryness)
- Consolidate H-32, H-34, H-35 into a parent for "PBR replacement of variant-driven blocks" with deltas per material category

**Decorative entity overlay**:
- Passive `pw:tree_decoration` entities attached to standing trees
- Random per-instance variants (extra branches, vines, leaf clusters)
- Cost: 1 entity per "important" tree (mega jungle, fancy oak elder)

**Two-phase ship pattern documentation** (architecture + polish):
- Pattern proven in v1.2.29+v1.2.30 dual-phase ship
- Apply to v1.3.0 subpacks resolution tier launch:
  - v1.3.0a: subpack manifest infrastructure (architecture)
  - v1.3.0b: 32x/64x/128x/256x asset variants (polish + asset)

**Foundation document v2.0.0**:
- Aggregate all v1.x.x handoffs + foundation doc into v2.0.0 foundation
- Universal rules where v1.x had species-specific deltas
- Reduced lesson count via parent-child consolidation
- Falsified candidates removed
- Promoted candidates incorporated
- Regression-prevention verification suites for older packs/documents

---

## §4. AUTHORIZATION AUDIT TRAIL

Significant decisions where the user explicitly authorized a path:

- **v1.0.1 rename**: PatrixWorld → Abs0lutRealism (UUID-stable rename, 2026-05-07)
- **v1.1.0 perf pass**: Forest crash fix on PS5 (chunk-load gate + tightened scan) (2026-05-07)
- **v1.1.3 Conservative atmospherics tier**: User confirmed Conservative selection out of three offered (2026-05-08)
- **v1.2.0 lens flare implementation**: Path B selection (2026-05-08)
- **v1.2.0 cinematic mood pass**: User authorized "Fold into v1.2.0" with 500-turn budget (2026-05-08)
- **v1.2.0 Vibrant BSL Lite Edition**: User explicitly REJECTED as too extreme (2026-05-08)
- **v1.2.27 Option C (combined Phases 1+2+3)**: User authorized combined leaf overhaul (2026-05-10)
- **v1.2.31 fixes**: User authorized combined options 2+3 scanner fix + variant_0 redesign + MERS asymmetric option C (2026-05-10)
- **Master-doc consolidation (this document set)**: User requested 4 master docs to replace project knowledge (2026-05-10)

---

## §5. PROCESS EVOLUTION

### Standing protocol — current state

Every "please continue" turn (and any turn that could involve action) starts with:
1. `tail -40 _logs/phase_log.md`
2. `find . -type f -mmin -90` for working file mtimes
3. `ls -la /mnt/user-data/outputs/` for output state
4. `ls _logs/v1_*_*.json _build/v1_*_*` for in-progress markers
5. `tail -80 _logs/decision_journal.md` (v1.2.31+ addition)

Failure-mode prevention:
- Re-execution of completed work (would double-apply changes)
- Anomalous-state misclassification (file already at proposed value — not a mutation, just prior-turn work)
- Picking up at wrong phase
- Shipping half-built deliverable

### Decision-journal protocol (NEW v1.2.31)

In addition to phase log (records milestones), maintain decision journal that captures:
- DECISION (chose between alternatives)
- OBSERVATION (discovered something non-obvious)
- ASSUMPTION (proceeded under uncertainty)
- VERIFICATION (confirmed/falsified hypothesis)
- DEFERRAL (knowingly skipped for later)
- CONTRADICTION (user input or new evidence contradicted prior position)

Cleanup rule: archive `decision_journal.md` and `phase_log.md` to `/home/claude/_logs/archive/v<old>_journal.md` BEFORE deleting build dirs.

### Authorization gate — amnesia recovery (v1.1.3+)

When found work corresponds to a multi-choice option I had offered:
> "Amnesia recovery: I see [work X] was completed. This corresponds to [the option I offered, named specifically]. Two questions:
> 1. Did you actually select this option, or was it executed without your explicit approval?
> 2. Has anything changed in your intent since this work was started?"

WAIT for user response before proceeding with verification, presentation, or further building.

### Lesson-promotion criteria

- CANDIDATE → CONFIRMED: 1+ independent corroboration in different context
- CONFIRMED → PROMOTED: reproving cost a release cycle (expensive lesson)
- Tracked in this document; v2.0.0 will incorporate the consolidation

---

## §6. END OF HISTORY-AND-BACKLOG DOCUMENT

For locked invariants and lessons library, see `ABSOLUTREALISM-FOUNDATION-v1_2_31.md`.

For technical system architecture, see `ABSOLUTREALISM-ARCHITECTURE-v1_2_31.md`.

For known unresolved diagnostic issues, see `ABSOLUTREALISM-DIAGNOSTICS-v1_2_31.md`.

*Document authored 2026-05-10 as part of the master-doc consolidation. Supersedes all prior handoffs / READMEs / changelog sections through v1.2.31.*

---

## §7. POST-v1.2.31 RELEASES (v1.2.32 → v1.2.36)

> *[v4 editorial: renumbered from v3’s appended duplicate §3; content untouched.]*

This section continues the per-version chronicle for releases shipped after the v1.2.31 history was frozen.

### v1.2.32 — 2026-05-10 (Leaf overhaul + Patrix-authentic MERS + inner-core saturation + U4 atmospherics)

**Status**: SHIPPED + visually verified.

**Deliverables** (v1.2.32 final):
- `AbsolutRealism-v1_2_32-MAIN.mcaddon` (12 packs) — MD5 `59efee105d17c0f7e7c8c982b3049631`
- `AbsolutRealism-v1_2_32-ATMOSPHERICS.mcaddon` (BP-01 + RP-02 with U4 applied)
- `RP-04-Abs0lutRealism-Basic-RP-v1_2_32.mcpack` (version-bump only)
- `RP-07-Abs0lutRealism-Neutral-Mobs-RP-v1_2_32.mcpack` (version-bump only)

**Changes**:

| Change | Files touched |
|---|---|
| Q1: variant_0 → A-Sweet-Spot geometry (core 12×16×12, faces 6×6×3, slabs 8×4×8, corners unchanged) | `RP-09/models/blocks/pw_leaves_variants.geo.json` |
| Q2+Q3: Patrix-authentic MERS, all 9 species × 7 variants (54 textures) | 54× `RP-09/textures/blocks/pw_*_leaves_v*_mer.png` |
| U2: Two-layer leaf cube — saturated inner core | 54× new `_inner.png` + 54× new `_inner.texture_set.json` + 54 entries in `terrain_texture.json` + 6 cubes in geometry got face-level `material_instance: "inner_core"` + 63 perms in 9 BP block JSONs got `inner_core` material |
| U3: Per-species SSS tier (jungle high SSS, spruce low SSS, pale_oak G=4 emissive) | embedded in MER values per Q2 |
| U5: Per-frame roughness flipbook variance (R deltas [+8, -5, +12, -8, +5, -10, +15, -7]) | embedded in MER values per Q2 |
| U4: Atmospherics warm-tint at golden hour | RP-02/lighting/global.json + RP-02/color_grading/color_grading.json |
| Manifest version bump | 16× `*/manifest.json` (v1.2.31 → v1.2.32) |

**Per-species MERS targets (final)**:

| Species | M | E | R | S |
|---|---|---|---|---|
| oak | 0 | 0 | 210 | 205 |
| spruce | 0 | 0 | 220 | 170 |
| birch | 0 | 0 | 225 | 200 |
| jungle | 0 | 0 | 200 | 235 |
| acacia | 0 | 0 | 225 | 195 |
| dark_oak | 0 | 0 | 215 | 180 |
| mangrove | 0 | 0 | 210 | 215 |
| cherry | 0 | 0 | 210 | 215 |
| pale_oak | 0 | 4 | 215 | 195 |

**U4 details** (sun illuminance +15% at golden-hour keyframes, ambient color amber bias, color grading highlights warm):

| Keyframe | Sun illuminance old | New (×1.15) |
|---|---|---|
| `0.225` (sunset golden) | 85.0 | 97.75 |
| `0.250` (sunset orange) | 35.0 | 40.25 |
| `0.750` (sunrise dim) | 15.0 | 17.25 |
| `0.775` (sunrise golden) | 85.0 | 97.75 |

Ambient color amber bias at golden hour (R+8, B−8 push):

| Keyframe | Old | New |
|---|---|---|
| `0.220` | [205, 175, 145] | [213, 175, 137] |
| `0.250` | [200, 145, 120] | [208, 145, 112] |
| `0.750` | [200, 145, 120] | [208, 145, 112] |
| `0.780` | [205, 175, 145] | [213, 175, 137] |

Color grading highlights warm bias: `highlights.gain` `[1.1, 1.1, 1.1]` → `[1.15, 1.10, 1.05]`.

**Godray penetration through 4-deep canopy**: 36.7% (vanilla 31.85%; v1.2.31 was 10.3%). +15% over vanilla.

**Critical mid-build correction**: Material_instance binding is at FACE level (`cube.uv.face.material_instance`), NOT bone-name level. Initial Phase 1 split cubes into `inner_core` and `leaves` bones. Got verified at static check level but web research before shipping caught that bone-name binding is the entity render-controller pattern. Fixed by adding face-level `material_instance` to all 6 faces of each inner_core cube. → Lesson #157.

**Lessons added**: #154 (MERS sampling at alpha ≥ 128), #155 (3 string deps preserved correctly), #156 (LabPBR-to-MERS conversion), #157 (per-face material_instance binding), #158 (godray geometry — only inner-footprint cubes), #159 (U4 surgical golden-hour edits). See FOUNDATION-v2 §6.5.

### v1.2.33 — 2026-05-10 (REGRESSION — variant_0 12×16×12 broke alpha-test rendering)

**Status**: SHIPPED → KNOWN BROKEN. NEVER USE THIS VERSION.

**Intent**: Restore variant_0 to "alpha-test era" puffy design + falling tree fixes.

**Changes attempted**:
1. variant_0 core 12×16×12 → 16×16×16 (intent: eliminate floating bits)
2. Defer playAnimation + playSound by 2 ticks (block-clear sync)
3. Animation timing: 2s slow lean + accel + impact at 3.4s + bounce
4. Render controller color multiplier [0.82, 0.79, 0.74] for bark

**What broke**: User reported leaves with "opaque green undersides + Z-fight" in canopy. Full investigation in v1.2.34 cycle determined the inner_core resize had introduced coplanar shared faces with surrounding cubes, causing depth-buffer z-fight in alpha-test rendering. The "opaque green" was the upward-facing inner_core face rendering instead of the (transparent) underside of the slab above it.

**Action**: superseded by v1.2.34 with regression investigation, full variant_0 redesign, and additional fixes. v1.2.33 deliverables not used; v1.2.32 remains the last KNOWN-GOOD baseline through v1.2.34 ship.

### v1.2.34 — 2026-05-10 (Regression fix + extras: scanner unification, leaf-loot, falling-tree timing, birch dodecagon)

**Status**: SHIPPED + visually verified.

**Deliverable MD5**: `775566a634097853631669c28368f4c2` for `AbsolutRealism-v1_2_34-MAIN.mcaddon`

**5 fixes**:

1. **variant_0 redesign — 15 cubes**: 8 corner puffs (4 top + 4 bottom) + 4 face puffs + 2 slabs + inner_core 14×14×14. The inner_core was reduced from 16×16×16 (v1.2.33) to 14×14×14 at offset [-7,1,-7] to eliminate coplanar shared faces with adjacent puffs (per the newly-confirmed Lesson #161). This z-fight-safe design was preserved through v1.2.35 and v1.2.36.

2. **Unified scanner + randomizer in BP-02**: Combined the prior tier-1 (section flag scanner) + tier-2 (variant scanner) into one pass. (Later rewritten in v1.2.36 due to performance issues.)

3. **Leaf-loot setblock destroy fix**: Replaced `setblock destroy` with `setPermutation(air)` + manual loot rolls in script. The previous approach (`setblock destroy`) bypassed `match_tool` conditions in the loot table (MCPE-50331) — shears were giving stick drops instead of sapling drops. New code checks `player.getComponent('equippable').getEquipment(EquipmentSlot.Mainhand)?.typeId` against `minecraft:shears` and rolls sapling vs stick drops accordingly. → Lesson #160.

4. **Falling-tree timing flip**: Entity spawns FIRST, then blocks clear +1 tick later. Combined with the script defer (2 ticks before animation), this prevents the entity from visually overlapping with not-yet-cleared logs. From the player's perspective: log breaks → tree appears solid for ~100ms → tree starts the slow lean.

5. **Birch dodecagon geometry**: Sub-pixel corrected panel widths for the 12-sided birch vine geometry. Bad math (using `w = r` or `w = 2 × r × sin(15°)`) was producing visible gaps or overlaps between panels. The corrected widths use `w = 2 × r × tan(15°)` ≈ 0.5359 × r:
   - r = 3 → w = 3.2154
   - r = 3.5 → w = 3.7513
   - r = 3.75 → w = 4.0192

   → Lesson #163.

**Lessons added**: #160 (setblock destroy bypasses match_tool / MCPE-50331), #161 (alpha-test tolerates volume overlap, NOT coplanar shared faces), #162 (worldgen never fires onPlace), #163 (dodecagon panel chord formula). See FOUNDATION-v2 §6.5.

**Mid-build incident**: Z-fight bug discovered mid-build when user pointed out a specific cube combination would conflict. Required mid-stream geometry adjustment.

### v1.2.35 — 2026-05-10 (Variant geometry refinements — KNOWN GRAPHICS-RESET BUG)

**Status**: SHIPPED → KNOWN BUG (graphics resets in dense forests at sprint). Superseded by v1.2.36.

**Deliverable MD5**: `d3cb76bdc403ad1e98c3b210f949e6b5` for `AbsolutRealism-v1_2_35-MAIN.mcaddon`

**Changes**:

1. **Variant_3 redesign**: 8 corner puffs (4 top + 4 bottom) + inner_core 14×14×14 = 9 cubes
2. **Variant_4 redesign**: 4 mid-corner puffs + 4 face puffs depth 4 + inner_core 14×14×14 = 9 cubes
3. **bee_oak_with_vines re-routing**: `pw:oak_elder_with_branches` → `pw:oak_mature_with_vines_tree_feature`

**Bug emerged in user real-hardware testing**: "Everything loaded and looks beautiful. BUT scanner/randomizer bugging — graphics reset (everything goes dark, slowly reloads visually) — happens specifically in dense forests AND only while running (not walking). Canopy leaf blocks not visibly being replaced/randomized."

User was NOT being kicked from the world. Visual-only stall. Required complete scanner re-architecture for v1.2.36.

### v1.2.36 — 2026-05-10/11 (Scanner architecture rewrite — AWAITING USER VERIFICATION)

**Status**: SHIPPED → AWAITING USER VERIFICATION. See `CURRENT-STATE-v1_2_36.md` for full details.

**Deliverable MD5s**:

| File | Size | MD5 |
|---|---|---|
| `AbsolutRealism-v1_2_36-MAIN.mcaddon` | 379 MB | `5f16b20fba1c802901d4bcc488c4d3cb` |
| `AbsolutRealism-v1_2_36-ATMOSPHERICS.mcaddon` | 111 MB | `4f3cd67ee6c9c4ab03899acf0b3b0463` |
| `RP-04-Abs0lutRealism-Basic-RP-v1_2_36.mcpack` | 159 MB | `2bde2059ccd80617acd779cc435f6a45` |
| `RP-07-Abs0lutRealism-Neutral-Mobs-RP-v1_2_36.mcpack` | 206 MB | `b4825a57c213ec1b0b414b784e392f8f` |

**Root cause of v1.2.35 graphics-reset bug**:

The scanner did a synchronous 36,414-cell loop in one tick. Worst case in dense forest:
- 36,414 cell reads (the scan box: 51×51×14)
- Plus 120 marks × 70 reads = 8,400 additional reads (`detectSectionAndExposure`)
- = ~44,800 getBlock reads per scanner cycle, all in one tick

Bedrock uses QuickJS without JIT. Each `getBlock` costs ~10-30μs in interpreted context. 44,800 × 20μs = ~900ms per spike.

Bedrock script watchdog thresholds:
- `spike-threshold`: 100ms (warning + corrective action)
- `hang-threshold`: 3000ms (kicks the script)
- `slow-threshold`: 2ms (warning over multiple ticks)

The 900ms spike exceeded the 100ms threshold by 9×. Spike events don't kick the player but DO trigger engine corrective action — the render pipeline stalls and chunk meshes briefly go dark/missing. **That's the "graphics reset" symptom.** Matches MCPE-173706 pattern.

**The v1.2.36 architectural fix (locked spec)**:

1. **`system.runJob` with generator yields** — engine time-slices automatically across multiple ticks
2. **`dimension.getBlocks(volume, {includeTypes: PW_LEAF_TYPES_ARR}, true)`** — native C++ batch filter, ~100× faster than nested JS loop
3. **In-memory `_pwProcessedFlags` Map** — no `pw:section_rolled` state writes; eliminates GC pressure
4. **5-layer downward sweep** — 51×10×51 per layer, 5 layers covering player.y+35 down to y-15, 2.5s full sweep
5. **Movement-triggered cadence** — >8 blocks movement triggers next sweep (squared dist 64)
6. **Teleport detection** — >16 blocks/tick (squared dist 256) clears flag map + 10t settle delay

**Variant scheme (locked)**: 7 variants total, ALL 9 cubes uniformly, ALL sharing `inner_core 14×14×14 at [-7,1,-7]`. v0 = worldgen safety net (symmetric 8 corners). v1+v2 = bottom asymmetric pair. v3+v4 = middle asymmetric pair (diagonal corners). v5+v6 = top asymmetric pair. Pair selection by `((x+y+z)%2+2)%2` parity. See ARCHITECTURE-v2 §2.9 for full geometry coordinates.

**Diagnostics**: BP-02 emits 5-second aggregated chat reports via `world.sendMessage`. Toggle: `/scriptevent pw:diag_on` / `pw:diag_off` / `pw:scanner_force_sweep` / `pw:scanner_clear_flags`.

**BIGCANOPY cascade fix**: replaced `_enqueueCascade(p, dim.id)` with `_pwProcessedFlags.delete()` for 6 face neighbors + self when falling-tree clears leaves.

**Lessons added (CANDIDATE pending verification)**: #170 (system.runJob official pattern), #171 (getBlocks ~100× faster than nested loop), #172 (setPermutation triggers mesh rebuild even for no-op), #173 (position parity sufficient for mirror pair selection), #174 (BlockVolume has no documented hard size limit), #175 (graphics reset = render-pipeline stall, NOT watchdog kick). See FOUNDATION-v2 §6.5.

**Investigation rounds**: Round 1 identified scanner synchronous loops as a contributor but did not nail the watchdog spike-threshold vs render-pipeline stall distinction. User had to ask for round 2. Round 2 surfaced MCPE-173706 pattern match and the QuickJS no-JIT timing math. → Pattern 2 in OPERATING-MANUAL-v2 §3.2 (Initial investigation too shallow).

**Build incidents**:
- `_enqueueCascade` was left dangling after Phase 2 splice was cut by turn budget. Caught at start of next turn via grep audit. → Pattern 3 (turn budget exhaustion).
- Initial Python rename loop ran without renaming due to underscore-vs-hyphen separator confusion. → Pattern 4 (shell environment assumptions).
- Consolidated session-handoff doc was written but `present_files` was never called. User had to ask twice. → Pattern 6 (forgetting present_files).

---

## §8. END OF HISTORY v2 (v3-era closing marker)

> *[v4 editorial: renumbered from v3’s appended duplicate §4; content untouched.]*

For current ship status, queued work, and the 10 post-ship diagnostic priorities, see `CURRENT-STATE-v1_2_36.md`.
---

# PART II — THE LEAF-RENDERING LONG MARCH: v1.2.37 → v1.2.52
*Sources: HANDOFF-v1_2_36-through-v1_2_48.md (2026-05-14), HANDOFF-v1_2_49.md (2026-05-14), HANDOFF-v1_2_49-through-v1_2_52.md (2026-05-15). Lessons L1–L10 carried in full at §II.8. Time span ~5 days; 16 versions + one skip + one double-build.*

**Arc summary.** v1.2.36's scanner rewrite (chronicled at Part I §7) **broke silently for five versions** before a full revert (v1.2.41) restored the proven v1.2.35 architecture; v1.2.42 then added the layered+BFS design the rewrite had been reaching for. Leaf geometry iterated through tapered protrusions, a sand PBR rebuild intervened (v1.2.46), a texture misdiagnosis cost two cycles (v1.2.47→48), and the v1.2.49→52 chain resolved animation-shim errors, the snow warning, black-leaf corruption, and the far-distance render problem — ending at **v1.2.52, the first USER-VERIFIED-WORKING build of the entire v1.2.36→52 arc** ("everything looks and is working perfectly").

### v1.2.37 — 2026-05-13 (Cadence boost + asymmetric inner_core + atmospherics)

**Type**: Feature/tuning on the (still believed working) v1.2.36 scanner.

**What shipped**:
1. Scanner cadence: `PW_MOVE_THRESHOLD_SQ` 64→16 (4-block cadence), +15s force-sweep.
2. Per-variant asymmetric inner_core (line-pattern fix): v0 baseline 14×14×14; v1 bottom-sealed, v2 top-sealed, v3 north-sealed (+Z), v4 south-sealed (−Z), v5 east-sealed (+X), v6 west-sealed (−X). Adjacent leaves seal different faces → grid pattern breaks into random speckle.
3. Atmospherics: Rayleigh mid-day 0.2→0.3 (×1.5); Rayleigh golden hours 1.25→1.4 (×1.12); volumetric scattering.air ×1.25 across all 51 biome fogs; distance-to-opaque fog untouched per user spec.
4. Firefly Bush overhaul: palette PNG→RGBA (Lesson #128); 4 dim olive blobs → 40 small bright fireflies in 5 color variants (golden, amber, green-yellow, honey, chartreuse); 6-frame flipbook @ 6 ticks/frame (3.6s twinkle); MER emissive G 0→250; `firefly_emitter` particles max 5→20, spawn_rate (0.4,1.2)→(2.0,4.0), wider spread. *(The G=250 emissive later resurfaced as the "bright balls" bug once VV actually rendered — Part III.4.)*

**Status**: SHIPPED → SUPERSEDED. The cadence boost fed v1.2.38's watchdog concerns. User reported "nothing happening" — first inkling the v1.2.36 scanner was dead.

### v1.2.38 — 2026-05-13 (Scanner re-architect + first diagnostic surface)

**Type**: Scanner re-architecture on a misdiagnosis (watchdog assumed the problem) + diagnostic instrumentation.

**What shipped**:
- Layers 5×10 → 7×8 with 1-unit overlap; `PW_LAYER_CENTERS = [38, 31, 24, 17, 10, 3, -4]`; per-layer ymin = center−3, ymax = center+4; range y−7..y+42; per-layer cells 26,010→20,808 (−20%).
- Diagnostics: `PW_DIAG_REPORT_INTERVAL` 100→60 ticks; forced first-sweep chat broadcast at world load (+3s); try/catch around `dim.getBlocks()` with explicit error logging; `_pwSpikeWarnings` counter (any layer scan >50ms).

**Crucial outcome**: the try/catch surfaced the BlockVolume API error in v39 testing — the diagnostic addition made the real bug visible. First version where the BIGCANOPY warning surfaced an error.

**Status**: SHIPPED → led directly to v1.2.39.

### v1.2.39 — 2026-05-13 (BlockVolume API hotfix)

**Type**: API-contract hotfix.

**The discovery** (content log): `TypeError: Object did not have a native handle. Function argument [0] expected type: BlockVolumeBase`.

**Fix**: `dim.getBlocks({from, to}, filter, true)` → `dim.getBlocks(new BlockVolume(from, to), filter, true)` (class instance, not object literal; import already present).

**Result**: API error gone; scanner still misbehaved in mass deployment → set up the v41 revert.

**Status**: SHIPPED → SUPERSEDED.

### v1.2.40 — SKIPPED

The version number was never used; the line went v1.2.39 → v1.2.41.

### v1.2.41 — 2026-05-13 (Scanner reverted to v1.2.35 architecture)

**Type**: Full architectural revert — the right call.

**Forensic analysis of archived BP-02 packs**: v1.0.1→v1.2.24 (working) used `system.runInterval` (100t), per-cell `getBlock`, two-stage queue, multi-trigger redundancy (heartbeat + cascade re-flag + playerBreakBlock + playerSpawn). v1.2.28→v1.2.35 (still working) added section/exposure pools on that skeleton. v1.2.36+ (rewrite, broken) lost ALL redundancy paths and died silently.

**Fix**: v1.2.35 scanner restored wholesale; block JSONs / render controllers / atmospherics / firefly bush / v37-38 leaf features carried forward unchanged.

**Variant pool (NEVER variant 0 per user requirement)**:
```js
const PW_LEAF_VARIANT_POOLS = {
  "0_1": [1, 1, 2, 2],   // bottom outer
  "1_0": [3],            // middle inner (vestigial)
  "1_1": [4],            // middle outer
  "2_1": [5, 5, 6, 6],   // top outer
  "0_0": [3],            // bottom inner (vestigial)
  "2_0": [3],            // top inner (vestigial)
};
```

**Status**: SHIPPED → became the proven baseline all later versions build on. → Lesson L1 (§II.8).

### v1.2.42 — 2026-05-13 (Layered scanner + Tree-BFS + Verification)

**Type**: Scanner architecture upgrade on the proven skeleton. **This became the working scanner architecture through v1.2.48+.**

**What shipped**:
1. 6-layer player-relative scan: L1 y+14..21 (baseline canopy), L2 y+7..14 (low canopy/saplings), L3 y+21..28 (taller trees), L4 y+0..7 (ground brush), L5 y+28..35 (very tall), L6 y+35..42 (megatree tops, double-up weighting). Layers share a single mark-budget (800/cycle); horizontal radius ±25.
2. Tree-completion BFS: unflagged leaf → flood-fill same-species 6-face neighbors, cap 3000 cells/pass, walks through flagged neighbors for connectivity, shares mark budget.
3. Verification + retry script (third of the trio): re-marks leaves that drifted back to unflagged.
4. Diagnostic overhaul with aggregated stats.

**Status**: SHIPPED → confirmed working.

### v1.2.43 — 2026-05-13 (Tapered-protrusion leaf geometry)

**Type**: Leaf variant geometry redesign.

**Problem (v1.2.42 "puffs")**: single 4×4×4 cubes read as balloons — square silhouettes, one-voxel attachment (floated visually), identical sizes ("ring of puffs"), hard right angles.

**New design**: each protrusion = 3-cube tapered wedge stack — base (3×3×3 or 3×4×3, overlaps inner_core by 1 voxel), mid (2×2×2 or 2×3×3), tip (1×2×1 or 1×1×1, reaching to ±14). 7 variants × 4 protrusions × 3 cubes ≈ 168 cubes total.

**Status**: SHIPPED → geometry baseline for v44/45/47/48.

### v1.2.44 — 2026-05-13 (Tree feature conflict + alpha-cutout inner textures + vines + cross-block edges)

**Type**: Three-tier fix/feature release.

**Tier 1 — vanilla 1×1 trunk fix**: BP-02 and BP-05 both defined the same 9 `minecraft:*_tree_feature` IDs; load order picked the winner, and when BP-02 won, vanilla square `minecraft:oak_log` placed instead of pw dodecagons. Fix: deleted 12 duplicate tree features from BP-02; created 3 new BP-05 aggregates (roofed→dark_oak_elder, undecorated_jungle→jungle_young, jungle_bush→pw:jungle_bush); added BP-05→BP-02 manifest dependency forcing BP-02 to load first.

**Tier 2 — leaf geometry**: (A) all 54 inner textures (9 species × v0-v5) converted from `alpha=64` semi-transparent to true alpha-cutout (bg 0, leaf 255) — inner_core renders as translucent clusters, not solid green; (B) cross-block edge cubes, 1-2 per variant, extending up to 6 voxels into neighbors to hide grid lines (v0 top, v1 bottom, v2 top, v3 north, v4 south, v5/v6 east/west).

**Tier 3**: 4 new vine variants for birch + spruce (was oak-only).

**Status**: SHIPPED.

### v1.2.45 — 2026-05-13 (Cut 2 + bug fixes)

**Type**: Performance trim + 2 bug fixes.

**What shipped**: wedge stacks 4→3 cubes (168→140 total, −17%); tips still reach ±14 (steeper taper); cross-block edges preserved; inner core unchanged (locked §6.16). Bug 1: `pw:jungle_bush_feature` trunk_height `{base,variance,scale}` → required `{range_min: 2, range_max: 2}`. Bug 2: MARKER-C version drift ("v1.2.42 layered" string survived v43/v44 unbumped).

**MD5SUMS**: MAIN `da15c6bb1526898b8a7c53095ef7d7f3`; ATMOSPHERICS `47242c45ae6f59b3d53dce1583f3e73a`.

**Status**: SHIPPED → user's 5-screenshot review identified: horizontal gaps between stacked leaf blocks (CONFIRMED — vertical edges missing), texture "stretching" (MISDIAGNOSED — see v47/48), v3=0 across 103 marked leaves (CONFIRMED — classifier BFS biases all leaves to exposure=1), asymmetric pokey-out branches desired, sand edge blending desired ("custom sand exists, find it").

### v1.2.46 — 2026-05-14 (Sand PBR rebuild from ambientCG)

**Type**: Complete sand texture pipeline rebuild.

**Why**: the "find the custom sand" exchange (I grepped `sand.png`/`"sand"`, declared none; actual naming was `pw_sand_v1..v29` / `pw_red_sand_v5..v31` → Lesson L3). Discovery: 9 ambientCG sources at 1024×1024 existed on the build machine; the shipping 256×256 textures had been **over-blurred by the prior pipeline's plain-LANCZOS downscale**, destroying dune detail.

**Decisions**: dropped Ground099 (too dark), 052 (greenish), then 027/054/080 (no visible dunes); kept Ground033 (favorite) + 093A/B/C. Sand (24 variants) from Ground033 only — 16 crop×rotation + 4 hue-extreme + 4 flip; red sand (24 variants) from 093A/B/C — 8 each. Targets: sand RGB (220,205,175) "Florida cream"; red sand RGB (180,110,75) "Mars red". Aggressive clustering: `L_WEIGHT=0.95`, hue ±0.4° std / ±1.0° extreme, brightness ±0.8%/±1.5% → mean ΔE 0.64 sand / 0.48 red sand, max pair 2.39/1.59 — mostly below the ΔE 2.3 JND.

**Pipeline (formal)**: color 512×512 = LANCZOS + UnsharpMask(1.5, 130, 2) + Lab calibration + per-variant micro-shift (→ L5); normals = pixel rotation + **encoded-vector rotation math** (90°: X'=−Y, Y'=X; 180°: −X,−Y; 270°: Y,−X; flip_h: −X,Y; NEAREST resampling) (→ L4); MERS RGBA at format 1.21.30: R=0, G=0, B=roughness, A = subsurface via B2 formula `S = 25 − (AO/255)×15` clamped [10,25] (→ L6). Output: 48 color + 48 normal + 48 MERS + 48 texture_set.json; terrain_texture `pw_sand`/`pw_red_sand` → v1..v24 arrays at uniform weight 4. RP-04 grew 159→198 MB. 146 old files backed up to `_logs/v46_sand_backup/` (build machine only).

**Build incident**: "No space left on device" during bundling; ~5GB of old build dirs cleaned before retry.

**MD5SUMS**: MAIN `5be8ba210fa2312767c27aca77644a26` (380 MB); ATMOSPHERICS `93396a557953914f6849a5ab2c13bbbf` (111 MB); RP-04 `0e724159a60c4ab4623632a2d08c38c2` (198 MB); RP-07 `47d61e0d36d9ba2940770b602f19c8af` (205 MB).

**Status**: SHIPPED → testing deferred into the v46+v47 combined target. (Sand later user-verified "amazing" during v48 desert testing.) Note: no README-v1_2_46 survived — overwritten in outputs by v47 before staging.

### v1.2.47 — 2026-05-14 (Leaf bone geometry final pass — texture regression introduced)

**Type**: 5-item bundled leaf release + scanner audit. Introduced the texture regression.

**What shipped**:
1. texture_height 16→128 in all 7 variant descriptions (FROM THE PRIOR-TURN MISDIAGNOSIS of v45 "stretching").
2. Vertical cross-block edge cubes on ALL 7 variants (top to y=19, bottom to y=−1).
3. Per-cube UV tile variation `uv: [0, N*16]`, N 0-7.
4. v3 repurposed → VERTICAL-SPIKE (4 thin 1×6×1 sticks pointing up, no horizontal corners).
5. v6 repurposed → WILD SCATTER (6-8 random sticks + 3-cube asymmetric inner cluster replacing the 14×14×14 core).
6. Y-jitter + 60/40 wedge/stick shape randomization on v1/v2/v4/v5.

**Scanner audit (no code change)**: `detectSectionAndExposure()` BFS cascade biasing all leaves to exposure=1 is a mathematical property, not a bug; v3=0 solved by pool redistribution: `"0_1": [1,1,2,3]`, `"1_0": [3]`, `"1_1": [3,4,4]`, `"2_1": [3,5,5,6,6]`, `"0_0": [3]`, `"2_0": [3]` → predicted v3 ≈ 25% of marked leaves.

**Cube budget**: 96 total across 7 variants — 31% below v45's 140.

**MD5SUMS**: MAIN `049e49292fe913dac992f05f3e35616d`; ATMOSPHERICS `f7099b2ffca8f85f31a0bacc16db7ae9`; RP-04 `13ffb8aa9be2300090556f3de556be1d`; RP-07 `3ff7dc4cd13e47629a535707b1051121`.

**Status**: SHIPPED → user: "leaves look bad — just the texture." → v1.2.48. **Build incident**: built end-to-end but present_files/staging never executed same turn; user saw stale v46 outputs and re-sent decisions (Pattern 6).

### v1.2.48 — 2026-05-14 (Texture_height revert hotfix)

**Type**: Surgical revert of the v47 regression, keeping everything else.

**The mechanism, precisely**: v45 with `texture_height=16` on the 128×1024 texture sampled 32×256 px per face (8.0×64.0 px per declared unit) → two full leaf tiles compressed per face = the GOOD "dense leaves" look. v47's `texture_height=128` sampled 32×32 px → 1/4 of one tile = the fragment rendering the user rejected. The v45 "stretching" complaint had never been a defect — → Lesson L2.

**Fix**: texture_height 128→16 on all 7 variants; all 492 face UV entries reset `[0, N*16]`→`[0, 0]`. **Kept from v47**: vertical edges, v3 spike, v6 scatter, Y-jitter + shape randomization, pool redistribution (~25% v3), all v46 sand. Cube count 96.

**MD5SUMS**: MAIN `7b74c4f16023496effabf413f55fe3ae` (380 MB); ATMOSPHERICS `960308a0497312542b2cbf57c1ec4997` (111 MB); RP-04 `46fb03dc1721333351b42cc4400d0d56` (198 MB); RP-07 `86692970592a3aba9807d550f7ab61e7` (205 MB).

**Status**: SHIPPED → the user's desert test verified: leaf rendering correct in-game, sand variations working at blocks.json fmt 1.1.0 (despite Microsoft Learn's 1.21.110 claim), "sand looks amazing."

### v1.2.49 — 2026-05-14 (Snow warning + animation setup shims)

**Type**: Surgical hotfix, two in-game log issues from the desert test.

**Fix #1 — 10 animation setup shims.** `[Animation][error] can't find animation setup`: user hypothesized water caustics; investigation cleared caustics (fog/water schema, not entity animation) and found 10 entity client JSONs declaring `setup` against identifiers defined nowhere. Shims added (no-op, 0.05s loop, placeholder_bone): camel, cow (+mooshroom), fox, goat, guardian (+elder), horse (+donkey+mule), panda, polar_bear, rabbit, sheep. Shim file 22→32 animations; setup coverage 3→13.

**Fix #2 — snow_layer variations warning (Option A).** RP-10, added late, defined `snow`/`snow_layer` variations arrays without the FOUNDATION §5.5 partial-block override pattern; RP-10 loads after RP-04 and its terrain_texture won. Fix mirrors RP-04: `snow_layer_single`→`snow_layer_v2` + `snow_single`→`snow_v2` shortnames; blocks.json overrides for `minecraft:snow_layer` (+isotropic up) and `minecraft:snow` (isotropic). Variations arrays PRESERVED. → Lesson L7.

**Option B REJECTED (decision of record)**: bumping blocks.json format_version 1.1.0→1.21.110 was investigated and rejected on three grounds: (1) Bedrock 1.21.30 makes blocks.json a Content Error when its format_version ≥ the block names it overrides — we override vanilla blocks; Microsoft's own reference example uses 1.19.30, and 1.21.110 belongs to per-block custom JSON, a different file type; (2) variations empirically work at 1.1.0 (desert witness) — evidence outweighs the doc; (3) a 20-major-version jump risks silent total blocks.json failure. If a bump is ever forced, 1.1.0→1.19.30 is the safer middle ground.

**Deliverables**: MAIN `f55700435c0c87f9d5127c8ff8942e85` (380 MB); ATMOSPHERICS `eb57c45cb4baf10d02d1211b66471cb0` (111 MB); RP-04 `ac9f2e74f13496868ba501583b066818`; RP-07 `905d82186a7a0fc3c7ae300f534592ca`.

**Status**: SHIPPED → superseded: the snow warning AND a NEW `swim` animation error persisted into v50 testing — the v49 fixes were incomplete.

### v1.2.50 — 2026-05-14 (23 entity-specific animation shims + blocks.json format-string fix)

**Type**: Completion of both v49 fixes.

**Animation rule discovered (→ Lesson L8)**: generic identifiers (`animation.quadruped.walk`, `animation.common.look_at_target`) fall through to vanilla; **entity-specific identifiers** (`animation.pig.setup`, `animation.guardian.swim`, `animation.fish.flop`) do NOT — they must exist in the overriding pack stack. Full audit → 23 proactive no-op shims: fish.flop, dolphin.move, guardian.swim/move_eye/spikes, squid.move/rotate, tadpole.swim, turtle.move/ground_move, frog.jump, parrot.dance/flying/moving/standing, rabbit.move, sheep.grazing, silverfish.move, axolotl.walk_floor, humanoid.attack.rotations/move, skeleton.attack.rotations, zombie.attack_bare_hand. Shim file 32→55.

**Snow root difference found**: RP-04's working blocks.json had format_version as the STRING `"1.1.0"`; RP-10's was the LIST `[1, 1, 0]`. Converted RP-10 to string form.

**MD5SUMS**: MAIN `5618030d009cc3af55451c0860bbb8a2`; ATMOSPHERICS `525d320a1b1d935d9ea6b2a3583f0bd2`; RP-04 `73e6a928f71831b1a0b01ad8107edd49`; RP-07 `47437420759f3f52ed5288a2b72f5218`.

**Status**: SHIPPED → superseded. v50 testing produced the cleanest scanner log of the arc (v3 ≈26%, stable, all markers firing), but the user flagged black-leaf blotches (acacia/birch/mangrove) and requested the far-distance rendering work.

### v1.2.51 — 2026-05-14/15 (Black-leaf source replacement + v0 opaque + reverse-randomizer) — TWO BUILDS

**Type**: Texture repair + far-render architecture. Two builds under one number; the first was rejected before download.

**First build (REJECTED)**: black pixels "healed" by per-texture average-color patching. User: "You didn't clean all the black" — and disliked the look. → Lesson L10.

**Second build (SHIPPED)** — source-variant replacement: oak natively clean (all v0-v5 preserved); birch/spruce/jungle/dark_oak/pale_oak clean only at v0,v5 → v1-v4 regenerated from them; cherry/mangrove/acacia clean at v0,v1,v5 → v2-v4 regenerated. Method: orientation transforms (flip_h/flip_v/rotate_180/identity) + Lab a/b hue shifts ±3 (max spread ±6), per-tile in the 128×1024 strips. 96 textures regenerated; zero >0.5% black anywhere.

**Far-distance architecture (first form)**: v0 render_method `alpha_test`→`opaque` on all 9 species (18 slots) — v0 becomes a "far block"; NEW reverse-randomizer (`runInterval` 27t) scanning a 50-62 block radial shell reverting `pw:variant != 0` → v0 with `pw:section_rolled=false` + `pw:rseed=false`; forward scanner 40→38t (coprime with 27, LCM 51.3s).

**MD5SUMS (shipped build)**: MAIN `a67f55c5c47b20095f7a971d6f174838`; ATMOSPHERICS `b15f516032a595bd8d403bb4dd7f0966`; RP-04 `0749c2d1f5584f6ad725bb55739b1bf0`; RP-07 `6d4e249ca9df564d3cd0ce96d7b6154e`.

**Status**: SHIPPED → superseded: opaque v0 rendered as solid square blocks up close (opaque doesn't sample alpha — working as designed, looked wrong against v1-v6). → v52.

### v1.2.52 — 2026-05-15 (Vanilla-style v0 + faster scanner) — **THE VERIFIED WORKING BUILD**

**Type**: The far-render solution's final form. **USER-VERIFIED WORKING: "everything looks and is working perfectly."** First verified-good build of the v36→52 arc.

**Decision arc (recorded)**: Fix D (vanilla texture refs) considered → user changed to Fix A+B; Patrix-cropped textures chosen over vanilla-Bedrock references; cadence locked 22/39.

**Fix A — v0 as vanilla-style far block**: `geometry.pw_leaves_v0` 16-cube structure → single 16×16×16 cube (one `leaves` bone); v0 textures regenerated as 16×16 pixel-art (crop of Patrix flipbook tile 0 + LANCZOS); unused `inner_core` slot removed; render_method `opaque` kept → renders at max distance, reads like vanilla Fast leaves at every distance.

**Fix B — scanner cadence**: forward 38→**22t** (1.1s, ~1.7× faster — minimizes the v0 window before randomization); reverse 27→**39t** (1.95s); GCD(22,39)=1, LCM 858t = **42.9s** — coprimality is intentional, minimizing simultaneous-fire contention. **Do not "tidy" these numbers.**

**MD5SUMS**: MAIN `131035ece21900f645faafd096530e08` (379 MB); ATMOSPHERICS `dda87c23a7b52f9f43ddf5e21d9ac9ef` (111 MB); RP-04 `6f33c11dafaf50464bc0569d16241fc9` (198 MB); RP-07 `4fcefe9fbf35cf8c91d1b67b924703e5` (205 MB).

**Status**: SHIPPED → **USER-VERIFIED WORKING.** Known-good baseline; regression diffs go against MAIN `131035ece21900f645faafd096530e08` first.

## II.7 — The known-good leaf-rendering configuration (v1.2.52) [PRESERVED CANONICAL REFERENCE]

*Preserved intact from HANDOFF-v1_2_49-through-v1_2_52 §3 — the product of ~10 versions of iteration plus direct visual verification. Do not change without strong, specific reason and user direction.*

**The engine constraint that shaped everything (→ Lesson L9)**: custom blocks have a binary render-distance classification (Microsoft Learn "Exploring Custom Block Render Distance"): `render_method: "opaque"` = "far block" (max render distance, NO per-pixel alpha); any other method (`alpha_test`, `blend`, …) = "near block" (~half max distance, ~70 blocks, WITH alpha). Vanilla leaves dodge this via an internal LOD swap that custom blocks cannot replicate (Mojang: roadmap-only, 2024 Q&A).

**Solution architecture**:
- **v0 = vanilla-style far block**: single 16×16×16 cube, 16×16 pixel-art texture (Patrix tile-0 crop), `opaque`, only `*` material slot.
- **v1-v6 = detailed near blocks**: multi-cube geometry (7-15 cubes, leaves + inner_core bones), 128×1024 healed flipbooks, `alpha_test`, with the v43-v50 features (vertical cross-block edges, v3 vertical-spike, v6 wild-scatter, Y-jitter, shape randomization).
- **Forward scanner** (22t): randomizes v0→v1-v6 within ~25 blocks of the player.
- **Reverse-randomizer** (39t): 50-62 block shell reverts v1-v6→v0 (clearing `pw:section_rolled` + `pw:rseed`) — walked-away trees become far-renderable again and re-randomize on return.

**Texture state**: oak — v0 16×16 (v52), v1-v5 original clean Patrix flipbooks, v6 aliased to v5. birch/spruce/jungle/dark_oak/pale_oak — v0 16×16; v1-v4 regenerated (v51) from v0+v5; v5 original; v6→v5. cherry/mangrove/acacia — v0 16×16; v1 original clean; v2-v4 regenerated from v0+v5+v1; v5 original; v6→v5. Within-species variety comes from **cube geometry + orientation flips + subtle ±3 Lab hue shifts**, not from divergent textures — explicit user design choice, verified good in-game.

## II.8 — Lessons L1–L10 (full text, carried verbatim; this document is now their carrier of record)

### Lesson L1 — Multi-trigger redundancy is hard-won field knowledge
**Family**: Bedrock scripting architecture
**Pattern**: When replacing a working architecture with a new one based on official docs, OLD multi-trigger redundancy paths (heartbeat + cascade re-flag + playerBreakBlock + playerSpawn) often encode field-tested edge case coverage that the new docs don't mention. Strip them at your peril.
**Evidence**: v1.2.35 scanner had `runInterval` + per-cell `getBlock` + 4 redundancy triggers. v1.2.36 rewrite used `runJob` + `getBlocks(BlockVolume)` + flag map but lost ALL redundancy paths. Scanner silently failed for 5 versions until v1.2.41 full revert.
**Rule**: When rewriting a working subsystem, preserve EVERY redundancy path even if you can't immediately justify it. Default to "this exists for a reason I haven't discovered yet."

### Lesson L2 — Verify the rendering is a defect before fixing it
**Family**: Visual debugging
**Pattern**: User-reported "X looks weird" can mean "X is broken" OR "X is rendering exactly as the geometry/texture math specifies, and that's the look the user doesn't like." These have different fixes.
**Evidence**: User said v1.2.45 leaves looked "stretched." I diagnosed as `texture_height=16` bug, proposed and shipped `texture_height=128` fix in v47. User reported v47 leaves "look bad — just the texture." The v45 render was working as designed; my v47 change broke it. Cost two release cycles.
**Rule**: When user reports visual oddity on a non-obvious geometry/texture, FIRST calculate what the render SHOULD produce given the current setup, THEN compare to actual screenshot. If the render matches the math, the user is reporting an aesthetic preference not a defect — and the fix is aesthetic adjustment, not parameter change.

### Lesson L3 — Search loosely before claiming a file doesn't exist
**Family**: File discovery
**Pattern**: Project naming conventions (like `pw_` prefix) mean grep for vanilla names will miss everything. Don't claim "X doesn't exist in the pack" after one strict grep.
**Evidence**: User said "we have custom sand." I had grepped for `sand.png` and `"sand"` as terrain_texture key — both empty. Declared no custom sand. User was right: 24 sand variants existed as `pw_sand_v1..v29`. Cost a turn of pushback.
**Rule**: For ANY "is X present in the pack" question, search by prefix (`pw_*`), by category (`*sand*`), by extension (`*.texture_set.json`), AND by terrain_texture variation arrays before declaring absence. Multiple search strategies, then conclusion.

### Lesson L4 — Normal map rotation requires vector math, not just pixel rotation
**Family**: PBR pipeline
**Pattern**: When transforming a normal map (rotation, flip, mirror), rotating the IMAGE pixels alone is insufficient. The encoded R/G channel values represent VECTOR DIRECTIONS that must also be transformed.
**Evidence**: v1.2.46 sand pipeline needed rotated normal maps. NormalGL convention: R=X axis (−1..+1 mapped 0..255), G=Y axis, B=Z axis (out of surface).
**Math**: 90° rotation: new_X = −Y, new_Y = X (re-encode 0..255). 180°: new_X = −X, new_Y = −Y. 270°: new_X = Y, new_Y = −X. Horizontal flip: new_X = −X, new_Y = Y (B unchanged).
**Rule**: Any normal map rotation must apply BOTH PIL pixel rotation AND the encoded-vector transform. Resampling must use NEAREST (not LANCZOS/BILINEAR) — linear interpolation would mix normal vectors at boundaries.

### Lesson L5 — Detail-preserving downsample for PBR sources
**Family**: PBR pipeline
**Pattern**: Naive PIL `Image.resize(size, LANCZOS)` blurs high-frequency surface detail. For sand/dirt/rock PBR sources, that destroys dune ridges, scratch detail, and roughness variation. Always pair LANCZOS with UnsharpMask.
**Evidence**: Original 1024×1024 ambientCG sand had visible dune ridges, debris specks, surface ripples. The prior build pipeline used plain LANCZOS for 1024→256 → bland flat color. v1.2.46 pipeline used `LANCZOS + UnsharpMask(radius=1.5, percent=130, threshold=2)` for 1024→512 — preserved 90%+ of source detail.
**Rule**: For any PBR color/normal/roughness downsample, default to `LANCZOS + UnsharpMask(1.5, 130, 2)`. Tune unsharp parameters to source content. Box filter is sharper but introduces aliasing on directional patterns.

### Lesson L6 — MERS subsurface via AO mapping (B2 method)
**Family**: PBR pipeline
**Pattern**: Subsurface scattering S value in MERS alpha channel can be physically derived from source AO map rather than set uniform.
**Evidence**: v1.2.46 used `S = 25 − (AO/255) × 15` clamped [10, 25]. Where AO is dark (deeper hollows between dunes), S→25 (max subsurface — loose sand in shadows scatters more). Where AO is bright (exposed crests), S→10 (packed sand crests scatter less). Physically accurate for wind-deposited materials.
**Rule**: Default MERS subsurface = uniform 12 for compatibility. For high-quality PBR rebuilds, derive from AO via B2 formula. Range [10, 25] is LabPBR convention; values outside this look wrong under Vibrant Visuals lighting.

### Lesson L7 — Multi-pack texture overrides require matching blocks.json overrides
**Family**: Bedrock resource pack architecture / terrain_texture.json + blocks.json interaction
**Pattern**: When a later-loading pack overrides an earlier pack's `terrain_texture.json` shortname, it MUST also provide the matching `blocks.json` override if the earlier pack relied on one. Otherwise the engine resolves the vanilla blocks.json binding against the new (incompatible) terrain_texture entry.
**Evidence**: RP-04 had `minecraft:snow_layer` → `snow_layer_single` in blocks.json + the matching shortname in terrain_texture.json. RP-10 (later in load order) added `snow_layer` as a variations array in terrain_texture.json but had only `format_version` in blocks.json. Engine resolved vanilla `minecraft:snow_layer` through RP-10's entry → variations array → warning.
**Rule**: When ANY pack defines a `terrain_texture.json` shortname that another (typically earlier) pack uses for the partial-block geometry override pattern, the later pack must ALSO override the corresponding `minecraft:*` block in its `blocks.json` to point at a single-texture shortname. Belt-and-braces: both packs override the block, both packs have the single shortname.
**Affected partial-block geometry types** (per FOUNDATION §5.5): snow_layer, snow, candle, sea_pickle, top_snow, vines (attached-state), and any block with non-uniform/partial geometry.

### Lesson L8 — Entity-specific vs generic animation identifiers in pack overrides
**Family**: Bedrock entity/animation system
**Pattern**: When a resource pack overrides an entity client JSON, the engine resolves `animations` dict short-names differently by identifier type. **Generic identifiers** shared across many entities (`animation.quadruped.walk`, `animation.common.look_at_target`) fall through to the vanilla resource pack and resolve fine. **Entity-specific identifiers** tied to one entity (`animation.pig.setup`, `animation.guardian.swim`, `animation.fish.flop`) do NOT fall through — the engine requires them in the same pack stack as the overriding entity definition, or it errors with `can't find animation X`.
**Evidence**: v49 fixed 10 `setup` errors with shims; v50 then surfaced `swim` errors for entities whose generic animations worked fine but whose entity-specific swim animations were missing. A full audit found 23 such identifiers.
**Rule**: When overriding any entity client JSON, audit ALL declared animation short-names. For each, classify: entity-specific (named after one mob) or generic (shared)? Entity-specific identifiers MUST be present in the pack (real definition or no-op shim). Don't rely on vanilla fallthrough for entity-specific animations. No-op shims (0.05s loop on a placeholder bone) are safe when vanilla's version is itself trivial (setup poses) — verify before shimming animations with real motion.

### Lesson L9 — Custom blocks cannot replicate vanilla's distance-based render LOD swap
**Family**: Custom block rendering
**Pattern**: Vanilla leaves render fancy (transparent) up close and opaque (solid) at distance via an internal engine LOD swap. Custom blocks have a fixed `render_method` per material per permutation that applies at ALL distances. `opaque` = far block (full distance, no alpha); anything else = near block (~70 block cutoff, with alpha). There is no API to swap dynamically. Mojang acknowledged this is roadmap-only (2024 Bedrock Wiki Q&A) — not available as of Bedrock 1.26.x.
**Evidence**: The entire v51-v52 leaf-rendering arc. Attempting `opaque` v0 for far rendering produced solid-cube close-up appearance; the working solution required a *separate simplified geometry* for v0 plus a scanner-driven swap between v0 (far) and v1-v6 (near) rather than any per-block dynamic render method.
**Rule**: For any "render differently near vs far" requirement on custom blocks, do NOT search for a dynamic render_method toggle — it doesn't exist. The viable pattern is: two block states/variants (one opaque-far-friendly, one alpha_test-near-detailed) plus a script-driven scanner that swaps them based on player distance. Accept that the swap has visible latency (scanner cadence) and a transition band.

### Lesson L10 — Texture "healing" by averaging is inferior to clean-source replacement
**Family**: Texture pipeline
**Pattern**: When textures have a localized corruption (e.g., opaque-black pixels where transparency belonged), two repair strategies exist: (a) programmatically patch corrupt pixels with a computed average color, or (b) replace the whole corrupt variant with a transformed copy of a known-clean variant. Strategy (a) leaves subtle artifacts (averaged regions look flat/muddy, edges between original and patched pixels are detectable) and was rejected by the user on sight. Strategy (b) produces clean results because every pixel comes from a known-good source; variation is reintroduced via orientation transforms + imperceptible hue shifts.
**Evidence**: v51 first build used averaging (rejected: "you didn't clean all the black"); v51 rebuild used clean-source replacement with per-tile orientation + Lab ±3 hue shift and was accepted.
**Rule**: For corrupted-texture repair, prefer clean-source replacement over pixel averaging. Identify which variants/sources are natively clean, classify per-asset, and rebuild corrupt variants by transforming clean ones. Reintroduce variety through geometry and barely-perceptible (±3 Lab) color drift rather than relying on the (corrupt) texture content. Averaging is a last resort only when no clean source exists.

## II.9 — Era operational notes preserved

- **Workspace discipline of the era** (v36-48 handoff §6.3): `_logs/phase_log.md` (verbatim user-message log + completion markers), `_logs/decision_journal.md` (choices + rationale), `v37work/v{N}packs/` working trees, `mcpacks_v{N}/`, `deliverables_v{N}/`, outputs staged per release. Decision-journal protocol continued from v1.2.31.
- **Build scripts of the era** (recreatable from the specs above; did not persist): `sand_phaseA/B/Bv2/Bv3/C.py` (v46), `v47_geo_gen.py` (v47), `leaf_variant_replacer.py` (v51 shipped method), `leaf_black_heal.py` (v51 REJECTED averaging method — do not reuse), `v52_v0_texture_gen.py` (v52), `leaf_grid_builder.py` / `leaf_darkness_scan.py` (QA).
- **Backlog as it stood at v1.2.52** (all feature work, no open bugs): AmbientSounds 6.3.5 port (122 dormant sound events); custom water shader investigation; subpack tier system; 256x source integration; Marketplace prep; localization; partial-block variations audit (candle, sea_pickle, vines, top_snow); revisit the v0/reverse-randomizer architecture if Mojang ever ships dynamic render_method (it exists only to work around Lesson L9).
- **Lessons-for-future distillation of the v49 cycle** (preserved): user hypotheses are starting points, not conclusions (caustics ≠ animation system); Microsoft documentation can be misleading or context-specific — prefer empirical evidence; the simplest fix that works is usually right; read FOUNDATION §5.5 before partial-block texture work; audit-by-prefix when investigating.

---

# PART III — THE SKY ARC: v1.2.52 → v1.3.9
*Sources: SKY-MCPACK-INVESTIGATION-v2-ADDENDUM.md, SKY-Phase1-Spike-Protocol.md, HANDOFF-v1_3_x-SKY-ROOTCAUSE-and-PHASE1-SCANNER.md (D-094→D-136, generated 2026-05-17), AbsolutRealism-FOG-LIGHTING-Stacking-Dossier.md (chronicle-relevant history only — the dossier itself remains the canonical living reference), HANDOFF-v1_3_6-through-v1_3_9-ALPHASKY-SCRIPTEDSKY.md (D-138→D-165).*

**Arc summary.** For the project's entire history to this point, **no custom sky had ever rendered** — and the reason turned out to be a single wrong folder name inherited from day one. This arc runs: third-party teardown (the native cubemap mechanism exists) → spike protocol (per-biome routing is real; texture binding undocumented) → the root-cause session (folder name found, witness-proven, v1.3.5 shipped; Phase-1 scanner rewrite; "the blue was never a regression") → the alpha-sky session (the user's own optical invention; scripted fog-stack sky; a four-bug witness-driven fix chain; v1.3.8 MAIN + v1.3.9 ATMOSPHERICS). The sky story continues past this arc — §III.6 indexes every later sky-thread entry.

## III.1 — Investigation prehistory (pre-v1.3.x)

**III.1.a — The v2 addendum teardown (supersedes INVESTIGATION-v1's route conclusion).** *INVESTIGATION-v1 itself is not among the surviving sources; it is known through the addendum's corrections and is recorded here as referenced-but-absent.* v1 had concluded "Bedrock has no native custom-sky hook" and recommended a scripted-dome route (Route A) requiring RP+BP. The teardown of the user's uploaded pack collection proved that wrong:

- **Better_Clouds_v2.mcpack** (Bedrock, min_engine 1.17): `textures/environment/overworld_cubemap/cubemap_0..5.png` + `clouds.png` as a **1×1 transparent pixel** (kills vanilla clouds so they don't fight the cubemap) — proof #1 of the native cubemap; the clouds-kill trick directly reusable.
- **RealSource_VibrantVisuals_PLUS_2_0.zip** (Bedrock, pbr capability): same reserved folder **+ `cubemaps/cubemap.json`** at format 1.21.130 with `minecraft:cubemap_settings` — time-keyframed `ambient_light_illuminance` (1.5→7.0 across the day), `sky_light_contribution`, `directional_light_contribution`, `affected_by_atmospheric_scattering/volumetric_scattering` — proof #2 + the modern schema template.
- Realism_Visuals v1.3, Vibrant_BSL_Lite, RealismCraft_2_3: procedural (`atmospherics/` + `client_biome`) references — the other half. RealismCraft also carried a real authored 8919-byte `clouds.png`.
- Dramatic_Skys_Demo + Hyper_Realistic_Sky v3.8 (JAVA, Celestial system): **design references only** — formula-blended multi-layer skies (`night_fade` ramps 12500-13500/22500-23500, per-object `alpha = "night_fade * (1-rainAlpha)"` = weather-reactive sky with zero scripting, `rotation.degrees_y = worldTime*(360/24000)*0.866`). Not Bedrock-loadable; 3rd-party IP — our sources stay the CC0 ambientCG HDRIs.
- Sildur's (GLSL), pmweather/simpleclouds (Java mods): algorithm references only. Smooth_Craft: irrelevant.

**Key mechanism facts established**: the native cubemap is RP-only (no BP, no scripts, activates by presence); time-of-day is handled natively via the keyframed illuminance; it composites WITH the VV atmosphere; the earlier "static clouds looked terrible / perceptible square" failure was diagnosed as a **face-projection bug** (naive slicing instead of gnomonic per-face projection with edge bleed), fully solvable in the converter. Recommended routes: **4-A** (single night-leaning cubemap + procedural day, RP-only, lowest risk), **4-B** (per-biome cubemap routing IF verifiable), **4-C** (scripted swap — discouraged: no clean script hook to cubemap faces). v1's "you need RP+BP" downgraded: RP-only is the path.

**III.1.b — The Phase-1 spike (Gate A-1).** Live Microsoft Learn verification reversed the addendum's one wrong caution (logged as decision **D-010, corrected**): **4-B per-biome routing IS real and RP-only** — `cubemaps/*.json` + `client_biome` → `minecraft:cubemap_identifier`, with documented spatial cross-blending at biome borders; the cubemap JSON schema controls **lighting only** (no texture path field); `cubemaps/cubemap.json` is the reserved global-default filename. The one honest unknown — how a *named* cubemap identifier finds its 6 face PNGs — was attacked empirically: a 17 MB spike pack (`AbsolutRealism-SKY-Spike-v0_1_0.mcpack`) shipped Forest (control, reserved `minecraft:cubemap` at the known-good folder), Desert (Milky Way, `absr:sky_milkyway`, faces at BOTH `textures/environment/sky_milkyway/` [Conv-A: folder = json filename stem] AND `textures/environment/overworld_cubemap_milkyway/` [Conv-B: legacy suffix]), and Ice Plains (aurora, `absr:sky_aurora`, Conv-A only) — a dual-convention layout designed so any in-game outcome is conclusive. Faces were proper gnomonic per-face projections of the ambientCG night HDRIs (001 clear, 002 Milky Way, 004 aurora); `clouds.png` 1×1 transparent; night-leaning lighting so the test reads at any hour. The outcome matrix (all-three / control-only / desert-only / nothing / square-visible) was pre-committed, with witness data driving the next phase.

## III.2 — The root-cause session (D-094→D-136) and v1.3.5

### THE SKY ROOT CAUSE

**For the entire history of this project, no custom sky ever rendered.** Cause, definitively confirmed by in-game witness:

> The reserved cubemap texture folder **must** be `textures/environment/overworld_cubemap/`.
> AbsolutRealism's original RP-02 used `textures/environment/overworld_cubemap_default/` — an extra `_default`.

Every build ever made faithfully preserved the wrong folder name. That single wrong path is why no custom sky — including AbsolutRealism's own intended sky — ever displayed, and it explains the user's long-standing "could never achieve the effects I wanted": the sky pipeline was never connected. **Proof:** SKYTEST3 packs E/F/G (garish magenta/cyan/yellow cubemaps at the correct path) all rendered on PS5 under Vibrant Visuals (**D-124, witness-positive**).

**Corollaries proven by E/F/G**: `textures_list.json` NOT required (F had none); `cubemaps/*.json` + `client_biome cubemap_identifier` NOT required for the texture (E/F/G had neither); the 1.21.130 data-driven cubemap system is **LIGHTING/EFFECTS ONLY** (schema has no texture field by design — texture binding is the separate legacy reserved-path mechanism); `capabilities: ["pbr"]` + `min_engine_version ≥ [1,21,120]` IS required (a non-VV-capable pack anywhere in the stack silently drops the whole world to the classic renderer).

**The investigation chain (preserved as method)**: D-109 docs-led client_biome binding applied to all 106 files → still no clouds (D-112). D-114 major reframe: the data-driven system is lighting-only; community VV cubemap packs refuted the "hard engine limit" fear. D-115/116 magenta empirical matrix; the user caught that the test packs had disabled VV → D-117 the VV-capability finding. D-118/120 VV-capable matrix all failed; the "VV Settings Pane cubemap control" ruled out (Editor-only). **D-121, the turning point — the user's witness question: "is the cubemap actually wired inside the pack? the magenta has nothing to attach to"** → forced re-examination of a day-one assumption. D-122/123 Bedrock Wiki authoritative structure → the folder name → SKYTEST3 isolation build. D-124 witness positive. **Methodological lesson: empirical isolation + witness beat documentation** — the critical facts were split across sources and contradicted by the pack's own inherited structure.

### PHASE-1 SCANNER REWRITE (crash source eliminated)

The forward+reverse scanner/randomizer (v1.2.52 form) was the primary lag/crash source — synchronous ~1.1M-cell loops tripping the 10s script watchdog in dense foliage. Replaced with **classify-once + distance-toggle**:
- **One-time permanent classifier**: a leaf with `pw:section_rolled=false` is classified exactly once (section + exposure via `detectSectionAndExposure`), flags written, never recomputed.
- **Distance toggle with hysteresis**: beyond 68 blocks → `pw:variant=0` (far opaque render); within 62 → the section/exposure-appropriate variant; 62–68 = no change (no boundary strobe).
- Both as yielding `system.runJob` generators with hard cell budgets — structurally cannot trip the watchdog.
- Heavy old paths (`_runLayeredScan` BFS, `_drainRandomizerQueue`, reverse re-revert churn) made unreachable (caller audit D-102).

**Witness-confirmed (D-108, sky session): "leaf switch working perfectly."** Phase 2 (planned, user-confirmed direction): per-species `.mcstructure` trees with `pw:zone`/section baked at design time, collapsing runtime to a trivial toggle.

### ATMOSPHERICS DIAGNOSIS — the blue was never a regression

Extreme blue saturation everywhere = AbsolutRealism's *real, aggressively-tuned daytime atmosphere rendering correctly for the first time* — previously dormant because the cross-pack reference chain (client_biome → atmospherics) never resolved under the old broken load order. Diagnosed top-down (lighting → atmosphere → fog): `rayleigh_strength` daytime keyframes were 1.5/1.4 (aggressive; ~1.0 is natural), amplified by color_grading saturation ×1.2–1.25 + contrast ×1.1, then ACES. **Adjustment (D-105, conservative, reversible; originals in journal)**: daytime rayleigh 1.5/1.4 → 1.0; `sky_zenith_color` desaturated `[77,180,254]→[120,175,232]` and `[69,174,254]→[115,172,230]`; dawn/dusk/night keyframes preserved exactly; color_grading untouched.

### The empirical orientation map (D-128/D-129 — LOCKED; replaces the wrong early assumption D-071)

From the SKYCAL calibration pack + the user's sun-anchored witness (sun rises EAST):

| cubemap file | Calib color | World direction |
|---|---|---|
| `cubemap_0` | RED | **NORTH** (−Z) |
| `cubemap_1` | GREEN | **EAST** (+X) |
| `cubemap_2` | BLUE | **SOUTH** (+Z) |
| `cubemap_3` | YELLOW | **WEST** (−X) |
| `cubemap_4` | MAGENTA | **UP / zenith** — texture-up points SOUTH |
| `cubemap_5` | CYAN | **DOWN / nadir** |

(User's pole reasoning: magenta certainly up; cyan never visible because it is below, through the world blocks.) The v1.3.5 night cubemap was built to this map: N/E/S/W faces carry the night sky with full horizontal bleed hiding the 4 horizon seams (milky way continuous — verified in `review_images/NIGHT_horizon_NESW.png`); zenith subtle/fading alpha; nadir fully transparent.

### v1.3.5 — 2026-05-17 (first v1.3.x ship)

*Numbering note: v1.3.0→v1.3.4 are not attested as ships in any surviving source — the session's test packs were v0.x (SKY-Spike v0_1_0, SKYTEST, SKYTEST3, SKYCAL). v1.3.5 is the first documented v1.3.x version.*

**Deliverables** (canonical zip-of-mcpacks structure; all packs `[1,3,5]`):

| Deliverable | Size | Contents |
|---|---|---|
| `AbsolutRealism-v1_3_5-MAIN.mcaddon` | 379 MB | 10 nested .mcpack: RP-01 Tectonic, RP-03 PBR, RP-05 Flora, RP-06 Hostile Mobs, RP-08 Items, RP-09 Trees, RP-10 Terrain, RP-11 Ores, BP-02 Tectonic (Phase-1), BP-05 Trees |
| `AbsolutRealism-v1_3_5-ATMOSPHERICS.mcaddon` | 113 MB | RP-02 Atmospheric Effects (unified night-sky), BP-01 Atmospheric Effects BP |
| `RP-04-AbsolutRealism-Basic-RP-v1_3_5.mcpack` | 197 MB | standalone (too large to bundle) |
| `RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_3_5.mcpack` | 205 MB | standalone |

**mcaddon = zip of .mcpack files, NOT extracted folders** — a build error the user caught at D-135, corrected D-136; the structure check became mandatory before any mcaddon ship (→ L-PKG-1). User-supplied BP Mob Spawn + BP Diagnostics verified not sky/leaf-critical (D-131). Transfer limit 500 MB: MAIN+ATMOSPHERICS = 491 MB, Basic+Neutral = 402 MB.

**Cross-pack verification (D-131 — 8 audits, all clean)**: UUID uniqueness (14 header + 16 module); dependency resolution; engine/capabilities consistency (all RP pbr + 1.21.120, BPs correctly none); **all 106 client_biome references resolve** (10 atmosphere, 51 fog, 10 lighting, 22 water, 10 color-grading, + `pw:overworld_cubemap`); BP-02↔BP-05 leaf state contract; script deps intact (BP-01 1.16.0, BP-02 2.0.0, BP-05 none); 35 block IDs zero collisions; faithful-superset (RP-02 differs only by intended changes; water/fogs/lighting/color_grading byte-identical). Two audit flags proven false positives (`pw:top_variant` is log-only and typeId-guarded; the "26 vs 9" leaf-id count legitimately includes 17 log tiers).

**Status**: SHIPPED → awaiting first real-sky witness. If sky still failed, the binding mechanism was witness-proven — suspect integration (conflicting pack, load order, spike pack not removed), not the mechanism.

## III.3 — The FOG-LIGHTING Stacking Dossier (chronicle entry; the dossier LIVES ON)

Produced during the root-cause session as its companion reference deliverable, the dossier established **the definitive model of how every VV visual layer composes**, cross-referenced against v1.2.52's real files (51 fogs / 10 atmospherics / 10 lighting / 10 color-grading / 106 client_biome). Chronicle-relevant results — the facts that shaped ships:

- **The pipeline order**: LIGHTING → ATMOSPHERE → DISTANCE FOG → VOLUMETRIC FOG → CUBEMAP composite → COLOR GRADING + ACES last, on the entire frame. The colour coupling (volumetric fog inherits distance-fog colour, which inherits atmosphere, which inherits lighting) is the deepest stacking dependency — hence the standing law: **diagnose fog/sky colour bugs top-down (lighting → atmosphere → fog), never fog-first**.
- **There are three independent fog systems** (stack-resolved biome fog; distance fog; VV volumetric fog) resolved **per-property, not per-file** — AbsolutRealism's 51 fogs are sparse overlays, not replacements. `remove_all_prior_fog` is a silent kill-switch; biome fog is a proximity-weighted average; `render` vs `fixed` distance idioms don't blend cleanly.
- **The D-085 regression fully explained**: `affected_by_volumetric_scattering: true` put the skybox inside the ~0.045-density medium across the whole sky-dome path length → integrates to near-opaque. The fog values were never wrong; the sky was put inside them. → `volumetric_scattering: false` LOCKED on the cubemap.
- **The D-056 double-grade mechanism confirmed**: color grading is unconditionally post-composite and global — converter output must stay near-neutral.
- Tone mapping (ACES), orbital offset, caustics, waves do NOT blend between biomes — divergence = hard seams; per-channel `absorption` is secretly monochrome (luminance-collapsed) — tint via `scattering`; volumetric fog does not render at Y≥320 (reference screenshots must be taken at gameplay altitude); `henyey_greenstein_g` is the actual god-ray control (which later became the H-24 recipe clarified in v1.3.25); the cubemap's three lighting-contribution knobs are the correct surface for time-of-day cloud response, not the volumetric flag.
- Its 8 actionable recommendations seeded later work: the tone-mapping audit (D-096, queued), the fog-idiom audit, the `remove_all_prior_fog` audit, the isolated `atmospheric_scattering: true` cloud-tint test (the D-088 v0.4.2 plan), god-rays as a separate workstream, and the top-down diagnosis law.

**Disposition (Abs0lum ruling, 2026-07-10):** the dossier **remains in project knowledge as the canonical living technical reference** for the stacking model. It is NOT retired by this synthesis and does NOT appear on the post-v4 delete list. Flagged for future absorption into ARCHITECTURE.

## III.4 — The alpha-sky session (D-138→D-165): v1.3.6 → v1.3.9

### THE ALPHA-SKY — the user's own invention

After the folder-name fix, the remaining problem: a Bedrock cubemap is one static texture set — the night starfield showed at noon. **The user proposed the mechanism: make the black of the night cubemap transparent.** Bright pixels (stars, milky-way band) stay opaque; dark sky becomes see-through; the engine's own atmosphere renders through the transparent regions. Day: bright blue atmosphere washes/hides the stars. Night: dark atmosphere reads as dark — stars on black. **One static cubemap that self-resolves day/night optically, no script.**

Confirmed sound on two independent grounds: (1) research (Minecraft Wiki *Sky*: transparent regions let the colour behind take over; VV composites cubemap with atmosphere via texture alpha); (2) **our own prior witness** — D-138/D-140 had already observed the day atmosphere bleeding through the near-transparent zenith face.

**Built (D-163/164, shipped v1.3.9)**: all 6 faces alpha-keyed by luminance. Source night-HDRI luma measured: dark sky ≈31–58 (mean 48); milky-way band & bright stars ≈72–246. Ramp from those percentiles: **LO=52** (transparent below), **HI=90** (opaque above), **GAMMA=0.9**, star-point preserve (luma >110 forced opaque). Result: ~70–90% of each side face transparent; nadir fully transparent. Honest status at ship: the day/night composite preview (`review_images/ALPHASKY_day_vs_night.png`) showed the mechanism working (night excellent; day blue-dominant) with residual faint day speckle of the brightest stars — the inherent single-static-cubemap tradeoff, ~80–90% solved optically, expected to need ~1 ramp iteration from real witness, with daytime fog as the complementary wash.

### THE SCRIPTED FOG-STACK SKY (research-confirmed mechanism)

For weather/time mood beyond alpha, the user declined guesswork ("don't want dead ends") and cited the RealismCraft / Hyper Realistic Moon marketplace family. Research established the actual technique: **nobody runtime-swaps the Bedrock cubemap** (even Hyper Realistic Sky's Bedrock port is static subpacks); the reliable scriptable lever is the **per-player fog stack** (`/fog push|remove`; command layer top-priority; fog colour drives perceived sky/atmosphere colour, especially at the horizon); there is **no typed script fog API** — command-runner only.

**Architecture (built into BP-01)**: a self-contained module appended to the 713-line ambient-sound script (original an exact prefix — zero risk to audio). `system.runInterval` 40t per player; state resolved by **dimension > weather > time-of-day** precedence (guaranteeing "not clear while raining"); on state change only, pop previous `ar_sky` fog, push new; state-cached; `playerLeave` cleanup. Resource side: 9 fog definitions (`ar_sky_day/night/dawn/dusk/rain/thunder/snow/nether/end`) tuned to the PATH D palette. **`/fog` is cheat-gated** — the alpha-key cubemap works regardless (pure texture), making it a useful diagnostic discriminator.

### THE WITNESS-DRIVEN FIX CHAIN (four real bugs)

1. **Square-oak-vine (D-145→D-151).** Witness: square TRUNK on vined non-elder oaks. Process lesson preserved: D-146's first diagnosis ("square leaves / vine-survivability") was a **misread of the witness report** — the user said *trunk*, not leaves; discarded at D-147 (→ L-WITNESS-2). Definitive cause (D-149): BP-05 has no feature_rules — pw oaks enter worldgen by overriding vanilla `minecraft:oak_tree_feature` with a weighted_random of pw features; under dense-canopy crowding the pw trunk fails to place → **vanilla square `minecraft:oak_log` fallback**, decorated by the wide vine scatter (12 iter, ±5 xz, y 3–18). Fix **A+C+D** (D-150/151, BP-05 `features/` only; `blocks/` byte-identical so the scanner contract held): A broadened `may_replace` (+oak_log, vine, leaves/leaves2, pw oak logs, ferns) and `may_grow_through` (+podzol/moss/dirt_with_roots); C reweighted toward robust `pw:oak_young` (55) with every weighted entry verified pw-dodecagon (no vanilla path); D tightened `pw_vine_overlay_scatter` (iters 6, xz ±1, y 2–9) + `may_attach_to` = pw oak trunks only → a fallback vanilla oak gets no vines, making the symptom structurally impossible. Caveat: worldgen fixes affect newly generated chunks only.
2. **"Weird bright balls" (D-152→D-153).** 19-screenshot witness batch: bright glowing orbs in/over the forest at night. Cause: `firefly_mer.png` emissive max 250 (~98%) blooming under VV HDR — **dormant since v1.2.37, surfaced only when D-124 made the VV pipeline actually work. The user's hypothesis ("firefly tweaking from ages ago") was exactly correct.** Canopy emission checked NEGATIVE (no `minecraft:light_emission` on any leaf block or permutation; leaf MER emissive 0). Fix (D-155): emissive 250→60; firefly bush left intentionally emissive.
3. **Valley-tree leaves (D-155).** Phase-1 scanned only upward (`PW_P1_Y_LO = 0`); downslope/valley canopies never reached. Fix: Y_LO 0→−40; per-yield budget 2000→2600 (volume ×1.93 but still yields — watchdog-safe); `dy*dy` verified negative-safe. Confirmed in the user's log (MARKER-D/E at a below-player coordinate).
4. **Fog-schema bug (D-162, a Claude error).** All 9 `ar_sky` fogs failed schema: authored `volumetric.density.air = {max_density_height: 320, zero_density_height: 0}` violates `zero_density_height >= max_density_height` → all 9 failed to load → the entire scripted sky was inert (and part of why daytime stars persisted). Fix (D-163): removed the `volumetric` block entirely (design relies on `distance.air`; the dossier warns AR volumetric drowns the sky).

**Near-miss caught before shipping (D-159→D-160)**: the first sky script used `player.runCommand(...)` — a v2-era API that does not exist at BP-01's locked `@minecraft/server` 1.16.0 (and `Dimension.runCommandAsync` was removed in 2.0.0). Rewritten to version-correct `runCommandAsync` with dimension fallback; the FOUNDATION dep lock respected, no bump.

### PATH D recalibration (D-144, in v1.3.6+; night witnessed genuinely good)

moon_mie night→0.3; moon.illuminance 0.85→0.4; moon.color→[163,182,255]; sky_horizon night→[20,40,75]; sky_zenith night→[5,8,18]; ambient→~0.02–0.03; color-grading saturation 1.2/1.25→1.05/1.08 (ACES kept); cubemap json sky/dir contributions 1.0→0.4 / ambient 4.0→1.5.

### Version chain and deliverables

*The v1.3.6→v1.3.9 chain was a functionally-correct patch series the session itself flagged for consolidation. Ship-state at era end:*

| File | Size | Role |
|---|---|---|
| `AbsolutRealism-v1_3_9-ATMOSPHERICS.mcaddon` | 113 MB | Alpha-keyed self-resolving cubemap + 9 schema-fixed fogs + fog-stack sky scheduler |
| `AbsolutRealism-v1_3_8-MAIN.mcaddon` | 379 MB | Scan-below (BP-02) + tamed fireflies (RP-10) + A+C+D vine fix (BP-05) + 7 reversioned |
| RP-04 / RP-07 v1_3_5 | 197/205 MB | unchanged |

Mixed-version drop-in delivery model established (independent manifests; only changed packs bump). **Version attribution within the chain**: v1.3.6 carried PATH D recalibration; v1.3.7 carried the vine fix (A+C+D); v1.3.8 MAIN aggregated scan-below + fireflies + vine fix; v1.3.9 ATMOSPHERICS carried the alpha-sky + fixed fogs + scheduler. Superseded by this chain: all v0.x spike/test packs, BP-02 hangfix/phase1 standalones, v1.3.5/6/7/8-ATMOSPHERICS and v1.3.7-MAIN.

**Verification performed (preserved)**: faithful-superset on every ATMOSPHERICS build (51 original biome fogs 0 changed; water/ 0 changed); BP-01 script = exact-prefix extension, `node -c` valid; BP-05 `blocks/` byte-identical (scanner contract); all 5 oak-override entries resolve pw; fog schema re-validated; zero v2-only calls; zip-of-mcpack verified; alpha ramp set from measured luma, not guesswork.

**Open at era end (into Part IV)**: the decisive v1.3.9 witness gate (fog errors gone; day wash quality; night quality; cheats gate; fresh-chunk vine check); alpha-ramp tuning iteration; **the projection seam / dark blocky quads (D-154)** — per-face equirect sampling discontinuous at face boundaries, needing a single consistent equirect→cubemap reprojection (the alpha-key does not fix it); weather/time crossfades (fog `mid_seconds`/`max_seconds`); the **day-cloud fallback plan (D-129)** — if day overhead clouds look bad, use only the 4 horizon faces (N/E/S/W) for clouds with zenith transparent, building the panoramic distant-cloud look first (night > day priority, user-directed contingency); the full 213-sky converter (classification LOCKED in `_logs/classification_tags.md`); Phase-2 structure-template tree pipeline; "perhaps we invent one ourselves" — the alpha-key endorsed as the seed of the bespoke sky system.

## III.5 — Sky-era lessons (full text, carried verbatim; this document is now their carrier of record)

- **L-SKY-1 (the big one):** The reserved in-world cubemap texture folder is **`textures/environment/overworld_cubemap/`**. Never `overworld_cubemap_default`. A custom cubemap at the wrong folder name silently does nothing — no error, just vanilla sky. This was inherited from AbsolutRealism and undetected for the project's entire history.
- **L-SKY-2:** The 1.21.130 data-driven cubemap system (`cubemaps/*.json` + `client_biome cubemap_identifier`) controls **lighting/effects only**, not texture binding. Its schema has no texture field by design. Texture binding is the separate legacy reserved-path mechanism.
- **L-SKY-3:** A resource pack is Vibrant-Visuals-capable **only** with `capabilities: ["pbr"]` (or `raytraced`) AND `min_engine_version ≥ [1,21,120]`. A non-VV-capable pack anywhere in the stack forces the *entire world* to the classic renderer, silently disabling all VV features including custom cubemaps.
- **L-SKY-4:** `textures_list.json` is NOT required for a cubemap to render; the reserved path binds directly. (Harmless to include.)
- **L-SCAN-1:** The leaf scanner's correct architecture is classify-once (permanent per-leaf flags) + a cheap distance toggle, NOT continuous re-scan/re-roll. The re-classification churn — not the toggling — was the cost. A leaf's correct variant is a fixed property of its position; computing it repeatedly is the waste.
- **L-ATMO-1:** AbsolutRealism's atmosphere/rayleigh/color-grading were historically *never applying* due to broken cross-pack reference resolution under the old load order. Correct loading makes the real (aggressive) tuning render for the first time — diagnose "sudden" visual extremes as "dormant feature now active," not "new regression."
- **L-PKG-1:** A `.mcaddon` is a **zip of `.mcpack` files** (zip-of-zips), each nested mcpack having its manifest at its own archive root. Never a zip of extracted pack folders. Always verify top-level entries end in `.mcpack` before shipping any mcaddon.
- **L-METHOD-1 (reinforces the packed-ice precedent):** When documentation is insufficient/contradictory, the resolution path is garish single-variable empirical test packs + witness, not more doc-reading. The user's witness about *symptoms* ("nothing to attach to") repeatedly out-performed static analysis at locating the true cause.
- **L-SKY-5 — Alpha-key self-resolving cubemap:** a single static night cubemap can serve both day and night by alpha-keying per pixel by luminance (bright = opaque stars, dark = transparent). The engine's atmosphere renders through the transparent regions (day-blue washes stars; night-dark shows them). Confirmed by Minecraft Wiki *Sky* + our own D-138 zenith bleed-through. Inherent tradeoff: stars kept opaque for night show as faint day speckle; tune the luma ramp from real witness and use daytime fog to finish the wash.
- **L-SKY-6 — Fog volumetric schema rule:** in `minecraft:fog_settings.volumetric.density.air`, `zero_density_height` **must be ≥** `max_density_height`. If volumetric isn't needed, omit the block entirely (the valid AR biome-fog shape is `description` + `distance` only). An invalid fog file fails to load *silently from the gameplay side* — the only signal is the render log.
- **L-API-1 — @minecraft/server v1 vs v2 command running:** v1.x uses `runCommandAsync`; v2.0.0 removed `Dimension.runCommandAsync` and introduced sync `runCommand`. A script must match its **manifest-declared** module version. Never assume a command API exists; never blindly bump a locked dep — find the version-correct call.
- **L-FX-1 — Particle MER emissive blooms huge under VV:** a tiny particle with a near-max emissive MER channel becomes a large bright orb once the VV pipeline is active. Audit legacy emissive tweaks after any change that newly enables VV/atmospherics — dormant settings can surface dramatically.
- **L-WORLDGEN-1 — Vanilla-override tree features can fall back to the vanilla square block:** overriding `minecraft:oak_tree_feature` with a weighted_random/aggregate of custom features still leaves a vanilla fallback path under crowding. To eliminate it: make the custom features robust (broaden may_replace/grow_through), ensure every weighted entry is custom, and decouple decorations (vines) so a fallback is undecorated and therefore invisible as the symptom.
- **L-SCAN-2 — Scans must span below the player:** a player-relative scan that only goes upward misses valley/downslope content. Extend the lower Y bound and re-budget the per-yield cell count so the larger volume stays watchdog-safe; verify `dy*dy`-style math is negative-safe.
- **L-WITNESS-2 — Read witness reports literally:** the square-oak-vine misread (D-146 "leaves" vs the user's actual "trunk") cost a discarded diagnosis. When the user reports a symptom, do not substitute a more convenient interpretation; confirm the literal claim before root-causing.
- **L-PROCESS-1 — Research the mechanism, don't guess:** when the user can't articulate a known-working technique, research the authoritative mechanism (here: the fog-stack technique, confirmed via wiki/docs + the marketplace-pack family) rather than picking the theoretically cleanest option. This avoided shipping the wrong architecture.

## III.6 — Sky-thread continuation index

The sky story continues beyond this arc. In version order:
- **v1.3.10→v1.3.20 (record gap, Part IV.1):** projection math locked (D-181), zero camera roll (D-203), Milky Way layout B — overhead arch (D-205), cubemap.json time-keyed lighting values locked (D-219), the D-233–236 cloud iteration → AZIM-BLEND baseline + double-faded "enhanced-3" stamp, ending at the user-approved v1.3.21 sky baseline.
- **v1.3.22→v1.3.27 (Part IV.2):** the fog henyey_greenstein_g schema saga (H-24 recipe corrected); the sun disc fix — sun.png (v1.3.26) then the decisive `sun_vv.png` VV-variant supersession (v1.3.27, → L-VV-1).
- **v1.3.28 (Part IV.3):** cubemap_4 zenith seam replaced (→ L-VV-2); sunset zenith/horizon keyframes; golden-hour boost; Milky Way procedural particle starfield (→ L-PARTICLE-1).
- **v1.3.35 era (Part V.3):** the sun-skip mystery root-caused as TPS collapse (client celestial extrapolation snap-back), not a sky bug; SKYDIAG diagnostic BP.
- **2026-07-04 session (Part VI.2):** celestial back-skip + sky gray banding under investigation (suspect periodic TPS hitch).
- **2026-07-05/06 session (Part VI.4):** BP-01 v1.3.29 idempotent 15s fog re-assert (D-54 hardening + darkness discriminator); the darkness case CLOSED — convicted as an Android VV deferred-renderer stale-atmosphere partition (engine-side), scanner exonerated as direct cause; Mojang bug-report packet prepared.

---

# PART IV — CONSOLIDATION ERA: v1.3.10 → v1.3.33
*Sources: HANDOFF-v1_3_21-through-v1_3_27.md (D-237→D-251), HANDOFF-v1_3_28.md (D-252→D-260, 2026-05-24), plus reference reconstruction for the two gap spans.*

## IV.1 — RECORD GAP: v1.3.10 → v1.3.20 (reference reconstruction only)

**No handoff for this span exists in the source set.** The span corresponds to decision-journal entries ~D-166→D-236, which are not in project knowledge. What survives, via later documents' citations — every statement below carries its source:

- **D-181 — projection math locked** (cited as a locked invariant, v1_3_21-27 handoff §2). The equirect→cubemap projection math for the sky pipeline.
- **D-203 — zero camera roll locked** (same citation).
- **D-205 — AbsolutRealism Milky Way layout = B (overhead arch)** (same citation).
- **D-219 — cubemap.json time-keyed lighting locked**: `ambient_light_illuminance` ranging 1.5↔7.0, `sky_light_contribution: 1.0`, directional `0.2`, `affected_by_atmospheric_scattering: true`, `affected_by_volumetric_scattering: false` (same citation; the volumetric false reaffirms D-085).
- **D-233→D-236 — extensive cloud iteration at v1.3.20-21**, shipping the **AZIM-BLEND baseline + double-faded "enhanced-3" stamp** (v1_3_21-27 handoff §3 Issue B background). Preserved canonical sky artifacts on the era build machine: `equirect_v1_3_21.jpg`, `equirect_052B_azim_blend_v2.jpg`, `equirect_052B_core_killed.jpg`.
- **v1.3.21 — the user-approved sky/atmospherics baseline** that the next session audited against ("compare to v1.3.21 baseline which user previously approved").

**Also attested-by-reference only, exact content unrecorded:**
- **v1.2.53 / v1.2.54** — the v1_3_21-27 handoff §3 Issue C cites "v1.2.54's inline variant assignment in `_phase1ScanJob`", placing Phase-1-scanner-era work under v1.2.5x numbers between v1.2.52 and v1.3.5. No ship record survives for either number.

*These entries append in full when/if their handoffs are recovered. Nothing else about this span is asserted.*

## IV.2 — v1.3.21 → v1.3.27 — Fog/Sun/Scanner/Vines (D-237→D-251)

**Session shape**: began as a fog/lighting/atmospherics audit on the v1.3.21 baseline; became a five-ship ATMOSPHERICS chain (two of them wrong turns), one MAIN scanner rewrite, and the sun-disc fix.

| Version | Type | What changed | MD5 | Status |
|---|---|---|---|---|
| v1.3.22 | ATMOS | Audit edits (ambient.illuminance, sun_mie keyframes, rayleigh peak, fog henyey_greenstein_g **in the wrong location**, pale_garden density) | (superseded) | SUPERSEDED — broke fog schema |
| v1.3.23 | MAIN | Scanner rewrite — Process A trunk-association + Process B distance-toggle | `2ab885541d50ed2613fb62e8dff53473` (400.5 MB) | **CANONICAL** |
| v1.3.24 | ATMOS | Fog fix attempt — removed the structure that was actually correct | (superseded) | SUPERSEDED — made it worse |
| v1.3.25 | ATMOS | REAL fog fix (correct H-G structure restored per Microsoft Learn) | `a9656ea4eb6e4147dddf2b89d880b659` | Superseded |
| v1.3.26 | ATMOS | sun.png replaced (120px core, soft halo to 217px; D-250, user Option B) | `fcee7b08fe570f9789fa9ac96c692b36` | Superseded |
| v1.3.27 | ATMOS | **sun_vv.png ALSO replaced** — the VV-variant filename supersession | `8eb0309a951a38663bc61ef1da6b2fa7` (117.2 MB) | **CANONICAL** |

**The fog-schema saga (D-238→D-249, a three-strike #77 sequence preserved as method)**: D-238 added `henyey_greenstein_g` to `density.air` (wrong location; project-knowledge research D-239, shipped as v1.3.22's five audit edits D-240) → v1.3.22 fog binding errors. D-248 "fixed" by removing the nested `volumetric.henyey_greenstein_g` structure that *looked* malformed — **it was the schema-correct structure**; v1.3.24 made things worse. D-249 (CRITICAL FAILURE LOG): Microsoft Learn confirms the correct schema IS the nested-twice form `volumetric.henyey_greenstein_g.<medium>.henyey_greenstein_g`. v1.3.25 real fix: invalid `density.air.henyey_greenstein_g` removed; correct top-level structure restored across all 51 fogs — overworld air g=0.65 (H-24 recipe), water preserved 0.82, Nether/End originals preserved (H-03 exception). → **L-SCHEMA-1** born; **H-24 recipe clarified**: `volumetric.density.air.uniform: true` + `max_density: 0.04-0.05` + `volumetric.henyey_greenstein_g.air.henyey_greenstein_g: 0.5-0.7` (NOT in density.air!) + `render_distance_type: "render"`.

**v1.3.27 cumulative ATMOSPHERICS content (from the v1.3.21 baseline)**: ambient.illuminance restored to the 0.04–0.08 brand baseline; sun_mie keyframes cleaned (0 at midnight/midday, 0.75 at sunrise/sunset); rayleigh biome-variant shape (peak 1.5 horizon, 0.2–0.3 mid-day); the 51-fog H-G restoration; pale_garden max_density 0.15→0.05 (H-14 Android safety); sun.png + sun_vv.png at the small design — 1024×1024 canvas, 120px solid core, smoothstep falloff to 217px, colors sampled from the original (bright cream 250,239,218 → warm cream 238,222,193 → cool edge 94,85,69), user-selected Option B. **The sun fix mechanism (D-251)**: pack-load-order supersession at FILENAME level — `sun_vv.png` is the VV-specific variant that loads when VV is on; v1.3.26 modified only the non-VV file. → **L-VV-1**. Small-sun PNG MD5 `bd697292bb582c9f732cadbd2a7154b5`; three legacy backup PNGs noted as cruft (~600KB, don't load): `sun_v1_1_2_backup.png`, `sun_v1_1_3_backup.png`, `sun_vv_v1_1_2_backup.png`.

**v1.3.23 MAIN — the two-process scanner (D-241→D-247, verification 30/30 PASS; the arc: investigation D-241, code reading D-242, proposal D-243, event-hook research D-244, design revision D-245 — NO new block state needed, Path B chosen — final design confirmation D-246)**:
- **Process A — trunk-association job (NEW)**: every 30t; logs searched in 35-block XZ radius, ±70 Y; precomputed priority-near outward-shell traversal (Chebyshev then Euclidean); found log → walk to column top → adjacent leaf; if `pw:section_rolled=true` the tree is done (cheap skip); else `_treeCompletionBFS` floods the canopy. Caps: 3 trees/cycle, 600 leaves/tree.
- **Process B — distance-toggle (REFACTORED)**: same 62/68 hysteresis and classify-once permanence; now priority-near offset iteration (`PW_P1_OFFSETS_NEAR`) instead of a uniform grid.
- **Event hooks**: `playerJoin`, `playerDimensionChange`, broadened `playerSpawn` all kick Process A.
- New symbols: `PW_TA_LOG_TYPES`, `PW_TA_INTERVAL=30`, `PW_TA_RADIUS_XZ=35`, `PW_TA_Y_RANGE=70`, `PW_TA_CELLS_PER_YIELD=3000`, `PW_TA_MAX_TREES_PER_CYCLE=3`, `PW_TA_BFS_BUDGET_PER_TREE=600`, `PW_TA_OFFSETS`, `PW_P1_OFFSETS_NEAR`, `_taStats`, `_taJobActive`, `_findAdjacentLeaf`, `_findTreeTop`, `_walkTreeFromLog`, `_treeAssociationJob`, `_kickTreeAssociationNow`, `_buildOffsetList`.
- Pre-existing bugs caught during build: `PW_SCAN_RADIUS_XZ` TDZ (used literal 25); `PW_SCAN_VERT_DOWN/UP` referenced-never-defined (added as legacy constants 0/42); `PW_LOG_TYPES` duplicate declaration (renamed to `PW_TA_LOG_TYPES`).
- Markers: MARKER-F (Process A first cycle), MARKER-G (first tree walked) added; MARKER-D/E preserved. **User witness confirmed working**: `MARKER-G v1.3.23 Process A first tree walked: 284 leaves at (-37,95,36)` and `600 leaves at (3,78,1)`.
- Deferred: dormant `_runLayeredScan`/`_runScanBox`/`_drainRandomizerQueue` left in place (dead-code refs only). Cosmetic: the stats line's per-variant counters read 0 (only the dormant path updated them; MARKER-E proves variants assign).

**Locked invariants restated by this session** (preserved through all later stamping): D-128 orientation; D-181/D-203/D-205/D-219; D-085 volumetric_scattering false; zip-of-mcpack; the 3 `@minecraft/server` string deps (BP-01 "1.16.0", BP-02 "2.0.0", BP-03 "2.0.0"); **BP-01→RP-02 pinned dep uuid `41a528a6-4cbc-473b-960f-8bf7f88e30cd` locked at `[1,2,52]` — never bump with the rest**; H-03 Nether/End fog exceptions; H-14 density ≤0.05; H-53/H-54 manifest stamping laws.

**Open issues carried out of the session**: (A) vines + "floating artifacts" — the A+C+D robustness fix was **OAK-ONLY** (3 of 25 pw tree features); birch(5)/jungle(6)/spruce(5)/elder_with_branches(4) still narrow → same vanilla-fallback mechanism, different species (high confidence); **the floating-artifacts diagnosis (cross-block ±14 leaf protrusions) was DECLARED WRONG by the user** — preserved as a correction record: the geometry observation is true, the causal claim is not; mechanism unknown pending screenshots. (B) cloud coloring complaint, screenshots pending. (C) stats counter cosmetic. (D) sun backup-PNG cruft. **Session-end user asks preserved**: three screenshot sets (vines/artifacts, clouds, sun verification).

**Process-violation observation (Lesson #77 pattern, preserved)**: three ships in one session violated parse-OK ≠ runtime-OK (v1.3.22 invalid field; v1.3.24 removed correct structure; v1.3.26 modified the wrong file). The recorded rule: when the user reports the same symptom after a "fix," the correct response is RE-INVESTIGATION, not assuming something else broke.

**Also this session**: `AR-Tree-Structure-Building-Guide.txt` delivered — the user's Realm tree-building workflow (build with girlfriend + friends → save `.mcstructure` → upload → palette/connectivity analysis → wire into `structure_template_feature` worldgen). The guide became a canonical project document.

## IV.3 — v1.3.28 — 2026-05-24 (Polishing pass) (D-252→D-260)

**Type**: Single ship covering phases A+B+C+D1+D2+D4+D5+D6+D7+E; D3 skipped (schema-blocked). Predecessor stack: v1.3.23 MAIN + v1.3.27 ATMOSPHERICS.

| Issue | Phase | Resolution |
|---|---|---|
| Floating `pw:*_elder_branch` artifacts in air | A | Branches disabled — 5 elder_branch_scatter.json iterations 3→0 (D-252) |
| Square-trunk-with-vines (birch/jungle/spruce/elder) | B+E | A-fix extended to 14 tree features — may_replace/may_grow_through broadened, 9+ bonus replaceable blocks (D-253) |
| Tiny/bugged canopies | B+E | Same extension addresses the canopy-fern-blocker |
| Falling tree animation disappears / sound mismatch | D7 | Root cause: controller threshold `q.anim_time > 1.78` vs animation_length 3.85 — keyframes between 1.8s and 3.4s NEVER rendered. Threshold → 3.83; FALL_KEYS + collision-elapsed 1.8→3.83 (D-254) |
| Sunset zenith-horizon abrupt transition | D1 | 4 intermediate keyframes (zenith + horizon, sunset + sunrise mirror) (D-257) |
| Golden-hour cloud reflection + ground illumination | D2 | sun_mie 0.75→1.25 at sunset/sunrise; ambient.color deepened; warm hold extended; illuminance boosted (D-257) |
| Water "face clear after emerging" too slow | D5 | 51 fogs: transition max_seconds 30→7, mid_seconds 5→1.5 (D-255) |
| Water too murky all biomes | D6 | 22 water files particle_concentrations scaled; 15 fog max_density clamped; 38 fog_end 60→80 (D-256) |
| Cubemap diagonal seam | C | cubemap_4.png replaced with near-uniform pale-grey matching side-face top color (D-258) |
| Milky Way procedural starfield | D4 | New particle + texture + spawner in BP-02 (experimental) (D-259) |
| Star/moon rotation decouple | D3 | SKIPPED — schema doesn't expose star rotation |
| Mob corrections (Issue 4) | — | DEFERRED pending screenshots (trader llamas invisible, sea turtle UV face swap, sheep tail upside down, armadillo rendering vanilla) |

**Files touched**: BP-05 19 (5 branch scatters, 14 tree features, manifest); BP-02 2 (main.js FALL_KEYS/fallAngleAtTime/elapsed/milky-way spawner, manifest); RP-01 2 (falling_tree controller, manifest); RP-02 ~77 (atmospherics, lighting, cubemap_4, milky-way particle + texture, 22 water, 51+15+38 fog edits, manifest); other 13 packs manifest-only. All 16 manifests `[1, 3, 28]`; all locked invariants preserved (UUIDs, pw:, string deps, RP-02 pin `[1,2,52]`, format_versions, activation order). D-260: stamping + packaging + verification + READMEs.

**Lessons (candidates, full text):**
- **L-WORLDGEN-2 — Aggregate features have no conditional execution.** `minecraft:aggregate_feature` runs ALL listed features regardless of earlier success. To make decorations conditional on trunk placement: (a) make the trunk robust enough to always succeed (broaden may_replace) — D-150's oak path; (b) disable the decoration when unpaired — v1.3.28's elder branches (iterations=0); (c) `single_block_feature` with `enforce_survivability_rules=true` so decoration auto-skips — the vines' existing path.
- **L-ANIM-1 — Controller threshold vs animation_length silently truncates.** A transition `q.anim_time > N` with N < animation_length runs the animation N seconds then snaps. Looks like "animation disappears"/"doesn't follow the sound." Always check controller thresholds against the referenced animation_length. (Instance: 1.78 vs 3.85.)
- **L-VV-2 — Cubemap face content must align at edges.** Adjacent faces' edge pixels (color/brightness/cloud features) must match or the seam is visible. Side faces carry horizon content at ~50%; the UP face should fade to side-face top-edge color at its edges — radial symmetry is the simplest guarantee; resolution mismatch (512 top vs 1024 sides) is tolerated.
- **L-PARTICLE-1 — Particle-based static starfield is viable.** `particle_appearance_billboard` at fixed world positions, 60s lifetime, ~80/player respawned every 45s; world-anchored (slow trail while moving) — acceptable ambient decoration. Constants: `MILKY_PARTICLE_COUNT`, `MILKY_RESPAWN_TICKS`, `MILKY_HEIGHT_MIN/MAX`, `MILKY_BAND_WIDTH_DEG`, `MILKY_BAND_HORIZONTAL_RADIUS`; band fixed at world +X. PENDING user verification at ship.
- **Watch items recorded**: falling-tree 3.85s pacing may want tuning (was effectively 1.78s); milky-way density; `with_vines` aggregates share the unconditional-run pattern (safe only while `enforce_survivability_rules=true` holds on `pw_vine_block_feature`); OB2 secondary suspect if tiny canopies persist (variant scanner over-classifying deep_inner v3).

## IV.4 — RECORD GAP: v1.3.29 → v1.3.33 (fragments only)

**No handoff for this span exists in the source set.** Attested fragments, each with its citation:
- A **"v1.3.33-era" fix**: vanilla "tree with vines" feature IDs bypassing the pw routing was fixed in this span (cited in HANDOFF-v1_3_36-47 §KEY MECHANISMS: "Vanilla 'tree with vines' feature IDs bypass routing (fixed v1.3.33-era)").
- **RP-09 Trees RP v1.3.29** existed and became the canonical leaf/log geometry source later absorbed into RP-01 (cited in the 07-04 handoffs' upload manifest and merger records).
- The era ended at the state v1.3.34 picks up from (Part V).

*Entries append when the covering handoffs are recovered. Note: BP-01's July version v1.3.29 (Part VI.4) is a per-pack-era number, unrelated to this span.*

---

# PART V — MOB-CONVERSION ERA: v1.3.34 → v1.3.35
*Sources: HISTORY-v3.md (v1.3.34/v1.3.35 sections, preserved verbatim below in V.1), CURRENT-STATE-v1_3_35-patch8.md (gaps absorbed in V.2), HANDOFF-SunSkip-and-BP-02-v1_3_35-TPS-Fix.md (V.3 — entirely new to the chronicle; the doc's own filing instruction was "append to HISTORY-v3").*

## V.1 — v3's chronicle, preserved verbatim

## v1.3.34 — RP-07 Patrix neutral mobs initial conversion (May 2026)

### Scope
First conversion of Patrix Java mod neutral mobs to Bedrock Edition. RP-07 introduced as a standalone resource pack for the 33 neutral mobs: pig, cow, mooshroom, sheep, chicken (3 variants), rabbit, cat, ocelot, wolf, fox, panda, polar_bear, horse, donkey, mule, llama, trader_llama, camel, goat, dolphin, turtle, cod, salmon, tropical_fish (4 variants), pufferfish (3 sizes), axolotl, parrot, frog.

### Initial issues observed (pre-Patch 6)
- Mobs slide/glide while moving (no leg animation)
- Several mobs (dolphin, turtle) appear upside-down
- Various UV mapping issues across mobs
- Bone hierarchy variations causing animation mismatches
- Custom mob geos use NON-vanilla bone naming (cat/ocelot use `front_left_leg` etc.)

---

## v1.3.35 — Mob conversion iteration patches

### Patch 1-5 (prior session work)
- Initial geometry conversions from JEM source
- Format version conformance
- Initial UV mapping copies
- Render controller setup
- Discovery of bone hierarchy variations

### Patch 6 (this session) — Initial mob fixes

**MD5**: `25acd5a2384fc29e5db1759b65088a22`

Iteration focused on observable mob issues. Multiple fixes:
- Horse mane Z position adjustment (7→11)
- Donkey/mule unchanged from horse base
- Goat south UV restored
- Wolf head/mane shifted -1 Z
- Fox head top to Y=16
- Universal 0-axis cube inflate rule applied (0.01 standard, 0.05 for chicken legs)
- Frog limbs anatomical reposition (first attempt)
- Dolphin/turtle body_cubes sub-bone added with `rotation: [0, 0, 180]` and `mirror: true` — FAILED to produce visual flip

### Patch 7 (this session) — Major iteration with animations

**MD5**: `96c7bb41e3d3406468d47c905b0983d8` → `85bc98581474ab7f7d673bd27650325f` (with ocelot scale)

Items shipped:
- **Horse + Donkey embedding**: Head down 2Y (embeds into neck); neck down 2Y (embeds into body); mane re-parented from `neck` to `head2` (follows head as mohawk)
- **Chicken wings + legs**: Right wing X +1, left wing X -1 (fully outside body); `[0, 180, 0]` rotation on leg0 + leg1 (feet point forward)
- **Pig snout**: Z size 4 → 1.5 (shortened 2.5); `[-10, 0, 0]` rotation (tilt up)
- **Cow head**: Entire head hierarchy down 2 Y
- **Goat coat**: Down 1 Y
- **Wolf**: All head bones + mane forward 1 Z (away from body front)
- **Parrot**: 4 wing-decoration cubes re-parented from `body_main` to `left_wing`/`right_wing`
- **Sheep south UV**: `[56,32]/[8,-16]` → `[56,16]/[8,16]` — STILL upside down per witness
- **Frog diamond**: **Body bone got `rotation: [0, 45, 0]`** (the breakthrough!); all limbs repositioned to body-local coords mapping to correct world positions after rotation; limb rotations cleared
- **Dolphin + Turtle**: Removed body_cubes sub-bone; applied UV-based Y-flip (swap up↔down, V-flip sides) to ALL bones — STILL upside down per witness
- **Animation speeds**: 1.5× frequency + 1.25× amplitude on all primary `math.<sin/cos>(distance_moved * F) * A` patterns; 23 anim files updated

**Original Tier 1-4 animations authored**: 31 animation files (`ar_*.animation.json`) covering all 33 mobs with original procedural patterns (sine-wave leg cycles + idle breathing).

**Ocelot scale fix**: Added 1.4× geometric scaling to ocelot.geo.json to compensate for vanilla MC's smaller ocelot scale (Lesson #202 discovered).

### Patch 8 (this session) — Iteration on Patch 7 feedback

**MD5**: `430196e120755208f096a4c296e2fcbc`

Items shipped:
- **Dolphin + Turtle**: Per-cube `rotation: [0, 0, 180]` with `pivot: [centroid]` on every cube; UVs restored to pre-Patch-7 originals (via self-inverse application of flip_y_uvs)
- **Ocelot rear leg "thighs"**: New `thigh_left` and `thigh_right` bones parented to body; 3.5×5.6×5.6 cubes filling gap between body bottom and back leg top; UVs sampled from back_left_leg's existing texture
- **Horse 1.4× scale**: All coordinates multiplied by 1.4 (same approach as Patch 7 ocelot)
- **Fox head**: Dropped 0.5 more Y; bone's pivot moved to BASE of head cube (bottom-rear corner) so look-at rotations pivot at neck joint (Lesson #205)
- **Frog inspection mode**: Each limb moved 1 unit outward from body edge; all 6 faces of each limb cube remapped to 2×2 distinct-color region (green/light/dark/distinct)
- **Parrot wings**: Removed thin 3×9×1 extending cubes; kept only folded-wing decoration cubes (moved in Patch 7) in wing bones
- **Cow neck**: Calculated body cube top Y; lowered neck cube origin Y by the delta so its top matches body top
- **Cod fin**: Per-cube `[0, 0, 180]` rotation on any "_b" or "back" fin bones
- **Llama**: Added `inflate: 0.01` to body_cube (diagnostic + z-fight mitigation for south face clipping)
- **Pig**: `inflate: 0.01` on body_cube (UV gap mitigation); snout tilt -10° → -15° (more nostril visibility)
- **Sheep**: South UV `[56,16]/[8,16]` → `[64,32]/[-8,-16]` (180° UV rotation); up face remapped from blank region to `[48,16]/[-8,-8]`
- **Animation activation threshold**: All `* query.modified_move_speed` → `* math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)` (Lesson #203). Applied to 24 animation files and 25 entity files.

**Awaiting witness test as of session end.**

### Patch 8 expected outcomes (predictions from witness data)

- Dolphin + turtle should be right-side up if Lesson #204 (geometric not textural) is correct
- Animation threshold should make slow movement show full-amplitude legs
- Frog limbs should be visually identifiable by color, enabling directional language
- Ocelot rear legs connected via thigh fillers
- Horse scaled up appropriately
- Other items incrementally improved

---

## Lessons added during patches 1-8

See FOUNDATION-v3.md §200s for full detail. Summary:
- 196: Vanilla anims fail on custom bone names
- 197: Diagonal leg pairing
- 198: Body-rotation inverse math
- 199: Child rotations compound with parent
- 200: Per-cube `[0,0,180]` rotation for Y-flips
- 201: Re-parent decorative cubes to limb bones
- 202: Vanilla MC ocelot scale compensation
- 203: Animation activation threshold pattern
- 204: Geometric vs textural upside-down diagnosis
- 205: Bone pivots at joints, not centroids
- 206: Mob-anatomical-frame direction language

---

*End of v3 history. Current state captured in CURRENT-STATE-v1_3_35-patch8.md.*
> *[v4 editorial: the line above closed HISTORY-v3; its CURRENT-STATE pointer is historical. The v1.3.35 state documents are absorbed below; the live CURRENT-STATE is the newest HANDOFF-* document per custom instructions §2.5.]*

## V.2 — Absorbed from CURRENT-STATE-v1_3_35-patch8 (verification finding + gaps)

**Verification finding (per the synthesis charter):** v3's V.1 sections above already chronicle the Patch 6–8 ship content and their MD5s (Patch 6 `25acd5a2384fc29e5db1759b65088a22`; Patch 7 initial `96c7bb41e3d3406468d47c905b0983d8`, final w/ ocelot scale `85bc98581474ab7f7d673bd27650325f`; Patch 8 `430196e120755208f096a4c296e2fcbc`). The state doc's unique content absorbed here:

**Ship-state facts**: Patch 8 = `RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_3_35.mcpack`, 206 MB, shipped 2026-05-25, JSON validation 139 files / 0 errors. Patch application scripts of record: `patch6_apply.py`, `patch7_apply.py`, `patch8_apply.py` (era build machine, `_research/v1_3_35_jem_methodology/`).

**Deferred at Patch 8** (the open board the next era inherited):
- **C.1 Donkey head/neck** — Patch 7 embedding applied same as horse; witness still reported "head and neck and neck and body problems"; embedding alone insufficient, awaiting Patch 8 data before committing an approach.
- **C.2 Mule mane polish** — same setup as horse/donkey; no mule-specific witness yet.
- **C.3 Frog directional language** — Patch 8's color-coded inspection mode exists precisely to unlock precise directional witness instructions for the real fix.
- **C.4 Sheep UV iteration** — if the 180° rotation missed, the larger texture unfold in sheep.png's lower-right is the next candidate (possible full remap).
- **C.5 Llama south clipping** — inflate was a diagnostic; a real intersection fix may follow.
- **C.6 Methodology hand-off to FreshLX** — `JEM-TO-BEDROCK-CONVERSION-STANDARD.md` completed this session; hand-off awaits a witness-confirmed stable state and the user's timing decision.

**Documentation event of record**: this session produced the **v3 master document set** — OPERATING-MANUAL-v3, FOUNDATION-v3 (lessons #1–206), ARCHITECTURE-v3, HISTORY-v3, CURRENT-STATE-v1_3_35-patch8, JEM-TO-BEDROCK-CONVERSION-STANDARD.

*(The state doc's per-item predictions, expected-witness-feedback shapes, and failure-mode watchlists are recorded as deliberately dropped in COVERAGE-VERIFICATION.md — superseded by the witnessed outcomes chronicled in Part VI.)*

## V.3 — The Sun-Skip Investigation & BP-02 v1.3.35 TPS Fix (new to the chronicle)

**Symptom (witness)**: at a fixed position, the sky appeared to "jump" time of day — sharpened over the investigation to: **the sun physically skips backward to an earlier position and re-descends, repeatedly** ("sets ~3 times" in back-to-back screenshots), on mobile/PS5, with the world clock NOT observed going backward.

**Eliminations (preserved method)**: time-writing script — ELIMINATED (exhaustive grep of all BPs: no `setTimeOfDay`/`time set`/`time add`, no functions/, tick.json, .mcfunction; an external model's hidden-time-loop theory also wrong, retracted). BP-01's fog scheduler — NOT the sun cause (swaps `pw:ar_sky_dusk` #B5704F vs `pw:ar_sky_day` #7BB4E6 on a 40t poll; reads time, never writes; can flicker horizon tint only). `orbital_offset_degrees: 23.5` tilt — ELIMINATED (consistent across all 10 lighting files; orbital tables keyframe only illuminance + color; static tilt is deterministic). Note preserved: the tilt exists to center the cloud texture; a cloud-recenter + zero-tilt rework was queued then SHELVED once the real cause landed.

**ROOT CAUSE (confirmed): server-tick (TPS) collapse surfacing as client-side celestial snap-back.** Measured with SKYDIAG v3's effective-TPS meter: stable 20.0 TPS for the opening ~16s (sun smooth), then collapse to 2–9 TPS with multi-second freezes (4.95s, 6.25s) coinciding exactly with BIGCANOPY Process A walking 600-leaf trees + phase-1 classify of the initial forest. **Mechanism**: the Bedrock client extrapolates the sun forward in real time between sim ticks; when a tick takes seconds, the rendered sun overshoots then snaps backward on resync. Both witness statements were simultaneously true: sim time monotonic AND the rendered sun skipping backward. User confirmed the causal lock (smooth at 20 TPS; skipping began exactly at the collapse).

**Why runJob didn't save us**: the scan jobs are cooperative generators, but `_walkTreeFromLog` was a **synchronous** helper called inside the job — one dense tree could execute up to `PW_BFS_MAX_LEAVES` (3000) getBlock calls in a single uninterrupted chunk.

**Fix shipped — BP-02 Tectonic v1.3.35** (UUID `c3e09ed5-d121-40d1-9ea8-65b4701dbc67` preserved; drop-in; performance-only):

| Constant | Old | New | Why |
|---|---|---|---|
| `PW_TA_CELLS_PER_YIELD` | 3000 | 400 | trunk-assoc job yields ~7.5× more often |
| `PW_P1_CELLS_PER_YIELD` | 2600 | 400 | phase-1 classify yields more often |
| `PW_TA_BFS_BUDGET_PER_TREE` | 600 | 300 | fewer marks per tree per pass |
| `PW_BFS_MAX_LEAVES` | 3000 | 1500 | caps worst-case SYNCHRONOUS walk per tree |
| held-torch interval | 8t | 20t | minor; movement-gated already |

Added `[PW-PERF] v1.3.35 throttle ACTIVE` startup log. Single-job guards (`_taJobActive`/`_p1JobActive`) verified already present. **Verification at handoff**: v1.3.35 confirmed loading on the realm (`[PW-PERF]` present; `first tree walked: 300 leaves`, was 600); PS5 TPS re-measure and visual smooth-sun confirmation pending. Watch items recorded: `rnd=0`/variants-0 with marked/queue ~11k likely the marking-heavy startup phase (confirm rnd climbs, queue drains); startup-burst vs steady-state TPS; **if steady-state sag persists → convert `_walkTreeFromLog` to a generator** (the deeper fix, then earmarked "v1.3.36"). *(The July era's hybrid count+time yields and deadline-boxed walk — Part VI.3 — became that deeper fix.)*

**Diagnostic assets created (reuse, don't rebuild)**: **SKYDIAG BP-01**, versions **v1.3.36→37→38** (UUID `2e7000fd-1751-455b-b061-54a79490d024` preserved) — logging-only drop-in BP-01: `[AR-SKY-DIAG]` per-poll resolved sky state (tod/state/weather/fog); `[AR-TOD]` 0.5s clock sampler + backward-jump detector + effective-TPS meter (`dt=…ms tps=…`, flags `<<< LOW TPS` below 15). Final file: `BP-01-…-v1_3_38-SKYDIAG-tps.mcpack`. *(These numbers are diagnostic-line only — see Part 0.1.)*

**Lessons (unnumbered at source, carried verbatim; FOUNDATION absorption pending)**:
- A monotonic sim clock and a backward-skipping rendered sun are NOT contradictory. The client extrapolates celestial position in real time and snaps back on sim stalls. Visual "time-of-day jumps" can be a **performance/TPS symptom**, not a clock/lighting bug.
- `runJob` is cooperative, but a synchronous helper called inside the generator can still block a tick up to its own internal cap regardless of `CELLS_PER_YIELD`. Cap or yield-ify synchronous inner loops.
- **Measure effective TPS first** (Date.now() delta between fixed-interval samples) before touching lighting/atmosphere JSON when diagnosing sun/time anomalies.

---

# PART VI — THE PER-PACK ERA: 2026-07-03 → 2026-07-07
*Sources: HANDOFF-v1_3_36-through-v1_3_47.md (status 2026-07-04), HANDOFF-SESSION-2026-07-04-v1_3_48-through-v1_3_54.md, HANDOFF-SESSION-2026-07-05-06-CROWN-ROOFS-MEDIEVALISM.md, HANDOFF-SESSION-2026-07-06-07-ROOFS-PLANKS-PROVENANCE-MIGRATION.md (history absorbed; the document itself remains the live CURRENT-STATE).*

## VI.1 — The versioning-model change

From these sessions onward, packs version independently: a session ships a **per-pack version ledger**, not one suite number. The **Abs0lutMedievalism (`am:`) private pack suite** is born here with its own v0.x line. Session iteration stamps (e.g., "04g", "06i", "2026-07-07h") identify builds within a day. The **description-stamp law** (adopted 07-04) makes every shipped manifest description carry `vX.Y.Z · iter <date><letter> · headline` — cache-proof identification, born from a live regression caused by a world pinned to a stale RP-97 v0.1.0.

## VI.2 — Session 2026-07-03/04 — Medievalism study begins, felling overhaul, AM pack birth, armor pilot

**Version ledger (all suite-gated; witness status as marked):**

| Pack | Version | Contents |
|---|---|---|
| RP-01 Tectonic | **v1.3.47** | Falling-tree overhaul: trunk parity from BLOCK DEFINITIONS (spruce/jungle young/mature/old = pw_oak dodecagons; ALL elders + dark_oak + pale_oak = pw_simple_log full cube; birch = birch geos; rest FULLBLOCK16); canopy_4..canopy_16 deterministic bones (base = h*16−1, vines folded), height via part_visibility; ALL q.property math purged from position channels; gravity drop (constant −16px over 0.3s); w2 2×2 geometries; pw-leaf canopies via dual render controllers; 48-slot tier-aware trunk texture array; wind-resistance fall 5.90s; tex space 16 |
| BP-02 Tectonic | **v1.3.38** | Two-cue audio (creak@cut + `pw.tree_impact.<tier>`@tick106); REST 70t; [FELL] ID message (species/tier/WxW/h/logs); other-tree BFS boundary (`_rootedCache`, hDist>3); disconnection felling (creative kept); 2×2 cross-section rule (fall toward missing-3); slope-primary yaw (R=10, slopeMode ≥1 relief) |
| BP-05 Trees | v1.3.42 | dripleaf fix complete (big_dripleaf + small_dripleaf_block) |
| RP-03 PBR | v1.3.39 | stone placeholder purge |
| RP-04 Basic | v1.3.41 | stone fix + chest doubles (witness GOOD) + `_s` strip (−181 files) |
| RP-06 / RP-08 | v1.3.41 | `_s` strips |
| RP-07 Neutral Mobs | v1.3.41 | `_s`+`_n` strip (216→75 MB; mobs need no MERS per Abs0lum) |
| Abs0lutMedievalism RP+BP | **v0.3.0** | **PACK BIRTH** — PRIVATE pack, namespace `am:`; terracotta_tiles pilot (MERS pipeline PASSED witness) + 16 colored tiles (recipes keyed `minecraft:<color>_terracotta`; plain recipe needs UNCOLORED terracotta) + 68 variations-wired keys + `am:variant_test` |
| RP-97 Armor Pilot | v0.1.0 | diamond helmet attachable overriding `minecraft:diamond_helmet` (vanilla contract mirrored); `geometry.ar.diamond_helmet` (7 plates); palette texture from RP-08 art |

**Mechanisms/lessons established (candidates for FOUNDATION, carried verbatim):**
- **L-ENTITY-2 (candidate)**: q.property arithmetic FAILS in animation POSITION channels (reads 0); constants and part_visibility molang WORK. Never put property math in position channels.
- **L-ENTITY-1 (candidate)**: part_visibility `"*"` hides PARENT bones → whole subtree; explicit bone lists required for show-only-X controllers.
- **L-VAR-1 (candidate)**: terrain_texture variations do NOT traverse material_instances (first-texture-only); custom-block variety needs permutations/scripting.
- Sand glint = sparse low-R specks (0.5–1%, R 40–70) on a HIGH-R base (~215), not a lower mean R (Patrix red_sand: mean 217/std 36/0.66% sparkle vs ours 148/9/0%).
- `textures_list.json` = inventory manifest; regenerate on any texture removal (**L-TOOL-3**).
- ZipInfo reuse across archives corrupts zips — `writestr(name, data)` only.
- Verification expectations from SOURCE data, parsed comparisons only (two check-side false alarms this session).
- Vanilla "tree with vines" feature IDs bypass routing (fixed v1.3.33-era); jungle 2-tall + tiny canopy likely vanilla jungle bush (await repeat witness).

**Open investigations at session end**: falling-entity fullbright/unshaded (trunk 'entity' opaque material experiment shipped in the v1.3.45 chain, carried into 47 — witness pending; candidate 2 = VV entity texture_sets; relevant to future door animations); celestial back-skip + sky gray banding (frame-16 numerics: bands top 10%, gray 70↔34; BP-01 sets NO time; suspect periodic TPS hitch, verify-pass 200t candidate); fall-start latency (likely wind-curve design or device lag); canopy linger after fell + STRICT per-tree leaf boundaries via Process A association data (approved direction, not yet built); creak/crash tuning after AV session.

**Backlog approved/queued this session**: P3 zero-MERS authoring batch (144 files per GPU-AUDIT-PHASE1-REPORT), firefly_bush_emissive fix, 64px floors (166), `_mer`→4ch MERS migration at half-res; P4 256 color re-derivation from Patrix sources (hero-first, ~1.8GB reclaimed budget); P5 sand glint pilots (48 files); armor chain (helmet verdict → geometry tune → photoreal texture → chestplate → legs/boots → material batch → VV texture_set on attachables); craft-again planks family (AM); circular architecture program (design doc first); log-top end-grain textures; BP-02 startup MARKER strings printing old versions (PW-VERSION line truthful); leaf artifacts + inter-block gap puffs (RP-09 geometry); Lesson #135 supersession + HISTORY-v4 + redwoods PAUSED per Abs0lum.

**Witness questions carried forward**: v1.3.47 canopies attached at trunk top all heights/species, dodecagon/square parity, dims vs [FELL] readout; RP-97 helmet crest/nasal/cheek shapes (override proof); bark textures on falling trunks; sound/AV session deferred until image viewing works.

## VI.3 — Session 2026-07-04, iterations a→j — Felling defect wave, pack mergers, entity PBR, helmet program

**Version ledger:**

| Pack | Version | Stamp | Status |
|---|---|---|---|
| RP-01 Tectonic | **v1.3.54** | 04g | Shipped, presumed live; **ABSORBS RP-09 Trees RP v1.3.29** |
| BP-02 Tectonic | **v1.3.46** | 04j | **CONFIRMED LIVE** via PW-VERSION in the user's log; **ABSORBS BP-05 Trees BP v1.3.42** |
| RP-08 Items | **v1.3.43** | 04i | **WITNESS-CONFIRMED** ("helmet looks great") |
| RP-97 Armor Pilot | v0.2.2 | — | **RETIRED** (job done; helmet lives in RP-08) |
| BP-05 / RP-09 | — | — | **RETIRED** — fully absorbed. BP-05's hard manifest dependency on RP-09's UUID (80ab076f…) discovered and REWIRED to RP-01 ba3c58e5… @[1,3,52] before deletion |

**Standing laws adopted (all journaled):** description-stamp law (§VI.1); batch-testing cadence (accumulate multi-fix batches between test sessions); suite-gated packaging (zips built ONLY after the verification suite passes, same script — the gate caught two real defects); upload hygiene (uploads rotate out on the user's side — request specific packs only when needed, extract SAME TURN; BP-05 was lost once, frames twice).

**The felling-system defect wave — 12 mechanisms (fix version in parentheses):**
1. **Boxy trunks** (all 4 dodecagon species × 3 tiers) — the v1.3.47 flattening dropped the 24 bone rotations ([0,N×30,0] about [0,0,0]) per log segment. Fixed v1.3.48: rotations baked per-cube (rotation+pivot); radii re-standardized to RP-09 block sources (−0.25/−0.5 z drift unintentional). → **L-GEO-FLATTEN**. No complaint across later fells — treat as good, confirm opportunistically.
2. **Dead setup animation** (empty bones{} content-log error) — removed v1.3.48; error line gone ✓.
3. **Launch spin** — client yaw-lerp from spawn default to setRotation. Fixed v1.3.39(BP): yaw pre-spawn via `SpawnEntityOptions.initialRotation`, idempotent re-assert; playAnimation double-drive removed (controller-only). No spin since ✓.
4. **Phantom late impact** — the fixed 106t cue never cancelled on collision-freeze → second impact. Fixed v1.3.40: handle captured, `clearRun` on pin.
5. **Impact alignment** — samples normalized to peak @ +0.5s; cue 92t→82t (thud at exactly 4.60s). Logged correction: the "3s leading silence" first analysis was a silencedetect misread; the real defect was 0.2–0.8s peak jitter.
6. **Heavy-impact curve** — (t/5.35)^2.8 → ^2.5 (v1.3.48/39), then full retime v1.3.49/40: 38%@3.6s, 58%@4.0s, 78%@4.3s, IMPACT 4.60s, length 5.05s; controller threshold 5.03; FALL_DURATION_TICKS 101; all consumers suite-asserted. Creak: 0.6s lead + swell-to-2.2s on all 8 samples — **witness: "much much better" ✓**.
7. **First-contact terminal angle** (v1.3.40) — terrain profile along the fall line d=2..trunkLen, terminal = min contact angle; groundYAt exported from pickFallYaw. **WITNESS-CONFIRMED: no ground clipping ✓.** Caveat: slope sampling direction inherits the Phase-6 sign verdict.
8. **Watchdog crashes — two mechanisms, both confirmed fixed**: (a) leaf-cleanup 40k-getBlock AABB + multi-BFS → `function* cleanOrphanLeavesJob` runJob, yields ×3 (v1.3.40; canopy-linger side effect APPROVED); (b) PS5-join chunk-storm multiplying per-getBlock latency 10–100× under call-count budgets → **hybrid count+time yields (PW_SLICE_MS=8)** in both scan jobs + 40ms deadline-boxed `_walkTreeFromLog→_treeCompletionBFS` (v1.3.41). **WITNESS: PS5 joined clean ✓.** → **L-PERF-2 (time-based budgets) CONFIRMED.** *(This is the deeper fix the v1.3.35 TPS handoff earmarked — Part V.3.)*
9. **Trunk cap 16→32** (v1.3.49/40): property [1,32], script cap, log_17..32 + canopy_17..32 (+896 bones) across all 28 geos, both RCs extended, canopy_16 rule `>=16`→`==16`.
10. **Taller-than-real trunks** — measureColumnHeight maxY−minY counted branch logs re-crossing the trunk column (oak arcs; birch none — the species asymmetry); cap-32 exposed it. Fixed v1.3.42(BP): contiguous ascent from stump (`while (ys.has(minY+h)) h++`).
11. **Oak vanish + one-frame upright flash** — visible_bounds 8-wide cull box; fixed v1.3.51: 76×44 @ [0,18,0] all geos. **PARTIAL**: vanish gone; a residual **upright-SNAP persists** — mechanism ESTABLISHED in the final turn, fix designed, NOT BUILT (below).
12. **2×2 / direction inversion (Phase 6, OPEN)** — witness: 2×2 fell dead-opposite; elders ~quarter-turn off. Script convention `dir=(−cos y, sin y)` is a REFLECTION of MC body-forward `(−sin y, cos y)`; the mirror predicts axis-dependent error (matches both witnesses; a global 180 cannot make 90° errors). Fix = one sign in the shared yaw mapping; TWO candidate signs; **decided by one datum: any [FELL] line's `dir yaw=` + actual lie direction**. v1.3.46's enriched [FELL] made this self-serving.

**The designed-but-unbuilt upright-snap fix (preserved spec, the era's ready work item):** the collision-freeze rewrites `ft:fall_angle` mid-fall; the rest animation reads fall_angle (keys: 0.0 `q.property('ft:fall_angle')`, 0.15 −4.0, 0.30 +1.0, 0.45 −0.5, 0.60 exact); between the client receiving the rewritten angle and the fall_stopped transition, the FALLING state renders newAngle × curveMult(t) — e.g. pinned at −47° with mult 0.5 → −23° → visible snap toward upright, then correct rest. FIX: add property `ft:rest_angle` (int, [−135,−60], default −90, client_sync); BP sets rest_angle at spawn (=fallAngle) AND at pin (=freezeAngle) and STOPS rewriting fall_angle at pin; RP rest-animation expressions switch fall_angle→rest_angle keeping settle offsets. Planned ship: BP-02 v1.3.47 + RP-01 v1.3.55, suite-gated. *(Still on the open board at 2026-07-07 per the live CURRENT-STATE §9.)*

**Canopy rings (v1.3.54/44→46)**: design approved after correction — TRUE current envelope is 3×3 (docs had carried 7×7). `ft:canopy_size` 0–3 (3×3/7×7/11×11/15×15); 694 ring bones / 10,561 cubes; tier policy young r1@4–8, mature r1–2@5–12, old r1–2@8–16, elder r1–3@12–32; rings clone full-tile leaf UV; both RCs wired (`==N && canopy_size>=r`). BP measures via 8-ray bounded scan (≤280 getBlocks, 15ms guard) — v1.3.45/46 HARDENED to full-radius scan (early-break misread branch-structured canopies as maxR=0) with rays-bitmask diagnostics. **Witness verdict PENDING** (the "small canopies" report predates confirmed-live v1.3.46 + presumed RP v1.3.54).

**Bark shade (OPEN at session end; mechanism partially established)**: the live texture path is the 48-slot `trunk_<species>_<tier>` array — the earlier side-by-side was built on LEGACY UNUSED atlases (→ **L-TEX-1**: trace the live reference chain first; both early bark verdicts void). Live per-tier textures AT PIXEL PARITY with block sources (Δ≤+1.5 luma; oak_elder +7.4 fixed). Entity texture_sets shipped for ALL 12 species (44 sets: 5 sourced in-pack, 6 from RP-03, oak AUTHORED v1.3.54 — contract from sibling woods: MER RGBA metal 0 / emissive 0 / roughness ~210±35 crevice-modulated / subsurface 12, normals from color-height). **Witness after all that: STILL lighter (birch/oak/cherry).** Final-turn evidence: entity materials map is `{"default":"entity_alphatest","trunk":"entity"}` — the legacy opaque `entity` material is the prime candidate gating VV/PBR response. The user's directive granted latitude: fix the chain OR per-species LAB shade compensation as sanctioned fallback. pw_oak LEAVES MERS deliberately excluded (foliage subsurface differs — backlog LEAVES-MERS).

**Armor/equipment program (directive: "start doing ALL of the equipment now")**: Helmet v2.1 in RP-08 v1.3.43 **WITNESS-CONFIRMED GREAT** — short nasal (mouth open), temple cheek flaps (side plate + front plate ±14° about temple hinge, inboard |x|≥2.9 keeping eyes visible; smaller than the Vendel reference), dome/brow/neck/strap; material-distinct texture from TRUE Patrix palette (diamond teal 104,201,210 / bright 121,223,226 / dim 84,197,215; steel 132,129,126; trim 19,24,24; leather + white stitches); geometry single-sourced with the approval render. **Lessons CONFIRMED**: **L-ATTACH-1** — vanilla armor needs DUAL attachables: `minecraft:diamond_helmet` (mobs) + `minecraft:diamond_helmet.player` (item filter `query.owner_identifier == 'minecraft:player'`, offset anim `animation.armor.helmet.offset`) — the entire "worn looks vanilla" mystery, and the user's own "referenced differently once equipped" hypothesis; **L-ATTACH-2** — attachable cube coords are ABSOLUTE humanoid-model space: head 24–32, body 12–24, legs 0–12 (v2.1 first shipped ON HIS FEET at y0.35–9.2; +24 fix witnessed ✓). Suite-enforced. Next chain: photoreal helmet texture + texture_set → chestplate (Patrix white/brown fabric + stitching) → leggings/boots → held/placed/equipped audit.

**Diagnostics / witness-channel law (→ L-DIAG-1 candidate)**: `log()` = console.log behind DEBUG=false → **invisible in the content-log GUI (warn-only)** — every fell diagnostic, including the direction datum requested three times, was unobtainable by construction. v1.3.46 fix: enriched chat + warn mirror: `[FELL] <species> <tier> trunk WxW h=H logs=L | dir yaw=Y angle=A | canopy=S (maxR=R rays=BBBBBBB)` / `[PW-FELL] …`. Retro-sweep queued: audit BP-01/BP-03 + remaining BP-02 log()-only diagnostics.

**Image-viewing anomaly (the reason the next chat existed)**: frame batches 1–3 rendered fine and drove multiple mechanisms; batches 4 and 5 did NOT render on Claude's side (stated honestly both times). Batch 5 (6 frames) was believed to contain the helmet confirmations, bark comparisons, the upright-SNAP frame, and possibly the Phase-6 direction datum.

**Session lesson register**: CONFIRMED L-ATTACH-1, L-ATTACH-2, L-PERF-2. CANDIDATES L-GEO-FLATTEN (bake bone transforms when flattening), L-TEX-1 (trace live texture chain), L-DIAG-1 (witness-visible channels). Plus the four standing laws.

## VI.4 — Session 2026-07-05 → 07-06 (iters 05a→06i) — "Crown, Roofs, Medievalism"

**Version ledger (all suite-gated):**

| Pack | Version | What changed |
|---|---|---|
| BP-01 Atmospheric | **v1.3.29** | Sky scheduler v1.3.9 hardened: idempotent 15s fog re-assert per player (D-54 hardening [this session's journal] + darkness discriminator); heartbeat log every ~40 reasserts |
| BP-02 Tectonic | **v1.3.54** | Falling-tree PHASE A (`ft:leaf_variant` property + fell-time `pw:variant` state sampling), PHASE B (own-canopy-first cleanup, LEAF_DECAY_RANGE 6→8, canopy tier +1), PHASE C (stump-top spawn +1 on BOTH spawn paths, contact-angle pivot dY=gy−(stumpY+1)); `pw:golden_crown` item (first BP-02 custom item; wearable head, protection 100); crown AURA script (Resistance IV no-particles while worn, flame particle 8t above crown, dynamic light_block 14 following wearer, air-only placement + typeId-guarded cleanup; toggles PW_CROWN_RESIST/FLAME/LIGHT) |
| RP-01 Tectonic | **v1.3.56** | PHASE A: 84-entry species×variant RC canopy texture array (`wood_type*7+leaf_variant`), sheets BYTE-COPIED from world block textures, canopy color multiplier neutralized to 1.0 (trunk multiplier untouched). *Hard anchor (Abs0lum, pack git archive): single ship, 2026-07-05.* |
| RP-03 PBR | **v1.3.40** | CLASSIC DOOR FIX: six classic doors × upper/lower block art + `_mer`/`_n` + rewritten texture_sets at vanilla LEGACY paths (`door_wood_*`, `door_spruce_*`, …) |
| RP-08 Items | **v1.3.69** | Golden-equipment arc: gold sprite fix (legacy `gold_*` file paths), full armor matrix (7 materials × 4 pieces) confirmed working; golden CROWN v4 (octagonal 8-panel wrap on a bone carrying the 13° tilt; position dialed over 3 witness iterations); `pw_golden_crown` attachable + icon + texts; golden_helmet RESTORED to diamond-formula in gold (teal→gold recolor, face opening intact); classic door ITEM sprites at legacy names |
| RP-04 Basic | v1.3.41 (unchanged) | Uploaded for the door hunt; its doors are MODERN generation (cherry/bamboo/mangrove/copper) with modern names → already correct; do not reinstall |
| am: BP + RP | **v0.6.1** | Architecture Wave: v0.4.0 first roof set → v0.5.x wedge rebuilds → v0.6.0 OVERHANG LICENSED → v0.6.1 companion script (§ below) |

**Falling-tree program Phases A/B/C (BP-02/RP-01) — SHIPPED**: Phase A texture match — canopy probe tallies `pw:variant` at fell; dominant → synced `ft:leaf_variant` [0,6]; RC array `Array.leaf_textures[q.property('ft:wood_type')*7+q.property('ft:leaf_variant')]`; sheets byte-copies → pixel-identical swap by construction; variant 0 = unrandomized/vanilla preserved; crimson/warped/mushroom keep aliases (no pw families — backlog). Phase B contiguity — own-canopy claim BFS from FELLED logs runs before standing-log protection; protection exempts owned leaves in seed+expansion (tie to the fallen tree); range 6→8; canopy_size mapping +1 tier (reversible mapping form). WATCH: `MAX_LEAVES=260` per-fell cap — elder crowns can exceed; scale-by-tier on request. Phase C stump seat — anim root drops 0→−16u over 0.3s (the witnessed clip-through was in keyframes); spawn `stump.y+1` on primary AND legacy paths (**L-PATH-1** caught the fallback); contact-angle pivot corrected (flat → ~−92°, tip truly grounds); corridor gates verified unaffected; RP anim untouched → timing law holds by construction (FALL_DURATION 101t, anim 5.05s). Deferred by witness: Phase E (birch black spots) + AV session until screen recordings exist; Phase D (spawn-time canopy capture) awaits separate approval. Diagnostic note preserved: `rnd=0` on revisited terrain is benign (already-randomized rescan).

**Golden equipment arc — CLOSED (hardware-confirmed) + crown program**: **L-ICON-1 (LOCKED, witness-confirmed)** — Bedrock armor icons resolve via vanilla PER-PIECE texture ARRAYS (item_texture.json keys `helmet/chestplate/leggings/boots`, material-indexed); per-material atlas keys are inert; gold slots point at LEGACY paths `textures/items/gold_*` — Java-named `golden_*` files override nothing; fix = file-level overrides at exact vanilla paths. (The witness's historical clue — "diamond showed Patrix, reverted after equip, in a previous iteration" — unlocked the mechanism.) Investigation-history preserved for method: the "RP-08 not applying" conclusion was FALSIFIED by the user's edit-world screenshot (description-stamp proved v1.3.63 active) → truncated evidence listings banned; the legacy attachable-NAMING theory falsified by vanilla fetch (identifiers `golden_helmet`/`chainmail_helmet` are modern; ours were correct). **Crown ledger**: v1 fork `geometry.ar.golden_crown` (band above eyes, icon-mask spike alpha) → tilt sign corrected (+13 = player-left; renderer roll calibration BANKED — witness: "tilt is perfect") → three position dials (**L-DIR-1 born**: the witness's "left" was VIEW-left; both frames echoed on every lateral directive since) → **v4 octagonal wrap**: 8 Y-rotated panels, apothem 5.0, texture in 4 circumference strips (spike alpha preserved), 13° tilt on a BONE (per-cube combo would skew the tilt axis — bone/cube split law); final pivot [−0.35, 28.85, 0]. **Item split**: `pw:golden_crown` = the dignifier (crown art + geo + aura); `golden_helmet` = proper armor (diamond projection re-palettized teal→gold, 64,630 px; icons recolored at both gold sprite paths). **Crown aura (BP-02)**: warden math of record — sonic boom BYPASSES armor points; protection:100 as asked, survivability from scripted Resistance IV (amplifier 3; 4 = immunity); flame + dynamic light independent toggles; dynamic light = light_block-follows-player, air-only, typeId-guarded cleanup. Pending witness at session end: crown v4 on-body (Y-rot + bone-tilt in the L-ROT sign-risk class), crown item registration (#77 watch), aura test, golden helmet look.

**Architecture Wave (am: private pack; license law in force) — the roof ledger**: v0.4.0 first roof set (8 blocks: oak+spruce × 45/ridge/63L/63U, MERS shingles, recipes) → witness "sloped visual on stairs… didn't work" → **witness design law: MORE SPECIFIC PIECES, DUMBER SCANNERS** (63 = 1-across-2-up; local scans can't distinguish 1H2V vs 2H1V intent → explicit lower/upper, facing-only; 45 = native `vertical_half` click intent, zero scanning) → v0.5.0/1 (solidity gate; **L-ROT-1 LOCKED**: +θ = engine X-rotation for block cubes — the circular-gate lesson: rasterizers validate hypotheses, only the witness validates conventions) → v0.5.2 rafter-over-plank-courses ("planks ending at the roof"; NO-GAP gate cov≥0.985) → v0.5.3 (bounds lock; full-tent ridge per witness — later independently validated by Medievalism's own collision shapes) → **v0.6.0 OVERHANG LICENSED** → **v0.6.1 COMPANION SYSTEM**.
- **SUPERSESSION (D-108, this session's journal, witness-directed)**: bounds-lock law ("lock the images", 05x) SUPERSEDED BY overhang-license law ("fully allow it, AS LONG AS no clipping + smooth/clean") after Medievalism mesh evidence. Preserved constraint: clipping banned — enforced by the gate trio: render envelope (±12, −4..20) + NO-CLIP CONTRACTS (outside-block geometry confined to perpendicular slope bands + declared eave/apex air-cell rects, stray ≤1%) + in-block coverage ≥0.97. Gate-craft lessons: perpendicular-distance metric for slope bands; half-cell rasterization tolerance at block boundaries; "proud" anti-z-fight offsets FORBIDDEN on contract-gated surfaces (D-106); deterministic analytic insets replace stateful search loops.
- **v0.6.0 geometry (Medievalism-measured)**: 45 eave plane to (−11,−3) + drip fascia; 63L eave (−9.5,−3); sheathing PROUD (+1.2/−1.0 about the ideal plane); tent ridge drip lips + apex cap to 17.6; 63U trim past apex.
- **v0.6.1 COMPANION SYSTEM** (first am: script; manifest script module + `@minecraft/server` 1.16.0 added): place a 63 LOWER → UPPER auto-places above with copied facing (withState; graceful fallback logs `[AM-COMPANION] facing copy unavailable` — #77 watch); break either → partner removed + dropped as item; occupied cell → lower stands alone. Witness on the design: **"ABSOLUTELY brilliant."** Generalization banked: **companion placement as BUILD GUIDANCE** (observatory ribs, crown molding — the partner teaches the continuation).
- **63 consolidation RESOLVED by consultation**: Bedrock collision_box is clamped INSIDE the block's cell (Java Medievalism's is too, per bytecode salvage) → a single-block 63 can never carry upper collision → two real blocks + companion sugar is canonical.
- Proposals on the table at session end: VAULTED CEILINGS (one block, `vertical_half` click intent extended to 63 family + ridge, ceiling-look via permutation-level material_instances; contracts hold by symmetry under [180,yrot]); ARCH P2 spec shipped awaiting 3 answers (auto-transform vs explicit L/R; materials; solo-arch semantics). Watch: render_method alpha_test on roofs (A/B vs opaque if VV artifacts). Recipes: 2×3 planks→6 straight; +plank=63L; +stick=63U; ×2=ridge.

**Medievalism v7 study (license: technique-only, private, never distributed)**: distribution architecture mapped (RP per-resolution + Mod + Modrinth + Dev Map — everything supplied). **The three-stage hunt (method laws)**: (1) RP block models read as "empty shells" — WRONG: a partial field dump missed `"loader": "neoforge:composite"` → `"neoforge:obj"` → **LAW: schema investigations dump FULL RAW BYTES, never field projections**; (2) "no meshes in archive" — WRONG: json-filtered listing → **LAW: absence claims require a complete extension census** (120 OBJ + 117 MTL true meshes); (3) mod JAR assets = lang only (MCreator/NeoForge; models ship in the RP). **Bytecode salvage tool (reusable)**: pure-python .class constant-pool + bytecode walker (javap absent) → recovered VoxelShape collision decompositions: 45 = 4-step staircase; 63 = single-block staggered steps; ridge = FULL TENT from bottom corners (independently validating the witness ridge spec). **True-mesh findings**: meshes deliberately EXCEED the block (45: 16×21×19; 63: 38.7u tall; ridge 23×22) — their polish derives from designed overhang → drove the D-108 supersession. Piece taxonomy banked as roadmap: per pitch straight / corner concave+convex / ends L,R / ridge + ridge corner/T/cross/ends.

**Darkness case — CLOSED (engine-side conviction)**: the BP-01 v1.3.29 discriminator worked in one episode — darkness outlived the 15s re-assert → the stuck-fog class EXONERATED. Convicting chain: chunk-grid "boxy" spread (witness-confirmed) → relog usually heals → **NEVER on PS5 sharing the SAME world** (perfect natural control: same chunks/packs/scanner, different renderer → content exonerated as direct cause) → **caught mid-episode: ONE FRAME showing TWO time/weather states** (night+storm left, clear midday right) split on a hard seam through sky gradient, cloudscape AND terrain lighting. A world has one time; two rendered states = renderer state defect. **Conviction: Android Vibrant Visuals deferred-renderer STALE-ATMOSPHERE PARTITION** (regional stale night/storm lighting; rebuilds on rejoin). Scanner demoted to possible stressor only (near-idle at capture). Deliverables: annotated evidence panel + filing-ready Mojang bug report. Standing offer: optional Android-comfort throttle, on request only. Pending corroboration: relog-heal on next load.

**Classic door fix (L-ICON-1 EXTENDED to blocks)**: witness datum — the earlier double-door auto-hinge system (prior conversation; script fine) showed VANILLA door textures. Vanilla-source-verified mechanism: the six classic doors use LEGACY file names (`door_wood_upper/lower`, `door_<wood>_*` — all 200) while Java/Patrix names 404; moderns use modern names → RP-04 was already correct (why only oak was noticed). Shipped: RP-03 v1.3.40 + RP-08 v1.3.69 sprites, byte-equality gated. **L-ICON-1 now covers blocks AND items.** Backlog (M/high): audit ALL ported vanilla-override textures for legacy-name families (beds, signs, chests, grass_side…).

**Lessons & laws (new/locked this session, carried verbatim)**: **L-ICON-1** (locked — vanilla legacy file naming traps Java-named overrides; override at vanilla's exact paths); **L-ROT-1** (locked — +θ = engine X-rotation for block cubes; rasterizers model hypotheses, the witness validates conventions); **L-RENDER-1** (offline preview renderer trusted for texture/design reads, NEVER for engine placement/rotation semantics); **L-DIR-1** (lateral directives may arrive in VIEW frame — echo BOTH frames before building); **L-PATH-1** (primary/fallback duplicate code paths are a cross-path consistency class — census duplicates on every shared-constant change); **D-101 tooling law** (hard: completion log lines written INSIDE gated python only — shell `cat >>` runs regardless of exit code; four slips forced the structural fix); geometry writes use round(v,3); evidence prints never truncated ([:N] banned on listings); full-raw-bytes law; extension-census law; the witness design laws (specific pieces/dumber scanners; overhang licensed/clipping banned; companion as build guidance).

**Open board at session end**: witness verdicts (Phases A/B/C in-game; crown v4 + item + aura; golden helmet; v0.6.0 eaves; companion-63 test card; doors swinging Patrix; darkness relog corroboration); decisions (VAULTS one word; ARCH P2 3 answers; optional Android throttle; optional 63 mega-mesh visual — not recommended, collision truth); queued (arch build on approval; corner pieces per taxonomy P1.5; legacy-name audit; crimson/warped/mushroom leaf sources; HISTORY-v4 synthesis; Phase E + AV; Phase D approval; redwood deferred; Lesson #135 verification deferred); watch (MAX_LEAVES=260; alpha_test vs opaque under VV; trait-state write #77; crown octagon sign-risk).

## VI.5 — Session 2026-07-06 → 07-07 — "Roofs · Planks · Provenance · Migration"

*The source handoff for this session is the live CURRENT-STATE and remains in project knowledge (rule 5); this chapter absorbs its history.*

**Version ledger (every ship, with MD5):**

| Pack | Version | Headline | MD5 |
|---|---|---|---|
| am: BP/RP | v0.6.2 | Roof kiss-fix (boards mate the step-corner diagonal; −1.0 interpenetration cured) + Companion v2 diagnostics | `314010368cbc617405e5316c3bb27a72` / `413f28c58d188d4f8a538af7c16c3212` |
| am: BP/RP | v0.6.3 | Gable alpha-image fill (Abs0lum's design), r=0.25 recessed quads, k=0 ground triangles | `8042dd750cefb29ed2ec21e1b51ca818` / `0240c20eb9ea7b3b56231bb6c3c02288` |
| am: BP/RP | v0.6.4 | Single-face quads (flicker fix), mirror topology, boards trimmed to flush cell-spans, support-below fill law, fascia tucked | `6fcd6c04189ca10cc9e4d4519df198ad` / `d8463755dcc906c6ef7493c246d0e924` |
| am: BP/RP | v0.6.5 | Patrix-derived roof textures (approved plank design @512), normals regenerated, fill bands re-derived | `5cea3d82b6ad63e5af5b3abb578517c1` / `9773425c92b17c84367ae8299d1b18d0` |
| am: BP/RP | v0.6.6 | Spruce noise-floor propagation to roofs + spruce fill bands | `3037f9cb41ff3353b9fcda33dd1b0744` / `9761f0e44b0801ec630b41e52e3580b6` |
| RP-03 | v1.3.41 | PLANK REBUILD: approved A/B pattern, 12 species / 64 maps, context-derived borders, seam-free grain, 12 normals regenerated | `df464e75e4a3718402148a2ceeb3a536` |
| RP-03 | v1.3.42 | Border grain-noise floor: dark_oak + spruce deepened; vis-ratio ≥1.5 gate all species | `b99bc3467b53ff56c5c14d0ac78eb6b6` |
| RP-04 | v1.3.42 | Plank set replicated into Basic RP (byte-identical to RP-03); STALE STAMP fixed (was v1.2.52 text) | `601601a3fc149be42cbf7285a0d9bbc6` |
| **RP-04** | **v1.3.43** | **MIGRATION: pw: roof visuals + pw_angled_wall geometry land in AbsolutRealism (dossier-cited)** | `24b71203854006924d62ace3dbe02fbb` |
| **BP-02** | **v1.3.55** | **MIGRATION: 8 pw: roof blocks + 8 recipes + PW-C2 companion @2.0.0 + pw:angled_wall (13 materials)** | `bf012ac2e5da835bb6ccd46cb2d885f8` |
| **am: BP/RP** | **v0.7.0** | **Roof family PORTED OUT (44 files stripped, tt pruned, script stubbed); am: = Medievalism study content only** | `b4c3969815774b522ebdc9bd42f923b5` / `49c1eb6baa06f12bd200a60fb1c0ffc4` |


Docs shipped: PROVENANCE-DOSSIER-ROOF-PIECES-v1 · PRIOR-ART-CLAIMS-ADDENDUM-v1 (+Part C) · MIGRATION-PLAN-ORIGINAL-WORK-v1 · per-ship READMEs · MD5 registries.

**Arc A — roof defect chain (all witness-driven):**
- **A1 Gable "teeth"**: after one retracted wrong turn (honesty ledger below), true mechanism: the v0.6.0 "+1.2/−1.0 proud" sheathing spec buried each board 1.0px INSIDE the step cubes; interpenetrating solids painted overlapping same-facing faces on the shared x=±8 gable planes → z-fight teeth. **MATING/KISS LAW**: solids sharing a boundary plane must not interpenetrate; the board underside was raised to kiss the step-corner diagonal exactly (all 7 corners colinear — one thin board suffices). All five boards across four geometries carried the identical 1.000px defect.
- **A2 Void fill**: cube-based sub-step fills rejected; **Abs0lum invented the superior solution** — each riser void is a closed triangular prism EXCEPT its two gable-end triangles → two zero-thickness quads per block carry an alpha-test texture painting the whole reverse-step band. Recess r=0.25 (face-on invisible, kills neighbor-quad coplanarity). k=0 ground triangles initially included, then REMOVED by witness verdict → **SUPPORT-BELOW LAW**: fill paints only void columns with a course beneath (gated).
- **A3 Fill flicker** (witness recalled the heartwood-filler precedent): a 0-thickness cube with BOTH faces textured self-z-fights. **SINGLE-FACE QUAD LAW**: visual quads render exactly one outward face. Retro-Sweep hit: verify the heartwood filler's current form (open investigation candidate). Mirror topology corrected same build (east normal / west u-flipped); the global-orientation coin awaits the 45 witness verdict — 63s inherit it.
- **A4 Board length** (witness: below y=0, over-hang): all boards trimmed so underside endpoints land EXACTLY on each piece's in-cell diagonal span (45: (0,−8)→(16,8); 63L: (0,−8)→(16,0); 63U: (0,0)→(16,8); ridge symmetric); consecutive pieces butt flush with opposite-facing end faces. Fascia repositioned to the new eave ([−8,−1.4,−8.8]) — flagged judgment call awaiting verdict.
- **A5 Roof textures**: witness "cartoony" on Medievalism textures — validated mechanically (authored for Java shaders; OldPBR height/spec carried the depth; color-only flattening collapses it). Replaced with Patrix-derived generation from the approved plank design; normals regenerated; spruce noise-floor propagated (v0.6.6).

**Arc B — plank program (12 species; laws established)**: approved pattern (Abs0lum): 128px, 4 rows ×32px, alternating **A = FULL|FULL (joint @64)** and **B = HALF|FULL|HALF (joints @32,96)**; grid-line convention (line at row top + plank left); B rows have NO edge verticals; the two half-planks painted from ONE continuous grain strip split across the wrap → a wrapped plank reads as a single board across block seams. Style S2 dark line, evolved through suite-forced iteration into: **BORDER-RELATIVITY LAW** (never fixed line colors across species — fixed brown screamed at 48–97 contrast on light woods and INVERTED on acacia; line pixels derive from LOCAL CONTEXT × 0.72 — Weber-correct relative contrast by construction); **GRAIN-NOISE FLOOR** (witness: pattern invisible on dark_oak, "maybe spruce" — both confirmed by measurement, vis-ratios 0.96/1.00; visibility = delta vs local grain noise, not luma: delta_req = max(14, 1.6·grain_std); per-pixel k = clamp(1−Δreq/Lctx, 0.40, 0.72); suite gate vis-ratio ≥1.5 all species); **ONE-METRIC LAW** (fixer and verification gate must share ONE metric or convergence is luck — spruce_planks_3: sampler measured 32 rows, gate 29). Seam-free sampling (reject rolls carrying source cliffs >8) + iterative feathering + post-write recheck. 12 normal maps regenerated (grooves at NEW joints — old normals would ghost the old pattern under VV; luma-derived v1, witness under VV pending). Deployed byte-identical to RP-03 AND RP-04 (pack order moot). Open offers: variant phase-shift (v0=ABAB/v1=BABA) unapplied (never approved); bamboo included per "every variant" but may deserve exemption on sight.

**Arc C — companion/auto-transform**: witness "auto transform never triggered." Static teardown ALL-PASS (playerPlaceBlock verified IN stable 1.16.0 via npm type defs — an L-SCHEMA-1 win). True cause: **coverage** — tests used 45s; only 63-LOWER had a rule. **Companion v2**: boot beacon (content log + chat), GATE 1–5 chat diagnostics per 63-LOWER placement, "no transform rule exists for this piece" announcements on 45/ridge (coverage gaps can never read as silent failures again), zero silent catches. Ported to `@minecraft/server` 2.0.0 in the migration as BP-02 `scripts/pw_companion.js` (one import line in main.js; BIGCANOPY untouched; prefix **[PW-C2]**).

**Provenance & IP — rulings in force (recorded law; full text in the dossier + addendum, incorporated into the live CURRENT-STATE):**
- **Standing-law amendment (Abs0lum, 2026-07-07)**: the sloped roof family (45/63/ridge — geometry, mechanics, generators, Patrix-derived textures, v0.6.6+) is ruled **original AbsolutRealism work** with documented prior art (stepped cubes 05-17; observatory + angled wall + stepped-height articulation 05-31; terrain caps 06-01 — all pre-Medievalism 07-03; zero Medievalism expression in shipped artifacts; mined eave dims removed v0.6.4; textures Patrix-derived v0.6.5+). Cleared for `pw:`. **Executed** via the migration (RP-04 v1.3.43 / BP-02 v1.3.55 / am v0.7.0).
- **Claimed families (addendum Parts A + C), homed in pw: for all future builds**: angled/diagonal walls (strongest claim — the 05-31 spike, REBUILT this session as `pw:angled_wall`) · vaulted ceilings · the auto-transform mechanic + application list (prior art: terrain lattice, trunk scanner, pw: oak double-door hinge work; IP line drawn AT directive creation 07-04) · window/glass wall concept class (bay-window lineage 05-31) · gable infill technique · plank flooring · arch AUTO-MECHANIC incl. keystone (concept only) · **oculus** (Part C — the verbatim keystone→observatory trajectory; nothing in their pack to derive from) · designer's-method evidence (CAD fluency, architecture coursework, precision internal-imagery process).
- **Left behind, am:/private forever (Part B)**: arch MESH PROFILES (curves, gothic pointing — P2 parses their OBJs), timber framing/beams, fences & stairs-fence combos, arrow slits, decorative wall patterns, all Medievalism-textured content (terracotta).
- **NO-CONSULT RULE (in force)**: claimed-family builds never consult Medievalism assets; any consultation moves that piece to am:. Abs0lum's stated intent: never look again.
- **Inspiration-chain note on record**: Medievalism's own Patreon credits Patrix for inspiration; ideas flow down chains lawfully — only expression carries ownership. Abs0lum's conduct (FreshLX permission, renaming, independent engineering, honest ledgers) is the higher standard in the chain.

**Lesson candidates awaiting formalization**: mating/kiss law (L-ROT-1 family interaction — evaluation-timing question STILL OPEN with Abs0lum); single-face quad law (+ heartwood verification candidate); support-below fill law; border-relativity + grain-noise floor + one-metric laws; interpenetration + coplanar-overlap verifier gate (in suite; formalize); description-stamp violations found (BP-03 v1.2.52 text @ v1.3.28 — still open; RP-04 fixed v1.3.42); environment watch — the assistant's view tool failed to render its OWN generated images 4× this session (witness images attached in-message rendered fine) → workaround: witness critique is the verification for aesthetics; direct-attach frames for defect reads.

**Honesty ledger (assistant's corrected calls, preserved)**: "corners buried −1.2 by design" → sign-convention bracket → "board on wrong side of diagonal" → RETRACTED after a pivot-intercept arithmetic slip was found (c=y−z: 8.142 not 5.0); final verified mechanism = designed interpenetration → gable-plane z-fight; the witness's fix concept survived all three framings unchanged. "Exact triangular fill impossible" → true for SOLID geometry, overstated as blanket — Abs0lum's alpha-image insight was correct and superior; conceded and credited. alpha_test promoted to prime flicker suspect → demoted (geometric + double-face causes proven); remains a deferred watch (opaque-flip A/B).

**Open witness stack at 2026-07-07 (the live CURRENT-STATE §8 carries this)**: pw: roofs render parity vs am v0.6.6; [PW-C2] boot line + GATE 1–5 + 45 "no-rule" line + pair-break; mirror orientation BOTH gables (global coin); flicker extinction; stacked 63L+63U+ridge junction; fascia verdict; grazing shimmer (r=0.25); **pw:angled_wall debut** ("/" on N/S facing, "\" on E/W, 13-material cycle, glass transparency, full-block collision); plank readability in-game (dark_oak/spruce, bamboo call, normals under VV, Patrix roof sharpness); am v0.7.0 old placements render UNKNOWN — rebuild test structures in pw:.

## VI.6 — POST-2026-07-07 RECORD GAP (append point)

Ships after the 2026-07-06/07 handoff have no handoff coverage in the sources of this synthesis. Per Abs0lum's record reconciliation (2026-07-10, hard anchors from the pack git archive description stamps):

- **RP-01 v1.3.56 is NOT a gap ship** — it is the single 2026-07-05 ship ("PHASE A: per-variant canopy textures, leaf_variant RC array") chronicled at VI.4; the synthesis charter's gap line overstated. No number reuse in evidence.
- **The true post-07-07 gap ships**: **RP-01 v1.3.57** (2026-07-10, sound-only: 8 fall oggs normalized onto the 2200ms/44t grid + stamped manifest) and **any BP-02 / RP-04 terracotta ships the 07-06-07 handoff doesn't carry** (e.g., a BP-02 v1.3.56).
- **RP-01 v1.3.55**: no ship attested in any source. The 07-04 session had earmarked "BP-02 v1.3.47 + RP-01 v1.3.55" for the upright-snap fix, which remained on the open board (unbuilt) as of 07-07 — the number's actual disposition awaits the next handoff.

**Their full entries append here when their handoffs are uploaded.** This chronicle asserts nothing further about them.

---

# PART VII — CUMULATIVE REGISTERS

## VII.A — Version ledger (complete)

### VII.A.1 — Unified-stack era (one number, whole suite)

| Version | Date | Theme | Status |
|---|---|---|---|
| v1.0.0 | 05-06 | Initial production ship (PatrixWorld) | superseded |
| v1.0.1 | 05-07 | Rename → Abs0lutRealism; atmos tuning | superseded |
| v1.1.0 | 05-07 | Performance pass | superseded |
| v1.1.1–v1.1.3 | 05-07/08 | ContentLog closure; canopy; sun visibility | superseded |
| v1.2.0 | 05-08 | Cinematic mood + lens flare | superseded |
| v1.2.1–v1.2.5 | 05-08 | Mood iteration (H-01..17 family) | superseded |
| v1.2.6 | 05-08 | Texture pipeline repair (H-18) | superseded |
| v1.2.7–v1.2.9 | 05-08 | RC integration; visual fixes; water/sand/ice PBR | superseded |
| v1.2.10–v1.2.12 | — | refinements | superseded |
| v1.2.13–v1.2.14 | — | manifest corrections | superseded |
| v1.2.15 | 05-09 | DISASTER (dep stamping) — never use | dead |
| v1.2.16 | 05-09 | Recovery (H-53/54/55) | superseded |
| v1.2.17–v1.2.18 | — | iteration | superseded |
| v1.2.19–v1.2.21 | 05-09 | Dodecagon trunks; falling-tree rebuild; branches+sounds | superseded |
| v1.2.22–v1.2.26 | 05-09 | chord-flush; panel widths locked | superseded |
| v1.2.27–v1.2.31 | 05-10 | Leaf overhaul; cascade; scanner fix | superseded |
| v1.2.32 | 05-10 | MERS + inner-core + U4 (KNOWN-GOOD baseline of its era) | superseded |
| v1.2.33 | 05-10 | REGRESSION — never use | dead |
| v1.2.34–v1.2.35 | 05-10 | regression fix; variant refinements (v35 graphics-reset bug) | superseded |
| v1.2.36 | 05-10/11 | Scanner rewrite (silently broken) | superseded |
| v1.2.37–v1.2.39 | 05-13 | cadence; diagnostics; BlockVolume hotfix | superseded |
| v1.2.40 | — | SKIPPED | — |
| v1.2.41–v1.2.42 | 05-13 | revert to v1.2.35 architecture; layered+BFS | superseded |
| v1.2.43–v1.2.45 | 05-13 | tapered protrusions; tree-feature conflict; cut 2 | superseded |
| v1.2.46 | 05-14 | Sand PBR rebuild (ambientCG) | superseded |
| v1.2.47 | 05-14 | leaf bones final (texture regression) | superseded |
| v1.2.48 | 05-14 | texture_height revert | superseded |
| v1.2.49–v1.2.51 | 05-14/15 | shims; blocks.json; black-leaf; far-render v1 | superseded |
| **v1.2.52** | 05-15 | far-render final — **USER-VERIFIED WORKING** | historic known-good |
| v1.2.53–v1.2.54 | — | attested by reference only (Part IV.1) | record gap |
| v1.3.0–v1.3.4 | — | not attested as ships (sky-era tests were v0.x) | record gap |
| v1.3.5 | 05-17 | SKY ROOT CAUSE fixed; Phase-1 scanner | superseded |
| v1.3.6–v1.3.9 | 05-17+ | PATH D; vine fix; fireflies; alpha-sky; fog-stack sky | superseded |
| v1.3.10–v1.3.20 | — | RECORD GAP (D-181/203/205/219, D-233–236 attested) | record gap |
| v1.3.21 | — | user-approved sky baseline | superseded |
| v1.3.22–v1.3.27 | 05-23~ | fog schema saga; scanner Process A/B; sun_vv | superseded |
| v1.3.28 | 05-24 | polishing pass (branches off; 14 features; anim threshold) | superseded |
| v1.3.29–v1.3.33 | — | RECORD GAP (vanilla-vine routing fixed in-span) | record gap |
| v1.3.34–v1.3.35 | 05-2x | RP-07 mob conversion + patches; BP-02 TPS fix | last unified versions |

### VII.A.2 — Per-pack era (2026-07-03 →); latest attested version per pack

| Pack | Chain (this chronicle) | Latest attested | Note |
|---|---|---|---|
| RP-01 Tectonic | v1.3.47 → v1.3.54 → v1.3.56 | **v1.3.56** live; **v1.3.57** = post-07-07 gap ship (sound-only) | absorbs RP-09 |
| BP-02 Tectonic | v1.3.38 → v1.3.39–46 → v1.3.54 → v1.3.55 | **v1.3.55** | absorbs BP-05; PW-C2 |
| RP-03 PBR | v1.3.39 → v1.3.40 → v1.3.41 → v1.3.42 | **v1.3.42** | |
| RP-04 Basic | v1.3.41 → v1.3.42 → **v1.3.43** | **v1.3.43** | + roof family + angled wall |
| RP-06 Hostile | v1.3.41 | v1.3.41 | |
| RP-07 Neutral | v1.3.41 | v1.3.41 | v1.3.35-era content |
| RP-08 Items | v1.3.43 → v1.3.63 → v1.3.69 | **v1.3.69** | crown, gold, doors |
| BP-01 Atmospheric | v1.3.28(BP) → **v1.3.29** | **v1.3.29** | fog re-assert |
| RP-02 Atmospheric | (v1.3.28-era) | v1.3.28-era | July RP-02 ship not attested in sources |
| BP-03 | — | v1.3.28 manifests, **stale v1.2.52 description** | stamp violation OPEN |
| RP-05 Flora / RP-10 / RP-11 / BP-04 | v1.3.28-era | v1.3.28-era | |
| RP-09 Trees / BP-05 Trees | RETIRED | — | absorbed 07-04 |
| RP-97 Armor Pilot | v0.1.0 → v0.2.2 RETIRED | — | job done |
| am: Medievalism BP/RP | v0.3.0 → v0.4.x → v0.5.x → v0.6.0–v0.6.6 → **v0.7.0** | **v0.7.0** | roofs ported out |

## VII.B — Lesson index (cross-reference)

- **Numbered (#1–#206)**: FOUNDATION-v3 is the register of record. Chronicle birthplaces: #1–125 (v1.0.0), #126–152 (v1.0.1), #144–155 (v1.2.28–31), #154–159 *second series* (v1.2.32 — collision with the v1.2.31 candidates #154/#155 preserved as-is; see Part 0.4), #160–163 (v1.2.34), #170–175 (v1.2.36), #196–206 (v1.3.34/35).
- **H-family**: born v1.2.x (H-18 texture-pipeline; H-53/54/55 manifest laws; H-14 density cap; H-22/23 water schema; H-31/32 sources & sand; H-24 god-ray recipe — corrected form at IV.2).
- **G-family**: v1.2.0 cinematic mood (G-01..07, supersessions logged in Part I §2).
- **L1–L10**: Part II.8 (full text).
- **L-SKY-1..6, L-SCAN-1..2, L-ATMO-1, L-PKG-1, L-METHOD-1, L-API-1, L-FX-1, L-WORLDGEN-1..2, L-WITNESS-2, L-PROCESS-1**: Part III.5 (full text) + IV.3 (L-WORLDGEN-2).
- **L-SCHEMA-1**: IV.2 (fog saga). **L-ANIM-1, L-VV-2, L-PARTICLE-1**: IV.3. **L-VV-1**: IV.2 (sun_vv).
- **July laws**: L-ENTITY-1/2, L-VAR-1, L-TOOL-3 (VI.2); L-GEO-FLATTEN, L-TEX-1, L-DIAG-1, L-PERF-2, L-ATTACH-1/2 (VI.3); L-ICON-1, L-ROT-1, L-RENDER-1, L-DIR-1, L-PATH-1, D-101 tooling law (VI.4); mating/kiss, single-face quad, support-below, border-relativity, grain-noise floor, one-metric (VI.5, candidates).
- **Unnumbered v1.3.35-era TPS lessons**: V.3 (FOUNDATION absorption pending).

## VII.C — Ship-artifact MD5 registry

All MD5s recorded in this chronicle, by era: Part I §7 (v1.2.32/34/35/36 tables), Part II (v1.2.45→52 per-version), Part IV.2 (v1.3.23/25/26/27 + small-sun `bd697292bb582c9f732cadbd2a7154b5`), Part V (RP-07 patches 6/7/8), Part VI.5 (the twelve-ship table). Per the suite-gated packaging law, an MD5 in this chronicle attests a build that passed its verification suite.

## VII.D — Decision-journal index (session-scoped; see Part 0.2)

- **D-1 → D-260 (the unified-era build machine's journal)**: D-010 (spike corrected), D-051/D-052 (storm-perception), D-054 *(era)* , D-056 (double-grade), D-071 (orientation WRONG → D-128/129), D-077 (parse-OK precedent), D-085 (volumetric_scattering), D-088 (magenta matrix era), D-094→D-136 (sky root-cause session: D-101 hang diagnosis, D-102 caller audit, D-105 rayleigh, D-108 *square-oak-vine deferral*, D-109/D-112/D-114/D-115/D-117/D-118/D-121/D-122/D-124 the root-cause chain, D-128/D-129 orientation locked, D-131 audits, D-135/D-136 mcaddon law), D-138→D-165 (alpha-sky session: D-140 zenith bleed, D-144 PATH D, D-145→D-151 vine chain, D-146→D-147 witness-misread correction, D-149/D-150 mechanism+fix, D-152→D-153 fireflies, D-154 projection seam, D-155 valley scan, D-158 fog-stack architecture, D-159→D-160 API near-miss, D-162→D-164 schema fix + alpha build), D-181/D-203/D-205/D-219 (gap-span locks), D-233→D-236 (clouds), D-237→D-251 (fog/sun/scanner session), D-252→D-260 (v1.3.28).
- **July sessions journal their own D-numbers per session**: e.g., D-54 (BP-01 re-assert hardening, 07-05/06), **D-108 (overhang-license supersession, 07-05/06 — collides with the sky-session D-108)**, D-101 (tooling law, 07-05/06), D-106 (proud-offsets ban). Always cite July D-numbers with their session handoff.

## VII.E — Cross-pack timing constants (assert equal before shipping)

Falling-tree family (as of the latest attested ships): `FALL_DURATION_TICKS = 101` (BP-02) · fall animation_length **5.05s** / controller threshold **5.03** (RP-01) · impact cue **82t** · sample peaks normalized **+0.5s** · REST **70t** · gravity-drop 0.3s/−16px · stump-top spawn +1 (both paths). Desync history: the 1.78s-vs-3.85 truncation (IV.3), the 5.35→4.60 retime + 106t phantom (VI.3). *(The post-07-07 v1.3.57 sound work re-anchored fall audio to a 2200ms/44t grid — its constants enter this register with its handoff.)*

---

# END OF HISTORY v4

*Synthesized 2026-07-10/11 (Cowork session, Abs0lum-approved outline; coverage audited in COVERAGE-VERIFICATION.md; independent token audit passed 2026-07-11). The era archive and state documents listed in the front matter are retired upon Abs0lum's approval of this document; the live CURRENT-STATE (newest handoff) and the FOG-LIGHTING dossier remain in project knowledge. Post-07-07 ships append at Part VI.6.*
