// test_coins.mjs — B7 (WE10, his "silver nickel"): exact prices, the pay plan (gold first, nickels, change), the issue plan,
// and the ledger invariant through a player purchase.
import * as E from "../pw_civ_economy.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);
eq(E.payPlan(5, 0, 24), { gold: 2, nick: 0, change: 0 }, "24 p = 2 gold");
eq(E.payPlan(5, 10, 30), { gold: 2, nick: 6, change: 0 }, "30 p = 2 gold + 6 nickels");
eq(E.payPlan(5, 2, 30), { gold: 3, nick: 0, change: 6 }, "short of nickels: 3 gold, 6 back");
eq(E.payPlan(0, 40, 30), { gold: 0, nick: 30, change: 0 }, "nickels only");
eq(E.payPlan(2, 5, 30), null, "29 p cannot pay 30");
eq(E.payPlan(1, 0, 5), { gold: 1, nick: 0, change: 7 }, "a gold coin for 5 p: 7 back");
for (let p = 1; p <= 200; p++) for (const [g, n] of [[0, 300], [20, 0], [3, 7], [9, 11]]) {
  const r = E.payPlan(g, n, p);
  if (g * 12 + n < p) { ok(r === null, `cannot pay ${p} from ${g}/${n}`); continue; }
  ok(r && r.gold <= g && r.nick <= n && r.gold * 12 + r.nick - r.change === p && r.change >= 0 && r.change < 12, `exact pay ${p} from ${g}/${n}: ${JSON.stringify(r)}`);
}
eq(E.issuePlan(30), { gold: 2, nick: 6 }, "issue 30 p");
eq(E.issuePlan(11), { gold: 0, nick: 11 }, "issue 11 p");
const L = E.newLedger();
L.stock.bread = 100; L.prices.bread = 13;
const before = L.treasury + L.purse;
const q = E.buy(L, "bread", 3);
eq(q.exact, 39, "3 bread at 13 p = 39 p exact");
eq(L.treasury + L.purse - before, 39, "the treasury takes the exact pennies");
console.log(`test_coins: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
