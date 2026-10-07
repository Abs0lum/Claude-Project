// pw_civ_shop.js — CIVITAS SHOPKEEPERS (v1.3.219, his 17:00 "the villagers don't seem to be at their stations for me to
// purchase from them" + V1 / V2 = yes: keepers walk to their stations in work hours, you trade with them there, in coins,
// in our own window with the town's live prices).
// Mechanism found (D-C528): the shops had NO people — HOUSEHOLD gave the bakery, butcher, smithy, lumberyard and quarry
// nobody, their workers depended on the game's own job-site claiming (random, range-limited), and nobody was assigned.
// Now: every shop (and the inn, and the town hall's clerk) gets ONE named KEEPER when it is furnished (a villager tagged
// civ:keeper + civ:shop:<id>). In WORK HOURS (game time 1000..11000, morning to evening) a keeper away from the shop's
// STATION (its first station marker, else the cell inside the door) is brought back when no player is close enough to
// see it happen, and kept there (slowness while on duty); after hours the keeper is free (home, bed, the bell).
// Talking to a keeper opens the SHOP WINDOW: what this shop sells (the town's stock and live price, in gold coins) and
// what it buys (its own goods and its inputs, at 70 %); the town hall's clerk changes emeralds and coins (1 : 4).
// Prices, stock and the treasury are the settlement's economy ledger (pw_civ_economy.js); coins are the mint's
// (pw_civ_coin.js): paying returns coins to the treasury, being paid issues new serials from it.
import { world, system } from "@minecraft/server";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import * as PLAYER from "./pw_civ_player.js";                 // 1.3.228 (B11): standing, talk, gifts, titles, the guide
import * as COIN from "./pw_civ_coin.js";
import * as WALK from "./pw_civ_walk.js";          // C2.1 (D-C541): keepers walk to their stations
import * as HB from "./pw_civ_beat.js";
import * as VOICE from "./pw_civ_voice.js";      // 1.3.228 (B5): talk stops, lines, petitions          // 1.3.228 (B1 / BF1): the heartbeat (slot 9 of 100, optional) and the bodies cache

let API = null;                                  // the clock's functions (initShops)
const WORK = [1000, 11000];                      // time of day: on duty
const TRADE = { bakery: "Baker", butcher: "Butcher", smithy: "Smith", lumberyard: "Woodcutter", quarry: "Quarryman", inn: "Innkeeper",
                town_hall: "Clerk", farm_wheat: "Farmer", farm_terrace: "Farmer", farm_cattle: "Herder" };
export const KEEPS = Object.keys(TRADE);

export function initShops(api) { API = api; }
const hireTried = new Map();                     // 1.3.224: building id -> tick of the last hire attempt

const onDuty = () => { const t = world.getTimeOfDay(); return t >= WORK[0] && t < WORK[1]; };

/** the station a keeper works at: the first civ:station marker inside the building, else the cell inside the door */
function stationOf(dim, b, def) {
  const [fx, sy, fz] = API.footprint(def, b.rot);
  try {
    for (const e of dim.getEntities({ location: { x: b.x, y: b.y, z: b.z }, volume: { x: fx, y: sy, z: fz } })) {
      if (e.typeId === "pw:marker" && e.hasTag("civ:station")) return { x: Math.floor(e.location.x) + 0.5, y: Math.floor(e.location.y), z: Math.floor(e.location.z) + 0.5 };
    }
  } catch { /* unloaded */ }
  const [sx, , sz] = def.size;
  const door = def.door || [0, 0, Math.floor(sz / 2)];
  const [ox, oz] = API.rotXZ(2, door[2], sx, sz, b.rot);
  return { x: b.x + ox + 0.5, y: b.y + def.datum_y, z: b.z + oz + 0.5 };
}

/** a shop furnished: its keeper (once). Called by the clock after the furnished stage is placed. */
export function hireKeeper(dim, b, def, st) {
  const kind = API.short(b);
  if (!TRADE[kind]) return null;
  if (b.keeper) { try { if (world.getEntity(b.keeper)) return b.keeper; } catch { /* gone */ } }
  const at = stationOf(dim, b, def);
  try {
    const v = dim.spawnEntity(API.VILLAGER_ID, at);
    const name = API.nameFor(b, st);
    v.nameTag = `${name} the ${TRADE[kind]}`;
    v.addTag("civ:villager");
    v.addTag("civ:keeper");
    // D-C550: the keeper is a census person (the master of the shop): trust, skill and rank are theirs
    if (API.keeperPerson) { const pid = API.keeperPerson(b, st, name); if (pid !== null && pid !== undefined) v.addTag(`civ:person:${pid}`); }
    v.addTag(`civ:shop:${b.id}`);
    if (st) v.addTag(`civ:settlement:${st.id}`);
    try { if (API.civOn) API.civOn(v); } catch { /* left */ }   // 1004b
    b.keeper = v.id;
    b.station = at;
    if (st) st.log.push(`day ${API.load().simDays.toFixed(0)}: ${v.nameTag} keeps the ${kind} (#${b.id})`);
    return v.id;
  } catch (e) { console.warn(`[CIV-SHOP] hire at #${b.id}: ${e}`); return null; }
}

/** every 5 s: keepers on duty at their stations (moved only when no player is near), anchored while there */
HB.register("shop", { fn: () => {
  if (!API) return;
  const s = API.load();
  const duty = onDuty();
  let tod = 0; try { tod = world.getTimeOfDay(); } catch { /* left */ }
  let beatSends = 0;                                                  // 1.3.228 (B4 / PE1): at most BEAT_SENDS beat moves a beat
  const tb0 = Date.now();
  const byId = new Map(s.buildings.map((q) => [q.id, q]));          // 1.3.227: one lookup per keeper (was a list scan each)
  // review 19:1x: a keeper the clock re-hired while the old one stood in an unloaded chunk comes back later as a second
  // keeper: any loaded keeper that is not its shop's current one is sent away
  // 1.3.228 (B1 / BF1): a settlement's keepers come from the shared bodies cache (they carry civ:settlement); the whole-
  // overworld query is kept only while a shop outside any settlement (the `plot` tool) has a keeper
  const sendAway = (e) => {
    const tag = e.getTags().find((x) => x.startsWith("civ:shop:"));
    const b = tag ? byId.get(Number(tag.slice(9))) : null;
    if (b && b.keeper && b.keeper !== e.id) e.remove();
  };
  for (const st of s.settlements) { try { for (const e of HB.bodiesOf(st)) if (e.hasTag("civ:keeper")) sendAway(e); } catch { /* left */ } }
  if (s.buildings.some((q) => q.keeper && q.settlement === undefined)) {
    try { for (const e of world.getDimension("minecraft:overworld").getEntities({ tags: ["civ:keeper"] })) { let tg; try { tg = e.getTags(); } catch { continue; } if (!tg.some((x) => x.startsWith("civ:settlement:"))) sendAway(e); } } catch { /* left */ }
  }
  const tm0 = Date.now();
  try { marketBeat(s, duty); } catch (e) { console.warn(`[CIV-SHOP] market: ${e}`); }   // 1.3.224: the market clerk on the square
  // 1.3.231 (INN24): from dusk, once a world day, the inn's guests pay their beds (and the [CIV-INN] line)
  if (tod >= 12000) {
    let wday = 0; try { wday = world.getDay(); } catch { /* left */ }
    for (const st of s.settlements) {
      if (st.innNight === wday) continue;
      const inn = s.buildings.find((q) => q.settlement === st.id && q.stage >= 4 && !q.closed && API.short(q) === "inn");
      if (inn) { try { if (innNight(st, inn, API.BUILDINGS[inn.family], wday, tod, Math.floor(s.simDays))) API.save(); } catch (e) { console.warn(`[CIV-SHOP] inn night: ${e}`); } }
    }
  }
  const tm1 = Date.now();
  // 1.3.227 (profiled at city II: shop beats of 120..423 ms): at most HIRES_PER_BEAT keepers are hired in one beat (each is a
  // spawn and its set-up); the rest are hired on the next beats
  let hires = 0;
  for (const b of s.buildings) {
    if (b.closed || b.stage < 4) continue;
    if (!b.keeper) {                                                  // 1.3.224: a hire that failed (chunk asleep) is tried again
      const def = API.BUILDINGS[b.family];
      if (!def || b.stage < def.stages - 1 || !TRADE[API.short(b)] || (!duty && API.short(b) !== "inn")) continue;   // 1.3.231 (INN24): the inn hires at any hour
      const last = hireTried.get(b.id) || -1e9;
      if (system.currentTick - last < 1200) continue;
      if (hires >= HIRES_PER_BEAT) continue;
      hires++;
      hireTried.set(b.id, system.currentTick);
      try { const dim = world.getDimension(b.dim); if (API.blockAt(dim, b.x, b.y + def.datum_y, b.z)) hireKeeper(dim, b, def, s.settlements.find((x) => x.id === b.settlement)); } catch { /* unloaded */ }   // 1.3.228: guarded
      continue;
    }
    let v;
    try { v = world.getEntity(b.keeper); } catch { v = undefined; }
    if (v && v.hasTag("civ:working")) continue;                       // C2.2: at the pit / the stand / on the way to the store
    if (!v) {
      // the keeper is gone (died, unloaded far away): hire again when the shop's chunk is loaded and it is a work day
      if (hires >= HIRES_PER_BEAT) continue;
      hires++;
      try { const dim = world.getDimension(b.dim); if ((duty || API.short(b) === "inn") && API.blockAt(dim, b.x, b.y + 15, b.z)) { b.keeper = null; hireKeeper(dim, b, API.BUILDINGS[b.family], s.settlements.find((x) => x.id === b.settlement)); } } catch { /* unloaded */ }
      continue;
    }
    const stK = s.settlements.find((x) => x.id === b.settlement) || null;
    // 1.3.228 (B4 / BF5): the keeper's OWN shift (the late template: 09..19, the id's offset, the town's rest day)
    const kOn = stK && API.onShift ? API.onShift(v, stK, tod) : duty;
    if (!kOn) {                                                       // 1.3.224: off duty the keeper goes up to its rooms (it lives over the shop)
      const def = API.BUILDINGS[b.family];
      if (def && API.insideDoor) {
        const home = API.insideDoor(b, def);
        const dh = Math.hypot(v.location.x - home.x, v.location.z - home.z);
        const st = s.settlements.find((x) => x.id === b.settlement);
        if (dh > 2.5 && st && !WALK.walking(v)) WALK.send(v, st, { ...home, mode: "home" });
        else if (dh <= 2.5) { try { if (API.civState) API.civState(v, "home"); } catch { /* left */ } }
      }
      continue;
    }
    if (!b.station) continue;
    // 1.3.228 (B4 / PE1): the beat's spot (the main task at the station, a look about, a second spot, the store, the door —
    // never more than 4 blocks off the station, the store 6) and the block it faces
    const ws = stK && API.workSpot ? API.workSpot(b, v, stK, system.currentTick) : null;
    const tgt = ws ? ws.stand : b.station;
    const d = Math.hypot(v.location.x - tgt.x, v.location.z - tgt.z) + Math.abs(v.location.y - tgt.y);
    if (d > 2.5) {
      // C2.1 (D-C541): the keeper WALKS to the station (the lead primitive); the clock's schedule sends the others
      const st = stK;
      const inShop = Math.hypot(v.location.x - b.station.x, v.location.z - b.station.z) <= 8 && Math.abs(v.location.y - b.station.y) <= 3;
      if (st && !WALK.walking(v) && (!inShop || beatSends < BEAT_SENDS)) {
        try { v.removeEffect("slowness"); } catch { /* left */ }            // the anchor would hold him at the station
        // a move inside the shop is one straight leg (never via the street graph); from outside, the route
        if (inShop) { beatSends++; WALK.sendPath(v, st, [[Math.floor(tgt.x), Math.floor(tgt.z), Math.floor(tgt.y)]]); } else WALK.send(v, st, tgt);
      }
    } else {
      if (WALK.walking(v)) WALK.cancel(v);
      try { if (API.civState) API.civState(v, "stand"); } catch { /* left */ }
      try { const ef = v.getEffect("slowness"); if (!ef || ef.duration < 110 || ef.amplifier < 255) v.addEffect("slowness", 140, { amplifier: 255, showParticles: false }); } catch { /* left */ }   // 1.3.227: renewed only when it runs low
      if (ws && ws.look) { try { v.setRotation({ x: 0, y: API.PEOPLE.yawTo(v.location, ws.look) }); } catch { /* left */ } }   // B4 (PE1): faces the beat's block
    }
  }
  const tm2 = Date.now();
  if (tm2 - tm0 > 150) console.warn(`[CIV-SHOP] slow beat: ${tm2 - tm0} ms (keepers check ${tm0 - tb0}, market ${tm1 - tm0}, shops ${tm2 - tm1}, hires ${hires})`);
} });
const HIRES_PER_BEAT = 2;
const BEAT_SENDS = 2;                            // 1.3.228 (B4 / PE1): beat moves inside the shops a shop beat (the SEND budget)

/** talking to a keeper opens the shop window; talking to ANY other civ opens the talk window (1004b, his 15:27: never
 *  the vanilla emerald screen) */
world.beforeEvents.playerInteractWithEntity.subscribe((ev) => {
  const v = ev.target;
  if (!v || !v.hasTag) return;
  let keeper = false, civ = false;
  try { keeper = v.hasTag("civ:keeper"); civ = keeper || v.hasTag("civ:villager"); } catch { return; }
  if (!civ) return;
  ev.cancel = true;
  const player = ev.player;
  const vname = v.nameTag;
  const mtag = keeper ? v.getTags().find((t) => t.startsWith("civ:market:")) : null;
  if (mtag) { const sid = Number(mtag.slice(11)); system.run(() => { try { openMarket(player, sid, vname); } catch (e) { console.warn(`[CIV-SHOP] market window: ${e}`); } }); return; }
  if (keeper) {
    const tag = v.getTags().find((t) => t.startsWith("civ:shop:"));
    const bid = tag ? Number(tag.slice(9)) : NaN;
    system.run(() => { try { openShop(player, bid, vname, v); } catch (e) { console.warn(`[CIV-SHOP] window: ${e}`); } });
  } else if (innJobOf(v) !== null) {
    // 1.3.231 (INN24): any of the inn's staff serves (the rota's night keeper, the serving staff), not only the keeper
    const bid = innJobOf(v);
    system.run(() => { try { openShop(player, bid, vname, v); } catch (e) { console.warn(`[CIV-SHOP] inn window: ${e}`); } });
  } else {
    system.run(() => { try { VOICE.hold(v, player); openTalk(player, v); } catch (e) { console.warn(`[CIV-SHOP] talk: ${e}`); } });   // B5 (PE11): he stops and faces you
  }
});

/** the TALK window: who this civ is (the census), how they feel, what they have heard — an RPG town is investigated by talking */
export function openTalk(player, v) {
  const s = API.load();
  const tags = v.getTags();
  const stTag = tags.find((t) => t.startsWith("civ:settlement:")), pTag = tags.find((t) => t.startsWith("civ:person:"));
  const st = stTag ? s.settlements.find((x) => x.id === Number(stTag.slice(15))) : null;
  const P = st && st.people, person = P && pTag ? API.PEOPLE.byId(P, Number(pTag.slice(11))) : null;
  const day = Math.floor(s.simDays);
  const name = v.nameTag || (person ? person.name : "a civ");
  const form = new ActionFormData().title(name);
  const lines = [];
  let said = null;
  if (person) {
    const stage = API.PEOPLE.stage(person, day);
    const home = person.home ? s.buildings.find((b) => b.id === person.home) : null;
    const job = person.job ? s.buildings.find((b) => b.id === person.job) : null;
    const trade = typeof person.job === "string" ? person.job : (job ? `${API.short(job)} #${job.id}` : null);
    lines.push(`${stage === "child" ? "A child" : stage === "apprentice" ? "An apprentice" : stage === "elder" ? "An elder" : "A grown civ"} of ${st.name}${home ? `, of the house #${home.id} ${API.short(home)}` : ""}.`);
    lines.push(trade ? `Works as: ${trade}${person.trade ? ` (${API.PEOPLE.rankOf(person, person.trade)})` : ""}.` : (stage === "child" ? "Too young to work." : "Without a trade."));
    if (person.spouse) { const sp = API.PEOPLE.byId(P, person.spouse); if (sp) lines.push(`Married to ${sp.name}.`); }
    if (person.kids && person.kids.length) lines.push(`${person.kids.length} child${person.kids.length === 1 ? "" : "ren"}.`);
    const mood = person.mood ?? 50;
    lines.push(`Mood: ${mood >= 75 ? "content" : mood >= 50 ? "fair" : mood >= 30 ? "low" : "miserable"}.`);
    const g = API.PEOPLE.greeting(P, person, day);
    const pt = ptitle(st, player);                                    // B11 (WP11): the player's title in this town
    lines.push(g.tier === "friend" ? `Greets you as a friend${pt !== "stranger" ? `, ${PLAYER.PTITLE_NAME[pt]}` : ""}.` : g.tier === "customer" ? `Knows your face${pt !== "stranger" ? ` (${PLAYER.PTITLE_NAME[pt]})` : ""}.` : "Does not know you.");
    // 1.3.228 (B5 / PE10): the line comes from the dialogue table (needs, news, temperament — deterministic, never random)
    try { said = VOICE.talkLine(s, st, v, player); } catch (e) { console.warn(`[CIV-VOICE] line: ${e}`); }
    if (said) lines.push(`"${said.text}"`);
    try { if (PLAYER.talkCounts(person, day)) API.PEOPLE.playerContact(person, PLAYER.TALK_FOND); } catch { /* left */ }   // B11 (WP10): 3 a day count
  } else {
    lines.push(st ? `A civ of ${st.name}.` : "A civ.");
  }
  const state = tags.find((t) => t.startsWith("civ:state:"));
  if (state) lines.push(`(${state.slice(10) === "home" ? "at home" : state.slice(10) === "idle" ? "taking the air" : "at work or on watch"})`);
  form.body(lines.join("\n"));
  // 1.3.228 (B5 / BF11): a petitioner waiting on this player is answered here
  const acts = [];
  if (said && said.petition) { acts.push({ label: "I'll see to it", run: () => { if (VOICE.promise(API.load(), st, v, player)) player.sendMessage(`§a${name} will hold you to it — the census checks in 5 days.`); } }); acts.push({ label: "Not now", run: () => {} }); }
  else {
    // B11 (WP10 / WP12 / WP11): give what you hold; "show me the way"; an alderman names a district
    if (person && st) {
      const held = heldItem(player);
      if (held) acts.push({ label: `Give the ${held.typeId.replace(/^[a-z]+:/, "").replace(/_/g, " ")} (${held.amount})`, run: () => giveHeld(player, st, person, v, name) });
      if (API.guideTo) acts.push({ label: "Show me the way to…", run: () => openGuide(player, st, v, name) });
      if (PLAYER.PTITLES.indexOf(ptitle(st, player)) >= 3 && API.districtAt) acts.push({ label: "Name this district (a vote)", run: () => nameDistrict(player, st) });
    }
    acts.push({ label: "Leave", run: () => {} });
  }
  for (const a of acts) form.button(a.label);
  form.show(player).then((r) => { if (!r.canceled && r.selection !== undefined && acts[r.selection]) { try { acts[r.selection].run(); } catch (e) { console.warn(`[CIV-VOICE] act: ${e}`); } } });
}

function goodsOf(kind, ECON) {
  if (kind === "inn") return { sells: Object.keys(ECON.INN_SALES), buys: [] };
  const p = ECON.PRODUCE[kind];
  if (!p) return { sells: [], buys: [] };
  return { sells: Object.keys(p.out), buys: [...new Set([...Object.keys(p.in), ...Object.keys(p.out)])] };
}

// INN24 (1.3.231, his 00:23 ruling; his 02:43 witness "We're closed" from Sven the Innkeeper in daylight). Mechanism: this
// window opened only while the world's time of day was inside the FIXED WORK window (1000..11000) — never the keeper's own
// shift (the late template, 3000..13000) — so 17:00..19:00 (daylight) the keeper stood at his station and refused. Now a
// shop is open while ITS KEEPER is on his own shift (API.onShift), and the inn while ANY of its staff is on the rota's
// duty (PEOPLE.innStatus): "closed" only when no staffer is.
/** INN24: the census person's inn (its job's building id) of a body that is not the keeper, or null */
function innJobOf(v) {
  try {
    if (!API) return null;
    const pTag = v.getTags().find((t) => t.startsWith("civ:person:")), sTag = v.getTags().find((t) => t.startsWith("civ:settlement:"));
    if (!pTag || !sTag) return null;
    const s = API.load(), st = s.settlements.find((x) => x.id === Number(sTag.slice(15)));
    const p = st && st.people ? API.PEOPLE.byId(st.people, Number(pTag.slice(11))) : null;
    if (!p || !p.alive || typeof p.job !== "number") return null;
    const b = s.buildings.find((x) => x.id === p.job);
    return b && API.short(b) === "inn" && b.stage >= 4 && !b.closed ? b.id : null;
  } catch { return null; }
}
/** INN24: the inn's staff on duty at world time (tod, wday) -> { on: [persons], next: ticks until open (0 now; null never),
 *  staff, rota } — the rota over the census staff (the same rota the clock's schedule walks them by) */
export function innNow(st, b, tod, wday, simDay) {
  const staff = st && st.people ? API.PEOPLE.innStaff(st.people, b.id, simDay) : [];
  return { ...API.PEOPLE.innStatus(staff, tod, wday, { seed: (st && st.seed) || 0 }), staff };
}
const ROLE = { inn_solo: "innkeeper", inn_long_d: "day", inn_long_n: "night", inn_day: "day", inn_eve: "evening", inn_night: "night", inn_serve: "serving" };
/** INN24: a guest rents a bed for tonight (the player): the price returns to the treasury (as a sale does), once a night */
function rentBed(player, st, b, vname) {
  const L = st && st.ledger, price = API.PEOPLE.INN24.bedP;
  let wday = 0; try { wday = world.getDay(); } catch { /* left */ }
  const e = (st && st.pstats && st.pstats[player.name]) || null;
  if (e && e.bed === wday) { player.sendMessage(`§7${vname}: "Your bed is paid for tonight — any free bed upstairs."`); return; }
  if (!COIN.payPennies(player, price, st ? st.name : "the inn", `a bed at the inn #${b.id}`)) { player.sendMessage(`§c${vname}: "A bed is ${COIN.fmtP(price)} — you carry ${COIN.fmtP(COIN.countPennies(player))}."`); return; }
  if (L) { L.treasury += price; L.playerNet += price; L.sales[b.id] = (L.sales[b.id] || 0) + 1; }
  pstat(st, player, "t");
  try { st.pstats[player.name].bed = wday; } catch { /* no name */ }
  API.save();
  player.sendMessage(`§a${vname}: "A bed for the night, ${COIN.fmtP(price)}. Any free bed upstairs is yours — sleep well."`);
}
/** INN24: once a world day (from dusk) the inn's guests — the homeless the clock lodges there (PEOPLE.innGuests) — pay
 *  their beds from the citizens' purse into the inn's till (the economy's day pays the till out: toll to the treasury,
 *  the rest to the purse); one [CIV-INN] line a town a day */
export function innNight(st, b, def, wday, tod, simDay) {
  if (!st || !b || st.innNight === wday || tod < 12000) return null;
  st.innNight = wday;
  const guests = API.PEOPLE.innGuests(st.people ? st.people.list : [], API.PEOPLE.bedsOf(def ? def.dir : []), b.id);
  const L = st.ledger;
  const bill = API.PEOPLE.lodgeBill(guests.length, L ? L.purse : 0);
  if (L && bill.paid > 0) { L.purse -= bill.paid; L.tills[b.id] = (L.tills[b.id] || 0) + bill.paid; L.sales[b.id] = (L.sales[b.id] || 0) + Math.max(1, Math.round(bill.paid / API.ECON.COIN)); }
  if (guests.length) st.log.push(`day ${simDay}: ${guests.length} without a home slept at the inn #${b.id} (${bill.paid} of ${bill.price} pennies paid)`);
  const S = innNow(st, b, tod, wday, simDay);
  const roles = {}; for (const [, t] of S.rota) roles[ROLE[t] || t] = (roles[ROLE[t] || t] || 0) + 1;
  console.warn(`[CIV-INN] ${JSON.stringify({ st: st.id, inn: b.id, day: wday, staff: S.staff.length, roles, on: S.on.length, guests: guests.length, paid: bill.paid })}`);
  return { guests, bill };
}

export function openShop(player, bid, vname, v = null) {
  const s = API.load();
  const b = s.buildings.find((x) => x.id === bid);
  if (!b) { player.sendMessage("§7The shopkeeper shrugs."); return; }
  const st = s.settlements.find((x) => x.id === b.settlement);
  const L = st && st.ledger;
  const ECON = API.ECON;
  const kind = API.short(b);
  let tod = 0, wday = 0; try { tod = world.getTimeOfDay(); wday = world.getDay(); } catch { /* left */ }
  let serving = null;
  if (kind === "inn") {
    const S = innNow(st, b, tod, wday, Math.floor(s.simDays));
    if (!S.on.length) {
      const at = S.next !== null ? ` — we open at ${String(API.PEOPLE.hourOf(tod + S.next)).padStart(2, "0")}:00` : "";
      player.sendMessage(`§7${vname}: "We're closed${at}."`); return;
    }
    serving = S.on.map((q) => `${q.name} (${ROLE[S.rota.get(q.id)] || "staff"})`);
  } else {
    let on;
    try { on = v && st && API.onShift ? API.onShift(v, st, tod) : onDuty(); } catch { on = onDuty(); }
    if (!on) { player.sendMessage(`§7${vname}: "We're closed — come back in the morning."`); return; }
  }
  if (b.closed) { player.sendMessage(`§7${vname}: "The shop has closed."`); return; }
  const coins = COIN.countCoins(player);
  const form = new ActionFormData().title(`${vname}`);
  const acts = [];
  let body = `${st ? st.name : ""} · you carry §e${COIN.fmtP(COIN.countPennies(player))}§r`;
  if (kind === "town_hall") {
    const em = COIN.countItem(player, "minecraft:emerald");
    body += ` and ${em} emerald${em === 1 ? "" : "s"}\nThe town's treasury: ${L ? Math.floor(L.treasury / ECON.COIN) : 0} coin · coins in circulation: ${COIN.inCirculation()}`;
    for (const n of [1, 8]) {
      acts.push({ label: `Change ${n} emerald${n > 1 ? "s" : ""} for ${n * COIN.COIN_PER_EMERALD} coins`, run: () => exchangeIn(player, st, n, vname) });
      acts.push({ label: `Change ${n * COIN.COIN_PER_EMERALD} coins for ${n} emerald${n > 1 ? "s" : ""}`, run: () => exchangeOut(player, st, n, vname) });
    }
    acts.push({ label: "The mint's ledger", run: () => showLedger(player) });
  } else if (L) {
    const { sells, buys } = goodsOf(kind, ECON);
    const lines = [];
    for (const g of sells) {
      const unit = PLAYER.buyUnit(ECON.counterPrice(L, g, b.id, Math.floor(s.simDays)), st.standing);   // B7 (BF9 + WE7) the counter's price; B11 (WP9) your standing
      lines.push(`${g}: ${ECON.sellable(L, g)} for sale at ${COIN.fmtP(unit)} each`);
      for (const n of [1, 8]) {
        const q = ECON.quote(L, g, n, unit);
        if (q && q.n > 0) acts.push({ label: `Buy ${q.n} ${g} — ${COIN.fmtP(q.exact)}`, run: () => buy(player, st, b, g, n, vname) });   // B7: exact (nickels)
      }
    }
    for (const g of buys) {
      const have = COIN.countItem(player, ECON.ITEM[g]);
      if (have <= 0) continue;
      const n = Math.min(have, 64);
      const pay = PLAYER.sellPay(Math.floor(n * L.prices[g] * SHOP_RATE), st.standing);   // B7 exact pennies (the label said coins); B11 (WP9) standing
      if (pay > 0) acts.push({ label: `Sell ${n} ${g} — ${COIN.fmtP(pay)}`, run: () => sell(player, st, b, g, n, vname) });
    }
    body += `\n${lines.join("\n")}`;
  }
  if (kind === "inn" && serving) {                                   // 1.3.231 (INN24): who is on duty; a bed for the night
    body += `\nServing now: ${serving.join(", ")}`;
    acts.unshift({ label: `Rent a bed for the night — ${COIN.fmtP(API.PEOPLE.INN24.bedP)}`, run: () => rentBed(player, st, b, vname) });
    if (v && v.isValid) acts.push({ label: "Talk", run: () => { try { VOICE.hold(v, player); openTalk(player, v); } catch (e) { console.warn(`[CIV-SHOP] talk: ${e}`); } } });
  }
  acts.push({ label: "Leave", run: () => {} });
  form.body(body);
  for (const a of acts) form.button(a.label);
  form.show(player).then((r) => { if (!r.canceled && r.selection !== undefined) { try { acts[r.selection].run(); } catch (e) { console.warn(`[CIV-SHOP] act: ${e}`); } } });
}

function buy(player, st, b, good, n, vname) {
  const s = API.load();
  const L = st.ledger;
  const unit = PLAYER.buyUnit(API.ECON.counterPrice(L, good, b.id, Math.floor(s.simDays)), st.standing);   // B7 (BF9) + B11 (WP9)
  const q = API.ECON.quote(L, good, n, unit);
  if (!q || q.n <= 0) { player.sendMessage(`§7${vname}: "Sold out, sorry."`); return; }
  // 1.3.228 (B7 / WE10): the exact price in pennies — gold first, nickels, change in nickels
  if (!COIN.payPennies(player, q.exact, st.name, `bought ${q.n} ${good} at #${b.id}`)) { player.sendMessage(`§c${vname}: "That's ${COIN.fmtP(q.exact)} — you carry ${COIN.fmtP(COIN.countPennies(player))}."`); return; }
  API.ECON.buy(L, good, q.n, unit);
  L.sales[b.id] = (L.sales[b.id] || 0) + Math.max(1, Math.round(q.exact / API.ECON.COIN));   // the shop sold something today (no lean day)
  COIN.giveItem(player, API.ECON.ITEM[good], q.n);
  pstat(st, player, "t");                                             // B11 (WP11): a trade
  try { st.pstats[player.name].last = b.id; } catch { /* no name */ }   // B11 (WP12): "the shop you last bought from"
  API.save();
  player.sendMessage(`§a${vname}: "${q.n} ${good}, ${COIN.fmtP(q.exact)}. Thank you!"`);
  void s;
}

const SHOP_RATE = 0.75, MARKET_RATE = 0.6;      // 1.3.224 (his answer): a shop pays a bit more for its own goods than the market
function sell(player, st, b, good, n, vname) {
  const L = st.ledger;
  const pay = PLAYER.sellPay(Math.floor(n * L.prices[good] * SHOP_RATE), st.standing);   // B7 (WE10) exact pennies; B11 (WP9) standing
  if (pay <= 0) return;
  if (L.treasury < pay) { player.sendMessage(`§7${vname}: "The town can't pay for that today."`); return; }
  if (!COIN.takeItem(player, API.ECON.ITEM[good], n)) return;
  L.stock[good] += n;
  L.treasury -= pay; L.playerNet -= pay;                            // the ledger's invariant (economy.sell)
  COIN.issuePennies(player, pay, st.name, `paid for ${n} ${good} at #${b.id}`);
  pstat(st, player, "t");
  API.save();
  player.sendMessage(`§a${vname}: "${COIN.fmtP(pay)} for your ${good}."`);
}

function exchangeIn(player, st, n, vname) {
  if (!COIN.takeItem(player, "minecraft:emerald", n)) { player.sendMessage(`§c${vname}: "You need ${n} emerald${n > 1 ? "s" : ""}."`); return; }
  const c = n * COIN.COIN_PER_EMERALD;
  if (st && st.ledger) st.ledger.treasury += 0;                   // emeralds bought the coins: the treasury neither gains nor pays
  COIN.issue(player, c, st ? st.name : "the mint", `exchanged for ${n} emerald${n > 1 ? "s" : ""}`);
  API.save();
  player.sendMessage(`§a${vname}: "${c} gold coins for your emeralds."`);
}

function exchangeOut(player, st, n, vname) {
  const c = n * COIN.COIN_PER_EMERALD;
  if (!COIN.takeCoins(player, c)) { player.sendMessage(`§c${vname}: "That takes ${c} coins."`); return; }
  COIN.returned(player, c, st ? st.name : "the mint", `exchanged for ${n} emerald${n > 1 ? "s" : ""}`);
  COIN.giveItem(player, "minecraft:emerald", n);
  API.save();
  player.sendMessage(`§a${vname}: "${n} emerald${n > 1 ? "s" : ""} for your coins."`);
}

function showLedger(player) {
  const c = COIN.census();
  const l = COIN.ledger();
  player.sendMessage(`§e[MINT] issued ${c.issued} (serials #1-#${c.seq}) · returned ${c.returned} · lost ${c.destroyed} · in circulation ${c.circulation}` +
    ` · carried by players online ${c.carried} · in ${c.piles} pile(s) ${c.inPiles}`);
  for (const line of l.lines.slice(-8)) player.sendMessage(`§7  ${line}`);
}

// ------------------------------------------------------------------------------------------------ THE MARKET (1.3.224)
// His 16:50: "I can't find anyone at any of the shops to purchase or sell to … I need to be able to sell so I can accumulate
// gold coins … man a post (like a point of sale clerk) when it's work hours." His answer: a BROAD market list. Every
// founded settlement keeps a MARKET CLERK at a stall on the square's corner from its first day: on duty (work hours) at the
// stall, off duty in lodgings. The clerk BUYS a broad list (wood, stone, crops, meat, wool, leather, ores, ingots …) at
// the town's live price x MARKET_RATE (a shop pays SHOP_RATE for its own goods) — or at a fixed export price for things the
// town does not stock — paid in gold coins from the treasury; and SELLS what the town has in stock at the live price.
const MARKET_TABLE = [
  // [test, good | null, multiplier (good) | pennies each (export)]
  [/^minecraft:(stripped_)?\w*_(log|wood|stem|hyphae)$/, "timber", 1], [/^pw:\w*_log$/, "timber", 1], [/^pw:(oak|birch|spruce|jungle|acacia|dark_oak|mangrove|cherry|pale_oak)_(young|mature|old|elder)$/, "timber", 1],
  [/_planks$/, "planks", 1],
  [/^minecraft:(cobblestone|cobbled_deepslate|stone|andesite|diorite|granite|deepslate|tuff|blackstone|sandstone|mossy_cobblestone|calcite)$/, "stone", 1],
  [/^minecraft:(stone_bricks|polished_andesite|polished_diorite|polished_granite|smooth_stone)$/, "stone", 1.5],
  ["minecraft:wheat", "grain", 1], [/^minecraft:(carrot|potato|beetroot)$/, "grain", 0.5], ["minecraft:hay_block", "thatch", 1],
  ["minecraft:bread", "bread", 1],
  [/^minecraft:cooked_(beef|porkchop|mutton|chicken|rabbit)$/, "meat", 1], [/^minecraft:cooked_(cod|salmon)$/, "fish", 1.2], [/^minecraft:(cod|salmon)$/, "fish", 0.8], ["minecraft:tropical_fish", "fish", 0.5],
  [/^minecraft:(beef|porkchop|mutton|chicken|rabbit)$/, "meat", 0.5],
  ["minecraft:leather", "hides", 1], ["minecraft:rabbit_hide", "hides", 0.25], [/^minecraft:\w*_wool$/, "hides", 0.5],
  ["minecraft:iron_ingot", "iron", 1], ["minecraft:raw_iron", "iron", 0.7], ["minecraft:iron_nugget", "iron", 0.1], ["minecraft:iron_block", "iron", 9],
  ["minecraft:bone_meal", "lime", 1], ["minecraft:bone", "lime", 3],
  ["minecraft:glass", "glass", 1], ["minecraft:sand", "glass", 0.15],
  [/^minecraft:iron_(pickaxe|axe|shovel|hoe|sword)$/, "tools", 0.8],
  ["minecraft:gold_ingot", null, 96], ["minecraft:raw_gold", null, 70], ["minecraft:gold_nugget", null, 10], ["minecraft:gold_block", null, 864],
  ["minecraft:diamond", null, 480], ["minecraft:coal", null, 8], ["minecraft:charcoal", null, 6],
  ["minecraft:copper_ingot", null, 14], ["minecraft:raw_copper", null, 10], ["minecraft:lapis_lazuli", null, 12], ["minecraft:redstone", null, 5],
  ["minecraft:quartz", null, 10], ["minecraft:amethyst_shard", null, 10], ["minecraft:string", null, 3], ["minecraft:feather", null, 2],
  ["minecraft:egg", null, 3], ["minecraft:honeycomb", null, 8], ["minecraft:ink_sac", null, 4], ["minecraft:apple", null, 6],
  ["minecraft:melon_slice", null, 2], ["minecraft:pumpkin", null, 8], ["minecraft:sugar_cane", null, 3], ["minecraft:sweet_berries", null, 2],
];
/** what the market pays for one item of this type, in pennies (0 = it does not buy it), and the ledger good it becomes */
export function marketOffer(L, typeId) {
  for (const [test, good, k] of MARKET_TABLE) {
    const hit = typeof test === "string" ? test === typeId : test.test(typeId);
    if (!hit) continue;
    if (good) return { good, k, pennies: (L.prices[good] || 0) * k * MARKET_RATE };
    return { good: null, k: 1, pennies: k };
  }
  return null;
}
const MARKET_SPOT = [1, 1];                       // the clerk's cell on the square (12 x 12; the well stands at +3..7 / +3..8)
export function marketStation(st) { return { x: st.square.x + MARKET_SPOT[0] + 0.5, y: st.square.y + 1, z: st.square.z + MARKET_SPOT[1] + 0.5 }; }
/** the stall: a barrel counter and a lantern post beside the clerk (only into air) */
function buildStall(dim, st) {
  const x = st.square.x + MARKET_SPOT[0], y = st.square.y + 1, z = st.square.z + MARKET_SPOT[1];
  const put = (dx, dy, dz, id) => { try { const b = dim.getBlock({ x: x + dx, y: y + dy, z: z + dz }); if (b && b.isAir) b.setType(id); } catch { /* unloaded */ } };
  put(1, 0, 0, "minecraft:barrel"); put(0, 0, -1, "minecraft:oak_fence"); put(0, 1, -1, "minecraft:lantern");
  put(-1, 0, 0, "minecraft:barrel");
}
function marketLodging(s, st) {
  const homes = s.buildings.filter((b) => b.settlement === st.id && b.stage >= 4 && !b.palace && /cottage|house|home|manor|inn/.test(API.short(b)));
  const inn = homes.find((b) => API.short(b) === "inn");
  const b = inn || homes[0];
  return b ? API.insideDoor(b, API.BUILDINGS[b.family]) : null;
}
const clerkTried = new Map();
/** every keeper beat: each settlement's market clerk — hired once the square stands, at the stall on duty, lodged off duty */
function marketBeat(s, duty) {
  for (const st of s.settlements) {
    if (!st.square || !st.kit || st.phase !== "built") continue;
    const dim = world.getDimension(st.dim);
    let v = null;
    if (st.mclerk) { try { v = world.getEntity(st.mclerk); } catch { v = null; } }
    const at = marketStation(st);
    if (!v) {
      if (!duty) continue;
      const last = clerkTried.get(st.id) || -1e9;
      if (system.currentTick - last < 1200) continue;
      clerkTried.set(st.id, system.currentTick);
      let loaded = false;
      loaded = !!API.blockAt(dim, Math.floor(at.x), Math.floor(at.y), Math.floor(at.z));   // 1.3.228: guarded
      if (!loaded) continue;
      // a clerk standing in a chunk that slept comes back later: the old one (tagged for this market) is retired first
      try { for (const e of dim.getEntities({ tags: [`civ:market:${st.id}`] })) e.remove(); } catch { /* left */ }
      try {
        const c = dim.spawnEntity(API.VILLAGER_ID, at);
        const name = API.nameFor({ id: 9000 + st.id }, st);
        c.nameTag = `${name} the Market Clerk`;
        for (const tg of ["civ:villager", "civ:keeper", `civ:market:${st.id}`, `civ:settlement:${st.id}`]) c.addTag(tg);
        try { if (API.civOn) API.civOn(c); } catch { /* left */ }
        st.mclerk = c.id;
        buildStall(dim, st);
        st.log.push(`day ${API.load().simDays.toFixed(0)}: ${c.nameTag} opens the market stall on the square`);
        API.save();
      } catch (e) { console.warn(`[CIV-SHOP] market clerk: ${e}`); }
      continue;
    }
    if (duty) {
      const d = Math.hypot(v.location.x - at.x, v.location.z - at.z);
      if (d > 2.0) { if (!WALK.walking(v)) WALK.send(v, st, at); }
      else {
        if (WALK.walking(v)) WALK.cancel(v);
        try { if (API.civState) API.civState(v, "stand"); } catch { /* left */ }
        try { const ef = v.getEffect("slowness"); if (!ef || ef.duration < 110 || ef.amplifier < 255) v.addEffect("slowness", 140, { amplifier: 255, showParticles: false }); } catch { /* left */ }   // 1.3.227: renewed only when it runs low
      }
    } else {
      const home = marketLodging(s, st);
      if (!home) continue;
      const dh = Math.hypot(v.location.x - home.x, v.location.z - home.z);
      if (dh > 2.5) { if (!WALK.walking(v)) WALK.send(v, st, { ...home, mode: "home" }); }
      else { try { if (API.civState) API.civState(v, "home"); } catch { /* left */ } }
    }
  }
}
/** the market window: sell everything the market buys that you carry (each kind as one button), buy from the town's stock */
export function openMarket(player, sid, vname) {
  const s = API.load();
  const st = s.settlements.find((x) => x.id === sid);
  const L = st && st.ledger;
  const ECON = API.ECON;
  if (!L) { player.sendMessage(`§7${vname}: "The market isn't open yet."`); return; }
  if (!onDuty()) { player.sendMessage(`§7${vname}: "The stall is shut — come back in the morning."`); return; }
  const coins = COIN.countCoins(player);
  const form = new ActionFormData().title(`${vname}`);
  const acts = [];
  // what the player carries that the market buys (by item type)
  const inv = player.getComponent("minecraft:inventory").container;
  const have = new Map();
  for (let i = 0; i < inv.size; i++) { const it = inv.getItem(i); if (it) have.set(it.typeId, (have.get(it.typeId) || 0) + it.amount); }
  const offers = [];
  for (const [id, n] of have) { const o = marketOffer(L, id); if (o && o.pennies > 0) offers.push({ id, n, ...o }); }
  offers.sort((a, b) => b.pennies * b.n - a.pennies * a.n);
  for (const o of offers) {
    const pay = PLAYER.sellPay(Math.floor(o.n * o.pennies), st.standing);   // B7 exact pennies; B11 (WP9) standing
    const nice = o.id.replace(/^[a-z]+:/, "").replace(/_/g, " ");
    if (pay > 0) acts.push({ label: `Sell ${o.n} ${nice} — ${COIN.fmtP(pay)}`, run: () => marketSell(player, st, o.id, vname) });
    else acts.push({ label: `Sell ${o.n} ${nice} — not worth a nickel (bring more)`, run: () => player.sendMessage(`§7${vname}: "That's not worth a nickel yet — bring more."`) });
  }
  // the town's stock for sale (live price)
  const lines = [];
  for (const g of ECON.GOODS) {
    if (Math.floor(L.stock[g] || 0) <= 0) continue;
    lines.push(`${g}: ${Math.floor(L.stock[g])} at ${(L.prices[g] / ECON.COIN).toFixed(2)} coin each`);
    for (const n of [1, 16]) { const q = ECON.quote(L, g, n, PLAYER.buyUnit(L.prices[g], st.standing)); if (q && q.n > 0) acts.push({ label: `Buy ${q.n} ${g} — ${COIN.fmtP(q.exact)}`, run: () => marketBuy(player, st, g, n, vname) }); }
  }
  // 1.3.228 (B7 / BF8): the town's NOTICES — real gaps the player can fill for a reward (at most NOTICE_CAP a day)
  let slips = [];
  try { slips = API.noticeSlips ? API.noticeSlips(s, st) : []; } catch (e) { console.warn(`[CIV-SHOP] notices: ${e}`); }
  if (slips.length) acts.push({ label: `Notices (${slips.length})`, run: () => openNotices(player, st, vname) });
  if (API.chronicleOf) acts.push({ label: "The town's chronicle", run: () => openChronicle(player, st) });   // B10 (WP7)
  acts.push({ label: "Leave", run: () => {} });
  form.body(`${st.name} market · you carry §e${COIN.fmtP(COIN.countPennies(player))}§r · the treasury holds ${Math.floor(L.treasury / ECON.COIN)} coin\n` +
    (offers.length ? "The clerk will buy what you carry (below)." : "Nothing you carry is wanted here — wood, stone, crops, meat, wool, leather, ores and ingots are.") +
    (lines.length ? `\n\nFor sale:\n${lines.join("\n")}` : ""));
  for (const a of acts) form.button(a.label);
  form.show(player).then((r) => { if (!r.canceled && r.selection !== undefined) { try { acts[r.selection].run(); } catch (e) { console.warn(`[CIV-SHOP] market act: ${e}`); } } });
}
function marketSell(player, st, id, vname) {
  const L = st.ledger;
  const ECON = API.ECON;
  const n = COIN.countItem(player, id);
  const o = marketOffer(L, id);
  if (!o || n <= 0) return;
  const pay = PLAYER.sellPay(Math.floor(n * o.pennies), st.standing);   // B7 exact pennies; B11 (WP9) standing
  if (pay <= 0) return;
  if (L.treasury < pay) { player.sendMessage(`§7${vname}: "The town can't pay that much today (${Math.floor(L.treasury / ECON.COIN)} coin in the chest)."`); return; }
  if (!COIN.takeItem(player, id, n)) return;
  if (o.good) L.stock[o.good] = (L.stock[o.good] || 0) + n * o.k;
  L.treasury -= pay; L.playerNet -= pay;
  L.marketBought = (L.marketBought || 0) + Math.round(pay / ECON.COIN);
  COIN.issuePennies(player, pay, st.name, `the market bought ${n} ${id.replace(/^[a-z]+:/, "")}`);
  pstat(st, player, "t");
  API.save();
  player.sendMessage(`§a${vname}: "${COIN.fmtP(pay)} for your ${id.replace(/^[a-z]+:/, "").replace(/_/g, " ")}."`);
}
function marketBuy(player, st, good, n, vname) {
  const L = st.ledger;
  const unit = PLAYER.buyUnit(L.prices[good], st.standing);          // B11 (WP9)
  const q = API.ECON.quote(L, good, n, unit);
  if (!q || q.n <= 0) { player.sendMessage(`§7${vname}: "Sold out, sorry."`); return; }
  if (!COIN.payPennies(player, q.exact, st.name, `bought ${q.n} ${good} at the market`)) { player.sendMessage(`§c${vname}: "That's ${COIN.fmtP(q.exact)} — you carry ${COIN.fmtP(COIN.countPennies(player))}."`); return; }
  API.ECON.buy(L, good, q.n, unit);
  COIN.giveItem(player, API.ECON.ITEM[good], q.n);
  pstat(st, player, "t");
  API.save();
  player.sendMessage(`§a${vname}: "${q.n} ${good}, ${COIN.fmtP(q.exact)}. Thank you!"`);
}

// ------------------------------------------------------------------------------------------------ 1.3.228 B11: the player
/** the player's counters in a town (st.pstats[name] = { t: trades, s: slips }) — a small map per town */
function pstat(st, player, k, n = 1) {
  try { st.pstats = st.pstats || {}; const e = st.pstats[player.name] || (st.pstats[player.name] = {}); e[k] = (e[k] || 0) + n; } catch { /* no name */ }
}
/** WP11: the player's title in a town (derived on the spot: nothing saved but the counters) */
function ptitle(st, player) {
  if (!st) return "stranger";
  const e = (st.pstats && st.pstats[player.name]) || {};
  const tier = String(st.tier || "village");
  const tierClass = tier === "capital" ? 4 : tier.startsWith("metropolis") ? 3 : tier.startsWith("city") ? 2 : tier.startsWith("town") ? 1 : 0;
  const townLevel = Number((tier.match(/(\d)$/) || [0, 1])[1]);
  return PLAYER.ptitleOf({ standing: st.standing || 0, trades: e.t || 0, slips: e.s || 0, stall: !!e.stall, tierClass, townLevel });
}
export function ptitleIn(st, player) { return ptitle(st, player); }
function heldItem(player) {
  try { const inv = player.getComponent("minecraft:inventory").container; const it = inv.getItem(player.selectedSlotIndex); return it || null; } catch { return null; }
}
/** WP10: a gift — the held stack goes to the person's household (the town's store when the market knows the good) */
function giveHeld(player, st, person, v, name) {
  const it = heldItem(player);
  if (!it) return;
  const L = st.ledger, s = API.load(), day = Math.floor(s.simDays);
  const o = L ? marketOffer(L, it.typeId) : null;
  const value = o ? Math.floor(it.amount * (o.good ? (L.prices[o.good] || 0) * o.k : o.pennies)) : it.amount;
  const interest = API.PEOPLE.interestName ? API.PEOPLE.interestName(person) : null;
  const r = PLAYER.giveTo(person, day, value, !!(o && o.good && PLAYER.likes(interest, o.good)));
  if (r.refused) { player.sendMessage(`§7${name}: "You're too kind — I can't take any more today."`); return; }
  const n = it.amount;
  if (!COIN.takeItem(player, it.typeId, n)) return;
  if (o && o.good && L) L.stock[o.good] = (L.stock[o.good] || 0) + n * o.k;
  API.save();
  player.sendMessage(`§a${name}: "${r.fond >= 6 ? "That's very generous — thank you!" : r.fond >= 2 ? "Thank you, truly." : "Oh — thank you."}"`);
  console.warn(`[CIV-GIFT] ${JSON.stringify({ st: st.id, pid: person.id, item: it.typeId, n, value, fond: r.fond, gn: person.gn })}`);
}
/** WP12: where the guide can take the player */
function openGuide(player, st, v, name) {
  const places = API.guidePlaces ? API.guidePlaces(st, player) : [];
  if (!places.length) { player.sendMessage(`§7${name}: "I don't know the way anywhere yet."`); return; }
  const form = new ActionFormData().title(`${name} — show me the way`);
  for (const p of places) form.button(p.label);
  form.button("Never mind");
  form.show(player).then((r) => {
    if (r.canceled || r.selection === undefined || r.selection >= places.length) return;
    try { if (API.guideTo(v, player, st, places[r.selection])) player.sendMessage(`§a${name}: "Follow me — ${places[r.selection].label.toLowerCase()} it is."`); else player.sendMessage(`§7${name}: "I can't find the way just now."`); } catch (e) { console.warn(`[CIV-GUIDE] ${e}`); }
  });
}
/** WP11: an alderman (or councillor) puts a new name for the district he stands in to the town's vote */
function nameDistrict(player, st) {
  const d = API.districtAt(st, Math.floor(player.location.x), Math.floor(player.location.z));
  if (!d) { player.sendMessage("§7You are not standing on a street of this town."); return; }
  new ModalFormData().title(`Rename ${d.name}`).textField("The new name (3..24 letters)", d.name).show(player).then((r) => {
    if (r.canceled || !r.formValues) return;
    const nm = PLAYER.cleanName(r.formValues[0]);
    if (!nm) { player.sendMessage("§cThat name won't do (3..24 letters)."); return; }
    const adults = API.PEOPLE.alive(st.people || { list: [] }).filter((p) => API.PEOPLE.stage(p, Math.floor(API.load().simDays)) === "adult");
    const vt = PLAYER.vote(adults);
    player.sendMessage(`§e${st.name} votes on "${nm}": ${vt.yes} yes, ${vt.no} no, ${vt.abstain} abstain — ${vt.pass ? "§aCARRIED" : "§cLOST"}`);
    if (vt.pass && API.renameDistrict) { API.renameDistrict(st, d.sid, nm); API.save(); }
  });
}
/** 1.3.228 (B10 / WP7): the chronicle — the town's annals and its latest news */
function openChronicle(player, st) {
  const form = new ActionFormData().title(`${st.name} — chronicle`).body(API.chronicleOf(st)).button("Close");
  form.show(player).catch(() => {});
}
// ------------------------------------------------------------------------------------------------ 1.3.228 B7 (BF8): notices
const NOTICE_CAP = 10;
const noticesToday = new Map();            // "player id|day" -> n (memory: a reload may allow a few more; harmless)
function openNotices(player, st, vname) {
  const s = API.load();
  const slips = API.noticeSlips(s, st);
  const day = Math.floor(s.simDays);
  const key = `${player.id}|${day}`;
  const used = noticesToday.get(key) || 0;
  const form = new ActionFormData().title(`${st.name} — notices`);
  const acts = [];
  const lines = slips.map((x) => `${x.qty} ${x.good} — ${COIN.fmtP(x.reward)} (${x.why}); you carry ${COIN.countItem(player, API.ECON.ITEM[x.good])}`);
  for (const x of slips) {
    const have = COIN.countItem(player, API.ECON.ITEM[x.good]);
    if (have >= x.qty && used < NOTICE_CAP) acts.push({ label: `Deliver ${x.qty} ${x.good} — ${COIN.fmtP(x.reward)}`, run: () => deliverNotice(player, st, x, vname) });
  }
  acts.push({ label: "Back", run: () => {} });
  form.body(`${lines.join("\n") || "Nothing wanted today."}${used >= NOTICE_CAP ? "\n\n(You have filled enough notices today.)" : ""}`);
  for (const a of acts) form.button(a.label);
  form.show(player).then((r) => { if (!r.canceled && r.selection !== undefined && acts[r.selection]) { try { acts[r.selection].run(); } catch (e) { console.warn(`[CIV-SHOP] notice: ${e}`); } } });
}
function deliverNotice(player, st, slip, vname) {
  const s = API.load();
  const L = st.ledger;
  const day = Math.floor(s.simDays);
  if (!st.slips || st.slips.day !== day || st.slips.done.includes(slip.good)) { player.sendMessage(`§7${vname}: "That notice is already filled."`); return; }
  if (L.treasury < slip.reward) { player.sendMessage(`§7${vname}: "The town can't pay that today."`); return; }
  if (!COIN.takeItem(player, API.ECON.ITEM[slip.good], slip.qty)) { player.sendMessage(`§7${vname}: "You need ${slip.qty} ${slip.good}."`); return; }
  if (!API.ECON.deliverSlip(L, slip)) { COIN.giveItem(player, API.ECON.ITEM[slip.good], slip.qty); return; }
  st.slips.done.push(slip.good);
  COIN.issuePennies(player, slip.reward, st.name, `notice: ${slip.qty} ${slip.good}`);
  pstat(st, player, "s");                                            // B11 (WP11): a notice filled
  const key = `${player.id}|${day}`;
  noticesToday.set(key, (noticesToday.get(key) || 0) + 1);
  st.log.push(`day ${day}: a traveller filled the notice for ${slip.qty} ${slip.good} (${COIN.fmtP(slip.reward)})`);
  API.save();
  player.sendMessage(`§a${vname}: "${slip.qty} ${slip.good} — the town thanks you. ${COIN.fmtP(slip.reward)}."`);
}
