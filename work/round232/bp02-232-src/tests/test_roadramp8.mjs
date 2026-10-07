// test_roadramp8.mjs — 1.3.232 (#5): 8-part ramps on mild narrow ROADS, laid block by block. His rulings: 04:12 CT 10-07
// "8-part on mild roads, 4-part only on steep; switchback legs stay 4-part"; D-GH1007-RAMP8 "one by one (block by block)" —
// the staged structure r_ramp8.mcstructure stays unused. Covers:
//   * the REAL blocks (tests/fixtures/ramp_cobble_230.json, read from BP-02 1.3.230 by make_fixture.py): ids, states, and
//     the street piece t_ramp8's cobble lane — the model the road copies (e1 at the low end, cardinal_direction = uphill);
//   * the profile (KIT.planProfile with the road's law + opts.ramp8): mild -> 8-part, steep -> 4-part, the cut / fill law,
//     continuity; without opts.ramp8 (the legs) nothing changes;
//   * the road planner (KIT.planRoadJob opts) and the clock's wiring (static checks on the source);
//   * the clock's road layer: layRoadOp cut from pw_civ_clock.js and run on a stand-in world (every block it sets).
// Usage: node tests/test_roadramp8.mjs
import * as KIT from "../pw_civ_streets.js";
import { readFileSync, readdirSync } from "node:fs";

let n = 0, bad = 0;
const ok = (name, cond, info) => { n++; if (!cond) bad++; console.log(`${cond ? "PASS" : "FAIL"} ${n} ${name}${cond ? "" : " — " + String(JSON.stringify(info)).slice(0, 500)}`); };
const FX = JSON.parse(readFileSync(new URL("./fixtures/ramp_cobble_230.json", import.meta.url), "utf8"));
const run = (gen) => { let r = gen.next(); while (!r.done) r = gen.next(); return r.value; };
const CARDS = ["north", "south", "east", "west"];

// ------------------------------------------------------------------------------------------------ 1. the real blocks
{
  const e = [1, 2, 3, 4, 5, 6, 7, 8].map((k) => FX.blocks[`pw:ramp_cobble_8_e${k}`]);
  ok("fixture: pw:ramp_cobble_8_e1..e8 exist in BP-02 1.3.230", e.every(Boolean), Object.keys(FX.blocks));
  ok("fixture: their states are cardinal_direction (placement trait) + pw:snow 0..4 only — no pw:var (SLIM)", e.every((b) => b && JSON.stringify(b.trait_states) === '["minecraft:cardinal_direction"]'
     && JSON.stringify(Object.keys(b.states)) === '["pw:snow"]' && JSON.stringify(b.states["pw:snow"]) === "[0,1,2,3,4]"), e.map((b) => b && b.states));
  ok("fixture: e_k's collision top is 2k px (one block over 8 cells; e8 is a full block)", e.every((b, i) => b && b.collision_h === 2 * (i + 1)), e.map((b) => b && b.collision_h));
  ok("fixture: the same facing table as the 4-part (south 0, east 90, north 180, west 270)", e.every((b) => JSON.stringify(b.rot) === JSON.stringify(FX.blocks["pw:ramp_cobble_4_q1"].rot)), e.map((b) => b && b.rot));
  const lane = FX.t_ramp8_lane.cells;
  ok("model (street piece t_ramp8, travel +x, low end x 0): e1 .. e8 from the low end to the high end, every one facing east (= uphill)",
     lane.length === 8 && lane.every((c, i) => c.name === `pw:ramp_cobble_8_e${i + 1}` && c.states["minecraft:cardinal_direction"] === "east"), lane);
}

// ------------------------------------------------------------------------------------------------ 2. the profile
// the road's law (the clock's planRoadJob): fixed ends, 7 flat cells at each end, cut <= ROAD_CUT_MAX, fill <= ROAD_CUT (a deck
// beyond), the ramp on a deck allowed; his 4-part ramp R = ROAD_RAMP; opts.ramp8 = the 8-part allowed (preferred by cost)
const roadOpts = (L, H0, H1, ramp8) => ({ startDead: false, endDead: false, startH: H0, endH: H1, flat: [[0, 6], [L - 7, L - 1]],
  maxCut: KIT.ROAD_CUT_MAX, maxFill: KIT.ROAD_CUT, bridgeDrop: KIT.ROAD_CUT, ramp: KIT.ROAD_RAMP, rampOnBridge: true, ramp8 });
const slope = (L, s, base = 64) => Array.from({ length: L }, (_, t) => ({ g: base + Math.floor(t * s), water: false }));
const lensOf = (p) => p.segs.filter((q) => q.kind === "ramp").map((q) => q.len);
// the law of every planned road: H steps <= 1; an 8-ramp's 8 cells at its lower level, the cell beyond its high end one up;
// fill <= ROAD_CUT unless a deck (bridge segment), cut <= ROAD_CUT_MAX
const lawOf = (p, g) => {
  const why = [];
  for (let t = 1; t < p.H.length; t++) if (Math.abs(p.H[t] - p.H[t - 1]) > 1) why.push(["step", t]);
  for (const q of p.segs.filter((s) => s.kind === "ramp" && s.len === 8)) {
    const lo = q.dir > 0 ? q.H : q.H - 1;
    for (let k = 0; k < 8; k++) if (p.H[q.a + k] !== lo) why.push(["lower", q.a + k]);
    if (q.dir > 0 && q.a + 8 < p.H.length && p.H[q.a + 8] !== lo + 1) why.push(["after", q.a + 8]);
    if (q.dir < 0 && q.a > 0 && p.H[q.a - 1] !== lo + 1) why.push(["before", q.a - 1]);
  }
  const deck = new Set();
  for (const q of p.segs.filter((s) => s.kind === "bridge")) for (let k = 0; k < q.len; k++) deck.add(q.a + k);
  p.H.forEach((h, t) => { if (g[t].g - h > KIT.ROAD_CUT_MAX) why.push(["cut", t]); if (h - g[t].g > KIT.ROAD_CUT && !deck.has(t)) why.push(["fill", t]); });
  return why;
};
{
  for (const [name, L, s] of [["1 in 16", 120, 1 / 16], ["1 in 12", 120, 1 / 12], ["1 in 10", 100, 1 / 10]]) {
    const g = slope(L, s), H0 = g[0].g, H1 = g[L - 1].g;
    const p = KIT.planProfile(g, roadOpts(L, H0, H1, true)), lens = lensOf(p);
    ok(`mild road ${name} (climb ${H1 - H0}): every ramp is the 8-part`, p.cost < Infinity && lens.length === H1 - H0 && lens.every((x) => x === 8), lens);
    ok(`mild road ${name}: the law holds (steps <= 1, 8-ramp cells at the lower level, cut / fill caps)`, p.cost < Infinity && lawOf(p, g).length === 0, lawOf(p, g).slice(0, 4));
    const p4 = KIT.planProfile(g, roadOpts(L, H0, H1, false)), l4 = lensOf(p4);
    ok(`mild road ${name} WITHOUT ramp8 (the switchback legs' law): every ramp the 4-part, as before`, p4.cost < Infinity && l4.length === H1 - H0 && l4.every((x) => x === KIT.ROAD_RAMP), l4);
  }
  // 1 in 8 = the 8-part's own pitch: the 14 flat end cells make the road climb a little faster than the ground somewhere
  {
    const L = 100, g = slope(L, 1 / 8), H0 = g[0].g, H1 = g[L - 1].g;
    const p = KIT.planProfile(g, roadOpts(L, H0, H1, true)), lens = lensOf(p);
    ok("road at 1 in 8 (the 8-part's pitch): mostly 8-parts (>= 2/3), a 4-part only where the fixed flat ends force a quicker climb", p.cost < Infinity && lens.filter((x) => x === 8).length * 3 >= lens.length * 2 && lens.length === H1 - H0, lens);
    ok("road at 1 in 8: the law holds", lawOf(p, g).length === 0, lawOf(p, g).slice(0, 4));
  }
  // STEEP: 1 in 4 (the 4-part's own pitch), climb 20 in 100 cells
  {
    const L = 100, g = slope(L, 1 / 4), H0 = g[0].g, H1 = H0 + 20;
    const p = KIT.planProfile(g, roadOpts(L, H0, H1, true)), lens = lensOf(p);
    ok("steep road 1 in 4: the 4-part (>= 90 % of the ramps)", p.cost < Infinity && lens.length === 20 && lens.filter((x) => x === 4).length >= 18, lens);
    ok("steep road 1 in 4: the law holds", lawOf(p, g).length === 0, lawOf(p, g).slice(0, 4));
  }
  // between the pitches (1 in 6): the planner mixes 4- and 8-parts and keeps the road on the ground (|H - g| <= 1)
  {
    const L = 100, g = slope(L, 1 / 6), H0 = g[0].g, H1 = g[L - 1].g;
    const p = KIT.planProfile(g, roadOpts(L, H0, H1, true)), lens = lensOf(p);
    let worst = 0; p.H.forEach((h, t) => { worst = Math.max(worst, Math.abs(h - g[t].g)); });
    ok("road at 1 in 6 (between the pitches): both kinds, the road within one block of the ground", p.cost < Infinity && lens.includes(4) && lens.includes(8) && worst <= 1, { lens, worst });
  }
  // DESCENDING (the cells run downhill): the 8-ramp's dir -1, its cells at the lower level
  {
    const L = 100, g = slope(L, -1 / 10, 80), H0 = g[0].g, H1 = g[L - 1].g;
    const p = KIT.planProfile(g, roadOpts(L, H0, H1, true));
    const rs = p.segs.filter((q) => q.kind === "ramp");
    ok("descending mild road: every ramp an 8-part going down (dir -1)", p.cost < Infinity && rs.length === H0 - H1 && rs.every((q) => q.len === 8 && q.dir === -1), rs);
    ok("descending mild road: the law holds", lawOf(p, g).length === 0, lawOf(p, g).slice(0, 4));
  }
  // the streets keep their own law (ramp7 vs ramp8): unchanged by the roads' opt
  {
    const g = slope(80, 3 / 79);
    const p = KIT.planProfile(g, { maxCut: 6, maxFill: 6, ramp8: true });
    ok("streets unchanged: a gentle street still takes the 8-ramp (street law, R = 7)", p.cost < Infinity && lensOf(p).length >= 2 && lensOf(p).every((x) => x === 8), lensOf(p));
  }
}

// ------------------------------------------------------------------------------------------------ 3. the road planner
// the planner picks its own shape (on these open slopes a 4-turn one); its LANDINGS (7 flat cells at each end, 3 each side of
// a turn) hold no ramp, so the road must sometimes climb quicker right beside one: a 4-part may stand there, nowhere else
const landingGap = (r) => {
  const n2 = r.cells.length, wins = [[0, 6], [n2 - 7, n2 - 1]].concat(r.turns.map((i) => [i - 3, i + 3]));
  return r.segs.filter((q) => q.kind === "ramp" && q.len === 4).map((q) => Math.min(...wins.map(([p, e]) => Math.max(0, p - (q.a + 3), q.a - e))));
};
for (const [L, div] of [[100, 10], [120, 12], [140, 14], [200, 12]]) {
  const ground = (x, z) => ({ g: 64 + Math.floor(Math.max(0, x) / div), water: false });
  const H1 = 64 + Math.floor(L / div);
  const r8 = run(KIT.planRoadJob(ground, () => false, [0, 0], [1, 0], [L, 0], [1, 0], 64, H1, 6, {}, { ramp8: true }));
  const l8 = r8 ? lensOf(r8) : [], gaps = r8 ? landingGap(r8) : [99];
  ok(`planRoadJob opts.ramp8, mild road 1 in ${div} (climb ${H1 - 64}): the 8-part carries the climb (>= 2/3 of the ramps); a 4-part only beside a landing (<= 2 cells)`,
     r8 && l8.length === H1 - 64 && l8.filter((x) => x === 8).length * 3 >= l8.length * 2 && gaps.every((gp) => gp <= 2), { l8, gaps });
  const r4 = run(KIT.planRoadJob(ground, () => false, [0, 0], [1, 0], [L, 0], [1, 0], 64, H1, 6, {}));
  const l4 = r4 ? lensOf(r4) : null;
  ok(`planRoadJob without opts (the climbing legs), 1 in ${div}: only his 4-part ramp, as before`, r4 && l4.length === H1 - 64 && l4.every((x) => x === KIT.ROAD_RAMP), l4);
}
{
  const steep = (x, z) => ({ g: 64 + Math.floor(Math.max(0, x) / 4), water: false });
  const rs = run(KIT.planRoadJob(steep, () => false, [0, 0], [1, 0], [100, 0], [1, 0], 64, 84, 6, {}, { ramp8: true }));
  const ls = rs ? lensOf(rs) : null;
  ok("planRoadJob opts.ramp8 on a steep road (1 in 4, climb 20): the 4-part (>= 90 %)", rs && ls.length === 20 && ls.filter((x) => x === 4).length >= 18, ls);
}

// ------------------------------------------------------------------------------------------------ 4. the clock's wiring
const src = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
const ssrc = readFileSync(new URL("../pw_civ_streets.js", import.meta.url), "utf8");
{
  ok("streets: planProfile allows the 8-ramp for the road's 4-part ramp too (the gate)", /const with8 = !!opts\.ramp8 && \(R === RAMP \|\| R === ROAD_RAMP\);/.test(ssrc));
  // the road's own dial: a road's ends are fixed (a street end, a bench end), so the streets' 12 left ~27 % 4-parts on mild
  // roads on the gate world's heightmap (40 roads, ramp-scripts/realroads.mjs); 48 -> 95 %, steep roads unchanged (6 %)
  ok("streets: the roads' 4-part costs ROAD4_EXTRA (48) more when the 8-part is on; the streets keep RAMP7_EXTRA (12)", KIT.ROAD4_EXTRA === 48 && KIT.RAMP7_EXTRA === 12
     && /let rc = with8 \? 5 \+ \(R === ROAD_RAMP \? ROAD4_EXTRA : RAMP7_EXTRA\) : 5;/.test(ssrc), [KIT.ROAD4_EXTRA, KIT.RAMP7_EXTRA]);
  ok("streets: planRoadJob / planRoadShapesJob take opts and hand ramp8 to both exact profiles",
     /export function\* planRoadShapesJob\([^)]*stats = null, opts = null\)/.test(ssrc) && /export function\* planRoadJob\([^)]*stats = null, opts = null\)/.test(ssrc)
     && (ssrc.match(/ramp: ROAD_RAMP, rampOnBridge: true, ramp8: !!\(opts && opts\.ramp8\) \}\)/g) || []).length === 2
     && /yield\* planRoadShapesJob\(ground, blocked, P0, d0, P1, d1, H0, H1, maxDP, S, opts\)/.test(ssrc));
  ok("streets: the band leg (planBandLegJob, then its planRoadJob fallback) never asks for the 8-ramp (switchback legs stay 4-part)",
     ssrc.includes("if (!road) road = yield* planRoadJob(ground2, blocked, P0, d0, P1, d1, Hb, Hn, BAND.maxDP, legStats);") && !/function\* planBandLegJob[\s\S]{0,6000}ramp8/.test(ssrc.slice(0, ssrc.indexOf("export function* planBandStreetJob"))));
  ok("clock: ROAD_OPTS = { ramp8: true }; the bench road (benchJob) plans with it",
     /const ROAD_OPTS = \{ ramp8: true \};/.test(src) && src.includes("const road = yield* KIT.planRoadJob(ground, blocked, dep.P, dep.d, P1, d1, dep.H, H1, 6, stats, ROAD_OPTS);"));
  ok("clock: the climbing leg (legJob) plans WITHOUT it (a switchback leg: 4-part)", src.includes("const road = yield* KIT.planRoadJob(ground, blocked, P0, d0, P1, d1, Hb, Hn, 6, stats);"));
  ok("clock: the gate stubs (a straight narrow road) plan with it", /maxCut: 4, maxFill: 4, noBridge: true, \.\.\.ROAD_OPTS \}\)/.test(src));
  const recs = src.match(/ramps: (?:road|plan)\.segs\.filter\(\(q\) => q\.kind === "ramp"\)\.map\(\(q\) => \[q\.a, q\.dir, q\.len\]\)/g) || [];
  ok("clock: every road record keeps each ramp's own length [a, dir, len] (commitBench, commitLeg, the gate stubs)", recs.length === 3 && !/\.map\(\(q\) => \[q\.a, q\.dir\]\)/.test(src), recs.length);
  const scripts = readdirSync(new URL("..", import.meta.url)).filter((f) => f.endsWith(".js"));
  const held = scripts.filter((f) => /r_ramp8|road\/r_/.test(readFileSync(new URL(`../${f}`, import.meta.url), "utf8")));
  ok("no script references the held structure r_ramp8 (the road ramp is laid block by block)", held.length === 0, held);
}

// ------------------------------------------------------------------------------------------------ 5. layRoadOp on stand-ins
const cut = (name) => {
  let i = src.indexOf(`function ${name}(`);
  let j = src.indexOf("{", i), depth = 0;
  for (; j < src.length; j++) { if (src[j] === "{") depth++; else if (src[j] === "}" && --depth === 0) break; }
  return src.slice(i, j + 1);
};
const cutConst = (name) => { const i = src.indexOf(`const ${name} =`); return src.slice(i, src.indexOf(";\n", i) + 1); };
const resolveLog = [];
const BlockPermutation = {
  // the engine's resolve, held to the REAL block table: an unknown id, state or value throws (as BlockPermutation.resolve does)
  resolve(id, states = {}) {
    const b = FX.blocks[id];
    if (!b) throw new Error(`unknown block ${id}`);
    for (const [k, v] of Object.entries(states)) {
      if (k === "minecraft:cardinal_direction" ? !(b.trait_states.includes(k) && CARDS.includes(v)) : !(b.states[k] && b.states[k].includes(v))) throw new Error(`bad state ${k}=${v} on ${id}`);
    }
    resolveLog.push(id);
    return { id, states: { "minecraft:cardinal_direction": "south", "pw:snow": 0, ...states } };
  },
};
function world() {
  const m = new Map(), level = [];
  const key = (x, y, z) => `${x},${y},${z}`;
  const dim = { getBlock: ({ x, y, z }) => ({ get typeId() { return (m.get(key(x, y, z)) || { id: "minecraft:air" }).id; },
    setType(id) { m.set(key(x, y, z), { id, states: {} }); }, setPermutation(p) { m.set(key(x, y, z), { id: p.id, states: p.states }); } }) };
  return { m, dim, level, at: (x, y, z) => m.get(key(x, y, z)) || { id: "minecraft:air", states: {} } };
}
function layer(w) {
  const env = { plotBoxes: () => [], levelColumn: (dim, x, z, top, clear) => { w.level.push({ x, z, top, clear }); return top; }, sealWater: () => 0,
    groundAt: () => undefined, terraceFace: () => 0, wallColumn: () => 0, BlockPermutation, KIT, console };
  return new Function(...Object.keys(env), `${cutConst("DIRS4")}\n${cutConst("CARD4")}\n${cut("layRoadOp")}\nreturn layRoadOp;`)(...Object.values(env));
}
const DIRS4 = [[1, 0], [0, 1], [-1, 0], [0, -1]], CARD4 = ["east", "south", "west", "north"];
// a straight road record from a planned profile: cells from (x0, z0) along DIRS4[di]
function recOf(p, di, x0 = 0, z0 = 0, tuple = 3) {
  const d = DIRS4[di];
  const cells = p.H.map((_, i) => [x0 + d[0] * i, z0 + d[1] * i]);
  return { id: 1, cells, H: p.H.slice(), turns: [], dirs: cells.map(() => di), rampLen: KIT.ROAD_RAMP,
           ramps: p.segs.filter((q) => q.kind === "ramp").map((q) => (tuple === 3 ? [q.a, q.dir, q.len] : [q.a, q.dir])) };
}
const layAll = (rec, w) => { const lay = layer(w); for (let i = 0; i < rec.cells.length; i += 7) lay(w.dim, { buildings: [] }, { id: 1 }, rec, i, Math.min(7, rec.cells.length - i)); };
// what the road should carry at cell i: [id, cardinal] or null (a flat cell)
function expected(p, di) {
  const want = new Map();
  for (const q of p.segs.filter((s) => s.kind === "ramp")) {
    const up = q.dir > 0 ? di : (di + 2) % 4;
    if (q.len === 8) for (let k = 0; k < 8; k++) want.set(q.a + k, [`pw:ramp_cobble_8_e${q.dir > 0 ? k + 1 : 8 - k}`, CARD4[up]]);
    else for (let k = 0; k < 4; k++) want.set(q.dir > 0 ? q.a + k : q.a + (q.len - 4) + k, [`pw:ramp_cobble_4_q${q.dir > 0 ? k + 1 : 4 - k}`, CARD4[up]]);
  }
  return want;
}
function check(p, di, label, tuple = 3) {
  const w = world(), rec = recOf(p, di, 0, 0, tuple);
  layAll(rec, w);
  const want = expected(p, di), d = DIRS4[di], s = [-d[1], d[0]];
  const wrong = [];
  rec.cells.forEach(([x, z], i) => {
    const H = rec.H[i], e = want.get(i);
    for (let k = -2; k <= 2; k++) {
      const cx = x + s[0] * k, cz = z + s[1] * k, b = w.at(cx, H + 1, cz), deck = w.at(cx, H, cz);
      if (deck.id !== "minecraft:cobblestone") wrong.push([i, k, "deck", deck.id]);
      if (e ? (b.id !== e[0] || b.states["minecraft:cardinal_direction"] !== e[1]) : b.id !== "minecraft:air") wrong.push([i, k, b.id, b.states["minecraft:cardinal_direction"], e]);
    }
  });
  return { wrong, w, rec };
}
{
  const L = 72;
  const up = KIT.planProfile(slope(L, 1 / 12), roadOpts(L, 64, 64 + Math.floor((L - 1) / 12), true));
  const down = KIT.planProfile(slope(L, -1 / 12, 80), roadOpts(L, 80, 80 + Math.floor(-(L - 1) / 12), true));
  ok("stand-in: the profiles carry 8-part ramps up and down", lensOf(up).every((x) => x === 8) && lensOf(down).every((x) => x === 8) && lensOf(up).length >= 4 && lensOf(down).length >= 4, [lensOf(up), lensOf(down)]);
  for (const di of [0, 1, 2, 3]) {
    const a = check(up, di), b = check(down, di);
    ok(`layRoadOp, travel ${CARD4[di]}, climbing: every cell of an 8-ramp carries e1..e8 from the low end, facing uphill (${CARD4[di]}); flat cells none; cobble under all`, a.wrong.length === 0, a.wrong.slice(0, 4));
    ok(`layRoadOp, travel ${CARD4[di]}, descending: e8 at the high (first) end .. e1 at the low end, facing uphill (${CARD4[(di + 2) % 4]})`, b.wrong.length === 0, b.wrong.slice(0, 4));
  }
  // the walking SURFACE is continuous along the run (in eighths of a block): a flat cell is H + 1 at both edges; e_k climbs
  // from H + 1 + (k - 1)/8 to H + 1 + k/8 toward its uphill side, q_k from H + 1 + (k - 1)/4 to H + 1 + k/4 — every cell's far
  // edge meets the next cell's near edge (no step, no gap: the part index runs the right way along the run)
  const surface = (p, di) => {
    const want = expected(p, di), bad2 = [];
    const edges = p.H.map((H, i) => {
      const e = want.get(i), base = 8 * (H + 1);
      if (!e) return [base, base];
      const k = Number(e[0].slice(-1)), step = e[0].includes("_8_e") ? 1 : 2, upAlong = e[1] === CARD4[di];
      return upAlong ? [base + step * (k - 1), base + step * k] : [base + step * k, base + step * (k - 1)];
    });
    for (let i = 1; i < edges.length; i++) if (edges[i - 1][1] !== edges[i][0]) bad2.push([i, edges[i - 1], edges[i]]);
    return bad2;
  };
  ok("surface: continuous along the climbing road (every far edge = the next near edge)", surface(up, 0).length === 0, surface(up, 0).slice(0, 4));
  ok("surface: continuous along the descending road", surface(down, 2).length === 0, surface(down, 2).slice(0, 4));
  // HEADROOM (>= 2 everywhere): every ramp cell's column is levelled at its H with 3 cleared above (H + 1 .. H + 3): over
  // the full e8 (top H + 2) two blocks stay clear
  const { w, rec } = check(up, 0);
  const rampCells = new Set([...expected(up, 0).keys()].map((i) => `${rec.cells[i][0]},${rec.cells[i][1]}`));
  const lv = w.level.filter((c) => rampCells.has(`${c.x},${c.z}`));
  ok("headroom: every ramp cell levelled at its H, cleared 3 above (>= 2 free over the full e8)", lv.length === rampCells.size && lv.every((c) => c.clear >= 3 && c.top === rec.H[rec.cells.findIndex(([x, z]) => x === c.x && z === c.z)]), lv.slice(0, 3));
  ok("every ramp block went through BlockPermutation.resolve against the real table (ids + states valid)", resolveLog.length > 0 && resolveLog.every((id) => id.startsWith("pw:ramp_cobble_")), resolveLog.slice(0, 3));
  // the 4-part path is unchanged: a steep road (all 4-parts), and an OLD saved record ([a, dir] + rampLen 4) lays the same
  const L2 = 60, steepP = KIT.planProfile(slope(L2, 1 / 4), roadOpts(L2, 64, 74, false));
  const s3 = check(steepP, 1), s2 = check(steepP, 1, "old", 2);
  ok("4-part road (q1..q4 from the low end, facing uphill): unchanged", lensOf(steepP).every((x) => x === 4) && s3.wrong.length === 0, s3.wrong.slice(0, 4));
  ok("an old saved road record ([a, dir], rampLen 4) lays exactly as before", s2.wrong.length === 0 && JSON.stringify([...s2.w.m]) === JSON.stringify([...s3.w.m]), s2.wrong.slice(0, 4));
  // the old 7-cell gate-stub ramp ([a, dir], no rampLen): its 4 quarters at the low end (up) / the last 4 cells (down)
  const g7 = { H: Array(30).fill(70).map((h, i) => (i >= 10 && i < 17 ? (i < 14 ? 70 : 71) : i >= 17 ? 71 : 70)), segs: [{ kind: "flat", a: 0, len: 10, H: 70 }, { kind: "ramp", a: 10, len: 7, H: 70, dir: 1 }, { kind: "flat", a: 17, len: 13, H: 71 }] };
  const w7 = world(), rec7 = recOf(g7, 0, 0, 0, 2);
  delete rec7.rampLen;
  layAll(rec7, w7);
  ok("an old 7-cell ramp record (no rampLen) still lays q1..q4 on its first 4 cells", [10, 11, 12, 13].every((i, k) => w7.at(i, 71, 0).id === `pw:ramp_cobble_4_q${k + 1}`) && w7.at(14, 72, 0).id === "minecraft:air", [10, 11, 12, 13, 14].map((i) => w7.at(i, 71, 0).id));
  // a mixed road (1 in 6): every ramp laid by its own length
  const L3 = 100, mixP = KIT.planProfile(slope(L3, 1 / 6), roadOpts(L3, 64, 64 + Math.floor(99 / 6), true));
  const mx = check(mixP, 3);
  ok("mixed road (4- and 8-parts, travel north): every ramp laid by its own length", lensOf(mixP).includes(4) && lensOf(mixP).includes(8) && mx.wrong.length === 0, mx.wrong.slice(0, 4));
  ok("surface: continuous along the mixed road and the steep (4-part) road", surface(mixP, 3).length === 0 && surface(steepP, 1).length === 0, [surface(mixP, 3).slice(0, 3), surface(steepP, 1).slice(0, 3)]);
}

// ------------------------------------------------------------------------------------------------ 6. the witness list
// /scriptevent pw:clock roadramps — every narrow road's ramps (where each starts, 8-part or 4-part, which way it climbs);
// roadRampList cut from the clock and run on a planned road
{
  const env = { KIT };
  const list = new Function(...Object.keys(env), `${cutConst("DIRS4")}\n${cutConst("CARD4")}\n${cut("roadRampList")}\nreturn roadRampList;`)(...Object.values(env));
  const L = 72, p = KIT.planProfile(slope(L, 1 / 12), roadOpts(L, 64, 64 + Math.floor((L - 1) / 12), true));
  const rec = recOf(p, 1, 10, 20);
  const rows = list(rec);
  const rs = p.segs.filter((q) => q.kind === "ramp");
  ok("roadRampList: one row per ramp — its first cell along the road (x, y = the ramp row H + 1, z), its parts (8 / 4) and its uphill facing",
     rows.length === rs.length && rows.every((r, i) => r.x === 10 && r.z === 20 + rs[i].a && r.y === p.H[rs[i].a] + 1 && r.parts === (rs[i].len === 8 ? 8 : 4) && r.up === "south"), rows.slice(0, 3));
  const old = list({ ...rec, ramps: rec.ramps.map(([a, d]) => [a, d]), rampLen: 4 });
  ok("roadRampList: an old record ([a, dir], rampLen 4) lists 4-part ramps", old.length === rs.length && old.every((r) => r.parts === 4));
  ok("clock: /scriptevent pw:clock roadramps is wired, and the bench road's chronicle line counts its 8-part / 4-part ramps",
     /if \(cmd === "roadramps"\)/.test(src) && /roadRampList\(r\)/.test(src) && /8-part ramp/.test(src.slice(src.indexOf("function commitBench("), src.indexOf("function commitBench(") + 3000)));
}

console.log(`test_roadramp8: ${n - bad}/${n} passed`);
if (bad) process.exitCode = 1;
