// pw_vine.js — 3D VINES (BP-02 1.3.203; his 09:30 Q1 = a, 11:23 Q5/Q6 = c).
// Vanilla vines are swapped ONCE to pw:vine (Patrix 3D leaf-card models): the same attachment sides (vanilla
// vine_direction_bits copied into pw:bits) and a texture variant picked from the position (pw:v). Swapped vines no
// longer spread (custom blocks do not grow) — accepted (Q1 = a). pw:bits and pw:v are never changed after the swap.
// MOTION (custom blocks get no engine motion): the leaves sway gently all the time (wind flipbooks, RP side) and RUSTLE
// when a player walks into them: the touched vine and its neighbours (3 x 3 x 3) switch pw:r to true -> the rustle
// flipbooks; RUSTLE_TICKS after the last touch pw:r goes back to false.
// CLIMBING (custom blocks have no climbable component): while a player stands in a pw:vine cell (feet or head)
//   holding JUMP  -> pushed up (climb, ~vanilla ladder speed)
//   SNEAKING      -> held in place (vertical motion cancelled)
//   otherwise     -> slow descent with no fall damage (slow_falling, renewed while inside)
import { world, system, BlockPermutation, BlockVolume } from "@minecraft/server";

const VINE = "minecraft:vine";
const PW_VINE = "pw:vine";
const VARIANTS = 12;
const SCAN_EVERY_TICKS = 100, SCAN_RADIUS = 24, SCAN_HALF_HEIGHT = 16, BOX = 16, MAX_SWAPS_PER_STEP = 64;
const CLIMB_EVERY_TICKS = 2;
const CLIMB_UP = 0.22;          // vertical knockback per 2 ticks while jumping
const VINE_TOUCH_RUSTLE = false;  // 1004b: his ruling — off
const RUSTLE_TICKS = 40;        // 2 s of rustle after the last touch
const RUSTLE_CHECK_TICKS = 10;

function variantAt(loc) {
  // stable position hash -> 0..11 (same block always gets the same variant)
  const h = (Math.imul(Math.floor(loc.x), 73856093) ^ Math.imul(Math.floor(loc.y), 19349663) ^ Math.imul(Math.floor(loc.z), 83492791)) >>> 0;
  return h % VARIANTS;
}

function swapOnce(block) {
  if (!block || block.typeId !== VINE) return false;
  let bits = 0;
  try { bits = block.permutation.getState("vine_direction_bits") ?? 0; } catch { bits = 0; }
  block.setPermutation(BlockPermutation.resolve(PW_VINE, { "pw:bits": bits, "pw:v": variantAt(block.location), "pw:r": false }));
  return true;
}

world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try { swapOnce(ev.block); } catch (e) { console.warn(`[pw_vine] place swap failed: ${e}`); }
});

let busy = false;
function* scanJob(players) {
  let swaps = 0;
  for (const p of players) {
    let dim, c;
    try { dim = p.dimension; c = p.location; } catch { continue; }
    const r = dim.heightRange;
    const y0 = Math.max(r.min, Math.floor(c.y) - SCAN_HALF_HEIGHT), y1 = Math.min(r.max - 1, Math.floor(c.y) + SCAN_HALF_HEIGHT);
    const x0 = Math.floor(c.x) - SCAN_RADIUS, x1 = Math.floor(c.x) + SCAN_RADIUS;
    const z0 = Math.floor(c.z) - SCAN_RADIUS, z1 = Math.floor(c.z) + SCAN_RADIUS;
    for (let bx = x0; bx <= x1; bx += BOX) for (let bz = z0; bz <= z1; bz += BOX) for (let by = y0; by <= y1; by += BOX) {
      let list;
      try {
        list = dim.getBlocks(new BlockVolume({ x: bx, y: by, z: bz },
          { x: Math.min(bx + BOX - 1, x1), y: Math.min(by + BOX - 1, y1), z: Math.min(bz + BOX - 1, z1) }), { includeTypes: [VINE] }, true);
      } catch { yield; continue; }
      for (const loc of list.getBlockLocationIterator()) {
        try { if (swapOnce(dim.getBlock(loc))) swaps++; } catch {}
        if (swaps >= MAX_SWAPS_PER_STEP) { swaps = 0; yield; }
      }
      yield;
    }
  }
  busy = false;
}
system.runInterval(() => {
  if (busy) return;
  const players = world.getAllPlayers();
  if (!players.length) return;
  busy = true;
  system.runJob(scanJob(players));
}, SCAN_EVERY_TICKS);

// ---- rustle
const rustling = new Map();     // "dim|x|y|z" -> { dim, loc, until }

function setRustle(block, on) {
  try {
    if (!block || block.typeId !== PW_VINE) return;
    if (block.permutation.getState("pw:r") === on) return;
    block.setPermutation(block.permutation.withState("pw:r", on));
  } catch {}
}

function touchAround(p) {
  const l = p.location, dim = p.dimension, now = system.currentTick;
  const cx = Math.floor(l.x), cy = Math.floor(l.y), cz = Math.floor(l.z);
  for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 2; dy++) for (let dz = -1; dz <= 1; dz++) {
    const loc = { x: cx + dx, y: cy + dy, z: cz + dz };
    let b;
    try { b = dim.getBlock(loc); } catch { continue; }
    if (!b || b.typeId !== PW_VINE) continue;
    setRustle(b, true);
    rustling.set(`${dim.id}|${loc.x}|${loc.y}|${loc.z}`, { dim, loc, until: now + RUSTLE_TICKS });
  }
}

system.runInterval(() => {
  const now = system.currentTick;
  for (const [k, r] of rustling) {
    if (now < r.until) continue;
    try { setRustle(r.dim.getBlock(r.loc), false); } catch {}
    rustling.delete(k);
  }
}, RUSTLE_CHECK_TICKS);

// ---- climbing (+ touch -> rustle)
function inVine(p) {
  const l = p.location;
  for (const dy of [0, 1]) {
    try {
      const b = p.dimension.getBlock({ x: Math.floor(l.x), y: Math.floor(l.y) + dy, z: Math.floor(l.z) });
      if (b && b.typeId === PW_VINE) return true;
    } catch {}
  }
  return false;
}

system.runInterval(() => {
  for (const p of world.getAllPlayers()) {
    try {
      if (!inVine(p)) continue;
      if (VINE_TOUCH_RUSTLE) touchAround(p);   // 1004b (his 17:38): no quick shake on contact; the wind sway (RP flipbooks) stays
      const vy = p.getVelocity().y;
      if (p.isJumping) {
        p.applyKnockback({ x: 0, z: 0 }, CLIMB_UP);
      } else if (p.isSneaking) {
        if (Math.abs(vy) > 0.001) p.applyKnockback({ x: 0, z: 0 }, -vy);
      } else {
        p.addEffect("slow_falling", 6, { amplifier: 0, showParticles: false });
      }
    } catch {}
  }
}, CLIMB_EVERY_TICKS);
