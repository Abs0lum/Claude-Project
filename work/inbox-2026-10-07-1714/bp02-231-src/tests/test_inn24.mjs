// test_inn24.mjs — 1.3.231 (CIV-PEOPLE; his 00:23 CT 10-07 ruling + his 02:43 witness "We're closed" in daylight): pure.
// The witnessed mechanism: the shop window (pw_civ_shop.js openShop) refused whenever world time of day was outside the
// FIXED window 1000..11000, while the innkeeper's own shift (the "late" template) runs 3000..13000 — so from 17:00 to 19:00
// (tod 11000..13000, full daylight) Sven stood at his station and said "We're closed". The ruling: the inn is open round
// the clock with several staff on a rota (day / evening / night, serving staff beyond), a guest can always rent a bed or
// buy food while ANY staffer is on duty, "closed" only when no staffer is. The inn's cover posts are hired after the
// town's posts and before the shops (D-C1006-WATCH: priority classes kept, nearest within each class).
import * as PEOPLE from "../pw_civ_people.js";
let pass = 0, fail = 0;
const ok = (c, m, extra) => { if (c) pass++; else { fail++; console.log("FAIL", m, extra === undefined ? "" : JSON.stringify(extra)); } };
const { SHIFT, INN24 } = PEOPLE;
const staffer = (id, o = {}) => ({ id, name: `S${id}`, sex: "m", born: 0, home: 50, job: 50, trade: "inn", spouse: null, parents: [], kids: [], friends: {}, mood: 55, alive: true, knows: [], ...o });

// ------------------------------------------------------------------------------------------------ 1. the old mismatch (documented)
{
  const keeper = staffer(7, { keeper: true });
  // the old gate: 1000 <= tod < 11000; the keeper's own "late" shift without a rota: W 09..19 (tod 3000..13000) +- offset
  const oldGate = (tod) => tod >= 1000 && tod < 11000;
  let mismatch = 0;
  for (let tod = 11000; tod < 12800; tod += 100) if (!oldGate(tod) && PEOPLE.shiftAt(keeper, tod, 3, { kind: "inn", keeper: true }).slot === "W") mismatch++;
  ok(mismatch >= 15, "mechanism: 17:00..18:48 the late-shift keeper is AT WORK while the old fixed gate said closed", mismatch);
}

// ------------------------------------------------------------------------------------------------ 2. templates
{
  ok(INN24 && INN24.cover === 3, "INN24.cover = 3 (day, evening, night)");
  for (const t of ["inn_solo", "inn_long_d", "inn_long_n", "inn_day", "inn_eve", "inn_night", "inn_serve"]) ok(SHIFT.T[t] && SHIFT.T[t].length === 24 && /^[WMIR]+$/.test(SHIFT.T[t]), `template ${t}: 24 hours of W/M/I/R`);
  ok(Object.values(SHIFT.T).every((t) => t.length === 24 && /^[WMIR]+$/.test(t)), "every template still valid");
  ok(PEOPLE.isInnTpl("inn_day") && !PEOPLE.isInnTpl("late") && !PEOPLE.isInnTpl(undefined), "isInnTpl");
  // the rota's three 8-hour shifts tile the day exactly once
  const cover = new Array(24).fill(0);
  for (const t of ["inn_day", "inn_eve", "inn_night"]) for (let h = 0; h < 24; h++) if (SHIFT.T[t][h] === "W") cover[h]++;
  ok(cover.every((n) => n === 1), "day + evening + night: every hour covered exactly once", cover);
  const pair = new Array(24).fill(0);
  for (const t of ["inn_long_d", "inn_long_n"]) for (let h = 0; h < 24; h++) if (SHIFT.T[t][h] === "W") pair[h]++;
  ok(pair.every((n) => n === 1), "two staff: two 12-hour shifts cover every hour", pair);
  ok(["inn_day", "inn_eve", "inn_night", "inn_long_d", "inn_long_n", "inn_solo"].every((t) => (SHIFT.off[t] || 0) === 0), "the cover shifts take no whole day off (8 / 12-hour days; a lone keeper never closes a whole day)");
  ok([...SHIFT.T.inn_solo].filter((c) => c === "W").length >= 16, "a lone innkeeper keeps the inn open late (>= 16 hours)");
}

// ------------------------------------------------------------------------------------------------ 3. the rota
{
  const R = (staff) => PEOPLE.innRota(staff);
  const a = staffer(9), k = staffer(12, { keeper: true }), b = staffer(3), c = staffer(20), d = staffer(5);
  ok(R([k]).get(12) === "inn_solo", "one staffer: the lone keeper's long day");
  const r2 = R([a, k]);
  ok(r2.get(12) === "inn_long_d" && r2.get(9) === "inn_long_n", "two: the keeper takes the day, the other the night", [...r2]);
  const r3 = R([a, b, k]);
  ok(r3.get(12) === "inn_day" && r3.get(3) === "inn_night" && r3.get(9) === "inn_eve", "three: keeper day, then by id night, evening", [...r3]);
  const r5 = R([c, a, d, b, k]);
  ok(r5.get(12) === "inn_day" && r5.get(3) === "inn_night" && r5.get(5) === "inn_eve" && r5.get(9) === "inn_serve" && r5.get(20) === "inn_serve", "five: + two serving staff", [...r5]);
  ok(R([]).size === 0 && R([staffer(4, { alive: false }), k]).get(12) === "inn_solo", "the dead are not on the rota");
  ok(PEOPLE.shiftTemplate(a, { kind: "inn", inn: r3 }) === "inn_eve" && PEOPLE.shiftTemplate(a, { kind: "inn" }) === "late", "shiftTemplate reads the rota (without one: the old late template)");
  ok(PEOPLE.shiftTemplate(staffer(9, { shift: "standard" }), { kind: "inn", inn: r3 }) === "standard", "the shift command's override still wins");
}

// ------------------------------------------------------------------------------------------------ 4. round-the-clock cover
{
  const day0 = 0;
  let gaps = 0, checked = 0;
  for (const ids of [[12, 3, 9], [12, 3, 9, 5], [12, 3, 9, 5, 20], [401, 77, 1999]]) {
    const staff = ids.map((id, i) => staffer(id, { keeper: i === 0 }));
    for (const seed of [0, 1, 777]) for (let day = day0; day < day0 + 14; day++) for (let tod = 0; tod < 24000; tod += 50) {
      checked++;
      if (!PEOPLE.innStatus(staff, tod, day, { seed }).on.length) gaps++;
    }
  }
  ok(gaps === 0, "3+ staff: someone is on duty at EVERY tick-50 of 14 days, any ids, any seed (no handover gap: the rota has no start offset)", { gaps, checked });
  let gaps2 = 0;
  const two = [staffer(12, { keeper: true }), staffer(1999)];
  for (let day = 0; day < 14; day++) for (let tod = 0; tod < 24000; tod += 50) if (!PEOPLE.innStatus(two, tod, day, { seed: 5 }).on.length) gaps2++;
  ok(gaps2 === 0, "2 staff: open round the clock too", gaps2);
  const solo = [staffer(12, { keeper: true })];
  let dayGaps = 0;
  for (let day = 0; day < 14; day++) for (let tod = 0; tod <= 12500; tod += 50) if (!PEOPLE.innStatus(solo, tod, day, { seed: 9 }).on.length) dayGaps++;
  ok(dayGaps === 0, "a lone keeper: open through ALL daylight (06:00..18:30) every day — the witnessed 'closed in daylight' cannot recur", dayGaps);
  const st = PEOPLE.innStatus(solo, 18000, 3, { seed: 9 });     // midnight
  ok(st.on.length === 0 && st.next === 6000, "a lone keeper at midnight: closed, opens in 6,000 ticks (06:00)", st);
  ok(PEOPLE.innStatus([], 6000, 1, {}).on.length === 0 && PEOPLE.innStatus([], 6000, 1, {}).next === null, "no staff at all: closed, no opening time");
  // the walk home (PE5) never cuts a cover shift short: the relief comes to the counter, the staffer goes when relieved
  const eve = staffer(9);
  ok(PEOPLE.shiftAt(eve, 15900, 2, { tpl: "inn_eve", travel: 3000 }).slot === "W", "inn_eve at 21:54 with a 3,000-tick walk home: still at work");
  ok(PEOPLE.shiftAt(staffer(9, { trade: "bakery", job: 100 }), 12900, 2, { tpl: "late", travel: 3000 }).slot === "R", "other trades keep the walk-home rule");
}

// ------------------------------------------------------------------------------------------------ 5. hiring: town posts -> the inn's cover -> shops
{
  const base = (o) => ({ day: 200, fed: 1, paid: true, seed: 3, sanitation: 1, foodDays: 5, levels: new Map(), ...o });
  const P = PEOPLE.newPeople();
  const keeper = PEOPLE.newPerson(P, 200, { home: 50, job: 50, trade: "inn", age: 40, seed: 9 }); keeper.keeper = true;
  const folk = [1, 2, 3, 4, 5].map((i) => PEOPLE.newPerson(P, 200, { home: 1, age: 30 + i, seed: 10 + i }));
  const jobs = [{ id: 101, kind: "bakery", vacancies: 5, x: 2, z: 0 }, { id: 50, kind: "inn", vacancies: 4, x: 120, z: 0 },
                { id: "watch", kind: "watch", vacancies: 1, x: 300, z: 0 }];
  PEOPLE.dayStep(P, base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }, { id: 50, room: 0, x: 120, z: 0 }], jobs }));
  const by = (j) => folk.filter((q) => q.job === j).length;
  ok(by("watch") === 1, "the watch (a town post) is filled first, though farthest", folk.map((q) => q.job));
  ok(by(50) === 2, "then the inn's cover: 2 more beside the keeper (3 in all), though the bakery is nearer", folk.map((q) => q.job));
  ok(by(101) === 2, "then the shops (the bakery next door)", folk.map((q) => q.job));
  ok(jobs[1].vacancies === 2 && jobs[0].vacancies === 3 && jobs[2].vacancies === 0, "vacancies counted once each", jobs.map((j) => j.vacancies));
  ok(folk.filter((q) => q.job === 50).every((q) => q.trade === "inn"), "the inn's staff carry the trade 'inn'");
  // a full cover: the rest of the inn's stations are ordinary shop vacancies (nearest within the shop class)
  const P2 = PEOPLE.newPeople();
  for (const i of [1, 2, 3]) { const q = PEOPLE.newPerson(P2, 200, { home: 50, job: 50, trade: "inn", age: 40, seed: 30 + i }); if (i === 1) q.keeper = true; }
  const x = PEOPLE.newPerson(P2, 200, { home: 1, age: 33, seed: 44 });
  const jobs2 = [{ id: 101, kind: "bakery", vacancies: 1, x: 2, z: 0 }, { id: 50, kind: "inn", vacancies: 2, x: 120, z: 0 }];
  PEOPLE.dayStep(P2, base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }, { id: 50, room: 0, x: 120, z: 0 }], jobs: jobs2 }));
  ok(x.job === 101, "the inn already covered (3): the nearer bakery wins as before", x.job);
}

// ------------------------------------------------------------------------------------------------ 6. guests and the night's bill
{
  const P = PEOPLE.newPeople();
  const res = PEOPLE.newPerson(P, 200, { home: 50, job: 50, age: 40, seed: 1 });
  const h = [1, 2, 3, 4].map((i) => PEOPLE.newPerson(P, 200, { home: null, age: 30 + i, seed: 20 + i }));
  const housed = PEOPLE.newPerson(P, 200, { home: 1, age: 30, seed: 9 });
  const g = PEOPLE.innGuests(P.list, 4, 50);
  ok(g.length === 3 && !g.includes(res.id) && !g.includes(housed.id) && JSON.stringify(g) === JSON.stringify(h.slice(0, 3).map((q) => q.id)), "4 beds, 1 lives there: the 3 lowest-id homeless are tonight's guests", g);
  ok(PEOPLE.innGuests(P.list, 0, 50).length === 0 && PEOPLE.innGuests([], 4, 50).length === 0, "no beds / nobody: no guests");
  h[0].alive = false;
  ok(PEOPLE.innGuests(P.list, 4, 50).length === 3 && !PEOPLE.innGuests(P.list, 4, 50).includes(h[0].id), "the dead are no guests");
  ok(JSON.stringify(PEOPLE.lodgeBill(3, 1000)) === JSON.stringify({ n: 3, price: 3 * INN24.bedP, paid: 3 * INN24.bedP }), "three guests pay three beds from the purse", PEOPLE.lodgeBill(3, 1000));
  ok(PEOPLE.lodgeBill(3, 10).paid === 10 && PEOPLE.lodgeBill(0, 1000).paid === 0 && PEOPLE.lodgeBill(2, -5).paid === 0, "a short purse pays what it holds; never negative");
  ok(INN24.bedP > 0 && INN24.bedP < 36, "a bed costs less than a day's food (RATION_P 36)", INN24.bedP);
}

// ------------------------------------------------------------------------------------------------ 7. the shop module (engine stub)
{
  const SHOP = await import("../pw_civ_shop.js");
  const ECON = await import("../pw_civ_economy.js");
  SHOP.initShops({ PEOPLE, ECON, short: (b) => b.kind, save: () => {}, load: () => ({ simDays: 300, buildings: [], settlements: [] }) });
  const P = PEOPLE.newPeople();
  const k = PEOPLE.newPerson(P, 200, { home: 60, job: 60, trade: "inn", age: 40, seed: 1, name: "Sven" }); k.keeper = true;
  const n1 = PEOPLE.newPerson(P, 200, { home: 1, job: 60, trade: "inn", age: 35, seed: 2, name: "Hilda" });
  const n2 = PEOPLE.newPerson(P, 200, { home: 1, job: 60, trade: "inn", age: 33, seed: 3, name: "Orla" });
  const hl = [1, 2, 3].map((i) => PEOPLE.newPerson(P, 200, { home: null, age: 30 + i, seed: 40 + i }));
  const st = { id: 1, seed: 7, people: P, log: [], ledger: ECON.newLedger() };
  st.ledger.purse = 1000;
  const inn = { id: 60, kind: "inn" };
  const def = { dir: [0, 2, 4, 6].flatMap((x) => [[x, 1, 0, "minecraft:bed"], [x, 1, 1, "minecraft:bed"]]) };
  // the witnessed hour: 17:30 (tod 11500), daylight — the day keeper's relief, the evening shift, is serving
  const a = SHOP.innNow(st, inn, 11500, 1, 300);
  ok(a.on.length >= 1 && a.staff.length === 3, "shop: at 17:30 (the witnessed daylight hour) the inn is OPEN", a.on.map((q) => q.name));
  ok(a.on.some((q) => q.name === "Orla") && a.rota.get(k.id) === "inn_day", "shop: the keeper keeps the day, the evening staffer serves at 17:30", [...a.rota]);
  for (const tod of [0, 3000, 6000, 9000, 12000, 15000, 18000, 21000, 23950]) ok(SHOP.innNow(st, inn, tod, 2, 300).on.length >= 1, `shop: open at tod ${tod}`);
  const solo = { ...st, people: { ...P, list: [k] } };
  const sn = SHOP.innNow(solo, inn, 18000, 2, 300);
  ok(sn.on.length === 0 && sn.next === 6000, "shop: a lone keeper at midnight: closed, opens at 06:00", sn);
  // the night's bill: 4 beds, 1 resident (the keeper) -> 3 guests x bedP from the purse into the inn's till
  const r0 = SHOP.innNight(st, inn, def, 1, 11000, 300);
  ok(r0 === null && st.ledger.purse === 1000, "shop: before dusk nothing is billed");
  const r = SHOP.innNight(st, inn, def, 1, 12500, 300);
  ok(r && r.guests.length === 3 && st.ledger.purse === 1000 - 3 * PEOPLE.INN24.bedP && st.ledger.tills[60] === 3 * PEOPLE.INN24.bedP, "shop: three guests pay their beds (purse -> the inn's till)", { purse: st.ledger.purse, till: st.ledger.tills[60] });
  ok(SHOP.innNight(st, inn, def, 1, 20000, 300) === null && st.ledger.purse === 1000 - 3 * PEOPLE.INN24.bedP, "shop: once a night only");
  ok(st.innNight === 1 && st.log.some((l) => /slept at the inn/.test(l)), "shop: the night is marked and told in the chronicle", st.log);
  void hl; void n1; void n2;
}

console.log(`test_inn24: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
