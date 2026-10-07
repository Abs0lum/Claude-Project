// pw_testrunner_p9.js — lineup "p9" (PW-TestRunner BP v0.4.0, D-C292: the SIZE ROUND — his 19:52 law "the scale I want is compared to
// REAL LIFE ... we're scaling against real life measurements"; BP-02 1.3.190 resizes 18 vanilla animals (model AND hitbox), RP-06 1.4.19
// draws the warden 20 % bigger (hitbox unchanged), StripMine BP 1.3.4 moves the Naturalist creatures onto the same curve (Realm only).
// /scriptevent pw:test start p9    a size parade: each resized animal in a pen, and YOU (5'10") are the yardstick beside it
// Needs: BP-02 v1.3.190, RP-06 v1.4.19 active; the Naturalist steps (w09-w13) only work where PW-StripMine BP 1.3.4 is loaded (the Realm).
const CLEAR = ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"];
const SHOT_S = "SHOT 1 SIDE-ON: stand right next to the pen wall, level with the animals, and look at them side-on (walk to the EAST side, look WEST) - you are the 5'10\" ruler.";
const SHOT_F = "SHOT 2 FRONT: from the south, eye level.";
const PASS_M = "PASS = the sizes look real-life right next to you. FAIL + note = which one looks too big or too small (and roughly how much).";

// chat lines stay <= 190 characters: the text breaks between sentences (and after ': ' / ' - ' when one sentence is longer)
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
function rigStep(id, group, title, look, rig, shots, pass) {
  return { id, group, title, body: lines(`${look}\n${shots || `${SHOT_S}\n${SHOT_F}`}\n${pass || PASS_M}`), setup: [{ cmd: CLEAR }, { rig }] };
}
const REALM = "REALM ONLY: these are Naturalist creatures (PW-StripMine BP 1.3.4). In a world without it the pen stays empty and the log says so - then just SKIP.\n";

const STEPS9 = [
  rigStep("z01", "P9 FARM", "COW · MOOSHROOM · LLAMA (BIGGER)",
    "LEFT to RIGHT: MOOSHROOM, COW, LLAMA - all three were drawn smaller than the real animals. Now: cow and mooshroom x1.28 (a real cow is ~2.1 m long, 2.2 blocks here), llama x1.21. Their HITBOX grew too (your 'visual + hitbox').\n" +
    "Look for: real-cow size next to you (your head at about the cow's shoulder height + a bit).",
    { mob: "minecraft:cow", label: "cow", half: 6, halfz: 3, row: [{ mob: "minecraft:mooshroom", dx: -3, label: "mooshroom" }, { mob: "minecraft:llama", dx: 3, label: "llama" }] }),
  rigStep("z02", "P9 FARM", "HORSE · MULE · CAMEL (BIGGER)",
    "LEFT to RIGHT: MULE, HORSE, CAMEL. Horse x1.10 (2.4 m -> 2.5 blocks), mule x1.15, camel x1.15 (3 m -> 3.2 blocks). Hitboxes grew with them.\n" +
    "Look for: a horse you would really have to climb onto; the camel towering.",
    { mob: "minecraft:horse", label: "horse", half: 7, halfz: 3, height: 5, row: [{ mob: "minecraft:mule", dx: -3, label: "mule" }, { mob: "minecraft:camel", dx: 4, label: "camel" }] }),
  rigStep("z03", "P9 FARM", "SKELETON HORSE · ZOMBIE HORSE · TRADER LLAMA",
    "LEFT to RIGHT: ZOMBIE HORSE, SKELETON HORSE, TRADER LLAMA - the same real-life sizes as the horse (x1.21) and the llama (x1.21).",
    { mob: "minecraft:skeleton_horse", label: "skeleton horse", half: 6, halfz: 3, height: 5, row: [{ mob: "minecraft:zombie_horse", dx: -3, label: "zombie horse" }, { mob: "minecraft:trader_llama", dx: 3, label: "trader llama" }] }),
  rigStep("z04", "P9 SMALLER", "GOAT · ARMADILLO · PANDA (SMALLER)",
    "LEFT to RIGHT: ARMADILLO, GOAT, PANDA - all three were drawn bigger than the real animals. Goat x0.70 (1.2 m), armadillo x0.60 (40 cm), panda x0.68 (a giant panda is ~1.5 m long).\n" +
    "Look for: a goat about waist-high on you; a panda smaller than a cow.",
    { mob: "minecraft:goat", label: "goat", half: 6, halfz: 3, row: [{ mob: "minecraft:armadillo", dx: -2, label: "armadillo" }, { mob: "minecraft:panda", dx: 3, label: "panda" }] }),
  rigStep("z05", "P9 SMALLER", "POLAR BEAR (A LITTLE SMALLER) + WOLF (REFERENCE)",
    "LEFT: a WOLF (unchanged - your R8 calibration, the reference). CENTRE: the POLAR BEAR x0.88 (2.1 m long).\n" +
    "Look for: the bear still big and heavy, just not over-size.",
    { mob: "minecraft:polar_bear", label: "polar bear", half: 6, halfz: 3, row: [{ mob: "minecraft:wolf", dx: -3, label: "wolf (reference)" }] }),
  rigStep("z06", "P9 WATER", "DOLPHIN · TURTLE · SALMON",
    "In the pool, LEFT to RIGHT: TURTLE (x0.63 - a green sea turtle is ~1.4 m flipper to flipper), DOLPHIN (x1.11 - 2.5 m), SALMON (x0.52 - it was 1.5 blocks long for a 75 cm fish; the small / large salmon scale with it).\n" +
    "Look for: the dolphin clearly longer than you are tall; the salmon about a forearm and a half.",
    { mob: "minecraft:dolphin", label: "dolphin", water: true, depth: 3, half: 6, halfz: 3, free: false, row: [{ mob: "minecraft:turtle", dx: -3, label: "turtle" }, { mob: "minecraft:salmon", dx: 3, label: "salmon" }] },
    "SHOT 1 SIDE-ON: stand at the pool edge and look along it.\nSHOT 2 TOP: look down into the pool."),
  rigStep("z07", "P9 WATER", "COD · TROPICAL FISH (+ PUFFERFISH REFERENCE)",
    "In the pool, LEFT to RIGHT: TROPICAL FISH (x0.77 - the old curve missed vanilla's own x1.3 on tropical fish), COD (x0.91 - 80 cm), PUFFERFISH (unchanged, the reference).",
    { mob: "minecraft:cod", label: "cod", water: true, depth: 2, half: 5, halfz: 2, row: [{ mob: "minecraft:tropicalfish", dx: -2, label: "tropical fish" }, { mob: "minecraft:pufferfish", dx: 2, label: "pufferfish (reference)" }] },
    "SHOT 1 SIDE-ON at the pool edge.\nSHOT 2 TOP: look down into the pool."),
  rigStep("z08", "P9 FANTASY", "THE WARDEN, 20 % BIGGER",
    "The WARDEN in a tall roofed pen: drawn 20 % bigger (about 3.9 blocks), his hitbox is the ORIGINAL size (your ruling) - so he should look like he cannot possibly fit through places he walks through.\n" +
    "Look for: bigger and scarier; no floating or sinking into the floor; the content log shows no warden animation error.",
    { mob: "minecraft:warden", label: "warden", roof: true, height: 6, half: 4, halfz: 3 },
    "SHOT 1 FRONT: from the south, stand close and look UP at him.\nSHOT 2 SIDE: from the east, looking west.",
    "PASS = he looks right and scary. FAIL + note = what is off (size, floating, clipping, log error)."),
  rigStep("w09", "P9 REALM", "GRIZZLY · BLACK BEAR · BOAR (BIGGER)",
    REALM + "LEFT to RIGHT: BLACK BEAR (x1.12), GRIZZLY (x1.24 - 2.2 m), BOAR (x1.67 - a wild boar is ~1.6 m long).",
    { mob: "sf_nba:grizzly_bear", label: "grizzly", half: 7, halfz: 3, row: [{ mob: "sf_nba:black_bear", dx: -3, label: "black bear" }, { mob: "sf_nba:boar", dx: 4, label: "boar" }] }),
  rigStep("w10", "P9 REALM", "DEER · TORTOISE",
    REALM + "LEFT: the TORTOISE (x1.48 - a giant tortoise, ~1.2 m). CENTRE: the DEER (unchanged - it was already right once its antlers were counted; the reference).",
    { mob: "sf_nba:deer", label: "deer (reference)", half: 6, halfz: 3, row: [{ mob: "sf_nba:tortoise", dx: -3, label: "tortoise" }] }),
  rigStep("w11", "P9 REALM", "THE SMALL ONES: HAMSTER · BEETLE · FIREFLY · FINCH",
    REALM + "LEFT to RIGHT: BEETLE (x1.60), HAMSTER (x2.09), FIREFLY (x1.78), FINCH (x1.30). Small creatures sit on the visibility ramp: bigger in life stays bigger in game, and none too tiny to see.",
    { mob: "sf_nba:hamster", label: "hamster", half: 6, halfz: 2, row: [{ mob: "sf_nba:beetle", dx: -2, label: "beetle" }, { mob: "sf_nba:firefly", dx: 2, label: "firefly" }, { mob: "sf_nba:finch", dx: 4, label: "finch" }] },
    "SHOT 1 SIDE-ON: crouch at the pen wall, level with them.\nSHOT 2 TOP: look down on all four."),
  rigStep("w12", "P9 REALM", "SCORPIONS + RATTLESNAKE (TRUE SIZE)",
    REALM + "LEFT to RIGHT: DESERT SCORPION (x0.41 - 14 cm), JUNGLE SCORPION (x0.21 - an emperor scorpion, 20 cm), RATTLESNAKE (x0.72 - 1.2 m). Your ruling: these follow real life (only the sharks stay imposing).",
    { mob: "sf_nba:jungle_scorpion", label: "jungle scorpion", half: 6, halfz: 2, row: [{ mob: "sf_nba:desert_scorpion", dx: -2, label: "desert scorpion" }, { mob: "sf_nba:rattlesnake", dx: 3, label: "rattlesnake" }] }),
  rigStep("w13", "P9 REALM", "MORAYS + ELECTRIC EEL (TRUE SIZE)",
    REALM + "In the pool, LEFT to RIGHT: SPOTTED MORAY (x0.29 - ~1 m), MORAY (x0.44 - 1.5 m), ELECTRIC EEL (x0.59 - 2 m).",
    { mob: "sf_nba:moray", label: "moray", water: true, depth: 2, half: 6, halfz: 3, row: [{ mob: "sf_nba:spotted_moray", dx: -3, label: "spotted moray" }, { mob: "sf_nba:electric_eel", dx: 3, label: "electric eel" }] },
    "SHOT 1 SIDE-ON at the pool edge.\nSHOT 2 TOP: look down into the pool."),
];

const Q0 = { id: "q0", group: "P9 SETUP", title: "P9: VERSIONS, CREATIVE, EASY, FLAT, FACE NORTH",
  body: lines("Check the packs first: Settings > Global Resources > My Packs - RP-06 must say v1.4.19 in its description; in the world's Behavior Packs BP-02 must say v1.3.190 (the Realm: PW-StripMine BP v1.3.4); this runner says v0.4.0 in the chat banner.\n" +
        "After the world loads, glance at the content log: no 'format_version' or entity errors for cow / horse / panda / dolphin / polar bear (they use Mojang's newest file format).\n" +
        "Creative mode, Difficulty EASY, an open FLAT spot with nothing for 14 blocks NORTH and 9 to each side, daylight, HUD position ON. Every mob is grown up by the runner and its age is logged.\n" +
        "PASS = versions right, log clean, you are set up. FAIL + note = a version is different or the log shows an error (copy it)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P9 DONE", title: "P9: ALL CLEAR - UPLOAD THE SHOTS",
  body: lines("The pens are removed. The whale (15.8 blocks now) is too big for a pen: if you meet one in the ocean, a screenshot next to it is welcome.\n" +
        "Upload the screenshots and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p9 and copy that.\nPASS = uploaded (or about to)."),
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P9_STEPS = [Q0, ...STEPS9, Q9];
export const P9_INDEX = Object.fromEntries(P9_STEPS.map((s, i) => [s.id, i]));
export const P9_MOBS = P9_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
