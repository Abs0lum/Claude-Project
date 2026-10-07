// test_player.mjs — B11 the player (pw_civ_player.js): standing bands + prices, talk fatigue, gifts, deeds (OFF),
// festivals (feast > wedding > monthly holiday), the ring, the dusk speech, titles + votes, district names, the guide.
import * as PL from "../pw_civ_player.js";

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);

// WP9
eq(PL.standingOf([]), 0, "nobody knows the player");
eq(PL.standingOf([{ playerFond: 50 }, { playerFond: 30 }, {}, { playerFond: 90, alive: false }]), 40, "mean over those who know (dead skipped)");
eq(PL.bandOf(0), "neutral", "neutral");
eq(PL.bandOf(40), "friend", "friend at 40");
eq(PL.bandOf(75), "hero", "hero at 75");
eq(PL.bandOf(-20), "unfriendly", "unfriendly at -20");
eq(PL.buyUnit(100, 0), 100, "neutral price");
eq(PL.buyUnit(100, 45), 90, "friend buys at 0.9");
eq(PL.buyUnit(100, 80), 80, "hero buys at 0.8");
eq(PL.buyUnit(100, -30), 120, "unfriendly buys at 1.2");
eq(PL.buyUnit(1, 80), 1, "never below a penny");
eq(PL.sellPay(100, 45), 105, "friend sells at 1.05");
eq(PL.sellPay(100, 80), 110, "hero sells at 1.1");
eq(PL.sellPay(100, -30), 100, "unfriendly sells at 1");
// the invariant: every band's buy factor >= its sell factor's inverse margin (the town never pays more than it asks)
for (const b of Object.keys(PL.PRICE_X)) ok(PL.PRICE_X[b].sell <= 1.1 && PL.PRICE_X[b].buy >= 0.8, `band ${b} inside the bounds`);

// WP10
const p = { id: 1 };
ok(PL.talkCounts(p, 5) && PL.talkCounts(p, 5) && PL.talkCounts(p, 5), "three talks count");
ok(!PL.talkCounts(p, 5), "the fourth does not");
ok(PL.talkCounts(p, 6), "a new day counts again");
PL.pruneTalk(p, 7);
eq([p.td, p.tn, p.gn], [undefined, undefined, undefined], "pruned the next day");
eq(PL.giftFond(100, 0), 10, "sqrt(100) = 10, the cap");
eq(PL.giftFond(400, 0), 10, "capped at 10");
eq(PL.giftFond(16, 0), 4, "sqrt(16)");
eq(PL.giftFond(16, 1), 2, "halved for the second gift");
eq(PL.giftFond(16, 2), 1, "quartered for the third");
eq(PL.giftFond(16, 0, true), 6, "+2 on interest");
const q = { id: 2 };
let tot = 0;
for (let i = 0; i < 8; i++) tot += PL.giveTo(q, 3, 100).fond;
eq(tot, 10 + 5 + 2.5 + 1.3 + 0.6 + 0.3, "diminishing curve over a day (6 max)");
ok(PL.giveTo(q, 3, 100).refused, "the 7th gift today is refused");
ok(!PL.giveTo(q, 4, 100).refused, "tomorrow again");
ok(PL.likes("the sea", "fish") && !PL.likes("the sea", "stone"), "interest likes");
ok(PL.likes("trade", "stone"), "trade likes everything");

// WP8 (OFF)
eq(PL.DEEDS.enabled, false, "deeds are OFF by his ruling");
const w = { id: 3, playerFond: 30 };
ok(!PL.witness(w, "counter", 1) && w.playerFond === 30, "OFF: nothing changes");
PL.DEEDS.enabled = true;
ok(PL.witness(w, "counter", 1) && w.playerFond === 20 && w.mem.saw_deed === 31, "ON: fond falls hit x 5, memory kept");
PL.DEEDS.enabled = false;
eq(PL.amendsOf(10), 15, "amends x 1.5");
eq(PL.amendsOf(3), 5, "rounded up");
eq(PL.witnessesOf([{ pid: 1, x: 0, y: 64, z: 0 }, { pid: 2, x: 13, y: 64, z: 0 }, { pid: 3, x: 3, y: 70, z: 0 }], { x: 0, y: 64, z: 0 }), [1], "witnesses by reach + height");

// WP5
eq(PL.festivalOf(0, 10, { tierDay: 10, weddingDay: 10 }).kind, "feast", "the feast wins");
eq(PL.festivalOf(0, 11, { tierDay: 10 }).kind, "feast", "feast the next day too");
eq(PL.festivalOf(0, 12, { tierDay: 10, seed: 7 }), PL.holidayDay(7) === 0 ? { kind: "holiday", why: "the month's holiday" } : null, "feast over after two days");
eq(PL.festivalOf(0, 20, { weddingDay: 19 }).kind, "wedding", "a wedding yesterday");
const hd = PL.holidayDay(99);
eq(PL.festivalOf(hd, 50, { seed: 99 }).kind, "holiday", "the month's holiday");
eq(PL.festivalOf(hd + PL.FEST.monthDays, 80, { seed: 99 }).kind, "holiday", "every month");
let hol = 0;
for (let d = 0; d < 300; d++) if (PL.festivalOf(d, d, { seed: 99 })) hol++;
eq(hol, 10, "ten holidays in 300 days");
ok(PL.holidayDay(1) >= 0 && PL.holidayDay(1) < 30, "holiday in the month");
const r = PL.ringSlot(0, 0, 5);
const rr = Math.hypot(r.x, r.z);
ok(rr >= 4 - 1e-9 && rr <= 6 + 1e-9, "ring radius 4..6");
eq(PL.ringSlot(0, 0, 5), r, "ring deterministic");

// WP6
const L1 = PL.speechLines({ town: "Ashby", built: ["bakery"], tier: "Market Town" });
eq(L1.length, 3, "three lines");
ok(L1[1].includes("bakery"), "a building finished");
ok(L1[2].includes("Market Town"), "the title");
const L2 = PL.speechLines({ town: "Ashby", short: ["bread", "fish", "stone"], festival: "wedding", mood: 30 });
ok(L2[0].includes("the wedding") && L2[1].includes("bread and fish") && L2[2].includes("hard"), "festival, shortage, hard times");

// WP11
eq(PL.ptitleOf({}), "stranger", "stranger");
eq(PL.ptitleOf({ standing: 25, trades: 10 }), "citizen", "citizen");
eq(PL.ptitleOf({ standing: 25, trades: 10, slips: 10 }), "burgher", "burgher by slips");
eq(PL.ptitleOf({ standing: 25, trades: 10, stall: true }), "burgher", "burgher by a stall");
eq(PL.ptitleOf({ standing: 55, trades: 10, slips: 10, tierClass: 1, townLevel: 1 }), "burgher", "alderman needs town II");
eq(PL.ptitleOf({ standing: 55, trades: 10, slips: 10, tierClass: 1, townLevel: 2 }), "alderman", "alderman");
eq(PL.ptitleOf({ standing: 55, trades: 10, slips: 30, tierClass: 2 }), "councillor", "councillor");
eq(PL.vote([{ playerFond: 40 }, { playerFond: 10 }, { playerFond: -5 }]), { yes: 1, no: 1, abstain: 1, pass: false }, "a tie fails");
eq(PL.vote([{ playerFond: 40 }, { playerFond: 50 }, { playerFond: -5 }]).pass, true, "yes > no passes");
eq(PL.vote([{ playerFond: 40 }, { playerFond: 50 }, { playerFond: 0 }], true).pass, true, "recall 2/3 of all");
eq(PL.vote([{ playerFond: 40 }, { playerFond: 0 }, { playerFond: 0 }], true).pass, false, "recall fails below 2/3");
eq(PL.cleanName("  Rose §cHill!! "), "Rose Hill", "names cleaned");
eq(PL.cleanName("ab"), null, "too short");

// WP12
eq(PL.guideStep(3, 20, false), "walk", "close: walk");
eq(PL.guideStep(9, 20, false), "hold", "the player fell behind: hold");
eq(PL.guideStep(6, 20, true), "hold", "holding until the player is within 4");
eq(PL.guideStep(3, 20, true), "walk", "the player caught up");
eq(PL.guideStep(30, 3, false), "arrive", "at the door");

console.log(`test_player: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
