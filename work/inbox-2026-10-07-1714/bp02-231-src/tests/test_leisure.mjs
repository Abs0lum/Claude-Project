// test_leisure.mjs — 1.3.231 (CIV-PEOPLE; his 02:44 CT 10-07 screenshot at -168 68 125: four civs bunched on the square's
// paving around the well in daylight). Mechanism (pw_civ_clock.js 1.3.230): (a) leisureGoal offered the square's ring at
// EVERY hour as one of 2..4 equal options (1/2 of a homeless body's idle hours, 1/3..1/4 of a housed one's) and the
// neighbourhood centre's WELL front; (b) goalFor's rest slot sent every body WITHOUT a home to the square's ring — all
// night, and all DAY for the night watch (rest 05..17). The fix: idle places are weighted (home, workplace, shops, the
// centre's shops, the park's benches, the inn) and the square is offered only at its hours (dusk, the midday market);
// a body without a home rests in the inn as a paying guest, else in a shelter (its workplace, the town hall, the chapel).
// Pure parts from pw_civ_people.js; leisureGoal / restGoal cut from pw_civ_clock.js and run on stand-ins.
import { readFileSync } from "node:fs";
import * as PEOPLE from "../pw_civ_people.js";
let pass = 0, fail = 0;
const ok = (c, m, extra) => { if (c) pass++; else { fail++; console.log("FAIL", m, extra === undefined ? "" : JSON.stringify(extra)); } };
const { LEISURE } = PEOPLE;

// ------------------------------------------------------------------------------------------------ 1. weights by the hour
{
  ok(LEISURE && LEISURE.market && LEISURE.market[0] === 5000 && LEISURE.market[1] === 7000, "the market hours are the clock's MARKET (5000..7000)");
  const day = PEOPLE.leisureWeights({ dusk: false, tod: 3000, housed: true });
  ok(day.square === 0 && day.well === undefined, "a morning: the square is NOT an idle place (and no well kind exists)", day);
  ok(day.home > 0 && day.shop > 0 && day.park > 0 && day.centre > 0 && day.inn > 0 && day.work > 0, "a morning: home, work, shops, the centre's shops, the park, the inn", day);
  ok(PEOPLE.leisureWeights({ dusk: false, tod: 9000, housed: true }).square === 0, "the afternoon: no square");
  ok(PEOPLE.leisureWeights({ dusk: false, tod: 6000, housed: true }).square > 0, "the midday market: the square (the stall) is a place");
  const dusk = PEOPLE.leisureWeights({ dusk: true, tod: 11500, housed: true });
  ok(dusk.square > 0 && dusk.inn > day.inn, "dusk: the square and the inn draw people (the evening gathering kept)", dusk);
  const hl = PEOPLE.leisureWeights({ dusk: false, tod: 3000, housed: false });
  ok(hl.home === 0 && hl.square === 0 && hl.inn > day.inn, "no home: no home front; the inn weighs more", hl);
}

// ------------------------------------------------------------------------------------------------ 2. the pick
{
  const C = [{ kind: "home", at: { x: 1 } }, { kind: "square", at: { x: 2 } }, { kind: "shop", at: { x: 3 } }, { kind: "park", at: { x: 4 } }];
  const w = PEOPLE.leisureWeights({ dusk: false, tod: 3000, housed: true });
  let sq = 0, n0 = 0;
  const seen = {};
  for (let n = 1; n <= 3000; n++) for (let ph = 0; ph < 4; ph++) { const c = PEOPLE.leisurePick(C, n, ph, w); n0++; if (c.kind === "square") sq++; seen[c.kind] = (seen[c.kind] || 0) + 1; }
  ok(sq === 0, "daytime: nobody idles on the square", seen);
  ok(Object.keys(seen).length === 3 && Object.values(seen).every((k) => k > n0 * 0.15), "daytime: home, shop and park all used (each > 15 %)", seen);
  ok(PEOPLE.leisurePick(C, 77, 2, w) === PEOPLE.leisurePick(C, 77, 2, w), "deterministic by person and phase");
  let moved = 0;
  for (let n = 1; n <= 500; n++) if (PEOPLE.leisurePick(C, n, 1, w).kind !== PEOPLE.leisurePick(C, n, 2, w).kind) moved++;
  ok(moved > 150, "people move on between phases (the town spreads out through the day)", moved);
  ok(PEOPLE.leisurePick([], 5, 1, w) === null && PEOPLE.leisurePick([{ kind: "square", at: {} }], 5, 1, w) === null, "nothing allowed: null (the caller falls back)");
  const wd = PEOPLE.leisureWeights({ dusk: true, tod: 11500, housed: true });
  let sqd = 0;
  for (let n = 1; n <= 3000; n++) if (PEOPLE.leisurePick(C, n, 4, wd).kind === "square") sqd++;
  ok(sqd > 300 && sqd < 1500, "dusk: a share goes to the square (10..50 %), not everybody", sqd);
}

// ------------------------------------------------------------------------------------------------ 3. the park's bench spots
{
  ok(PEOPLE.parkSpot(null, 1) === null && PEOPLE.parkSpot({ box: [0, 14, 0, 14], H: 70, done: false }, 1) === null, "no park / not laid: none");
  const pk = { box: [10, 24, 20, 34], H: 70, done: true };
  const spots = [0, 1, 2, 3].map((k) => PEOPLE.parkSpot(pk, k));
  const cx = 17, cz = 27;
  ok(spots.every((s) => s && s.y === 71 && (Math.floor(s.x) === cx || Math.floor(s.z) === cz)), "four spots on the park's cross paths at feet level", spots);
  const benches = [[cx - 1, cz - 3], [cx + 1, cz + 3], [cx - 3, cz + 1], [cx + 3, cz - 1]];
  ok(spots.every((s) => benches.some(([bx, bz]) => Math.abs(bx - Math.floor(s.x)) + Math.abs(bz - Math.floor(s.z)) === 1)), "each spot is beside one of layPark's four benches", spots);
  ok(new Set(spots.map((s) => `${s.x},${s.z}`)).size === 4 && PEOPLE.parkSpot(pk, 5).x === spots[1].x, "four different spots, by k mod 4");
}

// ------------------------------------------------------------------------------------------------ 4. the clock's leisureGoal and restGoal (cut, stand-ins)
{
  const src = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
  const cut = (name) => {
    const i = src.indexOf(`function ${name}(`);
    if (i < 0) return null;
    let k = src.indexOf("{", i), depth = 0, j = k;
    for (; j < src.length; j++) { if (src[j] === "{") depth++; else if (src[j] === "}" && --depth === 0) break; }
    return src.slice(i, j + 1);
  };
  const lg = cut("leisureGoal"), rg = cut("restGoal");
  ok(!!lg && !!rg, "leisureGoal and restGoal exist in the clock");
  if (lg && rg) {
    const SQ = { x: 100, y: 64, z: 100 };
    const B = new Map();
    const add = (b) => { B.set(b.id, { settlement: 1, stage: 4, rot: 0, ...b }); return B.get(b.id); };
    const home = add({ id: 1, family: "cot", x: 0, y: 64, z: 0 });
    const well = add({ id: 2, family: "well", x: 104, y: 64, z: 104 });                       // the square's well
    const cwell = add({ id: 3, family: "well", x: 300, y: 64, z: 0 });                        // a neighbourhood centre's well
    const cbak = add({ id: 4, family: "bakery", x: 310, y: 64, z: 0 });
    const smithy = add({ id: 5, family: "smithy", x: 50, y: 64, z: 60 });
    const inn = add({ id: 6, family: "inn", x: 80, y: 64, z: 140 });
    const hall = add({ id: 7, family: "town_hall", x: 140, y: 64, z: 80 });
    const st = { id: 1, square: SQ, centres: [{ sid: 9, well: 3, shops: [4] }], park: { box: [200, 214, 200, 214], H: 64, done: true }, people: PEOPLE.newPeople() };
    const short = (b) => b.family;
    const BUILDINGS = { cot: { dir: [] }, well: { dir: [] }, bakery: { dir: [] }, smithy: { dir: [] }, town_hall: { dir: [] },
                        inn: { dir: [0, 2, 4, 6].flatMap((x) => [[x, 1, 0, "minecraft:bed"], [x, 1, 1, "minecraft:bed"]]) } };   // 4 beds (2 blocks each)
    const front = (b) => ({ x: b.x + 0.5, z: b.z + 0.5, y: b.y, of: b.id });
    const insideDoor = (b) => ({ x: b.x + 1.5, y: b.y, z: b.z + 1.5, in: b.id });
    const squareSlot = (st0, n, salt = 0) => ({ x: st0.square.x + 1 + ((n + salt) % 10) + 0.5, z: st0.square.z + 1.5, y: st0.square.y + 1, ring: true });
    const plotsOf = () => [...B.values()];
    const env = { PEOPLE, BUILDINGS, insideDoor, squareSlot, plotsOf, short, SHOPS: ["bakery", "butcher", "smithy", "inn", "lumberyard", "quarry"],
                  buildingById: (s0, id) => B.get(id) || null, innGoal: () => null, idNum: (v, p) => (p ? p.id : 1), MARKET: [5000, 7000] };
    const leisureGoal = new Function(...Object.keys(env), `${lg}; return leisureGoal;`)(...Object.values(env));
    const restGoal = new Function(...Object.keys(env), `${rg}; return restGoal;`)(...Object.values(env));
    const ctx = () => ({ byId: B, fin: [smithy, inn, cbak], inn, people: new Map() });
    const nearWell = (g) => g && Math.abs(g.x - (well.x + 2)) <= 3 && Math.abs(g.z - (well.z + 3)) <= 3;
    const onSquare = (g) => g && g.x >= SQ.x && g.x < SQ.x + 12 && g.z >= SQ.z && g.z < SQ.z + 12;
    const atCentreWell = (g) => g && g.of === cwell.id;
    // daytime idle: the whole town (2,000 people x 4 phases), housed (with a centre) and homeless
    let sqDay = 0, wellAny = 0, cwellAny = 0, total = 0;
    const kinds = {};
    for (let id = 1; id <= 2000; id++) for (const tod of [1500, 3500, 8000, 10500]) {
      const p = { id, home: id % 2 ? 1 : null, job: id % 3 === 0 ? 5 : null };
      const g = leisureGoal({}, st, { id: `v${id}` }, p, p.home ? home : null, tod, front, p.home ? cwell : null, false, ctx());
      total++;
      if (onSquare(g)) sqDay++;
      if (nearWell(g)) wellAny++;
      if (atCentreWell(g)) cwellAny++;
      kinds[g ? g.leisure : "null"] = (kinds[g ? g.leisure : "null"] || 0) + 1;
    }
    ok(sqDay === 0 && wellAny === 0, "clock: daytime idle never on the square / at the well", { sqDay, wellAny, kinds });
    ok(cwellAny === 0 && kinds.centre > 0, "clock: the neighbourhood centre means its shops, never its well front", kinds);
    ok(kinds.park > total * 0.05 && kinds.home > total * 0.1 && kinds.shop > total * 0.1 && kinds.inn > 0 && kinds.work > 0, "clock: idle civs spread over home, shops, park, inn, workplace", kinds);
    let sqDusk = 0;
    for (let id = 1; id <= 2000; id++) { const p = { id, home: 1, job: null }; if (onSquare(leisureGoal({}, st, { id: "v" }, p, home, 11500, front, null, true, ctx()))) sqDusk++; }
    ok(sqDusk > 100 && sqDusk < 1200, "clock: at dusk some go to the square (the gathering kept), not all", sqDusk);
    // the rest slot: no home -> the inn's guest bed (3 beds free: 4 minus the resident), then a shelter, never the square
    const P = st.people;
    const resident = PEOPLE.newPerson(P, 200, { home: 6, job: 6, age: 40, seed: 1 });
    const hl = [1, 2, 3, 4, 5].map((i) => PEOPLE.newPerson(P, 200, { home: null, age: 30 + i, seed: 10 + i, job: i === 5 ? 5 : i === 4 ? "watch" : null }));
    const c = ctx();
    const gs = hl.map((p) => restGoal({}, st, p, typeof p.job === "number" ? B.get(p.job) : null, c));
    ok(gs.slice(0, 3).every((g) => g && g.in === inn.id && g.lodge === inn.id), "clock: the first three homeless sleep at the inn as guests", gs);
    ok(gs[3] && gs[3].in === hall.id, "clock: the inn full, a homeless watchman (no workplace) shelters in the town hall", gs[3]);
    ok(gs[4] && gs[4].in === smithy.id, "clock: the inn full, a homeless smith shelters in his smithy", gs[4]);
    ok(gs.every((g) => !onSquare(g)), "clock: no homeless body rests on the square");
    let threw = false, r0;
    try { r0 = restGoal({}, { ...st, people: PEOPLE.newPeople() }, null, null, { byId: new Map(), inn: null, people: new Map() }); } catch (e) { threw = String(e); }
    ok(!threw && r0 && r0.in === hall.id, "clock: a body with no census person rests in a shelter (no crash)", { threw, r0 });
    void resident;
  }
}

console.log(`test_leisure: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
