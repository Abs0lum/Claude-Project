// mock_mc.mjs — a small stand-in for @minecraft/server 2.x, for mock-running BP-01, BP-03 and pw_weather.js in
// node.  It models the parts those scripts touch, plus EARLY EXECUTION: until _ready() is called, every
// world/dimension/player read or write throws (as in 2.x while scripts load); subscribing and scheduling
// are allowed.  Player has runCommand (2.x) and deliberately NO runCommandAsync (removed in 2.0.0).
export const _state = { ready: false, tick: 0, timeOfDay: 6000, dyn: new Map(), players: [], intervals: [], queue: [], warns: [] };
function early(what) { if (!_state.ready) throw new Error(`early-execution: ${what} called while scripts load`); }
function signal(name) {
  const subs = [];
  return {
    subscribe(cb, opts) { subs.push({ cb, opts }); return cb; },
    unsubscribe(cb) { const i = subs.findIndex((s) => s.cb === cb); if (i >= 0) subs.splice(i, 1); },
    fire(ev) {
      for (const s of subs) {
        if (s.opts && s.opts.namespaces && typeof ev.id === "string" && !s.opts.namespaces.includes(ev.id.split(":")[0])) continue;
        s.cb(ev);
      }
    },
    get count() { return subs.length; },
    name,
  };
}
export const WeatherType = { Clear: "Clear", Rain: "Rain", Thunder: "Thunder" };
export const system = {
  get currentTick() { return _state.tick; },
  runInterval(cb, t = 1) { _state.intervals.push({ cb, t: Math.max(1, t) }); return _state.intervals.length; },
  run(cb) { _state.queue.push(cb); return _state.queue.length; },
  afterEvents: { scriptEventReceive: signal("scriptEventReceive") },
};
export const world = {
  afterEvents: { weatherChange: signal("weatherChange"), playerLeave: signal("playerLeave"), playerSpawn: signal("playerSpawn"), playerBreakBlock: signal("playerBreakBlock") },
  beforeEvents: {},   // the STABLE shape: no chatSend
  getAllPlayers() { early("world.getAllPlayers"); return _state.players; },
  getTimeOfDay() { early("world.getTimeOfDay"); return _state.timeOfDay; },
  getDynamicProperty(k) { early("world.getDynamicProperty"); return _state.dyn.get(k); },
  setDynamicProperty(k, v) { early("world.setDynamicProperty"); if (v === undefined) _state.dyn.delete(k); else _state.dyn.set(k, v); },
};
export class MockDimension {
  constructor(id, biome) { this.id = id; this.biome = biome; this.particles = []; }
  getBiome(loc) {
    early("Dimension.getBiome");
    if (loc.y > 320 || loc.y < -64) throw new Error("LocationOutOfWorldBoundariesError");
    return { id: this.biome };
  }
  spawnParticle(id, loc) { early("Dimension.spawnParticle"); this.particles.push([id, loc]); }
}
export class MockPlayer {
  constructor(name, dimId = "minecraft:overworld", biome = "minecraft:forest") {
    this.typeId = "minecraft:player"; this.id = "id-" + name; this.name = name;
    this.location = { x: 0.5, y: 70, z: 0.5 }; this.dimension = new MockDimension(dimId, biome);
    this.cmds = []; this.sounds = []; this.msgs = []; this.dyn = new Map(); this.failPush = false;
  }
  runCommand(cmd) {
    early("Entity.runCommand"); this.cmds.push(cmd);
    if (this.failPush && / push /.test(cmd)) throw new Error("CommandError: fog definition not found");
    return { successCount: 1 };
  }
  playSound(id, opts) { early("Player.playSound"); this.sounds.push([id, opts]); }
  sendMessage(m) { early("Player.sendMessage"); this.msgs.push(Array.isArray(m) ? m.join("") : String(m)); }
  getDynamicProperty(k) { early("Entity.getDynamicProperty"); return this.dyn.get(k); }
  setDynamicProperty(k, v) { early("Entity.setDynamicProperty"); this.dyn.set(k, v); }
}
export function _ready() { _state.ready = true; }
export function _advance(n) {
  for (let i = 0; i < n; i++) {
    _state.tick++;
    for (const iv of _state.intervals) if (_state.tick % iv.t === 0) iv.cb();
    const q = _state.queue.splice(0); for (const cb of q) cb();
  }
}
