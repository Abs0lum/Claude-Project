// pw_testrunner_p22.js — lineup "p22" CIVITAS: THE LIVING TOWN ON THE LAND (PW-TestRunner BP v0.5.15, D-C498/D-C499, 10-02/03).
// /scriptevent pw:test start p22 — BP-02 v1.3.207 (the village clock: founding on the real land, contour streets on either
// axis, terraces, yards + stoops, hill cladding, bridges + cuttings, living marks, tiers, economy + market, decline /
// immigration, daughters + A* roads + trade + the ladder, the notice board) + RP-07 v1.4.45 + RP-08 v1.4.14.
// Every step sends a /scriptevent pw:clock command for him (as the player), then tells him what to look for.
// The server probe (tools/civ_evo_probe.py) already checks every block of every building; THIS round is the witness
// round for what only a human can judge: does it read as a town, does the land look worked, do the villagers live.

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
const PASSN = "PASS = right. FAIL + note = what is off (and where: the building's name tag / the street). Notes have 3 boxes - use them all if you need to.";
const C = (...cmds) => ({ cmd: cmds.map((c) => `scriptevent pw:clock ${c}`) });

const Q0 = { id: "q0", group: "P22 SETUP", title: "P22 CIVITAS: A HILLSIDE, SIMULATION DISTANCE UP, CREATIVE, FACE NORTH",
  body: lines("Packs: BP-02 v1.3.214 (replaces 1.3.207 … 212) + RP-07 v1.4.45 + RP-08 v1.4.14 (they replace 1.4.44 / 1.4.13), PW-TestRunner BP v0.5.20 at the bottom. " +
    "Content log after load: '[CIV-CLOCK] village clock loaded — 38 staged building(s)'.\n" +
    "Settings > Game: SIMULATION DISTANCE as high as your console allows (8+ chunks) - the town reads the land 80 blocks around you.\n" +
    "Stand on a HILLSIDE (a slope, a knoll, a valley side - NOT flat plains, NOT a cliff face), with 100 blocks of land each way. Water nearby is a bonus (a pier). CREATIVE. FACE NORTH.\n" +
    "Nothing is placed yet. PASS = ready. FAIL + note = versions or log differ."),
  setup: [{ daytime: "noon" }, { weather: "clear" }, { cmd: ["gamemode creative @s"] }] };

const STEPS22 = [
  { id: "c01", group: "P22 FOUNDING", title: "FOUND THE TOWN WHERE YOU STAND: THE SQUARE, THE CONTOUR STREET, THE FIRST PLOTS",
    body: lines("The clock reads the land around you (10-20 seconds: chat says 'reading the land', then 'founded: square at X Z ... contour street y N with K run(s)').\n" +
      "Look for: 1) a 12 x 12 paved SQUARE on the flattest knoll near you - cobblestone border, four lantern posts, the WELL in the middle, a SIGN at its south-west corner (the notice board). " +
      "2) the MAIN STREET leaving the square along the hill's CONTOUR (it may run north-south or east-west - whichever the hill offers): a 3-wide path, cobblestone steps where it rises, never more than one block per step. " +
      "3) the first PLOTS staked along it: levelled terraces (cobblestone retaining faces on the downhill side, dirt inside), each with a 2-cell FRONT YARD and stoop steps up to its door cell.\n" +
      "Walk the whole street end to end. SHOT of the square and of the street.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("village 7", "pause")] },
  { id: "c02", group: "P22 FOUNDING", title: "SIX DAYS: THE FIRST HOUSES STAND, FAMILIES MOVE IN",
    body: lines("Six village days pass at once. The first plots go frame -> walls -> roof -> furnished; the farm's wheat is planted.\n" +
      "Look for: finished houses with their DOORS FACING THE STREET, stoops in the yards (no step on the street itself), roofs whole, the hill side of a house cut into the slope with a cobblestone face. " +
      "Villagers appear inside furnished homes - their names read 'Ada', 'Bram' ... and later 'Ada the Farmer' once they work.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("skip 6")] },
  { id: "c03", group: "P22 VILLAGE", title: "DAY 20: THE WHOLE VILLAGE - WALK THE STREET, READ THE BOARD",
    body: lines("Fourteen more days: every founding plot is finished (farm, cottages, bakery, town hall, inn, butcher, smithy, quarry, lumberyard, cattle farm, well).\n" +
      "Walk the street end to end AGAIN: no hole in the path, no 2-block step, every house reachable from the street through its yard. " +
      "Read the SIGN on the square: the last lines of the town's chronicle (founding, who moved in). /scriptevent pw:clock log prints the whole chronicle in chat.\n" +
      "SHOT down the street from each end.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("skip 14", "log")] },
  { id: "c04", group: "P22 GROWTH", title: "DAY 30: VILLAGE2 - A SECOND STREET ON THE NEXT TERRACE, THE HILLSIDE FIELD",
    body: lines("Ten more days: the village reaches its second tier. A NEW STREET opens on the terrace above or below the first (6 blocks higher or lower, following its own contour), new plots on it, " +
      "the HILLSIDE FIELD (four climbing strips of wheat with cobblestone retaining walls, a water channel, a stair), and the streets harden from path to GRAVEL. Behind the quarry a stepped PIT is dug.\n" +
      "Look for: the second street never cuts through a standing house; the field's strips step up the hill one block at a time; the water channel holds (no flooding, no dry air pocket).\n" + PASSN),
    setup: [{ daytime: "noon" }, C("skip 10", "log")] },
  { id: "c05", group: "P22 GROWTH", title: "DAY 70: TOWN - THREE STREETS, HOUSES IN THE HILL, BRIDGES OR CUTTINGS",
    body: lines("Forty days: TOWN. Another terrace street, more houses and shops. Where a street crosses a gully it stands on a plank BRIDGE (log piers, fence rails); where it passes through a rise it is a CUTTING with cobblestone walls.\n" +
      "Look for: houses on the uphill side cut into the slope (cobblestone retaining faces at their sides), the lumberyard's CLEARING (stumps where trees stood - only if trees were near), the quarry pit deeper.\n" +
      "SHOT from above the town (fly up 40 blocks, look down) and one along a terrace street.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("skip 40", "log")] },
  { id: "c06", group: "P22 ECONOMY", title: "DAY 140: TOWN2 + THE MARKET - BUY BREAD WITH EMERALDS",
    body: lines("Seventy days: TOWN2 (second shops, more homes; streets COBBLED). You get 16 emeralds.\n" +
      "Chat shows the MARKET: every good's stock and price in coin (1 emerald = 4 coin). Then: /scriptevent pw:clock buy bread 4 -> bread in your hand, emeralds taken; /scriptevent pw:clock sell cobblestone 8 (hold cobblestone) -> emeralds back at 70 %.\n" +
      "Look for: prices that moved since day 20 (short goods dearer, surplus cheaper, never below half or above double the base), the treasury growing.\n" +
      "PASS = buy and sell both work and the numbers make sense. FAIL + note = what happened."),
    setup: [{ daytime: "noon" }, { give: [["emerald", 16], ["cobblestone", 16]] }, C("skip 70", "market")] },
  { id: "c07", group: "P22 DECLINE", title: "HARD TIMES: TWO SHOPS CLOSE, THEN NEWCOMERS REOPEN ONE",
    body: lines("The town is set to DECLINE and 45 days pass: every 20 days a shop closes - COBWEBS in its doorway, its work stations gone, its family leaves (the house empties). " +
      "Then NEWCOMERS arrive: the first closed shop REOPENS (webs gone, stations back, a family moves in), and decline is switched off.\n" +
      "Look for: the closed shop(s) you can find by their webs; the reopened one clean again; chat lines 'closed', 'left', 'reopened'. /scriptevent pw:clock log tells which.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("decline on 1", "skip 45", "immigrate cottage_s 1", "decline off 1", "log")] },
  { id: "c08", group: "P22 WORLD", title: "DAY 300: CITY WALL + SETTLERS LEAVE - WALK TO THE NEW SITE",
    body: lines("Eighty days, then eighty more: the town becomes a CITY - a stone-brick WALL 4 high rings the built ground with GATES where the streets cross it - and, once it has fed everyone for 30 days, " +
      "SETTLERS SET OUT: chat says 'settlers set out for X Z' (170-230 blocks away).\n" +
      "WALK (or fly) to X Z and stay there a minute: the daughter reads her own land and founds her own square and street. Then walk BACK along the straight line between the two squares and wait: " +
      "the ROAD is found over the real ground (around every house, across streets at their own level, never through a plot) and laid - path, steps, bridges where it must.\n" +
      "Look for: the wall (no wall through a house), the gates, the daughter's square + street, the road joining the end of one town's street to the other's.\n" +
      "SHOT of a gate, of the daughter from above, of the road.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("skip 80", "skip 80", "log")] },
  { id: "c09", group: "P22 WORLD", title: "TRADE ALONG THE ROAD: WAGON LINES, A MARKET STAND, NAMED TRADES",
    body: lines("Thirty days with both towns loaded (stand between them, or fly over): goods move along the road from the cheaper town to the dearer one.\n" +
      "Look for: chronicle lines 'wagons: 12 grain out, 8 bread in' (/scriptevent pw:clock log), after 5 days of inbound goods a MARKET STAND on the square (two trestle tables and a barrel), " +
      "villagers whose names now carry their trade ('Cora the Farmer', 'Dag the Butcher'), the notice board updated.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("skip 30", "log")] },
  { id: "c10", group: "P22 WORLD", title: "SNAPSHOT: SAVE THE TOWN, LOAD IT BACK",
    body: lines("The town is saved ('snapshot save v6') and loaded back ('snapshot load v6'): every building is re-placed at its saved stage, villagers cleared and re-homed.\n" +
      "Look for: the town exactly as it was (same houses, streets, yards, wall), chat 'snapshot v6 loaded'.\n" + PASSN),
    setup: [{ daytime: "noon" }, C("snapshot save v6", "snapshot load v6", "status")] },
];
const Q9 = { id: "q9", group: "P22 DONE", title: "P22: UPLOAD",
  body: lines("Leave the towns standing (they are the witness evidence). Upload the shots and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or /scriptevent pw:test report p22.\n" +
    "PASS = uploaded (or about to)."),
  setup: [{ daytime: "noon" }, C("resume")] };

export const P22_STEPS = [Q0, ...STEPS22, Q9];
export const P22_INDEX = Object.fromEntries(P22_STEPS.map((s, i) => [s.id, i]));
