// pw_civ_people.js — CIVITAS people v1 (D-C536, his 21:55: "the villager relationship and happiness models that will later
// allow gossip … the entire interconnectedness models"). PURE functions over plain data (no engine imports): the same code
// runs live, in catch-up and in the node tests. A settlement's PEOPLE are records; the villager entities near a player
// are their bodies (the clock spawns a few, named from these records).
//
// THE MODEL (canon: SOCIAL-DYNAMICS / COMPETITIVE-SOCIETY / LIFECYCLE): a person has a home, a job, a spouse, parents and
// children, FRIENDS with a fondness that rises by co-presence (household, workmates, the square) and fades otherwise, a MOOD
// (happiness) from being fed, housed, employed and paid, from friends and family and from grief, and the RUMOURS they have
// heard. Every day: ages advance (child -> apprentice -> adult -> elder -> death, all dials); adults who like each other
// marry; married couples have children where there is room; elders die and leave what they held to kin, then the closest
// friend, then the town; the unhappy leave; a happy, fed town with free housing draws newcomers (the Immigrant Faucet);
// rumours pass friend to friend (knowledge at foot speed) and expire; THREADS are live situations with a default course.
export const DIALS = { child: 10, apprentice: 20, elder: 120, death: 130, deathSpan: 30, fertile: 100, marryFond: 60, friend: 40, close: 70,
                       birthChance: 0.03, crowd: 2, moveOutAge: 25, leaveMood: 25, leaveDays: 10, faucetMood: 60, faucetEvery: 5, rumourDays: 30, tellChance: 0.5,
                       contactGain: 2, contactFade: 1, maxContacts: 6, maxFriends: 12 };
export const NAMES_M = ["Bram", "Dag", "Finn", "Hal", "Jory", "Lars", "Nils", "Pim", "Sven", "Ulf", "Wim", "Zane", "Arn", "Cole", "Eyvind", "Garr", "Ivo", "Kell", "Marek", "Osric"];
export const NAMES_F = ["Ada", "Cora", "Edda", "Greta", "Ida", "Kari", "Maud", "Orla", "Rhea", "Tess", "Vera", "Ylva", "Brit", "Dove", "Elin", "Freja", "Hilde", "Juno", "Liv", "Nessa"];

export function newPeople() { return { next: 1, list: [], rumours: [], threads: [], nextThread: 1, player: {}, faucet: 0 }; }

// ---------------------------------------------------------------------------------------------------------------------------
// D-C550 (his 00:43 / 00:52): PEOPLE WHO LEARN — "experience + time + a learning factor". Every person keeps TRUST in what they
// deal with (other people "p:<id>", shops "s:<id>", the town "town:<topic>", places, the player "player") as a value 0..1 with
// a count of experiences. After an outcome o (0..1): v <- v + a (o - v), a = 1 / (n + 2) — quick to learn at first, settled
// later. Untouched trust drifts back toward 0.5 (forgetting, LEARN.drift a day). SURPRISE |o - v| is the self-questioning
// signal: it raises the person's EXPLORE share (trying an untried source next time) and becomes a rumour when large.
// Opinions ARE these numbers; they steer choices (choose), the buyer's score, migration, the council.
// ranks scaled to a working life of ~110 days (adult 20 .. death ~130-160): journeyman at 15 days, master at 60 (R5: a 7-year
// apprenticeship in a ~40-year career = 17 %)
export const LEARN = { drift: 0.01, surprise: 0.4, exploreBase: 0.1, exploreMax: 0.5, exploreDecay: 0.02, journeyman: 15, master: 60, skillCap: 0.5, skillDays: 120 };
/** one experience: returns the surprise (0..1) */
export function learn(person, key, outcome, day) {
  const t = (person.trust = person.trust || {});
  const e = t[key] || (t[key] = { v: 0.5, n: 0, day });
  const o = Math.max(0, Math.min(1, outcome));
  const surprise = Math.abs(o - e.v);
  e.v += (o - e.v) / (e.n + 2);
  e.n++; e.day = day;
  if (surprise >= LEARN.surprise) person.explore = Math.min(LEARN.exploreMax, (person.explore ?? LEARN.exploreBase) + 0.1);
  return surprise;
}
export function trustOf(person, key) { return person.trust && person.trust[key] ? person.trust[key].v : 0.5; }
/** time: what was not experienced today drifts back toward neutral; the urge to explore settles */
export function forget(person, day) {
  for (const e of Object.values(person.trust || {})) if (e.day < day) e.v += (0.5 - e.v) * LEARN.drift;
  if (person.explore !== undefined) person.explore = Math.max(LEARN.exploreBase, person.explore - LEARN.exploreDecay);
}
/** 1.3.227 (the saved town at city II: 3.6 million characters, 3.1 million of them TRUST entries — 452 people, the dead
 *  included, ~120 entries each with 17-digit values): the dead and departed keep no opinions (a day after, when the
 *  inheritance has read them); a trust entry back within TRUST_NEUTRAL of 0.5 and untouched for TRUST_IDLE days is
 *  forgotten (trustOf answers 0.5 for it — as it would after the drift); an opinion of someone no longer a friend is
 *  forgotten with the friendship; values keep 4 decimals. */
const TRUST_NEUTRAL = 0.03, TRUST_IDLE = 20;
export function diet(P, day) {
  for (const p of P.list) {
    if (!p.alive) {
      if (day - (p.died ?? p.left ?? day) >= 1) { if (p.trust) delete p.trust; if (p.knows && p.knows.length) p.knows = []; }
      continue;
    }
    const t = p.trust;
    if (!t) continue;
    for (const k of Object.keys(t)) {
      const e = t[k];
      // an opinion of a person who is no longer a friend goes with the friendship (p: entries are read by nothing else —
      // gate 226-2's world: 139 of them per living civ, ~10 of them friends)
      if (k.startsWith("p:") && !(p.friends && p.friends[k.slice(2)] !== undefined)) { delete t[k]; continue; }
      if (Math.abs(e.v - 0.5) < TRUST_NEUTRAL && day - e.day > TRUST_IDLE) { delete t[k]; continue; }
      e.v = Math.round(e.v * 10000) / 10000;
    }
  }
}
/** a choice among options [{ key, value }] (value 0..1: what the option promises): the best value x trust, except an
 *  explore share spent on the least-known option (the "need to do more and seek it out"). r = a 0..1 random source */
export function choose(person, options, r) {
  if (!options.length) return null;
  const e = person.explore ?? LEARN.exploreBase;
  if (options.length > 1 && r() < e) {
    const t = person.trust || {};
    return options.slice().sort((a, b) => ((t[a.key] && t[a.key].n) || 0) - ((t[b.key] && t[b.key].n) || 0))[0];
  }
  let best = null, bs = -Infinity;
  for (const o of options) { const sc = o.value * (0.5 + trustOf(person, o.key)); if (sc > bs) { bs = sc; best = o; } }
  return best;
}
/** the canon's buyer score, now with trust: price (lower better, 0..1 after scaling), distance, standing, fondness, trust */
export function buyerScore(person, key, { price = 1, dist = 0, standing = 0.5, fond = 0 } = {}) {
  return (1 / Math.max(0.1, price)) * (1 / (1 + dist / 100)) * (0.5 + standing) * (1 + fond / 100) * (0.5 + trustOf(person, key));
}
/** GROWTH of a person: days worked in a trade -> apprentice / journeyman / master; the output factor 1 .. 1 + skillCap */
export function skillOf(person, trade) { return (person.skill && person.skill[trade]) || 0; }
export function rankOf(person, trade) { const d = skillOf(person, trade); return d >= LEARN.master ? "master" : d >= LEARN.journeyman ? "journeyman" : "apprentice"; }
export function outputFactor(person, trade) { return 1 + Math.min(LEARN.skillCap, skillOf(person, trade) / LEARN.skillDays); }

/** a deterministic random from a seed (mulberry32) */
export function rng(seed) { let a = seed >>> 0; return () => { a += 0x6D2B79F5; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

export function newPerson(P, day, opts = {}) {
  const r = rng((P.next * 7919 + (opts.seed || 0)) >>> 0);
  const sex = opts.sex || (r() < 0.5 ? "m" : "f");
  const names = sex === "m" ? NAMES_M : NAMES_F;
  const p = { id: P.next++, name: opts.name || names[Math.floor(r() * names.length)], sex, born: day - (opts.age !== undefined ? opts.age : DIALS.apprentice + Math.floor(r() * 60)),
              home: opts.home ?? null, job: opts.job ?? null, trade: opts.trade ?? null, spouse: null, parents: opts.parents || [], kids: [], friends: {}, mood: 55, alive: true,
              knows: [], grief: 0, lowDays: 0, playerFond: 0 };
  P.list.push(p);
  return p;
}
export const age = (p, day) => day - p.born;
export const stage = (p, day) => { const a = age(p, day); return a < DIALS.child ? "child" : a < DIALS.apprentice ? "apprentice" : a < DIALS.elder ? "adult" : "elder"; };
export const alive = (P) => P.list.filter((p) => p.alive);
// 1.3.227 (profiled at city II: byId scanned the whole list for every villager on every beat): an index per list array —
// the list only grows by push and is replaced whole when the long dead are forgotten, so its length tells when to rebuild
const IDX = new WeakMap();
export const byId = (P, id) => {
  const L = P.list;
  let e = IDX.get(L);
  if (!e || e.n !== L.length) { e = { n: L.length, m: new Map(L.map((p) => [p.id, p])) }; IDX.set(L, e); }
  return e.m.get(id);
};

/** a rumour everyone in `who` knows from today; spreads by contacts */
export function rumour(P, day, kind, text, who = [], about = []) {
  const r = { id: P.rumours.length ? P.rumours[P.rumours.length - 1].id + 1 : 1, day, kind, text, about, heard: who.length };
  P.rumours.push(r);
  for (const id of who) { const p = byId(P, id); if (p && !p.knows.includes(r.id)) p.knows.push(r.id); }
  return r;
}
/** a thread: a live situation with a default course on its deadline */
export function openThread(P, day, kind, text, people, deadline, data = {}) {
  const t = { id: P.nextThread++, kind, text, people, day, deadline, state: "open", data, lines: [] };
  P.threads.push(t);
  return t;
}
export function closeThread(P, t, how, text) { t.state = how; t.closed = text; }

function bump(p, q, n) {
  p.friends[q.id] = Math.min(100, (p.friends[q.id] || 0) + n);
  q.friends[p.id] = Math.min(100, (q.friends[p.id] || 0) + n);
}
function inherit(P, dead, ctx, ev) {
  // succession = three lookups: kin (spouse, then the eldest child), then the closest friend, then the town
  const heirs = [];
  if (dead.spouse) { const sp = byId(P, dead.spouse); if (sp && sp.alive) heirs.push(sp); }
  for (const kid of dead.kids.map((id) => byId(P, id)).filter((k) => k && k.alive).sort((a, b) => a.born - b.born)) heirs.push(kid);
  const friend = Object.entries(dead.friends).sort((a, b) => b[1] - a[1]).map(([id]) => byId(P, Number(id))).find((f) => f && f.alive && f.friends[dead.id] >= DIALS.friend);
  if (friend) heirs.push(friend);
  const heir = heirs[0] || null;
  const held = { home: dead.home, job: dead.job };
  let passed = false;
  if (heir) {
    if (held.job && !heir.job && typeof held.job === "number") { heir.job = held.job; heir.trade = dead.trade; passed = true; }   // a shop passes to kin; an OFFICE (a string post: builders, sewer keeper) never does (D-C539)
    ev.push({ kind: "inherit", text: `${dead.name}'s ${held.job ? "shop" : "house"} passes to ${heir.name}${heir === friend ? " (a friend; no kin)" : ""}`, people: [dead.id, heir.id], held, heir: heir.id });
  } else ev.push({ kind: "escheat", text: `${dead.name} left no kin: the town takes the ${held.job ? "shop" : "house"}`, people: [dead.id], held, heir: null });
  return passed;
}

/** one day. ctx = { day, fed (0..1 share who ate), paid (wages met), homes: [{id, room (free places), street}], jobs: [{id, kind, stations}],
 *  seed }. Returns { events: [{kind, text, people, ...}], arrivals, departures } — the clock writes the chronicle, moves bodies. */
export function dayStep(P, ctx) {
  const day = ctx.day, r = rng(((ctx.seed || 1) * 131 + day) >>> 0);
  // (review 10-04: the list only grew; byId is a scan) the long dead and long departed are forgotten after 200 days
  if (day % 10 === 0 && P.list.length > 120) P.list = P.list.filter((q) => q.alive || day - (q.died ?? q.left ?? day) < 200);
  diet(P, day);
  const ev = [];
  const people = alive(P);
  const homes = new Map((ctx.homes || []).map((h) => [h.id, h]));
  const jobs = new Map((ctx.jobs || []).map((j) => [j.id, j]));
  // 1. CONTACTS: household, workmates, the square (a few random meetings) -> fondness; everyone else fades
  const seen = new Map();
  const meet = (p, q) => { if (p === q) return; const k = p.id < q.id ? `${p.id}-${q.id}` : `${q.id}-${p.id}`; if (seen.has(k)) return; seen.set(k, 1); bump(p, q, DIALS.contactGain); };
  const byHome = {}, byJob = {};
  for (const p of people) { if (p.home) (byHome[p.home] = byHome[p.home] || []).push(p); if (p.job) (byJob[p.job] = byJob[p.job] || []).push(p); }
  for (const group of Object.values(byHome).concat(Object.values(byJob))) for (let i = 0; i < group.length; i++) for (let j = i + 1; j < group.length && j < i + DIALS.maxContacts; j++) meet(group[i], group[j]);
  for (const p of people) { for (let k = 0; k < 2 && people.length > 1; k++) meet(p, people[Math.floor(r() * people.length)]); }
  for (const p of people) {
    for (const id of Object.keys(p.friends)) {
      const q = byId(P, Number(id));
      const k = p.id < Number(id) ? `${p.id}-${id}` : `${id}-${p.id}`;
      if (!q || !q.alive) { delete p.friends[id]; continue; }
      if (!seen.has(k)) { p.friends[id] = Math.max(0, p.friends[id] - DIALS.contactFade); if (p.friends[id] === 0) delete p.friends[id]; }
    }
    // keep the friend list short: the fondest stay
    const keys = Object.keys(p.friends);
    if (keys.length > DIALS.maxFriends) { keys.sort((a, b) => p.friends[b] - p.friends[a]); for (const k of keys.slice(DIALS.maxFriends)) delete p.friends[k]; }
  }
  // 2. LIFECYCLE
  for (const p of people) {
    const a = age(p, day);
    if (a === DIALS.apprentice) ev.push({ kind: "grown", text: `${p.name} is grown and looks for work`, people: [p.id] });
    // F7 (D-C549): sickness — poor sanitation shortens lives (up to +60 % death chance), healers lengthen them (-30 % with an infirmary)
    const san = ctx.sanitation === undefined ? 1 : ctx.sanitation, care = Math.min(1, ctx.health || 0);
    const sick = (1 + 0.6 * (1 - san)) * (1 - 0.3 * care);
    if (a >= DIALS.death && r() < (a - DIALS.death + 1) / DIALS.deathSpan * sick) {
      p.alive = false; p.died = day;
      ev.push({ kind: "death", text: `${p.name} died at ${a} days${p.spouse ? `, mourned by ${byId(P, p.spouse)?.name || "the household"}` : ""}`, people: [p.id].concat(p.spouse ? [p.spouse] : [], p.kids) });
      for (const id of [p.spouse].concat(p.kids).filter(Boolean)) { const q = byId(P, id); if (q && q.alive) q.grief = 20; }
      if (p.spouse) { const sp = byId(P, p.spouse); if (sp) sp.spouse = null; }
      const passed = inherit(P, p, ctx, ev);
      if (p.job && !passed) { const j = jobs.get(p.job); if (j) j.vacant = true; }   // (review 10-04: an inherited station was also hired out)
    }
  }
  const living = alive(P);
  // marriages: two single adults fond of each other (one man, one woman: the births below), the spouse moves in where there is room
  const single = living.filter((p) => !p.spouse && stage(p, day) === "adult");
  for (const p of single) {
    if (p.spouse) continue;
    const match = Object.entries(p.friends).filter(([id, f]) => f >= DIALS.marryFond).map(([id]) => byId(P, Number(id)))
      .find((q) => q && q.alive && !q.spouse && q.sex !== p.sex && stage(q, day) === "adult" && !p.parents.includes(q.id) && !q.parents.includes(p.id)
        && !p.parents.some((x) => q.parents.includes(x)));                       // (review 10-04: no siblings)
    if (!match) continue;
    p.spouse = match.id; match.spouse = p.id;
    const hp = homes.get(p.home), hq = homes.get(match.home);
    if (hp && hq && hp !== hq) { if ((hq.room || 0) > 0) { p.home = match.home; hq.room--; hp.room = (hp.room || 0) + 1; } else if ((hp.room || 0) > 0) { match.home = p.home; hp.room--; hq.room = (hq.room || 0) + 1; } }
    ev.push({ kind: "wedding", text: `${p.name} and ${match.name} married`, people: [p.id, match.id] });
  }
  // births: a married woman 20..80 days old, a home with room, the town fed
  for (const p of living) {
    if (p.sex !== "f" || !p.spouse || !p.home) continue;
    const a = age(p, day);
    if (a < DIALS.apprentice || a > DIALS.fertile) continue;
    const h = homes.get(p.home);
    // 0.0.22 (run 0.0.21: 24 couples, 0 children, the founders all died within 30 days of each other — 52 people became 31):
    // a family home may hold DIALS.crowd children beyond its places (crowded; the grown move out to free rooms below)
    if (!h || ((h.room || 0) <= 0 && (h.over || 0) >= DIALS.crowd) || (ctx.fed ?? 1) < 0.9) continue;
    if (r() < DIALS.birthChance) {
      const baby = newPerson(P, day, { age: 0, home: p.home, parents: [p.id, p.spouse], seed: day });
      if ((h.room || 0) > 0) h.room--; else h.over = (h.over || 0) + 1;
      p.kids.push(baby.id); const f = byId(P, p.spouse); if (f) f.kids.push(baby.id);
      bump(p, baby, 50); if (f) bump(f, baby, 50);
      ev.push({ kind: "birth", text: `${p.name} and ${f ? f.name : "?"} have a ${baby.sex === "m" ? "son" : "daughter"}, ${baby.name}`, people: [p.id, baby.id].concat(f ? [f.id] : []) });
    }
  }
  // the grown children of a crowded home move out to a free room (a new household; the town builds more homes on demand)
  for (const p of living) {
    if (!p.alive || !p.home || !p.parents.length || age(p, day) < DIALS.moveOutAge) continue;
    if (!p.parents.some((id) => { const q = byId(P, id); return q && q.alive && q.home === p.home; })) continue;   // (review 10-04: the CHILD moves out, not the parent)
    const h = homes.get(p.home);
    if (!h || (h.over || 0) <= 0) continue;
    const to = (ctx.homes || []).find((x) => x.id !== p.home && (x.room || 0) > 0);
    if (!to) continue;
    h.over--; to.room--;
    const was = p.home;
    p.home = to.id;
    if (p.spouse) { const sp = byId(P, p.spouse); if (sp && sp.home === was && (to.room || 0) > 0) { sp.home = to.id; to.room--; h.room = (h.room || 0) + 1; } }
    ev.push({ kind: "moved", text: `${p.name} moved out of #${was} into #${to.id}`, people: [p.id] });
  }
  // 1.3.226 (his 20:48): a household whose house was bought for the town's core (home null) takes the first home with room
  // (the replacement house on the outskirts, once it stands); a spouse goes along
  for (const p of living) {
    if (!p.alive || p.home) continue;
    const to = (ctx.homes || []).find((x) => (x.room || 0) > 0);
    if (!to) continue;
    to.room--; p.home = to.id;
    ev.push({ kind: "moved", text: `${p.name} found a new home in #${to.id}`, people: [p.id] });
  }
  // 3. JOBS: grown people without work take a vacant station; children do not work
  const openJobs = (ctx.jobs || []).filter((j) => (j.vacancies || 0) > 0 || j.vacant);
  for (const p of living) {
    if (p.job || stage(p, day) === "child" || stage(p, day) === "apprentice" && age(p, day) < DIALS.child + 5) continue;
    const j = openJobs.find((x) => (x.vacancies || 0) > 0 || x.vacant);
    if (!j) break;
    p.job = j.id; p.trade = j.kind;
    if (j.vacant) j.vacant = false; else j.vacancies--;
  }
  // 3b. D-C550 LEARNING: today's experiences -> trust; skills grow with work; what was not met fades
  for (const p of living) {
    const st = stage(p, day);
    if (st === "child") continue;
    learn(p, "town:food", ctx.fed ?? 1, day);
    if (p.job) {
      const s0 = learn(p, `s:${p.job}`, ctx.paid === false ? 0.15 : 0.85, day);
      if (s0 >= LEARN.surprise && ctx.paid === false) ev.push({ kind: "grumble", text: `${p.name} was not paid and says so`, people: [p.id] });
      const tr = p.trade || "work";
      const before = rankOf(p, tr);
      (p.skill = p.skill || {})[tr] = skillOf(p, tr) + 1;
      const after = rankOf(p, tr);
      if (after !== before) {
        ev.push({ kind: "rank", text: `${p.name} is a ${after} ${tr} now`, people: [p.id] });
        if (after === "master" && !(P.masters = P.masters || {})[tr]) { P.masters[tr] = p.id; ev.push({ kind: "first", text: `${p.name} is the town's first master ${tr}`, people: [p.id] }); }
      }
    }
    learn(p, "town:council", (p.home ? 0.35 : 0) + (p.job || st === "elder" ? 0.35 : 0) + ((ctx.fed ?? 1) >= 1 ? 0.3 : 0), day);
    // the people met today: trust follows how they were (their mood) — a cheerful neighbour is trusted more
    for (const id of Object.keys(p.friends)) { const q = byId(P, Number(id)); if (q && q.alive && seen.has(p.id < q.id ? `${p.id}-${q.id}` : `${q.id}-${p.id}`)) learn(p, `p:${q.id}`, 0.3 + q.mood / 200, day); }
    forget(p, day);
  }
  // 4. MOOD (happiness): fed, housed, employed, paid, friends, family, grief
  let moodSum = 0;
  for (const p of living) {
    const st = stage(p, day);
    let m = 50;
    m += (ctx.fed ?? 1) >= 1 ? 20 : (ctx.fed ?? 1) >= 0.7 ? 0 : -30;
    m += p.home ? 10 : -20;
    if (st === "adult" || st === "elder") m += p.job ? 10 : (st === "adult" ? -10 : 0);
    if (p.job && ctx.paid === false) m -= 10;
    const friends = Object.values(p.friends).filter((f) => f >= DIALS.friend).length;
    m += friends >= 2 ? 10 : friends === 1 ? 4 : -4;
    if (p.spouse) m += 5;
    if (p.kids.length) m += 3;
    if (p.grief > 0) { m -= p.grief; p.grief = Math.max(0, p.grief - 1); }
    m += Math.round((trustOf(p, "town:council") - 0.5) * 20);              // D-C550: faith in the town (learned)
    if (ctx.sanitation !== undefined) m += Math.round((ctx.sanitation - 0.7) * 20);   // F7: a clean town (works vs people)
    p.mood = Math.round(0.7 * p.mood + 0.3 * Math.max(0, Math.min(100, m)));
    moodSum += p.mood;
    p.lowDays = p.mood < DIALS.leaveMood ? p.lowDays + 1 : 0;
  }
  const meanMood = living.length ? moodSum / living.length : 50;
  // 5. MIGRATION: the long unhappy leave (with their household); the faucet draws newcomers to a happy, fed town with room
  const departures = [];
  for (const p of living) {
    if (p.lowDays < DIALS.leaveDays) continue;
    p.alive = false; p.left = day;
    departures.push(p.id);
    if (p.home) { const h = homes.get(p.home); if (h) h.room = (h.room || 0) + 1; }
    if (p.job) { const j = jobs.get(p.job); if (j) j.vacant = true; }
    if (p.spouse) { const sp = byId(P, p.spouse); if (sp) sp.spouse = null; }
    ev.push({ kind: "left", text: `${p.name} left ${ctx.name || "the town"} unhappy`, people: [p.id] });
  }
  const arrivals = [];
  P.faucet = (P.faucet || 0) + 1;
  if (meanMood >= DIALS.faucetMood && (ctx.fed ?? 1) >= 1 && P.faucet >= DIALS.faucetEvery) {
    const h = (ctx.homes || []).find((x) => (x.room || 0) >= 2);              // 0.0.22: one place stays free for a birth or a grown child
    if (h) {
      P.faucet = 0;
      const p = newPerson(P, day, { home: h.id, seed: day * 3 });
      h.room--;
      arrivals.push(p.id);
      ev.push({ kind: "arrival", text: `${p.name} arrived and took a room in #${h.id}`, people: [p.id] });
    }
  }
  // 6. RUMOURS from the day's events, then word of mouth (friends tell friends), expiry
  for (const e of ev) if (["wedding", "birth", "death", "inherit", "escheat", "left", "arrival", "first", "grumble"].includes(e.kind)) {
    const witnesses = e.people.slice();
    for (let k = 0; k < 2 && living.length; k++) witnesses.push(living[Math.floor(r() * living.length)].id);
    rumour(P, day, e.kind, e.text, [...new Set(witnesses)], e.people);
  }
  for (const e of ctx.events || []) rumour(P, day, e.kind || "news", e.text, living.slice(0, 3).map((p) => p.id).concat(e.people || []), e.people || []);
  const fresh = new Set(P.rumours.filter((x) => day - x.day <= DIALS.rumourDays).map((x) => x.id));
  // 1.3.227 (profiled: the census day took 221..273 ms at city II): rumours by id, and each listener's knowledge as a set
  const ruById = new Map(P.rumours.map((x) => [x.id, x]));
  const kset = new Map();
  const knowsOf = (q) => { let s = kset.get(q.id); if (!s) { s = new Set(q.knows); kset.set(q.id, s); } return s; };
  for (const p of living) {
    p.knows = p.knows.filter((id) => fresh.has(id));
    if (!p.knows.length) continue;
    for (const [fid, f] of Object.entries(p.friends)) {
      if (f < DIALS.friend) continue;
      const q = byId(P, Number(fid));
      if (!q || !q.alive || r() > DIALS.tellChance) continue;
      const qs = knowsOf(q);
      for (const id of p.knows) if (!qs.has(id)) { qs.add(id); q.knows.push(id); const ru = ruById.get(id); if (ru) ru.heard++; }
    }
  }
  P.rumours = P.rumours.filter((x) => day - x.day <= DIALS.rumourDays * 2);
  // 7. THREADS: default courses on their deadlines
  for (const t of P.threads) {
    if (t.state !== "open") continue;
    if (day >= t.deadline) { closeThread(P, t, "resolved", t.data.defaultText || `${t.kind} ran its course`); ev.push({ kind: "thread", text: `${t.text} — ${t.closed}`, people: t.people }); }
  }
  P.threads = P.threads.filter((t) => t.state === "open" || day - (t.deadline || day) < 60);
  return { events: ev, arrivals, departures, meanMood };
}

/** what a keeper might tell the player: the freshest rumour the keeper knows, by their fondness for the player */
export function greeting(P, person, day) {
  const fond = person.playerFond || 0;
  const tier = fond >= DIALS.close ? "friend" : fond >= 20 ? "customer" : "stranger";
  const known = person.knows.map((id) => P.rumours.find((x) => x.id === id)).filter(Boolean).sort((a, b) => b.day - a.day);
  const tell = tier === "stranger" ? null : known[0] || null;
  return { tier, rumour: tell ? tell.text : null, open: P.threads.filter((t) => t.state === "open").length };
}
/** the player's standing with a person rises with every purchase (co-presence) */
export function playerContact(person, n = 5) { person.playerFond = Math.min(100, (person.playerFond || 0) + n); return person.playerFond; }
/** the notice board: the freshest rumours and open threads */
export function board(P, day, n = 6) {
  const rums = P.rumours.filter((x) => day - x.day <= DIALS.rumourDays).sort((a, b) => b.day - a.day).slice(0, n).map((x) => `day ${x.day}: ${x.text}`);
  const threads = P.threads.filter((t) => t.state === "open").map((t) => `#${t.id} ${t.text} (until day ${t.deadline})`);
  return { rumours: rums, threads };
}
export function meanMood(P) { const l = alive(P); return l.length ? l.reduce((a, p) => a + p.mood, 0) / l.length : 50; }

// ------------------------------------------------------------------------------------------------ WHY-IDLE (1.3.228 B2 / BF3)
// One reason code per person, from facts the schedule pass gathers (f). Priority: home > food > site > route, then the
// work module's own reason, then busy / rain / no site / no job. "—" = idle for a reason we do not know (the gate wants 0).
export const WHY = {
  WORKING: "at work (or on the way)",
  OFF_SHIFT: "off shift (dusk / night)",
  CHILD: "a child",
  NO_HOME: "no home",
  ASLEEP_CHUNK: "no body in loaded land",
  NO_STOCK: "the shopper found no shop with stock",
  SITE_WAITS: "the builders' sites wait for a material",
  UNREACHABLE: "could not reach the place (resting before trying again)",
  NO_ROUTE: "the route is still being searched / no walk graph yet",
  SLOTS_FULL: "no free walking lead (all slots taken)",
  NO_FACE: "no quarry face / no real tree in reach",
  STOCK_FULL: "the workshop's store chest is full",
  RAIN: "sent home by the rain",
  NO_SITE: "a builder with no labour site",
  NO_JOB: "no job",
  HOME_FAR: "home too far from work (reserved: PE5)",
  UNPAID: "not paid (reserved: WP1)",
  "—": "idle, reason unknown",
};
/** f = { child, asleep, phase: "work" | "off", noStock, siteWaits: <good> | null, walk: code | null, worker: code | null,
 *  busy, wet, builderIdle } */
export function whyOf(person, f = {}) {
  if (!person) return "—";
  if (f.child) return "CHILD";
  if (!person.home) return "NO_HOME";
  if (f.asleep) return "ASLEEP_CHUNK";
  if (f.phase !== "work") return "OFF_SHIFT";
  if (f.noStock) return "NO_STOCK";
  if (f.siteWaits) return `SITE_WAITS:${f.siteWaits}`;
  if (f.walk) return f.walk;
  if (f.worker) return f.worker;
  if (f.busy) return "WORKING";
  if (f.wet) return "RAIN";
  if (f.builderIdle) return "NO_SITE";
  if (!person.job) return "NO_JOB";
  return "—";
}
/** a tally {code: n} kept to at most `cap` keys (the rarest go to "other") */
export function capTally(t, cap = 16) {
  const e = Object.entries(t).sort((a, b) => b[1] - a[1]);
  if (e.length <= cap) return Object.fromEntries(e);
  const out = Object.fromEntries(e.slice(0, cap - 1));
  out.other = e.slice(cap - 1).reduce((a, [, n]) => a + n, 0);
  return out;
}
