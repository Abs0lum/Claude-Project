// test_why.mjs — 1.3.228 (B2 / BF3): the why-idle code of a person (PEOPLE.whyOf) over a table of synthetic facts.
// Priority: home > food > site > route > the work module's reason > busy > rain > no site > no job; the tally cap.
import { whyOf, capTally, WHY } from "../pw_civ_people.js";
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const P = (o = {}) => ({ id: 1, name: "Ada", home: 7, job: 12, ...o });
const W = { phase: "work" };
const rows = [
  [null, W, "—", "no person: unknown"],
  [P(), { ...W, child: true }, "CHILD", "a child"],
  [P({ home: null }), { ...W, busy: true, noStock: true }, "NO_HOME", "home first (over food and work)"],
  [P(), { ...W, asleep: true }, "ASLEEP_CHUNK", "no body in loaded land"],
  [P(), { phase: "off", busy: true }, "OFF_SHIFT", "off shift"],
  [P(), { ...W, noStock: true, siteWaits: "stone", walk: "UNREACHABLE" }, "NO_STOCK", "food over site and route"],
  [P({ job: "builders" }), { ...W, siteWaits: "stone", walk: "NO_ROUTE", builderIdle: true }, "SITE_WAITS:stone", "site over route"],
  [P(), { ...W, walk: "UNREACHABLE", busy: true }, "UNREACHABLE", "route over busy"],
  [P(), { ...W, walk: "SLOTS_FULL" }, "SLOTS_FULL", "lead slots full"],
  [P(), { ...W, worker: "NO_FACE", busy: true }, "NO_FACE", "the work module's reason over busy"],
  [P(), { ...W, worker: "STOCK_FULL", busy: true }, "STOCK_FULL", "store full"],
  [P(), { ...W, busy: true }, "WORKING", "at work"],
  [P(), { ...W, wet: true }, "RAIN", "rain"],
  [P({ job: "builders" }), { ...W, builderIdle: true }, "NO_SITE", "a builder with no site"],
  [P({ job: null }), { ...W }, "NO_JOB", "no job"],
  [P(), { ...W }, "—", "a jobholder idle for no known reason"],
];
for (const [p, f, want, m] of rows) { const got = whyOf(p, f); ok(got === want, `${m}: ${got} (want ${want})`); }
for (const [, , want] of rows) ok(WHY[want.split(":")[0]] !== undefined, `${want} is described`);
const t = {}; for (let k = 0; k < 20; k++) t[`C${k}`] = 20 - k;
const c = capTally(t, 16);
ok(Object.keys(c).length === 16 && c.other === 5 + 4 + 3 + 2 + 1 && c.C0 === 20, `the tally keeps 15 + other (${JSON.stringify(c).length} chars)`);
console.log(`test_why: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
