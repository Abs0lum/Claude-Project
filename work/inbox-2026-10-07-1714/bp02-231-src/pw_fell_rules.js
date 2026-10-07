// pw_fell_rules.js — his FELLING RULES (F5, 15:42 10-02; memory 'falling-tree'), enforced BEFORE the BIGCANOPY fall runs
// (BP-02 v1.3.206, tree program T3 step 1). A tree falls ONLY when:
//   R1  the cut separates a TRUNK from the ground: below the cut a column of the same species' logs (or the cut itself)
//       stands on natural ground. A log whose column ends in air / leaves / a building is a BRANCH or a loose log: it
//       just breaks (his F6 = a).
//   R2  there is trunk ABOVE the cut (something to fall).
//   R3  it is a WORLD-BUILT tree: (a) a structure tree — its column reaches a pw:*_root block (worldgen / grown trees
//       carry one, T2) — or (b) an older generated tree with no root (his F1 = b: today's rules + the placed-log ledger).
//   R4  no log of it was ever placed by a player: every log a player places is written to a small per-chunk ledger
//       (playerPlaceBlock), and a candidate tree that contains a ledger log never falls (logs in buildings never fall).
//   R5  real canopy attached: at least 3 NATURAL leaves touch its logs (vanilla leaves with persistent_bit false, or our
//       pw leaves) — player-placed vanilla leaves (persistent) do not count.
// Breaking a log never by itself means a fall: R1 + R2 + R3 + R4 + R5 must all hold.
import { world, BlockPermutation, BlockVolume, BlockTypes } from "@minecraft/server";

const GROUND = new Set(["minecraft:grass_block", "minecraft:grass", "minecraft:dirt", "minecraft:coarse_dirt",
  "minecraft:podzol", "minecraft:mycelium", "minecraft:moss_block", "minecraft:mud", "minecraft:rooted_dirt",
  "minecraft:dirt_with_roots", "minecraft:muddy_mangrove_roots", "minecraft:mangrove_roots", "minecraft:sand",
  "minecraft:red_sand", "minecraft:gravel", "minecraft:clay", "minecraft:snow", "minecraft:stone", "minecraft:farmland",
  "minecraft:grass_path", "minecraft:dirt_path", "minecraft:pale_moss_block", "minecraft:crimson_nylium",
  "minecraft:warped_nylium", "minecraft:netherrack", "minecraft:soul_soil", "pw:grass_block"]);
const LEDGER = "pw:plog:";
let _logIds = null;          // every log id of every species (set by registerRootLogs)

/** Add pw:<tier>_root to each species' log list (same species, same drop). Call once after SPECIES is defined. */
/** the square species whose trunks are vanilla logs keep a pw root of their own (T2b, BP-02 1.3.208) */
const VANILLA_ROOTS = { "minecraft:acacia_log": "pw:acacia_root", "minecraft:cherry_log": "pw:cherry_root", "minecraft:mangrove_log": "pw:mangrove_root" };
export function registerRootLogs(SPECIES, LOG_TO_SPECIES) {
  for (let i = 0; i < SPECIES.length; i++) {
    for (const id of [...SPECIES[i].logs]) {
      const root = id.startsWith("pw:") && /_(young|mature|old|elder)$/.test(id) ? `${id}_root` : VANILLA_ROOTS[id];
      if (!root) continue;
      if (!SPECIES[i].logs.includes(root)) SPECIES[i].logs.push(root);
      LOG_TO_SPECIES.set(root, i);
    }
  }
  _logIds = new Set(LOG_TO_SPECIES.keys());
}

// ---------------------------------------------------------------- R4: the placed-log ledger (per chunk)
function key(x, z) { return `${LEDGER}${Math.floor(x / 16)},${Math.floor(z / 16)}`; }
function readChunk(x, z) {
  try { const v = world.getDynamicProperty(key(x, z)); return typeof v === "string" ? v : ""; } catch { return ""; }
}
function writeChunk(x, z, s) {
  try { world.setDynamicProperty(key(x, z), s.length ? s : undefined); } catch { /* full: oldest entries roll off */ }
}
const cellTag = (x, y, z) => `;${x},${y},${z}`;

world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try {
    const id = ev.block.typeId;
    if (!_logIds || !_logIds.has(id)) return;
    const { x, y, z } = ev.block.location;
    let s = readChunk(x, z);
    const t = cellTag(x, y, z);
    if (s.includes(t + ";") || s.endsWith(t)) return;
    s += t;
    if (s.length > 30000) s = s.slice(s.indexOf(";", 4000));   // keep the newest ~2,000 logs of a chunk
    writeChunk(x, z, s);
  } catch { /* never block placing */ }
});

world.afterEvents.playerBreakBlock.subscribe((ev) => {
  try {
    const id = ev.brokenBlockPermutation.type.id;
    if (!_logIds || !_logIds.has(id)) return;
    const { x, y, z } = ev.block.location;
    const s = readChunk(x, z);
    const t = cellTag(x, y, z);
    if (!s.includes(t)) return;
    writeChunk(x, z, s.split(";").filter((e) => e && e !== `${x},${y},${z}`).map((e) => ";" + e).join(""));
  } catch { /* ignore */ }
});

/** True when any of these logs was placed by a player (ledger). */
export function touchesPlacedLog(logs) {
  const byChunk = new Map();
  for (const p of logs) {
    const k = key(p.x, p.z);
    if (!byChunk.has(k)) byChunk.set(k, readChunk(p.x, p.z));
    const s = byChunk.get(k);
    if (s && (s.includes(cellTag(p.x, p.y, p.z) + ";") || s.endsWith(cellTag(p.x, p.y, p.z)))) return true;
  }
  return false;
}

// ---------------------------------------------------------------- R1 / R2 / R3
/** Decide whether a survival log break may start a fall. cut = the broken cell (now air). */
export function fellVerdict(dim, cut, speciesLogs) {
  const get = (x, y, z) => { try { return dim.getBlock({ x, y, z }); } catch { return undefined; } };
  // R2: trunk above the cut (the 2x2 rule in main.js handles wide trunks; here: any species log directly above or a
  // 2x2 partner column above)
  let above = false;
  for (const [dx, dz] of [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1]]) {
    const b = get(cut.x + dx, cut.y + 1, cut.z + dz);
    if (b && speciesLogs.has(b.typeId)) { above = true; break; }
  }
  if (!above) return { allow: false, reason: "R2 nothing above the cut" };
  // R1 + R3: walk down from below the cut through the same species' logs to the ground (<= 32)
  let root = null;
  for (let dy = 1; dy <= 33; dy++) {
    const b = get(cut.x, cut.y - dy, cut.z);
    if (!b) return { allow: false, reason: "R1 column runs into an unloaded chunk" };
    const id = b.typeId;
    if (speciesLogs.has(id)) {
      if (id.endsWith("_root")) {
        root = { x: cut.x, y: cut.y - dy, z: cut.z, id, tpl: (b.permutation.getState("pw:tpl") ?? 0) + 16 * (b.permutation.getState("pw:tpl_hi") ?? 0),
                 dir: b.permutation.getState("minecraft:cardinal_direction") };
      }
      continue;
    }
    if (GROUND.has(id)) return { allow: true, reason: root ? "R3a structure tree" : "R3b generated tree (no root)", root };
    return { allow: false, reason: `R1 column ends on ${id} (branch / loose log / building) -> just breaks` };
  }
  return { allow: false, reason: "R1 no ground within 32 below the cut" };
}

// ---------------------------------------------------------------- R5
/** At least `need` natural leaves touching the logs (vanilla non-persistent, or pw leaves).
 *  read(x, y, z): the block or a falsy value — 1.3.228 (B1 hygiene): the town passes its guarded blockAt (pw_civ_clock
 *  naturalCanopy); without it (a player's own felling, one event) the read is the old one in try. */
export function hasNaturalCanopy(dim, logs, need = 3, read = null) {
  let n = 0;
  const seen = new Set();
  for (const p of logs) {
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
      const k = `${p.x + dx},${p.y + dy},${p.z + dz}`;
      if (seen.has(k)) continue;
      seen.add(k);
      let b;
      if (read) b = read(p.x + dx, p.y + dy, p.z + dz);
      else { try { b = dim.getBlock({ x: p.x + dx, y: p.y + dy, z: p.z + dz }); } catch { continue; } }
      if (!b) continue;
      const id = b.typeId;
      const natural = id.startsWith("pw:") ? id.endsWith("_leaves") :
        ((id.endsWith("_leaves") || id.endsWith("_wart_block") || id.endsWith("mushroom_block")) &&
         b.permutation.getState("persistent_bit") !== true);
      if (natural && ++n >= need) return true;
    }
  }
  return false;
}

// ---------------------------------------------------------------- F8 = b: the fallen trunk stays on the ground
const SOFT = (id) => id === "minecraft:air" || id.endsWith("_grass") || id === "minecraft:short_grass" ||
  id === "minecraft:tall_grass" || id.endsWith("fern") || id.endsWith("_flower") || id === "minecraft:snow_layer" ||
  id === "minecraft:dandelion" || id === "minecraft:poppy" || id === "minecraft:leaf_litter" || id === "minecraft:pink_petals" ||
  id === "minecraft:wildflowers" || id === "minecraft:bush";
const NOT_GROUND = (id) => SOFT(id) || id.endsWith("_leaves") || id === "minecraft:water" || id === "minecraft:lava";

/** Lay up to `count` logs along the fall line (unit fx, fz) from 2 blocks past the stump, each resting on the ground
 *  (searched 3 up .. 4 down from the stump level). Stops at the first cell that is blocked. Returns how many were laid;
 *  the caller drops the rest as items. */
export function placeLyingLog(dim, stump, fx, fz, count, logId) {
  if (!(count > 0) || !logId) return 0;
  const axis = Math.abs(fx) >= Math.abs(fz) ? "x" : "z";
  let perm;
  try { perm = BlockPermutation.resolve(logId, { pillar_axis: axis }); } catch { return 0; }
  let laid = 0;
  const done = new Set();
  for (let d = 2; laid < count && d < count + 12; d++) {
    const x = Math.floor(stump.x + 0.5 + fx * d), z = Math.floor(stump.z + 0.5 + fz * d);
    const k = `${x},${z}`;
    if (done.has(k)) continue;
    done.add(k);
    let placed = false;
    for (let y = stump.y + 3; y >= stump.y - 4; y--) {
      let b, below;
      try { b = dim.getBlock({ x, y, z }); below = dim.getBlock({ x, y: y - 1, z }); } catch { break; }
      if (!b || !below) break;
      if (SOFT(b.typeId) && !NOT_GROUND(below.typeId)) {
        try { b.setPermutation(perm); placed = true; laid++; } catch { /* protected cell */ }
        break;
      }
    }
    if (!placed) break;                                         // a wall / water / cliff: the rest drops as items
  }
  return laid;
}

// ---------------------------------------------------------------- F4 = c: player blocks on a falling tree drop as items
const NATURAL_ATTACHED = (id) => id === "minecraft:air" || id.endsWith("_leaves") || id.endsWith("vine") ||
  id.endsWith("vines") || id === "minecraft:cocoa" || id === "minecraft:bee_nest" || id === "minecraft:snow_layer" ||
  id === "minecraft:water" || id === "minecraft:moss_carpet" || id === "minecraft:glow_lichen" ||
  id.startsWith("pw:vine") || id === "pw:leaf_litter" || id.endsWith("_wart_block") || id.endsWith("mushroom_block") ||
  id === "minecraft:mangrove_propagule" || id === "minecraft:hanging_roots" || id === "minecraft:pale_hanging_moss" ||
  GROUND.has(id) || NOT_GROUND(id);

/** Every non-natural block touching a face of a falling log (planks, torches, ladders, signs, glass, ... a treehouse) is
 *  broken WITH its item drop before the tree falls. Returns how many. Ground under the stump is never touched. */
export function dropAttachedBlocks(dim, logs, speciesLogs) {
  const logSet = new Set(logs.map((p) => `${p.x},${p.y},${p.z}`));
  const minY = Math.min(...logs.map((p) => p.y));
  let n = 0;
  const done = new Set();
  for (const p of logs) {
    for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]) {
      const x = p.x + dx, y = p.y + dy, z = p.z + dz;
      const k = `${x},${y},${z}`;
      if (logSet.has(k) || done.has(k) || y < minY) continue;
      done.add(k);
      let b; try { b = dim.getBlock({ x, y, z }); } catch { continue; }
      if (!b || speciesLogs.has(b.typeId) || NATURAL_ATTACHED(b.typeId)) continue;
      try { dim.runCommand(`setblock ${x} ${y} ${z} air destroy`); n++; } catch { /* protected */ }
    }
  }
  return n;
}

// ---------------------------------------------------------------- F9 = yes: the stump shows its growth rings
const TIER_RX = /^pw:((?:oak|spruce|birch|jungle|dark_oak|pale_oak)_(?:young|mature|old|elder))(?:_root)?$/;
/** After a fall: every trunk cell right under the cut (the cut column and a 2x2 partner) whose top is now open becomes
 *  pw:<tier>_stump (same trunk shape, ring face by age). Vanilla logs keep their own end grain. Returns how many. */
export function placeStumps(dim, cut) {
  let n = 0;
  let center = null;                                // the cut column's tier, read BEFORE it becomes a stump
  try { center = TIER_RX.exec(dim.getBlock({ x: cut.x, y: cut.y - 1, z: cut.z })?.typeId || ""); } catch { /* unloaded */ }
  for (const [dx, dz] of [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) {
    let b, up;
    try { b = dim.getBlock({ x: cut.x + dx, y: cut.y - 1, z: cut.z + dz }); up = dim.getBlock({ x: cut.x + dx, y: cut.y, z: cut.z + dz }); }
    catch { continue; }
    if (!b || !up || up.typeId !== "minecraft:air") continue;
    const m = TIER_RX.exec(b.typeId);
    if (!m) continue;
    if (dx !== 0 || dz !== 0) {                     // a partner column only when it is the same tier (2x2 elders)
      if (!center || center[1] !== m[1]) continue;
    }
    try { b.setPermutation(BlockPermutation.resolve(`pw:${m[1]}_stump`)); n++; } catch { /* unknown stump id */ }
  }
  return n;
}

// ---------------------------------------------------------------- F7 = yes: on flat ground the tree falls toward its heavy side
/** Crown lean: centroid (x, z) of the tree's branch logs + its leaves, relative to the stump, from ONE engine-filtered
 *  getBlocks over the logs' box +3. strength 0..1 = offset / (half the crown width), so a symmetric crown gives ~0. */
export function crownLean(dim, logs, stump, leafIds) {
  try {
    let x0 = Infinity, y0 = Infinity, z0 = Infinity, x1 = -Infinity, y1 = -Infinity, z1 = -Infinity;
    for (const p of logs) {
      x0 = Math.min(x0, p.x); y0 = Math.min(y0, p.y); z0 = Math.min(z0, p.z);
      x1 = Math.max(x1, p.x); y1 = Math.max(y1, p.y); z1 = Math.max(z1, p.z);
    }
    const vol = new BlockVolume({ x: x0 - 3, y: y0, z: z0 - 3 }, { x: x1 + 3, y: y1 + 3, z: z1 + 3 });
    let sx = 0, sz = 0, n = 0, minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
    const add = (x, z, w) => { sx += (x - stump.x) * w; sz += (z - stump.z) * w; n += w;
      minX = Math.min(minX, x); maxX = Math.max(maxX, x); minZ = Math.min(minZ, z); maxZ = Math.max(maxZ, z); };
    for (const p of logs) add(p.x, p.z, 2);                       // wood weighs more than a leaf
    const known = leafIds.filter((id) => { try { return !!BlockTypes.get(id); } catch { return false; } });
    const res = dim.getBlocks(vol, { includeTypes: known.length ? known : ["minecraft:oak_leaves"] }, true);
    for (const l of res.getBlockLocationIterator()) add(l.x, l.z, 1);
    if (!n) return { x: 0, z: 0, strength: 0 };
    const cx = sx / n, cz = sz / n;
    const half = Math.max(1, Math.max(maxX - minX, maxZ - minZ) / 2);
    const len = Math.hypot(cx, cz);
    return { x: len ? cx / len : 0, z: len ? cz / len : 0, strength: Math.min(1, len / half) };
  } catch { return { x: 0, z: 0, strength: 0 }; }
}

// ---------------------------------------------------------------- T4: the EXACT falling set from the template (D-C503)
// A structure tree carries its template id and rotation in its root (tpl + tpl_hi + cardinal_direction). The template
// (structureManager.get) is the one source of truth for which cells are the tree: trunk / branch logs and leaves. The
// falling set is those cells, rotated about the root into the world and filtered to what still stands — never a
// neighbour's logs (G13), never a BFS heuristic (SCANNER-AND-FALLING-TREES §6.3). Cached per template (a small LRU).
const TPL_CACHE = new Map();
const TPL_CACHE_MAX = 24;
const DIR_ROT = { north: 0, east: 1, south: 2, west: 3 };
export const isTreeLogId = (id) => /^pw:[a-z_]+_(young|mature|old|elder)(_root)?$/.test(id) || /^minecraft:(stripped_)?[a-z_]+_log$/.test(id) || id === "minecraft:mangrove_roots";
export const isTreeLeafId = (id) => id.includes("leaves") || id.includes("_leaf") || id === "minecraft:vine" || id === "minecraft:mangrove_propagule";

/** "pw:oak_mature_root" + 7 -> "pw:trees/oak_mature_07"; "pw:acacia_root" + 19 -> "pw:trees/acacia_19" */
export function templateName(rootId, tpl) {
  const stem = rootId.replace(/^pw:/, "").replace(/_root$/, "");
  return `pw:trees/${stem}_${String(tpl).padStart(2, "0")}`;
}

/** rotate a local offset (relative to the root) by the root's facing: north = as saved; east / south / west = 1 / 2 / 3
 *  clockwise quarter turns (the rotation law of D-C477 / the clock's rotXZ on relative vectors) */
export function turnOffset(dx, dz, dir) {
  const r = DIR_ROT[dir] ?? 0;
  if (r === 1) return [-dz, dx];
  if (r === 2) return [-dx, -dz];
  if (r === 3) return [dz, -dx];
  return [dx, dz];
}

/** decode a template once: its cells relative to its root cell, split into logs and leaves (local, north-facing) */
export function templateCells(name, manager = world.structureManager) {
  if (TPL_CACHE.has(name)) { const v = TPL_CACHE.get(name); TPL_CACHE.delete(name); TPL_CACHE.set(name, v); return v; }
  let st;
  try { st = manager.get(name); } catch { st = undefined; }
  if (!st) return null;
  const { x: sx, y: sy, z: sz } = st.size;
  const logs = [], leaves = [];
  let root = null;
  for (let x = 0; x < sx; x++) for (let y = 0; y < sy; y++) for (let z = 0; z < sz; z++) {
    let perm;
    try { perm = st.getBlockPermutation({ x, y, z }); } catch { perm = undefined; }
    if (!perm) continue;
    const id = perm.type.id;
    if (id === "minecraft:air") continue;
    if (id.endsWith("_root") && id.startsWith("pw:")) { root = [x, y, z]; logs.push([x, y, z]); }
    else if (isTreeLogId(id)) logs.push([x, y, z]);
    else if (isTreeLeafId(id)) leaves.push([x, y, z]);
  }
  if (!root) return null;
  const rel = (c) => [c[0] - root[0], c[1] - root[1], c[2] - root[2]];
  const v = { name, size: [sx, sy, sz], root, logs: logs.map(rel), leaves: leaves.map(rel) };
  TPL_CACHE.set(name, v);
  if (TPL_CACHE.size > TPL_CACHE_MAX) TPL_CACHE.delete(TPL_CACHE.keys().next().value);
  return v;
}

/** the falling set of a structure tree: root = {id, tpl, dir, x, y, z} (fellVerdict's root + its world cell), cut = the
 *  broken log's position. Returns null when the template is unknown; else {trunkAbove, trunkBelow, leaves, name},
 *  every list in WORLD coords and filtered to cells that still hold a tree log / leaf (present(dim, p, kind)). */
export function templateFallingSet(dim, root, cut, opts = {}) {
  const cells = templateCells(templateName(root.id, root.tpl), opts.manager);
  if (!cells) return null;
  const present = opts.present || ((p, kind) => { let b; try { b = dim.getBlock(p); } catch { return false; } if (!b) return false; return kind === "log" ? isTreeLogId(b.typeId) : isTreeLeafId(b.typeId); });
  const place = (c) => { const [ox, oz] = turnOffset(c[0], c[2], root.dir); return { x: root.x + ox, y: root.y + c[1], z: root.z + oz }; };
  const trunkAbove = [], trunkBelow = [], leaves = [];
  for (const c of cells.logs) {
    const p = place(c);
    if (p.x === cut.x && p.y === cut.y && p.z === cut.z) continue;          // the cut cell is already broken
    if (!present(p, "log")) continue;
    (p.y > cut.y ? trunkAbove : trunkBelow).push(p);
  }
  for (const c of cells.leaves) { const p = place(c); if (present(p, "leaf")) leaves.push(p); }
  return { name: cells.name, trunkAbove, trunkBelow, leaves, total: cells.logs.length + cells.leaves.length };
}
