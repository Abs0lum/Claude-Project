# F-TOWNS-ROADS — towns, districts, roads (study for CIVITAS, 2026-10-06)

Group items: Countered's Settlement Roads, RoadWeaver, RoadArchitect, Routes, Medieval Fantasy City Generator (watabou),
GDPC + GDMC-HTTP, Microsoft scripting samples, and five structure/village packs (Towns and Towers, CTOV, Better Villages,
Villages&Pillages, Medieval Buildings).
Every mechanism below comes from a file I opened (named inline). "Not found" is stated where I looked and found nothing.
Licences are as shown in the files (and in the intake LEDGER.json); all are fine to study for personal use. We write our own Bedrock code.

Effort: S = under a day of script work, M = a few days, L = a week or more. Value: 1 (nice) to 5 (changes how towns look or play).

---

### Countered's Settlement Roads (Forge/Fabric 1.20.1 jar 2.0.1 + GitHub source "settlement-roads-new"; licence: CC0 1.0 in both the source LICENSE and the jar's LICENSE_settlement-roads, the Modrinth ledger says MIT; files examined: see list)

- **What it does:** finds vanilla villages with `/locate`-style searches, joins each new village to its nearest neighbour, runs a grid A* over the worldgen heightmap, stores the path, and lays it chunk by chunk as a world feature with lamps, distance signs and buoys.
- **Mechanisms found:**
  - **Topology** (`StructureConnector.java`): each newly located village gets one edge, to its single nearest other village (squared distance). Duplicate pairs are skipped. The result is a nearest-neighbour forest, not a planned network. On world load it locates `initialLocatingCount = 7` villages; after that it locates one more every 300 feature calls, up to `maxLocatingCount = 100` (`RoadFeature.tryFindNewStructureConnection`, `ModConfig.java`). Pathfinding runs on a 7-thread pool (`ModEventHandler.THREAD_COUNT = 7`) with `maxSteps = 5000`.
  - **A*** (`RoadPathCalculator.java`, constants match the decompiled jar class):
    - Nodes sit on a 4-block grid (`neighborDistance = 4`) with 8 neighbours. Heights come from `WORLD_SURFACE_WG`, cached in a hash map that is cleared above 100 000 entries.
    - A step is **rejected** if the height difference to the neighbour is more than 3, or if the "terrain stability" (sum of |Δy| to the 4 cardinal neighbours) is more than 2.
    - Step cost g += 1 (orthogonal) or 1.5 (diagonal) + 40·|Δy| + 8·50 for river/ocean biomes + 8·20 if y == 62 (sea-level beaches) + 16·stability.
    - Heuristic = (|dx|+|dz| − 0.6·min(|dx|,|dz|))·30. The search stops when the Manhattan distance to the goal is under 8.
  - **Width rasterisation** (`generateWidth`): direction classes are X, Z and two diagonals. Width 3 (`ModConfiguredFeatures`: width list `[3]`) stamps a 3-wide cross-section. Diagonals stamp a 3×3 square minus 2 corners. The 3 intermediate cells between grid nodes are interpolated.
  - **Laying** (`RoadFeature.runLogic`):
    - The first and last 60 segments are skipped (they leave the village itself untouched).
    - Each column's Y is the average of the heightmap over ±`averagingRadius = 1` segments.
    - Placement replaces the block below the surface with a random pick from the material set and clears up to 3 blocks above (stopping at air, logs or fences). Grass two below becomes dirt.
    - Placement is refused on ice, packed/blue ice, leaves, logs, planks, fences, mangrove roots, seagrass, or when both blocks below are non-opaque.
    - "Natural" roads place each block with only 50 % chance, which gives a broken path look.
    - Materials: artificial sets are mud bricks/packed mud, polished andesite/stone bricks, and stone/mossy/cracked bricks. Natural sets are coarse/rooted dirt/packed mud, cobble/mossy/cracked, and dirt path/coarse/packed mud.
  - **Decorations** (`RoadFeature.addDecoration`, `*Decoration.java`, `WoodSelector.java`):
    - Distance signs: a hanging sign on a 4-high fence post at segment 65 and at length−65, offset 2 blocks sideways. Text is "Next Village / %d m" with the segment count as the distance, plus "Welcome traveller" on the back.
    - Lampposts: a 4-high fence with an arm and a hanging lantern every 59 segments on a random side (natural roads get a fence+torch waypoint instead). Skipped if the side ground differs by more than 1.
    - Buoys: spruce planks + fence every 25 segments when the surface is water. There are **no bridges** in this mod (no bridge class in source or jar).
    - Wood follows the biome: bamboo / jungle / acacia / dark oak / cherry / birch / spruce (taiga) / oak.
  - **Data schema** (`Records.java`): `RoadData{width, road_type, materials[], placements[{middle_pos, positions[]}]}`, `StructureConnection{from,to}`, `StructureLocationData[BlockPos]`. These are stored as world attachments.
- **Usable for CIVITAS:**
  - **Hard rejection thresholds as a cheap pre-filter** in our road A*: refuse a cell when |Δy| > 3 to the previous node or when the cardinal-neighbour roughness is > 2, before computing the real cost. On Bedrock, add it as an early `continue` in `planRoadJob`'s neighbour loop using the land-survey heights we already hold. Effort S, value 2 (we already have ramp and cost logic; this only trims the search).
  - **Lamp / sign cadence for country roads between towns:** a lamp every ~59 cells on alternating sides, a "Name — N m" sign about 65 cells out from each town gate, and wood chosen by biome. On Bedrock, place it from a template (`pw:roadside_lamp`) in the same runJob that lays the road. Write the sign text with the `BlockSignComponent` (`block.getComponent("minecraft:sign").setText`). Effort S, value 2.

### RoadWeaver (Forge 1.20.1 jar 2.3.0 + GitHub source; licence MIT; files examined: see list)

- **What it does:** a full road-network generator. It predicts structure positions, plans a network topology with one of five planners, pathfinds each edge with a terrain-aware cost, smooths the path (spline plus slope limiting), places it with slabs on half-steps, adds bridges with piers and ramps, and can grow roadside hamlets.
- **Mechanisms found:**
  - **Topology** (`planning/impl/*.java`; the default is `PlanningAlgorithm.RNG` in `PlanningConfig.java`; max edge length 2048 blocks in `RoadConstants`):
    - *RNG (relative neighbourhood graph):* edge A–B is kept unless some third town C is closer to both A and B than they are to each other (`da2 < d2 && db2 < d2`). This is O(n³). It gives "natural" networks with no redundant triangles, and the graph stays connected.
    - *MST (Kruskal + union-find):* the minimal network, a tree with no loops.
    - *KNN:* k = 2, `alpha = 1.8` (an edge is a candidate only if d² ≤ α²·max(nn²(i), nn²(j)), so a town is not connected far beyond its local spacing). Also a Gabriel test (reject if any C has |AC|²+|BC|² ≤ |AB|²), degree cap 2, and a minimum angle of 40° between edges leaving one node. `connectComponents` then joins separate clusters by shortest pairs (degree cap 3, minimum angle 35°).
    - *SnapBranch:* insertion order. It starts from the closest pair. Each new town attaches either to the nearest node or to the **projection onto an existing edge** (when t is within (0.10, 0.90) and the split edge is at most 1.20× its old length; edge attachments get a −6 bias). This creates **T-junctions mid-road** instead of star hubs. Above 700 points it falls back to RNG.
  - **A* cost** (`BasicAStarPathfinder.java`, defaults in `RoadConstants`):
    - Grid step 8 (`DEFAULT_ASTAR_STEP`), max 200 000 steps, weighted heuristic ×1.2 (ε = 0.2), heuristic weight 15.
    - Move cost = step (1 / 1.414) + 80·|Δy| + 2·12 for water biomes + 15·stability + 80·water depth (in water columns) + 80 near water + 0.5·(perpendicular deviation from the straight A→B line)/step.
    - The **deviation term** keeps roads near the direct line unless the terrain argues otherwise.
  - **Contour-following "potential field" variant** (`PotentialFieldPathfinder.java` + `TerrainGradientHelper.java`):
    - The gradient comes from central differences over ±step. The contour direction is (−∂h/∂z, ∂h/∂x), flipped to face the goal.
    - Base cost ×(1 − alignment·0.45·min(1, 2|∇h|)), floored at 0.3: moving along contours on slopes is cheaper.
    - Grade = |Δy| / horizontal distance. A soft limit of 8 % adds 600·(g−0.08)/0.08 and a hard limit of 15 % adds 6000·(g−0.15)/0.15. Elevation cost is quadratic (Δy²·80·0.5). A penalty of 80·d·|∇h|·cos(move, gradient) applies for climbing straight up the fall line.
    - Water: 800 + depth²·80·2. The search box is the start/end bbox ± max(128, min(1024, L1/3)).
  - **Post-processing** (`PathPostProcessor.java`):
    - Simplify: drop nodes whose cross product with neighbours is ≤ 16.
    - Detect bridge cells (water depth ≥ 1 below sea level) and straighten bridge runs to a straight line between entry and exit.
    - Relax non-bridge nodes with (prev + 2·cur + next)/4.
    - Catmull-Rom spline at ceil(dist·4) samples per span (linear on bridge spans), then resample centres every 1 block.
    - Rasterise all cells within width/2 of the spline and assign each cell to its nearest centre (search ±20 centres) so that segments own their cells.
  - **Height profile** (`HeightProfileService.java`):
    - Average of `MOTION_BLOCKING_NO_LEAVES` over ±`averagingRadius` (default 8) centres.
    - Then a **two-pass slope clamp**: forward and backward, each step ≤ ceil(s/2) from the previous centre and ≤ s from two back (s = `maxSlopeStepPerTwoSegments`, default 1). The road therefore rises at most 1 block per 2 cells, in either direction.
  - **Paving** (`SegmentPaver.java`, `RoadHeightInterpolator.java`):
    - Each width cell gets its Y by projecting onto the centre polyline and lerping the target Y. Natural roads choose materials per biome preset.
    - A **bottom slab** is placed on a cell when a neighbour along X or Z is higher and the opposite one is not lower. That gives slab half-steps on every rise.
  - **Bridges** (`BridgeRangeCalculator`, `BridgeTransitionAdjuster`, `BridgeBuilder`, `PathFeature.java`):
    - Bridge ranges are merged when gaps are ≤ 8 segments and dropped if shorter than 5. Spans longer than 100 blocks are skipped, or get buoys instead.
    - Deck Y = sea level + 2 (`bridgeDeckClearance`). The deck is stone bricks at the road's own width, with the air above cleared.
    - Piers every 6 segments (minimum 3), 1 wide, dropped down until a sturdy face, at most 20 tall.
    - Ramps: 4 segments on each side, lerped from the ground Y to the boundary Y, then the slope clamp is re-run.
  - **Decorations** (`DecorationPlanner.java`):
    - Distance signs at segment 8 and at n−10. The sign text is the Euclidean distance in metres to the other end.
    - Lamps every 32 segments (`DEFAULT_LAMP_INTERVAL`), offset max(2, width/2+1) from the centre on a random side. If the side ground differs by more than 1, a lantern "fallback" replaces the post.
  - **Roadside hamlets** (`RoadsideVillagePrecomputer.java`):
    - Roll 30 % per road. The road must be ≥ 32 segments. Windows of 24 segments are scored by flatness + curve, and the curve must be 0–70°.
    - Slots run along both sides, with the right side phase-shifted by gap/2. The footprint radius is 8, the stride 2 segments, and after every 3 buildings a gap of 3 segments is left.
    - Consecutive slots may differ by ≤ 3 in height. Bounding boxes must not overlap. The last slot becomes a villager spot, and every 4th slot is decor.
  - **Plot suitability score** (`scoreFootprint`, the most reusable piece):
    - Sample heights on a disc of radius r. Compute the water ratio, mean, variance, IQR (q1 at n/4, q3 at 3n/4), the "core range" (20th–80th percentile), the full range, and |mean − roadY|.
    - The plot is **usable** iff water ≤ 8 %, core range ≤ maxRange, IQR ≤ max(2, maxLocalSlope+1), variance ≤ max(2.5, 1.5·maxLocalSlope²), and road delta ≤ max(maxDist/2, 2·maxHeightDiff).
    - Defaults: maxLocalSlope 4, maxHeightDiff 4, maxRange = max(slope+2, diff+3) = 7.
    - Score = 1.8/(1+coreRange) + 1/(1+variance) + 1/(1+roadDelta) − 4·waterRatio − (0.5 if full range > maxRange).
  - **Road snapping** (`RoadSnapService.java`): a secondary road running within 12 blocks (split threshold 24) of a primary road and parallel to it reuses the primary's segments, and a 3-segment transition forms a T-junction.
  - **Throttle** (`ThrottleHelper.java`): duty-cycled pathfinding. After each 20 ms of work it sleeps 20·(100−duty)/duty ms (maximum 200), with duty 50 % by default.
- **Usable for CIVITAS:**
  - **Plot suitability score in the land survey and slot picking.** Port `scoreFootprint` to a JS function over our survey height grid (`pw_civ_land.js` site). Use the percentile core range and IQR instead of plain max−min, so a single boulder or ditch does not veto a lot, and rank candidate home lots by the score (our contour lanes in the hills would benefit most). Effort S, value 4.
  - **Two-pass slope clamp + slab half-steps** for any road we lay outside the 13-wide kit (country roads, hill lanes): forward/backward clamp of centre Y, then a slab where the neighbour is higher. On Bedrock, place `*_slab` with `minecraft:vertical_half=bottom`. Effort S, value 3.
  - **Contour-alignment discount and soft/hard grade penalties** added to `planRoadJob`'s cost (gradient from our survey heights). It complements our existing switchback/hairpin shapes by letting the A* itself prefer contour-hugging lines. Effort M, value 3.
  - **Network topology for multi-town worlds:** RNG (connected, no redundant triangles) or SnapBranch (T-junctions onto existing roads, which looks the most "grown"). With fewer than about 50 towns, O(n³) is trivial in script. Effort S (algorithm) / L (laying long roads in jobs), value 3.
  - **Roadside ribbon hamlets** as a migration outlet: when a town is full, new homes grow as a strip along the road to the neighbour town, using the window and slot rules above. Effort M, value 3.
  - **Deviation-from-chord penalty** (0.5·distance/step) so town roads do not wander. Effort S, value 2.

### RoadArchitect (Forge 1.20.1 jar 1.6.6 + GitHub source; licence Apache-2.0; files examined: see list)

- **What it does:** a second road mod. It builds a planar graph between structures, runs a weighted A* per new edge (async), post-processes heights and merges near-parallel roads into trunks, then lays roads with biome-specific palettes.
- **Mechanisms found:**
  - **Graph** (`RoadGraphState.connect`): every new node tries to connect to **all** existing nodes within 2×`maxConnectionDistance` (715 → 1430 blocks, `RoadArchitectConfigData`). An edge is **rejected if it crosses any existing edge** (2-D segment intersection) that does not share a node. This is a greedy planar graph, and insertion order matters. The pipeline runs every 120 s (`pipelineIntervalSeconds`).
  - **A*** (`util/PathFinder.java`):
    - Grid 4. Weighted A* with ε = 1.5. The octile heuristic (dx+dz−0.5·min) is scaled by a per-run factor that smoothsteps from 80 to 120 as the L1 distance goes from 200 to 1200.
    - The step cap is 16·L1/4, clamped to [512, 200 000].
    - Costs: step 1 / 1.5, 40·|Δy|, biome tags (river 240, ocean 280, deep ocean 320, mountain 160, beach 160), y ≤ 63 adds 240, water step +200, coast buffer 16 blocks adds 180, forbidden-biome buffer 16 blocks adds 500. |Δy| > 3 is impassable.
    - Stability (`TerrainAnalyzer.java`): the cardinal |Δy| sum must be ≤ 3, else impassable. Base cost 16·sum, plus a **roughness penalty** of 15·(range−12) where range = max−min height in a 25×25 window (radius 12, stride 3, with a coarse pass first and early exit). This makes mountains "feel wider".
    - **Partial acceptance:** if the cap is hit but the best node made ≥ 80 % progress (L1), that partial path is accepted.
  - **Post-processing** (`handlers/RoadPostProcessor.java`):
    - Height normalisation, 2 passes of: median filter (window 5), forward then backward clamp of ±1 per node, and a de-spike (a node ≥ 2 above both neighbours goes to their average).
    - Parallel-road merge: roads within 45 blocks, at an angle < 35°, are partners. The convergence point needs a tail angle < 35°, an average distance < 67.5, and a score (angle + dist/10) < 50. The secondary road is truncated there to join the trunk.
  - **Placement** (`worldgen/RoadFeature.java`, `config/defaults/RoadStyleDefaults.java`): roads are laid as stripes with half-width + 2 clearance. Palettes are weighted per biome (e.g. the default is grass_block 3, cobblestone 2, mossy 1, gravel 1; beach uses sand 7; old-growth pine taiga uses podzol 7). Lamps every 30 blocks, side decorations every 12, buoys every 18.
- **Usable for CIVITAS:**
  - **Partial-path acceptance** for our road and lane jobs: when `planRoadJob` exhausts its budget, accept the best node if it made ≥ 80 % progress and finish with a short second search. That avoids the "no road at all" outcome. Effort S, value 3.
  - **Roughness window penalty** (range over radius 12 above a threshold of 12) as an extra cost or a survey flag, so streets steer around rough ground instead of skirting it closely. Effort S, value 2.
  - **Median + clamp + de-spike** on any laid profile, before handing it to the kit-street placer. Effort S, value 2.
  - **Planar greedy topology** (reject crossing edges) is an alternative to RNG when towns are added one at a time over game days (which is what CIVITAS does): connect the new town to every town in range whose road would not cross an existing road. Effort S, value 3.

### Routes (NeoForge 1.21.1 jar 1.2.119; licence "shiero's Mods License — If you make money, I make money" v2.0: personal/non-commercial use and modification are free; files examined: see list)

- **What it does:** builds a named road network ("Route 1…") between settlements, sorted into tiers (village/town/city). It paints chunks as CITY / ROUTE / AREA zones, names towns and areas, and shows "Now entering" notifications.
- **Mechanisms found:**
  - **Tiers** (`gen2/SettlementGraph.tierOf`, `RoutesConfig`): the settlement span across ≥ 128 blocks makes a CITY, ≥ 64 a TOWN, otherwise a VILLAGE (`settlement_tier_town_span = 64`, `city_span = 128`). Structures within a cluster radius of 128 (revision ≥ 2) are merged into one node.
  - **Network** (`SettlementGraph.buildMutual`, default config: `max_route_connections = 4`, `route_max_length = 1600`, `route_loop_closing = true`):
    1. Each node wants `connectionsFor` = a hashed count within its tier band: lo = 1 + t·(k−1)/3, hi = 1 + (t+1)·(k−1)/3. Bigger places want more roads.
    2. It takes candidates in distance order, skipping any whose direction is within **30°** of an already kept one (`MIN_ANGLE_DEG = 30`, "thinning").
    3. An edge is kept if it is **mutual** (each side wants the other).
    4. **RNG** edges are added: the lune is empty.
    5. **Gabriel** "loop-closing" edges are added: the disk is empty, i.e. no C with |AC|²+|BC|² ≤ |AB|².
    6. Isolated nodes connect to their nearest neighbour (up to 2× max length).
    7. **Fork trunks** (`forkTrunks`/`branch`): for a town with ≥ 2 edges each ≥ 320 blocks long, those edges are replaced by a shared trunk that leaves the town in the mean bearing for 112–(shortest−192) blocks (trunk = max(48/angular gap, 112)). Destinations are split at the widest angular gap and recursed (depth ≤ 4). The result is **one road leaving town that forks later**, instead of many parallel roads.
  - **Zones** (`route/ZonePaint.java`): the chunk centre within 48 of a town is CITY (core). Within 28 of a route segment it is ROUTE. Within 96 of a town it is CITY. Otherwise it is AREA.
  - **Areas** (`route/AreaRegions.java`): a 4-way chunk flood-fill bounded by CITY/ROUTE chunks gives an enclosed region. If it reaches the network bbox ± 4 chunks or spans > 96 chunks, it is "wild" (open). The region id is the smallest packed chunk key. Results are memoised (≤ 262 144 entries).
  - **Naming** (`gen2/Gen2Names.java`, `Gen2NameLedger.java`, `route/RouteTracker.java`):
    - Town name = pool[hash(seed, x, z) mod n]. A 1-in-1000 "rare" pool exists (Paraguayan place names). The base pool is 40 names.
    - A ledger guarantees uniqueness: the first free name from the preferred index onward, else "Name 2", "Name 3"… Claims are persisted on the next server tick.
    - Area names = biome prefix (Frost / Dune / Rust / …) + a hashed suffix from {pine, vale, reach, fen, hollow, moor, field, grove, run, rise, flats, wood}, avoiding prefix = suffix. Routes are "Route N" in discovery order.
  - **Notifications** (`RouteTracker.onTick`): every 20 ticks, per player, it resolves the zone and sends a toast / announcement / chat line on change (lang `message.routes.zone_enter.city` = "Now entering").
  - Route geometry config (`RoutesConfig`, defaults only, implementation not opened): width 5, water width 10, max grade 8, tunnels 9 wide × 8 high, straight bridges.
- **Usable for CIVITAS:**
  - **"Now entering <Town> / <District>" titles:** every 20 ticks, compare each player's zone (town core radius, district polygon, road corridor) with the last one and call `player.onScreenDisplay.setActionBar` or `setTitle` on change. The cost is tiny. Effort S, value 3.
  - **Unique name ledger + biome-flavoured names** for towns, districts and the countryside between towns (e.g. a district called "Millfield" in plains). Store `{key → name}` in one dynamic property. Effort S, value 3.
  - **Tier-scaled road count + 30° thinning + fork trunks** when CIVITAS connects towns. A metropolis gets more roads, and they leave through a few gates then fork, which matches our wall-gate design. Effort M, value 3.
  - **Zone thresholds as a template:** core 48 / outskirts 96 / road corridor 28 for "is the player in town" checks used by watchmen, rumours or migration. Effort S, value 2.

### Medieval Fantasy City Generator — TownGeneratorOS (Haxe/OpenFL source; licence GPL-3.0; files examined: see list) — main study object

- **What it does:** generates a 2-D medieval city plan from a seed: Voronoi wards, optional walls with gates and towers, an optional citadel, a plaza/market, streets from each gate to the plaza, roads out of the gates, ward types assigned by location-rating rules, and building footprints carved by recursive bisection.
- **The algorithm step by step** (`building/Model.hx` unless noted):
  0. **Size & switches.** `nPatches` = number of city wards (default 15). The UI (`ui/CitySizeButton.hx`, `TownScene.hx`) picks size = min + floor(rand·(max−min)): Small Town 6–9, Large Town 10–14, Small City 15–23, Large City 24–39 (the comment lists Metropolis 40). `plazaNeeded`, `citadelNeeded` and `wallsNeeded` are **each a 50 % coin flip**. The build retries from scratch on any error ("Bad citadel shape", "Unable to build a street", "Bad walled area shape").
  1. **Seeds on a spiral** (`buildPatches`): nPatches·8 points. Point i has angle sa + √i·5 and radius 0 for i = 0, else 10 + i·(2 + rand). Voronoi on these. **Lloyd-relax 3 times**, but only the 3 most central seeds plus seed #nPatches, so the core cells are even and the outer ones stay irregular. Regions are sorted by seed distance from the origin.
     - Region 0 = centre (`center` = its vertex nearest the origin), and the **plaza** if needed.
     - Regions 0..nPatches−1 = the city (`withinCity`, `withinWalls = wallsNeeded`).
     - Region nPatches = the **citadel** if needed. It sits just outside the inner ring, on the edge of the city.
  2. **Junction cleanup** (`optimizeJunctions`): on city and citadel patches, any edge shorter than 8 units is collapsed. The two vertices merge at their midpoint and neighbours are updated and de-duplicated. This avoids tiny street stubs.
  3. **Walls** (`buildWalls` + `building/CurtainWall.hx`):
     - The wall polygon is the **outer boundary of the inner patches** (`findCircumference`: edges not shared with another inner patch, chained).
     - If real, every non-reserved vertex is smoothed with factor min(1, 40/nInner). Citadel vertices are reserved and not smoothed.
     - **Gate candidates** = wall vertices (not reserved) that touch **more than one inner patch**, i.e. where a street between two wards meets the wall.
     - Loop: pick a random candidate and make it a gate. If exactly one outer patch touches it, **split that outer patch** from the gate to its vertex farthest along the wall's outward normal, so a road can leave the gate. Remove the gate **and its two neighbouring candidates** from the list, so gates are never adjacent. Repeat while ≥ 3 candidates remain.
     - Gate vertices are smoothed. **Towers stand on every wall vertex that is not a gate** (`buildTowers`).
     - Patches farther than 3× the wall radius are discarded.
     - The **citadel** becomes a `Castle` ward with its own real curtain wall (reserved vertices = those touching non-city patches). It is rejected (rebuild) if its compactness is < 0.75. The castle's gates are added to the city's gates.
  4. **Streets and roads** (`buildStreets` + `building/Topology.hx` + `geom/Graph.hx`):
     - The graph is built on all Voronoi vertices with edge weight = length. Wall and citadel vertices are **blocked except gates**. Vertices of city patches (not on the border) are "inner", the rest "outer".
     - For **each gate**: a **street** runs from the gate to the nearest plaza vertex (or the centre), searched **excluding outer nodes**, so it stays inside. If the gate is on the city border, a **road** runs from the graph vertex nearest to a point 1000 units out along the gate's direction back to the gate, excluding inner nodes.
     - Note: `Graph.aStar` takes `openSet.shift()` from an unsorted list. It is effectively breadth-first with relaxation, not optimal A*.
     - `tidyUpRoads`: all streets and roads are cut into segments, segments running **along the plaza** are dropped, duplicates removed, and the rest re-chained into `arteries`. Arteries get 3 smoothing passes (`smoothVertexEq(3)`) except at their endpoints.
     - Ward edges that are not arteries become ordinary streets/alleys implicitly, through the inset in step 6.
  5. **Ward assignment** (`createWards` + `wards/*.hx`):
     - a. Plaza → `Market`.
     - b. Every inner patch touching a **border gate** becomes a `GateWard` with probability 0.5 if walled, 0.2 if not.
     - c. The ward queue is a fixed list of 36 (`WARDS`): 21 Craftsmen, 5 Slum, 2 Merchant, 2 Patriciate, 2 Market, 1 Cathedral, 1 Administration, 1 Military, 1 Park. The order matters: Merchant is 3rd, **Cathedral 6th**, Administration 15th, the first **Slum 17th**, Patriciate 20th, the 2nd Market 21st, Military 30th, Park 33rd. A light shuffle does floor(36/10) = 3 random adjacent swaps. **Small towns therefore get only craftsmen, a merchant quarter and a temple; slums, rich quarters, barracks and parks appear only as the city grows.** After the list runs out, the rest are Slum.
     - d. For each class in queue order: if it has `rateLocation`, the **unassigned patch with the minimum rating** gets it; otherwise a random patch does. The ratings:
       - `MerchantWard`: distance to the plaza centre (or the centre). Closest wins.
       - `Cathedral`: −1/area if it borders the plaza (a big lot facing the plaza wins), else distance × area.
       - `AdministrationWard`: 0 if it borders the plaza, else distance to the plaza centre.
       - `Market` (a second market): +∞ if it touches another market, else area/plazaArea (no bigger than the plaza).
       - `PatriciateWard`: −1 per bordering Park, +1 per bordering Slum.
       - `MilitaryWard`: 0 if it borders the citadel, 1 if it borders the wall, else +∞ (0 when there is neither wall nor citadel).
       - `Slum`: −distance from the centre, so the farthest wins.
       - `CraftsmenWard`, `Park`: no rating, random.
     - e. **Outskirts:** if walled, for each wall gate with probability 1 − 1/(nPatches−5), unassigned patches touching that gate **outside** the wall become `withinCity` GateWards. These are suburbs at the gates.
     - f. City radius = farthest vertex of any city patch. Countryside patches become `Farm` if rand < 0.2 and compactness ≥ 0.7, else empty `Ward`.
  6. **Footprints** (`Ward.hx`, `building/Cutter.hx`):
     - `getCityBlock` insets each patch edge by half a street width: MAIN_STREET 2.0 on arteries and plaza edges, REGULAR 1.0 for inner edges, ALLEY 0.6 for outer edges; wall edges get MAIN/2.
     - `createAlleys` bisects the block recursively across its longest edge. The ratio is (1−s)/2 + rand·s with s = 0.8·gridChaos. The angle jitter is ±(π/6·gridChaos)/2, zero if the area is < 4·minSq. The cut leaves an alley gap. A piece stops splitting when its area < minSq·2^(4·sizeChaos·(rand−0.5)), and it is kept with probability 1 − emptyProb.
     - Per-ward parameters (minSq, gridChaos, sizeChaos, emptyProb):
       - Craftsmen: 10+80r², 0.5–0.7, 0.6, 0.04
       - Merchant: 50+60r², 0.5–0.8, 0.7, 0.15
       - Patriciate: 80+30r², 0.5–0.8, 0.8, 0.2
       - Administration: 80+30r², 0.1–0.4, 0.3
       - Slum: 10+30r², 0.6–1.0, 0.8, 0.03
       - Gate: 10+50r², 0.5–0.8, 0.7
       - Military: √area·(1+r), 0.1–0.4, 0.3, 0.25
     - Cathedral: 40 % a "ring" building (peel of thickness 2–6), else orthogonal blocks (minSq 50, fill 0.8). Castle: block shrunk by 4, orthogonal blocks minSq √area·4, fill 0.6. Park: radial sectors (compactness ≥ 0.7) or semi-radial, with alley gaps. Market: a statue (60 %) or a fountain, offset 20–60 % toward the longest edge. Farm: a 4×4 house 30–70 % of the way from a random vertex to the centroid.
     - Unenclosed wards are thinned by `filterOutskirts`: buildings far from populated edges are dropped by a density falloff (edges on roads weigh 1, enclosed neighbours 1, other city neighbours 0.4, and vertices shared only with city patches 2·rand). This gives ragged edges at the city limit.
- **Usable for CIVITAS:**
  - **The ward queue as our growth ladder.** Unlock district kinds by town tier in watabou's order: craft + merchant + temple from village I, administration (town hall) mid-town, the first poor quarter and rich quarter around ~17–20 districts, a second market at ~21, barracks and park late. Encode this as `DISTRICT_LADDER = [...]` in `pw_civ_clock.js` next to `DISTRICT`. Effort S, value 4.
  - **`rateLocation` scoring for each district kind on top of our DISTRICT street ordering.** Instead of the fixed street order, score candidate streets or lots: merchants by distance to the square; temple and town hall must **face the square**, with large lots preferred; a second market may not touch the first; the manor/rich quarter takes −1 per adjacent park and +1 per adjacent poor/edge-trade street; barracks must border the wall or the palace; poor quarters go farthest out. Our streets already carry `role` and distance to the square, so adjacency can come from the junction graph. Effort S–M, value 4.
  - **Gate siting rules for CIVITAS walls:** gates only where an existing street meets the wall line (a vertex shared by ≥ 2 inner districts); after choosing one, block its two neighbouring candidates (no adjacent gates); a tower on every other wall vertex; and when a gate opens onto a single outer lot, split that lot to make room for the exit road. Effort S, value 3.
  - **Suburbs at the gates:** after the wall stands, let the lots touching each gate *outside* the wall become "gate districts" with probability 1 − 1/(n−5). This fits our GREENBELT rule as a controlled exception at gates only. Effort S, value 3.
  - **Plaza rule:** artery segments that run along the plaza edge are not streets (the plaza itself is the street), and the first civic buildings are chosen as those whose lots border it. We already have the square; the rating functions (above) give the "overlooks the plaza" behaviour. Effort S, value 2.
  - **Recursive bisect lot subdivision** for big blocks behind the frontage (back lots, courtyards). Port `createAlleys` with per-district minSq/chaos so that rich quarters get large regular lots and poor quarters small chaotic ones, then fit our templates to the lots. Effort M, value 3 (only if we move beyond pure street-frontage slots).
  - **Ragged town edge:** apply the `filterOutskirts` density falloff to decide which outer slots stay empty, so the edge is not a hard line. Effort S, value 2.
  - Citadel placement: the region just outside the core ring, on the edge, with its own wall, re-rolled if not compact (≥ 0.75). That matches our palace with a reserved block. Use the compactness test (4π·area/perimeter²) when choosing the palace block. Effort S, value 2.

### GDPC (Python framework for GDMC; licence MIT; files examined: see list) and GDMC-HTTP interface (Fabric/NeoForge mod; licence MIT; files examined: see list)

- **What they do:** GDPC is a Python client that edits a Minecraft Java world over HTTP (the GDMC settlement-generation competition). GDMC-HTTP is the server-side mod exposing `/blocks`, `/heightmap`, `/structure`, `/chunks`, `/entities`. Neither ships a plot-selection algorithm. They are helper toolkits, so the mechanisms are infrastructure.
- **Mechanisms found:**
  - **Heightmaps** (`gdpc/world_slice.py`): a `WorldSlice` loads chunk NBT for a rect and decodes the 4 heightmaps (MOTION_BLOCKING, MOTION_BLOCKING_NO_LEAVES, OCEAN_FLOOR, WORLD_SURFACE) from packed long bit-arrays into numpy arrays (value + yBegin).
  - **Custom heightmaps** (`gdmc_http_interface/.../utils/CustomHeightmap.java`, `docs/Endpoints.md`):
    - `MOTION_BLOCKING_NO_PLANTS` treats leaves, logs, bee nests, mangrove roots, mushroom blocks, pumpkin, melon, moss, nether wart block, cactus, farmland, coral, sponge, bamboo, cobweb, sculk, saplings, flowers and crops as transparent. It gives **ground height under trees and crops**.
    - Also arbitrary `?blocks=` lists (ids or tags treated as transparent) and `yBounds` (scan from a ceiling down, for caves).
    - The scan is per column, from yMax down to the first "opaque" block.
  - **Placement controls** (`Endpoints.md`): `doBlockUpdates=false` gives flags 0110010, which is faster and stops water flowing and torches popping. `keepLiquids=false` on structure placement removes water already present. Structure placement takes `rotate 0–3`, `mirror x|y` and `pivotX/Z`.
  - **Transforms** (`gdpc/transform.py`, `block_state_tools.py`): flip → rotate (90° steps in XZ; rotation 1 maps (1,0,0) to (0,0,1)) → translate. `rotatedBoxTransform(box, r)` maps a local box (0,0,0)-size to a world box under rotation by adding size−1 on x for r ∈ {1,2} and on z for r ∈ {2,3}. `transformFacing`, `rotateRotation` (sign 0–15) and `flipHalf` rewrite block states consistently.
  - **Editor performance** (`gdpc/editor.py`, `examples/tutorials/7_editor_performance.py`): buffered placement (bufferLimit 1024 blocks per request), an LRU block cache (8192), and optional multithreaded flush, with a warning that more than 1 worker can reorder writes.
  - Example settlement (`examples/emerald_city.py`): the road height is a running average of heights along both axes, and towers are only built where four probe blocks are the expected platform block (a "probe before build" check).
- **Usable for CIVITAS:**
  - **A "ground under vegetation" survey height:** scan columns down from the top and skip a transparent set (leaves, logs, our pw: leaf/log blocks, flowers, crops, saplings). Then the land survey and the plot score see the real ground in forests, and a log is not mistaken for a hill. On Bedrock: `dimension.getTopmostBlock` then step down while the block type is in the set, inside our runJob. Effort S, value 3.
  - **A single transform helper for template rotation** (flip → rotate → translate, with the size−1 offset rule) plus block-state rewrite for facing / sign rotation / half. This is useful if our gallery and furniture code places rotated pieces by hand. Effort S, value 2 (we likely have this already in `rotXZ`/`rotFor`).
  - **Placement without neighbour updates** when bulk-laying streets (Bedrock `structureManager.place` has no update flag. Use `fillBlocks` / `setPermutation` in jobs. There is nothing to borrow beyond the principle). Value 1.

### Microsoft minecraft-scripting-samples (TypeScript, Bedrock Script API; licence MIT; files examined: see list)

- **What it does:** official samples for Bedrock scripting (how-to gallery, the build-challenge game, editor extensions).
- **Mechanisms found:**
  - **runJob generator** (`howto-gallery/scripts/SystemRun.ts` `cubeGenerator`): `system.runJob(gen)` where the generator does one `setPermutation` per `yield`. The engine time-slices the job. It also shows a self-rescheduling `system.run(trapTick)` loop with a `currentTick % 1200` check, and `system.runInterval(fn, 600)`.
  - **Dynamic properties** (`DynamicProperties.ts`): a number property, and a **JSON blob in a string property**, with an explicit warning: "be very careful to ensure your serialized JSON str cannot exceed limits". It checks the parse result type before using it.
  - **Large scripted system** (`build-challenge/scripts/Challenge.ts`, `ChallengePlayer.ts`):
    - Game state is saved as many small world properties (`challenge:phase`, `challenge:size`, `nwbX/Y/Z`) plus JSON blobs for teams and players (`challenge:teamData`, `challenge:playerState`). Per-player values are stored on the player (`player.setDynamicProperty("challenge:teamId")`).
    - Loaded-area management: `tickingarea remove_all`, then **9 `tickingarea add` strips** cover the arena. The real work is deferred with `system.run` "so that tickingareas have a moment to get instated".
    - **Time-sliced scoring scan** (`updateCount(tick)`): each tick scans one team's pad and only one 1/16 slice of it (team index = floor(tick/16) % teams, slice = tick % 16).
    - **Canary check**: before scanning, it reads a known block. If it is not the expected type, the chunk is treated as unloaded and the scan is skipped.
    - `player.isValid` is checked before use.
  - Not found: structure placement via `world.structureManager` or entity-path patterns in these samples.
- **Usable for CIVITAS:**
  - **Canary-block loaded check** before any job touches a town area (read one known block of the square, such as our border stone. If it is not what we placed, skip this tick instead of acting on an unloaded or partially loaded area). Effort S, value 3. It guards against acting on air in unloaded chunks.
  - **Round-robin 1/16 slicing** for census-style scans (e.g. counter restock and house-occupancy checks: one town and one slice per tick) as a pattern for work that is not a generator. Effort S, value 2.
  - **Ticking areas for active construction sites** (Bedrock allows 10 per world): add one while a site is being built over days, and remove it when done. Effort S, value 3 (it lets builders finish when the player is away; check his Realm's limits).
  - Keep JSON blobs small and split by concern (we already do). Value 1.

### Village/structure packs — design study for our templates

#### Towns and Towers (Fabric/Forge jar 1.12, data pack; licence: the jar's LICENSE says CC BY-NC-ND 4.0 "no changes", the ledger says CC-BY-NC-SA-4.0; files examined: see list)
- **Mechanisms found:**
  - 27 village structures, one per biome style (Swiss meadow, Japanese flower forest, Viking snowy taiga, Polish old-growth taiga, Romanian birch, pueblo badlands, tipi wooded badlands, swamp boat, beach lighthouse, Polynesian sparse jungle…), plus 8 "exclusives" (tudor, iberian, mediterranean, nilotic, piglin, rustic, swedish, classic) (`worldgen/structure/*.json`).
  - Jigsaw `size` 3–7. `max_distance_from_center` 116 (80 for beach, grove, piglin, savanna plateau, snowy slopes). `terrain_adaptation: beard_thin`. Start projected to `WORLD_SURFACE_WG`.
  - Placement (`structure_set/towns.json`): random_spread spacing 48, separation 24 chunks, **exclusion zone 5 chunks from vanilla villages**. Towers use 48/24 at frequency 0.2 and exclusion 5 from towns.
  - Pools (`template_pool/village/meadow_swiss/*.json`):
    - town_centers: 1 meeting point (11×5×11).
    - streets: 12 pieces of equal weight (corners 20×15/20×20/5×5, crossroads 5×5…23×23, straights 3–4×15–17 and 15×11), `terrain_matching`, fallback → terminators (3 pieces).
    - houses: 17 buildings, weights 1–5 (small ×5, medium ×4, large ×4, job sites ×1–4, temple ×3), plus **empty weight 24 of 79 (≈30 % of sockets stay empty)**. All `rigid`.
    - decor: lamp 4 / feature 2 / empty 7. dogs: `terrain_matching`.
  - Footprints from the NBT `size` tags: small house 9×10×9; medium 9–12×10×11–13; large 17×12×13; temple 11×14×11; job sites 10–13 wide. Houses are 2–5 jigsaws, mostly villager spawns.
  - **Street pieces carry dense house sockets**: straight_01 (3×15) has 24 jigsaws, crossroad_04 (23×23) has 34. Many sockets compete, and the collision check keeps those that fit.
  - **Marker-block material randomiser** (`processor_list/village/street_meadow.json`): streets are authored in `cyan_concrete`. At placement, rule processors swap it for gravel (p 0.2), stone bricks (0.2), double andesite slab (0.2), else double stone slab, evaluated in order.
- **Usable for CIVITAS:**
  - **Placeholder-block randomiser for our kit streets and lanes:** author street templates with one marker block (e.g. `pw:street_marker`). After `structureManager.place`, a job replaces markers with a weighted palette per district or biome (worn cobble in poor quarters, dressed stone at the square). This needs a list of marker offsets per template, precomputed by our build tool so no scan is needed. Effort S–M, value 4.
  - **Empty-socket weight:** about 30 % of frontage slots are left empty on purpose (gardens, yards) instead of packing every metre. CIVITAS could apply an "empty" weight per district (low at the core, high at the edge). Effort S, value 3.
  - **Biome style sets as a design reference** for template families (one style per biome, 15–30 houses each). Value 2 (art direction, not code).

#### ChoiceTheorem's Overhauled Village — CTOV (Forge jar 3.4.14; licence BY-NC-ND-4.0 per mods.toml; files examined: see list)
- **Mechanisms found:**
  - **Size tiers as separate structures**: small / medium / large of each of 22 styles differ **only by jigsaw `size` 4 / 5 / 6** (same pools, `max_distance_from_center` 80, `beard_thin`) (`worldgen/structure/{small,medium,large}/village_plains.json`).
  - Plains pools (`template_pool/village/plains/*.json`): houses are 19 entries (small ×5, med ×2, big ×2 and 10 job sites, mostly weight 5; pen and farm weight 2), with **fallback → `deco` pool**. When a house does not fit, a deco piece is tried there instead: lamps ×4, well, hay bale, wagon, 4 features, empty 5 of 16. Roads are straight 4, three T-pieces, two bends and an intersection at 1 each, with fallback → terminator.
  - Footprints (NBT): small 7–9 × 8–11 × 8–9; med 9–11 × 10–16 × 15–17; big 10–13 × 13–16 × 11–15; road straight 3×9; T 12×21; intersection 21×21; town centre 17×10×17.
  - **Fortified variant** (`plains_fortified`): the same road set, a **28-tall town-centre keep (17×28×17)**, extra loomhouse/pen, the house list repeated 3× (weight 266) and no empty deco. Not found: a separate wall-ring piece in the pools I opened.
- **Usable for CIVITAS:**
  - **Fallback-to-decor when no house fits a slot:** if `kitSlot` finds frontage too short for the smallest cottage, place a well, cart, lamp or hay template there, so the street has no bare gaps. Effort S, value 3.
  - **One pool, growing jigsaw depth = our tiers:** a reminder that tiers can share all templates and differ only by how far the network extends. Value 1 (we already grow in stages).

#### Better Villages (Forge jar 1.20.1-3.3.1; licence All Rights Reserved — study only; files examined: see list)
- **Mechanisms found:**
  - Replaces the vanilla plains/desert/savanna/snowy/taiga village NBTs (houses 28–36 per biome) and the placement: `StructureSetMixin` swaps the vanilla villages' placement for its own config (`Config.class`: spacing 45, separation 20, salt 10387312). The changelog says this is "to prevent villages from being too close".
  - **Street pieces are 48 blocks tall** (`village/plains/streets/*.nbt`, e.g. straight_01 30×48×24 with 34 409 air of 34 560 blocks; the content lies at y 0–2 and the jigsaws at y 1). The tall air volume **clears trees and overhangs above every street** and reserves headroom, so no house or terrain feature intrudes over the road.
  - The changelog notes armour stands, banners and item frames were reduced "to improve performance", and "fix some buildings to improve villagers' mobility".
- **Usable for CIVITAS:**
  - **Street-headroom clearing:** give each kit street template (or a follow-up `fillBlocks` air job) a tall air volume over the carriageway (e.g. 12–16 high), so leaves and overhangs of BIGCANOPY trees never hang into streets where villagers walk. Note this interacts with our falling-tree rules (clearing is not felling). Effort S, value 3.
  - Keep entity decorations (armour stands, item frames) out of templates for performance. Value 2.

#### Villages&Pillages (Forge jar 2.0.0; licence CC-BY-NC-ND-4.0 per mods.toml; files examined: see list)
- **Mechanisms found:**
  - Witch village: jigsaw size 7, start at absolute Y 64, max distance 63, and spawn overrides by piece bounding box (witches 4–8, cats 2–4). Placement spacing 24 / separation 16 (`worldgen/structure/village_witch.json`, `structure_set/village_witch.json`).
  - Pools (`template_pool/village_witch/*.json`): **roads and houses share one pool** (4-, 3-, 2- and 1-way crossroads, short/medium/long roads, damaged/broken one-ways, small and medium houses), so roads and houses alternate freely. Terminators: dead end 5, short 4, medium 3, long 2, broken 1. Decoration: empty 100 vs cages 8+8 and dead trees 3×3.
  - **PillarProcessor** (`common/world/processor/PillarProcessor.class`, configured in `processor_list/village_witch*.json`): a marker block in the template (brown concrete → oak wood, light-grey concrete → mossy cobblestone wall) is replaced by the output block, and then a column of it is **extended downward through air and fluid until the first solid block**, optionally up to `pillar_length`. Only cells inside the current chunk are processed. This gives **automatic stilts and foundations** for houses over swamp water or slopes.
  - **Flatness check** (`checks/StructureFlatnessCheck.class`, `StructurePieceSampler.class`): it samples the 4 corners + centre of every main piece (ignoring pieces ≤ 2 wide and pieces inside others), merges samples in touching chunks, and orders them by distance from the centre. Then it **rejects the whole village if the `OCEAN_FLOOR_WG` heights span more than 12**.
  - Custom terrain adaptation (`VillageWitchTerrainAdaptation.class`): a 48³ Gaussian kernel exp(−d²/96) that only carves density above piece bottoms (densityModifier −1 above, 0 below). That is "beard" without the fill.
- **Usable for CIVITAS:**
  - **Pillar markers for hillside and riverside homes:** templates carry `pw:pillar_marker` blocks under corner posts. After placement, a runJob replaces each marker with the post block and extends it down to solid ground (stopping at a cap such as 16). This is what our `allowStilts` path needs, without per-template stilt variants. The marker offsets are precomputed per template in our build tool. Effort S, value 4.
  - **Site-level flatness veto:** before founding a town or a new district, sample the corners and centres of the planned blocks and refuse if the span is > 12 (or our own threshold). This is a cheap first gate before the full survey. Effort S, value 3.
  - **Mixed road+house pool** for informal hamlets (no kit streets): alternate road pieces and houses for an organic small settlement or a squatters' edge. Effort M, value 2.

#### Medieval Buildings (Forge jar 1.1.3; licence All Rights Reserved — study only; files examined: see list)
- **Mechanisms found:**
  - 5 single-piece structures (jigsaw size 1, no jigsaw blocks): house_1 13×16×12, house_2 18×12×23, tower 12×30×12, ship 13×35×39, and a **fort 68×30×55** (109 905 blocks, 28 saved entities; the dominant blocks are stripped spruce logs 1370 = palisade, farmland/wheat 529 each).
  - Placement: houses / tower / fort share one set with spacing **105** / separation 77 chunks, weights 2/3/2/2, and an **exclusion zone of 10 chunks from vanilla villages**. The ship is 90/50 (`structure_set/*.json`).
  - **Post-placement fix-ups via a 1-second function loop** (`functions/main_1s.mcfunction`):
    - A `marker` entity tagged `shipmarker` saved in the ship template triggers `remove_ship_water`: fill air over water in a 27×7×27 box, then un-waterlog stairs, slabs and trapdoors by `fill … replace`.
    - Villagers with a helmet inside the fort (`predicates/in_fort.json`) are replaced (`replace_villagers`: summon a fresh villager tagged `fixed`, teleport the old one to y −65).
- **Usable for CIVITAS:**
  - **Marker entity inside a template for post-placement scripts:** save an invisible `pw:fixup_marker` entity in a .mcstructure. When the structure loads, our `entitySpawn`/`entityLoad` handler reads its tag (e.g. `fix:dewater`, `fix:stock_counter`, `fix:assign_job`) and runs the fix-up once, then removes the marker. It suits staged builds that finish while the player is away. Effort S, value 3.
  - **Spacing reference:** isolated big sites about 105 chunks apart with a 10-chunk exclusion from villages, and village spacing of 45/20 (Better Villages) or 48/24 + 5 exclusion (T&T). These are useful numbers if CIVITAS ever founds new settlements by migration. Value 2.

---

## Top ideas from this group (ranked)

1. **Ward "rateLocation" scoring + growth ladder from watabou** on top of our DISTRICT table. District kinds unlock in watabou's queue order (temple early, town hall mid, poor and rich quarters ~17–20, barracks and park late). Each kind picks its lot by its rule: merchants near the square; temple and town hall facing the square, large lots preferred; no two markets adjacent; rich next to parks and away from poor; barracks on the wall or palace; poor farthest out. S–M, value 4.
2. **Plot suitability score (RoadWeaver `scoreFootprint`)** in the land survey and slot choice: water ≤ 8 %, 20–80-percentile height range, IQR, variance and road delta, instead of max−min. Ranks hillside lots and stops one boulder from vetoing a lot. S, value 4.
3. **Marker-block post-processors in our templates:** pillar markers that extend to the ground (V&P `PillarProcessor`) for stilts and foundations, plus a placeholder street block replaced by a weighted palette per district or biome (T&T `street_meadow`). The marker offsets are precomputed per template by the build tool. S–M, value 4.
4. **Gate and wall rules from watabou `CurtainWall`:** gates only where a street meets the wall, no two adjacent gates, towers on every other wall vertex, split the outer lot so an exit road fits, and gate suburbs outside the wall with probability 1 − 1/(n−5) as the GREENBELT exception. S, value 3.
5. **Fallback decor + intentional empty sockets:** CTOV's house→deco fallback (well/cart/lamp when a slot is too small) and T&T's ~30 % empty house weight (gardens), scaled by district (dense core, loose edge). S, value 3.
6. **Inter-town network:** Routes' mutual-kNN with 30° thinning + RNG + Gabriel loop closing + tier-scaled road counts + **fork trunks** (one road leaves a gate, then forks). Alternatives: RoadArchitect's planar greedy (reject crossing edges) for towns added over time, and RoadWeaver's SnapBranch for T-junctions onto existing roads. M, value 3.
7. **Better road costs and profiles for country roads and lanes:** RoadWeaver's contour-alignment discount (0.45·min(1, 2|∇h|)) and soft/hard grade penalties (8 % / 15 %); the two-pass slope clamp (≤ 1 block per 2 cells); slabs on half-steps; RoadArchitect's median + clamp + de-spike; and partial-path acceptance at ≥ 80 % progress. S–M, value 3.
8. **Zone names and "Now entering" titles (Routes):** a unique name ledger, biome-prefix + suffix names for districts and countryside, and a zone check every 20 ticks (core 48 / outskirts 96 / road 28) that sends an action-bar title on change. S, value 3.
9. **Street headroom clearing (Better Villages' 48-tall street pieces):** clear a tall air volume over the carriageway at placement so canopies never hang into streets. S, value 3.
10. **Robust job hygiene (MS samples):** a canary-block loaded check before acting on a town area, ticking areas for active building sites, and round-robin 1/16 slicing for periodic scans. S, value 3.
11. **Marker entity fix-ups in templates (Medieval Buildings):** a hidden entity in the .mcstructure triggers a one-time script (dewater, stock counter, assign workplace). S, value 3.
12. **Roadside ribbon hamlets (RoadWeaver):** overflow homes grow along the road to the next town (window curve 0–70°, stride 2, a gap after every 3, height step ≤ 3). M, value 3.
13. **Ground-under-vegetation survey height (GDMC `MOTION_BLOCKING_NO_PLANTS`)** so forests do not read as hills. S, value 3.

## Files examined

Intake ledgers:
/home/claude/_intake/civmods/source/LEDGER.json
/home/claude/_intake/civmods/modrinth/LEDGER.json
/home/claude/_intake/civmods/curseforge/LEDGER.json

Countered's Settlement Roads (source tar Coun7ered__settlement-roads-new.tar.gz; jar countereds-settlement-roads__settlement-roads-2.0.1.jar):
LICENSE (source)
changelog.md
src/main/java/net/countered/settlementroads/features/roadlogic/RoadPathCalculator.java
src/main/java/net/countered/settlementroads/features/roadlogic/Road.java
src/main/java/net/countered/settlementroads/features/RoadFeature.java
src/main/java/net/countered/settlementroads/config/ModConfig.java
src/main/java/net/countered/settlementroads/helpers/StructureConnector.java
src/main/java/net/countered/settlementroads/helpers/StructureLocator.java
src/main/java/net/countered/settlementroads/helpers/Records.java
src/main/java/net/countered/settlementroads/events/ModEventHandler.java
src/main/java/net/countered/settlementroads/features/config/RoadFeatureConfig.java
src/main/java/net/countered/settlementroads/features/config/ModConfiguredFeatures.java
src/main/java/net/countered/settlementroads/features/decoration/RoadStructures.java
src/main/java/net/countered/settlementroads/features/decoration/Decoration.java
src/main/java/net/countered/settlementroads/features/decoration/OrientedDecoration.java
src/main/java/net/countered/settlementroads/features/decoration/DistanceSignDecoration.java
src/main/java/net/countered/settlementroads/features/decoration/LamppostDecoration.java
src/main/java/net/countered/settlementroads/features/decoration/FenceWaypointDecoration.java
src/main/java/net/countered/settlementroads/features/decoration/util/WoodSelector.java
src/main/generated/data/settlement-roads/worldgen/placed_feature/road_feature_placed.json
jar: (listing), LICENSE_settlement-roads, net/countered/settlementroads/features/roadlogic/RoadPathCalculator.class, net/countered/settlementroads/features/RoadFeature.class

RoadWeaver (source tar shiroha-233__RoadWeaver.tar.gz; jar roadweaver-forge-2.3.0-1.20.1.jar listing):
LICENSE
gradle.properties
common/.../planning/NetworkPlannerFactory.java
common/.../planning/impl/MSTPlanner.java
common/.../planning/impl/RNGPlanner.java
common/.../planning/impl/KNNPlanner.java
common/.../planning/impl/SnapBranchPlanner.java
common/.../config/sub/PlanningConfig.java
common/.../core/constants/RoadConstants.java
common/.../pathfinding/impl/BasicAStarPathfinder.java
common/.../pathfinding/impl/PotentialFieldPathfinder.java
common/.../pathfinding/impl/TerrainGradientHelper.java
common/.../pathfinding/impl/PathPostProcessor.java
common/.../pathfinding/impl/ThrottleHelper.java
common/.../features/path/pathlogic/pathfinding/HeightProfileService.java
common/.../features/path/pathlogic/pathfinding/RoadHeightInterpolator.java
common/.../features/path/pathlogic/pathfinding/BridgeTransitionAdjuster.java
common/.../features/path/pathlogic/core/SegmentPaver.java
common/.../features/path/pathlogic/core/StructureAvoidanceService.java (grep)
common/.../features/path/pathlogic/core/Road.java (grep)
common/.../features/path/pathlogic/bridge/BridgeBuilder.java
common/.../features/path/pathlogic/bridge/BridgeRangeCalculator.java
common/.../features/path/pathlogic/bridge/BridgeSegmentPlanner.java (grep)
common/.../features/path/PathFeature.java (grep)
common/.../features/path/decoration/system/DecorationPlanner.java
common/.../structures/precompute/RoadsideVillagePrecomputer.java
common/.../postprocess/RoadSnapService.java

RoadArchitect (source tar 0xCoDSnet__RoadArchitect.tar.gz):
LICENSE
modules/common/.../util/PathFinder.java
modules/common/.../util/TerrainAnalyzer.java
modules/common/.../handlers/PathFinderManager.java
modules/common/.../handlers/RoadPostProcessor.java
modules/common/.../storage/RoadGraphState.java
modules/common/.../storage/EdgeStorage.java (grep)
modules/common/.../config/RoadArchitectConfigData.java (grep)
modules/common/.../config/defaults/RoadStyleDefaults.java
modules/common/.../worldgen/RoadFeature.java (grep)

Routes (jar routes__routes-neoforge-1.2.119.jar):
(listing)
LICENSE
assets/routes/lang/en_us.json
com/routes/gen2/Gen2Names.class
com/routes/gen2/Gen2NameLedger.class
com/routes/gen2/SettlementGraph.class
com/routes/config/RoutesConfig.class
com/routes/route/AreaRegions.class
com/routes/route/ZonePaint.class
com/routes/route/RouteTracker.class

Medieval Fantasy City Generator (source tar watabou__TownGeneratorOS.tar.gz):
LICENSE
Source/com/watabou/towngenerator/building/Model.hx
Source/com/watabou/towngenerator/building/CurtainWall.hx
Source/com/watabou/towngenerator/building/Topology.hx
Source/com/watabou/towngenerator/building/Cutter.hx
Source/com/watabou/towngenerator/building/Patch.hx
Source/com/watabou/towngenerator/wards/Ward.hx
Source/com/watabou/towngenerator/wards/AdministrationWard.hx
Source/com/watabou/towngenerator/wards/Castle.hx
Source/com/watabou/towngenerator/wards/Cathedral.hx
Source/com/watabou/towngenerator/wards/CommonWard.hx
Source/com/watabou/towngenerator/wards/CraftsmenWard.hx
Source/com/watabou/towngenerator/wards/Farm.hx
Source/com/watabou/towngenerator/wards/GateWard.hx
Source/com/watabou/towngenerator/wards/Market.hx
Source/com/watabou/towngenerator/wards/MerchantWard.hx
Source/com/watabou/towngenerator/wards/MilitaryWard.hx
Source/com/watabou/towngenerator/wards/Park.hx
Source/com/watabou/towngenerator/wards/PatriciateWard.hx
Source/com/watabou/towngenerator/wards/Slum.hx
Source/com/watabou/towngenerator/ui/CitySizeButton.hx
Source/com/watabou/towngenerator/TownScene.hx (grep)
Source/com/watabou/towngenerator/Main.hx (grep)
Source/com/watabou/geom/Graph.hx
Source/com/watabou/geom/Voronoi.hx (relax/build)

GDPC (source tar avdstaaij__gdpc.tar.gz):
LICENSE
src/gdpc/world_slice.py
src/gdpc/editor.py
src/gdpc/transform.py
src/gdpc/editor_tools.py
src/gdpc/block_state_tools.py (grep)
src/gdpc/geometry.py (grep)
examples/emerald_city.py
examples/tutorials/7_editor_performance.py

GDMC HTTP interface (source tar Niels-NTG__gdmc_http_interface.tar.gz):
LICENSE
docs/Endpoints.md
common/src/main/java/nl/nielspoldervaart/gdmc/common/utils/CustomHeightmap.java

Microsoft minecraft-scripting-samples (source tar microsoft__minecraft-scripting-samples.tar.gz):
LICENSE
howto-gallery/scripts/DynamicProperties.ts
howto-gallery/scripts/SystemRun.ts
build-challenge/scripts/Challenge.ts
build-challenge/scripts/ChallengePlayer.ts (grep)

Towns and Towers (jar towns-and-towers__Towns-and-Towers-1.12-Fabric+Forge.jar):
(listing)
LICENSE
data/towns_and_towers/worldgen/structure/*.json (27 village_* + exclusives/village_* read for size/distance/adaptation)
data/towns_and_towers/worldgen/structure/village_meadow.json
data/towns_and_towers/worldgen/structure_set/towns.json
data/towns_and_towers/worldgen/structure_set/towers.json
data/towns_and_towers/worldgen/structure_set/other.json
data/kaisyn/worldgen/template_pool/village/meadow_swiss/{decor,dogs,houses,streets,terminators,town_centers}.json
data/kaisyn/worldgen/processor_list/village/street_meadow.json
data/kaisyn/structures/village/meadow_swiss/houses/*.nbt (17)
data/kaisyn/structures/village/meadow_swiss/streets/*.nbt (12)
data/kaisyn/structures/village/meadow_swiss/town_centers/meadow_meeting_point_1.nbt

ChoiceTheorem's Overhauled Village (jar choicetheorems-overhauled-village__[forge]ctov-3.4.14.jar):
(listing)
META-INF/mods.toml
data/ctov/worldgen/structure/small/village_plains.json
data/ctov/worldgen/structure/medium/village_plains.json
data/ctov/worldgen/structure/large/village_plains.json
data/ctov/worldgen/template_pool/village/plains/{deco,house,roads,terminator,town_centers}.json
data/ctov/worldgen/template_pool/village/plains_fortified/{deco,house,roads,terminator,town_centers}.json
data/ctov/structures/village/plains/town_center.nbt
data/ctov/structures/village/plains/roads/*.nbt (9)
data/ctov/structures/village/plains/house/*.nbt (9)
data/ctov/structures/village/plains_fortified/town_center.nbt
data/ctov/structures/village/plains_fortified/roads/*.nbt (9)

Better Villages (jar better-village-forge__bettervillage-forge-1.20.1-3.3.1-all.jar):
(listing)
license_bettervillage.txt
changelog.md
com/jtorleonstudios/bettervillage/Config.class
com/jtorleonstudios/bettervillage/mixin/StructureSetMixin.class
com/jtorleonstudios/bettervillage/mixin/AbstractDecorationEntityMixin.class
com/jtorleonstudios/bettervillage/compat/CompatResourcesListener.class
data/bettervillage/bettervillage_compat/morevillager.json
data/minecraft/structures/village/plains/streets/*.nbt (16)
data/minecraft/structures/village/plains/town_centers/*.nbt (4)

Villages&Pillages (jar villages-and-pillages__villagesandpillages-forge-2.0.0+mc1.20.1.jar):
(listing)
META-INF/mods.toml
com/faboslav/villagesandpillages/common/world/processor/PillarProcessor.class
com/faboslav/villagesandpillages/common/world/checks/StructureFlatnessCheck.class
com/faboslav/villagesandpillages/common/world/checks/StructurePieceSampler.class
com/faboslav/villagesandpillages/common/world/structures/terrain/VillageWitchTerrainAdaptation.class
data/villagesandpillages/worldgen/structure/village_witch.json
data/villagesandpillages/worldgen/structure_set/village_witch.json
data/villagesandpillages/worldgen/processor_list/village_witch.json
data/villagesandpillages/worldgen/processor_list/village_witch_house.json
data/villagesandpillages/worldgen/template_pool/village_witch/{center,decoration,road_and_house,terminators}.json

Medieval Buildings (jar medieval-buildings__medieval_buildings-1.20.1-1.1.3-forge.jar):
(listing)
META-INF/mods.toml
data/medieval_buildings/worldgen/structure/{fort,house_1,house_2,ship,tower}.json
data/medieval_buildings/worldgen/structure_set/houses.json
data/medieval_buildings/worldgen/structure_set/ship.json
data/medieval_buildings/functions/{load,main_1s,remove_ship_water,replace_villagers}.mcfunction
data/medieval_buildings/predicates/in_fort.json
data/medieval_buildings/structures/{fort,house_1,house_2,ship,tower}.nbt

CIVITAS context (read to avoid duplicating existing work):
/home/claude/tools/bp02_src_227/pw_civ_clock.js (DISTRICT table and kitSlot, lines ~3808–3860)
/home/claude/tools/bp02_src_227/pw_civ_streets.js (export list)
/home/claude/tools/bp02_src_227/pw_civ_land.js (export list)
/home/claude/tools/bp02_src_227/pw_civ_lanes.js (export list)
/home/claude/_docs/GROWTH-PROGRAM-2026-10-05.md (grep: districts/walls)
