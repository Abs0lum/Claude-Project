// pw_planks.js — PLANK GRIDS (BP-02 1.3.204; his 00:07 / 00:53 rulings + 13:31 neighbour rule, 10-02).
// Every vanilla plank block of the 11 Patrix species becomes pw:<species>_planks_grid, whose three states
// pw:gx / pw:gy / pw:gz say which cell of Patrix's 4 x 4 'repeat' grid it shows (the block's permutations map each
// face to one of the 16 tiles), so neighbouring planks continue the boards on every face.
//
// NEIGHBOUR RULE (his 13:31): a NEW plank continues the pattern of an OLDER grid plank beside it — v2 sits east of
// v1, west of v3, and so on, on all three axes. The older block never changes; the new block adapts to it.
// Neighbour priority when several touch: below, north, west, south, east, above (first found wins). With no grid
// plank beside it, a plank starts the pattern from its world position (position mod 4), so a lone plank is still
// predictable. To shift a floor's pattern: build it offset, then remove the extra pieces.
// SET ONCE (his rule, like the leaves): a block is set exactly once — when a player places a vanilla plank, or when
// the scanner finds one near a player. A grid block is never matched again (the scanner only looks for vanilla
// planks), so placing a plank next to it never changes it.
// STRUCTURES: /structure load does not turn our custom states with the structure, so a rotated building would show
// its boards running the wrong way. The CIVITAS placer calls reflowPlanks(dim, min, max) ONCE right after loading a
// structure: every grid plank inside the box is set from its position relative to the box corner, then never again.
// Manual: /scriptevent pw:planks reflow <radius>  (once, around you — for a structure you loaded by hand).
import { world, system, BlockPermutation, BlockVolume } from "@minecraft/server";

const SPECIES = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "crimson", "warped"];
const MAP = {};
for (const s of SPECIES) MAP[`minecraft:${s}_planks`] = `pw:${s}_planks_grid`;
const VANILLA = Object.keys(MAP);
const GRID = new Set(Object.values(MAP));

const SCAN_EVERY_TICKS = 100;   // 5 s
const SCAN_RADIUS = 24;         // blocks around each player, horizontally
const SCAN_HALF_HEIGHT = 16;    // blocks above / below the player
const BOX = 16;                 // sub-volume edge for getBlocks
const MAX_SWAPS_PER_STEP = 64;  // swaps before the job yields
const MAX_REFLOW_RADIUS = 48;

// neighbour offsets in priority order: below, north, west, south, east, above
const NEIGHBOURS = [[0, -1, 0], [0, 0, -1], [-1, 0, 0], [0, 0, 1], [1, 0, 0], [0, 1, 0]];

function mod4(v) {
  return ((Math.floor(v) % 4) + 4) % 4;
}

function gridStates(gx, gy, gz) {
  return { "pw:gx": mod4(gx), "pw:gy": mod4(gy), "pw:gz": mod4(gz) };
}

/** The grid cell a new plank at loc should show: continue the first older grid neighbour, else the world position. */
function cellFor(dim, loc) {
  for (const [dx, dy, dz] of NEIGHBOURS) {
    let nb;
    try {
      nb = dim.getBlock({ x: loc.x + dx, y: loc.y + dy, z: loc.z + dz });
    } catch {
      nb = undefined;
    }
    if (!nb || !GRID.has(nb.typeId)) continue;
    const p = nb.permutation;
    // the neighbour sits at loc + d, so this block is one grid step back along d
    return gridStates(p.getState("pw:gx") - dx, p.getState("pw:gy") - dy, p.getState("pw:gz") - dz);
  }
  return gridStates(loc.x, loc.y, loc.z);
}

/** Set one vanilla plank to its grid block (once); returns true when set. */
function swapOnce(block) {
  const id = block ? MAP[block.typeId] : undefined;
  if (!id) return false;
  block.setPermutation(BlockPermutation.resolve(id, cellFor(block.dimension, block.location)));
  return true;
}

/** Once, after a structure load: every grid plank in the box takes its cell from its position relative to the box's
 *  min corner (the pattern the structure had when it was built, whatever rotation it was loaded at). */
export function reflowPlanks(dim, min, max) {
  let n = 0;
  for (let x = min.x; x <= max.x; x++) {
    for (let y = min.y; y <= max.y; y++) {
      for (let z = min.z; z <= max.z; z++) {
        let b;
        try {
          b = dim.getBlock({ x, y, z });
        } catch {
          continue;
        }
        if (!b || !GRID.has(b.typeId)) continue;
        try {
          b.setPermutation(BlockPermutation.resolve(b.typeId, gridStates(x - min.x, y - min.y, z - min.z)));
          n++;
        } catch {}
      }
    }
  }
  return n;
}

world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try {
    swapOnce(ev.block);
  } catch (e) {
    console.warn(`[pw_planks] place swap failed: ${e}`);
  }
});

system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:planks") return;
  const src = ev.sourceEntity;
  const [cmd, rArg] = (ev.message || "").trim().split(/\s+/);
  if (cmd !== "reflow" || !src) return;
  const r = Math.min(MAX_REFLOW_RADIUS, Math.max(1, parseInt(rArg, 10) || 16));
  const c = src.location;
  const min = { x: Math.floor(c.x) - r, y: Math.floor(c.y) - r, z: Math.floor(c.z) - r };
  const max = { x: Math.floor(c.x) + r, y: Math.floor(c.y) + r, z: Math.floor(c.z) + r };
  const n = reflowPlanks(src.dimension, min, max);
  try {
    src.sendMessage(`[pw_planks] reflow r${r}: ${n} grid planks set from the box corner`);
  } catch {}
});

let busy = false;

function* scanJob(players) {
  let swaps = 0;
  for (const p of players) {
    let dim, c;
    try {
      dim = p.dimension;
      c = p.location;
    } catch {
      continue;
    }
    const range = dim.heightRange;
    const y0 = Math.max(range.min, Math.floor(c.y) - SCAN_HALF_HEIGHT);
    const y1 = Math.min(range.max - 1, Math.floor(c.y) + SCAN_HALF_HEIGHT);
    const x0 = Math.floor(c.x) - SCAN_RADIUS, x1 = Math.floor(c.x) + SCAN_RADIUS;
    const z0 = Math.floor(c.z) - SCAN_RADIUS, z1 = Math.floor(c.z) + SCAN_RADIUS;
    for (let bx = x0; bx <= x1; bx += BOX) {
      for (let bz = z0; bz <= z1; bz += BOX) {
        for (let by = y0; by <= y1; by += BOX) {
          let list;
          try {
            const vol = new BlockVolume({ x: bx, y: by, z: bz },
              { x: Math.min(bx + BOX - 1, x1), y: Math.min(by + BOX - 1, y1), z: Math.min(bz + BOX - 1, z1) });
            list = dim.getBlocks(vol, { includeTypes: VANILLA }, true);
          } catch {
            yield;   // unloaded or out of range: skip this box
            continue;
          }
          for (const loc of list.getBlockLocationIterator()) {
            try {
              if (swapOnce(dim.getBlock(loc))) swaps++;
            } catch {}
            if (swaps >= MAX_SWAPS_PER_STEP) {
              swaps = 0;
              yield;
            }
          }
          yield;
        }
      }
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
