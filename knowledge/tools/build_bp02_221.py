#!/usr/bin/env python3
"""build_bp02_221.py — BP-02 1.3.221 from the frozen 1.3.220 (never rebuilt): THE CITY PALACE (D-C570; his 21:07 rulings).
  1. The four palace pieces (tools/palacegen.py -> _staging/civ/palace): structures/pw/mvv_palace_<q>_a_r1 + their five
     stages; CIV_BUILDINGS entries (dir limited to our pw:n/e/s/w furniture — the engine rotates the vanilla states itself).
  2. Two walk-through blocks of the hidden world: pw:jib_panel, pw:secret_painting (tools/build_palace_blocks.py; the RP side
     goes into RP-01 1.3.123 by the same tool).
  3. pw_civ_clock.js: at CITY II the palace block is found (128 x 128, free of plots / streets / the square, the flattest site
     110..320 from the square, the gate toward the square) and the four pieces laid as one rotated group; the pieces climb
     their stages in LOCKSTEP as the crown's works (PALACE_STAGE_DAYS, wages from the treasury, never waiting for stock);
     land prep (clear + terrace) per piece; a daily retry while the site's chunks are unloaded.
Usage: python3 tools/build_bp02_221.py   (bp02-221 must not exist)"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-220", B / "bp02-221"
STG = Path("/home/claude/_staging/civ/palace")
LOG = []


def rep(text, old, new, what, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"PATCH '{what}': expected {count} match(es), found {n}")
    LOG.append(what)
    return text.replace(old, new)


def read(rel):
    return (DST / rel).read_text(encoding="utf-8")


def write(rel, text):
    (DST / rel).write_text(text, encoding="utf-8")


DIRK_OURS = {"pw:n", "pw:e", "pw:s", "pw:w"}


def palace_entries():
    sys.path.insert(0, "/home/claude/tools")
    import civ_village_data as V
    out = {}
    for p in sorted((STG / "manifests").glob("*.json")):
        m = json.loads(p.read_text())
        stem = m["name"].split(":", 1)[1]
        # the bill of materials from the stage files (the same class rule as every other building)
        bom = []
        for k in range(5):
            f = STG / "stages" / f"{stem}_s{k}.mcstructure"
            st = V.M.Structure.from_bytes(f.read_bytes())
            sx, sy, sz = st.size
            cnt = {}
            for x in range(sx):
                for y in range(sy):
                    for z in range(sz):
                        e = st.get(x, y, z)
                        if not isinstance(e, tuple):
                            continue
                        c = V.mat_class(e[0])
                        if c:
                            cnt[c] = cnt.get(c, 0) + 1
            bom.append(cnt)
        out[m["name"]] = {
            "stem": stem, "size": m["size"], "datum_y": m["datum_y"], "stages": 5,
            "lids": [],
            "door": [0, 0, m["size"][2] // 2],
            "work": sum(1 for e in m["entities"] if e.get("fam") == "station" and e.get("kind") not in ("door", "bed", "seat", "store")),
            "dir": [[x, y, z, n, {k: v for k, v in s.items() if k in DIRK_OURS}] for x, y, z, n, s in m["blocks"] if set(s) & DIRK_OURS],
            "bom": bom,
            "chests": sorted([[x, y, z, n] for x, y, z, n, s in m["blocks"] if n in ("minecraft:chest", "minecraft:barrel")],
                             key=lambda c: (abs(c[1] - m["datum_y"]), c[1], c[0], c[2])),
        }
    return out


CLOCK_PALACE = r'''
// ------------------------------------------------------------------------------------------------ THE CITY PALACE (1.3.221, D-C570)
// At CITY II the Seat of Government is laid on a palace block: four 64 x 64 pieces (sw se nw ne of the 128 x 128 model,
// tools/palacegen.py), placed as ONE rotated group (each piece rotated, the 2 x 2 positions permuted) with the gate toward
// the square; built in lockstep as the crown's works (wages from the treasury, materials imported — never waiting for stock).
const PALACE_PIECES = ["sw", "se", "nw", "ne"];
const PALACE_GRID = { sw: [0, 0], se: [0, 1], nw: [1, 0], ne: [1, 1] };          // (i = depth from the gate side, j = frontage)
const PALACE_STAGE_DAYS = [6, 8, 8, 6];                                            // village days at stage k before k + 1
const PALACE_TIER = "city2";
const palaceFamily = (q) => `pw:mvv_palace_${q}_a_r1`;
function palaceGridRot(i, j, r) { return r === 1 ? [1 - j, i] : r === 2 ? [1 - i, 1 - j] : r === 3 ? [j, 1 - i] : [i, j]; }
/** the palace block: a 128 x 128 site (+ 2 cells of margin) 110..320 from the square, free of plots / streets / the square /
 *  park, the flattest candidate (ground sampled every 16 cells), its gate side toward the square. A SURVEY over days
 *  (st.palaceSurvey): each day up to 6 loaded candidates are measured; the first sleeping one is kept awake by the
 *  crown's surveyors (a 160 x 160 ticking area, held busy until the palace is laid) so tomorrow can read it. Accepted:
 *  relief <= 14 at once; <= 24 once 8 candidates were measured; <= 40 after 30 days; the best of all once every
 *  candidate has been tried. */
function palaceSite(s, st, dim) {
  const sq = st.square;
  if (!sq) return null;
  const cx = sq.x + 6, cz = sq.z + 6;
  // occupancy at CHUNK resolution, built once per survey day (run 2 of the gate: a per-candidate walk over ~20k street
  // cell keys took > 10 s in one tick — the watchdog killed the pack); a candidate is free when none of the chunks its
  // box touches holds a street cell or a plot box (conservative by up to 15 blocks, which the 2-cell margin absorbs)
  const occ = new Set();
  for (const k of streetHeights(s).keys()) { const c = k.indexOf(","); occ.add(`${Math.floor(+k.slice(0, c) / 16)},${Math.floor(+k.slice(c + 1) / 16)}`); }
  for (const [a, b2, c, d] of plotBoxes(s, 2)) for (let i = Math.floor(a / 16); i <= Math.floor(b2 / 16); i++) for (let j = Math.floor(c / 16); j <= Math.floor(d / 16); j++) occ.add(`${i},${j}`);
  const free = (x0, z0) => {
    const x1 = x0 + 131, z1 = z0 + 131;
    for (let i = Math.floor(x0 / 16); i <= Math.floor(x1 / 16); i++) for (let j = Math.floor(z0 / 16); j <= Math.floor(z1 / 16); j++) if (occ.has(`${i},${j}`)) return false;
    return true;
  };
  const sv = st.palaceSurvey || (st.palaceSurvey = { tried: {}, best: null, days: 0, loaded: 0 });
  sv.days++;
  let woke = null, evaluated = 0, open = 0;
  for (let R = 110; R <= 320 && evaluated < 6; R += 24) {
    for (let a = 0; a < 16 && evaluated < 6; a++) {
      const ang = a * Math.PI / 8;
      const x0 = Math.round(cx + Math.cos(ang) * R) - 64, z0 = Math.round(cz + Math.sin(ang) * R) - 64;
      const key = `${x0},${z0}`;
      if (sv.tried[key]) continue;
      if (!free(x0 - 2, z0 - 2)) { sv.tried[key] = 0; continue; }
      const hs = [];
      let miss = false, wet = 0;
      for (let i = 0; i < 128 && !miss; i += 16) for (let j = 0; j < 128; j += 16) {
        // gallery gate run 2: a lake at y 108 read as flat ground (groundAt walks down to the bed) and the palace was laid in it;
        // the topmost block decides wetness at ANY height
        let topId, aboveId;
        try {
          const top = dim.getTopmostBlock({ x: x0 + i, z: z0 + j });             // run 4: this skips liquids (a 5-deep lake read as dry) —
          topId = top ? top.typeId : undefined;                                  // so the block ABOVE the topmost solid is read too
          const above = top ? dim.getBlock({ x: x0 + i, y: top.location.y + 1, z: z0 + j }) : undefined;
          aboveId = above ? above.typeId : "minecraft:air";
        } catch { topId = undefined; }                                            // reading a block of an unloaded chunk throws (run 3)
        if (!topId) { miss = true; break; }
        const isWet = (id) => id === "minecraft:water" || id === "minecraft:flowing_water" || id.includes("ice") || id === "minecraft:lava";
        if (isWet(topId) || isWet(aboveId)) wet++;
        const g = groundAt(dim, x0 + i, z0 + j);
        if (g === undefined) { miss = true; break; }
        hs.push(g);
      }
      if (miss) {
        open++;
        if (!woke) {
          woke = [x0, z0, R];
          try { const nm = ensureTicking(s, st, [x0 - 8, z0 - 8, x0 + 135, z0 + 135], `palace site survey (${R} from the square)`); if (nm) sv.area = nm; }   // run 9: the held area must cover the OUTSIDE samples too (8 cells out), or the site stays open for ever
          catch (e) { console.warn(`[CIV-CLOCK] palace survey: ${e}`); }
        }
        continue;                                                                    // a later candidate may be loaded already
      }
      evaluated++; sv.loaded++;
      const relief = Math.max(...hs) - Math.min(...hs);
      const H = median(hs) + 1;
      // gate runs 2–6: the box read dry and flat, but a lake stood just OUTSIDE it above the floor level; the land job's cut let
      // it pour in. 36 samples 8 cells outside the box (9 a side; run 9: 24 cells out lay beyond any area the surveyors can
      // hold — 10 x 10 chunks — and such sites were never measured): water (or ice) standing at or above feet -1 rejects
      let outsideWet = 0, bowl = 0;
      for (let k = 0; k < 36 && !miss; k++) {
        const t = k % 9, side = Math.floor(k / 9) % 4, far = 8;
        const sx2 = side === 0 ? x0 - far : side === 1 ? x0 + 127 + far : x0 + t * 16, sz2 = side === 2 ? z0 - far : side === 3 ? z0 + 127 + far : z0 + t * 16;
        try {
          const top = dim.getTopmostBlock({ x: sx2, z: sz2 });
          if (!top) { miss = true; break; }
          let wetHere = top.typeId.includes("ice") ? top.location.y : -999;
          for (let yy = top.location.y + 1; yy < top.location.y + 64; yy++) { const a = dim.getBlock({ x: sx2, y: yy, z: sz2 }); if (a && (a.typeId === "minecraft:water" || a.typeId === "minecraft:flowing_water")) wetHere = yy; else break; }
          if (wetHere >= H - 1) outsideWet++;
          if (top.location.y >= H + 16) bowl++;                                             // run 7: a mountain beside the block poured its lake over the walls
        } catch { miss = true; break; }
      }
      // inside, denser: any standing water above the floor level inside the box rejects (the first survey's 64 points missed a corner pond)
      let wetIn = 0;
      for (let i = 8; i < 128 && !miss; i += 16) for (let j = 8; j < 128; j += 16) {
        try {
          const top = dim.getTopmostBlock({ x: x0 + i, z: z0 + j });
          if (!top) { miss = true; break; }
          const a = dim.getBlock({ x: x0 + i, y: top.location.y + 1, z: z0 + j });
          if ((a && a.typeId === "minecraft:water" && a.location.y >= H - 1) || (top.typeId.includes("ice") && top.location.y >= H - 1)) wetIn++;
        } catch { miss = true; break; }
      }
      if (miss) { open++; continue; }
      const score = relief + (wet + wetIn) * 6 + outsideWet * 6 + bowl * 3 + R / 40;
      sv.tried[key] = relief + 1;
      if (wet < 3 && wetIn === 0 && outsideWet === 0 && bowl === 0 && (!sv.best || score < sv.best.score)) sv.best = { x0, z0, score, relief, wet, R, H };
      if (relief <= 40 && (!sv.anyBest || score < sv.anyBest.score)) sv.anyBest = { x0, z0, score, relief, wet, wetIn, outsideWet, bowl, R, H };   // the fallback (60 days): the least wet, the least bowl-like
    }
  }
  const exhausted = !woke && evaluated === 0;
  let b = sv.best;
  if (!b && sv.anyBest && (sv.days >= 60 || exhausted)) b = sv.anyBest;             // no dry site in 60 days: the walls will hold the water
  const accept = b && (b.relief <= 14 || (sv.loaded >= 8 && b.relief <= 24) || (sv.days >= 30 && b.relief <= 40) || exhausted);
  if (!accept) {
    st.palaceSearch = { days: sv.days, loaded: sv.loaded, open, best: b ? [b.x0, b.z0, b.relief, b.R] : null, waiting: woke, day: s.simDays };
    if (exhausted && !b && sv.days % 30 === 0) { sv.tried = {}; st.log.push(`day ${s.simDays.toFixed(0)}: the crown's surveyors found no ground for a palace yet (${sv.loaded} sites measured); they start again`); }
    return null;
  }
  const dx = cx - (b.x0 + 64), dz = cz - (b.z0 + 64);
  b.rot = Math.abs(dx) >= Math.abs(dz) ? (dx < 0 ? 0 : 2) : (dz < 0 ? 1 : 3);       // gate west 0 / north 1 / east 2 / south 3
  b.days = sv.days; b.measured = sv.loaded;
  return b;
}
function placePalace(s, st, dim) {
  if (st.palace) return false;
  const site = palaceSite(s, st, dim);
  if (!site) { st.palaceTries = (st.palaceTries || 0) + 1; return false; }
  const group = s.nextId++;
  const ids = [];
  for (const q of PALACE_PIECES) {
    const [i, j] = PALACE_GRID[q];
    const [gi, gj] = palaceGridRot(i, j, site.rot);
    const b = { id: s.nextId++, family: palaceFamily(q), dim: st.dim, x: site.x0 + gi * 64, y: site.H - BUILDINGS[palaceFamily(q)].datum_y, z: site.z0 + gj * 64,
                rot: site.rot, settled: true, stage: 0, progress: 0, delay: 0, pending: [0], settlement: st.id, planned: true, civic: "palace", palace: { group, q } };
    s.buildings.push(b);
    ids.push(b.id);
  }
  st.palace = { group, x0: site.x0, z0: site.z0, rot: site.rot, H: site.H, ids, day: s.simDays, survey: [site.days, site.measured] };
  delete st.palacePending; delete st.palaceSurvey; delete st.palaceSearch;
  st.log.push(`day ${s.simDays.toFixed(0)}: the SEAT OF GOVERNMENT is laid out — the palace block (128 x 128) at ${site.x0} ${site.z0}, gate ${["west", "north", "east", "south"][site.rot]}, ${site.R} from the square (relief ${site.relief}); the crown builds it`);
  return true;
}
/** the palace block's land, a generator for system.runJob (the plot stage of a piece is LIGHT — only the ground work at
 *  feet >= -2 — because placing the full 196k-cell box took up to 8 s in one tick, two seconds under the watchdog):
 *  1. NATURAL blocks inside the piece's box and 24 rows above it are cleared (trees, plants, hills, water, snow) — never
 *     a block of ours, so a stage placed while the job still runs is safe;
 *  2. hollows under the floor slab (feet -15 .. -3) are filled with dirt where the terrain is air, water or leaves;
 *  3. the one-cell margin ring is filled from the ground up to the lawn (feet -1).
 *  ~300 block reads per tick; a piece takes ~15 s of real time, well inside the six days to the frame stage */
const NATURAL = ["minecraft:dirt", "minecraft:grass_block", "minecraft:stone", "minecraft:deepslate", "minecraft:gravel", "minecraft:sand", "minecraft:red_sand",
  "minecraft:coarse_dirt", "minecraft:podzol", "minecraft:mycelium", "minecraft:clay", "minecraft:tuff", "minecraft:calcite", "minecraft:andesite", "minecraft:diorite",
  "minecraft:granite", "minecraft:water", "minecraft:flowing_water", "minecraft:snow", "minecraft:snow_layer", "minecraft:ice", "minecraft:packed_ice", "minecraft:mud",
  "minecraft:moss_block", "minecraft:rooted_dirt", "minecraft:dirt_with_roots", "minecraft:mossy_cobblestone", "minecraft:bedrock"];
const NATURAL_WORDS = ["leaves", "_log", "_wood", "sapling", "mushroom", "vine", "bee_nest", "cocoa", "fern", "grass", "bush", "flower", "lily", "kelp", "seagrass",
  "coral", "cactus", "bamboo", "azalea", "dripleaf", "sweet_berry", "spore", "sugar_cane", "pumpkin", "melon", "dead_bush", "tallgrass", "double_plant", "mangrove_roots"];
function isNatural(id) {
  if (NATURAL.includes(id) || id.endsWith("_ore") || isTreeLeafId(id)) return true;
  if (id.startsWith("pw:")) return ["leaves", "root", "ground", "log", "trunk", "vine", "moss", "fern", "grass", "bush", "mushroom", "litter"].some((q) => id.includes(q));   // our tree / plant blocks only — never a roof, a flue, a furnishing
  return NATURAL_WORDS.some((q) => id.includes(q));
}
/** the RETAINING WALLS on the palace block's outer perimeter (never between two pieces): where the land or standing water
 *  just outside stands at or above the floor, the piece's edge column is clad in stone from feet -1 up to that height.
 *  Run 11 (10-05): an edge whose OUTSIDE column lay in a sleeping chunk got no wall at all (the read came back empty) and the
 *  lake poured in at 26k cells a day — so the height is the greater of the outside column and the piece's own edge column
 *  (always loaded while the piece is built), each climbed from the topmost solid through any water to the SURFACE; and the
 *  walls are checked again on every pump pass (a chunk asleep at the land job wakes later). */
function* palaceWallJob(dim, b, def) {
  const [fx, sy, fz] = footprint(def, b.rot);
  const slab = b.y + def.datum_y - 1;
  let ops = 0, walled = 0;
  const tick = function* () { if (++ops % 300 === 0) yield; };
  const stp = load().settlements.find((x) => x.palace && x.palace.group === b.palace.group);
  const box = stp ? [stp.palace.x0, stp.palace.z0, stp.palace.x0 + 127, stp.palace.z0 + 127] : null;
  if (!box) return 0;
  const WATERY = (a) => a.typeId === "minecraft:water" || a.typeId === "minecraft:flowing_water" || a.typeId.includes("ice") || a.isLiquid || a.isWaterlogged
    || /kelp|seagrass|coral|sea_pickle|bubble_column|lily_pad/.test(a.typeId);
  const surfaceAt = (x, z) => {                                              // the WATER surface + 1 in column x z (his 12:12 rule), or the ground; undefined when asleep
    const t = dim.getTopmostBlock({ x, z });
    if (!t) return undefined;
    let top = t.location.y, wet = WATERY(t);
    for (let yy = top + 1; yy < top + 64; yy++) { const a = dim.getBlock({ x, y: yy, z }); if (a && WATERY(a)) { top = yy; wet = true; } else break; }   // run 16: through water plants too
    return wet ? top + 1 : top;                                                // run 17: +1 only over WATER — a wall read as its own top grew one block every pass
  };
  const edge = [];
  for (let i = 0; i < fx; i++) { if (b.z === box[1]) edge.push([b.x + i, b.z, 0, -1]); if (b.z + fz - 1 === box[3]) edge.push([b.x + i, b.z + fz - 1, 0, 1]); }
  for (let j = 0; j < fz; j++) { if (b.x === box[0]) edge.push([b.x, b.z + j, -1, 0]); if (b.x + fx - 1 === box[2]) edge.push([b.x + fx - 1, b.z + j, 1, 0]); }
  for (const [x, z, dx, dz] of edge) {
    let top = -999;
    // run 15: the margin ring is filled to the slab and reads DRY — the lake begins one cell further out and poured over the
    // margin at its own level; the wall takes the highest surface found 1..8 cells out (loaded columns only)
    for (const far of [1, 2, 3, 5, 8]) { try { const o = surfaceAt(x + dx * far, z + dz * far); if (o !== undefined) top = Math.max(top, o); } catch { /* asleep: the next column decides */ } }
    // gate 223-1 (15:4x): the INSIDE column's topmost block is the palace itself (walls, eaves, roofs) once the stages stand —
    // reading it raised a stone curtain to roof height round the block (824 + 622 + 762 blocks). Only the OUTSIDE columns
    // decide; while they sleep the edge waits for a later pump pass (the pumps hold the block's area).
    // run 16 (his 12:12 rule): the wall stands ONE BLOCK HIGHER than the water — the east wall reached y 119 under a lake
    // whose surface cell was 120, and the lake walked over it onto the cornice
    for (let y = slab; y <= Math.min(top, b.y + sy - 1); y++) {
      // run 14: the wall in the piece's own edge column is opened again by the stages (the front doors, the carriage arch) —
      // the lake walked in through the doorways. The wall now stands in the MARGIN column outside the piece as well, which
      // no stage ever touches; the inside course stays as the fallback while the outside chunk sleeps
      for (const [wx, wz] of [[x + dx, z + dz], [x, z]]) {
        try { const blk = dim.getBlock({ x: wx, y, z: wz }); if (blk && (blk.typeId === "minecraft:air" || isNatural(blk.typeId))) { blk.setType("minecraft:stone_bricks"); walled++; } } catch { /* unloaded */ }
      }
      yield* tick();
    }
    yield* tick();
  }
  return walled;
}
/** run 12 (10-05): a lake is INFINITE WATER — two source blocks beside a drained cell make a new source, so a cell-by-cell
 *  drain (300 cells a tick) never ends: every pump pass found 20–27k cells again with every wall in place. The water is
 *  removed in ONE go per slab with /fill ... replace (engine-side, one tick, no regeneration window): slabs of 7 layers
 *  keep each call under the 32,768-block limit. Returns [commands that succeeded, commands that failed]. */
function drainBox(dim, x0, y0, z0, x1, y1, z1) {
  let ok = 0, bad = 0, firstErr = null;
  for (let y = y0; y <= y1; y += 7) {
    const yt = Math.min(y + 6, y1);
    // FLOW test (10-05 13:2x): flowing and falling water carry the id minecraft:water (liquid_depth 1-7, 8+) — one filter removes all
    try { const r = dim.runCommand(`fill ${x0} ${y} ${z0} ${x1} ${yt} ${z1} air [] replace water`); if (r && r.successCount > 0) ok++; else { bad++; if (!firstErr) firstErr = `successCount 0 at y ${y}..${yt} (nothing matched, or a chunk of the volume sleeps)`; } }
    catch (e) { bad++; if (!firstErr) firstErr = String(e).slice(0, 120); }
  }
  if (bad && firstErr) console.warn(`[CIV-CLOCK] drain: ${bad} fill command(s) failed: ${firstErr}`);
  return [ok, bad];
}
/** the palace block's land, a generator for system.runJob (the plot stage of a piece is LIGHT — only the ground work at
 *  feet >= -2 — because placing the full 196k-cell box took up to 8 s in one tick, two seconds under the watchdog):
 *  0. the retaining walls (palaceWallJob);
 *  1. NATURAL blocks inside the piece's box and 24 rows above it are cleared (trees, plants, hills, water, snow) — never
 *     a block of ours, so a stage placed while the job still runs is safe;
 *  2. hollows under the floor slab (feet -15 .. -3) are filled with dirt where the terrain is air, water or leaves;
 *  3. the one-cell margin ring is filled from the ground up to the lawn (feet -1).
 *  ~300 block reads per tick; a piece takes ~2 min of real time, well inside the six days to the frame stage */
function* palaceLandJob(dim, b, def) {
  const [fx, sy, fz] = footprint(def, b.rot);
  const slab = b.y + def.datum_y - 1;
  const floor0 = b.y + def.datum_y;                                 // feet 0
  let ops = 0, cleared = 0, filled = 0;
  const tick = function* () { if (++ops % 300 === 0) yield; };
  const walled = yield* palaceWallJob(dim, b, def);
  const [dOk, dBad] = drainBox(dim, b.x, floor0, b.z, b.x + fx - 1, b.y + sy + 23, b.z + fz - 1);   // the lake inside, in one go (feet 0 up: the basin at feet -1 is the template's)
  yield;
  for (let i = 0; i < fx; i++) for (let j = 0; j < fz; j++) {
    const x = b.x + i, z = b.z + j;
    for (let y = floor0; y < b.y + sy + 24; y++) {                 // 1. the box and the sky above it
      let blk;
      try { blk = dim.getBlock({ x, y, z }); } catch { blk = undefined; }
      if (blk && blk.typeId !== "minecraft:air" && isNatural(blk.typeId)) { try { blk.setType("minecraft:air"); cleared++; } catch { /* left */ } }
      yield* tick();
    }
    for (let y = b.y; y <= slab - 2; y++) {                          // 2. under the slab
      let blk;
      try { blk = dim.getBlock({ x, y, z }); } catch { blk = undefined; }
      if (blk && (blk.typeId === "minecraft:air" || blk.typeId === "minecraft:water" || blk.typeId === "minecraft:flowing_water" || blk.typeId.includes("leaves") || isTreeLeafId(blk.typeId))) { try { blk.setType("minecraft:dirt"); filled++; } catch { /* left */ } }
      yield* tick();
    }
  }
  for (let i = -1; i <= fx; i++) for (let j = -1; j <= fz; j++) {   // 3. the margin ring
    if (!(i < 0 || j < 0 || i >= fx || j >= fz)) continue;
    const x = b.x + i, z = b.z + j;
    const g = groundAt(dim, x, z);
    if (g === undefined) { yield* tick(); continue; }
    for (let y = g + 1; y <= slab; y++) {
      try { const blk = dim.getBlock({ x, y, z }); if (blk && (blk.typeId === "minecraft:air" || !isGround(blk.typeId))) { blk.setType(y === slab ? "minecraft:grass_block" : "minecraft:dirt"); filled++; } } catch { /* unloaded */ }
      yield* tick();
    }
  }
  console.warn(`[CIV-CLOCK] palace land #${b.id} ${b.palace.q}: ${walled} retaining blocks, drain ${dOk} ok / ${dBad} failed, ${cleared} natural blocks cleared, ${filled} filled`);
  b.palaceDrain = 60;                                                 // the pumps: sixty daily passes (each re-checks the walls first)
}
/** the palace's pumps: the walls are checked again, then water above the floor inside the piece's box becomes air (a
 *  generator; ~300 reads a tick) */
function* palaceDrainJob(dim, pieces, def) {
  // run 14: the four quarters are drained in ONE tick (a quarter drained minutes after its neighbour regrows from it)
  let ops = 0, before = 0, after = 0, walled = 0, dOk = 0, dBad = 0;
  for (let w = 0; w < 60; w++) yield;                                       // build 19: the areas asked for a moment ago need a few ticks to load
  for (const b of pieces) walled += yield* palaceWallJob(dim, b, def);
  const wet = (x, y, z) => { try { const t = dim.getBlock({ x, y, z })?.typeId; return t === "minecraft:water" || t === "minecraft:flowing_water"; } catch { return false; } };
  // run 17 (the dump): a mountain pond INSIDE the block's columns above the box's top (y 141+ over an SE corner at 140) fed the
  // palace from the sky — the pumps emptied the box to its top and the pond refilled it. The pumps reach the land job's
  // clearing height (24 rows above the box), and the whole group in one tick, so no part of a pond survives to regrow.
  const boxes = pieces.map((b) => { const [fx, sy, fz] = footprint(def, b.rot); return [b.x, b.y + def.datum_y, b.z, b.x + fx - 1, b.y + sy + 23, b.z + fz - 1]; });
  for (const [x0, y0, z0, x1, y1, z1] of boxes) for (let x = x0; x <= x1; x += 4) for (let z = z0; z <= z1; z += 4) for (let y = y0; y <= y1; y++) { if (wet(x, y, z)) before++; if (++ops % 300 === 0) yield; }
  for (const [x0, y0, z0, x1, y1, z1] of boxes) { const [o, bd] = drainBox(dim, x0, y0, z0, x1, y1, z1); dOk += o; dBad += bd; }
  yield;
  for (const [x0, y0, z0, x1, y1, z1] of boxes) for (let x = x0; x <= x1; x += 4) for (let z = z0; z <= z1; z += 4) for (let y = y0; y <= y1; y++) { if (wet(x, y, z)) after++; if (++ops % 300 === 0) yield; }
  const names = pieces.map((b) => `#${b.id} ${b.palace.q}`).join(" ");
  if (before || walled || dOk) console.warn(`[CIV-CLOCK] palace pumps ${names}: ${before} sampled water cells before, ${after} after (fill ${dOk} ok / ${dBad} nothing), ${walled} wall blocks added (${pieces[0].palaceDrain} passes left)`);
}
/** every piece of the group must stand at stage k - 1 before any piece goes to stage k (the four quarters rise together) */
function palaceSiblingsReady(s, b, k) {
  for (const o of s.buildings) if (o.palace && o.palace.group === b.palace.group && o.id !== b.id && o.stage < k - 1) return false;
  return true;
}
'''


def main():
    if DST.exists():
        raise SystemExit(f"{DST} exists — move it to _garbage first")
    shutil.copytree(SRC, DST)
    m = json.loads(read("manifest.json"))
    m["header"]["version"] = [1, 3, 221]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.221"
    for mod in m["modules"]:
        mod["version"] = [1, 3, 221]
    m["header"]["description"] = ("v1.3.221 (2026-10-04) THE CITY PALACE: at city II the Seat of Government rises on a 128 x 128 palace block — "
                                  "gatehouse, court of honour, great hall, council / audience / cabinet, the hidden spine corridor with jib doors, "
                                  "the strongroom behind a painting, the prison tower, the service court (needs RP-01 1.3.123). Includes all of "
                                  + m["header"]["description"])[:1200]
    write("manifest.json", json.dumps(m, indent=2))
    main_js = read("scripts/main.js")
    main_js = rep(main_js, 'const PW_BUILD = "1.3.220";', 'const PW_BUILD = "1.3.221";', "PW_BUILD")
    write("scripts/main.js", main_js)
    comp = read("scripts/pw_companion.js")
    comp = rep(comp, "companion v7 LOADED (pack v1.3.220", "companion v7 LOADED (pack v1.3.221", "companion banner")
    write("scripts/pw_companion.js", comp)
    # 1. structures + stages
    for f in sorted((STG / "structures").glob("*.mcstructure")):
        shutil.copy2(f, DST / "structures/pw" / f.name)
    n_st = 0
    for f in sorted((STG / "stages").glob("*.mcstructure")):
        if f.stem.endswith("_full"):
            continue                                                  # the record copy of the heavy s0 (palace_light_s0.py)
        shutil.copy2(f, DST / "structures/pw/stages" / f.name)
        n_st += 1
    assert n_st == 20, n_st
    LOG.append("4 palace pieces + 20 stage files")
    # 1b. build 16 (his 08:55 CT 10-05, Q34): the well's parapet closes (eight walls with their connection states) — the
    # refreshed template + its stages come from the roster staging (_staging/civ), the SRC copies are replaced
    TOWN = Path("/home/claude/_staging/civ")
    shutil.copy2(TOWN / "structures/pw/mvv_well_a_r1.mcstructure", DST / "structures/pw/mvv_well_a_r1.mcstructure")
    for k in range(5):
        shutil.copy2(TOWN / "stages" / f"mvv_well_a_r1_s{k}.mcstructure", DST / "structures/pw/stages" / f"mvv_well_a_r1_s{k}.mcstructure")
    LOG.append("the well's closed parapet (template + 5 stages from the roster staging)")
    # the table
    bld = read("scripts/pw_civ_buildings.js")
    MARK = "export const CIV_BUILDINGS = "
    head, body = bld.split(MARK, 1)
    body = body.strip()
    assert body.endswith(";")
    tbl = json.loads(body[:-1])
    import civ_village_data as VD
    tbl["pw:mvv_well_a_r1"] = dict(VD.table()["pw:mvv_well_a_r1"], art=tbl.get("pw:mvv_well_a_r1", {}).get("art", []))   # build 16: the well's refreshed bill (8 walls)
    for k, v in palace_entries().items():
        assert k not in tbl
        tbl[k] = v
    write("scripts/pw_civ_buildings.js", head + MARK + json.dumps(tbl, separators=(",", ":")) + ";")
    LOG.append(f"CIV_BUILDINGS + 4 palace entries ({len(tbl)} buildings)")
    # 2. blocks (BP side here; the RP side by build_rp01_123.py)
    r = subprocess.run([sys.executable, "/home/claude/tools/build_palace_blocks.py", str(DST), str(B / "rp01-123")], capture_output=True, text=True)
    print(r.stdout[-400:], r.stderr[-800:])
    if r.returncode != 0:
        raise SystemExit("palace blocks failed")
    LOG.append("blocks pw:jib_panel + pw:secret_painting")
    # 3. the clock
    clock = read("scripts/pw_civ_clock.js")
    clock = rep(clock, "// ------------------------------------------------------------------------------------------------ settlements\nfunction plotsOf(s, st)",
                CLOCK_PALACE + "\n// ------------------------------------------------------------------------------------------------ settlements\nfunction plotsOf(s, st)", "palace functions")
    clock = rep(clock, "    while (b.stage < last && b.progress >= STAGE_DAYS[b.stage]) {",
                "    const SDAYS = b.palace ? PALACE_STAGE_DAYS : STAGE_DAYS;                       // 1.3.221: the palace keeps its own calendar\n"
                "    while (b.stage < last && b.progress >= SDAYS[b.stage]) {\n"
                "      if (b.palace) {                                                            // the crown's works: lockstep, wages only\n"
                "        if (!palaceSiblingsReady(s, b, b.stage + 1)) { b.progress = SDAYS[b.stage]; break; }\n"
                "        const stp = s.settlements.find((x) => x.id === b.settlement);\n"
                "        if (stp && stp.ledger && stp.ledger.v === 2) {\n"
                "          const bill = stageBillOf(b, b.stage + 1);\n"
                "          const w = Math.min(bill.wages, Math.max(0, stp.ledger.treasury));\n"
                "          ECON.pay(stp.ledger, { mats: {}, wages: w, blocks: 0 });\n"
                "          stp.log.push(`day ${s.simDays.toFixed(0)}: the crown's works — the ${STAGE_NAMES[b.stage + 1]} of the palace's ${b.palace.q} quarter (${bill.blocks} blocks; ${w} p wages from the treasury)`);\n"
                "        }\n"
                "        b.progress -= SDAYS[b.stage];\n"
                "        b.stage += 1;\n"
                "        b.pending.push(b.stage);\n"
                "        events.push(`#${b.id} ${short(b)} -> ${STAGE_NAMES[b.stage]}`);\n"
                "        continue;\n"
                "      }", "palace stage calendar + lockstep")
    clock = rep(clock, "    if (k === 0 && b.street) { clearOver(dim, b, def); b.filled = (b.land && b.land.kind === \"stilts\") ? 0 : terrace(dim, b, def); }   // a stilt house has posts, not a ring",
                "    if (k === 0 && b.street) { clearOver(dim, b, def); b.filled = (b.land && b.land.kind === \"stilts\") ? 0 : terrace(dim, b, def); }   // a stilt house has posts, not a ring\n"
                "    if (k === 0 && b.palace) { b.filled = 0; try { system.runJob(palaceLandJob(dim, b, def)); } catch (e) { console.warn(`[CIV-CLOCK] palace land: ${e}`); } }   // 1.3.221: the palace block's land, spread over ticks (a 64 x 64 piece in one tick hangs the watchdog)",
                "palace land prep")
    # the placement of a palace piece is timed (the watchdog budget is 10 s per tick), and a clock beat works off at most
    # 3 carried days instead of 5 (a city's day costs ~1 s of script at 40 buildings / 130 people — run 3 of the gate hung
    # at 4 days + a palace stage in one beat)
    clock = rep(clock, "    world.structureManager.place(`pw:stages/${def.stem}_s${k}`, dim, { x: b.x, y: b.y, z: b.z },\n      anim ? { rotation: ROTS[b.rot], includeEntities: true, animationMode: StructureAnimationMode.Layers, animationSeconds: secs } : { rotation: ROTS[b.rot], includeEntities: true });",
                "    timed(`place #${b.id} ${def.stem} s${k}`, () => world.structureManager.place(`pw:stages/${def.stem}_s${k}`, dim, { x: b.x, y: b.y, z: b.z },\n      anim ? { rotation: ROTS[b.rot], includeEntities: true, animationMode: StructureAnimationMode.Layers, animationSeconds: secs } : { rotation: ROTS[b.rot], includeEntities: true }));",
                "timed placement")
    clock = rep(clock, "const LAG_SLICES = 5;", "const LAG_SLICES = 3;", "lag slices 3")
    # every CHUNK under a piece must be loaded before a stage is placed (gallery gate runs 2/4/5: a 64 x 64 piece spanning five
    # chunks passed the two-corner test while its middle chunks slept — structureManager.place skips unloaded chunks without a
    # word, the piece stood half built, and the terrain's lake read as "the palace is flooded")
    clock = rep(clock, "    try { loaded = !!dim.getBlock({ x: b.x, y: yProbe, z: b.z }) && !!dim.getBlock({ x: b.x + fx - 1, y: yProbe, z: b.z + fz - 1 }); } catch { loaded = false; }",
                "    try {\n"
                "      loaded = true;\n"
                "      for (let cx = Math.floor(b.x / 16) * 16; loaded && cx <= b.x + fx - 1; cx += 16) for (let cz = Math.floor(b.z / 16) * 16; cz <= b.z + fz - 1; cz += 16) {\n"
                "        if (!dim.getBlock({ x: Math.max(cx, b.x), y: yProbe, z: Math.max(cz, b.z) })) { loaded = false; break; }\n"
                "      }\n"
                "    } catch { loaded = false; }                                           // 1.3.221: every chunk of the footprint, not two corners",
                "all chunks loaded before a stage")
    # one palace piece per beat (four 196k-block placements in one tick would trip the 10 s watchdog)
    clock = rep(clock, "function flushPending() {\n  const s = load();\n  for (const b of s.buildings) {\n    while (b.pending.length) {\n      const k = b.pending[0];",
                "function flushPending() {\n  const s = load();\n  let palacePlaced = false;                                                       // 1.3.221: one palace piece per beat\n"
                "  for (const b of s.buildings) {\n    if (b.palace && palacePlaced) continue;\n    while (b.pending.length) {\n      const k = b.pending[0];\n      if (b.palace && palacePlaced) break;\n      if (b.palace && typeof k !== \"string\") palacePlaced = true;",
                "palace one piece per beat")
    clock = rep(clock, "  st.tier = tier;\n  st.tierDay = s.simDays;",
                "  st.tier = tier;\n  st.tierDay = s.simDays;\n"
                "  if (tier === PALACE_TIER && !st.palace) {                                          // 1.3.221: the Seat of Government\n"
                "    try { if (!placePalace(s, st, world.getDimension(st.dim))) st.palacePending = true; } catch (e) { console.warn(`[CIV-CLOCK] palace: ${e}`); st.palacePending = true; }\n"
                "  }", "palace at city II")
    clock = rep(clock, "function coreBusy(s, a) {\n  const st = s.settlements.find((x) => x.id === a.st);\n  if (!st) return false;",
                "function coreBusy(s, a) {\n  const st = s.settlements.find((x) => x.id === a.st);\n  if (!st) return false;\n"
                "  if (st.palaceSurvey && st.palaceSurvey.area === a.name && !st.palace) return true;   // 1.3.221: the crown's surveyors hold their area",
                "palace survey hold")
    clock = rep(clock, "function stepSettlementBody(s, st, days, events) {\n  const age = s.simDays - st.founded;\n  stepEconomy(s, st, days, events);",
                "function stepSettlementBody(s, st, days, events) {\n  const age = s.simDays - st.founded;\n  stepEconomy(s, st, days, events);\n"
                "  if (st.palacePending && !st.palace) { try { placePalace(s, st, world.getDimension(st.dim)); } catch (e) { console.warn(`[CIV-CLOCK] palace retry: ${e}`); } }   // 1.3.221: until the site's chunks are loaded\n"
                "  { const wetPieces = s.buildings.filter((pb) => pb.palace && pb.settlement === st.id && pb.palaceDrain > 0);\n"
                "    if (wetPieces.length) { try { const pd = BUILDINGS[wetPieces[0].family]; for (const pb of wetPieces) { pb.palaceDrain -= 1; const [pfx, , pfz] = footprint(pd, pb.rot); ensureTicking(s, st, [pb.x - 8, pb.z - 8, pb.x + pfx + 7, pb.z + pfz + 7], `palace pumps #${pb.id}`); } system.runJob(palaceDrainJob(world.getDimension(st.dim), wetPieces, pd)); } catch (e) { console.warn(`[CIV-CLOCK] palace pumps: ${e}`); } } }   // 1.3.221: the pumps (build 20: the whole group in one job, its chunks held — /fill needs them loaded)",
                "palace daily retry")
    write("scripts/pw_civ_clock.js", clock)
    print("\n".join(f"  ok  {w}" for w in LOG))
    print("DONE", DST)


if __name__ == "__main__":
    main()
