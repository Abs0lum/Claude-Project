// test_homes.mjs — 1.3.232 (#29): FAMILY ROOM (his 04:12 CT 10-07: "[the cottages and initial homes] just seemed small to me
// for a family of 4"; resizing allowed). Pure census law + the clock's homes context, node-tested.
// 0 MEASURE: the starter homes' beds (from the shipped templates) and places (the clock's HOUSEHOLD x DENSITY); his sleeping
//   law (the palace's: a double bed sleeps COURT.sleepers = 2, "the children's bed sleeps two") -> only the large cottage
//   sleeps a family of 4.
// 1 familyOf: the parents and their dependants at home (under moveOutAge, unmarried) — never a married child, never a grown one.
// 2 sleeps(): beds x 2 cover the family plus whoever already lives there; the inn's beds are guest beds (never a family's).
// 3 dayStep MOVE: a family whose home's beds cannot sleep it takes a free home that does — classes kept in order: sleeps,
//   then the best level it affords, then an empty house before a shared one, then nearest work; never past COMMUTE.far from
//   work; never the inn; at most FAMILY.perDay a town a day (the most short of beds first); deeds and restorations as HD.
// 4 dayStep SWAP: no free home sleeps it -> the family exchanges homes with a smaller household living alone in a home whose
//   beds sleep the family, when the family's old beds sleep that household, both sets of places hold them, the family affords
//   the level and nobody's rank falls; no deeds (an exchange inside the one purse); both homes are queued for restoration.
// 5 kill switch, result counts, no beds known -> nothing happens (old callers unchanged).
// 6 the clock: homeRoom carries each home's kind and beds (cut from pw_civ_clock.js, run on stand-ins); familyCensus for
//   /scriptevent pw:clock homes.
// 7 SIMULATION (the real dayStep over a growing town, the clock's HOUSEHOLD / DENSITY / TIER_ADDS read from its source): the
//   families of 4 that sleep in their beds rise, the population holds.
import { readFileSync } from "node:fs";
import * as PEOPLE from "../pw_civ_people.js";
import * as ECON from "../pw_civ_economy.js";
import { CIV_BUILDINGS } from "../pw_civ_buildings.js";
import { COURT } from "../pw_civ_court.js";
let pass = 0, fail = 0;
const ok = (c, m, extra) => { if (c) pass++; else { fail++; console.log("FAIL", m, extra === undefined ? "" : JSON.stringify(extra)); } };
const { DIALS, HOUSING } = PEOPLE;
const FAMILY = PEOPLE.FAMILY || {};
const D = 300;

function mk(P, o = {}) {
  const p = PEOPLE.newPerson(P, D, { age: o.age ?? 40, home: o.home ?? null, sex: o.sex || "m", parents: o.parents ? o.parents.map((q) => q.id) : [], job: o.job ?? null, trade: o.trade ?? null, seed: P.next });
  for (const q of o.parents || []) q.kids.push(p.id);
  if (o.skill) p.skill = { ...o.skill };
  return p;
}
const wed = (a, b) => { a.spouse = b.id; b.spouse = a.id; };
/** a family of 4 at `home`: father (job 101) + mother (job 102) + two small children */
function fam4(P, home, o = {}) {
  const fa = mk(P, { age: 40, home, job: o.jobs === false ? null : 101, trade: "smithy" });
  const mo = mk(P, { age: 38, home, sex: "f", job: o.jobs === false || o.oneEarner ? null : 102, trade: "bakery" });
  wed(fa, mo);
  const k1 = mk(P, { age: 5, home, parents: [fa, mo] }), k2 = mk(P, { age: 3, home, sex: "f", parents: [fa, mo] });
  return { fa, mo, k1, k2, all: [fa, mo, k1, k2] };
}
function cx(o = {}) {
  const homes = o.homes || [];
  return { day: o.day ?? D, fed: 1, paid: true, homes, jobs: o.jobs || [{ id: 101, kind: "smithy", vacancies: 0, x: 0, z: 0 }, { id: 102, kind: "bakery", vacancies: 0, x: 0, z: 0 }],
           seed: o.seed ?? 7, levels: o.levels || new Map(homes.map((h) => [h.id, h.lvl ?? 1])), foodDays: 15, wageOf: o.wageOf || (() => 72), health: 0 };
}
const ledger = (o = {}) => { const L = ECON.newLedger(); L.treasury = o.treasury ?? 100000; L.purse = o.purse ?? 100000; L.minted = L.treasury + L.purse; return L; };
const money = (L) => L.treasury + L.purse + Object.values(L.tills).reduce((a, v) => a + v, 0);
const homeOf = (q) => q.home;

// ------------------------------------------------------------------------------------------------ 0. measure
const clk = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
const grab = (re) => { const m = clk.match(re); if (!m) throw new Error(`not in the clock: ${re}`); return m[1]; };
const HOUSEHOLD = Function(`return ${grab(/const HOUSEHOLD = (\{[^}]*\});/)}`)();
const DENSITY = JSON.parse(grab(/const DENSITY = (\[[^\]]*\]);/));
{
  const bedsOf = (stem) => PEOPLE.bedsOf((CIV_BUILDINGS[`pw:mvv_${stem}_r1`] || {}).dir);
  const skins = ["a", "b", "c", "d"];
  ok(skins.every((k) => bedsOf(`cottage_s_${k}`) === 1) && skins.every((k) => bedsOf(`cottage_m_${k}`) === 1) && skins.every((k) => bedsOf(`cottage_l_${k}`) === 2),
     "measure: beds per starter home (every skin) — cottage_s 1, cottage_m 1, cottage_l 2", skins.map((k) => [bedsOf(`cottage_s_${k}`), bedsOf(`cottage_m_${k}`), bedsOf(`cottage_l_${k}`)]));
  ok(bedsOf("farm_cattle_a") === 0 && bedsOf("farm_wheat_a") === 1 && bedsOf("manor_a") === 11 && bedsOf("inn_a") === 4
     && PEOPLE.bedsOf((CIV_BUILDINGS["pw:mvv_inn_a_r2"] || {}).dir) === 32,   // 1.3.232 merge: r1 inn kept (4 beds), new inns = r2 (32)
     "measure: farm_cattle 0, farm_wheat 1, manor 11, inn r1 4 / r2 32 (guest beds)");
  ok(HOUSEHOLD.cottage_s === 2 && HOUSEHOLD.cottage_m === 2 && HOUSEHOLD.cottage_l === 3 && JSON.stringify(DENSITY) === "[1,1.5,3,6,10]",
     "measure: places = HOUSEHOLD x DENSITY (village 2 / 2 / 3; unchanged by this round)", [HOUSEHOLD, DENSITY]);
  ok(FAMILY.perBed === COURT.sleepers && FAMILY.perBed === 2, "his sleeping law: a bed sleeps two (the palace's COURT.sleepers; 'the children's bed sleeps two')", FAMILY.perBed);
  const sleep4 = ["cottage_s_a", "cottage_m_a", "cottage_l_a"].filter((st) => PEOPLE.sleeps && PEOPLE.sleeps({ beds: bedsOf(st), kind: st.slice(0, -2) }, 4));
  ok(sleep4.length === 1 && sleep4[0] === "cottage_l_a", "measure: of the starter homes only the large cottage sleeps a family of 4 (cottage_s / cottage_m sleep a couple)", sleep4);
}

// ------------------------------------------------------------------------------------------------ 1. familyOf
{
  const P = PEOPLE.newPeople();
  const { fa, mo, k1, k2 } = fam4(P, 1);
  const app = mk(P, { age: 15, home: 1, parents: [fa, mo] });                        // an apprentice: a dependant
  const s22 = mk(P, { age: 22, home: 1, parents: [fa, mo] });                        // grown, unmarried, under moveOutAge
  const d23 = mk(P, { age: 23, home: 1, sex: "f", parents: [fa, mo] });              // married: her own household
  const sil = mk(P, { age: 24, home: 1 }); wed(d23, sil);
  const s30 = mk(P, { age: 30, home: 1, parents: [fa, mo] });                        // grown (>= moveOutAge): moves out on his own
  const away = mk(P, { age: 6, home: 9, parents: [fa, mo] });                        // a child living elsewhere
  const F = typeof PEOPLE.familyOf === "function" ? PEOPLE.familyOf(P, fa, D) : [];
  const ids = new Set(F.map((q) => q.id));
  ok(F.length === 6 && [fa, mo, k1, k2, app, s22].every((q) => ids.has(q.id)), "familyOf: the parents, the children, the apprentice, the unmarried son under moveOutAge", F.map((q) => q.name));
  ok(!ids.has(d23.id) && !ids.has(sil.id) && !ids.has(s30.id) && !ids.has(away.id), "familyOf: never a married child (nor her husband), a grown son, a child living elsewhere");
  const Fm = typeof PEOPLE.familyOf === "function" ? PEOPLE.familyOf(P, mo, D) : [];
  ok(Fm.length === 6, "familyOf: the same family from the mother");
  const P2 = PEOPLE.newPeople();
  const wid = mk(P2, { age: 50, home: 3, sex: "f" }), kid = mk(P2, { age: 4, home: 3, parents: [wid] });
  ok(typeof PEOPLE.familyOf === "function" && PEOPLE.familyOf(P2, wid, D).length === 2 && PEOPLE.familyOf(P2, kid, D).length === 1, "familyOf: a widow and her child; a child alone is no family head");
}

// ------------------------------------------------------------------------------------------------ 2. sleeps
{
  const s = PEOPLE.sleeps || (() => null);
  ok(s({ beds: 2 }, 4) === true && s({ beds: 2 }, 4, 1) === false && s({ beds: 1 }, 2) === true && s({ beds: 1 }, 3) === false,
     "sleeps: two to a bed, counting whoever already lives there");
  ok(s({ beds: 32, kind: "inn" }, 4) === false && s({ beds: 0 }, 1) === false && s({ room: 9 }, 2) === false, "sleeps: never the inn's guest beds; no beds or unknown beds sleep nobody");
}

// ------------------------------------------------------------------------------------------------ 3. dayStep: MOVE
{
  // a family of 4 in a 1-bed cottage (#1, crowded) — #2 a free 2-bed home -> they move, all of them; deeds + restorations
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  const homes = [{ id: 1, room: 0, over: 2, beds: 1, kind: "cottage_s", x: 0, z: 0, lvl: 1 }, { id: 2, room: 4, beds: 2, kind: "cottage_l", x: 10, z: 0, lvl: 2 }];
  const r = PEOPLE.dayStep(P, cx({ homes }));
  ok(f.all.every((q) => q.home === 2), "move: the whole family of 4 takes the free home whose beds sleep it", f.all.map(homeOf));
  ok(r.events.some((e) => e.kind === "moved" && /family of 4/.test(e.text) && e.people.length === 4), "move: a 'moved' event names the family of 4", r.events.map((e) => e.text));
  ok((r.deeds || []).some((d) => d.kind === "buy" && d.home === 2 && d.price === HOUSING.price[2]) && (r.deeds || []).some((d) => d.kind === "sell" && d.home === 1 && d.price === HOUSING.price[1]),
     "move: they buy the new home (its level's price) and sell the old one they left empty", r.deeds);
  ok((r.restore || []).includes(1) && (r.restore || []).includes(2), "move: both homes are queued for restoration (his 21:47 law)", r.restore);
  ok(homes[1].room === 0 && homes[0].room === 2 && !homes[0].over, "move: the places follow (new 0 free, old 2 free, no longer over)", homes);
  ok(r.family && r.family.moved === 1 && r.family.swapped === 0, "move: the result counts it", r.family);
  // money: the shared purse pays the difference to the treasury; nothing created
  const L = ledger(); const m0 = money(L);
  PEOPLE.settleDeeds(L, r.deeds);
  ok(money(L) === m0 && L.treasury === 100000 + HOUSING.price[2] - HOUSING.price[1], "move: money conserved (purse -> treasury the difference)", [money(L), m0, L.treasury]);
}
{
  // CLASS ORDER: sleeping before nearest — #2 (1 bed, beside the work) vs #3 (2 beds, far but within COMMUTE.far)
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 2, beds: 1, x: 0, z: 0 }, { id: 2, room: 4, beds: 1, x: 1, z: 0 }, { id: 3, room: 4, beds: 2, x: 100, z: 0, lvl: 2 }] }));
  ok(f.all.every((q) => q.home === 3), "class: a home that sleeps the family beats a nearer one that does not", f.all.map(homeOf));
}
{
  // within the sleeping class: the best level they afford, then an empty house before a shared one, then nearest work
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  const lodger = mk(P, { age: 50, home: 4 });
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 2, beds: 1, x: 0, z: 0 }, { id: 2, room: 4, beds: 2, x: 5, z: 0, lvl: 1 }, { id: 3, room: 4, beds: 2, x: 60, z: 0, lvl: 2 },
    { id: 4, room: 5, beds: 3, x: 3, z: 0, lvl: 2 }, { id: 5, room: 4, beds: 2, x: 40, z: 0, lvl: 2 }] }));
  ok(f.all.every((q) => q.home === 5) && lodger.home === 4, "class: best affordable level (2), an empty house (#3/#5) before the shared #4, then the nearer (#5)", f.all.map(homeOf));
}
{
  // AFFORD: one earner (72 a day x 20 = 1440) cannot buy the level-2 home; no swap partner -> they stay
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1, { oneEarner: true });
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 2, beds: 1, x: 0, z: 0 }, { id: 3, room: 4, beds: 2, x: 20, z: 0, lvl: 2 }] }));
  ok(f.all.every((q) => q.home === 1) && !(r.deeds || []).length, "afford: a home above the family's means is never taken", f.all.map(homeOf));
}
{
  // FAR: a sleeping home farther than COMMUTE.far from the father's work is not taken (the far rule would send them back)
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 2, beds: 1, x: 0, z: 0 }, { id: 3, room: 4, beds: 2, x: PEOPLE.COMMUTE.far + 40, z: 0, lvl: 2 }] }));
  ok(f.all.every((q) => q.home === 1), "far: never a home past COMMUTE.far from work", f.all.map(homeOf));
}
{
  // INN: a free inn with 32 guest beds and room is never a family's home
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 2, beds: 1, x: 0, z: 0 }, { id: 7, room: 6, beds: 32, kind: "inn", x: 5, z: 0, lvl: 2 }] }));
  ok(f.all.every((q) => q.home === 1), "inn: the guest beds are never a family's", f.all.map(homeOf));
}
{
  // PER DAY: three families short of beds, three free 2-bed homes -> FAMILY.perDay move, the most short of beds first
  const P = PEOPLE.newPeople();
  const a = fam4(P, 1), b = fam4(P, 2), c = fam4(P, 3);
  const extra = mk(P, { age: 2, home: 2, parents: [b.fa, b.mo] });                   // family b: 5 (the most short)
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 2, beds: 1, x: 0, z: 0 }, { id: 2, room: 0, over: 3, beds: 1, x: 0, z: 1 }, { id: 3, room: 0, over: 2, beds: 1, x: 0, z: 2 },
    { id: 11, room: 6, beds: 3, x: 9, z: 0, lvl: 2 }, { id: 12, room: 6, beds: 3, x: 9, z: 1, lvl: 2 }, { id: 13, room: 6, beds: 3, x: 9, z: 2, lvl: 2 }] }));
  const moved = [a, b, c].filter((x) => x.fa.home !== x.k1.home || x.fa.home > 10).length;
  ok(r.family && r.family.moved === FAMILY.perDay && moved === FAMILY.perDay, "per day: at most FAMILY.perDay families", [r.family, moved]);
  ok(b.fa.home > 10 && extra.home === b.fa.home && a.fa.home > 10 && c.fa.home === 3, "per day: the most short of beds first (5 in 1 bed), then by id", [a.fa.home, b.fa.home, c.fa.home]);
}
{
  // NO FAMILY: three grown strangers in a 1-bed home -> nobody moves by this rule
  const P = PEOPLE.newPeople();
  const xs = [mk(P, { age: 40, home: 1 }), mk(P, { age: 41, home: 1 }), mk(P, { age: 42, home: 1 })];
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 1, beds: 1, x: 0, z: 0 }, { id: 2, room: 4, beds: 2, x: 9, z: 0 }] }));
  ok(xs.every((q) => q.home === 1) && (!r.family || r.family.moved === 0), "no family: unrelated adults are not moved by the family rule", xs.map(homeOf));
}
{
  // STRANGERS DO NOT TRIGGER: a family of 3 sleeps in its 2 beds; a lodger shares the house (4 residents) -> no move
  const P = PEOPLE.newPeople();
  const fa = mk(P, { age: 40, home: 1, job: 101 }), mo = mk(P, { age: 38, home: 1, sex: "f", job: 102 }); wed(fa, mo);
  const k = mk(P, { age: 4, home: 1, parents: [fa, mo] });
  const lod = mk(P, { age: 33, home: 1 });
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, beds: 2, x: 0, z: 0 }, { id: 2, room: 4, beds: 2, x: 9, z: 0, lvl: 2 }] }));
  ok([fa, mo, k, lod].every((q) => q.home === 1), "own need: a family that sleeps in its beds stays, whoever else lives there", [fa, mo, k, lod].map(homeOf));
}
{
  // NOBODY SPLIT: the married daughter and her husband stay; the family (with its apprentice) moves whole
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  const app = mk(P, { age: 15, home: 1, parents: [f.fa, f.mo] });
  const d23 = mk(P, { age: 23, home: 1, sex: "f", parents: [f.fa, f.mo] }), sil = mk(P, { age: 24, home: 1 }); wed(d23, sil);
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 5, beds: 1, x: 0, z: 0 }, { id: 2, room: 6, beds: 3, x: 9, z: 0, lvl: 2 }] }));
  ok([...f.all, app].every((q) => q.home === 2) && d23.home === 1 && sil.home === 1, "split: the family of 5 moves whole; the married daughter's household stays", [...f.all, app, d23, sil].map(homeOf));
}

// ------------------------------------------------------------------------------------------------ 4. dayStep: SWAP
{
  // the family of 4 alone in a 1-bed cottage; a widower alone in a 2-bed cottage (town tier: 5 places); no free home sleeps
  // the family -> they exchange homes
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  const wid = mk(P, { age: 70, home: 2 });
  const homes = [{ id: 1, room: 0, over: 2, beds: 1, kind: "cottage_s", x: 0, z: 0, lvl: 1 }, { id: 2, room: 4, beds: 2, kind: "cottage_l", x: 20, z: 0, lvl: 2 }];
  const r = PEOPLE.dayStep(P, cx({ homes }));
  ok(f.all.every((q) => q.home === 2) && wid.home === 1, "swap: the family takes the 2-bed home, the widower the cottage", [f.all.map(homeOf), wid.home]);
  ok(r.events.some((e) => e.kind === "moved" && /exchanged homes/.test(e.text)), "swap: the chronicle tells the exchange", r.events.map((e) => e.text));
  ok(!(r.deeds || []).length && (r.restore || []).includes(1) && (r.restore || []).includes(2), "swap: no deeds (an exchange inside the one purse); both homes queued for restoration", [r.deeds, r.restore]);
  ok(homes[0].room === 1 && !homes[0].over && homes[1].room === 1 && !homes[1].over, "swap: the places follow (#1 holds 1 of 2, #2 holds 4 of 5)", homes);
  ok(r.family && r.family.swapped === 1 && r.family.moved === 0, "swap: the result counts it", r.family);
}
{
  // the partner: a household that cannot grow first (a young couple would soon be short in the 1-bed house), then the smallest
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  const yh = mk(P, { age: 30, home: 2 }), yw = mk(P, { age: 28, home: 2, sex: "f" }); wed(yh, yw);   // may still have children
  const wid = mk(P, { age: DIALS.fertile + 12, home: 3 }), wif = mk(P, { age: DIALS.fertile + 10, home: 3, sex: "f" }); wed(wid, wif); // past DIALS.fertile
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 2, beds: 1, x: 0, z: 0 }, { id: 2, room: 3, beds: 2, x: 10, z: 0, lvl: 2 }, { id: 3, room: 3, beds: 2, x: 120, z: 0, lvl: 2 }] }));
  ok(f.all.every((q) => q.home === 3) && wid.home === 1 && yh.home === 2, "swap: the old couple (cannot grow) before the nearer young couple", [f.all.map(homeOf), wid.home, yh.home]);
}
{
  // a free home that sleeps the family comes before a swap
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  const wid = mk(P, { age: 70, home: 2 });
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 2, beds: 1, x: 0, z: 0 }, { id: 2, room: 4, beds: 2, x: 20, z: 0, lvl: 2 }, { id: 3, room: 4, beds: 2, x: 90, z: 0, lvl: 2 }] }));
  ok(f.all.every((q) => q.home === 3) && wid.home === 2, "swap: a free home that sleeps the family first", [f.all.map(homeOf), wid.home]);
}
{
  // SWAP GUARDS
  const run = (o) => {
    const P = PEOPLE.newPeople();
    const f = fam4(P, 1);
    if (o.famMaster) f.fa.skill = { smithy: 90 };                                    // a master smith, held back at level 1
    const extra = o.lodgerAt1 ? mk(P, { age: 30, home: 1 }) : null;
    const G = [];
    for (let i = 0; i < (o.gSize || 1); i++) G.push(mk(P, { age: 70 - i, home: 2, job: o.master ? 103 : null, trade: o.master ? "smithy" : null, skill: o.master ? { smithy: 90 } : undefined }));
    const homes = [{ id: 1, room: 0, over: extra ? 3 : 2, beds: o.beds1 ?? 1, x: 0, z: 0, lvl: 1 }, { id: 2, room: (o.cap2 ?? 5) - G.length, beds: o.beds2 ?? 2, kind: o.kind2, x: 20, z: 0, lvl: o.lvl2 ?? 2 }];
    PEOPLE.dayStep(P, cx({ homes, jobs: [{ id: 101, kind: "smithy", vacancies: 0, x: 0, z: 0 }, { id: 102, kind: "bakery", vacancies: 0, x: 0, z: 0 }, { id: 103, kind: "smithy", vacancies: 0, x: 0, z: 0 }], wageOf: o.wageOf }));
    return f.fa.home === 2;
  };
  ok(!run({ gSize: 4 }), "swap guard: the other household must be smaller than the family");
  ok(!run({ gSize: 3 }), "swap guard: the family's old beds must sleep the other household (1 bed sleeps 2, not 3)");
  ok(!run({ lodgerAt1: true }), "swap guard: the family must live alone in its home (a lodger stays put: no exchange)");
  ok(!run({ cap2: 3 }), "swap guard: the other home's places must hold the family (3 places < 4)");
  ok(!run({ beds2: 1 }), "swap guard: the other home's beds must sleep the family");
  ok(!run({ kind2: "inn", beds2: 32 }), "swap guard: never the inn");
  ok(!run({ lvl2: 4 }), "swap guard: the family must afford the other home's level");
  ok(!run({ master: true, wageOf: () => 200 }), "swap guard: the town's ranks at work never fall (a master smith keeps his level-2 house from a family with no master)");
  ok(run({ master: true, famMaster: true, wageOf: () => 200 }), "swap guard: a family whose master the 1-bed cottage holds back may exchange with a master (ranks at work: 1 + 2 -> 2 + 1)");
  ok(run({}), "swap guard: the plain case still swaps (control)");
}

// ------------------------------------------------------------------------------------------------ 5. switch, counts, old callers
{
  const P = PEOPLE.newPeople();
  const f = fam4(P, 1);
  const was = FAMILY.on;
  FAMILY.on = false;
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, over: 2, beds: 1, x: 0, z: 0 }, { id: 2, room: 4, beds: 2, x: 9, z: 0, lvl: 2 }] }));
  FAMILY.on = was;
  ok(was === true && f.all.every((q) => q.home === 1), "switch: FAMILY.on (default true) = false turns the rule off", [was, f.all.map(homeOf)]);
  const P2 = PEOPLE.newPeople();
  const g = fam4(P2, 1);
  const r2 = PEOPLE.dayStep(P2, cx({ homes: [{ id: 1, room: 0, over: 2, x: 0, z: 0 }, { id: 2, room: 4, x: 9, z: 0, lvl: 2 }] }));
  ok(g.all.every((q) => q.home === 1) && r2.family && r2.family.moved === 0 && r2.family.swapped === 0, "old callers: no beds in the homes context -> nothing moves (the rule needs beds)", g.all.map(homeOf));
}

// ------------------------------------------------------------------------------------------------ 6. the clock
{
  const cut = (name) => {
    const i = clk.indexOf(`function ${name}(`);
    if (i < 0) return null;
    let k = clk.indexOf("{", i), depth = 0, j = k;
    for (; j < clk.length; j++) { if (clk[j] === "{") depth++; else if (clk[j] === "}" && --depth === 0) break; }
    return clk.slice(i, j + 1);
  };
  const plots = [{ id: 1, family: "pw:mvv_cottage_l_a_r1", stage: 4 }, { id: 2, family: "pw:mvv_cottage_s_b_r1", stage: 4 }, { id: 3, family: "pw:mvv_inn_a_r1", stage: 4 }, { id: 4, family: "pw:mvv_bakery_a_r1", stage: 4 }];
  const short = (b) => CIV_BUILDINGS[b.family].stem.replace(/^mvv_/, "").replace(/_[a-z]_r1$/, "");
  const P = PEOPLE.newPeople(); mk(P, { home: 1 }); mk(P, { home: 1 });
  const env = { DENSITY, TIER_CLASS: () => 1, census: () => P, PEOPLE, plotsOf: () => plots, hhOf: (b) => HOUSEHOLD[short(b)] || 0, bedsOfFamily: (fam) => PEOPLE.bedsOf(CIV_BUILDINGS[fam].dir),
                placeOf: (b) => ({ x: b.id, y: 64, z: 0 }), short };
  const src = cut("homeRoom");
  const homeRoom = new Function(...Object.keys(env), `${src}; return homeRoom;`)(...Object.values(env));
  const H = homeRoom({}, { tier: "town" });
  const h1 = H.find((h) => h.id === 1), h2 = H.find((h) => h.id === 2), h3 = H.find((h) => h.id === 3);
  ok(H.length === 3 && !H.some((h) => h.id === 4), "clock homeRoom: the dwellings (a shop is no home)", H.map((h) => h.id));
  ok(h1.kind === "cottage_l" && h1.beds === 2 && h1.room === 3 && h2.kind === "cottage_s" && h2.beds === 1 && h3.kind === "inn",
     "clock homeRoom: each home carries its kind and beds (the inn's guest beds can be told apart)", H);
  ok(/cmd === "homes"/.test(clk), "clock: /scriptevent pw:clock homes exists");
  // familyCensus (what pw:clock homes prints): the families by size, those that sleep in their beds, those short of beds
  const Q = PEOPLE.newPeople();
  const a = fam4(Q, 1), b = fam4(Q, 2);
  const wid = mk(Q, { age: 50, home: 3, sex: "f" }); mk(Q, { age: 4, home: 3, parents: [wid] });
  const c = PEOPLE.familyCensus ? PEOPLE.familyCensus(Q, [{ id: 1, beds: 1 }, { id: 2, beds: 2 }, { id: 3, beds: 1 }], D) : null;
  ok(c && c.families === 3 && c.bySize[4] === 2 && c.bySize[2] === 1 && c.sleep === 2 && c.short === 1 && c.short4 === 1 && c.sleep4 === 1,
     "familyCensus: 3 families (two of 4, one of 2); 2 sleep in their beds, the family of 4 in the 1-bed home is short", c);
  ok(a && b, "familyCensus fixture");
}

// ------------------------------------------------------------------------------------------------ 7. simulation
{
  const TIER_ADDS = Function(`return ${grab(/const TIER_ADDS = (\{[\s\S]*?\n\});/)}`)();
  const TIER_DAYS = Function(`return ${grab(/const TIER_DAYS = (\{[^}]*\});/)}`)();
  const TIERS = Function(`return ${grab(/const TIERS = (\[[^\]]*\]);/)}`)();
  const cls = (tier) => tier === "capital" ? 4 : tier.startsWith("metropolis") ? 3 : tier.startsWith("city") ? 2 : tier.startsWith("town") ? 1 : 0;
  const bedsK = (k) => PEOPLE.bedsOf((CIV_BUILDINGS[`pw:mvv_${k}_a_r1`] || {}).dir);
  const sim = (seed, days, on) => {
    const was = FAMILY.on; FAMILY.on = on;
    const P = PEOPLE.newPeople(), homes = [];
    let nid = 1, tier = "village";
    const build = (kind, day) => {
      const h = { id: nid++, kind, x: (nid * 37) % 200, z: (nid * 53) % 200 }; homes.push(h);
      for (let i = 0; i < (HOUSEHOLD[kind] || 0); i++) { const hs = (h.id * 7 + i * 11 + seed) >>> 0; PEOPLE.newPerson(P, day, { home: h.id, seed: h.id * 31 + i * 7 + seed, age: i < 2 ? 20 + (hs % 40) : hs % 15, sex: i === 0 ? "m" : i === 1 ? "f" : undefined, parents: [] }); }
    };
    for (const k of ["farm_wheat", "cottage_s", "inn", "cottage_m", "cottage_l", "farm_cattle"]) build(k, 0);
    const pend = [];
    let fam4 = 0, fam4Sleep = 0;
    for (let day = 1; day <= days; day++) {
      const nx = TIERS[TIERS.indexOf(tier) + 1];
      if (nx && day >= TIER_DAYS[nx]) { tier = nx; for (const [k, n] of TIER_ADDS[tier]) if (HOUSEHOLD[k] !== undefined) for (let i = 0; i < n; i++) pend.push(k); }
      for (let i = 0; i < 2 && pend.length; i++) build(pend.shift(), day);
      const live = {}; for (const p of PEOPLE.alive(P)) if (p.home) live[p.home] = (live[p.home] || 0) + 1;
      const H = homes.map((h) => { const cap = Math.round((HOUSEHOLD[h.kind] || 0) * DENSITY[cls(tier)]); return { id: h.id, kind: h.kind, beds: bedsK(h.kind), room: Math.max(0, cap - (live[h.id] || 0)), over: Math.max(0, (live[h.id] || 0) - cap), x: h.x, z: h.z }; });
      const adults = PEOPLE.alive(P).filter((p) => PEOPLE.stage(p, day) !== "child").length, filled = PEOPLE.alive(P).filter((p) => p.job === "builders").length;
      PEOPLE.dayStep(P, { day, fed: 1, paid: true, homes: H, jobs: [{ id: "builders", kind: "builder", vacancies: Math.max(0, adults - filled) + 2, x: 100, z: 100 }], seed, name: "Sim", events: [], sanitation: 1, health: 0,
                          levels: new Map(homes.map((h) => [h.id, PEOPLE.homeLevel(h.kind)])), foodDays: 15, diet: 1, wageOf: () => 72 });
      const c = PEOPLE.familyCensus(P, homes.map((h) => ({ id: h.id, beds: bedsK(h.kind), kind: h.kind })), day);
      fam4 += c.bySize4plus; fam4Sleep += c.sleep4;
    }
    FAMILY.on = was;
    return { fam4, fam4Sleep, pop: PEOPLE.alive(P).length };
  };
  if (PEOPLE.familyCensus) {
    // four towns (seeds) to city I (260 days): one seed alone is noisy (a move changes who meets whom, so the births
    // differ); the sum is the measure. Measured 10-07 on 8 seeds: the share of family-of-4+ days spent in beds that sleep
    // the family rose from 13-31 % (mean 18.8) to 26-51 % (mean 38.4); population within 3 %.
    const res = [3, 7, 23, 59].map((seed) => ({ seed, off: sim(seed, 260, false), on: sim(seed, 260, true) }));
    const sum = (k, f) => res.reduce((a, x) => a + x[k][f], 0);
    const shareOff = sum("off", "fam4Sleep") / sum("off", "fam4"), shareOn = sum("on", "fam4Sleep") / sum("on", "fam4");
    ok(shareOn >= 2 * shareOff, `sim: the share of family-of-4+ days spent in beds that sleep the family at least doubles (${(100 * shareOff).toFixed(1)} % -> ${(100 * shareOn).toFixed(1)} %)`, res);
    for (const x of res) ok(Math.abs(x.on.pop - x.off.pop) <= 0.08 * x.off.pop, `sim seed ${x.seed}: the population holds (off ${x.off.pop}, on ${x.on.pop})`, x);
    console.log(`  sim: share ${(100 * shareOff).toFixed(1)} % -> ${(100 * shareOn).toFixed(1)} %; ${JSON.stringify(res)}`);
  } else ok(false, "sim: familyCensus missing");
}

console.log(`test_homes: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
