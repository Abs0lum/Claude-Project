import {
  world,
  system,
  ItemStack,
  BlockPermutation,
  EntityDamageCause,
  MolangVariableMap,
  BlockTypes,
  BlockVolume,
} from "@minecraft/server";
let _forgeBeat = -1000000; let _forgeWasOn = false; // SLABFORGE key-pack heartbeat gate (v1.3.150) — hoisted v1.3.154 (TA reads it)
import { pwConvertRiser } from "./pw_ground.js";   // two-material ground family + riser conversion
import "./pw_companion.js"; // PW-C2 companion module (roof family port, dossier-cited)
import "./pw_homestead.js"; // HOMESTEAD: hearth / flue / dual wall / rafter (v1.3.178)
import "./pw_furniture.js"; // FURNITURE: 12 pieces x 3 woods, sit + table auto-join (v1.3.183)
import "./pw_flutter.js"; // v1.3.200: fowl FLUTTER physics - a hop, slow fall 1.2 s, then the drop (his J3 = d, 10-01)
import "./pw_vine.js"; // v1.3.202: 3D vines, swap once + scripted climbing (his Q1 = a, 10-02); v1.3.203 rustle on touch
import "./pw_planks.js"; // v1.3.201: Patrix 4x4 plank grids, swap once (his 00:53, 10-02)
import "./pw_mob_light.js"; // v1.3.194: self-lit mobs throw real light (blaze / magma cube / glow squid)
import "./pw_civ_clock.js";
import "./pw_gallery.js"; // v1.3.222: THE GALLERY — unique public-domain paintings + the Connoisseur's Book (D-C571)
import "./sf_nba_main.js"; // v1.3.206 his NS1 = b: the Naturalist add-on scripts run (ants from hills, variants, buckets, info book, eggs, chrysalis …)
import { registerRootLogs, fellVerdict, touchesPlacedLog, hasNaturalCanopy, placeLyingLog, dropAttachedBlocks, placeStumps, crownLean, templateFallingSet, templateCells, turnOffset } from "./pw_fell_rules.js";
import * as FALLPHYS from "./pw_fall_physics.js"; // v1.3.220 (1004b, D-C563 / D-C565): physics fall + the yaw law // v1.3.206: his felling rules F5 (T3 step 1) // v1.3.206: CIVITAS village clock + time tool (/scriptevent pw:clock …), buildings grow through stages
import { FT_TPL_INDEX } from "./pw_ft_tpl_index.js"; // v1.3.217 carbon-copy falling tree (D-C524)
import { weatherIn } from "./pw_weather.js"; // v1.3.186: weather via world.afterEvents.weatherChange (stable); Dimension.getWeather is beta-only

// ====================================================================================
// v1.2.41 DIAGNOSTIC MARKER A — module-entry beacon
// If you see this line in your content log, BP-02 script has loaded successfully.
// ====================================================================================
// ===== v1.3.60 V2 PHASE-0: single-source build stamp + boot-generation id =====
const PW_BUILD = "1.3.231";
globalThis.__PW_BUILD = PW_BUILD;
const PW_BOOT_ID = "g" + Date.now().toString(36).slice(-4) + Math.floor(Math.random()*1296).toString(36).padStart(2,"0");
try { console.warn(`[BIGCANOPY-DIAG] MARKER-A v${PW_BUILD} ${PW_BOOT_ID} module entered — imports OK`); } catch {}


// ---- Diagnostics --------------------------------------------------------
// v2.7.5 DEBUG-ON: dev build. Chat trace restored so in-world testing produces
// visible event log per tree chop. For realm/multiplayer hosting flip DEBUG
// to false (matches v2.7.4 NOCHAT behavior). Content-log output always goes
// to console.warn regardless; only chat visibility is gated.
//
// v0.6.6 FIX: Split `log` (informational, uses console.log → doesn't clutter
// the game's "warning" log) from `logErr` (uses console.warn, for problems).
// Startup/progress messages should use log(). Failure paths should use logErr().
const DEBUG = false;
try { console.warn(`[PW-PERF] v${PW_BUILD} ${PW_BOOT_ID} throttle ACTIVE: TA_YIELD=400 P1_YIELD=400 BFS_BUDGET=300 BFS_MAX=1500 torch=20t`); } catch {}
function log(msg) {
  if (DEBUG) {
    try { world.sendMessage(`§a[BIGCANOPY] §f${msg}`); } catch {}
  }
  try { console.log(`[BIGCANOPY] ${msg}`); } catch {}
}
function logErr(msg) {
  if (DEBUG) {
    try { world.sendMessage(`§c[BIGCANOPY] §f${msg}`); } catch {}
  }
  try { console.warn(`[BIGCANOPY] ${msg}`); } catch {}
}

log("v0.15.18 loaded — Fixes: yellow sand redesigned (continuous undulating beach dunes via Perlin height-field + directional Lambertian shading; HHH/KKK curve mix with mixed sigma 22-48; tier-based drama: small-σ tiles 78% calm + large-σ tiles 108% chaos; shadows confined to interior with sigma-tier inset 55-80px; peaks level out to neutral on all 4 edges with 18px fade; subtle sun-aligned streaks for natural blending); sand glimmer (1.2% emissive sparkles in MER G channel + low roughness for sun shimmer); sheep body south face uv_rotation:180 (sheep + sheep_wool); diamond/iron/gold/chainmail/netherite/leather/copper/turtle_scute armor copied to NEW Bedrock 1.21.70+ humanoid path");

// ---- Species ------------------------------------------------------------
const SPECIES = [
  // v0.10.0: pw:oak_* tier blocks added to oak species. They drop as
  // minecraft:oak_log so the player gets standard oak logs in inventory.
  { key: "oak",      logs: ["minecraft:oak_log", "minecraft:stripped_oak_log",
                            "pw:oak_young", "pw:oak_mature", "pw:oak_old",
                            "pw:oak_elder"],
    drop: "minecraft:oak_log",      leaves: ["minecraft:oak_leaves", "pw:oak_leaves",
                                            "pw:oak_leaves_a", "pw:oak_leaves_b",
                                            "pw:oak_leaves_c", "pw:oak_leaves_d",
                                            "pw:oak_leaves_e", "pw:oak_leaves_f",
                                            "pw:azalea_leaves", "pw:flowering_azalea_leaves"] },
  { key: "spruce",   logs: ["minecraft:spruce_log", "minecraft:stripped_spruce_log",
                            "pw:spruce_young", "pw:spruce_mature", "pw:spruce_old",
                            "pw:spruce_elder"],
    drop: "minecraft:spruce_log",   leaves: ["minecraft:spruce_leaves", "pw:spruce_leaves"] },
  { key: "birch",    logs: ["minecraft:birch_log", "minecraft:stripped_birch_log",
                            "pw:birch_young", "pw:birch_mature", "pw:birch_old"],
    drop: "minecraft:birch_log",    leaves: ["minecraft:birch_leaves", "pw:birch_leaves"] },
  { key: "jungle",   logs: ["minecraft:jungle_log", "minecraft:stripped_jungle_log",
                            "pw:jungle_young", "pw:jungle_mature", "pw:jungle_old",
                            "pw:jungle_elder"],
    drop: "minecraft:jungle_log",   leaves: ["minecraft:jungle_leaves", "pw:jungle_leaves"] },
  { key: "acacia",   logs: ["minecraft:acacia_log",   "minecraft:stripped_acacia_log"],   drop: "minecraft:acacia_log",   leaves: ["minecraft:acacia_leaves", "pw:acacia_leaves"] },
  { key: "dark_oak", logs: ["minecraft:dark_oak_log", "minecraft:stripped_dark_oak_log",
                            "pw:dark_oak_elder"],
    drop: "minecraft:dark_oak_log", leaves: ["minecraft:dark_oak_leaves", "pw:dark_oak_leaves"] },
  { key: "mangrove", logs: ["minecraft:mangrove_log", "minecraft:stripped_mangrove_log"], drop: "minecraft:mangrove_log", leaves: ["minecraft:mangrove_leaves", "pw:mangrove_leaves"] },
  { key: "cherry",   logs: ["minecraft:cherry_log",   "minecraft:stripped_cherry_log"],   drop: "minecraft:cherry_log",   leaves: ["minecraft:cherry_leaves", "pw:cherry_leaves"] },
  { key: "crimson",  logs: ["minecraft:crimson_stem", "minecraft:stripped_crimson_stem"], drop: "minecraft:crimson_stem", leaves: ["minecraft:nether_wart_block"] },
  { key: "warped",   logs: ["minecraft:warped_stem",  "minecraft:stripped_warped_stem"],  drop: "minecraft:warped_stem",  leaves: ["minecraft:warped_wart_block"] },
  // v0.10.0 NEW SPECIES:
  { key: "pale_oak", logs: ["minecraft:pale_oak_log", "minecraft:stripped_pale_oak_log",
                            "pw:pale_oak_elder"],
    drop: "minecraft:pale_oak_log", leaves: ["minecraft:pale_oak_leaves", "pw:pale_oak_leaves"] },
  { key: "mushroom", logs: ["minecraft:mushroom_stem"],
                                                                                          drop: "minecraft:mushroom_stem",
                                                                                          leaves: ["minecraft:brown_mushroom_block", "minecraft:red_mushroom_block"] }];

const LOG_TO_SPECIES = new Map();
for (let i = 0; i < SPECIES.length; i++) {
  for (const id of SPECIES[i].logs) LOG_TO_SPECIES.set(id, i);
}
registerRootLogs(SPECIES, LOG_TO_SPECIES);
const PW_TEMPLATE_FELL = true;   // v1.3.209 T4: structure trees fall by their template's exact cell set (D-C503) // v1.3.206: pw:<tier>_root blocks (structure trees) are logs of their species

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
// v1.3.40: FIRST-CONTACT TERMINAL ANGLE (Abs0lum spec: no ground clipping).
// Sample ground height along the fall direction at every distance d=2..trunkLen
// from the stump; the trunk rotates until it FIRST touches the terrain line, so
// the terminal angle is the minimum rotation over all samples:
//   contact(d) = 90° + atan2(-Δy, d)   (Δy = groundY(d) - (stumpY+1); v1.3.52 stump-top pivot)
// Flat ground -> exactly -90 (rests ON the surface by construction). Uniform
// downslope -> lies along the slope. Rising ground / valleys -> rests on the
// nearest contact; the mid-fall collision pin still handles hard obstacles.
// NOTE: samples along the SCRIPT's fall-direction convention; slope accuracy
// inherits the Phase-6 direction-sign verdict (flat ground exact regardless).
function computeFallAngle(dim, stumpPos, yawDeg, trunkHeight, groundYAtFn) {
  const yr = yawDeg * Math.PI / 180;
  const dx = -Math.cos(yr), dz = Math.sin(yr);
  const trunkLen = Math.max(4, Math.min(32, trunkHeight));
  // v1.3.67 TERMINAL FLOOR FIX (4th member of the v1.3.52 family: spawn, pin, pivot, THIS):
  // init at 90 vetoed every flat/downhill result — contacts there are ALL >90 (90+atan(1/d)),
  // so min-from-90 returned exactly -90 forever and the v1.3.52 "tip truly touches down"
  // comment never shipped functionally. The old ground-height pin masked it by laying the
  // trunk flush. Init at Infinity; true first-contact = min over samples; flat h=9 -> -96.
  let minContact = Infinity;
  for (let d = 2; d <= trunkLen; d++) {
    const sx = Math.round(stumpPos.x + dx * d);
    const sz = Math.round(stumpPos.z + dz * d);
    let gy;
    try { gy = groundYAtFn(sx, sz); } catch { continue; }
    const dY = gy - (stumpPos.y + 1);  // v1.3.52 PHASE C: pivot rides the stump top (spawn +1); flat ground -> ~-92deg so the tip truly touches down
    const contact = 90 + Math.atan2(-dY, d) * 180 / Math.PI;
    if (contact < minContact) minContact = contact;
  }
  if (!isFinite(minContact)) minContact = 90 + Math.atan2(1, trunkLen) * 180 / Math.PI; // no samples -> flat-equivalent tip-ground
  return Math.max(-135, Math.min(-60, Math.round(-minContact)));
}

// Collision-test predicate — returns true if a block should stop the falling
// trunk. Stricter than the pre-fall corridor obstacle test: we don't want to
// stop on grass/snow/leaves/plants, only on hard structure.
function isFallCollider(id) {
  if (!id || id === "minecraft:air") return false;
  if (id.includes("water") || id.includes("lava")) return false;
  if (id.includes("_leaves") || id.includes("_wart_block")) return false;
  if (id.includes("sapling") || (id.includes("grass") && !id.includes("grass_block")) ||   // v1.3.220: grass_block is ground (R6 A2)
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

// v1.3.220 (1004b, R6 §5): the crown of a ROOTLESS (legacy BFS) tree for the resting computation — the species' leaves
// within Chebyshev r <= maxR of the trunk top, y in [top-2, top+1]; flagged as leaves (they may crush into the ground).
// Budgeted: <= 4 x (2 maxR + 1)^2 reads, maxR <= 3.
function fallCrownCells(dim, stumpPos, topY, leafIds, maxR) {
  const out = [];
  const R = Math.max(1, Math.min(3, maxR | 0));
  const ids = new Set(leafIds);
  for (let dy = -2; dy <= 1; dy++) {
    for (let dx = -R; dx <= R; dx++) for (let dz = -R; dz <= R; dz++) {
      let b;
      try { b = dim.getBlock({ x: stumpPos.x + dx, y: topY + dy, z: stumpPos.z + dz }); } catch { continue; }
      if (b && ids.has(b.typeId)) out.push([stumpPos.x + dx, topY + dy, stumpPos.z + dz, 1]);
    }
  }
  return out;
}

// Fall-animation keyframes as [time_seconds, angle_multiplier_of_terminal]
// pairs. Matches the keyframes in falling_tree.animation.json so JS
// interpolation lines up with what the renderer is showing on screen.
const FALL_KEYS = [
  // v1.3.40: HEAVY-IMPACT curve per Abs0lum — early build unchanged (creak alignment
  // witnessed GOOD in v1.3.48), hard acceleration past ~50-60%: trees are heavy.
  // v1.3.61 SPLINTER-BREAK mirror-law amendment: the RP fall animation now carries a
  // pre-pivot hinge-creak (keys < 0.75s, |multiplier| <= 0.008, ~<=0.72deg) that is
  // deliberately RP-ONLY. The JS<->RP mirror contract applies to the PIVOT ENVELOPE
  // (keys >= 0.75s), which remains byte-identical to this table. Position channel is
  // now a constant seat [0,-16,0] from frame zero (transient-black / standing-ghost fix).
  // Impact moved 5.35s -> 4.60s; overshoot/bounce compressed; length 5.05s.
  // MUST match falling_tree.animation.json (RP-01 v1.3.49) and controller threshold (5.03).
  [0.00, 0.000],
  [0.75, 0.007],
  [1.50, 0.042],
  [2.25, 0.115],
  [3.00, 0.235],
  [3.60, 0.380],
  [4.00, 0.580],
  [4.30, 0.780],
  [4.45, 0.890],
  [4.60, 1.000],  // IMPACT
  [4.72, 1.050],  // overshoot
  [4.90, 0.980],  // bounce
  [5.05, 1.000],  // terminal rest
];

function fallAngleAtTime(elapsedS, terminalDeg) {
  if (elapsedS <= 0) return 0;
  if (elapsedS >= 5.05) return terminalDeg;  // v1.3.40: heavy-impact length
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
  "minecraft:pale_oak_leaves"];

// ---- Config -------------------------------------------------------------
const MAX_LOGS = 200;  // v0.10.0: bumped to handle 2x2 mega trees
const MAX_LEAVES = 260;
const FALL_DURATION_TICKS = 101; // v1.3.40: 5.05s heavy-impact — must match animation_length in falling_tree.animation.json
const REST_TICKS = 80;          // v1.3.220: 4.0 s after the IMPACT frame (the big rumble runs 3.88 s from the impact)
const DESPAWN_BUFFER_TICKS = 3;
const FALL_PEAK_TICKS = 44;     // v1.3.68: fall-sound peak anchor @2200ms (F4 charter) — timing-assert family member
// v1.3.68 JOIN-TIME ORPHAN SWEEP (Abs0lum design): any falling-tree/litter entity alive at boot is a crash orphan
// (legit falls live <9s and cannot span a session; despawn logic only runs while the script lives).
system.runTimeout(() => {
  for (const dn of ["overworld", "nether", "the_end"]) {
    try {
      const dim = world.getDimension(dn);
      for (const e of dim.getEntities({ type: "ft:falling_tree" })) { try { e.remove(); } catch {} }
      for (const e of dim.getEntities({ type: "pw:leaf_litter" })) { try { e.remove(); } catch {} }
    } catch {}
  }
}, 40);
// v1.3.62 DIRECTIONAL SWEEP (Abs0lum design 2026-07-18): the orphan-leaf consumption is
// paced against the fall envelope and ordered trailing-edge-first along the fall vector,
// so the REAL leaf blocks (both light layers: voxel dampening + VV dapple) withdraw WITH
// the falling canopy instead of popping off at the swap. TIMING-ASSERT FAMILY members:
const SWEEP_START_TICKS = 15;   // 0.75s — creak hold ends; RP creak keys all < 0.75s
const SWEEP_END_TICKS   = 92;   // 4.60s visual impact family (82t cue + 10t sample peak)
const MAX_SWEEP_PER_TICK = 40;  // per-tick removal cap (drain + flush bound)

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
  { x: 0, y: 0, z: 1 }, { x: 0, y: 0, z: -1 }];

const AXE_RE = /_axe$/;

// ---- Helpers ------------------------------------------------------------
const posKey = (x, y, z) => `${x},${y},${z}`;

function findConnectedTree(dim, seed, startY, speciesLogs, speciesIdx) {
  const found = [];
  const _rootedCache = new Map();  // v1.3.38: per-column rooted-elsewhere memo
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
      // v1.3.38: OTHER-TREE BOUNDARY — jungle giants touch; without this, one fell
      // consumed neighbors. Any candidate >3 blocks (horiz) from the seed whose own
      // column is independently ROOTED (same-species logs straight down to solid
      // ground, base >2.5 blocks from seed) belongs to another tree — pruned.
      const hDist = Math.hypot(nx - seed.x, nz - seed.z);
      if (hDist > 3) {
        const colKey = `${nx},${nz}`;
        let rooted = _rootedCache.get(colKey);
        if (rooted === undefined) {
          rooted = false;
          let cy = ny;
          for (let steps = 0; steps < 24; steps++) {
            let bb; try { bb = dim.getBlock({ x: nx, y: cy - 1, z: nz }); } catch { break; }
            if (!bb) break;
            if (speciesLogs.has(bb.typeId)) { cy--; continue; }
            const bid = bb.typeId;
            rooted = bid !== "minecraft:air" && !bid.endsWith("_leaves");
            break;
          }
          if (rooted) {
            const baseDist = Math.hypot(nx - seed.x, nz - seed.z);
            rooted = baseDist > 2.5;
          }
          _rootedCache.set(colKey, rooted);
        }
        if (rooted) continue;  // another tree's column — do not consume
      }
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


// =========================================================================
// v0.10.0 Concern #3 — LEAF ADJACENCY CHECK (filter standalone log columns)
// =========================================================================
// Player-built log structures (fence posts, log walls, log pillars) should
// NOT trigger the falling tree animation. Only ACTUAL trees with foliage
// should fall. A "tree" is identified by having at least one log within
// 1 block of leaves.
//
// "Within 1 block" maps to the 26-neighborhood around each log position
// (the 3x3x3 cube minus the log itself).
// =========================================================================

const NEIGHBORS_27 = (() => {
  const arr = [];
  for (let dx = -1; dx <= 1; dx++)
    for (let dy = -1; dy <= 1; dy++)
      for (let dz = -1; dz <= 1; dz++)
        arr.push({ x: dx, y: dy, z: dz });
  return arr;
})();

function hasAdjacentLeaves(logs, speciesIdx, dim) {
  const speciesLeaves = new Set(SPECIES[speciesIdx].leaves);
  // Generic foliage detection (handles cross-species canopies in mixed forests):
  const isAnyLeaves = (id) => {
    if (!id) return false;
    if (speciesLeaves.has(id)) return true;
    if (id.endsWith("_leaves")) return true;
    if (id === "minecraft:nether_wart_block") return true;
    if (id === "minecraft:warped_wart_block") return true;
    if (id === "minecraft:azalea_leaves") return true;
    if (id === "minecraft:flowering_azalea_leaves") return true;
    // Mushroom species: huge mushroom caps are the "foliage"
    if (id === "minecraft:brown_mushroom_block") return true;
    if (id === "minecraft:red_mushroom_block") return true;
    return false;
  };

  for (const p of logs) {
    for (const n of NEIGHBORS_27) {
      const np = { x: p.x + n.x, y: p.y + n.y, z: p.z + n.z };
      let nb;
      try { nb = dim.getBlock(np); } catch { continue; }
      if (nb && isAnyLeaves(nb.typeId)) return true;
    }
  }
  return false;
}

// =========================================================================
// v0.10.0 Concern #2 — 2x2 TRUNK DETECTION
// =========================================================================
// Big trees (mega_jungle, dark_oak, mega_spruce, pale_oak with fancy variants,
// our new pw:oak_elder, etc) have 2x2 wide trunks. The default 1x1 falling
// entity geometry looks broken for these — only one column of logs animates
// while the other 3 disappear instantly.
//
// This function inspects the BOTTOM LAYER of the connected log set. If the
// X/Z bounding box at that Y level is 2x2, we flag this as a 2x2 fall.
// =========================================================================
// v0.12.0-A T2: Detect oak tier from chopped block ID.
// Returns: 0=young, 1=mature, 2=old, 3=elder
// Default 1 (mature) for vanilla oak_log or unknown — gives sensible R=7.5 dodecagon.
function detectOakTier(blockId) {
  if (blockId === "pw:oak_young") return 0;
  if (blockId === "pw:oak_old") return 2;
  if (blockId === "pw:oak_elder") return 3;
  // pw:oak_mature, minecraft:oak_log, minecraft:stripped_oak_log → mature
  return 1;
}

// v0.13.1: Generic species tier detection (extends oak tier system to spruce/jungle/birch/dark_oak/pale_oak)
function detectSpeciesTier(blockId) {
  // Returns 0=young, 1=mature, 2=old, 3=elder
  if (blockId.endsWith("_young")) return 0;
  if (blockId.endsWith("_old")) return 2;
  if (blockId.endsWith("_elder")) return 3;
  if (blockId.endsWith("_mature")) return 1;
  // Vanilla logs default to mature (tier 1)
  return 1;
}



function detectTrunkWidth(logs) {
  if (!logs || logs.length === 0) return 1;

  // Find lowest Y in the log set
  let minY = Infinity;
  for (const p of logs) if (p.y < minY) minY = p.y;

  // Collect XZ positions of all logs at that bottom layer
  const xs = new Set();
  const zs = new Set();
  let bottomCount = 0;
  for (const p of logs) {
    if (p.y === minY) {
      xs.add(p.x);
      zs.add(p.z);
      bottomCount++;
    }
  }

  // 2x2 trunk: bottom layer has exactly 4 logs spread across 2 X values and 2 Z values
  if (bottomCount >= 4 && xs.size === 2 && zs.size === 2) {
    const xArr = Array.from(xs).sort((a, b) => a - b);
    const zArr = Array.from(zs).sort((a, b) => a - b);
    if ((xArr[1] - xArr[0]) === 1 && (zArr[1] - zArr[0]) === 1) {
      return 2;
    }
  }
  return 1;
}

/**
 * v0.15.17: Detect if the chopped tree had vines growing on it.
 * Scans every block 1 step away from each log for minecraft:vine.
 * Vines attach to log/leaf faces, so they're 1 block away in N/S/E/W directions.
 * Returns true if any vine block found within the tree's volume.
 */
function hasVines(logs, dimension) {
  if (!logs || logs.length === 0) return false;
  const checked = new Set();
  // Bound the search to the tree's extent + 1 (vines hang from canopy too)
  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;
  let minZ = Infinity, maxZ = -Infinity;
  for (const p of logs) {
    if (p.x < minX) minX = p.x;
    if (p.x > maxX) maxX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.y > maxY) maxY = p.y;
    if (p.z < minZ) minZ = p.z;
    if (p.z > maxZ) maxZ = p.z;
  }
  // Expand bounds slightly — vines also grow on leaves (above max trunk Y)
  const padXZ = 4;  // canopy radius
  const padYUp = 6;  // canopy height above last log
  minX -= 1; maxX += 1; minZ -= 1; maxZ += 1;
  minY -= 1; maxY += padYUp;
  minX -= padXZ; maxX += padXZ; minZ -= padXZ; maxZ += padXZ;

  // Sample a coarse grid — we just need ANY vine to flag has_vines
  const STEP = 2;
  for (let y = minY; y <= maxY; y += STEP) {
    for (let x = minX; x <= maxX; x += STEP) {
      for (let z = minZ; z <= maxZ; z += STEP) {
        try {
          const b = dimension.getBlock({ x, y, z });
          if (b && b.typeId === "minecraft:vine") return true;
        } catch (e) { /* OOB or unloaded */ }
      }
    }
  }
  return false;
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
// v1.2.34 — Species index → sapling item type for manual loot rolls.
// Used by _rollLeafLoot when cleanOrphanLeaves silently removes leaves during tree fell.
// Indices match the SPECIES array order. null = no sapling for this species (nether/mushroom).
const _LEAF_LOOT_SAPLING_BY_SPECIES = [
  "minecraft:oak_sapling",       // 0 oak
  "minecraft:spruce_sapling",    // 1 spruce
  "minecraft:birch_sapling",     // 2 birch
  "minecraft:jungle_sapling",    // 3 jungle
  "minecraft:acacia_sapling",    // 4 acacia
  "minecraft:dark_oak_sapling",  // 5 dark_oak
  "minecraft:mangrove_propagule",// 6 mangrove
  "minecraft:cherry_sapling",    // 7 cherry
  null,                          // 8 crimson (no sapling — wart block)
  null,                          // 9 warped  (no sapling — wart block)
  "minecraft:pale_oak_sapling",  // 10 pale_oak
  null,                          // 11 mushroom (no sapling — stem)
];
// v1.3.63 LOOT-EXACT (Abs0lum under-production check): per-species vanilla rates.
// jungle sapling is vanilla 2.5% (was flat 5% = over); nether/mushroom rows are 0
// (their "leaves" use self-drop / cap-roll paths below, and vanilla gives them no sticks).
const _LEAF_LOOT_SAPLING_CHANCE_BY_SPECIES = [
  0.05, 0.05, 0.05, 0.025, 0.05, 0.05, 0.05, 0.05, 0, 0, 0.05, 0];
const _LEAF_LOOT_STICK_CHANCE = 0.02;   // matches loot table pool 3 random_chance (leafy species only)
const _LEAF_LOOT_APPLE_CHANCE = 0.005;  // vanilla 1/200 — oak + dark_oak only

// Roll the rare drops (sapling 5%, stick 2%) that the loot table normally provides
// when leaves are broken without shears. Used when the falling-tree script silently
// removes leaves (no setblock destroy). Preserves player-desired drops without the
// leaf-block-as-item drop that setblock destroy was producing.
function _rollLeafLoot(dim, pos, leafTypeId, speciesIdx) {
  try {
    const center = { x: pos.x + 0.5, y: pos.y + 0.5, z: pos.z + 0.5 };
    // v1.3.63 LOOT-EXACT — vanilla manual-harvest equivalence per species class:
    if (speciesIdx === 8 || speciesIdx === 9) {
      // Wart blocks drop THEMSELVES on any break (no sticks, no sapling in vanilla).
      const wart = (typeof leafTypeId === "string" && leafTypeId.includes("wart"))
        ? leafTypeId
        : (speciesIdx === 8 ? "minecraft:nether_wart_block" : "minecraft:warped_wart_block");
      try { dim.spawnItem(new ItemStack(wart, 1), center); } catch {}
      return;
    }
    if (speciesIdx === 11) {
      // Mushroom caps: vanilla table = uniform(-6..2) clamped to >=0 -> P(0)=7/9, P(1)=1/9, P(2)=1/9.
      const n = Math.max(0, -6 + Math.floor(Math.random() * 9));
      if (n > 0) {
        const shroom = (typeof leafTypeId === "string" && leafTypeId.includes("red"))
          ? "minecraft:red_mushroom" : "minecraft:brown_mushroom";
        try { dim.spawnItem(new ItemStack(shroom, n), center); } catch {}
      }
      return;
    }
    const sapChance = _LEAF_LOOT_SAPLING_CHANCE_BY_SPECIES[speciesIdx] ?? 0.05;
    if (Math.random() < sapChance) {
      const saplingType = _LEAF_LOOT_SAPLING_BY_SPECIES[speciesIdx];
      if (saplingType) {
        try { dim.spawnItem(new ItemStack(saplingType, 1), center); } catch {}
      }
    }
    if (Math.random() < _LEAF_LOOT_STICK_CHANCE) {
      const stickCount = 1 + Math.floor(Math.random() * 2); // 1 or 2 (matches loot table set_count {min:1,max:2})
      try { dim.spawnItem(new ItemStack("minecraft:stick", stickCount), center); } catch {}
    }
    if ((speciesIdx === 0 || speciesIdx === 5) && Math.random() < _LEAF_LOOT_APPLE_CHANCE) {
      try { dim.spawnItem(new ItemStack("minecraft:apple", 1), center); } catch {}  // vanilla oak/dark_oak apples restored
    }
  } catch {}
}

// v1.3.40: WATCHDOG FIX — converted to a system.runJob generator. The AABB scan
// (up to 40k getBlock) + multi-source leaf BFS ran synchronously in one tick and
// is the prime suspect for the witnessed 10,075ms watchdog hang on elder fells.
// Yields every ~250 ops; leaves now fade over a few ticks (approved canopy-linger).
function* cleanOrphanLeavesJob(dim, logPositions, speciesIdx, sweep = null, exactLeaves = null) {
  const LEAF_DECAY_RANGE = 8;  // v1.3.51 PHASE B: range raise (witnessed: canopy left behind)
  const SEARCH_HALF = LEAF_DECAY_RANGE + 1;
  const speciesLeaves = new Set([
    ...SPECIES[speciesIdx].leaves,
    ...EXTRA_LEAF_IDS]);
  // v1.3.209 T4: a template tree hands over its exact leaf list — no AABB scan, no owned / protected BFS: the sweep
  // consumes exactly those cells (still leaves at consumption time; a neighbour's canopy is never in the list)
  if (exactLeaves && exactLeaves.length) {
    const unprotectedT = exactLeaves.slice(0, MAX_LEAVES);
    yield* sweepLeaves(dim, unprotectedT, speciesIdx, sweep);
    return;
  }

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
        if (scanned % 250 === 0) yield; // v1.3.40 watchdog throttle
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

  // v1.3.51 PHASE B — Step 1.5: OWN-CANOPY-FIRST claim. BFS from the FELLED
  // logs through connected species-leaves: these belong to the fallen tree and
  // may NOT be protected by a neighboring tree's standing logs (witnessed:
  // neighbor protection stranded our canopy edges — "canopy left behind").
  const ownedSet = new Set();
  {
    const oDist = new Map();
    const oQueue = [];
    for (const fl of logPositions) {
      for (const d of NEIGHBORS_6) {
        const p = { x: fl.x + d.x, y: fl.y + d.y, z: fl.z + d.z };
        const k = posKey(p.x, p.y, p.z);
        if (!candidates.has(k)) continue;
        if (oDist.has(k)) continue;
        oDist.set(k, 1);
        ownedSet.add(k);
        oQueue.push([p, 1]);
      }
    }
    let oGuard = 0;
    while (oQueue.length && oGuard++ < MAX_LEAVES * 16) {
      if (oGuard % 250 === 0) yield;
      const [p, d] = oQueue.shift();
      if (d >= LEAF_DECAY_RANGE) continue;
      for (const step of NEIGHBORS_6) {
        const np = { x: p.x + step.x, y: p.y + step.y, z: p.z + step.z };
        const k = posKey(np.x, np.y, np.z);
        if (!candidates.has(k)) continue;
        if (oDist.has(k)) continue;
        oDist.set(k, d + 1);
        ownedSet.add(k);
        oQueue.push([np, d + 1]);
      }
    }
  }

  // Step 2: BFS from every standing log through connected species-leaves,
  // marking leaves as "protected" up to LEAF_DECAY_RANGE distance.
  // v1.3.51: owned leaves are exempt — tie goes to the fallen tree.
  const protectedSet = new Set();
  const dist = new Map();
  const queue = [];

  // Seed: every leaf directly adjacent (face-neighbor) to any standing log
  for (const sl of standingLogs) {
    for (const d of NEIGHBORS_6) {
      const p = { x: sl.x + d.x, y: sl.y + d.y, z: sl.z + d.z };
      const k = posKey(p.x, p.y, p.z);
      if (!candidates.has(k)) continue;
      if (ownedSet.has(k)) continue;  // v1.3.51: fallen tree owns it
      if (dist.has(k)) continue;
      dist.set(k, 1);
      protectedSet.add(k);
      queue.push([p, 1]);
    }
  }

  // Expand through connected leaves
  let guard = 0;
  while (queue.length && guard++ < MAX_LEAVES * 16) {
    if (guard % 250 === 0) yield; // v1.3.40 watchdog throttle
    const [p, d] = queue.shift();
    if (d >= LEAF_DECAY_RANGE) continue;
    for (const step of NEIGHBORS_6) {
      const np = { x: p.x + step.x, y: p.y + step.y, z: p.z + step.z };
      const k = posKey(np.x, np.y, np.z);
      if (!candidates.has(k)) continue;
      if (ownedSet.has(k)) continue;  // v1.3.51: fallen tree owns it
      if (dist.has(k)) continue;
      dist.set(k, d + 1);
      protectedSet.add(k);
      queue.push([np, d + 1]);
    }
  }

  // Step 3 (v1.3.62 DIRECTIONAL SWEEP — Abs0lum design): consume unprotected leaves
  // trailing-edge-first along the fall vector, paced by the fall envelope, so the real
  // canopy's voxel shade + VV dapple withdraw in tandem with the falling entity. Loot
  // single-authority (v1.2.34 silent air + rolls) is unchanged per leaf.
  const unprotected = [];
  for (const [k, p] of candidates) {
    if (protectedSet.has(k)) continue;
    unprotected.push(p);
    if (unprotected.length >= MAX_LEAVES) break;
  }
  yield* sweepLeaves(dim, unprotected, speciesIdx, sweep);
}

/** the v1.3.62 directional sweep over a leaf list (shared by the AABB path and the T4 exact path) */
function* sweepLeaves(dim, unprotected, speciesIdx, sweep) {
  const N = unprotected.length;
  if (N === 0) return;
  const removeOne = (p) => {
    try {
      const blk = dim.getBlock(p);
      const blkType = blk?.typeId;
      if (blk) {
        try { blk.setPermutation(BlockPermutation.resolve("minecraft:air")); } catch {}
      }
      _rollLeafLoot(dim, p, blkType, speciesIdx);
      _enqueueCascade(p, dim.id);
    } catch {}
  };
  if (!sweep) {  // legacy/fallback path: immediate consumption (pre-1.3.62 behavior)
    let processed = 0;
    for (const p of unprotected) { if (++processed % 100 === 0) yield; removeOne(p); }
    return;
  }
  const sx = sweep.sx, sz = sweep.sz, fx = sweep.fx, fz = sweep.fz;
  unprotected.sort((a, b) => {
    const pa = (a.x - sx) * fx + (a.z - sz) * fz;
    const pb = (b.x - sx) * fx + (b.z - sz) * fz;
    if (pa !== pb) return pa - pb;   // most-negative projection = furthest BEHIND the fall = first
    return b.y - a.y;                // higher leaves vacate their cells soonest
  });
  const fellTick = sweep.fellTick != null ? sweep.fellTick : system.currentTick;
  let consumed = 0;
  const ivId = system.runInterval(() => {
    try {
      const tau = system.currentTick - fellTick;
      let target;
      const _swEnd = sweep.endTick || SWEEP_END_TICKS, _swT = sweep.fallT || 3.5, _swRest = sweep.restDeg || 90;   // v1.3.220
      if ((sweep.ctl && sweep.ctl.flushNow) || tau >= _swEnd) target = N;
      else if (tau < SWEEP_START_TICKS) target = 0;
      else target = Math.floor(N * Math.min(1, Math.max(0, FALLPHYS.thetaAt(tau / 20, _swT, _swRest) / _swRest)));
      let n = 0;
      while (consumed < target && n < MAX_SWEEP_PER_TICK) { removeOne(unprotected[consumed++]); n++; }
      if (consumed >= N) system.clearRun(ivId);
    } catch { try { system.clearRun(ivId); } catch {} }
  }, 1);
  // absolute safety flush — survives interval death (Android suspend class)
  system.runTimeout(() => {
    try { while (consumed < N) removeOne(unprotected[consumed++]); } catch {}
  }, (sweep.endTick || FALL_DURATION_TICKS) + REST_TICKS);
}

/**
 * Fall-direction picker. Tries to fall downhill, biased toward "away from
 * the player". We sample ground elevation in 8 compass directions at radius
 * 4 from the stump and score each by (player-awayness + downhill-ness).
 *
 * Returns a yaw in degrees so that the entity's -X local axis points in
 * the chosen direction (which is how the fall animation tips the trunk).
 */
function pickFallYaw(dim, player, stumpPos, trunkHeight, forcedYawDeg = null, lean = null) {
  const LEAN_WEIGHT = 9.0;            // v1.3.206 his F7: on FLAT ground the heavy side decides (slope stays primary); a
                                      // symmetric crown (strength ~0) leaves the old away-from-the-chopper choice

  const DIRS = 8;                      // sample 8 compass directions
  const RADIUS = 10;                   // v1.3.37: slope sampled at 10 blocks per Abs0lum spec
  const VERTICAL_SEARCH = 12;          // v1.3.37: deeper scan to catch real slopes at R=10
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

  // Ground TOP FACE at a sample point. v1.3.220 (R6 A1 / A2): the old reader returned the ground BLOCK's y and skipped
  // every id containing "grass" — grass_block included — so a lawn read two blocks low. Tree parts, plants, water and
  // snow are passable (pw_fall_physics.isFallPassable); everything else is ground.
  const groundYAt = (wx, wz) => {
    for (let dy = 3; dy >= -VERTICAL_SEARCH; dy--) {
      const p = { x: wx, y: stumpPos.y + dy, z: wz };
      let b;
      try { b = dim.getBlock(p); } catch { return stumpPos.y; }
      if (!b) continue;
      if (FALLPHYS.isFallPassable(b.typeId)) continue;
      return stumpPos.y + dy + 1;
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

  // v1.3.220 (R-54): the drop is measured from the GROUND under the stump, not from the log's y. With the old reference every
  // direction read a 2-4 block "drop" on flat ground, so the slope mode always won and his F7 flat-ground rule (the heavy
  // side, else away from the chopper; v1.3.206) never ran — flat falls went to the first sample (east) or the least obstacles.
  let stumpGroundY = stumpPos.y;
  try { const _g0 = groundYAt(stumpPos.x, stumpPos.z); if (typeof _g0 === "number") stumpGroundY = _g0; } catch { /* keep */ }

  // v1.3.37: 2x2 rule supplies a forced direction (toward the missing columns).
  // Compute drop along it for the terminal-angle calc, then return immediately.
  if (forcedYawDeg !== null) {
    const _fd = FALLPHYS.fallDirOfYaw(forcedYawDeg);   // v1.3.220 D-C565: the yaw law
    const fdx = _fd.x, fdz = _fd.z;
    const fsx = Math.round(stumpPos.x + fdx * RADIUS);
    const fsz = Math.round(stumpPos.z + fdz * RADIUS);
    let fdrop = 0;
    try { fdrop = stumpGroundY - groundYAt(fsx, fsz); } catch {}
    log(`fall dir FORCED (2x2 rule): yaw=${forcedYawDeg.toFixed(0)} drop=${fdrop}`);
    return { yaw: forcedYawDeg, drop: fdrop, groundYAt };
  }

  const trunkLen = Math.max(3, Math.min(8, trunkHeight));

  let bestScore = -Infinity;
  let bestYaw = FALLPHYS.yawOfFallDir(awayX, awayZ); // fallback: straight away (v1.3.220: the yaw law)

  // Debug: log each direction's breakdown
  const breakdown = [];

  // v1.3.37: TWO-PASS SLOPE-PRIMARY SCORING (Abs0lum spec restored):
  // trees ALWAYS fall downhill when a slope exists; player-awayness is ONLY the
  // flat-ground tiebreak. Veto removed (a downhill tree can fall toward you).
  const samples = [];
  for (let i = 0; i < DIRS; i++) {
    const theta = (i / DIRS) * Math.PI * 2;
    const dirX = Math.cos(theta);
    const dirZ = Math.sin(theta);
    const sx = Math.round(stumpPos.x + dirX * RADIUS);
    const sz = Math.round(stumpPos.z + dirZ * RADIUS);
    const drop = stumpGroundY - groundYAt(sx, sz);   // positive = downhill
    const away = dirX * awayX + dirZ * awayZ;
    const obstacles = countObstacles(dirX, dirZ, trunkLen);
    samples.push({ i, dirX, dirZ, drop, away, obstacles });
  }
  const maxAbsDrop = Math.max(...samples.map(s => Math.abs(s.drop)));
  const slopeMode = maxAbsDrop >= 1;   // any >=1-block relief -> slope rules
  for (const s of samples) {
    const score = slopeMode
      ? (8.0 * s.drop) - (OBSTACLE_WEIGHT * s.obstacles)
      : (AWAY_WEIGHT * s.away) + (DOWNHILL_WEIGHT * s.drop) - (OBSTACLE_WEIGHT * s.obstacles) +
        (lean ? LEAN_WEIGHT * lean.strength * (s.dirX * lean.x + s.dirZ * lean.z) : 0);
    breakdown.push({ i: s.i, dirX: +s.dirX.toFixed(2), dirZ: +s.dirZ.toFixed(2), away: +s.away.toFixed(2), drop: s.drop, obstacles: s.obstacles, mode: slopeMode ? "slope" : "flat", score: +score.toFixed(2) });
    if (score > bestScore) {
      bestScore = score;
      bestYaw = FALLPHYS.yawOfFallDir(s.dirX, s.dirZ);   // v1.3.220 D-C565
    }
  }

  // Log the best pick and its obstacle count for debugging
  let bestDrop = 0;
  try {
    const best = breakdown.reduce((a, b) => (a.score > b.score ? a : b));
    bestDrop = best.drop;
    log(`fall dir: yaw=${bestYaw.toFixed(0)}° obst=${best.obstacles} drop=${best.drop} away=${best.away}`);
  } catch {}

  return { yaw: bestYaw, drop: bestDrop, groundYAt };
}

function findStumpY(logPositions) {
  let minY = Infinity;
  for (const p of logPositions) if (p.y < minY) minY = p.y;
  return minY;
}

function measureColumnHeight(logPositions, chopped) {
  // v1.3.42: CONTIGUOUS column height (Abs0lum witness: falling object taller
  // than the real tree). maxY-minY counted any BRANCH log that re-crosses the
  // trunk's x/z column higher up (oak branches arc; birch has none — which is
  // why only oaks inflated). The 16-cap used to hide this; cap 32 exposed it.
  // Now: walk consecutive y's upward from the lowest log; first gap ends the trunk.
  const col = logPositions.filter(p => p.x === chopped.x && p.z === chopped.z);
  if (col.length === 0) return Math.max(2, Math.min(16, logPositions.length));
  const ys = new Set(col.map(p => p.y));
  const minY = Math.min(...ys);
  let h = 0;
  while (ys.has(minY + h)) h++;
  return Math.max(2, h);
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
  "nether_sprouts", "nether_wart"];
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
          // v1.3.62 LOOT-EQUIVALENCE (Abs0lum ruling): `air destroy` dropped every crushed
          // block AS ITSELF (MCPE-50331 — same bug class v1.2.34 fixed for leaves): saplings,
          // dead_bush sticks, vines, azalea, berries, crops... none of which a manual harvest
          // of the tree would yield. Crushed vegetation now yields NOTHING (silent air).
          b.setPermutation(BlockPermutation.resolve("minecraft:air"));
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

    // v0.13.9-C: extend damage to mobs (non-player entities) in fall corridor
    try {
      const mobs = dim.getEntities({ excludeTypes: ["minecraft:player", "ft:falling_tree", "minecraft:item", "minecraft:xp_orb"] });
      let mobHits = 0;
      for (const m of mobs) {
        const mdx = m.location.x - (stump.x + 0.5);
        const mdz = m.location.z - (stump.z + 0.5);
        const mAlong = mdx * fx + mdz * fz;
        const mLat   = mdx * (-fz) + mdz * fx;
        if (mAlong < -0.5 || mAlong > trunkLen + 1.5) continue;
        if (Math.abs(mLat) > CORRIDOR_WIDTH) continue;
        const mdy = m.location.y - stump.y;
        if (mdy < -1.5 || mdy > 3) continue;
        mobHits++;
        try { m.applyDamage(DAMAGE_AMOUNT, { cause: EntityDamageCause.entityAttack }); }
        catch (e) {
          try { m.runCommand(`damage @s ${DAMAGE_AMOUNT} entity_attack`); } catch (e2) {}
        }
      }
      log(`mob impact sweep: ${mobHits}/${mobs.length} in corridor`);
    } catch (e) { log(`mob sweep err: ${e}`); }
  } catch (e) { log(`applyImpactEffects err: ${e}`); }
}

world.afterEvents.playerBreakBlock.subscribe(ev => {
  try {
    const { player, block, brokenBlockPermutation, dimension } = ev;
    if (!player || !brokenBlockPermutation) { return; }

    const brokenId = brokenBlockPermutation.type.id;
    if (String(brokenId).indexOf('pw:slab_') === 0 || String(brokenId).indexOf('pw:seated_') === 0) { /* CANOPY EXEMPTION */ } else {
    log(`broke ${brokenId}`);
    }

    const speciesIdx = LOG_TO_SPECIES.get(brokenId);
    if (speciesIdx === undefined) return;
    log(`species idx ${speciesIdx} (${SPECIES[speciesIdx].key})`);

    // axe check — use the event's own item snapshot (the item as it was
    // when the swing started). This is reliable across API versions;
    // reading from equippable post-break was flaky.
    // v1.3.37: DISCONNECTION PRINCIPLE — any survival break that severs the trunk
    // fells the tree. Bare-hand and axe-only gates REMOVED per Abs0lum directive.
    // Creative gate below stays (mcstructure editing must not topple trees).

    if (isCreative(player)) { log("creative -> skip"); return; }

    const start = { x: block.location.x, y: block.location.y, z: block.location.z };
    const speciesLogs = new Set(SPECIES[speciesIdx].logs);

    // v1.3.206 HIS FELLING RULES (pw_fell_rules.js): trunk separated from the ground, a world-built tree, never a branch,
    // never a loose / building / player-placed log. Anything else just breaks.
    const _verdict = fellVerdict(dimension, start, speciesLogs);
    if (!_verdict.allow) { log(`[FELL-RULES] no fall: ${_verdict.reason}`); return; }
    log(`[FELL-RULES] ${_verdict.reason}${_verdict.root ? ` (root ${_verdict.root.id} tpl ${_verdict.root.tpl} ${_verdict.root.dir})` : ""}`);

    // v1.3.37: 2x2 CROSS-SECTION RULE — a 2x2 trunk does NOT fell until all four
    // columns at the cut layer are severed; it then falls TOWARD the missing three.
    let forcedYaw = null;
    try {
      const bx = start.x, by = start.y, bz = start.z;
      let quad = null;
      for (const ly of [by + 1, by - 1]) {           // trunk continues above (or below if top-cut)
        for (const qx of [bx - 1, bx]) {
          for (const qz of [bz - 1, bz]) {
            let logsAt = 0;
            for (const [ox, oz] of [[0,0],[1,0],[0,1],[1,1]]) {
              let b; try { b = dimension.getBlock({ x: qx+ox, y: ly, z: qz+oz }); } catch { continue; }
              if (b && speciesLogs.has(b.typeId)) logsAt++;
            }
            if (logsAt === 4) { quad = { qx, qz }; break; }
          }
          if (quad) break;
        }
        if (quad) break;
      }
      if (quad) {
        // width-2 trunk confirmed: count survivors at the CUT layer
        let remaining = 0; const missing = [];
        for (const [ox, oz] of [[0,0],[1,0],[0,1],[1,1]]) {
          const px = quad.qx+ox, pz = quad.qz+oz;
          if (px === bx && pz === bz) { missing.push([px, pz]); continue; } // the block just broken
          let b; try { b = dimension.getBlock({ x: px, y: by, z: pz }); } catch { continue; }
          if (b && speciesLogs.has(b.typeId)) remaining++; else missing.push([px, pz]);
        }
        if (remaining > 0) {
          log(`2x2 cross-section: ${remaining} column(s) still standing at cut layer -> no fell yet`);
          return;
        }
        // all four severed: fall toward centroid of the three previously-missing columns
        const others = missing.filter(([px, pz]) => !(px === bx && pz === bz));
        if (others.length) {
          const cx = others.reduce((a, [px]) => a + px, 0) / others.length;
          const cz = others.reduce((a, [, pz]) => a + pz, 0) / others.length;
          const vx = cx - bx, vz = cz - bz;
          const vl = Math.hypot(vx, vz) || 1;
          forcedYaw = FALLPHYS.yawOfFallDir(vx / vl, vz / vl);   // v1.3.220 D-C565: the yaw law
          log(`2x2 cross-section COMPLETE -> forced fall toward missing columns, yaw=${forcedYaw.toFixed(0)}`);
        }
      }
    } catch (e) { log(`2x2 rule err: ${e}`); }

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

        const _bfsT0 = Date.now();
        // v1.3.209 T4 (D-C503): a structure tree's falling set comes from its TEMPLATE (root = template + rotation):
        // exactly its trunk / branch logs above the cut and its leaves — never a neighbour's, no heuristic. Legacy trees
        // (no root) keep the BFS. PW_TEMPLATE_FELL switches it off in one place.
        let logs = null, exactLeaves = null, tplName = null;
        if (PW_TEMPLATE_FELL && _verdict.root) {
          try {
            const set = templateFallingSet(dimension, _verdict.root, start);
            if (set) { logs = set.trunkAbove; exactLeaves = set.leaves; tplName = set.name; log(`[T4] template ${set.name}: ${logs.length} logs above the cut, ${set.trunkBelow.length} below, ${exactLeaves.length} leaves (${Date.now() - _bfsT0}ms)`); }
            else log(`[T4] template unknown for ${_verdict.root.id} tpl ${_verdict.root.tpl}: BFS fallback`);
          } catch (e) { log(`[T4] template set err: ${e} -> BFS fallback`); logs = null; }
        }
        if (!logs) {
          logs = findConnectedTree(dimension, seed, start.y, speciesLogs, speciesIdx);
          log(`found ${logs.length} connected logs (BFS ${Date.now() - _bfsT0}ms)`);
        }
        if (logs.length < 2) return;

        // v0.10.0 Concern #3: Filter out standalone log structures (player-built
        // log walls/pillars/fences). Only actual trees with foliage should fall.
        if (touchesPlacedLog(logs)) { log(`[FELL-RULES] no fall: R4 a player-placed log is part of it`); return; }
        if (!hasNaturalCanopy(dimension, logs, 3)) {
          log(`no adjacent leaves (likely a player-built structure) -> skip felling`);
          return;
        }
        log(`leaf-adjacency confirmed - proceeding with fell`);

        // v1.3.206 his F4 = c: player blocks fixed to the tree (a treehouse, torches, signs) drop as items first
        try { const _att = dropAttachedBlocks(dimension, logs, speciesLogs); if (_att) log(`[FELL] ${_att} attached block(s) dropped as items`); }
        catch (e) { log(`attached-drop err: ${e}`); }

        // v0.10.0 Concern #2: Detect 2x2 trunk for proper falling entity geometry
        const trunkWidth = detectTrunkWidth(logs);
        log(`trunk_width=${trunkWidth}`);

        const stumpY = findStumpY(logs);
        const stump = { x: start.x, y: stumpY, z: start.z };
        const trunkH = measureColumnHeight(logs, start);
        log(`stump (${stump.x},${stump.y},${stump.z}) h=${trunkH}`);
        // v1.3.46: bare early [FELL] line REMOVED — re-emitted enriched (dir/canopy)
        // after those values exist. See WITNESS-CHANNEL block below.

        // v1.2.34 — TIMING FLIP: entity spawn happens FIRST, blocks clear 1 tick LATER.
        // The 1-tick (50ms) gap means the visual disappearance of the standing tree is
        // imperceptible — by the time the player's eye registers the change, the falling
        // entity is already in place. Previous v1.2.32 ordering cleared blocks first then
        // spawned the entity, which left a brief empty-space frame visible during fell.
        // Air permutation prepared now; the actual clearing happens in a deferred runTimeout.
        const airPerm = BlockPermutation.resolve("minecraft:air");

        // v0.15.17: For 2x2 trunks, spawn at cluster center (not chopped log) so
        // the falling tree's 2x2 base aligns with where the standing tree was.
        // Without this, the falling tree appears offset by 0.5 blocks in each direction.
        let spawnX = stump.x + 0.5;
        let spawnZ = stump.z + 0.5;
        // v1.3.217 (D-C524): a template tree falls as its own carbon copy, built around the template's ROOT cell
        const _ftTpl = (tplName && _verdict.root) ? FT_TPL_INDEX.get(tplName) : undefined;
        if (_ftTpl !== undefined) {
          spawnX = _verdict.root.x + 0.5;
          spawnZ = _verdict.root.z + 0.5;
          log(`[FT-COPY] template ${tplName} = geometry ${_ftTpl}; spawn over the root (${_verdict.root.x}, ${_verdict.root.z})`);
        } else if (trunkWidth === 2) {
          let mnX = Infinity, mxX = -Infinity, mnZ = Infinity, mxZ = -Infinity;
          for (const p of logs) {
            if (p.y === stumpY) {
              if (p.x < mnX) mnX = p.x;
              if (p.x > mxX) mxX = p.x;
              if (p.z < mnZ) mnZ = p.z;
              if (p.z > mxZ) mxZ = p.z;
            }
          }
          if (isFinite(mnX) && isFinite(mnZ)) {
            spawnX = (mnX + mxX) / 2 + 0.5;
            spawnZ = (mnZ + mxZ) / 2 + 0.5;
            log(`2x2 cluster center: (${spawnX}, ${spawnZ}) [chopped log at (${stump.x+0.5}, ${stump.z+0.5})]`);
          }
        }

        // v1.3.39: fall yaw is computed BEFORE spawn and applied via
        // SpawnEntityOptions.initialRotation so the client never sees a
        // default-yaw frame — eliminates the visible yaw-lerp "spin" at
        // fall start (client interpolates any post-spawn setRotation).
        let pick = { yaw: 0, drop: 0 };
        try {
          let _lean = null;
          try { _lean = crownLean(dimension, logs, stump, SPECIES[speciesIdx].leaves.filter((id) => !id.includes("_leaves_"))); }
          catch { _lean = null; }
          if (_lean) log(`[FELL] crown lean (${_lean.x.toFixed(2)}, ${_lean.z.toFixed(2)}) strength ${_lean.strength.toFixed(2)}`);
          pick = pickFallYaw(dimension, player, stump, trunkH, forcedYaw, _lean);
        } catch (e) { log(`pickFallYaw err: ${e}`); }

        // v1.3.62 SWEEP wiring: fall unit vector + origin tick + flush handle, captured
        // once here so the +1t leaf job and the collision pin can share them.
        const _swDir = FALLPHYS.fallDirOfYaw(pick.yaw);   // v1.3.220 D-C565: the yaw law (FALL_Z_SIGN)
        const swFx = _swDir.x;
        const swFz = _swDir.z;
        const fellTick = system.currentTick;
        const sweepCtl = { flushNow: false };
        let fallT = 3.5, impTick = 92, restDegPos = 90;   // v1.3.220: set by the physics block below; read by the +1t sweep and the cleanup

        // Try spawning the entity — if this fails, we still drop loot
        let ent = null;
        try {
          ent = dimension.spawnEntity("ft:falling_tree", {
            x: spawnX,
            // v1.3.52 PHASE C: spawn ONE block higher — the anim's 0.3s gravity
            // drop (root 0 -> -16) now terminates ON the stump top instead of
            // clipping through the remaining trunk (witnessed R5); the pivot
            // fall starts from the stump seat.
            y: stump.y + 1,
            z: spawnZ,
          }, { initialRotation: pick.yaw });
          log(`spawned entity ok (initialRotation=${pick.yaw.toFixed(0)})`);
        } catch (e) {
          // Older runtime without initialRotation support — plain spawn.
          try {
            ent = dimension.spawnEntity("ft:falling_tree", {
              x: spawnX,
              y: stump.y + 1,  // v1.3.52 PHASE C: legacy path must match primary seat
              z: spawnZ,
            });
            log(`spawned entity ok (no initialRotation; legacy path)`);
          } catch (e2) { log(`spawn failed: ${e2}`); }
        }

        // v1.2.34 — Schedule block clear for +1 tick AFTER entity spawn.
        // The user-visible standing-tree disappearance is now imperceptible because
        // the falling entity occupies the same volume by the time the eye registers
        // the change. If entity spawn failed, we still need to clear the blocks
        // (otherwise the player's chopping action does nothing visible).
        system.runTimeout(() => {
          try {
            let cleared = 0;
            for (const p of logs) {
              try {
                const b = dimension.getBlock(p);
                if (b) { b.setPermutation(airPerm); cleared++; }
              } catch (e) { log(`clear err at ${p.x},${p.y},${p.z}: ${e}`); }
            }
            log(`cleared ${cleared}/${logs.length} logs (deferred 1t)`);
            try { const _st = placeStumps(dimension, start); if (_st) log(`[FELL] ${_st} stump(s) with growth rings`); }   // v1.3.206 F9
            catch (e) { log(`stump err: ${e}`); }
            system.runJob(cleanOrphanLeavesJob(dimension, logs, speciesIdx,
              { sx: stump.x, sz: stump.z, fx: swFx, fz: swFz, fellTick, ctl: sweepCtl, fallT, endTick: impTick, restDeg: restDegPos }, exactLeaves));
            log(`leaf-cleanup job started (throttled; canopy lingers a few ticks)`);
          } catch (e) { log(`deferred-clear err: ${e}`); }
        }, 1);

        if (ent && _ftTpl !== undefined) {
          try {
            const _dirQ = { north: 0, east: 1, south: 2, west: 3 }[_verdict.root.dir] ?? 0;
            let _turn = Math.round(90 * _dirQ - pick.yaw);
            while (_turn > 360) _turn -= 360;
            while (_turn < -360) _turn += 360;
            const _lift = Math.max(0, Math.min(63, stump.y - _verdict.root.y));
            ent.setProperty("ft:tpl", _ftTpl);
            ent.setProperty("ft:lift", _lift);
            ent.setProperty("ft:turn", _turn);
            log(`[FT-COPY] tpl=${_ftTpl} lift=${_lift} turn=${_turn} (root facing ${_verdict.root.dir}, yaw ${pick.yaw.toFixed(0)})`);
          } catch (e) { log(`[FT-COPY] setProperty err: ${e} -> old model`); try { ent.setProperty("ft:tpl", -1); } catch {} }
        }
        if (ent) {
          try { ent.setProperty("ft:wood_type", speciesIdx); }
          catch (e) { log(`setProp wood_type err: ${e}`); }
          // v1.3.44: CANOPY SIZE measurement — 8 rays from the trunk top, out to
          // Chebyshev r=7, sampling y in [top-1 .. top+3] for species leaves.
          // Bounded: <= 280 getBlocks + 15ms wall-clock guard (L-PERF-2).
          // Mapping: maxR<=1 -> 0 (3x3), <=3 -> 1 (7x7), <=5 -> 2 (11x11), else 3 (15x15).
          let canopySize = 0; let _csMaxR = 0; let _csRays = "0000000";
          const _lvTally = new Map();  // v1.3.50 PHASE A: pw:variant state tally
          try {
            const topY = stump.y + trunkH - 1;
            const DIRS8 = [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]];
            const _csT0 = Date.now();
            // v1.3.45: scan ALL radii (no early break) — canopies that start
            // above/away from the trunk top (branch-structured trees) have an
            // empty r=1 ring; the old early-break read them as maxR=0 -> size 0.
            let maxR = 0; let rayMask = 0;  // exposed via _csMaxR/_csRays for the [FELL] summary
            for (let r = 1; r <= 7; r++) {
              if (Date.now() - _csT0 > 15) break;
              scan:
              for (const [dx, dz] of DIRS8) {
                for (let dy = -1; dy <= 3; dy++) {
                  let b;
                  try { b = dimension.getBlock({ x: stump.x + dx * r, y: topY + dy, z: stump.z + dz * r }); } catch { continue; }
                  if (b && PW_LEAF_TYPES.has(b.typeId)) {
                    maxR = r; rayMask |= (1 << (r - 1));
                    // v1.3.50 PHASE A: sample the pw:variant state so the entity canopy
                    // wears the SAME texture the standing tree wore (witnessed:
                    // vanilla-texture reversion + color pop at the swap).
                    try {
                      const _lv = b.permutation.getState("pw:variant");
                      if (typeof _lv === "number") _lvTally.set(_lv, (_lvTally.get(_lv) || 0) + 1);
                    } catch {}
                    break scan;
                  }
                }
              }
            }
            canopySize = maxR <= 1 ? 1 : maxR <= 3 ? 2 : 3;  // v1.3.51 PHASE B: one tier fuller (witnessed: small entity canopies)
            // v1.3.65 HEIGHT CLAMP (witnessed 2026-07-19: h=2 mature felled with canopy=3,
            // rays=1111111 — in dense groves the radial scan reads NEIGHBOR trees' leaves,
            // dressing stick-trunks in giant canopies). A tree cannot wear more canopy than
            // its height supports: h<=3 -> max 1, h<=6 -> max 2, else 3.
            const _csClamp = trunkH <= 3 ? 1 : trunkH <= 6 ? 2 : 3;
            if (canopySize > _csClamp) { log(`canopy clamp ${canopySize}->${_csClamp} (h=${trunkH})`); canopySize = _csClamp; }
            _csMaxR = maxR; _csRays = rayMask.toString(2).padStart(7, "0");
          } catch (e) { log(`canopy size err: ${e}`); }
          try { ent.setProperty("ft:canopy_size", canopySize); } catch {}
          // v1.3.50 PHASE A: dominant leaf variant -> ft:leaf_variant (0 = base/vanilla)
          let _lvMode = 0, _lvBest = 0;
          for (const [v, n] of _lvTally) { if (n > _lvBest) { _lvBest = n; _lvMode = v; } }
          try { ent.setProperty("ft:leaf_variant", _lvMode); } catch (e) { log(`setProp leaf_variant err: ${e}`); }
          try { ent.setProperty("ft:trunk_height", Math.min(32, trunkH)); }
          catch (e) { log(`setProp trunk_height err: ${e}`); }
          // v0.10.0 Concern #2: trunk_width drives geometry selection in render_controller
          try { ent.setProperty("ft:trunk_width", trunkWidth); }
          catch (e) { log(`setProp trunk_width err: ${e}`); }

          // v0.15.17: Detect and set vine status
          const hasV = hasVines(logs, dimension);
          try { ent.setProperty("ft:has_vines", hasV ? 1 : 0); }
          catch (e) { log(`setProp has_vines err: ${e}`); }
          log(`has_vines=${hasV ? 1 : 0}`);

          // v0.12.0-A T2: Oak tier picks dodecagon geometry per chopped tier
          // (young R=4, mature/old R=7.5, elder R=13). brokenId captured at top
          // of event handler. Vanilla oak_log defaults to mature (idx 1).
          if (speciesIdx === 0) {
            const oakTier = detectOakTier(brokenId);
            try { ent.setProperty("ft:oak_tier", oakTier); }
            catch (e) { log(`setProp oak_tier err: ${e}`); }
            log(`oak_tier=${oakTier} (from ${brokenId})`);
          }
          
          // v0.13.1: Set species_tier property for all species (not just oak).
          // Used by render_controller to select tier-specific dodecagon geometries.
          const speciesTier = detectSpeciesTier(brokenId);
          try { ent.setProperty("ft:species_tier", speciesTier); }
          catch (e) { log(`setProp species_tier err: ${e}`); }
          log(`species_tier=${speciesTier} (from ${brokenId})`);

          // v2.8.0 WIDEGRID: ft:canopy_size removed. ft:wood_type now directly
          // selects the species-specific geometry via render_controller's
          // Array.species_geos[q.property('ft:wood_type')]. Each species has its
          // own canopy layout within a shared 7x7 envelope.

          // v1.3.39: yaw already applied at spawn via initialRotation; re-assert
          // idempotently (same value -> no client-side lerp) to cover runtimes
          // that ignored the spawn option.
          try { ent.setRotation({ x: 0, y: pick.yaw }); } catch (e) { log(`setRotation err: ${e}`); }

          // v1.3.220 (1004b, D-C563 / R6): the RESTING ANGLE from the tree's own cells (logs above the cut + its leaves)
          // rotated about the stump top's LEADING EDGE — the drawn model's pivot (pivotRadius) — against the real ground
          // (top faces; grass_block is ground; leaves may crush 0.6 into it). Flat ground ~85-96°, downhill more, a bank less.
          // Replaces computeFallAngle (trunk axis only, ground read a block low, pivot a block high; R6 Appendix A).
          const _carbon = _ftTpl !== undefined;
          const _ftR = FALLPHYS.pivotRadius(SPECIES[speciesIdx].key, speciesTier, trunkWidth, _carbon);
          const _pivot = { x: spawnX + swFx * _ftR, y: stump.y, z: spawnZ + swFz * _ftR };
          let fallAngle = -90, _restInfo = null;
          try {
            const _cells = logs.map((p) => [p.x, p.y, p.z]);
            if (exactLeaves && exactLeaves.length) {
              // the lowest and the highest leaf of every column decide contact (below / beyond 90°); the rest never do
              const _lo = new Map(), _hi = new Map();
              for (const p of exactLeaves) {
                const k = `${p.x},${p.z}`;
                const lo = _lo.get(k); if (!lo || p.y < lo.y) _lo.set(k, p);
                const hi = _hi.get(k); if (!hi || p.y > hi.y) _hi.set(k, p);
              }
              for (const p of _lo.values()) _cells.push([p.x, p.y, p.z, 1]);
              for (const [k, p] of _hi) if (_lo.get(k) !== p) _cells.push([p.x, p.y, p.z, 1]);
            } else {
              for (const c of fallCrownCells(dimension, stump, stump.y + trunkH - 1, SPECIES[speciesIdx].leaves, Math.max(2, _csMaxR))) _cells.push(c);
            }
            let _reads = 0;
            const _gDim = dimension;
            const _ground = FALLPHYS.makeGroundReader((x, y, z) => {
              if (++_reads > 3000) return "minecraft:stone";             // budget (L-PERF-2): beyond it the scan top is ground
              let b; try { b = _gDim.getBlock({ x, y, z }); } catch { return null; }
              return b ? b.typeId : null;
            }, stump.y + 4, stump.y - 16);
            const _t0 = Date.now();
            _restInfo = FALLPHYS.restAngle(_cells, _pivot, { x: swFx, z: swFz }, _ground, { fine: 1 });
            fallAngle = Math.max(-135, Math.min(-1, -Math.round(_restInfo.deg)));
            log(`[FALL] rest ${_restInfo.deg}° (${_cells.length} cells, ${_restInfo.tested} tests, ${_reads} reads, ${Date.now() - _t0}ms) pivot r=${_ftR} contact=${_restInfo.contact ? _restInfo.contact.slice(0, 3).join(",") : "none"}`);
          } catch (e) { log(`[FALL] rest err: ${e} -> -90`); fallAngle = -90; }
          restDegPos = -fallAngle;
          fallT = FALLPHYS.fallDuration(trunkH);
          impTick = Math.max(10, Math.round(20 * FALLPHYS.impactTime(fallT, restDegPos)));
          const fallTTenths = Math.max(8, Math.min(80, Math.round(fallT * 10)));

          // v1.3.46 WITNESS-CHANNEL FIX: log() is console.log + DEBUG=false, which the
          // content-log GUI never shows — every fell diagnostic (incl. the direction
          // datum requested for the yaw-mapping fix) has been INVISIBLE to Abs0lum.
          // Witness-critical data now goes through the two channels he can actually
          // capture: the [FELL] chat line (screenshots) and console.warn (log pastes).
          try {
            const tierNames = ["young", "mature", "old", "elder"];
            const fellTier = detectSpeciesTier(brokenId);
            const tn = tierNames[fellTier] ?? `t${fellTier}`;
            const summary = `${SPECIES[speciesIdx].key} ${tn} trunk ${trunkWidth}x${trunkWidth} h=${trunkH} logs=${logs.length} | dir yaw=${pick.yaw.toFixed(0)} ${FALLPHYS.compassName(swFx, swFz)} rest=${fallAngle} T=${fallT.toFixed(2)}s imp=${(impTick / 20).toFixed(2)}s | canopy=${canopySize} (maxR=${_csMaxR} rays=${_csRays})`;
            player.sendMessage(`§7[FELL] §a${summary}`);
            console.warn(`[PW-FELL] ${summary}`);
          } catch (e) { log(`fell-id msg err: ${e}`); }
          try { ent.setProperty("ft:fall_angle", Math.max(-135, Math.min(-60, fallAngle))); }   // v1.3.220: legacy range; the renderer reads rest_angle + fall_t
          catch (e) { log(`setProp fall_angle err: ${e}`); }
          // v1.3.47: rest_angle is the SOLE input of the rest animation. Set at
          // spawn (= terminal fallAngle) and OVERWRITTEN at collision-pin. The
          // fall animation keeps reading fall_angle, which is never rewritten
          // mid-fall anymore -- that rewrite made the FALLING state render
          // newAngle * curveMult(t) for the transition tick (visible upright
          // SNAP); and pins shallower than -60 threw out-of-range on
          // fall_angle's [-135,-60] and were silently lost (over-rotate snap).
          try { ent.setProperty("ft:rest_angle", fallAngle); }
          catch (e) { log(`setProp rest_angle err: ${e}`); }
          try { ent.setProperty("ft:fall_t", fallTTenths); }   // v1.3.220: the fall duration (tenths of a second) for the RP's curve
          catch (e) { log(`setProp fall_t err: ${e}`); }
          log(`species=${SPECIES[speciesIdx].key} fallAngle=${fallAngle}°`);

          // v1.3.39: playAnimation overlay REMOVED — controller.animation.
          // ft_falling_tree.fall auto-plays 'fall' from spawn (scripts.animate),
          // so the API overlay double-drove the same animation (additive root
          // rotation risk) and is unnecessary.

          // v1.2.21 — Phase 3: Play tree fall sound based on species tier.
          // young → small, mature → medium, old/elder → big, nether species → generic
          let impactCueId = null;  // v1.3.40: cancellable impact cue
          try {
            let fallSound = "pw.tree_fall.medium";
            const speciesKey = SPECIES[speciesIdx].key;
            if (speciesKey === "crimson" || speciesKey === "warped" || speciesKey === "mushroom") {
              fallSound = "pw.tree_fall.generic";
            } else if (speciesTier === 0) {
              fallSound = "pw.tree_fall.small";
            } else if (speciesTier === 1) {
              fallSound = "pw.tree_fall.medium";
            } else if (speciesTier === 2 || speciesTier === 3) {
              fallSound = "pw.tree_fall.big";
            }
            // v1.3.38: TWO-CUE AUDIO (Abs0lum witness: delayed start felt late).
            // Cue 1: the original fall sound (creak/tear) fires AT THE CUT (t=0).
            // Cue 2: the pack's dedicated pw.tree_impact.<tier> fires at visual
            // impact (tick 106 = 5.30s), so the crash lands with the hit and the
            // rumble tail plays out over the extended rest.
            const impactSound = fallSound.replace("tree_fall", "tree_impact");
            try { dimension.playSound(fallSound, { x: spawnX, y: stump.y, z: spawnZ }); log(`creak cue: ${fallSound} @t0`); }
            catch (e) { log(`creak cue err: ${e}`); }
            const impX = spawnX, impY = stump.y, impZ = spawnZ, impDim = dimension;
            // v1.3.40: impact retimed to the new visual impact (4.60s = 92t) and the
            // handle is captured so a collision-freeze can CANCEL it — previously the
            // scheduled cue still fired after the collision path had already played
            // its own impact, producing a phantom late second impact.
            // v1.3.42: all impact samples normalized to peak @ +0.5s (10t); cue
            // fires at 82t so the thud lands exactly on the 4.60s visual impact,
            // with the samples' quiet crash-rustle riding the fast final sweep.
            impactCueId = system.runTimeout(() => {
              try { impDim.playSound(impactSound, { x: impX, y: impY, z: impZ }); log(`impact cue: ${impactSound} @${Math.max(1, impTick - 10)}t (peak@${impTick}t)`); }
              catch (e) { log(`impact cue err: ${e}`); }
            }, Math.max(1, impTick - 10));   // v1.3.220: the samples peak at +0.5 s -> fire 10 ticks before the impact frame
            // v1.3.220: the controller leaves the fall state ON the impact frame (the curve is clamped at rest from here on)
            system.runTimeout(() => { try { if (ent && ent.isValid && !pinStopped) ent.setProperty("ft:fall_stopped", 1); } catch { /* gone */ } }, impTick);
          } catch (e) { log(`fall sound err: ${e}`); }

          // v1.2.30 C-10 — mid-fall leaf shedding for cinematic fall.
          // Schedule 3 bursts of leaf_litter spawns along the falling arc at
          // 30%, 55%, 80% of FALL_DURATION_TICKS. Each burst spawns 2-4 entities
          // at randomized positions around the stump, mid-air. The leaf_litter
          // physics (has_gravity=true) gives them a natural fall path.
          // Cost: 3 timeouts + 6-12 spawnEntity calls per fall. Negligible.
          try {
            const speciesKey = SPECIES[speciesIdx].key;
            const leafTypeId = `pw:${speciesKey}_leaves`;
            const woodTypeIdx = PW_LEAF_TO_WOOD_TYPE[leafTypeId];
            // Some species don't have leaf_litter mapping (crimson/warped/mushroom)
            // — skip silently in that case
            if (woodTypeIdx !== undefined) {
              const SHED_FRACTIONS = [0.30, 0.55, 0.80];
              const baseSpawnX = spawnX;  // capture for closure
              const baseSpawnY = stump.y;
              const baseSpawnZ = spawnZ;
              const cdim = dimension;
              for (const frac of SHED_FRACTIONS) {
                const delay = Math.floor(impTick * frac);   // v1.3.220
                system.runTimeout(() => {
                  try {
                    const sheddingCount = 2 + Math.floor(Math.random() * 3);  // 2..4
                    for (let i = 0; i < sheddingCount; i++) {
                      const offsetX = (Math.random() - 0.5) * 6;
                      const offsetZ = (Math.random() - 0.5) * 6;
                      const offsetY = 4 + Math.random() * 8;  // mid-air spawn
                      const sLoc = {
                        x: baseSpawnX + offsetX,
                        y: baseSpawnY + offsetY,
                        z: baseSpawnZ + offsetZ
                      };
                      const ent2 = cdim.spawnEntity("pw:leaf_litter", sLoc);
                      if (ent2) {
                        try { ent2.setProperty("pw:wood_type", woodTypeIdx); } catch {}
                        try { ent2.setProperty("pw:lifetime", 0); } catch {}
                        try { ent2.setProperty("pw:on_ground", 0); } catch {}
                      }
                    }
                  } catch {}
                }, delay);
              }
            }
          } catch (e) { log(`mid-fall shed scheduler err: ${e}`); }

          // Pin the entity at its spawn location every tick + run collision sweep.
          // Without pinning, water flow, gravity edge-cases, or chunk-border
          // drift can push the "dead" prop entity around. The collision sweep
          // (2C) samples world blocks along the current trunk orientation each
          // tick and stops the fall animation early if the trunk would pass
          // through a solid block — fixes the "swing through walls" issue.
          const pinX = spawnX;  // v0.15.17: matches 2x2 cluster center logic above
          // v1.3.66 SEAT-PIN PARITY (L-PATH-1 closure of the v1.3.52 family): spawn moved to
          // stump.y+1 in v1.3.52 but this pin kept stump.y — every tick-1 teleport yanked the
          // entity DOWN one block. The old 0.3s RP gravity drop masked the yank; the v1.3.66-RP
          // constant seat exposed it (witnessed: "still falls one block after break"). The pin
          // and the collision-sweep origin now share the spawn/pivot convention (stumpPos.y+1).
          const pinY = stump.y + 1;
          const pinZ = spawnZ;
          const pinRotY = ent.getRotation().y;
          const pinYawRad = pinRotY * Math.PI / 180;
          const _pinDir = FALLPHYS.fallDirOfYaw(pinRotY);   // v1.3.220 D-C565
          const pinFx = _pinDir.x;
          const pinFz = _pinDir.z;
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
              if (elapsed * 20 >= impTick + 2) {  // v1.3.220: the impact frame (was the fixed 5.05 s). v1.3.47: was 5.88 — STALE consumer from the
                // v1.3.37 timeline that the v1.3.49 retime missed. Fall completes at
                // 5.05 (curve clamps to terminal); sweeping past it collision-tests
                // the RESTED trunk, whose contact-envelope samples can floor() into
                // the surface block on slopes = false pin that visibly re-poses a
                // resting tree. The impact sound this branch played was a duplicate
                // of the scheduled 82t cue (1.28s late, masked under the rumble).
                pinStopped = true;
                return;
              }
              if (elapsed < 0.25) return;  // skip first few ticks while still vertical

              const curAngleDeg = -FALLPHYS.thetaAt(elapsed, fallT, -fallAngle);   // v1.3.220: the physics curve
              // v1.3.67 TERMINAL-APPROACH GUARD: the computed terminal IS ground contact by
              // construction (tip-grounding). Within 1.5deg of it the fall is landing — stop
              // sweeping so collider floors (sand/gravel/stone) can't false-pin during the
              // 1.05x overshoot and freeze a buried rest_angle + duplicate impact.
              if (Math.abs(curAngleDeg) >= Math.abs(fallAngle) - 1.5) { pinStopped = true; return; }
              const angleRad = Math.abs(curAngleDeg) * Math.PI / 180;
              const sinA = Math.sin(angleRad);
              const cosA = Math.cos(angleRad);

              // Sample positions along the trunk (r = 2..trunkH+1, one per block)
              // Skip r=0,1 since those are at the stump/just above (won't collide
              // with anything the pre-fall obstacle check didn't already catch)
              let hitR = 0;
              for (let r = 2; r <= trunkH + 1; r++) {
                // v1.3.220: the trunk axis hinged at the leading-edge pivot (R6 A7: the old origin was a block high)
                const _along = -_ftR * cosA + r * sinA, _up = _ftR * sinA + r * cosA;
                const px = _pivot.x + pinFx * _along;
                const py = _pivot.y + _up;
                const pz = _pivot.z + pinFz * _along;
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
                // v1.3.47: freeze via ft:rest_angle ONLY. fall_angle is NOT
                // rewritten (mid-fall rewrite caused the upright snap: falling
                // state rendered freezeAngle * curveMult(t) before the rest
                // transition landed). rest_angle range [-135,-1] matches this
                // clamp exactly -- shallow pins no longer silently throw.
                const freezeAngle = Math.max(-135, Math.min(-1, Math.round(curAngleDeg)));
                try { ent.setProperty("ft:rest_angle", freezeAngle); } catch {}
                try { ent.setProperty("ft:fall_stopped", 1); } catch {}
                try { console.warn(`[PW-PIN] r=${hitR} freeze=${freezeAngle} deg`); } catch {}
                pinStopped = true;
                sweepCtl.flushNow = true;  // v1.3.62: canopy landed early — drain the sweep
                log(`collision at r=${hitR} angle=${freezeAngle}°`);
                // v1.3.40: cancel the scheduled impact cue — the collision path
                // plays its own impact NOW; without this the 92t cue fired late.
                if (impactCueId !== null) { try { system.clearRun(impactCueId); impactCueId = null; } catch {} }
                
                // v1.2.21 — Phase 3: Play impact sound on collision-stop
                try {
                  let impactSound = "pw.tree_impact.medium";
                  const speciesKey = SPECIES[speciesIdx].key;
                  if (speciesKey === "crimson" || speciesKey === "warped" || speciesKey === "mushroom") {
                    impactSound = "pw.tree_impact.generic";
                  } else if (speciesTier === 0) {
                    impactSound = "pw.tree_impact.small";
                  } else if (speciesTier === 1) {
                    impactSound = "pw.tree_impact.medium";
                  } else if (speciesTier === 2 || speciesTier === 3) {
                    impactSound = "pw.tree_impact.big";
                  }
                  dimension.playSound(impactSound, { x: pinX, y: pinY, z: pinZ });
                } catch (e) { log(`impact sound err: ${e}`); }
              }
            } catch {
              system.clearRun(pinId);
            }
          }, 1);

          try { dimension.playSound("dig.wood", stump, { volume: 1.3, pitch: 0.85 }); } catch {}

          // Compute the fall-direction vector once for all particle scheduling
          const _fxDir = FALLPHYS.fallDirOfYaw(ent.getRotation().y);   // v1.3.220 D-C565
          const fx = _fxDir.x;
          const fz = _fxDir.z;
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
                const angleRad = FALLPHYS.thetaAt(impTick * phase.tFrac / 20, fallT, -fallAngle) * Math.PI / 180;   // v1.3.220: where the crown really is
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
                // v1.2.21 — Phase 3: spawn pw:leaf_fall particle at canopy position
                // (only for leaf-bearing trees — skip nether stems/mushroom)
                const speciesKey = SPECIES[speciesIdx].key;
                if (speciesKey !== "crimson" && speciesKey !== "warped" && speciesKey !== "mushroom") {
                  try {
                    dimension.runCommand(
                      `particle pw:leaf_fall ${cx.toFixed(2)} ${cy.toFixed(2)} ${cz.toFixed(2)}`
                    );
                  } catch {}
                }
              } catch {}
            }, Math.floor(impTick * phase.tFrac));   // v1.3.220
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
          }, impTick);   // v1.3.220: the impact frame
        }

        // schedule cleanup
        system.runTimeout(() => {
          try { ent?.remove(); } catch {}
          // v1.3.217 his 13:57 ruling (F8 b reverted): NO lying log. The trunk's logs drop as items along the line where
          // it came down (one per block of trunk, from 2 blocks past the stump), the branch logs at the crown's end.
          // Leaf litter + saplings + sticks + apples still come from the leaves.
          let _dropped = 0;
          try {
            const _n = logs.length;
            const _run = Math.max(1, Math.min(trunkH, _n));
            for (let i = 0; i < _n; i++) {
              const _d = 2 + Math.min(i, _run - 1);
              const _p = { x: Math.floor(stump.x + 0.5 + swFx * _d), y: stump.y, z: Math.floor(stump.z + 0.5 + swFz * _d) };
              dropItems(dimension, _p, SPECIES[speciesIdx].drop, 1);
              _dropped++;
            }
          } catch (e) { log(`fall-line drops err: ${e}`); dropItems(dimension, stump, SPECIES[speciesIdx].drop, logs.length - _dropped); }
          log(`[FELL] ${logs.length} log(s) dropped as items along the fall line (no lying log)`);
          try { dimension.playSound("random.wood_click", stump, { volume: 2.0, pitch: 0.6 }); } catch {}
          applyAxeDamage(player, logs.length - 1);
          log(`cleanup done`);
        }, impTick + REST_TICKS + DESPAWN_BUFFER_TICKS);   // v1.3.220
      } catch (e) {
        log(`system.run err: ${e}`);
      }
    });
  } catch (e) {
    log(`subscribe err: ${e}`);
  }
});


// =========================================================================
// DYNAMIC HELD-TORCH LIGHTING (v0.6.2)
// =========================================================================
// Detects torch in player's hand; places an invisible pw:held_light block at
// the player's feet emitting light level 15. Updates on each player tick.
// Removes when torch unequipped or player logs out.
// =========================================================================

const TORCH_ITEMS = new Set([
  "minecraft:torch",
  "minecraft:soul_torch",
  "minecraft:redstone_torch",
  "minecraft:lantern",
  "minecraft:soul_lantern"]);

// Track each player's current held-light position so we can clean it up
const heldLightPositions = new Map(); // player.id → {x, y, z, dimension}

function playerHoldsTorch(player) {
  try {
    const eq = player.getComponent("minecraft:equippable");
    if (!eq) return false;
    const mainHand = eq.getEquipment("Mainhand");
    if (mainHand && TORCH_ITEMS.has(mainHand.typeId)) return true;
    const offHand = eq.getEquipment("Offhand");
    if (offHand && TORCH_ITEMS.has(offHand.typeId)) return true;
  } catch (_) {}
  return false;
}

function placeHeldLightAt(player) {
  try {
    const loc = player.location;
    const dim = player.dimension;
    // Round to block coords, offset up by 1 block from feet (torso level is better lit)
    const bx = Math.floor(loc.x);
    const by = Math.floor(loc.y) + 1;
    const bz = Math.floor(loc.z);
    const block = dim.getBlock({ x: bx, y: by, z: bz });
    if (!block) return null;
    // Only replace if current block is air or our held_light
    if (block.typeId !== "minecraft:air" && block.typeId !== "pw:held_light") return null;
    block.setType("pw:held_light");
    return { x: bx, y: by, z: bz, dimension: dim };
  } catch (_) {
    return null;
  }
}

function removeHeldLightAt(pos) {
  if (!pos) return;
  try {
    const block = pos.dimension.getBlock({ x: pos.x, y: pos.y, z: pos.z });
    if (block && block.typeId === "pw:held_light") {
      block.setType("minecraft:air");
    }
  } catch (_) {}
}

function updatePlayerLight(player) {
  const id = player.id;
  const hasLight = playerHoldsTorch(player);
  const prev = heldLightPositions.get(id);

  if (!hasLight) {
    if (prev) { removeHeldLightAt(prev); heldLightPositions.delete(id); }
    return;
  }

  // Holds torch — ensure light is at current position
  const target = { x: Math.floor(player.location.x), y: Math.floor(player.location.y) + 1, z: Math.floor(player.location.z) };
  if (prev && (prev.x !== target.x || prev.y !== target.y || prev.z !== target.z)) {
    removeHeldLightAt(prev);
  }
  if (!prev || prev.x !== target.x || prev.y !== target.y || prev.z !== target.z) {
    const placed = placeHeldLightAt(player);
    if (placed) heldLightPositions.set(id, placed);
  }
}

// v0.16.10: movement-gated polling — only update when player moved
const _lastTorchPos = new Map();  // playerId -> {x, y, z}
function _hasMoved(player) {
  const id = player.id;
  const loc = player.location;
  const last = _lastTorchPos.get(id);
  if (!last) {
    _lastTorchPos.set(id, { x: loc.x, y: loc.y, z: loc.z });
    return true;  // first check, do update
  }
  const dx = loc.x - last.x, dy = loc.y - last.y, dz = loc.z - last.z;
  const dist2 = dx*dx + dy*dy + dz*dz;
  if (dist2 > 0.25) {  // moved >0.5 blocks
    _lastTorchPos.set(id, { x: loc.x, y: loc.y, z: loc.z });
    return true;
  }
  return false;
}

system.runInterval(() => {
  try {
    for (const p of world.getAllPlayers()) {
      // v0.16.10: skip if player hasn't moved AND already has a light
      if (!_hasMoved(p) && heldLightPositions.has(p.id)) continue;
      updatePlayerLight(p);
    }
  } catch (_) {}
}, 20);  // v1.3.35 perf: was 8t — movement-gated held-torch light (1Hz)

// Clean up on player leave
world.afterEvents.playerLeave.subscribe((ev) => {
  const prev = heldLightPositions.get(ev.playerId);
  if (prev) { removeHeldLightAt(prev); heldLightPositions.delete(ev.playerId); }
});

log("dynamic held-torch lighting active");


// =========================================================================
// PERMUTATION SYSTEM v0.14.5
// =========================================================================
// Custom block component "pw:randomize_variant" — fires onPlace for any
// pw:* block that includes it. Sets a uniformly-random pw:variant value
// in [0..N-1] where N is the number of declared values for that state.
// 
// Why this works (engine reasoning):
//   Bedrock custom components fire on ALL block placements: player, feature,
//   structure, fill, /setblock. Variation arrays in terrain_texture only work
//   for vanilla blocks; custom blocks need property-driven permutations and a
//   randomization step. This component is the randomization step.
// 
// The script reads the property's declared value list from the block's
// permutation object so we don't hardcode "5" — works with any property size.
// =========================================================================

// v0.14.14: REVERTED v0.14.13 random_ticking experiment.
// 
// v0.14.13 attempted to add onRandomTick callback to fix worldgen leaves staying
// at variant=0. It broke leaf registration entirely on PS5/Android — leaves
// stopped registering with the engine and cascaded into "Unknown block" errors.
// 
// v0.14.14 restores the v0.14.12 behavior: onPlace only. Worldgen-placed leaves
// will all be at variant=0 (one variant per tree, slightly gridlike) but trees
// register correctly and player-placed leaves randomize as expected.
// v1.0.1 — Type-aware variant count lookup. Leaves declare 6 variants (v0..v5);
// log tier blocks (young/mature/old/elder per species) declare 5 (v0..v4).
// Hardcoded N=6 in v0.15.15 only worked for leaves; logs got bogus state value
// 5 from the random pick, which silently failed to match any permutation and
// caused the "all bark = variant 0" bug observed in v1.0.0/v1.0.1 (lesson #150).
// v1.0.1 §2.2 leaf rework: leaves reduced from 6 → 4 variants
//   variant 0 = pw_leaves_v0 (UNTOUCHED canonical 10-cube — engine fallback)
//   variant 1 = pw_leaves_v1 (BOTTOM+MIDDLE 6-cube — no top puffs)
//   variant 2 = pw_leaves_v2 (MIDDLE+TOP   6-cube — no bottom puffs)
//   variant 3 = pw_leaves_v3 (UNIVERSAL    8-cube — slight bias, layer-agnostic)
//   See pickLeafVariant() below for layer-aware selection logic.
const PW_VARIANT_COUNT = {
  // Leaves: 7 variants (v0..v6) — v0 worldgen default, v1-v6 sectional (Phase 2)
  "pw:oak_leaves": 7, "pw:spruce_leaves": 7, "pw:birch_leaves": 7,
  "pw:jungle_leaves": 7, "pw:dark_oak_leaves": 7, "pw:pale_oak_leaves": 7,
  "pw:acacia_leaves": 7, "pw:mangrove_leaves": 7, "pw:cherry_leaves": 7,
  "pw:azalea_leaves": 7, "pw:flowering_azalea_leaves": 7,
  // Log tiers: 5 variants (v0..v4)
  "pw:oak_young": 5, "pw:oak_mature": 5, "pw:oak_old": 5, "pw:oak_elder": 5,
  "pw:spruce_young": 5, "pw:spruce_mature": 5, "pw:spruce_old": 5, "pw:spruce_elder": 5,
  "pw:birch_young": 5, "pw:birch_mature": 5, "pw:birch_old": 5,
  "pw:jungle_young": 5, "pw:jungle_mature": 5, "pw:jungle_old": 5, "pw:jungle_elder": 5,
  "pw:dark_oak_elder": 5, "pw:pale_oak_elder": 5
};

// v1.2.27 §2 — Section/exposure-aware leaf variant selection.
// REPLACED v1.0.1 layer-based detection (Y±1 neighbor check) with the
// SECTION FLAG SCANNER (defined later in this file). The flag scanner does
// proper walk-up/walk-down to find canopy bounds and 6-face neighbor check
// for exposure, then writes pw:section + pw:exposure block states. This
// picker reads those states and selects a section-appropriate variant.
//
// Variant geometry semantics (matched to pw_leaves_variants.geo.json):
//   v0 = worldgen default / distant view (11 cubes — heaviest, complete silhouette)
//   v1 = bottom_outer_a (10 cubes — comprehensive: bottom corners + axis puffs + bottom face)
//   v2 = bottom_outer_b (9  cubes — alternate bottom for visual diversity)
//   v3 = middle_inner   (1  cube  — lightest; god-ray friendly + perf)
//   v4 = middle_outer   (5  cubes — outward corner puffs only)
//   v5 = top_outer_a    (9  cubes — top corners + axis puffs + top face)
//   v6 = top_outer_b    (7  cubes — alternate top for visual diversity)
//
// Pool keyed on `${section}_${exposure}`:
//   - bottom (0) outer (1): v1/v2 weighted
//   - middle (1) inner (0): v3 only
//   - middle (1) outer (1): v4 only
//   - top    (2) outer (1): v5/v6 weighted
//   - bottom (0) inner (0): fallback to v3 (rare — leaf-walled bottom canopy)
//   - top    (2) inner (0): fallback to v3 (rare — leaf-walled top canopy)
const PW_LEAF_VARIANT_POOLS = {
  // v1.2.47: redistributed v3 (vertical-spike) and v6 (wild scatter) into outer pools
  // v3 in 1_0/0_0/2_0 vestigial — classifier rarely produces exposure=0 in practice
  "0_1": [1, 1, 2, 3],     // bottom outer — adds v3 (25%)
  "1_0": [3],              // middle inner (vestigial)
  "1_1": [3, 4, 4],        // middle outer — adds v3 (33% v3, 67% v4)
  "2_1": [3, 5, 5, 6, 6],  // top outer — adds v3 (20% v3, 40% v5, 40% v6)
  "0_0": [3],              // bottom inner (vestigial)
  "2_0": [3],              // top inner    (vestigial)
};

// Pick variant for a leaf block based on the section/exposure flags written by
// the SECTION FLAG SCANNER. If flags aren't set yet (pw:section_rolled !== true),
// returns 0 (worldgen default — let the flag scanner go first).
//
// For non-leaf blocks (logs etc.) returns plain uniform pick from 0..N-1.
// =========================================================================
// v1.3.196 LEAF LOOK (D-C343 / D-C345, the C-WH80 pilot rule; his GO 18:44 CT 09-30)
//   A leaf's look is picked ONCE from its position (a fixed hash, never Math.random) and its distance to the wood:
//   touching wood -> cards only (v5 / v6); 2..band blocks -> a coin flip by position between cards and full; farther -> one of five
//   full shapes (v0-v4). Spruce: seven full shapes (no cards, as in Java). Band: jungle / acacia 4, spruce 0, others 3.
//   Distance is probed in Manhattan shells around the leaf (<= band, max 4), not walked through the leaves (the pilot's BFS).
// =========================================================================
const PW_LEAF_BAND = { "pw:jungle_leaves": 4, "pw:acacia_leaves": 4, "pw:spruce_leaves": 0 };
function pwCellHash(x, y, z) {
  let h = (Math.imul(x | 0, 73856093) ^ Math.imul(y | 0, 19349663) ^ Math.imul(z | 0, 83492791)) >>> 0;
  h ^= h >>> 16; h = Math.imul(h, 2246822507) >>> 0; h ^= h >>> 13; h = Math.imul(h, 3266489909) >>> 0; h ^= h >>> 16;
  return h >>> 0;
}
const PW_WOOD_SHELLS = (() => {
  const sh = [[], [], [], [], []];
  for (let dx = -4; dx <= 4; dx++) for (let dy = -4; dy <= 4; dy++) for (let dz = -4; dz <= 4; dz++) {
    const d = Math.abs(dx) + Math.abs(dy) + Math.abs(dz);
    if (d >= 1 && d <= 4) sh[d].push([dx, dy, dz]);
  }
  return sh;
})();
function pwIsWood(id) { return PW_TA_LOG_TYPES.has(id) || /(_log|_wood|_stem|hyphae)$/.test(id); }
function pwWoodDistance(dim, x, y, z, maxD) {
  for (let d = 1; d <= maxD; d++) {
    for (const [a, b, c] of PW_WOOD_SHELLS[d]) {
      let n; try { n = dim.getBlock({ x: x + a, y: y + b, z: z + c }); } catch { continue; }
      if (n && pwIsWood(n.typeId)) return d;
    }
  }
  return 99;
}
function pwLeafLook(block) {
  const id = block.typeId; const loc = block.location; const h = pwCellHash(loc.x, loc.y, loc.z);
  if (id === "pw:spruce_leaves") return (h >>> 12) % 7;
  const band = PW_LEAF_BAND[id] ?? 3;
  let d = 99; try { d = pwWoodDistance(block.dimension, loc.x, loc.y, loc.z, Math.min(band, 4)); } catch { /* unloaded neighbour */ }
  if (d === 1) return 5 + (h % 2);
  if (d >= 2 && d <= band && ((h >>> 8) & 1) === 1) return 5 + ((h >>> 9) % 2);
  return (h >>> 12) % 5;
}

// v1.3.198 LEAF NUDGE (D-C350, Z1 option B): neighbouring leaves never share a plane (z-clipping, his p16 note). pw:off =
// (x + 2y + 4z) mod 7 picks one of seven tiny shifts (k-3)*(1,2,3)*0.006 block: two leaves that touch on a face OR on an edge (the
// diagonal card twins) always get different shifts, so their cube faces and cards are never coplanar. Set with the look (onPlace +
// the scanner's assign-once); unscanned leaves keep 0, like their look.
function pwNudge(loc) { return (((Math.floor(loc.x) + 2 * Math.floor(loc.y) + 4 * Math.floor(loc.z)) % 7) + 7) % 7; }

function pickVariantForBlock(block) {
  const typeId = block.typeId;
  const isLeaf = typeId.endsWith("_leaves");
  if (isLeaf) return pwLeafLook(block);   // v1.3.196: position + distance to the wood, no Math.random
  const N = PW_VARIANT_COUNT[typeId] || 5;
  return Math.floor(Math.random() * N);
}

function pwRandomizeVariant(arg) {
  // v1.0.1 — sets BOTH pw:variant and pw:rseed=true.
  // v1.2.19 — for log blocks, ALSO sets pw:top_variant (0-6) INDEPENDENTLY so
  // the log-top end-grain texture varies separately from the bark side variant.
  // 7 Patrix variants per species (variants 2,4,6,7,8 inpainted crack-free; 3,5 retain cracks for variety).
  // pw:rseed=true marks "already randomized" for the periodic scanner.
  // Worldgen-placed blocks never fire onPlace, so they remain rseed=false
  // until the scanner picks them up. Player-placed blocks fire onPlace
  // (this function) and are randomized instantly.
  // v1.2.27 §3 — for leaves, if pw:section_rolled isn't true yet, DON'T set rseed.
  // This keeps the leaf at v0 (default) and lets the section flag scanner +
  // variant scanner pair re-process it on a later cycle. Without this, onPlace
  // would set rseed=true permanently and the scanner would skip the leaf forever.
  try {
    const block = arg.block;
    // v1.3.206 (T0 probe P-2): structureManager.place fires onPlace, which re-rolled the BAKED looks of our structure
    // trees and buildings. A block that already carries rseed=true has its final look: leave it alone.
    try { if (block.permutation.getState("pw:rseed") === true) return; } catch { /* no rseed state */ }
    const isLeaf = block.typeId.endsWith("_leaves");
    const choice = pickVariantForBlock(block);

    // For leaves: only set rseed=true if section flags are already set
    // (which only happens if scanner had previously processed this position
    // before the leaf was broken and replaced — uncommon).
    const setRseed = true;   // v1.3.196: a leaf's look needs no classification first (position + wood), so it is final
    let newPerm = block.permutation.withState("pw:variant", choice);
    try { if (PW_LEAF_TYPES_DECAY.has(block.typeId)) newPerm = newPerm.withState("pw:off", pwNudge(block.location)); } catch { /* no pw:off */ }
    if (setRseed) {
      newPerm = newPerm.withState("pw:rseed", true);
    }
    // v1.2.19: independent log-top variant for log blocks (0-6, 7 Patrix variants)
    if (block.typeId.includes("_young") || block.typeId.includes("_mature") ||
        block.typeId.includes("_old") || block.typeId.includes("_elder")) {
      try {
        const topChoice = Math.floor(Math.random() * 7);
        newPerm = newPerm.withState("pw:top_variant", topChoice);
      } catch (e) {
        // pw:top_variant may not exist on this block — ignore
      }
    }
    block.setPermutation(newPerm);
  } catch (e) {
    // Silent: random feature placements may temporarily fail; not critical
  }
}

system.beforeEvents.startup.subscribe((ev) => {
  try {
    ev.blockComponentRegistry.registerCustomComponent("pw:randomize_variant", {
      onPlace: pwRandomizeVariant
    });
    log("[pw_variants] custom component pw:randomize_variant registered (onPlace only)");
  } catch (e) {
    logErr(`[pw_variants] failed to register custom component: ${e}`);
  }
});


// =========================================================================
// LEAF VARIANT SCANNER — v0.15.15
// =========================================================================
// Worldgen-placed leaves never fire onPlace, so they stay at default variant=0
// (uniformly V1/lean-east). To distribute all 6 variants evenly across naturally
// generated canopies, this scanner periodically inspects blocks near each player
// and randomizes any pw:*_leaves with pw:rseed=false. Once randomized, rseed is
// set to true and the block is skipped on subsequent scans (idempotent).
//
// Tuning rationale:
//   SCAN_INTERVAL=40 ticks (2 seconds): responsive without spamming the engine.
//   SCAN_RADIUS=12 horizontal / 8-down 16-up vertical: covers a typical canopy
//     above the player (trees grow up) plus 8 below for sapling-grown trees.
//   MAX_PER_TICK=80: caps work per cycle. A typical 1×1 tree canopy has ~50-200
//     leaves, so a tree's worth gets randomized in 1-3 cycles (~2-6 seconds).
//
// Performance note: scanning ~25×25×25=15,625 cells with getBlock + early-skip
// on non-pw blocks is cheap (memory-only reads). The expensive op is
// setPermutation, which we cap at MAX_PER_TICK to avoid lag spikes.
// =========================================================================
// v1.0.1 — Renamed from PW_LEAF_TYPES to PW_RANDOMIZE_TYPES + extended to include
// log tier blocks (young/mature/old/elder per species). Previously only leaves were
// scanned, which is why worldgen-placed log blocks all stayed at variant 0 (visible
// as "1 bark texture" in v1.0.0/v1.0.1 — the v1.0.1 bark randomization fix).
const PW_RANDOMIZE_TYPES = new Set([
  // Leaves
  "pw:oak_leaves", "pw:spruce_leaves", "pw:birch_leaves",
  "pw:jungle_leaves", "pw:dark_oak_leaves", "pw:pale_oak_leaves",
  "pw:acacia_leaves", "pw:mangrove_leaves", "pw:cherry_leaves",
  "pw:azalea_leaves", "pw:flowering_azalea_leaves",
  // Log tier blocks — species with full lifecycle (young/mature/old/elder)
  "pw:oak_young", "pw:oak_mature", "pw:oak_old", "pw:oak_elder",
  "pw:spruce_young", "pw:spruce_mature", "pw:spruce_old", "pw:spruce_elder",
  "pw:birch_young", "pw:birch_mature", "pw:birch_old",
  "pw:jungle_young", "pw:jungle_mature", "pw:jungle_old", "pw:jungle_elder",
  // Elder-only species
  "pw:dark_oak_elder", "pw:pale_oak_elder"
]);
// Backward-compat alias — some downstream code in this script may reference the old name
const PW_LEAF_TYPES = PW_RANDOMIZE_TYPES;

// =========================================================================
// v1.3.23 — Process A (trunk-association) constants
// =========================================================================
// New scanner architecture: a SECOND job that finds logs near the player
// and walks their connected canopies via the existing _treeCompletionBFS.
// Massively faster classification of close-range leaves because we don't
// have to iterate every cell in a 25×25×82 box looking for unflagged leaves —
// we just find a log (sparse) and follow it to all its leaves.
//
// Both jobs are watchdog-safe yielding generators with hard cell budgets.

const PW_TA_LOG_TYPES = new Set([
  // Vanilla overworld logs
  "minecraft:oak_log", "minecraft:stripped_oak_log",
  "minecraft:spruce_log", "minecraft:stripped_spruce_log",
  "minecraft:birch_log", "minecraft:stripped_birch_log",
  "minecraft:jungle_log", "minecraft:stripped_jungle_log",
  "minecraft:acacia_log", "minecraft:stripped_acacia_log",
  "minecraft:dark_oak_log", "minecraft:stripped_dark_oak_log",
  "minecraft:mangrove_log", "minecraft:stripped_mangrove_log",
  "minecraft:cherry_log", "minecraft:stripped_cherry_log",
  "minecraft:pale_oak_log", "minecraft:stripped_pale_oak_log",
  // Vanilla nether stems
  "minecraft:crimson_stem", "minecraft:stripped_crimson_stem",
  "minecraft:warped_stem", "minecraft:stripped_warped_stem",
  // pw: tier logs
  "pw:oak_young", "pw:oak_mature", "pw:oak_old", "pw:oak_elder",
  "pw:spruce_young", "pw:spruce_mature", "pw:spruce_old", "pw:spruce_elder",
  "pw:birch_young", "pw:birch_mature", "pw:birch_old",
  "pw:jungle_young", "pw:jungle_mature", "pw:jungle_old", "pw:jungle_elder",
  "pw:dark_oak_elder", "pw:pale_oak_elder",
]);

// v1.3.23: legacy compat constants — _forceKickScanner ignores these args
// (line 2468 comment confirms), but the call sites still pass them by name.
// Define here so script-load doesn't throw ReferenceError.
const PW_SCAN_VERT_DOWN = 0;
const PW_SCAN_VERT_UP = 42;

// Process A configuration
const PW_TA_INTERVAL = 30;
const PW_TA_RADIUS_XZ = 35;
const PW_TA_Y_RANGE = 70;
const PW_TA_CELLS_PER_YIELD = 400;    // v1.3.35 perf: was 3000 — smaller yield chunks let the sim thread breathe
// v1.3.41: TIME-SLICED YIELDS (PS5-join watchdog fix). Call-count budgets assume
// ~constant getBlock cost; a joining player's chunk-generation storm on the host
// multiplies per-call latency 10-100x, so a 400-call slice can exceed the 10s
// watchdog. Jobs now also yield when a slice exceeds PW_SLICE_MS wall-clock, and
// tree walks are deadline-boxed (aborted walks self-heal: unrolled leaves are
// re-walked on the next cycle).
const PW_SLICE_MS = 8;                 // max wall-clock ms per generator slice
const PW_TA_WALK_DEADLINE_MS = 40;     // max wall-clock ms per single tree walk
const PW_TA_MAX_TREES_PER_CYCLE = 3;
const PW_TA_BFS_BUDGET_PER_TREE = 300; // v1.3.35 perf: was 600 — fewer marks per tree per resumption

// =========================================================================
// v1.3.34 — Lazy shell-by-shell offset iterator (replaces precomputed lists)
// =========================================================================
// The old _buildOffsetList allocated ~932,000 {dx,dy,dz,cheb,eucSq} objects
// at module load (710K for Process A + 221K for Process B), pushing peak
// memory to 130+ MB and OOM-killing the script before it could finish loading.
//
// New design combines two strategies that support each other:
//
//   Layer C (interface): A generator yields offsets one at a time in near-
//     to-far order (Chebyshev shell ascending, Euclidean squared distance
//     ascending within shell). Zero allocation at module load; iteration
//     starts allocate-on-demand. Consumers iterate via for...of and may
//     break early.
//
//   Layer B (storage): Inside the generator, each shell is materialized
//     into preallocated Int16Array (dx, dy, dz) and Uint32Array (eucSq)
//     buffers reused across shells. ~14 bytes per entry instead of ~100.
//     Largest shell for Process A (cheb=35) is ~29,400 entries = ~412 KB.
//
// Combined peak memory during iteration: ~600 KB (one shell of typed
// buffers + sort index + scratch). Versus the old 130+ MB.
//
// Fallback (safety net): Strategy chosen up-front at iteration start. If
// TypedArray allocation throws (extremely unlikely in Bedrock JS but
// possible if budget exhausted), we degrade to a pure-object shell
// generator that has no precompute and yields a shared scratch object.
// Decision made before any yield so the consumer never sees duplicates.
//
// Consumer pattern:
//   for (const off of pwOffsetIterator(radiusXZ, yRange)) {
//     // off.dx, off.dy, off.dz, off.cheb, off.eucSq
//     // off is a SHARED scratch object — do not retain across iterations.
//     // Read fields immediately and assign to locals if you need them later.
//     if (someCondition) break;  // early exit fine
//   }

function* pwOffsetIterator(radiusXZ, yRange) {
  // Decide strategy up-front: try to allocate typed buffers. If that fails,
  // use pure-object path. This avoids mid-stream fallback (which would
  // duplicate or skip offsets).
  const xzDim = 2 * radiusXZ + 1;
  const yDim = 2 * yRange + 1;
  // Upper-bound the largest shell. The biggest shell is the surface of the
  // bounded box, which is at most 4*xzDim*yDim + 2*xzDim*xzDim cells. Add
  // 25% slack for safety.
  const maxShellSize = Math.ceil((4 * xzDim * yDim + 2 * xzDim * xzDim) * 1.25);

  let bufDX, bufDY, bufDZ, bufEucSq;
  let useTyped = true;
  try {
    bufDX = new Int16Array(maxShellSize);
    bufDY = new Int16Array(maxShellSize);
    bufDZ = new Int16Array(maxShellSize);
    bufEucSq = new Uint32Array(maxShellSize);
  } catch (e) {
    useTyped = false;
    try { console.warn(`[pw_offsets] typed buffer alloc failed (${e}) — falling back to pure generator`); } catch {}
  }

  if (useTyped) {
    yield* _pwOffsetIterator_typed(radiusXZ, yRange, bufDX, bufDY, bufDZ, bufEucSq);
  } else {
    yield* _pwOffsetIterator_pure(radiusXZ, yRange);
  }
}

// Layer B+C combined: shell-by-shell with TypedArray storage.
function* _pwOffsetIterator_typed(radiusXZ, yRange, bufDX, bufDY, bufDZ, bufEucSq) {
  const maxCheb = Math.max(radiusXZ, yRange);
  // Shared scratch object — mutated and yielded each step. Consumers must
  // read fields immediately and not retain references.
  const scratch = { dx: 0, dy: 0, dz: 0, cheb: 0, eucSq: 0 };

  // Shell 0 (origin)
  scratch.dx = 0; scratch.dy = 0; scratch.dz = 0; scratch.cheb = 0; scratch.eucSq = 0;
  yield scratch;

  for (let cheb = 1; cheb <= maxCheb; cheb++) {
    const xzLim = cheb < radiusXZ ? cheb : radiusXZ;
    const yLim = cheb < yRange ? cheb : yRange;

    // Enumerate cells in this shell into the typed buffers
    let n = 0;
    for (let dy = -yLim; dy <= yLim; dy++) {
      const ady = dy < 0 ? -dy : dy;
      for (let dx = -xzLim; dx <= xzLim; dx++) {
        const adx = dx < 0 ? -dx : dx;
        for (let dz = -xzLim; dz <= xzLim; dz++) {
          const adz = dz < 0 ? -dz : dz;
          // Manual max to avoid Math.max call overhead in tight loop
          let cMax = adx;
          if (ady > cMax) cMax = ady;
          if (adz > cMax) cMax = adz;
          if (cMax !== cheb) continue;
          bufDX[n] = dx;
          bufDY[n] = dy;
          bufDZ[n] = dz;
          bufEucSq[n] = dx*dx + dy*dy + dz*dz;
          n++;
        }
      }
    }

    if (n === 0) continue; // defensive: shouldn't happen for valid cheb in range

    // Build a plain index array and sort by eucSq ascending. We sort
    // indices rather than the typed arrays themselves because TypedArray
    // .sort with comparator is awkward and we'd need parallel reorder
    // anyway.
    const idx = new Array(n);
    for (let i = 0; i < n; i++) idx[i] = i;
    idx.sort((a, b) => bufEucSq[a] - bufEucSq[b]);

    // Yield in sorted order
    for (let i = 0; i < n; i++) {
      const k = idx[i];
      scratch.dx = bufDX[k];
      scratch.dy = bufDY[k];
      scratch.dz = bufDZ[k];
      scratch.cheb = cheb;
      scratch.eucSq = bufEucSq[k];
      yield scratch;
    }
  }
}

// Layer C only: pure-object fallback if TypedArray allocation failed.
// Per-shell object arrays (each shell is small, so this is still fine).
function* _pwOffsetIterator_pure(radiusXZ, yRange) {
  const maxCheb = Math.max(radiusXZ, yRange);

  // Shell 0
  yield { dx: 0, dy: 0, dz: 0, cheb: 0, eucSq: 0 };

  for (let cheb = 1; cheb <= maxCheb; cheb++) {
    const xzLim = cheb < radiusXZ ? cheb : radiusXZ;
    const yLim = cheb < yRange ? cheb : yRange;

    const shell = [];
    for (let dy = -yLim; dy <= yLim; dy++) {
      const ady = dy < 0 ? -dy : dy;
      for (let dx = -xzLim; dx <= xzLim; dx++) {
        const adx = dx < 0 ? -dx : dx;
        for (let dz = -xzLim; dz <= xzLim; dz++) {
          const adz = dz < 0 ? -dz : dz;
          let cMax = adx;
          if (ady > cMax) cMax = ady;
          if (adz > cMax) cMax = adz;
          if (cMax !== cheb) continue;
          shell.push({ dx, dy, dz, cheb, eucSq: dx*dx + dy*dy + dz*dz });
        }
      }
    }
    shell.sort((a, b) => a.eucSq - b.eucSq);
    for (let i = 0; i < shell.length; i++) yield shell[i];
  }
}

const _taStats = {
  cyclesRun: 0,
  totalLogsScanned: 0,
  totalTreesWalked: 0,
  totalLeavesMarkedByTreeAssoc: 0,
  lastFireTick: 0,
  _markerFFired: false,
};
let _taJobActive = false;

// v1.1.0 — Post-teleport cooldown for leaf scan (Phase 5)
// Tracks last position per player; if displacement > 32 blocks in one tick = teleport,
// skip leaf scans for COOLDOWN_TICKS to let chunks settle.
const _leafScanLastPos = new Map();
const _leafScanCooldown = new Map();
const TELEPORT_THRESHOLD_SQ = 32 * 32; // squared distance
const POST_TELEPORT_COOLDOWN = 60; // ticks (3 seconds at 20 tps)

function _isInTeleportCooldown(player, currentTick) {
  const cd = _leafScanCooldown.get(player.id);
  if (cd && currentTick < cd) return true;
  const last = _leafScanLastPos.get(player.id);
  const loc = player.location;
  if (last) {
    const dx = loc.x - last.x;
    const dy = loc.y - last.y;
    const dz = loc.z - last.z;
    if ((dx*dx + dy*dy + dz*dz) > TELEPORT_THRESHOLD_SQ) {
      _leafScanCooldown.set(player.id, currentTick + POST_TELEPORT_COOLDOWN);
      _leafScanLastPos.set(player.id, { x: loc.x, y: loc.y, z: loc.z });
      return true;
    }
  }
  _leafScanLastPos.set(player.id, { x: loc.x, y: loc.y, z: loc.z });
  return false;
}

// =========================================================================
// LEAF SCANNER + RANDOMIZER — v1.2.34 UNIFIED ARCHITECTURE
// =========================================================================
//
// Replaces: v1.2.31 variant scanner (LEAF_SCAN_*) + v1.2.31 section flag
// scanner (SECTION_SCAN_*) + portions of v1.2.29 leaf cascade.
//
// Design (per user spec):
//   1. ONE combined scanner: marks leaves with pw:section/pw:exposure/pw:section_rolled
//      and enqueues them for the randomizer. Does NOT pick variants directly.
//   2. SEPARATE randomizer: queue-fed, no scanning. Pulls from the scanner's queue
//      and applies pw:variant. Fires at +10 ticks every 4th scanner cycle (~410 ticks).
//   3. CHAINED VERTICAL EXTENSION: if scanner finds leaves in its 9-block-high initial
//      window, schedule chained scans at +25/+50/+75 ticks each going 9 blocks higher.
//      Chain stops when a window finds zero leaves.
//   4. MULTI-TRIGGER REDUNDANCY: scanner kicks via runInterval(100t) + playerBreakBlock
//      on any pw:* leaf + chunk-area entry + 600t heartbeat self-check.
//   5. DIAGNOSTICS: optional in-chat health pings every 400t (20s).
//
// State diagram for a single leaf (pw:*_leaves):
//   freshly_placed (worldgen):
//     pw:section_rolled = false (default)
//     pw:rseed = false (default)
//     pw:variant = 0 (default)
//   → scanner pass marks it:
//     pw:section_rolled = true
//     pw:section = 0/1/2 (bottom/middle/top)
//     pw:exposure = 0/1 (inner/outer)
//     pw:rseed = false (still — randomizer hasn't run yet)
//     (v1.3.36: applied-registry replaces the old _scanQueue)
//   → randomizer pass picks it from queue:
//     pw:variant = chosen variant from PW_LEAF_VARIANT_POOLS[section_exposure]
//     pw:rseed = true
//   → block-break of nearby leaf invalidates affected leaves:
//     pw:section_rolled = false (forces re-mark on next scan)
//     pw:rseed = false (forces re-randomize after re-mark)
//
// Idempotent: leaves with pw:section_rolled=true AND pw:rseed=true are skipped.
// Both flags must be true to skip; if either is false, the leaf gets re-processed.
// =========================================================================

// ---- Tunables (v1.2.42 retuned for faster mass coverage) ----
const PW_SCAN_INTERVAL = 22;             // v1.2.52: forward scanner cadence (1.1s @ 20 tps), coprime with reverse=39t, LCM=858t=42.9s
const PW_SCAN_RADIUS_XZ = 25;            // horizontal scan radius around player
const PW_SCAN_MAX_MARK_PER_CYCLE = 800;  // max marks per scanner cycle — was 120
const PW_RAND_CYCLE_DIVISOR = 1;         // randomizer fires every scanner cycle — was 4
const PW_RAND_OFFSET_TICKS = 5;          // randomizer fires +5t after scanner — was 10
const PW_RAND_MAX_DRAIN_PER_CYCLE = 1000;// max queue items consumed per randomizer cycle — was 200
const PW_HEARTBEAT_INTERVAL = 600;       // 30s — heartbeat self-check cadence
const PW_HEARTBEAT_STALE_THRESHOLD = 300; // 15s — if scanner hasn't fired in this many ticks, force-fire
const PW_BREAK_RADIUS = 4;               // blocks-around-broken-leaf to force-rescan
const PW_DIAGNOSTICS_ENABLED = false;    // toggle in-chat diagnostics; flip to true for debugging
// v1.3.206 TREE PROGRAM T5 SWITCH: false = the leaf scanner (Process A, phase-1, cascade, verify, heartbeat) never runs.
// Flipped to false in the build where every worldgen tree is a structure tree with baked final leaves (T2 complete).
// Old-chunk leaves: /scriptevent pw:leaf_finish [radius] assigns their look once (his F2 = b).
const PW_SCANNER_ON = false;   // T2 wired every species to templates (tools/tree_wire_t2.py)
const PW_DIAGNOSTICS_INTERVAL = 400;     // 20s ping cadence

// v1.2.51: Reverse-randomizer tunables — sets randomized leaves back to v0 in a
// radial shell beyond forward scan range, enabling far-distance render via opaque v0.
const PW_REVERSE_INTERVAL = 39;          // v1.2.52: reverse scanner cadence (1.95s @ 20 tps)
                                          // coprime with PW_SCAN_INTERVAL=22, LCM=858t≈42.9s
const PW_REVERSE_MIN_RADIUS = 50;        // inner radius — leaves below this distance untouched
const PW_REVERSE_MAX_RADIUS = 62;        // outer radius — leaves beyond this untouched
const PW_REVERSE_MIN_RADIUS_SQ = PW_REVERSE_MIN_RADIUS * PW_REVERSE_MIN_RADIUS;
const PW_REVERSE_MAX_RADIUS_SQ = PW_REVERSE_MAX_RADIUS * PW_REVERSE_MAX_RADIUS;
const PW_REVERSE_VERTICAL_RANGE = 35;    // ±Y blocks around player to scan
const PW_REVERSE_MAX_REVERTS_PER_CYCLE = 400;  // cap per-cycle work

// v1.2.42: Six layer scan pattern relative to player Y.
// Sequence: middle → down → up → lower → higher → highest (double-up at end).
// Each layer is 8 blocks tall (yLo to yHi inclusive). Layers overlap at boundaries.
const PW_LAYER_OFFSETS = [
  { yLo: 14, yHi: 21 },  // L1: baseline middle (y+14..y+21)
  { yLo:  7, yHi: 14 },  // L2: down 7 (y+7..y+14)
  { yLo: 21, yHi: 28 },  // L3: up 7 (y+21..y+28)
  { yLo:  0, yHi:  7 },  // L4: down 14 (y+0..y+7)
  { yLo: 28, yHi: 35 },  // L5: up 14 (y+28..y+35)
  { yLo: 35, yHi: 42 },  // L6: up 21 (y+35..y+42) DOUBLE-UP
];

// v1.2.42: Tree-completion BFS budget
// Bounds visited Set size (NOT just leaf count — includes non-leaf neighbors checked).
// 3000 handles canopies up to ~1500 leaves (custom pw_jungle_elder, mega spruce, etc).
const PW_BFS_MAX_LEAVES = 1500;          // v1.3.35 perf: was 3000 — caps worst-case SYNCHRONOUS getBlock walk per tree (walk is non-generator)

// v1.2.42: Third verification script
const PW_VERIFY_INTERVAL = 200;          // 10s
const PW_VERIFY_RADIUS_XZ = 30;
const PW_VERIFY_MAX_PER_CYCLE = 500;

// v1.2.42: Periodic stats logger
const PW_STATS_LOG_INTERVAL = 1200;      // v1.3.189: 60 s (was 5 s — it flooded the P0 content log); /scriptevent pw:stats off|on|now
let _statsEnabled = true;                 // v1.3.189: pw:stats off silences the periodic line (pw:stats now still prints one)
let _lastStatsLogTick = 0;

// ---- State ----
// _appliedRegistry (v1.3.36): posKey "x,y,z,dimId" → {x,y,z,dimId} for varied leaves
// Map preserves insertion order; oldest entries drained first.
// v1.3.36: _scanQueue REMOVED (leak; replaced by bounded _appliedRegistry).
const _scanStats = {
  lastFireTick: 0,
  lastMarkTick: 0,
  lastRandomTick: 0,
  totalMarked: 0,
  totalRandomized: 0,
  totalRevertedFar: 0,   // v1.3.36: far-band reverts (near-scan + reverter)
  totalForceKicks: 0,
  totalHeartbeatRecoveries: 0,
  cyclesRun: 0,
  // v1.2.42: per-species + per-variant counters
  perSpecies: {},        // typeId → count of marked
  perVariant: {},        // variant (1-6) → count of randomized
  _markerDFired: false,  // for MARKER-D one-shot guard
  _markerEFired: false,  // v1.2.54 MARKER-E one-shot guard
};
let _scanCycleCounter = 0;

// ---- detectSectionAndExposure (preserved verbatim from v1.2.31) ----
// Determine the canopy section (0/1/2) for a leaf at (x, y, z) within its dimension.
// Walk up and down to find the contiguous leaf column bounds, then compute relative Y.
// Returns int 0=bottom, 1=middle, 2=top.
//
// Bounded walk: cap at 32 blocks each direction (2× max canopy height) to avoid runaway
// reads if the dimension misbehaves. Beyond 32 we treat the column as unbounded and
// classify as middle (safe fallback).
function detectSectionAndExposure(dim, x, y, z, leafType) {
  const MAX_WALK = 32;
  // Walk up
  let canopyTop = y;
  for (let i = 1; i <= MAX_WALK; i++) {
    let above;
    try { above = dim.getBlock({ x, y: y + i, z }); } catch { break; }
    if (!above || above.typeId !== leafType) break;
    canopyTop = y + i;
  }
  // Walk down
  let canopyBottom = y;
  for (let i = 1; i <= MAX_WALK; i++) {
    let below;
    try { below = dim.getBlock({ x, y: y - i, z }); } catch { break; }
    if (!below || below.typeId !== leafType) break;
    canopyBottom = y - i;
  }
  
  const canopyHeight = canopyTop - canopyBottom + 1;
  let section;
  if (canopyHeight <= 1) {
    section = 1;
  } else {
    const relativeY = (y - canopyBottom) / (canopyHeight - 1);
    if (relativeY < 0.34) section = 0;
    else if (relativeY < 0.67) section = 1;
    else section = 2;
  }
  
  // Exposure: 6-face neighbor check + flagged-neighbor depth-1 detection.
  const offsets = [[1,0,0], [-1,0,0], [0,1,0], [0,-1,0], [0,0,1], [0,0,-1]];
  const leafNeighbors = [];
  let isEdge = false;
  for (const [dx, dy, dz] of offsets) {
    let nb;
    try { nb = dim.getBlock({ x: x + dx, y: y + dy, z: z + dz }); } catch { isEdge = true; break; }
    if (!nb) { isEdge = true; break; }
    const nid = nb.typeId;
    if (!nid.endsWith("_leaves") && !nid.endsWith("_wart_block")) {
      isEdge = true;
      break;
    }
    leafNeighbors.push(nb);
  }
  
  let exposure;
  if (isEdge) {
    exposure = 1;
  } else {
    let foundOuterNeighbor = false;
    for (const nb of leafNeighbors) {
      let nbRolled, nbExp;
      try { nbRolled = nb.permutation.getState("pw:section_rolled"); } catch { continue; }
      if (nbRolled !== true) continue;
      try { nbExp = nb.permutation.getState("pw:exposure"); } catch { continue; }
      if (nbExp === 1) {
        foundOuterNeighbor = true;
        break;
      }
    }
    exposure = foundOuterNeighbor ? 1 : 0;
  }
  
  return { section, exposure };
}

// ---- v1.2.42: Mark a single leaf and enqueue for randomizer ----
// Returns true if marked, false if skipped (already flagged or error).
function _markLeaf(dim, block, x, y, z) {
  try {
    const { section, exposure } = detectSectionAndExposure(dim, x, y, z, block.typeId);
    const newPerm = block.permutation
      .withState("pw:section", section)
      .withState("pw:exposure", exposure)
      .withState("pw:section_rolled", true)
      .withState("pw:rseed", false);
    block.setPermutation(newPerm);
    _scanStats.totalMarked++;
    _scanStats.lastMarkTick = system.currentTick;
    // Per-species counter (v1.2.42)
    const tid = block.typeId;
    if (!_scanStats.perSpecies[tid]) _scanStats.perSpecies[tid] = 0;
    _scanStats.perSpecies[tid]++;
    // v1.3.36: legacy randomizer-queue enqueue REMOVED (consumer orphaned in
    // v1.2.54 -> unbounded Map leak + rnd=0 stats lie). Application lives in the
    // phase-1 distance toggle; the applied-registry tracks varied leaves.
    return true;
  } catch (e) { return false; }
}

// ---- v1.2.42: Tree-completion BFS ----
// When a leaf is found unflagged, flood-fill through 6-face neighbors of same species,
// marking each one. This guarantees an entire connected canopy gets processed before
// the box scan moves to the next cell.
//
// Caps at PW_BFS_MAX_LEAVES (~800) to prevent runaway on bug or insane megastructures.
// Returns count of leaves marked via BFS (NOT counting the seed leaf which was already marked).
function _treeCompletionBFS(dim, leafType, sx, sy, sz, budget, deadlineMs = 0) {
  const visited = new Set();
  const startKey = `${sx},${sy},${sz}`;
  visited.add(startKey);  // Mark seed as visited (already processed by caller)
  const frontier = [[sx, sy, sz]];
  const offsets = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
  let marked = 0;
  while (frontier.length > 0 && marked < budget && visited.size < PW_BFS_MAX_LEAVES) {
    if (deadlineMs && Date.now() > deadlineMs) break;  // v1.3.41 deadline-box: partial walk self-heals next cycle
    const [x, y, z] = frontier.shift();
    for (const [dx, dy, dz] of offsets) {
      const nx = x + dx, ny = y + dy, nz = z + dz;
      const key = `${nx},${ny},${nz}`;
      if (visited.has(key)) continue;
      visited.add(key);
      let nb;
      try { nb = dim.getBlock({ x: nx, y: ny, z: nz }); } catch { continue; }
      if (!nb) continue;
      // Only walk through same-species leaves
      if (nb.typeId !== leafType) continue;
      let alreadyFlagged;
      try { alreadyFlagged = nb.permutation.getState("pw:section_rolled"); } catch { continue; }
      if (alreadyFlagged === true) {
        // Still walk through for BFS reachability, but don't re-mark
        frontier.push([nx, ny, nz]);
        continue;
      }
      // Mark this leaf
      if (_markLeaf(dim, nb, nx, ny, nz)) {
        marked++;
        frontier.push([nx, ny, nz]);
      }
      if (marked >= budget) break;
    }
  }
  return { marked, visited: visited.size };
}

// ---- v1.2.42: Core scan routine — 6-layer player-relative pattern with tree-BFS ----
// Scans 6 sequential layers above player in order:
//   L1: y+14..y+21 (baseline)
//   L2: y+7..y+14  (down)
//   L3: y+21..y+28 (up)
//   L4: y+0..y+7   (lower)
//   L5: y+28..y+35 (higher)
//   L6: y+35..y+42 (highest, double-up)
// For each unflagged leaf found, runs tree-completion BFS to flood-fill the whole tree.
// Shares mark budget across all 6 layers; stops when budget exhausted.
//
// Returns: { leavesFound, leavesMarked, treesBfsd }
function _runLayeredScan(dim, px, py, pz, marksRemainingBudget) {
  let leavesFound = 0;
  let leavesMarked = 0;
  let treesBfsd = 0;
  for (let li = 0; li < PW_LAYER_OFFSETS.length; li++) {
    if (leavesMarked >= marksRemainingBudget) break;
    const layer = PW_LAYER_OFFSETS[li];
    const yLo = py + layer.yLo;
    const yHi = py + layer.yHi;
    for (let y = yLo; y <= yHi; y++) {
      if (leavesMarked >= marksRemainingBudget) break;
      for (let dx = -PW_SCAN_RADIUS_XZ; dx <= PW_SCAN_RADIUS_XZ; dx++) {
        if (leavesMarked >= marksRemainingBudget) break;
        for (let dz = -PW_SCAN_RADIUS_XZ; dz <= PW_SCAN_RADIUS_XZ; dz++) {
          if (leavesMarked >= marksRemainingBudget) break;
          const x = px + dx, z = pz + dz;
          let block;
          try { block = dim.getBlock({ x, y, z }); } catch { continue; }
          if (!block) continue;
          if (!PW_LEAF_TYPES.has(block.typeId)) continue;
          leavesFound++;
          let alreadyFlagged;
          try { alreadyFlagged = block.permutation.getState("pw:section_rolled"); } catch { continue; }
          if (alreadyFlagged === true) continue;
          // Mark this leaf
          if (_markLeaf(dim, block, x, y, z)) {
            leavesMarked++;
            // Tree-completion BFS — flood-fill the connected canopy
            const budgetRemaining = marksRemainingBudget - leavesMarked;
            const bfsResult = _treeCompletionBFS(dim, block.typeId, x, y, z, budgetRemaining);
            leavesMarked += bfsResult.marked;
            treesBfsd++;
          }
        }
      }
    }
  }
  return { leavesFound, leavesMarked, treesBfsd };
}

// Backward-compat alias: existing callsites use _runScanBox (force kicks etc.)
function _runScanBox(dim, cx, cy, cz, vertDown, vertUp, budget) {
  // v1.2.42: redirect to layered scan, treat (cx,cy,cz) as player position.
  // Old vertDown/vertUp args ignored — layered scan covers full vertical span.
  return _runLayeredScan(dim, cx, cy, cz, budget);
}

// ---- v1.2.42: Vertical extensions removed ----
// The new 6-layer scan covers all heights y+0..y+42 above player in one pass,
// making chained vertical extensions unnecessary. Kept as no-op stub for legacy
// callers (none currently exist after v1.2.42).
function _scheduleVerticalExtensions(dim, centerX, baseY, centerZ, chainDepth) {
  // no-op
}

// ---- Main scanner interval (v1.2.54 PHASE-1: classify-once + distance-toggle) ----
// REPLACES the v1.2.42 continuous layered re-scan + per-cycle BFS + randomizer
// churn + reverse re-classification. Those were the primary lag/crash source
// (1.1M-cell synchronous loops, watchdog hangs in dense foliage).
//
// New model (D-098..D-101):
//  1. CLASSIFY-ONCE: any leaf with pw:section_rolled=false is classified EXACTLY
//     once (section + exposure via the existing detectSectionAndExposure walk),
//     flags written, pw:section_rolled=true. A rolled leaf is NEVER recomputed.
//     Its (section,exposure) is its permanent "zone".
//  2. DISTANCE-TOGGLE with hysteresis: a classified leaf beyond
//     PW_FAR_OUTER blocks -> pw:variant=0 (opaque far-render, important).
//     Within PW_FAR_INNER -> pw:variant = pickVariantForBlock() from the FROZEN
//     flags. Band [INNER,OUTER] = no change (no boundary strobing).
// Both run as yielding generators with a hard per-cycle cell budget, kicked on
// the original cadence with a single-job guard — cannot trip the 10s watchdog.
// All heavy helpers (detectSectionAndExposure, pickVariantForBlock) reused as-is.

const PW_FAR_INNER = 64;                 // within this -> show detailed variant
const PW_FAR_OUTER = 72;                 // beyond this -> revert to v0 (far opaque)
const PW_FAR_INNER_SQ = PW_FAR_INNER * PW_FAR_INNER;
const PW_FAR_OUTER_SQ = PW_FAR_OUTER * PW_FAR_OUTER;
const PW_P1_CELLS_PER_YIELD = 400;       // v1.3.35 perf: was 2600 — phase-1 classify yields far more often
const PW_P1_SCAN_RADIUS_XZ = PW_SCAN_RADIUS_XZ;   // reuse existing 25
const PW_P1_Y_LO = -40;
// --- v1.3.36: O(applied) far-reverter ---
// Phase-1 iterator reaches only PW_P1_SCAN_RADIUS_XZ (25), so the >PW_FAR_OUTER (68)
// revert branch was UNREACHABLE dead code: hysteresis LOD never functioned. Instead of
// scanning the 25..68 shell (TPS-hostile), the reverter walks ONLY positions that were
// actually varied (applied-registry), throttled, on a 39t cadence (coprime w/ 22t scan).
const PW_APPLIED_MAX = 30000;            // registry hard cap (memory bound)
const PW_REVERT_INTERVAL = 39;           // ticks — coprime with PW_SCAN_INTERVAL=22
const PW_REVERT_MAX_PER_CYCLE = 300;     // permutation-write budget per pass
const _appliedRegistry = new Map();      // "x,y,z,dimId" -> {x,y,z,dimId}                  // v1.3.8: scan BELOW player too (valley/downslope tree canopies were never classified -> stayed v0 square)
const PW_P1_Y_HI = 42;
let _p1JobActive = false;

// =========================================================================
// v1.3.23 — Process A: TRUNK-ASSOCIATION JOB
// =========================================================================
// Finds logs near the player (priority-near order), walks their connected
// canopies via _treeCompletionBFS. Trees walked already (= adjacent leaves
// already have pw:section_rolled=true) are skipped cheaply.
// =========================================================================

function _findAdjacentLeaf(dim, lx, ly, lz) {
  const offs = [[0,1,0],[0,-1,0],[1,0,0],[-1,0,0],[0,0,1],[0,0,-1]];
  for (const [dx, dy, dz] of offs) {
    let nb;
    try { nb = dim.getBlock({ x: lx+dx, y: ly+dy, z: lz+dz }); } catch { continue; }
    if (!nb) continue;
    if (!nb.typeId.endsWith("_leaves")) continue;
    return { block: nb, x: lx+dx, y: ly+dy, z: lz+dz };
  }
  return null;
}

function _findTreeTop(dim, sx, sy, sz, maxWalk) {
  let topY = sy;
  for (let i = 1; i <= maxWalk; i++) {
    let nb;
    try { nb = dim.getBlock({ x: sx, y: sy + i, z: sz }); } catch { break; }
    if (!nb) break;
    if (!PW_TA_LOG_TYPES.has(nb.typeId)) break;
    topY = sy + i;
  }
  return { x: sx, y: topY, z: sz };
}

function _walkTreeFromLog(dim, lx, ly, lz, budget, deadlineMs = 0) {
  const top = _findTreeTop(dim, lx, ly, lz, 32);
  // v1.3.147 OAK FIX (witnessed: logs counted, trees=0, taLeaves=0 in oak forests while birch and
  // spruce walked fine): our nineteen custom oak features shape crowns OFFSET from the trunk tip, so
  // the strict six-adjacent test at the topmost log found nothing and every oak died at this door.
  // Tolerant search: tip, then a radius-2 shell around it, then up to three logs down repeating both.
  let adj = _findAdjacentLeaf(dim, top.x, top.y, top.z);
  if (!adj) {
    outer:
    for (let step = 0; step <= 3 && !adj; step++) {
      const ty = top.y - step;
      for (let dy = 2; dy >= -1; dy--) {
        for (let dx = -2; dx <= 2; dx++) {
          for (let dz = -2; dz <= 2; dz++) {
            if (dx === 0 && dy === 0 && dz === 0) continue;
            let b2; try { b2 = dim.getBlock({ x: top.x + dx, y: ty + dy, z: top.z + dz }); } catch { continue; }
            if (b2 && typeof b2.typeId === "string" && b2.typeId.indexOf("leaves") >= 0) { adj = { block: b2, x: top.x + dx, y: ty + dy, z: top.z + dz }; break outer; }
          }
        }
      }
    }
  }
  if (!adj) return 0;
  let rolled;
  try { rolled = adj.block.permutation.getState("pw:section_rolled"); } catch { return 0; }
  if (rolled === true) return 0;
  let marked = 0;
  if (_markLeaf(dim, adj.block, adj.x, adj.y, adj.z)) {
    marked = 1;
  } else {
    return 0;
  }
  try {
    const bfs = _treeCompletionBFS(dim, adj.block.typeId, adj.x, adj.y, adj.z, budget - 1, deadlineMs);
    marked += bfs.marked;
  } catch {}
  return marked;
}

let _pwJobRotor = 0;  // v1.3.49: round-robin player start order (multi-player fairness)
function _pwRotatedPlayers() {
  const ps = world.getPlayers();
  if (ps.length <= 1) return ps;
  const r = (_pwJobRotor++) % ps.length;
  return ps.slice(r).concat(ps.slice(0, r));
}

function* _treeAssociationJob() {
  if (!PW_SCANNER_ON) return;
  _taStats.cyclesRun++;
  if (_taStats.cyclesRun === 1) {
    try { console.warn(`[BIGCANOPY-DIAG] MARKER-F v${PW_BUILD} ${PW_BOOT_ID} Process A trunk-association started`); } catch {}
  }
  let _cells = 0;
  let _slice = Date.now();  // v1.3.41 time-sliced yields

  for (const player of _pwRotatedPlayers()) {
    if (_isInTeleportCooldown(player, system.currentTick)) continue;
    let _treesThisCycle = 0;  // v1.3.49: PER-PLAYER tree budget — shared cap starved
                              // every player after the first (witnessed: PS5 player
                              // got zero canopy transitions while host was in forest)
    const dim = player.dimension;
    const px = Math.floor(player.location.x);
    const py = Math.floor(player.location.y);
    const pz = Math.floor(player.location.z);

    try {
      // v1.3.34: replaced precomputed PW_TA_OFFSETS array (710K objects = OOM)
      // with lazy shell-by-shell generator. Behaviorally identical iteration
      // order (Chebyshev ascending, eucSq ascending within shell).
      for (const off of pwOffsetIterator(PW_TA_RADIUS_XZ, PW_TA_Y_RANGE)) {
        if (_treesThisCycle >= ((system.currentTick - _forgeBeat > 200) ? PW_TA_MAX_TREES_PER_CYCLE * 3 : PW_TA_MAX_TREES_PER_CYCLE)) break; // DORMANT-BOOST v1.3.153: 3x tree walking while the SlabForge key is out
        if (++_cells >= PW_TA_CELLS_PER_YIELD || (Date.now() - _slice) >= PW_SLICE_MS) { _cells = 0; yield; _slice = Date.now(); }
        const x = px + off.dx, y = py + off.dy, z = pz + off.dz;
        let block;
        try { block = dim.getBlock({ x, y, z }); } catch { continue; }
        if (!block) continue;
        if (!PW_TA_LOG_TYPES.has(block.typeId)) continue;
        _taStats.totalLogsScanned++;
        const markedNow = _walkTreeFromLog(dim, x, y, z, PW_TA_BFS_BUDGET_PER_TREE, Date.now() + PW_TA_WALK_DEADLINE_MS);
        if (markedNow > 0) {
          _treesThisCycle++;
          _taStats.totalTreesWalked++;
          _taStats.totalLeavesMarkedByTreeAssoc += markedNow;
          if (!_taStats._markerFFired) {
            _taStats._markerFFired = true;
            try { console.warn(`[BIGCANOPY-DIAG] MARKER-G v${PW_BUILD} ${PW_BOOT_ID} Process A first tree walked: ${markedNow} leaves at (${x},${y},${z})`); } catch {}
          }
          yield;
        }
      }
    } catch (e) { logErr(`[pw_ta] err: ${e}`); }
  }
  _taStats.lastFireTick = system.currentTick;
  _taJobActive = false;
}

system.runInterval(() => {
  if (_taJobActive) return;
  _taJobActive = true;
  try {
    system.runJob(_treeAssociationJob());
  } catch (e) {
    _taJobActive = false;
    try { logErr(`[pw_ta] job-kick err: ${e}`); } catch {}
  }
}, PW_TA_INTERVAL);

function _kickTreeAssociationNow() {
  if (_taJobActive) return;
  _taJobActive = true;
  try {
    system.runJob(_treeAssociationJob());
  } catch (e) {
    _taJobActive = false;
    try { logErr(`[pw_ta] event-kick err: ${e}`); } catch {}
  }
}

function* _phase1ScanJob() {
  if (!PW_SCANNER_ON) return;
  let _slice = Date.now();  // v1.3.41 time-sliced yields
  _scanStats.cyclesRun++;
  if (_scanStats.cyclesRun === 1) {
    try { console.warn(`[BIGCANOPY-DIAG] MARKER-C v${PW_BUILD} ${PW_BOOT_ID} phase-1 classify+toggle started`); } catch {}
  }
  let _cells = 0;

  for (const player of _pwRotatedPlayers()) {  // v1.3.49: fair start order
    if (_isInTeleportCooldown(player, system.currentTick)) continue;
    const dim = player.dimension;
    const px = Math.floor(player.location.x);
    const py = Math.floor(player.location.y);
    const pz = Math.floor(player.location.z);

    try {
      // v1.3.34: replaced precomputed PW_P1_OFFSETS_NEAR array (221K objects)
      // with lazy shell-by-shell generator. Iteration order preserved
      // (Chebyshev ascending, Euclidean sub-ordering — cells nearest the
      // player processed first, same as before). This is the fix for
      // "leaves don't flag fast enough when I walk into a forest."
      for (const off of pwOffsetIterator(PW_P1_SCAN_RADIUS_XZ, PW_P1_Y_HI)) {
        if (++_cells >= PW_P1_CELLS_PER_YIELD || (Date.now() - _slice) >= PW_SLICE_MS) { _cells = 0; yield; _slice = Date.now(); }
        const dx = off.dx, dy = off.dy, dz = off.dz;
        // Respect legacy P1 Y range; generator's yRange is symmetric so the
        // PW_P1_Y_LO guard is still required for the negative end.
        if (dy < PW_P1_Y_LO || dy > PW_P1_Y_HI) continue;
        const y = py + dy;
        const x = px + dx, z = pz + dz;
        // Capture eucSq into a local before any yield/await because off is
        // a shared scratch object that gets mutated on each generator step.
        const offEucSq = off.eucSq;

        let block;
        try { block = dim.getBlock({ x, y, z }); } catch { continue; }
        if (!block) continue;
        if (!PW_LEAF_TYPES.has(block.typeId)) continue;

        // --- 1. CLASSIFY ONCE (permanent) ---
        // Note: Process A (trunk-association) handles MOST classification now.
        // This path remains as a safety net for leaves Process A missed.
        let rolled;
        try { rolled = block.permutation.getState("pw:section_rolled"); } catch { continue; }
        if (rolled !== true) {
          try {
            if (_markLeaf(dim, block, x, y, z)) {
              if (!_scanStats._markerDFired) {
                _scanStats._markerDFired = true;
                try { console.warn(`[BIGCANOPY-DIAG] MARKER-D v${PW_BUILD} ${PW_BOOT_ID} first leaf classified at (${x},${y},${z})`); } catch {}
              }
            }
          } catch {}
          try { block = dim.getBlock({ x, y, z }); } catch { continue; }
          if (!block) continue;
          try { rolled = block.permutation.getState("pw:section_rolled"); } catch { continue; }
          if (rolled !== true) continue;
        }

        // --- 2. THE LOOK, ONCE (v1.3.196) ---
        // pw:rseed = 'look set'. The look comes from the position + the wood (pwLeafLook), so a re-pick gives the same answer;
        // the far swap is the game's own (alpha_test_to_opaque, L-FAR-1): no distance branch, no applied-registry.
        let rseed;
        try { rseed = block.permutation.getState("pw:rseed"); } catch { continue; }
        if (rseed !== true) {
          let target = 0;
          try { target = pickVariantForBlock(block); } catch { target = 0; }
          try {
            block.setPermutation(block.permutation.withState("pw:variant", target).withState("pw:rseed", true).withState("pw:off", pwNudge(block.location)));
            _scanStats.totalRandomized++;
            _scanStats.lastRandomTick = system.currentTick;
            if (!_scanStats.perVariant[target]) _scanStats.perVariant[target] = 0;
            _scanStats.perVariant[target]++;
            if (!_scanStats._markerEFired) {
              _scanStats._markerEFired = true;
              try { console.warn(`[BIGCANOPY-DIAG] MARKER-E v${PW_BUILD} ${PW_BOOT_ID} first leaf look -> variant=${target} at (${x},${y},${z})`); } catch {}
            }
          } catch {}
        }
      }
    } catch (e) { logErr(`[pw_p1] err: ${e}`); }
  }

  _scanStats.lastFireTick = system.currentTick;
  _p1JobActive = false;
}

system.runInterval(() => {
  if (_p1JobActive) return;
  _p1JobActive = true;
  try {
    system.runJob(_phase1ScanJob());
  } catch (e) {
    _p1JobActive = false;
    try { logErr(`[pw_p1] job-kick err: ${e}`); } catch {}
  }
}, PW_SCAN_INTERVAL);

// v1.3.198: the relook sweep (v1.3.197) is removed — his p16 ruling: every tree from now on is a new tree.

// =========================================================================
// v1.2.51: REVERSE-RANDOMIZER
// =========================================================================
// Purpose: enable far-distance leaf rendering. Custom blocks using alpha_test
// render method are "near" blocks (engine cuts them at ~half max render distance,
// roughly 70 blocks). v0 was changed to render_method=opaque in v1.2.51 making
// it a "far" block (full render distance). But v1-v6 randomized leaves stay
// alpha_test and disappear past ~70 blocks.
//
// The reverse-randomizer addresses this by reverting any randomized leaf in the
// 50-62 block radial shell back to pw:variant=0 AND clearing its pw:section_rolled
// flag. This means:
//   - When player walks AWAY from trees, reverse-randomizer fires and swaps
//     v1-v6 → v0 in the transition band. Those leaves become "far" blocks again
//     and remain visible past 70 blocks.
//   - When player walks BACK toward those trees, the cleared section_rolled flag
//     allows the forward scanner to re-mark + re-randomize, giving fresh detail
//     in the close-range zone.
//
// Cadence: PW_REVERSE_INTERVAL = 27t (1.35s), coprime with forward's 38t (1.9s).
// LCM 51.3s — they only coincide once per 51.3 seconds.
// =========================================================================

const _reverseStats = {
  cyclesRun: 0,
  totalReverted: 0,
  lastReverted: 0,
  lastFireTick: 0,
  _markerFired: false,
};

function _isLeafPwBlock(typeId) {
  return typeId && typeId.startsWith("pw:") && typeId.endsWith("_leaves");
}

// v1.2.54: REVERSE-RANDOMIZER REMOVED. Phase-1 distance-toggle in the
// main scan job now handles v0<->variant by distance with hysteresis;
// the old reverse re-revert/re-classify churn is obsolete & was a
// primary lag/crash source. (No-op retained for structural clarity.)

// ---- v1.3.36: far-reverter — walks the applied-registry, reverting leaves ----
// now beyond PW_FAR_OUTER of EVERY player back to v0 (far LOD). Hysteresis: entries
// within PW_FAR_OUTER of any player are kept; the near branch handles <INNER
// re-application; the [INNER,OUTER] band never strobes.
system.runInterval(() => {
  if (_appliedRegistry.size === 0) return;
  const players = world.getPlayers();
  if (players.length === 0) return;
  let processed = 0;
  for (const [key, e] of _appliedRegistry) {
    if (e.dormant) continue;
    if (processed >= PW_REVERT_MAX_PER_CYCLE) break;
    processed++;
    let minSq = Infinity;
    for (const pl of players) {
      if (pl.dimension.id !== e.dimId) continue;
      const dx = pl.location.x - e.x, dy = pl.location.y - e.y, dz = pl.location.z - e.z;
      const d = dx*dx + dy*dy + dz*dz;
      if (d < minSq) minSq = d;
    }
    if (minSq <= PW_FAR_OUTER_SQ) continue;   // still near someone (or hysteresis band) — keep
    let dim, block;
    try { dim = world.getDimension(e.dimId); block = dim.getBlock({ x: e.x, y: e.y, z: e.z }); }
    catch { _appliedRegistry.delete(key); continue; }
    if (!block || !PW_LEAF_TYPES.has(block.typeId)) { _appliedRegistry.delete(key); continue; }
    try {
      const v = block.permutation.getState("pw:variant");
      if (v !== 0) {
        block.setPermutation(block.permutation.withState("pw:variant", 0));
        _scanStats.totalRevertedFar++;
      }
      e.dormant = true;
    } catch { _appliedRegistry.delete(key); }
  }
}, PW_REVERT_INTERVAL);

// ---- HOTFIX-2 (v1.3.59): registry re-applicator — restores stored variants for ----
// dormant entries when a player returns within PW_FAR_INNER. No re-scan, no re-roll:
// trees keep their identity across visits (V2 persistence, delivered early).
const PW_REAPPLY_INTERVAL = 17;          // coprime with 22t scan & 39t reverter
const PW_REAPPLY_MAX_PER_CYCLE = 300;
system.runInterval(() => {
  if (_appliedRegistry.size === 0) return;
  const players = world.getPlayers();
  if (players.length === 0) return;
  let done = 0;
  for (const [key, e] of _appliedRegistry) {
    if (!e.dormant) continue;
    if (done >= PW_REAPPLY_MAX_PER_CYCLE) break;
    let minSq = Infinity;
    for (const pl of players) {
      if (pl.dimension.id !== e.dimId) continue;
      const dx = pl.location.x - e.x, dy = pl.location.y - e.y, dz = pl.location.z - e.z;
      const d = dx*dx + dy*dy + dz*dz;
      if (d < minSq) minSq = d;
    }
    if (minSq >= PW_FAR_INNER_SQ) continue;
    done++;
    let dim, block;
    try { dim = world.getDimension(e.dimId); block = dim.getBlock({ x: e.x, y: e.y, z: e.z }); }
    catch { _appliedRegistry.delete(key); continue; }
    if (!block || !PW_LEAF_TYPES.has(block.typeId)) { _appliedRegistry.delete(key); continue; }
    try {
      if (block.permutation.getState("pw:variant") === 0 && e.v) {
        block.setPermutation(block.permutation.withState("pw:variant", e.v));
        _scanStats.totalReapplied = (_scanStats.totalReapplied || 0) + 1;
      }
      e.dormant = false;
    } catch {}
  }
}, PW_REAPPLY_INTERVAL);

// ---- Multi-trigger redundancy ----
// Trigger 1: playerBreakBlock on any pw:* leaf forces a re-scan around the broken position
//            AND flags 6 face-neighbors' section_rolled=false (so re-marked next scan).
const _pendingCascades = new Set();  // key: "x,y,z,dimensionId" — for break-cascade re-flagging
const CASCADE_FLUSH_INTERVAL = 4;
const CASCADE_MAX_PER_TICK = 50;

function _enqueueCascade(loc, dimId) {
  if (!PW_SCANNER_ON) return;
  _pendingCascades.add(`${loc.x},${loc.y},${loc.z},${dimId}`);
}

function _forceKickScanner(dim, x, y, z, vertDown, vertUp) {
  // v1.2.54 PHASE-1: heavy _runScanBox/_runLayeredScan path REMOVED (was the
  // lag/crash source). The Phase-1 scan job already classifies+toggles a bounded
  // area on its own cadence; break/explosion cascades clear pw:section_rolled on
  // affected neighbors so they re-classify ONCE on the next pass. Force-kick now
  // only clears a stuck job guard so recovery is immediate.
  _scanStats.totalForceKicks++;
  if (_p1JobActive) {
    // If a prior job somehow stalled, releasing the guard lets the next
    // interval re-kick it. (Bounded yielding generator cannot hang the watchdog.)
    _p1JobActive = false;
  }
}

world.afterEvents.playerBreakBlock.subscribe((ev) => {
  try {
    const id = ev.brokenBlockPermutation?.type?.id;
    if (!id) return;
    const isLeafB = id.endsWith("_leaves") && PW_LEAF_TYPES.has(id);
    if (!isLeafB && !pwIsWood(id)) return;   // v1.3.197: a broken LOG re-looks the leaves beside it
    // Enqueue cascade for re-flagging of inner-neighbor leaves
    _enqueueCascade(ev.block.location, ev.dimension.id);
    // Also force-kick scanner for surrounding 4-block cube: catches any leaves that may have
    // been missed AND ensures scanner is alive after this user action.
    _forceKickScanner(ev.dimension, ev.block.location.x, ev.block.location.y, ev.block.location.z, PW_BREAK_RADIUS, PW_BREAK_RADIUS);
  } catch {}
});

// Trigger 2: explosion event — same cascade re-flag
world.afterEvents.explosion.subscribe((ev) => {
  try {
    const blocks = ev.getImpactedBlocks();
    const dimId = ev.dimension.id;
    for (const block of blocks) {
      _enqueueCascade(block.location, dimId);
    }
  } catch {}
});

// Trigger 3: player spawn → kick scanner once around them
world.afterEvents.playerSpawn.subscribe((ev) => {
  try {
    // v1.3.23: kick Process A on EVERY spawn (respawn-after-death covered);
    // Process B kick stays initialSpawn-only to match prior behavior.
    _kickTreeAssociationNow();
    if (ev.initialSpawn) {
      const player = ev.player;
      const loc = player.location;
      _forceKickScanner(player.dimension, Math.floor(loc.x), Math.floor(loc.y), Math.floor(loc.z), PW_SCAN_VERT_DOWN, PW_SCAN_VERT_UP);
    }
  } catch {}
});

// v1.3.23: Process A on world join (catches existing-world reload)
world.afterEvents.playerJoin.subscribe(() => {
  try { _kickTreeAssociationNow(); } catch {}
});

// v1.3.23: Process A on dimension change (Overworld <-> Nether <-> End)
world.afterEvents.playerDimensionChange.subscribe(() => {
  try { _kickTreeAssociationNow(); } catch {}
});

// ---- Cascade flush — re-flag 6 face-neighbors of recently-broken leaves ----
// Resets their pw:section_rolled=false so the next scanner pass re-marks them.
// This catches the case where breaking an outer leaf exposed an inner neighbor.
system.runInterval(() => {
  if (_pendingCascades.size === 0) return;
  const offsets = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
  let processed = 0;
  for (const key of _pendingCascades) {
    if (processed >= CASCADE_MAX_PER_TICK) break;
    const parts = key.split(",");
    const x = parseInt(parts[0], 10);
    const y = parseInt(parts[1], 10);
    const z = parseInt(parts[2], 10);
    const dimId = parts.slice(3).join(",");
    let dim;
    try { dim = world.getDimension(dimId); }
    catch { _pendingCascades.delete(key); processed++; continue; }
    for (const [dx, dy, dz] of offsets) {
      let nb;
      try { nb = dim.getBlock({ x: x + dx, y: y + dy, z: z + dz }); }
      catch { continue; }
      if (!nb) continue;
      if (!PW_LEAF_TYPES.has(nb.typeId)) continue;
      try {
        // Reset BOTH flags so scanner re-marks AND randomizer re-rolls
        nb.setPermutation(nb.permutation
          .withState("pw:section_rolled", false)
          .withState("pw:rseed", false));
      } catch {}
    }
    _pendingCascades.delete(key);
    processed++;
  }
}, CASCADE_FLUSH_INTERVAL);

// ---- Heartbeat self-check ----
// Every 600t (30s), verify scanner has fired recently. If not, force-fire one cycle for each player.
// Verify randomizer has drained recently (or queue is empty). If queue is non-empty AND randomizer
// hasn't drained in 600t, force-drain.
system.runInterval(() => {
  if (!PW_SCANNER_ON) return;
  const now = system.currentTick;
  // Scanner staleness check
  if (now - _scanStats.lastFireTick > PW_HEARTBEAT_STALE_THRESHOLD) {
    _scanStats.totalHeartbeatRecoveries++;
    for (const player of world.getPlayers()) {
      try {
        const dim = player.dimension;
        const loc = player.location;
        _forceKickScanner(dim, Math.floor(loc.x), Math.floor(loc.y), Math.floor(loc.z), PW_SCAN_VERT_DOWN, PW_SCAN_VERT_UP);
      } catch {}
    }
  }
  // v1.2.54 PHASE-1: no separate randomizer queue (classify+toggle is inline
  // in _phase1ScanJob). Old _drainRandomizerQueue staleness recovery removed.
}, PW_HEARTBEAT_INTERVAL);

// ---- Diagnostics chat ping (toggleable) ----
system.runInterval(() => {
  if (!PW_DIAGNOSTICS_ENABLED) return;
  try {
    const now = system.currentTick;
    const scanAge = now - _scanStats.lastFireTick;
    const markAge = _scanStats.lastMarkTick > 0 ? now - _scanStats.lastMarkTick : -1;
    const randAge = _scanStats.lastRandomTick > 0 ? now - _scanStats.lastRandomTick : -1;
    let scanStatus = "OK";
    if (scanAge > PW_HEARTBEAT_STALE_THRESHOLD) scanStatus = "WARN";
    let randStatus = "OK";
    if (_appliedRegistry.size >= PW_APPLIED_MAX) randStatus = "ALERT";      // registry cap saturated
    else if (_appliedRegistry.size > 0 && randAge > 600) randStatus = "WARN";
    world.sendMessage(
      `§a[pw:scan]§f tick=${now} last_fire=${scanAge}t marked=${_scanStats.totalMarked} cycles=${_scanStats.cyclesRun} kicks=${_scanStats.totalForceKicks} hb=${_scanStats.totalHeartbeatRecoveries} status=§${scanStatus==="OK"?"a":"e"}${scanStatus}`
    );
    world.sendMessage(
      `§b[pw:rand]§f tick=${now} last_rand=${randAge}t randomized=${_scanStats.totalRandomized} reg=${_appliedRegistry.size} rvt=${_scanStats.totalRevertedFar} status=§${randStatus==="OK"?"a":"e"}${randStatus}`
    );
  } catch {}
}, PW_DIAGNOSTICS_INTERVAL);

try { console.warn(`[BIGCANOPY-DIAG] MARKER-B v${PW_BUILD} ${PW_BOOT_ID} scanner module loaded — 6 LAYERS y+0..y+42, tree-BFS, verify script, periodic stats (v0 vanilla-cube + scanner 22t/39t coprime)`); } catch {}
log("[pw_scanner] v1.2.52 layered+BFS scanner active — 40t base, 6 layers y+0..y+42, tree-BFS completion (800 cap), randomizer every cycle +5t, heartbeat 600t, verify 200t");

// =========================================================================
// v1.2.42: THIRD SCRIPT — Verification + Retry
// =========================================================================
// Scans near player for leaves marked but NOT randomized (section_rolled=true
// AND rseed=false). Re-enqueues stranded leaves for the randomizer.
//
// This catches edge cases where:
//   - The randomizer queue dropped an entry (race, error)
//   - A leaf was marked but its enqueue failed
//   - Player moved away before randomizer drained the queue
// =========================================================================
const _verifyStats = {
  cyclesRun: 0,
  totalStrandedFound: 0,
  totalReEnqueued: 0,
  lastFireTick: 0,
};

function* _runVerificationScan(dim, px, py, pz) {
  // v1.3.48 (L-PERF-2): converted to yielding generator — this was a fully
  // synchronous 6-layer x 61x61 getBlock sweep inside one tick; under PS5-join
  // chunk-storm latency it blew the watchdog (InternalError: interrupted,
  // witnessed main.js:3206). Hybrid count+time yields per the v1.3.41 pattern.
  let _vc = 0; let _vslice = Date.now();
  let strandedFound = 0;
  let reEnqueued = 0;
  // Scan all 6 layers (same as main scanner)
  for (let li = 0; li < PW_LAYER_OFFSETS.length; li++) {
    if (reEnqueued >= PW_VERIFY_MAX_PER_CYCLE) break;
    const layer = PW_LAYER_OFFSETS[li];
    const yLo = py + layer.yLo;
    const yHi = py + layer.yHi;
    for (let y = yLo; y <= yHi; y++) {
      if (reEnqueued >= PW_VERIFY_MAX_PER_CYCLE) break;
      for (let dx = -PW_VERIFY_RADIUS_XZ; dx <= PW_VERIFY_RADIUS_XZ; dx++) {
        if (reEnqueued >= PW_VERIFY_MAX_PER_CYCLE) break;
        for (let dz = -PW_VERIFY_RADIUS_XZ; dz <= PW_VERIFY_RADIUS_XZ; dz++) {
          if (reEnqueued >= PW_VERIFY_MAX_PER_CYCLE) break;
          if (++_vc >= 250 || (Date.now() - _vslice) >= PW_SLICE_MS) { _vc = 0; yield; _vslice = Date.now(); }
          const x = px + dx, z = pz + dz;
          let block;
          try { block = dim.getBlock({ x, y, z }); } catch { continue; }
          if (!block) continue;
          if (!PW_LEAF_TYPES.has(block.typeId)) continue;
          let sectionRolled, rseed;
          try {
            sectionRolled = block.permutation.getState("pw:section_rolled");
            rseed = block.permutation.getState("pw:rseed");
          } catch { continue; }
          // Stranded: marked but not randomized
          if (sectionRolled === true && rseed === false) {
            strandedFound++;
            // v1.3.36: re-enqueue removed — stranded leaves (variant==0, rseed=false)
            // are self-healing: the phase-1 toggle re-applies any v0 leaf inside
            // PW_FAR_INNER on its next pass. Counter retained for diagnostics.
          }
        }
      }
    }
  }
  return { strandedFound, reEnqueued };
}

let _verifyJobRunning = false;  // v1.3.48 (L-PERF-2): one scan job at a time
system.runInterval(() => {
  if (!PW_SCANNER_ON || _verifyJobRunning) return;
  _verifyStats.cyclesRun++;
  _verifyStats.lastFireTick = system.currentTick;
  const _vplayers = world.getAllPlayers().filter(p => !_isInTeleportCooldown(p, system.currentTick));
  if (_vplayers.length === 0) return;
  _verifyJobRunning = true;
  system.runJob((function* () {
    try {
      for (const player of _vplayers) {
        let dim, px, py, pz;
        try {
          dim = player.dimension;
          px = Math.floor(player.location.x);
          py = Math.floor(player.location.y);
          pz = Math.floor(player.location.z);
        } catch { continue; }
        try {
          const result = yield* _runVerificationScan(dim, px, py, pz);
          _verifyStats.totalStrandedFound += result.strandedFound;
          _verifyStats.totalReEnqueued += result.reEnqueued;
          if (result.reEnqueued > 0) {
            try { console.warn(`[BIGCANOPY-VERIFY] v${PW_BUILD} ${PW_BOOT_ID}: ${result.reEnqueued} stranded leaves noted; Phase-1 scan job will re-classify/toggle them on its next pass (no separate randomizer drain).`); } catch {}
          }
        } catch (e) { logErr(`[pw_verify] err: ${e}`); }
        yield;
      }
    } finally { _verifyJobRunning = false; }
  })());
}, PW_VERIFY_INTERVAL);

log(`[pw_verify] v${PW_BUILD} verification script active — 200t (10s) cadence, ±30 radius, all 6 layers`);

// =========================================================================
// v1.2.42: PERIODIC STATS LOGGER
// =========================================================================
// Replaces single-fire MARKER-E/D diagnostics with periodic content-log output
// showing cumulative scanner+randomizer state. Fires every PW_STATS_LOG_INTERVAL
// ticks (5s) if there's been activity since the last log.
// =========================================================================
let _lastLoggedMarked = 0;
let _lastLoggedRandomized = 0;
let _lastStatsHeartbeatTick = 0;  // v1.3.60
function emitStats(force) {                 // v1.3.189: the periodic body, callable by pw:stats now
  const now = system.currentTick;
  // Skip if no new activity since last log
  if (!force && _scanStats.totalMarked === _lastLoggedMarked && _scanStats.totalRandomized === _lastLoggedRandomized
      && (now - _lastStatsHeartbeatTick) < 6000) return;  // v1.3.189: 5 min heartbeat when idle (was 30 s)
  _lastStatsHeartbeatTick = now;
  _lastLoggedMarked = _scanStats.totalMarked;
  _lastLoggedRandomized = _scanStats.totalRandomized;
  // Build per-species summary
  const speciesParts = [];
  for (const [tid, count] of Object.entries(_scanStats.perSpecies)) {
    const shortName = tid.replace("pw:", "").replace("_leaves", "");
    speciesParts.push(`${shortName}=${count}`);
  }
  const speciesSummary = speciesParts.length > 0 ? speciesParts.join(",") : "none";
  // Build per-variant summary
  const variantParts = [];
  for (let v = 1; v <= 6; v++) {
    const c = _scanStats.perVariant[v] || 0;
    variantParts.push(`v${v}=${c}`);
  }
  try {
    console.warn(`[BIGCANOPY-STATS] cycles=${_scanStats.cyclesRun} marked=${_scanStats.totalMarked} rnd=${_scanStats.totalRandomized} reg=${_appliedRegistry.size} rvt=${_scanStats.totalRevertedFar} reapplied=${_scanStats.totalReapplied||0} | species: ${speciesSummary} | variants: ${variantParts.join(",")} | verify_cycles=${_verifyStats.cyclesRun} re-enq=${_verifyStats.totalReEnqueued} | reverse_cycles=${_reverseStats.cyclesRun} reverted=${_reverseStats.totalReverted} | boot=${PW_BOOT_ID} | ta: logs=${_taStats.totalLogsScanned} trees=${_taStats.totalTreesWalked} taLeaves=${_taStats.totalLeavesMarkedByTreeAssoc} taFire=+${now-(_taStats.lastFireTick||0)}t p1Fire=+${now-(_scanStats.lastFireTick||0)}t`);
  } catch {}
}
system.runInterval(() => { if (_statsEnabled && PW_SCANNER_ON) emitStats(false); }, PW_STATS_LOG_INTERVAL);
// v1.3.206 his F2 = b: ONE-SHOT leaf finisher for leaves the scanner never reached (old chunks / non-structure trees):
// /scriptevent pw:leaf_finish [radius 8..96, default 48] — every pw leaf around you with rseed=false gets its final look
// (pwLeafLook + nudge) once; engine-filtered getBlocks per 16-block column slab, time-sliced job.
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:leaf_finish") return;
  const p = ev.sourceEntity;
  if (!p || p.typeId !== "minecraft:player") return;
  const R = Math.max(8, Math.min(96, parseInt(ev.message || "48", 10) || 48));
  const dim = p.dimension, c = p.location;
  const types = [...PW_LEAF_TYPES_DECAY].filter((id) => { try { return !!BlockTypes.get(id); } catch { return false; } });
  try { p.sendMessage(`§e[LEAF-FINISH] radius ${R}: assigning final looks …`); } catch {}
  system.runJob((function* () {
    let done = 0, seen = 0, t0 = Date.now();
    for (let x = Math.floor(c.x) - R; x <= Math.floor(c.x) + R; x += 16) for (let z = Math.floor(c.z) - R; z <= Math.floor(c.z) + R; z += 16) {
      let res;
      try { res = dim.getBlocks(new BlockVolume({ x, y: Math.max(-60, Math.floor(c.y) - 48), z },
        { x: x + 15, y: Math.min(318, Math.floor(c.y) + 64), z: z + 15 }), { includeTypes: types }, true); } catch { continue; }
      for (const loc of res.getBlockLocationIterator()) {
        seen++;
        try {
          const b = dim.getBlock(loc);
          if (!b || b.permutation.getState("pw:rseed") === true) continue;
          let perm = b.permutation.withState("pw:variant", pwLeafLook(b)).withState("pw:rseed", true);
          try { perm = perm.withState("pw:off", pwNudge(loc)); } catch {}
          b.setPermutation(perm); done++;
        } catch {}
        if (Date.now() - t0 > 6) { yield; t0 = Date.now(); }
      }
      yield;
    }
    try { p.sendMessage(`§a[LEAF-FINISH] ${done} leaves finished (${seen} pw leaves checked)`); } catch {}
  })());
});
system.afterEvents.scriptEventReceive.subscribe((ev) => {      // v1.3.189: /scriptevent pw:stats off | on | now
  if (ev.id !== "pw:stats") return;
  const a = String(ev.message || "").trim().toLowerCase();
  if (a === "off") { _statsEnabled = false; log(`[pw_stats] periodic line OFF (pw:stats on restores it; pw:stats now prints one)`); }
  else if (a === "on") { _statsEnabled = true; log(`[pw_stats] periodic line ON (every ${PW_STATS_LOG_INTERVAL}t)`); }
  else emitStats(true);
});

log(`[pw_stats] v${PW_BUILD} periodic stats logger active — 1200t (60s) cadence while active, 5 min idle heartbeat; /scriptevent pw:stats off|on|now`);




// =========================================================================
// LEAF DECAY SCANNER + LEAF LITTER LIFECYCLE — v1.2.10 NEW
// =========================================================================
// When player-action removes a log, leaves nearby may become orphaned (no
// connection to any log within ~6 blocks). This scanner:
//   1. Periodically inspects loaded leaves around each player.
//   2. Performs bounded BFS connectivity check toward nearest log.
//   3. If orphan: replaces leaf block with air + spawns pw:leaf_litter entity.
// 
// Critical lesson #v0.14.13 → v0.14.14: NEVER add minecraft:random_ticking
// to leaf blocks. Broke registration on PS5/Android. This scanner uses
// system.runInterval instead, applying same bounded-budget pattern as
// LEAF VARIANT SCANNER.
// 
// Tuning (intentionally light):
//   DECAY_SCAN_INTERVAL=200 ticks (10 seconds) — much less frequent than
//     variant scan; decay isn't urgent.
//   DECAY_SCAN_RADIUS=10 horizontal / 8 vertical — moderate area.
//   DECAY_MAX_PER_TICK=8 — small cap; even big tree fells produce ~50-150 
//     leaves; spread over 6-20 cycles = 60-200 seconds of falling = natural.
//   DECAY_BFS_MAX=50 — BFS cost cap per leaf check.
//   DECAY_SEARCH_RADIUS=6 — log connectivity search distance.

const PW_LEAF_TYPES_DECAY = new Set([
  "pw:oak_leaves", "pw:spruce_leaves", "pw:birch_leaves",
  "pw:jungle_leaves", "pw:dark_oak_leaves", "pw:pale_oak_leaves",
  "pw:acacia_leaves", "pw:mangrove_leaves", "pw:cherry_leaves",
  "pw:azalea_leaves", "pw:flowering_azalea_leaves",
]);

// Map leaf type → wood_type index (matches render_controller array)
const PW_LEAF_TO_WOOD_TYPE = {
  "pw:oak_leaves": 0,
  "pw:spruce_leaves": 1,
  "pw:birch_leaves": 2,
  "pw:jungle_leaves": 3,
  "pw:dark_oak_leaves": 4,
  "pw:pale_oak_leaves": 5,
  "pw:acacia_leaves": 6,
  "pw:cherry_leaves": 7,
  "pw:mangrove_leaves": 8,
  "pw:azalea_leaves": 0,
  "pw:flowering_azalea_leaves": 0,
};

// Set of all log types (vanilla + custom tier blocks) that count as connection
const PW_LOG_TYPES = new Set([
  "minecraft:oak_log", "minecraft:spruce_log", "minecraft:birch_log",
  "minecraft:jungle_log", "minecraft:dark_oak_log", "minecraft:pale_oak_log",
  "minecraft:acacia_log", "minecraft:cherry_log", "minecraft:mangrove_log",
  "minecraft:stripped_oak_log", "minecraft:stripped_spruce_log",
  "minecraft:stripped_birch_log", "minecraft:stripped_jungle_log",
  "minecraft:stripped_dark_oak_log", "minecraft:stripped_pale_oak_log",
  "minecraft:stripped_acacia_log", "minecraft:stripped_cherry_log",
  "minecraft:stripped_mangrove_log",
  "minecraft:oak_wood", "minecraft:spruce_wood", "minecraft:birch_wood",
  "minecraft:jungle_wood", "minecraft:dark_oak_wood", "minecraft:pale_oak_wood",
  "minecraft:acacia_wood", "minecraft:cherry_wood", "minecraft:mangrove_wood",
  // pw:* tier blocks
  "pw:oak_young", "pw:oak_mature", "pw:oak_old", "pw:oak_elder",
  "pw:spruce_young", "pw:spruce_mature", "pw:spruce_old", "pw:spruce_elder",
  "pw:birch_young", "pw:birch_mature", "pw:birch_old",
  "pw:jungle_young", "pw:jungle_mature", "pw:jungle_old", "pw:jungle_elder",
  "pw:dark_oak_elder", "pw:pale_oak_elder",
]);
for (const id of [...PW_LOG_TYPES]) if (id.startsWith("pw:")) { PW_LOG_TYPES.add(`${id}_root`); PW_LOG_TYPES.add(`${id}_stump`); } // v1.3.206

const DECAY_SCAN_INTERVAL = 200;       // 10 seconds (slower than variant scan)
const DECAY_SCAN_RADIUS_XZ = 10;
const DECAY_SCAN_VERT = 8;
const DECAY_MAX_PER_TICK = 8;
const DECAY_BFS_MAX = 50;
const DECAY_SEARCH_RADIUS = 6;

// Track which leaves we've already checked recently (avoid re-checking healthy ones every cycle)
// Key: "x,y,z,dim" → tick when last verified connected
const _decayLastVerified = new Map();
const DECAY_VERIFICATION_TTL = 600;  // 30 seconds — re-check this often

// v1.2.29 Phase A3 — re-validate stored pw:exposure against actual 6-neighbor pattern.
// Catch-all for ANY silent block mutation that transitions inner→outer or outer→inner
// without firing a cascade event (creeper destruction, /fill, structure load, custom
// setPermutation calls, etc.). Bedrock has NO blockSetPermutation event, so periodic
// re-validation is the only complete coverage.
//
// SEMANTIC NOTE: this checks "edge" exposure only (any non-leaf neighbor → outer).
// It does NOT validate depth-2 status — that's handled by the section flag scanner's
// 12-read flag-based check on its 100-tick cycle. Edge mismatches are the most
// common case (block changes that introduce/remove a non-leaf neighbor); depth-1/2
// shifts are downstream and converge on next section scan.
//
// Cost: 6 getBlock + 1 state-read per leaf, only when called. Decay scanner runs
// every 200 ticks and processes ~50-100 leaves per typical scan area; added cost
// ~300 getBlock per 10-sec window per player. Negligible.
const PW_EXPOSURE_RESETS = false;
function reValidateExposure(block) {
  let storedExposure;
  try { storedExposure = block.permutation.getState("pw:exposure"); }
  catch { return false; }
  if (storedExposure === undefined) return false;  // not flagged yet — section scanner will handle

  let storedRolled;
  try { storedRolled = block.permutation.getState("pw:section_rolled"); }
  catch { return false; }
  if (storedRolled !== true) return false;  // section scanner hasn't processed yet — let it do its job

  const dim = block.dimension;
  const loc = block.location;
  const offsets = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
  let actualEdge = 0;  // 0=not edge, 1=edge (any non-leaf neighbor)
  for (const [dx, dy, dz] of offsets) {
    let nb;
    try { nb = dim.getBlock({ x: loc.x + dx, y: loc.y + dy, z: loc.z + dz }); }
    catch { actualEdge = 1; break; }
    if (!nb) { actualEdge = 1; break; }
    const nid = nb.typeId;
    if (!nid.endsWith("_leaves") && !nid.endsWith("_wart_block")) {
      actualEdge = 1;
      break;
    }
  }

  // Mismatch detection:
  //   stored=0 (deep_inner), actual=1 (edge) → leaf became exposed; needs re-flag → outer
  //   stored=1 (outer), actual=0 (no edge)   → leaf is no longer at edge; might be shell or deep
  //                                            → reset to let scanner re-classify (could become
  //                                              shell/outer or deep_inner)
  // Either way, mismatch triggers reset. Section scanner re-flags on next 100-tick cycle.
  // For the (stored=1, actual=0) case where the leaf is actually shell, the flag scanner's
  // depth-2 detection will keep it classified as outer — converges correctly.
  const inferredFromEdge = actualEdge === 1 ? 1 : storedExposure;
  // Optimization: only reset if edge state actually disagrees with what storedExposure
  // implies. storedExposure=1 with actualEdge=1 is consistent (this leaf is an edge).
  // storedExposure=1 with actualEdge=0 means the leaf used to be edge but isn't now —
  // could legitimately still be shell, so reset for re-classification.
  // storedExposure=0 with actualEdge=1 means leaf was deep_inner but is now edge — definitely reset.
  // storedExposure=0 with actualEdge=0 is consistent.
  let shouldReset = false;
  if (storedExposure === 0 && actualEdge === 1) shouldReset = true;       // inner→edge, must re-flag
  else if (storedExposure === 1 && actualEdge === 0) shouldReset = true;  // not edge anymore — re-evaluate

  if (shouldReset && PW_EXPOSURE_RESETS) {   // v1.3.197: off — the look depends on position + wood only
    try {
      block.setPermutation(block.permutation
        .withState("pw:section_rolled", false)
        .withState("pw:rseed", false));
      return true;
    } catch { return false; }
  }
  return false;
}

// BFS connectivity check: from `startBlock`, can we reach a log block?
// Walks through other leaves of same type. Returns true if connected to a log.
function isLeafConnectedToLog(startBlock) {
  const startId = startBlock.typeId;
  const dim = startBlock.dimension;
  const start = startBlock.location;
  
  const visited = new Set();
  const queue = [{ x: start.x, y: start.y, z: start.z, dist: 0 }];
  visited.add(`${start.x},${start.y},${start.z}`);
  
  let iterations = 0;
  while (queue.length > 0 && iterations < DECAY_BFS_MAX) {
    iterations++;
    const cur = queue.shift();
    
    if (cur.dist > DECAY_SEARCH_RADIUS) continue;
    
    // Check 6 neighbors
    const dirs = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
    for (const [dx, dy, dz] of dirs) {
      const nx = cur.x + dx, ny = cur.y + dy, nz = cur.z + dz;
      const key = `${nx},${ny},${nz}`;
      if (visited.has(key)) continue;
      visited.add(key);
      
      let nb;
      try { nb = dim.getBlock({ x: nx, y: ny, z: nz }); }
      catch { continue; }
      if (!nb) continue;
      
      const nid = nb.typeId;
      
      // Found a log! Connected.
      if (PW_LOG_TYPES.has(nid)) return true;
      
      // Same-species leaf — continue BFS through it
      if (nid === startId && cur.dist + 1 <= DECAY_SEARCH_RADIUS) {
        queue.push({ x: nx, y: ny, z: nz, dist: cur.dist + 1 });
      }
    }
  }
  
  return false;
}

// Spawn a pw:leaf_litter entity to replace a decayed leaf block
function spawnLeafLitter(block) {
  try {
    const dim = block.dimension;
    const loc = block.location;
    const woodType = PW_LEAF_TO_WOOD_TYPE[block.typeId] ?? 0;
    
    // Spawn the entity slightly above the block center
    const spawnLoc = { x: loc.x + 0.5, y: loc.y + 0.4, z: loc.z + 0.5 };
    const entity = dim.spawnEntity("pw:leaf_litter", spawnLoc);
    if (entity) {
      try { entity.setProperty("pw:wood_type", woodType); } catch {}
      try { entity.setProperty("pw:lifetime", 0); } catch {}
      try { entity.setProperty("pw:on_ground", 0); } catch {}
    }
    
    // Replace leaf block with air
    block.setPermutation(BlockPermutation.resolve("minecraft:air"));
    return true;
  } catch (e) {
    return false;
  }
}

// Main decay scanner — runs every DECAY_SCAN_INTERVAL ticks
// v1.3.48 (L-PERF-2): guarded yielding job — the synchronous per-player leaf
// sweep (getBlock triple loop + reValidateExposure + connectivity BFS per leaf)
// blew the watchdog under PS5-join latency (InternalError at main.js:3386).
let _decayJobRunning = false;
system.runInterval(() => {
  if (!PW_SCANNER_ON || _decayJobRunning) return;     // v1.3.206: the periodic sweep goes with the scanner switch
  _decayJobRunning = true;
  system.runJob(_decaySweepJob());
}, DECAY_SCAN_INTERVAL);

// v1.3.206 EVENT-DRIVEN LEAF DECAY (tree program T5): when a log goes WITHOUT a fall (a branch cut, a log taken out of a
// tree, an explosion), the pw leaves within 7 blocks that no longer reach any log within DECAY_SEARCH_RADIUS turn to
// litter, one second later. One engine-filtered getBlocks per event; nothing runs between events.
const _decayEventQueue = [];
function _queueDecayCheck(dim, loc) {
  if (_decayEventQueue.length < 64) _decayEventQueue.push({ dim, x: Math.floor(loc.x), y: Math.floor(loc.y), z: Math.floor(loc.z), due: system.currentTick + 20 });
}
world.afterEvents.playerBreakBlock.subscribe((ev) => {
  try { if (PW_LOG_TYPES.has(ev.brokenBlockPermutation.type.id)) _queueDecayCheck(ev.dimension, ev.block.location); } catch {}
});
world.afterEvents.explosion.subscribe((ev) => {
  try {
    const blocks = ev.getImpactedBlocks();
    if (blocks.length) _queueDecayCheck(ev.dimension, blocks[Math.floor(blocks.length / 2)].location);
  } catch {}
});
let _decayEventJob = false;
system.runInterval(() => {
  if (_decayEventJob || !_decayEventQueue.length || _decayEventQueue[0].due > system.currentTick) return;
  const e = _decayEventQueue.shift();
  _decayEventJob = true;
  system.runJob((function* () {
    try {
      const types = [...PW_LEAF_TYPES_DECAY].filter((id) => { try { return !!BlockTypes.get(id); } catch { return false; } });
      const res = e.dim.getBlocks(new BlockVolume({ x: e.x - 7, y: e.y - 7, z: e.z - 7 }, { x: e.x + 7, y: e.y + 7, z: e.z + 7 }),
        { includeTypes: types }, true);
      let n = 0, t0 = Date.now(), far = null, farD = 0;
      // 1.3.224 (birch trunks end at the crown's base, his 16:50): a leaf is orphaned only when its WHOLE cluster of
      // same-species leaves touches no log — a crown's far leaves are 13-21 steps from the shortened trunk, which the old
      // 6-step / 50-node search called orphaned (it already stripped ~18 % of an old birch whenever a log was cut nearby).
      const label = new Map();                                   // "x,y,z" -> true (attached) | false (orphaned)
      const KEY = (x, y, z) => `${x},${y},${z}`;
      for (const loc of res.getBlockLocationIterator()) {
        const k0 = KEY(loc.x, loc.y, loc.z);
        if (!label.has(k0)) {
          const b0 = e.dim.getBlock(loc);
          if (!b0) continue;
          const sid = b0.typeId, seen = [k0], q = [[loc.x, loc.y, loc.z]], vis = new Set([k0]);
          let attached = false, capped = false, steps = 0;
          while (q.length && !attached) {
            const [x, y, z] = q.shift();
            for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]) {
              const nx = x + dx, ny = y + dy, nz = z + dz, k = KEY(nx, ny, nz);
              if (vis.has(k)) continue;
              vis.add(k);
              let nb; try { nb = e.dim.getBlock({ x: nx, y: ny, z: nz }); } catch { nb = undefined; }
              if (!nb) { capped = true; continue; }             // an unloaded neighbour: never strip on doubt
              if (PW_LOG_TYPES.has(nb.typeId)) { attached = true; break; }
              if (nb.typeId === sid) { if (label.has(k)) { attached = attached || label.get(k); if (label.get(k)) break; } q.push([nx, ny, nz]); seen.push(k); }
            }
            if (++steps >= 3000) { capped = true; break; }
            if (Date.now() - t0 > 6) { yield; t0 = Date.now(); }
          }
          const v = attached || capped;
          for (const k of seen) label.set(k, v);
        }
        if (label.get(k0)) continue;
        const b = e.dim.getBlock(loc);
        if (b && spawnLeafLitter(b)) {
          const d = Math.max(Math.abs(loc.x - e.x), Math.abs(loc.y - e.y), Math.abs(loc.z - e.z));
          if (d > farD) { farD = d; far = loc; }
          if (++n >= 200) break;
        }
        if (Date.now() - t0 > 6) { yield; t0 = Date.now(); }
      }
      if (n) log(`[DECAY] ${n} orphan leaves -> litter near ${e.x},${e.y},${e.z}`);
      if (far && farD >= 5) _queueDecayCheck(e.dim, far);   // a long orphaned limb: follow it past the box edge
    } catch (err) { log(`[DECAY] event job err: ${err}`); }
    _decayEventJob = false;
  })());
}, 10);

function* _decaySweepJob() {
  try {
  let totalDecayed = 0;
  const currentTick = system.currentTick;
  let _dc = 0; let _dslice = Date.now();
  
  for (const player of world.getPlayers()) {
    if (totalDecayed >= DECAY_MAX_PER_TICK) break;
    
    // Reuse teleport cooldown from leaf variant scanner
    if (_isInTeleportCooldown(player, currentTick)) continue;
    
    const dim = player.dimension;
    const px = Math.floor(player.location.x);
    const py = Math.floor(player.location.y);
    const pz = Math.floor(player.location.z);
    
    let blocksScanned = 0;
    const EARLY_EXIT_THRESHOLD = 1000;
    let leavesFoundThisPlayer = 0;
    
    for (let dy = DECAY_SCAN_VERT; dy >= -DECAY_SCAN_VERT; dy--) {
      if (totalDecayed >= DECAY_MAX_PER_TICK) break;
      for (let dx = -DECAY_SCAN_RADIUS_XZ; dx <= DECAY_SCAN_RADIUS_XZ; dx++) {
        if (totalDecayed >= DECAY_MAX_PER_TICK) break;
        for (let dz = -DECAY_SCAN_RADIUS_XZ; dz <= DECAY_SCAN_RADIUS_XZ; dz++) {
          if (totalDecayed >= DECAY_MAX_PER_TICK) break;
          
          if (blocksScanned > EARLY_EXIT_THRESHOLD && leavesFoundThisPlayer === 0) {
            dy = -DECAY_SCAN_VERT - 1;  // force outer exit
            break;
          }
          blocksScanned++;
          if (++_dc >= 200 || (Date.now() - _dslice) >= PW_SLICE_MS) { _dc = 0; yield; _dslice = Date.now(); }
          
          const bx = px + dx, by = py + dy, bz = pz + dz;
          let block;
          try { block = dim.getBlock({ x: bx, y: by, z: bz }); }
          catch { continue; }
          if (!block) continue;
          if (!PW_LEAF_TYPES_DECAY.has(block.typeId)) continue;
          
          leavesFoundThisPlayer++;

          // v1.2.29 Phase A3 — re-validate exposure flag against actual neighbor pattern.
          // Runs BEFORE the connectivity-cache shortcut so we catch stale exposure flags
          // even on connected (cached) leaves. Catches silent block mutations from
          // creeper/fill/structure/setPermutation that fire no event.
          reValidateExposure(block);

          // Check verification cache
          const key = `${bx},${by},${bz},${dim.id}`;
          const lastVerified = _decayLastVerified.get(key);
          if (lastVerified !== undefined && (currentTick - lastVerified) < DECAY_VERIFICATION_TTL) {
            continue;  // recently verified as connected; skip
          }
          
          // Run connectivity check (chunky: BFS) — breathe first if slice is stale
          if ((Date.now() - _dslice) >= PW_SLICE_MS) { yield; _dslice = Date.now(); }
          if (isLeafConnectedToLog(block)) {
            // Connected — cache result
            _decayLastVerified.set(key, currentTick);
          } else {
            // Orphan — spawn litter, remove leaf
            if (spawnLeafLitter(block)) {
              totalDecayed++;
              _decayLastVerified.delete(key);
            }
          }
        }
      }
    }
  }
  
  // Clean up old cache entries (memory pressure prevention)
  if (_decayLastVerified.size > 5000) {
    const cutoff = currentTick - DECAY_VERIFICATION_TTL * 2;
    for (const [k, v] of _decayLastVerified) {
      if (v < cutoff) _decayLastVerified.delete(k);
    }
  }
  } finally { _decayJobRunning = false; }
}


// =========================================================================
// LEAF LITTER ENTITY LIFECYCLE — v1.2.10 NEW
// =========================================================================
// pw:leaf_litter entities have minecraft:physics has_gravity=true so they
// fall under gravity automatically. We need to:
//   1. Detect when entity lands on solid ground (block below = solid)
//   2. Set pw:on_ground=1 to trigger client landed animation
//   3. Increment pw:lifetime; despawn after ~10 seconds on ground
//   4. Despawn fallback after 30 seconds total to prevent stragglers

const LITTER_LIFECYCLE_INTERVAL = 20;  // 1 second
const LITTER_GROUND_DESPAWN_TICKS = 200;  // 10 sec on ground
const LITTER_MAX_LIFETIME = 600;  // 30 sec absolute

system.runInterval(() => {
  for (const dim of [world.getDimension("overworld"), world.getDimension("nether"), world.getDimension("the_end")]) {
    if (!dim) continue;
    let entities;
    try {
      entities = dim.getEntities({ type: "pw:leaf_litter" });
    } catch { continue; }
    
    for (const ent of entities) {
      try {
        let lifetime = ent.getProperty("pw:lifetime") ?? 0;
        const onGround = ent.getProperty("pw:on_ground") ?? 0;
        lifetime += LITTER_LIFECYCLE_INTERVAL;
        
        // Check landing
        if (onGround === 0) {
          // Sample block directly below entity location
          const loc = ent.location;
          let belowBlock;
          try {
            belowBlock = dim.getBlock({ 
              x: Math.floor(loc.x), 
              y: Math.floor(loc.y - 0.1), 
              z: Math.floor(loc.z) 
            });
          } catch { belowBlock = null; }
          
          if (belowBlock && belowBlock.typeId !== "minecraft:air" && !belowBlock.typeId.includes("water")) {
            // Landed
            ent.setProperty("pw:on_ground", 1);
            ent.setProperty("pw:lifetime", 0);  // reset lifetime; counts as on-ground time now
            // Disable gravity so it stays put
            try {
              ent.applyImpulse({ x: 0, y: 0, z: 0 });
            } catch {}
            continue;
          }
        } else {
          // On ground — despawn after timer
          if (lifetime >= LITTER_GROUND_DESPAWN_TICKS) {
            try { ent.remove(); } catch {}
            continue;
          }
        }
        
        // Hard timeout safety
        if (lifetime >= LITTER_MAX_LIFETIME) {
          try { ent.remove(); } catch {}
          continue;
        }
        
        ent.setProperty("pw:lifetime", lifetime);
      } catch {}
    }
  }
}, LITTER_LIFECYCLE_INTERVAL);



// =========================================================================
// DIAGNOSTIC SCRIPTEVENT — pw:variant_dump
// =========================================================================
// Usage in-game:
//   /scriptevent pw:variant_dump
// 
// Scans a 32-block radius around the executing player and reports the
// distribution of pw:variant values across all pw:* blocks. Provides
// non-visual proof that the permutation system is actually setting different
// variant values per block (ie: not just visual approximation of variation).
// =========================================================================

// v1.2.42: pw:variant_audit handler — scan ±32 around player, report variant distribution per species
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id === "pw:forge_beat") { _forgeBeat = system.currentTick; return; }
  if (ev.id !== "pw:variant_audit") return;
  const player = ev.sourceEntity;
  if (!player || player.typeId !== "minecraft:player") return;
  const dim = player.dimension;
  const cx = Math.floor(player.location.x);
  const cy = Math.floor(player.location.y);
  const cz = Math.floor(player.location.z);
  const R = 32;
  // species → {variant_count_map, flagged_total, unflagged_total, randomized_total}
  const audit = new Map();
  let totalLeaves = 0;
  for (let dx = -R; dx <= R; dx++) {
    for (let dy = -R; dy <= R; dy++) {
      for (let dz = -R; dz <= R; dz++) {
        try {
          const b = dim.getBlock({ x: cx+dx, y: cy+dy, z: cz+dz });
          if (!b) continue;
          if (!PW_LEAF_TYPES.has(b.typeId)) continue;
          totalLeaves++;
          if (!audit.has(b.typeId)) audit.set(b.typeId, { vCounts: {}, flagged: 0, unflagged: 0, rseeded: 0 });
          const s = audit.get(b.typeId);
          let variant = null, secRolled = null, rseed = null;
          try { variant = b.permutation.getState("pw:variant"); } catch {}
          try { secRolled = b.permutation.getState("pw:section_rolled"); } catch {}
          try { rseed = b.permutation.getState("pw:rseed"); } catch {}
          if (variant !== null && variant !== undefined) {
            s.vCounts[variant] = (s.vCounts[variant] || 0) + 1;
          }
          if (secRolled === true) s.flagged++; else s.unflagged++;
          if (rseed === true) s.rseeded++;
        } catch {}
      }
    }
  }
  try {
    player.sendMessage(`§b[pw:variant_audit] §fScanned ±${R} around (${cx},${cy},${cz}) — found §a${totalLeaves}§f leaves across §a${audit.size}§f species:`);
    for (const [tid, s] of audit) {
      const shortName = tid.replace("pw:", "").replace("_leaves", "");
      const total = s.flagged + s.unflagged;
      const vStr = [0,1,2,3,4,5,6].map(v => `v${v}=${s.vCounts[v]||0}`).join(" ");
      player.sendMessage(`  §e${shortName}§f total=§a${total}§f flagged=§a${s.flagged}§f unflagged=§c${s.unflagged}§f rseeded=§a${s.rseeded}§f`);
      player.sendMessage(`     §7${vStr}`);
    }
    if (audit.size === 0) {
      player.sendMessage(`  §cNo pw:* leaves found in scan range. Are you near a tree?`);
    }
  } catch {}
});

// v1.2.41: pw:diag_status handler — instant scanner state snapshot
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:diag_status") return;
  const player = ev.sourceEntity;
  if (!player || player.typeId !== "minecraft:player") return;
  const now = system.currentTick;
  const scanAge = now - _scanStats.lastFireTick;
  const markAge = _scanStats.lastMarkTick > 0 ? now - _scanStats.lastMarkTick : -1;
  const randAge = _scanStats.lastRandomTick > 0 ? now - _scanStats.lastRandomTick : -1;
  try {
    player.sendMessage(`§b[pw:scanner v1.2.52] §fSTATUS SNAPSHOT:`);
    player.sendMessage(`  §7tick: §a${now}§f cycles_run: §a${_scanStats.cyclesRun}§f`);
    player.sendMessage(`  §7last_fire: §a${scanAge}t§f last_mark: §a${markAge}t§f last_rand: §a${randAge}t§f`);
    player.sendMessage(`  §7totalMarked: §a${_scanStats.totalMarked}§f totalRandomized: §a${_scanStats.totalRandomized}§f`);
    player.sendMessage(`  §7reg_size: §a${_appliedRegistry.size}§f force_kicks: §a${_scanStats.totalForceKicks}§f heartbeats: §a${_scanStats.totalHeartbeatRecoveries}§f`);
    player.sendMessage(`  §7verify_cycles: §a${_verifyStats.cyclesRun}§f re-enqueued: §a${_verifyStats.totalReEnqueued}§f stranded_found: §a${_verifyStats.totalStrandedFound}§f`);
    // Per-variant summary
    const vParts = [];
    for (let v = 1; v <= 6; v++) vParts.push(`v${v}=${_scanStats.perVariant[v]||0}`);
    player.sendMessage(`  §7variants randomized: §a${vParts.join(" ")}§f`);
  } catch {}
});

// Existing pw:variant_dump handler
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:variant_dump") return;
  if (!ev.sourceEntity) {
    console.warn("[pw_variants] variant_dump invoked without source entity");
    return;
  }
  const player = ev.sourceEntity;
  const dim = player.dimension;
  const cx = Math.floor(player.location.x);
  const cy = Math.floor(player.location.y);
  const cz = Math.floor(player.location.z);
  const R = 32;
  const counts = new Map();   // typeId → Map(variant → count)
  let total = 0;
  for (let dx = -R; dx <= R; dx++) {
    for (let dy = -R; dy <= R; dy++) {
      for (let dz = -R; dz <= R; dz++) {
        try {
          const b = dim.getBlock({ x: cx + dx, y: cy + dy, z: cz + dz });
          if (!b) continue;
          const id = b.typeId;
          if (!id || !id.startsWith("pw:")) continue;
          // Skip held_light — it's a runtime block, not part of the permutation system
          if (id === "pw:held_light") continue;
          let v = null;
          try { v = b.permutation.getState("pw:variant"); } catch {}
          if (v === undefined || v === null) continue;
          if (!counts.has(id)) counts.set(id, new Map());
          const sub = counts.get(id);
          sub.set(v, (sub.get(v) || 0) + 1);
          total++;
        } catch {}
      }
    }
  }
  player.sendMessage(`§e[pw_variants] §fVariant distribution within ${R}-block radius (total pw:* blocks: ${total}):`);
  if (total === 0) {
    player.sendMessage(`§7  (no pw:* blocks found — try this near custom-block trees)`);
    return;
  }
  // Sort blocks by total count descending
  const entries = Array.from(counts.entries()).sort((a, b) => {
    const sumA = Array.from(a[1].values()).reduce((s, x) => s + x, 0);
    const sumB = Array.from(b[1].values()).reduce((s, x) => s + x, 0);
    return sumB - sumA;
  });
  for (const [id, sub] of entries) {
    const sum = Array.from(sub.values()).reduce((s, x) => s + x, 0);
    const variantParts = [];
    for (let i = 0; i < 5; i++) {
      const c = sub.get(i) || 0;
      const pct = sum > 0 ? Math.round((c / sum) * 100) : 0;
      variantParts.push(`v${i}:${c}(${pct}%)`);
    }
    player.sendMessage(`§a${id}§7 §f[${sum}]§7 ${variantParts.join(" ")}`);
  }
  player.sendMessage(`§e[pw_variants] §7Even distribution = randomization working. Skewed = bug.`);
});

log("[pw_variants] scriptevent pw:variant_dump registered");


// ============================================================================
// FIREFLY AMBIENT — v0.14.25
// Spawns pw:firefly_ambient particles around players in swamp/mangrove biomes
// at night. Designed as a graceful, low-impact ambient field that adds the
// "fireflies everywhere" atmosphere without tying emission to firefly bushes.
//
// Performance budget: 2 particles/second/player. Each particle lives 10-18s.
// Steady state: ~30 active particles per player. Negligible cost.
// ============================================================================
const FIREFLY_AMBIENT_BIOMES = ["minecraft:swamp", "minecraft:swampland", "minecraft:mangrove_swamp"];
const FIREFLY_AMBIENT_INTERVAL = 30;     // ticks (1 second)
const FIREFLY_AMBIENT_PER_CYCLE = 2;     // particles per cycle per player
const FIREFLY_AMBIENT_RADIUS_H = 14;     // horizontal radius (blocks)
const FIREFLY_AMBIENT_RADIUS_V = 5;      // vertical radius (blocks)
const FIREFLY_NIGHT_START = 12500;        // game ticks (dusk)
const FIREFLY_NIGHT_END = 23500;          // game ticks (pre-dawn)
const FIREFLY_PARTICLE = "pw:firefly_ambient";

// Probe state — set false if dimension.getBiome unavailable in this engine version
let fireflyBiomeApiOk = null;

function spawnAmbientFirefliesForPlayer(player) {
  // Night-time check
  let timeOk = true;
  try {
    const t = world.getTimeOfDay();
    timeOk = (t >= FIREFLY_NIGHT_START && t <= FIREFLY_NIGHT_END);
  } catch { /* fall through with timeOk=true if API unavailable */ }
  if (!timeOk) return;

  // Biome check. v1.3.186: the pack now pins @minecraft/server 2.3.0, where Dimension.getBiome is stable, so
  // fireflies keep to swamps and mangroves as designed (on the 2.0.0 pin the call did not exist and the
  // fallback below spawned them in every biome). A throw at ONE location (above the build limit, an unloaded
  // chunk) now skips this beat only, instead of switching the biome gate off for the rest of the session.
  let biomeOk = true;
  if (fireflyBiomeApiOk !== false) {
    if (typeof player.dimension.getBiome !== "function") {
      fireflyBiomeApiOk = false;
    } else {
      let biome;
      try { biome = player.dimension.getBiome(player.location); } catch { return; }
      const biomeId = biome?.id ?? biome?.typeId ?? null;
      if (biomeId !== null) {
        const idLower = String(biomeId).toLowerCase();
        biomeOk = FIREFLY_AMBIENT_BIOMES.includes(biomeId) || idLower.includes("swamp") || idLower.includes("mangrove");
        fireflyBiomeApiOk = true;
      } else {
        fireflyBiomeApiOk = false;
      }
    }
  }
  if (fireflyBiomeApiOk === false) {
    // Fallback (API missing): spawn anyway at night so the user still sees fireflies
    biomeOk = true;
  }
  if (!biomeOk) return;

  // Spawn particles in random positions around player
  const loc = player.location;
  for (let i = 0; i < FIREFLY_AMBIENT_PER_CYCLE; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 4 + Math.random() * (FIREFLY_AMBIENT_RADIUS_H - 4);
    const x = loc.x + Math.cos(angle) * dist;
    const z = loc.z + Math.sin(angle) * dist;
    const y = loc.y + (Math.random() - 0.3) * FIREFLY_AMBIENT_RADIUS_V;
    try {
      player.dimension.spawnParticle(FIREFLY_PARTICLE, { x, y, z });
    } catch { /* unloaded chunk or location invalid — silently skip */ }
  }
}

system.runInterval(() => {
  try {
    for (const p of world.getAllPlayers()) {
      try { spawnAmbientFirefliesForPlayer(p); } catch {}
    }
  } catch {}
}, FIREFLY_AMBIENT_INTERVAL);

log("[firefly_ambient] active — pw:firefly_ambient spawns at night in swamp/mangrove biomes");


// v1.2.41 final init marker — proves script reached end of file
try { console.warn(`[BIGCANOPY-DIAG] MARKER-Z v${PW_BUILD} ${PW_BOOT_ID} reached end of main.js — all init complete (renamed from MARKER-F to end the F collision)`); } catch {}


// ============================================================================
// v1.3.28 — MILKY WAY procedural star band (D4)
// Spawns ~80 small "star" particles in a galactic-plane band 50-90 blocks above
// each player, only at night. Each particle has a 60s lifetime; re-spawn every
// 45s to maintain continuous starfield. Particles are stationary in world space
// once spawned, so they appear to slowly trail as the player walks (acceptable
// for ambient sky decoration — they're far overhead and visually distant).
//
// Galactic band orientation: along world East-West axis, ±20° latitudinal spread.
// Density gradient: higher toward "galactic center" (random per-spawn offset).
// Total particles per player per cycle: 80.
//
// Cost: ~80 spawnParticle calls every 45 seconds per online player. Negligible.
// User direction: D4 Path 1 (particle band). If feedback indicates it's too sparse
// or too dense, adjust MILKY_PARTICLE_COUNT or MILKY_RESPAWN_TICKS.
// ============================================================================

const MILKY_PARTICLE_COUNT = 80;
const MILKY_RESPAWN_TICKS = 900;  // 45 seconds
const MILKY_HEIGHT_MIN = 50;
const MILKY_HEIGHT_MAX = 90;
const MILKY_BAND_WIDTH_DEG = 22;   // ±22° latitude from galactic plane
const MILKY_BAND_HORIZONTAL_RADIUS = 70;  // XZ spread radius

function _spawnMilkyWayForPlayer(player) {
  try {
    // Time check: only spawn at night. Bedrock time-of-day: 12000-23000 is night.
    const tod = world.getTimeOfDay ? world.getTimeOfDay() : 13000;
    if (tod < 12500 || tod > 23000) return;
    
    const px = player.location.x;
    const py = player.location.y;
    const pz = player.location.z;
    const dim = player.dimension;
    
    // Galactic band center is a random horizontal direction (re-randomized per spawn cycle)
    // For visual consistency, anchor the band to a worldwide-stable angle: 0° (along +X axis)
    // This way the band appears in the same direction every night
    const bandYaw = 0;  // along world +X
    
    for (let i = 0; i < MILKY_PARTICLE_COUNT; i++) {
      // Random position along galactic band
      // r: horizontal distance from player along band
      const r = (Math.random() * 2 - 1) * MILKY_BAND_HORIZONTAL_RADIUS;
      // lat: perpendicular offset (latitude from galactic plane)
      const lat = (Math.random() * 2 - 1) * MILKY_BAND_WIDTH_DEG / 90 * MILKY_BAND_HORIZONTAL_RADIUS * 0.35;
      // Apply bandYaw rotation: at yaw=0, X=r (along band), Z=lat (perp)
      const sx = px + r * Math.cos(bandYaw) - lat * Math.sin(bandYaw);
      const sz = pz + r * Math.sin(bandYaw) + lat * Math.cos(bandYaw);
      const sy = py + MILKY_HEIGHT_MIN + Math.random() * (MILKY_HEIGHT_MAX - MILKY_HEIGHT_MIN);
      
      // Density bias toward "galactic center" — spawn extras within ±25 of band center
      if (Math.abs(r) > 25 && Math.random() < 0.6) continue;  // skip 60% of outer-band particles
      
      try {
        dim.spawnParticle("pw:milky_way_star", { x: sx, y: sy, z: sz });
      } catch (e) {
        // Silently skip — particle may fail in unloaded chunks
      }
    }
  } catch (e) {
    // Silently fail at top level
  }
}

system.runInterval(() => {
  try {
    const players = world.getAllPlayers();
    for (const p of players) {
      _spawnMilkyWayForPlayer(p);
    }
  } catch (e) {
    // silently swallow
  }
}, MILKY_RESPAWN_TICKS);

// Initial spawn on startup
system.runTimeout(() => {
  try {
    const players = world.getAllPlayers();
    for (const p of players) {
      _spawnMilkyWayForPlayer(p);
    }
  } catch (e) {}
}, 100);  // 5 seconds after world load


// ============================================================================
// pw:golden_crown AURA (v1.3.54) — Resistance while worn, floating flame,
// torch-grade dynamic light. Toggles below; flame can be disabled while
// keeping the light (witness request).
// ============================================================================
const PW_CROWN_RESIST = true;   // Resistance IV while worn (survives warden hits; armor points alone cannot — sonic boom bypasses armor)
const PW_CROWN_FLAME  = true;   // flame particle floating just above the crown
const PW_CROWN_LIGHT  = true;   // dynamic light: torch-level light block follows the wearer
const PW_CROWN_TICKS  = 4;
const _pwCrownLight = new Map(); // playerId -> {dimId,x,y,z}

function _pwClearCrownLight(rec) {
  if (!rec) return;
  try {
    const dim = world.getDimension(rec.dimId);
    const b = dim.getBlock({ x: rec.x, y: rec.y, z: rec.z });
    // v1.3.214 (D-C515): the engine reports the flattened id minecraft:light_block_14 — the old exact test never matched,
    // so the crown left a light above every cell its wearer walked through. Any light block at our recorded cell is ours.
    if (b && String(b.typeId).startsWith("minecraft:light_block")) b.setType("minecraft:air");
  } catch {}
}

system.runInterval(() => {
  for (const player of world.getAllPlayers()) {
    let wearing = false;
    try {
      const eq = player.getComponent("minecraft:equippable");
      const head = eq ? eq.getEquipment("Head") : undefined;
      wearing = !!head && head.typeId === "pw:golden_crown";
    } catch {}
    const rec = _pwCrownLight.get(player.id);
    if (!wearing) {
      if (rec) { _pwClearCrownLight(rec); _pwCrownLight.delete(player.id); }
      continue;
    }
    if (PW_CROWN_RESIST) {
      try { player.addEffect("resistance", PW_CROWN_TICKS * 20, { amplifier: 3, showParticles: false }); } catch {}
    }
    if (PW_CROWN_FLAME && (system.currentTick % (PW_CROWN_TICKS * 2) === 0)) {
      try {
        player.dimension.spawnParticle("minecraft:basic_flame_particle",
          { x: player.location.x, y: player.location.y + 2.35, z: player.location.z });
      } catch {}
    }
    if (PW_CROWN_LIGHT) {
      try {
        const lx = Math.floor(player.location.x), ly = Math.floor(player.location.y) + 2, lz = Math.floor(player.location.z);
        const dimId = player.dimension.id;
        if (!rec || rec.x !== lx || rec.y !== ly || rec.z !== lz || rec.dimId !== dimId) {
          const target = player.dimension.getBlock({ x: lx, y: ly, z: lz });
          if (target && target.isAir) {
            target.setPermutation(BlockPermutation.resolve("minecraft:light_block", { block_light_level: 14 }));
            _pwClearCrownLight(rec);
            _pwCrownLight.set(player.id, { dimId, x: lx, y: ly, z: lz });
          }
          // occupied target: keep the previous light until a free cell appears
        }
      } catch {}
    }
  }
}, PW_CROWN_TICKS);

world.afterEvents.playerLeave.subscribe((ev) => {
  const rec = _pwCrownLight.get(ev.playerId);
  if (rec) { _pwClearCrownLight(rec); _pwCrownLight.delete(ev.playerId); }
});

try { console.warn(`[PW-VERSION] BP-02 v${PW_BUILD} (iter 2026-08-21s) ${PW_BOOT_ID} — crown aura: Resistance IV + flame + torch-grade dynamic light (toggles), protection 100`); } catch {}


// ============================================================
// [PW-SLABSMOOTH S2] Terrain slab smoothing pass — v1.3.98
// Countered's notch test + cliff gate, ported to runtime scan.
// Floor slabs only. Additive module; touches no leaf code.
// ============================================================
const PW_SLAB_ENABLED = true;
const PW_SLAB_INTERVAL = 20;
const PW_SLAB_RADIUS_XZ = 20;   // heartbeat window: 30 out in every cardinal direction
const PW_SLAB_Y_DOWN = 3, PW_SLAB_Y_UP = 3;   // +3/-3 band: never run ahead of the player
const PW_SLAB_CELLS_PER_YIELD = 350;
const PW_SLAB_MAX_PLACE_PER_CYCLE = 160;
const PW_SLAB_MIN_RUN = 4;
const PW_SLAB_LIP_MAX = 48;   // per SEED, so the spiral keeps advancing instead of stalling on the first lip      // how far a single lip walk may travel before handing back to the spiral
const PW_SLAB_SLOPE_MAX = 0.55;  // his metric: leave the lip when |slope| crosses this   // a rise face must be continuous for at least this many cells to be slabbed
const PW_SLAB_MAP = new Map(Object.entries({
  "minecraft:hardened_clay":"pw:slab_terracotta", "minecraft:stained_hardened_clay":"pw:slab_terracotta",
  "minecraft:white_terracotta":"pw:slab_terracotta_white", "minecraft:orange_terracotta":"pw:slab_terracotta_orange", "minecraft:magenta_terracotta":"pw:slab_terracotta_magenta", "minecraft:light_blue_terracotta":"pw:slab_terracotta_light_blue", "minecraft:yellow_terracotta":"pw:slab_terracotta_yellow", "minecraft:lime_terracotta":"pw:slab_terracotta_lime", "minecraft:pink_terracotta":"pw:slab_terracotta_pink", "minecraft:gray_terracotta":"pw:slab_terracotta_gray", "minecraft:light_gray_terracotta":"pw:slab_terracotta_light_gray", "minecraft:cyan_terracotta":"pw:slab_terracotta_cyan", "minecraft:purple_terracotta":"pw:slab_terracotta_purple", "minecraft:blue_terracotta":"pw:slab_terracotta_blue", "minecraft:brown_terracotta":"pw:slab_terracotta_brown", "minecraft:green_terracotta":"pw:slab_terracotta_green", "minecraft:red_terracotta":"pw:slab_terracotta_red", "minecraft:black_terracotta":"pw:slab_terracotta_black",
  "minecraft:grass_block":"pw:slab_grass", "minecraft:dirt":"pw:slab_dirt",
  "minecraft:coarse_dirt":"pw:slab_coarse_dirt", "minecraft:podzol":"pw:slab_podzol",
  "minecraft:mycelium":"pw:slab_mycelium", "minecraft:grass_path":"pw:slab_path",
  "minecraft:dirt_path":"pw:slab_path", "minecraft:mud":"pw:slab_mud",
  "minecraft:clay":"pw:slab_clay", "minecraft:moss_block":"pw:slab_moss",
  "minecraft:stone":"pw:slab_stone", "minecraft:deepslate":"pw:slab_deepslate",
  "minecraft:andesite":"pw:slab_andesite", "minecraft:diorite":"pw:slab_diorite",
  "minecraft:granite":"pw:slab_granite", "minecraft:tuff":"pw:slab_tuff",
  "minecraft:calcite":"pw:slab_calcite", "minecraft:sandstone":"pw:slab_sandstone",
  "minecraft:red_sandstone":"pw:slab_red_sandstone", "minecraft:sand":"pw:slab_sand",
  "minecraft:red_sand":"pw:slab_red_sand", "minecraft:gravel":"pw:slab_gravel",
  "minecraft:snow":"pw:slab_snow", "minecraft:packed_ice":"pw:slab_packed_ice"
}));
const _slabRegistry = new Map();
try { console.warn(`[SLABSMOOTH] BOOT v1.3.174 (dormant until PW-SlabForge heartbeats) module loaded — interval=${PW_SLAB_INTERVAL}t radius=${PW_SLAB_RADIUS_XZ} band=±${PW_SLAB_Y_UP}`); } catch {}
const _slabStats = { cycles:0, placed:0, cliffSkip:0, considered:0, mapMiss:0, firstFired:false, vegSaved:0, probeFired:false, denied:0, denySkip:0, doneSkip:0, approachSkip:0, pillarSkip:0, runSkip:0, riserSkip:0, slopeSkip:0, editSkip:0, bridged: 0, spanSkip:0, lipPlaced:0, dugSkip:0, riserConv:0, kinSkip:0, repaired:0, chunkClosed:0, snowCleared:0, vegLift:0, snowLift:0, capWarned:false, hits:new Map() };
const _slabVegLedger = new Map();
// VEGETATION SEATS (Abs0lum 2026-08-26): store -> slab -> re-seat one block up on -8px geometry.
// Vanilla plants pop off slabs (support rules), so the restored plant is OUR clone.
const PW_VEG_DOUBLE = new Map(Object.entries({
  "minecraft:tall_grass":"pw:seated_double_tall_grass", "minecraft:large_fern":"pw:seated_double_large_fern", "minecraft:lilac":"pw:seated_double_lilac", "minecraft:rose_bush":"pw:seated_double_rose_bush", "minecraft:peony":"pw:seated_double_peony", "minecraft:sunflower":"pw:seated_double_sunflower"
}));
const PW_VEG_SEAT = new Map(Object.entries({
  "minecraft:deadbush":"pw:seated_deadbush", "minecraft:dandelion":"pw:seated_dandelion", "minecraft:poppy":"pw:seated_poppy", "minecraft:blue_orchid":"pw:seated_blue_orchid", "minecraft:allium":"pw:seated_allium", "minecraft:azure_bluet":"pw:seated_azure_bluet", "minecraft:red_tulip":"pw:seated_red_tulip", "minecraft:orange_tulip":"pw:seated_orange_tulip", "minecraft:white_tulip":"pw:seated_white_tulip", "minecraft:pink_tulip":"pw:seated_pink_tulip", "minecraft:oxeye_daisy":"pw:seated_oxeye_daisy", "minecraft:cornflower":"pw:seated_cornflower", "minecraft:lily_of_the_valley":"pw:seated_lily_of_the_valley", "minecraft:short_grass":"pw:seated_short_grass", "minecraft:fern":"pw:seated_fern"
}));

let _slabJobActive = false;
let _slabJobStartTick = 0;
let _slabSchedFired = false;
const PW_SLAB_REPLACEABLE = new Set([
  "minecraft:short_grass","minecraft:tallgrass","minecraft:tall_grass","minecraft:fern","minecraft:large_fern",
  "minecraft:snow_layer","minecraft:dandelion","minecraft:poppy","minecraft:cornflower","minecraft:oxeye_daisy",
  "minecraft:azure_bluet","minecraft:red_tulip","minecraft:orange_tulip","minecraft:white_tulip","minecraft:pink_tulip",
  "minecraft:allium","minecraft:lily_of_the_valley","minecraft:blue_orchid","minecraft:wither_rose","minecraft:torchflower",
  "minecraft:pink_petals","minecraft:leaf_litter","minecraft:wildflowers","minecraft:bush","minecraft:firefly_bush",
  "minecraft:dead_bush","minecraft:sweet_berry_bush","minecraft:pitcher_plant","minecraft:closed_eyeblossom",
  "minecraft:open_eyeblossom","minecraft:crimson_roots","minecraft:warped_roots","minecraft:nether_sprouts",
  "minecraft:moss_carpet","minecraft:pale_moss_carpet","minecraft:glow_lichen","minecraft:vine","minecraft:hanging_roots",
  "minecraft:seagrass","minecraft:kelp","minecraft:lily_pad","minecraft:sugar_cane","minecraft:brown_mushroom",
  "minecraft:red_mushroom","minecraft:crimson_fungus","minecraft:warped_fungus","minecraft:cocoa","minecraft:web"
]);
for (const k of PW_VEG_SEAT.keys()) PW_SLAB_REPLACEABLE.add(k);
for (const k of PW_VEG_DOUBLE.keys()) PW_SLAB_REPLACEABLE.add(k);  // the lift species always qualify as clearable

// Pattern fallback: ground clutter absorbed from other packs uses namespaces we cannot enumerate.
// A block is clutter if its id matches one of these AND is not a real surface material.
const PW_SLAB_CLUTTER_RX = /(_sapling|_flower|flower_|_petals|leaf_litter|_carpet|_fern|_bush|_roots|_sprouts|_lichen|_vine|_mushroom|seagrass|_coral|_crop|_stem|_grass)$/;
const PW_SLAB_NEVER_CLUTTER = new Set(["minecraft:grass_block","minecraft:dirt_with_roots","minecraft:mangrove_roots","minecraft:muddy_mangrove_roots"]);
function _slabIsClutter(tid) {
  if (typeof tid !== "string") return false;
  if (PW_SLAB_NEVER_CLUTTER.has(tid)) return false;
  if (tid.endsWith("_block")) return false;
  return PW_SLAB_CLUTTER_RX.test(tid);
}
function _slabIsOurs(tid){ return typeof tid === "string" && tid.indexOf("pw:slab_") === 0; }
function _slabPassable(b){ return !!b && (b.isAir === true || PW_SLAB_REPLACEABLE.has(b.typeId) || _slabIsClutter(b.typeId)); }
function _slabIsLava(b){ return !!b && (b.typeId === "minecraft:lava" || b.typeId === "minecraft:flowing_lava"); }
// Column surface via typeId/isAir only (no isSolid — property unproven on this module pin).
// Returns { y, slabId, ours } for the topmost non-passable block, or null.
// Anything that is not natural ground is VOID for slope purposes (Abs0lum's ruling): a tree standing on
// the high side must not disqualify a rise. Logs, leaves, planks, fences, glass, furniture and every other
// built or grown thing are descended through until real terrain is found.
const PW_SLAB_NONGROUND_RX = /(_log|_wood|_leaves|_planks|_stem|_hyphae|_sapling|_fence|_gate|_door|_trapdoor|_stairs|_wall$|_sign|_button|_pressure_plate|_bed$|_banner|_carpet|_wool$|_glass|_pane|_torch|_lantern|_campfire|_chest|_barrel|_table|_scaffolding|shroomlight|_wart_block|bamboo|cactus|sugar_cane|_mushroom_block|beehive|bee_nest|_ladder|_vine|_chain|_rail|_shulker_box|_candle|_head$|_skull$)/;
function _slabIsNonGround(tid) {
  if (typeof tid !== "string") return false;
  if (tid.startsWith("pw:") && !tid.startsWith("pw:slab_")) return true;
  if (/^minecraft:(oak|birch|spruce|jungle|acacia|dark_oak|mangrove|cherry|pale_oak|crimson|warped|bamboo)_/.test(tid)) return true;
  return PW_SLAB_NONGROUND_RX.test(tid);
}
function _slabColumnSurface(dim, x, z, yTop, yBot, throughOurs) {
  // CAVE FIX: descending from yTop underground lands inside the CEILING, and the ceiling was being
  // reported as terrain — which is why the smoother crawled below ground and read negative slope badly.
  // We must first see open space, then take the first solid below it: that is the floor we stand on.
  for (let y = yTop; y >= yBot; y--) {
    let b; try { b = dim.getBlock({ x, y, z }); } catch { return null; }
    if (!b) return null;
    if (_slabPassable(b)) continue;
    if (throughOurs && _slabIsOurs(b.typeId)) continue;
    if (!_slabIsOurs(b.typeId) && !_slabIsLava(b) && _slabIsNonGround(b.typeId)) continue;
    // EXPOSURE TEST (Abs0lum's correction): a solid only counts as a surface if the block DIRECTLY above
    // it is void. That is what separates a floor you can stand on from the underside of a ceiling or a
    // block buried in rock, and it is a stronger test than "did we pass through open space at some point".
    if (!_slabIsLava(b)) {
      let up; try { up = dim.getBlock({ x, y: y + 1, z }); } catch { up = null; }
      if (!up) return null;
      const upOk = _slabPassable(up) || (throughOurs && _slabIsOurs(up.typeId)) || _slabIsNonGround(up.typeId);
      if (!upOk) continue;
    }
    if (_slabIsLava(b)) return { y, slabId: null, ours: false, lava: true };
    const tid = b.typeId;
    return { y, slabId: PW_SLAB_MAP.get(tid) || null, ours: _slabIsOurs(tid), lava: false };
  }
  return null;
}
const PW_SLAB_DENY_PROP = "pw:slab_deny";
const PW_SLAB_DONE_PROP = "pw:slab_done";
const PW_SLAB_EDITCOL_PROP = "pw:slab_editcols";
const _slabEditCol = new Set();
function _slabMarkEdit(x, z) { for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++) _slabEditCol.add(`${x + dx},${z + dz}`); _slabPersistDirty = true; } // columns the player touched (3x3 around every place/break) — the smoother never revisits

const PW_SLAB_PROP_CAP = 20000;
const _slabDeny = new Set();      // positions a player broke — never re-place
const _slabDone = new Set();
      // chunk keys fully processed — never revisit
const _slabChunkSeen = new Map(); // chunkKey -> Set of UNIQUE column keys actually evaluated
const PW_SLAB_CHUNK_COLS = 256;
// TERRAIN-BASELINE IMMUNITY (Abs0lum's ruling): the engine cannot tell us whether a column ever had a
// block above it, so we record what the ground looked like the FIRST time we ever saw it. A column only
// stays eligible while its surface still matches that first reading. Dig a build site out and the heights
// disagree — immune. Fill a hollow to make a platform — immune. Untouched terrain matches and is smoothed
// normally. Memory-only by necessity: 256 heights per chunk will not fit the 20k dynamic-property budget,
// so this resets on reload, while the persisted done-chunk ledger keeps finished chunks protected anyway.
const _slabBaseline = new Map();          // chunkKey -> Map(colIndex -> y)
const PW_SLAB_BASELINE_CHUNKS = 256;      // LRU cap so a long session cannot grow without bound
function _slabBaselineOK(ck, x, z, y) {
  let cm = _slabBaseline.get(ck);
  if (!cm) {
    if (_slabBaseline.size >= PW_SLAB_BASELINE_CHUNKS) {
      const oldest = _slabBaseline.keys().next().value;
      if (oldest !== undefined) _slabBaseline.delete(oldest);
    }
    cm = new Map(); _slabBaseline.set(ck, cm);
  }
  const ci = (x & 15) * 16 + (z & 15);
  const had = cm.get(ci);
  if (had === undefined) { cm.set(ci, y); return true; }   // first sighting becomes the baseline
  return had === y;                                        // changed since first sighting -> immune
}
let _slabAnchorIx = 0, _slabPersistDirty = false;
const _slabScanners = new Map();   // playerId -> cursor state; the LEDGERS stay world-level
function _slabLoadLedgers() {
  try {
    let d = undefined, c = undefined;
    try { d = world.getDynamicProperty(PW_SLAB_DENY_PROP); } catch { d = undefined; }
    try { c = world.getDynamicProperty(PW_SLAB_DONE_PROP); } catch { c = undefined; }
    if (typeof d === "string" && d.length) for (const k of d.split(";")) if (k) _slabDeny.add(k);
    if (typeof c === "string" && c.length) for (const k of c.split(";")) if (k) _slabDone.add(k);
      const ec = world.getDynamicProperty(PW_SLAB_EDITCOL_PROP);
      if (typeof ec === "string" && ec.length) for (const k of ec.split(";")) if (k) _slabEditCol.add(k);
    console.warn(`[SLABSMOOTH] ledgers loaded: deny=${_slabDeny.size} done_chunks=${_slabDone.size} open_chunks=${_slabChunkSeen.size}`);
  } catch (e) { logErr("slabsmooth-ledger-load: " + (e && e.message ? e.message : e)); }
}
function _slabSaveLedgers() {
  if (!_slabPersistDirty) return;
  _slabPersistDirty = false;
  try {
    const d = Array.from(_slabDeny).join(";");
    const c = Array.from(_slabDone).join(";");
    if (d.length <= PW_SLAB_PROP_CAP) world.setDynamicProperty(PW_SLAB_DENY_PROP, d);
    if (c.length <= PW_SLAB_PROP_CAP) world.setDynamicProperty(PW_SLAB_DONE_PROP, c);
    else if (!_slabStats.capWarned) { _slabStats.capWarned = true; logErr("slabsmooth-ledger: done-chunk ledger exceeded " + PW_SLAB_PROP_CAP + " chars — persistence paused (session memory still active)"); }
  try { world.setDynamicProperty(PW_SLAB_EDITCOL_PROP, Array.from(_slabEditCol).slice(0, PW_SLAB_PROP_CAP).join(";")); } catch {}
  } catch (e) { logErr("slabsmooth-ledger-save: " + (e && e.message ? e.message : e)); }
}
// spiral offsets: nearest-first so the player's immediate surroundings finish before the rim
system.run(() => { try { _slabLoadLedgers(); } catch (e) { logErr("slabsmooth-ledger-load-deferred: " + (e && e.message ? e.message : e)); } });   // deferred one tick: early-execution law (v1.3.157) above — the old call site sat before them, inside the temporal dead zone
const PW_SLAB_OFFSETS = (() => {
  const o = [];
  for (let dx = -PW_SLAB_RADIUS_XZ; dx <= PW_SLAB_RADIUS_XZ; dx++)
    for (let dz = -PW_SLAB_RADIUS_XZ; dz <= PW_SLAB_RADIUS_XZ; dz++) o.push([dx, dz, dx * dx + dz * dz]);
  o.sort((a, b) => a[2] - b[2]);
  return o.map(v => [v[0], v[1]]);
})();
world.afterEvents.playerBreakBlock.subscribe((ev) => {
  try {
    const id = ev.brokenBlockPermutation && ev.brokenBlockPermutation.type ? ev.brokenBlockPermutation.type.id : "";
    if (typeof id === "string" && id.indexOf("pw:slab_") === 0) {
      const l = ev.block.location;
      const k = `${l.x},${l.y},${l.z}`;
      _slabDeny.add(k);
    try { _slabMarkEdit(ev.block.location.x, ev.block.location.z); } catch {} _slabRegistry.delete(k); _slabPersistDirty = true;
      _slabStats.denied++;
    }
  } catch (e) { logErr("slabsmooth-break: " + (e && e.message ? e.message : e)); }
});
const PW_SLAB_N8 = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
const PW_SLAB_AXES = [[[0,-1],[0,1]], [[1,0],[-1,0]], [[1,-1],[-1,1]], [[1,1],[-1,-1]]];

// Does this column qualify for a slab? Abs0lum's rule, evaluated over ALL EIGHT directions at once:
//   gradient — no neighbour may sit more than one level away, either sign (cliff lips refused)
//   riser    — at least one of the eight must sit exactly +1 (diagonals included, so corners count)
//   span     — on at least one of the four axes, prev/cell/next must span no more than one level
// Returns {sy, slabId} or null. No direction variable survives this function, which is the bug class
// that produced "'rd' is not defined" in v1.3.122.
function _slabQualify(x, z, surf, dim) {   // v1.3.220: dim was undefined here (lint)
  const c0 = surf(x, z);
  if (!c0 || c0.lava || c0.ours || !c0.slabId) return null;
  if (_slabEditCol.has(`${x},${z}`)) { _slabStats.editSkip++; return null; }
  const sy = c0.y + 1;
  // TWO-FLAT RULE (Abs0lum): a rise only counts when the cell DIRECTLY OPPOSITE it is level with the
  // candidate. That is the "two horizontal contiguous blocks of the same elevation before a rise", and
  // the slab lands on the middle one. Without it a cell with a rise on one side and a drop on the other
  // could still pass on a perpendicular axis — which is where the stray placements came from.
  // TWO-FLAT RULE — ANTIPODE ONLY, and the corner case is still covered.
  //   A rise only counts when the cell DIRECTLY OPPOSITE it sits at the candidate's own height. That is
  //   "two horizontal contiguous blocks of the same elevation before a rise", and the slab lands on the
  //   middle one. Diagonal RISES use the diagonal antipode, which is how corners are served — v1.3.129
  //   instead broadened the BACK test to the antipode's two flanking cells, and that was wrong: on any
  //   terrace running perpendicular to the rise those flanks are always level, so the two-flat rule was
  //   satisfied by geometry that had nothing to do with the slope. Simulated on profile 0,0,1,2 the old
  //   rule placed a slab on index 2 — the HIGH block of the step — which is exactly what Abs0lum saw.
  // SAME-MATERIAL GATE (his rule): at least one neighbour must sit at the candidate's own height AND be
  //   the same slab family, so a slab never appears on an isolated pocket of one material.
  // TWO PASSES, deliberately. v1.3.139's `break` on the first qualifying rise skipped the cliff test for
  // every neighbour later in the ring, so a cell with a valid rise at N and a 2-high wall at E would
  // place a slab hugging the wall — partially re-opening the exact class he reported. The cliff/lava scan
  // now completes over ALL EIGHT neighbours before any riser logic runs, restoring the pre-.139 guarantee.
  for (const [dx, dz] of PW_SLAB_N8) {
    const nb = surf(x + dx, z + dz);
    if (!nb) continue;
    if (nb.lava) return null;
    const d = nb.y - c0.y;
    if (d > 1 || d < -1) { _slabStats.cliffSkip++; return null; }
  }
  let riser = false;
  for (let i = 0; i < PW_SLAB_N8.length; i++) {
    const nb = surf(x + PW_SLAB_N8[i][0], z + PW_SLAB_N8[i][1]);
    if (!nb || nb.ours || nb.y - c0.y !== 1) continue;
    const k = (i + 4) % 8;
    const back = surf(x + PW_SLAB_N8[k][0], z + PW_SLAB_N8[k][1]);
    if (back && !back.lava && back.y === c0.y) { riser = true; break; }
    _slabStats.approachSkip++;
  }
  // CONTINUATION RULE v1.3.148 (supersedes the both-sides bridge — witnessed: corners placed, the
  // adjacent cardinal cell skipped forever, bridged=0 across three sessions): a lip line continues
  // through inside corners and single gaps. Conditions: some cardinal neighbour already carries OUR
  // slab for this material at this level, AND some cardinal neighbour is a wall (higher ground) —
  // so flats never slab spontaneously. Every safety test above has already passed for this cell.
  if (!riser) {
    const want = PW_SLAB_MAP.get(c0.id);
    if (want) {
      let oursAdj = false, wallAdj = false;
      for (const [ax, az] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        if (!oursAdj) { try { const tb = dim.getBlock({ x: x + ax, y: sy, z: z + az }); if (tb && tb.typeId === want) oursAdj = true; } catch {} }
        if (!wallAdj) { const nb = surf(x + ax, z + az); if (nb && !nb.ours && nb.y === sy) wallAdj = true; }
        if (oursAdj && wallAdj) { riser = true; _slabStats.bridged++; break; }
      }
    }
  }
  if (!riser) { _slabStats.riserSkip++; return null; }
  // SLOPE GATE (Abs0lum's rule, 2026-08-30): a slab exists to make walking terrain even. If placing it
  // would leave ANY cardinal neighbour's walking plane more than half a block BELOW the new slab top,
  // the slab is refused — no accommodating downhill. Diagonals exempt by ruling. Plane arithmetic in
  // half-blocks: h2 = 2*surfY + (slab ? 1 : 2); the new slab tops out at 2*c0.y + 3.
  for (const [gx, gz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
    const gn = surf(x + gx, z + gz);
    if (!gn) { _slabStats.slopeSkip++; return null; }
    const h2n = 2 * gn.y + (gn.ours ? 1 : 2);
    if (h2n < 2 * c0.y + 2) { _slabStats.slopeSkip++; return null; }
  }
  {
    let kin = false;
    for (const [dx, dz] of PW_SLAB_N8) {
      const nb = surf(x + dx, z + dz);
      if (nb && !nb.ours && nb.y === c0.y && nb.slabId === c0.slabId) { kin = true; break; }
    }
    if (!kin) { _slabStats.kinSkip++; return null; }
  }
  for (const [pa, pb] of PW_SLAB_AXES) {
    const A = surf(x + pa[0], z + pa[1]), B = surf(x + pb[0], z + pb[1]);
    if (!A || !B || A.lava || B.lava) continue;
    if (Math.max(A.y, c0.y, B.y) - Math.min(A.y, c0.y, B.y) <= 1) return { sy, slabId: c0.slabId };
  }
  _slabStats.spanSkip++;
  return null;
}

// GVAR SEED — position-derived so a reload can never change the answer, and taken from the GROUND COLUMN
// BENEATH the slab rather than the slab's own cell, so the slab inherits the variant of the block it is
// completing. That is what makes a rise read as one continuous surface stepping upward.
// How many authored variants each slab family actually has. Needed because the mosaic must be sized to
// the family, not to a fixed 16.
const PW_SLAB_VARN = new Map(Object.entries({
  "pw:slab_sand":24, "pw:slab_red_sand":24,
  "pw:slab_dirt":16, "pw:slab_coarse_dirt":16, "pw:slab_gravel":16, "pw:slab_mud":16,
  "pw:slab_grass":16, "pw:slab_podzol":16, "pw:slab_mycelium":16,
  "pw:slab_stone":8, "pw:slab_andesite":8, "pw:slab_granite":8, "pw:slab_diorite":8,
  "pw:slab_calcite":8, "pw:slab_deepslate":8, "pw:slab_snow":8,
  "pw:slab_sandstone":8, "pw:slab_red_sandstone":8,
  "pw:slab_clay":1, "pw:slab_moss":1, "pw:slab_packed_ice":1, "pw:slab_path":1, "pw:slab_tuff":1
}));
// VARIANT LATTICE — replaces the square mosaic, which only behaved when the variant count was a perfect
// square. index = (x + 2*z) mod n. For every one of the eight neighbour offsets the delta (dx + 2*dz) is
// non-zero mod n at n = 8, 16 and 24, so NO two adjacent columns can ever share a variant. Slabs add a
// constant K = 4, which is likewise non-zero against all eight deltas AND against zero — so a slab differs
// from the block beneath it and from every block and slab around it. Verified over 51,200 adjacency pairs
// per family: zero collisions on all four relationships. n = 4 has no solution and falls back; n = 1 is
// one texture and cannot help itself.
const PW_VAR_B = 2, PW_VAR_K = 4;
function _varBlockIdx(x, z, n) { if (n <= 1) return 0; return (((x + PW_VAR_B * z) % n) + n) % n; }
function _varSlabIdx(x, z, n)  { if (n <= 1) return 0; return (((x + PW_VAR_B * z + PW_VAR_K) % n) + n) % n; }
function _gvarSeedRaw(x, y, z) {
  let h = (Math.imul(x, 374761393) ^ Math.imul(y, 668265263) ^ Math.imul(z, 2147483647)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return (h ^ (h >>> 16)) >>> 0;
}
function _slabPlaceAt(dim, x, z, q, H) {
  if (_slabDeny.has(`${x},${q.sy},${z}`)) { _slabStats.denySkip++; return false; }
  let cCell, cAbove;
  try { cCell = dim.getBlock({ x, y: q.sy, z }); cAbove = dim.getBlock({ x, y: q.sy + 1, z }); }
  catch { return false; }
  if (!_slabPassable(cCell) || !_slabPassable(cAbove)) return false;
  if (cCell.isAir !== true) { _slabVegLedger.set(`${x},${q.sy},${z}`, cCell.typeId); _slabStats.vegSaved++; }
  const _vegLift = PW_VEG_SEAT.get(cCell.typeId) || null;
  let _dblLift = null;
  if (PW_VEG_DOUBLE.has(cCell.typeId)) {
    _dblLift = PW_VEG_DOUBLE.get(cCell.typeId);
    _slabVegLedger.set(`${x},${q.sy},${z}`, cCell.typeId + "|D");
    try { if (cAbove && cAbove.typeId === cCell.typeId) cAbove.setPermutation(BlockPermutation.resolve("minecraft:air")); } catch (e) {}
  }
  let _snowH = -1;
  if (cCell.typeId === "minecraft:snow_layer") { try { _snowH = cCell.permutation.getState("height") | 0; } catch (e) { _snowH = 0; }
    _slabVegLedger.set(`${x},${q.sy},${z}`, "minecraft:snow_layer|" + _snowH); }
  // Sand and red sand carry 24 authored variants, more than one 16-value state can address, so those two
  // families get a second state and the seed is taken modulo 24 instead of 16. Nothing is unreachable.
  // Seeded from the GROUND COLUMN BENEATH so the slab inherits the variant of the block it completes.
  const nvar = PW_SLAB_VARN.get(q.slabId) || 16;
  // PHASE SHIFT (Abs0lum): the slab must not land on the same variant as the block beneath it —
  // "you never see two identical 5 square foot patches of grass right next to each other". Offsetting
  // the mosaic sample by a non-zero amount mod W guarantees a different cell every time, while keeping
  // the field deterministic and still clump-free.
  const idx = _varSlabIdx(x, z, nvar);
  const wide = (q.slabId === "pw:slab_sand" || q.slabId === "pw:slab_red_sand");
  const gv = idx % 16, gx = wide ? Math.floor(idx / 16) : 0;
  let perm;
  try {
    perm = wide
      ? BlockPermutation.resolve(q.slabId, { "minecraft:vertical_half": "bottom", "pw:gvar": gv, "pw:gvarx": gx })
      : BlockPermutation.resolve(q.slabId, { "minecraft:vertical_half": "bottom", "pw:gvar": gv });
  }
  catch (e1) {
    logErr("slabsmooth-resolve(gvar): " + (e1 && e1.message ? e1.message : e1));
    try { perm = BlockPermutation.resolve(q.slabId, { "minecraft:vertical_half": "bottom" }); }
    catch { try { perm = BlockPermutation.resolve(q.slabId); } catch { return false; } }
  }
  cCell.setPermutation(perm);
  try { if (cAbove && cAbove.typeId === "minecraft:snow_layer") { cAbove.setPermutation(BlockPermutation.resolve("minecraft:air")); _slabStats.snowCleared++; } } catch {}
  if (_snowH >= 0) {
    try { const _ca = dim.getBlock({ x, y: q.sy + 1, z });
      if (_ca && _ca.isAir) { _ca.setPermutation(BlockPermutation.resolve("pw:seated_snow", { "pw:layers": Math.min(8, _snowH + 1) })); _slabStats.snowLift++; }
    } catch (e) {}
  }
  if (_dblLift) {
    try { const _ca = dim.getBlock({ x, y: q.sy + 1, z }); if (_ca && _ca.isAir) { _ca.setPermutation(BlockPermutation.resolve(_dblLift)); _slabStats.vegLift++; } } catch (e) {}
  }
  if (_vegLift) {
    try {
      const _ca = dim.getBlock({ x, y: q.sy + 1, z });
      if (_ca && _ca.isAir) { _ca.setPermutation(BlockPermutation.resolve(_vegLift)); _slabStats.vegLift++; }
    } catch (e) {}
  }
  // REOPEN-ON-PLACE v1.3.148: a fresh slab gives its neighbourhood a second look — done-chunk
  // freezing was why no continuation could ever fire after the fact.
  {
    const _ckx = Math.floor(x / 16), _ckz = Math.floor(z / 16);
    for (let _cdx = -1; _cdx <= 1; _cdx++) for (let _cdz = -1; _cdz <= 1; _cdz++) {
      const _ck = `${_ckx + _cdx},${_ckz + _cdz}`;
      if (_slabDone.delete(_ck)) _slabPersistDirty = true;
      _slabChunkSeen.delete(_ck);
    }
  }
  _slabRegistry.set(`${x},${q.sy},${z}`, q.slabId);
  _slabStats.placed++;
  // The rise this slab completes is the only ground we ever convert — a two-block line at terrace
  // edges. Everything the pw: family cannot inherit from vanilla is confined to that hairline.
  try {
    for (const [dx, dz] of PW_SLAB_N8) {
      const n2 = H.get((x + dx) + "," + (z + dz));
      if (n2 && !n2.ours && n2.y === q.sy) { if (pwConvertRiser(dim, x + dx, q.sy, z + dz)) _slabStats.riserConv++; }
    }
  } catch {}
  H.set(x + "," + z, { y: q.sy, slabId: null, ours: true, lava: false });
  return true;
}

function* _slabSweep(dim, cx, cy, cz) {
  let cells = 0, placedThisCycle = 0;
  const yTop = Math.min(310, cy + PW_SLAB_Y_UP), yBot = Math.max(-60, cy - PW_SLAB_Y_DOWN);
  const H = new Map();
  const surf = (x, z) => {
    const k = x + "," + z;
    if (!H.has(k)) H.set(k, _slabColumnSurface(dim, x, z, yTop, yBot));
    return H.get(k);
  };
  for (const [ox, oz] of PW_SLAB_OFFSETS) {
    const x = cx + ox, z = cz + oz;
    if (++cells % 24 === 0) yield;
    if (placedThisCycle >= PW_SLAB_MAX_PLACE_PER_CYCLE) return;
    const ck = `${Math.floor(x/16)},${Math.floor(z/16)}`;
    if (_slabDone.has(ck)) { _slabStats.doneSkip++; continue; }
    try {
      const c0 = surf(x, z);
      if (!c0 || c0.lava || c0.ours) continue;
      { // Completion counts ONLY columns where ground was actually found. Previously a column counted the
        // moment it was visited, so flying more than three blocks above the terrain — which puts the whole
        // +-3 band in open air — marked chunks done with nothing judged, and they stayed closed after
        // landing. His log shows it exactly: considered=0, map_miss=0, done_chunks=1 on the first cycle.
        let seen = _slabChunkSeen.get(ck);
        if (!seen) { seen = new Set(); _slabChunkSeen.set(ck, seen); }
        seen.add((x & 15) * 16 + (z & 15));
        if (seen.size >= PW_SLAB_CHUNK_COLS && !_slabDone.has(ck)) { _slabDone.add(ck); _slabChunkSeen.delete(ck); _slabPersistDirty = true; }
      }
      if (!_slabBaselineOK(ck, x, z, c0.y)) { _slabStats.dugSkip++; continue; }
      if (!c0.slabId) { _slabStats.mapMiss++; continue; }
      _slabStats.considered++;
      _slabStats.hits.set(c0.slabId, (_slabStats.hits.get(c0.slabId) || 0) + 1);
      const q = _slabQualify(x, z, surf, dim);
      if (!q) continue;
      if (!_slabPlaceAt(dim, x, z, q, H)) continue;
      placedThisCycle++;
      if (!_slabStats.firstFired) {
        _slabStats.firstFired = true;
        try { console.warn(`[SLABSMOOTH] MARKER-S first slab placed: ${q.slabId} @ ${x},${q.sy},${z}`); } catch {}
      }
      // The lip is no longer walked inline. The seed is handed to a SEPARATE job so the player-centred
      // sweep always restarts nearest the player on schedule (Abs0lum's ruling) while the lip runs itself
      // out in parallel and fizzles when it finds no more candidates. Both write the same world ledgers.
      if (_slabLipQueue.length < PW_SLAB_LIP_QUEUE_CAP) _slabLipQueue.push({ dim, x, z, y0: q.sy });
    } catch (e) { logErr("slabsmooth: " + (e && e.message ? e.message : e)); }
  }
}
// FAILSAFE / REPAIR (Abs0lum's ruling): erroneous placements are acceptable only if they self-correct.
// Every slab we own is re-judged against the SAME qualifier that placed it, but with our own slabs made
// transparent so the ground beneath is what gets measured. Anything that no longer qualifies is pulled
// and its displaced vegetation put back. Runs every PW_SLAB_AUDIT_EVERY cycles.
const PW_SLAB_AUDIT_EVERY = 4;
function* _slabAuditJob(dim, cx, cy, cz) {
  const yTop = Math.min(310, cy + PW_SLAB_Y_UP + 2), yBot = Math.max(-60, cy - PW_SLAB_Y_DOWN - 2);
  const G = new Map();
  const surfG = (x, z) => {
    const k = x + "," + z;
    if (!G.has(k)) G.set(k, _slabColumnSurface(dim, x, z, yTop, yBot, true));
    return G.get(k);
  };
  let checked = 0, pulled = 0;
  for (const [key, slabId] of Array.from(_slabRegistry.entries())) {
    const p = key.split(",");
    const x = +p[0], y = +p[1], z = +p[2];
    if (Math.abs(x - cx) > PW_SLAB_RADIUS_XZ + 4 || Math.abs(z - cz) > PW_SLAB_RADIUS_XZ + 4) continue;
    if (Math.abs(y - cy) > PW_SLAB_Y_UP + 4) continue;
    if (++checked % 32 === 0) yield;
    try {
      const b = dim.getBlock({ x, y, z });
      if (!b || !_slabIsOurs(b.typeId)) { _slabRegistry.delete(key); continue; }
      if (_slabQualify(x, z, surfG, dim)) continue;              // still legitimate — leave it alone
      const veg = _slabVegLedger.get(key);
      let put = "minecraft:air";
      if (veg && veg.indexOf("|D") > 0) { /*RESTORE_DOUBLE*/
        const _did = veg.split("|")[0];
        try {
          b.setPermutation(BlockPermutation.resolve(_did, { upper_block_bit: false }));
          const _ub = b.dimension.getBlock({ x: b.location.x, y: b.location.y + 1, z: b.location.z });
          if (_ub) _ub.setPermutation(BlockPermutation.resolve(_did, { upper_block_bit: true }));
        } catch { try { b.setPermutation(BlockPermutation.resolve("minecraft:air")); } catch {} }
      } else if (veg && veg.indexOf("minecraft:snow_layer|") === 0) { /*RESTORE_SNOW*/
        try { b.setPermutation(BlockPermutation.resolve("minecraft:snow_layer", { height: (parseInt(veg.split("|")[1], 10) || 0) })); } catch { b.setPermutation(BlockPermutation.resolve("minecraft:air")); }
      } else {
        if (veg) { try { BlockPermutation.resolve(veg); put = veg; } catch {} }
        b.setPermutation(BlockPermutation.resolve(put));
      }
      try { const _ab = b.dimension.getBlock({ x: b.location.x, y: b.location.y + 1, z: b.location.z });
            if (_ab && typeof _ab.typeId === "string" && _ab.typeId.indexOf("pw:seated_") === 0) _ab.setPermutation(BlockPermutation.resolve("minecraft:air")); } catch (e) {}
      _slabRegistry.delete(key); _slabVegLedger.delete(key);
      G.delete(x + "," + z);
      pulled++; _slabStats.repaired++;
    } catch (e) { logErr("slabaudit: " + (e && e.message ? e.message : e)); }
  }
  if (pulled) { try { console.warn(`[SLABSMOOTH] repair: checked=${checked} pulled=${pulled}`); } catch {} }
}
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  try {
    if (ev.id !== "pw:slabaudit") return;
    const p = world.getAllPlayers()[0]; if (!p) return;
    const l = p.location;
    system.runJob(_slabAuditJob(p.dimension, Math.floor(l.x), Math.floor(l.y), Math.floor(l.z)));
  } catch (e) { logErr("slabaudit-cmd: " + (e && e.message ? e.message : e)); }
});
const _slabLipQueue = [];
const PW_SLAB_LIP_QUEUE_CAP = 64;
let _slabLipActive = false;
// Independent lip job: drains queued seeds, spreading through all eight directions from each and
// continuing while ANY neighbour still qualifies. Runs alongside the player sweep, shares the ledgers.
function* _slabLipJob() {
  let steps = 0;
  while (_slabLipQueue.length) {
    const seed = _slabLipQueue.shift();
    const dim = seed.dim;
    const yTop = Math.min(310, seed.y0 !== undefined ? seed.y0 : 320), yBot = -60;
    const H = new Map();
    const surf = (x, z) => {
      const k = x + "," + z;
      if (!H.has(k)) H.set(k, _slabColumnSurface(dim, x, z, Math.min(310, seed.y0 + PW_SLAB_Y_UP), Math.max(-60, seed.y0 - PW_SLAB_Y_DOWN), false));
      return H.get(k);
    };
    const queue = [[seed.x, seed.z]], seen = new Set([seed.x + "," + seed.z]);
    let walked = 0;
    while (queue.length && walked < PW_SLAB_LIP_MAX) {
      const [qx, qz] = queue.shift();
      for (const [dx, dz] of PW_SLAB_N8) {
        const nx = qx + dx, nz = qz + dz, nk = nx + "," + nz;
        if (seen.has(nk)) continue;
        seen.add(nk);
        if (++steps % 24 === 0) yield;
        // A lip could previously spread INTO a finished chunk and place there, defeating both the
        // done ledger and the baseline immunity. It now honours both, exactly like the main sweep.
        const nck = `${Math.floor(nx/16)},${Math.floor(nz/16)}`;
        if (_slabDone.has(nck)) continue;
        { const gs = surf(nx, nz); if (gs && !_slabBaselineOK(nck, nx, nz, gs.y)) { _slabStats.dugSkip++; continue; } }
        let q;
        try { q = _slabQualify(nx, nz, surf, dim); } catch (e) { logErr("sliplip: " + (e && e.message ? e.message : e)); continue; }
        if (!q) continue;
        try { if (!_slabPlaceAt(dim, nx, nz, q, H)) continue; } catch { continue; }
        walked++; _slabStats.lipPlaced++;
        queue.push([nx, nz]);
      }
    }
  }
  _slabLipActive = false;
}
function* _slabCycleJob(targets) {
  // targets: one entry per online player. yield* MUST live in a generator — the scheduler below is an
  // arrow function, and `yield` there parses as an identifier in sloppy mode but is a SyntaxError in a
  // module, which is exactly how v1.3.122 died on load.
  for (const t of targets) {
    try { yield* _slabSweep(t.dim, t.x, t.y, t.z); } catch (e) { logErr("slabsmooth-job: " + (e && e.message ? e.message : e)); }
    if (_slabStats.cycles % PW_SLAB_AUDIT_EVERY === 0) {
      try { yield* _slabAuditJob(t.dim, t.x, t.y, t.z); } catch (e) { logErr("slabaudit-job: " + (e && e.message ? e.message : e)); }
    }
  }
  _slabStats.cycles++;
  try { console.warn(`[SLABSMOOTH] c=${_slabStats.cycles} placed=${_slabStats.placed} snow=${_slabStats.snowLift} veg=${_slabStats.vegLift}/${_slabStats.vegSaved} key=${(system.currentTick - _forgeBeat) <= 200 ? "in" : "out"}`); } catch {}
  if (_slabStats.cycles <= 3 || _slabStats.cycles % 4 === 0) {
    try { console.warn(`[SLABSMOOTH] cycles=${_slabStats.cycles} placed=${_slabStats.placed} lip=${_slabStats.lipPlaced} lipq=${_slabLipQueue.length} dug_skips=${_slabStats.dugSkip} riser_conv=${_slabStats.riserConv} kin_skips=${_slabStats.kinSkip} repaired=${_slabStats.repaired} snow=${_slabStats.snowLift} veg=${_slabStats.vegLift}/${_slabStats.vegSaved} bridged=${_slabStats.bridged} slope_skips=${_slabStats.slopeSkip} edit_skips=${_slabStats.editSkip} edit_cols=${_slabEditCol.size} riser_skips=${_slabStats.riserSkip} span_skips=${_slabStats.spanSkip} cliff_skips=${_slabStats.cliffSkip} done_chunks=${_slabDone.size} deny=${_slabDeny.size} considered=${_slabStats.considered} map_miss=${_slabStats.mapMiss} | top: ${Array.from(_slabStats.hits.entries()).sort((a,b)=>b[1]-a[1]).slice(0,4).map(e=>e[0].replace("pw:slab_","")+"="+e[1]).join(",")}`); } catch (e) { try { console.warn("[SLABSMOOTH] banner-err: " + (e && e.message ? e.message : e)); } catch {} }
  }
  _slabJobActive = false;
  _slabJobStartTick = 0;
}
if (PW_SLAB_ENABLED) {
  system.runInterval(() => {
    // SLABFORGE GATE v1.3.150 (Abs0lum's ruling): the scanner runs ONLY while the PW-SlabForge key-pack
    // heartbeats. Remove that pack and smoothing halts within seconds at near-zero cost; every ledger
    // stays home in THIS pack, so re-adding the key resumes with full memory.
    if (system.currentTick - _forgeBeat > 200) {
      if (_forgeWasOn) { _forgeWasOn = false; try { _slabSaveLedgers(); } catch {} try { console.warn("[SLABFORGE] disengaged — scanner dormant (key pack absent)"); } catch {} }
      return;
    }
    if (!_forgeWasOn) { _forgeWasOn = true; try { console.warn("[SLABFORGE] engaged — smoothing active"); } catch {} }
    if (_slabJobActive) {
      if (_slabJobStartTick > 0 && system.currentTick - _slabJobStartTick > 600) {
        logErr("slabsmooth-watchdog: job active " + (system.currentTick - _slabJobStartTick) + " ticks — force-reset (wedge class)");
        _slabJobActive = false; _slabJobStartTick = 0;
      }
      return;
    }
    _slabJobActive = true;
    _slabJobStartTick = system.currentTick;
    if (!_slabSchedFired) { _slabSchedFired = true; try { console.warn(`[SLABSMOOTH] sched-fire #1 tick=${system.currentTick}`); } catch {} }
    try {
      const players = world.getAllPlayers();
      if (players.length === 0) { _slabJobActive = false; return; }
      _slabSaveLedgers();
      // PER-PLAYER SCANNERS, ONE SHARED WORLD LEDGER (his ruling): every online player becomes a target
      // in the same job; _slabDone / _slabDeny stay world-level so two scanners never redo each other's work.
      const targets = [];
      for (const p of players) {
        const pid = p.id;
        if (!_slabScanners.has(pid)) _slabScanners.set(pid, { last: 0 });
        _slabScanners.get(pid).last = system.currentTick;
        const l = p.location;
        targets.push({ dim: p.dimension, x: Math.floor(l.x), y: Math.floor(l.y), z: Math.floor(l.z) });
      }
      for (const k of Array.from(_slabScanners.keys())) {
        if (!players.some(pp => pp.id === k)) _slabScanners.delete(k);   // player left, drop their cursor
      }
      system.runJob(_slabCycleJob(targets));
      if (!_slabLipActive && _slabLipQueue.length) { _slabLipActive = true; system.runJob(_slabLipJob()); }
    } catch (e) { logErr("slabsmooth-sched: " + (e && e.message ? e.message : e)); _slabJobActive = false; }
  }, PW_SLAB_INTERVAL);
}


// ============================================================
// [PW-TREEGROW G2] Sapling -> baked structure growth engine — v1.3.105
// Interceptor per PW-TREE-GROWTH-ENGINE-DESIGN-v1. Additive module.
// ============================================================
const PW_GROW_ENABLED = true;
const PW_GROW_INTERVAL = 40;
const PW_GROW_DELAY = 2400;          // ~2 min base
const PW_GROW_JITTER = 1200;         // + up to 1 min, position-seeded
const PW_GROW_CHUNK_CAP = 6;
const PW_GROW_CAP_RESET = 12000;
const PW_GROW_CLEAR_TOL = 4;         // non-passable blocks tolerated in clearance volume
const PW_GROW_GROUND = new Set(["minecraft:grass_block","minecraft:grass","minecraft:dirt","minecraft:coarse_dirt","minecraft:podzol","minecraft:mycelium","minecraft:moss_block","minecraft:mud","minecraft:rooted_dirt"]);
// v1.3.209 T5 (D-C503): the pools are the T2 TEMPLATES (the P11 audit F9: pw:test_* existed nowhere). A sapling grows a
// YOUNG tree of its species (24 each); acacia / cherry / mangrove their 32; dark oak and pale oak their elders (their only
// templates). The root lands ON the sapling cell (F10: structureManager.place with the origin = sapling - rotated root).
const _pool = (stem, n) => Array.from({ length: n }, (_, i) => `pw:trees/${stem}_${String(i).padStart(2, "0")}`);
const PW_GROW_POOLS = new Map(Object.entries({
  "minecraft:oak_sapling":      _pool("oak_young", 24),
  "minecraft:birch_sapling":    _pool("birch_young", 24),
  "minecraft:spruce_sapling":   _pool("spruce_young", 24),
  "minecraft:jungle_sapling":   _pool("jungle_young", 24),
  "minecraft:acacia_sapling":   _pool("acacia", 32),
  "minecraft:dark_oak_sapling": _pool("dark_oak_elder", 32),
  "minecraft:cherry_sapling":   _pool("cherry", 32),
  "minecraft:pale_oak_sapling": _pool("pale_oak_elder", 32),
  "minecraft:mangrove_propagule":_pool("mangrove", 32)
}));
const PW_GROW_ROT = ["None", "Rotate90", "Rotate180", "Rotate270"];
const PW_GROW_KEY = "pw:treegrow";    // the pending saplings survive a reload (was memory-only: lost on every rejoin)
// the registry on disk: one dynamic property holds at most 32,767 chars (the CIVITAS state law, D-C499) — 400 entries of
// ["minecraft:mangrove_propagule","minecraft:overworld",x,y,z,left] could pass it, so entries are saved COMPACT (type and
// dimension as indexes into the two tables, ~25 chars each: 400 entries = ~10,000 chars) and split over numbered chunks
// pw:treegrow:0 .. :n of 30,000 chars should the cap ever grow. The old long form (an array of arrays with string ids)
// still loads (a world saved by 1.3.209).
const PW_GROW_TYPES = [...PW_GROW_POOLS.keys()];      // a Map: Object.keys() was [] (D-C511: every type saved as -1, nothing restored)
const PW_GROW_DIMS = ["minecraft:overworld", "minecraft:nether", "minecraft:the_end"];
const PW_GROW_CHUNK = 30000;
function _growSave() {
  try {
    const arr = [...(_growRegistry.values())].slice(0, 400).map((i) => [PW_GROW_TYPES.indexOf(i.type), PW_GROW_DIMS.indexOf(i.dim), i.x, i.y, i.z, i.due - system.currentTick]);
    const text = JSON.stringify(arr);
    const parts = [];
    for (let k = 0; k < text.length; k += PW_GROW_CHUNK) parts.push(text.slice(k, k + PW_GROW_CHUNK));
    world.setDynamicProperty(PW_GROW_KEY, undefined);
    world.setDynamicProperty(PW_GROW_KEY + ":n", parts.length);
    for (let k = 0; k < parts.length; k++) world.setDynamicProperty(`${PW_GROW_KEY}:${k}`, parts[k]);
    // drop stale chunks beyond the new count (the registry shrank)
    for (let k = parts.length; k < parts.length + 4; k++) { try { if (world.getDynamicProperty(`${PW_GROW_KEY}:${k}`) !== undefined) world.setDynamicProperty(`${PW_GROW_KEY}:${k}`, undefined); } catch {} }
  } catch (e) { logErr("treegrow-save: " + (e && e.message ? e.message : e)); }
}
function _growLoad() {
  try {
    let raw = world.getDynamicProperty(PW_GROW_KEY);                 // the 1.3.209 single property
    if (typeof raw !== "string") {
      const n = world.getDynamicProperty(PW_GROW_KEY + ":n");
      if (typeof n !== "number" || n <= 0) return 0;
      raw = "";
      for (let k = 0; k < n; k++) { const part = world.getDynamicProperty(`${PW_GROW_KEY}:${k}`); if (typeof part !== "string") return 0; raw += part; }
    }
    let count = 0;
    for (const [t, d, x, y, z, left] of JSON.parse(raw)) {
      const type = typeof t === "number" ? PW_GROW_TYPES[t] : t, dim = typeof d === "number" ? PW_GROW_DIMS[d] : d;
      if (!type || !dim) continue;
      _growRegistry.set(`${dim}|${x},${y},${z}`, { type, dim, x, y, z, due: system.currentTick + Math.max(40, left | 0) }); count++;
    }
    return count;
  } catch (e) { logErr("treegrow-load-registry: " + (e && e.message ? e.message : e)); return 0; }
}
/** the structure origin that puts the template's ROOT on the sapling cell after `rot` quarter turns (the rotation law) */
function _growOrigin(sap, tpl, rot) {
  const [sx, , sz] = tpl.size, [rx, ry, rz] = tpl.root;
  let ox, oz;
  if (rot === 1) { ox = sz - 1 - rz; oz = rx; } else if (rot === 2) { ox = sx - 1 - rx; oz = sz - 1 - rz; } else if (rot === 3) { ox = rz; oz = sx - 1 - rx; } else { ox = rx; oz = rz; }
  return { x: sap.x - ox, y: sap.y - ry, z: sap.z - oz };
}
const _growRegistry = new Map();
const _growChunkCount = new Map();
const _growStats = { cycles:0, grown:0, pending:0, deniedGround:0, deniedSpace:0, capped:0, poolMiss:0, firstFired:false };
try { console.warn(`[TREEGROW] BOOT v${PW_BUILD} — interval=${PW_GROW_INTERVAL}t delay=${PW_GROW_DELAY}t cap=${PW_GROW_CHUNK_CAP}/chunk`); } catch {}
function _growHash(x, y, z) { let h = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791); return Math.abs(h); }

// RAMP VARIANT LATTICE (v1.3.168): a placed ramp takes pw:var = (x + 2z) mod 8 so eight variants tile without a grid
world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try {
    const b = ev.block; if (!b.typeId.startsWith("pw:ramp_")) return;
    const v = ((b.location.x + 2 * b.location.z) % 8 + 8) % 8;
    system.run(() => { try { b.setPermutation(b.permutation.withState("pw:var", v)); } catch (e) {} });
  } catch (e) {}
});
// SNOW ACCUMULATION (v1.3.174) — deterministic sweep: each pass walks one 24-wide strip of the 24x24 area round each player (6 strips,
// 4 wide each -> the whole area every 6 passes). Our slabs, ramps and seated stairs gain pw:snow (0-4, 2px per level) while vanilla
// snow_layer forms on neighbouring full blocks and lose it as that melts; a vanilla layer above one of ours folds into its cap; a layer
// floating above any other partial block (vanilla stairs, bottom slabs, posts) is removed.
const PW_SNOW_SCAN_T = 100, PW_SNOW_HALF = 12, PW_SNOW_STRIP = 4;
let _snowStrip = 0;
function _isSnowable(b) { return !!b && (b.typeId.startsWith("pw:slab_") || b.typeId.startsWith("pw:ramp_") || b.typeId === "pw:frame_post" || (b.typeId.startsWith("pw:seated_") && b.typeId.endsWith("_stairs"))); }
function _isPartial(b) { const id = b.typeId; return id.endsWith("_stairs") || (id.endsWith("_slab") && id.startsWith("minecraft:")) || id === "pw:frame_post" || id.startsWith("pw:seated_"); }
function _neighbourSnow(dim, x, y, z) {
  // vanilla matching: returns the deepest neighbouring vanilla layer as a level (1..8), 0 when none — ours never exceeds it
  let best = 0;
  for (const [dx, dz] of [[1,0],[-1,0],[0,1],[0,-1]]) {
    for (const dy of [0, 1]) { try { const nb = dim.getBlock({ x: x + dx, y: y + dy, z: z + dz }); if (nb && nb.typeId === "minecraft:snow_layer") { let h = 0; try { h = nb.permutation.getState("height") | 0; } catch (e) {} best = Math.max(best, h + 1); break; } } catch (e) {} }
  }
  return best;
}
system.runInterval(() => {
  try {
    const strip = _snowStrip; _snowStrip = (_snowStrip + 1) % Math.ceil(2 * PW_SNOW_HALF / PW_SNOW_STRIP);
    for (const p of world.getAllPlayers()) {
      const dim = p.dimension, px = Math.floor(p.location.x), py = Math.floor(p.location.y), pz = Math.floor(p.location.z);
      const x0 = px - PW_SNOW_HALF + strip * PW_SNOW_STRIP;
      for (let x = x0; x < x0 + PW_SNOW_STRIP; x++) for (let z = pz - PW_SNOW_HALF; z < pz + PW_SNOW_HALF; z++) {
        for (let y = py + 6; y >= py - 6; y--) {
          let b; try { b = dim.getBlock({ x, y, z }); } catch (e) { break; }
          if (!b || b.isAir) continue;
          if (b.typeId === "minecraft:snow_layer") {
            let under; try { under = dim.getBlock({ x, y: y - 1, z }); } catch (e) {}
            if (!under) break;
            if (_isSnowable(under)) {
              let hgt = 0; try { hgt = b.permutation.getState("height") | 0; } catch (e) {}
              const lvl = under.permutation.getState("pw:snow") | 0; const want = Math.max(lvl, Math.min(4, hgt + 1));
              try { b.setType("minecraft:air"); under.setPermutation(under.permutation.withState("pw:snow", want)); } catch (e) {}
            } else if (under.typeId.startsWith("minecraft:") && under.typeId.endsWith("_stairs")) {   // vanilla stair: overlay cap in this cell
              let ud = false, f = 0; try { ud = !!under.permutation.getState("upside_down_bit"); f = under.permutation.getState("weirdo_direction") | 0; } catch (e) {}
              let hgt = 0; try { hgt = b.permutation.getState("height") | 0; } catch (e) {}
              try { if (ud) b.setType("minecraft:air"); else b.setPermutation(BlockPermutation.resolve("pw:snowcap_stairs", { "pw:facing": f, "pw:level": Math.min(4, hgt + 1) })); } catch (e) {}
            } else if (under.typeId.startsWith("minecraft:") && under.typeId.endsWith("_slab")) {     // vanilla slab: overlay cap dropped to its top
              let bottom = true; try { const vh = under.permutation.getState("minecraft:vertical_half"); if (vh !== undefined) bottom = vh === "bottom"; } catch (e) {}
              let hgt = 0; try { hgt = b.permutation.getState("height") | 0; } catch (e) {}
              try { if (bottom) b.setPermutation(BlockPermutation.resolve("pw:snowcap_slab", { "pw:level": Math.min(4, hgt + 1) })); } catch (e) {}
            } else if (_isPartial(under)) { try { b.setType("minecraft:air"); } catch (e) {} }
            break;
          }
          if (b.typeId === "pw:snowcap_stairs" || b.typeId === "pw:snowcap_slab") {                 // overlay caps grow, melt, and vanish with their support
            let under; try { under = dim.getBlock({ x, y: y - 1, z }); } catch (e) {}
            const ok = under && under.typeId.startsWith("minecraft:") && ((b.typeId === "pw:snowcap_stairs" && under.typeId.endsWith("_stairs")) || (b.typeId === "pw:snowcap_slab" && under.typeId.endsWith("_slab")));
            if (!ok) { try { b.setType("minecraft:air"); } catch (e) {} break; }
            const lvl = b.permutation.getState("pw:level") | 0; const n = _neighbourSnow(dim, x, y - 1, z);
            const target = Math.min(4, n);
            if (lvl < target && Math.random() < 0.5) { try { b.setPermutation(b.permutation.withState("pw:level", lvl + 1)); } catch (e) {} }
            else if (lvl > target && Math.random() < 0.35) { try { if (lvl > 1) b.setPermutation(b.permutation.withState("pw:level", lvl - 1)); else b.setType("minecraft:air"); } catch (e) {} }
            break;
          }
          if (!_isSnowable(b)) break;
          let above; try { above = dim.getBlock({ x, y: y + 1, z }); } catch (e) {}
          if (!above || !(above.isAir || (b.typeId === "pw:frame_post" && above.typeId === "pw:frame_post"))) break;
          const lvl = b.permutation.getState("pw:snow") | 0; const n = _neighbourSnow(dim, x, y, z);
          let want = lvl;
          const target = Math.min(4, n);
          if (lvl < target && Math.random() < 0.5) want = lvl + 1;
          else if (lvl > target && Math.random() < 0.35) want = lvl - 1;
          if (want !== lvl) { try { b.setPermutation(b.permutation.withState("pw:snow", want)); } catch (e) {} }
          break;
        }
      }
    }
  } catch (e) {}
}, PW_SNOW_SCAN_T);
// SEATED STAIRS (v1.3.158) — a stair placed on ANY bottom slab (pw:slab_* or vanilla *_slab, bottom half) becomes pw:seated_<stair>,
// geometry and collision dropped 8px so it rests on the slab. Upside-down stairs are left alone. Structures-only doctrine (D-C126).
function _isBottomSlab(b) {
  if (!b) return false;
  const id = b.typeId;
  if (id.startsWith("pw:slab_")) return true;
  if (id.startsWith("minecraft:") && id.endsWith("_slab")) {
    try { const vh = b.permutation.getState("minecraft:vertical_half"); if (vh !== undefined) return vh === "bottom"; } catch (e) {}
    try { const ts = b.permutation.getState("top_slot_bit"); if (ts !== undefined) return ts === false; } catch (e) {}
    return true;
  }
  return false;
}
world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try {
    const b = ev.block, id = b.typeId;
    if (!id.startsWith("minecraft:") || !id.endsWith("_stairs")) return;
    let ud = false; try { ud = !!b.permutation.getState("upside_down_bit"); } catch (e) {}
    if (ud) return;
    const below = b.dimension.getBlock({ x: b.location.x, y: b.location.y - 1, z: b.location.z });
    if (!_isBottomSlab(below) && !(below && below.typeId.startsWith("pw:seated_") && below.typeId.endsWith("_stairs"))) return;   // chains: a stair on a seated stair seats too
    let f = 0; try { f = b.permutation.getState("weirdo_direction") | 0; } catch (e) {}
    const seated = "pw:seated_" + id.slice(10);
    system.run(() => { try { b.setPermutation(BlockPermutation.resolve(seated, { "pw:facing": f })); } catch (e) { logErr("seated-stairs: " + e); } });
  } catch (e) {}
});
world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try {
    const b = ev.block;
    if (!PW_GROW_POOLS.has(b.typeId)) return;
    const k = `${b.dimension.id}|${b.location.x},${b.location.y},${b.location.z}`;
    _growRegistry.set(k, { type: b.typeId, dim: b.dimension.id, x: b.location.x, y: b.location.y, z: b.location.z,
      due: system.currentTick + PW_GROW_DELAY + (_growHash(b.location.x, b.location.y, b.location.z) % PW_GROW_JITTER) });
    _growSave();
  } catch (e) { logErr("treegrow-place: " + (e && e.message ? e.message : e)); }
});
// /scriptevent pw:treegrow plant <x> <y> <z> [sapling id] — a probe / test tool: the sapling block is set and registered as due now
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:treegrow") return;
  try {
    const [cmd, xs, ys, zs, idArg] = (ev.message || "").trim().split(/\s+/);
    const dim = (ev.sourceEntity && ev.sourceEntity.dimension) || world.getDimension("overworld");
    if (cmd === "plant") {
      const x = Number(xs), y = Number(ys), z = Number(zs), id = idArg || "minecraft:oak_sapling";
      dim.getBlock({ x, y, z })?.setType(id);
      _growRegistry.set(`${dim.id}|${x},${y},${z}`, { type: id, dim: dim.id, x, y, z, due: system.currentTick });
      _growSave();
      console.warn(`[TREEGROW] planted ${id} at ${x},${y},${z} (due now)`);
    } else if (cmd === "status") {
      console.warn(`[TREEGROW] ${JSON.stringify({ ..._growStats, pending: _growRegistry.size })}`);
    }
  } catch (e) { logErr("treegrow-tool: " + (e && e.message ? e.message : e)); }
});
system.runTimeout(() => { const n = _growLoad(); if (n) { try { console.warn(`[TREEGROW] ${n} pending sapling(s) restored`); } catch {} } }, 20);
if (PW_GROW_ENABLED) {
  system.runInterval(() => {
    try {
      _growStats.cycles++;
      _growStats.pending = _growRegistry.size;
      const now = system.currentTick;
      for (const [k, info] of _growRegistry) {
        if (now < info.due) continue;
        let dim;
        try { dim = world.getDimension(info.dim); } catch { continue; }
        let sap;
        try { sap = dim.getBlock({ x: info.x, y: info.y, z: info.z }); } catch { continue; }
        if (!sap) continue;                       // unloaded — stay pending
        if (sap.typeId !== info.type) { _growRegistry.delete(k); continue; }  // broken/changed
        let ground;
        try { ground = dim.getBlock({ x: info.x, y: info.y - 1, z: info.z }); } catch { continue; }
        if (!ground || !PW_GROW_GROUND.has(ground.typeId)) { _growStats.deniedGround++; _growRegistry.delete(k); continue; }
        const ck = `${info.dim}|${Math.floor(info.x / 16)},${Math.floor(info.z / 16)}`;
        const cc = _growChunkCount.get(ck) || 0;
        if (cc >= PW_GROW_CHUNK_CAP) { _growStats.capped++; continue; }
        const pool = PW_GROW_POOLS.get(info.type) || [];
        if (pool.length === 0) { _growStats.poolMiss++; _growRegistry.delete(k); _growSave(); continue; }
        const _mix = (h) => ((h ^ (h >>> 7) ^ (h >>> 13) ^ (h >>> 19)) >>> 0);   // aligned coordinates (multiples of 4) made the raw hash ≡ 0 mod 4 (growprobe: 9 trees all "north")
        const structName = pool[_mix(_growHash(info.x, info.y, info.z)) % pool.length];
        const rotIdx = _mix(_growHash(info.z + 11, info.x + 7, info.y + 3)) % 4, rot = PW_GROW_ROT[rotIdx];
        const tpl = templateCells(structName);
        if (!tpl) { _growStats.poolMiss++; logErr("treegrow: template missing " + structName); _growRegistry.delete(k); _growSave(); continue; }
        const origin = _growOrigin({ x: info.x, y: info.y, z: info.z }, tpl, rotIdx);
        // clearance: the template's own cells (rotated about the root) must find air / plants / leaves — at most PW_GROW_CLEAR_TOL solid blocks
        let blocked = 0;
        try {
          const dir = ["north", "east", "south", "west"][rotIdx];
          for (const c of tpl.logs.concat(tpl.leaves)) {
            if (c[1] === 0) continue;                                  // the root cell is the sapling itself
            const [ox, oz] = turnOffset(c[0], c[2], dir);
            const bb = dim.getBlock({ x: info.x + ox, y: info.y + c[1], z: info.z + oz });
            if (bb && !_slabPassable(bb) && !bb.typeId.includes("leaves")) blocked++;
            if (blocked > PW_GROW_CLEAR_TOL) break;
          }
        } catch {}
        if (blocked > PW_GROW_CLEAR_TOL) { _growStats.deniedSpace++; continue; }   // stays pending: space may clear
        try {
          world.structureManager.place(structName, dim, origin, { rotation: rot, includeEntities: false });
          _growChunkCount.set(ck, cc + 1);
          _growRegistry.delete(k);
          _growSave();
          _growStats.grown++;
          if (!_growStats.firstFired) {
            _growStats.firstFired = true;
            try { console.warn(`[TREEGROW] MARKER-T first growth: ${structName} @ ${info.x},${info.y},${info.z} rot=${rot} origin ${origin.x},${origin.y},${origin.z}`); } catch {}
          }
        } catch (e) {
          _growStats.poolMiss++;
          logErr("treegrow-place(" + structName + "): " + (e && e.message ? e.message : e));
          _growRegistry.delete(k); _growSave();
        }
      }
      if (_growStats.cycles % 8 === 0 && (_growRegistry.size > 0 || _growStats.grown > 0 || _growStats.poolMiss > 0)) {
        try { console.warn(`[TREEGROW] cycles=${_growStats.cycles} grown=${_growStats.grown} pending=${_growRegistry.size} denied_ground=${_growStats.deniedGround} denied_space=${_growStats.deniedSpace} capped=${_growStats.capped} pool_miss=${_growStats.poolMiss}`); } catch {}
      }
    } catch (e) { logErr("treegrow-cycle: " + (e && e.message ? e.message : e)); }
  }, PW_GROW_INTERVAL);
  system.runInterval(() => { _growChunkCount.clear(); }, PW_GROW_CAP_RESET);
}


// ---- /scriptevent pw:slabclear — wipe every pw:slab_* nearby and reopen those chunks ----
function* _slabClearJob(dim, cx, cy, cz, R) {
  let removed = 0, cells = 0, reopened = 0;
  const AIR = BlockPermutation.resolve("minecraft:air");
  const chunks = new Set();
  for (let x = cx - R; x <= cx + R; x++) {
    for (let z = cz - R; z <= cz + R; z++) {
      for (let y = Math.max(-60, cy - 40); y <= Math.min(310, cy + 40); y++) {
        if (++cells % 400 === 0) yield;
        let b; try { b = dim.getBlock({ x, y, z }); } catch { continue; }
        if (!b || typeof b.typeId !== "string" || b.typeId.indexOf("pw:slab_") !== 0) continue;
        try { b.setPermutation(AIR); removed++; } catch {}
        _slabRegistry.delete(`${x},${y},${z}`);
        _slabDeny.delete(`${x},${y},${z}`);
        chunks.add(`${Math.floor(x/16)},${Math.floor(z/16)}`);
      }
    }
  }
  for (const k of chunks) { if (_slabDone.delete(k)) reopened++; _slabChunkSeen.delete(k); }
  _slabPersistDirty = true; _slabSaveLedgers();
  try { console.warn(`[SLABSMOOTH] slabclear: removed=${removed} chunks_reopened=${reopened} radius=${R}`); } catch {}
}
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  try {
    if (ev.id !== "pw:slabclear") return;
    const p = world.getAllPlayers()[0]; if (!p) return;
    const R = Math.max(8, Math.min(96, parseInt(ev.message, 10) || 48));
    const l = p.location;
    console.warn(`[SLABSMOOTH] slabclear starting radius=${R} ...`);
    system.runJob(_slabClearJob(p.dimension, Math.floor(l.x), Math.floor(l.y), Math.floor(l.z), R));
  } catch (e) { logErr("slabclear: " + (e && e.message ? e.message : e)); }
});


// ============================ AMBIENT LEAF DRIFT ============================
// Better Foliage drops leaf particles that react to wind and blow harder in storms. Motion in the AIR
// reads as wind far more convincingly than motion in a texture, and it costs no atlas memory. We sample
// leaf blocks near each player, spawn from the UNDERSIDE of a canopy, and scale speed and tumble with the
// weather. Uses pw:leaf_drift — the falling-tree burst keeps its own pw:leaf_fall untouched.
const PW_LEAF_DRIFT_INTERVAL = 40;      // 2s
const PW_LEAF_DRIFT_RADIUS = 22;
const PW_LEAF_DRIFT_SAMPLES = 26;
const PW_LEAF_DRIFT_MAX = 4;            // emissions per player per beat
function _leafWind(dim) {
  // v1.3.186: the weather comes from pw_weather.js (world.afterEvents.weatherChange, stable API). The old
  // dim.getWeather() is beta-only, so on our stable pin it was always missing and leaves drifted at the
  // calm speed through every storm.
  let w = "Clear";
  try { w = weatherIn(dim); } catch {}
  if (w === "Thunder") return 1.6;
  if (w === "Rain") return 0.8;
  return 0.15;
}
function _isLeafId(tid) {
  if (typeof tid !== "string") return false;
  return tid.indexOf("leaves") > 0;
}
system.runInterval(() => {
  let players;
  try { players = world.getAllPlayers(); } catch { return; }
  for (const p of players) {
    try {
      const dim = p.dimension, l = p.location;
      const wind = _leafWind(dim);
      let spawned = 0;
      for (let i = 0; i < PW_LEAF_DRIFT_SAMPLES && spawned < PW_LEAF_DRIFT_MAX; i++) {
        const x = Math.floor(l.x) + Math.floor((Math.random() * 2 - 1) * PW_LEAF_DRIFT_RADIUS);
        const z = Math.floor(l.z) + Math.floor((Math.random() * 2 - 1) * PW_LEAF_DRIFT_RADIUS);
        for (let dy = 12; dy >= -2; dy--) {
          const y = Math.floor(l.y) + dy;
          let b; try { b = dim.getBlock({ x, y, z }); } catch { break; }
          if (!b || !_isLeafId(b.typeId)) continue;
          let below; try { below = dim.getBlock({ x, y: y - 1, z }); } catch { break; }
          if (!below || below.isAir !== true) break;     // only shed where a leaf hangs over open air
          try {
            const mv = new MolangVariableMap();
            mv.setFloat("wind", wind);
            mv.setFloat("pick", Math.floor(Math.random() * 4));
            mv.setFloat("sz", (Math.random() - 0.5) * 0.03);
            dim.spawnParticle("pw:leaf_drift", { x: x + 0.5, y: y - 0.2, z: z + 0.5 }, mv);
            spawned++;
          } catch {}
          break;
        }
      }
    } catch (e) { logErr("leafdrift: " + (e && e.message ? e.message : e)); }
  }
}, PW_LEAF_DRIFT_INTERVAL);
