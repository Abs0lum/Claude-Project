# R10 — Bedrock water: what it does and what we control (measured on our server, 2026-10-05)

**Why this exists.** His request at 19:48: *"we need a firm understanding of water and all of its capabilities and properties and commands and states … everything we can control and how to control it."* The aim is to grow cities to Metropolis 3 and finish the palaces on wet ground.

**How it was measured.** A test-only pack, `waterprobe` (0.0.1 and 0.0.2, never shipped to him), ran on our Bedrock Dedicated Server 1.26.52 with `@minecraft/server` 2.3.0. Each experiment builds its own stone arena in the sky (y 230) and prints numbers. The raw logs are `_bds/logs/civtest-20261005-200222.txt` (0.0.1) and `civtest-20261005-200640.txt` (0.0.2). Source and build scripts: `tools/waterprobe_src/main.js`, `tools/build_waterprobe_00{1,2}.py`. The 0.0.1 script is archived at `_logs/archive/waterprobe_main.0.0.1.js`.

**How to read the labels.**
- **MEASURED** means the server did it in front of us.
- **DOCUMENTED** means taken from Mojang's documentation or our own shipped files, not measured here.
- **OPEN** means not settled yet.

Everything is still "awaiting his witness" for how it *looks* on PS5. These are server-behaviour facts.

---

## 1. The ten laws (short version)

| # | Law | Evidence |
|---|---|---|
| W1 | **Water placed by script or `/setblock` as `minecraft:water` is INERT.** It does not flow until one of its six neighbours changes. One source placed on a flat floor was still one block after 200 ticks. A partial level (depth 3, 7, or 8 = falling) also stays exactly where it was put. | E1 (0.0.1), E2, E2b — MEASURED |
| W2 | **Placing `minecraft:flowing_water` makes it LIVE.** A source spreads at once. A partial level placed this way drains away within 40 ticks. Reading a block back always reports `minecraft:water`, never `flowing_water`. "Flowing" is a way of *placing* water (with an update scheduled), not a separate state you can read later. | E2 rows 4–5, E1 (0.0.2) — MEASURED |
| W3 | **Anything that changes next to inert water wakes it.** This includes a block set and removed, another water cell placed beside it, or a structure placed beside it. A 9 × 9 sheet placed cell by cell woke itself and spread from 81 to 176 cells. One block poked at its edge brought it to 310. A 6 × 6 inert sheet grew from 36 to 265 when a building was placed beside it. **`/fill water` is always live**: an 81-cell sheet grew to 321. | E13 A, B, D — MEASURED |
| W4 | **Spread:** one step every **5 ticks** (4 per second). It reaches **7 blocks** along a straight line, with depth rising 1→7 per step. On the diagonal the depth goes 0, 2, 4, 6 (Manhattan distance), so the puddle is a diamond of **113 cells**. When the source is removed, the sheet holds for 20 ticks and is gone by **35 ticks**. | E1, E1b (0.0.2) — MEASURED |
| W5 | **Falling water** reports depth **9** (8 or more means falling). A 12-block drop took **65 ticks** (about 5 ticks per block). It is slow because each new cell waits for its own 5-tick update. | E3 — MEASURED |
| W6 | **Infinite source:** a gap between two sources becomes a **source (depth 0)** only when **solid ground** is under it. Over air it stays flowing (depth 1) and falls (depth 9). A 2 × 2 pool made from two diagonal sources fills to four sources. | E4 — MEASURED |
| W7 | **Structures overwrite water with their own air.** Placed with default options (`structureManager.place` or `/structure load`), a closed 5 × 5 × 5 room inside a flooded tank stayed **dry: 27 of 27 cells air after 62 ticks**. With `waterlogged: true` (the API option, or the command's 7th argument) the room came out **full of water (27 of 27)**. An **open-topped** room was dry at tick 2 (6 wet cells) and **full by tick 62 (35 of 35)**: water comes back through any opening. | E10 — MEASURED |
| W8 | **Draining:** `/fill … air replace water` removes **every depth**, sources and flowing alike, at once (1 ms for 3,000 cells). `replace flowing_water` then finds nothing. A flooded 7 × 7 × 4 room emptied with its doorway open **refilled 44 cells in 60 ticks**. Sealed first, then emptied: **0 cells after 60 ticks**. | E5, E14 — MEASURED |
| W9 | **Waterlogged blocks act as sources once woken.** A waterlogged fence spread to 36, then 48 cells after a poke. A waterlogged stairs spread to 12 after a poke. **Flowing water never waterlogs anything.** Stairs, fences, slabs, panes, leaves and chests beside a live source all stayed dry inside. | E13 C, E6b — MEASURED |
| W10 | **Cost:** a sheet of **576 sources falling 22 blocks** onto a floor (1,194 water cells after 200 ticks) moved the server tick from 50 ms to a **worst of 61 ms**. Clearing 22 layers of 40 × 40 took **89 ms** in one tick. Water itself is cheap. **Our scripts' work around water is what costs**: the palace pumps hit 1–8 s before 1.3.224. | E11 — MEASURED |

---

## 2. Every state and block

**Block types the server has (E0, MEASURED):**
- **Water and lava:** `water`, `flowing_water`, `lava`, `flowing_lava`.
- **Underwater blocks:** `bubble_column`, `kelp`, `seagrass`, `sea_pickle`, `conduit`, `underwater_torch`, `underwater_tnt`, `waterlily`, `frog_spawn`, `turtle_egg`, all corals (live and dead, block, fan and wall fan).
- **Sponge and ice:** `sponge`, `wet_sponge`, `ice`, `packed_ice`, `blue_ice`, `frosted_ice`.
- **Other water-related blocks:** `cauldron`, `pointed_dripstone`, `dripstone_block`, `snow`, `snow_layer`, `powder_snow`, `mud` and mud family, `mangrove_roots`, `muddy_mangrove_roots`, `dried_kelp_block`.

| Block | States (MEASURED) |
|---|---|
| `minecraft:water` / `flowing_water` | `liquid_depth` 0–15. 0 = source; 1–7 = flowing, thinner each step; 8–15 = falling (the probe saw 9) |
| `minecraft:lava` | `liquid_depth` 0–15 (same scheme) |
| `minecraft:bubble_column` | `drag_down` true (over magma) / false (over soul sand) |
| `minecraft:cauldron` | `fill_level` 0–6, `cauldron_liquid` "water" / "lava" / "powder_snow" |
| `minecraft:sponge` | `sponge_type` "dry". Wet sponge is its own block, `minecraft:wet_sponge` |
| `minecraft:kelp` | `kelp_age` |
| `minecraft:seagrass` | `sea_grass_type` |

**Waterlogging is not a block state.** It is a second layer the API reads with `block.isWaterlogged`.

**Gamerules (E0, MEASURED).** No water rule exists in Bedrock: no `waterSourceConversion`, no flow-speed rule. `randomTickSpeed` (1 on the server) drives ice melting and kelp growth, not flow.

---

## 3. Everything a script can do (`@minecraft/server` 2.3.0, all present — E0)

| Call | What it does (MEASURED unless marked) |
|---|---|
| `block.setPermutation(BlockPermutation.resolve("minecraft:water", {liquid_depth: n}))` | **Inert** water at level n (W1). This is our tool for **still decorative water**: fountains, moats, a pond's surface, a mill-race at a fixed level. It stays until something next to it changes. |
| `… resolve("minecraft:flowing_water", {liquid_depth: 0})` | A **live source** (W2). Use it when we *want* the engine to flood, for example filling a moat that should find its own level. |
| `block.isWaterlogged`, `block.setWaterlogged(true/false)` | Waterlog or dry a block that can hold water. It throws "Block type cannot be waterlogged" on glass, stone and sea lantern. |
| `block.canContainLiquid(LiquidType.Water)` | true for stairs, slab, fence, pane, bars, leaves, chest, ladder, wall, lantern, rail, flower pot, campfire, scaffolding, chain, bed. false for glass, stone, torch, sea lantern. |
| `block.isLiquidBlocking(LiquidType.Water)` | true for full blocks and most "containers" listed above; false for rail, torch, flower pot. |
| `block.canBeDestroyedByLiquidSpread(…)`, `liquidSpreadCausesSpawn(…)`, `liquidCanFlowFromDirection(…, Direction)` | Present and answering. **OPEN:** the torch answered false to "destroyed by spread", which needs a witness check. Use these read-only until verified. |
| `block.isLiquid` | Present. |
| `block.getComponent("minecraft:fluid_container")` (cauldron) | Present. Setting `fillLevel = 6` writes the `fill_level` state. Setting the state directly works too. |
| `dimension.runCommand("fill … water")` | **Live** water (W3). Good for flooding an area. |
| `dimension.runCommand("fill … air replace water")` | Removes **all** water in the box, every depth (W8). Our drain. |
| `structureManager.place(id, dim, loc, { waterlogged })` | Default = the structure's air overwrites water (dry inside). `waterlogged: true` = the room fills (W7). |
| `structureManager.createFromWorld(…, { saveMode: StructureSaveMode.Memory })` | Works. `StructureSaveMode` = World / Memory. |
| `entity.isInWater`, `entity.isSwimming`, `getVelocity`, `applyImpulse`, `clearVelocity` | Present. `isInWater` turned true for items, cows and our test entities in the pool. `isSwimming` stayed false for all of them (it is the player/mob swim pose). |
| Enums | `LiquidType` = **Water only**. `FluidType` = Water, Lava, PowderSnow, Potion (cauldron contents). |

**There is no liquid event.** Nothing in the API fires when water flows. To know where water went, we **read blocks**: our flood-watch and palace survey do this.

---

## 4. Commands

| Command | Behaviour |
|---|---|
| `setblock x y z water` | Inert source (W1). `water ["liquid_depth"=4]` = inert partial level (E2b: still there after 40 ticks). |
| `setblock x y z flowing_water ["liquid_depth"=4]` | Live, drains away (E2b: air after 40 ticks). |
| `fill … water` | Live (W3); 300 blocks in 2 ms. |
| `fill … air replace water` | Every depth removed (W8). |
| `structure load name x y z rot mirror includeEntities includeBlocks waterlogged` | 7th argument = waterlogged (E10 row 4). |
| In the **Nether** | `setblock`, `fill` and script placement **all keep water**: three sources still there after 62 ticks, 80 cells of spread (E12). Only a *bucket* evaporates there. A Nether palace fountain is possible. |

---

## 5. Interactions

| Case | Result (MEASURED) |
|---|---|
| Water flows onto a **lava source** | **obsidian** |
| **Lava flows** into still water | **cobblestone** |
| Lava **falls onto** water | **stone** |
| **Sponge** placed by script into a 15 × 15 sheet | absorbed, became `wet_sponge` (225 → 206 cells). A second sponge by `/setblock` took 32 more. **OPEN:** Bedrock's sponge should take up to 65 blocks within 6. Our thin one-layer sheet may be the reason. |
| **Bubble column** in a 1 × 1 shaft | Formed by itself within 30 ticks over soul sand (`drag_down` false, lifts) and over magma (true, pulls down), all six cells. |
| **Ice** removed by `/setblock … air` or `… air destroy` | Leaves **air**, not water. Only a player breaking it (or melting) makes water. |
| **Kelp / seagrass** placed in AIR by script | They stay and report `isWaterlogged = true`. They carry their own water. |
| **Cauldron** | `fill_level` 6 and `cauldron_liquid` "water" by state or by component. |

---

## 6. Floating things (E8, MEASURED; positions every 10 ticks)

| Entity | In a 13 × 13 × 8 pool |
|---|---|
| Item (oak log) | Rises from 2 below the surface to the surface in about 20 ticks, bobs at the surface |
| Cow | Rises about 0.07 blocks per tick, bobs at the surface |
| **`wp:float`** (our test entity with **`minecraft:buoyant`**, base_buoyancy 1.0, simulate_waves) | Rises slowly from 4 deep: about 0.2 blocks per 10 ticks (2 blocks in 100 ticks). It works, but this buoyancy value is slow. **Tune** base_buoyancy above 1 for a log that bobs up briskly. |
| `wp:sinker` (physics, no buoyant) | Sinks to the floor (−5) in about 60 ticks |
| Item / `wp:float` in a **current** (a live channel) | Drift **about 0.5 blocks per second** down the flow and stop where the flow ends (x 9.2 / 9.6) |

**What this means for us:** a felled tree's logs (or our falling-tree entity) can **float and drift downstream** with `minecraft:buoyant` + `minecraft:physics`. This is the Haubna "buoyancy" idea made of engine parts (R9 §8).

---

## 7. Custom blocks: `minecraft:liquid_detection` (E7)

Six of our own blocks loaded with no content-log error (format 1.21.80, full-block geometry):
- default (no component)
- `can_contain_liquid: true`
- `on_liquid_touches: popped`
- `broken`
- `blocking`
- `stops_liquid_flowing_from_direction: ["east"]`

- `canContainLiquid` answers follow the JSON (true for `contain` and `stop_east`).
- Script `setWaterlogged(true)` on the `contain` block **works** (`isWaterlogged` true), and it did not spill in 30 ticks (inert, W1).
- **OPEN:** with a live source beside them, **none** of the popped / broken blocks changed. Most likely reason: a full cube is never "entered" by water. These reactions are probably meant for blocks with partial geometry (plants, posts, grates). Probe 0.0.3 will test them with partial geometry. Until then: **a custom sluice gate or grate cannot rely on popped/broken.**

---

## 8. Looks (DOCUMENTED — our shipped files; his PS5 is the witness)

- **Vibrant Visuals `water/water.json`** (RP-02, `format_version` 1.26.0; RealSource's values, kept by his ruling 20:01):
  - `particle_concentrations`: chlorophyll 0.015, suspended_sediment 0.1, cdom 0.08 (these set colour and murk)
  - `waves`: enabled, depth 0.08, frequency 0.9, octaves 9, speed 2.6, …
  - `caustics`: enabled, power 1.3, scale 0.4
  - `biome_water_color_contribution` 0.15

  These are **global**. There is no per-block or per-region wave control (Haubna's "distance to shore" is a Java shader; not possible here).
- **Water textures with normal and MER maps:** from Kelly's RTX pack (`textures/blocks/water_*.texture_set.json`).
- **Particles we already override** in RP-02: `water_splash`, `water_splash_manual`, `water_drip`, `water_wake`, `water_evaporation_*`.
- **Per-biome water colour** is client-side (`client_biome` / biome JSON water colour). Scripts cannot change it.
- **Fog under water** comes from the fog settings (the FOG-LIGHTING dossier). Not touched here.

---

## 9. What this changes in our own work (Retro-Sweep candidates — backlog, nothing auto-applied)

1. **Palace drainage (mechanism now explained).**
   - Why water comes back: the palace pieces are structures. Their air overwrites water at placement (W7), but every open doorway, window or roofless court next to the moat or the sea lets it back in (W7 open box, E14 A). Placing a piece also wakes inert water beside it (W3 D).
   - **Fix direction:** before a piece is placed in or beside water, ring its footprint with a temporary **cofferdam** (glass or cobble walls, 1 thick, up to the water surface). Place the piece, drain the inside with one `/fill air replace water`, then take the cofferdam down **only where the piece's own walls hold the water**.
   - This replaces repeated pump passes (each pass costs time and refills).
   - Effort M · priority HIGH (palaces to Metropolis 3).
2. **Moats, fountains, ponds and the well:** place them as **inert** water (setPermutation `water`, W1). They then never spread onto streets. Building next to them must expect W3: a plot placed later beside the moat wakes it, so the moat's rim must be solid before its water goes in. Effort S.
3. **Flood-watch:** water spreads at most 7 cells on flat ground and only 1 step per 5 ticks. The watch can look only within 8 cells of known water. Effort S.
4. **Stilts and piers in water:** posts are full blocks, so they are fine. Fences, walls and chains used as posts can be **waterlogged** (W9), and a waterlogged post *spreads* water once disturbed. **Use full logs or stone under water.** Effort S.
5. **Falling trees into rivers:** `minecraft:buoyant` (§6) lets logs float and drift. Effort M, idea only.
6. **Nether builds:** script and command water survives in the Nether (E12). Idea only.
7. **Drains:** `/fill air replace water` takes every depth (W8), so the old two-pass drain (`water` then `flowing_water`) can drop its second pass. Effort S.

## 10. Still OPEN (probe 0.0.3)

- Whether `liquid_detection` popped/broken/blocking work on blocks with **partial geometry**.
- Sponge reach in a **3-D** pool.
- Whether **random ticks** ever wake inert water (it did not in 200 ticks at `randomTickSpeed` 1).
- Whether inert water **survives a chunk unload and reload** (this matters for moats far from the player).
- Water against **our custom blocks** (pw: roofs, ramps, angled walls) used as moat walls.


---

## 11. Probe 0.0.3 — the open items closed (21:2x CT; log `_bds/logs/civtest-20261005-212047.txt`, BP-02 loaded beside it)

| # | Question | Result (MEASURED) |
|---|---|---|
| W11 | `liquid_detection` on NON-full blocks | **Partial collision (our ramp-quarter geometry, a 4-px slab): `popped` and `broken` WORK.** The block is destroyed and water takes its cell (no drop: the test blocks had no loot). `can_contain_liquid: true` + `no_reaction`: the block holds the water (`isWaterlogged` true) and the flow passes it. `blocking`: the block stays; water went around it on the open floor. **Cross geometry with no collision:** `no_reaction` lets water through and the block reports waterlogged. `popped`, `broken`, `blocking` and `contain` all **held the water back** (west of the block stayed dry) and the block was not destroyed. **So `popped`/`broken` need a collision box** — the R10 §7 OPEN item is closed: a sluice, a grate, a weir must be a partial-collision block. |
| W12 | Sponge in 3-D | A script-placed sponge in a 15 × 15 × 7 pool absorbed **33 cells**, all within **taxicab 4**, and became `wet_sponge`. (Java's 65 within 7 does NOT hold on Bedrock as placed by script; a player's sponge was not measured.) |
| W13 | Random ticks vs inert water | Under randomTickSpeed 300 for 200 ticks, inert partial levels (d3, d7) **stayed exactly as placed** (not spread, not gone) — random ticks never wake water. **Inert SOURCES at y 231 turned to ICE**: high ground is cold (biome temperature falls with height), and a still source in the open freezes there. A mountain moat or fountain above the snow line needs a roof, a light, or a lower site. |
| W14 | Inert water across an unload | A ticking area removed for 200 ticks (the chunks really unloaded) and re-added: the inert source and the inert d3 level were both **still there and still inert** (no spread). A moat far from the player keeps its shape. |
| W15 | Our blocks | Every pw: block tested (roof45, roof ridge, ramp quarters, ramp 2-hi, angled wall, bench, chair) **cannot be waterlogged** (`setWaterlogged` throws "Block type cannot be waterlogged") and answers `isLiquidBlocking` = true; water poured on top of each **stayed on top** (the block itself was never replaced). Water beside them reached the far side only by flowing around on the open test floor (ramp, ridge, furniture: wet; roof45 and angled wall: dry) — a wall of them holds water. (The planks-grid row used a wrong id, `pw:planks_grid_oak`; the block is `pw:oak_planks_grid` — row void, retest later.) |
| W16 | What a flow destroys (vs the API) | **Destroyed:** torch, stone button, ladder, short grass, wheat, oak sapling. **Stayed:** rail, poppy, carpet, redstone wire, lantern; tripwire became waterlogged. **The API's `canBeDestroyedByLiquidSpread` said FALSE for every one of them, including the six that were destroyed** — it cannot be trusted for this; a planner must use a measured list (above). |
| W17 | Farmland | Void: the test's source froze (W13) before the farmland could be wetted; retest at sea level. |
| W18 | Concrete powder | Turns to concrete beside **inert** water too (20 ticks) — placing powder is itself the update. |

**Retro-Sweep hits (backlog):** (a) palace / castle moats and fountains on high ground: cover or site below the freezing height (W13) · (b) the sewer grate / sluice gate as a partial-collision custom block with `popped` → no; with `blocking` + a 4-px collision (W11) · (c) the lane and street planners must not lay torches, ladders, saplings or crops where water can reach (W16) · (d) farmland test at sea level (W17).
