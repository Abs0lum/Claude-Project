// mock_mc2.mjs — a stand-in for @minecraft/server 2.3.0 + @minecraft/server-ui 2.0.0 covering what pw_testrunner.js touches.
// EARLY EXECUTION is modelled: until _ready() every world/player/dimension read or write throws (as in 2.x while
// scripts load); subscribing and scheduling are allowed. Registries (ItemTypes/BlockTypes/EntityTypes) are sets the
// test fills. Forms resolve from a scripted queue (_ui.queue).
export const _state = {
  ready: false, tick: 0, timeOfDay: 6000, day: 3, dyn: new Map(), players: [], intervals: [], timeouts: [], warns: [],
  weather: [], entities: [], particles: [], blocks: new Map(), rules: { doDayLightCycle: true, doWeatherCycle: true },
  items: new Set(), blockTypes: new Set(), entityTypes: new Set(), ents: [], teleports: [], effects: [], dims: new Map(),
};
function early(what) { if (!_state.ready) throw new Error(`early-execution: ${what} called while scripts load`); }
function signal(name) {
  const subs = [];
  return {
    subscribe(cb, opts) { subs.push({ cb, opts }); return cb; },
    unsubscribe(cb) { const i = subs.findIndex((s) => s.cb === cb); if (i >= 0) subs.splice(i, 1); },
    fire(ev) { for (const s of subs) { if (s.opts && s.opts.namespaces && typeof ev.id === "string" && !s.opts.namespaces.includes(ev.id.split(":")[0])) continue; s.cb(ev); } },
    get count() { return subs.length; }, name,
  };
}
export const WeatherType = { Clear: "Clear", Rain: "Rain", Thunder: "Thunder" };
export const GameMode = { Adventure: "Adventure", Creative: "Creative", Spectator: "Spectator", Survival: "Survival" };
export const ItemLockMode = { inventory: "inventory", none: "none", slot: "slot" };
export class ItemType { constructor(id) { this.id = id; } }
export class ItemStack {
  constructor(t, amount = 1) { this.typeId = typeof t === "string" ? t : t.id; this.amount = amount; this.nameTag = undefined; this.lockMode = "none"; this.keepOnDeath = false; }
}
export const ItemTypes = { get(id) { early("ItemTypes.get"); return _state.items.has(id) ? new ItemType(id) : undefined; } };
export const BlockTypes = { get(id) { early("BlockTypes.get"); return _state.blockTypes.has(id) ? { id } : undefined; } };
export const EntityTypes = { get(id) { early("EntityTypes.get"); return _state.entityTypes.has(id) ? { id } : undefined; } };
export const system = {
  get currentTick() { return _state.tick; },
  runInterval(cb, t = 1) { _state.intervals.push({ cb, t: Math.max(1, t) }); return _state.intervals.length; },
  runTimeout(cb, t = 1) { _state.timeouts.push({ cb, at: _state.tick + Math.max(1, t) }); return _state.timeouts.length; },
  run(cb) { _state.timeouts.push({ cb, at: _state.tick + 1 }); return _state.timeouts.length; },
  runJob(gen) { early("system.runJob"); (_state.jobs || (_state.jobs = [])).push(gen); return _state.jobs.length; },   // v0.4.6
  afterEvents: { scriptEventReceive: signal("scriptEventReceive") },
};
const rulesProxy = new Proxy(_state.rules, { get(t, k) { early("world.gameRules"); return t[k]; }, set(t, k, v) { early("world.gameRules"); t[k] = v; return true; } });
export const world = {
  afterEvents: { itemUse: signal("itemUse"), playerSpawn: signal("playerSpawn"), weatherChange: signal("weatherChange"), playerLeave: signal("playerLeave") },
  beforeEvents: {},
  get gameRules() { early("world.gameRules"); return rulesProxy; },
  getAllPlayers() { early("world.getAllPlayers"); return _state.players; },
  getTimeOfDay() { early("world.getTimeOfDay"); return _state.timeOfDay; },
  setTimeOfDay(t) { early("world.setTimeOfDay"); _state.timeOfDay = t; },
  getDay() { early("world.getDay"); return _state.day; },
  getDynamicProperty(k) { early("world.getDynamicProperty"); return _state.dyn.get(k); },
  setDynamicProperty(k, v) { early("world.setDynamicProperty"); if (v === undefined) _state.dyn.delete(k); else _state.dyn.set(k, v); },
  getDimension(id) { early("world.getDimension"); const d = _state.dims.get(id); if (!d) throw new Error(`unknown dimension ${id}`); return d; },
};
function key(l) { return `${Math.floor(l.x)},${Math.floor(l.y)},${Math.floor(l.z)}`; }
export class BlockPermutation {
  constructor(id, states = {}) { this.type = { id }; this.states = { ...states }; }
  getAllStates() { return { ...this.states }; }
  static resolve(id, states = {}) { early("BlockPermutation.resolve"); return new BlockPermutation(id, states); }
}
export class MockBlock {
  constructor(dim, loc) { this.dim = dim; this.loc = { x: Math.floor(loc.x), y: Math.floor(loc.y), z: Math.floor(loc.z) }; }
  get location() { return { ...this.loc }; }
  get typeId() { return _state.blocks.get(key(this.loc)) || (this.loc.y < 64 ? "minecraft:grass_block" : "minecraft:air"); }
  get isAir() { return this.typeId === "minecraft:air"; }
  get isLiquid() { return this.typeId === "minecraft:water"; }
  get permutation() { early("Block.permutation"); return new BlockPermutation(this.typeId, this.typeId === "minecraft:grass_block" ? { "dirt_type": "normal" } : {}); }
  setType(id) { early("Block.setType"); _state.blocks.set(key(this.loc), id); }
  setPermutation(p) { early("Block.setPermutation"); _state.blocks.set(key(this.loc), p.type.id); (_state.perms || (_state.perms = new Map())).set(key(this.loc), { ...p.states }); }
  // v0.4.1: a jukebox answers minecraft:record_player only when the test sets _state.recordPlayer (else undefined, as a missing component)
  getComponent(id) {
    early("Block.getComponent");
    if (id !== "minecraft:record_player" || !_state.recordPlayer || this.typeId !== "minecraft:jukebox") return undefined;
    const at = key(this.loc);
    return { setRecord(disc, play) { (_state.records || (_state.records = [])).push([at, typeof disc === "string" ? disc : disc.id, play]); } };
  }
}
export class MockEntity {
  constructor(id, loc, dim) { this.typeId = id; this.location = { ...loc }; this.dimension = dim; this.tags = new Set(); this.rotation = { x: 0, y: 0 }; this.events = []; this.valid = true; this.id = "ent-" + (_state.ents.length + 1); }
  get isValid() { return this.valid; }
  playAnimation(id, o) { early("Entity.playAnimation"); (this.played = this.played || []).push(id); }   // v0.5.8 (p21)
  addTag(t) { early("Entity.addTag"); this.tags.add(t); return true; }
  hasTag(t) { early("Entity.hasTag"); return this.tags.has(t); }
  getTags() { early("Entity.getTags"); return [...this.tags]; }
  remove() { early("Entity.remove"); this.valid = false; const i = _state.ents.indexOf(this); if (i >= 0) _state.ents.splice(i, 1); }
  teleport(loc, opts) { early("Entity.teleport"); this.location = { ...loc }; if (opts && opts.rotation) this.rotation = { ...opts.rotation }; _state.teleports.push([this.typeId, { ...loc }, opts]); }
  setRotation(r) { early("Entity.setRotation"); this.rotation = { ...r }; }
  getRotation() { early("Entity.getRotation"); return { ...this.rotation }; }
  triggerEvent(ev) {
    early("Entity.triggerEvent");
    if (ev === "minecraft:ageable_grow_up" && _state.noGrowUp && _state.noGrowUp.has(this.typeId)) throw new Error("InvalidArgumentError: Invalid value passed to argument [0]");
    if (ev === "minecraft:as_adult" && !(_state.zombieFamily && _state.zombieFamily.has(this.typeId))) throw new Error("InvalidArgumentError: Invalid value passed to argument [0]");
    this.events.push(ev);
    if (ev === "minecraft:ageable_grow_up" || ev === "minecraft:as_adult") this.baby = false;
  }
  setProperty(k, v) { early("Entity.setProperty"); this.props = { ...(this.props || {}), [k]: v }; }
  hasComponent(id) { early("Entity.hasComponent"); return id === "minecraft:is_baby" ? !!this.baby : false; }
  getComponent(id) { early("Entity.getComponent"); return id === "minecraft:variant" && this.variant !== undefined ? { value: this.variant } : undefined; }   // v0.4.1
  clearVelocity() { early("Entity.clearVelocity"); }
  addEffect(id, d, o) { early("Entity.addEffect"); _state.effects.push([this.typeId, id, d, o]); }
  runCommand(c) { early("Entity.runCommand"); (this.cmds || (this.cmds = [])).push(c);   // v0.3.7 (rig items)
    // v0.4.3: replaceitem mainhand fills this.mainhand unless the test lists the mob in _state.noHold (the game drops it);
    // testfor @s[hasitem={item=X,location=slot.weapon.mainhand}] answers from it; _state.testforThrows makes the check error
    let m = /^replaceitem entity @s slot\.weapon\.mainhand 0 (\S+)$/.exec(c);
    if (m) { if (!(_state.noHold && _state.noHold.has(this.typeId))) this.mainhand = m[1].replace("minecraft:", ""); return { successCount: 1 }; }
    m = /^testfor @s\[hasitem=\{item=([^,}]+),location=slot\.weapon\.mainhand\}\]$/.exec(c);
    if (m) { if (_state.testforThrows) throw new Error("CommandError: Syntax error: Unexpected \"hasitem\""); return { successCount: this.mainhand === m[1].replace("minecraft:", "") ? 1 : 0 }; }
    return { successCount: 1 }; }
}
export class MockDimension {
  constructor(id = "minecraft:overworld", biome = "minecraft:forest") { this.id = id; this.biome = biome; }
  getBiome(loc) { early("Dimension.getBiome"); if (loc.y > 320 || loc.y < -64) throw new Error("LocationOutOfWorldBoundariesError"); return { id: this.biome }; }
  setWeather(t, d) { early("Dimension.setWeather"); _state.weather.push([t, d]); }
  spawnEntity(id, loc) { early("Dimension.spawnEntity"); if (!_state.entityTypes.has(id)) throw new Error(`unknown entity ${id}`); _state.entities.push([id, { ...loc }]); const e = new MockEntity(id, loc, this); if (_state.babySpawn && _state.babySpawn.has(id)) e.baby = true;
    // v0.4.1: the first N spawns of an id come out as babies (_state.babyFirst), a variant is rolled per spawn (_state.variants: id -> count)
    if (_state.babyFirst && _state.babyFirst.get(id) > 0) { e.baby = true; _state.babyFirst.set(id, _state.babyFirst.get(id) - 1); }
    if (_state.variants && _state.variants.has(id)) { _state.seed = ((_state.seed ?? 12345) * 16807) % 2147483647; e.variant = Math.floor(_state.seed / 2147483647 * _state.variants.get(id)); }   // Park-Miller
    _state.ents.push(e); return e; }
  getEntities(q = {}) { early("Dimension.getEntities"); return _state.ents.filter((e) => e.valid && e.dimension.id === this.id && (!q.tags || q.tags.every((t) => e.tags.has(t))) && (!q.type || e.typeId === q.type)); }
  spawnParticle(id, loc) { early("Dimension.spawnParticle"); _state.particles.push([id, { ...loc }]); }
  // v0.5.0: Dimension.placeFeature (API); _state.noApiPlace makes it throw (the command path is then tried), _state.noPlace refuses both
  placeFeature(id, loc, shouldThrow) { early("Dimension.placeFeature");
    if (_state.noApiPlace || _state.noPlace) { if (shouldThrow) throw new Error(`PlaceFeatureError: could not place ${id}`); return false; }
    const r = this.runCommand(`place feature ${id} ${Math.floor(loc.x)} ${Math.floor(loc.y)} ${Math.floor(loc.z)}`);
    _state.placeWays[_state.placeWays.length - 1] = "api"; return r.successCount > 0; }
  getBlock(loc) { early("Dimension.getBlock"); if (_state.unloaded && _state.unloaded(loc)) return undefined; return new MockBlock(this, loc); }   // v0.4.9: unloaded chunks
  // v0.4.6: fill (air / grass_block, block-by-block), tickingarea (logged), place feature -> a small tree whose leaf id follows the feature
  // (BP-02 grows pw: trees; azalea is vanilla and mixes plain + flowered leaves); _state.noPlace makes /place fail (stand-in path)
  runCommand(c) {
    early("Dimension.runCommand"); (_state.dimCmds || (_state.dimCmds = [])).push(c);
    let m = /^fill (-?\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) (\S+)$/.exec(c);
    if (m) { const [x1, y1, z1, x2, y2, z2] = m.slice(1, 7).map(Number); const id = m[7].includes(":") ? m[7] : "minecraft:" + m[7];
      const vol = (Math.abs(x2 - x1) + 1) * (Math.abs(y2 - y1) + 1) * (Math.abs(z2 - z1) + 1); _state.maxFill = Math.max(_state.maxFill || 0, vol);
      if (vol > 32768) throw new Error(`CommandError: too many blocks in the specified area (${vol} > 32768)`);
      for (let x = Math.min(x1, x2); x <= Math.max(x1, x2); x++) for (let y = Math.min(y1, y2); y <= Math.max(y1, y2); y++) for (let z = Math.min(z1, z2); z <= Math.max(z1, z2); z++) {
        const k = `${x},${y},${z}`; if (id === "minecraft:air") { if (_state.blocks.has(k)) _state.blocks.delete(k); } else _state.blocks.set(k, id); }
      return { successCount: 1 }; }
    m = /^place feature (\S+) (-?\d+) (-?\d+) (-?\d+)$/.exec(c);
    if (m) { if (_state.noPlace) throw new Error("CommandError: unknown feature");
      (_state.placeWays || (_state.placeWays = [])).push("cmd");
      // v0.4.8: BP-02 ids pw:<wood>_<age>_tree_feature / pw:<wood>_elder_tree_feature_v2 (trunk pw:<wood>_<age>, elders 2x2) and the
      // vanilla-id overrides; every placement rolls its own crown (a counter), so only /clone makes two trees identical
      const f = m[1].replace(/^(minecraft|pw):/, "").replace(/_tree_feature(_v2)?$/, ""); const [x, y, z] = m.slice(2).map(Number);
      const am = /^([a-z_]+?)_(young|mature|old|elder)$/.exec(f); const sp = am ? am[1] : f; const age = am ? am[2] : "";
      _state.placedFeatures = (_state.placedFeatures || []).concat([m[1]]);
      const leaf = sp === "azalea" ? "minecraft:azalea_leaves" : `pw:${sp}_leaves`;
      const logId = sp === "azalea" ? "minecraft:oak_log" : (["acacia", "mangrove", "cherry"].includes(sp) ? `minecraft:${sp}_log` : `pw:${sp}_${age || "young"}`);
      const wide = age === "elder" ? 2 : 1; const H = { young: 5, mature: 7, old: 9, elder: 12 }[age] || 5; const R = age === "elder" ? 4 : 2;
      const roll = (_state.treeRoll = (_state.treeRoll || 0) + 1);
      for (let h = 0; h < H; h++) for (let a = 0; a < wide; a++) for (let b = 0; b < wide; b++) _state.blocks.set(`${x + a},${y + h},${z + b}`, logId);
      if (age === "elder") {                                                       // v0.4.9: a DIAGONAL branch (edge-connected only, like fancy_trunk)
        for (let d = 1; d <= 4; d++) _state.blocks.set(`${x + 1 + d},${y + H - 8 + d},${z - d}`, logId);
        for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) { const k = `${x + 7 + a},${y + H - 3},${z - 5 + b}`; if (!_state.blocks.has(k)) _state.blocks.set(k, leaf); } }
      if (_state.bigTree) _state.blocks.set(`${x + 8},${y + H},${z}`, leaf);         // v0.4.9: a leaf on the r8 rim (EDGE)
      for (let dx = -R; dx <= R + wide - 1; dx++) for (let dy = H - 2; dy <= H + 1; dy++) for (let dz = -R; dz <= R + wide - 1; dz++) {
        if (dx >= 0 && dx < wide && dz >= 0 && dz < wide && dy < H) continue; if (Math.abs(dx) + Math.abs(dz) > R + wide) continue;
        if (((dx * 7 + dy * 13 + dz * 5 + roll * 11) % 9 + 9) % 9 === 0) continue;                                  // this tree's own gaps
        const k = `${x + dx},${y + dy},${z + dz}`; if (_state.blocks.get(k) === logId) continue;
        _state.blocks.set(k, sp === "azalea" && (dx + dz) % 2 ? "minecraft:azalea_leaves_flowered" : leaf); }
      return { successCount: 1 }; }
    // v0.4.8: clone (replace mode: air copies too) with block states; the game caps fill / clone at 32,768 blocks
    m = /^clone (-?\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+)$/.exec(c);
    if (m) { const [x1, y1, z1, x2, y2, z2, tx, ty, tz] = m.slice(1).map(Number);
      const vol = (Math.abs(x2 - x1) + 1) * (Math.abs(y2 - y1) + 1) * (Math.abs(z2 - z1) + 1);
      if (vol > 32768) throw new Error(`CommandError: too many blocks in the specified area (${vol} > 32768)`);
      if (_state.noClone) throw new Error("CommandError: clone refused");
      const cp = []; const perms = _state.perms || (_state.perms = new Map());
      for (let x = Math.min(x1, x2); x <= Math.max(x1, x2); x++) for (let y = Math.min(y1, y2); y <= Math.max(y1, y2); y++) for (let z = Math.min(z1, z2); z <= Math.max(z1, z2); z++) {
        const k = `${x},${y},${z}`; cp.push([`${tx + x - Math.min(x1, x2)},${ty + y - Math.min(y1, y2)},${tz + z - Math.min(z1, z2)}`, _state.blocks.get(k), perms.get(k)]); }
      for (const [k, id, st] of cp) { if (id === undefined) _state.blocks.delete(k); else _state.blocks.set(k, id); if (st) perms.set(k, { ...st }); else perms.delete(k); }
      _state.clones = (_state.clones || 0) + 1; return { successCount: vol }; }
    return { successCount: 1 };
  }
}
export class MockContainer {
  constructor(n = 36) { this.size = n; this.slots = new Array(n).fill(undefined); }
  getItem(i) { early("Container.getItem"); return this.slots[i]; }
  setItem(i, s) { early("Container.setItem"); this.slots[i] = s; }
  addItem(s) { early("Container.addItem"); const i = this.slots.findIndex((x) => x === undefined); if (i < 0) return s; this.slots[i] = s; return undefined; }
  count(pred) { return this.slots.filter((s) => s && pred(s)).length; }
}
export class MockPlayer {
  constructor(name, biome = "minecraft:forest") {
    this.typeId = "minecraft:player"; this.id = "id-" + name; this.name = name; this.location = { x: 10.5, y: 70, z: 20.5 };
    this.dimension = new MockDimension("minecraft:overworld", biome); _state.dims.set(this.dimension.id, this.dimension); this.gameMode = "Creative"; this.view = { x: 0, y: 0, z: 1 }; this.rotation = { x: 0, y: 180 };
    this.cmds = []; this.sounds = []; this.msgs = []; this.titles = []; this.bars = []; this.inv = new MockContainer(36); this.failCmds = false;
    this.onScreenDisplay = {
      setTitle: (t, o) => { early("onScreenDisplay.setTitle"); this.titles.push([t, o]); },
      setActionBar: (t) => { early("onScreenDisplay.setActionBar"); this.bars.push(t); },
    };
  }
  getViewDirection() { early("Entity.getViewDirection"); return this.view; }
  getRotation() { early("Entity.getRotation"); return { ...this.rotation }; }
  getGameMode() { early("Player.getGameMode"); return this.gameMode; }
  runCommand(c) {
    early("Entity.runCommand"); this.cmds.push(c);
    if (this.failCmds) throw new Error("CommandError");
    // Bedrock block-state syntax: ["name"=value, ...] — the ":" form fails to parse (the v0.3.0 bug, witnessed 09-28)
    for (const m of String(c).matchAll(/\[([^\]]*)\]/g)) {
      for (const pair of m[1].split(",")) {
        if (!/^\s*"[^"]+"\s*=\s*("[^"]*"|true|false|-?\d+)\s*$/.test(pair)) { _state.cmdErrors = (_state.cmdErrors || 0) + 1; throw new Error(`CommandError: Error occurred with parsing block states: ${pair}`); }
      }
    }
    return { successCount: 1 };
  }
  sendMessage(m) { early("Player.sendMessage"); this.msgs.push(Array.isArray(m) ? m.join("") : String(m)); }
  playSound(id) { early("Player.playSound"); this.sounds.push(id); }
  getComponent(id) { early("Entity.getComponent"); if (id === "minecraft:inventory") return { container: this.inv }; return undefined; }
}
export function _ready() { _state.ready = true; }
export function _advance(n) {
  for (let i = 0; i < n; i++) {
    _state.tick++;
    for (const iv of _state.intervals) if (_state.tick % iv.t === 0) iv.cb();
    const due = _state.timeouts.filter((t) => t.at <= _state.tick); _state.timeouts = _state.timeouts.filter((t) => t.at > _state.tick);
    for (const t of due) t.cb();
    for (const g of [...(_state.jobs || [])]) { for (let k = 0; k < 40; k++) { const r = g.next(); if (r.done) { _state.jobs = _state.jobs.filter((x) => x !== g); break; } } }
  }
}
// ---------------------------------------------------------------- @minecraft/server-ui
export const _ui = { queue: [], shown: [] };
class FormBase {
  constructor(kind) { this.kind = kind; this.parts = []; }
  title(t) { this.parts.push(["title", t]); return this; }
  body(t) { this.parts.push(["body", t]); return this; }
  button(t) { this.parts.push(["button", t]); return this; }
  label(t) { this.parts.push(["label", t]); return this; }
  textField(l, p, o) { this.parts.push(["textField", l, p, o]); return this; }
  submitButton(t) { this.parts.push(["submit", t]); return this; }
  show(player) {
    early("FormData.show");
    _ui.shown.push({ kind: this.kind, parts: this.parts, player });
    const r = _ui.queue.length ? _ui.queue.shift() : { canceled: true, cancelationReason: "UserClosed" };
    return Promise.resolve(r);
  }
}
export class ActionFormData extends FormBase { constructor() { super("action"); } }
export class ModalFormData extends FormBase { constructor() { super("modal"); } }
export class MessageFormData extends FormBase { constructor() { super("message"); } }
