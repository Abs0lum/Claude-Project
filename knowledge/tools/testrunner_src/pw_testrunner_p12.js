// pw_testrunner_p12.js — lineup "p12" (PW-TestRunner BP v0.4.3, D-C310 / D-C312: R16a — RP-06 1.4.22 + RP-07 1.4.28 +
// BP-02 1.3.194). /scriptevent pw:test start p12
// Needs: RP-06 v1.4.22, RP-07 v1.4.28, BP-02 v1.3.194 active. RUN IT IN A COPY of the test world (BP-02 changed the leaf blocks).
const CLEAR = ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"];
const SHOT_S = "SHOT 1 SIDE-ON: from the EAST side of the pen, level with them, looking WEST.";
const SHOT_F = "SHOT 2 FRONT: from the south, eye level.";
const PASS_M = "PASS = it looks right to you. FAIL + note = what is off.";

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
function rigStep(id, group, title, look, rig, shots, pass, extra) {
  return { id, group, title, body: lines(`${look}\n${shots || `${SHOT_S}\n${SHOT_F}`}\n${pass || PASS_M}`), setup: [{ cmd: CLEAR }, ...(extra || []), { rig }] };
}
const PROOF = "The content log now PROVES whether it holds it: 'RIG item ... CONFIRMED in ...' or 'RIG item ... NOT in ...'.";

const STEPS12 = [
  rigStep("h01", "P12 HANDS", "VEX · THE SWORD (ENGINE VERSION FIX)",
    "The VEX with an iron sword. It was the only item-holding mob still on Minecraft's old 1.8.0 entity version - now 1.21.0, like every mob that draws its item. Its items are drawn at Mojang's 70 % size.\n" + PROOF + "\n" +
    "Look for: the SWORD in its right hand.",
    { mob: "minecraft:vex", label: "vex", item: "iron_sword", roof: true, height: 5, fly: true },
    "SHOT: from the south, close. If there is still no sword, copy the RIG item line from the content log.", "PASS = the sword shows. FAIL + note = no sword (and what the RIG item line says)."),
  rigStep("h02", "P12 HANDS", "VEX · AN AMETHYST SHARD",
    "The same vex with an amethyst shard.\n" + PROOF + "\nLook for: a purple shard in its hand.",
    { mob: "minecraft:vex", label: "vex", item: "amethyst_shard", roof: true, height: 5, fly: true },
    "SHOT: from the south, close.", "PASS = the shard shows. FAIL + note."),
  rigStep("h03", "P12 HANDS", "ALLAY · THE SWORD AT 70 %",
    "The ALLAY with an iron sword - now at Mojang's 70 % held-item size (it was bigger than the allay).\n" +
    "Look for: a sword that suits the allay's size, held in front of it.",
    { mob: "minecraft:allay", label: "allay", item: "iron_sword", roof: true, height: 5, fly: true },
    "SHOT: from the south, close.", "PASS = the size looks right. FAIL + note = still too big / too small."),
  rigStep("l01", "P12 LIGHT", "BLAZE AT MIDNIGHT · REAL LIGHT",
    "MIDNIGHT. The BLAZE now lights up what is around it (an invisible light block rides with it, level 13).\n" +
    "Look for: the pen floor and walls lit orange-warm around the blaze; the light moving with it.",
    { mob: "minecraft:blaze", label: "blaze", roof: true, height: 5, half: 4, fly: true },
    "SHOT 1 from the south with the floor in view. SHOT 2 from the east.", "PASS = it lights its surroundings. FAIL + note = no light / too strong / stuck behind.", [{ daytime: 18000 }]),
  rigStep("l02", "P12 LIGHT", "MAGMA CUBE AT MIDNIGHT · REAL LIGHT",
    "Still midnight. A MAGMA CUBE, lighting its cell (level 10).\n" +
    "Look for: the ground lit around it as it hops.",
    { mob: "minecraft:magma_cube", label: "magma cube", half: 4, halfz: 3, free: true },
    "SHOT: from the south, the floor in view.", "PASS = it glows on its surroundings. FAIL + note.", [{ daytime: 18000 }]),
  rigStep("l03", "P12 LIGHT", "GLOW SQUID AT MIDNIGHT · SOFT LIGHT",
    "Still midnight. A GLOW SQUID in the pool - a soft light (level 6) that swims with it. The light only sits in still water and the water comes back when it moves on.\n" +
    "Look for: a soft glow on the pool floor near the squid; no holes or odd blocks left in the water.",
    { mob: "minecraft:glow_squid", label: "glow squid", water: true, depth: 3, half: 6, halfz: 4 },
    "SHOT 1 at the pool edge. SHOT 2 TOP: look down into the pool.", "PASS = a soft glow, the water intact. FAIL + note.", [{ daytime: 18000 }]),
  rigStep("w01", "P12 WINGS", "PARROT FLYING · THE WING JOINT",
    "NOON. The PARROT flying in a tall roofed pen. Its outer feather block now sits ON the inner wing (Patrix's small gap closed) and turns only at the joint (your pick A).\n" +
    "Look for: no gap opening between the inner wing block and the outer feathers, all through the flap.",
    { mob: "minecraft:parrot", label: "parrot", roof: true, height: 5, half: 4, free: true },
    "VIDEO or SHOT from below-front while it flaps.", "PASS = the wing stays joined. FAIL + note = where it opens.", [{ daytime: "noon" }]),
  rigStep("w02", "P12 WINGS", "PHANTOM AT DUSK · THE WING TIPS",
    "DUSK (the runner sets it). The PHANTOM in a tall roofed pen. Its wing tips now turn only at the joint with the inner wing (your pick A).\n" +
    "Look for: the tips flapping with no gap at the joint; the tips no longer swinging sideways like doors.",
    { mob: "minecraft:phantom", label: "phantom", roof: true, height: 5, half: 5, free: true },
    "VIDEO or SHOT from below while it flies.", "PASS = the tips stay joined. FAIL + note.", [{ daytime: 13000 }]),
  rigStep("t01", "P12 LEAVES", "LEAVES AFTER THE STATE CUT",
    "NOON. A 3x3x3 block of our OAK LEAVES around an oak-log core, to the RIGHT of the chicken (seen from the south). BP-02 1.3.194 dropped the unused 'far' state (block states 64,700 -> 40,500). The side flags that show the leaf fringe toward air are KEPT.\n" +
    "Look for: the leaves re-rolling into their variants within a few seconds; the fringe only on the OUTSIDE faces; no missing or pink blocks. If your copy has older trees, look at them too.",
    { mob: "minecraft:chicken", label: "chicken (scale)", half: 5, halfz: 4,
      boxes: [{ id: "pw:oak_leaves", from: [2, 0, -1], to: [4, 2, 1] }, { id: "minecraft:oak_log", from: [3, 0, 0], to: [3, 2, 0] }] },
    "SHOT 1 from the south, close. SHOT 2 of an older tree if there is one.", "PASS = leaves look right. FAIL + note.",
    [{ daytime: "noon" }]),
];

const Q0 = { id: "q0", group: "P12 SETUP", title: "P12: A COPY OF THE TEST WORLD, VERSIONS, FLAT, FACE NORTH",
  body: lines("FIRST make a COPY of your test world (World list > edit > Copy World) and run p12 in the copy - BP-02 changed the leaf blocks.\n" +
        "Packs: RP-06 v1.4.22, RP-07 v1.4.28, BP-02 v1.3.194; this runner says v0.4.3 in the chat banner.\n" +
        "Content log after load: '[PW-MOBLIGHT] active ...' and '[PW-MOBLIGHT] boot ...' lines; the 'over 65536 block permutations' warning should be GONE.\n" +
        "Creative, EASY, a flat open spot, 14 blocks clear NORTH and 9 to each side.\n" +
        "PASS = versions right, log as described. FAIL + note = what differs (copy the line)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P12 DONE", title: "P12: ALL CLEAR - UPLOAD THE SHOTS",
  body: lines("The pens are removed.\n" +
        "Upload the screenshots / videos and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p12 and copy that.\nPASS = uploaded (or about to)."),
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P12_STEPS = [Q0, ...STEPS12, Q9];
export const P12_INDEX = Object.fromEntries(P12_STEPS.map((s, i) => [s.id, i]));
export const P12_MOBS = P12_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
