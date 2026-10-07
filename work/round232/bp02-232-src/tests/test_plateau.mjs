// test_plateau.mjs — 1.3.230 (PL) FRONTAGE PLATEAUS (owner backlog "frontage plateau": on hills the streets are mostly
// ramps and houses need flat frontage, so many street sides stay empty). Pure functions only:
//   * PLAN.padHeight — the pad stands at the street's height at the door, or one step above it, never below a sidewalk cell;
//   * PLAN.planPlateau — cut / fill volumes, the dials (cut / fill / face), retaining walls (downhill) and clad cut faces
//     (uphill, lifts of 3 with a bench), never into another plot, a street, water or a protected tree, and the DRAIN (the pad
//     drains along a gravel gutter to a grated drop into the street's sewer hall, or a soakaway where no hall is there);
//   * PLAN.plateauBillInto — the plot's first paid stage bill carries the plateau's stone and labour;
//   * KIT.placeAlong opts.riseMax — a frontage rising 2 is offered as a PLATEAU slot (door within one step, the sewer link
//     within one block); without opts nothing changes (test_frontage keeps the old law).
// Usage: node tests/test_plateau.mjs
import * as PLAN from "../pw_civ_plan.js";
import * as K from "../pw_civ_streets.js";

let n = 0, bad = 0;
const ok = (name, cond, info) => { n++; if (!cond) bad++; console.log(`${cond ? "PASS" : "FAIL"} ${n} ${name}${cond ? "" : " — " + String(JSON.stringify(info)).slice(0, 500)}`); };
const D = PLAN.PLATEAU;

// ------------------------------------------------------------------------------------------------ dials
// 1.3.232 (#7, ruling D-GH1007-PLATEAU 2026-10-07): the cut / fill dial is 9 (was 6)
ok("dials: cut 9, fill 9, lifts of 3, three face lifts, frontage rise 2, door step 1", D && D.cutMax === 9 && D.fillMax === 9 && D.lift === 3 && D.faceLifts === 3 && D.frontRise === 2 && D.doorStep === 1, D);

// ------------------------------------------------------------------------------------------------ pad height
{
  const a = PLAN.padHeight([70, 70, 70, 70, 70], 2);
  ok("pad: a level frontage -> P = the street, step 0", a.ok && a.P === 70 && a.rise === 0 && a.step === 0, a);
  const b = PLAN.padHeight([70, 70, 71, 71, 72, 72, 72, 72, 72], 4);
  ok("pad: rise 2, door at the upper half -> P = the highest sidewalk, step 0", b.ok && b.P === 72 && b.rise === 2 && b.step === 0, b);
  const c = PLAN.padHeight([70, 70, 70, 71, 71, 71, 72, 72, 72], 4);
  ok("pad: rise 2, door one below the top -> one step", c.ok && c.P === 72 && c.step === 1, c);
  const d = PLAN.padHeight([70, 70, 70, 70, 70, 71, 72, 72, 72], 1);
  ok("pad: rise 2 with the door two below the pad -> refused (door)", !d.ok && d.why === "door", d);
  const e = PLAN.padHeight([70, 71, 72, 73, 73, 73, 73, 73, 73], 6);
  ok("pad: rise 3 -> refused (rise)", !e.ok && e.why === "rise", e);
  const f = PLAN.padHeight([70, undefined, 70], 1);
  ok("pad: an unknown sidewalk cell -> refused (unknown)", !f.ok && f.why === "unknown", f);
}

// ------------------------------------------------------------------------------------------------ the plateau planner
// a site in plateau coordinates: q along the frontage (-1 .. fz are the side rings), d the depth from the corridor's edge
// (0 = the row against the street; depth = the rear ring row). gfun(q, d) -> ground height.
function site(gfun, extra = {}) {
  return {
    fz: 9, depth: 8, P: 70,
    Hring: (q) => 70, hallAt: (q) => 70,
    ground: (q, d) => ({ h: gfun(q, d), wet: false }),
    blocked: () => null,
    ...extra,
  };
}
const inBox = (o, fz = 9, depth = 8) => o.q >= 0 && o.q < fz && o.d >= 0 && o.d < depth;
const isRing = (o, fz = 9, depth = 8) => !inBox(o, fz, depth) && o.q >= -1 && o.q <= fz && o.d >= 0 && o.d <= depth;

{
  const r = PLAN.planPlateau(site(() => 70));
  ok("flat: ok, cut 0, fill 0, no walls / faces / berms", r.ok && r.cut === 0 && r.fill === 0 && !r.ops.some((o) => o.kind === "face" || o.kind === "berm" || (o.kind === "pad" && o.wall !== null)), r);
  ok("flat: the pad is the ring (2 x 9 side cells + 9 rear cells = 27), never a box cell", r.ops.filter((o) => o.kind === "pad").length === 27 && r.ops.filter((o) => o.kind === "pad").every((o) => isRing(o)), r.ops.filter((o) => o.kind === "pad").length);
  ok("flat: no op inside the house's box (the structure is its own cut and fill)", r.ops.every((o) => o.kind === "link" || !inBox(o)), r.ops.filter((o) => inBox(o)));
  ok("flat: the pad still drains — a sewer outlet with a 4-cell link over the hall's two top rows (H - 9 .. H - 8)", r.drain && r.drain.to === "sewer" && r.ops.filter((o) => o.kind === "link").length === 8 && r.ops.filter((o) => o.kind === "link").every((o) => o.y === 61 || o.y === 62) && r.ops.find((o) => o.kind === "outlet").yBot === 61, r.drain);
  ok("flat: earth 0, labour 0, stone only for the gutter and the grate's bed", r.bill.earth === 0 && r.bill.labourDays === 0 && r.bill.wages === 0 && r.bill.iron === 1 && r.bill.stone > 0, r.bill);
}

// an UPHILL slot: the ground rises 0.6 per cell away from the street (the street cut into the hill at the edge)
{
  const g = (q, d) => 70 + Math.floor(0.6 * (d + 1));
  // the OLD law (slotRelief): cut = the highest cell over the box, the 1-cell ring and the 3-cell rear bench + its wall
  // (d 0 .. depth + 3) — 70 + floor(0.6 * 12) = 77 -> cut 7 > CUT_MAX 6 -> rejected
  let oldCut = 0;
  for (let q = -1; q <= 9; q++) for (let d = 0; d <= 8 + 3; d++) oldCut = Math.max(oldCut, g(q, d) - 70);
  ok("uphill 0.6: the old law rejects it (cut over box + ring + bench > 6)", oldCut > 6, oldCut);
  const r = PLAN.planPlateau(site(g));
  ok("uphill 0.6: the plateau takes it (pad cut 5 <= cutMax)", r.ok && r.cut <= 6 && r.cut === 5, r.why || r.cut);
  const faces = r.ops.filter((o) => o.kind === "face");
  ok("uphill: a cut face stands behind the rear ring (rows beyond d = depth)", faces.length > 0 && faces.every((o) => o.d > 8 || o.q < -1 || o.q > 9), faces.slice(0, 4));
  const clads = faces.filter((o) => o.clad);
  ok("uphill: every clad wall is at most one lift (3) high", clads.length > 0 && clads.every((o) => o.clad[1] - o.clad[0] + 1 <= D.lift && o.clad[0] <= o.clad[1]), clads.slice(0, 4));
  ok("uphill: every face cell is cut to its lift (y = min(ground, P + 3 * row): one lift per cell of setback)", faces.every((o) => {
    const row = o.d > 8 ? o.d - 8 : o.q < -1 ? -1 - o.q : o.q - 9;
    return o.y === Math.min(o.g, 70 + D.lift * row);
  }), faces.slice(0, 6));
  ok("uphill: the gutter runs along the face's foot (the rear ring row)", r.ops.filter((o) => o.kind === "gutter" && o.d === 8).length === 11, r.ops.filter((o) => o.kind === "gutter").map((o) => [o.q, o.d]));
  // volumes, by hand: the ring cells' cut over P + the face rows' cut
  let cutVol = 0;
  for (const o of r.ops) { if (o.kind === "pad") cutVol += Math.max(0, o.g - 70); if (o.kind === "face") cutVol += Math.max(0, o.g - o.y); }
  ok("uphill: cut volume = sum of every cut column, fill volume 0 (no hollow)", r.cutVol === cutVol && r.fillVol === 0 && cutVol > 0, { cutVol: r.cutVol, mine: cutVol, fill: r.fillVol });
  let stone = 0;
  for (const o of r.ops) { if (o.kind === "face" && o.clad) stone += o.clad[1] - o.clad[0] + 1; if (o.kind === "gutter") stone += 2; if (o.kind === "pad" && o.wall !== null) stone += o.y - o.wall; if (o.kind === "berm") stone += Math.max(0, o.y - 1 - o.g); }
  ok("uphill: the bill's stone = clad + walls + berm faces + gutter (gravel + cobble bed)", r.bill.stone === stone, { bill: r.bill.stone, mine: stone });
  ok("uphill: labour = ceil(earth / earthPerDay) labourer days at the labourer's wage", r.bill.earth === r.cutVol + r.fillVol && r.bill.labourDays === Math.ceil(r.bill.earth / D.earthPerDay) && r.bill.wages === r.bill.labourDays * D.wageLabour, r.bill);
}

{
  const steep = PLAN.planPlateau(site((q, d) => 70 + Math.floor(1.6 * (d + 1))));
  ok("uphill 1.6 per cell: refused (cut)", !steep.ok && steep.why === "cut", steep.why);
  // a slope whose pad is fine but whose hill keeps climbing beyond three lifts (the face would be overtopped)
  const cliff = PLAN.planPlateau(site((q, d) => (d <= 8 ? 75 : 75 + 2 * (d - 8))));
  ok("a pad cut 5 into a hill that climbs 2 per cell behind it: refused once three lifts cannot hold it", !cliff.ok && cliff.why === "cut", cliff.why);
  const nat = PLAN.planPlateau(site((q, d) => (d <= 8 ? 70 : 70 + 2 * (d - 8))));
  ok("an uncut pad below a natural 2-per-cell rise: only its first step is clad (the natural hill is not cut)", nat.ok && nat.ops.filter((o) => o.kind === "face").every((o) => o.d === 9 && o.y === o.g && o.clad[0] === 71 && o.clad[1] === 72) && nat.cutVol === 0, nat.why || nat.ops.filter((o) => o.kind === "face").slice(0, 3));
  const easy = PLAN.planPlateau(site((q, d) => (d <= 8 ? 70 : 70 + (d - 8))));
  ok("a hill rising 1 per cell behind the pad: no face at all (a walkable natural slope)", easy.ok && !easy.ops.some((o) => o.kind === "face"), easy.ops.filter((o) => o.kind === "face"));
}

// a CROSS slope: the ground falls along the street (q): the high end is cut, the low end filled — the old law rejects any
// lot with cut > 3 AND fill > 3
{
  const g = (q, d) => 74 - q;                       // q -1 -> 75 (cut 5), q 9 -> 65 (fill 5)
  const r = PLAN.planPlateau(site(g));
  ok("cross slope (cut 5, fill 5): taken (the old law: both > 3 -> reject)", r.ok && r.cut === 5 && r.fill === 5, r.why || [r.cut, r.fill]);
  const walls = r.ops.filter((o) => o.kind === "pad" && o.wall !== null);
  ok("cross slope: the downhill ring cells are stone retaining walls (from the ground outside + 1 to P - 1)", walls.length > 0 && walls.every((o) => o.q === 9 || o.d === 8) && walls.every((o) => o.wall <= 69 && o.wall >= 70 - D.fillMax + 1), walls.map((o) => [o.q, o.d, o.wall]).slice(0, 6));
  const berms = r.ops.filter((o) => o.kind === "berm");
  ok("cross slope: a drop of 5..6 outside gets ONE berm lift (top at P - 3) beyond the wall (side q 10, or the rear corner)", berms.some((o) => o.q === 10) && berms.every((o) => o.y === 70 - D.lift && (o.q === 10 || o.d === 9)), berms.slice(0, 3));
  ok("cross slope: no berm where the ground outside lies within one of the lift (a 3-course wall + its top holds it)", !berms.some((o) => o.d === 9 && o.q === 8), berms.filter((o) => o.d === 9));
  ok("cross slope: the uphill end gets a clad face (q < -1)", r.ops.some((o) => o.kind === "face" && o.q < -1 && o.clad), r.ops.filter((o) => o.kind === "face").slice(0, 3));
  ok("cross slope: fill volume = the hollows of the ring + the berms", r.fillVol === r.ops.reduce((a, o) => a + (o.kind === "pad" ? Math.max(0, 70 - o.g) : o.kind === "berm" ? o.y - o.g : 0), 0), r.fillVol);
  const deep = PLAN.planPlateau(site((q, d) => 76 - 2 * q));
  ok("a drop beyond the fill dial (fill 12 > 9): refused (fill or drop)", !deep.ok && (deep.why === "fill" || deep.why === "drop" || deep.why === "cut"), deep.why);
}

// the NEVER-INTO rules
{
  const g = (q, d) => 74 - q;
  const street = PLAN.planPlateau(site(g, { blocked: (q, d) => (q === 10 ? "street" : null) }));
  ok("a berm needed into a street: refused (street)", !street.ok && street.why === "street", street.why);
  const water = PLAN.planPlateau(site(g, { blocked: (q, d) => (q === 10 ? "water" : null) }));
  ok("a berm needed into water: refused (water)", !water.ok && water.why === "water", water.why);
  const up = (q, d) => 70 + Math.floor(0.6 * (d + 1));
  const tree = PLAN.planPlateau(site(up, { blocked: (q, d) => (d === 10 && q === 4 ? "tree" : null) }));
  ok("a cut face through a protected tree: refused (tree)", !tree.ok && tree.why === "tree", tree.why);
  const treeFar = PLAN.planPlateau(site(up, { blocked: (q, d) => (d === 30 ? "tree" : null) }));
  ok("a tree beyond the works: no matter", treeFar.ok, treeFar.why);
  const plot = PLAN.planPlateau(site(up, { blocked: (q, d) => (d >= 10 ? "plot" : null) }));
  ok("the face meets another plot: it stops there (the neighbour's box holds the hill), no op in the plot", plot.ok && plot.ops.every((o) => o.d === undefined || o.d < 10), plot.why);
  const ringWet = PLAN.planPlateau(site(() => 70, { ground: (q, d) => ({ h: 70, wet: q === -1 && d === 3 }) }));
  ok("a wet ring cell: refused (water)", !ringWet.ok && ringWet.why === "water", ringWet.why);
  const ringPlot = PLAN.planPlateau(site(() => 70, { blocked: (q, d) => (q === 9 ? "plot" : null) }));
  ok("a ring cell inside another plot: refused (plot)", !ringPlot.ok && ringPlot.why === "plot", ringPlot.why);
  const unknown = PLAN.planPlateau(site(() => 70, { ground: (q, d) => (q === 9 && d === 2 ? undefined : { h: 70, wet: false }) }));
  ok("an unread ring cell: refused (unknown — the plot waits for its chunks)", !unknown.ok && unknown.why === "unknown", unknown.why);
  const skip = PLAN.planPlateau(site(() => 70, { skipBox: true, ground: (q, d) => (inBox({ q, d }) ? undefined : { h: 70, wet: false }) }));
  ok("skipBox (the job, after the house stands): the box is never read", skip.ok, skip.why);
}

// the DRAIN
{
  const g = (q, d) => 70 + Math.floor(0.6 * (d + 1));
  const lowRight = PLAN.planPlateau(site(g, { Hring: (q) => (q === 9 ? 69 : 70), hallAt: (q) => (q === 9 ? 69 : 70) }));
  ok("drain: the outlet takes the LOWER street end (q 9, H 69)", lowRight.ok && lowRight.drain.q === 9 && lowRight.drain.H === 69, lowRight.drain);
  const run = lowRight.drain.run;
  ok("drain: the run is contiguous, outside the box, and ends at the outlet beside the street (d 0)", run.length > 0 && run.every((c, i) => i === 0 || Math.abs(c[0] - run[i - 1][0]) + Math.abs(c[1] - run[i - 1][1]) === 1) && run.every(([q, d]) => !inBox({ q, d })) && run[run.length - 1][1] === 0 && run[run.length - 1][0] === 9, run);
  ok("drain: the run starts at the face's far corner (all of the face's gutter is upstream)", run[0][1] === 8 && run[0][0] === -1, run[0]);
  const out = lowRight.ops.find((o) => o.kind === "outlet");
  ok("drain: a grated drop from the pad down to the hall's top rows (H - 9 .. H - 8), then 4 link cells on both rows", out && out.y === 70 && out.yBot === 60 && out.to === "sewer" && lowRight.ops.filter((o) => o.kind === "link").length === 8 && lowRight.ops.filter((o) => o.kind === "link").every((o) => (o.y === 60 || o.y === 61) && o.q === 9), out);
  const higher = PLAN.planPlateau(site(g, { Hring: (q) => (q === -1 ? 72 : 69), hallAt: (q) => (q === -1 ? 72 : 69) }));
  ok("drain: never toward a street end above the pad", higher.ok && higher.drain.q === 9, higher.drain);
  const noHall = PLAN.planPlateau(site(g, { hallAt: () => undefined }));
  ok("drain: no sewer hall at either end (a bridge, a dead end) -> a soakaway (gravel, P - 8)", noHall.ok && noHall.drain.to === "soak" && noHall.ops.find((o) => o.kind === "outlet").yBot === 70 - D.soakDepth && !noHall.ops.some((o) => o.kind === "link"), noHall.drain);
  const neighbour = PLAN.planPlateau(site(g, { Hring: () => 70, blocked: (q, d) => (q === -2 ? "plot" : null) }));
  ok("drain: equal ends — the side whose gap is not shared with a built neighbour", neighbour.ok && neighbour.drain.q === 9, neighbour.drain);
}

// the BILL on the plot's first paid stage
{
  const bill = { mats: { timber: 40 }, blocks: 40, builderDays: 1, wages: 120 };
  const land = { kind: "plateau", stone: 90, iron: 1, labourDays: 3, wages: 216 };
  const b2 = PLAN.plateauBillInto(bill, land, 40, 120);
  ok("bill: stone and iron added to the materials", b2.mats.stone === 90 && b2.mats.iron === 1 && b2.mats.timber === 40, b2);
  ok("bill: the blocks grow, the builder days follow, the labourers' wages are added", b2.blocks === 131 && b2.builderDays === 4 && b2.wages === 4 * 120 + 216, b2);
  ok("bill: the original bill is not changed (a fresh object)", bill.blocks === 40 && !bill.mats.stone, bill);
  ok("bill: a plot without a plateau keeps its bill", PLAN.plateauBillInto(bill, { kind: "level" }, 40, 120) === bill && PLAN.plateauBillInto(bill, null, 40, 120) === bill);
}

// ------------------------------------------------------------------------------------------------ 1.3.232 (#7) THE DIAL AT 9
// D-GH1007-PLATEAU (owner ruling 2026-10-07): cutMax / fillMax 6 -> 9. The deeper pad keeps every law of the 6-dial: clad
// faces and walls of at most one lift (3), berm lifts at P - 3 / P - 6 / P - 9, protected trees never worked, and the
// house's own plot stage still clears its box (the box's cut is capped by the rows the stage's air reaches).
import { CIV_BUILDINGS } from "../pw_civ_buildings.js";
{
  const six = { cutMax: 6, fillMax: 6 };
  // UPHILL 0.9 per cell: the rear ring (d 8) stands at 70 + floor(0.9 * 9) = 78 -> pad cut 8
  const g9 = (q, d) => 70 + Math.floor(0.9 * (d + 1));
  const r = PLAN.planPlateau(site(g9));
  ok("dial 9: an uphill lot with pad cut 8 is taken", r.ok && r.cut === 8, r.why || r.cut);
  const r6 = PLAN.planPlateau(site(g9, { dials: six }));
  ok("dial 9: the same lot is refused at the old dial 6 (cut)", !r6.ok && r6.why === "cut", r6.why);
  const faces = (r.ops || []).filter((o) => o.kind === "face");
  ok("dial 9 uphill: every clad face is at most one lift (3) high", faces.length > 0 && faces.every((o) => !o.clad || (o.clad[0] <= o.clad[1] && o.clad[1] - o.clad[0] + 1 <= D.lift)), faces.filter((o) => o.clad && o.clad[1] - o.clad[0] + 1 > D.lift).slice(0, 4));
  ok("dial 9 uphill: every face cell is cut to its lift (y = min(ground, P + 3 * row))", faces.every((o) => {
    const row = o.d > 8 ? o.d - 8 : o.q < -1 ? -1 - o.q : o.q - 9;
    return o.y === Math.min(o.g, 70 + D.lift * row);
  }), faces.slice(0, 6));
  ok("dial 9 uphill: the pad (ring) is level at P, no op inside the box", r.ok && r.ops.filter((o) => o.kind === "pad").every((o) => o.y === 70 && isRing(o)) && r.ops.every((o) => o.kind === "link" || !inBox(o)));
  // DOWNHILL behind the house: ring at 68 (fill 2), the ground beyond falls 61, 59, 58, 57 (rows 1..4 out of the rear ring)
  // -> the first outside cell lies 9 below the pad (exposure 9): three berm lifts at P - 3, P - 6, P - 9
  const deepDown = (q, d) => (d <= 8 ? 68 : [61, 59, 58, 57][d - 9] ?? 57);
  const dd = PLAN.planPlateau(site(deepDown));
  ok("dial 9 downhill: a drop of 9 behind the pad is taken", dd.ok, dd.why);
  const dd6 = PLAN.planPlateau(site(deepDown, { dials: six }));
  ok("dial 9 downhill: refused at the old dial 6 (drop)", !dd6.ok && dd6.why === "drop", dd6.why);
  const berms = dd.ok ? dd.ops.filter((o) => o.kind === "berm" && o.q === 4) : [];
  ok("dial 9 downhill: three berm lifts behind the rear ring, tops P - 3, P - 6, P - 9 (rows d 9, 10, 11), none on row 12", JSON.stringify(berms.map((o) => [o.d, o.y])) === JSON.stringify([[9, 67], [10, 64], [11, 61]]), berms.map((o) => [o.d, o.y]));
  const walls = dd.ok ? dd.ops.filter((o) => o.kind === "pad" && o.wall !== null) : [];
  ok("dial 9 downhill: every retaining wall on the ring is at most one lift (P - wall <= 3)", walls.length > 0 && walls.every((o) => o.y - o.wall <= D.lift), walls.filter((o) => o.y - o.wall > D.lift).slice(0, 4));
  ok("dial 9 downhill: every berm's stone face below its top is at most one lift where the next row is not a berm", dd.ok && dd.ops.filter((o) => o.kind === "berm").every((o) => {
    const nxt = dd.ops.find((p) => p.kind === "berm" && ((o.d > 8 && p.q === o.q && p.d === o.d + 1) || (o.q > 9 && p.d === o.d && p.q === o.q + 1) || (o.q < -1 && p.d === o.d && p.q === o.q - 1)));
    if (nxt) return o.y - nxt.y === D.lift;                                  // the next lift down, exactly one lift lower
    const out = o.d > 8 ? deepDown(o.q, o.d + 1) : deepDown(o.q > 9 ? o.q + 1 : o.q - 1, o.d);   // the ground beyond the berm
    return o.y - out <= D.lift + 1;                                          // a 3-course face + its top
  }));
  const deeper = PLAN.planPlateau(site((q, d) => (d <= 8 ? 68 : [60, 59, 58, 57][d - 9] ?? 57)));
  ok("dial 9 downhill: a drop of 10 just outside the ring is still refused (drop)", !deeper.ok && deeper.why === "drop", deeper.why);
  // PROTECTED TREES: the third lift (row 3 out) is worked now — a trunk there refuses the plateau; a trunk on row 4, where the
  // ground already meets the last lift (not worked), does not matter
  const t3 = PLAN.planPlateau(site(deepDown, { blocked: (q, d) => (d === 11 && q === 4 ? "tree" : null) }));
  ok("dial 9: a protected tree on the third berm lift: refused (tree)", !t3.ok && t3.why === "tree", t3.why);
  const t4 = PLAN.planPlateau(site(deepDown, { blocked: (q, d) => (d === 12 && q === 4 ? "tree" : null) }));
  ok("dial 9: a tree beyond the last lift (ground meets it, never worked): no matter", t4.ok, t4.why);
  const tf = PLAN.planPlateau(site(g9, { blocked: (q, d) => (d === 11 && q === 2 ? "tree" : null) }));
  ok("dial 9: a protected tree in the deeper cut face (row 3): refused (tree)", !tf.ok && tf.why === "tree", tf.why);
  // HEADROOM over the house: the box is never worked; the plot stage (s0) clears it with air from the floor to its top row
  // (size y - 1 - datum_y; read from the 43 s0 templates of BP-02 1.3.230: cottage_s / butcher / farms +8, quarry / well
  // +6). A box cell cut deeper than that would leave the hill on the roof -> the box's cut is capped there (g.boxCutMax).
  const cs = CIV_BUILDINGS["pw:mvv_cottage_s_a_r1"], cm = CIV_BUILDINGS["pw:mvv_cottage_m_a_r1"], qu = CIV_BUILDINGS["pw:mvv_quarry_a_r1"];
  ok("PLAN.boxClearOf: the rows the plot stage clears above the floor — cottage_s 8, cottage_m 10, quarry 6", typeof PLAN.boxClearOf === "function" && PLAN.boxClearOf(cs) === 8 && PLAN.boxClearOf(cm) === 10 && PLAN.boxClearOf(qu) === 6, typeof PLAN.boxClearOf === "function" && [PLAN.boxClearOf(cs), PLAN.boxClearOf(cm), PLAN.boxClearOf(qu)]);
  const hillInBox = (q, d) => (q === 4 && d === 6 ? 79 : 70);                // one box cell 9 above the floor, the ring flat
  const bx = PLAN.planPlateau(site(hillInBox));
  ok("box cut 9 with no cap: within the dial (the cut is measured, the box never worked)", bx.ok && bx.cut === 9, bx.why || bx.cut);
  const bxS = PLAN.planPlateau(site(hillInBox, { boxCutMax: 8 }));
  ok("box cut 9 under a house whose plot stage clears 8 rows (cottage_s): refused (cut, at the box cell)", !bxS.ok && bxS.why === "cut" && JSON.stringify(bxS.at) === "[4,6]", bxS);
  const bxM = PLAN.planPlateau(site(hillInBox, { boxCutMax: 10 }));
  ok("box cut 9 under a house clearing 10 rows (cottage_m): taken (the cap never exceeds the dial)", bxM.ok && bxM.cut === 9, bxM.why);
  const bx10 = PLAN.planPlateau(site((q, d) => (q === 4 && d === 6 ? 80 : 70), { boxCutMax: 10 }));
  ok("box cut 10 under a house clearing 10 rows: still refused by the dial 9 (cut)", !bx10.ok && bx10.why === "cut", bx10.why);
  ok("the box cap ignores the ring (a ring cell cut 9 next to a cottage_s box is the pad's own cut, worked to P)", PLAN.planPlateau(site((q, d) => (d === 8 ? 79 : 70), { boxCutMax: 8 })).ok);
}
// the DOOR LANDING (1.3.232 #6, test_doorramp): a floor raised to a ramp's high level stands on a pad at P = the floor; at
// dial 9 a pad with fill 8 under it plans, and its works never touch the landing (the corridor's sidewalk rows in front of
// the door, filled y H + 1 .. floor): the pad and the landing meet at the floor, side by side
{
  const f = K.frameOf(0, 0, [1, 0], [0, 1]);
  const Hs3 = [60, 60, 60, 60, 60, 61, 61, 62, 62, 62, 62, 62];
  const st3 = { a: 0, b: Hs3.length - 1, H: 60, Hs: Hs3, kinds: "ffffrrrrrfff" };
  const w = K.placeAlong(f, { "1": [st3], "-1": [] }, { size: [8, 20, 9] }, null, 4.5, () => true, new Set(), 1, 1, [], { riseMax: 2, doorStep: 1 });
  const P = w ? w.H : 62;
  const g = { fz: 9, depth: 8, P, Hring: (q) => (w ? w.Hring[q + 1] : undefined), hallAt: (q) => (w ? w.Hring[q + 1] : undefined), ground: () => ({ h: P - 8, wet: false }), blocked: () => null };
  const pp = PLAN.planPlateau(g);
  ok("door landing: the raised ramp-door slot (floor 62) plans a pad over ground 8 below at dial 9", w && w.doorRamp && pp.ok && pp.P === 62 && pp.fill === 8, pp.why || pp.fill);
  ok("door landing: the same pad is refused at the old dial 6 (fill)", !PLAN.planPlateau({ ...g, dials: { cutMax: 6, fillMax: 6 } }).ok);
  const L = w ? K.landingCells(f, 1, w.doorT, (t) => Hs3[t - st3.a], P, "t") : [];
  const cellsOf = (o) => {
    if (o.kind === "link") { const [x, z] = K.cellOf(f, w.at + o.q, K.W - 1 - o.k); return [[x, o.y, z]]; }
    const [x, z] = K.cellOf(f, w.at + o.q, K.W + o.d);
    const y0 = o.kind === "outlet" ? o.yBot : o.kind === "gutter" ? P - 1 : o.kind === "face" ? Math.min(o.y, o.clad ? o.clad[0] : o.y) : (o.g ?? P) + 1;
    const y1 = o.kind === "face" ? o.g + 2 : o.kind === "pad" ? Math.max(o.g, P) + 3 : o.y ?? P;
    const out = [];
    for (let y = y0; y <= y1; y++) out.push([x, y, z]);
    return out;
  };
  const hit = pp.ok ? pp.ops.flatMap(cellsOf).filter(([x, y, z]) => L.some((c) => c.x === x && c.z === z && y >= c.y0 && y <= c.y1)) : ["no plan"];
  ok("door landing: the plateau's works never touch a landing cell (the pad starts behind the corridor, w >= 13)", L.length > 0 && hit.length === 0, { L: L.length, hit: hit.slice(0, 4) });
  ok("door landing: the landing's top and the pad stand at the same floor (P)", L.length > 0 && L.every((c) => c.y1 === pp.P), L.map((c) => c.y1));
}

// ------------------------------------------------------------------------------------------------ the slot search (KIT.placeAlong)
// a steep street: one block every 4 cells — every 9-cell frontage spans a rise of 2 (the old law fits nothing here)
{
  const L = 64;
  const Hs = Array.from({ length: L }, (_, i) => 70 + Math.floor(i / 4));
  const stretch = { a: 0, b: L - 1, H: Hs[0], Hs, kinds: "f".repeat(L) };
  const def = { size: [8, 20, 9] };
  const f = K.frameOf(0, 0, [1, 0], [0, 1]);
  const pack = (opts) => {
    const slots = [], taken = new Set();
    for (let i = 0; i < 20; i++) {
      const s = K.placeAlong(f, { "1": [stretch], "-1": [] }, def, 4, 0, (big) => !slots.some((o) => !(big[1] < o.box[0] || big[0] > o.box[1] || big[3] < o.box[2] || big[2] > o.box[3])), taken, 1, 1, [], opts);
      if (!s) break;
      slots.push(s);
      if (s.shaftT !== null) taken.add(s.shaftT);
    }
    return slots;
  };
  const old = pack(undefined);
  const plat = pack({ riseMax: D.frontRise, doorStep: D.doorStep });
  ok("steep street: the old law fits no house (every frontage rises 2)", old.length === 0, old.length);
  ok("steep street: plateau slots fit (riseMax 2)", plat.length >= 4, plat.length);
  ok("plateau slots: marked, rise 2, floor = the highest sidewalk", plat.every((s) => s.plateau && s.plateau.rise === 2 && s.H === Math.max(...Hs.slice(s.at, s.at + 9))), plat.map((s) => [s.at, s.H, s.plateau]));
  ok("plateau slots: the door within one step of the pad", plat.every((s) => Number.isInteger(s.doorT) && s.doorT >= s.at && s.doorT < s.at + 9 && s.H - Hs[s.doorT] <= 1), plat.map((s) => [s.at, s.doorT, s.H, Hs[s.doorT]]));
  ok("plateau slots: the house's sewer link (hatch or branch) within one block of its floor (>= 3 shared rows)", plat.every((s) => { const t = s.shaftT !== null ? s.shaftT : s.branchT; return t === null || t === undefined || s.H - Hs[t] <= 1; }), plat.map((s) => [s.at, s.shaftT, s.branchT, s.H]));
  ok("plateau slots: they carry the street heights of the ring (t = at - 1 .. at + fz)", plat.every((s) => Array.isArray(s.Hring) && s.Hring.length === 11 && s.Hring[1] === Hs[s.at]), plat.map((s) => s.Hring));
  // a gentle street: the plateau option changes nothing where the old law fits
  const gentle = Array.from({ length: L }, (_, i) => 70 + Math.floor(i / 12));
  const st2 = { a: 0, b: L - 1, H: 70, Hs: gentle, kinds: "f".repeat(L) };
  const p1 = K.placeAlong(f, { "1": [st2], "-1": [] }, def, 4, 30, () => true, new Set(), 1, 1, []);
  const p2 = K.placeAlong(f, { "1": [st2], "-1": [] }, def, 4, 30, () => true, new Set(), 1, 1, [], { riseMax: 2, doorStep: 1 });
  ok("gentle street: the same first slot with or without the plateau option, not marked", p1 && p2 && p1.at === p2.at && p1.H === p2.H && !p2.plateau, [p1 && p1.at, p2 && p2.at, p2 && p2.plateau]);
}

// the PARK (12 deep, 15 along the street): no 15-cell frontage rises <= 1 on this street, a plateau one does
{
  const L = 80;
  const Hs = Array.from({ length: L }, (_, i) => 70 + Math.floor(i / 6));
  const st = { a: 0, b: L - 1, H: 70, Hs, kinds: "f".repeat(L) };
  const PARK = { size: [12, 1, 15], dir: [] };
  const f = K.frameOf(0, 0, [1, 0], [0, 1]);
  const none = K.placeAlong(f, { "1": [st], "-1": [] }, PARK, null, 40, () => true, new Set(), 1);
  const park = K.placeAlong(f, { "1": [st], "-1": [] }, PARK, null, 40, () => true, new Set(), 1, 1, [], { riseMax: D.frontRise, doorStep: D.doorStep });
  ok("park: no flat 15-cell frontage under the old law", none === null, none);
  ok("park: a plateau frontage (rise 2, its gate within one step)", park && park.plateau && park.plateau.rise === 2 && park.H - Hs[park.doorT] <= 1, park);
  const pp = park && PLAN.planPlateau({ fz: 15, depth: 12, P: park.H, Hring: (q) => park.Hring[q + 1], hallAt: (q) => park.Hring[q + 1], ground: (q, d) => ({ h: 70 + Math.floor((q + park.at) / 6), wet: false }), blocked: () => null, boxFillMax: D.fillMax });
  ok("park: its plateau plans with the park's box filled (box fill <= the fill dial)", pp && pp.ok, pp && pp.why);
}

// ------------------------------------------------------------------------------------------------ the CLOCK's half, on stand-ins
// plateauLand / plateauJob / stageBillOf cut from pw_civ_clock.js (as test_households does) and run on a fake block world:
// a street along x (frame t = x, w = z; corridor z 0..12 at H 70, its sewer hall z 4..8 at y 59..62), the house's box at
// t 10..18, z 13..20, and a hill rising 0.6 per cell away from the street (the uphill case above).
import { readFileSync } from "node:fs";
import * as ECON from "../pw_civ_economy.js";
{
  const src = readFileSync(new URL("../pw_civ_clock.js", import.meta.url), "utf8");
  const cut = (name) => {
    let i = src.indexOf(`function ${name}(`);
    if (i < 0) i = src.indexOf(`function* ${name}(`);
    let j = src.indexOf("{", i), depth = 0;
    for (; j < src.length; j++) { if (src[j] === "{") depth++; else if (src[j] === "}" && --depth === 0) break; }
    return src.slice(i, j + 1);
  };
  const cutConst = (name) => { const i = src.indexOf(`const ${name} =`); return src.slice(i, src.indexOf(";\n", i) + 1); };
  const H = 70;
  let slope = 0.6;                                              // 1.3.232 (#7): 0.9 below for the dial-9 lot
  const ground0 = (x, z) => (z <= 12 ? H : H + Math.floor(slope * (z - 13 + 1)));
  const over = new Map();                                       // (x,y,z) -> typeId set by the job
  const kOf = (x, y, z) => `${x},${y},${z}`;
  let asleep = () => false;
  const trees = new Set();                                      // "x,z" -> an oak trunk standing on the ground there
  const idAt = (x, y, z) => {
    const k = kOf(x, y, z);
    if (over.has(k)) return over.get(k);
    if (z <= 12 && z >= 0) { if (z >= 4 && z <= 8 && y >= H - 11 && y <= H - 8) return "minecraft:air"; return y <= H ? "minecraft:stone_bricks" : "minecraft:air"; }
    const g = ground0(x, z);
    if (y === g + 1 && trees.has(`${x},${z}`)) return "minecraft:oak_log";
    return y < g ? "minecraft:dirt" : y === g ? "minecraft:grass_block" : "minecraft:air";
  };
  const blk = (x, y, z) => ({ typeId: idAt(x, y, z), location: { x, y, z }, setType(id) { over.set(kOf(x, y, z), id); this.typeId = id; } });
  const blockAt = (dim, x, y, z) => (asleep(x, z) ? null : blk(x, y, z));
  const topAt = (dim, x, z) => { if (asleep(x, z)) return undefined; for (let y = 120; y > 0; y--) if (idAt(x, y, z) !== "minecraft:air") return blk(x, y, z); return undefined; };
  const isGround = (id) => id !== "minecraft:air" && !id.endsWith("_log") && !id.includes("leaves");
  const groundAt = (dim, x, z, t0) => { const t = t0 || topAt(dim, x, z); if (!t) return undefined; for (let y = t.location.y; y > 0; y--) if (isGround(idAt(x, y, z))) return y; return undefined; };
  const S = { simDays: 12, buildings: [], settlements: [] };
  const street = { kind: "kit", id: 3, f: K.frameOf(0, 0, [1, 0], [0, 1]), tmin: 0, H: Array(60).fill(H), segs: [{ kind: "flat", a: 0, len: 60, H }] };
  const st = { id: 1, streets: [street], log: [] };
  S.settlements.push(st);
  const house = { id: 42, x: 10, z: 13, land: null };
  S.buildings.push(house);
  const box = [10, 18, 13, 20];
  const fc = { tunnels: new Set(), roadCells: new Set(), legacy: new Map(), bodies: [new Map(Array.from({ length: 60 * 13 }, (_, i) => [`${i % 60},${Math.floor(i / 60)}`, H]))], boxes: [box] };
  const base = { PLAN, KIT: K, ECON, kitHAt: (sr, t) => sr.H[t - sr.tmin], boxesNear: (f2) => f2.boxes, inReserve: () => false, load: () => S, freeSets: () => fc,
                 topAt, groundAt, blockAt, isGround, isVeg: (id) => id.includes("leaves") || id.includes("short_grass"), TREE_LOG: (id) => id.endsWith("_log"),
                 isWater: (id) => id === "minecraft:water" || id === "minecraft:flowing_water", localGround: () => ({ fill: "minecraft:dirt", ring: "minecraft:cobblestone", top: "minecraft:grass_block" }),
                 clearTreesOver: () => 0, BRANCH_CUT: ["minecraft:stone_bricks", "minecraft:dirt", "minecraft:cobblestone", "minecraft:stone"], ENGINE: { throws: 0 }, console };
  const names = ["streetRing", "plateauBlocked", "plateauFrame", "plateauRecord", "plateauLand", "plateauJob", "stageBillOf"];
  const consts = ["PLATEAU_WAIT", "PLATEAU_OPS", "PLATEAU_READS", "PL_STONE", "PL_WORKED"].map(cutConst).join("\n");
  const mk = (env) => new Function(...Object.keys(env), `${consts}\n${names.map(cut).join("\n")}\nreturn { ${names.join(", ")} };`)(...Object.values(env));
  const C = mk({ ...base, BUILDINGS: { fam: { bom: [{}, { timber: 40 }, { stone: 80 }] } } });
  ok("clock: the plateau functions are cut from pw_civ_clock.js", names.every((nm) => typeof C[nm] === "function"), names.filter((nm) => typeof C[nm] !== "function"));

  // plateauLand (plan time, on the site field): the compact record, no cell lists
  const lsite = { at: (x, z) => ground0(x, z), isWater: () => false };
  const slot = { box, at: 10, len: 9, side: 1, H, _street: street };
  const land = C.plateauLand(S, lsite, street.f, { ...slot, box: [10, 18, 13, 20] }, { ...fc, boxes: [] });
  ok("clock plateauLand: the uphill lot -> a plateau record (P, cut, fill, stone, labour, drain)", land.kind === "plateau" && land.P === H && land.cut === 5 && land.stone > 0 && land.drain === "sewer", land);
  ok("clock plateauLand: the saved record is small (no ops, < 200 chars)", !land.ops && JSON.stringify(land).length < 200, JSON.stringify(land).length);
  house.land = land;
  const bill1 = C.stageBillOf({ family: "fam", land }, 1), bill2 = C.stageBillOf({ family: "fam", land }, 2), bare = C.stageBillOf({ family: "fam", land: null }, 1);
  ok("clock stageBillOf: the frame's bill carries the plateau (stone, iron, labour); the walls' bill does not", bill1.mats.stone === land.stone && bill1.mats.iron === 1 && bill1.wages === bill1.builderDays * ECON.WAGE.builder + land.wages && bill2.mats.stone === 80 && !bare.mats.stone, [bill1, bill2, bare]);

  // plateauJob (build time, live ground through the guarded reads)
  const run = (ctxExtra = {}) => {
    let fell = 0;
    const ctx = { key: "b:42", f: street.f, side: 1, at: 10, fz: 9, depth: 8, P: H, sid: 3, stId: 1, self: box, label: "#42 cottage", rec: () => house, fallback: () => { fell++; }, ...ctxExtra };
    let ticks = 0;
    for (const _ of C.plateauJob({}, ctx)) { ticks++; if (ticks > 100000) break; }
    return { fell, ticks };
  };
  const r1 = run();
  const set = [...over.entries()].map(([k, id]) => { const [x, y, z] = k.split(",").map(Number); return { x, y, z, id }; });
  ok("clock plateauJob: done (no fallback), the result on the house", r1.fell === 0 && house.plateauDone && house.plateauDone.ok, [r1, house.plateauDone]);
  ok("clock plateauJob: spread over ticks (it yields)", r1.ticks >= 3, r1.ticks);
  ok("clock plateauJob: never a block inside the house's box", !set.some((c) => c.x >= 10 && c.x <= 18 && c.z >= 13 && c.z <= 20), set.filter((c) => c.x >= 10 && c.x <= 18 && c.z >= 13 && c.z <= 20).slice(0, 4));
  ok("clock plateauJob: the rear ring is levelled at P with a gravel gutter on a cobblestone bed", [9, 10, 14, 18, 19].every((x) => idAt(x, H, 21) === "minecraft:gravel" && idAt(x, H - 1, 21) === "minecraft:cobblestone" && idAt(x, H + 1, 21) === "minecraft:air"), [9, 14, 19].map((x) => [idAt(x, H - 1, 21), idAt(x, H, 21), idAt(x, H + 1, 21)]));
  ok("clock plateauJob: the cut face behind is clad in stone bricks, its lifts at P + 3 and the ground (P + 6)", idAt(14, H + 1, 22) === "minecraft:stone_bricks" && idAt(14, H + 3, 22) === "minecraft:stone_bricks" && idAt(14, H + 4, 22) === "minecraft:air" && idAt(14, H + 6, 23) === "minecraft:stone_bricks", [22, 23].map((z) => [H + 1, H + 3, H + 4, H + 6].map((y) => idAt(14, y, z))));
  const out = house.plateauDone;
  const dq = PLAN.planPlateau({ fz: 9, depth: 8, P: H, Hring: () => H, hallAt: () => H, ground: (q, d) => ({ h: ground0(10 + q, 13 + d), wet: false }), blocked: () => null }).drain.q;
  const ox = 10 + dq;
  ok("clock plateauJob: the grated drop beside the street falls to the hall's top rows", idAt(ox, H, 13) === "minecraft:iron_bars" && [H - 1, H - 5, H - 9].every((y) => idAt(ox, y, 13) === "minecraft:air") && idAt(ox, H - 10, 13) === "minecraft:dirt", [H, H - 1, H - 9, H - 10].map((y) => idAt(ox, y, 13)));
  ok("clock plateauJob: the link through the corridor's side wall (z 12..9, 2 rows) meets the hall (z 8)", [12, 11, 10, 9].every((z) => idAt(ox, H - 9, z) === "minecraft:air" && idAt(ox, H - 8, z) === "minecraft:air") && idAt(ox, H - 8, 8) === "minecraft:air" && out.link === 8, [12, 9].map((z) => idAt(ox, H - 8, z)));
  ok("clock plateauJob: the chronicle tells it", st.log.some((l) => /plateau of #42 cottage is cut at y 70/.test(l)), st.log);

  // a protected tree in the face: the live plan refuses -> the old ring terrace (fallback), nothing built
  over.clear(); delete house.plateauDone; trees.add("14,22");
  const r2 = run({ key: "b:43" });
  ok("clock plateauJob: a trunk in the cut face -> refused (tree), the fallback runs, no block set", r2.fell === 1 && house.plateauDone && house.plateauDone.why === "tree" && over.size === 0, [r2, house.plateauDone, over.size]);
  trees.clear();
  // a chunk that never loads: waits (PLATEAU_WAIT tries), then the fallback
  over.clear(); delete house.plateauDone; asleep = (x, z) => x === 21 && z === 15;              // q 11, d 2: on a side ray
  const r3 = run({ key: "b:44" });
  ok("clock plateauJob: a sleeping chunk -> it waits (many ticks), then the fallback; nothing set", r3.fell === 1 && r3.ticks > 1000 && over.size === 0, [r3, over.size]);
  asleep = () => false;

  // 1.3.232 (#7) the dial 9 on the clock's half
  const Rm = src.match(/const R = PLAN\.PLATEAU\.faceLifts \+ (\d+);/);
  const Rread = Rm ? D.faceLifts + Number(Rm[1]) : -1;
  ok("clock plateauJob: its read radius covers the deepest berm ray (floor(fillMax / lift) + 1 rows) and face ray (faceLifts + 1)", Rread >= Math.floor(D.fillMax / D.lift) + 1 && Rread >= D.faceLifts + 1, { Rread, berm: Math.floor(D.fillMax / D.lift) + 1 });
  // the box cap: the uphill 0.6 lot has a box cut of 4 (z 20: 70 + floor(0.6 * 8))
  const capLow = C.plateauLand(S, lsite, street.f, { ...slot, box: [10, 18, 13, 20] }, { ...fc, boxes: [] }, false, 3);
  ok("clock plateauLand: a box cut (4) beyond the rows the house's plot stage clears (3) -> reject (cut)", capLow.kind === "reject" && capLow.why === "cut", capLow);
  const capOk = C.plateauLand(S, lsite, street.f, { ...slot, box: [10, 18, 13, 20] }, { ...fc, boxes: [] }, false, 8);
  ok("clock plateauLand: the same lot under a house clearing 8 rows -> plateau", capOk.kind === "plateau" && capOk.cut === 5, capOk);
  const calls = src.match(/kitFree\(s, [^\n]*?\);/g) || [];
  ok("clock kitFree: hands the building's plot-stage rows to the plateau (PLAN.boxClearOf(def)); every caller with a site passes its def",
     /function kitFree\(s, st = null, lsite = null, allowStilts = false, whyOut = null, allowPlateau = false, def = null\)/.test(src)
     && /const boxCut = def \? PLAN\.boxClearOf\(def\) : undefined;/.test(src)
     && src.includes("const pl = plateauLand(s, lsite, f, slot, fc, false, boxCut);")
     && /function plateauLand\(s, lsite, f, slot, fc, park = false, boxCut = undefined\)/.test(src) && src.includes("boxCutMax: boxCut,")
     && calls.length === 4 && calls.every((c) => /, def\);$/.test(c)), calls);
  // HEADROOM on the deeper lot: slope 0.9 -> the rear ring at 78 (pad cut 8), faces at P + 3 / P + 6 / P + 9
  slope = 0.9; over.clear(); delete house.plateauDone;
  const r4 = run({ key: "b:45" });
  ok("clock plateauJob dial 9: the deeper lot (pad cut 8) is cut, no fallback", r4.fell === 0 && house.plateauDone && house.plateauDone.ok, [r4, house.plateauDone]);
  const ringXZ = [];
  for (let x = 9; x <= 19; x++) for (let z = 13; z <= 21; z++) if (!(x >= 10 && x <= 18 && z <= 20)) ringXZ.push([x, z]);
  const lowRoof = ringXZ.filter(([x, z]) => ![H + 1, H + 2, H + 3].every((y) => idAt(x, y, z) === "minecraft:air") || idAt(x, H, z) === "minecraft:air");
  ok("clock plateauJob dial 9: headroom — every ring cell stands solid at P with open air P + 1 .. P + 3 above", ringXZ.length === 27 && lowRoof.length === 0, lowRoof.slice(0, 4).map(([x, z]) => [x, z, [H, H + 1, H + 2, H + 3].map((y) => idAt(x, y, z))]));
  ok("clock plateauJob dial 9: the rear face climbs in clad lifts of 3 (P+1..P+3, P+4..P+6, P+7..P+9), air above each",
     [[22, H + 1, H + 3], [23, H + 4, H + 6], [24, H + 7, H + 9]].every(([z, y0, y1]) => idAt(14, y0, z) === "minecraft:stone_bricks" && idAt(14, y1, z) === "minecraft:stone_bricks" && idAt(14, y1 + 1, z) === "minecraft:air"),
     [22, 23, 24].map((z) => [H + 1, H + 3, H + 4, H + 6, H + 7, H + 9, H + 10].map((y) => idAt(14, y, z).replace("minecraft:", ""))));
  const inBoxSet = [...over.keys()].map((k) => k.split(",").map(Number)).filter(([x, , z]) => x >= 10 && x <= 18 && z >= 13 && z <= 20);
  ok("clock plateauJob dial 9: never a block inside the house's box", inBoxSet.length === 0, inBoxSet.slice(0, 4));
  over.clear(); delete house.plateauDone; trees.add("14,24");
  const r5 = run({ key: "b:46" });
  ok("clock plateauJob dial 9: a trunk on the third lift of the deeper face (row 3) -> refused (tree), the fallback, nothing set", r5.fell === 1 && house.plateauDone && house.plateauDone.why === "tree" && over.size === 0, [r5, house.plateauDone, over.size]);
  trees.clear(); over.clear(); delete house.plateauDone; slope = 0.6;
}

console.log(`test_plateau: ${n - bad}/${n} passed`);
if (bad) process.exitCode = 1;
