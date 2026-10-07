// test_hygiene.mjs — 1.3.228 (B1 hygiene): the exported guarded readers never send a read into a sleeping chunk (a thrown
// engine error leaks ~650 B); groundAt walks past the trees; boxLoaded sees every chunk of a box; R5 through blockAt
import { blockAt, topAt, groundAt, boxLoaded, naturalCanopy, ENGINE } from "../pw_civ_clock.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
// a fake dimension: chunks with x >= 64 sleep; getBlock / getTopmostBlock there THROW (and are counted)
function world0() {
  const m = new Map(), stat = { asleepReads: 0, reads: 0, asks: 0 };
  const loaded = (x) => x < 64;
  const blk = (x, y, z) => ({ typeId: m.get(`${x},${y},${z}`) || "minecraft:air", isValid: true, location: { x, y, z }, permutation: { getState: (k) => (k === "persistent_bit" ? m.get(`p${x},${y},${z}`) === true : undefined) } });
  const dim = {
    isChunkLoaded: ({ x }) => { stat.asks++; return loaded(x); },
    getBlock: ({ x, y, z }) => { stat.reads++; if (!loaded(x)) { stat.asleepReads++; throw new Error("LocationInUnloadedChunkError"); } return blk(x, y, z); },
    getTopmostBlock: ({ x, z }) => { stat.reads++; if (!loaded(x)) { stat.asleepReads++; throw new Error("LocationInUnloadedChunkError"); } for (let y = 200; y > -64; y--) if (m.has(`${x},${y},${z}`) && m.get(`${x},${y},${z}`) !== "minecraft:water") return blk(x, y, z); return undefined; },
  };
  return { m, dim, stat };
}
const t0 = ENGINE.throws;
{
  const { m, dim, stat } = world0();
  for (let y = 60; y <= 64; y++) m.set(`5,${y},5`, "minecraft:dirt");
  m.set("5,64,5", "minecraft:grass_block");
  for (let y = 65; y <= 70; y++) m.set(`5,${y},5`, "minecraft:oak_log");
  for (let y = 71; y <= 73; y++) m.set(`5,${y},5`, "minecraft:oak_leaves");
  ok(groundAt(dim, 5, 5) === 64, `ground under a tree: ${groundAt(dim, 5, 5)}`);
  const t = topAt(dim, 5, 5);
  ok(t && t.location.y === 73, "topAt = the crown");
  ok(groundAt(dim, 5, 5, t) === 64, "groundAt from a pre-read top");
  ok(blockAt(dim, 70, 64, 5) === null, "a sleeping chunk: null");
  ok(blockAt(dim, 5, 400, 5) === undefined && blockAt(dim, 5, -70, 5) === undefined, "outside the world: undefined");
  ok(topAt(dim, 80, 5) === undefined && groundAt(dim, 80, 5) === undefined, "a sleeping column: undefined");
  const asks = stat.asks;
  ok(blockAt(dim, 5, 66, 5, true).typeId === "minecraft:oak_log" && stat.asks === asks, "loaded = true skips the ask");
  ok(boxLoaded(dim, 0, 0, 63, 63) === true, "a loaded box");
  ok(boxLoaded(dim, 40, 0, 70, 15) === false && boxLoaded(dim, 0, 0, 64, 0) === false, "a box touching a sleeping chunk");
  ok(boxLoaded(dim, 48, 0, 63, 200) === true, "a long box in loaded chunks");
  ok(stat.asleepReads === 0, `no read reached a sleeping chunk (${stat.asleepReads})`);
}
{
  const { m, dim, stat } = world0();
  // R5: natural leaves round the logs; persistent ones do not count; a trunk at the edge of the loaded land reads no further
  for (let y = 65; y <= 68; y++) m.set(`63,${y},0`, "minecraft:oak_log");          // x 63: its +x neighbours sleep (x 64)
  m.set("62,68,0", "minecraft:oak_leaves"); m.set("63,69,0", "minecraft:oak_leaves"); m.set("63,68,1", "minecraft:oak_leaves");
  const logs = [65, 66, 67, 68].map((y) => ({ x: 63, y, z: 0 }));
  ok(naturalCanopy(dim, logs, 3) === true, "three natural leaves");
  m.set("p62,68,0", true); m.set("p63,69,0", true);
  ok(naturalCanopy(dim, logs, 3) === false, "persistent leaves are a player's");
  ok(stat.asleepReads === 0, `R5 never read the sleeping chunk at x 64 (${stat.asleepReads})`);
}
ok(ENGINE.throws === t0, `engine throws flat (${ENGINE.throws - t0})`);
console.log(`test_hygiene: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
