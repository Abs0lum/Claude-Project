// waterprobe (BDS only) — R10: measure what Bedrock water does and what we can control, on the server itself.
// Every experiment builds its own little arena in the sky (y 230), runs, and prints one [CIVTEST] JSON line.
import * as mc from "@minecraft/server";
const { world, system, BlockPermutation, ItemStack } = mc;
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (t) => new Promise((r) => system.runTimeout(r, t));
const X0 = 992, Z0 = 992, Y = 230, CELL = 40;             // ticking area 992..1151 = exactly 10 x 10 chunks (an area is capped at 100 chunks; 1000 is not chunk-aligned)
const cellOrigin = (i) => ({ x: X0 + 4 + (i % 4) * CELL, z: Z0 + 4 + Math.floor(i / 4) * CELL });
const short = (id) => (id || "?").replace("minecraft:", "");
const WATERS = new Set(["minecraft:water", "minecraft:flowing_water"]);

function cmd(dim, c) { try { return dim.runCommand(c).successCount; } catch (e) { return "ERR " + String(e).slice(0, 120); } }
function fill(dim, x0, y0, z0, x1, y1, z1, id, extra = "") { return cmd(dim, `fill ${x0} ${y0} ${z0} ${x1} ${y1} ${z1} ${id} ${extra}`.trim()); }
function blk(dim, x, y, z) { try { return dim.getBlock({ x, y, z }); } catch { return undefined; } }
function depth(b) { try { return b.permutation.getState("liquid_depth"); } catch { return undefined; } }
function wl(b) { try { return b.isWaterlogged; } catch { return "n/a"; } }
function cell(dim, x, y, z) {
  const b = blk(dim, x, y, z);
  if (!b) return { t: "unloaded" };
  const o = { t: short(b.typeId) };
  const d = depth(b); if (d !== undefined) o.d = d;
  const w = wl(b); if (w === true) o.wl = true;
  return o;
}
const isWet = (b) => b && (WATERS.has(b.typeId) || wl(b) === true);
function scan(dim, x0, z0, x1, z1, y, cx, cz) {        // count water at one level; histogram of liquid_depth; reach
  let n = 0, still = 0, flowing = 0, reach = 0; const hist = {};
  for (let x = x0; x <= x1; x++) for (let z = z0; z <= z1; z++) {
    const b = blk(dim, x, y, z);
    if (!b || !WATERS.has(b.typeId)) continue;
    n++; if (b.typeId === "minecraft:water") still++; else flowing++;
    const d = depth(b); hist[d] = (hist[d] || 0) + 1;
    if (cx !== undefined) reach = Math.max(reach, Math.abs(x - cx) + Math.abs(z - cz));
  }
  return { n, still, flowing, reach, hist };
}
function setPerm(dim, x, y, z, id, states) {
  const b = blk(dim, x, y, z);
  try { b.setPermutation(BlockPermutation.resolve(id, states || {})); return "ok"; } catch (e) { return "ERR " + String(e).slice(0, 120); }
}
function floor(dim, o, w, y = Y, id = "stone") { return fill(dim, o.x, y, o.z, o.x + w - 1, y, o.z + w - 1, id); }
function clearCell(dim, o, y0 = Y - 14, y1 = Y + 12) {      // air out a whole cell (in slabs: fill is capped at 32768)
  for (let y = y0; y <= y1; y += 4) fill(dim, o.x - 2, y, o.z - 2, o.x + CELL - 6, Math.min(y + 3, y1), o.z + CELL - 6, "air");
}

// ------------------------------------------------------------------------------------------------------------- E0
function e0Catalogue() {
  const out = { step: "E0", what: "block types, states, enums, gamerules, API surface" };
  try {
    const all = mc.BlockTypes.getAll().map((t) => t.id);
    out.blockTypes = all.filter((id) => /water|lava|bubble|kelp|seagrass|sponge|ice|cauldron|coral|pickle|conduit|dripstone|snow|frog|lily|turtle|mangrove_roots|mud/.test(id)).map(short).sort();
  } catch (e) { out.blockTypesErr = String(e); }
  for (const id of ["minecraft:water", "minecraft:flowing_water", "minecraft:lava", "minecraft:bubble_column", "minecraft:cauldron", "minecraft:kelp", "minecraft:seagrass", "minecraft:sponge"]) {
    try { out[short(id) + "_states"] = BlockPermutation.resolve(id).getAllStates(); } catch (e) { out[short(id) + "_states"] = "ERR " + String(e).slice(0, 80); }
  }
  try { const s = mc.BlockStates.get("liquid_depth"); out.liquid_depth_values = s ? s.validValues : null; } catch (e) { out.liquid_depth_values = "ERR"; }
  out.LiquidType = mc.LiquidType ? Object.keys(mc.LiquidType) : "not exported";
  out.FluidType = mc.FluidType ? Object.keys(mc.FluidType) : "not exported";
  out.StructureSaveMode = mc.StructureSaveMode ? Object.keys(mc.StructureSaveMode) : "not exported";
  const bp = mc.Block.prototype;
  out.blockApi = ["isWaterlogged", "setWaterlogged", "isLiquid", "canContainLiquid", "isLiquidBlocking", "liquidCanFlowFromDirection",
    "liquidSpreadCausesSpawn", "canBeDestroyedByLiquidSpread", "getComponent"].map((k) => `${k}:${k in bp ? "yes" : "no"}`);
  const ep = mc.Entity.prototype;
  out.entityApi = ["isInWater", "isSwimming", "isOnGround", "getVelocity", "applyImpulse", "clearVelocity"].map((k) => `${k}:${k in ep ? "yes" : "no"}`);
  try {
    const gr = world.gameRules; const names = Object.getOwnPropertyNames(Object.getPrototypeOf(gr)).filter((k) => k !== "constructor");
    out.gameRules = Object.fromEntries(names.map((k) => { try { return [k, gr[k]]; } catch { return [k, "?"]; } }));
  } catch (e) { out.gameRulesErr = String(e); }
  log(out);
}

// ------------------------------------------------------------------------------------------------------------- E1
async function e1Spread(dim) {                    // one source on a flat 37 x 37 floor: speed, reach, depth by distance, decay
  const o = cellOrigin(0); clearCell(dim, o); floor(dim, o, 37);
  const cx = o.x + 18, cz = o.z + 18, y = Y + 1;
  await sleep(2);
  const t0 = system.currentTick;
  const how = setPerm(dim, cx, y, cz, "minecraft:flowing_water", { liquid_depth: 0 });
  const firstWet = {};                            // distance -> tick it was first wet
  const counts = [];
  for (let t = 1; t <= 60; t++) {
    await sleep(1);
    const s = scan(dim, cx - 9, cz - 9, cx + 9, cz + 9, y, cx, cz);
    for (let k = 1; k <= s.reach; k++) if (firstWet[k] === undefined) firstWet[k] = system.currentTick - t0;
    if (t % 5 === 0) counts.push([system.currentTick - t0, s.n]);
  }
  const axis = []; const diag = [];
  for (let k = 0; k <= 9; k++) { axis.push(cell(dim, cx + k, y, cz)); diag.push(cell(dim, cx + k, y, cz + k)); }
  const final = scan(dim, cx - 9, cz - 9, cx + 9, cz + 9, y, cx, cz);
  const src = cell(dim, cx, y, cz);
  log({ step: "E1", what: "one source on flat stone", place: how, firstWetTickByDistance: firstWet, countsEvery5: counts, final, source: src, axis, diag });
  // decay: remove the source
  const t1 = system.currentTick;
  setPerm(dim, cx, y, cz, "minecraft:air");
  const left = [];
  let gone = null;
  for (let t = 1; t <= 80; t++) {
    await sleep(1);
    const s = scan(dim, cx - 9, cz - 9, cx + 9, cz + 9, y);
    if (t % 5 === 0) left.push([system.currentTick - t1, s.n]);
    if (s.n === 0 && gone === null) { gone = system.currentTick - t1; break; }
  }
  log({ step: "E1b", what: "source removed: how fast the sheet drains", leftEvery5: left, allGoneAfterTicks: gone });
}

// ------------------------------------------------------------------------------------------------------------- E2
async function e2Static(dim) {                    // script-placed partial levels: do they stay put?
  const o = cellOrigin(1); clearCell(dim, o); floor(dim, o, 30);
  const y = Y + 1, sites = [
    ["water d0 (still source)", "minecraft:water", 0], ["water d3 (still, partial)", "minecraft:water", 3], ["water d7 (still, thinnest)", "minecraft:water", 7],
    ["flowing_water d0", "minecraft:flowing_water", 0], ["flowing_water d3", "minecraft:flowing_water", 3], ["water d8 (falling bit)", "minecraft:water", 8],
  ];
  const res = [];
  for (let i = 0; i < sites.length; i++) {
    const x = o.x + 3 + i * 4, z = o.z + 4;
    res.push({ label: sites[i][0], place: setPerm(dim, x, y, z, sites[i][1], { liquid_depth: sites[i][2] }), x, z });
  }
  const snap = () => res.map((r) => ({ at: cell(dim, r.x, y, r.z), around: scan(dim, r.x - 2, r.z - 2, r.x + 2, r.z + 2, y).n }));
  await sleep(1); const t1 = snap();
  await sleep(40); const t40 = snap();
  await sleep(160); const t200 = snap();
  // poke: put a block next to each and take it away again (a neighbour update)
  for (const r of res) { setPerm(dim, r.x, y, r.z + 1, "minecraft:stone"); }
  await sleep(1);
  for (const r of res) { setPerm(dim, r.x, y, r.z + 1, "minecraft:air"); }
  await sleep(40); const poked = snap();
  log({ step: "E2", what: "script-placed still vs flowing water, by level; then a neighbour update",
    rows: res.map((r, i) => ({ label: r.label, place: r.place, t1: t1[i], t40: t40[i], t200: t200[i], after_poke40: poked[i] })) });
  // the same with /setblock
  const x = o.x + 3, z = o.z + 14;
  const c1 = cmd(dim, `setblock ${x} ${y} ${z} water ["liquid_depth"=4]`);
  const c2 = cmd(dim, `setblock ${x + 6} ${y} ${z} flowing_water ["liquid_depth"=4]`);
  await sleep(40);
  log({ step: "E2b", what: "/setblock water d4 and flowing_water d4, 40 ticks later", water: [c1, cell(dim, x, y, z), scan(dim, x - 3, z - 3, x + 3, z + 3, y).n],
    flowing: [c2, cell(dim, x + 6, y, z), scan(dim, x + 3, z - 3, x + 9, z + 3, y).n] });
}

// ------------------------------------------------------------------------------------------------------------- E3
async function e3Fall(dim) {                      // a source at a floor's edge: the falling column and the pool below
  const o = cellOrigin(2); clearCell(dim, o);
  fill(dim, o.x, Y, o.z, o.x + 6, Y, o.z + 6, "stone");               // upper shelf 7 x 7
  floor(dim, o, 33, Y - 12);                                          // lower floor 33 x 33
  const sx = o.x + 6, sz = o.z + 3, y = Y + 1;
  setPerm(dim, sx, y, sz, "minecraft:flowing_water", { liquid_depth: 0 });
  const t0 = system.currentTick; let landed = null;
  for (let t = 1; t <= 80; t++) {
    await sleep(1);
    if (landed === null && WATERS.has((blk(dim, sx + 1, Y - 11, sz) || {}).typeId)) landed = system.currentTick - t0;
  }
  const column = [];
  for (let yy = y; yy >= Y - 11; yy--) column.push([yy - Y, cell(dim, sx + 1, yy, sz)]);
  const pool = scan(dim, o.x, o.z, o.x + 32, o.z + 32, Y - 11, sx + 1, sz);
  log({ step: "E3", what: "source at a shelf edge falling 12 blocks", ticksToLand: landed, column, poolBelow: pool });
}

// ------------------------------------------------------------------------------------------------------------- E4
async function e4Infinite(dim) {                  // two sources with one gap: does the gap become a source?
  const o = cellOrigin(3); clearCell(dim, o);
  const y = Y + 1;
  const trench = (x, z, floorUnderMiddle) => {
    fill(dim, x - 1, Y, z - 1, x + 3, y, z + 1, "stone");            // block 5 x 3 x 2
    fill(dim, x, y, z, x + 2, y, z, "air");                          // the 3-long trench
    if (!floorUnderMiddle) { fill(dim, x + 1, Y, z, x + 1, Y, z, "air"); fill(dim, x + 1, Y - 3, z - 1, x + 1, Y - 3, z + 1, "stone"); }
    setPerm(dim, x, y, z, "minecraft:flowing_water", { liquid_depth: 0 });
    setPerm(dim, x + 2, y, z, "minecraft:flowing_water", { liquid_depth: 0 });
  };
  trench(o.x + 3, o.z + 3, true);
  trench(o.x + 3, o.z + 10, false);
  // a 2 x 2 of sources poured from one bucket-equivalent corner: the classic infinite pool
  fill(dim, o.x + 2, Y, o.z + 17, o.x + 5, y, o.z + 20, "stone"); fill(dim, o.x + 3, y, o.z + 18, o.x + 4, y, o.z + 19, "air");
  setPerm(dim, o.x + 3, y, o.z + 18, "minecraft:flowing_water", { liquid_depth: 0 }); setPerm(dim, o.x + 4, y, o.z + 19, "minecraft:flowing_water", { liquid_depth: 0 });
  await sleep(60);
  log({ step: "E4", what: "infinite-source rule",
    gapOverStone: cell(dim, o.x + 4, y, o.z + 3), gapOverAir: cell(dim, o.x + 4, y, o.z + 10), belowGapOverAir: cell(dim, o.x + 4, Y, o.z + 10),
    pool2x2: [cell(dim, o.x + 3, y, o.z + 18), cell(dim, o.x + 4, y, o.z + 18), cell(dim, o.x + 3, y, o.z + 19), cell(dim, o.x + 4, y, o.z + 19)] });
}

// ------------------------------------------------------------------------------------------------------------- E5
async function e5FillCommands(dim) {              // what /fill ... replace hits; timing of big fills and clears
  const o = cellOrigin(4); clearCell(dim, o); floor(dim, o, 34);
  fill(dim, o.x, Y + 1, o.z, o.x + 33, Y + 4, o.z, "stone"); fill(dim, o.x, Y + 1, o.z + 33, o.x + 33, Y + 4, o.z + 33, "stone");
  fill(dim, o.x, Y + 1, o.z, o.x, Y + 4, o.z + 33, "stone"); fill(dim, o.x + 33, Y + 1, o.z, o.x + 33, Y + 4, o.z + 33, "stone");
  const y = Y + 1, cx = o.x + 16, cz = o.z + 16;
  // a source in the middle spreads (flowing); then a 10 x 10 still block placed by /fill
  setPerm(dim, cx, y, cz, "minecraft:water", { liquid_depth: 0 });
  let t = Date.now(); const f1 = fill(dim, o.x + 2, y, o.z + 2, o.x + 11, y + 2, o.z + 11, "water"); const msFill = Date.now() - t;
  await sleep(50);
  const before = scan(dim, o.x + 1, o.z + 1, o.x + 32, o.z + 32, y);
  t = Date.now(); const r1 = fill(dim, o.x + 1, y, o.z + 1, o.x + 32, y + 2, o.z + 32, "air", "replace water"); const msR1 = Date.now() - t;
  const after1 = scan(dim, o.x + 1, o.z + 1, o.x + 32, o.z + 32, y);
  const r2 = fill(dim, o.x + 1, y, o.z + 1, o.x + 32, y + 2, o.z + 32, "air", "replace flowing_water");
  const after2 = scan(dim, o.x + 1, o.z + 1, o.x + 32, o.z + 32, y);
  // state-specific replace
  setPerm(dim, cx, y, cz, "minecraft:water", { liquid_depth: 0 }); await sleep(30);
  const r3 = fill(dim, o.x + 1, y, o.z + 1, o.x + 32, y, o.z + 32, "air", 'replace water ["liquid_depth"=0]');
  const after3 = scan(dim, o.x + 1, o.z + 1, o.x + 32, o.z + 32, y);
  await sleep(30);
  const after3b = scan(dim, o.x + 1, o.z + 1, o.x + 32, o.z + 32, y);
  // a stone shell filled with sources by one /fill, then emptied in one go: no spill
  log({ step: "E5", what: "/fill water and /fill air replace …", fillWater10x10x3: [f1, msFill + " ms"], before,
    replaceWater: [r1, msR1 + " ms", after1], thenReplaceFlowing: [r2, after2], replaceWaterDepth0Only: [r3, after3, "30 ticks later", after3b] });
}

// ------------------------------------------------------------------------------------------------------------- E6
const WL_TESTS = ["oak_stairs", "oak_slab", "oak_fence", "glass_pane", "iron_bars", "oak_leaves", "chest", "ladder", "oak_trapdoor",
  "cobblestone_wall", "lantern", "glass", "stone", "oak_door", "rail", "torch", "flower_pot", "campfire", "scaffolding", "chain", "sea_lantern", "oak_sign", "bed"];
async function e6Waterlog(dim) {
  const o = cellOrigin(5); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1, LT = mc.LiquidType ? mc.LiquidType.Water : undefined;
  const rows = [];
  for (let i = 0; i < WL_TESTS.length; i++) {
    const x = o.x + 2 + (i % 8) * 4, z = o.z + 2 + Math.floor(i / 8) * 10;
    const id = "minecraft:" + WL_TESTS[i];
    const r = { block: WL_TESTS[i], x, z };
    r.place = setPerm(dim, x, y, z, id);
    const b = blk(dim, x, y, z);
    const q = (name, fn) => { try { r[name] = fn(); } catch (e) { r[name] = "ERR " + String(e).slice(0, 60); } };
    q("canContain", () => b.canContainLiquid(LT));
    q("blocking", () => b.isLiquidBlocking(LT));
    q("spreadPops", () => b.canBeDestroyedByLiquidSpread(LT));
    q("spreadSpawns", () => b.liquidSpreadCausesSpawn(LT));
    q("flowFromNorth", () => b.liquidCanFlowFromDirection(LT, mc.Direction.North));
    q("setWaterlogged", () => { b.setWaterlogged(true); return "ok"; });
    q("isWaterloggedAfterSet", () => blk(dim, x, y, z).isWaterlogged);
    rows.push(r);
  }
  await sleep(40);
  for (const r of rows) {             // did the waterlogged block spill into the cell south of it?
    r.t40 = cell(dim, r.x, y, r.z); r.spillSouth = cell(dim, r.x, y, r.z + 1); r.spillEast = cell(dim, r.x + 1, y, r.z);
  }
  log({ step: "E6", what: "waterlogging: API answers per block; spill after 40 ticks", rows: rows.slice(0, 12) });
  log({ step: "E6.2", rows: rows.slice(12) });
  // a source flowing up to an empty stairs / fence / slab: does flowing water waterlog them?
  const z2 = o.z + 28;
  const T2 = ["oak_stairs", "oak_fence", "oak_slab", "glass_pane", "oak_leaves", "chest"];
  for (let i = 0; i < T2.length; i++) { const x = o.x + 2 + i * 5; setPerm(dim, x + 2, y, z2, "minecraft:" + T2[i]); setPerm(dim, x + 1, y, z2, "minecraft:water", { liquid_depth: 0 }); setPerm(dim, x, y, z2, "minecraft:stone"); }
  await sleep(40);
  log({ step: "E6b", what: "a source right beside an empty block (40 ticks)", rows: T2.map((n, i) => { const x = o.x + 2 + i * 5; return [n, cell(dim, x + 2, y, z2), "beyond", cell(dim, x + 3, y, z2)]; }) });
}

// ------------------------------------------------------------------------------------------------------------- E7
async function e7CustomBlocks(dim) {              // our own blocks with minecraft:liquid_detection
  const o = cellOrigin(6); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1, ids = ["wp:ld_default", "wp:ld_contain", "wp:ld_popped", "wp:ld_broken", "wp:ld_blocking", "wp:ld_stop_east"];
  const rows = [];
  for (let i = 0; i < ids.length; i++) {
    const x = o.x + 3 + i * 5, z = o.z + 4;
    const r = { id: ids[i], place: setPerm(dim, x, y, z, ids[i]) };
    setPerm(dim, x + 1, y, z, "minecraft:flowing_water", { liquid_depth: 0 });      // live source to the EAST of the block
    r.x = x; r.z = z; rows.push(r);
  }
  await sleep(40);
  for (const r of rows) {
    const b = blk(dim, r.x, r.y ?? y, r.z); r.t40 = cell(dim, r.x, y, r.z); r.west = cell(dim, r.x - 1, y, r.z);
    try { r.canContain = b.canContainLiquid(mc.LiquidType.Water); } catch (e) { r.canContain = "ERR"; }
  }
  // the 'contain' block, waterlogged by script, then a source two cells away
  const x = o.x + 3, z = o.z + 14;
  setPerm(dim, x, y, z, "wp:ld_contain"); let sw;
  try { blk(dim, x, y, z).setWaterlogged(true); sw = blk(dim, x, y, z).isWaterlogged; } catch (e) { sw = "ERR " + String(e).slice(0, 80); }
  await sleep(30);
  log({ step: "E7", what: "custom blocks with minecraft:liquid_detection; a source placed EAST of each, 40 ticks", rows, containSetWaterlogged: sw, containT30: cell(dim, x, y, z), containSpill: cell(dim, x + 1, y, z) });
}

// ------------------------------------------------------------------------------------------------------------- E8
async function e8Entities(dim) {                  // floating, sinking, drift in a current
  const o = cellOrigin(7); clearCell(dim, o);
  fill(dim, o.x, Y - 6, o.z, o.x + 14, Y + 2, o.z + 14, "stone"); fill(dim, o.x + 1, Y - 5, o.z + 1, o.x + 13, Y + 2, o.z + 13, "water");   // pool 13 x 13 x 8
  // a current: a channel with a source at the west end
  fill(dim, o.x, Y, o.z + 20, o.x + 16, Y + 2, o.z + 22, "stone"); fill(dim, o.x + 1, Y + 1, o.z + 21, o.x + 15, Y + 2, o.z + 21, "air");
  setPerm(dim, o.x + 1, Y + 1, o.z + 21, "minecraft:flowing_water", { liquid_depth: 0 });
  await sleep(30);
  const ents = [];
  const spawn = (label, f) => { try { const e = f(); ents.push({ label, e, y0: e.location.y, x0: e.location.x }); } catch (err) { ents.push({ label, err: String(err).slice(0, 100) }); } };
  const at = (dx, dy, dz) => ({ x: o.x + dx + 0.5, y: Y + dy, z: o.z + dz + 0.5 });
  spawn("item oak_log (pool)", () => dim.spawnItem(new ItemStack("minecraft:oak_log", 1), at(3, -2, 3)));
  spawn("cow (pool)", () => dim.spawnEntity("minecraft:cow", at(7, -3, 7)));
  spawn("wp:float buoyant (pool, deep)", () => dim.spawnEntity("wp:float", at(10, -4, 4)));
  spawn("wp:sinker no buoyant (pool)", () => dim.spawnEntity("wp:sinker", at(4, 1, 10)));
  spawn("item oak_log (current)", () => dim.spawnItem(new ItemStack("minecraft:oak_log", 1), at(3, 1.2, 21)));
  spawn("wp:float (current)", () => dim.spawnEntity("wp:float", at(4, 1.2, 21)));
  const track = [];
  for (let t = 0; t <= 100; t += 10) {
    track.push([t, ents.map((r) => { if (!r.e) return null; try { const l = r.e.location; return [+(l.x - o.x).toFixed(2), +(l.y - Y).toFixed(2), r.e.isInWater ? "W" : "-", r.e.isSwimming ? "S" : "-"]; } catch { return "gone"; } })]);
    await sleep(10);
  }
  log({ step: "E8", what: "entities in still water and in a current (x and y relative to the cell, every 10 ticks)", labels: ents.map((r) => r.label + (r.err ? " ERR " + r.err : "")), track });
  for (const r of ents) try { r.e && r.e.remove(); } catch { /* */ }
}

// ------------------------------------------------------------------------------------------------------------- E9
async function e9Specials(dim) {                  // sponge, bubble columns, cauldron, kelp/seagrass, ice, lava meets water
  const o = cellOrigin(8); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1, out = { step: "E9", what: "sponge, bubble columns, cauldron, kelp, ice, lava" };
  // sponge in a 15 x 15 x 1 sheet of sources (walled)
  fill(dim, o.x, y, o.z, o.x + 16, y, o.z + 16, "stone"); fill(dim, o.x + 1, y, o.z + 1, o.x + 15, y, o.z + 15, "water");
  await sleep(5);
  const b0 = scan(dim, o.x + 1, o.z + 1, o.x + 15, o.z + 15, y).n;
  out.spongeScript = setPerm(dim, o.x + 8, y, o.z + 8, "minecraft:sponge");
  await sleep(5);
  out.sponge = { before: b0, after: scan(dim, o.x + 1, o.z + 1, o.x + 15, o.z + 15, y).n, block: cell(dim, o.x + 8, y, o.z + 8) };
  out.spongeCmd = cmd(dim, `setblock ${o.x + 3} ${y} ${o.z + 3} sponge`);
  await sleep(5);
  out.spongeCmdAfter = { left: scan(dim, o.x + 1, o.z + 1, o.x + 15, o.z + 15, y).n, block: cell(dim, o.x + 3, y, o.z + 3) };
  // bubble columns: 1 x 1 shafts 6 deep over soul sand and magma
  for (const [k, base] of [[0, "soul_sand"], [1, "magma"]]) {
    const x = o.x + 20 + k * 4, z = o.z + 2;
    fill(dim, x - 1, y, z - 1, x + 1, y + 6, z + 1, "glass"); setPerm(dim, x, y, z, "minecraft:" + base);
    fill(dim, x, y + 1, z, x, y + 6, z, "water");
  }
  await sleep(30);
  out.bubble = [0, 1].map((k) => { const x = o.x + 20 + k * 4, z = o.z + 2; const col = []; for (let yy = y; yy <= y + 6; yy++) { const b = blk(dim, x, yy, z); col.push(b ? short(b.typeId) + (b.typeId === "minecraft:bubble_column" ? JSON.stringify(b.permutation.getAllStates()) : "") : "?"); } return col; });
  // cauldron
  const cx = o.x + 20, cz = o.z + 8;
  setPerm(dim, cx, y, cz, "minecraft:cauldron");
  out.cauldronStates = blk(dim, cx, y, cz).permutation.getAllStates();
  try { const c = blk(dim, cx, y, cz).getComponent("minecraft:fluid_container"); out.cauldronComp = c ? "present" : "absent"; if (c) { c.fillLevel = 6; out.cauldronAfterSet = blk(dim, cx, y, cz).permutation.getAllStates(); } } catch (e) { out.cauldronComp = "ERR " + String(e).slice(0, 80); }
  try { setPerm(dim, cx + 2, y, cz, "minecraft:cauldron", { fill_level: 6, cauldron_liquid: "water" }); out.cauldronByState = blk(dim, cx + 2, y, cz).permutation.getAllStates(); } catch (e) { out.cauldronByState = "ERR"; }
  // kelp / seagrass in air and in water
  out.kelpInAir = setPerm(dim, o.x + 20, y, o.z + 12, "minecraft:kelp"); out.seagrassInAir = setPerm(dim, o.x + 22, y, o.z + 12, "minecraft:seagrass");
  await sleep(5);
  out.kelpAir5 = cell(dim, o.x + 20, y, o.z + 12); out.seagrassAir5 = cell(dim, o.x + 22, y, o.z + 12);
  // ice over a source: break it with /setblock destroy and with /setblock air
  fill(dim, o.x + 26, y, o.z + 12, o.x + 30, y, o.z + 16, "stone");
  setPerm(dim, o.x + 27, y, o.z + 13, "minecraft:ice"); setPerm(dim, o.x + 29, y, o.z + 13, "minecraft:ice");
  cmd(dim, `setblock ${o.x + 27} ${y} ${o.z + 13} air destroy`); cmd(dim, `setblock ${o.x + 29} ${y} ${o.z + 13} air`);
  await sleep(5);
  out.iceDestroy = cell(dim, o.x + 27, y, o.z + 13); out.iceAir = cell(dim, o.x + 29, y, o.z + 13);
  // lava meets water: (a) water flows onto a lava source; (b) lava flows into still water; (c) lava falls onto water
  const lx = o.x + 2, lz = o.z + 22;
  fill(dim, lx - 1, y, lz - 1, lx + 30, y + 3, lz + 9, "stone"); fill(dim, lx, y, lz, lx + 29, y + 3, lz + 8, "air");
  setPerm(dim, lx + 2, y, lz + 1, "minecraft:lava", { liquid_depth: 0 }); setPerm(dim, lx, y, lz + 1, "minecraft:flowing_water", { liquid_depth: 0 });
  setPerm(dim, lx + 10, y, lz + 1, "minecraft:water", { liquid_depth: 0 }); setPerm(dim, lx + 12, y, lz + 1, "minecraft:flowing_lava", { liquid_depth: 0 });
  setPerm(dim, lx + 20, y, lz + 1, "minecraft:water", { liquid_depth: 0 }); setPerm(dim, lx + 20, y + 3, lz + 1, "minecraft:flowing_lava", { liquid_depth: 0 });
  await sleep(100);
  const row = (x0) => { const r = []; for (let k = 0; k <= 4; k++) r.push(short((blk(dim, x0 + k, y, lz + 1) || {}).typeId)); return r; };
  const col = (x0) => { const r = []; for (let k = 0; k <= 3; k++) r.push(short((blk(dim, x0, y + k, lz + 1) || {}).typeId)); return r; };
  out.lava = { waterFlowsToLavaSource: row(lx), lavaFlowsToWater: row(lx + 10), lavaFallsOnWater_column: col(lx + 20) };
  log(out);
}

// ------------------------------------------------------------------------------------------------------------ E10
async function e10Structures(dim) {               // our buildings are structures: what happens when one lands in water?
  const o = cellOrigin(9); clearCell(dim, o); floor(dim, o, 34);
  const out = { step: "E10", what: "structure placed into a pool: air inside the walls vs the water" };
  // build a 5 x 5 x 5 stone shell with an air room 3 x 3 x 3 and save it
  const bx = o.x + 26, bz = o.z + 26, by = Y + 1;
  fill(dim, bx, by, bz, bx + 4, by + 4, bz + 4, "stone"); fill(dim, bx + 1, by + 1, bz + 1, bx + 3, by + 3, bz + 3, "air");
  // an open-topped variant (no roof) and one with a stairs block inside
  fill(dim, bx - 8, by, bz, bx - 4, by + 4, bz + 4, "stone"); fill(dim, bx - 7, by + 1, bz + 1, bx - 5, by + 4, bz + 3, "air"); setPerm(dim, bx - 6, by + 1, bz + 2, "minecraft:oak_stairs");
  let sm;
  try {
    const opt = { includeEntities: false, includeBlocks: true }; if (mc.StructureSaveMode) opt.saveMode = mc.StructureSaveMode.Memory;
    sm = world.structureManager;
    try { sm.delete("wp:box"); } catch { /* */ } try { sm.delete("wp:openbox"); } catch { /* */ }
    sm.createFromWorld("wp:box", dim, { x: bx, y: by, z: bz }, { x: bx + 4, y: by + 4, z: bz + 4 }, opt);
    sm.createFromWorld("wp:openbox", dim, { x: bx - 8, y: by, z: bz }, { x: bx - 4, y: by + 4, z: bz + 4 }, opt);
    out.saved = "ok";
  } catch (e) { out.saved = "ERR " + String(e).slice(0, 120); log(out); return; }
  // pools: four 9 x 9 x 9 water tanks
  const tanks = [];
  for (let k = 0; k < 4; k++) {
    const tx = o.x + 1 + (k % 2) * 12, tz = o.z + 1 + Math.floor(k / 2) * 12;
    fill(dim, tx, Y - 8, tz, tx + 10, Y + 2, tz + 10, "stone"); fill(dim, tx + 1, Y - 7, tz + 1, tx + 9, Y + 1, tz + 9, "water");
    tanks.push({ tx, tz });
  }
  await sleep(5);
  const room = (x, y, z, h = 3) => { let w = 0, a = 0, other = 0; for (let i = 1; i <= 3; i++) for (let j = 1; j <= h; j++) for (let k = 1; k <= 3; k++) { const b = blk(dim, x + i, y + j, z + k); if (!b) continue; if (isWet(b)) w++; else if (b.typeId === "minecraft:air") a++; else other++; } return { water: w, air: a, other }; };
  const loc = (k) => ({ x: tanks[k].tx + 3, y: Y - 5, z: tanks[k].tz + 3 });
  const tries = [
    ["box, default options", () => sm.place("wp:box", dim, loc(0))],
    ["box, waterlogged:true", () => sm.place("wp:box", dim, loc(1), { waterlogged: true })],
    ["openbox (no roof, stairs inside), default", () => sm.place("wp:openbox", dim, loc(2))],
    ["box via /structure load … waterlogged true", () => cmd(dim, `structure load wp:box ${loc(3).x} ${loc(3).y} ${loc(3).z} 0_degrees none false true true`)],
  ];
  out.rows = [];
  for (let k = 0; k < tries.length; k++) { let r; try { r = tries[k][1](); r = r === undefined ? "ok" : r; } catch (e) { r = "ERR " + String(e).slice(0, 100); } out.rows.push({ how: tries[k][0], placed: r }); }
  await sleep(2);
  for (let k = 0; k < 4; k++) out.rows[k].room_t2 = room(loc(k).x, loc(k).y, loc(k).z, k === 2 ? 4 : 3);
  await sleep(60);
  for (let k = 0; k < 4; k++) out.rows[k].room_t62 = room(loc(k).x, loc(k).y, loc(k).z, k === 2 ? 4 : 3);
  out.stairsInOpenbox = cell(dim, loc(2).x + 2, loc(2).y + 1, loc(2).z + 2);
  log(out);
}

// ------------------------------------------------------------------------------------------------------------ E11
async function e11Cost(dim) {                     // what a flood costs the server: ticks timed while water falls and spreads
  const o = cellOrigin(10); clearCell(dim, o, Y - 14, Y + 14);
  floor(dim, o, 36, Y - 12);
  const gaps = []; let last = Date.now(); let on = true;
  const iv = system.runInterval(() => { const n = Date.now(); if (on) gaps.push(n - last); last = n; }, 1);
  await sleep(20);
  const base = gaps.splice(0);
  let t = Date.now(); const f = fill(dim, o.x + 4, Y + 10, o.z + 4, o.x + 27, Y + 10, o.z + 27, "water"); const msF = Date.now() - t;  // 24 x 24 sheet of sources in the air
  await sleep(200);
  const flood = gaps.splice(0);
  const lower = scan(dim, o.x, o.z, o.x + 35, o.z + 35, Y - 11);
  t = Date.now();
  let cleared = 0; for (let yy = Y - 11; yy <= Y + 10; yy++) { const r = fill(dim, o.x - 2, yy, o.z - 2, o.x + 37, yy, o.z + 37, "air", "replace water"); const r2 = fill(dim, o.x - 2, yy, o.z - 2, o.x + 37, yy, o.z + 37, "air", "replace flowing_water"); cleared += (typeof r === "number" ? r : 0) + (typeof r2 === "number" ? r2 : 0); }
  const msClear = Date.now() - t;
  await sleep(40);
  const after = gaps.splice(0); on = false; system.clearRun(iv);
  const stat = (a) => { if (!a.length) return null; const s = [...a].sort((p, q) => p - q); return { n: a.length, avg: Math.round(a.reduce((p, q) => p + q, 0) / a.length), p95: s[Math.floor(s.length * 0.95)], max: s[s.length - 1] }; };
  log({ step: "E11", what: "server tick gaps (ms) before / during a 576-source sheet falling 22 blocks / after a 22-layer clear", fill: [f, msF + " ms"],
    baseline: stat(base), flood200: stat(flood), lowerFloorWater: lower, clear: [cleared, msClear + " ms"], afterClear40: stat(after) });
}

// ------------------------------------------------------------------------------------------------------------ E12
async function e12Nether() {                      // water in the Nether
  const nd = world.getDimension("nether");
  const out = { step: "E12", what: "water placed in the Nether" };
  out.area = cmd(nd, "tickingarea add 0 0 0 15 127 15 wnether true");
  for (let i = 0; i < 100; i++) { if (blk(nd, 8, 100, 8)) break; await sleep(10); }
  fill(nd, 2, 98, 2, 12, 104, 12, "stone"); fill(nd, 3, 100, 3, 11, 103, 11, "air");
  out.script = setPerm(nd, 5, 100, 5, "minecraft:water", { liquid_depth: 0 });
  out.cmd = cmd(nd, "setblock 9 100 9 water");
  out.fill = fill(nd, 5, 100, 8, 6, 100, 9, "water");
  await sleep(2);
  out.t2 = [cell(nd, 5, 100, 5), cell(nd, 9, 100, 9), cell(nd, 5, 100, 8)];
  await sleep(60);
  out.t62 = [cell(nd, 5, 100, 5), cell(nd, 9, 100, 9), cell(nd, 5, 100, 8)];
  out.spread = scan(nd, 3, 3, 11, 11, 100).n;
  log(out);
}

// ------------------------------------------------------------------------------------------------------------ E13
async function e13Wake(dim) {                     // an INERT still sheet: what wakes it, and how far does the waking spread?
  const o = cellOrigin(11); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1, out = { step: "E13", what: "inert still water (setPermutation water) and what wakes it" };
  // A: a 9 x 9 still sheet with open edges (no walls), placed cell by cell by script
  const ax = o.x + 2, az = o.z + 2;
  for (let i = 0; i < 9; i++) for (let k = 0; k < 9; k++) setPerm(dim, ax + i, y, az + k, "minecraft:water", { liquid_depth: 0 });
  await sleep(40); out.A_after40 = scan(dim, ax - 8, az - 2, ax + 10, az + 10, y).n;
  // poke ONE cell beyond the west edge (stone in, air back): how much of the sheet starts to spill?
  setPerm(dim, ax - 1, y, az + 4, "minecraft:stone"); await sleep(1); setPerm(dim, ax - 1, y, az + 4, "minecraft:air");
  await sleep(60);
  let spillW = 0, spillE = 0, spillN = 0;
  for (let k = -2; k <= 10; k++) { if (isWet(blk(dim, ax - 1, y, az + k))) spillW++; if (isWet(blk(dim, ax + 9, y, az + k))) spillE++; }
  for (let i = -2; i <= 10; i++) if (isWet(blk(dim, ax + i, y, az - 1))) spillN++;
  out.A_poke_west = { spillCellsWestEdge: spillW, eastEdge: spillE, northEdge: spillN, total: scan(dim, ax - 9, az - 9, ax + 17, az + 17, y).n };
  // B: a still sheet placed by /fill (edges open): does it spill by itself?
  const bx = o.x + 20, bz = o.z + 2;
  fill(dim, bx, y, bz, bx + 8, y, bz + 8, "water");
  await sleep(60); out.B_fill_after60 = { total: scan(dim, bx - 8, bz - 2, bx + 13, bz + 13, y).n, sheet: 81 };
  // C: a waterlogged stairs and a waterlogged fence (by script), then a neighbour update beside each
  const cx = o.x + 4, cz = o.z + 22;
  setPerm(dim, cx, y, cz, "minecraft:oak_stairs"); blk(dim, cx, y, cz).setWaterlogged(true);
  setPerm(dim, cx + 8, y, cz, "minecraft:oak_fence"); blk(dim, cx + 8, y, cz).setWaterlogged(true);
  await sleep(20);
  out.C_before = [scan(dim, cx - 3, cz - 3, cx + 3, cz + 3, y).n, scan(dim, cx + 5, cz - 3, cx + 11, cz + 3, y).n];
  for (const dx of [0, 8]) { setPerm(dim, cx + dx, y, cz + 1, "minecraft:stone"); }
  await sleep(1);
  for (const dx of [0, 8]) { setPerm(dim, cx + dx, y, cz + 1, "minecraft:air"); }
  await sleep(60);
  out.C_after_poke = { stairs: [cell(dim, cx, y, cz), scan(dim, cx - 3, cz - 3, cx + 3, cz + 3, y).n], fence: [cell(dim, cx + 8, y, cz), scan(dim, cx + 5, cz - 3, cx + 11, cz + 3, y).n] };
  // D: a structure placed beside an inert sheet: does placing a building wake the water?
  const dx0 = o.x + 20, dz0 = o.z + 18;
  for (let i = 0; i < 6; i++) for (let k = 0; k < 6; k++) setPerm(dim, dx0 + i, y, dz0 + k, "minecraft:water", { liquid_depth: 0 });
  await sleep(10);
  let placed;
  try { world.structureManager.place("wp:box", dim, { x: dx0 + 6, y: y, z: dz0 }); placed = "ok"; } catch (e) { placed = "ERR " + String(e).slice(0, 80); }
  await sleep(60);
  out.D_structure_beside = { placed, total: scan(dim, dx0 - 8, dz0 - 8, dx0 + 5, dz0 + 13, y).n, sheet: 36 };
  log(out);
}

// ------------------------------------------------------------------------------------------------------------ E14
async function e14Pump(dim) {                     // the fastest dry-out of a flooded room: one /fill vs sponge vs block-by-block
  const o = cellOrigin(12); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1, out = { step: "E14", what: "emptying a flooded 7 x 7 x 4 room with live water outside an open doorway" };
  const room = (x0, z0) => { fill(dim, x0, y, z0, x0 + 8, y + 4, z0 + 8, "stone"); fill(dim, x0 + 1, y, z0 + 1, x0 + 7, y + 3, z0 + 7, "flowing_water"); fill(dim, x0 + 9, y, z0 + 3, x0 + 12, y + 3, z0 + 5, "flowing_water"); };
  // A: drain while the doorway is open (it refills); B: wall the doorway first, then drain
  const ax = o.x + 1, az = o.z + 1, bx = o.x + 1, bz = o.z + 16;
  room(ax, az); room(bx, bz);
  fill(dim, ax + 8, y, az + 4, ax + 8, y + 1, az + 4, "air"); fill(dim, bx + 8, y, bz + 4, bx + 8, y + 1, bz + 4, "air");   // doorways
  await sleep(40);
  const wet = (x0, z0) => { let n = 0; for (let i = 1; i <= 7; i++) for (let j = 0; j <= 3; j++) for (let k = 1; k <= 7; k++) if (isWet(blk(dim, x0 + i, y + j, z0 + k))) n++; return n; };
  out.A_before = wet(ax, az);
  fill(dim, ax + 1, y, az + 1, ax + 7, y + 3, az + 7, "air", "replace water");
  out.A_t0 = wet(ax, az); await sleep(60); out.A_t60 = wet(ax, az);
  out.B_before = wet(bx, bz);
  fill(dim, bx + 8, y, bz + 4, bx + 8, y + 1, bz + 4, "glass");                 // seal first
  fill(dim, bx + 1, y, bz + 1, bx + 7, y + 3, bz + 7, "air", "replace water");
  out.B_t0 = wet(bx, bz); await sleep(60); out.B_t60 = wet(bx, bz);
  log(out);
}

async function main() {
  const dim = world.getDimension("overworld");
  log({ step: "start", tick: system.currentTick, area: cmd(dim, `tickingarea add ${X0} -64 ${Z0} ${X0 + 159} 320 ${Z0 + 159} wprobe true`) });
  for (let i = 0; i < 200; i++) {
    let ok = true;
    for (const [x, z] of [[X0 + 2, Z0 + 2], [X0 + 157, Z0 + 157], [X0 + 80, Z0 + 80]]) if (!blk(dim, x, Y, z)) ok = false;
    if (ok) break;
    await sleep(10);
  }
  cmd(dim, "gamerule domobspawning false"); cmd(dim, "time set noon"); cmd(dim, "weather clear");
  const run = async (name, f) => { const t = Date.now(); try { await f(); } catch (e) { log({ step: name, err: String(e), st: String(e.stack).slice(0, 400) }); } log({ step: name + ".ms", ms: Date.now() - t }); await sleep(5); };
  // 0.0.2: only the experiments that 0.0.1 ran with inert water, plus the new wake / pump tests (E0, E2, E5, E10-E12 stand)
  await run("E1", () => e1Spread(dim));
  await run("E3", () => e3Fall(dim));
  await run("E4", () => e4Infinite(dim));
  await run("E7", () => e7CustomBlocks(dim));
  await run("E8", () => e8Entities(dim));
  await run("E9", () => e9Specials(dim));
  await run("E10", () => e10Structures(dim));   // needed again: E13 places wp:box
  await run("E13", () => e13Wake(dim));
  await run("E14", () => e14Pump(dim));
  log({ step: "DONE" });
}
system.runTimeout(() => { main().catch((e) => log({ step: "main", err: String(e), st: String(e.stack) })); }, 100);
