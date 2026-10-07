// run the test's simulation for many seeds (copy of tests/test_homes.mjs §7)
import { readFileSync } from "node:fs";
const SRC = process.argv[2];
const PEOPLE = await import(SRC + "/pw_civ_people.js");
const { CIV_BUILDINGS } = await import(SRC + "/pw_civ_buildings.js");
const FAMILY = PEOPLE.FAMILY;
const clk = readFileSync(SRC + "/pw_civ_clock.js", "utf8");
const grab = (re) => clk.match(re)[1];
const HOUSEHOLD = Function(`return ${grab(/const HOUSEHOLD = (\{[^}]*\});/)}`)();
const DENSITY = JSON.parse(grab(/const DENSITY = (\[[^\]]*\]);/));
const TIER_ADDS = Function(`return ${grab(/const TIER_ADDS = (\{[\s\S]*?\n\});/)}`)();
const TIER_DAYS = Function(`return ${grab(/const TIER_DAYS = (\{[^}]*\});/)}`)();
const TIERS = Function(`return ${grab(/const TIERS = (\[[^\]]*\]);/)}`)();
const cls = (tier) => tier === "capital" ? 4 : tier.startsWith("metropolis") ? 3 : tier.startsWith("city") ? 2 : tier.startsWith("town") ? 1 : 0;
const OVR = JSON.parse(process.env.BEDS || "{}"); const bedsK = (k) => OVR[k] ?? PEOPLE.bedsOf((CIV_BUILDINGS[`pw:mvv_${k}_a_r1`] || {}).dir);
const sim = (seed, days, on) => {
  const was = FAMILY.on; FAMILY.on = on;
  const P = PEOPLE.newPeople(), homes = [];
  let nid = 1, tier = "village", moves = 0, swaps = 0;
  const build = (kind, day) => { const h = { id: nid++, kind, x: (nid * 37) % 200, z: (nid * 53) % 200 }; homes.push(h);
    for (let i = 0; i < (HOUSEHOLD[kind] || 0); i++) { const hs = (h.id * 7 + i * 11 + seed) >>> 0; PEOPLE.newPerson(P, day, { home: h.id, seed: h.id * 31 + i * 7 + seed, age: i < 2 ? 20 + (hs % 40) : hs % 15, sex: i === 0 ? "m" : i === 1 ? "f" : undefined, parents: [] }); } };
  for (const k of ["farm_wheat", "cottage_s", "inn", "cottage_m", "cottage_l", "farm_cattle"]) build(k, 0);
  const pend = []; let fam4 = 0, fam4Sleep = 0, births = 0;
  for (let day = 1; day <= days; day++) {
    const nx = TIERS[TIERS.indexOf(tier) + 1];
    if (nx && day >= TIER_DAYS[nx]) { tier = nx; for (const [k, n] of TIER_ADDS[tier]) if (HOUSEHOLD[k] !== undefined) for (let i = 0; i < n; i++) pend.push(k); }
    for (let i = 0; i < 2 && pend.length; i++) build(pend.shift(), day);
    const live = {}; for (const p of PEOPLE.alive(P)) if (p.home) live[p.home] = (live[p.home] || 0) + 1;
    const H = homes.map((h) => { const cap = Math.round((HOUSEHOLD[h.kind] || 0) * DENSITY[cls(tier)]); return { id: h.id, kind: h.kind, beds: bedsK(h.kind), room: Math.max(0, cap - (live[h.id] || 0)), over: Math.max(0, (live[h.id] || 0) - cap), x: h.x, z: h.z }; });
    const adults = PEOPLE.alive(P).filter((p) => PEOPLE.stage(p, day) !== "child").length, filled = PEOPLE.alive(P).filter((p) => p.job === "builders").length;
    const r = PEOPLE.dayStep(P, { day, fed: 1, paid: true, homes: H, jobs: [{ id: "builders", kind: "builder", vacancies: Math.max(0, adults - filled) + 2, x: 100, z: 100 }], seed, name: "Sim", events: [], sanitation: 1, health: 0,
                        levels: new Map(homes.map((h) => [h.id, PEOPLE.homeLevel(h.kind)])), foodDays: 15, diet: 1, wageOf: () => 72 });
    moves += r.family ? r.family.moved : 0; swaps += r.family ? r.family.swapped : 0; births += r.events.filter((e) => e.kind === "birth").length;
    const c = PEOPLE.familyCensus(P, homes.map((h) => ({ id: h.id, beds: bedsK(h.kind), kind: h.kind })), day);
    fam4 += c.bySize4plus; fam4Sleep += c.sleep4;
  }
  FAMILY.on = was;
  return { fam4, fam4Sleep, share: Math.round(1000 * fam4Sleep / Math.max(1, fam4)) / 10, pop: PEOPLE.alive(P).length, births, moves, swaps };
};
const days = Number(process.argv[3] || 260);
for (const seed of [3, 7, 11, 23, 31, 47, 59, 71]) { const off = sim(seed, days, false), on = sim(seed, days, true); console.log(seed, "off", JSON.stringify(off), "on", JSON.stringify(on), "x", (on.fam4Sleep / Math.max(1, off.fam4Sleep)).toFixed(2)); }
