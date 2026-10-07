// test_alarm.mjs — 1.3.232 #3: the bell rings only for hostiles inside/near the town (not cave mobs far below, not a
// lone harmless one in daylight), and a monster-rung bell clears when they are gone.
import * as P from "../pw_civ_people.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const town = { cx: 0, cy: 64, cz: 0, r: 64 };
const m = (x, y, z, t = "minecraft:zombie") => ({ x, y, z, typeId: t });
const NIGHT = 18000, DAY = 6000;
ok(typeof P.alarmThreat === "function", "alarmThreat exists");
if (typeof P.alarmThreat === "function") {
  ok(P.alarmThreat([m(5, 64, 5), m(-10, 65, 3), m(20, 63, -8)], town, NIGHT).ring, "3 zombies in the streets at night ring");
  ok(!P.alarmThreat([m(5, 20, 5), m(-10, 15, 3), m(20, 30, -8)], town, NIGHT).ring, "3 cave mobs 30+ below never ring");
  ok(!P.alarmThreat([m(90, 64, 5), m(5, 64, 5)], town, NIGHT).ring, "outside the border does not count");
  ok(!P.alarmThreat([m(40, 64, 40, "minecraft:witch")], town, DAY).ring, "a lone witch walking by in daylight: no bell");
  ok(!P.alarmThreat([m(40, 64, 40), m(45, 64, 30), m(50, 64, 50)], town, DAY).ring, "daylight: 3 far from the square: no bell");
  ok(P.alarmThreat([m(4, 64, 4), m(-6, 64, 2), m(8, 64, -3)], town, DAY).ring, "daylight: 3 at the square: bell");
  ok(P.alarmThreat([], town, NIGHT).calm, "none: calm (a monster bell clears)");
  ok(P.alarmThreat([m(5, 20, 5)], town, DAY).calm, "only cave mobs: calm");
  ok(!P.alarmThreat([m(5, 64, 5)], town, NIGHT).calm, "one in town at night: not calm");
}
console.log(`test_alarm: ${pass} pass, ${fail} fail`);
if (fail) process.exit(1);
// #3 (b): his CIV-SHIFT said day 0 at sim day 137 — world.getDay() stuck (/time set resets the absolute time), so the
// rota's week never turned and a town whose rest day was day 0 kept its shops shut forever. dayCount counts dawns itself.
{
  ok(typeof P.dayCount === "function", "dayCount exists");
  if (typeof P.dayCount === "function") {
    let c = P.dayCount(null, 0, 1000);
    ok(c.n === 0, "starts at the world day");
    c = P.dayCount(c, 0, 18000); ok(c.n === 0, "same day, later");
    c = P.dayCount(c, 0, 1000); ok(c.n === 1, "/time set day (getDay stays 0, the clock went back): a new day");
    c = P.dayCount(c, 1, 200); ok(c.n === 2, "a natural dawn: +1 once");
    c = P.dayCount(c, 1, 300); ok(c.n === 2, "no double count");
    c = P.dayCount(c, 4, 100); ok(c.n === 5, "a skip of 3 world days");
  }
}
console.log(`test_alarm (b): ${pass} pass, ${fail} fail`);
if (fail) process.exit(1);
