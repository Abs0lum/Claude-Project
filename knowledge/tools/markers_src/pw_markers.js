// pw_markers.js — PW-Civitas Markers v0.2.1
// Markers are ENTITIES now (Abs0lum 2026-09-22 20:24, PROPOSAL Z): a zone corner, station, port or datum shares a cell
// with any block — furniture, beds, chests, doors — because an entity does not occupy the block grid.
// + PROPOSAL H probe: the ladder hatch lid, a collidable entity over a vanilla ladder (native climbing).
//
// Placement uses the SAME items as before (the pw:zone_/station_/port_/datum block items). The block is never placed:
// world.beforeEvents.playerInteractWithBlock is cancelled and a pw:marker entity is spawned instead.
//   normal tap  -> the cell in front of the tapped face (exactly where the block would have gone)
//   SNEAK tap   -> the tapped block's OWN cell (the chair, the bed, the table ...)
// Numbering is unchanged from v0.1.9: zone corners count per player per kind (a new kind starts a new ring,
// /scriptevent civ:zone close ends it), stations and ports count per player per role (civ:station reset).
import { world, system, BlockVolume, GameMode, ItemStack, Direction } from "@minecraft/server";

export const MARKER = "pw:marker";
export const LID = "pw:hatch_lid";
export const LID_ITEM = "pw:hatch_lid";

// FROZEN, APPEND-ONLY: the pw:icon number of every marker kind. Saved buildings carry these numbers — never reorder.
export const ZONES = ["threshold", "stable", "cellar", "storeroom", "kitchen", "quarters", "chamber", "workfloor", "shopfloor", "yard", "garden", "commons"];
export const STATIONS = ["anvil", "bed", "bench", "counter", "desk", "door", "field", "hearth", "oven", "pen", "post", "prep", "rack", "seat", "stall", "store", "table", "yard"];
export const PORTS = ["passage", "sewer", "stair", "well"];
export const FAM = { zone: 0, station: 1, port: 2, datum: 3 };
export const ICONS = [
  ...ZONES.map((k) => ["zone", k]),
  ...STATIONS.map((k) => ["station", k]),
  ...PORTS.map((k) => ["port", k]),
  ["datum", "datum"],
];

/** Marker kind of a block/item id, or null. */
export function classify(typeId) {
  if (typeId === "pw:datum") return { fam: "datum", kind: "datum", icon: ICONS.length - 1 };
  const m = /^pw:(zone|station|port)_([a-z_]+)$/.exec(typeId || "");
  if (!m) return null;
  const fam = m[1], kind = m[2];
  const icon = ICONS.findIndex(([f, k]) => f === fam && k === kind);
  return icon < 0 ? null : { fam, kind, icon };
}
export function blockIdOf(icon) {
  const [fam, kind] = ICONS[icon];
  return fam === "datum" ? "pw:datum" : `pw:${fam}_${kind}`;
}
export const MARKER_BLOCK_IDS = ICONS.map((_, i) => blockIdOf(i));

const FACE = {
  [Direction.Up]: { x: 0, y: 1, z: 0 }, [Direction.Down]: { x: 0, y: -1, z: 0 },
  [Direction.North]: { x: 0, y: 0, z: -1 }, [Direction.South]: { x: 0, y: 0, z: 1 },
  [Direction.East]: { x: 1, y: 0, z: 0 }, [Direction.West]: { x: -1, y: 0, z: 0 },
};
const floor3 = (l) => ({ x: Math.floor(l.x), y: Math.floor(l.y), z: Math.floor(l.z) });
const cellKey = (dimId, c) => `${dimId}|${c.x},${c.y},${c.z}`;
function say(tag, m) { try { world.sendMessage(`${tag}§r ${m}`); } catch (e) { /* no chat */ } }
function bar(player, m) { try { player.onScreenDisplay.setActionBar(m); } catch (e) { /* ignore */ } }
function isCreative(player) { try { return player.getGameMode() === GameMode.Creative; } catch (e) { return true; } }

function consumeHeld(player, typeId) {
  if (isCreative(player)) return;
  try {
    const c = player.getComponent("minecraft:inventory").container, slot = player.selectedSlotIndex, it = c.getItem(slot);
    if (!it || it.typeId !== typeId) return;
    if (it.amount > 1) { it.amount -= 1; c.setItem(slot, it); } else c.setItem(slot, undefined);
  } catch (e) { /* ignore */ }
}
function giveBack(player, typeId) {
  if (!player || isCreative(player)) return;
  try { const left = player.getComponent("minecraft:inventory").container.addItem(new ItemStack(typeId, 1)); if (left) player.dimension.spawnItem(left, player.location); } catch (e) { /* ignore */ }
}

// ---------------------------------------------------------------------------------------------------------------------
// VISIBILITY (world-wide): hidden markers are invisible AND lose their hit box (custom_hit_test), so they never catch a tap;
// the collision box is always 0 x 0 on the floor plane, so a marker never refuses a block placement
// ---------------------------------------------------------------------------------------------------------------------
export function markersVisible() { try { return world.getDynamicProperty("civ:markers_vis") !== false; } catch (e) { return true; } }
function applyVis(e, vis) {
  try {
    if (e.getProperty("pw:vis") === vis) return;
    e.setProperty("pw:vis", vis); e.triggerEvent(vis ? "pw:show" : "pw:hide");
  } catch (err) { /* entity gone */ }
}
function allMarkers(dimOnly) {
  const out = [];
  for (const id of dimOnly ? [dimOnly] : ["overworld", "nether", "the_end"]) {
    try { out.push(...world.getDimension(id).getEntities({ type: MARKER })); } catch (e) { /* dimension unavailable */ }
  }
  return out;
}
export function setVisibility(vis) {
  try { world.setDynamicProperty("civ:markers_vis", vis); } catch (e) { /* ignore */ }
  const ms = allMarkers(); for (const e of ms) applyVis(e, vis);
  return ms.length;
}

// ---------------------------------------------------------------------------------------------------------------------
// SPAWN / NUMBER
// ---------------------------------------------------------------------------------------------------------------------
export function spawnMarker(dim, cell, info, n) {
  const e = dim.spawnEntity(MARKER, { x: cell.x + 0.5, y: cell.y, z: cell.z + 0.5 });
  e.setProperty("pw:fam", FAM[info.fam]); e.setProperty("pw:icon", info.icon); e.setProperty("pw:n", n);
  for (const t of ["civ:marker", `civ:${info.fam}`, `civ:kind:${info.kind}`, `civ:n:${n}`]) e.addTag(t);
  try { e.setRotation({ x: 0, y: 0 }); } catch (err) { /* ignore */ }
  const vis = markersVisible(); if (!vis) applyVis(e, false);
  return e;
}
export function markerAt(dim, cell, icon) {
  try { return dim.getEntitiesAtBlockLocation(cell).find((e) => e.typeId === MARKER && (icon === undefined || e.getProperty("pw:icon") === icon)); } catch (e) { return undefined; }
}

const zoneRings = new Map();        // player.id -> { kind, idx }  (mirrored to the player's dynamic property: survives a reload)
function ringOf(player) {
  if (zoneRings.has(player.id)) return zoneRings.get(player.id);
  try { const s = player.getDynamicProperty("civ:zone_ring"); if (typeof s === "string") { const r = JSON.parse(s); zoneRings.set(player.id, r); return r; } } catch (e) { /* none */ }
  return null;
}
function storeRing(player, r) {
  if (r) zoneRings.set(player.id, r); else zoneRings.delete(player.id);
  try { player.setDynamicProperty("civ:zone_ring", r ? JSON.stringify(r) : undefined); } catch (e) { /* ignore */ }
}
export function nextZoneNumber(player, kind) {
  let r = ringOf(player);
  if (!r || r.kind !== kind) { r = { kind, idx: 0 }; say("§b[ZONE]", `ring begun: ${kind}`); }
  const n = Math.min(63, r.idx); r.idx = n + 1; storeRing(player, r);
  return n;
}
const stationCounters = new Map();  // player.name|blockId -> next index (as v0.1.1)
export function nextStationNumber(player, blockId) {
  const key = player.name + "|" + blockId; const n = Math.min(7, stationCounters.get(key) || 0);
  stationCounters.set(key, n + 1); return n;
}

function placeMarker(player, dim, cell, info, heldTypeId) {
  const n = info.fam === "zone" ? nextZoneNumber(player, info.kind) : (info.fam === "datum" ? 0 : nextStationNumber(player, blockIdOf(info.icon)));
  spawnMarker(dim, cell, info, n);
  if (heldTypeId) consumeHeld(player, heldTypeId);
  if (info.fam === "zone") say("§b[ZONE]", `${info.kind} corner #${n}`);
  else if (info.fam === "datum") say("§e[DATUM]", `datum at ${cell.x} ${cell.y} ${cell.z}`);
  else say("§6[STATION]", `${info.fam === "port" ? "port_" : "station_"}${info.kind} #${n}`);
}

// ---------------------------------------------------------------------------------------------------------------------
// PLACEMENT INTERCEPT (+ fallback if the engine still places the block)
// ---------------------------------------------------------------------------------------------------------------------
const pendingPlace = new Map();     // cellKey -> tick the intercept spawned there
world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
  const id = ev.itemStack && ev.itemStack.typeId;
  if (!id) return;
  if (id === LID_ITEM) {
    ev.cancel = true; if (!ev.isFirstEvent) return;
    const player = ev.player, b = ev.block, dim = b.dimension, loc = floor3(b.location);
    system.run(() => placeLid(player, dim, loc));
    return;
  }
  const info = classify(id); if (!info) return;
  ev.cancel = true; if (!ev.isFirstEvent) return;
  const player = ev.player, b = ev.block, dim = b.dimension, base = floor3(b.location);
  const off = player.isSneaking ? { x: 0, y: 0, z: 0 } : (FACE[ev.blockFace] || { x: 0, y: 1, z: 0 });
  const cell = { x: base.x + off.x, y: base.y + off.y, z: base.z + off.z };
  const now = system.currentTick;
  if (pendingPlace.size > 256) for (const [k, t] of pendingPlace) if (now - t > 200) pendingPlace.delete(k);
  pendingPlace.set(cellKey(dim.id, cell), now);
  system.run(() => { try { placeMarker(player, dim, cell, info, id); } catch (e) { say("§c[MARKERS]", "place error: " + e); } });
});
world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try {
    const info = classify(ev.block.typeId); if (!info) return;
    const dim = ev.block.dimension, cell = floor3(ev.block.location), t = pendingPlace.get(cellKey(dim.id, cell));
    ev.block.setType("minecraft:air");                            // a marker is never a block any more
    if (t !== undefined && system.currentTick - t < 40) return;   // the intercept already spawned it
    placeMarker(ev.player, dim, cell, info, null);
  } catch (e) { /* ignore */ }
});

// ---------------------------------------------------------------------------------------------------------------------
// REMOVE: hit a visible marker (or the lid); /scriptevent civ:markers remove = nearest marker within 3 blocks
// ---------------------------------------------------------------------------------------------------------------------
export function removeMarker(e, player) {
  let icon; try { icon = e.getProperty("pw:icon"); } catch (err) { /* ignore */ }
  try { e.remove(); } catch (err) { return false; }
  if (typeof icon === "number" && icon >= 0 && icon < ICONS.length) giveBack(player, blockIdOf(icon));
  return true;
}
world.afterEvents.entityHitEntity.subscribe((ev) => {
  const t = ev.hitEntity, p = ev.damagingEntity;
  try {
    if (!t || !t.isValid || !p || p.typeId !== "minecraft:player") return;
    if (t.typeId === MARKER) { if (t.getProperty("pw:vis") === false) return; removeMarker(t, p); bar(p, "Marker removed"); }
    else if (t.typeId === LID) { t.remove(); giveBack(p, LID_ITEM); bar(p, "Hatch removed"); }
  } catch (e) { /* ignore */ }
});

// ---------------------------------------------------------------------------------------------------------------------
// MIGRATE old marker BLOCKS -> entities (same kind, same number); the block ids stay registered so old saves load
// ---------------------------------------------------------------------------------------------------------------------
export function numberFromBlock(block, info) {
  const p = block.permutation;
  if (info.fam === "zone") { const i = p.getState("pw:idx") | 0, r = p.getState("pw:ring") | 0; return Math.min(63, r * 16 + i); }
  if (info.fam === "datum") return 0;
  return p.getState("pw:index") | 0;
}
export function migrate(dim, centre, r) {
  const c = floor3(centre), lo = Math.max(dim.heightRange.min, c.y - 16), hi = Math.min(dim.heightRange.max - 1, c.y + 16);
  const locs = [];
  try {
    const list = dim.getBlocks(new BlockVolume({ x: c.x - r, y: lo, z: c.z - r }, { x: c.x + r, y: hi, z: c.z + r }), { includeTypes: MARKER_BLOCK_IDS }, true);
    for (const l of list.getBlockLocationIterator()) locs.push({ x: l.x, y: l.y, z: l.z });
  } catch (e) {
    const rr = Math.min(r, 16);                                   // fallback scan, capped
    for (let x = c.x - rr; x <= c.x + rr; x++) for (let z = c.z - rr; z <= c.z + rr; z++) for (let y = lo; y <= hi; y++) {
      const b = dim.getBlock({ x, y, z }); if (b && classify(b.typeId)) locs.push({ x, y, z });
    }
  }
  let made = 0, dup = 0;
  for (const l of locs) {
    const b = dim.getBlock(l); if (!b) continue;
    const info = classify(b.typeId); if (!info) continue;
    const n = numberFromBlock(b, info);
    const have = markerAt(dim, l, info.icon);
    if (have && have.getProperty("pw:n") === n) dup++; else { spawnMarker(dim, l, info, n); made++; }
    b.setType("minecraft:air");
  }
  return { found: locs.length, made, dup };
}

// ---------------------------------------------------------------------------------------------------------------------
// LIST / CHECK (pre-save: structures must now be saved with Include Entities ON)
// ---------------------------------------------------------------------------------------------------------------------
export function listMarkers(dim, centre, r) {
  const groups = new Map();
  for (const e of dim.getEntities({ type: MARKER, location: centre, maxDistance: r })) {
    const icon = e.getProperty("pw:icon"), n = e.getProperty("pw:n");
    const [fam, kind] = ICONS[icon] || ["?", "?"]; const k = fam === "datum" ? "datum" : `${fam} ${kind}`;
    if (!groups.has(k)) groups.set(k, []); groups.get(k).push(n);
  }
  return [...groups.entries()].sort().map(([k, ns]) => `${k}: ${ns.sort((a, b) => a - b).join(" ")}`);
}
const NOT_SAVED_CONCERN = new Set(["minecraft:player", MARKER, LID, "pw:seat"]);
export function checkForSave(dim, centre, r) {
  const counts = new Map();
  for (const e of dim.getEntities({ location: centre, maxDistance: r })) {
    if (NOT_SAVED_CONCERN.has(e.typeId)) continue;
    counts.set(e.typeId, (counts.get(e.typeId) || 0) + 1);
  }
  return [...counts.entries()].sort().map(([t, n]) => `${t} x${n}`);
}

// ---------------------------------------------------------------------------------------------------------------------
// THE LADDER HATCH LID (probe). Hinge = the side the ladder FACES = opposite the ladder (Abs0lum D-C189).
// pw:hinge is a WORLD side: 0 north, 1 east, 2 south, 3 west. Ladder facing_direction: 2 N, 3 S, 4 W, 5 E.
// ---------------------------------------------------------------------------------------------------------------------
export const HINGE_FROM_LADDER = { 2: 0, 5: 1, 3: 2, 4: 3 };
export const SIDE_NAME = ["north", "east", "south", "west"];
export function lidAt(dim, cell) {
  try { return dim.getEntitiesAtBlockLocation(cell).find((e) => e.typeId === LID); } catch (e) { return undefined; }
}
export function placeLid(player, dim, cell) {
  const b = dim.getBlock(cell);
  if (!b || b.typeId !== "minecraft:ladder") { bar(player, "Use the hatch on the TOP ladder of the opening"); return null; }
  const above = dim.getBlock({ x: cell.x, y: cell.y + 1, z: cell.z });
  if (!above || !above.isAir) { bar(player, "The hatch closes the top of a ladder shaft: the space above this ladder must be open"); return null; }
  if (lidAt(dim, cell)) { bar(player, "There is already a hatch here"); return null; }
  let facing; try { facing = b.permutation.getState("facing_direction"); } catch (e) { /* ignore */ }
  const hinge = HINGE_FROM_LADDER[facing] ?? 0;
  const e = dim.spawnEntity(LID, { x: cell.x + 0.5, y: cell.y + 0.8125, z: cell.z + 0.5 });
  e.setProperty("pw:hinge", hinge);
  try { e.setRotation({ x: 0, y: 0 }); } catch (err) { /* ignore */ }
  consumeHeld(player, LID_ITEM);
  try { dim.playSound("close.wooden_trapdoor", e.location); } catch (err) { /* ignore */ }
  bar(player, `Hatch placed (closed) - hinge on the ${SIDE_NAME[hinge]} side, opposite the ladder. Tap it to open.`);
  return e;
}
// breaking the ladder under a lid removes the lid (it has nothing to close any more)
world.afterEvents.playerBreakBlock.subscribe((ev) => {
  try {
    if (!ev.brokenBlockPermutation || ev.brokenBlockPermutation.type.id !== "minecraft:ladder") return;
    const lid = lidAt(ev.block.dimension, floor3(ev.block.location)); if (lid) { lid.remove(); giveBack(ev.player, LID_ITEM); }
  } catch (e) { /* ignore */ }
});
// sound after the data-driven toggle (the property is read a tick later, once the event has applied)
world.afterEvents.dataDrivenEntityTrigger.subscribe((ev) => {
  try {
    if (ev.eventId !== "pw:toggle" || !ev.entity || ev.entity.typeId !== LID) return;
    const e = ev.entity;
    system.run(() => { try { e.dimension.playSound(e.getProperty("pw:open") ? "open.wooden_trapdoor" : "close.wooden_trapdoor", e.location); } catch (err) { /* ignore */ } });
  } catch (e) { /* ignore */ }
});

// ---------------------------------------------------------------------------------------------------------------------
// COMMANDS  (/scriptevent civ:markers hide|show|migrate [r]|list [r]|check [r]|remove · civ:hatch turn|flip ·
//            civ:zone close|status · civ:station reset)
// ---------------------------------------------------------------------------------------------------------------------
function commandPlayer(ev) {
  if (ev.sourceEntity && ev.sourceEntity.typeId === "minecraft:player") return ev.sourceEntity;
  return world.getAllPlayers()[0];
}
function nearest(dim, loc, type, maxD) {
  const es = dim.getEntities({ type, location: loc, maxDistance: maxD });
  let best = null, bd = 1e9;
  for (const e of es) { const d = (e.location.x - loc.x) ** 2 + (e.location.y - loc.y) ** 2 + (e.location.z - loc.z) ** 2; if (d < bd) { bd = d; best = e; } }
  return best;
}
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  try {
    const p = commandPlayer(ev); if (!p) return;
    const [verb, arg] = (ev.message || "").trim().split(/\s+/);
    const r = Math.max(1, Math.min(64, parseInt(arg, 10) || 32));
    if (ev.id === "civ:markers") {
      if (verb === "hide" || verb === "show") { const n = setVisibility(verb === "show"); say("§d[MARKERS]", `${verb === "show" ? "shown" : "hidden"} (${n} loaded)`); }
      else if (verb === "migrate") { const res = migrate(p.dimension, p.location, r); say("§d[MARKERS]", `migrate r${r}: ${res.found} marker blocks -> ${res.made} entities (${res.dup} already there)`); }
      else if (verb === "list") { const lines = listMarkers(p.dimension, p.location, r); say("§d[MARKERS]", lines.length ? `within ${r}:` : `none within ${r}`); for (const l of lines) say("§d  ", l); }
      else if (verb === "check") { const lines = checkForSave(p.dimension, p.location, r); say("§d[MARKERS]", lines.length ? `these would be saved too (Include Entities ON), within ${r}: ${lines.join(", ")}` : `nothing but markers within ${r} - safe to save with Include Entities ON`); }
      else if (verb === "remove") { const e = nearest(p.dimension, p.location, MARKER, 3); if (e) { removeMarker(e, p); say("§d[MARKERS]", "nearest marker removed"); } else say("§d[MARKERS]", "no marker within 3 blocks"); }
      else say("§d[MARKERS]", "verbs: hide | show | migrate [r] | list [r] | check [r] | remove");
    } else if (ev.id === "civ:hatch") {
      const lid = nearest(p.dimension, p.location, LID, 4); if (!lid) { say("§6[HATCH]", "no hatch within 4 blocks"); return; }
      const step = verb === "turn" ? 1 : verb === "flip" ? 2 : 0; if (!step) { say("§6[HATCH]", "verbs: turn | flip"); return; }
      const h = ((lid.getProperty("pw:hinge") | 0) + step) % 4; lid.setProperty("pw:hinge", h); say("§6[HATCH]", `hinge now on the ${SIDE_NAME[h]} side`);
    } else if (ev.id === "civ:zone") {
      const rng = ringOf(p);
      if (verb === "close") { if (rng) { say("§b[ZONE]", `ring closed: ${rng.kind}, ${rng.idx} corners`); storeRing(p, null); } else say("§b[ZONE]", "no open ring"); }
      else if (verb === "status") say("§b[ZONE]", rng ? `open ring: ${rng.kind}, next corner #${rng.idx}` : "no open ring");
    } else if (ev.id === "civ:station" && verb === "reset") { stationCounters.clear(); say("§6[STATION]", "counters reset"); }
  } catch (e) { say("§c[MARKERS]", "error: " + e); }
});

// markers loaded from disk or a structure take the current world-wide visibility
function onArrive(ev) { try { const e = ev.entity; if (e && e.typeId === MARKER) applyVis(e, markersVisible()); } catch (err) { /* ignore */ } }
world.afterEvents.entityLoad.subscribe(onArrive);
world.afterEvents.entitySpawn.subscribe(onArrive);

try { console.warn(`[CIVITAS-MARKERS] v0.2.1 markers are entities — ${ICONS.length} kinds (12 zones, 18 stations, 4 ports, datum); hatch lid probe; visible=${markersVisible()}`); } catch (e) { /* ignore */ }
