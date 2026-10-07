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
ok("dials: cut 6, fill 6, lifts of 3, three face lifts, frontage rise 2, door step 1", D && D.cutMax === 6 && D.fillMax === 6 && D.lift === 3 && D.faceLifts === 3 && D.frontRise === 2 && D.doorStep === 1, D);

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
  ok("uphill 0.6: the plateau takes it (pad cut <= 6)", r.ok && r.cut <= 6 && r.cut === 5, r.why || r.cut);
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
  ok("a drop beyond the fill dial (6): refused (fill or drop)", !deep.ok && (deep.why === "fill" || deep.why === "drop" || deep.why === "cut"), deep.why);
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
  const ground0 = (x, z) => (z <= 12 ? H : H + Math.floor(0.6 * (z - 13 + 1)));
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
}

console.log(`test_plateau: ${n - bad}/${n} passed`);
if (bad) process.exitCode = 1;
