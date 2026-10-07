// pw_civ_lanes.js — CONTOUR LANES (his 20:01 / 20:48: "contour lanes so slopes become usable"; San Francisco / Atlanta —
// build WITH the rises and falls). Pure functions (no engine imports): the clock reads the land into a site field
// (site.at(x, z) = ground y, site.isWater(x, z)) and lays what these plan with the narrow-road machinery.
//
// A LANE is a narrow road (LANE_HALF each side of its centre line, the roads7 width) that keeps ONE level (H) the whole way:
// it follows a contour of the hillside, turning by right angles where the contour bends, so the houses along it stand on
// a terrace rather than on a slope. Lanes stack up a hill one storey-and-a-bit apart and are joined by stair streets
// and the switchback roads. A cell is fit for the lane when every column across its width lies within LANE_CUT above
// or LANE_FILL below H, is dry, and is not blocked (plots, streets, roads, other lanes).
//
// Houses front a lane on both sides on its STRAIGHT legs: frame t along the leg, w across it (the centre line w = 0), the
// house's front wall at w = +-(LANE_HALF + 1); their floor is the lane's level (a house is never on a ramp: the lane has
// none). Every lane house reaches the sewer: the lane carries its own GALLERY under the centre line (laneGalleryCells),
// joined to a street's sewer where the lane departs, and each house's cellar gallery is joined to it by a BRANCH
// (laneBranchCells) — his 20:36 rule.
import * as KIT from "./pw_civ_streets.js";
export const LANE_HALF = 3;               // 7 wide: the narrow roads' width (layRoadOp lays it)
export const LANE_CUT = 4, LANE_FILL = 4; // a cutting / an embankment of at most this under any column of the lane
export const LEG_MIN = 7, LEG_MAX = 42, LANE_MAX = 168, LANE_MIN = 28;
const DIRS = [[1, 0], [0, 1], [-1, 0], [0, -1]];
const left = (d) => [d[1], -d[0]], right = (d) => [-d[1], d[0]];

/** can the lane's cell (x, z) stand at level H (every column across the width; dir = the travel direction)? */
export function laneCellOk(site, x, z, dir, H, blocked) {
  const [vx, vz] = left(dir);
  for (let w = -LANE_HALF; w <= LANE_HALF; w++) {
    const cx = x + w * vx, cz = z + w * vz;
    if (blocked && blocked(cx, cz)) return false;
    const g = site.at(cx, cz);
    if (g === undefined || site.isWater(cx, cz)) return false;
    if (g - H > LANE_CUT || H - g > LANE_FILL) return false;
  }
  return true;
}
/** how many cells straight ahead from (x, z) (exclusive) the lane can run at H, up to max */
function runAhead(site, x, z, dir, H, blocked, max) {
  let k = 0;
  while (k < max && laneCellOk(site, x + dir[0] * (k + 1), z + dir[1] * (k + 1), dir, H, blocked)) k++;
  return k;
}
/** the mean |ground - H| over the next n cells (how well a direction holds the contour) */
function fitAhead(site, x, z, dir, H, n) {
  let s = 0, m = 0;
  for (let k = 1; k <= n; k++) { const g = site.at(x + dir[0] * k, z + dir[1] * k); if (g !== undefined) { s += Math.abs(g - H); m++; } }
  return m ? s / m : Infinity;
}
/** plan one lane from P0 (its first cell) heading d0 at level H: straight legs of LEG_MIN..LEG_MAX joined by right-angle
 *  turns toward the side that keeps the contour, until the land, the blocked cells or LANE_MAX end it. A turn needs
 *  LANE_HALF + 1 cells of the current leg past the corner (the elbow's width) and LEG_MIN cells ahead on the new leg.
 *  Returns { cells, dirs, H, legs: [{ a, len, dir }] } or null when shorter than LANE_MIN. O(LANE_MAX * width). */
export function planLane(site, P0, d0, H, blocked) {
  if (!laneCellOk(site, P0[0], P0[1], d0, H, blocked)) return null;
  const cells = [[P0[0], P0[1]]], dirs = [d0];
  const legs = [{ a: 0, len: 1, dir: d0 }];
  let [x, z] = P0, dir = d0, leg = 1, turns = 0;
  const used = new Set([`${x},${z}`]);
  const free = (cx, cz) => !used.has(`${cx},${cz}`) && !(blocked && blocked(cx, cz));
  const blk = (cx, cz) => !free(cx, cz) && !(cx === x && cz === z);
  while (cells.length < LANE_MAX) {
    const ahead = leg < LEG_MAX ? runAhead(site, x, z, dir, H, blk, 1) : 0;
    if (ahead) {
      x += dir[0]; z += dir[1]; cells.push([x, z]); dirs.push(dir); used.add(`${x},${z}`); leg++; legs[legs.length - 1].len++;
      continue;
    }
    // a corner: the leg must be long enough; the new direction must run LEG_MIN at H; prefer the one that hugs the contour
    if (leg < LANE_HALF + 1) break;
    const opts = [left(dir), right(dir)].map((d) => ({ d, run: runAhead(site, x, z, d, H, blk, LEG_MIN), fit: fitAhead(site, x, z, d, H, LEG_MIN) }))
      .filter((o) => o.run >= LEG_MIN).sort((a, b) => a.fit - b.fit);
    if (!opts.length || turns >= 6) break;
    dir = opts[0].d; leg = 0; turns++;
    legs.push({ a: cells.length, len: 0, dir });
    // the corner cell itself already stands; the new leg begins with the next cell
  }
  // drop an empty last leg
  if (legs.length && legs[legs.length - 1].len === 0) legs.pop();
  if (cells.length < LANE_MIN) return null;
  return { cells, dirs, H, legs, turns };
}
/** the leg's frame: t along it from its first cell, w to its LEFT (w = 0 the centre line) */
export function legFrame(lane, legIdx) {
  const L = lane.legs[legIdx];
  const [ox, oz] = lane.cells[L.a];
  const v = left(L.dir);
  return { ox, oz, ux: L.dir[0], uz: L.dir[1], vx: v[0], vz: v[1] };
}
const { cellOf, tw, rotFor, rotXZ } = KIT;                    // the kit's own frame and rotation laws (one law for streets and lanes)
/** a house slot on a lane leg: side +1 = the leg's left (w > 0), -1 = right; the front wall at w = +-(LANE_HALF + 1);
 *  the house's front (template local -x) faces the lane. Returns { x, z, rot, box, at, len, side, shaftT, H, corr } or null
 *  when the frontage would pass the leg's ends (the corners keep LANE_HALF + 1 clear). corr = the lane's w band (for
 *  slotRelief's "never the corridor"). */
export function laneSlot(lane, legIdx, side, def, shaftZ, at) {
  const L = lane.legs[legIdx];
  const fz = def.size[2], depth = def.size[0];
  const t0 = legIdx === 0 ? 0 : LANE_HALF + 1, t1 = L.len - 1 - (legIdx === lane.legs.length - 1 ? 0 : LANE_HALF + 1);
  if (at < t0 || at + fz - 1 > t1) return null;
  const f = legFrame(lane, legIdx);
  const away = side > 0 ? [f.vx, f.vz] : [-f.vx, -f.vz];
  const rot = rotFor([1, 0], away);
  const w0 = side > 0 ? LANE_HALF + 1 : -LANE_HALF - depth, w1 = side > 0 ? LANE_HALF + depth : -LANE_HALF - 1;
  const a = cellOf(f, at, w0), b = cellOf(f, at + fz - 1, w1);
  const box = [Math.min(a[0], b[0]), Math.max(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[1], b[1])];
  let shaftT = null;
  if (shaftZ !== null && shaftZ !== undefined) {
    const [sx, , sz] = def.size;
    const [ox, oz] = rotXZ(1, shaftZ, sx, sz, rot);
    shaftT = tw(f, box[0] + ox, box[2] + oz)[0];
  }
  return { x: box[0], z: box[2], rot, box, at, len: fz, side, shaftT, H: lane.H, f, corr: [-LANE_HALF, LANE_HALF], leg: legIdx };
}
/** the lane's sewer GALLERY: under the centre line, 3 wide (w -1..1), 4 high (H - 11 .. H - 8) — the kit hall's section —
 *  plus its lining (w +-2 and the rows H - 12 / H - 7) for the clock to clad where the ground is air or loose.
 *  Returns { air: [[x, y, z]...], lining: [[x, y, z]...] } over the lane's cells (corners included). */
export function laneGalleryCells(lane) {
  const air = [], lining = [];
  const seen = new Set();
  const add = (arr, x, y, z) => { const k = `${x},${y},${z}`; if (!seen.has(k)) { seen.add(k); arr.push([x, y, z]); } };
  lane.cells.forEach(([x, z], i) => {
    const d = lane.dirs[i], v = left(d);
    for (let w = -2; w <= 2; w++) {
      const cx = x + w * v[0], cz = z + w * v[1];
      for (let y = lane.H - 12; y <= lane.H - 7; y++) {
        const inner = Math.abs(w) <= 1 && y >= lane.H - 11 && y <= lane.H - 8;
        add(inner ? air : lining, cx, y, cz);
      }
    }
  });
  const airSet = new Set(air.map((c) => c.join(",")));
  return { air, lining: lining.filter((c) => !airSet.has(c.join(","))) };
}
/** a lane house's BRANCH: from its cellar gallery (front wall, floor - 11 .. floor - 8) across w = +-(LANE_HALF) .. +-2 to
 *  the gallery's side (w = +-1 is the gallery itself). Returns [[x, y, z]...] */
export function laneBranchCells(lane, legIdx, t, side) {
  const f = legFrame(lane, legIdx);
  const out = [];
  for (let k = 2; k <= LANE_HALF; k++) {
    const [x, z] = cellOf(f, t, side * k);
    for (let y = lane.H - 11; y <= lane.H - 8; y++) out.push([x, y, z]);
  }
  return out;
}
