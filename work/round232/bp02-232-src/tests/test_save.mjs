// test_save.mjs — 1.3.228 (B2 / BF2 + WE14): sectioned saves. split/assemble round trip; a save writes only the changed
// sections, all in one call, the index LAST; an unchanged town after a reload writes nothing but the index; a legacy
// single-JSON save loads and is migrated (sections written, legacy key dropped); a removed settlement's keys go; a broken
// section is never dropped; every property value fits the engine's 32,767-char limit; diagnostics leave the save (WE14).
import * as SAVE from "../pw_civ_save.js";
import { diagOutOfSave } from "../pw_civ_clock.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };

// a key-order-insensitive deep equality
const canon = (o) => Array.isArray(o) ? o.map(canon) : o && typeof o === "object" ? Object.fromEntries(Object.keys(o).sort().map((k) => [k, canon(o[k])])) : o;
const same = (a, b) => JSON.stringify(canon(a)) === JSON.stringify(canon(b));
const clone = (o) => JSON.parse(JSON.stringify(o));

/** a Map-backed dynamic-property store that records every write in order */
function store0() {
  const m = new Map(), log = [];
  return {
    m, log,
    getDynamicProperty: (k) => m.get(k),
    setDynamicProperty: (k, v) => {
      if (typeof v === "string" && v.length > 32767) throw new Error(`value too long for ${k}: ${v.length}`);
      log.push(k);
      if (v === undefined) m.delete(k); else m.set(k, v);
    },
  };
}

function town() {
  const person = (id, home) => ({ id, name: `P${id}`, sex: id % 2 ? "m" : "f", born: -30, home, job: null, alive: true, mood: 55, friends: { [id + 1]: 40 }, knows: Array.from({ length: 40 }, (_, k) => `rumour ${id}-${k} about the well and the market`) });
  const st = (id, n) => ({
    id, name: `Town ${id}`, tier: "town", dim: "minecraft:overworld", x0: id * 500, z0: 0, seed: id * 7, kit: true, phase: "built",
    square: { x: id * 500, y: 70, z: 0 }, kitVer: 3, why: { WORKING: 5, OFF_SHIFT: 2 },
    streets: [{ kind: "kit", id: 1, role: "main", H: Array.from({ length: 90 }, (_, k) => 70 + (k % 3)), segs: [], tmin: 0 }],
    profile: [1, 2, 3], roads7: [], walls: [], kitQueue: [{ op: "lay", i: 1 }], parked: [],
    people: { next: n + 1, list: Array.from({ length: n }, (_, k) => person(k + 1, 100 + k)), rumours: [], threads: [], nextThread: 1, player: {}, faucet: 0 },
    ledger: { day: 10, treasury: 1200, stock: { bread: 10, stone: 4 }, prices: { bread: 2 }, history: [1, 2, 3], prosperity: [1, 1] },
    log: ["day 1: founded", "day 2: a house"],
  });
  const B = [];
  let id = 1;
  for (let k = 0; k < 30; k++) B.push({ id: id++, family: "cottage_s", dim: "minecraft:overworld", x: k * 10, y: 70, z: 5, rot: k % 4, stage: 4, progress: 0, delay: 0, pending: [], settlement: k % 3 === 0 ? 2 : 1 });
  B.push({ id: id++, family: "cottage_m", dim: "minecraft:overworld", x: 9, y: 70, z: 9, rot: 0, stage: 1, progress: 0.5, delay: 0, pending: [] });   // the plot tool: no settlement
  return { paused: false, speed: 1, simDays: 12.5, lastWorld: 40.25, nextId: id, tick: { slots: 4, areas: {}, next: 1 }, buildings: B, settlements: [st(1, 120), st(2, 20)] };
}

// ---- 1. the round trip, and split(assemble(t)) gives back the same texts
{
  const S = town();
  const secs = SAVE.split(S);
  const r = SAVE.assemble((k) => (k === SAVE.INDEX ? JSON.stringify({ v: 3, keys: [...secs.keys()], gen: 1 }) : secs.get(k)));
  ok(r && r.state && same(r.state, S), "assemble(split(state)) deep-equals the state");
  ok(r && r.problems.length === 0, "no problems");
  ok(r && r.state.buildings.map((b) => b.id).join() === S.buildings.map((b) => b.id).join(), "the buildings keep their order (interleaved settlements + the plot tool)");
  const again = SAVE.split(r.state);
  ok([...secs].every(([k, t]) => again.get(k) === t) && again.size === secs.size, "split(assemble(t)) = t (stable texts)");
  ok(secs.has("pw:civ:b:1") && secs.has("pw:civ:b:2") && secs.has("pw:civ:b:_"), "one buildings section per settlement + the plot tool's");
  ok(["core", "streets", "people", "ledger"].every((p) => secs.has(`pw:civ:st:1:${p}`)), "core / streets / people / ledger per settlement");
  ok(!JSON.parse(secs.get("pw:civ:st:1:core")).people && !JSON.parse(secs.get("pw:civ:st:1:core")).streets, "core holds no part");
  ok(secs.get("pw:civ:st:1:people").length > SAVE.TEXT_CHUNK, `the census is a multi-chunk section (${secs.get("pw:civ:st:1:people").length} chars)`);
}

// ---- 2. the saver: first write = every section; then only the dirty ones; the index last
{
  const W = store0(), S = town();
  const sv = SAVE.createSaver(W);
  const w1 = sv.write(S);
  ok(w1.wrote === w1.of && w1.of === SAVE.split(S).size, `first save writes every section (${w1.wrote}/${w1.of})`);
  ok(W.log[W.log.length - 1] === SAVE.INDEX, "the index is the last write");
  ok(W.log.every((k) => typeof W.m.get(k) !== "string" || W.m.get(k).length <= 32767), "every value <= 32,767 chars");
  W.log.length = 0;
  const w2 = sv.write(S);
  ok(w2.wrote === 0 && W.log.length === 1 && W.log[0] === SAVE.INDEX, `an unchanged town writes only the index (${W.log.join()})`);
  // one stage change dirties only its settlement's buildings section
  W.log.length = 0;
  S.buildings[4].stage = 3;                                                     // building 5 is settlement 1's
  const w3 = sv.write(S);
  ok(w3.wrote === 1 && w3.changed[0] === "pw:civ:b:1", `a stage change dirties only b:1 (${w3.changed})`);
  ok(W.log.indexOf(SAVE.INDEX) === W.log.length - 1, "index last");
  ok(W.log.filter((k) => k.startsWith("pw:civ:b:1:")).length >= 1 && !W.log.some((k) => k.startsWith("pw:civ:st:")), "no settlement section written");
  // a mood change dirties only the census — and only the chunks that changed (the last person: the last chunk)
  W.log.length = 0;
  const P = S.settlements[0].people.list;
  P[P.length - 1].mood = 56;
  const w4 = sv.write(S);
  ok(w4.wrote === 1 && w4.changed[0] === "pw:civ:st:1:people", `a mood change dirties only st:1:people (${w4.changed})`);
  const n = Number(W.m.get("pw:civ:st:1:people:n"));
  const chunkWrites = W.log.filter((k) => /^pw:civ:st:1:people:\d+$/.test(k)).length;
  ok(n >= 2 && chunkWrites === 1, `only the changed chunk is rewritten (${chunkWrites} of ${n})`);
  // a new building of settlement 2: its section and the meta (the order)
  S.buildings.push({ id: S.nextId++, family: "bakery", dim: "minecraft:overworld", x: 1, y: 70, z: 1, rot: 0, stage: 0, progress: 0, delay: 0, pending: [], settlement: 2 });
  const w5 = sv.write(S);
  ok(w5.wrote === 2 && w5.changed.includes("pw:civ:b:2") && w5.changed.includes(SAVE.META), `a new building: b:2 + meta (${w5.changed})`);
  // a daily tick: meta + ledger + core only
  S.simDays += 1; S.settlements[0].ledger.treasury += 5; S.settlements[0].why = { WORKING: 6 };
  const w6 = sv.write(S);
  ok(w6.wrote === 3 && ["pw:civ:meta", "pw:civ:st:1:ledger", "pw:civ:st:1:core"].every((k) => w6.changed.includes(k)), `a day: meta + ledger + core (${w6.changed})`);

  // ---- 3. reload: the same town; its first save writes nothing but the index
  const sv2 = SAVE.createSaver(W);
  const L = sv2.load();
  ok(L.from === "index" && same(L.state, S), "reload from the index = the town");
  W.log.length = 0;
  const w7 = sv2.write(L.state);
  ok(w7.wrote === 0 && W.log.length === 1, `after a reload an unchanged town writes only the index (${w7.changed})`);
  ok(w7.gen === w6.gen + 1, "the generation counts on across the reload");

  // ---- 4. a removed settlement's keys are dropped (after the index)
  W.log.length = 0;
  L.state.settlements.pop();
  L.state.buildings = L.state.buildings.filter((b) => b.settlement !== 2);
  const w8 = sv2.write(L.state);
  ok(w8.dropped === 5, `settlement 2's five keys dropped (${w8.dropped})`);
  ok(![...W.m.keys()].some((k) => k.startsWith("pw:civ:st:2:") || k.startsWith("pw:civ:b:2")), "nothing of settlement 2 is left in the store");
  const ix = W.log.indexOf(SAVE.INDEX);
  ok(ix >= 0 && W.log.slice(ix + 1).every((k) => k.startsWith("pw:civ:st:2:") || k.startsWith("pw:civ:b:2")), "the drops come after the index");
}

// ---- 5. legacy: a 1.3.227 single JSON (chunked pw:civ_clock) loads, and the first save migrates it
{
  const W = store0();
  const old = town();
  old.settlements[0].marketGate = [12, 11, false, 0, [[3, 4, 0]]];
  old.settlements[0].counters = { day: 12, shops: [[3, "bakery", 4, "ok"]] };
  old.settlements[0].marketTry = { day: 12, goals: 7, noShop: 1, shoppers: [1, 2, 3] };
  old.settlements[0].market = { day: 12, buys: 9, empty: 0, homes: [100, 101, 100, 102] };
  const txt = JSON.stringify(old);
  for (let i = 0; i * 30000 < txt.length; i++) W.m.set(`pw:civ_clock:${i}`, txt.slice(i * 30000, (i + 1) * 30000));
  W.m.set("pw:civ_clock:n", String(Math.ceil(txt.length / 30000)));
  const sv = SAVE.createSaver(W);
  const L = sv.load();
  ok(L.from === "legacy" && same(L.state, old), "the legacy JSON loads whole");
  for (const st of L.state.settlements) diagOutOfSave(st);                    // what the clock's load() does (WE14)
  const st1 = L.state.settlements[0];
  ok(st1.marketGate === undefined && st1.counters === undefined && st1.marketTry === undefined, "WE14: the diagnostics left the saved settlement");
  ok(st1.market.homes === 3 && st1.market.buys === 9, `WE14: market.homes is a count of distinct homes (${st1.market.homes})`);
  const w = sv.write(L.state);
  ok(w.migrated && w.wrote === w.of, `the first save writes every section and migrates (${w.wrote}/${w.of})`);
  ok(![...W.m.keys()].some((k) => k.startsWith("pw:civ_clock")), "the legacy key is gone");
  const L2 = SAVE.createSaver(W).load();
  ok(L2.from === "index" && same(L2.state, L.state), "the next load reads the sections");
  ok(!JSON.stringify(L2.state).includes("marketGate") && !JSON.stringify(L2.state).includes("shoppers"), "no diagnostics in the saved sections");
}

// ---- 6. a single-key legacy (v1.3.206 / early 207) loads too
{
  const W = store0();
  const S = { paused: true, speed: 2, simDays: 3, lastWorld: 1, buildings: [], nextId: 1, settlements: [] };
  W.m.set("pw:civ_clock", JSON.stringify(S));
  const sv = SAVE.createSaver(W);
  const L = sv.load();
  ok(L.from === "legacy" && same(L.state, S), "a single-key legacy save loads");
  sv.write(L.state);
  ok(!W.m.has("pw:civ_clock") && W.m.has(SAVE.INDEX), "and is migrated");
}

// ---- 7. a broken section: reported, the rest loads, and it is never dropped as stale
{
  const W = store0(), S = town();
  SAVE.createSaver(W).write(S);
  W.m.set("pw:civ:st:2:core:0", "{broken");
  const sv = SAVE.createSaver(W);
  const L = sv.load();
  ok(L.from === "index" && L.problems.length === 1 && L.problems[0].includes("pw:civ:st:2:core"), `the broken section is reported (${L.problems})`);
  ok(L.state.settlements.length === 1 && L.state.settlements[0].id === 1, "the readable settlement loads");
  sv.write(L.state);
  ok(W.m.get("pw:civ:st:2:core:0") === "{broken", "the broken section stays in the store (recoverable), never dropped");
}

// ---- 8. nothing saved yet: no state, no problems (a fresh world, not a hold)
{
  const L = SAVE.createSaver(store0()).load();
  ok(L.state === null && L.from === "none" && L.problems.length === 0, "a fresh world: nothing to load, nothing wrong");
}

// ---- 9. putText chunk law
{
  const W = store0();
  const big = "x".repeat(65000);
  SAVE.putText(W, "k", big);
  ok(W.m.get("k:n") === "3" && SAVE.getText(W, "k") === big, "65,000 chars = 3 chunks, read back whole");
  SAVE.putText(W, "k", "short", big);
  ok(W.m.get("k:n") === "1" && !W.m.has("k:1") && !W.m.has("k:2") && SAVE.getText(W, "k") === "short", "a shorter text drops the extra chunks");
}

console.log(`test_save: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
