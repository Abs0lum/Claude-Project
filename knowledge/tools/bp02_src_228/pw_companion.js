// SEMANTICS v4 (#174, 2026-10-02): corner/hip/ring maps re-derived under the MEASURED transformation law (D-C487)
import { world, system, ItemStack } from "@minecraft/server";

// ============================================================================
// PW COMPANION SYSTEM v3 (BP-02 B2 wave) — @minecraft/server 2.0.0 — instrumented diagnostic build
// Coverage: 63 LOWER placement -> auto-places 63 UPPER above (same facing).
//           Breaking either half removes + drops the partner.
// v3 (B2 wave): 45 corner self-fold -> roof_hip · ridge summit-snap -> ridge_end ·
// 4-diagonal-hips apex snap -> pyramidion. 63 coverage unchanged.
// Every gate reports to chat with the [PW-C2] prefix. Errors print their text.
// ============================================================================

const DIAG = true; // diagnostic chat output (flip false after witness pass)
const say = (msg) => { if (DIAG) try { world.sendMessage(`§6[PW-C2]§r ${msg}`); } catch {} };

const AM_MATS = ["oak", "spruce"];
const LOWER = new Set(AM_MATS.flatMap((m) => [`pw:roof63_lower_${m}`, `pw:roof_gusset_lower_${m}`]));
const UPPER = new Set(AM_MATS.flatMap((m) => [`pw:roof63_upper_${m}`, `pw:roof_gusset_upper_${m}`]));
const R45   = new Set(AM_MATS.map((m) => `pw:roof45_${m}`));
const RIDGE = new Set(AM_MATS.map((m) => `pw:roof45_ridge_${m}`));
const HIP   = new Set(AM_MATS.map((m) => `pw:roof_hip_${m}`));
const NO_RULE = new Set(); // every roof piece now carries a rule (v3)
const matOf = (id) => AM_MATS.find((m) => id.endsWith(`_${m}`));
const PERP = { north: ["east","west"], south: ["east","west"], east: ["north","south"], west: ["north","south"] };
// HIP_FACE re-derived under the FRONT-STATE law (Fix-Wave 1 / D-1):
// two features facing f⊥nf share quadrant Q(f,nf); the corner piece's high/open
// feature belongs in the OPPOSITE quadrant; quadrant→front by the locked rotation
// (front n→NW, w→SW, s→SE, e→NE). One witness verdict flips all four if the
// opposite-quadrant premise is inverted — same one-shot property as before.
const HIP_FACE = { "north|west":"north", "west|north":"north", "north|east":"east", "east|north":"east",
                   "south|east":"south", "east|south":"south", "south|west":"west", "west|south":"west" };
// #174 (D-C489): hip corner = the corner it sits at, n->NW w->SW s->SE e->NE, under the MEASURED transformation law
// (D-C487). Room-wall corners keep their own (old) map until the walls get their own audit.
// #175 (D-C490): room_wall_corner at state s occupies the outer edges {s, s+90 cw}: n = N+E, w = W+N, s = S+W, e = E+S.
const WALL_CORNER_FACE = { "north|east":"north", "east|north":"north", "north|west":"west", "west|north":"west",
                   "south|west":"south", "west|south":"south", "south|east":"east", "east|south":"east" };
const DV = { north:[0,-1], south:[0,1], east:[1,0], west:[-1,0] };
const N4 = [[1,0],[-1,0],[0,1],[0,-1]]; const D4 = [[1,1],[1,-1],[-1,1],[-1,-1]];
const RW = "pw:room_wall"; const RWC = "pw:room_wall_corner";
const RING = new Set(["pw:crown_ring_oak","pw:crown_ring_spruce","pw:crown_ring_stone"]);
const PRISM = "pw:wall_prism";
const OPP2 = { north:"south", south:"north", east:"west", west:"east" };
// LINER_OFF re-derived (Fix-Wave 1): state = the facade's OUTWARD direction, so the
// interior twin sits on the BACK side. (The old map was calibrated to the dead semantics.)
const LINER_OFF = { north:[0,1], south:[0,-1], east:[-1,0], west:[1,0] };
const FULL_OF = (mat) => mat === "glass" ? "minecraft:glass" : `minecraft:${mat}`;
const BACK = { north: [0,1], south: [0,-1], east: [-1,0], west: [1,0] }; // cell behind the panel face
const matStateOf = (b) => { try { return b.permutation.getState("pw:material") || "oak_planks"; } catch { return "oak_planks"; } };
const faceOf = (b) => { try { return b.permutation.getState("minecraft:cardinal_direction") || null; } catch { return null; } };
const halfOf = (b) => { try { return b.permutation.getState("minecraft:vertical_half") || "bottom"; } catch { return "bottom"; } };
// 1.3.227 (memprobe 0.0.1, 10-06): Block.below()/above()/offset() leak ~650 B of SERVER memory per call, never freed;
// dimension.getBlock at the computed cell does not
const rel = (b, dx, dy, dz) => { const l = b.location; return b.dimension.getBlock({ x: l.x + dx, y: l.y + dy, z: l.z + dz }); };
const nb = (b, dx, dz) => { try { return rel(b, dx, 0, dz); } catch { return null; } };
const setBlockWithStates = (cell, id, facing, half) => {
  cell.setType(id);
  try { cell.setPermutation(cell.permutation.withState("minecraft:cardinal_direction", facing)); } catch {}
  try { cell.setPermutation(cell.permutation.withState("minecraft:vertical_half", half)); } catch {}
};
// v5 RULE F — hip auto-climb: a hip placed above-and-diagonal of a hip continues its fold direction.
function tryHipClimb(b) {
  for (const [dx,dz] of D4) {
    try {
      const below = rel(b, dx, -1, dz);
      if (below && HIP.has(below.typeId)) {
        const f = faceOf(below);
        if (f) { b.setPermutation(b.permutation.withState("minecraft:cardinal_direction", f));
          say(`RULE F — auto-climb: hip continued the fold facing ${f} — §aCLIMBED§r`); return true; }
      }
    } catch {}
  }
  return false;
}
// v5 RULE G — crown ring: straight/corner reflow + closure detection (the keystone event).
function ringNeighbors(b) {
  const out = [];
  for (const [dx,dz] of N4) { const n = nb(b,dx,dz); if (n && RING.has(n.typeId)) out.push([dx,dz,n]); }
  return out;
}
function ringReflow(b) {
  const cells = [b, ...ringNeighbors(b).map((t) => t[2])];
  for (const c of cells) {
    if (!RING.has(c.typeId)) continue;
    const ns = ringNeighbors(c);
    const ax = ns.filter((t) => t[0] !== 0).length, az = ns.filter((t) => t[1] !== 0).length;
    const form = (ax >= 1 && az >= 1) ? "corner" : "straight";
    try { c.setPermutation(c.permutation.withState("pw:ring_form", form)); } catch {}
    if (form === "corner") {                         // #174: the corner's outer lip = the two sides WITHOUT neighbours
      const ex = ns.some((t) => t[0] === 1), sz = ns.some((t) => t[1] === 1);
      const cf = ex && sz ? "north" : !ex && sz ? "east" : !ex && !sz ? "south" : "west";
      try { c.setPermutation(c.permutation.withState("minecraft:cardinal_direction", cf)); } catch {}
    }
  }
}
function ringClosureCheck(b, id) {
  try {
    const seen = new Set(); const key = (c) => `${c.location.x},${c.location.y},${c.location.z}`;
    let frontier = [b]; seen.add(key(b)); let degTwo = true;
    while (frontier.length && seen.size <= 256) {
      const next = [];
      for (const c of frontier) {
        const ns = ringNeighbors(c);
        if (ns.length !== 2) degTwo = false;
        for (const [,,n] of ns) { const k = key(n); if (!seen.has(k)) { seen.add(k); next.push(n); } }
      }
      frontier = next;
    }
    if (degTwo && seen.size >= 8) {
      try {                                          // #174: closed ring -> every straight faces outward
        const cells = [...seen].map((k) => k.split(",").map(Number));
        const cx = cells.reduce((a, c) => a + c[0], 0) / cells.length, cz = cells.reduce((a, c) => a + c[2], 0) / cells.length;
        for (const [x, y, z] of cells) {
          const c = b.dimension.getBlock({ x, y, z }); if (!c || !RING.has(c.typeId)) continue;
          const ns = ringNeighbors(c);
          if (ns.length === 2 && ns[0][0] === -ns[1][0] && ns[0][1] === -ns[1][1]) {
            const alongX = ns[0][0] !== 0;
            const of = alongX ? (z < cz ? "north" : "south") : (x < cx ? "west" : "east");
            c.setPermutation(c.permutation.withState("minecraft:cardinal_direction", of));
          }
        }
      } catch (e) { say(`RULE G orient err: ${e}`); }
      say(`RULE G — §6RING CLOSURE§r: ${seen.size} segments, every joint true — §athe keystone event. The oculus is whole.§r`);
      try { b.dimension.playSound("random.levelup", b.location); } catch {}
    }
  } catch (e) { say(`RULE G walk err: ${e}`); }
}
// v5 RULE H — liner pairing (PW-C2 port): exterior prism auto-places its 180° interior twin, same material.
function tryLinerPair(b) {
  const f = faceOf(b); if (!f) return false;
  const [dx,dz] = LINER_OFF[f]; const t = nb(b,dx,dz);
  if (!t) return false;
  if (t.typeId === PRISM) { say(`liner: partner pre-placed — §emanual override respected§r`); return false; }
  if (!t.isAir) { say(`liner: interior cell occupied — prism stands §esolo§r (coverage-gap style)`); return false; }
  try {
    const mat = matStateOf(b);
    t.setType(PRISM);
    t.setPermutation(t.permutation.withState("minecraft:cardinal_direction", OPP2[f]));
    try { t.setPermutation(t.permutation.withState("pw:material", mat)); } catch {}
    say(`RULE H — liner pairing: interior twin placed at 180°, material ${mat} — §aLINED§r (wall reads 11.3px solid)`);
    return true;
  } catch (e) { say(`RULE H FAIL: ${e}`); return false; }
}
// v4 RULE D — back-to-back merge: two half walls hugging the same boundary fuse into one full block.
function tryWallMerge(b) {
  const f = faceOf(b); if (!f) return false;
  // #175: the half panel hugs the cell's edge on its state side, so the half hugging the same boundary from the other
  // side is the FRONT neighbour facing back at it (the old code looked behind: a full cell of air between the panels).
  const [dx,dz] = DV[f]; const n = nb(b,dx,dz);
  if (!n || n.typeId !== RW) return false;
  const nf = faceOf(n);
  const opp = { north:"south", south:"north", east:"west", west:"east" };
  if (nf !== opp[f]) return false;                       // must hug the SAME shared face
  const mat = matStateOf(n);
  try {
    b.setType(FULL_OF(mat));
    n.setType("minecraft:air");
    say(`RULE D — back-to-back merge: two half walls fused into ${FULL_OF(mat)} — §aMERGED§r (2 halves = 1 full)`);
    return true;
  } catch (e) { say(`RULE D merge FAIL: ${e}`); return false; }
}
// v4 RULE E — L-corner resolve: a half wall placed to meet a perpendicular half wall at a shared corner becomes the corner piece.
function makeWallCorner(cell, f, nf) {
  const cornerFacing = WALL_CORNER_FACE[`${f}|${nf}`]; if (!cornerFacing) return false;
  try {
    const mat = matStateOf(cell);
    cell.setType(RWC);
    cell.setPermutation(cell.permutation.withState("minecraft:cardinal_direction", cornerFacing));
    try { cell.setPermutation(cell.permutation.withState("pw:material", mat)); } catch {}
    say(`RULE E — L-corner resolve: half wall met a perpendicular run; became room_wall_corner facing ${cornerFacing} — §aCORNERED§r`);
    return true;
  } catch (e) { say(`RULE E FAIL: ${e}`); return false; }
}
function tryWallCorner(b) {
  const f = faceOf(b); if (!f) return false;
  // #175: (1) the placed wall is the corner cell: a perpendicular half wall sits BEHIND it (its run leaves from the back)
  const back = nb(b, -DV[f][0], -DV[f][1]);
  if (back && back.typeId === RW) {
    const nf = faceOf(back);
    if (nf && PERP[f].includes(nf) && makeWallCorner(b, f, nf)) return true;
  }
  // (2) the placed wall is the perpendicular run: the corner cell is the neighbour along my panel whose back faces me
  for (const [dx,dz] of N4) {
    if (dx === DV[f][0] && dz === DV[f][1]) continue;
    if (dx === -DV[f][0] && dz === -DV[f][1]) continue;
    const n = nb(b,dx,dz); if (!n || n.typeId !== RW) continue;
    const nf = faceOf(n); if (!nf || !PERP[f].includes(nf)) continue;
    if (DV[nf][0] !== -dx || DV[nf][1] !== -dz) continue;        // n's front points away from me: I am behind n
    if (makeWallCorner(n, nf, f)) return true;
  }
  return false;
}
// v3 RULE A — corner self-fold: a 45 placed where two perpendicular 45 runs meet becomes a hip.
function tryCornerFold(b, id) {
  const m = matOf(id); const f = faceOf(b); if (!m || !f) return false;
  if (halfOf(b) !== "bottom") return false; // v1: bottom-half folds only (D-B2-3)
  const along = (f === "north" || f === "south") ? [[1,0],[-1,0]] : [[0,1],[0,-1]];
  const across = (f === "north" || f === "south") ? [[0,1],[0,-1]] : [[1,0],[-1,0]];
  for (const pf of PERP[f]) {
    // OUTER corner only (#174): the f-run continues AWAY from the pf side, the pf-run continues away from the f side.
    const run = nb(b, -DV[pf][0], -DV[pf][1]);
    const per = nb(b, -DV[f][0], -DV[f][1]);
    if (!run || !R45.has(run.typeId) || faceOf(run) !== f) continue;
    if (!per || !R45.has(per.typeId) || faceOf(per) !== pf) continue;
    const hf = HIP_FACE[`${f}|${pf}`]; if (!hf) continue;
    setBlockWithStates(b, `pw:roof_hip_${m}`, hf, "bottom");
    say(`RULE A — corner self-fold: 45 at run-meet became roof_hip_${m} facing ${hf} — §aFOLDED§r`);
    try { tryPyramidion(b); } catch {}
    return true;
  }
  return false;
}
// v3 RULE B — summit snap (ridge_end): a ridge placed against a hip along its ridge axis caps itself.
function tryRidgeEnd(b, id) {
  const m = matOf(id); const f = faceOf(b); if (!m || !f) return false;
  if (halfOf(b) !== "bottom") return false;
  const axis = (f === "north" || f === "south") ? [[1,0],[-1,0]] : [[0,1],[0,-1]];
  const DIRNAME = (dx,dz) => dx===1?"east":dx===-1?"west":dz===1?"south":"north";
  for (const [dx,dz] of axis) {
    // #174: a hipped end = along the ridge axis the next cell is open and, one level DOWN, a 45 slopes away from the
    // ridge (its downhill side = the axis direction). The ridge_end's state = the side its hip end points to.
    const n = nb(b,dx,dz);
    let below = null; try { below = rel(b, dx, -1, dz); } catch {}
    if (n && n.isAir && below && R45.has(below.typeId) && faceOf(below) === DIRNAME(dx,dz)) {
      const endFacing = DIRNAME(dx,dz);
      setBlockWithStates(b, `pw:roof_ridge_end_${m}`, endFacing, "bottom");
      say(`RULE B — summit snap: ridge terminating on a hip became roof_ridge_end_${m} facing ${endFacing} — §aCAPPED§r`);
      return true;
    }
  }
  return false;
}
// v3 RULE C — apex snap (pyramidion): the hip that completes 4 diagonal hips around an air cell caps it.
function tryPyramidion(b) {
  for (const [cx,cz] of D4) {
    const c = nb(b,cx,cz); if (!c) continue;
    let hips = 0, m = null;
    for (const [dx,dz] of D4) { const h = nb(c,dx,dz); if (h && HIP.has(h.typeId)) { hips++; m = m || matOf(h.typeId); } }
    let top = null; try { top = rel(c, 0, 1, 0); } catch {}
    if (hips === 4 && m && top && top.isAir) {
      // #174: the four hips' inner edges stand a full block above the centre cell -> the cap goes one level UP
      setBlockWithStates(top, `pw:roof_pyramidion_${m}`, "north", "bottom");
      say(`RULE C — apex snap: four hips closed the square; roof_pyramidion_${m} capped the summit — §aCROWNED§r`);
      return true;
    }
  }
  return false;
}
const upId = (id) => id.replace("_lower_", "_upper_");

// ---- BOOT BEACON: console (content log) + chat (first tick) ----------------
console.warn("[PW-C2] companion v7 LOADED (pack v1.3.227 \u00b7 expects RP-04 v1.3.156) — SEMANTICS v4 (#174/#175: hips, ridge ends, pyramidion, ring, room-wall merge + corners re-derived under the measured transformation law) — Rules A-H armed, witness round pending");
system.run(() => say("companion v2 booted — place a 63 LOWER to test auto-place"));

// ---- PLACE: gate-by-gate ----------------------------------------------------
world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try {
    const b = ev.block;
    if (!b) { say("place event fired but block handle missing"); return; }
    const id = b.typeId;
    if (id === RW) { if (!tryWallMerge(b)) tryWallCorner(b); return; }
    if (RING.has(id)) { ringReflow(b); ringClosureCheck(b, id); return; }
    if (id === PRISM) { tryLinerPair(b); return; }
    if (R45.has(id)) {
      if (tryCornerFold(b, id)) return;
      try {                                          // #174: a 45 laid under the open end of a ridge caps that ridge
        const f = faceOf(b); const d = DV[f];
        const r = rel(b, -d[0], 1, -d[1]);
        if (r && RIDGE.has(r.typeId)) tryRidgeEnd(r, r.typeId);
      } catch {}
      return;
    }
    if (RIDGE.has(id)) { tryRidgeEnd(b, id); return; }
    if (HIP.has(id)) { tryHipClimb(b); tryPyramidion(b); return; }
    if (!LOWER.has(id)) return; // non-pw or upper: silent
    say(`GATE 1 ok — place event fired for ${id}`);

    const above = rel(b, 0, 1, 0);
    if (!above) { say("GATE 2 FAIL — cell above unavailable (world edge?)"); return; }
    if (!above.isAir) {
      say(`GATE 2 stop — cell above occupied by ${above.typeId}; lower stands alone (manual law)`);
      return;
    }
    say("GATE 2 ok — cell above is air");

    let facing = "north";
    try {
      const f = b.permutation.getState("minecraft:cardinal_direction");
      if (f) { facing = f; say(`GATE 3 ok — lower facing read: ${facing}`); }
      else say("GATE 3 warn — facing state returned empty; defaulting north");
    } catch (e) { say(`GATE 3 FAIL reading facing: ${e} — defaulting north`); }

    try {
      above.setType(upId(id));
      say(`GATE 4 ok — ${upId(id)} placed above`);
    } catch (e) { say(`GATE 4 FAIL setType: ${e}`); return; }

    try {
      above.setPermutation(above.permutation.withState("minecraft:cardinal_direction", facing));
      say(`GATE 5 ok — upper facing set to ${facing} — §aCOMPANION COMPLETE§r`);
    } catch (e) {
      console.warn(`[PW-C2] facing copy unavailable (${e})`);
      say(`GATE 5 FAIL facing copy: ${e} — upper kept default facing`);
    }
  } catch (e) { say(`place handler error: ${e}`); }
});

// ---- BREAK: pair removal + drop ---------------------------------------------
world.afterEvents.playerBreakBlock.subscribe((ev) => {
  try {
    const id = ev.brokenBlockPermutation?.type?.id;
    if (!id || !(LOWER.has(id) || UPPER.has(id))) return;
    const b = ev.block, dim = b.dimension;
    const partner = LOWER.has(id) ? rel(b, 0, 1, 0) : rel(b, 0, -1, 0);
    const want = LOWER.has(id) ? UPPER : LOWER;
    if (!partner || !want.has(partner.typeId)) {
      say(`broke ${id} — no paired partner found adjacent (ok if placed pre-v0.6.1)`);
      return;
    }
    const drop = partner.typeId;
    try {
      partner.setType("minecraft:air");
      say(`broke ${id} — partner ${drop} removed`);
    } catch (e) { say(`partner removal FAIL: ${e}`); return; }
    try { dim.spawnItem(new ItemStack(drop, 1), partner.center()); }
    catch (e) { say(`partner drop spawn FAIL: ${e}`); }
  } catch (e) { say(`break handler error: ${e}`); }
});

// ---- CODEX (isolated dynamic import: server-ui trouble degrades gracefully) ----
import("./pw_codex.js").then(() => say("codex loaded")).catch((e) => say(`codex unavailable: ${e}`));
