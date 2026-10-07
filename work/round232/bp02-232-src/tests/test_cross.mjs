// test_cross.mjs — 1.3.232 (#28): CROSSROADS FIRST (his 04:12 CT 10-07: "We should also use more crossroads").
// Mechanism (pw_civ_clock.js sideStreetJob): the side-street search lists its junction windows street by street (the main
// street first), side +1 before side -1, nearest the middle first, and opens ONE street per run — so a town opened every
// +1 side street of its main street before the first -1 one, and a crossroads (two tees at one t: the cross13 piece,
// queueJunction) formed only when a -1 search happened to land where a +1 tee already stood. Now, INSIDE each base street's
// own windows (the base order — main first — is kept: no runaway growth along one line), a window that completes a
// crossroads (a tee already stands at that t on the other side) comes first; the rest keep their order. closeBlocks the
// same, counting both ends of the connector.
// 1 PLAN.crossFirst: stable; grouped by base street in first-seen order; completes desc inside a group; no tees -> unchanged.
// 2 the clock's junction windows (cut from pw_civ_clock.js, run on stand-ins): after a +1 tee at t, the main street's next
//   job is the -1 window at the same t (a crossroads), and the side street's outward reserved window (its own tee at `half`
//   on the other side) completes a crossroads too.
// 3 wiring: sideStreetJob and closeBlocks order their jobs through PLAN.crossFirst.
import { readFileSync } from "node:fs";
import * as PLAN from "../pw_civ_plan.js";
let pass = 0, fail = 0;
const ok = (c, m, extra) => { if (c) pass++; else { fail++; console.log("FAIL", m, extra === undefined ? "" : JSON.stringify(extra)); } };
const crossFirst = PLAN.crossFirst || (() => null);

// ------------------------------------------------------------------------------------------------ 1. PLAN.crossFirst
{
  const main = { id: 1, tees: [{ t: 56, side: 1 }] }, side2 = { id: 2, tees: [{ t: 70, side: -1 }] };
  const completes = ([base, side, tj]) => ((base.tees || []).some((j) => j.t === tj && j.side === -side) ? 1 : 0);
  const jobs = [[main, 1, 112], [main, 1, 0], [main, -1, 56], [main, -1, 112], [side2, 1, 70], [side2, 1, 126]];
  const out = crossFirst(jobs, completes, (j) => j[0]);
  const key = (j) => `${j[0].id}:${j[1]}:${j[2]}`;
  ok(Array.isArray(out) && out.map(key).join(" ") === "1:-1:56 1:1:112 1:1:0 1:-1:112 2:1:70 2:1:126",
     "crossFirst: inside the main street the window that completes a crossroads first, the rest in their order; the side street after the main (base order kept)", out && out.map(key));
  ok(out !== jobs && jobs.map(key).join(" ") === "1:1:112 1:1:0 1:-1:56 1:-1:112 2:1:70 2:1:126", "crossFirst: the input list is not changed");
  const none = [[{ id: 3, tees: [] }, 1, 5], [{ id: 3, tees: [] }, -1, 5]];
  ok(crossFirst(none, completes, (j) => j[0]).map((j) => j[2] + ":" + j[1]).join(" ") === "5:1 5:-1", "crossFirst: no tees -> the order is unchanged");
  // closeBlocks: a connector may complete a crossroads at both ends (2 before 1 before 0)
  const b = { id: 10 }, o1 = { id: 11 }, o2 = { id: 12 };
  const jobs2 = [[b, 1, o1, 0, 0], [b, 1, o1, 56, 1], [b, 1, o2, 112, 2], [b, -1, o2, 168, 1]];
  const out2 = crossFirst(jobs2, (j) => j[4], (j) => j[0]);
  ok(out2 && out2.map((j) => j[3]).join(" ") === "112 56 168 0", "crossFirst: closeBlocks counts both ends (2, then 1s in order, then 0)", out2 && out2.map((j) => j[3]));
  ok(crossFirst([], completes, (j) => j[0]).length === 0, "crossFirst: an empty list");
}

// ------------------------------------------------------------------------------------------------ 2. the clock's windows
const clk = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
const cut = (name, src = clk) => {
  const i = src.indexOf(`function ${name}(`);
  if (i < 0) return null;
  let k = src.indexOf("{", i), depth = 0, j = k;
  for (; j < src.length; j++) { if (src[j] === "{") depth++; else if (src[j] === "}" && --depth === 0) break; }
  return src.slice(i, j + 1);
};
{
  const env = { JW: 13, GRID_PITCH: 56, kitHAt: (street, q) => (q >= street.tmin && q < street.tmin + street.H.length ? 70 : undefined), winReleased: () => false, tOffOf: (s) => s.tOff || 0 };
  const src = [cut("gridWindowsIn"), cut("junctionWindows")].join("\n");
  const junctionWindows = new Function(...Object.keys(env), `${src}; return junctionWindows;`)(...Object.values(env));
  // a main street 300 cells (t 0..299), middle 150, grid at 150 +- 56k; the square on its -1 side at t 150..161
  const main = { id: 1, kind: "kit", tmin: 0, H: new Array(300).fill(70), tees: [], access: [], reserved: [], mid: 150, sqT: [150, 161] };
  const st = { gridMid: 150, streets: [main] };
  const build = () => { const jobs = []; for (const base of st.streets) for (const side of [1, -1]) for (const tj of junctionWindows(st, base, side)) jobs.push([base, side, tj]); return jobs; };
  const completes = ([base, side, tj]) => ((base.tees || []).some((j) => j.t === tj && j.side === -side) ? 1 : 0);
  const before = build();
  ok(before.length && before[0][1] === 1 && before[0][2] === 150, "windows: the first search opens +1 at the grid line opposite the square (t 150)", before.map((j) => [j[1], j[2]]));
  main.tees.push({ t: 94, side: 1 });                                     // a side street opened at +1, t 94
  const old = build(), now = crossFirst(build(), completes, (j) => j[0]);
  ok(old[0][1] === 1 && old[0][2] !== 94, "windows (old order): the next search would open another +1 street (no crossroads)", old.slice(0, 3).map((j) => [j[1], j[2]]));
  ok(now[0][1] === -1 && now[0][2] === 94, "windows (crossFirst): the next search completes the crossroads at t 94 on the -1 side", now.slice(0, 3).map((j) => [j[1], j[2]]));
  ok(!now.some((j) => j[1] === -1 && j[2] === 150), "windows: the square's frontage never takes a tee (unchanged)");
  // the side street opened at +60 keeps its outward window reserved at its junction (`half`): it completes a crossroads
  const side2 = { id: 2, kind: "kit", role: "side", tmin: 0, H: new Array(153).fill(72), tees: [{ t: 70, side: -1 }], access: [], reserved: [[70, 82, 1]], mid: 76, tOff: 24 };
  st.streets.push(side2);
  const now2 = crossFirst(build(), completes, (j) => j[0]);
  const firstSide2 = now2.find((j) => j[0] === side2);
  ok(firstSide2 && firstSide2[1] === 1 && firstSide2[2] === 70, "windows: the side street's outward reserved window (straight on through its junction) leads its own list", now2.filter((j) => j[0] === side2).map((j) => [j[1], j[2]]));
  ok(now2[0][0] === main, "windows: the main street's windows still come first (base order kept)");
}

// ------------------------------------------------------------------------------------------------ 3. wiring
{
  const sj = cut("* sideStreetJob") || (() => { const i = clk.indexOf("function* sideStreetJob("); return i < 0 ? null : clk.slice(i, clk.indexOf("\n}\n", i)); })();
  const cb = cut("closeBlocks");
  ok(!!sj && /PLAN\.crossFirst\(/.test(sj), "wiring: sideStreetJob orders its jobs through PLAN.crossFirst");
  ok(!!cb && /PLAN\.crossFirst\(/.test(cb), "wiring: closeBlocks orders its jobs through PLAN.crossFirst");
}

console.log(`test_cross: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
