// test_landclock.mjs — 1.3.231 (CIV-LAND): the clock's wiring of the wide survey and the terrace (band) streets, cut from
// pw_civ_clock.js and run on stand-ins (the engine is not here), plus the legJob mouth fix. Usage: node tests/test_landclock.mjs
import * as LAND from "../pw_civ_land.js";
import * as KIT from "../pw_civ_streets.js";
import { readFileSync } from "node:fs";
let n = 0, bad = 0;
const ok = (name, cond, info) => { n++; if (!cond) bad++; console.log(`${cond ? "PASS" : "FAIL"} ${n} ${name}${cond ? "" : " — " + JSON.stringify(info).slice(0, 400)}`); };
const src = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
const cut = (name) => {
  let i = src.indexOf(`\nfunction ${name}(`);
  if (i < 0) i = src.indexOf(`\nfunction* ${name}(`);
  if (i < 0) i = src.indexOf(`\nexport function ${name}(`);
  if (i < 0) throw new Error(`no function ${name}`);
  i = src.indexOf("function", i);
  let k = src.indexOf("{", src.indexOf(")", i)), depth = 0, j = k;
  for (; j < src.length; j++) { if (src[j] === "{") depth++; else if (src[j] === "}" && --depth === 0) break; }
  return src.slice(i, j + 1);
};
const constOf = (name) => { const m = src.match(new RegExp(`\\nconst ${name} = [\\s\\S]*?;[ \\t]*(//[^\\n]*)?\\n`)); if (!m) throw new Error(`no const ${name}`); return m[0]; };

// ------------------------------------------------------------------------------------------------ 1. source facts
ok("legJob takes its mouths from KIT.bandMouths (the arrival heads INTO the parallel)", /function\* legJob[\s\S]{0,1400}KIT\.bandMouths\(f, tj, side, other\.f, tOther\)/.test(src) && !/d1 = \[-side \* f\.vx, -side \* f\.vz\]/.test(src));
ok("sideStreetJob tries a band street when no parallel (or only a trench) is found", /const trench = !!best && landH !== undefined[\s\S]{0,600}KIT\.planBandStreetJob\(lsite, f, tj, side, Hb, D, veto\.street, veto\.leg, STREET_OPTS, why\)/.test(src));
ok("the site field is written as d1 and read either way", src.includes("saveSite(st.id, LAND.siteEncode(site))") && src.includes("LAND.siteDecode(JSON.parse(txt))"));
ok("the room heartbeat starts the wide survey", /HB\.register\("room"[\s\S]{0,400}startWideSurvey\(s, st\)/.test(src));

// ------------------------------------------------------------------------------------------------ 2. the wide survey, end to end on a fake world
{
  // a world: ground y = 70 + (x + z) / 32; a lake (water 3 deep over a bed at 60) in a disc; leaves over some columns;
  // chunks inside |x|,|z| < 100 always loaded, the rest only while a ticking area holds them (they load one pause later)
  const cx = 0, cz = 0;
  const lake = (x, z) => Math.hypot(x - 150, z + 40) < 20;
  const tree = (x, z) => (x * 31 + z * 17) % 53 === 0;
  const areas = new Map();            // name -> { box, age }
  const awake = (x, z) => (Math.abs(x) < 100 && Math.abs(z) < 100) || [...areas.values()].some((a) => a.age >= 1 && x >= a.box[0] && x <= a.box[2] && z >= a.box[1] && z <= a.box[3]);
  const g0 = (x, z) => 70 + Math.floor((x + z) / 32);
  const block = (x, y, z) => {
    if (lake(x, z)) return y > 63 ? null : y >= 61 ? "minecraft:water" : y === 60 ? "minecraft:sand" : "minecraft:stone";
    const g = g0(x, z);
    if (tree(x, z)) { if (y > g + 5) return null; if (y > g + 2) return "minecraft:oak_leaves"; if (y > g) return "minecraft:oak_log"; }
    if (y > g) return null;
    return y === g ? "minecraft:grass_block" : "minecraft:dirt";
  };
  const mk = (x, y, z) => { const id = block(x, y, z); return id ? { typeId: id, isValid: true, location: { x, y, z } } : { typeId: "minecraft:air", isValid: true, location: { x, y, z } }; };
  let reads = 0;
  const dim = {
    id: "overworld",
    isChunkLoaded: ({ x, z }) => awake(x, z),
    getBlock: ({ x, y, z }) => { reads++; return mk(x, y, z); },
    getTopmostBlock: ({ x, z }) => { reads++; for (let y = 100; y > -64; y--) { const id = block(x, y, z); if (id) return mk(x, y, z); } return undefined; },
  };
  const jobs = [], timeouts = [];
  const system = { runJob: (g) => jobs.push(g), runTimeout: (fn, t) => timeouts.push(fn) };
  const world = { getDimension: () => dim };
  // the settlement: a founding field of 160 x 160 (read), a village ring
  const core = LAND.makeSite(-80, -80, 160, 160);
  for (let x = -80; x < 80; x++) for (let z = -80; z < 80; z++) core.set(x, z, g0(x, z), false);
  const st = { id: 1, kit: true, phase: "built", square: { x: -6, z: -6 }, border: { r: 64 }, log: [], dim: "overworld" };
  const siteCache = new Map([[1, core]]);
  const saved = [];
  const T = { slots: 4, areas: {}, next: 1 };
  const S = { simDays: 50, settlements: [st] };
  const env = {
    LAND, world, system, ENGINE: { throws: 0 }, siteCache,
    siteOf: (x) => siteCache.get(x.id), squareCentre: (x) => [x.square.x + 6, x.square.z + 6],
    load: () => S, save: () => {}, saveSite: (id, r) => saved.push([id, r]), coreState: () => T,
    ensureTicking: (s, x, box, why) => { const name = `civ${T.next++}`; T.areas[name] = { name, box: [box[0], box[1], box[2], box[3]] }; areas.set(name, { box, age: 0 }); return name; },
    releaseTicking: (s, name) => { delete T.areas[name]; areas.delete(name); },
  };
  const fnSrc = [constOf("NOT_GROUND"), cut("isGround"), cut("blockAt"), cut("boxLoaded"), cut("topAt"), "const WIDE_PAUSE = 100; const wideJobs = new Map();",
    cut("siteColumn"), cut("wideNeed"), cut("startWideSurvey"), cut("wideDone"), "return { siteColumn, wideNeed, startWideSurvey, wideJobs };"].join("\n");
  const C = new Function(...Object.keys(env), fnSrc)(...Object.values(env));
  // the column reader: under trees the ground; in the lake the bed with the water flag
  { let tx = 0, tz = 0; for (let x = 1; x < 99; x++) if (tree(x, 7)) { tx = x; tz = 7; break; }
    const c = C.siteColumn(dim, tx, tz); ok("siteColumn: a tree column reads the grass under the trunk, dry", c && c.g === g0(tx, tz) && !c.water, { tx, c, g: g0(tx, tz) }); }
  ok("wideNeed: a village with a 160 field needs 192", C.wideNeed(S, st) === 192, C.wideNeed(S, st));
  ok("startWideSurvey: started, one at a time", C.startWideSurvey(S, st) === true && C.startWideSurvey(S, st) === false && C.wideJobs.size === 1);
  // run: jobs to completion; each timeout = a pause (held areas age, so their chunks load)
  let guard = 0;
  while ((jobs.length || timeouts.length) && guard++ < 2000) {
    while (jobs.length) { const g = jobs.shift(); let r = g.next(); while (!r.done) r = g.next(); }
    if (timeouts.length) { for (const a of areas.values()) a.age++; timeouts.shift()(); }
  }
  const site = siteCache.get(1);
  ok("the survey finished and the field was replaced in one step (384 x 384)", C.wideJobs.size === 0 && site !== core && site.w === 384 && site.d === 384, { jobs: C.wideJobs.size, w: site.w });
  ok("st.wide records it (R 192, no tile skipped)", st.wide && st.wide.R === 192 && st.wide.skipped === 0, st.wide);
  ok("every ticking area it took was released", areas.size === 0 && Object.keys(T.areas).length === 0, [...areas.keys()]);
  let wrong = 0, unknown = 0;
  for (let x = -192; x < 192; x += 3) for (let z = -192; z < 192; z += 3) {
    const v = site.at(x, z);
    if (v === undefined) { unknown++; continue; }
    const want = lake(x, z) ? 60 : g0(x, z);
    if (v !== want || site.isWater(x, z) !== lake(x, z)) wrong++;
  }
  ok("the far land is read right: the ground under trees, the lake's bed + water", wrong === 0 && unknown === 0, { wrong, unknown });
  ok("the founding's cells are the founding's (kept, never read again)", site.at(10, 10) === core.at(10, 10));
  ok("saved once, as d1 text, and it decodes to the same field", saved.length === 1 && saved[0][1].enc === "d1" && LAND.siteDecode(saved[0][1]).at(150, -40) === 60);
  ok("nothing more to survey now", C.wideNeed(S, st) === 0);
  st.border.r = 176;
  ok("the stones move out to 176: the survey is wanted again at 272", C.wideNeed(S, st) === 272, C.wideNeed(S, st));
  // no free ticking slot: the survey waits and never evicts the town's areas
  T.slots = 0;
  ok("no free slot: started, it waits (no area taken)", C.startWideSurvey(S, st) === true);
  for (let k = 0; k < 5 && (jobs.length || timeouts.length); k++) { while (jobs.length) { const g = jobs.shift(); let r = g.next(); while (!r.done) r = g.next(); } if (timeouts.length) timeouts.shift()(); }
  ok("no free slot: no ticking area taken", Object.keys(T.areas).length === 0 && areas.size === 0);
}

// ------------------------------------------------------------------------------------------------ 2b. pw:clock survey holds sleeping land awake
{
  // loaded: |x|,|z| < 64 around the player; the rest only inside the "civsurvey" area, 30 ticks after it is added
  let area = null, adds = 0, removes = 0, refuse = false;
  const sys = { currentTick: 0 };
  const awake = (x, z) => (Math.abs(x) < 64 && Math.abs(z) < 64) || (area && sys.currentTick - area.t >= 30 && x >= area.x0 && x <= area.x1 && z >= area.z0 && z <= area.z1);
  const dim = {
    isChunkLoaded: ({ x, z }) => awake(x, z),
    getBlock: ({ x, y, z }) => ({ isValid: true, typeId: y <= 70 ? "minecraft:grass_block" : "minecraft:air", location: { x, y, z } }),
    getTopmostBlock: ({ x, z }) => ({ isValid: true, typeId: "minecraft:grass_block", location: { x, y: 70, z } }),
    runCommand: (c) => {
      const m = c.match(/^tickingarea add (-?\d+) -64 (-?\d+) (-?\d+) 320 (-?\d+) civsurvey true$/);
      if (m) { if (refuse) return { successCount: 0 }; adds++; area = { x0: +m[1], z0: +m[2], x1: +m[3], z1: +m[4], t: sys.currentTick }; return { successCount: 1 }; }
      if (c === "tickingarea remove civsurvey") { if (area) removes++; area = null; return { successCount: 1 }; }
      throw new Error(c);
    },
  };
  const env = { LAND, system: sys, ENGINE: { throws: 0 } };
  const body = [constOf("NOT_GROUND"), cut("isGround"), cut("blockAt"), cut("boxLoaded"), cut("topAt"), cut("groundAt"),
    constOf("SURVEY_STEP"), constOf("SURVEY_HOLD_TICKS"), cut("surveyJob"), "return surveyJob;"].join("\n");
  const surveyJob = new Function(...Object.keys(env), body)(...Object.values(env));
  const runSurvey = () => { let out = null; const g = surveyJob(dim, 0, 0, 192, (r) => { out = r; }); let r = g.next(), k = 0; while (!r.done && k++ < 1e7) { sys.currentTick++; r = g.next(); } return out; };
  const r1 = runSurvey();
  ok("survey: every one of the 2,401 columns read (the far ones by holding their tiles awake)", r1 && r1.columns === 2401 && r1.asleep === 0 && r1.woke > 2000, r1 && { asleep: r1.asleep, woke: r1.woke, held: r1.held });
  ok("survey: one area at a time, each removed (none left)", adds === r1.held && removes >= adds && area === null, { adds, removes, held: r1.held });
  refuse = true; adds = 0;
  const r2 = runSurvey();
  ok("survey: a world with no free ticking area -> the sleeping columns stay unread and are counted (as before)", r2 && r2.held === 0 && r2.asleep > 2000 && adds === 0, r2 && { asleep: r2.asleep, held: r2.held });
}

// ------------------------------------------------------------------------------------------------ 3. commitBand on stand-ins
{
  const site = { at: (x, z) => 64 + Math.floor(Math.max(0, z) * 0.3), isWater: () => false };
  const f = KIT.frameOf(0, 0, [1, 0], [0, 1]);
  const base = { kind: "kit", id: 1, role: "main", f, tmin: 0, H: new Array(130).fill(65), segs: [{ kind: "flat", a: 0, len: 130, H: 65 }], tees: [], reserved: [[50, 62, 1]] };
  const band = (() => { const g = KIT.planBandStreetJob(site, f, 50, 1, 65, 60, () => false, () => false, { maxCut: 6, maxFill: 6, ramp8: true }, {}); let r = g.next(); while (!r.done) r = g.next(); return r.value; })();
  ok("a band to commit", !!band);
  const st = { id: 1, streets: [base], nextStreetId: 2, log: [], kitQueue: [], border: { r: 200, moves: [] } };
  const legs = [], queued = [];
  const env = {
    KIT, BORDER_ASK: 3, STONE_EVERY: 16,
    junctionWindows: (s, b, side) => (b === base && side === 1 ? [50] : []),
    freeSets: () => ({ roadCells: new Set(), legacy: new Map(), bodies: [], tunnels: new Set(), grid: new Map() }),
    boxesNear: () => [], inReserve: () => false, cellsInInfluence: (x, m) => { for (const k of m.keys()) { const [a, b] = k.split(",").map(Number); if (Math.abs(a) > x.border.r || Math.abs(b) > x.border.r) return false; } return true; },
    planBorderGrowth: () => {}, tOffOf: (x) => x.tOff || 0, kitTouch: () => {}, queueKitStreet: (x, street) => queued.push(street.id),
    commitLeg: (...a) => legs.push(a),
  };
  const C = new Function(...Object.keys(env), [cut("bandVeto"), cut("commitBand"), "return { commitBand };"].join("\n"))(...Object.values(env));
  const why = { gone: 0, blocked2: 0, border: 0 };
  const okC = C.commitBand({ simDays: 9, accelNow: false }, st, base, 50, 1, 65, band, why);
  const ns = st.streets[1];
  ok("commitBand: the terrace street is recorded on its own level (role side, band, its outward window reserved)", okC && ns && ns.band && ns.role === "side" && ns.H[band.half] === band.Hn && ns.reserved[0][0] === band.half && ns.reserved[0][2] === 1, { okC, ns: ns && { id: ns.id, band: ns.band } });
  ok("commitBand: its pieces queued, then the leg committed between the two windows (tees by commitLeg)", queued[0] === ns.id && legs.length === 1 && legs[0][1] === 1 && legs[0][2] === 50 && legs[0][4] === ns.id && legs[0][5] === band.half && legs[0][7] === band.Hn, legs[0] && legs[0].slice(0, 8));
  ok("commitBand: a chronicle line names the terrace and the switchback", /TERRACE street opened 60 blocks beyond street 1 on its own level \(y \d+, \+\d+ from the junction at y 65/.test(st.log[0]) && /switchback of \d+ cells, \d+ turns/.test(st.log[0]), st.log[0]);
  // past the stones: refused, counted
  const st2 = { id: 2, streets: [base], nextStreetId: 2, log: [], kitQueue: [], border: { r: 40, moves: [] }, borderWait: 0 };
  const why2 = { gone: 0, blocked2: 0, border: 0 };
  ok("commitBand: past the boundary stones -> refused (border counted)", C.commitBand({ simDays: 9 }, st2, base, 50, 1, 65, band, why2) === false && why2.border === 1 && st2.streets.length === 1);
}
console.log(`test_landclock: ${n - bad}/${n} passed`);
if (bad) process.exitCode = 1;
