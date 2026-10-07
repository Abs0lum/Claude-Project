// test_markers.mjs — mock-run of pw_markers.js (Markers v0.2.0). Run from a dir whose node_modules/@minecraft/server is
// mock_server.mjs; argv[2] = BP root (entity JSON for the data-driven events). Prints "MOCK OK" or the failures.
import fs from "node:fs";
const BP = process.argv[2];
globalThis.__ENTITY_DEFS = {
  "pw:marker": JSON.parse(fs.readFileSync(BP + "/entities/pw_marker.json", "utf8"))["minecraft:entity"],
  "pw:hatch_lid": JSON.parse(fs.readFileSync(BP + "/entities/pw_hatch_lid.json", "utf8"))["minecraft:entity"],
};
const S = await import("@minecraft/server");
const M = await import("./pw_markers.js");
const { world, system, OVERWORLD: dim, Player, GameMode, Direction, _log } = S;
let fails = 0, passes = 0;
const ok = (c, m) => { if (c) passes++; else { fails++; console.log("FAIL " + m); } };
const P = new Player(dim, "Abs0lum", { x: 0.5, y: 65, z: 0.5 }); dim.addPlayer(P);
const tap = (block, face, itemId, opts = {}) => {
  const ev = { block, blockFace: face, faceLocation: { x: 0, y: 0, z: 0 }, isFirstEvent: opts.first !== false, itemStack: itemId ? new S.ItemStack(itemId) : undefined, player: P, cancel: false };
  world.beforeEvents.playerInteractWithBlock.fire(ev); system._advance(1); return ev;
};
const markers = () => dim.getEntities({ type: M.MARKER });
const at = (x, y, z) => dim.getEntitiesAtBlockLocation({ x, y, z }).filter((e) => e.typeId === M.MARKER);
const cmd = (id, message) => system.afterEvents.scriptEventReceive.fire({ id, message, sourceEntity: P });

// 0 the frozen icon table
ok(M.ICONS.length === 35 && M.ICONS[4][1] === "kitchen" && M.ICONS[12 + 13][1] === "seat" && M.ICONS[34][0] === "datum", "icon table 35 (kitchen=4, seat=25, datum=34)");
ok(M.classify("pw:zone_kitchen").icon === 4 && M.classify("pw:station_seat").icon === 25 && M.classify("pw:port_stair").icon === 32 && M.classify("pw:datum").icon === 34 && M.classify("minecraft:oak_planks") === null, "classify");
// 1 zone placement: tap the floor's top face -> the cell above; cancel set; properties + tags
const floor = dim.setBlock({ x: 0, y: 64, z: 0 }, "minecraft:oak_planks");
let ev = tap(floor, Direction.Up, "pw:zone_kitchen");
let e = at(0, 65, 0)[0];
ok(ev.cancel === true, "intercept cancels the block placement");
ok(e && e.getProperty("pw:fam") === 0 && e.getProperty("pw:icon") === 4 && e.getProperty("pw:n") === 0 && e.getProperty("pw:vis") === true, "zone marker spawned in the cell above the tapped face, fam 0 icon 4 n 0 visible");
ok(e && e.location.x === 0.5 && e.location.y === 65 && e.location.z === 0.5, "marker sits at the cell floor centre");
ok(e && e.hasTag("civ:marker") && e.hasTag("civ:zone") && e.hasTag("civ:kind:kitchen") && e.hasTag("civ:n:0"), "tags carry kind + number in words");
ok(e && e.getRotation().y === 0, "rotation forced to 0");
ok(e && e.groups.has("pw:hittable") && e.def.components["minecraft:collision_box"].width === 0 && e.def.components["minecraft:collision_box"].height === 0, "a new marker is hittable (hit box group) while its collision box is 0 x 0");
ok(dim.getBlock({ x: 0, y: 65, z: 0 }).isAir, "no block placed");
tap(floor, Direction.North, "pw:zone_kitchen");       // second corner: north face of the floor block -> cell z-1
ok(at(0, 64, -1)[0] && at(0, 64, -1)[0].getProperty("pw:n") === 1, "second corner #1 in front of the north face");
ev = tap(floor, Direction.Up, "pw:zone_kitchen", { first: false });
ok(ev.cancel === true && markers().length === 2, "repeat (isFirstEvent false) cancels but spawns nothing");
tap(floor, Direction.East, "pw:zone_yard");
ok(at(1, 64, 0)[0] && at(1, 64, 0)[0].getProperty("pw:n") === 0 && _log.some((l) => l.includes("ring begun: yard")), "a new kind begins a new ring at #0");
cmd("civ:zone", "status"); ok(_log[_log.length - 1].includes("open ring: yard, next corner #1"), "civ:zone status");
cmd("civ:zone", "close"); ok(_log[_log.length - 1].includes("ring closed: yard, 1 corners"), "civ:zone close");
tap(floor, Direction.West, "pw:zone_yard"); ok(at(-1, 64, 0)[0].getProperty("pw:n") === 0, "after close the ring restarts at #0");
// ring survives a reload (in-memory map cleared -> read back from the player's dynamic property)
ok(typeof P.getDynamicProperty("civ:zone_ring") === "string" && JSON.parse(P.getDynamicProperty("civ:zone_ring")).idx === 1, "open ring mirrored to the player dynamic property");
// 2 SNEAK tap: the tapped block's own cell (a chair)
const chair = dim.setBlock({ x: 3, y: 65, z: 3 }, "pw:furn_chair_oak");
P.isSneaking = true; tap(chair, Direction.Up, "pw:station_seat"); P.isSneaking = false;
e = at(3, 65, 3)[0];
ok(e && e.getProperty("pw:fam") === 1 && e.getProperty("pw:icon") === 25 && e.getProperty("pw:n") === 0 && dim.getBlock({ x: 3, y: 65, z: 3 }).typeId === "pw:furn_chair_oak", "sneak-tap puts the seat station INSIDE the chair's cell; the chair stays");
tap(floor, Direction.Up, "pw:station_seat"); tap(floor, Direction.Up, "pw:station_seat");
ok(at(0, 65, 0).map((m) => m.getProperty("pw:n")).includes(2), "station numbering 0,1,2 per role");
cmd("civ:station", "reset"); tap(floor, Direction.South, "pw:station_seat"); ok(at(0, 64, 1)[0].getProperty("pw:n") === 0, "civ:station reset");
tap(floor, Direction.South, "pw:port_stair"); ok(at(0, 64, 1).some((m) => m.getProperty("pw:fam") === 2 && m.getProperty("pw:icon") === 32), "port marker fam 2");
tap(floor, Direction.South, "pw:datum"); ok(at(0, 64, 1).some((m) => m.getProperty("pw:fam") === 3 && m.getProperty("pw:n") === 0), "datum marker fam 3 (shares the cell with other markers)");
// 3 survival consumes one item
P.mode = GameMode.Survival; const inv = P.getComponent("minecraft:inventory").container; inv.setItem(0, new S.ItemStack("pw:zone_garden", 3));
tap(floor, Direction.Up, "pw:zone_garden"); ok(inv.getItem(0).amount === 2, "survival: the held stack loses one"); P.mode = GameMode.Creative;
// 4 fallback: the block got placed anyway
const placed = dim.setBlock({ x: 7, y: 65, z: 7 }, "pw:zone_cellar", { "pw:idx": 0, "pw:ring": 0 });
world.afterEvents.playerPlaceBlock.fire({ block: placed, player: P, dimension: dim });
ok(dim.getBlock({ x: 7, y: 65, z: 7 }).isAir && at(7, 65, 7).length === 1, "fallback: a placed marker block becomes air + one entity");
const n0 = markers().length; tap(floor, Direction.Up, "pw:zone_commons");
const placed2 = dim.setBlock({ x: 0, y: 65, z: 0 }, "pw:zone_commons", {}); world.afterEvents.playerPlaceBlock.fire({ block: placed2, player: P, dimension: dim });
ok(markers().length === n0 + 1 && dim.getBlock({ x: 0, y: 65, z: 0 }).isAir, "fallback after a successful intercept: block removed, no double marker");
// 5 hide / show
cmd("civ:markers", "hide");
ok(markers().every((m) => m.getProperty("pw:vis") === false && !m.groups.has("pw:hittable")), "hide: every marker invisible + no hit box");
tap(floor, Direction.Up, "pw:zone_quarters"); ok(at(0, 65, 0).some((m) => m.getProperty("pw:icon") === 5 && m.getProperty("pw:vis") === false), "a marker placed while hidden is hidden");
const hid = at(0, 65, 0).find((m) => m.getProperty("pw:icon") === 5);
world.afterEvents.entityHitEntity.fire({ damagingEntity: P, hitEntity: hid }); ok(hid.isValid, "hitting a hidden marker does nothing");
cmd("civ:markers", "show"); ok(markers().every((m) => m.getProperty("pw:vis") === true && m.groups.has("pw:hittable")), "show: visible + hit box back");
// 6 hit to remove (+ item back in survival)
P.mode = GameMode.Survival; const before = inv.items.length;
world.afterEvents.entityHitEntity.fire({ damagingEntity: P, hitEntity: hid });
ok(!hid.isValid && inv.items.length === before + 1 && inv.items[inv.items.length - 1].typeId === "pw:zone_quarters", "hit removes a visible marker; survival gets pw:zone_quarters back"); P.mode = GameMode.Creative;
// 7 migrate old blocks
dim.setBlock({ x: 10, y: 65, z: 10 }, "pw:zone_kitchen", { "pw:idx": 3, "pw:ring": 1 });
dim.setBlock({ x: 11, y: 65, z: 10 }, "pw:station_seat", { "pw:index": 2 });
dim.setBlock({ x: 12, y: 65, z: 10 }, "pw:datum", {});
cmd("civ:markers", "migrate 20");
ok(at(10, 65, 10)[0] && at(10, 65, 10)[0].getProperty("pw:n") === 19 && at(11, 65, 10)[0].getProperty("pw:n") === 2 && at(12, 65, 10)[0].getProperty("pw:fam") === 3, "migrate: kitchen idx3 ring1 -> n19, seat index2 -> n2, datum");
ok(["10,65,10", "11,65,10", "12,65,10"].every((k) => { const [x, y, z] = k.split(",").map(Number); return dim.getBlock({ x, y, z }).isAir; }), "migrate: old blocks removed");
ok(_log[_log.length - 1].includes("3 marker blocks -> 3 entities"), "migrate report");
cmd("civ:markers", "migrate 20"); ok(_log[_log.length - 1].includes("0 marker blocks"), "migrate is idempotent");
// 8 list / check / remove
cmd("civ:markers", "list 40"); ok(_log.some((l) => l.includes("zone kitchen: 0 1 19")), "list groups by kind with sorted numbers");
dim.spawnEntity("minecraft:cow", { x: 2, y: 65, z: 2 });
cmd("civ:markers", "check 40"); ok(_log[_log.length - 1].includes("minecraft:cow x1") && !_log[_log.length - 1].includes("pw:marker"), "check lists non-marker entities only");
const cnt = markers().length; P.location = { x: 12.5, y: 65, z: 10.5 }; cmd("civ:markers", "remove"); ok(markers().length === cnt - 1 && !at(12, 65, 10).length, "remove = nearest within 3");
// 9 hatch lid
const shaftTop = { x: 20, y: 64, z: 20 };
dim.setBlock({ x: 20, y: 65, z: 20 }, "minecraft:oak_planks");
let lad = dim.setBlock(shaftTop, "minecraft:ladder", { facing_direction: 2 });
tap(dim.setBlock({ x: 21, y: 64, z: 20 }, "minecraft:oak_planks"), Direction.Up, M.LID_ITEM);
ok(!dim.getEntities({ type: M.LID }).length && P.bar[P.bar.length - 1].includes("TOP ladder"), "lid on a non-ladder block: refused");
tap(lad, Direction.North, M.LID_ITEM);
ok(!dim.getEntities({ type: M.LID }).length && P.bar[P.bar.length - 1].includes("must be open"), "lid under a solid block: refused");
dim.setBlock({ x: 20, y: 65, z: 20 }, "minecraft:air");
const lev = tap(lad, Direction.North, M.LID_ITEM); let lid = dim.getEntities({ type: M.LID })[0];
ok(lev.cancel === true && lid && lid.location.y === 64.8125 && lid.location.x === 20.5 && lid.location.z === 20.5, "lid spawned at the ladder cell centre, y + 0.8125");
ok(lid && lid.getProperty("pw:hinge") === 0, "ladder facing 2 (faces north) -> hinge 0 north");
ok(lid.groups.has("pw:lid_closed"), "the spawn event adds the collidable closed group");
tap(lad, Direction.North, M.LID_ITEM); ok(dim.getEntities({ type: M.LID }).length === 1 && P.bar[P.bar.length - 1].includes("already"), "one lid per ladder cell");
for (const [f, h] of [[5, 1], [3, 2], [4, 3]]) {
  const c = { x: 30 + f, y: 64, z: 30 }; const l2 = dim.setBlock(c, "minecraft:ladder", { facing_direction: f }); tap(l2, Direction.Up, M.LID_ITEM);
  const L = dim.getEntitiesAtBlockLocation(c).find((x) => x.typeId === M.LID); ok(L && L.getProperty("pw:hinge") === h, `ladder facing ${f} -> hinge ${h}`);
}
// toggle (data-driven first_valid from the BP JSON)
lid.triggerEvent("pw:toggle"); ok(lid.getProperty("pw:open") === true && lid.groups.has("pw:lid_open") && !lid.groups.has("pw:lid_closed"), "toggle #1 opens: no is_collidable");
ok(dim.sounds.includes("open.wooden_trapdoor"), "open sound");
lid.triggerEvent("pw:toggle"); ok(lid.getProperty("pw:open") === false && lid.groups.has("pw:lid_closed") && !lid.groups.has("pw:lid_open"), "toggle #2 closes: is_collidable back");
ok(dim.sounds[dim.sounds.length - 1] === "close.wooden_trapdoor", "close sound");
P.location = { x: 20.5, y: 65, z: 21.5 };
cmd("civ:hatch", "turn"); ok(lid.getProperty("pw:hinge") === 1, "civ:hatch turn +90");
cmd("civ:hatch", "flip"); ok(lid.getProperty("pw:hinge") === 3, "civ:hatch flip +180");
world.afterEvents.entityHitEntity.fire({ damagingEntity: P, hitEntity: lid }); ok(!lid.isValid, "hit removes the lid");
const lad2 = dim.setBlock({ x: 25, y: 64, z: 25 }, "minecraft:ladder", { facing_direction: 3 }); tap(lad2, Direction.Up, M.LID_ITEM);
const lid2 = dim.getEntitiesAtBlockLocation({ x: 25, y: 64, z: 25 }).find((x) => x.typeId === M.LID);
dim.setBlock({ x: 25, y: 64, z: 25 }, "minecraft:air");
world.afterEvents.playerBreakBlock.fire({ block: dim.getBlock({ x: 25, y: 64, z: 25 }), player: P, dimension: dim, brokenBlockPermutation: new S.Perm("minecraft:ladder", { facing_direction: 3 }) });
ok(lid2 && !lid2.isValid, "breaking the ladder removes its lid");
// 10 a marker loaded from disk while hidden takes the world state
cmd("civ:markers", "hide"); const late = new S.Entity(dim, M.MARKER, { x: 40.5, y: 65, z: 40.5 }); dim._entities.add(late);
late.groups.add("pw:hittable"); world.afterEvents.entityLoad.fire({ entity: late }); ok(late.getProperty("pw:vis") === false && !late.groups.has("pw:hittable"), "entityLoad applies the hidden state"); cmd("civ:markers", "show");
console.log(fails === 0 ? `MOCK OK ${passes} assertions` : `MOCK FAILS ${fails} (passed ${passes})`);
process.exit(fails ? 1 : 0);
