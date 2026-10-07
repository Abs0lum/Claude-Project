#!/usr/bin/env python3
"""patch_clock_219.py — pw_civ_clock.js for BP-02 1.3.219 from the frozen 1.3.218 copy (D-C529 / D-C530):
kit streets (pw_civ_streets.js + tools/bp02_src/kit_block.js), keepers + coin shop (pw_civ_shop.js, pw_civ_coin.js),
leaf sweep, park, widening at town. Every replacement must match exactly once (silent no-match is a failure, P4).
Usage: patch_clock_219.py  -> writes tools/bp02_src/pw_civ_clock.js"""
from pathlib import Path

SRC = Path("/home/claude/_build/bp02-218/scripts/pw_civ_clock.js")
OUT = Path("/home/claude/tools/bp02_src/pw_civ_clock.js")
KIT_BLOCK = Path("/home/claude/tools/bp02_src/kit_block.js")
t = SRC.read_text()


def rep(old, new, what):
    global t
    n = t.count(old)
    if n != 1:
        raise SystemExit(f"{what}: expected 1 match, found {n}")
    t = t.replace(old, new)


# ---------------------------------------------------------------- header + imports
rep("// pw_civ_clock.js — CIVITAS VILLAGE CLOCK + TIME TOOL (BP-02 v1.3.207): the living town on the land.",
    "// pw_civ_clock.js — CIVITAS VILLAGE CLOCK + TIME TOOL (BP-02 v1.3.219): the living town on the land.\n"
    "// v1.3.219 (D-C529 / D-C530): new settlements lay HIS StreetKit pieces (KIT STREETS below: straight streets, ramps,\n"
    "//   dead ends with sewer outfalls, bridges with railing openings, side streets by T junctions, streets that grow,\n"
    "//   village width -> town width at tier town), houses flush on the street at sidewalk height with an access piece at\n"
    "//   each sewer shaft; KEEPERS at the shops' stations in work hours and a COIN SHOP window (pw_civ_shop.js); the GOLD\n"
    "//   COIN mint (pw_civ_coin.js); floating leaves cleared daily; a PARK at tier town. Older settlements keep their streets.",
    "header")
rep('import { world, system, ItemStack } from "@minecraft/server";',
    'import { world, system, ItemStack, BlockVolume, BlockTypes, BlockPermutation, LiquidType } from "@minecraft/server";', "import server")
rep('import * as LAND from "./pw_civ_land.js";',
    'import * as LAND from "./pw_civ_land.js";\n'
    'import * as KIT from "./pw_civ_streets.js";\n'
    'import { PARK_TREE_SET } from "./pw_civ_parktrees.js";\n'
    'import * as SHOP from "./pw_civ_shop.js";\n'
    'import * as COIN from "./pw_civ_coin.js";', "import kit")

# ---------------------------------------------------------------- kit plots: the door's street height, no settle
rep("""function streetHeightAtDoor(b, def) {
  const front = doorFront(b, def);""", """function streetHeightAtDoor(b, def) {
  if (b.kit) return b.kit.H;                                     // v1.3.219: a kit plot stands at its street's sidewalk height
  const front = doorFront(b, def);""", "streetHeightAtDoor")

# ---------------------------------------------------------------- placeStage: the access piece with the first stage; keepers
rep("""    if (k === 0 && b.street) { if (!b.planned) layStreet(dim, b); b.yardCells = yardPass(dim, b, def); b.steps = stoop(dim, b, def); }
    if (k === def.stages - 1 && b.settlement !== undefined && !b.villagers) moveIn(dim, b, def);""",
    """    if (k === 0 && b.street) { if (!b.planned) layStreet(dim, b); b.yardCells = yardPass(dim, b, def); b.steps = stoop(dim, b, def); }
    if (k === 0 && b.kit) { const kst = load().settlements.find((x) => x.id === b.settlement); if (kst) kitPlotAccess(kst, b); }
    if (k === def.stages - 1 && b.settlement !== undefined && !b.villagers) moveIn(dim, b, def);
    // v1.3.219: a furnished shop (and the inn, the town hall, the farms) gets its KEEPER at the station
    if (k === def.stages - 1 && b.settlement !== undefined && SHOP.KEEPS.includes(short(b)) && !b.closed) {
      const kst = load().settlements.find((x) => x.id === b.settlement);
      SHOP.hireKeeper(dim, b, def, kst);
    }""", "placeStage hooks")

# ---------------------------------------------------------------- addPlot: kit settlements
rep("""function addPlot(s, st, family, dimId, delay, pick) {
  const spot = allocate(s, st, family, pick);""", """function addPlot(s, st, family, dimId, delay, pick) {
  if (st.kit) return kitAddPlot(s, st, family, delay);          // v1.3.219: StreetKit streets
  const spot = allocate(s, st, family, pick);""", "addPlot")

# ---------------------------------------------------------------- the land marks: widening, park, leaves
rep("""  const hardened = hardenStreets(dim, st, ti);
  if (hardened) marks.push(`streets ${ti >= 2 ? "cobbled" : "gravelled"} (${hardened})`);""",
    """  const hardened = st.kit ? 0 : hardenStreets(dim, st, ti);
  if (hardened) marks.push(`streets ${ti >= 2 ? "cobbled" : "gravelled"} (${hardened})`);
  if (st.kit && ti >= 2) {                                       // v1.3.219: town width + a park (his 18:02)
    const n = widenKit(st);
    if (n) marks.push(`streets resurfaced to the town width (${n} pieces)`);
    if (!st.park && kitPark(s, st)) marks.push("a park staked out");
  }
  if (st.kit) sweepLeaves(st);""", "livingMarks")

# ---------------------------------------------------------------- daily: the leaf sweep
rep("""    const evs = ECON.dayStep(L, shopsOf(s, st), population(s, st));""",
    """    const evs = ECON.dayStep(L, shopsOf(s, st), population(s, st));
    if (st.kit) sweepLeaves(st);                                 // v1.3.219 (his 18:02): floating leaves cleared every day""", "daily sweep")

# ---------------------------------------------------------------- bodies: kit corridors count as streets everywhere
rep("""function streetHeights(s, only = null) {
  const m = new Map();
  for (const st of s.settlements) {
    if (only && st.id !== only.id) continue;
    for (const [k, h] of LAND.streetBody(st.profile || {}, st.axis || "x")) m.set(k, h);
  }
  return m;
}""", """function streetHeights(s, only = null) {
  const m = new Map();
  for (const st of s.settlements) {
    if (only && st.id !== only.id) continue;
    for (const [k, h] of bodyOf(st)) m.set(k, h);
  }
  return m;
}
/** a settlement's street body: its kit corridors (v1.3.219) or its legacy profile's 3-wide body */
function bodyOf(st) { return st.kit ? kitBody(st) : LAND.streetBody(st.profile || {}, st.axis || "x"); }""", "streetHeights")
rep("""  const streetCells = new Set(LAND.streetBody(st.profile || {}, st.axis || "x").keys());""",
    """  const streetCells = new Set(bodyOf(st).keys());""", "wall gates")
rep("""  for (const st of s.settlements) if (st.square && (!only || st.id === only.id)) boxes.push([st.square.x - margin, st.square.x + LAND.SQUARE - 1 + margin, st.square.z - margin, st.square.z + LAND.SQUARE - 1 + margin]);""",
    """  for (const st of s.settlements) if (st.square && (!only || st.id === only.id)) boxes.push([st.square.x - margin, st.square.x + LAND.SQUARE - 1 + margin, st.square.z - margin, st.square.z + LAND.SQUARE - 1 + margin]);
  for (const st of s.settlements) if (st.park && (!only || st.id === only.id)) { const [a, b2, c, d] = st.park.box; boxes.push([a - margin, b2 + margin, c - margin, d + margin]); }""", "plotBoxes parks")

# nearestStreetCell: kit corridors
rep("""function nearestStreetCell(st, px, pz) {""", """function nearestStreetCell(st, px, pz) {
  if (st.kit) {                                                  // v1.3.219: the nearest corridor cell of the kit streets
    let bk = null, bd = Infinity;
    for (const [key, h] of kitBody(st)) { const [x, z] = key.split(",").map(Number); const d = Math.abs(x - px) + Math.abs(z - pz); if (d < bd) { bd = d; bk = { x, z, h }; } }
    return bk;
  }""", "nearestStreetCell")

# ---------------------------------------------------------------- founding: kit first
rep("""  system.runJob(readSiteJob(st, cx, cz, dimId, (site) => {
    const plan = LAND.planMainStreet(site, cx, cz, seedN);""", """  system.runJob(readSiteJob(st, cx, cz, dimId, (site) => {
    // v1.3.219 (his 17:37 / 18:01): StreetKit streets — the legacy contour street only when the kit cannot be planned here
    try { if (foundKitSettlement(s, st, site, cx, cz, seedN, reply)) return; } catch (e) { console.warn(`[CIV-CLOCK] kit founding: ${e} ${e.stack || ""}`); }
    const plan = LAND.planMainStreet(site, cx, cz, seedN);""", "foundSettlement")

# ---------------------------------------------------------------- the kit queue's own heartbeat
rep("""function say(p, msg) {""", """// v1.3.219: the kit queue (street pieces, bridges, outfalls) and the park run on their own short beat
let kitOpsSinceSave = 0;
system.runInterval(() => {
  const s = load();
  const busy = s.settlements.some((x) => x.kit && ((x.kitQueue && x.kitQueue.length) || (x.park && !x.park.done)));
  if (!busy) return;
  const n = processKitQueue(s);
  for (const st of s.settlements) if (st.park && !st.park.done && !(st.kitQueue && st.kitQueue.length)) { try { layPark(st); } catch (e) { console.warn(`[CIV-CLOCK] park: ${e}`); } }
  kitOpsSinceSave += n;
  if (kitOpsSinceSave >= 15 || !s.settlements.some((x) => x.kitQueue && x.kitQueue.length)) { kitOpsSinceSave = 0; save(); }
}, 2);

function say(p, msg) {""", "kit heartbeat")

# ---------------------------------------------------------------- status: kit facts + the mint
rep("""    if (st.roads && st.roads.length) say(p,""", """    if (st.kit) say(p, `§a    kit streets: ${st.streets.filter((x) => x.kind === "kit").map((x) => `#${x.id} ${x.role} ${x.H.length} cells`).join(", ")} · width ${st.width === "t" ? "town (7)" : "village (5)"} · ` +
      `${(st.kitQueue || []).length} piece(s) queued, ${st.kitLaid || 0} laid · leaves cleared ${st.leafSwept || 0}${st.park ? ` · park ${st.park.done ? "laid" : "staked"}` : ""}`);
    if (st.roads && st.roads.length) say(p,""", "status kit")

# ---------------------------------------------------------------- the kit block, before the living marks section
marker = "// ------------------------------------------------------------------------------------------------ living marks (step 4)"
rep(marker, KIT_BLOCK.read_text() + "\n" + marker, "kit block")

# ---------------------------------------------------------------- the shop module gets the clock's functions
t += """
// v1.3.219: the shopkeepers' module reads the clock through these
SHOP.initShops({ load, save, footprint, rotXZ, short, ECON, BUILDINGS, VILLAGER_ID,
  nameFor: (b, st) => NAMES[((b.id * 11) + (st ? st.seed : 0)) % NAMES.length] });
"""

# ---------------------------------------------------------------- commands: coins (mint census)
rep("""  if (cmd === "market" || cmd === "buy" || cmd === "sell") {""", """  if (cmd === "coins") {                                        // v1.3.219: the mint's census
    const c = COIN.census();
    reply(`§e[MINT] issued ${c.issued} (serials #1-#${c.seq}) · returned ${c.returned} · lost ${c.destroyed} · in circulation ${c.circulation} · ` +
      `carried by players online ${c.carried} · ${c.piles} pile(s) holding ${c.inPiles}`);
    for (const line of COIN.ledger().lines.slice(-10)) reply(`§7  ${line}`);
    if (p && a === "give") { const n = Math.max(1, Math.min(640, Math.floor(Number(b) || 16))); COIN.issue(p, n, "the mint", "test tool"); reply(`§a[MINT] ${n} coins issued to you`); }
    return;
  }
  if (cmd === "market" || cmd === "buy" || cmd === "sell") {""", "coins cmd")


# ---------------------------------------------------------------- status events stay under the 2 KB message cap (kit streets carry arrays)
rep("""      const { ledger, log, shortDays, ...rest } = st;                    // a script event message is capped (2 KB): keep it compact""",
    """      const { ledger, log, shortDays, kitQueue, streets, profile, leftover, triedTerraces, ...rest } = st;   // a script event message is capped (2 KB): keep it compact
      rest.streets = (streets || []).map((x) => x.kind === "kit" ? { kind: "kit", id: x.id, role: x.role, n: x.H.length, f: x.f, tmin: x.tmin, ramps: x.segs.filter((q) => q.kind === "ramp").length,
        bridges: x.segs.filter((q) => q.kind === "bridge").map((q) => [q.a, q.len]), tees: (x.tees || []).length, access: (x.access || []).length, outfalls: (x.outfalls || []).map((o) => o.plan ? o.plan.exit : null) } : { kind: x.kind, laid: x.laid, nCells: x.nCells });
      rest.kitQueue = kitQueue ? kitQueue.length : 0;""", "status compact")


# ---------------------------------------------------------------- review 19:1x: groundAt never throws (kitvillage-0.0.5: a Block handle in an
# unloaded chunk threw on .typeId, outside the try — the kit founding died half-way and the legacy founding ran on top of it)
rep("""function groundAt(dim, x, z) {
  let b;
  try { b = dim.getTopmostBlock({ x, z }); } catch { return undefined; }
  for (let i = 0; b && i < 48; i++) {
    if (isGround(b.typeId)) return b.location.y;
    try { b = b.below(); } catch { return undefined; }
  }
  return b ? b.location.y : undefined;
}""", """function groundAt(dim, x, z) {
  try {
    let b = dim.getTopmostBlock({ x, z });
    for (let i = 0; b && i < 48; i++) {
      if (isGround(b.typeId)) return b.location.y;
      b = b.below();
    }
    return b ? b.location.y : undefined;
  } catch { return undefined; }                                // an unloaded chunk anywhere on the way down
}""", "groundAt safe")
rep("""    try { if (foundKitSettlement(s, st, site, cx, cz, seedN, reply)) return; } catch (e) { console.warn(`[CIV-CLOCK] kit founding: ${e} ${e.stack || ""}`); }""",
    """    try { if (foundKitSettlement(s, st, site, cx, cz, seedN, reply)) return; } catch (e) {
      console.warn(`[CIV-CLOCK] kit founding: ${e} ${e.stack || ""}`);
      // review 19:1x: a kit founding that failed after it began (streets / plots made) is kept as it is — never a second,
      // legacy founding laid on top of it (kitvillage-0.0.5: both ran: two wells, two street systems)
      if (st.kit) { st.phase = "built"; st.log.push(`day ${s.simDays.toFixed(0)}: founding interrupted (${String(e).slice(0, 80)}) — kept as far as it got`); flushPending(); save(); reply(`§c[CLOCK] ${st.name}: founding interrupted (${e}); kept as far as it got`); return; }
    }""", "no double founding")


# ---------------------------------------------------------------- D-C533: the headless status carries the sewer-water facts the probe reads
rep("""        bridges: x.segs.filter((q) => q.kind === "bridge").map((q) => [q.a, q.len]), tees: (x.tees || []).length, access: (x.access || []).length, outfalls: (x.outfalls || []).map((o) => o.plan ? o.plan.exit : null) } : { kind: x.kind, laid: x.laid, nCells: x.nCells });
      rest.kitQueue = kitQueue ? kitQueue.length : 0;""",
    """        bridges: x.segs.filter((q) => q.kind === "bridge").map((q) => [q.a, q.len]), tees: (x.tees || []).length, access: (x.access || []).length,
        outfalls: (x.outfalls || []).map((o) => o.plan ? [o.plan.exit[0], o.plan.exit[1], o.plan.dir[0], o.plan.dir[1], o.plan.floorY, o.plan.cells.length] : null) } : { kind: x.kind, laid: x.laid, nCells: x.nCells });
      rest.kitQueue = kitQueue ? kitQueue.length : 0;
      rest.kitWater = st.kitWater || 0;""", "status sewer facts")


# ---------------------------------------------------------------- planning budget: a tier's plots that found no room are LEFTOVERS retried daily
rep("""  for (const [nm, n] of TIER_ADDS[tier]) {
    for (let i = 0; i < n; i++) {
      const skins = skinsOf(nm);
      const family = familyOf(nm, skins[Math.floor(pick() * skins.length)]);
      const b = addPlot(s, st, family, st.dim, k * VILLAGE_STAGGER, pick);
      if (b) { added.push(b); k++; }
    }
  }""", """  for (const [nm, n] of TIER_ADDS[tier]) {
    for (let i = 0; i < n; i++) {
      const skins = skinsOf(nm);
      const family = familyOf(nm, skins[Math.floor(pick() * skins.length)]);
      const b = addPlot(s, st, family, st.dim, k * VILLAGE_STAGGER, pick);
      if (b) { added.push(b); k++; } else st.leftover.push(nm);                 // no room now: retried a plot a day (stepSettlement)
    }
  }""", "tier leftovers")
rep("""function stepSettlement(s, st, days, events) {
  const age = s.simDays - st.founded;
  stepEconomy(s, st, days, events);""", """function stepSettlement(s, st, days, events) {
  const age = s.simDays - st.founded;
  stepEconomy(s, st, days, events);
  // a leftover plot (no room when its tier came) gets one try a day: the street grows / a side street opens / a bench
  if (st.kit && st.leftover && st.leftover.length && st.phase === "built") {
    const nm = st.leftover[0];
    const skins = skinsOf(nm);
    const pick = rng((st.seed + s.simDays * 31) >>> 0);
    const b = addPlot(s, st, familyOf(nm, skins[Math.floor(pick() * skins.length)]), st.dim, 0, pick);
    if (b) { st.leftover.shift(); st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${nm} (#${b.id})`); }
  }""", "daily leftover")


rep("""  for (const nm of (st.leftover || [])) {
    const skins = skinsOf(nm);
    const b = addPlot(s, st, familyOf(nm, skins[Math.floor(pick() * skins.length)]), st.dim, k * VILLAGE_STAGGER, pick);
    if (b) { added.push(b); k++; }
  }
  st.leftover = [];""", """  const still = [];
  for (const nm of (st.leftover || [])) {
    const skins = skinsOf(nm);
    const b = addPlot(s, st, familyOf(nm, skins[Math.floor(pick() * skins.length)]), st.dim, k * VILLAGE_STAGGER, pick);
    if (b) { added.push(b); k++; } else still.push(nm);
  }
  st.leftover = still;""", "leftover keep")


rep("""    if (k === 0 && b.kit) { const kst = load().settlements.find((x) => x.id === b.settlement); if (kst) kitPlotAccess(kst, b); }""",
    """    if (k === 0 && b.kit) { const kst = load().settlements.find((x) => x.id === b.settlement); if (kst) { kitPlotAccess(kst, b); try { kitLandPrep(dim, b, def, kst); } catch (e) { console.warn(`[CIV-CLOCK] land prep #${b.id}: ${e}`); } } }""", "landprep hook")


rep("""    if (k === 0 && b.street) { clearOver(dim, b, def); b.filled = terrace(dim, b, def); }""",
    """    if (k === 0 && b.street) { clearOver(dim, b, def); b.filled = (b.land && b.land.kind === "stilts") ? 0 : terrace(dim, b, def); }   // a stilt house has posts, not a ring""", "stilts no ring")


rep("""    const b = addPlot(s, st, familyOf(nm, skins[Math.floor(pick() * skins.length)]), st.dim, 0, pick);
    if (b) { st.leftover.shift(); st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${nm} (#${b.id})`); }
  }""", """    const b = addPlot(s, st, familyOf(nm, skins[Math.floor(pick() * skins.length)]), st.dim, 0, pick);
    if (b) { st.leftover.shift(); st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${nm} (#${b.id})`); }
    // D-C534 §2.3: still no room and the streets cannot grow -> look for a NEW BENCH joined by a switchback road
    else if (!(st.kitQueue || []).length && (st.benchFail === undefined || s.simDays - st.benchFail >= BENCH_WAIT)) startBenchJob(st);
  }""", "bench trigger")


# ---------------------------------------------------------------- D-C534 §2.3: `bench [n]` starts the bench + road job now (witness / probe)
rep("""  if (cmd === "grow" || cmd === "decline" || cmd === "immigrate" || cmd === "log") {""",
    """  if (cmd === "bench") {
    const st = targetSettlement(s, p, a);
    if (!st || !st.kit) { reply("§c[CLOCK] no kit settlement here"); return; }
    delete st.benchFail;
    startBenchJob(st);
    reply(`§e[CLOCK] ${st.name}: looking for a new bench and a road to it (${departures(st).length} departure(s))`);
    return;
  }
  if (cmd === "grow" || cmd === "decline" || cmd === "immigrate" || cmd === "log") {""", "bench cmd")


rep("""      rest.kitQueue = kitQueue ? kitQueue.length : 0;
      rest.kitWater = st.kitWater || 0;""", """      rest.kitQueue = kitQueue ? kitQueue.length : 0;
      rest.kitWater = st.kitWater || 0;
      rest.streets.forEach((x, i) => { const src = (streets || [])[i]; if (src && src.bench) x.bench = true; });
      rest.roads7 = (st.roads7 || []).map((r) => ({ id: r.id, from: r.from, end: r.end, to: r.to, n: r.cells.length, turns: r.turns.length, ramps: r.ramps.length }));
      rest.roadLaid = st.roadLaid || 0;
      rest.benchFail = st.benchFail;
      // the roads' cells, in parts (a script event message is capped at 2 KB)
      for (const r of (st.roads7 || [])) {
        for (let i = 0; i < r.cells.length; i += 60) {
          const part = { id: r.id, st: st.id, i, cells: r.cells.slice(i, i + 60), H: r.H.slice(i, i + 60), dirs: r.dirs.slice(i, i + 60), turns: r.turns, ramps: r.ramps, n: r.cells.length };
          try { system.sendScriptEvent("pw:clock_road", JSON.stringify(part)); } catch (e) { console.warn(`[CLOCK] ${e}`); }
        }
      }""", "status roads")


# ---------------------------------------------------------------- D-C534 §1: the ladder to metropolis II
rep("""const TIERS = ["village", "village2", "town", "town2", "city"];
const TIER_DAYS = { village2: 25, town: 60, town2: 120, city: 200 };            // age at which a tier may be reached
const TIER_ADDS = {                                                            // what each tier adds (building, count)
  village2: [["cottage_s", 2], ["cottage_m", 1], ["farm_terrace", 1]],      // the hillside field (step 2b)
  town: [["bakery", 1], ["cottage_l", 1], ["cottage_s", 2], ["lumberyard", 1], ["inn", 1]],
  town2: [["butcher", 1], ["smithy", 1], ["cottage_m", 2], ["cottage_s", 2], ["farm_cattle", 1]],  // second sellers: competition
  city: [["town_hall", 1], ["bakery", 1], ["cottage_l", 2], ["cottage_m", 2], ["cottage_s", 3], ["quarry", 1], ["well", 1]],
};""", """// D-C535 (his 21:52): THREE steps per tier — village I-III, town I-III, city I-III, metropolis I-III — and above them the
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
  town2: [["cottage_m", 5], ["cottage_s", 5], ["cottage_l", 2], ["farm_wheat", 1], ["bakery", 1], ["quarry", 1]],
  town3: [["cottage_m", 6], ["cottage_s", 7], ["cottage_l", 3], ["farm_terrace", 1], ["farm_cattle", 1], ["smithy", 1], ["inn", 1]],
  city: [["town_hall", 1], ["bakery", 2], ["cottage_l", 5], ["cottage_m", 7], ["cottage_s", 6], ["quarry", 1], ["well", 1], ["butcher", 1], ["lumberyard", 1]],
  city2: [["cottage_s", 10], ["cottage_m", 10], ["cottage_l", 6], ["bakery", 1], ["butcher", 1], ["smithy", 1], ["inn", 2], ["farm_wheat", 2], ["farm_cattle", 1], ["lumberyard", 1]],
  city3: [["cottage_s", 12], ["cottage_m", 12], ["cottage_l", 7], ["bakery", 2], ["butcher", 1], ["smithy", 1], ["inn", 1], ["farm_wheat", 1], ["farm_terrace", 1], ["quarry", 1], ["town_hall", 1]],
  metropolis: [["cottage_s", 16], ["cottage_m", 16], ["cottage_l", 10], ["bakery", 2], ["butcher", 2], ["smithy", 2], ["inn", 2], ["farm_wheat", 2], ["farm_cattle", 1], ["lumberyard", 1], ["quarry", 1]],
  metropolis2: [["cottage_s", 20], ["cottage_m", 20], ["cottage_l", 14], ["bakery", 3], ["butcher", 2], ["smithy", 2], ["inn", 2], ["farm_wheat", 2], ["farm_terrace", 2], ["farm_cattle", 1], ["lumberyard", 1], ["quarry", 1]],
  metropolis3: [["cottage_s", 24], ["cottage_m", 22], ["cottage_l", 16], ["bakery", 3], ["butcher", 3], ["smithy", 2], ["inn", 3], ["farm_wheat", 2], ["farm_cattle", 2], ["lumberyard", 2], ["quarry", 1]],
  capital: [["cottage_s", 36], ["cottage_m", 34], ["cottage_l", 24], ["bakery", 5], ["butcher", 4], ["smithy", 3], ["inn", 4], ["farm_wheat", 3], ["farm_terrace", 2], ["farm_cattle", 2], ["lumberyard", 2], ["quarry", 1]],
};""", "tiers 13")
rep("""  if (st.tier === "city" && !st.wall) { const n = buildWall(dim, s, st); if (n) marks.push(`city wall raised (${n} blocks)`); }""",
    """  if (st.kit) {
    // D-C534 §3: walls as queued ops — ring 1 at city, ring 2 at metropolis I
    if (ti >= 4 && !(st.walls || []).some((w) => w.ring === 1)) { const n = queueWall(s, st, 1); if (n) marks.push(`city wall staked (${n} cells)`); }
    if (ti >= 6 && !(st.walls || []).some((w) => w.ring === 2)) { const n = queueWall(s, st, 2); if (n) marks.push(`second wall staked (${n} cells)`); }
  } else if (st.tier === "city" && !st.wall) { const n = buildWall(dim, s, st); if (n) marks.push(`city wall raised (${n} blocks)`); }""", "wall queue")
rep("""    // D-C534 §2.3: still no room and the streets cannot grow -> look for a NEW BENCH joined by a switchback road
    else if (!(st.kitQueue || []).length && (st.benchFail === undefined || s.simDays - st.benchFail >= BENCH_WAIT)) startBenchJob(st);
  }""", """    // D-C534 §2.3: still no room and the streets cannot grow -> look for a NEW BENCH joined by a switchback road
    else if (!(st.kitQueue || []).length && (st.benchFail === undefined || s.simDays - st.benchFail >= BENCH_WAIT)) startBenchJob(st);
  }
  // D-C534 §3: from tier town the blocks close — one cross street a day between adjacent parallel streets
  if (st.kit && st.phase === "built" && TIER_IDX(st.tier) >= 2 && !(st.kitQueue || []).length) { try { closeBlocks(s, st); } catch (e) { console.warn(`[CIV-CLOCK] blocks: ${e}`); } }""", "close blocks daily")


rep("""      rest.roadLaid = st.roadLaid || 0;
      rest.benchFail = st.benchFail;""", """      rest.roadLaid = st.roadLaid || 0;
      rest.benchFail = st.benchFail;
      rest.crossroads = st.crossroads || 0; rest.blocksClosed = st.blocksClosed || 0;
      rest.walls = (st.walls || []).map((w) => ({ ring: w.ring, n: w.n, gates: w.gates.length, laid: w.laid, box: w.box }));
      rest.leftover = (leftover || []).length;""", "status grid")


# ================================================================ PHASE C (D-C534 §4): the material economy + wages
# population = RECORDS (the settlers arrive with the plan; the villager entities appear when a home is furnished)
rep("""function population(s, st) {
  return plotsOf(s, st).reduce((n, b) => n + (b.villagers ? b.villagers.length : 0), 0);
}""", """function population(s, st) {
  return plotsOf(s, st).reduce((n, b) => n + (b.people !== undefined ? b.people : (b.villagers ? b.villagers.length : (HOUSEHOLD[short(b)] || 0))), 0);
}
function households(s, st) { return plotsOf(s, st).filter((b) => (HOUSEHOLD[short(b)] || 0) > 0 && !b.closed).length; }""", "population records")
# the ledger carried into v2; the founding stock; the day's context
rep("""function stepEconomy(s, st, days, events) {
  if (!st.ledger) st.ledger = ECON.newLedger();
  st.dayAcc = (st.dayAcc || 0) + days;
  while (st.dayAcc >= 1) {
    st.dayAcc -= 1;
    const L = st.ledger;
    try { const dim = world.getDimension(st.dim); for (const b of plotsOf(s, st)) if (b.stage >= 4 && (short(b) === "farm_wheat" || short(b) === "farm_terrace")) harvestFarm(dim, b, st); } catch { /* unloaded */ }
    const evs = ECON.dayStep(L, shopsOf(s, st), population(s, st));""",
"""/** the settlers' wagons (D-C534 §4): the founding plots' walls, roofs and furnishings + 20 %, food for 20 days, and the
 *  founding purse — the foundations' stone is dug on site (s0 costs labour only) */
function genesisStock(s, st) {
  const L = st.ledger;
  const need = {};
  for (const b of plotsOf(s, st)) {
    const bom = BUILDINGS[b.family].bom || [];
    for (let k = 1; k < bom.length; k++) for (const [m, n] of Object.entries(bom[k])) need[m] = (need[m] || 0) + n;
  }
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
function produceDaily(s, st) {
  const out = {};
  let dim;
  try { dim = world.getDimension(st.dim); } catch { return out; }
  for (const b of plotsOf(s, st)) {
    if (b.stage < 4 || b.closed) continue;
    const kind = short(b);
    const stations = BUILDINGS[b.family].work || 1;
    try {
      if (kind === "quarry") { const n = digQuarry(dim, b, st, TIER_IDX(st.tier), stations * 24); if (n !== undefined) out[b.id] = n; }
      else if (kind === "lumberyard") { const r = clearForest(dim, b, st, TIER_IDX(st.tier), stations); if (r && r.trees !== undefined) out[b.id] = r.logs; }
      else if (kind === "farm_wheat" || kind === "farm_terrace") { const n = harvestFarm(dim, b, st); if (n !== undefined && n > 0) out[b.id] = n; }
    } catch { /* unloaded: the abstract rate stands in */ }
  }
  return out;
}
function stepEconomy(s, st, days, events) {
  if (!st.ledger) { st.ledger = ECON.newLedger(); genesisStock(s, st); }
  if (st.ledger.v !== 2) st.ledger = ECON.upgradeLedger(st.ledger);
  st.dayAcc = (st.dayAcc || 0) + days;
  while (st.dayAcc >= 1) {
    st.dayAcc -= 1;
    const L = st.ledger;
    const produced = produceDaily(s, st);
    const neighbours = (st.roads || []).map((r) => { const o = s.settlements.find((x) => x.id === r.to); return o && o.ledger ? { id: o.id, stock: o.ledger.stock, prices: o.ledger.prices, dist: r.length || 300 } : null; }).filter(Boolean);
    const inns = plotsOf(s, st).filter((b) => short(b) === "inn" && b.stage >= 4 && !b.closed).length;
    const demand = constructionDemand(s, st);
    // hiring: outsiders lodged at the inns when the waiting work exceeds five days of the town's own builders
    const queued = plotsOf(s, st).filter((b) => b.waiting).reduce((a, b) => a + (b.waiting.blocks || 0), 0);
    const own = Math.max(0, Math.round(population(s, st) * ECON.WORKERS_PER_PERSON) - shopsOf(s, st).length);
    L.hired = queued > own * ECON.BLOCKS_PER_BUILDER_DAY * 5 ? Math.min(10 * inns, Math.ceil(queued / (ECON.BLOCKS_PER_BUILDER_DAY * 5))) : 0;
    const evs = ECON.dayStep(L, { shops: shopsOf(s, st), population: population(s, st), households: households(s, st), inns, produced, neighbours, demand });
    if (L.hired) { const hw = L.hired * ECON.WAGE.hired; const paid = Math.min(L.treasury, hw); L.treasury -= paid; L.purse += paid; }
    st.buildBudget = (own + L.hired) * ECON.BLOCKS_PER_BUILDER_DAY;""", "stepEconomy v2")
rep("""    for (const g of ECON.GOODS) {
      st.shortDays[g] = shortNow.has(g) ? (st.shortDays[g] || 0) + 1 : 0;
      if (st.shortDays[g] >= CHARTER_DAYS && !st.declining) {""", """    for (const g of Object.keys(CHARTER)) {
      st.shortDays[g] = shortNow.has(g) ? (st.shortDays[g] || 0) + 1 : 0;
      if (st.shortDays[g] >= CHARTER_DAYS && !st.declining) {""", "charter goods")
# the stage gate in advance(): materials + wages + the day's builder budget
rep("""    b.progress += d;
    while (b.stage < last && b.progress >= STAGE_DAYS[b.stage]) {
      b.progress -= STAGE_DAYS[b.stage];
      b.stage += 1;
      b.pending.push(b.stage);
      events.push(`#${b.id} ${short(b)} -> ${STAGE_NAMES[b.stage]}`);
    }
    if (b.stage >= last) b.progress = 0;""", """    b.progress += d;
    while (b.stage < last && b.progress >= STAGE_DAYS[b.stage]) {
      // D-C534 §4: the next stage is built only from stock, wages and builders on hand (a settlement's ledger)
      const stt = b.settlement !== undefined ? s.settlements.find((x) => x.id === b.settlement) : null;
      if (stt && stt.ledger && stt.ledger.v === 2) {
        const L = stt.ledger;
        const bill = stageBillOf(b, b.stage + 1);
        const budget = stt.buildBudget === undefined ? Infinity : stt.buildBudget;
        const miss = ECON.missing(L, bill, budget);
        if (Object.keys(miss).length) {
          b.progress = STAGE_DAYS[b.stage];                                  // ready, waiting
          const key = Object.keys(miss).join(",");
          if (b.waitKey !== key) { b.waitKey = key; stt.log.push(`day ${s.simDays.toFixed(0)}: #${b.id} ${short(b)} waits for ${Object.entries(miss).map(([m, n]) => `${n} ${m}`).join(", ")}`); }
          b.waiting = { ...miss, blocks: bill.blocks };
          break;
        }
        ECON.pay(L, bill);
        stt.buildBudget = budget - bill.blocks;
        if (b.waiting) stt.log.push(`day ${s.simDays.toFixed(0)}: #${b.id} ${short(b)} ${STAGE_NAMES[b.stage + 1]} built (${Object.entries(bill.mats).map(([m, n]) => `${n} ${m}`).join(", ") || "labour"}; ${bill.wages} p wages)`);
        delete b.waiting; delete b.waitKey;
      }
      b.progress -= STAGE_DAYS[b.stage];
      b.stage += 1;
      b.pending.push(b.stage);
      events.push(`#${b.id} ${short(b)} -> ${STAGE_NAMES[b.stage]}`);
    }
    if (b.stage >= last) b.progress = 0;""", "stage gate")
# the status line in coins
rep("""    if (st.ledger) say(p, `§7    treasury ${Math.round(st.ledger.treasury)} coin · fed ${Math.round((st.ledger.prosperity.slice(-1)[0] || 0) * 100)} % · ` +
      ECON.GOODS.map((g) => `${g} ${Math.floor(st.ledger.stock[g])}@${st.ledger.prices[g]}`).join(" "));""",
    """    if (st.ledger) say(p, `§7    treasury ${Math.floor(st.ledger.treasury / ECON.COIN)} coin · purse ${Math.floor((st.ledger.purse || 0) / ECON.COIN)} · builders ${st.ledger.builders || 0}${st.ledger.hired ? ` (+${st.ledger.hired} hired)` : ""} · fed ${Math.round((st.ledger.prosperity.slice(-1)[0] || 0) * 100)} % · ` +
      ECON.GOODS.map((g) => `${g} ${Math.floor(st.ledger.stock[g])}@${st.ledger.prices[g]}p`).join(" "));""", "status coins")


# ---------------------------------------------------------------- D-C534 §4: the quarry is WORKED daily (a growing pit), the yard fells daily
rep("""function digQuarry(dim, b, st, tierIdx) {
  const def = BUILDINGS[b.family];
  const c = backOf(b, def);
  const r = 4 + 2 * tierIdx, depth = 2 + tierIdx;
  const dirx = b.rot === 0 ? 1 : b.rot === 2 ? -1 : 0, dirz = b.rot === 1 ? 1 : b.rot === 3 ? -1 : 0;   // away from the street
  const cx = c.x + dirx * (r + 1), cz = c.z + dirz * (r + 1);
  let dug = 0;
  const occupied = occupiedTest(load(), st);
  for (let i = -r; i <= r; i++) for (let j = -r; j <= r; j++) {
    const d = Math.max(Math.abs(i), Math.abs(j));
    const steps = Math.min(depth, Math.floor((r - d) / 2) + 1);         // deeper toward the middle
    if (steps <= 0) continue;
    const x = cx + i, z = cz + j;
    if (occupied(x, z)) continue;
    try {
      const g = groundAt(dim, x, z);
      if (g === undefined) continue;
      for (let y = g; y > g - steps; y--) {
        const blk = dim.getBlock({ x, y, z });
        if (!blk || blk.typeId === "minecraft:air" || blk.typeId === "minecraft:water" || blk.typeId === "minecraft:bedrock") continue;
        if (/stone|andesite|diorite|granite|deepslate|tuff|ore|gravel/.test(blk.typeId)) dug++;
        blk.setType("minecraft:air");
      }
      // plants above
      for (let y = g + 1; y <= g + 2; y++) { const up = dim.getBlock({ x, y, z }); if (up && up.typeId !== "minecraft:air" && !isGround(up.typeId)) up.setType("minecraft:air"); }
    } catch { /* unloaded */ }
  }
  if (st.ledger) st.ledger.stock.stone += dug;
  b.dug = (b.dug || 0) + dug;
  return dug;
}""", """/** the QUARRY is worked: a stepped pit behind the yard that grows ring by ring and deeper toward the middle, at most
 *  maxBlocks a call (a day's work for its quarrymen); the pit's radius grows with the tier (4 + 2 per tier) and the
 *  settlement's needs (one more ring when the tier's pit is worked out, up to QUARRY_R_MAX). Returns the STONE dug
 *  (stone-class blocks), undefined when the pit's chunk is not loaded. The stone goes to the ledger by the caller. */
const QUARRY_R_MAX = 14, QUARRY_D_MAX = 9;
function digQuarry(dim, b, st, tierIdx, maxBlocks = Infinity) {
  const def = BUILDINGS[b.family];
  const c = backOf(b, def);
  const pit = (b.pit = b.pit || { r: 4 + 2 * tierIdx, depth: 2 + tierIdx, i: 0 });
  pit.r = Math.max(pit.r, 4 + 2 * tierIdx); pit.depth = Math.max(pit.depth, 2 + tierIdx);
  const dirx = b.rot === 0 ? 1 : b.rot === 2 ? -1 : 0, dirz = b.rot === 1 ? 1 : b.rot === 3 ? -1 : 0;   // away from the street
  const cx = c.x + dirx * (pit.r + 1), cz = c.z + dirz * (pit.r + 1);                                  // the pit grows away from the yard
  let dug = 0, removed = 0, seen = 0, unloaded = false;
  const occupied = occupiedTest(load(), st);
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
      const floor = b.pitTop - steps;
      for (let y = Math.min(g, b.pitTop); y > floor && removed < maxBlocks; y--) {
        const blk = dim.getBlock({ x, y, z });
        if (!blk || blk.typeId === "minecraft:air" || blk.typeId === "minecraft:water" || blk.typeId === "minecraft:bedrock") continue;
        if (/stone|andesite|diorite|granite|deepslate|tuff|ore|gravel/.test(blk.typeId)) dug++;
        blk.setType("minecraft:air"); removed++;
      }
      for (let y = g + 1; y <= g + 2; y++) { const up = dim.getBlock({ x, y, z }); if (up && up.typeId !== "minecraft:air" && !isGround(up.typeId)) up.setType("minecraft:air"); }
    } catch { unloaded = true; break; }
  }
  if (unloaded && removed === 0) return undefined;
  pit.i = (pit.i + seen) % cells;
  // a worked-out pit grows a ring (and a step) up to the caps
  if (removed === 0 && seen >= cells) { if (pit.r < QUARRY_R_MAX) pit.r += 1; else if (pit.depth < QUARRY_D_MAX) pit.depth += 1; pit.i = 0; }
  b.dug = (b.dug || 0) + dug;
  return dug;
}""", "quarry daily")
rep("""  if (st.ledger) st.ledger.stock.timber += logs;
  b.felled = (b.felled || 0) + trees;
  return { trees, logs };""", """  b.felled = (b.felled || 0) + trees;
  return { trees, logs };""", "forest no ledger")
rep("""  if (n && st.ledger) st.ledger.stock.grain += n;
  b.harvested = (b.harvested || 0) + n;
  return n;""", """  if (n && st.ledger) st.ledger.stock.grain += n;                 // the fields' real wheat is a bonus over the farm's rate
  b.harvested = (b.harvested || 0) + n;
  return n;""", "farm keep")
rep("""      if (kind === "quarry") { const dug = digQuarry(dim, b, st, ti); if (dug) marks.push(`quarry dug ${dug} stone`); }
      if (kind === "lumberyard") { const r = clearForest(dim, b, st, ti); if (r.trees) marks.push(`lumberyard felled ${r.trees} trees (${r.logs} logs)`); }""",
    """      if (kind === "quarry") { const dug = digQuarry(dim, b, st, ti, 400); if (dug) { marks.push(`quarry dug ${dug} stone`); if (st.ledger) st.ledger.stock.stone += dug; } }
      if (kind === "lumberyard") { const r = clearForest(dim, b, st, ti); if (r.trees) { marks.push(`lumberyard felled ${r.trees} trees (${r.logs} logs)`); if (st.ledger) st.ledger.stock.timber += r.logs; } }""", "marks ledger")
rep("""      else if (kind === "farm_wheat" || kind === "farm_terrace") { const n = harvestFarm(dim, b, st); if (n !== undefined && n > 0) out[b.id] = n; }""",
    """      else if (kind === "farm_wheat" || kind === "farm_terrace") harvestFarm(dim, b, st);""", "farms bonus")


rep("""      const summary = ledger ? { day: ledger.day, treasury: Math.round(ledger.treasury), stock: ledger.stock, prices: ledger.prices, prosperity: ledger.prosperity.slice(-5), closing: ledger.closing } : null;""",
    """      const summary = ledger ? { day: ledger.day, treasury: Math.round(ledger.treasury), purse: Math.round(ledger.purse || 0), minted: ledger.minted, sunk: ledger.sunk, builders: ledger.builders, hired: ledger.hired, arrears: ledger.arrears,
                                 stock: Object.fromEntries(Object.entries(ledger.stock).map(([k, v]) => [k, Math.floor(v)])), prices: ledger.prices, prosperity: ledger.prosperity.slice(-5), closing: ledger.closing, orders: (ledger.orders || []).length, drift: ledger.drift || 0 } : null;
      rest.waiting = plotsOf(s, st).filter((b) => b.waiting).map((b) => [b.id, b.waiting]).slice(0, 6);
      rest.waitingN = plotsOf(s, st).filter((b) => b.waiting).length;
      rest.buildBudget = st.buildBudget;""", "status ledger v2")


# ---------------------------------------------------------------- D-C535: class-based comparisons, representation, population density, daughters by class
rep("""  if (hardened) marks.push(`streets ${ti >= 2 ? "cobbled" : "gravelled"} (${hardened})`);
  if (st.kit && ti >= 2) {                                       // v1.3.219: town width + a park (his 18:02)""",
    """  if (hardened) marks.push(`streets ${TIER_CLASS(st.tier) >= 1 ? "cobbled" : "gravelled"} (${hardened})`);
  if (st.kit && TIER_CLASS(st.tier) >= 1) {                      // v1.3.219: town width + a park (his 18:02)""", "marks class 1")
rep("""    if (ti >= 4 && !(st.walls || []).some((w) => w.ring === 1)) { const n = queueWall(s, st, 1); if (n) marks.push(`city wall staked (${n} cells)`); }
    if (ti >= 6 && !(st.walls || []).some((w) => w.ring === 2)) { const n = queueWall(s, st, 2); if (n) marks.push(`second wall staked (${n} cells)`); }""",
    """    if (TIER_CLASS(st.tier) >= 2 && !(st.walls || []).some((w) => w.ring === 1)) { const n = queueWall(s, st, 1); if (n) marks.push(`city wall staked (${n} cells)`); }
    if (TIER_CLASS(st.tier) >= 3 && !(st.walls || []).some((w) => w.ring === 2)) { const n = queueWall(s, st, 2); if (n) marks.push(`second wall staked (${n} cells)`); }""", "walls class")
rep("""  if (st.kit && st.phase === "built" && TIER_IDX(st.tier) >= 2 && !(st.kitQueue || []).length) { try { closeBlocks(s, st); } catch (e) { console.warn(`[CIV-CLOCK] blocks: ${e}`); } }""",
    """  if (st.kit && st.phase === "built" && TIER_CLASS(st.tier) >= 1 && !(st.kitQueue || []).length) { try { timed("close blocks", () => closeBlocks(s, st)); } catch (e) { console.warn(`[CIV-CLOCK] blocks: ${e}`); } }""", "blocks class")
# (0.0.15: the grid windows are reserved on every street from the start — the tier-class form of this rep is retired)
rep("""  const surface = tierIdx >= 2 ? "minecraft:cobblestone" : tierIdx >= 1 ? "minecraft:gravel" : null;""",
    """  const surface = tierIdx >= 3 ? "minecraft:cobblestone" : tierIdx >= 1 ? "minecraft:gravel" : null;""", "harden class")
# population: records with the tier's density
rep("""function population(s, st) {
  return plotsOf(s, st).reduce((n, b) => n + (b.people !== undefined ? b.people : (b.villagers ? b.villagers.length : (HOUSEHOLD[short(b)] || 0))), 0);
}""", """function population(s, st) {
  const dens = DENSITY[TIER_CLASS(st.tier)] || 1;
  return plotsOf(s, st).reduce((n, b) => n + Math.round((HOUSEHOLD[short(b)] || 0) * (b.closed ? 0 : dens)), 0);
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
}""", "population density + representation")
rep("""  const next = TIERS[TIERS.indexOf(st.tier) + 1];
  if (next && st.phase !== "reading" && plotsOf(s, st).length > 0 && age >= TIER_DAYS[next] && allRoofed(s, st) && prosperityOk(st)) tierUp(s, st, next, events);
}""", """  const next = TIERS[TIERS.indexOf(st.tier) + 1];
  if (next && st.phase !== "reading" && plotsOf(s, st).length > 0 && age >= TIER_DAYS[next] && allRoofed(s, st) && prosperityOk(st)) {
    if (representationOk(s, st, next)) tierUp(s, st, next, events);
    else if (!st.repWaitLogged || s.simDays - st.repWaitLogged > 30) {
      const r = representation(s, st), q = REP_REQ[next];
      st.repWaitLogged = s.simDays;
      st.log.push(`day ${s.simDays.toFixed(0)}: ${TIER_LABEL[next]} needs ${q[0]} settlements represented here (${q[1]} cities, ${q[2]} metropolises) — has ${r.n} (${r.cities} cities, ${r.metropolises} metropolises)${r.names.length ? `: ${r.names.join(", ")}` : ""}`);
    }
  }
}""", "tier gate rep")
rep("""  st.tier = tier;
  st.tierDay = s.simDays;
  st.log.push(`day ${s.simDays.toFixed(0)}: ${tier} (+${added.length} plots)`);
  events.push(`§b${st.name} -> ${tier.toUpperCase()} (+${added.length} plots)`);""", """  st.tier = tier;
  st.tierDay = s.simDays;
  st.log.push(`day ${s.simDays.toFixed(0)}: ${tierLabel(st)} (+${added.length} plots; ${population(s, st)} people)`);
  events.push(`§b${st.name} -> ${tierLabel(st).toUpperCase()} (+${added.length} plots)`);""", "tier label")
# daughters by class, sequential (the next one when the last road is done and DAUGHTER_GAP days passed)
rep("""function maybeFoundDaughter(s, st, events) {
  if (st.daughter || !st.ledger || TIER_IDX(st.tier) < 2 || population(s, st) < DAUGHTER_POP) return;""",
    """function maybeFoundDaughter(s, st, events) {
  if (!st.ledger || TIER_CLASS(st.tier) < 1 || population(s, st) < DAUGHTER_POP) return;
  st.daughters = st.daughters || (st.daughter && st.daughter.id ? [st.daughter.id] : []);
  if (st.daughters.length >= DAUGHTERS_MAX[TIER_CLASS(st.tier)]) return;
  if (st.daughter && (st.roadPending || s.simDays - st.daughter.day < DAUGHTER_GAP)) return;""", "daughters class")
rep("""  st.daughter = { x: cx, z: cz, day: s.simDays };""", """  st.daughter = { x: cx, z: cz, day: s.simDays };
  const pickAng = pick;
  void pickAng;""", "daughter record")
rep("""  child.mother = st.id;
  child.name = `${st.name}'s daughter`;
  st.daughter.id = child.id;
  st.roadPending = true;""", """  child.mother = st.id;
  child.name = st.daughters.length ? `${st.name}'s daughter ${st.daughters.length + 1}` : `${st.name}'s daughter`;
  st.daughter.id = child.id;
  st.daughters.push(child.id);
  st.roadPending = true; st.roadTries = 0;""", "daughter list")
rep("""  const pick = rng((st.seed * 31 + 7) >>> 0);
  const dist = DAUGHTER_DIST[0] + Math.floor(pick() * (DAUGHTER_DIST[1] - DAUGHTER_DIST[0]));""",
    """  const pick = rng((st.seed * 31 + 7 + (st.daughters.length * 977)) >>> 0);
  const dist = DAUGHTER_DIST[0] + Math.floor(pick() * (DAUGHTER_DIST[1] - DAUGHTER_DIST[0]));""", "daughter seed")
# status: tier label
rep("""    say(p, `§b  ${st.name} at ${st.x0} ${st.z0}: ${st.tier.toUpperCase()} · ${plots.length} plots (${plots.filter((b) => b.closed).length} closed) · ` +""",
    """    say(p, `§b  ${st.name} at ${st.x0} ${st.z0}: ${tierLabel(st).toUpperCase()} · ${plots.length} plots (${plots.filter((b) => b.closed).length} closed) · ` +""", "status label")


# ---------------------------------------------------------------------------------------------- 0.0.13: DAY SLICES (D-C537/D-C542)
# the day's build budget, wages and hiring are DAILY: a long advance (a 'skip', or the world ran without the clock) used to
# apply all its days to the buildings in one pass with one budget -> six plots waited "for builders" for 46 days (0.0.13)
rep("""function advance(days) {
  const s = load();
  if (days <= 0) return [];
  s.simDays += days;
  const events = [];""", """const LAG_SLICES = 5;                         // D-C537: a lag is worked off at most 5 whole days per clock beat
/** advance the village by `days`: whole-day slices (the budget, wages and hiring are daily), at most maxSlices now, the
 *  rest carried in s.lag and worked off on the kit beat (one slice per beat) */
function advance(days, maxSlices = LAG_SLICES) {
  const s = load();
  let left = (s.lag || 0) + Math.max(0, days || 0);
  let events = [];
  for (let n = 0; left > 1e-9 && n < maxSlices; n++) { const d = Math.min(1, left); events = events.concat(advanceOnce(d)); left -= d; }
  s.lag = left > 1e-9 ? left : 0;
  flushPending();
  save();
  return events;
}
function advanceOnce(days) {
  const s = load();
  if (days <= 0) return [];
  s.simDays += days;
  const events = [];""", "advance in day slices")
rep("""  for (const st of s.settlements) {
    stepSettlement(s, st, days, events);
    if (!st.firstMarks && plotsOf(s, st).length && plotsOf(s, st).every((b) => b.stage >= 4)) { st.firstMarks = true; livingMarks(s, st, events); }
  }
  flushPending();
  save();
  return events;
}""", """  for (const st of s.settlements) {
    stepSettlement(s, st, days, events);
    if (!st.firstMarks && plotsOf(s, st).length && plotsOf(s, st).every((b) => b.stage >= 4)) { st.firstMarks = true; livingMarks(s, st, events); }
  }
  return events;
}""", "advanceOnce tail")
rep("""  const busy = s.settlements.some((x) => x.kit && ((x.kitQueue && x.kitQueue.length) || (x.park && !x.park.done)));
  if (!busy) return;""", """  if (s.lag > 0) { try { advance(0, 1); } catch (e) { console.warn(`[CIV-CLOCK] lag slice: ${e}`); } }   // one carried day per beat (a paused clock still owes its skipped days)
  const busy = s.settlements.some((x) => x.kit && ((x.kitQueue && x.kitQueue.length) || (x.park && !x.park.done)));
  if (!busy) return;""", "lag on the kit beat")
rep("""    const evs = advance(days);
    const shown = evs.length > 12 ? evs.slice(0, 12).join(", ") + ` … (+${evs.length - 12})` : evs.join(", ");
    reply(`§e[CLOCK] +${days} village day(s) -> day ${s.simDays.toFixed(2)}${evs.length ? ": " + shown : " (no stage change)"}`);
    return;""", """    const evs = advance(days);                                 // the first LAG_SLICES days now, the rest one per beat
    const shown = evs.length > 12 ? evs.slice(0, 12).join(", ") + ` … (+${evs.length - 12})` : evs.join(", ");
    reply(`§e[CLOCK] +${days} village day(s) -> day ${s.simDays.toFixed(2)}${s.lag > 0 ? ` (${s.lag.toFixed(0)} more day(s) run on the beat)` : ""}${evs.length ? ": " + shown : " (no stage change)"}`);
    return;""", "skip reply")
rep("""      rest.buildBudget = st.buildBudget;""", """      rest.buildBudget = st.buildBudget;
      rest.lag = s.lag || 0;                                               // the probe waits for the carried days""", "lag in status")


# 0.0.14: inter-settlement payments are money that crossed between two ledgers — the invariant counts it as trade in / out
# (the 0.0.14 ledger reported a 49,659 p "drift" that was only the daughters' purchases)
rep("""      const pay = n * Math.min(pa, pb);
      to.ledger.treasury -= pay; from.ledger.treasury += pay;""", """      const pay = n * Math.min(pa, pb);
      to.ledger.treasury -= pay; from.ledger.treasury += pay;
      to.ledger.sunk += pay; from.ledger.tradeIn = (from.ledger.tradeIn || 0) + pay;      // the buyer's money left, the seller's came in""", "trade money accounting")


# ---------------------------------------------------------------------------------------------- D-C536: THE CENSUS (pw_civ_people.js)
rep("""import * as ECON from "./pw_civ_economy.js";""", """import * as ECON from "./pw_civ_economy.js";
import * as PEOPLE from "./pw_civ_people.js";                    // D-C536: the census — relationships, happiness, gossip""", "people import")
rep("""function population(s, st) {
  const dens = DENSITY[TIER_CLASS(st.tier)] || 1;""", """// ---- THE CENSUS (D-C536): people as RECORDS per settlement (names, homes, jobs, kin, friends, mood, rumours). The hands
// (embodied villagers) take their names from it; the ledger's population stays the dwellings' count until C2 (hands vs census)
function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }
/** dwellings with room: capacity = HOUSEHOLD x DENSITY (tenements at the high tiers) minus the people living there */
function homeRoom(s, st) {
  const dens = DENSITY[TIER_CLASS(st.tier)] || 1, P = census(st), living = {};
  for (const p of PEOPLE.alive(P)) if (p.home) living[p.home] = (living[p.home] || 0) + 1;
  return plotsOf(s, st).filter((b) => (HOUSEHOLD[short(b)] || 0) > 0 && b.stage >= 4 && !b.closed)
    .map((b) => ({ id: b.id, room: Math.max(0, Math.round((HOUSEHOLD[short(b)] || 0) * dens) - (living[b.id] || 0)) }));
}
/** the posts: every open shop's stations minus the people already at them */
function jobPosts(s, st) {
  const P = census(st), filled = {};
  for (const p of PEOPLE.alive(P)) if (p.job) filled[p.job] = (filled[p.job] || 0) + 1;
  return shopsOf(s, st).filter((sh) => !sh.closed).map((sh) => ({ id: sh.id, kind: sh.kind, vacancies: Math.max(0, sh.stations - (filled[sh.id] || 0)) }));
}
/** a household moves in: n people recorded at the dwelling (their names go on the villagers at the door) */
function censusMoveIn(s, st, b, n) {
  const P = census(st), names = [];
  for (let i = 0; i < n; i++) { const p = PEOPLE.newPerson(P, Math.floor(s.simDays), { home: b.id, seed: b.id * 31 + i * 7 + (st.seed || 0), age: 20 + ((b.id * 7 + i * 11) % 25) }); names.push(p.name); }
  return names;
}
/** one day of the census: contacts, weddings, births, deaths, inheritance, mood, migration, rumours, threads */
function censusDay(s, st, events) {
  const P = census(st), L = st.ledger;
  const fed = L ? (L.prosperity.slice(-1)[0] ?? 1) : 1, paid = !L || !(L.arrears > 0);
  const r = PEOPLE.dayStep(P, { day: Math.floor(s.simDays), fed, paid, homes: homeRoom(s, st), jobs: jobPosts(s, st), seed: st.seed || 1, name: st.name, events: [] });
  for (const e of r.events) {
    st.log.push(`day ${s.simDays.toFixed(0)}: ${e.text}`);
    if (e.kind === "wedding" || e.kind === "birth" || e.kind === "death" || e.kind === "arrival" || e.kind === "inherit") events.push(`§d${st.name}: ${e.text}`);
  }
  st.mood = Math.round(r.meanMood);
}
const MOOD_GATE = 45;                                   // D-C536: an unhappy town does not rise a tier
function moodOk(st) { return !st.people || !PEOPLE.alive(st.people).length || (st.mood ?? 55) >= MOOD_GATE; }
function population(s, st) {
  const dens = DENSITY[TIER_CLASS(st.tier)] || 1;""", "census helpers")
rep("""  for (let i = 0; i < n; i++) {
    try {
      const v = dim.spawnEntity(VILLAGER_ID, { x: front.x + 0.5, y, z: front.z + 0.5 });
      const name = NAMES[(s.nextId * 7 + i * 13 + (st ? st.seed : 0)) % NAMES.length];""", """  const names = st ? censusMoveIn(s, st, b, n) : [];                  // D-C536: the census names the household
  for (let i = 0; i < n; i++) {
    try {
      const v = dim.spawnEntity(VILLAGER_ID, { x: front.x + 0.5, y, z: front.z + 0.5 });
      const name = names[i] || NAMES[(s.nextId * 7 + i * 13 + (st ? st.seed : 0)) % NAMES.length];""", "move-in names")
rep("""    try { nameTrades(s, st); noticeBoard(world.getDimension(st.dim), st); } catch (e) { console.warn(`[CIV-CLOCK] day: ${e}`); }""",
    """    try { censusDay(s, st, events); } catch (e) { console.warn(`[CIV-CLOCK] census: ${e}`); }
    try { nameTrades(s, st); noticeBoard(world.getDimension(st.dim), st); } catch (e) { console.warn(`[CIV-CLOCK] day: ${e}`); }""", "census day")
rep("""  if (next && st.phase !== "reading" && plotsOf(s, st).length > 0 && age >= TIER_DAYS[next] && allRoofed(s, st) && prosperityOk(st)) {
    if (representationOk(s, st, next)) tierUp(s, st, next, events);""", """  if (next && st.phase !== "reading" && plotsOf(s, st).length > 0 && age >= TIER_DAYS[next] && allRoofed(s, st) && prosperityOk(st) && moodOk(st)) {
    if (representationOk(s, st, next)) tierUp(s, st, next, events);""", "mood gate")
rep("""    const sign = blk.getComponent("minecraft:sign");
    if (sign) sign.setText(st.log.slice(-4).map((l) => l.replace(/^day (\\d+): /, "d$1 ").slice(0, 32)).join("\\n"));""",
    """    const sign = blk.getComponent("minecraft:sign");
    // D-C536: the freshest rumour heads the board, the chronicle's last lines follow
    const rum = st.people ? PEOPLE.board(st.people, Math.floor(load().simDays)).rumours[0] : null;
    const lines = (rum ? [rum] : []).concat(st.log.slice(-4)).slice(0, 4);
    if (sign) sign.setText(lines.map((l) => l.replace(/^day (\\d+): /, "d$1 ").slice(0, 32)).join("\\n"));""", "board rumour")
rep("""      rest.buildBudget = st.buildBudget;""", """      rest.buildBudget = st.buildBudget;
      if (st.people) { const al = PEOPLE.alive(st.people); rest.census = { n: al.length, mood: st.mood ?? null, married: al.filter((p) => p.spouse).length, children: al.filter((p) => PEOPLE.stage(p, Math.floor(s.simDays)) === "child").length, rumours: st.people.rumours.length, threads: st.people.threads.filter((t) => t.state === "open").length }; }""", "census in status")


rep("""      const { ledger, log, shortDays, kitQueue, streets, profile, leftover, triedTerraces, ...rest } = st;   // a script event message is capped (2 KB): keep it compact""",
    """      const { ledger, log, shortDays, kitQueue, streets, profile, leftover, triedTerraces, people, ...rest } = st;   // a script event message is capped (2 KB): keep it compact (the census stays home)
      void people;""", "census out of the status payload")


# D-C542: the ticking cores — the daily sweep, the tickslots command, status
rep("""    try { censusDay(s, st, events); } catch (e) { console.warn(`[CIV-CLOCK] census: ${e}`); }""",
    """    try { censusDay(s, st, events); } catch (e) { console.warn(`[CIV-CLOCK] census: ${e}`); }
    try { coreSweep(s); } catch (e) { console.warn(`[CIV-CLOCK] cores: ${e}`); }""", "core sweep daily")
rep("""  if (cmd === "pause" || cmd === "resume") {""", """  if (cmd === "tickslots") {                                   // D-C542: how many ticking areas the clock may hold (by host)
    const n = parseInt(a || "", 10);
    if (!(n >= 0 && n <= 9)) { reply(`§e[CLOCK] ticking slots: ${coreState(s).slots} (areas: ${Object.values(coreState(s).areas).map((x) => `${x.name} ${x.why}`).join("; ") || "none"}) — usage: tickslots <0..9>`); return; }
    coreState(s).slots = n; save(); reply(`§e[CLOCK] ticking slots set to ${n}`); return;
  }
  if (cmd === "pause" || cmd === "resume") {""", "tickslots command")
rep("""      rest.buildBudget = st.buildBudget;""", """      rest.buildBudget = st.buildBudget;
      rest.ticking = Object.values(coreState(s).areas).filter((x) => x.st === st.id).map((x) => [x.name, x.box, x.why]);""", "ticking in status")


# D-C542: a stage waiting for sleeping chunks asks for its ticking area; a settlement's core stays while a building is unfinished
rep("""function flushPending() {
  for (const b of load().buildings) {
    while (b.pending.length) {
      const k = b.pending[0];
      const ok = typeof k === "string" ? applyShopMark(b, k) : placeStage(b, k);
      if (!ok) break;
      b.pending.shift();
    }
  }
}""", """function flushPending() {
  const s = load();
  for (const b of s.buildings) {
    while (b.pending.length) {
      const k = b.pending[0];
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
}""", "stage wake")


# 0.0.16: a 10 s watchdog hang at the town grow — a slice timer on every entry point (what took longer than SLOW_MS is named)
rep("""function advance(days, maxSlices = LAG_SLICES) {
  const s = load();""", """const SLOW_MS = 150;
function timed(name, fn) { const t0 = Date.now(); try { return fn(); } finally { const ms = Date.now() - t0; if (ms > SLOW_MS) console.warn(`[CIV-CLOCK] slow: ${name} took ${ms} ms`); } }
function advance(days, maxSlices = LAG_SLICES) {
  const s = load();""", "timer helper")
rep("""  if (!s.paused && d > 0) advance(d * s.speed);""", """  if (!s.paused && d > 0) timed("advance", () => advance(d * s.speed));""", "time advance")
rep("""  if (s.lag > 0) { try { advance(0, 1); } catch (e) { console.warn(`[CIV-CLOCK] lag slice: ${e}`); } }   // one carried day per beat (a paused clock still owes its skipped days)""",
    """  if (s.lag > 0) { try { timed("lag slice", () => advance(0, 1)); } catch (e) { console.warn(`[CIV-CLOCK] lag slice: ${e}`); } }   // one carried day per beat (a paused clock still owes its skipped days)""", "time lag")
rep("""  const n = processKitQueue(s);""", """  const n = timed("kit queue", () => processKitQueue(s));""", "time queue")
rep("""  for (const st of s.settlements) if (st.park && !st.park.done && !(st.kitQueue && st.kitQueue.length)) { try { layPark(st); } catch (e) { console.warn(`[CIV-CLOCK] park: ${e}`); } }""",
    """  for (const st of s.settlements) if (st.park && !st.park.done && !(st.kitQueue && st.kitQueue.length)) { try { timed("park", () => layPark(st)); } catch (e) { console.warn(`[CIV-CLOCK] park: ${e}`); } }""", "time park")
rep("""function stepSettlement(s, st, days, events) {""", """function stepSettlement(s, st, days, events) { return timed(`settlement ${st.id} step`, () => stepSettlementBody(s, st, days, events)); }
function stepSettlementBody(s, st, days, events) {""", "time settlement step")
rep("""function tierUp(s, st, tier, events) {""", """function tierUp(s, st, tier, events) { return timed(`tier-up ${tier}`, () => tierUpBody(s, st, tier, events)); }
function tierUpBody(s, st, tier, events) {""", "time tier-up")


# ---------------------------------------------------------------------------------------------- C2.1: WALKING (pw_civ_walk.js)
rep("""import * as SHOP from "./pw_civ_shop.js";""", """import * as SHOP from "./pw_civ_shop.js";
import * as WALK from "./pw_civ_walk.js";                        // C2.1 (D-C541): villagers walk where the clock sends them""", "walk import")
# the census person rides on the villager as a tag (the schedule finds the job through it)
rep("""function censusMoveIn(s, st, b, n) {
  const P = census(st), names = [];
  for (let i = 0; i < n; i++) { const p = PEOPLE.newPerson(P, Math.floor(s.simDays), { home: b.id, seed: b.id * 31 + i * 7 + (st.seed || 0), age: 20 + ((b.id * 7 + i * 11) % 25) }); names.push(p.name); }
  return names;
}""", """function censusMoveIn(s, st, b, n) {
  const P = census(st), names = [];
  for (let i = 0; i < n; i++) { const p = PEOPLE.newPerson(P, Math.floor(s.simDays), { home: b.id, seed: b.id * 31 + i * 7 + (st.seed || 0), age: 20 + ((b.id * 7 + i * 11) % 25) }); names.push(p.name); (st.lastMoveIn = st.lastMoveIn || []).push(p.id); }
  return names;
}""", "move-in ids")
rep("""      const name = names[i] || NAMES[(s.nextId * 7 + i * 13 + (st ? st.seed : 0)) % NAMES.length];
      v.nameTag = name;""", """      const name = names[i] || NAMES[(s.nextId * 7 + i * 13 + (st ? st.seed : 0)) % NAMES.length];
      v.nameTag = name;
      if (st && st.lastMoveIn && st.lastMoveIn[i] !== undefined) v.addTag(`civ:person:${st.lastMoveIn[i]}`);   // C2.1: the census record""", "person tag")
rep("""  if (st) st.log.push(`day ${s.simDays.toFixed(0)}: ${n} moved into the ${short(b)} (#${b.id})`);
}""", """  if (st) { st.log.push(`day ${s.simDays.toFixed(0)}: ${n} moved into the ${short(b)} (#${b.id})`); delete st.lastMoveIn; }
}""", "move-in cleanup")
# the walk API + the schedule
rep("""// v1.3.219: the shopkeepers' module reads the clock through these""", """// C2.1 (D-C541 / D-C542): the walkers' module reads the clock through these; the SCHEDULE below sends everyone somewhere
// by the time of day — work in the morning, the square at dusk, home at night — and the keepers' own beat sends them to
// their stations. Nothing teleports; a walker that cannot get there is counted (st.walkStuck).
WALK.initWalk({
  cellOf: KIT.cellOf, dirs4: DIRS4,
  plotsOf: (st) => plotsOf(load(), st), plotCount: (st) => plotsOf(load(), st).length,
  doorFront: (b) => { const def = BUILDINGS[b.family]; if (!def) return null; const fr = doorFront(b, def); return { x: fr.x, z: fr.z, y: b.y + def.datum_y }; },
  arrived: (v, w) => { const s = load(); const st = s.settlements.find((x) => x.id === w.stId); if (st) st.walkArrived = (st.walkArrived || 0) + 1; },
  stuck: (v, w) => { const s = load(); const st = s.settlements.find((x) => x.id === w.stId); if (st) { st.walkStuck = (st.walkStuck || 0) + 1; st.log.push(`day ${s.simDays.toFixed(0)}: ${v.nameTag || "a villager"} could not reach ${Math.floor(w.target.x)} ${Math.floor(w.target.z)} (${w.mode}${w.cause ? `, ${w.cause}` : ""}${w.feet ? `, standing in ${w.feet} at ${Math.floor(v.location.x)} ${Math.floor(v.location.y)} ${Math.floor(v.location.z)}` : ""})`); } },
  groundAt: (dim, x, z) => groundAt(dim, x, z),                      // 0.0.22: straight-line waypoints off the walk graph stand on the ground
});
const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };
function goalFor(s, st, v, tod) {
  const tags = v.getTags();
  const pid = tags.find((t) => t.startsWith("civ:person:")), home = tags.find((t) => t.startsWith("civ:home:"));
  const homeB = home ? s.buildings.find((b) => b.id === Number(home.slice(9))) : null;
  const person = pid && st.people ? PEOPLE.byId(st.people, Number(pid.slice(11))) : null;
  const jobB = person && person.job ? s.buildings.find((b) => b.id === person.job) : null;
  const front = (b) => { const def = b && BUILDINGS[b.family]; if (!def) return null; const fr = doorFront(b, def); return { x: fr.x + 0.5, z: fr.z + 0.5, y: b.y + def.datum_y }; };
  const square = st.square ? { x: st.square.x + 6.5, z: st.square.z + 6.5, y: st.square.y + 1 } : null;
  if (tod >= SCHED.work[0] && tod < SCHED.work[1]) return jobB ? (jobB.station || front(jobB)) : (square || front(homeB));
  if (tod >= SCHED.dusk[0] && tod < SCHED.dusk[1]) return square || front(homeB);
  return front(homeB) || square;
}
system.runInterval(() => {
  const s = load();
  let tod;
  try { tod = world.getTimeOfDay(); } catch { return; }
  for (const st of s.settlements) {
    if (!st.kit || !st.square) continue;
    let vs;
    try { vs = world.getDimension(st.dim).getEntities({ tags: [`civ:settlement:${st.id}`], type: "minecraft:villager_v2" }); } catch { continue; }
    for (const v of vs) {
      if (v.hasTag("civ:keeper")) continue;                                  // the keepers' own beat (pw_civ_shop) sends them
      const g = goalFor(s, st, v, tod);
      if (!g) continue;
      if (Math.hypot(v.location.x - g.x, v.location.z - g.z) <= 3) { if (WALK.walking(v)) WALK.cancel(v); continue; }
      if (!WALK.walking(v)) WALK.send(v, st, g);
    }
  }
}, 100);
// v1.3.219: the shopkeepers' module reads the clock through these""", "walk api + schedule")
rep("""      rest.buildBudget = st.buildBudget;""", """      rest.buildBudget = st.buildBudget;
      rest.walk = { arrived: st.walkArrived || 0, stuck: st.walkStuck || 0, ...WALK.stats() };""", "walk in status")


# ---------------------------------------------------------------------------------------------- C2.2: WORK IN REAL TIME (pw_civ_work.js)
rep("""import * as WALK from "./pw_civ_walk.js";                        // C2.1 (D-C541): villagers walk where the clock sends them""",
    """import * as WALK from "./pw_civ_walk.js";                        // C2.1 (D-C541): villagers walk where the clock sends them
import * as WORKMOD from "./pw_civ_work.js";                     // C2.2 (D-C542): quarrymen mine, woodcutters fell, both carry to the store""", "work import")
rep("""const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };""", """WORKMOD.initWork({
  load, BUILDINGS, rotXZ, backOf, footprint, groundAt, isGround, TREE_LOG, fellTree, short,
  tierIdx: (t) => TIER_IDX(t), QUARRY_R_MAX, QUARRY_D_MAX,
  plotsOf: (st) => plotsOf(load(), st), occupied: (st) => occupiedTest(load(), st),
  wake: (st, b) => { const s = load(); try { ensureTicking(s, st, [b.x - 24, b.z - 24, b.x + 40, b.z + 40], `${short(b)} #${b.id} work`); } catch { /* left */ } },
  deposited: (st, b, n, kind) => { (st.workToday = st.workToday || {})[b.id] = ((st.workToday || {})[b.id] || 0) + n; st.workTotal = (st.workTotal || 0) + n; },
  // D-C550: a skilled hand works faster (the census person's output factor in this trade)
  skill: (v, st, kind) => { try { const tag = v.getTags().find((t) => t.startsWith("civ:person:")); const p = tag && st.people ? PEOPLE.byId(st.people, Number(tag.slice(11))) : null; return p ? PEOPLE.outputFactor(p, kind) : 1; } catch { return 1; } },
});
const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };""", "work init")
# the schedule leaves working keepers to the work module (they are keepers anyway, skipped already)
# production: real days = what the hands deposited; accelerated (skip) days = the scripted pit / stand (harness only)
rep("""function produceDaily(s, st) {
  const out = {};
  let dim;
  try { dim = world.getDimension(st.dim); } catch { return out; }
  for (const b of plotsOf(s, st)) {
    if (b.stage < 4 || b.closed) continue;
    const kind = short(b);
    const stations = BUILDINGS[b.family].work || 1;
    try {
      if (kind === "quarry") {""", """function produceDaily(s, st) {
  const out = {};
  let dim;
  try { dim = world.getDimension(st.dim); } catch { return out; }
  const real = !s.accelNow;                                          // D-C542: a real day's stone is what the hands carried in
  const today = st.workToday || {};
  st.workToday = {};
  for (const b of plotsOf(s, st)) {
    if (b.stage < 4 || b.closed) continue;
    const kind = short(b);
    const stations = BUILDINGS[b.family].work || 1;
    if (real && (kind === "quarry" || kind === "lumberyard")) { out[b.id] = today[b.id] || 0; continue; }
    try {
      if (kind === "quarry") {""", "real production")
rep("""function advanceOnce(days) {
  const s = load();
  if (days <= 0) return [];
  s.simDays += days;""", """function advanceOnce(days) {
  const s = load();
  if (days <= 0) return [];
  s.accelNow = (s.accelLeft || 0) > 1e-9;                             // a skipped day (the harness): the scripted work stands in
  if (s.accelNow) s.accelLeft = Math.max(0, s.accelLeft - days);
  s.simDays += days;""", "accel flag")
rep("""    const evs = advance(days);                                 // the first LAG_SLICES days now, the rest one per beat""",
    """    s.accelLeft = (s.accelLeft || 0) + days;                   // D-C542: skipped days are ACCELERATED (no hands worked them)
    const evs = advance(days);                                 // the first LAG_SLICES days now, the rest one per beat""", "skip accel")
rep("""      rest.walk = { arrived: st.walkArrived || 0, stuck: st.walkStuck || 0, ...WALK.stats() };""",
    """      rest.walk = { arrived: st.walkArrived || 0, stuck: st.walkStuck || 0, ...WALK.stats() };
      rest.work = { total: st.workTotal || 0, today: st.workToday || {}, ...WORKMOD.stats(), pits: plotsOf(s, st).filter((b) => short(b) === "quarry").map((b) => [b.id, b.dug || 0, b.spoil || 0, b.pit ? b.pit.r : null]), stands: plotsOf(s, st).filter((b) => short(b) === "lumberyard").map((b) => [b.id, b.felled || 0, b.replanted || 0]) };""", "work in status")


# ---------------------------------------------------------------------------------------------- C2.3: BUILDERS (real time)
# A stage (1..4) begins when its bill is paid: the materials leave the store, the BUILDERS (the town's crew: census people with
# job "builders") walk to the site, and the stage advances only while they are there in working hours — one block per
# BUILD_TICKS per builder. When the labour is done the stage rises layer by layer (structure animation). Accelerated (skipped)
# days keep the old pace (the harness).
rep("""import { world, system, ItemStack, BlockVolume, BlockTypes, BlockPermutation, LiquidType } from "@minecraft/server";""",
    """import { world, system, ItemStack, BlockVolume, BlockTypes, BlockPermutation, LiquidType, StructureAnimationMode } from "@minecraft/server";""", "anim import")
rep("""    b.progress += d;
    while (b.stage < last && b.progress >= STAGE_DAYS[b.stage]) {""", """    b.progress += d;
    if (b.labor) { b.progress = Math.min(b.progress, STAGE_DAYS[b.stage] || 0); continue; }   // C2.3: the builders are at it
    while (b.stage < last && b.progress >= STAGE_DAYS[b.stage]) {""", "labor holds the stage")
rep("""        ECON.pay(L, bill);
        stt.buildBudget = budget - bill.blocks;""", """        ECON.pay(L, bill);
        stt.buildBudget = budget - bill.blocks;
        if (!s.accelNow) {
          // C2.3 (D-C541): a REAL day — the materials leave the store and the builders come; the stage waits for their work
          const took = takeFromStores(s, stt, bill);
          b.labor = { k: b.stage + 1, need: Math.max(BUILD_TICKS * 8, bill.blocks * BUILD_TICKS), done: 0, day: s.simDays, took };
          b.progress = STAGE_DAYS[b.stage];
          delete b.waiting; delete b.waitKey;
          stt.log.push(`day ${s.simDays.toFixed(0)}: the builders begin the ${STAGE_NAMES[b.stage + 1]} of #${b.id} ${short(b)} (${bill.blocks} blocks${took ? `; ${took} taken from the stores` : ""})`);
          break;
        }""", "labor starts")
rep("""function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }""",
    """function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }
const BUILD_TICKS = 40;                                   // C2.3: one block per 2 s per builder at the site
/** the labour sites of a settlement: buildings whose next stage the builders are working on */
function laborSites(s, st) { return plotsOf(s, st).filter((b) => b.labor && !b.closed); }
/** materials out of the stores for a bill: stone from the quarries' chests, logs from the lumberyards' (best effort, loaded
 *  chunks only; the ledger already paid). Returns the count taken. */
function takeFromStores(s, st, bill) {
  let took = 0;
  const want = { stone: (bill.mats && bill.mats.stone) || 0, timber: (bill.mats && bill.mats.timber) || 0 };
  let dim; try { dim = world.getDimension(st.dim); } catch { return 0; }
  for (const b of plotsOf(s, st)) {
    const kind = short(b);
    const key = kind === "quarry" ? "stone" : kind === "lumberyard" ? "timber" : null;
    if (!key || !b.store || want[key] <= 0) continue;
    try {
      const con = dim.getBlock(b.store)?.getComponent("minecraft:inventory")?.container;
      if (!con) continue;
      for (let i = 0; i < con.size && want[key] > 0; i++) {
        const it = con.getItem(i);
        if (!it) continue;
        const n = Math.min(it.amount, want[key]);
        if (n === it.amount) con.setItem(i, undefined); else { it.amount -= n; con.setItem(i, it); }
        want[key] -= n; took += n;
      }
    } catch { /* unloaded */ }
  }
  return took;
}""", "labor helpers")
# builder posts first in the census's job list
rep("""function jobPosts(s, st) {
  const P = census(st), filled = {};
  for (const p of PEOPLE.alive(P)) if (p.job) filled[p.job] = (filled[p.job] || 0) + 1;
  return shopsOf(s, st).filter((sh) => !sh.closed).map((sh) => ({ id: sh.id, kind: sh.kind, vacancies: Math.max(0, sh.stations - (filled[sh.id] || 0)) }));
}""", """function jobPosts(s, st) {
  const P = census(st), filled = {};
  for (const p of PEOPLE.alive(P)) if (p.job) filled[p.job] = (filled[p.job] || 0) + 1;
  // C2.3: the builders' crew comes first (2, +2 per site at work, at most a third of the people)
  const crew = Math.min(Math.ceil(PEOPLE.alive(P).length / 3), 2 + 2 * laborSites(s, st).length);
  const posts = [{ id: "builders", kind: "builder", vacancies: Math.max(0, crew - (filled.builders || 0)) }];
  return posts.concat(shopsOf(s, st).filter((sh) => !sh.closed).map((sh) => ({ id: sh.id, kind: sh.kind, vacancies: Math.max(0, sh.stations - (filled[sh.id] || 0)) })));
}""", "builder posts")
# the schedule: builders go to the sites; presence = labour
rep("""  if (tod >= SCHED.work[0] && tod < SCHED.work[1]) return jobB ? (jobB.station || front(jobB)) : (square || front(homeB));""",
    """  if (tod >= SCHED.work[0] && tod < SCHED.work[1]) {
    if (person && (person.job === "builders" || !person.job)) {
      // C2.3: the nearest site with the fewest builders
      const sites = laborSites(s, st);
      if (sites.length) {
        let best = null, bs = Infinity;
        for (const b of sites) { const f = front(b); if (!f) continue; const sc = Math.hypot(v.location.x - f.x, v.location.z - f.z) + 40 * (b.labor.crew || 0); if (sc < bs) { bs = sc; best = b; } }
        if (best) { best.labor.crew = (best.labor.crew || 0) + 1; return { ...front(best), site: best.id }; }
      }
    }
    return jobB ? (jobB.station || front(jobB)) : (square || front(homeB));
  }""", "builders to sites")
rep("""  for (const st of s.settlements) {
    if (!st.kit || !st.square) continue;
    let vs;
    try { vs = world.getDimension(st.dim).getEntities({ tags: [`civ:settlement:${st.id}`], type: "minecraft:villager_v2" }); } catch { continue; }
    for (const v of vs) {
      if (v.hasTag("civ:keeper")) continue;                                  // the keepers' own beat (pw_civ_shop) sends them
      const g = goalFor(s, st, v, tod);
      if (!g) continue;
      if (Math.hypot(v.location.x - g.x, v.location.z - g.z) <= 3) { if (WALK.walking(v)) WALK.cancel(v); continue; }
      if (!WALK.walking(v)) WALK.send(v, st, g);
    }
  }""", """  const onDuty = tod >= SCHED.work[0] && tod < SCHED.work[1];
  for (const st of s.settlements) {
    if (!st.kit || !st.square) continue;
    let vs;
    try { vs = world.getDimension(st.dim).getEntities({ tags: [`civ:settlement:${st.id}`], type: "minecraft:villager_v2" }); } catch { continue; }
    const sites = laborSites(s, st);
    for (const b of sites) b.labor.crew = 0;
    for (const v of vs) {
      if (v.hasTag("civ:keeper")) continue;                                  // the keepers' own beat (pw_civ_shop) sends them
      const g = goalFor(s, st, v, tod);
      if (!g) continue;
      const here = Math.hypot(v.location.x - g.x, v.location.z - g.z);
      if (g.site !== undefined && onDuty && here <= 6) {                     // C2.3: a builder at the site works
        const b = sites.find((x) => x.id === g.site);
        if (b && b.labor) { b.labor.done += 100; b.labor.worked = (b.labor.worked || 0) + 1; try { v.dimension.playSound(b.labor.done % 300 < 100 ? "use.stone" : "use.wood", v.location, { volume: 0.7 }); } catch { /* left */ } }
      }
      if (here <= 3) { if (WALK.walking(v)) WALK.cancel(v); continue; }
      if (!WALK.walking(v)) WALK.send(v, st, g);
    }
    // a finished labour: the stage rises (layers), the next one may start
    let done = false;
    for (const b of sites) {
      if (b.labor.done < b.labor.need) continue;
      const k = b.labor.k;
      st.log.push(`day ${s.simDays.toFixed(0)}: the builders finished the ${STAGE_NAMES[k]} of #${b.id} ${short(b)} (${b.labor.worked || 0} builder-beats)`);
      st.built = (st.built || 0) + 1;
      delete b.labor;
      b.stage = k; b.progress = 0; b.animate = true; b.pending.push(k);
      done = true;
    }
    if (done) { flushPending(); save(); }
  }""", "labor beat")
# placement with the layers animation after real labour (post-work deferred until the animation ends)
rep("""    world.structureManager.place(`pw:stages/${def.stem}_s${k}`, dim, { x: b.x, y: b.y, z: b.z },
      { rotation: ROTS[b.rot], includeEntities: true });
    const set = fixDirections(dim, b, def);
    if (set) b.turned = (b.turned || 0) + set;
    if (k === 2) turnLids(dim, b, def);""", """    const anim = b.animate && k > 0;
    const secs = anim ? Math.min(30, Math.max(8, Math.round((stageBillOf(b, k).blocks || 100) / 20))) : 0;
    world.structureManager.place(`pw:stages/${def.stem}_s${k}`, dim, { x: b.x, y: b.y, z: b.z },
      anim ? { rotation: ROTS[b.rot], includeEntities: true, animationMode: StructureAnimationMode.Layers, animationSeconds: secs } : { rotation: ROTS[b.rot], includeEntities: true });
    delete b.animate;
    const post = () => { const set = fixDirections(dim, b, def); if (set) b.turned = (b.turned || 0) + set; if (k === 2) turnLids(dim, b, def); };
    if (anim) system.runTimeout(() => { try { post(); } catch (e) { console.warn(`[CIV-CLOCK] post-place #${b.id}: ${e}`); } }, secs * 20 + 20);
    else post();""", "animated stages")
rep("""      rest.work = { total: st.workTotal || 0,""", """      rest.labor = { built: st.built || 0, sites: plotsOf(s, st).filter((b) => b.labor).map((b) => [b.id, b.labor.k, b.labor.done, b.labor.need, b.labor.crew || 0]) };
      rest.work = { total: st.workTotal || 0,""", "labor in status")


# C2.3 harness: start a real labour now on the first building that has a next stage (need x fraction)
rep("""  if (cmd === "tickslots") {""", """  if (cmd === "realstage") {                                   // the harness: a real labour site now (C2.3)
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
  if (cmd === "tickslots") {""", "realstage cmd")


# D-C550: keepers are census people (the shop's master); the work module reads their skill
rep("""SHOP.initShops({ load, save, footprint, rotXZ, short, ECON, BUILDINGS, VILLAGER_ID,
  nameFor: (b, st) => NAMES[((b.id * 11) + (st ? st.seed : 0)) % NAMES.length] });""", """SHOP.initShops({ load, save, footprint, rotXZ, short, ECON, BUILDINGS, VILLAGER_ID,
  nameFor: (b, st) => { const P = st ? census(st) : null; const p = P ? PEOPLE.alive(P).find((q) => q.job === b.id && q.keeper) : null; return p ? p.name : NAMES[((b.id * 11) + (st ? st.seed : 0)) % NAMES.length]; },
  keeperPerson: (b, st, name) => {
    if (!st) return null;
    const P = census(st), day = Math.floor(load().simDays);
    let p = PEOPLE.alive(P).find((q) => q.job === b.id && q.keeper);
    if (!p) { p = PEOPLE.newPerson(P, day, { job: b.id, trade: short(b), name, age: 30, seed: b.id * 13, home: null }); p.keeper = true; }
    return p.id;
  } });""", "keeper person")
rep("""    if (e.kind === "wedding" || e.kind === "birth" || e.kind === "death" || e.kind === "arrival" || e.kind === "inherit") events.push(`§d${st.name}: ${e.text}`);""",
    """    if (["wedding", "birth", "death", "arrival", "inherit", "first", "rank"].includes(e.kind)) events.push(`§d${st.name}: ${e.text}`);""", "learning events to the player")


# F3 (D-C538): manholes daily (once the street work is done; a handful a day)
rep("""    try { coreSweep(s); } catch (e) { console.warn(`[CIV-CLOCK] cores: ${e}`); }""",
    """    try { coreSweep(s); } catch (e) { console.warn(`[CIV-CLOCK] cores: ${e}`); }
    if (st.kit && st.phase === "built" && !(st.kitQueue || []).length) { try { const n = queueManholes(st); if (n) st.log.push(`day ${s.simDays.toFixed(0)}: ${n} manhole(s) staked in the sidewalks`); } catch (e) { console.warn(`[CIV-CLOCK] manholes: ${e}`); } }""", "manholes daily")
rep("""      rest.labor = {""", """      rest.manholes = { laid: st.manholesLaid || 0, planned: st.streets.reduce((a, x) => a + ((x.manholes || []).length), 0), cells: (st.manholeCells || []).slice(0, 24) };
      rest.labor = {""", "manholes in status")


# ---------------------------------------------------------------------------------------------- F4: KEYS (pw_civ_keys.js)
rep("""import * as WORKMOD from "./pw_civ_work.js";""", """import * as WORKMOD from "./pw_civ_work.js";
import * as KEYS from "./pw_civ_keys.js";                         // F4 (D-C538 / D-C539): the sewer keys — a register, not a recipe""", "keys import")
rep("""const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };""", """KEYS.initKeys({ load });
const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };""", "keys init")
rep("""  const posts = [{ id: "builders", kind: "builder", vacancies: Math.max(0, crew - (filled.builders || 0)) }];""",
    """  const posts = [{ id: "builders", kind: "builder", vacancies: Math.max(0, crew - (filled.builders || 0)) }];
  // F4: the SEWER KEEPER (from town I, once the streets have manholes): one post, one key
  if (TIER_CLASS(st.tier) >= 1 && (st.manholesLaid || 0) > 0) posts.push({ id: "sewer_keeper", kind: "sewer_keeper", vacancies: (filled.sewer_keeper || 0) ? 0 : 1 });""", "sewer keeper post")
rep("""  st.mood = Math.round(r.meanMood);
}""", """  st.mood = Math.round(r.meanMood);
  // F4: the key register follows the posts (a new holder gets the key; a gone one's key goes back to the strongbox)
  try { KEYS.reconcile(st, P.list, Math.floor(s.simDays), (text) => { st.log.push(`day ${s.simDays.toFixed(0)}: ${text}`); events.push(`§6${st.name}: ${text}`); }); } catch (e) { console.warn(`[CIV-CLOCK] keys: ${e}`); }
}""", "keys reconcile")
rep("""  if (cmd === "realstage") {""", """  if (cmd === "keytest") {                                      // F4 witness: a test key, only for a player tagged civ:tester
    if (!p || !p.hasTag("civ:tester")) { reply("§c[CLOCK] keytest is for a player tagged civ:tester (the keys are never given otherwise)"); return; }
    const st = s.settlements.slice().sort((a2, b2) => Math.hypot(a2.x0 - p.location.x, a2.z0 - p.location.z) - Math.hypot(b2.x0 - p.location.x, b2.z0 - p.location.z))[0];
    if (!st) { reply("§c[CLOCK] no settlement"); return; }
    const k = KEYS.giveTestKey(p, st, Math.floor(s.simDays));
    st.log.push(`day ${s.simDays.toFixed(0)}: (test) key ${k.id} given to ${p.name}`);
    save(); reply(`§e[CLOCK] test key ${k.id} of ${st.name} in your inventory`); return;
  }
  if (cmd === "realstage") {""", "keytest cmd")
rep("""      rest.manholes = {""", """      rest.keys = KEYS.assets(st);
      rest.sewerLamps = st.sewerLamps || 0;
      rest.manholes = {""", "keys in status")


# ---------------------------------------------------------------------------------------------- F6 (D-C540): GREEN CORRIDORS
# A road between settlements is a closed, FENCED channel (a fence 3 high on the ground just outside the road's body, open
# only where it meets a settlement), crossed by GRASS LAND BRIDGES every CROSS_EVERY cells where it runs straight: a deck 5
# along the road x the road + fences + 1 across, 5 above the road (4 clear), grass on top, stone-brick abutments, fences on
# the deck's two road-facing edges, earth approaches falling 1 per 2 cells to the natural ground on both sides. Animals
# cross over, people and carts pass under — the road and the wild kept apart (his 22:22).
rep("""    try { road.laid = layPlannedStreet(world.getDimension(st2.dim), road); } catch (e) { console.warn(`[CIV-CLOCK] road lay: ${e}`); road.laid = 0; }""",
    """    try { road.laid = layPlannedStreet(world.getDimension(st2.dim), road); } catch (e) { console.warn(`[CIV-CLOCK] road lay: ${e}`); road.laid = 0; }
    try { const g = greenCorridor(world.getDimension(st2.dim), s2, road); road.fence = g.fence; road.crossings = g.crossings; if (g.fence) st2.log.push(`day ${s2.simDays.toFixed(0)}: the road to ${ch2.name} is fenced (${g.fence} posts) with ${g.crossings.length} green bridge(s)`); } catch (e) { console.warn(`[CIV-CLOCK] green corridor: ${e}`); }""", "green corridor call")
rep("""function layPlannedStreet(dim, street) {""", """const CORRIDOR_FENCE = "minecraft:spruce_fence", CROSS_EVERY = 80, CROSS_LEN = 5, CROSS_CLEAR = 4;
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
function layPlannedStreet(dim, street) {""", "green corridor fn")


# ---------------------------------------------------------------------------------------------- B4: BORDER STONES (D-C549)
rep("""  st.tier = tier;
  st.tierDay = s.simDays;
  st.log.push(`day ${s.simDays.toFixed(0)}: ${tierLabel(st)} (+${added.length} plots; ${population(s, st)} people)`);""",
    """  st.tier = tier;
  st.tierDay = s.simDays;
  // run 0.0.22: a founding ring wide enough for a long main street (160) outgrew every tier's influence below the city (112..144),
  // so the ring stood still from village to town III and the streets could not grow (leftover 87 plots): every tier now
  // carries the ring at least BORDER_TIER further out
  try { if (st.border) planBorderGrowth(s, st, Math.max(INFLUENCE[tier] || 0, st.border.r + BORDER_TIER), !!s.accelNow); } catch (e) { console.warn(`[CIV-CLOCK] border growth: ${e}`); }
  st.log.push(`day ${s.simDays.toFixed(0)}: ${tierLabel(st)} (+${added.length} plots; ${population(s, st)} people)`);""", "border on tier-up")
rep("""    try { coreSweep(s); } catch (e) { console.warn(`[CIV-CLOCK] cores: ${e}`); }""",
    """    try { coreSweep(s); } catch (e) { console.warn(`[CIV-CLOCK] cores: ${e}`); }
    try { borderDay(s, st); if (s.accelNow && st.border && st.border.moves.some((m) => !m.done && m.blocked === null)) { for (const m of st.border.moves) if (!m.done && m.blocked === null) moveStoneNow(s, st, m); finishBorderIfDone(s, st); } } catch (e) { console.warn(`[CIV-CLOCK] border day: ${e}`); }""", "border daily")
# the surveyor office
rep("""  // F4: the SEWER KEEPER (from town I, once the streets have manholes): one post, one key""",
    """  // B4: the SURVEYOR (an office) while boundary stones wait to be carried out
  if (st.border && st.border.moves.some((m) => !m.done && m.blocked === null)) posts.push({ id: "surveyor", kind: "surveyor", vacancies: (filled.surveyor || 0) ? 0 : 1 });
  // F4: the SEWER KEEPER (from town I, once the streets have manholes): one post, one key""", "surveyor post")
rep("""  if (tod >= SCHED.work[0] && tod < SCHED.work[1]) {
    if (person && (person.job === "builders" || !person.job)) {""", """  if (tod >= SCHED.work[0] && tod < SCHED.work[1]) {
    if (person && person.job === "surveyor") {
      const task = surveyorTask(st);
      if (task) { const g = groundAt(world.getDimension(st.dim), task.x, task.z); return { x: task.x + 0.5, z: task.z + 0.5, y: (g ?? 64) + 1, survey: task }; }
    }
    if (person && (person.job === "builders" || !person.job)) {""", "surveyor goal")
rep("""      if (here <= 3) { if (WALK.walking(v)) WALK.cancel(v); continue; }
      if (!WALK.walking(v)) WALK.send(v, st, g);
    }
    // a finished labour: the stage rises (layers), the next one may start""", """      if (g.survey && onDuty && here <= 3) {                                   // B4: the surveyor lifts / sets a stone
        try { surveyorAct(s, st, g.survey); v.dimension.playSound(g.survey.kind === "lift" ? "dig.stone" : "use.stone", v.location, { volume: 0.8 }); } catch (e) { console.warn(`[CIV-CLOCK] surveyor: ${e}`); }
        if (WALK.walking(v)) WALK.cancel(v);
        continue;
      }
      if (here <= 3) { if (WALK.walking(v)) WALK.cancel(v); continue; }
      if (!WALK.walking(v)) WALK.send(v, st, g);
    }
    // a finished labour: the stage rises (layers), the next one may start""", "surveyor acts")
rep("""      rest.keys = KEYS.assets(st);""", """      rest.keys = KEYS.assets(st);
      rest.border = st.border ? { r: st.border.r, target: st.border.target, stones: st.border.stones.length, moving: st.border.moves.filter((m) => !m.done).length, disputes: (st.border.disputes || []).map((d) => [d.key, d.state]), wait: st.borderWait || 0 } : null;""", "border in status")


# ---------------------------------------------------------------------------------------------- A0.2 SEWER EXITS v2 (D-C547 / D-C549) in the status
rep("""        outfalls: (x.outfalls || []).map((o) => o.plan ? [o.plan.exit[0], o.plan.exit[1], o.plan.dir[0], o.plan.dir[1], o.plan.floorY, o.plan.cells.length] : null) } : { kind: x.kind, laid: x.laid, nCells: x.nCells });""",
    """        outfalls: (x.outfalls || []).filter((o) => !o || !o.sealed).map((o) => o && o.plan ? [o.plan.exit[0], o.plan.exit[1], o.plan.dir[0], o.plan.dir[1], o.plan.floors ? o.plan.floors[o.plan.floors.length - 1] : o.plan.floorY, o.plan.cells.length, o.plan.target || "v1", o.gone ? 1 : 0, (o.manholes || []).length] : null),
        sealed: (x.outfalls || []).filter((o) => o && o.sealed).length } : { kind: x.kind, laid: x.laid, nCells: x.nCells });""", "status outfalls v2")
rep("""      rest.sewerLamps = st.sewerLamps || 0;""", """      rest.sewerLamps = st.sewerLamps || 0;
      rest.drain = { nets: st.drainNets || null, day: st.drainDay ?? null, trunkLamps: st.trunkLamps || 0 };""", "status drain")


# ---------------------------------------------------------------------------------------------- 0.0.22: a daughter never lands on another settlement
# run 0.0.21 (and every run since benches): the daughter's random bearing put her square on the mother's WEST BENCH — her
# square overlapped the mother's farm #22, and the mother's bench people commuted 270 blocks to the quarry. The bearing is
# now searched (12 bearings from the seeded one, two distances) for a site whose disc holds no other settlement's square,
# corridor or building and lies outside every boundary-stone ring.
rep("""  const ang = pick() * Math.PI * 2;
  const cx = Math.round(st.square.x + 6 + Math.cos(ang) * dist), cz = Math.round(st.square.z + 6 + Math.sin(ang) * dist);""",
    """  const ang0 = pick() * Math.PI * 2;
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
  if (cx === null) { st.daughterWait = s.simDays; if (!st.daughterSaid || s.simDays - st.daughterSaid > 30) { st.daughterSaid = s.simDays; st.log.push(`day ${s.simDays.toFixed(0)}: no free land for a daughter town within ${dist + 40} blocks`); } return; }""", "daughter clear land")


# ---------------------------------------------------------------------------------------------- 0.0.22: a town that lives on (D-C536)
# run 0.0.21: every founder was 20..44 at move-in, homes were always full (no births), and the whole generation died within
# 30 days (52 people -> 31). Households now arrive with two adults (20..59) and children (0..14); homes report how far they
# are crowded (births may crowd a family home by 2; the grown move out to free rooms).
rep("""  for (let i = 0; i < n; i++) { const p = PEOPLE.newPerson(P, Math.floor(s.simDays), { home: b.id, seed: b.id * 31 + i * 7 + (st.seed || 0), age: 20 + ((b.id * 7 + i * 11) % 25) }); names.push(p.name); (st.lastMoveIn = st.lastMoveIn || []).push(p.id); }""",
    """  for (let i = 0; i < n; i++) {
    const hsh = (b.id * 7 + i * 11 + (st.seed || 0)) >>> 0;
    const p = PEOPLE.newPerson(P, Math.floor(s.simDays), { home: b.id, seed: b.id * 31 + i * 7 + (st.seed || 0), age: i < 2 ? 20 + (hsh % 40) : hsh % 15, sex: i === 0 ? "m" : i === 1 ? "f" : undefined, parents: [] });
    names.push(p.name); (st.lastMoveIn = st.lastMoveIn || []).push(p.id);
  }""", "household ages")
rep("""    .map((b) => ({ id: b.id, room: Math.max(0, Math.round((HOUSEHOLD[short(b)] || 0) * dens) - (living[b.id] || 0)) }));""",
    """    .map((b) => { const cap = Math.round((HOUSEHOLD[short(b)] || 0) * dens); return { id: b.id, room: Math.max(0, cap - (living[b.id] || 0)), over: Math.max(0, (living[b.id] || 0) - cap) }; });""", "homes crowded")


# ---------------------------------------------------------------------------------------------- F5: THE WATCH (pw_civ_watch.js) + BODIES (census <-> villagers)
rep("""import * as KEYS from "./pw_civ_keys.js";""", """import * as KEYS from "./pw_civ_keys.js";
import * as WATCH from "./pw_civ_watch.js";                       // F5 (D-C538): patrols above and below ground (monsters only: Utopia-First)""", "watch import")
rep("""KEYS.initKeys({ load });""", """KEYS.initKeys({ load });
WATCH.initWatch({
  load, kitHAt: (street, t) => street.H[t - street.tmin], cellOf: KIT.cellOf,
  stOf: (id) => load().settlements.find((x) => x.id === id),
  personOf: (v, st) => { try { const tag = v.getTags().find((x) => x.startsWith("civ:person:")); return tag && st.people ? PEOPLE.byId(st.people, Number(tag.slice(11))) : null; } catch { return null; } },
  keyOf: (st, pid) => KEYS.keyOf(st, pid), slideCover: (b, to) => KEYS.slideCover(b, to),
});""", "watch init")
# the posts: the watch by tier
rep("""  if (TIER_CLASS(st.tier) >= 1 && (st.manholesLaid || 0) > 0) posts.push({ id: "sewer_keeper", kind: "sewer_keeper", vacancies: (filled.sewer_keeper || 0) ? 0 : 1 });
  return posts.concat(""", """  if (TIER_CLASS(st.tier) >= 1 && (st.manholesLaid || 0) > 0) posts.push({ id: "sewer_keeper", kind: "sewer_keeper", vacancies: (filled.sewer_keeper || 0) ? 0 : 1 });
  // F5: the WATCH (village III: 1 constable, town I: 2 ... city I: 6, more per tier)
  const nWatch = WATCH.WATCH_POSTS[st.tier] || 0;
  if (nWatch) posts.push({ id: "watch", kind: "watch", vacancies: Math.max(0, nWatch - (filled.watch || 0)) });
  return posts.concat(""", "watch posts")
# the schedule leaves the watch (and the sewer keeper on its rounds) to the patrol module
rep("""      if (v.hasTag("civ:keeper")) continue;                                  // the keepers' own beat (pw_civ_shop) sends them
      const g = goalFor(s, st, v, tod);""", """      if (v.hasTag("civ:keeper")) continue;                                  // the keepers' own beat (pw_civ_shop) sends them
      if (v.hasTag("civ:watching")) continue;                                // F5: a patrol on its round (pw_civ_watch)
      const g = goalFor(s, st, v, tod);""", "schedule skips patrols")
rep("""      rest.sewerLamps = st.sewerLamps || 0;
      rest.drain = {""", """      rest.sewerLamps = st.sewerLamps || 0;
      rest.watch = { posts: WATCH.WATCH_POSTS[st.tier] || 0, ...WATCH.stats(st) };
      rest.bodies = st.bodies || null;
      rest.drain = {""", "watch in status")
# BODIES: the census and the villagers agree every day — the dead and the departed leave the world, post holders without a
# body are embodied at their door (a few a day, up to EMBODY_CAP per settlement), a moved person's home tag follows the record
rep("""function censusDay(s, st, events) {""", """const EMBODY_CAP = 48, BODY_POSTS = ["watch", "sewer_keeper", "surveyor", "builders"];
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
  for (const p of PEOPLE.alive(P)) {
    if (made >= 3 || byPid.size >= EMBODY_CAP) break;
    if (byPid.has(p.id) || p.keeper || !BODY_POSTS.includes(p.job)) continue;
    const home = p.home ? s.buildings.find((b) => b.id === p.home) : null;
    const def = home && BUILDINGS[home.family];
    let spot = null;
    if (def) { const fr = doorFront(home, def); spot = { x: fr.x + 0.5, y: home.y + def.datum_y, z: fr.z + 0.5 }; }
    else if (st.square) spot = { x: st.square.x + 6.5, y: st.square.y + 1, z: st.square.z + 6.5 };
    if (!spot) continue;
    try {
      const v = dim.spawnEntity(VILLAGER_ID, spot);
      v.nameTag = p.name; v.addTag(`civ:person:${p.id}`); v.addTag("civ:villager"); v.addTag(`civ:settlement:${st.id}`); if (p.home) v.addTag(`civ:home:${p.home}`);
      byPid.set(p.id, v); made++;
    } catch { /* unloaded: tomorrow */ }
  }
  st.bodies = { n: byPid.size, made: ((st.bodies && st.bodies.made) || 0) + made, gone: ((st.bodies && st.bodies.gone) || 0) + gone };
}
function censusDay(s, st, events) {""", "body sync")
rep("""  st.mood = Math.round(r.meanMood);
  // F4: the key register follows the posts""", """  st.mood = Math.round(r.meanMood);
  try { bodySync(s, st); } catch (e) { console.warn(`[CIV-CLOCK] bodies: ${e}`); }
  // F4: the key register follows the posts""", "body sync daily")


# ---------------------------------------------------------------------------------------------- 0.0.23: keepers live at their shops
# run 0.0.22: the keepers' census records had no home (-20 mood), a grain shortage added -30, and the village's keepers left
# unhappy in its second week (Kari of the quarry, Finn of the farm): a keeper lives at the shop (rooms above the counter)
rep("""    if (!p) { p = PEOPLE.newPerson(P, day, { job: b.id, trade: short(b), name, age: 30, seed: b.id * 13, home: null }); p.keeper = true; }""",
    """    if (!p) { p = PEOPLE.newPerson(P, day, { job: b.id, trade: short(b), name, age: 30, seed: b.id * 13, home: b.id }); p.keeper = true; }
    if (!p.home) p.home = b.id;""", "keeper lives at the shop")

# ---------------------------------------------------------------------------------------------- F7 CIVIC WORKS + SANITATION (D-C549)
# "Civilizations rose and fell before roads, gutters, sanitation (sewers, waste removal, plumbing, hospitals) became normal."
# Each tier lays out its WORKS with its plots (built from the ledger like any plot; stand-in templates until Abs0lum picks his
# own — Q12) or opens its OFFICE (a census post); the next tier waits until they stand. The SANITATION dial (works present /
# works due) moves mood (+-) and lengthens or shortens lives; an infirmary with a healer lowers the death chance.
t = t.replace("HOUSEHOLD[short(b)]", "hhOf(b)") if t.count("HOUSEHOLD[short(b)]") == 0 else t
rep("""function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }""",
    """function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }
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
}""", "civic works")
t = t.replace("HOUSEHOLD[short(b)]", "hhOf(b)")
assert t.count("function hhOf(b) { return b && b.civic ? 0 : (hhOf(b) || 0); }") == 1
t = t.replace("function hhOf(b) { return b && b.civic ? 0 : (hhOf(b) || 0); }", "function hhOf(b) { return b && b.civic ? 0 : (HOUSEHOLD[short(b)] || 0); }")
# the works come with the tier's plots
rep("""  st.tier = tier;
  st.tierDay = s.simDays;""", """  // F7: the tier's civic works are laid out with its plots (offices open as census posts)
  for (const [work, fam] of CIVIC[tier] || []) {
    if (fam === "post") { st.log.push(`day ${s.simDays.toFixed(0)}: the council opens the ${work} office`); continue; }
    const skins = skinsOf(fam);
    const b = addPlot(s, st, familyOf(fam, skins[Math.floor(pick() * skins.length)]), st.dim, k * VILLAGE_STAGGER, pick);
    if (b) { b.civic = work; added.push(b); k++; st.log.push(`day ${s.simDays.toFixed(0)}: the ${work} is laid out (#${b.id}, a ${fam.replace("_", " ")} until its own design)`); }
    else (st.civicLeft = st.civicLeft || []).push([work, fam]);
  }
  st.tier = tier;
  st.tierDay = s.simDays;""", "civic plots")
# the natural tier-up waits for the works
rep("""  if (next && st.phase !== "reading" && plotsOf(s, st).length > 0 && age >= TIER_DAYS[next] && allRoofed(s, st) && prosperityOk(st) && moodOk(st)) {""",
    """  const works = civicWorks(s, st);
  if (next && works.missing.length && age >= TIER_DAYS[next] && (!st.worksSaid || s.simDays - st.worksSaid > 30)) { st.worksSaid = s.simDays; st.log.push(`day ${s.simDays.toFixed(0)}: ${TIER_LABEL[next]} waits for the town's works: ${works.missing.join(", ")}`); }
  if (next && st.phase !== "reading" && plotsOf(s, st).length > 0 && age >= TIER_DAYS[next] && allRoofed(s, st) && prosperityOk(st) && moodOk(st) && !works.missing.length) {""", "works gate")
# the offices: the midden carter (village III), the lamplighter (town III), a healer per infirmary
rep("""  const nWatch = WATCH.WATCH_POSTS[st.tier] || 0;""", """  for (const [tier, works] of Object.entries(CIVIC)) if (TIERS.indexOf(tier) <= TIERS.indexOf(st.tier)) for (const [w, fam] of works) if (fam === "post") posts.push({ id: w, kind: w, vacancies: (filled[w] || 0) ? 0 : 1 });
  const infirm = plotsOf(s, st).filter((b) => ["infirmary", "hospital", "ward"].includes(b.civic) && b.stage >= 4).length;
  if (infirm) posts.push({ id: "healer", kind: "healer", vacancies: Math.max(0, infirm - (filled.healer || 0)) });
  const nWatch = WATCH.WATCH_POSTS[st.tier] || 0;""", "civic posts")
# the census day knows how clean and how cared-for the town is
rep("""  const r = PEOPLE.dayStep(P, { day: Math.floor(s.simDays), fed, paid, homes: homeRoom(s, st), jobs: jobPosts(s, st), seed: st.seed || 1, name: st.name, events: [] });""",
    """  st.sanitation = Math.round(sanitationOf(s, st) * 100) / 100;
  const r = PEOPLE.dayStep(P, { day: Math.floor(s.simDays), fed, paid, homes: homeRoom(s, st), jobs: jobPosts(s, st), seed: st.seed || 1, name: st.name, events: [], sanitation: st.sanitation, health: healthOf(s, st) });""", "census sanitation")
rep("""      rest.watch = { posts: WATCH.WATCH_POSTS[st.tier] || 0, ...WATCH.stats(st) };""", """      rest.watch = { posts: WATCH.WATCH_POSTS[st.tier] || 0, ...WATCH.stats(st) };
      rest.works = { ...civicWorks(s, st), sanitation: st.sanitation ?? null, health: healthOf(s, st) };""", "works in status")


# ---------------------------------------------------------------------------------------------- F2 STEWARDSHIP: the quarry's rim re-greens daily
rep("""      if (kind === "quarry") { const n = digQuarry(dim, b, st, TIER_IDX(st.tier), stations * 24); if (n !== undefined) out[b.id] = n; }""",
    """      if (kind === "quarry") { const n = digQuarry(dim, b, st, TIER_IDX(st.tier), stations * 24); if (n !== undefined) { out[b.id] = n; b.spoil = (b.spoil || 0) + Math.floor(n / 4); } }""", "accelerated spoil")
rep("""    } catch { /* unloaded: the abstract rate stands in */ }
  }
  return out;
}""", """    } catch { /* unloaded: the abstract rate stands in */ }
    if (kind === "quarry") { try { const g = WORKMOD.regreen(dim, b, st, 8); if (g && !st.greenSaid) { st.greenSaid = true; st.log.push(`day ${s.simDays.toFixed(0)}: the quarry's spent rim is greening again (topsoil from the spoil)`); } } catch { /* unloaded */ } }
  }
  return out;
}""", "regreen daily")
rep("""      rest.works = { ...civicWorks(s, st), sanitation: st.sanitation ?? null, health: healthOf(s, st) };""",
    """      rest.works = { ...civicWorks(s, st), sanitation: st.sanitation ?? null, health: healthOf(s, st) };
      rest.stewardship = { greened: plotsOf(s, st).filter((b) => short(b) === "quarry").reduce((a, b) => a + (b.greened || 0), 0), spoil: plotsOf(s, st).filter((b) => short(b) === "quarry").reduce((a, b) => a + (b.spoil || 0), 0),
                           replanted: plotsOf(s, st).filter((b) => short(b) === "lumberyard").reduce((a, b) => a + (b.replanted || 0), 0), greenbelt: (st.slotWhy && st.slotWhy.greenbelt) || 0 };""", "stewardship status")


# ---------------------------------------------------------------------------------------------- B2: neighbourhood centres at the tier-up + in the schedule
rep("""  // F7: the tier's civic works are laid out with its plots (offices open as census posts)""", """  // B2 (his 23:30): every parallel street grows its own small market centre from town II
  try { for (const b of openCentres(s, st, pick, k * VILLAGE_STAGGER)) { added.push(b); k++; } } catch (e) { console.warn(`[CIV-CLOCK] centres: ${e}`); }
  // F7: the tier's civic works are laid out with its plots (offices open as census posts)""", "centres at tier-up")
rep("""  const square = st.square ? { x: st.square.x + 6.5, z: st.square.z + 6.5, y: st.square.y + 1 } : null;
  if (tod >= SCHED.work[0] && tod < SCHED.work[1]) {""", """  const square0 = st.square ? { x: st.square.x + 6.5, z: st.square.z + 6.5, y: st.square.y + 1 } : null;
  const centreB = centreOf(s, st, homeB);                              // B2: the neighbourhood's own market, when its street has one
  const square = centreB ? front(centreB) : square0;
  if (tod >= SCHED.work[0] && tod < SCHED.work[1]) {""", "centre in the schedule")
rep("""      rest.works = { ...civicWorks(s, st), sanitation: st.sanitation ?? null, health: healthOf(s, st) };""",
    """      rest.works = { ...civicWorks(s, st), sanitation: st.sanitation ?? null, health: healthOf(s, st) };
      rest.centres = (st.centres || []).map((c) => [c.sid, c.well, c.shops.length, (s.buildings.find((b) => b.id === c.well) || {}).stage ?? null]);""", "centres in status")


# ---------------------------------------------------------------------------------------------- C2.4 PURCHASES AT THE COUNTER (design §13, D-C550)
# At midday one person of each household walks to a food shop — the one it TRUSTS most for its distance (D-C550's choice,
# with the exploration share), the neighbourhood's own first (B2) — and buys a loaf or a cut at the counter: the item leaves
# the shop's chest (stocked each real morning from the shop's day of work), and the outcome teaches the buyer (an empty
# counter lowers trust in that shop; a rumour goes round). The ledger keeps the town's money; the counter is its visible act.
rep("""function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }""",
    """function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }
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
    const c = chestOf(b);
    if (!c) continue;
    const good = kind === "bakery" ? "bread" : "meat";
    const have = L && L.stock ? Math.floor(L.stock[good] || 0) : 0;
    const n = Math.min(16, Math.max(0, have > 0 ? Math.ceil(households(s, st) / 2) : 0));
    if (!n) continue;
    try { const inv = dim.getBlock(c)?.getComponent("minecraft:inventory"); if (inv && inv.container) inv.container.addItem(new ItemStack(COUNTER[kind][0], n)); } catch { /* unloaded */ }
  }
}
/** the purchase: one item out of the shop's chest; the buyer learns; the market day is counted */
function buyAt(s, st, v, person, shopB) {
  const day = Math.floor(s.simDays);
  st.market = st.market && st.market.day === day ? st.market : { day, buys: 0, empty: 0, homes: [] };
  if (person.home) st.market.homes.push(person.home);
  let got = false;
  try {
    const c = chestOf(shopB);
    const con = c ? world.getDimension(st.dim).getBlock(c)?.getComponent("minecraft:inventory")?.container : null;
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
  const r = rng(((st.seed || 1) * 977 + Math.floor(s.simDays) * 31 + person.id) >>> 0);
  const o = PEOPLE.choose(person, opts, r);
  return o ? o.b : null;
}""", "counter helpers")
rep("""    if (person && (person.job === "builders" || !person.job)) {""", """    // C2.4: midday — the household's shopper (no post, no station) goes to the counter it trusts
    // (run 0.0.23: no purchase at all — every grown person held a station, and only the jobless shopped) the household's
    // SHOPPER is its first grown member who keeps no shop and stands no watch; they leave the work for the counter at midday
    const shopper = person && person.home && tod >= MARKET[0] && tod < MARKET[1]
      ? PEOPLE.alive(census(st)).filter((q) => q.home === person.home && !q.keeper && q.job !== "watch" && q.job !== "builders" && PEOPLE.stage(q, Math.floor(s.simDays)) !== "child").sort((a2, b2) => a2.id - b2.id)[0] : null;
    if (shopper && shopper.id === person.id) {
      const day = Math.floor(s.simDays);
      const done = st.market && st.market.day === day && st.market.homes.includes(person.home);
      if (!done) { const shopB = shopFor(s, st, v, person, homeB); if (shopB) { const f = shopB.station || front(shopB); if (f) return { ...f, buy: shopB.id, person: person.id }; } }
    }
    if (person && (person.job === "builders" || !person.job)) {""", "shopping goal")
rep("""      if (g.site !== undefined && onDuty && here <= 6) {                     // C2.3: a builder at the site works""",
    """      if (g.buy !== undefined && here <= 3) {                                  // C2.4: at the counter
        const shopB = s.buildings.find((b) => b.id === g.buy), person = PEOPLE.byId(census(st), g.person);
        if (shopB && person) buyAt(s, st, v, person, shopB);
        if (WALK.walking(v)) WALK.cancel(v);
        continue;
      }
      if (g.site !== undefined && onDuty && here <= 6) {                     // C2.3: a builder at the site works""", "counter act")
rep("""  const real = !s.accelNow;                                          // D-C542: a real day's stone is what the hands carried in""",
    """  const real = !s.accelNow;                                          // D-C542: a real day's stone is what the hands carried in
  if (real) { try { stockCounters(s, st); } catch (e) { console.warn(`[CIV-CLOCK] counters: ${e}`); } }""", "counters stocked")
rep("""      rest.centres = (st.centres || []).map((c) => [c.sid, c.well, c.shops.length, (s.buildings.find((b) => b.id === c.well) || {}).stage ?? null]);""",
    """      rest.centres = (st.centres || []).map((c) => [c.sid, c.well, c.shops.length, (s.buildings.find((b) => b.id === c.well) || {}).stage ?? null]);
      rest.market = st.market ? { day: st.market.day, buys: st.market.buys, empty: st.market.empty, homes: st.market.homes.length } : null;""", "market in status")


# ---------------------------------------------------------------------------------------------- 0.0.23: more hands at the workshops
# run 0.0.22: one hand (the keeper) and nothing mined; the census already gives the quarry and the lumberyard their workers
# (people whose job is the workshop): their villagers now work the face / the stand with the keeper; the schedule leaves a
# villager tagged civ:working to the work module
rep("""  skill: (v, st, kind) => {""", """  hands: (st, b) => {
    const out = [];
    try {
      for (const v of world.getDimension(st.dim).getEntities({ tags: [`civ:settlement:${st.id}`], type: VILLAGER_ID })) {
        if (v.hasTag("civ:keeper") || v.hasTag("civ:watching")) continue;
        const tag = v.getTags().find((x) => x.startsWith("civ:person:"));
        const p = tag && st.people ? PEOPLE.byId(st.people, Number(tag.slice(11))) : null;
        if (p && p.alive && p.job === b.id) out.push(v);
      }
    } catch { /* unloaded */ }
    return out;
  },
  skill: (v, st, kind) => {""", "work hands")
rep("""      if (v.hasTag("civ:watching")) continue;                                // F5: a patrol on its round (pw_civ_watch)""",
    """      if (v.hasTag("civ:watching")) continue;                                // F5: a patrol on its round (pw_civ_watch)
      if (v.hasTag("civ:working")) continue;                                 // C2.2: a hand at the face / the stand (pw_civ_work)""", "schedule skips hands")


# ---------------------------------------------------------------------------------------------- 0.0.23: the founders' crew (no deadlock)
# runs 0.0.22-23: with few planned cottages the town's own builders came to 0 (population x workers per person minus the
# shops), no inn stood to lodge hired hands, and the founding plots waited "for 1 builder" from day 24 to day 44. The
# settlers always keep a crew of two (they build their own town).
rep("""    const own = Math.max(0, Math.round(population(s, st) * ECON.WORKERS_PER_PERSON) - shopsOf(s, st).length);""",
    """    const own = Math.max(FOUNDERS_CREW, Math.round(population(s, st) * ECON.WORKERS_PER_PERSON) - shopsOf(s, st).length);""", "founders crew")
rep("""function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }""",
    """function census(st) { if (!st.people) st.people = PEOPLE.newPeople(); return st.people; }
const FOUNDERS_CREW = 2;""", "founders crew const")


# ---------------------------------------------------------------------------------------------- D: THE MANOR HOUSE (town II; civ_roster.manor)
# His C3 / R3 §5 at town scale: the reception rooms in front, the service corridor with jib doors and the baize door behind
# them, the back range (kitchen, back stair, the steward's office, the pantry), chambers above, garrets in the roof. Its
# stations are the public servants' posts (steward's desk, the cook's hearth and ovens, the prep table).
rep("""const HOUSEHOLD = { cottage_s: 2, cottage_m: 2, cottage_l: 3, inn: 1, farm_wheat: 1, farm_terrace: 1, farm_cattle: 1 };""",
    """const HOUSEHOLD = { cottage_s: 2, cottage_m: 2, cottage_l: 3, inn: 1, farm_wheat: 1, farm_terrace: 1, farm_cattle: 1, manor: 4 };""", "manor household")
rep("""  town2: [["cottage_m", 5], ["cottage_s", 5], ["cottage_l", 2], ["farm_wheat", 1], ["bakery", 1], ["quarry", 1]],""",
    """  town2: [["manor", 1], ["cottage_m", 5], ["cottage_s", 5], ["cottage_l", 2], ["farm_wheat", 1], ["bakery", 1], ["quarry", 1]],""", "manor at town II")


# ---------------------------------------------------------------------------------------------- 0.0.24: one pit law for the hands and the harness
rep("""  const pit = (b.pit = b.pit || { r: 4 + 2 * tierIdx, depth: 2 + tierIdx, i: 0 });
  pit.r = Math.max(pit.r, 4 + 2 * tierIdx); pit.depth = Math.max(pit.depth, 2 + tierIdx);
  const dirx = b.rot === 0 ? 1 : b.rot === 2 ? -1 : 0, dirz = b.rot === 1 ? 1 : b.rot === 3 ? -1 : 0;   // away from the street
  const cx = c.x + dirx * (pit.r + 1), cz = c.z + dirz * (pit.r + 1);                                  // the pit grows away from the yard""",
    """  void c;
  const { pit, cx, cz } = WORKMOD.pitOf(b, def, tierIdx);                                               // capped; the next pit beside a spent one""", "dig pit law")
rep("""  if (removed === 0 && seen >= cells) { if (pit.r < QUARRY_R_MAX) pit.r += 1; else if (pit.depth < QUARRY_D_MAX) pit.depth += 1; pit.i = 0; }""",
    """  if (removed === 0 && seen >= cells) WORKMOD.pitWorkedOut(b, tierIdx);""", "dig worked out")
rep("""      rest.stewardship = { greened:""", """      rest.quarries = plotsOf(s, st).filter((b) => short(b) === "quarry").map((b) => [b.id, b.pit ? b.pit.r : null, b.pit ? b.pit.depth : null, b.pit ? b.pit.off || 0 : 0, b.pitsOpened || 1, (b.oldPits || []).length]);
      rest.stewardship = { greened:""", "quarries in status")


# ---------------------------------------------------------------------------------------------- 0.0.25: pit sites, worked-out quarries
# run 0.0.24: the accelerated days worked out four pits in a row (each 2r+3 further out); the fifth lay 124 blocks behind
# the quarry and the hand never reached it. Now: pits on chosen sites around the quarry (pw_civ_work.choosePitSite), one
# change a day, six sites at most — then the quarry is WORKED OUT (its stone stops; the shortage charters a new quarry)
rep("""  void c;
  const { pit, cx, cz } = WORKMOD.pitOf(b, def, tierIdx);                                               // capped; the next pit beside a spent one
  let dug = 0, removed = 0, seen = 0, unloaded = false;
  const occupied = occupiedTest(load(), st);""",
    """  void c;
  if (b.workedOut) return 0;                                                                             // 0.0.25: every pit site spent
  const occupied = occupiedTest(load(), st);
  const ctx = { dim, occupied, day: load().simDays, wake: (box) => { try { ensureTicking(load(), st, box, `quarry #${b.id} pit site`); } catch { /* left */ } } };
  const po = WORKMOD.pitOf(b, def, tierIdx, ctx);                                                       // its site chosen once
  if (po.wait) return undefined;                                                                         // 0.0.25d: the sites' land sleeps
  const { pit, cx, cz } = po;
  let dug = 0, removed = 0, seen = 0, unloaded = false;""", "dig pit sites")
rep("""  if (removed === 0 && seen >= cells) WORKMOD.pitWorkedOut(b, tierIdx);""",
    """  if (removed === 0 && seen >= cells) { WORKMOD.pitWorkedOut(b, tierIdx, ctx); if (b.workedOut && !b.workedOutSaid) { b.workedOutSaid = true; st.log.push(`day ${load().simDays.toFixed(0)}: the quarry (#${b.id}) is worked out — every pit site around it is spent`); } }""", "dig worked out 2")
rep("""      rest.quarries = plotsOf(s, st).filter((b) => short(b) === "quarry").map((b) => [b.id, b.pit ? b.pit.r : null, b.pit ? b.pit.depth : null, b.pit ? b.pit.off || 0 : 0, b.pitsOpened || 1, (b.oldPits || []).length]);""",
    """      rest.quarries = plotsOf(s, st).filter((b) => short(b) === "quarry").map((b) => [b.id, b.pit ? b.pit.r : null, b.pit ? b.pit.depth : null, b.pit ? b.pit.off || 0 : 0, b.pitsOpened || 1, (b.oldPits || []).length, b.pit ? b.pit.site ?? null : null, b.workedOut ? 1 : 0, b.skipped || 0]);""", "quarries in status 2")
rep("""  wake: (st, b) => { const s = load(); try { ensureTicking(s, st, [b.x - 24, b.z - 24, b.x + 40, b.z + 40], `${short(b)} #${b.id} work`); } catch { /* left */ } },""",
    """  wake: (st, b) => {
    const s = load();
    let box = [b.x - 24, b.z - 24, b.x + 40, b.z + 40];
    // 0.0.25: the pit's own box (a site may lie beside the quarry, not behind it)
    if (b.pit && b.pit.site !== undefined) { try { const q = WORKMOD.pitOf(b, BUILDINGS[b.family], TIER_IDX(st.tier)); const R = b.pit.r + 2; box = [Math.min(box[0], q.cx - R), Math.min(box[1], q.cz - R), Math.max(box[2], q.cx + R), Math.max(box[3], q.cz + R)]; } catch { /* legacy */ } }
    try { ensureTicking(s, st, box, `${short(b)} #${b.id} work`); } catch { /* left */ }
  },""", "work wake pit box")


# ---------------------------------------------------------------------------------------------- 0.0.25: THE WALK TEST (an instrument)
# runs 0.0.22-0.0.24: 41-78 walks ended "stuck" (52 "level"), yet an offline 2.5D connectivity check of run 0.0.24's dump
# found 25 of 26 stuck places JOINED to the square (a villager could walk there by vanilla rules): the cause is in the
# guidance (route / lead / follow), not in the land. The walk test sends up to 8 villagers on chosen walks and traces each
# one (place, feet block, lead, path index, next waypoints) every 20 ticks; a walker that stalls gets the blocks around it
# and around its next waypoints written to the log ([CIV-WALKTRACE] / [CIV-WALKSTALL] / [CIV-WALKTEST]).
rep("""  if (cmd === "keytest") {                                      // F4 witness: a test key, only for a player tagged civ:tester""",
    """  if (cmd === "walktest") {                                    // 0.0.25: the walk instrument (the harness)
    const st = s.settlements.filter((x) => x.kit && x.square).slice(-1)[0];
    if (!st) { reply("§c[CLOCK] no kit settlement"); return; }
    walkTest(s, st, Math.max(1, Math.min(8, parseInt(a || "8", 10) || 8)));
    reply(`§e[CLOCK] walk test: ${walkTests.size} walkers`); return;
  }
  if (cmd === "keytest") {                                      // F4 witness: a test key, only for a player tagged civ:tester""", "walktest cmd")
rep("""const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };""",
    """const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };
// ---- 0.0.25 THE WALK TEST: chosen walks, traced (the harness's instrument; nothing in normal play calls it)
const walkTests = new Map();                                       // villager id -> { name, target, t0, end, stalls }
let walkTestTimer = null;
function blockId(dim, x, y, z) { try { const b = dim.getBlock({ x, y, z }); return b ? b.typeId.replace("minecraft:", "").replace("pw:", "") : "?"; } catch { return "?"; } }
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
  if (walkTestTimer !== null) system.clearRun(walkTestTimer);
  walkTestTimer = system.runInterval(() => {
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
      walkTests.clear(); system.clearRun(walkTestTimer); walkTestTimer = null;
    }
  }, 20);
}""", "walk test")
rep("""      if (v.hasTag("civ:working")) continue;                                 // C2.2: a hand at the face / the stand (pw_civ_work)""",
    """      if (v.hasTag("civ:working")) continue;                                 // C2.2: a hand at the face / the stand (pw_civ_work)
      if (v.hasTag("civ:walktest")) continue;                                // 0.0.25: the walk instrument's walkers""", "schedule skips walktest")
rep("""  stuck: (v, w) => { const s = load();""", """  stuck: (v, w) => { const s = load(); if (walkTests.has(v.id)) { const r = walkTests.get(v.id); if (!r.end) { r.end = "stuck"; console.warn(`[CIV-WALKTEST] ${JSON.stringify({ end: r.name, how: "stuck", cause: w.cause || null, feet: w.feet || null, at: [Math.floor(v.location.x), Math.floor(v.location.y), Math.floor(v.location.z)], ticks: system.currentTick - r.t0, stalls: r.stalls })}`); try { v.removeTag("civ:walktest"); } catch { /* left */ } } }""", "walktest stuck")

# ---------------------------------------------------------------------------------------------- 0.0.25: shoppers with bodies
# run 0.0.24: no purchase at all (market null). The shopper rule picked the household's first grown member — but only
# villagers WITH a body run the schedule, and bodies went to the posts (watch, sewer keeper, surveyor, builders) and the
# immigrants at the door; a household whose first member had no body never shopped. Now: the shopper is the household's
# first grown member WITH a body (no post, no shop); bodySync gives each household without one a body for its shopper;
# the day's shopping goals and arrivals are counted (status: marketTry)
rep("""const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };""",
    """const SCHED = { work: [1000, 11000], dusk: [11000, 13000] };
const bodiesNow = new Map();                                       // 0.0.25: settlement id -> the person ids with a body this beat""", "bodies now")
rep("""      ? PEOPLE.alive(census(st)).filter((q) => q.home === person.home && !q.keeper && q.job !== "watch" && q.job !== "builders" && PEOPLE.stage(q, Math.floor(s.simDays)) !== "child").sort((a2, b2) => a2.id - b2.id)[0] : null;""",
    """      ? PEOPLE.alive(census(st)).filter((q) => q.home === person.home && !q.keeper && q.job !== "watch" && q.job !== "builders" && PEOPLE.stage(q, Math.floor(s.simDays)) !== "child" && (!bodiesNow.has(st.id) || bodiesNow.get(st.id).has(q.id))).sort((a2, b2) => a2.id - b2.id)[0] : null;""", "shopper with a body")
rep("""      if (!done) { const shopB = shopFor(s, st, v, person, homeB); if (shopB) { const f = shopB.station || front(shopB); if (f) return { ...f, buy: shopB.id, person: person.id }; } }""",
    """      if (!done) {
        const shopB = shopFor(s, st, v, person, homeB);
        const mt = (st.marketTry = st.marketTry && st.marketTry.day === day ? st.marketTry : { day, goals: 0, noShop: 0, shoppers: [] });
        if (!shopB) mt.noShop++;
        if (shopB) { const f = shopB.station || front(shopB); if (f) { mt.goals++; if (!mt.shoppers.includes(person.id)) mt.shoppers.push(person.id); return { ...f, buy: shopB.id, person: person.id }; } }
      }""", "market goals counted")
rep("""    const sites = laborSites(s, st);
    for (const b of sites) b.labor.crew = 0;
    for (const v of vs) {
      if (v.hasTag("civ:keeper")) continue;                                  // the keepers' own beat (pw_civ_shop) sends them""",
    """    const sites = laborSites(s, st);
    for (const b of sites) b.labor.crew = 0;
    { const ids = new Set(); for (const v of vs) { const tg = v.getTags().find((x) => x.startsWith("civ:person:")); if (tg) ids.add(Number(tg.slice(11))); } bodiesNow.set(st.id, ids); }
    for (const v of vs) {
      if (v.hasTag("civ:keeper")) continue;                                  // the keepers' own beat (pw_civ_shop) sends them""", "bodies now set")
rep("""      rest.market = st.market ? { day: st.market.day, buys: st.market.buys, empty: st.market.empty, homes: st.market.homes.length } : null;""",
    """      rest.market = st.market ? { day: st.market.day, buys: st.market.buys, empty: st.market.empty, homes: st.market.homes.length } : null;
      rest.marketTry = st.marketTry ? { day: st.marketTry.day, goals: st.marketTry.goals, noShop: st.marketTry.noShop, shoppers: st.marketTry.shoppers.length } : null;""", "market try status")
rep("""  for (const p of PEOPLE.alive(P)) {
    if (made >= 3 || byPid.size >= EMBODY_CAP) break;
    if (byPid.has(p.id) || p.keeper || !BODY_POSTS.includes(p.job)) continue;""",
    """  // 0.0.25: each household's SHOPPER gets a body too (its first grown member with no post and no shop), when the
  // household has no such member walking yet — the posts first (the loop below), then the shoppers
  const day0 = Math.floor(s.simDays);
  const shopperOk = (q) => !q.keeper && q.job !== "watch" && q.job !== "builders" && PEOPLE.stage(q, day0) !== "child";
  const homesWithShopper = new Set(PEOPLE.alive(P).filter((q) => q.home && byPid.has(q.id) && shopperOk(q)).map((q) => q.home));
  const want = PEOPLE.alive(P).filter((p) => !byPid.has(p.id) && !p.keeper && (BODY_POSTS.includes(p.job) || (p.home && shopperOk(p) && !homesWithShopper.has(p.home))))
    .sort((a2, b2) => (BODY_POSTS.includes(a2.job) ? 0 : 1) - (BODY_POSTS.includes(b2.job) ? 0 : 1) || a2.id - b2.id);
  for (const p of want) {
    if (made >= 3 || byPid.size >= EMBODY_CAP) break;
    if (byPid.has(p.id) || p.keeper) continue;
    if (!BODY_POSTS.includes(p.job)) { if (homesWithShopper.has(p.home)) continue; homesWithShopper.add(p.home); }""", "shopper bodies")

# ---------------------------------------------------------------------------------------------- 0.0.25b: parked sewer ops come back
rep("""    if (st.kit && st.phase === "built" && !(st.kitQueue || []).length) { try { const n = queueManholes(st);""",
    """    if (st.kit && st.parked && st.parked.length && Math.floor(s.simDays) % PARK_DAYS === 0) { st.kitQueue = st.kitQueue || []; for (const op of st.parked.splice(0)) st.kitQueue.push(op); }   // 0.0.25b
    if (st.kit && st.phase === "built" && !(st.kitQueue || []).length) { try { const n = queueManholes(st);""", "parked ops requeued")

# ---------------------------------------------------------------------------------------------- 0.0.25b: up to 3 leftover plots a day
rep("""  if (st.kit && st.leftover && st.leftover.length && st.phase === "built") {
    const nm = st.leftover[0];
    const skins = skinsOf(nm);
    const pick = rng((st.seed + s.simDays * 31) >>> 0);
    const b = addPlot(s, st, familyOf(nm, skins[Math.floor(pick() * skins.length)]), st.dim, 0, pick);
    if (b) { st.leftover.shift(); st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${nm} (#${b.id})`); }""",
    """  // 0.0.25b: up to LEFTOVER_PER_DAY a day while room is found (the background room search opens the streets)
  for (let q = 0; q < LEFTOVER_PER_DAY && st.kit && st.leftover && st.leftover.length && st.phase === "built"; q++) {
    const nm = st.leftover[0];
    const skins = skinsOf(nm);
    const pick = rng((st.seed + s.simDays * 31 + q * 7) >>> 0);
    const b = addPlot(s, st, familyOf(nm, skins[Math.floor(pick() * skins.length)]), st.dim, 0, pick);
    if (b) { st.leftover.shift(); st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${nm} (#${b.id})`); continue; }""", "leftovers a day 1")
rep("""    else if (!(st.kitQueue || []).length && (st.benchFail === undefined || s.simDays - st.benchFail >= BENCH_WAIT)) startBenchJob(st);
  }""",
    """    if (!(st.kitQueue || []).length && (st.benchFail === undefined || s.simDays - st.benchFail >= BENCH_WAIT)) startBenchJob(st);
    break;
  }""", "leftovers a day 2")
rep("""const FOUNDERS_CREW = 2;""", """const FOUNDERS_CREW = 2;
const LEFTOVER_PER_DAY = 3;                                        // 0.0.25b""", "leftover const")

# ---------------------------------------------------------------------------------------------- 0.0.25d: the counters stocked for the market
# run 0.0.25c: 96 shopping trips, 9 households at the counters, 0 bought — the counters are filled on a REAL morning only,
# and the town had come out of skipped days at mid-morning: the first market of the day stocks them if the morning did not
rep("""    { const ids = new Set(); for (const v of vs) { const tg = v.getTags().find((x) => x.startsWith("civ:person:")); if (tg) ids.add(Number(tg.slice(11))); } bodiesNow.set(st.id, ids); }""",
    """    { const ids = new Set(); for (const v of vs) { const tg = v.getTags().find((x) => x.startsWith("civ:person:")); if (tg) ids.add(Number(tg.slice(11))); } bodiesNow.set(st.id, ids); }
    // 0.0.25j (run 0.0.28: the counters were never stocked — s.accelNow is refreshed only when days advance, and a PAUSED
    // clock (the harness pauses it; so may he) kept the last skip's "true"): the gate reads the skip itself (accelLeft)
    if (tod >= MARKET[0] && tod < MARKET[1] && !((s.accelLeft || 0) > 1e-9) && st.stockedDay !== Math.floor(s.simDays)) { st.stockedDay = Math.floor(s.simDays); try { stockCounters(s, st); } catch (e) { console.warn(`[CIV-CLOCK] counters: ${e}`); } }""", "counters at the market")
rep("""  if (real) { try { stockCounters(s, st); } catch (e) { console.warn(`[CIV-CLOCK] counters: ${e}`); } }""",
    """  if (real) { st.stockedDay = Math.floor(s.simDays); try { stockCounters(s, st); } catch (e) { console.warn(`[CIV-CLOCK] counters: ${e}`); } }""", "counters stocked day")

# ---------------------------------------------------------------------------------------------- 0.0.25d: neighbourhood centres retried
# run 0.0.25c: no centre at all by town III — openCentres ran once, at the town II tier-up, and its wells found no slot
# then; a centre is now retried every 4 days on every parallel street still without one
rep("""  // D-C534 §3: from tier town the blocks close — one cross street a day between adjacent parallel streets""",
    """  if (st.kit && st.phase === "built" && TIERS.indexOf(st.tier) >= CENTRE_FROM && Math.floor(s.simDays) % 4 === 0 && st.centreTry !== Math.floor(s.simDays)) {
    st.centreTry = Math.floor(s.simDays);
    try { openCentres(s, st, rng(((st.seed || 1) + Math.floor(s.simDays) * 17) >>> 0), 0); } catch (e) { console.warn(`[CIV-CLOCK] centres: ${e}`); }
  }
  // D-C534 §3: from tier town the blocks close — one cross street a day between adjacent parallel streets""", "centres retried")

# ---------------------------------------------------------------------------------------------- 0.0.25d: a script profiler (an instrument)
# run 0.0.25c ran at ~14 TPS in its real-time phase (25 s of ticks took 35 s): every interval of the clock is wrapped to
# add its milliseconds to globalThis.__civProf (shared with the walk / work / watch / shop modules); the status carries it
import sys as _sys
_sys.path.insert(0, "/home/claude/tools")
import profwrap as _pw
rep("""import * as KIT from "./pw_civ_streets.js";""", """import * as KIT from "./pw_civ_streets.js";
const PROF = (globalThis.__civProf = globalThis.__civProf || {});
const prof = (name, fn) => () => { const t0 = Date.now(); try { fn(); } finally { PROF[name] = (PROF[name] || 0) + Date.now() - t0; } };""", "profiler helper")
_names = []
for _anchor, _nm in [("const skinOf = (b) => (BUILDINGS[b.family].stem.match(/_([a-z])_r1$/) || [, \"a\"])[1];\n\nsystem.runInterval(() => {", "clock"),
                     ("let kitOpsSinceSave = 0;\nsystem.runInterval(() => {", "kitqueue"),
                     ("let roomLast = 0;\nsystem.runInterval(() => {", "room"),
                     ("  return front(homeB) || square;\n}\nsystem.runInterval(() => {", "schedule")]:
    assert t.count(_anchor) == 1, _nm
    _ln = t[: t.index(_anchor) + len(_anchor) - len("system.runInterval(() => {")].count("\n") + 1
    _names.append((_ln, _nm))
for _ln, _nm in sorted(_names, reverse=True):
    t = _pw.wrap(t, _ln, _nm)
rep("""      rest.quarries = plotsOf(s, st)""", """      rest.prof = { ...(globalThis.__civProf || {}), tick: system.currentTick, ms: Date.now() };
      rest.quarries = plotsOf(s, st)""", "prof in status")

# ---------------------------------------------------------------------------------------------- 0.0.25d: civic works first, and never lost
# runs 0.0.23-0.0.25c: the latrine, the bathhouse and the infirmary never stood. At a tier-up the civic works were laid out
# LAST (after every leftover and every new house had taken the room), and a work that found no room went to st.civicLeft,
# which nothing ever read again. Now the tier's civic works are laid out FIRST, and a civic work without room is retried
# every day before the leftover houses; the leftovers themselves go by rank (prestige, shops, trades, homes)
rep("""  // the founding's leftovers (no room on the first street) come first
  const still = [];""", """  // 0.0.25d: the tier's civic works FIRST (the council's charter), then the old leftovers, then the tier's own plots
  for (const [work, fam] of CIVIC[tier] || []) {
    if (fam === "post") { st.log.push(`day ${s.simDays.toFixed(0)}: the council opens the ${work} office`); continue; }
    const skins = skinsOf(fam);
    const b = addPlot(s, st, familyOf(fam, skins[Math.floor(pick() * skins.length)]), st.dim, k * VILLAGE_STAGGER, pick);
    if (b) { b.civic = work; added.push(b); k++; st.log.push(`day ${s.simDays.toFixed(0)}: the ${work} is laid out (#${b.id}, a ${fam.replace("_", " ")} until its own design)`); }
    else (st.civicLeft = st.civicLeft || []).push([work, fam]);
  }
  const still = [];""", "civic first")
rep("""  // F7: the tier's civic works are laid out with its plots (offices open as census posts)
  for (const [work, fam] of CIVIC[tier] || []) {
    if (fam === "post") { st.log.push(`day ${s.simDays.toFixed(0)}: the council opens the ${work} office`); continue; }
    const skins = skinsOf(fam);
    const b = addPlot(s, st, familyOf(fam, skins[Math.floor(pick() * skins.length)]), st.dim, k * VILLAGE_STAGGER, pick);
    if (b) { b.civic = work; added.push(b); k++; st.log.push(`day ${s.simDays.toFixed(0)}: the ${work} is laid out (#${b.id}, a ${fam.replace("_", " ")} until its own design)`); }
    else (st.civicLeft = st.civicLeft || []).push([work, fam]);
  }
  st.tier = tier;""", """  st.tier = tier;""", "civic no longer last")
rep("""  // 0.0.25b: up to LEFTOVER_PER_DAY a day while room is found (the background room search opens the streets)
  for (let q = 0; q < LEFTOVER_PER_DAY && st.kit && st.leftover && st.leftover.length && st.phase === "built"; q++) {
    const nm = st.leftover[0];""", """  // 0.0.25d: a civic work still without room tries first (one a day)
  if (st.kit && st.phase === "built" && (st.civicLeft || []).length) {
    const [work, fam] = st.civicLeft[0];
    const skins = skinsOf(fam);
    const pk = rng(((st.seed || 1) + Math.floor(s.simDays) * 53) >>> 0);
    const b = addPlot(s, st, familyOf(fam, skins[Math.floor(pk() * skins.length)]), st.dim, 0, pk);
    if (b) { b.civic = work; st.civicLeft.shift(); st.log.push(`day ${s.simDays.toFixed(0)}: room found for the ${work} (#${b.id}, a ${fam.replace("_", " ")} until its own design)`); }
    else st.civicLeft.push(st.civicLeft.shift());
  }
  // the MANOR goes to the front of the leftovers (run 0.0.26: ranking every prestige and craft plot first starved the
  // founding of its farm, quarry and lumberyard — no timber, no bread, nothing built; the order of the rest is the plan's)
  if (st.leftover && st.leftover.length > 1) {
    const rank = (nm) => (nm === "manor" ? 0 : 1);
    st.leftover = st.leftover.map((nm, i) => [nm, i]).sort((a2, b2) => rank(a2[0]) - rank(b2[0]) || a2[1] - b2[1]).map(([nm]) => nm);
  }
  // 0.0.25b: up to LEFTOVER_PER_DAY a day while room is found (the background room search opens the streets)
  for (let q = 0; q < LEFTOVER_PER_DAY && st.kit && st.leftover && st.leftover.length && st.phase === "built"; q++) {
    const nm = st.leftover[0];""", "civic retried + leftovers ranked")
rep("""    if (!st.kit || st.phase !== "built" || !(st.leftover || []).length || (st.kitQueue || []).length > 40) continue;""",
    """    if (!st.kit || st.phase !== "built" || !((st.leftover || []).length || (st.civicLeft || []).length) || (st.kitQueue || []).length > 40) continue;""", "room search for civic too")
rep("""      rest.leftover = (leftover || []).length;""", """      rest.leftover = (leftover || []).length;
      rest.civicLeft = (st.civicLeft || []).map(([w]) => w);""", "civicLeft in status")

# ---------------------------------------------------------------------------------------------- 0.0.25d: the posts outrank the shoppers for bodies
# run 0.0.25c: the night watch had NO ONE on duty (0.0.24: 6) — the shoppers' bodies (3 a day) had filled the cap of 48
# before the city's later watch posts were filled, and a post holder without a body never walks a round. Shoppers now keep
# SHOPPER_RESERVE bodies free for the posts, carry the tag civ:shopper, and give up a body when a post holder needs one
rep("""  for (const p of want) {
    if (made >= 3 || byPid.size >= EMBODY_CAP) break;
    if (byPid.has(p.id) || p.keeper) continue;
    if (!BODY_POSTS.includes(p.job)) { if (homesWithShopper.has(p.home)) continue; homesWithShopper.add(p.home); }""",
    """  // a post holder without a body while the cap is full: a shopper's body (not walking) is released for it
  const postless = want.filter((p) => BODY_POSTS.includes(p.job)).length;
  if (postless && byPid.size >= EMBODY_CAP) {
    let freed = 0;
    for (const [pid, v] of [...byPid]) {
      if (freed >= postless) break;
      if (!v.hasTag("civ:shopper") || WALK.walking(v)) continue;
      const q = PEOPLE.byId(P, pid);
      if (q && BODY_POSTS.includes(q.job)) continue;
      try { v.remove(); byPid.delete(pid); freed++; gone++; } catch { /* left */ }
    }
  }
  for (const p of want) {
    if (made >= 3 || byPid.size >= EMBODY_CAP) break;
    if (byPid.has(p.id) || p.keeper) continue;
    if (!BODY_POSTS.includes(p.job)) { if (byPid.size >= EMBODY_CAP - SHOPPER_RESERVE || homesWithShopper.has(p.home)) continue; homesWithShopper.add(p.home); }""", "posts outrank shoppers")
rep("""      v.nameTag = p.name; v.addTag(`civ:person:${p.id}`); v.addTag("civ:villager"); v.addTag(`civ:settlement:${st.id}`); if (p.home) v.addTag(`civ:home:${p.home}`);
      byPid.set(p.id, v); made++;""", """      v.nameTag = p.name; v.addTag(`civ:person:${p.id}`); v.addTag("civ:villager"); v.addTag(`civ:settlement:${st.id}`); if (p.home) v.addTag(`civ:home:${p.home}`);
      if (!BODY_POSTS.includes(p.job)) v.addTag("civ:shopper");
      byPid.set(p.id, v); made++;""", "shopper tag")
rep("""const EMBODY_CAP = 48, BODY_POSTS = ["watch", "sewer_keeper", "surveyor", "builders"];""",
    """const EMBODY_CAP = 48, BODY_POSTS = ["watch", "sewer_keeper", "surveyor", "builders"], SHOPPER_RESERVE = 12;""", "shopper reserve")

rep("""stands: plotsOf(s, st).filter((b) => short(b) === "lumberyard").map((b) => [b.id, b.felled || 0, b.replanted || 0]) };""",
    """stands: plotsOf(s, st).filter((b) => short(b) === "lumberyard").map((b) => [b.id, b.felled || 0, b.replanted || 0, b.planted || 0]) };""", "coppice in status")

# ---------------------------------------------------------------------------------------------- 0.0.25e: a stage bigger than a day's work
# run 0.0.26b (a cramped site: two plots at the founding, no newcomers yet): ONE building finished by village II — every
# other stage (the farm 82 blocks, the cottage 86, the bakery 127) was bigger than the founders' whole day (2 x 40 = 80)
# and "waited for builders" forever: the day's budget never carried over. Now a crew with its whole day free takes on a
# bigger stage and works it off over the next days (the debt comes out of their next budgets)
rep("""    st.buildBudget = (own + L.hired) * ECON.BLOCKS_PER_BUILDER_DAY;""",
    """    const cap = (own + L.hired) * ECON.BLOCKS_PER_BUILDER_DAY, debt = st.buildDebt || 0;
    st.buildCap = cap; st.buildBudget = Math.max(0, cap - debt); st.buildDebt = Math.max(0, debt - cap);""", "build debt per day")
rep("""        const budget = stt.buildBudget === undefined ? Infinity : stt.buildBudget;
        const miss = ECON.missing(L, bill, budget);""",
    """        const budget = stt.buildBudget === undefined ? Infinity : stt.buildBudget;
        // 0.0.25e: the whole day free; 0.0.25h (run 0.0.27: the manor's 1,146-block stage never found a whole free day — the
        // small stages ahead of it took a little every day): a stage bigger than the crew's whole day starts on any day the
        // crew has work left and no debt
        const fresh = stt.buildCap !== undefined && !(stt.buildDebt > 0) && budget > 0 && (budget >= stt.buildCap || bill.blocks > stt.buildCap);
        const miss = ECON.missing(L, bill, fresh ? Infinity : budget);""", "big stage on a free day")
rep("""        ECON.pay(L, bill);
        stt.buildBudget = budget - bill.blocks;""",
    """        ECON.pay(L, bill);
        stt.buildBudget = budget - bill.blocks;
        if (stt.buildBudget < 0) { stt.buildDebt = (stt.buildDebt || 0) - stt.buildBudget; stt.buildBudget = 0; }""", "build debt")

# ---------------------------------------------------------------------------------------------- 0.0.25f: the wagons carry the whole founding plan
# run 0.0.26c (the cramped site): the settlers' wagons carried the bill of the 2 plots that fit at the founding — the
# other founding plots (placed from the leftovers on day 6) found no timber, stone, planks or glass for weeks
rep("""  for (const b of plotsOf(s, st)) {
    const bom = BUILDINGS[b.family].bom || [];
    for (let k = 1; k < bom.length; k++) for (const [m, n] of Object.entries(bom[k])) need[m] = (need[m] || 0) + n;
  }
  for (const [m, n] of Object.entries(need)) if (ECON.MATS.includes(m)) L.stock[m] = (L.stock[m] || 0) + Math.ceil(n * 1.2);""",
    """  const fams = plotsOf(s, st).map((b) => b.family);
  for (const nm of st.leftover || []) { const sk = skinsOf(nm); if (sk.length) fams.push(familyOf(nm, sk[0])); }   // 0.0.25f: the plan's waiting plots too
  for (const fam of fams) {
    const bom = (BUILDINGS[fam] && BUILDINGS[fam].bom) || [];
    for (let k = 1; k < bom.length; k++) for (const [m, n] of Object.entries(bom[k])) need[m] = (need[m] || 0) + n;
  }
  for (const [m, n] of Object.entries(need)) if (ECON.MATS.includes(m)) L.stock[m] = (L.stock[m] || 0) + Math.ceil(n * 1.2);""", "genesis covers the plan")

# ---------------------------------------------------------------------------------------------- 0.0.25g: the hands found once a beat
rep("""  hands: (st, b) => {
    const out = [];
    try {
      for (const v of world.getDimension(st.dim).getEntities({ tags: [`civ:settlement:${st.id}`], type: VILLAGER_ID })) {
        if (v.hasTag("civ:keeper") || v.hasTag("civ:watching")) continue;
        const tag = v.getTags().find((x) => x.startsWith("civ:person:"));
        const p = tag && st.people ? PEOPLE.byId(st.people, Number(tag.slice(11))) : null;
        if (p && p.alive && p.job === b.id) out.push(v);
      }
    } catch { /* unloaded */ }
    return out;
  },""", """  hands: (st, b) => {
    // 0.0.25g (the profiler): the settlement's villagers are read ONCE a tick for all its workshops (was once per workshop)
    const now = system.currentTick;
    let hc = handsCache.get(st.id);
    if (!hc || hc.tick !== now) {
      hc = { tick: now, by: new Map() };
      try {
        for (const v of world.getDimension(st.dim).getEntities({ tags: [`civ:settlement:${st.id}`], type: VILLAGER_ID })) {
          if (v.hasTag("civ:keeper") || v.hasTag("civ:watching")) continue;
          const tag = v.getTags().find((x) => x.startsWith("civ:person:"));
          const p = tag && st.people ? PEOPLE.byId(st.people, Number(tag.slice(11))) : null;
          if (p && p.alive && typeof p.job === "number") { if (!hc.by.has(p.job)) hc.by.set(p.job, []); hc.by.get(p.job).push(v); }
        }
      } catch { /* unloaded */ }
      handsCache.set(st.id, hc);
    }
    return hc.by.get(b.id) || [];
  },""", "hands cached per tick")
rep("""const bodiesNow = new Map();""", """const bodiesNow = new Map();
const handsCache = new Map();                                      // 0.0.25g: settlement id -> { tick, by: workshop id -> villagers }""", "hands cache decl")

# ---------------------------------------------------------------------------------------------- 0.0.25g: at most SENDS_PER_BEAT new walks a beat
# the profiler (run 0.0.26d): the schedule beat cost 100-400 ms every 5 s — each new walk plans a route and its off-graph
# legs (a local A* over the real blocks); a beat now starts at most SENDS_PER_BEAT walks, the rest go on the next beat
rep("""      if (here <= 3) { if (WALK.walking(v)) WALK.cancel(v); continue; }
      if (!WALK.walking(v)) WALK.send(v, st, g);
    }""", """      if (here <= 3) { if (WALK.walking(v)) WALK.cancel(v); continue; }
      if (!WALK.walking(v) && sends < SENDS_PER_BEAT) { sends++; WALK.send(v, st, g); }
    }""", "sends per beat")
rep("""    { const ids = new Set(); for (const v of vs) { const tg = v.getTags().find((x) => x.startsWith("civ:person:")); if (tg) ids.add(Number(tg.slice(11))); } bodiesNow.set(st.id, ids); }""",
    """    { const ids = new Set(); for (const v of vs) { const tg = v.getTags().find((x) => x.startsWith("civ:person:")); if (tg) ids.add(Number(tg.slice(11))); } bodiesNow.set(st.id, ids); }
    let sends = 0;""", "sends counter")
rep("""const handsCache = new Map();""", """const handsCache = new Map();
const SENDS_PER_BEAT = 6;""", "sends const")

# ---------------------------------------------------------------------------------------------- 0.0.25i: the occupied test cached
# the profiler (run 0.0.27, real time): the work beat cost 5-14 ms a tick and pulled the server from 19.5 to ~15.5 TPS —
# every hand's face / tree / coppice search built the town's occupied set anew (every street cell and its 4 neighbours as
# strings, ~100,000 entries); it is now built once per change of the town (plots, streets) and at most every 20 s
rep("""function occupiedTest(s, st = null) {
  const boxes = plotBoxes(s, 1, null);""", """let occCache = null;
function occupiedTest(s, st = null) {
  const okey = `${s.buildings.length}:${s.settlements.map((x) => `${x.kitVer || 0}/${(x.streets || []).length}`).join(",")}`;
  if (occCache && occCache.key === okey && system.currentTick - occCache.tick < 400) return occCache.fn;
  const fn = occupiedBuild(s, st);
  occCache = { key: okey, tick: system.currentTick, fn };
  return fn;
}
function occupiedBuild(s, st = null) {
  void st;
  const boxes = plotBoxes(s, 1, null);""", "occupied cached")

# ---------------------------------------------------------------------------------------------- 0.0.25i: the counters say what happened
# run 0.0.27: the first market hour stocked the counters (no error) and the shoppers still found nothing — each stocking
# now records per shop what it did (n, or why not), into the status (counters)
rep("""    if (!COUNTER[kind] || b.stage < 4 || b.closed) continue;
    const c = chestOf(b);
    if (!c) continue;
    const good = kind === "bakery" ? "bread" : "meat";
    const have = L && L.stock ? Math.floor(L.stock[good] || 0) : 0;
    const n = Math.min(16, Math.max(0, have > 0 ? Math.ceil(households(s, st) / 2) : 0));
    if (!n) continue;
    try { const inv = dim.getBlock(c)?.getComponent("minecraft:inventory"); if (inv && inv.container) inv.container.addItem(new ItemStack(COUNTER[kind][0], n)); } catch { /* unloaded */ }""",
    """    if (!COUNTER[kind] || b.stage < 4 || b.closed) continue;
    const rec = (st.counters = st.counters && st.counters.day === Math.floor(s.simDays) ? st.counters : { day: Math.floor(s.simDays), shops: [] });
    const c = chestOf(b);
    if (!c) { rec.shops.push([b.id, kind, 0, "nochest"]); continue; }
    const good = kind === "bakery" ? "bread" : "meat";
    const have = L && L.stock ? Math.floor(L.stock[good] || 0) : 0;
    const n = Math.min(16, Math.max(4, have > 0 ? Math.ceil(households(s, st) / 2) : 0));                   // 0.0.25i: at least 4
    if (!have) { rec.shops.push([b.id, kind, 0, "nostock"]); continue; }
    let why = "ok";
    try {
      const blk = dim.getBlock(c);
      if (!blk) why = "unloaded";
      else { const inv = blk.getComponent("minecraft:inventory"); if (!inv || !inv.container) why = `noinv:${blk.typeId}`; else { const rest = inv.container.addItem(new ItemStack(COUNTER[kind][0], n)); if (rest) why = `full:${rest.amount}`; } }
    } catch (e) { why = `err:${String(e).slice(0, 40)}`; }
    rec.shops.push([b.id, kind, n, why, c.x, c.y, c.z]);""", "counters diagnosed")
rep("""      rest.marketTry = st.marketTry ?""", """      rest.counters = st.counters || null;
      rest.marketTry = st.marketTry ?""", "counters in status")

# ---------------------------------------------------------------------------------------------- 0.0.25j: the market gate recorded
# run 0.0.28: in the market hour the counters' record stayed null all along (not one stocking reached a shop) — the gate's
# inputs are kept on the settlement (day, the day last stocked, skipping?) so the next run says which one held it shut
rep("""    if (tod >= MARKET[0] && tod < MARKET[1] && !((s.accelLeft || 0) > 1e-9) && st.stockedDay !== Math.floor(s.simDays)) {""",
    """    if (tod >= MARKET[0] && tod < MARKET[1]) st.marketGate = [Math.floor(s.simDays), st.stockedDay ?? null, !!s.accelNow, (s.accelLeft || 0) > 1e-9 ? 1 : 0, plotsOf(s, st).filter((b) => COUNTER[short(b)]).map((b) => [b.id, b.stage, b.closed ? 1 : 0])];
    if (tod >= MARKET[0] && tod < MARKET[1] && !((s.accelLeft || 0) > 1e-9) && st.stockedDay !== Math.floor(s.simDays)) {""", "market gate")
OUT.write_text(t)
print(f"wrote {OUT} ({len(t):,} chars)")
