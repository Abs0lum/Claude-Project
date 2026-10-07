// pw_testrunner_p15.js — lineup "p15" LEAF PILOT (PW-TestRunner BP v0.5.0 + RP v0.4.0, D-C329..D-C344, his GO 15:27 / 15:41 / 16:07 CT 09-30).
// /scriptevent pw:test start p15 — OUR trees (BP-02's own tree features), ONE AGE PER STEP, then their leaves swapped for the pilot
// blocks: pw:pilot_<species>_leaves (pre-coloured) and ..._bt (biome colour). Each step shows TODAY's leaves beside the pilot.
// v0.4.8 (his 16:07 "use our dodecagon trunks ... each age variant"): every species-age gets its own step, grown from its own
// feature (pw:<wood>_<age>_tree_feature; elders = ..._elder_tree_feature_v2, square 2x2 trunks with branches). ONE tree is grown per
// step; the others are EXACT COPIES of it (/clone), so today and pilot are judged on the same tree shape.
// The job runs in 4 phases: clear -> grow the source trees -> copy them -> swap the leaves (a copy is always taken before any swap).
// Leaf shapes: steps to the nearest log (vanilla 'distance') + a position hash (fixed randomness, his 14:39 OK):
// touching wood -> cards only (pv 6/7), 2..band steps -> a coin flip by position, farther -> one of the six full shapes (pv 1-5, 8).
// If /place is refused, a scripted tree of the same species stands in with OUR trunk block (the log says which).
// v0.4.9 (independent check): each tree's WHOLE box is scanned (fancy branches step diagonally, so a face-only walk missed branch-tip
// leaves); ticking areas are made inside the job (absolute coordinates, chunks awaited); q9 clears every box this run planted, then
// drops the ticking areas.
import { system, world, BlockPermutation } from "@minecraft/server";

const N6 = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
const FULL_PV = [1, 2, 3, 4, 5, 8];
const CARD_PV = [6, 7];
// species -> default (mixed-age) tree feature, the leaf ids a grown tree can carry (ours first, then vanilla), the 2..band coin-flip range
export const SPECIES = {
  oak: { feature: "minecraft:oak_tree_feature", leaves: ["pw:oak_leaves", "pw:oak_leaves_a", "pw:oak_leaves_b", "pw:oak_leaves_c", "pw:oak_leaves_d",
                                                         "pw:oak_leaves_e", "pw:oak_leaves_f", "minecraft:oak_leaves"], band: 3 },
  birch: { feature: "minecraft:birch_tree_feature", leaves: ["pw:birch_leaves", "minecraft:birch_leaves"], band: 3 },
  spruce: { feature: "minecraft:spruce_tree_feature", leaves: ["pw:spruce_leaves", "minecraft:spruce_leaves"], band: 0 },
  jungle: { feature: "minecraft:jungle_tree_feature", leaves: ["pw:jungle_leaves", "minecraft:jungle_leaves"], band: 4 },
  acacia: { feature: "minecraft:acacia_tree_feature", leaves: ["pw:acacia_leaves", "minecraft:acacia_leaves"], band: 4 },
  dark_oak: { feature: "minecraft:dark_oak_tree_feature", leaves: ["pw:dark_oak_leaves", "minecraft:dark_oak_leaves"], band: 3 },
  mangrove: { feature: "minecraft:mangrove_tree_feature", leaves: ["pw:mangrove_leaves", "minecraft:mangrove_leaves"], band: 3 },
  cherry: { feature: "minecraft:cherry_tree_feature", leaves: ["pw:cherry_leaves", "minecraft:cherry_leaves"], band: 3 },
  pale_oak: { feature: "minecraft:pale_oak_tree_feature", leaves: ["pw:pale_oak_leaves", "minecraft:pale_oak_leaves"], band: 3 },
  azalea: { feature: "minecraft:azalea_tree_feature", leaves: ["minecraft:azalea_leaves"], band: 3,
            also: { "minecraft:azalea_leaves_flowered": "flowering_azalea" } },
};
// our trunks (BP-02 1.3.195): young/mature/old = dodecagons, no branches; every ELDER = square 2x2 (pw_simple_log) with branches
export const AGES = {
  oak: ["young", "mature", "old", "elder"], birch: ["young", "mature", "old"], spruce: ["young", "mature", "old", "elder"],
  jungle: ["young", "mature", "old", "elder"], dark_oak: ["elder"], pale_oak: ["elder"],
};
// the copy box around a trunk: r blocks each side (clear, copy, scan), h blocks up; every box <= 32,768 blocks (the fill / clone cap)
export const BOX = { young: { r: 8, h: 26 }, mature: { r: 8, h: 26 }, old: { r: 8, h: 28 }, elder: { r: 13, h: 36 },
                     acacia: { r: 8, h: 22 }, mangrove: { r: 8, h: 24 }, cherry: { r: 9, h: 26 }, azalea: { r: 5, h: 14 } };
// the feature + trunk block + box for one species-age (age undefined = the vanilla-id species: acacia, mangrove, cherry, azalea)
export function treeOf(sp, age) {
  if (!age) {
    const trunk = { acacia: "minecraft:acacia_log", mangrove: "minecraft:mangrove_log", cherry: "minecraft:cherry_log" }[sp] || "minecraft:oak_log";
    return { feature: SPECIES[sp].feature, trunk, ...BOX[sp] };
  }
  return { feature: age === "elder" ? `pw:${sp}_elder_tree_feature_v2` : `pw:${sp}_${age}_tree_feature`, trunk: `pw:${sp}_${age}`, ...BOX[age] };
}

// fixed randomness by position: the same cell always gets the same number (32-bit mix, no Math.random)
export function cellHash(x, y, z, salt = 0) {
  let h = (Math.imul(x | 0, 73856093) ^ Math.imul(y | 0, 19349663) ^ Math.imul(z | 0, 83492791) ^ Math.imul(salt | 0, 2654435761)) >>> 0;
  h ^= h >>> 16; h = Math.imul(h, 2246822507) >>> 0; h ^= h >>> 13; h = Math.imul(h, 3266489909) >>> 0; h ^= h >>> 16;
  return h >>> 0;
}
// the pilot shape for one leaf: d = steps to the nearest log (1 = touching), band = last coin-flip step (0 = spruce: never cards)
export function pickShape(x, y, z, d, band) {
  const h = cellHash(x, y, z);
  if (band > 0) {
    if (d === 1) return CARD_PV[h % 2];
    if (d >= 2 && d <= band && ((h >>> 8) & 1) === 1) return CARD_PV[(h >>> 9) % 2];
  }
  return FULL_PV[(h >>> 12) % FULL_PV.length];
}
// steps from each leaf to the nearest log, through leaves (vanilla leaf 'distance', capped at 7). keys "x,y,z".
export function leafDistances(logs, leaves) {
  const dist = new Map(); let front = [];
  for (const k of leaves) {
    const [x, y, z] = k.split(",").map(Number);
    if (N6.some(([a, b, c]) => logs.has(`${x + a},${y + b},${z + c}`))) { dist.set(k, 1); front.push([x, y, z]); }
  }
  for (let step = 1; front.length && step < 7; step++) {
    const next = [];
    for (const [x, y, z] of front) for (const [a, b, c] of N6) {
      const n = `${x + a},${y + b},${z + c}`;
      if (leaves.has(n) && !dist.has(n)) { dist.set(n, step + 1); next.push([x + a, y + b, z + c]); }
    }
    front = next;
  }
  for (const k of leaves) if (!dist.has(k)) dist.set(k, 7);
  return dist;
}
// a trunk: vanilla logs/wood/stems, BP-02's pw:<wood>_young|mature|old|elder (their only mark is tag:log), or anything tagged log
const PW_TRUNK = /^pw:[a-z_]+_(young|mature|old|elder)$/;
export function isLog(id, block) {
  if (/(_log|_wood|_stem|hyphae)/.test(id) || PW_TRUNK.test(id) || (id.startsWith("pw:") && /log/.test(id))) return true;
  try { return !!(block && block.hasTag && block.hasTag("log")); } catch { return false; }
}
// the volume of a fill / clone box (the game refuses more than 32,768 blocks)
export function boxVolume(r, h) { return (2 * r + 1) * (2 * r + 1) * (h + 2); }
// v0.5.2 (p16 m01-m10, the 128 vs 256 comparison): a copy of BP-02 1.3.197 main.js pwLeafLook. The look is hashed at the SOURCE tree's
// spot, so the 128 tree (the source: main.js's relook sweep would pick the same) and its 256 copies match leaf for leaf; the wood probe
// is the same Manhattan shells (1..4 steps) over this tree's own logs. Returns pw:variant 0-6 (5/6 = cards only; spruce 0-6 all full).
export const LOOK_BAND = { jungle: 4, acacia: 4, spruce: 0 };
const WOOD_SHELLS = (() => { const sh = [[], [], [], [], []];
  for (let a = -4; a <= 4; a++) for (let b = -4; b <= 4; b++) for (let c = -4; c <= 4; c++) { const d = Math.abs(a) + Math.abs(b) + Math.abs(c); if (d >= 1 && d <= 4) sh[d].push([a, b, c]); }
  return sh; })();
export function woodDistance(logs, x, y, z, maxD) {
  for (let d = 1; d <= maxD; d++) for (const [a, b, c] of WOOD_SHELLS[d]) if (logs.has(`${x + a},${y + b},${z + c}`)) return d;
  return 99;
}
export function leafLook(sp, x, y, z, d) {
  const h = cellHash(x, y, z);
  if (sp === "spruce") return (h >>> 12) % 7;
  const band = LOOK_BAND[sp] ?? 3;
  if (d === 1) return 5 + (h % 2);
  if (d >= 2 && d <= band && ((h >>> 8) & 1) === 1) return 5 + ((h >>> 9) % 2);
  return (h >>> 12) % 5;
}

// a scripted stand-in tree (only if /place is refused): OUR trunk (2x2 for elders) + a leaf crown of the species' own leaf id
function standIn(dim, base, spec) {
  const put = (x, y, z, id, alt) => { try { dim.getBlock({ x, y, z })?.setType(id); } catch { if (alt) put(x, y, z, alt); } };
  const sp = spec.sp; const L = SPECIES[sp].leaves; const leafId = L[0]; const alt = L[L.length - 1];
  const wide = spec.age === "elder" ? 2 : 1;
  const h = spec.age === "elder" ? 12 : ({ spruce: 9, jungle: 10, birch: 7, azalea: 3 }[sp] || 6) + (spec.age === "old" ? 2 : 0);
  for (let y = 0; y < h; y++) for (let a = 0; a < wide; a++) for (let b = 0; b < wide; b++) put(base.x + a, base.y + y, base.z + b, spec.trunk, "minecraft:oak_log");
  const R = spec.age === "elder" ? 4 : 2;
  for (let y = h - 3; y <= h + 1; y++) {
    const r = sp === "spruce" ? Math.max(0, Math.round((h + 1 - y) * 0.45)) : (y === h + 1 ? R - 1 : R);
    for (let dx = -r; dx <= r + wide - 1; dx++) for (let dz = -r; dz <= r + wide - 1; dz++) {
      if (dx >= 0 && dx < wide && dz >= 0 && dz < wide && y < h) continue;
      put(base.x + dx, base.y + y, base.z + dz, leafId, alt);
    }
  }
}

// a step's leaf actions run as ONE job, in 4 phases: clears -> grow sources -> copies -> leaf swaps
// tree spec: { sp, age?, dx, dz, keep?, block?, from?: [dx, dz] (copy that tree), noclear? (grove: no per-tree clearing),
//             look? (v0.5.2: block gets pw:variant by the BP-02 look rule + pw:rseed true), label? (the log's kind word) }
let leafJobBusy = false;
// every tree box a run made (for q9). v0.5.1: kept in a world dynamic property, so a relog (p16 n03) does not forget them
const PLANTED_KEY = "pw:test:planted";
const plantedMap = new Map(); let plantedLoaded = false;
const planted = {
  load() { if (plantedLoaded) return; plantedLoaded = true;
    try { const raw = world.getDynamicProperty(PLANTED_KEY); if (typeof raw === "string") for (const [k, v] of JSON.parse(raw)) plantedMap.set(k, v); } catch { /* none yet */ } },
  save() { try { world.setDynamicProperty(PLANTED_KEY, plantedMap.size ? JSON.stringify([...plantedMap.entries()]).slice(0, 30000) : undefined); } catch { /* storage refused */ } },
  set(k, v) { this.load(); plantedMap.set(k, v); this.save(); },
  delete(k) { this.load(); plantedMap.delete(k); this.save(); },
  entries() { this.load(); return plantedMap.entries(); },
};
export function plantedBoxes() { return [...planted.entries()].map(([k, v]) => ({ at: k.split(",").map(Number), ...v })); }
export function runLeafSetup(player, actions, log) {
  const origin = (() => { const l = player.location; return { x: Math.floor(l.x), y: Math.floor(l.y), z: Math.floor(l.z) }; })();   // fixed at step start
  system.runJob((function* () {
    if (leafJobBusy) log("LEAFSETUP queued: the previous step's trees are still growing - this step starts when they finish");
    while (leafJobBusy) yield;
    leafJobBusy = true;
    try {
      const specs = actions.filter((a) => a.leaftree).map((a) => ({ ...a.leaftree, ...treeOf(a.leaftree.sp, a.leaftree.age) }));
      for (const a of actions) if (a.leafarea) yield* areaJob(player, a.leafarea, log, origin);
      for (const a of actions) if (a.leafreset) yield* resetJob(player, a.leafreset, log, origin);
      for (const a of actions) if (a.leafclear) yield* clearJob(player, a.leafclear, log, origin);
      for (const a of actions) if (a.placeprobe) yield* probeJob(player, a.placeprobe, log, origin);
      for (const a of actions) if (a.leafmark) {                                  // v0.5.3: a box made by commands (p17 probe) - q9 clears it
        const m = a.leafmark; planted.set(`${origin.x + m.dx},${origin.y},${origin.z + m.dz}`, { r: m.r, h: m.h }); log(`LEAFMARK box r${m.r} h${m.h} @${origin.x + m.dx},${origin.y},${origin.z + m.dz}`);
      }
      const grown = new Map();                                                    // "dx,dz" -> { ok, how }
      for (const s of specs) if (!s.from) grown.set(`${s.dx},${s.dz}`, yield* growJob(player, s, log, origin));
      for (const s of specs) if (s.from) {
        const src = grown.get(`${s.from[0]},${s.from[1]}`);
        if (src && src.ok) grown.set(`${s.dx},${s.dz}`, yield* copyJob(player, s, src, log, origin));
        else { log(`LEAFTREE ${s.sp} ${s.age || ""}: its source never grew - growing its own`); grown.set(`${s.dx},${s.dz}`, yield* growJob(player, s, log, origin)); }
      }
      let k = 0;
      for (const s of specs) { k++; yield* swapJob(player, s, grown.get(`${s.dx},${s.dz}`), log, origin); if (specs.length > 3) log(`LEAFTREE ${k}/${specs.length} done`); }
      if (specs.length) try { player.sendMessage(`§a[PW-TEST] ${specs.length} tree${specs.length === 1 ? "" : "s"} ready`); } catch { /* player left */ }
    } finally { leafJobBusy = false; }
  })());
}
const baseOf = (origin, s) => ({ x: origin.x + s.dx, y: origin.y, z: origin.z + s.dz });
const cmdOf = (dim) => (c) => { try { return dim.runCommand(c).successCount; } catch { return -1; } };
function* waitChunk(dim, base) {
  const at = () => { try { return dim.getBlock(base); } catch { return undefined; } };
  for (let t = 0; t < 200 && !at(); t++) yield;                                  // far rows: wait for the chunk (ticking area)
  return !!at();
}
// grow one tree from its feature (or the stand-in) on a cleared, grassed pad
function* growJob(player, s, log, origin) {
  const dim = player.dimension; const base = baseOf(origin, s); const cmd = cmdOf(dim);
  if (!(yield* waitChunk(dim, base))) { log(`LEAFTREE ${s.sp} at ${base.x},${base.y},${base.z}: chunk never loaded - skipped`); return { ok: false }; }
  if (!s.noclear) cmd(`fill ${base.x - s.r} ${base.y} ${base.z - s.r} ${base.x + s.r} ${base.y + s.h} ${base.z + s.r} air`);
  cmd(`fill ${base.x - 3} ${base.y - 1} ${base.z - 3} ${base.x + 3} ${base.y - 1} ${base.z + 3} grass_block`);
  planted.set(`${base.x},${base.y},${base.z}`, { r: s.r, h: s.h });
  const r = placeTree(dim, s.feature, base, log);
  let how = r.how;
  if (!r.ok) { how = "stand-in"; standIn(dim, base, s); }
  for (let t = 0; t < 4; t++) yield;
  return { ok: true, how, base };
}
// v0.5.0 (D, his GO 18:14): grow a feature two ways and KEEP the refusal text. 1) the script API Dimension.placeFeature(id, loc, true)
// (stable in @minecraft/server 2.3.0; throws with the reason), 2) the /place feature command (its CommandError text). The first
// refusal of each (feature, way) pair is logged once per run: "PLACE REFUSED <feature> api|cmd: <reason>".
const refusalSeen = new Set();
function short(e) { return String((e && e.message) || e).replace(/\s+/g, " ").slice(0, 90); }
export function placeTree(dim, feature, base, log) {
  const say = (way, why) => { const k = `${feature}|${way}`; if (!refusalSeen.has(k)) { refusalSeen.add(k); log(`PLACE REFUSED ${way} ${feature}`); log(`PLACE REASON ${way}: ${why}`); } };
  try {
    if (typeof dim.placeFeature === "function") {
      if (dim.placeFeature(feature, { x: base.x, y: base.y, z: base.z }, true)) return { ok: true, how: "api" };
      say("api", "returned false");
    } else say("api", "placeFeature missing");
  } catch (e) { say("api", short(e)); }
  try {
    const n = dim.runCommand(`place feature ${feature} ${base.x} ${base.y} ${base.z}`).successCount;
    if (n > 0) return { ok: true, how: "place" };
    say("cmd", `successCount ${n}`);
  } catch (e) { say("cmd", short(e)); }
  return { ok: false };
}
// copy a grown tree (its whole box, ground layer included) - the copy is the SAME tree
function* copyJob(player, s, src, log, origin) {
  const dim = player.dimension; const base = baseOf(origin, s); const cmd = cmdOf(dim); const b = src.base;
  if (!(yield* waitChunk(dim, base))) { log(`LEAFTREE ${s.sp} copy at ${base.x},${base.y},${base.z}: chunk never loaded - skipped`); return { ok: false }; }
  const n = cmd(`clone ${b.x - s.r} ${b.y - 1} ${b.z - s.r} ${b.x + s.r} ${b.y + s.h} ${b.z + s.r} ${base.x - s.r} ${base.y - 1} ${base.z - s.r}`);
  if (n <= 0) { log(`LEAFTREE ${s.sp} copy refused (clone ${n}) - growing its own`); return yield* growJob(player, s, log, origin); }
  planted.set(`${base.x},${base.y},${base.z}`, { r: s.r, h: s.h });
  for (let t = 0; t < 2; t++) yield;
  return { ok: true, how: src.how === "place" || src.how === "api" ? "copy" : `copy(${src.how})`, base, src: b };
}
// walk the tree from its trunk (its own logs + leaves only), then swap its leaves for the pilot block (keep = log only)
function* swapJob(player, s, grown, log, origin) {
  if (!grown || !grown.ok) return;
  const dim = player.dimension; const base = grown.base; const S = SPECIES[s.sp];
  const kind = (x, y, z) => {
    let b; try { b = dim.getBlock({ x, y, z }); } catch { return null; }
    if (!b) return null; const id = b.typeId;
    if (id === "minecraft:air") return null;                                     // most of the box: skip the tag lookup
    if (isLog(id, b)) return "log";
    if (S.leaves.includes(id)) return s.sp;
    if (S.also && S.also[id]) return S.also[id];
    return null;
  };
  // the WHOLE box (boxes never overlap, and the box was cleared or copied whole, so everything in it is this tree): fancy branches
  // step diagonally, so a face-only walk from the trunk missed branch-tip leaf clusters (independent check B1, v0.4.9)
  const logs = new Set(), leaves = new Map(); let n = 0, edge = 0, top = -1;
  for (let y = base.y; y <= base.y + s.h; y++) for (let x = base.x - s.r; x <= base.x + s.r; x++) for (let z = base.z - s.r; z <= base.z + s.r; z++) {
    const t = kind(x, y, z);
    if (t) {
      const k = `${x},${y},${z}`; if (t === "log") logs.add(k); else leaves.set(k, t);
      if (Math.max(Math.abs(x - base.x), Math.abs(z - base.z)) === s.r) edge++;
      top = Math.max(top, y - base.y);
    }
    if (++n % 400 === 0) yield;
  }
  // one content-log line, <= 120 characters, warnings first: LEAFTREE <species> <age> <kind> [EDGE] [TOP] via <how> @x,y,z ...
  const tag = `${s.sp}${s.age ? " " + s.age : ""}`;
  const kindOf = s.label || (s.keep ? "TODAY" : (s.block ? (s.block.match(/_leaves_(\w+)$/) || [, "pilot"])[1] : "pilot"));
  const warn = `${edge ? `EDGE(${edge} on the r${s.r} rim) ` : ""}${top >= s.h ? "TOP " : ""}`;
  const at = `@${base.x},${base.y},${base.z}`;                                   // coordinates last: a long line only loses them
  if (s.keep) {
    log(`LEAFTREE ${tag} TODAY ${warn}via ${grown.how} logs ${logs.size} leaves ${leaves.size} height ${top + 1} ${at}`);
    if (s.chop) {                                                              // p16 decay test: the wood goes, the leaves stay
      let k = 0; for (const c of logs) { const [x, y, z] = c.split(",").map(Number); try { dim.getBlock({ x, y, z }).setType("minecraft:air"); k++; } catch { /* unloaded */ } }
      log(`LEAFCHOP ${tag}: ${k} logs removed, ${leaves.size} leaves left to decay ${at}`);
    }
    return;
  }
  if (s.look) {                                                                // v0.5.2: the BP-02 1.3.197 look, same leaf for leaf in every copy
    const src = grown.src || base; const ox = src.x - base.x, oy = src.y - base.y, oz = src.z - base.z;
    let cards = 0, full = 0, fails = 0, miss = ""; n = 0;
    for (const [k, sp] of leaves) {
      const [x, y, z] = k.split(",").map(Number);
      const band = LOOK_BAND[sp] ?? 3;
      const v = leafLook(sp, x + ox, y + oy, z + oz, band > 0 ? woodDistance(logs, x, y, z, Math.min(band, 4)) : 99);
      const id = s.block.replace("{sp}", sp);
      try { dim.getBlock({ x, y, z }).setPermutation(BlockPermutation.resolve(id, { "pw:variant": v, "pw:rseed": true })); v >= 5 && sp !== "spruce" ? cards++ : full++; }
      catch { fails++; miss = id; }
      if (++n % 150 === 0) yield;
    }
    log(`LEAFTREE ${tag} ${kindOf} ${warn}${fails ? `FAILED ${fails} ${miss} ` : ""}via ${grown.how} logs ${logs.size} = ${full} full + ${cards} cards ${at}`);
    return;
  }
  const dist = leafDistances(logs, new Set(leaves.keys()));
  let cards = 0, full = 0, fails = 0; n = 0;
  for (const [k, sp] of leaves) {
    const [x, y, z] = k.split(",").map(Number);
    const band = SPECIES[sp] ? SPECIES[sp].band : 3;
    const pv = pickShape(x, y, z, dist.get(k), band);
    const id = s.block ? s.block.replace("{sp}", sp) : `pw:pilot_${sp}_leaves`;
    try { dim.getBlock({ x, y, z }).setPermutation(BlockPermutation.resolve(id, { "pw:pv": pv })); pv >= 6 && pv <= 7 ? cards++ : full++; }
    catch { fails++; }
    if (++n % 150 === 0) yield;
  }
  log(`LEAFTREE ${tag} ${kindOf} ${warn}${fails ? `FAILED ${fails} (pilot packs loaded?) ` : ""}via ${grown.how} logs ${logs.size} = ${full} full + ${cards} cards ${at}`);
}

// p16 (D): /place probe — each case grows ONE feature by the script API (row z = apiZ) and ONE by the command (row z = cmdZ) on its
// own ground block, and logs the outcome of each way with the refusal text ("PROBE api|cmd <feature> on <ground>: OK|REFUSED")
export function* probeJob(player, spec, log, origin) {
  const dim = player.dimension; const cmd = cmdOf(dim);
  for (const c of spec.cases) {
    for (const way of ["api", "cmd"]) {
      const base = { x: origin.x + c.dx, y: origin.y, z: origin.z + (way === "api" ? spec.apiZ : spec.cmdZ) };
      if (!(yield* waitChunk(dim, base))) { log(`PROBE ${way} ${c.feature}: chunk never loaded`); continue; }
      cmd(`fill ${base.x - 8} ${base.y} ${base.z - 8} ${base.x + 8} ${base.y + 26} ${base.z + 8} air`);
      cmd(`fill ${base.x - 3} ${base.y - 1} ${base.z - 3} ${base.x + 3} ${base.y - 1} ${base.z + 3} ${c.ground}`);
      planted.set(`${base.x},${base.y},${base.z}`, { r: 8, h: 26 });
      let ok = false, why = "";
      try {
        if (way === "api") ok = !!dim.placeFeature(c.feature, { x: base.x, y: base.y, z: base.z }, true);
        else { const n = dim.runCommand(`place feature ${c.feature} ${base.x} ${base.y} ${base.z}`).successCount; ok = n > 0; if (!ok) why = `successCount ${n}`; }
      } catch (e) { why = short(e); }
      log(`PROBE ${way} ${c.feature} on ${c.ground.replace("minecraft:", "")}: ${ok ? "OK" : "REFUSED"}`);
      if (!ok) log(`PROBE REASON ${way}: ${why || "returned false"}`);
      for (let t = 0; t < 2; t++) yield;
    }
  }
}
// a ticking area in ABSOLUTE coordinates (box relative to the step origin), made inside the job; waits until its far corner loads
function* areaJob(player, spec, log, origin) {
  const dim = player.dimension; const [x1, y1, z1, x2, y2, z2] = spec.box;
  try { dim.runCommand(`tickingarea remove ${spec.name}`); } catch { /* none yet: fine */ }
  let ok = false;
  try { ok = dim.runCommand(`tickingarea add ${origin.x + x1} ${origin.y + y1} ${origin.z + z1} ${origin.x + x2} ${origin.y + y2} ${origin.z + z2} ${spec.name}`).successCount > 0; }
  catch (e) { log(`TICKINGAREA ${spec.name} FAILED: ${String(e && e.message || e).slice(0, 60)}`); return; }
  const far = { x: origin.x + (Math.abs(x1) > Math.abs(x2) ? x1 : x2), y: origin.y, z: origin.z + (Math.abs(z1) > Math.abs(z2) ? z1 : z2) };
  const loaded = yield* waitChunk(dim, far);
  log(`TICKINGAREA ${spec.name} ${ok ? "added" : "not confirmed"}${loaded ? "" : " · far corner still not loaded"}`);
}
// q9: clear every tree box this run planted (wherever the player now stands), then drop the ticking areas
function* resetJob(player, spec, log, origin) {
  const dim = player.dimension; const boxes = plantedBoxes(); let n = 0;
  for (const b of boxes) {
    const [x, y, z] = b.at;
    if (!(yield* waitChunk(dim, { x, y, z }))) continue;
    try { dim.runCommand(`fill ${x - b.r} ${y} ${z - b.r} ${x + b.r} ${y + b.h} ${z + b.r} air`); n++; } catch { /* unloaded */ }
    planted.delete(b.at.join(","));
    yield;
  }
  log(`LEAFRESET ${n}/${boxes.length} tree boxes cleared${boxes.length ? "" : " (none recorded - a relog forgets them; the ground ahead is cleared instead)"}`);
  if (!boxes.length && spec.box) yield* clearJob(player, { box: spec.box, h: spec.h }, log, origin);
  for (const name of spec.areas || []) { try { dim.runCommand(`tickingarea remove ${name}`); } catch { /* already gone */ } }
  if ((spec.areas || []).length) log(`TICKINGAREA removed: ${spec.areas.join(", ")}`);
}

// clear the pilot ground ahead (above the feet only) in slices that stay under the 32,768-block fill cap
export function sliceDepth(xa, xb, h) { return Math.max(1, Math.min(8, Math.floor(32768 / ((xb - xa + 1) * (h + 1))))); }
function* clearJob(player, spec, log, origin) {
  const dim = player.dimension; const x0 = origin.x, y0 = origin.y, z0 = origin.z;
  const [xa, xb, za, zb] = spec.box || [-32, 32, -32, -2]; const h = spec.h || 40; const d = sliceDepth(xa, xb, h);
  let slices = 0;
  for (let z = za; z <= zb; z += d) {
    try { dim.runCommand(`fill ${x0 + xa} ${y0} ${z0 + z} ${x0 + xb} ${y0 + h} ${z0 + Math.min(z + d - 1, zb)} air`); slices++; } catch { /* unloaded */ }
    yield;
  }
  log(`LEAFCLEAR ${slices} slices x ${xa}..${xb} z ${za}..${zb} above y ${y0}`);
}

// ---------------------------------------------------------------------------------------------------------------------
// the lineup
// ---------------------------------------------------------------------------------------------------------------------
function lines(text) {
  const out = [];
  for (const para of String(text).split("\n")) {
    let cur = "";
    for (const piece of para.split(/(?<=[.!?:]) +| (?=- )/)) {
      if (cur && (cur + " " + piece).length > 190) { out.push(cur); cur = piece; } else cur = cur ? cur + " " + piece : piece;
    }
    if (cur) out.push(cur);
  }
  return out.join("\n");
}
const NEAR = { leafarea: { name: "pw_pilot_near", box: [-48, -5, -62, 48, 40, 2] } };
const SHOTS = "SHOT 1 all of them from here. SHOT 2 walk up to the PILOT tree. SHOT 3 stand UNDER it, look up.";
const PASSN = "PASS = this species-age is ready to replace today's leaf. FAIL + note = what is off (colour, fullness, shape, flicker, gaps).";
const UP = (s) => s.toUpperCase().replace("_", " ");
function trunkNote(sp, age) {
  if (!age) return sp === "azalea" ? "Vanilla azalea tree (oak log)." : `Vanilla ${sp.replace("_", " ")} log; the shape is today's BP-02 tree (branchless).`;
  return age === "elder" ? "Our ELDER trunk: square 2x2 with branches." : `Our ${age.toUpperCase()} dodecagon trunk, no branches.`;
}
// a row of copies: TODAY (grown), then copies of it with the pilot blocks; spacing / depth come from the tree's box
function lineOf(id, sp, age, n) {
  const { r } = treeOf(sp, age); const gap = 2 * r + 3; const dz = -(r + 4);
  const xs = n === 3 ? [-gap, 0, gap] : [-Math.ceil(gap / 2), Math.ceil(gap / 2)];
  const clear = { leafclear: { box: [xs[0] - r - 1, xs[xs.length - 1] + r + 1, dz - r - 1, -2], h: treeOf(sp, age).h + 2 } };
  const trees = [{ leaftree: { sp, age, dx: xs[0], dz, keep: true } }, { leaftree: { sp, age, dx: xs[1], dz, from: [xs[0], dz] } }];
  if (n === 3) trees.push({ leaftree: { sp, age, dx: xs[2], dz, from: [xs[0], dz], block: "pw:pilot_{sp}_leaves_bt" } });
  const name = `${UP(sp)}${age ? " " + age.toUpperCase() : ""}`;
  const where = n === 3 ? "LEFT = TODAY's leaves. MIDDLE = PILOT pre-coloured. RIGHT = PILOT biome colour (the biome you stand in decides it)."
                        : "LEFT = TODAY's leaves. RIGHT = PILOT (painted art, never biome-coloured, as in Java).";
  return { id, group: "P15 LEAVES", title: `${name}: TODAY vs PILOT${n === 3 ? " vs PILOT BIOME COLOUR" : ""}`,
    body: lines(`${n === 3 ? "Three" : "Two"} copies of ONE ${name} tree grow ${-dz} blocks NORTH (give it 5 seconds). ${trunkNote(sp, age)}\n${where}\n${SHOTS.replace("the PILOT tree", n === 3 ? "the MIDDLE tree" : "the RIGHT tree")}\n${PASSN}`),
    setup: [NEAR, clear, { daytime: "noon" }, ...trees] };
}
const trio = (id, sp, age) => lineOf(id, sp, age, 3);
const duo = (id, sp, age) => lineOf(id, sp, age, 2);

const FAR_Z = [-20, -44, -68, -92, -116];   // rows 24 apart; trees 18 apart inside a row (oak / spruce MATURE, box r 8)
const FAR_X = [-36, -18, 0, 18, 36];
const FAR_STEP = { id: "l24", group: "P15 FAR SWAP", title: "FAR SWAP: DOES THE GAME TURN THEM SOLID ON ITS OWN?",
  body: lines("Five identical rows of MATURE trees NORTH at 20, 44, 68, 92 and 116 blocks. In each row, WEST to EAST: OAK TODAY · OAK PILOT far-swap (see-through bits left as they are) · OAK PILOT far-swap PAINTED (see-through bits leaf-coloured) · SPRUCE far-swap · SPRUCE far-swap painted.\n" +
    "Walk SOUTH away from them, looking back. Note the distance where each kind turns SOLID, and what solid looks like (flat green panels? a box?). Also look at their SHADOWS at noon from close up.\n" +
    "SHOTS: from close, then from far (turned solid). PASS = the far look is acceptable. FAIL + note = what you saw and at what distance."),
  setup: [{ leafarea: { name: "pw_pilot_far", box: [-46, -5, -130, 46, 40, -4] } }, { leafclear: { box: [-45, 45, -128, -2], h: 30 } }, { daytime: "noon" },
    ...FAR_Z.flatMap((z, i) => {
      const row = [["oak", { keep: true }], ["oak", { block: "pw:pilot_{sp}_leaves_far" }], ["oak", { block: "pw:pilot_{sp}_leaves_farp" }],
                   ["spruce", { block: "pw:pilot_{sp}_leaves_far" }], ["spruce", { block: "pw:pilot_{sp}_leaves_farp" }]];
      return row.map(([sp, extra], j) => {
        const src = j <= 2 ? [FAR_X[0], FAR_Z[0]] : [FAR_X[3], FAR_Z[0]];                        // every oak = a copy of row 1 oak TODAY; spruce of row 1 spruce
        const grownHere = i === 0 && (j === 0 || j === 3);
        return { leaftree: { sp, age: "mature", dx: FAR_X[j], dz: z, ...extra, ...(grownHere ? {} : { from: src }) } };
      });
    })] };

const SPECIES_STEPS = [
  ...AGES.oak.map((a) => ["oak", a, 3]), ...AGES.birch.map((a) => ["birch", a, 3]), ...AGES.spruce.map((a) => ["spruce", a, 3]),
  ...AGES.jungle.map((a) => ["jungle", a, 3]), ["dark_oak", "elder", 3], ["pale_oak", "elder", 2],
  ["acacia", undefined, 3], ["mangrove", undefined, 3], ["cherry", undefined, 2], ["azalea", undefined, 2],
];
const STEPS15 = SPECIES_STEPS.map(([sp, age, n], i) => {
  const st = lineOf(`l${String(i + 1).padStart(2, "0")}`, sp, age, n);
  if (sp === "spruce") st.body = st.body.replace("\n", "\nSpruce has no cards-only leaves (as in Java): every spruce leaf is the full shape.\n");
  if (sp === "azalea") st.body = st.body.replace("\n", "\nThe azalea tree carries BOTH kinds: plain AZALEA and FLOWERING AZALEA leaves - judge both (say which, if one fails).\n");
  return st;
});
const N_SP = STEPS15.length;   // 21 species-age steps: l01..l21
STEPS15.push(
  { id: "l22", group: "P15 LEAVES", title: "RANDOM PICTURE TURNS (ISOTROPIC): OFF vs ON",
    body: lines("Four PILOT trees NORTH (OLD oak, OLD spruce; each pair = one tree and its exact copy). WEST pair = OAK: left without, right WITH random picture turns on the cube faces. EAST pair = SPRUCE: same.\n" +
      "Look for: any visible repeating pattern on the left ones that the right ones break up - and whether the right ones look broken or wrong anywhere.\n" +
      "SHOTS: each pair close up.\nPASS = random turns help (or no difference). FAIL + note = they hurt."),
    setup: [NEAR, { leafclear: { box: [-39, 39, -22, -2], h: 30 } }, { daytime: "noon" },
      { leaftree: { sp: "oak", age: "old", dx: -29, dz: -12 } }, { leaftree: { sp: "oak", age: "old", dx: -10, dz: -12, from: [-29, -12], block: "pw:pilot_{sp}_leaves_iso" } },
      { leaftree: { sp: "spruce", age: "old", dx: 10, dz: -12 } }, { leaftree: { sp: "spruce", age: "old", dx: 29, dz: -12, from: [10, -12], block: "pw:pilot_{sp}_leaves_iso" } }] },
  { id: "l23", group: "P15 LEAVES", title: "SHADE AT NOON: TODAY vs PILOT",
    body: lines("NOON. Two copies of ONE OLD oak NORTH: LEFT = TODAY's leaves, RIGHT = PILOT. Stand under each and look at the GROUND.\nLook for: the pilot throws dappled shade (sun spots through the gaps) like today's leaves - not a solid block of shadow, not none.\n" +
      "SHOTS: the ground under each tree.\nPASS = the pilot's shade looks right. FAIL + note."),
    setup: [NEAR, { leafclear: { box: [-20, 20, -22, -2], h: 30 } }, { daytime: "noon" }, { weather: "clear" },
      { leaftree: { sp: "oak", age: "old", dx: -10, dz: -12, keep: true } }, { leaftree: { sp: "oak", age: "old", dx: 10, dz: -12, from: [-10, -12] } }] },
  FAR_STEP,
  { id: "l25", group: "P15 GROVE", title: "A GROVE: WALK THROUGH IT (FRAME RATE)",
    body: lines("Twelve PILOT trees (oak, birch, spruce, jungle; young, mature, old) in a grove NORTH. Walk through it, then run through it.\nLook for: stutter or frame drops compared with a forest of today's leaves. Please note PS5 and PHONE separately if you can.\n" +
      "PASS = smooth. FAIL + note = where it stuttered, which device."),
    setup: [NEAR, { leafclear: { box: [-37, 37, -60, -2], h: 30 } }, { daytime: "noon" },
      ...[-27, -9, 9, 27].flatMap((dx, i) => [-14, -32, -50].map((dz, j) => ({ leaftree: { sp: ["oak", "birch", "spruce", "jungle"][(i + j) % 4], age: ["young", "mature", "old"][(i + 2 * j) % 3], dx, dz, noclear: true } })))] },
);
const Q0 = { id: "q0", group: "P15 SETUP", title: "P15 LEAF PILOT: A COPY OF THE TEST WORLD, VIBRANT VISUALS ON, FACE NORTH",
  body: lines("Packs: PW-TestRunner RP v0.4.0 (TOP of the resource list) + BP v0.5.1 (bottom), with your normal pack stack. Use a COPY of the test world. On the PS5.\n" +
    "Vibrant Visuals only works if EVERY resource pack supports it: swap Civitas Markers RP v0.2.1 for v0.2.2 (the only one that did not).\n" +
    `Settings: Vibrant Visuals ON. Creative. Stand on a big FLAT open area (50 blocks each side, 130 blocks clear NORTH for step l24) and FACE NORTH. Steps l01-l${N_SP} = one species-age each (${N_SP} steps).\n` +
    "While you are in Video settings: is there a 'Texture Streaming' toggle? Note it here.\nPASS = ready (note the toggle answer and whether Vibrant Visuals is ON)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P15 DONE", title: "P15: ALL CLEAR - UPLOAD THE SHOTS",
  body: lines("Every pilot tree this run grew is cleared (wherever you stand now), then both ticking areas are removed. Give it 10 seconds.\nUpload the screenshots and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p15 and copy that.\nPASS = uploaded (or about to)."),
  setup: [{ leafreset: { areas: ["pw_pilot_far", "pw_pilot_near"], box: [-48, 48, -128, -2], h: 40 } }, { daytime: "noon" }] };

export const P15_STEPS = [Q0, ...STEPS15, Q9];
export const P15_INDEX = Object.fromEntries(P15_STEPS.map((s, i) => [s.id, i]));
