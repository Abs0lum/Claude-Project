// waterprobe 0.0.3 (BDS only) — R10's OPEN items (his 20:35 "understand everything about it, fully"):
//  E15 minecraft:liquid_detection on NON-full blocks (cross geometry, low collision) — popped / broken / blocking / contain
//  E16 the sponge in a 3-D pool              E17 random ticks vs inert water (randomTickSpeed 300)
//  E18 inert water across a chunk UNLOAD and reload (a moat far from the player)
//  E19 water against OUR blocks (BP-02 loaded beside): roofs, ramp quarters, angled wall, furniture — contain, flow through?
//  E20 what a live flow destroys (torch, rail, flower, carpet, redstone, button, lantern, ladder) vs the API's answer
//  E21 farmland hydration distance           E22 concrete powder meeting water
// Every experiment prints one [CIVTEST] JSON line; the arenas sit in the sky (y 230) of a 10 x 10-chunk ticking area.
import * as mc from "@minecraft/server";
const { world, system, BlockPermutation } = mc;
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (t) => new Promise((r) => system.runTimeout(r, t));
const X0 = 992, Z0 = 992, Y = 230, CELL = 40;
const cellOrigin = (i) => ({ x: X0 + 4 + (i % 4) * CELL, z: Z0 + 4 + Math.floor(i / 4) * CELL });
const short = (id) => (id || "?").replace("minecraft:", "");
const LT = mc.LiquidType ? mc.LiquidType.Water : undefined;
function cmd(dim, c) { try { return dim.runCommand(c).successCount; } catch (e) { return "ERR " + String(e).slice(0, 120); } }
function fill(dim, x0, y0, z0, x1, y1, z1, id, extra = "") { return cmd(dim, `fill ${x0} ${y0} ${z0} ${x1} ${y1} ${z1} ${id} ${extra}`.trim()); }
function blk(dim, x, y, z) { try { return dim.getBlock({ x, y, z }); } catch { return undefined; } }
function cell(dim, x, y, z) {
  const b = blk(dim, x, y, z);
  if (!b) return { t: "unloaded" };
  const o = { t: short(b.typeId) };
  try { const d = b.permutation.getState("liquid_depth"); if (d !== undefined) o.d = d; } catch { /* none */ }
  try { if (b.isWaterlogged) o.wl = true; } catch { /* none */ }
  return o;
}
const wet = (b) => !!b && (b.typeId === "minecraft:water" || (() => { try { return b.isWaterlogged; } catch { return false; } })());
function setPerm(dim, x, y, z, id, states) { try { blk(dim, x, y, z).setPermutation(BlockPermutation.resolve(id, states || {})); return "ok"; } catch (e) { return "ERR " + String(e).slice(0, 100); } }
const live = (dim, x, y, z) => setPerm(dim, x, y, z, "minecraft:flowing_water", { liquid_depth: 0 });
function clearCell(dim, o, y0 = Y - 10, y1 = Y + 10) { for (let y = y0; y <= y1; y += 4) fill(dim, o.x - 2, y, o.z - 2, o.x + CELL - 6, Math.min(y + 3, y1), o.z + CELL - 6, "air"); }
function floor(dim, o, w, y = Y, id = "stone") { return fill(dim, o.x, y, o.z, o.x + w - 1, y, o.z + w - 1, id); }
function api(b) {
  const r = {};
  const q = (k, f) => { try { r[k] = f(); } catch (e) { r[k] = "ERR"; } };
  q("contain", () => b.canContainLiquid(LT)); q("blocking", () => b.isLiquidBlocking(LT)); q("destroyedBySpread", () => b.canBeDestroyedByLiquidSpread(LT));
  q("spawnsOnSpread", () => b.liquidSpreadCausesSpawn(LT)); q("flowFromN", () => b.liquidCanFlowFromDirection(LT, mc.Direction.North));
  return r;
}

// ------------------------------------------------------------------------------------------------------------ E15
async function e15(dim) {
  const o = cellOrigin(0); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1;
  const ids = ["wp:x_noreact", "wp:x_popped", "wp:x_broken", "wp:x_blocking", "wp:x_contain", "wp:low_popped", "wp:low_broken", "wp:low_contain", "wp:low_blocking"];
  const rows = [];
  for (let i = 0; i < ids.length; i++) {
    const x = o.x + 3 + (i % 5) * 6, z = o.z + 4 + Math.floor(i / 5) * 10;
    const r = { id: ids[i], place: setPerm(dim, x, y, z, ids[i]), x, z };
    r.api = (() => { const b = blk(dim, x, y, z); return b ? api(b) : null; })();
    live(dim, x + 1, y, z);                                    // a live source EAST of it
    rows.push(r);
  }
  await sleep(40);
  for (const r of rows) { r.t40 = cell(dim, r.x, y, r.z); r.west = cell(dim, r.x - 1, y, r.z); r.drops = dim.getEntities({ location: { x: r.x + 0.5, y: y + 0.5, z: r.z + 0.5 }, maxDistance: 3, type: "minecraft:item" }).map((e) => { try { return e.getComponent("minecraft:item").itemStack.typeId; } catch { return "?"; } }); }
  log({ step: "E15", what: "liquid_detection on non-full blocks (cross geometry / 4-px collision); a live source EAST of each, 40 ticks", rows });
}

// ------------------------------------------------------------------------------------------------------------ E16
async function e16(dim) {
  const o = cellOrigin(1); clearCell(dim, o, Y - 10, Y + 10);
  fill(dim, o.x, Y - 6, o.z, o.x + 16, Y + 1, o.z + 16, "stone"); fill(dim, o.x + 1, Y - 5, o.z + 1, o.x + 15, Y + 1, o.z + 15, "water");   // 15 x 15 x 7 pool
  await sleep(5);
  const count = () => { let n = 0; for (let x = o.x + 1; x <= o.x + 15; x++) for (let z = o.z + 1; z <= o.z + 15; z++) for (let yy = Y - 5; yy <= Y + 1; yy++) if (wet(blk(dim, x, yy, z))) n++; return n; };
  const before = count();
  const c = { x: o.x + 8, y: Y - 2, z: o.z + 8 };
  const place = setPerm(dim, c.x, c.y, c.z, "minecraft:sponge");
  await sleep(5);
  const after = count();
  let far = 0; for (let x = o.x + 1; x <= o.x + 15; x++) for (let z = o.z + 1; z <= o.z + 15; z++) for (let yy = Y - 5; yy <= Y + 1; yy++) if (!wet(blk(dim, x, yy, z)) && !(x === c.x && yy === c.y && z === c.z)) far = Math.max(far, Math.abs(x - c.x) + Math.abs(yy - c.y) + Math.abs(z - c.z));
  log({ step: "E16", what: "sponge in a 15 x 15 x 7 pool (placed by script at the centre)", place, before, after, absorbed: before - after, farthestDryTaxicab: far, sponge: cell(dim, c.x, c.y, c.z) });
}

// ------------------------------------------------------------------------------------------------------------ E17
async function e17(dim) {
  const o = cellOrigin(2); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1, spots = [];
  for (let i = 0; i < 6; i++) { const x = o.x + 3 + i * 5, z = o.z + 5; spots.push([x, z, [0, 3, 7, 0, 3, 7][i]]); setPerm(dim, x, y, z, "minecraft:water", { liquid_depth: [0, 3, 7, 0, 3, 7][i] }); }
  const rts = cmd(dim, "gamerule randomtickspeed 300");
  await sleep(200);
  const t200 = spots.map(([x, z, d]) => [d, cell(dim, x, y, z), (() => { let n = 0; for (let dx = -3; dx <= 3; dx++) for (let dz = -3; dz <= 3; dz++) if (wet(blk(dim, x + dx, y, z + dz))) n++; return n; })()]);
  cmd(dim, "gamerule randomtickspeed 1");
  log({ step: "E17", what: "inert water (setPermutation) under randomTickSpeed 300 for 200 ticks", gamerule: rts, t200 });
}

// ------------------------------------------------------------------------------------------------------------ E18
async function e18(dim) {
  const FX = 4800, FZ = 4800;                                   // far from everything (no player on the server)
  const out = { step: "E18", what: "inert water across a chunk unload / reload" };
  out.add = cmd(dim, `tickingarea add ${FX} -64 ${FZ} ${FX + 15} 320 ${FZ + 15} wfar true`);
  for (let i = 0; i < 60 && !blk(dim, FX + 8, Y, FZ + 8); i++) await sleep(10);
  fill(dim, FX + 1, Y, FZ + 1, FX + 14, Y, FZ + 14, "stone");
  setPerm(dim, FX + 4, Y + 1, FZ + 4, "minecraft:water", { liquid_depth: 0 });
  setPerm(dim, FX + 10, Y + 1, FZ + 10, "minecraft:water", { liquid_depth: 3 });
  await sleep(20);
  out.before = [cell(dim, FX + 4, Y + 1, FZ + 4), cell(dim, FX + 10, Y + 1, FZ + 10)];
  out.remove = cmd(dim, "tickingarea remove wfar");
  await sleep(200);
  out.whileGone = blk(dim, FX + 4, Y + 1, FZ + 4) ? "still loaded" : "unloaded";
  out.readd = cmd(dim, `tickingarea add ${FX} -64 ${FZ} ${FX + 15} 320 ${FZ + 15} wfar true`);
  for (let i = 0; i < 60 && !blk(dim, FX + 8, Y, FZ + 8); i++) await sleep(10);
  await sleep(60);
  const around = (x, z) => { let n = 0; for (let dx = -3; dx <= 3; dx++) for (let dz = -3; dz <= 3; dz++) if (wet(blk(dim, x + dx, Y + 1, z + dz))) n++; return n; };
  out.after60 = [cell(dim, FX + 4, Y + 1, FZ + 4), around(FX + 4, FZ + 4), cell(dim, FX + 10, Y + 1, FZ + 10), around(FX + 10, FZ + 10)];
  cmd(dim, "tickingarea remove wfar");
  log(out);
}

// ------------------------------------------------------------------------------------------------------------ E19
async function e19(dim) {
  const o = cellOrigin(3); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1;
  const ids = ["pw:roof45_spruce", "pw:roof45_ridge_spruce", "pw:ramp_cobble_4_q1", "pw:ramp_cobble_2_hi", "pw:angled_wall", "pw:furn_bench_oak", "pw:furn_chair_oak", "pw:planks_grid_oak"];
  const rows = [];
  for (let i = 0; i < ids.length; i++) {
    const x = o.x + 3 + (i % 4) * 8, z = o.z + 4 + Math.floor(i / 4) * 12;
    const r = { id: ids[i], place: setPerm(dim, x, y, z, ids[i]), x, z };
    const b = blk(dim, x, y, z);
    r.api = b ? api(b) : null;
    try { b.setWaterlogged(true); r.setWL = blk(dim, x, y, z).isWaterlogged; } catch (e) { r.setWL = "ERR " + String(e).slice(0, 60); }
    try { blk(dim, x, y, z).setWaterlogged(false); } catch { /* none */ }
    live(dim, x + 1, y, z);                                    // live source EAST
    setPerm(dim, x, y + 1, z + 3, ids[i]); live(dim, x, y + 2, z + 3);   // a source standing ON TOP of a second one
    rows.push(r);
  }
  await sleep(40);
  for (const r of rows) { r.t40 = cell(dim, r.x, y, r.z); r.west = cell(dim, r.x - 1, y, r.z); r.underTop = cell(dim, r.x, y, r.z + 3); r.onTopBlock = cell(dim, r.x, y + 1, r.z + 3); }
  log({ step: "E19", what: "water against our blocks: API answers, script waterlogging, a live source EAST (does it pass to WEST?), a source ON TOP (does it fall through?)", rows });
}

// ------------------------------------------------------------------------------------------------------------ E20
async function e20(dim) {
  const o = cellOrigin(4); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1;
  const ids = ["minecraft:torch", "minecraft:rail", "minecraft:poppy", "minecraft:white_carpet", "minecraft:redstone_wire", "minecraft:stone_button", "minecraft:lantern", "minecraft:ladder", "minecraft:short_grass", "minecraft:wheat", "minecraft:oak_sapling", "minecraft:tripwire"];
  const rows = [];
  for (let i = 0; i < ids.length; i++) {
    const x = o.x + 3 + (i % 6) * 5, z = o.z + 4 + Math.floor(i / 6) * 10;
    if (ids[i] === "minecraft:ladder") { setPerm(dim, x, y, z - 1, "minecraft:stone"); }
    if (ids[i] === "minecraft:wheat" || ids[i] === "minecraft:oak_sapling" || ids[i] === "minecraft:short_grass" || ids[i] === "minecraft:poppy") setPerm(dim, x, Y, z, ids[i] === "minecraft:wheat" ? "minecraft:farmland" : "minecraft:grass_block");
    const r = { id: short(ids[i]), place: setPerm(dim, x, y, z, ids[i]), x, z };
    const b = blk(dim, x, y, z); r.api = b ? api(b) : null; r.before = cell(dim, x, y, z);
    rows.push(r);
  }
  for (const r of rows) live(dim, r.x + 1, y, r.z);
  await sleep(40);
  for (const r of rows) r.t40 = cell(dim, r.x, y, r.z);
  log({ step: "E20", what: "a live source beside each block for 40 ticks: what the flow destroys, against the API's answer", rows });
}

// ------------------------------------------------------------------------------------------------------------ E21
async function e21(dim) {
  const o = cellOrigin(5); clearCell(dim, o); floor(dim, o, 34, Y, "dirt");
  const y = Y;
  setPerm(dim, o.x + 10, y, o.z + 10, "minecraft:water", { liquid_depth: 0 });       // inert source in the ground (a farm's channel)
  for (let k = 1; k <= 7; k++) { setPerm(dim, o.x + 10 + k, y, o.z + 10, "minecraft:farmland"); setPerm(dim, o.x + 10 - k, y, o.z + 10 - (k % 2), "minecraft:farmland"); }
  const rts = cmd(dim, "gamerule randomtickspeed 300");
  await sleep(200);
  cmd(dim, "gamerule randomtickspeed 1");
  const row = []; for (let k = 1; k <= 7; k++) { const b = blk(dim, o.x + 10 + k, y, o.z + 10); let m; try { m = b.permutation.getState("moisturized_amount"); } catch { m = "?"; } row.push([k, short(b ? b.typeId : "?"), m]); }
  log({ step: "E21", what: "farmland hydration by distance from one water block (randomTickSpeed 300, 200 ticks)", gamerule: rts, row, source: cell(dim, o.x + 10, y, o.z + 10) });
}

// ------------------------------------------------------------------------------------------------------------ E22
async function e22(dim) {
  const o = cellOrigin(6); clearCell(dim, o); floor(dim, o, 34);
  const y = Y + 1;
  setPerm(dim, o.x + 5, y, o.z + 5, "minecraft:white_concrete_powder"); live(dim, o.x + 6, y, o.z + 5);
  setPerm(dim, o.x + 15, y, o.z + 5, "minecraft:white_concrete_powder"); setPerm(dim, o.x + 16, y, o.z + 5, "minecraft:water", { liquid_depth: 0 });   // inert beside
  await sleep(20);
  log({ step: "E22", what: "concrete powder beside live / inert water (20 ticks)", live: cell(dim, o.x + 5, y, o.z + 5), inert: cell(dim, o.x + 15, y, o.z + 5) });
}

async function main() {
  const dim = world.getDimension("overworld");
  log({ step: "start", area: cmd(dim, `tickingarea add ${X0} -64 ${Z0} ${X0 + 159} 320 ${Z0 + 159} wprobe true`) });
  for (let i = 0; i < 200; i++) { if (blk(dim, X0 + 2, Y, Z0 + 2) && blk(dim, X0 + 157, Y, Z0 + 157)) break; await sleep(10); }
  cmd(dim, "gamerule domobspawning false"); cmd(dim, "time set noon"); cmd(dim, "weather clear");
  const run = async (name, f) => { const t = Date.now(); try { await f(); } catch (e) { log({ step: name, err: String(e), st: String(e.stack).slice(0, 400) }); } log({ step: name + ".ms", ms: Date.now() - t }); await sleep(5); };
  await run("E15", () => e15(dim));
  await run("E16", () => e16(dim));
  await run("E17", () => e17(dim));
  await run("E18", () => e18(dim));
  await run("E19", () => e19(dim));
  await run("E20", () => e20(dim));
  await run("E21", () => e21(dim));
  await run("E22", () => e22(dim));
  log({ step: "DONE" });
}
system.runTimeout(() => { main().catch((e) => log({ step: "main", err: String(e), st: String(e.stack) })); }, 100);
