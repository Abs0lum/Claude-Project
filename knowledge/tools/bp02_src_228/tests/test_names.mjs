// test_names.mjs — B9 TR10 street names (unique, deterministic) and GB6 titles (spirit points -> rung).
import * as N from "../pw_civ_names.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);
const taken = new Set();
for (let i = 1; i <= 40; i++) { const nm = N.streetName(i, i % 3 ? "side" : "main", taken, 7); ok(!taken.has(nm), `unique ${nm}`); taken.add(nm); }
eq(N.streetName(5, "side", new Set(), 7), N.streetName(5, "side", new Set(), 7), "deterministic");
ok(N.streetName(3, "lane", new Set(), 1).match(/Steps|Lane|Walk|Rise/), "a lane's suffix");
const pts = N.spiritOf({ fishery: 6, bakery: 1, cottage_s: 9 });
eq(pts, { nautical: 30, market: 3 }, "points");
eq(N.titleOf(pts), { spirit: "nautical", rung: 0, title: "Fishing Hamlet" }, "first rung");
eq(N.titleOf(N.spiritOf({ fishery: 13 })).title, "Fishing Village", "60 points -> second rung");
eq(N.titleOf({ nautical: 30, mining: 30, market: 30 }), null, "no dominant spirit");
eq(N.titleOf({}), null, "nothing standing");
eq(N.titleOf({ crown: 8 }), null, "below the first step");
console.log(`test_names: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
