// pw_furniture.js — the pw:furniture family runtime (BP-02 v1.3.183): sit + table auto-join.
//
//  seats   pw:furn_{bench,stool,chair,barrel_seat}_<wood>  custom component pw:seat: interact (empty hand or any item that is
//          not a block) -> an invisible rideable pw:seat entity is spawned at the seat surface and the player mounts it;
//          sneak dismounts (vanilla); a 1 s sweeper removes riderless seat entities.  One seat entity per cell, reused.
//  tables  pw:furn_table_<wood>  states pw:n/e/s/w (world-aligned booleans, n = the cell at z-1): adjacent tables auto-join —
//          the permutation picks one of 16 geometries where joined sides drop their apron rail and shared corner legs.
//          Neighbour listener on place/break (the same pattern as the Markers frame_post resolver).
// Engine notes: block custom components are registered in system.beforeEvents.startup (@minecraft/server 2.0.0);
// the rider's pelvis sits ~0.3 below the seat entity's origin -> SEAT_Y_OFFSET (ASSUMPTION, witness item).
import { world, system, BlockPermutation } from "@minecraft/server";

const TAG = "[pw_furniture]";
const log = (m) => { try { console.warn(`${TAG} ${m}`); } catch { /* no console */ } };
const WOODS = ["oak", "spruce", "dark_oak"];
const SEAT_TOP = { bench: 8, stool: 10, chair: 10, barrel_seat: 10 };          // seat surface in cubes (1/16 block)
export const SEAT_BLOCKS = new Map();                                           // block id -> seat surface (cubes); the CIVITAS seat-station registry
for (const [piece, top] of Object.entries(SEAT_TOP)) for (const w of WOODS) SEAT_BLOCKS.set(`pw:furn_${piece}_${w}`, top);
export const TABLE_IDS = new Set(WOODS.map((w) => `pw:furn_table_${w}`));
const SEAT_ENTITY = "pw:seat";
const SEAT_Y_OFFSET = -0.30;                                                    // ASSUMPTION: rider origin vs seat surface (witness; +/-0.1 steps)
const YAW = { north: 180, south: 0, east: -90, west: 90 };                       // Bedrock yaw: 0 = +z (south), 180 = north

function seatFor(block) {
  const top = SEAT_BLOCKS.get(block.typeId); if (top === undefined) return null;
  const dim = block.dimension, l = block.location;
  const loc = { x: l.x + 0.5, y: l.y + top / 16 + SEAT_Y_OFFSET, z: l.z + 0.5 };
  const near = dim.getEntities({ type: SEAT_ENTITY, location: loc, maxDistance: 0.75 });
  let seat = near[0];
  if (seat) {
    const r = seat.getComponent("minecraft:rideable");
    if (r && r.getRiders().length > 0) return null;                             // occupied
    seat.teleport(loc);
  } else seat = dim.spawnEntity(SEAT_ENTITY, loc);
  return seat;
}

function sit(player, block) {
  const seat = seatFor(block); if (!seat) return false;
  let yaw = 0;
  try { const d = block.permutation.getState("minecraft:cardinal_direction"); if (d in YAW) yaw = YAW[d]; } catch { /* no state */ }
  try { seat.setRotation({ x: 0, y: yaw }); } catch { /* ignore */ }
  const r = seat.getComponent("minecraft:rideable"); if (!r) return false;
  const ok = r.addRider(player);
  if (ok) system.run(() => { try { player.setRotation({ x: 0, y: yaw }); } catch { /* ignore */ } });
  return ok;
}

// riderless seat entities are removed (sneak-dismount leaves them behind); 1 s cadence, cheap: a handful of entities at most
system.runInterval(() => {
  try {
    for (const dimId of ["overworld", "nether", "the_end"]) {
      const dim = world.getDimension(dimId);
      for (const e of dim.getEntities({ type: SEAT_ENTITY })) {
        const r = e.getComponent("minecraft:rideable");
        if (!r || r.getRiders().length === 0) e.remove();
      }
    }
  } catch (x) { /* dimension not ready */ }
}, 20);

// ---- table auto-join --------------------------------------------------------------------------------------------------
function joinMask(dim, l) {
  const at = (dx, dz) => { try { const b = dim.getBlock({ x: l.x + dx, y: l.y, z: l.z + dz }); return !!b && TABLE_IDS.has(b.typeId); } catch { return false; } };
  return { "pw:n": at(0, -1), "pw:e": at(1, 0), "pw:s": at(0, 1), "pw:w": at(-1, 0) };
}
function refreshTable(dim, l) {
  try {
    const b = dim.getBlock(l); if (!b || !TABLE_IDS.has(b.typeId)) return;
    const m = joinMask(dim, b.location);
    const cur = b.permutation;
    if (["pw:n", "pw:e", "pw:s", "pw:w"].every((k) => cur.getState(k) === m[k])) return;
    b.setPermutation(BlockPermutation.resolve(b.typeId, m));
  } catch (x) { log(`refreshTable: ${x}`); }
}
function refreshAround(dim, l, self) {
  if (self) refreshTable(dim, l);
  for (const [dx, dz] of [[0, -1], [1, 0], [0, 1], [-1, 0]]) refreshTable(dim, { x: l.x + dx, y: l.y, z: l.z + dz });
}
world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try { if (TABLE_IDS.has(ev.block.typeId)) refreshAround(ev.block.dimension, ev.block.location, true); } catch (x) { log(`place: ${x}`); }
});
world.afterEvents.playerBreakBlock.subscribe((ev) => {
  try { if (TABLE_IDS.has(ev.brokenBlockPermutation.type.id)) refreshAround(ev.block.dimension, ev.block.location, false); } catch (x) { log(`break: ${x}`); }
});

system.beforeEvents.startup.subscribe((ev) => {
  try {
    ev.blockComponentRegistry.registerCustomComponent("pw:seat", {
      onPlayerInteract: (e) => {
        try {
          if (!e.player) return;
          const held = e.itemStack;
          if (held && held.typeId.startsWith("pw:")) return;                 // placing our blocks against a seat stays a placement
          sit(e.player, e.block);
        } catch (x) { log(`seat onPlayerInteract: ${x}`); }
      }
    });
    log("custom component pw:seat registered; tables: " + [...TABLE_IDS].join(","));
  } catch (x) { log(`startup: ${x}`); }
});
try { console.warn(`${TAG} ready — 12 pieces x 3 woods, seats ${SEAT_BLOCKS.size}, tables auto-join`); } catch { /* no console */ }
