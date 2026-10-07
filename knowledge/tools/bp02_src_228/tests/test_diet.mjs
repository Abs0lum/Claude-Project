// test_diet.mjs — 1.3.227: the people's daily diet (trust of the dead, of former friends, neutral idle entries)
import * as PEOPLE from "../pw_civ_people.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const P = { list: [], next: 1, rumours: [], threads: [], nextThread: 1 };
const a = PEOPLE.newPerson(P, 100, { age: 30 }), b = PEOPLE.newPerson(P, 100, { age: 30 }), c = PEOPLE.newPerson(P, 100, { age: 30 }), d = PEOPLE.newPerson(P, 100, { age: 30 });
a.friends[b.id] = 40;                                                  // b is a's friend; c is not (any more)
PEOPLE.learn(a, `p:${b.id}`, 0.8, 100); PEOPLE.learn(a, `p:${c.id}`, 0.8, 100);
PEOPLE.learn(a, "shop:5", 1, 100); PEOPLE.learn(a, "shop:6", 0.52, 50);  // shop:6 near neutral and idle 70 days
PEOPLE.learn(a, "town:food", 0.52, 119);                               // near neutral but recent
a.trust["shop:5"].v = 0.123456789;
d.alive = false; d.died = 110; d.trust = { "shop:1": { v: 0.9, n: 3, day: 100 } }; d.knows = [1, 2];
c.alive = false; c.died = 120; c.trust = { "shop:2": { v: 0.9, n: 3, day: 120 } };
PEOPLE.diet(P, 120);
ok(a.trust[`p:${b.id}`] !== undefined, "friend's opinion kept");
ok(a.trust[`p:${c.id}`] === undefined, "former friend's opinion dropped");
ok(a.trust["shop:6"] === undefined, "neutral idle entry dropped");
ok(a.trust["town:food"] !== undefined, "recent neutral entry kept");
ok(a.trust["shop:5"].v === 0.1235, "4 decimals");
ok(d.trust === undefined && d.knows.length === 0, "the long dead keep no opinions");
ok(c.trust !== undefined, "died today: kept for the inheritance");
ok(PEOPLE.trustOf(a, "shop:6") === 0.5, "forgotten = neutral");
console.log(`test_diet: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
