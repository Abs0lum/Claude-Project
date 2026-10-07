// test_households.mjs — 1.3.230 (HD): HOUSEHOLDS & DYNASTY (his 2026-10-06 21:39 / 21:47), census law, pure.
// 1 MOVE OUT AT ADULTHOOD: an adult still with a parent leaves whenever a free home exists (a dial of households a town a
//   day, crowded homes first), the BEST level the household can afford (tie: nearest work), a spouse goes along; the
//   moved-out household is its own household for births / crowding; an elder moves too; no free home: they stay.
// 2 DYNASTY: p.dyn from the father, else the mother; founders and newcomers are their own line (no field); the line's name
//   is registered on its first town-born child; a line with no living member ends; adopt() keeps lines among movers.
// 3 HOME SALES: the last resident dies and the heir lives elsewhere -> the heir sells (the town pays the price by level)
//   unless the house is better than the heir's: then the heir's household moves in and sells the old one (when it is left
//   empty). Spouse -> eldest child -> the line's kin -> the closest friend -> the town. Orphans, two heirs, no room.
// 4 RESTORE ON MOVE: every move out of / into a home queues a restoration (deduped, capped); the bill (materials + builder
//   wages) is paid by the treasury when it can (an empty treasury waits), the work takes its days, then it is done; a
//   household buying a free home pays the town (that replenishes the restoration); money is conserved.
// 5 the children of adult children: a town run long enough has a third generation born in the town.
// 6 the save: bytes per person of the new fields.
// 7 the clock's restoration day (restoreDaily, wageOfPerson cut from pw_civ_clock.js, run on stand-ins).
import { readFileSync } from "node:fs";
import * as PEOPLE from "../pw_civ_people.js";
import * as ECON from "../pw_civ_economy.js";
let pass = 0, fail = 0;
const ok = (c, m, extra) => { if (c) pass++; else { fail++; console.log("FAIL", m, extra === undefined ? "" : JSON.stringify(extra)); } };
const { HOUSING, DIALS } = PEOPLE;
const H = HOUSING;

const D = 300;                                                     // the test's day
/** a person of a given age (no friends: nobody marries by accident; no job unless given) */
function mk(P, o = {}) {
  const p = PEOPLE.newPerson(P, D, { age: o.age ?? 40, home: o.home ?? null, sex: o.sex || "m", parents: o.parents ? o.parents.map((q) => q.id) : [], job: o.job ?? null, trade: o.trade ?? null, seed: P.next });
  for (const q of o.parents || []) q.kids.push(p.id);
  if (o.dyn !== undefined) p.dyn = o.dyn;
  return p;
}
const wed = (a, b) => { a.spouse = b.id; b.spouse = a.id; };
/** a census day's context: homes [{id, room, over, x, z}], levels Map, no jobs unless given */
function cx(o = {}) {
  const homes = o.homes || [];
  return { day: o.day ?? D, fed: 1, paid: true, homes, jobs: o.jobs || [], seed: o.seed ?? 7, levels: o.levels || new Map(homes.map((h) => [h.id, h.lvl ?? 1])),
           foodDays: o.foodDays ?? 15, wageOf: o.wageOf, health: 0 };
}
const ledger = (o = {}) => { const L = ECON.newLedger(); L.treasury = o.treasury ?? 100000; L.purse = o.purse ?? 100000; L.minted = L.treasury + L.purse; for (const [g, n] of Object.entries(o.stock || { stone: 1000, planks: 1000 })) L.stock[g] = n; return L; };
const money = (L) => L.treasury + L.purse + Object.values(L.tills).reduce((a, v) => a + v, 0);

// ------------------------------------------------------------------------------------------------ 1. move out at adulthood
{
  // a grown son (25) with his parents in #1 (not crowded); #2 free -> he moves; the genealogy stays
  const P = PEOPLE.newPeople();
  const fa = mk(P, { age: 60, home: 1 }), mo = mk(P, { age: 58, home: 1, sex: "f" }); wed(fa, mo);
  const son = mk(P, { age: DIALS.moveOutAge, home: 1, parents: [fa, mo] });
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 1, x: 0, z: 0 }, { id: 2, room: 2, x: 10, z: 0 }] }));
  ok(son.home === 2, "an adult (moveOutAge) with his parents moves out when a free home exists (not only when crowded)", son.home);
  ok(fa.home === 1 && mo.home === 1, "the parents stay");
  ok(son.parents.includes(fa.id) && fa.kids.includes(son.id), "the genealogy stays (parents / kids arrays)");
  ok(r.events.some((e) => e.kind === "moved" && e.people.includes(son.id)), "a 'moved' event");
  ok(Array.isArray(r.restore) && r.restore.includes(1) && r.restore.includes(2), "both homes (out of and into) are queued for restoration", r.restore);
  ok(Array.isArray(r.deeds) && r.deeds.some((d) => d.kind === "buy" && d.home === 2 && d.price === H.price[1] * H.buyShare), "the household buys the free home at its level's price", r.deeds);
  ok(!PEOPLE.household(P, fa, D).includes(son), "the grown son is no longer in his parents' household");
}
{
  // a day younger than moveOutAge: stays; no free home: stays
  const P = PEOPLE.newPeople();
  const fa = mk(P, { age: 60, home: 1 });
  const kid = mk(P, { age: DIALS.moveOutAge - 1, home: 1, parents: [fa] });
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0 }, { id: 2, room: 2 }] }));
  ok(kid.home === 1, "below moveOutAge: stays");
  const P2 = PEOPLE.newPeople();
  const f2 = mk(P2, { age: 60, home: 1 });
  const s2 = mk(P2, { age: 30, home: 1, parents: [f2] });
  const r2 = PEOPLE.dayStep(P2, cx({ homes: [{ id: 1, room: 0 }] }));
  ok(s2.home === 1 && !(r2.deeds || []).length && !(r2.restore || []).length, "no free home: stays, no deed, nothing queued", r2.restore);
  const P3 = PEOPLE.newPeople();
  const f3 = mk(P3, { age: 60, home: 1 }), mo3 = mk(P3, { age: 60, home: 1, sex: "f" });
  const s3 = mk(P3, { age: 30, home: 1, parents: [f3] }), w3 = mk(P3, { age: 30, home: 1, sex: "f" }); wed(s3, w3);
  PEOPLE.dayStep(P3, cx({ homes: [{ id: 1, room: 0 }, { id: 2, room: 1 }] }));
  ok(s3.home === 1 && w3.home === 1, "a couple does not split for a home with one place", [s3.home, w3.home]);
}
{
  // the BEST level the household can afford: one earner at 150 p a day affords 150 x 20 = 3000 -> level 2 (2880), not 3
  const P = PEOPLE.newPeople();
  const fa = mk(P, { age: 70, home: 1 });
  const son = mk(P, { age: 30, home: 1, parents: [fa], job: 101, trade: "smithy" });
  const homes = [{ id: 1, room: 0, x: 0, z: 0 }, { id: 2, room: 2, x: 5, z: 0, lvl: 1 }, { id: 3, room: 2, x: 90, z: 0, lvl: 2 }, { id: 4, room: 2, x: 60, z: 0, lvl: 2 }, { id: 5, room: 2, x: 5, z: 5, lvl: 3 }];
  const jobs = [{ id: 101, kind: "smithy", vacancies: 0, x: 100, z: 0 }];
  const r = PEOPLE.dayStep(P, cx({ homes, jobs, wageOf: (p) => (p.job ? 150 : 0) }));
  ok(son.home === 3, "the best affordable level (2), the nearest to work of the two (#3 at 10 blocks, not #4 at 40), never level 3", son.home);
  ok(r.deeds.some((d) => d.kind === "buy" && d.home === 3 && d.lvl === 2 && d.price === H.price[2] * H.buyShare), "the deed: level 2's price", r.deeds);
  ok(PEOPLE.affordLevel(0) === H.minLevel && PEOPLE.affordLevel(150) === 2 && PEOPLE.affordLevel(10000) === H.price.length - 1, "affordLevel: the floor, 150 p -> 2, rich -> the top",
     [PEOPLE.affordLevel(0), PEOPLE.affordLevel(150), PEOPLE.affordLevel(10000)]);
  // jobless: the lowest level only
  const P2 = PEOPLE.newPeople();
  const f2 = mk(P2, { age: 70, home: 1 });
  const s2 = mk(P2, { age: 30, home: 1, parents: [f2] });
  PEOPLE.dayStep(P2, cx({ homes: [{ id: 1, room: 0 }, { id: 2, room: 2, lvl: 3 }, { id: 3, room: 2, lvl: 1 }] }));
  ok(s2.home === 3, "a jobless adult takes the open (lowest) level", s2.home);
  // nothing affordable (only a manor free): stays
  const P3 = PEOPLE.newPeople();
  const f3 = mk(P3, { age: 70, home: 1 });
  const s3 = mk(P3, { age: 30, home: 1, parents: [f3] });
  PEOPLE.dayStep(P3, cx({ homes: [{ id: 1, room: 0 }, { id: 2, room: 2, lvl: 4 }] }));
  ok(s3.home === 1, "only an unaffordable home free: stays", s3.home);
}
{
  // a spouse goes along: (a) living at the same parents' home, (b) living with her own parents in another house
  const P = PEOPLE.newPeople();
  const fa = mk(P, { age: 70, home: 1 });
  const son = mk(P, { age: 30, home: 1, parents: [fa] }), wife = mk(P, { age: 28, home: 1, sex: "f" }); wed(son, wife);
  const homes = [{ id: 1, room: 0 }, { id: 2, room: 2 }];
  PEOPLE.dayStep(P, cx({ homes, foodDays: 0 }));                         // foodDays 0: no birth today (a third mouth would not fit)
  ok(son.home === 2 && wife.home === 2, "(a) the wife at the same home goes along", [son.home, wife.home]);
  ok(homes[1].room === 0 && homes[0].room === 2, "rooms booked: #2 -2, #1 +2", homes.map((h) => h.room));
  const P2 = PEOPLE.newPeople();
  const f2 = mk(P2, { age: 70, home: 1 }), g2 = mk(P2, { age: 70, home: 5, sex: "f" });
  const s2 = mk(P2, { age: 30, home: 1, parents: [f2] }), w2 = mk(P2, { age: 28, home: 5, sex: "f", parents: [g2] }); wed(s2, w2);
  const h2 = [{ id: 1, room: 0 }, { id: 5, room: 0 }, { id: 2, room: 2 }];
  const r2 = PEOPLE.dayStep(P2, cx({ homes: h2, foodDays: 0 }));
  ok(s2.home === 2 && w2.home === 2, "(b) the wife living with her own parents goes along", [s2.home, w2.home]);
  ok(h2[1].room === 1 && r2.restore.includes(5), "(b) her parents' house gets her place back and is queued", [h2[1].room, r2.restore]);
}
{
  // the daily cap: 5 grown children, 5 free homes -> HOUSING.moveOutPerDay move; the crowded home first, then the eldest
  const P = PEOPLE.newPeople();
  const kids = [];
  for (let i = 0; i < 5; i++) { const f = mk(P, { age: 80, home: 10 + i }); kids.push(mk(P, { age: 30 + i, home: 10 + i, parents: [f] })); }
  const homes = [];
  for (let i = 0; i < 5; i++) homes.push({ id: 10 + i, room: 0, over: i === 0 ? 1 : 0 });
  for (let i = 0; i < 5; i++) homes.push({ id: 20 + i, room: 1 });
  PEOPLE.dayStep(P, cx({ homes }));
  const moved = kids.filter((k, i) => k.home !== 10 + i);
  ok(moved.length === H.moveOutPerDay, `at most ${H.moveOutPerDay} households a day`, moved.length);
  ok(kids[0].home >= 20, "the crowded home's child goes first (the youngest of the five)");
  ok(moved.slice(1).every((k) => k.born <= Math.min(...kids.filter((q, i) => q.home === 10 + i).map((q) => q.born))), "then the eldest", kids.map((k) => [k.born, k.home]));
  ok(moved.every((k) => k.home >= 20), "an empty home of the same level before a place in another family's house (#14 freed today)", kids.map((k) => k.home));
}
{
  // an elder still with a parent moves out as well
  const P = PEOPLE.newPeople();
  const fa = mk(P, { age: 129, home: 1 });
  const el = mk(P, { age: DIALS.elder + 1, home: 1, parents: [fa] });
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0 }, { id: 2, room: 1 }], seed: 3 }));
  ok(PEOPLE.stage(el, D) === "elder" && el.home === 2, "an elder with a parent moves out too", el.home);
}
{
  // own household for births: a moved-out daughter, married, has a child in her own home although her parents' home holds
  // BIRTH.kidsPerHome children (the crowding rule counts her new home only)
  const P = PEOPLE.newPeople();
  const fa = mk(P, { age: 60, home: 1 }), mo = mk(P, { age: 55, home: 1, sex: "f" }); wed(fa, mo);
  mk(P, { age: 2, home: 1, parents: [fa, mo] }); mk(P, { age: 3, home: 1, parents: [fa, mo] });
  const dau = mk(P, { age: 30, home: 2, sex: "f", parents: [fa, mo] }), hus = mk(P, { age: 31, home: 2 }); wed(dau, hus);
  dau.mood = hus.mood = 100;
  let born = 0;
  const homes = () => [{ id: 1, room: 0, over: 0 }, { id: 2, room: 2 }];
  for (let d = 0; d < 400 && !born; d++) { const r = PEOPLE.dayStep(P, cx({ day: D + d, homes: homes(), seed: 11 })); born = r.events.filter((e) => e.kind === "birth" && e.people.includes(dau.id)).length; dau.mood = hus.mood = 100; }
  ok(born > 0, "a grown, moved-out daughter has children in her own home (her parents' full nursery does not block her)");
}

// ------------------------------------------------------------------------------------------------ 2. dynasty
{
  const P = PEOPLE.newPeople();
  const gf = mk(P, { age: 90, home: 1 });
  ok(gf.dyn === undefined && PEOPLE.dynOf(gf) === gf.id, "a founder is his own line (no field stored)");
  const fa = mk(P, { age: 40, home: 2, parents: [gf] }); fa.dyn = PEOPLE.dynOf(gf);
  const mo = mk(P, { age: 30, home: 2, sex: "f" }); wed(fa, mo);
  ok(PEOPLE.birthLine(mo, fa) === gf.id, "a child's line is the father's (here the grandfather's line)");
  ok(PEOPLE.birthLine(mo, null) === mo.id, "no father: the mother's line");
  ok(PEOPLE.birthLine(mk(PEOPLE.newPeople(), { age: 30, sex: "f", dyn: 77 }), null) === 77, "no father, a town-born mother: her line");
  // a real birth stores dyn and registers the line's name
  fa.mood = mo.mood = 100;
  let baby = null;
  for (let d = 0; d < 400 && !baby; d++) {
    const r = PEOPLE.dayStep(P, cx({ day: D + d, homes: [{ id: 1, room: 1 }, { id: 2, room: 2 }], seed: 5 }));
    const e = r.events.find((x) => x.kind === "birth");
    if (e) { baby = P.list.find((q) => e.people.includes(q.id) && q !== mo && q !== fa); ok(/line of/.test(e.text), "the birth's chronicle names the line (the father is town-born)", e.text); }
    fa.mood = mo.mood = 100;
  }
  ok(baby && baby.dyn === gf.id, "a baby carries p.dyn = the father's line", baby && baby.dyn);
  ok(P.lines && P.lines[gf.id] === gf.name, "the line's name is registered", P.lines);
  // a newcomer (the faucet) is a founder: no dyn
  const n = PEOPLE.newPerson(P, D, { home: 1 });
  ok(n.dyn === undefined, "a newcomer has no dyn (his own line)");
  // adopt(): movers keep their lines among themselves; a mover whose line stays behind founds his own
  const Q = PEOPLE.newPeople();
  const got = PEOPLE.adopt(Q, [fa, mo, baby], D, 9);
  const [fa2, mo2, baby2] = got;
  ok(baby2.dyn === undefined || baby2.dyn === PEOPLE.dynOf(fa2), "adopt: the baby's line follows the moved father when he founds the line there", [baby2.dyn, fa2.id]);
  ok(fa2.dyn === undefined && PEOPLE.dynOf(baby2) === fa2.id, "adopt: the father (his line's founder stayed behind) founds it anew; the child's line is his", [fa2.dyn, baby2.dyn, fa2.id]);
}

// ------------------------------------------------------------------------------------------------ 3. inheritance and sales
/** the dead (age 160: dies today for certain) in #1 alone; returns the census and its people */
function estate(o = {}) {
  const P = PEOPLE.newPeople();
  const dead = mk(P, { age: 160, home: 1 });
  return { P, dead };
}
{
  // (a) the heir (eldest son) lives in a house as good: the heir SELLS; the town pays level 1's price
  const { P, dead } = estate();
  const son = mk(P, { age: 60, home: 2, parents: [dead] });
  const homes = [{ id: 1, room: 0, lvl: 1 }, { id: 2, room: 0, lvl: 1 }];
  const r = PEOPLE.dayStep(P, cx({ homes }));
  ok(!dead.alive, "(a) the old man died");
  ok(son.home === 2, "(a) the heir stays at home");
  const s = r.deeds.find((d) => d.kind === "sell");
  ok(s && s.home === 1 && s.pid === son.id && s.price === H.price[1] * H.sellShare, "(a) a sale deed: #1, the heir, level 1's price", r.deeds);
  ok(r.events.some((e) => e.kind === "sold" && e.people.includes(son.id)), "(a) a 'sold' event");
  ok(r.restore.includes(1), "(a) the sold house is queued for restoration");
  ok(homes[0].room === 1, "(a) the house is free for a newcomer", homes[0].room);
}
{
  // (b) the inherited house is BETTER: the heir's household (him, his wife, their child) moves in; the old house is sold
  const { P, dead } = estate();
  const son = mk(P, { age: 60, home: 2, parents: [dead] }), wife = mk(P, { age: 58, home: 2, sex: "f" }); wed(son, wife);
  const kid = mk(P, { age: 5, home: 2, parents: [son, wife] });
  const homes = [{ id: 1, room: 2, lvl: 3 }, { id: 2, room: 0, lvl: 1 }];
  const r = PEOPLE.dayStep(P, cx({ homes }));
  ok(son.home === 1 && wife.home === 1 && kid.home === 1, "(b) the household moves into the better inherited house", [son.home, wife.home, kid.home]);
  const s = r.deeds.find((d) => d.kind === "sell");
  ok(s && s.home === 2 && s.price === H.price[1] * H.sellShare, "(b) the OLD house (level 1) is sold", r.deeds);
  ok(!r.deeds.some((d) => d.kind === "buy"), "(b) nothing bought (the house is inherited)");
  ok(r.restore.includes(1) && r.restore.includes(2), "(b) both houses are queued", r.restore);
  ok(homes[0].room === 0 && homes[1].room === 3, "(b) rooms: #1 3 -> 0, #2 0 -> 3", homes.map((h) => h.room));
}
{
  // (c) better house, but the heir lived with his in-laws: they move in, the in-laws' house is NOT sold
  const { P, dead } = estate();
  const inlaw = mk(P, { age: 90, home: 2, sex: "f" });
  const son = mk(P, { age: 60, home: 2, parents: [dead] });
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 1, lvl: 2 }, { id: 2, room: 0, lvl: 1 }] }));
  ok(son.home === 1 && inlaw.home === 2 && !r.deeds.some((d) => d.kind === "sell"), "(c) the heir moves in; the house others still live in is not sold", r.deeds);
}
{
  // (d) not the last resident (the widow lives there): nothing sold; (e) a homeless heir moves in
  const P = PEOPLE.newPeople();
  const dead = mk(P, { age: 160, home: 1 }), wid = mk(P, { age: 100, home: 1, sex: "f" }); wed(dead, wid);
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0 }] }));
  ok(wid.home === 1 && !r.deeds.length, "(d) the widow keeps the house: no sale", r.deeds);
  const { P: P2, dead: d2 } = estate();
  const son = mk(P2, { age: 60, home: null, parents: [d2] });
  const r2 = PEOPLE.dayStep(P2, cx({ homes: [{ id: 1, room: 0, lvl: 1 }] }));
  ok(son.home === 1 && !r2.deeds.length, "(e) a homeless heir moves into the inherited house (nothing to sell)", [son.home, r2.deeds]);
}
{
  // (f) two heirs: the eldest child inherits (and sells); with the eldest dead, the next
  const { P, dead } = estate();
  const a = mk(P, { age: 70, home: 2, parents: [dead] }), b = mk(P, { age: 60, home: 3, parents: [dead] });
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0 }, { id: 2, room: 0 }, { id: 3, room: 0 }] }));
  ok(r.deeds.some((d) => d.kind === "sell" && d.pid === a.id) && !r.deeds.some((d) => d.pid === b.id), "(f) two heirs: the eldest sells", r.deeds);
  const { P: P2, dead: d2 } = estate();
  const a2 = mk(P2, { age: 70, home: 2, parents: [d2] }), b2 = mk(P2, { age: 60, home: 3, parents: [d2] });
  a2.alive = false; a2.died = D - 5;
  const r2 = PEOPLE.dayStep(P2, cx({ homes: [{ id: 1, room: 0 }, { id: 2, room: 1 }, { id: 3, room: 0 }] }));
  ok(r2.deeds.some((d) => d.kind === "sell" && d.pid === b2.id), "(f) the eldest dead: the next child", r2.deeds);
}
{
  // (g) orphans: both parents die; the child lives in the house -> it stays his (no sale), the shop does not go to a child
  const P = PEOPLE.newPeople();
  const fa = mk(P, { age: 160, home: 1, job: 50, trade: "bakery" }), mo = mk(P, { age: 160, home: 1, sex: "f" }); wed(fa, mo);
  const kid = mk(P, { age: 8, home: 1, parents: [fa, mo] });
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0 }], jobs: [{ id: 50, kind: "bakery", vacancies: 0 }] }));
  ok(!fa.alive && !mo.alive && kid.home === 1 && !r.deeds.length, "(g) an orphan living in the house keeps it", r.deeds);
  ok(kid.job === null, "(g) the shop does not pass to a child", kid.job);
  // (h) an orphan child living elsewhere (with his grandmother): the house is sold, the child does not move
  const P2 = PEOPLE.newPeople();
  const gm = mk(P2, { age: 100, home: 2, sex: "f" });
  const d2 = mk(P2, { age: 160, home: 1 });
  const k2 = mk(P2, { age: 6, home: 2, parents: [d2] });
  const r2 = PEOPLE.dayStep(P2, cx({ homes: [{ id: 1, room: 0, lvl: 3 }, { id: 2, room: 2, lvl: 1 }] }));
  ok(k2.home === 2 && gm.home === 2 && r2.deeds.some((d) => d.kind === "sell" && d.home === 1 && d.pid === k2.id), "(h) a child heir elsewhere: the better house is sold, the child stays", [k2.home, r2.deeds]);
}
{
  // (i) the line's kin before a friend: no spouse, no living child; a grandson of the same line inherits
  const P = PEOPLE.newPeople();
  const dead = mk(P, { age: 160, home: 1 });
  const son = mk(P, { age: 100, home: 2, parents: [dead] }); son.dyn = dead.id; son.alive = false; son.died = D - 3;
  const gs = mk(P, { age: 40, home: 3, parents: [son] }); gs.dyn = dead.id;
  const pal = mk(P, { age: 90, home: 4 }); dead.friends[pal.id] = 90; pal.friends[dead.id] = 90;
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0 }, { id: 3, room: 0 }, { id: 4, room: 0 }] }));
  const inh = r.events.find((e) => e.kind === "inherit");
  ok(inh && inh.heir === gs.id, "(i) the line's kin (a grandson) inherits before the closest friend", inh);
  ok(r.deeds.some((d) => d.kind === "sell" && d.pid === gs.id), "(i) and sells", r.deeds);
}
{
  // (j) a line with no living members ends (its registered name goes); no friend -> the town takes it (escheat): queued,
  // no deed (nobody is paid)
  const P = PEOPLE.newPeople();
  const dead = mk(P, { age: 160, home: 1 });
  P.lines = { [dead.id]: dead.name };
  const son = mk(P, { age: 100, home: 2, parents: [dead] }); son.dyn = dead.id; son.alive = false; son.died = D - 3;
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0 }] }));
  ok(r.events.some((e) => e.kind === "escheat"), "(j) no heir: the town takes the house");
  ok(r.events.some((e) => e.kind === "line" && e.people.includes(dead.id)), "(j) the line's end is told", r.events.map((e) => e.kind));
  ok(!(dead.id in (P.lines || {})), "(j) the ended line leaves the register", P.lines);
  ok(!r.deeds.length && r.restore.includes(1), "(j) escheat: no deed, the house is queued for restoration", [r.deeds, r.restore]);
}
{
  // (k) the better house is too small for the heir's household (2 people, 1 place free after the death): sold instead
  const { P, dead } = estate();
  const son = mk(P, { age: 60, home: 2, parents: [dead] }), wife = mk(P, { age: 58, home: 2, sex: "f" }); wed(son, wife);
  const r = PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 0, lvl: 3 }, { id: 2, room: 0, lvl: 1 }] }));
  ok(son.home === 2 && r.deeds.some((d) => d.kind === "sell" && d.home === 1 && d.price === H.price[3] * H.sellShare), "(k) no room for the household: the better house is sold", r.deeds);
}
{
  // (l) an elder heir moves into the better house with his wife
  const { P, dead } = estate();
  const el = mk(P, { age: DIALS.elder + 2, home: 2, parents: [dead] }), w = mk(P, { age: DIALS.elder, home: 2, sex: "f" }); wed(el, w);
  PEOPLE.dayStep(P, cx({ homes: [{ id: 1, room: 1, lvl: 2 }, { id: 2, room: 0, lvl: 1 }], seed: 2 }));
  ok(el.home === 1 && w.home === 1, "(l) an elder heir's household moves into the better house", [el.home, w.home]);
}

// ------------------------------------------------------------------------------------------------ 4. restoration and money
{
  const b0 = PEOPLE.restoreBill(1, 0), b3 = PEOPLE.restoreBill(2, 3);
  ok(b0.days === H.restore.freshDays && b0.wages === H.restore.freshDays * H.restore.wage, "a fresh house: a fresh-up day of a builder", b0);
  ok(b3.days === H.restore.freshDays + 3 && b3.wages === b3.days * H.restore.wage && b3.mats.stone === H.restore.perBand.stone * 3 * 2, "band 3, level 2: days and stone scale", b3);
  ok(H.restore.wage === ECON.WAGE.builder, "the restoration wage is the builder's wage");
  // the queue: deduped, capped
  const Q = [];
  ok(PEOPLE.queueRestore(Q, [5, 5, 6]) === 2 && Q.length === 2, "queueRestore dedupes", Q);
  ok(PEOPLE.queueRestore(Q, [null, undefined, "x"]) === 0, "only numeric home ids are queued");
  const big = []; PEOPLE.queueRestore(big, Array.from({ length: H.restore.queueMax + 10 }, (_, i) => i + 1));
  ok(big.length === H.restore.queueMax, "the queue is capped", big.length);
  // a day: pay (treasury -> purse, stock down), work, done
  const L = ledger({ treasury: 5000, purse: 0 });
  const m0 = money(L);
  const q = [{ h: 7 }];
  const lv = () => 1, band = () => 2;
  const r1 = PEOPLE.restoreDay(L, q, { lvl: lv, band });
  const bill = PEOPLE.restoreBill(1, 2);
  ok(r1.started.length === 1 && L.treasury === 5000 - bill.wages && L.purse === bill.wages && money(L) === m0, "paid: wages treasury -> purse (the builders' jobs), money conserved", [L.treasury, L.purse]);
  ok(L.stock.stone === 1000 - bill.mats.stone && L.stock.planks === 1000 - bill.mats.planks, "the materials leave the stock", L.stock);
  let done = r1.done.length ? 1 : 0, days = 1;
  while (!done && days < 10) { const r = PEOPLE.restoreDay(L, q, { lvl: lv, band }); days++; done = r.done.includes(7) ? 1 : 0; }
  ok(done && days === bill.days && !q.length, `done after the bill's ${bill.days} days, out of the queue`, [days, q]);
  // an empty treasury: waits, nothing goes negative; money next day -> starts
  const E = ledger({ treasury: 0, purse: 0 });
  const qe = [{ h: 3 }];
  const re = PEOPLE.restoreDay(E, qe, { lvl: lv, band });
  ok(!re.started.length && re.waiting === 1 && E.treasury === 0 && qe.length === 1 && qe[0].l === undefined, "an empty treasury: the restoration waits (no debt)", [re, E.treasury, qe]);
  E.treasury = 10000;
  ok(PEOPLE.restoreDay(E, qe, { lvl: lv, band }).started.length === 1, "and starts when the treasury can pay");
  // no materials: waits; the daily cap; a house no longer a home is dropped
  const N = ledger({ stock: { stone: 0, planks: 0 } });
  ok(PEOPLE.restoreDay(N, [{ h: 1 }], { lvl: lv, band }).waiting === 1, "no materials: waits");
  const C = ledger();
  const qc = [1, 2, 3, 4, 5].map((h) => ({ h }));
  ok(PEOPLE.restoreDay(C, qc, { lvl: lv, band }).started.length === H.restore.perDay, `at most ${H.restore.perDay} started a day`);
  const qd = [{ h: 1 }, { h: 2 }];
  const rd = PEOPLE.restoreDay(C, qd, { lvl: lv, band, ok: (h) => h !== 1 });
  ok(rd.dropped === 1 && qd.every((e) => e.h !== 1), "a house no longer a home leaves the queue", qd);
  // deeds: a sale pays the heir (treasury -> purse), a purchase pays the town (purse -> treasury); conserved; capped
  const M = ledger({ treasury: 3000, purse: 500 });
  const mm = money(M);
  const out = PEOPLE.settleDeeds(M, [{ kind: "buy", price: 1440 }, { kind: "sell", price: 2000 }]);
  ok(M.treasury === 3000 + 500 - 2000 && M.purse === 2000 && money(M) === mm, "deeds: purchase capped at the purse (500), sale 2000 paid, money conserved", [M.treasury, M.purse]);
  ok(out[0].paid === 500 && out[1].paid === 2000, "each deed records what was paid", out);
  const Z = ledger({ treasury: 0, purse: 0 });
  ok(PEOPLE.settleDeeds(Z, [{ kind: "sell", price: 2000 }])[0].paid === 0 && Z.treasury === 0, "a sale with an empty treasury pays nothing (no debt)");
  ok(PEOPLE.settleDeeds(null, [{ kind: "sell", price: 5 }])[0].paid === 0, "no ledger yet: deeds move no money");
  // the sale replenishes the restoration: a purchase at a level covers that level's worst restoration
  ok([1, 2, 3, 4, 5].every((lvl) => H.price[lvl] * H.buyShare >= PEOPLE.restoreBill(lvl, 3).wages + 12 * PEOPLE.restoreBill(lvl, 3).mats.stone + 4 * PEOPLE.restoreBill(lvl, 3).mats.planks),
     "a level's price covers its worst restoration (wages + materials at base prices)");
}
{
  // every move queues: the faucet's newcomer, a marriage move, a departure
  const P = PEOPLE.newPeople();
  for (let i = 0; i < 4; i++) { const p = mk(P, { age: 40, home: 1 + i, sex: i % 2 ? "f" : "m" }); p.mood = 90; }
  P.faucet = DIALS.faucetEvery;
  const r = PEOPLE.dayStep(P, cx({ homes: [1, 2, 3, 4].map((id) => ({ id, room: 0 })).concat([{ id: 8, room: 3 }]) }));
  ok(r.arrivals.length === 1 && r.restore.includes(8), "an arrival queues its home", r.restore);
  const P2 = PEOPLE.newPeople();
  const a = mk(P2, { age: 40, home: 1 }), b = mk(P2, { age: 40, home: 2, sex: "f" });
  a.friends[b.id] = 90; b.friends[a.id] = 90;
  const r2 = PEOPLE.dayStep(P2, cx({ homes: [{ id: 1, room: 0 }, { id: 2, room: 1 }] }));
  ok(a.spouse === b.id && a.home === 2 && r2.restore.includes(1) && r2.restore.includes(2), "a marriage move queues both homes", r2.restore);
  const P3 = PEOPLE.newPeople();
  const c = mk(P3, { age: 40, home: 3 }); c.lowDays = DIALS.leaveDays; c.mood = 0;
  const r3 = PEOPLE.dayStep(P3, cx({ homes: [{ id: 3, room: 0 }] }));
  ok(!c.alive && r3.restore.includes(3), "a departure queues the home left", r3.restore);
}

// ------------------------------------------------------------------------------------------------ 5. the children of adult children
{
  // 12 founders (6 couples), plenty of homes and work; 500 days: a third generation is born in the town
  const P = PEOPLE.newPeople();
  for (let i = 0; i < 6; i++) { const m = mk(P, { age: 25, home: 1 + i, job: 100 + (i % 3), trade: "bakery" }), f = mk(P, { age: 23, home: 1 + i, sex: "f", job: 100 + (i % 3), trade: "bakery" }); wed(m, f); }
  const homes = () => Array.from({ length: 80 }, (_, k) => ({ id: 1 + k, room: 0, x: (k % 10) * 12, z: Math.floor(k / 10) * 12 }));
  const live = new Map();
  let gen3 = 0, wed2 = 0;
  for (let d = 0; d < 500; d++) {
    const occ = new Map(); for (const p of PEOPLE.alive(P)) if (p.home) occ.set(p.home, (occ.get(p.home) || 0) + 1);
    const hs = homes().map((h) => ({ ...h, room: Math.max(0, 4 - (occ.get(h.id) || 0)), over: Math.max(0, (occ.get(h.id) || 0) - 4) }));
    const jobs = [100, 101, 102, 103, 104, 105].map((id) => ({ id, kind: "bakery", vacancies: 6, x: 30, z: 30 }));
    const r = PEOPLE.dayStep(P, { day: D + d, fed: 1, paid: true, homes: hs, jobs, seed: 13, foodDays: 30, levels: new Map(hs.map((h) => [h.id, 1 + (h.id % 2)])), wageOf: (p) => (p.job ? 96 : 0) });
    for (const p of PEOPLE.alive(P)) if (p.mood < 70) p.mood = 70;                        // keep the town content (the test is about kinship)
    for (const e of r.events) if (e.kind === "birth") {
      const baby = P.list[P.list.length - 1];
      const par = baby.parents.map((id) => PEOPLE.byId(P, id)).filter(Boolean);
      if (par.some((q) => q.parents.length)) gen3++;
    }
    for (const e of r.events) if (e.kind === "wedding" && e.people.some((id) => (PEOPLE.byId(P, id)?.parents || []).length)) wed2++;
    live.set(d, PEOPLE.alive(P).length);
  }
  ok(wed2 > 0, "town-born adults marry", wed2);
  ok(gen3 > 0, "town-born adults have children (a third generation)", gen3);
  const g3 = P.list.filter((p) => p.parents.length && p.parents.some((id) => (PEOPLE.byId(P, id)?.parents || []).length));
  ok(g3.length > 0 && g3.every((p) => p.dyn !== undefined), "every grandchild carries a line", g3.length);
  ok(g3.some((p) => p.alive && P.lines && P.lines[p.dyn]), "a living grandchild's line is registered by name", g3.slice(0, 3).map((p) => p.dyn));
  console.log(`  5: 500 days from 12 founders: ${PEOPLE.alive(P).length} living, town-born weddings ${wed2}, third-generation births ${gen3}, lines ${Object.keys(P.lines || {}).length}`);
}

// ------------------------------------------------------------------------------------------------ 6. save bytes per person
{
  const P = PEOPLE.newPeople();
  const n = 600;
  for (let i = 0; i < n; i++) mk(P, { age: 20 + (i % 80), home: 500 + (i >> 1), sex: i % 2 ? "f" : "m" });
  const s0 = JSON.stringify(P).length;
  for (const p of P.list) if (p.id % 3) p.dyn = 1 + (p.id % 97) * 37;               // two thirds town-born (4-digit lines)
  P.lines = {}; for (let k = 0; k < 97; k++) P.lines[1 + k * 37] = PEOPLE.NAMES_M[k % 20];
  const s1 = JSON.stringify(P).length;
  const per = (s1 - s0) / n;
  console.log(`  6: 600 people ${s0} -> ${s1} chars with lines (+${per.toFixed(1)} per person, register ${JSON.stringify(P.lines).length})`);
  ok(per <= 14, "the new fields cost <= 14 chars a person (dyn on the town-born + the line register)", per);
}

// ------------------------------------------------------------------------------------------------ 7. the clock's restoration day
{
  // restoreDaily and wageOfPerson, cut from pw_civ_clock.js and run on stand-ins (the engine is not here)
  const src = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
  const cut = (name) => {
    const i = src.indexOf(`function ${name}(`);
    let k = src.indexOf("{", i), depth = 0, j = k;
    for (; j < src.length; j++) { if (src[j] === "{") depth++; else if (src[j] === "}" && --depth === 0) break; }
    return src.slice(i, j + 1);
  };
  const placed = [];
  let loaded = false;
  const world = { getDimension: () => ({ isChunkLoaded: () => loaded }), structureManager: { place: (...a) => placed.push(a) } };
  const BUILDINGS = { fam: { stem: "mvv_cottage_s_a_r1" } };
  const B = new Map([[7, { id: 7, settlement: 1, family: "fam", stage: 4, x: 0, y: 64, z: 0, rot: 0, wx: 2, built: 10 }], [8, { id: 8, settlement: 1, family: "fam", stage: 2, x: 9, y: 64, z: 0, rot: 0 }]]);
  const env = { world, BUILDINGS, ROTS: ["None"], ECON, PEOPLE, buildingById: (s, id) => B.get(id) || null, hhOf: () => 1, short: () => "cottage_s", diagOf: () => ({}) };
  const restoreDaily = new Function(...Object.keys(env), `${cut("restoreDaily")}; return restoreDaily;`)(...Object.values(env));
  const L = ledger({ treasury: 10000, purse: 0 });
  const st = { id: 1, dim: "overworld", ledger: L, log: [], restore: [{ h: 7 }, { h: 8 }] };
  const s0 = { simDays: 400 };
  const bill = PEOPLE.restoreBill(1, 2);
  for (let d = 0; d < bill.days; d++) { s0.simDays = 400 + d; restoreDaily(s0, st); }
  ok(!st.restore.some((e) => e.h === 8), "clock: a plot still under construction leaves the queue", st.restore);
  ok(L.treasury === 10000 - bill.wages && L.purse === bill.wages, "clock: the bill is paid once (treasury -> purse)", [L.treasury, L.purse]);
  ok(B.get(7).wx === 2 && placed.length === 0 && st.restore.length === 1, "clock: done in an unloaded chunk -> waits for the chunk (the blocks are not placed)", st.restore);
  loaded = true; s0.simDays += 1; restoreDaily(s0, st);
  ok(placed.length === 1 && placed[0][0] === "pw:stages/mvv_cottage_s_a_r1_r" && B.get(7).wx === undefined && B.get(7).built === s0.simDays && !st.restore,
     "clock: loaded -> the fresh blocks (_r) are placed, the age restarts, the queue is gone", [placed.map((x) => x[0]), B.get(7), st.restore]);
  ok(st.log.some((l) => /began restoring/.test(l)) && st.log.some((l) => /is restored/.test(l)), "clock: the chronicle tells the start and the end", st.log);
  const wageOfPerson = new Function("ECON", "PEOPLE", "jobKindOf", `${cut("wageOfPerson")}; return wageOfPerson;`)(ECON, PEOPLE, (s, p) => p.k);
  ok(wageOfPerson({}, { job: null }) === 0 && wageOfPerson({}, { job: 5, k: "smithy", trade: "smithy" }) === ECON.WAGE.keeper && wageOfPerson({}, { job: "builders", k: "builders", trade: "builder" }) === ECON.WAGE.builder
     && wageOfPerson({}, { job: "watch", k: "watch", trade: "watch" }) === ECON.WAGE.watch && wageOfPerson({}, { job: 6, k: "quarry", trade: "quarry", skill: { quarry: 99 } }) === ECON.WAGE.master,
     "clock: wages for affording — none, a keeper, a builder, the watch, a master quarryman");
}

console.log(`test_households: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
