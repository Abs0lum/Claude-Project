// test_ramp8.mjs — 1.3.228 (his 12:20 + 13:40): the street planner prefers the 8-block ramp and falls back to the 7-cell
// ramp only where there is no room; pieces are named ramp8 / ramp7 by length; heights stay continuous.
import { planProfile, piecesOf, RAMP8 } from "../pw_civ_streets.js";
let pass = 0, fail = 0;
const ok = (c, m, x) => { if (c) pass++; else { fail++; console.log("FAIL", m, x !== undefined ? JSON.stringify(x) : ""); } };
const gentle = (L, from, to) => Array.from({ length: L }, (_, t) => ({ g: Math.round(from + (to - from) * t / (L - 1)) }));
const opts = { maxCut: 6, maxFill: 6, ramp8: true };
{ // a long gentle hill: 3 blocks over 80 cells -> all 8-ramps
  const p = planProfile(gentle(80, 64, 67), opts);
  const r = p.segs.filter((s) => s.kind === "ramp");
  ok(p.cost < Infinity && r.length >= 2 && r.every((s) => s.len === 8), "gentle hill: only 8-ramps (the planner may cut instead of a third)", r.map((s) => s.len));
}
{ // ramp8 off: the old behaviour (7-cell ramps)
  const p = planProfile(gentle(80, 64, 67), { maxCut: 6, maxFill: 6 });
  const r = p.segs.filter((s) => s.kind === "ramp");
  ok(r.length === 3 && r.every((s) => s.len === 7), "ramp8 off: 7-cell ramps as before", r.map((s) => s.len));
}
{ // no room: 5 blocks to climb in 38 free cells (fixed ends) -> 8 x 5 = 40 does not fit, so some 7s
  const g = gentle(38, 60, 65);
  const p = planProfile(g, { ...opts, startDead: false, endDead: false, startH: 60, endH: 65, maxCut: 8, maxFill: 8 });
  const r = p.segs.filter((s) => s.kind === "ramp");
  ok(p.cost < Infinity && r.length === 5 && r.some((s) => s.len === 7) && r.some((s) => s.len === 8), "no room: a mix of 7 and 8", r.map((s) => s.len));
}
{ // room for all 8s: the same climb over 60 free cells -> all 8
  const g = gentle(60, 60, 65);
  const p = planProfile(g, { ...opts, startDead: false, endDead: false, startH: 60, endH: 65, maxCut: 8, maxFill: 8 });
  const r = p.segs.filter((s) => s.kind === "ramp");
  ok(p.cost < Infinity && r.length === 5 && r.every((s) => s.len === 8), "room: all 8-ramps", r.map((s) => s.len));
}
{ // continuity: H never jumps by more than 1 between neighbours, and the ramp's cells are the lower level
  const p = planProfile(gentle(90, 70, 66), opts);
  let jump = 0;
  for (let t = 1; t < p.H.length; t++) if (p.H[t] !== undefined && p.H[t - 1] !== undefined && Math.abs(p.H[t] - p.H[t - 1]) > 1) jump++;
  ok(jump === 0, "descending: no jumps > 1", jump);
  const r = p.segs.filter((s) => s.kind === "ramp" && s.len === 8);
  ok(r.length >= 3 && r.every((s) => s.dir === -1 && p.H[s.a] === s.H - 1 && p.H[s.a + 7] === s.H - 1), "descending 8-ramps: cells at the lower level", r);
  const f = { ox: 0, oz: 0, ux: 1, uz: 0, vx: 0, vz: 1 };
  const pcs = piecesOf(f, p, "t", 0).pieces.filter((q) => q.kind === "ramp");
  ok(pcs.length >= 3 && pcs.every((q) => q.name === "t_ramp8" && q.len === RAMP8), "pieces named t_ramp8", pcs.map((q) => q.name));
}
console.log(`test_ramp8: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
