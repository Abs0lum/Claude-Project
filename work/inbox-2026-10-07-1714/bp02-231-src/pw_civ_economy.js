// pw_civ_economy.js — CIVITAS economy v2 (D-C534 §4, his C3: "ACTUALLY quarrying, trading through buying and selling goods,
// and using those goods to build their village … wages need to exist and be real"). PURE functions over plain data (no
// engine imports): the same code runs live, in catch-up, in the test skip and in the node tests.
//
// UNITS: the ledger counts PENNIES (p); 12 p = one pw:gold_coin item (the player's purse is the only coin that exists as an
// item). A material unit is ONE BLOCK: a building's bill is read from its own stage templates (CIV_BUILDINGS[..].bom), so a
// house is literally built from the stone its quarry dug and the logs its lumberyard felled (the clock passes the day's
// REAL production in ctx.produced; a workshop whose chunk was not loaded produces its abstract rate instead).
//
// THE LOOP (one village day, R2 §5.8): wages (treasury -> the citizens' purse) · rations bought (purse -> the shops' tills)
// · shops' earnings pay their keepers (tills -> purse) and tolls (tills -> treasury) · hearth tax (purse -> treasury) ·
// construction: a stage is placed only when its materials are in stock and its wages affordable (stock down, treasury ->
// purse) · the MINT issues pennies against real production when money is scarce (logged) · prices move with stock ·
// IMPORTS: a material short for 3 days is ordered from a neighbour by road at the delivered price, else a wandering
// merchant at 3x after 10 days · an INVARIANT ties every penny to its origin (minted + player's coins in - sunk).
export const MATS = ["stone", "lime", "timber", "planks", "thatch", "iron", "glass"];
export const GOODS = ["bread", "meat", "grain", "hides", "timber", "stone", "tools", "planks", "thatch", "lime", "iron", "glass", "fish"];   // 1.3.225: fish (his 20:35: fishermen)
export const BASE = { bread: 24, meat: 48, grain: 12, hides: 24, timber: 12, stone: 12, tools: 144, planks: 4, thatch: 6, lime: 36, iron: 240, glass: 120, fish: 30 };   // p per unit
export const BAND = [0.5, 3.0];
export const ITEM = { bread: "minecraft:bread", meat: "minecraft:cooked_beef", grain: "minecraft:wheat", hides: "minecraft:leather",
                     timber: "minecraft:oak_log", stone: "minecraft:cobblestone", tools: "minecraft:iron_pickaxe", planks: "minecraft:oak_planks",
                     thatch: "minecraft:hay_block", lime: "minecraft:bone_meal", iron: "minecraft:iron_ingot", glass: "minecraft:glass", fish: "minecraft:cooked_cod" };
export const LEAN_DAYS = 20;
export const COIN = 12;                                       // pennies per gold coin
// what each workshop makes per STATION per day when the world did not produce for it (abstract rate), from its inputs
export const PRODUCE = {
  farm_wheat: { out: { grain: 24 }, in: {} },
  farm_terrace: { out: { grain: 32 }, in: {} },
  farm_cattle: { out: { meat: 12, hides: 6 }, in: {} },
  bakery: { out: { bread: 48 }, in: { grain: 24 } },
  butcher: { out: { meat: 16 }, in: { hides: 0 } },
  lumberyard: { out: { timber: 40, planks: 80 }, in: {} },    // planks: the sawyers at the yard (a log makes 4)
  quarry: { out: { stone: 60, lime: 6 }, in: {} },            // lime: the quarry's kiln burns a little stone
  smithy: { out: { tools: 2, iron: 4 }, in: { timber: 4, stone: 4 } },
  brickworks: { out: { glass: 8 }, in: { stone: 8, timber: 8 } },
  fishery: { out: { fish: 10 }, in: {} },                     // 1.3.225: per fisherman per day (the catch on the shore replaces it on a real day)
};
// which real-world production replaces the abstract one (ctx.produced[kind] from the clock: dug / felled / harvested)
export const REAL = { quarry: "stone", lumberyard: "timber", farm_wheat: "grain", farm_terrace: "grain", fishery: "fish" };
export const EAT = { bread: 1, meat: 0.5 };
export const INN_SALES = { bread: 2, meat: 1 };
export const RATION_P = 36;                                   // what a person pays for a day's food
// wages in pennies per day (R2 §5.4 at 24 labour-days per game day)
export const WAGE = { fisher: 60, farmer: 60, quarryman: 84, woodcutter: 72, keeper: 96, builder: 120, labourer: 72, clerk: 144, servant: 60, official: 144, master: 192, hired: 180,
                      watch: 96, sewer_keeper: 84, carter: 72 };   // 1.3.228 (B10 / WP1): the posts are on the payroll (the watch first)
export const STATION_WAGE = { farm_wheat: "farmer", farm_terrace: "farmer", farm_cattle: "farmer", quarry: "quarryman", lumberyard: "woodcutter",
                              bakery: "keeper", butcher: "keeper", smithy: "keeper", inn: "keeper", town_hall: "clerk", brickworks: "keeper",
                              manor: "official", palace: "official", chapel: "clerk", church: "clerk", market: "keeper", fishery: "fisher" };
export const BLOCKS_PER_BUILDER_DAY = 40;                     // a builder lays this many blocks a day
export const TOLL = 0.02, STALLAGE = 6, HEARTH = 12, HEARTH_DAYS = 30, RENT = 0.08;
export const MINT_WAGE_DAYS = 30, MINT_SHARE = 0.5, MINT_MAX = 0.05;
export const IMPORT_DAYS = 3, MERCHANT_DAYS = 10, MERCHANT_X = 3;
export const WORKERS_PER_PERSON = 0.6;

export function newLedger() {
  const stock = {}, prices = {};
  for (const g of GOODS) { stock[g] = 0; prices[g] = BASE[g]; }
  return { v: 2, stock, prices, treasury: 20 * COIN, purse: 0, tills: {}, minted: 20 * COIN, sunk: 0, playerNet: 0, day: 0, prosperity: [],
           sales: {}, lean: {}, closing: [], history: [], waiting: {}, shortDays: {}, orders: [], arrears: 0, prodValue: [], wages: 0, builders: 0, hired: 0 };
}
/** an old ledger (v1, coins) carried into v2 pennies */
export function upgradeLedger(L) {
  if (L.v === 2) return L;
  const N = newLedger();
  for (const g of GOODS) { N.stock[g] = L.stock[g] || 0; }
  N.treasury = Math.round((L.treasury || 0) * COIN);
  N.minted = N.treasury;
  N.day = L.day || 0; N.prosperity = L.prosperity || []; N.history = []; N.lean = L.lean || {}; N.closing = L.closing || [];
  return N;
}

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const money = (L) => L.treasury + L.purse + Object.values(L.tills).reduce((a, v) => a + v, 0);

/** the bill of one stage: materials (blocks by class) + wages (builder-days * builder wage) */
export function stageBill(bom, k) {
  const b = (bom && bom[k]) || {};
  const mats = {};
  let blocks = 0;
  for (const m of MATS) { const n = b[m] || 0; if (n > 0) mats[m] = n; blocks += n; }
  const days = Math.max(1, Math.ceil(blocks / BLOCKS_PER_BUILDER_DAY));
  return { mats, blocks, builderDays: days, wages: days * WAGE.builder };
}
/** what is missing for a bill: {} when it can be paid now */
export function missing(L, bill, capacityBlocks = Infinity) {
  const out = {};
  for (const [m, n] of Object.entries(bill.mats)) if ((L.stock[m] || 0) < n) out[m] = n - Math.floor(L.stock[m] || 0);
  if (L.treasury < bill.wages) out.pennies = bill.wages - L.treasury;
  if (capacityBlocks < bill.blocks) out.builders = Math.ceil((bill.blocks - capacityBlocks) / BLOCKS_PER_BUILDER_DAY);
  return out;
}
/** pay a bill: stock down, wages treasury -> purse */
export function pay(L, bill) {
  for (const [m, n] of Object.entries(bill.mats)) L.stock[m] -= n;
  L.treasury -= bill.wages;
  L.purse += bill.wages;
  L.wagesPaid = (L.wagesPaid || 0) + bill.wages;
}

/** one village day. ctx = { shops: [{id, kind, stations, closed}], population, households, inns, produced: {kind -> real
 *  units today | undefined}, neighbours: [{id, stock, prices, dist}], day, moodBy: {shop id -> output factor} (B3) }.
 *  Returns the day's events (strings). */
export function dayStep(L, ctx) {
  const ev = [];
  L.day += 1;
  for (const g of GOODS) { if (L.stock[g] === undefined) L.stock[g] = 0; if (L.prices[g] === undefined) L.prices[g] = BASE[g]; }   // 1.3.225: a new good joins an old ledger
  const shops = ctx.shops || [];
  const population = ctx.population || 0;
  const open = shops.filter((s) => !s.closed && PRODUCE[s.kind]);
  // 1. PRODUCTION: real where the world produced today, the abstract rate otherwise; converters need their inputs
  const order = ["farm_wheat", "farm_terrace", "farm_cattle", "fishery", "lumberyard", "quarry", "butcher", "bakery", "smithy", "brickworks"];
  const byKind = {};
  for (const s of open) (byKind[s.kind] = byKind[s.kind] || []).push(s);
  let prodValue = 0;
  for (const kind of order) {
    const list = (byKind[kind] || []).slice().sort((a, b) => b.stations - a.stations);
    for (const s of list) {
      const p = PRODUCE[kind];
      // 1.3.228 (B3 / BF4): the workshop's mood tier scales its abstract runs (ctx.moodBy[shop id]: 1.2 .. 0.70; 0 only with
      // the strike flag); a real day's carried production is not scaled again (the mood is in the hands' pace)
      const mf = ctx.moodBy && ctx.moodBy[s.id] !== undefined ? ctx.moodBy[s.id] : 1;
      let runs = Math.max(1, s.stations || 1) * mf;
      for (const [g, n] of Object.entries(p.in)) if (n > 0) runs = Math.min(runs, Math.floor((L.stock[g] || 0) / n));
      if (runs <= 0) { L.sales[s.id] = 0; continue; }
      for (const [g, n] of Object.entries(p.in)) L.stock[g] -= n * runs;
      let value = 0;
      const realKey = REAL[kind];
      const real = ctx.produced && realKey && ctx.produced[s.id] !== undefined ? ctx.produced[s.id] : undefined;
      // 1.3.228 (B7 / WE8): a multi-output workshop leans its runs to the SCARCER output (Townstead's score, deterministic);
      // (WE9) nothing is made past its good's CAP
      const share = splitOutputs(L, p.out, population);
      for (const [g, n] of Object.entries(p.out)) {
        let made = g === realKey && real !== undefined ? real : n * runs * share[g];
        made = Math.max(0, Math.min(made, (CAP[g] ?? Infinity) - (L.stock[g] || 0)));
        L.stock[g] += made;
        value += made * L.prices[g];
      }
      L.sales[s.id] = value;
      prodValue += value;
    }
  }
  L.prodValue.push(Math.round(prodValue));
  if (L.prodValue.length > 10) L.prodValue.shift();
  // 2. WAGES from the treasury: every station worker (by trade), the officials; builders are paid per stage (pay())
  let payroll = 0;
  // 1.3.228 (B10 / WP1): the town's POSTS are paid FIRST (the watch, the sewer keeper, the carters: ctx.posts {post: n});
  // a short treasury falls on the station workers after them. L.watchPaid says whether the watch's pay was covered today
  let postsWage = 0;
  for (const [post, n] of Object.entries(ctx.posts || {})) postsWage += (WAGE[post] || 0) * (n || 0);
  L.watchPaid = L.treasury >= postsWage;
  payroll += postsWage;
  const workers = Math.round(population * WORKERS_PER_PERSON);
  let stationed = 0;
  for (const s of shops.filter((x) => !x.closed)) {
    const trade = STATION_WAGE[s.kind];
    if (!trade) continue;
    const n = Math.max(1, s.stations || 1);
    stationed += n;
    payroll += WAGE[trade] * n;
  }
  const paid = Math.min(L.treasury, payroll);
  L.treasury -= paid; L.purse += paid;
  L.wages = payroll;
  if (paid < payroll) { L.arrears += 1; if (L.arrears === 3) ev.push(`wages in arrears for 3 days: the sites pause`); } else L.arrears = 0;
  L.builders = Math.max(0, workers - stationed) + (L.hired || 0);
  // 3. RATIONS: the people buy bread and meat from the stock; the purse pays the shops' tills (the bakery's / butcher's)
  const short = {};
  let foodSpend = 0;
  for (const [g, per] of Object.entries(EAT)) {
    const need = per * population;
    const take = Math.min(L.stock[g] || 0, need);
    L.stock[g] -= take;
    short[g] = need - take;
    foodSpend += take * L.prices[g];
  }
  const spend = Math.min(L.purse, Math.round(foodSpend));
  L.purse -= spend;
  const sellers = open.filter((s) => s.kind === "bakery" || s.kind === "butcher");
  if (sellers.length) { const each = Math.floor(spend / sellers.length); let rest = spend; for (const s of sellers) { L.tills[s.id] = (L.tills[s.id] || 0) + each; rest -= each; } L.tills[sellers[0].id] += rest; }
  else L.treasury += spend;                                     // no shop yet: the common store sells
  // rents, licences, fines and the town's own goods: a share of the purse returns to the treasury every day (R2 §5.8:
  // 25-50 % of a wage is food; the rest buys goods and pays rent) — this is what lets the treasury pay for stone and sites
  const rent = Math.floor(L.purse * RENT);
  L.purse -= rent; L.treasury += rent;
  // the inn's trade with travellers: coin from outside (counted as minted by trade)
  for (const s of shops.filter((x) => !x.closed && x.kind === "inn")) {
    let earned = 0;
    for (const [g, n] of Object.entries(INN_SALES)) { const take = Math.min(L.stock[g] || 0, n); L.stock[g] -= take; earned += take * L.prices[g]; }
    L.tills[s.id] = (L.tills[s.id] || 0) + earned; L.minted += earned;      // travellers' money enters the town
    L.sales[s.id] = earned;
  }
  // 4. TILLS pay tolls to the treasury and their keepers' share to the purse (the keepers are citizens)
  for (const id of Object.keys(L.tills)) {
    const v = L.tills[id];
    if (v <= 0) continue;
    const toll = Math.floor(v * TOLL) + Math.min(v - Math.floor(v * TOLL), STALLAGE);
    L.treasury += toll;
    L.purse += v - toll;
    L.tills[id] = 0;
  }
  // hearth tax every HEARTH_DAYS
  if (L.day % HEARTH_DAYS === 0) { const tax = Math.min(L.purse, Math.round(HEARTH * taxFactor(L) * (ctx.households || 0))); L.purse -= tax; L.treasury += tax; }   // B7 (WE11): the dial
  // 5. PRICES: stock against ten days of need (people + a construction demand the clock reports)
  for (const g of GOODS) {
    const need = (EAT[g] || 0) * population * 10 + (INN_SALES[g] || 0) * 10 + ((ctx.demand && ctx.demand[g]) || 0) + 10 + 0.5 * ((L.sold && L.sold[g]) || 0);   // B7 (WE6)
    const ratio = Math.sqrt(need / Math.max(1, L.stock[g] || 0));
    L.prices[g] = Math.round(clamp(BASE[g] * ratio, BASE[g] * BAND[0], BASE[g] * BAND[1]));
  }
  // 1.3.228 (B7 / WE9): today's RESERVES (never sold to players or exported): food for RESERVE_FOOD_DAYS of need, materials
  // for the next waiting bills (ctx.waitNeed {good: n}); the counters' sales of the day reset
  L.reserve = {};
  for (const g of GOODS) {
    const r = Math.ceil((EAT[g] || 0) * population * RESERVE_FOOD_DAYS + ((ctx.waitNeed && ctx.waitNeed[g]) || 0));
    if (r > 0) L.reserve[g] = r;
  }
  L.sold = {};
  // 6. IMPORTS: a material short for IMPORT_DAYS -> an order by road, else the wandering merchant after MERCHANT_DAYS
  for (const m of MATS.concat(["grain"])) {
    const want = ctx.demand && ctx.demand[m] ? ctx.demand[m] : 0;
    const isShort = (L.stock[m] || 0) < want || (m === "grain" && short.bread > 0);
    L.shortDays[m] = isShort ? (L.shortDays[m] || 0) + 1 : 0;
    if (L.shortDays[m] >= IMPORT_DAYS && !L.orders.some((o) => o.good === m)) {
      const qty = Math.max(20, want - Math.floor(L.stock[m] || 0));
      const nb = (ctx.neighbours || []).filter((n) => (n.stock[m] || 0) > 2 * qty).sort((a, b) => a.dist - b.dist)[0];
      if (nb) {
        const price = Math.round(BASE[m] * (1 + nb.dist / 1200));
        L.orders.push({ good: m, qty, price, from: nb.id, due: L.day + Math.max(1, Math.ceil(nb.dist / 2000)) });
        ev.push(`${m} short: ${qty} ordered from settlement ${nb.id} at ${price} p (${nb.dist} blocks by road)`);
        L.shortDays[m] = 0;
      } else if (L.shortDays[m] >= MERCHANT_DAYS) {
        L.orders.push({ good: m, qty, price: BASE[m] * MERCHANT_X, from: 0, due: L.day + 1 });
        ev.push(`${m} short for ${MERCHANT_DAYS} days: a wandering merchant sells ${qty} at ${BASE[m] * MERCHANT_X} p`);
        L.shortDays[m] = 0;
      }
    }
  }
  // arrivals: the treasury pays what it can (the rest of the order waits a day)
  const keep = [];
  for (const o of L.orders) {
    if (o.due > L.day) { keep.push(o); continue; }
    const afford = Math.min(o.qty, Math.floor(L.treasury / Math.max(1, o.price)));
    if (afford <= 0) { o.due = L.day + 1; keep.push(o); continue; }
    L.stock[o.good] += afford; L.treasury -= afford * o.price; L.sunk += afford * o.price;     // money leaves the town
    o.qty -= afford;
    ev.push(`${afford} ${o.good} arrived ${o.from ? `from settlement ${o.from}` : "with the merchant"} (${afford * o.price} p)`);
    if (o.qty > 0) { o.due = L.day + 1; keep.push(o); }
  }
  L.orders = keep;
  // 7. THE MINT: when money is scarce for the payroll, new pennies against real production (bounded, logged)
  const M = money(L);
  const recent = L.prodValue.reduce((a, v) => a + v, 0);
  if (M < MINT_WAGE_DAYS * Math.max(payroll, 1) && recent > 0) {
    const cap = Math.min(Math.floor(recent * MINT_SHARE / 10), Math.max(Math.floor(M * MINT_MAX), payroll) + 10 * COIN);   // at least a day's payroll (the bootstrap)
    if (cap > 0) { L.treasury += cap; L.minted += cap; ev.push(`the mint issues ${cap} p against ${recent} p of production`); }
  }
  // 8. competition: among two or more shops of one kind, a shop that earned nothing today gets a lean day
  const kinds = {};
  for (const s of open) kinds[s.kind] = (kinds[s.kind] || 0) + 1;
  for (const s of open) {
    if (kinds[s.kind] < 2) { L.lean[s.id] = 0; continue; }
    if ((L.sales[s.id] || 0) > 0) L.lean[s.id] = 0;
    else { L.lean[s.id] = (L.lean[s.id] || 0) + 1; if (L.lean[s.id] >= LEAN_DAYS && !L.closing.includes(s.id)) { L.closing.push(s.id); ev.push(`${s.kind} #${s.id} has sold nothing for ${LEAN_DAYS} days: closing`); } }
  }
  // 9. prosperity + history + the invariant
  const needAll = Object.entries(EAT).reduce((a, [, per]) => a + per * population, 0);
  const shortAll = Object.values(short).reduce((a, v) => a + v, 0);
  const pros = needAll > 0 ? Math.max(0, 1 - shortAll / needAll) : 1;
  L.prosperity.push(Math.round(pros * 100) / 100);
  if (L.prosperity.length > 30) L.prosperity.shift();
  if (shortAll > 0) ev.push(`short: ${Object.entries(short).filter(([, v]) => v > 0).map(([g, v]) => `${g} ${v.toFixed(1)}`).join(", ")}`);
  L.history.push({ day: L.day, treasury: L.treasury, purse: L.purse, stone: Math.floor(L.stock.stone), timber: Math.floor(L.stock.timber), bread: Math.floor(L.stock.bread), pros: L.prosperity[L.prosperity.length - 1], M });
  if (L.history.length > 60) L.history.shift();
  const drift = money(L) - (L.minted + L.playerNet + (L.tradeIn || 0) - L.sunk);
  if (drift !== 0) { ev.push(`LEDGER DRIFT ${drift} p (money ${money(L)} vs minted ${L.minted} + player ${L.playerNet} + trade in ${L.tradeIn || 0} - sunk ${L.sunk})`); L.drift = (L.drift || 0) + drift; L.minted += drift; }
  return ev;
}

/** prosperous = everyone ate for the last n days (the growth gate once the economy runs) */
export function prosperous(L, n = 5) {
  const p = L.prosperity.slice(-n);
  return p.length >= n && p.every((v) => v >= 1);
}

/** a purchase by a player: `count` of `good` at today's price; coin = pw:gold_coin (12 p); emeralds at COIN_PER_EMERALD */
export const COIN_PER_EMERALD = 4;
export function quote(L, good, count, unit = L.prices[good]) {   // B7 (BF9): `unit` = a counter's own price
  if (!GOODS.includes(good)) return null;
  const n = Math.max(0, Math.min(count, sellable(L, good)));     // B7 (WE9): never below the day's reserve
  const exact = Math.round(n * unit);                     // 1.3.228 (B7 / WE10): the exact price in pennies (silver nickels)
  const coin = Math.ceil(exact / COIN);
  return { n, coin, exact, pennies: exact, emeralds: Math.ceil(coin / COIN_PER_EMERALD) };
}
export function buy(L, good, count, unit = L.prices[good]) {
  const q = quote(L, good, count, unit);
  if (!q || q.n <= 0) return null;
  L.stock[good] -= q.n;
  (L.sold = L.sold || {})[good] = (L.sold[good] || 0) + q.n;    // B7 (WE6): today's sales raise tomorrow's need
  L.treasury += q.exact; L.playerNet += q.exact;
  return q;
}
// 1.3.228 (B7 / WE10; his 12:20: "add a SILVER NICKEL"): pw:silver_nickel = 1 penny, so every price is paid exactly; 12
// nickels make a gold coin. The plans are pure (the coin module moves the items and logs the mint).
export const NICKEL_P = 1;
/** what a purse of `gold` coins and `nick` nickels pays for `p` pennies: { gold, nick, change } (nickels back), or null.
 *  Whole gold coins first, the rest in nickels; short of nickels: one more gold coin and the change in nickels. */
export function payPlan(gold, nick, p) {
  if (p <= 0) return { gold: 0, nick: 0, change: 0 };
  if (gold * COIN + nick < p) return null;
  let g = Math.min(gold, Math.floor(p / COIN));
  const rem = p - g * COIN;
  if (rem <= nick) return { gold: g, nick: rem, change: 0 };
  g += 1;                                                          // one more gold coin, the change in nickels
  return g <= gold ? { gold: g, nick: 0, change: g * COIN - p } : null;
}
/** how `p` pennies are issued: whole gold coins and the rest in nickels */
export function issuePlan(p) { return { gold: Math.floor(p / COIN), nick: p % COIN }; }
export function sell(L, good, count) {               // the player sells to the town at 70 % of the price
  if (!GOODS.includes(good) || count <= 0) return null;
  const pennies = Math.floor(count * L.prices[good] * 0.7);
  const coin = Math.floor(pennies / COIN);
  if (coin <= 0 || L.treasury < coin * COIN) return null;
  L.stock[good] += count;
  L.treasury -= coin * COIN; L.playerNet -= coin * COIN;
  return { n: count, coin, pennies: coin * COIN, emeralds: Math.floor(coin / COIN_PER_EMERALD) };
}

// ------------------------------------------------------------------------------------------------ 1.3.228 B7: ECONOMY CORE
// WE11 the TAX DIAL (his 12:20: a free command): the hearth tax x 0.75 / 1 / 1.25 and a fixed mood factor (people.moodParts
// c.tax) — deterministic, no riot roll. WE9 CAPS and RESERVES. WE8 the scarcity-first split. BF9 the COUNTER PRICE (town
// price x a seeded +-10 % wobble per counter and day x a slope on the chest's stock), always inside BAND. BF8 NOTICE SLIPS
// from real gaps only. WE2 the carters' haul pick (MineColonies' courier score).
export const TAX = { low: 0.75, normal: 1, high: 1.25 };
export const TAX_MOOD = { low: 1.06, normal: 1, high: 0.94 };
export const taxFactor = (L) => TAX[L.tax || "normal"] ?? 1;
export const CAP = { stone: 4096, timber: 2048, planks: 4096, grain: 1024, bread: 1024, meat: 768, fish: 768, hides: 512, lime: 512, thatch: 1024, tools: 256, iron: 512, glass: 512 };
export const RESERVE_FOOD_DAYS = 3;
export function sellable(L, good) { return Math.max(0, Math.floor((L.stock[good] || 0) - ((L.reserve && L.reserve[good]) || 0))); }
/** WE8: shares of a multi-output workshop's runs by score = value + max(0, 8 - 1.5 d) - 2.5 d (d = days of stock at the
 *  town's need); a single output keeps 1. The shares are normalised to the output count, so the total runs are conserved. */
export function splitOutputs(L, out, population = 0) {
  const goods = Object.keys(out);
  if (goods.length < 2) return Object.fromEntries(goods.map((g) => [g, 1]));
  const score = {};
  for (const g of goods) {
    const need = Math.max(1, (EAT[g] || 0) * population + 10);
    const d = (L.stock[g] || 0) / need;
    const value = (L.prices[g] || BASE[g]) / Math.max(1, BASE[g]);
    score[g] = Math.max(0.05, value + Math.max(0, 8 - 1.5 * d) - 2.5 * d);
  }
  const sum = goods.reduce((a, g) => a + score[g], 0);
  return Object.fromEntries(goods.map((g) => [g, (score[g] / sum) * goods.length]));
}
function hash2(a, b) { let h = (Math.imul(a ^ 0x9E3779B9, 0x85EBCA6B) ^ Math.imul(b + 0x632BE59B, 0xC2B2AE35)) >>> 0; h ^= h >>> 16; h = Math.imul(h, 0x7FEB352D) >>> 0; return (h ^ (h >>> 15)) >>> 0; }
/** BF9 + WE7: a counter's price for a good today (pennies per unit) */
export function counterPrice(L, good, counterId, day, chestStock = 16) {
  const base = L.prices[good] ?? BASE[good];
  const gi = GOODS.indexOf(good);
  const wobble = 1 + 0.10 * (2 * (hash2(day * 131 + gi, counterId) / 4294967296) - 1);
  const slope = chestStock <= 2 ? 1.15 : chestStock >= 16 ? 1.0 : 1.15 - 0.15 * (chestStock - 2) / 14;
  return Math.round(clamp(base * wobble * slope, BASE[good] * BAND[0], BASE[good] * BAND[1]));
}
/** BF8: the notice slips from REAL gaps: the waiting stage bills' materials (waitNeed), food short of 10 days' need, tools.
 *  qty = min(gap, 64), reward = qty x price x 1.1 (pennies) while the treasury covers the running total; at most 6; the order
 *  is deterministic per (day, roll): easy (small) to hard */
export function slipsOf(L, ctx = {}, day = 0, roll = 0) {
  const gaps = [];
  for (const [g, n] of Object.entries(ctx.waitNeed || {})) { const gap = Math.ceil(n - (L.stock[g] || 0)); if (gap > 0 && GOODS.includes(g)) gaps.push([g, gap, "a site waits"]); }
  for (const g of ["bread", "meat", "fish"]) { const need = (EAT[g] || 0) * (ctx.population || 0) * 10; const gap = Math.ceil(need - (L.stock[g] || 0)); if (gap > 0) gaps.push([g, gap, "the larders"]); }
  if ((L.stock.tools || 0) < 4) gaps.push(["tools", 4 - Math.floor(L.stock.tools || 0), "the workshops"]);
  const slips = [];
  let budget = L.treasury;
  for (const [g, gap, why] of gaps.sort((a, b) => (hash2(day * 7 + roll, GOODS.indexOf(a[0])) - hash2(day * 7 + roll, GOODS.indexOf(b[0]))))) {
    const qty = Math.min(gap, 64);
    const reward = Math.round(qty * (L.prices[g] ?? BASE[g]) * 1.1);
    if (reward <= 0 || reward > budget) continue;
    budget -= reward;
    slips.push({ good: g, qty, reward, why });
    if (slips.length >= 6) break;
  }
  return slips.sort((a, b) => a.qty - b.qty || (a.good < b.good ? -1 : 1));
}
/** BF8: a delivered slip: stock in, the reward out of the treasury to the player (playerNet keeps the invariant) */
export function deliverSlip(L, slip) {
  if (L.treasury < slip.reward) return false;
  L.stock[slip.good] = (L.stock[slip.good] || 0) + slip.qty;
  L.treasury -= slip.reward; L.playerNet -= slip.reward;
  return true;
}
/** WE2: the carter's next haul from st.haul [{from, to, g, n, age, pri}]: the best pri + age - sqrt(manhattan), same-destination
 *  loads batched up to `batch` (1 + rank); skipped entries age +1 (cap 14). Returns { picks, queue } */
export function pickHaul(queue, at, batch = 1, dist = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.z - b.z)) {
  if (!queue.length) return { picks: [], queue };
  const sc = (h) => (h.pri || 0) + (h.age || 0) - Math.sqrt(dist(at, h.fromAt || at));
  const order = queue.map((h, i) => ({ h, i, s: sc(h) })).sort((a, b) => b.s - a.s || a.i - b.i);
  const first = order[0].h;
  const picks = order.filter((o) => o.h.to === first.to).slice(0, Math.max(1, batch)).map((o) => o.h);
  const rest = queue.filter((h) => !picks.includes(h)).map((h) => ({ ...h, age: Math.min(14, (h.age || 0) + 1) }));
  return { picks, queue: rest };
}
