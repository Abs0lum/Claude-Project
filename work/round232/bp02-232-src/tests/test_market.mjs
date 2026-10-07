// test_market.mjs — 1.3.224 market math (his broad list; coins, never pennies paid as coins)
const S = await import("../pw_civ_shop.js");
const E = await import("../pw_civ_economy.js");
let n = 0, fails = 0;
const ok = (name, cond, info) => { n++; if (!cond) fails++; console.log(`${cond ? "PASS" : "FAIL"} ${n} ${name}${cond ? "" : " — " + JSON.stringify(info)}`); };
const L = E.newLedger();
const o = (id) => S.marketOffer(L, id);
ok("oak log -> timber at 0.6 of the live price (12 p) = 7.2 p each", o("minecraft:oak_log").good === "timber" && Math.abs(o("minecraft:oak_log").pennies - 7.2) < 1e-9, o("minecraft:oak_log"));
ok("stripped birch log and our tree logs (pw:birch_mature, pw:oak_old) are timber too", o("minecraft:stripped_birch_log").good === "timber" && o("pw:birch_mature").good === "timber" && o("pw:oak_old").good === "timber");
ok("spruce planks -> planks", o("minecraft:spruce_planks").good === "planks");
ok("cobbled deepslate -> stone; stone bricks at 1.5x", o("minecraft:cobbled_deepslate").good === "stone" && o("minecraft:stone_bricks").k === 1.5);
ok("raw beef -> meat at half", o("minecraft:beef").k === 0.5);
// 1.3.225 (fishermen): fish is its own good — cooked cod / salmon 1.2, raw 0.8, tropical 0.5 of the fish price (30 p)
ok("cooked salmon -> fish at 1.2; raw cod 0.8; tropical fish 0.5", o("minecraft:cooked_salmon").good === "fish" && o("minecraft:cooked_salmon").k === 1.2 && o("minecraft:cod").k === 0.8 && o("minecraft:tropical_fish").k === 0.5);
ok("a new ledger has fish in stock (0) at 30 p", L.stock.fish === 0 && L.prices.fish === 30);
{ const old = E.newLedger(); delete old.stock.fish; delete old.prices.fish; E.dayStep(old, { shops: [{ id: "fishery:1", kind: "fishery", stations: 2 }], population: 0 }); ok("an old ledger gains fish; 2 fishermen land 20 on an abstract day", old.stock.fish === 20 && old.prices.fish > 0, old.stock.fish); }
{ const L2 = E.newLedger(); E.dayStep(L2, { shops: [{ id: "fishery:1", kind: "fishery", stations: 2 }], population: 0, produced: { "fishery:1": 7 } }); ok("a real day's catch (7) replaces the abstract rate", L2.stock.fish === 7, L2.stock.fish); }
ok("white wool -> hides at half (cloth)", o("minecraft:white_wool").good === "hides" && o("minecraft:white_wool").k === 0.5);
ok("gold ingot is an export at 96 p (8 coins)", o("minecraft:gold_ingot").good === null && o("minecraft:gold_ingot").pennies === 96);
ok("diamond 480 p = 40 coins", Math.floor(o("minecraft:diamond").pennies / E.COIN) === 40);
ok("a dirt block is not bought", o("minecraft:dirt") === null);
ok("a netherite ingot is not on the list", o("minecraft:netherite_ingot") === null);
// a stack of 64 oak logs: 64 x 7.2 = 460.8 p -> 38 coins (floor), never 460 coins
const pay = Math.floor((64 * o("minecraft:oak_log").pennies) / E.COIN);
ok("64 oak logs pay 38 coins (pennies / 12)", pay === 38, pay);
// shop rate vs market rate: a shop pays SHOP_RATE 0.75 of its own good, the market 0.6
const shopPay = Math.floor(64 * L.prices.timber * 0.75 / E.COIN);
ok("the lumberyard itself would pay 48 coins for the same 64 logs (more than the market)", shopPay === 48 && shopPay > pay, shopPay);
console.log(`${n - fails}/${n} passed`);
process.exit(fails ? 1 : 0);
