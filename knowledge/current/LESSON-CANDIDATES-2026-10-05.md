# LESSON CANDIDATES — 2026-10-05 (round 1005: the palace, the gallery, the book)

Status: CANDIDATE until Abs0lum's witness on real hardware confirms the in-game ones; the BDS-observed engine facts are
marked (BDS) — they were seen in the harness log, not inferred.

- **LC-1005-1 (BDS) The script watchdog kills the pack at 10 s of script in one tick; QuickJS is slow.** A per-candidate
  walk over ~20k street-cell keys (`k.split(",")`) hung 10,007 ms (gate run 2 of 221). Pre-index into a chunk Set once
  per day; never loop cells × candidates in one tick. Related: a city day costs ~1 s at 40 buildings / 130 people;
  LAG_SLICES went 5 → 3 so a beat stays near 3 s.
- **LC-1005-2 (BDS) `structureManager.place` costs ~40 µs per cell.** A full 64×48×64 plot stage (196k cells) took
  6.8–8.2 s; the light plot (7–8k cells: foundations and lawn only) takes 0.16 s. Keep any stage file under ~150k placed
  cells; make the land (clear above, fill below) a runJob generator.
- **LC-1005-3 (BDS) A Block handle from an unloaded chunk throws on READ.** `getTopmostBlock` inside try/catch is not
  enough: reading `.typeId` afterwards throws `LocationInUnloadedChunkError`. Wrap the read.
- **LC-1005-4 (BDS) Entities spawn only in TICKING chunks.** A chunk can be loaded (getBlock works, a structure places)
  and still refuse `spawnEntity` — "not in a chunk currently loaded and ticking". Anything that spawns must be resumable.
- **LC-1005-5 (BDS) Wetness is the TOPMOST block, at any height.** `groundAt` walks down to a lake bed and reports flat
  ground; the palace was laid in a mountain lake at y 108. Count water / ice tops in the site sample.
- **LC-1005-6 (BDS) The crown's surveyors.** A site beyond the player's simulation distance can only be measured if a
  ticking area is held over it; one 160×160 area (10×10 chunks, chunk-aligned) holds a 132×132 block.
- **LC-GAL-1 (to witness) One entity type per picture loads only the textures in view.** 6,256 client entities each
  with its own JPEG; the claim is that VRAM scales with what hangs near the player, not with the catalogue. Witness:
  walk the palace on PS5, then the phone; watch for stalls when a new room's pictures first render.
- **LC-GAL-2 (to witness) .jpg entity textures render.** RP-12 ships JPEG textures (174 MB for 6,256); Bedrock lists
  png / tga / jpg as texture formats. Witness: any picture visible = confirmed.
- **LC-GAL-3 (to witness) Per-face UV on the north / west faces is not mirrored.** The frame geometry maps the picture
  onto the facing face only; if a north- or west-facing picture shows mirrored (a signature backwards), the fix is a
  negative uv_size on those faces.
- **LC-GAL-4 (BDS) The no-repeat registry holds.** Gate run 2: 192 pictures, 186 distinct entity types, 0 true
  duplicates (the 6 counted in run 1 were boundary pictures seen from two buildings' boxes).
- **LC-SRC-1 The Met retired `/v1/search` on 2026-10-01** (410 with a message); `/v1.1/search` is paginated (limit,
  offset) and keeps artistOrCulture / departmentId / isHighlight. `/v1/objects/{id}` still serves.
- **LC-SRC-2 The Art Institute of Chicago's IIIF server sits behind a Cloudflare challenge** (403 "Just a moment") for
  scripted fetches; its JSON API answers. Wikimedia 400, Rijksmuseum 410, nga.gov pages 403 from the shell; NGA open
  data (GitHub CSVs) + api.nga.gov IIIF, Cleveland's API + CDN, and Wikidata entity JSON all serve.
- **LC-1005-7 (BDS) `structureManager.place` skips unloaded chunks WITHOUT a word.** A 64×64 piece spans five chunks; the
  clock's two-corner "loaded" test passed while middle chunks slept (the harness loads a plus-shaped area; the palace sat in
  its corner), the piece came out half built over the original terrain and its lake, and three gate runs read it as "the
  palace is flooded". Every chunk of a footprint is probed before a stage is placed (1.3.221 placeStage). The real-play
  twin: a PS5 at simulation distance 4 can have the far side of a piece unloaded while the near corner is in view.
- **LC-1005-8 (BDS) `getTopmostBlock` skips liquids — a lake reads as its bed.** The wetness test (run 4), the retaining
  wall height (run 7: a 27-deep mountain lake poured over a wall built one block above its bed) and the outside-water test
  all needed to climb from the topmost solid through the water column to the SURFACE. Rule: any "how high is the water"
  read walks up from the topmost solid.
- **LC-1005-9 (harness) A timed-out Bash tool call kills background jobs started from earlier calls in the same session**
  (run 6 died in the same minute as a 2-minute poll timing out). Start long runs with `setsid nohup … &` and keep polls
  under ~110 s.
- **LC-1005-10 (static, engine fact) A light block has NO collision — one buried in a walkable floor course is a hole.**
  palacegen's `slab()` buried `light_block_14` in every floor course it laid (first floors, attics, the gatehouse's rooms):
  59 hole cells in the 128×128 model, found while writing the castle verifier. Rule: a light block stands in the AIR of a
  storey (just above the floor, or at the ceiling), never in a course anyone walks on. Census of the 52 shipped templates
  after the fix: 239 light blocks, 0 hole-type. castlegen v0.2 follows the same rule.
- **LC-1005-11 (BDS) A survey must sample only inside the area it holds.** Gate run 9: the site rules read 24 cells outside
  the 128-block box, beyond the 10×10-chunk area the surveyors can hold; those reads threw / missed, the sites stayed
  "open" for ever (58 of them), and no palace was laid in 80 days. Rule: hold the area so that every sample of the test
  lies inside it (the survey box is the block ± the sample distance, 8 cells), and never let a sample that cannot be
  taken keep a site pending beyond the day its area is held.
- **LC-CASTLE-1 (static, physics) A diagonal line of corner-touching blocks beside a parapet cannot be walked.** A player's
  0.6-wide box must overlap a block below while it clears the wall block at its level; on a 1-wide diagonal walk with a
  solid skin on one side and a drop on the other, no path exists. Diagonal wall-walks are laid two courses wide (a
  4-connected staircase of cells). The offline verifier (tools/castle_verify.py) models exactly this pinch rule.
- **LC-1005-12 (process) A new pack takes the next FREE number of the registry.** The gallery shipped twice under "RP-08",
  which is the Items pack; RP-09 (BP-05's locked dependency), RP-10 Terrain and RP-11 Ores are taken → RP-12. Check the
  outputs folder's RP-NN / BP-NN names and the locked dependency list before naming a pack.
- **LC-1005-13 (BDS) A land job that reads the column OUTSIDE its box reads a chunk it does not hold.** Run 11: the nw
  quarter got 0 retaining blocks (its outside columns slept when the land job ran — `getTopmostBlock` came back empty and
  the code took "no wall needed"), and the lake poured in at ~26k cells a day for as long as the pumps ran. Rule: a wall's
  height comes from the piece's OWN edge column too (always loaded while the piece is built), the greater of the two; and
  anything decided from a column that may sleep is re-checked on every later pass (the pumps re-run the wall job).
- **LC-1005-14 (BDS, mechanism) A lake is infinite water: a cell-by-cell drain never ends.** Runs 10–12: every pump pass
  found 20–27k water cells again right after a pass had left ~0, with every retaining wall in place and no new wall needed —
  two source blocks beside a drained cell make a new source faster than a 300-cells-a-tick job removes them. Rule: standing
  water is removed ATOMICALLY (`/fill x y z x y z air [] replace water` and `… replace flowing_water`, slabs of 7 layers
  under the 32,768-block limit), never by a generator over ticks; the same holds for any future moat, canal or pond work.
- **LC-1005-15 (BDS) `runCommand` does not throw when a command does nothing — read `successCount`.** Run 13: `/fill`
  over a quarter whose chunks were partly asleep returned without an exception and changed nothing; the log said "ok".
  Rule: a command's success is `result.successCount > 0`, never "it did not throw"; and a /fill needs the whole volume's
  chunks loaded — hold the area (ensureTicking) and wait a few ticks before the command (FILLTEST probe, 10-05).
- **LC-1005-16 (BDS, measured — the LAKE and FLOW tests, 13:1x–13:3x) How standing water is held and removed.** A wall whose
  top cell is AT the water's surface cell holds a lake (0 regrowth in 400 ticks); +1 holds too and is the rule (his 12:12:
  the harness's east wall stood one short, 119 under a 120 surface, and the lake stepped over it onto the cornice and
  filled the palace's rooms to their ceilings). Margin or edge column: no difference. Halves drained 60 ticks apart self-heal
  to 0 once no source remains. A 1 × 2 opening leaks a bounded puddle (121 cells); a closed door holds. A partial drain
  regrows as SOURCE water within 60 ticks. Flowing and falling water carry the id `minecraft:water` (liquid_depth 1–7, 8+):
  `/fill … air [] replace water` removes sources, flowing and falling alike; `replace flowing_water` matches nothing.
  `successCount` is 1 only when a block changed (0 = nothing matched, or a chunk of the volume asleep).
- **LC-1005-17 (BDS, mechanism) Water comes from where the SURFACE MAP says it is highest — read the map before the
  wall.** Runs 12–17 chased the lake beside the palace; the water-surface map of the run-16 dump (tools/palace_water_audit.py)
  showed the inside standing ABOVE the outside: a pond in the block's own columns above the box's top fed the rooms from the
  sky, and a drain whose ceiling was the box's top could never win. Rule: any drain covers the whole cleared column (box
  top + the clearing height), and before a water fix the surface heights inside / at the margin / 8–24 cells out are mapped.

## CORRECTIONS (15:4x CT 10-05) — the "flooded palace" root cause
- **LC-1005-18 (static + BDS, ROOT CAUSE of gate runs 2–18) A structure writer passed the block VERSION as the waterlogged
  flag: every cell of the palace was saved waterlogged.** palacegen.cut() handed `e[2]` of the palette tuple (name, states,
  version) to `Structure.set(..., waterlogged)`; the int was truthy, so layer1 = water source in all 196,608 cells of each
  piece and in the 20 stage files. Every waterloggable block (panes, doors, ladders, slabs, roof wedges) became a spring:
  the rooms flooded, water ran down the roofs, and every drain regrew in seconds. Proven by the PALACE-DRY probe (the pieces
  on a platform in the air: 353 sources in 200 ticks; after the fix only the 17 basin cells by design). Rules: never pass a
  palette tuple's fields positionally; every structure file is censused for layer1 cells before it ships (833 files today:
  only the 24 palace files carried it); a "template or site?" test (the structure placed alone, far from any terrain) comes
  BEFORE any site theory.
- SUPERSESSION / RE-ATTRIBUTION (lesson-supersession protocol: the losers are tagged, not deleted):
  - LC-1005-17 (the pond above the box) — **SUPERSEDED BY LC-1005-18**: the water on the roofs came from waterlogged roof
    wedges, not from a pond.
  - LC-1005-13 (a sleeping outside column gave no wall) — the fact stands (reads of sleeping chunks come back empty); the
    claim that it flooded the palace is withdrawn.
  - LC-1005-14 (a cell-by-cell drain never wins) — the measured part stands (laketest V9: a partial drain regrows as sources
    in 60 ticks); the palace's regrowth was the waterlogged springs.
  - LC-1005-16 — the measured dam / flow / fill facts stand; the line "the harness's east wall stood one short and the lake
    stepped over it" is withdrawn as the cause.
  - LC-1005-5/8 (getTopmostBlock skips liquids) and LC-1005-7 (place skips sleeping chunks) stand on their own evidence.
- **LC-1005-19 (BDS, the CASCADE probe) Moving water is free.** A dammed pond drained through a 1–2 wide lip into a stepped race
  → basin → drop shaft → trench stays finite for 2,000 ticks: the pond stays full, the path holds 98–130 flowing cells and 0
  new sources; a fountain jet (one source in a basin) stays one source; a closed trench does not back up. Water features and
  sewer feeds can be built without any drain machinery.

## ROUND 1005c (his 16:50 report on 1.3.222) — 18:xx CT
- **LC-1005-20 (static, PENDING WITNESS) Bedrock draws an entity model turned 180° about Y at yaw 0.** RP-12's frame bones
  were authored as if file axes were world axes: bone n (file z 7..8, art on its 'north' face) rendered on the ROOM side of
  its cell (world z −0.5..−0.4375) with the art pointing INTO the wall — the back faced the room, 0.9375 of gap behind it
  (his screenshots: he stood in it). Every facing showed the same error, so the fix shows the OPPOSITE bone per facing
  (0→s, 1→w, 2→n, 3→e). Whether L-XFACE's X-mirror applies to entities is open: his "all of them" fits a pure rotation;
  an E/W painting shot after RP-12 1.0.1 settles it. Rule: any directional entity geometry is checked in-game per facing.
- **LC-1005-21 (witness + BDS) The script watchdog's Hang (10 s on his device) is a TICK budget, and a tier-up was one tick.**
  City II = 6–8 s on our PC host (the 36 plots' slot searches in one loop); past City II his world was shut down
  ("Unhandled critical exception of type 'Hang'", plus "High memory usage" > 100 MB). Rules: work that scales with a
  tier's plot count is a queued charter (one item per beat); skipped days are paced (one per 10 ticks, never in the main
  beat's tick); the state JSON is saved at most every 100 ticks; gates run with script-watchdog-hang-threshold=3000 and
  treat "High memory usage" and any slow line ≥ 1 s as failures; gates climb PAST the last tier he reached.
- **LC-1005-22 (static) A ledger unit must be converted at the payment boundary.** The shop's sell price was computed in
  pennies (12 to the coin) and issued as coins: 12× pay. Every price shown or paid names its unit; tests pin it.
- **LC-1005-23 (witness) A crowd sent to one point stands in one clump — and that point was inside the well.** The square
  goal was square + 6.5 = inside the well's footprint, for every jobless person at work hours and EVERYONE at dusk. Goals
  for many people are per-person slots (a ring of 33 cells), rotated through the day across yards / centres / shops / inn.
- **LC-1005-24 (static + sim) An orphan-leaf check must ask "does this CLUSTER touch a log", not "is a log within 6 steps".**
  The 6-step / 50-node BFS already stripped ~18.5 % of an old birch's leaves whenever any log nearby was cut (the 'bare
  pole'); with the trunk ending at the crown base it would strip 84–88 %. Now a whole-cluster flood (≤ 3000 cells; an
  unloaded neighbour or the cap = keep).
- **LC-1005-25 (witness) Terrain checks take the WORST column, and unread ground is never a yes.** The street profile
  judged the MEDIAN ground across the corridor (ridges passed with 20–40-block edges); slotRelief accepted plots whose
  ground was more than half unknown (the cliff-edge houses). Now: build up only over drops ≤ 15, stepped in lifts of 3
  (R5's retaining-wall rule), slide / other streets beyond that, stilts ≤ 24 as the last resort (his answers).

## R10 WATER (his 19:48 "everything we can control") — 20:1x CT, BDS-measured (waterprobe 0.0.1 / 0.0.2)
- **LC-1005-26 (BDS) Script/command `water` is INERT; `flowing_water` is LIVE; read-back is always `water`.** A source set by
  setPermutation or /setblock stayed one block for 200 ticks; partial levels (d3, d7, d8) held their shape until a
  neighbour changed. `flowing_water` d0 spread at once; d3 drained in 40 ticks. Any neighbour change wakes inert water
  (a poke, an adjacent water placement, a structure placed beside it); /fill water is always live. Use: inert water for
  fountains / moats / ponds that must never creep; live water only when we want the engine to find the level.
- **LC-1005-27 (BDS) A structure's air overwrites water; openings let it back.** Default structure placement into a flooded
  tank left a closed room 27/27 dry after 62 ticks; waterlogged:true filled it 27/27; an open-topped room refilled 35/35.
  A room drained with its doorway open refilled 44 cells in 60 ticks; sealed first, it stayed at 0. Drains go: seal,
  then one `/fill air replace water` (it takes every depth). The palace pump passes were fighting W3 + openings.
- **LC-1005-28 (BDS) Water flow costs the server nothing measurable; our scripts around it do.** 576 sources falling 22
  blocks: worst tick 61 ms vs 55 baseline; a 22-layer clear 89 ms. Spread 1 step / 5 ticks, reach 7, falling 5 t/block,
  infinite source only over solid ground, waterlogged blocks spread once woken, flowing water never waterlogs.

## ROUND 1005d (growth, sewers, lanes, the stalled builders) — 22:0x CT
- **LC-1005-29 (BDS census) Measure the frontage before redesigning the town.** A one-command census (every street, both sides,
  packed with one house, each refusal charged to its first rule) showed 26 % of street sides were legal frontage and 0
  positions free from village on — the stall was the kit's ramps / dead ends / reserved windows / hatch spacing, not the
  land alone. Houses on ramps + windows given back after 3 failed searches: town III 34 -> 76 plots on the same site.
- **LC-1005-30 (witness 21:51 + code) A gate that pauses the clock never tests the real-time path.** Real-day stages waited for
  a builder BODY within 6 blocks, and skipped days froze them; the BDS gate only skipped, so it passed while his towns stood
  as pits for 200+ days. Every mode he plays in (real time at his speed, skips) must be in the gate; work the town owes is
  done by the crew's numbers, bodies only add to it.
- **LC-1005-31 (BDS) QuickJS refuses a duplicate top-level name that node --check accepts** ("invalid redefinition of global
  identifier"): the whole pack fails to load. Every build runs tools/js_dupcheck.py.
- **LC-1005-32 (Mojang docs) A Bedrock add-on cannot shape the terrain** (custom biomes paint the surface; overworld_height is
  legacy, map colour only). Cities adapt: survey for gentle land, lanes on contours, hillside houses — never terraform.
