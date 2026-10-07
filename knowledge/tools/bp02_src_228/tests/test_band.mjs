// test_band.mjs — 1.3.231 (CIV-LAND) ELEVATION BANDS: a parallel street on its own contour level joined by a 4-part-ramp
// switchback leg (KIT.planBandStreetJob), on synthetic hillsides like his 00:23 10-07 site. Usage: node tests/test_band.mjs
// [--dump FILE [SLOPE]] (writes the plan of one hill, 0.3 / 0.35 / 0.45, as JSON for the renderer).
import * as KIT from "../pw_civ_streets.js";
import { writeFileSync } from "node:fs";
let n = 0, bad = 0;
const ok = (name, cond, info) => { n++; if (!cond) bad++; console.log(`${cond ? "PASS" : "FAIL"} ${n} ${name}${cond ? "" : " — " + JSON.stringify(info).slice(0, 400)}`); };
const run = (gen) => { let r = gen.next(), steps = 0; while (!r.done) { r = gen.next(); steps++; } return [r.value, steps]; };
const STREET_OPTS = { maxCut: 6, maxFill: 6, ramp8: true };          // = the clock's STREET_OPTS (STREET_CUT / STREET_FILL 6, 8-ramp)
const HALVES = [70, 55, 40];                                           // = the clock's KIT_SIDE_HALVES
// a hillside rising along +z (slope blocks per block, floored: 1-block terraces as in his screenshots); flat below z 0
const hill = (slope) => ({ at: (x, z) => 64 + Math.floor(Math.max(0, z) * slope), isWater: () => false });
// the base street: along +x at z 0..12 (on the contour), 130 cells; its junction window at tj 50, side +1 (uphill)
const f = KIT.frameOf(0, 0, [1, 0], [0, 1]);
const tj = 50, side = 1;
const baseCells = new Set();
for (let t = 0; t < 130; t++) for (let w = 0; w < 13; w++) { const [x, z] = KIT.cellOf(f, t, w); baseCells.add(`${x},${z}`); }
// houses on the base street's uphill side, outside its junction window (t 50..62): boxes w 13..24
const houses = [];
for (let t = 2; t + 9 < 128; t += 11) { if (t + 9 >= tj && t <= tj + 12) continue; houses.push([t, t + 9]); }
const inHouse = (x, z) => houses.some(([a, b]) => x >= a && x <= b && z >= 13 && z <= 24);
const streetBlocked = (x, z) => baseCells.has(`${x},${z}`) || inHouse(x, z);
const legBlocked = streetBlocked;

// --- 1. the OLD law (the clock's sideStreetJob, connector within +-K of Hb), replayed: which hills can it climb?
function oldLaw(site) {
  const Hb = site.at(tj + 6, 6);
  let okN = 0;
  for (const D of KIT.SIDE_OFFSETS) {
    const Lc = D - 13, K = Math.min(3, Math.floor(Lc / 7));
    const [cx0, cz0] = KIT.cellOf(f, tj, 13);
    const fc = KIT.frameOf(cx0, cz0, [0, 1], [1, 0]);
    const gc = KIT.groundAlong(site, fc, 0, Lc);
    let found = false;
    for (const half of HALVES) {
      const f2 = KIT.frameOf(f.ox + D * f.vx + (tj - half) * f.ux, f.oz + D * f.vz + (tj - half) * f.uz, [1, 0], [0, 1]);
      const ground = KIT.groundAlong(site, f2, 0, 2 * half + 13);
      for (let dh = -K; dh <= K && !found; dh++) {
        const fixed = new Map(); for (let t = half; t < half + 13; t++) fixed.set(t, Hb + dh);
        const p2 = KIT.planProfile(ground, { ...STREET_OPTS, fixed, flat: [[half - 1, half + 13]] });
        if (p2.cost === Infinity) continue;
        const pc = KIT.planProfile(gc, { ...STREET_OPTS, startDead: false, endDead: false, startH: Hb, endH: Hb + dh });
        if (pc.cost < Infinity) found = true;
      }
      if (found) break;
    }
    if (found) okN++;
  }
  return okN;
}
const old10 = oldLaw(hill(0.1)), old30 = oldLaw(hill(0.3)), old45 = oldLaw(hill(0.45));
ok("old law: a 1-in-10 hill opens parallels at every pitch (8 of 8)", old10 === 8, old10);
ok("old law: a 0.30 hill opens NO parallel at any of the 8 pitches (the witnessed stall)", old30 === 0, old30);
ok("old law: a 0.45 hill opens none either", old45 === 0, old45);

// --- 2. the mouths
{
  const f2 = KIT.frameOf(0, 60, [1, 0], [0, 1]);
  const m = KIT.bandMouths(f, tj, side, f2, tj);
  ok("mouths: P0 just outside the base (w 13), P1 just outside the parallel's near side (w -1)", m.P0[1] === 13 && m.P1[1] === 59 && m.P0[0] === 56 && m.P1[0] === 56, m);
  ok("mouths: the road arrives heading INTO the parallel (d1 = d0 = +v)", m.d0.join() === "0,1" && m.d1.join() === "0,1", m);
  const f2r = KIT.frameOf(0, 72, [1, 0], [0, -1]);                    // the same corridor z 60..72, its v reversed
  const mr = KIT.bandMouths(f, tj, side, f2r, tj);
  ok("mouths: a parallel whose v runs the other way — P1 still on its near side (z 59)", mr.P1[1] === 59, mr);
  const fd = KIT.frameOf(0, 0, [1, 0], [0, 1]);
  const md = KIT.bandMouths(fd, tj, -1, KIT.frameOf(0, -60, [1, 0], [0, 1]), tj);
  ok("mouths: side -1 — P0 at z -1, P1 at z -47 (the parallel's far side w 13), heading -v", md.P0[1] === -1 && md.P1[1] === -47 && md.d1.join() === "0,-1", md);
}

// --- 3. the clock's legJob arrival (d1 = -d0) can never land; the band mouths can (the 1.3.231 one-line fix)
{
  const site = hill(0.3);
  const of = KIT.frameOf(0, 60, [1, 0], [0, 1]);
  const body = new Set(baseCells);
  for (let t = 0; t < 130; t++) for (let w = 0; w < 13; w++) { const [x, z] = KIT.cellOf(of, t, w); body.add(`${x},${z}`); }
  const blocked = (x, z) => body.has(`${x},${z}`);
  const ground = (x, z) => ({ g: site.at(x, z), water: false });
  const Hb = site.at(56, 6), Hn = site.at(56, 66);
  const m = KIT.bandMouths(f, tj, side, of, tj);
  const [oldRoad] = run(KIT.planRoadJob(ground, blocked, m.P0, m.d0, m.P1, [-m.d0[0], -m.d0[1]], Hb, Hn, 6, {}));
  const [newRoad] = run(KIT.planRoadJob(ground, blocked, m.P0, m.d0, m.P1, m.d1, Hb, Hn, 6, {}));
  ok("legJob's old arrival (heading back to the base) finds no leg between parallels 18 apart in height", oldRoad === null, oldRoad && oldRoad.cells.length);
  ok("the corrected arrival finds the switchback leg", !!newRoad && newRoad.H[0] === Hb && newRoad.H[newRoad.H.length - 1] === Hn, newRoad && { n: newRoad.cells.length });
}

// --- 4. the band street on the hills the old law could not climb
// (a house row 12 deep lines the base street's uphill side except at the window: the leg must leave through the window's
// 13-cell gap first, flat for its first 7 cells — on that bank the band reaches 0.35; on an open hillside 0.5)
const openBlocked = (x, z) => baseCells.has(`${x},${z}`);
const plans = {};
for (const [slope, withHouses] of [[0.3, true], [0.35, true], [0.45, false]]) {
  const site = hill(slope);
  const Hb = site.at(tj + 6, 6);
  const stats = {};
  const t0 = Date.now();
  let band = null, steps = 0;
  const sb = withHouses ? streetBlocked : openBlocked;
  for (const D of KIT.BAND.offsets) { [band, steps] = run(KIT.planBandStreetJob(site, f, tj, side, Hb, D, sb, sb, STREET_OPTS, stats)); if (band) break; }
  const ms = Date.now() - t0;
  plans[slope] = { band, Hb, site, withHouses };
  ok(`band ${slope}${withHouses ? " (houses on the bank)" : " (open hillside)"}: a band street and its leg are planned`, !!band, stats);
  if (!band) continue;
  const lf = KIT.legFacts(band.road);
  ok(`band ${slope}: the parallel stands beyond the connector's reach (rise ${band.rise} > K 3)`, band.rise > 3, band.rise);
  ok(`band ${slope}: its junction window is level at its own height (13 cells at Hn ${band.Hn})`, band.p2.H.slice(band.half, band.half + 13).every((h) => h === band.Hn));
  const g = band.f2 && KIT.groundAlong(site, band.f2, 0, band.L2);
  const worst = Math.max(...band.p2.H.map((h, i) => (g[i] ? Math.abs(h - g[i].g) : 0)));
  ok(`band ${slope}: the band street keeps the street law (cut / fill <= 6 over its median ground; worst ${worst})`, worst <= 6, worst);
  ok(`band ${slope}: the leg climbs exactly the rise (${lf.climb})`, lf.climb === band.rise && band.road.H[0] === Hb, lf);
  ok(`band ${slope}: every ramp of the leg is his 4-part ramp (1 block over 4 cells)`, lf.rampLens.length === 1 && lf.rampLens[0] === KIT.ROAD_RAMP && lf.ramps >= band.rise, lf);
  ok(`band ${slope}: never steeper than 1 in 4 (any 4 cells rise <= 1; any step <= 1)`, lf.steep4 <= 1 && lf.maxStep <= 1, lf);
  ok(`band ${slope}: it zig-zags — at least 2 turns, every turn on a flat 7-cell landing`, lf.turns >= 2 && lf.landings, lf);
  const legCells = band.road.cells;
  const cells2 = KIT.corridorCells(band.f2, band.p2, 0, new Map());
  const touches = legCells.slice(1, -1).filter(([x, z], i) => { const d = band.road.dirs[i + 1], p = [-d[1], d[0]]; for (let k = -KIT.ROAD_HALF; k <= KIT.ROAD_HALF; k++) { const cx = x + p[0] * k, cz = z + p[1] * k; if (sb(cx, cz) || cells2.has(`${cx},${cz}`)) return true; } return false; });
  ok(`band ${slope}: the leg's 7-cell width never touches the base street, its houses or the band street`, touches.length === 0, touches.slice(0, 3));
  ok(`band ${slope}: one search stays a background job (${ms} ms in node, ${steps} yields)`, ms < 4000 && steps > 20, { ms, steps });
  // his 04:0x 10-07 ruling: "because of the width of the roads, we have to do more short runs, and run them contiguously to
  // get the correct height jump, THEN make the switchback" — the climb is made on the straight RUNS (along the contour, f.u)
  // by 4-part ramps chained end to end; the uphill LINKS (along f.v) that make the switchback are flat; more short runs
  // rather than deep cuts (road within ROAD_CUT of the ground away from the two mouth landings)
  // LEAD RULINGS 10-07 (04:3x CT): Q1 — the straight MOUTH out through the window (the first segment, along f.v) may carry
  // chained 4-part ramps, so it is exempt from the flat-link check (it is still checked for chaining); Q2 — the earthwork
  // check uses the narrow-road law: fill (road above ground) <= ROAD_CUT 4, cut (road below ground) <= ROAD_CUT_MAX 6
  {
    const R = band.road, Hs = R.H, bounds = [0, ...R.turns, Hs.length - 1];
    let linkRise = 0, broken = 0, runs = 0, worstFill = 0, worstCut = 0;
    for (let k = 0; k + 1 < bounds.length; k++) {
      const a = bounds[k], b = bounds[k + 1], d = R.dirs[Math.min(b, a + 1)];
      const alongU = Math.abs(d[0] * f.ux + d[1] * f.uz) === 1;
      const rises = [];
      for (let i = a + 1; i <= b; i++) if (Hs[i] !== Hs[i - 1]) rises.push(i);
      if (!alongU && k > 0) { linkRise += Math.abs(Hs[b] - Hs[a]); continue; }   // Q1: the mouth (k 0) may climb
      if (rises.length) runs++;
      for (let j = 1; j < rises.length; j++) if (rises[j] - rises[j - 1] !== KIT.ROAD_RAMP) broken++;
    }
    for (let i = 7; i < Hs.length - 7; i++) { const [x, z] = R.cells[i]; const dH = Hs[i] - site.at(x, z); worstFill = Math.max(worstFill, dH); worstCut = Math.max(worstCut, -dH); }
    ok(`band ${slope}: the switchback links (uphill) are flat — the height is gained on the runs (link rise ${linkRise})`, linkRise === 0, { linkRise });
    ok(`band ${slope}: on every run the 4-part ramps are chained end to end (no flat between ramps; ${broken} breaks, ${runs} climbing runs)`, broken === 0 && runs >= 2, { broken, runs });
    ok(`band ${slope}: more short runs, not deep cuts — off the mouths fill <= ${KIT.ROAD_CUT}, cut <= ${KIT.ROAD_CUT_MAX} (fill ${worstFill}, cut ${worstCut})`, worstFill <= KIT.ROAD_CUT && worstCut <= KIT.ROAD_CUT_MAX, { worstFill, worstCut });
  }
  console.log(`  band ${slope}: D ${band.D}, half ${band.half}, Hb ${Hb} -> Hn ${band.Hn} (rise ${band.rise}); leg ${lf.cells} cells, ${lf.turns} turns, ${lf.ramps} ramps; ${ms} ms`);
}

// the limit, recorded: 0.45 behind a house row — the window's straight exit climbs 5.4 in 12 cells against 1 in 4
{
  const site = hill(0.45), Hb = site.at(tj + 6, 6);
  let band = null;
  for (const D of KIT.BAND.offsets) { [band] = run(KIT.planBandStreetJob(site, f, tj, side, Hb, D, streetBlocked, legBlocked, STREET_OPTS, {})); if (band) break; }
  ok("limit: a 0.45 bank behind a house row gets no band from this window (the bench roads remain)", band === null, band && band.rise);
}
// --- 5. a gentle hill: the band planner still works (the clock tries it only after the connector law failed)
{
  const site = hill(0.1), Hb = site.at(tj + 6, 6);
  const [band] = run(KIT.planBandStreetJob(site, f, tj, side, Hb, 60, streetBlocked, legBlocked, STREET_OPTS, {}));
  ok("gentle hill: a band plan exists (rise <= 9) with a leg of 1 in 4 at most", !!band && KIT.legFacts(band.road).steep4 <= 1, band && band.rise);
}
// --- 6. a river between the bands: no leg through water deeper than the road's deck rules; nothing is returned over unknown land
{
  const site = { at: (x, z) => (z > 30 && z < 40 ? undefined : 64 + Math.floor(Math.max(0, z) * 0.3)), isWater: () => false };
  const Hb = site.at(tj + 6, 6);
  const [band] = run(KIT.planBandStreetJob(site, f, tj, side, Hb, 60, streetBlocked, legBlocked, STREET_OPTS, {}));
  ok("unknown land (an unread strip) between the bands: no band is planned across it", band === null || band.road.cells.every(([x, z]) => site.at(x, z) !== undefined), band && band.road.cells.length);
}

const dumpAt = process.argv.indexOf("--dump");
const dumpSlope = Number(process.argv[dumpAt + 2] || 0.45);
if (dumpAt > 0 && plans[dumpSlope] && plans[dumpSlope].band) {
  const { band, Hb, site, withHouses } = plans[dumpSlope];
  const box = [-10, 150, -6, 140];
  const grid = [];
  for (let z = box[2]; z <= box[3]; z++) { const row = []; for (let x = box[0]; x <= box[1]; x++) row.push(site.at(x, z)); grid.push(row); }
  const cells2 = [...KIT.corridorCells(band.f2, band.p2, 0, new Map())].map(([k, h]) => k.split(",").map(Number).concat([h]));
  const base = [...baseCells].map((k) => k.split(",").map(Number));
  writeFileSync(process.argv[dumpAt + 1], JSON.stringify({ box, grid, base, slope: dumpSlope, houses: withHouses ? houses.map(([a, b]) => [a, b, 13, 24]) : [], band: cells2, leg: band.road.cells.map(([x, z], i) => [x, z, band.road.H[i]]), turns: band.road.turns, Hb, Hn: band.Hn, D: band.D, half: band.half, tj }));
  console.log(`  dumped the ${dumpSlope} plan to ${process.argv[dumpAt + 1]}`);
}
console.log(`test_band: ${n - bad}/${n} passed`);
if (bad) process.exitCode = 1;
