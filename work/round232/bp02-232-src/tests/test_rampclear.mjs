// test_rampclear.mjs — 1.3.231: RAMPS-231's mock-world test of rampclear, run against the applied KIT.rampClear
// (pw_civ_streets.js; the clock's pw:clock handler calls it). Usage: node tests/test_rampclear.mjs
import * as KIT from "../pw_civ_streets.js";
const handler = (cmd, a, s, reply, planOf, world, sys) => reply(KIT.rampClear(s, a, planOf, world, sys));
let pass = 0, fail = 0; const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const f = { ox: 0, oz: 0, ux: 1, uz: 0, vx: 0, vz: 1 };
const plan = { segs: [{ kind: "flat", a: 0, len: 4, H: 70 }, { kind: "ramp", a: 4, len: 8, H: 70, dir: -1 }, { kind: "flat", a: 12, len: 4, H: 69 }] };
const blocks = new Map(); const K = (x, y, z) => `${x},${y},${z}`;
const { pieces } = KIT.piecesOf(f, plan, "v", 0); const rp = pieces.find((p) => p.kind === "ramp");
const H = rp.y + 15;
for (let t = 4; t < 12; t++) for (let w = 0; w <= 12; w++) { const [x, z] = KIT.cellOf(f, t, w); blocks.set(K(x, H, z), w === 0 || w === 12 ? "minecraft:stone_bricks" : t === 4 ? "pw:ramp_x" : "minecraft:dirt"); blocks.set(K(x, H + 1, z), "minecraft:grass_block"); }
const outside = KIT.cellOf(f, 2, 5); blocks.set(K(outside[0], H, outside[1]), "minecraft:dirt");
const unloadedCell = KIT.cellOf(f, 11, 6);
const dim = { isChunkLoaded: ({ x, z }) => !(x === unloadedCell[0] && z === unloadedCell[1]),
  getBlock: ({ x, y, z }) => { const k = K(x, y, z); return { isValid: true, get typeId() { return blocks.get(k) || "minecraft:air"; }, setType(id) { blocks.set(k, id); } }; } };
const world = { getDimension: () => dim };
const s = { settlements: [{ dim: "overworld", streets: [{ kind: "kit", id: 1, f, tmin: 0, plan }] }] };
let msg = ""; const reply = (m) => { msg = m; };
const snap = new Map(blocks);
const timers = []; const sys = { runTimeout: (fn) => timers.push(fn) };
handler("rampclear", undefined, s, reply, (st) => st.plan, world, sys);
ok([...blocks].every(([k, v]) => snap.get(k) === v), "dry run changes nothing");
ok(/1 ramp piece/.test(msg) && /1 column/.test(msg), "dry run reports pieces + unloaded: " + msg);
handler("rampclear", "go", s, reply, (st) => st.plan, world, sys);
let dirtLeft = 0, keptBricks = 0, keptPw = 0;
for (let t = 4; t < 12; t++) for (let w = 0; w <= 12; w++) { const [x, z] = KIT.cellOf(f, t, w); const v = blocks.get(K(x, H, z)); const v1 = blocks.get(K(x, H + 1, z));
  const unl = x === unloadedCell[0] && z === unloadedCell[1];
  if (!unl && (v === "minecraft:dirt" || v1 === "minecraft:grass_block")) dirtLeft++;
  if (v === "minecraft:stone_bricks") keptBricks++; if (v === "pw:ramp_x") keptPw++; }
ok(dirtLeft === 0, "all natural ground over the lane cut, left=" + dirtLeft);
ok(keptBricks === 16 && keptPw === 11, `structure blocks kept (bricks ${keptBricks}/16, pw ${keptPw}/11)`);
ok(blocks.get(K(unloadedCell[0], H, unloadedCell[1])) === "minecraft:dirt", "unloaded column untouched");
ok(blocks.get(K(outside[0], H, outside[1])) === "minecraft:dirt", "cells outside ramp pieces untouched");
console.log(`rampclear: ${pass} pass, ${fail} fail`); if (fail) process.exit(1);
{ // force: a lane cell the server holds as AIR at y = H gets dirt now, air one tick later; sidewalks/curbs untouched
  const [lx, lz] = KIT.cellOf(f, 6, 6); blocks.set(K(lx, H, lz), "minecraft:air");
  const [cx, cz] = KIT.cellOf(f, 6, 3); const curb = blocks.get(K(cx, H, cz));
  handler("rampclear", "force", s, reply, (st) => st.plan, world, sys);
  ok(blocks.get(K(lx, H, lz)) === "minecraft:dirt" && timers.length > 0, "force: air lane cell rewritten to dirt first");
  timers.splice(0).forEach((fn) => fn());
  ok(blocks.get(K(lx, H, lz)) === "minecraft:air", "force: then back to air (two block updates sent)");
  ok(blocks.get(K(cx, H, cz)) === curb, "force: curb cell untouched");
  console.log(`rampclear force: ${pass} pass, ${fail} fail`); if (fail) process.exit(1);
}
