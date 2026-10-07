// test_frontage.mjs — 1.3.225 house frontage (KIT.frontStretches + placeAlong): ramps carry houses, the floor stands at the
// highest sidewalk, a frontage never spans more than FRONT_RISE, a shaft without room for its own hatch is a cesspit
// house, the old flat stretches keep the old law. Usage: node tests/test_frontage.mjs
import * as K from "../pw_civ_streets.js";
let n = 0, bad = 0;
const ok = (name, cond, info) => { n++; if (!cond) bad++; console.log(`${cond ? "PASS" : "FAIL"} ${n} ${name}${cond ? "" : " — " + JSON.stringify(info).slice(0, 400)}`); };
// a hill rising 1 per 10 cells: the planner makes ramps with flats between
const L = 160;
const ground = Array.from({ length: L }, (_, t) => { const g = 60 + Math.floor(t / 10); return { g, water: false, lo: g, hi: g }; });
const plan = K.planProfile(ground, {});
const ramps = plan.segs.filter((s) => s.kind === "ramp").length;
ok("the hill plan has ramps", ramps >= 6, plan.segs);
const flatCells = K.flatStretches(plan, 0, []).reduce((a, s) => a + s.b - s.a + 1, 0);
const runs = K.frontStretches(plan, 0, []);
const frontCells = runs.reduce((a, s) => a + s.b - s.a + 1, 0);
ok("frontage runs cover flat + ramp cells (more than the flats)", frontCells > flatCells && frontCells === L - 26, { flatCells, frontCells });
ok("runs carry per-cell heights and kinds", runs.every((s) => s.Hs.length === s.b - s.a + 1 && s.kinds.length === s.Hs.length && /^[fr]+$/.test(s.kinds)), runs[0]);
ok("a reserved window is cut out", K.frontStretches(plan, 0, [[60, 72]]).every((s) => s.b < 60 || s.a > 72));
// a house def: 8 deep, 9 frontage, shaft at local z 4
const def = { size: [8, 20, 9] };
const f = K.frameOf(0, 0, [1, 0], [0, 1]);
const free = () => true;
// pack the whole street: every slot's frontage rise <= 1, floor = max sidewalk along it
const slots = [];
const taken = new Set();
for (let i = 0; i < 40; i++) {
  const s = K.placeAlong(f, { "1": runs, "-1": [] }, def, 4, 0, (big) => !slots.some((o) => !(big[1] < o.box[0] || big[0] > o.box[1] || big[3] < o.box[2] || big[2] > o.box[3])), taken, 1, 1, []);
  if (!s) break;
  slots.push(s);
  if (s.shaftT !== null) taken.add(s.shaftT);
}
const H = plan.H;
const riseOk = slots.every((s) => { const hs = H.slice(s.at, s.at + 9); return Math.max(...hs) - Math.min(...hs) <= K.FRONT_RISE && s.H === Math.max(...hs); });
ok("every house: rise <= 1 along its front, floor at the highest cell", riseOk, slots.map((s) => [s.at, s.H, H.slice(s.at, s.at + 9)]));
const flatOnly = (() => { const sl = []; const tk = new Set(); for (let i = 0; i < 40; i++) { const s = K.placeAlong(f, { "1": K.flatStretches(plan, 0, []), "-1": [] }, def, 4, 0, (big) => !sl.some((o) => !(big[1] < o.box[0] || big[0] > o.box[1] || big[3] < o.box[2] || big[2] > o.box[3])), tk, 1, 1, []); if (!s) break; sl.push(s); if (s.shaftT !== null) tk.add(s.shaftT); } return sl.length; })();
ok("the hill street holds more houses with ramp frontage than flat-only", slots.length > flatOnly, { ramp: slots.length, flatOnly });
const cess = slots.filter((s) => s.cesspit);
ok("a house whose shaft cannot have its own hatch is a BRANCH house (shaftT null, branchT = its shaft)", slots.filter((s) => s.cesspit).every((s) => s.shaftT === null && Number.isInteger(s.branchT)) && slots.filter((s) => !s.cesspit).every((s) => s.shaftT !== null), slots.map((s) => [s.at, s.shaftT, s.branchT]));
// every house reaches the sewer: a hatch, or a branch whose 4 cells x 4 rows meet the hall (H(t) - 11 .. H(t) - 8) in >= 3 rows
const reach = slots.every((s) => {
  if (s.shaftT !== null) return true;
  const cells = K.branchCells(f, s.branchT, 1, s.H);
  const Ht = plan.H[s.branchT];
  const rows = new Set(cells.map((c) => c[1]).filter((y) => y >= Ht - 11 && y <= Ht - 8));
  const ws = new Set(cells.map((c) => c[2]));
  return cells.length === 16 && rows.size >= 3 && [9, 10, 11, 12].every((w) => ws.has(w));
});
ok("every branch house reaches the sewer hall (>= 3 shared rows, w 9..12 on side +1)", reach);
ok("branch cells on side -1 are w 0..3", JSON.stringify([...new Set(K.branchCells(f, 20, -1, 70).map((c) => c[2]))].sort()) === "[0,1,2,3]");
const hatchOk = slots.filter((s) => s.shaftT !== null).every((s) => { const q = s.shaftT; return plan.segs.some((g) => g.kind === "flat" && g.a <= q - 1 && g.a + g.len - 1 >= q + 1); });
ok("every hatch stands on 3 flat cells", hatchOk);
// two hatches never closer than ACCESS unless shared
const ts = slots.filter((s) => s.shaftT !== null).map((s) => s.shaftT).sort((a, b) => a - b);
ok("hatches keep their spacing", ts.every((t, i) => i === 0 || t === ts[i - 1] || t - ts[i - 1] >= K.ACCESS), ts);
// the old law (flat stretches without Hs) still refuses a shaft without a hatch
const oldSt = [{ a: 13, b: 25, H: 60 }];
const s0 = K.placeAlong(f, { "1": oldSt, "-1": [] }, def, 4, 0, free, new Set([18]), 1, 1, []);
ok("old flat stretches: a clashing shaft is still refused there", s0 === null || s0.shaftT === null || Math.abs(s0.shaftT - 18) >= K.ACCESS || s0.shaftT === 18, s0);
console.log(`test_frontage: ${n - bad}/${n} passed (houses: ramp-aware ${slots.length}, flat-only ${flatOnly}, cesspit ${cess.length}, ramps ${ramps})`);
if (bad) process.exitCode = 1;
