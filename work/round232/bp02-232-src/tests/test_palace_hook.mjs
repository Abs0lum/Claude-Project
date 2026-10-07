// test_palace_hook.mjs — 1.3.232 (#21): the PALACE II hook (HOOK-PROPOSAL.diff Parts A-C) in pw_civ_clock.js + the court.
// Covered: the two palace models (4 x 4 PALACE II, 2 x 2 kept for saved worlds and as the fallback), the 4 x 4 grid
// permutation == the whole model rotated (rotXZ) at 0/90/180/270, the per-palace span (a saved 2 x 2 palace keeps 128),
// FAIL SAFE: a missing table entry / stage structure -> the 2 x 2 palace + one [CIV-PALACE] line (pack list, get()
// fallback, a throwing engine, the real table of this source), a reserve / survey of the other model starts again, the
// survey QUARTER by quarter (identical verdict to the one-box measure; completes with ONE held area at a time — the
// proposal's whole-box hold never does), the court beds (old + new keys), >= 2 lord beds filled and kept.
import * as C from "../pw_civ_clock.js";
import * as COURT from "../pw_civ_court.js";
import { PALACE_BEDS, PALACE_BEDS_1, PALACE_BEDS_2 } from "../pw_civ_court_data.js";
import { CIV_BUILDINGS } from "../pw_civ_buildings.js";

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);

// ---- the models
const M2 = C.PALACE_MODELS[2], M4 = C.PALACE_MODELS[4];
eq(M2.pieces, ["sw", "se", "nw", "ne"], "the 2 x 2 palace keeps its pieces (saved worlds)");
eq(M2.family("sw"), "pw:mvv_palace_sw_a_r1", "2 x 2 family");
eq(M4.pieces, ["00", "01", "02", "03", "10", "11", "12", "13", "20", "21", "22", "23", "30", "31", "32", "33"], "PALACE II: 16 pieces rc (r = depth from the gate, c = frontage)");
eq(M4.family("21"), "pw:mvv_palace2_21_a_r1", "PALACE II family (HOOK-PROPOSAL Part A)");
eq([M2.R, M4.R], [[110, 320], [180, 440]], "survey rings: 110..320 (2 x 2) / 180..440 (PALACE II: centre >= the half-diagonal 181 out)");
eq([M4.grid["00"], M4.grid["21"], M4.grid["33"]], [[0, 0], [2, 1], [3, 3]], "PALACE II grid [i, j] = [r, c]");

// ---- the grid permutation + each piece rotated in place == the whole model rotated rigidly, both models, every rotation
for (const n of [2, 4]) for (let r = 0; r < 4; r++) {
  const S = 64 * n;
  let bad = 0;
  for (let x = 0; x < S; x += 7) for (let z = 0; z < S; z += 5) {
    const i = Math.floor(x / 64), j = Math.floor(z / 64);
    const [gi, gj] = C.palaceGridRot(i, j, r, n);
    const [lx, lz] = C.rotXZ(x - i * 64, z - j * 64, 64, 64, r);
    const [wx, wz] = C.rotXZ(x, z, S, S, r);
    if (gi * 64 + lx !== wx || gj * 64 + lz !== wz) bad++;
  }
  ok(bad === 0, `n ${n} rot ${r}: pieces placed like the whole model rotated (${bad} cells differ)`);
}
eq(C.palaceGridRot(1, 0, 1), [1, 1], "palaceGridRot without n keeps the 2 x 2 law (1 - j, i)");

// ---- the span is the PALACE's own (a saved world's 2 x 2 palace has no n: 128 — its walls, centre and reserve stay)
eq(C.palaceSpanOf({ x0: 0, z0: 0 }), 128, "legacy palace record: 128");
eq(C.palaceSpanOf({ n: 4 }), 256, "PALACE II: 256");
eq(C.palaceBox({ x0: 10, z0: 20 }), [10, 20, 137, 147], "legacy wall box (palaceWallJob) unchanged: x0 + 127");
eq(C.palaceBox({ x0: 10, z0: 20, n: 4 }), [10, 20, 265, 275], "PALACE II wall box: x0 + 255");
eq(C.palaceCentre({ x0: 10, z0: 20 }), [74, 84], "legacy centre +64 (status line)");
eq(C.palaceCentre({ x0: 10, z0: 20, n: 4 }), [138, 148], "PALACE II centre +128");
eq(C.palaceReserveBox({ x0: 10, z0: 20 }), [8, 139, 18, 149], "legacy reserve box (+2): x0 - 2 .. x0 + 129");
eq(C.palaceReserveBox({ x0: 10, z0: 20, n: 4 }), [8, 267, 18, 277], "PALACE II reserve box: x0 - 2 .. x0 + 257");
eq(C.palaceReserveFits({ x0: 1 }, 2), true, "a legacy reserve fits the 2 x 2 palace");
eq(C.palaceReserveFits({ x0: 1 }, 4), false, "a legacy 128 reserve does NOT fit PALACE II (the surveyors look again)");
eq(C.palaceReserveFits({ x0: 1, n: 4 }, 4), true, "a PALACE II reserve fits PALACE II");
eq(C.palacePieceLabel("sw"), "sw quarter", "the 2 x 2 stage log keeps 'quarter'");
eq(C.palacePieceLabel("21"), "piece 21 (row 2 from the gate)", "PALACE II stage log (HOOK-PROPOSAL hunk 1)");

// ---- FAIL SAFE: what the build must include, and the check
const stems = M4.pieces.map((q) => `mvv_palace2_${q}_a_r1`);
const fullDefs = Object.fromEntries(M4.pieces.map((q) => [M4.family(q), { stem: `mvv_palace2_${q}_a_r1`, size: [64, 50, 64], datum_y: 15, stages: 5 }]));
const allIds = ["pw:stages/mvv_palace_sw_a_r1_s0", ...stems.flatMap((s) => [0, 1, 2, 3, 4].map((k) => `pw:stages/${s}_s${k}`))];
eq(C.palaceRequiredStructures(4).length, 80, "PALACE II needs 80 stage structures (16 pieces x s0..s4)");
eq(C.palaceRequiredStructures(4)[0], "pw:stages/mvv_palace2_00_a_r1_s0", "ids as placeStage places them");
eq(C.palaceMissing(M4, fullDefs, () => true), [], "everything present: nothing missing");
eq(C.palaceMissing(M4, {}, () => true).length, 16, "no table entries (Part C not merged): all 16 pieces missing");
{
  const miss = C.palaceMissing(M4, fullDefs, (id) => !id.startsWith("pw:stages/mvv_palace2_21_a_r1_"));
  eq(miss, [{ q: "21", what: ["s0", "s1", "s2", "s3", "s4"] }], "one piece's structures missing -> that piece");
  eq(C.palaceMissing(M4, fullDefs, (id) => id !== "pw:stages/mvv_palace2_33_a_r1_s4"), [{ q: "33", what: ["s4"] }], "one stage missing -> named");
}
const fakeSm = (ids, opts = {}) => ({
  getPackStructureIds: opts.noList ? undefined : () => { if (opts.listThrows) throw new Error("not allowed in early execution"); return ids.slice(); },
  get: (id) => { if (opts.getThrows) throw new Error("boom"); return ids.includes(id) ? { id } : undefined; },
});
{
  const logs = [];
  const r = C.checkPalaceII(fakeSm(allIds), fullDefs, (l) => logs.push(l));
  ok(r.ok && r.n === 4 && r.how === "pack list", `complete pack: PALACE II (${r.how})`);
  ok(logs.length === 1 && logs[0].startsWith("[CIV-PALACE]") && logs[0].includes("4 x 4"), `one [CIV-PALACE] line: ${logs[0]}`);
}
{
  const logs = [];
  const r = C.checkPalaceII(fakeSm(allIds.filter((id) => !id.includes("_21_"))), fullDefs, (l) => logs.push(l));
  ok(!r.ok && r.n === 2 && r.missing.length === 1 && r.missing[0].q === "21", "piece 21 missing from the pack: the 2 x 2 palace");
  ok(logs.length === 1 && /^\[CIV-PALACE\] PALACE II is not complete/.test(logs[0]) && logs[0].includes("21") && logs[0].includes("2 x 2"), `fallback line: ${logs[0]}`);
}
{
  const r = C.checkPalaceII(fakeSm([], {}), fullDefs, () => {});
  ok(!r.ok && r.missing.length === 16, "an empty pack list (no palace files at all): the 2 x 2 palace");
}
{
  // the pack list's id form not confirmed (the 2 x 2 palace's own s0 is not in it) -> get() per piece (s0 and s4)
  const r = C.checkPalaceII(fakeSm(allIds.filter((id) => !id.includes("mvv_palace_sw")), {}), fullDefs, () => {});
  ok(r.ok && r.how === "get", `unconfirmed list form -> get(): ${r.how}`);
  const r2 = C.checkPalaceII(fakeSm(allIds, { noList: true }), fullDefs, () => {});
  ok(r2.ok && r2.how === "get", "no getPackStructureIds (older engine): get()");
  const r3 = C.checkPalaceII(fakeSm(allIds.filter((id) => id !== "pw:stages/mvv_palace2_12_a_r1_s0"), { noList: true }), fullDefs, () => {});
  ok(!r3.ok && r3.missing.some((m) => m.q === "12"), "get() finds a missing piece");
  const r4 = C.checkPalaceII(fakeSm(allIds, { listThrows: true, getThrows: true }), fullDefs, () => {});
  ok(!r4.ok && r4.n === 2, "a throwing engine: no crash, the 2 x 2 palace");
  const r5 = C.checkPalaceII(undefined, fullDefs, () => {});
  ok(!r5.ok && r5.n === 2, "no structure manager at all: the 2 x 2 palace");
}
{
  // THIS source's real table (Part C's 16 entries are generated in the cloud workspace, not in this repo): fail safe
  const logs = [];
  const r = C.checkPalaceII(fakeSm(allIds), CIV_BUILDINGS, (l) => logs.push(l));
  const has = M4.pieces.every((q) => CIV_BUILDINGS[M4.family(q)]);
  ok(has ? r.ok : (!r.ok && r.missing.length === 16 && logs[0].includes("table")), `real CIV_BUILDINGS (palace2 entries ${has ? "present" : "absent"}): ${has ? "PALACE II" : "fallback"}`);
  ok(M2.pieces.every((q) => CIV_BUILDINGS[M2.family(q)]), "the 2 x 2 palace's 4 entries stay in the table (saved worlds, fallback)");
}
{
  // the session check through the engine stand-in (no structures, no palace2 entries): 2, said ONCE
  const was = console.warn, seen = [];
  console.warn = (l) => seen.push(String(l));
  try { C.__resetPalaceCheck(); const a = C.palaceModelNow(), b = C.palaceModelNow(); ok(a === 2 && b === 2, "the session's model: 2 x 2 (fallback)"); }
  finally { console.warn = was; }
  eq(seen.filter((l) => l.startsWith("[CIV-PALACE]")).length, 1, "the [CIV-PALACE] line is written once a session");
}

// ---- the survey, QUARTER by quarter
eq(C.PALACE_QSPAN, 128, "a quarter is 128 x 128");
eq(C.palaceQuarters(128), [[0, 0]], "the 2 x 2 palace: one quarter (the old single box)");
eq(C.palaceQuarters(256), [[0, 0], [0, 128], [128, 0], [128, 128]], "PALACE II: four quarters");
eq(C.palaceQuarterBox(1000, 2000, [0, 0]), [992, 1992, 1135, 2135], "the 2 x 2 hold box = the old one (x0 - 8 .. x0 + 135)");
eq(C.palaceQuarterBox(1000, 2000, [128, 128]), [1120, 2120, 1263, 2263], "PALACE II far quarter + 8 out");
for (let a = 0; a < 16; a++) {   // any alignment: a 144-cell box spans <= 10 chunks (the engine's ticking-area cap)
  const [x0, , x1] = C.palaceQuarterBox(a, 0, [128, 0]);
  ok(Math.floor(x1 / 16) - Math.floor(x0 / 16) + 1 <= 10, `quarter box at alignment ${a}: <= 10 chunks`);
}
// a synthetic land (deterministic): ground, water, outside lakes, ice
function land(seed) {
  let s = seed >>> 0;
  const rnd = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  const g = new Map(), o = new Map(), w = new Map();
  const at = (m, x, z, f) => { const k = `${x},${z}`; if (!m.has(k)) m.set(k, f()); return m.get(k); };
  return {
    ground: (x, z) => at(g, x, z, () => ({ g: 60 + Math.floor(rnd() * 20), wet: rnd() < 0.05 })),
    outside: (x, z) => at(o, x, z, () => ({ w: rnd() < 0.2 ? 60 + Math.floor(rnd() * 25) : -999, t: 55 + Math.floor(rnd() * 40) })),
    inner: (x, z) => at(w, x, z, () => ({ wy: rnd() < 0.1 ? 60 + Math.floor(rnd() * 25) : null })),
  };
}
// the reference: the ONE-BOX measure exactly as HOOK-PROPOSAL Part A wrote it (ground every 16, 4 x (span/16 + 1) outside
// samples 8 out, the inner wet grid from 8), on the same reads
function reference(x0, z0, span, L) {
  const hs = []; let wet = 0;
  for (let i = 0; i < span; i += 16) for (let j = 0; j < span; j += 16) { const r = L.ground(x0 + i, z0 + j); if (r.wet) wet++; hs.push(r.g); }
  const srt = hs.slice().sort((p, q) => p - q), H = srt[Math.floor(srt.length / 2)] + 1;
  let outsideWet = 0, bowl = 0, wetIn = 0;
  const PER = span / 16 + 1;
  for (let k = 0; k < PER * 4; k++) {
    const t = k % PER, side = Math.floor(k / PER) % 4, far = 8;
    const sx2 = side === 0 ? x0 - far : side === 1 ? x0 + span - 1 + far : x0 + t * 16, sz2 = side === 2 ? z0 - far : side === 3 ? z0 + span - 1 + far : z0 + t * 16;
    const r = L.outside(sx2, sz2); if (r.w >= H - 1) outsideWet++; if (r.t >= H + 16) bowl++;
  }
  for (let i = 8; i < span; i += 16) for (let j = 8; j < span; j += 16) { const r = L.inner(x0 + i, z0 + j); if (r.wy !== null && r.wy >= H - 1) wetIn++; }
  return { relief: Math.max(...hs) - Math.min(...hs), H, wet, outsideWet, bowl, wetIn };
}
for (const span of [128, 256]) for (const seed of [1, 7, 42, 99]) {
  const L = land(seed), part = { key: "k", q: {} };
  const m = C.palaceMeasure(part, 5000, -3000, span, L);
  ok(m.done && m.need === null, `span ${span} seed ${seed}: all loaded -> measured in one call`);
  const v = C.palaceVerdict(part), r = reference(5000, -3000, span, L);
  eq([v.relief, v.H, v.wet, v.outsideWet, v.bowl, v.wetIn], [r.relief, r.H, r.wet, r.outsideWet, r.bowl, r.wetIn], `span ${span} seed ${seed}: the quartered verdict == the one-box measure`);
  ok(v.samples === (span / 16) ** 2 * 2 + (span / 16 + 1) * 4, `span ${span}: every sample read once (${v.samples})`);
}
// LIVENESS: a sleeping site, ONE ticking area at a time (the town core holds a slot; the default is 4 slots; the area held
// yesterday may be released for other work) — the quartered survey completes; the proposal's whole-box test never does
for (const span of [128, 256]) {
  const L = land(3), x0 = 7000, z0 = 7000;
  let held = null, days = 0, done = false;
  const part = { key: "k", q: {} };
  const inBox = (b, x, z) => b && x >= b[0] && x <= b[2] && z >= b[1] && z <= b[3];
  const gate = (f) => (x, z) => (inBox(held, x, z) ? f(x, z) : undefined);
  const rd = { ground: gate(L.ground), outside: gate(L.outside), inner: gate(L.inner) };
  let maxHeld = 0;
  while (!done && days < 20) {
    days++;
    const m = C.palaceMeasure(part, x0, z0, span, rd);
    if (m.done) { done = true; break; }
    held = C.palaceQuarterBox(x0, z0, m.need);                 // the surveyors hold ONE quarter (what one area can wake)
    maxHeld = 1;
  }
  ok(done && days === (span / 128) ** 2 + 1 && maxHeld <= 1, `span ${span}: measured in ${days} days holding one area at a time`);
  // the one-box rule (HOOK-PROPOSAL: a candidate is measured only when ALL its samples read in one day) under the same
  // one-area condition: never for 256 (a quarter's area can never wake the other three)
  let held2 = null, days2 = 0, done2 = false;
  while (!done2 && days2 < 20) {
    days2++;
    const g2 = (f) => (x, z) => (inBox(held2, x, z) ? f(x, z) : undefined);
    const p2 = { key: "k", q: {} };
    const m2 = C.palaceMeasure(p2, x0, z0, span, { ground: g2(L.ground), outside: g2(L.outside), inner: g2(L.inner) });
    if (m2.done) { done2 = true; break; }
    held2 = C.palaceQuarterBox(x0, z0, m2.need);
  }
  ok(span === 256 ? !done2 : done2, `span ${span}: the whole-box rule with one area ${done2 ? "completes" : "never completes"} (why the survey is quartered)`);
}
// the day's BUDGET: PALACE_PER_DAY (2) quarters a day — a 2 x 2 site is one quarter (2 sites a day, as before 1.3.232)
{
  const L = land(11), part = { key: "k", q: {} };
  const m1 = C.palaceMeasure(part, 0, 0, 256, L, 2);
  ok(!m1.done && m1.budget && m1.stored === 2 && m1.need === null, "a loaded 256 site: 2 quarters today (the budget), not asleep");
  const m2 = C.palaceMeasure(part, 0, 0, 256, L, 2);
  ok(m2.done && m2.stored === 2, "the other 2 tomorrow: judged");
  const p2 = { key: "k", q: {} };
  ok(C.palaceMeasure(p2, 0, 0, 128, L, 2).done, "a 2 x 2 site is one quarter: judged within the budget");
}
// THE REAL SURVEY (palaceSite) on a flat world whose chunks load only inside the ticking areas the clock asks for (2 slots:
// the town keeps the others) — a sleeping PALACE II site is measured quarter by quarter and accepted; never more than the
// slots; every day reads at most 2 quarters' worth; the 2 x 2 site is accepted on day 2 as before
function surveyRun(n, slots) {
  const st = { id: 1, dim: "overworld", square: { x: 0, z: 0, y: 63 }, log: [], tier: "town3" };
  const s = { settlements: [st], buildings: [], simDays: 0, tick: { slots, areas: {}, next: 1 } };
  const home = [-48, -48, 60, 60];
  const inBox = (b, x, z) => x >= b[0] && x <= b[2] && z >= b[1] && z <= b[3];
  const loaded = (x, z) => inBox(home, x, z) || Object.values(s.tick.areas).some((a) => inBox(a.box, x, z));
  let reads = 0;
  const dim = {
    isChunkLoaded: ({ x, z }) => loaded(x, z),
    getTopmostBlock: ({ x, z }) => { reads++; if (!loaded(x, z)) throw new Error("unloaded"); return { typeId: "minecraft:grass_block", location: { x, y: 63, z }, isValid: true }; },
    getBlock: ({ x, y, z }) => { if (!loaded(x, z)) throw new Error("unloaded"); return { typeId: y <= 63 ? "minecraft:grass_block" : "minecraft:air", location: { x, y, z }, isValid: true }; },
  };
  const was = console.warn; console.warn = () => {};
  let site = null, day = 0, maxAreas = 0, maxReads = 0;
  try {
    while (!site && day < 40) { day++; s.simDays = day; reads = 0; site = C.palaceSite(s, st, dim, n); maxAreas = Math.max(maxAreas, Object.keys(s.tick.areas).length); maxReads = Math.max(maxReads, reads); }
  } finally { console.warn = was; }
  return { site, day, maxAreas, maxReads, st };
}
{
  const r = surveyRun(4, 2);
  ok(r.site && r.site.n === 4 && r.site.relief === 0, `PALACE II: a sleeping flat site is accepted (day ${r.day})`);
  ok(r.day <= 6 && r.maxAreas <= 2, `within 6 days holding at most the 2 slots (day ${r.day}, areas ${r.maxAreas})`);
  ok(r.maxReads <= 2 * 210, `at most 2 quarters' reads a day (${r.maxReads} topmost reads; one PALACE II quarter = 210)`);
  ok(!(r.st.palaceSurvey.parts || {})[`${r.site.x0},${r.site.z0}`], "the judged site keeps no partial record");
  const r2 = surveyRun(2, 2);
  ok(r2.site && r2.site.n === 2 && r2.day === 2, `the 2 x 2 palace: accepted on day ${r2.day} (as before: wake, then measure)`);
  // a 2 x 2 survey in a save (no n) is started again for PALACE II; a PALACE II survey goes on
  const st = { id: 1, dim: "overworld", square: { x: 0, z: 0, y: 63 }, log: [], palaceSurvey: { tried: { "1,1": 3 }, best: null, days: 9, loaded: 4 } };
  const s = { settlements: [st], buildings: [], simDays: 10, tick: { slots: 2, areas: {}, next: 1 } };
  const dim0 = { isChunkLoaded: () => false, getTopmostBlock: () => { throw new Error("x"); }, getBlock: () => { throw new Error("x"); } };
  const was = console.warn; console.warn = () => {};
  try { C.palaceSite(s, st, dim0, 4); } finally { console.warn = was; }
  ok(st.palaceSurvey.n === 4 && st.palaceSurvey.days === 1 && !st.palaceSurvey.tried["1,1"], "a saved 2 x 2 survey starts again for PALACE II");
  ok(st.log.some((l) => l.includes("start again") && l.includes("256 x 256")), "and the chronicle says so");
}
// a partial measure keeps what it read: a quarter that reads asleep halfway is not stored
{
  const L = land(5), part = { key: "k", q: {} };
  let n = 0;
  const flaky = { ground: (x, z) => (++n === 70 ? undefined : L.ground(x, z)), outside: L.outside, inner: L.inner };
  const m = C.palaceMeasure(part, 0, 0, 256, flaky);
  ok(!m.done && m.need !== null && Object.keys(part.q).length < 4, `a quarter with a sleeping read is not kept (stored ${Object.keys(part.q).length}, need ${m.need})`);
  const m2 = C.palaceMeasure(part, 0, 0, 256, L);
  ok(m2.done, "the next day reads only the quarters it lacks");
}

// ---- the court beds: the 2 x 2 table unchanged (saved worlds) + PALACE II keyed "00".."33"
eq(Object.keys(PALACE_BEDS_1).sort(), ["ne", "nw", "se", "sw"], "the 2 x 2 table (tools/palace_beds.py) kept");
eq(Object.keys(PALACE_BEDS_2).sort(), M4.pieces, "PALACE II beds keyed 00..33 (Part B)");
eq(Object.keys(PALACE_BEDS).length, 20, "PALACE_BEDS = both (20 keys, none shared)");
const tot = (T) => { const o = {}; for (const b of Object.values(T)) for (const [k, v] of Object.entries(b)) o[k] = (o[k] || 0) + v; return Object.fromEntries(Object.entries(o).sort()); };
eq(tot(PALACE_BEDS_2), { cell: 8, child: 36, clerk: 12, guard: 26, lord: 2, noble: 16, servant: 201 }, "PALACE II bed roles (palace2_hookdata.py output)");
eq([COURT.bedsOfPiece("21").lord, COURT.bedsOfPiece("22").lord], [1, 1], "the 2 lord beds: pieces 21 and 22 (D-GH1007-LORDBEDS: at least 2)");
eq(COURT.bedsOfPiece("ne").lord, 1, "a saved 2 x 2 palace keeps its lord's bed (ne)");
ok(COURT.bedsOfPiece("10").cell === undefined && COURT.bedsOfPiece("03").child === undefined, "cells and children's beds are never role slots");

// ---- >= 2 lord beds through the court plan: every free lord bed is filled in one pass, each household its own piece, kept
{
  let nid = 1;
  const P = { list: [] };
  const mk = (o) => { const p = { id: nid++, alive: true, born: 0, spouse: null, kids: [], home: 100, job: null, trade: null, skill: {}, ...o }; P.list.push(p); return p; };
  const byId = (P2, id) => P2.list.find((p) => p.id === id);
  const f = {
    stage: (p) => (p.child ? "child" : "adult"),
    household: (p) => { const out = [p]; const sp = p.spouse ? byId(P, p.spouse) : null; if (sp && sp.alive && sp.home === p.home) out.push(sp); for (const k of p.kids) { const c = byId(P, k); if (c && c.alive && c.home === p.home && c.child) out.push(c); } return out; },
    districtOf: () => null, homeKind: () => "cottage_m", tradeOf: (p) => p.trade, dead: (id) => { const q = byId(P, id); return !q || !q.alive; },
  };
  const couple = (skill, home) => { const a = mk({ skill: { smithy: skill }, home }), b = mk({ home }); a.spouse = b.id; b.spouse = a.id; return [a, b]; };
  const [a1, a2] = couple(90, 101), [b1, b2] = couple(80, 102), [c1] = couple(70, 103);
  const pieces = M4.pieces.map((q, k) => ({ id: 600 + k, q }));                 // placePalace creates them 00..33 in order
  const id21 = pieces.find((p) => p.q === "21").id, id22 = pieces.find((p) => p.q === "22").id;
  const plan = COURT.courtPlan(pieces, P.list, f);
  const at = (p) => plan.admit.find((x) => x.pid === p.id);
  eq([at(a1) && at(a1).r, at(a2) && at(a2).r, at(b1) && at(b1).r, at(b2) && at(b2).r], ["lord", "lord", "lord", "lord"], "the two top couples both take a lord's bed in ONE pass");
  eq([at(a1).b, at(b1).b], [id21, id22], "each to his own piece: the top family to 21 (the lord's state bedchamber), the next to 22 (the consort's)");
  eq(at(c1) && at(c1).r, "noble", "the third family: an apartment of state");
  eq(plan.held.lord, 2, "2 lord beds held");
  COURT.applyCourt(plan, P, byId, () => true);
  eq([a1.home, a2.home, b1.home, b2.home], [id21, id21, id22, id22], "their homes are their own pieces (the night place the schedule sends them to)");
  const again = COURT.courtPlan(pieces, P.list, f);
  ok(!again.release.length && !again.admit.some((x) => x.r === "lord"), "the next day: both lords keep their beds (stable)");
  // the saved 2 x 2 palace: one lord bed -> one lord household (unchanged)
  P.list.forEach((p) => { delete p.court; });
  const old = COURT.courtPlan([{ id: 1, q: "sw" }, { id: 2, q: "se" }, { id: 3, q: "nw" }, { id: 4, q: "ne" }], P.list, f);
  eq(old.admit.filter((x) => x.r === "lord").map((x) => x.pid).sort(), [a1.id, a2.id].sort(), "the 2 x 2 palace: one lord household, as before");
}

console.log(`test_palace_hook: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
