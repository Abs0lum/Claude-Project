// test_watch.mjs — B10: the watch's morale (unpaid x0.7, a good day +2, cap), half rounds below 40, the watchman who leaves
// below 20 (never a crime), the crime factors measured, and the posts paid first in the economy.
import * as P from "../pw_civ_people.js";
import * as E from "../pw_civ_economy.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);
eq(P.watchMorale(undefined, { paid: true, housed: true, fed: true }), 62, "a good day from the start");
eq(P.watchMorale(60, { paid: false }), 42, "an unpaid day x0.7");
eq(P.watchMorale(99.5, { paid: true, housed: true, fed: true }), 100, "capped");
eq(P.watchMorale(50, { paid: true, housed: false, fed: true }), 50, "homeless: no gain");
let m = 60, d = 0; while (m >= P.WATCH_M.half) { m = P.watchMorale(m, { paid: false }); d++; }
eq(d, 2, "two unpaid days to half rounds");
while (m >= P.WATCH_M.crime) { m = P.watchMorale(m, { paid: false }); d++; }
eq(d, 4, "four unpaid days and he leaves");
ok(P.halfRounds({ job: "watch", mor: 39 }) && !P.halfRounds({ job: "watch", mor: 41 }) && !P.halfRounds({ job: "baker", mor: 10 }), "half rounds rule");
eq(P.crimeFactors({ job: 3, mood: 10, hl: 4, jl: 0 }, { paid: false, hd: 8 }), { score: 9, parts: { unpaid: 2, homeless: 2, hungry: 2, mood: 3 } }, "factors");
eq(P.crimeFactors({ job: 3, mood: 70 }, { paid: true, hd: 0 }).score, 0, "a content paid worker: 0");
ok(P.CRIME.enabled === false, "crime stays OFF");
// dayStep: an unpaid watch over 5 days -> half rounds, then he leaves; a departure event, never a crime
const PP = P.newPeople();
const w = P.newPerson(PP, 0, { job: "watch", age: 30, home: 1, seed: 3 });
const crimeSeen = [];
let left = false;
for (let day = 1; day <= 8 && !left; day++) {
  const r = P.dayStep(PP, { day, fed: 1, paid: false, watchPaid: false, homes: [{ id: 1, room: 3 }], jobs: [], seed: 1, name: "Lyn", events: [] });
  crimeSeen.push(r.crime.atRisk);
  if (r.departures.includes(w.id)) { left = true; ok(r.events.some((e) => e.kind === "left" && /watch/.test(e.text)), "the leaving is told"); }
}
ok(left, "the unpaid watchman leaves");
ok(!w.alive, "and is gone from the census");
// economy: the posts are paid first
const L = E.newLedger(); L.treasury = 100;
E.dayStep(L, { shops: [{ id: 1, kind: "bakery", stations: 2 }], population: 4, households: 1, posts: { watch: 1 } });
ok(L.watchPaid === true, "100 p covers the watch's 96");
const L2 = E.newLedger(); L2.treasury = 50;
E.dayStep(L2, { shops: [], population: 4, households: 1, posts: { watch: 1 } });
ok(L2.watchPaid === false, "50 p does not");
console.log(`test_watch: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
