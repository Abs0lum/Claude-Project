// pw_homestead.js — HOMESTEAD family runtime (BP-02 v1.3.182; room wall test fixed in v1.3.185): hearth · flue · dual wall · rafter.
//
//  hearth  pw:hearth_<material>   states: minecraft:cardinal_direction, pw:phase (cold/fueled/lit/embers/spent)
//          fuel + flint & steel state machine (pw_homestead_logic.js), smoke (chute walk through pw:flue),
//          room smoke (bounded flood-fill = the room; state level 0..15; block-colliding particles; fog),
//          crackle, fire-pit puff (campfire smoke from the flame while lit, thin in embers — v1.3.182).
//          Timing lives in a world dynamic-property ledger, one entry per hearth.  'spent' = burnt out,
//          the charcoal stays in the pit until new fuel replaces it.
//  flue    pw:flue_<material>     state: pw:cap (true when nothing is above -> chimney cap + exhaust point)
//          v1.3.182: hollow bore, NO collision box -> chimneys are enterable.  A per-tick bore keeper holds
//          the walls (side entry is pushed back; only straight down/up the column gets in), and inside a chute
//          you suffocate at the drowning rate, take 1/2 heart of heat per second over coals (stops on exit)
//          and are set on fire like normal fire over a LIT hearth (Abs0lum's hazard law, 2026-09-22).
//  wall    pw:wall_<material>     states: minecraft:cardinal_direction, pw:inner (16 interior finishes)
//          empty-hand tap cycles the inner finish, tap with a stick flips inner/outer
//  rafter  pw:rafter45_<wood>     no collision; players inside get slowness (~70 % speed)
//
// Engine notes: particles are client-side and fire-and-forget (no tracking is possible) — the smoke
// model is a per-room LEVEL that re-emits every cycle.  Vanilla flint & steel would place a fire block
// in the cell in front of the hearth, so the before-event cancels it and we run the transition ourselves.

import { world, system, BlockVolume, EquipmentSlot, EntityDamageCause } from "@minecraft/server";
import * as L from "./pw_homestead_logic.js";
import { HEARTH_IDS, FLUE_IDS, WALL_IDS, RAFTER_IDS, INNER16 } from "./pw_homestead_materials.js";

const TAG = "[pw_homestead]";
const log = (m) => { try { console.warn(`${TAG} ${m}`); } catch { /* no console */ } };

const HEARTH_SET = new Set(HEARTH_IDS);
const FLUE_SET = new Set(FLUE_IDS);
const WALL_SET = new Set(WALL_IDS);
const RAFTER_SET = new Set(RAFTER_IDS);

const CYCLE_TICKS = 40;          // hearth cycle (2 s): phase check, smoke, crackle
const ROOM_TTL_TICKS = 600;      // room flood-fill cache (30 s)
const ROOM_MAX_CELLS = 400;      // bigger than this = outdoors / open hall -> smoke dissipates
const ROOM_RADIUS = 12;
const CHUTE_MAX = 48;
const SMOKE_MAX = 15;
const FOG_ON = 8, FOG_OFF = 5;   // hysteresis for the room fog push/pop
const COUGH_LEVEL = 12;
const CRACKLE_ID = "block.campfire.crackle";
const INDEX_KEY = "pw:hearth_index";
const KEY_PREFIX = "pw:hearth|";
const PUFF_TICKS = 4;            // fire-pit puff cycle
const PUFF_ID = "pw:hearth_puff";
const BORE_HALF = 0.375;         // bore 12 px -> +-0.375 from the cell centre
const PLAYER_HALF = 0.3;         // player width 0.6
const BORE_SLACK = BORE_HALF - PLAYER_HALF;   // 0.075: how far off-centre a player may drift inside

// ---------------------------------------------------------------------------------------------
// LEDGER (world dynamic properties; one JSON entry per hearth; an index of keys)
// ---------------------------------------------------------------------------------------------
const ledger = new Map();        // key -> entry (mirror of the dynamic properties)
const rooms = new Map();         // key -> { cells: [{x,y,z}], set: Set<string>, open: bool, until: tick }
const smoke = new Map();         // key -> level 0..15
const fogged = new Map();        // playerId -> hearth key whose fog is pushed
const puffTargets = new Map();   // key -> { dimId, x, y, z, phase } refreshed by hearthCycle (lit/embers with players near)
const chuteAir = new Map();      // playerId -> air (L.AIR_MAX when full; entries are dropped once full again)
const lastCell = new Map();      // playerId -> { x, y, z, inFlue, px, py, pz }

function keyOf(dimId, x, y, z) { return `${KEY_PREFIX}${dimId}|${x},${y},${z}`; }
function parseKey(key) {
  const [, dimId, xyz] = key.split("|");
  const [x, y, z] = xyz.split(",").map(Number);
  return { dimId, x, y, z };
}
function saveIndex() {
  try { world.setDynamicProperty(INDEX_KEY, JSON.stringify([...ledger.keys()])); } catch (e) { log(`index save failed: ${e}`); }
}
function saveEntry(key, entry) {
  ledger.set(key, entry);
  try { world.setDynamicProperty(key, JSON.stringify(entry)); } catch (e) { log(`entry save failed: ${e}`); }
}
function dropEntry(key) {
  ledger.delete(key); rooms.delete(key); smoke.delete(key);
  try { world.setDynamicProperty(key, undefined); } catch { /* ignore */ }
  saveIndex();
}
function loadLedger() {
  let n = 0;
  try {
    for (const id of world.getDynamicPropertyIds()) {
      if (!id.startsWith(KEY_PREFIX)) continue;
      const raw = world.getDynamicProperty(id);
      if (typeof raw !== "string") continue;
      try { ledger.set(id, JSON.parse(raw)); n++; } catch { /* corrupt entry -> skip */ }
    }
  } catch (e) { log(`ledger load failed: ${e}`); }
  saveIndex();
  log(`ledger loaded: ${n} hearth(s)`);
}
function entryFor(block) {
  const { x, y, z } = block.location;
  const key = keyOf(block.dimension.id, x, y, z);
  let e = ledger.get(key);
  if (!e) { e = L.newEntry(now()); saveEntry(key, e); saveIndex(); }
  return { key, entry: e };
}
function now() { try { return world.getAbsoluteTime(); } catch { return system.currentTick; } }

// ---------------------------------------------------------------------------------------------
// HELPERS
// ---------------------------------------------------------------------------------------------
function isHearth(b) { return !!(b && HEARTH_SET.has(b.typeId)); }
function isFlue(b) { return !!(b && FLUE_SET.has(b.typeId)); }
function isWall(b) { return !!(b && WALL_SET.has(b.typeId)); }
function isRafter(b) { return !!(b && RAFTER_SET.has(b.typeId)); }
function getBlockSafe(dim, x, y, z) { try { return dim.getBlock({ x, y, z }); } catch { return undefined; } }
function setState(block, name, value) {
  try {
    const cur = block.permutation.getState(name);
    if (cur === value) return false;
    block.setPermutation(block.permutation.withState(name, value));
    return true;
  } catch (e) { log(`setState ${name}=${value} failed: ${e}`); return false; }
}
function heldItem(player, fallback) {
  try {
    const eq = player.getComponent("equippable");
    const it = eq ? eq.getEquipment(EquipmentSlot.Mainhand) : undefined;
    if (it) return it;
  } catch { /* fall through */ }
  return fallback;
}
function isCreative(player) {
  try { return String(player.getGameMode()).toLowerCase() === "creative"; } catch { return false; }
}
function consumeOne(player) {
  if (isCreative(player)) return;
  try {
    const cont = player.getComponent("inventory").container;
    const slot = player.selectedSlotIndex;
    const it = cont.getItem(slot);
    if (!it) return;
    if (it.amount > 1) { it.amount -= 1; cont.setItem(slot, it); } else cont.setItem(slot, undefined);
  } catch (e) { log(`consume failed: ${e}`); }
}
function damageTool(player) {
  if (isCreative(player)) return;
  try {
    const cont = player.getComponent("inventory").container;
    const slot = player.selectedSlotIndex;
    const it = cont.getItem(slot);
    if (!it) return;
    const dur = it.getComponent("durability");
    if (!dur) { consumeOne(player); return; }          // fire charge: single use
    dur.damage += 1;
    if (dur.damage >= dur.maxDurability) cont.setItem(slot, undefined); else cont.setItem(slot, it);
  } catch (e) { log(`tool damage failed: ${e}`); }
}
function actionBar(player, text) { try { player.onScreenDisplay.setActionBar(text); } catch { /* ignore */ } }
function sound(dim, id, loc, volume = 1, pitch = 1) { try { dim.playSound(id, loc, { volume, pitch }); } catch { /* ignore */ } }
function centre(x, y, z) { return { x: x + 0.5, y: y + 0.5, z: z + 0.5 }; }

// ---------------------------------------------------------------------------------------------
// HEARTH interactions
// ---------------------------------------------------------------------------------------------
function applyPhase(block, entry) {
  return setState(block, "pw:phase", entry.phase);
}

function hearthInteract(player, block, item) {
  const { key, entry } = entryFor(block);
  const t = now();
  const id = item ? item.typeId : "";
  const dim = block.dimension;
  const { x, y, z } = block.location;
  const units = L.fuelUnitsFor(id);
  if (units > 0) {
    const r = L.addFuel(entry, units, t);
    if (!r.accepted) { actionBar(player, "Hearth: full — it holds four days of fuel"); saveEntry(key, r.entry); applyPhase(block, r.entry); return; }
    consumeOne(player);
    saveEntry(key, r.entry); applyPhase(block, r.entry);
    sound(dim, r.relit ? "fire.ignite" : "dig.wood", centre(x, y, z), 0.8, r.relit ? 1.0 : 0.8);
    actionBar(player, L.describe(r.entry, t));
    return;
  }
  if (L.isIgniter(id)) {
    const r = L.ignite(entry, t);
    saveEntry(key, r.entry); applyPhase(block, r.entry);
    if (r.lit) { damageTool(player); sound(dim, "fire.ignite", centre(x, y, z), 1.0, 1.0); }
    actionBar(player, r.lit ? L.describe(r.entry, t) : (r.entry.phase === "lit" ? "Hearth: already burning" : "Hearth: nothing to light — add fuel first"));
    return;
  }
  // anything else: status only
  const a = L.advance(entry, t);
  if (a.changed) { saveEntry(key, a.entry); applyPhase(block, a.entry); }
  actionBar(player, L.describe(a.entry, t));
}

// Vanilla flint & steel / fuel placement must not happen on a hearth: cancel, then run ours.
world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
  try {
    const b = ev.block;
    if (!isHearth(b)) return;
    if (ev.isFirstEvent === false) { ev.cancel = true; return; }
    const item = ev.itemStack;
    const id = item ? item.typeId : "";
    if (!(L.fuelUnitsFor(id) > 0 || L.isIgniter(id))) return;     // empty hand / other items: vanilla + onPlayerInteract
    ev.cancel = true;
    const player = ev.player;
    system.run(() => { try { hearthInteract(player, b, item); } catch (e) { log(`hearthInteract: ${e}`); } });
  } catch (e) { log(`before interact: ${e}`); }
});

// ---------------------------------------------------------------------------------------------
// FLUE cap resolver (cap = nothing above)
// ---------------------------------------------------------------------------------------------
function refreshFlue(block) {
  if (!isFlue(block)) return;
  let above;
  try { above = block.above(); } catch { above = undefined; }
  if (!above) return;                       // unloaded above: leave as is
  setState(block, "pw:cap", above.isAir === true);
}
function refreshFlueBelow(dim, x, y, z) {
  const below = getBlockSafe(dim, x, y - 1, z);
  if (isFlue(below)) refreshFlue(below);
}

// ---------------------------------------------------------------------------------------------
// DUAL WALL interactions: empty hand = cycle inner finish; stick = flip (inner <-> outer side)
// ---------------------------------------------------------------------------------------------
function wallInteract(player, block, item) {
  const id = item ? item.typeId : "";
  if (id === "minecraft:stick") {
    const dir = block.permutation.getState("minecraft:cardinal_direction");
    setState(block, "minecraft:cardinal_direction", L.oppositeDir(dir));
    actionBar(player, "Wall: flipped — the inner face now looks the other way");
    return;
  }
  if (id) return;                                             // holding something: let vanilla place
  const cur = block.permutation.getState("pw:inner");
  const next = L.nextInList(INNER16, cur);
  setState(block, "pw:inner", next);
  actionBar(player, `Wall inner finish: ${next.replace(/_/g, " ")}`);
}

// ---------------------------------------------------------------------------------------------
// SMOKE: chute walk, room fill, level, particles, fog
// ---------------------------------------------------------------------------------------------
function chuteWalk(dim, x, y, z) {
  // returns { open: bool, top: y of the last flue (or the hearth) , blocked: bool, unknown: bool }
  let top = y;
  for (let k = 1; k <= CHUTE_MAX; k++) {
    const b = getBlockSafe(dim, x, y + k, z);
    if (!b) return { open: false, blocked: false, unknown: true, top };
    if (b.isAir) return { open: true, blocked: false, unknown: false, top };
    if (isFlue(b)) { top = y + k; continue; }
    return { open: false, blocked: true, unknown: false, top };
  }
  return { open: true, blocked: false, unknown: false, top };
}

function roomFor(key, dim, block) {
  const t = system.currentTick;
  const cached = rooms.get(key);
  if (cached && cached.until > t) return cached;
  const { x, y, z } = block.location;
  const dir = block.permutation.getState("minecraft:cardinal_direction");
  const f = L.frontOffset(dir);
  const start = { x: x + f.x, y, z: z + f.z };
  // v1.3.185 (D-C228): the wall test is L.smokePasses (stable API: typeId + block state), not Block.isSolid (beta-only).
  const probe = (px, py, pz) => {
    const b = getBlockSafe(dim, px, py, pz);
    if (!b) return undefined;                                // unloaded: treat as open, retry later
    return L.smokePasses(b.typeId, (name) => b.permutation.getState(name));
  };
  const r = L.floodRoom(probe, start, { x, y, z }, ROOM_MAX_CELLS, ROOM_RADIUS);
  const room = { cells: r.cells, set: r.seen, open: r.open, until: t + ROOM_TTL_TICKS };
  rooms.set(key, room);
  return room;
}

function emitRoomSmoke(dim, room, level) {
  const n = Math.min(6, Math.ceil(level / 3));
  const cells = room.cells;
  if (!cells.length) return;
  for (let i = 0; i < n; i++) {
    const c = cells[Math.floor(Math.random() * cells.length)];
    const loc = { x: c.x + Math.random(), y: c.y + 0.3 + Math.random() * 0.6, z: c.z + Math.random() };
    try { dim.spawnParticle("pw:room_smoke", loc); } catch { return; }
  }
}
function emitChimneySmoke(dim, x, top, z, strong) {
  const n = strong ? 2 : 1;
  for (let i = 0; i < n; i++) {
    const loc = { x: x + 0.35 + Math.random() * 0.3, y: top + 1.25, z: z + 0.35 + Math.random() * 0.3 };
    try { dim.spawnParticle("pw:chimney_smoke", loc); } catch { return; }
  }
}

function playersNear(dim, x, y, z, r) {
  try { return dim.getPlayers({ location: { x, y, z }, maxDistance: r }); } catch { return []; }
}
function playerInRoom(player, room) {
  try {
    const p = player.location, h = player.getHeadLocation();
    const k1 = `${Math.floor(p.x)},${Math.floor(p.y)},${Math.floor(p.z)}`;
    const k2 = `${Math.floor(h.x)},${Math.floor(h.y)},${Math.floor(h.z)}`;
    return room.set.has(k1) || room.set.has(k2);
  } catch { return false; }
}
function fogPush(player, key) {
  if (fogged.get(player.id) === key) return;
  try { player.runCommand("fog @s push pw:smoke_room pw_hearth_smoke"); fogged.set(player.id, key); } catch { /* ignore */ }
}
function fogPop(player) {
  if (!fogged.has(player.id)) return;
  try { player.runCommand("fog @s pop pw_hearth_smoke"); } catch { /* ignore */ }
  fogged.delete(player.id);
}

// ---------------------------------------------------------------------------------------------
// THE CYCLE (every 2 s)
// ---------------------------------------------------------------------------------------------
let cycleNo = 0;
function hearthCycle() {
  cycleNo++;
  const t = now();
  const stillFogged = new Set();
  for (const [key, entry0] of ledger) {
    const { dimId, x, y, z } = parseKey(key);
    let dim; try { dim = world.getDimension(dimId); } catch { continue; }
    const block = getBlockSafe(dim, x, y, z);
    if (!block) continue;                                        // chunk unloaded: timers keep running by absolute time
    if (!isHearth(block)) { dropEntry(key); continue; }          // replaced by something else
    const a = L.advance(entry0, t);
    if (a.changed) { saveEntry(key, a.entry); applyPhase(block, a.entry); }
    const entry = a.entry;
    const lit = entry.phase === "lit";
    const near = playersNear(dim, x, y, z, 48);
    if ((lit || entry.phase === "embers") && near.length) puffTargets.set(key, { dimId, x, y, z, phase: entry.phase });
    else puffTargets.delete(key);
    let level = smoke.get(key) || 0;
    if (lit && near.length) {
      // crackle + smoke only when somebody can perceive it
      if (cycleNo % 2 === 0) sound(dim, CRACKLE_ID, centre(x, y, z), 0.5, 0.9 + Math.random() * 0.2);
      const chute = chuteWalk(dim, x, y, z);
      if (chute.open) {
        emitChimneySmoke(dim, x, chute.top, z, true);
        level = Math.max(0, level - 1);
      } else if (chute.blocked) {
        const room = roomFor(key, dim, block);
        if (room.open) level = Math.max(0, level - 1);           // outdoors / huge hall: smoke dissipates
        else level = Math.min(SMOKE_MAX, level + 1);
      }
    } else if (entry.phase === "embers" && near.length && cycleNo % 3 === 0) {
      const chute = chuteWalk(dim, x, y, z);
      if (chute.open) emitChimneySmoke(dim, x, chute.top, z, false);
      level = Math.max(0, level - 1);
    } else {
      level = Math.max(0, level - 1);
    }
    smoke.set(key, level);
    if (level > 0 && near.length) {
      const room = roomFor(key, dim, block);
      if (!room.open) {
        emitRoomSmoke(dim, room, level);
        for (const p of near) {
          const inside = playerInRoom(p, room);
          if (inside && level >= FOG_ON) { fogPush(p, key); stillFogged.add(p.id); }
          else if (inside && fogged.get(p.id) === key && level > FOG_OFF) { stillFogged.add(p.id); }
          if (inside && level >= COUGH_LEVEL && cycleNo % 2 === 0) {
            actionBar(p, "The room is full of smoke — you cough");
            try { p.addEffect("slowness", 45, { amplifier: 0, showParticles: false }); } catch { /* ignore */ }
          }
        }
      }
    }
  }
  // pop fog for everyone no longer inside a smoky room
  for (const p of world.getAllPlayers()) { if (fogged.has(p.id) && !stillFogged.has(p.id)) fogPop(p); }
}

// ---------------------------------------------------------------------------------------------
// FIRE-PIT PUFF (every 4 ticks): campfire smoke rising from the flame itself — lit: most cycles; embers: thin
// ---------------------------------------------------------------------------------------------
let puffNo = 0;
function puffCycle() {
  puffNo++;
  for (const [, t] of puffTargets) {
    const want = t.phase === "lit" ? Math.random() < 0.6 : (puffNo % 8 === 0);
    if (!want) continue;
    let dim; try { dim = world.getDimension(t.dimId); } catch { continue; }
    const loc = { x: t.x + 0.5 + (Math.random() - 0.5) * 0.3, y: t.y + 0.55 + Math.random() * 0.25, z: t.z + 0.5 + (Math.random() - 0.5) * 0.3 };
    try { dim.spawnParticle(PUFF_ID, loc); } catch { /* particle pack missing: silent */ }
  }
}

// ---------------------------------------------------------------------------------------------
// CHUTE (every tick): bore keeper + suffocation + heat/fire for players inside a hollow flue
// ---------------------------------------------------------------------------------------------
function hearthAtColumnBottom(dim, x, y, z) {
  // walk down through flue blocks; the block under the lowest flue is the hearth (or nothing)
  for (let k = 1; k <= CHUTE_MAX; k++) {
    const b = getBlockSafe(dim, x, y - k, z);
    if (!b) return undefined;
    if (isFlue(b)) continue;
    return isHearth(b) ? b : undefined;
  }
  return undefined;
}

function chuteCycle() {
  const tick = system.currentTick;
  for (const p of world.getAllPlayers()) {
    try {
      const dim = p.dimension;
      const loc = p.location;
      const cell = { x: Math.floor(loc.x), y: Math.floor(loc.y), z: Math.floor(loc.z) };
      const feet = getBlockSafe(dim, cell.x, cell.y, cell.z);
      const inFlue = isFlue(feet);
      const last = lastCell.get(p.id);
      if (inFlue) {
        // 1. side entry through a wall -> back where you came from
        if (last && !last.inFlue && !L.legalChuteEntry({ x: last.x, y: last.y, z: last.z }, cell)) {
          try { p.teleport({ x: last.px, y: last.py, z: last.pz }, { dimension: dim, keepVelocity: false }); } catch { /* ignore */ }
          continue;                                            // lastCell unchanged: still outside
        }
        // 2. bore keeper: stay inside the 12-px bore
        const cx = cell.x + 0.5, cz = cell.z + 0.5;
        if (Math.abs(loc.x - cx) > BORE_SLACK || Math.abs(loc.z - cz) > BORE_SLACK) {
          const nx = cx + Math.max(-BORE_SLACK, Math.min(BORE_SLACK, loc.x - cx));
          const nz = cz + Math.max(-BORE_SLACK, Math.min(BORE_SLACK, loc.z - cz));
          try { p.teleport({ x: nx, y: loc.y, z: nz }, { dimension: dim, keepVelocity: true }); } catch { /* ignore */ }
        }
        // 3. suffocation at the drowning rate
        const air0 = chuteAir.has(p.id) ? chuteAir.get(p.id) : L.AIR_MAX;
        const st = L.airStep(air0, true);
        chuteAir.set(p.id, st.air);
        try { const br = p.getComponent("minecraft:breathable"); if (br && "airSupply" in br) br.airSupply = Math.max(0, st.air); } catch { /* read-only on this version */ }
        if (st.damage) { try { p.applyDamage(st.damage, { cause: EntityDamageCause.suffocation }); } catch { /* ignore */ } }
        // 4. heat / fire from the hearth at the bottom of the column
        if (tick % L.HEAT_PERIOD_TICKS === 0) {
          const hearth = hearthAtColumnBottom(dim, cell.x, cell.y, cell.z);
          if (hearth) {
            const { entry } = entryFor(hearth);
            const hz = L.hazardFor(L.advance(entry, now()).entry.phase);
            if (hz.fire) { try { p.setOnFire(L.FIRE_SECONDS, true); } catch { /* ignore */ } }
            else if (hz.heat) { try { p.applyDamage(L.HEAT_DAMAGE, { cause: EntityDamageCause.fireTick }); } catch { /* ignore */ } }
            if (hz.heat && tick % 60 === 0) actionBar(p, hz.fire ? "The chimney is full of fire!" : "The chimney is hot and full of smoke");
          }
        }
      } else if (chuteAir.has(p.id)) {
        const st = L.airStep(chuteAir.get(p.id), false);
        if (st.air >= L.AIR_MAX) chuteAir.delete(p.id); else chuteAir.set(p.id, st.air);
      }
      lastCell.set(p.id, { x: cell.x, y: cell.y, z: cell.z, inFlue, px: loc.x, py: loc.y, pz: loc.z });
    } catch { /* ignore this player this tick */ }
  }
}

// ---------------------------------------------------------------------------------------------
// RAFTERS: pass-through with slowness while inside
// ---------------------------------------------------------------------------------------------
function rafterCycle() {
  for (const p of world.getAllPlayers()) {
    try {
      const dim = p.dimension;
      const f = p.location, h = p.getHeadLocation();
      const b1 = getBlockSafe(dim, Math.floor(f.x), Math.floor(f.y), Math.floor(f.z));
      const b2 = getBlockSafe(dim, Math.floor(h.x), Math.floor(h.y), Math.floor(h.z));
      if (isRafter(b1) || isRafter(b2)) p.addEffect("slowness", 15, { amplifier: 1, showParticles: false });
    } catch { /* ignore */ }
  }
}

// ---------------------------------------------------------------------------------------------
// REFLOW (structure loads fire no place events): /scriptevent pw:home reflow
// ---------------------------------------------------------------------------------------------
function reflowAround(player) {
  const dim = player.dimension;
  const c = player.location;
  const from = { x: Math.floor(c.x) - 16, y: Math.floor(c.y) - 8, z: Math.floor(c.z) - 16 };
  const to = { x: Math.floor(c.x) + 16, y: Math.floor(c.y) + 8, z: Math.floor(c.z) + 16 };
  let hearths = 0, flues = 0;
  const visit = (b) => {
    if (isHearth(b)) { entryFor(b); hearths++; }
    else if (isFlue(b)) { refreshFlue(b); flues++; }
  };
  try {
    const vol = new BlockVolume(from, to);
    const list = dim.getBlocks(vol, { includeTypes: [...HEARTH_IDS, ...FLUE_IDS] }, true);
    for (const loc of list.getBlockLocationIterator()) visit(getBlockSafe(dim, loc.x, loc.y, loc.z));
  } catch (e) {
    log(`getBlocks unavailable (${e}); falling back to a loop`);
    for (let x = from.x; x <= to.x; x++) for (let y = from.y; y <= to.y; y++) for (let z = from.z; z <= to.z; z++) visit(getBlockSafe(dim, x, y, z));
  }
  return { hearths, flues };
}

// ---------------------------------------------------------------------------------------------
// WIRING
// ---------------------------------------------------------------------------------------------
system.beforeEvents.startup.subscribe((ev) => {
  try {
    ev.blockComponentRegistry.registerCustomComponent("pw:hearth", {
      onPlace: (e) => { try { entryFor(e.block); } catch (x) { log(`hearth onPlace: ${x}`); } },
      onPlayerInteract: (e) => {
        try {
          if (!e.player) return;
          const item = heldItem(e.player, e.itemStack);
          hearthInteract(e.player, e.block, item);
        } catch (x) { log(`hearth onPlayerInteract: ${x}`); }
      },
    });
    ev.blockComponentRegistry.registerCustomComponent("pw:flue", {
      onPlace: (e) => {
        try {
          refreshFlue(e.block);
          const { x, y, z } = e.block.location;
          refreshFlueBelow(e.block.dimension, x, y, z);
        } catch (x) { log(`flue onPlace: ${x}`); }
      },
    });
    ev.blockComponentRegistry.registerCustomComponent("pw:wall_dual", {
      onPlayerInteract: (e) => {
        try { if (e.player) wallInteract(e.player, e.block, heldItem(e.player, e.itemStack)); } catch (x) { log(`wall onPlayerInteract: ${x}`); }
      },
    });
    log("custom components registered: pw:hearth, pw:flue, pw:wall_dual");
  } catch (e) { log(`register failed: ${e}`); }
});

world.afterEvents.playerBreakBlock.subscribe((ev) => {
  try {
    const id = ev.brokenBlockPermutation ? ev.brokenBlockPermutation.type.id : "";
    const { x, y, z } = ev.block.location;
    if (HEARTH_SET.has(id)) dropEntry(keyOf(ev.dimension.id, x, y, z));
    refreshFlueBelow(ev.dimension, x, y, z);               // a flue (or anything) removed above a flue re-caps it
  } catch (e) { log(`break: ${e}`); }
});
world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try {
    const { x, y, z } = ev.block.location;
    if (!isFlue(ev.block)) refreshFlueBelow(ev.dimension, x, y, z);   // anything placed on a capped flue un-caps it
  } catch (e) { log(`place: ${e}`); }
});

system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:home") return;
  const player = ev.sourceEntity;
  const msg = (ev.message || "").trim();
  try {
    if (msg === "reflow" && player) {
      const r = reflowAround(player);
      player.sendMessage(`${TAG} reflow: ${r.hearths} hearth(s) registered, ${r.flues} flue(s) re-capped`);
    } else if (msg === "status" && player) {
      const t = now();
      let n = 0;
      for (const [key, e] of ledger) {
        const { x, y, z } = parseKey(key);
        player.sendMessage(`${key.slice(KEY_PREFIX.length)} -> ${L.describe(e, t)} · smoke ${smoke.get(key) || 0}`);
        if (++n >= 12) break;
      }
      player.sendMessage(`${TAG} ${ledger.size} hearth(s) in the ledger; showing ${n}`);
    } else if (msg.startsWith("smoke ") && player) {
      const lvl = Math.max(0, Math.min(SMOKE_MAX, parseInt(msg.slice(6), 10) || 0));
      for (const key of ledger.keys()) smoke.set(key, lvl);
      player.sendMessage(`${TAG} smoke level forced to ${lvl} on every hearth (debug)`);
    } else if (msg === "clear" && player) {
      for (const key of [...ledger.keys()]) dropEntry(key);
      player.sendMessage(`${TAG} ledger cleared`);
    } else if (player) {
      player.sendMessage(`${TAG} usage: /scriptevent pw:home reflow | status | smoke <0-15> | clear`);
    }
  } catch (e) { log(`scriptevent: ${e}`); }
});

world.afterEvents.playerLeave.subscribe((ev) => { fogged.delete(ev.playerId); chuteAir.delete(ev.playerId); lastCell.delete(ev.playerId); });

system.run(() => {
  loadLedger();
  system.runInterval(hearthCycle, CYCLE_TICKS);
  system.runInterval(puffCycle, PUFF_TICKS);
  system.runInterval(chuteCycle, 1);
  system.runInterval(rafterCycle, 10);
  log("HOMESTEAD runtime up (cycle 40t, puff 4t, chute 1t, rafters 10t)");
});
