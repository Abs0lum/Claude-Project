// scratch evidence (not a deliverable test): the real survey on the same fake world — 1.3.232 vs HOOK-PROPOSAL Part A as written
const which = process.argv[2];
const C = await import(which === "prop" ? "./pw_civ_clock_prop.js" : "./pw_civ_clock.js");
function run(n, slots) {
  const st = { id: 1, dim: "overworld", square: { x: 0, z: 0, y: 63 }, log: [], tier: "town3" };
  const s = { settlements: [st], buildings: [], simDays: 0, tick: { slots, areas: {}, next: 1 } };
  const home = [-48, -48, 60, 60];
  const inBox = (b, x, z) => x >= b[0] && x <= b[2] && z >= b[1] && z <= b[3];
  const loaded = (x, z) => inBox(home, x, z) || Object.values(s.tick.areas).some((a) => inBox(a.box, x, z));
  let reads = 0;
  const dim = { isChunkLoaded: ({ x, z }) => loaded(x, z),
    getTopmostBlock: ({ x, z }) => { reads++; if (!loaded(x, z)) throw new Error("u"); return { typeId: "minecraft:grass_block", location: { x, y: 63, z }, isValid: true }; },
    getBlock: ({ x, y, z }) => { if (!loaded(x, z)) throw new Error("u"); return { typeId: y <= 63 ? "minecraft:grass_block" : "minecraft:air", location: { x, y, z }, isValid: true }; } };
  const was = console.warn; console.warn = () => {};
  let site = null, day = 0, maxA = 0, maxR = 0, tot = 0;
  try { while (!site && day < 60) { day++; s.simDays = day; reads = 0; site = which === "prop" ? C.palaceSite(s, st, dim) : C.palaceSite(s, st, dim, n); maxA = Math.max(maxA, Object.keys(s.tick.areas).length); maxR = Math.max(maxR, reads); tot += reads; } } finally { console.warn = was; }
  return `${which} n${n} slots ${slots}: ${site ? `ACCEPTED day ${day} (relief ${site.relief})` : `NOT accepted in ${day} days`}; max areas ${maxA}; max reads/day ${maxR}; total reads ${tot}`;
}
for (const slots of [2, 3, 4]) console.log(run(4, slots));
if (which !== "prop") console.log(run(2, 2));
