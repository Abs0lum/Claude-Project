// pw_civ_plan.js — CIVITAS B6 GROWTH & BUILDING, the PURE half (no engine imports: node-tested in tests/test_plan.mjs).
// Program 228 (FIT-MATRIX BF6 + GB1 + GB5 + GB12 + GB13 + TR1 + TR2 + TR3 + EN2), fitted to OUR model:
//   * THE CHARTER IS LAW: a tier's lot counts never change; the pick only ORDERS them (and the leftovers) — civic works,
//     a business that cures a shortage, homes when rooms run short, then the rest; an unaffordable big project waits behind
//     affordable work (Millénaire's fallback, our manor rank). "Max 2 works at once" is DROPPED (1.3.226's crew-share law).
//   * REST: a family whose slot search failed rests FAIL_COOL days; a player PRIORITY (pw:clock prio <family>) goes first.
//   * DISTRICT SKINS (GB12): the skin (a..d) follows the district and the tier class instead of a roll.
//   * RELIEF (TR2 + TR3): a lot is judged on the 20th..80th percentile heights with a water share <= 8 % and an error
//     budget of bad cells (<= 10, or 5 % of a big box) — one boulder or one wet cell no longer vetoes a lot.
//   * FILLERS (GB13; his 12:20 "fillers only" — no garden quotas): a leftover stretch of frontage 4..(cottage width - 1)
//     gets a small filler (well / lamp / bench / cart), never counted as a lot.
//   * WEATHERING (EN2; his 12:20: "lived-in houses age too; past a bad level the city fines the household and repairs the
//     house"): a dwelling ages one band every WEATHER.bandDays it stands; band >= WEATHER.fineBand -> the council fines the
//     household (purse -> treasury) and repairs it (band 0).
import { hash32 } from "./pw_civ_people.js";

export const ROLE = { civic: 6, cure: 4, homesShort: 4, home: 2, business: 1 };
export const AFFORD = { shortX: 0.3, prodDays: 5 };
export const FAIL_COOL = 2;                       // village days a family rests after a failed slot search
export const BIG = ["manor", "town_hall", "palace"];
export const HOMES = ["cottage_s", "cottage_m", "cottage_l", "townhouse", "manor", "farm_wheat", "farm_terrace", "farm_cattle"];

/** the weight of one plan item. it = {nm (short family), work?, fam?}; c = { shortGoods: Set, produces(nm) -> [goods],
 *  roomsFree, missing(nm) -> {} | {...}, prio: [nm...] } */
export function weightOf(it, c) {
  const nm = it.nm || it.fam || "";
  let w;
  if (it.work) w = ROLE.civic;
  else if ((c.produces ? c.produces(nm) : []).some((g) => c.shortGoods && c.shortGoods.has(g))) w = ROLE.cure;
  else if (HOMES.includes(nm)) w = (c.roomsFree ?? 99) < 2 ? ROLE.homesShort : ROLE.home;
  else w = ROLE.business;
  const miss = c.missing ? c.missing(nm) : {};
  if (miss && Object.keys(miss).length) w *= AFFORD.shortX;
  if (c.prio && c.prio.includes(nm)) w += 100;                                   // a player's priority first (GB5)
  return w;
}

/** BF6: the charter's items in pick order (the same items: counts are law). Deterministic: ties by hash32(seed, index). */
export function orderItems(items, c, seed = 0) {
  return items.map((it, i) => ({ it, i, w: weightOf(it, c), h: hash32((seed >>> 0) ^ (i * 2654435761 >>> 0), 0x5EED) }))
    .sort((a, b) => b.w - a.w || a.h - b.h || a.i - b.i).map((x) => x.it);
}

/** the next leftover to try today: priority first, then the highest weight, skipping families at rest (failCool) */
export function nextLeftover(leftover, c, day, failCool = {}, seed = 0) {
  const ready = leftover.map((nm, i) => ({ nm, i })).filter((x) => !(failCool[x.nm] > day));
  if (!ready.length) return null;
  const ord = orderItems(ready.map((x) => ({ nm: x.nm, _i: x.i })), c, seed);
  return { nm: ord[0].nm, index: ord[0]._i };
}
export function rest(failCool, nm, day) { failCool[nm] = day + FAIL_COOL; return failCool; }
export function pruneCool(failCool, day) { for (const [k, d] of Object.entries(failCool || {})) if (d <= day) delete failCool[k]; return failCool; }

// --------------------------------------------------------------------------------------------- GB12 district skins
// skins: the families' existing a..d variants. prestige -> the stone skin (d) when it exists; craft -> c; homes -> a / b by
// the street's parity; edge -> a. A missing skin falls back down the list.
export function skinFor(district, skins, tierClass = 0, streetId = 0) {
  if (!skins || !skins.length) return "a";
  const want = district === "prestige" ? (tierClass >= 1 ? ["d", "c", "b", "a"] : ["b", "a"])
    : district === "craft" ? ["c", "b", "a"]
    : district === "edge" ? ["a", "b"]
    : (streetId % 2 ? ["b", "a"] : ["a", "b"]);
  for (const k of want) if (skins.includes(k)) return k;
  return skins[0];
}

// --------------------------------------------------------------------------------------------- TR2 + TR3 relief
export const RELIEF = { lo: 0.2, hi: 0.8, water: 0.08, badMax: 10, badShare: 0.05, bigArea: 200, badDelta: 10 };
export function percentile(sorted, q) {
  if (!sorted.length) return 0;
  const i = Math.min(sorted.length - 1, Math.max(0, Math.round(q * (sorted.length - 1))));
  return sorted[i];
}
/** cells = [{ h, wet }] sampled over a lot; H = the street's level. Returns { ok, lo, hi, water, bad, why } */
export function judgeLot(cells, H, area = cells.length) {
  if (!cells.length) return { ok: false, why: "no cells" };
  const dry = cells.filter((c) => !c.wet).map((c) => c.h).sort((a, b) => a - b);
  const water = 1 - dry.length / cells.length;
  if (water > RELIEF.water) return { ok: false, water, why: "water" };
  const lo = percentile(dry, RELIEF.lo), hi = percentile(dry, RELIEF.hi);
  const bad = cells.filter((c) => c.wet || Math.abs(c.h - H) > RELIEF.badDelta).length;
  const budget = area > RELIEF.bigArea ? Math.floor(area * RELIEF.badShare) : RELIEF.badMax;
  if (bad > budget) return { ok: false, lo, hi, water, bad, why: "bad cells" };
  return { ok: true, lo, hi, water, bad };
}

// --------------------------------------------------------------------------------------------- GB13 fillers
export const FILLERS = ["well", "lamp", "bench", "cart"];
export const FILLER_W = { well: 3, lamp: 1, bench: 2, cart: 2 };
/** a leftover stretch [t0, t1) of a street's frontage -> the filler for it (deterministic by t0), or null */
export function fillerFor(t0, t1, minLot, streetId = 0) {
  const len = t1 - t0;
  if (len < 4 || len >= minLot) return null;
  const fits = FILLERS.filter((f) => FILLER_W[f] <= len - 2);
  if (!fits.length) return null;
  return fits[hash32((t0 * 131 + streetId) >>> 0, 0xF111) % fits.length];
}

// --------------------------------------------------------------------------------------------- EN2 weathering
export const WEATHER = { bandDays: 40, bands: 3, fineBand: 3, integrity: [0, 0.25, 0.45, 0.6], finePerBand: 4, mood: 4 };
/** the age band of a dwelling standing `age` days (0..WEATHER.bands) */
export function bandOf(age) { return Math.max(0, Math.min(WEATHER.bands, Math.floor((age || 0) / WEATHER.bandDays))); }
/** the fine (pennies) a household pays when its house passes the bad level: the repair's share, from the purse */
export function fineOf(band, coin = 12) { return band >= WEATHER.fineBand ? WEATHER.finePerBand * band * coin : 0; }

// --------------------------------------------------------------------------------------------- 1.3.230 (PL) FRONTAGE PLATEAUS
// Owner backlog "frontage plateau" (gate logs: "23 more cottage_m would fit along 4 streets (475 cells of frontage of 722)";
// "SPRAWL on hills — 9 streets for 22 buildings ... houses need flat frontage -> terraced platforms"). Where a street side is
// too steep for a plot's flat footprint, the planner may CUT / FILL a level PAD for it:
//   * the pad stands at the street's height at the door, or one step above it (never below any sidewalk cell of its
//     frontage: the floor is the highest sidewalk) — a frontage may rise PLATEAU.frontRise (2) instead of FRONT_RISE (1);
//   * the pad = the house's 1-cell RING (the box itself is the structure's own cut and fill); its cut and its fill are each
//     at most cutMax / fillMax (6);
//   * DOWNHILL: a ring cell whose outside lies 2+ below the pad is a STONE RETAINING WALL (from the ground outside + 1 to
//     P - 1, the pad's top on it); a drop of more than one lift gets BERM lifts beyond (top P - 3, P - 6; R5: walls <= 3);
//   * UPHILL: the hill beyond the ring is cut in LIFTS — one clad wall (<= 3 high) per cell of setback (stepBerm's law), up
//     to faceLifts lifts; a hill that would overtop the last lift refuses the plateau;
//   * NEVER INTO another plot (its box holds the hill / abuts: a face stops there; a ring or berm cell refuses), a street,
//     water or a protected tree (refused wherever a cell must be worked);
//   * DRAINAGE (his water law, 10-05: "water can't be stopped, only moved"): a gravel gutter along the foot of the cut face
//     and down one side ring to a GRATED DROP beside the street, which falls to the top rows of the street's sewer hall
//     (H - 9 .. H - 8) and is joined to it through the corridor's side wall (4 cells, like a house branch); no hall at either end
//     (a bridge, a dead end) -> a soakaway pit (gravel lower half);
//   * the COST (stone for the walls, clad faces and gutter; an iron grate; the earth moved as labourer days) is added to
//     the plot's first paid stage bill (plateauBillInto).
export const PLATEAU = { cutMax: 6, fillMax: 6, lift: 3, faceLifts: 3, frontRise: 2, doorStep: 1, boxDrop: 12,
  earthPerDay: 80, wageLabour: 72, soakDepth: 8, hallTop: 8 };

/** the pad's height from the frontage's sidewalk heights Hs (q = 0 .. fz - 1) and the door's q: { ok, P, rise, step, why } */
export function padHeight(Hs, doorQ, dials = PLATEAU) {
  if (!Hs || !Hs.length || Hs.some((h) => h === undefined || h === null)) return { ok: false, why: "unknown" };
  let lo = Infinity, hi = -Infinity;
  for (const h of Hs) { if (h < lo) lo = h; if (h > hi) hi = h; }
  const rise = hi - lo;
  if (rise > dials.frontRise) return { ok: false, why: "rise", rise };
  const step = hi - Hs[Math.max(0, Math.min(Hs.length - 1, doorQ))];
  if (step > dials.doorStep) return { ok: false, why: "door", rise, step };
  return { ok: true, P: hi, rise, step };
}

/** the outward directions of a ring cell (never the street side: d = -1 is the corridor) */
function ringOut(q, d, fz, depth) {
  const out = [];
  if (q === -1) out.push([-1, 0]);
  if (q === fz) out.push([1, 0]);
  if (d === depth) out.push([0, 1]);
  return out;
}

/** plan one plateau. g = { fz, depth, P, Hring(q) -> street H at ring t (q -1 .. fz) | undefined, hallAt(q) -> the sewer
 *  hall's street H under that t | undefined, ground(q, d) -> { h, wet } | undefined (unread), blocked(q, d) -> null |
 *  "plot" | "street" | "water" | "tree", skipBox (the job: the house already stands), boxFillMax (default boxDrop; the
 *  park: fillMax), dials }. q runs along the frontage (0 .. fz - 1 = the box), d away from the corridor (0 = the row
 *  against it, depth = the rear ring). Returns { ok, why, at } or { ok, P, cut, fill, ops, cutVol, fillVol, drain, bill }.
 *  ops (in build order): pad {q, d, g, y: P, wall: y0 | null} · berm {q, d, g, y} · face {q, d, g, y, clad: [y0, y1] | null}
 *  · gutter {q, d, y} · outlet {q, d, y, yBot, to} · link {q, k, y} (corridor cell k = 0..3 inward from its edge). */
export function planPlateau(g) {
  const dl = { ...PLATEAU, ...(g.dials || {}) };
  const { fz, depth, P } = g;
  const boxFillMax = g.boxFillMax ?? dl.boxDrop;
  const memo = new Map();
  const G = (q, d) => { const k = q * 4099 + d; if (!memo.has(k)) memo.set(k, g.ground(q, d)); return memo.get(k); };
  const B = (q, d) => (g.blocked ? g.blocked(q, d) : null);
  const fail = (why, at = null) => ({ ok: false, why, at });
  let cut = 0, fill = 0;
  // the box: measured (a cut beyond the dial, a hollow below the house's subsurface, standing water), never worked
  if (!g.skipBox) {
    let wet = 0, n = 0;
    for (let q = 0; q < fz; q++) for (let d = 0; d < depth; d++) {
      const c = G(q, d);
      if (!c) return fail("unknown", [q, d]);
      n++;
      if (c.wet) { wet++; continue; }
      if (c.h - P > cut) cut = c.h - P;
      if (P - c.h > boxFillMax) return fail("fill", [q, d]);
    }
    if (wet > n * RELIEF.water) return fail("water");
  }
  // the ring (the pad proper): side columns q = -1 and q = fz (d 0 .. depth), the rear row d = depth
  const ring = [];
  for (let q = -1; q <= fz; q++) for (let d = 0; d <= depth; d++) if (!(q >= 0 && q < fz && d < depth)) ring.push([q, d]);
  for (const [q, d] of ring) {
    const bl = B(q, d);
    if (bl) return fail(bl, [q, d]);
    const c = G(q, d);
    if (!c) return fail("unknown", [q, d]);
    if (c.wet) return fail("water", [q, d]);
    if (c.h - P > cut) cut = c.h - P;
    if (P - c.h > fill) fill = P - c.h;
  }
  if (cut > dl.cutMax) return fail("cut");
  if (fill > dl.fillMax) return fail("fill");
  const ops = [], tail = [];
  let cutVol = 0, fillVol = 0, stone = 0;
  const faced = new Set();
  // one outward ray from a ring cell: the downhill berms or the uphill terraces. Returns { ok, exposure, bermed } or a fail.
  const ray = (q, d, dq, dd) => {
    const b1 = B(q + dq, d + dd);
    if (b1 === "plot") return { ok: true, exposure: 0, bermed: false };       // the neighbour's box abuts (and holds) the pad
    const o1 = G(q + dq, d + dd);
    if (!o1) return fail("unknown", [q + dq, d + dd]);
    if (o1.h > P + 1) {
      // UPHILL: the cut is retained in LIFTS (stepBerm's law, R5: a wall <= 3 high, one cell of setback per lift): row j is
      // cut down to P + lift * j and its face clad from the row before + 1; the first row whose ground lies within its lift
      // is only clad (natural from there on). A hill still above the lift after faceLifts rows would be overtopped: refused.
      let prev = P;
      for (let j = 1; j <= dl.faceLifts + 1; j++) {
        const cq = q + dq * j, cd = d + dd * j;
        const bl = B(cq, cd);
        if (bl === "plot" || bl === "street") return { ok: true, exposure: 0, bermed: false };   // they hold the hill there
        const c = G(cq, cd);
        if (!c) return fail("unknown", [cq, cd]);
        if (c.h <= prev + 1) return { ok: true, exposure: 0, bermed: false };   // the natural slope from here on
        const cap = P + dl.lift * j;
        if (c.h > cap && j > dl.faceLifts) return fail("cut", [cq, cd]);      // the last lift would be overtopped
        if (bl) return fail(bl, [cq, cd]);                                      // water / a protected tree in the works
        if (c.wet) return fail("water", [cq, cd]);
        const y = Math.min(c.h, cap);
        tail.push({ kind: "face", q: cq, d: cd, g: c.h, y, clad: [prev + 1, y] });
        cutVol += c.h - y;
        stone += y - prev;
        faced.add(q * 4099 + d);
        if (c.h <= cap) return { ok: true, exposure: 0, bermed: false };       // the face meets the natural ground
        prev = y;
      }
      return { ok: true, exposure: 0, bermed: false };
    }
    const exposure = P - o1.h;
    if (exposure < 2) return { ok: true, exposure: 0, bermed: false };
    if (exposure > dl.fillMax) return fail("drop", [q + dq, d + dd]);
    // DOWNHILL: berm lifts (top P - lift * k) while the ground lies more than one below the next lift
    const K = Math.floor(dl.fillMax / dl.lift);
    let bermed = false;
    for (let k = 1; k <= K + 1; k++) {
      const cq = q + dq * k, cd = d + dd * k;
      const T = P - dl.lift * k;
      const bl = B(cq, cd);
      if (bl === "plot" && k > 1) return { ok: true, exposure, bermed };       // the neighbour's box below holds the toe
      const c = G(cq, cd);
      if (!c) return fail("unknown", [cq, cd]);
      if (c.h >= T - 1) return { ok: true, exposure, bermed };                  // the ground meets this lift: done
      if (k > K) return fail("drop", [cq, cd]);
      if (bl) return fail(bl, [cq, cd]);
      if (c.wet) return fail("water", [cq, cd]);
      if (T - c.h > dl.fillMax) return fail("drop", [cq, cd]);
      tail.push({ kind: "berm", q: cq, d: cd, g: c.h, y: T });
      fillVol += T - c.h;
      stone += Math.max(0, T - 1 - c.h);
      bermed = true;
    }
    return { ok: true, exposure, bermed };
  };
  for (const [q, d] of ring) {
    const c = G(q, d);
    let exposure = 0, bermed = false;
    if (d === 0 && (q === -1 || q === fz) && g.Hring) { const hs = g.Hring(q); if (hs !== undefined && P - hs > exposure) exposure = P - hs; }   // the street face
    for (const [dq, dd] of ringOut(q, d, fz, depth)) {
      const r = ray(q, d, dq, dd);
      if (!r.ok) return r;
      if (r.exposure > exposure) exposure = r.exposure;
      bermed = bermed || r.bermed;
    }
    if (exposure > dl.fillMax) return fail("drop", [q, d]);
    const wall = exposure >= 2 ? (bermed ? P - dl.lift + 1 : P - exposure + 1) : null;
    ops.push({ kind: "pad", q, d, g: c.h, y: P, wall });
    cutVol += Math.max(0, c.h - P);
    fillVol += Math.max(0, P - c.h);
    if (wall !== null) stone += P - wall;
  }
  ops.push(...tail.filter((o) => o.kind === "berm"), ...tail.filter((o) => o.kind === "face"));
  // the DRAIN: the side whose street end is not above the pad, a sewer hall before a soakaway, a gap not shared with a
  // built neighbour, the lower street end, then q = -1
  const cands = [-1, fz].map((qd) => {
    const H = g.Hring ? g.Hring(qd) : undefined;
    const usable = H !== undefined && H <= P;
    const hall = usable && g.hallAt ? g.hallAt(qd) : undefined;
    return { qd, H, usable, hall, shared: B(qd + (qd < 0 ? -1 : 1), 0) === "plot" };
  });
  cands.sort((a, b) => (b.usable - a.usable) || ((b.hall !== undefined) - (a.hall !== undefined)) || (a.shared - b.shared)
    || ((a.H ?? 1e9) - (b.H ?? 1e9)) || (a.qd - b.qd));
  const dr = cands[0];
  const to = dr.hall !== undefined ? "sewer" : "soak";
  const far = dr.qd === -1 ? fz : -1;
  const run = [];
  if (faced.size) for (let q = far; q !== dr.qd; q += dr.qd > far ? 1 : -1) run.push([q, depth]);   // along the face's foot
  for (let d = depth; d >= 0; d--) run.push([dr.qd, d]);                                              // down the side ring
  const gut = new Map(run.slice(0, -1).map(([q, d]) => [q * 4099 + d, [q, d]]));
  for (const k of faced) {                                                     // a faced far side column joins the corner
    const q = Math.round(k / 4099), d = k - q * 4099;
    if (q === far && faced.size) for (let dd = d; dd <= depth; dd++) gut.set(q * 4099 + dd, [q, dd]);
  }
  for (const [q, d] of gut.values()) { ops.push({ kind: "gutter", q, d, y: P }); stone += 2; }     // gravel on a cobblestone bed
  // the hall's top row is H - hallTop under a flat piece and one lower under some ramp pieces: the drop and its link span
  // both rows (H - hallTop - 1 .. H - hallTop), inside the rows a house branch already carves (H - 11 .. H - 8)
  const yBot = to === "sewer" ? dr.hall - dl.hallTop - 1 : P - dl.soakDepth;
  ops.push({ kind: "outlet", q: dr.qd, d: 0, y: P, yBot, to });
  if (to === "sewer") for (let k = 0; k < 4; k++) for (let y = yBot; y <= yBot + 1; y++) ops.push({ kind: "link", q: dr.qd, k, y });
  else stone += Math.ceil(dl.soakDepth / 2);
  const earth = cutVol + fillVol;
  const labourDays = earth > 0 ? Math.ceil(earth / dl.earthPerDay) : 0;
  return { ok: true, P, cut: Math.max(0, cut), fill: Math.max(0, fill), ops, cutVol, fillVol,
           drain: { q: dr.qd, H: dr.H, to, run, outlet: [dr.qd, 0] },
           bill: { stone, iron: 1, earth, labourDays, wages: labourDays * dl.wageLabour } };
}

/** the plot's first paid stage bill with its plateau's cost: stone + iron into the materials (and the builders' blocks),
 *  the labourers' wages for the earth moved. A plot without a plateau keeps its bill (the same object). */
export function plateauBillInto(bill, land, perDay = 40, builderWage = 120) {
  if (!land || land.kind !== "plateau") return bill;
  const mats = { ...bill.mats };
  if (land.stone) mats.stone = (mats.stone || 0) + land.stone;
  if (land.iron) mats.iron = (mats.iron || 0) + land.iron;
  const blocks = bill.blocks + (land.stone || 0) + (land.iron || 0);
  const builderDays = Math.max(1, Math.ceil(blocks / perDay));
  return { ...bill, mats, blocks, builderDays, wages: builderDays * builderWage + (land.wages || 0), plateau: true };
}
