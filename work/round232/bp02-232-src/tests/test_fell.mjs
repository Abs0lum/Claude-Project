// test_fell.mjs — 1.3.228 (B2 / BF10): his BIGCANOPY rule in the town — only a real, world-built tree with its natural
// leaves is felled; a player's logs never (the placed-log ledger, R4); a log pole without natural leaves never (R5); a
// structure tree (pw root) is; a tree reaching a sleeping chunk is left alone. The woodcutter's search (nextTree) passes
// a player's cabin by, and two hands never get the same tree (work-site claims, longest-untouched first).
import { treeOk, treeKnown, treeVerdict, fellTree, __setPlacedTest, FELL, blockAt, groundAt } from "../pw_civ_clock.js";
import * as WORK from "../pw_civ_work.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };

// a fake dimension: chunks with x >= 512 sleep (reads there would throw); persistent_bit per cell; setType records
function world0() {
  const m = new Map(), persist = new Set();
  const loaded = (x) => x < 512;
  const blk = (x, y, z) => ({
    typeId: m.get(`${x},${y},${z}`) || "minecraft:air", isValid: true, location: { x, y, z },
    permutation: { getState: (k) => (k === "persistent_bit" ? persist.has(`${x},${y},${z}`) : undefined) },
    setType: (id) => { if (id === "minecraft:air") m.delete(`${x},${y},${z}`); else m.set(`${x},${y},${z}`, id); },
    getComponent: () => undefined,
  });
  const dim = {
    isChunkLoaded: ({ x }) => loaded(x),
    getBlock: ({ x, y, z }) => { if (!loaded(x)) throw new Error("LocationInUnloadedChunkError"); return blk(x, y, z); },
    getTopmostBlock: ({ x, z }) => { if (!loaded(x)) throw new Error("LocationInUnloadedChunkError"); for (let y = 200; y > -64; y--) if (m.has(`${x},${y},${z}`)) return blk(x, y, z); return undefined; },
  };
  const ground = (x0, z0, x1, z1) => { for (let x = x0; x <= x1; x++) for (let z = z0; z <= z1; z++) m.set(`${x},64,${z}`, "minecraft:grass_block"); };
  const oak = (x, z, h = 5, leaf = "minecraft:oak_leaves", persistent = false) => {
    for (let y = 65; y < 65 + h; y++) m.set(`${x},${y},${z}`, "minecraft:oak_log");
    for (let y = 65 + h - 2; y <= 65 + h; y++) for (let dx = -2; dx <= 2; dx++) for (let dz = -2; dz <= 2; dz++) {
      const k = `${x + dx},${y},${z + dz}`;
      if (m.has(k)) continue;
      m.set(k, leaf); if (persistent) persist.add(k);
    }
  };
  const pole = (x, z, h = 6) => { for (let y = 65; y < 65 + h; y++) m.set(`${x},${y},${z}`, "minecraft:spruce_log"); };
  const cabin = (x0, z0) => { const cells = []; for (let y = 65; y <= 67; y++) for (let i = 0; i < 5; i++) for (const [x, z] of [[x0 + i, z0], [x0 + i, z0 + 4], [x0, z0 + i], [x0 + 4, z0 + i]]) { m.set(`${x},${y},${z}`, "minecraft:oak_log"); cells.push(`${x},${y},${z}`); } return cells; };
  return { m, persist, dim, ground, oak, pole, cabin };
}
// the ledger (R4): the cells a player placed (the real one is pw_fell_rules' per-chunk dynamic property)
const placed = new Set();
__setPlacedTest((logs) => logs.some((p) => placed.has(`${p.x},${p.y},${p.z}`)));
const none = () => false;
let now = 1000;

// ---- 1. a natural oak is felled (each case moves the clock past the verdict cache: the cells repeat)
{
  const W = world0(); W.ground(-10, -10, 10, 10); W.oak(0, 0);
  ok(treeOk(W.dim, 0, 65, 0, none, now) === true, "a natural oak may fall");
  const n = fellTree(W.dim, 0, 65, 0, none);
  ok(n === 5 && !W.m.has("0,67,0") && !W.m.has("1,68,1"), `the natural oak is felled (${n} logs, crown gone: ${W.m.get("0,67,0")} ${W.m.get("1,68,1")})`);
  ok(W.m.get("0,65,0") === "minecraft:oak_log", "a stump stays");
}
now += 10000;
// ---- 2. a player's log cabin never falls (R4) — not at the search, not at the fell
{
  const W = world0(); W.ground(0, 0, 30, 30);
  const cells = W.cabin(20, 20); for (const c of cells) placed.add(c);
  ok(treeOk(W.dim, 20, 65, 20, none, now) === false, "the cabin is refused at the search");
  const before = W.m.size;
  ok(fellTree(W.dim, 20, 65, 20, none) === 0 && W.m.size === before, "and at the fell: nothing removed");
  ok(treeVerdict(W.dim, { logs: [[20, 65, 20, "minecraft:oak_log"]], leaves: [], rooted: true, unknown: false, big: false }).why === "placed", "R4 beats a root");
  for (const c of cells) placed.delete(c);
}
now += 10000;
// ---- 3. a log pole without natural leaves never falls (R5), nor one with player (persistent) leaves
{
  const W = world0(); W.ground(-10, -10, 10, 10); W.pole(3, 3);
  ok(treeOk(W.dim, 3, 65, 3, none, now) === false, "a bare log pole is refused");
  ok(fellTree(W.dim, 3, 65, 3, none) === 0 && W.m.get("3,70,3") === "minecraft:spruce_log", "and stands after a fell attempt");
  const W2 = world0(); W2.ground(-10, -10, 10, 10); W2.oak(0, 0, 5, "minecraft:oak_leaves", true);
  ok(treeOk(W2.dim, 0, 65, 0, none, now) === false, "an oak dressed in player-placed (persistent) leaves is refused");
  const W3 = world0(); W3.ground(-10, -10, 10, 10); W3.oak(4, -4, 5, "pw:oak_mature_leaves");
  ok(treeOk(W3.dim, 4, 65, -4, none, now) === true, "pw leaves are natural");
}
now += 10000;
// ---- 4. a natural tree touching a player's log is refused whole (R4 over the flood)
{
  const W = world0(); W.ground(-10, -10, 10, 10); W.oak(0, 0);
  W.m.set("1,66,0", "minecraft:oak_log"); placed.add("1,66,0");
  ok(treeOk(W.dim, 0, 65, 0, none, now) === false, "an oak with a player's log against it is refused");
  placed.delete("1,66,0");
}
now += 10000;
// ---- 5. a structure tree (pw root under the trunk) is world-built: it may fall without counting leaves
{
  const W = world0(); W.ground(-10, -10, 10, 10);
  W.m.set("0,64,0", "pw:oak_mature_root");
  for (let y = 65; y <= 70; y++) W.m.set(`0,${y},0`, "pw:oak_mature");
  ok(treeOk(W.dim, 0, 65, 0, none, now) === true, "a rooted structure tree may fall (R3a)");
}
now += 10000;
// ---- 6. a tree reaching a sleeping chunk is left alone, and the verdict is not cached
{
  const W = world0(); W.ground(500, -5, 511, 5); W.oak(511, 0);
  const t0 = FELL.asleep;
  ok(treeOk(W.dim, 511, 65, 0, none, now) === false && FELL.asleep === t0 + 1, "a trunk against a sleeping chunk: refused (asleep)");
  ok(treeOk(W.dim, 511, 65, 0, none, now) === false && FELL.asleep === t0 + 2, "asked again, not cached");
}
now += 10000;
// ---- 7. the verdict cache: TREE_TTL ticks, then judged again
{
  const W = world0(); W.ground(-10, -10, 10, 10); W.pole(-5, -5);
  ok(treeOk(W.dim, -5, 65, -5, none, now) === false, "bare pole: refused");
  W.oak(-5, -5, 6);                                                             // leaves grow on it
  const c0 = FELL.cached;
  ok(treeOk(W.dim, -5, 65, -5, none, now + 10) === false && FELL.cached === c0 + 1, "cached within TTL");
  ok(treeOk(W.dim, -5, 65, -5, none, now + 7000) === true, "judged again after the TTL");
}

now += 10000;
// ---- 8. claims: two claimants never hold one site; release, expiry, longest-untouched first
{
  const C = WORK.createClaims(1200);
  ok(C.take("5,5", "A", 0) === true, "A claims 5,5");
  ok(C.take("5,5", "B", 10) === false && C.free("5,5", "B", 10) === false, "B cannot");
  ok(C.take("5,5", "A", 20) === true, "A may claim again (his)");
  C.release("5,5", "A", 100);
  ok(C.take("5,5", "B", 101) === true, "released: B takes it");
  ok(C.free("5,5", "A", 1302) === true, "B's claim expires after 1,200 ticks unworked");
  const C2 = WORK.createClaims(1200);
  C2.take("1,1", "B", 0); C2.renew("1,1", "B", 1000);
  ok(C2.free("1,1", "A", 1500) === false, "a renewed claim holds");
  C2.releaseAll("B", 1600);
  ok(C2.free("1,1", "A", 1601) === true, "releaseAll (off duty / body gone)");
  // longest-untouched first: a site never claimed comes before one released lately; ties keep the given (nearest) order
  const C3 = WORK.createClaims(1200);
  C3.take("0,0", "X", 0); C3.release("0,0", "X", 500);                         // touched at 500
  C3.take("9,9", "X", 0); C3.release("9,9", "X", 100);                         // touched at 100
  const cands = [{ x: 0, z: 0 }, { x: 9, z: 9 }, { x: 3, z: 3 }, { x: 4, z: 4 }];
  const order = C3.order(cands, (f) => `${f.x},${f.z}`, "Y", 600).map((f) => `${f.x},${f.z}`);
  ok(order.join(" ") === "3,3 4,4 9,9 0,0", `order: untouched (nearest first), then oldest touch (${order.join(" ")})`);
  C3.take("3,3", "Z", 600);
  ok(!C3.order(cands, (f) => `${f.x},${f.z}`, "Y", 601).some((f) => f.x === 3), "a held site is not offered to another");
}

now += 10000;
// ---- 9. the woodcutter's search: the cabin by the yard is passed by; two hands get two different real trees
{
  const W = world0(); W.ground(-30, -30, 30, 30);
  const cells = W.cabin(2, 2); for (const c of cells) placed.add(c);        // nearest to the yard: a player's cabin
  W.pole(-3, 0);                                                              // then a bare pole
  W.oak(6, -6); W.oak(-8, 7);                                                 // two real trees further out
  WORK.initWork({
    BUILDINGS: { lumberyard: {} }, footprint: () => [1, 1, 1], tierIdx: () => 0,
    occupied: () => none, groundAt: (dim, x, z) => groundAt(dim, x, z), blockAt,
    TREE_LOG: (id) => id.endsWith("_log") || /pw:[a-z_]+_(young|mature|old|elder)$/.test(id),
    treeOk: (dim, x, y, z, occ) => treeOk(dim, x, y, z, occ, now + 20000), treeKnown: (x, y, z) => treeKnown(x, y, z, now + 20000),
  });
  const yard = { family: "lumberyard", x: 0, z: 0, rot: 0 };
  const st = { tier: "village" };
  // the search asks at most 8 fresh verdicts a call and resumes its ring next beat: call it like the work beat does
  const search = (vid) => { for (let k = 0; k < 12; k++) { const t = WORK.nextTree(W.dim, yard, st, vid); if (t || !yard.treeRing) return t; } return null; };
  const t1 = search("hand-1");
  ok(t1 && !cells.includes(`${t1.x},${t1.y},${t1.z}`) && !(t1.x === -3 && t1.z === 0), `hand 1 is sent to a real tree (${t1 && [t1.x, t1.z]})`);
  yard.treeRing = 0;
  const t2 = search("hand-2");
  ok(t1 && t2 && `${t1.x},${t1.z}` !== `${t2.x},${t2.z}`, `hand 2 gets the other tree (${t2 && [t2.x, t2.z]})`);
  ok(t2 && ((t2.x === 6 && t2.z === -6) || (t2.x === -8 && t2.z === 7)), "both are the real oaks");
  yard.treeRing = 0;
  const t3 = search("hand-3");
  ok(t3 === null, "a third hand finds no free real tree (the cabin and the pole are never offered)");
  ok(WORK.claimHeld(t1.x, t1.z) && WORK.claimHeld(t2.x, t2.z), "the clock's daily clearing sees both claims");
  for (const c of cells) placed.delete(c);
}

console.log(`test_fell: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
