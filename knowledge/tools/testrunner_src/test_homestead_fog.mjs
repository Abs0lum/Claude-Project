// test_homestead_fog.mjs — mock-runs the SHIPPED BP-02 pw_homestead.js (v1.3.187) fog behaviour: stuck-fog sweep at boot and on
// join, room fog push OFF, pop -> remove.  Usage: node test_homestead_fog.mjs <bp02 scripts dir>
import fs from "node:fs"; import path from "node:path"; import os from "node:os"; import { pathToFileURL } from "node:url";
const SRC = path.resolve(process.argv[2]); const HERE = path.dirname(new URL(import.meta.url).pathname);
const td = fs.mkdtempSync(path.join(os.tmpdir(), "pwfog-"));
fs.writeFileSync(path.join(td, "package.json"), JSON.stringify({ type: "module" }));
// the mock: mock_mc2 + the names pw_homestead.js imports and the calls it makes at boot
fs.writeFileSync(path.join(td, "mock_homestead.mjs"), `
export * from ${JSON.stringify(pathToFileURL(path.join(HERE, "mock_mc2.mjs")).href)};
import { world, system, _state, MockDimension, MockPlayer } from ${JSON.stringify(pathToFileURL(path.join(HERE, "mock_mc2.mjs")).href)};
function signal() { const subs = []; return { subscribe(cb) { subs.push(cb); return cb; }, unsubscribe() {}, fire(ev) { for (const cb of subs) cb(ev); } }; }
export class BlockVolume { constructor(a, b) { this.a = a; this.b = b; } }
export const EquipmentSlot = { Mainhand: "Mainhand" };
export const EntityDamageCause = { suffocation: "suffocation", fireTick: "fireTick" };
world.beforeEvents.playerInteractWithBlock = signal();
world.afterEvents.playerBreakBlock = signal(); world.afterEvents.playerPlaceBlock = signal();
system.beforeEvents = { startup: signal() };
world.getDynamicPropertyIds = () => { if (!_state.ready) throw new Error("early"); return [..._state.dyn.keys()]; };
const dims = new Map();
world.getDimension = (id) => { if (!dims.has(id)) dims.set(id, new MockDimension(id)); return dims.get(id); };
MockDimension.prototype.getPlayers = function () { return _state.players; };
MockPlayer.prototype.getHeadLocation = function () { return { x: this.location.x, y: this.location.y + 1.6, z: this.location.z }; };
MockPlayer.prototype.addEffect = function () {}; MockPlayer.prototype.applyDamage = function () {};
`);
for (const mod of ["@minecraft/server"]) {
  const d = path.join(td, "node_modules", mod); fs.mkdirSync(d, { recursive: true });
  fs.writeFileSync(path.join(d, "package.json"), JSON.stringify({ name: mod, type: "module", main: "index.js" }));
  fs.writeFileSync(path.join(d, "index.js"), `export * from ${JSON.stringify(pathToFileURL(path.join(td, "mock_homestead.mjs")).href)};`);
}
for (const f of ["pw_homestead.js", "pw_homestead_logic.js", "pw_homestead_materials.js"]) fs.copyFileSync(path.join(SRC, f), path.join(td, f));

const M = await import(pathToFileURL(path.join(td, "mock_homestead.mjs")).href);
const { _state, _ready, _advance, world, MockPlayer } = M;
const warns = []; const ow = console.warn; console.warn = (m) => warns.push(String(m));
let pass = 0, fail = 0; const check = (n, ok, d = "") => { ok ? pass++ : fail++; console.log(`${ok ? "PASS" : "FAIL"} ${n}${d ? " — " + d : ""}`); };

const H = await import(pathToFileURL(path.join(td, "pw_homestead.js")).href);
check("1 module loads in early execution (subscribes + schedules only)", true);
_ready();
const p = new MockPlayer("Abs0lum"); _state.players.push(p);
_advance(2);                                                     // the boot system.run fires
check("2 boot sweep removes pw_hearth_smoke for every online player", p.cmds.includes("fog @s remove pw_hearth_smoke"), JSON.stringify(p.cmds));
check("2b boot log says sweep + room fog OFF", warns.some((w) => /stuck-fog sweep( \(since v[0-9.]+\))? at boot: 1 player\(s\); room fog push OFF/.test(w)), warns.filter((w) => w.includes("sweep")).join(" | "));
check("2c HOMESTEAD runtime up line unchanged", warns.some((w) => w.includes("HOMESTEAD runtime up (cycle 40t, puff 4t, chute 1t, rafters 10t)")));
const before = p.cmds.length;
world.afterEvents.playerSpawn.fire({ initialSpawn: true, player: p }); _advance(25);
check("3 join sweep 20 ticks after an initial spawn", p.cmds.slice(before).includes("fog @s remove pw_hearth_smoke") && warns.some((w) => w.includes("stuck-fog sweep on join: Abs0lum")));
world.afterEvents.playerSpawn.fire({ initialSpawn: false, player: p }); _advance(25);
check("3b a respawn (not initial) does not sweep", p.cmds.length === before + 1);
const b2 = p.cmds.length;
H.fogPush(p, "minecraft:overworld|1,2,3");
check("4 fogPush is a no-op while ROOM_FOG is off (no push command, nothing remembered)", p.cmds.length === b2 && H._fogged().size === 0);
H._fogged().set(p.id, "k"); H.fogPop(p);
check("5 fogPop uses remove and forgets", p.cmds.at(-1) === "fog @s remove pw_hearth_smoke" && H._fogged().size === 0);
p.failCmds = true; H.fogClear(p); p.failCmds = false;
check("6 a failing remove (nothing on the stack) is swallowed", true);
_advance(120);
check("7 the cycles run with an empty ledger without throwing", true);
check("8 every log line carries the [pw_homestead] tag", warns.every((w) => w.startsWith("[pw_homestead]")), warns.find((w) => !w.startsWith("[pw_homestead]")));
console.warn = ow;
console.log(`\n${pass} passed, ${fail} failed`); fs.rmSync(td, { recursive: true, force: true }); process.exit(fail ? 1 : 0);
