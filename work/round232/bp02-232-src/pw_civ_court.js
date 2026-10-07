// pw_civ_court.js — CIVITAS 1.3.229 ROLE BEDS (his 14:07 + his answers), the PURE half (node-tested in tests/test_court.mjs).
// "the beds that are filled have to correlate to job or position within the palace and castles … these beds are reserved
// until those roles are filled." His answers: the nobles = the town's TOP FAMILIES + POLITICAL REPRESENTATION PER DISTRICT;
// the servants' quarters are staffed by the town's BEST COOKS AND TRADESMEN; "Families move in too" — only where the room
// has enough beds; elsewhere single staff live in, and married staff keep the family home (the role bed stays reserved for
// a single hire).
//   * THE BEDS: tools/palace_beds.py reads palacegen's model (every bed carries its room's role) -> PALACE_BEDS per piece:
//     lord (the state bedchamber), noble (the officials' apartments), servant (garrets, the little commons, the quarters),
//     guard (guard rooms, the porter), clerk (the clerks' lodgings), cell (the piombi: never a home).
//   * WHO: lord = the top family that fits (1.3.232: one per lord's bed — PALACE II has two); noble = one representative household per district first (the district's top
//     family that fits), then the next top families; servant = single grown people of a cook's or craft trade, the most
//     skilled first (shop keepers stay with their shops); guard = single watchmen; clerk = single surveyors / clerks.
//     A noble household is a MARRIED COUPLE with no children at home (one double bed) whose best skill is at least a
//     journeyman's; singles serve (staff); a post holder's household (the watch, the clerks) is never noble.
//   * FITS: a household moves in only when the room's beds sleep it (a double bed sleeps COURT.sleepers). His 17:52: every
//     apartment of state and the lord's chamber get a CHILDREN'S BED (role "child" in PALACE_BEDS) — then a couple with up
//     to COURT.sleepers children at home fits; without children's beds only a couple (no children at home) fits.
//   * STABLE: a member keeps the bed while eligible (no daily reshuffle); one who is no longer eligible (married, left the
//     post, the family grew) goes back to the home he came from (p.court.prev) and the bed waits for the next.
//   * RESERVED: a role bed is never anyone else's; the general housing never sees the palace (HOUSEHOLD has no palace).
import { PALACE_BEDS } from "./pw_civ_court_data.js";

export const COURT = {
  sleepers: 2,
  kidsMax: Object.values(PALACE_BEDS).some((o) => (o.child || 0) > 0) ? 2 : 0,   // his 17:52: the children's bed sleeps two
  nobleMin: 15,                       // a noble household has at least one journeyman (LEARN.journeyman) — the top families rank above
  cooks: ["bakery", "butcher", "inn", "fishery", "fisher"],
  crafts: ["smithy", "brickworks", "lumberyard", "quarry", "weaver", "tannery", "cooper", "mason", "carpenter"],
  clerks: ["surveyor", "clerk", "town_hall"],
  guards: ["watch"],
  order: ["lord", "noble", "guard", "clerk", "servant"],
};
export const ROLE_NAME = { lord: "the lord's bedchamber", noble: "an apartment of state", servant: "the servants' quarters", guard: "the guard room", clerk: "the clerks' lodgings" };

/** the beds of a palace piece by role ({} for an unknown piece); cells are never homes */
export function bedsOfPiece(q) { const b = { ...(PALACE_BEDS[q] || {}) }; delete b.cell; delete b.child; return b; }

/** the score of a household (top families): the best skill of its grown members + 40 for a shop master + 20 for a manor */
export function familyScore(hh, f) {
  let best = 0, bonus = 0;
  for (const p of hh) {
    if (f.stage(p) !== "adult" && f.stage(p) !== "elder") continue;
    const sk = p.skill ? Math.max(0, ...Object.values(p.skill)) : 0;
    if (sk > best) best = sk;
    if (p.keeper) bonus = Math.max(bonus, 40);
  }
  if (f.homeKind && f.homeKind(hh[0]) === "manor") bonus += 20;
  return best + bonus;
}
const tradeOf = (p, f) => (f.tradeOf ? f.tradeOf(p) : p.trade) || "";
/** the role a single person may hold at court (null: none) */
export function staffRole(p, f) {
  if (p.alive === false || p.spouse || p.keeper) return null;
  if (f.stage(p) !== "adult") return null;
  const job = typeof p.job === "string" ? p.job : null, tr = tradeOf(p, f);
  if (job && COURT.guards.includes(job)) return "guard";
  if ((job && COURT.clerks.includes(job)) || COURT.clerks.includes(tr)) return "clerk";
  if (p.job === null || p.job === undefined) return null;
  if (COURT.cooks.includes(tr) || COURT.crafts.includes(tr)) return "servant";
  return null;
}
const skillIn = (p, f) => (p.skill && p.skill[tradeOf(p, f)]) || 0;

/** does a household fit one apartment? at most COURT.sleepers grown, at most COURT.kidsMax children */
export function fitsApartment(hh, f) {
  const kids = hh.filter((q) => f.stage(q) === "child").length;
  return hh.length - kids <= COURT.sleepers && kids <= COURT.kidsMax;
}
/** a court GROUP (one slot): the members sharing { r, b, head } — eligible while it is still one household that fits
 *  (lord / noble: every living spouse inside, at most COURT.sleepers) or the single still holds the role (staff) */
export function groupEligible(members, f) {
  if (!members.length) return false;
  const c = members[0].court;
  if (c.r === "lord" || c.r === "noble") {
    if (!fitsApartment(members, f)) return false;
    const ids = new Set(members.map((q) => q.id));
    return members.every((q) => !q.spouse || ids.has(q.spouse) || f.dead(q.spouse));
  }
  return members.length === 1 && staffRole(members[0], f) === c.r;
}
/**
 * the court plan for a town. pieces = [{ id, q }] (finished palace pieces); people = the census list; f = { stage(p),
 * household(p) -> [persons], districtOf(p) -> key | null, homeKind(p) -> short family | null, tradeOf(p), dead(pid) }.
 * Returns { release: [pid], admit: [{ pid, b, r }], free: { role: n }, held: { role: n } } — nothing is changed here.
 */
export function courtPlan(pieces, people, f) {
  const living = people.filter((p) => p.alive !== false);
  const slots = [];                                     // { b, r, taken }
  for (const pc of [...pieces].sort((a, b) => a.id - b.id)) {
    const beds = bedsOfPiece(pc.q);
    for (const r of COURT.order) for (let i = 0; i < (beds[r] || 0); i++) slots.push({ b: pc.id, r, taken: false });
  }
  const release = [], admit = [], atCourt = new Set();
  const pieceIds = new Set(pieces.map((p) => p.id));
  // 1. the members, by group { r, b, head }: keep an eligible group (it holds one slot of its role in its piece); release the rest
  const groups = new Map();
  for (const p of living) {
    if (!p.court) continue;
    const k = `${p.court.r}|${p.court.b}|${p.court.head}`;
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(p);
  }
  for (const members of [...groups.values()].sort((a, b) => a[0].id - b[0].id)) {
    const c = members[0].court;
    const s = pieceIds.has(c.b) && groupEligible(members, f) ? slots.find((x) => !x.taken && x.b === c.b && x.r === c.r) : null;
    if (s) { s.taken = true; for (const q of members) atCourt.add(q.id); } else for (const q of members) release.push(q.id);
  }
  const free = (r) => slots.filter((x) => !x.taken && x.r === r);
  const take = (r) => { const s = free(r)[0]; if (s) s.taken = true; return s; };
  // 2. the families: candidates = households (by their head: the oldest grown member) that fit one bed and are not at court
  const seen = new Set(), fams = [];
  for (const p of living) {
    if (seen.has(p.id) || atCourt.has(p.id) || release.includes(p.id) || p.court) continue;
    const st = f.stage(p);
    if (st !== "adult" && st !== "elder") continue;
    const hh = f.household(p);
    hh.forEach((q) => seen.add(q.id));
    if (hh.some((q) => q.court || atCourt.has(q.id))) continue;
    if (hh.some((q) => q.keeper)) continue;             // a shop master's household lives with its shop
    if (!fitsApartment(hh, f)) continue;                // the apartment's beds: a couple + (with the children's bed) up to 2 children
    if (hh.filter((q) => f.stage(q) !== "child").length < 2) continue;   // FAMILIES: a married couple (singles serve as staff)
    if (hh.some((q) => staffRole(q, f) === "guard" || staffRole(q, f) === "clerk")) continue;   // a post holder's household serves
    const head = hh.filter((q) => f.stage(q) !== "child").sort((a, b) => a.born - b.born || a.id - b.id)[0];
    const score = familyScore(hh, f);
    if (score < COURT.nobleMin) continue;
    fams.push({ head, hh, score, district: f.districtOf ? f.districtOf(head) : null });
  }
  fams.sort((a, b) => b.score - a.score || a.head.id - b.head.id);
  const used = new Set();
  const admitFam = (fm, r) => { const s = take(r); if (!s) return false; used.add(fm.head.id); for (const q of fm.hh) admit.push({ pid: q.id, b: s.b, r, head: fm.head.id }); return true; };
  // 1.3.232 (#21, D-GH1007-LORDBEDS "at least 2 — it's supposed to house a court"): EVERY free lord's bed is filled, the top
  // families first (was: one lord a pass — PALACE II's second lord's bed then went to nobody: the next families had become
  // nobles the same day, and a family at court is never a candidate again)
  for (const fm of fams) { if (!free("lord").length) break; if (!used.has(fm.head.id)) admitFam(fm, "lord"); }
  // one representative household per district (districts without one already at court), by the district's key
  const repped = new Set(living.filter((p) => p.court && (p.court.r === "noble" || p.court.r === "lord") && p.court.d !== undefined && p.court.d !== null).map((p) => p.court.d));
  const districts = [...new Set(fams.map((x) => x.district).filter((d) => d !== null && d !== undefined))].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
  for (const d of districts) {
    if (!free("noble").length) break;
    if (repped.has(d)) continue;
    const fm = fams.find((x) => x.district === d && !used.has(x.head.id));
    if (fm && admitFam(fm, "noble")) { repped.add(d); admit.filter((a) => a.head === fm.head.id).forEach((a) => (a.d = d)); }
  }
  for (const fm of fams) { if (!free("noble").length) break; if (!used.has(fm.head.id)) admitFam(fm, "noble"); }
  // 3. the staff: single grown people by role, the most skilled first
  for (const r of ["guard", "clerk", "servant"]) {
    if (!free(r).length) continue;
    const cands = living.filter((p) => !p.court && !atCourt.has(p.id) && !used.has(p.id) && !admit.some((a) => a.pid === p.id) && staffRole(p, f) === r)
      .sort((a, b) => skillIn(b, f) - skillIn(a, f) || a.id - b.id);
    for (const p of cands) { const s = take(r); if (!s) break; admit.push({ pid: p.id, b: s.b, r, head: p.id }); }
  }
  const tally = (taken) => { const o = {}; for (const s of slots) if (s.taken === taken) o[s.r] = (o[s.r] || 0) + 1; return o; };
  return { release, admit, free: tally(false), held: tally(true), slots: slots.length };
}

/** apply a plan to the census: release -> back to p.court.prev (or homeless); admit -> p.court = { r, b, prev, head, beds, d } */
export function applyCourt(plan, P, byId, homeOk) {
  const out = { released: 0, admitted: 0 };
  for (const pid of plan.release) {
    const p = byId(P, pid);
    if (!p || !p.court) continue;
    const prev = p.court.prev;
    p.home = prev !== undefined && prev !== null && homeOk(prev) ? prev : null;
    delete p.court; out.released++;
  }
  for (const a of plan.admit) {
    const p = byId(P, a.pid);
    if (!p) continue;
    p.court = { r: a.r, b: a.b, prev: p.home ?? null, head: a.head, beds: 1 };
    if (a.d !== undefined) p.court.d = a.d;
    p.home = a.b; out.admitted++;
  }
  return out;
}
