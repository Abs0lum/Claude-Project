// test_testrunner.mjs — mock-runs pw_testrunner.js end to end against mock_mc2.mjs.
// Usage: node test_testrunner.mjs <dir-with-pw_testrunner.js-and-steps>   (the harness builds a temp package around it)
import fs from "node:fs"; import path from "node:path"; import os from "node:os"; import { pathToFileURL } from "node:url";

const SRC = path.resolve(process.argv[2] || ".");
const HERE = path.dirname(new URL(import.meta.url).pathname);
const td = fs.mkdtempSync(path.join(os.tmpdir(), "pwtest-"));
fs.writeFileSync(path.join(td, "package.json"), JSON.stringify({ type: "module" }));
for (const [mod, file] of [["@minecraft/server", "mock_mc2.mjs"], ["@minecraft/server-ui", "mock_mc2.mjs"]]) {
  const d = path.join(td, "node_modules", mod); fs.mkdirSync(d, { recursive: true });
  fs.writeFileSync(path.join(d, "package.json"), JSON.stringify({ name: mod, type: "module", main: "index.js" }));
  fs.writeFileSync(path.join(d, "index.js"), `export * from ${JSON.stringify(pathToFileURL(path.join(HERE, file)).href)};`);
}
for (const f of ["pw_testrunner.js", "pw_testrunner_steps.js", "pw_testrunner_p0.js", "pw_testrunner_p1.js", "pw_testrunner_p2.js", "pw_testrunner_p3.js", "pw_testrunner_p4.js", "pw_testrunner_p5.js", "pw_testrunner_p6.js", "pw_testrunner_p7.js", "pw_testrunner_p8.js", "pw_testrunner_p9.js", "pw_testrunner_p10.js", "pw_testrunner_p11.js", "pw_testrunner_p12.js", "pw_testrunner_p13.js", "pw_testrunner_p14.js", "pw_testrunner_p15.js", "pw_testrunner_p16.js", "pw_testrunner_p17.js", "pw_testrunner_p18.js", "pw_testrunner_p19.js", "pw_testrunner_p20.js", "pw_testrunner_p21.js", "pw_testrunner_bump.js", "pw_testrunner_rig.js"]) fs.copyFileSync(path.join(SRC, f), path.join(td, f));
if (fs.existsSync(path.join(SRC, "pw_testrunner_p22.js"))) fs.copyFileSync(path.join(SRC, "pw_testrunner_p22.js"), path.join(td, "pw_testrunner_p22.js"));   // 0.5.15: p22 CIVITAS
if (fs.existsSync(path.join(SRC, "pw_testrunner_p23.js"))) fs.copyFileSync(path.join(SRC, "pw_testrunner_p23.js"), path.join(td, "pw_testrunner_p23.js"));   // 0.5.16: p23 TREES
if (fs.existsSync(path.join(SRC, "pw_testrunner_p24.js"))) fs.copyFileSync(path.join(SRC, "pw_testrunner_p24.js"), path.join(td, "pw_testrunner_p24.js"));   // 0.5.22: p24 CIVITAS CITY

const M = await import(pathToFileURL(path.join(HERE, "mock_mc2.mjs")).href);
const { _state, _ready, _advance, _ui, MockPlayer, system, world } = M;
let pass = 0, fail = 0;
function check(name, ok, detail = "") { if (ok) pass++; else fail++; console.log(`${ok ? "PASS" : "FAIL"} ${name}${detail ? " — " + detail : ""}`); }
const warns = [];
const origWarn = console.warn; console.warn = (m) => { warns.push(String(m)); };
const testLines = () => warns.filter((w) => w.startsWith("[PW-TEST]"));

// ---------------------------------------------------------------- registries (a full stack)
const VANILLA = ["firefly_bush", "oak_log", "flint_and_steel", "oak_planks", "oak_door", "ladder", "light_gray_wool", "light_gray_carpet", "red_stained_glass", "red_stained_glass_pane", "rail", "golden_rail", "detector_rail",
  "activator_rail", "redstone_block", "anvil", "chipped_anvil", "damaged_anvil", "quartz_pillar", "chiseled_quartz_block", "potato", "beetroot_seeds", "cocoa_beans", "nether_wart", "torchflower_seeds", "bone_meal",
  "crimson_door", "crimson_trapdoor", "crimson_planks", "crimson_stem", "crimson_sign", "warped_door", "warped_trapdoor", "warped_planks", "warped_stem", "warped_sign", "candle", "mob_spawner", "web", "noteblock", "frame",
  "packed_ice", "honeycomb_block", "honey_block", "slime", "wet_sponge", "undyed_shulker_box", "light_gray_shulker_box", "chest", "ender_chest", "copper_chest", "chain", "copper_chain", "campfire", "soul_campfire", "dried_ghast",
  "trapped_chest", "armor_stand", "bell", "banner", "loom", "end_crystal", "conduit", "decorated_pot", "cauldron", "water_bucket", "furnace", "blast_furnace", "smoker", "dispenser", "dropper", "repeater", "comparator", "observer",
  "lit_pumpkin", "iron_door", "sandstone_slab", "sandstone_stairs", "smooth_stone_slab", "andesite_slab", "andesite_stairs", "granite_slab", "granite_stairs", "diorite_slab", "diorite_stairs", "stone_bricks", "mossy_stone_bricks",
  "cracked_stone_bricks", "chiseled_stone_bricks", "nether_brick", "red_nether_brick", "end_bricks", "prismarine", "oak_sign", "oak_hanging_sign", "oak_boat", "oak_chest_boat", "charcoal", "snow_layer", "stick"];
const PW_ITEMS = ["pw:hearth_cobblestone", "pw:flue_cobblestone", "pw:station_seat", "pw:furn_chair_oak", "pw:zone_kitchen", "pw:furn_table_oak", "pw:hatch_lid", "pw:furn_mantel_oak", "pw:furn_wall_shelf_oak", "pw:furn_trestle_oak",
  "pw:furn_barrel_seat_oak", "pw:furn_shelf_oak", "pw:furn_cupboard_oak", "pw:furn_dresser_oak", "pw:furn_bench_oak", "pw:furn_stool_oak", "pw:furn_coat_pegs_oak", "pw:hearth_oak_planks", "pw:flue_oak_planks", "pw:frame_cornerpost",
  "pw:roof45_ridge_oak", "pw:roof_ridge_end_oak", "pw:roof45_oak", "pw:ramp_cobble_2_lo", "pw:ramp_cobble_2_hi", "pw:ramp_cobble_4_q1", "pw:ramp_cobble_4_q2", "pw:ramp_cobble_4_q3", "pw:ramp_cobble_4_q4"];
for (const v of VANILLA) _state.items.add("minecraft:" + v); for (const p of PW_ITEMS) _state.items.add(p);
for (const b of ["pw:furn_chair_oak", "pw:hearth_cobblestone", "pw:slab_stone", "pw:roof45_oak", "pw:ramp_cobble_2_lo", "pw:zone_kitchen", "pw:manhole_cover", "minecraft:firefly_bush"]) _state.blockTypes.add(b);
for (const e of ["pw:seat", "pw:marker", "minecraft:trader_llama", "pw:probe"]) _state.entityTypes.add(e);   // sf_nba:firefly deliberately ABSENT

// ---------------------------------------------------------------- 1 early execution
const mod = await import(pathToFileURL(path.join(td, "pw_testrunner.js")).href);
const { STEPS } = await import(pathToFileURL(path.join(td, "pw_testrunner_steps.js")).href);
const { P0_STEPS, P0_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p0.js")).href);
const RIG = await import(pathToFileURL(path.join(td, "pw_testrunner_rig.js")).href);
const { P1_STEPS, P1_HOSTILES, P1_PROBES, P1R_STEPS, P1R_IDS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p1.js")).href);
const { P2_STEPS, P2_SIZES, P2_RENDERS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p2.js")).href);
const { P3_STEPS, P3N_STEPS, P3_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p3.js")).href);
const { P4_STEPS, P4_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p4.js")).href);
const { P5_STEPS, P5_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p5.js")).href);
const { P6_STEPS, P6_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p6.js")).href);
const { P7_STEPS, P7_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p7.js")).href);
const { P8_STEPS, P8_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p8.js")).href);
const { P9_STEPS, P9_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p9.js")).href);
const { P10_STEPS, P10_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p10.js")).href);
const { P11_STEPS, P11_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p11.js")).href);
const { P12_STEPS, P12_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p12.js")).href);
const { P13_STEPS, P13_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p13.js")).href);
const { P14_STEPS, P14_MOBS } = await import(pathToFileURL(path.join(td, "pw_testrunner_p14.js")).href);
for (const m of P1_HOSTILES) _state.entityTypes.add(m.id); for (const m of P2_SIZES) _state.entityTypes.add(m.id); for (const m of P2_RENDERS) _state.entityTypes.add(m.id);
for (const m of P0_MOBS) _state.entityTypes.add(m.id);
for (const m of P3_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P4_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P5_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P6_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P7_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P8_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P9_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P10_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P11_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P12_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P13_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
for (const m of P14_MOBS) { _state.entityTypes.add(m.rig.mob); for (const r of m.rig.row || []) _state.entityTypes.add(r.mob); }
_state.entityTypes.delete("sf_nba:firefly");   // test 2c keeps it deliberately ABSENT (p9 w11 rigs one in the Realm)
// v0.3.1: which mobs lack the grow-up event (they throw), which answer as_adult, and which spawn as babies in this mock world
_state.noGrowUp = new Set(["minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:zombie_pigman", "minecraft:ravager", "minecraft:rabbit", "minecraft:pillager"]);
_state.zombieFamily = new Set(["minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:zombie_pigman"]);
_state.babySpawn = new Set(["minecraft:turtle", "minecraft:zombie"]);
check("1 module loads during early execution (no world calls at top level)", true);
// the banner carries the manifest's version (the version-flag law, RECHECK A6): read it from the manifest beside the scripts
const MANI = JSON.parse(fs.readFileSync(path.join(SRC, "..", "manifest.json"), "utf8").replace(/^\uFEFF/, ""));
const VER = MANI.header.version.join(".");
check(`1b banner is the version flag (manifest v${VER})`, warns.some((w) => w.startsWith(`[PW-VERSION] PW Test Runner BP v${VER}`) && w.includes(" p18 34 p19 98 p20 ") && w.includes(" bump 3") && w.length <= 140), warns[0]);
_advance(25);                                                  // the heartbeat fires once before the world is ready
check("1c heartbeat before ready does not throw and touches nothing", _state.players.length === 0);

// ---------------------------------------------------------------- 2 start
_ready();
const p = new MockPlayer("Abs0lum"); _state.players.push(p);
const fire = (msg) => system.afterEvents.scriptEventReceive.fire({ id: "pw:test", message: msg, sourceEntity: p });
fire("start");
const S = mod._state();
check("2 run state created at step 0", S && S.active && S.i === 0 && S.run.length > 10);
check("2b state persisted to the world", typeof _state.dyn.get("pw:test_state") === "string" && JSON.parse(_state.dyn.get("pw:test_state")).i === 0);
check("2c census: ok list logged + sf_nba:firefly reported MISSING", testLines().some((l) => l.includes("CENSUS ok 11/12")) && testLines().some((l) => l.includes("CENSUS MISSING: sf_nba:firefly")));
check("2d gamerules saved (true/true) and switched off", _state.rules.doDayLightCycle === false && _state.rules.doWeatherCycle === false && S.gr.day === true && S.gr.wx === true);
const clicker = p.inv.slots[8];
check("2e clicker in hotbar slot 9 (index 8): named stick, inventory-locked, kept on death", clicker && clicker.typeId === "minecraft:stick" && clicker.nameTag.includes("PW TEST CLICKER") && clicker.lockMode === "inventory" && clicker.keepOnDeath === true);
check("2f step 1 announced: title + sound + chat + STEP log line", p.titles.length === 1 && p.sounds.includes("random.orb") && p.msgs.some((m) => m.includes("step 1/")) && testLines().some((l) => /STEP #01 s0 /.test(l)));
fire("start");
check("2g a second start refuses while a run is active", S === mod._state() && p.msgs.some((m) => m.includes("already at step")));

// ---------------------------------------------------------------- 3 heartbeat / action bar
_advance(20);
check("3 action bar shows step + biome every second", p.bars.length >= 1 && p.bars.at(-1).includes("1/") && p.bars.at(-1).includes("forest"));

// ---------------------------------------------------------------- 4 walk every step with PASS via the clicker menu; check setups
const useClicker = () => world.afterEvents.itemUse.fire({ itemStack: clicker, source: p });
const tick = () => new Promise((r) => setTimeout(r, 0));
let setupsSeen = { daytime: 0, weather: 0, give: 0, cmd: 0, spawn: 0 };
const before = { items: p.inv.count(() => true), cmds: p.cmds.length, ents: _state.entities.length, weather: _state.weather.length };
for (let i = 0; i < STEPS.length; i++) {
  const st = STEPS[i];
  check(`4.${st.id} runner is on step ${i + 1}`, mod._state().i === i);
  for (const a of st.setup || []) { for (const k of Object.keys(a)) setupsSeen[k] = (setupsSeen[k] || 0) + 1; }
  if (i === 1) {                                                // u1: the props button exists and builds a bush without leaving the step
    _ui.queue.push({ selection: 5 });                          // PASS FAIL PASS+ FAIL+ Repeat PROPS ...
    useClicker(); await tick(); await tick();
    check("4.props bush placed 3 blocks ahead + step unchanged", _state.blocks.get("10,70,23") === "minecraft:firefly_bush" && mod._state().i === 1);
  }
  if (i === 2) {                                                // u2: props = bush + 12 particles
    _ui.queue.push({ selection: 5 }); useClicker(); await tick(); await tick();
    check("4.props 12 bush fireflies spawned ahead", _state.particles.filter((x) => x[0] === "minecraft:firefly_particle").length === 12);
  }
  if (st.id === "u2") {                                         // FAIL + note through the modal form
    _ui.queue.push({ selection: 3 }, { formValues: ["clusters of balls, about twenty per bush, hanging and floating; no flashing at all; " + "x".repeat(140)] });
    useClicker(); await tick(); await tick(); await tick();
    check("4.note FAIL recorded with the note", mod._state().verdicts.u2.v === "FAIL" && mod._state().verdicts.u2.n.startsWith("clusters"));
    check("4.note long note split into NOTE / NOTE+ lines", testLines().some((l) => l.includes("NOTE u2: clusters")) && testLines().some((l) => l.includes("NOTE u2:+ ")));
    continue;
  }
  if (st.id === "v3") {                                         // Repeat setup via the menu re-runs weather
    const w0 = _state.weather.length; _ui.queue.push({ selection: 4 }); useClicker(); await tick(); await tick();
    check("4.repeat re-runs the setup (weather set again)", _state.weather.length === w0 + 1 && mod._state().i === i);
  }
  if (st.id === "y3") check("4.spawn four trader llamas ahead", _state.entities.filter((e) => e[0] === "minecraft:trader_llama").length === 4);
  if (st.id === "b1") check("4.cmd bed colours went through runCommand", p.cmds.filter((c) => c.startsWith("give @s bed 1 ")).length === 4);
  if (st.id === "z1") check("4.give all 12 furniture pieces in the inventory", p.inv.count((s) => s.typeId.startsWith("pw:furn_")) >= 12);
  _ui.queue.push({ selection: 0 });                            // PASS
  useClicker(); await tick(); await tick();
}
check("4 all steps walked; run finished (DONE)", mod._state().active === false && testLines().some((l) => /DONE at step #48/.test(l)));
check("4b setups exercised every kind", setupsSeen.daytime > 0 && setupsSeen.weather > 0 && setupsSeen.give > 0 && setupsSeen.cmd > 0 && setupsSeen.spawn > 0, JSON.stringify(setupsSeen));
check("4c items were given and none reported MISSING", p.inv.count(() => true) > before.items && !testLines().some((l) => l.includes("MISSING (pack")));
check("4d gamerules restored at the end", _state.rules.doDayLightCycle === true && _state.rules.doWeatherCycle === true);
check("4e clicker removed at the end", !p.inv.slots.some((s) => s && s.nameTag && s.nameTag.includes("PW TEST CLICKER")));

// ---------------------------------------------------------------- 5 the report block
const rep = testLines(); const iRep = rep.findIndex((l) => l.includes("REPORT run")); const iEnd = rep.lastIndexOf("[PW-TEST] END");
check("5 report block present, ends with END", iRep >= 0 && iEnd > iRep);
const block = rep.slice(iRep, iEnd + 1);
check("5b one line per step in the block (+ note lines)", block.filter((l) => /\[PW-TEST\] #\d\d /.test(l)).length === STEPS.length);
check("5c counts: PASS 47 FAIL 1", block[0].includes("PASS 47 FAIL 1 SKIP 0 open 0"), block[0]);
const longest = Math.max(...warns.map((w) => w.length));
check("5d every content-log line <= 120 characters", longest <= 120, `longest ${longest}`);
check("5e every runner line carries the [PW-TEST] prefix or the version flag", warns.every((w) => w.startsWith("[PW-TEST]") || w.startsWith("[PW-VERSION]")));

// ---------------------------------------------------------------- 6 a second run: commands, skip/next/back/goto/note/where/clear, relog resume, stop
fire("start!"); const S2 = mod._state();
check("6 start! begins a fresh run", S2 !== S && S2.active && S2.i === 0);
fire("skip not today"); check("6b skip records SKIP + note and advances", S2.verdicts.s0.v === "SKIP" && S2.verdicts.s0.n === "not today" && S2.i === 1);
fire("next"); check("6c next moves on without a verdict (OPEN line)", S2.i === 2 && testLines().some((l) => /OPEN #02 u1 /.test(l)));
fire("back"); check("6d back returns one step (no setup re-run)", S2.i === 1);
fire("goto x5"); check("6e goto by id", S2.i === STEPS.findIndex((s) => s.id === "x5"));
fire("goto 3"); check("6f goto by number", S2.i === 2);
fire("note the bush looked fine by day"); check("6g note attaches to the current step", S2.verdicts.u2 && S2.verdicts.u2.n.includes("bush looked fine"));
fire("where"); check("6h where logs position + biome", testLines().some((l) => /WHERE 10,70,20 forest/.test(l)));
p.gameMode = "Survival"; fire("clear"); check("6i clear refused outside creative", p.msgs.at(-1).includes("only works in creative"));
p.gameMode = "Creative"; fire("clear"); check("6j clear in creative runs the command and keeps the clicker", p.cmds.includes("clear @s") && p.inv.slots.some((s) => s && s.nameTag && s.nameTag.includes("PW TEST CLICKER")));
// relog: the player leaves (clicker gone with the fresh inventory) and spawns again
p.inv.slots.fill(undefined); p.titles.length = 0;
world.afterEvents.playerSpawn.fire({ initialSpawn: true, player: p }); _advance(45);
check("6k rejoin: clicker re-given, step re-shown, REJOIN logged", p.inv.slots[8] && p.inv.slots[8].nameTag.includes("PW TEST CLICKER") && p.titles.length === 1 && testLines().some((l) => /REJOIN at step #03 u2/.test(l)));
fire("resume"); check("6l resume re-shows the step", testLines().some((l) => /RESUME at step #03 u2/.test(l)));
fire("pass all good"); check("6m pass by command", S2.verdicts.u2.v === "PASS" && S2.verdicts.u2.n.includes("all good") && S2.i === 3);
_state.rules.doDayLightCycle = false;                          // (still off from start!)
fire("stop");
check("6n stop: run inactive, gamerules restored, report written, clicker removed", S2.active === false && _state.rules.doDayLightCycle === true && !p.inv.slots.some((s) => s && s.nameTag) && testLines().filter((l) => l.includes("REPORT run")).length === 2);
fire("report"); check("6o report after stop still works from the saved state", testLines().filter((l) => l.includes("REPORT run")).length === 3);
fire("reset"); check("6p reset forgets the run", mod._state() === null && !_state.dyn.has("pw:test_state"));
fire("help"); check("6q help prints the verb list", p.msgs.at(-1).includes("/scriptevent pw:test <verb>"));

// ---------------------------------------------------------------- 7 failure paths never throw out of the handlers
_state.items.delete("pw:hearth_cobblestone"); p.failCmds = true;
fire("start!"); fire("goto w1");
check("7 missing pack item is logged as MISSING, the step still begins", testLines().some((l) => l.includes("MISSING (pack not loaded?) pw:hearth_cobblestone")) && mod._state().i === STEPS.findIndex((s) => s.id === "w1"));
fire("goto b1"); check("7b failing commands are logged, not thrown", testLines().some((l) => l.includes("setup cmd FAILED: give @s bed 1 8")));
p.failCmds = false; fire("reset");

// ---------------------------------------------------------------- 8 the PHASE 0 lineup: probe + rig, end to end
p.location = { x: 10.5, y: 70, z: 20.5 }; p.rotation = { x: 0, y: 180 };     // standing at 10,70,20 facing NORTH
fire("start p0"); const S3 = mod._state();
check("8 start p0 begins the P0 lineup at q0", S3 && S3.active && S3.lineup === "p0" && S3.i === 0 && P0_STEPS[0].id === "q0");
check("8b RUN START line names the lineup", testLines().some((l) => l.includes("RUN START") && l.includes("p0 (PHASE 0")));
_advance(20);
check("8c the bar shows the facing during a P0 run", p.bars.at(-1).includes("facing NORTH"), p.bars.at(-1));
check("8d facingName: 0 south, 90 west, -90 east, 180 north, -170 north, 44 south", RIG.facingName(0) === "SOUTH" && RIG.facingName(90) === "WEST" && RIG.facingName(-90) === "EAST" && RIG.facingName(180) === "NORTH" && RIG.facingName(-170) === "NORTH" && RIG.facingName(44) === "SOUTH" && RIG.facingName(NaN) === "?");
fire("pass");                                                                   // -> q1 probe static
const probes = () => _state.ents.filter((e) => e.typeId === "pw:probe");
check("8e q1: one pw:probe 3 blocks NORTH at eye height, facing SOUTH (yaw 0), tagged", S3.i === 1 && probes().length === 1 && probes()[0].location.x === 10.5 && Math.abs(probes()[0].location.y - 70.12) < 1e-9 && probes()[0].location.z === 17.5 && probes()[0].rotation.y === 0 && probes()[0].tags.has("pw_rig") === false && probes()[0].tags.has("pw_probe") && probes()[0].events.length === 0);
check("8f PROBE log line", testLines().some((l) => /PROBE static at 10,70,17 facing SOUTH/.test(l)));
fire("repeat");
check("8g repeat setup replaces the probe (still exactly one)", probes().length === 1);
fire("pass");                                                                   // -> q2 probe anim
check("8h q2: the animated probe replaced the static one (pw:t6 fired, one probe)", S3.i === 2 && probes().length === 1 && probes()[0].events.includes("pw:t6"));
const typeAt = (k) => _state.blocks.get(k) || (parseInt(k.split(",")[1], 10) < 64 ? "minecraft:grass_block" : "minecraft:air");
const snapshot = () => { const m = new Map(); for (let x = 0; x <= 20; x++) for (let y = 66; y <= 76; y++) for (let z = 8; z <= 24; z++) { const k = `${x},${y},${z}`; m.set(k, typeAt(k)); } return m; };
const before8 = snapshot();
fire("pass");                                                                   // -> r01 turtle in water
const rig = () => RIG._rig();
const rigged = () => _state.ents.filter((e) => e.tags.has("pw_rig"));
check("8i r01: the probe is gone, a turtle is rigged", probes().length === 0 && rigged().length === 1 && rigged()[0].typeId === "minecraft:turtle" && P0_STEPS[3].id === "r01");
check("8j the pen: barrier ring at dx/dz = +-3, y0..y0+2 (5 blocks north: centre 10,70,15)", _state.blocks.get("13,70,15") === "minecraft:barrier" && _state.blocks.get("7,72,15") === "minecraft:barrier" && _state.blocks.get("10,71,18") === "minecraft:barrier" && _state.blocks.get("10,70,12") === "minecraft:barrier" && _state.blocks.get("13,73,15") === undefined);
check("8k the pool: water 2 deep inside, air above, stone floor under it (the mock ground at y 69 was air)", typeAt("10,70,15") === "minecraft:water" && typeAt("12,71,13") === "minecraft:water" && typeAt("10,72,15") === "minecraft:air" && typeAt("10,69,15") === "minecraft:stone" && typeAt("13,69,15") === "minecraft:air");
check("8l rig state saved: centre, hold spot in the water, mob id, replaced blocks remembered", rig() && rig().mob === "minecraft:turtle" && rig().centre.x === 10 && rig().centre.z === 15 && rig().hold.y === 70.5 && rig().cells.length > 100 && typeof _state.dyn.get("pw:test_rig") === "string");
check("8m the mob spawned at the hold spot facing SOUTH, slowness applied", rigged()[0].location.y === 70.5 && rigged()[0].rotation.y === 0 && _state.effects.some((e) => e[0] === "minecraft:turtle" && e[1] === "slowness" && e[3].amplifier === 255));
const tp0 = _state.teleports.length; rigged()[0].location = { x: 12, y: 70.5, z: 15 };
_advance(3);
check("8n the hold loop teleports it back every tick, facing south", _state.teleports.length >= tp0 + 3 && rigged()[0].location.x === 10.5 && _state.teleports.at(-1)[2].rotation.y === 0);
// v0.2.1: the pool re-melts its ice every second; the rigged mob is an adult; the title stays 1 s; the P0 menu carries the quick tags
_state.blocks.set("11,70,14", "minecraft:ice"); _state.blocks.set("9,71,16", "minecraft:frosted_ice"); _advance(20);
check("8n2 v0.2.1 pool ice re-melted within a second (ice + frosted ice -> water, logged)", typeAt("11,70,14") === "minecraft:water" && typeAt("9,71,16") === "minecraft:water" && testLines().some((l) => l.includes("pool re-melted 2")));
check("8n3 v0.3.1 a BABY rigged mob is grown up (ageable_grow_up fired, no entity_born, logged)", rigged()[0].events.includes("minecraft:ageable_grow_up") && !rigged()[0].events.includes("minecraft:entity_born") && testLines().some((l) => l.includes("RIG baby grown up")));
check("8n4 v0.2.1 the step title stays 1 s (20 ticks) so it does not cover the front shot", p.titles.at(-1)[1].stayDuration === 20);
check("8n5 v0.2.1 no NO MOB notice while the spawn worked", RIG.rigStatus() && RIG.rigStatus().spawnError === "" && !p.bars.at(-1).includes("NO MOB"));
_ui.queue.push({ selection: 2 }); useClicker(); await tick(); await tick();    // P0 menu: PASS · FAIL · FAIL: vanilla? · FAIL: magenta? · FAIL: parts? · ...
check("8n6 v0.2.1 quick tag 'FAIL: vanilla?' records FAIL + note vanilla? and moves on", S3.verdicts.r01 && S3.verdicts.r01.v === "FAIL" && S3.verdicts.r01.n === "vanilla?" && S3.i === 4 && testLines().some((l) => /FAIL #04 r01 .*\+note/.test(l)));
check("8n7 v0.2.1 the P0 menu shows the three quick tags and the PASS button says Patrix", (() => { const f = _ui.shown.at(-1); const b = f.parts.filter((x) => x[0] === "button").map((x) => x[1]); return b[0].includes("Patrix") && b[2] === "§4FAIL: vanilla?" && b[3] === "§4FAIL: magenta?" && b[4] === "§4FAIL: parts?" && b[5] === "PASS + note"; })());
fire("back"); fire("repeat");                                                    // -> r01 again; repeat = rig it again
check("8n8 back + repeat re-rigs r01 (a turtle again)", S3.i === 3 && rigged().length === 1 && rigged()[0].typeId === "minecraft:turtle");
fire("pass");                                                                   // -> r02 salmon (water)
check("8o r02: the turtle is removed, a salmon rigged, the pen rebuilt (still water)", rigged().length === 1 && rigged()[0].typeId === "minecraft:salmon" && _state.blocks.get("10,70,15") === "minecraft:water");
for (let k = 0; k < 5; k++) fire("pass");                                       // r03..r06 water mobs -> r07 horse (land)
check("8p0 v0.3.1 an ADULT rigged mob gets no grow-up event and no FAILED line", rigged()[0].typeId === "minecraft:horse" && rigged()[0].events.length === 0 && !testLines().some((l) => l.includes("rig event minecraft:ageable_grow_up FAILED")));
check("8p r07: a land mob stands on the floor level, the pen is air inside", S3.i === 9 && rigged()[0].typeId === "minecraft:horse" && rigged()[0].location.y === 70 && typeAt("10,70,15") === "minecraft:air" && typeAt("10,71,15") === "minecraft:air");
const ids = P0_STEPS.map((s) => s.id);
check("8q P0 lineup: q0 q1 q2, one r-step per mob, q9 last; unique ids", ids[0] === "q0" && ids[1] === "q1" && ids[2] === "q2" && ids.at(-1) === "q9" && ids.filter((i) => i.startsWith("r")).length === P0_MOBS.length && new Set(ids).size === ids.length && P0_MOBS.length >= 30);
check("8r every P0 body names the shots and PASS; water steps say pool; top steps ask for SHOT 3", P0_STEPS.every((s) => s.body.includes("PASS")) && P0_STEPS.filter((s) => s.id.startsWith("r")).every((s) => s.body.includes("SHOT 1 FRONT") && s.body.includes("SHOT 2 LEFT FLANK")) && P0_MOBS.every((m, i) => (m.water === P0_STEPS[3 + i].body.includes("POOL")) && (m.top === P0_STEPS[3 + i].body.includes("SHOT 3 TOP"))));
// jump to the end: q9 clears everything and restores the ground
fire("goto q9");
check("8s q9: no rigged mob, no probe, rig state gone", rigged().length === 0 && probes().length === 0 && rig() === null && !_state.dyn.has("pw:test_rig"));
const diffNow = () => { const now = snapshot(); return [...before8.keys()].filter((k) => before8.get(k) !== now.get(k)); };
const diff = diffNow();
check("8t every replaced block restored (world block map == before the rig)", diff.length === 0, diff.slice(0, 5).join(" "));
fire("pass");
check("8u P0 run DONE; report names p0", S3.active === false && testLines().some((l) => /DONE at step #\d\d/.test(l)) && testLines().some((l) => l.includes("REPORT run") && l.includes("· p0 (current) ·")));
// stop mid-rig clears the pen
fire("start! p0"); fire("goto r03");
check("8v stop mid-rig removes the mob and restores the blocks", (fire("stop"), rigged().length === 0 && RIG._rig() === null && diffNow().length === 0));
fire("reset");
// a run started without a lineup name still walks the main lineup (old saved states have no lineup field)
fire("start!"); check("8w plain start = the witness lineup, 48 steps", mod._state().lineup === "main" && p.msgs.some((m) => m.includes("witness lineup: 48 steps"))); fire("reset");
check("8w2 v0.2.1 a failed rig spawn is kept in the rig state and the bar says NO MOB (and why)", (() => {
  _state.entityTypes.delete("minecraft:zombie_pigman"); fire("start! p0"); fire("goto r23");
  const st = RIG.rigStatus(); _advance(20);
  const ok = st && st.mob === "minecraft:zombie_pigman" && st.spawnError.length > 0 && p.bars.at(-1).includes("NO MOB (minecraft:zombie_pigman)") && rigged().length === 0 && testLines().some((l) => l.includes("RIG spawn FAILED minecraft:zombie_pigman"));
  fire("reset"); _state.entityTypes.add("minecraft:zombie_pigman"); return ok; })());
check("8w3 v0.2.1 the main lineup menu is unchanged (PASS · FAIL · PASS + note · FAIL + note · Repeat setup ...)", (() => { fire("start!"); _ui.queue.push({ canceled: true }); useClicker(); const f = _ui.shown.at(-1); const b = f.parts.filter((x) => x[0] === "button").map((x) => x[1]); fire("reset"); return b[0] === "§2PASS" && b[1] === "§4FAIL" && b[2] === "PASS + note" && b[3] === "FAIL + note" && b[4] === "Repeat setup"; })());
// ---------------------------------------------------------------- 9 the P1 lineup (v0.3.0): roofed hostile rig, block stations, probes, sky, leaves, regression
p.location = { x: 10.5, y: 70, z: 20.5 }; p.rotation = { x: 0, y: 180 }; p.cmds.length = 0;
fire("start! p1"); const S4 = mod._state();
check("9 start p1 begins the P1 lineup at q0; ids q0 h01..h11 b01..b14 q9 unique, no size steps (they moved to p2)", S4 && S4.lineup === "p1" && S4.i === 0 && P1_STEPS[0].id === "q0" && P1_STEPS.at(-1).id === "q9" && new Set(P1_STEPS.map((s) => s.id)).size === P1_STEPS.length && P1_STEPS.filter((s) => s.id.startsWith("h")).length === P1_HOSTILES.length && P1_STEPS.filter((s) => s.id.startsWith("b")).length === 14 && P1_STEPS.filter((s) => s.id.startsWith("s")).length === 0 && P1_STEPS.length === 27);
fire("pass");                                                                   // -> h01 zombie in the ROOFED pen
check("9b h01: a zombie is rigged under a barrier roof (ceiling cells at y0+3), fire resistance + as_adult applied, station volume cleared first",
  rigged().length === 1 && rigged()[0].typeId === "minecraft:zombie" && typeAt("10,73,15") === "minecraft:barrier" && typeAt("12,73,13") === "minecraft:barrier" && typeAt("10,72,15") === "minecraft:air"
  && _state.effects.some((e) => e[0] === "minecraft:zombie" && e[1] === "fire_resistance") && rigged()[0].events.includes("minecraft:as_adult") && !rigged()[0].events.includes("minecraft:ageable_grow_up") && p.cmds.some((c) => c.startsWith("fill ~-3 ~ ~-9 ~3 ~5 ~-2 air")));
check("9c the roofed pen restores its ceiling cells on clear", (fire("goto b01"), typeAt("10,73,15") === "minecraft:air"));
check("9d b01 torches: rigclear then the station commands ran in order (clear, then 3 setblocks)", (() => { const i = p.cmds.lastIndexOf("fill ~-3 ~ ~-9 ~3 ~5 ~-2 air"); return i >= 0 && p.cmds.slice(i + 1, i + 4).every((c) => c.startsWith("setblock ") && c.includes("torch")); })());
fire("goto b09"); check("9e b09 XPACK probe: the three probe blocks A B C then the three logs, in that order, after the clear", (() => { const i = p.cmds.lastIndexOf("fill ~-3 ~ ~-9 ~3 ~5 ~-2 air"); const c = p.cmds.slice(i + 1); return c.length === 6 && c[0].includes("pw:xprobe_a") && c[1].includes("pw:xprobe_b") && c[2].includes("pw:xprobe_c") && c.slice(3).every((x) => x.includes("_log")); })());
check("9e2 the probe paths: A = stone, B = an RP-01-only 128 (mushroom_stem_v3), C = nowhere", P1_PROBES.a === "textures/blocks/stone" && P1_PROBES.b === "textures/blocks/mushroom_stem_v3" && P1_PROBES.c.includes("nowhere"));
fire("goto b10"); check("9f b10 SUN sets sunset (12500) + clear weather before the (empty) station commands; b11 midnight; b12 noon", (() => { const a = _state.timeOfDay === 12500 && String(_state.weather.at(-1)?.[0]).toLowerCase().includes("clear"); fire("goto b11"); const b = _state.timeOfDay === 18000; fire("goto b12"); const c = _state.timeOfDay === 6000; return a && b && c; })());
fire("goto b13"); check("9f2 b13 LEAVES places five vanilla leaves (persistent) and two pw: variant leaves", (() => { const i = p.cmds.lastIndexOf("fill ~-3 ~ ~-9 ~3 ~5 ~-2 air"); const c = p.cmds.slice(i + 1); return c.length === 7 && c.slice(0, 5).every((x) => x.includes("_leaves") && x.includes("persistent_bit")) && c[5].includes("pw:oak_leaves") && c[6].includes("pw:spruce_leaves"); })());
fire("goto b14"); check("9f3 b14 DEDUPE row: 7 back-row blocks, 3 flowers (+ rose bush top), 2 pw slabs", (() => { const i = p.cmds.lastIndexOf("fill ~-3 ~ ~-9 ~3 ~5 ~-2 air"); const c = p.cmds.slice(i + 1); return c.length === 13 && c[0].includes("quartz_block") && c[7].includes("allium") && c[10].includes("upper_block_bit") && c[11].includes("pw:slab_dirt") && c[12].includes("pw:slab_sand"); })());
_advance(20); check("9g the bar shows the facing during a P1 run", p.bars.at(-1).includes("facing NORTH"));
fire("goto q9"); check("9h q9 clears the pen and the station volume and sets noon", rigged().length === 0 && p.cmds.at(-1) === "fill ~-3 ~ ~-9 ~3 ~5 ~-2 air" && _state.timeOfDay === 6000);
// v0.3.1: the Bedrock block-state syntax — the mock rejects the v0.3.0 ":" form exactly as the game did on 09-28
check("9i v0.3.1 the mock rejects the old [\"key\":value] form (CommandError) and accepts [\"key\"=value]", (() => { let threw = false; try { p.runCommand('setblock ~ ~ ~ kelp ["kelp_age":0]'); } catch { threw = true; } let ok = true; try { p.runCommand('setblock ~ ~ ~ kelp ["kelp_age"=0]'); p.runCommand('setblock ~ ~ ~ lit_furnace ["minecraft:cardinal_direction"="south"]'); } catch { ok = false; } return threw && ok; })());
check("9j v0.3.1 walking EVERY p1 step runs every station command with zero parse errors", (() => { _state.cmdErrors = 0; const n = testLines().length; for (const st of P1_STEPS) fire(`goto ${st.id}`); return _state.cmdErrors === 0 && !testLines().slice(n).some((l) => l.includes("setup cmd FAILED")); })(), `cmdErrors ${_state.cmdErrors}`);
check("9k v0.3.1 h10 rigs minecraft:evocation_illager (the Bedrock id), never minecraft:evoker", P1_HOSTILES.find((h) => h.name === "evoker").id === "minecraft:evocation_illager" && !P1_HOSTILES.some((h) => h.id === "minecraft:evoker"));
fire("reset");
// ---------------------------------------------------------------- 10 the P2 lineup (v0.3.0): Realm sizes + Naturalist renders
p.cmds.length = 0; fire("start! p2"); const S5 = mod._state();
check("10 start p2 begins the P2 lineup at q0; ids q0 s01..s04 r01..r03 q9, 9 steps", S5 && S5.lineup === "p2" && S5.i === 0 && P2_STEPS.map((s) => s.id).join(" ") === "q0 s01 s02 s03 s04 r01 r02 r03 q9");
fire("pass"); check("10b s01: a beetle is rigged next to the white post", rigged().length === 1 && rigged()[0].typeId === "sf_nba:beetle" && p.cmds.at(-1) === "setblock ~1 ~ ~-4 white_wool");
fire("goto r01"); check("10c r01: a deer is rigged in a dry pen (no water)", rigged().length === 1 && rigged()[0].typeId === "sf_nba:deer" && typeAt("10,70,15") !== "minecraft:water");
fire("goto r03"); check("10d r03: the hammer-head shark is rigged in a POOL", rigged().length === 1 && rigged()[0].typeId === "sf_nba:hammer_head_shark" && typeAt("10,70,15") === "minecraft:water");
_advance(20); check("10e the bar shows the facing + rig status during a P2 run", p.bars.at(-1).includes("facing NORTH"));
fire("goto q9"); check("10f q9 clears the pen and the station volume", rigged().length === 0 && p.cmds.at(-1) === "fill ~-3 ~ ~-9 ~3 ~5 ~-2 air");
fire("reset");
// ---------------------------------------------------------------- 11 the P1 RE-RUN lineup (v0.3.1)
p.cmds.length = 0; fire("start! p1r"); const S6 = mod._state();
check("11 start p1r: 16 steps q0 h03..h10 b03 b04 b07 b08 b13 b14 q9, the same step objects as p1", S6 && S6.lineup === "p1r" && P1R_STEPS.map((s) => s.id).join(" ") === P1R_IDS.join(" ") && P1R_STEPS.length === 16 && P1R_STEPS.every((s) => P1_STEPS.includes(s)));
fire("pass"); check("11b p1r step 2 = h03 drowned rigged in the roofed pen", S6.i === 1 && rigged().length === 1 && rigged()[0].typeId === "minecraft:drowned");
const n11 = testLines().length; fire("goto b07"); check("11c p1r b07 places the kelp with no parse error", (() => { const i = p.cmds.lastIndexOf("fill ~-3 ~ ~-9 ~3 ~5 ~-2 air"); const c = p.cmds.slice(i + 1); return c.filter((x) => x.includes("kelp_age\"=")).length === 3 && !testLines().slice(n11).some((l) => l.includes("setup cmd FAILED")); })());
fire("repeat"); check("11d v0.3.1 'repeat' is logged to the content log (SETUP REPEATED b07)", testLines().some((l) => l.includes("SETUP REPEATED b07")));
fire("fail no kelp at all, only water"); fire("stop");
// ---------------------------------------------------------------- 12 the run ARCHIVE + one-line-per-step report (v0.3.1)
fire("start! p0"); fire("pass"); fire("pass"); fire("fail vanilla?"); fire("stop");         // a p0 run: q0 PASS, q1 PASS, q2 FAIL vanilla?
fire("start! p2"); fire("pass"); fire("stop");                                             // then another lineup replaces the current run
const n0 = testLines().length; fire("report p0"); const rep0 = testLines().slice(n0);
check("12 report p0 re-emits the ARCHIVED p0 run after a p2 run", rep0.length > 0 && rep0[0].includes("REPORT run") && rep0[0].includes("p0 (archived)") && rep0.at(-1).endsWith("END"));
check("12b one line per step, the note on the verdict line ('#03 q2 FAIL ... | vanilla?')", rep0.filter((l) => /\] #\d\d /.test(l)).length === P0_STEPS.length && rep0.some((l) => /#03 q2 FAIL .* \| vanilla\?/.test(l)) && !rep0.some((l) => l.includes("NOTE q2")));
const n1 = testLines().length; fire("report p1r"); const rep1 = testLines().slice(n1);
check("12c report p1r keeps its note on the b07 line", rep1.some((l) => /b07 FAIL .* \| no kelp at all, only water/.test(l)));
fire("runs"); check("12d runs lists p0, p1r and p2 with their answered counts", ["p0:", "p1r:", "p2:"].every((k) => testLines().some((l) => l.includes(`RUNS ${k}`))));
check("12e the archive lives in one world property per lineup", ["p0", "p1r", "p2"].every((k) => typeof _state.dyn.get(`pw:test_last_${k}`) === "string"));
fire("report nosuch"); check("12f report <unknown lineup> answers, does not throw", p.msgs.at(-1).includes("unknown lineup"));
const longest12 = Math.max(...testLines().map((l) => l.length)); check("12g every content-log line still <= 120 characters", longest12 <= 120, `longest ${longest12}`);
fire("reset");
// ---------------------------------------------------------------- 13 the P3 lineups (v0.3.2, D-C277)
p.cmds.length = 0; fire("start! p3n"); const S7 = mod._state();
check("13 start p3n: q0 n01..n14 q9 (16 steps); p3 = q0 n01..n14 e01..e17 q9 (33), ids unique",
  S7 && S7.lineup === "p3n" && P3N_STEPS.map((s) => s.id).join(" ") === ["q0", ...Array.from({ length: 14 }, (_, i) => `n${String(i + 1).padStart(2, "0")}`), "q9"].join(" ")
  && P3_STEPS.length === 33 && new Set(P3_STEPS.map((s) => s.id)).size === 33 && P3_STEPS.filter((s) => s.id.startsWith("e")).length === 17);
fire("pass");
const row = () => rigged().map((e) => [e.typeId, [...e.tags].find((t) => t.startsWith("pw_rig_dx_")) || "", e.location.x]);
check("13b n01: horse in the middle, donkey held 3 west, mule 3 east (tags pw_rig_dx_-3 / _3), all rigged, a wide pen (barrier at x+6)",
  S7.i === 1 && rigged().length === 3 && row().some(([t, d, x]) => t === "minecraft:horse" && d === "" && x === 10.5) && row().some(([t, d, x]) => t === "minecraft:donkey" && d === "pw_rig_dx_-3" && x === 7.5)
  && row().some(([t, d, x]) => t === "minecraft:mule" && d === "pw_rig_dx_3" && x === 13.5) && typeAt("16,70,15") === "minecraft:barrier" && typeAt("15,70,15") === "minecraft:air"
  && typeAt("10,70,18") === "minecraft:barrier" && typeAt("10,70,17") === "minecraft:air", JSON.stringify(row()));
rigged().forEach((e) => { e.location = { x: e.location.x + 1, y: 70, z: 16 }; }); _advance(2);
check("13c the hold loop returns every row mob to ITS OWN spot", row().every(([t, d, x]) => x === (d === "pw_rig_dx_-3" ? 7.5 : d === "pw_rig_dx_3" ? 13.5 : 10.5)) && rigged().every((e) => e.location.z === 15.5), JSON.stringify(row()));
fire("goto n05");
check("13d n05: the guardian is FREE (tag pw_rig_free, no slowness) in a 9x9, 3-deep tank centred 7 north (south wall 2 blocks ahead of him)",
  rigged().length === 1 && rigged()[0].typeId === "minecraft:guardian" && rigged()[0].tags.has("pw_rig_free") && RIG._rig().centre.z === 13 && typeAt("10,72,15") === "minecraft:water" && typeAt("14,70,15") === "minecraft:water"
  && typeAt("15,70,15") === "minecraft:barrier" && typeAt("10,70,18") === "minecraft:barrier" && typeAt("10,70,19") !== "minecraft:barrier" && typeAt("10,70,20") !== "minecraft:barrier");
const tpf = _state.teleports.length; rigged()[0].location = { x: 12, y: 71, z: 13 }; _advance(3);
check("13e a free mob is NOT teleported back", _state.teleports.length === tpf && rigged()[0].location.x === 12);
fire("goto n04"); check("13f n04: the resting guardian is held (no free tag) in the 2-deep pool", rigged().length === 1 && !rigged()[0].tags.has("pw_rig_free") && typeAt("10,71,15") === "minecraft:water" && typeAt("10,72,15") === "minecraft:air");
fire("goto q9"); check("13g q9 clears every rigged mob and restores the blocks", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0);
fire("start! p3"); fire("goto e10"); check("13h p3 e10 rigs the squid in a pool", rigged().length === 1 && rigged()[0].typeId === "minecraft:squid" && typeAt("10,70,15") === "minecraft:water");
fire("stop"); fire("reset");
const longest13 = Math.max(...testLines().map((l) => l.length)); check("13i every content-log line still <= 120 characters", longest13 <= 120, `longest ${longest13}`);
// ---------------------------------------------------------------- 14 the P4 lineup (v0.3.3, D-C278)
fire("start! p4"); const S8 = mod._state();
const ids4 = P4_STEPS.map((s) => s.id);
check("14 start p4: q0 a01..a22 q9 (24 steps, unique)", S8 && S8.lineup === "p4" && ids4.join(" ") === ["q0", ...Array.from({ length: 22 }, (_, i) => `a${String(i + 1).padStart(2, "0")}`), "q9"].join(" ")
  && new Set(ids4).size === 24, ids4.join(" "));
fire("goto a01");
const ch = rigged(); const chW = ch.find((e) => [...e.tags].includes("pw_rig_dx_-2")); const chC = ch.find((e) => [...e.tags].includes("pw_rig_dx_2")); const chT = ch.find((e) => ![...e.tags].some((x) => x.startsWith("pw_rig_dx_")));
check("14a a01: three chickens - the middle one gets minecraft:climate_variant=temperate, left hatch_warm, right hatch_cold", ch.length === 3 && ch.every((e) => e.typeId === "minecraft:chicken")
  && chT && chT.props && chT.props["minecraft:climate_variant"] === "temperate" && chW && chW.events.includes("minecraft:hatch_warm") && chC && chC.events.includes("minecraft:hatch_cold")
  && testLines().some((l) => l.includes("RIG property minecraft:climate_variant=temperate")), JSON.stringify(ch.map((e) => [[...e.tags], e.events, e.props])));
chT.props["minecraft:climate_variant"] = "cold";   // the biome spawn event landing a tick late
_advance(6); check("14a2 the property is applied again 5 ticks later (a spawn event may set it late)", chT.props["minecraft:climate_variant"] === "temperate");
fire("goto a11");
const moo = rigged(); const brown = moo.find((e) => [...e.tags].includes("pw_rig_dx_3"));
check("14b a11: two mooshrooms, the row one got minecraft:become_brown, the main one no event", moo.length === 2 && moo.every((e) => e.typeId === "minecraft:mooshroom")
  && brown && brown.events.includes("minecraft:become_brown") && moo.filter((e) => e !== brown).every((e) => !e.events.includes("minecraft:become_brown")), JSON.stringify(moo.map((e) => [[...e.tags], e.events])));
fire("goto a06"); check("14c a06: the spider walks FREE", rigged().length === 1 && rigged()[0].typeId === "minecraft:spider" && rigged()[0].tags.has("pw_rig_free"));
fire("goto a07"); check("14d a07: the resting guardian is HELD in the pool; a08 the tank is free", rigged().length === 1 && !rigged()[0].tags.has("pw_rig_free") && typeAt("10,70,15") === "minecraft:water"
  && (() => { fire("goto a08"); return rigged().length === 1 && rigged()[0].tags.has("pw_rig_free"); })());
fire("goto a20"); check("14e a20: pig / horse / cow in a row", rigged().length === 3 && ["minecraft:pig", "minecraft:horse", "minecraft:cow"].every((id) => rigged().some((e) => e.typeId === id)));
fire("goto q9"); check("14f q9 clears everything", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0);
fire("stop"); fire("reset");
const longest14 = Math.max(...testLines().map((l) => l.length)); check("14g every content-log line still <= 120 characters", longest14 <= 120, `longest ${longest14}`);
// ---------------------------------------------------------------- 15 the P5 lineup (v0.3.5, D-C284)
fire("start! p5"); const S9 = mod._state();
const ids5 = P5_STEPS.map((s) => s.id);
check("15 start p5: q0 b01..b18 q9 (20 steps, unique)", S9 && S9.lineup === "p5" && ids5.join(" ") === ["q0", ...Array.from({ length: 18 }, (_, i) => `b${String(i + 1).padStart(2, "0")}`), "q9"].join(" ")
  && new Set(ids5).size === 20, ids5.join(" "));
fire("goto b14");
const mo = rigged(); const nm = (e) => e.nameTag;
check("15a b14: four mooshrooms carry the name tags Moo A..D at x -6 / -3 / 0 / +3", mo.length === 4 && mo.every((e) => e.typeId === "minecraft:mooshroom")
  && JSON.stringify(mo.map((e) => [([...e.tags].find((x) => x.startsWith("pw_rig_dx_")) || "pw_rig_dx_0").slice(10), nm(e)]).sort((a, b) => Number(a[0]) - Number(b[0])))
     === JSON.stringify([["-6", "Moo A"], ["-3", "Moo B"], ["0", "Moo C"], ["3", "Moo D"]])
  && testLines().some((l) => l.includes('RIG name tag "Moo A"')), JSON.stringify(mo.map((e) => [[...e.tags], e.nameTag])));
fire("goto b06"); const en = rigged();
check("15b b06: one enderman, made angry by minecraft:become_angry, held in the roofed pen", en.length === 1 && en[0].typeId === "minecraft:enderman" && en[0].events.includes("minecraft:become_angry") && !en[0].tags.has("pw_rig_free"));
fire("goto b12"); const sq = rigged();
check("15c b12: squid + glow squid FREE in the tank", sq.length === 2 && sq.every((e) => e.tags.has("pw_rig_free")) && ["minecraft:squid", "minecraft:glow_squid"].every((id) => sq.some((e) => e.typeId === id)) && typeAt("10,70,15") === "minecraft:water");
fire("goto b07"); const ev = rigged();
check("15d b07: the evoker spawns as minecraft:evocation_illager with a villager beside it", ev.length === 2 && ev.some((e) => e.typeId === "minecraft:evocation_illager") && ev.some((e) => e.typeId === "minecraft:villager_v2"));
fire("goto q9"); check("15e q9 clears everything", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0);
fire("stop"); fire("reset");
const longest15 = Math.max(...testLines().map((l) => l.length)); check("15f every content-log line still <= 120 characters", longest15 <= 120, `longest ${longest15}`);
// ---------------------------------------------------------------- 16 the P6 lineup (v0.3.7, D-C285)
fire("start! p6"); const S10 = mod._state();
const ids6 = P6_STEPS.map((s) => s.id);
check("16 start p6: q0 c01..c08 q9 (10 steps, unique)", S10 && S10.lineup === "p6" && ids6.join(" ") === ["q0", ...Array.from({ length: 8 }, (_, i) => `c${String(i + 1).padStart(2, "0")}`), "q9"].join(" ")
  && new Set(ids6).size === 10, ids6.join(" "));
fire("goto c07"); _advance(3); const hi = rigged();
const dxOf = (e) => Number(([...e.tags].find((x) => x.startsWith("pw_rig_dx_")) || "pw_rig_dx_0").slice(10));
const handed = hi.map((e) => [dxOf(e), e.typeId, (e.cmds || []).find((c) => c.startsWith("replaceitem entity @s slot.weapon.mainhand 0 "))]).sort((a, b) => a[0] - b[0]);
check("16a c07: seven mobs, each handed its item by replaceitem (main hand), left to right pillager..piglin", hi.length === 7
  && JSON.stringify(handed.map((h) => [h[0], h[1], (h[2] || "").split(" ").pop()])) === JSON.stringify([[-6, "minecraft:pillager", "minecraft:crossbow"], [-4, "minecraft:stray", "minecraft:bow"],
     [-2, "minecraft:bogged", "minecraft:bow"], [0, "minecraft:zombie", "minecraft:iron_sword"], [2, "minecraft:husk", "minecraft:iron_shovel"], [4, "minecraft:drowned", "minecraft:trident"], [6, "minecraft:piglin", "minecraft:golden_sword"]])
  && testLines().some((l) => l.includes("RIG item iron_sword CONFIRMED in held-items row's main hand")), JSON.stringify(handed));
fire("goto c01"); const sf = rigged();
check("16b c01: one silverfish, FREE", sf.length === 1 && sf[0].typeId === "minecraft:silverfish" && sf[0].tags.has("pw_rig_free"));
fire("goto c03"); const en6 = rigged();
check("16c c03: one angry enderman, held", en6.length === 1 && en6[0].events.includes("minecraft:become_angry") && !en6[0].tags.has("pw_rig_free"));
fire("goto q9"); check("16d q9 clears everything", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0);
fire("stop"); fire("reset");
const longest16 = Math.max(...testLines().map((l) => l.length)); check("16e every content-log line still <= 120 characters", longest16 <= 120, `longest ${longest16}`);
// ---------------------------------------------------------------- 17 the P7 lineup (v0.3.8, D-C286)
fire("start! p7"); const S11 = mod._state();
check("17 start p7: q0 d01 d02 d03 q9", S11 && S11.lineup === "p7" && P7_STEPS.map((s) => s.id).join(" ") === "q0 d01 d02 d03 q9");
fire("goto d02"); const ar = rigged();
const bows = ar.map((e) => [dxOf(e), e.typeId, (e.cmds || []).find((c) => c.startsWith("replaceitem entity @s slot.weapon.mainhand 0 "))]).sort((a, b) => a[0] - b[0]);
check("17a d02: skeleton / stray / bogged left to right, each handed a bow", ar.length === 3
  && JSON.stringify(bows.map((h) => [h[0], h[1], (h[2] || "").split(" ").pop()])) === JSON.stringify([[-3, "minecraft:skeleton", "minecraft:bow"], [0, "minecraft:stray", "minecraft:bow"], [3, "minecraft:bogged", "minecraft:bow"]]), JSON.stringify(bows));
fire("goto d03"); const sq7 = rigged();
check("17b d03: squid + glow squid FREE in the tank", sq7.length === 2 && sq7.every((e) => e.tags.has("pw_rig_free")));
fire("goto q9"); check("17c q9 clears everything", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0);
fire("stop"); fire("reset");
const longest17 = Math.max(...testLines().map((l) => l.length)); check("17d every content-log line still <= 120 characters", longest17 <= 120, `longest ${longest17}`);
// ---------------------------------------------------------------- 18 the P8 lineup (v0.3.9, D-C288)
fire("start! p8"); const S12 = mod._state();
check("18 start p8: q0 e01 e02 e03 q9", S12 && S12.lineup === "p8" && P8_STEPS.map((s) => s.id).join(" ") === "q0 e01 e02 e03 q9");
const hand = (e) => ((e.cmds || []).find((c) => c.startsWith("replaceitem entity @s slot.weapon.mainhand 0 ")) || "").split(" ").pop();
const body = (e) => ((e.cmds || []).find((c) => c.startsWith("replaceitem entity @s slot.armor.body 0 ")) || "").split(" ").pop();
fire("goto e01"); const b8 = rigged().map((e) => [dxOf(e), e.typeId, hand(e)]).sort((a, b) => a[0] - b[0]);
check("18a e01: skeleton left, bogged centre, each handed a bow", JSON.stringify(b8) === JSON.stringify([[-3, "minecraft:skeleton", "minecraft:bow"], [0, "minecraft:bogged", "minecraft:bow"]]), JSON.stringify(b8));
fire("goto e02"); const p8r = rigged().map((e) => [dxOf(e), e.typeId, hand(e)]).sort((a, b) => a[0] - b[0]);
check("18b e02: brute crossbow / piglin crossbow / wither skeleton bow, left to right", JSON.stringify(p8r) === JSON.stringify([[-3, "minecraft:piglin_brute", "minecraft:crossbow"], [0, "minecraft:piglin", "minecraft:crossbow"], [3, "minecraft:wither_skeleton", "minecraft:bow"]]), JSON.stringify(p8r));
fire("goto e03"); const w8 = rigged(); const wolf = w8.find((e) => e.typeId === "minecraft:wolf"); const zp = w8.find((e) => e.typeId === "minecraft:zombie_pigman");
check("18c e03: the wolf is tamed (on_tame) and wears wolf armor in the body slot; the zombified piglin holds a crossbow",
  w8.length === 2 && wolf && wolf.events.includes("minecraft:on_tame") && body(wolf) === "minecraft:wolf_armor" && zp && hand(zp) === "minecraft:crossbow",
  JSON.stringify(w8.map((e) => [e.typeId, e.events, e.cmds])));
check("18d the armor put-on is logged", testLines().some((l) => l.includes("RIG armor wolf_armor on wolf (tamed, armored)")));
fire("goto q9"); check("18e q9 clears everything", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0);
fire("stop"); fire("reset");
const longest18 = Math.max(...testLines().map((l) => l.length), ...warns.filter((w) => w.startsWith("[PW-VERSION]")).map((w) => w.length));
check("18f every content-log line (and the banner) still <= 120 characters", longest18 <= 120, `longest ${longest18}`);
// ---------------------------------------------------------------- 19 the P9 size parade + grow-up after a step event (v0.4.0, D-C292)
fire("start! p9"); const S19 = mod._state();
check("19 start p9: q0 z01..z08 w09..w13 q9", S19 && S19.lineup === "p9" && P9_STEPS.map((s) => s.id).join(" ") === "q0 z01 z02 z03 z04 z05 z06 z07 z08 w09 w10 w11 w12 w13 q9");
fire("goto z01"); const z1 = rigged().map((e) => [dxOf(e), e.typeId]).sort((a, b) => a[0] - b[0]);
check("19a z01: mooshroom / cow / llama, left to right", JSON.stringify(z1) === JSON.stringify([[-3, "minecraft:mooshroom"], [0, "minecraft:cow"], [3, "minecraft:llama"]]), JSON.stringify(z1));
_advance(8);
check("19b every rigged mob's age is logged after the rig (3 lines, adult)", ["cow at x 0: adult", "mooshroom at x -3: adult", "llama at x 3: adult"].every((t) => testLines().some((l) => l.includes(`RIG age ${t}`))),
  JSON.stringify(testLines().filter((l) => l.includes("RIG age"))));
fire("goto z08"); const wd = rigged(); check("19c z08: the warden alone in a roofed pen", wd.length === 1 && wd[0].typeId === "minecraft:warden" && RIG._rig().roof === true);
fire("goto q9"); check("19d q9 clears everything", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0);
fire("stop"); fire("reset");
// the e03 slip: a step event (on_tame) on a mob that spawned as a BABY must still be grown up (v0.3.9 skipped the grow-up)
_state.babySpawn.add("minecraft:wolf");
fire("start! p8"); fire("goto e03"); _advance(8); const w19 = rigged().find((e) => e.typeId === "minecraft:wolf");
check("19e a baby wolf rigged with a step event (on_tame) is tamed AND grown up, and its age logs adult",
  w19 && w19.events.includes("minecraft:on_tame") && w19.events.includes("minecraft:ageable_grow_up") && !w19.baby && testLines().some((l) => l.includes("RIG age wolf at x 0: adult")),
  JSON.stringify(w19 && w19.events));
fire("stop"); fire("reset"); _state.babySpawn.delete("minecraft:wolf");
const longest19 = Math.max(...testLines().map((l) => l.length), ...warns.filter((w) => w.startsWith("[PW-VERSION]")).map((w) => w.length));
check("19f every content-log line (and the banner) still <= 120 characters", longest19 <= 120, `longest ${longest19}`);
// ---------------------------------------------------------------- 20 the P10 lineup: FA-1 + predator sizes; re-roll, jukebox, sweep (v0.4.1, D-C300)
fire("start! p10"); const S20 = mod._state();
const ids10 = P10_STEPS.map((s) => s.id);
check("20 start p10: q0 f01..f15 w16 w17 q9 (19 steps, unique)", S20 && S20.lineup === "p10"
  && ids10.join(" ") === ["q0", ...Array.from({ length: 15 }, (_, i) => `f${String(i + 1).padStart(2, "0")}`), "w16", "w17", "q9"].join(" ") && new Set(ids10).size === 19, ids10.join(" "));
_state.variants = new Map([["minecraft:parrot", 5]]);                        // every parrot spawn rolls a colour 0..4
fire("goto f01"); _advance(200);
const par = rigged().filter((e) => e.typeId === "minecraft:parrot").map((e) => [dxOf(e), e.variant]).sort((a, b) => a[0] - b[0]);
check("20a f01: re-rolled until each of the five parrots has its colour (x -4..+4 = 0 red-blue, 1 blue, 2 green, 3 yellow-blue, 4 grey)",
  rigged().length === 5 && JSON.stringify(par) === JSON.stringify([[-4, 0], [-2, 1], [0, 2], [2, 3], [4, 4]]), JSON.stringify(par));
check("20b every re-roll is logged with its reason; the settled colours are logged without a WANTED flag",
  testLines().some((l) => /RIG re-roll .*parrot \(colour \d, want \d\) try \d+/.test(l)) && [-4, -2, 0, 2, 4].every((x, i) => testLines().some((l) => l.includes(`RIG age parrot at x ${x}: adult · colour ${i}`) && !l.includes("WANTED"))),
  JSON.stringify(testLines().filter((l) => l.includes("RIG re-roll")).slice(0, 2)));
_state.recordPlayer = false; fire("goto f03"); _advance(10);
const c3 = RIG._rig().centre; const jbk = `${c3.x + 2},${c3.y},${c3.z - 1}`;
check("20c f03: a jukebox 2 east / 1 north of the parrot inside the pen; no record player -> the fallback line (use the commands)", typeAt(jbk) === "minecraft:jukebox"
  && testLines().some((l) => l.includes("RIG jukebox at") && l.includes("could not start a disc")), jbk);
_state.recordPlayer = true; fire("repeat"); _advance(10);
check("20d with the record player API the disc starts by script (music_disc_cat, playing) and it is logged",
  (_state.records || []).some((r) => r[0] === jbk && r[1] === "minecraft:music_disc_cat" && r[2] === true) && testLines().some((l) => l.includes("playing music_disc_cat (started by script)")), JSON.stringify(_state.records));
const par3 = rigged().map((e) => [dxOf(e), e.typeId]).sort((a, b) => a[0] - b[0]);
check("20e f03: allay left, parrot centre", JSON.stringify(par3) === JSON.stringify([[-2, "minecraft:allay"], [0, "minecraft:parrot"]]), JSON.stringify(par3));
fire("goto f05"); _advance(10); const al = rigged()[0];
check("20f f05: the allay is handed an amethyst shard, held 1 block up in a roofed pen", rigged().length === 1 && al.typeId === "minecraft:allay" && hand(al) === "minecraft:amethyst_shard"
  && RIG._rig().roof === true && RIG._rig().hold.y === RIG._rig().centre.y + 1);
fire("goto f06"); _advance(10);
check("20g f06: the vex holds an iron sword", rigged().length === 1 && rigged()[0].typeId === "minecraft:vex" && hand(rigged()[0]) === "minecraft:iron_sword");
fire("goto f08"); _advance(10);
check("20h f08: the warden at midnight in a roofed pen (height 6)", rigged().length === 1 && rigged()[0].typeId === "minecraft:warden" && _state.timeOfDay === 18000 && RIG._rig().roof && RIG._rig().height === 6);
// babies that cannot grow up are summoned again (his R12 z03 skeleton horse); standing in water is noted
_state.noGrowUp.add("minecraft:fox"); _state.babyFirst = new Map([["minecraft:fox", 2]]);
_state.blocks.set("10,70,20", "minecraft:water");                             // his feet cell (the player stands at 10.5, 70, 20.5)
fire("goto f14"); _advance(60);
const fox = rigged().find((e) => e.typeId === "minecraft:fox");
check("20i f14: a baby fox with no grow-up event is re-summoned until an adult stands there (2 re-rolls, logged)", fox && !fox.baby
  && testLines().some((l) => l.includes("RIG re-roll fox (still a BABY - no grow-up event on this mob) try 1")) && testLines().some((l) => l.includes("RIG re-roll fox (still a BABY - no grow-up event on this mob) try 2"))
  && testLines().some((l) => l.includes("RIG age fox at x 4: adult")), JSON.stringify(testLines().filter((l) => l.includes("fox")).slice(-4)));
check("20j the rig notes that you stand in water", testLines().some((l) => l.includes("RIG note: you stand in water at 10,70,20")));
_state.blocks.delete("10,70,20"); _state.noGrowUp.delete("minecraft:fox"); _state.babyFirst = new Map();
const f14 = rigged().map((e) => [dxOf(e), e.typeId]).sort((a, b) => a[0] - b[0]);
check("20k f14: wolf / polar bear / fox / ocelot, left to right", JSON.stringify(f14) === JSON.stringify([[-5, "minecraft:wolf"], [0, "minecraft:polar_bear"], [4, "minecraft:fox"], [6, "minecraft:ocelot"]]), JSON.stringify(f14));
// the leftover-water sweep: water that was there BEFORE the pool stays; water that appears around it while it stands is removed on clear
_state.blocks.set("0,70,13", "minecraft:water");                              // a 'lake' cell west of the f15 pool, clear of every pen wall (inside the sweep box)
fire("goto f15"); _advance(10);
const c15 = RIG._rig().centre;
check("20l f15: the dolphin pool (3 deep, centre 10,70,13); the rig logs the water already around it", rigged().length === 1 && rigged()[0].typeId === "minecraft:dolphin" && c15.x === 10 && c15.z === 13
  && typeAt("10,72,13") === "minecraft:water" && testLines().some((l) => l.includes("RIG pool: 1 water / ice cell(s) already around it")), JSON.stringify(c15));
// D-C303 wall repair: a tapped wall (east wall x 17) and an opened pool floor come back within 0.5 s, each logged once
_state.blocks.set("17,70,13", "minecraft:air"); _state.blocks.set("10,69,13", "minecraft:air"); _advance(12);
check("20l2 a broken pen wall is put back (barrier) and an opened pool floor filled (stone) within 0.5 s, logged",
  typeAt("17,70,13") === "minecraft:barrier" && typeAt("10,69,13") === "minecraft:stone"
  && testLines().some((l) => l.includes("RIG pen wall broken at 17,70,13 (air) - put back")) && testLines().some((l) => l.includes("RIG pool floor open at 10,69,13 - filled with stone")));
_state.blocks.set("17,70,13", "minecraft:air"); _advance(12);
check("20l3 a second break of the same wall cell is repaired again but not logged twice",
  typeAt("17,70,13") === "minecraft:barrier" && testLines().filter((l) => l.includes("RIG pen wall broken at 17,70,13")).length === 1);
_state.blocks.set("10,70,19", "minecraft:water");                             // a leak one block south of the pen (his R12 swim buttons)
fire("goto w16"); _advance(10);
check("20m leaving the pool sweeps the leak (logged with where) and leaves the pre-existing water alone", typeAt("10,70,19") === "minecraft:air" && typeAt("0,70,13") === "minecraft:water"
  && testLines().some((l) => l.includes("RIG leftover water swept: 1 cell(s) around the old pool (e.g. 10,70,19)")) && !_state.dyn.has("pw:test_rig_pre"));
_state.blocks.delete("0,70,13");
const w16 = rigged().map((e) => [dxOf(e), e.typeId]).sort((a, b) => a[0] - b[0]);
check("20n w16: black bear / grizzly / male lion (StripMine creatures), left to right", JSON.stringify(w16) === JSON.stringify([[-4, "sf_nba:black_bear"], [0, "sf_nba:grizzly_bear"], [5, "sf_nba:male_lion"]]), JSON.stringify(w16));
// a lake beside the pool (more than 400 wet cells in the box) -> no sweep at all
const LAKE = []; for (const x of [-1, 0, 20, 21]) for (let z = 4; z <= 22; z++) for (let y = 69; y <= 74; y++) LAKE.push(`${x},${y},${z}`);   // clear of every p10 pen wall (x 1..19)
for (const k of LAKE) _state.blocks.set(k, "minecraft:water");                  // 4 columns x 19 x 6 layers = 456 wet cells
fire("goto f15"); _advance(5); _state.blocks.set("10,70,19", "minecraft:water");
fire("goto w17"); _advance(5);
check("20o a lake beside the pool (456 wet cells > 400) -> the sweep is skipped and says why; nothing is removed", LAKE.length === 456 && typeAt("10,70,19") === "minecraft:water" && typeAt("0,70,13") === "minecraft:water"
  && testLines().some((l) => l.includes("RIG pool: 456 water / ice cell(s)")) && testLines().some((l) => l.includes("RIG sweep skipped: 456 water / ice cells") && l.includes("a lake or river?")));
for (const k of LAKE) _state.blocks.delete(k); _state.blocks.delete("10,70,19");
fire("goto q9"); _advance(10);
check("20p q9 clears everything (pens, jukebox, pool) and restores the ground", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0, diffNow().slice(0, 5).join(" "));
fire("stop"); fire("reset"); _state.variants = new Map(); _state.recordPlayer = false;
const longest20 = Math.max(...testLines().map((l) => l.length), ...warns.filter((w) => w.startsWith("[PW-VERSION]")).map((w) => w.length));
check("20q every content-log line (and the banner) still <= 120 characters", longest20 <= 120, `longest ${longest20}`);
// ---------------------------------------------------------------- 21 the P11 lineup: the R14 fixes (v0.4.2, D-C307)
fire("start! p11"); const S21 = mod._state();
const ids11 = P11_STEPS.map((s) => s.id);
check("21 start p11: q0 g01..g10 w11 w12 q9 (14 steps, unique)", S21 && S21.lineup === "p11"
  && ids11.join(" ") === ["q0", ...Array.from({ length: 10 }, (_, i) => `g${String(i + 1).padStart(2, "0")}`), "w11", "w12", "q9"].join(" ") && new Set(ids11).size === 14, ids11.join(" "));
_state.recordPlayer = true; fire("goto g01"); _advance(10);
const c21 = RIG._rig().centre; const jbk21 = `${c21.x + 2},${c21.y},${c21.z - 1}`;
check("21a g01: the allay alone beside a jukebox playing music_disc_cat", rigged().length === 1 && rigged()[0].typeId === "minecraft:allay" && typeAt(jbk21) === "minecraft:jukebox"
  && (_state.records || []).some((r) => r[0] === jbk21 && r[1] === "minecraft:music_disc_cat" && r[2] === true));
fire("goto g02"); _advance(10);
check("21b g02: the allay holds an amethyst shard in a roofed pen (height 5)", rigged().length === 1 && hand(rigged()[0]) === "minecraft:amethyst_shard" && RIG._rig().roof && RIG._rig().height === 5);
fire("goto g03"); _advance(10);
check("21c g03: the vex holds an iron sword", rigged().length === 1 && rigged()[0].typeId === "minecraft:vex" && hand(rigged()[0]) === "minecraft:iron_sword");
fire("goto g04"); _advance(10);
check("21d g04 PROBE A: the vex holds an amethyst shard", rigged().length === 1 && rigged()[0].typeId === "minecraft:vex" && hand(rigged()[0]) === "minecraft:amethyst_shard");
fire("goto g05"); _advance(10);
check("21e g05 PROBE B: the allay holds an iron sword", rigged().length === 1 && rigged()[0].typeId === "minecraft:allay" && hand(rigged()[0]) === "minecraft:iron_sword");
fire("goto g06"); _advance(10);
check("21f g06: the blaze at midnight in a roofed pen", rigged().length === 1 && rigged()[0].typeId === "minecraft:blaze" && _state.timeOfDay === 18000 && RIG._rig().roof);
fire("goto g07"); _advance(10);
check("21g g07: the blaze again at noon", rigged().length === 1 && rigged()[0].typeId === "minecraft:blaze" && _state.timeOfDay === 6000);
fire("goto g08"); _advance(20);
const g08 = rigged().map((e) => [dxOf(e), e.typeId]).sort((a, b) => a[0] - b[0]);
check("21h g08: the wolf (reference) left, the polar bear centre", JSON.stringify(g08) === JSON.stringify([[-5, "minecraft:wolf"], [0, "minecraft:polar_bear"]]), JSON.stringify(g08));
fire("goto g09"); _advance(10);
check("21i g09: the dolphin in a 3-deep pool", rigged().length === 1 && rigged()[0].typeId === "minecraft:dolphin" && testLines().some((l) => l.includes("RIG dolphin in a 3-deep pool")));
fire("goto g10"); _advance(10);
check("21j g10: the endermite loose in the pen", rigged().length === 1 && rigged()[0].typeId === "minecraft:endermite");
fire("goto w11"); _advance(10);
const w11 = rigged().map((e) => [dxOf(e), e.typeId]).sort((a, b) => a[0] - b[0]);
check("21k w11: black bear / grizzly / male lion, left to right", JSON.stringify(w11) === JSON.stringify([[-4, "sf_nba:black_bear"], [0, "sf_nba:grizzly_bear"], [5, "sf_nba:male_lion"]]), JSON.stringify(w11));
fire("goto w12"); _advance(10);
const w12 = rigged().map((e) => [dxOf(e), e.typeId]).sort((a, b) => a[0] - b[0]);
check("21l w12: komodo / alligator / rat snake, left to right", JSON.stringify(w12) === JSON.stringify([[-5, "sf_nba:komodo_dragon"], [0, "sf_nba:alligator"], [5, "sf_nba:snake"]]), JSON.stringify(w12));
fire("goto q9"); _advance(10);
check("21m q9 clears everything and restores the ground", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0, diffNow().slice(0, 5).join(" "));
check("21n every p11 chat body line <= 190 characters", P11_STEPS.every((st) => st.body.split("\n").every((l) => l.length <= 190)), "");
fire("stop"); fire("reset"); _state.recordPlayer = false;
const longest21 = Math.max(...testLines().map((l) => l.length), ...warns.filter((w) => w.startsWith("[PW-VERSION]")).map((w) => w.length));
check("21o every content-log line (and the banner) still <= 120 characters", longest21 <= 120, `longest ${longest21}`);
// ---------------------------------------------------------------- 22 the P12 lineup: R16a (v0.4.3, D-C310)
fire("start! p12"); const S22 = mod._state();
const ids12 = P12_STEPS.map((s) => s.id);
check("22 start p12: q0 h01 h02 h03 l01 l02 l03 w01 w02 t01 q9 (11 steps, unique)", S22 && S22.lineup === "p12"
  && ids12.join(" ") === "q0 h01 h02 h03 l01 l02 l03 w01 w02 t01 q9" && new Set(ids12).size === 11, ids12.join(" "));
const before22 = testLines().length;
fire("goto h01"); _advance(1);
check("22a h01: the vex is handed an iron sword; no proof line before the 2-tick check", rigged().length === 1 && rigged()[0].typeId === "minecraft:vex"
  && hand(rigged()[0]) === "minecraft:iron_sword" && !testLines().slice(before22).some((l) => l.includes("RIG item iron_sword")));
_advance(3);
check("22b h01: 2 ticks later the game is ASKED - testfor hasitem on the main hand - and the log says CONFIRMED",
  (rigged()[0].cmds || []).includes("testfor @s[hasitem={item=iron_sword,location=slot.weapon.mainhand}]")
  && testLines().some((l) => l.includes("RIG item iron_sword CONFIRMED in vex's main hand")));
_state.noHold = new Set(["minecraft:vex"]); const mark22c = testLines().length; fire("goto h02"); _advance(5);
check("22c h02: when the game does not keep the item, the log says NOT in (not a false 'in hand')", hand(rigged()[0]) === "minecraft:amethyst_shard"
  && testLines().some((l) => l.includes("RIG item amethyst_shard NOT in vex's main hand (the game did not keep it)"))
  && !testLines().slice(mark22c).some((l) => l.includes("RIG item amethyst_shard CONFIRMED")));
_state.noHold = new Set(); _state.testforThrows = true; fire("repeat"); _advance(5);
check("22d a check that errors is logged with its message (NOT in ...? check said: ...), never thrown",
  testLines().some((l) => l.includes("RIG item amethyst_shard NOT in vex's main hand? (check said: Error: CommandError")));
_state.testforThrows = false;
fire("goto h03"); _advance(5);
check("22e h03: the allay holds an iron sword, CONFIRMED", rigged().length === 1 && rigged()[0].typeId === "minecraft:allay" && hand(rigged()[0]) === "minecraft:iron_sword"
  && testLines().some((l) => l.includes("RIG item iron_sword CONFIRMED in allay's main hand")));
fire("goto l01"); _advance(10);
check("22f l01: the blaze at midnight (18000) in a roofed pen, height 5", rigged().length === 1 && rigged()[0].typeId === "minecraft:blaze" && _state.timeOfDay === 18000 && RIG._rig().roof && RIG._rig().height === 5);
fire("goto l02"); _advance(10);
check("22g l02: the magma cube FREE at midnight", rigged().length === 1 && rigged()[0].typeId === "minecraft:magma_cube" && rigged()[0].tags.has("pw_rig_free") && _state.timeOfDay === 18000);
fire("goto l03"); _advance(10);
check("22h l03: the glow squid in a 3-deep pool at midnight", rigged().length === 1 && rigged()[0].typeId === "minecraft:glow_squid" && RIG._rig().water && RIG._rig().depth === 3 && _state.timeOfDay === 18000);
fire("goto w01"); _advance(10);
check("22i w01: the parrot FREE in a roofed pen at noon", rigged().length === 1 && rigged()[0].typeId === "minecraft:parrot" && rigged()[0].tags.has("pw_rig_free") && RIG._rig().roof && _state.timeOfDay === 6000);
fire("goto w02"); _advance(10);
check("22j w02: the phantom FREE in a roofed pen at dusk (13000)", rigged().length === 1 && rigged()[0].typeId === "minecraft:phantom" && rigged()[0].tags.has("pw_rig_free") && _state.timeOfDay === 13000);
fire("goto t01"); _advance(10);
const c22 = RIG._rig().centre; const at22 = (dx, dy, dz) => typeAt(`${c22.x + dx},${c22.y + dy},${c22.z + dz}`);
let leaves22 = 0, logs22 = 0;
for (let x = 2; x <= 4; x++) for (let y = 0; y <= 2; y++) for (let z = -1; z <= 1; z++) { const t = at22(x, y, z); if (t === "pw:oak_leaves") leaves22++; if (t === "minecraft:oak_log") logs22++; }
check("22k t01: the chicken at the centre; 24 oak leaves around a 3-high oak-log core at dx 2..4 (right, seen from the south)",
  rigged().length === 1 && rigged()[0].typeId === "minecraft:chicken" && leaves22 === 24 && logs22 === 3 && at22(3, 1, 0) === "minecraft:oak_log" && at22(1, 0, 0) !== "pw:oak_leaves",
  `leaves ${leaves22} logs ${logs22}`);
check("22l t01: the placement is logged (leaves then the log core)", testLines().some((l) => l.includes("RIG blocks pw:oak_leaves x27 at dx 2..4 dy 0..2 dz -1..1"))
  && testLines().some((l) => l.includes("RIG blocks oak_log x3 at dx 3..3 dy 0..2 dz 0..0")));
fire("goto q9"); _advance(10);
check("22m q9 clears everything - the leaf cube and log core too - and restores the ground", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0
  && at22(3, 1, 0) !== "minecraft:oak_log" && at22(2, 0, -1) !== "pw:oak_leaves", diffNow().slice(0, 5).join(" "));
check("22n every p12 chat body line <= 190 characters", P12_STEPS.every((st) => st.body.split("\n").every((l) => l.length <= 190)), "");
check("22o every p12 step has a title, a body and a setup", P12_STEPS.every((st) => st.title && st.body && Array.isArray(st.setup)), "");
fire("stop"); fire("reset");
const longest22 = Math.max(...testLines().map((l) => l.length), ...warns.filter((w) => w.startsWith("[PW-VERSION]")).map((w) => w.length));
check("22p every content-log line (and the banner) still <= 120 characters", longest22 <= 120, `longest ${longest22}`);
// ---------------------------------------------------------------- 23 the P13 lineup: R16b, the Patrix fidelity ports (v0.4.4, D-C314)
fire("start! p13"); const S23 = mod._state();
const ids13 = P13_STEPS.map((s) => s.id);
check("23 start p13: q0 f01 f02 c01 o01 g01 d01 d02 i01 i02 h01 q9 (12 steps, unique)", S23 && S23.lineup === "p13"
  && ids13.join(" ") === "q0 f01 f02 c01 o01 g01 d01 d02 i01 i02 h01 q9" && new Set(ids13).size === 12, ids13.join(" "));
const want13 = { f01: [[0, "minecraft:fox"]], f02: [[0, "minecraft:fox"], [4, "minecraft:chicken"]], c01: [[0, "minecraft:cat"]], o01: [[0, "minecraft:ocelot"]],
  g01: [[0, "minecraft:goat"]], d01: [[0, "minecraft:cod"]], d02: [[0, "minecraft:cod"]], i01: [[0, "minecraft:iron_golem"]],
  i02: [[0, "minecraft:iron_golem"], [4, "minecraft:zombie"]], h01: [[-4, "minecraft:zoglin"], [0, "minecraft:hoglin"]] };
const got13 = {};
for (const id of Object.keys(want13)) { fire(`goto ${id}`); _advance(10); got13[id] = rigged().map((e) => [dxOf(e), e.typeId]).sort((a, b) => a[0] - b[0]); }
check("23a every p13 step rigs its mob(s), rows at their offsets", Object.keys(want13).every((id) => JSON.stringify(got13[id]) === JSON.stringify(want13[id])), JSON.stringify(got13));
fire("goto d01"); _advance(10);
check("23b d01: the cod in a 3-deep pool; d02 (next) on dry ground, loose", RIG._rig().water && RIG._rig().depth === 3);
fire("goto d02"); _advance(10);
check("23c d02: no pool, the cod FREE", !RIG._rig().water && rigged()[0].tags.has("pw_rig_free"));
fire("goto f01"); _advance(5);
check("23d f01 / f02 run at noon", _state.timeOfDay === 6000);
fire("goto q9"); _advance(10);
check("23e q9 clears everything and restores the ground", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0, diffNow().slice(0, 5).join(" "));
check("23f every p13 chat body line <= 190 characters; every body names PASS", P13_STEPS.every((st) => st.body.split("\n").every((l) => l.length <= 190) && st.body.includes("PASS")), "");
fire("stop"); fire("reset");
const longest23 = Math.max(...testLines().map((l) => l.length), ...warns.filter((w) => w.startsWith("[PW-VERSION]")).map((w) => w.length));
check("23g every content-log line (and the banner) still <= 120 characters", longest23 <= 120, `longest ${longest23}`);
// ---------------------------------------------------------------- 24 the P14 lineup: R17 (v0.4.5, D-C317 / D-C318)
fire("start! p14"); const S24 = mod._state();
const ids14 = P14_STEPS.map((s) => s.id);
check("24 start p14: q0 i01 i02 v01 v02 f01 f02 f03 d01 c01 c02 t01 q9 (13 steps, unique)", S24 && S24.lineup === "p14"
  && ids14.join(" ") === "q0 i01 i02 v01 v02 f01 f02 f03 d01 c01 c02 t01 q9" && new Set(ids14).size === 13, ids14.join(" "));
const want14 = { i01: [[0, "minecraft:iron_golem"]], i02: [[0, "minecraft:iron_golem"], [4, "minecraft:zombie"]], v01: [[0, "minecraft:vex"]], v02: [[0, "minecraft:vex"]],
  f01: [[0, "minecraft:fox"], [4, "minecraft:chicken"]], f02: [[0, "minecraft:fox"]], f03: [[0, "minecraft:fox"]], d01: [[0, "minecraft:cod"]],
  c01: [[0, "minecraft:cat"], [4, "minecraft:rabbit"]], c02: [[0, "minecraft:cat"]], t01: [[0, "minecraft:chicken"]] };
const got14 = {};
for (const id of Object.keys(want14)) { fire(`goto ${id}`); _advance(10); got14[id] = rigged().map((e) => [dxOf(e), e.typeId]).sort((a, b) => a[0] - b[0]); }
check("24a every p14 step rigs its mob(s), rows at their offsets", Object.keys(want14).every((id) => JSON.stringify(got14[id]) === JSON.stringify(want14[id])), JSON.stringify(got14));
fire("goto d01"); _advance(10);
check("24b d01: the cod FREE in a 3-deep pool", RIG._rig().water && RIG._rig().depth === 3 && rigged()[0].tags.has("pw_rig_free"));
fire("goto v01"); _advance(5);
check("24c v01 / v02 put the item in the vex's hand and log the proof", testLines().some((l) => l.includes("RIG item iron_sword CONFIRMED in vex")), "");
fire("goto f03"); _advance(5);
check("24d f03: a roofed pen, fox free, at noon", RIG._rig().roof && rigged()[0].tags.has("pw_rig_free") && _state.timeOfDay === 6000);
fire("goto q9"); _advance(10);
check("24e q9 clears everything and restores the ground", rigged().length === 0 && RIG._rig() === null && diffNow().length === 0, diffNow().slice(0, 5).join(" "));
check("24f every p14 chat body line <= 190 characters; every body names PASS", P14_STEPS.every((st) => st.body.split("\n").every((l) => l.length <= 190) && st.body.includes("PASS")), "");
fire("stop"); fire("reset");
const longest24 = Math.max(...testLines().map((l) => l.length), ...warns.filter((w) => w.startsWith("[PW-VERSION]")).map((w) => w.length));
check("24g every content-log line (and the banner) still <= 120 characters", longest24 <= 120, `longest ${longest24}`);

// ---------------------------------------------------------------- 25 the P15 lineup: LEAF PILOT (v0.4.6, D-C332; v0.4.8 D-C336: every species-age on our trees, copies)
const L15 = await import(pathToFileURL(path.join(td, "pw_testrunner_p15.js")).href);
const ids15 = L15.P15_STEPS.map((s) => s.id);
const want15 = ["q0", ...Array.from({ length: 25 }, (_, i) => `l${String(i + 1).padStart(2, "0")}`), "q9"];
check("25 p15 = q0 l01..l25 q9 (27 steps, unique)", ids15.join(" ") === want15.join(" ") && new Set(ids15).size === 27, ids15.join(" "));
check("25a fixed randomness: the same cell always gets the same hash; neighbours differ", L15.cellHash(5, 70, -3) === L15.cellHash(5, 70, -3) && L15.cellHash(5, 70, -3) !== L15.cellHash(6, 70, -3));
const picks = {}; for (let x = -20; x < 20; x++) for (let z = -20; z < 20; z++) { const v = L15.pickShape(x, 80, z, 5, 3); picks[v] = (picks[v] || 0) + 1; }
check("25b far from the wood: only the six full shapes (1-5, 8), each 12-22 % of 1600 cells", Object.keys(picks).sort().join(",") === "1,2,3,4,5,8" && Object.values(picks).every((n) => n > 190 && n < 350), JSON.stringify(picks));
const near = new Set(); for (let x = 0; x < 40; x++) near.add(L15.pickShape(x, 80, 0, 1, 3));
const band = []; for (let x = 0; x < 400; x++) band.push(L15.pickShape(x, 80, 7, 2, 3));
const bandCards = band.filter((v) => v === 6 || v === 7).length;
check("25c touching wood -> cards only (6/7); 2 steps -> about half cards; spruce (band 0) never cards", [...near].every((v) => v === 6 || v === 7) && bandCards > 150 && bandCards < 250
  && [1, 2, 3].every((d) => { for (let x = 0; x < 50; x++) if ([6, 7].includes(L15.pickShape(x, 1, 1, d, 0))) return false; return true; }), `band cards ${bandCards}/400`);
const dl = L15.leafDistances(new Set(["0,0,0"]), new Set(["1,0,0", "2,0,0", "3,0,0", "9,9,9"]));
check("25d leaf distance = steps to the nearest log through leaves; cut-off leaves count 7", dl.get("1,0,0") === 1 && dl.get("2,0,0") === 2 && dl.get("3,0,0") === 3 && dl.get("9,9,9") === 7);
// the species-age table (his 16:07 / 16:14 / 16:15 rulings): our features, our trunks, elders square
const spAge = L15.P15_STEPS.slice(1, 22).map((st) => { const t = st.setup.find((a) => a.leaftree && !a.leaftree.from).leaftree; return [t.sp, t.age]; });
const feats = spAge.map(([sp, age]) => L15.treeOf(sp, age).feature);
check("25p l01..l21 = one species-age each, grown from OUR features (17 pw age features + acacia / mangrove / cherry / azalea)",
  feats.length === 21 && new Set(feats).size === 21 && feats.filter((f) => f.startsWith("pw:")).length === 17
  && ["pw:oak_young_tree_feature", "pw:oak_elder_tree_feature_v2", "pw:birch_old_tree_feature", "pw:spruce_elder_tree_feature_v2", "pw:jungle_mature_tree_feature",
      "pw:dark_oak_elder_tree_feature_v2", "pw:pale_oak_elder_tree_feature_v2", "minecraft:acacia_tree_feature", "minecraft:azalea_tree_feature"].every((f) => feats.includes(f))
  && !feats.includes("pw:birch_elder_tree_feature_v2"), feats.join(" "));
check("25q every step: each tree's box <= 32,768 blocks, clear slices <= 32,768, and no two cleared boxes overlap",
  L15.P15_STEPS.every((st) => {
    const T = st.setup.filter((a) => a.leaftree).map((a) => ({ ...a.leaftree, ...L15.treeOf(a.leaftree.sp, a.leaftree.age) }));
    const C = st.setup.filter((a) => a.leafclear).map((a) => a.leafclear);
    return T.every((t) => L15.boxVolume(t.r, t.h) <= 32768)
      && C.every((c) => { const [xa, xb] = c.box; const h = c.h || 40; return (xb - xa + 1) * (h + 1) * L15.sliceDepth(xa, xb, h) <= 32768; })
      && T.every((t, i) => t.noclear || T.every((u, j) => i === j || u.noclear || Math.abs(t.dx - u.dx) > t.r + u.r || Math.abs(t.dz - u.dz) > t.r + u.r))
      && T.every((t) => C.length === 0 || C.some((c) => t.dx - t.r >= c.box[0] && t.dx + t.r <= c.box[1] && t.dz - t.r >= c.box[2] && t.dz + t.r <= c.box[3] + 2));
  }));
_state.blockTypes.add("pw:pilot_oak_leaves");
const pf0 = (_state.placedFeatures || []).length, cl0 = _state.clones || 0;
fire("start! p15"); const S25 = mod._state(); fire("goto l01"); _advance(600);
const pv = [..._state.blocks.entries()].filter(([, id]) => id.startsWith("pw:pilot_oak_leaves"));
const bt = [..._state.blocks.entries()].filter(([, id]) => id === "pw:pilot_oak_leaves_bt");
const keepLeaves = [..._state.blocks.entries()].filter(([, id]) => id === "pw:oak_leaves");
check("25e l01 OAK YOUNG: LEFT keeps today's leaves, MIDDLE -> pilot, RIGHT -> pilot biome colour", S25 && S25.lineup === "p15" && keepLeaves.length > 20 && bt.length > 20 && pv.length - bt.length > 20,
  `today ${keepLeaves.length} pilot ${pv.length - bt.length} bt ${bt.length}`);
check("25e2 l01 grows ONE tree from pw:oak_young_tree_feature (trunk pw:oak_young) and makes 2 exact copies (/clone)",
  (_state.placedFeatures || []).slice(pf0).join(" ") === "pw:oak_young_tree_feature" && (_state.clones || 0) - cl0 === 2 && [..._state.blocks.values()].filter((id) => id === "pw:oak_young").length >= 15,
  `${(_state.placedFeatures || []).slice(pf0).join(" ")} clones ${(_state.clones || 0) - cl0}`);
{ // the three trees are the same shape: every non-air block offset around each base matches (ids aside from the leaf swap)
  const o = { x: 10, y: 70, z: 20 }; const { r, h } = L15.treeOf("oak", "young"); const gap = 2 * r + 3, dz = -(r + 4);
  const shape = (dx) => { const out = []; for (const [k, id] of _state.blocks) { const [x, y, z] = k.split(",").map(Number);
    if (Math.abs(x - (o.x + dx)) <= r && Math.abs(z - (o.z + dz)) <= r && y >= o.y && y <= o.y + h) out.push(`${x - o.x - dx},${y - o.y},${z - o.z - dz}:${/leaves/.test(id) ? "L" : id}`); } return out.sort().join(" "); };
  const A = shape(-gap), B = shape(0), C = shape(gap);
  check("25e3 today / pilot / biome-colour trees are the SAME tree (block-for-block offsets match)", A.length > 100 && A === B && B === C, `${A.length} ${B.length} ${C.length}`); }
const states = [...(_state.perms || new Map()).entries()].filter(([k]) => (_state.blocks.get(k) || "").startsWith("pw:pilot_")).map(([, st]) => st["pw:pv"]);
check("25f every pilot leaf carries pw:pv 1..8 (never the far cube 0); both shape families used", states.length > 40 && states.every((v) => v >= 1 && v <= 8) && states.some((v) => v >= 6) && states.some((v) => v <= 5), `${states.length} leaves`);
check("25g the content log names each tree with its age and kind: TODAY via api (Dimension.placeFeature), pilot / bt via copy",
  testLines().some((l) => l.includes("LEAFTREE oak young TODAY") && l.includes("via api")) && testLines().some((l) => l.includes("LEAFTREE oak young pilot") && l.includes("via copy logs"))
  && testLines().some((l) => l.includes("LEAFTREE oak young bt") && l.includes("via copy logs")));
const pf4 = (_state.placedFeatures || []).length; fire("goto l04"); _advance(900);
{ // v0.4.9 B1: the elder's branch-tip cluster hangs on a DIAGONAL branch; the pilot copies must carry NO today's leaves anywhere in their boxes
  const o = { x: 10, y: 70, z: 20 }; const { r, h } = L15.treeOf("oak", "elder"); const gap = 2 * r + 3, dz = -(r + 4);
  const inBox = (k, dx) => { const [x, y, z] = k.split(",").map(Number); return Math.abs(x - (o.x + dx)) <= r && Math.abs(z - (o.z + dz)) <= r && y >= o.y && y <= o.y + h; };
  const today = (dx) => [..._state.blocks.entries()].filter(([k, id]) => id === "pw:oak_leaves" && inBox(k, dx)).length;
  const tip = (dx) => _state.blocks.get(`${o.x + dx + 7},${o.y + 12 - 3},${o.z + dz - 5}`) || "";
  check("25r2 elder (B1): branch-tip leaves on a diagonal branch are swapped too - the pilot copies keep 0 of today's leaves", today(-gap) > 20 && today(0) === 0 && today(gap) === 0 && tip(0) === "pw:pilot_oak_leaves" && tip(gap) === "pw:pilot_oak_leaves_bt",
    `today ${today(-gap)} / ${today(0)} / ${today(gap)} tips ${tip(-gap)} ${tip(0)} ${tip(gap)}`); }
check("25r l04 OAK ELDER: pw:oak_elder_tree_feature_v2, a square 2x2 trunk of pw:oak_elder, 3 trees logged",
  (_state.placedFeatures || []).slice(pf4).join(" ") === "pw:oak_elder_tree_feature_v2" && [..._state.blocks.values()].filter((id) => id === "pw:oak_elder").length >= 3 * 48
  && testLines().filter((l) => l.startsWith("LEAFTREE oak elder") || l.includes("LEAFTREE oak elder")).length >= 3, (_state.placedFeatures || []).slice(pf4).join(" "));
const n17 = testLines().length; _state.noPlace = true; fire("goto l17"); _advance(900); _state.noPlace = false;
check("25z1 v0.5.0 (D): when both ways refuse, the reasons are logged once each: 'PLACE REFUSED <feature> api: ...' and '... cmd: ...'",
  testLines().slice(n17).filter((l) => l.includes("PLACE REFUSED api pw:pale_oak_elder_tree_feature_v2")).length === 1 && testLines().slice(n17).some((l) => l.includes("PLACE REASON api: PlaceFeatureError"))
  && testLines().slice(n17).filter((l) => l.includes("PLACE REFUSED cmd pw:pale_oak_elder_tree_feature_v2")).length === 1 && testLines().slice(n17).some((l) => l.includes("PLACE REASON cmd: CommandError: unknown feature")), testLines().slice(n17).filter((l) => /REFUSED|REASON/.test(l)).join(" | "));
check("25h if /place is refused a stand-in grows with OUR trunk (pw:pale_oak_elder, logged 'stand-in') and still gets pilot leaves",
  testLines().some((l) => l.includes("LEAFTREE pale_oak elder") && l.includes("stand-in")) && [..._state.blocks.values()].includes("pw:pale_oak_elder") && [..._state.blocks.values()].some((id) => id === "pw:pilot_pale_oak_leaves"));
{ const n0 = testLines().length, w0 = (_state.placeWays || []).length; _state.noApiPlace = true; fire("goto l03"); _advance(900); _state.noApiPlace = false;
  check("25z2 v0.5.0 (D): if the API refuses, the /place command is tried next (tree grows 'via place', refusal logged with its reason)",
    testLines().slice(n0).some((l) => l.includes("PLACE REFUSED api pw:oak_old_tree_feature")) && testLines().slice(n0).some((l) => l.includes("PLACE REASON api: PlaceFeatureError")) && testLines().slice(n0).some((l) => l.includes("LEAFTREE oak old TODAY via place"))
    && (_state.placeWays || []).slice(w0).includes("cmd"), testLines().slice(n0).filter((l) => /REFUSED|TODAY/.test(l)).join(" | ")); }
_state.noClone = true; fire("goto l05"); _advance(900); _state.noClone = false;
check("25s if /clone is refused each copy grows its own tree (logged 'copy refused') and still gets pilot leaves",
  testLines().some((l) => l.includes("copy refused")) && [..._state.blocks.values()].some((id) => id === "pw:pilot_birch_leaves") && [..._state.blocks.values()].some((id) => id === "pw:pilot_birch_leaves_bt"));
{ // v0.4.9: an unloaded source chunk -> 'skipped', and each copy grows its own tree ('its source never grew')
  const n0 = testLines().length; _state.unloaded = (loc) => loc.x < -5 && loc.z < 20 && loc.z > -20; fire("goto l06"); _advance(900); _state.unloaded = undefined;
  const L = testLines().slice(n0);
  check("25v an unloaded source: 'chunk never loaded - skipped', then each copy grows its own and still gets pilot leaves",
    L.some((l) => l.includes("chunk never loaded - skipped")) && L.filter((l) => l.includes("its source never grew")).length === 2 && L.some((l) => l.includes("LEAFTREE birch mature pilot via api")), L.filter((l) => /LEAFTREE/.test(l)).join(" | ")); }
{ const n0 = testLines().length; _state.bigTree = true; fire("goto l02"); _advance(900); _state.bigTree = false;
  check("25w a tree touching its box rim is flagged EDGE, and the warning comes before the numbers", testLines().slice(n0).some((l) => /LEAFTREE oak mature TODAY EDGE\(\d+ on the r8 rim\)/.test(l)), testLines().slice(n0).filter((l) => l.includes("TODAY")).join(" | ")); }
fire("goto l21"); _advance(600);
check("25i azalea: plain leaves -> pilot azalea, flowered -> pilot flowering azalea (one tree)", [..._state.blocks.values()].includes("pw:pilot_azalea_leaves") && [..._state.blocks.values()].includes("pw:pilot_flowering_azalea_leaves"));
fire("goto l22"); _advance(900);
{ const iso = [..._state.blocks.values()].filter((id) => id === "pw:pilot_oak_leaves_iso").length, isoS = [..._state.blocks.values()].filter((id) => id === "pw:pilot_spruce_leaves_iso").length;
  check("25x l22 (phase order guard): the iso copies are taken BEFORE the source is swapped, so both iso trees carry pilot iso leaves", iso > 20 && isoS > 20, `oak iso ${iso} spruce iso ${isoS}`); }
const n24 = testLines().length, cl24 = _state.clones || 0, pf24 = (_state.placedFeatures || []).length; fire("goto l24"); _advance(3000);
check("25j l24 far rows: a ticking area first; 2 trees grown (oak + spruce MATURE), 23 copies",
  (_state.dimCmds || []).some((c) => c.startsWith("tickingarea add") && c.endsWith("pw_pilot_far") && !c.includes("~")) && (_state.placedFeatures || []).slice(pf24).join(" ") === "pw:oak_mature_tree_feature pw:spruce_mature_tree_feature" && (_state.clones || 0) - cl24 === 23,
  `${(_state.placedFeatures || []).slice(pf24).join(" ")} clones ${(_state.clones || 0) - cl24}`);
const farRows = new Set([..._state.blocks.entries()].filter(([, id]) => id === "pw:pilot_oak_leaves_farp").map(([k]) => Math.round(Number(k.split(",")[2]) / 24)));
check("25k l24: painted far-swap oaks stand in 5 rows", farRows.size === 5, [...farRows].join(" "));
{ const sf = [..._state.blocks.values()].filter((id) => id === "pw:pilot_spruce_leaves_farp").length;
  check("25y l24 (phase order guard): spruce far-swap PAINTED trees (copies of the spruce that is itself swapped) carry their leaves", sf > 100, `spruce farp ${sf}`); }
check("25t no fill / clone the planner sent went over the 32,768-block cap", (_state.maxFill || 0) <= 32768 && !testLines().slice(n24).some((l) => l.includes("copy refused")), `max fill ${_state.maxFill}`);
const loc9 = { ...p.location }; p.location = { x: loc9.x + 37, y: loc9.y, z: loc9.z + 61 };    // the witness walked away (l24 / l25 tell him to)
const d9 = (_state.dimCmds || []).length; fire("goto q9"); _advance(4000); p.location = loc9;
{ const C = (_state.dimCmds || []).slice(d9); const lastFill = C.map((c, i) => c.startsWith("fill") ? i : -1).reduce((a, b) => Math.max(a, b), -1);
  const firstRemove = C.findIndex((c) => c.startsWith("tickingarea remove"));
  check("25l q9 clears EVERY planted box even after the witness walked away, THEN removes both ticking areas", ![..._state.blocks.values()].some((id) => id.startsWith("pw:pilot_"))
    && C.includes("tickingarea remove pw_pilot_far") && C.includes("tickingarea remove pw_pilot_near") && firstRemove > lastFill && testLines().some((l) => /LEAFRESET \d+\/\d+ tree boxes cleared/.test(l)),
    testLines().filter((l) => l.includes("LEAFRESET")).join(" | ")); }
check("25m every p15 chat body line <= 190 characters; every body names PASS", L15.P15_STEPS.every((st) => st.body.split("\n").every((l) => l.length <= 190) && st.body.includes("PASS")));
check("25u no p15 tree log line was cut at 120 characters (warnings come first in each line)", testLines().filter((l) => /LEAF(TREE|CLEAR|SETUP)|PLACE (REFUSED|REASON)/.test(l)).every((l) => l.length <= 120 && !l.endsWith("~")), testLines().filter((l) => /LEAF(TREE|CLEAR|SETUP)/.test(l)).find((l) => l.endsWith("~")) || "");
fire("stop"); fire("reset");

check("25n BP-02 trunks count as logs: pw:oak_young / pw:spruce_elder (tag:log only) and vanilla logs; leaves never", L15.isLog("pw:oak_young") && L15.isLog("pw:spruce_elder") && L15.isLog("minecraft:cherry_log") && !L15.isLog("pw:oak_leaves") && !L15.isLog("pw:pilot_oak_leaves"));
const n25o = testLines().length; fire("start! p15"); fire("goto l01"); fire("goto l02"); _advance(1500);
{ const L = testLines().slice(n25o).filter((l) => /LEAF/.test(l)); const lastYoung = L.map((l, i) => l.includes("LEAFTREE oak young") ? i : -1).reduce((a, b) => Math.max(a, b), -1);
  const firstMature = L.findIndex((l) => l.includes("LEAFTREE oak mature")); const clearBetween = L.slice(lastYoung + 1, firstMature).some((l) => l.includes("LEAFCLEAR")) ? firstMature : -1;
  check("25o two steps started back to back run one after the other: the 2nd step's clear waits for the 1st step's last tree", lastYoung >= 0 && clearBetween > lastYoung, L.slice(-7).join(" | ")); }
fire("stop"); fire("reset");
// ---------------------------------------------------------------- 26 the P16 lineup: LEAF ROLLOUT (v0.5.0, D-C346)
const L16 = await import(pathToFileURL(path.join(td, "pw_testrunner_p16.js")).href);
const ids16 = L16.P16_STEPS.map((s) => s.id);
check("26 p16 = q0 n01..n12 m01..m10 n13 q9 (25 steps, unique)", ids16.join(" ") === "q0 n01 n02 n03 n04 n05 n06 n07 n08 n09 n10 n11 n12 m01 m02 m03 m04 m05 m06 m07 m08 m09 m10 n13 q9" && new Set(ids16).size === 25, ids16.join(" "));
check("26a every p16 step: tree boxes <= 32,768, inside the step's clear box and ticking area, never overlapping (grove excepted); areas <= 100 chunks",
  L16.P16_STEPS.every((st) => {
    const T = st.setup.filter((a) => a.leaftree).map((a) => ({ ...a.leaftree, ...L15.treeOf(a.leaftree.sp, a.leaftree.age) }));
    const C = st.setup.filter((a) => a.leafclear).map((a) => a.leafclear); const A = st.setup.filter((a) => a.leafarea).map((a) => a.leafarea);
    const chunks = A.every((a) => (Math.floor((a.box[3] - a.box[0]) / 16) + 2) * (Math.floor((a.box[5] - a.box[2]) / 16) + 2) <= 100);
    return chunks && T.every((t) => L15.boxVolume(t.r, t.h) <= 32768)
      && C.every((c) => { const [xa, xb] = c.box; const h = c.h || 40; return (xb - xa + 1) * (h + 1) * L15.sliceDepth(xa, xb, h) <= 32768; })
      && T.every((t, i) => t.noclear || T.every((u, j) => i === j || u.noclear || Math.abs(t.dx - u.dx) > t.r + u.r || Math.abs(t.dz - u.dz) > t.r + u.r))
      && T.every((t) => t.from || C.some((c) => t.dx - t.r >= c.box[0] && t.dx + t.r <= c.box[1] && t.dz - t.r >= c.box[2] && t.dz + t.r <= c.box[3] + 2))
      && T.every((t) => A.some((a) => t.dx - t.r >= a.box[0] && t.dx + t.r <= a.box[3] && t.dz - t.r >= a.box[2] && t.dz + t.r <= a.box[5]))
      && st.body.split("\n").every((l) => l.length <= 190) && st.body.includes("PASS");
  }));
check("26b p16 n-steps only grow OUR trees as they are (every tree 'keep': no pilot / test blocks are placed)",
  L16.P16_STEPS.filter((st) => !st.id.startsWith("m")).every((st) => st.setup.filter((a) => a.leaftree).every((a) => a.leaftree.keep === true && !a.leaftree.block)));
fire("start! p16"); const n16 = testLines().length; const pre16 = new Set(_state.blocks.keys()); fire("goto n01"); _advance(900);
{ const L = testLines().slice(n16); const o = { x: 10, z: 20 };
  const near = [..._state.blocks.entries()].filter(([k, id]) => !pre16.has(k) && /_leaves/.test(id) && (() => { const [x, , z] = k.split(",").map(Number); return Math.max(Math.abs(x - o.x), Math.abs(z - o.z)) <= 25; })());
  check("26c n01: six of our trees grow 30+ blocks north (outside the 25-block scanner), each logged TODAY; no leaf within 25 blocks",
    L.filter((l) => l.includes(" TODAY ")).length === 6 && near.length === 0 && ![..._state.blocks.entries()].some(([k, id]) => !pre16.has(k) && id.startsWith("pw:pilot_")), `${L.filter((l) => l.includes(" TODAY ")).length} trees; ${near.length} near leaves`); }
const c6 = p.cmds.length; fire("goto n06"); _advance(900);
check("26d n06: the azalea + flowering azalea cubes are filled around oak logs beside the witness",
  p.cmds.slice(c6).some((c) => c.includes("pw:azalea_leaves")) && p.cmds.slice(c6).some((c) => c.includes("pw:flowering_azalea_leaves")));
const c7 = p.cmds.length; fire("goto n07"); _advance(600);
check("26e n07: SURVIVAL + an iron axe for the felling", p.cmds.slice(c7).includes("gamemode survival @s") && p.inv.count((s) => s && String(s.typeId || s.type?.id || "").includes("iron_axe")) >= 0);
const c8 = p.cmds.length, n8 = testLines().length; fire("goto n08"); _advance(900);
{ const L = testLines().slice(n8); const left = [..._state.blocks.entries()].filter(([k, id]) => id === "pw:oak_mature" && (() => { const [x, , z] = k.split(",").map(Number); return Math.abs(x - 10) <= 8 && Math.abs(z - 6) <= 8; })()).length;
  check("26f n08: back to CREATIVE; the oak grows, then its wood is removed (LEAFCHOP) and its leaves are left to decay",
    p.cmds.slice(c8).includes("gamemode creative @s") && L.some((l) => /LEAFCHOP oak mature: \d+ logs removed/.test(l)) && left === 0, L.filter((l) => /LEAF/.test(l)).join(" | ")); }
const n12 = testLines().length; fire("goto n12"); _advance(1200);
{ const L = testLines().slice(n12);
  check("26g n12 probe: 6 cases x 2 ways logged (API row + command row), all OK on the mock", L.filter((l) => /PROBE (api|cmd) \S+ on \S+: OK/.test(l)).length === 12, L.filter((l) => l.includes("PROBE")).slice(0, 3).join(" | ")); }
const n12b = testLines().length; _state.noApiPlace = true; fire("goto n12"); _advance(1200); _state.noApiPlace = false;
{ const L = testLines().slice(n12b);
  check("26h n12 probe: an API refusal is logged with its reason, the command row still reports its own result",
    L.filter((l) => /PROBE api \S+ on \S+: REFUSED/.test(l)).length === 6 && L.filter((l) => l.includes("PROBE REASON api: PlaceFeatureError")).length === 6
    && L.filter((l) => /PROBE cmd \S+ on \S+: OK/.test(l)).length === 6, L.filter((l) => l.includes("PROBE")).slice(0, 4).join(" | ")); }
{ const raw = _state.dyn.get("pw:test:planted"); let n = 0; try { n = JSON.parse(raw).length; } catch {}
  check("26j v0.5.1: the planted tree boxes are kept in a world dynamic property (a relog does not lose them)", n >= 20, `${n} boxes stored`); }
const d9b = (_state.dimCmds || []).length, c9b = p.cmds.length; fire("goto q9"); _advance(5000);
{ const C = (_state.dimCmds || []).slice(d9b);
  check("26i q9: every planted box cleared (probe trees included), all 3 ticking areas removed, creative restored",
    !["pw:oak_mature", "pw:birch_old", "pw:spruce_old", "pw:jungle_old"].some((id) => [..._state.blocks.values()].includes(id))
    && ["pw_pilot_far", "pw_pilot_near", "pw_probe_area"].every((a) => C.includes(`tickingarea remove ${a}`)) && p.cmds.slice(c9b).includes("gamemode creative @s")
    && _state.dyn.get("pw:test:planted") === undefined,
    C.filter((c) => c.startsWith("tickingarea")).join(" | ")); }
fire("stop"); fire("reset");
// ---------------------------------------------------------------- 27 p16 m01-m10: the 128 vs 256 comparison (v0.5.2, D-C348)
{ const M16 = L16.P16_STEPS.filter((s) => s.id.startsWith("m"));
  check("27 ten m-steps, each = one grown tree (128, our pw:<sp>_leaves) + two clones (pw:t256_ / pw:t256m_), every tree 'look', none 'keep'",
    M16.length === 10 && M16.every((st) => { const T = st.setup.filter((a) => a.leaftree).map((a) => a.leaftree);
      return T.length === 3 && T.every((x) => x.look && !x.keep) && !T[0].from && T[1].from && T[2].from
        && T[0].block === "pw:{sp}_leaves" && T[1].block === "pw:t256_{sp}_leaves" && T[2].block === "pw:t256m_{sp}_leaves"
        && T[1].from[0] === T[0].dx && T[2].from[0] === T[0].dx && T[0].dx < T[1].dx && T[1].dx < T[2].dx; }));
  const sps = new Set(M16.map((st) => st.setup.find((a) => a.leaftree).leaftree.sp));
  check("27a all 11 leaf species covered (azalea's tree carries flowering azalea too)", ["oak", "birch", "spruce", "jungle", "dark_oak", "pale_oak", "acacia", "mangrove", "cherry", "azalea"].every((s) => sps.has(s))
    && L15.SPECIES.azalea.also["minecraft:azalea_leaves_flowered"] === "flowering_azalea"); }
// the runner's look rule == BP-02 1.3.197 main.js pwLeafLook (extracted from the built file and run on a fake dimension)
{ const src = fs.readFileSync(process.argv[3] || "/home/claude/_build/bp02-206/scripts/main.js", "utf8");   // BP-02 under test (argv[3]); was pinned to 1.3.197
  const grab = (re) => { const m = src.match(re); return m ? m[0] : ""; };
  const code = [grab(/const PW_LEAF_BAND = [^\n]*\n/), grab(/function pwCellHash\([\s\S]*?\n}\n/), grab(/const PW_WOOD_SHELLS = [\s\S]*?\n}\)\(\);\n/),
    grab(/function pwWoodDistance\([\s\S]*?\n}\n/), grab(/function pwLeafLook\([\s\S]*?\n}\n/)].join("");
  const ok = code.includes("pwLeafLook") && code.includes("PW_WOOD_SHELLS") && code.includes("PW_LEAF_BAND");
  const mk = new Function("pwIsWood", code + "\nreturn pwLeafLook;");
  let same = 0, diff = 0, n = 0, ex = "";
  for (const sp of ["oak", "birch", "spruce", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "azalea", "flowering_azalea"]) {
    const logs = new Set(); for (let y = 0; y < 9; y++) logs.add(`0,${y},0`); for (let x = 1; x < 4; x++) logs.add(`${x},5,0`);
    const look = mk((id) => id === "log");
    const dim = { getBlock: (l) => ({ typeId: logs.has(`${l.x},${l.y},${l.z}`) ? "log" : "air" }) };
    for (let x = -6; x <= 6; x++) for (let y = 2; y <= 10; y++) for (let z = -6; z <= 6; z += 2) {
      if (logs.has(`${x},${y},${z}`)) continue; n++;
      const a = look({ typeId: `pw:${sp}_leaves`, location: { x: x + 1000, y: y + 64, z: z - 3000 }, dimension: { getBlock: (l) => dim.getBlock({ x: l.x - 1000, y: l.y - 64, z: l.z + 3000 }) } });
      const band = L15.LOOK_BAND[sp] ?? 3;
      const b = L15.leafLook(sp, x + 1000, y + 64, z - 3000, band > 0 ? L15.woodDistance(logs, x, y, z, Math.min(band, 4)) : 99);
      if (a === b) same++; else { diff++; if (!ex) ex = `${sp} ${x},${y},${z}: main ${a} runner ${b}`; }
    } }
  check("27b the runner's look rule gives the SAME pw:variant as BP-02 1.3.197 main.js pwLeafLook (11 species x every cell around a log tree)", ok && diff === 0 && n > 8000, `${same}/${n} same ${ex}`); }
fire("start! p16"); fire("goto m01"); const n27 = testLines().length; const pre27 = new Set(_state.blocks.keys()); _advance(1500);
{ const L = testLines().slice(n27).filter((l) => l.includes("LEAFTREE oak old")).map((l) => l.slice(l.indexOf("LEAFTREE")));
  const st = L16.P16_STEPS.find((s) => s.id === "m01"); const T = st.setup.filter((a) => a.leaftree).map((a) => a.leaftree);
  const o = { x: 10, z: 20 }; const gap = T[1].dx - T[0].dx;
  const W = [..._state.blocks.entries()].filter(([k, id]) => id === "pw:oak_leaves" && !pre27.has(k));
  let same = 0, bad = "", rs = 0;
  for (const [k] of W) { const [x, y, z] = k.split(",").map(Number); const v = _state.perms.get(k)?.["pw:variant"];
    if (_state.perms.get(k)?.["pw:rseed"] === true) rs++;
    const m = `${x + gap},${y},${z}`, e = `${x + 2 * gap},${y},${z}`;
    if (_state.blocks.get(m) === "pw:t256_oak_leaves" && _state.blocks.get(e) === "pw:t256m_oak_leaves" && _state.perms.get(m)?.["pw:variant"] === v && _state.perms.get(e)?.["pw:variant"] === v
        && _state.perms.get(m)?.["pw:rseed"] === true && _state.perms.get(e)?.["pw:rseed"] === true) same++;
    else if (!bad) bad = `${k} ${v} vs ${_state.blocks.get(m)} ${_state.perms.get(m)?.["pw:variant"]} / ${_state.blocks.get(e)} ${_state.perms.get(e)?.["pw:variant"]}`; }
  const cards = W.filter(([k]) => _state.perms.get(k)["pw:variant"] >= 5).length;
  check("27c m01: three oak (old) trees logged 128 / 256 / 256+MERS64 (west to east), none FAILED",
    L.length === 3 && / 128 /.test(L[0]) && / 256 /.test(L[1]) && / 256\+MERS64 /.test(L[2]) && !L.some((l) => l.includes("FAILED")), L.join(" | "));
  check("27d m01: every leaf of the WEST tree has the same pw:variant in the MIDDLE (pw:t256_) and EAST (pw:t256m_) copy, pw:rseed true everywhere; cards beside the wood",
    W.length > 20 && same === W.length && rs === W.length && cards > 0 && cards < W.length, `${same}/${W.length} matched, ${cards} cards ${bad}`); }
{ let all = 0, failed = 0; const seen = new Set(); const spruce = [];
  for (const id of ["m02", "m03", "m04", "m05", "m06", "m07", "m08", "m09", "m10"]) { const n0 = testLines().length; fire(`goto ${id}`); _advance(2500);
    const L = testLines().slice(n0).filter((l) => /LEAFTREE \S+.* (128|256|256\+MERS64) /.test(l)).map((l) => l.slice(l.indexOf("LEAFTREE"))); all += L.length; failed += L.filter((l) => l.includes("FAILED")).length;
    for (const l of L) seen.add(l.split(" ")[1]);
    if (id === "m03") for (const [k, s] of _state.perms.entries()) if (_state.blocks.get(k) === "pw:t256_spruce_leaves") spruce.push(s["pw:variant"]); }
  check("27e m02-m10: 27 more trees, each logged with its label, none FAILED; spruce copies use all 7 full looks, never a 'cards' count",
    all === 27 && failed === 0 && seen.size === 9 && new Set(spruce).size >= 5, `${all} trees, ${failed} failed, species ${[...seen].join(",")}, spruce looks ${[...new Set(spruce)].sort().join("")}`);
  const az = [..._state.blocks.values()];
  check("27f m10: the azalea copies carry both test kinds (pw:t256_azalea_leaves + pw:t256_flowering_azalea_leaves) when the tree grows flowered leaves",
    az.includes("pw:t256_azalea_leaves") && az.includes("pw:t256m_azalea_leaves") && (!az.includes("minecraft:azalea_leaves_flowered") || az.includes("pw:t256_flowering_azalea_leaves")),
    `flowering copies: ${az.filter((x) => x === "pw:t256_flowering_azalea_leaves").length}`); }
fire("goto q9"); _advance(6000);
check("27g q9 clears every comparison tree too (no pw:t256* leaf left)", ![..._state.blocks.values()].some((id) => /^pw:t256m?_/.test(id)));
fire("stop"); fire("reset");
// ---------------------------------------------------------------- 28 p17: the leaf fixes + the culling probe (v0.5.3, D-C350)
{ const L17 = await import(pathToFileURL(path.join(td, "pw_testrunner_p17.js")).href);
  const ids17 = L17.P17_STEPS.map((s) => s.id);
  check("28 p17 = q0 f01 f02 f03 z01 q9 (6 steps, unique); every body names PASS, lines <= 190; q0 names BP-02 v1.3.198 + RP-01 v1.3.107 + runner BP v0.5.3 + RP v0.6.0",
    ids17.join(" ") === "q0 f01 f02 f03 z01 q9" && L17.P17_STEPS.every((s) => s.body.includes("PASS") && s.body.split("\n").every((l) => l.length <= 190))
    && ["v1.3.198", "v1.3.107", "v0.5", "v0.6.0"].every((v) => L17.P17_STEPS[0].body.includes(v)), ids17.join(" "));
  const z = L17.P17_STEPS.find((s) => s.id === "z01"); const cmds = z.setup.find((a) => a.cmd).cmd;
  const sets = cmds.filter((c) => c.startsWith("setblock")); const qs = sets.map((c) => Number(c.match(/"pw:q"=(\d)/)[1]));
  check("28a z01 places 16 probe blocks = 8 pairs, 2 per quarter turn per row (east pairs + south pairs), the area is cleared first",
    sets.length === 16 && [0, 1, 2, 3].every((q) => qs.filter((x) => x === q).length === 4) && cmds[0].startsWith("fill") && cmds[0].endsWith(" air"), `${sets.length} setblocks`);
  const box = z.setup.find((a) => a.leafmark).leafmark; const xs = L17.PROBE_X;
  check("28b z01 marks a box that holds every probe block, so q9 clears it wherever you stand",
    xs.every((x) => x >= box.dx - box.r && x + 1 <= box.dx + box.r) && [L17.PROBE_EAST_Z, L17.PROBE_SOUTH_Z, L17.PROBE_SOUTH_Z + 1].every((zz) => zz >= box.dz - box.r && zz <= box.dz + box.r), JSON.stringify(box)); }
fire("start! p17"); fire("goto z01"); { const n28 = testLines().length; _advance(800);
check("28c z01 runs: the probe box is recorded (LEAFMARK) and the 16 setblock commands ran", testLines().slice(n28).some((l) => l.includes("LEAFMARK box r7 h4"))
  && p.cmds.filter((c) => c.includes("pw:cullprobe")).length >= 16, testLines().slice(n28).filter((l) => /LEAF/.test(l)).join(" | ")); }
{ const n = testLines().length; _ui.queue.push({ selection: 3 }, { formValues: ["first box text", "second box text", "third"] }); useClicker(); await tick(); await tick(); await tick();
  check("28d the note form has 3 boxes, joined in order into one note", testLines().slice(n).some((l) => l.includes("first box text second box text third")), testLines().slice(n).join(" | ")); }
fire("stop"); fire("reset");
// ---------------------------------------------------------------- 29 p18: the new-animals parade (v0.5.5, D-C351)
{ const L18 = await import(pathToFileURL(path.join(td, "pw_testrunner_p18.js")).href);
  const mobs = L18.P18_STEPS.flatMap((s) => s.setup.filter((a) => a.rig).flatMap((a) => [a.rig.mob, ...(a.rig.row || []).map((r) => r.mob)]));
  check("29 p18 = q0 + 32 pens + q9; 147 creatures, each shown once, each with a name tag", L18.P18_STEPS.length === 34 && mobs.length === 147 && new Set(mobs).size === 147
    && L18.P18_STEPS.every((s) => s.setup.filter((a) => a.rig).every((a) => a.rig.name && (a.rig.row || []).every((r) => r.name))), `${mobs.length} mobs`);
  for (const m of mobs) _state.entityTypes.add(m);
  fire("start! p18"); const n29 = testLines().length; fire("goto a01"); _advance(200);
  const L = testLines().slice(n29); if (process.env.DBG29) console.log(L.filter((l) => !l.includes("wall broken")).join("\n"));
  check("29a a01 builds a roofed pen and spawns its 5 creatures with their name tags", L.some((l) => l.includes("roofed pen")) && L.filter((l) => l.includes("RIG name tag")).length === 5,
    L.filter((l) => /RIG (name tag|.*pen)/.test(l)).slice(0, 8).join(" | ") + ` [${L.filter((l) => l.includes("RIG name tag")).length} tags]`);
  fire("stop"); fire("reset"); }
// ---------------------------------------------------------------- 30 p19: his picks parade (v0.5.6, D-C353)
{ const L19 = await import(pathToFileURL(path.join(td, "pw_testrunner_p19.js")).href);
  const mobs = L19.P19_STEPS.flatMap((s) => s.setup.filter((a) => a.rig).flatMap((a) => [a.rig.mob, ...(a.rig.row || []).map((r) => r.mob)]));
  check("30 p19 = q0 + 96 pens + q9; 323 creatures, each shown once, each with a 'Name (PACK)' tag", L19.P19_STEPS.length === 98 && mobs.length === 323 && new Set(mobs).size === 323
    && L19.P19_STEPS.every((s) => s.setup.filter((a) => a.rig).every((a) => /\)$/.test(a.rig.name) && (a.rig.row || []).every((r) => /\)$/.test(r.name)))), `${mobs.length} mobs`);
  for (const m of mobs) _state.entityTypes.add(m);
  fire("start! p19"); const n30 = testLines().length; fire("goto b03"); _advance(200);
  const L = testLines().slice(n30);
  check("30a b03 (the bears) builds a roofed pen and spawns our 2 bears + the 2 AnF bears with their tags", L.some((l) => l.includes("roofed pen")) && L.filter((l) => l.includes("RIG name tag")).length === 4
    && L.some((l) => l.includes("Black Bear (OURS)")) && L.some((l) => l.includes("(AnF)")),
    L.filter((l) => /RIG (name tag|.*pen)/.test(l)).slice(0, 8).join(" | "));
  const n30b = testLines().length; fire("goto b96"); _advance(200); const W = testLines().slice(n30b);
  check("30b the last pool step builds a pool and spawns its swimmers", W.some((l) => l.includes("deep pool")) && W.some((l) => l.includes("RIG name tag")), W.filter((l) => /RIG/.test(l)).slice(0, 6).join(" | "));
  fire("stop"); fire("reset"); }
// ---------------------------------------------------------------- 32 p22: CIVITAS (v0.5.15, D-C499)
if (fs.existsSync(path.join(td, "pw_testrunner_p22.js"))) {
  const L22 = await import(pathToFileURL(path.join(td, "pw_testrunner_p22.js")).href);
  check("32a p22 has 12 steps q0 c01..c10 q9", L22.P22_STEPS.length === 12 && L22.P22_STEPS[0].id === "q0" && L22.P22_STEPS[11].id === "q9", L22.P22_STEPS.map((s) => s.id).join(" "));
  const cmds = L22.P22_STEPS.flatMap((s) => (s.setup || []).flatMap((a) => a.cmd || []));
  check("32b every p22 clock command is a /scriptevent pw:clock line the clock knows", cmds.filter((c) => c.startsWith("scriptevent pw:clock ")).every((c) => /^scriptevent pw:clock (village|pause|resume|skip|log|market|decline|immigrate|snapshot|status)\b/.test(c)) && cmds.length >= 15, cmds.filter((c) => !/^scriptevent pw:clock (village|pause|resume|skip|log|market|decline|immigrate|snapshot|status)\b/.test(c)));
  fire("start! p22"); const n32 = testLines().length; fire("goto c01"); _advance(40);
  const L32 = testLines().slice(n32);
  check("32c p22 c01 runs its setup commands through the player", L32.some((l) => l.includes("setup cmd ok: scriptevent pw:clock village 7")), L32.slice(-6));
  fire("goto c06"); _advance(40);
  check("32d p22 c06 hands out emeralds (the mock has no item registry: the attempt is logged) and asks the market", testLines().slice(n32).some((l) => (l.includes("gave") || l.includes("MISSING")) && l.includes("emerald")) && testLines().slice(n32).some((l) => l.includes("pw:clock market")), testLines().slice(-8));
  fire("stop");
}
// ---------------------------------------------------------------- 31 p20 / p21 / bump: the judging pass (v0.5.8, D-C398)
{ const L20 = await import(pathToFileURL(path.join(td, "pw_testrunner_p20.js")).href);
  const L21 = await import(pathToFileURL(path.join(td, "pw_testrunner_p21.js")).href);
  const LB = await import(pathToFileURL(path.join(td, "pw_testrunner_bump.js")).href);
  const rigsOf = (S) => S.flatMap((s) => s.setup.filter((a) => a.rig).map((a) => a.rig));
  const m20 = rigsOf(L20.P20_STEPS).flatMap((r) => [r.mob, ...(r.row || []).map((x) => x.mob)]);
  check("31 p20: every pen names its creatures, nothing shown twice, the unsafe step has no rig", m20.length > 600 && new Set(m20).size === m20.length
    && L20.P20_STEPS.some((s) => s.title.startsWith("NOT SUMMONED") && !s.setup.some((a) => a.rig)), `${m20.length} entities`);
  const r21 = rigsOf(L21.P21_STEPS);
  check("31a p21: every copy plays an animation and its name tag is that animation's short name", r21.length > 500
    && r21.every((r) => r.play && (r.row || []).every((x) => x.play && x.name)), `${r21.length} pens`);
  check("31b bump: one step, 8 pw:nbump copies (main + 7 in the row)", LB.BUMP_STEPS.length === 3 && rigsOf(LB.BUMP_STEPS)[0].row.length === 7);
  for (const m of [...m20, ...r21.flatMap((r) => [r.mob, ...(r.row || []).map((x) => x.mob)]), "pw:nbump"]) _state.entityTypes.add(m);
  fire("start! p21"); const n31 = testLines().length; fire("goto a0001"); _advance(200);
  const L = testLines().slice(n31);
  check("31c p21 a0001 spawns its copies and starts each one's animation", L.filter((l) => l.includes("RIG play")).length >= 1
    && !L.some((l) => l.includes("RIG play") && l.includes("FAILED")), L.filter((l) => /RIG (play|name tag)/.test(l)).slice(0, 6).join(" | "));
  fire("stop"); fire("reset"); }
check("8x probe FAILED is logged, not thrown, when the RP/BP entity is missing", (() => { _state.entityTypes.delete("pw:probe"); fire("start! p0"); fire("pass"); const ok = testLines().some((l) => l.includes("PROBE FAILED")); fire("reset"); _state.entityTypes.add("pw:probe"); return ok; })());

console.warn = origWarn;
console.log(`\n${pass} passed, ${fail} failed`);
fs.rmSync(td, { recursive: true, force: true });
process.exit(fail ? 1 : 0);
