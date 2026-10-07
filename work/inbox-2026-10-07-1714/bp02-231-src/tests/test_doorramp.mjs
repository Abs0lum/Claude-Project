// test_doorramp.mjs — 1.3.232 (#6, his 11:27 ruling): a house whose door stands on or within 1 cell of a sidewalk RAMP
// has its floor at the ramp's HIGH level (the ramp never rises across the door); slot.doorRamp records it.
// Usage: node tests/test_doorramp.mjs
import * as K from "../pw_civ_streets.js";
let n = 0, bad = 0;
const ok = (name, cond, info) => { n++; if (!cond) bad++; console.log(`${cond ? "PASS" : "FAIL"} ${n} ${name}${cond ? "" : " — " + String(JSON.stringify(info)).slice(0, 400)}`); };
const f = K.frameOf(0, 0, [1, 0], [0, 1]);
const def = { size: [8, 20, 9] };                       // door at the middle of the frontage (q 4)
const free = () => true;
// a run: 6 flat at 61, a 7-cell ramp 61 -> 62 (cells H 61,61,61,61,62,62,62), 10 flat at 62
const Hs = [61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62];
const kinds = "ffffffrrrrrrrffffffffff";
const st = { a: 0, b: Hs.length - 1, H: 61, Hs, kinds };
// mid 4.5 -> the first slot at at = 0: door q 4, ramp starts q 6 (2 away) -> no change; push it to at = 2 (door q 6 = ramp)
const sAt = (at) => K.placeAlong(f, { "1": [{ ...st }], "-1": [] }, def, null, at + 4.5, free, new Set(), 1, 1, []);
const s0 = sAt(0);
ok("door 2 cells from the ramp: floor = highest sidewalk of the frontage (62 via cells 10..)", s0 && s0.at === 0, s0);
const s2 = sAt(2);
const qd = s2 ? s2.doorT - st.a : null;
ok("slot at 2: the door's cell is a ramp cell", s2 && kinds[qd] === "r", { s2, qd });
ok("door on the ramp: floor = the ramp's high level 62", s2 && s2.H === 62, s2 && s2.H);
ok("door on the ramp: slot.doorRamp records the landing", s2 && s2.doorRamp && s2.doorRamp.H === 62, s2 && s2.doorRamp);
// door ON the low half of a ramp whose own frontage is flat 61 only below it: frontage 61..61 at at = 0 with ramp at q 5
const Hs2 = [61, 61, 61, 61, 61, 61, 61, 61, 61, 62, 62, 62, 62, 62];
const st2 = { a: 0, b: Hs2.length - 1, H: 61, Hs: Hs2, kinds: "fffffrrrrrrrff" };
const t = K.placeAlong(f, { "1": [st2], "-1": [] }, { size: [8, 20, 5] }, null, 2.5, free, new Set(), 1, 1, []);
// 5-wide house at at = 0: door q 2, frontage q 0..4 all 61 flat; ramp begins q 5 (3 away) -> floor 61, no doorRamp
ok("ramp 3 cells from the door: no change (floor 61, no doorRamp)", t && t.at === 0 && t.H === 61 && !t.doorRamp, t);
const u = K.placeAlong(f, { "1": [{ ...st2, kinds: "ffffrrrrrrrfff" }], "-1": [] }, { size: [8, 20, 5] }, null, 2.5, free, new Set(), 1, 1, []);
// ramp begins q 4 (2 away from door q 2) -> still no change; begins q 3 (1 away) -> floor = the ramp's high level 62
ok("ramp 2 cells from the door: no change", u && u.H === 61 && !u.doorRamp, u);
const v = K.placeAlong(f, { "1": [{ ...st2, kinds: "fffrrrrrrrffff" }], "-1": [] }, { size: [8, 20, 5] }, null, 2.5, free, new Set(), 1, 1, []);
ok("ramp 1 cell from the door (beside it): floor = 62, doorRamp", v && v.at === 0 && v.H === 62 && v.doorRamp && v.doorRamp.H === 62, v);
// 1.3.232 (c) lead ruling 11:4x: a PLATEAU frontage (rise 2) whose door stands on the low end of a chained ramp run passes the
// door-step check through its flat LANDING at the floor (step 0), not the ramp cell's own height (was: refused, step 2)
{
  // synthetic steep ramp run (q 4..8: 60,61,61,62,62) so the door cell q 4 sits 2 below the frontage's top 62
  const Hs3 = [60, 60, 60, 60, 60, 61, 61, 62, 62, 62, 62, 62];
  const st3 = { a: 0, b: Hs3.length - 1, H: 60, Hs: Hs3, kinds: "ffffrrrrrfff" };
  const w = K.placeAlong(f, { "1": [st3], "-1": [] }, { size: [8, 20, 9] }, null, 4.5, free, new Set(), 1, 1, [], { riseMax: 2, doorStep: 1 });
  ok("plateau at a ramp door: slot at 0 taken (door q 4 on the ramp at 60, floor 62)", w && w.at === 0 && w.H === 62 && w.doorRamp, w);
  ok("plateau at a ramp door: step measured from the landing = 0", w && w.plateau && w.plateau.step === 0 && w.plateau.rise === 2, w && w.plateau);
}
// 1.3.232 (a): the clock routes a raised ramp-door slot through the PLATEAU planner (P = slot.H: ground + ring filled up to
// the floor); if the plateau plan fails the slot is refused (never a floating floor)
{
  const { readFileSync } = await import("node:fs");
  const src = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
  ok("clock kitFree: doorRamp.raised > 0 takes the plateau path", /const rampDoor = !!\(slot\.doorRamp && slot\.doorRamp\.raised > 0\);/.test(src)
     && /if \(slot\.plateau \|\| rampDoor \|\| \(allowPlateau && land\.kind === "reject"\)\)/.test(src)
     && /if \(slot\.plateau \|\| rampDoor\) \{ why\.land\+\+; return false; \}/.test(src));
}
// 1.3.232 (b) lead ruling: a raised flat LANDING — the sidewalk cells (house side only, never curb / carriageway) at
// t = doorT-1 .. doorT+1 whose sidewalk H is below the floor are filled with full sidewalk blocks y H+1 .. floor
{
  const Hat = (t) => ({ 4: 61, 5: 61, 6: 62, 7: 62, 8: 62 })[t];   // a ramp's high level 62 reached at t 6; door t 5
  const L = K.landingCells(f, 1, 5, Hat, 62, "t");
  ok("landing: town width, side +1 -> rows w 11, 12 at t 4, 5 (H 61) only", L.length === 4 && L.every((c) => c.y0 === 62 && c.y1 === 62)
     && JSON.stringify(L.map((c) => [c.x, c.z])) === JSON.stringify([[4, 11], [4, 12], [5, 11], [5, 12]]), L);
  const V = K.landingCells(f, -1, 5, Hat, 62, "v");
  ok("landing: village width, side -1 -> rows w 0, 1, 2 (verge + sidewalk)", V.length === 6 && V.every((c) => c.z >= 0 && c.z <= 2), V);
  ok("landing: nothing when the sidewalk already stands at the floor", K.landingCells(f, 1, 7, Hat, 62, "t").length === 0);
}
{
  const { readFileSync } = await import("node:fs");
  const src = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
  ok("clock: plot records doorT + doorRamp; kitPlotAccess queues op landing; executor lays KIT.landingCells", src.includes("doorT: slot.doorT, doorRamp: slot.doorRamp || null")
     && src.includes('push({ op: "landing", sid: b.kit.sid, a: b.kit.doorT - 1, len: 3, H: b.kit.H, side: b.kit.side, doorT: b.kit.doorT })')
     && /op\.op === "landing"[\s\S]{0,200}KIT\.landingCells\(street\.f, op\.side, op\.doorT/.test(src));
}
console.log(`\n${n - bad}/${n} PASS`);
process.exit(bad ? 1 : 0);
