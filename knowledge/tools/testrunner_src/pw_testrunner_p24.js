// pw_testrunner_p24.js — lineup "p24" CIVITAS CITY: THE TOWN THAT WORKS (PW-TestRunner BP v0.5.23, 2026-10-04).
// /scriptevent pw:test start p24 — BP-02 v1.3.219 (StreetKit streets, sewer exits v2, manholes + the key register,
// villagers that walk, mine, build and shop in real time, the night watch above and below ground, boundary stones moved by
// a surveyor, civic works + sanitation, neighbourhood markets, the manor, green-corridor roads, the mob size pass) +
// RP-04 v1.3.158 (the walking lead + the sewer key's icon) + Markers BP v0.2.3.
// Every step sends /scriptevent pw:clock commands for him (as the player), then says what to look for. The BDS probe
// (tools/kit_village_probe.py) already checks every block of every building; THIS round is what only a human can judge.

function lines(text) {
  const out = [];
  for (const para of String(text).split("\n")) {
    let cur = "";
    for (const piece of para.split(/(?<=[.!?:]) +| (?=- )/)) {
      if (cur && (cur + " " + piece).length > 190) { out.push(cur); cur = piece; } else cur = cur ? cur + " " + piece : piece;
    }
    if (cur) out.push(cur);
  }
  return out.join("\n");
}
const PASSN = "PASS = right. FAIL + note = what is off (and where: a villager's name tag, the street, the building). Notes have 3 boxes - use them all if you need to.";
const C = (...cmds) => ({ cmd: cmds.map((c) => `scriptevent pw:clock ${c}`) });

const Q0 = { id: "q0", group: "P24 SETUP", title: "P24 CIVITAS CITY: A HILLSIDE, SIMULATION DISTANCE UP, CREATIVE, FACE NORTH",
  body: lines("Packs: BP-02 v1.3.219 (replaces 1.3.215 and every earlier 1.3.2xx) + RP-04 v1.3.158 (replaces 1.3.156 / 1.3.157) + Markers BP v0.2.3 (replaces 0.2.1; the Markers RP 0.2.2 stays), PW-TestRunner BP v0.5.23 at the bottom. " +
    "Content log after load: '[CIV-CLOCK] village clock loaded — 39 staged building(s)'.\n" +
    "Settings > Game: SIMULATION DISTANCE as high as your console allows (8+ chunks).\n" +
    "Stand on a HILLSIDE with about 150 blocks of land each way (a river within 100 blocks is a bonus: the sewer will find it). CREATIVE. FACE NORTH.\n" +
    "Nothing is placed yet. PASS = ready. FAIL + note = versions or log differ."),
  setup: [{ daytime: "noon" }, { weather: "clear" }, { cmd: ["gamemode creative @s", "tag @s add civ:tester"] }] };

const STEPS24 = [
  { id: "d01", group: "P24 FOUNDING", title: "FOUND THE TOWN: THE SQUARE, THE STREETKIT MAIN STREET, A PARALLEL STREET, THE BOUNDARY STONES",
    body: lines("The clock reads the land (10-20 s), then founds: the 12 x 12 SQUARE with the well, the MAIN STREET of your StreetKit pieces (sidewalks, curbs, the cobbled road, 1-in-7 ramps, a dead end at each end), " +
      "a PARALLEL street about 60 blocks away joined by a cross street, and a ring of BOUNDARY STONES (a mossy cobblestone block with a mossy wall on top, every 16 blocks) 100-200 blocks out.\n" +
      "Look for: the street following the hill without cuttings deeper than 6; where the ground falls away beside a sidewalk, a BERM (grass, level with the sidewalk) or a stone-brick RETAINING WALL with a cobblestone-wall PARAPET - nobody can step off into a hole. Find one boundary stone.\n" +
      "SHOT of the square + street, one of a parapet or berm, one of a boundary stone.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("village 7", "pause")] },
  { id: "d02", group: "P24 SEWER", title: "BELOW THE STREET: A MANHOLE, YOUR KEY, THE RUNNING SEWER AND WHERE IT GOES",
    body: lines("Twenty days pass. You were tagged civ:tester, so you get a TEST KEY (a sewer key in your inventory; it is the only way a player gets one here - no recipe, no shop).\n" +
      "Find a MANHOLE COVER in a sidewalk (a round cover every 26 cells or so on level stretches). Hold the KEY and tap the cover FROM ABOVE: it slides open ('the cover lifts'). Without the key: 'It won't budge.' A key that is not yours: 'The lock doesn't know this key.'\n" +
      "Climb down: the HALL under the street, water running in the trench, LANTERNS in the wall niches (no dark sewer). Walk to the street's LOW POINT: a TRUNK leaves it through a lined tunnel (lanterns every 12, the floor stepping down) to a GRATE in a hillside or river bank with water spilling out - or a SOAKAWAY: a gravel pit under the trench. The higher dead ends are sealed.\n" +
      "The open cover shuts itself ~15 s after you leave the shaft. /scriptevent pw:clock log names the exit ('the sewer drains into the water / out of the hillside / into a soakaway').\n" +
      "SHOT of the cover open, the hall with water, the mouth or the pit.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("skip 20", "keytest", "log")] },
  { id: "d03", group: "P24 REAL WORK", title: "MORNING AT THE QUARRY: THE HANDS MINE THE FACE AND CARRY TO THE CHEST",
    body: lines("Time is set to the morning (1000); the clock stays paused, so everything you see now happens in REAL time.\n" +
      "Go to the QUARRY (a stepped pit on the best rock beside or behind the quarry hut - a spent pit makes way for the next site, six at most, then the quarry is 'worked out' and a new one is chartered). Watch the QUARRYMAN (name tag 'Kari the Quarryman' or similar) and any other hands: they walk to a face in the pit (down the benches, up ladders rung by rung), strike it (stone sounds, one block every ~2 s), " +
      "and when their barrow is full (16) walk to the quarry hut's CHEST and put it in. Open that chest: cobblestone appears there, nowhere else.\n" +
      "Watch for 3-4 minutes. Also: villagers walking to work along the streets (each behind its OWN invisible lead), nobody teleporting, nobody stuck in a cellar or on a ladder. " +
      "At the LUMBERYARD: the woodcutter fells the nearest tree and plants a sapling by the stump; where no tree stands in reach he plants a COPPICE (saplings in rows near the yard).\n" +
      "SHOT of a hand at the face, the chest's contents.\n" + PASSN),
    setup: [{ daytime: 1000 }] },
  { id: "d04", group: "P24 REAL WORK", title: "THE BUILDERS AND THE MIDDAY MARKET",
    body: lines("A real building site is opened (a fifth of a stage's labour, so it finishes in minutes). The BUILDERS walk to it and work (stone / wood sounds); when their labour is done the stage RISES LAYER BY LAYER.\n" +
      "Then at MIDDAY (5000-7000) one person from each household walks to a BAKERY or BUTCHER counter and buys a loaf or a cut: it leaves the shop's chest (open it before and after). The counters are filled each morning (or at the first market hour after skipped days). An empty counter goes into the chronicle ('found nothing at the counter').\n" +
      "Look for: the stage rising in layers (not popping in), shoppers at the counters, the chests going down.\n" + PASSN),
    setup: [{ daytime: 1000 }, C("realstage 0.2")] },
  { id: "d05", group: "P24 GROWTH", title: "TOWN I-II: THE WATCH, THE MANOR, THE NEIGHBOURHOOD MARKET, THE CIVIC WORKS, A BENCH",
    body: lines("The village grows through village II, village III and town I to TOWN II (72 days). New: WATCH posts (2, then 3), the MANOR HOUSE (on the main street when it has room, else on the first street that has - a bench on a crowded hill; stone ground floor, oak upper storey, big hipped roof, three chimneys; its big stage may wait a few days for GLASS, which only the wandering merchant brings), " +
      "a NEIGHBOURHOOD MARKET on the parallel street (a well with a bakery and a butcher beside it), the civic works as stand-ins (a small cottage as the LATRINE, a well as the CISTERN), and a BENCH street up the hill reached by a narrow switchback road (1-in-4 four-part ramps).\n" +
      "Walk into the MANOR: the parlour / hall / dining hall in front; the plain spruce door in the hall's back wall that looks like the wall (the JIB door) and the GREEN door (the BAIZE door) into the hidden SERVICE CORRIDOR; " +
      "the kitchen, the back stair (one ladder from cellar to roof), the steward's office with the lectern, the pantry; the chambers upstairs; the servants' beds in the roof.\n" +
      "SHOT of the manor front, the service corridor, the garrets; the neighbourhood market.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("grow", "skip 12", "grow", "skip 12", "grow", "skip 24", "grow", "skip 24", "log")] },
  { id: "d06", group: "P24 NIGHT", title: "THE NIGHT WATCH: ROUNDS ABOVE AND BELOW, THREE ZOMBIES ON THE SQUARE",
    body: lines("Night falls (14000) and three ZOMBIES are let loose beside you. Stay in creative, out of the way.\n" +
      "Look for: the WATCHMEN walking their rounds from stop to stop along every street; one of them reaching a manhole, the cover opening (their key), climbing down rung by rung, and coming up at the next manhole along the street, the cover shutting behind; " +
      "the zombies struck by a watchman within reach (a strong-hit sound) and gone within a minute.\n" +
      "/scriptevent pw:clock log tells rounds and kills next morning.\n" + PASSN),
    setup: [{ daytime: 14000 }, { cmd: ["summon zombie ~4 ~ ~4", "summon zombie ~-4 ~ ~4", "summon zombie ~4 ~ ~-4"] }] },
  { id: "d07", group: "P24 CITY", title: "CITY I: THE WALL, THE GREENBELT, THE INFIRMARY, THE STONES MOVED OUT",
    body: lines("The town becomes a CITY (about 120 more days): the stone-brick WALL rings the built ground with GATES; outside it a GREENBELT about 24 blocks wide stays unbuilt (benches excepted). " +
      "The BOUNDARY STONES stand further out than at the founding (the SURVEYOR carried them - on skipped days they move at once). The civic works for a city: a WELL-HOUSE and an INFIRMARY (a large cottage stand-in with a healer).\n" +
      "Look for: no house within ~24 blocks outside the wall except on bench streets; the quarry's OLD PIT greening (grass and flowers coming back on its floor) while the hands work a NEW pit beside it.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("grow", "skip 24", "grow", "skip 46", "log")] },
  { id: "d08", group: "P24 WORLD", title: "THE DAUGHTER AND THE GREEN-CORRIDOR ROAD",
    body: lines("Settlers leave for a new site (chat: 'settlers set out for X Z'; it is chosen clear of every street, building and boundary ring). Go there: the daughter's square and street.\n" +
      "The ROAD between the two towns: a 3-HIGH SPRUCE FENCE along both sides, closed from gate to gate, and every ~80 blocks a WILDLIFE CROSSING - a grass-topped OVERPASS where the road runs in a cutting, a grass-floored UNDERPASS where it runs on an embankment.\n" +
      "SHOT of the fenced road and one crossing.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("skip 80", "log")] },
  { id: "d09", group: "P24 MOBS", title: "THE SIZE PASS: GIANTS 2.5 x THEIR SMALL KIN, SMALL HOSTILES GENTLER",
    body: lines("Two pairs are summoned beside you: a blue CRAB and a GIANT blue crab; a desert SCORPION and a GIANT desert scorpion.\n" +
      "Look for: each giant about 2.5 times its small kin (the crab's shell scales with it - one model); in SURVIVAL (switch for a moment) a small hostile hits for at most one heart and half as often as before; a giant hits harder than its kin but not as hard as before.\n" +
      "The full before / after table is in the delivery (MOB-PASS-G.md).\n" + PASSN),
    setup: [{ daytime: "noon" }, { cmd: ["summon pw:crab_blue_anf ~3 ~ ~", "summon pw:giant_crab_blue_anf ~6 ~ ~", "summon sf_nba:desert_scorpion ~3 ~ ~4", "summon pw:giant_desert_scorpion_nba ~6 ~ ~4"] }] },
];
const Q9 = { id: "q9", group: "P24 DONE", title: "P24: UPLOAD",
  body: lines("Leave the towns standing (they are the witness evidence). Upload the shots and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or /scriptevent pw:test report p24.\n" +
    "PASS = uploaded (or about to)."),
  setup: [{ daytime: "noon" }, C("resume")] };

export const P24_STEPS = [Q0, ...STEPS24, Q9];
export const P24_INDEX = Object.fromEntries(P24_STEPS.map((s, i) => [s.id, i]));
