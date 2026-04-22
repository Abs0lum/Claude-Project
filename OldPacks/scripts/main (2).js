import {
  world,
  system,
  ItemStack,
  BlockPermutation,
} from "@minecraft/server";

// ---- Diagnostics --------------------------------------------------------
// Set to true to get chat messages at every step so we can see where it breaks.
const DEBUG = false;
function log(msg) {
  if (!DEBUG) return;
  try { world.sendMessage(`§7[FT] §f${msg}`); } catch {}
  try { console.warn(`[FT] ${msg}`); } catch {}
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

const EXTRA_LEAF_IDS = [
  "minecraft:azalea_leaves",
  "minecraft:flowering_azalea_leaves",
  "minecraft:pale_oak_leaves",
];

// ---- Config -------------------------------------------------------------
const MAX_LOGS = 180;
const MAX_LEAVES = 260;
const FALL_DURATION_TICKS = 24; // 1.2s — must match animation_length
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

function findConnectedTree(dim, seed, startY, speciesLogs) {
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
function pickFallYaw(dim, player, stumpPos) {
  const DIRS = 8;                      // sample 8 compass directions
  const RADIUS = 4;                    // blocks out from stump
  const VERTICAL_SEARCH = 6;           // how far up/down we scan for ground
  const DOWNHILL_WEIGHT = 2.5;         // vs awayness; higher = more terrain-led

  // Vector from player to stump (horizontal) = preferred away direction
  const pLoc = player.location;
  const ax = (stumpPos.x + 0.5) - pLoc.x;
  const az = (stumpPos.z + 0.5) - pLoc.z;
  const aLen = Math.hypot(ax, az) || 1;
  const awayX = ax / aLen;
  const awayZ = az / aLen;

  // Ground height at a sample point (scan from stumpY+3 down to stumpY-VERTICAL_SEARCH)
  const groundYAt = (wx, wz) => {
    for (let dy = 3; dy >= -VERTICAL_SEARCH; dy--) {
      const p = { x: wx, y: stumpPos.y + dy, z: wz };
      let b;
      try { b = dim.getBlock(p); } catch { return stumpPos.y; }
      if (!b) continue;
      const id = b.typeId;
      // treat air / foliage / snow layer as "not ground"
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

  const stumpGroundY = stumpPos.y;

  let bestScore = -Infinity;
  let bestYaw = Math.atan2(awayZ, -awayX) * 180 / Math.PI; // fallback: straight away

  for (let i = 0; i < DIRS; i++) {
    const theta = (i / DIRS) * Math.PI * 2;
    const dirX = Math.cos(theta);
    const dirZ = Math.sin(theta);

    // sample ground elevation at this direction
    const sx = Math.round(stumpPos.x + dirX * RADIUS);
    const sz = Math.round(stumpPos.z + dirZ * RADIUS);
    const gy = groundYAt(sx, sz);
    // elevation drop: positive = downhill
    const drop = stumpGroundY - gy;

    // awayness: dot product with away-from-player unit vector
    const away = dirX * awayX + dirZ * awayZ;

    // combined score
    const score = away + DOWNHILL_WEIGHT * drop;

    if (score > bestScore) {
      bestScore = score;
      // yaw such that entity local -X aligns with (dirX, dirZ)
      bestYaw = Math.atan2(dirZ, -dirX) * 180 / Math.PI;
    }
  }

  return bestYaw;
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

// ---- Main event ---------------------------------------------------------
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

        const logs = findConnectedTree(dimension, seed, start.y, speciesLogs);
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

          try {
            const yaw = pickFallYaw(dimension, player, stump);
            ent.setRotation({ x: 0, y: yaw });
          } catch (e) { log(`setRotation err: ${e}`); }

          const tag = `ftfall${Math.floor(Math.random() * 1e9)}`;
          try { ent.addTag(tag); } catch (e) { log(`addTag err: ${e}`); }

          try {
            dimension.runCommand(
              `playanimation @e[tag=${tag}] animation.ft_falling_tree.fall fall_once 0`
            );
            log(`playanimation fired`);
          } catch (e) { log(`playanimation err: ${e}`); }

          try { dimension.playSound("dig.wood", stump, { volume: 1.3, pitch: 0.85 }); } catch {}

          // Impact burst timed to land with the trunk hitting ground.
          // At t ~= 1.0s of a 1.2s animation the rotation is at -75°, so
          // the tree is essentially on the ground. Schedule effects there.
          system.runTimeout(() => {
            // compute where the trunk top would be on the ground
            // (roughly trunk_height blocks away from stump in fall direction)
            try {
              const yaw = ent.getRotation().y * Math.PI / 180;
              // entity local -X direction in world space after yaw
              const fx = -Math.cos(yaw);
              const fz =  Math.sin(yaw);
              const fallDist = Math.max(2, trunkH - 1);
              // a few impact points along the fallen trunk
              for (let s = 1; s <= Math.min(4, fallDist); s++) {
                const t = s / Math.min(4, fallDist);
                const ix = stump.x + 0.5 + fx * fallDist * t;
                const iz = stump.z + 0.5 + fz * fallDist * t;
                const iy = stump.y + 0.2;
                try {
                  dimension.runCommand(
                    `particle minecraft:explosion_manual ${ix.toFixed(2)} ${iy.toFixed(2)} ${iz.toFixed(2)}`
                  );
                } catch {}
                try {
                  dimension.runCommand(
                    `particle minecraft:wind_explosion_emitter ${ix.toFixed(2)} ${iy.toFixed(2)} ${iz.toFixed(2)}`
                  );
                } catch {}
              }
              dimension.playSound("block.azalea_leaves.fall", stump, { volume: 2.0, pitch: 0.9 });
              dimension.playSound("dig.wood", stump, { volume: 1.5, pitch: 0.6 });
            } catch {}
          }, Math.floor(FALL_DURATION_TICKS * 0.85));
        }

        // schedule cleanup
        system.runTimeout(() => {
          try { ent?.remove(); } catch {}
          dropItems(dimension, stump, SPECIES[speciesIdx].drop, logs.length);
          try { dimension.playSound("random.wood_click", stump, { volume: 2.0, pitch: 0.6 }); } catch {}
          cleanOrphanLeaves(dimension, logs, speciesIdx);
          applyAxeDamage(player, logs.length - 1);
          log(`cleanup done`);
        }, FALL_DURATION_TICKS + DESPAWN_BUFFER_TICKS);
      } catch (e) {
        log(`system.run err: ${e}`);
      }
    });
  } catch (e) {
    log(`subscribe err: ${e}`);
  }
});
