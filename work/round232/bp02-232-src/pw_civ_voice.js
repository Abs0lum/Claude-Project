// pw_civ_voice.js — CIVITAS B5 VOICE, the ENGINE half (program 228: BF12 speech bubbles + overheard talk, PE11 talk stops,
// BF11 petitioners). The choices are pw_civ_talk.js (pure, node-tested); this module only shows them on the bodies.
//   * BUBBLE: the speaker's nameTag becomes "<name>\n<the line, wrapped>" for speechTicks(line), then the plain name again.
//     Nothing is saved: the restore map is memory, and any body found later with a two-line nameTag and no live bubble
//     (a world closed mid-line) is put back to its first line.
//   * HOLD (PE11): talking to a civ stops him, turns him to the player for HOLD_TICKS; the schedule pass leaves held bodies.
//   * OVERHEARD: at dusk (11000..13000), every OVERHEARD.every ticks, per town with a player in its influence: the most fond
//     friend pair (<= 5 apart) within OVERHEARD.radius of that player plays a 2-4 line script (deterministic, 18,000-tick
//     cooldown per pair).
//   * PETITIONS: every PETITION.every ticks, per player in a town: the most urgent civ (talk.pickPetitioner) within
//     PETITION.radius walks to the player, says his plea (bubble + chat) and waits; talking to him then offers "I'll see to
//     it" (a petition thread; the census checks the need on its deadline). p.pet (a day) is the only saved field.
// Heartbeat: one slot ("voice", every 20 ticks at slot 9; optional — shed under load). Cost: one getPlayers() per pass at
// most, distance checks over the shared bodies cache, <= 2 nameTag writes per 20 ticks per town.
import { world, system } from "@minecraft/server";
import * as HB from "./pw_civ_beat.js";
import * as WALK from "./pw_civ_walk.js";
import * as TALK from "./pw_civ_talk.js";

let API = null;
export const HOLD_TICKS = 200;
const DUSK = [11000, 13000];
const bubbles = new Map();          // vid -> { v, until, name, text }
const held = new Map();             // vid -> until tick
const pairLast = new Map();         // "a-b" -> tick (overheard cooldown)
const playerLast = new Map();       // player id -> tick (petition cooldown per player)
const petitions = new Map();        // vid -> { playerId, stId, pid, need, plea, phase: "walk" | "wait", since }
const queue = [];                   // overheard lines: { v, text, at }
export const VSTAT = { bubbles: 0, restored: 0, overheard: 0, petitions: 0, promised: 0, holds: 0, cleaned: 0 };

export function initVoice(api) {
  API = api;
  HB.register("voice", { every: 20, slot: 9, budgetMs: 10, optional: true, fn: beat });
}

/** a two-line nameTag (a bubble) — the name is its first line */
const plain = (tag) => String(tag || "").split("\n")[0].replace(/§./g, "");
export function bubbling(vid) { const b = bubbles.get(vid); return !!b && b.until > system.currentTick; }
export function isHeld(vid) { const h = held.get(vid); return (h !== undefined && h > system.currentTick) || petitions.has(vid); }

/** show a line over a civ's head */
export function say(v, text, ticks = TALK.speechTicks(text)) {
  if (!v || !v.isValid || !text) return false;
  const cur = bubbles.get(v.id);
  let name;
  try { name = cur ? cur.name : plain(v.nameTag); } catch { return false; }
  const shown = `§7${name}§r\n${TALK.wrap(text).join("\n")}`;
  try { v.nameTag = shown; } catch { return false; }
  bubbles.set(v.id, { v, until: system.currentTick + ticks, name, text: shown });
  VSTAT.bubbles++;
  return true;
}
function restore(vid, b) {
  bubbles.delete(vid);
  try { if (b.v.isValid && b.v.nameTag === b.text) { b.v.nameTag = b.name; VSTAT.restored++; } } catch { /* left */ }
}

/** PE11: the civ the player talks to stops, faces the player, and stands for HOLD_TICKS */
export function hold(v, player) {
  try {
    if (WALK.walking(v)) WALK.cancel(v);
    if (API && API.civState) API.civState(v, "stand");
    const p = player.location, q = v.location;
    v.setRotation({ x: 0, y: Math.atan2(-(p.x - q.x), p.z - q.z) * 180 / Math.PI });
  } catch { /* left */ }
  held.set(v.id, system.currentTick + HOLD_TICKS);
  VSTAT.holds++;
}

/** the facts of a body's person for a line (null: no census person) */
export function factsFor(s, st, v, player) {
  const tags = v.getTags();
  const pt = tags.find((t) => t.startsWith("civ:person:"));
  const P = st.people;
  const person = P && pt ? API.PEOPLE.byId(P, Number(pt.slice(11))) : null;
  if (!person) return null;
  const day = Math.floor(s.simDays);
  const g = API.PEOPLE.greeting(P, person, day);
  const job = typeof person.job === "number" ? s.buildings.find((b) => b.id === person.job) : null;
  const trade = typeof person.job === "string" ? person.job : (job ? API.short(job).replace(/_/g, " ") : null);
  const why = API.whyCode ? API.whyCode(st, person.id) : null;
  const pet = petitions.get(v.id);
  const f = TALK.factsOf(person, { day, town: st.name, trade, why, hd: (P.need && P.need.hd) || 0, arrears: (st.ledger && st.ledger.arrears) || 0,
    rumour: g.rumour, wet: API.wetNow ? API.wetNow(st) : false, tier: g.tier, temper: API.PEOPLE.temperName(person),
    child: API.PEOPLE.stage(person, day) === "child", recentBuilt: API.recentBuilt ? API.recentBuilt(s, st, day) : null,
    petition: pet && player && pet.playerId === player.id ? pet.plea : null });
  f.siteWaitsMine = !!(why && why.startsWith("SITE_WAITS:") && (person.job === "builders" || person.job === "builder"));
  return { person, f, day };
}

/** the talk form's opening line (PE10): picked, remembered, shown as a bubble too. Returns { text, petition } */
export function talkLine(s, st, v, player) {
  const r = factsFor(s, st, v, player);
  if (!r) return null;
  const line = TALK.pickLine(r.person, r.f, r.day);
  if (!line) return null;
  TALK.noteSaid(r.person, line.id, r.day);
  say(v, line.text);
  const pet = petitions.get(v.id);
  return { text: line.text, petition: pet && pet.playerId === player.id ? pet : null, person: r.person };
}

/** "I'll see to it": the promise becomes a thread the census settles on its deadline */
export function promise(s, st, v, player) {
  const pet = petitions.get(v.id);
  if (!pet || pet.playerId !== player.id || !st.people) return false;
  const day = Math.floor(s.simDays);
  const q = API.PEOPLE.byId(st.people, pet.pid);
  API.PEOPLE.openThread(st.people, day, "petition", `${q ? q.name : "a civ"} asked: ${pet.plea}`, [pet.pid], day + TALK.PETITION.deadlineDays, { pid: pet.pid, need: pet.need });
  petitions.delete(v.id);
  held.set(v.id, system.currentTick + 40);
  say(v, "Thank you. I'll hold you to it.");
  VSTAT.promised++;
  API.save();
  return true;
}

function beat() {
  const now = system.currentTick;
  for (const [vid, b] of bubbles) if (b.until <= now) restore(vid, b);
  for (const [vid, t] of held) if (t <= now) held.delete(vid);
  for (let i = queue.length - 1; i >= 0; i--) { const q = queue[i]; if (q.at <= now) { say(q.v, q.text); queue.splice(i, 1); } }
  const s = API.load();
  if (!s || !s.settlements) return;
  if (now % 1200 < 20) cleanup(s);                                        // a world closed mid-line: back to the plain name
  const doOver = now % TALK.OVERHEARD.every < 20, doPet = now % TALK.PETITION.every < 20;
  if (!doOver && !doPet && !petitions.size) return;
  let players = [];
  try { players = world.getPlayers(); } catch { return; }
  petitionSteps(s, players, now);
  if (!players.length) return;
  let tod = 0; try { tod = world.getTimeOfDay(); } catch { /* left */ }
  for (const pl of players) {
    const loc = pl.location;
    const st = s.settlements.find((x) => x.dim === pl.dimension.id && x.people && API.inInfluence(x, loc.x, loc.z));
    if (!st) continue;
    if (doOver && tod >= DUSK[0] && tod < DUSK[1]) overheard(s, st, pl, now);
    if (doPet && now - (playerLast.get(pl.id) ?? -1e9) >= TALK.PETITION.playerCooldown) petitionFor(s, st, pl, now);
  }
  if (now % 6000 < 20 && (VSTAT.bubbles || VSTAT.petitions)) console.warn(`[CIV-VOICE] ${JSON.stringify(VSTAT)}`);
}

function near(st, loc, r) {
  return HB.bodiesOf(st).filter((v) => { try { return Math.abs(v.location.x - loc.x) <= r && Math.abs(v.location.z - loc.z) <= r && Math.abs(v.location.y - loc.y) <= 8; } catch { return false; } });
}
function pidOf(v) { const t = v.getTags().find((x) => x.startsWith("civ:person:")); return t ? Number(t.slice(11)) : null; }

function overheard(s, st, pl, now) {
  const P = st.people;
  const bodies = [];
  for (const v of near(st, pl.location, TALK.OVERHEARD.radius)) {
    if (bubbling(v.id) || isHeld(v.id)) continue;
    const pid = pidOf(v);
    if (pid === null) continue;
    bodies.push({ v, vid: v.id, pid, x: v.location.x, z: v.location.z });
  }
  if (bodies.length < 2) return;
  const fond = (a, b) => { const p = API.PEOPLE.byId(P, a); return (p && p.friends && p.friends[b]) || 0; };
  const pair = TALK.pickPair(bodies, fond, pairLast, now);
  if (!pair) return;
  pairLast.set(pair.key, now);
  if (pairLast.size > 400) for (const [k, t] of pairLast) if (now - t > TALK.OVERHEARD.pairCooldown) pairLast.delete(k);
  const r = factsFor(s, st, pair.a.v, null);
  if (!r) return;
  const sc = TALK.scriptFor(r.f);
  for (const l of sc.lines) queue.push({ v: (l.who === 0 ? pair.a : pair.b).v, text: l.text, at: now + l.delay });
  for (const b of [pair.a, pair.b]) { try { b.v.setRotation({ x: 0, y: Math.atan2(-((b === pair.a ? pair.b : pair.a).x - b.x), (b === pair.a ? pair.b : pair.a).z - b.z) * 180 / Math.PI }); } catch { /* left */ } held.set(b.vid, now + sc.lines[sc.lines.length - 1].delay + 80); }
  VSTAT.overheard++;
}

function petitionFor(s, st, pl, now) {
  for (const pet of petitions.values()) if (pet.playerId === pl.id) return;      // one at a time per player
  const cands = [];
  for (const v of near(st, pl.location, TALK.PETITION.radius)) {
    try { if (v.hasTag("civ:keeper") || v.hasTag("civ:watching") || isHeld(v.id)) continue; } catch { continue; }
    const r = factsFor(s, st, v, null);
    if (!r) continue;
    cands.push({ p: r.person, f: r.f, d: Math.hypot(v.location.x - pl.location.x, v.location.z - pl.location.z), v });
  }
  const pk = TALK.pickPetitioner(cands, Math.floor(s.simDays));
  if (!pk) return;
  playerLast.set(pl.id, now);
  pk.p.pet = Math.floor(s.simDays);                                            // the only saved field (cooldown day)
  petitions.set(pk.v.id, { playerId: pl.id, stId: st.id, pid: pk.p.id, need: pk.need, plea: pk.plea, phase: "walk", since: now, v: pk.v });
  VSTAT.petitions++;
  API.save();
}

function petitionSteps(s, players, now) {
  for (const [vid, pet] of petitions) {
    const v = pet.v, pl = players.find((x) => x.id === pet.playerId);
    if (!v || !v.isValid || !pl || now - pet.since > (pet.phase === "walk" ? TALK.PETITION.walkTimeout : 1200)) { petitions.delete(vid); continue; }
    const d = Math.hypot(v.location.x - pl.location.x, v.location.z - pl.location.z);
    if (pet.phase === "walk") {
      if (d <= TALK.PETITION.reach) {
        pet.phase = "wait"; pet.since = now;
        if (WALK.walking(v)) WALK.cancel(v);
        hold(v, pl);
        say(v, pet.plea);
        try { pl.sendMessage(`§e${plain(v.nameTag)}§r: "${pet.plea}" §7(talk to them to answer)`); } catch { /* left */ }
      } else if (now % 40 < 20) {
        const st = s.settlements.find((x) => x.id === pet.stId);
        const back = d > 0 ? 2 / d : 0;
        if (st) WALK.send(v, st, { x: pl.location.x + (v.location.x - pl.location.x) * back, y: pl.location.y, z: pl.location.z + (v.location.z - pl.location.z) * back });
      }
    } else if (d <= 8) held.set(vid, now + 40);                                // waits for the answer while the player is near
  }
}

function cleanup(s) {
  for (const st of s.settlements) {
    for (const v of HB.bodiesOf(st)) {
      try { if (!bubbles.has(v.id) && String(v.nameTag || "").includes("\n")) { v.nameTag = plain(v.nameTag); VSTAT.cleaned++; } } catch { /* left */ }
    }
  }
}
