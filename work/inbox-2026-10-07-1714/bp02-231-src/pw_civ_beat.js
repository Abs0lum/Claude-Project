// pw_civ_beat.js — CIVITAS HEARTBEAT (1.3.228 B1 / BF1, FIT-MATRIX 10-06): ONE system.runInterval for every CIVITAS beat.
// Before 228 the town ran 11 separate intervals (clock, kit queue, walk, work, watch, shop, keys, flush, save, room, the
// schedule's starter) with no common plan: two heavy beats could land in one tick. Now every beat is REGISTERED here with
// a tick SLOT in a 20-tick frame (slot = tick % 20; a beat slower than 20 ticks takes its slot in its own period), and the
// one dispatcher runs whatever is due this tick:
//   * each fn is timed (per-system ms, runs, worst) and runs in its own try/catch (a JS error is cheap and counted; the
//     engine reads stay behind blockAt / topAt — a THROWN engine error leaks ~650 B, memprobe 0.0.1);
//   * a fn that took more than 2 x its budget skips its NEXT turn (counted: `over` / `skipped`);
//   * the measured MSPT (Date.now between dispatches, a 20-tick window): above MSPT_SHED the OPTIONAL beats (shop, room,
//     keys, the fishery's follow-up) are shed and the kit queue runs on every other slot, until it falls to MSPT_CLEAR;
//   * every LOG_EVERY ticks one [CIV-BEAT] line: per-system [ms, runs, worst ms, over, skipped, shed, errors], the mean
//     MSPT, the worst server tick gap and the worst beat tick (then the counters start again);
//   * the BODIES cache: one getEntities per settlement per 20 ticks (slot 10), read by the watch's post holders, the work
//     hands, the schedule pass and the keepers' check (they made 4-6 queries per settlement per 20 ticks before).
// runJob generators (schedule pass, walk graph, routes, side / bench / leg jobs, canopy, sweeps, accel) stay jobs.
// The core (createBeat) has no engine calls: tests/test_beat.mjs drives it with a fake clock.
import { world, system } from "@minecraft/server";

export const FRAME = 20;                                  // ticks in one slot frame (slot = tick % FRAME)
export const MSPT_SHED = 70, MSPT_CLEAR = 60;             // shed the optional beats above 70 ms mean MSPT, restore at <= 60
export const MSPT_WINDOW = 20;                            // ticks in the MSPT mean
export const LOG_EVERY = 1200;                            // ticks between [CIV-BEAT] lines

// THE SLOT PLAN (FIT-MATRIX BF1, adjusted to the real loops — B1-NOTES.md): every / slot(s) / budget ms / flags.
// Heavy beats never share a tick: even ticks hold the clock (0 of 40), the bodies cache (10) and the kit queue (the other
// evens); odd ticks hold work (3, 13), flush (7, 17), shop (9 of 100), the fishery follow-up (5) and save (19).
export const PLAN = {
  clock:     { every: 40,  slot: 0,  budgetMs: 150, heavy: true },                                   // the day advance (was 40)
  kitqueue:  { every: 2,   slot: [2, 4, 6, 8, 12, 14, 16, 18], budgetMs: 40, heavy: true, halveOnShed: true },   // was every 2 (10 a frame, now 8)
  bodies:    { every: 20,  slot: 10, budgetMs: 10, heavy: true },                                    // the shared bodies cache (new)
  walk:      { every: 10,  slot: 1,  budgetMs: 15 },                                                 // slots 1, 11 (was 10)
  work:      { every: 10,  slot: 3,  budgetMs: 40, heavy: true },                                    // slots 3, 13 (was 10)
  watch:     { every: 10,  slot: 5,  budgetMs: 15 },                                                 // slots 5, 15 (was 10)
  fishery:   { every: 20,  slot: 5,  budgetMs: 40, heavy: true, optional: true },                    // the shore survey's follow-up (new: 40 columns a call)
  flush:     { every: 10,  slot: 7,  budgetMs: 200, heavy: true },                                   // slots 7, 17 (was 5; its own FLUSH_MS 200 is the budget)
  shop:      { every: 100, slot: 9,  budgetMs: 20, heavy: true, optional: true },                    // was 100
  room:      { every: 20,  slot: 17, budgetMs: 20, optional: true },                                 // was 5 (its own gate: 100 / 10 accelerated)
  keys:      { every: 40,  slot: 17, budgetMs: 5, optional: true },                                  // was 40
  walktest:  { every: 20,  slot: 13, budgetMs: 0 },                                                  // the walk instrument (harness only; was its own 20)
  schedule:  { every: 100, slot: 19, budgetMs: 0 },                                                  // starts the schedule JOB (was 100)
  save:      { every: 20,  slot: 19, budgetMs: 0, heavy: true },                                     // the save check (was 20; writes at most every SAVE_EVERY)
  voice:     { every: 20,  slot: 9,  budgetMs: 10, optional: true },                                 // B5: bubbles, overheard talk, petitions (new)
  zone:      { every: 20,  slot: 9,  budgetMs: 3, optional: true },                                  // B9: "Now entering" (new)
  rally:     { every: 20,  slot: 15, budgetMs: 10 },                                                 // B10: the watch overwhelmed -> civs band together (new)
  lights:    { every: 20,  slot: 5,  budgetMs: 4, optional: true },                                  // B10: the watch's lanterns at night (new)
  guest:     { every: 20,  slot: 11, budgetMs: 8, optional: true },                                  // B11: festivals, the dusk speech, the guide (new)
};

/** a dispatcher core: register / unregister / step(tick) / stats / dueAt. opts: clock (ms), log, prof (name -> ms) */
export function createBeat(opts = {}) {
  const clock = opts.clock || (() => Date.now());
  const log = opts.log || ((s) => console.warn(s));
  const prof = opts.prof || null;
  const plan = opts.plan || PLAN;
  const systems = [];
  const S = { lastNow: null, win: [], wsum: 0, shed: false, shedOn: 0, shedTicks: 0, ticks: 0, dtSum: 0, dtN: 0, worstDt: 0, worstMs: 0, worstAt: -1, lastLog: null };

  function register(name, o = {}) {
    const p = { ...(plan[name] || {}), ...o };
    const every = Math.floor(p.every);
    if (!(every >= 1) || (FRAME % every && every % FRAME)) throw new Error(`beat ${name}: every ${p.every} must divide ${FRAME} or be a multiple of it`);
    if (typeof p.fn !== "function") throw new Error(`beat ${name}: no fn`);
    const frame = Math.max(every, FRAME);
    let slots;
    if (Array.isArray(p.slot)) slots = p.slot.map((x) => ((x % frame) + frame) % frame);
    else { const s0 = (((Math.floor(p.slot || 0)) % every) + every) % every; slots = []; for (let x = s0; x < frame; x += every) slots.push(x); }
    unregister(name);
    const sy = { name, every, frame, slots: new Set(slots), budgetMs: p.budgetMs || 0, fn: p.fn, optional: !!p.optional, heavy: !!p.heavy, halveOnShed: !!p.halveOnShed,
                 turn: 0, skipNext: false, ms: 0, runs: 0, max: 0, over: 0, skipped: 0, shedSkips: 0, errors: 0, totalMs: 0, totalRuns: 0 };
    systems.push(sy);
    return sy;
  }
  function unregister(name) { const i = systems.findIndex((x) => x.name === name); if (i >= 0) systems.splice(i, 1); }
  const dueAt = (sy, t) => sy.slots.has(((t % sy.frame) + sy.frame) % sy.frame);

  function measure() {
    const now = clock();
    if (S.lastNow !== null) {
      const dt = now - S.lastNow;
      S.win.push(dt); S.wsum += dt;
      if (S.win.length > MSPT_WINDOW) S.wsum -= S.win.shift();
      S.dtSum += dt; S.dtN++;
      if (dt > S.worstDt) S.worstDt = dt;
    }
    S.lastNow = now;
    const full = S.win.length >= MSPT_WINDOW;
    const mean = full ? S.wsum / S.win.length : 0;
    if (!S.shed && full && mean > MSPT_SHED) { S.shed = true; S.shedOn++; }
    else if (S.shed && mean <= MSPT_CLEAR) S.shed = false;
    if (S.shed) S.shedTicks++;
  }

  /** one tick: every system due at tick t runs (or is skipped / shed); returns the names that ran */
  function step(t) {
    measure();
    const ran = [];
    let tickMs = 0;
    for (const sy of systems.slice()) {
      if (!dueAt(sy, t)) continue;
      sy.turn++;
      if (sy.skipNext) { sy.skipNext = false; sy.skipped++; continue; }
      if (S.shed && sy.optional) { sy.shedSkips++; continue; }
      if (S.shed && sy.halveOnShed && sy.turn % 2) { sy.shedSkips++; continue; }
      const t0 = clock();
      try { sy.fn(t); } catch (e) { sy.errors++; if (sy.errors <= 3 || sy.errors % 100 === 0) log(`[CIV-BEAT] ${sy.name} error (${sy.errors}): ${e}`); }
      const ms = clock() - t0;
      sy.ms += ms; sy.runs++; sy.totalMs += ms; sy.totalRuns++; if (ms > sy.max) sy.max = ms;
      tickMs += ms;
      if (prof) prof[sy.name] = (prof[sy.name] || 0) + ms;
      if (sy.budgetMs > 0 && ms > 2 * sy.budgetMs) { sy.over++; sy.skipNext = true; }
      ran.push(sy.name);
    }
    S.ticks++;
    if (tickMs > S.worstMs) { S.worstMs = tickMs; S.worstAt = t; }
    if (S.lastLog === null) S.lastLog = t;
    if (t - S.lastLog >= LOG_EVERY) { log(`[CIV-BEAT] ${JSON.stringify(report(t))}`); reset(t); }
    return ran;
  }
  function report(t) {
    const sys = {};
    for (const sy of systems) sys[sy.name] = [sy.ms, sy.runs, sy.max, sy.over, sy.skipped, sy.shedSkips, sy.errors];
    return { t, ticks: S.ticks, mspt: S.dtN ? Math.round(S.dtSum / S.dtN * 10) / 10 : null, worstDt: S.worstDt, worstMs: S.worstMs, worstAt: S.worstAt, shed: S.shed ? 1 : 0, shedOn: S.shedOn, shedTicks: S.shedTicks, sys };
  }
  function reset(t) {
    S.lastLog = t; S.ticks = 0; S.dtSum = 0; S.dtN = 0; S.worstDt = 0; S.worstMs = 0; S.worstAt = -1; S.shedOn = 0; S.shedTicks = 0;
    for (const sy of systems) { sy.ms = 0; sy.runs = 0; sy.max = 0; sy.over = 0; sy.skipped = 0; sy.shedSkips = 0; sy.errors = 0; }
  }
  /** the window so far (status): mean MSPT now, shedding, per-system [ms, runs, worst, over, skipped, shed, errors] */
  function stats() { const r = report(S.lastLog ?? 0); r.msptNow = S.win.length ? Math.round(S.wsum / S.win.length * 10) / 10 : null; return r; }
  return { register, unregister, step, stats, dueAt, systems, state: S };
}

// ---- the one heartbeat of the pack
const PROF = (globalThis.__civProf = globalThis.__civProf || {});           // the profiler's totals (status -> prof)
export const CORE = createBeat({ prof: PROF });
export function register(name, o) { return CORE.register(name, o); }
export function unregister(name) { CORE.unregister(name); }
export function stats() { return CORE.stats(); }
system.runInterval(() => { try { CORE.step(system.currentTick); } catch (e) { console.warn(`[CIV-BEAT] dispatch: ${e}`); } }, 1);

// ---- THE BODIES CACHE (BF1): one getEntities per settlement per 20 ticks; readers get the VALID bodies only (an entity
// gone since the read would throw on hasTag / getTags — a thrown engine error leaks)
const VILLAGER = "minecraft:villager_v2";
const bodies = new Map();                                  // settlement id -> { tick, list }
let bodySource = null;                                     // () => the settlements ([{ id, dim }])
function queryBodies(st) {
  let list = [];
  try { list = world.getDimension(st.dim).getEntities({ tags: [`civ:settlement:${st.id}`], type: VILLAGER }); } catch { list = []; }
  const c = { tick: system.currentTick, list };
  bodies.set(st.id, c);
  return c;
}
/** the clock names its settlements; the cache beat is registered with them (slot 10) */
export function bodiesFrom(fn) {
  bodySource = fn;
  register("bodies", { fn: () => {
    const sts = bodySource ? bodySource() || [] : [];
    const ids = new Set();
    for (const st of sts) { ids.add(st.id); queryBodies(st); }
    for (const id of [...bodies.keys()]) if (!ids.has(id)) bodies.delete(id);
  } });
}
/** the settlement's villager bodies (read at most 20 ticks ago; the first ask of a settlement reads now), valid ones only */
export function bodiesOf(st) {
  const c = bodies.get(st.id) || queryBodies(st);
  return c.list.filter((v) => v.isValid);
}
