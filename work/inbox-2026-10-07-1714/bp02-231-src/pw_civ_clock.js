// pw_civ_clock.js — CIVITAS VILLAGE CLOCK + TIME TOOL (BP-02 v1.3.219): the living town on the land.
// v1.3.219 (D-C529 / D-C530): new settlements lay HIS StreetKit pieces (KIT STREETS below: straight streets, ramps,
//   dead ends with sewer outfalls, bridges with railing openings, side streets by T junctions, streets that grow,
//   village width -> town width at tier town), houses flush on the street at sidewalk height with an access piece at
//   each sewer shaft; KEEPERS at the shops' stations in work hours and a COIN SHOP window (pw_civ_shop.js); the GOLD
//   COIN mint (pw_civ_coin.js); floating leaves cleared daily; a PARK at tier town. Older settlements keep their streets.
// Bedrock has no /tick (BDS probe 10-02): the world cannot be run faster, so the village owns its own clock.
//   * The clock follows the WORLD's days (world.getDay() + time of day): sleeping, /time add and normal play all move it.
//     One advance(days) does every change, whether the days came from play, the time tool or offline catch-up.
//   * FOUNDING (step 1 of the world-shaping program, D-C498): `village` reads the land 80 blocks around the spot as a job
//     (pw_civ_land.js site field: ground + water), finds the flattest 12 x 12 knoll (the SQUARE: paved, lanterns, the
//     well, the notice board) and walks the MAIN STREET along the contour from the square's edge, on whichever axis the
//     hill offers more frontage (north-south streets since 0.0.12). Streets are laid once from a smoothed PROFILE (<= 1
//     block per cell; cut / fill; path; cobble steps; a plank BRIDGE over a drop >= 4; a clad CUTTING through a rise >= 3).
//   * PLOTS take slots along a street (both sides, from the middle out), each with a 2-cell FRONT YARD before the street
//     body; the floor is street + 1 .. + 3 (deeper into the hill when the ground is higher), the footprint is TERRACED
//     (cobblestone retaining ring, dirt core; the hill side clad), the yard levelled to the street and the STOOP's steps
//     climb in the yard. Buildings grow through authored STAGES (structures/pw/stages/<building>_s0..s4: plot, frame,
//     walls, roof, furnished; STAGE_DAYS between them); a stage whose chunk is not loaded waits quietly.
//   * Every building can be turned (None / Rotate90 / Rotate180 / Rotate270); after a turned stage every direction-
//     carrying block (pw_civ_buildings.js "dir") gets its rigidly-turned state and hatch lids their hinge.
//   * SETTLEMENTS grow by tier (village -> village2 25 d -> town 60 -> town2 120 -> city 200) when every plot is roofed and
//     the people are fed (prosperity >= 0.8 over 5 days): new terrace streets open at h0 +- 6 / 4 / 8 / 10 / 12, LIVING
//     MARKS appear (quarry pit, lumberyard clearing, harvests, streets path -> gravel -> cobble, a city WALL with gates, a
//     pier when water is near). The ECONOMY (pw_civ_economy.js) runs daily: production, meals, prices in a band, the inn's
//     trade, charters for 10-day shortages, closures of a shop that sold nothing for 20 days (only among >= 2 of a kind),
//     households that move in / leave / return (vanilla villagers, named, with their trade once they work).
//   * DAUGHTERS: a prosperous town (pop >= 24, fed 30 days) sends settlers 170-230 blocks away; the daughter founds
//     herself the same way; a ROAD is found by A* over the real ground (LAND.findRoadJob: around every plot, across streets
//     at their own grade) and laid like a street; goods TRADE along it; the LADDER: a market stand after 5 days of inbound
//     goods, a branch after 20. The chronicle is the notice board's text and `log`.
//   * STATE: one JSON in chunked dynamic properties (pw:civ_clock:n + :i, 30,000 chars each — a city passed 32 KB);
//     site fields in pw:civ_site:<id>; snapshots likewise.
// Commands (chat):  /scriptevent pw:clock <command>     (PW-TestRunner forwards /scriptevent pw:time … here)
//   status                    clock, speed, pause, every building and its stage (no player: pw:clock_bld / pw:clock_stl events)
//   plot [building] [rot]     start a building beside you (box starts 2 blocks east, ground floor at your feet);
//                             building = cottage_s | cottage_s_b (skin) | pw:mvv_cottage_s_b_r1
//   plotat x y z [building] [rot]   the same at a given spot (ground-floor feet level y)
//   village [seed]            found a settlement on the land where you stand (the site read, the square, the contour
//                             street, the first 12 plots; skins by seed) · villageat x z [seed] the same at x z ·
//                             add `flat` for the straight test street of V1
//   grow [n]                  settlement n (default: the one nearest you / the first) reaches its next tier now
//   decline on|off [n]        the settlement declines: no growth, a shop closes every 20 days (webs, stations gone)
//   immigrate [building] [n]  newcomers: an empty home fills, else a closed shop reopens, else a new plot (the named building)
//   log [n]                   the settlement's chronicle · market  stock, prices (coin) and treasury
//   buy <good> <n>            buy from the town for emeralds (1 emerald = 4 coin) · sell <good> <n>  sell to the town at 70 %
//   step [days] / skip <days> advance the village by days — the world's own clock does not move
//   speed <x>                 village days per world day (0.1 .. 100; default 1) · pause | resume
//   snapshot save|load|list <name>   store the whole state, or put it back (stages re-placed up to the saved one)
//   beat                      the heartbeat's window so far -> [CIV-BEAT] (1.3.228) · dpceiling <MB>  the dynamic-property warning ceiling
//   why [name|CODE]           why-idle codes: the tally per town, one person's reason, or who has a code (1.3.228 B2 / BF3)
//   why icons on|off          the reason as a short suffix on the names of villagers near a player (OFF by default)
//   savehold [off]            the save hold (a stored town that could not be read is never overwritten until released)
//   shift [name] [template|default]   BF5 shifts: the templates per town and who is off today, one person's shift, or set
//                             his template (the only saved shift field, p.shift; default clears it) (1.3.228 B4)
//   prio [family|clear]       build this family first inside the tier charter (a free command, B6) · tax low|normal|high (B7)
//   audit · board              the economy's ledger check / the notice board (B7)
//   beds                       the palace's role beds: held / reserved per role and who sleeps there (1.3.229)
import { world, system, ItemStack, BlockVolume, BlockTypes, BlockPermutation, LiquidType, StructureAnimationMode } from "@minecraft/server";
import { CIV_BUILDINGS } from "./pw_civ_buildings.js";
import * as ECON from "./pw_civ_economy.js";
import * as PEOPLE from "./pw_civ_people.js";                    // D-C536: the census — relationships, happiness, gossip
import * as LAND from "./pw_civ_land.js";
import * as KIT from "./pw_civ_streets.js";
import * as LN from "./pw_civ_lanes.js";                         // 1.3.226: contour lanes (his 20:01 / 20:48)
import * as HB from "./pw_civ_beat.js";                          // 1.3.228 (B1 / BF1): one heartbeat, tick slots, the bodies cache
import * as SAVE from "./pw_civ_save.js";                        // 1.3.228 (B2 / BF2): sectioned saves
const PROF = (globalThis.__civProf = globalThis.__civProf || {});
import { PARK_TREE_SET } from "./pw_civ_parktrees.js";
import * as SHOP from "./pw_civ_shop.js";
import * as WALK from "./pw_civ_walk.js";                        // C2.1 (D-C541): villagers walk where the clock sends them
import * as WORKMOD from "./pw_civ_work.js";
import { weatherIn } from "./pw_weather.js";                    // 1.3.224: rain sends the idle home
import * as KEYS from "./pw_civ_keys.js";
import * as VOICE from "./pw_civ_voice.js";
import * as PLAYER from "./pw_civ_player.js";                     // 1.3.228 (B11): standing, talk, gifts, festivals, titles
import * as GUEST from "./pw_civ_guest.js";
import * as COURT from "./pw_civ_court.js";                       // 1.3.229 ROLE BEDS (his 14:07): the palace beds by role                       // 1.3.228 (B11): festivals, the dusk speech, the guide, deeds (OFF)
import * as PLAN from "./pw_civ_plan.js";
import * as NAMES_ from "./pw_civ_names.js";                       // 1.3.228 (B9): district names, town titles, "Now entering"                          // 1.3.228 (B6): the weighted pick, district skins, relief, fillers, weathering                       // 1.3.228 (B5): speech bubbles, talk stops, overheard talk, petitioners
import * as WATCH from "./pw_civ_watch.js";                       // F5 (D-C538): patrols above and below ground (monsters only: Utopia-First)                         // F4 (D-C538 / D-C539): the sewer keys — a register, not a recipe                     // C2.2 (D-C542): quarrymen mine, woodcutters fell, both carry to the store
import * as COIN from "./pw_civ_coin.js";
import * as GALLERY from "./pw_gallery.js";                     // 1.3.222: unique paintings hang at the furnished stage (D-C571)
import { templateFallingSet, isTreeLeafId, isTreeLogId, templateCells, templateName, turnOffset, touchesPlacedLog, hasNaturalCanopy } from "./pw_fell_rules.js";   // 1004b: the town fells a tree by its TEMPLATE (D-C563)

const KEY = SAVE.LEGACY;                      // the pre-1.3.228 single-JSON key (pw:civ_clock): read once and migrated by pw_civ_save.js
void KEY;
const SNAP = "pw:civ_clock_snap:";
const STAGE_NAMES = ["plot", "frame", "walls", "roof", "furnished"];
const STAGE_DAYS = [1, 2, 2, 1];              // village days spent at stage k before stage k+1 is placed
const BUILDINGS = CIV_BUILDINGS;
const ROTS = ["None", "Rotate90", "Rotate180", "Rotate270"];
const CARD = ["north", "east", "south", "west"];                  // clockwise
const FACING = { 2: "north", 3: "south", 4: "west", 5: "east" };  // facing_direction ints
const FACING_INV = { north: 2, south: 3, west: 4, east: 5 };
const DIRN = ["south", "west", "north", "east"];                  // bed / bell / grindstone "direction" ints (clockwise)
const PWDIR = { "pw:n": "north", "pw:e": "east", "pw:s": "south", "pw:w": "west" };
const PWKEY = { north: "pw:n", east: "pw:e", south: "pw:s", west: "pw:w" };
const VILLAGE_STAGGER = 1;                    // village days between one plot and the next
// the village street plan (west -> east). North side: fronts face south (Rotate270); south side: fronts face north (Rotate90)
const VILLAGE_NORTH = ["farm_wheat", "cottage_s", "bakery", "town_hall", "inn", "butcher", "smithy"];
const VILLAGE_SOUTH = ["quarry", "cottage_m", "cottage_l", "lumberyard", "farm_cattle"];      // the well stands on the square (step 2)
const STREET_W = 3;                           // street rows z0 .. z0+2
// ---- SETTLEMENTS (V3, economy draft §4 + his E3 ~60 / ~200 days, E4 decline yes, immigration): a settlement is the record
// that owns a village's plots and grows it through TIERS on the village clock. Each tier adds plots along the streets
// (the allocator extends the street east, then opens a parallel street 24 blocks north / south). Growth needs the tier's
// age AND every plot roofed. Decline (E4): while a settlement is declining it does not grow and every DECLINE_DAYS one
// shop closes (cobwebs in its doorway, its station markers removed); immigration reopens shops first, then adds cottages.
// ASSUMPTION (his 20:04): until the economy (V5) drives prosperity, growth is driven by days + completion, and decline is
// switched by the `decline` tool (or a future economic trigger).
// D-C535 (his 21:52): THREE steps per tier — village I-III, town I-III, city I-III, metropolis I-III — and above them the
// PORT CITY (docks) / CAPITAL CITY. Day gates, cumulative buildings 12 .. 500, population records 24 .. 5,000-10,000.
const TIERS = ["village", "village2", "village3", "town", "town2", "town3", "city", "city2", "city3", "metropolis", "metropolis2", "metropolis3", "capital"];
const TIER_DAYS = { village2: 25, village3: 50, town: 80, town2: 120, town3: 170, city: 230, city2: 300, city3: 380, metropolis: 480, metropolis2: 600, metropolis3: 750, capital: 950 };
const TIER_LABEL = { village: "village I", village2: "village II", village3: "village III", town: "town I", town2: "town II", town3: "town III", city: "city I", city2: "city II", city3: "city III",
                     metropolis: "metropolis I", metropolis2: "metropolis II", metropolis3: "metropolis III", capital: "capital city" };
const TIER_CLASS = (tier) => tier === "capital" ? 4 : tier.startsWith("metropolis") ? 3 : tier.startsWith("city") ? 2 : tier.startsWith("town") ? 1 : 0;
const tierLabel = (st) => st.tier === "capital" ? (st.docks ? "PORT CITY" : "CAPITAL CITY") : TIER_LABEL[st.tier] || st.tier;
// people per dwelling by tier class: cottages (village), the same houses let as tenements and apartments as the town densifies
const DENSITY = [1, 1.5, 3, 6, 10];
// REPRESENTATION (his 21:52): partners with a market stand or a branch here (the Presence Ladder); [partners, cities, metropolises]
const REP_REQ = { city: [2, 0, 0], city2: [3, 0, 0], city3: [4, 0, 0], metropolis: [6, 1, 0], metropolis2: [8, 2, 0], metropolis3: [10, 3, 0], capital: [12, 3, 1] };
const DAUGHTERS_MAX = [1, 2, 3, 3, 3], DAUGHTER_GAP = 60;
// what each tier adds (building, count) — cumulative 12 / 20 / 28 / 40 / 55 / 75 / 100 / 135 / 175 / 230 / 300 / 380 / 500
const TIER_ADDS = {
  village2: [["cottage_s", 3], ["cottage_m", 2], ["farm_terrace", 1], ["cottage_l", 1], ["farm_wheat", 1]],
  village3: [["cottage_s", 3], ["cottage_m", 2], ["bakery", 1], ["cottage_l", 1], ["farm_cattle", 1]],
  town: [["cottage_l", 2], ["cottage_s", 4], ["cottage_m", 2], ["lumberyard", 1], ["inn", 1], ["butcher", 1], ["smithy", 1]],
  town2: [["manor", 1], ["cottage_m", 5], ["cottage_s", 5], ["cottage_l", 2], ["farm_wheat", 1], ["bakery", 1], ["quarry", 1]],
  town3: [["cottage_m", 6], ["cottage_s", 7], ["cottage_l", 3], ["farm_terrace", 1], ["farm_cattle", 1], ["smithy", 1], ["inn", 1]],
  city: [["town_hall", 1], ["bakery", 2], ["cottage_l", 5], ["cottage_m", 7], ["cottage_s", 6], ["quarry", 1], ["well", 1], ["butcher", 1], ["lumberyard", 1]],
  city2: [["cottage_s", 10], ["cottage_m", 10], ["cottage_l", 6], ["bakery", 1], ["butcher", 1], ["smithy", 1], ["inn", 2], ["farm_wheat", 2], ["farm_cattle", 1], ["lumberyard", 1]],
  city3: [["cottage_s", 12], ["cottage_m", 12], ["cottage_l", 7], ["bakery", 2], ["butcher", 1], ["smithy", 1], ["inn", 1], ["farm_wheat", 1], ["farm_terrace", 1], ["quarry", 1], ["town_hall", 1]],
  metropolis: [["cottage_s", 16], ["cottage_m", 16], ["cottage_l", 10], ["bakery", 2], ["butcher", 2], ["smithy", 2], ["inn", 2], ["farm_wheat", 2], ["farm_cattle", 1], ["lumberyard", 1], ["quarry", 1]],
  metropolis2: [["cottage_s", 20], ["cottage_m", 20], ["cottage_l", 14], ["bakery", 3], ["butcher", 2], ["smithy", 2], ["inn", 2], ["farm_wheat", 2], ["farm_terrace", 2], ["farm_cattle", 1], ["lumberyard", 1], ["quarry", 1]],
  metropolis3: [["cottage_s", 24], ["cottage_m", 22], ["cottage_l", 16], ["bakery", 3], ["butcher", 3], ["smithy", 2], ["inn", 3], ["farm_wheat", 2], ["farm_cattle", 2], ["lumberyard", 2], ["quarry", 1]],
  capital: [["cottage_s", 36], ["cottage_m", 34], ["cottage_l", 24], ["bakery", 5], ["butcher", 4], ["smithy", 3], ["inn", 4], ["farm_wheat", 3], ["farm_terrace", 2], ["farm_cattle", 2], ["lumberyard", 2], ["quarry", 1]],
};
const STREET_MAX = 90;                        // a street takes plots up to this length before a new one opens
const STREET_GAP = 40;                        // z between parallel streets: two 16-deep plots back to back + the street + gaps (probe run 3: 26 overlapped)
const DECLINE_DAYS = 20;                      // one shop closes per this many declining days
const SHOPS = ["bakery", "butcher", "smithy", "inn", "lumberyard", "quarry"];
// ---- VILLAGERS (V4 first slice; ASSUMPTION under his 20:04): the game's own villagers live in our buildings. When a
// dwelling is furnished the clock spawns its household at the door; they claim our beds, take the jobs our shops hold
// (smoker, blast furnace, lectern, composter, stonecutter, barrel …) and meet at the town-hall bell, walking the terraces
// and steps with the engine's pathfinding. Our station markers drive the economy (V5), not the walking (V4b).
const HOUSEHOLD = { cottage_s: 2, cottage_m: 2, cottage_l: 3, inn: 1, farm_wheat: 1, farm_terrace: 1, farm_cattle: 1, manor: 4 };
const NAMES = ["Ada", "Bram", "Cora", "Dag", "Edda", "Finn", "Greta", "Hal", "Ida", "Jory", "Kari", "Lars", "Maud", "Nils", "Orla",
               "Pim", "Rhea", "Sven", "Tess", "Ulf", "Vera", "Wim", "Ylva", "Zane"];
const VILLAGER_ID = "minecraft:villager_v2";
// ---- ECONOMY (V5 slice 1, pw_civ_economy.js): one ledger per settlement, one dayStep per whole village day. Shortages
// charter the missing shop on a free plot (the Catchment Law in action), lean shops close for real, tier growth needs
// prosperity (everyone ate for 5 days) once the economy runs. ASSUMPTION (his 20:04): the charter table below.
const CHARTER = { bread: "bakery", meat: "butcher", grain: "farm_terrace", hides: "farm_cattle", timber: "lumberyard", stone: "quarry", tools: "smithy" };
const CHARTER_DAYS = 10;                      // days of shortage before a shop is chartered
const GROWTH_PROSPERITY = 0.8;                // mean prosperity over the last 5 days needed for a tier (0.8 = most people ate)

let state = null;
// 1.3.228 (B2 / WE14): DIAGNOSTICS live in memory, not in the save (st.marketGate, st.counters and st.marketTry were
// written with the town on every market pass) — status still shows them; a reload forgets them (harmless)
const DIAG = new Map();                                            // settlement id -> { counters, marketGate, marketTry }
function diagOf(st) { let d = DIAG.get(st.id); if (!d) DIAG.set(st.id, (d = {})); return d; }
// st.market.homes was a list that grew with every purchase: it is a COUNT now, and today's homes are a memory Set (after a
// reload a household may shop twice that day — harmless)
const marketHomes = new Map();                                     // settlement id -> { day, homes: Set }
function homesToday(st, day) { let m = marketHomes.get(st.id); if (!m || m.day !== day) marketHomes.set(st.id, (m = { day, homes: new Set() })); return m.homes; }
/** a loaded settlement's saved diagnostics move to memory (a legacy / 227 save carries them) */
export function diagOutOfSave(st) {
  if (st.marketGate !== undefined) { diagOf(st).marketGate = st.marketGate; delete st.marketGate; }
  if (st.counters !== undefined) { diagOf(st).counters = st.counters; delete st.counters; }
  if (st.marketTry !== undefined) { const t = st.marketTry || {}; diagOf(st).marketTry = { day: t.day, goals: t.goals || 0, noShop: t.noShop || 0, shoppers: new Set(t.shoppers || []) }; delete st.marketTry; }
  if (st.market && Array.isArray(st.market.homes)) { const hs = new Set(st.market.homes); marketHomes.set(st.id, { day: st.market.day, homes: hs }); st.market.homes = hs.size; }
}

function worldDays() {
  return world.getDay() + world.getTimeOfDay() / 24000;
}

/** a text of any length in dynamic properties: <key>:n = the chunk count, <key>:<i> = 30,000-char chunks (one property
 *  holds 32,767 chars at most — run 0.0.14's city state was 34,075 and 45 saves failed; the single-key form of
 *  v1.3.206/early 207 is still read). 1.3.228 (B2 / BF2): the chunked texts live in pw_civ_save.js (pure, node-tested);
 *  these wrappers keep their old names for the snapshots and the site fields. */
const TEXT_CHUNK = SAVE.TEXT_CHUNK;
function putText(key, txt) { SAVE.putText(world, key, txt); return Math.ceil(txt.length / TEXT_CHUNK) || 1; }
function getText(key) { return SAVE.getText(world, key); }
function dropText(key) { SAVE.dropText(world, key); }
// 1.3.228 (B2 / BF2): the town is saved in SECTIONS (pw_civ_save.js: meta, buildings per settlement, each settlement's
// core / streets / people / ledger, the index last); a save writes only the sections whose text changed, all in one tick
const SAVER = SAVE.createSaver(world);
let saveHold = false;                      // a saved town was there but could not be read: never overwrite it with a fresh one
let saveHoldSaid = -1e9;

/** raw = a whole-state JSON to load instead of the saved town (a snapshot restore) */
function load(raw = undefined) {
  if (state) return state;
  let from = "none", problems = [];
  try {
    if (raw !== undefined) { state = JSON.parse(raw); from = "snapshot"; }
    else { const r = SAVER.load(); state = r.state; from = r.from; problems = r.problems || []; }
  } catch (e) { state = null; problems.push(String(e).slice(0, 80)); }
  if (problems.length) console.warn(`[CIV-SAVE] load (${from}): ${problems.length} problem(s): ${problems.slice(0, 8).join("; ")}`);
  if (from === "legacy") console.warn("[CIV-SAVE] the legacy save (pw:civ_clock) was loaded: the next save writes the sections and drops it");
  if (!state && problems.length && raw === undefined) { saveHold = true; console.warn("[CIV-SAVE] HOLD: the saved town could not be read — saves are held so it is not overwritten (pw:clock savehold off releases)"); }
  if (!state) state = { paused: false, speed: 1, simDays: 0, lastWorld: worldDays(), buildings: [], nextId: 1, settlements: [] };
  if (!state.settlements) state.settlements = [];
  if (!state.buildings) state.buildings = [];
  for (const b of state.buildings) {          // records from v1.3.206 (no rotation / delay / footprint)
    if (b.rot === undefined) b.rot = 0;
    if (b.delay === undefined) b.delay = 0;
  }
  for (const st of state.settlements) diagOutOfSave(st);     // 1.3.228 (B2 / WE14)
  return state;
}

/** 1.3.224: save() marks the state dirty; the state is written at most once per SAVE_EVERY ticks (it was written on every
 *  lag beat — a large town's state is a multi-megabyte string each time: memory and slow ticks). saveNow() writes. */
const SAVE_EVERY = 600;                                  // 1.3.227 (gate 226-2: 22 MB of dynamic properties saved a minute at 150 buildings): every 30 s
let lastSaveTick = -1e9, saveDirty = false;
function save(force = false) {
  saveDirty = true;
  if (!force) return;                                      // 1.3.228: the save slot writes (was: at once when SAVE_EVERY had passed)
  saveNow();
}
// 1.3.228 (B1 / BF1): the save check is a heartbeat slot (19); a save() between checks only marks the state dirty, so the
// multi-megabyte write never lands in another heavy beat's tick (save(true) still writes at once)
HB.register("save", { fn: () => { if (saveDirty && state && system.currentTick - lastSaveTick >= SAVE_EVERY) saveNow(); } });
// 1.3.228 (his 14:07, "save the village each time the game closes"): the town already lives IN the world (dynamic
// properties, written every SAVE_EVERY); what closing could lose is the last <= 30 s since that write. The shutdown
// before-event (stable in @minecraft/server 2.3.0; "after players have left, before the world has closed") writes it.
// setDynamicProperty carries no read-only restriction in the 2.3.0 typings — the BDS stop + his PS5 close are the witnesses.
try {
  system.beforeEvents.shutdown.subscribe(() => {
    if (!state) return;
    if (!saveDirty) { console.warn("[CIV-SAVE] shutdown: the town was already saved"); return; }
    try { saveNow(); console.warn(`[CIV-SAVE] shutdown: final save written (tick ${system.currentTick})`); } catch (e) { console.warn(`[CIV-SAVE] shutdown save failed: ${e}`); }
  });
} catch (e) { console.warn(`[CIV-SAVE] no shutdown hook on this engine: ${e}`); }
function saveNow() {
  if (!state) return;
  if (saveHold) {
    if (system.currentTick - saveHoldSaid >= 6000) { saveHoldSaid = system.currentTick; console.warn("[CIV-SAVE] HOLD: not saved (the stored town could not be read at load; pw:clock savehold off releases)"); }
    return;
  }
  lastSaveTick = system.currentTick;
  saveDirty = false;
  for (const st of state.settlements || []) {
    if (st.log && st.log.length > 60) st.log.splice(0, st.log.length - 60);           // the chronicle keeps its last 60 lines
    if (st.ledger && st.ledger.history.length > 30) st.ledger.history.splice(0, st.ledger.history.length - 30);
  }
  try {
    const r = SAVER.write(state);                                       // 1.3.228 (B2 / BF2): changed sections, one tick, index last
    state.bytes = r.total;                                              // reported by status (the world's memory of itself)
    console.warn(`[CIV-SAVE] ${JSON.stringify({ wrote: r.wrote, of: r.of, chars: r.chars, total: r.total, chunks: r.chunks, gen: r.gen, tick: system.currentTick, ...(r.migrated ? { migrated: 1 } : {}), ...(r.dropped ? { dropped: r.dropped } : {}), keys: r.changed.map((k) => k.replace("pw:civ:", "")) })}`);
  } catch (e) { console.warn(`[CIV-CLOCK] save failed: ${e}`); }
  dpCheck();
}
// 1.3.228 (B1 / EN4): the world's dynamic-property bytes after each save write (once per save, never in a loop): kept as
// state.dpBytes; one [CIV-DP] line whenever a settlement's tier changes (the probe reads it per tier); a warning when the
// bytes grow 25 % within one set of tiers, or pass the ceiling (DP_CEILING, or `pw:clock dpceiling <MB>`)
const DP_CEILING = 4 * 1024 * 1024;
const dpMark = { key: null, base: 0, warnAt: 0, ceilWarned: -1e9, unsupported: false };
function dpCheck() {
  if (!state || dpMark.unsupported) return;
  let n;
  try { n = world.getDynamicPropertyTotalByteCount(); } catch (e) { dpMark.unsupported = true; console.warn(`[CIV-DP] getDynamicPropertyTotalByteCount unavailable: ${e}`); return; }
  if (typeof n !== "number") return;
  state.dpBytes = n;
  const key = (state.settlements || []).map((x) => `${x.id}:${x.tier}`).join(",");
  if (dpMark.key !== key) {
    console.warn(`[CIV-DP] ${JSON.stringify({ tiers: key, bytes: n, stateChars: state.bytes || 0, buildings: (state.buildings || []).length, tick: system.currentTick })}`);
    dpMark.key = key; dpMark.base = n; dpMark.warnAt = Math.ceil(n * 1.25);
  } else if (n > dpMark.warnAt) {
    console.warn(`[CIV-DP] dynamic properties grew to ${n} B (+${Math.round((n / dpMark.base - 1) * 100)} % since ${dpMark.base} B at these tiers: ${key})`);
    dpMark.warnAt = Math.ceil(n * 1.25);
  }
  const ceil = state.dpCeiling || DP_CEILING;
  if (n > ceil && system.currentTick - dpMark.ceilWarned >= 6000) { dpMark.ceilWarned = system.currentTick; console.warn(`[CIV-DP] dynamic properties ${n} B are above the ceiling ${ceil} B`); }
}

// ------------------------------------------------------------------------------------------------ rotation law
/** saved-file (x, z) -> offset from the placement corner after `rot` clockwise quarter turns (BDS-verified 10-02). */
export function rotXZ(x, z, sx, sz, rot) {
  if (rot === 1) return [sz - 1 - z, x];
  if (rot === 2) return [sx - 1 - x, sz - 1 - z];
  if (rot === 3) return [z, sx - 1 - x];
  return [x, z];
}

function footprint(def, rot) {
  const [sx, sy, sz] = def.size;
  return rot % 2 ? [sz, sy, sx] : [sx, sy, sz];
}

const turnCard = (c, n) => CARD[(CARD.indexOf(c) + n) % 4];

/** the states a block must carry after the building is turned n quarter turns clockwise (rigid body). */
export function turnStates(states, n) {
  const out = {};
  for (const [k, v] of Object.entries(states)) {
    if (k === "minecraft:cardinal_direction") out[k] = turnCard(v, n);
    else if (k === "facing_direction") out[k] = FACING[v] ? FACING_INV[turnCard(FACING[v], n)] : v;
    else if (k === "direction") out[k] = DIRN.indexOf(turnCard(DIRN[v], n));
    else if (k === "pillar_axis") out[k] = n % 2 && v !== "y" ? (v === "x" ? "z" : "x") : v;
    else if (PWDIR[k]) out[PWKEY[turnCard(PWDIR[k], n)]] = v;
    else out[k] = v;
  }
  return out;
}

/** after a turned stage: give every direction-carrying block of this building its turned state; returns how many it set. */
let turnLog = 0;
function fixDirections(dim, b, def) {
  if (!b.rot) return 0;
  const [sx, , sz] = def.size;
  let set = 0;
  for (const [x, y, z, name, states] of def.dir) {
    const [ox, oz] = rotXZ(x, z, sx, sz, b.rot);
    let blk;
    try { blk = dim.getBlock({ x: b.x + ox, y: b.y + y, z: b.z + oz }); } catch { blk = undefined; }
    if (!blk || blk.typeId !== name) continue;               // not placed yet (a later stage) or changed by a player
    const want = turnStates(states, b.rot);
    const got = blk.permutation.getAllStates();
    // booleans come back as true/false while the roster table carries 0/1: compare by value, not by type
    const same = (a, b) => a === b || (typeof a === "boolean" && a === Boolean(b)) || (typeof b === "boolean" && b === Boolean(a));
    if (Object.entries(want).every(([k, v]) => same(got[k], v))) continue;
    if (turnLog < 40) { turnLog++; console.warn(`[CIV-CLOCK] turned ${name} (${ROTS[b.rot]}): engine left ${JSON.stringify(got)}, set ${JSON.stringify(want)}`); }
    try {
      let perm = blk.permutation;
      for (const [k, v] of Object.entries(want)) perm = perm.withState(k, typeof got[k] === "boolean" ? Boolean(v) : v);
      blk.setPermutation(perm);
      set++;
    } catch (e) { console.warn(`[CIV-CLOCK] turn ${name} failed: ${e}`); }
  }
  return set;
}

function turnLids(dim, b, def) {
  if (!b.rot) return 0;
  const [sx, , sz] = def.size;
  let n = 0;
  for (const [x, fy, z, hinge] of def.lids) {
    const [ox, oz] = rotXZ(x, z, sx, sz, b.rot);
    for (const e of dim.getEntitiesAtBlockLocation({ x: b.x + ox, y: b.y + fy + def.datum_y, z: b.z + oz })) {
      if (e.typeId !== "pw:hatch_lid") continue;
      try { e.setProperty("pw:hinge", (hinge + b.rot) % 4); n++; } catch { /* left */ }
    }
  }
  return n;
}

// ------------------------------------------------------------------------------------------------ ground + plot prep
const NOT_GROUND = ["leaves", "_log", "_wood", "log", "short_grass", "tall_grass", "fern", "flower", "vine", "snow_layer", "bush",
  "mushroom", "sapling", "roots", "propagule", "dandelion", "poppy", "tulip", "petals", "orchid", "allium", "bluet", "daisy",
  "cornflower", "lily", "rose", "peony", "lilac", "sunflower", "azalea", "berry", "dripleaf", "moss_carpet", "pumpkin",
  "melon", "cactus", "sugar_cane", "bamboo", "deadbush", "web", "torch", "pw:"];
const CLEAR_OVER = ["leaves", "log", "_wood", "vine", "pw:", "bee_nest", "cocoa"];

function isGround(id) {
  if (id === "minecraft:air") return false;
  return !NOT_GROUND.some((s) => id.includes(s)) || id.startsWith("pw:ground") || id.includes("grass_block");
}

// 1.3.227 (memprobe 0.0.1 / leakdiag, 10-06): EVERY Script API call that THROWS leaks ~650 B of server memory, never
// freed (3 M out-of-bounds getBlock throws: +1.94 GB), and Block.below/above/offset leak the same without throwing. The
// planners read the ground at the edge of the loaded land thousands of times a second at metropolis (the topmost block's
// typeId threw "unloaded chunk": 140 k throws = +92 MB). So: ask dim.isChunkLoaded first (it does not throw), check
// block.isValid before reading it, and count what still throws (pw:clock status -> engine throws).
export const ENGINE = { throws: 0 };
// 1.3.228 (B1 hygiene): exported (and handed to the work / watch / shop / keys / walk modules through their init) — every
// hot-path block read of CIVITAS goes through these. `loaded` = the caller already found this COLUMN loaded in this tick
// (a chunk is loaded for its whole height): the isChunkLoaded ask is skipped, the read stays in try.
export function blockAt(dim, x, y, z, loaded = false) {  // undefined = outside the world, null = chunk not loaded
  if (y < -64 || y > 319) return undefined;
  if (!loaded && !dim.isChunkLoaded({ x, y, z })) return null;
  try { const b = dim.getBlock({ x, y, z }); return b && b.isValid ? b : null; } catch { ENGINE.throws++; return null; }
}
/** 1.3.228 (B1 hygiene): every chunk of the box [x0..x1] x [z0..z1] is loaded — asked before a getBlocks over the box (a
 *  volume read over a sleeping chunk throws: the leak path); isChunkLoaded never throws */
export function boxLoaded(dim, x0, z0, x1, z1) {
  for (let x = x0; ; x = Math.min(x + 16, x1)) {
    for (let z = z0; ; z = Math.min(z + 16, z1)) { if (!dim.isChunkLoaded({ x, y: 64, z })) return false; if (z >= z1) break; }
    if (x >= x1) break;
  }
  return true;
}
export function topAt(dim, x, z) {                       // the topmost block, or undefined (unloaded / none)
  if (!dim.isChunkLoaded({ x, y: 64, z })) return undefined;
  try { const b = dim.getTopmostBlock({ x, z }); return b && b.isValid ? b : undefined; } catch { ENGINE.throws++; return undefined; }
}

/** y of the ground block at (x, z): topmost block, walking down past trees, plants and snow (undefined if unloaded).
 *  t0: the column's topmost block when the caller has just read it (1.3.228: the survey reads it once for both uses). */
export function groundAt(dim, x, z, t0 = null) {
  try {
    // 1.3.227 (gate 227-3: the server grew 150 MB / 30 s during slot searches and was OOM-killed at metropolis; memprobe
    // 0.0.1: Block.below() / above() / offset() leak ~650 B of server memory per call, never freed): step down with
    // dimension.getBlock at the computed cell (no leak)
    const t = t0 || topAt(dim, x, z);
    if (!t) return undefined;
    let y = t.location.y, b = t;
    for (let i = 0; b && i < 48; i++) {
      if (isGround(b.typeId)) return y;
      y--;
      b = blockAt(dim, x, y, z, true);                      // 1.3.228: the column is loaded (topAt asked) — one engine call a step
    }
    return b ? y : undefined;
  } catch { ENGINE.throws++; return undefined; }                                // an unloaded chunk anywhere on the way down
}

function median(a) {
  const s = a.slice().sort((p, q) => p - q);
  return s[Math.floor(s.length / 2)];
}

/** measure the plot's ground once its chunk is loaded: datum feet 0 = median ground + 1. */
function settle(dim, b, def) {
  const [fx, , fz] = footprint(def, b.rot);
  const hs = [];
  for (let i = 0; i < fx; i += 2) for (let j = 0; j < fz; j += 2) {
    const g = groundAt(dim, b.x + i, b.z + j);
    if (g === undefined) return false;
    hs.push(g);
  }
  let floor = median(hs) + 1;                               // feet 0 = one above the median ground
  // ELEVATION (his 22:23 / 22:24): a plot never sits below its street, and never more than 4 above it — a higher plot is
  // cut deeper into the hill (its back rooms in the slope, the roof emerging). The street's height is its laid PROFILE.
  const sh = streetHeightAtDoor(b, def);
  if (sh !== undefined) floor = Math.max(sh + 1, Math.min(floor, sh + 1 + (b.yard || 0)));     // the stoop (one step per yard cell) must reach the street
  b.y = floor - def.datum_y;
  b.settled = true;
  return true;
}

/** the laid street height in front of the door: the settlement's profile if this plot belongs to a planned street,
 *  else the ground in front of the door. */
function streetHeightAtDoor(b, def) {
  if (b.kit) return b.kit.H;                                     // v1.3.219: a kit plot stands at its street's sidewalk height
  const front = doorFront(b, def);
  if (!front) return undefined;
  const s = load();
  const st = s.settlements.find((x) => x.id === b.settlement);
  if (st && st.profile) {
    // from the front cell, step toward the street (the door's facing) across the yard until a street body cell is met
    const body = LAND.streetBody(st.profile, st.axis || "x");
    const dx = b.rot === 0 ? -1 : b.rot === 2 ? 1 : 0, dz = b.rot === 1 ? -1 : b.rot === 3 ? 1 : 0;
    for (let k = 0; k <= (b.yard || 0) + 1; k++) { const h = body.get(`${front.x + dx * k},${front.z + dz * k}`); if (h !== undefined) return h; }
    const key = `${front.x},${front.z}`;
    if (st.profile[key] !== undefined) return st.profile[key];
    for (const d of [1, 2, -1, -2]) { const k2 = `${front.x},${front.z + d}`; if (st.profile[k2] !== undefined) return st.profile[k2]; }
    for (const d of [1, 2, -1, -2]) { const k3 = `${front.x + d},${front.z}`; if (st.profile[k3] !== undefined) return st.profile[k3]; }
  }
  try { return groundAt(world.getDimension(b.dim), front.x, front.z); } catch { return undefined; }
}

/** the world cell just outside the door (on the street side), from the table's door cell and the plot's rotation. */
function doorFront(b, def) {
  const [sx, , sz] = def.size;
  const door = def.door || [0, 0, Math.floor(sz / 2)];
  const [ox, oz] = rotXZ(-1, door[2], sx, sz, b.rot);       // local x -1 = one cell in front of the front wall
  return { x: b.x + ox, z: b.z + oz, fy: door[1] };
}

// ------------------------------------------------------------------------------------------------ elevation (his 22:23)
// How a settlement deals with sloping ground:
//  1. TERRACE every plot before its foundations: the footprint is cut to the floor level (the structure's own air does that)
//     and FILLED below the floor slab where the ground falls away — cobblestone on the outer ring (a retaining face), dirt
//     inside — so no floor ever floats and the downhill side reads as a stone terrace wall.
//  2. The STREET keeps a walkable profile: along its length the surface never changes more than one block per cell
//     (the higher side is cut down), low spots are filled, the surface is a path, and every one-block rise gets a
//     cobblestone step; plants above the street are cleared.
//  3. A STOOP joins the street to the door: cobblestone steps climb from the street in front of the door up to the floor,
//     one step out per block of height (the plot's own clearance column).
const FILL_OUT = "minecraft:cobblestone", FILL_IN = "minecraft:dirt";
/** 1.3.228 (B6 / GB9): the LOCAL ground of a column (its own surface block before the work): a beach is filled with sandstone
 *  under sand, a red-sand mesa with red sandstone, a gravel bank keeps gravel on top; everything else as before (dirt fill,
 *  cobblestone faces, grass on top). Read through the guarded blockAt (never throws) */
const LOCAL_GROUND = [[/red_sand/, { fill: "minecraft:red_sandstone", ring: "minecraft:red_sandstone", top: "minecraft:red_sand" }],
                      [/(^|:)sand$|pw_sand/, { fill: "minecraft:sandstone", ring: "minecraft:sandstone", top: "minecraft:sand" }],
                      [/gravel/, { fill: "minecraft:dirt", ring: "minecraft:cobblestone", top: "minecraft:gravel" }]];
const DEFAULT_GROUND = { fill: "minecraft:dirt", ring: "minecraft:cobblestone", top: "minecraft:grass_block" };
function localGround(dim, x, g, z) {
  if (g === undefined) return DEFAULT_GROUND;
  const b = blockAt(dim, x, g, z);
  const id = b ? b.typeId : "";
  for (const [re, pal] of LOCAL_GROUND) if (re.test(id)) return pal;
  return DEFAULT_GROUND;
}
const BRIDGE_DROP = 4, PIER = 4, CUT_RISE = 3;   // step 3: a street >= 4 above the ground becomes a bridge; >= 3 below it, a clad cutting

/** 1.3.224 (his 16:50 "we need to research how to properly terrace areas"; R5: a retaining wall is <= 3-4 high, taller
 *  retention is stepped in lifts with setbacks): from a built-up edge cell (x, z) whose top is `top`, the fill steps DOWN
 *  outward along dir — each further cell LIFT lower (a grass top, a cobblestone face of LIFT, dirt below) — until it meets
 *  the ground. Cells inside a plot or a street body are never touched. Returns the blocks set. */
function stepBerm(dim, x, z, dir, top, inPlot = () => false, body = null) {
  let n = 0;
  for (let k = 1; k <= Math.ceil(BUILD_UP_MAX / LIFT); k++) {
    const cx = x + dir[0] * k, cz = z + dir[1] * k;
    if (inPlot(cx, cz) || (body && body.has(`${cx},${cz}`))) break;
    const target = top - LIFT * k;
    const g = groundAt(dim, cx, cz);
    if (g === undefined || g >= target) break;                            // the ground meets the step: done
    for (let y = g + 1; y <= target; y++) {
      try {
        const blk = dim.getBlock({ x: cx, y, z: cz });
        if (!blk || !(blk.typeId === "minecraft:air" || isVeg(blk.typeId) || blk.typeId.includes("water"))) continue;
        blk.setType(y === target ? "minecraft:grass_block" : y > target - LIFT ? FILL_OUT : FILL_IN); n++;
      } catch { /* unloaded */ }
    }
  }
  return n;
}
/** the other plots' boxes (never stepped into) */
function inPlotOf(b) {
  const boxes = plotBoxes(load(), 0, null).filter(([x0, , z0]) => !(x0 === b.x && z0 === b.z));
  return (x, z) => boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
}
function terrace(dim, b, def) {
  const [fx, , fz] = footprint(def, b.rot);
  const slab = b.y + def.datum_y - 1;                        // the floor slab's y (feet -1)
  let filled = 0;
  // which margin side faces the street (never terraced: the street keeps its own profile; the stoop joins door and street)
  const frontSide = b.rot === 3 ? "south" : b.rot === 1 ? "north" : b.rot === 2 ? "east" : "west";
  for (let i = -1; i <= fx; i++) for (let j = -1; j <= fz; j++) {
    const x = b.x + i, z = b.z + j;
    if ((frontSide === "south" && j >= fz) || (frontSide === "north" && j < 0) || (frontSide === "east" && i >= fx) || (frontSide === "west" && i < 0)) continue;
    const g = groundAt(dim, x, z);
    if (g === undefined) continue;
    const outer = i < 0 || j < 0 || i >= fx || j >= fz;
    const ring = outer || i === 0 || j === 0 || i === fx - 1 || j === fz - 1;
    const top = outer ? slab : slab - 1;                     // the margin reaches the slab level; inside stops under the slab
    const lg = g < top ? localGround(dim, x, g, z) : DEFAULT_GROUND;   // B6 (GB9)
    for (let y = g + 1; y <= top; y++) {
      try {
        const blk = dim.getBlock({ x, y, z });
        if (!blk) continue;
        if (blk.typeId === "minecraft:air" || !isGround(blk.typeId)) { blk.setType(ring ? lg.ring : lg.fill); filled++; }
      } catch { /* unloaded */ }
    }
    // 1.3.224: a built-up margin steps DOWN outward (lifts of 3) instead of standing as one tall face
    if (outer && g < slab - LIFT) {
      const dir = i < 0 ? [-1, 0] : i >= fx ? [1, 0] : j < 0 ? [0, -1] : [0, 1];
      filled += stepBerm(dim, x, z, dir, slab, inPlotOf(b), null);
    }
    // the HILL side (step 2): where the ground around the house stands above its floor, the margin becomes a clad
    // retaining face — cobblestone from the slab up to the ground, so the house reads as cut into the slope
    if (outer && g >= slab + 2) {
      for (let y = slab + 1; y <= g; y++) {
        try { const blk = dim.getBlock({ x, y, z }); if (blk && isGround(blk.typeId) && blk.typeId !== "minecraft:water") { blk.setType(FILL_OUT); filled++; } } catch { /* unloaded */ }
      }
    }
  }
  return filled;
}

/** the FRONT YARD: the cells between the plot and the street body, levelled at the street's height (dirt, cobblestone
 *  on the two side edges, a path surface), cleared above; the stoop then climbs on it toward the door */
function yardPass(dim, b, def) {
  const y = b.yard || 0;
  if (!y) return 0;
  const g = streetHeightAtDoor(b, def);
  if (g === undefined) return 0;
  const [fx, , fz] = footprint(def, b.rot);
  const cells = [];
  for (let k = 1; k <= y; k++) {
    if (b.rot === 1) for (let i = 0; i < fx; i++) cells.push([b.x + i, b.z - k, i === 0 || i === fx - 1]);
    else if (b.rot === 3) for (let i = 0; i < fx; i++) cells.push([b.x + i, b.z + fz - 1 + k, i === 0 || i === fx - 1]);
    else if (b.rot === 0) for (let j = 0; j < fz; j++) cells.push([b.x - k, b.z + j, j === 0 || j === fz - 1]);
    else for (let j = 0; j < fz; j++) cells.push([b.x + fx - 1 + k, b.z + j, j === 0 || j === fz - 1]);
  }
  // each yard cell takes the street's height at its own row / column (the street steps along its length; the yard
  // follows it, so no drop opens between street and yard); the door's column keeps g for the stoop
  const sSt = load().settlements.find((x) => x.id === b.settlement);
  const body = sSt && sSt.profile ? LAND.streetBody(sSt.profile, sSt.axis || "x") : new Map();
  const dx = b.rot === 0 ? -1 : b.rot === 2 ? 1 : 0, dz = b.rot === 1 ? -1 : b.rot === 3 ? 1 : 0;
  const hereH = (x, z) => { for (let k = 0; k <= y + 1; k++) { const h = body.get(`${x + dx * k},${z + dz * k}`); if (h !== undefined) return h; } return g; };
  let n = 0;
  for (const [x, z, edge] of cells) {
    try {
      const gr = groundAt(dim, x, z);
      if (gr === undefined) continue;
      const gh = hereH(x, z);
      for (let yy = gr + 1; yy <= gh; yy++) dim.getBlock({ x, y: yy, z })?.setType(edge ? FILL_OUT : FILL_IN);
      for (let yy = gh + 1; yy <= Math.max(gr, gh) + 3; yy++) { const a = dim.getBlock({ x, y: yy, z }); if (a && a.typeId !== "minecraft:air" && a.typeId !== "minecraft:water") a.setType("minecraft:air"); }
      const top = dim.getBlock({ x, y: gh, z });
      if (top && top.typeId !== "minecraft:water") top.setType(edge ? FILL_OUT : "minecraft:grass_path");
      supportUnder(dim, x, gh, z);
      clearTreesOver(dim, x, z, Math.max(gr, gh) + 3);
      n++;
    } catch { /* unloaded */ }
  }
  return n;
}

function stoop(dim, b, def) {
  const front = doorFront(b, def);
  if (!front) return 0;
  const floorY = b.y + def.datum_y;                          // feet 0 (the air level inside the door)
  const g = streetHeightAtDoor(b, def);
  if (g === undefined) return 0;
  const rise = floorY - 1 - g;                               // steps needed between the street and the slab
  if (rise <= 0) return 0;
  // step outward from the door: step k (k = 0 nearest) sits at y = slab - k, one cell further from the door each time —
  // never past the yard (a plot without a yard, the flat village, may use the street's edge row)
  const [sx, , sz] = def.size;
  const door = def.door || [0, 0, Math.floor(sz / 2)];
  let n = 0;
  for (let k = 0; k < Math.min(rise, Math.max(1, b.yard || 0)); k++) {
    const [ox, oz] = rotXZ(-1 - k, door[2], sx, sz, b.rot);
    const x = b.x + ox, z = b.z + oz, y = floorY - 1 - k;
    try {
      const gk = Math.min(groundAt(dim, x, z) ?? g, g);        // never dig below the street's laid height
      for (let yy = gk + 1; yy <= y; yy++) dim.getBlock({ x, y: yy, z })?.setType(FILL_OUT);
      for (let yy = y + 1; yy <= y + 2; yy++) { const a = dim.getBlock({ x, y: yy, z }); if (a && !isGround(a.typeId)) a.setType("minecraft:air"); }
      n++;
    } catch { /* unloaded */ }
  }
  return n;
}

/** clear trees standing over the plot (anything tree-like above the box, up to 24 blocks). */
function clearOver(dim, b, def) {
  const [fx, sy, fz] = footprint(def, b.rot);
  for (let i = 0; i < fx; i++) for (let j = 0; j < fz; j++) for (let y = b.y + sy; y < b.y + sy + 24; y++) {
    let blk;
    try { blk = dim.getBlock({ x: b.x + i, y, z: b.z + j }); } catch { blk = undefined; }
    if (blk && CLEAR_OVER.some((s) => blk.typeId.includes(s))) { try { blk.setType("minecraft:air"); } catch { /* left */ } }
  }
}

/** the street in front of a village plot: grass path on the ground, plants above it cleared. */
function layStreet(dim, b) {
  if (!b.street) return;
  const [x0, x1, z0] = b.street;
  // the profile: one height per column x (median of the rows), then no step larger than one block (the high side is cut)
  const h = [];
  for (let x = x0; x <= x1; x++) {
    const gs = [];
    for (let z = z0; z < z0 + STREET_W; z++) { const g = groundAt(dim, x, z); if (g !== undefined) gs.push(g); }
    h.push(gs.length ? median(gs) : undefined);
  }
  for (let pass = 0; pass < 8; pass++) {
    let changed = false;
    for (let i = 1; i < h.length; i++) {
      if (h[i] === undefined || h[i - 1] === undefined) continue;
      if (h[i] > h[i - 1] + 1) { h[i] = h[i - 1] + 1; changed = true; }
      if (h[i - 1] > h[i] + 1) { h[i - 1] = h[i] + 1; changed = true; }
    }
    if (!changed) break;
  }
  for (let i = 0; i < h.length; i++) {
    const x = x0 + i, hy = h[i];
    if (hy === undefined) continue;
    const rise = i > 0 && h[i - 1] !== undefined && hy > h[i - 1];
    for (let z = z0; z < z0 + STREET_W; z++) {
      try {
        const g = groundAt(dim, x, z);
        if (g === undefined) continue;
        for (let y = g + 1; y <= hy; y++) dim.getBlock({ x, y, z })?.setType(FILL_IN);           // fill a low spot
        for (let y = hy + 1; y <= Math.max(g, hy) + 3; y++) {                                     // cut the high side + plants
          const up = dim.getBlock({ x, y, z });
          if (up && up.typeId !== "minecraft:air" && up.typeId !== "minecraft:water") up.setType("minecraft:air");
        }
        const top = dim.getBlock({ x, y: hy, z });
        if (top && top.typeId !== "minecraft:water") top.setType(rise ? FILL_OUT : "minecraft:grass_path");
      } catch { /* left */ }
    }
  }
}

// ------------------------------------------------------------------------------------------------ stages
function placeStage(b, k) {
  const def = BUILDINGS[b.family];
  try {
    const dim = world.getDimension(b.dim);
    const [fx, , fz] = footprint(def, b.rot);
    const yProbe = b.settled === false ? 64 : b.y + def.datum_y;
    let loaded = false;
    try {
      loaded = true;
      for (let cx = Math.floor(b.x / 16) * 16; loaded && cx <= b.x + fx - 1; cx += 16) for (let cz = Math.floor(b.z / 16) * 16; cz <= b.z + fz - 1; cz += 16) {
        if (!blockAt(dim, Math.max(cx, b.x), yProbe, Math.max(cz, b.z))) { loaded = false; break; }
      }
    } catch { loaded = false; }                                           // 1.3.221: every chunk of the footprint, not two corners
    if (!loaded) return false;                                           // beyond the loaded chunks: wait quietly (0.0.13: a warning every 2 s)
    if (b.settled === false && !settle(dim, b, def)) return false;       // chunk not loaded: wait
    if (k === 0 && b.street) { clearOver(dim, b, def); b.filled = (b.land && (b.land.kind === "stilts" || b.land.kind === "plateau")) ? 0 : terrace(dim, b, def); }   // a stilt house has posts, not a ring; 1.3.230 (PL): a plateau's ring is its job's
    if (k === 0 && b.palace) { b.filled = 0; try { system.runJob(palaceLandJob(dim, b, def)); } catch (e) { console.warn(`[CIV-CLOCK] palace land: ${e}`); } }   // 1.3.221: the palace block's land, spread over ticks (a 64 x 64 piece in one tick hangs the watchdog)
    const anim = b.animate && k > 0;
    const secs = anim ? Math.min(30, Math.max(8, Math.round((stageBillOf(b, k).blocks || 100) / 20))) : 0;
    if (k === 0 && b.kit) {   // 1004b: the plot's standing water goes BEFORE the stage is placed; the template's own water stays
      try { const kst0 = load().settlements.find((x) => x.id === b.settlement); const dn = plotDrain(dim, b, def, b.kit.H); if (dn && kst0) kst0.log.push(`day ${load().simDays.toFixed(0)}: ${dn} cells of water drained under #${b.id} ${short(b)} (sealed)`); }
      catch (e) { console.warn(`[CIV-CLOCK] plot drain #${b.id}: ${e}`); }
    }
    timed(`place #${b.id} ${def.stem} s${k}`, () => world.structureManager.place(`pw:stages/${def.stem}_s${k}`, dim, { x: b.x, y: b.y, z: b.z },
      anim ? { rotation: ROTS[b.rot], includeEntities: true, animationMode: StructureAnimationMode.Layers, animationSeconds: secs } : { rotation: ROTS[b.rot], includeEntities: true }));
    delete b.animate;
    try { b.cleared = (b.cleared || 0) + clearMobsIn(dim, b.x - 1, b.y, b.z - 1, b.x + fx, b.y + def.size[1], b.z + fz); } catch (e) { console.warn(`[CIV-CLOCK] mobs #${b.id}: ${e}`); }   // 1004b (his 17:59): nothing left inside a script-built structure
    const post = () => { const set = fixDirections(dim, b, def); if (set) b.turned = (b.turned || 0) + set; if (k === 2) turnLids(dim, b, def); };
    if (anim) system.runTimeout(() => { try { post(); } catch (e) { console.warn(`[CIV-CLOCK] post-place #${b.id}: ${e}`); } }, secs * 20 + 20);
    else post();
    if (k === 0 && b.street) { if (!b.planned) layStreet(dim, b); b.yardCells = yardPass(dim, b, def); b.steps = stoop(dim, b, def); }
    if (k === 0 && b.kit) { const kst = load().settlements.find((x) => x.id === b.settlement); if (kst) { kitPlotAccess(kst, b); try { kitLandPrep(dim, b, def, kst); } catch (e) { console.warn(`[CIV-CLOCK] land prep #${b.id}: ${e}`); } } }
    if (k === def.stages - 1 && b.settlement !== undefined && !b.villagers) moveIn(dim, b, def);
    if (k === def.stages - 1 && b.settlement !== undefined) { const sst = load().settlements.find((x) => x.id === b.settlement); if (sst) sweepBox(dim, sst, b.x - 10, b.z - 10, b.x + fx + 9, b.z + fz + 9, b.y + def.datum_y - 6, `#${b.id} ${short(b)}`); }   // 1004b: the air above a finished building holds no floating crown
    if (k === def.stages - 1 && !b.artDone) { try { const nh = GALLERY.hangBuilding(dim, b, def, Math.floor(load().simDays)); if (nh) { const sst2 = load().settlements.find((x) => x.id === b.settlement); if (sst2) sst2.log.push(`day ${load().simDays.toFixed(0)}: ${nh} picture(s) hung in #${b.id} ${short(b)}${b.artDone ? "" : " (more to come)"}`); } } catch (e) { console.warn(`[GALLERY] #${b.id}: ${e}`); } }   // 1.3.222: the gallery (resumable: the sweep finishes it)
    // v1.3.219: a furnished shop (and the inn, the town hall, the farms) gets its KEEPER at the station
    if (k === def.stages - 1 && b.settlement !== undefined && SHOP.KEEPS.includes(short(b)) && !b.closed) {
      const kst = load().settlements.find((x) => x.id === b.settlement);
      SHOP.hireKeeper(dim, b, def, kst);
    }
    return true;
  } catch (e) {
    console.warn(`[CIV-CLOCK] place ${def.stem}_s${k} failed: ${e}`);
    return false;
  }
}

/** the household moves in: spawned at the door, named, remembered on the plot (entity ids persist across sessions). */
function moveIn(dim, b, def) {
  const n = hhOf(b) || 0;
  b.villagers = [];
  if (!n) return;
  const front = doorFront(b, def);
  const y = b.y + def.datum_y;
  const s = load();
  const st = s.settlements.find((x) => x.id === b.settlement);
  const names = st ? censusMoveIn(s, st, b, n) : [];                  // D-C536: the census names the household
  for (let i = 0; i < n; i++) {
    try {
      const v = dim.spawnEntity(VILLAGER_ID, { x: front.x + 0.5, y, z: front.z + 0.5 });
      const name = names[i] || NAMES[(s.nextId * 7 + i * 13 + (st ? st.seed : 0)) % NAMES.length];
      v.nameTag = name;
      if (st && st.lastMoveIn && st.lastMoveIn[i] !== undefined) v.addTag(`civ:person:${st.lastMoveIn[i]}`);   // C2.1: the census record
      v.addTag("civ:villager");
      v.addTag(`civ:home:${b.id}`);
      if (st) v.addTag(`civ:settlement:${st.id}`);
      civOn(v);
      b.villagers.push(v.id);
    } catch (e) { console.warn(`[CIV-CLOCK] move-in at #${b.id} failed: ${e}`); }
  }
  if (st) { st.log.push(`day ${s.simDays.toFixed(0)}: ${n} moved into the ${short(b)} (#${b.id})`); delete st.lastMoveIn; }
}

// ---- THE CENSUS (D-C536): people as RECORDS per settlement (names, homes, jobs, kin, friends, mood, rumours). The hands
// (embodied villagers) take their names from it; the ledger's population stays the dwellings' count until C2 (hands vs census)
function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }
const FOUNDERS_CREW = 2;
const LEFTOVER_PER_DAY = 3;                                        // 0.0.25b
const MARKET = [5000, 7000];
const COUNTER = { bakery: ["minecraft:bread"], butcher: ["minecraft:cooked_beef", "minecraft:cooked_porkchop", "minecraft:cooked_mutton", "minecraft:cooked_chicken"] };
/** a shop's store chest (its template's first chest), in the world */
function chestOf(b) {
  if (b.store) return b.store;
  const def = BUILDINGS[b.family];
  if (!def || !def.chests || !def.chests.length) return null;
  const [lx, ly, lz] = def.chests[0];
  const [ox, oz] = rotXZ(lx, lz, def.size[0], def.size[2], b.rot);
  b.store = { x: b.x + ox, y: b.y + ly, z: b.z + oz };
  return b.store;
}
/** the counter's stock each real morning: the shop's share of the day's bread / meat goes into its chest (to 64) */
function stockCounters(s, st) {
  let dim; try { dim = world.getDimension(st.dim); } catch { return; }
  const L = st.ledger;
  for (const b of plotsOf(s, st)) {
    const kind = short(b);
    if (!COUNTER[kind] || b.stage < 4 || b.closed) continue;
    const dg = diagOf(st);                                                    // 1.3.228 (B2 / WE14): in memory
    const rec = (dg.counters = dg.counters && dg.counters.day === Math.floor(s.simDays) ? dg.counters : { day: Math.floor(s.simDays), shops: [] });
    const c = chestOf(b);
    if (!c) { rec.shops.push([b.id, kind, 0, "nochest"]); continue; }
    const good = kind === "bakery" ? "bread" : "meat";
    const have = L && L.stock ? Math.floor(L.stock[good] || 0) : 0;
    const n = Math.min(16, Math.max(4, have > 0 ? Math.ceil(households(s, st) / 2) : 0));                   // 0.0.25i: at least 4
    if (!have) { rec.shops.push([b.id, kind, 0, "nostock"]); continue; }
    let why = "ok";
    try {
      const blk = blockAt(dim, c.x, c.y, c.z);
      if (!blk) why = "unloaded";
      else { const inv = blk.getComponent("minecraft:inventory"); if (!inv || !inv.container) why = `noinv:${blk.typeId}`; else { const rest = inv.container.addItem(new ItemStack(COUNTER[kind][0], n)); if (rest) why = `full:${rest.amount}`; } }
    } catch (e) { why = `err:${String(e).slice(0, 40)}`; }
    rec.shops.push([b.id, kind, n, why, c.x, c.y, c.z]);
  }
}
/** the purchase: one item out of the shop's chest; the buyer learns; the market day is counted */
function buyAt(s, st, v, person, shopB) {
  const day = Math.floor(s.simDays);
  st.market = st.market && st.market.day === day ? st.market : { day, buys: 0, empty: 0, homes: 0 };
  if (person.home) { const hs = homesToday(st, day); if (!hs.has(person.home)) { hs.add(person.home); st.market.homes = hs.size; } }   // 1.3.228 (B2 / WE14): a count
  if (shopB.market) {                                                        // 1.3.228 (B7 / BF9): the stall sells from the town's stock
    const L = st.ledger;
    const good = L ? ["bread", "meat", "fish"].find((g) => ECON.sellable(L, g) > 0) : null;
    PEOPLE.learn(person, "market", good ? 1 : 0, day);
    if (good) { (L.sold = L.sold || {})[good] = (L.sold[good] || 0) + 1; st.market.buys++; st.market.stall = (st.market.stall || 0) + 1; try { v.dimension.playSound("random.pop", v.location, { volume: 0.6 }); } catch { /* left */ } }
    else st.market.empty++;
    return;
  }
  let got = false;
  try {
    const c = chestOf(shopB);
    const con = c ? blockAt(world.getDimension(st.dim), c.x, c.y, c.z)?.getComponent("minecraft:inventory")?.container : null;
    if (con) for (let i = 0; i < con.size && !got; i++) {
      const it = con.getItem(i);
      if (!it || !COUNTER[short(shopB)].includes(it.typeId)) continue;
      if (it.amount > 1) { it.amount -= 1; con.setItem(i, it); } else con.setItem(i, undefined);
      got = true;
    }
  } catch { got = false; }
  PEOPLE.learn(person, `shop:${shopB.id}`, got ? 1 : 0, day);
  if (got) { st.market.buys++; shopB.sold = (shopB.sold || 0) + 1; try { v.dimension.playSound("random.pop", v.location, { volume: 0.6 }); } catch { /* left */ } }
  else { st.market.empty++; if (!st.marketSaid || st.marketSaid !== day) { st.marketSaid = day; st.log.push(`day ${day}: ${person.name} found nothing at the ${short(shopB)}'s counter (#${shopB.id})`); } }
}
/** the shop a household's shopper goes to (trusted x near; its neighbourhood's first), or null */
function shopFor(s, st, v, person, homeB) {
  const shops = plotsOf(s, st).filter((b) => COUNTER[short(b)] && b.stage >= 4 && !b.closed);
  if (!shops.length) return null;
  const centre = homeB && homeB.kit ? homeB.kit.sid : null;
  const opts = shops.map((b) => { const d = Math.hypot(b.x - v.location.x, b.z - v.location.z); return { key: `shop:${b.id}`, value: (1 / (1 + d / 60)) * (b.centre !== undefined && b.centre === centre ? 1.5 : 1), b }; });
  // 1.3.228 (B7 / BF9): the MARKET STALL on the square is a counter too (the clerk sells from the town's stock): a shopper
  // whose usual counters came up empty learns to try it (PEOPLE.choose weighs the trust each option earned)
  if (st.mclerk && st.square) { const at = SHOP.marketStation(st); const d = Math.hypot(at.x - v.location.x, at.z - v.location.z); opts.push({ key: "market", value: 0.8 / (1 + d / 60), b: { id: -st.id, market: true, station: { x: at.x, y: at.y, z: at.z } } }); };
  const r = rng(((st.seed || 1) * 977 + Math.floor(s.simDays) * 31 + person.id) >>> 0);
  const o = PEOPLE.choose(person, opts, r);
  return o ? o.b : null;
}
/** F7: a civic work is no dwelling (a stand-in cottage serving as the latrine or the infirmary houses nobody) */
function hhOf(b) { return b && b.civic ? 0 : (HOUSEHOLD[short(b)] || 0); }
const CIVIC = {
  village3: [["midden", "post"]],
  town: [["latrine", "cottage_s"], ["cistern", "well"]],
  town3: [["bathhouse", "cottage_l"], ["lamplighter", "post"]],
  city: [["wellhouse", "well"], ["infirmary", "cottage_l"]],
  city3: [["hospital", "town_hall"], ["fountain", "well"]],
  metropolis: [["waterworks", "well"], ["ward", "cottage_l"]],
  metropolis3: [["ward", "cottage_l"]],
};
const CIVIC_BASE = ["well", "sewer"];
/** the works due at a settlement's tier (the base + every tier's up to the current one) and the ones standing */
function civicWorks(s, st) {
  const due = CIVIC_BASE.slice();
  const ti = TIERS.indexOf(st.tier);
  for (const [tier, works] of Object.entries(CIVIC)) if (TIERS.indexOf(tier) <= ti) for (const [w] of works) due.push(w);
  const plots = plotsOf(s, st);
  const P = st.people ? PEOPLE.alive(st.people) : [];
  const have = (w) => {
    if (w === "well") return plots.some((b) => short(b) === "well" && b.stage >= 4);
    if (w === "sewer") return (st.kitWater || 0) > 0;
    if (w === "midden" || w === "lamplighter") return P.some((p) => p.job === w);
    return plots.some((b) => b.civic === w && b.stage >= 4);
  };
  const standing = due.filter(have);
  return { due, standing, missing: due.filter((w) => !have(w)) };
}
function sanitationOf(s, st) { const w = civicWorks(s, st); return w.due.length ? w.standing.length / w.due.length : 1; }
function healthOf(s, st) {
  const P = st.people ? PEOPLE.alive(st.people) : [];
  const healers = P.filter((p) => p.job === "healer").length;
  const houses = plotsOf(s, st).filter((b) => ["infirmary", "hospital", "ward"].includes(b.civic) && b.stage >= 4).length;
  return Math.min(houses, healers);
}
const BUILD_TICKS = 40;                                   // C2.3: one block per 2 s per builder at the site
/** the labour sites of a settlement: buildings whose next stage the builders are working on */
function laborSites(s, st) { return plotsOf(s, st).filter((b) => b.labor && !b.closed); }
/** materials out of the stores for a bill: stone from the quarries' chests, logs from the lumberyards' (best effort, loaded
 *  chunks only; the ledger already paid). Returns the count taken. */
function takeFromStores(s, st, bill, siteId = null) {
  let took = 0;
  const want = { stone: (bill.mats && bill.mats.stone) || 0, timber: (bill.mats && bill.mats.timber) || 0 };
  let dim; try { dim = world.getDimension(st.dim); } catch { return 0; }
  for (const b of plotsOf(s, st)) {
    const kind = short(b);
    const key = kind === "quarry" ? "stone" : kind === "lumberyard" ? "timber" : null;
    if (!key || !b.store || want[key] <= 0) continue;
    try {
      const con = blockAt(dim, b.store.x, b.store.y, b.store.z)?.getComponent("minecraft:inventory")?.container;
      if (!con) continue;
      for (let i = 0; i < con.size && want[key] > 0; i++) {
        const it = con.getItem(i);
        if (!it) continue;
        const n = Math.min(it.amount, want[key]);
        if (n === it.amount) con.setItem(i, undefined); else { it.amount -= n; con.setItem(i, it); }
        want[key] -= n; took += n;
        // 1.3.228 (B8 / WE2): the haul a carter can carry (visible + a small speed-up only — the stage never waits for it)
        if (siteId !== null) { const q = (st.haul = st.haul || []); const last = q.find((h) => h.from === b.id && h.to === siteId && h.g === key); if (last) last.n += n; else q.push({ from: b.id, to: siteId, g: key, n, age: 0, pri: 1 }); if (q.length > HAUL_MAX) q.splice(0, q.length - HAUL_MAX); }
      }
    } catch { /* unloaded */ }
  }
  return took;
}
/** dwellings with room: capacity = HOUSEHOLD x DENSITY (tenements at the high tiers) minus the people living there.
 *  1.3.228 (B4 / BF7): each carries its door front (x, y, z: the census takes the NEAREST free place) and its beds (counted
 *  from the template; the base only with PEOPLE.PLACES.BEDS_BASE, off) */
function homeRoom(s, st) {
  const dens = DENSITY[TIER_CLASS(st.tier)] || 1, P = census(st), living = {};
  for (const p of PEOPLE.alive(P)) if (p.home) living[p.home] = (living[p.home] || 0) + 1;
  return plotsOf(s, st).filter((b) => (hhOf(b) || 0) > 0 && b.stage >= 4 && !b.closed)
    .map((b) => {
      const beds = bedsOfFamily(b.family);
      const cap = Math.round((PEOPLE.PLACES.BEDS_BASE && beds ? beds : (hhOf(b) || 0)) * dens);
      return { id: b.id, room: Math.max(0, cap - (living[b.id] || 0)), over: Math.max(0, (living[b.id] || 0) - cap), beds, ...placeOf(b) };
    });
}
// ------------------------------------------------------------------------------------------------ B4 (1.3.228): PLACES & SHIFTS
// BF7: every home and every post carries a place (its door front; a town post the square) so the census takes the nearest
// free one. BF5 / PE5: the shift of a person now (PEOPLE.shiftAt: template from the job, the id's offset, the week's days off,
// the walk home); its travel time is cached per person (memory) and re-made when the home or the job changes.
const bedsCache = new Map();                                              // family -> beds (from the template's directional blocks)
function bedsOfFamily(fam) { if (!bedsCache.has(fam)) bedsCache.set(fam, PEOPLE.bedsOf((BUILDINGS[fam] || {}).dir)); return bedsCache.get(fam); }
/** a building's place: its door front {x, y, z} ({} when the family is unknown) */
function placeOf(b) {
  const def = b && BUILDINGS[b.family];
  if (!def) return {};
  const fr = doorFront(b, def);
  return { x: fr.x + 0.5, y: b.y + def.datum_y, z: fr.z + 0.5 };
}
const squarePlace = (st) => (st.square ? { x: st.square.x + 6.5, y: st.square.y + 1, z: st.square.z + 6.5 } : {});
let bIdx = { tick: -1, n: -1, m: new Map() };
/** buildings by id (rebuilt once a tick when the list changed) */
function buildingById(s, id) {
  const t = system.currentTick;
  if (bIdx.list !== s.buildings || bIdx.n !== s.buildings.length || t - bIdx.tick > 100 || t < bIdx.tick) bIdx = { tick: t, n: s.buildings.length, list: s.buildings, m: new Map(s.buildings.map((b) => [b.id, b])) };
  return bIdx.m.get(id) || null;
}
let wdCount = null;   // 1.3.232 #3: the shift week counts its own days (world.getDay() stops turning after /time set)
function worldDay() { try { wdCount = PEOPLE.dayCount(wdCount, world.getDay(), world.getTimeOfDay()); return wdCount.n; } catch { return wdCount ? wdCount.n : 0; } }
/** the place of a person's work: the workplace's door front; a fisherman's spot; a town post the square */
function workPlaceOf(s, st, p) {
  if (p.job === null || p.job === undefined) return null;
  if (typeof p.job === "number") { const b = buildingById(s, p.job); return b ? placeOf(b) : null; }
  if (p.job === "fisher") { const sp = fishSpotOf(st, p); if (sp) return { x: sp.x + 0.5, y: sp.y, z: sp.z + 0.5 }; }
  return st.square ? squarePlace(st) : null;
}
const travelCache = new Map();                                            // "st:pid" -> { h, j, t }
/** PE5: ticks of a person's walk from work to home (0 = not known) */
function travelOf(s, st, p) {
  const k = `${st.id}:${p.id}`, c = travelCache.get(k);
  if (c && c.h === p.home && c.j === p.job) return c.t;
  const hb = p.home ? buildingById(s, p.home) : null;
  const t = hb ? PEOPLE.travelTicks(workPlaceOf(s, st, p), placeOf(hb)) : 0;
  travelCache.set(k, { h: p.home, j: p.job, t });
  if (travelCache.size > 8192) travelCache.clear();
  return t;
}
/** the workplace kind of a person (a building's short name, else the post id) */
function jobKindOf(s, p) { if (typeof p.job === "number") { const b = buildingById(s, p.job); return b ? short(b) : null; } return p.job || null; }
/** BF5: the shift options of a person (template inputs, the town's seed, the walk home) */
function shiftOpts(s, st, p, child = PEOPLE.stage(p, Math.floor(s.simDays)) === "child") {
  const kind = jobKindOf(s, p);
  return { seed: st.seed || 0, keeper: !!p.keeper, kind, child, travel: child ? 0 : travelOf(s, st, p),
           inn: kind === "inn" && !child ? innRotaOf(s, st, p.job) : undefined };   // 1.3.231 (INN24): the inn's rota
}
/** BF5: where person p's day stands now ({slot, tpl, off, home, ...}) */
function shiftNow(s, st, p, tod = world.getTimeOfDay(), day = worldDay(), child) { return PEOPLE.shiftAt(p, tod, day, shiftOpts(s, st, p, child)); }
/** PE5: is p's home more than COMMUTE.far from work? */
function homeFarOf(s, st, p) { const hb = p.home ? buildingById(s, p.home) : null; return !!hb && PEOPLE.homeFar(placeOf(hb), workPlaceOf(s, st, p)); }

// ------------------------------------------------------------------------------------------------ FISHERMEN (1.3.225, his 20:35)
// From village II a town looks for FISHING SPOTS: a standable shore cell beside water at least 2 deep (a pond, a river, the
// sea) within FISH_R of the square, at least 8 apart, never on a plot, a street or a road. Fishermen (one per spot and one
// more per 8 households, at most FISH_MAX) walk to their spot in work hours, stand facing the water and land a fish now
// and then (a splash and the line's sound); the day's catch feeds the town's FISH stock (the ledger's "fishery", paid
// a fisher's wage; on a skipped day the abstract rate stands in). They wear the vanilla fisherman's clothes (variant 2).
const FISH_R = 112, FISH_STEP = 4, FISH_SPOTS = 4, FISH_SCAN = 160, FISH_MAX = 6, FISH_FROM = 1;   // FISH_FROM: TIERS index (village2)
const FISH_CHANCE = 0.12;                                                  // a catch per schedule beat (100 ticks) at the spot: ~12 a work day
let fishCands = null;
function fishCandidates() {                                                // ring offsets, nearest first (built once)
  if (fishCands) return fishCands;
  const out = [];
  for (let dx = -FISH_R; dx <= FISH_R; dx += FISH_STEP) for (let dz = -FISH_R; dz <= FISH_R; dz += FISH_STEP) { const d = Math.hypot(dx, dz); if (d >= 12 && d <= FISH_R) out.push([dx, dz, d]); }
  out.sort((a, b) => a[2] - b[2]);
  return (fishCands = out);
}
/** the water surface of column (x, z) and the depth under it, or null (dry), or undefined (asleep)
 *  1.3.228 (B1 hygiene): the raw reads threw on a sleeping column (the leak path; a survey day was ~6,400 reads in one
 *  tick): the column is asked for first, then read through topAt / blockAt (one engine call a cell) */
function waterColumn(dim, x, z) {
  if (!dim.isChunkLoaded({ x, y: 64, z })) return undefined;
  const top = topAt(dim, x, z);                               // skips liquids: the bed (palace run 4)
  if (!top) return null;
  let y = top.location.y + 1, surf = null;
  for (; y < top.location.y + 40; y++) { const b = blockAt(dim, x, y, z, true); if (b && b.typeId === "minecraft:water") surf = y; else break; }
  return surf === null ? null : { surf, depth: surf - top.location.y };
}
// 1.3.228 (B1 hygiene, FIT-MATRIX BF1): at most FISH_CALL columns a call — the day's call reads the first FISH_CALL and owes
// the rest of its FISH_SCAN to the heartbeat's fishery slot (FISH_CALL a beat), so a survey day keeps its 160 columns but
// never reads them in one tick. The debt is memory only (a reload forgets it: that day reads fewer columns).
const FISH_CALL = 40;
const fishOwed = new Map();                                                // settlement id -> columns still owed today
const fishBusy = new Map();                                                // settlement id -> { day, busy(x, z) } (memory)
function fishBusyOf(s, st) {
  const day = Math.floor(s.simDays);
  const c = fishBusy.get(st.id);
  if (c && c.day === day) return c.busy;
  const boxes = plotBoxes(s, 1, null), body = kitBody(st);
  const roadCells = new Set(); for (const r of st.roads7 || []) for (const [x, z] of r.cells) for (let a = -KIT.ROAD_HALF; a <= KIT.ROAD_HALF; a++) for (let b = -KIT.ROAD_HALF; b <= KIT.ROAD_HALF; b++) roadCells.add(`${x + a},${z + b}`);
  const busy = (x, z) => body.has(`${x},${z}`) || roadCells.has(`${x},${z}`) || boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  fishBusy.set(st.id, { day, busy });
  return busy;
}
function fisheryDay(s, st) {
  fishOwed.set(st.id, FISH_SCAN);
  fisheryCall(s, st);
}
function fisheryCall(s, st) {
  const owe = fishOwed.get(st.id) || 0;
  if (owe <= 0) { fishOwed.delete(st.id); return; }
  const k = Math.min(FISH_CALL, owe);
  const n = surveyFishery(s, st, k);
  if (n < k || owe - k <= 0) fishOwed.delete(st.id); else fishOwed.set(st.id, owe - k);   // short of k: rested, spots full or the ring done
}
HB.register("fishery", { fn: () => {                                        // slot 5 of 20 (optional: shed under load)
  if (!fishOwed.size) return;
  const s = load();
  for (const id of [...fishOwed.keys()]) {
    const st = s.settlements.find((x) => x.id === id);
    if (!st) { fishOwed.delete(id); continue; }
    fisheryCall(s, st);
    save();                                                                // the cursor moved (marks dirty; the save slot writes)
    return;                                                                // one settlement a beat
  }
} });
/** one call of the survey (at most `cap` columns): spots found are kept in st.fishery.spots [{ x, y, z, wx, wz }]; returns the
 *  columns read (0 when the fishery rests or has its spots) */
function surveyFishery(s, st, cap = FISH_CALL) {
  if (!st.square || TIERS.indexOf(st.tier) < FISH_FROM) return 0;
  const fy = (st.fishery = st.fishery || { spots: [], cursor: 0, rest: 0 });
  if (fy.spots.length >= FISH_SPOTS || s.simDays < (fy.rest || 0)) return 0;
  const dim = world.getDimension(st.dim);
  const cx = st.square.x + 6, cz = st.square.z + 6;
  const cands = fishCandidates();
  // 1.3.228: the occupancy is built when a shore is first tested, once per settlement and day (the day's survey is now 4
  // calls; the road cells alone are ~49 keys per road cell)
  const busy = (x, z) => fishBusyOf(s, st)(x, z);
  let n = 0;
  while (fy.cursor < cands.length && n < cap && fy.spots.length < FISH_SPOTS) {
    const [dx, dz] = cands[fy.cursor++]; n++;
    const wx = cx + dx, wz = cz + dz;
    let w;
    try { w = waterColumn(dim, wx, wz); } catch { w = null; }
    if (w === undefined) { fy.asleep = (fy.asleep || 0) + 1; continue; }        // a sleeping column (was: the thrown read)
    if (!w || w.depth < 2) continue;
    if (fy.spots.some((sp) => Math.hypot(sp.wx - wx, sp.wz - wz) < 8)) continue;
    // the shore: walk from the water toward the square up to 6 cells; the first dry column at the surface level (+-1) whose
    // two cells above are air is the stand
    const len = Math.hypot(dx, dz), ux = -dx / len, uz = -dz / len;
    for (let k = 1; k <= 6; k++) {
      const sx = Math.round(wx + ux * k), sz = Math.round(wz + uz * k);
      let top;
      try { top = topAt(dim, sx, sz); } catch { break; }
      if (!top) break;
      const above = blockAt(dim, sx, top.location.y + 1, sz, true), above2 = blockAt(dim, sx, top.location.y + 2, sz, true);
      if (!above || !above2) break;
      if (above.typeId === "minecraft:water") continue;                    // still water: go on toward the land
      if (Math.abs(top.location.y - w.surf) > 1 || top.typeId.includes("leaves") || top.typeId.includes("log")) break;
      if (above.typeId !== "minecraft:air" || above2.typeId !== "minecraft:air" || busy(sx, sz)) break;
      // the water cell he fishes: the last wet cell before the stand
      const fx = Math.round(wx + ux * (k - 1)), fz = Math.round(wz + uz * (k - 1));
      fy.spots.push({ x: sx, y: top.location.y + 1, z: sz, wx: fx, wz: fz, surf: w.surf });
      st.log.push(`day ${s.simDays.toFixed(0)}: a fishing spot on the shore at ${sx} ${top.location.y + 1} ${sz} (water ${w.depth} deep)`);
      break;
    }
  }
  if (fy.cursor >= cands.length) { fy.cursor = 0; fy.rest = s.simDays + (fy.spots.length ? 30 : 10); return 0; }   // looked everywhere: rest, then look again (the land may have woken)
  return n;
}
function fishersOf(st) { return st.people ? PEOPLE.alive(st.people).filter((p) => p.job === "fisher") : []; }
/** the fishery as a workshop for the ledger (one station per fisherman) */
function fisheryShop(st) {
  const n = fishersOf(st).length;
  return n && st.fishery && st.fishery.spots.length ? [{ id: `fishery:${st.id}`, kind: "fishery", stations: n, closed: false }] : [];
}
/** a fisherman's spot (spread over the spots by person id) */
function fishSpotOf(st, person) {
  const sp = st.fishery && st.fishery.spots;
  return sp && sp.length ? sp[person.id % sp.length] : null;
}
/** at his spot in work hours: now and then a fish (the catch counts toward today's real production) */
function fishAt(st, v, spot) {
  try {
    const want = Math.atan2(-(spot.wx + 0.5 - v.location.x), spot.wz + 0.5 - v.location.z) * 180 / Math.PI;
    v.setRotation({ x: 0, y: want });
  } catch { /* left */ }
  if (Math.random() >= FISH_CHANCE) return;
  st.fishToday = (st.fishToday || 0) + 1;
  st.fishCaught = (st.fishCaught || 0) + 1;
  try {
    const loc = { x: spot.wx + 0.5, y: (spot.surf ?? spot.y) + 0.9, z: spot.wz + 0.5 };
    v.dimension.spawnParticle("minecraft:water_splash_particle_manual", loc);
    v.dimension.playSound("random.splash", loc, { volume: 0.5, pitch: 1.3 });
  } catch { /* left */ }
}

/** the posts: every open shop's stations minus the people already at them. 1.3.228 (B4 / BF7): each with its place (a
 *  workplace's door front; the town's posts the square) */
function jobPosts(s, st) {
  const sq = squarePlace(st);
  return jobPostsBody(s, st).map((j) => ({ ...j, ...(typeof j.id === "number" ? placeOf(buildingById(s, j.id)) : sq) }));
}
function jobPostsBody(s, st) {
  const P = census(st), filled = {};
  for (const p of PEOPLE.alive(P)) if (p.job) filled[p.job] = (filled[p.job] || 0) + 1;
  // C2.3: the builders' crew comes first (2, +2 per site at work, at most a third of the people)
  // 1.3.230 (HD): a restoration at work (st.restore, paid, days left) is builders' work too (one more post each)
  const restoring = (st.restore || []).filter((e) => e.l !== undefined).length;
  const crew = Math.min(Math.ceil(PEOPLE.alive(P).length / 3), 2 + 2 * laborSites(s, st).length + restoring);
  const posts = [{ id: "builders", kind: "builder", vacancies: Math.max(0, crew - (filled.builders || 0)) }];
  // B4: the SURVEYOR (an office) while boundary stones wait to be carried out
  if (st.border && st.border.moves.some((m) => !m.done && m.blocked === null)) posts.push({ id: "surveyor", kind: "surveyor", vacancies: (filled.surveyor || 0) ? 0 : 1 });
  // 1.3.228 (B8 / WE2): CARTERS from town I — min(4, ceil(labour sites / 3)) — carry the stores' stone and timber to the sites
  if (TIER_CLASS(st.tier) >= 1) { const want = Math.min(CARTERS_MAX, Math.ceil(laborSites(s, st).length / 3)); posts.push({ id: "carter", kind: "carter", vacancies: Math.max(0, want - (filled.carter || 0)) }); }
  // F4: the SEWER KEEPER (from town I, once the streets have manholes): one post, one key
  if (TIER_CLASS(st.tier) >= 1 && (st.manholesLaid || 0) > 0) posts.push({ id: "sewer_keeper", kind: "sewer_keeper", vacancies: (filled.sewer_keeper || 0) ? 0 : 1 });
  // F5: the WATCH (village III: 1 constable, town I: 2 ... city I: 6, more per tier)
  for (const [tier, works] of Object.entries(CIVIC)) if (TIERS.indexOf(tier) <= TIERS.indexOf(st.tier)) for (const [w, fam] of works) if (fam === "post") posts.push({ id: w, kind: w, vacancies: (filled[w] || 0) ? 0 : 1 });
  const infirm = plotsOf(s, st).filter((b) => ["infirmary", "hospital", "ward"].includes(b.civic) && b.stage >= 4).length;
  if (infirm) posts.push({ id: "healer", kind: "healer", vacancies: Math.max(0, infirm - (filled.healer || 0)) });
  // 1.3.225: FISHERMEN — one per shore spot found, one more per 8 households, at most FISH_MAX
  if (st.fishery && st.fishery.spots.length) { const want = Math.min(FISH_MAX, Math.max(st.fishery.spots.length, Math.floor(households(s, st) / 8))); posts.push({ id: "fisher", kind: "fisher", vacancies: Math.max(0, want - (filled.fisher || 0)) }); }
  const nWatch = WATCH.WATCH_POSTS[st.tier] || 0;
  if (nWatch) posts.push({ id: "watch", kind: "watch", vacancies: Math.max(0, nWatch - (filled.watch || 0)) });
  return posts.concat(shopsOf(s, st).filter((sh) => !sh.closed).map((sh) => ({ id: sh.id, kind: sh.kind, vacancies: Math.max(0, sh.stations - (filled[sh.id] || 0)) })));
}
/** a household moves in: n people recorded at the dwelling (their names go on the villagers at the door) */
function censusMoveIn(s, st, b, n) {
  const P = census(st), names = [];
  for (let i = 0; i < n; i++) {
    const hsh = (b.id * 7 + i * 11 + (st.seed || 0)) >>> 0;
    const p = PEOPLE.newPerson(P, Math.floor(s.simDays), { home: b.id, seed: b.id * 31 + i * 7 + (st.seed || 0), age: i < 2 ? 20 + (hsh % 40) : hsh % 15, sex: i === 0 ? "m" : i === 1 ? "f" : undefined, parents: [] });
    names.push(p.name); (st.lastMoveIn = st.lastMoveIn || []).push(p.id);
  }
  return names;
}
/** one day of the census: contacts, weddings, births, deaths, inheritance, mood, migration, rumours, threads */
const EMBODY_CAP = 48, BODY_POSTS = ["watch", "sewer_keeper", "surveyor", "builders", "fisher", "carter"], SHOPPER_RESERVE = 12;   // B8: carters walk
const HAUL_MAX = 12, CARTERS_MAX = 4, HAUL_BONUS = 200;                  // 1.3.228 (B8 / WE2): the haul queue, posts, labour per load
function bodySync(s, st) {
  let dim, vs;
  try { dim = world.getDimension(st.dim); vs = dim.getEntities({ tags: [`civ:settlement:${st.id}`], type: VILLAGER_ID }); } catch { return; }
  const P = census(st), byPid = new Map();
  for (const v of vs) { const tag = v.getTags().find((x) => x.startsWith("civ:person:")); if (tag) byPid.set(Number(tag.slice(11)), v); }
  let gone = 0, made = 0;
  for (const [pid, v] of [...byPid]) {
    const p = PEOPLE.byId(P, pid);
    if (p && !p.alive) { try { WALK.cancel(v); v.remove(); gone++; } catch { /* left */ } byPid.delete(pid); continue; }
    if (p && p.home) { const tag = v.getTags().find((x) => x.startsWith("civ:home:")); if (tag !== `civ:home:${p.home}`) { try { if (tag) v.removeTag(tag); v.addTag(`civ:home:${p.home}`); } catch { /* left */ } } }
  }
  // 0.0.25: each household's SHOPPER gets a body too (its first grown member with no post and no shop), when the
  // household has no such member walking yet — the posts first (the loop below), then the shoppers
  const day0 = Math.floor(s.simDays);
  const shopperOk = (q) => !q.keeper && q.job !== "watch" && q.job !== "builders" && PEOPLE.stage(q, day0) !== "child";
  const homesWithShopper = new Set(PEOPLE.alive(P).filter((q) => q.home && byPid.has(q.id) && shopperOk(q)).map((q) => q.home));
  // 1.3.231 (INN24): the inn's staff walk too (the rota's night keeper and serving staff are posts with a body)
  const innIds = new Set(plotsOf(s, st).filter((b) => short(b) === "inn" && b.stage >= 4 && !b.closed).map((b) => b.id));
  const isPost = (job) => BODY_POSTS.includes(job) || innIds.has(job);
  const want = PEOPLE.alive(P).filter((p) => !byPid.has(p.id) && !p.keeper && (isPost(p.job) || (p.home && shopperOk(p) && !homesWithShopper.has(p.home))))
    .sort((a2, b2) => (isPost(a2.job) ? 0 : 1) - (isPost(b2.job) ? 0 : 1) || a2.id - b2.id);
  // a post holder without a body while the cap is full: a shopper's body (not walking) is released for it
  const postless = want.filter((p) => isPost(p.job)).length;
  if (postless && byPid.size >= EMBODY_CAP) {
    let freed = 0;
    for (const [pid, v] of [...byPid]) {
      if (freed >= postless) break;
      if (!v.hasTag("civ:shopper") || WALK.walking(v)) continue;
      const q = PEOPLE.byId(P, pid);
      if (q && isPost(q.job)) continue;
      try { v.remove(); byPid.delete(pid); freed++; gone++; } catch { /* left */ }
    }
  }
  for (const p of want) {
    if (made >= 3 || byPid.size >= EMBODY_CAP) break;
    if (byPid.has(p.id) || p.keeper) continue;
    if (!isPost(p.job)) { if (byPid.size >= EMBODY_CAP - SHOPPER_RESERVE || homesWithShopper.has(p.home)) continue; homesWithShopper.add(p.home); }
    const home = p.home ? s.buildings.find((b) => b.id === p.home) : null;
    const def = home && BUILDINGS[home.family];
    let spot = null;
    if (def) { const fr = doorFront(home, def); spot = { x: fr.x + 0.5, y: home.y + def.datum_y, z: fr.z + 0.5 }; }
    else if (st.square) spot = squareSlot(st, p.id);                      // 1.3.224: its own cell on the square's ring (6.5 was inside the well)
    if (!spot) continue;
    try {
      const v = dim.spawnEntity(VILLAGER_ID, spot);
      v.nameTag = p.name; v.addTag(`civ:person:${p.id}`); v.addTag("civ:villager"); v.addTag(`civ:settlement:${st.id}`); if (p.home) v.addTag(`civ:home:${p.home}`);
      if (!isPost(p.job)) v.addTag("civ:shopper");
      civOn(v);
      byPid.set(p.id, v); made++;
    } catch { /* unloaded: tomorrow */ }
  }
  st.bodies = { n: byPid.size, made: ((st.bodies && st.bodies.made) || 0) + made, gone: ((st.bodies && st.bodies.gone) || 0) + gone };
}
// 1.3.228 (B3 / PE4): the house level of every building a person may call home (dwellings by kind; a keeper's shop = rooms
// over the shop; PEOPLE.homeLevel holds the table)
function homeLevels(s, st) {
  const out = new Map();
  for (const b of plotsOf(s, st)) { try { out.set(b.id, PEOPLE.homeLevel(short(b))); } catch { /* an unknown family */ } }
  return out;
}
// 1.3.228 (B3 / PE7): real work acts per person today (a dug block, a chop) — memory only, read and cleared by the census day
const ACTS = new Map();                                                     // settlement id -> Map(pid -> acts)
function noteAct(v, st) {
  try {
    const tag = v.getTags().find((t) => t.startsWith("civ:person:"));
    if (!tag) return;
    const pid = Number(tag.slice(11));
    let m = ACTS.get(st.id); if (!m) ACTS.set(st.id, (m = new Map()));
    m.set(pid, (m.get(pid) || 0) + 1);
  } catch { /* a gone body */ }
}
// 1.3.228 (B4 / BF7): MOVING TOWN — the census's own migration (a departure here, an arrival there). The other towns' free
// rooms and posts are read once a census day per town (memory) and booked as households move in.
const placesToday = new Map();                                            // settlement id -> { day, homes, jobs }
function placesOf(s, st, day) {
  let c = placesToday.get(st.id);
  if (!c || c.day !== day) placesToday.set(st.id, (c = { day, homes: homeRoom(s, st), jobs: jobPosts(s, st) }));
  return c;
}
/** the nearest other town (squares' distance) with a home holding need.people and, for a job-seeker, an open post */
function moveTarget(s, st, need, day) {
  let best = null, bd = Infinity;
  for (const o of s.settlements) {
    if (o === st || o.id === st.id || !o.kit || !o.square || o.phase !== "built" || o.dim !== st.dim) continue;
    const c = placesOf(s, o, day);
    if (!c.homes.some((h) => (h.room || 0) >= need.people)) continue;
    if (need.job && !c.jobs.some((j) => (j.vacancies || 0) > 0 || j.vacant)) continue;
    const d = st.square ? Math.hypot(o.square.x - st.square.x, o.square.z - st.square.z) : 0;
    if (d < bd) { bd = d; best = o; }
  }
  return best ? { id: best.id, name: best.name } : null;
}
/** the movers arrive: the room nearest an open post (it holds the whole household), the census records, both towns' logs */
function moveTownIn(s, st, m, day, events) {
  const o = s.settlements.find((x) => x.id === m.to);
  if (!o) return;
  const c = placesOf(s, o, day);
  const open = c.jobs.filter((j) => ((j.vacancies || 0) > 0 || j.vacant) && Number.isFinite(j.x));
  let h = null, hd = Infinity;
  for (const x of c.homes) { if ((x.room || 0) < m.people.length) continue; const d = open.length ? Math.min(...open.map((j) => Math.hypot(x.x - j.x, x.z - j.z))) : 0; if (h === null || d < hd) { h = x; hd = d; } }
  if (!h) return;
  h.room -= m.people.length;
  try { PEOPLE.queueRestore((o.restore = o.restore || []), [h.id]); } catch { /* left */ }   // 1.3.230 (HD): a move in queues a restoration
  if (m.why === "job") { const j = c.jobs.find((x) => (x.vacancies || 0) > 0 || x.vacant); if (j) { if (j.vacancies > 0) j.vacancies--; else j.vacant = false; } }   // booked for the day
  const got = PEOPLE.adopt(census(o), m.people, day, h.id);
  const text = `${got.map((q) => q.name).join(", ")} came from ${st.name} (no ${m.why === "home" ? "home" : "work"} there) and took a room in #${h.id}`;
  o.log.push(`day ${day}: ${text}`);
  events.push(`§a${o.name}: ${text}`);
  console.warn(`[CIV-MOVE] ${JSON.stringify({ from: st.id, to: o.id, why: m.why, n: got.length, home: h.id, day })}`);
}
/** 1.3.230 (HD): a person's daily wage (pennies) for what a household affords: the workplace's trade wage (ECON.WAGE via
 *  STATION_WAGE; a post its own; the builders a builder's), a master at least the master's wage; no job 0 */
function wageOfPerson(s, p) {
  if (p.job === null || p.job === undefined) return 0;
  const k = jobKindOf(s, p);
  const trade = ECON.STATION_WAGE[k] || (k === "builders" ? "builder" : k);
  const w = ECON.WAGE[trade] ?? PEOPLE.HOUSING.wage;
  return PEOPLE.rankOf(p, p.trade || "work") === "master" ? Math.max(w, ECON.WAGE.master) : w;
}
function censusDay(s, st, events) {
  const P = census(st), L = st.ledger;
  const fed = L ? (L.prosperity.slice(-1)[0] ?? 1) : 1, paid = !L || !(L.arrears > 0);
  st.sanitation = Math.round(sanitationOf(s, st) * 100) / 100;
  // 1.3.228 (B3): the town's food in days of need and its variety (PE4 / PE6, town-wide: no household larder), house levels,
  // the day's real work acts
  const pop = population(s, st), stock = (L && L.stock) || {};
  const foodDays = PEOPLE.foodDaysOf(stock, pop), diet = L ? PEOPLE.dietVariety(stock, pop) : undefined;
  const acts = ACTS.get(st.id) || null; ACTS.delete(st.id);
  const day = Math.floor(s.simDays);
  // 1.3.228 (B4): BF5 a day off carries no fatigue (the world's day); BF7 a household with no home / no work and none free
  // here moves to the nearest other town with room (moveTarget)
  const wday = worldDay();
  const r = PEOPLE.dayStep(P, { day, fed, paid, homes: homeRoom(s, st), jobs: jobPosts(s, st), seed: st.seed || 1, name: st.name, events: [], sanitation: st.sanitation, health: healthOf(s, st),
                                levels: homeLevels(s, st), foodDays: Number.isFinite(foodDays) ? foodDays : 99, diet, acts,
                                restOf: (p) => PEOPLE.dayOff(p, wday, { seed: st.seed || 0, keeper: !!p.keeper, kind: jobKindOf(s, p), child: PEOPLE.stage(p, day) === "child" }),
                                elsewhere: (need) => moveTarget(s, st, need, day),
                                siteWaits: (() => { try { return !!siteWaitGood(s, st); } catch { return false; } })(),   // B5 (BF11): a petition's site need
                                taxMood: L ? (ECON.TAX_MOOD[L.tax || "normal"] ?? 1) : 1,                                 // B7 (WE11): the tax dial's mood
                                watchPaid: L ? L.watchPaid !== false : true,                                              // B10 (WP1): the posts' pay
                                wageOf: (p) => wageOfPerson(s, p) });                                                     // 1.3.230 (HD): what a household affords
  for (const m of r.movers || []) { try { moveTownIn(s, st, m, day, events); } catch (e) { console.warn(`[CIV-CLOCK] move to #${m.to}: ${e}`); } }
  // 1.3.230 (HD): the day's house DEEDS settle with the ledger (a sale: treasury -> purse; a purchase: purse -> treasury;
  // each capped at what the payer holds) and every home moved out of / into is queued for RESTORATION (restoreDaily)
  try {
    if (r.deeds && r.deeds.length) {
      PEOPLE.settleDeeds(L, r.deeds);
      for (const d of r.deeds) {
        const hb = buildingById(s, d.home), what = hb ? short(hb).replace(/_/g, " ") : "house";
        st.log.push(`day ${day}: ${d.kind === "sell" ? "the town bought back" : "a household bought"} the ${what} #${d.home} for ${(d.paid / ECON.COIN).toFixed(1)} coins${d.paid < d.price ? ` (of ${(d.price / ECON.COIN).toFixed(1)}: the ${d.kind === "sell" ? "treasury" : "purse"} was short)` : ""}`);
      }
      const dg = diagOf(st); dg.deeds = { day, sold: r.deeds.filter((d) => d.kind === "sell").length, bought: r.deeds.filter((d) => d.kind === "buy").length, paid: r.deeds.reduce((a, d) => a + (d.kind === "sell" ? -d.paid : d.paid), 0) };
    }
    if (r.restore && r.restore.length) PEOPLE.queueRestore((st.restore = st.restore || []), r.restore);
    if (st.restore && !st.restore.length) delete st.restore;
  } catch (e) { console.warn(`[CIV-CLOCK] houses: ${e}`); }
  if ((r.movers && r.movers.length) || r.far || r.farMoved) { const d = diagOf(st); d.moves = { day, out: (r.movers || []).reduce((n, m) => n + m.ids.length, 0), far: r.far || 0, farMoved: r.farMoved || 0 }; }
  for (const e of r.events) {
    st.log.push(`day ${s.simDays.toFixed(0)}: ${e.text}`);
    if (["wedding", "birth", "death", "arrival", "inherit", "first", "rank", "sold", "line"].includes(e.kind)) events.push(`§d${st.name}: ${e.text}`);   // 1.3.230 (HD): + sold, line
    if (["first", "rank"].includes(e.kind)) annal(st, s.simDays, e.text);       // B10 (WP7)
  }
  // B11 (WP5 / WP9 / WP10): the wedding day (a festival), the festival's mood, the player's standing, yesterday's talk counters
  if (r.events.some((e) => e.kind === "wedding")) st.wedDay = day;
  try {
    const fest = GUEST.festivalNow(s, st);
    if (fest) { for (const p of PEOPLE.alive(P)) p.mood = Math.min(100, (p.mood ?? 50) + PLAYER.FEST.mood); r.meanMood = Math.min(100, r.meanMood + PLAYER.FEST.mood); }
    for (const p of PEOPLE.alive(P)) PLAYER.pruneTalk(p, day);
    st.standing = PLAYER.standingOf(P.list);
  } catch (e) { console.warn(`[CIV-CLOCK] player day: ${e}`); }
  st.mood = Math.round(r.meanMood);
  // B10 (his 12:20 "measure the crime factors; crime stays OFF"): a daily [CIV-CRIME] line + the diag
  if (r.crime) { try { diagOf(st).crime = { day, ...r.crime }; console.warn(`[CIV-CRIME] ${JSON.stringify({ st: st.id, day, atRisk: r.crime.atRisk, max: r.crime.max, parts: r.crime.parts, enabled: PEOPLE.CRIME.enabled })}`); } catch {} }
  // B3 gate signals (memory, never saved): the mood-tier histogram, births in the last 10 days, the needs pressure; a
  // [CIV-MOOD] line every 10 census days and on the first day after a load
  try {
    const al = PEOPLE.alive(P);
    const births10 = al.filter((p) => p.parents && p.parents.length && day - p.born < 10).length;
    const knows = al.reduce((a, p) => a + (p.knows ? p.knows.length : 0), 0);
    const dg = diagOf(st);
    dg.mood = { day, n: al.length, mean: st.mood, tiers: PEOPLE.moodTiers(P), births10, knows, fed, foodDays: Math.round(Math.min(99, foodDays) * 10) / 10, diet: diet ?? null,
                hungerW: r.hungerW, need: P.need || null, fullness: r.fullness, parts: r.parts };
    if (day % 10 === 0 || !dg.moodSaid) { dg.moodSaid = true; console.warn(`[CIV-MOOD] ${JSON.stringify({ st: st.id, name: st.name, tier: st.tier, ...dg.mood })}`); }
  } catch (e) { console.warn(`[CIV-CLOCK] mood line: ${e}`); }
  try { bodySync(s, st); } catch (e) { console.warn(`[CIV-CLOCK] bodies: ${e}`); }
  // F4: the key register follows the posts (a new holder gets the key; a gone one's key goes back to the strongbox)
  try { KEYS.reconcile(st, P.list, Math.floor(s.simDays), (text) => { st.log.push(`day ${s.simDays.toFixed(0)}: ${text}`); events.push(`§6${st.name}: ${text}`); }); } catch (e) { console.warn(`[CIV-CLOCK] keys: ${e}`); }
}
const MOOD_GATE = 45;                                   // D-C536: an unhappy town does not rise a tier
function moodOk(st) { return !st.people || !PEOPLE.alive(st.people).length || (st.mood ?? 55) >= MOOD_GATE; }
function population(s, st) {
  const dens = DENSITY[TIER_CLASS(st.tier)] || 1;
  return plotsOf(s, st).reduce((n, b) => n + Math.round((hhOf(b) || 0) * (b.closed ? 0 : dens)), 0);
}
/** REPRESENTATION here: the partners with a stand or a branch on our square (rung >= 2), with their tiers */
function representation(s, st) {
  const partners = Object.entries(st.inbound || {}).filter(([, r]) => r.rung >= 2).map(([id]) => s.settlements.find((x) => x.id === Number(id))).filter(Boolean);
  return { n: partners.length, cities: partners.filter((p) => TIER_CLASS(p.tier) >= 2).length, metropolises: partners.filter((p) => TIER_CLASS(p.tier) >= 3).length, names: partners.map((p) => p.name) };
}
function representationOk(s, st, next) {
  const req = REP_REQ[next];
  if (!req) return true;
  const r = representation(s, st);
  return r.n >= req[0] && r.cities >= req[1] && r.metropolises >= req[2];
}
function households(s, st) { return plotsOf(s, st).filter((b) => (hhOf(b) || 0) > 0 && !b.closed).length; }

/** one household leaves a declining settlement (the newest furnished dwelling with people). */
function leave(s, st, events) {
  const homes = plotsOf(s, st).filter((b) => b.villagers && b.villagers.length).reverse();
  if (!homes.length) return;
  const b = homes[0];
  const dim = world.getDimension(b.dim);
  let gone = 0;
  for (const id of b.villagers) { try { const e = world.getEntity(id); if (e) { e.remove(); gone++; } } catch { /* already gone */ } }
  b.villagers = [];
  st.log.push(`day ${s.simDays.toFixed(0)}: the ${short(b)} household left (${gone})`);
  events.push(`§c${st.name}: a household left the ${short(b)}`);
}

const LAG_SLICES = 1;                         // 1.3.224: ONE day per call (3 per call + a lag slice in the same tick came to ~2 s on his device)
/** advance the village by `days`: whole-day slices (the budget, wages and hiring are daily), at most maxSlices now, the
 *  rest carried in s.lag and worked off on the kit beat (one slice per beat) */
const SLOW_MS = 150;
function timed(name, fn) { const t0 = Date.now(); try { return fn(); } finally { const ms = Date.now() - t0; if (ms > SLOW_MS) console.warn(`[CIV-CLOCK] slow: ${name} took ${ms} ms`); } }
// 1.3.228 (gate 228-1: a carried day took 955 ms = economy 369 + census 189 + flood watch 173 + the rest in ONE tick): a
// day's world chores (sweep, canopy, flood watch, census, cores, border, manholes, trade names) are a TAIL run on the next
// beats within DAY_TAIL_MS each; the next day does not start until yesterday's tail is done (same order as before)
const DAY_TAIL_MS = 60;
const dayTail = [];                 // [state, name, fn]
let tailEvents = [];
function deferDay(s, name, fn) { dayTail.push([s, name, fn]); }
function runDayTail(budgetMs = DAY_TAIL_MS) {
  const t0 = Date.now();
  while (dayTail.length && Date.now() - t0 < budgetMs) {
    const [s0, name, fn] = dayTail.shift();
    if (load() !== s0) continue;                                    // a reload / restore since: yesterday's state is gone
    try { timed(name, fn); } catch (e) { console.warn(`[CIV-CLOCK] ${name}: ${e}`); }
  }
  return dayTail.length;
}
function advance(days, maxSlices = LAG_SLICES) {
  const s = load();
  let left = (s.lag || 0) + Math.max(0, days || 0);
  let events = tailEvents.splice(0);
  if (runDayTail()) { s.lag = left > 1e-9 ? left : 0; flushPending(); save(); return events; }   // yesterday is not finished yet
  for (let n = 0; left > 1e-9 && n < maxSlices; n++) {
    const d = Math.min(1, left); events = events.concat(advanceOnce(d)); left -= d;
    if (dayTail.length) { if (n + 1 < maxSlices) runDayTail(); if (dayTail.length) { n = maxSlices; } }   // one day at a time while a tail waits
  }
  s.lag = left > 1e-9 ? left : 0;
  flushPending();
  save();
  return events;
}
function advanceOnce(days) {
  const s = load();
  if (days <= 0) return [];
  s.accelNow = (s.accelLeft || 0) > 1e-9;                             // a skipped day (the harness): the scripted work stands in
  if (s.accelNow) s.accelLeft = Math.max(0, s.accelLeft - days);
  s.simDays += days;
  const events = [];
  // 1.3.226 (his 21:51, witness: "the messages say things are happening, but nothing is developing" — plots stayed pits for
  // 200+ days at speed 20 with skips): a stage that went to the builders on a REAL day (b.labor) advanced ONLY by a builder's
  // body standing within 6 blocks in work hours (100 per beat, 40 per block) and skipped days froze it. Now the town's
  // whole crew works every labour site every day (the ledger's builders x BLOCKS_PER_BUILDER_DAY, shared over the sites);
  // the bodies at the site add to it, and the stage still rises in the schedule beat when the work is done.
  const crewShare = new Map();
  const shareOf = (stt) => {
    if (!crewShare.has(stt.id)) {
      const n = Math.max(1, s.buildings.filter((x) => x.settlement === stt.id && x.labor && !x.closed).length);
      const crew = Math.max(2, (stt.ledger && stt.ledger.builders) || 2);
      const keep = s.accelNow ? 1 : PEOPLE.rainKeep("builders", wetShareOf(stt));   // 1.3.228 (B4): rain — the builders shelter, half kept
      crewShare.set(stt.id, (crew * ECON.BLOCKS_PER_BUILDER_DAY * BUILD_TICKS * keep) / n);
    }
    return crewShare.get(stt.id);
  };
  for (const b of s.buildings) {
    const last = BUILDINGS[b.family].stages - 1;
    let d = days;
    if (b.stage < 0) {                                     // a village plot waiting for its start day
      const use = Math.min(d, b.delay);
      b.delay -= use;
      d -= use;
      if (b.delay > 1e-9) continue;
      b.delay = 0;
      b.stage = 0;
      b.progress = 0;
      b.pending.push(0);
      events.push(`#${b.id} ${short(b)} -> plot`);
    }
    b.progress += d;
    if (b.labor) {                                                             // C2.3: the builders are at it
      b.progress = Math.min(b.progress, STAGE_DAYS[b.stage] || 0);
      const stl = b.settlement !== undefined ? s.settlements.find((x) => x.id === b.settlement) : null;
      if (stl) { b.labor.done += shareOf(stl) * days; b.labor.crewDays = (b.labor.crewDays || 0) + days; }   // 1.3.226: the crew's day (real or skipped)
      continue;
    }
    const SDAYS = b.palace ? PALACE_STAGE_DAYS : STAGE_DAYS;                       // 1.3.221: the palace keeps its own calendar
    while (b.stage < last && b.progress >= SDAYS[b.stage]) {
      if (b.palace) {                                                            // the crown's works: lockstep, wages only
        if (!palaceSiblingsReady(s, b, b.stage + 1)) { b.progress = SDAYS[b.stage]; break; }
        const stp = s.settlements.find((x) => x.id === b.settlement);
        if (stp && stp.ledger && stp.ledger.v === 2) {
          const bill = stageBillOf(b, b.stage + 1);
          const w = Math.min(bill.wages, Math.max(0, stp.ledger.treasury));
          ECON.pay(stp.ledger, { mats: {}, wages: w, blocks: 0 });
          stp.log.push(`day ${s.simDays.toFixed(0)}: the crown's works — the ${STAGE_NAMES[b.stage + 1]} of the palace's ${b.palace.q} quarter (${bill.blocks} blocks; ${w} p wages from the treasury)`);
        }
        b.progress -= SDAYS[b.stage];
        b.stage += 1;
        b.pending.push(b.stage);
        events.push(`#${b.id} ${short(b)} -> ${STAGE_NAMES[b.stage]}`);
        continue;
      }
      // D-C534 §4: the next stage is built only from stock, wages and builders on hand (a settlement's ledger)
      const stt = b.settlement !== undefined ? s.settlements.find((x) => x.id === b.settlement) : null;
      if (stt && stt.ledger && stt.ledger.v === 2) {
        const L = stt.ledger;
        const bill = stageBillOf(b, b.stage + 1);
        const budget = stt.buildBudget === undefined ? Infinity : stt.buildBudget;
        // 0.0.25e: the whole day free; 0.0.25h (run 0.0.27: the manor's 1,146-block stage never found a whole free day — the
        // small stages ahead of it took a little every day): a stage bigger than the crew's whole day starts on any day the
        // crew has work left and no debt
        const fresh = stt.buildCap !== undefined && !(stt.buildDebt > 0) && budget > 0 && (budget >= stt.buildCap || bill.blocks > stt.buildCap);
        const miss = ECON.missing(L, bill, fresh ? Infinity : budget);
        if (Object.keys(miss).length) {
          b.progress = STAGE_DAYS[b.stage];                                  // ready, waiting
          const key = Object.keys(miss).join(",");
          if (b.waitKey !== key) { b.waitKey = key; stt.log.push(`day ${s.simDays.toFixed(0)}: #${b.id} ${short(b)} waits for ${Object.entries(miss).map(([m, n]) => `${n} ${m}`).join(", ")}`); }
          b.waiting = { ...miss, blocks: bill.blocks };
          break;
        }
        ECON.pay(L, bill);
        stt.buildBudget = budget - bill.blocks;
        if (stt.buildBudget < 0) { stt.buildDebt = (stt.buildDebt || 0) - stt.buildBudget; stt.buildBudget = 0; }
        if (!s.accelNow) {
          // C2.3 (D-C541): a REAL day — the materials leave the store and the builders come; the stage waits for their work
          const took = takeFromStores(s, stt, bill, b.id);
          b.labor = { k: b.stage + 1, need: Math.max(BUILD_TICKS * 8, bill.blocks * BUILD_TICKS), done: 0, day: s.simDays, took };
          b.progress = STAGE_DAYS[b.stage];
          delete b.waiting; delete b.waitKey;
          stt.log.push(`day ${s.simDays.toFixed(0)}: the builders begin the ${STAGE_NAMES[b.stage + 1]} of #${b.id} ${short(b)} (${bill.blocks} blocks${took ? `; ${took} taken from the stores` : ""})`);
          break;
        }
        if (b.waiting) stt.log.push(`day ${s.simDays.toFixed(0)}: #${b.id} ${short(b)} ${STAGE_NAMES[b.stage + 1]} built (${Object.entries(bill.mats).map(([m, n]) => `${n} ${m}`).join(", ") || "labour"}; ${bill.wages} p wages)`);
        delete b.waiting; delete b.waitKey;
      }
      b.progress -= STAGE_DAYS[b.stage];
      b.stage += 1;
      if (b.stage === 4) LAST_BUILT.set(b.settlement, { day: Math.floor(s.simDays), name: short(b).replace(/_/g, " ") });   // B5: the news
      b.pending.push(b.stage);
      events.push(`#${b.id} ${short(b)} -> ${STAGE_NAMES[b.stage]}`);
    }
    if (b.stage >= last) b.progress = 0;
  }
  for (const st of s.settlements) {
    stepSettlement(s, st, days, events);
    if (!st.firstMarks && plotsOf(s, st).length && plotsOf(s, st).every((b) => b.stage >= 4)) { st.firstMarks = true; livingMarks(s, st, events); }
  }
  return events;
}


// ------------------------------------------------------------------------------------------------ THE CITY PALACE (1.3.221, D-C570)
// At CITY II the Seat of Government is laid on a palace block: four 64 x 64 pieces (sw se nw ne of the 128 x 128 model,
// tools/palacegen.py), placed as ONE rotated group (each piece rotated, the 2 x 2 positions permuted) with the gate toward
// the square; built in lockstep as the crown's works (wages from the treasury, materials imported — never waiting for stock).
const PALACE_PIECES = ["sw", "se", "nw", "ne"];
const PALACE_GRID = { sw: [0, 0], se: [0, 1], nw: [1, 0], ne: [1, 1] };          // (i = depth from the gate side, j = frontage)
const PALACE_STAGE_DAYS = [6, 8, 8, 6];                                            // village days at stage k before k + 1
const PALACE_TIER = "city2";
const PALACE_PER_DAY = 2;                                                          // 1.3.224: candidates measured a day (6 made the day's step slow)
const palaceFamily = (q) => `pw:mvv_palace_${q}_a_r1`;
function palaceGridRot(i, j, r) { return r === 1 ? [1 - j, i] : r === 2 ? [1 - i, 1 - j] : r === 3 ? [j, 1 - i] : [i, j]; }
/** the palace block: a 128 x 128 site (+ 2 cells of margin) 110..320 from the square, free of plots / streets / the square /
 *  park, the flattest candidate (ground sampled every 16 cells), its gate side toward the square. A SURVEY over days
 *  (st.palaceSurvey): each day up to 6 loaded candidates are measured; the first sleeping one is kept awake by the
 *  crown's surveyors (a 160 x 160 ticking area, held busy until the palace is laid) so tomorrow can read it. Accepted:
 *  relief <= 14 at once; <= 24 once 8 candidates were measured; <= 40 after 30 days; the best of all once every
 *  candidate has been tried. */
function palaceSite(s, st, dim) {
  const sq = st.square;
  if (!sq) return null;
  const cx = sq.x + 6, cz = sq.z + 6;
  // occupancy at CHUNK resolution, built once per survey day (run 2 of the gate: a per-candidate walk over ~20k street
  // cell keys took > 10 s in one tick — the watchdog killed the pack); a candidate is free when none of the chunks its
  // box touches holds a street cell or a plot box (conservative by up to 15 blocks, which the 2-cell margin absorbs)
  const occ = new Set();
  for (const k of streetHeights(s).keys()) { const c = k.indexOf(","); occ.add(`${Math.floor(+k.slice(0, c) / 16)},${Math.floor(+k.slice(c + 1) / 16)}`); }
  for (const [a, b2, c, d] of plotBoxes(s, 2)) for (let i = Math.floor(a / 16); i <= Math.floor(b2 / 16); i++) for (let j = Math.floor(c / 16); j <= Math.floor(d / 16); j++) occ.add(`${i},${j}`);
  const free = (x0, z0) => {
    const x1 = x0 + 131, z1 = z0 + 131;
    for (let i = Math.floor(x0 / 16); i <= Math.floor(x1 / 16); i++) for (let j = Math.floor(z0 / 16); j <= Math.floor(z1 / 16); j++) if (occ.has(`${i},${j}`)) return false;
    return true;
  };
  const sv = st.palaceSurvey || (st.palaceSurvey = { tried: {}, best: null, days: 0, loaded: 0 });
  sv.days++;
  let woke = null, evaluated = 0, open = 0;
  for (let R = 110; R <= 320 && evaluated < PALACE_PER_DAY; R += 24) {
    for (let a = 0; a < 16 && evaluated < PALACE_PER_DAY; a++) {
      const ang = a * Math.PI / 8;
      const x0 = Math.round(cx + Math.cos(ang) * R) - 64, z0 = Math.round(cz + Math.sin(ang) * R) - 64;
      const key = `${x0},${z0}`;
      if (sv.tried[key]) continue;
      if (!free(x0 - 2, z0 - 2)) { sv.tried[key] = 0; sv.why = sv.why || {}; sv.why.occupied = (sv.why.occupied || 0) + 1; continue; }   // 1.3.226: the reasons, counted
      const hs = [];
      let miss = false, wet = 0;
      for (let i = 0; i < 128 && !miss; i += 16) for (let j = 0; j < 128; j += 16) {
        // gallery gate run 2: a lake at y 108 read as flat ground (groundAt walks down to the bed) and the palace was laid in it;
        // the topmost block decides wetness at ANY height
        let topId, aboveId;
        try {
          const top = topAt(dim, x0 + i, z0 + j);             // run 4: this skips liquids (a 5-deep lake read as dry) —
          topId = top ? top.typeId : undefined;                                  // so the block ABOVE the topmost solid is read too
          const above = top ? blockAt(dim, x0 + i, top.location.y + 1, z0 + j, true) : undefined;
          aboveId = above ? above.typeId : "minecraft:air";
        } catch { topId = undefined; }                                            // reading a block of an unloaded chunk throws (run 3)
        if (!topId) { miss = true; break; }
        const isWet = (id) => id === "minecraft:water" || id === "minecraft:flowing_water" || id.includes("ice") || id === "minecraft:lava";
        if (isWet(topId) || isWet(aboveId)) wet++;
        const g = groundAt(dim, x0 + i, z0 + j);
        if (g === undefined) { miss = true; break; }
        hs.push(g);
      }
      if (miss) {
        open++;
        if (!woke) {
          woke = [x0, z0, R];
          try { const nm = ensureTicking(s, st, [x0 - 8, z0 - 8, x0 + 135, z0 + 135], `palace site survey (${R} from the square)`); if (nm) sv.area = nm; }   // run 9: the held area must cover the OUTSIDE samples too (8 cells out), or the site stays open for ever
          catch (e) { console.warn(`[CIV-CLOCK] palace survey: ${e}`); }
        }
        continue;                                                                    // a later candidate may be loaded already
      }
      evaluated++; sv.loaded++;
      const relief = Math.max(...hs) - Math.min(...hs);
      const H = median(hs) + 1;
      // gate runs 2–6: the box read dry and flat, but a lake stood just OUTSIDE it above the floor level; the land job's cut let
      // it pour in. 36 samples 8 cells outside the box (9 a side; run 9: 24 cells out lay beyond any area the surveyors can
      // hold — 10 x 10 chunks — and such sites were never measured): water (or ice) standing at or above feet -1 rejects
      let outsideWet = 0, bowl = 0;
      for (let k = 0; k < 36 && !miss; k++) {
        const t = k % 9, side = Math.floor(k / 9) % 4, far = 8;
        const sx2 = side === 0 ? x0 - far : side === 1 ? x0 + 127 + far : x0 + t * 16, sz2 = side === 2 ? z0 - far : side === 3 ? z0 + 127 + far : z0 + t * 16;
        try {
          const top = topAt(dim, sx2, sz2);
          if (!top) { miss = true; break; }
          let wetHere = top.typeId.includes("ice") ? top.location.y : -999;
          for (let yy = top.location.y + 1; yy < top.location.y + 64; yy++) { const a = blockAt(dim, sx2, yy, sz2, true); if (a && (a.typeId === "minecraft:water" || a.typeId === "minecraft:flowing_water")) wetHere = yy; else break; }
          if (wetHere >= H - 1) outsideWet++;
          if (top.location.y >= H + 16) bowl++;                                             // run 7: a mountain beside the block poured its lake over the walls
        } catch { miss = true; break; }
      }
      // inside, denser: any standing water above the floor level inside the box rejects (the first survey's 64 points missed a corner pond)
      let wetIn = 0;
      for (let i = 8; i < 128 && !miss; i += 16) for (let j = 8; j < 128; j += 16) {
        try {
          const top = topAt(dim, x0 + i, z0 + j);
          if (!top) { miss = true; break; }
          const a = blockAt(dim, x0 + i, top.location.y + 1, z0 + j, true);
          if ((a && a.typeId === "minecraft:water" && a.location.y >= H - 1) || (top.typeId.includes("ice") && top.location.y >= H - 1)) wetIn++;
        } catch { miss = true; break; }
      }
      if (miss) { open++; continue; }
      const score = relief + (wet + wetIn) * 6 + outsideWet * 6 + bowl * 3 + R / 40;
      { const w = (sv.why = sv.why || {}); const k = relief <= 14 ? "r14" : relief <= 24 ? "r24" : relief <= 40 ? "r40" : "r40+"; w[k] = (w[k] || 0) + 1; if (wet >= 3) w.wet = (w.wet || 0) + 1; if (wetIn) w.wetIn = (w.wetIn || 0) + 1; if (outsideWet) w.outsideWet = (w.outsideWet || 0) + 1; if (bowl) w.bowl = (w.bowl || 0) + 1; }
      sv.tried[key] = relief + 1;
      if (wet < 3 && wetIn === 0 && outsideWet === 0 && bowl === 0 && (!sv.best || score < sv.best.score)) sv.best = { x0, z0, score, relief, wet, R, H };
      if (relief <= 40 && (!sv.anyBest || score < sv.anyBest.score)) sv.anyBest = { x0, z0, score, relief, wet, wetIn, outsideWet, bowl, R, H };   // the fallback (60 days): the least wet, the least bowl-like
    }
  }
  const exhausted = !woke && evaluated === 0;
  let b = sv.best;
  if (!b && sv.anyBest && (sv.days >= 60 || exhausted)) b = sv.anyBest;             // no dry site in 60 days: the walls will hold the water
  const accept = b && (b.relief <= 14 || (sv.loaded >= 8 && b.relief <= 24) || (sv.days >= 30 && b.relief <= 40) || exhausted);
  if (!accept) {
    st.palaceSearch = { days: sv.days, loaded: sv.loaded, open, best: b ? [b.x0, b.z0, b.relief, b.R] : null, waiting: woke, day: s.simDays, why: sv.why || null };
    if (exhausted && !b && sv.days % 30 === 0) { sv.tried = {}; st.log.push(`day ${s.simDays.toFixed(0)}: the crown's surveyors found no ground for a palace yet (${sv.loaded} sites measured); they start again`); }
    return null;
  }
  const dx = cx - (b.x0 + 64), dz = cz - (b.z0 + 64);
  b.rot = Math.abs(dx) >= Math.abs(dz) ? (dx < 0 ? 0 : 2) : (dz < 0 ? 1 : 3);       // gate west 0 / north 1 / east 2 / south 3
  b.days = sv.days; b.measured = sv.loaded;
  return b;
}
/** the compass direction and distance from the square to the palace's centre, e.g. "212 blocks south-east" */
function palaceDir(st, site) {
  const dx = site.x0 + 64 - (st.square.x + 6), dz = site.z0 + 64 - (st.square.z + 6);
  const names = ["east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"];
  const a = Math.round(Math.atan2(dz, dx) / (Math.PI / 4));
  return `${Math.round(Math.hypot(dx, dz))} blocks ${names[(a + 8) % 8]}`;
}
// 1.3.226 (gate 225-1: with the streets unlocked the town's homes spread over every candidate block — 142 sites measured in
// 71 days, none free): the CROWN RESERVES ITS LAND from town III — the survey runs daily until a site is accepted; the
// reserved block (+2) is closed to houses and lanes; at city II the palace is laid there (re-checked first: a street that
// grew into it meanwhile sends the surveyors out again).
const PALACE_RESERVE_FROM = "town3";
function reserveBox(st) { const r = st.palaceReserve; return r ? [r.x0 - 2, r.x0 + 129, r.z0 - 2, r.z0 + 129] : null; }
function inReserve(s, x, z) { for (const st of s.settlements) { const b = reserveBox(st); if (b && x >= b[0] && x <= b[1] && z >= b[2] && z <= b[3]) return true; } return false; }
function boxInReserve(s, x0, x1, z0, z1) { for (const st of s.settlements) { const b = reserveBox(st); if (b && x0 <= b[1] && x1 >= b[0] && z0 <= b[3] && z1 >= b[2]) return true; } return false; }
function reservePalaceLand(s, st, dim) {
  if (st.palace || st.palaceReserve || !st.square || TIERS.indexOf(st.tier) < TIERS.indexOf(PALACE_RESERVE_FROM)) return;
  const site = palaceSite(s, st, dim);
  if (!site) return;
  st.palaceReserve = site;
  delete st.palaceSurvey; delete st.palaceSearch;
  st.log.push(`day ${s.simDays.toFixed(0)}: the crown RESERVES its land — a 128 x 128 block at ${site.x0} ${site.z0}, ${palaceDir(st, site)} of the square (relief ${site.relief}); no house may be built there`);
  try { world.sendMessage(`§6${st.name}: the crown reserves land for its future seat — centre §e${site.x0 + 64} ${site.H} ${site.z0 + 64}§6, ${palaceDir(st, site)} of the square.`); } catch { /* left */ }
}
function placePalace(s, st, dim) {
  if (st.palace) return false;
  let site = null;
  if (st.palaceReserve) {
    // still free of streets? (houses and lanes were kept out; a street may have grown in)
    const r = st.palaceReserve, body = kitBody(st);
    let clash = false;
    for (const k of body.keys ? body.keys() : body) { const c = k.indexOf(","), x = +k.slice(0, c), z = +k.slice(c + 1); if (x >= r.x0 - 2 && x <= r.x0 + 129 && z >= r.z0 - 2 && z <= r.z0 + 129) { clash = true; break; } }
    if (!clash) site = r; else st.log.push(`day ${s.simDays.toFixed(0)}: a street grew into the crown's reserved land — the surveyors look again`);
    delete st.palaceReserve;
  }
  if (!site) site = palaceSite(s, st, dim);
  if (!site) { st.palaceTries = (st.palaceTries || 0) + 1; return false; }
  const group = s.nextId++;
  const ids = [];
  for (const q of PALACE_PIECES) {
    const [i, j] = PALACE_GRID[q];
    const [gi, gj] = palaceGridRot(i, j, site.rot);
    const b = { id: s.nextId++, family: palaceFamily(q), dim: st.dim, x: site.x0 + gi * 64, y: site.H - BUILDINGS[palaceFamily(q)].datum_y, z: site.z0 + gj * 64,
                rot: site.rot, settled: true, stage: 0, progress: 0, delay: 0, pending: [0], settlement: st.id, planned: true, civic: "palace", palace: { group, q } };
    s.buildings.push(b);
    ids.push(b.id);
  }
  st.palace = { group, x0: site.x0, z0: site.z0, rot: site.rot, H: site.H, ids, day: s.simDays, survey: [site.days, site.measured] };
  delete st.palacePending; delete st.palaceSurvey; delete st.palaceSearch;
  st.log.push(`day ${s.simDays.toFixed(0)}: the SEAT OF GOVERNMENT is laid out — the palace block (128 x 128) at ${site.x0} ${site.z0}, gate ${["west", "north", "east", "south"][site.rot]}, ${site.R} from the square (relief ${site.relief}); the crown builds it`);
  try { world.sendMessage(`§6${st.name}: the Seat of Government is laid out — the palace block's centre is at §e${site.x0 + 64} ${site.H} ${site.z0 + 64}§6, ${palaceDir(st, site)} of the square. It rises over the next weeks.`); } catch { /* left */ }   // 1.3.224: his 16:50 (he never found it)
  return true;
}
/** the palace block's land, a generator for system.runJob (the plot stage of a piece is LIGHT — only the ground work at
 *  feet >= -2 — because placing the full 196k-cell box took up to 8 s in one tick, two seconds under the watchdog):
 *  1. NATURAL blocks inside the piece's box and 24 rows above it are cleared (trees, plants, hills, water, snow) — never
 *     a block of ours, so a stage placed while the job still runs is safe;
 *  2. hollows under the floor slab (feet -15 .. -3) are filled with dirt where the terrain is air, water or leaves;
 *  3. the one-cell margin ring is filled from the ground up to the lawn (feet -1).
 *  ~300 block reads per tick; a piece takes ~15 s of real time, well inside the six days to the frame stage */
const NATURAL = ["minecraft:dirt", "minecraft:grass_block", "minecraft:stone", "minecraft:deepslate", "minecraft:gravel", "minecraft:sand", "minecraft:red_sand",
  "minecraft:coarse_dirt", "minecraft:podzol", "minecraft:mycelium", "minecraft:clay", "minecraft:tuff", "minecraft:calcite", "minecraft:andesite", "minecraft:diorite",
  "minecraft:granite", "minecraft:water", "minecraft:flowing_water", "minecraft:snow", "minecraft:snow_layer", "minecraft:ice", "minecraft:packed_ice", "minecraft:mud",
  "minecraft:moss_block", "minecraft:rooted_dirt", "minecraft:dirt_with_roots", "minecraft:mossy_cobblestone", "minecraft:bedrock"];
const NATURAL_WORDS = ["leaves", "_log", "_wood", "sapling", "mushroom", "vine", "bee_nest", "cocoa", "fern", "grass", "bush", "flower", "lily", "kelp", "seagrass",
  "coral", "cactus", "bamboo", "azalea", "dripleaf", "sweet_berry", "spore", "sugar_cane", "pumpkin", "melon", "dead_bush", "tallgrass", "double_plant", "mangrove_roots"];
function isNatural(id) {
  if (NATURAL.includes(id) || id.endsWith("_ore") || isTreeLeafId(id)) return true;
  if (id.startsWith("pw:")) return ["leaves", "root", "ground", "log", "trunk", "vine", "moss", "fern", "grass", "bush", "mushroom", "litter"].some((q) => id.includes(q));   // our tree / plant blocks only — never a roof, a flue, a furnishing
  return NATURAL_WORDS.some((q) => id.includes(q));
}
/** the RETAINING WALLS on the palace block's outer perimeter (never between two pieces): where the land or standing water
 *  just outside stands at or above the floor, the piece's edge column is clad in stone from feet -1 up to that height.
 *  Run 11 (10-05): an edge whose OUTSIDE column lay in a sleeping chunk got no wall at all (the read came back empty) and the
 *  lake poured in at 26k cells a day — so the height is the greater of the outside column and the piece's own edge column
 *  (always loaded while the piece is built), each climbed from the topmost solid through any water to the SURFACE; and the
 *  walls are checked again on every pump pass (a chunk asleep at the land job wakes later). */
function* palaceWallJob(dim, b, def) {
  const [fx, sy, fz] = footprint(def, b.rot);
  const slab = b.y + def.datum_y - 1;
  let ops = 0, walled = 0;
  const tick = function* () { if (++ops % 300 === 0) yield; };
  const stp = load().settlements.find((x) => x.palace && x.palace.group === b.palace.group);
  const box = stp ? [stp.palace.x0, stp.palace.z0, stp.palace.x0 + 127, stp.palace.z0 + 127] : null;
  if (!box) return 0;
  const WATERY = (a) => a.typeId === "minecraft:water" || a.typeId === "minecraft:flowing_water" || a.typeId.includes("ice") || a.isLiquid || a.isWaterlogged
    || /kelp|seagrass|coral|sea_pickle|bubble_column|lily_pad/.test(a.typeId);
  const surfaceAt = (x, z) => {                                              // the WATER surface + 1 in column x z (his 12:12 rule), or the ground; undefined when asleep
    const t = topAt(dim, x, z);
    if (!t) return undefined;
    let top = t.location.y, wet = WATERY(t);
    for (let yy = top + 1; yy < top + 64; yy++) { const a = blockAt(dim, x, yy, z, true); if (a && WATERY(a)) { top = yy; wet = true; } else break; }   // run 16: through water plants too
    return wet ? top + 1 : top;                                                // run 17: +1 only over WATER — a wall read as its own top grew one block every pass
  };
  const edge = [];
  for (let i = 0; i < fx; i++) { if (b.z === box[1]) edge.push([b.x + i, b.z, 0, -1]); if (b.z + fz - 1 === box[3]) edge.push([b.x + i, b.z + fz - 1, 0, 1]); }
  for (let j = 0; j < fz; j++) { if (b.x === box[0]) edge.push([b.x, b.z + j, -1, 0]); if (b.x + fx - 1 === box[2]) edge.push([b.x + fx - 1, b.z + j, 1, 0]); }
  for (const [x, z, dx, dz] of edge) {
    let top = -999;
    // run 15: the margin ring is filled to the slab and reads DRY — the lake begins one cell further out and poured over the
    // margin at its own level; the wall takes the highest surface found 1..8 cells out (loaded columns only)
    for (const far of [1, 2, 3, 5, 8]) { try { const o = surfaceAt(x + dx * far, z + dz * far); if (o !== undefined) top = Math.max(top, o); } catch { /* asleep: the next column decides */ } }
    // gate 223-1 (15:4x): the INSIDE column's topmost block is the palace itself (walls, eaves, roofs) once the stages stand —
    // reading it raised a stone curtain to roof height round the block (824 + 622 + 762 blocks). Only the OUTSIDE columns
    // decide; while they sleep the edge waits for a later pump pass (the pumps hold the block's area).
    // run 16 (his 12:12 rule): the wall stands ONE BLOCK HIGHER than the water — the east wall reached y 119 under a lake
    // whose surface cell was 120, and the lake walked over it onto the cornice
    for (let y = slab; y <= Math.min(top, b.y + sy - 1); y++) {
      // run 14: the wall in the piece's own edge column is opened again by the stages (the front doors, the carriage arch) —
      // the lake walked in through the doorways. The wall now stands in the MARGIN column outside the piece as well, which
      // no stage ever touches; the inside course stays as the fallback while the outside chunk sleeps
      for (const [wx, wz] of [[x + dx, z + dz], [x, z]]) {
        try { const blk = blockAt(dim, wx, y, wz); if (blk && (blk.typeId === "minecraft:air" || isNatural(blk.typeId))) { blk.setType("minecraft:stone_bricks"); walled++; } } catch { /* unloaded */ }
      }
      yield* tick();
    }
    yield* tick();
  }
  return walled;
}
/** run 12 (10-05): a lake is INFINITE WATER — two source blocks beside a drained cell make a new source, so a cell-by-cell
 *  drain (300 cells a tick) never ends: every pump pass found 20–27k cells again with every wall in place. The water is
 *  removed in ONE go per slab with /fill ... replace (engine-side, one tick, no regeneration window): slabs of 7 layers
 *  keep each call under the 32,768-block limit. Returns [commands that succeeded, commands that failed]. */
function drainBox(dim, x0, y0, z0, x1, y1, z1) {
  let ok = 0, bad = 0, firstErr = null;
  for (let y = y0; y <= y1; y += 7) {
    const yt = Math.min(y + 6, y1);
    // FLOW test (10-05 13:2x): flowing and falling water carry the id minecraft:water (liquid_depth 1-7, 8+) — one filter removes all
    try { const r = dim.runCommand(`fill ${x0} ${y} ${z0} ${x1} ${yt} ${z1} air [] replace water`); if (r && r.successCount > 0) ok++; else { bad++; if (!firstErr) firstErr = `successCount 0 at y ${y}..${yt} (nothing matched, or a chunk of the volume sleeps)`; } }
    catch (e) { bad++; if (!firstErr) firstErr = String(e).slice(0, 120); }
  }
  if (bad && firstErr) console.warn(`[CIV-CLOCK] drain: ${bad} fill command(s) failed: ${firstErr}`);
  return [ok, bad];
}
/** drainBox as a generator: one /fill per tick (1.3.224: a wet site's 36 fills in one step — ~1 M cells plus their water
 *  updates — was a watchdog Hang on his device). Returns [ok, bad]. */
function* drainBoxJob(dim, x0, y0, z0, x1, y1, z1) {
  let ok = 0, bad = 0;
  for (let y = y0; y <= y1; y += 7) {
    const [o, b] = drainBox(dim, x0, y, z0, x1, Math.min(y + 6, y1), z1);
    ok += o; bad += b;
    yield;
  }
  return [ok, bad];
}
/** the palace block's land, a generator for system.runJob (the plot stage of a piece is LIGHT — only the ground work at
 *  feet >= -2 — because placing the full 196k-cell box took up to 8 s in one tick, two seconds under the watchdog):
 *  0. the retaining walls (palaceWallJob);
 *  1. NATURAL blocks inside the piece's box and 24 rows above it are cleared (trees, plants, hills, water, snow) — never
 *     a block of ours, so a stage placed while the job still runs is safe;
 *  2. hollows under the floor slab (feet -15 .. -3) are filled with dirt where the terrain is air, water or leaves;
 *  3. the one-cell margin ring is filled from the ground up to the lawn (feet -1).
 *  ~300 block reads per tick; a piece takes ~2 min of real time, well inside the six days to the frame stage */
function* palaceLandJob(dim, b, def) {
  const [fx, sy, fz] = footprint(def, b.rot);
  const slab = b.y + def.datum_y - 1;
  const floor0 = b.y + def.datum_y;                                 // feet 0
  let ops = 0, cleared = 0, filled = 0;
  const tick = function* () { if (++ops % 300 === 0) yield; };
  const walled = yield* palaceWallJob(dim, b, def);
  const [dOk, dBad] = yield* drainBoxJob(dim, b.x, floor0, b.z, b.x + fx - 1, b.y + sy + 23, b.z + fz - 1);   // the lake inside (feet 0 up: the basin at feet -1 is the template's); 1.3.224: one fill per tick
  for (let i = 0; i < fx; i++) for (let j = 0; j < fz; j++) {
    const x = b.x + i, z = b.z + j;
    for (let y = floor0; y < b.y + sy + 24; y++) {                 // 1. the box and the sky above it
      let blk;
      try { blk = blockAt(dim, x, y, z); } catch { blk = undefined; }
      if (blk && blk.typeId !== "minecraft:air" && isNatural(blk.typeId)) { try { blk.setType("minecraft:air"); cleared++; } catch { /* left */ } }
      yield* tick();
    }
    for (let y = b.y; y <= slab - 2; y++) {                          // 2. under the slab
      let blk;
      try { blk = blockAt(dim, x, y, z); } catch { blk = undefined; }
      if (blk && (blk.typeId === "minecraft:air" || blk.typeId === "minecraft:water" || blk.typeId === "minecraft:flowing_water" || blk.typeId.includes("leaves") || isTreeLeafId(blk.typeId))) { try { blk.setType("minecraft:dirt"); filled++; } catch { /* left */ } }
      yield* tick();
    }
  }
  for (let i = -1; i <= fx; i++) for (let j = -1; j <= fz; j++) {   // 3. the margin ring
    if (!(i < 0 || j < 0 || i >= fx || j >= fz)) continue;
    const x = b.x + i, z = b.z + j;
    const g = groundAt(dim, x, z);
    if (g === undefined) { yield* tick(); continue; }
    for (let y = g + 1; y <= slab; y++) {
      try { const blk = blockAt(dim, x, y, z); if (blk && (blk.typeId === "minecraft:air" || !isGround(blk.typeId))) { blk.setType(y === slab ? "minecraft:grass_block" : "minecraft:dirt"); filled++; } } catch { /* unloaded */ }
      yield* tick();
    }
  }
  console.warn(`[CIV-CLOCK] palace land #${b.id} ${b.palace.q}: ${walled} retaining blocks, drain ${dOk} ok / ${dBad} failed, ${cleared} natural blocks cleared, ${filled} filled`);
  b.palaceDrain = 60;                                                 // the pumps: sixty daily passes (each re-checks the walls first)
}
/** the palace's pumps: the walls are checked again, then water above the floor inside the piece's box becomes air (a
 *  generator; ~300 reads a tick) */
function* palaceDrainJob(dim, pieces, def) {
  // run 14: the four quarters are drained in ONE tick (a quarter drained minutes after its neighbour regrows from it)
  let ops = 0, before = 0, after = 0, walled = 0, dOk = 0, dBad = 0;
  for (let w = 0; w < 60; w++) yield;                                       // build 19: the areas asked for a moment ago need a few ticks to load
  for (const b of pieces) walled += yield* palaceWallJob(dim, b, def);
  const wet = (x, y, z) => { try { const t = blockAt(dim, x, y, z)?.typeId; return t === "minecraft:water" || t === "minecraft:flowing_water"; } catch { return false; } };
  // run 17 (the dump): a mountain pond INSIDE the block's columns above the box's top (y 141+ over an SE corner at 140) fed the
  // palace from the sky — the pumps emptied the box to its top and the pond refilled it. The pumps reach the land job's
  // clearing height (24 rows above the box), and the whole group in one tick, so no part of a pond survives to regrow.
  const boxes = pieces.map((b) => { const [fx, sy, fz] = footprint(def, b.rot); return [b.x, b.y + def.datum_y, b.z, b.x + fx - 1, b.y + sy + 23, b.z + fz - 1]; });
  const wetIn = boxes.map(() => 0);
  for (let bi = 0; bi < boxes.length; bi++) { const [x0, y0, z0, x1, y1, z1] = boxes[bi]; for (let x = x0; x <= x1; x += 4) for (let z = z0; z <= z1; z += 4) for (let y = y0; y <= y1; y++) { if (wet(x, y, z)) { before++; wetIn[bi]++; } if (++ops % 300 === 0) yield; } }
  // 1.3.224: only a box with sampled water is filled, one /fill per tick (the four boxes inside ~36 ticks; a source needs two
  // source neighbours on solid ground to regrow, so the quarters no longer have to go in the same tick)
  for (let bi = 0; bi < boxes.length; bi++) { if (!wetIn[bi]) continue; const [o, bd] = yield* drainBoxJob(dim, ...boxes[bi]); dOk += o; dBad += bd; }
  for (const [x0, y0, z0, x1, y1, z1] of boxes) for (let x = x0; x <= x1; x += 4) for (let z = z0; z <= z1; z += 4) for (let y = y0; y <= y1; y++) { if (wet(x, y, z)) after++; if (++ops % 300 === 0) yield; }
  const names = pieces.map((b) => `#${b.id} ${b.palace.q}`).join(" ");
  // 1.3.224: three dry passes in a row end the pumps (the templates are dry since 1.3.223; only the site's own water is left)
  for (const b of pieces) { b.palaceDry = before === 0 && after === 0 ? (b.palaceDry || 0) + 1 : 0; if (b.palaceDry >= 3) b.palaceDrain = 0; }
  if (before || walled || dOk) console.warn(`[CIV-CLOCK] palace pumps ${names}: ${before} sampled water cells before, ${after} after (fill ${dOk} ok / ${dBad} nothing), ${walled} wall blocks added (${pieces[0].palaceDrain} passes left)`);
}
const palacePumpJobs = new Set();                                   // 1.3.224: one pump job per palace group at a time
/** every piece of the group must stand at stage k - 1 before any piece goes to stage k (the four quarters rise together) */
function palaceSiblingsReady(s, b, k) {
  for (const o of s.buildings) if (o.palace && o.palace.group === b.palace.group && o.id !== b.id && o.stage < k - 1) return false;
  return true;
}

// ------------------------------------------------------------------------------------------------ settlements
function plotsOf(s, st) { return s.buildings.filter((b) => b.settlement === st.id); }

function allRoofed(s, st) { return plotsOf(s, st).every((b) => b.stage >= 3); }

/** a new plot on the settlement's streets: the current street east of its last plot, else a new parallel street. */
function allocate(s, st, family, pick) {
  const def = BUILDINGS[family];
  if (st.planned) {
    const contour = st.streets.filter((x) => x.kind === "contour");
    const free = slotFree(s, st);
    const toSpot = (slot0) => { const slot = LAND.slotToWorld(slot0); return { x: slot.wx, z: slot.wz, rot: slot.wrot, fx: slot.wfx, street: streetOf(slot), streetAxis: slot.axis, yard: slot.yard || 0, planned: true }; };
    for (const street of contour) {
      const [slot] = LAND.slotsAlongStreet(street.runs, [{ family, ...LAND.sizeInFrame(def) }], 1, free);
      if (slot) return toSpot(slot);
    }
    for (let tries = 0; tries < 3; tries++) {
      const next = openContourStreet(s, st, pick);
      if (!next) break;
      const [slot] = LAND.slotsAlongStreet(next.runs, [{ family, ...LAND.sizeInFrame(def) }], 1, slotFree(s, st));
      if (slot) return toSpot(slot);
    }
    return null;
  }
  for (let tries = 0; tries < 4; tries++) {
    const street = st.streets[st.streets.length - 1];
    const north = street.nextNorth;                       // alternate sides so both frontages fill
    const rot = north ? 3 : 1;
    const [fx, , fz] = footprint(def, rot);
    const x = north ? street.xn : street.xs;
    if (x + fx - street.x0 <= STREET_MAX) {
      const z = north ? street.z0 - fz : street.z0 + STREET_W;
      if (north) street.xn = x + fx + 1; else street.xs = x + fx + 1;
      street.nextNorth = !north;
      return { x, z, rot, fx, street: [x - 1, x + fx - 1, street.z0] };
    }
    // open a parallel street: north of the first, then south, then further north …
    const k = st.streets.length;
    const dz = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * STREET_GAP;
    st.streets.push({ x0: st.x0, z0: st.z0 + dz, xn: st.x0, xs: st.x0, nextNorth: true });
  }
  return null;
}

/** the next contour street: a terrace up or down the hill (h0 +- 6), walked from the point north / south of the square
 *  where the ground reaches that height, snapped and smoothed like the main street; laid at once. */
function openContourStreet(s, st, pick) {
  const site = siteOf(st);
  if (!site || !st.square) return null;
  // terraces above and below the main street: +6, -6, +4, -4, +8, -8, +10, -10 … each tried once (the hill may not have it);
  // the start column is the square's middle, the start row the first ground at that height at least 14 rows away
  st.triedTerraces = st.triedTerraces || [];
  const used = new Set(st.streets.filter((x) => x.kind === "contour").map((x) => x.h ?? st.h0));
  const fsite = (st.axis || "x") === "z" ? LAND.transposed(site) : site;              // the planner's frame
  const fsq = (st.axis || "x") === "z" ? { x: st.square.z, z: st.square.x } : st.square;
  const cx = fsq.x + 6;
  let start = null, walk = null, up = true;
  for (const off of [6, -6, 4, -4, 8, -8, 10, -10, 12, -12]) {
    const target = st.h0 + off;
    if (st.triedTerraces.includes(off) || used.has(target)) continue;
    st.triedTerraces.push(off);
    for (const dir of [-1, 1]) {
      for (let dz = 14; dz <= 70 && !start; dz++) {
        const z = fsq.z + 6 + dir * dz;
        const y = fsite.at(cx, z);
        if (y !== undefined && !fsite.isWater(cx, z) && Math.abs(y - target) <= 1) start = { x: cx, z, y };
      }
      if (start) break;
    }
    if (!start) continue;
    const east = LAND.walkContour(fsite, start.x, start.z, start.y, +1);
    const west = LAND.walkContour(fsite, start.x, start.z, start.y, -1);
    walk = west.slice(1).reverse().concat(east);
    // the new street must not run over the plots already standing (keep 4 rows clear of every plot box) and must keep a
    // plot's depth (18 rows) from every existing street, or its plots would reach into the other street's plots
    const T = (st.axis || "x") === "z";
    const boxes = plotsOf(s, st).map((b) => { const [x0, x1, z0, z1] = boxOf(b, 4); return T ? [z0, z1, x0, x1] : [x0, x1, z0, z1]; });
    const streetZ = [];
    for (const key of Object.keys(st.profile || {})) { const [x, z] = key.split(",").map(Number); streetZ.push(T ? [z, x] : [x, z]); }
    const nearStreet = (c) => streetZ.some(([x, z]) => Math.abs(x - c[0]) <= 2 && Math.abs(z - c[1]) < 18 + STREET_W);
    const okCell = (c) => !boxes.some(([x0, x1, z0, z1]) => c[0] >= x0 && c[0] <= x1 && c[1] >= z0 && c[1] <= z1) && !nearStreet(c);
    // keep the longest unbroken stretch of the walk (a street with holes would snap into nonsense)
    let best = [], cur = [];
    for (const c of walk) { if (okCell(c)) cur.push(c); else { if (cur.length > best.length) best = cur; cur = []; } }
    if (cur.length > best.length) best = cur;
    walk = best;
    up = off > 0;
    if (walk.length >= 24) break;
    start = null; walk = null;
  }
  if (!start || !walk) return null;
  const { runs, cells } = LAND.snapRuns(walk);
  LAND.smoothProfile(cells);
  const axis = st.axis || "x";
  const w = (c) => (axis === "z" ? [c[1], c[0], c[2]] : c);
  const wcells = cells.map(w);
  for (const c of wcells) st.profile[`${c[0]},${c[1]}`] = c[2];
  for (const r of runs) { r.axis = axis; for (const c of r.cells) { const wc = w(c); c[2] = st.profile[`${wc[0]},${wc[1]}`]; } }
  const street = { kind: "contour", axis, runs: runs.map((r) => ({ axis, z: r.z, x0: r.x0, x1: r.x1, ux0: r.ux0, ux1: r.ux1, jog: r.jog })).filter((r) => r.x1 - r.x0 >= 8), cells: wcells, h: start.y };
  street.laid = layPlannedStreet(world.getDimension(st.dim), street);
  street.nCells = street.cells.length;
  delete street.cells;
  st.streets.push(street);
  st.log.push(`day ${s.simDays.toFixed(0)}: a new street opened on the ${up ? "upper" : "lower"} terrace (y ${start.y}, ${cells.length} cells)`);
  return street;
}

function addPlot(s, st, family, dimId, delay, pick) {
  if (st.kit) return kitAddPlot(s, st, family, delay);          // v1.3.219: StreetKit streets
  const spot = allocate(s, st, family, pick);
  if (!spot) return null;
  const bld = { id: s.nextId++, family, dim: dimId, x: spot.x, y: 0, z: spot.z, rot: spot.rot, settled: false, stage: -1,
                progress: 0, delay, pending: [], street: spot.street, streetAxis: spot.streetAxis || "x", yard: spot.yard || 0, settlement: st.id, planned: !!spot.planned };
  if (delay === 0) { bld.stage = 0; bld.pending.push(0); }
  s.buildings.push(bld);
  return bld;
}

function tierUp(s, st, tier, events) { return timed(`tier-up ${tier}`, () => tierUpBody(s, st, tier, events)); }
/** 1.3.228 (B7 / BF8): the notice board's slips today (real gaps only; the done ones are gone) */
function waitNeedOf(s, st) {
  const out = {};
  for (const b of plotsOf(s, st)) if (b.waiting) for (const [m, n] of Object.entries(b.waiting)) if (m !== "blocks" && typeof n === "number") out[m] = (out[m] || 0) + n;
  return out;
}
function noticeSlips(s, st) {
  const L = st.ledger;
  if (!L) return [];
  const day = Math.floor(s.simDays);
  if (!st.slips || st.slips.day !== day) st.slips = { day, roll: 0, done: [] };
  return ECON.slipsOf(L, { waitNeed: waitNeedOf(s, st), population: population(s, st) }, day, st.slips.roll).filter((x) => !st.slips.done.includes(x.good));
}
/** 1.3.228 (B6 / BF6): what the weighted pick reads — shortages, the rooms free, affordability (the whole bill s1..s4
 *  against the stock + PLAN.AFFORD.prodDays of production, and the treasury), the player's priorities */
function planCtx(s, st) {
  const L = st.ledger;
  const shortGoods = new Set(Object.entries(st.shortDays || {}).filter(([, d]) => d > 0).map(([g]) => g));
  let roomsFree = 0;
  try { for (const h of homeRoom(s, st)) roomsFree += h.room || 0; } catch { roomsFree = 99; }
  const prod = {};
  for (const b of plotsOf(s, st)) { const pr = ECON.PRODUCE[short(b)]; if (pr && b.stage >= 4 && !b.closed) for (const [g, n] of Object.entries(pr.out)) prod[g] = (prod[g] || 0) + n; }
  const missing = (nm) => {
    if (!L) return {};
    const fam = familyOf(nm, (skinsOf(nm)[0]) || "a");
    const bom = (BUILDINGS[fam] && BUILDINGS[fam].bom) || [];
    const need = {}; let wages = 0;
    for (let k = 1; k < bom.length; k++) { const bill = ECON.stageBill(bom, k); wages += bill.wages; for (const [m, n] of Object.entries(bill.mats)) need[m] = (need[m] || 0) + n; }
    const out = {};
    for (const [m, n] of Object.entries(need)) { const have = (L.stock[m] || 0) + (prod[m] || 0) * PLAN.AFFORD.prodDays; if (have < n) out[m] = Math.ceil(n - have); }
    if (L.treasury < wages) out.pennies = wages - L.treasury;
    return out;
  };
  return { shortGoods, produces: (nm) => Object.keys((ECON.PRODUCE[nm] || {}).out || {}), roomsFree, missing, prio: st.prio || [] };
}
/** 1.3.224 (his Hang past CITY II): a tier-up no longer lays its plots in one tick (City II took 6–8 s on the test server,
 *  City III would pass the 10 s watchdog). The charter is written NOW (tier, civic works, leftovers, the tier's plots,
 *  then the centres / palace / border / marks) as st.tierWork, and tierWorkStep lays it out ONE item per kit beat. */
function tierUpBody(s, st, tier, events) {
  const pick = rng((st.seed + TIERS.indexOf(tier) * 7919) >>> 0);
  const items = [];
  const tc = TIER_CLASS(tier);                                             // 1.3.228 (B6 / GB12): the skin follows the district
  const skinPick = (nm, i) => { const skins = skinsOf(nm); void pick(); return familyOf(nm, PLAN.skinFor(DISTRICT[nm] || "homes", skins, tc, i)); };
  for (const [work, fam] of CIVIC[tier] || []) {
    if (fam === "post") { st.log.push(`day ${s.simDays.toFixed(0)}: the council opens the ${work} office`); continue; }
    items.push({ family: skinPick(fam, items.length), work, fam });
  }
  for (const nm of (st.leftover || [])) items.push({ family: skinPick(nm, items.length), nm, left: true });
  st.leftover = [];
  for (const [nm, n] of TIER_ADDS[tier]) for (let i = 0; i < n; i++) items.push({ family: skinPick(nm, items.length), nm });
  // 1.3.228 (B6 / BF6): the charter's items (counts are law) in the weighted order: civic works, a business that cures a
  // shortage, homes when rooms run short, the rest; an unaffordable big project waits behind affordable work
  try { const ord = PLAN.orderItems(items, planCtx(s, st), (st.seed || 1) + TIERS.indexOf(tier)); items.length = 0; items.push(...ord); } catch (e) { console.warn(`[CIV-CLOCK] plan order: ${e}`); }
  st.tier = tier;
  st.tierDay = s.simDays;
  st.tierWork = { tier, items, i: 0, k: 0, added: 0, after: ["centres", "palace", "border", "marks"], seed: (st.seed + TIERS.indexOf(tier) * 104729) >>> 0 };
  st.log.push(`day ${s.simDays.toFixed(0)}: ${tierLabel(st)} — the council charters ${items.length} plot(s); the surveyors lay them out`);
  annal(st, s.simDays, `became a ${tierLabel(st)}`);                         // B10 (WP7): the chronicle
  events.push(`§b${st.name} -> ${tierLabel(st).toUpperCase()} (${items.length} plots being laid out)`);
  return [];
}
/** one item of a settlement's tier work (a plot, then the after-steps); called from the kit beat. Returns true when done. */
let tierStepLabel = "";
function tierWorkStep(s, st) {
  const tw = st.tierWork;
  if (!tw) return true;
  if (tw.i < tw.items.length) {
    const it = tw.items[tw.i];
    tierStepLabel = `${it.family || it.nm || "?"} phase ${it.phase || 0}`;
    const pick = rng((tw.seed + tw.i * 7919) >>> 0);
    let b = null;
    if (st.kit) {                                                            // 1.3.227: one search phase per beat
      let r = null;
      try { r = kitTryPhase(s, st, it.family, tw.k * VILLAGE_STAGGER, it.phase || 0); } catch (e) { console.warn(`[CIV-CLOCK] tier plot: ${e}`); }
      if (r === "next") { it.phase = (it.phase || 0) + 1; return false; }
      b = r;
    } else {
      try { b = addPlot(s, st, it.family, st.dim, tw.k * VILLAGE_STAGGER, pick); } catch (e) { console.warn(`[CIV-CLOCK] tier plot: ${e}`); }
    }
    if (b) {
      tw.k++; tw.added++;
      if (it.work) { b.civic = it.work; st.log.push(`day ${s.simDays.toFixed(0)}: the ${it.work} is laid out (#${b.id}, a ${it.fam.replace("_", " ")} until its own design)`); }
    } else if (it.work) (st.civicLeft = st.civicLeft || []).push([it.work, it.fam]);
    else (st.leftover = st.leftover || []).push(it.nm);                 // no room now: retried a plot a day (stepSettlement)
    tw.i++;
    save();
    return false;
  }
  const step = tw.after.shift();
  tierStepLabel = `after: ${step}${step === "marks" && tw.mk ? ` ${tw.mk.i}/${tw.mk.ids.length}.${tw.mk.r}` : ""}`;
  const pick = rng((tw.seed + 31337) >>> 0);
  const events = [];
  if (step === "centres") { try { for (const b of openCentres(s, st, pick, tw.k * VILLAGE_STAGGER)) { void b; tw.added++; tw.k++; } } catch (e) { console.warn(`[CIV-CLOCK] centres: ${e}`); } }
  else if (step === "palace") {
    if (tw.tier === PALACE_TIER && !st.palace) { try { if (!placePalace(s, st, world.getDimension(st.dim))) st.palacePending = true; } catch (e) { console.warn(`[CIV-CLOCK] palace: ${e}`); st.palacePending = true; } }
  } else if (step === "border") {
    try { if (st.border) planBorderGrowth(s, st, Math.max(INFLUENCE[tw.tier] || 0, st.border.r + BORDER_TIER), !!s.accelNow); } catch (e) { console.warn(`[CIV-CLOCK] border growth: ${e}`); }
  } else if (step === "marks") {                                       // 1.3.228: one quarry / lumberyard / town job per beat
    let done = true;
    try { if (!tw.mk) tw.mk = marksCursor(s, st); done = marksStep(s, st, tw.mk, events); } catch (e) { console.warn(`[CIV-CLOCK] marks: ${e}`); }
    if (!done) { tw.after.unshift("marks"); save(); return false; }
    delete tw.mk;
  }
  if (!tw.after.length) {
    st.log.push(`day ${s.simDays.toFixed(0)}: ${tierLabel(st)} laid out (+${tw.added} plots; ${population(s, st)} people)`);
    events.push(`§b${st.name}: ${tierLabel(st)} laid out (+${tw.added} plots)`);
    delete st.tierWork;
  }
  save();
  if (events.length) tellNear(st, events);
  return !st.tierWork;
}
/** events raised outside a day (tier work) go to the players, like a day's events */
function tellNear(st, events) { void st; for (const e of events) console.warn(`[CIV-CLOCK] ${e.replace(/§./g, "")}`); }

/** the marks a tier leaves on the land (also run once when the first plots finish, tierIdx 0).
 *  1.3.228: stepped — the tier-work "marks" step took 763 ms at City III and 1178 ms at Metropolis II in gate 228-1
 *  (every quarry dug + every lumberyard cleared + leaves + walls in ONE tick). marksStep does ONE quarry/lumberyard,
 *  or ONE of the town-wide jobs, per call; the kit beat calls it until it returns true. */
const MARK_KINDS = new Set(["quarry", "lumberyard"]);
function marksCursor(s, st) {
  return { ids: plotsOf(s, st).filter((b) => b.stage >= 4 && MARK_KINDS.has(short(b))).map((b) => b.id), i: 0, r: 0, dug: 0, trees: 0, logs: 0, marks: [] };
}
function marksStep(s, st, mk, events) {
  const dim = world.getDimension(st.dim);
  const ti = TIER_IDX(st.tier);
  if (mk.i < mk.ids.length) {
    const id = mk.ids[mk.i++];
    const b = s.buildings.find((x) => x.id === id && x.settlement === st.id);
    if (!b) return false;
    const kind = short(b);
    try {
      if (kind === "quarry") { const dug = digQuarry(dim, b, st, ti, 400); if (dug) { mk.dug += dug; if (st.ledger) st.ledger.stock.stone += dug; } }
      if (kind === "lumberyard") { const r = clearForest(dim, b, st, ti); if (r.trees) { mk.trees += r.trees; mk.logs += r.logs; if (st.ledger) st.ledger.stock.timber += r.logs; } }
    } catch (e) { console.warn(`[CIV-CLOCK] marks ${kind}: ${e}`); }
    return false;
  }
  const marks = mk.marks;
  switch (mk.r++) {
    case 0:
      if (mk.dug) marks.push(`quarries dug ${mk.dug} stone`);
      if (mk.trees) marks.push(`lumberyards felled ${mk.trees} trees (${mk.logs} logs)`);
      { const hardened = st.kit ? 0 : hardenStreets(dim, st, ti); if (hardened) marks.push(`streets ${TIER_CLASS(st.tier) >= 1 ? "cobbled" : "gravelled"} (${hardened})`); }
      return false;
    case 1:
      if (st.kit && TIER_CLASS(st.tier) >= 1) {                      // v1.3.219: town width + a park (his 18:02)
        const n = widenKit(st);
        if (n) marks.push(`streets resurfaced to the town width (${n} pieces)`);
      }
      return false;
    case 2:
      if (st.kit && TIER_CLASS(st.tier) >= 1 && !st.park && kitPark(s, st)) marks.push("a park staked out");
      return false;
    case 3:
      if (st.kit) sweepLeaves(st);
      return false;
    case 4:
      if (st.kit) {
        // D-C534 §3: walls as queued ops — ring 1 at city, ring 2 at metropolis I
        if (TIER_CLASS(st.tier) >= 2 && !(st.walls || []).some((w) => w.ring === 1)) { const n = queueWall(s, st, 1); if (n) marks.push(`city wall staked (${n} cells)`); }
        if (TIER_CLASS(st.tier) >= 3 && !(st.walls || []).some((w) => w.ring === 2)) { const n = queueWall(s, st, 2); if (n) marks.push(`second wall staked (${n} cells)`); }
      } else if (st.tier === "city" && !st.wall) { const n = buildWall(dim, s, st); if (n) marks.push(`city wall raised (${n} blocks)`); }
      return false;
    case 5:
      if (ti >= 1 && !st.docks) { if (buildDocks(dim, st, siteOf(st))) marks.push("a pier at the water"); }
      return false;
    default:
      if (marks.length) { st.log.push(`day ${s.simDays.toFixed(0)}: ${marks.join("; ")}`); events.push(`§6${st.name}: ${marks.join("; ")}`); }
      return true;
  }
}
function livingMarks(s, st, events) { const mk = marksCursor(s, st); while (!marksStep(s, st, mk, events)); }

function closeShop(s, st, events) {
  const open = plotsOf(s, st).filter((b) => b.stage >= 4 && !b.closed && SHOPS.includes(short(b)));
  if (!open.length) return;
  const b = open[Math.floor(rng((st.seed + s.simDays * 31) >>> 0)() * open.length)];
  b.closed = true;
  b.pending.push("close");
  st.log.push(`day ${s.simDays.toFixed(0)}: ${short(b)} closed`);
  events.push(`§c${st.name}: ${short(b)} CLOSED`);
}

function reopenShop(s, st, events) {
  const closed = plotsOf(s, st).filter((b) => b.closed);
  if (!closed.length) return false;
  const b = closed[0];
  b.closed = false;
  b.pending.push("reopen");
  st.log.push(`day ${s.simDays.toFixed(0)}: ${short(b)} reopened`);
  events.push(`§a${st.name}: ${short(b)} REOPENED`);
  return true;
}

function shopsOf(s, st) {
  return plotsOf(s, st).filter((b) => b.stage >= 4).map((b) => ({ id: b.id, kind: short(b), stations: BUILDINGS[b.family].work || 1, closed: !!b.closed }));
}

/** the settlers' wagons (D-C534 §4): the founding plots' walls, roofs and furnishings + 20 %, food for 20 days, and the
 *  founding purse — the foundations' stone is dug on site (s0 costs labour only) */
function genesisStock(s, st) {
  const L = st.ledger;
  const need = {};
  const fams = plotsOf(s, st).map((b) => b.family);
  for (const nm of st.leftover || []) { const sk = skinsOf(nm); if (sk.length) fams.push(familyOf(nm, sk[0])); }   // 0.0.25f: the plan's waiting plots too
  for (const fam of fams) {
    const bom = (BUILDINGS[fam] && BUILDINGS[fam].bom) || [];
    for (let k = 1; k < bom.length; k++) for (const [m, n] of Object.entries(bom[k])) need[m] = (need[m] || 0) + n;
  }
  for (const b of plotsOf(s, st)) if (b.land && b.land.kind === "plateau") { need.stone = (need.stone || 0) + (b.land.stone || 0); need.iron = (need.iron || 0) + (b.land.iron || 0); }   // 1.3.230 (PL)
  for (const [m, n] of Object.entries(need)) if (ECON.MATS.includes(m)) L.stock[m] = (L.stock[m] || 0) + Math.ceil(n * 1.2);
  const pop = population(s, st);
  L.stock.bread += pop * 20; L.stock.meat += pop * 10; L.stock.grain += pop * 10;
  const purse = 1500 * ECON.COIN;
  L.treasury += purse; L.minted += purse;
  st.log.push(`day ${s.simDays.toFixed(0)}: the settlers' wagons: ${Object.entries(need).filter(([m]) => ECON.MATS.includes(m)).map(([m, n]) => `${Math.ceil(n * 1.2)} ${m}`).join(", ")}, food for 20 days, a purse of 1500 coins`);
}
/** a stage's bill (the foundations' stone is dug on site) */
function stageBillOf(b, k) {
  const bom = BUILDINGS[b.family].bom || [];
  const bill = ECON.stageBill(bom, k);
  if (k === 0) { bill.mats = {}; }
  // 1.3.230 (PL): a plateau's walls, clad faces, gutter and grate (stone, iron) and its earthwork (labourer days) are paid
  // with the plot's first paid stage
  if (k === 1 && b.land && b.land.kind === "plateau") return PLAN.plateauBillInto(bill, b.land, ECON.BLOCKS_PER_BUILDER_DAY, ECON.WAGE.builder);
  return bill;
}
/** the construction demand: every waiting bill's materials, for the prices and the imports */
function constructionDemand(s, st) {
  const d = {};
  for (const b of plotsOf(s, st)) {
    if (!b.waiting) continue;
    for (const [m, n] of Object.entries(b.waiting)) if (ECON.MATS.includes(m)) d[m] = (d[m] || 0) + n;
  }
  return d;
}
/** the day's REAL production: quarries dig (stations x 24 blocks), lumberyards fell (one tree per station), farms harvest */
const accelWork = [];
let accelJobOn = false;
function queueAccelWork(st, b, kind) {
  if (accelWork.length < 64 && !accelWork.some((w) => w[1] === b.id)) accelWork.push([st.id, b.id, kind]);
  if (!accelJobOn) { accelJobOn = true; try { system.runJob(accelWorker()); } catch (e) { accelJobOn = false; console.warn(`[CIV-CLOCK] accel work: ${e}`); } }
}
function* accelWorker() {
  try {
    while (accelWork.length) {
      const [sid, bid, kind] = accelWork.shift();
      const s = load(), st = s.settlements.find((x) => x.id === sid), b = s.buildings.find((x) => x.id === bid);
      if (st && b && b.stage >= 4 && !b.closed) {
        try {
          const dim = world.getDimension(st.dim), stations = BUILDINGS[b.family].work || 1;
          timed(`accel ${kind} #${bid}`, () => {
            if (kind === "quarry") { const n = digQuarry(dim, b, st, TIER_IDX(st.tier), stations * 24); if (n !== undefined) b.spoil = (b.spoil || 0) + Math.floor(n / 4); }
            else if (kind === "lumberyard") clearForest(dim, b, st, TIER_IDX(st.tier), stations);
            else harvestFarm(dim, b, st);
          });
        } catch { /* unloaded: the abstract rate stood in */ }
      }
      yield;
    }
  } finally { accelJobOn = false; }
}
function produceDaily(s, st) {
  const out = {};
  let dim;
  try { dim = world.getDimension(st.dim); } catch { return out; }
  const real = !s.accelNow;                                          // D-C542: a real day's stone is what the hands carried in
  if (real) { st.stockedDay = Math.floor(s.simDays); try { stockCounters(s, st); } catch (e) { console.warn(`[CIV-CLOCK] counters: ${e}`); } }
  const today = st.workToday || {};
  st.workToday = {};
  // 1.3.228 (B4, his rain ruling): the quarrymen and woodcutters sheltered for `wet` of the work hours and keep half of it
  // (the dry hours' carried rate over the wet ones at RAIN.keep; mostly wet: half the abstract rate)
  const wet = real ? wetShareOf(st, true) : 0;
  if (wet > 0) { const d = diagOf(st); d.rain = { day: Math.floor(s.simDays), wet: Math.round(wet * 100) / 100 }; }
  if (real && (st.fishToday || 0) > 0) out[`fishery:${st.id}`] = st.fishToday;    // 1.3.225: the shore's real catch
  st.fishToday = 0;
  for (const b of plotsOf(s, st)) {
    if (b.stage < 4 || b.closed) continue;
    const kind = short(b);
    const stations = BUILDINGS[b.family].work || 1;
    if (real && (kind === "quarry" || kind === "lumberyard")) {
      const abs = ((ECON.PRODUCE[kind] || { out: {} }).out[ECON.REAL[kind]] || 0) * stations;
      out[b.id] = wet > 0 ? Math.round(PEOPLE.rainOutput(kind, today[b.id] || 0, wet, abs) * 10) / 10 : (today[b.id] || 0);
      continue;
    }
    // 1.3.224 (the gate's slow skipped days): a skipped day digs / fells in the world only every third day (the abstract
    // rate stands in on the others) — the scripted work was 300-500 ms of every skipped day in a town
    if ((kind === "quarry" || kind === "lumberyard") && Math.floor(s.simDays) % 3 !== b.id % 3) continue;
    // 1.3.226 (gate 225-1: 'produce' 450-520 ms inside a carried day): a skipped day's world work (the pit, the fell, the
    // harvest) runs as a background job, one workshop a step — the day's ledger takes the abstract rate meanwhile
    if (s.accelNow && (kind === "quarry" || kind === "lumberyard" || kind === "farm_wheat" || kind === "farm_terrace")) { queueAccelWork(st, b, kind); continue; }
    try {
      if (kind === "quarry") { const n = digQuarry(dim, b, st, TIER_IDX(st.tier), stations * 24); if (n !== undefined) { out[b.id] = n; b.spoil = (b.spoil || 0) + Math.floor(n / 4); } }
      else if (kind === "lumberyard") { const r = clearForest(dim, b, st, TIER_IDX(st.tier), stations); if (r && r.trees !== undefined) out[b.id] = r.logs; }
      else if (kind === "farm_wheat" || kind === "farm_terrace") harvestFarm(dim, b, st);
    } catch { /* unloaded: the abstract rate stands in */ }
    if (kind === "quarry") { try { const g = WORKMOD.regreen(dim, b, st, 8); if (g && !st.greenSaid) { st.greenSaid = true; st.log.push(`day ${s.simDays.toFixed(0)}: the quarry's spent rim is greening again (topsoil from the spoil)`); } } catch { /* unloaded */ } }
  }
  return out;
}
function stepEconomy(s, st, days, events) {
  // 1.3.228 fix (gates 228-5/9/11: a town that never built): the land survey is asynchronous since B1 (TR4), so a day could
  // step a settlement still READING its land; the settlers' wagons were then packed for zero plots (no timber, no planks)
  // and the lumberyard itself waited for timber for ever. The wagons now wait for the founding (phase "built"; a kit
  // founding never clears st.planned, so the phase alone is the test — gate 228-12 ran with no economy at all on it).
  if (!st.ledger && st.phase !== "built") return;
  if (!st.ledger) { st.ledger = ECON.newLedger(); genesisStock(s, st); }
  if (st.ledger.v !== 2) st.ledger = ECON.upgradeLedger(st.ledger);
  st.dayAcc = (st.dayAcc || 0) + days;
  while (st.dayAcc >= 1) {
    st.dayAcc -= 1;
    const L = st.ledger;
    const produced = timed(`produce ${st.id}`, () => produceDaily(s, st));
    const neighbours = (st.roads || []).map((r) => { const o = s.settlements.find((x) => x.id === r.to); return o && o.ledger ? { id: o.id, stock: o.ledger.stock, prices: o.ledger.prices, dist: r.length || 300 } : null; }).filter(Boolean);
    const inns = plotsOf(s, st).filter((b) => short(b) === "inn" && b.stage >= 4 && !b.closed).length;
    const demand = constructionDemand(s, st);
    // hiring: outsiders lodged at the inns when the waiting work exceeds five days of the town's own builders
    const queued = plotsOf(s, st).filter((b) => b.waiting).reduce((a, b) => a + (b.waiting.blocks || 0), 0);
    const own = Math.max(FOUNDERS_CREW, Math.round(population(s, st) * ECON.WORKERS_PER_PERSON) - shopsOf(s, st).length);
    L.hired = queued > own * ECON.BLOCKS_PER_BUILDER_DAY * 5 ? Math.min(10 * inns, Math.ceil(queued / (ECON.BLOCKS_PER_BUILDER_DAY * 5))) : 0;
    // 1.3.228 (B3 / BF4): each workshop's mood-tier output factor (the mean mood of its people; the fishermen's for the fishery)
    const moodBy = {};
    if (st.people) { const wm = PEOPLE.workMood(st.people); for (const [job, f] of Object.entries(wm)) moodBy[job === "fisher" ? `fishery:${st.id}` : job] = f; }
    // 1.3.228 (B7 / WE9): the waiting stage bills' materials are reserved (never sold to players or exported)
    const waitNeed = {};
    for (const b of plotsOf(s, st)) if (b.waiting) for (const [m, n] of Object.entries(b.waiting)) if (m !== "blocks" && typeof n === "number") waitNeed[m] = (waitNeed[m] || 0) + n;
    // 1.3.228 (B10 / WP1): the posts held today (the watch, the sewer keeper, the carters) are paid first
    const posts = {};
    if (st.people) for (const p of PEOPLE.alive(st.people)) if (["watch", "sewer_keeper", "carter"].includes(p.job)) posts[p.job] = (posts[p.job] || 0) + 1;
    const evs = ECON.dayStep(L, { shops: shopsOf(s, st).concat(fisheryShop(st)), population: population(s, st), households: households(s, st), inns, produced, neighbours, demand, moodBy, waitNeed, posts });
    if (L.hired) { const hw = L.hired * ECON.WAGE.hired; const paid = Math.min(L.treasury, hw); L.treasury -= paid; L.purse += paid; }
    const cap = (own + L.hired) * ECON.BLOCKS_PER_BUILDER_DAY, debt = st.buildDebt || 0;
    st.buildCap = cap; st.buildBudget = Math.max(0, cap - debt); st.buildDebt = Math.max(0, debt - cap);
    if (st.kit) deferDay(s, "sweep", () => sweepDaily(world.getDimension(st.dim), st));
    if (st.kit) deferDay(s, "canopy", () => canopyDaily(world.getDimension(st.dim), st));
    if (st.kit) deferDay(s, "headroom", () => headroomDaily(world.getDimension(st.dim), st));   // 1.3.228 (B6 / GB14): leaves / trunks over a street
    deferDay(s, "weather", () => weatherDaily(s, st));
    deferDay(s, "restore", () => restoreDaily(s, st));                                          // 1.3.230 (HD): homes moved out of / into are restored
    deferDay(s, "court", () => courtDaily(s, st));                                              // 1.3.229 (his 14:07): role beds
    if (st.kit) deferDay(s, "fillers", () => fillersDaily(s, st));                             // 1.3.228 (B6 / GB13, his 12:20): fillers only
    deferDay(s, "title", () => titleDaily(s, st, null));                                        // 1.3.228 (B9 / GB6): the town's title                                            // 1.3.228 (B6 / EN2): lived-in houses age; fines + repairs   // 1.3.227 (his 00:54 10-06): bare trunks come down   // 1004b: floating foliage (ground-connected rule) tile by tile
    if (st.kit) deferDay(s, "flood watch", () => floodWatch(world.getDimension(st.dim), st));   // 1004b: water on a street is drained and its source sealed
    deferDay(s, "census", () => censusDay(s, st, tailEvents));                  // its news joins the next advance's events
    deferDay(s, "cores", () => coreSweep(s));
    try { borderDay(s, st); if (s.accelNow && st.border && st.border.moves.some((m) => !m.done && m.blocked === null)) { for (const m of st.border.moves) if (!m.done && m.blocked === null) moveStoneNow(s, st, m); finishBorderIfDone(s, st); } } catch (e) { console.warn(`[CIV-CLOCK] border day: ${e}`); }
    if (st.kit && st.parked && st.parked.length && Math.floor(s.simDays) % PARK_DAYS === 0) { st.kitQueue = st.kitQueue || []; for (const op of st.parked.splice(0)) st.kitQueue.push(op); }   // 0.0.25b
    if (st.kit && st.phase === "built" && !(st.kitQueue || []).length) { try { const n = queueManholes(st); if (n) st.log.push(`day ${s.simDays.toFixed(0)}: ${n} manhole(s) staked in the sidewalks`); } catch (e) { console.warn(`[CIV-CLOCK] manholes: ${e}`); } }
    try { nameTrades(s, st); noticeBoard(world.getDimension(st.dim), st); } catch (e) { console.warn(`[CIV-CLOCK] day: ${e}`); }
    for (const e of evs) if (!e.startsWith("short")) { st.log.push(`day ${s.simDays.toFixed(0)}: ${e}`); events.push(`§6${st.name}: ${e}`); }
    // shortages: count consecutive days per good; charter the shop that makes it
    st.shortDays = st.shortDays || {};
    const shortNow = new Set((evs.find((e) => e.startsWith("short")) || "").replace("short: ", "").split(", ").map((x) => x.split(" ")[0]).filter(Boolean));
    for (const g of Object.keys(CHARTER)) {
      st.shortDays[g] = shortNow.has(g) ? (st.shortDays[g] || 0) + 1 : 0;
      if (st.shortDays[g] >= CHARTER_DAYS && !st.declining) {
        st.shortDays[g] = 0;
        const nm = CHARTER[g];
        const skins = skinsOf(nm);
        const fam = familyOf(nm, skins[Math.floor(rng((st.seed + s.simDays * 131) >>> 0)() * Math.max(1, skins.length))]);
        const nb = addPlot(s, st, fam, st.dim, 0, null);
        if (nb) { st.log.push(`day ${s.simDays.toFixed(0)}: ${g} short for ${CHARTER_DAYS} days — a ${nm} is chartered (#${nb.id})`); events.push(`§6${st.name}: ${g} short — ${nm} chartered`); }
      }
    }
    // economic closures: the ledger marked shops that sold nothing for LEAN_DAYS
    while (L.closing.length) {
      const id = L.closing.shift();
      const b = plotsOf(s, st).find((x) => x.id === id);
      if (b && !b.closed) { b.closed = true; b.pending.push("close"); st.log.push(`day ${s.simDays.toFixed(0)}: ${short(b)} (#${b.id}) closed — no sales`); events.push(`§c${st.name}: ${short(b)} closed (no sales)`); leave(s, st, events); }
    }
  }
}

function prosperityOk(st) {
  if (!st.ledger) return true;
  const p = st.ledger.prosperity.slice(-5);
  return p.length < 5 || p.reduce((a, v) => a + v, 0) / p.length >= GROWTH_PROSPERITY;
}

/** 1.3.226: one day's planning for a settlement, on the kit beat's own tick (see stepSettlementBody) */
const PLAN_BACKLOG = 4;
// 1.3.227 (gate 227-2: "plan day took 1,189 ms" — one leftover tried every search phase in one tick: slot 194 + grow
// street 300 + open lane 153 + stilts 408): a kit settlement's civic work / leftover plots are tried ONE PHASE PER TICK
// through a cursor (st.leftCursor); the day is not counted done until the cursor is finished ("more")
function planDay(s, st) {
  if (st.leftCursor) return leftoverStep(s, st);
  // a leftover plot (no room when its tier came) gets one try a day: the street grows / a side street opens / a bench
  // 0.0.25d: a civic work still without room tries first (one a day)
  if (!st.kit && st.phase === "built" && !st.tierWork && (st.civicLeft || []).length) {
    const [work, fam] = st.civicLeft[0];
    const skins = skinsOf(fam);
    const pk = rng(((st.seed || 1) + Math.floor(s.simDays) * 53) >>> 0);
    const b = addPlot(s, st, familyOf(fam, skins[Math.floor(pk() * skins.length)]), st.dim, 0, pk);
    if (b) { b.civic = work; st.civicLeft.shift(); st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${work} (#${b.id}, a ${fam.replace("_", " ")} until its own design)`); }
    else st.civicLeft.push(st.civicLeft.shift());
  }
  // the MANOR goes to the front of the leftovers (run 0.0.26: ranking every prestige and craft plot first starved the
  // founding of its farm, quarry and lumberyard — no timber, no bread, nothing built; the order of the rest is the plan's)
  // 1.3.228 (B6 / BF6): the weighted pick chooses which leftover is tried today (priority, shortage, rooms, affordability;
  // a family whose search failed rests PLAN.FAIL_COOL days) — it is moved to the front for the cursor
  if (st.leftover && st.leftover.length > 1) {
    const day = Math.floor(s.simDays);
    PLAN.pruneCool(st.failCool || {}, day);
    if (st.failCool && !Object.keys(st.failCool).length) delete st.failCool;
    let nx = null;
    try { nx = PLAN.nextLeftover(st.leftover, planCtx(s, st), day, st.failCool || {}, st.seed || 1); } catch (e) { console.warn(`[CIV-CLOCK] plan leftover: ${e}`); }
    if (nx && nx.index > 0) { const [nm] = st.leftover.splice(nx.index, 1); st.leftover.unshift(nm); }
  }
  if (st.kit && st.phase === "built" && TIERS.indexOf(st.tier) >= CENTRE_FROM && Math.floor(s.simDays) % 4 === 0 && st.centreTry !== Math.floor(s.simDays)) {
    st.centreTry = Math.floor(s.simDays);
    try { timed("centres", () => openCentres(s, st, rng(((st.seed || 1) + Math.floor(s.simDays) * 17) >>> 0), 0)); } catch (e) { console.warn(`[CIV-CLOCK] centres: ${e}`); }
  }
  // D-C534 §3: from tier town the blocks close — one cross street a day between adjacent parallel streets
  if (st.kit && st.phase === "built" && TIER_CLASS(st.tier) >= 1 && !(st.kitQueue || []).length) { try { timed("close blocks", () => closeBlocks(s, st)); } catch (e) { console.warn(`[CIV-CLOCK] blocks: ${e}`); } }
  if (st.kit) {
    if (st.phase === "built" && !st.tierWork && (st.civicLeft || []).length) { st.leftCursor = { kind: "civic", nm: st.civicLeft[0][1], work: st.civicLeft[0][0], ph: 0, q: 0 }; return "more"; }
    if (startLeftover(s, st, 0)) return "more";
    return;
  }
  // 0.0.25b: up to LEFTOVER_PER_DAY a day while room is found (the background room search opens the streets)
  for (let q = 0; q < (s.accelNow ? 1 : LEFTOVER_PER_DAY) && !st.tierWork && st.leftover && st.leftover.length && st.phase === "built"; q++) {
    const nm = st.leftover[0];
    const skins = skinsOf(nm);
    const pick = rng((st.seed + s.simDays * 31 + q * 7) >>> 0);
    const b = addPlot(s, st, familyOf(nm, skins[Math.floor(pick() * skins.length)]), st.dim, 0, pick);
    if (b) { st.leftover.shift(); st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${nm} (#${b.id})`); continue; }
    if (!(st.kitQueue || []).length && (st.benchFail === undefined || s.simDays - st.benchFail >= BENCH_WAIT)) startBenchJob(st);
    break;
  }
}
/** the leftover cursor for try number q of this day (false when there is nothing to try) */
function startLeftover(s, st, q) {
  if (q >= (s.accelNow ? 1 : LEFTOVER_PER_DAY) || st.tierWork || !st.leftover || !st.leftover.length || st.phase !== "built") return false;
  if (st.failCool && st.failCool[st.leftover[0]] > Math.floor(s.simDays)) return false;   // B6: the family at the front rests
  st.leftCursor = { kind: "left", nm: st.leftover[0], ph: 0, q };
  return true;
}
/** one search phase of the cursor's plot; "more" while phases (or more leftovers today) remain */
function leftoverStep(s, st) {
  const c = st.leftCursor;
  if (!c.family) {
    const skins = skinsOf(c.nm);
    c.family = familyOf(c.nm, PLAN.skinFor(DISTRICT[c.nm] || "homes", skins, TIER_CLASS(st.tier), (st.leftover || []).length + c.q));   // B6 (GB12)
  }
  const r = kitTryPhase(s, st, c.family, 0, c.ph);
  if (r === "next") { c.ph++; return "more"; }
  delete st.leftCursor;
  if (c.kind === "civic") {
    const head = (st.civicLeft || [])[0];
    if (r) { r.civic = c.work; if (head && head[0] === c.work) st.civicLeft.shift(); st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${c.work} (#${r.id}, a ${c.nm.replace("_", " ")} until its own design)`); }
    else if (head && head[0] === c.work) st.civicLeft.push(st.civicLeft.shift());
    return startLeftover(s, st, 0) ? "more" : undefined;
  }
  if (r) {
    if (st.leftover[0] === c.nm) st.leftover.shift();
    st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${c.nm} (#${r.id})`);
    return startLeftover(s, st, c.q + 1) ? "more" : undefined;
  }
  PLAN.rest((st.failCool = st.failCool || {}), c.nm, Math.floor(s.simDays));   // 1.3.228 (B6 / BF6): the family rests
  // D-C534 §2.3: still no room and the streets cannot grow -> look for a NEW BENCH joined by a switchback road
  if (!(st.kitQueue || []).length && (st.benchFail === undefined || s.simDays - st.benchFail >= BENCH_WAIT)) startBenchJob(st);
  return undefined;
}
function stepSettlement(s, st, days, events) { return timed(`settlement ${st.id} step`, () => stepSettlementBody(s, st, days, events)); }
function stepSettlementBody(s, st, days, events) {
  const age = s.simDays - st.founded;
  timed(`economy ${st.id}`, () => stepEconomy(s, st, days, events));   // 1.3.224: named so a slow day says which part
  if (st.kit && (!s.accelNow || Math.floor(s.simDays) % 3 === 0)) { try { timed("fishery", () => fisheryDay(s, st)); } catch (e) { console.warn(`[CIV-CLOCK] fishery: ${e}`); } }   // 1.3.225: the shore survey (real days; 1.3.228: FISH_CALL now, the rest on the heartbeat)
  if (st.palacePending && !st.palace) { try { placePalace(s, st, world.getDimension(st.dim)); } catch (e) { console.warn(`[CIV-CLOCK] palace retry: ${e}`); } }
  else if (st.kit && !st.palace) { try { timed("palace reserve", () => reservePalaceLand(s, st, world.getDimension(st.dim))); } catch (e) { console.warn(`[CIV-CLOCK] palace reserve: ${e}`); } }   // 1.3.226: the crown's land, from town III   // 1.3.221: until the site's chunks are loaded
  { const wetPieces = s.buildings.filter((pb) => pb.palace && pb.settlement === st.id && pb.palaceDrain > 0);
    // 1.3.224: never during skipped days (a skip stacked one job per day — his Hang), never two jobs for one group
    const grp = wetPieces.length ? wetPieces[0].palace.group : null;
    if (wetPieces.length && !s.accelNow && !palacePumpJobs.has(grp)) { try { const pd = BUILDINGS[wetPieces[0].family]; for (const pb of wetPieces) { pb.palaceDrain -= 1; const [pfx, , pfz] = footprint(pd, pb.rot); ensureTicking(s, st, [pb.x - 8, pb.z - 8, pb.x + pfx + 7, pb.z + pfz + 7], `palace pumps #${pb.id}`); }
      palacePumpJobs.add(grp);
      system.runJob((function* () { try { yield* palaceDrainJob(world.getDimension(st.dim), wetPieces, pd); } finally { palacePumpJobs.delete(grp); } })()); } catch (e) { palacePumpJobs.delete(grp); console.warn(`[CIV-CLOCK] palace pumps: ${e}`); } } }   // 1.3.221: the pumps (build 20: the whole group in one job, its chunks held — /fill needs them loaded)
  // 1.3.226 (gate 225-1: a carried day of 1.2-2.0 s — the plot searches inside it): the day's PLANNING (civic works,
  // leftover plots, neighbourhood centres, block closing) runs on its own beat (planDay), never in the day's tick
  if (st.kit) st.planDays = Math.min(PLAN_BACKLOG, (st.planDays || 0) + 1);
  if (st.ledger && st.ledger.day > 0) { maybeFoundDaughter(s, st, events); tradeAlong(s, st, events); }
  if (st.roadPending && st.daughter && st.daughter.id) {
    const child = s.settlements.find((x) => x.id === st.daughter.id);
    if (child && child.phase === "built" && (st.roadTries || 0) < ROAD_TRIES) { try { startRoadJob(s, st, child); } catch (e) { console.warn(`[CIV-CLOCK] road: ${e}`); } }
  }
  if (st.declining) {
    st.declineDays = (st.declineDays || 0) + days;
    while (st.declineDays >= DECLINE_DAYS) { st.declineDays -= DECLINE_DAYS; closeShop(s, st, events); leave(s, st, events); }
    return;
  }
  const next = TIERS[TIERS.indexOf(st.tier) + 1];
  const works = civicWorks(s, st);
  if (next && works.missing.length && age >= TIER_DAYS[next] && (!st.worksSaid || s.simDays - st.worksSaid > 30)) { st.worksSaid = s.simDays; st.log.push(`day ${s.simDays.toFixed(0)}: ${TIER_LABEL[next]} waits for the town's works: ${works.missing.join(", ")}`); }
  if (next && !st.tierWork && st.phase !== "reading" && plotsOf(s, st).length > 0 && age >= TIER_DAYS[next] && allRoofed(s, st) && prosperityOk(st) && moodOk(st) && !works.missing.length) {
    if (representationOk(s, st, next)) tierUp(s, st, next, events);
    else if (!st.repWaitLogged || s.simDays - st.repWaitLogged > 30) {
      const r = representation(s, st), q = REP_REQ[next];
      st.repWaitLogged = s.simDays;
      st.log.push(`day ${s.simDays.toFixed(0)}: ${TIER_LABEL[next]} needs ${q[0]} settlements represented here (${q[1]} cities, ${q[2]} metropolises) — has ${r.n} (${r.cities} cities, ${r.metropolises} metropolises)${r.names.length ? `: ${r.names.join(", ")}` : ""}`);
    }
  }
}

/** the closed / reopened marks: cobwebs in the doorway + the station markers removed (reopen = re-place the furnished stage). */
function applyShopMark(b, mark) {
  const def = BUILDINGS[b.family];
  const dim = world.getDimension(b.dim);
  const [sx, , sz] = def.size;
  // the door: the datum marker's cell (x 0, feet 0, z) is the doorway
  const door = def.door || [0, 0, Math.floor(sz / 2)];
  const [ox, oz] = rotXZ(door[0], door[2], sx, sz, b.rot);
  const at = { x: b.x + ox, y: b.y + def.datum_y, z: b.z + oz };
  if (mark === "close") {
    try { dim.getBlock(at)?.setType("minecraft:web"); dim.getBlock({ ...at, y: at.y + 1 })?.setType("minecraft:web"); } catch { /* unloaded */ }
    const [fx, sy, fz] = footprint(def, b.rot);
    try {
      for (const e of dim.getEntities({ location: { x: b.x, y: b.y, z: b.z }, volume: { x: fx, y: sy, z: fz } }))
        if (e.typeId === "pw:marker" && e.hasTag("civ:station")) e.remove();
    } catch { /* left */ }
    return true;
  }
  // reopen: the furnished stage back (door, stations) — clear the webs first
  try { dim.getBlock(at)?.setType("minecraft:air"); dim.getBlock({ ...at, y: at.y + 1 })?.setType("minecraft:air"); } catch { /* unloaded */ }
  return placeStage(b, def.stages - 1);
}

// 1.3.227 (gate 227-2: a carried day of 1,348 ms — several stage placements and their furniture turns in one tick): the
// placements of one call share FLUSH_MS; what is left stays pending, in order, and a 5-tick beat places it
const FLUSH_MS = 200;
let flushLeft = false;
// 1.3.228 (B1 / BF1): the flush is a heartbeat slot (7, 17: every 10 ticks, was 5); FLUSH_MS stays its budget
HB.register("flush", { fn: () => { if (flushLeft) { flushLeft = false; try { flushPending(); } catch (e) { console.warn(`[CIV-CLOCK] flush: ${e}`); } } } });
function flushPending() {
  const s = load();
  const tf0 = Date.now();
  let palacePlaced = false;                                                       // 1.3.221: one palace piece per beat
  for (const b of s.buildings) {
    if (b.palace && palacePlaced) continue;
    while (b.pending.length) {
      if (Date.now() - tf0 > FLUSH_MS) { flushLeft = true; return; }
      const k = b.pending[0];
      if (b.palace && palacePlaced) break;
      if (b.palace && typeof k !== "string") palacePlaced = true;
      const ok = typeof k === "string" ? applyShopMark(b, k) : placeStage(b, k);
      if (!ok) {
        // D-C542: a stage that cannot be placed because its chunks sleep asks for a ticking area (after a few beats)
        b.sleeps = (b.sleeps || 0) + 1;
        if (b.sleeps >= 20 && b.settlement !== undefined) {
          b.sleeps = 0;
          const st = s.settlements.find((x) => x.id === b.settlement);
          const def = BUILDINGS[b.family];
          if (st && def) { try { ensureTicking(s, st, [b.x - 8, b.z - 8, b.x + def.size[0] + 8, b.z + def.size[2] + 8], `${short(b)} #${b.id}`); } catch (e) { console.warn(`[CIV-CLOCK] stage wake: ${e}`); } }
        }
        break;
      }
      b.sleeps = 0;
      b.pending.shift();
    }
  }
}

const short = (b) => BUILDINGS[b.family].stem.replace(/^mvv_/, "").replace(/_[a-z]_r1$/, "");      // cottage_s (skin dropped)
const skinOf = (b) => (BUILDINGS[b.family].stem.match(/_([a-z])_r1$/) || [, "a"])[1];

// 1.3.228 (B1 / BF1): the clock is the heartbeat's slot 0 (every 40 ticks; the dispatcher times it — no prof wrapper)
HB.register("clock", { fn: () => {
  const s = load();
  lastMainTick = system.currentTick;
  if (system.currentTick % 100 === 0) {                                               // 1.3.222: older finished buildings get their pictures, one per sweep (1.3.224: 8 a sweep, every 100 ticks; 1.3.228: slot 0 of 40 -> every 200 ticks)
    for (const b of s.buildings) {
      const def = BUILDINGS[b.family];
      if (!def || b.artDone || b.stage < def.stages - 1 || b.pending.length || !(def.art || []).length) continue;
      try { const dim = world.getDimension(b.dim); if (!blockAt(dim, b.x, b.y + def.datum_y, b.z)) continue; const nh = GALLERY.hangBuilding(dim, b, def, Math.floor(s.simDays)); if (nh || b.artDone) save(); }
      catch (e) { console.warn(`[GALLERY] sweep #${b.id}: ${e}`); }
      break;
    }
  }
  const now = worldDays();
  let d = now - s.lastWorld;
  s.lastWorld = now;
  if (d < 0) d = 0;                                     // time set backwards: the village does not un-build
  if (!s.paused && d > 0) timed("advance", () => advance(d * s.speed));
  else if (s.buildings.some((b) => b.pending.length)) { flushPending(); save(); }
  else if (d > 0) save();
} });

// v1.3.219: the kit queue (street pieces, bridges, outfalls) and the park run on their own short beat
let kitOpsSinceSave = 0;
const LAG_EVERY = 10;                                 // 1.3.224: a carried (skipped) day every 10 ticks, never in the main beat's tick
let lastMainTick = -1e9, lastLagTick = -1e9;
// 1.3.228 (B1 / BF1): the kit queue takes the even slots but 0 and 10 (the clock, the bodies cache); halved when shedding
HB.register("kitqueue", { fn: () => {
  const s = load();
  const t = system.currentTick;
  const tw = s.settlements.find((x) => x.tierWork);
  if (tw) { if (t - lastMainTick >= 2) { try { const tt0 = Date.now(); tierWorkStep(s, tw); const tms = Date.now() - tt0; if (tms > SLOW_MS) console.warn(`[CIV-CLOCK] slow: tier work (${tierStepLabel}) took ${tms} ms`); } catch (e) { console.warn(`[CIV-CLOCK] tier work: ${e}`); delete tw.tierWork; } } return; }   // 1.3.224: a tier's plots, one per beat, before anything else
  if (s.lag > 0 && t - lastMainTick >= 2 && t - lastLagTick >= LAG_EVERY) { lastLagTick = t; try { timed("lag slice", () => advance(0, 1)); } catch (e) { console.warn(`[CIV-CLOCK] lag slice: ${e}`); } return; }
  { const pst = t - lastMainTick >= 2 && t - lastLagTick >= 2 ? s.settlements.find((x) => (x.planDays || 0) > 0) : null;   // 1.3.226: the day's planning, its own tick
    if (pst) { let more = false; try { more = timed(`plan day ${pst.id}${pst.leftCursor ? ` (${pst.leftCursor.nm} phase ${pst.leftCursor.ph})` : ""}`, () => planDay(s, pst)) === "more"; } catch (e) { console.warn(`[CIV-CLOCK] plan day: ${e}`); delete pst.leftCursor; } if (!more) pst.planDays--; return; } }   // one carried day per LAG_EVERY ticks (a paused clock still owes its skipped days)
  const busy = s.settlements.some((x) => x.kit && ((x.kitQueue && x.kitQueue.length) || (x.park && !x.park.done)));
  if (!busy) return;
  const kq0 = Date.now();
  const n = timed("kit queue", () => processKitQueue(s));
  if (Date.now() - kq0 > SLOW_MS) console.warn(`[CIV-CLOCK] slow kit ops: ${kitOpTimes.filter((x) => x[1] > 20).map(([l, ms]) => `${l} ${ms} ms`).join(", ")}`);
  for (const st of s.settlements) if (st.park && !st.park.done && !(st.kitQueue && st.kitQueue.length)) { try { timed("park", () => layPark(st)); } catch (e) { console.warn(`[CIV-CLOCK] park: ${e}`); } }
  kitOpsSinceSave += n;
  if (kitOpsSinceSave >= 15 || !s.settlements.some((x) => x.kitQueue && x.kitQueue.length)) { kitOpsSinceSave = 0; save(); }
} });

function say(p, msg) {
  try { p.sendMessage(msg); } catch { /* left */ }
}

function status(p) {
  const s = load();
  say(p, `§e[CLOCK] village day ${s.simDays.toFixed(2)} · speed ${s.speed}x · ${s.paused ? "§cPAUSED" : "§arunning"}§e · ` +
    `world day ${worldDays().toFixed(2)} · ${s.buildings.length} building(s) · ${s.settlements.length} settlement(s)`);
  // 1.3.228 (B1 / EN4 + BF1): the engine's own costs — thrown reads, the dynamic-property bytes, the heartbeat
  { const hb = HB.stats(); say(p, `§7  engine throws ${ENGINE.throws} · dynamic properties ${s.dpBytes ?? "?"} B (state ${s.bytes ?? "?"} chars) · heartbeat MSPT ${hb.msptNow ?? "?"}${hb.shed ? " §cSHEDDING§7" : ""} · worst beat tick ${hb.worstMs} ms`); }
  // 1.3.228 (B2): the last save (sections written of all), the trees refused / felled
  { const sv = SAVER.stats(), l = sv.last; say(p, `§7  last save: ${l ? `${l.wrote}/${l.of} sections, ${l.chars} of ${l.total} chars` : "none yet"}${saveHold ? " §cHELD§7" : ""} · trees felled ${FELL.felled} · refused: player logs ${FELL.placed}, bare ${FELL.bare}, at the fell ${FELL.refusedAtFell}`); }
  for (const st of s.settlements) {
    const plots = plotsOf(s, st);
    const next = TIERS[TIERS.indexOf(st.tier) + 1];
    const when = next ? ` · next ${next} at age ${TIER_DAYS[next]} (age ${(s.simDays - st.founded).toFixed(1)}${allRoofed(s, st) ? "" : ", waiting for roofs"})` : "";
    say(p, `§b  ${st.name} at ${st.x0} ${st.z0}: ${tierLabel(st).toUpperCase()} · ${plots.length} plots (${plots.filter((b) => b.closed).length} closed) · ` +
      `${population(s, st)} people · ${st.streets.length} street(s)${st.declining ? " · §cDECLINING" : ""}§b${when}`);
    if (st.kit) say(p, `§a    kit streets: ${st.streets.filter((x) => x.kind === "kit").map((x) => `#${x.id} ${x.role} ${x.H.length} cells`).join(", ")} · width ${st.width === "t" ? "town (7)" : "village (5)"} · ` +
      `${(st.kitQueue || []).length} piece(s) queued, ${st.kitLaid || 0} laid · leaves cleared ${st.leafSwept || 0}${st.park ? ` · park ${st.park.done ? "laid" : "staked"}` : ""}`);
    // 1.3.224 (his 16:50: he never found the palace): the tier work and the palace, in the settlement's own lines
    if (st.tierWork) say(p, `§b    laying out ${TIER_LABEL[st.tierWork.tier] || st.tierWork.tier}: ${st.tierWork.i}/${st.tierWork.items.length} plots${st.tierWork.i >= st.tierWork.items.length ? ` · then ${st.tierWork.after.join(", ")}` : ""}`);
    if (st.palace) { const pcs = s.buildings.filter((x) => x.palace && x.palace.group === st.palace.group); const stg = pcs.length ? Math.min(...pcs.map((x) => x.stage)) : 0;
      say(p, `§6    PALACE: centre §e${st.palace.x0 + 64} ${st.palace.H} ${st.palace.z0 + 64}§6 (${palaceDir(st, st.palace)} of the square) · ${STAGE_NAMES[Math.max(0, stg)]}${stg < 4 ? ` · ${pcs.filter((x) => x.pending.length).length} quarter(s) waiting for their chunks` : ""}`); }
    else if (st.palaceReserve) { const r = st.palaceReserve; say(p, `§6    PALACE: the crown has RESERVED its land — centre ${r.x0 + 64} ${r.H} ${r.z0 + 64}, ${palaceDir(st, r)} of the square; it is laid at city II`); }
    else if (st.palacePending || st.palaceSearch) { const ps = st.palaceSearch || {}; say(p, `§6    PALACE: the crown's surveyors are measuring sites 110–320 blocks out (${ps.days || 0} day(s), ${ps.loaded || 0} site(s) measured${ps.best ? `, best so far ${ps.best[0] + 64} ${ps.best[1] + 64} (relief ${ps.best[2]})` : ""})`); }
    if (st.why) say(p, `§7    why: ${Object.entries(st.why).map(([k, n]) => `${k} ${n}`).join(" · ")}`);   // 1.3.228 (B2 / BF3)
    if (st.roads && st.roads.length) say(p, `§d    roads: ${st.roads.map((r) => `to #${r.to} (${r.length} cells)`).join(", ")}${st.mother ? ` · daughter of #${st.mother}` : ""}`);
    if (st.ledger) say(p, `§7    treasury ${Math.floor(st.ledger.treasury / ECON.COIN)} coin · purse ${Math.floor((st.ledger.purse || 0) / ECON.COIN)} · builders ${st.ledger.builders || 0}${st.ledger.hired ? ` (+${st.ledger.hired} hired)` : ""} · fed ${Math.round((st.ledger.prosperity.slice(-1)[0] || 0) * 100)} % · ` +
      ECON.GOODS.map((g) => `${g} ${Math.floor(st.ledger.stock[g])}@${st.ledger.prices[g]}p`).join(" "));
  }
  for (const b of s.buildings) {
    const last = BUILDINGS[b.family].stages - 1;
    const name = b.stage < 0 ? `waiting (starts in ${b.delay.toFixed(2)} day(s))` : STAGE_NAMES[b.stage];
    const left = b.stage >= 0 && b.stage < last ? ` · next in ${((b.palace ? PALACE_STAGE_DAYS : STAGE_DAYS)[b.stage] - b.progress).toFixed(2)} day(s)` : "";   // 1.3.224: the palace's own calendar
    const wait = b.pending.length ? ` · §6waiting to place ${b.pending.map((k) => STAGE_NAMES[k]).join(", ")} (chunk not loaded)§7` : "";
    const where = b.settled === false ? `${b.x} ? ${b.z}` : `${b.x} ${b.y + BUILDINGS[b.family].datum_y} ${b.z}`;
    say(p, `§7  #${b.id} ${short(b)}/${skinOf(b)} (${ROTS[b.rot]}) at ${where}: ${name}${b.closed ? " §cCLOSED§7" : ""}${left}${wait}`);
  }
}

function familyOf(fam, skin) {
  // "cottage_s" -> pw:mvv_cottage_s_<skin or a>_r1; "cottage_s_b" -> that skin; a full id is taken as is
  if (!fam) return "pw:mvv_cottage_s_a_r1";
  let f = fam.includes(":") ? fam : `pw:${fam}`;
  if (BUILDINGS[f]) return f;
  const short = fam.replace(/^pw:/, "");
  const withSkin = `pw:mvv_${short}_r1`;                                   // "cottage_s_b"
  if (BUILDINGS[withSkin]) return withSkin;
  if (skin && BUILDINGS[`pw:mvv_${short}_${skin}_r1`]) return `pw:mvv_${short}_${skin}_r1`;
  return `pw:mvv_${short}_a_r1`;
}

/** the skins a building exists in (a, b, c, d …) */
function skinsOf(short) {
  return ["a", "b", "c", "d"].filter((k) => BUILDINGS[`pw:mvv_${short}_${k}_r1`]);
}

/** a small deterministic generator (mulberry32) so a village re-laid from the same corner looks the same */
function rng(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

function rotOf(r) {
  if (r === undefined) return 0;
  const n = ROTS.indexOf(r) >= 0 ? ROTS.indexOf(r) : ({ 0: 0, 90: 1, 180: 2, 270: 3 })[r];
  return n === undefined ? -1 : n;
}

/** the village: plots on both sides of an east-west street whose west end is (x0, z0). */
function layVillageOn(s, st, dimId, x0, z0, seedN) {
  const made = [];
  const pick = rng(seedN);
  let k = 0;
  const row = (list, north) => {
    let x = x0;
    for (const nm of list) {
      const skins = skinsOf(nm);
      const family = familyOf(nm, skins[Math.floor(pick() * skins.length)]);   // every plot picks its own skin
      const def = BUILDINGS[family];
      const rot = north ? 3 : 1;
      const [fx, , fz] = footprint(def, rot);
      const z = north ? z0 - fz : z0 + STREET_W;
      const bld = { id: s.nextId++, family, dim: dimId, x, y: 0, z, rot, settled: false, stage: -1, progress: 0,
                    delay: k * VILLAGE_STAGGER, pending: [], street: [x - 1, x + fx - 1, z0], settlement: st.id };
      if (bld.delay === 0) { bld.stage = 0; bld.pending.push(0); }
      s.buildings.push(bld);
      made.push(bld);
      x += fx + 1;
      k++;
    }
    const street = st.streets[0];
    if (north) street.xn = x; else street.xs = x;
  };
  // alternate sides in the build order: the street fills from the west on both sides
  row(VILLAGE_NORTH, true);
  const nNorth = made.length;
  k = 0;
  row(VILLAGE_SOUTH, false);
  for (let i = 0; i < made.length; i++) {
    const order = i < nNorth ? 2 * i : 2 * (i - nNorth) + 1;
    made[i].delay = order * VILLAGE_STAGGER;
    made[i].stage = made[i].delay === 0 ? 0 : -1;
    made[i].pending = made[i].delay === 0 ? [0] : [];
  }
  return made;
}

// ------------------------------------------------------------------------------------------------ the land (step 1)
const siteCache = new Map();          // settlement id -> LAND site (the heightfield; rebuilt from the saved RLE on load)

function siteToRLE(site) {
  const runs = [];
  let last = null, n = 0;
  for (let i = 0; i < site.h.length; i++) {
    const v = site.h[i] * 2 + site.water[i];
    if (v === last) n++; else { if (n) runs.push(n > 1 ? `${last}*${n}` : `${last}`); last = v; n = 1; }
  }
  runs.push(n > 1 ? `${last}*${n}` : `${last}`);
  return { x0: site.x0, z0: site.z0, w: site.w, d: site.d, rle: runs.join(",") };
}

function siteFromRLE(r) {
  const site = LAND.makeSite(r.x0, r.z0, r.w, r.d);
  let i = 0;
  for (const run of r.rle.split(",")) {
    const [v, n] = run.split("*").map(Number);
    const cnt = n || 1;
    for (let k = 0; k < cnt; k++, i++) { site.h[i] = Math.floor(v / 2); site.water[i] = v & 1; }
  }
  return site;
}

const SITE_KEY = "pw:civ_site:";          // the site field lives in its own dynamic properties (30,000 chars each; the state's 32 KB is for the town)
const SITE_CHUNK = 30000;
function saveSite(id, r) {
  const txt = JSON.stringify(r);
  const n = Math.ceil(txt.length / SITE_CHUNK);
  for (let i = 0; i < n; i++) world.setDynamicProperty(`${SITE_KEY}${id}:${i}`, txt.slice(i * SITE_CHUNK, (i + 1) * SITE_CHUNK));
  world.setDynamicProperty(`${SITE_KEY}${id}`, String(n));
}
function siteOf(st) {
  if (siteCache.has(st.id)) return siteCache.get(st.id);
  try {
    const n = Number(world.getDynamicProperty(SITE_KEY + st.id) || 0);
    if (n > 0) {
      let txt = "";
      for (let i = 0; i < n; i++) txt += world.getDynamicProperty(`${SITE_KEY}${st.id}:${i}`) || "";
      const site = LAND.siteDecode(JSON.parse(txt)); siteCache.set(st.id, site); return site;   // 1.3.231: "d1" or the old runs
    }
  } catch { /* none */ }
  return null;
}

/** read the land around (cx, cz) into a site field, spread over ticks (a generator for system.runJob). Columns whose
 *  chunk is not loaded stay unknown (-1): the plan treats them as outside. SITE_R = 80 -> 160 x 160 (the ticking law). */
const SITE_R = 80;
function* readSiteJob(st, cx, cz, dimId, onDone) {
  const dim = world.getDimension(dimId);
  const site = LAND.makeSite(cx - SITE_R, cz - SITE_R, 2 * SITE_R, 2 * SITE_R);
  let n = 0, known = 0;
  for (let x = cx - SITE_R; x < cx + SITE_R; x++) {
    for (let z = cz - SITE_R; z < cz + SITE_R; z++) {
      let top;
      top = topAt(dim, x, z);
      if (top) {
        let water = false, g;
        try {
          let b = top, by = top.location.y;
          for (let i = 0; b && i < 48; i++) {
            if (b.typeId === "minecraft:water" || b.typeId === "minecraft:flowing_water") { water = true; }
            if (isGround(b.typeId) && b.typeId !== "minecraft:water") { g = by; break; }
            by--;
            b = blockAt(dim, x, by, z);                              // 1.3.227: not b.below() (leaks server memory)
          }
        } catch { g = undefined; }
        if (g !== undefined) { site.set(x, z, g, water); known++; }
      }
      if (++n % 512 === 0) yield;
    }
  }
  st.siteKnown = known;
  if (known < site.h.length * 0.5 && (st.siteTries || 0) < 40) {
    // the land is mostly unloaded (a daughter site far from the player): read again later, when someone is near
    st.siteTries = (st.siteTries || 0) + 1;
    st.phase = "reading";
    system.runTimeout(() => { try { system.runJob(readSiteJob(st, cx, cz, dimId, onDone)); } catch (e) { console.warn(`[CIV-CLOCK] site retry: ${e}`); } }, 400);
    return;
  }
  siteCache.set(st.id, site);
  try { saveSite(st.id, LAND.siteEncode(site)); } catch (e) { console.warn(`[CIV-CLOCK] site save failed: ${e}`); }   // 1.3.231: "d1" text (~half)
  onDone(site);
}

// 1.3.231 (CIV-LAND) THE WIDE SURVEY (his 00:23 10-07: "survey a MUCH larger area and plan for elevation"): once a kit
// settlement stands, its field grows to LAND.wideRadius(border) around the square (192 = 384 x 384 for a village; more as
// the stones move out) in the background — LAND.wideSurveyPass (tests/test_survey.mjs): tiles of 128 x 128 nearest first; a
// loaded tile is read at once, a sleeping one is held awake by ONE ticking area (only when a slot is FREE — town work is
// never evicted for it) and released after its read; passes WIDE_PAUSE ticks apart. The founding's own cells are kept.
// The new field replaces the old in one step (siteCache + saveSite), so every planner sees one field or the other.
const WIDE_PAUSE = 100;
const wideJobs = new Map();                                     // settlement id -> survey progress (memory; a restart starts over)
/** one column for the field, as readSiteJob reads it: { g, water } (the bed under water), null asleep, undefined no ground */
function siteColumn(dim, x, z) {
  const top = topAt(dim, x, z);
  if (!top) return null;
  try {
    let water = false, b = top, by = top.location.y;
    for (let i = 0; b && i < 48; i++) {
      if (b.typeId === "minecraft:water" || b.typeId === "minecraft:flowing_water") water = true;
      if (isGround(b.typeId) && b.typeId !== "minecraft:water") return { g: by, water };
      by--;
      b = blockAt(dim, x, by, z, true);                         // the column is loaded (topAt asked): no throw, no below()
    }
  } catch { ENGINE.throws++; return null; }
  return undefined;
}
/** the radius the settlement's field should now reach (0 = it does) */
function wideNeed(s, st) {
  if (!st.kit || st.phase !== "built" || !st.square || !siteOf(st)) return 0;
  const R = LAND.wideRadius(st.border ? st.border.r : 0);
  const w = st.wide;
  if (!w || w.R < R) return R;
  if (w.skipped && Math.floor(s.simDays) - w.day >= 3) return R;   // the tiles that never woke get another look
  return 0;
}
function startWideSurvey(s, st) {
  const R = wideNeed(s, st);
  if (!R || wideJobs.size) return false;                        // one survey at a time in the world
  const [cx, cz] = squareCentre(st);
  const dim = world.getDimension(st.dim);
  const prog = LAND.wideProgress(siteOf(st), cx, cz, R);
  wideJobs.set(st.id, prog);
  st.log.push(`day ${s.simDays.toFixed(0)}: the surveyors set out to read the land ${R} blocks around the square (${prog.tiles.length} tiles of ${LAND.WIDE.tile})`);
  const io = {
    loaded: (t) => boxLoaded(dim, t[0], t[1], t[2], t[3]),
    column: (x, z) => siteColumn(dim, x, z),
    hold: (t) => {
      const s2 = load(), T = coreState(s2);
      if (Object.keys(T.areas).length >= T.slots) return null;  // no free slot: wait (the town's work keeps its areas)
      const before = new Set(Object.keys(T.areas));
      const nm = ensureTicking(s2, st, t, "land survey");
      return nm ? { name: nm, mine: !before.has(nm) } : null;
    },
    release: (h) => { if (h && h.mine) releaseTicking(load(), h.name); },
  };
  const pass = () => {
    function* job() {
      let res;
      try { res = yield* LAND.wideSurveyPass(prog, io); } catch (e) { console.warn(`[CIV-CLOCK] wide survey: ${e}`); wideJobs.delete(st.id); return; }
      if (res === "wait") { system.runTimeout(pass, WIDE_PAUSE); return; }
      wideDone(st.id, prog);
    }
    try { system.runJob(job()); } catch (e) { wideJobs.delete(st.id); console.warn(`[CIV-CLOCK] wide survey job: ${e}`); }
  };
  pass();
  return true;
}
function wideDone(stId, prog) {
  wideJobs.delete(stId);
  const s = load(), st = s.settlements.find((x) => x.id === stId);
  if (!st) return;
  siteCache.set(st.id, prog.site);
  try { saveSite(st.id, LAND.siteEncode(prog.site)); } catch (e) { console.warn(`[CIV-CLOCK] wide site save failed: ${e}`); }
  let known = 0;
  for (let i = 0; i < prog.site.h.length; i++) if (prog.site.h[i] >= 0) known++;
  st.wide = { R: prog.R, day: Math.floor(s.simDays), tiles: prog.tiles.length, skipped: prog.skipped.length, known };
  st.log.push(`day ${s.simDays.toFixed(0)}: the surveyors have read the land ${prog.R} blocks around the square (${known.toLocaleString()} of ${prog.site.h.length.toLocaleString()} columns known${prog.skipped.length ? `; ${prog.skipped.length} tiles never woke` : ""})`);
  console.warn(`[CIV-SURVEY] ${JSON.stringify({ st: st.id, wide: st.wide, read: prog.read, asleep: prog.asleep, kept: prog.kept })}`);
  save();
}

/** nothing hangs over a worked cell (street, square, yard): a trunk above it is felled whole (fellTree, no stump left on
 *  the surface), dangling leaves and vines above it are cleared, up to `reach` blocks (run 0.0.15: trees stood over the
 *  granddaughter's streets with their lower trunks cut — a floating canopy and a 2-block "step" in the probe's read) */
function clearTreesOver(dim, x, z, yTop, reach = 30) {
  let n = 0;
  for (let y = yTop + 1; y <= yTop + reach; y++) {
    const blk = blockAt(dim, x, y, z);                                     // 1.3.228: guarded (a sleeping cell ends the column)
    if (!blk) return n;
    const id = blk.typeId;
    // 1.3.228 (B2 / BF10): only a real tree is felled over a worked cell; a player's logs (or a bare log pole) stay
    if (TREE_LOG(id)) { const k = fellTree(dim, x, y, z, () => false, false); if (!k) return n; n += k; continue; }
    else if (TREE_LEAF(id) || CLEAR_OVER.some((s) => id.includes(s))) { try { blk.setType("minecraft:air"); n++; } catch { /* left */ } }
  }
  return n;
}

const STREET_SURFACE = new Set(["minecraft:grass_path", "minecraft:gravel", "minecraft:cobblestone", "minecraft:spruce_planks"]);
/** a street / yard surface at y must stand on something: fill air (or water) under it down to the first solid block
 *  (at most 6 deep — a cave roof, an overhang; the lay log of 10-03: a granddaughter's path over a hollow fell as gravel) */
function supportUnder(dim, x, y, z, maxDepth = 6) {
  let n = 0;
  for (let yy = y - 1; yy >= y - maxDepth; yy--) {
    let b;
    try { b = dim.getBlock({ x, y: yy, z }); } catch { return n; }
    if (!b) return n;
    if (b.typeId !== "minecraft:air" && b.typeId !== "minecraft:water" && b.typeId !== "minecraft:flowing_water" && !NOT_GROUND.some((t) => b.typeId.includes(t))) return n;
    b.setType(FILL_IN); n++;
  }
  return n;
}

/** lay a planned street from its profile: 3 wide, cut above, filled below, path surface, a cobblestone step at each rise */
const CORRIDOR_FENCE = "minecraft:spruce_fence", CROSS_EVERY = 80, CROSS_LEN = 5, CROSS_CLEAR = 4;
function greenCorridor(dim, s, road) {
  const cells = road.cells;
  if (!cells || cells.length < 12) return { fence: 0, crossings: [] };
  // the road's body (every lay shape) and its height per cell
  const body = new Map();
  cells.forEach((c, i) => { for (const [cx, cz] of LAND.layShapes(cells, i, null)) body.set(`${cx},${cz}`, c[2]); });
  // never fence inside or next to a settlement (its streets, plots and the 3 cells around them): the channel opens there
  const near = new Set();
  for (const st of s.settlements) for (const k of kitBody(st).keys()) near.add(k);
  for (const [x0, x1, z0, z1] of plotBoxes(s, 3, null)) for (let x = x0; x <= x1; x++) for (let z = z0; z <= z1; z++) near.add(`${x},${z}`);
  for (const k of streetHeights(s).keys()) near.add(k);
  const nearAny = (x, z) => { for (let dx = -3; dx <= 3; dx++) for (let dz = -3; dz <= 3; dz++) if (near.has(`${x + dx},${z + dz}`)) return true; return false; };
  // the crossings first (their cells are not fenced on the ground: the deck carries its own)
  const crossings = [];
  let last = -CROSS_EVERY / 2;
  for (let i = 3; i + CROSS_LEN + 3 < cells.length; i++) {
    if (i - last < CROSS_EVERY) continue;
    const run = cells.slice(i - 2, i + CROSS_LEN + 2);
    const alongX = run.every((c) => c[1] === run[0][1]), alongZ = run.every((c) => c[0] === run[0][0]);
    if (!alongX && !alongZ) continue;
    const hs = run.map((c) => c[2]);
    if (Math.max(...hs) - Math.min(...hs) > 1 || run.some((c) => nearAny(c[0], c[1]))) continue;
    crossings.push({ i, along: alongX ? "x" : "z", top: Math.max(...hs) + CROSS_CLEAR + 1, cells: cells.slice(i, i + CROSS_LEN) });
    last = i;
  }
  const underDeck = new Set();
  for (const c of crossings) for (const [x, z] of c.cells) for (let k = -4; k <= 4; k++) underDeck.add(c.along === "x" ? `${x},${z + k}` : `${x + k},${z}`);
  // the fence: every ground cell 4-adjacent to the body, not body, not near a settlement, not under a deck
  let fence = 0;
  const done = new Set();
  for (const k of body.keys()) {
    const [x, z] = k.split(",").map(Number);
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx, nz = z + dz, nk = `${nx},${nz}`;
      if (body.has(nk) || done.has(nk) || nearAny(nx, nz) || underDeck.has(nk)) continue;
      done.add(nk);
      const g = groundAt(dim, nx, nz);
      if (g === undefined) continue;
      try {
        for (let y = g + 1; y <= g + 3; y++) { const b = dim.getBlock({ x: nx, y, z: nz }); if (b && (b.typeId === "minecraft:air" || !isGround(b.typeId))) b.setType(CORRIDOR_FENCE); }
        fence++;
      } catch { /* unloaded */ }
    }
  }
  // the land bridges
  for (const c of crossings) {
    const top = c.top;
    for (const [x, z] of c.cells) for (let k = -6; k <= 6; k++) {
      const cx = c.along === "x" ? x : x + k, cz = c.along === "x" ? z + k : z;
      try {
        const abut = Math.abs(k) === 3 || Math.abs(k) === 4;                 // the fence lines carry the deck: stone-brick abutments
        if (Math.abs(k) <= 4) {
          if (abut) { const g = groundAt(dim, cx, cz) ?? top - 6; for (let y = g + 1; y < top - 1; y++) dim.getBlock({ x: cx, y, z: cz })?.setType("minecraft:stone_bricks"); }
          dim.getBlock({ x: cx, y: top - 1, z: cz })?.setType("minecraft:stone_bricks");
          dim.getBlock({ x: cx, y: top, z: cz })?.setType("minecraft:grass_block");
        } else {
          // the approaches: earth falling 1 per 2 cells outward from the deck to the natural ground
          const d = Math.abs(k) - 4;
          const want = top - Math.floor(d / 2);
          const g = groundAt(dim, cx, cz);
          if (g === undefined || g >= want) continue;
          for (let y = g + 1; y < want; y++) dim.getBlock({ x: cx, y, z: cz })?.setType("minecraft:dirt");
          dim.getBlock({ x: cx, y: want, z: cz })?.setType("minecraft:grass_block");
        }
      } catch { /* unloaded */ }
    }
    // the approaches continue further out until they meet the ground (up to 12 more cells)
    for (const [x, z] of c.cells) for (const sgn of [1, -1]) for (let d = 3; d <= 14; d++) {
      const k = sgn * (4 + d);
      const cx = c.along === "x" ? x : x + k, cz = c.along === "x" ? z + k : z;
      const want = top - Math.floor(d / 2);
      try { const g = groundAt(dim, cx, cz); if (g === undefined || g >= want) break; for (let y = g + 1; y < want; y++) dim.getBlock({ x: cx, y, z: cz })?.setType("minecraft:dirt"); dim.getBlock({ x: cx, y: want, z: cz })?.setType("minecraft:grass_block"); } catch { break; }
    }
    // the deck's road-facing edges: fences 3 high (the first and last row of the crossing)
    for (const [x, z] of [c.cells[0], c.cells[c.cells.length - 1]]) {
      const sh = c.along === "x" ? (x === c.cells[0][0] ? -1 : 1) : (z === c.cells[0][1] ? -1 : 1);
      for (let k = -4; k <= 4; k++) {
        const cx = c.along === "x" ? x + sh : x + k, cz = c.along === "x" ? z + k : z + sh;
        void cx; void cz;
        const ex = c.along === "x" ? x : x + k, ez = c.along === "x" ? z + k : z;
        for (let y = top + 1; y <= top + 3; y++) { try { dim.getBlock({ x: ex, y, z: ez })?.setType(CORRIDOR_FENCE); } catch { /* left */ } }
      }
    }
  }
  return { fence, crossings: crossings.map((c) => [c.cells[0][0], c.cells[0][1], c.top, c.along]) };
}
function layPlannedStreet(dim, street) {
  let laid = 0;
  const cells = street.cells;
  const axis = street.axis || null;                                  // "x" / "z" for a settlement street; null = a road
  for (let i = 0; i < cells.length; i++) {
    const [x, z, h] = cells[i];
    if (street.skip && street.skip(x, z)) continue;                    // an existing street cell: crossed at its own grade
    const prev = i > 0 ? cells[i - 1] : null;
    const rise = prev && h > prev[2];
    const shapes = LAND.layShapes(cells, i, axis);                // body / cross / both — the lay geometry law (pw_civ_land)
    for (const [cx, cz, w, vertical] of shapes) {
      if (street.skip && street.skip(cx, cz)) continue;              // a width cell on an existing street: left at its grade
      try {
        // a cell this street already laid at this height (a jog cross overlapping a run body, or a re-lay) is LEFT ALONE:
        // the lay log of 10-03 showed a bridge deck re-laid as a "normal" cell because its own planks counted as ground
        // (g = h, drop 0): the plank became a grass path hanging over the gully, the hardening made it gravel, and gravel
        // falls — two holes in the deck (D-C509)
        const already = dim.getBlock({ x: cx, y: h, z: cz });
        if (already && STREET_SURFACE.has(already.typeId)) { laid++; continue; }
        const g = groundAt(dim, cx, cz);
        if (g === undefined) continue;
        const drop = h - g;                                              // the street floats this high above the ground here
        if (drop >= BRIDGE_DROP) {
          // a BRIDGE (step 3): a plank deck at the street's grade on log piers every PIER cells, rails on both edges
          const pier = ((vertical ? z : x) % PIER === 0) && (w === 0 || w === STREET_W - 1);
          for (let y = g + 1; y < h; y++) dim.getBlock({ x: cx, y, z: cz })?.setType(pier ? "minecraft:spruce_log" : "minecraft:air");
          dim.getBlock({ x: cx, y: h, z: cz })?.setType("minecraft:spruce_planks");
          if (w === 0 || w === STREET_W - 1) dim.getBlock({ x: cx, y: h + 1, z: cz })?.setType("minecraft:spruce_fence");
          for (let y = h + 2; y <= h + 3; y++) { const up = dim.getBlock({ x: cx, y, z: cz }); if (up && up.typeId !== "minecraft:air") up.setType("minecraft:air"); }
          clearTreesOver(dim, cx, cz, h + 3);
          laid++;
          continue;
        }
        for (let y = g + 1; y <= h; y++) dim.getBlock({ x: cx, y, z: cz })?.setType(w === 0 || w === STREET_W - 1 ? FILL_OUT : FILL_IN);
        for (let y = h + 1; y <= Math.max(g, h) + 3; y++) {
          const up = dim.getBlock({ x: cx, y, z: cz });
          if (up && up.typeId !== "minecraft:air" && up.typeId !== "minecraft:water") up.setType("minecraft:air");
        }
        const top = dim.getBlock({ x: cx, y: h, z: cz });
        if (top && top.typeId !== "minecraft:water") top.setType(rise ? FILL_OUT : "minecraft:grass_path");
        supportUnder(dim, cx, h, cz);                                    // never a surface over a hollow (a cave roof, an overhang)
        clearTreesOver(dim, cx, cz, Math.max(g, h) + 3);
        // a CUTTING (step 3): the street passes through a rise — the walls beside the outer rows are clad cobblestone
        if (g >= h + CUT_RISE && (w === 0 || w === STREET_W - 1)) {
          const ox = vertical ? cx + (w === 0 ? -1 : 1) : cx, oz = vertical ? cz : cz + (w === 0 ? -1 : 1);
          for (let y = h + 1; y <= g; y++) { const wall = dim.getBlock({ x: ox, y, z: oz }); if (wall && isGround(wall.typeId) && wall.typeId !== "minecraft:water") wall.setType(FILL_OUT); }
        }
        laid++;
      } catch { /* unloaded */ }
    }
  }
  return laid;
}

/** found a settlement on the land: read the site (a job), plan the contour street from the flattest square, lay it,
 *  then hand the plots their slots. Falls back to the straight village if the land cannot be read / planned. */
function foundSettlement(s, dimId, cx, cz, seed, reply) {
  const seedN = seed === undefined ? ((cx * 73856093) ^ (cz * 19349663)) >>> 0 : seed >>> 0;
  const st = { id: s.settlements.length + 1, name: `settlement ${s.settlements.length + 1}`, dim: dimId, x0: cx, z0: cz, seed: seedN,
               founded: s.simDays, tier: "village", tierDay: s.simDays, declining: false, declineDays: 0, log: [], streets: [],
               phase: "reading", planned: true };
  s.settlements.push(st);
  save();
  system.runJob(readSiteJob(st, cx, cz, dimId, (site) => {
    // v1.3.219 (his 17:37 / 18:01): StreetKit streets — the legacy contour street only when the kit cannot be planned here
    try { if (foundKitSettlement(s, st, site, cx, cz, seedN, reply)) return; } catch (e) {
      console.warn(`[CIV-CLOCK] kit founding: ${e} ${e.stack || ""}`);
      // review 19:1x: a kit founding that failed after it began (streets / plots made) is kept as it is — never a second,
      // legacy founding laid on top of it (kitvillage-0.0.5: both ran: two wells, two street systems)
      if (st.kit) { st.phase = "built"; st.log.push(`day ${s.simDays.toFixed(0)}: founding interrupted (${String(e).slice(0, 80)}) — kept as far as it got`); flushPending(); save(); reply(`§c[CLOCK] ${st.name}: founding interrupted (${e}); kept as far as it got`); return; }
    }
    const plan = LAND.planMainStreet(site, cx, cz, seedN);
    if (!plan) {
      st.planned = false; st.phase = "built";
      st.log.push(`day ${s.simDays.toFixed(0)}: the land could not be read here — a straight street was laid`);
      st.streets.push({ x0: cx, z0: cz, xn: cx, xs: cx, nextNorth: true });
      layVillageOn(s, st, dimId, cx, cz, seedN);
      flushPending(); save();
      reply(`§e[CLOCK] ${st.name}: site unreadable (${st.siteKnown} columns known) — straight village at ${cx} ${cz}`);
      return;
    }
    st.square = plan.square;
    st.h0 = plan.h0;
    st.profile = {};
    for (const [k, v] of plan.profile) st.profile[k] = v;
    const street = { kind: "contour", axis: plan.axis, runs: plan.runs.map((r) => ({ axis: r.axis, z: r.z, x0: r.x0, x1: r.x1, ux0: r.ux0, ux1: r.ux1, jog: r.jog })), cells: plan.cells };
    st.streets.push(street);
    const dim = world.getDimension(dimId);
    street.laid = layPlannedStreet(dim, street);
    street.nCells = street.cells.length;
    delete street.cells;                                    // laid; the profile keeps every height (the state stays small)
    paveSquare(dim, st, site);
    st.phase = "built";
    // the first plots: the roster, alternating sides from the square outward (a 90-degree rotation on an east-west run:
    // the footprint is [sz, sx])
    st.axis = plan.axis;
    const pick = rng(seedN);
    const wanted = [];
    for (const nm of VILLAGE_NORTH.concat(VILLAGE_SOUTH)) {
      const skins = skinsOf(nm);
      const family = familyOf(nm, skins[Math.floor(pick() * skins.length)]);
      wanted.push({ family, ...LAND.sizeInFrame(BUILDINGS[family]) });
    }
    const slots = LAND.slotsAlongStreet(street.runs, wanted, 1, slotFree(s, st));
    let k = 0, missed = 0;
    st.leftover = [];
    slots.forEach((slot0, i) => {
      if (!slot0) { missed++; st.leftover.push(VILLAGE_NORTH.concat(VILLAGE_SOUTH)[i]); return; }
      const slot = LAND.slotToWorld(slot0);
      const w = wanted[i];
      const bld = { id: s.nextId++, family: w.family, dim: dimId, x: slot.wx, y: 0, z: slot.wz, rot: slot.wrot, settled: false, stage: -1,
                    progress: 0, delay: k * VILLAGE_STAGGER, pending: [], street: streetOf(slot), streetAxis: slot.axis, yard: slot.yard || 0, settlement: st.id, planned: true };
      if (bld.delay === 0) { bld.stage = 0; bld.pending.push(0); }
      s.buildings.push(bld);
      k++;
    });
    st.log.push(`day ${s.simDays.toFixed(0)}: founded on the knoll at ${plan.square.x + 6} ${plan.square.z + 6} (relief ${plan.square.relief}); ` +
      `contour street at y ${plan.h0}, ${street.runs.length} run(s), ${street.nCells} cells; ${k} plots${missed ? `, ${missed} wait for a second street` : ""}`);
    st.missed = missed;
    flushPending(); save();
    reply(`§e[CLOCK] ${st.name} founded: square at ${plan.square.x + 6} ${plan.square.z + 6} (relief ${plan.square.relief}), contour street y ${plan.h0} ` +
      `with ${street.runs.length} run(s) / ${street.nCells} cells (${street.laid} blocks laid), ${k} plots staggered${missed ? `, ${missed} without room yet` : ""}`);
  }));
  return st;
}

/** the SQUARE (step 2): the knoll is levelled to its median (cut above, filled below), paved with grass path, a cobblestone
 *  border, and the well placed at its centre as a plot of the settlement (no street, no stoop). */
function paveSquare(dim, st, site) {
  const sq = st.square;
  if (!sq) return;
  const y0 = sq.y;
  let paved = 0;
  for (let i = 0; i < LAND.SQUARE; i++) for (let j = 0; j < LAND.SQUARE; j++) {
    const x = sq.x + i, z = sq.z + j;
    const border = i === 0 || j === 0 || i === LAND.SQUARE - 1 || j === LAND.SQUARE - 1;
    try {
      const g = groundAt(dim, x, z);
      if (g === undefined) continue;
      for (let y = g + 1; y <= y0; y++) dim.getBlock({ x, y, z })?.setType(border ? FILL_OUT : FILL_IN);
      for (let y = y0 + 1; y <= Math.max(g, y0) + 3; y++) { const up = dim.getBlock({ x, y, z }); if (up && up.typeId !== "minecraft:air") up.setType("minecraft:air"); }
      dim.getBlock({ x, y: y0, z })?.setType(border ? FILL_OUT : "minecraft:grass_path");
      clearTreesOver(dim, x, z, Math.max(g, y0) + 3);
      paved++;
    } catch { /* unloaded */ }
  }
  // lanterns on the four corners (a fence post with a lantern)
  for (const [i, j] of [[1, 1], [LAND.SQUARE - 2, 1], [1, LAND.SQUARE - 2], [LAND.SQUARE - 2, LAND.SQUARE - 2]]) {
    try { dim.getBlock({ x: sq.x + i, y: y0 + 1, z: sq.z + j })?.setType("minecraft:spruce_fence"); dim.getBlock({ x: sq.x + i, y: y0 + 2, z: sq.z + j })?.setType("minecraft:lantern"); } catch { /* left */ }
  }
  // the well at the centre
  const s = load();
  const family = "pw:mvv_well_a_r1";
  const def = BUILDINGS[family];
  if (def) {
    const [sx, , sz] = def.size;
    const bld = { id: s.nextId++, family, dim: st.dim, x: sq.x + (LAND.SQUARE - sx) / 2 | 0, y: y0 + 1 - def.datum_y, z: sq.z + (LAND.SQUARE - sz) / 2 | 0,
                  rot: 0, settled: true, stage: 0, progress: 0, delay: 0, pending: [0], settlement: st.id, planned: true, onSquare: true };
    s.buildings.push(bld);
  }
  st.paved = paved;
}

// ------------------------------------------------------------------------------------------------ KIT STREETS (v1.3.219)
// His 17:37 / 18:01 / 18:13 / 18:15 rulings (D-C529, D-C530): streets are laid from HIS StreetKit pieces (pw:road/v_* village
// width, t_* town width), straight, profiled by ramps (pw_civ_streets.js), houses flush on the corridor at sidewalk height
// with an access piece in front of each house's sewer shaft, dead ends at both ends whose sewer runs on to an OUTFALL
// (a framed exit with a door-sized space for his grate), plank BRIDGES with openings in the railing, side streets joined
// by T junctions, streets that grow longer as the settlement grows, and the village width resurfaced to the town width
// at tier town. Everything placed goes through st.kitQueue (one op at a time per tick, retried while its chunks sleep).
const KIT_HALF = 50;                       // the main street: 50 cells either side of the square's frontage
const KIT_SIDE_HALF = 40;                  // a side street: at least 40 cells either side of its junction (longer tried first: D-C545)
const KIT_SIDE_HALVES = [70, 55, 40];      // the halves tried for a new parallel: 70 carries the grid windows at +-56 from its junction
const STREET_CUT = 6, STREET_FILL = 6;     // D-C538 / D-C545: a street is cut or filled by at most this (0.0.14: a parallel lay 50 deep in a mountain)
const STREET_OPTS = { maxCut: STREET_CUT, maxFill: STREET_FILL, ramp8: true };   // 1.3.228: the 8-block ramp preferred (his 12:20)
const KIT_MAX_LEN = 220;                   // a street grows up to this length
const KIT_GROW = 30;                       // cells added when a street grows
const PLAN_MS = 40;
const PARK_BEATS = 600, PARK_DAYS = 3;     // 0.0.25b: a sewer op asleep this many beats waits outside the queue; queued again every PARK_DAYS
const SIDE_REST = 3;                     // 0.0.25: days a failed side-street pass rests (the stones moving lift it)
// D-C534 §2 (his C3 / C5): land preparation per plot. The plot's floor is the sidewalk level H. Over its box + 1 margin
// on the three non-street sides + the rear bench: cut = highest ground - H, fill = H - lowest ground.
const BENCH = 3;                           // the levelled bench behind every house (R1 §4.5: Inca / Cinque Terre terrace width)
const WALL_MAX = 3;                        // one retaining wall is at most 3 high; above that the face is stepped (another bench)
const CUT_MAX = 6;                         // a cut deeper than 6 (two stepped walls): no house there (the street is road only)
// 1.3.224 (his 16:50 + his answer "step, else stilts"): the ground is BUILT UP under a plot only where the drop is <= 15
// (BUILD_UP_MAX), as a STEPPED embankment (lifts of <= 3 with a cell of setback, R5); beyond that the plot slides along
// the street / tries the other streets (the land is followed), and only when no slot is found anywhere it may stand on
// stilts over a drop of <= STILTS_MAX. Ground that cannot be read is never accepted (the plot waits for its chunks).
const BUILD_UP_MAX = 15, STILTS_MAX = 24, LIFT = 3;
const PODIUM_MAX = 6, FILL_MAX = BUILD_UP_MAX;       // a drop of 3..6 shows the cellar shell as a stone podium; 6..12 = STILTS (his C5: stilted
                                           // homes off cliff faces — the box's subsurface cut away, log posts); beyond 12: no house                        // the planners' time budget per call (watchdog: 100 ms spike, 3-10 s hang)
const KIT_OPS_PER_TICK = 1;                 // review 19:1x: one op per beat (a dead end's prep reads ~10k blocks; the watchdog history says spread it)
const ROAD_W = { v: [4, 8], t: [3, 9] };   // the road's width cells (w) per width: the deck of a bridge sits one lower there
const kitBodyCache = new Map();

/** the sewer shaft's local z of a building (its ladder at x 1, y 3), or null (no cellar, no access piece) */
function shaftZOf(def) {
  if (def.shaftZ !== undefined) return def.shaftZ;
  const hit = (def.dir || []).find(([x, y, , name]) => x === 1 && y === 3 && name === "minecraft:ladder");
  def.shaftZ = hit ? hit[2] : null;
  return def.shaftZ;
}

const kitFrame = (street) => street.f;
/** a street's plan view for the pure planner: { H: [...] by index, segs } with index = t - street.tmin */
const kitPlan = (street) => ({ H: street.H, segs: street.segs });
/** H at frame t (undefined outside) */
const kitHAt = (street, t) => street.H[t - street.tmin];

/** every corridor cell of a kit settlement -> sidewalk H (main, side and connector streets) */
function kitBody(st) {
  const key = `${st.id}:${st.kitVer || 0}`;
  if (kitBodyCache.has(key)) return kitBodyCache.get(key);
  const m = new Map();
  for (const street of st.streets || []) if (street.kind === "kit") KIT.corridorCells(street.f, kitPlan(street), street.tmin, m);
  for (const k of [...kitBodyCache.keys()]) if (k.startsWith(`${st.id}:`)) kitBodyCache.delete(k);
  kitBodyCache.set(key, m);
  return m;
}
function kitTouch(st) { st.kitVer = (st.kitVer || 0) + 1; }

/** the land a planner reads: the settlement's site field where known, else the live ground (loaded chunks) */
const GROUND_CACHE_MAX = 60000;            // 1.3.224: 200k string-keyed entries were ~20 MB of the 100 MB script-memory warning
const groundCache = new Map();             // "dimId:x,z" -> ground y read live (a session cache: planners re-read the same cells hundreds of times)
function liveSite(dim, site) {
  const pre = `${dim.id}:`;
  return {
    at: (x, z) => {
      const v = site ? site.at(x, z) : undefined;
      if (v !== undefined) return v;
      const k = pre + x + "," + z;
      if (groundCache.has(k)) return groundCache.get(k);
      const g = groundAt(dim, x, z);
      if (g !== undefined) { if (groundCache.size > GROUND_CACHE_MAX) groundCache.clear(); groundCache.set(k, g); }
      return g;
    },
    isWater: (x, z) => {
      if (site && site.inside(x, z) && site.at(x, z) !== undefined) return site.isWater(x, z);
      // 0.0.16: cached like the ground (every planner frame asked the engine for 1,000+ topmost blocks per call: 1.5 s side-street plans)
      const k = pre + "w" + x + "," + z;
      if (groundCache.has(k)) return groundCache.get(k);
      let w = false;
      const t = topAt(dim, x, z);
      if (!t) return false;
      try { w = t.typeId === "minecraft:water" || t.typeId === "minecraft:flowing_water"; } catch { ENGINE.throws++; return false; }
      if (groundCache.size > GROUND_CACHE_MAX) groundCache.clear();
      groundCache.set(k, w);
      return w;
    },
    // the topmost block's y (a water SURFACE where the site field holds the bed) — the outfall's flood check
    top: (x, z) => { const t = topAt(dim, x, z); return t ? t.location.y : undefined; },
  };
}

/** plan the MAIN street beside the square: the four sides tried, the cheapest per cell kept. Returns
 *  { f, tmin, H, segs, cost, reserved } or null. The square's frontage (12 cells) is level at the square's height. */
function planKitMain(lsite, sq, why = []) {
  // the longest street the land allows: 50 cells each side of the square, else 40, 30, 22 (a street end may not stand
  // over water or a deep gully — a dead end is never a bridge — so near a river the street stops short of it)
  // review 19:1x: the two ends shrink independently (a river on one side no longer shortens the other)
  const pairs = [];
  for (const h1 of [KIT_HALF, 40, 30, 22]) for (const h2 of [KIT_HALF, 40, 30, 22]) pairs.push([h1, h2]);
  pairs.sort((p, q) => (q[0] + q[1]) - (p[0] + p[1]));
  let lastSum = null, best = null;
  for (const [half, tail] of pairs) {
    if (best && lastSum !== null && half + tail < lastSum) break;   // the longest feasible length wins; shorter ones only if none fits
    lastSum = half + tail;
    const L = half + 12 + tail;
    const cands = [
      KIT.frameOf(sq.x - half, sq.z + 12, [1, 0], [0, 1]),          // south of the square, running east
      KIT.frameOf(sq.x - half, sq.z - 1, [1, 0], [0, -1]),          // north of it
      KIT.frameOf(sq.x + 12, sq.z - half, [0, 1], [1, 0]),          // east of it, running south
      KIT.frameOf(sq.x - 1, sq.z - half, [0, 1], [-1, 0]),          // west of it
    ];
    for (const f of cands) {
      const ground = KIT.groundAlong(lsite, f, 0, L);
      const fixed = new Map();
      for (let t = half; t < half + 12; t++) fixed.set(t, sq.y);
      // junction windows kept flat: opposite the square (+v) and beside it (-v, before the square)
      // the -v junction sits before the square when there is room, else after it, else there is none (a short street)
      const jPlus = [half, half + 12];
      const jMinus = half - 16 >= 13 ? [half - 16, half - 4] : (half + 28 <= L - 14 ? [half + 16, half + 28] : null);
      const gridFlat = gridWindowsIn(half, 0, 0, L - 1);                       // the family's lines inside the street (long streets)
      const plan = KIT.planProfile(ground, { ...STREET_OPTS, fixed, flat: [jPlus, ...(jMinus ? [jMinus] : []), [half - 1, half + 12], ...gridFlat] });
      const wet = ground.filter((c) => c && c.water).length, unknown = ground.filter((c) => !c).length;
      why.push(`${half}+${tail}/${f.ux},${f.uz}->${f.vx},${f.vz}: ${plan.cost === Infinity ? "impossible" : Math.round(plan.cost)} (water ${wet}, unknown ${unknown})`);
      if (plan.cost === Infinity) continue;
      const per = plan.cost / L;
      if (!best || per < best.per) best = { f, tmin: 0, H: plan.H, segs: plan.segs, cost: plan.cost, per, half,
        reserved: [[jPlus[0], jPlus[1], 1], ...(jMinus ? [[jMinus[0], jMinus[1], -1]] : [])] };
    }
  }
  return best;
}

/** queue every piece of a kit street (pieces at the settlement's width; access pieces + tees over their windows) */
function queueKitStreet(st, street) {
  const { pieces, bridges } = KIT.piecesOf(street.f, kitPlan(street), "v", street.tmin);
  const over = (t) => (street.access || []).some((a) => t >= a - 1 && t <= a + 1) || (street.tees || []).some((j) => t >= j.t && t <= j.t + 12);
  st.kitQueue = st.kitQueue || [];
  for (const p of pieces) {
    if (p.kind === "flat" && over(p.a)) continue;
    st.kitQueue.push({ op: "piece", kind: p.name.slice(2), x: p.x, y: p.y, z: p.z, rot: p.rot, sid: street.id, a: p.a, len: p.len, H: p.y + 14 + (p.kind === "ramp" && p.dir < 0 ? 1 : 0), end: p.end || null });
  }
  for (const a of street.access || []) { const H = kitHAt(street, a); const p = KIT.accessPiece(street.f, a, H, "v"); st.kitQueue.push({ op: "piece", kind: "access3", x: p.x, y: p.y, z: p.z, rot: p.rot, sid: street.id, a: p.a, len: 3, H }); }
  const seenT = new Set();
  for (const j of street.tees || []) { if (seenT.has(j.t)) continue; seenT.add(j.t); queueJunction(st, street, j.t, j.side, j.H); }
  for (const b of bridges) st.kitQueue.push({ op: "bridge", sid: street.id, a: b.a, len: b.len, H: b.H });
  // A0.2 (D-C547): the exits are decided for the whole network once the pieces are down (one decision, re-solved per change)
  if (pieces.some((q) => q.kind === "dead") || street.role === "connector") queueDrain(st);
}

/** the prepared ground under / over a stretch of corridor: trees and hills over it cut away (to 3 above the old ground),
 *  hollows under the piece filled (dirt; the piece itself is 15 deep), the uphill edge outside the corridor clad in
 *  cobblestone where the hill stands 2+ above the sidewalk (a cutting's retaining wall). */
function kitPrep(dim, street, a, len, H, bridge = false, boxes = [], body = null) {
  const f = street.f;
  const inPlot = (x, z) => boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  const set = (x, y, z, id) => { try { const b = dim.getBlock({ x, y, z }); if (b) b.setType(id); } catch { /* unloaded */ } };
  for (let t = a; t < a + len; t++) {
    for (let w = -1; w <= 13; w++) {
      const [x, z] = KIT.cellOf(f, t, w);
      const g = groundAt(dim, x, z);
      if (g === undefined) {
        // 1.3.231 (CIV-LAND, his dirt on the ramps 10-07): an unread corridor cell was skipped whole — no cut — and the
        // ramp8 piece's void top layer then left the old ground standing. Edges keep the skip (no berm without a ground
        // height); a corridor cell is cut to a fixed H + 4 (ramp rise 1 + headroom 3)
        if (w === -1 || w === 13) continue;
        street.prepBlind = (street.prepBlind || 0) + 1;
        for (let y = H + 1; y <= H + 4; y++) { const b = blockAt(dim, x, y, z); if (b && b.typeId !== "minecraft:air") b.setType("minecraft:air"); }
        continue;
      }
      if (w === -1 || w === 13) {                                   // the edge outside the corridor (never a house's wall)
        if (inPlot(x, z)) continue;
        // D-C534 §2.2: the uphill edge is a stepped face (walls <= 3, benches of 3), not one tall cladding
        if (g >= H + 2) terraceFace(dim, [[x, z]], H, w === -1 ? [-f.vx, -f.vz] : [f.vx, f.vz], 3, inPlot);
        // 0.0.19: a cut face that opens water (a spring, an aquifer, a pond's edge) is sealed with cobblestone at
        // H - 1 .. H + 6 (0.0.19: a dead end filled 4 deep from a pocket the cutting opened)
        sealWater(dim, x, z, H - 1, H + 6, FILL_OUT);
        // 0.0.22 (runs 0.0.17-0.0.21: seven villagers trapped in a 6-deep hollow beside a sidewalk, 8 below their leads):
        // the DOWNHILL edge is guarded — a drop of 2..3 is filled level with the sidewalk (a berm), a deeper one (to 16)
        // gets a stone-brick retaining column up to the sidewalk and a cobblestone-wall parapet on it; another street's
        // corridor (a junction) is never walled
        if (!bridge && g <= H - 2 && g >= H - BUILD_UP_MAX - 1 && !(body && body.has(`${x},${z}`))) {
          if (H - g <= 3) { for (let y = g + 1; y < H; y++) set(x, y, z, "minecraft:dirt"); set(x, H, z, "minecraft:grass_block"); }
          else {
            // 1.3.224: the edge wall is one LIFT of stone brick over a stepped embankment (was one column to 16)
            for (let y = g + 1; y <= H; y++) set(x, y, z, y > H - LIFT ? "minecraft:stone_bricks" : FILL_IN);
            set(x, H + 1, z, "minecraft:cobblestone_wall");
            stepBerm(dim, x, z, w === -1 ? [-f.vx, -f.vz] : [f.vx, f.vz], H, inPlot, body);
          }
          street.guarded = (street.guarded || 0) + 1;
        }
        continue;
      }
      for (let y = H + 1; y <= Math.max(g, H) + 3; y++) {           // cut over the corridor (water too: a street is never a pond)
        const b = dim.getBlock({ x, y, z });
        if (b && b.typeId !== "minecraft:air") b.setType("minecraft:air");
      }
      clearTreesOver(dim, x, z, Math.max(g, H) + 3);
      if (!bridge && g < H - 15) for (let y = g + 1; y <= H - 15; y++) { const b = dim.getBlock({ x, y, z }); if (b && !isGround(b.typeId)) b.setType(w === 0 || w === 12 ? FILL_OUT : FILL_IN); }
    }
  }
}

// ------------------------------------------------------------------------------------------------ BORDER STONES (B4, D-C549)
// A settlement's INFLUENCE is the square ring of its boundary stones (a mossy cairn every STONE_EVERY cells) around the
// square. New streets, benches and roads are planned only inside it. When a tier allows a wider ring, the SURVEYOR (an
// office: census job "surveyor") walks out and carries each stone to its new place — the influence grows only when the last
// stone stands. A stone whose new place lies inside another settlement's ring cannot be moved: a DISPUTE opens in both
// towns (a census thread; the default course after DISPUTE_DAYS = a shared boundary at the midline). Skipped (accelerated)
// days move the stones at once (the harness).
const INFLUENCE = { village: 64, village2: 80, village3: 96, town: 112, town2: 128, town3: 144, city: 176, city2: 208, city3: 240,
                    metropolis: 280, metropolis2: 320, metropolis3: 360, capital: 420 };
const STONE_EVERY = 16, DISPUTE_DAYS = 20;
const BORDER_TIER = 32;                                   // a tier carries the ring at least this much further out
const BORDER_ASK = 3;                                     // a street held back by the stones this many times asks for one more ring step
/** the stones of a square ring of radius r around (cx, cz): [{ x, z, side, s }] (s = the offset along its side) */
function ringStonesOf(cx, cz, r) {
  const out = [];
  for (let s = -r; s < r; s += STONE_EVERY) {
    out.push({ x: cx + s, z: cz - r }); out.push({ x: cx + r, z: cz + s });
    out.push({ x: cx - s, z: cz + r }); out.push({ x: cx - r, z: cz - s });
  }
  return out;
}
function placeStone(dim, x, z) {
  const g = groundAt(dim, x, z);
  if (g === undefined) return null;
  try { dim.getBlock({ x, y: g + 1, z })?.setType("minecraft:mossy_cobblestone"); dim.getBlock({ x, y: g + 2, z })?.setType("minecraft:mossy_cobblestone_wall"); } catch { return null; }
  return g + 1;
}
function liftStone(dim, st0) {
  if (st0.y === undefined) return;
  try {
    const a = dim.getBlock({ x: st0.x, y: st0.y + 1, z: st0.z }); if (a && a.typeId === "minecraft:mossy_cobblestone_wall") a.setType("minecraft:air");
    const b = dim.getBlock({ x: st0.x, y: st0.y, z: st0.z }); if (b && b.typeId === "minecraft:mossy_cobblestone") b.setType("minecraft:air");
  } catch { /* unloaded */ }
}
/** is (x, z) inside the settlement's influence (no border yet = everywhere) */
function inInfluence(st, x, z) {
  if (!st.border) return true;
  const [cx, cz] = squareCentre(st);
  const r = st.border.r;
  return Math.abs(x - cx) <= r && Math.abs(z - cz) <= r;
}
function cellsInInfluence(st, cells) { for (const k of cells.keys ? cells.keys() : cells) { const [x, z] = (typeof k === "string" ? k.split(",").map(Number) : k); if (!inInfluence(st, x, z)) return false; } return true; }
/** another settlement's ring that holds (x, z) */
function ringHolder(s, st, x, z) {
  for (const o of s.settlements) {
    if (o === st || !o.border || !o.square) continue;
    const [ox, oz] = squareCentre(o);
    if (Math.abs(x - ox) <= o.border.r && Math.abs(z - oz) <= o.border.r) return o;
  }
  return null;
}
/** the founding ring: wide enough for the founding streets (+ 8), at least the village's influence; stones set at once */
function foundBorder(s, st) {
  const dim = world.getDimension(st.dim);
  const [cx, cz] = squareCentre(st);
  let ext = 0;
  for (const k of kitBody(st).keys()) { const [x, z] = k.split(",").map(Number); ext = Math.max(ext, Math.abs(x - cx), Math.abs(z - cz)); }
  const r = Math.max(INFLUENCE.village, Math.ceil((ext + 8) / STONE_EVERY) * STONE_EVERY);
  const stones = ringStonesOf(cx, cz, r).map((p) => ({ ...p, y: placeStone(dim, p.x, p.z) ?? undefined }));
  st.border = { r, target: r, stones, moves: [], disputes: [] };
  st.log.push(`day ${s.simDays.toFixed(0)}: the boundary stones are set ${r} blocks out (${stones.length} cairns)`);
}
/** a wider ring is allowed (a tier): plan the moves — every stone of the new ring, from the nearest old stone or new */
function planBorderGrowth(s, st, target, accelerated) {
  if (!st.border || target <= st.border.r) return;
  const [cx, cz] = squareCentre(st);
  const next = ringStonesOf(cx, cz, target);
  const old = st.border.stones.slice();
  const moves = [];
  for (const n of next) {
    // the nearest unused old stone carries over (its direction from the centre), the rest come from the quarry's store
    let bi = -1, bd = Infinity;
    old.forEach((o, i) => { if (o.used) return; const d = Math.hypot(Math.atan2(o.z - cz, o.x - cx) - Math.atan2(n.z - cz, n.x - cx), 0); if (d < bd) { bd = d; bi = i; } });
    const from = bi >= 0 ? old[bi] : null;
    if (from) from.used = true;
    const holder = ringHolder(s, st, n.x, n.z);
    moves.push({ from: from ? { x: from.x, z: from.z, y: from.y } : null, to: { x: n.x, z: n.z }, done: false, blocked: holder ? holder.id : null });
  }
  for (const o of old) delete o.used;
  st.border.target = target;
  st.border.moves = moves;
  const blocked = moves.filter((m) => m.blocked !== null);
  for (const holderId of [...new Set(blocked.map((m) => m.blocked))]) openDispute(s, st, s.settlements.find((x) => x.id === holderId));
  st.log.push(`day ${s.simDays.toFixed(0)}: the surveyor is to carry the boundary out to ${target} blocks (${moves.length} stones${blocked.length ? `, ${blocked.length} disputed` : ""})`);
  if (accelerated) { for (const m of moves) if (m.blocked === null) moveStoneNow(s, st, m); finishBorderIfDone(s, st); }
}
function moveStoneNow(s, st, m) {
  const dim = world.getDimension(st.dim);
  if (m.from) liftStone(dim, m.from);
  m.y = placeStone(dim, m.to.x, m.to.z) ?? undefined;
  m.done = true;
}
/** the ring stands when every undisputed stone is placed: the influence becomes the new ring; disputed stones sit on the
 *  midline toward the neighbour (the shared boundary) once their dispute is settled */
function finishBorderIfDone(s, st) {
  const b = st.border;
  if (!b || !b.moves.length) return false;
  if (b.moves.some((m) => !m.done && m.blocked === null)) return false;
  b.stones = b.moves.filter((m) => m.done).map((m) => ({ x: m.to.x, z: m.to.z, y: m.y }));
  b.r = b.target;
  b.moves = b.moves.filter((m) => !m.done);
  st.log.push(`day ${s.simDays.toFixed(0)}: the boundary stones stand ${b.r} blocks out — the town's land has grown`);
  return true;
}
function openDispute(s, st, other) {
  if (!other) return;
  const key = [st.id, other.id].sort().join("-");
  st.border.disputes = st.border.disputes || [];
  if (st.border.disputes.some((d) => d.key === key && d.state === "open")) return;
  const day = Math.floor(s.simDays);
  const d = { key, a: st.id, b: other.id, day, deadline: day + DISPUTE_DAYS, state: "open" };
  st.border.disputes.push(d);
  if (other.border) (other.border.disputes = other.border.disputes || []).push({ ...d });
  for (const town of [st, other]) {
    try { if (town.people) PEOPLE.openThread(town.people, day, "dispute", `the boundary between ${st.name} and ${other.name} is disputed`, [], d.deadline, { defaultText: "the councils agreed on a shared boundary at the midline" }); } catch { /* left */ }
    town.log.push(`day ${s.simDays.toFixed(0)}: DISPUTE — the boundary between ${st.name} and ${other.name}: the stones cannot be moved onto the other's land`);
  }
}
/** the daily border step: settled disputes put their stones on the midline; a finished ring grows the influence */
function borderDay(s, st) {
  const b = st.border;
  if (!b) return;
  const day = Math.floor(s.simDays);
  for (const d of b.disputes || []) {
    if (d.state !== "open" || day < d.deadline) continue;
    d.state = "settled";
    const other = s.settlements.find((x) => x.id === (d.a === st.id ? d.b : d.a));
    const [cx, cz] = squareCentre(st), [ox, oz] = other ? squareCentre(other) : [cx, cz];
    for (const m of b.moves) {
      if (m.blocked === null || (other && m.blocked !== other.id)) continue;
      // the shared boundary: the stone stops at the midline between the two squares (along the line to its target)
      const mx = Math.round((cx + ox) / 2), mz = Math.round((cz + oz) / 2);
      const tx = Math.abs(m.to.x - cx) > Math.abs(mx - cx) && Math.sign(m.to.x - cx) === Math.sign(mx - cx) ? mx : m.to.x;
      const tz = Math.abs(m.to.z - cz) > Math.abs(mz - cz) && Math.sign(m.to.z - cz) === Math.sign(mz - cz) ? mz : m.to.z;
      m.to = { x: tx, z: tz }; m.blocked = null; m.shared = true;
    }
    st.log.push(`day ${s.simDays.toFixed(0)}: the dispute with ${other ? other.name : "a neighbour"} is settled — a shared boundary at the midline`);
  }
  finishBorderIfDone(s, st);
}
/** the surveyor's next task (the schedule sends him): { x, z, kind: "lift" | "place", m } or null */
function surveyorTask(st) {
  const b = st.border;
  if (!b) return null;
  const m = b.moves.find((q) => !q.done && q.blocked === null);
  if (!m) return null;
  if (m.from && !m.lifted) return { x: m.from.x, z: m.from.z, kind: "lift", m };
  return { x: m.to.x, z: m.to.z, kind: "place", m };
}
function surveyorAct(s, st, task) {
  const dim = world.getDimension(st.dim);
  if (task.kind === "lift") { liftStone(dim, task.m.from); task.m.lifted = true; return; }
  task.m.y = placeStone(dim, task.m.to.x, task.m.to.z) ?? undefined;
  task.m.done = true;
  finishBorderIfDone(s, st);
}
// ------------------------------------------------------------------------------------------------ STREET MANHOLES (F3, D-C538)
// Every MANHOLE_EVERY cells of level street an ACCESS piece (his kit: side galleries at sewer level, the utility gallery
// widened) carries a public shaft in the sidewalk (w 1 or 11): a ladder from the sewer gallery up through the utility
// gallery to a pw:manhole_cover flush with the sidewalk. The cover opens from below as every hatch does; from above only
// with a registered key (F4, the clock's hatch law).
const MANHOLE_EVERY = 26;
const LADDER_FACE = (u) => (u[0] === 1 ? 5 : u[0] === -1 ? 4 : u[1] === 1 ? 3 : 2);      // facing_direction: away from the t-1 wall
/** the manholes a street still lacks: [{ t, side }] on level stretches, clear of junctions, house access and dead ends */
function manholesWanted(st, street) {
  if (street.role === "connector" || street.bench) return [];
  const have = (street.manholes || []).map((m) => m.t);
  const blocked = (t) => (street.access || []).some((a) => Math.abs(a - t) <= 3) || (street.tees || []).some((j) => t >= j.t - 2 && t <= j.t + 14)
    || (street.reserved || []).some(([a, b]) => t >= a - 2 && t <= b + 2) || have.some((m) => Math.abs(m - t) < MANHOLE_EVERY);
  const level = (t) => { const h = kitHAt(street, t); return h !== undefined && kitHAt(street, t - 1) === h && kitHAt(street, t + 1) === h && kitHAt(street, t - 2) === h && kitHAt(street, t + 2) === h; };
  const segAt = (t) => kitPlan(street).segs.find((q) => t - street.tmin >= q.a && t - street.tmin < q.a + q.len);
  const out = [];
  let last = -1e9;
  for (const m of have) last = Math.max(last, m);
  const t0 = street.tmin + 16, t1 = street.tmin + street.H.length - 17;
  for (let t = t0; t <= t1; t++) {
    if (have.some((m) => Math.abs(m - t) < MANHOLE_EVERY) || out.some((m) => Math.abs(m.t - t) < MANHOLE_EVERY)) continue;
    const sg = segAt(t);
    if (!sg || sg.kind !== "flat" || !level(t) || blocked(t)) continue;
    out.push({ t, side: (have.length + out.length) % 2 ? 1 : -1 });
  }
  void last;
  return out;
}
/** queue the access pieces + shafts of the manholes a settlement's streets lack (daily; a handful at a time) */
function queueManholes(st, max = 6) {
  let n = 0;
  st.kitQueue = st.kitQueue || [];
  for (const street of st.streets.filter((x) => x.kind === "kit")) {
    for (const m of manholesWanted(st, street)) {
      if (n >= max) return n;
      const H = kitHAt(street, m.t);
      const p = KIT.accessPiece(street.f, m.t, H, st.width || "v");
      (street.manholes = street.manholes || []).push(m);
      (street.accessLaid = street.accessLaid || []).push(m.t);                // a straight queued later never covers it
      st.kitQueue.push({ op: "piece", kind: "access3", x: p.x, y: p.y, z: p.z, rot: p.rot, sid: street.id, a: m.t - 1, len: 3, H });
      st.kitQueue.push({ op: "manhole", sid: street.id, a: m.t, len: 1, H, side: m.side });
      n++;
    }
  }
  return n;
}
/** carve one public shaft: ladders from the sewer gallery (y0 + 3) to under the sidewalk, the cover on top */
function carveManhole(dim, street, t, H, side) {
  const w = side < 0 ? 1 : 11;
  const [x, z] = KIT.cellOf(street.f, t, w);
  const y0 = H - 14;
  const face = LADDER_FACE([street.f.ux, street.f.uz]);
  for (let y = y0 + 3; y <= y0 + 13; y++) {
    try { dim.getBlock({ x, y, z })?.setPermutation(BlockPermutation.resolve("minecraft:ladder", { facing_direction: face })); } catch (e) { console.warn(`[CIV-CLOCK] manhole ladder: ${e}`); return false; }
  }
  try { dim.getBlock({ x, y: y0 + 14, z })?.setPermutation(BlockPermutation.resolve("pw:manhole_cover", { "pw:skin": 0, "pw:phase": 0 })); }
  catch (e) { console.warn(`[CIV-CLOCK] manhole cover: ${e}`); return false; }
  return true;
}
// F5 (D-C538): the sewer is LIT so nothing spawns below — a lantern in a wall niche of the hall (w 3 / 9, the hall's
// middle height) and of the utility gallery (w 2 / 10), every SEWER_LAMP cells, the sides alternating
const SEWER_LAMP = 12;
function kitSewerLamps(dim, street, t) {
  const k = t - street.tmin;
  if (((k % SEWER_LAMP) + SEWER_LAMP) % SEWER_LAMP !== 6) return 0;
  const H = kitHAt(street, t);
  if (H === undefined) return 0;
  const y0 = H - 14, left = Math.floor(k / SEWER_LAMP) % 2 === 0;
  let n = 0;
  for (const [w, y] of [[left ? 3 : 9, y0 + 4], [left ? 2 : 10, y0 + 8]]) {
    const [x, z] = KIT.cellOf(street.f, t, w);
    try { const b = dim.getBlock({ x, y, z }); if (b && b.typeId === "minecraft:stone_bricks") { b.setType("minecraft:lantern"); n++; } } catch { /* unloaded */ }
  }
  return n;
}
/** water in one column between y0 and y1 becomes `fill` (a sealed face); returns how many cells changed */
function sealWater(dim, x, z, y0, y1, fill) {
  let n = 0;
  for (let y = y0; y <= y1; y++) {
    try { const b = dim.getBlock({ x, y, z }); if (b && (b.typeId === "minecraft:water" || b.typeId === "minecraft:flowing_water")) { b.setType(fill); n++; } } catch { /* unloaded */ }
  }
  return n;
}
/** a plank bridge: road deck one below the sidewalk deck (as on the pieces), railings on both outer edges with an opening
 *  every RAIL_GAP cells (his 18:01 R5), log piers under the deck only, solid abutments at both ends (they close the
 *  tunnels of the pieces beside the bridge). */
function kitBridge(dim, st, street, a, len, H) {
  const f = street.f;
  const [r0, r1] = ROAD_W[st.width || "v"];
  for (let t = a; t < a + len; t++) {
    const abut = t === a || t === a + len - 1;
    for (let w = 0; w < 13; w++) {
      const [x, z] = KIT.cellOf(f, t, w);
      const deckY = w >= r0 && w <= r1 ? H - 1 : H;
      let g = groundAt(dim, x, z);
      if (g === undefined) continue;
      // through water to its bed for piers and abutments
      let bed = g;
      for (let k = 0; k < 40; k++) { const b = dim.getBlock({ x, y: bed, z }); if (!b || (b.typeId !== "minecraft:water" && b.typeId !== "minecraft:flowing_water")) break; bed--; }
      const pier = (t - a) % 6 === 0 && (w === 1 || w === 6 || w === 11);
      for (let y = bed + 1; y < deckY; y++) {
        const b = dim.getBlock({ x, y, z });
        if (!b) continue;
        if (abut) b.setType("minecraft:stone_bricks");
        else if (pier) b.setType("minecraft:spruce_log");
        else if (b.typeId !== "minecraft:water" && b.typeId !== "minecraft:flowing_water" && b.typeId !== "minecraft:air") b.setType("minecraft:air");
      }
      dim.getBlock({ x, y: deckY, z })?.setType("minecraft:spruce_planks");
      // his 18:01 R5: openings in the railing — review 19:1x: only where there is somewhere to step to (the ground
      // outside the rail within 2 blocks below the deck, not water); over a gully or a river the rail is continuous
      let landing = false;
      if ((w === 0 || w === 12) && (t - a) % KIT.RAIL_GAP === Math.floor(KIT.RAIL_GAP / 2)) {
        const [ox, oz] = KIT.cellOf(f, t, w === 0 ? -1 : 13);
        const go = groundAt(dim, ox, oz);
        let wet = false;
        try { const tb = dim.getTopmostBlock({ x: ox, z: oz }); wet = !!tb && tb.typeId.includes("water"); } catch { wet = true; }
        landing = go !== undefined && !wet && go >= deckY - 2 && go <= deckY;
      }
      const rail = (w === 0 || w === 12) && !landing;
      dim.getBlock({ x, y: deckY + 1, z })?.setType(rail ? "minecraft:spruce_fence" : "minecraft:air");
      for (let y = deckY + 2; y <= deckY + 4; y++) { const b = dim.getBlock({ x, y, z }); if (b && b.typeId !== "minecraft:air") b.setType("minecraft:air"); }
      clearTreesOver(dim, x, z, deckY + 4);
    }
  }
}

const GRATE_BLOCK = "minecraft:iron_bars";    // D-C533: a stand-in grate in the exit opening (his grate replaces it); on Bedrock water
                                               // passes through waterloggable bars (R4 §2.5) — the probe checks the spill
const SOLID_ID = (id) => id && id !== "minecraft:air" && !id.includes("water") && !id.includes("slab") && !id.includes("stairs") && !id.includes("lava");

/** carve a planned outfall (D-C533 form): outside the piece a 3-wide tunnel lined in stone bricks — centre line y1 =
 *  the WATER channel (source blocks, continuing the trench), the two side cells y1 = stone-brick ledges, head room y2..y4;
 *  inside the piece the hall is left alone (its trench is already the channel) and only the wall it leaves through is
 *  opened (3 x 3 over the channel). The exit is a stone-brick frame with a door-sized space (1 x 2) where the channel
 *  spills out; GRATE_BLOCK stands in that space (his grate later). */
function kitCarveOutfall(dim, street, a, plan) {
  const inPiece = (x, z) => { const [t, w] = KIT.tw(street.f, x, z); return t >= a && t <= a + 12 && w >= 0 && w <= 12; };
  const fy = plan.floorY;
  const cells = plan.cells;
  const dirAt = (i) => { const p = cells[Math.max(0, i - 1)], q = cells[Math.max(1, i)]; return [Math.sign(q[0] - p[0]), Math.sign(q[1] - p[1])]; };
  const set = (x, y, z, id) => { try { const b = dim.getBlock({ x, y, z }); if (b) b.setType(id); } catch { /* unloaded */ } };
  const water = (x, y, z) => { try { const b = dim.getBlock({ x, y, z }); if (b) b.setPermutation(BlockPermutation.resolve("minecraft:water", { liquid_depth: 0 })); } catch { /* unloaded */ } };
  const [cx0, cz0] = cells[0];
  const dist = (x, z) => Math.abs(x - cx0) + Math.abs(z - cz0);      // steps from the piece centre (the path is straight inside the piece)
  // lining first (outside the piece), then the air (so a turn's corner stays open)
  for (let i = 1; i < cells.length; i++) {
    const [x, z] = cells[i], d = dirAt(i), p = [-d[1], d[0]];
    if (inPiece(x, z)) continue;
    for (let k = -2; k <= 2; k++) for (let y = fy - 1; y <= fy + 4; y++) {
      const cx = x + p[0] * k, cz = z + p[1] * k;
      if (Math.abs(k) === 2 || y === fy - 1 || y === fy + 4) set(cx, y, cz, "minecraft:stone_bricks");
    }
  }
  for (let i = 0; i < cells.length; i++) {
    const [x, z] = cells[i], d = dirAt(i), p = [-d[1], d[0]];
    const inside = inPiece(x, z);
    if (inside && dist(x, z) < 4) { water(x, fy, z); continue; }                     // the hall: the trench / cross drain is the channel
    for (let k = -1; k <= 1; k++) {
      const cx = x + p[0] * k, cz = z + p[1] * k;
      for (let y = fy + 1; y <= fy + 3; y++) set(cx, y, cz, "minecraft:air");
      if (k === 0) water(cx, fy, cz); else set(cx, fy, cz, "minecraft:stone_bricks");
    }
  }
  // the exit frame: a wall across the mouth, a door-sized space in its middle; the channel's last source sits in the
  // space's lower cell (it spills out), the grate stand-in in both cells
  const [ex, ez] = plan.exit, d = plan.dir, p = [-d[1], d[0]];
  for (let k = -2; k <= 2; k++) for (let y = fy - 1; y <= fy + 4; y++) {
    const inSpace = k === 0 && (y === fy || y === fy + 1);
    set(ex + p[0] * k, y, ez + p[1] * k, inSpace ? GRATE_BLOCK : "minecraft:stone_bricks");
  }
  // the water behind the grate: the source one cell before the exit keeps the channel full to the frame
  if (cells.length >= 2) { const [bx, bz] = cells[cells.length - 2]; water(bx, fy, bz); }
  try { const g = dim.getBlock({ x: ex, y: fy, z: ez }); if (g && g.canContainLiquid && g.canContainLiquid(LiquidType.Water)) g.setWaterlogged(true); } catch { /* no API */ }
}

// ------------------------------------------------------------------------------------------------ A0.2 SEWER EXITS v2 (D-C547 / D-C549)
// One decision per settlement, re-solved after every street change: the networks' low points get ONE exit each (open
// water > a hillside face > a soakaway pit), every other dead end stays sealed, an exit that serves no low point any more
// is back-filled. Records live on their street's `outfalls` with v2 = true: { v2, key, kind: "dead" | "side", a | t,
// end, plan: { cells, floors, sources, exit, dir, floorY, target, outlet, steps }, manholes: [[x, y, z, ground]], day,
// gone (its dead end built over), sealed (day) }.
const TRUNK_LAMP = 12, TRUNK_MANHOLE = 26;
const trunkKey = (kind, sid, at) => `${kind}:${sid}:${at}`;
function recKey(street, o) { return o.key || trunkKey("dead", street.id, o.a); }
/** the [street, record] of an exit key */
function exitRec(st, key) { for (const street of st.streets || []) for (const o of street.outfalls || []) if (o && recKey(street, o) === key) return [street, o]; return null; }
/** the drain decision goes to the BACK of the queue (after the pieces it depends on); a pending one is replaced */
function queueDrain(st) {
  st.kitQueue = (st.kitQueue || []).filter((op) => op.op !== "drain");
  st.kitQueue.push({ op: "drain" });
}
/** the cells of the piece / corridor stretch a trunk leaves from (no veto there; inside it only the way out is cut) */
function trunkOwn(street, rec) {
  const f = street.f;
  if (rec.kind === "side") return (x, z) => { const [t, w] = KIT.tw(f, x, z); return Math.abs(t - rec.t) <= 2 && w >= 0 && w <= 12; };
  return (x, z) => { const [t, w] = KIT.tw(f, x, z); return t >= rec.a && t <= rec.a + 12 && w >= 0 && w <= 12; };
}
/** decide (no block reads): which low points are served, which need an exit (outfall2 ops), which exits must go (sealout) */
function drainDecide(s, st) {
  const streets = (st.streets || []).filter((x) => x.kind === "kit" && x.H && x.H.length);
  const nets = KIT.drainNetworks(streets);
  st.kitQueue = (st.kitQueue || []).filter((op) => op.op !== "outfall2" && op.op !== "sealout");     // superseded by this decision
  const live = [];
  for (const street of streets) for (const o of street.outfalls || []) if (o && o.plan && !o.sealed) live.push([street, o]);
  const used = new Set();
  const summary = [];
  nets.forEach((net, ni) => {
    let served = 0, asked = 0;
    for (const m of net.minima) {
      const keys = new Set(m.dead.map((d) => trunkKey("dead", d.sid, d.a)));
      for (const sd of m.side) for (const t of sd.ts) keys.add(trunkKey("side", sd.sid, t));
      const have = live.find(([street, o]) => !o.gone && keys.has(recKey(street, o)));
      if (have) { used.add(recKey(have[0], have[1])); served++; continue; }
      // candidates: the dead ends of the low point (each tried), else up to 6 centre-line cells of each street in it that
      // stand on plain street (no tee, no access piece, no reserved window: a side channel must not cut a junction)
      const cands = m.dead.map((d) => ({ kind: "dead", sid: d.sid, a: d.a, end: d.end }));
      if (!cands.length) for (const sd of m.side) {
        const street = streets.find((x) => x.id === sd.sid);
        const plain = (t) => !(street.tees || []).some((j) => t >= j.t - 2 && t <= j.t + 14) && !(street.access || []).some((a) => Math.abs(a - t) <= 3)
          && !(street.reserved || []).some(([a, b]) => t >= a - 2 && t <= b + 2) && !(street.segs || []).some((q) => q.kind !== "flat" && t >= street.tmin + q.a - 2 && t < street.tmin + q.a + q.len + 2);
        // run 0.0.22: SIDE trunks from mid-street low points ran under the house frontage (7 low points, 7 trunks by day 6;
        // the tunnels' cells veto plots, and village II placed 2 plots of 5): a low point inside a street drains into a
        // SOAKAWAY under its own trench — the frontage stays for houses; trunks leave only from dead ends
        const tt = sd.ts.filter(plain);
        if (tt.length) { cands.push({ kind: "side", sid: sd.sid, t: tt[0], soakOnly: true }); break; }
      }
      if (!cands.length && m.side.length) cands.push({ kind: "side", sid: m.side[0].sid, t: m.side[0].ts[0], soakOnly: true });
      if (!cands.length) continue;
      const c0 = cands[0], street0 = streets.find((x) => x.id === c0.sid);
      const at = c0.kind === "dead" ? c0.a + 6 : c0.t;
      st.kitQueue.push({ op: "outfall2", sid: c0.sid, a: at, len: 1, H: kitHAt(street0, at), cands, floor: m.floor, net: ni });
      asked++;
    }
    summary.push({ streets: net.ids, lo: net.lo, hi: net.hi, minima: net.minima.length, served, asked });
  });
  for (const [street, o] of live) {
    const k = recKey(street, o);
    if (used.has(k)) continue;
    st.kitQueue.push({ op: "sealout", sid: street.id, a: o.kind === "side" ? o.t : o.a, len: 1, H: o.plan.floorY + 13, key: k });
  }
  st.drainNets = summary;
  st.drainDay = s.simDays;
}
/** a waterlogged-capable grate (R-1: water never flows INTO plain bars; a waterlogged one spills) */
function grate(dim, x, y, z) {
  try { const b = dim.getBlock({ x, y, z }); if (!b) return; b.setType(GRATE_BLOCK); if (b.canContainLiquid && b.canContainLiquid(LiquidType.Water)) b.setWaterlogged(true); } catch { /* unloaded */ }
}
/** carve a v2 trunk: lining, channel (a source at the head of every level stretch, air elsewhere: the engine runs the
 *  water down the steps), head room, lamps every TRUNK_LAMP cells (no dark sewer, F5), a manhole every TRUNK_MANHOLE
 *  cells where open ground lies 2+ above the vault (D-C549), the mouth frame with its waterlogged grate; or a soakaway */
function kitCarveTrunk(dim, st, street, rec) {
  const plan = rec.plan;
  if (!plan) return;
  const set = (x, y, z, id) => { try { const b = dim.getBlock({ x, y, z }); if (b) b.setType(id); } catch { /* unloaded */ } };
  const water = (x, y, z) => { try { const b = dim.getBlock({ x, y, z }); if (b) b.setPermutation(BlockPermutation.resolve("minecraft:water", { liquid_depth: 0 })); } catch { /* unloaded */ } };
  const cells = plan.cells, floors = plan.floors || cells.map(() => plan.floorY), src = new Set(plan.sources || []);
  if (plan.target === "soakaway") {
    // the medieval cesspit: under the trench at the low point a 3 x 3 pit SOAK_DEPTH deep in a cobblestone lining, gravel
    // in its lower half; the trench floor opens into it
    const [x, z] = plan.exit, fy = plan.floorY;
    for (let dx = -2; dx <= 2; dx++) for (let dz = -2; dz <= 2; dz++) for (let y = fy - 2 - KIT.SOAK_DEPTH; y <= fy - 2; y++) {
      const ring = Math.abs(dx) === 2 || Math.abs(dz) === 2 || y === fy - 2 - KIT.SOAK_DEPTH;
      set(x + dx, y, z + dz, ring ? "minecraft:cobblestone" : (y <= fy - 2 - KIT.SOAK_DEPTH / 2 ? "minecraft:gravel" : "minecraft:air"));
    }
    set(x, fy - 1, z, "minecraft:air");
    return;
  }
  const own = trunkOwn(street, rec);
  const dirAt = (i) => { const p = cells[Math.max(0, i - 1)], q = cells[Math.max(1, i)]; return [Math.sign(q[0] - p[0]), Math.sign(q[1] - p[1])]; };
  const [cx0, cz0] = cells[0];
  const dist = (x, z) => Math.abs(x - cx0) + Math.abs(z - cz0);
  // lining first (outside own), then the air (a turn's corner stays open)
  for (let i = 1; i < cells.length; i++) {
    const [x, z] = cells[i], d = dirAt(i), p = [-d[1], d[0]], fy = floors[i];
    if (own(x, z)) continue;
    for (let k = -2; k <= 2; k++) for (let y = fy - 1; y <= fy + 4; y++) if (Math.abs(k) === 2 || y === fy - 1 || y === fy + 4) set(x + p[0] * k, y, z + p[1] * k, "minecraft:stone_bricks");
  }
  let j = 0;
  for (let i = 0; i < cells.length; i++) {
    const [x, z] = cells[i], d = dirAt(i), p = [-d[1], d[0]], fy = floors[i];
    if (own(x, z)) {
      if (rec.kind === "side") { if (i > 0) { set(x, fy, z, "minecraft:air"); set(x, fy + 1, z, "minecraft:air"); } continue; }   // a cross channel to the corridor's edge
      if (dist(x, z) < 4) { water(x, fy, z); continue; }                         // the dead end's hall: the trench / cross drain is the channel
    } else j++;
    for (let k = -1; k <= 1; k++) {
      const cx = x + p[0] * k, cz = z + p[1] * k;
      for (let y = fy + 1; y <= fy + 3; y++) set(cx, y, cz, "minecraft:air");
      if (k !== 0) set(cx, fy, cz, "minecraft:stone_bricks");
      else if (src.has(i) || own(x, z)) water(cx, fy, cz);
      else set(cx, fy, cz, "minecraft:air");
    }
    if (j > 0 && j % TRUNK_LAMP === TRUNK_LAMP / 2) { const side = (Math.floor(j / TRUNK_LAMP) % 2) ? 2 : -2; set(x + p[0] * side, fy + 2, z + p[1] * side, "minecraft:lantern"); st.trunkLamps = (st.trunkLamps || 0) + 1; }
  }
  // manholes where open ground stands over the vault (not within 8 of either end)
  rec.manholes = rec.manholes || [];
  if (!rec.manholes.length) {
    const veto = kitVeto(load());
    let jj = 0;
    const nOut = cells.filter(([x, z]) => !own(x, z)).length;
    for (let i = 1; i < cells.length; i++) {
      const [x, z] = cells[i];
      if (own(x, z)) continue;
      jj++;
      if (jj % TRUNK_MANHOLE !== TRUNK_MANHOLE / 2 || jj > nOut - 8) continue;
      const d = dirAt(i), p = [-d[1], d[0]], fy = floors[i];
      const sx = x + p[0], sz = z + p[1];
      let top;
      try { top = dim.getTopmostBlock({ x: sx, z: sz }); } catch { top = undefined; }
      if (!top || top.typeId.includes("water") || veto(sx, sz)) continue;
      const g = top.location.y;
      if (g - (fy + 4) < 2) continue;
      const groundId = top.typeId;
      const face = LADDER_FACE([-p[0], -p[1]]);
      for (let y = fy + 4; y <= g; y++) for (const [ax, az] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = sx + ax, nz = sz + az;
        if (nx === x && nz === z) continue;                                     // the vault's own centre column below fy+4 stays
        set(nx, y, nz, "minecraft:stone_bricks");
      }
      for (let y = fy + 1; y < g; y++) { try { dim.getBlock({ x: sx, y, z: sz })?.setPermutation(BlockPermutation.resolve("minecraft:ladder", { facing_direction: face })); } catch { /* left */ } }
      try { dim.getBlock({ x: sx, y: g, z: sz })?.setPermutation(BlockPermutation.resolve("pw:manhole_cover", { "pw:skin": 0, "pw:phase": 0 })); } catch (e) { console.warn(`[CIV-CLOCK] trunk manhole: ${e}`); continue; }
      rec.manholes.push([sx, g, sz, groundId]);
      (st.manholeCells = st.manholeCells || []).push([sx, g + 1, sz]);
      st.manholesLaid = (st.manholesLaid || 0) + 1;
    }
  }
  // the mouth: a stone-brick frame across it, a door-sized space with the waterlogged grate
  const [ex, ez] = plan.exit, d = plan.dir, p = [-d[1], d[0]], fe = floors[floors.length - 1];
  for (let k = -2; k <= 2; k++) for (let y = fe - 1; y <= fe + 4; y++) {
    const inSpace = k === 0 && (y === fe || y === fe + 1);
    if (inSpace) grate(dim, ex + p[0] * k, y, ez + p[1] * k); else set(ex + p[0] * k, y, ez + p[1] * k, "minecraft:stone_bricks");
  }
  if (cells.length >= 2) { const [bx, bz] = cells[cells.length - 2]; water(bx, floors[floors.length - 2], bz); }
}
/** back-fill a trunk that serves no low point any more (D-C547 (6)): the channel and head room outside every corridor
 *  become cobblestone, the grate space stone bricks, its manholes closed (the ground block back on top), a soakaway's
 *  trench hole closed; a side channel across a standing corridor is walled again */
function kitSealTrunk(dim, s, st, street, rec) {
  const plan = rec.plan;
  if (!plan) return;
  const set = (x, y, z, id) => { try { const b = dim.getBlock({ x, y, z }); if (b) b.setType(id); } catch { /* unloaded */ } };
  const body = kitBody(st);
  if (plan.target === "soakaway") { set(plan.exit[0], plan.floorY - 1, plan.exit[1], "minecraft:stone_bricks"); return; }
  const cells = plan.cells, floors = plan.floors || cells.map(() => plan.floorY);
  const dirAt = (i) => { const p = cells[Math.max(0, i - 1)], q = cells[Math.max(1, i)]; return [Math.sign(q[0] - p[0]), Math.sign(q[1] - p[1])]; };
  const own = rec.v2 ? trunkOwn(street, rec) : () => false;
  for (let i = 1; i < cells.length; i++) {
    const [x, z] = cells[i], d = dirAt(i), p = [-d[1], d[0]], fy = floors[i];
    if (body.has(`${x},${z}`)) {
      if (rec.kind === "side" && own(x, z)) { set(x, fy, z, "minecraft:stone_bricks"); set(x, fy + 1, z, "minecraft:stone_bricks"); }
      continue;
    }
    for (let k = -1; k <= 1; k++) for (let y = fy; y <= fy + 3; y++) { const cx = x + p[0] * k, cz = z + p[1] * k; if (!body.has(`${cx},${cz}`)) set(cx, y, cz, "minecraft:cobblestone"); }
  }
  const [ex, ez] = plan.exit, fe = floors[floors.length - 1];
  if (!body.has(`${ex},${ez}`)) { set(ex, fe, ez, "minecraft:stone_bricks"); set(ex, fe + 1, ez, "minecraft:stone_bricks"); }
  for (const [mx, my, mz, gid] of rec.manholes || []) {
    set(mx, my, mz, gid && !gid.includes("manhole") ? gid : "minecraft:grass_block");
    for (let y = floors[0] - 20; y < my; y++) { try { const b = dim.getBlock({ x: mx, y, z: mz }); if (b && b.typeId === "minecraft:ladder") b.setType("minecraft:cobblestone"); } catch { /* left */ } }
    st.manholeCells = (st.manholeCells || []).filter((c) => !(c[0] === mx && c[2] === mz));
  }
  // a dead end that still stands is laid again (its walls close the opening)
  if (rec.kind !== "side" && !rec.gone) {
    const seg = (street.segs || []).find((q) => q.kind === "dead" && street.tmin + q.a === rec.a);
    if (seg) {
      const { pieces } = KIT.piecesOf(street.f, { H: street.H, segs: [seg] }, "v", street.tmin);
      for (const pc of pieces) st.kitQueue.push({ op: "piece", kind: pc.name.slice(2), x: pc.x, y: pc.y, z: pc.z, rot: pc.rot, sid: street.id, a: pc.a, len: pc.len, H: pc.y + 14, end: pc.end || null });
    }
  }
  void s;
}
/** the HOUSE FRONTAGE of a settlement's streets: the 16 cells beside every flat stretch, both sides (where plots stand or
 *  will) — a trunk never runs there (0.0.22: village II placed 2 of 5 plots; trunks' cells veto plots) */
const frontageCache = new Map();
function kitFrontage(st) {
  const key = `${st.id}:${st.kitVer || 0}`;
  const got = frontageCache.get(st.id);
  if (got && got.key === key) return got.set;
  const set = new Set();
  for (const street of (st.streets || []).filter((x) => x.kind === "kit" && x.role !== "connector")) {
    for (const q of street.segs || []) {
      if (q.kind !== "flat") continue;
      for (let t = street.tmin + q.a; t < street.tmin + q.a + q.len; t++) for (const w of [-16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]) {
        const [x, z] = KIT.cellOf(street.f, t, w);
        set.add(`${x},${z}`);
      }
    }
  }
  frontageCache.set(st.id, { key, set });
  return set;
}
/** plan + carve the exit of one low point: each candidate tried in order (water > face, shortest), a soakaway under the
 *  first when none reaches daylight. Returns "wait" while the survey's chunks sleep. */
function drainExitOp(dim, s, st, op) {
  const te0 = Date.now();
  try { return drainExitOpBody(dim, s, st, op, te0); } finally {
    const ms = Date.now() - te0;
    if (ms > SLOW_MS) console.warn(`[CIV-CLOCK] slow outfall candidate ${op.ci || 0}/${(op.cands || []).length}: ${ms} ms (veto ${exitT.veto}, plan ${exitT.plan}, carve ${exitT.carve})`);
  }
}
const exitT = { veto: 0, plan: 0, carve: 0 };
function drainExitOpBody(dim, s, st, op, te0) {
  exitT.veto = exitT.plan = exitT.carve = 0;
  const lsite = liveSite(dim, siteOf(st));
  const veto0 = kitVeto(s), front = kitFrontage(st);
  exitT.veto = Date.now() - te0;
  const veto = (x, z) => veto0(x, z) || front.has(`${x},${z}`);
  // 1.3.226 (gate 226-1: an outfall survey up to 994 ms in one tick): ONE candidate per call — a candidate that finds no
  // daylight sends the op back to the queue's front (op.ci), so each search has its own tick
  for (let ci = op.ci || 0; ci < op.cands.length; ci++) {
    const c = op.cands[ci];
    if (ci > (op.ci || 0)) { op.ci = ci; return "again"; }
    if (c.soakOnly) continue;
    const street = st.streets.find((x) => x.kind === "kit" && x.id === c.sid);
    if (!street) continue;
    const at = c.kind === "dead" ? c.a + 6 : c.t;
    const H = kitHAt(street, at);
    if (H === undefined) continue;
    const start = KIT.cellOf(street.f, at, 6);
    const u = [street.f.ux, street.f.uz], v = [street.f.vx, street.f.vz];
    const rec = { v2: true, kind: c.kind, a: c.a, t: c.t, end: c.end };
    const own = trunkOwn(street, rec);
    const dirs = c.kind === "dead" ? [c.end === "start" ? [-u[0], -u[1]] : u, v, [-v[0], -v[1]]] : [v, [-v[0], -v[1]]];
    const tp0 = Date.now();
    const plan = KIT.planOutfall2(lsite, { start, dirs, own, floorY: H - 13, blocked: (x, z) => veto(x, z) });
    exitT.plan += Date.now() - tp0;
    if (!plan) continue;
    // the mouth of a water exit stands on the BANK (the last cell before the water), its grate spilling into the water
    if (plan.target === "water" && plan.cells.length > 2) { plan.cells.pop(); plan.floors.pop(); plan.exit = plan.cells[plan.cells.length - 1]; plan.sources = plan.sources.filter((i) => i < plan.cells.length - 1); }
    // kitvillage-0.0.8: the field's ground may differ from the live blocks: the mouth must open on air or water at its
    // floor — walk on up to 8 cells (the floor stays)
    const fe = plan.floors[plan.floors.length - 1];
    const isOpen = (x, z) => { try { const b = dim.getBlock({ x, y: fe, z }); return !!b && (b.typeId === "minecraft:air" || b.typeId.includes("water")); } catch { return false; } };
    let [ex, ez] = plan.exit, k = 0;
    // review 04:4x #15: the extension obeys the same veto as the plan (no plot, no corridor, no house frontage)
    let vetoed = false;
    while (k < 8 && !isOpen(ex + plan.dir[0], ez + plan.dir[1])) {
      if (veto(ex + plan.dir[0], ez + plan.dir[1])) { vetoed = true; break; }
      ex += plan.dir[0]; ez += plan.dir[1]; plan.cells.push([ex, ez]); plan.floors.push(fe); k++;
    }
    if (vetoed || !isOpen(ex + plan.dir[0], ez + plan.dir[1])) continue;
    plan.exit = [ex, ez];
    if (k) { let last = plan.sources.length ? plan.sources[plan.sources.length - 1] : 0; while (last + 7 < plan.cells.length - 1) { last += 7; plan.sources.push(last); } }
    rec.key = trunkKey(c.kind, street.id, c.kind === "dead" ? c.a : c.t);
    rec.plan = plan; rec.day = Math.floor(s.simDays); rec.net = op.net;
    (street.outfalls = street.outfalls || []).push(rec);
    const tc0 = Date.now();
    kitCarveTrunk(dim, st, street, rec);
    exitT.carve = Date.now() - tc0;
    const where = plan.target === "water" ? "into the water" : "out of the hillside";
    const msg = `the sewer drains ${where} at ${ex} ${fe} ${ez} (a ${plan.cells.filter(([x, z]) => !own(x, z)).length}-block trunk${plan.steps ? `, falling ${plan.steps}` : ""}, from street ${street.id}'s ${c.kind === "dead" ? `${c.end} dead end` : "low point"})`;
    st.log.push(`day ${s.simDays.toFixed(0)}: ${msg}`);
    return true;
  }
  // no daylight within reach: a soakaway under the first candidate
  const c = op.cands[0];
  const street = st.streets.find((x) => x.kind === "kit" && x.id === c.sid);
  if (!street) return true;
  const at = c.kind === "dead" ? c.a + 6 : c.t;
  const H = kitHAt(street, at);
  if (H === undefined) return true;
  const rec = { v2: true, kind: c.kind, a: c.a, t: c.t, end: c.end, key: trunkKey(c.kind, street.id, c.kind === "dead" ? c.a : c.t), day: Math.floor(s.simDays), net: op.net,
                plan: KIT.soakawayAt(KIT.cellOf(street.f, at, 6), H - 13) };
  (street.outfalls = street.outfalls || []).push(rec);
  kitCarveTrunk(dim, st, street, rec);
  st.log.push(`day ${s.simDays.toFixed(0)}: no river or hillside within reach of street ${street.id}'s low point: the sewer drains into a soakaway pit at ${rec.plan.exit[0]} ${H - 13} ${rec.plan.exit[1]}`);
  return true;
}

/** D-C533: the sewer trench carries water — in every laid piece the LOWER of the trench's two air cells becomes a water
 *  source. Scan: y1..y2 of the piece (ramps: y1..y3 on the centre line only — their trench steps up with the road); a
 *  cell is the trench's bottom when it is air, the cell above is air and the cell below is a full solid block. The hall
 *  floor (y2 solid, y3 air) never matches. Runs after every placement, so a re-laid piece is re-watered. */
function kitWaterTrench(dim, street, a, len, kind) {
  const ramp = kind === "ramp7";
  let n = 0;
  for (let t = a; t < a + len; t++) {
    const H = kitHAt(street, t);
    if (H === undefined) continue;
    const y0 = H - 14;
    const ws = ramp ? [6] : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    for (const w of ws) {
      const [x, z] = KIT.cellOf(street.f, t, w);
      for (let y = y0 + 1; y <= y0 + (ramp ? 4 : 2); y++) {
        let here, above, below;
        try { here = dim.getBlock({ x, y, z }); above = dim.getBlock({ x, y: y + 1, z }); below = dim.getBlock({ x, y: y - 1, z }); } catch { break; }
        if (!here || !above || !below) break;
        if ((here.typeId === "minecraft:air" || here.typeId === "minecraft:flowing_water") && above.typeId === "minecraft:air" && SOLID_ID(below.typeId)) {
          try { here.setPermutation(BlockPermutation.resolve("minecraft:water", { liquid_depth: 0 })); n++; } catch { /* left */ }
          break;
        }
        if (here.typeId === "minecraft:water") break;
      }
    }
  }
  return n;
}

/** D-C533: the WELL's drain — a 1-wide lined water channel at trench level from the well's shaft to the main street's
 *  trench (through the piece's outer wall at w0..w5). Planned from the well plot; carved as a kit op after the pieces
 *  at its t are laid (and again whenever they are re-laid). Returns the plan or null. */
function wellDrainPlan(s, st) {
  const street = (st.streets || []).find((x) => x.kind === "kit" && x.role === "main");
  const well = s.buildings.find((b) => b.settlement === st.id && b.onSquare);
  if (!street || !well) return null;
  const def = BUILDINGS[well.family];
  if (!def) return null;
  const sx = well.x + 2, sz = well.z + 3;                                      // the shaft cell (rot 0 on the square)
  const [t, w] = KIT.tw(street.f, sx, sz);
  if (w >= 0 || t < street.tmin || t >= street.tmin + street.H.length) return null;
  const H = kitHAt(street, t);
  if (H === undefined) return null;
  const cells = [];
  for (let k = w + 1; k <= 6; k++) cells.push(KIT.cellOf(street.f, t, k));
  return { t, w, H, y: H - 13, shaft: [sx, sz], cells, u: [street.f.ux, street.f.uz] };
}
function kitCarveWellDrain(dim, plan) {
  const y = plan.y;
  const set = (x, yy, z, id) => { try { const b = dim.getBlock({ x, y: yy, z }); if (b && isGround(b.typeId) && b.typeId !== "minecraft:water") b.setType(id); } catch { /* unloaded */ } };
  const water = (x, z) => { try { const b = dim.getBlock({ x, y, z }); if (b) b.setPermutation(BlockPermutation.resolve("minecraft:water", { liquid_depth: 0 })); } catch { /* unloaded */ } };
  let i = 0;
  for (const [x, z] of plan.cells) {
    const inCorridor = i >= plan.cells.length - 7;                              // the last 7 cells are w0..w6 (the piece's own blocks line them)
    if (!inCorridor) {
      set(x, y - 1, z, "minecraft:stone_bricks"); set(x, y + 1, z, "minecraft:stone_bricks");
      set(x + plan.u[0], y, z + plan.u[1], "minecraft:stone_bricks"); set(x - plan.u[0], y, z - plan.u[1], "minecraft:stone_bricks");
    }
    water(x, z);
    i++;
  }
}

/** run queued kit ops whose chunks are loaded (a few per tick); returns how many ran */
// ------------------------------------------------------------------------------------------------ TICKING CORES (D-C542)
// Work happens only where chunks tick. The clock keeps every settlement's WORK SITES ticking with the engine's own ticking
// areas (10 per world, <= 100 chunks each): one core per settlement (the square +- CORE_R) and one more per work box that
// lies outside it (a bench, a road, a far street). Slots are capped per host (`clock tickslots N`); when all are taken
// the oldest idle area (no queued work in its box) is released; a world's own areas (the harness's) are never touched.
const CORE_R = 48, CORE_SLOTS_DEFAULT = 4, CORE_PAD = 8, CORE_MAX_SIDE = 160, CORE_MAX_CHUNKS = 10;   // 10 x 10 chunks = the engine's cap (chunk-aligned)
function coreState(s) { return (s.tick = s.tick || { slots: CORE_SLOTS_DEFAULT, areas: {}, next: 1 }); }
function coreCovers(a, x, z) { return x >= a.box[0] && x <= a.box[2] && z >= a.box[1] && z <= a.box[3]; }
/** ask for a ticking area over box [x0, z0, x1, z1] for settlement st (returns the area's name, or null when no slot) */
function ensureTicking(s, st, box, why) {
  const T = coreState(s);
  const dim = world.getDimension(st.dim);
  // already covered?
  for (const a of Object.values(T.areas)) if (coreCovers(a, box[0], box[1]) && coreCovers(a, box[2], box[3])) { a.day = s.simDays; return a.name; }
  // 0.0.25b (run 0.0.25 stalled at day 6): the box is laid on CHUNK boundaries and holds at most 10 x 10 chunks — a
  // 160-block box that does not start on a chunk edge spans 11 chunks (121 > the engine's 100-chunk cap) and the add
  // failed without a word; the pad is dropped first, then the window is centred
  const axis = (lo, hi) => {
    const fit = (a2, b2) => [Math.floor(a2 / 16) * 16, Math.ceil((b2 + 1) / 16) * 16 - 1];
    let [a3, b3] = fit(lo - CORE_PAD, hi + CORE_PAD);
    if ((b3 - a3 + 1) / 16 > CORE_MAX_CHUNKS) [a3, b3] = fit(lo, hi);
    if ((b3 - a3 + 1) / 16 > CORE_MAX_CHUNKS) { const c = (lo + hi) >> 1; a3 = Math.floor(c / 16) * 16 - (CORE_MAX_CHUNKS >> 1) * 16; b3 = a3 + CORE_MAX_CHUNKS * 16 - 1; }
    return [a3, b3];
  };
  const [x0, x1] = axis(box[0], box[2]), [z0, z1] = axis(box[1], box[3]);
  const names = Object.keys(T.areas);
  if (names.length >= T.slots) {
    // release the oldest area without queued work in it
    const idle = Object.values(T.areas).filter((a) => !coreBusy(s, a)).sort((p, q) => p.day - q.day);
    if (!idle.length) { T.refused = (T.refused || 0) + 1; if (T.refused % 50 === 1) console.warn(`[CIV-CLOCK] ticking: no slot for ${why} (${T.slots} slots all busy; refused ${T.refused} times)`); return null; }
    releaseTicking(s, idle[0].name);
  }
  const name = `civ${T.next++}`;
  let res = null;
  try { res = dim.runCommand(`tickingarea add ${x0} -64 ${z0} ${x1} 320 ${z1} ${name} true`); }
  catch (e) { console.warn(`[CIV-CLOCK] ticking area ${name} (${why}): ${e}`); return null; }
  if (res && res.successCount === 0) { console.warn(`[CIV-CLOCK] ticking area ${name} (${why}): the engine refused ${x0} ${z0} .. ${x1} ${z1}`); T.next--; return null; }
  console.warn(`[CIV-CLOCK] ticking area ${name}: ${why} (${x0} ${z0} .. ${x1} ${z1}); ${Object.keys(T.areas).length + 1}/${T.slots} slots`);
  T.areas[name] = { name, st: st.id, box: [x0, z0, x1, z1], day: s.simDays, why };
  st.log.push(`day ${s.simDays.toFixed(0)}: the ${why} is kept awake (ticking area ${name}: ${x0} ${z0} .. ${x1} ${z1})`);
  return name;
}
function releaseTicking(s, name) {
  const T = coreState(s);
  const a = T.areas[name];
  if (!a) return;
  const st = s.settlements.find((x) => x.id === a.st);
  try { world.getDimension(st ? st.dim : "overworld").runCommand(`tickingarea remove ${name}`); } catch (e) { console.warn(`[CIV-CLOCK] ticking area remove ${name}: ${e}`); }
  delete T.areas[name];
}
/** does any queued op of the area's settlement fall inside it? */
function coreBusy(s, a) {
  const st = s.settlements.find((x) => x.id === a.st);
  if (!st) return false;
  if (st.palaceSurvey && st.palaceSurvey.area === a.name && !st.palace) return true;   // 1.3.221: the crown's surveyors hold their area
  // 0.0.25b (run 0.0.25b stalled at day 68: four sewer surveys inside areas that could NOT wake them — their 145-block
  // boxes reach past the areas — kept every slot "busy", so no area that could wake them was ever granted): an op keeps
  // an area busy only when the area covers the whole box the op needs awake
  // 1.3.227 (profiled: "cores" 212..230 ms a carried day — every area walked the whole queue, a wall op rebuilding its ring
  // line each time): each op's anchor and box are read once per tick for all the areas
  for (const [ox, oz, bx0, bz0, bx1, bz1] of opNeeds(st)) {
    if (!coreCovers(a, ox, oz)) continue;
    if (bx0 !== undefined && !(coreCovers(a, bx0, bz0) && coreCovers(a, bx1, bz1))) continue;
    return true;
  }
  return false;
}
const opNeedsMemo = new Map();
/** [ox, oz, (x0, z0, x1, z1 — the box that must be awake, when there is one)] for every queued op with an anchor */
function opNeeds(st) {
  const q = st.kitQueue || [];
  const m = opNeedsMemo.get(st.id);
  if (m && m.tick === system.currentTick && m.q === q && m.len === q.length) return m.list;
  const list = [];
  const walls = new Map();
  for (const op of q) {
    let anc;
    if (op.op === "wall") {
      const rec = (st.walls || []).find((r) => r.ring === op.ring);
      if (rec) { if (!walls.has(op.ring)) walls.set(op.ring, ringLine(rec.box)); anc = walls.get(op.ring)[op.a] || []; } else anc = [];
    } else anc = opAnchor(st, op);
    const [ox, oz] = anc;
    if (ox === undefined) continue;
    const R = op.op === "outfall2" ? 72 : op.op === "sealout" ? 24 : 0;
    if (R) { list.push([ox, oz, ox - R, oz - R, ox + R, oz + R]); continue; }
    if (op.op !== "road" && op.op !== "wall" && op.op !== "drain" && op.sid !== undefined && op.a !== undefined) {
      const street = st.streets.find((x) => x.kind === "kit" && x.id === op.sid);
      if (street) { const [x0, z0, x1, z1] = KIT.boxCorner(street.f, op.a, op.len || 13, -1, 13); list.push([ox, oz, Math.min(x0, x1), Math.min(z0, z1), Math.max(x0, x1), Math.max(z0, z1)]); continue; }
    }
    list.push([ox, oz]);
  }
  opNeedsMemo.set(st.id, { tick: system.currentTick, q, len: q.length, list });
  return list;
}
/** a representative world cell of a queued op (undefined when the op has none) */
function opAnchor(st, op) {
  if (op.op === "road") { const rec = (st.roads7 || []).find((r) => r.id === op.rid); if (rec && rec.cells[op.a]) return rec.cells[op.a]; return []; }
  if (op.op === "wall") { const rec = (st.walls || []).find((r) => r.ring === op.ring); if (rec) return ringLine(rec.box)[op.a] || []; return []; }
  if (op.x !== undefined && op.z !== undefined) return [op.x, op.z];
  const street = st.streets.find((x) => x.kind === "kit" && x.id === op.sid);
  if (street && op.a !== undefined) return KIT.cellOf(street.f, op.a, 6);
  return [];
}
/** the daily sweep: an area whose settlement has had no work inside it for CORE_IDLE_DAYS is released (a settlement's
 *  own core stays while any of its buildings still has a stage to place) */
const CORE_IDLE_DAYS = 3;
function coreSweep(s) {
  const T = coreState(s);
  for (const a of Object.values(T.areas)) {
    const st = s.settlements.find((x) => x.id === a.st);
    if (!st) { releaseTicking(s, a.name); continue; }
    // unfinished buildings inside the area keep it (their next stage will need the chunks)
    const pending = s.buildings.some((b) => b.settlement === st.id && coreCovers(a, b.x, b.z) && ((b.pending && b.pending.length) || b.stage < (BUILDINGS[b.family] ? BUILDINGS[b.family].stages - 1 : 4)));
    if (coreBusy(s, a) || pending) { a.day = s.simDays; continue; }
    if (s.simDays - a.day >= CORE_IDLE_DAYS) { st.log.push(`day ${s.simDays.toFixed(0)}: ticking area ${a.name} released (${a.why}: idle)`); releaseTicking(s, a.name); }
  }
}
/** a sleeping op asks for its chunks: the box around its anchor (a street stretch / a road / a wall run) */
function wakeFor(s, st, op) {
  const [ox, oz] = opAnchor(st, op);
  if (ox === undefined) return;
  op.sleeps = (op.sleeps || 0) + 1;
  if (op.sleeps < 20) return;                                                 // a few beats of patience: the player may be walking in
  op.sleeps = 0;
  ensureTicking(s, st, [ox - 24, oz - 24, ox + 24, oz + 24], `${op.op === "road" ? "road" : op.op === "wall" ? "wall" : "street"} work at ${ox} ${oz}`);
}
const kitOpTimes = [];                                                           // 1.3.226: [label, ms] of this call's ops (named in a slow line)
function processKitQueue(s) {
  let ran = 0;
  kitOpTimes.length = 0;
  let prevLabel = null, prevT = Date.now();
  const mark = (label) => { const now = Date.now(); if (prevLabel) kitOpTimes.push([prevLabel, now - prevT]); prevLabel = label; prevT = now; };
  try { return processKitQueueBody(s, mark, () => ran, (n) => { ran = n; }); } finally { mark(null); }
}
function processKitQueueBody(s, mark, getRan, setRan) {
  let ran = getRan();
  for (const st of s.settlements) {
    if (!st.kit || !st.kitQueue || !st.kitQueue.length) continue;
    const dim = world.getDimension(st.dim);
    while (st.kitQueue.length && ran < KIT_OPS_PER_TICK) {
      const op = st.kitQueue[0];
      mark(`${op.op}${op.kind ? " " + op.kind : ""}${op.sid !== undefined ? " s" + op.sid : ""}${op.a !== undefined ? " @" + op.a : ""}`);
      // A0.2: the drain decision (no blocks), the exit of one low point (its survey box must be awake), a back-fill
      if (op.op === "drain") { st.kitQueue.shift(); ran++; try { drainDecide(s, st); } catch (e) { console.warn(`[CIV-CLOCK] drain: ${e}`); } continue; }
      if (op.op === "outfall2" || op.op === "sealout") {
        const st0 = st.streets.find((x) => x.kind === "kit" && x.id === op.sid);
        if (!st0) { st.kitQueue.shift(); continue; }
        const [ax, az] = KIT.cellOf(st0.f, op.a, 6);
        const R = op.op === "outfall2" ? 72 : 24;
        let awake = false;
        try { awake = !!blockAt(dim, ax - R, op.H, az - R) && !!blockAt(dim, ax + R, op.H, az + R) && !!blockAt(dim, ax - R, op.H, az + R) && !!blockAt(dim, ax + R, op.H, az - R); } catch { awake = false; }
        // review 04:4x #2: a sewer op never runs on sleeping chunks (it used to be forced after 80 beats: the exit survey
        // read unloaded land as dry, and the back-fill skipped unloaded cells yet marked the trunk sealed) — it waits
        // and asks for its chunks; the back-fill waits for EVERY cell of its trunk
        let box = [ax - R, az - R, ax + R, az + R];
        if (awake && op.op === "sealout") {
          const hit0 = exitRec(st, op.key), cells0 = hit0 && hit0[1].plan ? (hit0[1].plan.cells || []) : [];
          for (const [cx, cz] of cells0) {
            box = [Math.min(box[0], cx - 2), Math.min(box[1], cz - 2), Math.max(box[2], cx + 2), Math.max(box[3], cz + 2)];
            let ok = false; try { ok = !!blockAt(dim, cx, op.H, cz); } catch { ok = false; }
            if (!ok) awake = false;
          }
        }
        if (!awake) {
          op.sleeps = (op.sleeps || 0) + 1;
          if (op.sleeps % 20 === 0) ensureTicking(s, st, box, `sewer ${op.op === "outfall2" ? "survey" : "sealing"} at ${ax} ${az}`);
          if (op.sleeps % 400 === 0) console.warn(`[CIV-CLOCK] ${op.op} at ${ax} ${az}: still asleep after ${op.sleeps} beats`);
          // 0.0.25b: never run on sleeping land, never block the queue either — after PARK_BEATS the op waits OUTSIDE the
          // queue (st.parked) and is queued again every PARK_DAYS (stepEconomy)
          if (op.sleeps >= PARK_BEATS) { st.kitQueue.shift(); op.sleeps = 0; (st.parked = st.parked || []).push(op); console.warn(`[CIV-CLOCK] ${op.op} at ${ax} ${az}: parked (its land sleeps)`); ran++; continue; }
          st.kitQueue.push(st.kitQueue.shift()); ran++; break;
        }
        st.kitQueue.shift(); ran++;
        try {
          if (op.op === "outfall2") { if (drainExitOp(dim, s, st, op) === "again") st.kitQueue.unshift(op); }
          else {
            const hit = exitRec(st, op.key);
            if (hit && !hit[1].sealed) { kitSealTrunk(dim, s, st, hit[0], hit[1]); hit[1].sealed = Math.floor(s.simDays); st.log.push(`day ${s.simDays.toFixed(0)}: the old sewer outfall at ${hit[1].plan.exit[0]} ${hit[1].plan.exit[1]} was back-filled (it drains no low point now)`); }
          }
        } catch (e) { op.tries = (op.tries || 0) + 1; if (op.tries < 5) st.kitQueue.push(op); console.warn(`[CIV-CLOCK] ${op.op} (try ${op.tries}): ${e}`); }
        continue;
      }
      if (op.op === "lanegallery" || op.op === "lanebranch") {             // 1.3.226: a lane's sewer gallery / a lane house's branch
        const rec = (st.roads7 || []).find((r) => r.id === op.rid && r.ln);
        if (!rec) { st.kitQueue.shift(); continue; }
        const ends = op.op === "lanegallery" ? [rec.cells[0], rec.cells[rec.cells.length - 1]] : [rec.cells[0]];
        let awake = true;
        for (const [ex, ez] of ends) { try { if (!blockAt(dim, ex, op.H, ez)) awake = false; } catch { awake = false; } }
        if (!awake) { wakeFor(s, st, { ...op, x: ends[0][0], z: ends[0][1] }); st.kitQueue.push(st.kitQueue.shift()); ran++; break; }
        st.kitQueue.shift(); ran++;
        try {
          if (op.op === "lanegallery") { const [ga, gl] = layLaneGallery(dim, st, rec); st.log.push(`day ${s.simDays.toFixed(0)}: the sewer gallery under lane ${rec.id} is dug (${ga} cells, ${gl} lined)`); }
          else {
            const b = s.buildings.find((x) => x.id === op.bid);
            const ln = laneOf(st, rec.id);
            if (b && b.kit && ln) { let cut = 0; for (const [x, y, z] of LN.laneBranchCells(ln, b.kit.leg, b.kit.branchT, b.kit.side)) { try { const blk = blockAt(dim, x, y, z); if (blk && BRANCH_CUT.includes(blk.typeId)) { blk.setType("minecraft:air"); cut++; } } catch { /* asleep */ } } b.kit.branchCut = cut; st.branchesLaid = (st.branchesLaid || 0) + 1; }
          }
        } catch (e) { op.tries = (op.tries || 0) + 1; if (op.tries < 5) st.kitQueue.push(op); console.warn(`[CIV-CLOCK] ${op.op}: ${e}`); }
        continue;
      }
      const street = st.streets.find((x) => x.kind === "kit" && x.id === op.sid);
      if (!street) { st.kitQueue.shift(); continue; }
      if (op.op === "wall") {
        const rec = (st.walls || []).find((r) => r.ring === op.ring);
        if (!rec) { st.kitQueue.shift(); continue; }
        const [wx, wz] = ringLine(rec.box)[op.a];
        let wl = false;
        try { wl = !!blockAt(dim, wx, st.h0 ?? 64, wz); } catch { wl = false; }
        if (!wl) { wakeFor(s, st, op); st.kitQueue.push(st.kitQueue.shift()); ran++; break; }
        st.kitQueue.shift(); ran++;
        try { layWallOp(dim, s, st, rec, op.a, op.len); } catch (e) { op.tries = (op.tries || 0) + 1; if (op.tries < 5) st.kitQueue.push(op); console.warn(`[CIV-CLOCK] wall op: ${e}`); }
        continue;
      }
      if (op.op === "road") {
        const rec = (st.roads7 || []).find((r) => r.id === op.rid);
        if (!rec) { st.kitQueue.shift(); continue; }
        const [rx, rz] = rec.cells[op.a];
        let rl = false;
        try { rl = !!blockAt(dim, rx, op.H, rz); } catch { rl = false; }
        if (!rl) { wakeFor(s, st, op); st.kitQueue.push(st.kitQueue.shift()); ran++; break; }
        st.kitQueue.shift(); ran++;
        try { st.roadLaid = (st.roadLaid || 0) + layRoadOp(dim, s, st, rec, op.a, op.len); rec.laidTo = Math.max(rec.laidTo || 0, op.a + op.len); if (rec.laidTo >= rec.cells.length) rec.laid = true; } catch (e) { op.tries = (op.tries || 0) + 1; if (op.tries < 5) st.kitQueue.push(op); console.warn(`[CIV-CLOCK] road op: ${e}`); }
        continue;
      }
      const len = op.len || 13;
      // review 19:1x: the prep reads one column beyond the corridor on both sides — the whole grown box must be loaded
      const [x0, z0, x1, z1] = KIT.boxCorner(street.f, op.a, len, -1, 13);
      let loaded = false;
      try { loaded = !!blockAt(dim, x0, op.H, z0) && !!blockAt(dim, x1, op.H, z1) && !!blockAt(dim, x0, op.H, z1) && !!blockAt(dim, x1, op.H, z0); } catch { loaded = false; }
      if (!loaded) { wakeFor(s, st, op); st.kitQueue.push(st.kitQueue.shift()); ran++; break; }       // sleeping chunk: to the back, next tick (and ask for it)
      st.kitQueue.shift();
      ran++;
      try {
        const boxes = plotBoxes(s, 0, null);
        if (op.op === "piece") {
          // review 19:1x: a straight whose cell an access piece or a tee now covers is never laid over it (a sleeping
          // chunk can reorder the queue: the access piece may already stand there)
          if (op.kind === "straight1" && ((street.accessLaid || []).some((c) => op.a >= c - 1 && op.a <= c + 1) || (street.tees || []).some((j) => op.a >= j.t && op.a <= j.t + 12))) continue;
          kitPrep(dim, street, op.a, len, op.H, false, boxes, kitBody(st));
          try { st.kitDrained = (st.kitDrained || 0) + kitDrain(dim, street, op.a, len, op.H, boxes); } catch (e) { console.warn(`[CIV-CLOCK] drain: ${e}`); }   // 1004b: a street is never laid into standing water
          world.structureManager.place(`pw:road/${st.width || "v"}_${op.kind}`, dim, { x: op.x, y: op.y, z: op.z }, { rotation: ROTS[op.rot] });
          try { const [cx0, cz0] = KIT.cellOf(street.f, op.a, 0), [cx1, cz1] = KIT.cellOf(street.f, op.a + len - 1, 12); st.mobsCleared = (st.mobsCleared || 0) + clearMobsIn(dim, Math.min(cx0, cx1), op.H - 15, Math.min(cz0, cz1), Math.max(cx0, cx1), op.H + 4, Math.max(cz0, cz1)); } catch (e) { console.warn(`[CIV-CLOCK] mobs street: ${e}`); }
          // a dead end whose outfall is already carved: open the chamber wall again (a re-laid piece closes it)
          for (const o of street.outfalls || []) {
            if (!o || !o.plan || o.sealed || o.gone) continue;
            if (o.v2) { if ((o.kind === "dead" && op.kind === "dead13" && o.a === op.a) || (o.kind === "side" && o.t >= op.a - 2 && o.t <= op.a + len + 1)) kitCarveTrunk(dim, st, street, o); }
            else if (op.kind === "dead13" && o.a === op.a) kitCarveOutfall(dim, street, o.a, o.plan);
          }
          // 0.0.22 (run 0.0.21: 8 manholes laid, 0 standing — the town-width resurfacing re-laid their access pieces over
          // the shafts): a laid manhole under a re-laid piece is cut again
          for (const m of street.manholes || []) if (m.laid && m.t >= op.a && m.t < op.a + len) carveManhole(dim, street, m.t, kitHAt(street, m.t), m.side);
          for (const br of street.branches || []) if (br.laid && br.t >= op.a && br.t < op.a + len) carveBranch(dim, street, br);   // 1.3.225: a re-laid piece closes a branch: cut again
          st.kitWater = (st.kitWater || 0) + kitWaterTrench(dim, street, op.a, len, op.kind);     // D-C533: running water
          if (op.kind === "straight1") st.sewerLamps = (st.sewerLamps || 0) + kitSewerLamps(dim, street, op.a);  // F5: no dark sewer
          // the well's drain enters this street at st.wellDrain.t: a piece laid over it closes the mouth -> carve again
          if (st.wellDrain && street.id === st.wellDrain.sid && op.a <= st.wellDrain.t && op.a + len > st.wellDrain.t) st.kitQueue.push({ op: "welldrain", sid: street.id, a: st.wellDrain.t, len: 1, H: st.wellDrain.H });
          st.kitLaid = (st.kitLaid || 0) + 1;
        } else if (op.op === "bridge") {
          kitPrep(dim, street, op.a, op.len, op.H, true, boxes);
          kitBridge(dim, st, street, op.a, op.len, op.H);
        } else if (op.op === "landing") {                                      // 1.3.232 (#6 b): full sidewalk blocks up to the floor
          const cells = KIT.landingCells(street.f, op.side, op.doorT, (t) => kitHAt(street, t), op.H, st.width || "v");
          for (const c of cells) for (let y = c.y0; y <= c.y1; y++) dim.getBlock({ x: c.x, y, z: c.z })?.setType("minecraft:smooth_stone");
          st.landingsLaid = (st.landingsLaid || 0) + 1;
        } else if (op.op === "branch") {
          const br = (street.branches || []).find((r) => r.t === op.a && r.side === op.side);
          if (br) { br.cut = carveBranch(dim, street, br); br.laid = true; st.branchesLaid = (st.branchesLaid || 0) + 1; }
        } else if (op.op === "manhole") {
          if (carveManhole(dim, street, op.a, op.H, op.side)) {                 // F3 (D-C538): a public shaft in the sidewalk
            const mrec = (street.manholes || []).find((m) => m.t === op.a);
            if (mrec) mrec.laid = true;
            st.manholesLaid = (st.manholesLaid || 0) + 1;
            const [mx, mz] = KIT.cellOf(street.f, op.a, op.side < 0 ? 1 : 11);
            (st.manholeCells = st.manholeCells || []).push([mx, op.H, mz]);
          }
        } else if (op.op === "welldrain") {
          const plan = wellDrainPlan(s, st);
          if (plan) {
            let shaftWet = false;
            try { const b = blockAt(dim, plan.shaft[0], plan.y, plan.shaft[1]); shaftWet = !!b && b.typeId === "minecraft:water"; } catch { shaftWet = false; }
            if (!shaftWet) { op.tries = (op.tries || 0) + 1; if (op.tries < 20) st.kitQueue.push(op); continue; }     // the well's s0 is not down yet
            kitCarveWellDrain(dim, plan);
            st.wellDrain = { sid: street.id, t: plan.t, H: plan.H, cells: plan.cells.length, done: true };
            if (!st.wellDrainLogged) { st.wellDrainLogged = true; st.log.push(`day ${load().simDays.toFixed(0)}: the well's drain runs ${plan.cells.length} cells to the street's sewer`); }
          }
        } else if (op.op === "outfall") {
          street.outfalls = street.outfalls || [];
          let o = street.outfalls.find((q) => q.a === op.a);
          if (!o) {
            const veto = kitVeto(s);
            let plan = KIT.planOutfall(liveSite(dim, siteOf(st)), street.f, op.a, op.end, op.H, 72, (x, z) => veto(x, z));
            // kitvillage-0.0.8: one exit opened into solid stone (the site field's ground differed from the live blocks):
            // the exit must open on AIR or water at channel level — walk on along the last direction up to 8 cells
            if (plan) {
              const isOpen = (x, z) => { try { const b = blockAt(dim, x, plan.floorY, z); return !!b && (b.typeId === "minecraft:air" || b.typeId.includes("water")); } catch { return false; } };
              let [ex, ez] = plan.exit, k = 0;
              while (k < 8 && !isOpen(ex + plan.dir[0], ez + plan.dir[1])) { ex += plan.dir[0]; ez += plan.dir[1]; plan.cells.push([ex, ez]); k++; }
              if (!isOpen(ex + plan.dir[0], ez + plan.dir[1])) { st.log.push(`day ${load().simDays.toFixed(0)}: street ${street.id}'s ${op.end} sewer found no open face at ${ex} ${plan.floorY} ${ez} (closed)`); plan = null; }
              else plan.exit = [ex, ez];
            }
            o = { a: op.a, end: op.end, plan: plan ? { cells: plan.cells, exit: plan.exit, dir: plan.dir, floorY: plan.floorY } : null };
            street.outfalls.push(o);
            if (plan) st.log.push(`day ${load().simDays.toFixed(0)}: a sewer outfall at ${plan.exit[0]} ${plan.floorY} ${plan.exit[1]} (${plan.cells.length} cells of tunnel)`);
            else st.log.push(`day ${load().simDays.toFixed(0)}: street ${street.id}'s ${op.end} sewer has no way out to daylight within 72 blocks (closed)`);
          }
          if (o.plan) kitCarveOutfall(dim, street, op.a, o.plan);
        }
      } catch (e) {
        // review 19:1x: an op that failed (a chunk unloaded under it) is tried again later, up to 5 times — never lost
        op.tries = (op.tries || 0) + 1;
        if (op.tries < 5) st.kitQueue.push(op);
        console.warn(`[CIV-CLOCK] kit ${op.op} ${op.kind || ""} (try ${op.tries}): ${e}`);
      }
    }
  }
  return ran;
}

/** cells nothing new may take (review 19:1x): every plot box, square and park, every corridor cell (kit + legacy), every
 *  sewer outfall tunnel (centre +- 2) — houses are 15 deep and would cut a tunnel; a tunnel would cut a cellar */
function tunnelCells(s) {
  const m = new Set();
  for (const st of s.settlements) for (const street of st.streets || []) for (const o of street.outfalls || []) {
    if (!o || !o.plan || o.sealed) continue;
    for (const [x, z] of o.plan.cells) for (let dx = -2; dx <= 2; dx++) for (let dz = -2; dz <= 2; dz++) m.add(`${x + dx},${z + dz}`);
  }
  return m;
}
// 1.3.227 (gate 227-1: one sewer-outfall candidate took 964 ms — the veto was rebuilt for every candidate, copying every
// street body into a string map, and each query scanned every plot box): the veto is CACHED until a plot, a street piece
// or an outfall changes, its cells are number keys and the plot boxes are indexed by 16-block cell (same answers)
let vetoCache = null;
function kitVeto(s) {
  let tun = 0;
  for (const st of s.settlements) for (const street of st.streets || []) for (const o of street.outfalls || []) if (o && o.plan && !o.sealed) tun += o.plan.cells.length;
  const key = `${s.nextId}:${s.buildings.length}:${tun}:${s.settlements.map((x) => `${x.kitVer || 0}/${(x.streets || []).length}/${x.square ? 1 : 0}/${x.park ? 1 : 0}`).join(",")}`;
  if (vetoCache && vetoCache.key === key) return vetoCache.fn;
  const boxes = plotBoxes(s, 0, null);
  const cells = new Set();
  const K = (x, z) => (x + OCC_OFF) * OCC_W + (z + OCC_OFF);
  const addKey = (k) => { const c = k.indexOf(","); cells.add(K(+k.slice(0, c), +k.slice(c + 1))); };
  for (const stl of s.settlements) for (const k of bodyOf(stl).keys()) addKey(k);
  for (const k of tunnelCells(s)) addKey(k);
  const grid = new Map();
  for (const bx of boxes) {
    for (let gx = Math.floor(bx[0] / 16); gx <= Math.floor(bx[1] / 16); gx++) for (let gz = Math.floor(bx[2] / 16); gz <= Math.floor(bx[3] / 16); gz++) {
      const gk = gx * 100003 + gz;
      if (!grid.has(gk)) grid.set(gk, []);
      grid.get(gk).push(bx);
    }
  }
  const fn = (x, z) => {
    if (cells.has(K(x, z))) return true;
    const cell = grid.get(Math.floor(x / 16) * 100003 + Math.floor(z / 16));
    return !!cell && cell.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  };
  vetoCache = { key, fn };
  return fn;
}

/** the land under a slot (R1 §4.5 rules): returns { kind, cut, fill, unknown, water } — kind: level | stepped | stilts | reject */
function slotRelief(lsite, f, slot, allowStilts = false) {
  const [bx0, bx1, bz0, bz1] = slot.box;
  const [ta, wa] = KIT.tw(f, bx0, bz0), [tb, wb] = KIT.tw(f, bx1, bz1);
  const tmin = Math.min(ta, tb) - 1, tmax = Math.max(ta, tb) + 1;
  let wmin = Math.min(wa, wb), wmax = Math.max(wa, wb);
  if (slot.side > 0) wmax += 1 + BENCH; else wmin -= 1 + BENCH;           // the rear bench + its wall
  let lo = Infinity, hi = -Infinity, unknown = 0, water = 0, n = 0;
  const cells = [];                                                          // 1.3.228 (B6 / TR2 + TR3): judged by percentiles
  for (let t = tmin; t <= tmax; t++) for (let w = wmin; w <= wmax; w++) {
    const cw = slot.corr || [0, 12];                                          // 1.3.226: a lane's band is w -3..3
    if (slot.side > 0 ? w <= cw[1] : w >= cw[0]) continue;                   // never the corridor
    const [x, z] = KIT.cellOf(f, t, w);
    const g = lsite.at(x, z);
    n++;
    if (g === undefined) { unknown++; continue; }
    const wet = lsite.isWater(x, z);
    if (wet) water++;
    cells.push({ h: g, wet });
    if (g < lo) lo = g;
    if (g > hi) hi = g;
  }
  if (unknown > 0) return { kind: "unknown", cut: 0, fill: 0, unknown, water };   // 1.3.224: unread ground waits (the cliff-edge houses came through here)
  // 1.3.228 (B6 / TR2 + TR3): a lot is judged on its 20th..80th percentile heights with a water share <= 8 % and a budget of
  // bad cells (<= 10, or 5 % of a big box) — one boulder or one wet cell no longer vetoes a lot; a true cliff still does
  // (a drop beyond BUILD_UP_MAX + 6 at any cell still rejects)
  const judged = PLAN.judgeLot(cells, slot.H, cells.length);
  if (!judged.ok) return { kind: "reject", cut: Math.max(0, hi - slot.H), fill: Math.max(0, slot.H - lo), unknown, water, why: judged.why };
  // cuts stay judged on the highest cell (nothing inside the box cuts a boulder away); a single deep hole or a wet cell is
  // FILLED by the terrace (it fills air and water up to the slab), so the drop is judged on the 20th percentile
  if (slot.H - lo > (allowStilts ? STILTS_MAX : BUILD_UP_MAX) + 6) return { kind: "reject", cut: hi - slot.H, fill: slot.H - lo, unknown, water, why: "extreme" };
  const cut = Math.max(0, hi - slot.H), fill = Math.max(0, slot.H - judged.lo);
  let kind = "level";
  if (false) kind = "reject";
  else if (cut > CUT_MAX) kind = "reject";
  else if (cut > WALL_MAX && fill > WALL_MAX) kind = "reject";                  // both a deep cut and a deep drop: no
  else if (fill > BUILD_UP_MAX) kind = allowStilts && fill <= STILTS_MAX ? "stilts" : "reject";
  else if (cut > WALL_MAX) kind = "stepped";
  else if (fill > PODIUM_MAX) kind = "embankment";                               // built up, stepped down in lifts of 3
  else if (fill > WALL_MAX) kind = "podium";
  return { kind, cut, fill, unknown, water };
}

/** a plot's veto on a kit settlement: its box (+1 margin) touches no other plot, square or park; its box touches no
 *  corridor cell of ANY settlement */
// 1.3.226 (gate 225-1: a slot search took 0.4-0.6 s, several a day — every call rebuilt the road / tunnel / legacy sets and
// tested every plot box): the sets are cached until the town changes (buildings, roads, streets, outfalls), and the
// plot boxes are indexed by 16-block chunk so a candidate is tested against its neighbours only
let freeCache = { key: null };
function freeSets(s) {
  let sig = `${s.buildings.length}:${s.nextId}`;
  for (const st2 of s.settlements) sig += `|${st2.kitVer || 0}:${(st2.roads7 || []).length}:${(st2.streets || []).reduce((a, x) => a + (x.outfalls || []).length, 0)}`;
  if (freeCache.key === sig) return freeCache;
  const boxes = plotBoxes(s, 0, null);
  const grid = new Map();
  for (const bx of boxes) for (let i = Math.floor(bx[0] / 16); i <= Math.floor(bx[1] / 16); i++) for (let j = Math.floor(bx[2] / 16); j <= Math.floor(bx[3] / 16); j++) { const k = `${i},${j}`; if (!grid.has(k)) grid.set(k, []); grid.get(k).push(bx); }
  const roadCells = new Set();
  for (const st2 of s.settlements) for (const r of st2.roads7 || []) for (const [x, z] of r.cells) for (let dx = -KIT.ROAD_HALF; dx <= KIT.ROAD_HALF; dx++) for (let dz = -KIT.ROAD_HALF; dz <= KIT.ROAD_HALF; dz++) roadCells.add(`${x + dx},${z + dz}`);
  freeCache = { key: sig, boxes, grid, roadCells, legacy: streetHeights(s), tunnels: tunnelCells(s), bodies: s.settlements.filter((x) => x.kit).map((x) => kitBody(x)) };
  return freeCache;
}
function boxesNear(fc, x0, x1, z0, z1) {
  const out = new Set();
  for (let i = Math.floor(x0 / 16); i <= Math.floor(x1 / 16); i++) for (let j = Math.floor(z0 / 16); j <= Math.floor(z1 / 16); j++) for (const bx of fc.grid.get(`${i},${j}`) || []) out.add(bx);
  return out;
}
function kitFree(s, st = null, lsite = null, allowStilts = false, whyOut = null, allowPlateau = false) {
  const fc = freeSets(s);
  const bodies = fc.bodies;
  const legacy = fc.legacy;
  const tunnels = fc.tunnels;
  // 0.0.22 (village II placed 2 of 5 plots, reason unknown): why each slot was refused, counted on the settlement
  const why = whyOut || (st ? (st.slotWhy = st.slotWhy || { plot: 0, tunnel: 0, body: 0, legacy: 0, land: 0 }) : { plot: 0, tunnel: 0, body: 0, legacy: 0, land: 0 });
  // 0.0.25 (run 0.0.24: the butcher #15 stood ON the bench road's last 8 cells — 6 road cells read as air under its floor):
  // the narrow roads (7 wide, their elbows) are part of the veto
  const roadCells = fc.roadCells;
  return (big, box, slot, f) => {
    const [bx0, bx1, bz0, bz1] = big;
    for (const [x0, x1, z0, z1] of boxesNear(fc, bx0, bx1, bz0, bz1)) if (bx0 <= x1 && bx1 >= x0 && bz0 <= z1 && bz1 >= z0) { why.plot++; return false; }
    if (boxInReserve(s, bx0, bx1, bz0, bz1)) { why.crown = (why.crown || 0) + 1; return false; }        // 1.3.226: the crown's reserved land
    for (let x = box[0]; x <= box[1]; x++) for (let z = box[2]; z <= box[3]; z++) {
      const k = `${x},${z}`;
      if (tunnels.has(k)) { why.tunnel++; return false; }
      if (roadCells.has(k)) { why.road = (why.road || 0) + 1; return false; }
      if (legacy.has(k)) { why.legacy++; return false; }
      if (bodies.some((m) => m.has(k))) { why.body++; return false; }
    }
    // D-C534 §2.1: the land rule (his C3 / C5) — too much cut or drop, or water under the plot: no house here
    if (slot && f && lsite) {
      let land = slotRelief(lsite, f, slot, allowStilts);
      slot.land = land;
      if (land.kind === "unknown") { why.unread = (why.unread || 0) + 1; return false; }
      // 1.3.230 (PL): a frontage rising 2 always stands on its PLATEAU; a lot the land rule refuses may take one (the
      // existing kinds — level, stepped, podium, embankment, stilts — keep every lot they already take)
      // 1.3.232 (#6 a): a floor raised to a ramp's high level (slot.doorRamp) stands on a plateau pad at P = slot.H
      const rampDoor = !!(slot.doorRamp && slot.doorRamp.raised > 0);
      if (slot.plateau || rampDoor || (allowPlateau && land.kind === "reject")) {
        const pl = plateauLand(s, lsite, f, slot, fc);
        if (pl.kind === "plateau") { land = pl; slot.land = pl; why.plateauOk = (why.plateauOk || 0) + 1; }
        else {
          why.plateauNo = (why.plateauNo || 0) + 1;
          if (st) { st.plateauWhy = st.plateauWhy || {}; st.plateauWhy[pl.why] = (st.plateauWhy[pl.why] || 0) + 1; }
          if (pl.why === "unknown") { why.unread = (why.unread || 0) + 1; return false; }
          if (slot.plateau || rampDoor) { why.land++; return false; }
        }
      }
      if (land.kind === "reject") { why.land++; if (st) { st.landRejects = (st.landRejects || 0) + 1; st.landLast = [slot.box[0], slot.box[2], land.cut, land.fill, land.water]; } return false; }
    }
    return true;
  };
}

// ------------------------------------------------------------------------------------------------ 1.3.230 (PL) FRONTAGE PLATEAUS
// The planner's half is pure (PLAN.planPlateau in pw_civ_plan.js, node-tested in tests/test_plateau.mjs). Here: the
// street's facts at the pad's ring, the veto per cell, the slot -> plateau adapter (plan time, on the site field), the
// budgeted build job (live ground, guarded reads) and the plot's bill (stageBillOf).
/** a street's sidewalk H at frame t, and the H of its sewer hall there (flat / ramp cells outside every junction window;
 *  a bridge, a dead end or a window has none — the drain then takes the other end, or a soakaway) */
function streetRing(street) {
  const kinds = new Array(street.H.length).fill(null);
  for (const g of street.segs || []) for (let i = g.a; i < g.a + g.len && i < kinds.length; i++) kinds[i] = g.kind;
  const wins = (street.reserved || []).map(([a, b]) => [a, b]).concat((street.tees || []).map((j) => [j.t, j.t + 12]));
  return {
    H: (t) => kitHAt(street, t),
    hall: (t) => {
      const i = t - street.tmin, k = kinds[i];
      if (k !== "flat" && k !== "ramp") return undefined;
      return wins.some(([a, b]) => t >= a && t <= b) ? undefined : street.H[i];
    },
  };
}
/** a cell to a plateau's works: "plot" (a plot / square / park box, the crown's reserve), "street" (a corridor, a road, a
 *  tunnel, a legacy street) or null; self = the plateau's own box */
function plateauBlocked(s, fc, x, z, self = null) {
  for (const [x0, x1, z0, z1] of boxesNear(fc, x, x, z, z)) {
    if (self && x0 === self[0] && x1 === self[1] && z0 === self[2] && z1 === self[3]) continue;
    if (x >= x0 && x <= x1 && z >= z0 && z <= z1) return "plot";
  }
  if (inReserve(s, x, z)) return "plot";
  const k = `${x},${z}`;
  if (fc.tunnels.has(k) || fc.roadCells.has(k) || fc.legacy.has(k) || fc.bodies.some((m) => m.has(k))) return "street";
  return null;
}
/** the plateau's frame -> world cell: q along the frontage (0 = slot.at), d away from the corridor (0 = the row against it) */
function plateauFrame(f, side, at) { return (q, d) => KIT.cellOf(f, at + q, side > 0 ? KIT.W + d : -1 - d); }
/** the plot's compact land record (saved on the building: no cell lists — the job plans again on the live ground) */
function plateauRecord(res, slot) {
  return { kind: "plateau", P: res.P, cut: res.cut, fill: res.fill, rise: slot.plateau ? slot.plateau.rise : 0, step: slot.plateau ? slot.plateau.step : 0,
           stone: res.bill.stone, iron: res.bill.iron, earth: res.bill.earth, labourDays: res.bill.labourDays, wages: res.bill.wages, drain: res.drain.to };
}
/** slot -> its plateau, judged on the site field (the ground before the town worked it): the land record, or
 *  { kind: "reject", why } (why: cut / fill / drop / water / plot / street / tree / unknown) */
function plateauLand(s, lsite, f, slot, fc, park = false) {
  const street = slot._street || null;
  const [, wa] = KIT.tw(f, slot.box[0], slot.box[2]), [, wb] = KIT.tw(f, slot.box[1], slot.box[3]);
  const xz = plateauFrame(f, slot.side, slot.at);
  const ring = street ? streetRing(street) : null;
  const res = PLAN.planPlateau({
    fz: slot.len, depth: Math.abs(wb - wa) + 1, P: slot.H,
    Hring: (q) => (ring ? ring.H(slot.at + q) : slot.Hring ? slot.Hring[q + 1] : undefined),
    hallAt: (q) => (ring ? ring.hall(slot.at + q) : undefined),
    ground: (q, d) => { const [x, z] = xz(q, d); const h = lsite.at(x, z); return h === undefined ? undefined : { h, wet: lsite.isWater(x, z) }; },
    blocked: (q, d) => { const [x, z] = xz(q, d); return plateauBlocked(s, fc, x, z); },
    boxFillMax: park ? PLAN.PLATEAU.fillMax : undefined,
  });
  return res.ok ? plateauRecord(res, slot) : { kind: "reject", why: res.why, cut: 0, fill: 0, water: 0 };
}

// D-C534 §3 DISTRICTS (R1 §4.8): where a kind of building prefers to stand — prestige on the main street by the square,
// crafts on the side streets, homes on the side streets (then the main), edge trades (quarry, lumberyard, farms) at the
// far ends of the outermost streets
const DISTRICT = { town_hall: "prestige", inn: "prestige", bakery: "prestige", well: "prestige", manor: "prestige", chapel: "prestige",
                   church: "prestige", market: "prestige", palace: "prestige", butcher: "craft", smithy: "craft", brickworks: "craft",
                   cottage_s: "homes", cottage_m: "homes", cottage_l: "homes", townhouse: "homes",
                   lumberyard: "edge", quarry: "edge", farm_wheat: "edge", farm_cattle: "edge", farm_terrace: "edge", lime_kiln: "edge" };
function squareCentre(st) { return st.square ? [st.square.x + 6, st.square.z + 6] : [0, 0]; }
function streetDist(st, street) {
  const [cx, cz] = squareCentre(st);
  const mid = street.mid ?? (street.tmin + street.H.length / 2);
  const [x, z] = KIT.cellOf(street.f, Math.round(mid), 6);
  return Math.abs(x - cx) + Math.abs(z - cz);
}
/** a slot for a building on a kit settlement, by its district: the streets in the district's order, packed from the
 *  district's anchor (the square's side, or the far end for edge trades) outward */
const GREENBELT = 24;
const GATE_MIN = 26;                                                     // B9 (TR5): no adjacent gates
const TR1_SPACING = 30;                                                  // B6 (TR1): two bakeries / butchers never closer
function kitSlot(s, st, family, only = null, allowStilts = false, allowPlateau = false) {
  const def = BUILDINGS[family];
  const sz = shaftZOf(def);
  const free = kitFree(s, st, liveSite(world.getDimension(st.dim), siteOf(st)), allowStilts, null, allowPlateau);
  const plOpts = allowPlateau ? { riseMax: PLAN.PLATEAU.frontRise, doorStep: PLAN.PLATEAU.doorStep } : null;   // 1.3.230 (PL)
  const kind = (def.stem || "").replace(/^mvv_/, "").replace(/_[a-d]_r\d+$/, "");
  const district = DISTRICT[kind] || "homes";
  const streets = st.streets.filter((x) => x.kind === "kit");
  const byDist = streets.slice().sort((p, q) => streetDist(st, p) - streetDist(st, q));
  const mains = byDist.filter((x) => x.role === "main" && !x.bench), rest = byDist.filter((x) => !(x.role === "main" && !x.bench));
  let order;
  if (district === "prestige") order = mains.concat(rest);
  else if (district === "craft") order = rest.filter((x) => x.role !== "connector").concat(mains, rest.filter((x) => x.role === "connector"));
  else if (district === "edge") order = byDist.slice().reverse();
  // 1.3.226 (his 20:48: business and its housing in the centre, homes moving out to the edge as the town grows): homes take
  // the OUTERMOST streets first, packed from their far end inward; businesses keep the streets nearest the square
  else order = byDist.filter((x) => x.role !== "connector").reverse().concat(byDist.filter((x) => x.role === "connector"));
  // 1.3.228 (B6 / TR1): the manor prefers the streets nearest the park (the rich by the park); a second bakery or butcher
  // (not a neighbourhood centre's) never stands within TR1_SPACING of another of its kind
  const parkAt = st.park && st.park.box ? [(st.park.box[0] + st.park.box[1]) / 2, (st.park.box[2] + st.park.box[3]) / 2] : null;
  const midCell = (x) => KIT.cellOf(x.f, Math.round(x.mid ?? (x.tmin + x.H.length / 2)), 6);
  if (kind === "manor" && parkAt) order = order.slice().sort((p2, q2) => { const a2 = midCell(p2), b2 = midCell(q2); return (Math.abs(a2[0] - parkAt[0]) + Math.abs(a2[1] - parkAt[1])) - (Math.abs(b2[0] - parkAt[0]) + Math.abs(b2[1] - parkAt[1])); });
  const gateCells = (st.roads7 || []).filter((r) => r.gate).flatMap((r) => r.cells || []);
  const gateRoadNear = (big) => gateCells.some(([x, z]) => x >= big[0] - 3 && x <= big[1] + 3 && z >= big[2] - 3 && z <= big[3] + 3);
  const twins = (kind === "bakery" || kind === "butcher") && !only ? plotsOf(s, st).filter((b) => short(b) === kind && b.centre === undefined).map((b) => [b.x, b.z]) : [];
  const [cx, cz] = squareCentre(st);
  for (const street of only ? [only.street] : order) {
    const { bySide, noShaft } = kitStretches(street, st);
    const taken = new Set(street.access || []);
    let mid = only && only.mid !== undefined ? only.mid : (street.mid ?? (street.tmin + street.H.length / 2));
    if (district === "edge" || (district === "homes" && !only)) {
      // the end farther from the square (1.3.226: homes too — they fill from the outskirts inward)
      const [ax, az] = KIT.cellOf(street.f, street.tmin, 6), [bx, bz] = KIT.cellOf(street.f, street.tmin + street.H.length - 1, 6);
      mid = (Math.abs(ax - cx) + Math.abs(az - cz)) > (Math.abs(bx - cx) + Math.abs(bz - cz)) ? street.tmin + 13 : street.tmin + street.H.length - 14;
    }
    // F2 (D-C538, R5): the GREENBELT — once the wall stands, a ring GREENBELT cells wide outside it stays unbuilt (the
    // benches are their own districts and keep building)
    const freeS0 = street.bench ? free : (big, box, slot, f) => {
      for (const w of st.walls || []) {
        const [wx0, wx1, wz0, wz1] = w.box;
        const inBand = big[1] >= wx0 - GREENBELT && big[0] <= wx1 + GREENBELT && big[3] >= wz0 - GREENBELT && big[2] <= wz1 + GREENBELT
          && !(big[0] >= wx0 && big[1] <= wx1 && big[2] >= wz0 && big[3] <= wz1);
        // 1.3.228 (B9 / TR5): the gates' suburbs — homes whose lot touches a gate's road out are exempt from the greenbelt
        if (inBand && district === "homes" && gateRoadNear(big)) { st.slotWhy = st.slotWhy || {}; st.slotWhy.suburb = (st.slotWhy.suburb || 0) + 1; continue; }
        if (inBand) { st.slotWhy = st.slotWhy || {}; st.slotWhy.greenbelt = (st.slotWhy.greenbelt || 0) + 1; return false; }
      }
      if (twins.length && twins.some(([x, z]) => Math.abs(x - big[0]) + Math.abs(z - big[2]) < TR1_SPACING)) { st.slotWhy = st.slotWhy || {}; st.slotWhy.twin = (st.slotWhy.twin || 0) + 1; return false; }
      return free(big, box, slot, f);
    };
    const freeS = (big, box, slot, f) => { if (slot) slot._street = street; return freeS0(big, box, slot, f); };   // 1.3.230 (PL): the ring's street facts
    const slot = KIT.placeAlong(street.f, bySide, def, sz, mid, freeS, taken, (street.nextSide = -(street.nextSide || -1)), 1, noShaft, plOpts);
    if (slot) return { slot, street };
  }
  return null;
}
// ------------------------------------------------------------------------------------------------ B2 NEIGHBOURHOOD CENTRES (his 23:30, D-C545)
// From town II every PARALLEL street (role side, not a bench) grows its own small centre: a well as its fountain near the
// street's middle, a bakery and a butcher beside it — the neighbourhood's market. Its people take their midday and dusk
// there instead of the main square (the schedule). Built like any plot (from the ledger, by the builders).
const CENTRE_FROM = 4;                                                          // TIERS index: town2
function openCentres(s, st, pick, delay0 = 0) {
  const made = [];
  if (!st.kit || TIERS.indexOf(st.tier) < CENTRE_FROM) return made;
  st.centres = st.centres || [];
  let k = 0;
  for (const street of st.streets.filter((x) => x.kind === "kit" && x.role === "side" && !x.bench)) {
    if (st.centres.some((c) => c.sid === street.id)) continue;
    const mid = street.mid ?? (street.tmin + street.H.length / 2);
    const well = kitAddPlot(s, st, familyOf("well", skinsOf("well")[0]), delay0 + k * VILLAGE_STAGGER, { street, mid });
    if (!well) continue;
    well.centre = street.id; k++;
    const c = { sid: street.id, well: well.id, shops: [], day: s.simDays };
    for (const nm of ["bakery", "butcher"]) {
      const skins = skinsOf(nm);
      const b = kitAddPlot(s, st, familyOf(nm, skins[Math.floor(pick() * skins.length)]), delay0 + k * VILLAGE_STAGGER, { street, mid: well.kit.at + 6 });
      if (b) { b.centre = street.id; c.shops.push(b.id); k++; }
    }
    st.centres.push(c);
    made.push(well);
    st.log.push(`day ${s.simDays.toFixed(0)}: a neighbourhood market is laid out on street ${street.id} (a well, ${c.shops.length} shop(s))`);
  }
  return made;
}
/** the centre a household uses (its street's), or null (the main square) */
function centreOf(s, st, homeB) {
  if (!homeB || !homeB.kit || !st.centres) return null;
  const c = st.centres.find((x) => x.sid === homeB.kit.sid);
  if (!c) return null;
  const w = s.buildings.find((b) => b.id === c.well);
  return w && w.stage >= 4 ? w : null;
}
/** a street's house frontage per side: flat stretches minus the junction windows on THAT side (reserved or built tees);
 *  noShaft = every window (an access piece is 13 wide: it may not land in any junction window) */
function kitStretches(street, st = null) {
  // a built tee always; a reserved (unused) window unless released
  const wins = (street.reserved || []).filter((r) => r[3] || !(st && winReleased(st, street, r[2], r[0]))).map(([a, b, side]) => [a, b, side])
    .concat((street.tees || []).map((j) => [j.t, j.t + 12, j.side]));
  // D-C534 §3 / 0.0.15: the grid lines stay free for cross streets on EVERY street from the start (a window a house took
  // at village I could never close its block at town) — 1.3.225: until WIN_RELEASE side-street searches failed from it
  if (st && st.gridMid !== undefined && !street.bench) {
    const tOff = tOffOf(street), tmin = street.tmin, tmax = street.tmin + street.H.length - 1;
    for (const [a, b] of gridWindowsIn(st.gridMid, tOff, tmin, tmax)) for (const sd of [1, -1]) if (!winReleased(st, street, sd, a)) wins.push([a, b, sd]);
  }
  const bySide = {};
  // 1.3.225: house frontage runs over flat AND ramp cells (KIT.frontStretches); a house fronts at most FRONT_RISE of rise
  for (const side of [1, -1]) bySide[String(side)] = KIT.frontStretches(kitPlan(street), street.tmin, wins.filter((w) => w[2] === side).map(([a, b]) => [a, b]));
  return { bySide, noShaft: wins.map(([a, b]) => [a, b]) };
}
/** 1.3.225: a junction window that WIN_RELEASE side-street searches could not open is given back to the houses (the
 *  census: the windows held 13 of every 56 cells on both sides of every street, most of them never opened) */
const WIN_RELEASE = 3;
const winKey = (street, side, t) => `${street.id}:${side}:${t}`;
function winReleased(st, street, side, t) { return ((st.winFail || {})[winKey(street, side, t)] || 0) >= WIN_RELEASE; }
function winFailed(st, street, side, t) { st.winFail = st.winFail || {}; const k = winKey(street, side, t); st.winFail[k] = (st.winFail[k] || 0) + 1; if (st.winFail[k] === WIN_RELEASE) st.winReleased = (st.winReleased || 0) + 1; }

// 1.3.225 FRONTAGE CENSUS (his 16:50 / 20:01: growth stalls at ~45 plots): every street, both sides, packed with one house
// size from end to end; each position that cannot take the house is charged to the FIRST rule that refused it. Read-only.
function frontageCensus(s, st, family) {
  const def = BUILDINGS[family];
  if (!def) return null;
  const fz = def.size[2], sz = shaftZOf(def);
  const lsite = liveSite(world.getDimension(st.dim), siteOf(st));
  const why = { plot: 0, tunnel: 0, body: 0, legacy: 0, land: 0 };          // zeros: kitFree counts with ++ (diag1 showed these as '?')
  const free = kitFree(s, null, lsite, false, why);
  const freeP = kitFree(s, null, lsite, false, {}, true);                     // 1.3.230 (PL): the plateau's own counters, apart
  const out = { family, fz, streets: [], total: { corridor: 0, flat: 0, fits: 0, why: {} } };
  const charge = (o, k) => { o[k] = (o[k] || 0) + 1; out.total.why[k] = (out.total.why[k] || 0) + 1; };
  for (const street of st.streets.filter((x) => x.kind === "kit")) {
    const { bySide, noShaft } = kitStretches(street, st);
    const taken = new Set(street.access || []);
    const row = { id: street.id, role: street.role, bench: !!street.bench, len: street.H.length, flat: 0, fits: 0, why: {} };
    for (const side of [1, -1]) {
      for (const sx of bySide[String(side)]) {
        row.flat += sx.b - sx.a + 1;
        let at = sx.a;
        while (at + fz - 1 <= sx.b) {
          // the same law as KIT.placeAlong (1.3.225): rise along the frontage, then the world's veto; a shaft that cannot
          // have its own hatch makes a cesspit house (counted, never a refusal)
          let reason = null, Hf;
          if (sx.Hs) { let lo = Infinity, hi = -Infinity; for (let q = at - sx.a; q < at - sx.a + fz; q++) { lo = Math.min(lo, sx.Hs[q]); hi = Math.max(hi, sx.Hs[q]); } if (hi - lo > KIT.FRONT_RISE) reason = "rise"; Hf = hi; }
          const slot = KIT.slotFor(street.f, sx, side, def, sz, at, Hf);
          let cess = false;
          if (!reason && slot.shaftT !== null) {
            let ok = slot.shaftT - 1 >= sx.a && slot.shaftT + 1 <= sx.b;
            if (ok && sx.Hs) { const q = slot.shaftT - sx.a; ok = sx.kinds.slice(q - 1, q + 2) === "fff" && sx.Hs[q - 1] === sx.Hs[q] && sx.Hs[q + 1] === sx.Hs[q]; }
            if (ok && noShaft.some(([na, nb]) => slot.shaftT + 1 >= na && slot.shaftT - 1 <= nb)) ok = false;
            if (ok) for (const c of taken) if (c !== slot.shaftT && Math.abs(c - slot.shaftT) < KIT.ACCESS) { ok = false; break; }
            cess = !ok;
          }
          const [x0, x1, z0, z1] = slot.box, big = [x0 - 1, x1 + 1, z0 - 1, z1 + 1];
          if (!reason && !street.bench) for (const w of st.walls || []) {
            const [wx0, wx1, wz0, wz1] = w.box;
            if (big[1] >= wx0 - GREENBELT && big[0] <= wx1 + GREENBELT && big[3] >= wz0 - GREENBELT && big[2] <= wz1 + GREENBELT
                && !(big[0] >= wx0 && big[1] <= wx1 && big[2] >= wz0 && big[3] <= wz1)) { reason = "greenbelt"; break; }
          }
          if (!reason) {
            const before = JSON.stringify(why);
            const ok = free(big, slot.box, slot, street.f);
            if (ok) { row.fits++; out.total.fits++; if (cess) { row.branch = (row.branch || 0) + 1; out.total.branch = (out.total.branch || 0) + 1; } at += fz + 1; continue; }
            const now = why; const prev = JSON.parse(before);
            reason = Object.keys(now).find((k) => (now[k] || 0) !== (prev[k] || 0)) || "?";
            if (reason === "land" && slot.land) reason = `land ${slot.land.cut > CUT_MAX ? "cut" : slot.land.fill > BUILD_UP_MAX ? "drop" : slot.land.water ? "water" : "both"}`;
          }
          // 1.3.230 (PL): a position refused for its frontage's rise or its land — a PLATEAU may take it (counted as a fit)
          if ((reason === "rise" || reason.startsWith("land")) && censusPlateau(st, street, sx, side, def, sz, at, freeP)) {
            row.fits++; out.total.fits++; row.plateau = (row.plateau || 0) + 1; out.total.plateau = (out.total.plateau || 0) + 1;
            at += fz + 1;
            continue;
          }
          charge(row.why, reason);
          at += 1;
        }
      }
    }
    out.total.corridor += row.len; out.total.flat += row.flat;
    out.streets.push(row);
  }
  return out;
}

/** 1.3.230 (PL): the census's plateau test for one position — KIT.placeAlong's plateau rules (rise <= frontRise, the door
 *  within doorStep, the sewer link within one block), the greenbelt, then the world's veto with the plateau planner */
function censusPlateau(st, street, sx, side, def, sz, at, freeP) {
  if (!sx.Hs) return false;
  const fz = def.size[2];
  let lo = Infinity, hi = -Infinity;
  for (let q = at - sx.a; q < at - sx.a + fz; q++) { lo = Math.min(lo, sx.Hs[q]); hi = Math.max(hi, sx.Hs[q]); }
  if (hi - lo > PLAN.PLATEAU.frontRise) return false;
  const slot = KIT.slotFor(street.f, sx, side, def, sz, at, hi);
  if (hi - lo > KIT.FRONT_RISE) {
    const qd = slot.doorT - sx.a;
    if (!(qd >= 0 && qd < sx.Hs.length) || hi - sx.Hs[qd] > PLAN.PLATEAU.doorStep) return false;
    slot.plateau = { rise: hi - lo, step: hi - sx.Hs[qd] };
    if (slot.shaftT !== null) { const qs = slot.shaftT - sx.a; if (!(qs >= 0 && qs < sx.Hs.length) || hi - sx.Hs[qs] > 1) return false; }
  }
  const [x0, x1, z0, z1] = slot.box, big = [x0 - 1, x1 + 1, z0 - 1, z1 + 1];
  if (!street.bench) for (const w of st.walls || []) {
    const [wx0, wx1, wz0, wz1] = w.box;
    if (big[1] >= wx0 - GREENBELT && big[0] <= wx1 + GREENBELT && big[3] >= wz0 - GREENBELT && big[2] <= wz1 + GREENBELT
        && !(big[0] >= wx0 && big[1] <= wx1 && big[2] >= wz0 && big[3] <= wz1)) return false;
  }
  slot._street = street;
  return freeP(big, slot.box, slot, street.f);
}

// ------------------------------------------------------------------------------------------------ THE CORE GROWS (1.3.226, his 20:48)
// "keep businesses and business housing centralized, and keep moving homes out to the outskirts as they expand; converting
// old home structures into a parcel for a new business": from town II a business (prestige / craft district) whose best
// slot lies outside the CORE (or that found none) may take the lot of the nearest finished home inside the core. The
// household is re-homed (its people are homeless until a house has room; a replacement home joins the leftovers and is
// built on the outskirts, where homes now go first); the old house is taken down (above the street level to air, its
// cellar filled) and the business is planned on the freed frontage. One conversion a day.
const CORE_REACH = { town2: 60, town3: 70, city: 80, city2: 90, city3: 100, metropolis: 120, metropolis2: 140, metropolis3: 160, capital: 180 };   // (CORE_R is the ticking core's radius)
const HOME_KINDS = ["cottage_s", "cottage_m", "cottage_l", "townhouse"];
function slotDist(st, slot) { const [cx, cz] = squareCentre(st); const [x0, x1, z0, z1] = slot.box; return Math.hypot((x0 + x1) / 2 - cx, (z0 + z1) / 2 - cz); }
function convertForBusiness(s, st, family) {
  const R = CORE_REACH[st.tier];
  if (!R || st.convertDay === Math.floor(s.simDays)) return null;
  const [cx, cz] = squareCentre(st);
  const homes = plotsOf(s, st).filter((b) => b.kit && b.stage >= 4 && !b.closed && !b.palace && HOME_KINDS.includes(short(b)))
    .map((b) => { const def = BUILDINGS[b.family], [fx, , fz] = footprint(def, b.rot); return [b, Math.hypot(b.x + fx / 2 - cx, b.z + fz / 2 - cz)]; })
    .filter(([, d]) => d <= R).sort((p, q) => p[1] - q[1]);
  for (const [home] of homes.slice(0, 6)) {
    const street = st.streets.find((x) => x.kind === "kit" && x.id === home.kit.sid);
    if (!street) continue;
    const i = s.buildings.indexOf(home);
    s.buildings.splice(i, 1);                                              // its box must not veto its own replacement
    let got = null;
    try { got = kitSlot(s, st, family, { street, mid: home.kit.at + home.kit.len / 2 }); } catch (e) { console.warn(`[CIV-CLOCK] convert: ${e}`); }
    const [ox0, ox1, oz0, oz1] = (() => { const def = BUILDINGS[home.family], [fx, , fz] = footprint(def, home.rot); return [home.x, home.x + fx - 1, home.z, home.z + fz - 1]; })();
    const overlaps = got && got.slot.box[0] <= ox1 && got.slot.box[1] >= ox0 && got.slot.box[2] <= oz1 && got.slot.box[3] >= oz0;
    if (!overlaps) { s.buildings.splice(i, 0, home); continue; }
    // commit: the household moves out, the house comes down
    const P = census(st);
    let moved = 0;
    for (const q of PEOPLE.alive(P)) if (q.home === home.id) { q.home = null; moved++; }
    (st.leftover = st.leftover || []).push(short(home));
    street.branches = (street.branches || []).filter((r) => r.bid !== home.id);
    try { clearLot(world.getDimension(st.dim), home, BUILDINGS[home.family]); } catch (e) { console.warn(`[CIV-CLOCK] convert clear: ${e}`); }
    try { for (const v of world.getDimension(st.dim).getEntities({ tags: [`civ:home:${home.id}`] })) v.removeTag(`civ:home:${home.id}`); } catch { /* left */ }
    st.convertDay = Math.floor(s.simDays);
    st.conversions = (st.conversions || 0) + 1;
    st.log.push(`day ${s.simDays.toFixed(0)}: the town's core grows — #${home.id} ${short(home)} is bought for a new ${BUILDINGS[family].stem.replace(/^mvv_/, "").replace(/_[a-d]_r\d+$/, "")}; its household (${moved}) moves out to the edge of town`);
    return got;
  }
  return null;
}
/** take a converted house down: everything from the street level + 1 up to the box's top becomes air; the cellar below
 *  is filled with dirt (the new building's own box overwrites what it covers) */
function clearLot(dim, b, def) {
  const [fx, sy, fz] = footprint(def, b.rot);
  const floorY = b.y + def.datum_y;                                       // feet 0
  const x1 = b.x + fx - 1, z1 = b.z + fz - 1;
  dim.runCommand(`fill ${b.x} ${floorY} ${b.z} ${x1} ${b.y + sy - 1} ${z1} air`);
  dim.runCommand(`fill ${b.x} ${b.y + 9} ${b.z} ${x1} ${floorY - 2} ${z1} dirt`);
  dim.runCommand(`fill ${b.x} ${floorY - 1} ${b.z} ${x1} ${floorY - 1} ${z1} grass_block`);
}

// ------------------------------------------------------------------------------------------------ CONTOUR LANES (1.3.226, his 20:01 / 20:48)
// A home with no room on the streets (the homes go outward) takes a lot on a LANE: a 7-wide narrow road at ONE level that
// follows the hillside's contour from a street's dead end (pw_civ_lanes.js). The lane is laid by the road machinery (no
// kerbs: the houses' doors open onto it), it carries a sewer GALLERY under its centre line joined to the dead end's
// sewer hall, and every lane house is joined to the gallery by a branch (his 20:36: every home reaches the sewer).
const LANE_TRY_DAYS = 2;
function laneOf(st, rid) {
  const rec = (st.roads7 || []).find((r) => r.id === rid && r.ln);
  return rec ? { cells: rec.cells, dirs: rec.dirs.map((i) => DIRS4[i]), H: rec.ln.H, legs: rec.ln.legs, rec } : null;
}
function laneBlocked(s, st) {
  const boxes = plotBoxes(s, 1, null), body = kitBody(st);
  const roadCells = new Set();
  for (const r of st.roads7 || []) for (const [x, z] of r.cells) for (let a = -KIT.ROAD_HALF; a <= KIT.ROAD_HALF; a++) for (let c = -KIT.ROAD_HALF; c <= KIT.ROAD_HALF; c++) roadCells.add(`${x + a},${z + c}`);
  const wallCells = new Set();
  for (const w of st.walls || []) for (const [x, z] of ringLine(w.box)) for (let a = -3; a <= 3; a++) for (let c = -3; c <= 3; c++) wallCells.add(`${x + a},${z + c}`);
  return (x, z) => { const k = `${x},${z}`; return body.has(k) || roadCells.has(k) || wallCells.has(k) || inReserve(s, x, z) || boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1); };
}
/** plan + record + queue one lane from the first free dead end (one try a call; a failed end rests LANE_TRY_DAYS) */
function openLane(s, st) {
  if (!st.kit || st.laneDay === Math.floor(s.simDays)) return false;
  st.laneDay = Math.floor(s.simDays);
  const dim = world.getDimension(st.dim);
  const lsite = liveSite(dim, siteOf(st));
  const blocked = laneBlocked(s, st);
  st.laneFail = st.laneFail || {};
  for (const dep of departures(st)) {
    const key = `${dep.sid}:${dep.end}`;
    if (st.laneFail[key] !== undefined && s.simDays - st.laneFail[key] < LANE_TRY_DAYS) continue;
    let lane = null;
    try { lane = LN.planLane(lsite, dep.P, dep.d, dep.H, blocked); } catch (e) { console.warn(`[CIV-CLOCK] lane plan: ${e}`); }
    if (!lane) { st.laneFail[key] = s.simDays; continue; }
    const rid = (st.nextRoadId = (st.nextRoadId || 1)); st.nextRoadId++;
    const turns = lane.legs.slice(1).map((L) => L.a - 1);
    const rec = { id: rid, from: dep.sid, end: dep.end, to: 0, lane: true, noKerb: true, cells: lane.cells, H: lane.cells.map(() => lane.H), turns, ramps: [], rampLen: KIT.ROAD_RAMP,
                  dirs: lane.dirs.map((d) => d[0] === 1 ? 0 : d[1] === 1 ? 1 : d[0] === -1 ? 2 : 3), ln: { H: lane.H, legs: lane.legs, galleryDone: false } };
    (st.roads7 = st.roads7 || []).push(rec);
    const from = st.streets.find((x) => x.kind === "kit" && x.id === dep.sid);
    if (from) (from.roadsOut = from.roadsOut || []).push({ end: dep.end, to: `lane:${rid}` });
    kitTouch(st);
    st.kitQueue = st.kitQueue || [];
    for (let i = 0; i < rec.cells.length; i += 7) st.kitQueue.push({ op: "road", rid, a: i, len: Math.min(7, rec.cells.length - i), H: lane.H, sid: dep.sid });
    st.kitQueue.push({ op: "lanegallery", rid, sid: dep.sid, a: 0, len: 1, H: lane.H });
    st.lanes = (st.lanes || 0) + 1;
    st.log.push(`day ${s.simDays.toFixed(0)}: a contour lane leaves street ${dep.sid}'s ${dep.end} at y ${lane.H} (${lane.cells.length} cells, ${lane.legs.length} legs) — homes along the hillside`);
    return true;
  }
  return false;
}
/** a lot for `family` on a laid lane (both sides of every straight leg, packed from the lane's far end inward) */
function laneSlotFor(s, st, family) {
  const def = BUILDINGS[family];
  const sz = shaftZOf(def);
  const lsite = liveSite(world.getDimension(st.dim), siteOf(st));
  const free = kitFree(s, st, lsite, false);
  const fz = def.size[2];
  for (const rec of (st.roads7 || []).filter((r) => r.ln && r.laid && r.ln.galleryDone)) {   // the gallery first: its lining would close an earlier branch
    const ln = laneOf(st, rec.id);
    for (let li = ln.legs.length - 1; li >= 0; li--) {
      for (const side of [1, -1]) {
        for (let at = ln.legs[li].len - fz - 1; at >= 0; at--) {
          const slot = LN.laneSlot(ln, li, side, def, sz, at);
          if (!slot) continue;
          const [x0, x1, z0, z1] = slot.box;
          if (!free([x0 - 1, x1 + 1, z0 - 1, z1 + 1], slot.box, slot, slot.f)) continue;
          slot.branchT = slot.shaftT; slot.shaftT = null;
          return { slot, street: null, lane: rec.id };
        }
      }
    }
  }
  return null;
}
/** the lane's sewer gallery (air) and its lining (stone bricks where the ground is air or loose), plus the mouth into the
 *  dead end's hall (4 cells of the dead end's far wall on its centre line, w 5..7) */
const GALLERY_KEEP = ["minecraft:stone_bricks", "minecraft:cobblestone", "minecraft:stone", "minecraft:deepslate", "minecraft:smooth_stone"];
function layLaneGallery(dim, st, rec) {
  const ln = laneOf(st, rec.id);
  const g = LN.laneGalleryCells(ln);
  let air = 0, lined = 0;
  for (const [x, y, z] of g.lining) {
    try { const b = dim.getBlock({ x, y, z }); if (b && !GALLERY_KEEP.includes(b.typeId) && !b.typeId.startsWith("pw:")) { b.setType("minecraft:stone_bricks"); lined++; } } catch { /* asleep */ }
  }
  for (const [x, y, z] of g.air) {
    try { const b = dim.getBlock({ x, y, z }); if (b && b.typeId !== "minecraft:air") { b.setType("minecraft:air"); air++; } } catch { /* asleep */ }
  }
  // the mouth: from the lane's first cell back through the dead end's far wall into its hall
  const street = st.streets.find((x) => x.kind === "kit" && x.id === rec.from);
  if (street) {
    const seg = street.segs.find((q) => q.kind === "dead" && (rec.end === "start" ? q.a === 0 : q.a !== 0));
    if (seg) {
      const ts = rec.end === "start" ? [street.tmin, street.tmin + 1, street.tmin + 2, street.tmin + 3] : [9, 10, 11, 12].map((k) => street.tmin + seg.a + k);
      for (const tt of ts) for (let w = 5; w <= 7; w++) { const [x, z] = KIT.cellOf(street.f, tt, w); for (let y = rec.ln.H - 11; y <= rec.ln.H - 8; y++) { try { const b = dim.getBlock({ x, y, z }); if (b && b.typeId === "minecraft:stone_bricks") { b.setType("minecraft:air"); air++; } } catch { /* asleep */ } } }
    }
  }
  rec.ln.galleryDone = true;
  st.laneGallery = (st.laneGallery || 0) + air;
  return [air, lined];
}

/** a new plot on a kit settlement (the slot found now, the access piece laid with the plot's first stage) */
/** 1.3.227 (gate 226-2: a farm's lot search 720 ms + its stilts retry 552 ms in ONE tick): the search for a lot runs in
 *  PHASES, one costly search each — 0 the streets (+ a business's conversion in the core), 1 the lanes (homes), 2 a
 *  street grows, 3 a new lane (homes), 4 stilts, 5 a side-street job. kitTryPhase returns the building, "next" (try the
 *  next phase on a later tick) or null (no room). kitAddPlot runs every phase at once (the founding, the leftovers on the
 *  planning tick); the tier work runs one phase per beat. */
// 1.3.230 (PL): phase 1 = PLATEAUS on the existing streets (the frontage the hills left empty) — before a lane, a grown
// street or stilts (the sprawl on hills: "9 streets for 22 buildings"); the later phases moved up by one
const KIT_PHASES = 7;
const kindOfFamily = (family) => (BUILDINGS[family].stem || "").replace(/^mvv_/, "").replace(/_[a-d]_r\d+$/, "");
function kitTryPhase(s, st, family, delay, phase) {
  const isHome = HOME_KINDS.includes(kindOfFamily(family));
  let got = null;
  if (phase === 0) {
    got = timed(`slot ${family}`, () => kitSlot(s, st, family, null));
    const dist = DISTRICT[kindOfFamily(family)];
    if ((dist === "prestige" || dist === "craft") && CORE_REACH[st.tier] && (!got || slotDist(st, got.slot) > CORE_REACH[st.tier])) {   // 1.3.226 (his 20:48)
      const conv = timed(`convert for ${kindOfFamily(family)}`, () => convertForBusiness(s, st, family));
      if (conv) got = conv;
    }
  } else if (phase === 1) got = timed(`slot ${family} (plateau)`, () => kitSlot(s, st, family, null, false, true));
  else if (phase === 2) { if (isHome) got = timed("lane slot", () => laneSlotFor(s, st, family)); }
  else if (phase === 3) { if (timed("grow street", () => growKitStreet(s, st))) got = timed(`slot ${family}`, () => kitSlot(s, st, family)); }
  else if (phase === 4) { if (isHome) timed("open lane", () => openLane(s, st)); }
  else if (phase === 5) got = timed(`slot ${family} (stilts)`, () => kitSlot(s, st, family, null, true));
  else if (phase === 6) { startSideJob(st); return null; }
  if (got) return makeKitPlot(s, st, family, delay, got);
  return phase + 1 < KIT_PHASES ? "next" : null;
}
function kitAddPlot(s, st, family, delay, only = null) {
  if (only) { const got = timed(`slot ${family}`, () => kitSlot(s, st, family, only) || kitSlot(s, st, family, only, false, true)); return got ? makeKitPlot(s, st, family, delay, got) : null; }   // B2: one street only (1.3.230: then a plateau on it)
  if (st.noRoomTick === system.currentTick) return null;                         // this tick's planning budget is spent
  for (let ph = 0; ph < KIT_PHASES; ph++) {
    const r = kitTryPhase(s, st, family, delay, ph);
    if (r && r !== "next") return r;
    if (r === null) break;
  }
  st.noRoomTick = system.currentTick;
  return null;
}
function makeKitPlot(s, st, family, delay, got) {
  const { slot, street } = got;
  if (got.lane !== undefined) {                                            // 1.3.226: a lane house
    const bl = { id: s.nextId++, family, dim: st.dim, x: slot.x, y: slot.H - 14, z: slot.z, rot: slot.rot, settled: true, stage: -1, progress: 0, delay,
                 pending: [], street: null, streetAxis: "lane", yard: 0, settlement: st.id, planned: true,
                 kit: { sid: null, lane: got.lane, leg: slot.leg, shaftT: null, branchT: slot.branchT ?? null, side: slot.side, H: slot.H, at: slot.at, len: slot.len }, land: slot.land || null };
    if (delay === 0) { bl.stage = 0; bl.pending.push(0); }
    s.buildings.push(bl);
    return bl;
  }
  if (slot.shaftT !== null && !(street.access || []).includes(slot.shaftT)) (street.access = street.access || []).push(slot.shaftT);
  const bld = { id: s.nextId++, family, dim: st.dim, x: slot.x, y: slot.H - 14, z: slot.z, rot: slot.rot, settled: true, stage: -1, progress: 0, delay,
                pending: [], street: [street.id, slot.at, slot.side], streetAxis: "kit", yard: 0, settlement: st.id, planned: true,
                kit: { sid: street.id, shaftT: slot.shaftT, side: slot.side, H: slot.H, at: slot.at, len: slot.len, branchT: slot.branchT ?? null,
                       doorT: slot.doorT, doorRamp: slot.doorRamp || null }, land: slot.land || null };   // 1.3.232 (#6 b): the landing's facts
  if (delay === 0) { bld.stage = 0; bld.pending.push(0); }
  s.buildings.push(bld);
  if (bld.land && bld.land.kind === "plateau") {                           // 1.3.230 (PL)
    st.plateaus = (st.plateaus || 0) + 1;
    st.log.push(`day ${s.simDays.toFixed(0)}: #${bld.id} ${short(bld)} gets a PLATEAU at y ${bld.land.P} (frontage rise ${bld.land.rise}, cut ${bld.land.cut}, fill ${bld.land.fill}; ${bld.land.stone} stone, ${bld.land.labourDays} labourer days; drains to ${bld.land.drain === "sewer" ? "the sewer" : "a soakaway"})`);
  }
  return bld;
}

const GROUND_TOP = "minecraft:grass_block";
const isVeg = (id) => NOT_GROUND.some((s) => id.includes(s)) && !id.includes("water");
/** one column levelled to `top`: ground above it cut away (plants and trees too), hollows below filled (dirt, the top
 *  block grass), 3 of clearance above. Returns the ground before. */
function levelColumn(dim, x, z, top, clear = 3) {
  const g = groundAt(dim, x, z);
  if (g === undefined) return undefined;
  for (let y = top + 1; y <= Math.max(g, top) + clear; y++) {
    try { const b = dim.getBlock({ x, y, z }); if (b && b.typeId !== "minecraft:air" && !b.typeId.includes("water")) b.setType("minecraft:air"); } catch { /* unloaded */ }
  }
  const lg = localGround(dim, x, g, z);                                   // B6 (GB9): read before the column changes
  clearTreesOver(dim, x, z, Math.max(g, top) + clear);
  for (let y = g + 1; y < top; y++) { try { const b = dim.getBlock({ x, y, z }); if (b && (b.typeId === "minecraft:air" || isVeg(b.typeId))) b.setType(lg.fill); } catch { /* unloaded */ } }
  try { const b = dim.getBlock({ x, y: top, z }); if (b && (b.typeId === "minecraft:air" || isGround(b.typeId) || isVeg(b.typeId)) && !b.typeId.includes("water")) b.setType(lg.top); } catch { /* unloaded */ }
  return g;
}
/** a retaining wall in one column: cobblestone from y0 to y1 where the column is ground (never above the ground) */
function wallColumn(dim, x, z, y0, y1) {
  const g = groundAt(dim, x, z);
  if (g === undefined) return;
  for (let y = y0; y <= Math.min(y1, g); y++) { try { const b = dim.getBlock({ x, y, z }); if (b && isGround(b.typeId) && !b.typeId.includes("water")) b.setType(FILL_OUT); } catch { /* unloaded */ } }
}
/** a STEPPED FACE (R1 §4.5 / his C3 "terrace"): from an edge line outward along dir, walls of at most WALL_MAX and benches
 *  of BENCH cells, climbing 3 per step, up to maxSteps; cells inside plot boxes are left alone. edge = [[x, z], ...] at
 *  distance 0 (the first wall's line), H = the level the face rises from. */
function terraceFace(dim, edge, H, dir, maxSteps = 3, inPlot = () => false) {
  let touched = 0;
  for (const [ex, ez] of edge) {
    for (let k = 0; k < maxSteps; k++) {
      const wx = ex + dir[0] * 4 * k, wz = ez + dir[1] * 4 * k;
      if (inPlot(wx, wz)) break;
      const g = groundAt(dim, wx, wz);
      if (g === undefined || g <= H + 3 * k + 1) break;                        // no hill left to hold back
      wallColumn(dim, wx, wz, H + 1 + 3 * k, H + 3 + 3 * k); touched++;
      if (g <= H + 3 * (k + 1)) break;                                         // the wall reaches the ground: done
      for (let d = 1; d <= BENCH; d++) { const bx = wx + dir[0] * d, bz = wz + dir[1] * d; if (inPlot(bx, bz)) break; levelColumn(dim, bx, bz, H + 3 * (k + 1), 2); touched++; }
    }
  }
  return touched;
}
/** D-C534 §2: the land under and behind a kit plot once its plot stage is down — the REAR BENCH (BENCH wide, levelled at
 *  H, grass, its outer edge a retaining wall below or a stepped face above), STILTS for a plot over a drop (the box's
 *  exposed subsurface outside the cellar shell cut to air, posts left at the corners and every 4th cell, the shaft kept
 *  in a stone pier). The street side is never touched. */
function kitLandPrep(dim, b, def, st) {
  const k = b.kit;
  if (!k || !st) return;
  let f;
  if (k.lane !== undefined && k.lane !== null) {                             // 1.3.226: a lane house — the leg's frame
    const ln = laneOf(st, k.lane);
    if (!ln) return;
    f = LN.legFrame(ln, k.leg);
  } else {
    const street = st.streets.find((x) => x.kind === "kit" && x.id === k.sid);
    if (!street) return;
    f = street.f;
  }
  const [sx, , sz] = def.size;
  const [fx, , fz] = footprint(def, b.rot);
  const boxes = plotBoxes(load(), 0, null).filter(([x0, x1, z0, z1]) => !(x0 === b.x && z0 === b.z));
  const inPlot = (x, z) => boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  const away = k.side > 0 ? [f.vx, f.vz] : [-f.vx, -f.vz];
  const H = k.H;
  // the box in frame terms
  const [ta, wa] = KIT.tw(f, b.x, b.z), [tb, wb] = KIT.tw(f, b.x + fx - 1, b.z + fz - 1);
  const t0 = Math.min(ta, tb), t1 = Math.max(ta, tb);
  const wRear = k.side > 0 ? Math.max(wa, wb) : Math.min(wa, wb);
  // 1. the rear bench (not for a stilt house: it hangs over the drop)
  let benchCells = 0;
  const stilts = b.land && b.land.kind === "stilts";
  const plateau = b.land && b.land.kind === "plateau";                       // 1.3.230 (PL): its ring and faces are the job's
  for (let t = t0 - 1; t <= t1 + 1 && !stilts && !plateau; t++) {
    for (let d = 1; d <= BENCH; d++) {
      const [x, z] = KIT.cellOf(f, t, wRear + k.side * d);
      if (inPlot(x, z)) continue;
      const g = levelColumn(dim, x, z, H, 3);
      if (g !== undefined) benchCells++;
    }
    // the bench's outer cell: where the ground beyond lies below the bench, the fill's face is cobblestone (grass on top)
    const [ox, oz] = KIT.cellOf(f, t, wRear + k.side * (BENCH + 1));
    const [lx, lz] = KIT.cellOf(f, t, wRear + k.side * BENCH);
    if (!inPlot(ox, oz) && !inPlot(lx, lz)) { const g = groundAt(dim, ox, oz); if (g !== undefined && g < H) { wallColumn(dim, lx, lz, Math.max(g + 1, H - LIFT), H - 1); if (g < H - LIFT) stepBerm(dim, lx, lz, away, H, inPlot, null); } }   // 1.3.224: one lift, then stepped
  }
  const edge = [];
  for (let t = t0 - 1; t <= t1 + 1 && !stilts && !plateau; t++) edge.push(KIT.cellOf(f, t, wRear + k.side * (BENCH + 1)));
  if (edge.length) terraceFace(dim, edge, H, away, 3, inPlot);
  // 0.0.17: DRY the plot — a cut can open a pond's edge or an aquifer (cottage #14 stood in a pool at floor level): water
  // found within 2 cells of the box between H - 1 and H + 2 is replaced by dirt (air above it), and logged
  let dried = 0;
  for (let x = b.x - 2; x <= b.x + fx + 1; x++) for (let z = b.z - 2; z <= b.z + fz + 1; z++) {
    if (inPlot(x, z)) continue;
    if (x >= b.x && x < b.x + fx && z >= b.z && z < b.z + fz) continue;      // never the plot's own box (a farm's irrigation is water)
    for (let y = H - 1; y <= H + 2; y++) {
      try { const blk = dim.getBlock({ x, y, z }); if (blk && (blk.typeId === "minecraft:water" || blk.typeId === "minecraft:flowing_water")) { blk.setType(y <= H ? "minecraft:dirt" : "minecraft:air"); dried++; } } catch { /* unloaded */ }
    }
  }
  if (dried) { st.log.push(`day ${load().simDays.toFixed(0)}: ${dried} cells of water drained beside #${b.id} ${short(b)}`); b.dried = dried; }
  // the side margins (1 cell, the neighbours' gap): capped cladding — a stepped face beyond them is not cut (a neighbour may stand there)
  // 2. stilts
  if (b.land && b.land.kind === "stilts") {
    let cut = 0, posts = 0;
    const shaftLocal = shaftZOf(def);
    const lsite = liveSite(dim, siteOf(st));                                   // the ground BEFORE the box was placed
    for (let i = 0; i < sx; i++) for (let j = 0; j < sz; j++) {
      const [ox, oz] = rotXZ(i, j, sx, sz, b.rot);
      const x = b.x + ox, z = b.z + oz;
      const g = lsite.at(x, z);
      if (g === undefined || g >= b.y + 8) continue;
      const post = ((i === 0 || i === sx - 1) && (j === 1 || j === sz - 1 || (j - 1) % 4 === 0)) || ((j === 1 || j === sz - 1) && (i % 4 === 0));
      const pier = shaftLocal !== null && i <= 2 && Math.abs(j - shaftLocal) <= 1;
      // the box's subsurface: feet -15..-7 = box y 0..8 (dirt / smooth stone); the cellar shell y 9..14 stays
      for (let y = b.y; y <= b.y + 8; y++) {
        if (y <= g) continue;                                                // underground: leave it
        try {
          const blk = dim.getBlock({ x, y, z });
          if (!blk) continue;
          if (post) { if (blk.typeId !== "minecraft:spruce_log") { blk.setType("minecraft:spruce_log"); posts++; } }
          else if (pier) { if (blk.typeId === "minecraft:dirt" || blk.typeId === "minecraft:smooth_stone") blk.setType("minecraft:stone_bricks"); }
          else if (blk.typeId !== "minecraft:air" && blk.typeId !== "minecraft:ladder") { blk.setType("minecraft:air"); cut++; }
        } catch { /* unloaded */ }
      }
      // the posts stand on the ground
      if (post) for (let y = g + 1; y < b.y; y++) { try { dim.getBlock({ x, y, z })?.setType("minecraft:spruce_log"); } catch { /* left */ } }
    }
    b.stilts = { cut, posts };
  }
  // 3. 1.3.230 (PL): a PLATEAU — its ring, retaining walls, clad faces and drain, in a budgeted job on the live ground; a
  // plateau the live ground no longer allows (or that never loads) falls back to the old ring terrace
  if (plateau && k.sid !== undefined && k.sid !== null) {
    const bid = b.id;
    const live = () => load().buildings.find((x) => x.id === bid);
    startPlateauJob(dim, { key: `b:${bid}`, f, side: k.side, at: k.at, fz: k.len, depth: sx, P: H, sid: k.sid, stId: st.id,
      self: [b.x, b.x + fx - 1, b.z, b.z + fz - 1], label: `#${bid} ${short(b)}`, rec: live,
      fallback: () => { const lb = live(); if (lb) { try { lb.filled = terrace(dim, lb, def); } catch (e) { console.warn(`[CIV-CLOCK] plateau fallback #${bid}: ${e}`); } } } });
  }
  b.bench = benchCells;
}

/** 1.3.230 (PL): BUILD A PLATEAU — a generator for system.runJob. (1) the live ground of every cell the plan may ask for
 *  (the ring, the rays of its faces and berms), read through the guarded API (topAt / groundAt / blockAt: no throw, no
 *  leak); a chunk asleep -> wait (PLATEAU_WAIT tries of ~5 s, then the fallback); a trunk standing on the ground OUTSIDE
 *  the pad marks a PROTECTED tree (the face never cuts into it: the plan refuses). (2) PLAN.planPlateau again on that live
 *  ground (skipBox: the house stands). (3) the ops, PLATEAU_OPS block writes per tick: the pad (trees over it felled —
 *  clearing stops at a plot's box + its margin), stone retaining walls, berms, cut + clad faces (no worked block — a
 *  neighbour's wall, a path — is ever cut), the gravel gutter on its cobblestone bed, the grated drop and its link into
 *  the street's sewer hall (BRANCH_CUT only), or the soakaway. ctx = { key, f, side, at, fz, depth, P, sid, stId, self,
 *  boxFillMax, label, rec() (the record, found again after a reload), fallback() }. */
const PLATEAU_WAIT = 20, PLATEAU_OPS = 120, PLATEAU_READS = 48;
const PL_STONE = "minecraft:stone_bricks", PL_GRAVEL = "minecraft:gravel", PL_BED = "minecraft:cobblestone", PL_GRATE = "minecraft:iron_bars";
const PL_WORKED = new Set([PL_STONE, PL_BED, PL_GRATE, "minecraft:mossy_cobblestone", "minecraft:grass_path", "minecraft:dirt_path", "minecraft:smooth_stone",
  "minecraft:stone_brick_slab", "minecraft:cobblestone_wall", "minecraft:sandstone", "minecraft:red_sandstone"]);
const plateauJobs = new Set();
function startPlateauJob(dim, ctx) {
  if (plateauJobs.has(ctx.key)) return false;
  plateauJobs.add(ctx.key);
  function* wrapped() { try { yield* plateauJob(dim, ctx); } catch (e) { console.warn(`[CIV-CLOCK] plateau ${ctx.label}: ${e}`); } finally { plateauJobs.delete(ctx.key); } }
  try { system.runJob(wrapped()); return true; } catch (e) { plateauJobs.delete(ctx.key); console.warn(`[CIV-CLOCK] plateau job: ${e}`); return false; }
}
function* plateauJob(dim, ctx) {
  const { fz, depth, P } = ctx;
  const xz = plateauFrame(ctx.f, ctx.side, ctx.at);
  const R = PLAN.PLATEAU.faceLifts + 2;                                      // the farthest row a face ray or a berm reads
  const cells = new Map();
  let reads = 0;
  for (let tries = 0; ; tries++) {
    let missing = 0;
    for (let q = -1 - R; q <= fz + R; q++) for (let d = 0; d <= depth + R; d++) {
      if (q >= 0 && q < fz && d < depth) continue;                          // the house's box: the house stands there
      if (d > depth && (q < -1 || q > fz)) continue;                         // on no ray
      const key = q * 4099 + d;
      if (cells.has(key)) continue;
      const [x, z] = xz(q, d);
      const top = topAt(dim, x, z);
      const h = top ? groundAt(dim, x, z, top) : undefined;
      if (h === undefined) { missing++; continue; }
      const pad = q >= -1 && q <= fz && d <= depth;
      const above = pad ? null : blockAt(dim, x, h + 1, z, true);
      cells.set(key, { h, wet: isWater(top.typeId), tree: !!above && TREE_LOG(above.typeId) });
      if (++reads % PLATEAU_READS === 0) yield;
    }
    if (!missing) break;
    if (tries >= PLATEAU_WAIT) { console.warn(`[CIV-CLOCK] plateau ${ctx.label}: ${missing} cells never loaded — the old ring terrace instead`); if (ctx.fallback) ctx.fallback(); return; }
    for (let w = 0; w < 100; w++) yield;                                     // the chunks may wake
  }
  const s = load();
  const fc = freeSets(s);
  const st = s.settlements.find((x) => x.id === ctx.stId);
  const street = st && ctx.sid !== undefined && ctx.sid !== null ? st.streets.find((x) => x.kind === "kit" && x.id === ctx.sid) : null;
  const ring = street ? streetRing(street) : null;
  const res = PLAN.planPlateau({ fz, depth, P, skipBox: true, boxFillMax: ctx.boxFillMax,
    Hring: (q) => (ring ? ring.H(ctx.at + q) : undefined), hallAt: (q) => (ring ? ring.hall(ctx.at + q) : undefined),
    ground: (q, d) => { const c = cells.get(q * 4099 + d); return c ? { h: c.h, wet: c.wet } : undefined; },
    blocked: (q, d) => { const c = cells.get(q * 4099 + d); if (c && c.tree) return "tree"; const [x, z] = xz(q, d); return plateauBlocked(s, fc, x, z, ctx.self); } });
  if (!res.ok) {
    console.warn(`[CIV-CLOCK] plateau ${ctx.label}: the live ground refuses it (${res.why} at ${JSON.stringify(res.at)}) — the old ring terrace instead`);
    const r0 = ctx.rec(); if (r0) r0.plateauDone = { ok: false, why: res.why };
    if (ctx.fallback) ctx.fallback();
    return;
  }
  let n = 0, walls = 0, clad = 0, cut = 0, filled = 0, gutter = 0, link = 0;
  const put = (x, y, z, id, when) => {
    const b = blockAt(dim, x, y, z);
    if (!b || b.typeId === id || (when && !when(b.typeId))) return false;
    try { b.setType(id); return true; } catch { ENGINE.throws++; return false; }
  };
  const open = (id) => id === "minecraft:air" || (isVeg(id) && !TREE_LOG(id));                 // fill only air and plants: water is moved, never buried
  const natural = (id) => id !== "minecraft:air" && !isWater(id) && !TREE_LOG(id) && !PL_WORKED.has(id) && (isGround(id) || isVeg(id));
  for (const o of res.ops) {
    if (++n % PLATEAU_OPS === 0) yield;
    if (o.kind === "link") {                                                  // through the corridor's side wall, like a house branch
      const [x, z] = KIT.cellOf(ctx.f, ctx.at + o.q, ctx.side > 0 ? KIT.W - 1 - o.k : o.k);
      if (put(x, o.y, z, "minecraft:air", (id) => BRANCH_CUT.includes(id))) link++;
      continue;
    }
    const [x, z] = KIT.cellOf(ctx.f, ctx.at + o.q, ctx.side > 0 ? KIT.W + o.d : -1 - o.d);
    if (o.kind === "pad") {
      const lg = localGround(dim, x, o.g, z);                                 // B6 (GB9): read before the column changes
      clearTreesOver(dim, x, z, P);
      for (let y = P + 1; y <= Math.max(o.g, P) + 3; y++) if (put(x, y, z, "minecraft:air", natural)) cut++;
      for (let y = o.g + 1; y < P; y++) { const w = o.wall !== null && y >= o.wall; if (put(x, y, z, w ? PL_STONE : lg.fill, open)) { filled++; if (w) walls++; } }
      if (o.wall !== null) for (let y = o.wall; y <= Math.min(o.g, P - 1); y++) if (put(x, y, z, PL_STONE, natural)) clad++;   // the old ground in the face: clad
      if (put(x, P, z, lg.top, (id) => open(id) || natural(id))) filled++;
    } else if (o.kind === "berm") {
      const lg = localGround(dim, x, o.g, z);
      for (let y = o.g + 1; y < o.y; y++) if (put(x, y, z, PL_STONE, open)) { filled++; walls++; }
      if (put(x, o.y, z, lg.top, open)) filled++;
    } else if (o.kind === "face") {
      for (let y = o.y + 1; y <= o.g + 2; y++) if (put(x, y, z, "minecraft:air", natural)) cut++;
      if (o.clad) for (let y = o.clad[0]; y <= o.clad[1]; y++) if (put(x, y, z, PL_STONE, natural)) clad++;
    } else if (o.kind === "gutter") {
      if (put(x, P - 1, z, PL_BED, (id) => !isWater(id))) gutter++;
      if (put(x, P, z, PL_GRAVEL, (id) => !isWater(id))) gutter++;
    } else if (o.kind === "outlet") {
      const carve = (id) => natural(id) || id === PL_STONE || id === PL_BED || id === PL_GRAVEL || id === "minecraft:dirt";
      put(x, P, z, PL_GRATE, (id) => !isWater(id));
      const half = Math.ceil((P - o.yBot) / 2);
      for (let y = o.yBot; y < P; y++) put(x, y, z, o.to === "soak" && y < o.yBot + half ? PL_GRAVEL : "minecraft:air", carve);
    }
  }
  const s2 = load();
  const r = ctx.rec();
  if (r) r.plateauDone = { ok: true, walls, clad, cut, filled, gutter, link, drain: res.drain.to };
  const st2 = s2.settlements.find((x) => x.id === ctx.stId);
  if (st2) st2.log.push(`day ${s2.simDays.toFixed(0)}: the plateau of ${ctx.label} is cut at y ${P}: ${walls + clad} wall stones, ${cut} blocks cut, ${filled} filled, ${gutter} gutter, drained to ${res.drain.to === "sewer" ? `the sewer (${link} link cells)` : "a soakaway"}`);
}

/** 1.3.225: cut a house's sewer branch (KIT.branchCells): the corridor's side wall (stone bricks, dirt, cobble) becomes air;
 *  water, our pieces' furnishings and anything that is not masonry or earth are left alone. Returns the cells cut. */
const BRANCH_CUT = ["minecraft:stone_bricks", "minecraft:dirt", "minecraft:cobblestone", "minecraft:stone", "minecraft:smooth_stone", "minecraft:stone_brick_slab", "minecraft:gravel", "minecraft:grass_block"];
function carveBranch(dim, street, br) {
  let cut = 0;
  for (const [x, y, z] of KIT.branchCells(street.f, br.t, br.side, br.Hh)) {
    try { const blk = dim.getBlock({ x, y, z }); if (blk && BRANCH_CUT.includes(blk.typeId)) { blk.setType("minecraft:air"); cut++; } } catch { /* unloaded: the op is retried */ }
  }
  return cut;
}
/** 1.3.225 (his 20:36): does every finished house reach the sewer hall underground? For each: the cell in front of its
 *  cellar gallery (corridor w 0 / 12 at the shaft's t, house floor - 10) and the hall beside it (w 4 / 8, street H - 10)
 *  must both be air. Returns { houses, linked, hatch, branch, none: [...ids], blocked: [...ids] } (loaded land only). */
function sewerReach(s, st) {
  const dim = world.getDimension(st.dim);
  const out = { houses: 0, linked: 0, hatch: 0, branch: 0, none: [], blocked: [], asleep: 0 };
  for (const b of plotsOf(s, st)) {
    if (!b.kit || b.stage < 4 || !BUILDINGS[b.family] || shaftZOf(BUILDINGS[b.family]) === null) continue;
    if (b.kit.lane !== undefined && b.kit.lane !== null) {                  // 1.3.226: a lane house — its branch (w +-3) and the gallery (w +-1)
      const ln = laneOf(st, b.kit.lane);
      out.houses++;
      if (!ln || b.kit.branchT === null || b.kit.branchT === undefined) { out.none.push(b.id); continue; }
      const f = LN.legFrame(ln, b.kit.leg);
      const [ex, ez] = KIT.cellOf(f, b.kit.branchT, 3 * b.kit.side), [gx, gz] = KIT.cellOf(f, b.kit.branchT, b.kit.side);
      try {
        const e = dim.getBlock({ x: ex, y: b.kit.H - 10, z: ez }), g = dim.getBlock({ x: gx, y: ln.H - 10, z: gz });
        if (!e || !g) { out.asleep++; continue; }
        if (e.typeId === "minecraft:air" && g.typeId === "minecraft:air") { out.linked++; out.lane = (out.lane || 0) + 1; } else out.blocked.push([b.id, "lane", e.typeId.replace("minecraft:", ""), g.typeId.replace("minecraft:", "")]);
      } catch { out.asleep++; }
      continue;
    }
    const street = st.streets.find((x) => x.kind === "kit" && x.id === b.kit.sid);
    if (!street) continue;
    out.houses++;
    const t = b.kit.shaftT ?? b.kit.branchT;
    if (t === null || t === undefined) { out.none.push(b.id); continue; }
    const kind = b.kit.shaftT !== null && b.kit.shaftT !== undefined ? "hatch" : "branch";
    const [ex, ez] = KIT.cellOf(street.f, t, b.kit.side > 0 ? 12 : 0), [hx, hz] = KIT.cellOf(street.f, t, b.kit.side > 0 ? 8 : 4);
    const Ht = kitHAt(street, t);
    try {
      const e = dim.getBlock({ x: ex, y: b.kit.H - 10, z: ez }), h = dim.getBlock({ x: hx, y: Ht - 10, z: hz });
      if (!e || !h) { out.asleep++; continue; }
      if (e.typeId === "minecraft:air" && h.typeId === "minecraft:air") { out.linked++; out[kind]++; } else out.blocked.push([b.id, kind, e.typeId.replace("minecraft:", ""), h.typeId.replace("minecraft:", "")]);
    } catch { out.asleep++; }
  }
  return out;
}

/** the access piece in front of a kit plot's sewer shaft (laid with the plot's first stage; shared by facing houses) */
function kitPlotAccess(st, b) {
  if (b.kit && b.kit.lane !== undefined && b.kit.lane !== null) {           // 1.3.226: a lane house's branch into the lane gallery
    if (b.kit.branchT !== null && b.kit.branchT !== undefined) (st.kitQueue = st.kitQueue || []).push({ op: "lanebranch", rid: b.kit.lane, bid: b.id, a: 0, len: 1, H: b.kit.H });
    return;
  }
  if (b.kit && b.kit.doorRamp && b.kit.doorT !== undefined && b.kit.sid !== null) {   // 1.3.232 (#6 b): the flat landing at the floor
    (st.kitQueue = st.kitQueue || []).push({ op: "landing", sid: b.kit.sid, a: b.kit.doorT - 1, len: 3, H: b.kit.H, side: b.kit.side, doorT: b.kit.doorT });
  }
  if (b.kit && b.kit.branchT !== null && b.kit.branchT !== undefined) {         // 1.3.225: the sewer BRANCH (his 20:36: every home reaches the sewer)
    const street = st.streets.find((x) => x.kind === "kit" && x.id === b.kit.sid);
    if (!street) return;
    street.branches = street.branches || [];
    if (!street.branches.some((r) => r.t === b.kit.branchT && r.side === b.kit.side)) street.branches.push({ t: b.kit.branchT, side: b.kit.side, Hh: b.kit.H, bid: b.id, laid: false });
    (st.kitQueue = st.kitQueue || []).push({ op: "branch", sid: street.id, a: b.kit.branchT, len: 1, H: b.kit.H, side: b.kit.side });
    return;
  }
  if (!b.kit || b.kit.shaftT === null || b.kit.shaftT === undefined) return;
  const street = st.streets.find((x) => x.kind === "kit" && x.id === b.kit.sid);
  if (!street) return;
  street.accessLaid = street.accessLaid || [];
  if (street.accessLaid.includes(b.kit.shaftT)) return;
  street.accessLaid.push(b.kit.shaftT);
  const H = kitHAt(street, b.kit.shaftT);
  const p = KIT.accessPiece(street.f, b.kit.shaftT, H, "v");
  (st.kitQueue = st.kitQueue || []).push({ op: "piece", kind: "access3", x: p.x, y: p.y, z: p.z, rot: p.rot, sid: street.id, a: p.a, len: 3, H });
}

/** found a settlement on kit streets: the square, the main street beside it, the first plots */
function foundKitSettlement(s, st, site, cx, cz, seedN, reply) {
  const dim = world.getDimension(st.dim);
  const sq = LAND.findSquare(site, cx, cz);
  if (!sq) return false;
  const lsite = liveSite(dim, site);
  const why = [];
  let main = planKitMain(lsite, sq, why);
  if (!main) { KIT.RULES.strictDrop = false; try { main = planKitMain(lsite, sq, why); } finally { KIT.RULES.strictDrop = true; } if (main) st.log.push("the main street had to cross a drop of more than 15 (no gentler side of the square)"); }   // 1.3.224
  if (!main) {
    st.log.push(`day ${s.simDays.toFixed(0)}: no StreetKit street fits beside the square here (${why.slice(-4).join("; ")}) — the old contour street is laid`);
    console.warn(`[CIV-CLOCK] kit founding impossible at ${sq.x} ${sq.z}: ${why.join(" | ")}`);
    return false;
  }
  st.kit = true;
  st.width = "v";
  st.square = sq;
  st.h0 = sq.y;
  st.axis = "kit";
  st.profile = {};
  st.kitQueue = [];
  const street = { kind: "kit", id: 1, role: "main", f: main.f, tmin: 0, H: main.H, segs: main.segs, access: [], tees: [],
                   reserved: main.reserved, mid: main.half + 6, tOff: 0, sqT: [main.half, main.half + 11] };
  st.streets.push(street);
  st.nextStreetId = 2;
  // D-C534 §3: grid lines every GRID_PITCH of mainT from the square's window START (a window = [line, line + 12]; the
  // founding window opposite the square lies on line 0; 0.0.12 fix: it was the window's middle, so the family's windows
  // sat 6 cells off the founding ones and never coincided with the DP's flat reservations)
  st.gridMid = main.half;
  kitTouch(st);
  // D-C542: the settlement's core keeps ticking so its work goes on while nobody is there
  try { ensureTicking(s, st, [sq.x + 6 - CORE_R, sq.z + 6 - CORE_R, sq.x + 6 + CORE_R, sq.z + 6 + CORE_R], `core of ${st.name}`); } catch (e) { console.warn(`[CIV-CLOCK] core: ${e}`); }
  queueKitStreet(st, street);
  paveSquare(dim, st, site);
  // D-C533: the well's drain to the street's sewer (carved once the pieces at its t and the well's shaft are down)
  { const plan = wellDrainPlan(s, st); if (plan) { st.wellDrain = { sid: street.id, t: plan.t, H: plan.H, done: false }; st.kitQueue.push({ op: "welldrain", sid: street.id, a: plan.t, len: 1, H: plan.H }); } }
  st.phase = "built";
  const pick = rng(seedN);
  let k = 0, missed = 0;
  st.leftover = [];
  for (const nm of VILLAGE_NORTH.concat(VILLAGE_SOUTH)) {
    const skins = skinsOf(nm);
    const family = familyOf(nm, skins[Math.floor(pick() * skins.length)]);
    // review 19:1x: a founding plot without room grows the street or opens a side street at once (kitAddPlot), instead of
    // waiting for the next tier (the hill site of kitvillage-0.0.4 seated 2 of 12)
    const b = kitAddPlot(s, st, family, k * VILLAGE_STAGGER);
    if (!b) { missed++; st.leftover.push(nm); continue; }
    k++;
  }
  try { foundBorder(s, st); } catch (e) { console.warn(`[CIV-CLOCK] border: ${e}`); }                   // B4: the boundary stones (after the founding streets)
  const ramps = main.segs.filter((q) => q.kind === "ramp").length, bridges = main.segs.filter((q) => q.kind === "bridge").length;
  st.log.push(`day ${s.simDays.toFixed(0)}: founded on the knoll at ${sq.x + 6} ${sq.z + 6} (relief ${sq.relief}); main street ${street.H.length} cells ` +
    `(${ramps} ramp(s), ${bridges} bridge(s)), square at y ${sq.y}; ${k} plots${missed ? `, ${missed} wait for more street` : ""}`);
  st.missed = missed;
  flushPending(); save();
  reply(`§e[CLOCK] ${st.name} founded: square at ${sq.x + 6} ${sq.z + 6} y ${sq.y}, main street ${street.H.length} cells (${ramps} ramps, ${bridges} bridges), ` +
    `${k} plots staggered${missed ? `, ${missed} without room yet` : ""}; ${st.kitQueue.length} street pieces queued`);
  return true;
}

/** grow a kit street at one of its ends (his 18:15: as the territory grows they continue their roads): the dead end is
 *  replaced by street, KIT_GROW more cells are planned from its level, a new dead end + outfall at the new end. */
function growKitStreet(s, st) {
  const dim = world.getDimension(st.dim);
  const lsite = liveSite(dim, siteOf(st));
  const today = s.simDays;
  for (const street of st.streets.filter((x) => x.kind === "kit" && x.role !== "connector")) {
    if (street.H.length + KIT_GROW > KIT_MAX_LEN) continue;
    if (street.growFail !== undefined && today - street.growFail < 10) continue;     // planning budget: a failed end rests 10 days
    for (const end of ["end", "start"]) {
      if ((street.roadsOut || []).some((r) => r.end === end && !r.gate)) continue;   // 0.0.25: a bench road leaves this end: it stays
      const n = street.H.length;
      // the new stretch in frame t: from the old dead end's first cell, KIT_GROW + 13 further
      const ta = end === "end" ? street.tmin + n - 13 : street.tmin - KIT_GROW;
      const tb = end === "end" ? street.tmin + n + KIT_GROW : street.tmin + 13;          // exclusive
      const ground = KIT.groundAlong(lsite, street.f, ta, tb);
      const fixH = end === "end" ? kitHAt(street, street.tmin + n - 13) : kitHAt(street, street.tmin + 12);
      const base = end === "end" ? { ...STREET_OPTS, startDead: false, endDead: true, startH: fixH } : { ...STREET_OPTS, startDead: true, endDead: false, endH: fixH };
      // D-C534 §3: the family's junction windows inside the new stretch stay flat for the cross streets to come (indices
      // into ground[] are frame t - ta); when the land cannot hold them flat the stretch is planned without
      // (0.0.17: margin 0 — the stretch re-plans the old dead end too, so a window may begin right at ta; the main's window at
      // 106 sat across the founding street's end and was never held flat, which starved the grid of its second cross line)
      const gridFlat = gridWindowsIn(st.gridMid, tOffOf(street), ta, tb - 1, 0).map(([a, b]) => [a - ta, b - ta]);
      let plan = gridFlat.length ? KIT.planProfile(ground, { ...base, flat: gridFlat }) : null;
      if (!plan || plan.cost === Infinity || plan.cost / ground.length > 6) plan = KIT.planProfile(ground, base);
      if (plan.cost === Infinity || plan.cost / ground.length > 6) continue;
      // the new corridor must not run into plots / other corridors
      const cells = KIT.corridorCells(street.f, plan, ta, new Map());
      if (!cellsInInfluence(st, cells)) {                                         // B4: beyond the boundary stones
        st.borderWait = (st.borderWait || 0) + 1;
        // the town NEEDS land: the council sends the surveyor out one stone-step (the stones are carried before the street grows)
        if (st.border && st.borderWait % BORDER_ASK === 0 && !st.border.moves.some((m) => !m.done && m.blocked === null)) {
          planBorderGrowth(s, st, st.border.r + STONE_EVERY, !!s.accelNow);
          st.log.push(`day ${s.simDays.toFixed(0)}: the streets press on the boundary stones: the council sends the surveyor out ${STONE_EVERY} blocks`);
        }
        continue;
      }
      const own = kitBody(st);
      const boxes = plotBoxes(s, 0, null);
      let clash = false;
      for (const k of cells.keys()) {
        const [x, z] = k.split(",").map(Number);
        if (own.has(k) && !(end === "end" ? KIT.tw(street.f, x, z)[0] >= ta : KIT.tw(street.f, x, z)[0] < tb)) { clash = true; break; }
        if (boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1)) { clash = true; break; }
      }
      if (clash) continue;
      // splice the plan into the street (segments re-based on the street's tmin)
      const rebased = plan.segs.map((q) => ({ ...q, a: q.a + ta - (end === "end" ? street.tmin : ta) }));
      if (end === "end") {
        street.segs = street.segs.filter((q) => !(q.kind === "dead" && q.a === n - 13)).concat(rebased);
        street.H = street.H.slice(0, n - 13).concat(plan.H);
      } else {
        const shift = KIT_GROW;
        street.segs = rebased.concat(street.segs.filter((q) => !(q.kind === "dead" && q.a === 0)).map((q) => ({ ...q, a: q.a + shift })));
        street.H = plan.H.concat(street.H.slice(13));
        street.tmin -= shift;
      }
      street.segs.sort((p, q) => p.a - q.a);
      // A0.2: the replaced dead end's exit is GONE — the next drain decision back-fills its trunk outside the new street
      // (0.0.19: the record was simply dropped, and one queued behind the growth was written afterwards: open tunnels stayed)
      for (const o of street.outfalls || []) if (o && o.kind !== "side" && o.end === end && (end === "end" ? o.a >= ta : o.a < tb)) o.gone = true;
      kitTouch(st);
      // queue only the new stretch (and its dead end + outfall)
      const sub = { ...street, tmin: ta, H: plan.H, segs: plan.segs, access: [], tees: [] };
      const before = (st.kitQueue = st.kitQueue || []).length;
      queueKitStreet(st, sub);
      for (const op of st.kitQueue.slice(before)) op.sid = street.id;
      st.log.push(`day ${s.simDays.toFixed(0)}: street ${street.id} grew ${KIT_GROW} cells at its ${end} (${street.H.length} cells now)`);
      return true;
    }
    street.growFail = today;
  }
  return false;
}

// ------------------------------------------------------------------------------------------------ THE GRID (D-C534 §3, his C1 / C2 / C4)
// Streets of one FAMILY share the main street's axis; a street's t maps to the main's t by tOff (mainT = t + tOff).
// Junction windows lie on GRID LINES every GRID_PITCH cells of mainT from the main street's middle (and on the main's
// two founding windows). A window opens a PARALLEL street at pitch SIDE_OFFSETS (60 first) joined by a connector, or —
// when a parallel already stands there — a CONNECTOR to it (the block closes). Two tees at one t make a CROSSROADS.
const GRID_PITCH = 56;                                           // D-C545: blocks 43 x 47 (medieval scale, R1); 70 left side streets without a second window
const JW = 13;                                                   // a junction window (a tee / cross piece) is 13 cells
function tOffOf(street) { return street.tOff || 0; }
/** the family's junction windows, as [t, t + 12] in a street's frame, lying wholly inside [tlo, thi] with 13 cells of
 *  street to spare at both ends (never in a dead end) */
function gridWindowsIn(gridMid, tOff, tlo, thi, margin = 13) {
  const out = [];
  if (gridMid === undefined) return out;
  for (let k = -12; k <= 12; k++) { const tt = gridMid + k * GRID_PITCH - tOff; if (tt >= tlo + margin && tt + JW - 1 <= thi - margin) out.push([tt, tt + JW - 1]); }
  return out;
}
/** the windows where a junction may open on `street`'s `side`: [t, ...] (each a flat 13-cell stretch on that side, no
 *  access piece over it, no tee there yet, clear of the dead ends), nearest the settlement's middle first */
function junctionWindows(st, street, side) {
  const out = [];
  const have = (street.tees || []).filter((j) => j.side === side).map((j) => j.t);
  const anyTee = (street.tees || []).map((j) => j.t);
  const acc = street.access || [];
  const tmin = street.tmin, tmax = street.tmin + street.H.length - 1;
  const flatOk = (t) => { for (let q = t; q < t + JW; q++) { const h = kitHAt(street, q); if (h === undefined || h !== kitHAt(street, t)) return false; } return true; };
  const freeOk = (t) => !acc.some((c) => c + 1 >= t && c - 1 <= t + JW - 1) && !have.some((j) => Math.abs(j - t) < JW);
  const cands = new Set();
  for (const r of street.reserved || []) if (r[2] === side && !r[3]) cands.add(r[0]);
  for (const [a] of gridWindowsIn(st.gridMid, tOffOf(street), tmin, tmax)) cands.add(a);
  for (const tt of cands) {
    if (winReleased(st, street, side, tt)) continue;                         // 1.3.225: given back to the houses
    if (!flatOk(tt) || !freeOk(tt)) continue;
    // the square's frontage (the main street's -v side at the square) never takes a tee — the square is the k = 0 cross line there
    if (street.sqT && side === -1 && tt <= street.sqT[1] + 2 && tt + JW - 1 >= street.sqT[0] - 2) continue;
    // a tee at this t on the other side makes the junction a crossroads: fine (the cross piece); a tee within 13 on the
    // other side but not at the same t would overlap: skip
    if (anyTee.some((j) => j !== tt && Math.abs(j - tt) < JW)) continue;
    out.push(tt);
  }
  const centre = (street.mid ?? (tmin + tmax) / 2);
  out.sort((p, q) => Math.abs(p - centre) - Math.abs(q - centre));
  return out;
}
/** an existing street of the same family parallel to `base` at offset side * D (its corridor's w in base's frame) */
function parallelAt(st, base, side, D) {
  for (const o of st.streets) {
    if (o === base || o.kind !== "kit" || o.role === "connector") continue;
    if (o.f.ux !== base.f.ux || o.f.uz !== base.f.uz) continue;
    const [, w] = KIT.tw(base.f, o.f.ox, o.f.oz);
    if (w === side * D) return o;
  }
  return null;
}
/** queue a junction piece on a street: a tee, or the cross when the other side already has a tee at the same t */
function queueJunction(st, street, tj, side, H, width) {
  const other = (street.tees || []).find((j) => j.t === tj && j.side === -side);
  const w = width || st.width || "v";
  if (other) {
    const p = KIT.teePiece(street.f, tj, H, 1, w);
    st.kitQueue.push({ op: "piece", kind: "cross13", x: p.x, y: p.y, z: p.z, rot: p.rot, sid: street.id, a: tj, len: 13, H });
    st.crossroads = (st.crossroads || 0) + 1;
  } else {
    const p = KIT.teePiece(street.f, tj, H, side, w);
    st.kitQueue.push({ op: "piece", kind: "tee13", x: p.x, y: p.y, z: p.z, rot: p.rot, sid: street.id, a: tj, len: 13, H });
  }
}
/** a connector between base (window tj, side) and a parallel street `other` whose window at the same mainT must be flat
 *  and free; returns true when queued */
function openConnector(s, st, lsite, base, tj, side, other, blocked) {
  const tOther = tj + tOffOf(base) - tOffOf(other);
  if (!junctionWindows(st, other, -side).includes(tOther)) return false;
  const Hb = kitHAt(base, tj), Hn = kitHAt(other, tOther);
  if (Hb === undefined || Hn === undefined) return false;
  const [, wOther] = KIT.tw(base.f, other.f.ox, other.f.oz);
  const D = Math.abs(wOther);
  const Lc = D - 13;
  if (Lc < 7) return false;
  const f = base.f;
  const [cx0, cz0] = KIT.cellOf(f, tj, side > 0 ? 13 : -1);
  const fc = KIT.frameOf(cx0, cz0, [side * f.vx, side * f.vz], [f.ux, f.uz]);
  const gc = KIT.groundAlong(lsite, fc, 0, Lc);
  const pc = Math.abs(Hn - Hb) > Math.floor(Lc / 7) ? { cost: Infinity } : KIT.planProfile(gc, { ...STREET_OPTS, startDead: false, endDead: false, startH: Hb, endH: Hn });
  const cellsC = pc.cost === Infinity ? null : KIT.corridorCells(fc, pc, 0, new Map());
  if (!cellsC || blocked(cellsC)) {
    // D-C546 (B3): the storeys of a stepped town — the parallels sit at different levels (or the land between will not
    // hold a 13-wide street): a 7-wide CLIMBING LEG at 1 in 4 joins the two windows instead (a job; tees are laid when it lands)
    startLegJob(st, base, tj, side, other, tOther);
    return false;
  }
  for (const r of base.reserved || []) if (r[0] === tj && r[2] === side) r[3] = true;
  for (const r of other.reserved || []) if (r[0] === tOther && r[2] === -side) r[3] = true;
  base.tees = base.tees || []; base.tees.push({ t: tj, side, H: Hb });
  other.tees = other.tees || []; other.tees.push({ t: tOther, side: -side, H: Hn });
  const idc = st.nextStreetId++;
  const conn = { kind: "kit", id: idc, role: "connector", f: fc, tmin: 0, H: pc.H, segs: pc.segs, access: [], tees: [], reserved: [], mid: Lc / 2 };
  st.streets.push(conn);
  kitTouch(st);
  st.kitQueue = st.kitQueue || [];
  queueJunction(st, base, tj, side, Hb);
  queueJunction(st, other, tOther, -side, Hn);
  queueKitStreet(st, conn);
  st.blocksClosed = (st.blocksClosed || 0) + 1;
  st.log.push(`day ${s.simDays.toFixed(0)}: a cross street joins street ${base.id} and street ${other.id} (${Lc} cells)${st.crossroads ? `; crossroads ${st.crossroads}` : ""}`);
  return true;
}
/** open a PARALLEL street (pitch SIDE_OFFSETS) at the next free junction window, joined by a connector; where a parallel
 *  already stands at that offset, a connector to it instead.
 *  0.0.25c: a JOB (system.runJob) that yields after every plan — run 0.0.25c's synchronous scan took up to 2.3 s in one
 *  tick (fresh land read live), a freeze the player would feel. History: the budgeted scan (0.0.12) kept a cursor
 *  (job, offset); 0.0.25 (E3) found the half missing from it (the scan never passed its first half). Now the whole scan
 *  runs across ticks; the street it finds lands in the state and a waiting plot takes it on its next try. */
const sideJobs = new Set();
/** 1.3.224: at most two street searches at once (each holds an 80k-step search state: script memory) */
const searchBusy = () => sideJobs.size + legJobs.size + benchJobs.size >= 2;
function startSideJob(st) {
  if (sideJobs.has(st.id) || searchBusy()) return false;
  sideJobs.add(st.id);
  const gen = sideStreetJob(st.id);
  function* wrapped() { try { yield* gen; } finally { sideJobs.delete(st.id); } }
  try { system.runJob(wrapped()); } catch (e) { sideJobs.delete(st.id); console.warn(`[CIV-CLOCK] side job: ${e}`); return false; }
  return true;
}
function* sideStreetJob(stId) {
  const s = load();
  const st = s.settlements.find((x) => x.id === stId);
  if (!st || !st.kit) return;
  if (st.sideRest !== undefined && s.simDays < st.sideRest && (!st.border || st.border.r === st.sideRestR)) return;
  // 1.3.231 (CIV-LAND): the windows given back to the houses after 3 failed passes (WIN_RELEASE) failed under the old
  // connector law; with terrace streets they get one more look (his hill town: "jobs":0 from day 37 on)
  if (!st.bandLaw) { st.bandLaw = 1; if (st.winFail) { delete st.winFail; st.log.push(`day ${s.simDays.toFixed(0)}: the surveyors look again at the junctions given back to the houses (terrace streets)`); } }
  const dim = world.getDimension(st.dim);
  const lsite = liveSite(dim, siteOf(st));
  const blockedNow = () => {
    const boxes = plotBoxes(s, 0, null), body = kitBody(st);
    return (m) => { for (const k of m.keys()) { if (body.has(k)) return true; const [x, z] = k.split(",").map(Number); if (boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1)) return true; } return false; };
  };
  const alive = () => load() === s && s.settlements.includes(st);
  const bases = st.streets.filter((x) => x.kind === "kit" && x.role !== "connector");
  // every (base, side, window) in one list, the main street first, windows nearest the middle first
  const jobs = [];
  for (const base of bases) for (const side of [1, -1]) for (const tj of junctionWindows(st, base, side)) jobs.push([base, side, tj]);
  const why = st.sideWhy = st.sideWhy || {};
  if (why.day !== Math.floor(s.simDays)) { for (const k of Object.keys(why)) why[k] = 0; why.day = Math.floor(s.simDays); }
  for (const k of ["jobs", "noH", "p2inf", "blocked2", "blockedC", "conn", "halves", "plans", "gone", "border", "passes"]) why[k] = why[k] || 0;
  why.jobs = jobs.length;
  const still = (base, side, tj) => st.streets.includes(base) && junctionWindows(st, base, side).includes(tj);
  for (const [base, side, tj] of jobs) {
    const Hb = kitHAt(base, tj);
    if (Hb === undefined) { why.noH++; continue; }
    let goneW = false;
    for (const D of KIT.SIDE_OFFSETS) {
      yield;
      if (!alive()) return;
      if (!still(base, side, tj)) { why.gone++; goneW = true; break; }                // the town took this window meanwhile
      const f = base.f;
      // a parallel already there -> a connector closes the block
      const other = parallelAt(st, base, side, D);
      if (other) { if (openConnector(s, st, lsite, base, tj, side, other, blockedNow())) { st.sideRest = undefined; save(); return; } why.conn++; continue; }
      const Lc = D - 13;
      const K = Math.min(3, Math.floor(Lc / 7));
      const [cx0, cz0] = KIT.cellOf(f, tj, side > 0 ? 13 : -1);
      const fc = KIT.frameOf(cx0, cz0, [side * f.vx, side * f.vz], [f.ux, f.uz]);
      const gc = KIT.groundAlong(lsite, fc, 0, Lc);
      yield;
      // D-C545: the longest parallel the land holds (its halves tried longest first: 70 carries the grid windows at +-56
      // from its junction, so the blocks can close); the family's grid windows inside it stay flat (its own junction
      // window always); a hill that cannot hold them flat gets the street without them
      let best = null, landH;                                               // landH (1.3.231): the land's own junction level
      for (const half of KIT_SIDE_HALVES) {
        if (best) break;
        why.halves++;
        const f2 = KIT.frameOf(f.ox + side * D * f.vx + (tj - half) * f.ux, f.oz + side * D * f.vz + (tj - half) * f.uz, [f.ux, f.uz], [f.vx, f.vz]);
        const L2 = 2 * half + 13;
        const tOff2 = tOffOf(base) + tj - half;
        const ground = KIT.groundAlong(lsite, f2, 0, L2);
        yield;
        const gridFlat = gridWindowsIn(st.gridMid, tOff2, 0, L2 - 1).filter(([a]) => Math.abs(a - half) >= JW);
        for (const withGrid of gridFlat.length ? [true, false] : [false]) {
          // 0.0.22: the land's own junction height first (ONE profile with the junction window held level at any height,
          // then the connector to it) — the 2K + 1 fixed heights below only when that fails
          const pf = KIT.planProfile(ground, { ...STREET_OPTS, flat: [[half - 1, half + 13], ...(withGrid ? gridFlat : [])] });
          why.plans++; yield;
          if (pf.cost === Infinity) continue;                       // no height at all holds this street: the fixed ones cannot either
          const Hf = pf.H[half];
          if (landH === undefined) landH = Hf;
          if (Hf !== undefined && Math.abs(Hf - Hb) <= K && pf.H.slice(half, half + 13).every((h) => h === Hf)) {
            const pc = KIT.planProfile(gc, { ...STREET_OPTS, startDead: false, endDead: false, startH: Hb, endH: Hf });
            why.plans++; yield;
            if (pc.cost < Infinity) { best = { c: pf.cost + pc.cost, p2: pf, pc, Hn: Hf, withGrid, half, f2, L2, tOff2 }; break; }
          }
          for (let dh = -K; dh <= K; dh++) {
            const Hn = Hb + dh;
            const fixed = new Map(); for (let tt = half; tt < half + 13; tt++) fixed.set(tt, Hn);
            const p2 = KIT.planProfile(ground, { ...STREET_OPTS, fixed, flat: [[half - 1, half + 13], ...(withGrid ? gridFlat : [])] });
            why.plans++; yield;
            if (p2.cost === Infinity) continue;
            const pc = KIT.planProfile(gc, { ...STREET_OPTS, startDead: false, endDead: false, startH: Hb, endH: Hn });
            why.plans++; yield;
            if (pc.cost === Infinity) continue;
            const c = p2.cost + pc.cost;
            if (!best || c < best.c) best = { c, p2, pc, Hn, withGrid, half, f2, L2, tOff2 };
          }
          if (best) break;
        }
        if (best) break;                                                    // the longest feasible half wins
      }
      // 1.3.231 (CIV-LAND, his 00:23 10-07 "use 4-part slope switchbacks"): ELEVATION BAND — the connector cannot reach the
      // land's own level from this junction (no parallel at all, or only one sunk into a trench below it): first a parallel
      // on its own contour level joined by a climbing switchback leg (KIT.planBandStreetJob, tests/test_band.mjs)
      const trench = !!best && landH !== undefined && Math.abs(landH - Hb) > K && best.Hn !== landH;
      if ((!best || trench) && KIT.BAND.offsets.includes(D) && (why.band || 0) < KIT.BAND.perPass) {
        why.band = (why.band || 0) + 1;
        const veto = bandVeto(s, st);
        const band = yield* KIT.planBandStreetJob(lsite, f, tj, side, Hb, D, veto.street, veto.leg, STREET_OPTS, why);
        if (!alive()) return;
        if (band && commitBand(s, st, base, tj, side, Hb, band, why)) { st.sideRest = undefined; save(); return; }
      }
      if (!best) { why.p2inf++; continue; }
      // commit against the town as it is NOW (it went on building while this job planned)
      if (!alive()) return;
      if (!still(base, side, tj)) { why.gone++; goneW = true; break; }
      const blocked = blockedNow();
      const { f2, half, tOff2 } = best;
      const cells2 = KIT.corridorCells(f2, best.p2, 0, new Map());
      const cellsC = KIT.corridorCells(fc, best.pc, 0, new Map());
      if (blocked(cells2)) { why.blocked2++; continue; }
      if (blocked(cellsC)) { why.blockedC++; continue; }
      if (!cellsInInfluence(st, cells2) || !cellsInInfluence(st, cellsC)) {                                                  // B4
        why.border++;
        st.borderWait = (st.borderWait || 0) + 1;
        if (st.border && st.borderWait % BORDER_ASK === 0 && !st.border.moves.some((m) => !m.done && m.blocked === null)) {
          planBorderGrowth(s, st, st.border.r + STONE_EVERY, !!s.accelNow);
          st.log.push(`day ${s.simDays.toFixed(0)}: a new street presses on the boundary stones: the council sends the surveyor out ${STONE_EVERY} blocks`);
        }
        continue;
      }
      // commit: the junction on the base street, the side street with its own junction, the connector
      for (const r of base.reserved || []) if (r[0] === tj && r[2] === side) r[3] = true;
      base.tees = base.tees || [];
      base.tees.push({ t: tj, side, H: Hb });
      const id2 = st.nextStreetId++, idc = st.nextStreetId++;
      // the new street's outward window at its junction stays reserved: the cross street may run straight on to the next
      // parallel (restored in 0.0.13; it is also the family's grid window when the junction lies on a grid line)
      const side2 = { kind: "kit", id: id2, role: "side", f: f2, tmin: 0, H: best.p2.H, segs: best.p2.segs, access: [], mid: half + 6,
                      tees: [{ t: half, side: -side, H: best.Hn }], reserved: [[half, half + 12, side]], tOff: tOff2 };
      const conn = { kind: "kit", id: idc, role: "connector", f: fc, tmin: 0, H: best.pc.H, segs: best.pc.segs, access: [], tees: [], reserved: [], mid: Lc / 2 };
      st.streets.push(side2, conn);
      kitTouch(st);
      st.kitQueue = st.kitQueue || [];
      queueJunction(st, base, tj, side, Hb);
      queueKitStreet(st, conn);
      queueKitStreet(st, side2);
      st.log.push(`day ${s.simDays.toFixed(0)}: a side street opened ${D} blocks ${side > 0 ? "beyond" : "before"} street ${base.id} (${best.L2} cells, junction at y ${Hb}, the side street at y ${best.Hn}, a ${Lc}-cell connector${best.withGrid ? "" : "; its grid windows could not be held flat"})`);
      st.sideRest = undefined;
      st.roomFound = (st.roomFound || 0) + 1; st.roomDay = Math.floor(s.simDays);
      save();
      return;
    }
    if (!goneW && alive()) winFailed(st, base, side, tj);                         // 1.3.225: every offset failed from this window
  }
  if (!alive()) return;
  st.sideRest = s.simDays + SIDE_REST; st.sideRestR = st.border ? st.border.r : null;
  why.passes++;
  if (!why.said || why.said !== why.day) { why.said = why.day; console.warn(`[CIV-CLOCK] ${st.name} day ${why.day}: no side street could open — ${JSON.stringify(why)}`); }
}
// 0.0.25b/c: the ROOM SEARCH runs in the background — a town with plots waiting for room keeps a side-street job going
// (one at a time; one new street a day at most, the waiting plots take it first)
const ROOM_EVERY = 100, ROOM_EVERY_ACCEL = 10;
let roomLast = 0;
// 1.3.228 (B1 / BF1): a heartbeat slot (17 of 20, optional: shed under load); its own gate keeps the 100 / 10-tick pace
HB.register("room", { fn: () => {
  let s;
  try { s = load(); } catch { return; }
  const now = system.currentTick;
  if (now - roomLast < (s.accelNow ? ROOM_EVERY_ACCEL : ROOM_EVERY)) return;
  roomLast = now;
  // 1.3.231 (CIV-LAND): the wide survey — one settlement at a time, in the background (startWideSurvey)
  if (!wideJobs.size) for (const st of s.settlements) { try { if (wideNeed(s, st) && startWideSurvey(s, st)) break; } catch (e) { console.warn(`[CIV-CLOCK] wide survey start: ${e}`); break; } }
  for (const st of s.settlements) {
    if (!st.kit || st.phase !== "built" || !((st.leftover || []).length || (st.civicLeft || []).length) || (st.kitQueue || []).length > 40) continue;
    if (st.roomDay === Math.floor(s.simDays) || sideJobs.has(st.id)) continue;
    if (st.sideRest !== undefined && s.simDays < st.sideRest && (!st.border || st.border.r === st.sideRestR)) continue;
    if (startSideJob(st)) st.roomAsked = (st.roomAsked || 0) + 1;
    break;                                                                          // one settlement a beat
  }
} });

/** block closing (tier >= town, one a day): a connector between two adjacent parallels at a free grid line */
function closeBlocks(s, st) {
  const dim = world.getDimension(st.dim);
  const lsite = liveSite(dim, siteOf(st));
  const boxes = plotBoxes(s, 0, null);
  const body = kitBody(st);
  const blocked = (m) => { for (const k of m.keys()) { if (body.has(k)) return true; const [x, z] = k.split(",").map(Number); if (boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1)) return true; } return false; };
  const t0 = Date.now();
  const bases = st.streets.filter((x) => x.kind === "kit" && x.role !== "connector");
  const why = { pairs: 0, windows: 0, otherWin: 0, tried: 0 };
  // 0.0.25 (the R-22 audit): the windows in one list and a CURSOR over it — the old loop restarted at the first window
  // every call and stopped on the budget, so with slow connector plans the later windows were never tried
  const jobs = [];
  for (const base of bases) for (const side of [1, -1]) {
    for (const D of KIT.SIDE_OFFSETS) {
      const other = parallelAt(st, base, side, D);
      if (!other) continue;
      why.pairs++;
      for (const tj of junctionWindows(st, base, side)) {
        why.windows++;
        if (junctionWindows(st, other, -side).includes(tj + tOffOf(base) - tOffOf(other))) why.otherWin++;
        jobs.push([base, side, other, tj]);
      }
    }
  }
  const start = Math.min(st.closeCursor || 0, jobs.length);
  for (let i = start; i < jobs.length; i++) {
    if (i > start && Date.now() - t0 > PLAN_MS) { st.closeCursor = i; return false; }
    const [base, side, other, tj] = jobs[i];
    why.tried++;
    if (openConnector(s, st, lsite, base, tj, side, other, blocked)) { st.closeCursor = 0; return true; }
  }
  st.closeCursor = 0;
  if (!st.closeSaid || s.simDays - st.closeSaid > 10) { st.closeSaid = s.simDays; console.warn(`[CIV-CLOCK] ${st.name} day ${s.simDays.toFixed(0)}: no block closed — ${JSON.stringify(why)}`); }
  return false;
}

// ------------------------------------------------------------------------------------------------ BENCHES + SWITCHBACK ROADS (D-C534 §2.3, his C5)
const BENCH_DIST = [70, 110], BENCH_STEP = 35, BENCH_LENS = [100, 80, 59], BENCH_WAIT = 5;
const benchJobs = new Set();
/** every departure a road can leave from: the far face of each dead end of each kit street (not connectors) */
function departures(st) {
  const out = [];
  for (const street of st.streets.filter((x) => x.kind === "kit" && x.role !== "connector")) {
    for (const seg of street.segs.filter((q) => q.kind === "dead")) {
      const atStart = seg.a === 0;
      const t = atStart ? street.tmin - 1 : street.tmin + seg.a + 13;
      const d = atStart ? [-street.f.ux, -street.f.uz] : [street.f.ux, street.f.uz];
      const H = kitHAt(street, atStart ? street.tmin : street.tmin + seg.a);
      if (H === undefined) continue;
      const endName = atStart ? "start" : "end";
      const outs = (street.roadsOut || []).filter((r) => r.end === endName);
      if (outs.some((r) => !r.gate)) continue;                                        // one bench road per end
      const stub = outs.length ? (st.roads7 || []).find((r) => r.gate && r.from === street.id && r.end === endName) : null;
      if (stub) {                                                                     // a road out through the gate: depart from its far end
        const last = stub.cells[stub.cells.length - 1];
        out.push({ sid: street.id, end: endName, P: [last[0] + d[0], last[1] + d[1]], d, H: stub.H[stub.H.length - 1] });
      } else out.push({ sid: street.id, end: endName, P: KIT.cellOf(street.f, t, 6), d, H });
    }
  }
  return out;
}
/** the settlement's bounding box over its corridors and plots */
function settlementBox(s, st, coreOnly = true) {
  // 0.0.15: the CORE box — the main family's streets (not the benches 100 blocks out, which are quarters of their own
  // reached by road) and the plots on them; the wall ring and the bench search use this one. coreOnly = false: everything.
  let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
  const benchIds = new Set(st.streets.filter((x) => x.kind === "kit" && x.bench).map((x) => x.id));
  for (const street of st.streets) {
    if (street.kind !== "kit" || (coreOnly && street.bench)) continue;
    for (const t of [street.tmin, street.tmin + street.H.length - 1]) for (const w of [0, 12]) { const [x, z] = KIT.cellOf(street.f, t, w); x0 = Math.min(x0, x); x1 = Math.max(x1, x); z0 = Math.min(z0, z); z1 = Math.max(z1, z); }
  }
  for (const b of plotsOf(s, st)) {
    if (coreOnly && b.kit && benchIds.has(b.kit.sid)) continue;
    const def = BUILDINGS[b.family]; if (!def) continue;
    const [fx, fz] = b.rot % 2 ? [def.size[2], def.size[0]] : [def.size[0], def.size[2]];
    x0 = Math.min(x0, b.x); x1 = Math.max(x1, b.x + fx - 1); z0 = Math.min(z0, b.z); z1 = Math.max(z1, b.z + fz - 1);
  }
  return isFinite(x0) ? [x0, x1, z0, z1] : null;
}
/** the job: find a NEW BENCH (a stretch where a kit street of BENCH_LENS cells fits, 60-120 blocks out) and a NARROW
 *  ROAD to it from the nearest dead end; yields between every planner call. On success commits both. */
function* benchJob(stId) {
  const s0 = load();
  const st0 = s0.settlements.find((x) => x.id === stId);
  if (!st0) return;
  const dim = world.getDimension(st0.dim);
  const lsite = liveSite(dim, siteOf(st0));
  const box = settlementBox(s0, st0);
  if (!box) return;
  const vetoFn = kitVeto(s0);
  const deps = departures(st0);
  // the veto as a SET over the search area (the road planner asks millions of times)
  const R = BENCH_DIST[BENCH_DIST.length - 1] + 40;
  const vx0 = box[0] - R, vx1 = box[1] + R, vz0 = box[2] - R, vz1 = box[3] + R;
  const vetoSet = new Set();
  for (const k of kitBody(st0).keys()) vetoSet.add(k);
  for (const [x0, x1, z0, z1] of plotBoxes(s0, 0, null)) for (let x = Math.max(x0, vx0); x <= Math.min(x1, vx1); x++) for (let z = Math.max(z0, vz0); z <= Math.min(z1, vz1); z++) vetoSet.add(`${x},${z}`);
  for (const k of streetHeights(s0).keys()) vetoSet.add(k);
  for (const r of st0.roads7 || []) r.cells.forEach(([x, z], i) => { const d = DIRS4[r.dirs[i]], p = [-d[1], d[0]]; for (let k = -3; k <= 3; k++) vetoSet.add(`${x + p[0] * k},${z + p[1] * k}`); });
  yield;
  // the ROAD's veto has no tunnels (they run 13 below; a road's cut never reaches them); the bench street's does
  const roadVeto = (x, z) => vetoSet.has(`${x},${z}`) || (x < vx0 || x > vx1 || z < vz0 || z > vz1 ? vetoFn(x, z) : false);
  const tunnels = tunnelCells(s0);
  const veto = (x, z) => roadVeto(x, z) || tunnels.has(`${x},${z}`);
  if (!deps.length) { st0.benchFail = s0.simDays; return; }
  // 1. bench candidates: anchors on rings around the box, both axes; the street starts at the anchor and runs +u
  const cands = [];
  let n = 0, outside = 0;
  for (const D of BENCH_DIST) {
    const [x0, x1, z0, z1] = [box[0] - D, box[1] + D, box[2] - D, box[3] + D];
    const ring = [];
    for (let x = x0; x <= x1; x += BENCH_STEP) { ring.push([x, z0]); ring.push([x, z1]); }
    for (let z = z0 + BENCH_STEP; z < z1; z += BENCH_STEP) { ring.push([x0, z]); ring.push([x1, z]); }
    for (const [ax, az] of ring) {
      const g = lsite.at(ax, az);
      if (g === undefined || lsite.isWater(ax, az)) continue;
      // along the local contour: the axis across which the ground changes least (both ways along it)
      const gx = (lsite.at(ax + 10, az) ?? g) - (lsite.at(ax - 10, az) ?? g), gz = (lsite.at(ax, az + 10) ?? g) - (lsite.at(ax, az - 10) ?? g);
      const axes = Math.abs(gx) >= Math.abs(gz) ? [[[0, 1], [1, 0]], [[0, -1], [-1, 0]]] : [[[1, 0], [0, 1]], [[-1, 0], [0, -1]]];
      for (const [u, v] of axes) {
        for (const L of BENCH_LENS) {
          const f = KIT.frameOf(ax - 6 * v[0], az - 6 * v[1], u, v);          // the anchor on the centre line (w 6)
          const ground = KIT.groundAlong(lsite, f, 0, L);
          if (ground.filter((c) => !c).length > L * 0.2) continue;
          // B4: the bench lies inside the boundary stones
          if (!cellsInInfluence(st0, KIT.corridorCells(f, { H: ground.map(() => 0) }, 0, new Map()))) { outside++; continue; }
          // the bench must not touch the settlement's own body
          let clash = false;
          for (let tt = 0; tt < L && !clash; tt += 4) for (let w = 0; w < 13; w += 6) { const [x, z] = KIT.cellOf(f, tt, w); if (veto(x, z)) clash = true; }
          if (clash) continue;
          const mid = L >> 1;
          const plan = KIT.planProfile(ground, { ...STREET_OPTS, flat: [[mid - 6, mid + 6]] });
          n++;
          if (n % 3 === 0) yield;
          if (plan.cost === Infinity) continue;
          const ramps = plan.segs.filter((q) => q.kind === "ramp").length, bridges = plan.segs.filter((q) => q.kind === "bridge").length;
          if (bridges) continue;
          // 0.0.14: the road ARRIVES straight into one of the bench's dead ends: the 7 cells beyond that end must be
          // ground the road can hold at the end's level (a cutting <= ROAD_CUT_MAX, a fill <= ROAD_CUT or a deck); the
          // ends that pass are offered (both when both do) — a bench whose ends both sit under a hillside is skipped
          const ends = [];
          for (const end of [[-1, [u[0], u[1]], plan.H[0]], [L, [-u[0], -u[1]], plan.H[L - 1]]]) {
            const [tEnd, dArr, Hend] = end;
            let ok = true;
            for (let k = 1; k <= 7 && ok; k++) {
              const [x, z] = KIT.cellOf(f, tEnd < 0 ? tEnd - k + 1 : tEnd + k - 1, 6);   // the cells beyond the end, away from the street
              const g = lsite.at(x, z);
              if (g === undefined || lsite.isWater(x, z) || g - Hend > KIT.ROAD_CUT_MAX) ok = false;
            }
            if (ok) ends.push({ P1: KIT.cellOf(f, tEnd, 6), d1: dArr, H1: Hend });
          }
          if (!ends.length) continue;
          cands.push({ f, L, plan, per: plan.cost / L + ramps * 0.5, anchor: [ax, az], D, ends });
          break;                                                               // the longest street that fits at this anchor
        }
      }
    }
  }
  cands.sort((p, q) => p.per - q.per);
  // 2. a road to the best benches (either reachable end; the two nearest departures each)
  for (const c of cands.slice(0, 4)) {
    const benchCells = KIT.corridorCells(c.f, c.plan, 0, new Map());
    const blocked = (x, z) => roadVeto(x, z) || benchCells.has(`${x},${z}`);
    const ground = (x, z) => { const g = lsite.at(x, z); return g === undefined ? undefined : { g, water: lsite.isWater(x, z) }; };
    for (const { P1, d1, H1 } of c.ends) {
      const sorted = deps.slice().sort((p, q) => (Math.abs(p.P[0] - P1[0]) + Math.abs(p.P[1] - P1[1])) - (Math.abs(q.P[0] - P1[0]) + Math.abs(q.P[1] - P1[1])));
      for (const dep of sorted.slice(0, 2)) {
        // the departure's own approach: the 7 cells ahead of it must hold the road at its level
        let ok = true;
        for (let k = 1; k <= 7 && ok; k++) { const g = lsite.at(dep.P[0] + dep.d[0] * k, dep.P[1] + dep.d[1] * k); if (g !== undefined && g - dep.H > KIT.ROAD_CUT_MAX) ok = false; }
        if (!ok) { console.warn(`[CIV-CLOCK] bench road: departure ${dep.P} ${dep.d} H${dep.H} faces a hillside (skipped)`); continue; }
        const stats = {};
        const road = yield* KIT.planRoadJob(ground, blocked, dep.P, dep.d, P1, d1, dep.H, H1, 6, stats);
        if (!road) { console.warn(`[CIV-CLOCK] bench road ${dep.P} ${dep.d} H${dep.H} -> ${P1} ${d1} H${H1}: ${JSON.stringify(stats)}`); continue; }
        commitBench(stId, c, dep, road);
        return;
      }
    }
  }
  const s = load();
  const st = s.settlements.find((x) => x.id === stId);
  if (st) {
    st.benchFail = s.simDays;
    st.log.push(`day ${s.simDays.toFixed(0)}: no bench within ${BENCH_DIST[BENCH_DIST.length - 1]} blocks could be reached by a road (${cands.length} benches, ${deps.length} departures${outside ? `, ${outside} beyond the boundary stones` : ""})`);
    // 0.0.23 (runs 0.0.22-23: the benches came only at town I — the ring held them out): benches beyond the stones make the
    // council send the surveyor out one more step (the same ask as the streets')
    // review 04:4x #16: only when NO bench inside the stones was found (benches inside that no road reaches are no reason
    // to move the stones)
    if (outside && !cands.length && st.border && !st.border.moves.some((m) => !m.done && m.blocked === null)) {
      planBorderGrowth(s, st, st.border.r + STONE_EVERY * 2, !!s.accelNow);
      st.log.push(`day ${s.simDays.toFixed(0)}: the town needs a bench beyond its stones: the council sends the surveyor out ${STONE_EVERY * 2} blocks`);
    }
    save();
  }
}
function commitBench(stId, c, dep, road) {
  const s = load();
  const st = s.settlements.find((x) => x.id === stId);
  if (!st) return;
  const mid = c.L >> 1;
  const id = st.nextStreetId++;
  const street = { kind: "kit", id, role: "main", f: c.f, tmin: 0, H: c.plan.H, segs: c.plan.segs, access: [], tees: [], mid,
                   reserved: [[mid - 6, mid + 6, 1], [mid - 6, mid + 6, -1]], bench: true };
  st.streets.push(street);
  const from = st.streets.find((x) => x.kind === "kit" && x.id === dep.sid);
  if (from) (from.roadsOut = from.roadsOut || []).push({ end: dep.end, to: id });
  const rid = (st.nextRoadId = (st.nextRoadId || 1)) ; st.nextRoadId++;
  // the road record: compact (cells as flat ints, H, turns, ramp segs)
  const rec = { id: rid, from: dep.sid, end: dep.end, to: id, cells: road.cells.map(([x, z]) => [x, z]), H: road.H, turns: road.turns,
                ramps: road.segs.filter((q) => q.kind === "ramp").map((q) => [q.a, q.dir]), rampLen: KIT.ROAD_RAMP,
                dirs: road.dirs.map((d) => d[0] === 1 ? 0 : d[1] === 1 ? 1 : d[0] === -1 ? 2 : 3) };
  (st.roads7 = st.roads7 || []).push(rec);
  kitTouch(st);
  st.kitQueue = st.kitQueue || [];
  for (let i = 0; i < rec.cells.length; i += 7) st.kitQueue.push({ op: "road", rid, a: i, len: Math.min(7, rec.cells.length - i), H: rec.H[i], sid: id });
  queueKitStreet(st, street);
  st.log.push(`day ${s.simDays.toFixed(0)}: a new bench ${c.D} blocks out at ${c.anchor[0]} ${c.anchor[1]} (street ${id}, ${c.L} cells) reached by a ${rec.cells.length}-cell road with ${rec.turns.length} turns from street ${dep.sid}'s ${dep.end}`);
  delete st.benchFail;
  save();
}
// ------------------------------------------------------------------------------------------------ CLIMBING LEGS (D-C546, B3)
const legJobs = new Set();
/** a 7-wide 1-in-4 road between the windows of two parallel streets whose levels a kit connector cannot join: from the
 *  branch mouth of a tee on `base` at tj (side) to the branch mouth of a tee on `other` at tOther (-side) */
function* legJob(stId, baseId, tj, side, otherId, tOther) {
  const s0 = load();
  const st0 = s0.settlements.find((x) => x.id === stId);
  if (!st0) return;
  const base = st0.streets.find((x) => x.id === baseId), other = st0.streets.find((x) => x.id === otherId);
  if (!base || !other) return;
  const dim = world.getDimension(st0.dim);
  const lsite = liveSite(dim, siteOf(st0));
  const Hb = kitHAt(base, tj), Hn = kitHAt(other, tOther);
  if (Hb === undefined || Hn === undefined) return;
  const f = base.f;
  // the mouths: the cell just outside each tee's branch, the road heading away from base / into other
  // 1.3.231 (CIV-LAND): d1 was -side * v — an arrival heading back toward base, from inside other's own corridor: every
  // shape was vetoed (his 1.3.224 log, 1620 of 1620); KIT.bandMouths arrives heading INTO other (tests/test_band.mjs)
  const { P0, d0, P1, d1 } = KIT.bandMouths(f, tj, side, other.f, tOther);
  const own = kitBody(st0);
  const boxes = plotBoxes(s0, 0, null);
  // 1.3.224 (his log: every one of 1620 shapes vetoed, 1 pop): the leg's veto now matches the bench road's — the sewer
  // tunnels run 6+ below the streets and a road's cut never reaches them — and the first blocked cell is NAMED in the log
  const bodies = s0.settlements.filter((x) => x.kit).map((x) => kitBody(x));
  const legacy = streetHeights(s0);
  const whyBlocked = (x, z) => { const k = `${x},${z}`; if (own.has(k)) return "own street"; if (boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1)) return "plot"; if (legacy.has(k)) return "old street"; if (bodies.some((m) => m.has(k))) return "street"; return null; };
  const blocked = (x, z) => whyBlocked(x, z) !== null;
  const ground = (x, z) => { const g = lsite.at(x, z); return g === undefined ? undefined : { g, water: lsite.isWater(x, z) }; };
  const stats = {};
  const road = yield* KIT.planRoadJob(ground, blocked, P0, d0, P1, d1, Hb, Hn, 6, stats);
  if (!road) {
    let first = null;
    for (let k = 0; k <= 10 && !first; k++) for (let q = -KIT.ROAD_HALF; q <= KIT.ROAD_HALF && !first; q++) {
      const x = P0[0] + d0[0] * k + (-d0[1]) * q, z = P0[1] + d0[1] * k + d0[0] * q;
      const w = whyBlocked(x, z); if (w) first = [x, z, k, w]; else if (ground(x, z) === undefined) first = [x, z, k, "ground not loaded"];
    }
    console.warn(`[CIV-CLOCK] climbing leg ${P0} -> ${P1} (H ${Hb} -> ${Hn}): ${JSON.stringify(stats)}${first ? ` · first blocked cell ${first[0]} ${first[1]} (${first[2]} out): ${first[3]}` : ""}`);
    (st0.legFail = st0.legFail || {})[`${baseId}:${tj}:${side}`] = s0.simDays; save(); return;
  }
  commitLeg(stId, baseId, tj, side, otherId, tOther, Hb, Hn, road);
}
function commitLeg(stId, baseId, tj, side, otherId, tOther, Hb, Hn, road) {
  const s = load();
  const st = s.settlements.find((x) => x.id === stId);
  if (!st) return;
  const base = st.streets.find((x) => x.id === baseId), other = st.streets.find((x) => x.id === otherId);
  if (!base || !other) return;
  for (const r of base.reserved || []) if (r[0] === tj && r[2] === side) r[3] = true;
  for (const r of other.reserved || []) if (r[0] === tOther && r[2] === -side) r[3] = true;
  base.tees = base.tees || []; base.tees.push({ t: tj, side, H: Hb, leg: true });
  other.tees = other.tees || []; other.tees.push({ t: tOther, side: -side, H: Hn, leg: true });
  const rid = (st.nextRoadId = (st.nextRoadId || 1)); st.nextRoadId++;
  const rec = { id: rid, from: baseId, end: `leg:${tj}`, to: otherId, leg: true, cells: road.cells.map(([x, z]) => [x, z]), H: road.H, turns: road.turns,
                ramps: road.segs.filter((q) => q.kind === "ramp").map((q) => [q.a, q.dir]), rampLen: KIT.ROAD_RAMP,
                dirs: road.dirs.map((d) => d[0] === 1 ? 0 : d[1] === 1 ? 1 : d[0] === -1 ? 2 : 3) };
  (st.roads7 = st.roads7 || []).push(rec);
  kitTouch(st);
  st.kitQueue = st.kitQueue || [];
  queueJunction(st, base, tj, side, Hb);
  queueJunction(st, other, tOther, -side, Hn);
  for (let i = 0; i < rec.cells.length; i += 7) st.kitQueue.push({ op: "road", rid, a: i, len: Math.min(7, rec.cells.length - i), H: rec.H[i], sid: baseId });
  st.legs = (st.legs || 0) + 1;
  st.log.push(`day ${s.simDays.toFixed(0)}: a climbing leg joins street ${baseId} (y ${Hb}) and street ${otherId} (y ${Hn}): ${rec.cells.length} cells, ${rec.turns.length} turns`);
  save();
}
// 1.3.231 (CIV-LAND) ELEVATION BANDS: the cells a band street (street) and its climbing leg (leg) may not take — plots and the
// crown's reserve, every settlement's corridors, the narrow roads, the old streets; the street also never over a sewer tunnel
function bandVeto(s, st) {
  const fc = freeSets(s);
  const leg = (x, z) => {
    const k = `${x},${z}`;
    if (fc.roadCells.has(k) || fc.legacy.has(k) || fc.bodies.some((m) => m.has(k)) || inReserve(s, x, z)) return true;
    for (const [x0, x1, z0, z1] of boxesNear(fc, x, x, z, z)) if (x >= x0 && x <= x1 && z >= z0 && z <= z1) return true;
    return false;
  };
  return { leg, street: (x, z) => leg(x, z) || fc.tunnels.has(`${x},${z}`) };
}
/** commit a planned band street (KIT.planBandStreetJob) against the town as it is NOW: the street on its own level, then
 *  the climbing leg and both tees (commitLeg). false when the window was taken meanwhile, a cell is vetoed now, or the
 *  street / leg reach past the boundary stones (the council is asked to move them, as for a side street) */
function commitBand(s, st, base, tj, side, Hb, band, why) {
  if (!st.streets.includes(base) || !junctionWindows(st, base, side).includes(tj)) { why.gone++; return false; }
  const cells2 = KIT.corridorCells(band.f2, band.p2, 0, new Map());
  const legCells = new Map(band.road.cells.map(([x, z]) => [`${x},${z}`, 0]));
  const veto = bandVeto(s, st);
  for (const k of cells2.keys()) { const [x, z] = k.split(",").map(Number); if (veto.street(x, z)) { why.blocked2++; return false; } }
  if (!cellsInInfluence(st, cells2) || !cellsInInfluence(st, legCells)) {
    why.border++;
    st.borderWait = (st.borderWait || 0) + 1;
    if (st.border && st.borderWait % BORDER_ASK === 0 && !st.border.moves.some((m) => !m.done && m.blocked === null)) {
      planBorderGrowth(s, st, st.border.r + STONE_EVERY, !!s.accelNow);
      st.log.push(`day ${s.simDays.toFixed(0)}: a terrace street presses on the boundary stones: the council sends the surveyor out ${STONE_EVERY} blocks`);
    }
    return false;
  }
  const id2 = st.nextStreetId++;
  const street = { kind: "kit", id: id2, role: "side", band: true, f: band.f2, tmin: 0, H: band.p2.H, segs: band.p2.segs, access: [], mid: band.half + 6,
                   tees: [], reserved: [[band.half, band.half + 12, side]], tOff: tOffOf(base) + band.tOff };
  st.streets.push(street);
  kitTouch(st);
  st.kitQueue = st.kitQueue || [];
  queueKitStreet(st, street);
  commitLeg(st.id, base.id, tj, side, id2, band.half, Hb, band.Hn, band.road);       // the leg, both tees, the road ops
  st.bands = (st.bands || 0) + 1;
  st.log.push(`day ${s.simDays.toFixed(0)}: a TERRACE street opened ${band.D} blocks ${side > 0 ? "beyond" : "before"} street ${base.id} on its own level (y ${band.Hn}, ${band.rise >= 0 ? "+" : ""}${band.rise} from the junction at y ${Hb}; ${band.L2} cells), reached by a switchback of ${band.road.cells.length} cells, ${band.road.turns.length} turns`);
  st.roomFound = (st.roomFound || 0) + 1; st.roomDay = Math.floor(s.simDays);
  return true;
}
function startLegJob(st, base, tj, side, other, tOther) {
  const key = `${st.id}:${base.id}:${tj}:${side}`;
  if (legJobs.has(key) || searchBusy()) return;
  const s = load();
  const failed = (st.legFail || {})[`${base.id}:${tj}:${side}`];
  if (failed !== undefined && s.simDays - failed < 20) return;                // a failed pair rests 20 days
  legJobs.add(key);
  const gen = legJob(st.id, base.id, tj, side, other.id, tOther);
  function* wrapped() { try { yield* gen; } finally { legJobs.delete(key); } }
  try { system.runJob(wrapped()); } catch (e) { legJobs.delete(key); console.warn(`[CIV-CLOCK] leg job: ${e}`); }
}
function startBenchJob(st) {
  if (benchJobs.has(st.id) || searchBusy()) return;
  benchJobs.add(st.id);
  const gen = benchJob(st.id);
  function* wrapped() { try { yield* gen; } finally { benchJobs.delete(st.id); } }
  try { system.runJob(wrapped()); } catch (e) { benchJobs.delete(st.id); console.warn(`[CIV-CLOCK] bench job: ${e}`); }
}
const DIRS4 = [[1, 0], [0, 1], [-1, 0], [0, -1]];
const CARD4 = ["east", "south", "west", "north"];
/** lay 7 cells of a narrow road (its full ROAD_W width, elbow squares where a turn falls in these cells) */
function layRoadOp(dim, s, st, rec, a, len) {
  const boxes = plotBoxes(s, 0, null);
  const inPlot = (x, z) => boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  const rampAt = new Map();                                                  // cell index -> [q 1..4, uphill dir index]
  const RL = rec.rampLen || 7;                                               // the segment's length: 4 (his 4-part ramp) or the old 7
  for (const [ra, dir] of rec.ramps) {
    for (let q = 0; q < 4; q++) {
      const i = dir > 0 ? ra + q : ra + (RL - 4) + q;                       // up: the first 4 cells; down: the last 4
      const di = rec.dirs[Math.min(i, rec.dirs.length - 1)];
      rampAt.set(i, [dir > 0 ? q + 1 : 4 - q, dir > 0 ? di : (di + 2) % 4]);
    }
  }
  const turnSet = new Set(rec.turns);
  const done = new Set();
  const lay = (x, z, H, kerb) => {
    const key = `${x},${z}`;
    if (done.has(key) || inPlot(x, z)) return;
    done.add(key);
    levelColumn(dim, x, z, H, 3);
    sealWater(dim, x, z, H + 1, H + 4, "minecraft:air");                    // 0.0.19: never a puddle on the road
    try {
      const b = dim.getBlock({ x, y: H, z });
      if (b) b.setType("minecraft:cobblestone");
      if (kerb && !rec.noKerb) { const w = dim.getBlock({ x, y: H + 1, z }); if (w && w.typeId === "minecraft:air") w.setType("minecraft:cobblestone_wall"); }   // 1.3.226: lanes have no kerbs (doors open onto them)
    } catch { /* unloaded */ }
  };
  for (let i = a; i < a + len && i < rec.cells.length; i++) {
    const [x, z] = rec.cells[i], H = rec.H[i], d = DIRS4[rec.dirs[i]], p = [-d[1], d[0]];
    if (turnSet.has(i)) {
      // the elbow square: kerbs on its far side and on the side the road does not leave by; the entry (behind) and the
      // exit sides stay open. d = the incoming direction, out = the next leg's
      const out = DIRS4[rec.dirs[Math.min(i + 1, rec.dirs.length - 1)]];
      const outK = out[0] * p[0] + out[1] * p[1];                             // +1 / -1: which side the road leaves by
      for (let k = -3; k <= 3; k++) for (let m = -3; m <= 3; m++) {
        const kerb = m === 3 || k === -3 * outK || (m === -3 && Math.abs(k) === 3) ;
        lay(x + p[0] * k + d[0] * m, z + p[1] * k + d[1] * m, H, kerb);
      }
      continue;
    }
    for (let k = -3; k <= 3; k++) lay(x + p[0] * k, z + p[1] * k, H, Math.abs(k) === 3);
    const r = rampAt.get(i);
    if (r) {
      const [q, up] = r;
      for (let k = -2; k <= 2; k++) {
        try {
          const b = dim.getBlock({ x: x + p[0] * k, y: H + 1, z: z + p[1] * k });
          if (b) b.setPermutation(BlockPermutation.resolve(`pw:ramp_cobble_4_q${q}`, { "minecraft:cardinal_direction": CARD4[up] }));
        } catch (e) { console.warn(`[CIV-CLOCK] road ramp: ${e}`); }
      }
    }
    // the faces: a stepped cut uphill, a cobble face downhill (both sides checked); water at the shoulders sealed (0.0.19)
    for (const sgn of [1, -1]) {
      const [ex, ez] = [x + p[0] * 4 * sgn, z + p[1] * 4 * sgn];
      if (!inPlot(ex, ez)) sealWater(dim, ex, ez, H - 1, H + 4, "minecraft:cobblestone");
      const g = groundAt(dim, ex, ez);
      if (g === undefined || inPlot(ex, ez)) continue;
      if (g >= H + 2) terraceFace(dim, [[ex, ez]], H, [p[0] * sgn, p[1] * sgn], 2, inPlot);
      else if (g < H - 1) wallColumn(dim, x + p[0] * 3 * sgn, z + p[1] * 3 * sgn, g + 1, H - 1);
    }
  }
  return done.size;
}

// ------------------------------------------------------------------------------------------------ WALLS + GATES (D-C534 §3, tier city; a second ring at metropolis)
const WALL_H = 5, WALL_MARGIN = 10, GATE_W = 13, TOWER = 8;
/** the perimeter line of a ring box: [[x, z], ...] clockwise from the north-west corner */
function ringLine(box) {
  const [x0, x1, z0, z1] = box;
  const line = [];
  for (let x = x0; x <= x1; x++) line.push([x, z0]);
  for (let z = z0 + 1; z <= z1; z++) line.push([x1, z]);
  for (let x = x1 - 1; x >= x0; x--) line.push([x, z1]);
  for (let z = z1 - 1; z > z0; z--) line.push([x0, z]);
  return line;
}
/** stake a wall ring around the settlement and queue it in 16-cell ops; gates where a corridor crosses the line */
function queueWall(s, st, ring) {
  const box0 = settlementBox(s, st);
  if (!box0) return 0;
  const box = [box0[0] - WALL_MARGIN, box0[1] + WALL_MARGIN, box0[2] - WALL_MARGIN, box0[3] + WALL_MARGIN];
  // 0.0.17: a plot the ring line would cross (a bench-street house at the core's edge: cottage #13's frame became wall)
  // pushes that side of the ring out past it (up to 3 rounds)
  for (let round = 0; round < 3; round++) {
    let moved = false;
    for (const [x0, x1, z0, z1] of plotBoxes(s, 0, st)) {
      const inside = x0 >= box[0] && x1 <= box[1] && z0 >= box[2] && z1 <= box[3];
      const outside = x1 < box[0] || x0 > box[1] || z1 < box[2] || z0 > box[3];
      if (inside || outside) continue;
      if (x0 < box[0] && x1 >= box[0]) { box[0] = x0 - 3; moved = true; }
      if (x1 > box[1] && x0 <= box[1]) { box[1] = x1 + 3; moved = true; }
      if (z0 < box[2] && z1 >= box[2]) { box[2] = z0 - 3; moved = true; }
      if (z1 > box[3] && z0 <= box[3]) { box[3] = z1 + 3; moved = true; }
    }
    if (!moved) break;
  }
  const line = ringLine(box);
  const body = kitBody(st);
  const index = new Map(line.map(([x, z], i) => [`${x},${z}`, i]));
  const gates = [], gateCentres = [];
  line.forEach(([x, z], i) => { if (body.has(`${x},${z}`)) gates.push(i); });
  // a GATE where each street's axis meets the ring (the road out continues the street): 13 cells of gap centred on
  // the axis, and a stub road from the dead end to the gate
  let stubs = 0;
  const dim = world.getDimension(st.dim);
  const lsite = liveSite(dim, siteOf(st));
  for (const street of st.streets.filter((x) => x.kind === "kit" && x.role !== "connector")) {
    for (const end of ["start", "end"]) {
      const n = street.H.length;
      const t0 = end === "start" ? street.tmin - 1 : street.tmin + n;
      const d = end === "start" ? [-street.f.ux, -street.f.uz] : [street.f.ux, street.f.uz];
      const H = kitHAt(street, end === "start" ? street.tmin : street.tmin + n - 1);
      // walk out along the axis to the ring
      let hit = null, k = 0;
      for (; k < 200; k++) { const [x, z] = KIT.cellOf(street.f, t0 + k * (end === "start" ? -1 : 1), 6); const i = index.get(`${x},${z}`); if (i !== undefined) { hit = i; break; } }
      if (hit === null || k < 3) continue;
      // 1.3.228 (B9 / TR5): two gates never closer than GATE_MIN cells along the ring (the second street ends inside the wall)
      const ringD = (a2, b2) => { const d2 = Math.abs(a2 - b2); return Math.min(d2, line.length - d2); };
      if (gateCentres.some((c) => ringD(c, hit) < GATE_MIN)) { (st.slotWhy = st.slotWhy || {}).gateMerged = (st.slotWhy.gateMerged || 0) + 1; continue; }
      gateCentres.push(hit);
      for (let q = -6; q <= 6; q++) gates.push((hit + q + line.length) % line.length);
      // the stub: a straight narrow road from the dead end's far face to the gate line (planned level-ish: one profile)
      if ((street.roadsOut || []).some((r) => r.end === end)) continue;
      const cells = [];
      for (let q = 0; q <= k; q++) cells.push(KIT.cellOf(street.f, t0 + q * (end === "start" ? -1 : 1), 6));
      const ground = cells.map(([x, z]) => { const g = lsite.at(x, z); return g === undefined ? undefined : { g, water: lsite.isWater(x, z) }; });
      const plan = KIT.planProfile(ground, { startDead: false, endDead: false, startH: H, flat: [[0, Math.min(6, cells.length - 1)]], maxCut: 4, maxFill: 4, noBridge: true });
      if (plan.cost === Infinity) continue;
      const rid = (st.nextRoadId = (st.nextRoadId || 1)); st.nextRoadId++;
      const di = d[0] === 1 ? 0 : d[1] === 1 ? 1 : d[0] === -1 ? 2 : 3;
      const rec = { id: rid, from: street.id, end, to: 0, gate: true, cells, H: plan.H, turns: [], ramps: plan.segs.filter((q) => q.kind === "ramp").map((q) => [q.a, q.dir]), dirs: cells.map(() => di) };
      (st.roads7 = st.roads7 || []).push(rec);
      (street.roadsOut = street.roadsOut || []).push({ end, to: 0, gate: true });
      for (let i = 0; i < cells.length; i += 7) (st.kitQueue = st.kitQueue || []).push({ op: "road", rid, a: i, len: Math.min(7, cells.length - i), H: plan.H[i], sid: street.id });
      stubs++;
    }
  }
  const rec = { ring, box, n: line.length, gates: [...new Set(gates)], laid: 0 };
  (st.walls = st.walls || []).push(rec);
  st.kitQueue = st.kitQueue || [];
  for (let i = 0; i < line.length; i += 16) st.kitQueue.push({ op: "wall", ring, a: i, len: Math.min(16, line.length - i), H: 0, sid: 1 });
  st.log.push(`day ${s.simDays.toFixed(0)}: a ${ring === 1 ? "city" : "second"} wall staked out: ${line.length} cells, ${rec.gates.length} gate cells, ${stubs} road(s) out`);
  return line.length;
}
function layWallOp(dim, s, st, rec, a, len) {
  const line = ringLine(rec.box);
  const gateSet = new Set(rec.gates);
  // 0.0.17: the wall never stands on ANY plot (its own included: a bench-street house at the core's edge lost its frame)
  const foreign = plotBoxes(s, 1, null);
  const isForeign = (x, z) => foreign.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  let n = 0;
  for (let i = a; i < a + len && i < line.length; i++) {
    const [x, z] = line[i];
    // a gate: the corridor's cells stay open; the cells beside the gap carry towers
    const nearGate = [-2, -1, 0, 1, 2].some((d) => gateSet.has((i + d + line.length) % line.length));
    if (gateSet.has(i) || isForeign(x, z)) continue;
    const g = groundAt(dim, x, z);
    if (g === undefined) continue;
    const tower = nearGate && !gateSet.has(i);
    const top = g + (tower ? TOWER : WALL_H) + (!tower && i % 2 ? 1 : 0);
    for (let y = g + 1; y <= top; y++) { try { const blk = dim.getBlock({ x, y, z }); if (blk) { blk.setType("minecraft:stone_bricks"); n++; } } catch { /* unloaded */ } }
    if (tower) { try { dim.getBlock({ x, y: top + 1, z })?.setType("minecraft:torch"); } catch { /* left */ } }
    clearTreesOver(dim, x, z, top + 1);
  }
  rec.laid += n;
  return n;
}

/** tier town: the village width is resurfaced to the town width (his R3 = a) — every piece re-laid as t_* */
function widenKit(st) {
  if (!st.kit || st.width === "t") return 0;
  st.width = "t";
  const before = (st.kitQueue = st.kitQueue || []).length;
  for (const street of st.streets.filter((x) => x.kind === "kit")) {
    const laidAccess = street.accessLaid || [];
    queueKitStreet(st, { ...street, access: laidAccess });
  }
  // bridges are timber either way: skip their re-lay (the deck would be cut again for nothing)
  st.kitQueue = st.kitQueue.filter((op, i) => i < before || op.op !== "bridge");
  return st.kitQueue.length - before;
}

/** his 18:02: the village clears the floating leaves left in its land (felled trees' crowns hanging in the air). A leaf
 *  clump (26-connected) that touches no log is removed. Runs as a job over the settlement's extent, a column band per
 *  yield; the count goes into the chronicle. */
function* leafSweepJob(st) {
  const dim = world.getDimension(st.dim);
  const s = load();
  const boxes = plotBoxes(s, 0, st);
  for (const k of kitBody(st).keys()) { const [x, z] = k.split(",").map(Number); boxes.push([x, x, z, z]); }
  if (!boxes.length) return;
  let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
  for (const [a, b, c, d] of boxes) { x0 = Math.min(x0, a); x1 = Math.max(x1, b); z0 = Math.min(z0, c); z1 = Math.max(z1, d); }
  x0 -= 12; x1 += 12; z0 -= 12; z1 += 12;
  const y0 = (st.h0 ?? 64) - 8, y1 = (st.h0 ?? 64) + 40;
  const seen = new Set();
  let removed = 0, clumps = 0;
  const isLeaf = (id) => id.includes("leaves");
  const isWood = (id) => TREE_LOG(id);
  const types = leafTypes();
  if (!types.length) return;
  for (let bx = x0; bx <= x1; bx += 16) for (let bz = z0; bz <= z1; bz += 16) {
    let list;
    if (!boxLoaded(dim, bx, bz, Math.min(bx + 15, x1), Math.min(bz + 15, z1))) { yield; continue; }   // 1.3.228: asked, not thrown
    try {
      const vol = new BlockVolume({ x: bx, y: y0, z: bz }, { x: Math.min(bx + 15, x1), y: y1, z: Math.min(bz + 15, z1) });
      list = dim.getBlocks(vol, { includeTypes: types }, true);
    } catch { yield; continue; }
    const locs = [];
    try { for (const l of list.getBlockLocationIterator()) locs.push(l); } catch { /* unloaded */ }
    for (const l of locs) {
      const key = `${l.x},${l.y},${l.z}`;
      if (seen.has(key)) continue;
      // flood the clump (26-connected), noting whether any log touches it; cap the clump size (a forest is one clump)
      const clump = [], q = [[l.x, l.y, l.z]];
      seen.add(key);
      let anchored = false, n = 0;
      while (q.length && n < 4000) {
        const [x, y, z] = q.pop(); n++;
        clump.push([x, y, z]);
        for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
          if (!dx && !dy && !dz) continue;
          const k2 = `${x + dx},${y + dy},${z + dz}`;
          if (seen.has(k2)) continue;
          let id;
          { const nbk = blockAt(dim, x + dx, y + dy, z + dz); id = nbk ? nbk.typeId : undefined; }   // 1.3.227: no throwing read
          if (!id) { anchored = true; continue; }               // an unloaded neighbour: leave the clump alone
          if (isWood(id)) { anchored = true; continue; }
          // review 19:1x: a clump that rests on the GROUND (a hedge, a bush, leaves on a hillside) is not floating; leaves
          // hanging off a roof or in the air are (roofs, pw: blocks, are not ground)
          if (dy === -1 && dx === 0 && dz === 0 && isGround(id) && id !== "minecraft:water") { anchored = true; continue; }
          if (isLeaf(id)) { seen.add(k2); q.push([x + dx, y + dy, z + dz]); }
        }
        if (n % 200 === 0) yield;
      }
      if (q.length) anchored = true;                            // too big to judge: a forest, left alone
      if (!anchored) {
        clumps++;
        for (const [x, y, z] of clump) { try { blockAt(dim, x, y, z)?.setType("minecraft:air"); removed++; } catch { /* left */ } }
      }
    }
    yield;
  }
  st.leafSwept = (st.leafSwept || 0) + removed;
  if (removed) {
    const s2 = load();
    const st2 = s2.settlements.find((x) => x.id === st.id) || st;
    st2.leafSwept = (st2.leafSwept || 0) + removed;
    st2.log.push(`day ${s2.simDays.toFixed(0)}: the villagers cleared ${removed} floating leaves (${clumps} clump${clumps === 1 ? "" : "s"})`);
    save();
  }
}
// review 19:1x: the ids our packs really define (pw: from BP-02's blocks: + flowering azalea) and vanilla's; any id the engine
// does not know is dropped once (an unknown id in a block filter could make getBlocks throw -> nothing swept)
const LEAF_TYPES = ["minecraft:oak_leaves", "minecraft:spruce_leaves", "minecraft:birch_leaves", "minecraft:jungle_leaves", "minecraft:acacia_leaves",
  "minecraft:dark_oak_leaves", "minecraft:mangrove_leaves", "minecraft:cherry_leaves", "minecraft:azalea_leaves", "minecraft:azalea_leaves_flowered",
  "minecraft:pale_oak_leaves", "pw:oak_leaves", "pw:spruce_leaves", "pw:birch_leaves", "pw:jungle_leaves", "pw:acacia_leaves", "pw:dark_oak_leaves",
  "pw:mangrove_leaves", "pw:cherry_leaves", "pw:pale_oak_leaves", "pw:azalea_leaves", "pw:flowering_azalea_leaves"];
let leafTypesOk = null;
function leafTypes() {
  if (leafTypesOk) return leafTypesOk;
  leafTypesOk = LEAF_TYPES.filter((id) => { try { return !!BlockTypes.get(id); } catch { return false; } });
  if (leafTypesOk.length !== LEAF_TYPES.length) console.warn(`[CIV-CLOCK] leaf sweep: unknown ids dropped: ${LEAF_TYPES.filter((i) => !leafTypesOk.includes(i)).join(", ")}`);
  return leafTypesOk;
}
const leafJobs = new Set();
function sweepLeaves(st) {
  if (leafJobs.has(st.id)) return;
  leafJobs.add(st.id);
  const gen = leafSweepJob(st);
  function* wrapped() { try { yield* gen; } finally { leafJobs.delete(st.id); } }
  try { system.runJob(wrapped()); } catch (e) { leafJobs.delete(st.id); console.warn(`[CIV-CLOCK] leaf sweep: ${e}`); }
}

/** his 18:02: a PARK for the town — a level green on a plot of its own (12 deep, 15 along the street): gravel paths in a
 *  cross, benches (oak stairs) facing the paths, lanterns on posts, flowers, and young trees from our own templates. */
const PARK_DEF = { size: [12, 1, 15], dir: [] };
const PARK_TREES = ["oak", "birch", "cherry"];
function kitPark(s, st) {
  if (st.park) return false;
  const free = kitFree(s);
  for (const street of st.streets.filter((x) => x.kind === "kit" && x.role !== "connector")) {
    const { bySide } = kitStretches(street, st);
    const slot = KIT.placeAlong(street.f, bySide, PARK_DEF, null, street.mid ?? 0, free, new Set(street.access || []), 1);
    if (!slot) continue;
    st.park = { box: slot.box, H: slot.H, sid: street.id, side: slot.side, done: false };
    kitTouch(st);
    return true;
  }
  // 1.3.230 (PL; gate note "Park not placed (no flat 15-cell frontage)"): a PLATEAU park — a frontage rising up to 2 with
  // its gate within one step, judged by the plateau planner (the park's own box filled up to the fill dial)
  const lsite = liveSite(world.getDimension(st.dim), siteOf(st));
  const fc = freeSets(s);
  for (const street of st.streets.filter((x) => x.kind === "kit" && x.role !== "connector")) {
    const { bySide } = kitStretches(street, st);
    const freeP = (big, box, slot, f) => {
      if (!free(big, box, slot, f)) return false;
      slot._street = street;
      const pl = plateauLand(s, lsite, f, slot, fc, true);
      if (pl.kind !== "plateau") { st.plateauWhy = st.plateauWhy || {}; st.plateauWhy[`park ${pl.why}`] = (st.plateauWhy[`park ${pl.why}`] || 0) + 1; return false; }
      slot.land = pl;
      return true;
    };
    const slot = KIT.placeAlong(street.f, bySide, PARK_DEF, null, street.mid ?? 0, freeP, new Set(street.access || []), 1, 1, [],
      { riseMax: PLAN.PLATEAU.frontRise, doorStep: PLAN.PLATEAU.doorStep });
    if (!slot) continue;
    st.park = { box: slot.box, H: slot.H, sid: street.id, side: slot.side, done: false, at: slot.at, land: slot.land };
    st.log.push(`day ${s.simDays.toFixed(0)}: no level frontage for a park — a PLATEAU park is staked on street ${street.id} at y ${slot.H} (cut ${slot.land.cut}, fill ${slot.land.fill}; ${slot.land.stone} stone)`);
    kitTouch(st);
    return true;
  }
  return false;
}
function layPark(st) {
  const p = st.park;
  if (!p || p.done) return false;
  const dim = world.getDimension(st.dim);
  const [x0, x1, z0, z1] = p.box;
  try { if (!blockAt(dim, x0, p.H, z0) || !blockAt(dim, x1, p.H, z1)) return false; } catch { return false; }
  const cx = (x0 + x1) >> 1, cz = (z0 + z1) >> 1;
  const rnd = rng((st.seed + 4242) >>> 0);
  const FLOWERS = ["minecraft:poppy", "minecraft:dandelion", "minecraft:oxeye_daisy", "minecraft:cornflower", "minecraft:azure_bluet", "minecraft:allium"];
  for (let x = x0; x <= x1; x++) for (let z = z0; z <= z1; z++) {
    const g = groundAt(dim, x, z) ?? p.H;
    for (let y = g + 1; y < p.H; y++) blockAt(dim, x, y, z)?.setType("minecraft:dirt");
    for (let y = p.H + 1; y <= Math.max(g, p.H) + 4; y++) { const b = blockAt(dim, x, y, z); if (b && b.typeId !== "minecraft:air") b.setType("minecraft:air"); }
    clearTreesOver(dim, x, z, Math.max(g, p.H) + 4);
    const path = x === cx || z === cz;
    const edge = x === x0 || x === x1 || z === z0 || z === z1;
    blockAt(dim, x, p.H, z)?.setType(path ? "minecraft:gravel" : "minecraft:grass_block");
    if (path) blockAt(dim, x, p.H - 1, z)?.setType("minecraft:cobblestone");     // gravel never falls into a hollow
    if (!path && !edge && rnd() < 0.08) blockAt(dim, x, p.H + 1, z)?.setType(FLOWERS[Math.floor(rnd() * FLOWERS.length)]);
    if (edge && !path) blockAt(dim, x, p.H + 1, z)?.setType("minecraft:oak_fence");   // a closed fence; the four path ends are the gates
  }
  // benches beside the paths, lanterns at the crossing's corners
  const benches = [[cx - 1, cz - 3], [cx + 1, cz + 3], [cx - 3, cz + 1], [cx + 3, cz - 1]];
  // 1.3.228 (structure audit 10-06): our oak bench, each facing the path beside it (it was a vanilla oak stair, one facing for all)
  const benchFace = (x, z) => (x === cx - 1 || x === cx + 1 ? (x < cx ? "east" : "west") : (z < cz ? "south" : "north"));
  for (const [x, z] of benches) {
    try {
      const b = blockAt(dim, x, p.H + 1, z);
      if (!b) continue;
      b.setPermutation(BlockPermutation.resolve("pw:furn_bench_oak", { "minecraft:cardinal_direction": benchFace(x, z) }));
    } catch { try { blockAt(dim, x, p.H + 1, z)?.setType("pw:furn_bench_oak"); } catch { /* left */ } }
  }
  for (const [x, z] of [[cx - 1, cz - 1], [cx + 1, cz + 1]]) { try { blockAt(dim, x, p.H + 1, z)?.setType("minecraft:spruce_fence"); blockAt(dim, x, p.H + 2, z)?.setType("minecraft:lantern"); } catch { /* left */ } }
  // young trees from our own templates, one in each quarter (where a template of that species exists)
  const quarters = [[x0 + 2, z0 + 2], [x1 - 4, z0 + 2], [x0 + 2, z1 - 4], [x1 - 4, z1 - 4]];
  let planted = 0;
  quarters.forEach(([x, z], i) => {
    const sp = PARK_TREES[i % PARK_TREES.length];
    const names = Object.keys(PARK_TREE_SET).filter((n) => n.startsWith(sp === "cherry" ? "cherry_" : `${sp}_young_`));
    if (!names.length) return;
    const nm = names[Math.floor(rnd() * names.length)];
    const [, , , rx, , rz] = PARK_TREE_SET[nm];                 // the root block's cell in the template (y 0 = ground level)
    try { world.structureManager.place(`pw:trees/${nm}`, dim, { x: x + 1 - rx, y: p.H, z: z + 1 - rz }); planted++; } catch (e) { console.warn(`[CIV-CLOCK] park tree: ${e}`); }
  });
  p.done = true;
  st.log.push(`day ${load().simDays.toFixed(0)}: a park laid out at ${cx} ${cz} (${planted} young trees)`);
  // 1.3.230 (PL): a plateau park — its ring, walls, faces and drain (the park's box is the green above); paid from the
  // ledger as far as the stores and the treasury allow (a park has no stage bill)
  const street = p.land && p.land.kind === "plateau" ? st.streets.find((x) => x.kind === "kit" && x.id === p.sid) : null;
  if (street) {
    const L = st.ledger;
    if (L && L.v === 2) {
      const stone = Math.min(p.land.stone || 0, Math.max(0, Math.floor(L.stock.stone || 0)));
      const wages = Math.min(p.land.wages || 0, Math.max(0, L.treasury));
      ECON.pay(L, { mats: stone ? { stone } : {}, wages, blocks: stone });
      st.log.push(`day ${load().simDays.toFixed(0)}: the park's terrace — ${stone} stone from the stores, ${wages} p to the labourers`);
    }
    const stId = st.id;
    startPlateauJob(dim, { key: `park:${stId}`, f: street.f, side: p.side, at: p.at, fz: PARK_DEF.size[2], depth: PARK_DEF.size[0], P: p.H, sid: p.sid, stId,
      self: p.box, boxFillMax: PLAN.PLATEAU.fillMax, label: "the park", rec: () => { const s2 = load(); const st2 = s2.settlements.find((x) => x.id === stId); return st2 ? st2.park : null; }, fallback: null });
  }
  return true;
}

// ------------------------------------------------------------------------------------------------ living marks (step 4)
// The town changes the land: the quarry digs a stepped pit behind itself (stone counted into the ledger), the lumberyard
// fells the trees around it (template trees by their root blocks and natural ones by their trunks; stumps stay; timber
// counted), the farms are harvested by the day (grain = wheat actually grown), and the streets harden with use.
const TIER_IDX = (t) => TIERS.indexOf(t);
const TREE_LOG = (id) => id.endsWith("_log") || id.endsWith("_wood") || id.endsWith("_stem") || /pw:[a-z_]+_(young|mature|old|elder)$/.test(id) || id.endsWith("_root");
const TREE_LEAF = (id) => id.includes("leaves");

/** cells the land marks must never touch: EVERY settlement's plot boxes (+1 margin), squares and street cells (run
 *  0.0.11: a daughter's wall and a road ran through the mother's plots — the test was per settlement). `only` narrows
 *  it to one settlement when a caller wants its own extent. */
/** a plot's whole box [x0, x1, z0, z1] (inclusive): the structure plus its front YARD (b.yard cells on the door side:
 *  rot 1 faces north, 3 south, 0 west, 2 east), grown by `margin` all round */
function boxOf(b, margin = 0) {
  const [fx, , fz] = footprint(BUILDINGS[b.family], b.rot);
  const y = b.yard || 0;
  let x0 = b.x, x1 = b.x + fx - 1, z0 = b.z, z1 = b.z + fz - 1;
  if (b.rot === 1) z0 -= y; else if (b.rot === 3) z1 += y; else if (b.rot === 0) x0 -= y; else if (b.rot === 2) x1 += y;
  return [x0 - margin, x1 + margin, z0 - margin, z1 + margin];
}
function plotBoxes(s, margin = 1, only = null) {
  const boxes = [];
  for (const b of s.buildings) {
    if (only && b.settlement !== only.id) continue;
    boxes.push(boxOf(b, margin));
  }
  for (const st of s.settlements) if (st.square && (!only || st.id === only.id)) boxes.push([st.square.x - margin, st.square.x + LAND.SQUARE - 1 + margin, st.square.z - margin, st.square.z + LAND.SQUARE - 1 + margin]);
  for (const st of s.settlements) if (st.park && (!only || st.id === only.id)) { const [a, b2, c, d] = st.park.box; boxes.push([a - margin, b2 + margin, c - margin, d + margin]); }
  return boxes;
}
/** every street cell of every settlement (3 wide on either axis) -> its laid height */
function streetHeights(s, only = null) {
  const m = new Map();
  for (const st of s.settlements) {
    if (only && st.id !== only.id) continue;
    for (const [k, h] of bodyOf(st)) m.set(k, h);
  }
  return m;
}
/** a settlement's street body: its kit corridors (v1.3.219) or its legacy profile's 3-wide body */
function bodyOf(st) { return st.kit ? kitBody(st) : LAND.streetBody(st.profile || {}, st.axis || "x"); }
let occCache = null;
function occupiedTest(s, st = null) {
  const okey = `${s.buildings.length}:${s.settlements.map((x) => `${x.kitVer || 0}/${(x.streets || []).length}`).join(",")}`;
  if (occCache && occCache.key === okey && system.currentTick - occCache.tick < 400) return occCache.fn;
  const fn = occupiedBuild(s, st);
  occCache = { key: okey, tick: system.currentTick, fn };
  return fn;
}
// 1.3.227 (profiled at city II: a work beat's face search took up to 192 ms when this was rebuilt — 5 string keys per street
// cell, every 400 ticks): number keys, the street bodies read in place, the plot boxes indexed by 16-block cell
const OCC_OFF = 2097152, OCC_W = 4194304;
function occupiedBuild(s, st = null) {
  void st;
  const boxes = plotBoxes(s, 1, null);
  const near = new Set();
  const key = (x, z) => (x + OCC_OFF) * OCC_W + (z + OCC_OFF);
  for (const stl of s.settlements) {
    for (const k of bodyOf(stl).keys()) {
      const c = k.indexOf(","), x = +k.slice(0, c), z = +k.slice(c + 1);
      const K = key(x, z);
      near.add(K); near.add(K - 1); near.add(K + 1); near.add(K - OCC_W); near.add(K + OCC_W);
    }
  }
  const grid = new Map();
  for (const bx of boxes) {
    for (let gx = Math.floor(bx[0] / 16); gx <= Math.floor(bx[1] / 16); gx++) for (let gz = Math.floor(bx[2] / 16); gz <= Math.floor(bx[3] / 16); gz++) {
      const gk = gx * 100003 + gz;
      if (!grid.has(gk)) grid.set(gk, []);
      grid.get(gk).push(bx);
    }
  }
  return (x, z) => {
    if (near.has(key(x, z))) return true;
    const cell = grid.get(Math.floor(x / 16) * 100003 + Math.floor(z / 16));
    return !!cell && cell.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  };
}

/** the street tuple a plot remembers: [along0, along1, the street's row (east-west) or column (north-south)] */
function streetOf(slot) {
  return slot.axis === "z" ? [slot.wz - 1, slot.wz + slot.wfz - 1, slot.streetCol] : [slot.wx - 1, slot.wx + slot.wfx - 1, slot.streetRow];
}

/** a slot is free when its box touches no street cell or the square, and its box plus a one-cell margin touches no plot
 *  (the margin is not applied to streets: a plot stands right against its own street by design). Frame slots are
 *  translated to the world first. */
function slotFree(s, st) {
  // every settlement's plots count (a neighbour's plot is as solid as our own); the body is this settlement's streets
  const boxes = plotBoxes(s, 0, null);
  return LAND.slotVeto(streetHeights(s), boxes, st.square);
}

function backOf(b, def) {
  // the cell row just behind the back wall (local x = sx) and the plot's centre line, in world coords
  const [sx, , sz] = def.size;
  const [ox, oz] = rotXZ(sx + 1, Math.floor(sz / 2), sx, sz, b.rot);
  return { x: b.x + ox, z: b.z + oz };
}

/** the QUARRY pit: a stepped bowl dug into the ground behind the quarry (radius 4 + 2 per tier, 1 ring per step down) */
/** the QUARRY is worked: a stepped pit behind the yard that grows ring by ring and deeper toward the middle, at most
 *  maxBlocks a call (a day's work for its quarrymen); the pit's radius grows with the tier (4 + 2 per tier) and the
 *  settlement's needs (one more ring when the tier's pit is worked out, up to QUARRY_R_MAX). Returns the STONE dug
 *  (stone-class blocks), undefined when the pit's chunk is not loaded. The stone goes to the ledger by the caller. */
const QUARRY_R_MAX = 14, QUARRY_D_MAX = 9;
function digQuarry(dim, b, st, tierIdx, maxBlocks = Infinity) {
  const def = BUILDINGS[b.family];
  const c = backOf(b, def);
  void c;
  if (b.workedOut) return 0;                                                                             // 0.0.25: every pit site spent
  const occupied = occupiedTest(load(), st);
  const ctx = { dim, occupied, day: load().simDays, wake: (box) => { try { ensureTicking(load(), st, box, `quarry #${b.id} pit site`); } catch { /* left */ } } };
  const po = WORKMOD.pitOf(b, def, tierIdx, ctx);                                                       // its site chosen once
  if (po.wait) return undefined;                                                                         // 0.0.25d: the sites' land sleeps
  const { pit, cx, cz } = po;
  let dug = 0, removed = 0, seen = 0, unloaded = false;
  const r = pit.r, depth = pit.depth;
  const cells = (2 * r + 1) * (2 * r + 1);
  for (let n = 0; n < cells && removed < maxBlocks; n++) {
    const k = (pit.i + n) % cells;
    const i = Math.floor(k / (2 * r + 1)) - r, j = (k % (2 * r + 1)) - r;
    const d = Math.max(Math.abs(i), Math.abs(j));
    const steps = Math.min(depth, Math.floor((r - d) / 2) + 1);         // deeper toward the middle
    seen++;
    if (steps <= 0) continue;
    const x = cx + i, z = cz + j;
    if (occupied(x, z)) continue;
    try {
      const g = groundAt(dim, x, z);
      if (g === undefined) { unloaded = true; break; }
      // the pit floor at this cell: dig from the surface down `steps` below the ORIGINAL ground (b.pitTop remembered)
      b.pitTop = b.pitTop === undefined ? g : b.pitTop;
      // 1.3.228 (B2 / BF10): a log standing on the column (a tree, a player's cabin) — the column is left as a pillar: the
      // pit never undermines or cuts a log (the woodcutters fell real trees; a player's logs never)
      { let logCol = false; for (let y = g + 1; y <= g + 2; y++) { const up = blockAt(dim, x, y, z); if (up && TREE_LOG(up.typeId)) { logCol = true; break; } } if (logCol) continue; }
      const floor = b.pitTop - steps;
      for (let y = Math.min(g, b.pitTop); y > floor && removed < maxBlocks; y--) {
        const blk = blockAt(dim, x, y, z);
        if (!blk || blk.typeId === "minecraft:air" || blk.typeId === "minecraft:water" || blk.typeId === "minecraft:bedrock") continue;
        if (/stone|andesite|diorite|granite|deepslate|tuff|ore|gravel/.test(blk.typeId)) dug++;
        blk.setType("minecraft:air"); removed++;
      }
      for (let y = g + 1; y <= g + 2; y++) { const up = blockAt(dim, x, y, z); if (up && up.typeId !== "minecraft:air" && !isGround(up.typeId)) up.setType("minecraft:air"); }
    } catch { unloaded = true; break; }
  }
  if (unloaded && removed === 0) return undefined;
  pit.i = (pit.i + seen) % cells;
  // a worked-out pit grows a ring (and a step) up to the caps
  if (removed === 0 && seen >= cells) { WORKMOD.pitWorkedOut(b, tierIdx, ctx); if (b.workedOut && !b.workedOutSaid) { b.workedOutSaid = true; st.log.push(`day ${load().simDays.toFixed(0)}: the quarry (#${b.id}) is worked out — every pit site around it is spent`); } }
  b.dug = (b.dug || 0) + dug;
  return dug;
}

/** fell one tree: flood over log blocks from a trunk cell (radius 7, up 32), leaves within 2 of the removed logs; a stump stays */
const LEAF_REACH = 8;          // 1004b: a rootless tree's crown = leaves within this many face-steps of its logs (vanilla's decay reach)
const FELL_MAX_LEAVES = 1200;
/** 1004b (D-C563, his birches "incomplete and broken"): the cells of ONE tree. A structure tree — a pw root at or under
 *  its lowest log — gives its template's exact logs and leaves (nothing of a neighbour, nothing left floating, the T4 law
 *  of main.js). A rootless tree: its logs by the old flood, then every leaf reachable from them through leaves within
 *  LEAF_REACH steps. Returns null when no log stands at the start. */
function treeCells(dim, x, y, z, occupied = () => false, crown = true) {
  // 1.3.228 (B2 / BF10): a sleeping cell is recorded (unknown) — the town never judges or fells a tree it cannot see whole
  let unknown = false;
  const get = (cx, cy, cz) => { const bb = blockAt(dim, cx, cy, cz); if (bb === null) { unknown = true; return undefined; } return bb; };   // 1.3.227: no throwing read
  const logs = [];
  const seen = new Set();
  const q = [[x, y, z]];
  while (q.length && logs.length < 400) {
    const [cx, cy, cz] = q.pop();
    const key = `${cx},${cy},${cz}`;
    if (seen.has(key)) continue;
    seen.add(key);
    if (Math.abs(cx - x) > 7 || Math.abs(cz - z) > 7 || cy - y > 32 || cy < y - 1) continue;
    if (occupied(cx, cz)) continue;                                   // never a house's posts or the street
    const blk = get(cx, cy, cz);
    if (!blk || !TREE_LOG(blk.typeId)) continue;
    logs.push([cx, cy, cz, blk.typeId]);
    for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1], [1, 1, 0], [-1, 1, 0], [0, 1, 1], [0, 1, -1], [1, 0, 1], [-1, 0, -1], [1, 0, -1], [-1, 0, 1]])
      q.push([cx + dx, cy + dy, cz + dz]);
  }
  if (!logs.length) return null;
  const big = logs.length >= 400;
  const base = logs.reduce((a, l) => (l[1] < a[1] ? l : a), logs[0]);
  // the root: the base log itself, or a pw root block at most 3 below it (the trunk column is logs down to the root)
  for (let dy = 0; dy <= 3; dy++) {
    const b = get(base[0], base[1] - dy, base[2]);
    if (!b) break;
    const id = b.typeId;
    if (id.startsWith("pw:") && id.endsWith("_root")) {
      let root = null;
      try { root = { x: base[0], y: base[1] - dy, z: base[2], id, tpl: (b.permutation.getState("pw:tpl") ?? 0) + 16 * (b.permutation.getState("pw:tpl_hi") ?? 0), dir: b.permutation.getState("minecraft:cardinal_direction") }; }
      catch { root = null; }
      if (root) {
        let set = null;
        // 1.3.228 (B1 hygiene): the template's cells are read through blockAt (the default reader was the raw one in try)
        const present = (p, kind) => { const bb = blockAt(dim, p.x, p.y, p.z); return !!bb && (kind === "log" ? isTreeLogId(bb.typeId) : isTreeLeafId(bb.typeId)); };
        try { set = templateFallingSet(dim, root, { x: -1e9, y: -1e9, z: -1e9 }, { present }); } catch { set = null; }
        if (set) {
          const tlogs = [];
          for (const p of set.trunkAbove.concat(set.trunkBelow)) { if (occupied(p.x, p.z)) continue; const bb = get(p.x, p.y, p.z); tlogs.push([p.x, p.y, p.z, bb ? bb.typeId : "minecraft:air"]); }
          // R4 is judged on every log the flood met as well as the template's (a player's log touching a structure tree)
          return { logs: tlogs, flood: logs, leaves: set.leaves.map((p) => [p.x, p.y, p.z]), base: [root.x, root.y, root.z, id], tpl: set.name, rooted: true, unknown, big: false };
        }
        return { logs, flood: logs, leaves: crown ? crownOf(get, logs) : [], base, tpl: null, rooted: true, unknown, big };   // a root without a known template: still world-built (R3a)
      }
      break;
    }
    if (!TREE_LOG(id)) break;
  }
  return { logs, flood: logs, leaves: crown ? crownOf(get, logs) : [], base, tpl: null, rooted: false, unknown, big };
}
/** rootless: the crown by reach through leaves (LEAF_REACH face-steps from the logs). 1.3.228 (B2): the walk starts from
 *  the logs' own cells only — it skipped every cell the log flood had LOOKED at (its whole 14-neighbourhood: the leaves
 *  touching the trunk), so a felled rootless tree left its inner crown standing for the leaf sweep */
function crownOf(get, logs) {
  const leaves = [];
  const lseen = new Set(logs.map((l) => `${l[0]},${l[1]},${l[2]}`));
  let frontier = logs.map((l) => [l[0], l[1], l[2]]);
  for (let step = 0; step < LEAF_REACH && frontier.length && leaves.length < FELL_MAX_LEAVES; step++) {
    const next = [];
    for (const [cx, cy, cz] of frontier) {
      for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]) {
        const nx = cx + dx, ny = cy + dy, nz = cz + dz;
        const key = `${nx},${ny},${nz}`;
        if (lseen.has(key)) continue;
        lseen.add(key);
        const b = get(nx, ny, nz);
        if (!b || !isTreeLeafId(b.typeId)) continue;
        leaves.push([nx, ny, nz]);
        next.push([nx, ny, nz]);
      }
    }
    frontier = next;
  }
  return leaves;
}

// ------------------------------------------------------------------------------------------------ REAL TREES ONLY (B2 / BF10)
// His BIGCANOPY rule: only a real, world-built tree with its leaves may fall — a player's log never. The fit check found the
// woodcutter took ANY log 1-2 above the ground and a rootless tree had no natural-leaf and no placed-log test. Now every
// town felling (the woodcutter, the lumberyard's daily clearing, the trees over a worked cell) passes treeVerdict:
//   R4  no log of it (every log the flood meets) is on the placed-log ledger (pw_fell_rules touchesPlacedLog) — always fresh;
//   R3a a pw root under it (a structure tree), OR
//   R5  at least 3 NATURAL leaves touch its logs (hasNaturalCanopy through blockAt: the top TREE_R5_LOGS logs are examined);
//   and the whole tree is seen (no cell in a sleeping chunk), and the flood did not hit its 400-log cap (a log building).
// The verdict is cached in memory per start cell for TREE_TTL ticks (the woodcutter's search asks often); at the fell
// itself R4 is asked again. Counters: FELL (status -> fell).
const TREE_TTL = 6000, TREE_R5_LOGS = 64;
const treeVerdicts = new Map();                                   // "x,y,z" -> { ok, why, until }
export const FELL = { ok: 0, placed: 0, bare: 0, big: 0, asleep: 0, none: 0, cached: 0, felled: 0, refusedAtFell: 0 };
let fellPlaced = (logs) => touchesPlacedLog(logs);                 // the ledger test (the node tests inject their own)
export function __setPlacedTest(fn) { fellPlaced = fn || ((logs) => touchesPlacedLog(logs)); treeVerdicts.clear(); }
/** { ok, why } for a tree as read (treeCells' record); why = root | canopy | placed | bare | big | asleep | none */
export function treeVerdict(dim, tree) {
  if (!tree || !tree.logs.length) return { ok: false, why: "none" };
  if (tree.unknown) return { ok: false, why: "asleep" };
  const all = (tree.flood || tree.logs).concat(tree.flood && tree.flood !== tree.logs ? tree.logs : []);
  if (fellPlaced(all.map(([x, y, z]) => ({ x, y, z })))) return { ok: false, why: "placed" };
  if (tree.big) return { ok: false, why: "big" };
  if (tree.rooted) return { ok: true, why: "root" };
  const top = tree.logs.slice().sort((p, q2) => q2[1] - p[1]).slice(0, TREE_R5_LOGS).map(([x, y, z]) => ({ x, y, z }));
  return naturalCanopy(dim, top, 3) ? { ok: true, why: "canopy" } : { ok: false, why: "bare" };
}
/** may the town fell the tree standing at (x, y, z)? cached TREE_TTL ticks (a sleeping tree is not cached) */
export function treeOk(dim, x, y, z, occupied = () => false, now = system.currentTick) {
  const key = `${x},${y},${z}`;
  const c = treeVerdicts.get(key);
  if (c && c.until > now) { FELL.cached++; return c.ok; }
  const tree = treeCells(dim, x, y, z, occupied, false);
  const v = treeVerdict(dim, tree);
  FELL[v.ok ? "ok" : v.why] = (FELL[v.ok ? "ok" : v.why] || 0) + 1;
  if (v.why !== "asleep") {
    // the verdict holds for every log of the same flood (a cabin's other wall columns, a 2x2 trunk's partners: no re-judging)
    const e = { ok: v.ok, why: v.why, until: now + TREE_TTL };
    treeVerdicts.set(key, e);
    if (tree) for (const l of (tree.flood || tree.logs).slice(0, 400)) treeVerdicts.set(`${l[0]},${l[1]},${l[2]}`, e);
    if (treeVerdicts.size > 8192) {
      for (const [k, c] of treeVerdicts) if (c.until <= now) treeVerdicts.delete(k);
      for (const k of treeVerdicts.keys()) { if (treeVerdicts.size <= 6000) break; treeVerdicts.delete(k); }   // the oldest first
    }
  }
  return v.ok;
}
export function treeWhy(x, y, z) { const c = treeVerdicts.get(`${x},${y},${z}`); return c ? c.why : null; }
/** the cached verdict for the tree at (x, y, z): true / false, or undefined when it must be judged (costs reads) */
export function treeKnown(x, y, z, now = system.currentTick) { const c = treeVerdicts.get(`${x},${y},${z}`); return c && c.until > now ? c.ok : undefined; }

export function fellTree(dim, x, y, z, occupied = () => false, stump = true) {
  const tree = treeCells(dim, x, y, z, occupied);
  if (!tree) return 0;
  // 1.3.228 (B2 / BF10): judged again at the fell (R4 fresh — a log a player set since the search is never cut)
  const v = treeVerdict(dim, tree);
  if (!v.ok) { FELL.refusedAtFell++; treeVerdicts.set(`${x},${y},${z}`, { ok: false, why: v.why, until: system.currentTick + TREE_TTL }); return 0; }
  const { logs, leaves, base } = tree;
  let removed = 0;
  for (const [lx, ly, lz] of leaves) { try { const lf = blockAt(dim, lx, ly, lz); if (lf && isTreeLeafId(lf.typeId)) { lf.setType("minecraft:air"); removed++; } } catch { /* unloaded */ } }
  for (const [lx, ly, lz] of logs) { try { blockAt(dim, lx, ly, lz)?.setType("minecraft:air"); } catch { /* unloaded */ } }
  FELL.felled++;
  if (!stump) return logs.length;
  // the stump: the base log's tier if it was one of ours, else a plain oak-tier stump of the same wood when we have it
  const m = /pw:([a-z_]+_(?:young|mature|old|elder))(?:_root)?$/.exec(base[3]);
  try {
    const stumpId = m ? `pw:${m[1]}_stump` : null;
    const blk = blockAt(dim, base[0], base[1], base[2]);
    if (blk) { if (stumpId) { try { blk.setType(stumpId); } catch { blk.setType(base[3].replace("_root", "")); } } else blk.setType(base[3]); }
  } catch { /* left */ }
  return logs.length;
}

function fellTree_old_unused(dim, x, y, z, occupied = () => false, stump = true) {
  const logs = [];
  const seen = new Set();
  const q = [[x, y, z]];
  while (q.length && logs.length < 400) {
    const [cx, cy, cz] = q.pop();
    const key = `${cx},${cy},${cz}`;
    if (seen.has(key)) continue;
    seen.add(key);
    if (Math.abs(cx - x) > 7 || Math.abs(cz - z) > 7 || cy - y > 32 || cy < y - 1) continue;
    if (occupied(cx, cz)) continue;                                   // never a house's posts or the street
    let blk;
    try { blk = dim.getBlock({ x: cx, y: cy, z: cz }); } catch { continue; }
    if (!blk || !TREE_LOG(blk.typeId)) continue;
    logs.push([cx, cy, cz, blk.typeId]);
    for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1], [1, 1, 0], [-1, 1, 0], [0, 1, 1], [0, 1, -1], [1, 0, 1], [-1, 0, -1], [1, 0, -1], [-1, 0, 1]])
      q.push([cx + dx, cy + dy, cz + dz]);
  }
  if (!logs.length) return 0;
  const base = logs.reduce((a, l) => (l[1] < a[1] ? l : a), logs[0]);
  let leaves = 0;
  for (const [lx, ly, lz] of logs) {
    for (let dx = -2; dx <= 2; dx++) for (let dy = -1; dy <= 2; dy++) for (let dz = -2; dz <= 2; dz++) {
      try { const lf = dim.getBlock({ x: lx + dx, y: ly + dy, z: lz + dz }); if (lf && TREE_LEAF(lf.typeId)) { lf.setType("minecraft:air"); leaves++; } } catch { /* unloaded */ }
    }
  }
  for (const [lx, ly, lz] of logs) { try { dim.getBlock({ x: lx, y: ly, z: lz })?.setType("minecraft:air"); } catch { /* unloaded */ } }
  if (!stump) return logs.length;
  // the stump: the base log's tier if it was one of ours, else a plain oak-tier stump of the same wood when we have it
  const m = /pw:([a-z_]+_(?:young|mature|old|elder))(?:_root)?$/.exec(base[3]);
  try {
    const stumpId = m ? `pw:${m[1]}_stump` : null;
    const blk = dim.getBlock({ x: base[0], y: base[1], z: base[2] });
    if (blk) { if (stumpId) { try { blk.setType(stumpId); } catch { blk.setType(base[3].replace("_root", "")); } } else blk.setType(base[3]); }
  } catch { /* left */ }
  return logs.length;
}



// ------------------------------------------------------------------------------------------------ MOBS OUT (1004b, his 17:59)
// A structure placed by script leaves whatever stood there inside its walls. Every entity in the placed box that is not a
// player, a civ, a lead, a marker, an item or one of the engine's furniture entities is removed. The box is inclusive.
const KEEP_ENTITY = new Set(["minecraft:player", "minecraft:item", "minecraft:xp_orb", "pw:lead", "pw:marker", "pw:hatch_lid", "ft:falling_tree", "pw:leaf_litter",
  "minecraft:painting", "minecraft:item_frame", "minecraft:glow_item_frame", "minecraft:armor_stand", "minecraft:boat", "minecraft:chest_boat", "minecraft:minecart",
  "minecraft:chest_minecart", "minecraft:hopper_minecart", "minecraft:villager_v2", "minecraft:wandering_trader", "minecraft:iron_golem"]);
function clearMobsIn(dim, x0, y0, z0, x1, y1, z1) {
  let n = 0;
  let list = [];
  try { list = dim.getEntities({ location: { x: (x0 + x1) / 2, y: (y0 + y1) / 2, z: (z0 + z1) / 2 }, maxDistance: Math.hypot(x1 - x0, y1 - y0, z1 - z0) / 2 + 2 }); } catch { return 0; }
  for (const e of list) {
    try {
      if (!e || !e.isValid) continue;
      const id = e.typeId;
      if (KEEP_ENTITY.has(id)) continue;
      if (id === "minecraft:villager_v2" || e.hasTag("civ:villager")) continue;
      const l = e.location;
      if (l.x < x0 || l.x > x1 + 1 || l.y < y0 || l.y > y1 + 1 || l.z < z0 || l.z > z1 + 1) continue;
      e.remove(); n++;
    } catch { /* gone */ }
  }
  return n;
}

// ------------------------------------------------------------------------------------------------ FLOODING (1004b, his 17:38)
// "they attempted to build over water; the walls went up but the water itself was never removed and flooded the streets".
// kitDrain: before a piece is laid, every water cell in the corridor (w 0..12) from the pieces' lowest tunnel (H - 15) to
// H + 3 becomes air (above H) or dirt (at and below H, the pieces replace what they cover); the corridor's RING (w -1 and
// 13, the cells beyond the piece's ends) is sealed with stone bricks wherever it holds water between H - 16 and H + 6 — a
// cofferdam, so the pond cannot flow back. floodWatch (daily): the surface cells of every laid street (H + 1 .. H + 3)
// that hold water are drained and the water's source (the first wet cell outward on the same level) is sealed.
const DRAIN_FILL = "minecraft:stone_bricks";
const isWater = (id) => id === "minecraft:water" || id === "minecraft:flowing_water";
function kitDrain(dim, street, a, len, H, boxes = []) {
  const f = street.f;
  const inPlot = (x, z) => boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  let n = 0;
  const cell = (x, y, z, id) => { try { const b = blockAt(dim, x, y, z); if (b && isWater(b.typeId)) { b.setType(id); n++; } } catch { /* unloaded */ } };
  for (let t = a - 1; t <= a + len; t++) {
    for (let w = -1; w <= 13; w++) {
      const [x, z] = KIT.cellOf(f, t, w);
      const ring = w === -1 || w === 13 || t === a - 1 || t === a + len;
      if (ring) { if (inPlot(x, z)) continue; for (let y = H - 16; y <= H + 6; y++) cell(x, y, z, DRAIN_FILL); continue; }
      for (let y = H - 15; y <= H + 3; y++) cell(x, y, z, y <= H ? "minecraft:dirt" : "minecraft:air");
    }
  }
  if (n) street.drained = (street.drained || 0) + n;
  return n;
}
/** a plot: water inside the box from the cellar's floor (H - 16) to H + 3 is drained, the ring (1 cell around, H - 16 .. H + 6) sealed */
function plotDrain(dim, b, def, H) {
  const [fx, , fz] = footprint(def, b.rot);
  let n = 0;
  const cell = (x, y, z, id) => { try { const blk = blockAt(dim, x, y, z); if (blk && isWater(blk.typeId)) { blk.setType(id); n++; } } catch { /* unloaded */ } };
  for (let x = b.x - 1; x <= b.x + fx; x++) for (let z = b.z - 1; z <= b.z + fz; z++) {
    const ring = x === b.x - 1 || x === b.x + fx || z === b.z - 1 || z === b.z + fz;
    if (ring) { for (let y = H - 16; y <= H + 6; y++) cell(x, y, z, DRAIN_FILL); continue; }
    for (let y = H - 16; y <= H + 3; y++) cell(x, y, z, y <= H ? "minecraft:dirt" : "minecraft:air");
  }
  if (n) b.drained = (b.drained || 0) + n;
  return n;
}
function floodWatch(dim, st) {
  let drained = 0, sealed = 0;
  // 1.3.224 (the gate's slow days): ONE street a day, every cell of it (was every street every day: ~46k block reads a day
  // in a town — most of the 'economy' step's 800 ms); a flooded street is still found within a few days
  const kits = (st.streets || []).filter((x) => x.kind === "kit" && x.f && Array.isArray(x.H));
  if (!kits.length) return;
  st.floodNext = ((st.floodNext || 0) + 1) % kits.length;
  for (const street of [kits[st.floodNext]]) {
    const t0 = street.tmin, t1 = street.tmin + street.H.length - 1;
    for (let t = t0; t <= t1; t += 1) {
      const H = kitHAt(street, t);
      if (H === undefined) continue;
      for (let w = 0; w <= 12; w++) {
        const [x, z] = KIT.cellOf(street.f, t, w);
        for (let y = H + 1; y <= H + 3; y++) {
          let b; try { b = blockAt(dim, x, y, z); } catch { b = undefined; }
          if (!b || !isWater(b.typeId)) continue;
          b.setType("minecraft:air"); drained++;
          // the source: walk outward on this level from the corridor's edge until the first wet cell beyond the corridor, seal it
          for (const dw of [-1, 1]) {
            for (let k = 1; k <= 6; k++) {
              const [sx, sz] = KIT.cellOf(street.f, t, w + dw * k);
              let sb; try { sb = blockAt(dim, sx, y, sz); } catch { sb = undefined; }
              if (!sb) break;
              if (isWater(sb.typeId) && (w + dw * k < 0 || w + dw * k > 12)) { sb.setType(DRAIN_FILL); sealed++; break; }
            }
          }
        }
      }
    }
  }
  if (drained) { st.flood = { day: load().simDays, drained, sealed }; st.log.push(`day ${load().simDays.toFixed(0)}: flood — ${drained} cells of water drained from the streets, ${sealed} sealed`); }
  return drained;
}

// ------------------------------------------------------------------------------------------------ FLOATING FOLIAGE (1004b, his 17:38)
// "all of the space above towns and villages checked when buildings are built: foliage, leaf blocks or vines that aren't
// attached to a complete tree (contiguously connected to the ground) are removed". A CLUSTER = leaves + vines + logs
// joined face to face; it STANDS when one of its logs rests on ground (or on a log column that does). Clusters are found
// with the engine's own filter (getBlocks includeTypes, #171) one chunk column at a time, inside a runJob; a cluster is
// walked at most SWEEP_CLUSTER cells. Removal drops nothing (the crown was a leftover, not a harvest).
const SWEEP_CLUSTER = 1500, SWEEP_TOP = 48;
const SWEEP_GROUND = new Set(["minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:podzol", "minecraft:mycelium", "minecraft:moss_block",
  "minecraft:mud", "minecraft:rooted_dirt", "minecraft:dirt_with_roots", "minecraft:muddy_mangrove_roots", "minecraft:sand", "minecraft:red_sand", "minecraft:gravel",
  "minecraft:clay", "minecraft:stone", "minecraft:snow", "minecraft:farmland", "minecraft:grass_path", "minecraft:dirt_path", "minecraft:pale_moss_block",
  "minecraft:water", "minecraft:flowing_water", "pw:grass_block", "minecraft:deepslate", "minecraft:andesite", "minecraft:granite", "minecraft:diorite", "minecraft:tuff"]);
const SWEEP_LEAF_IDS = ["pw:oak_leaves", "pw:spruce_leaves", "pw:birch_leaves", "pw:jungle_leaves", "pw:acacia_leaves", "pw:dark_oak_leaves", "pw:mangrove_leaves",
  "pw:cherry_leaves", "pw:pale_oak_leaves", "pw:azalea_leaves", "pw:flowering_azalea_leaves", "minecraft:oak_leaves", "minecraft:spruce_leaves", "minecraft:birch_leaves",
  "minecraft:jungle_leaves", "minecraft:acacia_leaves", "minecraft:dark_oak_leaves", "minecraft:mangrove_leaves", "minecraft:cherry_leaves", "minecraft:pale_oak_leaves",
  "minecraft:azalea_leaves", "minecraft:azalea_leaves_flowered", "minecraft:vine", "pw:vine"];
let _sweepTypes = null;
function sweepTypes() {
  if (!_sweepTypes) _sweepTypes = SWEEP_LEAF_IDS.filter((id) => { try { return !!BlockTypes.get(id); } catch { return false; } });
  return _sweepTypes;
}
const isSweepFoliage = (id) => id.includes("leaves") || id === "minecraft:vine" || id === "pw:vine";
/** sweep one chunk column [cx, cz] (chunk coords) between yLo and yLo + SWEEP_TOP: a generator (yield between clusters) */
function* sweepChunk(dim, cx, cz, yLo, stats) {
  const vol = new BlockVolume({ x: cx * 16, y: yLo, z: cz * 16 }, { x: cx * 16 + 15, y: Math.min(yLo + SWEEP_TOP, 319), z: cz * 16 + 15 });
  let found;
  if (!boxLoaded(dim, cx * 16, cz * 16, cx * 16 + 15, cz * 16 + 15)) return;      // 1.3.228: asked, not thrown
  try { found = dim.getBlocks(vol, { includeTypes: sweepTypes() }, true); } catch { return; }
  const done = new Set();
  const get = (x, y, z) => { try { return blockAt(dim, x, y, z); } catch { return undefined; } };
  for (const loc of found.getBlockLocationIterator()) {
    const k0 = `${loc.x},${loc.y},${loc.z}`;
    if (done.has(k0)) continue;
    // the cluster: leaves + vines + logs, face-connected, bounded
    const cells = [], seen = new Set([k0]), stack = [[loc.x, loc.y, loc.z]];
    let stands = false, logsIn = 0;
    while (stack.length && cells.length < SWEEP_CLUSTER) {
      const [x, y, z] = stack.pop();
      const b = get(x, y, z);
      if (!b) { stands = true; break; }                                  // unloaded: never decide on a half-read cluster
      const id = b.typeId;
      const isLog = TREE_LOG(id) || id.endsWith("_stump");
      if (!isLog && !isSweepFoliage(id)) continue;
      cells.push([x, y, z, isLog]);
      if (isLog) {
        logsIn++;
        const under = get(x, y - 1, z);
        if (under && (SWEEP_GROUND.has(under.typeId) || under.typeId.endsWith("_stump"))) { stands = true; }
      }
      for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]) {
        const k = `${x + dx},${y + dy},${z + dz}`;
        if (!seen.has(k)) { seen.add(k); stack.push([x + dx, y + dy, z + dz]); }
      }
    }
    if (cells.length >= SWEEP_CLUSTER) stands = true;                   // too big to judge: leave it (a forest canopy)
    for (const [x, y, z] of cells) done.add(`${x},${y},${z}`);
    stats.clusters++;
    if (stands) continue;
    let n = 0;
    for (const [x, y, z, isLog] of cells) { if (isLog) continue; const b = get(x, y, z); if (b && isSweepFoliage(b.typeId)) { try { b.setType("minecraft:air"); n++; } catch { /* left */ } } }
    stats.removed += n; stats.orphans++;
    yield;
  }
}
/** sweep a world box [x0..x1] x [z0..z1] above ground level yLo (a generator for system.runJob); logs to the settlement */
function* sweepBoxJob(dim, x0, z0, x1, z1, yLo, st, label) {
  const stats = { clusters: 0, orphans: 0, removed: 0 };
  for (let cx = Math.floor(x0 / 16); cx <= Math.floor(x1 / 16); cx++) for (let cz = Math.floor(z0 / 16); cz <= Math.floor(z1 / 16); cz++) {
    yield* sweepChunk(dim, cx, cz, yLo, stats);
    yield;
  }
  if (st) { st.sweep = { day: load().simDays, ...stats, label }; if (stats.removed) st.log.push(`day ${load().simDays.toFixed(0)}: ${stats.removed} floating leaves cleared (${stats.orphans} crowns, ${label})`); }
}
const sweepJobs = new Map();                                          // settlement id -> running
function sweepBox(dim, st, x0, z0, x1, z1, yLo, label) {
  const key = `${st ? st.id : "w"}:${label}`;
  if (sweepJobs.has(key)) return false;
  sweepJobs.set(key, true);
  const job = sweepBoxJob(dim, x0, z0, x1, z1, yLo, st, label);
  system.runJob((function* () { try { yield* job; } finally { sweepJobs.delete(key); } })());
  return true;
}
/** 1.3.228 (B6 / EN2; his 12:20: "lived-in houses age too; past a bad level the city fines the household and repairs the
 *  house"). A dwelling with people in it ages one band every PLAN.WEATHER.bandDays it stands (b.built, a day, saved): each
 *  new band places its family's weathered overlay (pw:stages/<stem>_w: cracked / mossy stone, mossy cobble) with integrity
 *  0.25 / 0.45 and the building's id as the seed (the same house ages the same way). At the bad level (band 3) the council
 *  FINES the household (the repair's share, purse -> treasury: the ledger's money is unchanged), its people take a mood
 *  knock, and the house is REPAIRED (pw:stages/<stem>_r: the original blocks of those cells), its age starting again.
 *  At most WEATHER_PER_DAY placements a day per town; a house in an unloaded chunk waits. */
const WEATHER_PER_DAY = 3;
function weatherDaily(s, st) {
  const day = Math.floor(s.simDays);
  const dim = world.getDimension(st.dim);
  const P = census(st), L = st.ledger;
  const living = new Map();
  for (const p of PEOPLE.alive(P)) if (p.home) { if (!living.has(p.home)) living.set(p.home, []); living.get(p.home).push(p); }
  let placed = 0;
  for (const b of plotsOf(s, st)) {
    if (placed >= WEATHER_PER_DAY) break;
    if (!(hhOf(b) > 0) || b.stage < 4 || b.closed || !living.has(b.id)) continue;
    const def = BUILDINGS[b.family];
    if (!def) continue;
    if (b.built === undefined) { b.built = day; continue; }
    const band = PLAN.bandOf(day - b.built), cur = b.wx || 0;
    if (band <= cur) continue;
    if (!dim.isChunkLoaded({ x: b.x, y: b.y, z: b.z })) continue;
    if (band >= PLAN.WEATHER.fineBand) {
      const fine = PLAN.fineOf(band, ECON.COIN);
      const paid = L ? Math.min(L.purse, fine) : 0;
      if (L && paid > 0) { L.purse -= paid; L.treasury += paid; }
      const hh = living.get(b.id);
      for (const p of hh) p.mood = Math.max(0, (p.mood ?? 50) - PLAN.WEATHER.mood);
      try { world.structureManager.place(`pw:stages/${def.stem}_r`, dim, { x: b.x, y: b.y, z: b.z }, { rotation: ROTS[b.rot] }); } catch (e) { console.warn(`[CIV-CLOCK] repair #${b.id}: ${e}`); continue; }
      b.built = day; delete b.wx; placed++;
      const who = hh[0] ? `${hh[0].name}'s household` : `the household of #${b.id}`;
      st.log.push(`day ${day}: the council fined ${who} ${(paid / ECON.COIN).toFixed(1)} coins and repaired the ${short(b).replace(/_/g, " ")} #${b.id}`);
      try { PEOPLE.rumour(P, day, "news", `the council fined ${who} and repaired their house`, hh.map((p) => p.id), [b.id]); } catch { /* left */ }
      continue;
    }
    try { world.structureManager.place(`pw:stages/${def.stem}_w`, dim, { x: b.x, y: b.y, z: b.z }, { rotation: ROTS[b.rot], integrity: PLAN.WEATHER.integrity[band], integritySeed: String(b.id) }); }
    catch (e) { console.warn(`[CIV-CLOCK] weather #${b.id}: ${e}`); continue; }
    b.wx = band; placed++;
  }
  if (placed) { const d = diagOf(st); d.weather = { day, placed }; }
}
/** 1.3.230 (HD; his 21:47 "When someone moves out of a home AND/OR into a home, the home must be restored from its current
 *  weathered state to fresh; this makes jobs, spends money and keeps cities updated. And selling of homes replenishes those
 *  costs."): the town's RESTORATION queue st.restore [{h, l}] (homes moved out of / into; the census queues them). Each day
 *  at most PEOPLE.HOUSING.restore.perDay bills start when the ledger can pay (materials from the stock, the builders' wages
 *  treasury -> purse; an empty treasury waits); a started one takes its days (the builders' crew counts it: jobPostsBody);
 *  done, a weathered house gets its fresh blocks back (EN2's pw:stages/<stem>_r) and its age starts again (b.built = today,
 *  b.wx gone). A house in an unloaded chunk finishes on a later day; a plot no longer a standing dwelling leaves the queue. */
function restoreDaily(s, st) {
  const Q = st.restore;
  if (!Q || !Q.length) return;
  const L = st.ledger, day = Math.floor(s.simDays);
  const dim = world.getDimension(st.dim);
  const home = (id) => { const b = buildingById(s, id); return b && b.settlement === st.id && (hhOf(b) || 0) > 0 && b.stage >= 4 && !b.closed ? b : null; };
  const r = PEOPLE.restoreDay(L, Q, { ok: (id) => !!home(id), lvl: (id) => PEOPLE.homeLevel(short(home(id))) || 1, band: (id) => home(id).wx || 0 });
  for (const e of r.started) { const b = home(e.h); if (b) st.log.push(`day ${day}: the builders began restoring the ${short(b).replace(/_/g, " ")} #${b.id} (${e.days} day${e.days > 1 ? "s" : ""}; ${(e.wages / ECON.COIN).toFixed(1)} coins wages${e.mats.stone ? `, ${e.mats.stone} stone` : ""}, ${e.mats.planks || 0} planks)`); }
  for (const id of r.done) {
    const b = home(id);
    if (!b) continue;
    const def = BUILDINGS[b.family];
    if ((b.wx || 0) > 0 && def) {
      if (!dim.isChunkLoaded({ x: b.x, y: b.y, z: b.z })) { Q.push({ h: id, l: 1 }); continue; }   // finishes when its chunk is loaded
      try { world.structureManager.place(`pw:stages/${def.stem}_r`, dim, { x: b.x, y: b.y, z: b.z }, { rotation: ROTS[b.rot] }); }
      catch (e) { console.warn(`[CIV-CLOCK] restore #${b.id}: ${e}`); continue; }   // no endless retry: EN2's own repair still comes at the bad band
    }
    b.built = day; delete b.wx;
    st.log.push(`day ${day}: the ${short(b).replace(/_/g, " ")} #${b.id} is restored, fresh for its household`);
  }
  if (r.started.length || r.done.length || r.dropped) { const d = diagOf(st); d.restore = { day, started: r.started.length, done: r.done.length, waiting: r.waiting, dropped: r.dropped, queue: Q.length, spent: r.spent }; }
  if (!Q.length) delete st.restore;
}
/** 1.3.228 (B9 / GB6): the town's TITLE from its spirit (the standing buildings' points), once a day; a change is told */
function titleDaily(s, st, events) {
  const counts = {};
  for (const b of plotsOf(s, st)) if (b.stage >= 4 && !b.closed) counts[short(b)] = (counts[short(b)] || 0) + 1;
  if (st.docks || (st.fisherySpots || []).length) counts.fishery = (counts.fishery || 0) + Math.max(1, (st.fisherySpots || []).length);
  const t = NAMES_.titleOf(NAMES_.spiritOf(counts));
  const title = t ? t.title : null;
  if ((st.title || null) === title) return;
  if (title) { st.title = title; st.log.push(`day ${Math.floor(s.simDays)}: ${st.name} is known now as a ${title}`); annal(st, s.simDays, `known now as a ${title}`); if (events) events.push(`§b${st.name}: known now as a ${title}`); }
  else delete st.title;
}
/** 1.3.228 (B6 / GB13 — his 12:20 "Gardens: fillers only (well, cart, lamp) — no frontage left empty"): every gap of a
 *  kit street side between its lots (or a stretch's end beside a lot) too short for a house gets a small FILLER at the
 *  corridor's edge — a well (3 wide), a bench (2), a cart (2) or a lamp post (1), chosen by PLAN.fillerFor (deterministic by
 *  the gap's start). Placed by blocks, only onto solid ground with 3 blocks of air above; at most FILLER_MAX a town a day;
 *  st.fillers remembers each gap ("-" = refused for good). A street side with no house yet waits for houses. */
const FILLER_MAX = 4;
function fillersDaily(s, st) {
  const dim = world.getDimension(st.dim);
  const minLot = ((BUILDINGS[familyOf("cottage_s", "a")] || {}).size || [0, 0, 9])[2];
  st.fillers = st.fillers || {};
  let placed = 0;
  const lots = plotsOf(s, st).filter((b) => b.kit && b.kit.sid !== null && b.kit.sid !== undefined && !b.closed);
  for (const street of st.streets.filter((x) => x.kind === "kit" && x.H)) {
    const { bySide } = kitStretches(street, st);
    for (const side of [1, -1]) {
      const occ = lots.filter((b) => b.kit.sid === street.id && b.kit.side === side).map((b) => [b.kit.at, b.kit.at + b.kit.len - 1]).sort((a, b) => a[0] - b[0]);
      if (!occ.length) continue;
      for (const sx of bySide[String(side)] || []) {
        const gaps = [];
        let cur = sx.a;
        for (const [a, b] of occ) { if (b < sx.a || a > sx.b) continue; if (a - 1 >= cur) gaps.push([cur, a - 1]); cur = Math.max(cur, b + 1); }
        if (cur <= sx.b && cur > sx.a) gaps.push([cur, sx.b]);
        for (const [g0, g1] of gaps) {
          const key = `${street.id}:${side}:${g0}`;
          if (st.fillers[key]) continue;
          const kind = PLAN.fillerFor(g0, g1 + 1, minLot, street.id);
          if (!kind) continue;
          if (placed >= FILLER_MAX) return;
          const t0 = Math.floor((g0 + g1 + 1) / 2 - PLAN.FILLER_W[kind] / 2);
          const ok = placeFiller(dim, street, side, t0, kind);
          if (ok === null) continue;                                     // unloaded: another day
          st.fillers[key] = ok ? kind : "-";
          if (ok) { placed++; diagOf(st).fillers = (diagOf(st).fillers || 0) + 1; }
        }
      }
    }
  }
}
/** one filler: true placed, false refused (ground / headroom), null not loaded */
function placeFiller(dim, street, side, t0, kind) {
  const w = PLAN.FILLER_W[kind], deep = kind === "well" ? 3 : 1;
  const wAt = (j) => (side > 0 ? KIT.W + j : -1 - j);
  const cells = [];
  for (let i = 0; i < w; i++) for (let j = 0; j < deep; j++) {
    const t = t0 + i;
    if (t < street.tmin || t >= street.tmin + street.H.length) return false;
    const [x, z] = KIT.cellOf(street.f, t, wAt(j));
    cells.push({ i, j, x, z, H: kitHAt(street, t) });
  }
  const H = Math.max(...cells.map((c) => c.H));
  for (const c of cells) {
    const g = blockAt(dim, c.x, H, c.z);
    if (g === null) return null;
    if (!g || g.isAir || g.isLiquid) return false;
    for (let y = H + 1; y <= H + 3; y++) { const a = blockAt(dim, c.x, y, c.z); if (a === null) return null; if (!a || !a.isAir) return false; }
  }
  const put = (x, y, z, name, states = {}) => { try { dim.getBlock({ x, y, z })?.setPermutation(BlockPermutation.resolve(name, states)); } catch (e) { console.warn(`[CIV-FILL] ${name}: ${e}`); } };
  const toStreet = side > 0 ? [-street.f.vx, -street.f.vz] : [street.f.vx, street.f.vz];
  const card = toStreet[0] > 0 ? "east" : toStreet[0] < 0 ? "west" : toStreet[1] > 0 ? "south" : "north";
  if (kind === "lamp") { const c = cells[0]; put(c.x, H + 1, c.z, "minecraft:spruce_fence"); put(c.x, H + 2, c.z, "minecraft:spruce_fence"); put(c.x, H + 3, c.z, "minecraft:lantern", { hanging: false }); }
  else if (kind === "bench") { for (const c of cells) put(c.x, H + 1, c.z, "pw:furn_bench_spruce", { "minecraft:cardinal_direction": card }); }
  else if (kind === "cart") { put(cells[0].x, H + 1, cells[0].z, "minecraft:hay_block"); put(cells[1].x, H + 1, cells[1].z, "minecraft:barrel", { facing_direction: 1, open_bit: false }); }
  else if (kind === "well") {
    for (const c of cells) {
      const corner = (c.i === 0 || c.i === 2) && (c.j === 0 || c.j === 2), mid = c.i === 1 && c.j === 1;
      if (mid) put(c.x, H, c.z, "minecraft:water", { liquid_depth: 0 });
      else put(c.x, H + 1, c.z, "minecraft:cobblestone");
      if (corner) { put(c.x, H + 2, c.z, "minecraft:spruce_fence"); put(c.x, H + 3, c.z, "minecraft:spruce_fence"); }
      put(c.x, H + 4, c.z, "minecraft:spruce_slab", { "minecraft:vertical_half": "bottom" });
    }
  }
  return true;
}
/** 1.3.229 ROLE BEDS (his 14:07 + answers): the palace's beds go to the roles they belong to — the lord's bed and the
 *  apartments of state to the town's top couples (one representative household per district first), the guard rooms to
 *  single watchmen, the clerks' lodgings to single surveyors / clerks, the servants' quarters to the town's most skilled
 *  single cooks and tradesmen. Reserved until a role is filled; a member who is no longer eligible goes back to the home he
 *  came from. pw_civ_court.js decides; this applies it once a census day (deferDay "court"). */
function courtDaily(s, st) {
  const pieces = s.buildings.filter((b) => b.palace && b.settlement === st.id && b.stage >= 4 && !b.closed).map((b) => ({ id: b.id, q: b.palace.q }));
  const P = census(st);
  if (!pieces.length && !PEOPLE.alive(P).some((p) => p.court)) return;
  const day = Math.floor(s.simDays);
  const byId = new Map(s.buildings.map((b) => [b.id, b]));
  const dCache = new Map();
  const f = {
    stage: (p) => PEOPLE.stage(p, day), household: (p) => PEOPLE.household(P, p, day), tradeOf: (p) => p.trade,
    dead: (id) => { const q = PEOPLE.byId(P, id); return !q || !q.alive; },
    homeKind: (p) => { const b = byId.get(p.home); return b ? short(b) : null; },
    districtOf: (p) => {
      const b = byId.get(p.home);
      if (!b) return null;
      if (!dCache.has(b.id)) { let d = null; try { const r = districtAt(st, b.x, b.z); d = r ? r.sid : null; } catch { /* no streets */ } dCache.set(b.id, d); }
      return dCache.get(b.id);
    },
  };
  const plan = COURT.courtPlan(pieces, P.list, f);
  if (!plan.release.length && !plan.admit.length) { st.court = { held: plan.held, free: plan.free }; return; }
  const homeOk = (id) => { const b = byId.get(id); return !!b && !b.closed && (hhOf(b) > 0 || b.keeper !== undefined); };
  const res = COURT.applyCourt(plan, P, PEOPLE.byId, homeOk);
  st.court = { held: plan.held, free: plan.free };
  const heads = new Map();
  for (const a of plan.admit) if (a.head === a.pid) heads.set(a.pid, a);
  for (const a of heads.values()) {
    const p = PEOPLE.byId(P, a.pid);
    if (!p) continue;
    const text = a.r === "lord" ? `${p.name}'s household moved into the palace — the lord's bedchamber` : a.r === "noble" ? `${p.name}'s household took an apartment of state at the palace${a.d !== undefined ? ` (for ${st.names && st.names[a.d] ? st.names[a.d] : "its district"})` : ""}`
      : `${p.name} moved into ${COURT.ROLE_NAME[a.r]} at the palace`;
    st.log.push(`day ${day}: ${text}`);
    if (a.r === "lord" || a.r === "noble") annal(st, s.simDays, text);
  }
  if (res.released) st.log.push(`day ${day}: ${res.released} left the palace (no longer in their post or household)`);
  console.warn(`[CIV-COURT] ${JSON.stringify({ st: st.id, day, admitted: res.admitted, released: res.released, held: plan.held, free: plan.free })}`);
}
/** 1.3.228 (B10 / WP7): the town's ANNALS — its milestones (tiers, titles, firsts, ranks, the bell) kept for the Chronicle
 *  button; at most ANNALS_MAX (the oldest fall off; the founding line is kept) */
const ANNALS_MAX = 40;
function annal(st, day, text) {
  st.annals = st.annals || [];
  st.annals.push(`day ${Math.floor(day)}: ${text}`);
  if (st.annals.length > ANNALS_MAX) st.annals.splice(1, st.annals.length - ANNALS_MAX);
}
/** the Chronicle's text: the annals, then the last 20 lines of the town's log */
function chronicleOf(st) {
  const a = (st.annals || []).slice(-ANNALS_MAX), log = (st.log || []).slice(-20);
  return `${st.title ? `${st.name}, a ${st.title}` : st.name}\n\n§lAnnals§r\n${a.join("\n") || "(nothing yet)"}\n\n§lLately§r\n${log.join("\n") || "(quiet)"}`;
}
/** 1.3.228 (B9 / TR10): the district (kit street) a point stands on — the nearest street whose corridor lies within 20 cells;
 *  its name is given once (unique in the town, saved in st.names) */
function districtAt(st, x, z) {
  let best = null, bd = 21;
  for (const street of st.streets || []) {
    if (street.kind !== "kit" || !street.H || !street.f) continue;
    const [t, w] = KIT.tw(street.f, x, z);
    if (t < street.tmin - 2 || t > street.tmin + street.H.length + 2) continue;
    const d = w < 0 ? -w : w > 12 ? w - 12 : 0;
    if (d < bd) { bd = d; best = street; }
  }
  if (!best) return null;
  st.names = st.names || {};
  if (!st.names[best.id]) { st.names[best.id] = NAMES_.streetName(best.id, best.bench ? "bench" : best.role || "side", new Set(Object.values(st.names)), st.seed || 1); save(); }
  return { sid: best.id, name: st.names[best.id] };
}
/** the zone beat (slot 9 every 20 ticks; optional): "Now entering <Town> · <District>" on the actionbar when a player's
 *  district changes; a title on entering the town. Memory: ZONES (player id -> "st:sid") */
const ZONES = new Map();
HB.register("zone", { every: 20, slot: 9, budgetMs: 3, optional: true, fn: () => {
  let players; try { players = world.getPlayers(); } catch { return; }
  if (!players.length) return;
  const s = load();
  for (const pl of players) {
    const loc = pl.location;
    const st = s.settlements.find((x) => x.dim === pl.dimension.id && x.square && inInfluence(x, loc.x, loc.z));
    const prev = ZONES.get(pl.id) || "";
    if (!st) { if (prev) ZONES.delete(pl.id); continue; }
    const d = districtAt(st, Math.floor(loc.x), Math.floor(loc.z));
    const key = `${st.id}:${d ? d.sid : "-"}`;
    if (key === prev) continue;
    ZONES.set(pl.id, key);
    try {
      if (!prev.startsWith(`${st.id}:`)) pl.onScreenDisplay.setTitle(`§6${st.name}`, { subtitle: `${st.title ? `${st.title} · ` : ""}${tierLabel(st)}`, fadeInDuration: 10, stayDuration: 50, fadeOutDuration: 20 });
      pl.onScreenDisplay.setActionBar(`§7Now entering §f${st.name}${d ? ` §7· §f${d.name}` : ""}`);
    } catch { /* left */ }
  }
} });
/** 1.3.228 (B6 / GB14): the street HEADROOM — one kit street a day (round-robin, a job): leaves or tree logs inside the
 *  corridor (w 0..12) from H + 1 to H + 4 are cleared (clearing, not felling: BIGCANOPY's fell rules are untouched; a log
 *  inside a building's box is never touched; the placed-log ledger's logs neither — touchesPlacedLog) */
const headroomJobs = new Set();
function headroomDaily(dim, st) {
  const streets = (st.streets || []).filter((x) => x.kind === "kit" && x.H && x.H.length);
  if (!streets.length || headroomJobs.has(st.id)) return;
  const street = streets[(st.headTile || 0) % streets.length];
  st.headTile = ((st.headTile || 0) + 1) % streets.length;
  headroomJobs.add(st.id);
  const vols = [];                                                         // the building volumes beside this street
  for (const b of load().buildings) { const def = BUILDINGS[b.family]; if (!def || b.settlement !== st.id) continue; const [bx0, bx1, bz0, bz1] = boxOf(b, 0); vols.push([bx0, bx1, b.y, b.y + def.size[1] - 1, bz0, bz1]); }
  const inVol = (x, y, z) => vols.some(([a, b2, c, d, e, f]) => x >= a && x <= b2 && y >= c && y <= d && z >= e && z <= f);
  const job = (function* () {
    let cleared = 0, reads = 0;
    try {
      for (let i = 0; i < street.H.length; i++) {
        const t = street.tmin + i, H = street.H[i];
        for (let w = 0; w <= 12; w++) {
          const [x, z] = KIT.cellOf(street.f, t, w);
          for (let y = H + 1; y <= H + 4; y++) {
            if (++reads % 150 === 0) yield;
            const blk = blockAt(dim, x, y, z);
            if (!blk) continue;
            const id = blk.typeId;
            if (!(isTreeLeafId(id) || isTreeLogId(id))) continue;
            if (isTreeLogId(id) && (inVol(x, y, z) || touchesPlacedLog([{ x, y, z }]))) continue;
            try { blk.setType("minecraft:air"); cleared++; } catch { /* left */ }
          }
        }
      }
    } finally {
      headroomJobs.delete(st.id);
      if (cleared) st.log.push(`day ${load().simDays.toFixed(0)}: ${cleared} leaves / logs cleared over street #${street.id}`);
    }
  })();
  try { system.runJob(job); } catch (e) { headroomJobs.delete(st.id); console.warn(`[CIV-CLOCK] headroom job: ${e}`); }
}
/** the daily sweep: one 4 x 4-chunk tile of the influence square per call, round-robin (st.sweepTile) */
function sweepDaily(dim, st) {
  if (!st.square) return;
  const r = (st.border && st.border.r) || INFLUENCE[st.tier] || 64;
  const x0 = st.square.x + 6 - r, z0 = st.square.z + 6 - r, x1 = st.square.x + 6 + r, z1 = st.square.z + 6 + r;
  const tiles = Math.ceil((x1 - x0 + 1) / 64) * Math.ceil((z1 - z0 + 1) / 64);
  const i = (st.sweepTile || 0) % tiles, nz = Math.ceil((z1 - z0 + 1) / 64);
  const tx = Math.floor(i / nz), tz = i % nz;
  st.sweepTile = i + 1;
  const sx0 = x0 + tx * 64, sz0 = z0 + tz * 64;
  sweepBox(dim, st, sx0, sz0, Math.min(x1, sx0 + 63), Math.min(z1, sz0 + 63), (st.square.y || 64) - 8, `tile ${i + 1}/${tiles}`);
}

// ------------------------------------------------------------------------------------------------ the bare trunks (his 00:54, 10-06)
// "The towns were clearing leaf blocks, but not the actual tree logs, so we had long — very long — logs/stumps shooting up
// into the air. Make sure if a tree exists in town, and has fewer than 30% of its original canopy leaf blocks, the village
// will remove the rest." Mechanism: a plot's template air and the street clearing cut the crowns of trees beside them and
// the leaf sweep removes the floating clumps; the trunks stayed. Now, one tile of the influence square a day (round-robin,
// a job): every tree is measured against its ORIGINAL crown — a structure tree (pw root) against its template's leaves,
// exactly; a rootless tree against an expected crown (its logs x a species ratio). Below CANOPY_KEEP the village takes
// the rest down (leaves, then logs from the top) and the wood goes to the town's timber. Never: logs inside a building's
// volume, a tree with a player-placed log (the placed-log ledger), a tree reaching into an unloaded chunk.
const CANOPY_KEEP = 0.30;
// leaves per log of a whole crown, set LOW on purpose (a healthy tree must never read as bare; the bare trunks read ~0 %)
const CANOPY_RATIO = [[/spruce|pine|fir/, 5], [/birch/, 8], [/jungle/, 5], [/acacia/, 7], [/dark_oak|pale_oak/, 6], [/cherry/, 10], [/mangrove/, 5], [/./, 8]];
const canopyJobs = new Set();
let treeLogTypesOk = null;
function treeLogTypes() {
  if (treeLogTypesOk) return treeLogTypesOk;
  try { treeLogTypesOk = BlockTypes.getAll().map((b) => b.id).filter((id) => isTreeLogId(id) && !id.startsWith("minecraft:stripped_")); } catch { treeLogTypesOk = []; }
  return treeLogTypesOk;
}
function canopyDaily(dim, st) {
  if (!st.square) return;
  const r = (st.border && st.border.r) || INFLUENCE[st.tier] || 64;
  const x0 = st.square.x + 6 - r, z0 = st.square.z + 6 - r, x1 = st.square.x + 6 + r, z1 = st.square.z + 6 + r;
  const nz = Math.ceil((z1 - z0 + 1) / 64), tiles = Math.ceil((x1 - x0 + 1) / 64) * nz;
  const i = (st.canopyTile || 0) % tiles;
  st.canopyTile = i + 1;
  const sx0 = x0 + Math.floor(i / nz) * 64, sz0 = z0 + (i % nz) * 64;
  if (canopyJobs.has(st.id)) return;
  canopyJobs.add(st.id);
  const gen = canopyJob(dim, st, sx0, sz0, Math.min(x1, sx0 + 63), Math.min(z1, sz0 + 63));
  try { system.runJob((function* () { try { yield* gen; } finally { canopyJobs.delete(st.id); } })()); } catch (e) { canopyJobs.delete(st.id); console.warn(`[CIV-CLOCK] canopy job: ${e}`); }
}
/** the measure of one tree from any of its logs: { logs, leaves (present), original, kind } or null (unknown / not a tree) */
export function canopyOf(dim, start, inBuilding, seenLogs) {
  const get = (x, y, z) => { const b = blockAt(dim, x, y, z); return b === undefined ? undefined : b; };   // null = unloaded (1.3.227: no throwing read)
  const logs = [], q = [start], seen = new Set();
  let unknown = false;
  while (q.length && logs.length < 400) {
    const [x, y, z] = q.pop();
    const k = `${x},${y},${z}`;
    if (seen.has(k)) continue;
    seen.add(k);
    if (Math.abs(x - start[0]) > 7 || Math.abs(z - start[2]) > 7 || y - start[1] > 40 || start[1] - y > 40) continue;
    if (inBuilding(x, y, z)) continue;
    const b = get(x, y, z);
    if (b === null) { unknown = true; continue; }
    if (!b || !isTreeLogId(b.typeId)) continue;
    logs.push([x, y, z, b.typeId, b]);
    seenLogs.add(k);
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) if (dx || dy || dz) q.push([x + dx, y + dy, z + dz]);
  }
  if (!logs.length || unknown) return null;
  if (touchesPlacedLog(logs.map(([x, y, z]) => ({ x, y, z })))) return null;           // someone built with these logs
  const base = logs.reduce((a, l) => (l[1] < a[1] ? l : a), logs[0]);
  // a structure tree: its root measures the crown exactly against the template
  if (base[3].startsWith("pw:") && base[3].endsWith("_root")) {
    const rb = base[4];
    let cells = null, dir = "north";
    try {
      const tpl = (rb.permutation.getState("pw:tpl") ?? 0) + 16 * (rb.permutation.getState("pw:tpl_hi") ?? 0);
      dir = rb.permutation.getState("minecraft:cardinal_direction") || "north";
      cells = templateCells(templateName(base[3], tpl));
    } catch { cells = null; }
    if (cells && cells.leaves.length) {
      const leaves = [];
      for (const c of cells.leaves) {
        const [ox, oz] = turnOffset(c[0], c[2], dir);
        const p = [base[0] + ox, base[1] + c[1], base[2] + oz];
        const b = get(p[0], p[1], p[2]);
        if (b === null) return null;
        if (b && isTreeLeafId(b.typeId)) leaves.push(p);
      }
      return { logs, leaves, original: cells.leaves.length, kind: "template" };
    }
  }
  // rootless: the crown is the leaves within LEAF_REACH face-steps of the logs; the original crown is estimated
  const leaves = [], lseen = new Set(logs.map(([x, y, z]) => `${x},${y},${z}`));
  let frontier = logs.map(([x, y, z]) => [x, y, z]);
  for (let step = 0; step < LEAF_REACH && frontier.length && leaves.length < FELL_MAX_LEAVES; step++) {
    const next = [];
    for (const [cx, cy, cz] of frontier) for (const [dx, dy, dz] of [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]) {
      const p = [cx + dx, cy + dy, cz + dz], k = p.join(",");
      if (lseen.has(k)) continue;
      lseen.add(k);
      const b = get(p[0], p[1], p[2]);
      if (b === null) return null;
      if (!b || !isTreeLeafId(b.typeId)) continue;
      leaves.push(p); next.push(p);
    }
    frontier = next;
  }
  const ratio = (CANOPY_RATIO.find(([re]) => re.test(base[3])) || [null, 12])[1];
  return { logs, leaves, original: Math.max(20, logs.length * ratio), kind: "estimated" };
}
function* canopyJob(dim, st, x0, z0, x1, z1) {
  const s = load();
  // the building volumes in (and beside) this tile: a template's logs are never a tree
  const vols = [];
  for (const b of s.buildings) {
    const def = BUILDINGS[b.family];
    if (!def) continue;
    const [bx0, bx1, bz0, bz1] = boxOf(b, 0);
    if (bx1 < x0 - 8 || bx0 > x1 + 8 || bz1 < z0 - 8 || bz0 > z1 + 8) continue;
    vols.push([bx0, bx1, b.y, b.y + def.size[1] - 1, bz0, bz1]);
  }
  const inBuilding = (x, y, z) => vols.some(([a, b2, c, d, e, f]) => x >= a && x <= b2 && y >= c && y <= d && z >= e && z <= f);
  const types = treeLogTypes();
  if (!types.length) return;
  const yLo = (st.square.y || 64) - 12, yHi = (st.square.y || 64) + 60;
  const seenLogs = new Set();
  let trees = 0, logsCut = 0, leavesCut = 0, measured = 0;
  for (let bx = x0; bx <= x1; bx += 16) for (let bz = z0; bz <= z1; bz += 16) {
    const locs = [];
    if (!boxLoaded(dim, bx, bz, Math.min(bx + 15, x1), Math.min(bz + 15, z1))) { yield; continue; }   // 1.3.228: asked, not thrown
    try {
      const vol = new BlockVolume({ x: bx, y: yLo, z: bz }, { x: Math.min(bx + 15, x1), y: yHi, z: Math.min(bz + 15, z1) });
      for (const l of dim.getBlocks(vol, { includeTypes: types }, true).getBlockLocationIterator()) locs.push(l);
    } catch { yield; continue; }
    for (const l of locs) {
      if (seenLogs.has(`${l.x},${l.y},${l.z}`) || inBuilding(l.x, l.y, l.z)) continue;
      const tree = canopyOf(dim, [l.x, l.y, l.z], inBuilding, seenLogs);
      yield;
      if (!tree) continue;
      measured++;
      if (tree.leaves.length >= CANOPY_KEEP * tree.original) continue;
      for (const [x, y, z] of tree.leaves) { try { const b = blockAt(dim, x, y, z); if (b && isTreeLeafId(b.typeId)) { b.setType("minecraft:air"); leavesCut++; } } catch { /* left */ } }
      for (const [x, y, z] of tree.logs.sort((p, q2) => q2[1] - p[1])) { try { const b = blockAt(dim, x, y, z); if (b && isTreeLogId(b.typeId)) { b.setType("minecraft:air"); logsCut++; } } catch { /* left */ } }
      trees++;
      yield;
    }
    yield;
  }
  st.canopyMeasured = (st.canopyMeasured || 0) + measured;
  if (trees) {
    const s2 = load(), st2 = s2.settlements.find((x) => x.id === st.id) || st;
    st2.barkCut = (st2.barkCut || 0) + trees;
    if (st2.ledger) st2.ledger.stock.timber += logsCut;
    st2.log.push(`day ${s2.simDays.toFixed(0)}: the villagers took down ${trees} bare tree${trees === 1 ? "" : "s"} (under ${Math.round(CANOPY_KEEP * 100)} % of the crown left: ${logsCut} logs to the timber stack, ${leavesCut} leaves)`);
    save();
  }
}

/** the LUMBERYARD clearing: fell the trees within radius 10 + 6 per tier around the yard (at most N per pass) */
function clearForest(dim, b, st, tierIdx, maxTrees = 12) {
  const def = BUILDINGS[b.family];
  const [fx, , fz] = footprint(def, b.rot);
  const cx = b.x + (fx >> 1), cz = b.z + (fz >> 1), R = 10 + 6 * tierIdx;
  let trees = 0, logs = 0;
  const starts = [];
  const occupied = occupiedTest(load(), st);
  for (let x = cx - R; x <= cx + R && starts.length < 400; x += 2) for (let z = cz - R; z <= cz + R; z += 2) {
    if (occupied(x, z)) continue;                                                            // not the yard, no plot, no street
    try {
      const g = groundAt(dim, x, z);
      if (g === undefined) continue;
      for (let y = g + 1; y <= g + 2; y++) { const blk = blockAt(dim, x, y, z); if (blk && TREE_LOG(blk.typeId) && !blk.typeId.endsWith("_stump")) { starts.push([x, y, z]); break; } }
    } catch { /* unloaded */ }
  }
  for (const [x, y, z] of starts) {
    if (trees >= maxTrees) break;
    if (WORKMOD.claimHeld(x, z)) continue;                                                   // 1.3.228 (B2 / BF10): a hand's tree
    if (!treeOk(dim, x, y, z, occupied)) continue;                                           // only a real tree (R3/R4/R5)
    const n = fellTree(dim, x, y, z, occupied);
    if (n) { trees++; logs += n; }
  }
  b.felled = (b.felled || 0) + trees;
  return { trees, logs };
}

/** the FIELDS: harvest ripe wheat inside a farm's box (growth 7 -> 0); grain = the wheat actually grown */
function harvestFarm(dim, b, st) {
  const def = BUILDINGS[b.family];
  const [fx, sy, fz] = footprint(def, b.rot);
  let n = 0;
  const y0 = b.y + def.datum_y - 1, y1 = y0 + 3;
  for (let i = 0; i < fx; i++) for (let j = 0; j < fz; j++) for (let y = y0; y <= y1; y++) {
    try {
      const blk = blockAt(dim, b.x + i, y, b.z + j);
      if (blk && blk.typeId === "minecraft:wheat" && blk.permutation.getState("growth") === 7) { blk.setPermutation(blk.permutation.withState("growth", 0)); n++; }
    } catch { /* unloaded */ }
  }
  if (n && st.ledger) st.ledger.stock.grain += n;                 // the fields' real wheat is a bonus over the farm's rate
  b.harvested = (b.harvested || 0) + n;
  return n;
}

/** the streets harden with use: path -> gravel (village2) -> cobblestone (town+) */
function hardenStreets(dim, st, tierIdx) {
  const surface = tierIdx >= 3 ? "minecraft:cobblestone" : tierIdx >= 1 ? "minecraft:gravel" : null;
  if (!surface || !st.profile) return 0;
  let n = 0;
  for (const [key, h] of LAND.streetBody(st.profile, st.axis || "x")) {
    const [x, z] = key.split(",").map(Number);
    try { const blk = blockAt(dim, x, h, z); if (blk && (blk.typeId === "minecraft:grass_path" || blk.typeId === "minecraft:gravel")) { blk.setType(surface); n++; } } catch { /* unloaded */ }
  }
  return n;
}

/** the CITY WALL (step 6): stone bricks 4 high with a crenellated top along the ground around the built extent (6 out),
 *  gates (3 wide) where a street's profile crosses the line; follows the ground. */
function buildWall(dim, s, st) {
  const plots = plotsOf(s, st);
  if (!plots.length) return 0;
  let x0 = 1e9, x1 = -1e9, z0 = 1e9, z1 = -1e9;
  for (const b of plots) { const [bx0, bx1, bz0, bz1] = boxOf(b); x0 = Math.min(x0, bx0); x1 = Math.max(x1, bx1); z0 = Math.min(z0, bz0); z1 = Math.max(z1, bz1); }
  x0 -= 6; x1 += 6; z0 -= 6; z1 += 6;
  const streetCells = new Set(bodyOf(st).keys());
  const gate = (x, z) => { for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++) if (streetCells.has(`${x + dx},${z + dz}`)) return true; return false; };
  const line = [];
  for (let x = x0; x <= x1; x++) { line.push([x, z0]); line.push([x, z1]); }
  for (let z = z0 + 1; z < z1; z++) { line.push([x0, z]); line.push([x1, z]); }
  // never through another settlement's plots or streets (run 0.0.11: the daughter's wall cut the mother's bakery)
  const ownKeys = new Set(plots.map((b) => boxOf(b, 2).join(",")));
  const foreignBoxes = plotBoxes(s, 2, null).filter((bx) => !ownKeys.has(bx.join(",")));
  const foreignStreets = new Map([...streetHeights(s)].filter(([k]) => !streetCells.has(k)));
  const foreign = (x, z) => foreignStreets.has(`${x},${z}`) || foreignBoxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  let n = 0, k = 0;
  for (const [x, z] of line) {
    k++;
    try {
      const g = groundAt(dim, x, z);
      if (g === undefined || gate(x, z) || foreign(x, z)) continue;
      const top = g + 4 + (k % 2 ? 1 : 0);
      for (let y = g + 1; y <= top; y++) { const blk = dim.getBlock({ x, y, z }); if (blk) { blk.setType(y === top && k % 2 ? "minecraft:stone_bricks" : "minecraft:stone_bricks"); n++; } }
    } catch { /* unloaded */ }
  }
  st.wall = { x0, x1, z0, z1, blocks: n };
  return n;
}

/** DOCKS (step 5): if water lies within 40 of the square, a plank pier on fence posts runs 8 cells into it from the
 *  shore, with a barrel (the fisherman's post) and a boat at its end. */
function buildDocks(dim, st, site) {
  if (!site || !st.square || st.docks) return false;
  const sx = st.square.x + 6, sz = st.square.z + 6;
  let shore = null;
  for (let r = 6; r <= 40 && !shore; r++) {
    for (let a = 0; a < 16 && !shore; a++) {
      const ang = (a / 16) * Math.PI * 2;
      const x = Math.round(sx + Math.cos(ang) * r), z = Math.round(sz + Math.sin(ang) * r);
      if (site.isWater(x, z)) {
        // walk back toward the square to the last land cell
        const dx = Math.sign(sx - x), dz = Math.sign(sz - z);
        let lx = x, lz = z;
        for (let k = 0; k < 40 && site.isWater(lx, lz); k++) { if (Math.abs(sx - lx) > Math.abs(sz - lz)) lx += dx; else lz += dz; }
        shore = { x: lx, z: lz, dx: Math.sign(x - lx), dz: Math.sign(z - lz) };
      }
    }
  }
  if (!shore) return false;
  const wy = (site.at(shore.x + shore.dx, shore.z + shore.dz) ?? site.at(shore.x, shore.z) ?? 62);
  const deck = (site.at(shore.x, shore.z) ?? wy) + 1;
  let n = 0;
  try {
    for (let k = 0; k <= 8; k++) {
      const x = shore.x + shore.dx * k, z = shore.z + shore.dz * k;
      for (let y = wy; y < deck; y++) if (k % 3 === 0) dim.getBlock({ x, y, z })?.setType("minecraft:spruce_fence");
      dim.getBlock({ x, y: deck, z })?.setType("minecraft:spruce_planks");
      dim.getBlock({ x: x + shore.dz, y: deck, z: z + shore.dx })?.setType("minecraft:spruce_planks");   // 2 wide
      n++;
    }
    const ex = shore.x + shore.dx * 8, ez = shore.z + shore.dz * 8;
    dim.getBlock({ x: ex, y: deck + 1, z: ez })?.setType("minecraft:barrel");
    dim.spawnEntity("minecraft:boat", { x: ex + shore.dx * 2 + 0.5, y: wy + 1, z: ez + shore.dz * 2 + 0.5 });
  } catch (e) { console.warn(`[CIV-CLOCK] docks: ${e}`); }
  st.docks = { x: shore.x, z: shore.z, cells: n };
  st.log.push(`day ${load().simDays.toFixed(0)}: a pier built at the water (${shore.x} ${shore.z})`);
  return true;
}

// ------------------------------------------------------------------------------------------------ between settlements (step 7)
// A prosperous town founds a DAUGHTER: a site 120-200 blocks away is chosen by the land (the daughter's own site read),
// a ROAD is walked from square to square over the real ground (greedy, slope-costed, water avoided; laid like a street:
// profile smoothed, path surface, steps, bridges over gullies, causeways over shallows), and the two ledgers TRADE along it
// every day (goods move from the cheaper town to the dearer one when the gap pays the haulage; prices converge — the
// economy draft §1.2). ASSUMPTION (his 20:04): thresholds below; wagons as entities wait for V4b.
const DAUGHTER_POP = 24, DAUGHTER_PROS = 0.9, DAUGHTER_DAYS = 30, DAUGHTER_DIST = [170, 230];   // >= 2 x SITE_R + 10: two site fields never overlap (run 0.0.11: streets interleaved, the wall hit the mother)

function maybeFoundDaughter(s, st, events) {
  if (!st.ledger || TIER_CLASS(st.tier) < 1 || population(s, st) < DAUGHTER_POP) return;
  st.daughters = st.daughters || (st.daughter && st.daughter.id ? [st.daughter.id] : []);
  if (st.daughters.length >= DAUGHTERS_MAX[TIER_CLASS(st.tier)]) return;
  if (st.daughter && (st.roadPending || s.simDays - st.daughter.day < DAUGHTER_GAP)) return;
  const p = st.ledger.prosperity.slice(-DAUGHTER_DAYS);
  if (p.length < DAUGHTER_DAYS || p.some((v) => v < DAUGHTER_PROS)) return;
  // the direction: along the main street's axis, past its end, at a distance the land allows (the site read decides)
  const pick = rng((st.seed * 31 + 7 + (st.daughters.length * 977)) >>> 0);
  const dist = DAUGHTER_DIST[0] + Math.floor(pick() * (DAUGHTER_DIST[1] - DAUGHTER_DIST[0]));
  const ang0 = pick() * Math.PI * 2;
  const DAUGHTER_CLEAR = 70;
  const clearAt = (x, z) => {
    for (const o of s.settlements) {
      if (o.square && Math.hypot(o.square.x + 6 - x, o.square.z + 6 - z) < DAUGHTER_CLEAR + 60) return false;
      if (o.border && Math.abs(x - (o.square.x + 6)) <= (o.border.r || 0) + 24 && Math.abs(z - (o.square.z + 6)) <= (o.border.r || 0) + 24) return false;
      if (o.kit) for (const key of kitBody(o).keys()) { const c = key.indexOf(","); if (Math.abs(+key.slice(0, c) - x) < DAUGHTER_CLEAR && Math.abs(+key.slice(c + 1) - z) < DAUGHTER_CLEAR) return false; }
    }
    for (const b of s.buildings) if (Math.abs(b.x - x) < DAUGHTER_CLEAR && Math.abs(b.z - z) < DAUGHTER_CLEAR) return false;
    return true;
  };
  let cx = null, cz = null, ang = ang0;
  for (const dd of [dist, dist + 40]) {
    for (let k = 0; k < 12 && cx === null; k++) {
      const a = ang0 + k * Math.PI / 6;
      const x = Math.round(st.square.x + 6 + Math.cos(a) * dd), z = Math.round(st.square.z + 6 + Math.sin(a) * dd);
      if (clearAt(x, z)) { cx = x; cz = z; ang = a; }
    }
    if (cx !== null) break;
  }
  void ang;
  if (cx === null) { st.daughterWait = s.simDays; if (!st.daughterSaid || s.simDays - st.daughterSaid > 30) { st.daughterSaid = s.simDays; st.log.push(`day ${s.simDays.toFixed(0)}: no free land for a daughter town within ${dist + 40} blocks`); } return; }
  st.daughter = { x: cx, z: cz, day: s.simDays };
  const pickAng = pick;
  void pickAng;
  st.log.push(`day ${s.simDays.toFixed(0)}: settlers leave for a new site ${dist} blocks away (${cx} ${cz})`);
  events.push(`§d${st.name}: settlers set out for ${cx} ${cz}`);
  const child = foundSettlement(s, st.dim, cx, cz, (st.seed + 101) >>> 0, (m) => console.warn(`[CIV-CLOCK] daughter: ${m.replace(/§./g, "")}`));
  child.mother = st.id;
  child.name = st.daughters.length ? `${st.name}'s daughter ${st.daughters.length + 1}` : `${st.name}'s daughter`;
  st.daughter.id = child.id;
  st.daughters.push(child.id);
  st.roadPending = true; st.roadTries = 0;
}

/** the street cell of a settlement nearest to a point (the road leaves from the end of a street, not from the square) */
function nearestStreetCell(st, px, pz) {
  if (st.kit) {                                                  // v1.3.219: the nearest corridor cell of the kit streets
    let bk = null, bd = Infinity;
    for (const [key, h] of kitBody(st)) { const [x, z] = key.split(",").map(Number); const d = Math.abs(x - px) + Math.abs(z - pz); if (d < bd) { bd = d; bk = { x, z, h }; } }
    return bk;
  }
  let best = null, bd = 1e18;
  for (const [key, h] of Object.entries(st.profile || {})) {
    const [x, z] = key.split(",").map(Number);
    const d = (x - px) * (x - px) + (z - pz) * (z - pz);
    if (d < bd) { bd = d; best = (st.axis || "x") === "z" ? { x: x + 1, z, h } : { x, z: z + 1, h }; }     // the street's middle row / column
  }
  if (!best && st.square) best = { x: st.square.x + 6, z: st.square.z + LAND.SQUARE, h: st.square.y };
  return best;
}

/** the ROAD between two settlements (step 7): A* over the real ground as a job (LAND.findRoadJob) from the end of one
 *  street network to the other's, around every plot and square, across streets at their own grade (never re-laid),
 *  then laid like a street (profile smoothed, cut/fill, path, bridges, cuttings). Runs once per pair; while it runs
 *  st.roadJob is set (not saved: a reload restarts it); no path -> retried on later days (up to ROAD_TRIES). */
const ROAD_TRIES = 8;
const roadJobs = new Set();
function startRoadJob(s, st, child) {
  const pairKey = `${st.id}-${child.id}`;
  if (roadJobs.has(pairKey) || !child.square || !st.square) return false;
  const dim = world.getDimension(st.dim);
  const a = nearestStreetCell(st, child.square.x + 6, child.square.z + 6), b = nearestStreetCell(child, st.square.x + 6, st.square.z + 6);
  if (!a || !b) return false;
  const sites = [siteOf(st), siteOf(child)].filter(Boolean);
  const streets = streetHeights(s);
  const boxes = plotBoxes(s, 1, null);
  const blocked = (x, z) => boxes.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1);
  const fixedH = (x, z) => streets.get(`${x},${z}`);
  const ground = (x, z) => {
    for (const site of sites) { const g = site.at(x, z); if (g !== undefined) return { g, water: site.isWater(x, z) }; }
    try {
      const g = groundAt(dim, x, z);
      if (g === undefined) return undefined;
      let water = false;
      try { const t = blockAt(dim, x, g + 1, z)?.typeId; water = t === "minecraft:water" || t === "minecraft:flowing_water"; } catch { /* unloaded */ }
      return { g, water };
    } catch { return undefined; }
  };
  roadJobs.add(pairKey);
  const onDone = (cells, note) => {
    roadJobs.delete(pairKey);
    const s2 = load();
    const st2 = s2.settlements.find((x) => x.id === st.id), ch2 = s2.settlements.find((x) => x.id === child.id);
    if (!st2 || !ch2) return;
    if (!cells) {
      st2.roadTries = (st2.roadTries || 0) + 1;
      st2.log.push(`day ${s2.simDays.toFixed(0)}: no road to ${ch2.name} yet (${note})`);
      if (st2.roadTries >= ROAD_TRIES) st2.roadPending = false;
      save();
      return;
    }
    // the land moved on while the search ran (a job over many ticks, retried for days): streets opened and plots were
    // staked since the job started. Cross every street that exists NOW at its own grade (evo 0.0.18 on 210: a road laid
    // from the job-start street map cut a bridge deck and re-graded four cells of a street opened later — D-C508), and
    // if the way now runs through a plot, search again instead of building through it.
    const streetsNow = streetHeights(s2);
    const boxesNow = plotBoxes(s2, 1, null);
    const through = cells.filter(([x, z]) => !streetsNow.has(`${x},${z}`) && boxesNow.some(([x0, x1, z0, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1));
    if (through.length) {
      st2.roadTries = (st2.roadTries || 0) + 1;
      st2.log.push(`day ${s2.simDays.toFixed(0)}: the way to ${ch2.name} was built over while the surveyors worked (${through.length} cells) — they will look again`);
      if (st2.roadTries >= ROAD_TRIES) st2.roadPending = false;
      save();
      return;
    }
    LAND.smoothProfile(cells);
    const road = { kind: "road", to: ch2.id, cells, nCells: cells.length, skip: (x, z) => streetsNow.has(`${x},${z}`) };
    try { road.laid = layPlannedStreet(world.getDimension(st2.dim), road); } catch (e) { console.warn(`[CIV-CLOCK] road lay: ${e}`); road.laid = 0; }
    try { const g = greenCorridor(world.getDimension(st2.dim), s2, road); road.fence = g.fence; road.crossings = g.crossings; if (g.fence) st2.log.push(`day ${s2.simDays.toFixed(0)}: the road to ${ch2.name} is fenced (${g.fence} posts) with ${g.crossings.length} green bridge(s)`); } catch (e) { console.warn(`[CIV-CLOCK] green corridor: ${e}`); }
    road.length = cells.length;
    delete road.cells; delete road.skip;
    st2.roads = st2.roads || []; st2.roads.push(road);
    ch2.roads = ch2.roads || []; ch2.roads.push({ kind: "road", to: st2.id, length: road.length, laid: road.laid });
    st2.roadPending = false;
    st2.log.push(`day ${s2.simDays.toFixed(0)}: a road of ${road.length} cells reaches ${ch2.name} (${note})`);
    console.warn(`[CIV-CLOCK] ${st2.name}: road laid to ${ch2.name} (${road.length} cells, ${road.laid} blocks)`);
    save();
  };
  try { system.runJob(LAND.findRoadJob({ x: a.x, z: a.z }, { x: b.x, z: b.z }, ground, blocked, fixedH, onDone)); } catch (e) { roadJobs.delete(pairKey); console.warn(`[CIV-CLOCK] road job: ${e}`); return false; }
  return true;
}

/** trade along a road: for every good, move from the cheaper to the dearer town when the gap pays the haulage */
function tradeAlong(s, st, events) {
  for (const road of st.roads || []) {
    const other = s.settlements.find((x) => x.id === road.to);
    if (!other || !other.ledger || !st.ledger || other.id < st.id) continue;            // one end drives each pair
    const haul = 1 + road.length / 40;
    const moved = [];
    for (const g of ECON.GOODS) {
      const pa = st.ledger.prices[g], pb = other.ledger.prices[g];
      const [from, to] = pa < pb ? [st, other] : [other, st];
      if (Math.abs(pa - pb) <= haul) continue;
      const n = Math.min(Math.floor(from.ledger.stock[g] / 4), 20);
      if (n <= 0) continue;
      from.ledger.stock[g] -= n; to.ledger.stock[g] += n;
      const pay = n * Math.min(pa, pb);
      to.ledger.treasury -= pay; from.ledger.treasury += pay;
      to.ledger.sunk += pay; from.ledger.tradeIn = (from.ledger.tradeIn || 0) + pay;      // the buyer's money left, the seller's came in
      moved.push(`${n} ${g} ${from === st ? "out" : "in"}`);
      (to.inboundToday = to.inboundToday || []).push([from.id, g]);
    }
    if (moved.length) st.log.push(`day ${s.simDays.toFixed(0)}: wagons: ${moved.join(", ")}`);
    for (const town of [st, other]) {
      const byPartner = {};
      for (const [pid, g] of town.inboundToday || []) (byPartner[pid] = byPartner[pid] || []).push(g);
      for (const [pid, goods] of Object.entries(byPartner)) { const partner = s.settlements.find((x) => x.id === Number(pid)); if (partner) ladder(s, town, partner, goods, events); }
      town.inboundToday = [];
    }
  }
}

// ------------------------------------------------------------------------------------------------ threads + the ladder (step 8)
// The NOTICE BOARD: a sign post on the square shows the chronicle's last lines (E6: the town-hall board); villagers wear
// their trade in their name once they take a job ("Ada the Farmer" — E6: villagers who know you); a MARKET STAND (rung 2)
// appears on the square after five days of goods arriving from one partner, and a BRANCH (rung 4) after twenty: the
// partner's shop of that good opens a plot here, named in the chronicle. ASSUMPTION (his 20:04): the day counts.
const PROFESSION = ["", "Farmer", "Fisherman", "Shepherd", "Fletcher", "Librarian", "Cartographer", "Cleric", "Armorer", "Weaponsmith", "Toolsmith", "Butcher", "Leatherworker", "Mason", ""];

function noticeBoard(dim, st) {
  if (!st.square) return;
  const sq = st.square;
  const x = sq.x + 1, z = sq.z + LAND.SQUARE - 2, y = sq.y + 1;             // the south-west corner of the square, by the street
  try {
    let blk = blockAt(dim, x, y, z);
    if (!blk) return;
    if (blk.typeId !== "minecraft:standing_sign" && blk.typeId !== "minecraft:oak_standing_sign") {
      try { blk.setType("minecraft:standing_sign"); } catch { blk.setType("minecraft:oak_standing_sign"); }
      blk = blockAt(dim, x, y, z);
    }
    const sign = blk.getComponent("minecraft:sign");
    // D-C536: the freshest rumour heads the board, the chronicle's last lines follow
    const rum = st.people ? PEOPLE.board(st.people, Math.floor(load().simDays)).rumours[0] : null;
    const lines = (rum ? [rum] : []).concat(st.log.slice(-4)).slice(0, 4);
    if (sign) sign.setText(lines.map((l) => l.replace(/^day (\d+): /, "d$1 ").slice(0, 32)).join("\n"));
    st.board = { x, y, z };
  } catch (e) { console.warn(`[CIV-CLOCK] board: ${e}`); }
}

function nameTrades(s, st) {
  for (const b of plotsOf(s, st)) {
    for (const id of b.villagers || []) {
      try {
        const v = world.getEntity(id);
        if (!v || VOICE.bubbling(v.id)) continue;                           // B5: never over a line that is up
        const variant = v.getComponent("minecraft:variant");
        const prof = variant ? PROFESSION[variant.value] || "" : "";
        const base = plainName(v.nameTag || "").split(" the ")[0];          // 1.3.228 (B2 / BF3): never the why icon
        const want = prof ? `${base} the ${prof}` : base;
        if (base && v.nameTag !== want) v.nameTag = want;
      } catch { /* gone */ }
    }
  }
}

/** a market stand on the host square: two trestles and a barrel at the square's north edge (one per partner) */
function marketStand(dim, st, partnerId) {
  st.stands = st.stands || [];
  if (st.stands.some((x) => x.partner === partnerId)) return false;
  const k = st.stands.length;
  const sq = st.square;
  const x = sq.x + 2 + k * 4, z = sq.z + 1, y = sq.y + 1;
  try {
    dim.getBlock({ x, y, z })?.setType("pw:furn_trestle_oak");
    dim.getBlock({ x: x + 1, y, z })?.setType("pw:furn_trestle_oak");
    dim.getBlock({ x: x + 2, y, z })?.setType("minecraft:barrel");
  } catch (e) { console.warn(`[CIV-CLOCK] stand: ${e}`); }
  st.stands.push({ partner: partnerId, x, z });
  return true;
}

/** rung 2 and rung 4 of the Presence Ladder, driven by the days of inbound trade from each partner */
function ladder(s, st, partner, goods, events) {
  st.inbound = st.inbound || {};
  const key = String(partner.id);
  const rec = st.inbound[key] = st.inbound[key] || { days: 0, goods: {}, rung: 1 };
  rec.days += 1;
  for (const g of goods) rec.goods[g] = (rec.goods[g] || 0) + 1;
  if (rec.rung < 2 && rec.days >= 5) {
    rec.rung = 2;
    if (marketStand(world.getDimension(st.dim), st, partner.id)) { st.log.push(`day ${s.simDays.toFixed(0)}: ${partner.name} opens a market stand on the square`); events.push(`§d${partner.name}: a stand on ${st.name}'s square`); }
  }
  if (rec.rung < 4 && rec.days >= 20) {
    const g = Object.entries(rec.goods).sort((a, b) => b[1] - a[1])[0];
    const kind = g ? CHARTER[g[0]] : null;
    if (kind) {
      rec.rung = 4;
      const skins = skinsOf(kind);
      const fam = familyOf(kind, skins[Math.floor(rng((st.seed + rec.days) >>> 0)() * Math.max(1, skins.length))]);
      const nb = addPlot(s, st, fam, st.dim, 0, null);
      if (nb) { nb.branchOf = partner.id; st.log.push(`day ${s.simDays.toFixed(0)}: ${partner.name}'s ${kind} opens a branch here (#${nb.id})`); events.push(`§d${partner.name}: a ${kind} branch in ${st.name}`); }
    }
  }
}

/** which settlement a tool means: an explicit index (1-based), else the one whose square is nearest the player, else the first */
function targetSettlement(s, p, idx) {
  if (!s.settlements.length) return null;
  const n = Number(idx);
  if (n >= 1 && n <= s.settlements.length) return s.settlements[n - 1];
  if (p) {
    let best = null, bd = 1e18;
    for (const st of s.settlements) { const cx = (st.square ? st.square.x + 6 : st.x0), cz = (st.square ? st.square.z + 6 : st.z0); const d = (cx - p.location.x) ** 2 + (cz - p.location.z) ** 2; if (d < bd) { bd = d; best = st; } }
    return best;
  }
  return s.settlements[0];
}

function clearEntities(dim, b) {
  const def = BUILDINGS[b.family];
  const [fx, sy, fz] = footprint(def, b.rot);
  try {
    for (const e of dim.getEntities({ location: { x: b.x, y: b.y, z: b.z }, volume: { x: fx, y: sy, z: fz } }))
      if (e.typeId === "pw:marker" || e.typeId === "pw:hatch_lid") e.remove();
  } catch { /* left */ }
}


// ------------------------------------------------------------------------------------------------ LAND SURVEY (1.3.226, his 20:35 / 20:48)
// Bedrock's terrain cannot be reshaped by an add-on (Mojang: custom biomes paint the surface only), so a city must START
// where the land lets it spread. /scriptevent pw:clock survey [radius]: the loaded land around the player in an 8-block
// grid (a column is GENTLE when its 4 neighbours 8 away differ by <= SURVEY_SLOPE and it is dry); every 32 blocks a
// candidate centre is scored by its gentle area within SURVEY_R2; the best three (96+ apart) are named. A job (~100 columns
// a tick; 1.3.228: 50 — each column now walks down through the trees); unloaded columns are counted, never guessed.
// 1.3.228 (B1 / TR4): the height is the GROUND (topAt + the groundAt walk past leaves, logs and plants: a forest read as a
// hill before) and a sleeping column is asked, never read (the raw getTopmostBlock threw there — the leak path)
const SURVEY_STEP = 8, SURVEY_SLOPE = 3, SURVEY_R2 = 64, SURVEY_CENTRE = 32, SURVEY_RELIEF_MAX = 40;
const SURVEY_HOLD_TICKS = 200;                                 // 1.3.231: the longest wait for a held tile's chunks (10 s)
function* surveyJob(dim, cx, cz, R, done) {
  const n = Math.floor(R / SURVEY_STEP), W = 2 * n + 1;
  const H = new Array(W * W).fill(null), WET = new Uint8Array(W * W);
  let read = 0, asleep = 0;
  const readAt = (i, j) => {                                   // true when the column was read
    const x = cx + (i - n) * SURVEY_STEP, z = cz + (j - n) * SURVEY_STEP;
    try {
      const top = topAt(dim, x, z);
      const g = top ? groundAt(dim, x, z, top) : undefined;
      if (top && g !== undefined) {
        const above = blockAt(dim, x, top.location.y + 1, z, true);
        H[i * W + j] = g;
        if ((above && above.typeId === "minecraft:water") || top.typeId.includes("ice")) WET[i * W + j] = 1;
        return true;
      }
    } catch { /* asleep */ }
    return false;
  };
  for (let i = 0; i < W; i++) for (let j = 0; j < W; j++) {
    if (!readAt(i, j)) asleep++;
    if (++read % 50 === 0) yield;
  }
  // 1.3.231 (CIV-LAND, his 00:23 10-07 "until the survey can run again" — his survey: 2173 of 2401 columns not loaded):
  // the sleeping columns are read by holding their land awake — LAND.surveyTiles (128 x 128, chunk-aligned), one ticking
  // area at a time ("civsurvey"), up to SURVEY_HOLD_TICKS for its chunks to load, then removed; a world with no free area
  // (the engine's 10) keeps them unread (counted, as before)
  let held = 0, woke = 0;
  if (asleep) {
    const byTile = new Map();
    for (let i = 0; i < W; i++) for (let j = 0; j < W; j++) {
      if (H[i * W + j] !== null) continue;
      const x = cx + (i - n) * SURVEY_STEP, z = cz + (j - n) * SURVEY_STEP;
      const key = `${Math.floor(x / LAND.WIDE.tile)},${Math.floor(z / LAND.WIDE.tile)}`;
      if (!byTile.has(key)) byTile.set(key, []);
      byTile.get(key).push([i, j]);
    }
    const tiles = [...byTile.entries()].map(([key, cells]) => { const [a, b] = key.split(",").map(Number); return { x0: a * LAND.WIDE.tile, z0: b * LAND.WIDE.tile, cells }; })
      .sort((p, q) => Math.hypot(p.x0 + 64 - cx, p.z0 + 64 - cz) - Math.hypot(q.x0 + 64 - cx, q.z0 + 64 - cz));
    for (const t of tiles) {
      const x1 = t.x0 + LAND.WIDE.tile - 1, z1 = t.z0 + LAND.WIDE.tile - 1;
      try { dim.runCommand("tickingarea remove civsurvey"); } catch { /* none */ }
      let ok = false;
      try { ok = dim.runCommand(`tickingarea add ${t.x0} -64 ${t.z0} ${x1} 320 ${z1} civsurvey true`).successCount > 0; } catch { ok = false; }
      if (!ok) break;                                          // no free ticking area in this world: the rest stays unread
      held++;
      const t0 = system.currentTick;
      let last = -1;
      for (;;) {                                               // wait for the chunks (a check every 20 ticks)
        const now = system.currentTick;
        if (now - t0 > SURVEY_HOLD_TICKS) break;
        if (now - last >= 20) { last = now; if (boxLoaded(dim, t.x0, t.z0, x1, z1)) break; }
        yield;
      }
      for (const [i, j] of t.cells) { if (readAt(i, j)) { asleep--; woke++; } if (++read % 50 === 0) yield; }
      try { dim.runCommand("tickingarea remove civsurvey"); } catch { /* gone */ }
    }
  }
  const gentle = new Uint8Array(W * W);
  for (let i = 1; i < W - 1; i++) for (let j = 1; j < W - 1; j++) {
    const k = i * W + j, h = H[k];
    if (h === null || WET[k]) continue;
    let ok = true;
    for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const h2 = H[(i + di) * W + j + dj]; if (h2 === null || Math.abs(h2 - h) > SURVEY_SLOPE) { ok = false; break; } }
    if (ok) gentle[k] = 1;
  }
  yield;
  const r2 = Math.floor(SURVEY_R2 / SURVEY_STEP), cstep = Math.floor(SURVEY_CENTRE / SURVEY_STEP);
  const cands = [];
  for (let i = r2; i < W - r2; i += cstep) for (let j = r2; j < W - r2; j += cstep) {
    let area = 0, lo = Infinity, hi = -Infinity, known = 0;
    for (let di = -r2; di <= r2; di++) for (let dj = -r2; dj <= r2; dj++) {
      if (di * di + dj * dj > r2 * r2) continue;
      const k = (i + di) * W + j + dj;
      if (H[k] !== null) known++;
      if (!gentle[k]) continue;
      area++; lo = Math.min(lo, H[k]); hi = Math.max(hi, H[k]);
    }
    if (area && hi - lo <= SURVEY_RELIEF_MAX) cands.push({ x: cx + (i - n) * SURVEY_STEP, z: cz + (j - n) * SURVEY_STEP, area: area * SURVEY_STEP * SURVEY_STEP, relief: hi - lo, y: H[i * W + j], known });   // gate 226-1: a 'gentle' patch on a mesa next to a valley (relief 244) is no city site
  }
  yield;
  cands.sort((a, b) => b.area - a.area || a.relief - b.relief);
  const best = [];
  for (const c of cands) { if (best.every((o) => Math.hypot(o.x - c.x, o.z - c.z) >= 96)) best.push(c); if (best.length >= 3) break; }
  done({ best, columns: W * W, asleep, held, woke, gentleShare: gentle.reduce((a, v) => a + v, 0) / Math.max(1, W * W - asleep) });
}
function compassOf(dx, dz) {
  const names = ["east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"];
  return names[(Math.round(Math.atan2(dz, dx) / (Math.PI / 4)) + 8) % 8];
}

system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:clock") return;
  const p = ev.sourceEntity;
  const args = (ev.message || "").trim().split(/\s+/);
  const [cmd, a, b] = args;
  const s = load();
  const reply = (m) => (p ? say(p, m) : console.warn(m.replace(/§./g, "")));
  // 1.3.231 (RAMPS-231 / CIV-LAND, his dirt wedges on the ramps 10-07): /scriptevent pw:clock rampclear [go|force]
  // (dry run / cut natural ground over ramp pieces / also re-send the lane layer) — KIT.rampClear, tests/test_rampclear.mjs
  if (cmd === "rampclear") { reply(KIT.rampClear(s, a, kitPlan, world, system)); return; }
  if (!cmd || cmd === "status") {
    if (p) { status(p); return; }
    // no player (a command block, the console, another pack): one pw:clock_bld script event per building, so other
    // packs (tests, the future villager systems) can read where every building stands and how far it has grown
    console.warn(`[CLOCK] village day ${s.simDays.toFixed(2)} · ${s.buildings.length} building(s)`);
    for (const bb of s.buildings) { try { system.sendScriptEvent("pw:clock_bld", JSON.stringify(bb)); } catch (e) { console.warn(`[CLOCK] ${e}`); } }
    for (const st of s.settlements) {
      const { ledger, log, shortDays, kitQueue, streets, profile, leftover, triedTerraces, people, ...rest } = st;   // a script event message is capped (2 KB): keep it compact (the census stays home)
      void people;
      rest.streets = (streets || []).map((x) => x.kind === "kit" ? { kind: "kit", id: x.id, role: x.role, n: x.H.length, f: x.f, tmin: x.tmin, ramps: x.segs.filter((q) => q.kind === "ramp").length,
        bridges: x.segs.filter((q) => q.kind === "bridge").map((q) => [q.a, q.len]), tees: (x.tees || []).length, access: (x.access || []).length,
        outfalls: (x.outfalls || []).filter((o) => !o || !o.sealed).map((o) => o && o.plan ? [o.plan.exit[0], o.plan.exit[1], o.plan.dir[0], o.plan.dir[1], o.plan.floors ? o.plan.floors[o.plan.floors.length - 1] : o.plan.floorY, o.plan.cells.length, o.plan.target || "v1", o.gone ? 1 : 0, (o.manholes || []).length] : null),
        sealed: (x.outfalls || []).filter((o) => o && o.sealed).length } : { kind: x.kind, laid: x.laid, nCells: x.nCells });
      rest.kitQueue = kitQueue ? kitQueue.length : 0;
      rest.kitWater = st.kitWater || 0;
      rest.streets.forEach((x, i) => { const src = (streets || [])[i]; if (src && src.bench) x.bench = true; });
      rest.roads7 = (st.roads7 || []).map((r) => ({ id: r.id, from: r.from, end: r.end, to: r.to, n: r.cells.length, turns: r.turns.length, ramps: r.ramps.length }));
      rest.roadLaid = st.roadLaid || 0;
      rest.benchFail = st.benchFail;
      rest.crossroads = st.crossroads || 0; rest.blocksClosed = st.blocksClosed || 0;
      rest.walls = (st.walls || []).map((w) => ({ ring: w.ring, n: w.n, gates: w.gates.length, laid: w.laid, box: w.box }));
      rest.leftover = (leftover || []).length;
      rest.civicLeft = (st.civicLeft || []).map(([w]) => w);
      // the roads' cells, in parts (a script event message is capped at 2 KB)
      for (const r of (st.roads7 || [])) {
        for (let i = 0; i < r.cells.length; i += 60) {
          const part = { id: r.id, st: st.id, i, cells: r.cells.slice(i, i + 60), H: r.H.slice(i, i + 60), dirs: r.dirs.slice(i, i + 60), turns: r.turns, ramps: r.ramps, n: r.cells.length };
          try { system.sendScriptEvent("pw:clock_road", JSON.stringify(part)); } catch (e) { console.warn(`[CLOCK] ${e}`); }
        }
      }
      const summary = ledger ? { day: ledger.day, treasury: Math.round(ledger.treasury), purse: Math.round(ledger.purse || 0), minted: ledger.minted, sunk: ledger.sunk, builders: ledger.builders, hired: ledger.hired, arrears: ledger.arrears,
                                 stock: Object.fromEntries(Object.entries(ledger.stock).map(([k, v]) => [k, Math.floor(v)])), prices: ledger.prices, prosperity: ledger.prosperity.slice(-5), closing: ledger.closing, orders: (ledger.orders || []).length, drift: ledger.drift || 0 } : null;
      rest.waiting = plotsOf(s, st).filter((b) => b.waiting).map((b) => [b.id, b.waiting]).slice(0, 6);
      rest.waitingN = plotsOf(s, st).filter((b) => b.waiting).length;
      rest.buildBudget = st.buildBudget;
      rest.walk = { arrived: st.walkArrived || 0, stuck: st.walkStuck || 0, ...WALK.stats() };
      rest.keys = KEYS.assets(st);
      rest.border = st.border ? { r: st.border.r, target: st.border.target, stones: st.border.stones.length, moving: st.border.moves.filter((m) => !m.done).length, disputes: (st.border.disputes || []).map((d) => [d.key, d.state]), wait: st.borderWait || 0 } : null;
      rest.sewerLamps = st.sewerLamps || 0;
      rest.fishers = fishersOf(st).length;                                  // 1.3.225
      rest.laneHouses = plotsOf(s, st).filter((b) => b.kit && b.kit.lane !== undefined && b.kit.lane !== null).length;   // 1.3.226
      rest.lanesLaid = (st.roads7 || []).filter((r) => r.ln && r.laid).length;
      rest.watch = { posts: WATCH.WATCH_POSTS[st.tier] || 0, ...WATCH.stats(st) };
      rest.works = { ...civicWorks(s, st), sanitation: st.sanitation ?? null, health: healthOf(s, st) };
      rest.centres = (st.centres || []).map((c) => [c.sid, c.well, c.shops.length, (s.buildings.find((b) => b.id === c.well) || {}).stage ?? null]);
      rest.market = st.market ? { day: st.market.day, buys: st.market.buys, empty: st.market.empty, homes: Array.isArray(st.market.homes) ? st.market.homes.length : st.market.homes || 0 } : null;
      { const dg = diagOf(st);                                             // 1.3.228 (B2 / WE14): the diagnostics from memory
        rest.counters = dg.counters || null; rest.marketGate = dg.marketGate || null;
        rest.marketTry = dg.marketTry ? { day: dg.marketTry.day, goals: dg.marketTry.goals, noShop: dg.marketTry.noShop, shoppers: dg.marketTry.shoppers.size } : null; }
      rest.prof = { ...(globalThis.__civProf || {}), tick: system.currentTick, ms: Date.now() };
      rest.quarries = plotsOf(s, st).filter((b) => short(b) === "quarry").map((b) => [b.id, b.pit ? b.pit.r : null, b.pit ? b.pit.depth : null, b.pit ? b.pit.off || 0 : 0, b.pitsOpened || 1, (b.oldPits || []).length, b.pit ? b.pit.site ?? null : null, b.workedOut ? 1 : 0, b.skipped || 0]);
      rest.stewardship = { greened: plotsOf(s, st).filter((b) => short(b) === "quarry").reduce((a, b) => a + (b.greened || 0), 0), spoil: plotsOf(s, st).filter((b) => short(b) === "quarry").reduce((a, b) => a + (b.spoil || 0), 0),
                           replanted: plotsOf(s, st).filter((b) => short(b) === "lumberyard").reduce((a, b) => a + (b.replanted || 0), 0), greenbelt: (st.slotWhy && st.slotWhy.greenbelt) || 0 };
      rest.bodies = st.bodies || null;
      rest.drain = { nets: st.drainNets || null, day: st.drainDay ?? null, trunkLamps: st.trunkLamps || 0 };
      rest.manholes = { laid: st.manholesLaid || 0, planned: st.streets.reduce((a, x) => a + ((x.manholes || []).length), 0), cells: (st.manholeCells || []).slice(0, 24) };
      rest.labor = { built: st.built || 0, sites: plotsOf(s, st).filter((b) => b.labor).map((b) => [b.id, b.labor.k, b.labor.done, b.labor.need, b.labor.crew || 0]) };
      rest.work = { total: st.workTotal || 0, today: st.workToday || {}, ...WORKMOD.stats(), pits: plotsOf(s, st).filter((b) => short(b) === "quarry").map((b) => [b.id, b.dug || 0, b.spoil || 0, b.pit ? b.pit.r : null]), stands: plotsOf(s, st).filter((b) => short(b) === "lumberyard").map((b) => [b.id, b.felled || 0, b.replanted || 0, b.planted || 0]) };
      rest.ticking = Object.values(coreState(s).areas).filter((x) => x.st === st.id).map((x) => [x.name, x.box, x.why]);
      if (st.people) { const al = PEOPLE.alive(st.people); rest.census = { n: al.length, homeless: al.filter((p) => !p.home).length, mood: st.mood ?? null, married: al.filter((p) => p.spouse).length, children: al.filter((p) => PEOPLE.stage(p, Math.floor(s.simDays)) === "child").length, rumours: st.people.rumours.length, threads: st.people.threads.filter((t) => t.state === "open").length, needs: diagOf(st).mood || null, shift: diagOf(st).shift || null, inn: diagOf(st).inn || 0, rain: diagOf(st).rain || null, moves: diagOf(st).moves || null }; }   // B3: tiers, births10, pressure (memory); B4: shifts, inn, rain, moves
      rest.lag = s.lag || 0;                                               // the probe waits for the carried days
      rest.engineThrows = ENGINE.throws; rest.dpBytes = s.dpBytes ?? null;  // 1.3.228 (B1 / EN4)
      rest.fell = { ...FELL };                                               // 1.3.228 (B2 / BF10): tree verdicts and fells
      rest.save = (({ last, ...x }) => ({ ...x, wrote: last ? last.wrote : null, of: last ? last.of : null, chars: last ? last.chars : null }))(SAVER.stats());   // B2 / BF2
      try { system.sendScriptEvent("pw:clock_stl", JSON.stringify({ ...rest, log: log.slice(-6), population: population(s, st), ledger: summary, stateBytes: s.bytes })); } catch (e) { console.warn(`[CLOCK] ${e}`); }
    }
    return;
  }
  if (cmd === "walktest") {                                    // 0.0.25: the walk instrument (the harness)
    const st = s.settlements.filter((x) => x.kit && x.square).slice(-1)[0];
    if (!st) { reply("§c[CLOCK] no kit settlement"); return; }
    walkTest(s, st, Math.max(1, Math.min(8, parseInt(a || "8", 10) || 8)));
    reply(`§e[CLOCK] walk test: ${walkTests.size} walkers`); return;
  }
  if (cmd === "keytest") {                                      // F4 witness: a test key, only for a player tagged civ:tester
    if (!p || !p.hasTag("civ:tester")) { reply("§c[CLOCK] keytest is for a player tagged civ:tester (the keys are never given otherwise)"); return; }
    const st = s.settlements.slice().sort((a2, b2) => Math.hypot(a2.x0 - p.location.x, a2.z0 - p.location.z) - Math.hypot(b2.x0 - p.location.x, b2.z0 - p.location.z))[0];
    if (!st) { reply("§c[CLOCK] no settlement"); return; }
    const k = KEYS.giveTestKey(p, st, Math.floor(s.simDays));
    st.log.push(`day ${s.simDays.toFixed(0)}: (test) key ${k.id} given to ${p.name}`);
    save(); reply(`§e[CLOCK] test key ${k.id} of ${st.name} in your inventory`); return;
  }
  if (cmd === "realstage") {                                   // the harness: a real labour site now (C2.3)
    const frac = Math.min(1, Math.max(0.01, parseFloat(a || "1") || 1));
    const b = s.buildings.find((x) => x.settlement !== undefined && x.stage >= 0 && x.stage < BUILDINGS[x.family].stages - 1 && !x.labor && !x.closed && !x.pending.length);
    if (!b) { reply("§c[CLOCK] no building has a next stage to build"); return; }
    const st = s.settlements.find((x) => x.id === b.settlement);
    const bill = stageBillOf(b, b.stage + 1);
    const took = takeFromStores(s, st, bill);
    b.labor = { k: b.stage + 1, need: Math.max(BUILD_TICKS * 8, Math.round(bill.blocks * BUILD_TICKS * frac)), done: 0, day: s.simDays, took, harness: true };
    delete b.waiting; delete b.waitKey;
    st.log.push(`day ${s.simDays.toFixed(0)}: (harness) the builders begin the ${STAGE_NAMES[b.stage + 1]} of #${b.id} ${short(b)} (${bill.blocks} blocks x ${frac})`);
    save();
    reply(`§e[CLOCK] labour started on #${b.id} ${short(b)} -> ${STAGE_NAMES[b.stage + 1]} (need ${b.labor.need})`);
    return;
  }
  if (cmd === "survey" || cmd === "surveyat") {                 // 1.3.226: where can a city spread? (his 20:35 / 20:48)
    let cx, cz, dim;
    if (cmd === "survey") { if (!p) { reply("[CLOCK] survey needs a player (or surveyat x z [radius])"); return; } cx = Math.floor(p.location.x); cz = Math.floor(p.location.z); dim = p.dimension; }
    else { cx = Math.floor(Number(a)); cz = Math.floor(Number(b)); dim = world.getDimension("overworld"); if (!Number.isFinite(cx) || !Number.isFinite(cz)) { reply("§c[CLOCK] usage: surveyat <x> <z> [radius]"); return; } }
    const R = Math.min(320, Math.max(96, Number(cmd === "survey" ? a : args[3]) || 192));
    reply(`§e[CLOCK] the surveyors read the land within ${R} blocks (8-block grid) …`);
    system.runJob(surveyJob(dim, cx, cz, R, (r) => {
      console.warn(`[CIV-SURVEY] ${JSON.stringify({ at: [cx, cz], R, ...r })}`);
      if (!r.best.length) { reply(`§c[CLOCK] no gentle land found within ${R} blocks (${r.asleep} of ${r.columns} columns not loaded — walk further out and survey again)`); return; }
      const lines = r.best.map((c, i) => `§e${i + 1}) §f${c.x} ${c.y ?? "?"} ${c.z}§e — ${Math.round(Math.hypot(c.x - cx, c.z - cz))} blocks ${compassOf(c.x - cx, c.z - cz)}, ${c.area.toLocaleString()} m² of gentle land within 64, relief ${c.relief}`);
      reply(`§e[CLOCK] the best ground for a city (gentle = slope ≤ 3 per 8 blocks, dry):\n${lines.join("\n")}\n§7${Math.round(r.gentleShare * 100)} % of the land read is gentle; ${r.asleep} of ${r.columns} columns were not loaded${r.held ? ` (${r.woke} read by holding ${r.held} tiles awake)` : ""}. Stand on a site and use /scriptevent pw:clock village to found there.`);
    }));
    return;
  }
  if (cmd === "statesize") {                                    // 1.3.227: /scriptevent pw:clock statesize — what the saved town is made of
    const len = (o) => { try { return JSON.stringify(o).length; } catch { return -1; } };
    const top = Object.keys(s).filter((k) => k !== "settlements").map((k) => [k, len(s[k])]).sort((x, y) => y[1] - x[1]);
    const per = s.settlements.map((st) => ({ id: st.id, total: len(st), keys: Object.keys(st).map((k) => [k, len(st[k])]).sort((x, y) => y[1] - x[1]).slice(0, 14) }));
    const bk = {};
    for (const b of s.buildings) for (const k of Object.keys(b)) bk[k] = (bk[k] || 0) + len(b[k]);
    const total = len(s);
    const ppl = s.settlements.map((st) => {
      const P = st.people; if (!P) return null;
      const pk = {}; for (const q of P.list) for (const k of Object.keys(q)) pk[k] = (pk[k] || 0) + len(q[k]);
      const pre = {}; let entries = 0; for (const q of P.list) for (const k of Object.keys(q.trust || {})) { entries++; const pf = k.split(":")[0]; pre[pf] = (pre[pf] || 0) + 1; }
      return { id: st.id, trustEntries: entries, trustByKind: pre, deadWithTrust: P.list.filter((q) => !q.alive && q.trust).length, list: P.list.length, alive: P.list.filter((q) => q.alive).length, rumours: (P.rumours || []).length, threads: (P.threads || []).length,
        parts: Object.keys(P).map((k) => [k, len(P[k])]).sort((x, y) => y[1] - x[1]).slice(0, 8), personKeys: Object.entries(pk).sort((x, y) => y[1] - x[1]).slice(0, 10) };
    });
    console.warn(`[CIV-STATESIZE] ${JSON.stringify({ total, engineThrows: ENGINE.throws, dpBytes: s.dpBytes ?? null, dpCeiling: s.dpCeiling || DP_CEILING, buildings: s.buildings.length, sections: SAVER.sizes(), save: (({ last, ...x }) => x)(SAVER.stats()), top: top.slice(0, 8), buildingKeys: Object.entries(bk).sort((x, y) => y[1] - x[1]).slice(0, 12), per, people: ppl })}`);
    { const sz = Object.entries(SAVER.sizes()).sort((x, y) => y[1] - x[1]).slice(0, 6).map(([k, n]) => `${k.replace("pw:civ:", "")} ${n.toLocaleString()}`).join(" · ");   // 1.3.228 (B2 / BF2): per key
      reply(`§e[CLOCK] the saved town is ${total.toLocaleString()} characters (${s.buildings.length} buildings), the world's dynamic properties ${(s.dpBytes ?? 0).toLocaleString()} B; largest sections: ${sz || "(not saved yet)"}; details in the content log`); }
    return;
  }
  if (cmd === "dpceiling") {                                    // 1.3.228 (B1 / EN4): the dynamic-property warning ceiling in MB (0 = the default 4 MB)
    const mb = Number(a);
    if (!Number.isFinite(mb) || mb < 0) { reply(`§e[CLOCK] dynamic-property ceiling ${s.dpCeiling || DP_CEILING} B (now ${s.dpBytes ?? "?"} B); usage: dpceiling <MB>`); return; }
    if (mb === 0) delete s.dpCeiling; else s.dpCeiling = Math.round(mb * 1024 * 1024);
    save();
    reply(`§e[CLOCK] dynamic-property ceiling ${s.dpCeiling || DP_CEILING} B`);
    return;
  }
  if (cmd === "why") {                                          // 1.3.228 (B2 / BF3): why-idle codes — why [name|CODE] · why icons on|off
    if (a === "icons") {
      if (b === "on") s.whyIcons = true; else if (b === "off") delete s.whyIcons;
      else { reply(`§e[CLOCK] why icons are ${s.whyIcons ? "ON" : "OFF"} (usage: why icons on|off)`); return; }
      if (!s.whyIcons) for (const st of s.settlements) for (const v of HB.bodiesOf(st)) { try { if (ICON_TAG.test(v.nameTag || "")) setWhyIcon(v, null); } catch { /* left */ } }
      save();
      reply(`§e[CLOCK] why icons ${s.whyIcons ? `ON: villagers within ${WHY_ICON_R} blocks of a player carry their reason after their name (the next schedule pass)` : "OFF: the names are plain again"}`);
      return;
    }
    const q = args.slice(1).join(" ").trim();
    const isCode = /^[A-Z_]+(:[a-z_]+)?$|^—$/.test(q);
    for (const st of s.settlements) {
      if (!q) {
        console.warn(`[CIV-WHY] ${JSON.stringify({ settlement: st.id, tier: st.tier, day: Math.floor(s.simDays), why: st.why || null })}`);
        reply(`§e[CLOCK] ${st.name}: ${Object.entries(st.why || {}).map(([k, n]) => `${k} ${n}`).join(" · ") || "no tally yet (the next schedule pass)"}`);
        continue;
      }
      const P = st.people ? PEOPLE.alive(st.people) : [];
      const hits = isCode ? P.filter((x) => (whyNow.get(`${st.id}:${x.id}`) || "").startsWith(q)) : P.filter((x) => x.name.toLowerCase().includes(q.toLowerCase()));
      if (!hits.length) continue;
      if (isCode) reply(`§e[CLOCK] ${st.name}: ${q} (${PEOPLE.WHY[q.split(":")[0]] || "?"}): ${hits.slice(0, 20).map((x) => x.name).join(", ")}${hits.length > 20 ? ` … +${hits.length - 20}` : ""}`);
      else for (const x of hits.slice(0, 8)) { const c = whyNow.get(`${st.id}:${x.id}`) || "—"; reply(`§e[CLOCK] ${x.name} (${st.name}): ${c} — ${PEOPLE.WHY[c.split(":")[0]] || "?"}${c.startsWith("SITE_WAITS:") ? ` (${c.slice(11)})` : ""}`); }
    }
    if (q) reply(`§7[CLOCK] codes: ${Object.keys(PEOPLE.WHY).join(" ")}`);
    return;
  }
  if (cmd === "shift") {                                        // 1.3.228 (B4 / BF5): shift [name] [template|default]
    const T = Object.keys(PEOPLE.SHIFT.T), wd = worldDay();
    let tod0 = 0; try { tod0 = world.getTimeOfDay(); } catch { /* left */ }
    if (!a) {
      for (const st of s.settlements) {
        if (!st.people) continue;
        const by = {}; let off = 0;
        for (const q of PEOPLE.alive(st.people)) { const o = shiftOpts(s, st, q); const t = PEOPLE.shiftTemplate(q, o); by[t] = (by[t] || 0) + 1; if (PEOPLE.dayOff(q, wd, { ...o, tpl: t })) off++; }
        reply(`§e[CLOCK] ${st.name}: ${Object.entries(by).map(([k, n]) => `${k} ${n}`).join(" · ")}; ${off} off today (world day ${wd})${diagOf(st).shift ? `; now W ${diagOf(st).shift.W} M ${diagOf(st).shift.M} I ${diagOf(st).shift.I} R ${diagOf(st).shift.R}` : ""}`);
      }
      reply(`§7[CLOCK] templates: ${T.map((k) => `${k} ${PEOPLE.SHIFT.T[k]}`).join(" | ")} (W work, M meet, I idle, R rest; hour 0 = midnight). Usage: shift <name> <template|default>`);
      return;
    }
    const want = b ? b.toLowerCase() : null;
    if (want && want !== "default" && !T.includes(want)) { reply(`§c[CLOCK] no template "${b}" (${T.join(", ")}, default)`); return; }
    let n = 0;
    for (const st of s.settlements) {
      if (!st.people) continue;
      for (const q of PEOPLE.alive(st.people).filter((x) => x.name.toLowerCase().includes(a.toLowerCase())).slice(0, 8)) {
        if (want === "default") delete q.shift; else if (want) q.shift = want;
        const o = shiftOpts(s, st, q), sh = PEOPLE.shiftAt(q, tod0, wd, o);
        reply(`§e[CLOCK] ${q.name} (${st.name}): ${sh.tpl}${q.shift ? " (set)" : ""}, offset ${PEOPLE.shiftOffset(q.id)} ticks, now ${sh.slot}${sh.off ? ", a day off" : ""}${sh.home ? ", walking home" : ""}; walk home ${o.travel} ticks${homeFarOf(s, st, q) ? " (§chome too far§e)" : ""}`);
        n++;
      }
    }
    if (want && n) save();
    if (!n) reply(`§c[CLOCK] nobody named "${a}"`);
    return;
  }
  if (cmd === "tax" || cmd === "audit" || cmd === "board") {     // 1.3.228 (B7 / WE11 + WE12 + BF8; his 12:20: free commands)
    const loc = p && p.location;
    const st = (loc && s.settlements.find((x) => inInfluence(x, loc.x, loc.z))) || s.settlements[0];
    const L = st && st.ledger;
    if (!L) { reply("§e[CLOCK] no ledger yet"); return; }
    if (cmd === "tax") {
      if (a && ECON.TAX[a] !== undefined) { if (a === "normal") delete L.tax; else L.tax = a; save(); }
      else if (a) { reply("§e[CLOCK] tax low | normal | high"); return; }
      reply(`§e[CLOCK] ${st.name}: the hearth tax is ${L.tax || "normal"} (x${ECON.taxFactor(L)} every ${ECON.HEARTH_DAYS} days; mood x${ECON.TAX_MOOD[L.tax || "normal"]})`);
      return;
    }
    if (cmd === "audit") {
      const M = L.treasury + L.purse + Object.values(L.tills).reduce((x, v) => x + v, 0);
      const c = COIN.census();
      const lines = COIN.ledger().lines.slice(-8);
      reply(`§e[CLOCK] ${st.name} audit: money ${M} p = treasury ${L.treasury} + purse ${L.purse} + tills ${M - L.treasury - L.purse}; minted ${L.minted} + player ${L.playerNet} + trade ${L.tradeIn || 0} - sunk ${L.sunk} -> drift ${M - (L.minted + L.playerNet + (L.tradeIn || 0) - L.sunk)} (total drift ${L.drift || 0})`);
      reply(`§e[MINT] gold: issued ${c.issued}, returned ${c.returned}, lost ${c.destroyed}, in circulation ${c.circulation} (carried ${c.carried}, in piles ${c.inPiles}); nickels: issued ${c.nickels.issued}, returned ${c.nickels.returned}, in circulation ${c.nickels.circulation}`);
      for (const l of lines) reply(`§7  ${l}`);
      console.warn(`[CIV-AUDIT] ${JSON.stringify({ st: st.id, money: M, minted: L.minted, playerNet: L.playerNet, sunk: L.sunk, drift: L.drift || 0, mint: c })}`);
      return;
    }
    const slips = noticeSlips(s, st);
    reply(`§e[CLOCK] ${st.name} notices: ${slips.length ? slips.map((x) => `${x.qty} ${x.good} for ${COIN.fmtP(x.reward)} (${x.why})`).join(" · ") : "none — the town lacks nothing it can pay for"}`);
    return;
  }
  if (cmd === "prio") {                                         // 1.3.228 (B6 / BF6 + GB5; his 12:20: a free command): prio <family> | prio clear | prio
    const loc = p && p.location;
    const st = (loc && s.settlements.find((x) => inInfluence(x, loc.x, loc.z))) || s.settlements[0];
    if (!st) { reply("§e[CLOCK] no settlement"); return; }
    if (a === "clear") { delete st.prio; save(); reply(`§e[CLOCK] ${st.name}: priorities cleared`); return; }
    if (a) {
      const nm = a.replace(/^pw:(mvv_)?/, "").replace(/_[a-d]_r1$/, "");
      if (!skinsOf(nm).length && !BUILDINGS[familyOf(nm)]) { reply(`§e[CLOCK] unknown building "${a}" (e.g. bakery, cottage_m, manor)`); return; }
      st.prio = [...new Set([nm, ...(st.prio || [])])].slice(0, 6);
      save();
      reply(`§e[CLOCK] ${st.name} builds first: ${st.prio.join(", ")} (inside the tier charter — the counts never change)`);
      return;
    }
    reply(`§e[CLOCK] ${st.name} priorities: ${(st.prio || []).join(", ") || "none"}; resting after a failed search: ${Object.entries(st.failCool || {}).map(([k, d]) => `${k} (day ${d})`).join(", ") || "none"}`);
    return;
  }
  if (cmd === "beds") {                                         // 1.3.229 (his 14:07): the palace's role beds — held / reserved, and who
    const loc = p && p.location;
    const st = (loc && s.settlements.find((x) => inInfluence(x, loc.x, loc.z))) || s.settlements[0];
    if (!st) { reply("§e[CLOCK] no settlement"); return; }
    const pieces = s.buildings.filter((b) => b.palace && b.settlement === st.id);
    if (!pieces.length) { reply(`§e[CLOCK] ${st.name}: no palace yet (laid at city II)`); return; }
    const done = pieces.filter((b) => b.stage >= 4 && !b.closed).map((b) => b.palace.q);
    const all = {};
    for (const q of done) for (const [r, n] of Object.entries(COURT.bedsOfPiece(q))) all[r] = (all[r] || 0) + n;
    const P = census(st), mem = PEOPLE.alive(P).filter((q) => q.court);
    const by = {};
    for (const q of mem) (by[q.court.r] = by[q.court.r] || []).push(q.name);
    reply(`§e[CLOCK] ${st.name} palace beds (finished pieces ${done.join(" ") || "none"}):`);
    for (const r of COURT.COURT.order) if (all[r]) reply(`§e  ${r}: ${(by[r] || []).length} of ${all[r]}${r === "lord" || r === "noble" ? " (couples sleep 2 to a bed)" : ""} — ${(by[r] || []).slice(0, 8).join(", ") || "reserved, waiting for the role"}${(by[r] || []).length > 8 ? " …" : ""}`);
    return;
  }
  if (cmd === "savehold") {                                     // 1.3.228 (B2 / BF2): release a save hold (the stored town could not be read at load)
    if (a === "off") { saveHold = false; save(true); reply("§e[CLOCK] save hold released: the town in memory was saved"); return; }
    reply(`§e[CLOCK] save hold is ${saveHold ? "§cON§e (the stored town could not be read; savehold off writes the town in memory over it)" : "off"}`);
    return;
  }
  if (cmd === "beat") {                                         // 1.3.228 (B1 / BF1): the heartbeat now (the window so far) -> content log
    console.warn(`[CIV-BEAT] ${JSON.stringify(HB.stats())}`);
    reply("§e[CLOCK] heartbeat written to the content log ([CIV-BEAT])");
    return;
  }
  if (cmd === "sewers") {                                       // 1.3.225: /scriptevent pw:clock sewers — every home reaches the sewer?
    for (const st of s.settlements.filter((x) => x.kit)) {
      const r = sewerReach(s, st);
      console.warn(`[CIV-SEWERS] ${JSON.stringify({ settlement: st.id, tier: st.tier, ...r, none: r.none.slice(0, 20), blocked: r.blocked.slice(0, 20) })}`);
      reply(`§e[CLOCK] ${st.name}: ${r.linked} of ${r.houses} finished houses reach the sewer (${r.hatch} by a hatch, ${r.branch} by a branch)${r.blocked.length ? `, §c${r.blocked.length} blocked§e` : ""}${r.none.length ? `, §c${r.none.length} with no link§e` : ""}${r.asleep ? `, ${r.asleep} not loaded` : ""}`);
    }
    return;
  }
  if (cmd === "frontage") {                                     // 1.3.225: /scriptevent pw:clock frontage [house] — where can houses still go, and why not
    const kind = (a || "cottage_m").replace(/^pw:mvv_/, "");
    for (const st of s.settlements.filter((x) => x.kit)) {
      const fam = familyOf(kind, skinsOf(kind)[0]);
      const c = fam ? frontageCensus(s, st, fam) : null;
      if (!c) { reply(`§c[CLOCK] frontage: no house '${kind}'`); return; }
      console.warn(`[CIV-FRONTAGE] ${JSON.stringify({ settlement: st.id, tier: st.tier, plots: plotsOf(s, st).length, ...c })}`);
      const top = Object.entries(c.total.why).sort((p, q) => q[1] - p[1]).slice(0, 5).map(([k, n]) => `${k} ${n}`).join(", ");
      reply(`§e[CLOCK] ${st.name}: ${c.total.fits} more ${kind} would fit along ${c.streets.length} streets (${c.total.flat} cells of frontage of ${c.total.corridor * 2}; ${st.winReleased || 0} cross-street gaps given back${c.total.plateau ? `; ${c.total.plateau} of them on PLATEAUS` : ""}); refused: ${top}`);
    }
    return;
  }
  if (cmd === "tickslots") {                                   // D-C542: how many ticking areas the clock may hold (by host)
    const n = parseInt(a || "", 10);
    if (!(n >= 0 && n <= 9)) { reply(`§e[CLOCK] ticking slots: ${coreState(s).slots} (areas: ${Object.values(coreState(s).areas).map((x) => `${x.name} ${x.why}`).join("; ") || "none"}) — usage: tickslots <0..9>`); return; }
    coreState(s).slots = n; save(); reply(`§e[CLOCK] ticking slots set to ${n}`); return;
  }
  if (cmd === "pause" || cmd === "resume") { s.paused = cmd === "pause"; save(); reply(`§e[CLOCK] village clock ${s.paused ? "paused" : "running"}`); return; }
  if (cmd === "pace") {                                            // 1004b: /scriptevent pw:clock pace 20|25|35|50 (civ walking speed x0.01; 25 = half speed, the default)
    const pc = parseInt(a, 10);
    if (!PACES.includes(pc)) { reply(`§c[CLOCK] usage: pace <20|25|35|50>  (now ${s.pace || 25}; 25 = half the vanilla villager, 50 = vanilla)`); return; }
    s.pace = pc; save();
    let n = 0;
    for (const st of s.settlements) { try { for (const v of world.getDimension(st.dim).getEntities({ tags: [`civ:settlement:${st.id}`], type: VILLAGER_ID })) { applyPace(v, pc); n++; } } catch { /* unloaded */ } }
    reply(`§e[CLOCK] civ pace ${pc} (movement 0.${pc}) applied to ${n} civ(s); new civs follow`); return;
  }
  if (cmd === "speed") {
    const x = Math.min(100, Math.max(0.1, parseFloat(a)));
    if (!isFinite(x)) { reply("§c[CLOCK] usage: speed <0.1..100>"); return; }
    s.speed = x; save(); reply(`§e[CLOCK] ${x} village day(s) per world day`); return;
  }
  if (cmd === "step" || cmd === "skip") {
    const days = parseFloat(a || "1");
    if (!(days > 0 && days <= 3650)) { reply("§c[CLOCK] usage: step [days]  /  skip <days>  (up to 3650)"); return; }
    s.accelLeft = (s.accelLeft || 0) + days;                   // D-C542: skipped days are ACCELERATED (no hands worked them)
    const evs = advance(days);                                 // the first LAG_SLICES days now, the rest one per beat
    const shown = evs.length > 12 ? evs.slice(0, 12).join(", ") + ` … (+${evs.length - 12})` : evs.join(", ");
    reply(`§e[CLOCK] +${days} village day(s) -> day ${s.simDays.toFixed(2)}${s.lag > 0 ? ` (${s.lag.toFixed(0)} more day(s) run on the beat)` : ""}${evs.length ? ": " + shown : " (no stage change)"}`);
    return;
  }
  if (cmd === "plot" || cmd === "plotat") {
    const at = cmd === "plotat" ? args.slice(1, 4).map(Number) : null;
    if (cmd === "plot" && !p) { reply("[CLOCK] plot needs a player (or use plotat x y z)"); return; }
    if (at && !at.every(Number.isFinite)) { reply("§c[CLOCK] usage: plotat <x> <y> <z> [building] [rotation]"); return; }
    const fam = cmd === "plotat" ? args[4] : a;
    const rot = rotOf(cmd === "plotat" ? args[5] : b);
    const family = familyOf(fam);
    const def = BUILDINGS[family];
    if (!def) { reply(`§c[CLOCK] unknown building ${fam}; known: ${Object.values(BUILDINGS).map((d) => d.stem).join(", ")}`); return; }
    if (rot < 0) { reply("§c[CLOCK] rotation: None | Rotate90 | Rotate180 | Rotate270 (or 0 / 90 / 180 / 270)"); return; }
    const l = at ? { x: at[0] - 2, y: at[1], z: at[2] } : p.location;
    const bld = { id: s.nextId++, family, dim: p ? p.dimension.id : "minecraft:overworld", x: Math.floor(l.x) + 2, y: Math.floor(l.y) - def.datum_y,
                  z: Math.floor(l.z), rot, stage: 0, progress: 0, delay: 0, pending: [0] };
    s.buildings.push(bld);
    flushPending(); save();
    reply(`§e[CLOCK] #${bld.id} ${family} (${ROTS[rot]}): plot laid at ${bld.x} ${Math.floor(l.y)} ${bld.z}; frame after ${STAGE_DAYS[0]} village day(s)`);
    return;
  }
  if (cmd === "village" || cmd === "villageat") {
    let x0, z0, dimId;
    if (cmd === "village") {
      if (!p) { reply("[CLOCK] village needs a player (or use villageat x z)"); return; }
      x0 = Math.floor(p.location.x) + 3; z0 = Math.floor(p.location.z) - 1; dimId = p.dimension.id;
    } else {
      x0 = Number(a); z0 = Number(b); dimId = "minecraft:overworld";
      if (!Number.isFinite(x0) || !Number.isFinite(z0)) { reply("§c[CLOCK] usage: villageat <x> <z>"); return; }
      x0 = Math.floor(x0); z0 = Math.floor(z0);
    }
    const seedArg = cmd === "village" ? a : args[3];
    const seed = seedArg !== undefined && Number.isFinite(Number(seedArg)) ? Number(seedArg) : undefined;
    if (args.includes("flat")) {                              // the straight street of V1 (test tool)
      const st = { id: s.settlements.length + 1, name: `settlement ${s.settlements.length + 1}`, dim: dimId, x0, z0, seed: (seed ?? 1) >>> 0,
                   founded: s.simDays, tier: "village", tierDay: s.simDays, declining: false, declineDays: 0, log: [],
                   streets: [{ x0, z0, xn: x0, xs: x0, nextNorth: true }], planned: false };
      s.settlements.push(st);
      const made = layVillageOn(s, st, dimId, x0, z0, st.seed);
      flushPending(); save();
      reply(`§e[CLOCK] flat village of ${made.length} plots laid along a straight street from ${x0} ${z0}`);
      return;
    }
    reply(`§e[CLOCK] reading the land around ${x0} ${z0} (160 x 160) …`);
    foundSettlement(s, dimId, x0, z0, seed, reply);
    return;
  }
  if (cmd === "bench") {
    const st = targetSettlement(s, p, a);
    if (!st || !st.kit) { reply("§c[CLOCK] no kit settlement here"); return; }
    delete st.benchFail;
    startBenchJob(st);
    reply(`§e[CLOCK] ${st.name}: looking for a new bench and a road to it (${departures(st).length} departure(s))`);
    return;
  }
  if (cmd === "grow" || cmd === "decline" || cmd === "immigrate" || cmd === "log") {
    // settlement tools: grow = reach the next tier now (plots added, staggered) · decline on|off · immigrate [building]
    // = reopen a closed shop, else add a cottage (or the named building) · log = the settlement's chronicle
    const st = targetSettlement(s, p, b);
    if (!st) { reply("§c[CLOCK] no settlement yet — use village / villageat first"); return; }
    const evs = [];
    if (cmd === "grow") {
      const next = TIERS[TIERS.indexOf(st.tier) + 1];
      if (!next) { reply(`§e[CLOCK] ${st.name} is already a ${st.tier}`); return; }
      if (st.tierWork) { reply(`§e[CLOCK] ${st.name}: still laying out ${TIER_LABEL[st.tierWork.tier] || st.tierWork.tier} (${st.tierWork.i}/${st.tierWork.items.length} plots${st.tierWork.i >= st.tierWork.items.length ? `, then ${st.tierWork.after.join(", ")}` : ""}) — grow again when it is done`); return; }
      tierUp(s, st, next, evs);
    } else if (cmd === "decline") {
      st.declining = a !== "off";
      st.declineDays = 0;
      evs.push(`${st.name} ${st.declining ? "is now DECLINING (a shop closes every " + DECLINE_DAYS + " days, no growth)" : "recovers"}`);
    } else if (cmd === "immigrate") {
      // newcomers: an empty furnished home first, then a closed shop, then a new plot
      const empty = plotsOf(s, st).find((b) => b.stage >= 4 && b.villagers && !b.villagers.length && hhOf(b));
      if (empty) {
        delete empty.villagers;
        moveIn(world.getDimension(empty.dim), empty, BUILDINGS[empty.family]);
        evs.push(`§a${st.name}: newcomers moved into the empty ${short(empty)} (#${empty.id})`);
      } else if (!(a && a !== "cottage") || !reopenShop(s, st, evs)) {
        if (!reopenShop(s, st, evs)) {
          const nm = a || "cottage_s";
          const skins = skinsOf(nm);
          const fam = familyOf(nm, skins[Math.floor(rng((st.seed + s.simDays * 977) >>> 0)() * Math.max(1, skins.length))]);
          if (!BUILDINGS[fam]) { reply(`§c[CLOCK] unknown building ${nm}`); return; }
          const nb = addPlot(s, st, fam, st.dim, 0, null);
          if (!nb) { reply("§c[CLOCK] no room on the streets"); return; }
          st.log.push(`day ${s.simDays.toFixed(0)}: newcomers — ${short(nb)} plot`);
          evs.push(`§a${st.name}: newcomers take a ${short(nb)} plot at ${nb.x} ? ${nb.z}`);
        }
      }
    } else {
      reply(`§e[CLOCK] ${st.name} chronicle:`);
      for (const line of st.log.slice(-12)) reply(`§7  ${line}`);
      return;
    }
    flushPending(); save();
    reply(`§e[CLOCK] ${evs.join("; ") || "nothing to do"}`);
    return;
  }
  if (cmd === "coins") {                                        // v1.3.219: the mint's census
    const c = COIN.census();
    reply(`§e[MINT] issued ${c.issued} (serials #1-#${c.seq}) · returned ${c.returned} · lost ${c.destroyed} · in circulation ${c.circulation} · ` +
      `carried by players online ${c.carried} · ${c.piles} pile(s) holding ${c.inPiles}`);
    for (const line of COIN.ledger().lines.slice(-10)) reply(`§7  ${line}`);
    if (p && a === "give") { const n = Math.max(1, Math.min(640, Math.floor(Number(b) || 16))); COIN.issue(p, n, "the mint", "test tool"); reply(`§a[MINT] ${n} coins issued to you`); }
    return;
  }
  if (cmd === "market" || cmd === "buy" || cmd === "sell") {
    // market: the newest settlement's stock, prices, treasury · buy <good> <n> / sell <good> <n>: the player trades in
    // emeralds (1 emerald = COIN_PER_EMERALD coin; E5 c: coin + emeralds, exchangeable)
    const st = s.settlements[s.settlements.length - 1];
    if (!st || !st.ledger) { reply("§c[CLOCK] no market yet — found a village and let a day pass"); return; }
    const L = st.ledger;
    if (cmd === "market") {
      reply(`§e[MARKET] ${st.name}: treasury ${Math.round(L.treasury)} coin · day ${L.day} · fed ${Math.round((L.prosperity.slice(-1)[0] || 0) * 100)} %`);
      for (const g of ECON.GOODS) reply(`§7  ${g.padEnd(7)} stock ${String(Math.floor(L.stock[g])).padStart(4)}  price ${L.prices[g]} coin (${ECON.ITEM[g].replace("minecraft:", "")})`);
      reply(`§7  buy <good> <n> · sell <good> <n> · 1 emerald = ${ECON.COIN_PER_EMERALD} coin`);
      return;
    }
    if (!p) { reply("[CLOCK] buy / sell need a player"); return; }
    const good = a, n = Math.max(1, Math.floor(Number(b) || 1));
    const inv = p.getComponent("minecraft:inventory")?.container;
    if (!inv) { reply("§c[CLOCK] no inventory"); return; }
    if (cmd === "buy") {
      const q = ECON.quote(L, good, n);
      if (!q || q.n <= 0) { reply(`§c[MARKET] nothing to sell: ${good} (stock ${L.stock[good] ?? "?"})`); return; }
      let have = 0;
      for (let i = 0; i < inv.size; i++) { const it = inv.getItem(i); if (it && it.typeId === "minecraft:emerald") have += it.amount; }
      if (have < q.emeralds) { reply(`§c[MARKET] ${q.n} ${good} costs ${q.coin} coin = ${q.emeralds} emeralds; you carry ${have}`); return; }
      let left = q.emeralds;
      for (let i = 0; i < inv.size && left > 0; i++) {
        const it = inv.getItem(i);
        if (it && it.typeId === "minecraft:emerald") { const take = Math.min(left, it.amount); left -= take; if (it.amount - take > 0) { it.amount -= take; inv.setItem(i, it); } else inv.setItem(i, undefined); }
      }
      ECON.buy(L, good, q.n);
      let rest = q.n;
      while (rest > 0) { const k = Math.min(64, rest); inv.addItem(new ItemStack(ECON.ITEM[good], k)); rest -= k; }
      save();
      reply(`§a[MARKET] bought ${q.n} ${good} for ${q.emeralds} emeralds (${q.coin} coin); the town's treasury is ${Math.round(L.treasury)}`);
      return;
    }
    // sell: take the goods' items from the player, pay emeralds
    const item = ECON.ITEM[good];
    if (!item) { reply(`§c[MARKET] unknown good ${good}; goods: ${ECON.GOODS.join(", ")}`); return; }
    let carried = 0;
    for (let i = 0; i < inv.size; i++) { const it = inv.getItem(i); if (it && it.typeId === item) carried += it.amount; }
    const count = Math.min(n, carried);
    if (count <= 0) { reply(`§c[MARKET] you carry no ${good}`); return; }
    const r = ECON.sell(L, good, count);
    if (!r) { reply(`§c[MARKET] the town cannot pay for ${count} ${good} (treasury ${Math.round(L.treasury)})`); return; }
    let left = count;
    for (let i = 0; i < inv.size && left > 0; i++) {
      const it = inv.getItem(i);
      if (it && it.typeId === item) { const take = Math.min(left, it.amount); left -= take; if (it.amount - take > 0) { it.amount -= take; inv.setItem(i, it); } else inv.setItem(i, undefined); }
    }
    if (r.emeralds > 0) inv.addItem(new ItemStack("minecraft:emerald", r.emeralds));
    save();
    reply(`§a[MARKET] sold ${count} ${good} for ${r.coin} coin = ${r.emeralds} emeralds`);
    return;
  }
  if (cmd === "snapshot") {
    const name = (b || "").replace(/[^A-Za-z0-9_-]/g, "");
    if (a === "list") {
      const names = world.getDynamicPropertyIds().filter((k) => k.startsWith(SNAP) && k.endsWith(":n")).map((k) => k.slice(SNAP.length, -2));
      reply(`§e[CLOCK] snapshots: ${names.join(", ") || "(none)"}`); return;
    }
    if (!name || (a !== "save" && a !== "load")) { reply("§c[CLOCK] usage: snapshot save|load <name>  ·  snapshot list"); return; }
    if (a === "save") { const n = putText(SNAP + name, JSON.stringify(s)); reply(`§e[CLOCK] snapshot '${name}' saved (${n} chunk${n > 1 ? "s" : ""})`); return; }
    const raw = getText(SNAP + name);
    if (!raw) { reply(`§c[CLOCK] no snapshot '${name}'`); return; }
    try { JSON.parse(raw); } catch (e) { reply(`§c[CLOCK] snapshot '${name}' is broken (${String(e).slice(0, 60)}) — the town is left as it is`); return; }   // 1.3.228: never a fresh town over a broken snapshot
    for (const bb of s.buildings) if (bb.settled !== false) clearEntities(world.getDimension(bb.dim), bb);
    state = null;
    load(raw);                                                     // 1.3.228 (B2): the snapshot becomes the state; the next save writes its sections
    state.lastWorld = worldDays();
    for (const bb of state.buildings) {
      bb.pending = [];
      if (bb.settled !== false) clearEntities(world.getDimension(bb.dim), bb);
      for (let k = 0; k <= bb.stage; k++) bb.pending.push(k);
    }
    flushPending(); save(true);
    reply(`§e[CLOCK] snapshot '${name}' restored: village day ${state.simDays.toFixed(2)}, stages re-placed`);
    return;
  }
  reply("§e[CLOCK] status | plot [building] [rot] | plotat x y z [building] [rot] | village [seed] | villageat x z [seed] | " +
    "grow | decline on|off | immigrate [building] | log | market | buy <good> <n> | sell <good> <n> | step [days] | skip <days> | speed <x> | pause | resume | snapshot save|load|list <name> | why [name|CODE] | why icons on|off | statesize | savehold | shift [name] [template|default]");
});

console.warn(`[CIV-CLOCK] village clock loaded — ${Object.keys(BUILDINGS).length} staged building(s); /scriptevent pw:clock status`);


// ------------------------------------------------------------------------------------------------ CIV STATES (1004b, his 15:27 / 17:59)
// A civ (his word) never runs vanilla's villager AI: at its first beat (and once at every spawn) pw:civ_on strips the
// trade / stroll / dwelling / breeding / job groups (children can never take a profession; no emerald screen), then the
// clock owns every move: WALK (a lead), STAND (at a station, a counter, a site: still, looking about), IDLE (the square
// or the commons at dusk: a few short steps), HOME (inside the house at night: still). Purpose behind the inaction.
const CIV_STATES = ["stand", "idle", "home"];
const PACES = [20, 25, 35, 50];                                   // movement 0.20 / 0.25 (base, half speed) / 0.35 / 0.50
function applyPace(v, pace) {
  try { v.triggerEvent(`pw:pace_${PACES.includes(pace) ? pace : 25}`); if (v.hasTag("civ:watching")) { v.triggerEvent("pw:brisk_off"); v.triggerEvent("pw:brisk_on"); } } catch { /* left */ }
}
function civOn(v) {
  try { if (v.hasTag("civ:v220")) return false; v.triggerEvent("pw:civ_on"); v.addTag("civ:v220"); v.addTag("civ:state:stand"); const pc = load().pace; if (pc && pc !== 25) applyPace(v, pc); return true; } catch { return false; }
}
function civState(v, kind) {
  if (!CIV_STATES.includes(kind)) kind = "stand";
  try {
    if (v.hasTag(`civ:state:${kind}`)) return false;
    for (const t of v.getTags()) if (t.startsWith("civ:state:")) v.removeTag(t);
    v.addTag(`civ:state:${kind}`);
    v.triggerEvent(`pw:civ_${kind}`);
    return true;
  } catch { return false; }
}
/** the cell just inside a building's door (the night place; a keeper's fallback station) */
function insideDoor(b, def) {
  const [sx, , sz] = def.size;
  const door = def.door || [0, 0, Math.floor(sz / 2)];
  const [ox, oz] = rotXZ(2, door[2], sx, sz, b.rot);
  return { x: b.x + ox + 0.5, y: b.y + def.datum_y, z: b.z + oz + 0.5 };
}

// C2.1 (D-C541 / D-C542): the walkers' module reads the clock through these; the SCHEDULE below sends everyone somewhere
// by the time of day — work in the morning, the square at dusk, home at night — and the keepers' own beat sends them to
// their stations. Nothing teleports; a walker that cannot get there is counted (st.walkStuck).
WALK.initWalk({
  cellOf: KIT.cellOf, dirs4: DIRS4,
  plotsOf: (st) => plotsOf(load(), st), plotCount: (st) => plotsOf(load(), st).length,
  doorFront: (b) => { const def = BUILDINGS[b.family]; if (!def) return null; const fr = doorFront(b, def); return { x: fr.x, z: fr.z, y: b.y + def.datum_y }; },
  arrived: (v, w) => { const s = load(); const st = s.settlements.find((x) => x.id === w.stId); if (st) st.walkArrived = (st.walkArrived || 0) + 1; civState(v, "stand"); },
  civOn, civState, insideDoor,
  stuck: (v, w) => { const s = load(); if (walkTests.has(v.id)) { const r = walkTests.get(v.id); if (!r.end) { r.end = "stuck"; console.warn(`[CIV-WALKTEST] ${JSON.stringify({ end: r.name, how: "stuck", cause: w.cause || null, feet: w.feet || null, at: [Math.floor(v.location.x), Math.floor(v.location.y), Math.floor(v.location.z)], ticks: system.currentTick - r.t0, stalls: r.stalls })}`); try { v.removeTag("civ:walktest"); } catch { /* left */ } } } const st = s.settlements.find((x) => x.id === w.stId); if (st) { st.walkStuck = (st.walkStuck || 0) + 1; st.log.push(`day ${s.simDays.toFixed(0)}: ${v.nameTag || "a villager"} could not reach ${Math.floor(w.target.x)} ${Math.floor(w.target.z)} (${w.mode}${w.cause ? `, ${w.cause}` : ""}${w.feet ? `, standing in ${w.feet} at ${Math.floor(v.location.x)} ${Math.floor(v.location.y)} ${Math.floor(v.location.z)}` : ""})`); } },
  groundAt: (dim, x, z) => groundAt(dim, x, z),                      // 0.0.22: straight-line waypoints off the walk graph stand on the ground
  blockAt,                                                           // 1.3.228 (B1 hygiene): the guarded read
});
/** 1.3.228 (B1 hygiene): R5 (pw_fell_rules hasNaturalCanopy) reading through blockAt — the town's tree tests use this, never
 *  the raw read (a sleeping neighbour cell is "no leaf", never a thrown read) */
export function naturalCanopy(dim, logs, need = 3) { return hasNaturalCanopy(dim, logs, need, (x, y, z) => blockAt(dim, x, y, z)); }
WORKMOD.initWork({
  load, BUILDINGS, rotXZ, backOf, footprint, groundAt, isGround, TREE_LOG, fellTree, short,
  blockAt, topAt, naturalCanopy,                                     // 1.3.228 (B1 hygiene): the guarded reads
  treeOk: (dim, x, y, z, occ) => treeOk(dim, x, y, z, occ),          // 1.3.228 (B2 / BF10): only a real tree is felled
  treeKnown: (x, y, z) => treeKnown(x, y, z),
  tierIdx: (t) => TIER_IDX(t), QUARRY_R_MAX, QUARRY_D_MAX,
  plotsOf: (st) => plotsOf(load(), st), occupied: (st) => occupiedTest(load(), st),
  wake: (st, b) => {
    const s = load();
    let box = [b.x - 24, b.z - 24, b.x + 40, b.z + 40];
    // 0.0.25: the pit's own box (a site may lie beside the quarry, not behind it)
    if (b.pit && b.pit.site !== undefined) { try { const q = WORKMOD.pitOf(b, BUILDINGS[b.family], TIER_IDX(st.tier)); const R = b.pit.r + 2; box = [Math.min(box[0], q.cx - R), Math.min(box[1], q.cz - R), Math.max(box[2], q.cx + R), Math.max(box[3], q.cz + R)]; } catch { /* legacy */ } }
    try { ensureTicking(s, st, box, `${short(b)} #${b.id} work`); } catch { /* left */ }
  },
  deposited: (st, b, n, kind) => { (st.workToday = st.workToday || {})[b.id] = ((st.workToday || {})[b.id] || 0) + n; st.workTotal = (st.workTotal || 0) + n; },
  // D-C550: a skilled hand works faster (the census person's output factor in this trade)
  hands: (st, b) => {
    // 0.0.25g (the profiler): the settlement's villagers are read ONCE a tick for all its workshops (was once per workshop)
    const now = system.currentTick;
    let hc = handsCache.get(st.id);
    if (!hc || hc.tick !== now) {
      hc = { tick: now, by: new Map() };
      // 1.3.227 (profiled: the work beat 28..277 ms at city II): the census is indexed once (byId scanned the whole list per villager)
      const pm = st.people ? new Map(st.people.list.map((q) => [q.id, q])) : null;
      try {
        for (const v of HB.bodiesOf(st)) {                                  // 1.3.228 (B1): the shared bodies cache (was a query per work beat)
          if (v.hasTag("civ:keeper") || v.hasTag("civ:watching")) continue;
          const tag = v.getTags().find((x) => x.startsWith("civ:person:"));
          const p = tag && pm ? pm.get(Number(tag.slice(11))) : null;
          if (p && p.alive && typeof p.job === "number") { if (!hc.by.has(p.job)) hc.by.set(p.job, []); hc.by.get(p.job).push(v); }
        }
      } catch { /* unloaded */ }
      handsCache.set(st.id, hc);
    }
    return hc.by.get(b.id) || [];
  },
  // 1.3.228 (B3): the work pace = the skill curve (gated by the house level) x the mood tier (BF4; never below the floor)
  skill: (v, st, kind) => { try { const tag = v.getTags().find((t) => t.startsWith("civ:person:")); const p = tag && st.people ? PEOPLE.byId(st.people, Number(tag.slice(11))) : null; return p ? Math.max(0.05, PEOPLE.outputFactor(p, kind) * PEOPLE.moodFactor(p.mood)) : 1; } catch { return 1; } },
  act: (v, st) => noteAct(v, st),                                     // B3 / PE7: a real work act (the skill XP of the day)
  // 1.3.228 (B4): BF5 each hand's own shift; the rain ruling (shelter inside the workshop's door, half kept)
  onShift: (v, st) => bodyOnShift(v, st),
  wet: (st) => { try { return weatherIn(st.dim) !== "Clear"; } catch { return false; } },
  shelterOf: (b) => { const def = BUILDINGS[b.family]; return def ? insideDoor(b, def) : null; },
});
/** 1.3.228 (B4 / BF5): a body's census person (its civ:person tag, cached per body id: the tag never changes) */
const bodyPid = new Map();
function personOfBody(v, st) {
  let pid = bodyPid.get(v.id);
  if (pid === undefined) {
    try { const tag = v.getTags().find((t) => t.startsWith("civ:person:")); pid = tag ? Number(tag.slice(11)) : null; } catch { return null; }
    bodyPid.set(v.id, pid);
    if (bodyPid.size > 4096) bodyPid.clear();
  }
  return pid !== null && st.people ? PEOPLE.byId(st.people, pid) || null : null;
}
/** BF5: is this body on its own shift now (a body with no census person: the town's old hours) */
function bodyOnShift(v, st, tod = null) {
  let t = tod;
  if (t === null) { try { t = world.getTimeOfDay(); } catch { return false; } }
  const p = personOfBody(v, st);
  if (!p) return t >= SCHED.work[0] && t < SCHED.work[1];
  return shiftNow(load(), st, p, t, worldDay()).slot === "W";
}
KEYS.initKeys({ load, blockAt });                                   // 1.3.228 (B1 hygiene): blockAt
WATCH.initWatch({
  load, blockAt, kitHAt: (street, t) => street.H[t - street.tmin], cellOf: KIT.cellOf,
  stOf: (id) => load().settlements.find((x) => x.id === id),
  personOf: (v, st) => { try { const tag = v.getTags().find((x) => x.startsWith("civ:person:")); return tag && st.people ? PEOPLE.byId(st.people, Number(tag.slice(11))) : null; } catch { return null; } },
  keyOf: (st, pid) => KEYS.keyOf(st, pid), slideCover: (b, to) => KEYS.slideCover(b, to),
  onShift: (p, st, tod) => shiftNow(load(), st, p, tod, worldDay()).slot === "W",   // 1.3.228 (B4 / BF5): night / day templates
  inInfluence: (st, x, z) => inInfluence(st, x, z),                                     // 1.3.228 (B10): the rally's reach
  grown: (p) => { try { return PEOPLE.stage(p, Math.floor(load().simDays)) === "adult"; } catch { return false; } },
});
// 1.3.228 (B1 / BF1): the settlements' villager bodies are read ONCE per 20 ticks (heartbeat slot 10) for every reader
HB.bodiesFrom(() => { try { return load().settlements; } catch { return []; } });
const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };          // 1.3.228 (B4): only for bodies with no census person; people follow PEOPLE.SHIFT
// 1.3.228 (B4 / PE2): the inn stays (memory): "st:pid" -> { acc, last }; the pass adds the ticks since the last pass (at most
// INN.stepMax) and gives a mood point per INN.per ticks there
const innAcc = new Map();
function innStay(st, p) {
  const k = `${st.id}:${p.id}`, now = system.currentTick, c = innAcc.get(k) || { acc: 0, last: now - 100 };
  const r = PEOPLE.innStep(c.acc, now - c.last, p.mood ?? 50);
  innAcc.set(k, { acc: r.acc, last: now });
  if (innAcc.size > 4096) innAcc.clear();
  if (r.gain > 0) p.mood = Math.min(100, (p.mood ?? 50) + r.gain);
  return r.gain;
}
// 1.3.228 (B4 / rain ruling): settlement id -> { n: passes in the town's work hours, wet: of them wet } (memory; read and
// cleared by the day's production)
const wetLog = new Map();
// 1.3.228 (B4 / BF5 gate signal): the walk starts of each schedule pass from tod 10,000 to 13,000 (the end of the work day,
// now spread by the offsets and the walk home) and the pass's shift picture; one [CIV-SHIFT] line a town a world day
const shiftSeen = new Map();                                             // settlement id -> { day, starts: [[tod, n]], said }
function shiftDiag(st, tod, wday, sends, slotT) {
  let c = shiftSeen.get(st.id);
  if (!c || c.day !== wday) shiftSeen.set(st.id, (c = { day: wday, starts: [], said: false }));
  if (tod >= 10000 && tod < 13000) c.starts.push([tod, sends]);
  c.last = slotT;
  diagOf(st).shift = { day: wday, tod, ...slotT };
  if (!c.said && tod >= 13000) {
    c.said = true;
    const beats = c.starts.filter(([, n]) => n > 0).length;
    console.warn(`[CIV-SHIFT] ${JSON.stringify({ st: st.id, day: wday, startBeats: beats, starts: c.starts, now: slotT, wet: Math.round(wetShareOf(st) * 100) / 100, inn: diagOf(st).inn || 0 })}`);
  }
}
function wetShareOf(st, clear = false) {
  const w = wetLog.get(st.id);
  if (clear) wetLog.delete(st.id);
  return w && w.n ? w.wet / w.n : 0;
}
const bodiesNow = new Map();
const handsCache = new Map();
const SENDS_PER_BEAT = 6;                                      // 0.0.25g: settlement id -> { tick, by: workshop id -> villagers }                                       // 0.0.25: settlement id -> the person ids with a body this beat
// ---- 0.0.25 THE WALK TEST: chosen walks, traced (the harness's instrument; nothing in normal play calls it)
const walkTests = new Map();                                       // villager id -> { name, target, t0, end, stalls }
let walkTestTimer = null;
function blockId(dim, x, y, z) { const b = blockAt(dim, x, y, z); return b ? b.typeId.replace("minecraft:", "").replace("pw:", "") : "?"; }   // 1.3.228: guarded read
function walkTest(s, st, n) {
  const dim = world.getDimension(st.dim);
  let vs = [];
  try { vs = dim.getEntities({ tags: [`civ:settlement:${st.id}`], type: VILLAGER_ID }); } catch { vs = []; }
  vs = vs.filter((v) => !v.hasTag("civ:keeper") && !v.hasTag("civ:watching") && !v.hasTag("civ:working"));
  const fronts = plotsOf(s, st).filter((b) => b.stage >= 4).map((b) => { const def = BUILDINGS[b.family]; const fr = doorFront(b, def); return { x: fr.x + 0.5, z: fr.z + 0.5, y: b.y + def.datum_y, what: `${short(b)} #${b.id}` }; });
  const sq = { x: st.square.x + 6.5, z: st.square.z + 6.5, y: st.square.y + 1, what: "the square" };
  const now = system.currentTick;
  for (let i = 0; i < Math.min(n, vs.length); i++) {
    const v = vs[i];
    // the walks: the square, the farthest door, a door on another street — three kinds of leg
    let tgt = sq;
    if (i % 3 === 1 && fronts.length) tgt = fronts.slice().sort((p, q) => Math.hypot(q.x - v.location.x, q.z - v.location.z) - Math.hypot(p.x - v.location.x, p.z - v.location.z))[0];
    if (i % 3 === 2 && fronts.length) tgt = fronts[(i * 7) % fronts.length];
    try { v.addTag("civ:walktest"); } catch { continue; }
    WALK.cancel(v);
    const mode = WALK.send(v, st, tgt);
    walkTests.set(v.id, { name: v.nameTag || "?", target: tgt, t0: now, end: null, stalls: 0, mode, from: [Math.floor(v.location.x), Math.floor(v.location.y), Math.floor(v.location.z)] });
    console.warn(`[CIV-WALKTEST] ${JSON.stringify({ start: v.nameTag || "?", from: walkTests.get(v.id).from, to: [Math.floor(tgt.x), Math.floor(tgt.y), Math.floor(tgt.z)], what: tgt.what, mode })}`);
  }
  // 1.3.228 (B1 / BF1): the instrument is a heartbeat slot (13 of 20) while a test runs, unregistered when it ends
  if (walkTestTimer !== null) HB.unregister("walktest");
  walkTestTimer = HB.register("walktest", { fn: () => {
    const t = system.currentTick;
    for (const [vid, r] of walkTests) {
      let v; try { v = world.getEntity(vid); } catch { v = undefined; }
      if (!v) { if (!r.end) { r.end = "gone"; } continue; }
      if (r.end) continue;
      const pk = WALK.peek(v), L = v.location, fx = Math.floor(L.x), fy = Math.floor(L.y), fz = Math.floor(L.z);
      if (!pk) { r.end = Math.hypot(L.x - r.target.x, L.z - r.target.z) <= 3 ? "arrived" : "ended"; console.warn(`[CIV-WALKTEST] ${JSON.stringify({ end: r.name, how: r.end, at: [fx, fy, fz], ticks: t - r.t0, stalls: r.stalls })}`); try { v.removeTag("civ:walktest"); } catch { /* left */ } continue; }
      if ((t - r.t0) % 40 < 20) console.warn(`[CIV-WALKTRACE] ${JSON.stringify({ n: r.name, t: t - r.t0, at: [Math.round(L.x * 10) / 10, Math.round(L.y * 10) / 10, Math.round(L.z * 10) / 10], feet: blockId(v.dimension, fx, fy, fz), below: blockId(v.dimension, fx, fy - 1, fz), i: pk.i, of: pk.n, lead: pk.lead, d: pk.lead ? Math.round(Math.hypot(pk.lead[0] - L.x, pk.lead[2] - L.z) * 10) / 10 : null, idle: pk.idle, mode: pk.mode })}`);
      // a stall (no progress for 60 ticks): the blocks around the walker (x/z +-2, feet-1..feet+2) and at its next waypoints
      if (pk.idle >= 60 && (!r.stallAt || t - r.stallAt >= 200)) {
        r.stallAt = t; r.stalls++;
        const around = [];
        for (let dy = -1; dy <= 2; dy++) { const rows = []; for (let dz = -2; dz <= 2; dz++) { const row = []; for (let dx = -2; dx <= 2; dx++) row.push(blockId(v.dimension, fx + dx, fy + dy, fz + dz)); rows.push(row.join("|")); } around.push(`y${fy + dy}: ${rows.join(" / ")}`); }
        const wps = pk.next.map(([x, z, y]) => [x, z, y, blockId(v.dimension, x, y - 1, z), blockId(v.dimension, x, y, z), blockId(v.dimension, x, y + 1, z)]);
        // the leads near the walker (its own and any other walker's): does it follow the wrong carrot?
        let leads = [];
        try { leads = v.dimension.getEntities({ type: "pw:lead", location: v.location, maxDistance: 16 }).map((e) => { const own = e.getTags().includes(`civ:lead:${v.id}`); return [own ? "own" : "other", Math.round(Math.hypot(e.location.x - L.x, e.location.z - L.z) * 10) / 10]; }).sort((p, q) => p[1] - q[1]).slice(0, 4); } catch { leads = []; }
        console.warn(`[CIV-WALKSTALL] ${JSON.stringify({ n: r.name, t: t - r.t0, at: [fx, fy, fz], lead: pk.lead, i: pk.i, of: pk.n, mode: pk.mode, wps, leads })}`);
        for (const line of around) console.warn(`[CIV-WALKSTALL] ${r.name} ${line}`);
      }
    }
    if ([...walkTests.values()].every((r) => r.end) || t - Math.min(...[...walkTests.values()].map((r) => r.t0)) > 2400) {
      const sum = { arrived: 0, stuck: 0, ended: 0, gone: 0, open: 0 };
      for (const [vid, r] of walkTests) { sum[r.end || "open"] = (sum[r.end || "open"] || 0) + 1; try { const v = world.getEntity(vid); if (v) { v.removeTag("civ:walktest"); WALK.cancel(v); } } catch { /* left */ } }
      console.warn(`[CIV-WALKTEST] ${JSON.stringify({ done: sum })}`);
      walkTests.clear(); HB.unregister("walktest"); walkTestTimer = null;
    }
  } });
}
/** 1.3.224 (his 16:50: "all standing around together, mostly the well"): the old goal was the square's centre + 6.5 — INSIDE
 *  the well's footprint — for every jobless or site-less person in work hours and for EVERYONE at dusk. Now a person
 *  gets ITS OWN cell on a ring around the square (inset 1 from the edge: 36 cells, clear of the well and of the market
 *  stall at the corner), stable by person and rotating through the day. */
const SQUARE_RING = (() => { const c = []; for (let i = 1; i <= 10; i++) { c.push([i, 1]); c.push([i, 10]); } for (let j = 2; j <= 9; j++) { c.push([1, j]); c.push([10, j]); } return c.filter(([i, j]) => !(i <= 2 && j <= 2)); })();
function squareSlot(st, n, salt = 0) {
  const c = SQUARE_RING[(((n * 7 + salt * 13) % SQUARE_RING.length) + SQUARE_RING.length) % SQUARE_RING.length];
  return { x: st.square.x + c[0] + 0.5, z: st.square.z + c[1] + 0.5, y: st.square.y + 1 };
}
const idNum = (v, person) => person ? person.id : [...String(v.id)].reduce((a, ch) => (a * 31 + ch.charCodeAt(0)) >>> 0, 7);
/** where a person without work to do spends the hour: the home's yard, its own place on the square, the neighbourhood's
 *  centre, or a finished shop's front (browsing) — chosen by person and the time of day, so the town spreads out */
function leisureGoal(s, st, v, person, homeB, tod, front, centreB, dusk, ctx = null) {
  const n = idNum(v, person);
  // 1.3.228 (B4 / PE2): an unhappy body (mood < INN.mood) goes INTO the inn first, at dusk and in idle hours, while it has
  // room (INN.perStation a station); every INN.per ticks there is a mood point (the schedule pass counts the stay)
  const ig = innGoal(person, ctx);
  if (ig) return ig;
  const phase = Math.floor(tod / PEOPLE.LEISURE.phase);
  // 1.3.231 (CIV-PEOPLE; his 02:44 screenshot: civs bunched around the well in daylight): the square was one of 2..4 EQUAL
  // options at every hour and a centre meant its WELL's front. Now: weighted kinds (PEOPLE.leisureWeights) — home, the
  // workplace, a shop, the neighbourhood centre's SHOPS (never its well), a park bench, the inn; the square only at the
  // midday market and at dusk
  const C = [], at = (b) => (b ? front(b) : null), byId = (id) => (ctx && ctx.byId ? ctx.byId.get(id) : buildingById(s, id));
  const live = (b) => b && b.stage >= 4 && !b.closed;
  { const f = at(homeB); if (f) C.push({ kind: "home", at: f }); }
  if (person && typeof person.job === "number") { const jb = byId(person.job); const f = live(jb) ? at(jb) : null; if (f) C.push({ kind: "work", at: f }); }
  if (st.square) C.push({ kind: "square", at: squareSlot(st, n, phase) });
  if (centreB) {
    const c = (st.centres || []).find((x) => x.well === centreB.id);
    const cs = (c ? c.shops : []).map(byId).filter(live);
    const f = cs.length ? at(cs[(n + phase) % cs.length]) : null; if (f) C.push({ kind: "centre", at: f });
  }
  const fin = ctx ? ctx.fin : plotsOf(s, st).filter((b) => b.stage >= 4 && !b.closed && !b.palace && SHOPS.includes(short(b)));
  if (fin.length) { const f = at(fin[(n + phase) % fin.length]); if (f) C.push({ kind: "shop", at: f }); }
  { const inn = ctx ? ctx.inn : plotsOf(s, st).find((b) => short(b) === "inn" && b.stage >= 4 && !b.closed); const f = at(inn); if (f) C.push({ kind: "inn", at: f }); }
  { const f = PEOPLE.parkSpot(st.park, n + phase); if (f) C.push({ kind: "park", at: f }); }
  const c = PEOPLE.leisurePick(C, n, phase, PEOPLE.leisureWeights({ dusk, tod, housed: !!homeB }));
  return c ? { ...c.at, mode: "idle", leisure: c.kind } : null;
}
/** 1.3.231 (CIV-PEOPLE): where a body WITHOUT a home rests (was: the square's ring — all night, and all day for the night
 *  watch): a guest bed at the inn (tonight's guests: PEOPLE.innGuests, billed by the shop beat), else a shelter — its own
 *  workplace, the town hall, a chapel / church; null when none stands (the caller keeps the square as the last resort) */
function restGoal(s, st, person, jobB, ctx) {
  const inn = ctx ? ctx.inn : null;
  if (person && inn && BUILDINGS[inn.family]) {
    if (!ctx.guests) ctx.guests = new Set(PEOPLE.innGuests(st.people ? st.people.list : [], PEOPLE.bedsOf(BUILDINGS[inn.family].dir), inn.id));
    if (ctx.guests.has(person.id)) return { ...insideDoor(inn, BUILDINGS[inn.family]), mode: "home", lodge: inn.id };
  }
  const live = (b) => b && b.stage >= 4 && !b.closed && BUILDINGS[b.family];
  if (live(jobB) && short(jobB) !== "inn") return { ...insideDoor(jobB, BUILDINGS[jobB.family]), mode: "home", shelter: jobB.id };
  if (ctx && ctx.shelter === undefined) ctx.shelter = plotsOf(s, st).filter((b) => live(b) && ["town_hall", "chapel", "church"].includes(short(b))).sort((a, b) => a.id - b.id)[0] || null;
  const sh = ctx ? ctx.shelter : null;
  return sh ? { ...insideDoor(sh, BUILDINGS[sh.family]), mode: "home", shelter: sh.id } : null;
}
// 1.3.231 (INN24): the rota of an inn's staff (PEOPLE.innRota), once per settlement + inn per tick (memory)
const innRotaCache = new Map();
function innRotaOf(s, st, innId) {
  const k = `${st.id}:${innId}`, now = system.currentTick, c = innRotaCache.get(k);
  if (c && c.tick === now) return c.rota;
  const rota = PEOPLE.innRota(PEOPLE.innStaff(census(st), innId, Math.floor(s.simDays)));
  innRotaCache.set(k, { tick: now, rota });
  if (innRotaCache.size > 256) innRotaCache.clear();
  return rota;
}
/** B4 (PE2): the inn for an unhappy person (inside its door), or null (content, no inn, the inn full) */
function innGoal(person, ctx) {
  if (!ctx || !ctx.inn || !PEOPLE.wantsInn(person) || (ctx.innSent || 0) >= (ctx.innCap || 0)) return null;
  const def = BUILDINGS[ctx.inn.family];
  if (!def) return null;
  ctx.innSent = (ctx.innSent || 0) + 1;
  return { ...insideDoor(ctx.inn, def), mode: "idle", inn: ctx.inn.id };
}
/** 1.3.227 (the profiled gate 226-2 world, city II: the schedule beat took 140..781 ms at once — every civ's goal scanned
 *  the building list several times and, at market hours, the whole census to find its household's shopper): what the
 *  goals read is gathered ONCE per settlement per pass — buildings by id, the plots, the labour sites, the open shops and
 *  inn, the weather, each household's shopper — and the fronts and centres are cached for the pass. */
function schedCtx(s, st, tod) {
  const byId = new Map(s.buildings.map((b) => [b.id, b]));
  const plots = plotsOf(s, st);
  const day = Math.floor(s.simDays);
  const ctx = {
    byId, plots, day,
    sites: plots.filter((b) => b.labor && !b.closed),
    fin: plots.filter((b) => b.stage >= 4 && !b.closed && !b.palace && SHOPS.includes(short(b))),
    inn: plots.find((b) => short(b) === "inn" && b.stage >= 4 && !b.closed) || null,
    wet: (() => { try { return weatherIn(st.dim) !== "Clear"; } catch { return false; } })(),
    shopperOf: null, fronts: new Map(), centres: new Map(),
    wday: worldDay(), innSent: 0, innCap: 0, slot: null,                   // 1.3.228 (B4): BF5's week day, PE2's inn room
  };
  if (ctx.inn) ctx.innCap = PEOPLE.INN.perStation * ((BUILDINGS[ctx.inn.family] || {}).work || 1);
  if (tod >= MARKET[0] && tod < MARKET[1] && st.people) {
    // the household's SHOPPER: its lowest-id grown, living member with a body who keeps no shop and stands no watch / site
    const bodies = bodiesNow.get(st.id);
    ctx.shopperOf = new Map();
    for (const q of PEOPLE.alive(census(st)).sort((a2, b2) => a2.id - b2.id)) {
      if (!q.home || ctx.shopperOf.has(q.home)) continue;
      if (q.keeper || q.job === "watch" || q.job === "builders" || PEOPLE.stage(q, day) === "child") continue;
      if (bodies && !bodies.has(q.id)) continue;
      ctx.shopperOf.set(q.home, q.id);
    }
  }
  ctx.people = st.people ? new Map(st.people.list.map((q) => [q.id, q])) : new Map();
  return ctx;
}
// 1.3.228 (B4 / PE1): VARIED WORK BEATS — a station worker (and a keeper, in the shop beat) takes one beat a 600-tick window
// (PEOPLE.beatOf: the main task 8, near the station 5, a second spot 5, the store 6, the door 7) and stands where it puts
// him, facing the trade's look-at block (PEOPLE.LOOK: the oven, the smoker, the anvil, the lectern, barrels, shelves —
// found among the template's own blocks); the spots of a building are made once (memory)
const spotsCache = new Map();                                             // building id -> { fam, rot, station, sp }
export function workSpotsOf(b) {
  const def = b && BUILDINGS[b.family];
  if (!def) return null;
  const c = spotsCache.get(b.id);
  if (c && c.fam === b.family && c.rot === b.rot && c.station === b.station) return c.sp;
  const toW = (q) => { const [ox, oz] = rotXZ(q.x, q.z, def.size[0], def.size[2], b.rot); return { x: b.x + ox, y: b.y + q.y, z: b.z + oz }; };
  const seen = new Set(), blocks = [];
  for (const e of (def.dir || []).concat(def.chests || [])) { const k = `${e[0]},${e[1]},${e[2]}`; if (!seen.has(k)) { seen.add(k); blocks.push(e); } }
  const L = PEOPLE.lookCells(short(b), blocks);
  const inD = insideDoor(b, def);
  const store = def.chests && def.chests.length ? toW({ x: def.chests[0][0], y: def.chests[0][1], z: def.chests[0][2] }) : null;
  const sp = { station: b.station || inD, main: L.main.map(toW), second: L.second.map(toW), store, door: { in: inD, out: placeOf(b) } };
  spotsCache.set(b.id, { fam: b.family, rot: b.rot, station: b.station, sp });
  if (spotsCache.size > 4096) spotsCache.clear();
  return sp;
}
/** 1.3.228 (B8 / WE2 + WE3): a carter's goal — his loads (ECON.pickHaul: priority + age - sqrt(distance), same-destination
 *  loads batched up to 1 + rank) are fetched at the store's door and carried to the site's door; each load delivered adds
 *  HAUL_BONUS labour to the site (a small speed-up; nothing waits for him). Memory: CARTS (vid -> the job). */
const CARTS = new Map();
function carterGoal(s, st, v, person, front) {
  let job = CARTS.get(v.id);
  if (!job) {
    const q = st.haul || [];
    if (!q.length) return null;
    const rank = PEOPLE.rankOf(person, "carter");
    const batch = rank === "master" ? 3 : rank === "journeyman" ? 2 : 1;
    const withAt = q.map((h) => { const fb = buildingById(s, h.from); return { ...h, fromAt: fb ? { x: fb.x, z: fb.z } : { x: v.location.x, z: v.location.z } }; });
    const r = ECON.pickHaul(withAt, { x: v.location.x, z: v.location.z }, batch);
    if (!r.picks.length) return null;
    st.haul = r.queue.map(({ fromAt, ...h }) => h);
    job = { picks: r.picks.map(({ fromAt, ...h }) => h), phase: "load", i: 0 };
    CARTS.set(v.id, job);
  }
  const cur = job.picks[job.i] || job.picks[0];
  const target = buildingById(s, job.phase === "load" ? cur.from : cur.to);
  if (!target || (job.phase === "carry" && !target.labor)) { CARTS.delete(v.id); return null; }
  const f = target.station && job.phase === "load" ? target.station : front(target);
  if (!f) { CARTS.delete(v.id); return null; }
  if (Math.hypot(v.location.x - f.x, v.location.z - f.z) <= 3) {
    if (job.phase === "load") { job.i++; if (job.i >= job.picks.length) { job.phase = "carry"; job.i = 0; } }
    else {
      target.labor.done += HAUL_BONUS * job.picks.length;
      const d = diagOf(st); d.haul = d.haul && d.haul.day === Math.floor(s.simDays) ? d.haul : { day: Math.floor(s.simDays), loads: 0, trips: 0 };
      d.haul.loads += job.picks.length; d.haul.trips++;
      try { PEOPLE.learn(person, "carter", 1, Math.floor(s.simDays)); } catch { /* left */ }
      CARTS.delete(v.id);
      return null;
    }
  }
  return { x: f.x, y: f.y, z: f.z };
}
/** PE1: a station worker's goal now: the beat's stand, with what he faces (g.look) */
function workGoal(jobB, person, front) {
  const sp = workSpotsOf(jobB);
  if (!sp) return jobB.station || front(jobB);
  const w = PEOPLE.workSpot(PEOPLE.beatOf(person.id, system.currentTick), sp, person.id);
  return w ? { ...w.stand, look: w.look, beat: w.beat, mode: "stand" } : (jobB.station || front(jobB));
}
function goalFor(s, st, v, tod, ctx = schedCtx(s, st, tod)) {
  ctx.kind = null; ctx.noShop = false; ctx.builderIdle = false;         // 1.3.228 (B2 / BF3): what the goal is, for the why code
  ctx.slot = null; ctx.homeFar = false; ctx.shOff = false; ctx.shHome = false;   // 1.3.228 (B4): the person's shift slot, PE5's complaint
  const tags = v.getTags();
  const pid = tags.find((t) => t.startsWith("civ:person:")), home = tags.find((t) => t.startsWith("civ:home:"));
  const homeB = home ? ctx.byId.get(Number(home.slice(9))) || null : null;
  const person = pid ? ctx.people.get(Number(pid.slice(11))) || null : null;
  const jobB = person && person.job ? ctx.byId.get(person.job) || null : null;
  const front = (b) => {
    if (!b) return null;
    if (ctx.fronts.has(b.id)) return ctx.fronts.get(b.id);
    const def = BUILDINGS[b.family]; let f = null;
    if (def) { const fr = doorFront(b, def); f = { x: fr.x + 0.5, z: fr.z + 0.5, y: b.y + def.datum_y }; }
    ctx.fronts.set(b.id, f);
    return f;
  };
  const hk = homeB ? homeB.id : -1;
  if (!ctx.centres.has(hk)) ctx.centres.set(hk, centreOf(s, st, homeB));
  const centreB = ctx.centres.get(hk);                                // B2: the neighbourhood's own market, when its street has one
  // 1.3.224: rain sends everyone without a roof over their work home (vanilla's move_indoors is gone since 1004b)
  const wet = ctx.wet;
  const homeInside = homeB && BUILDINGS[homeB.family] ? { ...insideDoor(homeB, BUILDINGS[homeB.family]), mode: "home" } : null;
  // 1.3.228 (B4 / BF5): the person's OWN shift — the template from the job, the id's offset (-200..+200 ticks), the week's
  // days off (a day off turns work into idle) and PE5's walk home (he leaves to be home when his rest block starts); a body
  // with no census person keeps the town's old hours
  const child = !!person && PEOPLE.stage(person, ctx.day) === "child";
  const sh = person ? shiftNow(s, st, person, tod, ctx.wday, child) : null;
  const slot = sh ? sh.slot : (tod >= SCHED.work[0] && tod < SCHED.work[1] ? "W" : tod >= SCHED.dusk[0] && tod < SCHED.dusk[1] ? "M" : "R");
  ctx.slot = slot; ctx.shOff = !!(sh && sh.off); ctx.shHome = !!(sh && sh.home);
  // B10 (WP4 + his 10:15): the alarm bell — children and elders go home; grown civs go home too unless the watch is
  // overwhelmed (then the rally beat holds them, tagged civ:rally, and this pass skips them)
  if (homeInside && person && !(person.job === "watch") && WATCH.alarmOn(st.id)) {
    const stg = PEOPLE.stage(person, ctx.day);
    if (stg === "child" || stg === "elder" || !WATCH.overwhelmed(st.id)) { ctx.kind = "alarm"; return homeInside; }
  }
  if (slot === "W" || slot === "I") {
    if (slot === "W" && person && person.job === "fisher") {                // 1.3.225: to his shore (in rain too: fishermen fish in the rain)
      const sp = fishSpotOf(st, person);
      if (sp) { ctx.kind = "fish"; return { x: sp.x + 0.5, y: sp.y, z: sp.z + 0.5, fish: sp }; }
    }
    if (slot === "W" && person && person.job === "carter") {               // 1.3.228 (B8 / WE2): load at the store, carry to the site
      const g = carterGoal(s, st, v, person, front);
      if (g) { ctx.kind = "job"; return g; }
    }
    if (slot === "W" && person && person.job === "surveyor") {
      const task = surveyorTask(st);
      if (task) { const g = groundAt(world.getDimension(st.dim), task.x, task.z); ctx.kind = "survey"; return { x: task.x + 0.5, z: task.z + 0.5, y: (g ?? 64) + 1, survey: task }; }
    }
    // C2.4: midday — the household's shopper (no post, no station) goes to the counter it trusts
    // (run 0.0.23: no purchase at all — every grown person held a station, and only the jobless shopped) the household's
    // SHOPPER is its first grown member who keeps no shop and stands no watch; they leave the work for the counter at midday
    const shopperId = person && person.home && ctx.shopperOf ? ctx.shopperOf.get(person.home) : undefined;
    if (shopperId !== undefined && shopperId === person.id) {
      const day = Math.floor(s.simDays);
      const done = homesToday(st, day).has(person.home);                  // 1.3.228 (B2 / WE14): today's homes in memory
      if (!done) {
        const shopB = shopFor(s, st, v, person, homeB);
        const dg = diagOf(st);
        const mt = (dg.marketTry = dg.marketTry && dg.marketTry.day === day ? dg.marketTry : { day, goals: 0, noShop: 0, shoppers: new Set() });
        if (!shopB) { mt.noShop++; ctx.noShop = true; }                     // 1.3.228 (B2 / BF3): the why code NO_STOCK
        if (shopB) { const f = shopB.station || front(shopB); if (f) { mt.goals++; mt.shoppers.add(person.id); ctx.kind = "shop"; return { ...f, buy: shopB.id, person: person.id }; } }
      }
    }
    if (slot === "W" && person && (person.job === "builders" || !person.job)) {
      // C2.3: the nearest site with the fewest builders
      const sites = ctx.sites;
      if (sites.length) {
        let best = null, bs = Infinity;
        for (const b of sites) { if (!b.labor) continue; const f = front(b); if (!f) continue; const sc = Math.hypot(v.location.x - f.x, v.location.z - f.z) + 40 * (b.labor.crew || 0); if (sc < bs) { bs = sc; best = b; } }
        if (best) {
          best.labor.crew = (best.labor.crew || 0) + 1;
          // 1.3.228 (B4, his rain ruling): builders SHELTER (at home) and keep HALF their output: the pass credits the site
          if (wet && homeInside) { ctx.kind = "shelter"; return { ...homeInside, shelterSite: best.id }; }
          ctx.kind = "site"; return { ...front(best), site: best.id };
        }
      }
      if (person.job === "builders" || !jobB) ctx.builderIdle = true;          // 1.3.228 (B2 / BF3): no labour site for him
    }
    if (slot === "W" && jobB) { ctx.kind = "job"; ctx.homeFar = homeFarOf(s, st, person); return workGoal(jobB, person, front); }   // B4 (PE1): the beat's spot
    if (slot === "W" && person && person.job && typeof person.job === "string") ctx.homeFar = homeFarOf(s, st, person);
    if (wet && homeInside && !(PEOPLE.wantsInn(person) && ctx.inn)) { ctx.kind = "rain"; return homeInside; }
    ctx.kind = "leisure";
    return leisureGoal(s, st, v, person, homeB, tod, front, centreB, false, ctx) || homeInside || restGoal(s, st, person, jobB, ctx);   // 1.3.231: no home, no idle place -> a shelter
  }
  ctx.kind = "off";
  if (slot === "M") {
    if (wet && homeInside) return innGoal(person, ctx) || homeInside;
    // B11 (WP5 + his 10:15): a festival evening — everyone to their place in the ring on the square
    if (ctx.fest === undefined) ctx.fest = GUEST.festivalNow(s, st);
    const fg = ctx.fest ? GUEST.festGoal(s, st, person, ctx.fest) : null;
    if (fg) { ctx.kind = "leisure"; return fg; }
    return leisureGoal(s, st, v, person, homeB, tod, front, centreB, true, ctx) || homeInside;
  }
  // night: INSIDE the home (1004b: vanilla's move_indoors is gone; the civ stands in its house, still)
  if (homeInside) return homeInside;
  // 1.3.231 (CIV-PEOPLE): no home -> the inn's guest bed or a shelter; the square's ring only when no building stands
  const rg = restGoal(s, st, person, jobB, ctx);
  if (rg) { ctx.kind = rg.lodge !== undefined ? "lodge" : "shelter-night"; return rg; }
  return st.square ? { ...squareSlot(st, idNum(v, person)), mode: "idle" } : null;
}
// 1.3.227: the schedule is a JOB — a pass starts every 100 ticks when the last one has finished, and gives the tick back
// after each civ (the engine runs as many steps as its job budget allows), so a city's civs no longer land in one tick
// ------------------------------------------------------------------------------------------------ WHY-IDLE (1.3.228 B2 / BF3)
// Every schedule pass gives each person ONE reason code (PEOPLE.whyOf: home > food > site > route > the work module's own
// reason > busy / rain / no site / no job): whyNow (memory) per person, and the settlement's tally st.why = {code: n} (saved,
// at most 16 keys, ~200 chars). `pw:clock why [name|CODE]` reads them; [CIV-WHY] is written at every tier change.
// ICONS (off by default — his villagers' names stay clean): `pw:clock why icons on` adds a short suffix to the nameTag of
// bodies within WHY_ICON_R of a player: "Ada §8[§cno home§8]" (Script API 2.3.0 has no TextPrimitive: a one-line suffix,
// the matrix's fallback; written only on change, and stripped from every name when icons are off).
const whyNow = new Map();                                            // "stId:pid" -> code
const whyTierSaid = new Map();                                       // settlement id -> the tier its tally was last printed at
const WHY_ICON_R = 24;
const WHY_LABEL = { ALARM: "§cthe bell!", NO_HOME: "§cno home", NO_JOB: "§7no job", NO_STOCK: "§6no food to buy", NO_FACE: "§7nothing to cut", UNREACHABLE: "§ccan't get there",
  NO_ROUTE: "§eno route yet", SLOTS_FULL: "§ewaiting to walk", STOCK_FULL: "§6store full", RAIN: "§9rain", NO_SITE: "§7no site", "—": "§8?",
  SHELTER: "§9sheltering", HOME_FAR: "§6home too far" };                  // 1.3.228 (B4)
const ICON_TAG = / §8\[[^\]]*§8\]$/;
/** a nameTag without the why icon */
export function plainName(tag) { return (tag || "").split("\n")[0].replace(ICON_TAG, "").replace(/§./g, ""); }   // B5: a bubble's first line
function whyLabel(code) { return code && code.startsWith("SITE_WAITS:") ? `§6waits: ${code.slice(11)}` : WHY_LABEL[code] || null; }
function setWhyIcon(v, code) {
  if (VOICE.bubbling(v.id)) return;                                     // B5: a line is up — the icon waits
  let tag; try { tag = v.nameTag || ""; } catch { return; }
  const base = plainName(tag);
  if (!base) return;
  const lab = whyLabel(code);
  const want = lab ? `${base} §8[${lab}§8]` : base;
  if (tag !== want) { try { v.nameTag = want; } catch { /* left */ } }
}
/** the material the town's waiting sites lack most (b.waiting = { <material>: n, blocks }) */
function siteWaitGood(s, st) {
  const need = {};
  for (const b of plotsOf(s, st)) { if (!b.waiting) continue; for (const [m, n] of Object.entries(b.waiting)) if (m !== "blocks" && typeof n === "number") need[m] = (need[m] || 0) + n; }
  let best = null;
  for (const [m, n] of Object.entries(need)) if (n > 0 && (!best || n > need[best])) best = m;
  return best;
}
let schedBusy = false;
HB.register("schedule", { fn: () => {                                      // 1.3.228 (B1 / BF1): the starter is heartbeat slot 19 of 100
  if (schedBusy) return;
  schedBusy = true;
  try { system.runJob(scheduleJob()); } catch (e) { schedBusy = false; console.warn(`[CIV-CLOCK] schedule job: ${e}`); }
} });
function* scheduleJob() {
 let t0 = Date.now();
 const lap = () => { PROF.schedule = (PROF.schedule || 0) + Date.now() - t0; };
 try {
  const s = load();
  let tod;
  try { tod = world.getTimeOfDay(); } catch { return; }
  const onDuty = tod >= SCHED.work[0] && tod < SCHED.work[1];
  for (const st of s.settlements) {
    if (!st.kit || !st.square) continue;
    const vs = HB.bodiesOf(st);                                              // 1.3.228 (B1): the shared bodies cache (read <= 20 ticks ago)
    const sites = laborSites(s, st);
    for (const b of sites) b.labor.crew = 0;
    { const ids = new Set(); for (const v of vs) { const tg = v.getTags().find((x) => x.startsWith("civ:person:")); if (tg) ids.add(Number(tg.slice(11))); } bodiesNow.set(st.id, ids); }
    const ctx = schedCtx(s, st, tod);
    ctx.sites = sites;
    let sends = 0;
    // 1.3.228 (B4 / rain ruling): the share of the town's work hours that was wet (sampled once a pass, memory) — the day's
    // quarry / lumberyard / builders' output keeps half of it (produceDaily, advanceOnce)
    if (onDuty) { const w = wetLog.get(st.id) || { n: 0, wet: 0 }; w.n++; if (ctx.wet) w.wet++; wetLog.set(st.id, w); }
    // 1.3.228 (B2 / BF3): the why-idle tally of this pass (B4: the phase is each person's own shift slot)
    const tally = {}, seenPid = new Set(), dayN = Math.floor(s.simDays), phase = onDuty ? "work" : "off";
    let waitGood;
    const waitGoodOf = () => (waitGood === undefined ? (waitGood = siteWaitGood(s, st)) : waitGood);
    let innGain = 0;
    const slotT = { W: 0, M: 0, I: 0, R: 0, off: 0, leaving: 0, far: 0, inn: 0, shelter: 0 };   // B4: the pass's shift picture (memory)
    const icons = !!s.whyIcons;
    let players = [];
    if (icons) { try { players = world.getPlayers().filter((pl) => pl.dimension.id === st.dim).map((pl) => pl.location); } catch { players = []; } }
    const note = (v, pid, code) => {
      if (pid !== null) { seenPid.add(pid); whyNow.set(`${st.id}:${pid}`, code); }
      tally[code] = (tally[code] || 0) + 1;
      if (icons) { const near = players.some((q) => Math.abs(q.x - v.location.x) <= WHY_ICON_R && Math.abs(q.z - v.location.z) <= WHY_ICON_R && Math.abs(q.y - v.location.y) <= WHY_ICON_R); setWhyIcon(v, near ? code : null); }
      else { try { if (ICON_TAG.test(v.nameTag || "")) setWhyIcon(v, null); } catch { /* left */ } }
    };
    const pidOf = (v) => { const tg = v.getTags().find((x) => x.startsWith("civ:person:")); return tg ? Number(tg.slice(11)) : null; };
    // 0.0.25j (run 0.0.28: the counters were never stocked — s.accelNow is refreshed only when days advance, and a PAUSED
    // clock (the harness pauses it; so may he) kept the last skip's "true"): the gate reads the skip itself (accelLeft)
    if (tod >= MARKET[0] && tod < MARKET[1]) diagOf(st).marketGate = [Math.floor(s.simDays), st.stockedDay ?? null, !!s.accelNow, (s.accelLeft || 0) > 1e-9 ? 1 : 0, plotsOf(s, st).filter((b) => COUNTER[short(b)]).map((b) => [b.id, b.stage, b.closed ? 1 : 0])];
    if (tod >= MARKET[0] && tod < MARKET[1] && !((s.accelLeft || 0) > 1e-9) && st.stockedDay !== Math.floor(s.simDays)) { st.stockedDay = Math.floor(s.simDays); try { stockCounters(s, st); } catch (e) { console.warn(`[CIV-CLOCK] counters: ${e}`); } }
    lap(); yield; t0 = Date.now();
    for (const v of vs) {
      lap(); yield; t0 = Date.now();
      if (!v.isValid) continue;
      civOn(v);                                                              // 1004b: a body from an older pack becomes a civ on sight
      if (v.hasTag("civ:walktest")) continue;                                // 0.0.25: the walk instrument's walkers
      if (VOICE.isHeld(v.id)) continue;                                      // B5 (PE11 / BF11): talking, listening, petitioning
      try { if (v.hasTag("civ:rally")) continue; } catch {}                  // B10 (his 10:15): banded together against monsters
      if (GUEST.isGuiding(v.id)) continue;                                   // B11 (WP12): showing a player the way
      const pid = pidOf(v), person = pid !== null ? ctx.people.get(pid) || null : null;
      const child = !!person && PEOPLE.stage(person, dayN) === "child";
      if (v.hasTag("civ:keeper") || v.hasTag("civ:watching") || v.hasTag("civ:working")) {   // their own beats send them (shop / watch / work)
        const wk = v.hasTag("civ:working") ? WORKMOD.whyOf(v.id) : null;
        note(v, pid, PEOPLE.whyOf(person || { home: -1 }, { child, phase: "work", worker: wk, busy: true, homeFar: !!person && !wk && homeFarOf(s, st, person) }));
        continue;
      }
      const g = goalFor(s, st, v, tod, ctx);
      const here = g ? Math.hypot(v.location.x - g.x, v.location.z - g.z) : 0;
      const onShiftNow = ctx.slot === "W";                                    // 1.3.228 (B4 / BF5): his own shift
      if (ctx.slot) { slotT[ctx.slot]++; if (ctx.shOff) slotT.off++; if (ctx.shHome) slotT.leaving++; if (ctx.homeFar) slotT.far++; if (g && g.inn !== undefined) slotT.inn++; if (ctx.kind === "shelter") slotT.shelter++; }
      { const k = ctx.kind;                                                   // 1.3.228 (B2 / BF3): this person's reason now
        const wg = ctx.builderIdle && k !== "job" ? waitGoodOf() : null;
        note(v, pid, PEOPLE.whyOf(person, { child, phase: onShiftNow || k === "shop" ? "work" : "off", noStock: ctx.noShop && k !== "shop", siteWaits: wg,
          walk: g && here > 3 && !WALK.walking(v) ? WALK.whyNot(v) : null, busy: k === "fish" || k === "survey" || k === "shop" || k === "site" || k === "job",
          wet: k === "rain", builderIdle: ctx.builderIdle && k !== "job", homeFar: ctx.homeFar, shelter: k === "shelter", alarm: k === "alarm" })); }
      if (!g) continue;
      // 1.3.228 (B4 / rain ruling): a builder sheltering from the rain keeps half a body's work for his site
      if (g.shelterSite !== undefined) { const b = sites.find((x) => x.id === g.shelterSite); if (b && b.labor) { b.labor.done += 100 * PEOPLE.RAIN.keep; b.labor.rainDone = (b.labor.rainDone || 0) + 100 * PEOPLE.RAIN.keep; } }
      // 1.3.228 (B4 / PE2): an unhappy person inside the inn: a mood point every INN.per ticks there
      if (g.inn !== undefined && here <= 3 && person) innGain += innStay(st, person);
      if (g.buy !== undefined && here <= 3) {                                  // C2.4: at the counter
        const shopB = g.buy < 0 ? { id: g.buy, market: true } : ctx.byId.get(g.buy), person = ctx.people.get(g.person);   // B7: the stall
        if (shopB && person) buyAt(s, st, v, person, shopB);
        if (WALK.walking(v)) WALK.cancel(v);
        civState(v, "stand");
        continue;
      }
      if (g.site !== undefined && onShiftNow && here <= 6) {                 // C2.3: a builder at the site works
        const b = sites.find((x) => x.id === g.site);
        if (b && b.labor) { b.labor.done += 100; b.labor.worked = (b.labor.worked || 0) + 1; try { v.dimension.playSound(b.labor.done % 300 < 100 ? "use.stone" : "use.wood", v.location, { volume: 0.7 }); } catch { /* left */ } }
      }
      if (g.fish && onShiftNow && here <= 2.5) {                               // 1.3.225: the fisherman at his spot
        try { const vc = v.getComponent("minecraft:variant"); if (vc && vc.value !== 2) v.triggerEvent("pw:skin_fisher"); } catch { /* left */ }
        fishAt(st, v, g.fish);
        if (WALK.walking(v)) WALK.cancel(v);
        civState(v, "stand");
        continue;
      }
      if (g.survey && onShiftNow && here <= 3) {                               // B4: the surveyor lifts / sets a stone
        try { surveyorAct(s, st, g.survey); v.dimension.playSound(g.survey.kind === "lift" ? "dig.stone" : "use.stone", v.location, { volume: 0.8 }); } catch (e) { console.warn(`[CIV-CLOCK] surveyor: ${e}`); }
        if (WALK.walking(v)) WALK.cancel(v);
        continue;
      }
      if (here <= 3) {
        if (WALK.walking(v)) WALK.cancel(v); civState(v, g.mode || "stand");
        if (g.look) { try { v.setRotation({ x: 0, y: PEOPLE.yawTo(v.location, g.look) }); } catch { /* left */ } }   // B4 (PE1): faces the beat's block
        continue;
      }
      if (!WALK.walking(v) && sends < SENDS_PER_BEAT) { sends++; WALK.send(v, st, g); }
    }
    shiftDiag(st, tod, ctx.wday, sends, slotT);
    // 1.3.228 (B2 / BF3): the people with no body seen this pass (asleep land / not spawned), children, the homeless
    if (st.people) for (const q of PEOPLE.alive(st.people)) {
      if (seenPid.has(q.id)) continue;
      const code = PEOPLE.whyOf(q, { child: PEOPLE.stage(q, dayN) === "child", asleep: true, phase });
      whyNow.set(`${st.id}:${q.id}`, code); tally[code] = (tally[code] || 0) + 1;
    }
    st.why = PEOPLE.capTally(tally, 16);
    if (innGain) { const d = diagOf(st); d.inn = (d.inn || 0) + innGain; save(); }   // B4 (PE2): the census moved (marks dirty)
    if (whyTierSaid.get(st.id) !== st.tier) { whyTierSaid.set(st.id, st.tier); console.warn(`[CIV-WHY] ${JSON.stringify({ settlement: st.id, tier: st.tier, day: dayN, phase, why: st.why })}`); }
    // a finished labour: the stage rises (layers), the next one may start
    let done = false;
    for (const b of sites) {
      if (!b.labor || b.labor.done < b.labor.need) continue;
      const k = b.labor.k;
      st.log.push(`day ${s.simDays.toFixed(0)}: the builders finished the ${STAGE_NAMES[k]} of #${b.id} ${short(b)} (${b.labor.worked || 0} builder-beats)`);
      st.built = (st.built || 0) + 1;
      delete b.labor;
      b.stage = k; b.progress = 0; b.animate = true; b.pending.push(k);
      done = true;
    }
    if (done) { flushPending(); save(); }
  }
 } finally { lap(); schedBusy = false; }
}
// 1.3.228 (B5): the voice module reads the clock through these
const LAST_BUILT = new Map();                                            // settlement id -> { day, name } (memory: the newest furnished building)
VOICE.initVoice({ load, save, short, PEOPLE, civState, inInfluence: (st, x, z) => inInfluence(st, x, z),
  whyCode: (st, pid) => whyNow.get(`${st.id}:${pid}`) || null,
  wetNow: (st) => { try { return weatherIn(st.dim) !== "Clear"; } catch { return false; } },
  recentBuilt: (s, st, day) => { const r = LAST_BUILT.get(st.id); return r && day - r.day <= 2 ? r.name : null; } });
// 1.3.228 (B11): festivals, the dusk speech, the guide, deeds (OFF)
GUEST.initGuest({ load, worldDay, inInfluence: (st, x, z) => inInfluence(st, x, z), PEOPLE, ECON, short,
  recentBuilt: (st) => { const r = LAST_BUILT.get(st.id); return r && Math.floor(load().simDays) - r.day <= 1 ? [r.name] : []; } });
/** WP12: the places a guide knows in a town: the market, the inn, the smithy, the town hall, the player's last shop */
function guidePlaces(st, player) {
  const s = load(), out = [];
  const at = (b) => { const def = BUILDINGS[b.family]; if (!def) return null; const fr = doorFront(b, def); return { x: fr.x + 0.5, y: b.y + def.datum_y, z: fr.z + 0.5 }; };
  if (st.square) out.push({ label: "The market", target: SHOP.marketStation(st) });
  const fin = plotsOf(s, st).filter((b) => b.stage >= 4 && !b.closed);
  for (const [nm, label] of [["inn", "The inn"], ["smithy", "The smithy"], ["town_hall", "The town hall"], ["bakery", "The bakery"]]) {
    const b = fin.find((x) => short(x) === nm);
    const t = b ? at(b) : null;
    if (t) out.push({ label, target: t });
  }
  const last = st.pstats && st.pstats[player.name] && st.pstats[player.name].last;
  const lb = last ? fin.find((x) => x.id === last) : null;
  if (lb) { const t = at(lb); if (t) out.push({ label: `The ${short(lb).replace(/_/g, " ")} you last bought from`, target: t }); }
  return out;
}
// v1.3.219: the shopkeepers' module reads the clock through these
SHOP.initShops({ chronicleOf, worldDay: () => worldDay(),   // 1.3.232 #3: the counted week day
 
  guideTo: (v, player, st, place) => GUEST.guideTo(v, player, st, place),            // 1.3.228 (B11 / WP12)
  guidePlaces: (st, player) => guidePlaces(st, player),
  districtAt: (st, x, z) => districtAt(st, x, z),                                     // 1.3.228 (B11 / WP11)
  renameDistrict: (st, sid, nm) => { st.names = st.names || {}; if (Object.entries(st.names).some(([k, v]) => v === nm && Number(k) !== sid)) return false; st.names[sid] = nm; ZONES.clear(); st.log.push(`day ${Math.floor(load().simDays)}: the town voted to call a street ${nm}`); annal(st, load().simDays, `the town named ${nm}`); return true; },
  load, save, footprint, rotXZ, short, ECON, BUILDINGS, VILLAGER_ID, PEOPLE, civOn, civState, insideDoor, blockAt,   // 1.3.228: blockAt
  noticeSlips: (s, st) => noticeSlips(s, st),                          // 1.3.228 (B7 / BF8): the clerk's notices
  onShift: (v, st, tod) => bodyOnShift(v, st, tod),                   // 1.3.228 (B4 / BF5): the keeper's own (late) shift
  workSpot: (b, v, st, tick) => { const p = personOfBody(v, st); const sp = workSpotsOf(b); return p && sp ? PEOPLE.workSpot(PEOPLE.beatOf(p.id, tick), sp, p.id) : null; },   // B4 (PE1)
  nameFor: (b, st) => { const P = st ? census(st) : null; const p = P ? PEOPLE.alive(P).find((q) => q.job === b.id && q.keeper) : null; return p ? p.name : NAMES[((b.id * 11) + (st ? st.seed : 0)) % NAMES.length]; },
  keeperPerson: (b, st, name) => {
    if (!st) return null;
    const P = census(st), day = Math.floor(load().simDays);
    let p = PEOPLE.alive(P).find((q) => q.job === b.id && q.keeper);
    if (!p) { p = PEOPLE.newPerson(P, day, { job: b.id, trade: short(b), name, age: 30, seed: b.id * 13, home: b.id }); p.keeper = true; }
    if (!p.home) p.home = b.id;
    return p.id;
  } });
