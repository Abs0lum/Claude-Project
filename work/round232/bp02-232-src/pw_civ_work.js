// pw_civ_work.js — CIVITAS WORK IN REAL TIME (C2.2; his 22:28 / 22:30 rulings D-C541 / D-C542): the quarrymen MINE the pit
// face block by block, the woodcutters CHOP a tree and fell it, and both CARRY their load to their workshop's store chest,
// which is where the town's stock comes from. Nothing is produced by a timer: today's stone is the stone a villager broke
// and put in the chest today. Work hours 1000..11000; outside them the workers go home with the schedule (pw_civ_clock).
//
// A worker is a villager tagged civ:keeper of a quarry / lumberyard (its keeper) — more hands (household members whose
// census job is the workshop) join with the same loop (tag civ:person:<id> with person.job = the workshop's id).
// States: toFace (walking) -> work (one block per MINE_TICKS / one log per CHOP_TICKS) -> toStore (walking) -> deposit.
// Spoil (dirt, gravel) is kept on the workshop (b.spoil) for the pit's re-greening (F2); saplings go in beside every stump.
// 1.3.228 (B1): the beat is a heartbeat slot (pw_civ_beat.js: 3 and 13 of 20); every block read goes through the clock's
// guarded API.blockAt (null = the chunk sleeps: the old `catch` path; undefined = outside the world: the old `!blk` path)
// 1.3.228 (B4): each hand works his OWN shift (API.onShift: template, offset, days off, the walk home); in rain he SHELTERS
// inside the workshop's door (his claim goes, the barrow stays) and the day keeps half his output (the clock's produceDaily)
import { world, system, ItemStack } from "@minecraft/server";
import * as WALK from "./pw_civ_walk.js";
import * as HB from "./pw_civ_beat.js";

let API = null;
export function initWork(api) { API = api; }

const WORK = [1000, 11000];
const MINE_TICKS = 40, CHOP_TICKS = 30;                 // a block every 2 s; a log every 1.5 s
const LOAD_MAX = 16;                                    // a barrow
const REACH_H = 3.2, REACH_V = 4;                       // a face within this of the worker's feet can be struck
const BEAT = 10;
const workers = new Map();                              // villager id -> { shop, state, face, load, next, since }

// --------------------------------------------------------------------------------------------- work-site CLAIMS (1.3.228 B2 / BF10)
// Two hands never take the same tree or the same quarry face: a site (its column "x,z") is CLAIMED by one villager until it
// is felled / dug, he goes off duty, his body is gone, or CLAIM_TTL ticks pass without him working it (renewed while he
// walks to it and works it). Among free sites the LONGEST-UNTOUCHED goes first (a site never claimed before = oldest;
// ties keep the caller's order, nearest first). Memory only (save 0).
const CLAIM_TTL = 1200, TOUCH_KEEP = 24000;
export function createClaims(ttl = CLAIM_TTL) {
  const held = new Map();                               // "x,z" -> { vid, until }
  const touched = new Map();                            // "x,z" -> the tick its last claim ended
  const stat = { taken: 0, refused: 0, released: 0, expired: 0 };
  const holder = (key, now) => {
    const h = held.get(key);
    if (!h) return null;
    if (h.until <= now) { held.delete(key); touched.set(key, now); stat.expired++; return null; }
    return h.vid;
  };
  const C = {
    holder,
    free: (key, vid, now) => { const h = holder(key, now); return h === null || h === vid; },
    take(key, vid, now) {
      const h = holder(key, now);
      if (h !== null && h !== vid) { stat.refused++; return false; }
      held.set(key, { vid, until: now + ttl });
      if (h === null) stat.taken++;
      return true;
    },
    renew(key, vid, now) { const h = held.get(key); if (h && h.vid === vid) h.until = now + ttl; },
    release(key, vid, now) { const h = held.get(key); if (h && (vid === undefined || h.vid === vid)) { held.delete(key); touched.set(key, now); stat.released++; } },
    releaseAll(vid, now) { for (const [k, h] of held) if (h.vid === vid) { held.delete(k); touched.set(k, now); stat.released++; } },
    /** the candidates in pick order: free ones only, longest-untouched first (stable: the caller's order breaks ties) */
    order(cands, keyOf, vid, now) {
      const free = cands.filter((c) => C.free(keyOf(c), vid, now));
      const age = (c) => { const t = touched.get(keyOf(c)); return t === undefined ? -Infinity : t; };
      return free.map((c, i) => [c, age(c), i]).sort((a, b) => a[1] - b[1] || a[2] - b[2]).map((e) => e[0]);
    },
    prune(now) { for (const [k, t] of touched) if (now - t > TOUCH_KEEP) touched.delete(k); for (const [k, h] of held) if (h.until <= now) { held.delete(k); stat.expired++; } },
    stats: () => ({ held: held.size, touched: touched.size, ...stat }),
  };
  return C;
}
export const CLAIMS = createClaims();
const siteKey = (f) => `${f.x},${f.z}`;
/** the clock's daily clearing asks before it fells: is this column a hand's claimed tree? */
export function claimHeld(x, z) { return CLAIMS.holder(`${x},${z}`, system.currentTick) !== null; }
/** a worker's why-idle code (BF3): NO_FACE (no face / no real tree found), STOCK_FULL (the store chest is full), else null */
export function whyOf(vid) {
  const w = workers.get(vid);
  if (!w) return null;
  if (w.state === "shelter") return "SHELTER";                           // 1.3.228 (B4, rain ruling): sheltering, half kept
  if (w.full) return "STOCK_FULL";
  if (w.noFace && (!w.face || w.face.done)) return "NO_FACE";
  return null;
}

/** the store chest of a workshop: its first chest / barrel in the template, in world coordinates */
function storeOf(b) {
  if (b.store) return b.store;
  const def = API.BUILDINGS[b.family];
  if (!def || !def.chests || !def.chests.length) return null;
  const [lx, ly, lz] = def.chests[0];
  const [ox, oz] = API.rotXZ(lx, lz, def.size[0], def.size[2], b.rot);
  b.store = { x: b.x + ox, y: b.y + ly, z: b.z + oz };
  return b.store;
}

// --------------------------------------------------------------------------------------------- the quarry face
const STONE_DROP = (id) => {
  const n = id.replace("minecraft:", "");
  if (n === "stone" || n === "cobblestone" || n === "mossy_cobblestone") return ["minecraft:cobblestone", "stone"];
  if (n === "deepslate" || n === "cobbled_deepslate") return ["minecraft:cobbled_deepslate", "stone"];
  if (["andesite", "diorite", "granite", "tuff", "calcite", "sandstone", "red_sandstone"].includes(n)) return [id, "stone"];
  if (n === "coal_ore" || n === "deepslate_coal_ore") return ["minecraft:coal", "coal"];
  if (n === "iron_ore" || n === "deepslate_iron_ore") return ["minecraft:raw_iron", "iron"];
  if (n === "copper_ore" || n === "deepslate_copper_ore") return ["minecraft:raw_copper", "copper"];
  if (n === "gold_ore" || n === "deepslate_gold_ore") return ["minecraft:raw_gold", "gold"];
  if (["dirt", "grass_block", "coarse_dirt", "rooted_dirt", "gravel", "sand", "clay", "podzol", "mud"].includes(n)) return [null, "spoil"];
  return [null, "spoil"];
};
/** the next block of the pit to strike (the same stepped bowl the clock's digQuarry digs): { x, y, z, id } or null when
 *  the pit is worked out at its size (it grows a ring / a step then), undefined when its ground is unloaded */
/** the pit a quarry works now: its centre, radius and depth (0.0.24: capped; a worked-out pit makes way for the next one
 *  beside it — pit.off — and joins b.oldPits to re-green: run 0.0.23's accelerated days dug the only pit out, r 16 > cap 14,
 *  and the real hands then found no face at all) */
export function pitOf(b, def, tierIdx, ctx = null) {
  const c = API.backOf(b, def);
  const pit = (b.pit = b.pit || { r: 4 + 2 * tierIdx, depth: 2 + tierIdx, i: 0, off: 0 });
  const rmax = pit.rmax || API.QUARRY_R_MAX;                                          // 0.0.25h: a small site's own cap
  pit.r = Math.min(rmax, Math.max(pit.r, Math.min(rmax, 4 + 2 * tierIdx))); pit.depth = Math.min(API.QUARRY_D_MAX, Math.max(pit.depth, 2 + tierIdx));
  const dirx = b.rot === 0 ? 1 : b.rot === 2 ? -1 : 0, dirz = b.rot === 1 ? 1 : b.rot === 3 ? -1 : 0;
  // 0.0.25: the pit stands on a chosen SITE (back / beside / further back — the land with the most rock above its floor,
  // no plot or street in it); its near edge stays put while it grows (the centre moves out with the radius)
  if (pit.site === undefined && ctx && ctx.dim) {
    const pick = choosePitSite(b, def, ctx, new Set());
    if (pick && pick.wait) return { pit, cx: 0, cz: 0, dirx: 0, dirz: 0, wait: true };          // 0.0.25d: its land sleeps — ask again later
    pit.site = pick ? pick.k : 0;
    if (pick && pick.rmax) pit.rmax = pick.rmax;
    if (pick && pick.top !== undefined) b.pitTop = pick.top;
  }
  const [bk, lt] = pit.site !== undefined ? PIT_SITES[pit.site] : [pit.off || 0, 0];
  const reach = pit.r + 1 + bk * PIT_STEP();
  const lat = lt * PIT_STEP();
  return { pit, cx: c.x + dirx * reach - dirz * lat, cz: c.z + dirz * reach + dirx * lat, dirx, dirz };
}
// 0.0.25 (run 0.0.24: the accelerated days worked out four pits in a row, each 2r+3 further out — the fifth lay 124 blocks
// behind the quarry, beyond the hands' reach: no stone at all): at most PIT_SITES.length pits per quarry, around it
const PIT_SITES = [[0, 0], [0, 1], [0, -1], [1, 0], [1, 1], [1, -1]];          // [back, lateral] in pit steps
const PIT_STEP = () => 2 * API.QUARRY_R_MAX + 3;
const PIT_R_SMALL = 8, PIT_OCC = 0.12;
/** the best unused pit site: sampled every 2nd column at the cap radius — no plot / street / square in it (2 % at most),
 *  the most rock between the ground and the floor a pit of the cap depth would reach (median ground = its top) */
function choosePitSite(b, def, ctx, used) {
  const c = API.backOf(b, def);
  const dirx = b.rot === 0 ? 1 : b.rot === 2 ? -1 : 0, dirz = b.rot === 1 ? 1 : b.rot === 3 ? -1 : 0;
  const D = API.QUARRY_D_MAX, S = PIT_STEP();
  let best = null;
  const unknownSites = [];
  // 0.0.25h (run 0.0.27: worked out after ONE pit — on a crowded hill every other site touched a street or a plot): each
  // site is tried at the full radius, then at PIT_R_SMALL; up to PIT_OCC of its columns may be taken (the dig skips them)
  for (const [k, R] of PIT_SITES.flatMap((_, k2) => [[k2, API.QUARRY_R_MAX], [k2, PIT_R_SMALL]])) {
    if (used.has(k) || (best && best.k === k)) continue;
    const [bk, lt] = PIT_SITES[k];
    const reach = R + 1 + bk * S, lat = lt * S;
    const cx = c.x + dirx * reach - dirz * lat, cz = c.z + dirz * reach + dirx * lat;
    let n = 0, occ = 0, unknown = 0;
    const gs = [];
    for (let i = -R; i <= R; i += 2) for (let j = -R; j <= R; j += 2) {
      n++;
      if (ctx.occupied && ctx.occupied(cx + i, cz + j)) { occ++; continue; }
      let g; try { g = API.groundAt(ctx.dim, cx + i, cz + j); } catch { g = undefined; }
      if (g === undefined) { unknown++; continue; }
      gs.push(g);
    }
    if (occ > n * PIT_OCC) continue;
    // 0.0.25d: asleep land is not 'no rock' — the site is asked for and waited for
    if (gs.length < n * 0.5) { unknownSites.push(k); if (ctx.wake) { try { ctx.wake([cx - R, cz - R, cx + R, cz + R]); } catch { /* left */ } } continue; }
    gs.sort((p, q) => p - q);
    const top = gs[gs.length >> 1];
    let vol = 0;
    for (const g of gs) vol += Math.max(0, Math.min(D, g - (top - D)));
    const sc = vol - 2 * k;                                                       // a nearer site wins a tie
    if (!best || sc > best.sc) best = { k, sc, top, vol, unknown, rmax: R };
  }
  if (!best && unknownSites.length) return { wait: true, sites: unknownSites };
  return best;
}
/** a pit worked out at its size grows (a ring, then a step) up to the caps; at the caps the NEXT pit opens on the best
 *  free site around the quarry — at most one change a day; with every site used the quarry is WORKED OUT (no more
 *  stone: the shortage charters a new quarry elsewhere) */
export function pitWorkedOut(b, tierIdx, ctx = null) {
  const pit = b.pit;
  const day = ctx && ctx.day !== undefined ? Math.floor(ctx.day) : null;
  if (day !== null && b.pitOutDay === day) return;
  if (day !== null) b.pitOutDay = day;
  if (pit.r < (pit.rmax || API.QUARRY_R_MAX)) pit.r += 1;
  else if (pit.depth < API.QUARRY_D_MAX) pit.depth += 1;
  else {
    const def = API.BUILDINGS[b.family];
    const { cx, cz } = pitOf(b, def, tierIdx);
    (b.oldPits = b.oldPits || []).push({ cx, cz, r: pit.r, top: b.pitTop, green: 0, site: pit.site });
    const used = new Set((b.oldPits || []).map((o) => o.site).filter((x) => x !== undefined));
    if (pit.site !== undefined) used.add(pit.site);
    const pick = ctx && ctx.dim ? choosePitSite(b, def, ctx, used) : null;
    // 0.0.25d (run 0.0.25c: the quarry 'worked out' at town III with 2 pits — the other sites' land was asleep and read
    // as no rock): a site whose land sleeps is asked for and waited for; worked out only when every site was SEEN spent
    if (pick && pick.wait) { b.oldPits.pop(); b.pitWait = (b.pitWait || 0) + 1; pit.i = 0; return; }
    if (!pick) { b.workedOut = true; b.pitsOpened = b.pitsOpened || 1; pit.i = 0; return; }
    pit.site = pick.k; pit.off = PIT_SITES[pick.k][0] * PIT_STEP(); pit.rmax = pick.rmax || API.QUARRY_R_MAX;
    pit.r = Math.min(pit.rmax, 4 + 2 * tierIdx); pit.depth = Math.min(API.QUARRY_D_MAX, 2 + tierIdx);
    b.pitTop = pick.top;
    b.pitsOpened = (b.pitsOpened || 1) + 1;
  }
  pit.i = 0;
}
export function nextQuarryFace(dim, b, st, near = null, vid = null) {
  if (b.workedOut) return null;
  const def = API.BUILDINGS[b.family];
  const tierIdx = API.tierIdx(st.tier);
  const occupied = API.occupied(st);
  const ctx = { dim, occupied, day: API.load().simDays, wake: () => API.wake(st, b) };
  const po = pitOf(b, def, tierIdx, ctx);
  if (po.wait) return undefined;                                                     // the sites' land sleeps: wake (the caller asks)
  const { pit, cx, cz } = po;
  const r = pit.r, cells = (2 * r + 1) * (2 * r + 1);
  const skip = b.skipFaces || {};
  const nowT = system.currentTick;
  let head = true;
  const found2 = [];                                                         // 0.0.21: candidates; the one the worker can reach wins
  for (let n = 0; n < cells; n++) {
    const k = (pit.i + n) % cells;
    const i = Math.floor(k / (2 * r + 1)) - r, j = (k % (2 * r + 1)) - r;
    const d = Math.max(Math.abs(i), Math.abs(j));
    const steps = Math.min(pit.depth, Math.floor((r - d) / 2) + 1);
    const x = cx + i, z = cz + j;
    let found = null;
    if (steps > 0 && !occupied(x, z)) {
      const g = API.groundAt(dim, x, z);
      if (g === undefined) return undefined;
      if (b.pitTop === undefined) b.pitTop = g;
      const floor = b.pitTop - steps;
      // plants / snow over the column first (no load)
      let logCol = false;
      for (let y = g + 2; y >= g + 1 && !found && !logCol; y--) {
        const up = API.blockAt(dim, x, y, z);
        if (up === null) return undefined;
        // 1.3.228 (B2 / BF10): a LOG over the column (a tree's trunk, a player's cabin wall) is never struck as a "plant" —
        // the column is left standing (the woodcutters fell real trees; a player's logs are never cut)
        if (up && API.TREE_LOG(up.typeId)) { logCol = true; break; }
        if (up && up.typeId !== "minecraft:air" && !API.isGround(up.typeId) && !up.typeId.includes("water")) found = { x, y, z, id: up.typeId, plant: true };
      }
      // (a log column counts as dug: the cursor moves past it, the pit can still grow — the column stays a pillar)
      if (!logCol) for (let y = Math.min(g, b.pitTop); y > floor && !found; y--) {
        const blk = API.blockAt(dim, x, y, z);
        if (blk === null) return undefined;                                      // the chunk sleeps (was the thrown read)
        if (!blk || blk.typeId === "minecraft:air" || blk.typeId.includes("water") || blk.typeId === "minecraft:bedrock") continue;
        found = { x, y, z, id: blk.typeId };
      }
    }
    // review 04:4x #7: a face the hand could not reach (6 walks) rests SKIP_TICKS before it is offered again
    if (found && skip[`${found.x},${found.y},${found.z}`] > nowT) { head = false; found = null; continue; }
    if (found && vid !== null && !CLAIMS.free(siteKey(found), vid, nowT)) { head = false; found = null; continue; }   // 1.3.228 (B2 / BF10): another hand's face
    if (found) { head = false; found2.push(found); if (!near || found2.length >= 24) break; continue; }
    if (head) pit.i = (pit.i + 1) % cells;                                       // a finished column at the head: the cursor moves on
  }
  if (found2.length) {
    if (!near) { if (vid !== null) CLAIMS.take(siteKey(found2[0]), vid, nowT); return found2[0]; }
    // the face nearest the worker, a level change counting triple (he works the bench he stands on first); 1.3.228 (B2 /
    // BF10): among the free faces the longest-untouched column first, then the nearest
    const sc = (f) => Math.hypot(f.x - near.x, f.z - near.z) + 3 * Math.abs(f.y - near.y);
    const byNear = found2.slice().sort((p, q) => sc(p) - sc(q));
    const best = (vid !== null ? CLAIMS.order(byNear, siteKey, vid, nowT)[0] : byNear[0]) || byNear[0];
    if (vid !== null) CLAIMS.take(siteKey(best), vid, nowT);
    // where to stand: a free cell beside the face whose floor is at the face's level or one below
    best.stand = standBeside(dim, best, near);
    return best;
  }
  // worked out at this size: grow (a ring, then a step), or the next pit beside it — and start over (one change a day:
  // a column skipped for an unreachable face is no reason to call the pit spent)
  if (!head) return null;
  pitWorkedOut(b, tierIdx, ctx);
  return null;
}

/** a standable cell (air at feet + head over a solid floor) beside a face, its feet within 0..2 below the face: nearest the worker */
function standBeside(dim, f, near) {
  let best = null, bd = Infinity;
  for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]) {
    for (let fy = f.y - 2; fy <= f.y + 1; fy++) {
      try {
        const feet = API.blockAt(dim, f.x + dx, fy, f.z + dz), head = API.blockAt(dim, f.x + dx, fy + 1, f.z + dz), floor = API.blockAt(dim, f.x + dx, fy - 1, f.z + dz);
        if (!feet || !head || !floor) continue;
        if (feet.typeId !== "minecraft:air" || head.typeId !== "minecraft:air" || floor.typeId === "minecraft:air" || floor.typeId.includes("water")) continue;
        const d = Math.hypot(f.x + dx - near.x, f.z + dz - near.z) + Math.abs(fy - near.y);
        if (d < bd) { bd = d; best = { x: f.x + dx, y: fy, z: f.z + dz }; }
      } catch { /* unloaded */ }
    }
  }
  return best;
}
/** F2 STEWARDSHIP (D-C538): the pit's spent rim RE-GREENS — the spoil the hands set aside (dirt and gravel from the face) is
 *  spread back over the rim's floor as topsoil and grass, a few cells a day; a flower now and then. Returns the cells greened. */
export function regreen(dim, b, st, max = 8) {
  if (!b.pit || !(b.spoil > 0)) return 0;
  // a SPENT pit first: its whole floor returns to meadow, cell by cell (the old quarry becomes a hollow of grass)
  for (const old of b.oldPits || []) {
    if (old.done) continue;
    const side = 2 * old.r + 1, cells = side * side;
    let n = 0;
    const occupied = API.occupied(st);
    while (old.green < cells && n < max && b.spoil > 0) {
      const k = old.green++;
      const x = old.cx + Math.floor(k / side) - old.r, z = old.cz + (k % side) - old.r;
      if (occupied(x, z)) continue;
      const g = API.groundAt(dim, x, z);
      if (g === undefined) { old.green--; return n; }
      try {
        const top = API.blockAt(dim, x, g, z);
        if (top === null) { old.green--; return n; }                       // the chunk sleeps: this cell again tomorrow
        if (!top || top.typeId === "minecraft:grass_block" || top.typeId.includes("water")) continue;
        top.setType("minecraft:grass_block");
        const up = API.blockAt(dim, x, g + 1, z);
        if (up && up.typeId === "minecraft:air" && (x * 7 + z * 13) % 7 === 0) up.setType((x + z) % 3 ? "minecraft:short_grass" : "minecraft:poppy");
        b.spoil--; n++;
      } catch { old.green--; return n; }
    }
    if (old.green >= cells) old.done = true;
    b.greened = (b.greened || 0) + n;
    if (n) return n;
  }
  if (b.pitTop === undefined) return 0;
  const def = API.BUILDINGS[b.family];
  const { cx, cz } = pitOf(b, def, API.tierIdx(st.tier));
  const r = b.pit.r;
  const ring = [];
  for (let i = -r; i <= r; i++) { ring.push([cx + i, cz - r], [cx + i, cz + r]); }
  for (let j = -r + 1; j <= r - 1; j++) { ring.push([cx - r, cz + j], [cx + r, cz + j]); }
  const occupied = API.occupied(st);
  let n = 0;
  b.green = b.green || 0;
  for (let k = 0; k < ring.length && n < max && b.spoil > 0; k++) {
    const [x, z] = ring[(b.green + k) % ring.length];
    if (occupied(x, z)) continue;
    const g = API.groundAt(dim, x, z);
    if (g === undefined) return n;
    if (g > b.pitTop - 1) continue;                                      // not dug yet (or the rim is already grass at the old ground)
    try {
      const top = API.blockAt(dim, x, g, z);
      if (top === null) return n;                                          // the chunk sleeps
      if (!top || top.typeId === "minecraft:grass_block" || top.typeId.includes("water")) continue;
      top.setType("minecraft:grass_block");
      const up = API.blockAt(dim, x, g + 1, z);
      if (up && up.typeId === "minecraft:air" && (x * 7 + z * 13) % 9 === 0) up.setType((x + z) % 2 ? "minecraft:short_grass" : "minecraft:dandelion");
      b.spoil--; n++;
    } catch { return n; }
  }
  b.green = (b.green + n + 1) % Math.max(1, ring.length);
  b.greened = (b.greened || 0) + n;
  return n;
}
// --------------------------------------------------------------------------------------------- the wood stand
const SAPLING = (logId) => {
  for (const w of ["dark_oak", "spruce", "birch", "jungle", "acacia", "cherry", "mangrove", "pale_oak", "oak"]) if (logId.includes(w)) return w === "mangrove" ? "minecraft:mangrove_propagule" : `minecraft:${w}_sapling`;
  return "minecraft:oak_sapling";
};
/** the nearest standing REAL tree's base within the lumberyard's stand: { x, y, z, id } or null. 1.3.228 (B2 / BF10): a
 *  candidate log must be a real tree (the clock's treeOk: no player log, a pw root or natural leaves — cached), and not a
 *  tree another hand has claimed (vid = the asking villager: the tree is claimed for him) */
export function nextTree(dim, b, st, vid = null) {
  // review 04:4x #6: rings outward from the yard at step 1 (the step-2 grid missed every tree on an odd cell — the
  // saplings it planted itself among them), the nearest ring with a tree wins; at most TREE_SCAN cells a call (the scan
  // resumes at its ring next time), and an empty sweep rests the yard TREE_REST ticks
  const def = API.BUILDINGS[b.family];
  const [fx, , fz] = API.footprint(def, b.rot);
  const cx = b.x + (fx >> 1), cz = b.z + (fz >> 1), R = 10 + 6 * API.tierIdx(st.tier);
  const now = system.currentTick;
  if (b.treeRest && now < b.treeRest) return null;
  const occupied = API.occupied(st);
  let scanned = 0, judged = 0;
  for (let r = b.treeRing || 0; r <= R; r++) {
    const cands = [];
    const cells = r === 0 ? [[0, 0]] : [];
    if (r > 0) for (let k = -r; k < r; k++) cells.push([k, -r], [r, k], [-k, r], [-r, -k]);
    for (const [i, j] of cells) {
      const x = cx + i, z = cz + j;
      scanned++;
      if (occupied(x, z)) continue;
      const g = API.groundAt(dim, x, z);
      if (g === undefined) continue;
      for (let y = g + 1; y <= g + 2; y++) {
        const blk = API.blockAt(dim, x, y, z);
        if (blk === null) break;                                              // the chunk sleeps
        if (blk && API.TREE_LOG(blk.typeId) && !blk.typeId.endsWith("_stump")) {
          if (b.skipFaces && b.skipFaces[`${x},${y},${z}`] > now) break;     // review #7: an unreachable tree rests
          cands.push({ x, y, z, id: blk.typeId, dd: i * i + j * j });
          break;
        }
      }
    }
    cands.sort((p, q) => p.dd - q.dd);
    const order = vid !== null ? CLAIMS.order(cands, siteKey, vid, now) : cands;
    for (const c of order) {
      if (API.treeOk) {
        const known = API.treeKnown ? API.treeKnown(c.x, c.y, c.z) : undefined;   // a cached verdict costs no read
        if (known === false) continue;
        if (known === undefined) {
          if (judged >= TREE_JUDGE) { b.treeRing = r; return null; }         // fresh verdicts take reads: resume this ring next beat
          judged++;
          if (!API.treeOk(dim, c.x, c.y, c.z, occupied)) { treeRefused++; continue; }   // a player's logs / a bare pole / asleep
        }
      }
      if (vid !== null && !CLAIMS.take(siteKey(c), vid, now)) continue;
      b.treeRing = Math.max(0, r - 1);
      return { x: c.x, y: c.y, z: c.z, id: c.id };
    }
    if (scanned >= TREE_SCAN && r < R) { b.treeRing = r + 1; return null; }
  }
  b.treeRing = 0; b.treeRest = now + TREE_REST;
  return null;
}
const TREE_JUDGE = 8;                                       // fresh tree verdicts per call (cached ones cost nothing)
let treeRefused = 0;
const TREE_SCAN = 200, TREE_REST = 400, SKIP_TICKS = 6000;    // 0.0.25g: 200 columns a call (the profiler: the work beat cost 11-15 ms a tick at 900)
/** a coppice cell: free grass within 6..16 of the yard on a 3-block grid (room for crowns), not on a plot or a street,
 *  at most COPPICE saplings standing at once; the sapling kind follows the yard's last felled tree (oak by default) */
const COPPICE = 24, PLANT_EVERY = 200;
function plantSpot(dim, b, st) {
  const now = system.currentTick;
  if (b.plantAt && now - b.plantAt < PLANT_EVERY) return null;                    // 0.0.25g: one search per yard every 10 s
  b.plantAt = now;
  const def = API.BUILDINGS[b.family];
  const [fx, , fz] = API.footprint(def, b.rot);
  const cx = b.x + (fx >> 1), cz = b.z + (fz >> 1);
  const occupied = API.occupied(st);
  let standing = 0;
  const cand = [];
  for (let dx = -16; dx <= 16; dx += 3) for (let dz = -16; dz <= 16; dz += 3) {
    const d = Math.max(Math.abs(dx), Math.abs(dz));
    if (d < 6) continue;
    const x = cx + dx, z = cz + dz;
    if (occupied(x, z)) continue;
    const g = API.groundAt(dim, x, z);
    if (g === undefined) continue;
    const up = API.blockAt(dim, x, g + 1, z), gr = API.blockAt(dim, x, g, z);
    if (!up || !gr) continue;
    if (up.typeId.includes("sapling")) { standing++; continue; }
    if (up.typeId !== "minecraft:air" && !up.typeId.includes("short_grass") && !up.typeId.includes("fern")) continue;
    if (!/grass_block|dirt|podzol/.test(gr.typeId)) continue;
    cand.push({ x, y: g + 1, z, d: dx * dx + dz * dz });
  }
  if (standing >= COPPICE || !cand.length) return null;
  cand.sort((p, q) => p.d - q.d);
  const c = cand[0];
  return { x: c.x, y: c.y, z: c.z, sapling: SAPLING(b.lastLog || "oak"), hits: 0 };
}
/** the logs of one tree (counted, not cut): the chop takes one beat per log, then the tree is felled at once */
function treeLogs(dim, t) {
  let n = 0;
  for (let y = t.y; y < t.y + 32; y++) { const blk = API.blockAt(dim, t.x, y, t.z); if (!blk || !API.TREE_LOG(blk.typeId)) break; n++; }   // 1.3.228: guarded
  return Math.max(1, n);
}

// --------------------------------------------------------------------------------------------- the beat
function onDuty() { try { const t = world.getTimeOfDay(); return t >= WORK[0] && t < WORK[1]; } catch { return false; } }
/** the hands of a workshop: its keeper + any villager whose census person works there */
function handsOf(s, st, b) {
  const out = [];
  if (b.keeper) { try { const v = world.getEntity(b.keeper); if (v) out.push(v); } catch { /* gone */ } }
  // 0.0.23: the census workers of this workshop (their villagers) work beside the keeper
  if (API.hands) for (const v of API.hands(st, b)) if (!out.some((o) => o.id === v.id)) out.push(v);
  return out;
}
function speak(v, sound) { try { v.dimension.playSound(sound, v.location, { volume: 0.8 }); } catch { /* left */ } }

const FACE_BUDGET_MS = 40;
let faceMs = 0, faceDeferred = 0;
HB.register("work", { fn: () => {                                          // 1.3.228 (B1 / BF1): heartbeat slots 3, 13 (every BEAT = 10)
  if (!API) return;
  faceMs = 0;
  const tw0 = Date.now();
  try { workBeat(); } finally { const ms = Date.now() - tw0; if (ms > 150) console.warn(`[CIV-WORK] slow beat: ${ms} ms (face searches ${faceMs} ms, deferred so far ${faceDeferred})`); }
} });
function workBeat() {
  const s = API.load();
  const duty = onDuty();
  const now = system.currentTick;
  if (now % 200 < BEAT) {
    for (const vid of [...workers.keys()]) { let v; try { v = world.getEntity(vid); } catch { v = undefined; } if (!v || !v.isValid) { workers.delete(vid); CLAIMS.releaseAll(vid, now); } }   // 1.3.228: a gone body's claims go
    CLAIMS.prune(now);
    // review 04:4x #9: a civ:working tag nobody works under (a reload empties the map; a closed shop's hand) — the
    // schedule skips tagged villagers, so a stale tag froze them where they stood
    for (const st of s.settlements) {
      // 1.3.228 (B1 / BF1): the shared bodies cache (was its own query per settlement)
      // 1.3.228 (B4 / BF5): each hand keeps his own shift — a tag stays while his worker record is on duty
      for (const v of HB.bodiesOf(st)) if (v.hasTag("civ:working") && (!workers.has(v.id) || workers.get(v.id).state === "off" || (!API.onShift && !duty))) { try { v.removeTag("civ:working"); } catch { /* left */ } }
    }
  }
  for (const st of s.settlements) {
    if (!st.kit || st.phase !== "built") continue;
    let dim;
    try { dim = world.getDimension(st.dim); } catch { continue; }
    const wet = API.wet ? API.wet(st) : false;                                // 1.3.228 (B4): rain (pw_weather), once a town a beat
    for (const b of API.plotsOf(st)) {
      const kind = API.short(b);
      if ((kind !== "quarry" && kind !== "lumberyard") || b.stage < 4 || b.closed) continue;
      const store = storeOf(b);
      if (!store) continue;
      for (const v of handsOf(s, st, b)) {
        let w = workers.get(v.id);
        // 1.3.228 (B4 / BF5): each hand's OWN shift (template, offset, days off, the walk home — PEOPLE.shiftAt via the clock)
        const onDutyNow = API.onShift ? API.onShift(v, st) : duty;
        if (!onDutyNow) {                                                    // the day is over: whatever is carried goes in tomorrow
          if (w && w.state !== "off") { v.removeTag("civ:working"); if (WALK.walking(v)) WALK.cancel(v); w.state = "off"; if (w.face) { w.face.done = true; } CLAIMS.releaseAll(v.id, now); }   // 1.3.228: off duty, the claim goes
          continue;
        }
        if (!w) { w = { shop: b.id, st: st.id, state: "idle", load: {}, carried: 0, next: 0 }; workers.set(v.id, w); }
        if (!v.hasTag("civ:working")) v.addTag("civ:working");
        // 1.3.228 (B4, his rain ruling): in rain the hand SHELTERS inside his workshop (its door cell) — the day keeps half
        // his output (the clock's produceDaily: PEOPLE.rainOutput); his claim and face go, the barrow stays loaded
        if (wet) {
          if (w.state !== "shelter") { CLAIMS.releaseAll(v.id, now); if (w.face) w.face.done = true; if (WALK.walking(v)) WALK.cancel(v); w.state = "shelter"; }
          const sh = API.shelterOf ? API.shelterOf(b) : null;
          if (sh) {
            const d = Math.hypot(v.location.x - sh.x, v.location.z - sh.z);
            if (d > 2.6) { if (!WALK.walking(v)) WALK.send(v, st, sh); }
            else if (WALK.walking(v)) WALK.cancel(v);
          }
          continue;
        }
        if (w.state === "shelter" || w.state === "off") w.state = "idle";
        try { v.removeEffect("slowness"); } catch { /* left */ }
        const at = (p, h = REACH_H, vv = REACH_V) => Math.hypot(v.location.x - (p.x + 0.5), v.location.z - (p.z + 0.5)) <= h && Math.abs(v.location.y - p.y) <= vv;
        if (w.state === "idle" || w.state === "toFace") {
          if (w.carried >= LOAD_MAX) { w.state = "toStore"; WALK.send(v, st, { x: store.x + 0.5, y: store.y, z: store.z + 0.5 }); continue; }
          if (!w.face || w.face.done) {
            // 1.3.227: the face / tree searches share FACE_BUDGET_MS a beat (profiled: work beats of 100..345 ms at city II)
            if (faceMs >= FACE_BUDGET_MS) { faceDeferred++; continue; }
            const tf0 = Date.now();
            try {
            CLAIMS.releaseAll(v.id, now);                                     // 1.3.228 (B2 / BF10): one claim per hand
            w.face = kind === "quarry" ? nextQuarryFace(dim, b, st, { x: v.location.x, y: Math.floor(v.location.y), z: v.location.z }, v.id) : nextTree(dim, b, st, v.id);
            w.noFace = w.face === null;                                         // BF3: NO_FACE while nothing is found
            if (w.face === undefined) { API.wake(st, b); continue; }               // the pit's ground sleeps: ask for it
            // 0.0.25d (run 0.0.25c: two lumberyards, one tree felled — the land near them was bare): with no tree in reach the
            // woodcutter PLANTS a coppice — saplings in rows on free grass near the yard (the real practice), to fell later
            if (!w.face && kind === "lumberyard" && b.treeRest && now < b.treeRest) w.face = plantSpot(dim, b, st);
            if (!w.face) { if (w.carried > 0) { w.state = "toStore"; WALK.send(v, st, { x: store.x + 0.5, y: store.y, z: store.z + 0.5 }); } continue; }
            if (kind === "lumberyard" && !w.face.sapling) w.face.logs = treeLogs(dim, w.face);
            w.face.hits = 0; w.walks = 0;
            } finally { faceMs += Date.now() - tf0; }
          }
          if (!w.face.sapling) CLAIMS.renew(siteKey(w.face), v.id, now);
          if (at(w.face)) { w.state = "work"; w.next = now + Math.round((kind === "quarry" ? MINE_TICKS : CHOP_TICKS) / (API.skill ? API.skill(v, st, kind) : 1)); if (WALK.walking(v)) WALK.cancel(v); }
          else if (!WALK.walking(v)) {
            w.state = "toFace"; const sp = w.face.stand || w.face; WALK.send(v, st, { x: sp.x + 0.5, y: sp.y, z: sp.z + 0.5 }); w.walks = (w.walks || 0) + 1;
            if (w.walks > 6) {                                                // review 04:4x #7: unreachable — rest it, take another
              w.face.done = true; w.walks = 0;
              const sk = (b.skipFaces = b.skipFaces || {});
              sk[`${w.face.x},${w.face.y},${w.face.z}`] = now + SKIP_TICKS;
              for (const k of Object.keys(sk)) if (sk[k] <= now) delete sk[k];
              b.skipped = (b.skipped || 0) + 1;
              CLAIMS.release(siteKey(w.face), v.id, now);
            }
          }
          continue;
        }
        if (w.state === "work") {
          if (w.face && !w.face.sapling) CLAIMS.renew(siteKey(w.face), v.id, now);
          if (now < w.next) continue;
          if (!at(w.face, REACH_H + 1, REACH_V + 1)) { w.state = "idle"; continue; }
          if (kind === "quarry") {
            const blk = API.blockAt(dim, w.face.x, w.face.y, w.face.z);       // 1.3.228: guarded
            if (blk && blk.typeId !== "minecraft:air") {
              const [item, cls] = w.face.plant ? [null, "plant"] : STONE_DROP(blk.typeId);
              speak(v, w.face.plant ? "dig.grass" : "dig.stone");
              try { blk.setType("minecraft:air"); } catch { /* left */ }
              if (item) { w.load[item] = (w.load[item] || 0) + 1; w.carried++; }
              else if (cls === "spoil") b.spoil = (b.spoil || 0) + 1;
              b.dug = (b.dug || 0) + 1;
              if (API.act) API.act(v, st);                                    // 1.3.228 (B3 / PE7): a real act (skill XP)
            }
            w.face.done = true;
            CLAIMS.release(siteKey(w.face), v.id, now);                      // 1.3.228: dug
            w.state = "idle";
          } else if (w.face.sapling) {
            try {
              const cell = API.blockAt(dim, w.face.x, w.face.y, w.face.z), ground = API.blockAt(dim, w.face.x, w.face.y - 1, w.face.z);
              if (cell && ground && cell.typeId === "minecraft:air" && /grass_block|dirt|podzol/.test(ground.typeId)) { cell.setType(w.face.sapling); b.planted = (b.planted || 0) + 1; speak(v, "dig.grass"); }
            } catch { /* left */ }
            w.face.done = true; w.state = "idle";
          } else {
            w.face.hits++;
            if (API.act) API.act(v, st);                                      // 1.3.228 (B3 / PE7): a chop is a real act
            speak(v, "dig.wood");
            if (w.face.hits >= w.face.logs) {
              const n = API.fellTree(dim, w.face.x, w.face.y, w.face.z, API.occupied(st));
              if (n) {
                const logItem = w.face.id.startsWith("minecraft:") && w.face.id.endsWith("_log") ? w.face.id : "minecraft:oak_log";
                w.load[logItem] = (w.load[logItem] || 0) + n; w.carried += n;
                b.felled = (b.felled || 0) + 1; b.lastLog = w.face.id;
                // F2 stewardship: a sapling beside the stump (the first free grass cell around it)
                for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1], [2, 0], [0, 2]]) {
                  try {
                    const ground = API.blockAt(dim, w.face.x + dx, w.face.y - 1, w.face.z + dz), cell = API.blockAt(dim, w.face.x + dx, w.face.y, w.face.z + dz);
                    if (ground && cell && cell.typeId === "minecraft:air" && (ground.typeId === "minecraft:grass_block" || ground.typeId === "minecraft:dirt" || ground.typeId === "minecraft:podzol")) { cell.setType(SAPLING(w.face.id)); b.replanted = (b.replanted || 0) + 1; break; }
                  } catch { /* left */ }
                }
              }
              w.face.done = true;
              CLAIMS.release(siteKey(w.face), v.id, now);                    // 1.3.228: felled (or refused at the fell: a player's log)
              if (!n) treeRefused++;
              w.state = w.carried >= LOAD_MAX ? "toStore" : "idle";
              if (w.state === "toStore") WALK.send(v, st, { x: store.x + 0.5, y: store.y, z: store.z + 0.5 });
            } else w.next = now + Math.round(CHOP_TICKS / (API.skill ? API.skill(v, st, kind) : 1));
            if (w.face.done) continue;
            continue;
          }
          continue;
        }
        if (w.state === "toStore") {
          if (at(store, 2.6, 3)) {
            // DEPOSIT: into the chest (what does not fit stays in the barrow), the town's stock mirrors it
            let put = 0;
            try {
              const inv = API.blockAt(dim, store.x, store.y, store.z)?.getComponent("minecraft:inventory");   // 1.3.228: guarded
              const con = inv && inv.container;
              for (const [item, n] of Object.entries(w.load)) {
                let left = n;
                while (left > 0 && con) {
                  const k = Math.min(64, left);
                  const rest = con.addItem(new ItemStack(item, k));
                  const moved = k - (rest ? rest.amount : 0);
                  left -= moved; put += moved;
                  if (moved < k) break;                                       // the chest is full
                }
                if (left > 0) w.load[item] = left; else delete w.load[item];
              }
            } catch (e) { console.warn(`[CIV-WORK] deposit at #${b.id}: ${e}`); }
            w.carried = Object.values(w.load).reduce((a, n) => a + n, 0);
            w.full = w.carried > 0;                                           // BF3: STOCK_FULL — the chest took not all of it
            if (put) API.deposited(st, b, put, kind);
            if (WALK.walking(v)) WALK.cancel(v);
            w.state = "idle";
          } else if (!WALK.walking(v)) WALK.send(v, st, { x: store.x + 0.5, y: store.y, z: store.z + 0.5 });
        }
      }
    }
  }
}

export function stats() {
  const by = {};
  const sample = [];
  for (const [vid, w] of workers) {
    by[w.state] = (by[w.state] || 0) + 1;
    if (sample.length >= 6) continue;
    // 0.0.22 (run 0.0.21: 2 hands, nothing mined, no way to see why): each hand's state, where it stands, its target
    let v; try { v = world.getEntity(vid); } catch { v = undefined; }
    const loc = v ? v.location : null, f = w.face;
    sample.push([v ? v.nameTag : "?", w.shop, w.state, loc ? [Math.floor(loc.x), Math.floor(loc.y), Math.floor(loc.z)] : null,
                 f ? [f.x, f.y, f.z, f.stand ? [f.stand.x, f.stand.y, f.stand.z] : null] : null, w.carried, w.walks || 0, WALK.walking(v || { id: vid }) ? 1 : 0]);
  }
  return { workers: workers.size, ...by, sample, claims: CLAIMS.stats(), treeRefused };
}
