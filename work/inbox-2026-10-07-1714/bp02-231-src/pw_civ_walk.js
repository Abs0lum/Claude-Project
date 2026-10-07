// pw_civ_walk.js — CIVITAS WALKING (C2.1; D-C541 "no idle villagers", D-C542 "real time"): an embodied villager WALKS
// where the clock sends it — along the streets, the roads and the square — instead of being teleported. The engine does
// the stepping: the villager's vanilla AI follows a LEAD (pw:lead, an invisible weightless entity) that the clock moves
// along a route one waypoint at a time (the villager_v2 override's "pw:lead" group: follow_mob on family pw_lead).
// Routes come from the settlement's WALK GRAPH (the kit corridors' cells at their sidewalk height, the narrow roads' cells,
// the square, every plot's door front), a breadth-first search with |dH| <= 1 between neighbours; off the graph the lead
// simply goes to the target and the villager's own pathfinder does what it can. A walker that makes no progress for
// STUCK_TICKS is counted (st.walkStuck) and released; nothing is ever teleported here.
import { world, system } from "@minecraft/server";
import * as HB from "./pw_civ_beat.js";             // 1.3.228 (B1 / BF1): the beat is a heartbeat slot (1 and 11 of 20)

let API = null;                                   // the clock's helpers (initWalk)
const walkers = new Map();                        // villager id -> { target, path, i, lead, since, lastMove, lastPos, stId }
const LEAD_AHEAD = 4;                             // the lead stays this many route cells ahead of the villager
const REACH = 2.6;                                // the villager has arrived within this of the target (horizontal)
const STUCK_TICKS = 600;                          // 30 s without progress: give up (counted)
const BEAT = 10;                                  // ticks between lead moves
const CLIMB = 6;                                  // ticks per ladder rung (a scripted climb: the engine's villagers don't path on ladders)
let climbs = 0;
const FAR_GRAPH = 96;                             // 0.0.22: a villager off the graph walks a straight line to its nearest cell within this
const BACKOFF = [0, 0, 1200, 2400, 4800];         // 0.0.22: after the n-th stuck walk in a row to the same place, rest this many ticks
const stuckBy = { direct: 0, below: 0, above: 0, level: 0 };   // 0.0.22 (run 0.0.21: 94 stuck, 19 arrived): why walks fail
const tries = new Map();                          // villager id -> { key, n, until }

export function initWalk(api) { API = api; }

/** the settlement's walk graph: Map "x,z" -> y (the surface the feet stand on) — built once per kit version */
const graphs = new Map();
export function walkGraph(st) {
  // 0.0.25j (run 0.0.28's walk test: 7 of 8 walkers stuck on a NEW bench — the graph held its planned street and road
  // before they were laid, the leads floated over bare hillside): cells of streets / roads with pieces still queued are
  // left out until laid (the graph is rebuilt as the queue shrinks)
  const q = st.kitQueue || [];
  const key = `${st.id}:${st.kitVer || 0}:${(st.roads7 || []).length}:${API.plotCount(st)}:${Math.ceil(q.length / 10)}`;
  const got = graphs.get(st.id);
  if (got && got.key === key) return got.map;
  // 1.3.227 (profiled: a build of a city II graph, 20,284 cells, took 236..284 ms inside one send): the graph is BUILT AS
  // A JOB — the walkers use the old one until the new one is done; before the first one is done no walk starts (null)
  if (!graphJobs.has(st.id)) {
    graphJobs.add(st.id);
    const gen = graphSteps(st, key);
    try { system.runJob((function* () { try { yield* gen; } finally { graphJobs.delete(st.id); } })()); } catch (e) { graphJobs.delete(st.id); }
  }
  return got ? got.map : null;
}
const graphJobs = new Set();
function* graphSteps(st, key) {
  const q = st.kitQueue || [];
  const pendS = new Map(), pendR = new Map();
  for (const op of q) {
    if (op.op === "road" && op.rid !== undefined) { if (!pendR.has(op.rid)) pendR.set(op.rid, []); pendR.get(op.rid).push([op.a, op.a + (op.len || 7)]); }
    // (access pieces re-lay a laid street: they never take it out of the graph)
    else if (op.sid !== undefined && op.a !== undefined && ((op.op === "piece" && op.kind !== "access3") || op.op === "bridge")) { if (!pendS.has(op.sid)) pendS.set(op.sid, []); pendS.get(op.sid).push([op.a, op.a + (op.len || 13)]); }
  }
  const pending = (list, t) => list && list.some(([a2, b2]) => t >= a2 && t < b2);
  const map = new Map();
  for (const street of st.streets || []) {
    if (street.kind !== "kit" || !street.H) continue;
    const pl = pendS.get(street.id);
    street.H.forEach((H, i) => {
      if (H === undefined || pending(pl, street.tmin + i)) return;
      for (let w = 0; w <= 12; w++) { const [x, z] = API.cellOf(street.f, street.tmin + i, w); map.set(`${x},${z}`, H + 1); }
    });
    yield;
  }
  for (const r of st.roads7 || []) { const pl = pendR.get(r.id); r.cells.forEach(([x, z], i) => {
    if (pending(pl, i)) return;
    const H = r.H[i]; const d = API.dirs4[r.dirs[i]], p = [-d[1], d[0]];
    for (let k = -2; k <= 2; k++) map.set(`${x + p[0] * k},${z + p[1] * k}`, H + 1);
  }); yield; }
  if (st.square) for (let x = st.square.x; x < st.square.x + 12; x++) for (let z = st.square.z; z < st.square.z + 12; z++) map.set(`${x},${z}`, st.square.y + 1);
  for (const b of API.plotsOf(st)) {
    const fr = API.doorFront(b);
    if (fr) map.set(`${fr.x},${fr.z}`, fr.y);
  }
  map.__key = key;                                                      // 0.0.25g: the route cache's version
  // 1.3.227 (the profiled city II world: single schedule steps of 300..430 ms — a route between two cells the graph does
  // not join searched its whole piece, up to 60,000 cells): the graph's CONNECTED PIECES are labelled once per build;
  // a route between two pieces is refused at once
  map.__num = new Map();                                                // 1.3.227: the same cells under NUMBER keys (the searches)
  { let i = 0; for (const [k, y] of map) { const c = k.indexOf(","); map.__num.set(nk(+k.slice(0, c), +k.slice(c + 1)), y); if (++i % 4000 === 0) yield; } }
  map.__comp = yield* components(map.__num);
  graphs.set(st.id, { key, map });
  wst.graphBuilds++;
  wst.graphCells = map.size; wst.graphPieces = map.__comp.pieces;
  return map;
}
/** number keys: x and z offset by 2^21 (any x, z within +-2,097,151), z in the low 22 bits — a step is +-1 (z) or +-NW (x) */
const NOFF = 2097152, NW = 4194304;
const nk = (x, z) => (x + NOFF) * NW + (z + NOFF);
const nx_ = (k) => Math.floor(k / NW) - NOFF, nz_ = (k) => (k % NW) - NOFF;
const STEPS = [NW, -NW, 1, -1];
/** the graph's connected pieces (a step of at most one block joins two cells, as route() walks): Map number key -> piece */
function* components(num) {
  const comp = new Map();
  let pieces = 0, seen = 0;
  for (const k0 of num.keys()) {
    if (comp.has(k0)) continue;
    if (comp.size - seen > 4000) { seen = comp.size; yield; }
    const id = pieces++;
    comp.set(k0, id);
    const stack = [k0];
    while (stack.length) {
      const k = stack.pop(), y = num.get(k);
      for (const d of STEPS) {
        const q = k + d, yq = num.get(q);
        if (yq === undefined || comp.has(q) || Math.abs(yq - y) > 1) continue;
        comp.set(q, id);
        stack.push(q);
      }
    }
  }
  comp.pieces = pieces;
  return comp;
}
const numOf = (k) => { const c = k.indexOf(","); return nk(+k.slice(0, c), +k.slice(c + 1)); };
// 1.3.227: what the route planning costs (status / the slow-send line)
const wst = { graphBuilds: 0, graphMs: 0, graphMax: 0, graphCells: 0, graphPieces: 0, routes: 0, routeMs: 0, routeMax: 0, apart: 0, farMs: 0, slowSends: 0 };

/** the nearest graph cell to (x, z) within r */
function nearest(map, x, z, r = 6, y = null) {
  // 0.0.25d (the walk test: a villager on a lower street was joined to the graph cell of the street 4 blocks above her —
  // the nearest in x / z — and stood at the foot of its retaining wall): with a height given, a cell within 2 of it wins
  // (distance + 4 x the height difference squared); a cell at another level only when none is near
  let best = null, bd = Infinity, best2 = null, bd2 = Infinity;
  for (let dx = -r; dx <= r; dx++) for (let dz = -r; dz <= r; dz++) {
    const k = `${Math.round(x) + dx},${Math.round(z) + dz}`;
    if (!map.has(k)) continue;
    const d = dx * dx + dz * dz;
    if (y === null) { if (d < bd) { bd = d; best = k; } continue; }
    const dy = map.get(k) - y;
    if (Math.abs(dy) <= 2) { const sc = d + 4 * dy * dy; if (sc < bd) { bd = sc; best = k; } }
    else if (d < bd2) { bd2 = d; best2 = k; }
  }
  return best || best2;
}

/** the nearest graph cell within FAR_GRAPH (a full scan; only for villagers that wandered off the graph) */
function nearestFar(map, x, z) {
  const t0 = Date.now();
  let best = null, bd = FAR_GRAPH * FAR_GRAPH;
  for (const k of map.keys()) { const c = k.indexOf(","); const dx = +k.slice(0, c) - x, dz = +k.slice(c + 1) - z; const d = dx * dx + dz * dz; if (d < bd) { bd = d; best = k; } }
  wst.farMs += Date.now() - t0;
  return best;
}
/** a straight line of waypoints (one per cell) from (x0, z0) to (x1, z1), feet on the ground where it is known */
function line(dim, x0, z0, y0, x1, z1, y1) {
  const out = [];
  const n = Math.max(Math.abs(x1 - x0), Math.abs(z1 - z0));
  for (let i = 1; i <= n; i++) {
    const x = Math.round(x0 + (x1 - x0) * i / n), z = Math.round(z0 + (z1 - z0) * i / n);
    let y = Math.round(y0 + (y1 - y0) * i / n);
    if (API.groundAt) { const g = API.groundAt(dim, x, z); if (g !== undefined) y = g + 1; }
    out.push([x, z, y]);
  }
  return out;
}
/** 0.0.23 (run 0.0.22: the quarryman's straight line to the pit ran through his own quarry's back wall; 24 of 44 stuck
 *  walks were "level" — a wall or a fence in the way): a LOCAL PATH over the real blocks — A* on (x, z, feet y), a step
 *  up or down of one block at most, feet and head free (air, plants, a door, a ladder), a solid floor — inside the box of
 *  the two ends + PAD, at most MAX_NODES expansions. Returns [[x, z, y], ...] (feet) without the start, or null. */
const LOCAL_PAD = 12, LOCAL_MAX = 1500;            // 0.0.25g: 1500 expansions (the profiler)
const SOFT = (id) => id === "minecraft:air" || id.includes("_door") || id.includes("ladder") || id.includes("grass") && !id.includes("grass_block") || id.includes("flower")
  || id.includes("fern") || id.includes("sapling") || id.includes("torch") || id.includes("carpet") || id.includes("snow_layer") || id.includes("vine") || id.includes("dandelion") || id.includes("poppy");
function localPath(dim, x0, z0, y0, x1, z1, y1) {
  const cache = new Map();
  const id = (x, y, z) => { const k = `${x},${y},${z}`; if (cache.has(k)) return cache.get(k); let v = null; if (dim.isChunkLoaded({ x, y, z })) { try { const b = dim.getBlock({ x, y, z }); v = b && b.isValid ? b.typeId : null; } catch { v = null; } } cache.set(k, v); return v; };   // 1.3.227: a throwing read leaks ~650 B of server memory
  // 0.0.25: HALF blocks (a bottom slab, stairs the right way up, a street ramp's quarters q1..q3, a bench seat) are floors
  // INSIDE their own cell: the walker stands in that cell (feet on the half block) with two free cells above — the
  // kerbs, the street ramps and the sidewalk slabs were walls to this search before (run 0.0.24: legs fell back to the
  // straight line, 52 walks stuck "level")
  const halfCache = new Map();
  const half = (x, y, z) => {
    const t = id(x, y, z);
    if (!t || !(t.includes("_slab") || t.includes("stairs") || t.includes("ramp_"))) return false;
    const k = `${x},${y},${z}`;
    if (halfCache.has(k)) return halfCache.get(k);
    let v = false;
    if (t.includes("ramp_")) v = !t.endsWith("_q4");
    else { try { const p = dim.getBlock({ x, y, z }).permutation; v = t.includes("_slab") ? p.getState("minecraft:vertical_half") === "bottom" : !p.getState("upside_down_bit"); } catch { v = false; } }
    halfCache.set(k, v);
    return v;
  };
  const standable = (x, y, z) => {
    const f = id(x, y, z), h = id(x, y + 1, z);
    if (f === null || h === null || !SOFT(h)) return false;
    if (half(x, y, z)) return SOFT(id(x, y + 2, z) || "minecraft:air");
    const g = id(x, y - 1, z);
    return g !== null && SOFT(f) && !SOFT(g) && !g.includes("water") && !g.includes("lava") && !g.includes("fence") && !g.includes("wall");
  };
  const bx0 = Math.min(x0, x1) - LOCAL_PAD, bx1 = Math.max(x0, x1) + LOCAL_PAD, bz0 = Math.min(z0, z1) - LOCAL_PAD, bz1 = Math.max(z0, z1) + LOCAL_PAD;
  const key = (x, y, z) => `${x},${y},${z}`;
  const h = (x, z) => Math.abs(x - x1) + Math.abs(z - z1);
  // a binary heap on f (the open list)
  const heap = [];
  const push = (e) => { heap.push(e); let i = heap.length - 1; while (i > 0) { const p2 = (i - 1) >> 1; if (heap[p2][0] <= heap[i][0]) break; [heap[p2], heap[i]] = [heap[i], heap[p2]]; i = p2; } };
  const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < heap.length && heap[l][0] < heap[m][0]) m = l; if (r < heap.length && heap[r][0] < heap[m][0]) m = r; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; i = m; } } return top; };
  push([h(x0, z0), 0, x0, y0, z0]);
  const g = new Map([[key(x0, y0, z0), 0]]), prev = new Map();
  let n = 0, endK = null;
  while (heap.length && n < LOCAL_MAX) {
    const [, c, x, y, z] = pop();
    n++;
    if (Math.abs(x - x1) + Math.abs(z - z1) <= 1 && Math.abs(y - y1) <= 2) { endK = key(x, y, z); break; }
    // 0.0.24 (run 0.0.23: the quarryman and a cottager stood in LADDERS, 23 stuck walks — the template pit and the loft):
    // in a ladder column the way goes up or down a rung; the walker climbs it (scripted rungs, the beat below)
    if ((id(x, y, z) || "").includes("ladder")) {
      for (const dy of [1, -1]) {
        const ny = y + dy;
        const f = id(x, ny, z), hd = id(x, ny + 1, z);
        if (f === null || hd === null) continue;
        if (dy === 1 && !(SOFT(f) && SOFT(hd))) continue;
        if (dy === -1 && !f.includes("ladder")) continue;
        const k = key(x, ny, z), nc = c + 1.5;
        if (g.has(k) && g.get(k) <= nc) continue;
        g.set(k, nc); prev.set(k, key(x, y, z));
        push([nc + h(x, z), nc, x, ny, z]);
      }
    }
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx, nz = z + dz;
      if (nx < bx0 || nx > bx1 || nz < bz0 || nz > bz1) continue;
      // a ladder cell beside us at our level (its column's bottom or a landing) can be stepped into
      { const lid = id(nx, y, nz); if (lid && lid.includes("ladder") && SOFT(id(nx, y + 1, nz) || "minecraft:air")) { const k = key(nx, y, nz), nc = c + 1; if (!g.has(k) || g.get(k) > nc) { g.set(k, nc); prev.set(k, key(x, y, z)); push([nc + h(nx, nz), nc, nx, y, nz]); } continue; } }
      for (const dy of [0, 1, -1]) {
        const ny = y + dy;
        if (!standable(nx, ny, nz)) continue;
        if (dy === 1 && !SOFT(id(x, y + 2, z) || "minecraft:air")) continue;               // head room for the step up
        const k = key(nx, ny, nz), nc = c + 1 + (dy ? 0.5 : 0);
        if (g.has(k) && g.get(k) <= nc) break;
        g.set(k, nc); prev.set(k, key(x, y, z));
        push([nc + h(nx, nz), nc, nx, ny, nz]);
        break;                                                                              // one level per column
      }
    }
  }
  if (!endK) return null;
  const out = [];
  for (let k = endK; k && k !== key(x0, y0, z0); k = prev.get(k)) { const [x, y, z] = k.split(",").map(Number); out.push([x, z, y]); }
  out.reverse();
  return out;
}
/** a leg off the graph: the local path when one exists within reach, else the straight line */
function leg(dim, x0, z0, y0, x1, z1, y1) {
  if (Math.abs(x1 - x0) + Math.abs(z1 - z0) <= 80) { const p = localPath(dim, x0, z0, y0, x1, z1, y1); if (p && p.length) { legStats.local++; return p; } }
  legStats.line++;
  return line(dim, x0, z0, y0, x1, z1, y1);
}
const legStats = { local: 0, line: 0 };
/** A* over the graph (Manhattan heuristic, a binary heap): [[x, z, y], ...] from cell a to cell b (keys), or null.
 *  0.0.25g (the profiler, run 0.0.26d: the keepers' beat cost 4-5 ms a tick — every keeper away from its station
 *  re-planned a breadth-first route over the town's ~20,000 street cells every 5 s): A* explores toward the target, and
 *  the last ROUTE_CACHE routes are kept per graph version (the same keepers walk the same ways every day) */
const ROUTE_CACHE = 300;
const routeCache = new Map();
function route(map, a, b) {
  if (a === b) return [parse(map, a)];
  if (map.__comp && map.__comp.get(numOf(a)) !== map.__comp.get(numOf(b))) { wst.apart++; return null; }
  const ck = `${map.__key || ""}|${a}|${b}`;
  if (routeCache.has(ck)) { const r = routeCache.get(ck); routeCache.delete(ck); routeCache.set(ck, r); return r ? r.map((c) => c.slice()) : null; }
  // 1.3.227 (profiled: one in-piece search took 422 ms): a search runs here for ROUTE_SYNC steps; a longer one goes on as
  // a JOB and the send is refused (PENDING) until the route is in the cache — the caller's next beat finds it there
  if (routeJobs.has(ck)) return PENDING;
  if (!map.__num) { const tr0 = Date.now(); try { return routeSearch(map, a, b, ck); } finally { const ms = Date.now() - tr0; wst.routes++; wst.routeMs += ms; if (ms > wst.routeMax) wst.routeMax = ms; } }
  const gen = routeSteps(map, a, b, ck);
  const tr0 = Date.now();
  let r;
  try { for (let i = 0; i < ROUTE_SYNC; i++) { r = gen.next(); if (r.done) break; } } finally { const ms = Date.now() - tr0; wst.routes++; wst.routeMs += ms; if (ms > wst.routeMax) wst.routeMax = ms; }
  if (r.done) return r.value;
  if (routeJobs.size >= ROUTE_JOBS) { try { gen.return(); } catch { /* closed */ } return PENDING; }
  routeJobs.add(ck); wst.routeJobs = (wst.routeJobs || 0) + 1;
  try { system.runJob((function* () { try { yield* gen; } finally { routeJobs.delete(ck); } })()); } catch { routeJobs.delete(ck); }
  return PENDING;
}
export const PENDING = "pending";
const ROUTE_SYNC = 3, ROUTE_STEP = 500, ROUTE_JOBS = 3;   // 3 x 500 expansions here (~20 ms); at most 3 searches running on
const routeJobs = new Set();
/** routeSearch as steps of ROUTE_STEP expansions (the same search; the result goes to the cache) */
function* routeSteps(map, a, b, ck) {
  const num = map.__num;
  const A = numOf(a), Bk = numOf(b), bx = nx_(Bk), bz = nz_(Bk);
  const hh = (k) => Math.abs(nx_(k) - bx) + Math.abs(nz_(k) - bz);
  const heap = [];
  const less = (u, v) => u[0] < v[0] || (u[0] === v[0] && u[1] > v[1]);
  const push = (e) => { heap.push(e); let i = heap.length - 1; while (i > 0) { const p2 = (i - 1) >> 1; if (!less(heap[i], heap[p2])) break; [heap[p2], heap[i]] = [heap[i], heap[p2]]; i = p2; } };
  const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < heap.length && less(heap[l], heap[m])) m = l; if (r < heap.length && less(heap[r], heap[m])) m = r; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; i = m; } } return top; };
  const g = new Map([[A, 0]]), prev = new Map([[A, null]]);
  push([hh(A), 0, A]);
  let n = 0, found = false;
  while (heap.length && n < 60000) {
    const [, c, k] = pop();
    if (c > (g.get(k) ?? Infinity)) continue;
    n++;
    if (n % ROUTE_STEP === 0) yield;
    if (k === Bk) { found = true; break; }
    const y = num.get(k);
    for (const d of STEPS) {
      const q = k + d, yq = num.get(q);
      if (yq === undefined || Math.abs(yq - y) > 1) continue;
      const nc = c + 1;
      if (nc >= (g.get(q) ?? Infinity)) continue;
      g.set(q, nc); prev.set(q, k);
      push([nc + hh(q), nc, q]);
    }
  }
  wst.expanded = (wst.expanded || 0) + n;
  let out = null;
  if (found) { out = []; for (let k = Bk; k !== null; k = prev.get(k)) out.push([nx_(k), nz_(k), num.get(k)]); out.reverse(); }
  routeCache.set(ck, out);
  if (routeCache.size > ROUTE_CACHE) routeCache.delete(routeCache.keys().next().value);
  return out ? out.map((c) => c.slice()) : null;
}
function routeSearch(map, a, b, ck) {
  // 1.3.227: number keys, and among equal estimates the deeper node first (a 13-wide street made A* flood its width:
  // single searches of 110..270 ms at city II)
  const num = map.__num;
  if (!num) return routeSearchStr(map, a, b, ck);
  const A = numOf(a), Bk = numOf(b), bx = nx_(Bk), bz = nz_(Bk);
  const hh = (k) => Math.abs(nx_(k) - bx) + Math.abs(nz_(k) - bz);
  const heap = [];
  const less = (u, v) => u[0] < v[0] || (u[0] === v[0] && u[1] > v[1]);
  const push = (e) => { heap.push(e); let i = heap.length - 1; while (i > 0) { const p2 = (i - 1) >> 1; if (!less(heap[i], heap[p2])) break; [heap[p2], heap[i]] = [heap[i], heap[p2]]; i = p2; } };
  const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < heap.length && less(heap[l], heap[m])) m = l; if (r < heap.length && less(heap[r], heap[m])) m = r; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; i = m; } } return top; };
  const g = new Map([[A, 0]]), prev = new Map([[A, null]]);
  push([hh(A), 0, A]);
  let n = 0, found = false;
  while (heap.length && n < 60000) {
    const [, c, k] = pop();
    if (c > (g.get(k) ?? Infinity)) continue;
    n++;
    if (k === Bk) { found = true; break; }
    const y = num.get(k);
    for (const d of STEPS) {
      const q = k + d, yq = num.get(q);
      if (yq === undefined || Math.abs(yq - y) > 1) continue;
      const nc = c + 1;
      if (nc >= (g.get(q) ?? Infinity)) continue;
      g.set(q, nc); prev.set(q, k);
      push([nc + hh(q), nc, q]);
    }
  }
  wst.expanded = (wst.expanded || 0) + n;
  let out = null;
  if (found) { out = []; for (let k = Bk; k !== null; k = prev.get(k)) out.push([nx_(k), nz_(k), num.get(k)]); out.reverse(); }
  routeCache.set(ck, out);
  if (routeCache.size > ROUTE_CACHE) routeCache.delete(routeCache.keys().next().value);
  return out ? out.map((c) => c.slice()) : null;
}
function routeSearchStr(map, a, b, ck) {
  const [bx, bz] = b.split(",").map(Number);
  const hh = (x, z) => Math.abs(x - bx) + Math.abs(z - bz);
  const heap = [];
  const push = (e) => { heap.push(e); let i = heap.length - 1; while (i > 0) { const p2 = (i - 1) >> 1; if (heap[p2][0] <= heap[i][0]) break; [heap[p2], heap[i]] = [heap[i], heap[p2]]; i = p2; } };
  const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < heap.length && heap[l][0] < heap[m][0]) m = l; if (r < heap.length && heap[r][0] < heap[m][0]) m = r; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; i = m; } } return top; };
  const [ax, az] = a.split(",").map(Number);
  const g = new Map([[a, 0]]), prev = new Map([[a, null]]);
  push([hh(ax, az), 0, a, ax, az]);
  let n = 0, found = false;
  while (heap.length && n < 60000) {
    const [, c, k, x, z] = pop();
    if (c > (g.get(k) ?? Infinity)) continue;
    n++;
    if (k === b) { found = true; break; }
    const y = map.get(k);
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx, nz = z + dz, nk = `${nx},${nz}`;
      if (!map.has(nk)) continue;
      if (Math.abs(map.get(nk) - y) > 1) continue;
      const nc = c + 1;
      if (nc >= (g.get(nk) ?? Infinity)) continue;
      g.set(nk, nc); prev.set(nk, k);
      push([nc + hh(nx, nz), nc, nk, nx, nz]);
    }
  }
  let out = null;
  if (found) { out = []; for (let k = b; k !== null; k = prev.get(k)) out.push(parse(map, k)); out.reverse(); }
  routeCache.set(ck, out);
  if (routeCache.size > ROUTE_CACHE) routeCache.delete(routeCache.keys().next().value);
  return out ? out.map((c) => c.slice()) : null;
}
/** unit tests only */
export const __routeTest = { routeSearch: (map, a, b) => routeSearch(map, a, b, `t|${a}|${b}|${Math.random()}`), routeSteps: (map, a, b) => { const g = routeSteps(map, a, b, `j|${a}|${b}|${Math.random()}`); let r = g.next(); while (!r.done) r = g.next(); return r.value; }, routeSearchStr: (map, a, b) => routeSearchStr(map, a, b, `s|${a}|${b}|${Math.random()}`), components: (num) => { const g = components(num); let r = g.next(); while (!r.done) r = g.next(); return r.value; }, nk, numOf };
const parse = (map, k) => { const [x, z] = k.split(",").map(Number); return [x, z, map.get(k)]; };

/** send a villager to target {x, y, z} (feet). Returns "route" | "direct" | false */
// 1.3.227 (the profiled gate 226-2 world, 150 buildings: route searches from the schedule, the work and the shop beats
// landed in the same tick): the routes planned in one tick share SEND_BUDGET_MS; past it a send is refused for this tick
// (no rest recorded — the caller's next beat asks again)
const SEND_BUDGET_MS = 40;
let sendTick = -1, sendMs = 0, sendDeferred = 0;
export function sendBudgetLeft() { return system.currentTick !== sendTick || sendMs < SEND_BUDGET_MS; }
export function send(v, st, target) {
  if (!v || !v.isValid) return false;
  const cur = walkers.get(v.id);
  if (cur && cur.target && Math.abs(cur.target.x - target.x) <= 1 && Math.abs(cur.target.z - target.z) <= 1) return cur.mode;   // already going there
  if (system.currentTick !== sendTick) { sendTick = system.currentTick; sendMs = 0; }
  if (sendMs >= SEND_BUDGET_MS) { sendDeferred++; return false; }
  const t0 = Date.now(), g0 = wst.graphMs, r0 = wst.routeMs, f0 = wst.farMs;
  try { return sendNow(v, st, target); } finally {
    const ms = Date.now() - t0;
    sendMs += ms;
    if (ms > 100) { wst.slowSends++; if (wst.slowSends <= 5 || wst.slowSends % 50 === 0) console.warn(`[CIV-WALK] slow send (${wst.slowSends}): ${ms} ms — graph ${wst.graphMs - g0}, route ${wst.routeMs - r0}, far ${wst.farMs - f0} (graph ${wst.graphCells} cells, ${wst.graphPieces} pieces)`); }
  }
}
// 1.3.228 (B2 / BF3): why the last send of a villager was refused (the why-idle codes): villager id -> { why, tick }; a
// successful send clears it; whyNot() reads it for WHY_FRESH ticks
const refused = new Map();
const WHY_FRESH = 400;
function refuse(v, why) {
  refused.set(v.id, { why, tick: system.currentTick });
  if (refused.size > 512) { const old = system.currentTick - WHY_FRESH; for (const [k, r] of refused) if (r.tick < old) refused.delete(k); }
  return false;
}
/** UNREACHABLE (resting after stuck walks) | NO_ROUTE (no graph yet / the route is being searched) | SLOTS_FULL | null */
export function whyNot(v) { const r = refused.get(v.id); return r && system.currentTick - r.tick <= WHY_FRESH ? r.why : null; }
function sendNow(v, st, target) {
  // 0.0.22: a villager that failed to get to this same place lately rests before trying again (BACKOFF)
  const tkey = `${Math.floor(target.x)},${Math.floor(target.z)}`;
  const tr = tries.get(v.id);
  if (tr && tr.key === tkey && system.currentTick < tr.until) return refuse(v, tr.slots ? "SLOTS_FULL" : tr.n > 0 ? "UNREACHABLE" : "NO_ROUTE");
  const map = walkGraph(st);
  if (!map) return refuse(v, "NO_ROUTE");                                // 1.3.227: the town's first graph is still being built
  const loc = v.location;
  // 0.0.22 (run 0.0.21: a quarryman 250 blocks off the graph got ONE waypoint at the far target, beyond the 48-block
  // follow range — he never saw his lead): off the graph, a straight line to the nearest graph cell, the graph route,
  // and a straight line from the graph to a target off it; only when there is no graph near either end is the whole
  // walk a straight line — the carrot is always LEAD_AHEAD cells ahead, wherever the villager stands
  const a = nearest(map, loc.x, loc.z, 8, Math.floor(loc.y)) || nearestFar(map, loc.x, loc.z), b = nearest(map, target.x, target.z, 4, Math.floor(target.y)) || nearestFar(map, target.x, target.z);
  let path = a && b ? route(map, a, b) : null;
  if (path === PENDING) { wst.pending = (wst.pending || 0) + 1; return refuse(v, "NO_ROUTE"); }   // 1.3.227: the route is still being searched
  cancel(v);
  let mode = "route";
  const vx = Math.floor(loc.x), vz = Math.floor(loc.z), vy = Math.floor(loc.y);
  const tx = Math.floor(target.x), tz = Math.floor(target.z), ty = Math.floor(target.y);
  if (path) {
    const [ax, az, ay] = path[0], [bx, bz, by] = path[path.length - 1];
    if (Math.abs(ax - vx) + Math.abs(az - vz) > 2) { path = leg(v.dimension, vx, vz, vy, ax, az, ay).concat(path); mode = "route+"; }
    if (Math.abs(bx - tx) + Math.abs(bz - tz) > 2) { path = path.concat(leg(v.dimension, bx, bz, by, tx, tz, ty)); mode = mode === "route" ? "route+" : mode; }
  } else { path = leg(v.dimension, vx, vz, vy, tx, tz, ty); mode = "direct"; if (!path.length) path = [[tx, tz, ty]]; }
  // 0.0.20 (the lead test: villagers follow LOOSELY, orbiting within ~5 blocks): the whole route is kept and the lead is a
  // CARROT — always LEAD_AHEAD cells ahead of the villager's nearest route cell, never further, so it cannot run away
  const wps = path.slice();
  const end = [Math.floor(target.x), Math.floor(target.z), target.y];
  if (!wps.length || wps[wps.length - 1][0] !== end[0] || wps[wps.length - 1][1] !== end[1]) wps.push(end);
  const first = wps[Math.min(wps.length - 1, LEAD_AHEAD)];
  const lead = attachLead(v, first);
  // 0.0.25d: no lead (its first waypoint sleeps, or no slot) -> this target rests a little (it was re-sent every beat)
  if (!lead) { const tr2 = tries.get(v.id); const full = slotOf.size >= LEAD_SLOTS; tries.set(v.id, { key: tkey, n: tr2 && tr2.key === tkey ? tr2.n : 0, until: system.currentTick + 200, slots: full }); return refuse(v, full ? "SLOTS_FULL" : "NO_ROUTE"); }
  refused.delete(v.id);
  walkers.set(v.id, { target, path: wps, i: 0, lead: lead.id, since: system.currentTick, lastMove: system.currentTick, lastPos: [loc.x, loc.z], mode, stId: st.id });
  return mode;
}
/** walk an EXPLICIT path [[x, z, y], ...] (F5: the sewer hall below a street — no graph, no ground snapping) */
export function sendPath(v, st, path) {
  if (!v || !v.isValid || !path || !path.length) return false;
  cancel(v);
  const end = path[path.length - 1];
  const first = path[Math.min(path.length - 1, LEAD_AHEAD)];
  const lead = attachLead(v, first);
  if (!lead) return false;
  const loc = v.location;
  walkers.set(v.id, { target: { x: end[0] + 0.5, y: end[2], z: end[1] + 0.5 }, path: path.slice(), i: 0, lead: lead.id, since: system.currentTick, lastMove: system.currentTick, lastPos: [loc.x, loc.z], mode: "path", stId: st.id });
  return "path";
}
// 0.0.26 (run 0.0.24: walkers stood 16-33 blocks from their OWN leads on average; follow_mob takes any pw_lead within
// 48 blocks — with a dozen villagers walking at once, a villager followed another's carrot): each walker holds a SLOT;
// its lead carries the slot as the property pw:slot and the villager's follow group (pw:lead_<slot>) follows only the
// lead whose pw:slot equals it. 48 slots (the embodied cap); with all taken a walk is refused (the caller retries).
const LEAD_SLOTS = 48;
const slotOf = new Map();                          // villager id -> slot
let slotsFull = 0, orphansRemoved = 0, leadErrors = 0, rescues = 0;
// 0.0.25d (the walk test: on the bench roads the route cells' heights were one or two below the road's surface — the lead
// sat inside the cobblestone, the follower stood still): a route cell's height is checked against the blocks the first time
// the lead goes there — the standing place within 3 of it (feet free, head free, a floor; a slab / stairs / ramp quarter
// counts as a floor inside its own cell)
const PASSES = (id) => id === "minecraft:air" || id.includes("_door") || id.includes("ladder") || (id.includes("grass") && !id.includes("grass_block")) || id.includes("flower")
  || id.includes("fern") || id.includes("sapling") || id.includes("torch") || id.includes("carpet") || id.includes("snow_layer") || id.includes("vine") || id.includes("light_block") || id.includes("bush");
function standY(dim, w, idx) {
  const c = w.path[idx];
  if (!c) return 0;
  w.ys = w.ys || new Map();
  if (w.ys.has(idx)) return w.ys.get(idx);
  const [x, z, y0] = c;
  let got = y0;
  const id = (y) => { if (!dim.isChunkLoaded({ x, y, z })) return null; try { const b = dim.getBlock({ x, y, z }); return b && b.isValid ? b.typeId : null; } catch { return null; } };   // 1.3.227: no throwing read
  for (const dy of [0, 1, -1, 2, -2, 3, -3]) {
    const y = y0 + dy, f = id(y), h = id(y + 1), g = id(y - 1);
    if (f === null || h === null || g === null) break;
    const halfF = f.includes("_slab") || f.includes("stairs") || f.includes("ramp_");
    if (halfF && !f.endsWith("_q4") && PASSES(h)) { got = y; break; }
    if (PASSES(f) && PASSES(h) && !PASSES(g) && !g.includes("water") && !g.includes("lava") && !g.includes("fence") && !g.includes("wall")) { got = y; break; }
  }
  w.ys.set(idx, got);
  c[2] = got;                                                                          // the stuck cause and arrival read it too
  return got;
}
const LED = "civ:led";
function leadOff(v) { try { v.triggerEvent("pw:lead_off"); } catch { /* left */ } try { v.removeTag(LED); } catch { /* left */ } }
function freeSlot() { const used = new Set(slotOf.values()); for (let k = 0; k < LEAD_SLOTS; k++) if (!used.has(k)) return k; return -1; }
function attachLead(v, first) {
  const k = freeSlot();
  if (k < 0) { slotsFull++; return null; }
  let lead;
  try {
    // 1.3.224 (his log: "lead (1): LocationInUnloadedChunkError"): a first waypoint in a chunk that is not ticking falls
    // back to a point nearer the walker (half way, then one cell ahead) — the beat moves the carrot on as it walks
    const L = v.location, cands = [[first[0] + 0.5, first[2] + 0.6, first[1] + 0.5],
      [(L.x + first[0] + 0.5) / 2, Math.max(L.y, first[2]) + 0.6, (L.z + first[1] + 0.5) / 2],
      [L.x + Math.sign(first[0] + 0.5 - L.x), L.y + 0.6, L.z + Math.sign(first[1] + 0.5 - L.z)]];
    let lastErr = null;
    for (const [cx, cy, cz] of cands) { try { lead = v.dimension.spawnEntity("pw:lead", { x: cx, y: cy, z: cz }); break; } catch (e) { lastErr = e; } }
    if (!lead) throw lastErr || new Error("no lead");
    lead.addTag(`civ:lead:${v.id}`);
    let paired = true;
    try { lead.setProperty("pw:slot", k); } catch { paired = false; }
    try { v.triggerEvent("pw:civ_walk"); for (const t of v.getTags()) if (t.startsWith("civ:state:")) v.removeTag(t); } catch { /* an older body */ }   // 1004b: walking = no stand / idle / home group
    if (paired) { v.triggerEvent(`pw:lead_on_${k}`); slotOf.set(v.id, k); } else v.triggerEvent("pw:lead_on");     // an older pack: the shared group
    try { v.addTag(LED); } catch { /* left */ }                                     // 1.3.227: the sweep turns off only the led
    return lead;
  } catch (e) { leadErrors++; if (leadErrors <= 3 || leadErrors % 200 === 0) console.warn(`[CIV-WALK] lead (${leadErrors}): ${e}`); if (lead) { try { lead.remove(); } catch { /* left */ } } slotOf.delete(v.id); return null; }
}
/** every 10 s: leads no walk owns (a reload empties the walk table; the persistent leads stayed) are removed, and every
 *  civ villager that is not walking gets pw:lead_off again (a follow group left on by a reload) */
let sweptOnce = false;
function sweepOrphans() {
  const own = new Set([...walkers.values()].map((w) => w.lead));
  let dim; try { dim = world.getDimension("overworld"); } catch { return; }
  try { for (const e of dim.getEntities({ type: "pw:lead" })) if (!own.has(e.id)) { try { e.remove(); orphansRemoved++; } catch { /* left */ } } } catch { /* none */ }
  // 1.3.227 (profiled: 244 ms every 200 ticks — pw:lead_off was triggered on EVERY idle civ at city II): the first
  // sweep after a load turns off every idle civ's follow group (a reload empties the walk table); later sweeps only those
  // still tagged civ:led
  const q = sweptOnce ? { type: "minecraft:villager_v2", tags: ["civ:villager", LED] } : { type: "minecraft:villager_v2", tags: ["civ:villager"] };
  sweptOnce = true;
  try { for (const v of dim.getEntities(q)) if (!walkers.has(v.id)) { leadOff(v); slotOf.delete(v.id); } } catch { /* none */ }
}
export function cancel(v) {
  const w = walkers.get(v.id);
  slotOf.delete(v.id);
  if (!w) return;
  try { const l = world.getEntity(w.lead); if (l) l.remove(); } catch { /* gone */ }
  leadOff(v);
  walkers.delete(v.id);
}
export function walking(v) { return walkers.has(v.id); }
/** 0.0.25 (the walk test): a walker's state — path index / length, mode, the lead's place, the next waypoints, idle ticks */
export function peek(v) {
  const w = v ? walkers.get(v.id) : null;
  if (!w) return null;
  let lead = null;
  try { const l = world.getEntity(w.lead); if (l) lead = [Math.round(l.location.x * 10) / 10, Math.round(l.location.y * 10) / 10, Math.round(l.location.z * 10) / 10]; } catch { lead = null; }
  const now = system.currentTick;
  return { i: w.i, n: w.path.length, mode: w.mode, lead, next: w.path.slice(w.i, w.i + 6), idle: now - w.lastMove, age: now - w.since, cause: w.cause || null };
}
/** the walkers right now: how many, how far from their leads (a lead the villager lost = > 8 blocks), the oldest walk */
export function stats() {
  let n = 0, far = 0, sum = 0, oldest = 0;
  const sample = [];
  const now = system.currentTick;
  for (const [vid, w] of walkers) {
    let v, lead;
    try { v = world.getEntity(vid); lead = world.getEntity(w.lead); } catch { continue; }
    if (!v || !lead) continue;
    const d = Math.hypot(v.location.x - lead.location.x, v.location.z - lead.location.z);
    n++; sum += d; if (d > 8) far++; oldest = Math.max(oldest, now - w.since);
    if (sample.length < 6) sample.push([v.nameTag || "?", Math.round(v.location.x), Math.round(v.location.y), Math.round(v.location.z), Math.round(lead.location.x), Math.round(lead.location.y), Math.round(lead.location.z), `${w.i}/${w.path.length}`, w.mode, now - w.lastMove, now - w.since]);
  }
  return { sendDeferred, routing: { ...wst }, slots: slotOf.size, slotsFull, orphans: orphansRemoved, rescues, leadErrors, walking: walkers.size, lost: far, leadDist: n ? Math.round(sum / n * 10) / 10 : null, oldestTicks: oldest, stuckBy: { ...stuckBy }, legs: { ...legStats }, climbs, resting: [...tries.values()].filter((t) => t.until > now).length, sample };
}

/** the beat: the villager's nearest route cell (searched forward from the last one); the lead sits LEAD_AHEAD cells
 *  beyond it; arrival at the target ends the walk; no route progress for STUCK_TICKS = stuck (counted, released) */
HB.register("walk", { fn: () => {
  if (!API) return;
  const now = system.currentTick;
  if (now % 200 < BEAT) { try { sweepOrphans(); } catch (e) { console.warn(`[CIV-WALK] sweep: ${e}`); } }
  for (const [vid, w] of [...walkers]) {
   // review 04:4x #13: one walker's throw (a removed entity mid-beat) never stops the others' beat
   try {
    let v, lead;
    try { v = world.getEntity(vid); lead = world.getEntity(w.lead); } catch { v = undefined; }
    if (!v || !lead) { walkers.delete(vid); slotOf.delete(vid); try { if (lead) lead.remove(); } catch { /* left */ } if (v) leadOff(v); continue; }
    const loc = v.location;
    const endP = w.path[w.path.length - 1];
    // a rung: the path's next cell is the same column one up / down, and the walker stands in that column
    {
      const c0 = w.path[w.i], c1 = w.path[w.i + 1];
      if (c0 && c1 && c1[0] === c0[0] && c1[1] === c0[1] && c1[2] !== c0[2] && Math.abs(loc.x - (c0[0] + 0.5)) < 0.9 && Math.abs(loc.z - (c0[1] + 0.5)) < 0.9) {
        if (!w.climbAt || now - w.climbAt >= CLIMB) {
          w.climbAt = now;
          try { v.teleport({ x: c1[0] + 0.5, y: c1[2], z: c1[1] + 0.5 }); } catch { /* left */ }
          w.i += 1; w.lastMove = now; climbs++;
        }
        continue;
      }
    }
    if (Math.hypot(loc.x - (endP[0] + 0.5), loc.z - (endP[1] + 0.5)) <= REACH && Math.abs(loc.y - endP[2]) <= 3) { tries.delete(vid); API.arrived(v, w); cancel(v); continue; }
    // progress along the route: the nearest cell among the next 12 (and never backwards)
    let bi = w.i, bd = Infinity;
    for (let k = w.i; k < Math.min(w.path.length, w.i + 12); k++) { const c = w.path[k]; const d = Math.hypot(loc.x - (c[0] + 0.5), loc.z - (c[1] + 0.5)); if (d < bd) { bd = d; bi = k; } }
    if (bd <= 2.5 && bi > w.i) { w.i = bi; w.lastMove = now; }
    const ni = Math.min(w.path.length - 1, w.i + LEAD_AHEAD);
    const n = w.path[ni];
    const lx = n[0] + 0.5, lz = n[1] + 0.5;
    if (Math.abs(lead.location.x - lx) > 0.1 || Math.abs(lead.location.z - lz) > 0.1) { try { lead.teleport({ x: lx, y: standY(v.dimension, w, ni) + 0.6, z: lz }); } catch { /* left */ } }
    // 0.0.25d: a walker that made no progress for STUCK_TICKS is helped ONCE onto its current route cell (a villager in a
    // two-deep hollow cannot jump out; the walk test found one beside a road's retaining wall) — then it walks on
    if (now - w.lastMove > STUCK_TICKS && !w.rescued && w.mode !== "path") {
      const ci = Math.min(w.path.length - 1, w.i + 1), c = w.path[ci];
      const cy = standY(v.dimension, w, ci);
      if (Math.hypot(loc.x - (c[0] + 0.5), loc.z - (c[1] + 0.5)) <= 12) {
        try { v.teleport({ x: c[0] + 0.5, y: cy, z: c[1] + 0.5 }); w.rescued = 1; w.i = ci; w.lastMove = now; rescues++; continue; } catch { /* left */ }
      }
    }
    if (now - w.lastMove > STUCK_TICKS) {
      const c = w.path[Math.min(w.path.length - 1, w.i)], dy = loc.y - c[2];
      const cause = w.mode === "direct" ? "direct" : dy < -2.5 ? "below" : dy > 2.5 ? "above" : "level";
      stuckBy[cause]++;
      w.cause = cause;
      let feet = "?";
      try { feet = (API.blockAt ? API.blockAt(v.dimension, Math.floor(loc.x), Math.floor(loc.y), Math.floor(loc.z)) : null)?.typeId.replace("minecraft:", "") || "?"; } catch { /* left */ }   // 1.3.228: guarded
      w.feet = feet;
      const tkey = `${Math.floor(w.target.x)},${Math.floor(w.target.z)}`;
      const tr = tries.get(vid);
      const n = tr && tr.key === tkey ? tr.n + 1 : 1;
      tries.set(vid, { key: tkey, n, until: now + BACKOFF[Math.min(n, BACKOFF.length - 1)] });
      API.stuck(v, w); cancel(v);
    }
   } catch (e) {
    beatErrors++;
    if (beatErrors <= 3 || beatErrors % 100 === 0) console.warn(`[CIV-WALK] beat (${beatErrors}): ${e}`);
    try { walkers.delete(vid); slotOf.delete(vid); } catch { /* left */ }
   }
  }
} });
let beatErrors = 0;
