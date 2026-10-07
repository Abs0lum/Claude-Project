// test_route.mjs — 1.3.227: the number-key A* finds routes of the same length as the string-key one; pieces are right
import { __routeTest as R } from "../pw_civ_walk.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
function rnd(seed) { let a = seed >>> 0; return () => { a += 0x6D2B79F5; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
for (let trial = 0; trial < 12; trial++) {
  const r = rnd(trial + 1), map = new Map(), x0 = -300 + trial * 37, z0 = -120 - trial * 11;
  for (let x = x0; x < x0 + 60; x++) for (let z = z0; z < z0 + 60; z++) if (r() < 0.72) map.set(`${x},${z}`, 64 + Math.floor(r() * 3));
  map.__num = new Map(); for (const [k, y] of map) map.__num.set(R.numOf(k), y);
  map.__key = `t${trial}`;
  const keys = [...map.keys()];
  for (let q = 0; q < 10; q++) {
    const a = keys[Math.floor(r() * keys.length)], b = keys[Math.floor(r() * keys.length)];
    const p1 = R.routeSearch(map, a, b), p2 = R.routeSearchStr(map, a, b);
    const p3 = R.routeSteps(map, a, b);
    ok(JSON.stringify(p3) === JSON.stringify(p1), "steps = search");
    ok((p1 === null) === (p2 === null), `found differs ${a} ${b}`);
    if (p1 && p2) {
      ok(p1.length === p2.length, `length ${p1.length} vs ${p2.length}`);
      ok(`${p1[0][0]},${p1[0][1]}` === a && `${p1[p1.length - 1][0]},${p1[p1.length - 1][1]}` === b, "ends");
      let good = true; for (let i = 1; i < p1.length; i++) { const d = Math.abs(p1[i][0] - p1[i - 1][0]) + Math.abs(p1[i][1] - p1[i - 1][1]); if (d !== 1 || Math.abs(p1[i][2] - p1[i - 1][2]) > 1 || p1[i][2] !== map.get(`${p1[i][0]},${p1[i][1]}`)) good = false; }
      ok(good, "steps");
    }
    // pieces: same piece <=> a route exists
    const comp = R.components(map.__num);
    ok((comp.get(R.numOf(a)) === comp.get(R.numOf(b))) === (p2 !== null), `piece vs route ${a} ${b}`);
  }
}
console.log(`test_route: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
