#!/usr/bin/env python3
"""build_bp02_220.py — BP-02 1.3.220 from the frozen 1.3.219 (round 1004b, D-C563; his 17:38 / 17:59 / 18:23 / 18:30).
Every change is an exact-match patch (rep: one match or the build stops) on a fresh copy of bp02-219, so the build is
reproducible; the sources in tools/bp02_src are refreshed from the result at the end.
  1. FELLING BY TEMPLATE (pw_civ_clock.fellTree): a structure tree (a pw root under its base log) is taken by its
     template's exact logs + leaves; a rootless tree by a log BFS + leaves within LEAF_REACH steps. No floating crowns.
  2. FLOATING-FOLIAGE SWEEP: leaves / vines not connected (through leaves to a log column that stands on the ground) are
     removed — at founding, when a building completes, daily over the influence (a runJob, chunk by chunk).
  3. FLOODING: streets and plots are DRAINED to the pieces' depth and the box's ring is sealed (a cofferdam); a daily
     flood watch drains water that reaches a street's surface and seals its source.
  4. MOBS: every entity that is not a player / civ / lead / marker / item inside a placed structure's box is removed.
  5. CIVS (entities/villager_v2.json + pw_civ_walk/shop): vanilla trade / stroll / dwelling / breeding / job groups never
     reach a civ; stand / idle / home states; every civ opens our window; chimney flues avoided by the pathfinder.
  6. LECTERN: the town hall's lectern faces the speaker's side (east in the r1 frame) in the 4 templates + stages + dir.
  7. VINES: the touch shake is off; the wind sway stays.
  8. FALLING TREES: angle from the tree's own cells against the real ground (top faces, exact ground set, pivot at the
     stump's top leading edge), physics timing (T = 1.10 sqrt(H)), rebound UP, sounds on the impact frame (RP-01 1.3.122).
Usage: python3 tools/build_bp02_220.py            (bp02-220 must not exist: move the old one to _garbage first)"""
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-219", B / "bp02-220"
SRC_JS = Path("/home/claude/tools/bp02_src")
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


# ---------------------------------------------------------------------------------------------- 0. the copy
if DST.exists():
    raise SystemExit(f"{DST} exists — move it to _garbage first (never rebuild in place)")
shutil.copytree(SRC, DST)
m = json.loads(read("manifest.json"))
m["header"]["version"] = [1, 3, 220]
m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.220"
for mod in m["modules"]:
    mod["version"] = [1, 3, 220]
old_desc = m["header"]["description"]
m["header"]["description"] = ("v1.3.220 (2026-10-04) CIVS: every civ opens our window (no emerald trades), stand / idle / home "
                              "states (no vanilla wandering, jobs or breeding; children never work), chimney flues avoided; "
                              "FLOODING drained and sealed; mobs cleared from script-built structures; FLOATING FOLIAGE swept; "
                              "the town fells trees by their template; the lectern faces the speaker; vines sway only (no "
                              "shake); FALLING TREES rebuilt on physics (needs RP-01 1.3.122). Includes all of " + old_desc)[:1200]
write("manifest.json", json.dumps(m, indent=2))
main = read("scripts/main.js")
main = rep(main, 'const PW_BUILD = "1.3.219";', 'const PW_BUILD = "1.3.220";', "PW_BUILD")
write("scripts/main.js", main)
comp = read("scripts/pw_companion.js")
comp = rep(comp, "companion v7 LOADED (pack v1.3.219", "companion v7 LOADED (pack v1.3.220", "companion banner")
write("scripts/pw_companion.js", comp)

# ---------------------------------------------------------------------------------------------- 1. felling by template
clock = read("scripts/pw_civ_clock.js")
clock = rep(clock, 'import * as COIN from "./pw_civ_coin.js";',
            'import * as COIN from "./pw_civ_coin.js";\n'
            'import { templateFallingSet, isTreeLeafId } from "./pw_fell_rules.js";   // 1004b: the town fells a tree by its TEMPLATE (D-C563)',
            "clock imports pw_fell_rules")

OLD_FELL_HEAD = "function fellTree(dim, x, y, z, occupied = () => false, stump = true) {\n  const logs = [];"
NEW_FELL = r'''const LEAF_REACH = 8;          // 1004b: a rootless tree's crown = leaves within this many face-steps of its logs (vanilla's decay reach)
const FELL_MAX_LEAVES = 1200;
/** 1004b (D-C563, his birches "incomplete and broken"): the cells of ONE tree. A structure tree — a pw root at or under
 *  its lowest log — gives its template's exact logs and leaves (nothing of a neighbour, nothing left floating, the T4 law
 *  of main.js). A rootless tree: its logs by the old flood, then every leaf reachable from them through leaves within
 *  LEAF_REACH steps. Returns null when no log stands at the start. */
function treeCells(dim, x, y, z, occupied = () => false) {
  const get = (cx, cy, cz) => { try { return dim.getBlock({ x: cx, y: cy, z: cz }); } catch { return undefined; } };
  const logs = [];
  const seen = new Set();
  const q = [[x, y, z]];
  while (q.length && logs.length < 400) {
    const [cx, cy, cz] = q.pop();
    const key = `${cx},${cy},${cz}`;
    if (seen.has(key)) continue;
    seen.add(key);
    if (Math.abs(cx - x) > 7 || Math.abs(cz - z) > 7 || cy - y > 32 || cy < y - 1) continue;
    if (occupied(cx, cz)) continue;                                   // never a house's posts or the street
    const blk = get(cx, cy, cz);
    if (!blk || !TREE_LOG(blk.typeId)) continue;
    logs.push([cx, cy, cz, blk.typeId]);
    for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1], [1, 1, 0], [-1, 1, 0], [0, 1, 1], [0, 1, -1], [1, 0, 1], [-1, 0, -1], [1, 0, -1], [-1, 0, 1]])
      q.push([cx + dx, cy + dy, cz + dz]);
  }
  if (!logs.length) return null;
  const base = logs.reduce((a, l) => (l[1] < a[1] ? l : a), logs[0]);
  // the root: the base log itself, or a pw root block at most 3 below it (the trunk column is logs down to the root)
  for (let dy = 0; dy <= 3; dy++) {
    const b = get(base[0], base[1] - dy, base[2]);
    if (!b) break;
    const id = b.typeId;
    if (id.startsWith("pw:") && id.endsWith("_root")) {
      let root = null;
      try { root = { x: base[0], y: base[1] - dy, z: base[2], id, tpl: (b.permutation.getState("pw:tpl") ?? 0) + 16 * (b.permutation.getState("pw:tpl_hi") ?? 0), dir: b.permutation.getState("minecraft:cardinal_direction") }; }
      catch { root = null; }
      if (root) {
        let set = null;
        try { set = templateFallingSet(dim, root, { x: -1e9, y: -1e9, z: -1e9 }); } catch { set = null; }
        if (set) {
          const tlogs = [];
          for (const p of set.trunkAbove.concat(set.trunkBelow)) { if (occupied(p.x, p.z)) continue; const bb = get(p.x, p.y, p.z); tlogs.push([p.x, p.y, p.z, bb ? bb.typeId : "minecraft:air"]); }
          return { logs: tlogs, leaves: set.leaves.map((p) => [p.x, p.y, p.z]), base: [root.x, root.y, root.z, id], tpl: set.name };
        }
      }
      break;
    }
    if (!TREE_LOG(id)) break;
  }
  // rootless: the crown by reach through leaves
  const leaves = [];
  const lseen = new Set();
  let frontier = logs.map((l) => [l[0], l[1], l[2]]);
  for (let step = 0; step < LEAF_REACH && frontier.length && leaves.length < FELL_MAX_LEAVES; step++) {
    const next = [];
    for (const [cx, cy, cz] of frontier) {
      for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]) {
        const nx = cx + dx, ny = cy + dy, nz = cz + dz;
        const key = `${nx},${ny},${nz}`;
        if (lseen.has(key) || seen.has(key)) continue;
        lseen.add(key);
        const b = get(nx, ny, nz);
        if (!b || !isTreeLeafId(b.typeId)) continue;
        leaves.push([nx, ny, nz]);
        next.push([nx, ny, nz]);
      }
    }
    frontier = next;
  }
  return { logs, leaves, base, tpl: null };
}

function fellTree(dim, x, y, z, occupied = () => false, stump = true) {
  const tree = treeCells(dim, x, y, z, occupied);
  if (!tree) return 0;
  const { logs, leaves, base } = tree;
  let removed = 0;
  for (const [lx, ly, lz] of leaves) { try { const lf = dim.getBlock({ x: lx, y: ly, z: lz }); if (lf && isTreeLeafId(lf.typeId)) { lf.setType("minecraft:air"); removed++; } } catch { /* unloaded */ } }
  for (const [lx, ly, lz] of logs) { try { dim.getBlock({ x: lx, y: ly, z: lz })?.setType("minecraft:air"); } catch { /* unloaded */ } }
  if (!stump) return logs.length;
  // the stump: the base log's tier if it was one of ours, else a plain oak-tier stump of the same wood when we have it
  const m = /pw:([a-z_]+_(?:young|mature|old|elder))(?:_root)?$/.exec(base[3]);
  try {
    const stumpId = m ? `pw:${m[1]}_stump` : null;
    const blk = dim.getBlock({ x: base[0], y: base[1], z: base[2] });
    if (blk) { if (stumpId) { try { blk.setType(stumpId); } catch { blk.setType(base[3].replace("_root", "")); } } else blk.setType(base[3]); }
  } catch { /* left */ }
  return logs.length;
}

function fellTree_old_unused(dim, x, y, z, occupied = () => false, stump = true) {
  const logs = [];'''
clock = rep(clock, OLD_FELL_HEAD, NEW_FELL, "fellTree by template (old body kept as fellTree_old_unused)")

# ---------------------------------------------------------------------------------------------- 2. floating-foliage sweep
SWEEP = r'''
// ------------------------------------------------------------------------------------------------ FLOATING FOLIAGE (1004b, his 17:38)
// "all of the space above towns and villages checked when buildings are built: foliage, leaf blocks or vines that aren't
// attached to a complete tree (contiguously connected to the ground) are removed". A CLUSTER = leaves + vines + logs
// joined face to face; it STANDS when one of its logs rests on ground (or on a log column that does). Clusters are found
// with the engine's own filter (getBlocks includeTypes, #171) one chunk column at a time, inside a runJob; a cluster is
// walked at most SWEEP_CLUSTER cells. Removal drops nothing (the crown was a leftover, not a harvest).
const SWEEP_CLUSTER = 1500, SWEEP_TOP = 48;
const SWEEP_GROUND = new Set(["minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:podzol", "minecraft:mycelium", "minecraft:moss_block",
  "minecraft:mud", "minecraft:rooted_dirt", "minecraft:dirt_with_roots", "minecraft:muddy_mangrove_roots", "minecraft:sand", "minecraft:red_sand", "minecraft:gravel",
  "minecraft:clay", "minecraft:stone", "minecraft:snow", "minecraft:farmland", "minecraft:grass_path", "minecraft:dirt_path", "minecraft:pale_moss_block",
  "minecraft:water", "minecraft:flowing_water", "pw:grass_block", "minecraft:deepslate", "minecraft:andesite", "minecraft:granite", "minecraft:diorite", "minecraft:tuff"]);
const SWEEP_LEAF_IDS = ["pw:oak_leaves", "pw:spruce_leaves", "pw:birch_leaves", "pw:jungle_leaves", "pw:acacia_leaves", "pw:dark_oak_leaves", "pw:mangrove_leaves",
  "pw:cherry_leaves", "pw:pale_oak_leaves", "pw:azalea_leaves", "pw:flowering_azalea_leaves", "minecraft:oak_leaves", "minecraft:spruce_leaves", "minecraft:birch_leaves",
  "minecraft:jungle_leaves", "minecraft:acacia_leaves", "minecraft:dark_oak_leaves", "minecraft:mangrove_leaves", "minecraft:cherry_leaves", "minecraft:pale_oak_leaves",
  "minecraft:azalea_leaves", "minecraft:azalea_leaves_flowered", "minecraft:vine", "pw:vine"];
let _sweepTypes = null;
function sweepTypes() {
  if (!_sweepTypes) _sweepTypes = SWEEP_LEAF_IDS.filter((id) => { try { return !!BlockTypes.get(id); } catch { return false; } });
  return _sweepTypes;
}
const isSweepFoliage = (id) => id.includes("leaves") || id === "minecraft:vine" || id === "pw:vine";
/** sweep one chunk column [cx, cz] (chunk coords) between yLo and yLo + SWEEP_TOP: a generator (yield between clusters) */
function* sweepChunk(dim, cx, cz, yLo, stats) {
  const vol = new BlockVolume({ x: cx * 16, y: yLo, z: cz * 16 }, { x: cx * 16 + 15, y: Math.min(yLo + SWEEP_TOP, 319), z: cz * 16 + 15 });
  let found;
  try { found = dim.getBlocks(vol, { includeTypes: sweepTypes() }, true); } catch { return; }
  const done = new Set();
  const get = (x, y, z) => { try { return dim.getBlock({ x, y, z }); } catch { return undefined; } };
  for (const loc of found.getBlockLocationIterator()) {
    const k0 = `${loc.x},${loc.y},${loc.z}`;
    if (done.has(k0)) continue;
    // the cluster: leaves + vines + logs, face-connected, bounded
    const cells = [], seen = new Set([k0]), stack = [[loc.x, loc.y, loc.z]];
    let stands = false, logsIn = 0;
    while (stack.length && cells.length < SWEEP_CLUSTER) {
      const [x, y, z] = stack.pop();
      const b = get(x, y, z);
      if (!b) { stands = true; break; }                                  // unloaded: never decide on a half-read cluster
      const id = b.typeId;
      const isLog = TREE_LOG(id) || id.endsWith("_stump");
      if (!isLog && !isSweepFoliage(id)) continue;
      cells.push([x, y, z, isLog]);
      if (isLog) {
        logsIn++;
        const under = get(x, y - 1, z);
        if (under && (SWEEP_GROUND.has(under.typeId) || under.typeId.endsWith("_stump"))) { stands = true; }
      }
      for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]) {
        const k = `${x + dx},${y + dy},${z + dz}`;
        if (!seen.has(k)) { seen.add(k); stack.push([x + dx, y + dy, z + dz]); }
      }
    }
    if (cells.length >= SWEEP_CLUSTER) stands = true;                   // too big to judge: leave it (a forest canopy)
    for (const [x, y, z] of cells) done.add(`${x},${y},${z}`);
    stats.clusters++;
    if (stands) continue;
    let n = 0;
    for (const [x, y, z, isLog] of cells) { if (isLog) continue; const b = get(x, y, z); if (b && isSweepFoliage(b.typeId)) { try { b.setType("minecraft:air"); n++; } catch { /* left */ } } }
    stats.removed += n; stats.orphans++;
    yield;
  }
}
/** sweep a world box [x0..x1] x [z0..z1] above ground level yLo (a generator for system.runJob); logs to the settlement */
function* sweepBoxJob(dim, x0, z0, x1, z1, yLo, st, label) {
  const stats = { clusters: 0, orphans: 0, removed: 0 };
  for (let cx = Math.floor(x0 / 16); cx <= Math.floor(x1 / 16); cx++) for (let cz = Math.floor(z0 / 16); cz <= Math.floor(z1 / 16); cz++) {
    yield* sweepChunk(dim, cx, cz, yLo, stats);
    yield;
  }
  if (st) { st.sweep = { day: load().simDays, ...stats, label }; if (stats.removed) st.log.push(`day ${load().simDays.toFixed(0)}: ${stats.removed} floating leaves cleared (${stats.orphans} crowns, ${label})`); }
}
const sweepJobs = new Map();                                          // settlement id -> running
function sweepBox(dim, st, x0, z0, x1, z1, yLo, label) {
  const key = `${st ? st.id : "w"}:${label}`;
  if (sweepJobs.has(key)) return false;
  sweepJobs.set(key, true);
  const job = sweepBoxJob(dim, x0, z0, x1, z1, yLo, st, label);
  system.runJob((function* () { try { yield* job; } finally { sweepJobs.delete(key); } })());
  return true;
}
/** the daily sweep: one 4 x 4-chunk tile of the influence square per call, round-robin (st.sweepTile) */
function sweepDaily(dim, st) {
  if (!st.square) return;
  const r = (st.border && st.border.r) || INFLUENCE[st.tier] || 64;
  const x0 = st.square.x + 6 - r, z0 = st.square.z + 6 - r, x1 = st.square.x + 6 + r, z1 = st.square.z + 6 + r;
  const tiles = Math.ceil((x1 - x0 + 1) / 64) * Math.ceil((z1 - z0 + 1) / 64);
  const i = (st.sweepTile || 0) % tiles, nz = Math.ceil((z1 - z0 + 1) / 64);
  const tx = Math.floor(i / nz), tz = i % nz;
  st.sweepTile = i + 1;
  const sx0 = x0 + tx * 64, sz0 = z0 + tz * 64;
  sweepBox(dim, st, sx0, sz0, Math.min(x1, sx0 + 63), Math.min(z1, sz0 + 63), (st.square.y || 64) - 8, `tile ${i + 1}/${tiles}`);
}
'''
clock = rep(clock, "/** the LUMBERYARD clearing: fell the trees within radius 10 + 6 per tier around the yard (at most N per pass) */",
            SWEEP + "\n/** the LUMBERYARD clearing: fell the trees within radius 10 + 6 per tier around the yard (at most N per pass) */",
            "floating-foliage sweep functions")
write("scripts/pw_civ_clock.js", clock)
print("\n".join(f"  ok  {w}" for w in LOG))
print("STAGE 1 written (felling + sweep functions); hooks follow")

# ---------------------------------------------------------------------------------------------- 2b. hooks: sweep + mob clearing + flood watch
clock = read("scripts/pw_civ_clock.js")
clock = rep(clock, "    if (st.kit) sweepLeaves(st);                                 // v1.3.219 (his 18:02): floating leaves cleared every day",
            "    if (st.kit) { try { sweepDaily(world.getDimension(st.dim), st); } catch (e) { console.warn(`[CIV-CLOCK] sweep: ${e}`); } }   // 1004b: floating foliage (ground-connected rule) tile by tile\n"
            "    if (st.kit) { try { floodWatch(world.getDimension(st.dim), st); } catch (e) { console.warn(`[CIV-CLOCK] flood watch: ${e}`); } }   // 1004b: water on a street is drained and its source sealed",
            "daily sweep + flood watch hooks")
# mobs out of every placed stage, and the sweep when a building completes
clock = rep(clock,
            "    delete b.animate;\n    const post = () => { const set = fixDirections(dim, b, def); if (set) b.turned = (b.turned || 0) + set; if (k === 2) turnLids(dim, b, def); };",
            "    delete b.animate;\n"
            "    try { b.cleared = (b.cleared || 0) + clearMobsIn(dim, b.x - 1, b.y, b.z - 1, b.x + fx, b.y + def.size[1], b.z + fz); } catch (e) { console.warn(`[CIV-CLOCK] mobs #${b.id}: ${e}`); }   // 1004b (his 17:59): nothing left inside a script-built structure\n"
            "    const post = () => { const set = fixDirections(dim, b, def); if (set) b.turned = (b.turned || 0) + set; if (k === 2) turnLids(dim, b, def); };",
            "mob clearing at every stage")
clock = rep(clock,
            "    if (k === def.stages - 1 && b.settlement !== undefined && !b.villagers) moveIn(dim, b, def);",
            "    if (k === def.stages - 1 && b.settlement !== undefined && !b.villagers) moveIn(dim, b, def);\n"
            "    if (k === def.stages - 1 && b.settlement !== undefined) { const sst = load().settlements.find((x) => x.id === b.settlement); if (sst) sweepBox(dim, sst, b.x - 10, b.z - 10, b.x + fx + 9, b.z + fz + 9, b.y + def.datum_y - 6, `#${b.id} ${short(b)}`); }   // 1004b: the air above a finished building holds no floating crown",
            "sweep when a building completes")
# the street pieces: mobs out of the laid corridor cells, water drained to the pieces' depth and the ring sealed
clock = rep(clock,
            "          kitPrep(dim, street, op.a, len, op.H, false, boxes, kitBody(st));\n          world.structureManager.place(`pw:road/${st.width || \"v\"}_${op.kind}`, dim, { x: op.x, y: op.y, z: op.z }, { rotation: ROTS[op.rot] });",
            "          kitPrep(dim, street, op.a, len, op.H, false, boxes, kitBody(st));\n"
            "          try { st.kitDrained = (st.kitDrained || 0) + kitDrain(dim, street, op.a, len, op.H, boxes); } catch (e) { console.warn(`[CIV-CLOCK] drain: ${e}`); }   // 1004b: a street is never laid into standing water\n"
            "          world.structureManager.place(`pw:road/${st.width || \"v\"}_${op.kind}`, dim, { x: op.x, y: op.y, z: op.z }, { rotation: ROTS[op.rot] });\n"
            "          try { const [cx0, cz0] = KIT.cellOf(street.f, op.a, 0), [cx1, cz1] = KIT.cellOf(street.f, op.a + len - 1, 12); st.mobsCleared = (st.mobsCleared || 0) + clearMobsIn(dim, Math.min(cx0, cx1), op.H - 15, Math.min(cz0, cz1), Math.max(cx0, cx1), op.H + 4, Math.max(cz0, cz1)); } catch (e) { console.warn(`[CIV-CLOCK] mobs street: ${e}`); }",
            "street piece: drain + mob clearing")

MOBS_AND_FLOOD = r'''
// ------------------------------------------------------------------------------------------------ MOBS OUT (1004b, his 17:59)
// A structure placed by script leaves whatever stood there inside its walls. Every entity in the placed box that is not a
// player, a civ, a lead, a marker, an item or one of the engine's furniture entities is removed. The box is inclusive.
const KEEP_ENTITY = new Set(["minecraft:player", "minecraft:item", "minecraft:xp_orb", "pw:lead", "pw:marker", "pw:hatch_lid", "ft:falling_tree", "pw:leaf_litter",
  "minecraft:painting", "minecraft:item_frame", "minecraft:glow_item_frame", "minecraft:armor_stand", "minecraft:boat", "minecraft:chest_boat", "minecraft:minecart",
  "minecraft:chest_minecart", "minecraft:hopper_minecart", "minecraft:villager_v2", "minecraft:wandering_trader", "minecraft:iron_golem"]);
function clearMobsIn(dim, x0, y0, z0, x1, y1, z1) {
  let n = 0;
  let list = [];
  try { list = dim.getEntities({ location: { x: (x0 + x1) / 2, y: (y0 + y1) / 2, z: (z0 + z1) / 2 }, maxDistance: Math.hypot(x1 - x0, y1 - y0, z1 - z0) / 2 + 2 }); } catch { return 0; }
  for (const e of list) {
    try {
      if (!e || !e.isValid) continue;
      const id = e.typeId;
      if (KEEP_ENTITY.has(id)) continue;
      if (id === "minecraft:villager_v2" || e.hasTag("civ:villager")) continue;
      const l = e.location;
      if (l.x < x0 || l.x > x1 + 1 || l.y < y0 || l.y > y1 + 1 || l.z < z0 || l.z > z1 + 1) continue;
      e.remove(); n++;
    } catch { /* gone */ }
  }
  return n;
}

// ------------------------------------------------------------------------------------------------ FLOODING (1004b, his 17:38)
// "they attempted to build over water; the walls went up but the water itself was never removed and flooded the streets".
// kitDrain: before a piece is laid, every water cell in the corridor (w 0..12) from the pieces' lowest tunnel (H - 15) to
// H + 3 becomes air (above H) or dirt (at and below H, the pieces replace what they cover); the corridor's RING (w -1 and
// 13, the cells beyond the piece's ends) is sealed with stone bricks wherever it holds water between H - 16 and H + 6 — a
// cofferdam, so the pond cannot flow back. floodWatch (daily): the surface cells of every laid street (H + 1 .. H + 3)
// that hold water are drained and the water's source (the first wet cell outward on the same level) is sealed.
const DRAIN_FILL = "minecraft:stone_bricks";
const isWater = (id) => id === "minecraft:water" || id === "minecraft:flowing_water";
function kitDrain(dim, street, a, len, H, boxes = []) {
  const f = street.f;
  const inPlot = (x, z) => boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  let n = 0;
  const cell = (x, y, z, id) => { try { const b = dim.getBlock({ x, y, z }); if (b && isWater(b.typeId)) { b.setType(id); n++; } } catch { /* unloaded */ } };
  for (let t = a - 1; t <= a + len; t++) {
    for (let w = -1; w <= 13; w++) {
      const [x, z] = KIT.cellOf(f, t, w);
      const ring = w === -1 || w === 13 || t === a - 1 || t === a + len;
      if (ring) { if (inPlot(x, z)) continue; for (let y = H - 16; y <= H + 6; y++) cell(x, y, z, DRAIN_FILL); continue; }
      for (let y = H - 15; y <= H + 3; y++) cell(x, y, z, y <= H ? "minecraft:dirt" : "minecraft:air");
    }
  }
  if (n) street.drained = (street.drained || 0) + n;
  return n;
}
/** a plot: water inside the box from the cellar's floor (H - 16) to H + 3 is drained, the ring (1 cell around, H - 16 .. H + 6) sealed */
function plotDrain(dim, b, def, H) {
  const [fx, , fz] = footprint(def, b.rot);
  let n = 0;
  const cell = (x, y, z, id) => { try { const blk = dim.getBlock({ x, y, z }); if (blk && isWater(blk.typeId)) { blk.setType(id); n++; } } catch { /* unloaded */ } };
  for (let x = b.x - 1; x <= b.x + fx; x++) for (let z = b.z - 1; z <= b.z + fz; z++) {
    const ring = x === b.x - 1 || x === b.x + fx || z === b.z - 1 || z === b.z + fz;
    if (ring) { for (let y = H - 16; y <= H + 6; y++) cell(x, y, z, DRAIN_FILL); continue; }
    for (let y = H - 16; y <= H + 3; y++) cell(x, y, z, y <= H ? "minecraft:dirt" : "minecraft:air");
  }
  if (n) b.drained = (b.drained || 0) + n;
  return n;
}
function floodWatch(dim, st) {
  let drained = 0, sealed = 0;
  for (const street of st.streets || []) {
    if (street.kind !== "kit" || !street.f) continue;
    if (!Array.isArray(street.H)) continue;
    const t0 = street.tmin, t1 = street.tmin + street.H.length - 1;
    for (let t = t0; t <= t1; t += 1) {
      const H = kitHAt(street, t);
      if (H === undefined) continue;
      for (let w = 0; w <= 12; w++) {
        const [x, z] = KIT.cellOf(street.f, t, w);
        for (let y = H + 1; y <= H + 3; y++) {
          let b; try { b = dim.getBlock({ x, y, z }); } catch { b = undefined; }
          if (!b || !isWater(b.typeId)) continue;
          b.setType("minecraft:air"); drained++;
          // the source: walk outward on this level from the corridor's edge until the first wet cell beyond the corridor, seal it
          for (const dw of [-1, 1]) {
            for (let k = 1; k <= 6; k++) {
              const [sx, sz] = KIT.cellOf(street.f, t, w + dw * k);
              let sb; try { sb = dim.getBlock({ x: sx, y, z: sz }); } catch { sb = undefined; }
              if (!sb) break;
              if (isWater(sb.typeId) && (w + dw * k < 0 || w + dw * k > 12)) { sb.setType(DRAIN_FILL); sealed++; break; }
            }
          }
        }
      }
    }
  }
  if (drained) { st.flood = { day: load().simDays, drained, sealed }; st.log.push(`day ${load().simDays.toFixed(0)}: flood — ${drained} cells of water drained from the streets, ${sealed} sealed`); }
  return drained;
}
'''
clock = rep(clock, "// ------------------------------------------------------------------------------------------------ FLOATING FOLIAGE (1004b, his 17:38)",
            MOBS_AND_FLOOD + "\n// ------------------------------------------------------------------------------------------------ FLOATING FOLIAGE (1004b, his 17:38)",
            "mob clearing + drain + flood watch functions")
# the plot: drain BEFORE its first stage is placed (gate run 0.0.29/220 #1: draining after the placement turned a farm's own
# irrigation water into dirt — the template's water, a farm channel or the well's shaft, must stay)
clock = rep(clock, "    world.structureManager.place(`pw:stages/${def.stem}_s${k}`, dim, { x: b.x, y: b.y, z: b.z },",
            "    if (k === 0 && b.kit) {   // 1004b: the plot's standing water goes BEFORE the stage is placed; the template's own water stays\n"
            "      try { const kst0 = load().settlements.find((x) => x.id === b.settlement); const dn = plotDrain(dim, b, def, b.kit.H); if (dn && kst0) kst0.log.push(`day ${load().simDays.toFixed(0)}: ${dn} cells of water drained under #${b.id} ${short(b)} (sealed)`); }\n"
            "      catch (e) { console.warn(`[CIV-CLOCK] plot drain #${b.id}: ${e}`); }\n"
            "    }\n"
            "    world.structureManager.place(`pw:stages/${def.stem}_s${k}`, dim, { x: b.x, y: b.y, z: b.z },",
            "plot drain before the first stage")
write("scripts/pw_civ_clock.js", clock)
print("STAGE 2 written (hooks, mobs, flood)")

# ---------------------------------------------------------------------------------------------- 3. CIVS: the entity
ent_path = "entities/villager_v2.json"
ent = json.loads(read(ent_path))
E = ent["minecraft:entity"]; comps = E["components"]; groups = E["component_groups"]; events = E["events"]
VANILLA_FREE = ["minecraft:behavior.hide", "minecraft:behavior.look_at_trading_player", "minecraft:behavior.move_indoors",
                "minecraft:behavior.move_towards_dwelling_restriction", "minecraft:behavior.pickup_items", "minecraft:behavior.random_stroll",
                "minecraft:behavior.share_items", "minecraft:behavior.trade_with_player", "minecraft:dweller"]
groups["pw:vanilla_free"] = {k: comps.pop(k) for k in VANILLA_FREE if k in comps}
assert len(groups["pw:vanilla_free"]) == len(VANILLA_FREE), sorted(groups["pw:vanilla_free"])
# the pathfinder never crosses a chimney flue (his 15:27: civs clip through the chimney walls / enter the flue as a ladder)
flues = sorted(p.stem.replace("pw_", "pw:", 1) for p in (DST / "blocks").glob("pw_flue_*.json"))
assert len(flues) == 53, len(flues)
comps["minecraft:navigation.walk"]["blocks_to_avoid"] = [{"name": f} for f in flues]
# vanilla villagers (a vanilla village, an egg) keep today's behaviour: the group rides on spawn / birth
for evn in ("minecraft:entity_spawned", "minecraft:entity_born"):
    seq = events[evn]["sequence"]
    seq.append({"add": {"component_groups": ["pw:vanilla_free"]}})
# the civ states
groups["pw:civ"] = {"minecraft:type_family": {"family": ["villager", "peasant", "unskilled", "mob", "pw_civ"]}, "minecraft:variant": {"value": 0}}
groups["pw:civ_stand"] = {"minecraft:behavior.random_look_around": {"priority": 10, "look_distance": 8, "probability": 0.02, "min_look_time": 20, "max_look_time": 60}}
groups["pw:civ_idle"] = {"minecraft:behavior.random_look_around": {"priority": 10, "look_distance": 8, "probability": 0.02, "min_look_time": 20, "max_look_time": 60},
                         "minecraft:behavior.random_stroll": {"priority": 11, "speed_multiplier": 0.55, "xz_dist": 4, "y_dist": 1, "interval": 200}}
groups["pw:civ_home"] = {"minecraft:behavior.random_look_around": {"priority": 10, "look_distance": 6, "probability": 0.01, "min_look_time": 40, "max_look_time": 100}}
VANILLA_GROUPS = ["pw:vanilla_free", "adult", "baby", "basic_schedule", "jobless_schedule", "child_schedule", "farmer_schedule", "fisher_schedule", "librarian_schedule",
                  "work_schedule", "work_schedule_farmer", "work_schedule_fisher", "work_schedule_librarian", "work_schedule_villager",
                  "bed_schedule_villager", "gather_schedule_villager", "home_schedule_villager", "play_schedule_villager", "wander_schedule_villager",
                  "job_specific_goals", "behavior_peasant", "behavior_non_peasant", "make_and_receive_love", "trade_components", "trade_resupply_component_group",
                  "armorer", "butcher", "cartographer", "cleric", "farmer", "fisherman", "fletcher", "leatherworker", "librarian", "mason", "nitwit",
                  "shepherd", "toolsmith", "weaponsmith", "minecraft:celebrate"]
for g in VANILLA_GROUPS:
    assert g in groups, g
STATES = ["pw:civ_stand", "pw:civ_idle", "pw:civ_home"]
events["pw:civ_on"] = {"sequence": [{"remove": {"component_groups": VANILLA_GROUPS}}, {"add": {"component_groups": ["pw:civ", "unskilled", "adult", "pw:civ_stand"]}}]}
# 'adult' carries the preferred_path costs (roads cheap) and nothing else of vanilla's AI; it is kept
events["pw:civ_on"]["sequence"][0]["remove"]["component_groups"] = [g for g in VANILLA_GROUPS if g != "adult"]
events["pw:civ_walk"] = {"remove": {"component_groups": STATES}}
for st_ in STATES:
    events[st_] = {"sequence": [{"remove": {"component_groups": [x for x in STATES if x != st_]}}, {"add": {"component_groups": [st_]}}]}
write(ent_path, json.dumps(ent, indent=2))
LOG.append("villager_v2: vanilla_free group, flue blocks_to_avoid, civ states + events")
print("STAGE 3a written (entity)")

# ---------------------------------------------------------------------------------------------- 3b. CIVS: the scripts
clock = read("scripts/pw_civ_clock.js")
CIV_HELPERS = r'''
// ------------------------------------------------------------------------------------------------ CIV STATES (1004b, his 15:27 / 17:59)
// A civ (his word) never runs vanilla's villager AI: at its first beat (and once at every spawn) pw:civ_on strips the
// trade / stroll / dwelling / breeding / job groups (children can never take a profession; no emerald screen), then the
// clock owns every move: WALK (a lead), STAND (at a station, a counter, a site: still, looking about), IDLE (the square
// or the commons at dusk: a few short steps), HOME (inside the house at night: still). Purpose behind the inaction.
const CIV_STATES = ["stand", "idle", "home"];
function civOn(v) {
  try { if (v.hasTag("civ:v220")) return false; v.triggerEvent("pw:civ_on"); v.addTag("civ:v220"); v.addTag("civ:state:stand"); return true; } catch { return false; }
}
function civState(v, kind) {
  if (!CIV_STATES.includes(kind)) kind = "stand";
  try {
    if (v.hasTag(`civ:state:${kind}`)) return false;
    for (const t of v.getTags()) if (t.startsWith("civ:state:")) v.removeTag(t);
    v.addTag(`civ:state:${kind}`);
    v.triggerEvent(`pw:civ_${kind}`);
    return true;
  } catch { return false; }
}
/** the cell just inside a building's door (the night place; a keeper's fallback station) */
function insideDoor(b, def) {
  const [sx, , sz] = def.size;
  const door = def.door || [0, 0, Math.floor(sz / 2)];
  const [ox, oz] = rotXZ(2, door[2], sx, sz, b.rot);
  return { x: b.x + ox + 0.5, y: b.y + def.datum_y, z: b.z + oz + 0.5 };
}
'''
clock = rep(clock, "// C2.1 (D-C541 / D-C542): the walkers' module reads the clock through these; the SCHEDULE below sends everyone somewhere",
            CIV_HELPERS + "\n// C2.1 (D-C541 / D-C542): the walkers' module reads the clock through these; the SCHEDULE below sends everyone somewhere",
            "civ state helpers")
# every spawned body is a civ from its first tick
clock = rep(clock, "      if (st) v.addTag(`civ:settlement:${st.id}`);\n      b.villagers.push(v.id);",
            "      if (st) v.addTag(`civ:settlement:${st.id}`);\n      civOn(v);\n      b.villagers.push(v.id);", "civOn at move-in")
clock = rep(clock, "      if (!BODY_POSTS.includes(p.job)) v.addTag(\"civ:shopper\");\n      byPid.set(p.id, v); made++;",
            "      if (!BODY_POSTS.includes(p.job)) v.addTag(\"civ:shopper\");\n      civOn(v);\n      byPid.set(p.id, v); made++;", "civOn at embody")
# the schedule: goals carry their state; at the goal the civ takes it; bodies from an older pack are converted on sight
clock = rep(clock, "  if (tod >= SCHED.dusk[0] && tod < SCHED.dusk[1]) return square || front(homeB);\n  return front(homeB) || square;\n}",
            "  if (tod >= SCHED.dusk[0] && tod < SCHED.dusk[1]) { const g = square || front(homeB); return g ? { ...g, mode: \"idle\" } : null; }\n"
            "  // night: INSIDE the home (1004b: vanilla's move_indoors is gone; the civ stands in its house, still)\n"
            "  if (homeB) { const hdef = BUILDINGS[homeB.family]; if (hdef) return { ...insideDoor(homeB, hdef), mode: \"home\" }; }\n"
            "  return square ? { ...square, mode: \"idle\" } : null;\n}", "goals carry a state (dusk idle, night home)")
clock = rep(clock, "    for (const v of vs) {\n      if (v.hasTag(\"civ:keeper\")) continue;                                  // the keepers' own beat (pw_civ_shop) sends them",
            "    for (const v of vs) {\n      civOn(v);                                                              // 1004b: a body from an older pack becomes a civ on sight\n"
            "      if (v.hasTag(\"civ:keeper\")) continue;                                  // the keepers' own beat (pw_civ_shop) sends them",
            "civOn in the schedule beat")
clock = rep(clock, "      if (here <= 3) { if (WALK.walking(v)) WALK.cancel(v); continue; }\n      if (!WALK.walking(v) && sends < SENDS_PER_BEAT) { sends++; WALK.send(v, st, g); }",
            "      if (here <= 3) { if (WALK.walking(v)) WALK.cancel(v); civState(v, g.mode || \"stand\"); continue; }\n"
            "      if (!WALK.walking(v) && sends < SENDS_PER_BEAT) { sends++; WALK.send(v, st, g); }", "state at the goal")
clock = rep(clock, "      if (g.buy !== undefined && here <= 3) {                                  // C2.4: at the counter\n        const shopB = s.buildings.find((b) => b.id === g.buy), person = PEOPLE.byId(census(st), g.person);\n        if (shopB && person) buyAt(s, st, v, person, shopB);\n        if (WALK.walking(v)) WALK.cancel(v);\n        continue;",
            "      if (g.buy !== undefined && here <= 3) {                                  // C2.4: at the counter\n        const shopB = s.buildings.find((b) => b.id === g.buy), person = PEOPLE.byId(census(st), g.person);\n        if (shopB && person) buyAt(s, st, v, person, shopB);\n        if (WALK.walking(v)) WALK.cancel(v);\n        civState(v, \"stand\");\n        continue;",
            "state at the counter")
# the API for the other modules
clock = rep(clock, "  arrived: (v, w) => { const s = load(); const st = s.settlements.find((x) => x.id === w.stId); if (st) st.walkArrived = (st.walkArrived || 0) + 1; },",
            "  arrived: (v, w) => { const s = load(); const st = s.settlements.find((x) => x.id === w.stId); if (st) st.walkArrived = (st.walkArrived || 0) + 1; civState(v, \"stand\"); },\n"
            "  civOn, civState, insideDoor,", "API: civOn / civState / arrived -> stand")
write("scripts/pw_civ_clock.js", clock)

walk = read("scripts/pw_civ_walk.js")
walk = rep(walk, "    if (paired) { v.triggerEvent(`pw:lead_on_${k}`); slotOf.set(v.id, k); } else v.triggerEvent(\"pw:lead_on\");",
           "    try { v.triggerEvent(\"pw:civ_walk\"); for (const t of v.getTags()) if (t.startsWith(\"civ:state:\")) v.removeTag(t); } catch { /* an older body */ }   // 1004b: walking = no stand / idle / home group\n"
           "    if (paired) { v.triggerEvent(`pw:lead_on_${k}`); slotOf.set(v.id, k); } else v.triggerEvent(\"pw:lead_on\");", "walk clears the state groups")
write("scripts/pw_civ_walk.js", walk)

shop = read("scripts/pw_civ_shop.js")
shop = rep(shop, "    b.keeper = v.id;\n    b.station = at;",
           "    try { if (API.civOn) API.civOn(v); } catch { /* left */ }   // 1004b\n    b.keeper = v.id;\n    b.station = at;", "civOn at hire")
shop = rep(shop, "    } else {\n      if (WALK.walking(v)) WALK.cancel(v);\n      try { v.addEffect(\"slowness\", 140, { amplifier: 255, showParticles: false }); } catch { /* left */ }\n    }",
           "    } else {\n      if (WALK.walking(v)) WALK.cancel(v);\n      try { if (API.civState) API.civState(v, \"stand\"); } catch { /* left */ }\n      try { v.addEffect(\"slowness\", 140, { amplifier: 255, showParticles: false }); } catch { /* left */ }\n    }",
           "keeper stands at the station")
shop = rep(shop, '''/** talking to a keeper opens the shop window (the vanilla trade screen is not used) */
world.beforeEvents.playerInteractWithEntity.subscribe((ev) => {
  const v = ev.target;
  if (!v || !v.hasTag || !v.hasTag("civ:keeper")) return;
  ev.cancel = true;
  const player = ev.player;
  const tag = v.getTags().find((t) => t.startsWith("civ:shop:"));
  const bid = tag ? Number(tag.slice(9)) : NaN;
  const vname = v.nameTag;
  system.run(() => { try { openShop(player, bid, vname); } catch (e) { console.warn(`[CIV-SHOP] window: ${e}`); } });
});''', '''/** talking to a keeper opens the shop window; talking to ANY other civ opens the talk window (1004b, his 15:27: never
 *  the vanilla emerald screen) */
world.beforeEvents.playerInteractWithEntity.subscribe((ev) => {
  const v = ev.target;
  if (!v || !v.hasTag) return;
  let keeper = false, civ = false;
  try { keeper = v.hasTag("civ:keeper"); civ = keeper || v.hasTag("civ:villager"); } catch { return; }
  if (!civ) return;
  ev.cancel = true;
  const player = ev.player;
  const vname = v.nameTag;
  if (keeper) {
    const tag = v.getTags().find((t) => t.startsWith("civ:shop:"));
    const bid = tag ? Number(tag.slice(9)) : NaN;
    system.run(() => { try { openShop(player, bid, vname); } catch (e) { console.warn(`[CIV-SHOP] window: ${e}`); } });
  } else {
    system.run(() => { try { openTalk(player, v); } catch (e) { console.warn(`[CIV-SHOP] talk: ${e}`); } });
  }
});

/** the TALK window: who this civ is (the census), how they feel, what they have heard — an RPG town is investigated by talking */
export function openTalk(player, v) {
  const s = API.load();
  const tags = v.getTags();
  const stTag = tags.find((t) => t.startsWith("civ:settlement:")), pTag = tags.find((t) => t.startsWith("civ:person:"));
  const st = stTag ? s.settlements.find((x) => x.id === Number(stTag.slice(15))) : null;
  const P = st && st.people, person = P && pTag ? API.PEOPLE.byId(P, Number(pTag.slice(11))) : null;
  const day = Math.floor(s.simDays);
  const name = v.nameTag || (person ? person.name : "a civ");
  const form = new ActionFormData().title(name);
  const lines = [];
  if (person) {
    const stage = API.PEOPLE.stage(person, day);
    const home = person.home ? s.buildings.find((b) => b.id === person.home) : null;
    const job = person.job ? s.buildings.find((b) => b.id === person.job) : null;
    const trade = typeof person.job === "string" ? person.job : (job ? `${API.short(job)} #${job.id}` : null);
    lines.push(`${stage === "child" ? "A child" : stage === "apprentice" ? "An apprentice" : stage === "elder" ? "An elder" : "A grown civ"} of ${st.name}${home ? `, of the house #${home.id} ${API.short(home)}` : ""}.`);
    lines.push(trade ? `Works as: ${trade}${person.trade ? ` (${API.PEOPLE.rankOf(person, person.trade)})` : ""}.` : (stage === "child" ? "Too young to work." : "Without a trade."));
    if (person.spouse) { const sp = API.PEOPLE.byId(P, person.spouse); if (sp) lines.push(`Married to ${sp.name}.`); }
    if (person.kids && person.kids.length) lines.push(`${person.kids.length} child${person.kids.length === 1 ? "" : "ren"}.`);
    const mood = person.mood ?? 50;
    lines.push(`Mood: ${mood >= 75 ? "content" : mood >= 50 ? "fair" : mood >= 30 ? "low" : "miserable"}.`);
    const g = API.PEOPLE.greeting(P, person, day);
    lines.push(g.tier === "friend" ? "Greets you as a friend." : g.tier === "customer" ? "Knows your face." : "Does not know you.");
    if (g.rumour) lines.push(`"${g.rumour}"`);
    else if (g.tier === "stranger") lines.push(`"${["Good day.", "Mind the street.", "Have you been to the square?", "Busy, busy."][Math.floor(Math.random() * 4)]}"`);
    try { API.PEOPLE.playerContact(person, 1); } catch { /* left */ }
  } else {
    lines.push(st ? `A civ of ${st.name}.` : "A civ.");
  }
  const state = tags.find((t) => t.startsWith("civ:state:"));
  if (state) lines.push(`(${state.slice(10) === "home" ? "at home" : state.slice(10) === "idle" ? "taking the air" : "at work or on watch"})`);
  form.body(lines.join("\\n"));
  form.button("Leave");
  form.show(player).then(() => {});
}''', "talk window for every civ")
write("scripts/pw_civ_shop.js", shop)
print("STAGE 3b written (civ scripts)")
clock = read("scripts/pw_civ_clock.js")
clock = rep(clock, "SHOP.initShops({ load, save, footprint, rotXZ, short, ECON, BUILDINGS, VILLAGER_ID,",
            "SHOP.initShops({ load, save, footprint, rotXZ, short, ECON, BUILDINGS, VILLAGER_ID, PEOPLE, civOn, civState,", "SHOP API: PEOPLE + civ states")
write("scripts/pw_civ_clock.js", clock)
print("STAGE 3c written")

# ---------------------------------------------------------------------------------------------- 4. VINES: the touch shake is off (his 17:38), the wind sway stays
vine = read("scripts/pw_vine.js")
vine = rep(vine, "      if (!inVine(p)) continue;\n      touchAround(p);",
           "      if (!inVine(p)) continue;\n      if (VINE_TOUCH_RUSTLE) touchAround(p);   // 1004b (his 17:38): no quick shake on contact; the wind sway (RP flipbooks) stays",
           "vine touch rustle gated")
vine = rep(vine, "const RUSTLE_TICKS = 40;        // 2 s of rustle after the last touch",
           "const VINE_TOUCH_RUSTLE = false;  // 1004b: his ruling — off\nconst RUSTLE_TICKS = 40;        // 2 s of rustle after the last touch", "VINE_TOUCH_RUSTLE flag")
write("scripts/pw_vine.js", vine)

# ---------------------------------------------------------------------------------------------- 5. LECTERN: the town hall's lectern faces the speaker (east in the r1 frame)
LECTERN_NEW = "east"
touched = []
for f in sorted((DST / "structures/pw").glob("mvv_town_hall_*_r1.mcstructure")) + sorted((DST / "structures/pw/stages").glob("mvv_town_hall_*_r1_s*.mcstructure")):
    st = M.Structure.from_bytes(f.read_bytes())
    n = 0
    for i, (name, states, version) in enumerate(st.palette):
        if name == "minecraft:lectern" and "minecraft:cardinal_direction" in states and states["minecraft:cardinal_direction"].value == "west":
            states["minecraft:cardinal_direction"] = M.s(LECTERN_NEW)
            n += 1
    if n:
        f.write_bytes(st.to_bytes())
        touched.append(f.name)
assert len(touched) >= 4, touched
LOG.append(f"lectern -> {LECTERN_NEW} in {len(touched)} structures ({', '.join(touched)})")
bld = read("scripts/pw_civ_buildings.js")
MARK = "export const CIV_BUILDINGS = "
head, body = bld.split(MARK, 1)
body = body.strip()
assert body.endswith(";")
tbl = json.loads(body[:-1])
n_dir = 0
for key, d in tbl.items():
    if "town_hall" not in key:
        continue
    for e in d.get("dir", []):
        if e[3] == "minecraft:lectern" and e[4].get("minecraft:cardinal_direction") == "west":
            e[4]["minecraft:cardinal_direction"] = LECTERN_NEW
            n_dir += 1
assert n_dir == 4, n_dir
write("scripts/pw_civ_buildings.js", head + MARK + json.dumps(tbl, separators=(",", ":")) + ";")
LOG.append(f"lectern dir entries -> east ({n_dir}, town halls only)")
print("STAGE 4-5 written (vines, lectern)")

# ---------------------------------------------------------------------------------------------- 6. FALLING TREES (D-C563 / D-C565, research R6)
shutil.copy2(SRC_JS / "pw_fall_physics.js", DST / "scripts/pw_fall_physics.js")
LOG.append("scripts/pw_fall_physics.js added")
main = read("scripts/main.js")
main = rep(main, 'templateFallingSet, templateCells, turnOffset } from "./pw_fell_rules.js";',
           'templateFallingSet, templateCells, turnOffset } from "./pw_fell_rules.js";\n'
           'import * as FALLPHYS from "./pw_fall_physics.js"; // v1.3.220 (1004b, D-C563 / D-C565): physics fall + the yaw law', "import FALLPHYS")
# 6a. the crown helper for rootless trees, before the keyframe table
main = rep(main, "// Fall-animation keyframes as [time_seconds, angle_multiplier_of_terminal]",
           "// v1.3.220 (1004b, R6 §5): the crown of a ROOTLESS (legacy BFS) tree for the resting computation — the species' leaves\n"
           "// within Chebyshev r <= maxR of the trunk top, y in [top-2, top+1]; flagged as leaves (they may crush into the ground).\n"
           "// Budgeted: <= 4 x (2 maxR + 1)^2 reads, maxR <= 3.\n"
           "function fallCrownCells(dim, stumpPos, topY, leafIds, maxR) {\n"
           "  const out = [];\n"
           "  const R = Math.max(1, Math.min(3, maxR | 0));\n"
           "  const ids = new Set(leafIds);\n"
           "  for (let dy = -2; dy <= 1; dy++) {\n"
           "    for (let dx = -R; dx <= R; dx++) for (let dz = -R; dz <= R; dz++) {\n"
           "      let b;\n"
           "      try { b = dim.getBlock({ x: stumpPos.x + dx, y: topY + dy, z: stumpPos.z + dz }); } catch { continue; }\n"
           "      if (b && ids.has(b.typeId)) out.push([stumpPos.x + dx, topY + dy, stumpPos.z + dz, 1]);\n"
           "    }\n"
           "  }\n"
           "  return out;\n"
           "}\n\n"
           "// Fall-animation keyframes as [time_seconds, angle_multiplier_of_terminal]", "fallCrownCells helper")
# 6b. constants
main = rep(main, "const REST_TICKS = 70;          // v1.3.40: 3.5s rest — outlasts the longest impact rumble (big 3.88s from t=4.60 ends 8.48s; fall 5.05 + rest 3.5 = 8.55s)",
           "const REST_TICKS = 80;          // v1.3.220: 4.0 s after the IMPACT frame (the big rumble runs 3.88 s from the impact)", "REST_TICKS 80")
# 6c. the leaf sweep follows the physics curve and ends on the impact frame
main = rep(main, "      if ((sweep.ctl && sweep.ctl.flushNow) || tau >= SWEEP_END_TICKS) target = N;\n"
                 "      else if (tau < SWEEP_START_TICKS) target = 0;\n"
                 "      else target = Math.floor(N * Math.min(1, Math.max(0, fallAngleAtTime(tau / 20, -90) / -90)));",
           "      const _swEnd = sweep.endTick || SWEEP_END_TICKS, _swT = sweep.fallT || 3.5, _swRest = sweep.restDeg || 90;   // v1.3.220\n"
           "      if ((sweep.ctl && sweep.ctl.flushNow) || tau >= _swEnd) target = N;\n"
           "      else if (tau < SWEEP_START_TICKS) target = 0;\n"
           "      else target = Math.floor(N * Math.min(1, Math.max(0, FALLPHYS.thetaAt(tau / 20, _swT, _swRest) / _swRest)));", "sweep progress = physics curve")
main = rep(main, "    try { while (consumed < N) removeOne(unprotected[consumed++]); } catch {}\n  }, FALL_DURATION_TICKS + REST_TICKS);",
           "    try { while (consumed < N) removeOne(unprotected[consumed++]); } catch {}\n  }, (sweep.endTick || FALL_DURATION_TICKS) + REST_TICKS);", "sweep safety flush on the impact clock")
# 6d. pickFallYaw: ground TOP FACE, exact ground set, the drop measured from the ground under the stump, the yaw law
main = rep(main, "  // Ground height at a sample point\n"
                 "  const groundYAt = (wx, wz) => {\n"
                 "    for (let dy = 3; dy >= -VERTICAL_SEARCH; dy--) {\n"
                 "      const p = { x: wx, y: stumpPos.y + dy, z: wz };\n"
                 "      let b;\n"
                 "      try { b = dim.getBlock(p); } catch { return stumpPos.y; }\n"
                 "      if (!b) continue;\n"
                 "      const id = b.typeId;\n"
                 "      if (id === \"minecraft:air\" ||\n"
                 "          id.endsWith(\"_leaves\") ||\n"
                 "          id.endsWith(\"_log\") ||\n"
                 "          id.endsWith(\"_stem\") ||\n"
                 "          id.includes(\"sapling\") ||\n"
                 "          id.includes(\"grass\") ||\n"
                 "          id.includes(\"fern\") ||\n"
                 "          id.includes(\"flower\") ||\n"
                 "          id.includes(\"vine\") ||\n"
                 "          id.includes(\"tallgrass\")) continue;\n"
                 "      return stumpPos.y + dy;\n"
                 "    }\n"
                 "    return stumpPos.y - VERTICAL_SEARCH;\n"
                 "  };",
           "  // Ground TOP FACE at a sample point. v1.3.220 (R6 A1 / A2): the old reader returned the ground BLOCK's y and skipped\n"
           "  // every id containing \"grass\" — grass_block included — so a lawn read two blocks low. Tree parts, plants, water and\n"
           "  // snow are passable (pw_fall_physics.isFallPassable); everything else is ground.\n"
           "  const groundYAt = (wx, wz) => {\n"
           "    for (let dy = 3; dy >= -VERTICAL_SEARCH; dy--) {\n"
           "      const p = { x: wx, y: stumpPos.y + dy, z: wz };\n"
           "      let b;\n"
           "      try { b = dim.getBlock(p); } catch { return stumpPos.y; }\n"
           "      if (!b) continue;\n"
           "      if (FALLPHYS.isFallPassable(b.typeId)) continue;\n"
           "      return stumpPos.y + dy + 1;\n"
           "    }\n"
           "    return stumpPos.y - VERTICAL_SEARCH;\n"
           "  };", "pickFallYaw groundYAt = top face, exact ground set")
main = rep(main, "  const stumpGroundY = stumpPos.y;\n",
           "  // v1.3.220 (R-54): the drop is measured from the GROUND under the stump, not from the log's y. With the old reference every\n"
           "  // direction read a 2-4 block \"drop\" on flat ground, so the slope mode always won and his F7 flat-ground rule (the heavy\n"
           "  // side, else away from the chopper; v1.3.206) never ran — flat falls went to the first sample (east) or the least obstacles.\n"
           "  let stumpGroundY = stumpPos.y;\n"
           "  try { const _g0 = groundYAt(stumpPos.x, stumpPos.z); if (typeof _g0 === \"number\") stumpGroundY = _g0; } catch { /* keep */ }\n", "stumpGroundY = the ground under the stump")
main = rep(main, "    const yr = forcedYawDeg * Math.PI / 180;\n    const fdx = -Math.cos(yr), fdz = Math.sin(yr);",
           "    const _fd = FALLPHYS.fallDirOfYaw(forcedYawDeg);   // v1.3.220 D-C565: the yaw law\n    const fdx = _fd.x, fdz = _fd.z;", "forced dir via the yaw law")
main = rep(main, "  let bestYaw = Math.atan2(awayZ, -awayX) * 180 / Math.PI; // fallback: straight away",
           "  let bestYaw = FALLPHYS.yawOfFallDir(awayX, awayZ); // fallback: straight away (v1.3.220: the yaw law)", "fallback yaw via the law")
main = rep(main, "      bestYaw = Math.atan2(s.dirZ, -s.dirX) * 180 / Math.PI;",
           "      bestYaw = FALLPHYS.yawOfFallDir(s.dirX, s.dirZ);   // v1.3.220 D-C565", "best yaw via the law")
main = rep(main, "          forcedYaw = Math.atan2(vz / vl, -(vx / vl)) * 180 / Math.PI;",
           "          forcedYaw = FALLPHYS.yawOfFallDir(vx / vl, vz / vl);   // v1.3.220 D-C565: the yaw law", "2x2 forced yaw via the law")
# 6e. isFallCollider: grass_block is ground
main = rep(main, "  if (id.includes(\"sapling\") || id.includes(\"grass\") ||\n      id.includes(\"fern\") || id.includes(\"flower\") ||",
           "  if (id.includes(\"sapling\") || (id.includes(\"grass\") && !id.includes(\"grass_block\")) ||   // v1.3.220: grass_block is ground (R6 A2)\n      id.includes(\"fern\") || id.includes(\"flower\") ||", "isFallCollider grass_block")
# 6f. the fall direction + the physics clock variables
main = rep(main, "        const _swYawRad = pick.yaw * Math.PI / 180;\n        const swFx = -Math.cos(_swYawRad);\n        const swFz =  Math.sin(_swYawRad);\n        const fellTick = system.currentTick;\n        const sweepCtl = { flushNow: false };",
           "        const _swDir = FALLPHYS.fallDirOfYaw(pick.yaw);   // v1.3.220 D-C565: the yaw law (FALL_Z_SIGN)\n"
           "        const swFx = _swDir.x;\n        const swFz = _swDir.z;\n        const fellTick = system.currentTick;\n        const sweepCtl = { flushNow: false };\n"
           "        let fallT = 3.5, impTick = 92, restDegPos = 90;   // v1.3.220: set by the physics block below; read by the +1t sweep and the cleanup", "swFx/swFz via the law + clock vars")
main = rep(main, "              { sx: stump.x, sz: stump.z, fx: swFx, fz: swFz, fellTick, ctl: sweepCtl }, exactLeaves));",
           "              { sx: stump.x, sz: stump.z, fx: swFx, fz: swFz, fellTick, ctl: sweepCtl, fallT, endTick: impTick, restDeg: restDegPos }, exactLeaves));", "sweep gets the physics clock")
# 6g. the resting angle from the tree's own cells
main = rep(main, "          // v1.3.40: terminal angle from first-contact terrain profile (no tip clipping)\n"
                 "          const fallAngle = computeFallAngle(dimension, stump, pick.yaw, trunkH, pick.groundYAt);\n",
           "          // v1.3.220 (1004b, D-C563 / R6): the RESTING ANGLE from the tree's own cells (logs above the cut + its leaves)\n"
           "          // rotated about the stump top's LEADING EDGE — the drawn model's pivot (pivotRadius) — against the real ground\n"
           "          // (top faces; grass_block is ground; leaves may crush 0.6 into it). Flat ground ~85-96°, downhill more, a bank less.\n"
           "          // Replaces computeFallAngle (trunk axis only, ground read a block low, pivot a block high; R6 Appendix A).\n"
           "          const _carbon = _ftTpl !== undefined;\n"
           "          const _ftR = FALLPHYS.pivotRadius(SPECIES[speciesIdx].key, speciesTier, trunkWidth, _carbon);\n"
           "          const _pivot = { x: spawnX + swFx * _ftR, y: stump.y, z: spawnZ + swFz * _ftR };\n"
           "          let fallAngle = -90, _restInfo = null;\n"
           "          try {\n"
           "            const _cells = logs.map((p) => [p.x, p.y, p.z]);\n"
           "            if (exactLeaves && exactLeaves.length) {\n"
           "              // the lowest and the highest leaf of every column decide contact (below / beyond 90°); the rest never do\n"
           "              const _lo = new Map(), _hi = new Map();\n"
           "              for (const p of exactLeaves) {\n"
           "                const k = `${p.x},${p.z}`;\n"
           "                const lo = _lo.get(k); if (!lo || p.y < lo.y) _lo.set(k, p);\n"
           "                const hi = _hi.get(k); if (!hi || p.y > hi.y) _hi.set(k, p);\n"
           "              }\n"
           "              for (const p of _lo.values()) _cells.push([p.x, p.y, p.z, 1]);\n"
           "              for (const [k, p] of _hi) if (_lo.get(k) !== p) _cells.push([p.x, p.y, p.z, 1]);\n"
           "            } else {\n"
           "              for (const c of fallCrownCells(dimension, stump, stump.y + trunkH - 1, SPECIES[speciesIdx].leaves, Math.max(2, _csMaxR))) _cells.push(c);\n"
           "            }\n"
           "            let _reads = 0;\n"
           "            const _gDim = dimension;\n"
           "            const _ground = FALLPHYS.makeGroundReader((x, y, z) => {\n"
           "              if (++_reads > 3000) return \"minecraft:stone\";             // budget (L-PERF-2): beyond it the scan top is ground\n"
           "              let b; try { b = _gDim.getBlock({ x, y, z }); } catch { return null; }\n"
           "              return b ? b.typeId : null;\n"
           "            }, stump.y + 4, stump.y - 16);\n"
           "            const _t0 = Date.now();\n"
           "            _restInfo = FALLPHYS.restAngle(_cells, _pivot, { x: swFx, z: swFz }, _ground, { fine: 1 });\n"
           "            fallAngle = Math.max(-135, Math.min(-1, -Math.round(_restInfo.deg)));\n"
           "            log(`[FALL] rest ${_restInfo.deg}° (${_cells.length} cells, ${_restInfo.tested} tests, ${_reads} reads, ${Date.now() - _t0}ms) pivot r=${_ftR} contact=${_restInfo.contact ? _restInfo.contact.slice(0, 3).join(\",\") : \"none\"}`);\n"
           "          } catch (e) { log(`[FALL] rest err: ${e} -> -90`); fallAngle = -90; }\n"
           "          restDegPos = -fallAngle;\n"
           "          fallT = FALLPHYS.fallDuration(trunkH);\n"
           "          impTick = Math.max(10, Math.round(20 * FALLPHYS.impactTime(fallT, restDegPos)));\n"
           "          const fallTTenths = Math.max(8, Math.min(80, Math.round(fallT * 10)));\n", "resting angle from cells")
main = rep(main, "            const summary = `${SPECIES[speciesIdx].key} ${tn} trunk ${trunkWidth}x${trunkWidth} h=${trunkH} logs=${logs.length} | dir yaw=${pick.yaw.toFixed(0)} angle=${fallAngle} | canopy=${canopySize} (maxR=${_csMaxR} rays=${_csRays})`;",
           "            const summary = `${SPECIES[speciesIdx].key} ${tn} trunk ${trunkWidth}x${trunkWidth} h=${trunkH} logs=${logs.length} | dir yaw=${pick.yaw.toFixed(0)} ${FALLPHYS.compassName(swFx, swFz)} rest=${fallAngle} T=${fallT.toFixed(2)}s imp=${(impTick / 20).toFixed(2)}s | canopy=${canopySize} (maxR=${_csMaxR} rays=${_csRays})`;", "[FELL] summary: compass + timing")
main = rep(main, "          try { ent.setProperty(\"ft:fall_angle\", fallAngle); }\n          catch (e) { log(`setProp fall_angle err: ${e}`); }",
           "          try { ent.setProperty(\"ft:fall_angle\", Math.max(-135, Math.min(-60, fallAngle))); }   // v1.3.220: legacy range; the renderer reads rest_angle + fall_t\n          catch (e) { log(`setProp fall_angle err: ${e}`); }", "fall_angle clamped to its range")
main = rep(main, "          try { ent.setProperty(\"ft:rest_angle\", fallAngle); }\n          catch (e) { log(`setProp rest_angle err: ${e}`); }",
           "          try { ent.setProperty(\"ft:rest_angle\", fallAngle); }\n          catch (e) { log(`setProp rest_angle err: ${e}`); }\n"
           "          try { ent.setProperty(\"ft:fall_t\", fallTTenths); }   // v1.3.220: the fall duration (tenths of a second) for the RP's curve\n          catch (e) { log(`setProp fall_t err: ${e}`); }", "ft:fall_t set")
# 6h. the impact cue on the impact frame; fall_stopped on the impact frame
main = rep(main, "              try { impDim.playSound(impactSound, { x: impX, y: impY, z: impZ }); log(`impact cue: ${impactSound} @82t (peak@92t)`); }\n"
                 "              catch (e) { log(`impact cue err: ${e}`); }\n"
                 "            }, 82);",
           "              try { impDim.playSound(impactSound, { x: impX, y: impY, z: impZ }); log(`impact cue: ${impactSound} @${Math.max(1, impTick - 10)}t (peak@${impTick}t)`); }\n"
           "              catch (e) { log(`impact cue err: ${e}`); }\n"
           "            }, Math.max(1, impTick - 10));   // v1.3.220: the samples peak at +0.5 s -> fire 10 ticks before the impact frame\n"
           "            // v1.3.220: the controller leaves the fall state ON the impact frame (the curve is clamped at rest from here on)\n"
           "            system.runTimeout(() => { try { if (ent && ent.isValid && !pinStopped) ent.setProperty(\"ft:fall_stopped\", 1); } catch { /* gone */ } }, impTick);", "impact cue + fall_stopped on the impact frame")
# 6i. shed bursts, pin, trails, impact effects, cleanup on the physics clock
main = rep(main, "                const delay = Math.floor(FALL_DURATION_TICKS * frac);", "                const delay = Math.floor(impTick * frac);   // v1.3.220", "shed bursts on the impact clock")
main = rep(main, "          const pinFx = -Math.cos(pinYawRad);\n          const pinFz =  Math.sin(pinYawRad);",
           "          const _pinDir = FALLPHYS.fallDirOfYaw(pinRotY);   // v1.3.220 D-C565\n          const pinFx = _pinDir.x;\n          const pinFz = _pinDir.z;", "pin dir via the law")
main = rep(main, "              if (elapsed >= 5.05) {  // v1.3.47: was 5.88 — STALE consumer from the",
           "              if (elapsed * 20 >= impTick + 2) {  // v1.3.220: the impact frame (was the fixed 5.05 s). v1.3.47: was 5.88 — STALE consumer from the", "pin ends on the impact frame")
main = rep(main, "              const curAngleDeg = fallAngleAtTime(elapsed, fallAngle);",
           "              const curAngleDeg = -FALLPHYS.thetaAt(elapsed, fallT, -fallAngle);   // v1.3.220: the physics curve", "pin angle = physics curve")
main = rep(main, "              for (let r = 2; r <= trunkH + 1; r++) {\n"
                 "                const px = pinX + pinFx * sinA * r;\n"
                 "                const py = pinY + cosA * r;\n"
                 "                const pz = pinZ + pinFz * sinA * r;",
           "              for (let r = 2; r <= trunkH + 1; r++) {\n"
           "                // v1.3.220: the trunk axis hinged at the leading-edge pivot (R6 A7: the old origin was a block high)\n"
           "                const _along = -_ftR * cosA + r * sinA, _up = _ftR * sinA + r * cosA;\n"
           "                const px = _pivot.x + pinFx * _along;\n"
           "                const py = _pivot.y + _up;\n"
           "                const pz = _pivot.z + pinFz * _along;", "pin samples from the edge pivot")
main = rep(main, "          const yawRad = ent.getRotation().y * Math.PI / 180;\n          const fx = -Math.cos(yawRad);\n          const fz =  Math.sin(yawRad);",
           "          const _fxDir = FALLPHYS.fallDirOfYaw(ent.getRotation().y);   // v1.3.220 D-C565\n          const fx = _fxDir.x;\n          const fz = _fxDir.z;", "particle dir via the law")
main = rep(main, "                const angleRad = phase.angleDeg * Math.PI / 180;\n                const canopyDist = trunkH - 1;",
           "                const angleRad = FALLPHYS.thetaAt(impTick * phase.tFrac / 20, fallT, -fallAngle) * Math.PI / 180;   // v1.3.220: where the crown really is\n                const canopyDist = trunkH - 1;", "trail angle from the curve")
main = rep(main, "            }, Math.floor(FALL_DURATION_TICKS * phase.tFrac));", "            }, Math.floor(impTick * phase.tFrac));   // v1.3.220", "trail phases on the impact clock")
main = rep(main, "          }, Math.floor(FALL_DURATION_TICKS * 0.92));", "          }, impTick);   // v1.3.220: the impact frame", "impact effects on the impact frame")
main = rep(main, "        }, FALL_DURATION_TICKS + REST_TICKS + DESPAWN_BUFFER_TICKS);", "        }, impTick + REST_TICKS + DESPAWN_BUFFER_TICKS);   // v1.3.220", "cleanup on the impact clock")
# 6j. two pre-existing lint errors (shipped in 219): _slabQualify used an undefined `dim`; a duplicate stats key
main = rep(main, "function _slabQualify(x, z, surf) {", "function _slabQualify(x, z, surf, dim) {   // v1.3.220: dim was undefined here (lint)", "_slabQualify dim param")
main = rep(main, "      const q = _slabQualify(x, z, surf);", "      const q = _slabQualify(x, z, surf, dim);", "_slabQualify call 1")
main = rep(main, "      if (_slabQualify(x, z, surfG)) continue;", "      if (_slabQualify(x, z, surfG, dim)) continue;", "_slabQualify call 2")
main = rep(main, "        try { q = _slabQualify(nx, nz, surf); }", "        try { q = _slabQualify(nx, nz, surf, dim); }", "_slabQualify call 3")
main = rep(main, "vegSaved:0, vegLift:0", "vegLift:0", "duplicate vegSaved key")
write("scripts/main.js", main)
# 6k. the entity property
ent = json.loads(read("entities/falling_tree.json"))
props = ent["minecraft:entity"]["description"]["properties"]
assert "ft:fall_t" not in props
props["ft:fall_t"] = {"type": "int", "range": [8, 80], "default": 35, "client_sync": True}
write("entities/falling_tree.json", json.dumps(ent, indent=1))
LOG.append("entities/falling_tree.json: ft:fall_t [8,80]")
print("STAGE 6 written (falling trees)")

# ---------------------------------------------------------------------------------------------- 7. BIRCH TEMPLATES v2 (his 15:27 "incomplete and broken"; D-C566)
import importlib  # noqa: E402
_saved_argv = sys.argv
sys.argv = ["tree_gen.py", "birch"]
TG = importlib.import_module("tree_gen")
sys.argv = _saved_argv
n_birch, leaf_tot = 0, {"young": 0, "mature": 0, "old": 0}
for age in ("young", "mature", "old"):
    for idx in range(TG.PER_AGE):
        st, info, trunk, leaves, _ = TG.build("birch", age, idx)
        (DST / "structures/pw/trees" / f"birch_{age}_{idx:02d}.mcstructure").write_bytes(st.to_bytes())
        n_birch += 1
        leaf_tot[age] += info["leaves"]
assert n_birch == 72, n_birch
LOG.append(f"birch templates v2: 72 regenerated (leaves/age avg young {leaf_tot['young'] // 24}, mature {leaf_tot['mature'] // 24}, old {leaf_tot['old'] // 24})")
print("STAGE 7 written (birch templates v2)")
print("\n".join(f"  ok  {w}" for w in LOG[-12:]))

# ---------------------------------------------------------------------------------------------- 8. CIVS AT HALF SPEED (his 19:35) — the watch on duty stays brisk
ent = json.loads(read("entities/villager_v2.json"))
E = ent["minecraft:entity"]
assert E["components"]["minecraft:movement"]["value"] == 0.5
E["components"]["minecraft:movement"]["value"] = 0.25
n_lead_mv = 0
for g, comp in E["component_groups"].items():
    if (g == "pw:lead" or g.startswith("pw:lead_")) and "minecraft:movement" in comp:
        del comp["minecraft:movement"]
        n_lead_mv += 1
assert n_lead_mv == 49, n_lead_mv
assert "pw:civ_brisk" not in E["component_groups"]
E["component_groups"]["pw:civ_brisk"] = {"minecraft:movement": {"value": 0.5}}
assert "pw:brisk_on" not in E["events"]
E["events"]["pw:brisk_on"] = {"add": {"component_groups": ["pw:civ_brisk"]}}
E["events"]["pw:brisk_off"] = {"remove": {"component_groups": ["pw:civ_brisk"]}}
write("entities/villager_v2.json", json.dumps(ent, indent=1))
LOG.append("villager_v2: movement 0.5 -> 0.25 (lead groups no longer set it: 49 removed); pw:civ_brisk 0.5 + brisk_on/off events")
watch = read("scripts/pw_civ_watch.js")
watch = rep(watch, '        else { if (w) { state.delete(v.id); v.removeTag("civ:watching"); } continue; }',
            '        else { if (w) { state.delete(v.id); v.removeTag("civ:watching"); try { v.triggerEvent("pw:brisk_off"); } catch { /* left */ } } continue; }   // 1.3.220: back to the civ pace',
            "watch off duty -> brisk_off")
watch = rep(watch, '      if (!v.hasTag("civ:watching")) { v.addTag("civ:watching"); try { v.addEffect("resistance", 400, { amplifier: 1, showParticles: false }); } catch { /* left */ } }',
            '      if (!v.hasTag("civ:watching")) { v.addTag("civ:watching"); try { v.addEffect("resistance", 400, { amplifier: 1, showParticles: false }); } catch { /* left */ } try { v.triggerEvent("pw:brisk_on"); } catch { /* left */ } }   // 1.3.220 (his 19:35): civs walk at half speed; the watch on duty keeps the old pace',
            "watch on duty -> brisk_on")
write("scripts/pw_civ_watch.js", watch)
m = json.loads(read("manifest.json"))
m["header"]["description"] = m["header"]["description"].replace("CIVS: every civ opens our window", "CIVS walk at half speed (the watch stays brisk); every civ opens our window")[:1200]
write("manifest.json", json.dumps(m, indent=2))
print("STAGE 8 written (half speed)")

# ---------------------------------------------------------------------------------------------- 9. PACE: the civ speed is tunable in-game (gate 220 #1: arrivals per leg fell 69 % -> 33 % at half speed)
ent = json.loads(read("entities/villager_v2.json"))
E = ent["minecraft:entity"]
PACES = {"20": 0.2, "35": 0.35, "50": 0.5}          # 25 = the base (half speed, his 19:35)
for k, v in PACES.items():
    assert f"pw:pace_{k}" not in E["component_groups"]
    E["component_groups"][f"pw:pace_{k}"] = {"minecraft:movement": {"value": v}}
all_pace = [f"pw:pace_{k}" for k in PACES]
for k in list(PACES) + ["25"]:
    ev = {"remove": {"component_groups": [g for g in all_pace if g != f"pw:pace_{k}"]}}
    if k != "25":
        ev["add"] = {"component_groups": [f"pw:pace_{k}"]}
    assert f"pw:pace_{k}" not in E["events"]
    E["events"][f"pw:pace_{k}"] = ev
write("entities/villager_v2.json", json.dumps(ent, indent=1))
LOG.append("villager_v2: pace groups 20/35/50 (+ 25 = base) and pw:pace_* events")
clock = read("scripts/pw_civ_clock.js")
clock = rep(clock, "function civOn(v) {\n  try { if (v.hasTag(\"civ:v220\")) return false; v.triggerEvent(\"pw:civ_on\"); v.addTag(\"civ:v220\"); v.addTag(\"civ:state:stand\"); return true; } catch { return false; }\n}",
            "const PACES = [20, 25, 35, 50];                                   // movement 0.20 / 0.25 (base, half speed) / 0.35 / 0.50\n"
            "function applyPace(v, pace) {\n"
            "  try { v.triggerEvent(`pw:pace_${PACES.includes(pace) ? pace : 25}`); if (v.hasTag(\"civ:watching\")) { v.triggerEvent(\"pw:brisk_off\"); v.triggerEvent(\"pw:brisk_on\"); } } catch { /* left */ }\n"
            "}\n"
            "function civOn(v) {\n"
            "  try { if (v.hasTag(\"civ:v220\")) return false; v.triggerEvent(\"pw:civ_on\"); v.addTag(\"civ:v220\"); v.addTag(\"civ:state:stand\"); const pc = load().pace; if (pc && pc !== 25) applyPace(v, pc); return true; } catch { return false; }\n"
            "}", "applyPace + civOn applies the stored pace")
clock = rep(clock, '  if (cmd === "pause" || cmd === "resume") { s.paused = cmd === "pause"; save(); reply(`§e[CLOCK] village clock ${s.paused ? "paused" : "running"}`); return; }',
            '  if (cmd === "pause" || cmd === "resume") { s.paused = cmd === "pause"; save(); reply(`§e[CLOCK] village clock ${s.paused ? "paused" : "running"}`); return; }\n'
            '  if (cmd === "pace") {                                            // 1004b: /scriptevent pw:clock pace 20|25|35|50 (civ walking speed x0.01; 25 = half speed, the default)\n'
            '    const pc = parseInt(a, 10);\n'
            '    if (!PACES.includes(pc)) { reply(`§c[CLOCK] usage: pace <20|25|35|50>  (now ${s.pace || 25}; 25 = half the vanilla villager, 50 = vanilla)`); return; }\n'
            '    s.pace = pc; save();\n'
            '    let n = 0;\n'
            '    for (const st of s.settlements) { try { for (const v of world.getDimension(st.dim).getEntities({ tags: [`civ:settlement:${st.id}`], type: VILLAGER_ID })) { applyPace(v, pc); n++; } } catch { /* unloaded */ } }\n'
            '    reply(`§e[CLOCK] civ pace ${pc} (movement 0.${pc}) applied to ${n} civ(s); new civs follow`); return;\n'
            '  }', "clock: pace command")
write("scripts/pw_civ_clock.js", clock)
print("STAGE 9 written (pace)")
