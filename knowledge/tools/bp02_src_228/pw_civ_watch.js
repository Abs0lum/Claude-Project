// pw_civ_watch.js — CIVITAS PATROLS (F5; his 22:08 ruling D-C538): "managing monsters and their spawn abilities with
// patrols — both above ground, and below ground". Utopia-First: the watch guards against MONSTERS only (no crime yet).
//
// THE WATCH (an office from village III: 1, town I: 2 ... city I: 6, more per tier) walks the settlement's streets at night,
// stop to stop (every PATROL_STEP cells of every street, the square), and goes BELOW GROUND where a street has two laid
// manholes: it unlocks the cover with its registered key (F4: the watch is a sewer post, one key per watch), climbs down the
// ladder, walks the sewer hall to the next manhole, climbs up and locks the cover behind it. THE SEWER KEEPER does the same
// rounds below ground by day (inspection). A monster within STRIKE of a watch on duty is struck (a scripted blow every
// STRIKE_TICKS — the engine's villagers have no attack); one within CHASE draws the watch toward it (above ground).
// Kills, monsters seen and the rounds done are counted per settlement (the spawn-pressure dial, D-C538).
// Climbing is scripted (the engine's villagers do not path on ladders): one ladder rung per CLIMB_TICKS, the villager
// moved along its own shaft — never across space.
// 1.3.228 (B1): the beat is a heartbeat slot (pw_civ_beat.js: 5 and 15 of 20); the post holders come from the shared bodies
// cache; the covers are read through the clock's guarded API.blockAt
import { world, system, EntityDamageCause, BlockPermutation } from "@minecraft/server";
import * as WALK from "./pw_civ_walk.js";
import * as HB from "./pw_civ_beat.js";
import { halfRounds } from "./pw_civ_people.js";      // 1.3.228 (B10 / WP1): an unpaid, low-morale watchman walks half his rounds

let API = null;
export function initWatch(api) { API = api; }

export const WATCH_POSTS = { village3: 1, town: 2, town2: 3, town3: 4, city: 6, city2: 8, city3: 10, metropolis: 12, metropolis2: 14, metropolis3: 16, capital: 20 };
const PATROL_STEP = 24;                 // a stop every 24 cells of street
const NIGHT = [13000, 23000];           // the watch's hours (the sewer keeper works the day: 1000..11000)
const STRIKE = 3.2, CHASE = 16, STRIKE_TICKS = 20, STRIKE_DMG = 6;
const CLIMB_TICKS = 6;
const BEAT = 10;
const state = new Map();                // villager id -> { st, i (stop), mode, below: {...}, lastStrike }
const HOSTILE = ["minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:skeleton", "minecraft:stray", "minecraft:spider", "minecraft:cave_spider",
                 "minecraft:creeper", "minecraft:witch", "minecraft:zombie_villager_v2", "minecraft:slime", "minecraft:silverfish", "minecraft:pillager", "minecraft:vindicator", "minecraft:bogged"];

/** the stops of a settlement's round: every PATROL_STEP cells of every kit street (centre line, feet level), the square; a
 *  stop on a laid manhole with another laid manhole further along the same street carries the way below */
export function stopsOf(st) {
  const out = [];
  if (st.square) out.push({ x: st.square.x + 6, y: st.square.y + 1, z: st.square.z + 6, kind: "square" });
  for (const street of (st.streets || []).filter((x) => x.kind === "kit" && x.H && x.H.length)) {
    const laid = (street.manholes || []).filter((m) => m.laid).sort((a, b) => a.t - b.t);
    const tmax = street.tmin + street.H.length - 1;
    for (let t = street.tmin + 6; t <= tmax - 6; t += PATROL_STEP) {
      const H = API.kitHAt(street, t);
      if (H === undefined) continue;
      const [x, z] = API.cellOf(street.f, t, 6);
      out.push({ x, y: H + 1, z, kind: "street", sid: street.id, t });
    }
    // (review 10-04: manholes alternate sides; a pair on opposite sides crossed the open trench at the far end) the way below
    // runs from a manhole to the next one on the SAME side of the street
    for (let k = 0; k < laid.length; k++) {
      const a = laid[k], b = laid.slice(k + 1).find((m) => m.side === a.side);
      if (!b) continue;
      const Ha = API.kitHAt(street, a.t), Hb = API.kitHAt(street, b.t);
      if (Ha === undefined || Hb === undefined) continue;
      // a bridge between them has no hall (its abutments close the tunnel): no way below there
      if ((street.segs || []).some((q) => q.kind === "bridge" && street.tmin + q.a + q.len > a.t && street.tmin + q.a < b.t)) continue;
      const [ax, az] = API.cellOf(street.f, a.t, a.side < 0 ? 1 : 11);
      out.push({ x: ax, y: Ha + 1, z: az, kind: "manhole", sid: street.id, from: a, to: b });
    }
  }
  return out;
}
function onNight(tod) { return tod >= NIGHT[0] && tod < NIGHT[1]; }
function onDay(tod) { return tod >= 1000 && tod < 11000; }

/** the hall walk below one street from manhole a to manhole b: waypoints at the hall's side lane (w5 / w7), feet H - 11 */
function hallPath(street, a, b) {
  const pts = [];
  const lane = a.side < 0 ? 5 : 7;
  const [sx, sz] = API.cellOf(street.f, a.t, a.side < 0 ? 1 : 11);
  pts.push([sx, sz, API.kitHAt(street, a.t) - 11]);
  for (let w = a.side < 0 ? 2 : 10; a.side < 0 ? w <= lane : w >= lane; w += a.side < 0 ? 1 : -1) { const [x, z] = API.cellOf(street.f, a.t, w); pts.push([x, z, API.kitHAt(street, a.t) - 11]); }
  const step = b.t > a.t ? 1 : -1;
  for (let t = a.t + step; t !== b.t + step; t += step) { const H = API.kitHAt(street, t); if (H === undefined) continue; const [x, z] = API.cellOf(street.f, t, lane); pts.push([x, z, H - 11]); }
  const side2 = b.side < 0 ? 1 : 11;
  for (let w = lane; b.side < 0 ? w >= side2 : w <= side2; w += b.side < 0 ? -1 : 1) { const [x, z] = API.cellOf(street.f, b.t, w); pts.push([x, z, API.kitHAt(street, b.t) - 11]); }
  return pts;
}

/** the watch and the sewer keeper of a settlement (embodied villagers whose census person holds the post) */
function postHolders(st) {
  const out = [];
  const vs = HB.bodiesOf(st);                                       // 1.3.228 (B1 / BF1): the shared bodies cache (was a query every 10 ticks)
  for (const v of vs) {
    const p = API.personOf(v, st);
    if (p && (p.job === "watch" || p.job === "sewer_keeper")) out.push([v, p]);
  }
  return out;
}
function count(st, k, n = 1) { st.watch = st.watch || { rounds: 0, kills: 0, seen: 0, below: 0, strikes: 0, climbs: 0, keyless: 0 }; st.watch[k] = (st.watch[k] || 0) + n; }

/** the cover at a shaft: open (phase 5) / shut (phase 0) — only with a registered key (the register is the lock) */
function cover(dim, x, y, z, open) {
  try {
    const b = API.blockAt(dim, x, y, z);                              // 1.3.228: guarded
    if (!b || b.typeId !== "pw:manhole_cover") return false;
    API.slideCover(b, open ? 5 : 0);
    return true;
  } catch { return false; }
}

// a monster that dies of a watchman's blow is counted for his town (0.0.23: 14 strikes, the three zombies gone in 20 s, but
// "kills 0": the blow's tick still saw them alive)
world.afterEvents.entityDie.subscribe((ev) => {
  try {
    const d = ev.damageSource && ev.damageSource.damagingEntity;
    if (!d || !d.hasTag || !d.hasTag("civ:watching")) return;
    const w = state.get(d.id);
    if (!w) return;
    const st = API.stOf(w.st);
    if (st) count(st, "kills");
  } catch { /* left */ }
});
HB.register("watch", { fn: () => {                                      // 1.3.228 (B1 / BF1): heartbeat slots 5, 15 (every BEAT = 10)
  if (!API) return;
  const s = API.load();
  let tod;
  // a watchman whose body is gone (the census removed it) is forgotten (0.0.23: a stale "below-walk" stayed in the status)
  if (system.currentTick % 200 < BEAT) {
    for (const vid of [...state.keys()]) { let v; try { v = world.getEntity(vid); } catch { v = undefined; } if (!v || !v.isValid) state.delete(vid); }
    // (review 10-04: the tag outlived its entry after a reload / a lost post: the schedule then ignored the villager)
    // 1.3.228 (B1 / BF1): the shared bodies cache (was a whole-dimension query per settlement)
    for (const st of s.settlements) { try { for (const v of HB.bodiesOf(st)) if (v.hasTag("civ:watching") && !state.has(v.id)) v.removeTag("civ:watching"); } catch { /* left */ } }
  }
  try { tod = world.getTimeOfDay(); } catch { return; }
  const now = system.currentTick;
  for (const st of s.settlements) {
    if (!st.kit || !st.square || st.phase !== "built") continue;
    let dim;
    try { dim = world.getDimension(st.dim); } catch { continue; }
    const holders = postHolders(st);
    if (!holders.length) continue;
    let stops = null;
    for (const [v, p] of holders) {
      // 1.3.228 (B4 / BF5): his own shift — the watch's night template, the sewer keeper's day one, the id's offset, the days off
      const duty = API.onShift ? API.onShift(p, st, tod) : (p.job === "watch" ? onNight(tod) : onDay(tod));
      let w = state.get(v.id);
      if (!duty) {
        if (w && w.mode && w.mode.startsWith("below")) { /* finish the round below before going home */ }
        else { if (w) { state.delete(v.id); v.removeTag("civ:watching"); try { v.triggerEvent("pw:brisk_off"); } catch { /* left */ } } continue; }   // 1.3.220: back to the civ pace
      }
      if (!w) { w = { st: st.id, i: Math.floor(Math.random() * 1000), mode: "walk", lastStrike: 0 }; state.set(v.id, w); }
      if (!v.hasTag("civ:watching")) { v.addTag("civ:watching"); try { v.addEffect("resistance", 400, { amplifier: 1, showParticles: false }); } catch { /* left */ } try { v.triggerEvent("pw:brisk_on"); } catch { /* left */ } }   // 1.3.220 (his 19:35): civs walk at half speed; the watch on duty keeps the old pace
      // MONSTERS: strike within reach, chase within sight (above ground only; below, the hall is lit and narrow)
      let near = null, nd = Infinity;
      try {
        for (const e of dim.getEntities({ location: v.location, maxDistance: CHASE, families: ["monster"] })) {
          if (!e.isValid) continue;
          if (!HOSTILE.includes(e.typeId) && !(e.typeId.startsWith("pw:") || e.typeId.startsWith("sf_nba:"))) continue;
          const d = Math.hypot(e.location.x - v.location.x, e.location.z - v.location.z);
          if (Math.abs(e.location.y - v.location.y) > 4) continue;
          if (d < nd) { nd = d; near = e; }
        }
      } catch { near = null; }
      if (near) {
        if (!w.seen || w.seen !== near.id) { w.seen = near.id; count(st, "seen"); }
        if (nd <= STRIKE && now - w.lastStrike >= STRIKE_TICKS) {
          w.lastStrike = now;
          try { near.applyDamage(STRIKE_DMG, { cause: EntityDamageCause.entityAttack, damagingEntity: v }); count(st, "strikes"); } catch { /* left */ }
          try { v.dimension.playSound("game.player.attack.strong", v.location, { volume: 0.8 }); } catch { /* left */ }
          continue;
        }
        if (w.mode === "walk" && p.job === "watch") {
          if (!w.chaseAt || now - w.chaseAt >= 40) { w.chaseAt = now; WALK.send(v, API.stOf(w.st), { x: near.location.x, y: near.location.y, z: near.location.z }); }   // (review: re-planned every beat)
          continue;
        }
      }
      // THE ROUND
      if (w.mode === "walk") {
        stops = stops || stopsOf(st);
        if (!stops.length) continue;
        let stop = stops[w.i % stops.length];
        if (p.job === "sewer_keeper" && stop.kind !== "manhole") {                // (review 10-04: forward from here, not always the first)
          const from = w.i % stops.length;
          let j = stops.findIndex((x, i2) => i2 >= from && x.kind === "manhole");
          if (j < 0) j = stops.findIndex((x) => x.kind === "manhole");
          if (j < 0) continue;
          w.i = j; stop = stops[j];
        }
        const here = Math.hypot(v.location.x - (stop.x + 0.5), v.location.z - (stop.z + 0.5));
        if (here <= 3.2) {                                                // (0.0.23: 2.5 < the walk's own arrival 2.6 — a watchman could
                                                                          // arrive, be re-sent, arrive... and never count the stop)
          if (stop.kind === "manhole") {
            const key = API.keyOf(st, p.id);
            if (!key) { count(st, "keyless"); w.i++; continue; }
            if (WALK.walking(v)) WALK.cancel(v);
            const street = (st.streets || []).find((x) => x.kind === "kit" && x.id === stop.sid);
            if (!street) { w.i++; continue; }
            cover(dim, stop.x, stop.y - 1, stop.z, true);
            w.mode = "below-down"; w.below = { sid: stop.sid, from: stop.from, to: stop.to, path: hallPath(street, stop.from, stop.to), k: 0, rung: stop.y, x: stop.x, z: stop.z, top: stop.y - 1, next: now + 20 };
            count(st, "climbs");
          } else { w.i += halfRounds(p) && p.job === "watch" ? 2 : 1; count(st, "rounds"); if (halfRounds(p)) count(st, "halfRounds"); }
          continue;
        }
        if (!WALK.walking(v)) {
          const ok = WALK.send(v, API.stOf(w.st), { x: stop.x + 0.5, y: stop.y, z: stop.z + 0.5 });
          // (review 10-04: an unreachable stop was retried forever under the walk's backoff) 30 refusals: the next stop
          w.refused = ok ? 0 : (w.refused || 0) + 1;
          if (w.refused >= 30) { w.refused = 0; w.i++; count(st, "skipped"); }
        }
        continue;
      }
      if (w.mode === "below-down") {                                      // down the ladder, one rung at a time
        if (now < w.below.next) continue;
        const b = w.below;
        const street = (st.streets || []).find((x) => x.kind === "kit" && x.id === b.sid);
        const bottom = (street ? API.kitHAt(street, b.from.t) : b.top) - 11;
        b.rung = Math.min(b.rung, Math.floor(v.location.y)) - 1;
        try { v.teleport({ x: b.x + 0.5, y: Math.max(bottom, b.rung), z: b.z + 0.5 }); } catch { /* left */ }
        b.next = now + CLIMB_TICKS;
        if (b.rung <= bottom) { cover(dim, b.x, b.top, b.z, false); w.mode = "below-walk"; count(st, "below"); }
        continue;
      }
      if (w.mode === "below-walk") {                                      // the hall: the lead along the side lane
        const b = w.below;
        b.since = b.since || now;
        if (now - b.since > 2400 && b.turned) {                           // the walk back failed too: the failsafe (counted) — up the first shaft
          if (WALK.walking(v)) WALK.cancel(v);
          count(st, "rescued");
          const street = (st.streets || []).find((x) => x.kind === "kit" && x.id === b.sid);
          const top = street ? API.kitHAt(street, b.to.t) : b.top;
          const [cx, cz] = street ? API.cellOf(street.f, b.to.t, b.to.side < 0 ? 1 : 11) : [b.x, b.z];
          cover(dim, cx, top, cz, true);
          w.mode = "below-up"; w.below = { ...b, x: cx, z: cz, top, rung: top - 11, next: now + 10 };
          continue;
        }
        if (now - b.since > 2400 && !b.turned) {                          // 2 minutes and not through: WALK back to the shaft it came down
          if (WALK.walking(v)) WALK.cancel(v);
          count(st, "turnedBack");
          const from = b.from;
          w.below = { ...b, from: b.to, to: from, path: b.path.slice().reverse(), since: now, turned: true };
          continue;
        }
        const end = b.path[b.path.length - 1];
        if (Math.hypot(v.location.x - (end[0] + 0.5), v.location.z - (end[1] + 0.5)) <= 3.0) {   // (review 10-04: the walk itself stops at 2.6)
          if (WALK.walking(v)) WALK.cancel(v);
          const street = (st.streets || []).find((x) => x.kind === "kit" && x.id === b.sid);
          const top = street ? API.kitHAt(street, b.to.t) : end[2] + 11;
          const [cx, cz] = street ? API.cellOf(street.f, b.to.t, b.to.side < 0 ? 1 : 11) : [end[0], end[1]];
          cover(dim, cx, top, cz, true);
          w.mode = "below-up"; w.below = { ...b, x: cx, z: cz, top, rung: Math.floor(v.location.y), next: now + 10 };
          continue;
        }
        if (!WALK.walking(v)) WALK.sendPath(v, API.stOf(w.st), b.path);
        continue;
      }
      if (w.mode === "below-up") {                                        // up the ladder at the next manhole
        if (now < w.below.next) continue;
        const b = w.below;
        b.rung += 1;
        try { v.teleport({ x: b.x + 0.5, y: Math.min(b.top + 1, b.rung), z: b.z + 0.5 }); } catch { /* left */ }
        b.next = now + CLIMB_TICKS;
        if (b.rung >= b.top + 1) {
          // out on the sidewalk beside the shaft, the cover shut behind
          // out onto the outer sidewalk cell beside the shaft (review 10-04: he was set down on the still-open cover)
          const street = (st.streets || []).find((x) => x.kind === "kit" && x.id === b.sid);
          const [ox, oz] = street ? API.cellOf(street.f, b.to.t, b.to.side < 0 ? 0 : 12) : [b.x, b.z];
          try { v.teleport({ x: ox + 0.5, y: b.top + 1, z: oz + 0.5 }); } catch { /* left */ }
          system.runTimeout(() => cover(dim, b.x, b.top, b.z, false), 40);
          w.mode = "walk"; w.i++; delete w.below; count(st, "rounds");
        }
        continue;
      }
    }
  }
} });

/** the watch of every settlement right now (status): posts held, on duty, below ground, the counters */
export function stats(st) {
  let onDuty = 0, below = 0;
  const sample = [];
  for (const [vid, w] of state) {
    if (w.st !== st.id) continue;
    onDuty++;
    if (w.mode && w.mode.startsWith("below")) below++;
    if (sample.length < 4) { let v; try { v = world.getEntity(vid); } catch { v = undefined; } sample.push([v ? v.nameTag : "?", w.mode, v ? [Math.floor(v.location.x), Math.floor(v.location.y), Math.floor(v.location.z)] : null, w.i]); }
  }
  return { onDuty, below, ...(st.watch || {}), sample };
}

// ------------------------------------------------------------------------------------------------ 1.3.228 B10: rally, bell, lights
// His 12:20 ruling: "civs band together to defeat MONSTERS if the watch or guard is overwhelmed" — never civ against civ.
// OVERWHELMED: the hostile monsters inside the town's influence (one query per town every RALLY_EVERY ticks) number at
// least max(RALLY_MIN, 2 x the watchmen on duty). Then every grown civ (not a child, not an elder) within RALLY_REACH of a
// monster rallies: he walks at it and strikes (a weaker blow than the watch's, the same cooldown law); the schedule leaves
// rallied bodies alone (tag civ:rally) until the town is calm. Children and elders go indoors (the alarm).
// THE BELL (WP2): a player ringing a bell inside a town, or the watch seeing >= ALARM_SEEN monsters in one sweep, sounds the
// alarm for ALARM_TICKS: everyone but the watch and the rally goes home. Memory only.
// THE NIGHT LIGHT (WP4): a light block (level 10) at the head of up to LIGHTS_MAX watchmen near a player, moved with them,
// cleared at dawn and at load (st.lights keeps the cells so a reload can clear them).
const RALLY_EVERY = 40, RALLY_MIN = 3, RALLY_REACH = 14, RALLY_DMG = 3, ALARM_TICKS = 1200, ALARM_SEEN = 3, LIGHTS_MAX = 6;
const alarms = new Map();             // st id -> until tick
const rallyNow = new Map();           // st id -> { until, monsters: [ids] }
const rallyStrike = new Map();        // vid -> last strike tick
export function alarmOn(stId) { const t = alarms.get(stId); return t !== undefined && t > system.currentTick; }
export function overwhelmed(stId) { const r = rallyNow.get(stId); return !!r && r.until > system.currentTick; }
export function soundAlarm(st, why) {
  if (alarmOn(st.id)) return;
  alarms.set(st.id, system.currentTick + ALARM_TICKS);
  count(st, "alarms");
  try { st.log.push(`day ${Math.floor(API.load().simDays)}: the bell! (${why}) — everyone indoors`); } catch { /* left */ }
  try { for (const pl of world.getPlayers()) if (pl.dimension.id === st.dim && API.inInfluence && API.inInfluence(st, pl.location.x, pl.location.z)) pl.onScreenDisplay.setActionBar(`§c${st.name}: the bell! Everyone indoors.`); } catch { /* left */ }
}
world.afterEvents.playerInteractWithBlock.subscribe((ev) => {
  try {
    if (!ev.block || ev.block.typeId !== "minecraft:bell" || !API) return;
    const s = API.load(), l = ev.block.location;
    const st = s.settlements.find((x) => x.dim === ev.block.dimension.id && API.inInfluence && API.inInfluence(x, l.x, l.z));
    if (st) soundAlarm(st, `${ev.player.name} rang it`);
  } catch { /* left */ }
});
HB.register("rally", { every: 20, slot: 15, budgetMs: 10, optional: false, fn: () => {
  if (!API) return;
  const now = system.currentTick;
  const s = API.load();
  let tod = 0; try { tod = world.getTimeOfDay(); } catch { /* left */ }
  for (const st of s.settlements) {
    if (!st.kit || !st.square || st.phase !== "built") continue;
    let dim; try { dim = world.getDimension(st.dim); } catch { continue; }
    if (now % RALLY_EVERY < 20) {
      const r = (st.border && st.border.r) || 64;
      const cx = st.square.x + 6, cz = st.square.z + 6;
      if (!dim.isChunkLoaded({ x: cx, y: st.square.y, z: cz })) continue;
      let mons = [];
      try { mons = dim.getEntities({ location: { x: cx, y: st.square.y, z: cz }, maxDistance: r * 1.42, families: ["monster"] }).filter((e) => e.isValid && HOSTILE.includes(e.typeId) && Math.abs(e.location.x - cx) <= r && Math.abs(e.location.z - cz) <= r); } catch { mons = []; }
      let onDuty = 0;
      for (const [, w] of state) if (w.st === st.id) onDuty++;
      if (mons.length >= ALARM_SEEN && !alarmOn(st.id)) soundAlarm(st, `${mons.length} monsters in the town`);
      if (mons.length >= Math.max(RALLY_MIN, 2 * onDuty)) {
        if (!overwhelmed(st.id)) { count(st, "rallies"); try { st.log.push(`day ${Math.floor(s.simDays)}: the watch is overwhelmed (${mons.length} monsters, ${onDuty} on duty) — the townsfolk band together`); } catch { /* left */ } }
        rallyNow.set(st.id, { until: now + RALLY_EVERY * 2, monsters: mons.map((e) => e.id) });
      }
    }
    const rr = rallyNow.get(st.id);
    if (!rr || rr.until <= now) {
      if (rr) { rallyNow.delete(st.id); for (const v of HB.bodiesOf(st)) { try { if (v.hasTag("civ:rally")) v.removeTag("civ:rally"); } catch { /* left */ } } }
      continue;
    }
    const mons = rr.monsters.map((id) => { try { return world.getEntity(id); } catch { return undefined; } }).filter((e) => e && e.isValid);
    if (!mons.length) continue;
    let sends = 0;
    for (const v of HB.bodiesOf(st)) {
      let p;
      try { if (v.hasTag("civ:watching") || v.hasTag("civ:keeper")) continue; p = API.personOf(v, st); } catch { continue; }
      if (!p || !API.grown || !API.grown(p)) continue;
      let near = null, nd = Infinity;
      for (const e of mons) { const d = Math.hypot(e.location.x - v.location.x, e.location.z - v.location.z); if (d < nd && Math.abs(e.location.y - v.location.y) <= 4) { nd = d; near = e; } }
      if (!near || nd > RALLY_REACH) continue;
      try { if (!v.hasTag("civ:rally")) { v.addTag("civ:rally"); count(st, "rallied"); } } catch { continue; }
      if (nd <= STRIKE && now - (rallyStrike.get(v.id) || 0) >= STRIKE_TICKS) {
        rallyStrike.set(v.id, now);
        try { near.applyDamage(RALLY_DMG, { cause: EntityDamageCause.entityAttack, damagingEntity: v }); count(st, "rallyStrikes"); } catch { /* left */ }
      } else if (sends < 3 && !WALK.walking(v)) { sends++; WALK.send(v, st, { x: near.location.x, y: near.location.y, z: near.location.z }); }
    }
    void tod;
  }
} });
// the night lights
const lightAt = new Map();            // vid -> "x,y,z"
function clearLight(dim, key) {
  const [x, y, z] = key.split(",").map(Number);
  try { const b = API.blockAt(dim, x, y, z); if (b && b.typeId === "minecraft:light_block") b.setType("minecraft:air"); } catch { /* left */ }
}
HB.register("lights", { every: 20, slot: 5, budgetMs: 4, optional: true, fn: () => {
  if (!API) return;
  const s = API.load();
  let tod = 0; try { tod = world.getTimeOfDay(); } catch { return; }
  const night = onNight(tod);
  let players = []; try { players = world.getPlayers(); } catch { /* left */ }
  for (const st of s.settlements) {
    let dim; try { dim = world.getDimension(st.dim); } catch { continue; }
    const want = new Map();
    if (night && players.length) {
      for (const [vid, w] of state) {
        if (w.st !== st.id || (w.mode && w.mode.startsWith("below")) || want.size >= LIGHTS_MAX) continue;
        let v; try { v = world.getEntity(vid); } catch { v = undefined; }
        if (!v || !v.isValid) continue;
        if (!players.some((pl) => pl.dimension.id === st.dim && Math.abs(pl.location.x - v.location.x) <= 32 && Math.abs(pl.location.z - v.location.z) <= 32)) continue;
        want.set(vid, `${Math.floor(v.location.x)},${Math.floor(v.location.y) + 1},${Math.floor(v.location.z)}`);
      }
    }
    const keep = new Set(want.values());
    for (const key of st.lights || []) if (!keep.has(key)) clearLight(dim, key);           // dawn, a reload, a moved light
    for (const [vid, key] of lightAt) if (!keep.has(key) && !(st.lights || []).includes(key)) { /* another town's */ void vid; }
    const placed = [];
    for (const [vid, key] of want) {
      const [x, y, z] = key.split(",").map(Number);
      try { const b = API.blockAt(dim, x, y, z); if (b && (b.typeId === "minecraft:air" || b.typeId === "minecraft:light_block")) { if (b.typeId === "minecraft:air") b.setPermutation(BlockPermutation.resolve("minecraft:light_block", { block_light_level: 10 })); placed.push(key); lightAt.set(vid, key); } } catch { /* left */ }
    }
    if (placed.length || (st.lights && st.lights.length)) { if (placed.length) st.lights = placed; else delete st.lights; }
  }
} });
