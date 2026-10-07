# SLABFORGE FIRST-LOAD v2 — DESIGN DRAFT FOR DISCUSSION
**Stamp: 2026-09-22 23:4x CT · status: DRAFT — nothing built · journal D-C239 · supersedes the SlabForge runtime design (BP-02 v1.3.150–.186) once approved.**
**Ruling this answers (Abs0lum 23:25):** the ticking-area design is APPROVED in full, plus: an accurate timer (he will do a test run); coverage to the maximum AND minimum heights; applied underwater; ALL per-player behaviour removed; a first-load, spectator-only, timed world-building event; "we LOAD the world with the slabforge key, and once the world is loaded, we play without it"; quality over time; "we need much more discussion".

---

## §1 · The event, as I understand it (confirm or correct each line)
1. Create the world (single-player or Realm — either) with the full stack **plus the SlabForge key**.
2. First join: you are put in **spectator**. A title says WORLD BUILDING, and the action bar shows progress and a countdown.
3. The forge works outward from the **world spawn**, ring by ring, to the chosen radius (50 chunks = 800 blocks), smoothing ground at **every elevation** (peaks to valley floors) and **under water**.
4. You can leave at any time; progress is saved; the next join resumes where it stopped.
5. When it finishes: a completion screen. You Save & Quit, remove the key from the world's behaviour packs, rejoin — back in your normal game mode, slabs in place.
6. Play. Nothing smooths during play. To go further later: re-add the key, raise the radius; only the new rings are done.

## §2 · What goes away (the "per player" parts)
- The runtime scanner: 20-block radius around each player, ±3 blocks of the player's height, per-player cursors, 20-tick cycles.
- The lip walker and the audit/repair job during play.
- Edit immunity and terrain-baseline immunity (they exist because players change terrain while it smooths; a pre-play pass has no player edits).
- The done-chunk string ledger (caps near ~3,070 chunks) → replaced by a region bitmap (§6).
- The "dormant boost" coupling (tree walking ×3 while the key is out) is re-examined separately.
**Kept unchanged:** the qualifier (two-flat antipode rule, cliff gate over all 8 neighbours, slope gate, same-material gate), the slab family and its 16-variant lattice, flora seating, snow seating.

## §3 · Coverage — every height, and under water
**Heights.** Each column's ground is found from the top of the world (y 320) down, at any elevation down to −64, using `Dimension.getTopmostBlock` (stable) and then descending through things that are not ground: leaves, logs, plants, snow layers, water.
- **Question Q1 — "minimum heights":** (A) the TOP ground of every column (mountain tops, hillsides, valley floors, sea beds) — or (B) also every ground surface BELOW an overhang or cave roof (cave floors, ravine floors, under cliffs). B multiplies the work by the number of surfaces per column and puts slabs in caves.
**Under water.** Water, seagrass and kelp are descended through; the sea/river/lake bed is judged by the same rules.
- The slab must hold water, or every underwater slab leaves a dry pocket. **Engine facts (checked):** block component `minecraft:liquid_detection` with `can_contain_liquid: true` is **stable since block format 1.21.60** (ours are 1.21.80) and has `use_liquid_clipping` (the collision box clips the water visually); the script call `Block.setWaterlogged(true)` is stable. So each of the 40 slab blocks gains the component and underwater placements are waterlogged.
- **Question Q2:** seagrass or kelp rooted in the cell the slab would take — (A) skip that column, (B) place the slab and re-seat the plant on it, (C) place the slab and remove the plant.
- Ice over water: descend through it to the bed (default) — say if not.

## §4 · Loading far ground without a player
- **Script ticking areas** (`world.tickingAreaManager`, stable from @minecraft/server **2.6.0**, ≈ game **1.26.20+**; your last recorded version 1.26.32 qualifies — **Q3: please read the version at the bottom of the title screen**). The forge asks for an area, the game answers when every chunk in it is loaded and ticking, the forge works it, releases it, moves on.
- **Per-pack chunk cap:** Microsoft: "limited by a fixed amount of ticking chunks per pack independent of the command limits"; the number is only readable in-game (`maxChunkCount`) — the test run prints it and the batch size follows it.
- **Batch:** process 8 × 8 chunks with a 1-chunk margin (10 × 10 loaded) so edge columns can see their neighbours; if the cap is smaller, the batch shrinks automatically.
- **Unknown to verify in the test run:** whether a ticking area GENERATES chunks nobody has visited (the docs don't say). **Fallback if it doesn't:** the spectator is carried ring by ring (the PW-Pregen grid-hop idea — I could not find its source on the Drive or in project knowledge; upload it if you have it), and the game generates around the spectator exactly as it does for a walking player. Both paths end in the same forge.
- **Why not simulated players:** they exist only in the GameTest module, which has never had a stable release (every published version is beta) → the world needs the Beta APIs experiment and the forge would break with updates.
- **Order:** rings outward from world spawn, so an interrupted run always leaves a finished core.

## §5 · The timer
**Goal:** "about N min left" that is honest and settles quickly.
- **Work is counted in chunks.** Each batch records how long it took: waiting for the game to load/generate + judging columns + placing slabs.
- **Estimate = remaining chunks × recent seconds-per-chunk** (a moving average over the last several batches, so an ocean ring or a mountain ring moves it only gradually), shown with elapsed time and percent: `WORLD BUILDING 34% · 2,670 / 7,845 chunks · about 41 min left · 21 min elapsed`.
- **Before any batch has finished** there is no honest number; the calibration value from your test run (§8) seeds it, so the timer is useful from the first minute. Without one it shows "measuring…" for the first batches.
- **Q4 — accuracy vs total time:** (A) ONE pass (above; accurate after the first few percent) — or (B) TWO passes: a survey pass that loads/generates everything and counts the real work per chunk, then the smoothing pass with a near-exact countdown. B roughly doubles the loading cost; A is my recommendation unless the test run shows A wandering.
- The timer also measures the device: the same world takes longer on the phone than the laptop; the countdown follows whatever it measures.

## §6 · Resources (why a bigger radius only costs time)
- One batch at a time; a fixed slice of each tick for script work (the engine's runJob time-slicing, as all our scanners); memory per batch ≈ one 160 × 160 height grid.
- **Ledger:** 1 bit per chunk in 32 × 32-chunk regions (radius 50 ≈ 16 regions ≈ 2.8 k characters), world dynamic properties, saved after every batch → resume is exact.
- Rough scale (illustrative until the test run): radius 50 = 7,845 chunks ≈ 2.0 million columns.

## §7 · Completion and leaving
- Completion: title WORLD BUILT + a screen (server-ui form) with the next steps.
- **Limit:** a script cannot quit the game or send the host to the menu; the form tells you to use Save & Quit. On a Realm (a server), a "Quit now" button that disconnects the player is possible in principle — **to test**; in single-player it cannot work.
- While the key is still in after completion: spectator stays, the banner says remove the key.
- Rejoin without the key: your previous game mode is restored (recorded when spectator was applied). Nothing smooths.
- **Q5:** radius — 50 chunks as the first target?  **Q6:** centre — world spawn (default), or a spot you choose once?

## §8 · Test plan (your offer to do a test run)
- **T1 calibration world** (radius 4 chunks, ~50 chunks, ~minutes): prints the per-pack chunk cap, proves or disproves generation by ticking area, measures seconds-per-chunk on that device, and shows underwater slabs (look for dry pockets / water clipping). Its number seeds the timer.
- **T2** radius 16 on a fresh world: timer accuracy (compare the countdown with the stopwatch at 25/50/75 %).
- **T3** the real world at the chosen radius.

## §9 · Open questions (summary)
Q1 min heights A/B · Q2 seagrass/kelp A/B/C · Q3 game version · Q4 timer one pass / two passes · Q5 radius · Q6 centre.

## §10 · Sources
@minecraft/server typings (npm): 2.3.0 `getTopmostBlock(locationXZ, minHeight?)`, `heightRange`, `setWaterlogged`, `isChunkLoaded`, `GameMode.Spectator`, `setGameMode`; 2.6.0 `TickingAreaManager` (first stable; rc tags 1.26.10/1.26.20 previews); npm dist-tags of @minecraft/server-gametest (beta only). Microsoft Learn: TickingAreaManager class; minecraft:liquid_detection (min format 1.21.60, no experimental toggle); Ticking Areas command (10 areas, circle radius ≤ 4 — command limits, separate from the script manager). Bedrock Wiki block format history (liquid_detection experimental 1.21.50 → released 1.21.60). BP-02 v1.3.186 main.js (`_slabSweep`, `_slabColumnSurface`: water returned as the surface → no slab map → never reaches the bed).
