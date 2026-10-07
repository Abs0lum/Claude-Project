// pw_testrunner_rig.js — the PROBE and the MOB WITNESS RIG (PW-TestRunner BP v0.2.2, D-C257/D-C260/D-C263, 2026-09-27)
// v0.4.3 (D-C310, R16a): ITEM PROOF — a handed item is checked 2 ticks later with testfor hasitem and logged 'CONFIRMED in' or
//         'NOT in' (his vex: replaceitem's word was never checked); BOXES — spec.boxes sets boxes of blocks inside the pen (p12 t01's
//         leaf cube around an oak-log core), remembered and restored with the pen.
// v0.4.1 (D-C300, FA-1): RE-ROLL — a rigged mob that is still a baby 6 ticks after the grow-up (the skeleton horse has NO grow-up
//         event: his R12 z03 'tiny' horse) or that rolled the wrong colour (spec.variant: parrots) is removed and summoned again, up
//         to 30 times, each try logged; LEFTOVER WATER — clearing a pool rig sweeps water / ice left around its footprint (his R12
//         z08-w12 swim buttons) and logs the count; JUKEBOX — spec.jukebox places one inside the pen and tries to start a disc by
//         script (the step text carries the commands when it cannot); the rig logs when you stand in water. The sweep never touches
//         water / ice that was already there when the pool was built (snapshot kept in pw:test_rig_pre; more than 400 such cells =
//         a lake or river beside the pen -> no sweep at all, logged).
//         WALL REPAIR (D-C303, his 22:38 'I occasionally break the glass by mistake and the water leaks out'): every 0.5 s the rig
//         puts back any pen wall / roof cell IT placed that is no longer a barrier, and for a pool any floor cell under the water that
//         is air or liquid (filled with stone - a natural floor block you broke stays stone); each repair is logged once per cell.
// v0.3.9 (D-C288): rig specs take ARMOR (spec.armor / row[].armor): body slot by replaceitem (the p8 wolf-armor check).
// v0.3.7 (D-C285): rig specs take an ITEM (spec.item / row[].item): put in the mob's main hand by replaceitem (the p6 held-items check).
// v0.3.5 (D-C284): rig specs take a NAME TAG (spec.name / row[].name) — the mooshroom probe's render controller picks the model by name.
// v0.3.2 (D-C277, his 09-29 00:34 "a new test with the mobs to check"): rig spec `row` puts more mobs beside the main one (size
//         comparisons: each held at its own x offset), `half` / `height` / `depth` size the pen / pool (elder guardian, the swim
//         tank), `free` leaves the mob(s) un-held inside the pen so they walk / swim (spider legs, guardian spikes + tail).
// v0.3.1: rigged mobs are grown up only when they spawned as babies (is_baby) — no more FAILED grow-up lines for ravagers,
//         rabbits, piglins; a second check 5 ticks later catches a late baby group.
// v0.2.2: rig spec roof:true adds a barrier ceiling (undead in daylight do not burn), every rigged mob gets fire resistance, and
//         zombie-family adults via minecraft:as_adult as well as ageable_grow_up.
// v0.2.1: every rigged mob is grown up (minecraft:ageable_grow_up) so no random baby ever sits in the pen; a spawn failure is
//         kept in the rig state (rigStatus()) so the bar can say NO MOB and why; the pool re-melts any ice every second.
//
// PROBE   places pw:probe (the rotation-law chart entity, PW-TestRunner RP 0.2.2) 3 blocks NORTH of the player at eye
//         height, facing SOUTH (toward him); "anim" fires pw:t6 so the additivity animation plays.
// RIG     builds an INVISIBLE pen (minecraft:barrier ring, 5x5 inside, 3 high) 5 blocks NORTH of the player — or a
//         2-deep pool inside it — summons one mob at the centre facing SOUTH and HOLDS it there every tick (teleport back,
//         velocity cleared, slowness 255) so the pose is the rest pose and the facing is a fact.  Every block the pen
//         replaces is remembered in a world dynamic property and restored by clearRig(), so a relog cannot strand a pen.
// Nothing here runs during early execution: the hold loop reads the world only after the first tick that succeeds.
import { world, system, BlockPermutation } from "@minecraft/server";

const TAG = "[PW-TEST]";
const MAXLINE = 120;
export const RIG_KEY = "pw:test_rig";
export const RIG_TAG = "pw_rig";
const PRE_KEY = "pw:test_rig_pre";     // v0.4.1: water / ice already around a pool before it was built (never swept)
const PRE_CAP = 400;
const HEAL_EVERY = 10;              // v0.4.1 (D-C303): pen repair check every 10 ticks = 0.5 s
export const PROBE_TAG = "pw_probe";
export const PROBE_ID = "pw:probe";
const PEN_HALF = 2;                 // interior half-width: 5x5 inside
const PEN_HEIGHT = 3;               // walls y0..y0+2
const PEN_DISTANCE = 5;             // pen centre this many blocks north of the player
const PROBE_DISTANCE = 3;

function clip(s) { const t = String(s ?? ""); return t.length <= MAXLINE ? t : t.slice(0, MAXLINE - 1) + "~"; }
function log(text) { const line = clip(`${TAG} ${text}`); try { console.warn(line); } catch { /* no console */ } return line; }
function short(v, n) { const s = String(v ?? ""); return s.length <= n ? s : s.slice(0, n - 1) + "~"; }

// ---------------------------------------------------------------------------------------------------------------------
// facing (the bar shows it during a P0 run: the compass points to the world spawn, not north)
// ---------------------------------------------------------------------------------------------------------------------
export function facingName(yaw) {
  if (typeof yaw !== "number" || Number.isNaN(yaw)) return "?";
  const y = ((yaw % 360) + 540) % 360 - 180;            // -180 < y <= 180; 0 = south, 90 = west, -90 = east, 180 = north
  if (y > -45 && y <= 45) return "SOUTH";
  if (y > 45 && y <= 135) return "WEST";
  if (y > -135 && y <= -45) return "EAST";
  return "NORTH";
}
export function facing(player) { try { return facingName(player.getRotation().y); } catch { return "?"; } }

// ---------------------------------------------------------------------------------------------------------------------
// rig state (world dynamic property; lazy — never during early execution)
// ---------------------------------------------------------------------------------------------------------------------
let R = null;
let loaded = false;
export function _rig() { return R; }
function loadRig() {
  if (loaded) return true;
  let raw;
  try { raw = world.getDynamicProperty(RIG_KEY); } catch { return false; }
  loaded = true;
  if (typeof raw === "string" && raw !== "") { try { R = JSON.parse(raw); } catch { R = null; } }
  return true;
}
function saveRig() {
  try { world.setDynamicProperty(RIG_KEY, R ? JSON.stringify(R) : undefined); } catch (e) { log(`rig save failed: ${short(e, 60)}`); }
}

// ---------------------------------------------------------------------------------------------------------------------
// the probe
// ---------------------------------------------------------------------------------------------------------------------
function removeTagged(dim, tag) {
  let n = 0;
  try { for (const e of dim.getEntities({ tags: [tag] })) { try { e.remove(); n++; } catch { /* already gone */ } } } catch (e) { log(`getEntities ${tag}: ${short(e, 50)}`); }
  return n;
}
export function clearProbes(player) {
  const n = removeTagged(player.dimension, PROBE_TAG);
  if (n) log(`probe removed (${n})`);
  return n;
}
/** mode: "static" (the bind pose) | "anim" (pw:t6 -> the additivity animation) */
export function placeProbe(player, mode) {
  clearProbes(player);
  const l = player.location;
  const loc = { x: Math.floor(l.x) + 0.5, y: l.y + 0.12, z: Math.floor(l.z) + 0.5 - PROBE_DISTANCE };
  let e;
  try { e = player.dimension.spawnEntity(PROBE_ID, loc); } catch (err) { log(`PROBE FAILED (is PW-TestRunner RP + BP 0.2.2 attached?): ${short(err, 50)}`); return undefined; }
  try { e.addTag(PROBE_TAG); } catch { /* ignore */ }
  try { e.setRotation({ x: 0, y: 0 }); } catch { /* ignore */ }
  if (mode === "anim") { try { e.triggerEvent("pw:t6"); } catch (err) { log(`probe pw:t6 FAILED: ${short(err, 50)}`); } }
  log(`PROBE ${mode} at ${Math.floor(loc.x)},${Math.floor(loc.y)},${Math.floor(loc.z)} facing SOUTH (its nose toward you; you face NORTH)`);
  return e;
}

// ---------------------------------------------------------------------------------------------------------------------
// the pen
// ---------------------------------------------------------------------------------------------------------------------
function penCells(c, roof, half = PEN_HALF, height = PEN_HEIGHT, halfz = half) {
  const cells = [];
  for (let dx = -half - 1; dx <= half + 1; dx++) {
    for (let dz = -halfz - 1; dz <= halfz + 1; dz++) {
      const wall = Math.abs(dx) === half + 1 || Math.abs(dz) === halfz + 1;
      for (let dy = 0; dy < height; dy++) cells.push({ x: c.x + dx, y: c.y + dy, z: c.z + dz, kind: wall ? "wall" : "in" });
      if (!wall) cells.push({ x: c.x + dx, y: c.y - 1, z: c.z + dz, kind: "floor" });
      if (roof) cells.push({ x: c.x + dx, y: c.y + height, z: c.z + dz, kind: "wall" });   // v0.2.2: barrier ceiling = no sky light
    }
  }
  return cells;
}
function remember(list, block) {
  let id = "minecraft:air", states = {};
  try { const p = block.permutation; id = p.type.id; try { states = p.getAllStates(); } catch { states = {}; } } catch { /* ignore */ }
  list.push({ x: block.location.x, y: block.location.y, z: block.location.z, id, states });
}
function setBlockId(block, id) {
  try { block.setType(id); return true; } catch (e) { log(`setType ${id} at ${block.location.x},${block.location.y},${block.location.z}: ${short(e, 40)}`); return false; }
}
/** Build the pen around centre block c (feet level = c.y). Returns the remembered-block list. */
function buildPen(dim, c, water, roof, half = PEN_HALF, height = PEN_HEIGHT, depth = 2, halfz = half) {
  const changed = [];
  for (const cell of penCells(c, roof, half, height, halfz)) {
    let b; try { b = dim.getBlock(cell); } catch { b = undefined; }
    if (!b) { log(`pen: cell ${cell.x},${cell.y},${cell.z} not loaded`); continue; }
    if (cell.kind === "wall") {
      if (b.typeId === "minecraft:barrier") continue;
      remember(changed, b); setBlockId(b, "minecraft:barrier");
    } else if (cell.kind === "in") {
      const want = water && cell.y <= c.y + depth - 1 ? "minecraft:water" : "minecraft:air";
      if (b.typeId === want) continue;
      remember(changed, b); setBlockId(b, want);
    } else {                                                             // floor: solid stays, air/liquid becomes stone
      if (!b.isAir && !b.isLiquid) continue;
      remember(changed, b); setBlockId(b, "minecraft:stone");
    }
  }
  return changed;
}
function restoreBlocks(dim, list) {
  let n = 0;
  for (const r of list || []) {
    try {
      const b = dim.getBlock({ x: r.x, y: r.y, z: r.z }); if (!b) continue;
      let perm = null;
      try { perm = BlockPermutation.resolve(r.id, r.states || {}); } catch { perm = null; }
      if (perm) b.setPermutation(perm); else b.setType(r.id);
      n++;
    } catch (e) { log(`restore ${r.id} at ${r.x},${r.y},${r.z}: ${short(e, 40)}`); }
  }
  return n;
}

// ---------------------------------------------------------------------------------------------------------------------
// rig a mob / clear
// ---------------------------------------------------------------------------------------------------------------------
/** spec = { mob: "minecraft:fox", water?: bool, baby?: bool, fly?: bool, event?: string, label?: string, props?: {name: value}, name?: string (v0.3.5 name tag),
 *          item?: string (v0.3.7 main hand), armor?: string (v0.3.9 body slot), row?: [{ mob, dx, label?, event?, props?, name?, item?, armor? }] } */
/** Grow a rigged mob up if (and only if) it is a baby: minecraft:ageable_grow_up for ageable mobs, minecraft:as_adult for the
 *  zombie family. Adults are left alone, silently. */
function growUp(e) {
  let baby = false;
  try { baby = !!e.hasComponent("minecraft:is_baby"); } catch { baby = false; }
  if (!baby) return false;
  let ok = false;
  for (const evt of ["minecraft:ageable_grow_up", "minecraft:as_adult"]) {
    try { e.triggerEvent(evt); ok = true; } catch { /* not this mob's event */ }
  }
  log(ok ? "RIG baby grown up" : "RIG baby could not be grown up (no grow-up event on this mob)");
  return ok;
}
/** v0.3.4: set entity properties (e.g. the chicken's minecraft:climate_variant - the biome picks it at spawn; extreme_hills gives the
 *  dark COLD chicken). Applied right after the spawn and again 5 ticks later (a spawn event may set it a tick late). Logged either way. */
function applyProps(e, props, label) {
  if (!props) return;
  const put = (again) => {
    for (const [k, v] of Object.entries(props)) {
      try { e.setProperty(k, v); if (!again) log(`RIG property ${k}=${v} on ${label}`); }
      catch (err) { if (!again) log(`RIG property ${k}=${v} FAILED on ${label}: ${short(err, 40)}`); }
    }
  };
  put(false);
  system.runTimeout(() => { try { if (e.isValid) put(true); } catch { /* gone */ } }, 5);
}
/** v0.3.7: hand a rigged mob an item (main hand) - replaceitem, logged either way.
 *  v0.4.3 (D-C310): the log no longer takes replaceitem's word for it. 2 ticks later a testfor with hasitem asks the game whether
 *  the item really IS in the main hand: 'CONFIRMED in' (it holds it - a missing item on screen is then a drawing problem) or
 *  'NOT in' (the game never gave it the item). If the check itself errors, its message is logged so he can copy it. */
function equip(e, item, label) {
  if (!item) return;
  const id = item.includes(":") ? item : `minecraft:${item}`;
  const name = id.replace("minecraft:", "");
  try { e.runCommand(`replaceitem entity @s slot.weapon.mainhand 0 ${id}`); }
  catch (err) { log(`RIG item ${name} FAILED on ${label}: ${short(err, 40)}`); return; }
  system.runTimeout(() => {
    try { if (!e.isValid) return; } catch { return; }
    try {
      const r = e.runCommand(`testfor @s[hasitem={item=${name},location=slot.weapon.mainhand}]`);
      log((r && r.successCount > 0) ? `RIG item ${name} CONFIRMED in ${label}'s main hand` : `RIG item ${name} NOT in ${label}'s main hand (the game did not keep it)`);
    } catch (err) { log(`RIG item ${name} NOT in ${label}'s main hand? (check said: ${short(err, 60)})`); }
  }, 2);
}
/** v0.3.9 (D-C288): put body armor on a rigged mob (wolf armor) - replaceitem slot.armor.body, logged either way. */
function armorOn(e, item, label) {
  if (!item) return;
  const id = item.includes(":") ? item : `minecraft:${item}`;
  try { e.runCommand(`replaceitem entity @s slot.armor.body 0 ${id}`); log(`RIG armor ${id.replace("minecraft:", "")} on ${label}`); }
  catch (err) { log(`RIG armor ${id} FAILED on ${label}: ${short(err, 40)}`); }
}
// v0.5.8 (D-C398, p21): a rigged mob can PLAY one animation (spec.play / row[].play = the full animation id), re-started every
// PLAY_EVERY ticks so a one-shot clip (attack, eat) keeps showing; the controller name keeps it apart from the mob's own.
const PLAY_EVERY = 60;
const playing = new Map();          // entity -> animation id
function playOn(e, id, label) {
  if (!id) return;
  try { e.playAnimation(id, { blendOutTime: 0.1, controller: "pw_parade", stopExpression: "false" }); playing.set(e, id);
        log(`RIG play ${short(id.replace(/^animation\.std\./, ""), 60)} on ${label}`); }
  catch (err) { log(`RIG play ${short(id, 50)} FAILED on ${label}: ${short(err, 40)}`); }
}
let playTick = 0;
system.runInterval(() => {
  if (++playTick % PLAY_EVERY) return;
  for (const [e, id] of [...playing]) {
    let ok = false; try { ok = e.isValid; } catch { ok = false; }
    if (!ok) { playing.delete(e); continue; }
    try { e.playAnimation(id, { blendOutTime: 0.1, controller: "pw_parade", stopExpression: "false" }); } catch { /* gone */ }
  }
}, 1);
const MAX_REROLL = 30;
function fullId(m) { return m.includes(":") ? m : `minecraft:${m}`; }
/** v0.4.1: one rigged mob (the main one: dx 0, isMain) — the spawn and everything the spec asks for, as 0.4.0 did inline */
function spawnOne(dim, hold, m, spec) {
  const r = m.r; const rid = fullId(r.mob); const label = r.label || rid;
  const x = dim.spawnEntity(rid, { x: hold.x + m.dx, y: hold.y, z: hold.z });
  try { x.addTag(RIG_TAG); if (!m.isMain) x.addTag(`pw_rig_dx_${m.dx}`); if (spec.free) x.addTag("pw_rig_free"); } catch { /* ignore */ }
  if (m.isMain) {
    // v0.3.1 / v0.4.0: an explicit event; a requested baby is born; otherwise the grow-up runs (babies only) now and 5 ticks later
    if (spec.event && !spec.baby) { try { x.triggerEvent(spec.event); } catch (err) { log(`rig event ${spec.event} FAILED: ${short(err, 40)}`); } }
    if (spec.baby) {
      const evt = spec.event || "minecraft:entity_born";
      try { x.triggerEvent(evt); } catch (err) { log(`rig event ${evt} FAILED: ${short(err, 40)}`); }
    }
  } else if (r.event) { try { x.triggerEvent(r.event); } catch (err) { log(`RIG row event ${r.event} FAILED: ${short(err, 40)}`); } }   // v0.3.3
  if (!(m.isMain && spec.baby)) { growUp(x); system.runTimeout(() => { try { if (x.isValid) growUp(x); } catch { /* gone */ } }, 5); }
  applyProps(x, r.props, label);                                                                        // v0.3.4
  if (r.name) { try { x.nameTag = r.name; log(`RIG name tag "${r.name}" on ${label}`); } catch (err) { log(`RIG name tag FAILED on ${label}: ${short(err, 40)}`); } }   // v0.3.5
  equip(x, r.item, label);                                                                              // v0.3.7
  armorOn(x, r.armor, label);                                                                           // v0.3.9
  playOn(x, r.play, label);                                                                             // v0.5.8
  try { x.addEffect("fire_resistance", 20 * 60 * 30, { amplifier: 0, showParticles: false }); } catch { /* ignore */ }
  if (m.isMain) { try { x.setRotation({ x: 0, y: 0 }); } catch { /* ignore */ } }
  if (!spec.free) { try { x.addEffect("slowness", 20 * 60 * 30, { amplifier: 255, showParticles: false }); } catch { /* fish etc. may refuse effects */ } }
  if (!m.isMain) log(`RIG row ${label} at x ${m.dx > 0 ? "+" : ""}${m.dx}`);
  return x;
}
/** v0.4.1: 6 ticks after the spawn (the grow-up has had its retry): a baby that should be grown, or the wrong colour, is summoned
 *  again (up to MAX_REROLL); the age (and colour) of every settled mob is logged as in 0.4.0 */
function settle(dim, hold, spec, list, attempt) {
  system.runTimeout(() => {
    const redo = [];
    for (const it of list) {
      const x = it.e; let ok = false; try { ok = !!x && x.isValid; } catch { ok = false; }
      if (!ok) continue;
      let baby = false; try { baby = !!x.hasComponent("minecraft:is_baby"); } catch { baby = false; }
      let variant; try { variant = x.getComponent("minecraft:variant")?.value; } catch { variant = undefined; }
      const want = it.m.r.variant; const wantBaby = it.m.isMain ? !!spec.baby : !!it.m.r.baby;
      const why = baby && !wantBaby ? "still a BABY - no grow-up event on this mob" : (want !== undefined && variant !== want ? `colour ${variant}, want ${want}` : "");
      if (why && attempt < MAX_REROLL) { redo.push([it, why]); continue; }
      const name = x.typeId.replace("minecraft:", "");
      log(`RIG age ${name} at x ${it.m.dx}: ${baby ? "BABY" : "adult"}${want !== undefined ? ` · colour ${variant}${variant === want ? "" : ` (WANTED ${want})`}` : ""}${why ? ` · gave up after ${attempt} re-rolls` : ""}`);
    }
    for (const [it, why] of redo) {
      try { it.e.remove(); } catch { /* gone */ }
      try { it.e = spawnOne(dim, hold, it.m, spec); log(`RIG re-roll ${it.m.r.label || it.m.r.mob} (${why}) try ${attempt + 1}`); }
      catch (err) { log(`RIG re-roll FAILED ${it.m.r.mob}: ${short(err, 50)}`); it.e = undefined; }
    }
    if (redo.length) settle(dim, hold, spec, redo.map(([it]) => it), attempt + 1);
  }, 6);
}
/** v0.4.1: a jukebox inside the pen (remembered + restored like the pen), and a disc started by script when the API allows */
/** v0.4.3 (p12 t01): blocks set inside the pen after it is built - [{ id, from: [dx,dy,dz], to: [dx,dy,dz] }, ...] relative to the
 *  pen centre at feet level, applied in order (a later box overwrites an earlier one). Each cell is remembered once (its pre-rig
 *  block), so clearing the rig puts back what was there - the same as the pen walls. */
function placeBlocks(dim, c, boxes, changed) {
  for (const bx of boxes || []) {
    const id = fullId(bx.id); let n = 0, miss = 0;
    const lo = [0, 1, 2].map((i) => Math.min(bx.from[i], bx.to[i])), hi = [0, 1, 2].map((i) => Math.max(bx.from[i], bx.to[i]));
    for (let x = lo[0]; x <= hi[0]; x++) for (let y = lo[1]; y <= hi[1]; y++) for (let z = lo[2]; z <= hi[2]; z++) {
      const cell = { x: c.x + x, y: c.y + y, z: c.z + z };
      let b; try { b = dim.getBlock(cell); } catch { b = undefined; }
      if (!b) { miss++; continue; }
      if (!changed.some((q) => q.x === cell.x && q.y === cell.y && q.z === cell.z)) remember(changed, b);
      if (setBlockId(b, id)) n++;
    }
    log(`RIG blocks ${id.replace("minecraft:", "")} x${n}${miss ? ` (${miss} not loaded)` : ""} at dx ${lo[0]}..${hi[0]} dy ${lo[1]}..${hi[1]} dz ${lo[2]}..${hi[2]}`);
  }
}
function placeJukebox(dim, c, jb, changed) {
  const cell = { x: c.x + (jb.dx || 0), y: c.y, z: c.z + (jb.dz || 0) };
  let b; try { b = dim.getBlock(cell); } catch { b = undefined; }
  if (!b) { log(`RIG jukebox: cell ${cell.x},${cell.y},${cell.z} not loaded`); return; }
  if (!changed.some((q) => q.x === cell.x && q.y === cell.y && q.z === cell.z)) remember(changed, b);   // restore = the pre-rig block, once
  setBlockId(b, "minecraft:jukebox");
  const disc = fullId(jb.disc || "music_disc_cat");
  try {
    const rp = b.getComponent("minecraft:record_player");
    if (!rp) throw new Error("no record_player component");
    rp.setRecord(disc, true);
    log(`RIG jukebox at ${cell.x},${cell.y},${cell.z} playing ${disc.replace("minecraft:", "")} (started by script)`);
  } catch (err) {
    log(`RIG jukebox at ${cell.x},${cell.y},${cell.z} placed; the script could not start a disc (${short(err, 40)}) - use the commands in the step text`);
  }
}
export function rigMob(player, spec) {
  loadRig();
  clearRig(player);
  const dim = player.dimension; const l = player.location;
  const half = spec.half || PEN_HALF, height = spec.height || PEN_HEIGHT, depth = spec.depth || 2;
  const halfz = spec.halfz || half;                                    // v0.3.2: a wide row pen keeps its depth; a big pen moves north
  const c = { x: Math.floor(l.x), y: Math.floor(l.y), z: Math.floor(l.z) - Math.max(PEN_DISTANCE, halfz + 3) };   // south wall >= 2 blocks ahead
  const water = !!spec.water; const roof = !!spec.roof;
  if (water) snapshotWater(dim, { centre: c, half, halfz, height });                // v0.4.1: before the pool exists
  const changed = buildPen(dim, c, water, roof, half, height, depth, halfz);
  if (spec.jukebox) placeJukebox(dim, c, spec.jukebox, changed);
  if (spec.boxes) placeBlocks(dim, c, spec.boxes, changed);          // v0.4.3
  const hold = { x: c.x + 0.5, y: c.y + (water ? 0.5 : spec.fly ? 1.0 : 0.0), z: c.z + 0.5, yaw: 0 };
  const id = fullId(spec.mob);
  let e;
  let spawnError = "";
  const list = [];
  // v0.3.2: the row — more mobs beside the main one, each held at its own x offset (tag pw_rig_dx_<n>)
  for (const r of spec.row || []) {
    const m = { r, dx: r.dx, isMain: false };
    try { list.push({ m, e: spawnOne(dim, hold, m, spec) }); }
    catch (err) { log(`RIG row spawn FAILED ${fullId(r.mob)}: ${short(err, 50)}`); if (!spawnError) spawnError = `${r.label || r.mob}: ${short(err, 50)}`; }
  }
  const mm = { r: spec, dx: 0, isMain: true };
  try { e = spawnOne(dim, hold, mm, spec); list.push({ m: mm, e }); }
  catch (err) {
    spawnError = /hostile/i.test(String(err)) ? "hostile spawns are off - Settings > Game > Difficulty: Easy, then Repeat setup" : short(err, 70);
    log(`RIG spawn FAILED ${id}: ${short(err, 50)}`);
    if (/hostile/i.test(String(err))) log("RIG hint: this world blocks hostile mobs (Peaceful) - set Difficulty to Easy, then Repeat setup");
  }
  settle(dim, hold, spec, list, 0);
  // v0.4.1: where YOU stand (his R12 swim buttons in z08 / w10)
  try {
    const feet = dim.getBlock({ x: Math.floor(l.x), y: Math.floor(l.y), z: Math.floor(l.z) });
    if (feet && (feet.typeId.includes("water") || ICE.has(feet.typeId))) log(`RIG note: you stand in ${feet.typeId.replace("minecraft:", "")} at ${Math.floor(l.x)},${Math.floor(l.y)},${Math.floor(l.z)}`);
  } catch { /* ignore */ }
  R = { v: 1, dim: dim.id, centre: c, hold, mob: id, water, roof, half, halfz, height, depth, free: !!spec.free, cells: changed, since: Date.now(), spawnError };
  saveRig();
  log(`RIG ${spec.label || id} ${water ? `in a ${depth}-deep pool` : roof ? "in the roofed pen" : "in the pen"}${spec.free ? " (FREE: not held)" : ""} at ${c.x},${c.y},${c.z} facing SOUTH · ${changed.length} blocks replaced (restored on clear)`);
  return e;
}
/** v0.4.1: after a POOL rig is cleared, water / ice left around its footprint (+4 blocks, floor..roof+1) that the rig did not
 *  remember is removed and counted (his R12: the swim buttons one block south of later pens) */
function sweepBox(r) {
  const half = r.half || PEN_HALF, halfz = r.halfz || half, height = r.height || PEN_HEIGHT, c = r.centre;
  return { x0: c.x - half - 5, x1: c.x + half + 5, z0: c.z - halfz - 5, z1: c.z + halfz + 5, y0: c.y - 1, y1: c.y + height + 1 };
}
function isWet(t) { return t === "minecraft:water" || t === "minecraft:flowing_water" || ICE.has(t); }
function eachCell(box, fn) {
  for (let x = box.x0; x <= box.x1; x++) for (let z = box.z0; z <= box.z1; z++) for (let y = box.y0; y <= box.y1; y++) fn(x, y, z);
}
/** v0.4.1: before a pool is built, remember every water / ice cell already in the sweep box (a lake, a river, a leftover) */
function snapshotWater(dim, r) {
  const pre = [];
  eachCell(sweepBox(r), (x, y, z) => {
    let b; try { b = dim.getBlock({ x, y, z }); } catch { b = undefined; }
    if (b && isWet(b.typeId)) pre.push(`${x},${y},${z}`);
  });
  try { world.setDynamicProperty(PRE_KEY, JSON.stringify({ n: pre.length, cells: pre.slice(0, PRE_CAP) })); }
  catch (e) { log(`rig pre-water save failed: ${short(e, 50)}`); }
  if (pre.length) log(`RIG pool: ${pre.length} water / ice cell(s) already around it - the sweep will leave them`);
  return pre.length;
}
function sweepWater(dim, r) {
  let pre = { n: 0, cells: [] };
  try { const raw = world.getDynamicProperty(PRE_KEY); if (typeof raw === "string" && raw) pre = JSON.parse(raw); } catch { pre = { n: 0, cells: [] }; }
  try { world.setDynamicProperty(PRE_KEY, undefined); } catch { /* ignore */ }
  if ((pre.n || 0) > PRE_CAP) { log(`RIG sweep skipped: ${pre.n} water / ice cells were already around the pool (a lake or river?)`); return 0; }
  const seen = new Set([...(r.cells || []).map((q) => `${q.x},${q.y},${q.z}`), ...(pre.cells || [])]);
  let n = 0; const at = [];
  eachCell(sweepBox(r), (x, y, z) => {
    if (seen.has(`${x},${y},${z}`)) return;
    let b; try { b = dim.getBlock({ x, y, z }); } catch { b = undefined; }
    if (b && isWet(b.typeId) && setBlockId(b, "minecraft:air")) { n++; if (at.length < 3) at.push(`${x},${y},${z}`); }
  });
  if (n) log(`RIG leftover water swept: ${n} cell(s) around the old pool (e.g. ${at.join(" ")})`);
  return n;
}
export function clearRig(player) {
  loadRig();
  const dim = player.dimension;
  const n = removeTagged(dim, RIG_TAG);
  let restored = 0;
  if (R && R.cells) restored = restoreBlocks(dim, R.cells);
  if (R || n) log(`RIG cleared: ${n} mob(s) removed, ${restored} block(s) restored`);
  if (R && R.water && R.centre) { try { sweepWater(dim, R); } catch (e) { log(`RIG sweep: ${short(e, 50)}`); } }
  R = null; saveRig();
}
export function clearAll(player) { clearProbes(player); clearRig(player); }
/** { mob, water, spawnError } for the bar; null when nothing is rigged. */
export function rigStatus() { if (!loadRig() || !R) return null; return { mob: R.mob, water: !!R.water, spawnError: R.spawnError || "" }; }

// the pool freezes in cold biomes (extreme_hills froze it during the P0 run): put the water back every second
const ICE = new Set(["minecraft:ice", "minecraft:frosted_ice", "minecraft:packed_ice", "minecraft:blue_ice"]);
function meltPool(dim) {
  if (!R || !R.water || !R.centre) return 0;
  let n = 0;
  for (const cell of penCells(R.centre, false, R.half || PEN_HALF, R.height || PEN_HEIGHT, R.halfz || R.half || PEN_HALF)) {
    if (cell.kind !== "in" || cell.y > R.centre.y + (R.depth || 2) - 1) continue;
    let b; try { b = dim.getBlock(cell); } catch { b = undefined; }
    if (b && ICE.has(b.typeId)) { if (setBlockId(b, "minecraft:water")) n++; }
  }
  if (n) log(`RIG pool re-melted ${n} ice block(s)`);
  return n;
}

/** v0.4.1 (D-C303): put the pen back where a tap broke it. Walls / roof: only cells the rig itself turned into barrier (remembered,
 *  so the clear restores them); pool floor: any floor cell under the water that is air or liquid. Logged once per cell per rig. */
let healKey = null, healOwned = null, healSeen = new Set();
function healPen(dim) {
  if (!R || !R.centre) return 0;
  if (healKey !== R.since) {
    healKey = R.since; healSeen = new Set();
    healOwned = new Set((R.cells || []).map((q) => `${q.x},${q.y},${q.z}`));
  }
  let n = 0;
  for (const cell of penCells(R.centre, R.roof, R.half || PEN_HALF, R.height || PEN_HEIGHT, R.halfz || R.half || PEN_HALF)) {
    if (cell.kind === "in") continue;
    const k = `${cell.x},${cell.y},${cell.z}`;
    if (cell.kind === "wall" && !healOwned.has(k)) continue;
    if (cell.kind === "floor" && !R.water) continue;
    let b; try { b = dim.getBlock(cell); } catch { b = undefined; }
    if (!b) continue;
    const t = b.typeId;
    if (cell.kind === "wall") {
      if (t === "minecraft:barrier") continue;
      if (setBlockId(b, "minecraft:barrier")) { n++; if (!healSeen.has(k)) { healSeen.add(k); log(`RIG pen wall broken at ${k} (${t.replace("minecraft:", "")}) - put back`); } }
    } else {
      if (!b.isAir && !b.isLiquid) continue;
      if (setBlockId(b, "minecraft:stone")) { n++; if (!healSeen.has(k)) { healSeen.add(k); log(`RIG pool floor open at ${k} - filled with stone`); } }
    }
  }
  return n;
}

// the hold loop: every tick the rigged mob goes back to its spot facing south; slowness re-applied every 30 s
let holdTicks = 0;
export function holdTick() {
  if (!loadRig() || !R) return;
  holdTicks++;
  let dim; try { dim = world.getDimension(R.dim); } catch { return; }
  if (holdTicks % 20 === 0) meltPool(dim);
  if (holdTicks % HEAL_EVERY === 0) { try { healPen(dim); } catch (e) { log(`RIG pen repair: ${short(e, 50)}`); } }
  let ents; try { ents = dim.getEntities({ tags: [RIG_TAG] }); } catch { return; }
  for (const e of ents) {
    let tags = []; try { tags = e.getTags(); } catch { tags = []; }
    if (tags.includes("pw_rig_free")) continue;                                  // v0.3.2: free mobs walk / swim inside the pen
    const dt = tags.find((t) => t.startsWith("pw_rig_dx_")); const dx = dt ? Number(dt.slice(10)) || 0 : 0;
    try { e.teleport({ x: R.hold.x + dx, y: R.hold.y, z: R.hold.z }, { rotation: { x: 0, y: R.hold.yaw || 0 }, keepVelocity: false }); } catch { /* ignore */ }
    try { e.clearVelocity(); } catch { /* ignore */ }
    if (holdTicks % 600 === 0) { try { e.addEffect("slowness", 20 * 60 * 30, { amplifier: 255, showParticles: false }); } catch { /* ignore */ } }
  }
}
system.runInterval(holdTick, 1);
