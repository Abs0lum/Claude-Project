// test_logic.mjs — unit tests for pw_homestead_logic.js (run: node test_logic.mjs)
import assert from "node:assert/strict";
import * as L from "./pw_homestead_logic.js";

const U = L.UNIT_TICKS;
let n = 0;
function t(name, fn) { fn(); n++; console.log("ok -", name); }

t("fuel table: planks 1, log 2, wood 2, coal 4, charcoal 4, other 0", () => {
  assert.equal(L.fuelUnitsFor("minecraft:oak_planks"), 1);
  assert.equal(L.fuelUnitsFor("minecraft:spruce_log"), 2);
  assert.equal(L.fuelUnitsFor("minecraft:stripped_oak_wood"), 2);
  assert.equal(L.fuelUnitsFor("minecraft:coal"), 4);
  assert.equal(L.fuelUnitsFor("minecraft:charcoal"), 4);
  assert.equal(L.fuelUnitsFor("minecraft:cobblestone"), 0);
  assert.equal(L.fuelUnitsFor(undefined), 0);
});

t("cold + fuel -> fueled (not lit); flint lights it for pending units", () => {
  let e = L.newEntry(1000);
  let r = L.addFuel(e, 2, 1000);           // one log
  assert.ok(r.accepted); assert.equal(r.entry.phase, "fueled"); assert.equal(r.entry.pending, 2);
  const ig = L.ignite(r.entry, 1200);
  assert.ok(ig.lit); assert.equal(ig.entry.phase, "lit"); assert.equal(ig.entry.litUntil, 1200 + 2 * U);
});

t("flint on cold without fuel does nothing", () => {
  const ig = L.ignite(L.newEntry(0), 5);
  assert.equal(ig.lit, false); assert.equal(ig.entry.phase, "cold");
});

t("lit -> embers at litUntil; embers last 2x the lit phase (one log: 1/2 day lit -> 1 day embers)", () => {
  let e = L.ignite(L.addFuel(L.newEntry(0), 2, 0).entry, 0).entry;   // lit for 2U
  let a = L.advance(e, 2 * U - 1); assert.equal(a.entry.phase, "lit");
  a = L.advance(e, 2 * U); assert.equal(a.entry.phase, "embers"); assert.ok(a.changed);
  assert.equal(a.entry.emberUntil, 2 * U + 2 * (2 * U));            // = 6U -> embers for 4U = 1 day
  a = L.advance(a.entry, 6 * U - 1); assert.equal(a.entry.phase, "embers");
  a = L.advance(a.entry, 6 * U); assert.equal(a.entry.phase, "spent");   // v2: charcoal stays (was cold)
});

t("adding fuel while lit extends the burn without relighting", () => {
  let e = L.ignite(L.addFuel(L.newEntry(0), 1, 0).entry, 0).entry;   // 1U
  const r = L.addFuel(e, 4, 100);                                     // coal
  assert.ok(r.accepted); assert.equal(r.relit, false); assert.equal(r.entry.phase, "lit");
  assert.equal(r.entry.litUntil, 5 * U);
});

t("adding fuel on embers relights without flint & steel", () => {
  let e = L.ignite(L.addFuel(L.newEntry(0), 1, 0).entry, 0).entry;
  e = L.advance(e, U).entry; assert.equal(e.phase, "embers");
  const r = L.addFuel(e, 1, U + 10);
  assert.ok(r.accepted && r.relit); assert.equal(r.entry.phase, "lit"); assert.equal(r.entry.litAt, U + 10);
  assert.equal(r.entry.litUntil, U + 10 + U);
});

t("embers duration follows the WHOLE lit phase incl. top-ups", () => {
  let e = L.ignite(L.addFuel(L.newEntry(0), 1, 0).entry, 0).entry;   // lit 0..U
  e = L.addFuel(e, 1, 10).entry;                                      // lit until 2U
  const a = L.advance(e, 2 * U);
  assert.equal(a.entry.phase, "embers"); assert.equal(a.entry.emberUntil, 2 * U + 2 * (2 * U));
});

t("stockpile cap refuses fuel beyond MAX_AHEAD_UNITS (item not consumed)", () => {
  let e = L.newEntry(0);
  for (let i = 0; i < 16; i++) e = L.addFuel(e, 1, 0).entry;
  const r = L.addFuel(e, 1, 0);
  assert.equal(r.accepted, false); assert.equal(r.entry.pending, 16);
});

t("expired entries advance before an interaction is applied", () => {
  let e = L.ignite(L.addFuel(L.newEntry(0), 1, 0).entry, 0).entry;   // lit 0..U, embers U..3U
  const r = L.addFuel(e, 1, 10 * U);                                  // long cold by now
  assert.equal(r.entry.phase, "fueled"); assert.equal(r.entry.pending, 1);
});

t("nextInList cycles and recovers from unknown", () => {
  assert.equal(L.nextInList(["a", "b", "c"], "a"), "b");
  assert.equal(L.nextInList(["a", "b", "c"], "c"), "a");
  assert.equal(L.nextInList(["a", "b", "c"], "zz"), "a");
});

t("frontOffset / oppositeDir", () => {
  assert.deepEqual(L.frontOffset("north"), { x: 0, z: -1 });
  assert.deepEqual(L.frontOffset("east"), { x: 1, z: 0 });
  assert.equal(L.oppositeDir("west"), "east");
});



// ---- v2 (2026-09-22): spent phase, chimney hazard, air model, entry rule
t("embers expire into SPENT (charcoal stays), fuel on spent -> fueled, flint lights it", () => {
  let e = L.newEntry(0);
  e = L.addFuel(e, 1, 0).entry; e = L.ignite(e, 0).entry;            // lit for 1 unit
  let a = L.advance(e, U); assert.equal(a.entry.phase, "embers");
  a = L.advance(a.entry, U + L.EMBER_FACTOR * U); assert.equal(a.entry.phase, "spent");
  const f = L.addFuel(a.entry, 2, 3 * U + 5); assert.ok(f.accepted); assert.equal(f.entry.phase, "fueled"); assert.equal(f.entry.pending, 2);
  const ig = L.ignite(f.entry, 3 * U + 6); assert.ok(ig.lit); assert.equal(ig.entry.phase, "lit");
  assert.match(L.describe(a.entry, 3 * U), /burnt out/);
});

t("hazard: lit = heat + fire, embers = heat only, spent/fueled/cold = nothing", () => {
  assert.deepEqual(L.hazardFor("lit"), { heat: true, fire: true });
  assert.deepEqual(L.hazardFor("embers"), { heat: true, fire: false });
  for (const p of ["spent", "fueled", "cold"]) assert.deepEqual(L.hazardFor(p), { heat: false, fire: false });
});

t("air model: first hit after 320 ticks inside, then every 20; +4 per tick outside, capped at 300", () => {
  let air = L.AIR_MAX, hits = [];
  for (let tick = 1; tick <= 400; tick++) { const r = L.airStep(air, true); air = r.air; if (r.damage) hits.push(tick); }
  assert.deepEqual(hits.slice(0, 4), [320, 340, 360, 380]);
  assert.equal(L.airStep(0, false).air, 4);
  assert.equal(L.airStep(299, false).air, 300);
  assert.equal(L.airStep(-5, false).air, -1);
});

t("chute entry: legal only straight down/up the same column", () => {
  assert.ok(L.legalChuteEntry({ x: 3, y: 70, z: 9 }, { x: 3, y: 69, z: 9 }));
  assert.ok(L.legalChuteEntry({ x: 3, y: 68, z: 9 }, { x: 3, y: 69, z: 9 }));
  assert.ok(!L.legalChuteEntry({ x: 4, y: 69, z: 9 }, { x: 3, y: 69, z: 9 }));
  assert.ok(!L.legalChuteEntry(undefined, { x: 3, y: 69, z: 9 }));
});


// ---- ROOM SMOKE (v1.3.185, D-C228) ------------------------------------------------------------------------------------
const st = (states) => (k) => states[k];
t("smoke passes: air, open doors/trapdoors/gates, thin fittings, furniture, rafters, old markers, open manhole", () => {
  for (const id of ["minecraft:air", "minecraft:cave_air", "minecraft:torch", "minecraft:wall_torch", "minecraft:white_carpet", "minecraft:oak_wall_sign",
                    "minecraft:rail", "minecraft:stone_button", "minecraft:lantern", "minecraft:soul_lantern", "minecraft:ladder", "minecraft:vine",
                    "minecraft:flower_pot", "minecraft:white_candle", "minecraft:skeleton_skull", "minecraft:chain", "minecraft:light_block_7",
                    "pw:furn_table_oak", "pw:furn_chair_spruce", "pw:rafter45_oak", "pw:zone_kitchen", "pw:station_seat", "pw:datum"])
    assert.equal(L.smokePasses(id, st({})), true, id);
  assert.equal(L.smokePasses("minecraft:wooden_door", st({ open_bit: true })), true);
  assert.equal(L.smokePasses("minecraft:spruce_trapdoor", st({ open_bit: true })), true);
  assert.equal(L.smokePasses("minecraft:fence_gate", st({ open_bit: true })), true);
  assert.equal(L.smokePasses("pw:manhole_cover", st({ "pw:phase": 5 })), true);
});
t("smoke stops: walls, CLOSED doors/trapdoors/gates, glass, liquids, hearth/flue/wall pieces, sea lantern, unknown blocks", () => {
  for (const id of ["minecraft:oak_planks", "minecraft:stone_bricks", "minecraft:glass", "minecraft:glass_pane", "minecraft:water", "minecraft:lava",
                    "minecraft:sea_lantern", "minecraft:oak_stairs", "minecraft:oak_slab", "minecraft:chest",
                    "pw:hearth_oak_planks", "pw:flue_stone_bricks", "pw:wall_oak_planks", "pw:roof45_thatch", "pw:frame_post", "somemod:thing", "", undefined])
    assert.equal(L.smokePasses(id, st({})), false, String(id));
  assert.equal(L.smokePasses("minecraft:wooden_door", st({ open_bit: false })), false);
  assert.equal(L.smokePasses("minecraft:iron_trapdoor", st({ open_bit: false })), false);
  assert.equal(L.smokePasses("minecraft:spruce_fence_gate", st({})), false, "gate with no open_bit reads closed");
  assert.equal(L.smokePasses("pw:manhole_cover", st({ "pw:phase": 0 })), false);
});
// a 5 x 3 x 5 room (interior x 1..5, y 1..3, z 1..5) inside a shell of planks; the hearth sits in the west wall at (0,1,3) facing east
function world(opts = {}) {
  const cells = new Map();
  for (let x = 0; x <= 6; x++) for (let y = 0; y <= 4; y++) for (let z = 0; z <= 6; z++) {
    const inside = x >= 1 && x <= 5 && y >= 1 && y <= 3 && z >= 1 && z <= 5;
    cells.set(`${x},${y},${z}`, inside ? "minecraft:air" : "minecraft:oak_planks");
  }
  cells.set("3,2,3", "pw:furn_table_oak"); cells.set("2,1,2", "pw:furn_chair_oak");
  if (opts.door) cells.set("6,1,3", "minecraft:wooden_door"), cells.set("6,2,3", "minecraft:wooden_door");
  const states = { open_bit: !!opts.doorOpen };
  return (x, y, z) => {
    const id = cells.get(`${x},${y},${z}`) ?? "minecraft:air";            // outside the shell: open air
    return opts.oldBug ? true : L.smokePasses(id, (k) => states[k]);      // oldBug = every block reads 'not solid' (isSolid undefined)
  };
}
const START = { x: 1, y: 1, z: 3 }, ORIGIN = { x: 0, y: 1, z: 3 };
t("enclosed room: CLOSED (smoke builds), 75 cells counting the furniture cells", () => {
  const r = L.floodRoom(world(), START, ORIGIN, 400, 12);
  assert.equal(r.open, false); assert.equal(r.cells.length, 75);
});
t("REGRESSION D-C228: with the v1.3.184 behaviour (every block passable) the same room reads OPEN — smoke could never build", () => {
  const r = L.floodRoom(world({ oldBug: true }), START, ORIGIN, 400, 12);
  assert.equal(r.open, true);
});
t("a closed door keeps the room closed; opening it lets the smoke out", () => {
  assert.equal(L.floodRoom(world({ door: true, doorOpen: false }), START, ORIGIN, 400, 12).open, false);
  assert.equal(L.floodRoom(world({ door: true, doorOpen: true }), START, ORIGIN, 400, 12).open, true);
});
t("a room bigger than the cell cap (or an unloaded cell) reads open", () => {
  const hall = (x, y, z) => (y >= 0 && y <= 4) ? true : false;           // an endless open floor: the radius stops it
  assert.equal(L.floodRoom(hall, START, ORIGIN, 400, 12).open, true);
  const unloaded = (x, y, z) => (x > 3 ? undefined : L.smokePasses(y === 1 ? "minecraft:air" : "minecraft:oak_planks", () => undefined));
  assert.equal(L.floodRoom(unloaded, START, ORIGIN, 400, 12).open, true);
});

console.log(`\n${n} tests passed`);
