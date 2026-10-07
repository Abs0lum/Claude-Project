// pw_civ_player.js — CIVITAS B11 THE PLAYER, the PURE half (no engine imports: node-tested in tests/test_player.mjs).
// Program 228 (FIT-MATRIX WP5, WP6, WP8, WP9, WP10, WP11, WP12), fitted to OUR model and his 10:15 / 12:20 rulings:
//   * WP9 STANDING SETS PRICES: st.standing = the mean playerFond of the people who know the player (fond != 0), computed on
//     the census day. friend (>= 40) buys x0.9 / sells x1.05; hero (>= 75) x0.8 / x1.1; unfriendly (<= -20, reachable only
//     through WP8 deeds, which are OFF) buys x1.2. Coins still go in and out through the same calls (the mint invariant).
//   * WP10 TALK FATIGUE + GIFTS: a talk counts toward standing only for the first TALK_FREE talks per person per day
//     (p.td = the day, p.tn = talks, p.gn = gifts; saved only while set, cleared the next day). A gift's fondness is
//     min(10, sqrt(value in pennies)) x 0.5^(gifts to this person today) + 2 when it matches the person's interest (PE8).
//   * WP8 WITNESSED DEEDS: built, switched OFF (his 10:15: "until the narrative phase") — DEEDS.enabled = false.
//   * WP5 FESTIVALS (his 10:15): a WEDDING gathering, a FEAST at each tier-up, a MONTHLY HOLIDAY (game time: the world's
//     day; a month = FEST.monthDays) — on the square at dusk; +FEST.mood mood that census day; never random.
//   * WP6 DUSK SPEECH: the leader's 3 lines (yesterday's shortage, a building finished, the tier / festival).
//   * WP11 TITLES: an honorific ladder per town (stranger, citizen, burgher, alderman, councillor). His 12:20 ruling made the
//     tax dial and the build priority FREE commands, so a title gates nothing that exists; the alderman may put a district's
//     new NAME to the town's vote (adults: yes at fond >= 40, no below 0; passes on yes > no).
//   * WP12 THE GUIDE: the walk rules (hold distance, arrival, give-up) as constants.
import { hash32 } from "./pw_civ_people.js";

// --------------------------------------------------------------------------------------------- WP9 standing -> prices
export const STANDING = { friend: 40, hero: 75, unfriendly: -20 };
export const PRICE_X = { hero: { buy: 0.8, sell: 1.1 }, friend: { buy: 0.9, sell: 1.05 }, neutral: { buy: 1, sell: 1 }, unfriendly: { buy: 1.2, sell: 1 } };
/** the mean playerFond of the living people who know the player (fond != 0); 0 when nobody does */
export function standingOf(people) {
  let n = 0, sum = 0;
  for (const p of people || []) { if (p.alive === false) continue; const f = p.playerFond || 0; if (f) { n++; sum += f; } }
  return n ? Math.round(sum / n * 10) / 10 : 0;
}
export function bandOf(standing) {
  const s = standing || 0;
  return s >= STANDING.hero ? "hero" : s >= STANDING.friend ? "friend" : s <= STANDING.unfriendly ? "unfriendly" : "neutral";
}
export const priceX = (standing, side) => PRICE_X[bandOf(standing)][side];
/** the counter's unit price (pennies) for the player: never below 1 penny */
export const buyUnit = (unit, standing) => Math.max(1, Math.round(unit * priceX(standing, "buy")));
/** what the town pays the player for goods (pennies): floored */
export const sellPay = (pay, standing) => Math.floor(pay * priceX(standing, "sell"));

// --------------------------------------------------------------------------------------------- WP10 talk + gifts
export const TALK_FREE = 3, TALK_FOND = 1;
export const GIFT = { maxFond: 10, halving: 0.5, interest: 2, maxPerDay: 6 };
function today(p, day) { if (p.td !== day) { p.td = day; p.tn = 0; p.gn = 0; } }
/** a talk: counts (true) only for the first TALK_FREE today */
export function talkCounts(p, day) { today(p, day); p.tn = (p.tn || 0) + 1; return p.tn <= TALK_FREE; }
/** the fond a gift of `value` pennies gives a person who had `nToday` gifts today */
export function giftFond(value, nToday = 0, interest = false) {
  const base = Math.min(GIFT.maxFond, Math.sqrt(Math.max(0, value || 0)));
  return Math.round((base * GIFT.halving ** Math.max(0, nToday) + (interest ? GIFT.interest : 0)) * 10) / 10;
}
/** give: updates p.gn + playerFond; returns { fond, refused } */
export function giveTo(p, day, value, interest = false) {
  today(p, day);
  if ((p.gn || 0) >= GIFT.maxPerDay) return { fond: 0, refused: true };
  const f = giftFond(value, p.gn || 0, interest);
  p.gn = (p.gn || 0) + 1;
  p.playerFond = Math.min(100, (p.playerFond || 0) + f);
  return { fond: f, refused: false };
}
/** the next day: the day counters go (nothing saved for people not talked to) */
export function pruneTalk(p, day) { if (p.td !== undefined && p.td < day) { delete p.td; delete p.tn; delete p.gn; } }
/** PE8 interest -> the goods it likes */
export const LIKES = { building: ["stone", "timber", "planks", "brick", "lime"], trade: null, food: ["bread", "meat", "fish", "wheat", "crops"],
  family: ["wool", "bread"], "the sea": ["fish"], "the woods": ["timber", "planks"], "the town": ["stone", "brick"], news: null };
export function likes(interest, good) { const l = LIKES[interest]; return l === null ? !!good : !!(l && l.includes(good)); }

// --------------------------------------------------------------------------------------------- WP8 deeds (built, OFF)
export const DEEDS = { enabled: false, reach: 12, dy: 4, fondX: 5, amendsX: 1.5,
  law: { counter: { hit: 2 }, station: { hit: 3 }, wall: { hit: 1 }, chest: { hit: 2 } } };
export const deedHit = (kind) => (DEEDS.law[kind] ? DEEDS.law[kind].hit : 0);
/** the amends for a deed: the damage (pennies) x 1.5, rounded up */
export const amendsOf = (damage) => Math.ceil(Math.max(0, damage || 0) * DEEDS.amendsX);
/** witnesses of a deed at `at` among `bodies` [{ pid, x, y, z }] (distance + height, deterministic: no raycast) */
export function witnessesOf(bodies, at) {
  return (bodies || []).filter((b) => Math.hypot(b.x - at.x, b.z - at.z) <= DEEDS.reach && Math.abs(b.y - at.y) <= DEEDS.dy).map((b) => b.pid);
}
/** apply a deed to a witness (only when DEEDS.enabled): fond falls hit x 5; a memory key */
export function witness(p, kind, day) {
  if (!DEEDS.enabled) return false;
  p.playerFond = Math.max(-100, (p.playerFond || 0) - deedHit(kind) * DEEDS.fondX);
  p.mem = p.mem || {}; p.mem.saw_deed = day + 30;
  return true;
}

// --------------------------------------------------------------------------------------------- WP5 festivals
export const FEST = { monthDays: 30, mood: 3, ringR: [4, 6], particleEvery: 40, dusk: [11000, 13000] };
/** the festival of a town on world day `wday` / census day `day`: f = { weddingDay, tierDay, seed } -> { kind, why } | null.
 *  Priority: the feast (a tier laid out today or yesterday) > a wedding (today or yesterday) > the monthly holiday (the town's
 *  own day of the month: hash of its seed) */
export function festivalOf(wday, day, f = {}) {
  if (f.tierDay !== undefined && f.tierDay !== null && day - f.tierDay >= 0 && day - f.tierDay <= 1) return { kind: "feast", why: "the town rose a tier" };
  if (f.weddingDay !== undefined && f.weddingDay !== null && day - f.weddingDay >= 0 && day - f.weddingDay <= 1) return { kind: "wedding", why: "a wedding" };
  if (holidayDay(f.seed || 0) === (((wday % FEST.monthDays) + FEST.monthDays) % FEST.monthDays)) return { kind: "holiday", why: "the month's holiday" };
  return null;
}
export const holidayDay = (seed) => hash32((seed >>> 0) || 1, 0xF357) % FEST.monthDays;
/** a body's place in the festival ring around a centre: angle = id x 47 degrees, radius by id */
export function ringSlot(cx, cz, id) {
  const a = ((id * 47) % 360) * Math.PI / 180;
  const r = FEST.ringR[0] + (hash32(id >>> 0, 0x2196) % (FEST.ringR[1] - FEST.ringR[0] + 1));
  return { x: cx + Math.cos(a) * r, z: cz + Math.sin(a) * r, look: { x: cx, z: cz } };
}
export const FEST_NAME = { feast: "the tier feast", wedding: "the wedding", holiday: "the holiday" };

// --------------------------------------------------------------------------------------------- WP6 the dusk speech
export const SPEECH = { at: [11000, 11600], reach: 32, gap: 160 };
/** three lines from yesterday: f = { town, short: [goods], built: [family], tier, festival, mood } */
export function speechLines(f = {}) {
  const lines = [];
  if (f.festival) lines.push(`Friends of ${f.town}, tonight we keep ${FEST_NAME[f.festival] || "the feast"}!`);
  else lines.push(`Good people of ${f.town}, hear the day's news.`);
  if (f.built && f.built.length) lines.push(`The new ${f.built[0].replace(/_/g, " ")} stands finished — our thanks to the builders.`);
  else if (f.short && f.short.length) lines.push(`We are short of ${f.short.slice(0, 2).join(" and ")}; bring what you can to the market.`);
  else lines.push("The stores are sound and the work goes on.");
  if (f.mood !== undefined && f.mood < 45) lines.push("Times are hard; the council hears you.");
  else lines.push(f.tier ? `Long live ${f.town}, a ${f.tier}!` : `Long live ${f.town}!`);
  return lines.slice(0, 3);
}

// --------------------------------------------------------------------------------------------- WP11 titles + votes
export const PTITLES = ["stranger", "citizen", "burgher", "alderman", "councillor"];
export const PTITLE_NAME = { stranger: "Stranger", citizen: "Citizen", burgher: "Burgher", alderman: "Alderman", councillor: "Councillor" };
/** the player's title in a town: c = { standing, trades, slips, stall, tierClass } (tierClass 0 village, 1 town, 2 city, ...;
 *  townLevel: the town's rung within its class, e.g. town II = class 1 level >= 2) */
export function ptitleOf(c = {}) {
  let t = 0;
  if ((c.standing || 0) >= 20 && (c.trades || 0) >= 10) t = 1;
  if (t >= 1 && ((c.slips || 0) >= 10 || c.stall)) t = 2;
  if (t >= 2 && (c.standing || 0) >= 50 && (c.tierClass || 0) >= 1 && ((c.tierClass || 0) >= 2 || (c.townLevel || 0) >= 2)) t = 3;
  if (t >= 3 && (c.tierClass || 0) >= 2 && (c.slips || 0) >= 30) t = 4;
  return PTITLES[t];
}
/** the town's vote on a player's proposal: adults vote yes at fond >= 40, no below 0, else abstain */
export function vote(adults, recall = false) {
  let yes = 0, no = 0, abstain = 0;
  for (const p of adults || []) { const f = p.playerFond || 0; if (f >= 40) yes++; else if (f < 0) no++; else abstain++; }
  const pass = recall ? yes * 3 >= (yes + no + abstain) * 2 : yes > no;
  return { yes, no, abstain, pass };
}
/** a district name the player may give: 3..24 letters, spaces, apostrophes, hyphens */
export function cleanName(s) {
  const t = String(s || "").replace(/§./g, "").replace(/[^A-Za-z' \-]/g, "").replace(/\s+/g, " ").trim();
  return t.length >= 3 && t.length <= 24 ? t : null;
}

// --------------------------------------------------------------------------------------------- WP12 the guide
export const GUIDE = { hold: 8, resume: 4, arrive: 4, maxTicks: 2400, every: 20 };
/** one guide step: d = the player's distance from the guide, a = the guide's distance from the door -> "arrive" | "hold" | "walk" */
export function guideStep(d, a, holding) {
  if (a <= GUIDE.arrive) return "arrive";
  if (holding) return d <= GUIDE.resume ? "walk" : "hold";
  return d > GUIDE.hold ? "hold" : "walk";
}
