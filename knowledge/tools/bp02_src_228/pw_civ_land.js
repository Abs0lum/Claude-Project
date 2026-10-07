// pw_civ_land.js — CIVITAS WORLD-SHAPING step 1 (his 22:24 "it literally creates the actual world"): the LAND as data,
// and STREETS ON CONTOURS. Pure functions over a heightfield (no engine imports: the clock reads the world into the field
// and lays what these functions plan), so the same code runs live, in the probe and in the node tests.
//
// SITE   { x0, z0, w, d, h: Int16Array(w*d) ground y per column (-1 = unknown / water), water: Uint8Array(w*d) }
//        site.at(x, z) -> ground y (undefined outside / unknown); site.isWater(x, z)
// SQUARE the flattest 12 x 12 knoll within R of a point: min (max - min) of the window, no water, prefer closer.
// CONTOUR WALK  from the square along +x and -x: each step picks the next column (dz in -2..2) whose ground is nearest the
//        street's running height h0; the running height may drift by one block every DRIFT cells (the street follows the
//        hillside); stops at water, at a cliff (|dh| > 3 everywhere), or at LEN cells. The walk is then SNAPPED into
//        axis-aligned RUNS (east-west runs joined by short north-south jogs) so plots keep their four rotations.
// PROFILE each street cell gets a laid height: the smoothed walk height (<= 1 step per cell). Plots never touch it.
export const STREET_W = 3;
export const SETBACK = 2;          // the FRONT YARD: two cells between a plot's front wall and the street body — the stoop climbs here, never on the street (run 0.0.13: stoops crossed the street, +2 spikes in its middle row)
export const WALK_LEN = 80, DRIFT = 4, SQUARE = 12, SQUARE_R = 36;

export function makeSite(x0, z0, w, d) {
  const h = new Int16Array(w * d).fill(-1);
  const water = new Uint8Array(w * d);
  const site = { x0, z0, w, d, h, water };
  site.idx = (x, z) => (x - x0) + (z - z0) * w;
  site.inside = (x, z) => x >= x0 && z >= z0 && x < x0 + w && z < z0 + d;
  site.at = (x, z) => { if (!site.inside(x, z)) return undefined; const v = h[site.idx(x, z)]; return v < 0 ? undefined : v; };
  site.isWater = (x, z) => site.inside(x, z) && water[site.idx(x, z)] === 1;
  site.set = (x, z, y, isWater) => { if (site.inside(x, z)) { h[site.idx(x, z)] = y; water[site.idx(x, z)] = isWater ? 1 : 0; } };
  return site;
}

/** the flattest SQUARE x SQUARE window within SQUARE_R of (cx, cz) — returns {x, z, y (median), relief} or null */
export function findSquare(site, cx, cz, size = SQUARE, R = SQUARE_R) {
  let best = null;
  for (let x = cx - R; x <= cx + R - size; x += 2) for (let z = cz - R; z <= cz + R - size; z += 2) {
    let lo = 1e9, hi = -1e9, bad = false;
    const ys = [];
    for (let i = 0; i < size && !bad; i += 2) for (let j = 0; j < size; j += 2) {
      const y = site.at(x + i, z + j);
      if (y === undefined || site.isWater(x + i, z + j)) { bad = true; break; }
      ys.push(y); if (y < lo) lo = y; if (y > hi) hi = y;
    }
    if (bad) continue;
    const relief = hi - lo;
    const dist = Math.abs(x + size / 2 - cx) + Math.abs(z + size / 2 - cz);
    const score = relief * 10 + dist * 0.2;
    if (!best || score < best.score) { ys.sort((a, b) => a - b); best = { x, z, y: ys[ys.length >> 1], relief, score }; }
  }
  return best;
}

/** walk a contour from (sx, sz) at height h0 in direction dir (+1 east / -1 west); returns [[x, z, h], ...] */
export function walkContour(site, sx, sz, h0, dir, len = WALK_LEN) {
  const cells = [[sx, sz, h0]];
  let x = sx, z = sz, hRun = h0, sinceDrift = DRIFT;
  for (let n = 0; n < len; n++) {
    const nx = x + dir;
    let pick = null;
    for (const dz of [0, -1, 1, -2, 2]) {
      const nz = z + dz;
      const y = site.at(nx, nz);
      if (y === undefined || site.isWater(nx, nz)) continue;
      const cost = Math.abs(y - hRun) * 4 + Math.abs(dz);
      if (!pick || cost < pick.cost) pick = { nz, y, cost };
    }
    if (!pick || Math.abs(pick.y - hRun) > 3) break;                 // water / unknown ahead, or a cliff
    if (pick.y !== hRun && sinceDrift >= DRIFT) { hRun += Math.sign(pick.y - hRun); sinceDrift = 0; } else sinceDrift++;
    x = nx; z = pick.nz;
    cells.push([x, z, hRun]);
  }
  return cells;
}

/** snap a walk into axis-aligned runs: east-west runs at a fixed z, joined by north-south jogs. Returns the run list and
 *  the street cells (every cell of every run and jog, with the run's profile height). */
export function snapRuns(walk, minRun = 12) {
  if (walk.length < 2) return { runs: [], cells: walk.slice() };
  // group consecutive cells by z: a run is a stretch at one z of at least minRun cells; shorter stretches are absorbed
  // into the neighbouring run's z (the street stays straight there) unless the ground forces a jog
  const groups = [];
  for (const c of walk) {
    const g = groups[groups.length - 1];
    if (g && g.z === c[1]) g.cells.push(c); else groups.push({ z: c[1], cells: [c] });
  }
  // absorb short groups into the longer neighbour
  let merged = true;
  while (merged && groups.length > 1) {
    merged = false;
    for (let i = 0; i < groups.length; i++) {
      if (groups[i].cells.length >= minRun) continue;
      const nb = i > 0 && (i === groups.length - 1 || groups[i - 1].cells.length >= groups[i + 1].cells.length) ? i - 1 : i + 1;
      if (nb < 0 || nb >= groups.length) continue;
      const target = groups[nb];
      for (const c of groups[i].cells) target.cells.push([c[0], target.z, c[2]]);
      target.cells.sort((a, b) => a[0] - b[0]);
      groups.splice(i, 1);
      merged = true;
      break;
    }
  }
  const dir = Math.sign(walk[walk.length - 1][0] - walk[0][0]) || 1;
  const runs = groups.map((g) => {
    const xs = g.cells.map((c) => c[0]);
    return { axis: "x", z: g.z, x0: Math.min(...xs), x1: Math.max(...xs), cells: g.cells.slice().sort((a, b) => a[0] - b[0]) };
  });
  // jogs between runs (north-south), stepping the height between the runs' end heights
  const cells = [];
  for (let i = 0; i < runs.length; i++) {
    for (const c of runs[i].cells) cells.push([c[0], c[1], c[2]]);
    if (i + 1 < runs.length) {
      const a = runs[i], b = runs[i + 1];
      const xj = dir > 0 ? a.x1 : a.x0;
      const ha = a.cells[dir > 0 ? a.cells.length - 1 : 0][2], hb = b.cells[dir > 0 ? 0 : b.cells.length - 1][2];
      const zs = a.z < b.z ? [a.z + 1, b.z - 1] : [b.z + 1, a.z - 1];
      const n = Math.abs(b.z - a.z) - 1;
      for (let k = 1; k <= n; k++) {
        const z = a.z + Math.sign(b.z - a.z) * k;
        const h = Math.round(ha + (hb - ha) * (k / (n + 1)));
        cells.push([xj, z, h]);
      }
      runs[i].jog = { x: xj, z0: zs[0], z1: zs[1] };
      // the jog column (and the street's width beside it) is no plot's frontage: shrink the usable range of both runs
      if (dir > 0) { runs[i].ux1 = a.x1 - STREET_W; runs[i + 1].ux0 = b.x0 + STREET_W; }
      else { runs[i].ux0 = a.x0 + STREET_W; runs[i + 1].ux1 = b.x1 - STREET_W; }
    }
  }
  return { runs, cells };
}

/** smooth a profile so neighbours never differ by more than one block (the higher side comes down); in place */
export function smoothProfile(cells) {
  // along the list no step > 1; around a JOG (a cell that moved across the street's direction: same first coordinate
  // as the cell before it) the five cells i-2..i+2 stay within one block of each other — their 3-wide bodies touch
  // side by side, and run 0.0.16 read a 2-block step down the middle row at a jog (98 / 97 / 96 over two list steps)
  for (let pass = 0; pass < 128; pass++) {
    let changed = false;
    for (let i = 1; i < cells.length; i++) {
      if (cells[i][2] > cells[i - 1][2] + 1) { cells[i][2] = cells[i - 1][2] + 1; changed = true; }
      if (cells[i - 1][2] > cells[i][2] + 1) { cells[i - 1][2] = cells[i][2] + 1; changed = true; }
    }
    for (let i = 1; i < cells.length; i++) {
      if (cells[i][0] !== cells[i - 1][0]) continue;                 // not a jog cell
      const a = Math.max(0, i - 2), b = Math.min(cells.length - 1, i + 2);
      let lo = Infinity;
      for (let k = a; k <= b; k++) lo = Math.min(lo, cells[k][2]);
      for (let k = a; k <= b; k++) if (cells[k][2] > lo + 1) { cells[k][2] = lo + 1; changed = true; }
    }
    if (!changed) break;
  }
  return cells;
}

/** the site seen with x and z swapped: the same planner then lays NORTH-SOUTH streets (a hillside whose contours run
 *  north-south — the first hill town showed a 90-cell "jog" because only east-west runs were known) */
export function transposed(site) {
  return { x0: site.z0, z0: site.x0, w: site.d, d: site.w, transposed: true,
           at: (x, z) => site.at(z, x), isWater: (x, z) => site.isWater(z, x), inside: (x, z) => site.inside(z, x) };
}

/** plan one axis: the square, then contour walks both ways from its edge, snapped and smoothed (in the site's frame) */
function planAxis(site, cx, cz) {
  const sq = findSquare(site, cx, cz);
  if (!sq) return null;
  const sz = sq.z + SQUARE;                       // the street runs along the square's "south" edge (in this frame)
  const h0 = site.at(sq.x + (SQUARE >> 1), sz) ?? sq.y;
  const east = walkContour(site, sq.x + SQUARE - 1, sz, h0, +1);
  const west = walkContour(site, sq.x, sz, h0, -1);
  const frontage = [];                                              // the square's own frontage: level at h0, never a hole
  for (let x = sq.x; x < sq.x + SQUARE - 1; x++) frontage.push([x, sz, h0]);
  const walk = west.slice(1).reverse().concat(frontage, east);
  const { runs, cells } = snapRuns(walk);
  smoothProfile(cells);
  const usable = runs.reduce((a, r) => a + Math.max(0, (r.ux1 ?? r.x1) - (r.ux0 ?? r.x0)), 0);
  const jogs = cells.length - runs.reduce((a, r) => a + r.cells.length, 0);
  return { square: sq, h0, runs, cells, usable, jogs };
}

/** plan the main street on BOTH axes and keep the one with more plot frontage (fewer jog cells breaks ties).
 *  Everything returned is in WORLD coordinates: cells [x, z, h]; runs carry axis "x" (east-west, at a fixed z) or "z"
 *  (north-south, at a fixed x) and stay in their own frame for the slot allocator; profile: Map "x,z" -> h. */
export function planMainStreet(site, cx, cz, seed = 0) {
  const px = planAxis(site, cx, cz);
  const pz = planAxis(transposed(site), cz, cx);
  let best, axis;
  if (px && pz) { const zWins = pz.usable > px.usable * 1.15 || (pz.usable >= px.usable && pz.jogs < px.jogs); best = zWins ? pz : px; axis = zWins ? "z" : "x"; }
  else if (px) { best = px; axis = "x"; } else if (pz) { best = pz; axis = "z"; } else return null;
  const w = (c) => (axis === "z" ? [c[1], c[0], c[2]] : [c[0], c[1], c[2]]);     // frame -> world
  const cells = best.cells.map(w);
  const profile = new Map();
  for (const c of cells) profile.set(`${c[0]},${c[1]}`, c[2]);
  for (const r of best.runs) { r.axis = axis; for (const c of r.cells) { const wc = w(c); c[2] = profile.get(`${wc[0]},${wc[1]}`); } }
  const square = axis === "z" ? { x: best.square.z, z: best.square.x, y: best.square.y, relief: best.square.relief } : best.square;
  return { square, h0: best.h0, axis, runs: best.runs, cells, profile, usable: best.usable };
}

/** a slot from the run's frame to the world: on a north-south run the "N" side is WEST (fronts face east, Rotate180)
 *  and the "S" side is EAST (fronts face west, None); the footprint swaps back. */
export function slotToWorld(slot) {
  if (!slot) return null;
  const yard = slot.yard || 0;
  // the whole plot in the frame: structure + yard (the yard lies between the structure and the street body)
  const fz0 = slot.side === "N" ? slot.z : slot.z - yard, fz1 = slot.side === "N" ? slot.z + slot.fz - 1 + yard : slot.z + slot.fz - 1;
  if (slot.run.axis !== "z") return { ...slot, wx: slot.x, wz: slot.z, wrot: slot.rot, wfx: slot.fx, wfz: slot.fz, streetRow: slot.run.z, axis: "x",
                                      box: [slot.x, slot.x + slot.fx - 1, fz0, fz1] };
  return { ...slot, wx: slot.z, wz: slot.x, wrot: slot.side === "N" ? 2 : 0, wfx: slot.fz, wfz: slot.fx, streetCol: slot.run.z, axis: "z",
           box: [fz0, fz1, slot.x, slot.x + slot.fx - 1] };
}

/** the size a building takes in a run's frame: along the run (fx) and away from it (fz) — the same on both axes */
export function sizeInFrame(def) {
  return { fx: def.size[2], fz: def.size[0] };
}

/** plot slots along a run: both sides, packed from the run's middle outward; a slot = {x, z, rot, fx, fz, side} */
export function slotsAlongRun(run, sizes, gap = 1, isFree = () => true) {
  // sizes: [{family, fx, fz}] in the order they should be placed; alternate north / south, from the middle out.
  // isFree(slot) is the world's veto (another plot, a street, the square): a vetoed place is skipped (its x is burnt on
  // that side so the next plot does not land there either) and the other direction, then the other side, are tried.
  const X0 = run.ux0 ?? run.x0, X1 = run.ux1 ?? run.x1;
  const mid = (X0 + X1) >> 1;
  const out = [];
  if (!run.edge) run.edge = { N: { e: mid, w: mid - 1 - gap }, S: { e: mid, w: mid - 1 - gap } };   // next free x east / west per side (kept on the run); a gap between the two middle plots too
  const edge = run.edge;
  let side = run.nextSide || "N", dirE = run.nextDirE ?? true;
  const tryPlace = (sd, east, s) => {
    const e = edge[sd];
    for (let attempt = 0; attempt < 6; attempt++) {           // walk past vetoed places along this direction
      let x;
      if (east) { x = e.e; if (x + s.fx - 1 > X1) return null; }
      else { x = e.w - s.fx + 1; if (x < X0) return null; }
      const slot = { x, z: sd === "N" ? run.z - s.fz - SETBACK : run.z + STREET_W + SETBACK, rot: sd === "N" ? 3 : 1, fx: s.fx, fz: s.fz, side: sd, run, yard: SETBACK };
      if (isFree(slot)) { if (east) e.e = x + s.fx + gap; else e.w = x - 1 - gap; return slot; }
      if (east) e.e += 2; else e.w -= 2;                       // burn two cells and look further out
    }
    return null;
  };
  for (const s of sizes) {
    let slot = tryPlace(side, dirE, s) || tryPlace(side, !dirE, s);
    if (!slot) { const other = side === "N" ? "S" : "N"; slot = tryPlace(other, dirE, s) || tryPlace(other, !dirE, s); }
    out.push(slot);
    if (slot) {
      side = slot.side === "N" ? "S" : "N";
      if (side === "N") dirE = !dirE;
      run.nextSide = side; run.nextDirE = dirE;
    }
  }
  return out;
}

/** plot slots along a whole street: the longest run first, then the others; returns one slot (or null) per size, in order */
export function slotsAlongStreet(runs, sizes, gap = 1, isFree = () => true) {
  const order = runs.slice().sort((a, b) => (b.x1 - b.x0) - (a.x1 - a.x0));
  const out = new Array(sizes.length).fill(null);
  let pending = sizes.map((s, i) => ({ ...s, i }));
  for (const run of order) {
    if (!pending.length) break;
    const got = slotsAlongRun(run, pending, gap, isFree);
    const left = [];
    got.forEach((slot, k) => { if (slot) out[pending[k].i] = slot; else left.push(pending[k]); });
    pending = left;
  }
  return out;
}

// ------------------------------------------------------------------------------------------------ roads (step 7, run 0.0.11)
// The first road walker was greedy: on a slope a step toward the goal that climbs costs more than a step away on the
// flat, so it oscillated until its 600-cell guard, and it was laid straight through plots and across streets (re-profiled:
// bigStep 12 -> 49, cottage #45 cut). This is A* over the real ground, as a generator for system.runJob (yields every
// `batch` expansions). ground(x, z) -> {g, water} | undefined (undefined = unknown or impassable); blocked(x, z) -> true
// for cells a road must never cross (every plot's box + 1, the squares); fixedH(x, z) -> a height when the cell is an
// existing street cell (passable at that grade, never re-laid). Moves: 8 neighbours; cost = step (1 / 1.4) + 3 per block
// of rise or fall + 6 through water. Returns (via onDone) the cell list [x, z, h] from a to b, or null when no path.
export const ROAD_SLOPE = 3, ROAD_WATER = 6, ROAD_MARGIN = 40, ROAD_MAX_NODES = 60000;

class MinHeap {
  constructor() { this.a = []; }
  push(k, v) { const a = this.a; a.push([k, v]); let i = a.length - 1; while (i > 0) { const p = (i - 1) >> 1; if (a[p][0] <= a[i][0]) break; [a[p], a[i]] = [a[i], a[p]]; i = p; } }
  pop() { const a = this.a; const top = a[0]; const last = a.pop(); if (a.length) { a[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < a.length && a[l][0] < a[m][0]) m = l; if (r < a.length && a[r][0] < a[m][0]) m = r; if (m === i) break; [a[m], a[i]] = [a[i], a[m]]; i = m; } } return top; }
  get size() { return this.a.length; }
}

export function* findRoadJob(a, b, ground, blocked, fixedH, onDone, opts = {}) {
  const margin = opts.margin ?? ROAD_MARGIN, maxNodes = opts.maxNodes ?? ROAD_MAX_NODES, batch = opts.batch ?? 256;
  const x0 = Math.min(a.x, b.x) - margin, x1 = Math.max(a.x, b.x) + margin, z0 = Math.min(a.z, b.z) - margin, z1 = Math.max(a.z, b.z) + margin;
  const key = (x, z) => x * 65536 + (z + 32768);
  const cache = new Map();
  const cellAt = (x, z) => {
    const k = key(x, z);
    if (cache.has(k)) return cache.get(k);
    let c;
    const fh = fixedH ? fixedH(x, z) : undefined;
    if (fh !== undefined) c = { g: fh, water: false, street: true };
    else { const gr = ground(x, z); c = gr ? { g: gr.g, water: !!gr.water, street: false } : undefined; }
    cache.set(k, c);
    return c;
  };
  const h = (x, z) => { const dx = Math.abs(b.x - x), dz = Math.abs(b.z - z); return Math.max(dx, dz) + 0.4 * Math.min(dx, dz); };
  const start = cellAt(a.x, a.z);
  if (!start) { onDone(null, "start unknown"); return; }
  const open = new MinHeap();
  const best = new Map();                       // key -> {g, px, pz, h}
  best.set(key(a.x, a.z), { cost: 0, px: null, pz: null, h: start.g });
  open.push(h(a.x, a.z), [a.x, a.z, 0]);
  let expanded = 0, found = false;
  const MOVES = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, 1.4], [1, -1, 1.4], [-1, 1, 1.4], [-1, -1, 1.4]];
  while (open.size && expanded < maxNodes) {
    const [, [x, z, cost]] = open.pop();
    const cur = best.get(key(x, z));
    if (!cur || cur.cost < cost) continue;      // a stale heap entry
    if (x === b.x && z === b.z) { found = true; break; }
    expanded++;
    for (const [mx, mz, step] of MOVES) {
      const nx = x + mx, nz = z + mz;
      if (nx < x0 || nx > x1 || nz < z0 || nz > z1) continue;
      const goal = nx === b.x && nz === b.z;
      if (!goal && blocked && blocked(nx, nz)) continue;
      const c = cellAt(nx, nz);
      if (!c) continue;
      const nc = cost + step + Math.abs(c.g - cur.h) * ROAD_SLOPE + (c.water ? ROAD_WATER : 0);
      const k = key(nx, nz);
      const prev = best.get(k);
      if (prev && prev.cost <= nc) continue;
      best.set(k, { cost: nc, px: x, pz: z, h: c.g });
      open.push(nc + h(nx, nz), [nx, nz, nc]);
    }
    if (expanded % batch === 0) yield;
  }
  if (!found) { onDone(null, `no path (${expanded} nodes)`); return; }
  const cells = [];
  let x = b.x, z = b.z;
  while (x !== null) { const n = best.get(key(x, z)); cells.push([x, z, n.h]); x = n.px; z = n.pz; }
  cells.reverse();
  onDone(cells, `${cells.length} cells, ${expanded} nodes`);
}

/** run a generator to completion synchronously (tests, catch-up) */
export function runJobNow(gen) { let r = gen.next(); while (!r.done) r = gen.next(); }

/** the street BODY: every laid cell of a settlement's streets from its profile keys (the run's own row/column), 3 wide
 *  on the settlement's axis ("x": z..z+2 below the key row; "z": x..x+2 east of the key column) plus the centred cross
 *  body of jog cells (a key with another key in its own column (axis x) / row (axis z)). Returns Map "x,z" -> h. */
export function streetBody(profile, axis = "x") {
  const keys = profile instanceof Map ? [...profile.entries()] : Object.entries(profile || {});
  const has = new Set(keys.map(([k]) => k));
  const body = new Map();
  for (const [k, h] of keys) {
    const [x, z] = k.split(",").map(Number);
    const jog = axis === "z" ? (has.has(`${x - 1},${z}`) || has.has(`${x + 1},${z}`)) : (has.has(`${x},${z - 1}`) || has.has(`${x},${z + 1}`));
    for (let w = 0; w < STREET_W; w++) { if (axis === "z") body.set(`${x + w},${z}`, h); else body.set(`${x},${z + w}`, h); }
    if (jog) for (let w = -1; w <= 1; w++) { if (axis === "z") body.set(`${x},${z + w}`, h); else body.set(`${x + w},${z}`, h); }
  }
  return body;
}

/** the cells ONE key of a planned street lays, as [cx, cz, w, vertical]: a RUN cell lays its 3-wide body on the far
 *  side of the key row / column (the slot law: z..z+2 on an x street, x..x+2 on a z street); a JOG cell and every road
 *  cell lay a 3-wide cross centred across the travel; a run's FIRST cell after a jog lays both, so the corridor turns the
 *  corner as a solid L. A cell's role comes from EITHER sequence neighbour (GS-1, D-C505: judged from the previous cell
 *  alone, every run's first cell was laid as a cross and its two body cells were never laid). vertical = the travel runs
 *  along z at that cell (bridge piers, cutting walls). axis null = a road (direction from the neighbours). */
export function layShapes(cells, i, axis) {
  const [x, z] = cells[i];
  const prev = i > 0 ? cells[i - 1] : null;
  const next = i + 1 < cells.length ? cells[i + 1] : null;
  const movedZ = !!((prev && prev[0] === x && prev[1] !== z) || (!prev && next && next[0] === x));
  const continues = (c) => (axis === "x" ? c[1] === z && c[0] !== x : c[0] === x && c[1] !== z);
  const runCell = !!(axis && ((next && continues(next)) || (prev && continues(prev))));
  const crossX = axis ? axis === "x" : movedZ;                       // a jog on an x street travels along z: width across x
  const bodyVertical = axis ? (axis === "x" ? !runCell : runCell) : movedZ;
  const shapes = [];
  for (let w = 0; w < STREET_W; w++) {
    if (runCell) shapes.push(axis === "x" ? [x, z + w, w, bodyVertical] : [x + w, z, w, bodyVertical]);
    else shapes.push(crossX ? [x + w - 1, z, w, bodyVertical] : [x, z + w - 1, w, bodyVertical]);
  }
  const turnCell = runCell && prev && !continues(prev);
  if (turnCell) for (let w = 0; w < STREET_W; w++) {
    const c = crossX ? [x + w - 1, z, w, !bodyVertical] : [x, z + w - 1, w, !bodyVertical];
    if (!shapes.some((q) => q[0] === c[0] && q[1] === c[1])) shapes.push(c);
  }
  return shapes;
}

/** the world's veto for a frame slot: its own box may touch no street body cell and not the square; its box plus a
 *  one-cell margin may touch no standing plot (boxes = [x0, x1, z0, z1] inclusive, world). */
export function slotVeto(body, boxes, square) {
  const inBox = (x, z, bx) => x >= bx[0] && x <= bx[1] && z >= bx[2] && z <= bx[3];
  const sq = square ? [square.x, square.x + SQUARE - 1, square.z, square.z + SQUARE - 1] : null;
  return (slot0) => {
    const slot = slotToWorld(slot0);
    const [bx0, bx1, bz0, bz1] = slot.box;                          // structure + yard
    for (let x = bx0; x <= bx1; x++) for (let z = bz0; z <= bz1; z++) {
      if (body.has(`${x},${z}`)) return false;
      if (sq && inBox(x, z, sq)) return false;
    }
    for (let x = bx0 - 1; x <= bx1 + 1; x++) for (let z = bz0 - 1; z <= bz1 + 1; z++) {
      if (boxes.some((bx) => inBox(x, z, bx))) return false;
    }
    return true;
  };
}

// ------------------------------------------------------------------------------------------------ THE WIDE SURVEY (1.3.231, CIV-LAND)
// His 00:23 CT 10-07: "survey a MUCH larger area and plan for elevation". The founding reads a 160 x 160 field (the clock's
// SITE_R = 80) around the founding point; everything a town plans beyond it — benches 70..110 blocks past its streets, the
// bands up a hill, its roads — was read live, cell by cell, and only where a chunk happened to be loaded (his survey reply:
// "2173 of 2401 columns were not loaded"). The WIDE SURVEY grows the field to WIDE.R (192: 384 x 384) — and further as the
// boundary stones move out (border + WIDE.margin, at most WIDE.Rmax) — after the founding, in the background: TILES of
// 128 x 128 (8 x 8 chunks, chunk-aligned; one ticking area of <= 10 x 10 chunks each, the engine's cap) nearest first. A
// tile already loaded is read at once; a sleeping one is held awake by ONE ticking area at a time, read when its chunks
// load, then released. The founding's own field (the "before" ground the planners compare against) is never overwritten.
export const WIDE = { R: 192, Rmax: 320, margin: 96, tile: 128, waitPolls: 6, holdTries: 12, yieldEvery: 256 };

/** the radius the wide survey should cover for a boundary ring of radius borderR (16-block steps, R .. Rmax) */
export function wideRadius(borderR = 0) {
  return Math.min(WIDE.Rmax, Math.max(WIDE.R, Math.ceil((borderR + WIDE.margin) / 16) * 16));
}

/** the tiles [x0, z0, x1, z1] (inclusive, chunk-aligned, tile x tile) covering the square [cx - R, cx + R) x [cz - R, cz + R),
 *  without those wholly inside `have` (a site already read: { x0, z0, w, d }), nearest the centre first */
export function surveyTiles(cx, cz, R, tile = WIDE.tile, have = null) {
  const a = (v) => Math.floor(v / tile) * tile;
  const out = [];
  for (let x = a(cx - R); x < cx + R; x += tile) for (let z = a(cz - R); z < cz + R; z += tile) {
    const t = [x, z, x + tile - 1, z + tile - 1];
    if (have && t[0] >= have.x0 && t[1] >= have.z0 && t[2] < have.x0 + have.w && t[3] < have.z0 + have.d) continue;
    out.push(t);
  }
  const d2 = (t) => ((t[0] + t[2]) / 2 - cx) ** 2 + ((t[1] + t[3]) / 2 - cz) ** 2;
  out.sort((p, q) => d2(p) - d2(q) || p[0] - q[0] || p[1] - q[1]);
  return out;
}

/** a new field of radius R around (cx, cz) holding every known cell of `core` (and of `wide`, an earlier wide field) */
export function growSite(core, cx, cz, R, wide = null) {
  const site = makeSite(cx - R, cz - R, 2 * R, 2 * R);
  for (const src of [wide, core]) {                              // the core last: its "before" ground always wins
    if (!src) continue;
    const xa = Math.max(site.x0, src.x0), xb = Math.min(site.x0 + site.w, src.x0 + src.w);
    const za = Math.max(site.z0, src.z0), zb = Math.min(site.z0 + site.d, src.z0 + src.d);
    for (let z = za; z < zb; z++) for (let x = xa; x < xb; x++) {
      const i = src.idx(x, z);
      if (src.h[i] < 0) continue;
      const j = site.idx(x, z);
      site.h[j] = src.h[i]; site.water[j] = src.water[i];
    }
  }
  return site;
}

/** the survey's progress: { site, core, tiles, i, held, read, asleep, kept, skipped: [tile...], tries } */
export function wideProgress(core, cx, cz, R, wide = null) {
  const site = growSite(core, cx, cz, R, wide);
  // a tile is surveyed while any of its columns inside the field is still unknown (a re-run reads only the tiles that never
  // woke, and the columns the founding could not read)
  const unknownIn = (t) => {
    for (let x = Math.max(t[0], site.x0); x <= Math.min(t[2], site.x0 + site.w - 1); x++)
      for (let z = Math.max(t[1], site.z0); z <= Math.min(t[3], site.z0 + site.d - 1); z++) if (site.h[site.idx(x, z)] < 0) return true;
    return false;
  };
  const tiles = surveyTiles(cx, cz, R, WIDE.tile, null).filter(unknownIn);
  return { cx, cz, R, site, core, tiles, i: 0, held: null, read: 0, asleep: 0, kept: 0, skipped: [], tries: 0 };
}

/** ONE PASS of the wide survey (a generator for system.runJob; the clock runs a pass, and again after a pause while it
 *  answers "wait"). io = { loaded(tile) -> every chunk of the tile is loaded; column(x, z) -> { g, water } | null (asleep)
 *  | undefined (no ground); hold(tile) -> a handle (a ticking area over the tile) | null (no slot free); release(handle) }.
 *  Cells the field already knows are kept (never read again). Returns "done" | "wait". */
export function* wideSurveyPass(prog, io) {
  const site = prog.site;
  while (prog.i < prog.tiles.length) {
    const tile = prog.tiles[prog.i];
    if (!io.loaded(tile)) {
      if (!prog.held || prog.held.i !== prog.i) {
        const h = io.hold(tile);
        if (!h) {                                                 // no ticking slot free: wait, and give the tile up after holdTries
          if (++prog.tries > WIDE.holdTries) { prog.skipped.push(tile); prog.i++; prog.tries = 0; continue; }
          return "wait";
        }
        prog.held = { i: prog.i, h, polls: 0 };
        prog.tries = 0;
        return "wait";
      }
      if (++prog.held.polls > WIDE.waitPolls) {                   // its chunks never loaded: let it go, on to the next tile
        io.release(prog.held.h); prog.held = null;
        prog.skipped.push(tile); prog.i++;
        continue;
      }
      return "wait";
    }
    let n = 0;
    for (let x = tile[0]; x <= tile[2]; x++) for (let z = tile[1]; z <= tile[3]; z++) {
      if (!site.inside(x, z)) continue;
      if (site.at(x, z) !== undefined) { prog.kept++; continue; }
      const c = io.column(x, z);
      if (c === null) prog.asleep++;
      else if (c) { site.set(x, z, c.g, !!c.water); prog.read++; }
      if (++n % WIDE.yieldEvery === 0) yield;
    }
    if (prog.held && prog.held.i === prog.i) { io.release(prog.held.h); prog.held = null; }
    prog.i++;
    yield;
  }
  return "done";
}

// ------------------------------------------------------------------------------------------------ the site field as text (1.3.231)
// The field lives in dynamic properties (the clock's saveSite, 30,000 characters a property). The old text (one "v*n" run
// per change of v = ground * 2 + water) takes ~2 characters a column on hills; a 384 x 384 field would be ~300 KB. "d1":
// row-major, each column's v as a DELTA from the column before it, one character per delta (-30..+30 from DELTA_ABC),
// "~<v base 36>;" beyond that, and a run of one delta written once with "(<count base 36>)" after it (repeats).
const DELTA_ABC = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy";   // 61 characters: delta + 30
export function siteEncode(site) {
  const out = [];
  let prev = 0, last = null, run = 0;
  const flush = () => { if (last === null) return; out.push(last); if (run > 1) out.push(run === 2 ? last : `(${(run - 1).toString(36)})`); last = null; run = 0; };
  for (let i = 0; i < site.h.length; i++) {
    const v = site.h[i] * 2 + site.water[i];
    const d = v - prev;
    prev = v;
    const tok = d >= -30 && d <= 30 ? DELTA_ABC[d + 30] : `~${v.toString(36)};`;
    if (tok.length === 1 && tok === last) { run++; continue; }
    flush();
    if (tok.length === 1) { last = tok; run = 1; } else out.push(tok);
  }
  flush();
  return { x0: site.x0, z0: site.z0, w: site.w, d: site.d, enc: "d1", data: out.join("") };
}
/** text -> field: the "d1" text, or the old run list ({ rle }) */
export function siteDecode(r) {
  const site = makeSite(r.x0, r.z0, r.w, r.d);
  if (r.enc !== "d1") {
    let i = 0;
    for (const runTxt of r.rle.split(",")) {
      const [v, n] = runTxt.split("*").map(Number);
      const cnt = n || 1;
      for (let k = 0; k < cnt; k++, i++) { site.h[i] = Math.floor(v / 2); site.water[i] = v & 1; }
    }
    return site;
  }
  const s = r.data, N = site.h.length;
  let i = 0, p = 0, prev = 0, lastD = null;
  const put = (v) => { if (i < N) { site.h[i] = Math.floor(v / 2); site.water[i] = v & 1; } i++; prev = v; };
  while (p < s.length && i < N) {
    const ch = s[p];
    if (ch === "~") { const e = s.indexOf(";", p); put(parseInt(s.slice(p + 1, e), 36)); lastD = null; p = e + 1; continue; }
    if (ch === "(") { const e = s.indexOf(")", p); const n = parseInt(s.slice(p + 1, e), 36); for (let k = 0; k < n; k++) put(prev + lastD); p = e + 1; continue; }
    lastD = DELTA_ABC.indexOf(ch) - 30;
    put(prev + lastD);
    p++;
  }
  return site;
}
