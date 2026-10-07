// test_court.mjs — 1.3.229 role beds (pw_civ_court.js): the beds table, who fits, the lord, one representative per
// district, the top families, staff by skill (singles only, keepers stay), reservation, stability, release to the old home.
import * as C from "../pw_civ_court.js";
import { PALACE_BEDS_1 as PALACE_BEDS } from "../pw_civ_court_data.js";   // 1.3.232 (#21): the 2 x 2 palace's table (PALACE II's beds: test_palace_hook.mjs)

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);

// the table
eq(C.bedsOfPiece("sw").cell, undefined, "cells are never homes");
eq(C.bedsOfPiece("ne").lord, 1, "the lord's bed is in the ne piece");
const total = Object.values(PALACE_BEDS).reduce((a, o) => a + Object.entries(o).filter(([k]) => k !== "cell" && k !== "child").reduce((x, [, n]) => x + n, 0), 0);
eq(total, 96, "96 role beds (228 spirals: the commons hall took 2 servant beds; the gatehouse stair gave a guard bed back)");
const kids = Object.values(PALACE_BEDS).reduce((a, o) => a + (o.child || 0), 0);
const apts = Object.values(PALACE_BEDS).reduce((a, o) => a + (o.noble || 0) + (o.lord || 0), 0);
eq(kids, apts, "his 17:52: one children's bed per apartment of state + the lord's chamber (12)");
eq(C.COURT.kidsMax, 2, "with children's beds a couple + 2 children fits");
eq(C.bedsOfPiece("ne").child, undefined, "children's beds are not role slots");

// a town
let nid = 1;
const P = { list: [] };
const mk = (o) => { const p = { id: nid++, alive: true, born: 0, spouse: null, kids: [], home: 100, job: null, trade: null, skill: {}, ...o }; P.list.push(p); return p; };
const byId = (P2, id) => P2.list.find((p) => p.id === id);
const f = {
  stage: (p) => p.child ? "child" : "adult",
  household: (p) => { const out = [p]; const sp = p.spouse ? byId(P, p.spouse) : null; if (sp && sp.alive && sp.home === p.home) out.push(sp); for (const k of p.kids) { const c = byId(P, k); if (c && c.alive && c.home === p.home && c.child) out.push(c); } return out; },
  districtOf: (p) => p.district ?? null, homeKind: () => "cottage_m", tradeOf: (p) => p.trade, dead: (id) => { const q = byId(P, id); return !q || !q.alive; },
};
// families: A couple skill 90 (district 1), B couple skill 80 with a child (district 1: does not fit), C single skill 70 (district 2), D couple 60 (district 2)
const a1 = mk({ skill: { smithy: 90 }, home: 101, district: 1 }), a2 = mk({ home: 101, district: 1 }); a1.spouse = a2.id; a2.spouse = a1.id;
const b1 = mk({ skill: { bakery: 80 }, home: 102, district: 1 }), b2 = mk({ home: 102, district: 1 }), bk = mk({ home: 102, child: true, district: 1 }); b1.spouse = b2.id; b2.spouse = b1.id; b1.kids = [bk.id];
const c1 = mk({ skill: { quarry: 70 }, home: 103, district: 2 }), c2 = mk({ home: 103, district: 2 }); c1.spouse = c2.id; c2.spouse = c1.id;
const e1 = mk({ skill: { quarry: 10 }, home: 110, district: 3 }), e2 = mk({ home: 110, district: 3 }); e1.spouse = e2.id; e2.spouse = e1.id;   // below nobleMin
const f1 = mk({ skill: { quarry: 75 }, home: 111, district: 2 });                                                                             // a single: never noble
const d1 = mk({ skill: { mason: 60 }, home: 104, district: 2 }), d2 = mk({ home: 104, district: 2 }); d1.spouse = d2.id; d2.spouse = d1.id;
// staff: singles with trades
const s1 = mk({ trade: "bakery", job: 7, skill: { bakery: 50 }, home: 105 }), s2 = mk({ trade: "smithy", job: 8, skill: { smithy: 65 }, home: 106 });
const sk = mk({ trade: "bakery", job: 9, skill: { bakery: 99 }, home: 9, keeper: true });        // a shop master: stays
const w1 = mk({ job: "watch", trade: "watch", home: 107 });
const wm = mk({ job: "watch", trade: "watch", home: 108 }); const wsp = mk({ home: 108 }); wm.spouse = wsp.id; wsp.spouse = wm.id;   // married: keeps home
const cl = mk({ job: "surveyor", trade: "surveyor", home: 109 });

const pieces = [{ id: 501, q: "ne" }, { id: 502, q: "se" }];
// his 17:52 children's beds: with them a couple + up to 2 children fits an apartment
const kidsWas = C.COURT.kidsMax;
C.COURT.kidsMax = 2;
{ const p0 = C.courtPlan(pieces, P.list, f); const ab = p0.admit.find((x) => x.pid === b1.id), ak = p0.admit.find((x) => x.pid === bk.id);
  ok(ab && ak && ab.b === ak.b && ab.r === ak.r, "with children's beds the family with a child moves in together"); }
ok(C.fitsApartment([a1, a2, bk, bk], f) && !C.fitsApartment([a1, a2, bk, bk, bk], f), "2 children fit, 3 do not");
C.COURT.kidsMax = 0;                                     // the rest of this file: no children's beds (the strict rule)
let plan = C.courtPlan(pieces, P.list, f);
const at = (p) => plan.admit.find((x) => x.pid === p.id);
eq(at(a1) && at(a1).r, "lord", "the top fitting family is the lord's");
eq(at(a2) && at(a2).r, "lord", "with the spouse");
ok(!at(b1) && !at(bk), "a family with a child does not fit one bed");
eq(at(f1), undefined, "a single is never noble (no job: nothing)");
ok(!at(e1), "a household below the journeyman line is not noble");
eq(at(c1) && at(c1).r, "noble", "district 2's representative (its top couple)");
eq(at(c1).d, 2, "the representative's district");
eq(at(d1) && at(d1).r, "noble", "then the next top families");
ok(!at(sk), "a shop master stays with his shop");
eq(at(s2) && at(s2).r, "servant", "the most skilled tradesman serves");
eq(at(s1) && at(s1).r, "servant", "a cook serves");
ok(plan.admit.findIndex((x) => x.pid === s2.id) < plan.admit.findIndex((x) => x.pid === s1.id), "skill order (65 before 50)");
eq(at(w1) && at(w1).r, "guard", "a single watchman takes a guard bed");
ok(!at(wm), "a married watchman keeps the family home");
eq(at(cl) && at(cl).r, "clerk", "a surveyor takes a clerk's bed");
eq(plan.free.lord, undefined, "the lord's bed held");
ok(plan.free.guard > 0 && plan.free.servant > 0, "the rest reserved (free, waiting for roles)");

const homeOk = (id) => id >= 100 && id < 200;
let r = C.applyCourt(plan, P, byId, homeOk);
eq(r.admitted, plan.admit.length, "applied");
eq([a1.home, a1.court.r, a1.court.prev], [501, "lord", 101], "the lord lives in the ne piece; came from #101");
// stability: the next day nothing moves
plan = C.courtPlan(pieces, P.list, f);
eq([plan.release.length, plan.admit.length], [0, 0], "stable the next day");
// the servant marries -> released to the old home; the bed waits for the next single
const n1 = mk({ home: 120 }); s1.spouse = n1.id; n1.spouse = s1.id;
plan = C.courtPlan(pieces, P.list, f);
ok(plan.release.includes(s1.id), "a married servant is released");
r = C.applyCourt(plan, P, byId, homeOk);
eq([s1.home, s1.court], [105, undefined], "back to the home he came from");
// a noble widower remarries someone who lives elsewhere -> released (the couple may come back together)
c2.alive = false; const n2 = mk({ home: 121 }); c1.spouse = n2.id; n2.spouse = c1.id;
plan = C.courtPlan(pieces, P.list, f);
ok(plan.release.includes(c1.id), "a noble whose spouse lives elsewhere is released");
// the lord dies -> the widow keeps the bed
C.applyCourt(plan, P, byId, homeOk);
a1.alive = false;
plan = C.courtPlan(pieces, P.list, f);
ok(!plan.release.includes(a2.id) && a2.court.r === "lord", "the widow keeps the lord's bed");
// a piece gone (not finished / closed) -> its members released
plan = C.courtPlan([{ id: 502, q: "se" }], P.list, f);
ok(plan.release.includes(a2.id) && plan.release.includes(w1.id), "a missing piece releases its members");
// staffRole rules
eq(C.staffRole({ id: 1, job: "watch", trade: "watch", alive: true }, f), "guard", "watch -> guard");
eq(C.staffRole({ id: 1, job: 5, trade: "weaver", alive: true }, f), "servant", "craft -> servant");
eq(C.staffRole({ id: 1, job: 5, trade: "farm_wheat", alive: true }, f), null, "a farmer is not palace staff");
eq(C.staffRole({ id: 1, job: null, trade: "bakery", alive: true }, f), null, "no job: no post");

C.COURT.kidsMax = kidsWas;
console.log(`test_court: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
