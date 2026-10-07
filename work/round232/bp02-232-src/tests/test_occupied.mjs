// test_occupied.mjs — 1.3.227: the number-key occupancy test answers exactly as the string-key one (random streets + boxes)
import { readFileSync } from "node:fs";
const src = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
const grab = (name) => { const i = src.indexOf(`function ${name}(`); let d = 0, j = src.indexOf("{", i); for (let k = j; k < src.length; k++) { if (src[k] === "{") d++; else if (src[k] === "}") { d--; if (!d) return src.slice(i, k + 1); } } };
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; if (fail < 5) console.log("FAIL", m); } };
function rnd(seed) { let a = seed >>> 0; return () => { a += 0x6D2B79F5; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
for (let trial = 0; trial < 6; trial++) {
  const r = rnd(trial + 7);
  const bodies = [new Map(), new Map()];
  for (const m of bodies) for (let n = 0; n < 400; n++) m.set(`${Math.floor(r() * 200) - 300},${Math.floor(r() * 200) - 60}`, 70);
  const boxes = [];
  for (let n = 0; n < 40; n++) { const x0 = Math.floor(r() * 200) - 300, z0 = Math.floor(r() * 200) - 60; boxes.push([x0, x0 + Math.floor(r() * 20), z0, z0 + Math.floor(r() * 20)]); }
  const s = { settlements: [{ id: 1 }, { id: 2 }], buildings: [] };
  const env = { plotBoxes: () => boxes, bodyOf: (st) => bodies[st.id - 1], streetHeights: () => { const m = new Map(); for (const b of bodies) for (const [k, h] of b) m.set(k, h); return m; } };
  const newFn = new Function("plotBoxes", "bodyOf", "streetHeights", `const OCC_OFF = 2097152, OCC_W = 4194304; ${grab("occupiedBuild")}; return occupiedBuild;`)(env.plotBoxes, env.bodyOf, env.streetHeights)(s);
  const oldFn = (() => { const streets = env.streetHeights(); const near = new Set(); for (const k of streets.keys()) { const [x, z] = k.split(",").map(Number); near.add(k); near.add(`${x},${z - 1}`); near.add(`${x},${z + 1}`); near.add(`${x - 1},${z}`); near.add(`${x + 1},${z}`); } return (x, z) => near.has(`${x},${z}`) || boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1); })();
  for (let x = -310; x < -90; x++) for (let z = -70; z < 150; z += 3) ok(newFn(x, z) === oldFn(x, z), `${x},${z}`);
}
console.log(`test_occupied: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
