# R8 — WATER: STOP IT AND MOVE IT (D-C573; his 13:56 / 14:00 CT 10-05) — research + measurements

His law: "Water can't be stopped, only moved … feed the water into a man-made waterfall/fountain structure, and funnel it
down into the sewers … ALL of our structures include subsurface infrastructure." 14:00: "c — learn not just to move it, but
ALSO to stop it. We can dam the water, but we should also learn to direct it."

## 1. Engine facts (Bedrock) — measured on BDS (M) or from the wiki (W)
- (M) A wall whose top cell is AT the water's surface cell holds a lake: 0 regrowth in 400 ticks; +1 holds too (laketest V1–V4).
- (M) Edge column or margin column: no difference. A closed door holds (V8). A 1×2 opening leaks a BOUNDED puddle (121 cells, V7)
  — flowing water from one opening spreads 7 and stops.
- (M) A partial drain regrows as SOURCE water within 60 ticks (V9) — infinite water.
- (W) Bedrock source rule: a flowing cell becomes a source when ≥ 2 horizontal neighbours are sources and it sits on a solid
  block or a source — AND (Bedrock only) when it has one source beside it and one source ABOVE it. A pond above a drained room
  therefore re-sources the room top-down. [minecraft.wiki/w/Water]
- (W) Flow: 7 blocks on the flat, 5 ticks a block; falling water resets the distance.
- (M) Flowing and falling water report the id `minecraft:water` (state liquid_depth 1–7, 8+ falling); `/fill … air [] replace water`
  removes sources, flowing and falling alike; `replace flowing_water` matches nothing (flowtest).
- (M) `/fill` from a script works up to 32,768 blocks a call; `successCount` 0 = nothing matched OR part of the volume asleep;
  `dim.fillBlocks(BlockVolume, "minecraft:air", {blockFilter:{includeTypes:["minecraft:water"]}})` works too (filltest).
- (W) Sponges absorb water within 7 (taxicab); bubble columns (soul sand up / magma down) move entities, not water volume.
- (M, harness) `getTopmostBlock` skips liquids; a Block read in an unloaded chunk throws; `runCommand` does not throw on a no-op.

## 2. What "moving" water means in this engine
- Only SOURCE blocks are infinite. FLOWING water is finite: it runs at most 7 cells on a level and vanishes when its source
  is cut. So water is "moved" by keeping the sources where they are (the lake, the pond) and letting a FLOWING stream leave
  them through a designed path; the stream never multiplies as long as no two sources touch the same flowing cell
  (and, in Bedrock, no source sits above a flowing cell that has a source beside it).
- A cascade = a lip cut 1 wide in the dam (the stream's head), then steps: each drop resets the 7-cell run, so a stream can
  descend any height in steps of ≤ 7 cells of run. A fountain = a single source on a pedestal (water spills 1 down into a
  basin whose rim is one block high) — finite, the basin holds flowing water only.
- The sewer "exit": the stream falls into the trench (feet -13); the trench runs downhill to the outfall; at the outfall the
  flowing water ends (7 cells past the last drop) or joins a lower natural water body. Nothing has to be deleted.
- DAM rule: wall top ≥ the surface cell (+1 per his rule), on every edge where water stands at or above the floor, no
  waterloggable blocks in the wall, openings (doors) closed or above the surface.

## 3. Existing Bedrock add-ons found (licences as shown; he decides)
| add-on | author | what | version | licence shown |
|---|---|---|---|---|
| [Dynamic Flowing Water](https://www.curseforge.com/minecraft-bedrock/addons/dynamic-flowing-water) | user_fl2uk3ztx54otdej | particle-based water flow over terrain (waterfalls, streams, currents push players); BP only; needs Experimental + Beta API | 26.10 (2026-03-25) | All Rights Reserved |
| [WATERFALL](https://www.curseforge.com/minecraft-bedrock/addons/waterfall) | BATBOA | particles + ambient sound on natural waterfalls; a "Laguz rune" to tune them | 26.30 (2026-07-25) | All Rights Reserved |
| [UtilityCraft](https://www.curseforge.com/minecraft-bedrock/addons/utilitycraft) | DoriosStudios | machines incl. fluid tanks ("store and move huge amounts of liquids") | 26.30 (2026-08-21) | All Rights Reserved |
| [Item Pipe](https://www.curseforge.com/minecraft-bedrock/addons/item-pipe) ([mcpedl](https://mcpedl.com/item-pipe/)) | — | item pipes (models usable as decorative pipe/culvert pieces) | — | not read yet |
- Nothing found so far that is a ready-made Bedrock fountain / cascade / sewer-drain BLOCK set; Java mods with fluid pipes
  (Fluid Pipes, Better Fluid Pipes, Refined Pipes, Simple Copper Pipes) are Java-only. Builder references: GrabCraft medieval
  fountain blueprints (grabcraft.com/search/medieval fountain), EnderChest fountain designs, the Minecraft Wiki
  "Building water features" tutorial (fetch blocked, 402).
- Personal-use law (§9): any of these may be used; each would go on the RESTRICTED-ASSETS list.
- Honest read: the add-ons are visual (particles, sound) or industrial (tanks); the mechanism we need — capture, cascade,
  culvert, dam — is vanilla water + our own blocks/templates. Their value would be the LOOK (WATERFALL's mist/sound;
  Dynamic Flowing Water's particle cascade for big falls).

## 4. Proposed system (round 1006) — capture → cascade → culvert → sewer → outfall, with dams
1. Survey: map water-surface heights inside the site, at the margin and 8–24 cells out (palace_water_audit's map, live).
2. Dam: retaining walls to surface+1 on every wet edge, BEFORE any cut (exists in 222).
3. Capture: where a pond/lake stands above the floor, cut ONE 1-wide lip in the dam at its surface level (the head).
4. Cascade: a designed stone race from the head down the grounds (steps ≤ 6 run, drops 1–4), ending in a fountain basin or a
   grotto in the court; flowing water only (no two sources on one path).
5. Culvert: from the basin's low side a 1×1 drop shaft to the sewer trench (feet -13); the trench carries it to the outfall.
6. Subsurface for every template: a drain line under the ground floor to the street's trench (civ_roster "drain course"),
   the palace with several sewer entrances (court drains, kitchen court, stables yard, the well, the basin's overflow).
7. Probes first (5-minute BDS tests): lip + cascade + shaft stays finite (no source multiplication, measured over 2,000
   ticks); a stream crossing a sewer junction; the Bedrock "source above" rule near a pond; a sponge drain vs /fill.
