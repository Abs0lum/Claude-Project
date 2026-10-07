// pw_civ_palace_secrets.js — 1.3.232 (#21 Part D of HOOK-PROPOSAL.diff; his OK 10-07, Q2 of the 11:12 questions): the PALACE II
// SECRET PASSAGES (D-C1006-PAL2: used by the lord, the family, the guards and the servants — never ordinary townsfolk).
// THE RULE:
//   * the secret doors STAY SHUT — nothing here opens a door, writes a block or runs a command (vanilla navigation cannot
//     path through a jib panel or an iron door; the player discovers them);
//   * only a civ whose court role is lord, noble, child, guard or servant is MOVED (a teleport) from one end of a passage
//     to the other, and only when the place he is walking to (his bed / his station: the walk's target) lies strictly
//     nearer the other end than the end he stands at (within REACH);
//   * two-way passages (mode disguised / hidden) work both ways — a "hidden" space cannot be reached from the gate by
//     design, so a civ moved in must be able to come back the way he came;
//   * ONE-WAY passages (mode oneway: an iron door whose button is on ONE side) move only from the side the door opens
//     from. tools/palacegen2.py iron_gate(inside=...) puts that side at the row's HIDDEN end in all six (U1, U4b, H6b,
//     H6c, H10, U3 — e.g. the Bridge of Sighs: "the prisoner goes over; nobody comes back this way"), hence ONEWAY_FROM;
//   * "lore" rows (a story, no way through) and rows without two ends are skipped; both ends' pieces must be finished
//     (stage 4) and the arrival cell + the one above it free (a civ is never put into a wall).
// PURE: palaceCellToWorld / pieceOf / passageEnds / secretMoves take everything as arguments — the clock's rotation
// helpers (rotXZ, palaceGridRot) are PASSED IN, so this module imports neither the clock (no circular import) nor the
// engine. runPalaceSecrets is the tiny world-call wrapper: it reads the bodies the clock hands it and calls
// entity.teleport — nothing else. Tests: tests/test_palace_secrets.mjs.
import { PALACE_SECRETS } from "./pw_civ_palace_secrets_data.js";   // generated from palace2_secrets.json (41 rows)

export const MAY_USE = new Set(["lord", "noble", "child", "guard", "servant"]);   // never: clerk, cell, ordinary civs
export const REACH = 1.5;                                 // blocks from an end's cell (feet centre) that count as "at" it
export const ONEWAY_FROM = "hidden";                      // the end a one-way passage is entered from (see the header)
export const PIECE = 64;                                  // a palace piece is 64 x 64
export const PALACE_N = 4;                                // the passages belong to PALACE II (4 x 4 pieces) only
const TWO_WAY = new Set(["disguised", "hidden"]);

/** the piece key "rc" of a model cell [x, f, z] (r = x // 64 from the gate, c = z // 64) */
export function pieceOf(cell) { return `${Math.floor(cell[0] / PIECE)}${Math.floor(cell[2] / PIECE)}`; }

/** a MODEL cell [x, f, z] -> the world cell [x, y, z] of a placed palace (pal = st.palace: x0, z0, rot, H). Each 64 x 64
 *  piece is rotated in place and the 4 x 4 grid is permuted exactly as placePalace lays it (rot.gridRot), so the cell follows
 *  its piece; f (feet over the court) -> H + f (placePalace sets a piece's y = H - datum_y, datum_y 15 = feet 0). */
export function palaceCellToWorld(pal, cell, rot) {
  const [x, f, z] = cell;
  const i = Math.floor(x / PIECE), j = Math.floor(z / PIECE);
  const [gi, gj] = rot.gridRot(i, j, pal.rot);
  const [lx, lz] = rot.rotXZ(x - i * PIECE, z - j * PIECE, PIECE, PIECE, pal.rot);
  return [pal.x0 + gi * PIECE + lx, pal.H + f, pal.z0 + gj * PIECE + lz];
}

/** the passages a civ may use now: [{ id, mode, element, pub, hid }] in world cells (lore / one-ended rows skipped; both
 *  ends' pieces finished: ready(q)) */
export function passageEnds(pal, rot, ready = () => true, secrets = PALACE_SECRETS) {
  const out = [];
  for (const s of secrets) {
    if (!s || !s.public || !s.hidden) continue;
    if (!TWO_WAY.has(s.mode) && s.mode !== "oneway") continue;          // lore (or an unknown mode): never a way through
    if (!ready(pieceOf(s.public)) || !ready(pieceOf(s.hidden))) continue;
    out.push({ id: s.id, mode: s.mode, element: s.element, pub: palaceCellToWorld(pal, s.public, rot), hid: palaceCellToWorld(pal, s.hidden, rot) });
  }
  return out;
}

const centre = (c) => [c[0] + 0.5, c[1], c[2] + 0.5];
const d2 = (a, b) => (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2;

/**
 * ONE pass (pure). civs = [{ id, role, at: [x, y, z] (feet), goal: [x, y, z] | null }]; io = { rotXZ, gridRot, ready(q),
 * clear([x, y, z]) -> the arrival cell and the one above are free }. Returns the moves [{ id, via, from: "public"|"hidden",
 * to: [x, y, z] (the arrival cell) }] — at most one a civ, the one that brings him nearest his goal; nothing is changed.
 */
export function secretMoves(pal, civs, io, secrets = PALACE_SECRETS) {
  if (!pal) return [];
  const rot = { rotXZ: io.rotXZ, gridRot: io.gridRot };
  const ends = passageEnds(pal, rot, io.ready || (() => true), secrets);
  const clear = io.clear || (() => true);
  const R2 = REACH * REACH, moves = [];
  for (const c of civs) {
    if (!c || !MAY_USE.has(c.role) || !c.goal || !c.at) continue;     // ordinary civs never use a secret passage
    let best = null;
    for (const e of ends) {
      const pc = centre(e.pub), hc = centre(e.hid);
      const sides = [];
      if (d2(c.at, pc) <= R2 && (TWO_WAY.has(e.mode) || ONEWAY_FROM === "public")) sides.push(["public", pc, e.hid, hc]);
      if (d2(c.at, hc) <= R2 && (TWO_WAY.has(e.mode) || ONEWAY_FROM === "hidden")) sides.push(["hidden", hc, e.pub, pc]);
      for (const [from, here, to, there] of sides) {
        const dThere = d2(there, c.goal);
        if (!(dThere < d2(here, c.goal))) continue;                    // only when his way needs it (strictly nearer)
        if (best && dThere >= best.d) continue;
        if (!clear(to)) continue;
        best = { d: dThere, move: { id: c.id, via: e.id, from, to: to.slice() } };
      }
    }
    if (best) moves.push(best.move);
  }
  return moves;
}

const PASSABLE = (b) => !!b && (b.isAir === true || b.typeId === "minecraft:air" || b.typeId === "minecraft:cave_air" || b.typeId === "minecraft:light_block"
  || String(b.typeId).startsWith("minecraft:light_block") || b.typeId === "minecraft:structure_void");

/**
 * THE WORLD-CALL WRAPPER (one settlement, called by the clock's heartbeat every 40 ticks). st.palace must be PALACE II
 * (n 4); deps = { rot: { rotXZ, gridRot }, bodies: [entity], personOf(entity) -> census person | null,
 * goalOf(entity) -> { x, y, z } | null (the walk's target), ready(q) -> the piece is finished, blockAt(x, y, z) -> block |
 * null (a guarded READ), cancel(entity) (ends his walk: the schedule re-sends him from the new side), log(line) }.
 * Calls entity.teleport only. Returns { moved, considered }.
 */
export function runPalaceSecrets(st, deps) {
  const pal = st && st.palace;
  if (!pal || (pal.n || 2) !== PALACE_N) return { moved: 0, considered: 0 };   // the 2 x 2 palace has no passage data
  const civs = [], byCiv = new Map();
  for (const v of deps.bodies || []) {
    try {
      if (!v || v.isValid === false) continue;
      const p = deps.personOf(v);
      if (!p || !p.court || !MAY_USE.has(p.court.r)) continue;
      const g = deps.goalOf(v);
      if (!g) continue;
      const L = v.location;
      civs.push({ id: civs.length, role: p.court.r, at: [L.x, L.y, L.z], goal: Array.isArray(g) ? g : [g.x, g.y, g.z] });
      byCiv.set(civs.length - 1, [v, p]);
    } catch { /* a body that went away */ }
  }
  if (!civs.length) return { moved: 0, considered: 0 };
  const clear = ([x, y, z]) => { try { return PASSABLE(deps.blockAt(x, y, z)) && PASSABLE(deps.blockAt(x, y + 1, z)); } catch { return false; } };
  const moves = secretMoves(pal, civs, { ...deps.rot, ready: deps.ready, clear });
  let moved = 0;
  for (const m of moves) {
    const [v, p] = byCiv.get(m.id);
    try { v.teleport({ x: m.to[0] + 0.5, y: m.to[1], z: m.to[2] + 0.5 }); } catch { continue; }   // unloaded / gone: no move
    moved++;
    try { if (deps.cancel) deps.cancel(v); } catch { /* left */ }
    if (deps.log) deps.log(`[CIV-PALACE] secret ${m.via}: ${p.name || `#${p.id}`} (${p.court.r}) ${m.from} -> ${m.from === "public" ? "hidden" : "public"} end at ${m.to.join(" ")}`);
  }
  return { moved, considered: civs.length };
}
