// test_needs.mjs — 1.3.228 (B3 / PEOPLE I): census law, pure.
// BF4 needs pressure (whole points), escalation at 7 / 14 days, neutral factors leave the average, mood tiers -> output with
// the 0.70 floor (Q2) and the strike flag; Q4 sanitation no longer kills; PE3 grief by closeness; PE6 births by food,
// happiness and fullness; PE12 rumours (participants only, heard = tellings, cap 10, tellPerDay, interest first); PE4 + PE7
// house-level rank gate, the skill curve, the daily cap and the repetition penalty, diet variety; PE8 temperament and
// interest from the id; the save budget of a synthetic 600-person census (B3 fields within +10 %).
import { readFileSync } from "node:fs";
import * as PEOPLE from "../pw_civ_people.js";
import * as OLD from "./fixtures/pw_civ_people_b2.js";
import * as ECON from "../pw_civ_economy.js";
let pass = 0, fail = 0;
const ok = (c, m, extra) => { if (c) pass++; else { fail++; console.log("FAIL", m, extra === undefined ? "" : JSON.stringify(extra)); } };
const near = (a, b, e = 1e-9) => Math.abs(a - b) <= e;
const clone = (o) => JSON.parse(JSON.stringify(o));
const { NEEDS, OUTPUT, GRIEF, BIRTH, RUMOUR, SKILL, FLAGS } = PEOPLE;

/** a small town: n adults in homes of 2, jobs at shop 100..103 (every fifth jobless), all at mood 55 */
function town(n = 20, opts = {}) {
  const P = PEOPLE.newPeople();
  for (let i = 0; i < n; i++) PEOPLE.newPerson(P, 100, { home: opts.homeless ? null : 1 + (i >> 1), job: i % 5 === 4 ? null : 100 + (i % 4), trade: "bakery", seed: i, age: 25 + (i % 30), sex: opts.sex });
  return P;
}
const homesOf = (n, room = 1) => Array.from({ length: n }, (_, k) => ({ id: k + 1, room }));
const jobsOf = (vac = 0) => [100, 101, 102, 103].map((id) => ({ id, kind: "bakery", vacancies: vac }));
function ctx(day, o = {}) {
  const homes = o.homes || homesOf(10, 0);
  return { day, fed: o.fed ?? 1, paid: o.paid ?? true, homes, jobs: o.jobs || jobsOf(0), seed: o.seed ?? 7, sanitation: o.san ?? 1,
           levels: o.levels || new Map(homes.map((h) => [h.id, o.lvl ?? 1])), foodDays: o.foodDays ?? 0, diet: o.diet, acts: o.acts, health: o.health };
}
const meanOf = (P) => PEOPLE.meanMood(P);

// ------------------------------------------------------------------------------------------------ 1. pressure -> mood steps
{
  const seq = (pr, n) => { let c = 0; const out = []; for (let i = 0; i < n; i++) { const [w, r] = PEOPLE.carry(c, pr); out.push(w); c = r; } return out; };
  ok(JSON.stringify(seq(-1.5, 4)) === "[-1,-2,-1,-2]", "hungry -1.5 a day moves mood -1, -2, -1, -2 (whole points, fraction carried)", seq(-1.5, 4));
  ok(JSON.stringify(seq(0.5, 4)) === "[0,1,0,1]", "well fed +0.5 a day: no move until a whole point", seq(0.5, 4));
  ok(JSON.stringify(seq(-5, 2)) === "[-5,-5]", "starving -5 a day");
  ok(PEOPLE.hungerPressure(1, 10) === NEEDS.hunger.well && PEOPLE.hungerPressure(1, 2) === 0 && PEOPLE.hungerPressure(0.8) === NEEDS.hunger.hungry
     && PEOPLE.hungerPressure(0.5) === NEEDS.hunger.famished && PEOPLE.hungerPressure(0.3) === NEEDS.hunger.starving, "hunger bands");
  ok(PEOPLE.fatiguePressure(2, 0) === 0 && PEOPLE.fatiguePressure(2, 2) === -1 && PEOPLE.fatiguePressure(1, 9) === -NEEDS.fatigue.rate * NEEDS.fatigue.loadMax && PEOPLE.fatiguePressure(0, 3) === 0,
     "fatigue: staffed 0, half-staffed -1, capped at -loadMax, nobody 0");
  // through dayStep: two identical towns, one well fed (+0.5) and one adequately fed (0): equal on day 1, +1 exactly on day 2
  const A = town(), B = clone(A);
  PEOPLE.dayStep(A, ctx(100, { foodDays: 0 })); PEOPLE.dayStep(B, ctx(100, { foodDays: 10 }));
  ok(A.list.every((p, i) => p.mood === B.list[i].mood), "day 1: the +0.5 carry has not reached a whole point (moods equal)");
  ok(B.need && B.need.h === 0.5 && (!A.need || A.need.h === undefined), "the carried fraction is the town's (P.need.h)", B.need);
  PEOPLE.dayStep(A, ctx(101, { foodDays: 0 })); PEOPLE.dayStep(B, ctx(101, { foodDays: 10 }));
  ok(A.list.every((p, i) => B.list[i].mood - p.mood === 1), "day 2: every mood exactly +1 (one whole point)", A.list.map((p, i) => B.list[i].mood - p.mood));
  ok(!B.need || B.need.h === undefined, "the carry is spent (0 is not saved)");
  // fatigue: an understaffed workplace's holders lose whole points; a fully staffed one carries nothing
  const F = town(), G = clone(F);
  const held = F.list.filter((p) => p.job !== null).map((p) => p.id);         // the same holders in both towns
  for (let d = 0; d < 4; d++) { PEOPLE.dayStep(F, ctx(100 + d)); PEOPLE.dayStep(G, ctx(100 + d, { jobs: jobsOf(4) })); }
  const mOf = (T) => held.reduce((a, id) => a + T.list.find((q) => q.id === id).mood, 0) / held.length;
  ok(mOf(G) < mOf(F), "understaffed holders are moodier than in a staffed town (4 days)", [mOf(F), mOf(G)]);
  ok(G.need && G.need.f && Object.keys(G.need.f).length <= 4 && !(F.need && F.need.f), "fatigue drift only for understaffed workplaces", G.need);
}

// ------------------------------------------------------------------------------------------------ 2. escalation at 7 / 14 days
{
  ok(PEOPLE.escalation(0) === 1 && PEOPLE.escalation(6) === 1 && PEOPLE.escalation(7) === 0.75 && PEOPLE.escalation(13) === 0.75 && PEOPLE.escalation(14) === 0.5 && PEOPLE.escalation(40) === 0.5, "x0.75 from day 7, x0.5 from day 14");
  const p = { id: 1, born: 70, home: null, job: null, friends: {}, kids: [], parents: [], mood: 50 };
  ok(near(PEOPLE.moodParts(p, { day: 100, fed: 0.5, hd: 1 }).food, 0.2) && near(PEOPLE.moodParts(p, { day: 100, fed: 0.5, hd: 7 }).food, 0.15) && near(PEOPLE.moodParts(p, { day: 100, fed: 0.5, hd: 14 }).food, 0.1), "the hungry food factor escalates 0.2 -> 0.15 -> 0.1");
  ok(near(PEOPLE.moodParts({ ...p, hl: 7 }, { day: 100 }).home, 0.15) && near(PEOPLE.moodParts({ ...p, jl: 14 }, { day: 100 }).job, 0.25), "homeless and jobless escalate too");
  ok(PEOPLE.moodParts({ ...p, home: 3 }, { day: 100, fed: 1, hd: 20 }).food === NEEDS.food.full, "a met need does not escalate");
  const T = town(); const at = {};
  for (let d = 1; d <= 14; d++) { PEOPLE.dayStep(T, ctx(99 + d, { fed: 0.5 })); if (d === 1 || d === 7 || d === 14) at[d] = meanOf(T); }
  ok(at[14] < at[7] && at[7] < at[1], "fed 0.5 for 14 days: mood day 14 < day 7 < day 1", at);
  ok(T.need.hd === 14, "the town counted 14 hungry days", T.need);
  PEOPLE.dayStep(T, ctx(114, { fed: 1 }));
  ok(!T.need || T.need.hd === undefined, "fed again: the counter goes (not saved at 0)");
  // the homeless counter: stored only while > 0
  const H = town(4, { homeless: true });
  for (let d = 0; d < 8; d++) PEOPLE.dayStep(H, ctx(100 + d, { homes: [] }));
  ok(H.list.every((q) => q.hl === 8), "homeless 8 days: p.hl = 8", H.list.map((q) => q.hl));
  PEOPLE.dayStep(H, ctx(108, { homes: [{ id: 50, room: 9 }] }));
  ok(H.list.every((q) => q.home === 50 && q.hl === undefined), "housed: hl removed");
}

// ------------------------------------------------------------------------------------------------ 3. neutral factors leave the average
{
  ok(near(PEOPLE.moodTarget({ food: 1.8 }), 90), "one factor 1.8 -> 90");
  ok(near(PEOPLE.moodTarget({ food: 1.8, home: 1, job: 1, diet: 1 }), 90), "neutral factors do not pull the average");
  ok(PEOPLE.moodTarget({ food: 1, home: 1 }) === 50, "all neutral -> 50");
  ok(near(PEOPLE.moodTarget({ food: 1.8, home: 0.2 }), 50 * (4 * 1.8 + 3 * 0.2) / 7), "weights food 4, home 3");
  ok(PEOPLE.moodTarget({ food: 2, home: 2, job: 2 }) === 100 && PEOPLE.moodTarget({ food: 0, home: 0 }) === 0, "range 0..100");
  const child = { id: 2, born: 95, home: 1, job: null, friends: {}, kids: [], parents: [1], mood: 50 };
  ok(PEOPLE.moodParts(child, { day: 100 }).job === 1, "a child has no job factor (neutral)");
  ok(PEOPLE.moodParts({ ...child, born: 0, job: 5 }, { day: 100, paid: false }).paid === NEEDS.unpaid, "unpaid wages: a job holder's factor");
}

// ------------------------------------------------------------------------------------------------ 4. mood tiers -> output; the floor
{
  ok(PEOPLE.moodFactor(95) === 1.2 && PEOPLE.moodFactor(90) === 1.2 && PEOPLE.moodFactor(80) === 1.1 && PEOPLE.moodFactor(75) === 1.1 && PEOPLE.moodFactor(60) === 1.0
     && PEOPLE.moodFactor(50) === 1.0 && PEOPLE.moodFactor(40) === 0.85 && PEOPLE.moodFactor(30) === 0.85 && PEOPLE.moodFactor(29) === 0.7 && PEOPLE.moodFactor(15) === 0.7 && PEOPLE.moodFactor(14) === 0.5 && PEOPLE.moodFactor(0) === 0.5, "tier bands exact");
  ok(OUTPUT.floor === 0.5 && FLAGS.STRIKE === false, "Q2 (his 12:20): floor 0.50, no strike");
  const misery = (P, days, d0 = 100) => { for (let d = 0; d < days; d++) { for (const p of P.list) if (p.alive) p.mood = Math.min(p.mood, 5); PEOPLE.dayStep(P, ctx(d0 + d, { fed: 0, paid: false, san: 0, homes: [] })); } };
  const M = town(8, { homeless: true });
  misery(M, 6);
  const wm = PEOPLE.workMood(M);
  ok(Object.keys(wm).length > 0 && Object.values(wm).every((f) => f === 0.5), "a miserable workshop gives 0.50, never 0 (no strike)", wm);
  ok(M.list.every((p) => !p.alive || p.mood < 15), "they are below the strike mood", M.list.map((p) => p.mood));
  FLAGS.STRIKE = true;
  const S = town(8, { homeless: true });
  misery(S, 2);
  ok(Object.values(PEOPLE.workMood(S)).every((f) => f === 0.5), "strike flag on: 2 days below 15 -> still 0.50");
  misery(S, 1, 102);
  ok(Object.values(PEOPLE.workMood(S)).every((f) => f === 0), "strike flag on: the 3rd day -> 0", PEOPLE.workMood(S));
  FLAGS.STRIKE = false;
  ok(Object.values(PEOPLE.workMood(S)).every((f) => f === 0.5), "flag off again: the floor holds whatever the counter says");
  // the ledger: abstract runs scale, a real day's catch does not
  const farm = (mf) => { const L = ECON.newLedger(); ECON.dayStep(L, { shops: [{ id: 7, kind: "farm_wheat", stations: 2 }], population: 0, moodBy: mf === undefined ? undefined : { 7: mf } }); return L.stock.grain; };
  ok(farm() === 48 && near(farm(0.7), 33.6) && near(farm(1.2), 57.6) && farm(0) === 0, "farm 2 stations x 24 grain: x1 48, x0.70 33.6, x1.2 57.6, strike 0", [farm(), farm(0.7), farm(1.2), farm(0)]);
  const L2 = ECON.newLedger();
  ECON.dayStep(L2, { shops: [{ id: "fishery:1", kind: "fishery", stations: 2 }], population: 0, produced: { "fishery:1": 7 }, moodBy: { "fishery:1": 0.7 } });
  ok(L2.stock.fish === 7, "a real day's catch is not scaled again (the mood is in the hands' pace)", L2.stock.fish);
  const L3 = ECON.newLedger(); L3.stock.grain = 30;
  ECON.dayStep(L3, { shops: [{ id: 9, kind: "bakery", stations: 6 }], population: 0, moodBy: { 9: 1.2 } });
  ok(L3.stock.bread === 48 && L3.stock.grain === 6, "a converter is still bounded by its inputs (1 run of grain)", [L3.stock.bread, L3.stock.grain]);
  const H = town(4); for (const p of H.list) p.mood = 80;
  const f = PEOPLE.workMood(H);
  ok(Object.values(f).every((x) => x === 1.1), "a content workshop (80) gives 1.1", f);
}

// ------------------------------------------------------------------------------------------------ 5. Q4: sanitation no longer kills
{
  ok(FLAGS.SANITATION_DEATH === false, "Q4 default: SANITATION_DEATH = false");
  const old = () => { const P = PEOPLE.newPeople(); for (let i = 0; i < 40; i++) PEOPLE.newPerson(P, 0, { age: 0, home: 1, seed: i }); for (const p of P.list) p.born = -140; return P; };
  const deaths = (san) => { let n = 0; for (let seed = 1; seed <= 30; seed++) { const P = old(); PEOPLE.dayStep(P, { day: 0, fed: 1, homes: [{ id: 1, room: 0 }], jobs: [], seed, sanitation: san }); n += P.list.filter((p) => !p.alive).length; } return n; };
  const dClean = deaths(1), dDirty = deaths(0);
  ok(dClean === dDirty && dClean > 0, "poor sanitation leaves the death roll unchanged", [dClean, dDirty]);
  FLAGS.SANITATION_DEATH = true;
  const dDirtyOld = deaths(0);
  FLAGS.SANITATION_DEATH = false;
  ok(dDirtyOld > dDirty, "the old rule is still there behind the flag (more deaths in a dirty town)", [dDirty, dDirtyOld]);
  const p = { id: 1, born: 0, home: 1, job: null, friends: {}, kids: [], parents: [], mood: 50 };
  ok(PEOPLE.moodParts(p, { day: 50, san: 0.2 }).sanitation < 1 && PEOPLE.moodParts(p, { day: 50, san: 1 }).sanitation > 1 && PEOPLE.moodParts(p, { day: 50, san: 0.7 }).sanitation === 1, "sanitation stays a mood factor (0.7 neutral)");
}

// ------------------------------------------------------------------------------------------------ 6. PE3 grief by closeness
{
  const P = PEOPLE.newPeople();
  const mk = (o) => PEOPLE.newPerson(P, 200, { age: 60, ...o });
  const gp = mk({}), dead = mk({ parents: [gp.id] }), sp = mk({}), kid = mk({ parents: [dead.id, sp.id] }), sib = mk({ parents: [gp.id] });
  const close = mk({}), fr = mk({}), acq = mk({}), border = mk({}), already = mk({});
  dead.spouse = sp.id; sp.spouse = dead.id; dead.kids = [kid.id]; gp.kids = [dead.id, sib.id];
  close.friends[dead.id] = 70; fr.friends[dead.id] = 40; acq.friends[dead.id] = 39; border.friends[dead.id] = 69; sp.friends[dead.id] = 90;
  already.friends[dead.id] = 45; already.grief = 30;
  dead.alive = false;
  PEOPLE.mourn(P, dead);
  ok(sp.grief === GRIEF.spouse && kid.grief === GRIEF.child && gp.grief === GRIEF.parent && sib.grief === GRIEF.sibling, "spouse 20, child 20, parent 15, sibling 10", [sp.grief, kid.grief, gp.grief, sib.grief]);
  ok(close.grief === 8 && fr.grief === 4 && border.grief === 4 && !acq.grief, "friends: fondness >= 70 -> 8, >= 40 -> 4, below 40 -> none", [close.grief, fr.grief, border.grief, acq.grief]);
  ok(already.grief === 30, "a larger grief already held is kept");
  // through dayStep: a certain death (age 160), grief applied, then the day's -1 decay (as in 1.3.227)
  const Q = PEOPLE.newPeople();
  const d2 = PEOPLE.newPerson(Q, 300, { age: 160, home: 1 }), s2 = PEOPLE.newPerson(Q, 300, { age: 100, home: 1 }), k2 = PEOPLE.newPerson(Q, 300, { age: 50, home: 1, parents: [d2.id, s2.id] }), f2 = PEOPLE.newPerson(Q, 300, { age: 60, home: 1 });
  d2.spouse = s2.id; s2.spouse = d2.id; d2.kids = [k2.id]; f2.friends[d2.id] = 75; d2.friends[f2.id] = 75;
  PEOPLE.dayStep(Q, { day: 300, fed: 1, homes: [{ id: 1, room: 0 }], jobs: [], seed: 1 });
  ok(!d2.alive && s2.grief === 19 && k2.grief === 19 && f2.grief === 7, "dayStep: the table, then -1 a day", [d2.alive, s2.grief, k2.grief, f2.grief]);
}

// ------------------------------------------------------------------------------------------------ 7. PE6 births
{
  const c = (o) => PEOPLE.birthChance(o);
  let mono = true;
  for (let m = 0; m < 100; m += 10) if (!(c({ mood: m + 10, foodDays: 10 }) > c({ mood: m, foodDays: 10 }))) mono = false;
  ok(mono, "monotonic up in happiness");
  mono = true;
  for (let f = 0; f < 15; f += 1) if (!(c({ mood: 60, foodDays: f + 1 }) > c({ mood: 60, foodDays: f }))) mono = false;
  ok(mono && c({ mood: 60, foodDays: 30 }) === c({ mood: 60, foodDays: 15 }), "monotonic up in food, capped at foodMax (15 days)");
  mono = true;
  for (let k = 0; k < 10; k++) if (!(c({ mood: 60, foodDays: 10, fullness: (k + 1) / 10 }) < c({ mood: 60, foodDays: 10, fullness: k / 10 }))) mono = false;
  ok(mono, "falls as the town's homes fill");
  ok(near(c({ mood: 50, foodDays: 10, fullness: 0 }), BIRTH.base) && c({ mood: 50, foodDays: 0 }) === 0, "base 0.03 at mood 50, food 10 days, empty; no food -> no births");
  // through dayStep (seeded, positive chance): couples in roomy vs nearly full homes; homes with 2 children have no more
  const couples = (room, kids = 0) => {
    const P = PEOPLE.newPeople(), homes = [];
    for (let i = 0; i < 20; i++) {
      const a = PEOPLE.newPerson(P, 100, { age: 40, sex: "f", home: i + 1, seed: i }), b = PEOPLE.newPerson(P, 100, { age: 40, sex: "m", home: i + 1, seed: 50 + i });
      a.spouse = b.id; b.spouse = a.id; a.mood = b.mood = 70; a.friends[b.id] = b.friends[a.id] = 90;
      for (let k = 0; k < kids; k++) { const ch = PEOPLE.newPerson(P, 100, { age: 2, home: i + 1, parents: [a.id, b.id], seed: 99 + k }); a.kids.push(ch.id); b.kids.push(ch.id); }
      homes.push({ id: i + 1, room });
    }
    return { P, homes };
  };
  const births = (room, kids = 0, days = 5) => {
    let n = 0;
    for (let seed = 1; seed <= 40; seed++) {
      const { P, homes } = couples(room, kids);
      for (let d = 0; d < days; d++) n += PEOPLE.dayStep(P, { day: 100 + d, fed: 1, homes: homes.map((h) => ({ ...h })), jobs: [], seed, foodDays: 12 }).events.filter((e) => e.kind === "birth").length;
    }
    return n;
  };
  const roomy = births(6), full = births(1), capped = births(6, 2);
  ok(roomy > full && full > 0, "a fuller town has fewer births", [roomy, full]);
  ok(capped === 0, "a home with 2 children has no more", capped);
}

// ------------------------------------------------------------------------------------------------ 8. PE12 rumours
{
  const P = PEOPLE.newPeople();
  const a = PEOPLE.newPerson(P, 100, {}), b = PEOPLE.newPerson(P, 100, {}), c = PEOPLE.newPerson(P, 100, {});
  const r1 = PEOPLE.rumour(P, 100, "wedding", "a and b married", [a.id, b.id], [a.id, b.id]);
  ok(r1.heard === 0 && a.knows.includes(r1.id) && b.knows.includes(r1.id) && !c.knows.includes(r1.id), "a rumour starts known by its people only, heard 0");
  for (let i = 0; i < 15; i++) PEOPLE.rumour(P, 100, "news", `n${i}`, [c.id]);
  ok(c.knows.length === RUMOUR.cap && Math.min(...c.knows) === P.rumours[P.rumours.length - 10].id, "cap 10: the newest 10 kept", c.knows);
  ok(PEOPLE.know(c, r1.id) === false && c.knows.length === 10, "an older rumour than all 10 kept is not taken (no churn)");
  const src = readFileSync(new URL("../pw_civ_people.js", import.meta.url), "utf8");
  ok(!/witnesses\.push\(living\[/.test(src), "no random witnesses left in dayStep");
  // a quiet town (men only, no jobs, no free homes: no events): every telling is counted once in `heard`; tellPerDay; interest first
  let fam = 1; while (PEOPLE.interestName({ id: fam }) !== "family") fam++;
  let seen = 0, gained = 0, heardSum = 0, firstThree = true, tellerGain = 0;
  for (let seed = 1; seed <= 30; seed++) {
    const Q = { ...PEOPLE.newPeople(), next: fam };
    const t = PEOPLE.newPerson(Q, 100, { sex: "m", age: 40, home: 1 }), l = PEOPLE.newPerson(Q, 100, { sex: "m", age: 40, home: 2 });
    t.friends[l.id] = 50; l.friends[t.id] = 50;
    const fams = [1, 2, 3].map((k) => PEOPLE.rumour(Q, 99, "wedding", `w${k}`, [t.id]).id);
    for (let k = 0; k < 6; k++) PEOPLE.rumour(Q, 99, "arrival", `a${k}`, [t.id]);
    PEOPLE.dayStep(Q, { day: 100, fed: 1, homes: [{ id: 1, room: 0 }, { id: 2, room: 0 }], jobs: [], seed });
    const g = l.knows.length;
    if (g) { seen++; gained += g; if (!(g === RUMOUR.tellPerDay && fams.every((id) => l.knows.includes(id)))) firstThree = false; }
    heardSum += Q.rumours.reduce((s, x) => s + x.heard, 0);
    tellerGain += t.knows.length - 9;
  }
  ok(seen > 0 && firstThree, "a teller passes 3 a day to a friend — his interest (family: the weddings) before the newer arrivals", { seen });
  ok(heardSum === gained && tellerGain === 0, "heard grows only by tellings (sum heard = what listeners learned)", [heardSum, gained]);
  // a busy town for 30 days: nobody knows more than 10
  const B = town(40);
  let maxK = 0;
  for (let d = 0; d < 30; d++) {
    const ev = d % 2 ? [] : [{ kind: "news", text: `market day ${d}`, people: [B.list[d % 40].id] }];
    PEOPLE.dayStep(B, { ...ctx(100 + d), events: ev });
    for (const p of B.list) maxK = Math.max(maxK, p.knows.length);
  }
  ok(maxK <= RUMOUR.cap && maxK > 0, "busy town, 30 days: knows <= 10", maxK);
  const big = { id: 1, knows: Array.from({ length: 40 }, (_, k) => k + 1) };
  PEOPLE.capKnows(big);
  ok(big.knows.length === 10 && big.knows[0] === 31, "an old save's long list is cut to the newest 10");
}

// ------------------------------------------------------------------------------------------------ 9. PE4 + PE7 skill and diet
{
  const p = { id: 1, skill: { quarry: 70 } };
  ok(PEOPLE.rankOf(p, "quarry", 0) === "apprentice" && PEOPLE.rankOf(p, "quarry", 1) === "journeyman" && PEOPLE.rankOf(p, "quarry", 2) === "master" && PEOPLE.rankOf(p, "quarry", 5) === "master",
     "70 days: homeless apprentice, cottage journeyman, level 2+ master");
  ok(PEOPLE.rankOf(p, "quarry", undefined) === "master", "level not known yet: ungated");
  const curve = (d) => 1 + 0.5 * (1 - Math.exp(-d / 60));
  ok(near(PEOPLE.outputFactor({ skill: { q: 15 } }, "q", 5), curve(15)) && near(PEOPLE.outputFactor({ skill: { q: 60 } }, "q", 5), curve(60)) && near(PEOPLE.outputFactor({ skill: { q: 120 } }, "q", 5), curve(120)),
     "the curve 1 + 0.5 (1 - e^(-d/60)) at 15 / 60 / 120 days", [15, 60, 120].map((d) => PEOPLE.outputFactor({ skill: { q: d } }, "q", 5)));
  ok(near(PEOPLE.outputFactor({ skill: { q: 120 } }, "q", 1), curve(60)) && near(PEOPLE.outputFactor({ skill: { q: 120 } }, "q", 0), curve(15)), "gated: the output stops at the gated rank's ceiling");
  ok(PEOPLE.skillGain(0) === 1 && near(PEOPLE.skillGain(4), 1.2) && near(PEOPLE.skillGain(8), 1.4) && near(PEOPLE.skillGain(10), 1.4 + 2 * 0.05 * 0.35) && PEOPLE.skillGain(100) === SKILL.dayCap,
     "a day: 1 + 0.05 an act; after 8 acts x0.35 (repetition); capped at 1.5", [0, 4, 8, 10, 100].map(PEOPLE.skillGain));
  // through dayStep: in a cottage the days still count, the rank holds at journeyman; a level-2 home makes a master that day
  const P = PEOPLE.newPeople();
  const w = PEOPLE.newPerson(P, 100, { age: 40, home: 1, job: 100, trade: "quarry", sex: "m" });
  w.skill = { quarry: 59 };
  const day = (d, lvl, acts) => PEOPLE.dayStep(P, { day: d, fed: 1, homes: [{ id: 1, room: 0 }], jobs: [{ id: 100, kind: "quarry", vacancies: 0 }], seed: 1, levels: new Map([[1, lvl]]), acts });
  let r = day(100, 1);
  for (let d = 101; d < 105; d++) r = day(d, 1, new Map([[w.id, 20]]));
  ok(w.skill.quarry === 59 + 1 + 4 * 1.5 && PEOPLE.rankOf(w, "quarry") === "journeyman", "the days count while gated (59 + 1 + 4 x 1.5 = 66), still a journeyman", w.skill);
  r = day(105, 2);
  ok(PEOPLE.rankOf(w, "quarry") === "master" && r.events.some((e) => e.kind === "rank" && /master/.test(e.text)), "a level-2 home: master that day (the news)", r.events.map((e) => e.text));
  // diet variety
  ok(PEOPLE.dietVariety({ bread: 100, meat: 60, fish: 0, grain: 30 }, 50) === 3, "variety: goods above one day of need");
  ok(near(PEOPLE.foodDaysOf({ bread: 150, meat: 75 }, 100), 1.5), "food stock in days");
  const h = { id: 3, born: 0, home: 1, job: null, friends: {}, kids: [], parents: [], mood: 50 };
  ok(PEOPLE.moodParts(h, { day: 50, lvl: 1, diet: 2 }).diet === NEEDS.diet.ok && PEOPLE.moodParts(h, { day: 50, lvl: 3, diet: 2 }).diet === NEEDS.diet.short
     && PEOPLE.moodParts(h, { day: 50, lvl: 2, diet: 1 }).diet === 1 && PEOPLE.moodParts(h, { day: 50, lvl: 5, diet: 4 }).diet === NEEDS.diet.ok, "diet: a better house wants more variety (penalty only from level 3)");
  ok(PEOPLE.homeLevel("cottage_s") === 1 && PEOPLE.homeLevel("cottage_l") === 2 && PEOPLE.homeLevel("bakery") === 3 && PEOPLE.homeLevel("manor") === 4 && PEOPLE.homeLevel("palace_ne") === 5 && PEOPLE.homeLevel(null) === 0, "house levels by kind");
}

// ------------------------------------------------------------------------------------------------ 10. PE8 temperament and interest
{
  ok([1, 7, 123, 99999].every((id) => PEOPLE.temperOf({ id }) === PEOPLE.temperOf({ id, name: "x", mood: 3 })), "stable per id (nothing else counts)");
  const t = new Array(8).fill(0), it = new Array(8).fill(0);
  let same = 0;
  for (let id = 1; id <= 8000; id++) { t[PEOPLE.temperOf({ id })]++; it[PEOPLE.interestOf({ id })]++; if (PEOPLE.temperOf({ id }) === PEOPLE.interestOf({ id })) same++; }
  ok(t.every((n) => n > 850 && n < 1150) && it.every((n) => n > 850 && n < 1150), "even spread over the 8 (8,000 ids)", { t, it });
  ok(same > 800 && same < 1200, "temperament and interest are independent", same);
  ok(PEOPLE.temperOf({ id: 5, tm: 2 }) === 2 && FLAGS.TEMPER_INHERIT === false, "a stored tm wins; inheritance off by default (no saved field)");
  const src = readFileSync(new URL("../pw_civ_people.js", import.meta.url), "utf8");
  ok(!/Math\.random/.test(src), "no Math.random in the census law");
}

// ------------------------------------------------------------------------------------------------ 11. save budget (600 people)
{
  // a synthetic city census in the 1.3.228 B2 shape (the saved people section: trust, friends, knows, skill, zero fields)
  const synth = (n, knowsLen) => {
    const P = { next: n + 1, list: [], rumours: [], threads: [], nextThread: 1, player: {}, faucet: 2 };
    for (let i = 1; i <= n; i++) {
      const h = PEOPLE.hash32(i, 77);
      const friends = {}; for (let k = 1; k <= 8; k++) friends[1 + ((i * 7 + k * 13) % n)] = 20 + ((h >> k) % 80);
      const trust = {};
      for (const f of Object.keys(friends).slice(0, 4)) trust[`p:${f}`] = { v: Math.round((0.3 + (h % 50) / 100) * 10000) / 10000, n: 3 + (h % 9), day: 400 + (h % 20) };
      trust["town:food"] = { v: 0.8123, n: 40, day: 420 }; trust["town:council"] = { v: 0.9011, n: 40, day: 420 }; trust[`shop:${100 + (h % 30)}`] = { v: 0.7, n: 12, day: 419 }; trust[`s:${100 + (h % 30)}`] = { v: 0.85, n: 30, day: 420 };
      const job = i % 5 === 4 ? null : 100 + (h % 30), kids = i % 3 ? [] : [1 + ((i + 1) % n), 1 + ((i + 2) % n)];
      P.list.push({ id: i, name: PEOPLE.NAMES_F[h % 20], sex: h % 2 ? "m" : "f", born: 300 + (h % 100), home: 500 + (i >> 1), job, trade: job ? "bakery" : null, spouse: i % 2 ? i + 1 : i - 1,
        parents: i > 300 ? [i - 300, i - 299] : [], kids, friends, mood: 40 + (h % 50), alive: true, knows: Array.from({ length: knowsLen }, (_, k) => 900 + k + (h % 7)),
        grief: 0, lowDays: 0, playerFond: 0, trust, skill: job ? { bakery: 20 + (h % 90) } : {} });
    }
    return P;
  };
  const S0 = synth(600, 10);
  const size0 = JSON.stringify(S0).length;
  // (a) the B3 fields at their worst plausible incidence: 10 % homeless (hl 2 digits), 10 % jobless adults (jl), every skill
  // fractional, the town's needs drift (hunger, hungry days, 30 understaffed workplaces, strike counters), temperament
  // inherited by the town-born (if the flag were on); the B3 compaction drops the zero grief / lowDays / playerFond
  const addB3 = (P, compact) => {
    const Q = clone(P);
    for (const p of Q.list) {
      const h = PEOPLE.hash32(p.id, 5);
      if (h % 10 === 0) p.hl = 10 + (h % 80);
      if (h % 10 === 1) p.jl = 10 + (h % 80);
      for (const k of Object.keys(p.skill)) p.skill[k] = p.skill[k] + 0.5;
      if (p.parents.length && h % 2) p.tm = h % 8;
      if (compact) { for (const k of ["grief", "lowDays", "playerFond"]) if (!p[k]) delete p[k]; }
    }
    Q.need = { h: -0.67, hd: 12, f: Object.fromEntries(Array.from({ length: 30 }, (_, k) => [100 + k, -0.45])), sk: Object.fromEntries(Array.from({ length: 30 }, (_, k) => [100 + k, 2])) };
    return Q;
  };
  const size1 = JSON.stringify(addB3(S0, true)).length, size1raw = JSON.stringify(addB3(S0, false)).length;
  console.log(`  save: 600 people, B2 shape ${size0} chars; with B3 fields ${size1} (${((size1 / size0 - 1) * 100).toFixed(2)} %); without the compaction ${size1raw} (+${((size1raw / size0 - 1) * 100).toFixed(2)} %)`);
  ok(size1 <= size0 * 1.10, "B3 fields within +10 % of the census section", [size0, size1]);
  ok(size1raw <= size0 * 1.10, "even without the zero-field compaction, within +10 %", [size0, size1raw]);
  // (b) A/B: the same census (a 227-era save: 40 rumours known each) run 30 days under the B2 law and the B3 law
  const base = synth(600, 40);
  base.rumours = Array.from({ length: 60 }, (_, k) => ({ id: 900 + k, day: 395 + (k >> 2), kind: "news", text: `rumour ${k} about the market and the well`, about: [], heard: 5 }));
  const run = (M) => {
    const P = clone(base);
    const homes = Array.from({ length: 300 }, (_, k) => ({ id: 500 + k, room: 0 }));
    const jobs = Array.from({ length: 30 }, (_, k) => ({ id: 100 + k, kind: "bakery", vacancies: k % 4 }));
    const lv = new Map(homes.map((h) => [h.id, 1 + (h.id % 3)]));
    for (let d = 0; d < 30; d++) M.dayStep(P, { day: 420 + d, fed: d < 15 ? 1 : 0.6, paid: true, homes: homes.map((h) => ({ ...h })), jobs: jobs.map((j) => ({ ...j })), seed: 3, sanitation: 0.6, levels: lv, foodDays: 6, diet: 2 });
    return P;
  };
  const Pold = run(OLD), Pnew = run(PEOPLE);
  const sOld = JSON.stringify(Pold).length, sNew = JSON.stringify(Pnew).length;
  const kOld = Pold.list.reduce((a, p) => a + p.knows.length, 0), kNew = Pnew.list.reduce((a, p) => a + p.knows.length, 0);
  console.log(`  save A/B after 30 days: B2 law ${sOld} chars (knows ${kOld}), B3 law ${sNew} chars (knows ${kNew}): ${((sNew / sOld - 1) * 100).toFixed(1)} %`);
  ok(sNew <= sOld * 1.10, "A/B: the B3 census is within +10 % of the B2 one", [sOld, sNew]);
  ok(kNew < kOld && Pnew.list.every((p) => p.knows.length <= 10), "A/B: the knows share falls (cap 10)", [kOld, kNew]);
}

console.log(`test_needs: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
