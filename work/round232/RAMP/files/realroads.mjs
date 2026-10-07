// read-only experiment: bench-like roads on the gate world's saved heightmap (civheight-20261005-190214), planned with and
// without opts.ramp8; the share of 8-part ramps by the road's mean grade
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
const W = process.argv[2];
const K = await import(`${W}/pw_civ_streets.js`);
const txt = gunzipSync(readFileSync(`${W}/tests/fixtures/civheight-20261005-190214.txt.gz`)).toString();
const head = JSON.parse(txt.match(/\{"step":"heighthead".*\}/)[0]);
const H = new Map();
for (const m of txt.matchAll(/\[CIVHEIGHT\] (-?\d+) (\S+)/g)) {
  const z = Number(m[1]); let x = head.x0;
  for (const run of m[2].split(",")) { const [v, k] = run.split("*"); const cnt = k ? Number(k) : 1; for (let q = 0; q < cnt; q++, x++) { if (v === "?") continue; H.set(`${x},${z}`, v === "w" ? { g: 62, water: true } : { g: Number(v), water: false }); } }
}
const ground = (x, z) => H.get(`${x},${z}`);
const run = (gen) => { let r = gen.next(), n = 0; while (!r.done && n < 400000) { r = gen.next(); n++; } return r.done ? r.value : null; };
let seed = 12345; const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
const rows = [];
for (let tries = 0; rows.length < 40 && tries < 400; tries++) {
  const x0 = head.x0 + 20 + Math.floor(rnd() * (head.x1 - head.x0 - 140)), z0 = head.z0 + 20 + Math.floor(rnd() * (head.z1 - head.z0 - 40));
  const len = 60 + Math.floor(rnd() * 60);
  const P0 = [x0, z0], P1 = [x0 + len, z0];
  const a = ground(...P0), b = ground(...P1);
  if (!a || !b || a.water || b.water) continue;
  const S = {};
  const r8 = run(K.planRoadJob(ground, () => false, P0, [1, 0], P1, [1, 0], a.g, b.g, 6, S, { ramp8: true }));
  if (!r8) continue;
  const r4 = run(K.planRoadJob(ground, () => false, P0, [1, 0], P1, [1, 0], a.g, b.g, 6, {}));
  const lens = r8.segs.filter((s) => s.kind === "ramp").map((s) => s.len);
  if (!lens.length) continue;
  const grade = Math.abs(b.g - a.g) / len;
  // the LOCAL ground grade at each ramp: the ground's rise over the 16 cells around its middle (the road's own cells)
  const gAt = (i) => { const c = ground(...r8.cells[Math.max(0, Math.min(r8.cells.length - 1, i))]); return c ? c.g : null; };
  const local = r8.segs.filter((s) => s.kind === "ramp").map((s) => { const m = s.a + (s.len >> 1), u = gAt(m + 8), d = gAt(m - 8); return { len: s.len, lg: u === null || d === null ? null : Math.abs(u - d) / 16 }; });
  let ew = 0, deep = 0; r8.H.forEach((h, i) => { const c = ground(...r8.cells[i]); if (c && !c.water) { ew += Math.abs(h - c.g); if (c.g - h >= 5) deep++; } });
  const e4 = r4 ? r4.H.reduce((acc, h, i) => { const c = ground(...r4.cells[i]); return acc + (c && !c.water ? Math.abs(h - c.g) : 0); }, 0) : 0;
  rows.push({ ew, e4, deep, grade, n: lens.length, n8: lens.filter((x) => x === 8).length, cells: r8.cells.length, cells4: r4 ? r4.cells.length : null, local });
}
rows.sort((p, q) => p.grade - q.grade);
const band = (lo, hi) => { const rs = rows.filter((r) => r.grade >= lo && r.grade < hi); const n = rs.reduce((s, r) => s + r.n, 0), n8 = rs.reduce((s, r) => s + r.n8, 0); return `${rs.length} roads, ${n8}/${n} ramps 8-part (${n ? Math.round(100 * n8 / n) : "-"} %)`; };
console.log("grade <= 1/8 :", band(0, 0.125 + 1e-9));
console.log("1/8 .. 1/5   :", band(0.125 + 1e-9, 0.2));
console.log("1/5 .. 1/4   :", band(0.2, 0.25 + 1e-9));
console.log("> 1/4        :", band(0.25 + 1e-9, 9));
console.log(`earthwork sum |H-g|: ramp8 ${rows.reduce((a, r) => a + r.ew, 0)} vs 4-only ${rows.reduce((a, r) => a + r.e4, 0)}; cells cut >= 5: ${rows.reduce((a, r) => a + r.deep, 0)} of ${rows.reduce((a, r) => a + r.cells, 0)}`);
const all = rows.flatMap((r) => r.local).filter((q) => q.lg !== null);
for (const [lo, hi, nm] of [[0, 0.125 + 1e-9, "local ground <= 1/8"], [0.125 + 1e-9, 0.25 + 1e-9, "local 1/8 .. 1/4"], [0.25 + 1e-9, 99, "local > 1/4"]]) {
  const q = all.filter((x) => x.lg >= lo && x.lg < hi);
  console.log(`${nm}: ${q.length} ramps, ${q.filter((x) => x.len === 8).length} 8-part (${q.length ? Math.round(100 * q.filter((x) => x.len === 8).length / q.length) : "-"} %)`);
}
if (process.argv[3] === "rows") for (const r of rows) console.log(`grade 1/${(1 / r.grade).toFixed(1)}  ramps ${r.n}  8-part ${r.n8}  cells ${r.cells} (4-only plan ${r.cells4})`);
