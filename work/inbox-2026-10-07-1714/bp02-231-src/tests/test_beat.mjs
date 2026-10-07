// test_beat.mjs — 1.3.228 (B1 / BF1): the heartbeat's dispatcher on 2,000 synthetic ticks with a fake clock: no two heavy
// beats in one tick, every beat at its slot and period, an over-budget beat skips its next turn once, the optional beats
// are shed at a measured MSPT of 80 (the kit queue halves) and come back when it falls, a throwing beat never stops the
// others, the [CIV-BEAT] line every 1,200 ticks
import { createBeat, PLAN, FRAME, LOG_EVERY } from "../pw_civ_beat.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };

function harness(gap = 50) {
  const h = { now: 0, gap, logs: [], ran: new Map(), cost: new Map() };
  h.beat = createBeat({ clock: () => h.now, log: (s) => h.logs.push(s) });
  h.add = (name, o = {}) => {
    h.ran.set(name, []);
    return h.beat.register(name, { ...o, fn: (t) => { h.ran.get(name).push(t); const c = h.cost.get(name); if (c) h.now += typeof c === "function" ? c(t) : c; if (o.throws) throw new Error("boom"); } });
  };
  h.run = (t0, t1) => { for (let t = t0; t < t1; t++) { h.now += h.gap; h.beat.step(t); } };
  return h;
}

// 1. the real slot plan: every beat of PLAN, 2,000 ticks, no shedding
{
  const h = harness(50);
  for (const name of Object.keys(PLAN)) h.add(name);
  const heavyAt = new Map();
  const T0 = 1000, T1 = 3000;                                   // 2,000 synthetic ticks (an arbitrary start: the slots are absolute)
  h.run(T0, T1);
  for (const [name, ticks] of h.ran) if (PLAN[name].heavy) for (const t of ticks) heavyAt.set(t, (heavyAt.get(t) || []).concat(name));
  const clash = [...heavyAt].filter(([, ns]) => ns.length > 1);
  ok(clash.length === 0, `two heavy beats in one tick: ${JSON.stringify(clash.slice(0, 3))}`);
  // every beat at its period: single-slot beats exactly every `every`; the kit queue on its 8 slots of each 20
  for (const [name, ticks] of h.ran) {
    const p = PLAN[name];
    if (Array.isArray(p.slot)) {
      ok(ticks.every((t) => p.slot.includes(t % FRAME)), `${name} off its slots`);
      ok(ticks.length === (T1 - T0) / FRAME * p.slot.length, `${name} runs ${ticks.length}`);
      continue;
    }
    const frame = Math.max(p.every, FRAME);
    ok(ticks.length > 0, `${name} never ran`);
    ok(ticks.every((t) => t % p.every === p.slot % p.every && (p.every < FRAME || t % frame === p.slot)), `${name} off its slot ${p.slot}`);
    let even = true;
    for (let i = 1; i < ticks.length; i++) if (ticks[i] - ticks[i - 1] !== p.every) even = false;
    ok(even, `${name} period ${p.every} broken`);
    ok(Math.abs(ticks.length - (T1 - T0) / p.every) <= 1, `${name} ran ${ticks.length} times in ${T1 - T0} ticks (every ${p.every})`);
  }
  ok(h.beat.state.shed === false, "no shedding at 50 ms");
  // the [CIV-BEAT] line every LOG_EVERY ticks, with every system's counters
  const lines = h.logs.filter((l) => l.startsWith("[CIV-BEAT] {"));
  ok(lines.length === Math.floor((T1 - T0 - 1) / LOG_EVERY), `[CIV-BEAT] lines ${lines.length}`);
  const rep = JSON.parse(lines[0].slice(11));
  ok(rep.sys && rep.sys.walk && rep.sys.walk.length === 7 && rep.sys.walk[1] === LOG_EVERY / 10, `report shape ${lines[0].slice(0, 200)}`);
  ok(rep.mspt === 50, `mean MSPT ${rep.mspt}`);
}

// 2. over budget: a beat that takes > 2 x its budget skips its next turn once (counted), then runs again
{
  const h = harness(50);
  h.add("work", { every: 10, slot: 3, budgetMs: 40 });
  h.cost.set("work", (t) => (t === 23 ? 100 : 5));            // the 3rd turn (tick 23) takes 100 ms > 80
  h.run(0, 100);
  const tk = h.ran.get("work");
  ok(JSON.stringify(tk) === JSON.stringify([3, 13, 23, 43, 53, 63, 73, 83, 93]), `over-budget skip: ${tk}`);
  const sy = h.beat.systems.find((x) => x.name === "work");
  ok(sy.over === 1 && sy.skipped === 1, `counted over ${sy.over} skipped ${sy.skipped}`);
  // within budget x 2 (75 ms of 40): no skip
  const h2 = harness(50);
  h2.add("work", { every: 10, slot: 3, budgetMs: 40 });
  h2.cost.set("work", 75);
  h2.run(0, 60);
  ok(h2.ran.get("work").length === 6, "75 ms of a 40 ms budget is not over");
  // no budget (0): never skipped
  const h3 = harness(50);
  h3.add("save", { every: 20, slot: 19, budgetMs: 0 });
  h3.cost.set("save", 900);
  h3.run(0, 200);
  ok(h3.ran.get("save").length === 10, "a beat without a budget is never skipped");
}

// 3. load shedding at a measured MSPT of 80: optional beats skip, the kit queue halves; at 50 they come back
{
  const h = harness(80);
  h.add("shop", { ...PLAN.shop });
  h.add("room", { ...PLAN.room });
  h.add("kitqueue", { ...PLAN.kitqueue });
  h.add("walk", { ...PLAN.walk });
  h.run(0, 400);                                                // 80 ms a tick: shed from the 21st tick on
  ok(h.beat.state.shed === true, "shedding at MSPT 80");
  const shopRan = h.ran.get("shop"), roomRan = h.ran.get("room");
  ok(shopRan.every((t) => t < 21) && roomRan.every((t) => t < 21), `optional beats shed (shop ${shopRan}, room ${roomRan.slice(0, 5)})`);
  const kq = h.ran.get("kitqueue").filter((t) => t >= 40);
  ok(kq.length === (400 - 40) / FRAME * 8 / 2, `kit queue halved: ${kq.length}`);
  ok(h.ran.get("walk").filter((t) => t >= 40).length === (400 - 40) / 10, "a required beat is never shed");
  h.gap = 50;
  h.run(400, 800);
  ok(h.beat.state.shed === false, "shedding ends at MSPT 50");
  ok(h.ran.get("shop").some((t) => t >= 400) && h.ran.get("room").some((t) => t >= 450), "optional beats back");
  const sy = h.beat.systems.find((x) => x.name === "shop");
  ok(sy.shedSkips > 0, "shed turns counted");
  // a short spike (10 slow ticks) sheds only while it is inside the 20-tick window
  const h2 = harness(50);
  h2.add("shop", { ...PLAN.shop });
  h2.run(0, 100); h2.gap = 300; h2.run(100, 110); h2.gap = 50; h2.run(110, 135);
  ok(h2.beat.state.shed === false, "a 10-tick spike: shedding over 25 ticks later");
  h2.run(135, 400);
  ok(JSON.stringify(h2.ran.get("shop")) === JSON.stringify([9, 209, 309]), `the spike cost one shop turn (${h2.ran.get("shop")})`);
}

// 4. a throwing beat is caught and counted; the others in its tick still run; unregister stops it; bad periods refused
{
  const h = harness(50);
  h.add("bad", { every: 10, slot: 1, throws: true });
  h.add("good", { every: 10, slot: 1 });
  h.run(0, 50);
  ok(h.ran.get("good").length === 5 && h.ran.get("bad").length === 5, "a throw stops nothing");
  ok(h.beat.systems.find((x) => x.name === "bad").errors === 5 && h.logs.some((l) => l.includes("bad error")), "throws counted and logged");
  h.beat.unregister("bad");
  h.run(50, 100);
  ok(h.ran.get("bad").length === 5, "unregistered");
  let refused = false; try { h.beat.register("odd", { every: 7, slot: 0, fn: () => {} }); } catch { refused = true; }
  ok(refused, "every 7 refused (must divide 20 or be a multiple)");
  // re-registering a name replaces it (the walk instrument)
  h.add("good", { every: 20, slot: 13 });
  h.run(100, 140);
  ok(JSON.stringify(h.ran.get("good")) === JSON.stringify([113, 133]), `re-register replaces (${h.ran.get("good")})`);
}

// 5. every beat of the plan has a budget rule and a legal period
for (const [name, p] of Object.entries(PLAN)) ok((FRAME % p.every === 0 || p.every % FRAME === 0) && p.budgetMs >= 0, `${name} plan`);

console.log(`test_beat: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
