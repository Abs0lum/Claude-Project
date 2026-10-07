// test_talk.mjs — B5 voice (pw_civ_talk.js): speech duration, wrap, template fill, dialogue priority + once memory,
// memory cap, petition urgency / pick / cooldown / outcome, overheard pair pick + cooldown + scripts. Deterministic.
import * as T from "../pw_civ_talk.js";

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);

// PE9 speech duration
eq(T.speechTicks(""), 40, "empty line 40 ticks");
eq(T.speechTicks("x".repeat(20)), 70, "20 chars -> 70");
eq(T.speechTicks("x".repeat(400)), 360, "capped at 360");
// wrap
eq(T.wrap("one two three four five six seven eight nine ten", 12), ["one two", "three four", "five six", "seven eight", "nine ten"], "wrap at 12");
ok(T.wrap("a".repeat(50), 30).length === 1, "an over-long word stays whole");
// fill
eq(T.fill("{n} day{s:n}", { n: 1 }), "1 day", "plural 1");
eq(T.fill("{n} day{s:n}", { n: 3 }), "3 days", "plural 3");
eq(T.fill("{missing}!", {}), "!", "missing key empty");

// dialogue priority
const base = { id: 7, name: "Ada", mood: 60 };
let f = T.factsOf(base, { town: "Lyn", tier: "stranger" });
eq(T.pickLine(base, f, 10).id, "first", "first meeting wins over small talk");
const met = { ...base, playerFond: 5 };
f = T.factsOf(met, { town: "Lyn" });
eq(T.pickLine(met, f, 10).id, "small", "met + nothing else: small talk");
f = T.factsOf({ ...met, hl: 3 }, { town: "Lyn" });
const homeLine = T.pickLine({ ...met, hl: 3 }, f, 10);
eq(homeLine.id, "homeless", "homeless beats small talk");
ok(/3 days/.test(homeLine.text), `homeless line carries the days: ${homeLine.text}`);
f = T.factsOf({ ...met, hl: 3 }, { town: "Lyn", hd: 2, petition: "Please help" });
eq(T.pickLine({ ...met, hl: 3 }, f, 10).id, "petition", "petition beats every need");
f = T.factsOf(met, { town: "Lyn", why: "SITE_WAITS:stone" });
ok(/stone/.test(T.pickLine(met, f, 10).text), "site-waits line names the good");
// deterministic
const a1 = T.pickLine(met, T.factsOf(met, { town: "Lyn" }), 12), a2 = T.pickLine(met, T.factsOf(met, { town: "Lyn" }), 12);
eq(a1, a2, "same day same person same line");
// once: day (news)
const newsP = { ...met, id: 9 };
f = T.factsOf(newsP, { town: "Lyn", rumour: "the mill burned", tier: "customer" });
const n1 = T.pickLine(newsP, f, 20);
eq(n1.id, "news", "news when a rumour is known and not a stranger");
T.noteSaid(newsP, n1.id, 20);
ok(T.pickLine(newsP, f, 20).id !== "news", "news once a day");
eq(T.pickLine(newsP, f, 21).id, "news", "news again next day");
// once: ever (first)
const fresh = { id: 11, name: "Bo", mood: 50 };
f = T.factsOf(fresh, {});
T.noteSaid(fresh, "first", 5);
ok(T.pickLine(fresh, f, 6).id !== "first", "first meeting only once");
// stranger gets no news
f = T.factsOf(newsP, { rumour: "x", tier: "stranger" });
ok(T.pickLine(newsP, f, 30).id !== "news", "a stranger hears no news");

// memory cap
const m = { id: 1 };
for (let i = 0; i < 7; i++) T.remember(m, `k${i}`, 100 + i);
eq(Object.keys(m.mem).length, T.MEM.cap, "memory capped");
ok(m.mem.k6 === 106, "the newest key kept");
ok(m.mem.k0 === undefined, "the soonest-expiring dropped");
T.pruneMem(m, 104);
eq(Object.keys(m.mem).sort(), ["k4", "k5", "k6"], "prune expired");
T.pruneMem({ id: 2 }, 5);

// petitions
const pf = (o) => T.factsOf({ id: o.id || 1, name: "P", mood: 40, hl: o.hl || 0, jl: o.jl || 0, job: o.job ?? null }, { hd: o.hd || 0, arrears: o.arrears || 0 });
eq(T.urgencyOf(pf({ hl: 2 })), 6, "2 homeless days = 6");
eq(T.urgencyOf({ ...pf({ hl: 1 }), child: true }), 0, "children never petition");
eq(T.urgencyOf(pf({ arrears: 3 })), 0, "arrears count only for job holders");
eq(T.urgencyOf(pf({ arrears: 3, job: 5 })), 6, "3 days unpaid x2");
eq(T.needOf(pf({ hl: 1, jl: 5 })), "job", "the largest term names the need");
const cands = [
  { p: { id: 3 }, f: pf({ hl: 1 }), d: 5 },            // 3: below threshold
  { p: { id: 4 }, f: pf({ hl: 2 }), d: 9 },            // 6
  { p: { id: 5 }, f: pf({ hl: 3 }), d: 20 },           // 9 -> wins
  { p: { id: 6, pet: 99 }, f: pf({ hl: 9 }), d: 1 },   // 27 but on cooldown at day 100
];
const pk = T.pickPetitioner(cands, 100);
eq(pk.p.id, 5, "max urgency off cooldown wins");
eq(pk.need, "home", "need home");
ok(/3 days/.test(pk.plea), `plea text: ${pk.plea}`);
eq(T.pickPetitioner(cands, 101).p.id, 6, "cooldown passes after cooldownDays");
eq(T.pickPetitioner([cands[0]], 100), null, "nobody over the threshold: no petitioner");
const tie = T.pickPetitioner([{ p: { id: 8 }, f: pf({ hl: 2 }), d: 4 }, { p: { id: 7 }, f: pf({ hl: 2 }), d: 4 }], 50);
eq(tie.p.id, 7, "ties: distance then id");
ok(T.petitionMet("home", { home: 12 }) && !T.petitionMet("home", {}), "home met when housed");
ok(T.petitionMet("food", {}, { hd: 0 }) && !T.petitionMet("food", {}, { hd: 2 }), "food met when the town eats");
ok(!T.petitionMet("wages", {}, { arrears: 1 }), "wages unmet while in arrears");

// overheard pair
const bodies = [{ vid: "a", pid: 1, x: 0, z: 0 }, { vid: "b", pid: 2, x: 3, z: 0 }, { vid: "c", pid: 3, x: 1, z: 1 }, { vid: "d", pid: 4, x: 40, z: 0 }];
const fond = (x, y) => ({ "1-2": 50, "1-3": 80, "2-3": 30 })[`${Math.min(x, y)}-${Math.max(x, y)}`] || 0;
const pair = T.pickPair(bodies, fond, new Map(), 1000);
eq(pair.key, "1-3", "the most fond pair");
const last = new Map([["1-3", 900]]);
eq(T.pickPair(bodies, fond, last, 1000).key, "1-2", "cooldown skips the pair");
eq(T.pickPair(bodies, fond, last, 900 + T.OVERHEARD.pairCooldown).key, "1-3", "cooldown ends");
eq(T.pickPair([bodies[0], bodies[3]], () => 99, new Map(), 0), null, "too far apart");
eq(T.pickPair([bodies[0], bodies[1]], () => 5, new Map(), 0), null, "not fond enough");
// scripts
let sc = T.scriptFor(T.factsOf({ id: 1, mood: 60 }, { hd: 2, town: "Lyn" }));
eq(sc.key, "hungry", "hungry town script");
ok(sc.lines.length >= 2 && sc.lines.every((l, i) => i === 0 || l.delay > sc.lines[i - 1].delay), "script delays increase");
ok(/2 days/.test(sc.lines[2].text), "script filled");
sc = T.scriptFor(T.factsOf({ id: 1, mood: 80 }, { town: "Lyn" }));
eq(sc.key, "content", "content town script");
sc = T.scriptFor(T.factsOf({ id: 1, mood: 80 }, { town: "Lyn", rumour: "a wedding at the square" }));
eq(sc.key, "news", "news script");

console.log(`test_talk: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
