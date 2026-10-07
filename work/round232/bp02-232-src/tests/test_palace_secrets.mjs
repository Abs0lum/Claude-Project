// test_palace_secrets.mjs — 1.3.232 (#21 Part D, his OK 10-07 Q2): the PALACE II secret passages (pw_civ_palace_secrets.js).
// The rule: the secret doors stay SHUT; only the lord, his family (noble, child), guards and servants are MOVED from one end
// of a passage to the other when the place they are going to (bed / station) lies nearer that other end; one-way passages
// one direction only (the side their iron door opens from); "lore" entries are skipped; ordinary civs never.
// Covered: role filter, the nearer-end rule, two-way back, one-way, lore skip, unfinished pieces / blocked ends, rotations
// 0/90/180/270 (whole-model law + a hand-computed asymmetric cell + a passage across two pieces), decisions invariant
// under rotation, doors never opened (no block write, no command), >= 2 lord beds (two lords heading to their own beds).
import { readFileSync } from "node:fs";
import * as SEC from "../pw_civ_palace_secrets.js";
import { PALACE_SECRETS } from "../pw_civ_palace_secrets_data.js";
import { rotXZ, palaceGridRot } from "../pw_civ_clock.js";

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log("FAIL", m); } };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), `${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);

const ROT = { rotXZ, gridRot: (i, j, r) => palaceGridRot(i, j, r, 4) };       // the clock's helpers, PASSED IN (no circular import)
const byId = Object.fromEntries(PALACE_SECRETS.map((s) => [s.id, s]));
const PAL = (rot = 0) => ({ x0: 1000, z0: -500, rot, H: 70, n: 4 });
const all = () => true;
const W = (pal, cell) => SEC.palaceCellToWorld(pal, cell, ROT);
const feet = (pal, cell, dx = 0, dz = 0) => { const [x, y, z] = W(pal, cell); return [x + 0.5 + dx, y, z + 0.5 + dz]; };   // a body standing on the cell
const io = (o = {}) => ({ ...ROT, ready: all, clear: all, ...o });
const civ = (id, role, at, goal) => ({ id, role, at, goal });

// ---- the data
eq(PALACE_SECRETS.length, 41, "41 rows (palace2_secrets.json)");
const modes = {}; for (const s of PALACE_SECRETS) modes[s.mode] = (modes[s.mode] || 0) + 1;
eq(modes, { lore: 2, disguised: 22, hidden: 11, oneway: 6 }, "modes 22 disguised / 11 hidden / 6 oneway / 2 lore");
eq(SEC.ONEWAY_FROM, "hidden", "one-way passages move from the side their iron door opens from (palacegen2 iron_gate inside= is the HIDDEN end in all 6)");
ok(["lord", "noble", "child", "guard", "servant"].every((r) => SEC.MAY_USE.has(r)) && SEC.MAY_USE.size === 5, "MAY_USE = lord, noble, child, guard, servant");

// ---- rotations: the piece-wise mapping (grid permutation + each 64 x 64 piece rotated in place) == the whole 256 x 256 model
// rotated rigidly (rotXZ over 256), for every end of every row, at 0 / 90 / 180 / 270
for (let r = 0; r < 4; r++) {
  const pal = PAL(r);
  let bad = 0, n = 0;
  for (const s of PALACE_SECRETS) for (const c of [s.public, s.hidden]) {
    if (!c) continue;
    n++;
    const [wx, wz] = rotXZ(c[0], c[2], 256, 256, r);
    const got = W(pal, c);
    if (got[0] !== pal.x0 + wx || got[1] !== pal.H + c[1] || got[2] !== pal.z0 + wz) bad++;
  }
  ok(bad === 0 && n === 81, `rot ${r}: ${n} ends (41 public + 40 hidden) map like the whole model rotated (${bad} differ)`);
}
// a hand-computed ASYMMETRIC cell: H12's hidden end (145, -12, 73) — x != z, off the diagonals, below the court
eq(W(PAL(0), [145, -12, 73]), [1145, 58, -427], "rot 0 (gate west): x0 + 145, H - 12, z0 + 73");
eq(W(PAL(1), [145, -12, 73]), [1182, 58, -355], "rot 1 (gate north): x0 + 255 - 73, z0 + 145");
eq(W(PAL(2), [145, -12, 73]), [1110, 58, -318], "rot 2 (gate east): x0 + 255 - 145, z0 + 255 - 73");
eq(W(PAL(3), [145, -12, 73]), [1073, 58, -390], "rot 3 (gate south): x0 + 73, z0 + 255 - 145");
// a passage across TWO pieces (U5: kitchen cellar in piece 22 -> serving room in piece 21): the grid permutation matters
eq(SEC.pieceOf(byId.U5.public), "22", "U5 public end in piece 22");
eq(SEC.pieceOf(byId.U5.hidden), "21", "U5 hidden end in piece 21");
eq(W(PAL(1), byId.U5.public), [1000 + 255 - 133, 63, -500 + 181], "U5 public end at rot 1");
eq(W(PAL(3), byId.U5.hidden), [1000 + 105, 63, -500 + 255 - 152], "U5 hidden end at rot 3");

// ---- the ends that can be used: lore skipped, a row without a hidden end skipped, both pieces must be finished
{
  const ends = SEC.passageEnds(PAL(0), ROT, all);
  ok(ends.length === 39 && !ends.some((e) => e.id === "H16" || e.id === "H14"), `39 usable passages (lore H16 + H14 skipped): ${ends.length}`);
  const no21 = SEC.passageEnds(PAL(0), ROT, (q) => q !== "21");
  ok(!no21.some((e) => e.id === "U5") && no21.length < 39, "a passage with an end in an unfinished piece is not used");
}

// ---- the role filter: the same spot, the same goal — only the court roles move
{
  const pal = PAL(0), s = byId["H1-LORD'S STATE BEDCHAMBER"];
  const at = feet(pal, s.public), goal = feet(pal, [140, 6, 76]);           // a goal EAST of the spine: the hidden end is nearer
  const civs = ["lord", "noble", "child", "guard", "servant", "clerk", "cell", undefined, null].map((r, i) => civ(i + 1, r, at, goal));
  const mv = SEC.secretMoves(pal, civs, io());
  eq(mv.map((m) => m.id).sort(), [1, 2, 3, 4, 5], "lord, noble, child, guard, servant move; clerk, cell and ordinary civs never");
  ok(mv.every((m) => m.via === s.id && m.from === "public"), "through the lord's bedchamber jib door, public -> hidden");
  eq(mv[0].to, W(pal, s.hidden), "to the hidden end's cell");
}
// ---- the nearer-end rule
{
  const pal = PAL(0), s = byId["H1-LORD'S STATE BEDCHAMBER"];
  const at = feet(pal, s.public);
  eq(SEC.secretMoves(pal, [civ(1, "lord", at, feet(pal, [126, 6, 76]))], io()).length, 0, "goal on the public side (in the bedchamber): not moved");
  eq(SEC.secretMoves(pal, [civ(1, "lord", at, null)], io()).length, 0, "no goal (not walking anywhere): not moved");
  eq(SEC.secretMoves(pal, [civ(1, "lord", feet(pal, s.public, 0, 3), feet(pal, [140, 6, 76]))], io()).length, 0, "3 blocks from the end: not AT it (REACH 1.5)");
  // equidistant: the goal on the wall's line between the two ends (x 133) — strictly nearer is required
  eq(SEC.secretMoves(pal, [civ(1, "lord", at, [pal.x0 + 133.5, 76, pal.z0 + 76.5])], io()).length, 0, "equidistant: not moved");
}
// ---- two-way passages go back the other way (a hidden-mode space would otherwise trap a civ: unreachable from the gate)
{
  const pal = PAL(0), s = byId.H7a;
  eq(s.mode, "hidden", "H7a is a hidden-mode passage");
  const mv = SEC.secretMoves(pal, [civ(1, "servant", feet(pal, s.hidden), feet(pal, [152, 6, 56]))], io());
  ok(mv.length === 1 && mv[0].via === "H7a" && mv[0].from === "hidden", "hidden -> public when the goal lies nearer the public end");
  eq(mv[0].to, W(pal, s.public), "to the public end");
}
// ---- one-way: H10 Bridge of Sighs — the iron door opens from the palace side (the hidden end, x 156) only
{
  const pal = PAL(0), s = byId.H10;
  eq(s.mode, "oneway", "H10 is one-way");
  eq(SEC.secretMoves(pal, [civ(1, "guard", feet(pal, s.public), feet(pal, [150, 6, 22]))], io()).length, 0, "one-way: never from the public end (the prison side) back into the palace");
  const mv = SEC.secretMoves(pal, [civ(1, "guard", feet(pal, s.hidden), feet(pal, [170, 6, 22]))], io());
  ok(mv.length === 1 && mv[0].via === "H10" && mv[0].from === "hidden", "one-way: from the side the door opens from, toward the goal");
  for (const id of ["U1", "U4b", "H6b", "H6c", "U3"]) {
    const t = byId[id], away = (a, b) => [b[0] + (b[0] - a[0]) * 4, b[1], b[2] + (b[2] - a[2]) * 4];   // a goal beyond the far end
    const pub = SEC.secretMoves(pal, [civ(1, "guard", feet(pal, t.public), feet(pal, away(t.public, t.hidden)))], io()).length;
    const hid = SEC.secretMoves(pal, [civ(1, "guard", feet(pal, t.hidden), feet(pal, away(t.hidden, t.public)))], io()).length;
    ok(pub === 0 && hid === 1, `${id}: one direction only (hidden -> public): ${pub}/${hid}`);
  }
}
// ---- lore: never a way through (H16 has two recorded ends; H14 has no hidden end)
{
  const pal = PAL(0);
  eq(SEC.secretMoves(pal, [civ(1, "lord", feet(pal, byId.H16.public), feet(pal, [118, 0, 227]))], io()).length, 0, "lore H16 (the baize door): no move");
  eq(SEC.secretMoves(pal, [civ(1, "lord", feet(pal, byId.H14.public), feet(pal, [140, 6, 79]))], io()).length, 0, "lore H14 (no hidden end): no move, no error");
}
// ---- unfinished pieces and blocked ends
{
  const pal = PAL(0), s = byId.U5;
  const c = [civ(1, "servant", feet(pal, s.public), feet(pal, [150, -7, 100]))];
  eq(SEC.secretMoves(pal, c, io()).length, 1, "U5 used when both pieces stand");
  eq(SEC.secretMoves(pal, c, io({ ready: (q) => q !== "21" })).length, 0, "not while the hidden end's piece is unfinished");
  eq(SEC.secretMoves(pal, c, io({ clear: () => false })).length, 0, "not into a blocked cell (a civ is never put into a wall)");
}
// ---- the best end when two ends are in reach (H7b hidden 66 and H7c public 67, one block apart); one move a pass
{
  const pal = PAL(0);
  const mv = SEC.secretMoves(pal, [civ(1, "noble", feet(pal, [151, 6, 66], 0, 0.5), feet(pal, [151, 6, 70]))], io());
  ok(mv.length === 1 && mv[0].via === "H7c" && mv[0].from === "public", `at two ends: the move that brings him nearest (${mv.map((m) => m.via)})`);
}
// ---- >= 2 LORD BEDS (D-GH1007-LORDBEDS: "at least 2 — it's supposed to house a court"): two lords, each heading to his own
// bed (lord A's in piece 21, the lord's state bedchamber; lord B's in piece 22, the consort's), each takes his own way
{
  const pal = PAL(0);
  const bedA = feet(pal, [129, 6, 78]), bedB = feet(pal, [129, 6, 179]);
  eq([SEC.pieceOf([129, 6, 78]), SEC.pieceOf([129, 6, 179])], ["21", "22"], "the two lord beds' rooms lie in pieces 21 and 22");
  // the same spot (the kitchen end of the service tunnel U5): A's bed lies nearer the serving room (piece 21), B's does not
  const spot = feet(pal, byId.U5.public);
  const mv = SEC.secretMoves(pal, [civ(1, "lord", spot, bedA), civ(2, "lord", spot, bedB)], io());
  ok(mv.length === 1 && mv[0].id === 1 && mv[0].via === "U5", "same spot: lord A (bed in 21) takes U5, lord B (bed in 22) does not");
  // both in the hidden spine, each at the jib door of his own bedchamber: both move, each through his own door, in one pass
  const mv2 = SEC.secretMoves(pal, [civ(1, "lord", feet(pal, byId["H1-LORD'S STATE BEDCHAMBER"].hidden), bedA), civ(2, "lord", feet(pal, byId.H3.hidden), bedB)], io());
  eq(mv2.map((m) => [m.id, m.via, m.from]), [[1, "H1-LORD'S STATE BEDCHAMBER", "hidden"], [2, "H3", "hidden"]], "two lords, two passages, each toward his own bed");
  ok(Math.hypot(mv2[0].to[0] + 0.5 - bedA[0], mv2[0].to[2] + 0.5 - bedA[2]) < 4 && Math.hypot(mv2[1].to[0] + 0.5 - bedB[0], mv2[1].to[2] + 0.5 - bedB[2]) < 4, "each lands within 4 blocks of his own bed");
}
// ---- decisions are the same at every rotation (the rotation is rigid: distances keep)
{
  const scen = (pal) => [
    civ(1, "lord", feet(pal, byId.U5.public), feet(pal, [129, 6, 78])), civ(2, "lord", feet(pal, byId.U5.public), feet(pal, [129, 6, 179])),
    civ(3, "guard", feet(pal, byId.H10.hidden), feet(pal, [170, 6, 22])), civ(4, "guard", feet(pal, byId.H10.public), feet(pal, [150, 6, 22])),
    civ(5, "servant", feet(pal, byId.H12.public), feet(pal, [146, -12, 80])), civ(6, "clerk", feet(pal, byId.H12.public), feet(pal, [146, -12, 80])),
    civ(7, "noble", feet(pal, byId.H4.public), feet(pal, [126, 15, 80])),
  ];
  const sig = (r) => SEC.secretMoves(PAL(r), scen(PAL(r)), io()).map((m) => `${m.id}:${m.via}:${m.from}`).join(" ");
  const s0 = sig(0);
  ok(s0 === "1:U5:public 3:H10:hidden 5:H12:public 7:H4:public", `rot 0 decisions: ${s0}`);
  for (let r = 1; r < 4; r++) eq(sig(r), s0, `rot ${r} decides as rot 0`);
}

// ---- the world wrapper: teleports only, the walk is cancelled after a move, ordinary civs untouched, blocks never written
{
  const pal = PAL(1);
  const st = { id: 7, palace: pal };
  const writes = [];
  const block = (typeId) => new Proxy({ typeId, isAir: typeId === "minecraft:air" }, {
    get(t, k) { if (k in t) return t[k]; if (typeof k === "string" && /^set|^open|^toggle|^destroy|^place/.test(k)) return () => { writes.push(k); }; return undefined; },
    set(t, k) { writes.push(`set ${String(k)}`); return true; },
  });
  const tp = [], cancelled = [], logs = [];
  const body = (id, at) => ({ id: `v${id}`, isValid: true, location: { x: at[0], y: at[1], z: at[2] }, teleport(p) { tp.push([id, p]); } });
  const goalA = feet(pal, [140, 6, 76]);
  const people = { 1: { id: 1, name: "Ada", court: { r: "lord" } }, 2: { id: 2, name: "Bo" }, 3: { id: 3, name: "Cy", court: { r: "clerk" } } };
  const at = feet(pal, byId["H1-LORD'S STATE BEDCHAMBER"].public);
  const deps = {
    rot: ROT, bodies: [body(1, at), body(2, at), body(3, at)], personOf: (v) => people[Number(v.id.slice(1))] || null,
    goalOf: () => ({ x: goalA[0], y: goalA[1], z: goalA[2] }), ready: all, blockAt: () => block("minecraft:air"),
    cancel: (v) => cancelled.push(v.id), log: (l) => logs.push(l),
  };
  const r = SEC.runPalaceSecrets(st, deps);
  eq(r.moved, 1, "the wrapper moved one civ (the lord)");
  ok(tp.length === 1 && tp[0][0] === 1, "only the lord was teleported (the ordinary civ and the clerk were not)");
  const hid = W(pal, byId["H1-LORD'S STATE BEDCHAMBER"].hidden);
  eq([tp[0][1].x, tp[0][1].y, tp[0][1].z], [hid[0] + 0.5, hid[1], hid[2] + 0.5], "teleported onto the hidden end's cell (centre, feet)");
  eq(cancelled, ["v1"], "his walk is cancelled after the move (the schedule re-sends him from the new side)");
  eq(writes, [], "DOORS NEVER OPENED: no block was written (no setType / setPermutation / open)");
  ok(logs.length === 1 && logs[0].startsWith("[CIV-PALACE] secret") && logs[0].includes("Ada"), `one log line per move: ${logs[0]}`);
  // a blocked hidden end: no move
  tp.length = 0;
  const r2 = SEC.runPalaceSecrets(st, { ...deps, blockAt: () => block("minecraft:stone_bricks") });
  ok(r2.moved === 0 && tp.length === 0, "a blocked end: nobody is moved");
  // the 2 x 2 palace (no secrets data for it) and no palace: nothing
  eq(SEC.runPalaceSecrets({ id: 1, palace: { x0: 0, z0: 0, rot: 0, H: 64 } }, deps).moved, 0, "the 2 x 2 palace (n 2 / legacy): no passages");
  eq(SEC.runPalaceSecrets({ id: 1 }, deps).moved, 0, "no palace: nothing");
}
// ---- the module never writes a block or runs a command, and imports neither the clock nor the engine (no circular import)
{
  const src = readFileSync(new URL("../pw_civ_palace_secrets.js", import.meta.url), "utf8").replace(/\/\/.*$/gm, "").replace(/\/\*[\s\S]*?\*\//g, "");
  ok(!/setType|setPermutation|runCommand|open_bit|setBlockType|fillBlocks|\.place\(/.test(src), "no block write / command in the module's code");
  ok(!/from\s+["']\.\/pw_civ_clock\.js["']/.test(src) && !/@minecraft\/server/.test(src), "no import of the clock or the engine (helpers are passed in)");
}

console.log(`test_palace_secrets: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
