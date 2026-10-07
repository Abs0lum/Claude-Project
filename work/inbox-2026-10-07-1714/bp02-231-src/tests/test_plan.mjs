// test_plan.mjs — B6 growth (pw_civ_plan.js): the charter's counts preserved, role order, affordability, priorities,
// rest cooldown, district skins, relief judgement (percentiles + water share + bad-cell budget), fillers, weathering.
import * as PL from "../pw_civ_plan.js";

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);

const produces = (nm) => ({ bakery: ["bread"], quarry: ["stone", "lime"], lumberyard: ["timber", "planks"] })[nm] || [];
const items = [{ nm: "cottage_s" }, { nm: "smithy" }, { nm: "bakery" }, { nm: "chapel", work: "chapel" }, { nm: "cottage_m" }, { nm: "manor" }];
const c = { shortGoods: new Set(["bread"]), produces, roomsFree: 5, missing: (nm) => (nm === "manor" ? { stone: 200 } : {}), prio: [] };
const ord = PL.orderItems(items, c, 7);
eq(ord.length, items.length, "counts preserved (same length)");
eq([...ord].map((x) => x.nm).sort(), items.map((x) => x.nm).sort(), "counts preserved (same items)");
eq(ord[0].nm, "chapel", "civic work first");
eq(ord[1].nm, "bakery", "a business that cures a shortage next");
ok(ord.findIndex((x) => x.nm === "manor") > ord.findIndex((x) => x.nm === "smithy"), "an unaffordable manor waits behind an affordable business");
eq(PL.orderItems(items, c, 7), ord, "deterministic per seed");
const short = PL.orderItems(items, { ...c, roomsFree: 0 }, 7);
ok(short.findIndex((x) => x.nm === "cottage_s") < short.findIndex((x) => x.nm === "smithy"), "homes jump ahead when rooms run short");
const pr = PL.orderItems(items, { ...c, prio: ["smithy"] }, 7);
eq(pr[0].nm, "smithy", "a player's priority goes first");

// leftovers + rest
const fc = {};
eq(PL.nextLeftover(["cottage_s", "bakery"], c, 10, fc).nm, "bakery", "the leftover that cures a shortage first");
PL.rest(fc, "bakery", 10);
eq(PL.nextLeftover(["cottage_s", "bakery"], c, 11, fc).nm, "cottage_s", "a resting family is skipped");
eq(PL.nextLeftover(["cottage_s", "bakery"], c, 12, fc).nm, "bakery", "rest over after FAIL_COOL days");
eq(PL.nextLeftover(["bakery"], c, 11, fc), null, "only resting families: nothing today");
PL.pruneCool(fc, 12);
eq(Object.keys(fc), [], "prune cooled families");
eq(PL.nextLeftover(["cottage_s", "bakery"], c, 11, {}).index, 1, "index of the pick in the list");

// skins
eq(PL.skinFor("prestige", ["a", "b", "c", "d"], 2), "d", "prestige town: stone skin");
eq(PL.skinFor("prestige", ["a", "b"], 2), "b", "prestige falls back");
eq(PL.skinFor("craft", ["a", "b", "c"]), "c", "craft skin");
eq(PL.skinFor("homes", ["a", "b"], 0, 3), "b", "homes by street parity (odd)");
eq(PL.skinFor("homes", ["a", "b"], 0, 4), "a", "homes by street parity (even)");
eq(PL.skinFor("edge", ["c"], 0), "c", "only skin there is");

// relief
const flat = Array.from({ length: 100 }, (_, i) => ({ h: 70 + (i % 3 === 0 ? 1 : 0), wet: false }));
ok(PL.judgeLot(flat, 70).ok, "a flat lot passes");
const boulder = flat.map((c2, i) => (i === 5 ? { h: 82, wet: false } : c2));
ok(PL.judgeLot(boulder, 70).ok, "one boulder no longer vetoes");
const oneWet = flat.map((c2, i) => (i === 9 ? { h: 70, wet: true } : c2));
ok(PL.judgeLot(oneWet, 70).ok, "one wet cell no longer vetoes");
const pond = flat.map((c2, i) => (i < 12 ? { h: 70, wet: true } : c2));
eq(PL.judgeLot(pond, 70).why, "water", "a pond (12 %) is refused");
const slope = flat.map((c2, i) => ({ h: 60 + Math.floor(i / 4), wet: false }));
eq(PL.judgeLot(slope, 70).why, "bad cells", "a real slope is refused");
const big = Array.from({ length: 400 }, () => ({ h: 70, wet: false })).map((c2, i) => (i < 18 ? { h: 90, wet: false } : c2));
ok(PL.judgeLot(big, 70).ok, "a big box gets a 5 % budget (18 of 400)");
eq(PL.percentile([1, 2, 3, 4, 5], 0.5), 3, "median");

// fillers
eq(PL.fillerFor(0, 3, 9), null, "under 4: nothing");
eq(PL.fillerFor(0, 9, 9), null, "a lot-sized stretch is a lot, not a filler");
ok(PL.FILLERS.includes(PL.fillerFor(10, 16, 9, 2)), "a 6-long stretch gets a filler");
eq(PL.fillerFor(10, 16, 9, 2), PL.fillerFor(10, 16, 9, 2), "deterministic");
ok(PL.FILLER_W[PL.fillerFor(0, 4, 9)] <= 2, "a 4-long stretch only takes a 2-wide filler or less");

// weathering
eq(PL.bandOf(0), 0, "new house band 0");
eq(PL.bandOf(85), 2, "85 days band 2");
eq(PL.bandOf(10000), PL.WEATHER.bands, "capped");
eq(PL.fineOf(2), 0, "no fine below the bad level");
eq(PL.fineOf(3), 3 * 4 * 12, "fine at the bad level");

console.log(`test_plan: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
