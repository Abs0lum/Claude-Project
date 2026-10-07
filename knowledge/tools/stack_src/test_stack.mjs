// test_stack.mjs — mock-runs the SHIPPED scripts of BP-01 v1.3.35, BP-02 v1.3.186 (weather + fireflies) and
// BP-03 v1.3.34 against mock_mc.mjs (installed as node_modules/@minecraft/server).  One mode per process, so
// every mode gets a fresh module graph (a "world load").  usage: node test_stack.mjs <mode> [bp02dir]
//   modes: bp01 | bp01-reload | weather | bp02 | bp03
import * as M from "@minecraft/server";
import { readFileSync, writeFileSync } from "node:fs";

const warns = []; console.warn = (...a) => warns.push(a.join(" "));
let pass = 0, fail = 0;
function ok(name, cond, info) {
  if (cond) { pass++; console.log("  ok   " + name); }
  else { fail++; console.log("  FAIL " + name + (info !== undefined ? "  -> " + JSON.stringify(info) : "")); }
}
const strip = (s) => String(s).replace(/§./g, "");
const lastPush = (p) => [...p.cmds].reverse().find((c) => c.includes(" push "));
const pushes = (p) => p.cmds.filter((c) => c.includes(" push ")).length;
const mode = process.argv[2];
const B02 = process.argv[3] || "bp02";

async function bp01() {
  const p = new M.MockPlayer("Abs0lum"); M._state.players.push(p);
  let err = null; try { await import("./bp01/main.js"); } catch (e) { err = String(e); }
  ok("BP-01 loads while scripts load (no world call at the top level — 2.x early execution)", err === null, err);
  ok("subscribes weatherChange once (pw_weather.js) + playerLeave once", M.world.afterEvents.weatherChange.count === 1 && M.world.afterEvents.playerLeave.count === 1);
  ok("two intervals: fog 40 t, ambient 200 t", JSON.stringify(M._state.intervals.map((i) => i.t).sort((a, b) => a - b)) === "[40,200]");
  M._ready(); Math.random = () => 0;
  M._advance(40);
  ok("clear noon: 'fog @s remove ar_sky' then 'fog @s push \"pw:ar_sky_day\" ar_sky' via runCommand",
     p.cmds.length === 2 && p.cmds[0] === "fog @s remove ar_sky" && p.cmds[1] === 'fog @s push "pw:ar_sky_day" ar_sky', p.cmds);
  M.world.afterEvents.weatherChange.fire({ dimension: "minecraft:overworld", newWeather: "Rain", previousWeather: "Clear" });
  ok("rain is saved in the world dynamic property", M._state.dyn.get("pw:weather_cache") === '{"overworld":"Rain"}', M._state.dyn.get("pw:weather_cache"));
  M._advance(40);
  ok("rain -> sky fog pw:ar_sky_rain (first time this state can engage)", lastPush(p) === 'fog @s push "pw:ar_sky_rain" ar_sky', lastPush(p));
  M._advance(120);   // tick 200: ambient beat
  ok("rain -> ambient beat plays a RAIN-pool sound (getBiome works on 2.3.0; weather read works)", p.sounds.length === 1 && p.sounds[0][0] === "pw:ambient.weather.rain1", p.sounds);
  ok("sound options unchanged (volume 0.6, pitch 0.95-1.05)", p.sounds[0][1].volume === 0.6 && p.sounds[0][1].pitch >= 0.95 && p.sounds[0][1].pitch <= 1.05);
  M.world.afterEvents.weatherChange.fire({ dimension: "overworld", newWeather: "Thunder", previousWeather: "Rain" });   // no namespace
  M._advance(40);
  ok("thunder (event dimension without 'minecraft:') -> pw:ar_sky_thunder", lastPush(p) === 'fog @s push "pw:ar_sky_thunder" ar_sky', lastPush(p));
  M._advance(160);   // tick 400
  ok("thunder -> ambient plays a STORM-pool sound", p.sounds.length === 2 && p.sounds[1][0] === "pw:ambient.weather.storm_close", p.sounds.map((s) => s[0]));
  M.world.afterEvents.weatherChange.fire({ dimension: "minecraft:overworld", newWeather: "Clear", previousWeather: "Thunder" });
  M._advance(200);   // tick 600
  ok("clear again -> day fog + a FOREST day-pool sound (the biome pool itself)",
     lastPush(p) === 'fog @s push "pw:ar_sky_day" ar_sky' && p.sounds.length === 3 && p.sounds[2][0] === "pw:ambient.bird.bird_ambience1", [lastPush(p), p.sounds.map((s) => s[0])]);
  M._state.timeOfDay = 18000; M._advance(40);
  ok("midnight clear -> pw:ar_sky_night", lastPush(p) === 'fog @s push "pw:ar_sky_night" ar_sky', lastPush(p));
  const n = new M.MockPlayer("Visitor", "minecraft:nether", "minecraft:nether_wastes"); M._state.players.push(n);
  M.world.afterEvents.weatherChange.fire({ dimension: "minecraft:overworld", newWeather: "Thunder", previousWeather: "Clear" });
  M._advance(40);
  ok("nether player -> pw:ar_sky_nether even while the overworld storms", lastPush(n) === 'fog @s push "pw:ar_sky_nether" ar_sky', lastPush(n));
  M._state.players.splice(1);
  M.world.afterEvents.weatherChange.fire({ dimension: "minecraft:overworld", newWeather: "Clear", previousWeather: "Thunder" });
  const f = new M.MockPlayer("NoFogs"); f.failPush = true; M._state.players.push(f);
  const t0 = M._state.tick; M._advance(600);
  const fw = warns.filter((w) => w.includes("fog push failed: pw:ar_sky_night"));
  ok("a failing fog push (fog id not defined by any pack) is logged ONCE to the content log", fw.length === 1, warns.filter((w) => w.includes("fog push failed")));
  ok("...and never becomes a retry storm: <= 3 push attempts in 600 ticks (same cadence as 1.3.34: change + 15 s re-assert)", pushes(f) <= 3 && pushes(f) >= 1, { pushes: pushes(f), from: t0 });
  M._state.players.splice(0);
  const hi = new M.MockPlayer("Flyer"); hi.location.y = 400; M._state.players.push(hi);
  let thrown = null; try { M._advance(200); } catch (e) { thrown = String(e); }
  ok("above the build limit (getBiome throws) the beat just skips — no error escapes", thrown === null && hi.sounds.length === 0, thrown);
  ok("version flag says v1.3.35", warns.some((w) => w.includes("[PW-VERSION] BP-01 Atmospheric Effects v1.3.35")), warns.filter((w) => w.includes("PW-VERSION")));
}

async function bp01Reload() {
  M._state.dyn.set("pw:weather_cache", '{"overworld":"Thunder"}');   // saved by a previous session
  const p = new M.MockPlayer("Abs0lum"); M._state.players.push(p);
  let err = null; try { await import("./bp01/main.js"); } catch (e) { err = String(e); }
  M._ready(); M._advance(40);
  ok("world reload while it storms: the saved weather is read lazily -> pw:ar_sky_thunder with no new event", err === null && lastPush(p) === 'fog @s push "pw:ar_sky_thunder" ar_sky', [err, p.cmds]);
}

async function weatherUnit() {
  const W = await import(`./${B02}/pw_weather.js`);
  let early = null; try { early = W.weatherIn("minecraft:overworld"); } catch (e) { early = "threw " + e; }
  ok("a read while scripts load does not throw and says Clear", early === "Clear", early);
  M._state.dyn.set("pw:weather_cache", '{"overworld":"Rain"}');
  M._ready();
  ok("...and the saved value is still loaded afterwards (the early failure did not mark it loaded)", W.weatherIn("minecraft:overworld") === "Rain", W.weatherIn("minecraft:overworld"));
  ok("normWeather: Rain/Thunder kept, anything else -> Clear", W.normWeather("Rain") === "Rain" && W.normWeather("Thunder") === "Thunder" && W.normWeather("Snow") === "Clear" && W.normWeather(undefined) === "Clear");
  ok("dimKey strips minecraft:", W.dimKey("minecraft:overworld") === "overworld" && W.dimKey("overworld") === "overworld");
  M.world.afterEvents.weatherChange.fire({ dimension: "minecraft:overworld", newWeather: "Thunder", previousWeather: "Rain" });
  ok("event -> weatherIn(Dimension object) and weatherIn(id) agree", W.weatherIn({ id: "minecraft:overworld" }) === "Thunder" && W.weatherIn("overworld") === "Thunder");
  ok("other dimensions stay Clear", W.weatherIn("minecraft:the_end") === "Clear" && W.weatherIn("minecraft:nether") === "Clear");
  ok("save is JSON of every known dimension", M._state.dyn.get("pw:weather_cache") === '{"overworld":"Thunder"}', M._state.dyn.get("pw:weather_cache"));
}

async function bp02() {
  const src = readFileSync(`./${B02}/main.js`, "utf8");
  const a = src.indexOf("function _leafWind("), b = src.indexOf("function _isLeafId(");
  const c = src.indexOf("const FIREFLY_AMBIENT_BIOMES");
  const d = src.indexOf("system.runInterval(() => {\n  try {\n    for (const p of world.getAllPlayers()) {\n      try { spawnAmbientFirefliesForPlayer(p); }");
  ok("slices found in the shipped main.js (_leafWind, firefly block)", a > 0 && b > a && c > 0 && d > c, { a, b, c, d });
  const hasW = /import \{ weatherIn \} from "\.\/pw_weather\.js"/.test(src);
  const h = `import { world, system } from "@minecraft/server";\n` + (hasW ? `import { weatherIn } from "./pw_weather.js";\n` : "") +
            src.slice(a, b) + "\n" + src.slice(c, d) + "\nexport { _leafWind, spawnAmbientFirefliesForPlayer };\n";
  writeFileSync(`./${B02}/harness.mjs`, h);
  const H = await import(`./${B02}/harness.mjs`);
  M._ready();
  const ow = new M.MockDimension("minecraft:overworld", "minecraft:forest");
  ok("leaf wind calm in clear weather (0.15)", H._leafWind(ow) === 0.15, H._leafWind(ow));
  M.world.afterEvents.weatherChange.fire({ dimension: "minecraft:overworld", newWeather: "Rain", previousWeather: "Clear" });
  ok("leaf wind 0.8 in RAIN", H._leafWind(ow) === 0.8, H._leafWind(ow));
  M.world.afterEvents.weatherChange.fire({ dimension: "minecraft:overworld", newWeather: "Thunder", previousWeather: "Rain" });
  ok("leaf wind 1.6 in THUNDER", H._leafWind(ow) === 1.6, H._leafWind(ow));
  ok("nether leaves stay calm while the overworld storms", H._leafWind(new M.MockDimension("minecraft:nether", "minecraft:nether_wastes")) === 0.15);
  M._state.timeOfDay = 18000;
  const run = (biome, y = 70) => { const p = new M.MockPlayer("P", "minecraft:overworld", biome); p.location.y = y; H.spawnAmbientFirefliesForPlayer(p); return p.dimension.particles.length; };
  ok("night, swamp -> 2 fireflies", run("minecraft:swamp") === 2);
  ok("night, mangrove_swamp -> 2 fireflies", run("minecraft:mangrove_swamp") === 2);
  ok("night, forest -> NONE (biome gate works on 2.3.0)", run("minecraft:forest") === 0, run("minecraft:forest"));
  let thrown = null; let n; try { n = run("minecraft:plains", 400); } catch (e) { thrown = String(e); }
  ok("above the build limit (getBiome throws) -> no fireflies, no error", thrown === null && n === 0, [thrown, n]);
  ok("...and afterwards the gate still holds: forest -> NONE, swamp -> 2 (it used to switch itself off)", run("minecraft:forest") === 0 && run("minecraft:swamp") === 2, [run("minecraft:forest"), run("minecraft:swamp")]);
  M._state.timeOfDay = 6000;
  ok("daytime swamp -> none (night only)", run("minecraft:swamp") === 0);
}

async function bp03() {
  const p = new M.MockPlayer("Abs0lum"); M._state.players.push(p);
  let err = null; try { await import("./bp03/main.js"); } catch (e) { err = String(e); }
  ok("BP-03 loads while scripts load", err === null, err);
  ok("subscribes playerBreakBlock, playerSpawn, scriptEventReceive once each", M.world.afterEvents.playerBreakBlock.count === 1 && M.world.afterEvents.playerSpawn.count === 1 && M.system.afterEvents.scriptEventReceive.count === 1);
  M._ready();
  const se = (id, message, src = p) => M.system.afterEvents.scriptEventReceive.fire({ id, message, sourceEntity: src, sourceType: src ? "Entity" : "Server" });
  const brk = () => M.world.afterEvents.playerBreakBlock.fire({ player: p, block: { x: 1, y: 2, z: 3, dimension: { id: "minecraft:overworld" } },
    brokenBlockPermutation: { type: { id: "minecraft:stone" }, getAllStates: () => ({ stone_type: "granite" }) } });
  brk();
  ok("default mode (brief): break -> '[BLOCK] stone @ 1, 2, 3'", strip(p.msgs.at(-1)) === "[BLOCK] stone @ 1, 2, 3", strip(p.msgs.at(-1)));
  se("pw:diag", "off");
  ok("/scriptevent pw:diag off -> mode off + confirmation", p.dyn.get("pw_diag_mode") === "off" && strip(p.msgs.at(-1)).includes("Diagnostics OFF"), strip(p.msgs.at(-1)));
  const before = p.msgs.length; brk();
  ok("mode off: breaking announces nothing", p.msgs.length === before);
  se("diag:verbose", "");
  ok("shortcut /scriptevent diag:verbose -> mode verbose", p.dyn.get("pw_diag_mode") === "verbose");
  brk(); const v = strip(p.msgs.at(-1));
  ok("verbose break: id, coords, dim, states, texture hint", v.includes("stone") && v.includes("@ 1, 2, 3") && v.includes("dim: overworld") && v.includes("states: stone_type=granite") && v.includes("textures/blocks/stone.png"), v);
  se("pw:diag", "STATUS");
  ok("status (any case) -> 'Current mode: verbose'", strip(p.msgs.at(-1)) === "Current mode: verbose", strip(p.msgs.at(-1)));
  se("pw:diag", "");
  ok("no verb -> help listing the /scriptevent forms", strip(p.msgs.at(-1)).includes("/scriptevent pw:diag on") && strip(p.msgs.at(-1)).includes("/scriptevent pw:diag verbose"));
  se("pw:diag", "bogus");
  ok("unknown verb -> hint", strip(p.msgs.at(-1)).startsWith("Unknown diag command"));
  const c0 = p.msgs.length;
  se("pw:diag_status", ""); se("civ:markers", "hide");
  ok("other packs' ids (BP-02 pw:diag_status, markers civ:*) are ignored", p.msgs.length === c0);
  se("pw:diag", "on", undefined);
  ok("from a command block (no player source) -> applies to the first player", p.dyn.get("pw_diag_mode") === "brief");
  M.world.afterEvents.playerSpawn.fire({ player: p, initialSpawn: true });
  ok("join greeting names /scriptevent pw:diag help", strip(p.msgs.at(-1)).includes("/scriptevent pw:diag help"));
  ok("version flag says v1.3.34", warns.some((w) => w.includes("[PW-VERSION] BP-03 Identification Diagnostics v1.3.34")));
}

const modes = { bp01, "bp01-reload": bp01Reload, weather: weatherUnit, bp02, bp03 };
if (!modes[mode]) { console.log("unknown mode " + mode); process.exit(2); }
await modes[mode]();
console.log(`${mode}: ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
