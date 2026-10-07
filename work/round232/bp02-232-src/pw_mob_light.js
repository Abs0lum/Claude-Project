// pw_mob_light.js — BP-02 v1.3.194 (D-C310, his 02:00 CT 09-30: "Yes, it would give it the visual and effect of being 'on fire'")
// v1.3.214 (D-C515, 10-03): clearLight recognises the flattened light-block ids (light_block_0..15) — before, no light was ever removed.
// Self-lit mobs throw real light: an invisible minecraft:light_block rides with each blaze / magma cube / glow squid near a
// player, the way the held-torch and crown lights already do for players.
//   * a light is placed only in AIR (blaze, magma cube) or in a WATER SOURCE block (glow squid: the light block is waterlogged,
//     and the water source is put back when the squid moves on) — it never replaces anything else
//   * every light this module stands up is recorded in a world dynamic property; at world load any that were left behind (the
//     game closed mid-flight) are cleared first, so no stray light blocks stay in the world
//   * toggles + levels below; PW_MOBLIGHT = false switches the whole module off
import { world, system, BlockPermutation } from "@minecraft/server";

const PW_MOBLIGHT = true;
const MOB_LIGHT = {
  "minecraft:blaze":      { level: 13, dy: 1, water: false },   // burning rods: close to a fire's glow
  "minecraft:magma_cube": { level: 10, dy: 0, water: false },   // molten core
  "minecraft:glow_squid": { level: 6,  dy: 0, water: true },    // soft glow, like glow lichen
};
const TICKS = 4;            // 5 updates a second: a light keeps up with a flying blaze
const RANGE = 48;           // blocks around each player
const MAX_LIGHTS = 256;     // hard cap on lights standing at once
const KEY = "pw:mob_lights";

const lights = new Map();   // entity id -> { dimId, x, y, z, water }
let dirty = false;

function lightPerm(level) {
  return BlockPermutation.resolve("minecraft:light_block", { block_light_level: level });
}

function clearLight(rec) {
  // returns true when the cell no longer holds our light (cleared now, or already gone)
  try {
    const b = world.getDimension(rec.dimId).getBlock({ x: rec.x, y: rec.y, z: rec.z });
    if (!b) return false;                                    // chunk not loaded: try again later
    // v1.3.214 (D-C515): Bedrock flattened the light block — the engine reports `minecraft:light_block_<level>` (BDS 1.26.52), so
    // the old exact test never matched: every light was reported cleared and LEFT in the world. Any light block id is ours here.
    if (!String(b.typeId).startsWith("minecraft:light_block")) return true;   // a player replaced it: nothing to undo
    if (rec.water) b.setType("minecraft:water"); else b.setType("minecraft:air");
    return true;
  } catch { return false; }
}

function placeLight(dim, cell, cfg) {
  try {
    const b = dim.getBlock(cell);
    if (!b) return false;
    if (cfg.water) {
      if (b.typeId !== "minecraft:water") return false;
      let depth = 0;
      try { depth = b.permutation.getState("liquid_depth") ?? 0; } catch {}
      if (depth !== 0) return false;                         // sources only: putting a source back is then exact
      b.setPermutation(lightPerm(cfg.level));
      try { b.setWaterlogged(true); } catch { b.setType("minecraft:water"); return false; }
      return true;
    }
    if (!b.isAir) return false;
    b.setPermutation(lightPerm(cfg.level));
    return true;
  } catch { return false; }
}

function save() {
  if (!dirty) return;
  dirty = false;
  try { world.setDynamicProperty(KEY, JSON.stringify([...lights.values()])); } catch {}
}

function bootSweep() {
  let left = [];
  try { left = JSON.parse(world.getDynamicProperty(KEY) ?? "[]"); } catch { left = []; }
  let cleared = 0, pending = [];
  for (const rec of left) { if (clearLight(rec)) cleared++; else pending.push(rec); }
  // records in unloaded chunks stay in the property until they load and are cleared
  lights.clear();
  pending.forEach((rec, i) => lights.set(`boot_${i}`, rec));
  dirty = true; save();
  try { console.warn(`[PW-MOBLIGHT] boot: ${cleared} leftover light(s) cleared, ${pending.length} waiting for their chunk`); } catch {}
}

function tick() {
  const seen = new Set();
  for (const player of world.getAllPlayers()) {
    const dim = player.dimension;
    for (const [type, cfg] of Object.entries(MOB_LIGHT)) {
      let mobs = [];
      try { mobs = dim.getEntities({ type, location: player.location, maxDistance: RANGE }); } catch { continue; }
      for (const e of mobs) {
        if (seen.has(e.id)) continue;
        seen.add(e.id);
        let loc;
        try { loc = e.location; } catch { continue; }
        const cell = { x: Math.floor(loc.x), y: Math.floor(loc.y) + cfg.dy, z: Math.floor(loc.z) };
        const rec = lights.get(e.id);
        if (rec && rec.dimId === dim.id && rec.x === cell.x && rec.y === cell.y && rec.z === cell.z) continue;
        if (!rec && lights.size >= MAX_LIGHTS) continue;
        if (placeLight(dim, cell, cfg)) {
          if (rec) clearLight(rec);
          lights.set(e.id, { dimId: dim.id, x: cell.x, y: cell.y, z: cell.z, water: cfg.water });
          dirty = true;
        }
        // occupied cell: the light stays where it was until a free cell comes
      }
    }
  }
  for (const [id, rec] of [...lights.entries()]) {
    if (seen.has(id)) continue;
    if (clearLight(rec)) { lights.delete(id); dirty = true; }
  }
  save();
}

if (PW_MOBLIGHT) {
  system.run(() => {
    bootSweep();
    system.runInterval(() => { try { tick(); } catch {} }, TICKS);
    try { console.warn(`[PW-MOBLIGHT] active — ${Object.keys(MOB_LIGHT).map(t => t.replace("minecraft:", "") + " " + MOB_LIGHT[t].level).join(", ")}; ${TICKS}t, range ${RANGE}`); } catch {}
  });
}
