// test_canopy.mjs — 1.3.227 (his 00:54): the bare-tree measure (rootless path): a full oak keeps, a bare trunk goes,
// building logs are never a tree, an unloaded neighbour leaves the tree alone
import { canopyOf } from "../pw_civ_clock.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
function world0() {
  const m = new Map();
  const dim = { isChunkLoaded: ({ x }) => x <= 900, getBlock: ({ x, y, z }) => { if (x > 900) throw new Error("unloaded"); const id = m.get(`${x},${y},${z}`); return id ? { typeId: id, isValid: true, permutation: { getState: () => undefined } } : { typeId: "minecraft:air", isValid: true, permutation: { getState: () => undefined } }; } };
  return { m, dim };
}
const none = () => false;
// a full oak: trunk 5, crown 5x5x2 + 3x3x2 minus trunk cells
{
  const { m, dim } = world0();
  for (let y = 65; y <= 69; y++) m.set(`0,${y},0`, "minecraft:oak_log");
  for (let y = 67; y <= 68; y++) for (let x = -2; x <= 2; x++) for (let z = -2; z <= 2; z++) if (x || z) m.set(`${x},${y},${z}`, "minecraft:oak_leaves");
  for (let y = 69; y <= 70; y++) for (let x = -1; x <= 1; x++) for (let z = -1; z <= 1; z++) if (!m.has(`${x},${y},${z}`)) m.set(`${x},${y},${z}`, "minecraft:oak_leaves");
  const t = canopyOf(dim, [0, 66, 0], none, new Set());
  ok(t && t.logs.length === 5, "5 logs");
  ok(t && t.leaves.length >= 0.3 * t.original, `full oak kept (${t && t.leaves.length}/${t && t.original})`);
}
// a bare trunk 14 tall with 3 leaves left
{
  const { m, dim } = world0();
  for (let y = 65; y <= 78; y++) m.set(`5,${y},5`, "minecraft:spruce_log");
  m.set("6,78,5", "minecraft:spruce_leaves"); m.set("4,78,5", "minecraft:spruce_leaves"); m.set("5,79,5", "minecraft:spruce_leaves");
  const t = canopyOf(dim, [5, 70, 5], none, new Set());
  ok(t && t.leaves.length < 0.3 * t.original, `bare trunk goes (${t && t.leaves.length}/${t && t.original})`);
}
// building logs: inside the volume they are not a tree
{
  const { m, dim } = world0();
  for (let y = 65; y <= 70; y++) m.set(`20,${y},20`, "minecraft:oak_log");
  const t = canopyOf(dim, [20, 66, 20], (x, y, z) => x >= 18 && x <= 25 && z >= 18 && z <= 25 && y <= 80, new Set());
  ok(t === null, "a house's post is no tree");
}
// a trunk reaching an unloaded chunk is left alone
{
  const { m, dim } = world0();
  for (let y = 65; y <= 70; y++) m.set(`900,${y},0`, "minecraft:oak_log");
  m.set("901,70,0", "minecraft:oak_log");
  const t = canopyOf(dim, [900, 66, 0], none, new Set());
  ok(t === null, "unloaded neighbour -> unknown");
}
console.log(`test_canopy: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
