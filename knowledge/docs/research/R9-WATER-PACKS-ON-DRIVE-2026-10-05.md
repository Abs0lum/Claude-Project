# R9 — Water packs in the Drive "Packs" folder: census, the four new add-ons, and what to use for round 1006 (2026-10-05)

Companion to R8-WATER-MANIPULATION-2026-10-05.md. His 18:08: "If you're going to look at water packs, ALSO look at any other
water packs that are in the pack folder on the drive." Research only: nothing installed or changed, BDS not started.
Method: every folder under Packs (1ZHhqcLbhW_plxz4QYfpURF43-s8S_Zez) walked recursively; every archive's file list read over
HTTP range (tools/remote_zip.py) without downloading it; nested archives opened (stored by range, compressed < 30 MB in
memory); the four new add-ons downloaded whole and read line by line (~40 MB on disk, scratch waterpacks/).

## 0. Headline findings
1. **Dynamic_Flowing_Water = HDGMP Water Flow 1.0.0; Physics_water = HDGMP v2 2.0.0** — the same engine. Both use only
   `@minecraft/server` 1.14.0 (stable; no beta API, no experiment — R8 §3's "Experimental + Beta API" note is corrected).
   They are NOT particle effects: they rewrite `liquid_depth` on real water blocks (`setPermutation`) and several paths turn
   cells into **new SOURCE blocks** (v1 main.js 150/233, 172, 348; v2 349, 365, 370, the OBSTACLE template, the 327 clamp) —
   against our first water law, and they would fight the palace pumps. Off until `/function hdgmp/start_flow`; v1 and v2
   share function names and tags (never together). **Skip both.**
2. **UtilityCraft 3.5.4's Fluid Extractor removes world water**: a `liquid_depth` 0 block at its configured position →
   1,000 mB in the network → `setType("minecraft:air")` (`__bundle.js` line 194, `R1`/`vh`/`B1`); plus fluid pipes, tanks
   (basic…ultimate, creative), an infinite-water "sink", and a multiblock that clears its own box with
   `fill … air replace minecraft:water` layer by layer (the palace pumps' technique). Needs `@minecraft/server` 2.8.0
   (unverified on his build); a whole tech mod; no licence in the archive. **Port the mechanism into a pw: block.**
3. **Item Pipe 2.1.3 has no fluid** (`um:` item pipes; `um:item_pipe` 13 boolean states = 8,192 permutations, rewrites
   itself every 5 ticks). **Skip.**
4. **The best waterfall LOOK on the Drive is PUREVFX** (Bedrock): `dvfx:waterfall_mist`, `waterfall_splash`,
   `waterfall_cascade` particles + a waterfall scanner (`kzrmpvftxa.js`); it credits the Java mod Particular. The Java mods
   **Effective** (ARR) and **Particular** (LGPL-3.0) hold the original art; Effective also has `waterfall.ogg` (89 KB) and
   `water_river.ogg`.
5. **RP-02's `water/water.json` is byte-identical (md5 1e685a87…) to RealSource Realistic Visuals 1.9.1 LOW's.**
   RealSource's README: "I do not authorize the use of my texture, code or settings for personal purposes without my
   permission." There is no RealSource line on RESTRICTED-ASSETS. Recorded as a fact; nothing changed — his decision.
6. "WATERFALL" by BATBOA (R8 §3) is not on the Drive.

## 1. Census
| scope | entries | files | folders |
|---|---|---|---|
| Packs, recursive (incl. Mine, OldPacks, 12 folders of unpacked mods) | 114,550 | 109,438 | 5,112 |
| top-level files: Packs root 356 + Mine 33 + OldPacks 79 | 468 | 468 | — |
| archives whose file list was read | 425 top-level + 127 nested = 552 | | |
| top-level archive bytes | ~19.9 GB | | |

Subfolders: Patrix128+Alacrity 93,043 (unpacked Patrix 1.21.11 128x, Alacrity, LOW_RealisticJAVA 3.4, RealSource VV PLUS
2.0, BDS 1.26.14.1) · Fluids+Physics 7,805 (Java: physics-mod-pro v183i ×2, fluidphysics 1.6.0, flowing_fluids 1.0.5, wpo
0.3.0, FallingTree, efallingtrees) · OldPacks 5,718 · bedrockconversion 2,695 (our JEM output) · continuity 2,061 ·
Hyper_Realistic_Sky 1,661 · tectonic-3.0.22 477 · AmbientSounds 6.3.5 318 · atmospherics-2.6 141 · Dramatic Skys 103 ·
GlowingOres-RTX 58 · EnvironmentalRealism 41 · atmospherica 39 · Mine 33 files.
Mix of the 468 top-level files: our own 313 · third-party Bedrock 78 · Java resource packs 43 · Java mods 25 · wrapper zips 6
· BDS zips 2 · bedrock-samples 1. Duplicates: 58 same-size groups covering 156 files (mostly our builds stored twice).
Per-file table (468 rows): Appendix A at the end.

## 2. Water-relevant packs (K = 49 third-party families + 4 of ours)
### 2a. Mechanisms
| pack | platform | what | key files |
|---|---|---|---|
| Dynamic_Flowing_Water (HDGMP v1) | Bedrock BP, script | cellular automaton on liquid_depth; player pushes water | `scripts/main.js` (486 lines) |
| Physics_water (HDGMP v2) | Bedrock BP, script | template version of the same | `scripts/main.js` (638 lines) |
| UtilityCraft 3.5.4 | Bedrock BP+RP | fluid extractor, fluid pipes ×5, tanks, the sink | `BP/blocks/machinery/{tanks,pipes/fluid}`, `BP/scripts/__bundle.js` |
| Item Pipe 2.1.3 | Bedrock BP+RP | items only | `BP/blocks/item_pipe.json` |
| wpo 0.3.0 | Java Forge 1.16.5 | finite water, pipe, pipe pump, fluid gate, pressured tank | `net/skds/wpo/block/*` |
| flowing_fluids 1.0.5 | Java Forge 1.21.9 | finite flowing fluids | `traben/flowing_fluids/*` |
| fluidphysics 1.6.0 | Java Forge 1.16.4 | finite fluids, FluidSourceFinder, RainRefill | `…/fluidphysics/util/*` |
| physics-mod-pro (6 builds) | Java | GPU ocean, splash sounds/particles, foam | `assets/physicsmod/{sounds/splash_0-2.ogg, textures/ocean/foam.png, textures/particle/splash_*}` |

### 2b. Looks: particles and sounds
| pack | platform | water content |
|---|---|---|
| PUREVFX 0.1.0 | Bedrock | RP `particles/rnykosol/{wfmisthy,wfsplash,wfcascad}.json`, `textures/PUREVFX/wfmistfx.png` (128²), `wfsplashtx.png`, `particles/water_splash_*`, splash atlases, `haru:puddle*`, ocean/river/rain/dawn-mist fogs, drip/river/ocean sounds; BP `scripts/kzrmpvftxa.js` (waterfall scanner), `scripts/waterSplash.js` |
| Effective 2.4.8 / 2.3.2 | Java | `particles/{cascade,mist,ripple,splash,droplet}.json`, `cascade_0-11.png`, `ripple_0-7.png`, `mist.png`; `sounds/ambient/waterfall.ogg`, `water_river.ogg`, `water_waves.ogg`, cave-water oggs |
| Particular 1.1.1 | Java | `particles/{waterfall_spray,cascade,water_ripple,water_splash,water_splash_foam,water_splash_ring}.json` + frames |
| VFXCore 1.8.1 | Bedrock | rain, rain_sheet, dripstone drip; water_impact and rain-surface textures |
| TreePhysics | Bedrock | `tree_splash{,_entry,_impulse}` (impact-scaled splash) |
| Kelly's RTX 3.6 | Bedrock RTX | overrides water/rain/cauldron splash and drip |
| Ultra Realism | Bedrock VV | `immersive_rain:rain_puddle`, rain-splash override, puddle PBR |
| More Events Remastered | Bedrock | `ae_me:mist` box emitter (≤ 1,000 particles) |
| natural_weather 1.0.4 | Bedrock | rain, rain fog, rain splash; rain sounds (needs server 2.9.0) |
| NaturalDisasters 0.48 · Nature's Touch 2.6 · Aurora Cinema v8 | Bedrock | heavy_rain · rainmist · fogs/mist |
| Naturalist 26.1 | Bedrock | whale_spray (already in RP-02) |
| ycreatures-savanna | Bedrock | `water_elefante` trunk spray |
| Actions Stuff 1.10 · Fresh Animations Bedrock | Bedrock | splash ring/mid/small/big, water_impact, wave, rain-drop textures; caustics |
| AmbientSounds 6.3.5 | Java | cave-water, ocean, beach, underwater, rain oggs (already in RP-02) |
| wwa-animals-r | Bedrock | `splash0/1.ogg` |

### 2c. Vibrant Visuals water
| pack | water settings |
|---|---|
| bedrock-samples (vanilla) | `minecraft:default_water`; waves off; caustics scale 0.5, power 1 |
| Definitive VV | `ale:Water` 16 octaves, depth 0.055, caustics power 3.5 scale 0.25; `ale:swamp_water` (sediment 1.45, cdom 1.2) |
| RealSource VV PLUS 2.0 / RV 1.9.1 LOW | 9 octaves, depth 0.08, pull 0.52, speed 2.6 (LOW: biome colour 0.15) — identical to RP-02's |
| Ultra Realism | `xv:water` sediment 0.82, cdom 2.65, 18 octaves |
| Brazz (8 variants) · Faithful 64x | caustics / vanilla values |
Other water textures: Optimum Realism RTX and Kelly's (normal/heightmap/MER), Patrix, Stratum, Alacrity, Faithful 32x,
LOW_RealisticJAVA; Hyper Realistic Sky rain skyboxes; Prominence II (Complementary shaders, Java only).

### 2d. Structures and worldgen
Village_Generator `plains/town_centers/fountain.mcstructure` (9×4×9) · vanilla `plains_fountain_01.nbt` · Animals and Fauna
watering holes / buffalo wallow · Better Biomes / Nature Overhaul cave pools, water lilies · TerraSphere / Horizon_Natural
river biomes · Epic Terrain `lake_water` · tectonic underground rivers.

### 2e. Our own suite
RP-02 2.0.x (RealSource water.json, caustics, 22 vanilla particle overrides, AmbientSounds water sounds, Naturalist spray) ·
BP-02 1.3.187 (frozen waterfall feature, misty_river / river_canyon biomes) · PW-Experience 3.0.0 · OldPacks/RP
`water_settings/pw_{alpine,cherry,desert,forest}_water.json`.

## 3. The four new add-ons in depth
### 3.1 Dynamic_Flowing_Water.mcaddon (7,021 B) — HDGMP Water Flow 1.0.0
- One BP: manifest, `scripts/main.js` (17,781 B), 5 functions, icon. No RP, blocks, items, entities; no licence/readme.
- Manifest: header uuid 5a5611ab-8ed4-57d0-9c29-a3c2b35a2a1b, min engine 1.21.0, script uuid
  51fb9997-534e-5446-928f-cf74cb9b5539, `@minecraft/server` 1.14.0; no beta modules, experiments or capabilities.
- Control: `start_flow` / `stop_flow` add tags read by a 4-tick loop (466-479); one global flag, off (40); `demo_pool`
  builds a 19×19 basin.
- Activation (81-109) scans 33×33×5 round the player, tracks ≤ 600 water cells. Flow (112-199, every 2 ticks) moves
  "height" (15 − depth) downhill, **creates water at depth 12 in neighbouring air while height > 2 (155-159)**, creates water
  below at max(0, depth − 2) (166-174), tops up below (175-187), sources creep back to depth 0 (118-126). Writes ≤ 45 a pass
  (202-287); a non-source at depth ≥ 13 becomes air (250-260). Player push radius 4 (290-363). Vanilla drip / splash
  particles (366-405).
- Against our measured facts: treats 0–15 as one height (Bedrock: 0 source, 1–7 flowing, ≥ 8 falling). Three paths make
  real SOURCE blocks (233 from 150; 172; 348). Its `minecraft:flowing_water` check (62) never matches (harmless).
- Cost while running: ≤ 5,445 getBlock per activation, ~4,000 getBlock every 2 ticks.
### 3.2 Physics_water.mcaddon (11,760 B) — HDGMP Water Flow v2 2.0.0
- One BP: `scripts/main.js` (23,246 B), 6 functions; header uuid 2b5ba6c8-a756-5e37-be0b-217deff04258, script uuid
  13c79925-46df-5c04-b867-da21accf50cd, server 1.14.0, no beta/experiments; shares function names and tags with v1.
- Classifies cells (FLAT, SLOPE, CHANNEL, OBSTACLE, CASCADE, SOURCE; 153-244), applies per-template deltas (58-88,
  303-377), reclassifies every 60 ticks; creates water downstream at depth 11 (355) and below a CASCADE at the cell's own
  depth (370 — can be 0); ≤ 50 writes a pass; depth ≥ 14 → air. Source-creating paths: 370, 349, 365, OBSTACLE (78-81), 327.
### 3.3 UtilityCraft_v3.5.4.mcaddon (4,952,589 B) — Dorios Studios
- BP uuid 9d61a8df-7d50-4624-8bff-d2c90c52a5a0, RP uuid b8bff6b0-417e-43fb-9451-d1d9d80c309f; server 2.8.0, server-ui 2.0.0;
  5,024 files; one minified `scripts/__bundle.js` (508 KB). No licence (two Spanish texture READMEs).
- Fluid Extractor (ticks every 10; line 194): water/lava at liquid_depth 0 = 1,000 mB; transfers ≤ 4,000 × (speed + 1) mB;
  then sets the source to air — in open water neighbours refill it (R8 V9), so it only empties a closed basin.
- Pipes and tanks; `utilitycraft:sink` infinite water; multiblock teardown `fill … air replace minecraft:water` top-down every
  2 ticks (line 25). Global cost: 4-tick counter, 300-tick machine loop, periodic inventory scan, several event subscriptions.
### 3.4 Item Pipe V2.1.3.mcaddon (107,159 B)
- BP 8ab84ba3-c676-46e2-a03c-251c32fd9245, RP 841147e7-8f03-4782-aa90-8f4ccb1d1914; server 2.0.0; no licence. `um:item_pipe`
  (8,192 permutations; `setPermutation` every 5 ticks, `item_pipe.js` 91-114; east check reads x − 1, 16-18), dropper, chest
  coupler (an entity per block). No water.

## 4. How the other water packs could serve the programme
- Waterfall mist / spray / splash: PUREVFX's scanner reads ~2,560 getBlock per player every 14 ticks; for OUR cascades we know
  every drop point at build time — emitters belong in the templates (a marker or a clock-driven spawnParticle in loaded
  chunks), not a world scan. Art: PUREVFX wfmistfx / wfsplashtx, Effective mist + cascade_0-11, Particular cascade / foam /
  ring / ripple.
- Sound: Effective waterfall.ogg (cascades), water_river.ogg (channels, culverts); PUREVFX drips + our AmbientSounds cave water
  (sewers).
- Fountain jets: Naturalist whale_spray (in RP-02) / ycreatures water_elefante re-tuned upward; TreePhysics splash_entry for
  impact-scaled basin splashes.
- Rain on streets: Ultra Realism rain_puddle, PUREVFX haru:puddle*, VFXCore rain-surface (looks only).
- VV water: Definitive's `ale:swamp_water` suits sewer/moat water — but water appearance is per biome, not per block.
- Pipes as decor: low-res industrial models — reference only. Fountain layouts: Village_Generator + vanilla plains fountain.
- Java references (code reading): wpo pump / fluid gate, fluidphysics source finder / rain refill, flowing_fluids.

## 5. Compatibility with our suite
- Namespaces: hdgmp, utilitycraft:, dorios:, um:, dvfx:, haru:, weather_immersion:, ae_me:, treephysics:, immersive_rain:,
  xv:, ale: — **no clash with pw: / am:**.
- Vanilla particle overrides depend on stack order (RP-02 overrides 22; Kelly's, Ultra Realism, PUREVFX override rain/splash).
- Water-writing scripts: HDGMP near a palace fights the pumps (incompatible). PUREVFX: scanners read only, but
  `waterSplash.js` calls getEntities on 3 dimensions every tick (145-150) and `dynamicLights.js` writes light blocks (103);
  toggles default on. UtilityCraft removes sources only where a player sets it. VFXCore read-only.
- API versions (BP-02: server 2.3.0): HDGMP 1.14.0 · Item Pipe 2.0.0 · PUREVFX 2.2.0 / ui 2.1.0 · More Events 2.2.0 ·
  VFXCore 1.11.0 / ui 1.3.0 · UtilityCraft 2.8.0 / ui 2.0.0 · natural_weather 2.9.0. No beta modules or experiments anywhere;
  2.8.0 / 2.9.0 unverified on his build (a BDS load test would show it).
- PS5 / phone: particle caps (PUREVFX wfsplash rate 30 max 60; ae_me:mist ≤ 1,000; TreePhysics ≤ 400); Item Pipe's
  permutations; HDGMP's ~4,000 getBlock per 2 ticks is the costliest thing found.

## 6. Licences (as each archive states)
HDGMP v1/v2, UtilityCraft, Item Pipe, PUREVFX, VFXCore: none in the archive (R8: CurseForge ARR for HDGMP/UtilityCraft) ·
Effective: ARR (Ladysnake) · Particular: LGPL-3.0 · physics-mod-pro: ARR · AmbientSounds: LGPL-3.0-only · flowing_fluids:
LGPL 3.0 · fluidphysics: Apache-2.0 · wpo: ARR · Ultra Realism: ARR, no asset extraction for other projects · RealSource:
no personal use without permission · Faithful: Faithful License v3 · bedrock-samples: Mojang / EULA · Village_Generator:
attribution, no redistribution, files not to be used in other add-ons · Fresh Animations: no modification without permission ·
Alacrity: ARR · Stratum: do not redistribute · Optimum Realism: ARR (lists CC BY 4.0 sources) · Patrix: FreshLX permission
(§9) · wwa-animals-r: ask the author · ycreatures: no modification or copying · Actions Stuff: none (a re-hosted Marketplace
pack) · TreePhysics: credits only · Definitive VV, Brazz, Kelly's, More Events, natural_weather, NaturalDisasters, Nature's
Touch, Aurora, Naturalist, Better Biomes, Nature Overhaul, Animals and Fauna: none in the archive.
Under §9 any may be used, each asset recorded on RESTRICTED-ASSETS in the same build.

## 7. Recommendations for round 1006 (for his approval; nothing built)
1. Skip HDGMP v1 and v2 (they create sources and fight the pumps); if he wants to see one: a throwaway flat world only.
2. Port UtilityCraft's extractor idea into a BP-02 `pw:` sluice pump / drain grate: reads a liquid_depth 0 block at a set
   position, sets it to air on a slow tick, counts what it drains, stops when a closed basin is empty, logs; BDS probe first.
3. Skip Item Pipe; model our own stone / lead pipe pieces.
4. Port the LOOK: `pw:` mist / splash / cascade particles in RP-02 from PUREVFX / Effective / Particular art, fired from
   emitters placed in cascade and fountain templates; Effective waterfall / river loops; drips for sewers. All on RESTRICTED-ASSETS.
5. If he prefers PUREVFX whole: turn off waterSplash (every-tick entity scan), consider dynamicLights off, check stack order.
6. VV water: raise the RealSource water.json provenance; Ultra Realism / Definitive values show tuning directions; our own
   numbers would avoid the restriction.
7. Fountains: vanilla plains fountain + Village_Generator fountain as layout references; a single source on a pedestal (R8 §2).
8. Risks: phone particle budgets (cap emitters per loaded chunk), particle override order, any add-on writing water or light
   blocks near the pumps, the unverified 2.8.0 / 2.9.0 dependencies.

## 8. ADDENDUM (19:5x CT) — Haubna's Physics Mod (his 19:45 "check that one now")

**The file:** `physics-mod-pro-v188f-fabric-mc-263.jar` (Drive id 1j2CH9oQZj2Mx04cCZXR2YOAmQDvqUqcJ), 93,701,729 B, 2,389 entries. Read over HTTP range requests (the whole jar was never downloaded). `fabric.mod.json`: id `physicsmod`, version **3.2.5**, author **Haubna**, homepage minecraftphysicsmod.com, **licence "All rights reserved"**, needs Fabric Loader ≥ 0.14.14, **Minecraft Java "~26.3"**, Fabric API, **Java ≥ 25**. It is a Java Edition mod: compiled Java classes, GLSL shaders and a native PhysX library. None of it can run on Bedrock (PS5 or phone); Bedrock add-ons have no compute shaders, no custom render code and no client mods.

**How its water works (from the jar's own files):**

| Feature | How it is built (files) | What the menu says (lang/en_us.json, 544 keys) |
|---|---|---|
| **Liquid physics (PRO, BETA)** | GPU *Position-Based Fluids*: 18 compute shaders `shaders/core/liquid_compute/pbf_*.comp` (emit → integrate → count/scatter grid → lambda → delta → apply → finalize → classify for rendering); Java side `net/diebuddies/physics/liquid/compute/*` (LiquidComputeSystem, VoxelWorld, OpenGL + Vulkan back ends) | "Uses your graphics card to simulate realistic liquid movement." Particle size, world particle capacity, viscosity, friction, water density, max particles per source, lifetime. "Place a Minecraft water-source block to create a continuous source and remove it to stop the flow." Shift + right-click with a **stick** makes or removes a source. |
| **Ocean waves** | Two renderers: "Classic Mesh" and **FFT Ocean** — compute shaders `shaders/fft_ocean/{spectrum_init,spectrum_update,fft,normal_foam}.comp`, "a detailed four-cascade surface". The vertex shader `ocean_v3.vsh` moves each water vertex by `physics_fftOffset(position, waviness)`; **`physics_waviness` is a per-vertex value** the mod computes from distance to shore and depth | Wave height, speed, horizontal scale, wind rotation/turbulence, **"Wave distance to shore — how far from the shore the water has to be to form big waves; also takes into account the deepness of the water body"**, weather multiplier (clear / rain / thunder), tessellation near the camera (Iris only). |
| **Ripples** | `ocean_ripple_simulate.fsh`: a **2-D height-field wave equation** in a texture that follows the camera — `next = (2·current − previous)·damping + laplacian·propagation + impulse`, faded at the borders; entities write impulses | "Creates ripples on the water surface around entities." Needs ocean physics. |
| **Foam** | `normal_foam.comp`, `ocean_foam.glsl`, `textures/ocean/foam.png` (animated, .mcmeta) | Foam amount, foam opacity. |
| **Splashes** | particles `splash`, `splash_small`, `splash_explosion` (each 4 frames `splash_0..3`), sound event `splash_sound` = `splash_0/1/2.ogg` | Splashes on/opacity, ocean splash volume. |
| **Rain on water** | `particles/rain.json`, weather particles | "Rain puddle amount — creates puddles when rain particles hit the water"; vanilla rain splash particles on water. |
| **Floating things** | mixins `MixinBoat`, `MixinFluidRenderer`, `MixinLiquidBlockRenderer`, `MixinWaterDropParticle`; menu "Buoyancy X/Y/Z", "Stick to surface" | Physics objects float with set buoyancy and ride the waves. |

**What we can take into Bedrock (ideas, not code — nothing copied):**

1. **Shore-aware waves** (the *waviness* idea). Vibrant Visuals `water.json` waves are one global setting; we cannot vary them per block. But a script can do what the mod's "distance to shore" does for *extras*: only open, deep water (measured by our scanner) gets surf particles, foam particles at the shoreline, and louder splash sounds. Effort M.
2. **Splashes**: when an entity or a felled tree enters water, a script plays our own splash particle + sound at the surface. Bedrock supports this fully (particle JSON + `sound_definitions.json` + `dimension.spawnParticle` / `playSound`). The art must be our own or a pack already on our list (Kelly's / RealSource); the mod's textures and .ogg files are "All rights reserved" — personal use would allow them under §9, but they would go on the RESTRICTED list, and we do not need them. Effort S.
3. **Ripples around walkers**: a flat ring particle (`facing_camera_mode: "emitter_transform_xz"`) spawned under civs and the player while they stand in water. A cheap stand-in for the height-field ripple. Effort S.
4. **Buoyancy**: Bedrock already has an engine feature for this — the entity component **`minecraft:buoyant`** (base buoyancy, gravity, wave simulation, big-wave chance/speed, which liquid blocks count). Felled logs that land in a river could float and drift instead of vanishing. To be measured in the R10 probes. Effort M.
5. **Rain on water**: vanilla Bedrock already makes rain splash particles on water; Vibrant Visuals adds wet-surface shading. Nothing to build.
6. **True liquid simulation** (PBF particles, water pouring over obstacles as a fluid): **not possible on Bedrock.** The nearest thing is what HDGMP's Water Flow add-on does (scripted source movement, §3.1–3.2), which is a different, block-based idea.

**Licence (as the file states):** "All rights reserved." We studied it; we use no file from it. If a future build ever uses one of its sounds or textures, that asset goes on RESTRICTED-ASSETS (pack + file, source = Physics Mod Pro 3.2.5 jar on his Drive, licence "All rights reserved", owner Haubna).

## Appendix A — per-file census (468 rows)
| Packs | [Addon]BetterVills.mcaddon | 0.23 | Bedrock pack/add-on |  |
| Packs | Abs0lutMedievalism-BP-v0_7_5.mcpack | 0.00 | own (pw/AR suite or tooling) |  |
| Packs | Abs0lutMedievalism.mcaddon | 302.23 | own (pw/AR suite or tooling) |  |
| Packs | AbsolutRealism-Atmospherics-SUNFIX-HARD.mcaddon.txt | 122.04 | own (pw/AR suite or tooling) | D56 |
| Packs | AbsolutRealism-Atmospherics-SUNFIX-HARD.mcaddon.txt | 122.04 | own (pw/AR suite or tooling) | D56 |
| Packs | AbsolutRealism-BranchAlign-BP-v0_3.mcpack | 0.00 | own (pw/AR suite or tooling) |  |
| Packs | Actions Stuff 1.10-MODBIBO.zip | 63.49 | Bedrock pack/add-on |  |
| Packs | Alacrity.zip | 50.06 | Java resource pack | D51 |
| Packs | Alacrity.zip | 50.06 | Java resource pack | D51 |
| Packs | AmbientSounds_FABRIC_v6.3.5_mc26.1.2.jar | 84.83 | Java mod |  |
| Packs | AmbientSounds_NEOFORGE_v6.3.5_mc26.1.2.jar | 84.81 | Java mod |  |
| Packs | Animals and Fauna.mcaddon | 36.63 | Bedrock pack/add-on |  |
| Packs | APlus_v1.1.mcpack | 1.05 | Bedrock pack/add-on |  |
| Packs | app-release.apk | 21.32 | own (pw/AR suite or tooling) |  |
| Packs | atmospherica-1.0.0.jar | 0.07 | Java mod |  |
| Packs | atmospherics-2.6-mc-26.1.jar | 1.83 | Java mod |  |
| Packs | Aurora_Cinema_v8.mcaddon | 1.66 | Bedrock pack/add-on |  |
| Packs | bedrock-samples-main.zip | 158.15 | Mojang samples |  |
| Packs | bedrock-server-1.26.14.1 (1).zip | 83.50 | Bedrock Dedicated Server |  |
| Packs | bedrock-server-1.26.14.1.zip | 57.60 | Bedrock Dedicated Server |  |
| Packs | Better Biomes.mcaddon | 7.29 | Bedrock pack/add-on |  |
| Packs | Better Foliage Texture + Addon.mcaddon | 4.94 | Bedrock pack/add-on |  |
| Packs | Better Trees by Daniye - v1.4.3.mcaddon | 0.83 | Bedrock pack/add-on |  |
| Packs | BetterWorld_v7.mcaddon | 0.05 | Bedrock pack/add-on |  |
| Packs | BIGCANOPY-v2_4_1.mcaddon | 0.28 | own (pw/AR suite or tooling) |  |
| Packs | BIGCANOPY-v2_5_0.mcaddon.txt | 0.29 | own (pw/AR suite or tooling) |  |
| Packs | BIGCANOPY-v2_6_1.mcaddon.txt | 0.29 | own (pw/AR suite or tooling) |  |
| Packs | BIGCANOPY-v2_6_2.mcaddon.txt | 0.29 | own (pw/AR suite or tooling) | D22 |
| Packs | BIGCANOPY-v2_6_2.zip | 0.29 | own (pw/AR suite or tooling) | D22 |
| Packs | BIGCANOPY-v2_7_0.mcaddon (1).txt | 0.29 | own (pw/AR suite or tooling) |  |
| Packs | BIGCANOPY-v2_7_0.mcaddon.txt | 0.29 | own (pw/AR suite or tooling) |  |
| Packs | BIGCANOPY-v2_7_1.mcaddon | 0.29 | own (pw/AR suite or tooling) | D23 |
| Packs | BIGCANOPY-v2_7_1.mcaddon.txt | 0.29 | own (pw/AR suite or tooling) | D23 |
| Packs | BIGCANOPY-v2_7_2.mcaddon | 0.29 | own (pw/AR suite or tooling) |  |
| Packs | BIGCANOPY-v2_7_3-1.mcaddon | 0.30 | own (pw/AR suite or tooling) | D24 |
| Packs | BIGCANOPY-v2_7_3.mcaddon.txt | 0.30 | own (pw/AR suite or tooling) | D24 |
| Packs | BIGCANOPY-v2_7_4.mcaddon | 0.30 | own (pw/AR suite or tooling) |  |
| Packs | BIGCANOPY-v2_8_0-debugger.mcaddon | 0.38 | own (pw/AR suite or tooling) |  |
| Packs | BIGCANOPY-v2_8_0-nodebug.mcaddon | 0.38 | own (pw/AR suite or tooling) |  |
| Packs | BIGCANOPY-v2_8_1-debugger.mcaddon | 0.38 | own (pw/AR suite or tooling) | D26 |
| Packs | BIGCANOPY-v2_8_1-debugger.mcaddon.txt | 0.38 | own (pw/AR suite or tooling) | D26 |
| Packs | BIGCANOPY-v2_8_1-nodebug-1.mcaddon.txt | 0.38 | own (pw/AR suite or tooling) | D27 |
| Packs | BIGCANOPY-v2_8_1-nodebug.mcaddon | 0.38 | own (pw/AR suite or tooling) | D27 |
| Packs | BIGCANOPY-v2_8_1-VV_TEST_RUN.mcaddon | 0.37 | own (pw/AR suite or tooling) |  |
| Packs | BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_31.mcpack | 0.02 | own (pw/AR suite or tooling) |  |
| Packs | BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_33.mcpack | 0.02 | own (pw/AR suite or tooling) |  |
| Packs | BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_34.mcpack | 0.02 | own (pw/AR suite or tooling) | D14 |
| Packs | BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_35.mcpack | 0.02 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_143.mcpack | 0.34 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_176.mcpack | 0.50 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_187.mcpack | 0.78 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_82.mcpack | 0.26 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_83.mcpack.txt | 0.26 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_84.mcpack | 0.26 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_85.mcpack | 0.26 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_86.mcpack | 0.27 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_87.mcpack | 0.27 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_88.mcpack | 0.27 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_89.mcpack | 0.27 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_90.mcpack | 0.27 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_92.mcaddon | 108.42 | own (pw/AR suite or tooling) |  |
| Packs | BP-02-AbsolutRealism-Tectonic-BP-v1_3_94.mcaddon | 65.05 | own (pw/AR suite or tooling) |  |
| Packs | BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_30.mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_32.mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_33.mcpack | 0.01 | own (pw/AR suite or tooling) | D9 |
| Packs | BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_34.mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | Brazz_Shader.mcpack | 1.11 | Bedrock pack/add-on |  |
| Packs | bridge_companion_BP-v0_1_3.mcpack | 0.00 | own (pw/AR suite or tooling) |  |
| Packs | bridge_companion_BP-v0_1_5.mcpack | 0.00 | own (pw/AR suite or tooling) |  |
| Packs | bridge_companion_BP-v0_1_6.mcpack | 0.00 | own (pw/AR suite or tooling) | D5 |
| Packs | bridge_companion_BP-v0_1_6.mcpack | 0.00 | own (pw/AR suite or tooling) | D5 |
| Packs | bridge_mcp_v0.2.0.zip | 0.00 | own (pw/AR suite or tooling) |  |
| Packs | bridge_server_starter.js | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | continuity-3.0.1-beta.2+26.1.jar | 1.04 | Java mod |  |
| Packs | Craftopia Furniture WE 2.5 RP.mcpack | 7.40 | Bedrock pack/add-on |  |
| Packs | CreaturesPlus3.4.zip | 2.70 | Java resource pack |  |
| Packs | Definitive Vibrant Visuals - Default.mcpack | 14.53 | Bedrock pack/add-on |  |
| Packs | DistantHorizons-2.4.5-b-1.21.11-fabric-neoforge.jar | 25.62 | Java mod |  |
| Packs | Dramatic Skys Demo 1.5.3.36.3.zip | 13.91 | Java resource pack |  |
| Packs | dynamic-trees.mcaddon | 0.66 | Bedrock pack/add-on |  |
| Packs | Dynamic_Flowing_Water.mcaddon | 0.01 | Bedrock pack/add-on |  |
| Packs | efallingtrees-0.6.0-1.20+fabric.jar | 1.71 | Java mod |  |
| Packs | Effective 2.3.2-1.20.1-EXTRACT_ME (1).zip | 37.62 | zip (other) |  |
| Packs | Effective 2.3.2-1.20.1-EXTRACT_ME.zip | 54.05 | zip (other) |  |
| Packs | Epic Terrain 0.1.4+mod-EXTRACT_ME.zip | 0.48 | zip (other) |  |
| Packs | EpicTerrain.mcpack.zip | 0.14 | Bedrock pack/add-on |  |
| Packs | extracted_frames2.zip | 61.52 | zip (other) |  |
| Packs | Faithful 32x - 1.21.11.zip | 9.97 | Java resource pack |  |
| Packs | Faithful 64x - Release 11.mcpack | 24.86 | Bedrock pack/add-on |  |
| Packs | Faithful 64x - Release 13.mcpack | 34.51 | Bedrock pack/add-on |  |
| Packs | FaithfulPBR_128_1.1p.zip | 8.78 | Java resource pack |  |
| Packs | FallingTree-26.1.2-25.jar | 0.49 | own (pw/AR suite or tooling) |  |
| Packs | FallingTree.mcaddon.txt | 0.04 | own (pw/AR suite or tooling) | D16 |
| Packs | FallingTree_BP-1.mcpack.txt | 0.01 | own (pw/AR suite or tooling) | D10 |
| Packs | FallingTree_BP.mcpack.txt | 0.01 | own (pw/AR suite or tooling) | D10 |
| Packs | FallingTree_RP.mcpack.txt | 0.03 | own (pw/AR suite or tooling) | D15 |
| Packs | FallingTree_v2.mcaddon.txt | 0.04 | own (pw/AR suite or tooling) | D17 |
| Packs | FallingTree_v2_1.mcaddon.txt | 0.04 | own (pw/AR suite or tooling) | D18 |
| Packs | Feudal Furniture WE 8.7 RP.mcpack | 5.62 | Bedrock pack/add-on |  |
| Packs | flowing_fluids_1.21.9-forge-1.0.5.jar | 0.35 | Java mod |  |
| Packs | fluidphysics-1.6.0+forge-1.16.4.jar | 5.41 | Java mod |  |
| Packs | Fresh_Animations_v1.10.6.mcpack.zip | 0.55 | Bedrock pack/add-on |  |
| Packs | fresh_moves_bedrock_v1_2_7.mcpack.zip | 0.15 | Bedrock pack/add-on |  |
| Packs | FreshAnimations_v1.10.5.zip | 0.65 | Java resource pack |  |
| Packs | GameplayFriendlyTextures_128x_v12.zip | 25.75 | Java resource pack |  |
| Packs | glowing-ores-v1.0.1.mcaddon | 0.13 | Bedrock pack/add-on |  |
| Packs | GlowingOres-RealisticRTXpack4.7_LOW.zip | 0.61 | Bedrock pack/add-on |  |
| Packs | GuardVillager9.mcaddon | 0.27 | Bedrock pack/add-on |  |
| Packs | Horizon_Natural_v0_0_5.mcaddon | 1.25 | Bedrock pack/add-on |  |
| Packs | Hyper_Realistic_Sky_[v3.8].zip | 267.25 | Java resource pack |  |
| Packs | Illuminations-main.zip | 32.91 | Java mod |  |
| Packs | Immersive Fauna Savanna Update 1_5_0.mcaddon | 3.76 | Bedrock pack/add-on |  |
| Packs | Item Pipe V2.1.3.mcaddon | 0.11 | Bedrock pack/add-on |  |
| Packs | item-physics-v2_9-beharviors-packs.mcpack | 0.06 | Bedrock pack/add-on |  |
| Packs | item-physics-v2_9-resources-packs.mcpack | 0.06 | Bedrock pack/add-on |  |
| Packs | items-physics-v1_1.mcaddon | 0.24 | Bedrock pack/add-on |  |
| Packs | jurassic-project-kingdom-of-the-giants.mcaddon | 2.71 | Bedrock pack/add-on |  |
| Packs | Kellys_RTX_Base_pack_3.6_Size_fix.mcpack | 11.20 | Bedrock pack/add-on |  |
| Packs | kingdom_constructor_IronAge_MConverter.eu.mcaddon | 0.48 | Bedrock pack/add-on |  |
| Packs | KingdomConstructor_IronAge_1.1.2_MConverter.eu.mcaddon | 0.56 | Bedrock pack/add-on |  |
| Packs | LOW_RealisticJAVApack_3.4.zip | 37.46 | Java resource pack |  |
| Packs | Medievalism v7 x2048 (1.21).zip | 1,376.85 | Java resource pack |  |
| Packs | More Events Remastered v1.1.1.mcaddon | 0.39 | Bedrock pack/add-on |  |
| Packs | More Flowers Mini Pack v1.0.mcaddon | 0.13 | Bedrock pack/add-on |  |
| Packs | Natural Firefly Bushes 1.0.zip | 0.02 | Java resource pack |  |
| Packs | natural_weather_1.0.4.mcaddon | 6.28 | Bedrock pack/add-on | D41 |
| Packs | natural_weather_1.0.4.mcaddon | 6.28 | Bedrock pack/add-on | D41 |
| Packs | NaturalDisasters-Bedrock-0.48.0.mcaddon | 0.42 | Bedrock pack/add-on |  |
| Packs | naturalist-26-1.mcaddon | 22.17 | Bedrock pack/add-on |  |
| Packs | Nature Overhaul.mcaddon | 4.15 | Bedrock pack/add-on |  |
| Packs | Nature's_Touch_v2.6_Hotfix_3.mcaddon | 2.63 | Bedrock pack/add-on |  |
| Packs | Ne Cherry Update.mcaddon | 10.66 | Bedrock pack/add-on |  |
| Packs | newb-classic-16.54-merged.mcpack | 6.97 | Bedrock pack/add-on |  |
| Packs | Optimum Realism R4.0.0 64x RTX.mcpack | 30.08 | Bedrock pack/add-on |  |
| Packs | Optimum Realism R4.0.0 64x.mcpack | 77.94 | Java resource pack |  |
| Packs | owo-lib-0.11.2+1.20.jar | 0.91 | Java mod |  |
| Packs | PALM TREES_1773594172510.mcaddon | 0.10 | Bedrock pack/add-on |  |
| Packs | Particular ✨ 1.1.1-EXTRACT_ME.zip | 3.37 | zip (other) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_1_0.mcpack | 1.02 | own (pw/AR suite or tooling) | D34 |
| Packs | PATRIX-WORLD-SAMPLE-v0_1_0.mcpack | 1.02 | own (pw/AR suite or tooling) | D34 |
| Packs | PATRIX-WORLD-SAMPLE-v0_1_1.mcpack.txt | 1.09 | own (pw/AR suite or tooling) | D35 |
| Packs | PATRIX-WORLD-SAMPLE-v0_1_3.mcpack.txt | 1.17 | own (pw/AR suite or tooling) | D36 |
| Packs | PATRIX-WORLD-SAMPLE-v0_1_4.mcpack.txt | 1.19 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_1_5.mcpack.txt | 1.22 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_1_6.mcpack.txt | 1.21 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_1_7.mcpack.txt | 1.24 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_1_8.zip | 1.29 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_1.mcpack.txt | 3.43 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_10-1.mcpack | 11.84 | own (pw/AR suite or tooling) | D43 |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_10.mcpack | 11.84 | own (pw/AR suite or tooling) | D43 |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_11.mcpack | 11.82 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_2.mcpack.txt | 3.43 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_3.mcpack.txt | 1.98 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_4.mcpack.txt | 3.84 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_5 (2).mcpack | 5.84 | own (pw/AR suite or tooling) | D40 |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_5.mcpack | 5.84 | own (pw/AR suite or tooling) | D40 |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_5.mcpack.txt | 5.84 | own (pw/AR suite or tooling) | D40 |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_6.mcpack.txt | 6.35 | own (pw/AR suite or tooling) | D42 |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_7.mcpack.txt | 6.35 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_8.mcpack | 7.10 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_2_9.mcpack | 11.84 | own (pw/AR suite or tooling) |  |
| Packs | PATRIX-WORLD-SAMPLE-v0_3_0-VV_TEST_RUN.mcpack | 11.99 | own (pw/AR suite or tooling) |  |
| Packs | Patrix_1.21.11_128x_addon.zip | 105.80 | Java resource pack | D55 |
| Packs | Patrix_1.21.11_128x_addon.zip | 105.80 | Java resource pack | D55 |
| Packs | Patrix_1.21.11_128x_basic.zip | 487.35 | Java resource pack | D58 |
| Packs | Patrix_1.21.11_128x_basic.zip | 487.35 | Java resource pack | D58 |
| Packs | Patrix_1.21.11_128x_bonus.zip | 30.78 | Java resource pack |  |
| Packs | Patrix_1.21.11_128x_items.zip | 26.42 | Java resource pack |  |
| Packs | Patrix_1.21.11_128x_mobs (2).zip | 125.71 | Java resource pack | D57 |
| Packs | Patrix_1.21.11_128x_mobs.zip | 125.71 | Java resource pack | D57 |
| Packs | Patrix_1.21.11_128x_mobs.zip | 125.71 | Java resource pack | D57 |
| Packs | Patrix_1.21.11_64x_addon.zip | 42.29 | Java resource pack |  |
| Packs | Patrix_1.21.11_64x_basic.zip | 198.05 | Java resource pack |  |
| Packs | Patrix_1.21.11_64x_bonus.zip | 9.75 | Java resource pack |  |
| Packs | Patrix_1.21.11_models.zip | 0.06 | Java resource pack | D20 |
| Packs | Patrix_1.21.11_models.zip | 0.06 | Java resource pack | D20 |
| Packs | Patrix_26.1_256x_addon.zip | 373.10 | Java resource pack |  |
| Packs | Patrix_26.1_256x_basic.zip | 1,701.31 | Java resource pack |  |
| Packs | Patrix_26.2_128x_addon.zip | 106.85 | Java resource pack |  |
| Packs | Patrix_26.2_128x_basic.zip | 490.61 | Java resource pack |  |
| Packs | Patrix_26.2_128x_bonus.zip | 30.56 | Java resource pack |  |
| Packs | Patrix_26.2_128x_items.zip | 28.62 | Java resource pack |  |
| Packs | Patrix_26.2_128x_mobs.zip | 150.13 | Java resource pack |  |
| Packs | Patrix_26.2_256x_addon.zip | 376.73 | Java resource pack |  |
| Packs | Patrix_26.2_256x_basic.zip | 1,709.82 | Java resource pack |  |
| Packs | Patrix_26.2_256x_bonus.zip | 111.41 | Java resource pack |  |
| Packs | Patrix_26.2_256x_items.zip | 94.56 | Java resource pack |  |
| Packs | Patrix_26.2_256x_mobs.zip | 516.87 | Java resource pack |  |
| Packs | PatrixCanopyGen-v0_1_0.mcaddon.txt | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixCanopyGen-v0_1_1-1.mcaddon.txt | 0.01 | own (pw/AR suite or tooling) | D12 |
| Packs | PatrixCanopyGen-v0_1_1.mcaddon | 0.01 | own (pw/AR suite or tooling) | D12 |
| Packs | PatrixCanopyGen-v0_1_1.mcaddon (1).txt | 0.01 | own (pw/AR suite or tooling) | D12 |
| Packs | PatrixCanopyGen-v0_1_1.mcaddon.txt | 0.01 | own (pw/AR suite or tooling) | D12 |
| Packs | PatrixCanopyGen-v0_1_2 (2).mcaddon | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixCanopyGen-v0_1_2-VV_TEST_RUN.mcaddon | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixCanopyGen-v0_1_2.mcaddon | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld-Tectonic-v0_1_0.mcaddon.txt | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld-Tectonic-v0_2_0.mcaddon | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld-Tectonic-v0_3_0.mcaddon.txt | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld-Tectonic-v0_4_0.mcaddon | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld-Tectonic-v0_5_0.mcaddon | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld-Tectonic-v0_6_0.mcaddon | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld-Tectonic-v0_6_1-1.mcaddon.txt | 0.01 | own (pw/AR suite or tooling) | D8 |
| Packs | PatrixWorld-Tectonic-v0_6_1.mcaddon | 0.01 | own (pw/AR suite or tooling) | D8 |
| Packs | PatrixWorld-Tectonic-v0_7_1-VV_TEST_RUN.mcaddon.txt | 0.11 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld-Tectonic-v0_7_2-VV_TEST_RUN.mcaddon | 0.11 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld_Handoff_v2.md | 0.03 | own (pw/AR suite or tooling) |  |
| Packs | PatrixWorld_Handoff_v3.md | 0.03 | own (pw/AR suite or tooling) |  |
| Packs | physics-mod-pro-v183i-fabric-mc-1.21.11.jar.zip | 139.14 | Java mod |  |
| Packs | physics-mod-pro-v183i-fabric-mc-26.1.x.jar.zip | 139.13 | Java mod |  |
| Packs | physics-mod-pro-v183i-forge-mc-1.21.11.jar.zip | 139.10 | Java mod |  |
| Packs | physics-mod-pro-v183i-forge-mc-26.1.x.jar.zip | 138.64 | Java mod |  |
| Packs | physics-mod-pro-v183i-neoforge-mc-26.1.x.jar.zip | 139.08 | Java mod |  |
| Packs | physics-mod-pro-v188f-fabric-mc-263.jar | 93.70 | Java mod |  |
| Packs | Physics_water.mcaddon | 0.01 | Bedrock pack/add-on |  |
| Packs | pokemon-expansion.mcaddon | 0.10 | Bedrock pack/add-on |  |
| Packs | Prominence™ II Hasturian Era  v4.1.1.mcpack | 396.79 | Java resource pack |  |
| Packs | PUREVFX_v0_1_0.mcaddon | 23.81 | Bedrock pack/add-on |  |
| Packs | PW-Civitas-Markers-BP-v0_2_1.mcpack | 0.05 | own (pw/AR suite or tooling) |  |
| Packs | PW-Civitas-Markers-RP-v0_2_1.mcpack | 0.11 | own (pw/AR suite or tooling) |  |
| Packs | PW-Experience-COMPLETE-v3_0_0.mcpack | 7.99 | own (pw/AR suite or tooling) |  |
| Packs | PW-LeafProbe-BP-v0_4_0.mcpack | 0.00 | own (pw/AR suite or tooling) |  |
| Packs | PW-LeafProbe-BP-v0_4_1.mcpack | 0.00 | own (pw/AR suite or tooling) | D6 |
| Packs | PW-LeafProbe-BP-v0_4_1.mcpack | 0.00 | own (pw/AR suite or tooling) | D6 |
| Packs | PW-LeafProbe-RP-v0_3_0.mcpack | 0.57 | own (pw/AR suite or tooling) |  |
| Packs | PW-LeafProbe-RP-v0_3_1.mcpack | 0.57 | own (pw/AR suite or tooling) | D29 |
| Packs | PW-LeafProbe-RP-v0_3_1.mcpack | 0.57 | own (pw/AR suite or tooling) | D29 |
| Packs | PW-MOBFIX-Overlay-RP-v0_1_0.mcpack | 12.47 | own (pw/AR suite or tooling) |  |
| Packs | PW-MOBFIX-Overlay-RP-v0_2_0.mcpack | 11.73 | own (pw/AR suite or tooling) |  |
| Packs | PW-MOBFIX-Overlay-RP-v0_3_0.mcpack | 12.04 | own (pw/AR suite or tooling) |  |
| Packs | PW-MOBFIX-Overlay-RP-v0_5_0.mcpack | 12.04 | own (pw/AR suite or tooling) |  |
| Packs | PW-PROBE-MOSS-A-v0_0_1.mcpack.txt | 0.06 | own (pw/AR suite or tooling) |  |
| Packs | PW-SlabForge-Key-BP-v0_1_0.mcpack | 0.00 | own (pw/AR suite or tooling) | D2 |
| Packs | PW-SlabForge-Key-BP-v0_1_0.mcpack | 0.00 | own (pw/AR suite or tooling) | D2 |
| Packs | PW-StreetKit-BP-v0_1_4.mcpack | 0.01 | own (pw/AR suite or tooling) | D11 |
| Packs | PW-StreetKit-BP-v0_1_4.mcpack | 0.01 | own (pw/AR suite or tooling) | D11 |
| Packs | PW-StripMine-BP-v1_0_0.mcpack | 0.95 | own (pw/AR suite or tooling) |  |
| Packs | PW-StripMine-BP-v1_3_0.mcpack | 0.95 | own (pw/AR suite or tooling) |  |
| Packs | PW-StripMine-BP-v1_3_1.mcpack | 0.95 | own (pw/AR suite or tooling) | D33 |
| Packs | PW-StripMine-BP-v1_3_1.mcpack | 0.95 | own (pw/AR suite or tooling) | D33 |
| Packs | PW-StripMine-RP-v2_4_0.mcpack | 36.69 | own (pw/AR suite or tooling) |  |
| Packs | PW-StripMine-RP-v2_8_0.mcpack | 36.82 | own (pw/AR suite or tooling) |  |
| Packs | PW-StripMine-RP-v2_9_0.mcpack.txt | 36.82 | own (pw/AR suite or tooling) |  |
| Packs | PW-StripMine-RP-v3_0_0.mcpack | 27.67 | own (pw/AR suite or tooling) |  |
| Packs | PW-StripMine-RP-v3_0_1.mcpack | 27.67 | own (pw/AR suite or tooling) | D47 |
| Packs | PW-StripMine-RP-v3_0_1.mcpack | 27.67 | own (pw/AR suite or tooling) | D47 |
| Packs | PW-TestRunner-BP-v0_1_0.mcpack | 0.02 | own (pw/AR suite or tooling) |  |
| Packs | PW-WitnessRig-BP-v0_1_0.mcpack | 0.00 | own (pw/AR suite or tooling) | D4 |
| Packs | PW-WitnessRig-BP-v0_1_0.mcpack | 0.00 | own (pw/AR suite or tooling) | D4 |
| Packs | RealSource_RealisticVisuals_1.9.1_LOW.mcpack | 39.47 | Bedrock pack/add-on |  |
| Packs | RealSource_VibrantVisuals_PLUS_2.0.zip | 6.34 | Bedrock pack/add-on |  |
| Packs | RenderingStuff_2019_UNZIP-PLEASE_512x_d.zip | 128.06 | zip (other) |  |
| Packs | RP-01-AbsolutRealism-Tectonic-RP-v1_3_102.mcpack | 40.23 | own (pw/AR suite or tooling) | D49 |
| Packs | RP-01-AbsolutRealism-Tectonic-RP-v1_3_104.mcpack | 32.11 | own (pw/AR suite or tooling) |  |
| Packs | RP-01-AbsolutRealism-Tectonic-RP-v1_3_79.mcpack | 64.98 | own (pw/AR suite or tooling) |  |
| Packs | RP-01-AbsolutRealism-Tectonic-RP-v1_3_80.mcpack.txt | 64.98 | own (pw/AR suite or tooling) |  |
| Packs | RP-01-AbsolutRealism-Tectonic-RP-v1_3_81.mcpack.txt | 64.98 | own (pw/AR suite or tooling) |  |
| Packs | RP-01-AbsolutRealism-Tectonic-RP-v1_3_83.mcpack | 64.98 | own (pw/AR suite or tooling) |  |
| Packs | RP-01-AbsolutRealism-Tectonic-RP-v1_3_84.mcpack | 64.98 | own (pw/AR suite or tooling) |  |
| Packs | RP-01-AbsolutRealism-Tectonic-RP-v1_3_99.mcpack | 65.06 | own (pw/AR suite or tooling) |  |
| Packs | RP-02-AbsolutRealism-Atmospheric-Effects-RP-v1_3_38.mcpack | 116.64 | own (pw/AR suite or tooling) |  |
| Packs | RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_0.mcpack | 92.55 | own (pw/AR suite or tooling) |  |
| Packs | RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_1.mcpack | 92.55 | own (pw/AR suite or tooling) | D53 |
| Packs | RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_4.mcpack | 92.58 | own (pw/AR suite or tooling) |  |
| Packs | RP-03-AbsolutRealism-PBR-RP-v1_3_53.mcpack | 105.18 | own (pw/AR suite or tooling) |  |
| Packs | RP-03-AbsolutRealism-PBR-RP-v1_3_54.mcpack | 112.65 | own (pw/AR suite or tooling) |  |
| Packs | RP-03-AbsolutRealism-PBR-RP-v1_3_56.mcpack | 105.24 | own (pw/AR suite or tooling) | D54 |
| Packs | RP-03-AbsolutRealism-PBR-RP-v1_3_60.mcpack | 109.76 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_121.mcpack | 131.74 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_138.mcpack | 126.35 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_61.mcpack | 170.00 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_62.mcpack | 169.98 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_63.mcpack | 173.38 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_64.mcpack | 172.31 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_65.mcpack | 172.33 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_66.mcpack | 172.33 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_67.mcpack | 172.34 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_68.mcpack | 172.34 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_69.mcpack | 172.35 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_70.mcpack | 172.35 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_71.mcpack | 172.35 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_82.mcpack | 179.79 | own (pw/AR suite or tooling) |  |
| Packs | RP-04-AbsolutRealism-Basic-RP-v1_3_89.mcpack | 179.33 | own (pw/AR suite or tooling) |  |
| Packs | RP-05-AbsolutRealism-Flora-RP-v1_3_38.mcpack | 17.47 | own (pw/AR suite or tooling) |  |
| Packs | RP-05-AbsolutRealism-Flora-RP-v1_3_42.mcpack | 17.47 | own (pw/AR suite or tooling) |  |
| Packs | RP-05-AbsolutRealism-Flora-RP-v1_3_46.mcpack | 13.05 | own (pw/AR suite or tooling) | D44 |
| Packs | RP-05-AbsolutRealism-Flora-RP-v1_3_49.mcpack | 12.51 | own (pw/AR suite or tooling) |  |
| Packs | RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_3_44.mcpack | 29.55 | own (pw/AR suite or tooling) |  |
| Packs | RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_3.mcpack | 42.16 | own (pw/AR suite or tooling) |  |
| Packs | RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_6.mcpack | 39.35 | own (pw/AR suite or tooling) | D48 |
| Packs | RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_6.mcpack | 39.35 | own (pw/AR suite or tooling) | D48 |
| Packs | RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_3_47.mcpack | 43.58 | own (pw/AR suite or tooling) |  |
| Packs | RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_3_48.mcpack | 43.58 | own (pw/AR suite or tooling) |  |
| Packs | RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_3_65.mcpack | 43.41 | own (pw/AR suite or tooling) | D50 |
| Packs | RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_3_65.mcpack.txt | 43.41 | own (pw/AR suite or tooling) | D50 |
| Packs | RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_3_66.mcpack | 43.41 | own (pw/AR suite or tooling) |  |
| Packs | RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_11.mcpack | 57.96 | own (pw/AR suite or tooling) |  |
| Packs | RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_5.mcpack | 55.99 | own (pw/AR suite or tooling) |  |
| Packs | RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_8.mcpack | 55.99 | own (pw/AR suite or tooling) |  |
| Packs | RP-08-AbsolutRealism-Items-RP-v1_3_74.mcpack | 63.86 | own (pw/AR suite or tooling) |  |
| Packs | RP-08-AbsolutRealism-Items-RP-v1_4_3.mcpack | 76.44 | own (pw/AR suite or tooling) |  |
| Packs | RP-08-AbsolutRealism-Items-RP-v1_4_6.mcpack | 73.59 | own (pw/AR suite or tooling) | D52 |
| Packs | RP-08-AbsolutRealism-Items-RP-v1_4_6.mcpack | 73.59 | own (pw/AR suite or tooling) | D52 |
| Packs | RP-10-AbsolutRealism-Terrain-RP-v1_3_33.mcpack | 26.43 | own (pw/AR suite or tooling) | D46 |
| Packs | RP-10-AbsolutRealism-Terrain-RP-v1_3_33.mcpack | 26.43 | own (pw/AR suite or tooling) | D46 |
| Packs | RP-10-AbsolutRealism-Terrain-RP-v1_3_39.mcpack | 16.33 | own (pw/AR suite or tooling) | D45 |
| Packs | RP-10-AbsolutRealism-Terrain-RP-v1_3_40.mcpack | 16.33 | own (pw/AR suite or tooling) |  |
| Packs | RP-11-AbsolutRealism-Ores-RP-v1_3_34.mcpack | 4.83 | own (pw/AR suite or tooling) | D38 |
| Packs | RP-11-AbsolutRealism-Ores-RP-v1_3_34.mcpack | 4.83 | own (pw/AR suite or tooling) | D38 |
| Packs | RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack | 4.83 | own (pw/AR suite or tooling) | D39 |
| Packs | RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack | 4.83 | own (pw/AR suite or tooling) | D39 |
| Packs | RP-99-AbsolutRealism-Diagnostic-RP-v1_3_38.mcpack | 0.05 | own (pw/AR suite or tooling) |  |
| Packs | Rustic Furnture.mcaddon | 3.78 | Bedrock pack/add-on |  |
| Packs | saved_file.txt | 0.01 | own (pw/AR suite or tooling) |  |
| Packs | SMARTFALL-v2_4_0.mcaddon | 0.28 | own (pw/AR suite or tooling) |  |
| Packs | Stratum 256x.zip | 276.08 | Java resource pack |  |
| Packs | Stratum Fast Leaves.zip | 0.22 | Java resource pack |  |
| Packs | sun_diagnostic.tar.gz | 0.03 | own (pw/AR suite or tooling) |  |
| Packs | tectonic-3.0.22-neoforge-26.1 (1).jar | 0.34 | Java mod | D25 |
| Packs | tectonic-3.0.22-neoforge-26.1.jar | 0.34 | Java mod | D25 |
| Packs | tectonic_main.js | 0.17 | own (pw/AR suite or tooling) |  |
| Packs | terrain-slabs-mod-1.20.1.zip | 0.35 | Java mod |  |
| Packs | Terrain_reworks.mcaddon | 0.42 | Bedrock pack/add-on |  |
| Packs | TerraSphere v_1.2.mcpack | 1.44 | Bedrock pack/add-on |  |
| Packs | timber-physics-1.21.5-3 (1).jar | 1.68 | Java mod | D37 |
| Packs | timber-physics-1.21.5-3.jar | 1.68 | Java mod | D37 |
| Packs | timber-physics-plus-1.21.11-1.1.0.jar | 0.03 | Java mod |  |
| Packs | timber-tales.mcaddon | 0.55 | Bedrock pack/add-on |  |
| Packs | timber_tales.mcaddon | 0.56 | Bedrock pack/add-on |  |
| Packs | TreePhysics (1).mcaddon | 0.83 | Bedrock pack/add-on | D31 |
| Packs | TreePhysics.mcaddon | 0.83 | Bedrock pack/add-on | D31 |
| Packs | Ultra Realism.mcpack | 5.81 | Bedrock pack/add-on |  |
| Packs | Umsoea Funky Models v27_256x.zip | 8.76 | Java resource pack |  |
| Packs | Unified-Abs0lut-Claude-v0_12_0-B.txt.adding | 0.00 | own (pw/AR suite or tooling) |  |
| Packs | UtilityCraft_v3.5.4.mcaddon | 4.95 | Bedrock pack/add-on |  |
| Packs | VFXCore v1.8.1.mcaddon | 4.19 | Bedrock pack/add-on |  |
| Packs | Village Animations 1.3.2.mcpack | 0.89 | Bedrock pack/add-on | D32 |
| Packs | Village-Animations-Texture-Pack-26.0.mcpack | 0.89 | Bedrock pack/add-on | D32 |
| Packs | Village_Generator_2.4.0.mcaddon | 1.04 | Bedrock pack/add-on |  |
| Packs | Villager  Illager Lite V1.17.4.mcaddon | 6.36 | Bedrock pack/add-on |  |
| Packs | Villagers_Can_Build_Villages_1.0.mcaddon | 0.21 | Bedrock pack/add-on |  |
| Packs | Villages-Plus-v-0-7.mcaddon | 3.20 | Bedrock pack/add-on |  |
| Packs | wildlife-sanctuary-mobs-plus.mcaddon | 4.95 | Bedrock pack/add-on |  |
| Packs | World Animals Add-on.mcaddon | 5.98 | Bedrock pack/add-on |  |
| Packs | world-generations-by-blockcraftaddons.mcpack | 0.38 | Bedrock pack/add-on | D28 |
| Packs | world-generations-by-blockcraftaddons.mcpack | 0.38 | Bedrock pack/add-on | D28 |
| Packs | worldwildabeh.mcpack | 0.22 | Bedrock pack/add-on |  |
| Packs | worldy-library-1_0_1.mcaddon | 0.51 | Bedrock pack/add-on |  |
| Packs | wpo-1.16.5-0.3.0.jar | 0.19 | Java mod |  |
| Packs | wwa-animals-b (1).mcpack | 0.24 | Bedrock pack/add-on | D21 |
| Packs | wwa-animals-b.mcpack | 0.24 | Bedrock pack/add-on | D21 |
| Packs | wwa-animals-r.mcpack | 26.13 | Bedrock pack/add-on |  |
| Packs | xaeroworldmap-fabric-26.1.2-1.40.16.jar | 1.44 | Java mod |  |
| Packs | ycreatures-savanna-v1_0_5.mcaddon | 10.46 | Bedrock pack/add-on |  |
| Packs | ycreaturestrial-bp-v2_0_4.mcpack | 0.53 | Bedrock pack/add-on |  |
| Packs | ycreaturestrial-rp-v2_0_4.mcpack | 3.93 | Bedrock pack/add-on |  |
| Mine | BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_34.mcpack | 0.02 | own (pw/AR suite or tooling) | D14 |
| Mine | BP-02-AbsolutRealism-Tectonic-BP-v1_3_177.mcpack | 0.50 | own (pw/AR suite or tooling) |  |
| Mine | BP-02-AbsolutRealism-Tectonic-BP-v1_3_178.mcpack | 0.74 | own (pw/AR suite or tooling) | D30 |
| Mine | BP-02-AbsolutRealism-Tectonic-BP-v1_3_178.mcpack (1).zip | 0.74 | own (pw/AR suite or tooling) | D30 |
| Mine | BP-02-AbsolutRealism-Tectonic-BP-v1_3_178.mcpack (2).zip | 0.74 | own (pw/AR suite or tooling) | D30 |
| Mine | BP-02-AbsolutRealism-Tectonic-BP-v1_3_178.mcpack (3).zip | 0.74 | own (pw/AR suite or tooling) | D30 |
| Mine | BP-02-AbsolutRealism-Tectonic-BP-v1_3_178.mcpack (4).zip | 0.74 | own (pw/AR suite or tooling) | D30 |
| Mine | BP-02-AbsolutRealism-Tectonic-BP-v1_3_178.mcpack (5).zip | 0.74 | own (pw/AR suite or tooling) | D30 |
| Mine | BP-02-AbsolutRealism-Tectonic-BP-v1_3_178.mcpack.zip | 0.74 | own (pw/AR suite or tooling) | D30 |
| Mine | BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_33.mcpack | 0.01 | own (pw/AR suite or tooling) | D9 |
| Mine | bridge_companion_BP-v0_1_6.mcpack | 0.00 | own (pw/AR suite or tooling) | D5 |
| Mine | PW-Civitas-Markers-BP-v0_1_7.mcpack | 0.03 | own (pw/AR suite or tooling) |  |
| Mine | PW-Civitas-Markers-RP-v0_1_7.mcpack | 0.08 | own (pw/AR suite or tooling) |  |
| Mine | PW-HOTFIX-RP-oak-skins-roof-fill-v0_2_0.mcpack.zip | 0.10 | own (pw/AR suite or tooling) |  |
| Mine | PW-LeafProbe-BP-v0_4_1.mcpack | 0.00 | own (pw/AR suite or tooling) | D6 |
| Mine | PW-LeafProbe-RP-v0_3_1.mcpack | 0.57 | own (pw/AR suite or tooling) | D29 |
| Mine | PW-SlabForge-Key-BP-v0_1_0.mcpack | 0.00 | own (pw/AR suite or tooling) | D2 |
| Mine | PW-StreetKit-BP-v0_1_4.mcpack | 0.01 | own (pw/AR suite or tooling) | D11 |
| Mine | PW-StripMine-BP-v1_3_1.mcpack | 0.95 | own (pw/AR suite or tooling) | D33 |
| Mine | PW-StripMine-RP-v3_0_1.mcpack | 27.67 | own (pw/AR suite or tooling) | D47 |
| Mine | PW-WitnessRig-BP-v0_1_0.mcpack | 0.00 | own (pw/AR suite or tooling) | D4 |
| Mine | RP-01-AbsolutRealism-Tectonic-RP-v1_3_102.mcpack | 40.23 | own (pw/AR suite or tooling) | D49 |
| Mine | RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_1.mcpack | 92.55 | own (pw/AR suite or tooling) | D53 |
| Mine | RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_2.mcpack.zip | 92.56 | own (pw/AR suite or tooling) |  |
| Mine | RP-03-AbsolutRealism-PBR-RP-v1_3_56.mcpack | 105.24 | own (pw/AR suite or tooling) | D54 |
| Mine | RP-04-AbsolutRealism-Basic-RP-v1_3_127.mcpack | 131.83 | own (pw/AR suite or tooling) |  |
| Mine | RP-04-AbsolutRealism-Basic-RP-v1_3_128.mcpack.zip | 131.96 | own (pw/AR suite or tooling) |  |
| Mine | RP-05-AbsolutRealism-Flora-RP-v1_3_46.mcpack | 13.05 | own (pw/AR suite or tooling) | D44 |
| Mine | RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_6.mcpack | 39.35 | own (pw/AR suite or tooling) | D48 |
| Mine | RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_9.mcpack | 55.99 | own (pw/AR suite or tooling) |  |
| Mine | RP-08-AbsolutRealism-Items-RP-v1_4_6.mcpack | 73.59 | own (pw/AR suite or tooling) | D52 |
| Mine | RP-10-AbsolutRealism-Terrain-RP-v1_3_39.mcpack | 16.33 | own (pw/AR suite or tooling) | D45 |
| Mine | RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack | 4.83 | own (pw/AR suite or tooling) | D39 |
| OldPacks | -1 (28).zip | 1.17 | own (pw/AR suite or tooling) | D36 |
| OldPacks | -1 (29).zip | 1.09 | own (pw/AR suite or tooling) | D35 |
| OldPacks | -1 (30).zip | 0.04 | own (pw/AR suite or tooling) | D18 |
| OldPacks | -1 (31).zip | 0.04 | own (pw/AR suite or tooling) | D17 |
| OldPacks | -1 (32).zip | 0.03 | own (pw/AR suite or tooling) | D15 |
| OldPacks | -1 (33).zip | 0.01 | own (pw/AR suite or tooling) | D10 |
| OldPacks | -1 (34).zip | 0.01 | own (pw/AR suite or tooling) | D10 |
| OldPacks | -1 (35).zip | 0.04 | own (pw/AR suite or tooling) | D16 |
| OldPacks | -1 (6).zip | 6.35 | own (pw/AR suite or tooling) | D42 |
| OldPacks | AI-CONTINUITY-HANDOFF-v0_6_5.md | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | bigcanopy_bp (2).mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | bigcanopy_bp.mcpack | 0.02 | own (pw/AR suite or tooling) |  |
| OldPacks | bigcanopy_rp (2).mcpack | 0.28 | own (pw/AR suite or tooling) |  |
| OldPacks | bigcanopy_rp.mcpack | 0.28 | own (pw/AR suite or tooling) |  |
| OldPacks | blocks (10).json | 0.00 | own (pw/AR suite or tooling) | D3 |
| OldPacks | blocks (11).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | blocks (2).json | 0.01 | own (pw/AR suite or tooling) | D7 |
| OldPacks | blocks (3).json | 0.01 | own (pw/AR suite or tooling) | D7 |
| OldPacks | blocks (4).json | 0.01 | own (pw/AR suite or tooling) | D7 |
| OldPacks | blocks (5).json | 0.01 | own (pw/AR suite or tooling) | D7 |
| OldPacks | blocks (6).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | blocks (7).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | blocks (8).json | 0.00 | own (pw/AR suite or tooling) | D3 |
| OldPacks | blocks (9).json | 0.00 | own (pw/AR suite or tooling) | D3 |
| OldPacks | blocks.json | 0.01 | own (pw/AR suite or tooling) | D7 |
| OldPacks | BP (10).mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | BP (11).mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | BP (12).mcpack | 0.01 | own (pw/AR suite or tooling) | D10 |
| OldPacks | BP (2).mcpack | 0.01 | own (pw/AR suite or tooling) | D13 |
| OldPacks | BP (3).mcpack | 0.01 | own (pw/AR suite or tooling) | D13 |
| OldPacks | BP (4).mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | BP (5).mcpack | 0.01 | own (pw/AR suite or tooling) | D13 |
| OldPacks | BP (6).mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | BP (7).mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | BP (8).mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | BP (9).mcpack | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | BP.mcpack | 0.06 | own (pw/AR suite or tooling) |  |
| OldPacks | extract_frames.py | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (10).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (11).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (12).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (13).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (14).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (15).json | 0.00 | own (pw/AR suite or tooling) | D1 |
| OldPacks | manifest (16).json | 0.00 | own (pw/AR suite or tooling) | D1 |
| OldPacks | manifest (2).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (3).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (4).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (5).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (6).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (7).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (8).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest (9).json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | manifest.json | 0.00 | own (pw/AR suite or tooling) |  |
| OldPacks | pack_icon (10).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (11).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (12).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (13).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (2).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (3).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (4).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (5).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (6).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (7).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (8).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon (9).png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | pack_icon.png | 0.04 | own (pw/AR suite or tooling) | D19 |
| OldPacks | RP (2).mcpack | 0.28 | own (pw/AR suite or tooling) |  |
| OldPacks | RP (3).mcpack | 0.28 | own (pw/AR suite or tooling) |  |
| OldPacks | RP (4).mcpack | 0.28 | own (pw/AR suite or tooling) |  |
| OldPacks | RP (5).mcpack | 0.28 | own (pw/AR suite or tooling) |  |
| OldPacks | RP (6).mcpack | 0.03 | own (pw/AR suite or tooling) |  |
| OldPacks | RP (7).mcpack | 0.03 | own (pw/AR suite or tooling) |  |
| OldPacks | RP (8).mcpack | 0.03 | own (pw/AR suite or tooling) | D15 |
| OldPacks | RP.mcpack | 0.05 | own (pw/AR suite or tooling) |  |
| OldPacks | Unified-Abs0lut-Claude-v0_6_5-PROJECT-RETEST.mcaddon.txt | 425.04 | own (pw/AR suite or tooling) |  |
| OldPacks | Unified-Abs0lut-Claude-v0_6_6-HOTFIX.zip | 419.88 | own (pw/AR suite or tooling) |  |
| OldPacks | v0_6_5-TESTING-GUIDE.md | 0.01 | own (pw/AR suite or tooling) |  |
| OldPacks | v0_6_6-TESTING-GUIDE.md | 0.01 | own (pw/AR suite or tooling) |  |