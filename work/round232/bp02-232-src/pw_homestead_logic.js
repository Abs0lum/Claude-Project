// pw_homestead_logic.js — PURE hearth logic (no @minecraft imports) so Node can unit-test it.
// Times are absolute world ticks (world.getAbsoluteTime()).  1 fuel UNIT = 1/4 Minecraft day.
//
// Rulings (Abs0lum 2026-09-21 17:12):
//   planks = 1/4 day (1 unit) · log/wood = 1/2 day (2) · coal/charcoal = 1 day (4)
//   flint & steel is required only from COLD-with-fuel ("fueled"); adding fuel while LIT or
//   EMBERS never needs a relight; embers last TWICE as long as the lit phase.

export const UNIT_TICKS = 6000;          // 1/4 day
export const EMBER_FACTOR = 2;           // embers = 2 x lit duration
export const MAX_AHEAD_UNITS = 16;       // stockpile cap: 4 days queued ahead of "now"
export const PHASES = ["cold", "fueled", "lit", "embers", "spent"];   // spent = burnt out, charcoal in the pit (2026-09-22)

// Chimney hazard law (Abs0lum 2026-09-22 12:06): inside a chute you suffocate at the drowning rate; over coals you
// take 1/2 heart of heat damage every second (stops when you leave); over a LIT hearth you are set on fire like
// normal fire.  Vanilla drowning: 300 ticks of air, then 2 damage whenever air reaches -20 (reset to 0); air comes
// back +4 per tick outside.
export const AIR_MAX = 300;
export const AIR_DAMAGE = 2;          // 1 heart
export const HEAT_DAMAGE = 1;         // 1/2 heart
export const HEAT_PERIOD_TICKS = 20;  // every second
export const FIRE_SECONDS = 8;        // normal fire

/** Fuel units for a held item id, 0 when the item is not a fuel. */
export function fuelUnitsFor(typeId) {
  if (!typeId) return 0;
  const id = String(typeId);
  if (id === "minecraft:coal" || id === "minecraft:charcoal") return 4;
  if (id.endsWith("_planks")) return 1;
  if (id.endsWith("_log") || id.endsWith("_wood") || id.endsWith("_hyphae") || id.endsWith("_stem")) return 2;
  return 0;
}

export function isIgniter(typeId) {
  return typeId === "minecraft:flint_and_steel" || typeId === "minecraft:fire_charge";
}

/** A fresh ledger entry. */
export function newEntry(now) {
  return { phase: "cold", pending: 0, litAt: 0, litUntil: 0, emberUntil: 0, touched: now };
}

/**
 * Advance an entry to `now` — the ONLY place phases expire.
 * Returns { entry, changed } where `changed` is true when the phase moved.
 */
export function advance(entry, now) {
  const e = { ...entry };
  let changed = false;
  if (e.phase === "lit" && now >= e.litUntil) {
    const litFor = Math.max(0, e.litUntil - e.litAt);
    e.phase = "embers";
    e.emberUntil = e.litUntil + EMBER_FACTOR * litFor;
    e.pending = 0;
    changed = true;
  }
  if (e.phase === "embers" && now >= e.emberUntil) {
    e.phase = "spent";                 // the charcoal stays in the pit until new fuel replaces it
    changed = true;
  }
  return { entry: e, changed };
}

/**
 * Add `units` of fuel at `now`.  Returns { entry, accepted, relit } — accepted=false when the
 * stockpile cap refuses the item (the item is NOT consumed then).
 */
export function addFuel(entry, units, now) {
  const { entry: e } = advance(entry, now);
  if (units <= 0) return { entry: e, accepted: false, relit: false };
  if (e.phase === "lit") {
    const ahead = (e.litUntil - now) / UNIT_TICKS;
    if (ahead + units > MAX_AHEAD_UNITS) return { entry: e, accepted: false, relit: false };
    e.litUntil += units * UNIT_TICKS;
    return { entry: e, accepted: true, relit: false };
  }
  if (e.phase === "embers") {
    // embers relight new fuel by themselves — no flint & steel
    e.phase = "lit";
    e.litAt = now;
    e.litUntil = now + Math.min(units, MAX_AHEAD_UNITS) * UNIT_TICKS;
    e.emberUntil = 0;
    e.pending = 0;
    return { entry: e, accepted: true, relit: true };
  }
  // cold, spent or fueled: stockpile, waiting for flint & steel (new logs replace the charcoal)
  if (e.pending + units > MAX_AHEAD_UNITS) return { entry: e, accepted: false, relit: false };
  e.pending += units;
  e.phase = "fueled";
  return { entry: e, accepted: true, relit: false };
}

/** Flint & steel at `now`.  Returns { entry, lit } — lit=false when there was nothing to light. */
export function ignite(entry, now) {
  const { entry: e } = advance(entry, now);
  if (e.phase !== "fueled" || e.pending <= 0) return { entry: e, lit: false };
  e.phase = "lit";
  e.litAt = now;
  e.litUntil = now + e.pending * UNIT_TICKS;
  e.pending = 0;
  e.emberUntil = 0;
  return { entry: e, lit: true };
}

/** Human status line for the action bar. */
export function describe(entry, now) {
  const { entry: e } = advance(entry, now);
  const units = (t) => (t / UNIT_TICKS).toFixed(1);
  switch (e.phase) {
    case "lit":    return `Hearth: burning, ${units(Math.max(0, e.litUntil - now))} units (1/4 day each) left`;
    case "embers": return `Hearth: embers, ${units(Math.max(0, e.emberUntil - now))} units until cold — fuel relights it`;
    case "fueled": return `Hearth: ${e.pending} fuel unit(s) waiting — use flint and steel`;
    case "spent":  return "Hearth: burnt out — charcoal in the pit; add planks, logs or coal";
    default:       return "Hearth: cold — add planks, logs or coal";
  }
}

/** Next value in a cyclic list (unknown current -> first). */
export function nextInList(list, current) {
  const i = list.indexOf(current);
  return list[(i + 1) % list.length];
}

/** Front cell offset for a cardinal_direction state (local -z faces the placer). */
export function frontOffset(dir) {
  switch (dir) {
    case "north": return { x: 0, z: -1 };
    case "south": return { x: 0, z: 1 };
    case "east":  return { x: 1, z: 0 };
    case "west":  return { x: -1, z: 0 };
    default:      return { x: 0, z: -1 };
  }
}

export function oppositeDir(dir) {
  return { north: "south", south: "north", east: "west", west: "east" }[dir] || "north";
}

/** Hazard of standing in a chute above a hearth in `phase`: heat (1/2 heart per second) and/or fire. */
export function hazardFor(phase) {
  if (phase === "lit") return { heat: true, fire: true };
  if (phase === "embers") return { heat: true, fire: false };
  return { heat: false, fire: false };
}

/**
 * One tick of the air model.  Inside a chute the air drains by 1 per tick; when it reaches -20 the player takes
 * AIR_DAMAGE and the air resets to 0 (vanilla drowning cadence: first hit 320 ticks after entering, then every 20).
 * Outside, air comes back 4 per tick.  Returns { air, damage }.
 */
export function airStep(air, inside) {
  if (!inside) return { air: Math.min(AIR_MAX, air + 4), damage: 0 };
  let a = air - 1;
  if (a <= -20) return { air: 0, damage: AIR_DAMAGE };
  return { air: a, damage: 0 };
}

/** Is `from` -> `to` (block cells) a legal way into a chute cell?  Only straight down the column (or up it). */
export function legalChuteEntry(from, to) {
  if (!from) return false;
  return from.x === to.x && from.z === to.z && from.y !== to.y;
}

// ---------------------------------------------------------------------------------------------------------------------
// ROOM SMOKE — which cells smoke can fill (v1.3.185, D-C228).  The v1.3.178..184 runtime used Block.isSolid, which does NOT
// exist in the stable @minecraft/server 2.0.0 module this pack pins (beta only): it read undefined, so every wall let
// smoke through, every room came out "open", and a blocked chimney never filled the room.  This is the stable rule:
// DEFAULT = the block stops smoke (a wall).  Smoke passes only through air, OPEN doors/trapdoors/fence gates, a checked
// list of thin fittings (torches, carpets, signs, rails ...), furniture, rafters and the old marker blocks.
// ---------------------------------------------------------------------------------------------------------------------
const SMOKE_PASS_RE = [
  /^minecraft:(air|cave_air|void_air)$/, /^minecraft:light_block/,
  /torch/, /carpet$/, /sign$/, /rail$/, /button$/, /pressure_plate$/, /^minecraft:(standing|wall)_banner$/,
  /candle/, /^minecraft:(frame|glow_frame)$/, /^minecraft:(ladder|vine|glow_lichen|sculk_vein|redstone_wire|lever|tripwire|tripwire_hook|web|snow_layer|flower_pot|end_rod)$/,
  /_vines$/, /lightning_rod$/, /chain$/, /(_skull|_head)$/,
  /^pw:furn_/, /^pw:rafter/, /^pw:(zone|station|port)_/, /^pw:datum$/,
];
const OPENABLE_RE = /(door|fence_gate)$/;          // doors, trapdoors, fence gates: pass only while open_bit is true

/** Does smoke pass through a cell holding this block?  getState(name) reads the block's state (may be undefined). */
export function smokePasses(typeId, getState) {
  const id = String(typeId || "");
  if (!id) return false;
  if (id === "minecraft:sea_lantern") return false;                        // full block despite the name
  if (/lantern$/.test(id)) return true;
  if (OPENABLE_RE.test(id)) { try { return getState("open_bit") === true; } catch (e) { return false; } }
  if (id === "pw:manhole_cover") { try { return (getState("pw:phase") | 0) !== 0; } catch (e) { return false; } }
  return SMOKE_PASS_RE.some((re) => re.test(id));
}

/**
 * Bounded flood fill of the room in front of a hearth (same limits as v1.3.178): probe(x, y, z) returns
 * undefined for an unloaded cell, true when smoke passes, false for a wall.  A room is OPEN when the fill reaches an
 * unloaded cell, exceeds maxCells, or steps past radius from the origin (outdoors / a hall: smoke dissipates).
 * Returns { cells, seen, open } — seen holds every cell looked at (walls included), as the runtime's playerInRoom expects.
 */
export function floodRoom(probe, start, origin, maxCells, radius) {
  const cells = []; const seen = new Set(); const q = [start];
  seen.add(`${start.x},${start.y},${start.z}`);
  let open = false;
  while (q.length) {
    const c = q.shift();
    const p = probe(c.x, c.y, c.z);
    if (p === undefined) { open = true; break; }
    if (!p) continue;
    cells.push(c);
    if (cells.length > maxCells) { open = true; break; }
    for (const d of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]) {
      const nx = c.x + d[0], ny = c.y + d[1], nz = c.z + d[2];
      if (Math.abs(nx - origin.x) > radius || Math.abs(ny - origin.y) > radius || Math.abs(nz - origin.z) > radius) { open = true; continue; }
      const k = `${nx},${ny},${nz}`;
      if (seen.has(k)) continue;
      seen.add(k); q.push({ x: nx, y: ny, z: nz });
    }
    if (open) break;
  }
  return { cells, seen, open };
}
