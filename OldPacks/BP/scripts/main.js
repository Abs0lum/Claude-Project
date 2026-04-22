import {
  world,
  system,
  ItemStack,
  BlockPermutation,
  EntityDamageCause,
} from "@minecraft/server";

// ---- Diagnostics --------------------------------------------------------
// v2.7.5 DEBUG-ON: dev build. Chat trace restored so in-world testing produces
// visible event log per tree chop. For realm/multiplayer hosting flip DEBUG
// to false (matches v2.7.4 NOCHAT behavior). Content-log output always goes
// to console.warn regardless; only chat visibility is gated.
const DEBUG = true;
function log(msg) {
  if (DEBUG) {
    try { world.sendMessage(`§a[BIGCANOPY] §f${msg}`); } catch {}
  }
  try { console.warn(`[BIGCANOPY] ${msg}`); } catch {}
}

log("script loaded");

// ---- Species ------------------------------------------------------------
const SPECIES = [
  { key: "oak",      logs: ["minecraft:oak_log",      "minecraft:stripped_oak_log"],      drop: "minecraft:oak_log",      leaves: ["minecraft:oak_leaves"] },
  { key: "spruce",   logs: ["minecraft:spruce_log",   "minecraft:stripped_spruce_log"],   drop: "minecraft:spruce_log",   leaves: ["minecraft:spruce_leaves"] },
  { key: "birch",    logs: ["minecraft:birch_log",    "minecraft:stripped_birch_log"],    drop: "minecraft:birch_log",    leaves: ["minecraft:birch_leaves"] },
  { key: "jungle",   logs: ["minecraft:jungle_log",   "minecraft:stripped_jungle_log"],   drop: "minecraft:jungle_log",   leaves: ["minecraft:jungle_leaves"] },
  { key: "acacia",   logs: ["minecraft:acacia_log",   "minecraft:stripped_acacia_log"],   drop: "minecraft:acacia_log",   leaves: ["minecraft:acacia_leaves"] },
  { key: "dark_oak", logs: ["minecraft:dark_oak_log", "minecraft:stripped_dark_oak_log"], drop: "minecraft:dark_oak_log", leaves: ["minecraft:dark_oak_leaves"] },
  { key: "mangrove", logs: ["minecraft:mangrove_log", "minecraft:stripped_mangrove_log"], drop: "minecraft:mangrove_log", leaves: ["minecraft:mangrove_leaves"] },
  { key: "cherry",   logs: ["minecraft:cherry_log",   "minecraft:stripped_cherry_log"],   drop: "minecraft:cherry_log",   leaves: ["minecraft:cherry_leaves"] },
  { key: "crimson",  logs: ["minecraft:crimson_stem", "minecraft:stripped_crimson_stem"], drop: "minecraft:crimson_stem", leaves: ["minecraft:nether_wart_block"] },
  { key: "warped",   logs: ["minecraft:warped_stem",  "minecraft:stripped_warped_stem"],  drop: "minecraft:warped_stem",  leaves: ["minecraft:warped_wart_block"] },
];

const LOG_TO_SPECIES = new Map();
for (let i = 0; i < SPECIES.length; i++) {
  for (const id of SPECIES[i].logs) LOG_TO_SPECIES.set(id, i);
}

// v2.8.0 WIDEGRID: ft:wood_type (0..9) now drives geometry selection directly.
// The render_controller array Array.species_geos is ordered exactly to match
// the SPECIES array above:
//   0=oak, 1=spruce, 2=birch, 3=jungle, 4=acacia,
//   5=dark_oak, 6=mangrove, 7=cherry, 8=crimson, 9=warped
// Each has its own geometry with a canopy laid out within a unified 7×7
// entity envelope. Per-species canopy cube counts (from geo file):
//   oak 4, spruce 6, birch 4, jungle 8, acacia 2, dark_oak 4, mangrove 4,
//   cherry 4, crimson 5, warped 5.
// ft:canopy_size property is removed.

// Terminal fall angle (degrees, Z-axis rotation) based on downhill drop.
// Flat ground: -90° (tree lies flat). Each block of downhill drop adds ~4° of
// "overshoot" so the trunk follows the slope contour. Clamped to keep animation
// keyframe scaling (which uses fall_angle * multipliers) from overshooting visually.
function computeFallAngle(drop) {
  const raw = -90 - Math.max(0, drop) * 4;
  return Math.max(-135, Math.min(-80, Math.round(raw)));
}

// Collision-test predicate — returns true if a block should stop the falling
// trunk. Stricter than the pre-fall corridor obstacle test: we don't want to
// stop on grass/snow/leaves/plants, only on hard structure.
function isFallCollider(id) {
  if (!id || id === "minecraft:air") return false;
  if (id.includes("water") || id.includes("lava")) return false;
  if (id.includes("_leaves") || id.includes("_wart_block")) return false;
  if (id.includes("sapling") || id.includes("grass") ||
      id.includes("fern") || id.includes("flower") ||
      id.includes("bush") || id.includes("vine") ||
      id.includes("lichen") || id === "minecraft:snow" ||
      id.includes("tallgrass")) return false;
  if (id.endsWith("_log") || id.endsWith("_stem") ||
      id.endsWith("_wood") || id.endsWith("_hyphae")) return true;
  if (id.includes("stone") || id.includes("dirt") ||
      id.includes("deepslate") || id.includes("cobbled") ||
      id.includes("bricks") || id.includes("planks") ||
      id.includes("fence") || id.includes("wall") ||
      id.includes("concrete") || id.includes("terracotta") ||
      id.includes("copper") || id.includes("iron_block") ||
      id.includes("glass") || id.includes("gravel") ||
      id.includes("sand") || id.endsWith("_ore")) return true;
  return false;
}

// Fall-animation keyframes as [time_seconds, angle_multiplier_of_terminal]
// pairs. Matches the keyframes in falling_tree.animation.json so JS
// interpolation lines up with what the renderer is showing on screen.
const FALL_KEYS = [
  [0.00, 0.000],
  [0.35, 0.044],
  [0.90, 0.333],
  [1.40, 0.867],
  [1.65, 1.033],  // overshoot
  [1.72, 0.956],  // bounce
  [1.80, 1.000],  // terminal rest
];

function fallAngleAtTime(elapsedS, terminalDeg) {
  if (elapsedS <= 0) return 0;
  if (elapsedS >= 1.8) return terminalDeg;
  for (let i = 0; i < FALL_KEYS.length - 1; i++) {
    const [t0, k0] = FALL_KEYS[i];
    const [t1, k1] = FALL_KEYS[i + 1];
    if (elapsedS >= t0 && elapsedS <= t1) {
      const frac = (elapsedS - t0) / (t1 - t0);
      return terminalDeg * (k0 + (k1 - k0) * frac);
    }
  }
  return terminalDeg;
}

const EXTRA_LEAF_IDS = [
  "minecraft:azalea_leaves",
  "minecraft:flowering_azalea_leaves",
  "minecraft:pale_oak_leaves",
];

// ---- Config -------------------------------------------------------------
const MAX_LOGS = 180;
const MAX_LEAVES = 260;
const FALL_DURATION_TICKS = 36; // 1.8s — must match animation_length
const REST_TICKS = 20;          // 1s rest on ground before despawn
const DESPAWN_BUFFER_TICKS = 3;

// ---- Neighborhood -------------------------------------------------------
const NEIGHBORS_26 = (() => {
  const a = [];
  for (let dx = -1; dx <= 1; dx++)
    for (let dy = -1; dy <= 1; dy++)
      for (let dz = -1; dz <= 1; dz++)
        if (dx || dy || dz) a.push({ x: dx, y: dy, z: dz });
  return a;
})();

// 6-direction orthogonal (face-adjacent) neighbors, used for leaf decay
// (leaves only propagate through face-connected neighbors, matching vanilla)
const NEIGHBORS_6 = [
  { x: 1, y: 0, z: 0 }, { x: -1, y: 0, z: 0 },
  { x: 0, y: 1, z: 0 }, { x: 0, y: -1, z: 0 },
  { x: 0, y: 0, z: 1 }, { x: 0, y: 0, z: -1 },
];

const AXE_RE = /_axe$/;

// ---- Helpers ------------------------------------------------------------
const posKey = (x, y, z) => `${x},${y},${z}`;

function findConnectedTree(dim, seed, startY, speciesLogs, speciesIdx) {
  const found = [];
  const visited = new Set();
  const queue = [seed];
  visited.add(posKey(seed.x, seed.y, seed.z));

  while (queue.length && found.length < MAX_LOGS) {
    const p = queue.shift();
    let block;
    try { block = dim.getBlock(p); } catch { continue; }
    if (!block || !speciesLogs.has(block.typeId)) continue;
    found.push({ x: p.x, y: p.y, z: p.z });

    for (const n of NEIGHBORS_26) {
      if (p.y + n.y < startY) continue;
      const nx = p.x + n.x, ny = p.y + n.y, nz = p.z + n.z;
      const key = posKey(nx, ny, nz);
      if (visited.has(key)) continue;
      visited.add(key);
      queue.push({ x: nx, y: ny, z: nz });
    }
  }

  // v2.7.2 ACACIABRIDGE: acacia trees (speciesIdx 4) have L-shaped /
  // horizontal branch structures where log chunks can be separated by
  // leaves or 1-2 air blocks. The standard 26-adjacency BFS misses them.
  //
  // v2.7.1 attempted this with a second pass but shared the `visited` set
  // with phase 1, which had already marked every 26-neighbor of every
  // found log as visited during its enqueue phase (non-log cells get
  // visited.add() then continue; — they're visited but not expanded).
  // That meant phase 2's initial enumeration found every candidate cell
  // already in `visited` and enqueued nothing. The bridging pass was
  // inert. v2.7.2 gives phase 2 its own visited set, seeded only with
  // the found log positions, so neighbor enumeration can actually start.
  if (speciesIdx === 4 && found.length > 0 && found.length < MAX_LOGS) {
    const BRIDGE_RANGE = 2;  // how many air/leaf blocks we'll traverse

    // Separate visited set for phase 2. Seed with ONLY the found logs
    // so phase 2 doesn't re-add them, but all other cells are open for
    // traversal regardless of what phase 1 touched.
    const bridgeVisited = new Set();
    for (const p of found) bridgeVisited.add(posKey(p.x, p.y, p.z));

    // Queue of (pos, bridgesRemaining) pairs
    const bridgeQueue = [];
    for (const p of found) {
      for (const n of NEIGHBORS_26) {
        if (p.y + n.y < startY) continue;
        const nx = p.x + n.x, ny = p.y + n.y, nz = p.z + n.z;
        const key = posKey(nx, ny, nz);
        if (bridgeVisited.has(key)) continue;
        bridgeVisited.add(key);
        bridgeQueue.push({ x: nx, y: ny, z: nz, bridges: BRIDGE_RANGE });
      }
    }
    while (bridgeQueue.length && found.length < MAX_LOGS) {
      const p = bridgeQueue.shift();
      let block;
      try { block = dim.getBlock(p); } catch { continue; }
      if (!block) continue;
      const id = block.typeId;
      if (speciesLogs.has(id)) {
        // Found a bridged log — add it and continue BFS from it with
        // a fresh bridge budget.
        found.push({ x: p.x, y: p.y, z: p.z });
        for (const n of NEIGHBORS_26) {
          if (p.y + n.y < startY) continue;
          const nx = p.x + n.x, ny = p.y + n.y, nz = p.z + n.z;
          const key = posKey(nx, ny, nz);
          if (bridgeVisited.has(key)) continue;
          bridgeVisited.add(key);
          bridgeQueue.push({ x: nx, y: ny, z: nz, bridges: BRIDGE_RANGE });
        }
      } else if (p.bridges > 0 &&
                 (id === "minecraft:air" || id.endsWith("_leaves"))) {
        // Traverse through this non-log block — decrement bridge budget
        for (const n of NEIGHBORS_26) {
          if (p.y + n.y < startY) continue;
          const nx = p.x + n.x, ny = p.y + n.y, nz = p.z + n.z;
          const key = posKey(nx, ny, nz);
          if (bridgeVisited.has(key)) continue;
          bridgeVisited.add(key);
          bridgeQueue.push({ x: nx, y: ny, z: nz, bridges: p.bridges - 1 });
        }
      }
      // else: solid non-log block — stop traversal this branch
    }
  }

  return found;
}

/**
 * Connectivity-based leaf decay, mirroring vanilla behavior:
 *
 * A leaf is broken ONLY IF every path of connected leaves from it to a
 * log (within LEAF_DECAY_RANGE steps) leads to a FELLED log, i.e. there
 * is no standing log reachable within range.
 *
 * Approach:
 *   1. Gather all candidate leaves: any species-leaf within a generous
 *      search volume around felled logs.
 *   2. BFS outward from every STANDING log nearby, tagging leaves that
 *      are reachable within RANGE. Those leaves are "protected".
 *   3. Break any candidate leaf that is NOT protected.
 */
function cleanOrphanLeaves(dim, logPositions, speciesIdx) {
  const LEAF_DECAY_RANGE = 6;
  const SEARCH_HALF = LEAF_DECAY_RANGE + 1;
  const speciesLeaves = new Set([
    ...SPECIES[speciesIdx].leaves,
    ...EXTRA_LEAF_IDS,
  ]);

  const felledSet = new Set(logPositions.map(p => posKey(p.x, p.y, p.z)));
  const anyLogIds = new Set();
  for (const s of SPECIES) for (const id of s.logs) anyLogIds.add(id);

  const safeGet = (p) => { try { return dim.getBlock(p); } catch { return null; } };
  const isSpeciesLeaf = (b) => b && speciesLeaves.has(b.typeId);

  // Compute search AABB around all felled logs, clamped to LEAF_DECAY_RANGE
  let minX = Infinity, minY = Infinity, minZ = Infinity;
  let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
  for (const p of logPositions) {
    if (p.x < minX) minX = p.x; if (p.y < minY) minY = p.y; if (p.z < minZ) minZ = p.z;
    if (p.x > maxX) maxX = p.x; if (p.y > maxY) maxY = p.y; if (p.z > maxZ) maxZ = p.z;
  }
  minX -= SEARCH_HALF; minY -= SEARCH_HALF; minZ -= SEARCH_HALF;
  maxX += SEARCH_HALF; maxY += SEARCH_HALF; maxZ += SEARCH_HALF;

  // Step 1: gather all candidate leaves + find all STANDING logs in search AABB
  const candidates = new Map();  // leafKey -> pos
  const standingLogs = [];       // standing (not felled) logs within the search box
  let scanned = 0;
  for (let x = minX; x <= maxX; x++) {
    for (let y = minY; y <= maxY; y++) {
      for (let z = minZ; z <= maxZ; z++) {
        if (++scanned > 40000) break; // hard safety cap
        const p = { x, y, z };
        const k = posKey(x, y, z);
        const b = safeGet(p);
        if (!b) continue;
        if (isSpeciesLeaf(b)) {
          candidates.set(k, p);
        } else if (anyLogIds.has(b.typeId) && !felledSet.has(k)) {
          standingLogs.push(p);
        }
      }
    }
  }

  // Step 2: BFS from every standing log through connected species-leaves,
  // marking leaves as "protected" up to LEAF_DECAY_RANGE distance.
  const protectedSet = new Set();
  const dist = new Map();
  const queue = [];

  // Seed: every leaf directly adjacent (face-neighbor) to any standing log
  for (const sl of standingLogs) {
    for (const d of NEIGHBORS_6) {
      const p = { x: sl.x + d.x, y: sl.y + d.y, z: sl.z + d.z };
      const k = posKey(p.x, p.y, p.z);
      if (!candidates.has(k)) continue;
      if (dist.has(k)) continue;
      dist.set(k, 1);
      protectedSet.add(k);
      queue.push([p, 1]);
    }
  }

  // Expand through connected leaves
  let guard = 0;
  while (queue.length && guard++ < MAX_LEAVES * 16) {
    const [p, d] = queue.shift();
    if (d >= LEAF_DECAY_RANGE) continue;
    for (const step of NEIGHBORS_6) {
      const np = { x: p.x + step.x, y: p.y + step.y, z: p.z + step.z };
      const k = posKey(np.x, np.y, np.z);
      if (!candidates.has(k)) continue;
      if (dist.has(k)) continue;
      dist.set(k, d + 1);
      protectedSet.add(k);
      queue.push([np, d + 1]);
    }
  }

  // Step 3: break unprotected candidate leaves
  let broken = 0;
  for (const [k, p] of candidates) {
    if (broken >= MAX_LEAVES) break;
    if (protectedSet.has(k)) continue;
    try {
      dim.runCommand(`setblock ${p.x} ${p.y} ${p.z} air destroy`);
      broken++;
    } catch {}
  }
}

/**
 * Fall-direction picker. Tries to fall downhill, biased toward "away from
 * the player". We sample ground elevation in 8 compass directions at radius
 * 4 from the stump and score each by (player-awayness + downhill-ness).
 *
 * Returns a yaw in degrees so that the entity's -X local axis points in
 * the chosen direction (which is how the fall animation tips the trunk).
 */
function pickFallYaw(dim, player, stumpPos, trunkHeight) {
  const DIRS = 8;                      // sample 8 compass directions
  const RADIUS = 4;                    // blocks out from stump for ground sampling
  const VERTICAL_SEARCH = 6;           // how far up/down we scan for ground
  const DOWNHILL_WEIGHT = 1.5;         // vs awayness
  const AWAY_WEIGHT = 5.0;             // v2.7.0: hard prefer away-from-chopper
  const TOWARD_PLAYER_VETO = -0.3;     // v2.7.0: direction is vetoed if (dot with away-vec) < this
  const OBSTACLE_WEIGHT = 3.0;         // each obstacle heavily penalizes a direction
  const CANOPY_WIDTH = 2;              // half-width of trunk+canopy footprint (blocks each side)
  const CANOPY_HEIGHT = 3;             // how many blocks up to scan for canopy-level obstructions

  // Vector from player to stump (horizontal) = preferred away direction
  const pLoc = player.location;
  const ax = (stumpPos.x + 0.5) - pLoc.x;
  const az = (stumpPos.z + 0.5) - pLoc.z;
  const aLen = Math.hypot(ax, az) || 1;
  const awayX = ax / aLen;
  const awayZ = az / aLen;

  // Ground height at a sample point
  const groundYAt = (wx, wz) => {
    for (let dy = 3; dy >= -VERTICAL_SEARCH; dy--) {
      const p = { x: wx, y: stumpPos.y + dy, z: wz };
      let b;
      try { b = dim.getBlock(p); } catch { return stumpPos.y; }
      if (!b) continue;
      const id = b.typeId;
      if (id === "minecraft:air" ||
          id.endsWith("_leaves") ||
          id.endsWith("_log") ||
          id.endsWith("_stem") ||
          id.includes("sapling") ||
          id.includes("grass") ||
          id.includes("fern") ||
          id.includes("flower") ||
          id.includes("vine") ||
          id.includes("tallgrass")) continue;
      return stumpPos.y + dy;
    }
    return stumpPos.y - VERTICAL_SEARCH;
  };

  // Test whether a block ID counts as a "fall obstacle".
  // We want to count: other tree trunks, walls, buildings, cliffs/stone.
  // We don't want to count: air, grass, small plants, saplings, water, snow.
  const isObstacle = (id) => {
    if (!id || id === "minecraft:air") return false;
    // Logs and stems are the big ones — adjacent trees
    if (id.endsWith("_log") || id.endsWith("_stem") ||
        id.endsWith("_wood") || id.endsWith("_hyphae")) return true;
    // Solid building blocks
    if (id.includes("stone") || id.includes("dirt") ||
        id.includes("deepslate") || id.includes("cobbled") ||
        id.includes("bricks") || id.includes("planks") ||
        id.includes("fence") || id.includes("wall") ||
        id.includes("concrete") || id.includes("terracotta") ||
        id.endsWith("_ore") || id === "minecraft:gravel") return true;
    // Leaves count as a minor obstacle (adjacent tree canopy)
    if (id.endsWith("_leaves")) return true;
    // Plants, water, air, snow don't obstruct
    return false;
  };

  // Count obstacles in the corridor a fallen trunk would sweep.
  // The corridor is a rectangular column extending `trunkLen` blocks
  // from the stump in direction (dirX, dirZ), `CANOPY_WIDTH*2+1` blocks wide,
  // and `CANOPY_HEIGHT` blocks tall above ground.
  const countObstacles = (dirX, dirZ, trunkLen) => {
    let count = 0;
    // Perpendicular direction (for width sampling)
    const perpX = -dirZ;
    const perpZ = dirX;
    // Sample every 1-block step along the trunk, every width offset, every height layer
    // Start at step 1 so we don't count the stump itself.
    for (let step = 1; step <= trunkLen; step++) {
      for (let w = -CANOPY_WIDTH; w <= CANOPY_WIDTH; w++) {
        for (let dy = 0; dy < CANOPY_HEIGHT; dy++) {
          const wx = Math.round(stumpPos.x + dirX * step + perpX * w);
          const wz = Math.round(stumpPos.z + dirZ * step + perpZ * w);
          const wy = stumpPos.y + dy;
          let b;
          try { b = dim.getBlock({ x: wx, y: wy, z: wz }); } catch { continue; }
          if (!b) continue;
          if (isObstacle(b.typeId)) {
            // Weight canopy-height obstacles (dy>=1) more than ground-level ones,
            // because canopy collisions cause the visible landing-on-tree artifact.
            count += (dy >= 1 ? 2 : 1);
          }
        }
      }
    }
    return count;
  };

  const stumpGroundY = stumpPos.y;
  const trunkLen = Math.max(3, Math.min(8, trunkHeight));

  let bestScore = -Infinity;
  let bestYaw = Math.atan2(awayZ, -awayX) * 180 / Math.PI; // fallback: straight away

  // Debug: log each direction's breakdown
  const breakdown = [];

  for (let i = 0; i < DIRS; i++) {
    const theta = (i / DIRS) * Math.PI * 2;
    const dirX = Math.cos(theta);
    const dirZ = Math.sin(theta);

    // ground elevation drop (positive = downhill = good)
    const sx = Math.round(stumpPos.x + dirX * RADIUS);
    const sz = Math.round(stumpPos.z + dirZ * RADIUS);
    const gy = groundYAt(sx, sz);
    const drop = stumpGroundY - gy;

    // awayness: dot product with away-from-player unit vector
    const away = dirX * awayX + dirZ * awayZ;

    // obstacle count: lower = better, so subtract it
    const obstacles = countObstacles(dirX, dirZ, trunkLen);

    // v2.7.0: hard veto any direction that's meaningfully TOWARD the player.
    // 'away' near +1 means aligned with stump-minus-player vector (good).
    // 'away' near -1 means pointing AT the player (very bad — skip entirely).
    if (away < TOWARD_PLAYER_VETO) {
      breakdown.push({ i, dirX: +dirX.toFixed(2), dirZ: +dirZ.toFixed(2), away: +away.toFixed(2), drop, obstacles, score: -Infinity, vetoed: "toward_chopper" });
      continue;
    }

    // combined score — obstacles dominate, then away-from-player heavily, then downhill
    const score = (AWAY_WEIGHT * away) +
                  (DOWNHILL_WEIGHT * drop) -
                  (OBSTACLE_WEIGHT * obstacles);

    breakdown.push({ i, dirX: +dirX.toFixed(2), dirZ: +dirZ.toFixed(2), away: +away.toFixed(2), drop, obstacles, score: +score.toFixed(2) });

    if (score > bestScore) {
      bestScore = score;
      bestYaw = Math.atan2(dirZ, -dirX) * 180 / Math.PI;
    }
  }

  // Log the best pick and its obstacle count for debugging
  let bestDrop = 0;
  try {
    const best = breakdown.reduce((a, b) => (a.score > b.score ? a : b));
    bestDrop = best.drop;
    log(`fall dir: yaw=${bestYaw.toFixed(0)}° obst=${best.obstacles} drop=${best.drop} away=${best.away}`);
  } catch {}

  return { yaw: bestYaw, drop: bestDrop };
}

function findStumpY(logPositions) {
  let minY = Infinity;
  for (const p of logPositions) if (p.y < minY) minY = p.y;
  return minY;
}

function measureColumnHeight(logPositions, chopped) {
  const col = logPositions.filter(p => p.x === chopped.x && p.z === chopped.z);
  if (col.length === 0) return Math.max(2, Math.min(16, logPositions.length));
  let minY = Infinity, maxY = -Infinity;
  for (const p of col) {
    if (p.y < minY) minY = p.y;
    if (p.y > maxY) maxY = p.y;
  }
  return Math.max(2, maxY - minY + 1);
}

function isCreative(player) {
  // use runCommand-based test that works across all API versions
  try {
    const res = player.runCommand("testfor @s[m=creative]");
    return res && res.successCount > 0;
  } catch { return false; }
}

function dropItems(dim, pos, typeId, count) {
  const center = { x: pos.x + 0.5, y: pos.y + 0.5, z: pos.z + 0.5 };
  let remaining = count;
  while (remaining > 0) {
    const n = Math.min(64, remaining);
    try { dim.spawnItem(new ItemStack(typeId, n), center); } catch (e) { log(`spawnItem err: ${e}`); }
    remaining -= n;
  }
}

// ---- Axe damage (uses generic string component IDs for max compat) ------
function applyAxeDamage(player, extraBlocks) {
  if (extraBlocks <= 0) return;
  try {
    const equippable = player.getComponent("minecraft:equippable");
    if (!equippable) return;
    const slot = equippable.getEquipmentSlot("Mainhand");
    if (!slot || !slot.hasItem()) return;
    const item = slot.getItem();
    if (!item || !AXE_RE.test(item.typeId)) return;

    const durComp = item.getComponent("minecraft:durability");
    if (!durComp) return;

    let unbreaking = 0;
    try {
      const ench = item.getComponent("minecraft:enchantable");
      const lv = ench?.getEnchantment?.("unbreaking")?.level;
      if (typeof lv === "number") unbreaking = lv;
    } catch {}

    let damageToApply = 0;
    for (let i = 0; i < extraBlocks; i++) {
      let chance = 1;
      try {
        if (typeof durComp.getDamageChance === "function") {
          chance = durComp.getDamageChance(unbreaking) / 100;
        }
      } catch {}
      if (Math.random() < chance) damageToApply++;
    }
    if (damageToApply === 0) return;

    const newDamage = durComp.damage + damageToApply;
    if (newDamage >= durComp.maxDurability) {
      slot.setItem(undefined);
      try { player.playSound("random.break"); } catch {}
    } else {
      durComp.damage = newDamage;
      slot.setItem(item);
    }
  } catch (e) {
    log(`axe damage err: ${e}`);
  }
}

// ---- v2.7.0 NODAMAGE helpers --------------------------------------------
// Small-vegetation allowlist — these blocks get destroyed under a fallen tree's path.
// Everything else (logs/leaves/stone/dirt) stays intact.
const SMALL_VEG_TOKENS = [
  "grass", "tallgrass", "short_grass", "tall_grass", "fern",
  "flower", "poppy", "dandelion", "azure_bluet", "tulip",
  "oxeye_daisy", "cornflower", "lily_of_the_valley", "wither_rose",
  "blue_orchid", "allium", "sunflower", "lilac", "rose_bush", "peony",
  "sapling", "red_mushroom", "brown_mushroom",
  "bamboo", "sweet_berry_bush", "sugar_cane",
  "wheat", "carrots", "potatoes", "beetroots",
  "pumpkin_stem", "melon_stem", "torchflower_crop", "pitcher_crop",
  "dead_bush", "azalea", "pink_petals", "spore_blossom", "big_dripleaf",
  "small_dripleaf", "hanging_roots", "glow_lichen", "vine", "weeping_vines",
  "twisting_vines", "cave_vines", "crimson_roots", "warped_roots",
  "nether_sprouts", "nether_wart",
];
function isSmallVeg(id) {
  if (!id || id === "minecraft:air") return false;
  // Exclude block-leaves / logs explicitly (they contain "grass" in some edge names)
  if (id.endsWith("_leaves") || id.endsWith("_log") || id.endsWith("_stem") ||
      id.endsWith("_wood") || id.endsWith("_hyphae") || id.includes("grass_block")) {
    return false;
  }
  for (const t of SMALL_VEG_TOKENS) if (id.includes(t)) return true;
  return false;
}

// Destroy small vegetation along the fallen-tree swept corridor.
// Called at impact. Corridor: from stump outward `trunkLen` blocks in direction (fx,fz),
// width ±1 block either side, height 0..2 above ground.
function smashVegetationAlongFall(dim, stump, fx, fz, trunkLen) {
  let broken = 0;
  const perpX = -fz, perpZ = fx;
  for (let step = 0; step <= trunkLen; step++) {
    for (let w = -1; w <= 1; w++) {
      for (let dy = 0; dy < 3; dy++) {
        const px = Math.round(stump.x + fx * step + perpX * w);
        const pz = Math.round(stump.z + fz * step + perpZ * w);
        const py = stump.y + dy;
        let b;
        try { b = dim.getBlock({ x: px, y: py, z: pz }); } catch { continue; }
        if (!b || !isSmallVeg(b.typeId)) continue;
        try {
          dim.runCommand(`setblock ${px} ${py} ${pz} air destroy`);
          broken++;
        } catch {}
      }
    }
  }
  return broken;
}

// Damage + screen-shake + knockback to any entity whose location is inside
// the swept trunk corridor at impact. Chopping player already avoided via
// pickFallYaw, but we damage anyone ELSE who got caught.
//
// v2.7.3 DAMAGE: previous impl used `p.runCommand("damage @s 10 entity_attack")`
// which silently failed in some engine builds (player-scoped runCommand doesn't
// always bind @s to the running player, and peaceful-difficulty worlds could
// strip the command entirely depending on context). Switched to direct
// `p.applyDamage()` script API call which is the canonical path and cannot be
// suppressed by difficulty. Also loosened corridor tolerances slightly
// (CORRIDOR_WIDTH 1.2→1.5, along 0→-0.5, trunkLen+1→trunkLen+1.5, dy -1→-1.5 /
// 2.5→3) so players standing just outside the math-perfect line still get hit
// when the trunk visibly clips them. Added explicit per-sweep log so we can
// confirm the pass ran vs. didn't find anyone.
function applyImpactEffects(dim, stump, fx, fz, trunkLen, chopper) {
  const CORRIDOR_WIDTH = 1.5;   // half-width in blocks (v2.7.3: was 1.2)
  const DAMAGE_AMOUNT = 10;     // 5 hearts
  // v2.7.0 NODAMAGE→NODAMAGE-ALL: chopper is NOT exempt. If you're dumb enough to
  // stand where your tree's falling, you take the hit too. The yaw picker tries
  // to avoid dropping it toward the chopper, but if they move back into the
  // corridor mid-fall, that's on them.
  try {
    const players = dim.getPlayers();
    let hits = 0;
    for (const p of players) {
      // Project player position onto fall axis
      const dx = p.location.x - (stump.x + 0.5);
      const dz = p.location.z - (stump.z + 0.5);
      const along = dx * fx + dz * fz;          // distance along trunk axis
      const lateral = dx * (-fz) + dz * fx;      // perpendicular distance
      if (along < -0.5 || along > trunkLen + 1.5) continue;
      if (Math.abs(lateral) > CORRIDOR_WIDTH) continue;
      // Vertical gate — player must be near ground level (trunk is horizontal post-fall)
      const dy = p.location.y - stump.y;
      if (dy < -1.5 || dy > 3) continue;
      hits++;
      // v2.8.0 WIDEGRID: use EntityDamageCause.entityAttack enum (not raw string).
      // Prior v2.7.x passed {cause: "entityAttack"} literal — rejected by engine,
      // so applyDamage silently no-op'd AND its failure prevented the knockback
      // and camerashake calls that followed inside the same try block in early
      // builds. Now we run the three effects independently: damage → shake → kb.
      let damaged = false;
      try {
        damaged = p.applyDamage(DAMAGE_AMOUNT, {
          cause: EntityDamageCause.entityAttack
        });
      } catch (e) { log(`applyDamage err: ${e}`); }
      // Fallback command-path if API call didn't register (peaceful difficulty,
      // engine quirk, etc.). `damage` command accepts enum-style cause names.
      if (!damaged) {
        try { p.runCommand(`damage @s ${DAMAGE_AMOUNT} entity_attack`); }
        catch (e) { log(`damage cmd err: ${e}`); }
      }
      // Camerashake — standalone command, not auto-triggered by damage.
      // Syntax: /camerashake add <target> <intensity 0-4> <seconds> <positional|rotational>
      try {
        p.runCommand(`camerashake add @s 1.2 0.6 positional`);
      } catch (e) { log(`camerashake err: ${e}`); }
      // Knockback away from trunk axis (perpendicular to fall direction).
      // v2 API: applyKnockback(horizontalForce: VectorXZ, verticalStrength: number).
      const kbDir = Math.sign(lateral) || 1;
      const kbX = -fz * kbDir;
      const kbZ =  fx * kbDir;
      try {
        p.applyKnockback({ x: kbX * 2.2, z: kbZ * 2.2 }, 0.6);
      } catch (e) {
        // v1 API fallback
        try { p.applyKnockback(kbX, kbZ, 2.2, 0.6); }
        catch (e2) { log(`knockback err: ${e2}`); }
      }
      log(`impact hit ${p.name}: dmg=${damaged} shake=cmd kb=(${kbX.toFixed(1)},${kbZ.toFixed(1)})`);
    }
    log(`impact sweep: ${hits}/${players.length} in corridor`);
  } catch (e) { log(`applyImpactEffects err: ${e}`); }
}

world.afterEvents.playerBreakBlock.subscribe(ev => {
  try {
    const { player, block, brokenBlockPermutation, dimension } = ev;
    if (!player || !brokenBlockPermutation) { return; }

    const brokenId = brokenBlockPermutation.type.id;
    log(`broke ${brokenId}`);

    const speciesIdx = LOG_TO_SPECIES.get(brokenId);
    if (speciesIdx === undefined) return;
    log(`species idx ${speciesIdx} (${SPECIES[speciesIdx].key})`);

    // axe check — use the event's own item snapshot (the item as it was
    // when the swing started). This is reliable across API versions;
    // reading from equippable post-break was flaky.
    let held = ev.itemStackBeforeBreak ?? ev.itemStackAfterBreak ?? null;
    if (!held) {
      // fallback: equippable slot (may be empty post-break on some engines)
      try {
        const eq = player.getComponent("minecraft:equippable");
        const slot = eq?.getEquipmentSlot?.("Mainhand");
        if (slot?.hasItem?.()) held = slot.getItem();
      } catch {}
    }
    if (!held) { log("no held item in event or slot -> skip (bare hands?)"); return; }
    log(`held: ${held.typeId}`);
    if (!AXE_RE.test(held.typeId)) { log(`not an axe (${held.typeId}) -> skip`); return; }

    if (isCreative(player)) { log("creative -> skip"); return; }

    const start = { x: block.location.x, y: block.location.y, z: block.location.z };
    const speciesLogs = new Set(SPECIES[speciesIdx].logs);

    system.run(() => {
      try {
        // find seed log adjacent to chop point
        let seed = null;
        for (const n of NEIGHBORS_26) {
          const p = { x: start.x + n.x, y: start.y + n.y, z: start.z + n.z };
          if (p.y < start.y) continue;
          let b;
          try { b = dimension.getBlock(p); } catch { continue; }
          if (b && speciesLogs.has(b.typeId)) { seed = p; break; }
        }
        if (!seed) { log("no adjacent log -> nothing to fell"); return; }
        log(`seed at ${seed.x},${seed.y},${seed.z}`);

        const logs = findConnectedTree(dimension, seed, start.y, speciesLogs, speciesIdx);
        log(`found ${logs.length} connected logs`);
        if (logs.length < 2) return;

        const stumpY = findStumpY(logs);
        const stump = { x: start.x, y: stumpY, z: start.z };
        const trunkH = measureColumnHeight(logs, start);
        log(`stump (${stump.x},${stump.y},${stump.z}) h=${trunkH}`);

        // Clear real logs
        const airPerm = BlockPermutation.resolve("minecraft:air");
        let cleared = 0;
        for (const p of logs) {
          try {
            const b = dimension.getBlock(p);
            if (b) { b.setPermutation(airPerm); cleared++; }
          } catch (e) { log(`clear err at ${p.x},${p.y},${p.z}: ${e}`); }
        }
        log(`cleared ${cleared}/${logs.length} logs`);

        // Immediately break orphan leaves too, so the entity has clear space
        // to rotate through during its fall animation. This must happen
        // BEFORE the entity spawns.
        cleanOrphanLeaves(dimension, logs, speciesIdx);
        log(`cleaned leaves`);

        // Try spawning the entity — if this fails, we still drop loot
        let ent = null;
        try {
          ent = dimension.spawnEntity("ft:falling_tree", {
            x: stump.x + 0.5,
            y: stump.y,
            z: stump.z + 0.5,
          });
          log(`spawned entity ok`);
        } catch (e) {
          log(`spawn failed: ${e}`);
        }

        if (ent) {
          try { ent.setProperty("ft:wood_type", speciesIdx); }
          catch (e) { log(`setProp wood_type err: ${e}`); }
          try { ent.setProperty("ft:trunk_height", Math.min(16, trunkH)); }
          catch (e) { log(`setProp trunk_height err: ${e}`); }

          // v2.8.0 WIDEGRID: ft:canopy_size removed. ft:wood_type now directly
          // selects the species-specific geometry via render_controller's
          // Array.species_geos[q.property('ft:wood_type')]. Each species has its
          // own canopy layout within a shared 7x7 envelope.

          // Pick fall direction AND capture drop for terminal-angle calc
          let fallDrop = 0;
          try {
            const pick = pickFallYaw(dimension, player, stump, trunkH);
            fallDrop = pick.drop;
            ent.setRotation({ x: 0, y: pick.yaw });
          } catch (e) { log(`setRotation err: ${e}`); }

          // Fall angle from drop — tree leans further downhill than -90° when on a slope
          const fallAngle = computeFallAngle(fallDrop);
          try { ent.setProperty("ft:fall_angle", fallAngle); }
          catch (e) { log(`setProp fall_angle err: ${e}`); }
          log(`species=${SPECIES[speciesIdx].key} fallAngle=${fallAngle}°`);

          try {
            ent.playAnimation("animation.ft_falling_tree.fall", {
              blendOutTime: 0,
            });
            log(`playAnimation API fired`);
          } catch (e) {
            log(`playAnimation API err: ${e}`);
            // Fallback to command
            try {
              const tag = `ftfall${Math.floor(Math.random() * 1e9)}`;
              ent.addTag(tag);
              dimension.runCommand(
                `playanimation @e[tag=${tag}] animation.ft_falling_tree.fall`
              );
              log(`playanimation command fired (fallback)`);
            } catch (e2) { log(`fallback err: ${e2}`); }
          }

          // Pin the entity at its spawn location every tick + run collision sweep.
          // Without pinning, water flow, gravity edge-cases, or chunk-border
          // drift can push the "dead" prop entity around. The collision sweep
          // (2C) samples world blocks along the current trunk orientation each
          // tick and stops the fall animation early if the trunk would pass
          // through a solid block — fixes the "swing through walls" issue.
          const pinX = stump.x + 0.5;
          const pinY = stump.y;
          const pinZ = stump.z + 0.5;
          const pinRotY = ent.getRotation().y;
          const pinYawRad = pinRotY * Math.PI / 180;
          const pinFx = -Math.cos(pinYawRad);
          const pinFz =  Math.sin(pinYawRad);
          const pinStartTick = system.currentTick;
          let pinStopped = false;  // flip true once we've already stopped the fall
          const pinId = system.runInterval(() => {
            try {
              if (!ent || !ent.isValid) {
                system.clearRun(pinId);
                return;
              }
              ent.teleport({ x: pinX, y: pinY, z: pinZ },
                           { rotation: { x: 0, y: pinRotY } });

              // Collision sweep during the fall arc (skip if already stopped or done)
              if (pinStopped) return;
              const elapsed = (system.currentTick - pinStartTick) / 20;
              if (elapsed >= 1.8) { pinStopped = true; return; }
              if (elapsed < 0.25) return;  // skip first few ticks while still vertical

              const curAngleDeg = fallAngleAtTime(elapsed, fallAngle);
              const angleRad = Math.abs(curAngleDeg) * Math.PI / 180;
              const sinA = Math.sin(angleRad);
              const cosA = Math.cos(angleRad);

              // Sample positions along the trunk (r = 2..trunkH+1, one per block)
              // Skip r=0,1 since those are at the stump/just above (won't collide
              // with anything the pre-fall obstacle check didn't already catch)
              let hitR = 0;
              for (let r = 2; r <= trunkH + 1; r++) {
                const px = pinX + pinFx * sinA * r;
                const py = pinY + cosA * r;
                const pz = pinZ + pinFz * sinA * r;
                try {
                  const block = dimension.getBlock({
                    x: Math.floor(px),
                    y: Math.floor(py),
                    z: Math.floor(pz),
                  });
                  if (block && isFallCollider(block.typeId)) {
                    hitR = r;
                    break;
                  }
                } catch {}
              }

              if (hitR > 0) {
                // Freeze the tree at the current angle: set fall_angle to current
                // (so rest animation uses this as its resting pose) and flip
                // fall_stopped so the animation controller transitions to rest.
                const freezeAngle = Math.max(-135, Math.min(-1, Math.round(curAngleDeg)));
                try { ent.setProperty("ft:fall_angle", freezeAngle); } catch {}
                try { ent.setProperty("ft:fall_stopped", 1); } catch {}
                pinStopped = true;
                log(`collision at r=${hitR} angle=${freezeAngle}°`);
              }
            } catch {
              system.clearRun(pinId);
            }
          }, 1);

          try { dimension.playSound("dig.wood", stump, { volume: 1.3, pitch: 0.85 }); } catch {}

          // Compute the fall-direction vector once for all particle scheduling
          const yawRad = ent.getRotation().y * Math.PI / 180;
          const fx = -Math.cos(yawRad);
          const fz =  Math.sin(yawRad);
          const fallDist = Math.max(2, trunkH - 1);

          // ----- STAGE 1: Departure (at t=0, the moment the tree starts tipping)
          // Dust kicks up at the base + a small leaf-shake from the canopy above.
          try {
            const baseX = stump.x + 0.5;
            const baseZ = stump.z + 0.5;
            const baseY = stump.y + 0.1;
            // Dust at the base
            for (let i = 0; i < 6; i++) {
              const ox = baseX + (Math.random() - 0.5) * 1.8;
              const oz = baseZ + (Math.random() - 0.5) * 1.8;
              try {
                dimension.runCommand(
                  `particle minecraft:basic_smoke_particle ${ox.toFixed(2)} ${baseY.toFixed(2)} ${oz.toFixed(2)}`
                );
              } catch {}
            }
            // Quick leaf shake from the standing canopy
            const canopyTopY = stump.y + trunkH + 1;
            for (let i = 0; i < 6; i++) {
              const ox = baseX + (Math.random() - 0.5) * 4.5;
              const oy = canopyTopY + (Math.random() - 0.5) * 2.0;
              const oz = baseZ + (Math.random() - 0.5) * 4.5;
              try {
                dimension.runCommand(
                  `particle minecraft:falling_dust_mud_particle ${ox.toFixed(2)} ${oy.toFixed(2)} ${oz.toFixed(2)}`
                );
              } catch {}
            }
          } catch {}

          // ----- STAGE 2: Continuous leaf trail (multiple bursts through the fall arc)
          // Schedule 5 timed bursts at progressive angles to trail the falling canopy.
          // At t_frac, the tree has rotated angle = 90° * eased(t_frac); the canopy
          // tip sweeps through an arc. Each burst drops leaves where the canopy is now.
          const trailPhases = [
            { tFrac: 0.15, angleDeg:  8, count:  8, spread: 3.0 },  // just-started tipping
            { tFrac: 0.30, angleDeg: 20, count: 10, spread: 3.5 },  // starting to tilt
            { tFrac: 0.50, angleDeg: 38, count: 14, spread: 4.0 },  // mid-arc
            { tFrac: 0.70, angleDeg: 60, count: 18, spread: 4.5 },  // coming down
            { tFrac: 0.85, angleDeg: 80, count: 20, spread: 5.0 },  // near ground
          ];
          for (const phase of trailPhases) {
            system.runTimeout(() => {
              try {
                const angleRad = phase.angleDeg * Math.PI / 180;
                const canopyDist = trunkH - 1;
                // Canopy center in world space for this angle
                const cx = stump.x + 0.5 + fx * canopyDist * Math.sin(angleRad);
                const cy = stump.y + canopyDist * Math.cos(angleRad);
                const cz = stump.z + 0.5 + fz * canopyDist * Math.sin(angleRad);
                for (let i = 0; i < phase.count; i++) {
                  const ox = cx + (Math.random() - 0.5) * phase.spread;
                  const oy = cy + (Math.random() - 0.5) * (phase.spread * 0.6);
                  const oz = cz + (Math.random() - 0.5) * phase.spread;
                  try {
                    dimension.runCommand(
                      `particle minecraft:falling_dust_mud_particle ${ox.toFixed(2)} ${oy.toFixed(2)} ${oz.toFixed(2)}`
                    );
                  } catch {}
                }
              } catch {}
            }, Math.floor(FALL_DURATION_TICKS * phase.tFrac));
          }

          // ----- STAGE 3: Impact burst (at ~92% of fall, trunk crashes to ground)
          // v2.7.0: particles spawn UNDERNEATH the fallen trunk (y = stump.y - 0.05)
          //         so they appear to come from beneath the tree, not float inside it.
          //         Also: damage nearby entities, screenshake, knockback, smash small veg.
          system.runTimeout(() => {
            try {
              // v2.7.0: first, damage + shake + knockback any players in the fall corridor
              applyImpactEffects(dimension, stump, fx, fz, fallDist, player);
              // v2.7.0: destroy small vegetation along the fall path
              const smashed = smashVegetationAlongFall(dimension, stump, fx, fz, fallDist);
              if (smashed > 0) log(`smashed ${smashed} small veg blocks in fall path`);

              const steps = Math.min(8, fallDist + 2);
              // Dust cloud UNDER the fallen trunk (y just below ground top)
              const dustY = stump.y - 0.05;
              for (let s = 0; s <= steps; s++) {
                const t = s / steps;
                const ix = stump.x + 0.5 + fx * fallDist * t;
                const iz = stump.z + 0.5 + fz * fallDist * t;
                for (let j = 0; j < 4; j++) {
                  const ox = ix + (Math.random() - 0.5) * 1.6;
                  const oz = iz + (Math.random() - 0.5) * 1.6;
                  try {
                    dimension.runCommand(
                      `particle minecraft:basic_smoke_particle ${ox.toFixed(2)} ${dustY.toFixed(2)} ${oz.toFixed(2)}`
                    );
                  } catch {}
                  try {
                    dimension.runCommand(
                      `particle minecraft:falling_dust_mud_particle ${ox.toFixed(2)} ${dustY.toFixed(2)} ${oz.toFixed(2)}`
                    );
                  } catch {}
                }
              }
              // Leaf shower under the canopy end of the fallen trunk (stump.y level so
              // leaves appear to spill from the base of the rested canopy, not float above)
              const tipX = stump.x + 0.5 + fx * fallDist;
              const tipZ = stump.z + 0.5 + fz * fallDist;
              const tipY = stump.y;   // v2.7.0: was stump.y + 0.5 — now at ground
              for (let i = 0; i < 30; i++) {
                const ox = tipX + (Math.random() - 0.5) * 6.0;
                const oy = tipY + Math.random() * 1.8;       // small upward cone
                const oz = tipZ + (Math.random() - 0.5) * 6.0;
                try {
                  dimension.runCommand(
                    `particle minecraft:falling_dust_mud_particle ${ox.toFixed(2)} ${oy.toFixed(2)} ${oz.toFixed(2)}`
                  );
                } catch {}
              }
              // A few leaves settling broader around the whole fallen tree
              for (let i = 0; i < 15; i++) {
                const t = Math.random();
                const ox = stump.x + 0.5 + fx * fallDist * t + (Math.random() - 0.5) * 5.0;
                const oz = stump.z + 0.5 + fz * fallDist * t + (Math.random() - 0.5) * 5.0;
                const oy = stump.y + Math.random() * 0.8;     // v2.7.0: low spread, stays under trunk
                try {
                  dimension.runCommand(
                    `particle minecraft:falling_dust_mud_particle ${ox.toFixed(2)} ${oy.toFixed(2)} ${oz.toFixed(2)}`
                  );
                } catch {}
              }
              dimension.playSound("block.azalea_leaves.fall", stump, { volume: 1.8, pitch: 0.9 });
              dimension.playSound("dig.wood", stump, { volume: 2.0, pitch: 0.55 });
            } catch {}
          }, Math.floor(FALL_DURATION_TICKS * 0.92));
        }

        // schedule cleanup
        system.runTimeout(() => {
          try { ent?.remove(); } catch {}
          dropItems(dimension, stump, SPECIES[speciesIdx].drop, logs.length);
          try { dimension.playSound("random.wood_click", stump, { volume: 2.0, pitch: 0.6 }); } catch {}
          applyAxeDamage(player, logs.length - 1);
          log(`cleanup done`);
        }, FALL_DURATION_TICKS + REST_TICKS + DESPAWN_BUFFER_TICKS);
      } catch (e) {
        log(`system.run err: ${e}`);
      }
    });
  } catch (e) {
    log(`subscribe err: ${e}`);
  }
});
