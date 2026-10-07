// pw_civ_streets.js — CIVITAS STREETS FROM HIS STREETKIT (v1.3.219, his 17:37 / 18:01 / 18:13 / 18:15 rulings, D-C529/530).
// Pure functions (no engine imports): the clock reads the land into a site field and places what these plan; the same code
// runs in the node tests and the workspace server probe.
//
// THE KIT (BP structures/pw/road/, tools/road_kit.py, his own pieces): every piece is 13 wide; native orientation = travel
// along +x, width along z (0..12). Surface: sidewalk block y = origin + 14 ("H"), road block y = origin + 13.
//   straight1 (1 long) · access3 (3 long, side galleries into the sewer + utility tunnel, middle slice) · ramp7 (7 long, +1
//   block from x0 to x6, 16 tall) · dead13 (13 x 13, open on native -z only) · tee13 (open -z, +z, +x) · cross13 · elbow13
//   village width = prefix "v_" (5 road + grass verges), town width = "t_" (7 road); substructure identical.
// A STREET is straight (a 13-wide corridor cannot jog by one or two cells): frame {ox, oz, ux, uz, vx, vz}: world cell of
// (t, w) = (ox + t*ux + w*vx, oz + t*uz + w*vz); t = travel 0..len-1, w = width 0..12. Its PROFILE comes from a dynamic
// programme over the ground: flat cells + ramps (one block per 7 cells, chains allowed, flat runs between ramps >= 3),
// a dead end at each end, bridges where the ground falls more than BRIDGE_DROP below the street or there is water.
// Houses stand FLUSH on the corridor (w = -1 / w = 13 is their front wall), on flat stretches only; each house's sewer
// shaft gets an access piece centred on it. Junction windows (13 flat cells) are kept free for the tee of a future street.

export const W = 13;                       // corridor width
export const DEAD = 13, RAMP = 7, ACCESS = 3, JUNCTION = 13;
// 1.3.228 (his 12:20 + 13:40, 10-06): the 8-BLOCK RAMP (pw:ramp_<mat>_8_e1..e8, one block over 8 cells, ~7 deg) is the
// PREFERRED street ramp (street piece ramp8); his 7-cell ramp7 (the 4-part ramp + a 3-cell landing) only where there is no
// room for it (steep land, short stretches, switchbacks). opts.ramp8 turns the choice on (streets; the narrow roads keep
// the 4-part ramp).
export const RAMP8 = 8, RAMP7_EXTRA = 12;   // the 7-cell ramp costs 12 more: chosen only when the 8-ramp cannot fit or would cost far more earthwork
export const BRIDGE_DROP = 8;              // the ground this far below the sidewalk (or water) -> a plank bridge, no substructure
export const RULES = { strictDrop: true };   // the founding main street may relax it once (a settlement must stand somewhere)
export const BUILD_UP_MAX = 15;            // 1.3.224 (his 16:50): no street, embankment or dry-land pier over a drop of more than 15 at ANY column
export const MIN_FLAT = 3;                 // his 18:01 R1: strips are never shorter than 3
export const RAIL_GAP = 6;                 // his 18:01 R5: an opening in the bridge railing every 6 cells
export const SIDE_OFFSETS = [60, 73, 47, 54, 66, 40, 80, 90];   // corridor-to-corridor distance tried for a parallel street (D-C534 A5: pitch 60 first; 1.3.224: more pitches, so a parallel can find its own contour under the 15-drop rule)

// ------------------------------------------------------------------------------------------------ frames + rotations
export function frameOf(ox, oz, u, v) { return { ox, oz, ux: u[0], uz: u[1], vx: v[0], vz: v[1] }; }
export function cellOf(f, t, w) { return [f.ox + t * f.ux + w * f.vx, f.oz + t * f.uz + w * f.vz]; }
/** (x, z) -> (t, w) in the frame (inverse of cellOf for unit axis vectors) */
export function tw(f, x, z) { const dx = x - f.ox, dz = z - f.oz; return [dx * f.ux + dz * f.uz, dx * f.vx + dz * f.vz]; }

/** one clockwise quarter turn (seen from above, x east, z south) — the engine's Rotate90, as rotXZ in the clock */
const turn = ([dx, dz]) => [-dz, dx];
/** the rotation r (0..3) that carries the native direction `nat` onto the world direction `want` */
export function rotFor(nat, want) {
  let d = nat;
  for (let r = 0; r < 4; r++) { if (d[0] === want[0] && d[1] === want[1]) return r; d = turn(d); }
  throw new Error(`no rotation ${nat} -> ${want}`);
}
/** the min corner (x, z) of the box a piece covers: t in [ta, ta + len - 1], w in [0, 12] (or [w0, w1]) */
export function boxCorner(f, ta, len, w0 = 0, w1 = W - 1) {
  const a = cellOf(f, ta, w0), b = cellOf(f, ta + len - 1, w1);
  return [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[0], b[0]), Math.max(a[1], b[1])];
}

// ------------------------------------------------------------------------------------------------ the profile
/** ground along a frame: one {g, water} per t (median over the corridor width, every second cell), undefined = unknown */
export function groundAlong(site, f, t0, t1) {
  const out = [];
  for (let t = t0; t < t1; t++) {
    const gs = [];
    let wet = 0, n = 0;
    for (let w = 0; w < W; w += 2) {
      const [x, z] = cellOf(f, t, w);
      const g = site.at(x, z);
      if (g === undefined) continue;
      n++;
      if (site.isWater(x, z)) wet++;
      gs.push(g);
    }
    if (!gs.length) { out.push(undefined); continue; }
    gs.sort((a, b) => a - b);
    out.push({ g: gs[gs.length >> 1], water: wet * 2 > n, lo: gs[0], hi: gs[gs.length - 1] });
  }
  return out;
}

/** the cost of the sidewalk standing at H over ground c (cut costs a little more than fill; deep fill -> a bridge) */
export function cellCost(c, H) { return cellCostBase(c, H); }
function cellCostBase(c, H, drop = BRIDGE_DROP) {
  if (!c) return 30;                                       // unknown ground: strongly discouraged
  if (c.water) return H >= c.g + 2 ? 6 : Infinity;         // a bridge over water, deck at least 2 above it
  const d = H - c.g;
  if (RULES.strictDrop && H - (c.lo ?? c.g) > BUILD_UP_MAX) return Infinity;   // 1.3.224: the WORST column decides (the median let ridges through)
  if (d > drop) return 5 + 0.15 * d;                       // a bridge over a gully
  if (d >= 0) return d;                                    // fill (an embankment)
  return -d * 1.3 + (c.hi - H > 6 ? 2 : 0);                // a cutting (deep cuts a little dearer)
}
export const isBridgeCell = (c, H) => isBridgeCellBase(c, H);
const isBridgeCellBase = (c, H, drop = BRIDGE_DROP) => !!c && (c.water || H - c.g > drop);

/** plan the heights of one street: ground[] (index 0 = t0), options:
 *   startDead / endDead (default true): a dead end (13 flat) at that end · startH / endH: fixed sidewalk heights there
 *   flat: [[ta, tb], ...] windows (indices into ground[]) where no ramp may lie (junctions, the square's frontage)
 *   fixed: Map index -> H (the square's level)
 * Returns { cost, H: per-index sidewalk height (a ramp's first 4 cells at its low/entry H), segs: [{kind, a, len, H, dir}] }
 * kind: dead | flat | ramp (dir +1 up / -1 down, H = entry height) | bridge. Infinity cost = impossible. */
export function planProfile(ground, opts = {}) {
  const L = ground.length;
  // D-C534 §2.3 (roads): cut / fill caps and no bridges — a road is a cutting or an embankment of at most maxCut / maxFill
  // bridgeDrop: the fill beyond which a cell is a BRIDGE (a deck in the air; the kit's BRIDGE_DROP for streets, the cut
  // cap for the narrow roads — 0.0.14: hill sites hide ravines and cave mouths on the way to a bench)
  const drop = opts.bridgeDrop !== undefined ? opts.bridgeDrop : BRIDGE_DROP;
  const cellCost = (c, H) => {
    if (opts.maxCut !== undefined || opts.maxFill !== undefined || opts.noBridge) {
      if (!c) return 30;
      if (c.water && opts.noBridge) return Infinity;
      const d = H - c.g;
      if (opts.noBridge && d > drop) return Infinity;
      if (!c.water && opts.maxFill !== undefined && d > opts.maxFill && d <= drop) return Infinity;
      if (opts.maxCut !== undefined && -d > opts.maxCut) return Infinity;
    }
    return cellCostBase(c, H, drop);
  };
  const isBridgeCell = (c, H) => !opts.noBridge && isBridgeCellBase(c, H, drop);
  const rampOnBridge = !!opts.rampOnBridge;                 // roads: a deck may carry the 4-part ramp (a sloping viaduct)
  // the ramp's length in cells: the kit's ramp7 (1 in 7) for streets; his 4-part ramp (q1..q4 over 4 cells, 1 in 4) for the
  // narrow roads (D-C534 A4, 0.0.14: a 28 % hillside cannot be descended at 1 in 7 by axis-aligned legs within the cut).
  // The four quarter blocks are the FIRST 4 cells of an up ramp (base H, the surface rising to H + 1) and the LAST 4 of a
  // down ramp (base H - 1); the other cells of the segment are flat at the upper level.
  const R = opts.ramp || RAMP;
  const rampH = (dir, H, q) => dir > 0 ? (q < 4 ? H : H + 1) : (q < R - 4 ? H : H - 1);
  const with8 = !!opts.ramp8 && R === RAMP;
  const R8 = RAMP8;
  const rampH8 = (dir, H) => (dir > 0 ? H : H - 1);           // every cell of the 8-ramp is a quarter of the climb: base = the lower level
  const startDead = opts.startDead !== false, endDead = opts.endDead !== false;
  const known = ground.filter(Boolean).map((c) => c.g);
  if (!known.length) return { cost: Infinity, H: [], segs: [] };
  let lo = Math.min(...known) - 6, hi = Math.max(...known) + 6;
  if (opts.startH !== undefined) { lo = Math.min(lo, opts.startH); hi = Math.max(hi, opts.startH); }
  if (opts.endH !== undefined) { lo = Math.min(lo, opts.endH); hi = Math.max(hi, opts.endH); }
  for (const h of (opts.fixed ? opts.fixed.values() : [])) { lo = Math.min(lo, h); hi = Math.max(hi, h); }
  const NH = hi - lo + 1;
  const noRamp = new Uint8Array(L + Math.max(R, R8));
  for (const [a, b] of opts.flat || []) for (let t = Math.max(0, a); t <= Math.min(L - 1, b); t++) noRamp[t] = 1;
  const fixedAt = (t) => (opts.fixed ? opts.fixed.get(t) : undefined);
  const first = startDead ? DEAD : 0, last = endDead ? L - DEAD : L;     // the free stretch is [first, last)
  if (last < first) return { cost: Infinity, H: [], segs: [] };
  // state index: (t - first) * NH * 4 + h * 4 + a ; a: 0 = just after a ramp / start, 1, 2 = flat run, 3 = flat >= 3
  const S = (last - first + 1) * NH * 4;
  const cost = new Float64Array(S).fill(Infinity);
  const from = new Int32Array(S).fill(-1), how = new Int8Array(S);
  const idx = (t, h, a) => ((t - first) * NH + h) * 4 + a;
  // 0.0.22 (run 0.0.21: a side-street plan took 1.2 s, 214 times — 14 profiles of a 153-cell street per half): every
  // cell's cost and bridge flag at every height computed ONCE into tables (the ramps re-read 7 cells per state and the
  // dead ends 13); the ramp-blocked flag per t likewise. Results are identical (test_profile_speed.mjs).
  const CC = new Float64Array(L * NH), BR = new Uint8Array(L * NH);
  for (let t = 0; t < L; t++) for (let h = 0; h < NH; h++) { CC[t * NH + h] = cellCost(ground[t], lo + h); BR[t * NH + h] = isBridgeCell(ground[t], lo + h) ? 1 : 0; }
  const rampBlocked = new Uint8Array(L + 1), rampBlocked8 = new Uint8Array(L + 1);
  for (let t = 0; t < L; t++) { for (let q = t; q < t + R && q < L; q++) if (noRamp[q] || fixedAt(q) !== undefined) { rampBlocked[t] = 1; break; } }
  if (with8) for (let t = 0; t < L; t++) { for (let q = t; q < t + R8 && q < L; q++) if (noRamp[q] || fixedAt(q) !== undefined) { rampBlocked8[t] = 1; break; } }
  const deadCost = (a0, H) => { const h = H - lo; if (h < 0 || h >= NH) { let c = 0; for (let k = 0; k < DEAD; k++) { const cc = cellCost(ground[a0 + k], H); if (isBridgeCell(ground[a0 + k], H)) return Infinity; c += cc; } return c; }
    let c = 0; for (let k = 0; k < DEAD; k++) { const i = (a0 + k) * NH + h; if (BR[i]) return Infinity; c += CC[i]; } return c; };
  for (let h = 0; h < NH; h++) {
    const H = lo + h;
    if (opts.startH !== undefined && H !== opts.startH) continue;
    const c0 = startDead ? deadCost(0, H) : 0;
    if (c0 < Infinity) cost[idx(first, h, startDead ? 3 : 3)] = c0;
  }
  // the ramps' costs per (t, h): up (to h + 1) and down (to h - 1), Infinity where impossible (a bridge cell under a
  // street ramp, the edge of the height band, a no-ramp window) — computed once, read by both rest states
  const RUP = new Float64Array(L * NH).fill(Infinity), RDN = new Float64Array(L * NH).fill(Infinity);
  for (let t = first; t + R <= last; t++) {
    if (rampBlocked[t]) continue;
    for (let h = 0; h < NH; h++) {
      for (let di = 0; di < 2; di++) {
        const dir = di === 0 ? 1 : -1, h2 = h + dir;
        if (h2 < 0 || h2 >= NH) continue;
        let rc = with8 ? 5 + RAMP7_EXTRA : 5;                    // 1.3.228: with the 8-ramp on, the 7-cell ramp is the dearer choice
                                                                 // a price per ramp (review 19:1x: was 1.5 — hills came out as ramp after ramp with
                                                                 // 3-cell flats between, no frontage left; now the land is terraced first)
        for (let q = 0; q < R; q++) {
          const hq = (dir > 0 ? (q < 4 ? h : h2) : (q < R - 4 ? h : h2));
          const i = (t + q) * NH + hq;
          if (!rampOnBridge && BR[i]) { rc = Infinity; break; }
          rc += CC[i];
        }
        if (di === 0) RUP[t * NH + h] = rc; else RDN[t * NH + h] = rc;
      }
    }
  }
  // 1.3.228: the 8-ramp's costs (every cell at the lower level: the surface climbs across all 8)
  const RUP8 = new Float64Array(L * NH).fill(Infinity), RDN8 = new Float64Array(L * NH).fill(Infinity);
  if (with8) for (let t = first; t + R8 <= last; t++) {
    if (rampBlocked8[t]) continue;
    for (let h = 0; h < NH; h++) for (let di = 0; di < 2; di++) {
      const dir = di === 0 ? 1 : -1, h2 = h + dir;
      if (h2 < 0 || h2 >= NH) continue;
      const hq = dir > 0 ? h : h2;
      let rc = 5;
      for (let q = 0; q < R8; q++) { const i = (t + q) * NH + hq; if (!rampOnBridge && BR[i]) { rc = Infinity; break; } rc += CC[i]; }
      if (di === 0) RUP8[t * NH + h] = rc; else RDN8[t * NH + h] = rc;
    }
  }
  const FIX = new Float64Array(L + 1).fill(NaN);                 // the fixed height per t (NaN = free)
  if (opts.fixed) for (const [tt, hv] of opts.fixed) if (tt >= 0 && tt <= L) FIX[tt] = hv;
  const N4 = NH * 4;
  for (let t = first; t < last; t++) {
    const base = (t - first) * N4, fx = FIX[t], canRamp = t + R <= last, canRamp8 = with8 && t + R8 <= last;
    for (let h = 0; h < NH; h++) {
      const H = lo + h, cc = (fx !== fx || fx === H) ? CC[t * NH + h] : Infinity;
      const rup = canRamp ? RUP[t * NH + h] : Infinity, rdn = canRamp ? RDN[t * NH + h] : Infinity;
      const rup8 = canRamp8 ? RUP8[t * NH + h] : Infinity, rdn8 = canRamp8 ? RDN8[t * NH + h] : Infinity;
      for (let a = 0; a < 4; a++) {
        const k = base + h * 4 + a, c = cost[k];
        if (c === Infinity) continue;
        // a flat cell
        if (cc < Infinity) {
          const k2 = base + N4 + h * 4 + (a === 0 ? 1 : (a < 3 ? a + 1 : 3));
          if (c + cc < cost[k2]) { cost[k2] = c + cc; from[k2] = k; how[k2] = 0; }
        }
        // a ramp (only from rest: after a ramp or after >= 3 flat cells; never in a no-ramp window; not on a bridge)
        if (a === 0 || a === 3) {
          if (rup < Infinity) { const k2 = base + R * N4 + (h + 1) * 4; if (c + rup < cost[k2]) { cost[k2] = c + rup; from[k2] = k; how[k2] = 1; } }
          if (rdn < Infinity) { const k2 = base + R * N4 + (h - 1) * 4; if (c + rdn < cost[k2]) { cost[k2] = c + rdn; from[k2] = k; how[k2] = 2; } }
          if (rup8 < Infinity) { const k2 = base + R8 * N4 + (h + 1) * 4; if (c + rup8 < cost[k2]) { cost[k2] = c + rup8; from[k2] = k; how[k2] = 3; } }
          if (rdn8 < Infinity) { const k2 = base + R8 * N4 + (h - 1) * 4; if (c + rdn8 < cost[k2]) { cost[k2] = c + rdn8; from[k2] = k; how[k2] = 4; } }
        }
      }
    }
  }
  // the end
  let best = Infinity, bk = -1;
  for (let h = 0; h < NH; h++) for (let a = 0; a < 4; a++) {
    const H = lo + h;
    if (opts.endH !== undefined && H !== opts.endH) continue;
    if (a === 1 || a === 2) continue;                         // a flat strip shorter than 3 cells before the end: never
    const k = idx(last, h, a);
    if (cost[k] === Infinity) continue;
    const c = cost[k] + (endDead ? deadCost(last, H) : 0);
    if (c < best) { best = c; bk = k; }
  }
  if (bk < 0) return { cost: Infinity, H: [], segs: [] };
  // walk back
  const steps = [];
  for (let k = bk; from[k] >= 0; k = from[k]) {
    const t = Math.floor(k / (NH * 4)) + first, h = Math.floor(k / 4) % NH;
    steps.push({ t, h, how: how[k], k });
  }
  steps.reverse();
  const Hs = new Array(L).fill(undefined);
  const segs = [];
  const firstH = (() => { const k0 = steps.length ? from[steps[0].k] : bk; return lo + Math.floor(k0 / 4) % NH; })();
  if (startDead) { segs.push({ kind: "dead", a: 0, len: DEAD, H: firstH }); for (let q = 0; q < DEAD; q++) Hs[q] = firstH; }
  let prevH = firstH, t = first;
  for (const s of steps) {
    if (s.how === 0) {
      Hs[t] = prevH;
      const kind = isBridgeCell(ground[t], prevH) ? "bridge" : "flat";
      const top = segs[segs.length - 1];
      if (top && top.kind === kind && top.H === prevH && top.a + top.len === t) top.len++;
      else segs.push({ kind, a: t, len: 1, H: prevH });
      t++;
    } else if (s.how >= 3) {                                    // 1.3.228: an 8-ramp
      const dir = s.how === 3 ? 1 : -1;
      for (let q = 0; q < R8; q++) Hs[t + q] = rampH8(dir, prevH);
      segs.push({ kind: "ramp", a: t, len: R8, H: prevH, dir });
      prevH += dir;
      t += R8;
    } else {
      const dir = s.how === 1 ? 1 : -1;
      for (let q = 0; q < R; q++) Hs[t + q] = rampH(dir, prevH, q);
      segs.push({ kind: "ramp", a: t, len: R, H: prevH, dir });
      prevH += dir;
      t += R;
    }
  }
  if (endDead) { segs.push({ kind: "dead", a: last, len: DEAD, H: prevH }); for (let q = 0; q < DEAD; q++) Hs[last + q] = prevH; }
  return { cost: best, H: Hs, segs, lo, hi };
}

// ------------------------------------------------------------------------------------------------ pieces
/** the pieces of a planned street (world placements). width "v" | "t". Flat cells -> straight1 each (access pieces are
 *  laid later over three of them, centred on a house shaft); ramps -> ramp7; dead ends -> dead13; bridges -> deck jobs.
 *  Returns { pieces: [{name, x, y, z, rot, a, len}], bridges: [{a, len, H}] } with a / len in frame t (offset t0). */
export function piecesOf(f, plan, width = "v", t0 = 0) {
  const pre = width === "t" ? "t_" : "v_";
  const u = [f.ux, f.uz];
  const pieces = [], bridges = [];
  for (const s of plan.segs) {
    const ta = t0 + s.a;
    if (s.kind === "dead") {
      // the dead end's opening (native -z) faces the street: +u at the start, -u at the far end
      const facing = s.a === 0 ? u : [-u[0], -u[1]];
      const [x, z] = boxCorner(f, ta, DEAD);
      pieces.push({ name: `${pre}dead13`, x, y: s.H - 14, z, rot: rotFor([0, -1], facing), a: ta, len: DEAD, kind: "dead", end: s.a === 0 ? "start" : "end" });
    } else if (s.kind === "flat") {
      for (let q = 0; q < s.len; q++) {
        const [x, z] = boxCorner(f, ta + q, 1);
        pieces.push({ name: `${pre}straight1`, x, y: s.H - 14, z, rot: rotFor([1, 0], u), a: ta + q, len: 1, kind: "flat" });
      }
    } else if (s.kind === "ramp") {
      const len = s.len || RAMP;                                 // 1.3.228: ramp7 (7) or ramp8 (8)
      const [x, z] = boxCorner(f, ta, len);
      // up: native x0 (low) at the start, travel +u; down: the piece turned round, its high end at the start
      const up = s.dir > 0;
      pieces.push({ name: `${pre}ramp${len}`, x, y: (up ? s.H : s.H - 1) - 14, z, rot: rotFor([1, 0], up ? u : [-u[0], -u[1]]), a: ta, len, kind: "ramp", dir: s.dir });
    } else if (s.kind === "bridge") {
      bridges.push({ a: ta, len: s.len, H: s.H });
    }
  }
  return { pieces, bridges };
}

/** an access piece centred on frame t (replaces three straight1 cells) */
export function accessPiece(f, t, H, width = "v") {
  const [x, z] = boxCorner(f, t - 1, ACCESS);
  return { name: `${width === "t" ? "t_" : "v_"}access3`, x, y: H - 14, z, rot: rotFor([1, 0], [f.ux, f.uz]), a: t - 1, len: ACCESS, kind: "access" };
}

/** a tee on street f at t (13 cells from t), its branch toward `side` (+1 = +v, -1 = -v) */
export function teePiece(f, t, H, side, width = "v") {
  const [x, z] = boxCorner(f, t, JUNCTION);
  return { name: `${width === "t" ? "t_" : "v_"}tee13`, x, y: H - 14, z, rot: rotFor([1, 0], [side * f.vx, side * f.vz]), a: t, len: JUNCTION, kind: "tee", side };
}

/** every corridor cell -> sidewalk height (the street body for occupancy, walls, roads) */
export function corridorCells(f, plan, t0 = 0, out = new Map()) {
  plan.H.forEach((H, i) => {
    if (H === undefined) return;
    for (let w = 0; w < W; w++) { const [x, z] = cellOf(f, t0 + i, w); out.set(`${x},${z}`, H); }
  });
  return out;
}

/** the flat stretches a house may front: flat (not bridge, ramp, dead, junction) runs, as [a, b] inclusive + H */
export function flatStretches(plan, t0 = 0, reserved = []) {
  const out = [];
  for (const s of plan.segs) {
    if (s.kind !== "flat") continue;
    let a = t0 + s.a;
    const b = t0 + s.a + s.len - 1;
    // cut the reserved windows out
    const cuts = reserved.filter(([ra, rb]) => rb >= a && ra <= b).sort((p, q) => p[0] - q[0]);
    for (const [ra, rb] of cuts) { if (ra - 1 >= a) out.push({ a, b: ra - 1, H: s.H }); a = Math.max(a, rb + 1); }
    if (b >= a) out.push({ a, b, H: s.H });
  }
  return out;
}

/** a house's BRANCH to the sewer (1.3.225): the corridor cells carved at frame t on the house's side — w 0..3 (side -1)
 *  or 9..12 (side +1), between the house floor Hh - 11 and Hh - 8: the house's cellar gallery (its front wall, template
 *  y 3..6) meets the sewer hall (template z 4..8, y 3..6 under every straight / ramp cell, i.e. H(t) - 11 .. H(t) - 8;
 *  H(t) is Hh or Hh - 1, so at least 3 of the 4 rows overlap). Returns [[x, y, z], ...]. */
export function branchCells(f, t, side, Hh) {
  const out = [];
  for (let k = 0; k < 4; k++) {
    const w = side > 0 ? W - 1 - k : k;
    const [x, z] = cellOf(f, t, w);
    for (let y = Hh - 11; y <= Hh - 8; y++) out.push([x, y, z]);
  }
  return out;
}

/** 1.3.225 (his 20:01 "fix the city growth"; the frontage census: 26 % of a town's street sides were legal frontage and
 *  0 positions were free from village on): HOUSE FRONTAGE = runs of FLAT and RAMP cells (never a dead end, a bridge or a
 *  junction window), each cell with its sidewalk height (plan.H, a ramp's cells at its entry / upper level) and its kind
 *  ("f" flat, "r" ramp). A house may front a run whose cells rise at most FRONT_RISE; its floor stands at the highest. */
export const FRONT_RISE = 1;
export function frontStretches(plan, t0 = 0, reserved = []) {
  const L = plan.H.length;
  const kind = new Array(L).fill(null);
  for (const s of plan.segs) if (s.kind === "flat" || s.kind === "ramp") for (let q = s.a; q < s.a + s.len && q < L; q++) kind[q] = s.kind === "flat" ? "f" : "r";
  for (const [ra, rb] of reserved) for (let tt = ra; tt <= rb; tt++) { const i = tt - t0; if (i >= 0 && i < L) kind[i] = null; }
  const out = [];
  let i = 0;
  while (i < L) {
    if (!kind[i] || plan.H[i] === undefined) { i++; continue; }
    let j = i;
    while (j + 1 < L && kind[j + 1] && plan.H[j + 1] !== undefined) j++;
    out.push({ a: t0 + i, b: t0 + j, H: plan.H[i], Hs: plan.H.slice(i, j + 1), kinds: kind.slice(i, j + 1).join("") });
    i = j + 1;
  }
  return out;
}

// ------------------------------------------------------------------------------------------------ plots
/** a building's facts in its own file: sx (depth from the front), sz (frontage), shaft z (sewer ladder column) or null */
export function slotFor(f, stretch, side, def, shaftZ, at, Hover) {
  const fz = def.size[2], depth = def.size[0];             // frontage along the street, depth away from it
  // rotation: the house's front (local -x) faces the street: local +x points away from the corridor
  const away = side > 0 ? [f.vx, f.vz] : [-f.vx, -f.vz];
  const rot = rotFor([1, 0], away);
  const w0 = side > 0 ? W : -depth, w1 = side > 0 ? W + depth - 1 : -1;
  const [x0, z0, x1, z1] = boxCorner(f, at, fz, w0, w1);
  // the shaft's world cell -> its frame t (local (1, shaftZ) after the rotation, from the box corner)
  let shaftT = null;
  if (shaftZ !== null && shaftZ !== undefined) {
    const [sx, , sz] = def.size;
    const [ox, oz] = rotXZ(1, shaftZ, sx, sz, rot);
    shaftT = tw(f, x0 + ox, z0 + oz)[0];
  }
  // 1.3.230 (PL): the door's frame t (the table's door cell, else the middle of the frontage) — a plateau pad stands at the
  // street's height at the door or one step above it
  const [dsx, , dsz] = def.size;
  const door = def.door || [0, 0, Math.floor(dsz / 2)];
  const [dox, doz] = rotXZ(door[0] || 0, door[2], dsx, dsz, rot);
  const doorT = tw(f, x0 + dox, z0 + doz)[0];
  return { x: x0, z: z0, rot, box: [x0, x1, z0, z1], at, len: fz, side, shaftT, doorT, H: Hover !== undefined ? Hover : stretch.H };
}
/** saved-file (x, z) -> offset from the placement corner after rot clockwise quarter turns (same law as the clock) */
export function rotXZ(x, z, sx, sz, rot) {
  if (rot === 1) return [sz - 1 - z, x];
  if (rot === 2) return [sx - 1 - x, sz - 1 - z];
  if (rot === 3) return [z, sx - 1 - x];
  return [x, z];
}

/** find a place for one building along one street: both sides, packed outward from `mid`; a house needs its whole
 *  frontage on one flat stretch and its access piece (shaft t - 1 .. t + 1) on that stretch too, sharing no cell with
 *  another access piece unless it is the same piece (two houses facing each other share one). free(box) is the world's
 *  veto (other plots, squares, corridors). takenAccess: Set of access-centre t already laid on this street. */
export function placeAlong(f, stretches, def, shaftZ, mid, free, takenAccess, sidePref = 1, gap = 1, noShaft = [], opts = null) {
  // stretches: one list for both sides, or { "1": [...], "-1": [...] } per side (review 19:1x: a junction window keeps
  // only ITS side free; the other side may hold houses, as long as no access piece lands in the window — noShaft).
  // 1.3.230 (PL) opts = { riseMax, doorStep }: a frontage rising more than FRONT_RISE (up to riseMax) is offered as a
  // PLATEAU slot (slot.plateau = { rise, step }) when its door stands within doorStep of the floor (the highest sidewalk)
  // and its sewer link (hatch or branch) within one block of it (>= 3 shared rows); slot.Hring = the street heights at
  // t = at - 1 .. at + fz (the pad's ring). Without opts nothing changes.
  const fz = def.size[2];
  const riseMax = opts && opts.riseMax > FRONT_RISE ? opts.riseMax : FRONT_RISE;
  const doorStep = opts && opts.doorStep !== undefined ? opts.doorStep : 1;
  const perSide = !Array.isArray(stretches);
  const candsFor = (side) => {
    const list = perSide ? (stretches[String(side)] || []) : stretches;
    const cands = [];
    for (const st of list) for (let at = st.a; at + fz - 1 <= st.b; at++) cands.push([Math.abs(at + fz / 2 - mid), at, st]);
    cands.sort((p, q) => p[0] - q[0] || p[1] - q[1]);
    return cands;
  };
  for (const side of [sidePref, -sidePref]) {
    for (const [, at, st] of candsFor(side)) {
      let Hfront, rise = 0;
      if (st.Hs) {                                                        // 1.3.225: a frontage run (flat + ramp cells)
        let lo = Infinity, hi = -Infinity;
        for (let q = at - st.a; q < at - st.a + fz; q++) { const h = st.Hs[q]; if (h < lo) lo = h; if (h > hi) hi = h; }
        rise = hi - lo;
        if (rise > riseMax) continue;
        Hfront = hi;
      }
      const slot = slotFor(f, st, side, def, shaftZ, at, Hfront);
      if (rise > FRONT_RISE) {                                            // 1.3.230 (PL): a plateau frontage
        const qd = slot.doorT - st.a;
        if (!(qd >= 0 && qd < st.Hs.length) || Hfront - st.Hs[qd] > doorStep) continue;
        slot.plateau = { rise, step: Hfront - st.Hs[qd] };
      }
      if (opts && st.Hs) slot.Hring = Array.from({ length: fz + 2 }, (_, i) => { const q = at - 1 + i - st.a; return q >= 0 && q < st.Hs.length ? st.Hs[q] : undefined; });
      if (slot.shaftT !== null) {
        // the shaft's own access piece needs 3 FLAT cells at one height, outside every junction window, clear of other pieces
        let ok = slot.shaftT - 1 >= st.a && slot.shaftT + 1 <= st.b;
        if (ok && st.Hs) { const q = slot.shaftT - st.a; ok = st.kinds.slice(q - 1, q + 2) === "fff" && st.Hs[q - 1] === st.Hs[q] && st.Hs[q + 1] === st.Hs[q]; }
        if (ok && noShaft.some(([na, nb]) => slot.shaftT + 1 >= na && slot.shaftT - 1 <= nb)) ok = false;
        if (ok) for (const c of takenAccess) if (c !== slot.shaftT && Math.abs(c - slot.shaftT) < ACCESS) { ok = false; break; }
        if (!ok) {
          if (!st.Hs) continue;                                           // the old frontage keeps the old law
          // 1.3.225 (his 20:36: "as long as ALL of them have access to the homes from the sewers underground"): no hatch of
          // its own here — the house's cellar gallery is joined to the sewer hall under the street by a BRANCH (4 cells
          // carved through the corridor's side wall at the shaft's t), never left without the sewer
          slot.branchT = slot.shaftT; slot.shaftT = null; slot.cesspit = true;
        }
      }
      if (slot.plateau) {                                                 // 1.3.230 (PL): the sewer link within one block of the floor
        const ts = slot.shaftT !== null ? slot.shaftT : slot.branchT;
        if (ts !== null && ts !== undefined) { const qs = ts - st.a; if (!(qs >= 0 && qs < st.Hs.length) || Hfront - st.Hs[qs] > 1) continue; }
      }
      const [x0, x1, z0, z1] = slot.box;
      if (!free([x0 - gap, x1 + gap, z0 - gap, z1 + gap], [x0, x1, z0, z1], slot, f)) continue;
      return slot;
    }
  }
  return null;
}

// ------------------------------------------------------------------------------------------------ the sewer outfall
/** his 18:13: the sewer goes on past the street's dead end and turns toward the nearest face or open air, where it
 *  exits (a space for his metal grate / door). The dead end covers frame t in [a, a + 12]; its hall (w4..8, 10 cells from
 *  the open side) has the trench (w6, y1-2) along it and a CROSS drain (y1-2) across it at the piece's middle; the far wall
 *  (3 thick) and the side walls close it. From the piece centre the tunnel leaves through one of those walls, goes
 *  straight or makes ONE turn, and surfaces at the first cell outside the piece whose ground lies below the tunnel floor
 *  + 1 (a face, a valley), or whose WATER SURFACE lies below the tunnel floor (review 19:1x: an exit into water standing
 *  above the floor would flood the sewer and every cellar joined to it). D-C533 (his 19:48): the tunnel carries the
 *  sewer's water on: its centre line at floor level is a water channel between two 1-wide ledges, and the exit spills.
 *  Level tunnel, floor y = piece origin + 1 (the trench's water level). blocked(x, z) vetoes cells the tunnel (centre +- 2,
 *  its lining) may not pass: plots, other corridors, other tunnels. site.top(x, z) (optional) = the topmost block's y (the
 *  water surface where site.at gives the bed). Returns { cells: [[x, z], ...] centre line from the piece centre to the
 *  exit (inclusive), exit: [x, z], dir: [dx, dz] (last step), floorY } or null when no daylight lies within maxLen. */
export function planOutfall(site, f, a, end, H, maxLen = 72, blocked = () => false) {
  const u = [f.ux, f.uz], v = [f.vx, f.vz];
  const floorY = H - 14 + 1;
  const centre = cellOf(f, a + 6, 6);
  const inPiece = (x, z) => { const [t, w] = tw(f, x, z); return t >= a && t <= a + 12 && w >= 0 && w <= 12; };
  const daylight = (x, z) => {
    const g = site.at(x, z);
    if (g === undefined) return null;
    if (site.isWater(x, z)) { const top = site.top ? site.top(x, z) : g; return top !== undefined && top < floorY ? true : "wet"; }
    return g < floorY;                                       // strictly below the channel: the spill needs an air cell at floor level
  };
  // a step is allowed when its centre and lining band (+-2 across the travel) stay off vetoed cells (inside our own
  // dead end only the air is carved, so the piece itself never vetoes)
  const passable = (x, z, d) => {
    for (let k = -2; k <= 2; k++) { const cx = x - d[1] * k, cz = z + d[0] * k; if (!inPiece(cx, cz) && blocked(cx, cz)) return false; }
    return true;
  };
  const away = end === "start" ? [-u[0], -u[1]] : u;
  const dirs = [away, v, [-v[0], -v[1]]];
  let best = null;
  const walk = (start, d, budget, cells) => {
    let [x, z] = start;
    for (let n = 0; n < budget; n++) {
      x += d[0]; z += d[1];
      if (!passable(x, z, d)) return false;
      cells.push([x, z]);
      if (inPiece(x, z)) continue;
      const day = daylight(x, z);
      if (day === null || day === "wet") return false;          // unknown land, or water standing above the floor
      if (day) return true;
    }
    return false;
  };
  for (const d of dirs) {
    // straight
    const c1 = [centre.slice()];
    if (walk(centre, d, maxLen, c1) && (!best || c1.length < best.cells.length)) best = { cells: c1, exit: c1[c1.length - 1], dir: d, floorY };
    // one turn after leaving the piece by k cells
    for (const k of [3, 6, 10, 14, 20, 28, 36]) {
      const c2 = [centre.slice()];
      let [x, z] = centre, left = false, steps = 0, bad = false;
      while (steps < 40) { x += d[0]; z += d[1]; if (!passable(x, z, d)) { bad = true; break; } c2.push([x, z]); steps++; if (!inPiece(x, z)) { left = true; break; } }
      if (!left || bad) continue;
      let dead = false;
      for (let q = 1; q < k; q++) {
        x += d[0]; z += d[1];
        if (!passable(x, z, d)) { dead = true; break; }
        c2.push([x, z]);
        const day = daylight(x, z);
        if (day !== false) { dead = true; break; }              // daylight (the straight case covers it), water or unknown
      }
      if (dead) continue;
      for (const sg of [1, -1]) {
        const d2 = [-d[1] * sg, d[0] * sg];
        const c3 = c2.slice();
        if (walk([x, z], d2, maxLen - c3.length, c3) && (!best || c3.length < best.cells.length)) best = { cells: c3, exit: c3[c3.length - 1], dir: d2, floorY };
      }
    }
  }
  return best;
}

// ------------------------------------------------------------------------------------------------ A0.2 SEWER EXITS v2 (D-C547 / D-C549)
// His 23:55: "sewers within our roads need logic to find their appropriate exit points"; his 00:03: a sewer may run on
// UNDERGROUND where nothing lies above it, if the natural flow of its water needs an exit there — it has to drain somewhere.
// The sewer of a settlement is a NETWORK (streets whose corridors touch share it: tees, crossroads, connectors; a bridge
// has no substructure and splits it; a bench is its own network; the climbing legs carry none). Water collects at the
// network's LOW POINTS (every local minimum plateau of the trench floor) and leaves only through an exit of that low
// point: one TRUNK per low point, to open water (best), a lower hillside face, or a soakaway pit — every other dead end
// stays sealed. The trunk's floor falls 1 per TRUNK_FALL cells, so a water source at the top of each level stretch
// spreads along it and over the next step: the water really runs to the mouth.
export const TRUNK_FALL = 7;                      // the floor falls one block per 7 cells (water spreads 7 cells from a source)
export const TRUNK_WATER = 120, TRUNK_FACE = 72;  // the farthest a trunk runs to open water / to a hillside face
export const SOAK_DEPTH = 8;                      // a soakaway pit: 8 below the trench, gravel in its lower half

/** the drainage networks of kit streets [{ id, f, tmin, H, segs, role }]. Floor of a corridor cell = sidewalk H - 13 (the
 *  trench's water level). Returns [{ ids: [street ids], cells, lo, hi, minima: [{ floor, n, dead: [{ sid, a, end }],
 *  side: [{ sid, ts: [t...] }] }] }]: every LOCAL minimum plateau (connected cells of one floor whose neighbours in the
 *  network all lie higher) — water there cannot leave except through an exit of its own. dead = the dead ends inside the
 *  plateau (an exit leaves through their far or side walls); side = the plateau's centre-line cells per street, nearest
 *  its middle first (an exit leaves sideways when the low point has no dead end: a valley in a street). */
export function drainNetworks(streets) {
  const cell = new Map();                                         // "x,z" -> [floor, sid, t]
  for (const s of streets) {
    const bridgeT = new Set();
    for (const q of s.segs || []) if (q.kind === "bridge") for (let k = 0; k < q.len; k++) bridgeT.add(s.tmin + q.a + k);
    s.H.forEach((H, i) => {
      if (H === undefined) return;
      const t = s.tmin + i;
      if (bridgeT.has(t)) return;                                 // a bridge carries no sewer
      for (let w = 0; w < W; w++) {
        const [x, z] = cellOf(s.f, t, w);
        const k = `${x},${z}`, got = cell.get(k);
        if (!got || H - 13 < got[0]) cell.set(k, [H - 13, s.id, t]);
      }
    });
  }
  const N4 = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  const nb = (k) => { const c = k.indexOf(","); const x = +k.slice(0, c), z = +k.slice(c + 1); return N4.map(([dx, dz]) => `${x + dx},${z + dz}`); };
  // the networks: union of streets whose cells touch
  const par = new Map(streets.map((s) => [s.id, s.id]));
  const find = (a) => { while (par.get(a) !== a) { par.set(a, par.get(par.get(a))); a = par.get(a); } return a; };
  for (const [k, v] of cell) for (const n of nb(k)) { const o = cell.get(n); if (o && o[1] !== v[1]) { const a = find(v[1]), b = find(o[1]); if (a !== b) par.set(a, b); } }
  // the plateaus (4-connected cells of one floor) and the local minima among them
  const seen = new Set();
  const nets = new Map();
  for (const [k0, v0] of cell) {
    if (seen.has(k0)) continue;
    const floor = v0[0];
    const q = [k0];
    seen.add(k0);
    let lower = false;
    const members = [];
    for (let qi = 0; qi < q.length; qi++) {
      const k = q[qi];
      members.push(k);
      for (const n of nb(k)) {
        const o = cell.get(n);
        if (!o) continue;
        if (o[0] < floor) { lower = true; continue; }
        if (o[0] === floor && !seen.has(n)) { seen.add(n); q.push(n); }
      }
    }
    const root = find(v0[1]);
    if (!nets.has(root)) nets.set(root, { ids: [], cells: 0, lo: Infinity, hi: -Infinity, minima: [] });
    const net = nets.get(root);
    net.cells += members.length;
    net.lo = Math.min(net.lo, floor); net.hi = Math.max(net.hi, floor);
    if (lower) continue;
    // a minimum: its dead ends and its centre-line cells by street
    const m = { floor, n: members.length, dead: [], side: [] };
    const set = new Set(members);
    for (const s of streets) {
      if (find(s.id) !== root) continue;
      for (const q2 of s.segs || []) {
        if (q2.kind !== "dead") continue;
        const ta = s.tmin + q2.a;
        const [cx, cz] = cellOf(s.f, ta + 6, 6);
        if (set.has(`${cx},${cz}`)) m.dead.push({ sid: s.id, a: ta, end: q2.a === 0 ? "start" : "end" });
      }
      const ts = [];
      s.H.forEach((H, i) => { const [x, z] = cellOf(s.f, s.tmin + i, 6); if (set.has(`${x},${z}`) && cell.get(`${x},${z}`)[1] === s.id) ts.push(s.tmin + i); });
      if (ts.length) {
        const mid = ts[ts.length >> 1];
        ts.sort((p, r) => Math.abs(p - mid) - Math.abs(r - mid) || p - r);
        m.side.push({ sid: s.id, ts });
      }
    }
    net.minima.push(m);
  }
  for (const s of streets) { const net = nets.get(find(s.id)); if (net) net.ids.push(s.id); }
  const out = [...nets.values()];
  for (const n of out) n.minima.sort((p, r) => p.floor - r.floor);
  return out;
}

/** A0.2: the TRUNK from a sewer low point to its exit. o = { start: [x, z] (the trench cell the water leaves from), dirs:
 *  [[dx, dz], ...] (the ways out, best first), own(x, z) (cells of our own piece / corridor: no veto, no daylight test),
 *  floorY (the trench's water level), blocked(x, z) (plots, corridors, other tunnels), fall, maxWater, maxFace }.
 *  The trunk leaves own along one of dirs, runs straight or makes ONE turn, and ends at the FIRST cell outside own where
 *  it meets daylight at the trench's level: open WATER whose surface lies below floorY (a river, a lake, the sea; within
 *  maxWater cells) or ground lower than floorY (a hillside face; within maxFace cells). Water standing AT or ABOVE the
 *  floor stops that line (an exit there would flood the sewer and every cellar joined to it). Ranking (D-C547): water >
 *  face, then the shortest. THEN the floor falls toward the mouth (trunkFloors): one block per `fall` cells or slower,
 *  never below one above the water surface / the ground at the mouth (the spill falls out, the trunk never dives under
 *  its own outlet; 0.0.22 test 6: a trunk falling 1 per 7 over 70 cells sank below the river it was looking for).
 *  Returns { cells, floors, sources, exit, dir, floorY, target: "water" | "face", outlet } or null. */
export function planOutfall2(site, o) {
  const fall = o.fall || TRUNK_FALL, maxW = o.maxWater || TRUNK_WATER, maxF = o.maxFace || TRUNK_FACE;
  const blocked = o.blocked || (() => false);
  const own = o.own, fy = o.floorY;
  // daylight at the trench level: "water" (+ its surface) | "face" (+ the ground) | false (underground) | null (unknown) | "wet"
  const daylight = (x, z) => {
    const g = site.at(x, z);
    if (g === undefined) return null;
    if (site.isWater(x, z)) { const top = site.top ? site.top(x, z) : g; return top !== undefined && top < fy ? ["water", top] : "wet"; }
    return g < fy ? ["face", g] : false;
  };
  const passable = (x, z, d) => {
    for (let k = -2; k <= 2; k++) { const cx = x - d[1] * k, cz = z + d[0] * k; if (!own(cx, cz) && blocked(cx, cz)) return false; }
    return true;
  };
  let best = null;
  const better = (c) => !best || (c.target === "water") > (best.target === "water") || ((c.target === "water") === (best.target === "water") && c.cells.length < best.cells.length);
  const walk = (p, d, state, budget) => {
    let [x, z] = p;
    for (let n = 0; n < budget; n++) {
      x += d[0]; z += d[1];
      if (!passable(x, z, d)) return false;
      state.cells.push([x, z]);
      if (own(x, z)) continue;
      state.out++;
      const day = daylight(x, z);
      if (day === null || day === "wet") return false;
      if (day) { if (day[0] === "face" && state.out > maxF) return false; return day; }
      if (state.out >= maxW) return false;
    }
    return false;
  };
  const offer = (state, d, day) => { const c = { cells: state.cells, exit: state.cells[state.cells.length - 1], dir: d, floorY: fy, target: day[0], outlet: day[1] }; if (better(c)) best = c; };
  for (const d of o.dirs) {
    const s1 = { cells: [o.start.slice()], out: 0 };
    const t1 = walk(o.start, d, s1, maxW + 40);
    if (t1) offer(s1, d, t1);
    for (const k of [3, 6, 10, 14, 20, 28, 36, 48, 64]) {                // one turn after k cells outside own
      const s2 = { cells: [o.start.slice()], out: 0 };
      let [x, z] = o.start, bad = false;
      for (let n = 0; n < 60 && s2.out < k; n++) {
        x += d[0]; z += d[1];
        if (!passable(x, z, d)) { bad = true; break; }
        s2.cells.push([x, z]);
        if (own(x, z)) continue;
        s2.out++;
        if (daylight(x, z) !== false) { bad = true; break; }             // daylight already (the straight case has it), water, unknown
      }
      if (bad || s2.out < k) continue;
      for (const sg of [1, -1]) {
        const d2 = [-d[1] * sg, d[0] * sg];
        const s3 = { cells: s2.cells.slice(), out: s2.out };
        const t3 = walk([x, z], d2, s3, maxW - s3.out);
        if (t3) offer(s3, d2, t3);
      }
    }
  }
  if (best) trunkFloors(best, own, fall);
  return best;
}
/** the trunk's floor per cell and its water sources: inside own the trench level; outside, `steps` one-block steps spread
 *  evenly (never closer than `fall` cells), steps = min(the drop to one above the outlet, cells outside / fall); a source
 *  at the first cell of every level stretch and every `fall` cells within a longer one (flowing water spreads 7 cells from
 *  a source on Bedrock: the channel is wet end to end, and it RUNS where it steps down). */
export function trunkFloors(plan, own, fall = TRUNK_FALL) {
  const outIdx = [];
  plan.cells.forEach(([x, z], i) => { if (i > 0 && !own(x, z)) outIdx.push(i); });
  const nOut = outIdx.length;
  const drop = plan.outlet !== undefined ? Math.max(0, plan.floorY - (plan.outlet + 1)) : 0;
  const steps = nOut ? Math.min(drop, Math.floor(nOut / fall)) : 0;
  const seg = steps ? Math.max(fall, Math.ceil(nOut / (steps + 1))) : Math.max(fall, nOut);
  plan.floors = plan.cells.map(() => plan.floorY);
  plan.sources = [];
  outIdx.forEach((i, j) => {
    const s = Math.min(steps, Math.floor(j / seg));
    plan.floors[i] = plan.floorY - s;
    const inSeg = j - s * seg;
    if (inSeg % fall === 0 && i < plan.cells.length - 1) plan.sources.push(i);
  });
  plan.steps = steps;
  return plan;
}
/** the fallback (D-C547 (3c), the medieval cesspit): a SOAKAWAY pit under the trench at the low point */
export function soakawayAt(start, floorY) { return { cells: [start.slice()], floors: [floorY], sources: [], exit: start.slice(), dir: [0, 0], floorY, target: "soakaway", steps: 0 }; }


// ------------------------------------------------------------------------------------------------ narrow roads (D-C534 §2.3, his C5)
/** D-C534 §2.3: a NARROW ROAD (ROAD_W wide, no sidewalks, no sewer, no buildings) from P0 leaving in direction d0 to P1
 *  arriving in direction d1 (both unit axis vectors), as axis-aligned LEGS joined by flat elbows (a square of ROAD_W),
 *  rising by his 4-part ramps (1 in 4, ROAD_RAMP), cut or filled by at most ROAD_CUT. The shapes tried: straight, L, Z, U (a hairpin),
 *  and 4- or 5-leg switchbacks, legs of 7..70 cells; each shape's centre line is checked for vetoes and a cheap vertical
 *  feasibility, the best few are profiled exactly by planProfile (flat at both ends and at every elbow).
 *  ground(x, z) -> { g, water } | undefined (the planners' site), blocked(x, z) -> true where the road may not pass.
 *  Returns a GENERATOR (one candidate per yield) whose final value is { cells: [[x, z], ...], H: [...], segs, dirs: [[dx, dz]],
 *  turns: [index...], cost, legs } or null. */
export const ROAD_W = 7, ROAD_CUT = 4, ROAD_HALF = 3;        // fill beyond ROAD_CUT -> a deck (viaduct)
export const ROAD_CUT_MAX = 6;                                // a cutting of at most this (two stepped faces), like a street's
export const ROAD_RAMP = 4;                                   // his 4-part ramp: one block per 4 cells (1 in 4) on the narrow roads
export const ROAD_BRIDGE_MAX = 24;                            // a road bridge (deck over a ravine, a cave mouth or water) spans at most this
const LEG_LENS = [7, 14, 21, 28, 35, 42, 56, 70, 84, 98];
const MAX_LEG = 100;                                          // no leg longer than this (no giant loops as closures)
export function roadShapes(P0, d0, P1, d1) {
  const u = d0, v = [-d0[1], d0[0]];
  const dx = P1[0] - P0[0], dz = P1[1] - P0[1];
  const a = dx * u[0] + dz * u[1], b = dx * v[0] + dz * v[1];
  const d1u = d1[0] * u[0] + d1[1] * u[1], d1v = d1[0] * v[0] + d1[1] * v[1];      // +-1 / 0
  const out = [];
  const push = (legs) => { if (legs.every((l) => l.len >= 7 && l.len <= MAX_LEG)) out.push(legs); };
  // 1 leg
  if (b === 0 && d1u === 1 && a >= 7) push([{ d: u, len: a }]);
  // 2 legs: u then v
  if (b !== 0 && d1v === Math.sign(b) && a >= 7 && Math.abs(b) >= 7) push([{ d: u, len: a }, { d: [v[0] * Math.sign(b), v[1] * Math.sign(b)], len: Math.abs(b) }]);
  // 3 legs: u, v, +-u
  if (b !== 0 && d1u !== 0) {
    const sv = Math.sign(b), vv = [v[0] * sv, v[1] * sv];
    for (const L1 of LEG_LENS) {
      const L3 = d1u > 0 ? a - L1 : L1 - a;
      if (L3 < 7) continue;
      push([{ d: u, len: L1 }, { d: vv, len: Math.abs(b) }, { d: d1u > 0 ? u : [-u[0], -u[1]], len: L3 }]);
    }
  }
  // 4 legs: u, v, u', v'  (arrives along +-v)
  if (d1v !== 0) {
    for (const L1 of LEG_LENS) for (const s3 of [1, -1]) {
      const L3 = s3 > 0 ? a - L1 : L1 - a;
      if (L3 < 7) continue;
      for (const L2 of LEG_LENS) for (const s2 of [1, -1]) {
        const L4 = (b - s2 * L2) / d1v;
        if (L4 < 7) continue;
        push([{ d: u, len: L1 }, { d: [v[0] * s2, v[1] * s2], len: L2 }, { d: [u[0] * s3, u[1] * s3], len: L3 }, { d: [v[0] * d1v, v[1] * d1v], len: L4 }]);
      }
    }
  }
  // 5 legs: u, v, u', v', u'' (arrives along +-u) — the switchback proper when the middle leg runs back
  if (d1u !== 0) {
    for (const L1 of LEG_LENS) for (const s3 of [1, -1]) for (const L3 of LEG_LENS) {
      const L5 = (a - L1 - s3 * L3) / d1u;
      if (L5 < 7) continue;
      for (const L2 of LEG_LENS) for (const s2 of [1, -1]) for (const s4 of [1, -1]) {
        const L4 = (b - s2 * L2) / s4;
        if (L4 < 7) continue;
        push([{ d: u, len: L1 }, { d: [v[0] * s2, v[1] * s2], len: L2 }, { d: [u[0] * s3, u[1] * s3], len: L3 }, { d: [v[0] * s4, v[1] * s4], len: L4 }, { d: [u[0] * d1u, u[1] * d1u], len: L5 }]);
      }
    }
  }
  // fewest legs, then shortest
  out.sort((p, q) => p.length - q.length || p.reduce((s, l) => s + l.len, 0) - q.reduce((s, l) => s + l.len, 0));
  return out;
}
/** the SWITCHBACK STACK family (R1 §4.6): from P0 a first leg along d0, then k pairs of [a leg ACROSS the slope (toward
 *  P1's across coordinate), a leg ALONG it (alternating direction)], the across legs sharing the across distance to P1
 *  exactly, the last along leg running on to P1's along coordinate (d1 along) or stopping for a final across leg (d1
 *  across). Every leg >= 7. */
export function switchbackShapes(P0, d0, P1, d1) {
  const out = [];
  const u = d0, v = [-d0[1], d0[0]];
  const dx = P1[0] - P0[0], dz = P1[1] - P0[1];
  const A = dx * u[0] + dz * u[1], B = dx * v[0] + dz * v[1];          // along / across distances to P1
  if (Math.abs(B) < 14) return out;
  const sv = Math.sign(B), vd = [v[0] * sv, v[1] * sv];
  const d1u = d1[0] * u[0] + d1[1] * u[1], d1v = d1[0] * v[0] + d1[1] * v[1];
  for (let k = 2; k <= 10; k++) {
    const across = Math.abs(B) - (d1v !== 0 ? 0 : 0);
    for (const finalAcross of (d1v === sv ? [7, 14, 21] : [0])) {
      const share = across - finalAcross;
      if (share < 7 * k || share / k > 35) continue;
      const base = Math.floor(share / k), extra = share - base * k;              // p_i = base (+1 for the first `extra`)
      for (const q0 of [14, 21, 28, 42, 56]) for (const q of [14, 21, 28, 42, 56]) {
        const legs = [{ d: u, len: q0 }];
        let along = q0, su = -1;
        for (let i = 0; i < k; i++) {
          const p = base + (i < extra ? 1 : 0);
          legs.push({ d: vd, len: p });
          if (i < k - 1) { legs.push({ d: [u[0] * su, u[1] * su], len: q }); along += su * q; su = -su; }
        }
        // after the last across leg we head `su` along u; the last along leg must reach A exactly (d1 along) or stop
        // short for the final across leg (d1 across): its length = (A - along) * su
        const rest = (A - along) * su;
        if (d1v === 0) {                                                         // arrive along u: d1 must equal su * u
          if (d1u !== su || rest < 7) continue;
          legs.push({ d: [u[0] * su, u[1] * su], len: rest });
        } else {
          if (rest < 7) continue;
          legs.push({ d: [u[0] * su, u[1] * su], len: rest });
          legs.push({ d: vd, len: finalAcross });
        }
        if (legs.every((l) => l.len >= 7 && l.len <= MAX_LEG)) out.push(legs);
      }
    }
  }
  return out;
}
/** the HAIRPIN family (R1 §4.6; kitvillage-0.0.13: a bench 108 ahead and 30 below got no road — every shape zigzagged
 *  ALONG the fall line): long legs ACROSS the fall line that REVERSE direction (the true switchback), joined by short STEP
 *  legs along it. Family U: the fall line along u (P1 mostly ahead): steps +u, long legs +-v, their signed sum = B.
 *  Family V: the fall line along v (P1 mostly beside): steps along v toward P1, long legs +-u, their signed sum = A.
 *  Arrival along u ends with a step; arrival along v ends with the last long leg (family U) / a step (family V). */
export function hairpinShapes(P0, d0, P1, d1) {
  const out = [];
  const u = d0, v = [-d0[1], d0[0]];
  const dx = P1[0] - P0[0], dz = P1[1] - P0[1];
  const A = dx * u[0] + dz * u[1], B = dx * v[0] + dz * v[1];
  const d1u = d1[0] * u[0] + d1[1] * u[1], d1v = d1[0] * v[0] + d1[1] * v[1];
  const KS = [2, 3, 4, 5, 6], WS = [28, 42, 56, 70, 84, 100], QS = [7, 14, 21], Q0S = [7, 14, 28];
  const ok = (legs) => legs.every((l) => l.len >= 7 && l.len <= MAX_LEG);
  // family U
  if (A >= 21) {
    for (const k of KS) for (const w of WS) for (const q of QS) for (const q0 of Q0S) for (const s0 of [1, -1]) {
      if (d1v !== 0 && k >= 2 && s0 * (k % 2 ? 1 : -1) !== d1v) continue;          // the last long leg must run toward d1
      const qEnd = A - q0 - (k - 1) * q;
      if (d1u === 1 && qEnd < 7) continue;
      if (d1v !== 0 && (A - q0 - (k - 2) * q) < 7) continue;
      const legs = [{ d: u, len: q0 }];
      let net = 0, s = s0, bad = false;
      for (let i = 0; i < k; i++) {
        let wi = w;
        if (i === k - 1) { wi = (B - net) * s; if (wi < 7 || wi > MAX_LEG) { bad = true; break; } }
        legs.push({ d: [v[0] * s, v[1] * s], len: wi }); net += s * wi;
        if (i < k - 1) legs.push({ d: u, len: (d1v !== 0 && i === k - 2) ? A - q0 - (k - 2) * q : q });
        s = -s;
      }
      if (bad) continue;
      if (d1u === 1) legs.push({ d: u, len: qEnd });
      else if (d1v === 0) continue;                                                // arriving along -u: not a hairpin's end
      if (ok(legs)) out.push(legs);
    }
  }
  // family V
  if (Math.abs(B) >= 21) {
    const sv = Math.sign(B), vd = [v[0] * sv, v[1] * sv];
    for (const k of KS) for (const w of WS) for (const q of QS) for (const q0 of Q0S) {
      // long legs along u: the first one is the departure itself (+u), then alternating; signed sum = A
      const stepsN = d1v === sv ? k : k - 1;                                        // arrival along v: a final step; along u: none
      const across = Math.abs(B) - (d1v === sv ? 0 : 0);
      const qEnd = across - (stepsN - 1) * q;
      if (stepsN >= 1 && qEnd < 7) continue;
      if (d1v === sv && stepsN < 1) continue;
      const legs = [];
      let net = 0, s = 1, bad = false;
      for (let i = 0; i < k; i++) {
        let wi = i === 0 ? Math.max(q0, 7) : w;
        if (i === k - 1) { wi = (A - net) * s; if (wi < 7 || wi > MAX_LEG) { bad = true; break; } if (d1v === 0 && d1u !== s) { bad = true; break; } }
        legs.push({ d: [u[0] * s, u[1] * s], len: wi }); net += s * wi;
        if (i < k - 1) legs.push({ d: vd, len: (i === k - 2 && d1v !== sv) ? qEnd : q });
        s = -s;
      }
      if (bad) continue;
      if (d1v === sv) legs.push({ d: vd, len: qEnd });
      if (legs.length > 1 && ok(legs)) out.push(legs);
    }
  }
  return out;
}
/** the centre-line cells of a leg list from P0 (P0 is cell 0), with the travel direction per cell and the turn indices */
export function roadCells(P0, legs) {
  const cells = [P0.slice()], dirs = [legs[0].d], turns = [];
  let [x, z] = P0;
  legs.forEach((l, i) => {
    if (i > 0) turns.push(cells.length - 1);
    for (let k = 0; k < l.len; k++) { x += l.d[0]; z += l.d[1]; cells.push([x, z]); dirs.push(l.d); }
  });
  return { cells, dirs, turns };
}
/** the SHAPE pass: straight / L / Z / U / switchback / hairpin leg lists checked cheaply (length, ramp room, vetoes, no
 *  self-overlap, a vertical band, a greedy profile), the best few profiled exactly. Fast and good on open hillsides; the
 *  terrain search below takes over where ravines, humps and vetoes defeat fixed shapes. */
export function* planRoadShapesJob(ground, blocked, P0, d0, P1, d1, H0, H1, maxDP = 6, stats = null) {
  const shapes = roadShapes(P0, d0, P1, d1).concat(switchbackShapes(P0, d0, P1, d1), hairpinShapes(P0, d0, P1, d1));
  const cands = [];
  const climb = Math.abs(H1 - H0);
  let examined = 0;
  const S = stats || {};
  S.shapes = shapes.length; S.long = 0; S.room = 0; S.veto = 0; S.overlap = 0; S.unknown = 0; S.band = 0; S.greedy = 0; S.sdp = 0; S.sdpFail = 0;
  for (const legs of shapes) {
    examined++;
    if (examined % 4 === 0) yield;
    let L = 1, turnsN = legs.length - 1;
    for (const l of legs) L += l.len;
    if (L > 600) { S.long++; continue; }
    if (ROAD_RAMP * climb > L - 14 - 7 * turnsN) { S.room++; continue; }
    {
      let [x, z] = P0, bad = false;
      for (let li = 0; li < legs.length && !bad; li++) {
        const l = legs[li], p = [-l.d[1], l.d[0]];
        for (let k = 7; k <= l.len; k += 7) {
          const cx = x + l.d[0] * k, cz = z + l.d[1] * k;
          if (li === legs.length - 1 && k === l.len) break;
          for (let q = -ROAD_HALF; q <= ROAD_HALF; q += 3) if (blocked(cx + p[0] * q, cz + p[1] * q)) { bad = true; break; }
          if (bad) break;
        }
        x += l.d[0] * l.len; z += l.d[1] * l.len;
      }
      if (bad) { S.veto++; continue; }
    }
    const { cells, dirs, turns } = roadCells(P0, legs);
    const seen = new Set();
    let bad = false, why = "";
    for (let i = 0; i < L && !bad; i++) {
      const [x, z] = cells[i], d = dirs[i], p = [-d[1], d[0]];
      const key = `${x},${z}`;
      if (seen.has(key)) { bad = true; why = "overlap"; break; }
      seen.add(key);
      if (i === 0 || i === L - 1) continue;
      for (let k = -ROAD_HALF; k <= ROAD_HALF; k++) if (blocked(x + p[0] * k, z + p[1] * k)) { bad = true; why = "veto"; break; }
    }
    if (bad) { if (why === "overlap") S.overlap++; else S.veto++; continue; }
    const gs = cells.map(([x, z]) => ground(x, z));
    const flat = new Uint8Array(L);
    for (let i = 0; i < 7 && i < L; i++) { flat[i] = 1; flat[L - 1 - i] = 1; }
    for (const ti of turns) for (let i = ti - 3; i <= ti + 3; i++) if (i >= 0 && i < L) flat[i] = 1;
    const rampBefore = new Int32Array(L), rampAfter = new Int32Array(L);
    for (let i = 1; i < L; i++) rampBefore[i] = rampBefore[i - 1] + (flat[i] ? 0 : 1);
    for (let i = L - 2; i >= 0; i--) rampAfter[i] = rampAfter[i + 1] + (flat[i] ? 0 : 1);
    let miss = 0, score = 0, span = 0;
    for (let i = 0; i < L; i++) {
      const c = gs[i];
      if (!c) { miss++; if (miss > 3) { bad = true; why = "unknown"; break; } continue; }
      const up = Math.floor(rampBefore[i] / ROAD_RAMP), down = Math.floor(rampAfter[i] / ROAD_RAMP);
      const loE = Math.max(H0 - up, H1 - down), hiE = Math.min(H0 + up, H1 + down);
      if (loE > hiE) { bad = true; why = "band"; break; }
      const floor = c.water ? c.g + 2 : c.g - ROAD_CUT_MAX;
      if (c.water || loE > c.g + ROAD_CUT) {
        if (hiE < floor) { bad = true; why = "band"; break; }
        if (!c.water && loE - c.g > BUILD_UP_MAX) { bad = true; why = "band"; break; }   // 1.3.224: piers of at most 15
        if (++span > ROAD_BRIDGE_MAX) { bad = true; why = "band"; break; }   // a deck may begin at the street's end (an embankment end)
        continue;
      }
      span = 0;
      const lo = Math.max(floor, loE), hi = Math.min(c.g + ROAD_CUT, hiE);
      if (lo > hi) { bad = true; why = "band"; break; }
    }
    if (bad) { if (why === "unknown") S.unknown++; else S.band++; continue; }
    let Hr = H0, run = 0, worst = 0, gspan = 0;
    for (let i = 0; i < L; i++) {
      const c = gs[i];
      if (!flat[i]) {
        run++;
        if (run === ROAD_RAMP) {
          run = 0;
          const rampsLeft = Math.floor(rampAfter[i] / ROAD_RAMP);
          const needEnd = H1 - Hr;
          let dir;
          if (Math.abs(needEnd) >= rampsLeft) dir = Math.sign(needEnd);
          else {
            const g = c ? c.g : Hr;
            dir = Math.sign(Math.round(g - Hr));
            if (dir === 0 && needEnd !== 0 && Math.abs(g - (Hr + Math.sign(needEnd))) <= ROAD_CUT - 1) dir = Math.sign(needEnd);
            if (Math.abs(needEnd - dir) > rampsLeft) dir = Math.sign(needEnd);
          }
          Hr += dir;
        }
      }
      if (c) {
        const d = Hr - c.g;
        if (c.water ? Hr >= c.g + 2 : d > ROAD_CUT) { score += 5; gspan++; if (gspan > ROAD_BRIDGE_MAX) worst = 99; }
        else { gspan = 0; worst = Math.max(worst, -d); score += Math.max(0, Math.abs(d) - 1); }
      }
    }
    if (worst > ROAD_CUT_MAX || Hr !== H1) { S.greedy++; continue; }
    cands.push({ legs, cells, dirs, turns, gs, score: score + 8 * turns.length + 0.3 * L });
  }
  cands.sort((p, q) => p.score - q.score);
  let best = null;
  for (const c of cands.slice(0, maxDP)) {
    const flat = [[0, 6], [c.cells.length - 7, c.cells.length - 1]].concat(c.turns.map((i) => [i - 3, i + 3]));
    const plan = planProfile(c.gs, { startDead: false, endDead: false, startH: H0, endH: H1, flat, maxCut: ROAD_CUT_MAX, maxFill: ROAD_CUT, bridgeDrop: ROAD_CUT, ramp: ROAD_RAMP, rampOnBridge: true });
    yield;
    S.sdp++;
    if (plan.cost === Infinity) { S.sdpFail++; continue; }
    if (!best || plan.cost < best.cost) best = { cells: c.cells, dirs: c.dirs, turns: c.turns, H: plan.H, segs: plan.segs, cost: plan.cost, legs: c.legs };
  }
  return best;
}
/** 0.0.14 (D-C544 / D-C546): the TERRAIN SEARCH — A* on a 4-cell lattice (the ramp unit) over (lattice cell, heading,
 *  road height), so the road's cut, fill, decks and 1-in-4 ramps are priced in the search itself: a straight move is 4
 *  cells flat or a ramp (+-1), a turn costs an elbow (7 flat cells: the move runs 4 cells on, turns, 4 cells on), the
 *  road's 7 cells across must be known and free, water / fill beyond ROAD_CUT is a deck (priced), a cut beyond ROAD_CUT_MAX
 *  is forbidden. The goal is entered by a straight approach of 1..7 cells heading d1 at H1. The found path is then
 *  profiled EXACTLY by planProfile (which may place the ramps differently but cannot do worse). A generator. */
export const ROAD_TUNE = { margin: 50, turn: 10, ramp: 2, yieldEvery: 60, hSpan: 8, maxPops: 80000, debug: 0 };   // 0.0.16: 60 pops per slice (a slice of 1,200 held the tick ~1 s); a search gives up at maxPops
const ROAD_SEARCH_MARGIN = ROAD_TUNE.margin, ROAD_TURN_COST = ROAD_TUNE.turn, ROAD_RAMP_COST = ROAD_TUNE.ramp, ROAD_YIELD = ROAD_TUNE.yieldEvery, ROAD_H_SPAN = ROAD_TUNE.hSpan;
export function* planRoadJob(ground, blocked, P0, d0, P1, d1, H0, H1, maxDP = 6, stats = null) {
  const S = stats || {};
  const byShapes = yield* planRoadShapesJob(ground, blocked, P0, d0, P1, d1, H0, H1, maxDP, S);
  if (byShapes) return byShapes;
  S.pops = 0; S.dp = 0; S.dpFail = 0; S.noPath = 0;
  const DIRS = [[1, 0], [0, 1], [-1, 0], [0, -1]];
  const dirIdx = (d) => DIRS.findIndex((q) => q[0] === d[0] && q[1] === d[1]);
  const d0i = dirIdx(d0), d1i = dirIdx(d1);
  if (d0i < 0 || d1i < 0) return null;
  const M = ROAD_TUNE.margin;
  const x0 = Math.min(P0[0], P1[0]) - M, x1 = Math.max(P0[0], P1[0]) + M;
  const z0 = Math.min(P0[1], P1[1]) - M, z1 = Math.max(P0[1], P1[1]) + M;
  const W = x1 - x0 + 1, Hh = z1 - z0 + 1, N = W * Hh;
  const G = new Int16Array(N), WET = new Uint8Array(N), VETO = new Uint8Array(N);
  for (let iz = 0; iz < Hh; iz++) for (let ix = 0; ix < W; ix++) {
    const c = ground(x0 + ix, z0 + iz), k = iz * W + ix;
    if (!c) { G[k] = -32768; continue; }
    G[k] = c.g; WET[k] = c.water ? 1 : 0;
    if (blocked(x0 + ix, z0 + iz)) VETO[k] = 1;
  }
  yield;
  const inBox = (ix, iz) => ix >= 0 && iz >= 0 && ix < W && iz < Hh;
  // the price of the road standing at H on cell (ix, iz) heading dir: its 7 cells across must be free; the centre cell's
  // ground prices the cut / fill / deck (Infinity = impossible)
  const cellPrice = (ix, iz, dir, H) => {
    const p = [-DIRS[dir][1], DIRS[dir][0]];
    for (let k = -ROAD_HALF; k <= ROAD_HALF; k++) {
      const ax = ix + p[0] * k, az = iz + p[1] * k;
      if (!inBox(ax, az)) return Infinity;
      const q = az * W + ax;
      if (VETO[q] || G[q] === -32768) return Infinity;
    }
    const q = iz * W + ix, g = G[q];
    if (WET[q]) return H >= g + 2 ? 6 : Infinity;
    const d = H - g;
    if (d > BUILD_UP_MAX) return Infinity;                                  // 1.3.224: no deck on piers higher than 15 (dry land)
    if (d > ROAD_CUT) return 5 + 0.15 * d;                                  // a deck
    if (d >= 0) return d;                                                   // fill
    if (-d > ROAD_CUT_MAX) return Infinity;                                 // no tunnels
    return -d * 1.3;                                                        // a cutting
  };
  // states on the lattice: (cell, dir, h = H - Hlo). 0.0.16: cells get a compact id on first visit (the lattice touches
  // ~1/16 of the box; dense arrays over the whole box x 4 x NH cost 60+ MB per search and tripped the memory watchdog)
  const Hlo = Math.min(H0, H1) - ROAD_TUNE.hSpan, NH = Math.abs(H1 - H0) + 2 * ROAD_TUNE.hSpan + 1;
  const cellIds = new Map(), cellOf = [];
  const cid = (cell) => { let k = cellIds.get(cell); if (k === undefined) { k = cellOf.length; cellIds.set(cell, k); cellOf.push(cell); } return k; };
  const idx = (cell, dir, h) => (cid(cell) * 4 + dir) * NH + h;
  const cost = [], from = [], how = [];                                      // grown on demand (undefined = unvisited)
  const costAt = (s) => { const v = cost[s]; return v === undefined ? Infinity : v; };
  const cellOfState = (s) => cellOf[Math.floor(s / (NH * 4))];
  let hf = new Float64Array(1 << 16), hs = new Int32Array(1 << 16), hn = 0;
  const push = (f, s) => {
    if (hn === hf.length) { const nf = new Float64Array(hn * 2), ns = new Int32Array(hn * 2); nf.set(hf); ns.set(hs); hf = nf; hs = ns; }
    let i = hn++; hf[i] = f; hs[i] = s;
    while (i > 0) { const pI = (i - 1) >> 1; if (hf[pI] <= hf[i]) break; const tf = hf[pI], ts = hs[pI]; hf[pI] = hf[i]; hs[pI] = hs[i]; hf[i] = tf; hs[i] = ts; i = pI; }
  };
  const pop = () => {
    const f = hf[0], s = hs[0]; hn--;
    if (hn > 0) { hf[0] = hf[hn]; hs[0] = hs[hn]; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < hn && hf[l] < hf[m]) m = l; if (r < hn && hf[r] < hf[m]) m = r; if (m === i) break; const tf = hf[m], ts = hs[m]; hf[m] = hf[i]; hs[m] = hs[i]; hf[i] = tf; hs[i] = ts; i = m; } }
    return [f, s];
  };
  const sx = P0[0] - x0, sz = P0[1] - z0, ex = P1[0] - x0, ez = P1[1] - z0;
  if (!inBox(sx, sz) || !inBox(ex, ez)) return null;
  const heur = (ix, iz, H) => Math.abs(ix - ex) + Math.abs(iz - ez) + Math.max(0, ROAD_RAMP * Math.abs(H1 - H) - Math.abs(ix - ex) - Math.abs(iz - ez)) * 0.5;
  const s0 = idx(sz * W + sx, d0i, H0 - Hlo);
  cost[s0] = 0; from[s0] = -1; push(heur(sx, sz, H0), s0);
  let goal = -1, pops = 0;
  // a move of n cells straight from (ix, iz) heading dir, the road rising dh over it (0 = flat; +-1 = a ramp: its surface
  // at H for the first cells then H + dh — priced at the lower level, the ramp blocks sit above)
  const movePrice = (ix, iz, dir, H, n, dh) => {
    let c = 0;
    for (let k = 1; k <= n; k++) {
      const cx = ix + DIRS[dir][0] * k, cz = iz + DIRS[dir][1] * k;
      if (!inBox(cx, cz)) return Infinity;
      const Hk = dh === 0 ? H : (dh > 0 ? H : H - 1);                        // a 4-part ramp: base at the lower level
      const pr = cellPrice(cx, cz, dir, Hk);
      if (pr === Infinity) return Infinity;
      c += pr;
    }
    return c;
  };
  while (hn > 0) {
    const [f, s] = pop();
    const h = s % NH, dir = Math.floor(s / NH) % 4, cell = cellOfState(s);
    const ix = cell % W, iz = Math.floor(cell / W), H = Hlo + h;
    const c = costAt(s);
    if (f - heur(ix, iz, H) > c + 1e-6) continue;
    if (++pops % ROAD_TUNE.yieldEvery === 0) yield;
    if (pops > ROAD_TUNE.maxPops) break;                                      // too wide a search: give this pair up
    // the goal: straight ahead along d1 within 1..7 cells, flat at H1
    if (dir === d1i && H === H1) {
      const dx = ex - ix, dz = ez - iz;
      const along = dx * DIRS[dir][0] + dz * DIRS[dir][1], acrossD = dx * DIRS[dir][1] - dz * DIRS[dir][0];
      if (acrossD === 0 && along >= 1 && along <= 7) {
        const pr = movePrice(ix, iz, dir, H, along, 0);
        if (pr < Infinity) { const ns = idx(ez * W + ex, dir, h); if (c + pr < costAt(ns)) { cost[ns] = c + pr; from[ns] = s; how[ns] = 99; } goal = ns; break; }
      }
    }
    // straight: 4 cells on the goal's lattice; a cell not yet on the lattice along this axis takes ONE move of 5..7 to
    // get there (so any goal line is met while the lattice stays sparse); flat / up / down (one ramp per move)
    const alongRes = ((DIRS[dir][0] ? (ix - ex) : (iz - ez)) % 4 + 4) % 4;
    const lens = alongRes === 0 ? [4] : [4 + (4 - alongRes)];
    for (const n of lens) for (const dh of [0, 1, -1]) {
      const nh = h + dh;
      if (nh < 0 || nh >= NH) continue;
      const pr = movePrice(ix, iz, dir, H, n, dh);
      if (pr === Infinity) continue;
      const nx = ix + DIRS[dir][0] * n, nz = iz + DIRS[dir][1] * n;
      const ns = idx(nz * W + nx, dir, nh);
      const nc = c + n + pr + (dh ? ROAD_RAMP_COST : 0);
      if (nc < costAt(ns)) { cost[ns] = nc; from[ns] = s; how[ns] = dh === 0 ? 0 : (dh > 0 ? 1 : 2); push(nc + heur(nx, nz, Hlo + nh), ns); }
    }
    // a turn: `n` cells on at H (flat; 4, or 5..7 to reach the lattice along this axis), turn, 4 cells on the new heading
    // (flat) — the elbow square lies flat around the corner
    for (const n of lens) for (const t of [1, -1]) {
      const nd = (dir + t + 4) % 4;
      const pr1 = movePrice(ix, iz, dir, H, n, 0);
      if (pr1 === Infinity) continue;
      const cx = ix + DIRS[dir][0] * n, cz = iz + DIRS[dir][1] * n;
      const pr2 = movePrice(cx, cz, nd, H, 4, 0);
      if (pr2 === Infinity) continue;
      const nx = cx + DIRS[nd][0] * 4, nz = cz + DIRS[nd][1] * 4;
      const ns = idx(nz * W + nx, nd, h);
      const nc = c + n + 4 + pr1 + pr2 + ROAD_TURN_COST;
      if (nc < costAt(ns)) { cost[ns] = nc; from[ns] = s; how[ns] = 3 + (t > 0 ? 0 : 1) + 2 * (n - 4); push(nc + heur(nx, nz, H), ns); }
    }
  }
  S.pops += pops;
  S.states = cellOf.length;
  if (goal < 0) {
    S.noPath++;
    if (ROAD_TUNE.debug) {                                                   // how close did the search get?
      let bestD = Infinity, bestInfo = null;
      for (let s = 0; s < cost.length; s++) { if (cost[s] === undefined) continue; const h = s % NH, dir = Math.floor(s / NH) % 4, cell = cellOfState(s); const ix = cell % W, iz = Math.floor(cell / W); const d = Math.abs(ix - ex) + Math.abs(iz - ez); if (d < bestD) { bestD = d; bestInfo = { x: x0 + ix, z: z0 + iz, dir: DIRS[dir], H: Hlo + h, cost: cost[s] }; } }
      S.closest = bestInfo; S.goalGround = G[ez * W + ex];
    }
    return null;
  }
  // the centre line from the move chain
  const chain = [];
  for (let s = goal; s !== undefined && s >= 0; s = from[s]) chain.push(s);
  chain.reverse();
  const cells = [[P0[0], P0[1]]], dirs = [d0];
  for (let i = 1; i < chain.length; i++) {
    const s = chain[i], prev = chain[i - 1];
    const dir = Math.floor(s / NH) % 4, pdir = Math.floor(prev / NH) % 4;
    const pcell = cellOfState(prev), pix = pcell % W, piz = Math.floor(pcell / W);
    const kind = how[s];
    let x = x0 + pix, z = z0 + piz;
    if (kind >= 3 && kind !== 99) {
      const n = 4 + ((kind - 3) >> 1);
      for (let k = 0; k < n; k++) { x += DIRS[pdir][0]; z += DIRS[pdir][1]; cells.push([x, z]); dirs.push(DIRS[pdir]); }
      for (let k = 0; k < 4; k++) { x += DIRS[dir][0]; z += DIRS[dir][1]; cells.push([x, z]); dirs.push(DIRS[dir]); }
    } else {
      const cell = cellOfState(s), ix = cell % W, iz = Math.floor(cell / W);
      const n = Math.abs(ix - pix) + Math.abs(iz - piz);
      for (let k = 0; k < n; k++) { x += DIRS[dir][0]; z += DIRS[dir][1]; cells.push([x, z]); dirs.push(DIRS[dir]); }
    }
  }
  const turns = [];
  for (let i = 1; i < cells.length; i++) if (dirs[i][0] !== dirs[i - 1][0] || dirs[i][1] !== dirs[i - 1][1]) turns.push(i - 1);
  const gs = cells.map(([x, z]) => ground(x, z));
  const L = cells.length;
  const flat = [[0, 6], [L - 7, L - 1]].concat(turns.map((i) => [i - 3, i + 3]));
  const plan = planProfile(gs, { startDead: false, endDead: false, startH: H0, endH: H1, flat, maxCut: ROAD_CUT_MAX, maxFill: ROAD_CUT, bridgeDrop: ROAD_CUT, ramp: ROAD_RAMP, rampOnBridge: true });
  yield;
  S.dp++;
  if (plan.cost === Infinity) {
    S.dpFail++;
    if (S.debug) (S.failed = S.failed || []).push({ cells, turns, gs: gs.map((c) => c ? (c.water ? "w" : c.g) : "?") });
    return null;
  }
  const legs = [];
  { let a = 0; for (const t of turns.concat([L - 1])) { legs.push({ d: dirs[a + 1] || dirs[a], len: t - a }); a = t; } }
  return { cells, dirs, turns, H: plan.H, segs: plan.segs, cost: plan.cost, legs };
}
