// test_lanes.mjs — contour lanes (pw_civ_lanes.js) on synthetic hills. Usage: node tests/test_lanes.mjs
import * as LN from "../pw_civ_lanes.js";
let n = 0, bad = 0;
const ok = (name, cond, info) => { n++; if (!cond) bad++; console.log(`${cond ? "PASS" : "FAIL"} ${n} ${name}${cond ? "" : " — " + JSON.stringify(info).slice(0, 400)}`); };
// a round hill: ground falls 1 per 2 cells from y 140 at (0, 0)
const cone = { at: (x, z) => Math.round(140 - Math.hypot(x, z) / 2), isWater: () => false };
// on the contour y 110 (radius 60), heading along it (tangent) from (60, 0): +z
const lane = LN.planLane(cone, [60, 0], [0, 1], 110, null);
ok("a lane is planned around the hill", !!lane && lane.cells.length >= LN.LANE_MIN, lane && lane.cells.length);
const allOk = lane.cells.every(([x, z], i) => LN.laneCellOk(cone, x, z, lane.dirs[i], 110, null));
ok("every lane cell keeps cut / fill within 4 across the width", allOk);
const steps = lane.cells.every((c, i) => i === 0 || Math.abs(c[0] - lane.cells[i - 1][0]) + Math.abs(c[1] - lane.cells[i - 1][1]) === 1);
ok("the centre line is 4-connected (no jumps)", steps);
ok("it turns (follows the contour) with legs of >= 7", lane.turns >= 1 && lane.legs.every((L, i) => i === lane.legs.length - 1 || L.len >= LN.LEG_MIN), lane.legs);
const rad = lane.cells.map(([x, z]) => Math.hypot(x, z));
ok("it stays on the hill's flank (radius 52..68: the contour +-8)", rad.every((r) => r >= 52 && r <= 68), [Math.min(...rad), Math.max(...rad)]);
ok("never revisits a cell", new Set(lane.cells.map((c) => c.join(","))).size === lane.cells.length);
// blocked cells stop it
const blk = (x, z) => z > 10 && z < 14;
const short = LN.planLane(cone, [60, 0], [0, 1], 110, blk);
{ const cellsIn = short ? short.cells.filter(([x, z], i) => { const v = [short.dirs[i][1], -short.dirs[i][0]]; for (let w = -LN.LANE_HALF; w <= LN.LANE_HALF; w++) if (blk(x + w * v[0], z + w * v[1])) return true; return false; }) : [];
  ok("a blocked band is never crossed (no lane cell's width touches it)", cellsIn.length === 0, cellsIn.slice(0, 4)); }
// house slots on a leg: front at w = +-4, floor = lane H, inside the leg's ends
const def = { size: [8, 20, 9] };
const legIdx = lane.legs.findIndex((L) => L.len >= 20);
const s1 = LN.laneSlot(lane, legIdx, 1, def, 4, LN.LANE_HALF + 2), s2 = LN.laneSlot(lane, legIdx, -1, def, 4, LN.LANE_HALF + 2);
ok("slots on both sides of a long leg", !!s1 && !!s2, { legIdx, legs: lane.legs });
const f = LN.legFrame(lane, legIdx);
const twOf = (x, z) => { const dx = x - f.ox, dz = z - f.oz; return [dx * f.ux + dz * f.uz, dx * f.vx + dz * f.vz]; };
const wsOf = (s) => { const a = twOf(s.box[0], s.box[2]), b = twOf(s.box[1], s.box[3]); return [Math.min(a[1], b[1]), Math.max(a[1], b[1])]; };
ok("side +1 box spans w 4..11, side -1 w -11..-4", JSON.stringify(wsOf(s1)) === "[4,11]" && JSON.stringify(wsOf(s2)) === "[-11,-4]", [wsOf(s1), wsOf(s2)]);
ok("a slot's floor is the lane's level", s1.H === 110 && s2.H === 110);
ok("a slot past the leg's end is refused", LN.laneSlot(lane, legIdx, 1, def, 4, lane.legs[legIdx].len) === null);
// the gallery: 3 wide x 4 high under every cell, lined; the branch reaches w +-2..3
const g = LN.laneGalleryCells(lane);
ok("gallery: 12 air cells per lane cell (fewer at corners, shared)", g.air.length >= lane.cells.length * 9 && g.air.length <= lane.cells.length * 12, g.air.length);
ok("gallery rows H-11..H-8", g.air.every((c) => c[1] >= 99 && c[1] <= 102));
const br = LN.laneBranchCells(lane, legIdx, s1.shaftT, 1);
ok("a branch: w 2..3 x 4 rows = 8 cells, beside the gallery", br.length === 8 && br.every((c) => { const [, w] = twOf(c[0], c[2]); return w === 2 || w === 3; }));
console.log(`test_lanes: ${n - bad}/${n} passed (lane ${lane.cells.length} cells, ${lane.legs.length} legs, turns ${lane.turns})`);
if (bad) process.exitCode = 1;
