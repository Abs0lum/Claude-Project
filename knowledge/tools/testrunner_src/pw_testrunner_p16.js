// pw_testrunner_p16.js — lineup "p16" THE LEAF ROLLOUT (PW-TestRunner BP v0.5.2, D-C343..D-C348; his GO 18:44 CT 09-30;
// m01-m10 the 128 vs 256 comparison, his 19:33 / 19:41).
// /scriptevent pw:test start p16 — BP-02 v1.3.197 + RP-01 v1.3.106: the pilot leaves (p15 27/27 PASS) are now OUR leaves, same block
// names. Real BP-02 trees, no swapping: what a new world generates (every leaf on its default look, far from you), each leaf getting
// its look ONCE as you walk in (cards beside the wood), nothing re-rolling after a relog, the game's own far switch + shadows, every
// species + the new azalea leaves, felling, decay, breaking / placing by hand, random picture turns, a forest, and the /place probe.
// The tree jobs are the p15 ones (runLeafSetup in pw_testrunner_p15.js): trees grow by the script API, then the command, then a
// stand-in — every refusal reason is logged.

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
const NEAR = { leafarea: { name: "pw_pilot_near", box: [-58, -5, -62, 58, 40, 2] } };
const FAR_AREA = { leafarea: { name: "pw_pilot_far", box: [-46, -5, -130, 46, 40, -4] } };
const PROBE_AREA = { leafarea: { name: "pw_probe_area", box: [-58, -5, -48, 58, 40, 2] } };
const T = (sp, age, dx, dz, extra) => ({ leaftree: { sp, age, dx, dz, keep: true, ...(extra || {}) } });
const PASSN = "PASS = right. FAIL + note = what is off (and where).";

const Q0 = { id: "q0", group: "P16 SETUP", title: "P16 LEAF ROLLOUT: A COPY OF THE TEST WORLD, PS5, VIBRANT VISUALS ON, FACE NORTH",
  body: lines("Packs: BP-02 v1.3.197 + RP-01 v1.3.106 (they replace v1.3.195 / v1.3.104 - always together), PW-TestRunner BP v0.5.2 at the bottom. " +
    "PW-TestRunner RP v0.5.0 at the TOP of the resource packs (it replaces v0.4.0: the 256 test leaves for m01-m10). Use a COPY of the test world. PS5, Vibrant Visuals ON, Creative.\n" +
    "Content log after load: '[PW-VERSION] BP-02 v1.3.197' and 'PW Test Runner BP v0.5.2'.\n" +
    "Stand on big FLAT open ground (60 blocks clear each side, 130 NORTH) and FACE NORTH.\nPASS = ready. FAIL + note = versions or log differ."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };

const STEPS16 = [
  { id: "n01", group: "P16 NEW TREES", title: "WHAT A NEW WORLD GENERATES (FROM HERE, 40 BLOCKS AWAY)",
    body: lines("Six of OUR trees grow 40 blocks NORTH (oak, birch, spruce, jungle, acacia, cherry). Stay HERE first: they are beyond the leaf scanner, so every leaf shows its plain default look - exactly what a NEW world generates.\n" +
      "Look for: full, leafy crowns (no solid green boxes, no missing leaves). Note how far they look from here.\n" +
      "SHOT 1 from here (zoom if you can).\n" + PASSN),
    setup: [NEAR, { leafclear: { box: [-56, 56, -50, -30], h: 30 } }, { daytime: "noon" },
      T("oak", "mature", -45, -40), T("birch", "old", -27, -40), T("spruce", "old", -9, -40), T("jungle", "old", 9, -40),
      { leaftree: { sp: "acacia", dx: 27, dz: -40, keep: true } }, { leaftree: { sp: "cherry", dx: 46, dz: -40, keep: true } }] },
  { id: "n02", group: "P16 NEW TREES", title: "WALK IN: EACH LEAF GETS ITS LOOK ONCE",
    body: lines("Walk NORTH to the six trees. Within about 25 blocks the scanner gives each leaf its look ONCE: leaves touching the wood become the light 'cards only' look, the rest stay full.\n" +
      "Look for: the change happening as you come close, then NOTHING changing again while you stand there or walk around them.\n" +
      "SHOT 2 under the oak, looking up. SHOT 3 the jungle tree close.\n" + PASSN),
    setup: [{ daytime: "noon" }] },
  { id: "n03", group: "P16 NEW TREES", title: "RELOG: NOTHING RE-ROLLS",
    body: lines("Stand where you can see the OAK and the CHERRY clearly. SHOT 4.\nThen Save & Quit, rejoin, type /scriptevent pw:test resume, stand in the same spot and take SHOT 5.\n" +
      "Look for: SHOT 4 and SHOT 5 are the SAME leaves - every leaf kept its look.\nPASS = identical. FAIL + note = which leaves changed."),
    setup: [{ daytime: "noon" }] },
  { id: "n04", group: "P16 FAR + SHADE", title: "THE GAME'S OWN FAR SWITCH + THE SHADE AT NOON",
    body: lines("Five identical rows NORTH at 20, 44, 68, 92 and 116 blocks: OAK, SPRUCE, BIRCH (all our real trees now, no test blocks).\n" +
      "Walk SOUTH looking back: where do they turn solid, and does the solid look read as leaves (not black, not white)?\n" +
      "Then stand UNDER the nearest oak at noon and look at the GROUND: dappled shade (sun spots), not a solid square shadow.\n" +
      "SHOTS: far, then the ground under the oak.\n" + PASSN),
    setup: [FAR_AREA, { leafclear: { box: [-45, 45, -128, -2], h: 30 } }, { daytime: "noon" }, { weather: "clear" },
      ...[-20, -44, -68, -92, -116].flatMap((z, i) => [["oak", -18], ["spruce", 0], ["birch", 18]].map(([sp, x]) =>
        T(sp, "mature", x, z, i ? { from: [x, -20] } : {})))] },
  { id: "n05", group: "P16 SPECIES", title: "OAK, BIRCH, SPRUCE, JUNGLE CLOSE UP",
    body: lines("Four of our trees NORTH: OAK old, BIRCH mature, SPRUCE mature, JUNGLE mature. Walk around each, stand under each.\n" +
      "Look for: the approved pilot look on every species; biome colour right for this biome; spruce has no cards-only leaves.\n" +
      "SHOTS: each tree once.\n" + PASSN),
    setup: [NEAR, { leafclear: { box: [-45, 45, -24, -2], h: 30 } }, { daytime: "noon" },
      T("oak", "old", -30, -13), T("birch", "mature", -10, -13), T("spruce", "mature", 10, -13), T("jungle", "mature", 30, -13)] },
  { id: "n06", group: "P16 SPECIES", title: "ACACIA, MANGROVE, DARK OAK, PALE OAK + THE NEW AZALEA LEAVES",
    body: lines("Four trees NORTH: ACACIA, MANGROVE, DARK OAK elder, PALE OAK elder. To the SOUTH-WEST of you, 2 blocks away: a cube of our new AZALEA leaves and one of FLOWERING AZALEA leaves around oak logs (they stay until you break them).\n" +
      "Look for: each species right; azalea + flowering azalea in their own colours (flowers visible).\nSHOTS: each tree + the two azalea cubes.\n" + PASSN),
    setup: [NEAR, { leafclear: { box: [-50, 50, -32, -2], h: 36 } }, { daytime: "noon" },
      { leaftree: { sp: "acacia", dx: -36, dz: -14, keep: true } }, { leaftree: { sp: "mangrove", dx: -14, dz: -14, keep: true } },
      T("dark_oak", "elder", 8, -18), T("pale_oak", "elder", 36, -18),
      { cmd: ["fill ~-6 ~ ~2 ~-4 ~2 ~4 pw:azalea_leaves", "fill ~-5 ~ ~3 ~-5 ~2 ~3 oak_log", "fill ~-10 ~ ~2 ~-8 ~2 ~4 pw:flowering_azalea_leaves", "fill ~-9 ~ ~3 ~-9 ~2 ~3 oak_log"] }] },
  { id: "n07", group: "P16 FELLING", title: "FELLING (SURVIVAL): CHOP THE OAK",
    body: lines("You are now in SURVIVAL with an iron axe. An OAK grows 12 blocks NORTH.\nChop its BOTTOM log. The tree falls (BIGCANOPY).\n" +
      "Look for: the falling canopy in the oak's leaf colour (not grey, not black); the standing leaves cleared after the fall; drops.\n" +
      "SHOT or VIDEO of the fall.\n" + PASSN),
    setup: [NEAR, { leafclear: { box: [-12, 12, -24, -2], h: 30 } }, { daytime: "noon" }, T("oak", "mature", 0, -14),
      { cmd: ["gamemode survival @s"] }, { give: [["iron_axe", 1]] }] },
  { id: "n08", group: "P16 DECAY", title: "DECAY: A TREE WITHOUT ITS WOOD",
    body: lines("Back in CREATIVE. An OAK grows 12 blocks NORTH, then the runner removes its wood: its leaves now hang in the air.\n" +
      "Wait about 30-60 seconds near it. Look for: the leaves decaying a few at a time and dropping leaf litter.\n" + PASSN),
    setup: [{ cmd: ["gamemode creative @s"] }, NEAR, { leafclear: { box: [-12, 12, -24, -2], h: 30 } }, { daytime: "noon" }, T("oak", "mature", 0, -14, { chop: true })] },
  { id: "n09", group: "P16 BY HAND", title: "BREAK AND PLACE LEAVES BY HAND (SURVIVAL)",
    body: lines("SURVIVAL again, with shears and leaf blocks. A BIRCH grows 10 blocks NORTH.\n" +
      "1) Break a few leaves with your HAND (sometimes a sapling or stick drops). 2) Break a few with SHEARS (the leaf item drops). " +
      "3) PLACE some of the given oak / azalea leaves: each placed leaf gets its look at once.\n" + PASSN),
    setup: [NEAR, { leafclear: { box: [-12, 12, -22, -2], h: 30 } }, { daytime: "noon" }, T("birch", "mature", 0, -12),
      { cmd: ["gamemode survival @s"] }, { give: [["shears", 1], ["pw:oak_leaves", 16], ["pw:azalea_leaves", 16]] }] },
  { id: "n10", group: "P16 TURNS", title: "RANDOM PICTURE TURNS: LOOK CLOSELY (PS5)",
    body: lines("Back in CREATIVE. An OAK and a SPRUCE 8 blocks NORTH. Every leaf now has random picture turns ON (his 18:14).\n" +
      "Walk up close. Look for: no repeating stripes or tiles across neighbouring leaves; nothing looking broken or misaligned.\n" + PASSN),
    setup: [{ cmd: ["gamemode creative @s"] }, NEAR, { leafclear: { box: [-22, 22, -20, -2], h: 30 } }, { daytime: "noon" },
      T("oak", "old", -9, -10), T("spruce", "old", 9, -10)] },
  { id: "n11", group: "P16 FOREST", title: "A FOREST: WALK + RUN THROUGH IT (FRAME RATE)",
    body: lines("Twelve of our trees in a grove NORTH. Walk through, then run through.\nLook for: smooth frame rate (note any stutter while the scanner gives leaves their looks).\n" + PASSN),
    setup: [NEAR, { leafclear: { box: [-37, 37, -60, -2], h: 30 } }, { daytime: "noon" },
      ...[-27, -9, 9, 27].flatMap((dx, i) => [-14, -32, -50].map((dz, j) => T(["oak", "birch", "spruce", "jungle"][(i + j) % 4], ["young", "mature", "old"][(i + 2 * j) % 3], dx, dz, { noclear: true })))] },
  { id: "n12", group: "P16 PROBE", title: "THE /PLACE PROBE (WHY p15 USED STAND-INS)",
    body: lines("Nothing to judge by eye: the runner grows 6 trees two ways (script API in the near row, the /place command in the far row) on grass or dirt and writes each result into the content log.\n" +
      "Wait 10 seconds, then copy the content log (or type /scriptevent pw:test report p16).\nPASS = done (the log decides)."),
    setup: [PROBE_AREA, { leafclear: { box: [-56, 56, -46, -2], h: 30 } }, { daytime: "noon" },
      { placeprobe: { apiZ: -14, cmdZ: -36, cases: [
        { feature: "pw:oak_mature_tree_feature", ground: "grass_block", dx: -45 }, { feature: "pw:oak_mature_tree_feature", ground: "dirt", dx: -27 },
        { feature: "minecraft:oak_tree_feature", ground: "grass_block", dx: -9 }, { feature: "minecraft:azalea_tree_feature", ground: "grass_block", dx: 9 },
        { feature: "minecraft:cherry_tree_feature", ground: "grass_block", dx: 27 }, { feature: "pw:spruce_old_tree_feature", ground: "dirt", dx: 45 }] } }] },
];
// v0.5.2 (his 19:33 / 19:41 CT 09-30): THE 128 vs 256 LEAF COMPARISON — 10 trees, all 11 leaf species (azalea covers flowering azalea).
// Each step: ONE tree grown (the WEST one, 128 = our real leaves) and two exact copies (/clone) EAST of it; every leaf in all three gets
// the same look in the same spot (the BP-02 look rule hashed at the west tree), so only the textures differ:
// WEST 128 (RP-01 1.3.106) | MIDDLE 256 colour + 128 normal + 128 MERS (pw:t256_*) | EAST 256 colour + 128 normal + 64 MERS (pw:t256m_*).
const TRIO_ROW = { young: 8, mature: 8, old: 8, elder: 13, acacia: 8, mangrove: 8, cherry: 9, azalea: 5 };
function trio(sp, age) {
  const r = TRIO_ROW[age || sp]; const gap = 2 * r + 6; const dz = -(r + 4);
  const xs = [-gap, 0, gap];
  const t = (dx, extra) => ({ leaftree: { sp, ...(age ? { age } : {}), dx, dz, look: true, ...extra } });
  return [NEAR, { leafclear: { box: [-gap - r - 1, gap + r + 1, dz - r - 1, -2], h: age === "elder" ? 38 : 30 } }, { daytime: "noon" }, { weather: "clear" },
    t(xs[0], { block: "pw:{sp}_leaves", label: "128" }),
    t(xs[1], { from: [xs[0], dz], block: "pw:t256_{sp}_leaves", label: "256" }),
    t(xs[2], { from: [xs[0], dz], block: "pw:t256m_{sp}_leaves", label: "256+MERS64" })];
}
const TRIO_LOOK = "Look for, at THREE distances (2-4 blocks, about 15 blocks, about 40 blocks): sharpness and detail, colour, " +
  "any shimmer / sparkle when you move (fine detail can flicker far away). In Vibrant Visuals: the light through the leaves (backlit, " +
  "facing the sun) and their shine. EAST has the lower-detail MERS map, so watch for any difference from the MIDDLE.";
const TRIO_ANS = "PASS + your pick: 'up close 128/256/256M, far 128/256/256M' (and anything off). FAIL + note = a broken or missing tree.";
const TRIOS = [
  ["m01", "oak", "old", "OAK (OLD)"], ["m02", "birch", "old", "BIRCH (OLD)"], ["m03", "spruce", "old", "SPRUCE (OLD)"],
  ["m04", "jungle", "old", "JUNGLE (OLD)"], ["m05", "dark_oak", "elder", "DARK OAK (ELDER)"], ["m06", "pale_oak", "elder", "PALE OAK (ELDER)"],
  ["m07", "acacia", undefined, "ACACIA"], ["m08", "mangrove", undefined, "MANGROVE"], ["m09", "cherry", undefined, "CHERRY"],
  ["m10", "azalea", undefined, "AZALEA + FLOWERING AZALEA"],
];
const MSTEPS = TRIOS.map(([id, sp, age, name], i) => ({ id, group: "P16 128 vs 256", title: `128 vs 256: ${name}`,
  body: lines(`Three COPIES of the same ${name.toLowerCase()} tree NORTH, WEST to EAST: 128 (our leaves today) | 256 | 256 + MERS 64. ` +
    "Every leaf has the same look in the same spot - only the texture differs.\n" +
    (sp === "azalea" ? "The azalea tree carries BOTH leaf kinds: plain azalea and flowering azalea.\n" : "") +
    (i === 0 ? "Stand where you can see all three, then walk up to each. Keep the same spot for the far looks so they are fair.\n" : "") +
    TRIO_LOOK + "\nSHOTS: all three from about 15 blocks; then one close-up per tree if you see a difference.\n" + TRIO_ANS),
  setup: trio(sp, age) }));
STEPS16.push(...MSTEPS);
STEPS16.push({ id: "n13", group: "P16 OLD TREES", title: "OLD TREES: LEAVES SAVED BEFORE THE UPDATE",
  body: lines("Fly to a part of this world copy with trees that grew BEFORE the update (any old forest). Stand still near them for about a minute.\n" +
    "Look for: their leaves switching ONCE to the new look (cards beside the wood, full elsewhere) as the relook sweep reaches them - and then never again. " +
    "Also: a far-away old forest should look leafy, not boxy.\nSHOTS: before (if you catch it) and after.\n" + PASSN),
  setup: [{ daytime: "noon" }] });
const Q9 = { id: "q9", group: "P16 DONE", title: "P16: ALL CLEAR - UPLOAD",
  body: lines("Every tree this run grew is cleared (wherever you stand), the three ticking areas are removed, CREATIVE is restored. Give it 15 seconds.\n" +
    "Upload any shots and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or /scriptevent pw:test report p16.\nPASS = uploaded (or about to)."),
  setup: [{ cmd: ["gamemode creative @s"] }, { leafreset: { areas: ["pw_pilot_far", "pw_pilot_near", "pw_probe_area"], box: [-56, 56, -128, -2], h: 40 } }, { daytime: "noon" }] };

export const P16_STEPS = [Q0, ...STEPS16, Q9];
export const P16_INDEX = Object.fromEntries(P16_STEPS.map((s, i) => [s.id, i]));
