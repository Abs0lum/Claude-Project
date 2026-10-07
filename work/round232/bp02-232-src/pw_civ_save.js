// pw_civ_save.js — CIVITAS SECTIONED SAVES (1.3.228 B2 / BF2). PURE: no engine import — the store is passed in (the clock
// passes `world`; the node tests pass a Map-backed fake), so the same code runs live and in tests/test_save.mjs.
//
// Before 1.3.228 the whole town was ONE JSON (pw:civ_clock, 30,000-char chunks) rewritten whole on every save: gate 226-2
// measured 18..23 MB of dynamic-property writes a minute at 150 buildings. Now the state is cut into SECTIONS and a save
// writes only the sections whose text changed since the last write — all in ONE tick (the heartbeat's save slot), the
// index LAST:
//   pw:civ:meta                  every top-level field except buildings / settlements, + the settlement order + the
//                                building order (run-length: which section each position comes from)
//   pw:civ:b:<stId>              that settlement's buildings ("_" = buildings of no settlement: the plot tool)
//   pw:civ:st:<stId>:core        the settlement's scalars and small fields (everything not below)
//   pw:civ:st:<stId>:streets     streets, profile, roads7, walls, kitQueue, parked
//   pw:civ:st:<stId>:people      the census
//   pw:civ:st:<stId>:ledger      ledger + the chronicle (log)
//   pw:civ:index                 { v: 3, keys: [every section key], gen } — written last, every save
// Each section is a chunked text (putText: <key>:n + <key>:<i>, 30,000 chars each, one property holds 32,767 at most);
// within a changed section only the CHUNKS whose text changed are rewritten.
// Load: the index, else the legacy single JSON (pw:civ_clock). The first save after a legacy load writes every section,
// then the index, then drops the legacy key. A key the new index no longer lists (a removed settlement) is dropped after
// the index is written.

export const VERSION = 3;
export const INDEX = "pw:civ:index";
export const META = "pw:civ:meta";
export const LEGACY = "pw:civ_clock";
export const TEXT_CHUNK = 30000;
/** the settlement fields that live outside :core (each list in this order — split / assemble stay stable) */
export const ST_PARTS = {
  streets: ["streets", "profile", "roads7", "walls", "kitQueue", "parked"],
  people: ["people"],
  ledger: ["ledger", "log"],
};
const PART_OF = new Map(Object.entries(ST_PARTS).flatMap(([part, keys]) => keys.map((k) => [k, part])));

// ------------------------------------------------------------------------------------------------ chunked texts
const nKey = (key) => `${key}:n`;
/** a text of any length: <key>:n = the chunk count, <key>:<i> = the chunks. `old` = the text last written under this key
 *  (when known): only the chunks that differ are written. Returns the number of chunk writes. */
export function putText(store, key, txt, old = undefined) {
  const n = Math.ceil(txt.length / TEXT_CHUNK) || 1;
  let writes = 0;
  const oldN = Number(store.getDynamicProperty(nKey(key)) || 0);
  for (let i = 0; i < n; i++) {
    const part = txt.slice(i * TEXT_CHUNK, (i + 1) * TEXT_CHUNK);
    if (typeof old === "string" && i < oldN && old.slice(i * TEXT_CHUNK, (i + 1) * TEXT_CHUNK) === part) continue;
    store.setDynamicProperty(`${key}:${i}`, part); writes++;
  }
  for (let i = n; i < oldN; i++) { store.setDynamicProperty(`${key}:${i}`, undefined); writes++; }
  if (oldN !== n) { store.setDynamicProperty(nKey(key), String(n)); writes++; }
  if (store.getDynamicProperty(key) !== undefined) { store.setDynamicProperty(key, undefined); writes++; }   // a legacy single key goes
  return writes;
}
export function getText(store, key) {
  const n = Number(store.getDynamicProperty(nKey(key)) || 0);
  if (n > 0) { let txt = ""; for (let i = 0; i < n; i++) txt += store.getDynamicProperty(`${key}:${i}`) || ""; return txt; }
  const raw = store.getDynamicProperty(key);
  return typeof raw === "string" ? raw : undefined;
}
export function hasText(store, key) { return store.getDynamicProperty(nKey(key)) !== undefined || store.getDynamicProperty(key) !== undefined; }
export function dropText(store, key) {
  const n = Number(store.getDynamicProperty(nKey(key)) || 0);
  for (let i = 0; i < n; i++) store.setDynamicProperty(`${key}:${i}`, undefined);
  store.setDynamicProperty(nKey(key), undefined);
  store.setDynamicProperty(key, undefined);
}

// ------------------------------------------------------------------------------------------------ split / assemble
const tokOf = (v) => String(v).replace(/[^A-Za-z0-9_~-]/g, "_");
/** the state -> Map(section key -> JSON text). Deterministic: assemble(split(x)) deep-equals x, and split(assemble(t))
 *  gives back the same texts t (so a load followed by a save of an unchanged town writes nothing but the index). */
export function split(state) {
  const out = new Map();
  const meta = {};
  for (const k of Object.keys(state)) if (k !== "buildings" && k !== "settlements") meta[k] = state[k];
  // settlements: one token each (a repeated id gets ~<position>, so no two settlements share a key)
  const toks = [], seen = new Set();
  const sts = state.settlements || [];
  for (let i = 0; i < sts.length; i++) {
    let t = tokOf(sts[i].id);
    if (seen.has(t)) t = `${t}~${i}`;
    seen.add(t); toks.push(t);
  }
  // buildings: grouped by settlement; the global order as run-length [[group, count], ...]
  const groups = new Map(), rle = [];
  for (const b of state.buildings || []) {
    const g = b.settlement === undefined || b.settlement === null ? "_" : tokOf(b.settlement);
    if (!groups.has(g)) groups.set(g, []);
    groups.get(g).push(b);
    if (rle.length && rle[rle.length - 1][0] === g) rle[rle.length - 1][1]++;
    else rle.push([g, 1]);
  }
  out.set(META, JSON.stringify({ m: meta, st: toks, b: rle }));
  for (const [g, list] of groups) out.set(`pw:civ:b:${g}`, JSON.stringify(list));
  for (let i = 0; i < sts.length; i++) {
    const st = sts[i], base = `pw:civ:st:${toks[i]}`;
    const core = {};
    for (const k of Object.keys(st)) if (!PART_OF.has(k)) core[k] = st[k];
    out.set(`${base}:core`, JSON.stringify(core));
    for (const [part, keys] of Object.entries(ST_PARTS)) {
      const o = {}; let any = false;
      for (const k of keys) if (Object.prototype.hasOwnProperty.call(st, k)) { o[k] = st[k]; any = true; }
      if (any) out.set(`${base}:${part}`, JSON.stringify(o));
    }
  }
  return out;
}
/** read(key) -> text | undefined. Returns { state, problems } or null when there is no index (or it is not v3). A missing
 *  or broken section is reported in `problems` and skipped (never a fresh town: that would overwrite the saved one). */
export function assemble(read) {
  let idx;
  try { idx = JSON.parse(read(INDEX) || "null"); } catch { idx = null; }
  if (!idx || idx.v !== VERSION || !Array.isArray(idx.keys)) return null;
  const problems = [];
  const keys = new Set(idx.keys);
  const parse = (k) => { const t = read(k); if (t === undefined) { problems.push(`missing ${k}`); return undefined; } try { return JSON.parse(t); } catch (e) { problems.push(`broken ${k}: ${String(e).slice(0, 60)}`); return undefined; } };
  const meta = parse(META);
  if (!meta || typeof meta !== "object") return { state: null, problems, index: idx };
  const state = { ...(meta.m || {}) };
  // buildings in their saved order
  const groups = new Map();
  for (const k of idx.keys) if (k.startsWith("pw:civ:b:")) { const l = parse(k); if (Array.isArray(l)) groups.set(k.slice(9), l); }
  const at = new Map();
  const buildings = [];
  for (const [g, n] of meta.b || []) {
    const l = groups.get(g) || [];
    let i = at.get(g) || 0;
    for (let j = 0; j < n && i < l.length; j++) buildings.push(l[i++]);
    at.set(g, i);
  }
  for (const [g, l] of groups) { const i = at.get(g) || 0; if (i < l.length) { problems.push(`order: ${l.length - i} building(s) of ${g} appended`); for (let j = i; j < l.length; j++) buildings.push(l[j]); } }
  state.buildings = buildings;
  // settlements: core, then its parts in ST_PARTS order
  state.settlements = [];
  for (const t of meta.st || []) {
    const base = `pw:civ:st:${t}`;
    const core = parse(`${base}:core`);
    if (!core || typeof core !== "object") continue;
    for (const part of Object.keys(ST_PARTS)) {
      const k = `${base}:${part}`;
      if (!keys.has(k)) continue;
      const o = parse(k);
      if (o && typeof o === "object") Object.assign(core, o);
    }
    state.settlements.push(core);
  }
  return { state, problems, index: idx };
}

// ------------------------------------------------------------------------------------------------ the saver
/** createSaver(store): { load(), write(state), stats(), sizes() }. Keeps the text last written per key in memory (a string
 *  compare is native and fast; a hash over megabytes in QuickJS is not) — about the state's size in memory. */
export function createSaver(store) {
  const last = new Map();            // section key -> the text now stored under it
  let gen = 0, legacy = false, lastStat = null;
  const stat = { saves: 0, sectionWrites: 0, chunkWrites: 0, chars: 0, legacyMigrated: 0, dropped: 0 };
  return {
    /** -> { state, from: "index" | "legacy" | "none", problems } */
    load() {
      last.clear(); legacy = false;
      const texts = new Map();
      const read = (k) => { const t = getText(store, k); if (t !== undefined) texts.set(k, t); return t; };
      const r = assemble(read);
      if (r && r.state) {
        gen = Number(r.index.gen) || 0;
        // the texts as read are the texts now stored: an unchanged town's first save writes nothing but the index. Only a
        // section the assembled town gives back EXACTLY is remembered — a broken / unread one is never dropped as stale (it
        // stays in the store, recoverable) and a differing one is rewritten
        const again = split(r.state);
        for (const [k, t] of texts) if (k !== INDEX && again.get(k) === t) last.set(k, t);
        legacy = hasText(store, LEGACY);                  // a legacy key left over (a crash between the writes): dropped next save
        return { state: r.state, from: "index", problems: r.problems };
      }
      const raw = getText(store, LEGACY);
      if (raw) {
        try { const state = JSON.parse(raw); if (state && typeof state === "object") { legacy = true; return { state, from: "legacy", problems: r ? r.problems : [] }; } } catch (e) { return { state: null, from: "none", problems: [`legacy broken: ${String(e).slice(0, 60)}`] }; }
      }
      return { state: null, from: "none", problems: r ? r.problems : [] };
    },
    /** write the changed sections, then the index, then drop the stale keys (and a legacy key). One call = one tick. */
    write(state) {
      const secs = split(state);
      let wrote = 0, chars = 0, chunks = 0;
      const changed = [];
      for (const [k, txt] of secs) {
        const old = last.get(k);
        if (old === txt) continue;
        chunks += putText(store, k, txt, old);
        last.set(k, txt);
        wrote++; chars += txt.length; changed.push(k);
      }
      const prev = [...last.keys()].filter((k) => !secs.has(k));
      gen++;
      store.setDynamicProperty(INDEX, JSON.stringify({ v: VERSION, keys: [...secs.keys()], gen }));
      chunks++;
      for (const k of prev) { dropText(store, k); last.delete(k); stat.dropped++; }
      let migrated = false;
      if (legacy) { dropText(store, LEGACY); legacy = false; migrated = true; stat.legacyMigrated++; }
      let total = 0; for (const t of secs.values()) total += t.length;
      stat.saves++; stat.sectionWrites += wrote; stat.chunkWrites += chunks; stat.chars += chars;
      lastStat = { wrote, of: secs.size, chars, total, chunks, changed, dropped: prev.length, migrated, gen };
      return lastStat;
    },
    /** forget what is stored (the next write writes every section) */
    reset() { last.clear(); },
    stats() { return { ...stat, gen, last: lastStat }; },
    /** section key -> chars, as last written */
    sizes() { const o = {}; for (const [k, t] of last) o[k] = t.length; return o; },
  };
}
