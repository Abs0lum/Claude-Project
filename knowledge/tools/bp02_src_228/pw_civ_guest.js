// pw_civ_guest.js — CIVITAS B11 THE PLAYER, the ENGINE half (program 228: WP5 festivals, WP6 the dusk speech, WP12 the guide,
// WP8 witnessed deeds — built and OFF). The rules are pw_civ_player.js (pure, node-tested); this module shows them.
//   * FESTIVALS (his 10:15: a wedding gathering, a feast at each tier-up, a MONTHLY holiday, on the square at dusk): the
//     clock's dusk goal sends bodies to their ring slot (festGoal); this beat logs the festival once a day (+ a rumour), and
//     every FEST.particleEvery ticks puts a few particles over the ring when a player is within 48 of the square.
//   * THE DUSK SPEECH (WP6): 11000..11600, once a day per town with a player within SPEECH.reach of the square: the leader
//     (the town hall's keeper, else the eldest master's body) says three lines, SPEECH.gap ticks apart.
//   * THE GUIDE (WP12): a civ you ask walks you to a place by the walk graph (WALK.send). Player more than GUIDE.hold behind
//     -> he stops and waits (never teleported: our walk law); within GUIDE.resume -> he walks on; within GUIDE.arrive of the
//     door -> a line, particles, and he goes back to his day. Given up after GUIDE.maxTicks.
//   * DEEDS (WP8): the subscription exists; PLAYER.DEEDS.enabled = false (his 10:15) makes it return at once.
// Heartbeat: "guest" (every 20 ticks, slot 11; optional). Nothing saved here (the festival is derived; the day markers are memory).
import { world, system } from "@minecraft/server";
import * as HB from "./pw_civ_beat.js";
import * as WALK from "./pw_civ_walk.js";
import * as VOICE from "./pw_civ_voice.js";
import * as PLAYER from "./pw_civ_player.js";

let API = null;
const festSaid = new Map();      // st id -> world day the festival was announced
const speechDone = new Map();    // st id -> world day of the last speech
const speechQ = [];              // { v, text, at }
const guides = new Map();        // vid -> { v, playerId, stId, target, label, since, holding }
export const GSTAT = { festivals: 0, particles: 0, speeches: 0, guides: 0, arrived: 0, gaveUp: 0, deeds: 0 };

export function initGuest(api) {
  API = api;
  HB.register("guest", { every: 20, slot: 11, budgetMs: 8, optional: true, fn: beat });
  try {
    world.afterEvents.playerBreakBlock.subscribe((ev) => { if (!PLAYER.DEEDS.enabled) return; try { deed(ev.player, ev.block, "wall"); } catch { /* left */ } });
  } catch (e) { console.warn(`[CIV-GUEST] deeds subscribe: ${e}`); }
}
export function isGuiding(vid) { return guides.has(vid); }

/** the festival of a town today (or null) */
export function festivalNow(s, st) {
  try {
    return PLAYER.festivalOf(API.worldDay(), Math.floor(s.simDays), { weddingDay: st.wedDay, tierDay: st.tierDay !== undefined ? Math.floor(st.tierDay) : null, seed: st.seed || 1 });
  } catch { return null; }
}
/** the dusk goal of a body on a festival evening: its ring slot around the square's centre (null: no festival / no square) */
export function festGoal(s, st, person, fest) {
  if (!fest || !st.square || !person) return null;
  const c = squareCentre(st);
  const r = PLAYER.ringSlot(c.x, c.z, person.id);
  return { x: Math.floor(r.x) + 0.5, z: Math.floor(r.z) + 0.5, y: st.square.y + 1, look: r.look, mode: "idle", fest: fest.kind };
}
const squareCentre = (st) => ({ x: st.square.x + 6, z: st.square.z + 6 });

/** WP12: start a guide (v walks to place.target; the player follows) */
export function guideTo(v, player, st, place) {
  if (!v || !v.isValid || !place || !place.target) return false;
  const ok = WALK.send(v, st, place.target);
  if (!ok) return false;
  guides.set(v.id, { v, playerId: player.id, stId: st.id, target: place.target, label: place.label, since: system.currentTick, holding: false });
  GSTAT.guides++;
  console.warn(`[CIV-GUIDE] start ${JSON.stringify({ st: st.id, to: place.label, x: place.target.x, z: place.target.z })}`);
  return true;
}

function beat() {
  const tick = system.currentTick;
  stepGuides(tick);
  stepSpeech(tick);
  let players; try { players = world.getPlayers(); } catch { return; }
  if (!players.length) return;
  const tod = world.getTimeOfDay();
  const s = API.load();
  for (const st of s.settlements) {
    if (!st.square) continue;
    const near = players.filter((p) => { try { return p.dimension.id === st.dim && API.inInfluence(st, p.location.x, p.location.z); } catch { return false; } });
    if (!near.length) continue;
    const wday = API.worldDay();
    // festivals: announced once a day at dusk; particles over the ring
    if (tod >= PLAYER.FEST.dusk[0] && tod < PLAYER.FEST.dusk[1]) {
      const f = festivalNow(s, st);
      if (f) {
        if (festSaid.get(st.id) !== wday) {
          festSaid.set(st.id, wday);
          GSTAT.festivals++;
          const text = `the town keeps ${PLAYER.FEST_NAME[f.kind]} on the square`;
          try { st.log.push(`day ${Math.floor(s.simDays)}: ${text}`); if (st.people) API.PEOPLE.rumour(st.people, Math.floor(s.simDays), "news", `${st.name} kept ${PLAYER.FEST_NAME[f.kind]}`); } catch { /* left */ }
          for (const p of near) { try { p.onScreenDisplay.setActionBar(`§d${st.name} keeps ${PLAYER.FEST_NAME[f.kind]} tonight — on the square`); } catch { /* left */ } }
          console.warn(`[CIV-FEST] ${JSON.stringify({ st: st.id, wday, kind: f.kind, why: f.why })}`);
        }
        if (tick % PLAYER.FEST.particleEvery < 20) {
          const c = squareCentre(st);
          if (near.some((p) => Math.hypot(p.location.x - c.x, p.location.z - c.z) <= 48)) {
            const dim = world.getDimension(st.dim);
            for (let k = 0; k < 4; k++) {
              const a = (tick / 40 + k) * 1.57;
              try { dim.spawnParticle(k % 2 ? "minecraft:villager_happy" : "minecraft:note_particle", { x: c.x + Math.cos(a) * 5, y: st.square.y + 3, z: c.z + Math.sin(a) * 5 }); GSTAT.particles++; } catch { /* unloaded */ }
            }
          }
        }
      }
    }
    // the dusk speech
    if (tod >= PLAYER.SPEECH.at[0] && tod < PLAYER.SPEECH.at[1] && speechDone.get(st.id) !== wday) {
      const c = squareCentre(st);
      if (near.some((p) => Math.hypot(p.location.x - c.x, p.location.z - c.z) <= PLAYER.SPEECH.reach)) {
        speechDone.set(st.id, wday);
        speak(s, st, tick);
      }
    }
  }
}

/** WP6: the leader (the town hall's keeper, else the eldest master's body) says three lines from yesterday */
function speak(s, st, tick) {
  const bodies = HB.bodiesOf(st);
  const hall = s.buildings.find((b) => b.settlement === st.id && API.short(b) === "town_hall" && b.stage >= 4);
  let leader = hall ? bodies.find((v) => { try { return v.hasTag(`civ:shop:${hall.id}`); } catch { return false; } }) : null;
  if (!leader && st.people) {
    const masters = API.PEOPLE.alive(st.people).filter((p) => p.trade && API.PEOPLE.rankOf && API.PEOPLE.rankOf(p, p.trade) === "master").sort((a, b) => a.born - b.born);
    for (const m of masters) { leader = bodies.find((v) => { try { return v.hasTag(`civ:person:${m.id}`); } catch { return false; } }); if (leader) break; }
  }
  if (!leader) return;
  const L = st.ledger;
  const short = L ? API.ECON.GOODS.filter((g) => (L.stock[g] || 0) < 4 && (L.prices[g] || 0) > (API.ECON.BASE[g] || 0) * 1.2) : [];
  const built = API.recentBuilt ? API.recentBuilt(st) : [];
  const lines = PLAYER.speechLines({ town: st.name, short, built, tier: st.title || null, festival: (festivalNow(s, st) || {}).kind, mood: st.mood });
  lines.forEach((text, i) => speechQ.push({ v: leader, text, at: tick + i * PLAYER.SPEECH.gap }));
  // the bodies near the square turn to the leader
  try {
    const q = leader.location;
    for (const v of bodies) { const l = v.location; if (v.id !== leader.id && Math.hypot(l.x - q.x, l.z - q.z) <= 12) v.setRotation({ x: 0, y: Math.atan2(-(q.x - l.x), q.z - l.z) * 180 / Math.PI }); }
  } catch { /* left */ }
  GSTAT.speeches++;
  console.warn(`[CIV-SPEECH] ${JSON.stringify({ st: st.id, lines })}`);
}
function stepSpeech(tick) {
  for (let i = speechQ.length - 1; i >= 0; i--) {
    const q = speechQ[i];
    if (q.at > tick) continue;
    speechQ.splice(i, 1);
    try { if (q.v.isValid) { VOICE.say(q.v, q.text, PLAYER.SPEECH.gap - 10); world.getPlayers().forEach((p) => { try { if (Math.hypot(p.location.x - q.v.location.x, p.location.z - q.v.location.z) <= PLAYER.SPEECH.reach) p.sendMessage(`§7${String(q.v.nameTag || "").split("\n")[0]}: §f${q.text}`); } catch { /* left */ } }); } } catch { /* left */ }
  }
}

function stepGuides(tick) {
  for (const [vid, g] of guides) {
    const end = (why) => { guides.delete(vid); try { WALK.cancel(g.v); } catch { /* left */ } if (why) console.warn(`[CIV-GUIDE] ${why} ${JSON.stringify({ st: g.stId, to: g.label, ticks: tick - g.since })}`); };
    if (!g.v.isValid) { end("lost"); continue; }
    if (tick - g.since > PLAYER.GUIDE.maxTicks) { GSTAT.gaveUp++; end("gave up"); continue; }
    const pl = world.getPlayers().find((p) => p.id === g.playerId);
    if (!pl) { end("player left"); continue; }
    const v = g.v.location, p = pl.location;
    const d = Math.hypot(p.x - v.x, p.z - v.z), a = Math.hypot(g.target.x - v.x, g.target.z - v.z);
    const st = API.load().settlements.find((x) => x.id === g.stId);
    const step = PLAYER.guideStep(d, a, g.holding);
    if (step === "arrive") {
      GSTAT.arrived++;
      try { VOICE.say(g.v, `Here we are — ${g.label.toLowerCase()}.`); g.v.dimension.spawnParticle("minecraft:villager_happy", { x: g.target.x, y: g.target.y + 1, z: g.target.z }); } catch { /* left */ }
      end("arrived");
      continue;
    }
    if (step === "hold" && !g.holding) {
      g.holding = true;
      try { WALK.cancel(g.v); g.v.setRotation({ x: 0, y: Math.atan2(-(p.x - v.x), p.z - v.z) * 180 / Math.PI }); } catch { /* left */ }
    } else if (step === "walk" && (g.holding || !WALK.walking(g.v))) {
      g.holding = false;
      if (st) { try { WALK.send(g.v, st, g.target); } catch { /* left */ } }
    }
  }
}

/** WP8 (OFF): a deed seen by the bodies within reach of the broken block */
function deed(player, block, kind) {
  const s = API.load();
  const loc = block.location;
  const st = s.settlements.find((x) => x.dim === player.dimension.id && API.inInfluence(x, loc.x, loc.z));
  if (!st || !st.people) return;
  const bodies = [];
  for (const v of HB.bodiesOf(st)) {
    try { const tag = v.getTags().find((t) => t.startsWith("civ:person:")); if (tag) bodies.push({ pid: Number(tag.slice(11)), x: v.location.x, y: v.location.y, z: v.location.z }); } catch { /* left */ }
  }
  const seen = PLAYER.witnessesOf(bodies, loc);
  if (!seen.length) return;
  const day = Math.floor(s.simDays);
  for (const pid of seen) { const p = API.PEOPLE.byId(st.people, pid); if (p) PLAYER.witness(p, kind, day); }
  try { API.PEOPLE.rumour(st.people, day, "deed", `a traveller broke ${kind === "wall" ? "a wall" : `a ${kind}`} in ${st.name}`, seen); } catch { /* left */ }
  GSTAT.deeds++;
}
