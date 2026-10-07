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
// 1.3.228 B3 (PEOPLE I): the mood is a weighted mean of non-neutral factors with escalating unmet needs and carried needs
// pressure; mood tiers set work output; grief by closeness; births by food, happiness and fullness; rumours start with their
// own people and each person keeps 10; the house level gates the skill rank; temperament and interest from the id. All of
// the batch's constants and flags are in the B3 block below (FLAGS, NEEDS, OUTPUT, GRIEF, BIRTH, RUMOUR, SKILL, HOME_LEVEL).
// (DIALS.birthChance is superseded by BIRTH.base.)
// 1.3.228 B4 (PEOPLE II): personal shift templates with the id's start offset and a 7-day plan (SHIFT), the walk home and
// the home-too-far complaint (COMMUTE), the rain ruling (RAIN: quarrymen, woodcutters, builders shelter and keep half),
// varied work beats and look-at spots per trade (WORKBEAT, LOOK), the inn for the unhappy (INN), the nearest free place and
// the move to another town when none is free (MOVE, PLACES) — the B4 block, above WHY-IDLE.
// 1.3.230 (HD, his 2026-10-06 21:39 / 21:47): HOUSEHOLDS & DYNASTY — grown children move out at adulthood into the best free
// home they can afford, a person carries a line (p.dyn), heirs sell or move into the better house, and every move queues a
// restoration paid by the town (a household buying a free home pays the town back) — the HD block, above WHY-IDLE.
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
      if (day - (p.died ?? p.left ?? day) >= 1) {
        if (p.trust) delete p.trust; if (p.knows && p.knows.length) p.knows = [];
        delete p.hl; delete p.jl; delete p.grief; delete p.lowDays; delete p.playerFond;   // 1.3.228 B3: day counters go too
      }
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
// ============================================================================================================================
// 1.3.228 B3 — PEOPLE I (census law). EVERY constant and flag of the batch is HERE, in one place, so a ruling flips one value.
// Abs0lum's rulings: no random negative effects, no sickness, no violence; deterministic consequences are fine.
// ============================================================================================================================
export const FLAGS = {
  SANITATION_DEATH: false,  // Q4 default: poor sanitation no longer raises the death chance (was up to +60 %); it is a mood factor only
  STRIKE: false,            // Q2 (his 12:20 10-06): no full strike; a miserable workshop never falls below OUTPUT.floor (0.50)
  TEMPER_INHERIT: false,    // PE8: a town-born child takes a parent's temperament (one small int for town-born people); off = id only
};
/** BF4 — the MOOD SUM (MineColonies' law on our census): the weighted mean of the factors that are NOT neutral (a factor of
 *  exactly 1 leaves the average: numerator and denominator), target mood = 50 x that mean (factors 0..2 -> mood 0..100).
 *  An UNMET need (factor < 1: no home, no job, the town hungry) escalates: x0.75 from day 7, x0.5 from day 14.
 *  NEEDS PRESSURE (Townstead's drift): hunger (town-wide: food is the town's stock) and fatigue (an understaffed workplace)
 *  add a daily pressure to a CARRIED drift; only whole points move mood, the fraction is carried to the next day. */
export const NEEDS = {
  W: { food: 4, home: 3, job: 2, paid: 2, friends: 2, family: 1, grief: 3, council: 1, sanitation: 1, diet: 1 },
  fedFull: 1, fedLow: 0.7, fedFamished: 0.4,           // ledger prosperity (the share who ate) bands
  food: { full: 1.8, low: 0.2 },                       // fed >= 1: 1.8; fedLow..1: neutral; below fedLow: 0.2 (escalates)
  home: { none: 0.2, base: 1.4, perLevel: 0.1 },       // housed: 1.4 + 0.1 per house level above 1; homeless 0.2 (escalates)
  job: { has: 1.8, none: 0.5 },                        // adults and working elders; a jobless adult 0.5 (escalates); else neutral
  unpaid: 0.5,                                         // wages in arrears (a job holder)
  friends: [0.8, 1.4, 1.8],                            // 0 / 1 / 2+ friends (fondness >= DIALS.friend)
  family: { spouse: 1.6, kids: 0.2, kidsOnly: 1.3 },   // married 1.6 (+0.2 with children); children without a spouse 1.3
  griefDiv: 25,                                        // grief g -> 1 - g/25 (grief 20 -> 0.2)
  sanMid: 0.7, sanSlope: 1.5,                          // Q4: sanitation s -> 1 + 1.5 (s - 0.7), clamped 0..2 (mood only)
  diet: { ok: 1.3, short: 0.7, shortFrom: 3 },         // PE4: variety >= 1 + ceil(lvl/2) -> 1.3; below it at lvl >= 3 -> 0.7
  dietPer: { bread: 1, meat: 0.5, fish: 0.5, grain: 0.5 },   // a day's need per person, for "stock > 1 day of need"
  foodPerDay: 1.5,                                     // bread 1 + meat 0.5 a person (ECON.EAT): the food stock in days
  escalate: [[14, 0.5], [7, 0.75]],                    // unmet for >= 14 days x0.5, >= 7 days x0.75
  keep: 0.7,                                           // mood smoothing: yesterday's share (unchanged from 1.3.227)
  hunger: { well: 0.5, wellDays: 5, hungry: -1.5, famished: -3, starving: -5 },   // daily pressure by the town's food band
  fatigue: { rate: 1, loadMax: 2 },                    // per day: -rate x min(loadMax, (holders + vacancies) / holders - 1)
};
/** BF4 — mood tier -> work output (ECON abstract runs and the real work pace). Q2 default: never below floor (no strike). */
export const OUTPUT = { tiers: [[90, 1.2], [75, 1.1], [50, 1.0], [30, 0.85], [15, 0.7]], floor: 0.50, strikeMood: 15, strikeDays: 3 };   // his 12:20: floor 50 %
/** PE3 — grief by closeness (the mourner keeps the largest that applies; -1 a day as before) */
export const GRIEF = { spouse: 20, child: 20, parent: 15, sibling: 10, close: 8, friend: 4, closeFond: 70, friendFond: 40 };
/** PE6 — births: base x (0.5 + household mood/100) x min(foodMax, foodDays/foodRef) x (1 - fullCut x fullness) */
export const BIRTH = { base: 0.03, fedMin: 0.9, foodRef: 10, foodMax: 1.5, fullCut: 0.5, kidsPerHome: 2 };
/** PE12 — a rumour is known by its people only when it starts; each person keeps the newest `cap`; a teller passes at most
 *  `tellPerDay` new ones to each friend a day (his or her interest first) */
export const RUMOUR = { cap: 10, tellPerDay: 3 };
/** PE4 + PE7 — the skill law: output 1 + cap x (1 - e^(-days/tau)); a day worked gives 1 point, real work acts (a dug block,
 *  a chop) add actXP each, the first repFree at full rate, the rest x repX (repetition), the day's total capped at dayCap.
 *  The house level gates the rank: journeyman needs a home of level >= 1, master >= 2 (the days still count while gated). */
export const SKILL = { cap: 0.5, tau: 60, dayCap: 1.5, actXP: 0.05, repFree: 8, repX: 0.35, gate: { journeyman: 1, master: 2 } };   // 8 acts +0.4, the cap at 14
/** PE4 — house level by building kind (a keeper lives in rooms over the shop: any other kind = 3; palace* = 5) */
export const HOME_LEVEL = { cottage_s: 1, cottage_m: 1, farm_wheat: 1, farm_terrace: 1, farm_cattle: 1, cottage_l: 2, inn: 2, townhouse: 3, manor: 4, palace: 5 };
export const HOME_LEVEL_SHOP = 3;
/** PE8 — temperament and interest from the id (no save) */
export const TEMPERS = ["cheerful", "dour", "talkative", "shy", "proud", "worrier", "steady", "curious"];
export const INTERESTS = ["building", "trade", "food", "family", "the sea", "the woods", "the town", "news"];
export const TEMPER_TELL = { talkative: 1.5, curious: 1.2, dour: 0.8, shy: 0.6 };   // x DIALS.tellChance (clamped to 1)
export const INTEREST_KINDS = { family: ["wedding", "birth", "death", "line"], trade: ["inherit", "escheat", "first", "grumble", "sold"], "the town": ["arrival", "left", "news", "thread"] };   // 1.3.230 (HD): + line, sold

const clamp01x = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
/** a 32-bit integer hash (murmur3 finaliser) of an id and a salt */
export function hash32(n, salt = 0) {
  let h = (Math.imul((Number(n) | 0) ^ salt, 0x9E3779B1) + salt) >>> 0;
  h ^= h >>> 16; h = Math.imul(h, 0x85EBCA6B) >>> 0; h ^= h >>> 13; h = Math.imul(h, 0xC2B2AE35) >>> 0; h ^= h >>> 16;
  return h >>> 0;
}
/** PE8: the temperament index 0..7 (p.tm only when FLAGS.TEMPER_INHERIT stored one at birth) */
export function temperOf(p) { return p.tm ?? hash32(p.id, 0x7E4F) % TEMPERS.length; }
export function interestOf(p) { return hash32(p.id, 0x1A7E) % INTERESTS.length; }
export const temperName = (p) => TEMPERS[temperOf(p)];
export const interestName = (p) => INTERESTS[interestOf(p)];
/** PE4: a building kind's house level (0 = no home) */
export function homeLevel(kind) {
  if (!kind) return 0;
  if (HOME_LEVEL[kind] !== undefined) return HOME_LEVEL[kind];
  return String(kind).startsWith("palace") ? HOME_LEVEL.palace : HOME_LEVEL_SHOP;
}
// the house level each person had at the last census day (memory only: never saved; re-learned on the first day after a load)
const LVL = new WeakMap();
export function levelOf(p) { return LVL.get(p); }
export function noteLevel(p, lvl) { LVL.set(p, lvl); }
/** BF4: the escalation multiplier of an unmet need after `days` days */
export function escalation(days) { for (const [d, m] of NEEDS.escalate) if ((days || 0) >= d) return m; return 1; }
/** BF4: carry a pressure: returns [whole points that move mood today, the fraction carried (2 decimals)] */
export function carry(prev, pressure) {
  const t = (prev || 0) + pressure, w = Math.trunc(t);
  return [w, Math.round((t - w) * 100) / 100];
}
/** BF4: the town's hunger pressure for the day (fed = the share who ate; foodDays = the food stock in days of need) */
export function hungerPressure(fed = 1, foodDays = 0) {
  const H = NEEDS.hunger;
  if (fed >= NEEDS.fedFull) return foodDays >= H.wellDays ? H.well : 0;
  if (fed >= NEEDS.fedLow) return H.hungry;
  if (fed >= NEEDS.fedFamished) return H.famished;
  return H.starving;
}
/** BF4: an understaffed workplace's fatigue pressure (holders after the day's hiring, vacancies still open) */
export function fatiguePressure(holders, vacancies) {
  if (!holders || !(vacancies > 0)) return 0;
  return -NEEDS.fatigue.rate * Math.min(NEEDS.fatigue.loadMax, (holders + vacancies) / holders - 1);
}
/** PE4: food variety = the food goods with stock above one day of need */
export function dietVariety(stock = {}, population = 0) {
  let n = 0;
  for (const [g, per] of Object.entries(NEEDS.dietPer)) if ((stock[g] || 0) > per * Math.max(1, population)) n++;
  return n;
}
/** PE6 / BF4: the town's food stock in days of need */
export function foodDaysOf(stock = {}, population = 0) {
  const food = (stock.bread || 0) + (stock.meat || 0) + (stock.fish || 0);
  return population > 0 ? food / (NEEDS.foodPerDay * population) : (food > 0 ? Infinity : 0);
}
/** BF4: one person's mood factors (a factor of exactly 1 is neutral). c = { day, fed, paid, hd (town hungry days), lvl, diet,
 *  san } */
export function moodParts(p, c = {}) {
  const N = NEEDS, out = {};
  const st = stage(p, c.day ?? p.born), fed = c.fed ?? 1, lvl = c.lvl ?? (p.home ? 1 : 0);
  out.food = fed >= N.fedFull ? N.food.full : fed >= N.fedLow ? 1 : N.food.low * escalation(c.hd);
  out.home = p.home ? N.home.base + N.home.perLevel * (Math.max(1, lvl) - 1) : N.home.none * escalation(p.hl);
  out.job = (st === "adult" || st === "elder") && p.job ? N.job.has : st === "adult" ? N.job.none * escalation(p.jl) : 1;
  out.paid = p.job && c.paid === false ? N.unpaid : 1;
  let fr = 0;
  for (const f of Object.values(p.friends || {})) if (f >= DIALS.friend) fr++;
  out.friends = N.friends[Math.min(2, fr)];
  out.family = p.spouse ? N.family.spouse + ((p.kids || []).length ? N.family.kids : 0) : (p.kids || []).length ? N.family.kidsOnly : 1;
  out.grief = p.grief > 0 ? clamp01x(1 - p.grief / N.griefDiv, 0, 1) : 1;
  out.council = clamp01x(1 + 2 * (trustOf(p, "town:council") - 0.5), 0, 2);
  out.sanitation = c.san === undefined || c.san === null ? 1 : clamp01x(1 + N.sanSlope * (c.san - N.sanMid), 0, 2);
  out.tax = c.tax ?? 1;                                                     // 1.3.228 (B7 / WE11): the tax dial (low 1.06 / high 0.94)
  if (c.diet === undefined || c.diet === null || !p.home) out.diet = 1;
  else out.diet = c.diet >= 1 + Math.ceil(lvl / 2) ? N.diet.ok : lvl >= N.diet.shortFrom ? N.diet.short : 1;
  return out;
}
/** BF4: the target mood of a set of factors: 50 x the weighted mean of the non-neutral ones (all neutral -> 50) */
export function moodTarget(parts) {
  let s = 0, w = 0;
  for (const [k, f] of Object.entries(parts)) {
    if (Math.abs(f - 1) < 1e-9) continue;                                   // neutral: leaves the average
    const wt = NEEDS.W[k] ?? 1;
    s += wt * f; w += wt;
  }
  return w ? clamp01x(50 * s / w, 0, 100) : 50;
}
/** BF4: a mood's output factor (the tiers; Q2: never below OUTPUT.floor unless FLAGS.STRIKE and the strike holds) */
export function moodFactor(mood) {
  const m = mood ?? 50;
  for (const [min, f] of OUTPUT.tiers) if (m >= min) return f;
  return OUTPUT.floor;
}
/** BF4: the mood-tier histogram of the living (keys t90 t75 t50 t30 t0) */
export function moodTiers(P) {
  const h = { t90: 0, t75: 0, t50: 0, t30: 0, t0: 0 };
  for (const p of P.list) {
    if (!p.alive) continue;
    const m = p.mood ?? 50;
    if (m >= 90) h.t90++; else if (m >= 75) h.t75++; else if (m >= 50) h.t50++; else if (m >= 30) h.t30++; else h.t0++;
  }
  return h;
}
/** BF4: each workplace's output factor from the mean mood of its people (keyed by job id; "fisher" for the fishermen).
 *  With FLAGS.STRIKE, a workplace whose mean stayed below OUTPUT.strikeMood for OUTPUT.strikeDays census days gives 0. */
export function workMood(P) {
  const sum = new Map();
  for (const p of P.list) {
    if (!p.alive || p.job === null || p.job === undefined) continue;
    const e = sum.get(p.job) || [0, 0];
    e[0] += p.mood ?? 50; e[1]++;
    sum.set(p.job, e);
  }
  const out = {};
  const sk = (P.need && P.need.sk) || {};
  for (const [job, [s, n]] of sum) {
    out[job] = FLAGS.STRIKE && (sk[job] || 0) >= OUTPUT.strikeDays ? 0 : moodFactor(s / n);
  }
  return out;
}
/** PE6: the birth chance of a household (o = { mood, foodDays, fullness }); monotonic up in mood and food, down in fullness */
export function birthChance({ mood = 50, foodDays, fullness = 0 } = {}) {
  const food = foodDays === undefined || foodDays === null ? 1 : Math.min(BIRTH.foodMax, Math.max(0, foodDays) / BIRTH.foodRef);
  return BIRTH.base * (0.5 + clamp01x(mood, 0, 100) / 100) * food * (1 - BIRTH.fullCut * clamp01x(fullness, 0, 1));
}
/** PE7: a day's skill gain: 1 for the day worked + real acts (repetition-decayed), capped at SKILL.dayCap */
export function skillGain(acts = 0) {
  const a = Math.max(0, Math.floor(acts || 0));
  const xp = SKILL.actXP * (Math.min(a, SKILL.repFree) + SKILL.repX * Math.max(0, a - SKILL.repFree));
  return Math.min(SKILL.dayCap, 1 + xp);
}

/** GROWTH of a person: days worked in a trade -> apprentice / journeyman / master. B3 (PE4): the house level gates the rank
 *  (lvl undefined = not known yet: ungated); the output follows the concave curve up to the gated rank's ceiling. */
export function skillOf(person, trade) { return (person.skill && person.skill[trade]) || 0; }
export function rawRank(d) { return d >= LEARN.master ? "master" : d >= LEARN.journeyman ? "journeyman" : "apprentice"; }
export function rankOf(person, trade, lvl = levelOf(person)) {
  const r = rawRank(skillOf(person, trade));
  if (lvl === undefined || lvl === null) return r;
  if (r !== "apprentice" && lvl < SKILL.gate.journeyman) return "apprentice";
  if (r === "master" && lvl < SKILL.gate.master) return "journeyman";
  return r;
}
export function outputFactor(person, trade, lvl = levelOf(person)) {
  let d = skillOf(person, trade);
  const r = rankOf(person, trade, lvl);
  if (r === "apprentice") d = Math.min(d, LEARN.journeyman); else if (r === "journeyman") d = Math.min(d, LEARN.master);
  return 1 + SKILL.cap * (1 - Math.exp(-d / SKILL.tau));
}

/** a deterministic random from a seed (mulberry32) */
export function rng(seed) { let a = seed >>> 0; return () => { a += 0x6D2B79F5; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

export function newPerson(P, day, opts = {}) {
  const r = rng((P.next * 7919 + (opts.seed || 0)) >>> 0);
  const sex = opts.sex || (r() < 0.5 ? "m" : "f");
  const names = sex === "m" ? NAMES_M : NAMES_F;
  // 1.3.228 (B3): grief, lowDays and playerFond are stored only while non-zero (every reader treats a missing one as 0)
  const p = { id: P.next++, name: opts.name || names[Math.floor(r() * names.length)], sex, born: day - (opts.age !== undefined ? opts.age : DIALS.apprentice + Math.floor(r() * 60)),
              home: opts.home ?? null, job: opts.job ?? null, trade: opts.trade ?? null, spouse: null, parents: opts.parents || [], kids: [], friends: {}, mood: 55, alive: true,
              knows: [] };
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

/** PE12: a person learns rumour `id`, keeping only the newest RUMOUR.cap (rumour ids grow with time). Returns false when it
 *  is already known or older than everything a full memory holds (it would be dropped at once — no churn, no false "heard") */
export function know(p, id) {
  const k = p.knows || (p.knows = []);
  if (k.includes(id)) return false;
  if (k.length >= RUMOUR.cap) {
    let lo = 0;
    for (let i = 1; i < k.length; i++) if (k[i] < k[lo]) lo = i;
    if (id < k[lo]) return false;
    k.splice(lo, 1);
  }
  k.push(id);
  return true;
}
/** PE12: newest RUMOUR.cap of a knowledge list (an old save's long lists are cut on the first day) */
export function capKnows(p) { if (p.knows && p.knows.length > RUMOUR.cap) p.knows = p.knows.slice().sort((a, b) => a - b).slice(-RUMOUR.cap); }
/** a rumour known from today by the people in `who` ONLY (PE12: its participants — no random witnesses); `heard` counts the
 *  tellings after that (word of mouth in dayStep) */
export function rumour(P, day, kind, text, who = [], about = []) {
  const r = { id: P.rumours.length ? P.rumours[P.rumours.length - 1].id + 1 : 1, day, kind, text, about, heard: 0 };
  P.rumours.push(r);
  for (const id of who) { const p = byId(P, id); if (p) know(p, r.id); }
  return r;
}
// ------------------------------------------------------------------------------------------------ B10 (1.3.228): THE WATCH'S MORALE
// His 12:20 ruling: "unpaid + low morale -> walks half his rounds; below the 'would resort to crime' morale -> leaves town.
// MEASURE the crime factors now (no crime enabled)." p.mor (watchmen only; saved while held): an unpaid day x0.7, a paid,
// housed and fed day +2 (cap 100). Below WATCH_M.half the round skips every other stop (the watch module reads it); below
// WATCH_M.crime he leaves town (a departure, never a crime). CRIME: the factors are MEASURED for every grown person
// (FLAGS.CRIME stays false: nothing reads them but the gate's [CIV-CRIME] line).
export const WATCH_M = { start: 60, unpaidX: 0.7, goodDay: 2, half: 40, crime: 20, cap: 100 };
export function watchMorale(mor, c = {}) {
  const m = mor ?? WATCH_M.start;
  if (c.paid === false) return Math.round(m * WATCH_M.unpaidX * 10) / 10;
  if (c.housed && c.fed) return Math.min(WATCH_M.cap, m + WATCH_M.goodDay);
  return m;
}
export const halfRounds = (p) => !!p && p.job === "watch" && (p.mor ?? WATCH_M.start) < WATCH_M.half;
export const CRIME = { enabled: false, risk: 5 };
/** the crime factors of one person (measured only): { score, parts } — unpaid 2 · homeless 3+ days 2 · the town hungry
 *  1 (7+ days 2) · jobless 5+ days 1 · mood < 30 2 (< 15 3) */
export function crimeFactors(p, c = {}) {
  const parts = {};
  if (p.job && c.paid === false) parts.unpaid = 2;
  if ((p.hl || 0) >= 3) parts.homeless = 2;
  if ((c.hd || 0) > 0) parts.hungry = (c.hd || 0) >= 7 ? 2 : 1;
  if ((p.jl || 0) >= 5) parts.jobless = 1;
  const m = p.mood ?? 50;
  if (m < 15) parts.mood = 3; else if (m < 30) parts.mood = 2;
  const score = Object.values(parts).reduce((a, v) => a + v, 0);
  return { score, parts };
}
/** B5 (BF11): the petition outcome — mirrors pw_civ_talk.petitionMet (kept here: talk imports people, never the reverse) */
export const PETITION_FOND = { kept: 10, broken: 5, mood: 5 };
export function petitionNeedMet(need, p, town = {}) {
  if (need === "home") return !!p.home;
  if (need === "job") return !!p.job;
  if (need === "food") return !(town.hd > 0);
  if (need === "wages") return !(town.arrears > 0);
  if (need === "site") return !town.siteWaits;
  return false;
}
/** a thread: a live situation with a default course on its deadline */
export function openThread(P, day, kind, text, people, deadline, data = {}) {
  const t = { id: P.nextThread++, kind, text, people, day, deadline, state: "open", data, lines: [] };
  P.threads.push(t);
  return t;
}
export function closeThread(P, t, how, text) { t.state = how; t.closed = text; }

/** PE3: grief by closeness at a death — spouse and children 20, parents 15, siblings 10, friends whose fondness for the dead
 *  is >= 70: 8, >= 40: 4. A mourner keeps the largest that applies (and any larger grief already held). */
export function mourn(P, dead, people = alive(P)) {
  const set = new Map();
  const give = (q, g) => { if (q && q.alive && q !== dead && g > (set.get(q) || 0)) set.set(q, g); };
  if (dead.spouse) give(byId(P, dead.spouse), GRIEF.spouse);
  for (const id of dead.kids || []) give(byId(P, id), GRIEF.child);
  for (const id of dead.parents || []) give(byId(P, id), GRIEF.parent);
  const par = dead.parents || [];
  for (const q of people) {
    if (q === dead || !q.alive) continue;
    if (par.length && (q.parents || []).some((x) => par.includes(x))) give(q, GRIEF.sibling);
    const f = q.friends && q.friends[dead.id];
    if (f >= GRIEF.closeFond) give(q, GRIEF.close); else if (f >= GRIEF.friendFond) give(q, GRIEF.friend);
  }
  for (const [q, g] of set) q.grief = Math.max(q.grief || 0, g);
  return set;
}
function bump(p, q, n) {
  p.friends[q.id] = Math.min(100, (p.friends[q.id] || 0) + n);
  q.friends[p.id] = Math.min(100, (q.friends[p.id] || 0) + n);
}
function inherit(P, dead, ctx, ev, kinOf = null) {
  // succession = lookups: kin (spouse, then the eldest child), then the closest friend, then the town
  // 1.3.230 (HD): the LINE's kin (p.dyn: grandchildren, brothers, nephews — the eldest grown first) come before a friend;
  // a shop never passes to a child (an orphan keeps the house, the station is hired out). Returns { passed, heir }.
  const heirs = [];
  if (dead.spouse) { const sp = byId(P, dead.spouse); if (sp && sp.alive) heirs.push(sp); }
  for (const kid of dead.kids.map((id) => byId(P, id)).filter((k) => k && k.alive).sort((a, b) => a.born - b.born)) heirs.push(kid);
  const close = heirs.length;
  const kin = kinOf ? kinOf(dead) : [];
  for (const q of kin) heirs.push(q);
  const friend = Object.entries(dead.friends).sort((a, b) => b[1] - a[1]).map(([id]) => byId(P, Number(id))).find((f) => f && f.alive && f.friends[dead.id] >= DIALS.friend);
  if (friend) heirs.push(friend);
  const heir = heirs[0] || null;
  const held = { home: dead.home, job: dead.job };
  let passed = false;
  if (heir) {
    const grown = ctx.day === undefined || stage(heir, ctx.day) !== "child";
    if (held.job && !heir.job && typeof held.job === "number" && grown) { heir.job = held.job; heir.trade = dead.trade; passed = true; }   // a shop passes to kin; an OFFICE (a string post: builders, sewer keeper) never does (D-C539)
    const viaLine = !close && kin.length && heir === kin[0] ? ` (of ${lineName(P, dead)}'s line)` : "";
    ev.push({ kind: "inherit", text: `${dead.name}'s ${held.job ? "shop" : "house"} passes to ${heir.name}${viaLine}${!viaLine && heir === friend ? " (a friend; no kin)" : ""}`, people: [dead.id, heir.id], held, heir: heir.id });
  } else ev.push({ kind: "escheat", text: `${dead.name} left no kin: the town takes the ${held.job ? "shop" : "house"}`, people: [dead.id], held, heir: null });
  return { passed, heir };
}
/** 1.3.230 (HD): the dead's house after the inheritance. S = { homes: Map, lvl(id), res: Map(home -> residents today),
 *  touch(id), deeds }. The dead's place is free today. When nobody lives on there: no heir -> the town takes it (queued for
 *  restoration); the heir lives elsewhere -> a better house (level above the heir's) takes the heir's household when it
 *  holds them all (a child heir never moves) and the old house is sold when they left it empty; otherwise the heir sells
 *  the inherited house to the town (a 'sell' deed: the price by level, paid by the clock from the treasury). */
function houseAfterDeath(P, dead, heir, day, S, ev) {
  const hid = dead.home;
  if (hid === null || hid === undefined) return;
  const h = S.homes.get(hid);
  if (h) { if ((h.over || 0) > 0) h.over--; else h.room = (h.room || 0) + 1; }
  const left = Math.max(0, (S.res.get(hid) || 1) - 1);
  S.res.set(hid, left);
  if (left > 0) return;                                                    // the widow, the children live on there
  if (!heir) { S.touch(hid); return; }                                     // escheat: the town restores it for a newcomer
  if (heir.home === hid) return;
  const sell = (id, lvl, what) => {
    const price = Math.round(priceOf(lvl) * HOUSING.sellShare);
    S.deeds.push({ kind: "sell", home: id, lvl, price, pid: heir.id });
    S.touch(id);
    ev.push({ kind: "sold", text: `${heir.name} sold ${what} #${id} to the town`, people: [heir.id], home: id, price });
  };
  const from = heir.home, lvD = S.lvl(hid), lvH = from === null || from === undefined ? 0 : S.lvl(from);
  if (h && lvD > lvH && stage(heir, day) !== "child") {
    const hh = household(P, heir, day);
    if ((h.room || 0) >= hh.length) {
      for (const q of hh) q.home = hid;
      h.room -= hh.length;
      S.res.set(hid, hh.length);
      S.touch(hid);
      ev.push({ kind: "moved", text: `${heir.name}${hh.length > 1 ? ` and ${hh.length - 1} of the household` : ""} moved into ${dead.name}'s better house #${hid}`, people: hh.map((q) => q.id) });
      if (from !== null && from !== undefined) {
        const fh = S.homes.get(from);
        if (fh) { const k = Math.min(fh.over || 0, hh.length); if (k) fh.over -= k; fh.room = (fh.room || 0) + hh.length - k; }
        const rest = Math.max(0, (S.res.has(from) ? S.res.get(from) : hh.length) - hh.length);
        S.res.set(from, rest);
        S.touch(from);
        if (rest <= 0) sell(from, lvH, "the old house");
      }
      return;
    }
  }
  sell(hid, lvD, `${dead.name}'s house`);
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
  const jobAt = (p) => (p.job !== null && p.job !== undefined ? jobs.get(p.job) || null : null);   // B4 (BF7): {x, z} when the clock gave them
  // 1.3.228 B3: house levels (ctx.levels: Map | {id: lvl}; absent = not known: the rank is ungated), the day's real work
  // acts per person (ctx.acts: Map pid -> n, memory only), the town's needs state (P.need, saved only while non-zero)
  const levels = !ctx.levels ? null : ctx.levels instanceof Map ? ctx.levels : new Map(Object.entries(ctx.levels).map(([k, v]) => [Number.isNaN(Number(k)) ? k : Number(k), v]));
  const lvlOf = (p) => !levels ? undefined : p.home ? (levels.has(p.home) ? levels.get(p.home) : 1) : 0;
  const acts = ctx.acts instanceof Map ? ctx.acts : null;
  // 1.3.230 (HD): every home moved out of / into today (-> restore, the clock queues its restoration), the day's deeds
  // (house sales and purchases: the clock settles them with the ledger), the residents per home (the last one's death),
  // the house level of a home (ctx.levels; unknown 1), the people of each line (built at the first death)
  const touched = new Set(), deeds = [];
  const touch = (id) => { if (id !== null && id !== undefined) touched.add(id); };
  const lvlH = (id) => (levels && levels.has(id) ? levels.get(id) : 1);
  const resAt = new Map();
  for (const p of people) if (p.home !== null && p.home !== undefined) resAt.set(p.home, (resAt.get(p.home) || 0) + 1);
  let lineIdx = null;
  const lineKin = (d0) => {
    if (!lineIdx) { lineIdx = new Map(); for (const q of people) { const k = dynOf(q); if (!lineIdx.has(k)) lineIdx.set(k, []); lineIdx.get(k).push(q); } }
    return (lineIdx.get(dynOf(d0)) || []).filter((q) => q.alive && q !== d0)
      .sort((a, b) => ((stage(a, day) === "child") - (stage(b, day) === "child")) || (a.born - b.born) || (a.id - b.id));
  };
  const houses = { homes, lvl: lvlH, res: resAt, touch, deeds };
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
    // F7 (D-C549): healers lengthen lives (-30 % with an infirmary). 1.3.228 B3 (Q4 default): poor sanitation no longer
    // raises the death chance (it was up to +60 %: sickness, a chance-based harm) — it is a mood factor only; the old rule
    // stays behind FLAGS.SANITATION_DEATH
    const san = ctx.sanitation === undefined ? 1 : ctx.sanitation, care = Math.min(1, ctx.health || 0);
    const sick = (FLAGS.SANITATION_DEATH ? 1 + 0.6 * (1 - san) : 1) * (1 - 0.3 * care);
    if (a >= DIALS.death && r() < (a - DIALS.death + 1) / DIALS.deathSpan * sick) {
      p.alive = false; p.died = day;
      ev.push({ kind: "death", text: `${p.name} died at ${a} days${p.spouse ? `, mourned by ${byId(P, p.spouse)?.name || "the household"}` : ""}`, people: [p.id].concat(p.spouse ? [p.spouse] : [], p.kids) });
      mourn(P, p, people);                                                   // B3 / PE3: grief by closeness
      if (p.spouse) { const sp = byId(P, p.spouse); if (sp) sp.spouse = null; }
      const inh = inherit(P, p, ctx, ev, lineKin);                           // 1.3.230 (HD): the line's kin before a friend
      if (p.job && !inh.passed) { const j = jobs.get(p.job); if (j) j.vacant = true; }   // (review 10-04: an inherited station was also hired out)
      houseAfterDeath(P, p, inh.heir, day, houses, ev);                      // 1.3.230 (HD): sold, or the heir moves in
      const ln = dynOf(p);                                                   // 1.3.230 (HD): the last of a named line
      if (P.lines && P.lines[ln] !== undefined && !lineKin(p).length) { ev.push({ kind: "line", text: `with ${p.name}'s death the line of ${P.lines[ln]} ends`, people: [p.id] }); delete P.lines[ln]; }
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
    if (hp && hq && hp !== hq) { if ((hq.room || 0) > 0) { p.home = match.home; hq.room--; hp.room = (hp.room || 0) + 1; touch(hp.id); touch(hq.id); } else if ((hp.room || 0) > 0) { match.home = p.home; hp.room--; hq.room = (hq.room || 0) + 1; touch(hp.id); touch(hq.id); } }   // 1.3.230 (HD): queued
    ev.push({ kind: "wedding", text: `${p.name} and ${match.name} married`, people: [p.id, match.id] });
  }
  // births: a married woman 20..80 days old, a home with room, the town fed.
  // 1.3.228 B3 (PE6): the chance follows the household's happiness and the town's food stock (in days of need) and falls as
  // the town's homes fill (fullness = housed / (housed + free places)); at most BIRTH.kidsPerHome children in a home
  let housed = 0, free = 0;
  for (const q of living) if (q.home) housed++;
  for (const h of ctx.homes || []) free += Math.max(0, h.room || 0);
  const fullness = housed + free > 0 ? housed / (housed + free) : 0;
  const kidsAt = new Map();
  for (const q of living) if (q.home && stage(q, day) === "child") kidsAt.set(q.home, (kidsAt.get(q.home) || 0) + 1);
  for (const p of living) {
    if (p.sex !== "f" || !p.spouse || !p.home) continue;
    const a = age(p, day);
    if (a < DIALS.apprentice || a > DIALS.fertile) continue;
    const h = homes.get(p.home);
    // 0.0.22 (run 0.0.21: 24 couples, 0 children, the founders all died within 30 days of each other — 52 people became 31):
    // a family home may hold DIALS.crowd children beyond its places (crowded; the grown move out to free rooms below)
    if (!h || ((h.room || 0) <= 0 && (h.over || 0) >= DIALS.crowd) || (ctx.fed ?? 1) < BIRTH.fedMin) continue;
    if ((kidsAt.get(p.home) || 0) >= BIRTH.kidsPerHome) continue;
    const sp = byId(P, p.spouse);
    const hm = sp && sp.alive ? ((p.mood ?? 50) + (sp.mood ?? 50)) / 2 : (p.mood ?? 50);
    if (r() < birthChance({ mood: hm, foodDays: ctx.foodDays, fullness })) {
      const baby = newPerson(P, day, { age: 0, home: p.home, parents: [p.id, p.spouse], seed: day });
      // 1.3.230 (HD): the child's LINE is the father's (else the mother's); a line is named on its first town-born child
      const line = birthLine(p, sp && sp.alive ? sp : null);
      baby.dyn = line;
      if (!(P.lines = P.lines || {})[line]) { const fnd = byId(P, line); P.lines[line] = fnd ? fnd.name : (sp && sp.alive ? sp : p).name; }
      const ofLine = sp && sp.alive && line !== sp.id ? `, of the line of ${P.lines[line]}` : "";
      kidsAt.set(p.home, (kidsAt.get(p.home) || 0) + 1);
      if (FLAGS.TEMPER_INHERIT && hash32(baby.id, 0x1E1) % 2 === 0) { const from = byId(P, [p.id, p.spouse][hash32(baby.id, 0x2E2) % 2]); if (from) { const t = temperOf(from); if (t !== hash32(baby.id, 0x7E4F) % TEMPERS.length) baby.tm = t; } }
      if ((h.room || 0) > 0) h.room--; else h.over = (h.over || 0) + 1;
      p.kids.push(baby.id); const f = byId(P, p.spouse); if (f) f.kids.push(baby.id);
      bump(p, baby, 50); if (f) bump(f, baby, 50);
      ev.push({ kind: "birth", text: `${p.name} and ${f ? f.name : "?"} have a ${baby.sex === "m" ? "son" : "daughter"}, ${baby.name}${ofLine}`, people: [p.id, baby.id].concat(f ? [f.id] : []) });
    }
  }
  // 1.3.230 (HD; his 21:39 "children moving out of their parents' home when they grow up … upgrade to better homes when
  // they move out"): MOVE OUT AT ADULTHOOD — supersedes the crowded-home-only rule (0.0.22). An adult (moveOutAge, elders
  // too) still living with a parent leaves whenever a free home holds the household (him, a spouse wherever she lives,
  // their children at home): the BEST level the household can afford (affordLevel of its earners' daily wages), the one
  // nearest his work on a tie. At most HOUSING.moveOutPerDay households a town a day: the crowded homes first, then the
  // eldest. The household BUYS the free home (a 'buy' deed); both homes are queued for restoration. The parents / kids
  // arrays stay (genealogy); the household rules (births, crowding, moves) follow the home, so the link ends here.
  const withParent = (p) => p.parents.some((id) => { const q = byId(P, id); return q && q.alive && q.home === p.home; });   // (review 10-04: the CHILD moves out, not the parent)
  const crowdedAt = (p) => (((homes.get(p.home) || {}).over || 0) > 0 ? 1 : 0);
  const leavers = living.filter((p) => p.alive && p.home && p.parents.length && age(p, day) >= DIALS.moveOutAge && withParent(p))
    .sort((a, b) => (crowdedAt(b) - crowdedAt(a)) || (a.born - b.born) || (a.id - b.id));
  let outN = 0;
  const freeList = leavers.length ? (ctx.homes || []).filter((x) => (x.room || 0) > 0) : [];   // (a city of 10,000: scan the free homes only)
  for (const p of freeList.length ? leavers : []) {
    if (outN >= HOUSING.moveOutPerDay) break;
    if (!p.alive || !p.home || !withParent(p)) continue;                     // gone with a spouse today
    const hh = household(P, p, day);
    const sp = p.spouse ? byId(P, p.spouse) : null;
    if (sp && sp.alive && !hh.includes(sp)) for (const q of household(P, sp, day)) if (!hh.includes(q)) hh.push(q);
    const means = hh.reduce((a, q) => a + (q.job !== null && q.job !== undefined && stage(q, day) !== "child" ? (ctx.wageOf ? ctx.wageOf(q) || 0 : HOUSING.wage) : 0), 0);
    const cap = affordLevel(means), at = new Set(hh.map((q) => q.home));
    const fits = freeList.filter((x) => !at.has(x.id) && (x.room || 0) >= hh.length && lvlH(x.id) <= cap);
    if (!fits.length) continue;
    // the best level; an EMPTY house of it (a home of their own) before a place in another household's; then nearest work
    const best = Math.max(...fits.map((x) => lvlH(x.id)));
    const anyEmpty = fits.some((x) => lvlH(x.id) === best && !(resAt.get(x.id) > 0));
    const to = nearestFree(fits, jobAt(p) || homes.get(p.home), (x) => lvlH(x.id) === best && (!anyEmpty || !(resAt.get(x.id) > 0)));
    const was = p.home;
    for (const q of hh) {
      const fh = homes.get(q.home);
      if (fh) { if ((fh.over || 0) > 0) fh.over--; else fh.room = (fh.room || 0) + 1; }
      touch(q.home);
      if (q.home !== null && q.home !== undefined) resAt.set(q.home, Math.max(0, (resAt.get(q.home) || 1) - 1));
      q.home = to.id;
    }
    resAt.set(to.id, (resAt.get(to.id) || 0) + hh.length);
    to.room -= hh.length;
    touch(to.id);
    deeds.push({ kind: "buy", home: to.id, lvl: best, price: Math.round(priceOf(best) * HOUSING.buyShare), pid: p.id });
    outN++;
    ev.push({ kind: "moved", text: `${p.name}${hh.length > 1 ? ` and ${hh.length - 1} of the household` : ""} left the family home #${was} for a home of their own, #${to.id}${best > lvlH(was) ? " (a better house)" : ""}`, people: hh.map((q) => q.id) });
  }
  // 1.3.226 (his 20:48): a household whose house was bought for the town's core (home null) takes the first home with room
  // (the replacement house on the outskirts, once it stands); a spouse goes along
  for (const p of living) {
    if (!p.alive || p.home) continue;
    const to = nearestFree(ctx.homes, jobAt(p), (x) => (x.room || 0) > 0);   // B4 (BF7): the room nearest his work
    if (!to) continue;
    to.room--; p.home = to.id; touch(to.id);                                 // 1.3.230 (HD): queued
    ev.push({ kind: "moved", text: `${p.name} found a new home in #${to.id}`, people: [p.id] });
  }
  // 3. JOBS: grown people without work take a vacant station; children do not work. B4 (BF7): the free one NEAREST the home
  // 1.3.228 fix (gate 228-10: the night watch and the sewer keeper were never hired): the TOWN'S POSTS (string ids —
  // builders, surveyor, carters, sewer keeper, civic posts, healers, fishers, the watch) are filled before the shops
  // (numeric building ids), as the list order did before B4; the nearest-to-home choice holds within each class
  const openJobs = (ctx.jobs || []).filter((j) => (j.vacancies || 0) > 0 || j.vacant);
  // 1.3.231 (INN24): a third class between them — the inn's COVER (its first INN24.cover staff: open round the clock)
  const isFree = (x) => ((x.vacancies || 0) > 0 || x.vacant) && (!x.base || (x.base.vacancies || 0) > 0);
  const { town: townPosts, cover: coverPosts, shops: shopPosts } = hireClasses(openJobs, living);
  for (const p of living) {
    if (p.job || stage(p, day) === "child" || stage(p, day) === "apprentice" && age(p, day) < DIALS.child + 5) continue;
    const at = homes.get(p.home);
    const j = nearestFree(townPosts, at, isFree) || nearestFree(coverPosts, at, isFree) || nearestFree(shopPosts, at, isFree);
    if (!j) break;
    p.job = j.id; p.trade = j.kind;
    if (j.vacant) j.vacant = false; else j.vacancies--;
    if (j.base) j.base.vacancies--;                                          // the cover share is one of the inn's own
  }
  // 3c. B4 (BF7 / PE5): a home more than COMMUTE.far from work — the household takes a free room within COMMUTE.near of the
  // work (MOVE.far households a town a day, by id), else he complains (every COMMUTE.sayEvery days)
  let farN = 0, farMoved = 0;
  for (const p of living) {
    if (!p.alive || !p.home || p.job === null || p.job === undefined || stage(p, day) === "child") continue;
    const h = homes.get(p.home), j = jobs.get(p.job);
    if (!homeFar(h, j)) continue;
    farN++;
    if (farMoved < MOVE.far) {
      const hh = household(P, p, day);
      const to = nearestFree(ctx.homes, j, (x) => x.id !== p.home && (x.room || 0) >= hh.length && placeDist(x, j) <= COMMUTE.near);
      if (to) {
        for (const q of hh) q.home = to.id;
        to.room -= hh.length;
        const k = Math.min(h.over || 0, hh.length); if (k) h.over -= k; h.room = (h.room || 0) + hh.length - k;
        touch(h.id); touch(to.id);                                           // 1.3.230 (HD): queued
        farMoved++;
        ev.push({ kind: "moved", text: `${p.name} moved nearer work, into #${to.id}${hh.length > 1 ? ` with ${hh.length - 1} of the household` : ""}`, people: hh.map((q) => q.id) });
        continue;
      }
    }
    if ((day + p.id) % COMMUTE.sayEvery === 0) ev.push({ kind: "far", text: `${p.name} complains that home is a long walk from work (${Math.round(homeWorkDist(h, j))} blocks)`, people: [p.id] });
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
      // B3 (PE4 + PE7): the rank is gated by the house level; a day's gain = 1 + the day's real acts (repetition-decayed),
      // capped at SKILL.dayCap; one decimal is kept
      const lv = lvlOf(p), lv0 = levelOf(p);                               // lv0: yesterday's level (memory)
      const before = rankOf(p, tr, lv0 === undefined ? lv : lv0);           // a better home opening the gate is news today
      (p.skill = p.skill || {})[tr] = Math.round((skillOf(p, tr) + skillGain(acts ? acts.get(p.id) : 0)) * 10) / 10;
      const after = rankOf(p, tr, lv);
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
  // 4. MOOD (happiness) — 1.3.228 B3 (BF4): the weighted mean of the non-neutral factors (food, home, job, paid, friends,
  // family, grief, council trust, sanitation, diet), unmet needs escalating at 7 / 14 days; then the needs PRESSURE: the
  // town's hunger and each understaffed workplace's fatigue go into carried drifts, and only whole points move mood
  const need = (P.need = P.need || {});
  const fed = ctx.fed ?? 1;
  need.hd = fed < NEEDS.fedLow ? (need.hd || 0) + 1 : 0;                     // the town's hungry days (food is town-wide)
  let hungerW;
  [hungerW, need.h] = carry(need.h, hungerPressure(fed, ctx.foodDays ?? 0));
  const holders = new Map();
  for (const p of living) if (p.alive && p.job !== null && p.job !== undefined) holders.set(p.job, (holders.get(p.job) || 0) + 1);
  const tired = {}, fc = need.f || {}, nf = {};
  for (const [job, n] of holders) {
    const j = jobs.get(job);
    const pr = j ? fatiguePressure(n, (j.vacancies || 0) + (j.vacant ? 1 : 0)) : 0;
    if (!pr) continue;                                                       // fully staffed: rested, the drift goes
    const [w, c] = carry(fc[job], pr);
    tired[job] = w;
    if (c) nf[job] = c;
  }
  need.f = nf;                                                               // only understaffed workplaces keep a drift
  const partSum = {};
  let moodSum = 0;
  for (const p of living) {
    const st = stage(p, day);
    // day counters of unmet needs (stored only while > 0)
    if (p.mem) { for (const [k, d] of Object.entries(p.mem)) if (d < day) delete p.mem[k]; if (!Object.keys(p.mem).length) delete p.mem; }   // B5 (PE10)
    if (!p.home) p.hl = (p.hl || 0) + 1; else delete p.hl;
    if (st === "adult" && !p.job) p.jl = (p.jl || 0) + 1; else delete p.jl;
    const lv = lvlOf(p);
    if (lv !== undefined) noteLevel(p, lv);
    const parts = moodParts(p, { day, fed, paid: ctx.paid, hd: need.hd, lvl: lv, diet: ctx.diet, san: ctx.sanitation, tax: ctx.taxMood });
    for (const [k, f] of Object.entries(parts)) partSum[k] = (partSum[k] || 0) + f;
    if (p.grief > 0) { p.grief -= 1; if (p.grief <= 0) delete p.grief; } else delete p.grief;
    const rested = ctx.restOf ? ctx.restOf(p) : false;                         // B4 (BF5) hook: a rest day carries no fatigue
    const m = Math.round(NEEDS.keep * (p.mood ?? 50) + (1 - NEEDS.keep) * moodTarget(parts)) + hungerW + (rested ? 0 : (tired[p.job] || 0));
    p.mood = Math.max(0, Math.min(100, m));
    moodSum += p.mood;
    p.lowDays = p.mood < DIALS.leaveMood ? (p.lowDays || 0) + 1 : 0;
    if (!p.lowDays) delete p.lowDays;
    if (!p.playerFond) delete p.playerFond;
  }
  const meanMood = living.length ? moodSum / living.length : 50;
  // Q2: the strike counter (only with FLAGS.STRIKE): census days a workplace's mean mood stayed below OUTPUT.strikeMood
  if (FLAGS.STRIKE) {
    const sk = need.sk || {}, wm = new Map();
    for (const p of living) if (p.job !== null && p.job !== undefined) { const e = wm.get(p.job) || [0, 0]; e[0] += p.mood; e[1]++; wm.set(p.job, e); }
    const out = {};
    for (const [job, [s, n]] of wm) if (s / n < OUTPUT.strikeMood) out[job] = (sk[job] || 0) + 1;
    need.sk = out;
  } else delete need.sk;
  if (!need.h) delete need.h;
  if (!need.hd) delete need.hd;
  if (!Object.keys(need.f || {}).length) delete need.f;
  if (!Object.keys(need).length) delete P.need;
  // 5. MIGRATION: the long unhappy leave (with their household); the faucet draws newcomers to a happy, fed town with room
  // B10 (WP1 + his ruling): the watch's morale, the half rounds, the watchman who leaves; the crime factors MEASURED
  const crime = { atRisk: 0, max: 0, parts: {} };
  const watchLeft = [];
  for (const p of living) {
    if (!p.alive) continue;
    if (p.job === "watch") {
      p.mor = watchMorale(p.mor, { paid: ctx.watchPaid !== false, housed: !!p.home, fed: (ctx.fed ?? 1) >= NEEDS.fedLow });
      if (p.mor < WATCH_M.crime) watchLeft.push(p);
    } else if (p.mor !== undefined) delete p.mor;
    if (stage(p, day) === "child") continue;
    const cf = crimeFactors(p, { paid: ctx.paid, hd: need.hd || 0 });
    if (cf.score > crime.max) crime.max = cf.score;
    if (cf.score >= CRIME.risk) crime.atRisk++;
    for (const k of Object.keys(cf.parts)) crime.parts[k] = (crime.parts[k] || 0) + 1;
  }
  const departures = [];
  for (const p of watchLeft) {
    p.alive = false; p.left = day; delete p.mor;
    departures.push(p.id);
    if (p.home) { const h = homes.get(p.home); if (h) h.room = (h.room || 0) + 1; touch(p.home); }   // 1.3.230 (HD): queued
    if (p.spouse) { const sp = byId(P, p.spouse); if (sp) sp.spouse = null; }
    ev.push({ kind: "left", text: `${p.name} gave up the watch and left ${ctx.name || "the town"} (unpaid, his morale gone)`, people: [p.id] });
  }
  for (const p of living) {
    if (!p.alive) continue;
    if ((p.lowDays || 0) < DIALS.leaveDays) continue;                       // B3: stored only while non-zero
    p.alive = false; p.left = day;
    departures.push(p.id);
    if (p.home) { const h = homes.get(p.home); if (h) h.room = (h.room || 0) + 1; touch(p.home); }   // 1.3.230 (HD): queued
    if (p.job) { const j = jobs.get(p.job); if (j) j.vacant = true; }
    if (p.spouse) { const sp = byId(P, p.spouse); if (sp) sp.spouse = null; }
    ev.push({ kind: "left", text: `${p.name} left ${ctx.name || "the town"} unhappy`, people: [p.id] });
  }
  // B4 (BF7): no home (MOVE.homeless days) or, for an adult, no work (MOVE.jobless days) and none free here: the household
  // moves to another town with room (ctx.elsewhere({people, job, why}) -> {id, name} | null, the clock's choice); they
  // leave here like any departure and the clock enters them in that town's census (PEOPLE.adopt). No other town: they stay
  const movers = [];
  if (ctx.elsewhere) {
    const anyRoom = (ctx.homes || []).some((x) => (x.room || 0) > 0);
    const anyJob = (ctx.jobs || []).some((x) => (x.vacancies || 0) > 0 || x.vacant);
    for (const p of living) {
      if (movers.length >= MOVE.perDay) break;
      if (!p.alive) continue;
      const stg = stage(p, day);
      if (stg === "child") continue;
      const noHome = !p.home && (p.hl || 0) >= MOVE.homeless && !anyRoom;
      const noJob = !noHome && !!p.home && stg === "adult" && !p.job && (p.jl || 0) >= MOVE.jobless && !anyJob;
      if (!noHome && !noJob) continue;
      const hh = household(P, p, day);
      const why = noHome ? "home" : "job";
      const to = ctx.elsewhere({ people: hh.length, job: noJob, why });
      if (!to) continue;
      const ids = hh.map((q) => q.id);
      for (const q of hh) {
        q.alive = false; q.left = day;
        departures.push(q.id);
        if (q.home) { const h = homes.get(q.home); if (h) h.room = (h.room || 0) + 1; touch(q.home); }   // 1.3.230 (HD): queued
        if (q.job) { const j = jobs.get(q.job); if (j) j.vacant = true; }
        if (q.spouse && !ids.includes(q.spouse)) { const sp = byId(P, q.spouse); if (sp) sp.spouse = null; q.spouse = null; }
      }
      ev.push({ kind: "left", text: `${p.name}${hh.length > 1 ? ` and ${hh.length - 1} of the household` : ""} left for ${to.name || "another town"}: no ${why === "home" ? "home" : "work"} free here`, people: ids });
      movers.push({ ids, people: hh, to: to.id, why });
    }
  }
  const arrivals = [];
  P.faucet = (P.faucet || 0) + 1;
  if (meanMood >= DIALS.faucetMood && (ctx.fed ?? 1) >= 1 && P.faucet >= DIALS.faucetEvery) {
    // 0.0.22: one place stays free for a birth or a grown child. B4 (BF7): the room nearest an open job
    const open = (ctx.jobs || []).filter((j) => ((j.vacancies || 0) > 0 || j.vacant) && Number.isFinite(j.x));
    let h = null, hd = Infinity;
    for (const x of ctx.homes || []) { if ((x.room || 0) < 2) continue; const d = open.length ? Math.min(...open.map((j) => placeDist(x, j))) : 0; if (h === null || d < hd) { h = x; hd = d; } }
    if (h) {
      P.faucet = 0;
      const p = newPerson(P, day, { home: h.id, seed: day * 3 });
      h.room--; touch(h.id);                                                 // 1.3.230 (HD): queued
      arrivals.push(p.id);
      ev.push({ kind: "arrival", text: `${p.name} arrived and took a room in #${h.id}`, people: [p.id] });
    }
  }
  // 6. RUMOURS from the day's events, then word of mouth (friends tell friends), expiry.
  // 1.3.228 B3 (PE12): a rumour starts known by its own people only (the random witnesses are gone) and `heard` counts the
  // tellings; everyone keeps the newest RUMOUR.cap. PE8: a teller passes at most RUMOUR.tellPerDay new ones to a friend a day,
  // those of his interest first, then the newest; a talkative teller tells more often, a shy one less (TEMPER_TELL)
  for (const e of ev) if (["wedding", "birth", "death", "inherit", "escheat", "left", "arrival", "first", "grumble", "sold", "line"].includes(e.kind)) {   // 1.3.230 (HD): + sold, line
    rumour(P, day, e.kind, e.text, [...new Set(e.people)], e.people);
  }
  for (const e of ctx.events || []) rumour(P, day, e.kind || "news", e.text, (e.people && e.people.length ? e.people : living.slice(0, 1).map((p) => p.id)), e.people || []);
  const fresh = new Set(P.rumours.filter((x) => day - x.day <= DIALS.rumourDays).map((x) => x.id));
  // 1.3.227 (profiled: the census day took 221..273 ms at city II): rumours by id
  const ruById = new Map(P.rumours.map((x) => [x.id, x]));
  for (const p of living) { if (p.knows.length) { p.knows = p.knows.filter((id) => fresh.has(id)); capKnows(p); } }
  for (const p of living) {
    if (!p.alive || !p.knows.length) continue;
    const kinds = INTEREST_KINDS[INTERESTS[interestOf(p)]] || null;
    const mine = (id) => { const ru = ruById.get(id); return kinds && ru && kinds.includes(ru.kind) ? 1 : 0; };
    const order = p.knows.slice().sort((a, b) => (mine(b) - mine(a)) || (b - a));
    const tell = Math.min(1, DIALS.tellChance * (TEMPER_TELL[TEMPERS[temperOf(p)]] || 1));
    for (const [fid, f] of Object.entries(p.friends)) {
      if (f < DIALS.friend) continue;
      const q = byId(P, Number(fid));
      if (!q || !q.alive || r() > tell) continue;
      let told = 0;
      for (const id of order) {
        if (told >= RUMOUR.tellPerDay) break;
        if (!know(q, id)) continue;
        told++;
        const ru = ruById.get(id); if (ru) ru.heard++;
      }
    }
  }
  P.rumours = P.rumours.filter((x) => day - x.day <= DIALS.rumourDays * 2);
  // 7. THREADS: default courses on their deadlines
  for (const t of P.threads) {
    if (t.state !== "open") continue;
    if (day < t.deadline) continue;
    if (t.kind === "petition" && t.data && t.data.pid !== undefined) {
      // 1.3.228 (B5 / BF11): the player promised "I'll see to it" — the deadline checks the NEED itself (the census's own facts)
      const q = byId(P, t.data.pid);
      const met = !!q && q.alive && petitionNeedMet(t.data.need, q, { hd: need.hd || 0, arrears: ctx.paid === false ? 1 : 0, siteWaits: !!ctx.siteWaits });
      if (q && q.alive) {
        if (met) { q.playerFond = Math.min(100, (q.playerFond || 0) + PETITION_FOND.kept); q.mood = Math.min(100, (q.mood ?? 50) + PETITION_FOND.mood); }
        else q.playerFond = Math.max(0, (q.playerFond || 0) - PETITION_FOND.broken);
      }
      closeThread(P, t, met ? "kept" : "broken", met ? "the matter was seen to" : "nothing was done");
      ev.push({ kind: "thread", text: `${t.text} — ${t.closed}`, people: t.people });
      continue;
    }
    closeThread(P, t, "resolved", t.data.defaultText || `${t.kind} ran its course`); ev.push({ kind: "thread", text: `${t.text} — ${t.closed}`, people: t.people });
  }
  P.threads = P.threads.filter((t) => t.state === "open" || day - (t.deadline || day) < 60);
  // B3 diagnostics (memory: the clock logs them, never saves them): mean factor per name, today's pressure points, fullness
  const parts = {};
  for (const [k, v] of Object.entries(partSum)) parts[k] = Math.round(v / Math.max(1, living.length) * 100) / 100;
  // 1.3.230 (HD): a line with no living member leaves the register (every 10 days; a death tells it at once)
  if (P.lines && day % 10 === 0) {
    const live = new Set();
    for (const q of P.list) if (q.alive) live.add(dynOf(q));
    for (const k of Object.keys(P.lines)) if (!live.has(Number(k))) delete P.lines[k];
    if (!Object.keys(P.lines).length) delete P.lines;
  }
  return { events: ev, arrivals, departures, meanMood, parts, hungerW, tired, fullness: Math.round(fullness * 100) / 100, movers, far: farN, farMoved, crime,
           deeds, restore: [...touched].filter((id) => typeof id === "number" && Number.isFinite(id)) };   // 1.3.230 (HD)
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

// ------------------------------------------------------------------------------------------------ B4 (1.3.228): PEOPLE II
// BF5 personal shifts + a 7-day plan, PE5 the walk home / home too far / rain, PE1 varied work beats, PE2 the inn for the
// unhappy, BF7 the nearest free place (and a move to another town when there is none). Pure: the clock, the shop, the
// work and the watch beats ask these; nothing here touches the engine. Every constant of the batch is in this block.
//
// BF5 — a template is 24 letters, one an HOUR (hour 0 = midnight = tod 18000; tod 0 = 06:00): W work, M meet (dusk: the
// square, the inn), I idle (leisure by day), R rest (at home). The template comes from the job (nothing stored); p.shift
// (a template id, the only saved shift field) is set only by the `shift` command. Each person's day runs START_OFFSET
// ticks early or late (-200..+200, from the id), and a 7-day plan gives OFF days (consecutive; the first from the id and
// the town's seed; keepers all rest on the town's own day). The week day is the WORLD's day (world.getDay()), so a day off
// is a whole game day whatever the clock's speed.
export const SHIFT = {
  T: {
    standard: "RRRRRRRWWWWWWWWWWMMRRRRR",   // work 07..17 (tod 1000..11000: the old town-wide SCHED), meet 17..19
    early:    "RRRRRRWWWWWWWWWWIMMRRRRR",   // fishers, farmers: work 06..16, idle 16, meet 17..19
    late:     "RRRRRRRRIWWWWWWWWWWMRRRR",   // keepers, the inn: idle 08, work 09..19 (tod 3000..13000), meet 19..20
    night:    "WWWWWRRRRRRRRRRRRMMWWWWW",   // the watch: work 19..05 (tod 13000..23000: the old NIGHT), rest by day, meet 17..19
    day:      "RRRRRRRWWWWWWWWWWMMRRRRR",   // the sewer keeper (his own id, so a command can move him alone)
    child:    "RRRRRRRIIIIIIIIIIMMRRRRR",   // children play by day
    // 1.3.231 (INN24, his 00:23 CT 10-07: the inn open 24 h / late, several employees): the inn's ROTA (innRota below)
    inn_solo:   "RRRRRRWWWWWWWWWWWWWWWWWR", // a lone innkeeper: 06..23 (all daylight and the evening)
    inn_long_d: "RRRRRRWWWWWWWWWWWWIMRRRR", // two staff: the day half 06..18
    inn_long_n: "WWWWWWIRRRRRRRRRIIWWWWWW", //            the night half 18..06
    inn_day:    "RRRRRRWWWWWWWWIIIMMRRRRR", // three or more: the day keeper 06..14
    inn_eve:    "RRRRRRRRIIIIIIWWWWWWWWIR", //                the evening (the taproom) 14..22
    inn_night:  "WWWWWWIRRRRRRRRIIIMMIIWW", //                the night keeper 22..06
    inn_serve:  "RRRRRRRRIIIIIWWWWWWWWIIR", //                serving staff at the busy hours 13..21
  },
  off: { standard: 1, early: 1, late: 1, night: 2, day: 1, child: 0,
         inn_solo: 0, inn_long_d: 0, inn_long_n: 0, inn_day: 0, inn_eve: 0, inn_night: 0, inn_serve: 1 },   // days off in 7 (the inn's cover shifts: shorter days, no whole day off)
  offset: 200,                                                              // start offset: -200 .. +200 ticks from the id
};
const SH_SALT = 0x5F1F, REST_SALT = 0x0D7A;
/** the hour (0..23) of a time of day (tod 0 = 06:00) */
export function hourOf(tod) { return Math.floor((((tod + 6000) % 24000) + 24000) % 24000 / 1000); }
/** BF5: a person's start offset in ticks (-200..+200), stable per id, never stored */
export function shiftOffset(id) { return hash32(id, SH_SALT) % (2 * SHIFT.offset + 1) - SHIFT.offset; }
/** BF5: the template id of a person — the override (p.shift) first, then by job: watch night, sewer keeper day, fishers and
 *  farmers early, keepers (not of a quarry, a lumberyard or a farm) and the inn's people late, children child, else standard.
 *  o = { kind: the workplace's kind (short), keeper, child } */
export function shiftTemplate(p, o = {}) {
  if (p && p.shift && SHIFT.T[p.shift]) return p.shift;
  if (o.child) return "child";
  if (p && o.inn && typeof o.inn.get === "function" && o.inn.has(p.id)) return o.inn.get(p.id);   // 1.3.231 (INN24): the inn's rota
  const job = p ? p.job : null, kind = o.kind || (p && p.trade) || "";
  if (job === "watch") return "night";
  if (job === "sewer_keeper") return "day";
  if (job === "fisher" || String(kind).startsWith("farm_")) return "early";
  if (kind === "inn" || (o.keeper && kind && kind !== "quarry" && kind !== "lumberyard")) return "late";
  return "standard";
}
/** BF5: the first day off of a person's week (0..6): keepers rest on the town's day, everyone else from the id */
// 1.3.228 (B4 review): keepers rest on their OWN day too (one shared rest day closed every shop one day in 7)
export function restStart(p, seed = 0, keeper = false) { return (hash32(p.id, REST_SALT) + (seed >>> 0)) % 7; }
/** BF5: is world day `day` a day off for p? o = { tpl, seed, keeper } */
export function dayOff(p, day, o = {}) {
  const tpl = o.tpl || shiftTemplate(p, o);
  const n = SHIFT.off[tpl] || 0;
  if (n <= 0) return false;
  return ((((day - restStart(p, o.seed || 0, !!o.keeper)) % 7) + 7) % 7) < n;
}
/** BF5 + PE5: where a person's day stands. tod = world time of day, day = world day; o = { tpl, kind, keeper, child, seed,
 *  travel: ticks of the walk home (0 = not known) }. Returns { slot: W|M|I|R, tpl, hour, off (a day off), home (leaving
 *  early to be home when the rest block starts), toRest (ticks until it starts) }.
 *  A day off turns its W hours into I. PE5: a person in W / M / I leaves `travel` ticks before the next R block, so he is
 *  home when it starts (a far home ends the work early; a near one only shortens the evening). */
export function shiftAt(p, tod, day, o = {}) {
  const tpl = o.tpl || shiftTemplate(p, o);
  const T = SHIFT.T[tpl] || SHIFT.T.standard;
  const A = day * 24000 + tod - (isInnTpl(tpl) ? 0 : shiftOffset(p.id));   // 1.3.231 (INN24): the rota hands over on the hour (no gap)
  const d = Math.floor(A / 24000), t = A - d * 24000;
  const hour = hourOf(t);
  let slot = T[hour];
  const off = dayOff(p, d, { ...o, tpl });
  if (off && slot === "W") slot = "I";
  let toRest = Infinity, home = false;
  if (slot !== "R") {
    let k = 1;
    while (k < 24 && T[(hour + k) % 24] !== "R") k++;
    toRest = k * 1000 - ((t + 6000) % 1000);
    // 1.3.231 (INN24): an inn cover shift is never cut short by the walk home — the staffer leaves when relieved
    if (o.travel > 0 && toRest <= o.travel && !(slot === "W" && isInnTpl(tpl))) { home = true; slot = "R"; }
  }
  return { slot, tpl, hour, off, home, toRest };
}
/** BF5: is a person at work now (slot W)? */
export function onShift(p, tod, day, o = {}) { return shiftAt(p, tod, day, o).slot === "W"; }

// PE5 — the walk home (MineColonies: 6 ticks a block, a climb x1.5), the complaint and the move
export const COMMUTE = { perBlock: 6, climb: 1.5, far: 160, near: 80, max: 3000, sayEvery: 10 };
/** PE5: ticks to walk from a to b ({x, y, z}): 6 x the length with the rise counted 1.5 times, capped at COMMUTE.max */
export function travelTicks(a, b) {
  if (!a || !b) return 0;
  const len = Math.hypot((a.x || 0) - (b.x || 0), (a.z || 0) - (b.z || 0), COMMUTE.climb * ((a.y || 0) - (b.y || 0)));
  return Math.min(COMMUTE.max, Math.ceil(COMMUTE.perBlock * len));
}
/** PE5: the level distance between home and work (blocks), or null when either place is not known */
export function homeWorkDist(h, j) { return h && j && Number.isFinite(h.x) && Number.isFinite(j.x) ? Math.hypot(h.x - j.x, h.z - j.z) : null; }
/** PE5: a home more than COMMUTE.far blocks from work is a complaint (HOME_FAR) */
export function homeFar(h, j) { const d = homeWorkDist(h, j); return d !== null && d > COMMUTE.far; }

// RAIN (his ruling, 2026-10-06): quarrymen, woodcutters and builders SHELTER in rain and keep HALF their output; every
// other trade works on (fishermen fish in the rain, the keepers are indoors)
export const RAIN = { keep: 0.5, trades: ["quarry", "lumberyard", "builders", "builder"], measureMin: 0.25 };
/** the share of a day's output a trade keeps when `wet` of its work time was rain (0..1): 1 - 0.5 x wet for the three */
export function rainKeep(trade, wet = 1) { return RAIN.trades.includes(trade) ? 1 - (1 - RAIN.keep) * Math.max(0, Math.min(1, wet)) : 1; }
/** a real day's carried output of a quarry / lumberyard when `wet` of the work time was rain: the dry hours' rate carried
 *  over the wet hours at half (when at least RAIN.measureMin of the day was dry), else half the abstract rate over them */
export function rainOutput(trade, carried, wet, abstract = 0) {
  const w = Math.max(0, Math.min(1, wet || 0));
  if (!RAIN.trades.includes(trade) || w <= 0) return carried;
  const dry = 1 - w;
  if (dry >= RAIN.measureMin) return carried + RAIN.keep * (carried / dry) * w;
  return carried + RAIN.keep * abstract * w;
}

// PE1 — varied work beats: while at work a keeper / station worker picks one beat a BEAT window (600 ticks), weighted
// (Liberty's pool: the main task 8, near the station 5, a second spot 5, the side tasks 6 and 7), deterministic by id and
// window; look-at spots per trade come from the template's own blocks (furnace, smoker, anvil, lectern, barrels ...)
export const WORKBEAT = { window: 600, reach: 4, w: [["main", 8], ["near", 5], ["second", 5], ["store", 6], ["door", 7]] };
const WB_TOTAL = WORKBEAT.w.reduce((a, [, n]) => a + n, 0);
/** PE1: the beat of person `pid` at tick `tick` */
export function beatOf(pid, tick) {
  let h = hash32((Number(pid) * 2654435761 + Math.floor(tick / WORKBEAT.window)) >>> 0, 0xBEA7) % WB_TOTAL;
  for (const [b, n] of WORKBEAT.w) { if (h < n) return b; h -= n; }
  return "main";
}
// the blocks a trade looks at: main = its own work (the oven, the block, the anvil, the ledger), second = its stores and shelves
// (prefixes of the block id without the namespace)
export const LOOK = {
  bakery: { main: ["furnace", "hearth_brick", "furn_trestle"], second: ["barrel", "furn_shelf", "chest", "furn_stool"] },
  butcher: { main: ["smoker", "furn_trestle"], second: ["barrel", "furn_shelf", "chest"] },
  smithy: { main: ["anvil", "blast_furnace"], second: ["grindstone", "hearth", "barrel", "furn_shelf"] },
  inn: { main: ["barrel"], second: ["furn_table", "hearth", "furn_shelf", "chest"] },
  town_hall: { main: ["lectern"], second: ["chest", "bell", "furn_shelf", "furn_cupboard"] },
  lumberyard: { main: ["stonecutter", "furn_trestle"], second: ["barrel"] },
  quarry: { main: ["chest"], second: ["barrel", "furn_stool"] },
  farm: { main: ["barrel"], second: ["furn_stool", "furn_coat_pegs"] },
  any: { main: ["chest", "barrel"], second: ["barrel", "chest", "furn_shelf", "furn_table"] },
};
/** PE1: the look-at cells of a trade among a template's blocks [[x, y, z, typeId], ...] (any frame) -> { main, second } */
export function lookCells(kind, blocks) {
  const L = LOOK[kind] || (String(kind).startsWith("farm_") ? LOOK.farm : LOOK.any);
  const out = { main: [], second: [] };
  for (const c of blocks || []) {
    const id = String(c[3] || "").replace(/^[a-z_]+:/, "");
    if (L.main.some((p) => id.startsWith(p))) out.main.push({ x: c[0], y: c[1], z: c[2] });
    else if (L.second.some((p) => id.startsWith(p))) out.second.push({ x: c[0], y: c[1], z: c[2] });
  }
  return out;
}
/** PE1: where a beat puts a worker and what he faces. sp = { station: {x,y,z} (feet, centred), main: [cells], second:
 *  [cells], store: cell | null, door: { in: {x,y,z}, out: {x,y,z} } | null } (cells = block coords, same frame).
 *  Returns { beat, stand: {x,y,z}, look: {x,y,z} | null } — never further than WORKBEAT.reach (+2 for the store) from the
 *  station on the same floor; a beat with nothing to do falls back to the main task */
export function workSpot(beat, sp, salt = 0) {
  const st = sp && sp.station;
  if (!st) return null;
  const cen = (c) => ({ x: c.x + 0.5, y: c.y, z: c.z + 0.5 });
  const d2 = (c) => Math.hypot(c.x + 0.5 - st.x, c.z + 0.5 - st.z);
  const floorOk = (c) => c.y >= st.y - 2 && c.y <= st.y + 2;
  const inReach = (list, r = WORKBEAT.reach) => (list || []).filter((c) => floorOk(c) && d2(c) <= r).sort((a, b) => d2(a) - d2(b));
  const mains = inReach(sp.main), seconds = inReach(sp.second), any = mains.concat(seconds);
  const beside = (c) => { const dx = st.x - (c.x + 0.5), dz = st.z - (c.z + 0.5), L = Math.hypot(dx, dz) || 1; return { x: Math.floor(c.x + 0.5 + dx / L) + 0.5, y: st.y, z: Math.floor(c.z + 0.5 + dz / L) + 0.5 }; };
  const main = () => ({ beat: "main", stand: { ...st }, look: any.length ? cen(any[0]) : null });
  if (beat === "near") return any.length > 1 ? { beat, stand: { ...st }, look: cen(any[1 + (salt % (any.length - 1))]) } : { ...main(), beat };
  if (beat === "second" && seconds.length) { const c = seconds[salt % seconds.length]; return { beat, stand: beside(c), look: cen(c) }; }
  if (beat === "store" && sp.store && inReach([sp.store], WORKBEAT.reach + 2).length) return { beat, stand: beside(sp.store), look: cen(sp.store) };
  if (beat === "door" && sp.door) return { beat, stand: { ...sp.door.in }, look: { ...sp.door.out } };
  return main();
}
/** the yaw (degrees) that turns a body at `from` to face `to` (the fisherman's formula) */
export function yawTo(from, to) { return Math.atan2(-(to.x - from.x), to.z - from.z) * 180 / Math.PI; }

// PE2 — the inn for the unhappy (MCA: +1 mood a 1,200 ticks inside the favoured building while sad): a body whose mood is
// below INN.mood picks the inn first at dusk and in idle hours; while there it gains a point every INN.per ticks, never above
// INN.cap. The inn holds INN.perStation people per station (the lowest moods first).
export const INN = { mood: 40, per: 1200, cap: 55, perStation: 3, stepMax: 400 };
export const wantsInn = (p) => !!p && (p.mood ?? 50) < INN.mood;
/** PE2: one stay of dt ticks at the inn: acc = ticks carried; returns { acc, gain } (gain added to mood by the caller) */
export function innStep(acc, dt, mood) {
  if ((mood ?? 50) >= INN.cap) return { acc: 0, gain: 0 };
  let a = (acc || 0) + Math.max(0, Math.min(INN.stepMax, dt || 0));
  let gain = Math.floor(a / INN.per);
  a -= gain * INN.per;
  gain = Math.min(gain, INN.cap - (mood ?? 50));
  return { acc: a, gain };
}

// INN24 (1.3.231, his 00:23 CT 10-07 ruling; his 02:43 witness: "We're closed — come back in the morning" from Sven the
// Innkeeper in full daylight). Mechanism: the shop window opened only while the world's time of day was inside a FIXED
// 1000..11000 window, while the keeper's own shift (the "late" template) runs 3000..13000 — 17:00..19:00 is daylight, the
// keeper stood at his station, and the window said closed. Now the inn keeps a ROTA over its own staff (the people whose
// job is the inn): one = a lone keeper 06..23; two = day 06..18 + night 18..06; three or more = day 06..14 (the keeper),
// night 22..06, evening 14..22, the rest serving staff 13..21. The cover shifts start on the hour (no id offset, so no
// handover gap), are never cut short by the walk home, and take no whole day off (8- and 12-hour days). The window is
// open while ANY staffer is on duty (innStatus); the inn's first INN24.cover stations are hired after the town's posts and
// before the shops (hireClasses; D-C1006-WATCH: priority classes kept, nearest within each). A body WITHOUT a home rests
// in the inn as a paying guest while it has beds free (innGuests; the night is billed purse -> the inn's till, lodgeBill).
export const INN24 = { cover: 3, bedP: 24,
  solo: "inn_solo", pair: ["inn_long_d", "inn_long_n"], rota: ["inn_day", "inn_night", "inn_eve"], extra: "inn_serve" };
const INN_TPLS = new Set(["inn_solo", "inn_long_d", "inn_long_n", "inn_day", "inn_eve", "inn_night", "inn_serve"]);
/** INN24: is `tpl` one of the inn's rota templates? */
export function isInnTpl(tpl) { return INN_TPLS.has(tpl); }
/** INN24: the inn's staff in census P on sim day `day` (alive, grown, job = the inn's id) */
export function innStaff(P, innId, day) {
  return (P && P.list ? P.list : []).filter((q) => q.alive && q.job === innId && (day === undefined || stage(q, day) !== "child"));
}
/** INN24: the rota of an inn's staff -> Map(pid -> template). The keeper first, then by id. */
export function innRota(staff) {
  const s = (staff || []).filter((q) => q && q.alive !== false).sort((a, b) => (b.keeper ? 1 : 0) - (a.keeper ? 1 : 0) || a.id - b.id);
  const m = new Map();
  if (s.length === 1) m.set(s[0].id, INN24.solo);
  else if (s.length === 2) { m.set(s[0].id, INN24.pair[0]); m.set(s[1].id, INN24.pair[1]); }
  else s.forEach((q, i) => m.set(q.id, i < INN24.rota.length ? INN24.rota[i] : INN24.extra));
  return m;
}
/** INN24: who of the staff is on duty at world time (tod, day) -> { on: [persons], rota, next: ticks until someone is
 *  (0 when open now; null: nobody ever) }. o = { seed } (the town's seed: the serving staff's day off). The walk home is
 *  not counted here: a staffer still in his W hours is at the counter. */
export function innStatus(staff, tod, day, o = {}) {
  const rota = innRota(staff);
  const list = [...rota.keys()].map((id) => staff.find((q) => q.id === id));
  const onAt = (t, d) => list.filter((q) => shiftAt(q, t, d, { tpl: rota.get(q.id), seed: o.seed || 0, keeper: !!q.keeper }).slot === "W");
  const on = onAt(tod, day);
  if (on.length) return { on, rota, next: 0 };
  for (let k = 50; k <= 48000 && list.length; k += 50) {
    const A = day * 24000 + tod + k, d = Math.floor(A / 24000);
    if (onAt(A - d * 24000, d).length) return { on, rota, next: k };
  }
  return { on, rota, next: null };
}
/** INN24: the split of the open jobs into hiring classes — the town's posts (string ids), the inn's COVER (up to
 *  INN24.cover staff at each inn, counting those already there), the shops (numeric ids). A cover entry is a share of its
 *  inn's own vacancies (x.base): taking it takes one of the inn's. */
export function hireClasses(openJobs, living) {
  const town = [], cover = [], shops = [];
  for (const j of openJobs || []) {
    if (typeof j.id !== "number") { town.push(j); continue; }
    shops.push(j);
    if (j.kind !== "inn") continue;
    const have = (living || []).filter((q) => q.alive && q.job === j.id).length;
    const k = Math.min(Math.max(0, INN24.cover - have), j.vacancies || 0);
    if (k > 0) cover.push({ ...j, vacancies: k, base: j });
  }
  return { town, cover, shops };
}
/** INN24: tonight's guests — the homeless living people (lowest ids first) for the inn's beds less its residents */
export function innGuests(list, beds, innId) {
  const L = (list || []).filter((q) => q.alive);
  const free = Math.max(0, (beds || 0) - L.filter((q) => q.home === innId).length);
  if (!free) return [];
  return L.filter((q) => !q.home).sort((a, b) => a.id - b.id).slice(0, free).map((q) => q.id);
}
/** INN24: the night's bill for n guests from a purse (pennies): { n, price, paid } — a short purse pays what it holds */
export function lodgeBill(n, purse, bed = INN24.bedP) {
  const price = Math.max(0, n) * bed;
  return { n: Math.max(0, n), price, paid: Math.max(0, Math.min(price, Math.floor(purse || 0))) };
}

// LEISURE (1.3.231, his 02:44 CT 10-07 screenshot at -168 68 125: four civs bunched on the square around the well in
// daylight). Mechanism (the clock, 1.3.230): leisureGoal offered the square's ring at EVERY hour as one of 2..4 equal
// options and a neighbourhood centre's WELL front; the rest slot sent every body without a home to the square (all night,
// and all day for the night watch). Now the idle places are weighted by kind, the square only at its hours (the midday
// market, dusk), never a well; a body without a home rests at the inn or a shelter (the clock's restGoal).
export const LEISURE = { phase: 2500, market: [5000, 7000],
  w: { home: 4, work: 1, shop: 3, centre: 3, park: 3, inn: 1, square: 0 },
  dusk: { inn: 3, square: 3 }, marketSquare: 2, homelessInn: 2 };
/** LEISURE: the weight of each kind of idle place now. f = { dusk, tod, housed } */
export function leisureWeights(f = {}) {
  const w = { ...LEISURE.w };
  if (!f.housed) { w.home = 0; w.inn += LEISURE.homelessInn; }
  if (f.dusk) { w.inn = Math.max(w.inn, LEISURE.dusk.inn); w.square = LEISURE.dusk.square; }
  else if (f.tod >= LEISURE.market[0] && f.tod < LEISURE.market[1]) w.square = LEISURE.marketSquare;
  return w;
}
/** LEISURE: one of the candidates [{ kind, at }] for person n in phase `phase`, weighted by w (deterministic); null when
 *  no candidate has weight */
export function leisurePick(cands, n, phase, w) {
  const C = (cands || []).filter((c) => (w[c.kind] || 0) > 0);
  if (!C.length) return null;
  const tot = C.reduce((a, c) => a + w[c.kind], 0);
  let h = hash32((Number(n) * 2654435761 + Math.imul(Number(phase) | 0, 40503)) >>> 0, 0x1E15) % tot;
  for (const c of C) { if (h < w[c.kind]) return c; h -= w[c.kind]; }
  return C[0];
}
/** LEISURE: a standing spot beside one of the park's four benches (layPark: benches beside the cross paths, the paths at
 *  x = cx and z = cz), k mod 4; null when the park is not laid */
export function parkSpot(park, k) {
  if (!park || !park.done || !park.box) return null;
  const [x0, x1, z0, z1] = park.box, cx = (x0 + x1) >> 1, cz = (z0 + z1) >> 1;
  const S = [[cx, cz - 3], [cx, cz + 3], [cx - 3, cz], [cx + 3, cz]];
  const [x, z] = S[((Number(k) % 4) + 4) % 4];
  return { x: x + 0.5, y: park.H + 1, z: z + 0.5 };
}

// BF7 — places: a jobless person takes the free job NEAREST his home, a person without a home the room nearest his work,
// a newcomer the room nearest an open job; a home over COMMUTE.far from work is left for a room within COMMUTE.near of it
// (one household a town a day, by id); a household with no home / an adult with no job, none free here for MOVE days, moves
// to another town that has room (the census's own migration: they leave this town and arrive in that one)
export const MOVE = { homeless: 3, jobless: 5, perDay: 1, far: 1 };
export const PLACES = { BEDS_BASE: false };          // off: a home holds HOUSEHOLD x DENSITY (beds are counted, not used yet)
const placeDist = (a, b) => (a && b && Number.isFinite(a.x) && Number.isFinite(b.x) ? Math.hypot(a.x - b.x, a.z - b.z) : Infinity);
/** BF7: the item of `list` nearest `at` that passes `ok` (unknown places last, list order breaks ties) */
export function nearestFree(list, at, ok = () => true) {
  let best = null, bd = Infinity, bi = Infinity;
  for (let i = 0; i < (list || []).length; i++) {
    const c = list[i];
    if (!ok(c)) continue;
    const d = placeDist(c, at);
    if (best === null || d < bd || (d === bd && i < bi)) { best = c; bd = d; bi = i; }
  }
  return best;
}
/** BF7: the beds of a template (two bed blocks = one bed) from its directional blocks [[x, y, z, typeId, states], ...] */
export function bedsOf(dir) { return Math.floor((dir || []).filter((e) => /(^|:)bed$/.test(String(e[3] || ""))).length / 2); }
/** BF7: the members of p's household who move with him: p, a spouse at the same home (or both homeless), their children there */
export function household(P, p, day) {
  const out = [p];
  const sp = p.spouse ? byId(P, p.spouse) : null;
  if (sp && sp.alive && sp.home === p.home) out.push(sp);
  for (const id of p.kids || []) { const k = byId(P, id); if (k && k.alive && k.home === p.home && stage(k, day) === "child" && !out.includes(k)) out.push(k); }
  return out;
}
/** BF7: the newcomers of a move arrive in census P (another town's): new ids, the same names, sexes, births, trades and
 *  skills; spouse / parents / kids links kept among the movers; homed at `home` (job none: they take the nearest free one
 *  on that town's next census day). Returns the new people. */
export function adopt(P, movers, day, home) {
  const map = new Map();
  const out = [];
  for (const q of movers) {
    const p = newPerson(P, day, { home, name: q.name, sex: q.sex, age: day - q.born, trade: q.trade ?? null, seed: q.id });
    if (q.skill) p.skill = { ...q.skill };
    p.mood = Math.max(45, q.mood ?? 55);
    map.set(q.id, p);
    out.push(p);
  }
  for (const q of movers) {
    const p = map.get(q.id);
    if (q.spouse && map.has(q.spouse)) p.spouse = map.get(q.spouse).id;
    p.parents = (q.parents || []).filter((id) => map.has(id)).map((id) => map.get(id).id);
    p.kids = (q.kids || []).filter((id) => map.has(id)).map((id) => map.get(id).id);
  }
  for (const p of out) for (const r of out) if (r !== p && (r.spouse === p.id || p.kids.includes(r.id) || p.parents.includes(r.id))) p.friends[r.id] = 60;   // the household stays close
  // 1.3.230 (HD): LINES among the movers — a line whose founder moved keeps him; a line left behind is founded anew by the
  // eldest moving man of it (the father, else a parent); a lone mover founds his own (no field)
  const mv = new Map(movers.map((q) => [q.id, q]));
  const lineIn = (q, depth = 0) => {
    const d = dynOf(q);
    if (map.has(d)) return map.get(d).id;
    const par = (q.parents || []).map((id) => mv.get(id)).filter(Boolean);
    const fa = par.find((x) => x.sex === "m") || par[0];
    return fa && depth < 8 ? lineIn(fa, depth + 1) : map.get(q.id).id;
  };
  for (const q of movers) { const p = map.get(q.id), l = lineIn(q); if (l !== p.id) p.dyn = l; }
  return out;
}

// ------------------------------------------------------------------------------------------------ HD (1.3.230): HOUSEHOLDS & DYNASTY
// His 2026-10-06 21:39: "Children moving out of their parents' home when they grow up, which makes them an adult — and no
// longer linked to their parents, except through dynasty. This lets them sell old homes after their parents pass, and
// upgrade to better homes when they move out, which should naturally update the cities. Once an adult, a child-turned-adult
// can now have children." 21:47: "When someone moves out of a home AND/OR into a home, the home must be restored from its
// current weathered state to fresh; this makes jobs, spends money and keeps cities updated. And selling of homes
// replenishes those costs."
// MONEY (fitted to pw_civ_economy: one citizens' PURSE, the town's TREASURY, pennies; nothing is created or destroyed):
//   a SALE (an heir sells an inherited / left house): the town pays price x sellShare, treasury -> purse (the heir's
//   household is a part of the purse; the chronicle names the heir) — a short treasury pays what it holds (no debt);
//   a PURCHASE (a household moving out takes a free home): price x buyShare, purse -> treasury — this is what replenishes
//   the restorations (a level's price covers its worst restoration); a short purse pays what it holds;
//   a RESTORATION (every home moved out of / into, deduped, at most queueMax waiting): materials from the stock and the
//   builders' wages treasury -> purse (ECON.pay's law) when the town can pay; else it waits (an empty treasury waits; no
//   debt); the work takes freshDays + the weathering band days, then the clock places the fresh blocks (EN2's _r).
// PER PERSON: p.dyn only on the town-born (the founder's id, ~10 chars); founders and newcomers are their own line (no field);
// P.lines { founder id: name } only for lines with a town-born member (pruned when none lives).
export const HOUSING = {
  moveOutPerDay: 3,                            // households leaving the family home a town a day (crowded homes first, then the eldest)
  price: [0, 1440, 2880, 4320, 8640, 17280],   // pennies by house level 0..5 (1 cottage 120 coins … 5 palace 1,440 coins)
  sellShare: 1,                                // the share of the price the town pays a selling heir
  buyShare: 1,                                 // the share a household pays the town for a free home (0 = free homes)
  affordDays: 20,                              // a household affords a level when its earners' daily wages x affordDays >= the price
  wage: 72,                                    // an earner's daily wage when the clock does not tell (ctx.wageOf): a labourer's
  minLevel: 1,                                 // the lowest level is open to every household (a jobless adult too)
  restore: { perDay: 2, queueMax: 64, wage: 120, freshDays: 1, perBand: { stone: 12, planks: 4 } },   // wage = ECON.WAGE.builder
};
/** the price (pennies) of a house level */
export function priceOf(lvl) { const P = HOUSING.price; return P[Math.max(0, Math.min(P.length - 1, Math.floor(lvl || 0)))]; }
/** a person's line: p.dyn (town-born) else his own id (a founder, a newcomer) */
export const dynOf = (p) => (p ? p.dyn ?? p.id : null);
/** a child's line: the father's, else the mother's */
export function birthLine(mother, father) { return father ? dynOf(father) : dynOf(mother); }
/** the name of p's line (the register, else the founder's record, else p's own name) */
export function lineName(P, p) { const d = dynOf(p); return (P.lines && P.lines[d]) || (byId(P, d) || {}).name || p.name; }
/** the best house level a household affords with `means` pennies of daily wages (never below HOUSING.minLevel) */
export function affordLevel(means = 0) {
  let lv = HOUSING.minLevel;
  for (let k = HOUSING.minLevel + 1; k < HOUSING.price.length; k++) if ((means || 0) * HOUSING.affordDays >= HOUSING.price[k]) lv = k;
  return lv;
}
/** the bill of restoring a house of `level` at weathering `band` (0..3; EN2's b.wx) to fresh: stone for the weathered
 *  stone (band x level), planks for the fresh-up, builder-days freshDays + band at the builder's wage */
export function restoreBill(level = 1, band = 0) {
  const R = HOUSING.restore, lv = Math.max(1, Math.min(5, Math.floor(level || 1))), b = Math.max(0, Math.min(3, Math.floor(band || 0)));
  const mats = {};
  if (b > 0) mats.stone = R.perBand.stone * b * lv;
  mats.planks = R.perBand.planks * (1 + b) * lv;
  const days = R.freshDays + b;
  return { mats, days, wages: days * R.wage, blocks: Object.values(mats).reduce((a, n) => a + n, 0) };
}
/** queue homes (numeric ids) for restoration: deduped, at most HOUSING.restore.queueMax waiting; returns the count added */
export function queueRestore(Q, ids = []) {
  let n = 0;
  for (const id of ids || []) {
    if (typeof id !== "number" || !Number.isFinite(id)) continue;
    if (Q.length >= HOUSING.restore.queueMax) break;
    if (Q.some((e) => e.h === id)) continue;
    Q.push({ h: id }); n++;
  }
  return n;
}
const canPayBill = (L, bill) => L.treasury >= bill.wages && Object.entries(bill.mats).every(([m, k]) => (L.stock[m] || 0) >= k);
/** one day of the restoration queue Q [{h, l?}] (l = work days left once paid). o = { lvl(h), band(h), ok(h) (still a
 *  home) }. Starts at most HOUSING.restore.perDay bills the ledger can pay (stock down, wages treasury -> purse), works
 *  every started one a day, returns { started, done (home ids), waiting, dropped, spent } */
export function restoreDay(L, Q, o = {}) {
  const out = { started: [], done: [], waiting: 0, dropped: 0, spent: 0 };
  if (!Array.isArray(Q)) return out;
  let n = 0;
  for (let i = 0; i < Q.length; i++) {
    const e = Q[i];
    if (o.ok && !o.ok(e.h)) { Q.splice(i--, 1); out.dropped++; continue; }
    if (e.l === undefined) {
      if (n >= HOUSING.restore.perDay) { out.waiting++; continue; }
      const bill = restoreBill(o.lvl ? o.lvl(e.h) : 1, o.band ? o.band(e.h) : 0);
      if (!L || !canPayBill(L, bill)) { out.waiting++; continue; }
      for (const [m, k] of Object.entries(bill.mats)) L.stock[m] -= k;
      L.treasury -= bill.wages; L.purse += bill.wages; L.wagesPaid = (L.wagesPaid || 0) + bill.wages;
      e.l = bill.days; n++;
      out.started.push({ h: e.h, wages: bill.wages, mats: bill.mats, days: bill.days }); out.spent += bill.wages;
    }
    e.l--;
    if (e.l <= 0) { out.done.push(e.h); Q.splice(i--, 1); }
  }
  return out;
}
/** settle the day's deeds with the ledger: 'sell' treasury -> purse, 'buy' purse -> treasury, each capped at what the
 *  payer holds (no debt); records d.paid. No ledger yet: nothing moves (paid 0). */
export function settleDeeds(L, deeds = []) {
  for (const d of deeds || []) {
    let paid = 0;
    if (L && d.price > 0) {
      if (d.kind === "sell") { paid = Math.min(Math.max(0, L.treasury), d.price); L.treasury -= paid; L.purse += paid; }
      else if (d.kind === "buy") { paid = Math.min(Math.max(0, L.purse), d.price); L.purse -= paid; L.treasury += paid; }
    }
    d.paid = paid;
  }
  return deeds;
}

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
  HOME_FAR: "home more than 160 blocks from work (PE5: a complaint; BF7 moves the household when a room near work is free)",
  SHELTER: "sheltering from the rain (quarrymen, woodcutters, builders keep half their output)",
  UNPAID: "not paid (reserved: WP1)",
  ALARM: "the alarm bell rang: indoors until it stops (B10)",
  "—": "idle, reason unknown",
};
/** f = { child, asleep, phase: "work" | "off", noStock, siteWaits: <good> | null, walk: code | null, worker: code | null,
 *  busy, wet, builderIdle, homeFar, shelter (B4) } */
export function whyOf(person, f = {}) {
  if (!person) return "—";
  if (f.child) return "CHILD";
  if (!person.home) return "NO_HOME";
  if (f.asleep) return "ASLEEP_CHUNK";
  if (f.alarm) return "ALARM";                                             // B10 (WP4): the bell
  if (f.phase !== "work") return "OFF_SHIFT";
  if (f.noStock) return "NO_STOCK";
  if (f.siteWaits) return `SITE_WAITS:${f.siteWaits}`;
  if (f.walk) return f.walk;
  if (f.worker) return f.worker;
  if (f.homeFar) return "HOME_FAR";                                        // B4 (PE5): the complaint, over the plain WORKING
  if (f.shelter) return "SHELTER";                                         // B4 (rain ruling)
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

// 1.3.232 #3 (his 10-07 report: the bell "everyone indoors" by day, shops always closed): which monsters ring the bell.
// IN TOWN = inside the border box AND within ALARM.dy of the square's height (cave mobs below the streets never count).
// By day only those within ALARM.dayNear of the square count (a witch walking past the edge is no alarm). The bell rings
// at >= ALARM.seen; `calm` (none counted) clears a bell the monsters rang.
export const ALARM = { seen: 3, dy: 12, dayNear: 24 };
/** mons: [{x,y,z}], town: {cx,cy,cz,r}, tod: world time of day -> { n, ring, calm } */
export function alarmThreat(mons, town, tod) {
  const day = tod < 12500 || tod >= 23500;
  let n = 0;
  for (const e of mons || []) {
    const dx = Math.abs(e.x - town.cx), dz = Math.abs(e.z - town.cz);
    if (dx > town.r || dz > town.r || Math.abs(e.y - town.cy) > ALARM.dy) continue;
    if (day && Math.hypot(dx, dz) > ALARM.dayNear) continue;
    n++;
  }
  return { n, ring: n >= ALARM.seen, calm: n === 0 };
}
/** 1.3.232 #3: the shift week's day. world.getDay() stops turning when /time set rewinds the absolute time (his CIV-SHIFT
 *  "day":0 at sim day 137), so count the days: +k when the world day rises by k, +1 when the time of day goes back
 *  without it (a /time set). c: { g, t, n } or null (n starts at the world day) -> the new c */
export function dayCount(c, g, t) {
  if (!c) return { g, t, n: g };
  let n = c.n;
  if (g > c.g) n += g - c.g; else if (t < c.t) n += 1;
  return { g, t, n };
}
