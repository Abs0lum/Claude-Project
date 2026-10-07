// pw_civ_names.js — CIVITAS B9 names and titles, the PURE half (node-tested in tests/test_names.mjs).
// Program 228 (FIT-MATRIX TR10 + GB6): every kit street (a district) gets a NAME once, unique in its town, from our own word
// list (by the street's role and its index); a town gets a TITLE from its SPIRIT — the points its standing buildings give
// (nautical, mining, woodland, market, travel, pastoral, craft, crown) — the dominant spirit (a 0.4 share) and the tier's
// rung name ("Fishing Hamlet -> Harbour Town -> Port"). Nothing random: the choices are hashes of ids.
import { hash32 } from "./pw_civ_people.js";

const PRE = {
  main: ["High", "Market", "King's", "Broad", "Church", "Guild", "Bridge", "Castle"],
  side: ["Mill", "Lantern", "Baker's", "Cooper's", "Weaver's", "Chandler's", "Tanner's", "Smith's", "Well", "Orchard", "Rope", "Salt"],
  lane: ["Hill", "Lower", "Upper", "Crooked", "Steep", "Narrow", "Ivy", "Rose"],
  bench: ["Terrace", "Ridge", "Shelf", "Ledge"],
  connector: ["Cross", "Short", "Little", "Back"],
};
const SUF = {
  main: ["Street", "Row", "Way"],
  side: ["Street", "Lane", "Row", "Gate"],
  lane: ["Steps", "Lane", "Walk", "Rise"],
  bench: ["Row", "Walk", "Terrace"],
  connector: ["Lane", "Way", "Alley"],
};
/** a name for street `sid` of role `role` in a town whose names so far are `taken` (Set); unique in the town */
export function streetName(sid, role, taken, seed = 0) {
  const pre = PRE[role] || PRE.side, suf = SUF[role] || SUF.side;
  const h = hash32((sid * 2654435761 + seed) >>> 0, 0x57EE7);
  for (let k = 0; k < pre.length * suf.length; k++) {
    const i = (h + k) % (pre.length * suf.length);
    const nm = `${pre[i % pre.length]} ${suf[Math.floor(i / pre.length) % suf.length]}`;
    if (!taken.has(nm)) return nm;
  }
  return `${pre[h % pre.length]} ${suf[0]} ${sid}`;
}

// GB6: points per building family (only standing, furnished buildings count)
export const SPIRIT_PTS = { fishery: ["nautical", 5], quarry: ["mining", 5], lumberyard: ["woodland", 5], bakery: ["market", 3], butcher: ["market", 3],
  market: ["market", 3], inn: ["travel", 4], farm_wheat: ["pastoral", 4], farm_terrace: ["pastoral", 4], farm_cattle: ["pastoral", 4], smithy: ["craft", 4],
  brickworks: ["craft", 4], palace: ["crown", 8], manor: ["crown", 8] };
export const SPIRIT_STEPS = [25, 60, 140, 300, 600];
const RUNGS = {
  nautical: ["Fishing Hamlet", "Fishing Village", "Harbour Town", "Port", "Great Port"],
  mining: ["Quarry Hamlet", "Mining Village", "Stone Town", "Mining City", "City of Stone"],
  woodland: ["Woodcutters' Hamlet", "Forest Village", "Timber Town", "Forest City", "City of the Woods"],
  market: ["Crossroads", "Market Village", "Market Town", "Trading City", "City of Markets"],
  travel: ["Wayside", "Coaching Village", "Inn Town", "Waystation City", "City of Roads"],
  pastoral: ["Farmstead", "Farming Village", "Shire Town", "Granary City", "City of Fields"],
  craft: ["Workshop Hamlet", "Craft Village", "Guild Town", "City of Guilds", "City of Makers"],
  crown: ["Manor Hamlet", "Manor Village", "Seat", "Royal Seat", "Crown City"],
};
/** the town's spirit points from its standing families ({family short: count}) */
export function spiritOf(counts) {
  const pts = {};
  for (const [fam, n] of Object.entries(counts)) { const sp = SPIRIT_PTS[fam]; if (sp) pts[sp[0]] = (pts[sp[0]] || 0) + sp[1] * n; }
  return pts;
}
/** the title: { spirit, rung, title } or null (no dominant spirit / below the first step) */
export function titleOf(pts) {
  const total = Object.values(pts).reduce((a, v) => a + v, 0);
  if (!total) return null;
  const [spirit, v] = Object.entries(pts).sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1))[0];
  if (v / total < 0.4) return null;
  let rung = -1;
  for (let i = 0; i < SPIRIT_STEPS.length; i++) if (v >= SPIRIT_STEPS[i]) rung = i;
  if (rung < 0) return null;
  return { spirit, rung, title: RUNGS[spirit][rung] };
}
