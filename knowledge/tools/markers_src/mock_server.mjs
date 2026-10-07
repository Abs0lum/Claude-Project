// mock_server.mjs — a minimal @minecraft/server 2.0.0 stand-in for gate mock-runs of pw_markers.js.
// Entities apply their own data-driven events (add/remove component groups, set_property, first_valid with
// bool_property filters) from the BP entity JSON the gate passes in via globalThis.__ENTITY_DEFS.
export const Direction = { Up: "Up", Down: "Down", North: "North", South: "South", East: "East", West: "West" };
export const GameMode = { Creative: "Creative", Survival: "Survival", Adventure: "Adventure", Spectator: "Spectator" };
export class ItemStack { constructor(typeId, amount = 1) { this.typeId = typeId; this.amount = amount; } }
export class BlockVolume { constructor(from, to) { this.from = from; this.to = to; } }
function signal() { const subs = []; return { subs, subscribe: (f) => { subs.push(f); return f; }, fire(ev) { for (const f of subs) f(ev); } }; }
export const _log = [];
let tick = 1000;
export const system = {
  get currentTick() { return tick; }, _advance(n) { tick += n; },
  run: (f) => { f(); return 1; }, runTimeout: (f) => { f(); return 1; }, runInterval: () => 1,
  afterEvents: { scriptEventReceive: signal() }, beforeEvents: { startup: signal() },
};
const worldProps = new Map();
export const world = {
  beforeEvents: { playerInteractWithBlock: signal() },
  afterEvents: { playerPlaceBlock: signal(), playerBreakBlock: signal(), entityHitEntity: signal(), dataDrivenEntityTrigger: signal(), entityLoad: signal(), entitySpawn: signal() },
  sendMessage: (m) => _log.push(String(m)),
  getDynamicProperty: (k) => worldProps.get(k), setDynamicProperty: (k, v) => { if (v === undefined) worldProps.delete(k); else worldProps.set(k, v); },
  getDimension: (id) => { if (id !== "overworld") throw new Error("no dim"); return OVERWORLD; },
  getAllPlayers: () => PLAYERS,
};
export const PLAYERS = [];
// ---- blocks
export class Perm { constructor(id, states = {}) { this.typeId = id; this.states = states; this.type = { id }; } getState(k) { return this.states[k]; } }
export class Block {
  constructor(dim, loc, id, states) { this.dimension = dim; this.location = { ...loc }; this.x = loc.x; this.y = loc.y; this.z = loc.z; this.permutation = new Perm(id, states); }
  get typeId() { return this.permutation.typeId; } get isAir() { return this.typeId === "minecraft:air"; }
  setType(id) { this.permutation = new Perm(id, {}); } setPermutation(p) { this.permutation = p; }
}
// ---- entities
let eid = 0;
export class Entity {
  constructor(dim, typeId, loc) {
    this.id = String(++eid); this.dimension = dim; this.typeId = typeId; this.location = { ...loc }; this.isValid = true;
    this.tags = new Set(); this.groups = new Set(); this.rotation = { x: 0, y: 37 };  // spawn yaw is NOT 0 until set
    const def = (globalThis.__ENTITY_DEFS || {})[typeId]; this.def = def;
    this.props = {}; if (def) for (const [k, p] of Object.entries(def.description.properties || {})) this.props[k] = p.default;
  }
  getProperty(k) { return this.props[k]; }
  setProperty(k, v) { if (!(k in this.props)) throw new Error("unknown property " + k); this.props[k] = v; }
  addTag(t) { this.tags.add(t); return true; } hasTag(t) { return this.tags.has(t); } getTags() { return [...this.tags]; }
  setRotation(r) { this.rotation = { ...r }; } getRotation() { return this.rotation; }
  remove() { this.isValid = false; this.dimension._entities.delete(this); }
  triggerEvent(name) {
    const ev = this.def && this.def.events[name]; if (!ev) throw new Error("no event " + name);
    const apply = (a) => {
      for (const g of (a.add && a.add.component_groups) || []) this.groups.add(g);
      for (const g of (a.remove && a.remove.component_groups) || []) this.groups.delete(g);
      for (const [k, v] of Object.entries(a.set_property || {})) this.props[k] = v;
    };
    const pass = (f) => {
      if (!f) return true;
      if (f.test === "bool_property") { const v = !!this.props[f.domain]; const want = f.value === undefined ? true : f.value; return f.operator === "!=" ? v !== want : v === want; }
      if (f.test === "is_family") return true;
      throw new Error("filter not emulated: " + JSON.stringify(f));
    };
    if (ev.first_valid) { for (const a of ev.first_valid) if (pass(a.filters)) { apply(a); break; } }
    else if (ev.sequence) { for (const a of ev.sequence) if (pass(a.filters)) apply(a); }
    else apply(ev);
    world.afterEvents.dataDrivenEntityTrigger.fire({ entity: this, eventId: name, getModifiers: () => [] });
  }
  getComponent(n) { return this._components && this._components[n]; }
}
export class Player extends Entity {
  constructor(dim, name, loc) { super(dim, "minecraft:player", loc); this.name = name; this.isSneaking = false; this.mode = GameMode.Creative; this.selectedSlotIndex = 0; this.bar = [];
    this.dprops = new Map(); const items = []; this._components = { "minecraft:inventory": { container: {
      items, getItem: (s) => items[s], setItem: (s, it) => { items[s] = it; }, addItem: (it) => { items.push(it); return undefined; } } } };
    this.onScreenDisplay = { setActionBar: (m) => this.bar.push(m) }; }
  getGameMode() { return this.mode; }
  getDynamicProperty(k) { return this.dprops.get(k); } setDynamicProperty(k, v) { if (v === undefined) this.dprops.delete(k); else this.dprops.set(k, v); }
}
// ---- dimension
class Dimension {
  constructor(id) { this.id = id; this._blocks = new Map(); this._entities = new Set(); this.heightRange = { min: -64, max: 320 }; this.sounds = []; }
  key(l) { return `${Math.floor(l.x)},${Math.floor(l.y)},${Math.floor(l.z)}`; }
  setBlock(l, id, states) { const b = new Block(this, { x: Math.floor(l.x), y: Math.floor(l.y), z: Math.floor(l.z) }, id, states); this._blocks.set(this.key(l), b); return b; }
  getBlock(l) { return this._blocks.get(this.key(l)) || this.setBlock(l, "minecraft:air"); }
  getBlocks(vol, filter) {
    const out = [];
    for (const b of this._blocks.values()) {
      if (b.x < vol.from.x || b.x > vol.to.x || b.y < vol.from.y || b.y > vol.to.y || b.z < vol.from.z || b.z > vol.to.z) continue;
      if (filter.includeTypes && !filter.includeTypes.includes(b.typeId)) continue; out.push({ x: b.x, y: b.y, z: b.z });
    }
    return { getBlockLocationIterator: () => out[Symbol.iterator]() };
  }
  spawnEntity(typeId, loc) { const e = new Entity(this, typeId, loc); this._entities.add(e); if (e.def && e.def.events["minecraft:entity_spawned"]) e.triggerEvent("minecraft:entity_spawned"); world.afterEvents.entitySpawn.fire({ entity: e, cause: "Spawned" }); return e; }
  spawnItem(it, loc) { return null; }
  addPlayer(p) { this._entities.add(p); PLAYERS.push(p); }
  getEntities(o = {}) {
    return [...this._entities].filter((e) => {
      if (o.type && e.typeId !== o.type) return false;
      if (o.location && o.maxDistance !== undefined) { const d = Math.hypot(e.location.x - o.location.x, e.location.y - o.location.y, e.location.z - o.location.z); if (d > o.maxDistance) return false; }
      return true;
    });
  }
  getEntitiesAtBlockLocation(l) { const k = this.key(l); return [...this._entities].filter((e) => this.key(e.location) === k); }
  getPlayers() { return PLAYERS; }
  playSound(id, loc) { this.sounds.push(id); }
}
export const OVERWORLD = new Dimension("overworld");
