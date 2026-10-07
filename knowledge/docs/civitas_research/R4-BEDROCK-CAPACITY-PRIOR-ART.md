# R4 — Bedrock Capacity Limits & Settlement-Simulation Prior Art

**Scope:** engine capacity facts for a CIVITAS-class settlement simulation on Minecraft Bedrock (@minecraft/server 2.x era, game 1.21.80+; engine here reports 1.26.32, so the newest Learn docs are treated as applicable), plus prior art from Java mods and vanilla village generation, ending in proposed budgets and architecture.
**Date:** 2026-10-03.
**Reading key:** every paragraph is tagged either **[SOURCED]** (a URL backs the claim), **[INFERRED]** (my reading of sourced facts — needs a witness test before it becomes law), or **[PROPOSED]** (a rule I am recommending). Where two sources disagree, both numbers are given. Nothing below is witness-verified on our hardware; per P1, static facts only rule out, they never rule in.

---

## 1. Structure limits (`.mcstructure`, `/structure`, `structureManager.place`)

### 1.1 Size ceiling

**[SOURCED]** The Bedrock structure ceiling is **64 × 384 × 64** blocks (X × Y × Z). The wiki's Structure Block page states "The maximum structure size is 64×384×64" for Bedrock (Java is 48³) ([minecraft.wiki/Structure_Block](https://minecraft.wiki/w/Structure_Block)); the `/structure` command page lists the failure condition "The region is greater than 64 * 384 * 64" ([minecraft.wiki/Commands/structure](https://minecraft.wiki/w/Commands/structure)); Microsoft's structure-block tutorial says you can build "as long as it's smaller than 64 x 384 x 64 blocks" ([Learn: Introduction to Structure Blocks](https://learn.microsoft.com/en-us/minecraft/creator/documents/introductiontostructureblocks)). That is 1,572,864 block positions at the maximum.

**[SOURCED]** The old NBT-edit trick to exceed the limit (editing `xStructureSize`/`yStructureSize`/`zStructureSize`) "no longer works after 1.20.50 update"; the same page recommends "structure loading animations (Place by Block) when loading a huge structure" to reduce lag ([wiki.bedrock.dev/nbt/structure-limits](https://wiki.bedrock.dev/nbt/structure-limits)). The script API enforces the same cap: `StructureManager.createFromWorld` "Throws if the structure bounds exceed the maximum size" ([jaylydev StructureManager](https://jaylydev.github.io/scriptapi-docs/latest/classes/_minecraft_server.StructureManager.html)).

### 1.2 `StructurePlaceOptions` (stable docs)

**[SOURCED]** From [Learn: StructurePlaceOptions](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/structureplaceoptions?view=minecraft-bedrock-stable):

| Property | Type / default | Doc text |
|---|---|---|
| `animationMode` | `StructureAnimationMode` | "How the Structure should be animated when placed." (`/structure` exposes `block_by_block` and `layer_by_layer`) |
| `animationSeconds` | number | "How many seconds the animation should take." |
| `includeBlocks` | boolean, **true** | "Whether blocks should be included in the structure." |
| `includeEntities` | boolean, **true** | "Whether entities should be included in the structure." |
| `integrity` | number 0–1 | "A value of 1 will place 100% of the blocks while a value of 0 will place none. The blocks are chosen randomly based on the … integritySeed." |
| `integritySeed` | string, random | seed for the integrity selection |
| `mirror` | `StructureMirrorAxis.None` | "Which axes the Structure should be mirrored on when placed." |
| `rotation` | `AxisAlignedRotation.None` | "How the Structure should be rotated when placed." |
| `waterlogged` | boolean, **false** | "If true, blocks will become waterlogged when placed in water." |

**[SOURCED]** The `/structure load` command mirrors this: rotation `0_degrees/90_degrees/180_degrees/270_degrees`, mirror `x/z/xz/none`, animation `block_by_block|layer_by_layer`, `animationSeconds`, `includeEntities`, `includeBlocks`, `waterlogged`, integrity "between 0 and 100 (inclusive)", `seed` ([minecraft.wiki/Commands/structure](https://minecraft.wiki/w/Commands/structure)). Note the unit mismatch: command integrity is 0–100, script integrity is 0–1.

### 1.3 `StructureManager` surface and error contract

**[SOURCED]** From [Learn: StructureManager](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/structuremanager?view=minecraft-bedrock-stable) and the jaylydev mirror:

- `place(structure, dimension, location, options?) : void` — "**Structures placed in unloaded chunks will be queued for loading.**" Throws `ArgumentOutOfBoundsError` ("if the integrity value is outside of the range [0,1]"), `InvalidArgumentError` ("if the integrity seed is invalid"; "if the placement location contains blocks that are outside the world bounds"), `InvalidStructureError`. Not callable in restricted-execution (early-execution) mode.
- `createFromWorld(identifier, dimension, from, to, options?)` — "functionally equivalent to the /structure save command"; identifier "must include a namespace and must be unique".
- `createEmpty(identifier, size, saveMode = Memory)`, `delete`, `get`, `getPackStructureIds()` (behavior-pack structures only; added in module 2.8.0 per the [changelog](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/changelog?view=minecraft-bedrock-stable)), `getWorldStructureIds()` (world + memory only).
- `placeJigsaw(pool, targetJigsaw, maxDepth ∈ [1,20], …)` and `placeJigsawStructure(identifier, …)` return a `BlockBoundingBox`; both moved from beta to module 1.19.0 in game 1.21.80 ([minecraft.wiki/Bedrock_Edition_1.21.80](https://minecraft.wiki/w/Bedrock_Edition_1.21.80)).

**[SOURCED]** The `Structure` object exposes `size`, `getBlockPermutation(loc)`, `getIsWaterlogged(loc)`, `setBlockPermutation(loc, perm?, waterlogged = false)` ("Air and undefined blocks cannot be waterlogged"), `saveAs`, `saveToWorld` ([Learn: Structure](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/structure?view=minecraft-bedrock-stable)). The `waterlogged` parameter on `setBlockPermutation` arrived in 1.21.60 ([minecraft.wiki/Bedrock_Edition_1.21.60](https://minecraft.wiki/w/Bedrock_Edition_1.21.60)). This means CIVITAS can **edit a template in memory before placing it** (e.g., swap palette blocks per settlement culture, strip beds) without touching the world.

### 1.4 File format facts that matter for CIVITAS

**[SOURCED]** `.mcstructure` is uncompressed little-endian NBT with `format_version` (always 1), `size`, `structure_world_origin`, and `structure.block_indices` as **two layers** ("The secondary layer stores waterlogged blocks"; index −1 "indicates a void in the structure where no block exists"), a `palette` of block permutations, `block_position_data` carrying `block_entity_data` and `tick_queue_data`, and `entities` stored "in the same way as entities in the world file itself. Tags like Pos and UniqueID are saved, but replaced upon loading" ([wiki.bedrock.dev/nbt/mcstructure](https://wiki.bedrock.dev/nbt/mcstructure)).

**[INFERRED]** Consequences: (a) voids (−1) let a prefab leave existing terrain untouched where it has no block — a house template with void under its floor will not fill the slope, so CIVITAS must grade the plot itself; (b) entities inside a template are re-spawned fresh on every placement — never bake villagers into house templates or every placement doubles the population; (c) block entities (chests, signs) ride along — keep them minimal, each is a ticking/serialisation cost.

### 1.5 Pitfalls

- **[SOURCED]** Unloaded chunks: `/structure load` fails when "One or both specified regions are unloaded or out of the world" ([Commands/structure](https://minecraft.wiki/w/Commands/structure)); the script `place` instead **queues** the structure for when the chunk loads (above). Every block API throws `LocationInUnloadedChunkError` — "Thrown when the chunk for provided location or bounding area is not loaded" ([Learn: LocationInUnloadedChunkError](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/locationinunloadedchunkerror?view=minecraft-bedrock-stable)).
- **[SOURCED]** Performance: "Large clones, fills and structure loads during runtime should be avoided. Breaking these more extensive operations into multiple commands distributed over multiple ticks will avoid lag spikes, consider using structure loading animations." ([wiki.bedrock.dev/meta/addon-performance](https://wiki.bedrock.dev/meta/addon-performance))
- **[INFERRED]** `place()` returns `void` and the docs give no promise/callback, so for a loaded target the block writes happen inside the call (synchronous on the script thread); the animation modes are the only built-in way to spread a placement over time, and the queue-for-unloaded-chunk path is the only async behaviour. No source states the per-block cost; this needs a witness timing test (§6.5).

---

## 2. Script budgets

### 2.1 The watchdog

**[SOURCED — two sources disagree on defaults]**

| Property | wiki.bedrock.dev default | Learn (BDS server.properties) default | Meaning |
|---|---|---|---|
| `script-watchdog-enable` | true | true | master switch |
| `script-watchdog-hang-threshold` | **3000 ms** | **10000 ms** | "threshold for single tick hangs" |
| `script-watchdog-spike-threshold` | 100 ms | 100 ms | "threshold for single tick spikes" |
| `script-watchdog-slow-threshold` | **2 ms** | **10 ms** | "threshold for slow scripts over multiple ticks" |
| `script-watchdog-memory-warning` | 100 MB | 100 MB (0–2000) | content-log warning |
| `script-watchdog-memory-limit` | 250 MB | 250 MB (0–2000) | "Saves and shuts down the world when the combined script memory usage exceeds" it |
| `script-watchdog-hang-exception` | true | true | hang throws a critical exception |

Sources: [wiki.bedrock.dev/scripting/script-watchdog](https://wiki.bedrock.dev/scripting/script-watchdog), [Learn: Bedrock Dedicated Server Properties](https://learn.microsoft.com/en-us/minecraft/creator/documents/bedrockserver/server-properties?view=minecraft-bedrock-stable). The wiki also notes a hang "typically from loops" and that a memory-exceeded shutdown "cannot be canceled via BeforeWatchdogTerminateEvent", and that recursion without an exit point overflows the stack and "terminates the behavior pack" ([wiki.bedrock.dev/scripting/troubleshooting](https://wiki.bedrock.dev/scripting/troubleshooting)).

**[INFERRED]** On Realms, PS5 and Android these properties are not editable; assume the stricter wiki numbers (slow warnings at ~2 ms sustained, spike at 100 ms) as the design envelope. The "slow" threshold is the one CIVITAS will actually hit, since it is cumulative across ticks.

### 2.2 `system.runJob` is the engine's own throttle

**[SOURCED]** The System class: `runJob(generator)` "Queues a generator to run until completion. The generator will be given a time slice each tick, and will be run until it yields or completes." `run`, `runInterval`, `runTimeout`, `waitTicks` (min 1 tick), `currentTick`, and `serverSystemInfo` (device "memory tier") are also there ([Learn: System](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/system?view=minecraft-bedrock-stable)).

**[SOURCED]** Microsoft's system.run guide is the only official statement of relative throughput: "Hardware differences make matters even worse: what is performant on a PC may be slow on a mobile device or console." … "On a fast PC it may be able to do 30 block place operations, but on mobile that number drops to 5. A poorly authored generator function may perform 5 iterations on a fast PC, but on a mobile device it can only do 1—and that single operation triggers a watchdog warning." … "the job system will not starve your generators. At a minimum, every generator for every script behavior pack that has generators will be allowed to execute at least 1 iteration every tick." Recommended practice: yield after each discrete unit of work, keep work per iteration consistent so the scheduler can estimate, and make sure one iteration never exceeds the tick budget ([Learn: system.run guide](https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/system-run-guide?view=minecraft-bedrock-stable)).

**[INFERRED]** The 30-vs-5 figure is Microsoft's illustrative ratio (~6×) between a fast PC and a phone for *single-block setPermutation iterations per job time-slice*. PS5 sits between; treat it as ~3–4× a phone until measured. Because the guarantee is only "≥1 iteration per generator per tick", many concurrent jobs each get at least one iteration — N jobs can force N block edits per tick even when the device is struggling. CIVITAS should therefore run **one** master job (a scheduler generator) rather than spawning a job per building.

### 2.3 Bulk block APIs

**[SOURCED]** From [Learn: Dimension](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable):

- `fillBlocks(volume: BlockVolumeBase, block, options?: BlockFillOptions): ListBlockVolume` — returns "all the blocks that were placed"; throws `EngineError`, `Error`, `UnloadedChunksError`. `BlockFillOptions` = `{ blockFilter?: BlockFilter; ignoreChunkBoundErrors?: boolean }`, where `ignoreChunkBoundErrors` "will just fill the blocks that are inside the loaded chunk bounds and ignoring blocks outside" ([Learn: BlockFillOptions](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockfilloptions?view=minecraft-bedrock-stable)).
- `getBlocks(volume, options: BlockQueryOptions, allowUnloadedChunks = false): ListBlockVolume` — with `allowUnloadedChunks` it "Will only check the block locations that are within the loaded chunks in the volume."
- `containsBlock(volume, filter, allowUnloadedChunks)`, `getTopmostBlock(locationXZ, minHeight?)` (search starts at "the maximum dimension height" by default), `getBlock` (returns `undefined` or throws for unloaded chunks), `setBlockType`, `setBlockPermutation`, `spawnEntity` (throws `LocationInUnloadedChunkError`), `runCommand` (synchronous; `runCommandAsync` was removed in Scripting 2.0 — "use System.runJob instead" per [Learn: Scripting V2 overview](https://learn.microsoft.com/en-us/minecraft/creator/documents/scriptingv2.0.0overview?view=minecraft-bedrock-stable)).
- `BlockFilter` = `includeTypes/excludeTypes/includeTags/excludeTags/includePermutations/excludePermutations`; "If no include options are added it will select all blocks that are not rejected by the exclude options" ([Learn: BlockFilter](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockfilter?view=minecraft-bedrock-stable)).
- `BlockVolumeBase` offers `getCapacity()` ("W*D*H"), `getBlockLocationIterator()`, `getClosest/getFarthest(count, location)`, `isInside`, `translate`; **no size limit is documented** ([Learn: BlockVolumeBase](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockvolumebase?view=minecraft-bedrock-stable)).

**[SOURCED]** Neither Learn nor the jaylydev mirror documents a maximum block count for `fillBlocks`/`getBlocks`. The wiki's `/fill` page documents Java's old hard cap of 32,768 (now a gamerule) but "does not specify a maximum block limit for the /fill command in Bedrock Edition" ([minecraft.wiki/Commands/fill](https://minecraft.wiki/w/Commands/fill)). **[INFERRED]** The commonly quoted 32,768-block cap for Bedrock `/fill` is therefore unverified here; the script `fillBlocks` has no documented cap at all, which means the only limit is the watchdog — a 64×64×64 fill is 262,144 writes in one synchronous call and must be assumed to spike.

**[SOURCED]** Commands from script are explicitly slow: "it's slow to run a command from the Script API, and server performance starts to slow down as more commands are executed over time" ([wiki.bedrock.dev/scripting/script-server](https://wiki.bedrock.dev/scripting/script-server)); the performance page singles out per-tick `/effect` and `/gamemode` as having "a significant performance impact" ([addon-performance](https://wiki.bedrock.dev/meta/addon-performance)).

### 2.4 Dynamic properties

**[SOURCED]** Types: string, number (64-bit float), boolean, Vector3. "There is a length limit of 32,767 bytes for string dynamic properties" ([jaylydev Dynamic Properties](https://jaylydev.github.io/scriptapi-docs/features/dynamic-properties.html)); the Bedrock wiki phrases it as "a maximum of 32767 characters in length" ([script-server](https://wiki.bedrock.dev/scripting/script-server)). They "persist in a world's LevelDB database" keyed by the behavior-pack header UUID. `World.setDynamicProperty` throws `ArgumentOutOfBoundsError`; `getDynamicPropertyTotalByteCount()` exists so you can "ensure you're not storing gigantic sets of dynamic properties"; `getDynamicPropertyIds()`, `clearDynamicProperties()` ([Learn: World](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/world?view=minecraft-bedrock-stable)). Batch `setDynamicProperties` on World/Entity/ItemStack/ContainerSlot arrived in 1.21.60 ([Bedrock_Edition_1.21.60](https://minecraft.wiki/w/Bedrock_Edition_1.21.60)). Historically the string cap was 1,000 characters (creator issue #520 asked for it to be raised) ([MicrosoftDocs/minecraft-creator#520](https://github.com/MicrosoftDocs/minecraft-creator/issues/520)).

**[SOURCED]** **No total byte budget is documented anywhere** (Learn, jaylydev, wiki.bedrock.dev all silent). **[INFERRED]** The practical ceiling is the 250 MB script-memory limit plus LevelDB save time: every save serialises the whole property set, so the budget is a latency budget, not a hard cap. JSON.stringify of a 32 KB string costs ~ sub-millisecond on PS5 but is non-trivial on a phone when done every tick; batch writes per in-game day, not per tick.

### 2.5 Waterlogging in the script API (version facts)

**[SOURCED]** In 1.21.60 Mojang "Moved the following methods from beta to 1.17.0: Block::isWaterlogged, Block::setWaterlogged", "Added enum LiquidType { Water = 'Water' }", and added (beta then) `canBeDestroyedByLiquidSpread`, `isLiquidBlocking`, `liquidSpreadCausesSpawn`, `liquidCanFlowFromDirection`; `minecraft:liquid_detection` left the experiment "for format_versions 1.21.60 and above" ([Bedrock_Edition_1.21.60](https://minecraft.wiki/w/Bedrock_Edition_1.21.60)). The current stable Block page lists `isWaterlogged` (property), `setWaterlogged(bool)`, `canContainLiquid(LiquidType)` ("whether this block can have a liquid placed over it (i.e., be waterlogged)"), `isLiquidBlocking`, `liquidCanFlowFromDirection`, `liquidSpreadCausesSpawn`, `canBeDestroyedByLiquidSpread`, all throwing `LocationInUnloadedChunkError` ([Learn: Block](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/block?view=minecraft-bedrock-stable)).

**[SOURCED]** For our custom blocks, `minecraft:liquid_detection` (format 1.21.60+) has `detection_rules[]` with `liquid_type` (only `water`), `can_contain_liquid` (default false → waterloggable), `on_liquid_touches` (`blocking` default | `broken` | `popped` | `no_reaction`), `stops_liquid_flowing_from_direction[]`, `use_liquid_clipping` (default changed to false at 1.26.0); an empty `detection_rules` array is a content error from 1.26.10 ([Learn: minecraft:liquid_detection](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_liquid_detection?view=minecraft-bedrock-stable)).

**[SOURCED]** Does flowing water pass through iron bars and fences on Bedrock? The wiki: "In Bedrock Edition, generally all non-cube blocks can be waterlogged and none can be used to displace water source blocks, although they can still displace flowing water" and "waterlogging is handled by the game's layers system"; its table marks fences, iron bars, glass panes, stairs and slabs as able to hold water in Bedrock, and shows Bedrock's waterlogged blocks letting flowing water pass through ([minecraft.wiki/Waterlogging](https://minecraft.wiki/w/Waterlogging)). **[INFERRED]** So on Bedrock an iron-bar drain grate or fence culvert does **not** stop flowing water the way it does on Java; to keep water out of a tunnel we need a full cube or a custom block whose `liquid_detection` rule is `blocking` with `can_contain_liquid: false` — witness-test both before relying on it.

---

## 3. Chunk loading, ticking and time

### 3.1 Simulation distance

**[SOURCED]** Microsoft's guide: simulation distance "Default: Always 4 chunks", "up to 12 chunks (device-dependent)", always ≤ render distance; render distance on Realms "Typically maximum of 20 chunks" ([Learn: Simulation/Render distance guide](https://learn.microsoft.com/en-us/minecraft/creator/documents/simulationrenderdistanceguide?view=minecraft-bedrock-stable)). The wiki: "Even number ranging from 4 to 12, 4 in default" for singleplayer, "Integer ranging from 4 to 12, 4 in default" for multiplayer; it governs "mob spawning and despawning, and tick updates" and uses taxicab distance (a square) ([minecraft.wiki/Simulation_distance](https://minecraft.wiki/w/Simulation_distance)). The Fandom mirror adds "Realms worlds use a simulation distance of … 4 chunks in Bedrock Edition" and that at sim 4 mobs spawn 24–44 blocks away ([Fandom Simulation_distance](https://minecraft.fandom.com/wiki/Simulation_distance)). BDS exposes it as `tick-distance` (default 4, range 4–12, "Higher values have a performance impact") ([Learn: BDS properties](https://learn.microsoft.com/en-us/minecraft/creator/documents/bedrockserver/server-properties?view=minecraft-bedrock-stable)).

**[INFERRED]** Arithmetic: sim 4 ⇒ a 9×9-chunk square = **81 loaded, ticking chunks = 144 × 144 blocks** per player; sim 6 ⇒ 169 chunks; sim 8 ⇒ 289; sim 12 ⇒ 625. On a Realm (fixed at 4) a city of 1,000 buildings is mostly *not* ticking at any moment — this is the single most important design constraint.

### 3.2 What stops outside simulation distance

**[SOURCED]** Microsoft's guide: outside simulation distance entity AI, mob spawning ("including summoned mobs"), plant growth and fluid movement stop; "Redstone circuits function regardless of simulation distance" (the guide's own claim); persistent entities "won't despawn if marked with minecraft:persistent"; in ticking areas "Mobs may despawn but won't spawn unless a player is within simulation distance", and moving entities "stop moving if they exit ticking areas and aren't within simulation distance" ([Learn: Simulation/Render distance guide](https://learn.microsoft.com/en-us/minecraft/creator/documents/simulationrenderdistanceguide?view=minecraft-bedrock-stable)). The older ticking-area intro says the opposite about spawning ("crops grow, mobs spawn, and command blocks function as intended") ([Learn: Introduction to Ticking Areas](https://learn.microsoft.com/en-us/minecraft/creator/documents/tickingareacommand)) — conflicting; witness test if CIVITAS ever relies on spawns inside a ticking area.

### 3.3 Ticking areas and chunk loaders

**[SOURCED]** "Up to 10 ticking areas can be defined at one time"; an area "larger than 100 chunks" fails; circle radius "must be from 0 to 4" chunks; `preload` areas load before other chunks at world launch ([minecraft.wiki/Commands/tickingarea](https://minecraft.wiki/w/Commands/tickingarea); [Learn guide](https://learn.microsoft.com/en-us/minecraft/creator/documents/simulationrenderdistanceguide?view=minecraft-bedrock-stable) gives 10 × 100 = 1,000 chunks max). Since 1.18.30 "Entities must now be loaded for an area to be considered fully loaded and ticking" ([feedback.minecraft.net 1.18.30](https://feedback.minecraft.net/hc/en-us/articles/5520890863245-Minecraft-1-18-30-Bedrock)).

**[SOURCED]** The entity component `minecraft:tick_world` is an alternative loader not subject to the command's 10-area cap: "there can only be 10 loaded areas that can be created through that command. minecraft:tick_world does not suffer from this, and so there can be more than 10 areas, provided your device can handle it"; the open-source loader cycles radii of 2–6 chunks and warns "Do NOT add too many of these, it will lag your game" and that spawner/golem farms needing a nearby player still won't work ([cda94581/open-source-chunk-loaders README](https://github.com/cda94581/open-source-chunk-loaders/blob/main/README.md)).

**[INFERRED]** A 100-chunk ticking area is only ~160 × 160 blocks — one neighbourhood. Keeping a whole city ticking is impossible on Realms by design; CIVITAS must be built so that **nothing needs to tick when nobody is there**.

### 3.4 Scripts cannot touch unloaded chunks (yes, confirmed)

**[SOURCED]** `getBlock` returns `undefined` or throws `LocationInUnloadedChunkError`; `setBlockType/Permutation`, `spawnEntity`, every `Block` navigation method (`above/below/north/offset`) and the liquid queries all throw it; `fillBlocks/getBlocks/containsBlock` throw `UnloadedChunksError` unless told to ignore; `Entity.tryTeleport` "can fail if the destination chunk is unloaded" ([Learn: Dimension](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable), [Learn: Block](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/block?view=minecraft-bedrock-stable), [Learn: Entity](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable)). The one exception is `structureManager.place`, which queues (§1.3).

### 3.5 Time

**[SOURCED]** 24,000 ticks per day = 20 real minutes = **3 in-game days per real hour**; Bedrock markers: day 0, noon 6000, sunset 12000, night 13000, midnight 18000, sunrise 23000; Bedrock villagers "begin their workday" at 0, "begin socializing" at 8000, "go to their beds and sleep" at 12000 ([minecraft.wiki/Daylight_cycle](https://minecraft.wiki/w/Daylight_cycle)). `/time query daytime|gametime|day` returns ticks since sunrise, total game ticks, and elapsed days; `/time set day` = 1000 ([minecraft.wiki/Commands/time](https://minecraft.wiki/w/Commands/time)). Script equivalents: `world.getAbsoluteTime()` ("absolute time since the start of the world (in ticks)"), `getTimeOfDay()` 0–24000, `getDay()` ("world time divided by the number of ticks per day", starting at day 0) ([Learn: World](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/world?view=minecraft-bedrock-stable)).

**[INFERRED]** "Hundreds of in-game days" = 100 days ≈ 33 real hours of play with the area loaded. Absolute time keeps advancing while a chunk is unloaded, so **elapsed-day catch-up must be computed from `getAbsoluteTime()` deltas, never from ticks the script observed.**

---

## 4. Villagers, pathfinding, entities, spawning

### 4.1 `minecraft:navigation.walk` (all parameters)

**[SOURCED]** ([Learn: navigation.walk](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_navigation.walk?view=minecraft-bedrock-stable)) `avoid_damage_blocks` (false), `avoid_portals` (false), `avoid_sun` (false), `avoid_water` (false), `blocks_to_avoid` (list of block descriptors), `can_breach` (false), `can_break_doors` (false), `can_float`, `can_jump` (**true**, "whether or not it can jump up blocks"), `can_open_doors` (false), `can_open_iron_doors` (false), `can_pass_doors` (**true**), `can_path_from_air` (false), `can_path_over_lava` (false), `can_path_over_water` (false, "travel on the surface of the water"), `can_sink` (true), `can_swim` (false), `can_walk` (**true**), `can_walk_in_lava` (false), `is_amphibious` (false, "walk on the ground underwater"). From script these are **all read-only** on `EntityNavigationComponent`, and "The provided documentation contains no methods for setting a navigation target" ([Learn: EntityNavigationComponent](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entitynavigationcomponent?view=minecraft-bedrock-stable)).

### 4.2 Stairs, slabs, ramps, custom collision

**[SOURCED]** Bedrock villagers path by cost: they "prefer low-cost blocks like dirt paths, cobblestone, bricks, and planks", adults have a jump cost of 20 vs 5 for babies, they "can open all wooden and copper doors" but not trapdoors, fence gates or iron doors, and "can climb ladders, but do not recognize them as paths and do not deliberately use them" ([minecraft.wiki/Villager](https://minecraft.wiki/w/Villager)). Villagers "cannot pathfind when stuck in a 1×1 space, or mounted in a vehicle" ([minecraft.wiki/Village_mechanics](https://minecraft.wiki/w/Village_mechanics)). The Mojang tracker has a long-lived Bedrock issue titled "Mobs Won't Pathfind Over Short Blocks (Slabs …)" ([MCPE-47075](https://bugs-legacy.mojang.com/browse/MCPE-47075?attachmentOrder=asc)) and "Mobs Fail To Pathfind Through/Past multiple blocks" ([MCPE-46805](https://bugs-legacy.mojang.com/browse/MCPE-46805?attachmentSortBy=dateTime)) — the tracker refused automated fetch, so only the titles are confirmed here. The same algorithmic trap appears in TekTopia: a half slab next to stairs makes the pathfinder think "they can path up" and villagers jump forever because "the pathing algorithm treats half slabs as full-height blocks" ([TekTopia issue #652](https://github.com/TangoTek/TekTopia-Community/issues/652)).

**[SOURCED]** Custom blocks declare `minecraft:collision_box` (origin −8..8 / 0..24, size up to 16×24×16, or `false` to let entities pass; format ≥ 1.19.50); the reference says nothing about pathfinding ([Learn: minecraft:collision_box](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_collision_box?view=minecraft-bedrock-stable)). **[INFERRED]** No official source says whether the navigator reads a custom block's collision box or its full-cube default. Given the slab bug above, assume the pathfinder treats any non-full custom collision as either a full block or an obstacle until witnessed. For street ramps: full-block steps with `can_jump` (jump cost 20) are the only configuration that is documented to work; stair blocks are a witness-test item, custom sloped blocks are a second one (§6.5).

### 4.3 Data-driven movement goals usable by CIVITAS

**[SOURCED]**
- `minecraft:behavior.move_to_block`: `target_blocks[]`, `search_range` (0), `search_height` (1), `goal_radius` (0.5), `on_reach`, `on_stay_completed`, `stay_duration` (ticks), `target_offset`, `target_selection_method` (`nearest|random`), `start_chance` (1), `tick_interval` (20), `speed_multiplier` ([Learn: move_to_block](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_to_block?view=minecraft-bedrock-stable)).
- `minecraft:behavior.move_towards_target`: `within_radius` (0 = same block), `speed_multiplier`, `control_flags`; iron golem uses radius 32 ([Learn: move_towards_target](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_towards_target?view=minecraft-bedrock-stable)).
- `minecraft:behavior.move_to_poi`: `poi_type` ∈ `bed | jobsite | meeting_area` ([Learn: move_to_poi](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_to_poi?view=minecraft-bedrock-stable)).
- `minecraft:dweller`: `dwelling_type` ("village"), `dwelling_role` ("inhabitant, defender, hostile, passive"), `can_find_poi`, `can_migrate`, `dwelling_bounds_tolerance`, `first_founding_reward`, `preferred_profession`, `update_interval_base/variant` ([Learn: dweller](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_dweller?view=minecraft-bedrock-stable)). The Bedrock wiki's village-mechanic page shows the villager pattern: `minecraft:scheduler` with `hourly_clock_time` filters ("Morning (0-12000) triggers work; evening (21000-24000) triggers gathering"), `behavior.work` with `on_arrival`, `behavior.sleep` + `behavior.hide`, `behavior.move_indoors`, `behavior.move_towards_dwelling_restriction`, `behavior.mingle` ([wiki.bedrock.dev/entities/village-mechanic](https://wiki.bedrock.dev/entities/village-mechanic)). A custom entity can sleep in a bed with `minecraft:dweller` ("Undocumented, needed for entity to be able to sleep"), `behavior.sleep`, an `environment_sensor` on `is_daytime`, and ordinary navigation components ([wiki.bedrock.dev/entities/sleeping-entities](https://wiki.bedrock.dev/entities/sleeping-entities)); `behavior.sleep` exposes `cooldown_time`, `timeout_cooldown` (8 s), `sleep_collider_*`, `sleep_y_offset` ([Learn: behavior.sleep](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_sleep?view=minecraft-bedrock-stable)).
- The Bedrock wiki's long-range trick: give the mob an aggressive/targeting behavior aimed at a dummy marker entity placed at the destination, "allowing really long-range pathing" ([wiki.bedrock.dev/entities/entity-movement](https://wiki.bedrock.dev/entities/entity-movement)).

**[SOURCED]** Script-side movement is limited to `teleport(location, TeleportOptions)`, `tryTeleport(...) : boolean` ("can fail if the destination chunk is unloaded or if the teleport would result in intersecting with blocks"), `applyImpulse`, `applyKnockback`, `clearVelocity`, `triggerEvent` (component-group switching), `remove()` ([Learn: Entity](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable)); `TeleportOptions` = `checkForBlocks`, `dimension`, `facingLocation`, `keepVelocity`, `rotation`, `forceProvidedPositionOnDimensionChange` ([Learn: TeleportOptions](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/teleportoptions?view=minecraft-bedrock-stable)).

### 4.4 Vanilla village geometry (what the engine is tuned for)

**[SOURCED]** A Bedrock village starts as a "64.0m x 24.0m x 64.0m boundary" around the first claimed bed ("32 blocks in all horizontal directions and 12 blocks vertically"), can expand "an additional range of 32 blocks horizontally and 52 blocks vertically", two villages must be "at least 33 blocks away horizontally or 53 blocks vertically", each villager has "three slots" (bed, bell, job site), and iron golems need "at least 20 beds and at least 10 villagers", 75 % having worked that day, spawning in a 17×13×17 volume about "once every 35 seconds" ([minecraft.wiki/Village_mechanics](https://minecraft.wiki/w/Village_mechanics)). **[INFERRED]** The whole village subsystem is scoped to a ~130-block box; nothing in vanilla expects a villager to walk 400 blocks to work. CIVITAS districts should respect that scale per "virtual village".

### 4.5 Entity counts and despawn rules

**[SOURCED]** "Loaded entities at any given time should be minimized. Below 30 is optimal." Flying pathfinding "has a significant performance cost"; villager trade lists "cause performance issues and even crashes … at 60 trades or greater", "30 trades is a good safe number" ([wiki.bedrock.dev/meta/addon-performance](https://wiki.bedrock.dev/meta/addon-performance)). Standard despawn (`minecraft:despawn`): `despawn_from_distance.min_distance` 32 / `max_distance` 128, `min_range_inactivity_timer` 30 s, `min_range_random_chance` 800, `despawn_from_simulation_edge` true; a `filters` block replaces the standard rules ([Learn: minecraft:despawn](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_despawn?view=minecraft-bedrock-stable)). Vanilla Bedrock: mobs despawn instantly "in a chunk at the edge of simulation distance, or … more than 128 blocks from the nearest player", and beyond 32 blocks "have a 1 in 800 chance to despawn on each game tick if they have not taken damage for 30 seconds" ([Fandom: Spawn](https://minecraft.fandom.com/wiki/Spawn)). "Whether in a village or not, a villager never despawns" ([minecraft.wiki/Villager](https://minecraft.wiki/w/Villager)); `minecraft:persistent {}` makes any custom entity immune ([Learn guide](https://learn.microsoft.com/en-us/minecraft/creator/documents/simulationrenderdistanceguide?view=minecraft-bedrock-stable)). **[INFERRED]** Name-tag persistence is folk knowledge not fetched here; for CIVITAS citizens use `minecraft:persistent` (or simply omit `minecraft:despawn`) and never rely on name tags.

### 4.6 Hostile spawning in tunnels and enclosed spaces

**[SOURCED]** Bedrock: "Most overworld monsters cannot spawn if the sky light level is greater than or equal to 7 **or the block light level is greater than 0**"; spawning has "a 1⁄2000 chance of the mob spawning algorithm attempting to run per chunk, per tick"; at simulation distance 4 mobs spawn "between 24 and 44 blocks spherical radius from the player", at 6+ "between 24 and 128"; global cap 200; density is "calculated based on the 9 chunk x 9 chunk square area"; "There must be a block with a full, solid top surface under the spawn location" and mobs "cannot spawn on transparent full blocks like glass and leaves" ([Fandom: Spawn](https://minecraft.fandom.com/wiki/Spawn)). A community compilation adds "Cannot spawn on slabs or carpet", "Cannot spawn on bedrock or invisible bedrock", "Cannot spawn if the block below them is air" (its light figure, ≤7, predates 1.18.30) ([yonta gist](https://gist.github.com/yonta/ce7c7e17a78777655cc5d61f60092216)). The vanilla zombie rule is `brightness_filter {min 0, max 7, adjust_for_weather true}` with `herd 2–4` and a `has_biome_tag monster` filter ([Learn: zombie spawn_rule](https://learn.microsoft.com/en-us/minecraft/creator/reference/source/vanillabehaviorpack_snippets/spawn_rules/zombie?view=minecraft-bedrock-stable)); `brightness_filter` ranges 0–15 and `adjust_for_weather` lowers light in rain/thunder ([Learn: spawn_brightnessfilter](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/spawnrulesreference/examples/spawnrulescomponents/spawn_brightnessfilter?view=minecraft-bedrock-stable)); other components: `density_limit {surface, underground}`, `spawns_on_block_filter`, `spawns_on_block_prevented_filter`, `distance_filter {min 24, max 128}`, `height_filter`, `player_in_village_filter` ([Learn: spawn rules](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/spawnrulesreference/examples/spawnrulescomponents/spawn_rules?view=minecraft-bedrock-stable)).

**[PROPOSED]** Tunnel rule for CIVITAS: every tunnel/cellar floor gets **block light ≥ 1** (any light source every ≤ 13 blocks, since light falls 1 per block from 15) **or** a non-full top surface (bottom slab, carpet, our own custom floor block with a sub-full collision box — the latter needs a witness test since spawn validity on custom blocks is undocumented). Belt and braces: both.

---

## 5. Prior art — how others grow settlements

### 5.1 MineColonies (Java, Forge/Fabric)

**[SOURCED]** Founding "claims the surrounding chunks and spawns your first four citizens" ([minecraft-guides: MineColonies](https://www.minecraft-guides.com/mod/minecolonies/)); one guide quotes the default claim as "a 200x200 block area" ([gurugamer guide](https://gurugamer.com/pc-console/a-complete-guide-to-play-minecraft-minecolonies-mod-24564)). Construction pipeline (from the code-derived wiki): work orders are BUILD / UPGRADE / REPAIR / REMOVE; the builder walks `BuildingProgressStage`s **CLEAR → BUILD_SOLID → WEAK_SOLID → CLEAR_WATER → CLEAR_NON_SOLIDS → DECORATE → SPAWN** ("stages progress from clearing to building solid blocks, then decorations, and finally entity spawning"); iteration is a "Standard spiral pattern from center" or "layered" (Y-level) for miners; missing items go to a `BuildingResourcesModule` that raises colony requests and the builder "waits in NEEDS_ITEM state until deliveries arrive"; progress persists as `progressPos`/`progressStage` so a build resumes after interruption; the hut "Purges mobs from build site at level 4+" ([deepwiki: Work Orders and Structure Building](https://deepwiki.com/ldtteam/minecolonies/2.5-work-orders-and-structure-building)). Terrain is handled by schematic placeholders: the plain placeholder is "keep what is already here", the **Solid Placeholder** is "mostly used for foundations of buildings, these will place a solid block in case there is a non solid block there" (keeps existing solids, fills air/fluids), and the Fluid Placeholder places the dimension's fluid ([minecolonies.com Placeholder Blocks](https://minecolonies.com/wiki/items/placeholderblocks/)). A Structurize issue shows the sharp edge: fences and cobwebs counted as "solid", so wall torches on placeholders failed and "miners and builders get stuck trying to place hanging blocks on unsupportable surfaces" ([ldtteam/Structurize#427](https://github.com/ldtteam/Structurize/issues/427)). Builders "collect most blocks they remove", but "some blocks (e.g., ore blocks and glass) will be lost"; the builder's range is "100 blocks from their hut"; "The Builder can ONLY upgrade other huts to the level of their Builder's Hut" ([wiki.minecolonies.com Builder](https://wiki.minecolonies.com/source/workers/builder)). Logistics: "Couriers move items between the Warehouse and other buildings"; research at the University gates "a large share of the mod's buildings and upgrades" ([minecraft-guides](https://www.minecraft-guides.com/mod/minecolonies/)). Failure modes documented: stuck builders (recall button), racks that "clog with dug dirt and junk", and "Builders are slow at clearing terrain on their own. Digging out the building site yourself dramatically speeds up early construction" ([minecraft-guides](https://www.minecraft-guides.com/mod/minecolonies/)). Pacing complaint: players "done with the mod pack before I get more than 4-5 buildings past level 2" because every hut must climb 1→5 sequentially ([minecolonies-features#876](https://github.com/ldtteam/minecolonies-features/issues/876)).

**Lessons for CIVITAS:** (1) the clear-then-solid-then-decor staging is exactly the order that avoids floating torches and pop-offs on Bedrock too; (2) persist `(stage, index)` per build so a chunk unload mid-build resumes cleanly; (3) do not level outside the footprint — fill under with a "solid substitution" rule, keep what is already solid; (4) a sequential 1→5 per building is a known fun-killer; let CIVITAS skip tiers when the economy affords it.

### 5.2 Millénaire (Java)

**[SOURCED]** Villagers do real work with real inventories: "Miners will go to their mines and dig throughout the day", "lumberjacks will chop down trees, replant the saplings, and deliver their wood to the town hall"; construction is live — "The villagers will chop down any trees in the way, flatten the land out, and then build the structure, all in real-time"; the economy uses "denier, a currency that comes in bronze, silver, and gold varieties"; cost: "towns can generate a fair amount of lag … issues with their frame rate" and "a number of bugs … most glitches can be solved by reloading your world" ([HubPages: Mod Examination: Millenaire](https://discover.hubpages.com/games-hobbies/Minecraft-Mod-Examination-Millenaire)). Village definitions name a `centre` building plan and assign building priority tiers "core: … primary building goals, to be built before any other buildings", "secondary: … built after the core buildings", and extras; "Which building is to be built will be decided based on the priority system within the group" ([millenaire.org: Guide on making Custom Villages](https://millenaire.org/wiki/Guide_on_making_Custom_Villages)). The village "collects resources on its own, develops the village itself with those resources, trades with players"; players "can increase the development speed of the village by providing resources"; and a player-built house "is not recognized by the residents as a house and is treated as an 'unauthorized building (obstacle)'" ([namu.wiki: Millénaire](https://en.namu.wiki/w/Mill%C3%A9naire)). Villages field "men, women and children", "couples have children who grow up into new adults", and newer versions add player-placed buildings with a ghost preview plus "walls and paths connecting settlements" ([millenaire.org](https://www.millenaire.org/)).

**Lessons:** priority tiers (core/secondary/extra) are a clean growth pacer; real resource flow makes growth legible but costs AI time — on Bedrock, model the inventory in script, not as item entities; treat player builds inside the boundary as obstacles explicitly (or claim them) to avoid the "unauthorized building" confusion.

### 5.3 TekTopia (Java, 1.12)

**[SOURCED]** The mod does not build: "You build the village and your villagers adapt to your designs!" with "over 20 different villager professions" and a claim of "100+ villagers all working in harmony" ([CurseForge: TekTopia](https://www.curseforge.com/minecraft/mc-mods/tektopia)). Structures are recognised from player builds: "you'll need to have a wooden door with an item frame placed above it or adjacent to its top. Inside that item frame you'll place the structure marker"; the Town Hall "is the center point of your village"; Storage "is the heart of the city and all villagers will visit it many times a day"; new villagers arrive "by converting wandering nomads or by raising your own children" ([TekTopia wiki: Getting Started](https://sites.google.com/view/tektopia/home/getting-started)); a new Town Hall "must be at least 400 blocks from the nearest existing Town Hall" and storage should be central "to minimize the walking" ([TekTopia wiki: The Basics](https://sites.google.com/view/tektopia/home/guides/the-basics)). Known pathing bug with slabs + stairs (§4.2).

**Lessons:** recognition-by-marker is cheap and robust (CIVITAS can use a marker block or a dynamic-property record instead of scanning geometry); walking distance to a central depot is the dominant AI cost — keep depots per district.

### 5.4 Minecraft Comes Alive (Java)

**[NOT FETCHED]** The MCA Reborn wiki returned HTTP 402 to automated fetch, so no claims about its Blueprint/building-recognition system are made here; treat MCA as a hypothesis source only (its model is, like TekTopia's, player-built housing scanned into "buildings" with bed-limited population — unverified).

### 5.5 Vanilla village generation (Java and Bedrock)

**[SOURCED]** Villages are jigsaw structures. Terrain handling: when buildings generate over air, "circular or square platforms of grass or sand (depending on the terrain) generates below the structure", platforms do not form near cliffs or voids and instead "generate on the lowest blocks"; "Village paths generate at the level of existing terrain, potentially going up steep hills or down ravines"; "Paths do not go below one level of water" and over water they become planks of the village wood; "Villages are slightly more common in Bedrock Edition" and "can generate in more biomes in Bedrock Edition" ([minecraft.wiki/Village](https://minecraft.wiki/w/Village)). Pool elements are `rigid` ("place a fixed structure (like a house)") or `terrain_matching` ("match the terrain height (like a village road)") ([Fandom: Custom structure](https://minecraft.fandom.com/wiki/Custom_structure)); for terrain-matched pieces "each column of blocks is adjusted in height [to] match the terrain" ([minecraft.wiki/Jigsaw_structure](https://minecraft.wiki/w/Jigsaw_structure)). Bedrock's `minecraft:jigsaw_structure` documents `terrain_adaptation` exactly: `none` ("Do not adjust ambient block density"), `bury`, `beard_thin` ("Ambient block density is added below the structure and block density is reduced just above the ground"), `beard_box`, `encapsulate` ("added all around every piece"); `heightmap_projection` ∈ `none | world_surface | ocean_floor`; `max_depth` default 7 (1–20); `liquid_settings` `apply_waterlogging | ignore_waterlogging`; `dimension_padding` ([Learn: minecraft:jigsaw_structure](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/worldgenreference/examples/jigsawjigsawstructurejson?view=minecraft-bedrock-stable)); the Bedrock wiki summarises `beard_thin` as "places a platform around the base like villages" ([wiki.bedrock.dev/world-generation/jigsaw-structures](https://wiki.bedrock.dev/world-generation/jigsaw-structures)).

**[INFERRED]** Two things vanilla does that CIVITAS can copy cheaply: houses are **rigid** (one Y per piece, platform/beard under), roads are **terrain-matched** (per-column Y). And one thing vanilla gets away with that CIVITAS cannot: `terrain_adaptation` runs inside worldgen's density field at chunk-generation time — the script `placeJigsawStructure` on already-generated terrain gives us the pieces but **not** the beard (unverified; witness test §6.5).

### 5.6 A Bedrock add-on that grows towns

**[SOURCED]** "Villagers can build villages" (CurseForge, Bedrock) describes automatic construction of farms, granaries, workshops and a Communal Center: "Construction first searches for usable terrain and can adapt moderately uneven natural ground"; "Important structures can progressively search farther away if nearby terrain is unsuitable"; when land is inadequate "compatible structures can use wooden maritime platforms instead"; "Workers are selected for construction tasks and travel toward projects before construction is completed"; farms start with "a small number of crops … leaving the farmers themselves responsible for developing and filling the field over time" ([CurseForge: Villagers can build villages](https://www.curseforge.com/minecraft-bedrock/addons/villagers-can-build-villages)). No performance numbers are published.

**Lesson:** on Bedrock, a working design already exists that (a) searches outward for flat-enough land instead of grading hard, (b) falls back to platforms (stilts) over water, (c) makes a worker walk to the site before the prefab appears — which is precisely the "teleport-when-unseen, walk-when-seen" illusion CIVITAS wants.

### 5.7 Cross-cutting failure modes

| Failure | Seen in | Bedrock analogue |
|---|---|---|
| Builder stuck / unreachable site | MineColonies (100-block range, recall button) | Navigation has no script target; a citizen that cannot reach a plot must be teleported or the plot re-sited |
| Floating decor / hanging blocks on bad supports | Structurize #427 | Stage placement (solid before decor); never put torches on custom-collision blocks |
| Slab/stair jump loops | TekTopia #652, MCPE-47075 | Full-block steps for roads; stairs only after witness test |
| Village lag from many AI villagers | Millénaire | "Below 30 is optimal" — embody few, simulate many |
| Player builds treated as obstacles | Millénaire | Claim or fence off player builds inside district bounds |
| Grind from sequential tiers | MineColonies #876 | Allow tier-skipping when resources permit |

---

## 6. PROPOSALS for CIVITAS

Everything in this section is **[PROPOSED]** unless marked otherwise; the numbers are design targets derived from the sourced ratios above and must be confirmed by witness timing on PS5 and the phone.

### 6.1 Budget table

| Resource | Android (phone host) | PS5 / Realm server | BDS on laptop | Why |
|---|---|---|---|---|
| Script time per tick (steady state) | ≤ 1.0 ms | ≤ 2.0 ms | ≤ 4.0 ms | stays under both candidate "slow" thresholds (2 ms wiki / 10 ms BDS) |
| Single-block edits per tick (all jobs) | **≤ 40** | **≤ 120** | ≤ 250 | MS ratio 5 : 30 phone : PC; PS5 ~ 3–4× phone |
| `fillBlocks` per tick | 1 call, ≤ 512 blocks (8×8×8) | 1 call, ≤ 2,048 blocks | 1 call, ≤ 4,096 | no documented cap, so self-cap to a spike-safe size |
| `structureManager.place` per tick | ≤ 1, piece ≤ 12×12×12 (1,728) | ≤ 1, piece ≤ 16×16×16 (4,096) | ≤ 1, ≤ 24³ | place is synchronous; 1 per tick spreads cost |
| Large pieces (> cap) | `layer_by_layer`, ≥ 3 s | `layer_by_layer`, ≥ 2 s | same | "consider using structure loading animations" |
| `getTopmostBlock` samples per tick | ≤ 32 | ≤ 128 | ≤ 256 | heightmap sampling for plot search |
| `getBlocks` scan per tick | ≤ 1 volume ≤ 16×16×8 | ≤ 1 volume ≤ 16×16×16 | same | runs synchronously |
| Embodied (spawned) citizens near a player | **≤ 24** | **≤ 48** | ≤ 64 | "Below 30 is optimal"; PS5 headroom |
| Total entities in the player's sim square | ≤ 60 | ≤ 120 | ≤ 160 | includes animals, items, golems |
| `runCommand` per tick | 0 (≤ 1 on events) | 0 (≤ 1) | ≤ 2 | commands are slow |
| Dynamic-property string size | ≤ 24,000 B each (margin under 32,767) | same | same | documented per-string cap |
| Dynamic-property total (world) | ≤ 1 MB target / 4 MB hard | ≤ 2 MB / 8 MB | ≤ 4 MB / 16 MB | no documented cap; LevelDB save latency |
| DP write cadence | once per in-game hour (1,000 ticks) per shard + on dirty flush | same | same | avoid per-tick JSON |
| Block entities per building | ≤ 2 (one chest, one sign) | ≤ 3 | ≤ 4 | block entities serialise and tick |
| Village-mechanic radius per district | 64 × 24 × 64 initial, ≤ 128 wide | same | same | vanilla's own bounds |

Record sizing (arithmetic verified): 2,000 buildings × ~150 B ≈ 293 KB; 10,000 street pieces × 24 B ≈ 235 KB; a 24 KB shard holds ~160 building records at 150 B — so a 2,000-building city is ~13 building shards plus ~10 street shards. Throughput: 120 edits/tick = 2,400 blocks/s, so a 4,096-block house platform+shell takes ~1.7 s of exclusive budget on PS5, ~8.5 s on the phone (40/tick). Over one in-game day (1,200 s) the PS5 budget alone could grade and place ~700 small houses *if the chunks were loaded* — construction throughput is not the bottleneck, loaded-area is.

### 6.2 Architecture: "work only in loaded chunks, with catch-up"

**Two simulations, one clock.**

1. **Macro-sim (abstract, world-wide, no block access).** Settlement state lives in dynamic-property shards: population, stockpiles, treasury, a build queue, and per-cell `lastMaterialisedDay`. It advances on a `system.runInterval` every 200 ticks (10 s) using `world.getAbsoluteTime()` deltas, so it is correct whether or not any chunk is loaded. It decides *what* exists (house #1472 is "built", street piece #9000 is "paved") and never touches blocks.
2. **Micro-sim (physical, only in loaded cells).** The world is partitioned into 16×16 **cells** aligned to chunks. Each cell record stores `materialisedVersion` and a small list of pending physical ops (grade plot, place piece, pave, light). A single master `system.runJob` generator loops: pick the next cell from a priority queue ordered by (distance to nearest player, age of pending work), probe loadedness with one `dimension.getBlock(cellCentre)` inside try/catch (an `undefined`/throw means unloaded — skip, do not retry for 100 ticks), then execute ops under §6.1 budgets, yielding after every block edit or every placed piece. `ignoreChunkBoundErrors: true` / `allowUnloadedChunks: true` on any volume that straddles a cell edge.
3. **Catch-up on load.** When a cell's `materialisedVersion` lags the macro state, the micro-sim replays only the *net* difference (final state of each plot, not every intermediate stage) — e.g. a house that went L1→L3 while unloaded is placed once as L3. Cells within 2 chunks of a player get **invisible catch-up** (full-speed placement without animation) only while the player is > 48 blocks away; cells the player can see get the staged, animated build so growth is witnessed.
4. **Build staging (from MineColonies).** Each physical build persists `(stage, index)`: CLEAR (vegetation/air above footprint) → GRADE (solid substitution below) → SHELL (`structureManager.place` of the structural piece, `includeEntities:false`) → DECOR (second piece or script pass: torches, signs, beds) → LIGHT/AUDIT (block-light ≥ 1 on every walkable interior/tunnel floor). Interruption resumes at `(stage, index)`.
5. **Loader policy.** Do not use `/tickingarea` for the city (10 × 100 chunks is one neighbourhood). Optionally one `minecraft:tick_world` "heart" entity per capital (radius 2–3) for the market square only, and only after a witness test shows the phone tolerates it.
6. **Entity policy.** Citizens are **records**, not entities. A citizen is embodied (spawned with `minecraft:persistent`, no `minecraft:despawn`) only when their *virtual* position is inside a player's simulation square and the embodied count is under budget; when they leave it, their position is written back and the entity is `remove()`d. Villager-type AI (dweller/scheduler/POIs) runs on the embodied few; the macro-sim moves the rest by timetable.

### 6.3 Terrain levelling

- **Plot search first, grading second.** Sample the footprint plus a 1-block apron with `getTopmostBlock` (81 samples for 9×9, under the per-tick sample cap over 1–3 ticks). Accept plots with height variance ≤ 2 (cheap), tolerate ≤ 4 with a beard, and otherwise either (a) search outward (the Bedrock add-on's strategy) or (b) switch to a **stilt/platform template** (the vanilla "platform below the structure" and the add-on's "wooden maritime platforms").
- **Cost model (verified arithmetic, 9×9 footprint, uniform slope):** variance 1 ≈ 160 edits, 2 ≈ 240, 3 ≈ 325, 4 ≈ 405, 6 ≈ 570 (fill below + clear above + surface replace). Rule: **≤ 450 edits per house platform**; anything larger is a platform build, not a grade.
- **How to grade:** one `fillBlocks` per Y-layer of the footprint (≤ 81 blocks/call, well under the self-cap) with a `blockFilter.excludeTypes` for blocks we keep (ores, bedrock) — "solid substitution" semantics: replace only air, fluids, plants, snow layers; never overwrite an existing solid. Clear above with `fillBlocks(air)` filtered to vegetation/leaves/logs/snow so player-placed blocks survive.
- **Roads are terrain-matched, houses rigid** (vanilla). Street pieces are 1-column-tall per column: for each column set Y = heightmap, cap step to ±1 between neighbours (full-block steps, since jump cost 20 is what villagers are tuned for), and insert a 2-block landing after every 3 risers so the path never looks like a slab-stair trap.
- **Water:** never grade across water; use plank/platform street pieces over water (vanilla rule "Paths do not go below one level of water"), and treat `waterlogged:false` placement plus `liquid_detection: blocking` cubes as the tunnel seal.

### 6.4 Villager movement: teleport-when-unseen vs navigation

- **Within ~48 blocks of a player (inside the sim square, visible):** data-driven navigation only. Use `move_to_poi` (bed/jobsite/meeting_area) via `minecraft:dweller` for daily life, `move_to_block` for errands (target our own job-marker blocks, `search_range ≤ 32`), and the marker-entity trick for long legs (spawn a tiny invisible target entity at the far waypoint, `move_towards_target within_radius 2`, remove it on arrival). Never try to path > 64 blocks in one leg (vanilla scopes villages to ~65×25×65).
- **Beyond that:** the citizen is a record; the macro-sim advances a scheduled position along the street graph by timetable (work 0–8000, gather 8000, sleep 12000 — vanilla's own hours), and the entity does not exist. When the player approaches, spawn at the virtual position with `tryTeleport`-style validation (`checkForBlocks: true`; fall back to the nearest street node).
- **Transitions:** spawn/remove only when the citizen is ≥ 32 blocks from every player and out of line of sight (use `dimension.getBlockFromRay` from the player's head to the spawn point; any hit means hidden). This hides the pop-in and matches the Bedrock add-on's "workers travel toward projects" illusion for builders: spawn the builder at the street node nearest the site, let it walk the last ≤ 24 blocks, then place the piece.
- **Why not `applyImpulse`:** it is physics, not pathing; it cannot avoid obstacles and interacts badly with `can_jump`. Reserve it for cosmetic nudges.

### 6.5 Witness tests required before any of this is law

1. Time a `structureManager.place` of 1,728 / 4,096 / 13,824-block pieces on PS5 and phone (loaded chunk, no animation) — looking for spike warnings and frame hitches.
2. Time `fillBlocks` at 512 / 2,048 / 8,192 blocks on both devices.
3. Count how many `block.setPermutation` iterations one `runJob` achieves per tick on phone vs PS5 (calibrates §6.1).
4. Villager pathing over: full-block steps, stairs, bottom slabs, our custom sloped blocks with reduced collision, iron-bar grates.
5. Flowing water vs iron bars / fences / a custom `liquid_detection: blocking` cube.
6. Hostile spawn attempts on our custom floor blocks at block light 0 vs 1.
7. Whether `placeJigsawStructure` on existing terrain applies any `terrain_adaptation` beard.
8. `minecraft:tick_world` heart entity (radius 2) on the phone: tick time with and without.
9. Dynamic-property save latency at 1 MB / 4 MB total on the phone (`getDynamicPropertyTotalByteCount` as the gauge).

### 6.6 How big can a city be?

**[INFERRED]** Static blocks cost nothing to tick; a placed building is free once placed except for its block entities and any light updates during placement. The runtime cost of a city is therefore: (entities in the loaded square) + (block entities in the loaded square) + (script time) + (save size). Under §6.1:

- **PS5 / Realm (sim 4 fixed on Realms):** 1,000–3,000 buildings and 10,000+ street pieces are feasible as records; what the player experiences is the ≤ 81-chunk window with ≤ 48 embodied citizens and ≤ 120 entities. The limit to watch is DP total (keep ≤ 2 MB) and block entities (≤ 3 per building ⇒ a dense 144×144 window of ~150 buildings holds ≤ 450 block entities — acceptable, but do not add item frames or armour stands in bulk).
- **Android (secondary):** same records, but the embodied cap drops to ~24 citizens / 60 entities, block edits to 40/tick, and structures to 12³ pieces with layer animation; grading large plots on the phone should be avoided by biasing plot search toward variance ≤ 2. A phone-hosted world should not also run the `tick_world` heart.
- **Growth pacing:** with 3 in-game days per real hour and build throughput far above need, pace growth by economy and by the catch-up replay, not by block budget — the budget exists to protect frame time, not to slow the city.

---

## Sources

- https://minecraft.wiki/w/Structure_Block
- https://minecraft.wiki/w/Commands/structure
- https://learn.microsoft.com/en-us/minecraft/creator/documents/introductiontostructureblocks
- https://wiki.bedrock.dev/nbt/structure-limits
- https://wiki.bedrock.dev/nbt/mcstructure
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/structureplaceoptions?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/structuremanager?view=minecraft-bedrock-stable
- https://jaylydev.github.io/scriptapi-docs/latest/classes/_minecraft_server.StructureManager.html
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/structure?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/changelog?view=minecraft-bedrock-stable
- https://minecraft.wiki/w/Bedrock_Edition_1.21.80
- https://minecraft.wiki/w/Bedrock_Edition_1.21.60
- https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.21.80?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/scriptingv2.0.0overview?view=minecraft-bedrock-stable
- https://wiki.bedrock.dev/scripting/script-watchdog
- https://learn.microsoft.com/en-us/minecraft/creator/documents/bedrockserver/server-properties?view=minecraft-bedrock-stable
- https://wiki.bedrock.dev/scripting/troubleshooting
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/system?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/system-run-guide?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable
- https://jaylydev.github.io/scriptapi-docs/latest/classes/_minecraft_server.Dimension.html
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/locationinunloadedchunkerror?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockfilloptions?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockfilter?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockvolumebase?view=minecraft-bedrock-stable
- https://minecraft.wiki/w/Commands/fill
- https://wiki.bedrock.dev/scripting/script-server
- https://jaylydev.github.io/scriptapi-docs/features/dynamic-properties.html
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/world?view=minecraft-bedrock-stable
- https://github.com/MicrosoftDocs/minecraft-creator/issues/520
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/block?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_liquid_detection?view=minecraft-bedrock-stable
- https://minecraft.wiki/w/Waterlogging
- https://learn.microsoft.com/en-us/minecraft/creator/documents/simulationrenderdistanceguide?view=minecraft-bedrock-stable
- https://minecraft.wiki/w/Simulation_distance
- https://minecraft.fandom.com/wiki/Simulation_distance
- https://minecraft.wiki/w/Commands/tickingarea
- https://learn.microsoft.com/en-us/minecraft/creator/documents/tickingareacommand
- https://feedback.minecraft.net/hc/en-us/articles/5520890863245-Minecraft-1-18-30-Bedrock
- https://github.com/cda94581/open-source-chunk-loaders/blob/main/README.md
- https://minecraft.wiki/w/Daylight_cycle
- https://minecraft.wiki/w/Commands/time
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_navigation.walk?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entitynavigationcomponent?view=minecraft-bedrock-stable
- https://minecraft.wiki/w/Villager
- https://minecraft.wiki/w/Village_mechanics
- https://bugs-legacy.mojang.com/browse/MCPE-47075?attachmentOrder=asc
- https://bugs-legacy.mojang.com/browse/MCPE-46805?attachmentSortBy=dateTime
- https://github.com/TangoTek/TekTopia-Community/issues/652
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_collision_box?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_to_block?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_towards_target?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_to_poi?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_dweller?view=minecraft-bedrock-stable
- https://wiki.bedrock.dev/entities/village-mechanic
- https://wiki.bedrock.dev/entities/sleeping-entities
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_sleep?view=minecraft-bedrock-stable
- https://wiki.bedrock.dev/entities/entity-movement
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/teleportoptions?view=minecraft-bedrock-stable
- https://wiki.bedrock.dev/meta/addon-performance
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_despawn?view=minecraft-bedrock-stable
- https://minecraft.fandom.com/wiki/Spawn
- https://gist.github.com/yonta/ce7c7e17a78777655cc5d61f60092216
- https://learn.microsoft.com/en-us/minecraft/creator/reference/source/vanillabehaviorpack_snippets/spawn_rules/zombie?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/spawnrulesreference/examples/spawnrulescomponents/spawn_brightnessfilter?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/spawnrulesreference/examples/spawnrulescomponents/spawn_rules?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/spawning/entityspawningdeepdive?view=minecraft-bedrock-stable
- https://wiki.bedrock.dev/entities/spawn-rules
- https://www.minecraft-guides.com/mod/minecolonies/
- https://gurugamer.com/pc-console/a-complete-guide-to-play-minecraft-minecolonies-mod-24564
- https://deepwiki.com/ldtteam/minecolonies/2.5-work-orders-and-structure-building
- https://minecolonies.com/wiki/items/placeholderblocks/
- https://github.com/ldtteam/Structurize/issues/427
- https://wiki.minecolonies.com/source/workers/builder
- https://github.com/ldtteam/minecolonies-features/issues/876
- https://discover.hubpages.com/games-hobbies/Minecraft-Mod-Examination-Millenaire
- https://millenaire.org/wiki/Guide_on_making_Custom_Villages
- https://en.namu.wiki/w/Mill%C3%A9naire
- https://www.millenaire.org/
- https://www.curseforge.com/minecraft/mc-mods/tektopia
- https://sites.google.com/view/tektopia/home/getting-started
- https://sites.google.com/view/tektopia/home/guides/the-basics
- https://minecraft.wiki/w/Village
- https://minecraft.fandom.com/wiki/Custom_structure
- https://minecraft.wiki/w/Jigsaw_structure
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/worldgenreference/examples/jigsawjigsawstructurejson?view=minecraft-bedrock-stable
- https://wiki.bedrock.dev/world-generation/jigsaw-structures
- https://www.curseforge.com/minecraft-bedrock/addons/villagers-can-build-villages
