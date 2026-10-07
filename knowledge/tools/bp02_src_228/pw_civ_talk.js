// pw_civ_talk.js — CIVITAS B5 VOICE, the PURE half (no engine imports: node-tested in tests/test_talk.mjs).
// Program 228 (FIT-MATRIX BF12 + PE9 + PE10 + PE11 + BF11), fitted to OUR census: every line is chosen from facts the
// census and the ledger already hold (mood, homeless / jobless days, the town's hungry days, wages in arrears, the why-idle
// code, rumours, temperament) — nothing random: a choice that has to break a tie uses hash32(person, entry, day).
//   * SPEECH (BF12 + PE9): a line shows over the speaker's head for min(360, 40 + 1.5 x chars) ticks.
//   * DIALOGUE (PE10): a table of entries {id, pri, when(f), lines[], once?}; the highest priority whose condition holds
//     wins (petition 100 > needs 50..25 > first meeting 10 > news 5 > mood 3 > small talk 1). `once: "day"` entries are
//     remembered in p.mem (at most MEM.cap keys, each with an expiry day) so a person does not repeat himself.
//   * PETITIONS (BF11): urgencyOf(p, f) = homeless days x3 + the town's hungry days x2 + jobless days + a site waiting on
//     his trade x2 + wages in arrears x2 (job holders). >= PETITION.threshold makes a petitioner; the max wins.
//     The player's "I'll see to it" opens a petition thread; on its deadline the census checks the NEED itself (petitionCheck).
//   * OVERHEARD (BF12): at dusk, two friends (the most fond pair within OVERHEARD.pairDist) talk where a player can hear:
//     a 2-4 line script chosen by the town's situation.
// Ruling filters (his 10:15 / 12:20): no raids, no violence, no sickness, no random negative events — the lines only REPORT
// what the census holds; nothing here changes a mood except the petition's outcome (the player's own promise).
import { hash32, petitionNeedMet } from "./pw_civ_people.js";

export const SPEECH = { base: 40, perChar: 1.5, max: 360, wrap: 30 };
export const MEM = { cap: 4 };
export const PETITION = { threshold: 6, cooldownDays: 2, radius: 30, every: 200, playerCooldown: 2400, deadlineDays: 5, reach: 3, walkTimeout: 400,
                          fondKept: 10, fondBroken: 5, moodKept: 5 };
export const OVERHEARD = { every: 400, radius: 16, pairDist: 5, pairCooldown: 18000, minFond: 20 };

/** PE9: how long a line stays up (ticks) */
export function speechTicks(text) { return Math.min(SPEECH.max, Math.round(SPEECH.base + SPEECH.perChar * String(text || "").length)); }

/** a bubble's lines: the text wrapped at SPEECH.wrap characters on word boundaries */
export function wrap(text, width = SPEECH.wrap) {
  const out = [];
  let line = "";
  for (const w of String(text).split(/\s+/).filter(Boolean)) {
    if (line && (line.length + 1 + w.length) > width) { out.push(line); line = w; } else line = line ? `${line} ${w}` : w;
  }
  if (line) out.push(line);
  return out;
}

export function moodBand(mood = 50) { return mood >= 75 ? "content" : mood >= 50 ? "fair" : mood >= 30 ? "low" : "miserable"; }

/** template fill: {key} -> f[key]; {s:key} -> "" or "s" by f[key] === 1 */
export function fill(tpl, f) {
  return String(tpl).replace(/\{s:(\w+)\}/g, (_, k) => (f[k] === 1 ? "" : "s")).replace(/\{(\w+)\}/g, (_, k) => (f[k] === undefined || f[k] === null ? "" : String(f[k])));
}

/** the facts a line may use. c = { day, town, trade, why, hd (town hungry days), arrears, rumour, wet, tier, petition,
 *  temper, recentBuilt } — the caller reads them from the census / ledger / the why pass */
export function factsOf(p, c = {}) {
  return {
    name: p.name, town: c.town || "the town", trade: c.trade || null, band: moodBand(p.mood ?? 50), mood: p.mood ?? 50,
    hl: p.hl || 0, jl: p.jl || 0, hd: c.hd || 0, arrears: c.arrears || 0, job: !!p.job, why: c.why || "—",
    good: c.why && c.why.startsWith("SITE_WAITS:") ? c.why.slice(11) : null, grief: p.grief || 0,
    rumour: c.rumour || null, wet: !!c.wet, tier: c.tier || "stranger", met: (p.playerFond || 0) > 0,
    petition: c.petition || null, temper: c.temper || "steady", recentBuilt: c.recentBuilt || null, child: !!c.child,
  };
}

// --------------------------------------------------------------------------------------------- PE10: the dialogue table
const SMALL = {
  cheerful: ["A fine day to be in {town}!", "Mind the puddles — and good day to you!"],
  dour: ["Hm.", "Another day."],
  talkative: ["Have you seen the new roofs going up? Lovely work, lovely.", "I could talk all day — but the day won't wait."],
  shy: ["Oh — hello.", "...good day."],
  proud: ["{town} grows finer every season.", "You won't find better work than ours."],
  worrier: ["I do hope the stores hold.", "Have you checked the weather? I always check."],
  steady: ["Good day.", "Busy, busy."],
  curious: ["Where do you hail from?", "Have you been to the square today?"],
};
const FIRST = {
  cheerful: "Welcome to {town}! I'm {name}{tradeAs}.", dour: "{name}{tradeAs}. What is it?", talkative: "A new face! I'm {name}{tradeAs} — ask me anything about {town}.",
  shy: "Oh — I'm {name}.", proud: "{name}{tradeAs}, of {town}.", worrier: "Hello — I'm {name}. Is everything all right?",
  steady: "Good day. I'm {name}{tradeAs}.", curious: "Hello there — I'm {name}. Who might you be?",
};
export const DIALOGUE = [
  { id: "petition", pri: 100, when: (f) => !!f.petition, lines: ["{petition}"] },
  { id: "homeless", pri: 50, when: (f) => f.hl > 0 && !f.child, lines: ["I've had no roof for {hl} day{s:hl}. Is there no room in {town}?", "No bed for me these {hl} day{s:hl}."] },
  { id: "hungry", pri: 45, when: (f) => f.hd > 0, lines: ["The larders are thin — {hd} hungry day{s:hd} now.", "We eat little in {town} these days."] },
  { id: "unpaid", pri: 40, when: (f) => f.arrears > 0 && f.job, lines: ["The town owes us {arrears} day{s:arrears} of wages.", "No pay again. How long can it go on?"] },
  { id: "jobless", pri: 35, when: (f) => f.jl > 0 && !f.child, lines: ["No work for me in {town} these {jl} day{s:jl}.", "I'd take any honest work."] },
  { id: "waits", pri: 30, when: (f) => !!f.good, lines: ["The builders stand idle — no {good} to be had.", "We wait on {good} before we can build."] },
  { id: "grief", pri: 28, when: (f) => f.grief > 0, lines: ["Forgive me — we buried someone dear.", "It's been a hard season for my family."] },
  { id: "rain", pri: 25, when: (f) => f.wet, lines: ["Foul weather. We keep half a day's work in this.", "Rain again — the quarry floods in this."] },
  { id: "first", pri: 10, when: (f) => !f.met, lines: null, once: "ever" },
  { id: "built", pri: 6, when: (f) => !!f.recentBuilt, lines: ["Have you seen the new {recentBuilt}?", "They finished the {recentBuilt} — fine work."], once: "day" },
  { id: "news", pri: 5, when: (f) => !!f.rumour && f.tier !== "stranger", lines: ["Have you heard? {rumour}", "They say {rumour}"], once: "day" },
  { id: "content", pri: 3, when: (f) => f.band === "content", lines: ["Fine days in {town}.", "I've no complaints — none at all."] },
  { id: "low", pri: 3, when: (f) => f.band === "low" || f.band === "miserable", lines: ["Not the best of times.", "I've known better days."] },
  { id: "small", pri: 1, when: () => true, lines: null },
];

/** PE10 memory keys: p.mem = {key: expiryDay}; at most MEM.cap kept (the soonest to expire goes first) */
export function remember(p, key, untilDay) {
  const m = (p.mem = p.mem || {});
  m[key] = untilDay;
  const others = Object.keys(m).filter((k) => k !== key).sort((a, b) => m[a] - m[b] || (a < b ? -1 : 1));
  while (others.length + 1 > MEM.cap) delete m[others.shift()];
}
export function recalls(p, key, day) { return !!(p.mem && p.mem[key] !== undefined && p.mem[key] >= day); }
export function pruneMem(p, day) {
  if (!p.mem) return;
  for (const [k, d] of Object.entries(p.mem)) if (d < day) delete p.mem[k];
  if (!Object.keys(p.mem).length) delete p.mem;
}

/** the line a person says to the player now: { id, text } (deterministic) */
export function pickLine(p, f, day) {
  let best = null;
  for (const e of DIALOGUE) {
    if (!e.when(f)) continue;
    if (e.once === "day" && recalls(p, `d:${e.id}`, day)) continue;
    if (e.once === "ever" && recalls(p, `e:${e.id}`, day)) continue;
    if (!best || e.pri > best.pri) best = e;
  }
  if (!best) return null;
  let tpl;
  if (best.id === "first") tpl = FIRST[f.temper] || FIRST.steady;
  else if (best.id === "small") { const l = SMALL[f.temper] || SMALL.steady; tpl = l[hash32(p.id, day * 31 + 7) % l.length]; }
  else tpl = best.lines[hash32(p.id, day * 31 + best.pri) % best.lines.length];
  return { id: best.id, text: fill(tpl, { ...f, tradeAs: f.trade ? `, the ${f.trade}` : "" }) };
}
/** after a line is said: the once-entries are remembered */
export function noteSaid(p, id, day) {
  const e = DIALOGUE.find((x) => x.id === id);
  if (!e || !e.once) return;
  remember(p, e.once === "day" ? `d:${id}` : `e:${id}`, e.once === "day" ? day : day + 100000);
}

// --------------------------------------------------------------------------------------------- BF11: petitions
/** f = factsOf(...) plus siteWaitsMine (a site waits on this person's own trade) */
export function urgencyOf(f) {
  if (f.child) return 0;
  return f.hl * 3 + f.hd * 2 + f.jl + (f.siteWaitsMine ? 2 : 0) + (f.job ? f.arrears * 2 : 0);
}
/** the need behind a petition: the largest term of the urgency */
export function needOf(f) {
  const terms = [["home", f.hl * 3], ["food", f.hd * 2], ["job", f.jl], ["wages", f.job ? f.arrears * 2 : 0], ["site", f.siteWaitsMine ? 2 : 0]];
  terms.sort((a, b) => b[1] - a[1]);
  return terms[0][1] > 0 ? terms[0][0] : null;
}
const PLEA = {
  home: "Please — I've slept without a roof for {hl} day{s:hl}. Can {town} find me a bed?",
  food: "{town} has gone hungry {hd} day{s:hd}. Can anything be done about the larders?",
  job: "I've had no work for {jl} day{s:jl}. Is there a trade for me?",
  wages: "We've worked {arrears} day{s:arrears} without pay. Will the council pay us?",
  site: "Our site waits on {good}. Could you bring some to {town}?",
};
export function pleaOf(f) { const n = needOf(f); return n ? fill(PLEA[n], f) : null; }
/** cands = [{ p, f, d (distance to the player) }]; the max urgency >= threshold whose cooldown (p.pet, a day) has passed;
 *  ties by distance, then id */
export function pickPetitioner(cands, day) {
  let best = null, bu = -1;
  for (const c of cands) {
    if (c.p.pet !== undefined && day - c.p.pet < PETITION.cooldownDays) continue;
    const u = urgencyOf(c.f);
    if (u < PETITION.threshold) continue;
    if (u > bu || (u === bu && (c.d < best.d || (c.d === best.d && c.p.id < best.p.id)))) { best = c; bu = u; }
  }
  return best ? { ...best, urgency: bu, need: needOf(best.f), plea: pleaOf(best.f) } : null;
}
/** a petition thread's outcome on its deadline: was the NEED met? (the census decides with the same function) */
export const petitionMet = petitionNeedMet;

// --------------------------------------------------------------------------------------------- BF12: overheard talk
/** bodies = [{ vid, pid, x, z }]; fond(pidA, pidB) -> 0..100; last = Map("a-b" -> tick). The most fond pair within
 *  pairDist whose cooldown passed (fondness >= minFond); ties by the smaller pair key. */
export function pickPair(bodies, fond, last, now) {
  let best = null;
  for (let i = 0; i < bodies.length; i++) {
    for (let j = i + 1; j < bodies.length; j++) {
      const a = bodies[i], b = bodies[j];
      if (a.pid === b.pid || Math.hypot(a.x - b.x, a.z - b.z) > OVERHEARD.pairDist) continue;
      const lo = Math.min(a.pid, b.pid), hi = Math.max(a.pid, b.pid), key = `${lo}-${hi}`;
      const t = last && last.get(key);
      if (t !== undefined && now - t < OVERHEARD.pairCooldown) continue;
      const f = fond(a.pid, b.pid);
      if (f < OVERHEARD.minFond) continue;
      if (!best || f > best.f || (f === best.f && key < best.key)) best = { a: a.pid < b.pid ? a : b, b: a.pid < b.pid ? b : a, f, key };
    }
  }
  return best;
}
const SCRIPTS = {
  hungry: [[0, "Did you get bread today?"], [1, "Half a loaf. The baker's short again."], [0, "{hd} day{s:hd} of this..."]],
  homeless: [[0, "Someone slept by the well again last night."], [1, "There's no room left — they need more houses."]],
  unpaid: [[0, "Paid yet?"], [1, "Not a coin. The treasury's empty, they say."], [0, "Then the sites will stop."]],
  rain: [[0, "Wet through."], [1, "The quarrymen came home early."], [0, "Half a day's work lost."]],
  built: [[0, "Have you seen the new {recentBuilt}?"], [1, "Fine work. The masons earned their pay."]],
  news: [[0, "Did you hear?"], [1, "Hear what?"], [0, "{rumour}"], [1, "Well I never."]],
  content: [[0, "Lovely evening."], [1, "It is. {town} is doing well."]],
  low: [[0, "Long day."], [1, "They all are, lately."]],
};
/** the script two friends play: [{ who: 0 | 1, text, delay (ticks after the start) }] */
export function scriptFor(f) {
  const key = f.hd > 0 ? "hungry" : f.hl > 0 ? "homeless" : f.arrears > 0 ? "unpaid" : f.wet ? "rain" : f.recentBuilt ? "built"
    : f.rumour ? "news" : f.band === "low" || f.band === "miserable" ? "low" : "content";
  let t = 0;
  return { key, lines: SCRIPTS[key].map(([who, tpl]) => { const text = fill(tpl, f); const at = t; t += speechTicks(text) - 20; return { who, text, delay: at }; }) };
}
