// test_econ228.mjs — B7 economy core: tax dial, caps, reserves, scarcity-first split, counter price, notice slips, haul pick,
// and the ledger invariant through dayStep with the new terms.
import * as E from "../pw_civ_economy.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);
const money = (L) => L.treasury + L.purse + Object.values(L.tills).reduce((a, v) => a + v, 0);
const inv = (L) => money(L) - (L.minted + L.playerNet + (L.tradeIn || 0) - L.sunk);

// tax dial
const L = E.newLedger();
eq(E.taxFactor(L), 1, "normal by default");
L.tax = "high"; eq(E.taxFactor(L), 1.25, "high");
L.tax = "low"; eq(E.taxFactor(L), 0.75, "low");
// split: scarcer output gets more, runs conserved
const L2 = E.newLedger(); L2.stock.timber = 2000; L2.stock.planks = 0;
const sh = E.splitOutputs(L2, E.PRODUCE.lumberyard.out, 20);
ok(sh.planks > sh.timber, `scarce planks lean: ${JSON.stringify(sh)}`);
ok(Math.abs(sh.planks + sh.timber - 2) < 1e-9, "shares sum to the output count");
eq(E.splitOutputs(L2, { bread: 48 }, 20), { bread: 1 }, "single output keeps 1");
// caps through dayStep
const L3 = E.newLedger(); L3.stock.stone = E.CAP.stone - 10;
E.dayStep(L3, { shops: [{ id: 1, kind: "quarry", stations: 3 }], population: 5, households: 2 });
ok(L3.stock.stone <= E.CAP.stone, `stone clipped at the cap: ${L3.stock.stone}`);
eq(inv(L3), 0, "invariant after dayStep");
// reserves: quote never sells below the reserve
const L4 = E.newLedger(); L4.stock.bread = 100;
E.dayStep(L4, { shops: [], population: 10, households: 3 });
ok(L4.reserve.bread > 0, `bread reserve set: ${L4.reserve.bread}`);
const sellN = E.sellable(L4, "bread");
const q = E.quote(L4, "bread", 999);
eq(q.n, sellN, "quote stops at the reserve");
const L5 = E.newLedger(); L5.stock.stone = 50;
E.dayStep(L5, { shops: [], population: 0, households: 0, waitNeed: { stone: 40 } });
eq(E.sellable(L5, "stone"), Math.max(0, Math.floor(L5.stock.stone) - 40), "waiting bills reserve materials");
// sold term raises tomorrow's price
const A = E.newLedger(), B = E.newLedger();
for (const X of [A, B]) { X.stock.bread = 200; }
B.sold = { bread: 400 };
E.dayStep(A, { shops: [], population: 5, households: 1 }); E.dayStep(B, { shops: [], population: 5, households: 1 });
ok(B.prices.bread >= A.prices.bread, `sales raise the price: ${B.prices.bread} >= ${A.prices.bread}`);
// counter price
const C = E.newLedger();
for (const g of E.GOODS) for (let d = 0; d < 30; d++) for (const id of [1, 7, 99]) {
  const p = E.counterPrice(C, g, id, d, 8);
  ok(p >= E.BASE[g] * E.BAND[0] - 1 && p <= E.BASE[g] * E.BAND[1] + 1, `in band ${g} ${p}`);
}
eq(E.counterPrice(C, "bread", 3, 12, 5), E.counterPrice(C, "bread", 3, 12, 5), "deterministic");
ok(E.counterPrice(C, "bread", 3, 12, 1) >= E.counterPrice(C, "bread", 3, 12, 8) && E.counterPrice(C, "bread", 3, 12, 8) >= E.counterPrice(C, "bread", 3, 12, 20), "slope falls with chest stock");
// slips
const S = E.newLedger(); S.treasury = 100000; S.stock.bread = 0; S.stock.tools = 10;
const slips = E.slipsOf(S, { waitNeed: { stone: 30 }, population: 4 }, 5, 0);
ok(slips.some((x) => x.good === "stone" && x.qty === Math.min(64, Math.ceil(30 - S.stock.stone))) || S.stock.stone >= 30, "a waiting bill makes a stone slip");
ok(slips.some((x) => x.good === "bread"), "short bread makes a slip");
ok(!slips.some((x) => x.good === "tools"), "no tools slip when tools are stocked");
eq(E.slipsOf(S, { waitNeed: { stone: 30 }, population: 4 }, 5, 0), slips, "deterministic per day/roll");
const poor = E.newLedger(); poor.treasury = 10; poor.stock.bread = 0;
eq(E.slipsOf(poor, { population: 4 }, 5, 0).length, 0, "no slip the treasury cannot pay");
const before = inv(S);
ok(E.deliverSlip(S, slips[0]), "delivered");
eq(inv(S), before, "invariant after a delivery");
// haul pick
const qq = [{ from: 1, to: 9, g: "stone", n: 4, pri: 1, age: 0, fromAt: { x: 0, z: 0 } }, { from: 2, to: 9, g: "timber", n: 4, pri: 1, age: 0, fromAt: { x: 5, z: 0 } },
  { from: 3, to: 7, g: "stone", n: 4, pri: 3, age: 0, fromAt: { x: 100, z: 0 } }];
let r = E.pickHaul(qq, { x: 0, z: 0 }, 2);
eq(r.picks.map((h) => h.to), [9, 9], "nearest destination batched (2)");
eq(r.queue[0].age, 1, "skipped entries age");
r = E.pickHaul(qq, { x: 0, z: 0 }, 1);
eq(r.picks.length, 1, "batch 1");
let qa = [{ from: 3, to: 7, g: "stone", n: 4, pri: 3, age: 14, fromAt: { x: 100, z: 0 } }, { from: 1, to: 9, g: "stone", n: 4, pri: 1, age: 0, fromAt: { x: 0, z: 0 } }];
eq(E.pickHaul(qa, { x: 0, z: 0 }, 1).picks[0].to, 7, "an aged far load wins");
console.log(`test_econ228: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
