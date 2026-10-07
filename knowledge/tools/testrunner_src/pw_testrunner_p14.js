// pw_testrunner_p14.js — lineup "p14" (PW-TestRunner BP v0.4.5, D-C317 / D-C318: R17 — RP-06 1.4.24 + RP-07 1.4.31 + BP-02
// 1.3.195). /scriptevent pw:test start p14
// Needs: RP-06 v1.4.24, RP-07 v1.4.31, BP-02 v1.3.195 active. RUN IT IN A COPY of the test world (BP-02 changed the leaf blocks).
// Lesson from p13 (his 10:19 "the animations I didn't see ... simply weren't performed"): every behaviour step PROVOKES the
// behaviour (a target to chase, a roof for a daytime nap, taming instructions) and a mob that must be seen moving is FREE.
const CLEAR = ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"];
const WATCH = "SHOT 1 SIDE-ON: from the EAST side, level with it, looking WEST.\nSHOT 2 FRONT: from the south, eye level. A short VIDEO is even better.";
const PASS_M = "PASS = it looks right to you. FAIL + note = what is off.";
const PROOF = "The content log PROVES whether it holds the item: 'RIG item ... CONFIRMED in ...' or 'RIG item ... NOT in ...'.";

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
  return { id, group, title, body: lines(`${look}\n${shots || WATCH}\n${pass || PASS_M}`), setup: [{ cmd: CLEAR }, ...(extra || []), { rig }] };
}

const STEPS14 = [
  rigStep("i01", "P14 IRON GOLEM", "IRON GOLEM · THE WALK (HIP FIX)",
    "An IRON GOLEM loose in a big pen. Its whole motion script now runs (in p13 it stopped at line 70, so the legs only swung from the ground).\n" +
    "Look for: each leg swinging from the HIP, feet lifting and planting, the heavy side-to-side sway. The content log should show NO 'unknown variable' lines.",
    { mob: "minecraft:iron_golem", label: "iron golem", half: 7, halfz: 5, free: true, height: 5 }, null,
    "PASS = legs swing from the hips. FAIL + note."),
  rigStep("i02", "P14 IRON GOLEM", "IRON GOLEM · THE ATTACK (EASY)",
    "The IRON GOLEM loose, a ZOMBIE held beside it. Difficulty EASY.\nLook for: both arms swinging up to strike, the body leaning in, the legs still from the hips.",
    { mob: "minecraft:iron_golem", label: "iron golem", half: 7, halfz: 5, free: true, height: 5, row: [{ mob: "minecraft:zombie", dx: 4, label: "zombie" }] },
    "VIDEO from the south, or SHOT at the moment it strikes.", "PASS = the strike looks right. FAIL + note."),
  rigStep("v01", "P14 VEX PROBE", "VEX PROBE A · THE SWORD (MOJANG'S ARM NAMES)",
    "The VEX with an iron sword. PROBE A: this build gives its arms Mojang's own bone names (rightArm / leftArm) - the one difference from p12.\n" + PROOF + "\nLook for: the SWORD in its hand.",
    { mob: "minecraft:vex", label: "vex", item: "iron_sword", roof: true, height: 5, fly: true },
    "SHOT: from the south, close. Copy the RIG item line from the content log.", "PASS = the sword shows. FAIL + note = still no sword."),
  rigStep("v02", "P14 VEX PROBE", "VEX PROBE B · THE SHARD (HUNG ON THE BODY)",
    "The VEX with an amethyst shard. PROBE B: the hand points hang on its BODY, like the allay (which draws its items).\n" + PROOF + "\nLook for: a purple SHARD near its hand.",
    { mob: "minecraft:vex", label: "vex", item: "amethyst_shard", roof: true, height: 5, fly: true },
    "SHOT: from the south, close. Copy the RIG item line.", "PASS = the shard shows (even if it does not follow the arm). FAIL + note = still nothing."),
  rigStep("f01", "P14 FOX", "FOX · THE POUNCE (WHOLE-BODY TILT)",
    "NOON. A FOX loose, a CHICKEN held beside it (foxes hunt chickens).\nLook for: the crouch, then the leap - the WHOLE fox tilts nose-up as it jumps and nose-down as it drops (Java's pounce). A plain hop does not tilt.",
    { mob: "minecraft:fox", label: "fox", half: 6, halfz: 4, free: true, row: [{ mob: "minecraft:chicken", dx: 4, label: "chicken" }] },
    "VIDEO from the EAST side is best (the tilt is a side view).", "PASS = the body tilts into the pounce. FAIL + note (or 'it never pounced').", [{ daytime: "noon" }]),
  rigStep("f02", "P14 FOX", "FOX · AN ITEM IN ITS MOUTH",
    "A FOX holding SWEET BERRIES (in p13 an egg floated over its head).\n" + PROOF + "\nLook for: the berries IN ITS MOUTH at the tip of the snout, moving with the head.",
    { mob: "minecraft:fox", label: "fox", item: "sweet_berries", half: 4 },
    "SHOT 1 SIDE-ON from the east. SHOT 2 FRONT from the south, close.", "PASS = the item sits in the mouth. FAIL + note = where it is instead.", [{ daytime: "noon" }]),
  rigStep("f03", "P14 FOX", "FOX · SIT AND NAP (UNDER A ROOF)",
    "NOON, a ROOFED pen: foxes nap by day in the shade. A FOX loose.\nLook for: it SITS down now and then - the sit should SETTLE in over a quarter second (new; p13's was instant) - and it may curl up ASLEEP. Give it 1-2 minutes.",
    { mob: "minecraft:fox", label: "fox", half: 5, halfz: 4, free: true, roof: true, height: 4 }, null,
    "PASS = the sit settles smoothly (say if you saw it sleep). FAIL + note.", [{ daytime: "noon" }]),
  rigStep("d01", "P14 COD", "COD · SWIMMING FREE (VIEW FROM ABOVE)",
    "A COD loose in a big 3-deep pool (in p13 it was held still, so it could not swim).\nLook for, FROM ABOVE: the body bending side to side along its length as it swims, the tail sweeping, the fins paddling.",
    { mob: "minecraft:cod", label: "cod", water: true, depth: 3, half: 6, halfz: 5, free: true },
    "SHOT or VIDEO: from ABOVE, looking straight down into the pool.", "PASS = it swims with a side-to-side body wave. FAIL + note."),
  rigStep("c01", "P14 CAT", "CAT · CHASING (SNEAK AND SPRINT)",
    "A CAT loose, a RABBIT held beside it (cats hunt rabbits).\nLook for: the low SNEAK as it stalks, then the stretched SPRINT when it runs at the rabbit.",
    { mob: "minecraft:cat", label: "cat", half: 6, halfz: 4, free: true, row: [{ mob: "minecraft:rabbit", dx: 4, label: "rabbit" }] }, null,
    "PASS = sneak and / or sprint look like a cat (say which you saw). FAIL + note (or 'it never chased')."),
  rigStep("c02", "P14 CAT", "CAT · TAME IT, THEN SIT",
    "A CAT loose. TAME it: type /give @s cod 16, walk into the pen, hold the RAW COD and tap the cat until hearts show. Then tap it with an empty hand: it SITS.\n" +
    "Look for: the sit pose (tail curled round). Optional: sleep in a bed at night with the tame cat nearby - it lies on the bed on its side.",
    { mob: "minecraft:cat", label: "cat", half: 5, halfz: 4, free: true }, "SHOT: the sitting cat from the side (east) and front (south).",
    "PASS = the sit looks right. FAIL + note (or 'could not tame it')."),
  { id: "t01", group: "P14 LEAVES", title: "LEAVES · AFTER THE FULL STATE CUT",
    body: lines("A 3x3x3 block of fresh OAK LEAVES (log in the middle) east of the pen, and a chicken as a size mark. BP-02 1.3.195 removed the leaves' four side flags: every leaf now shows ALL its corner fill-ins.\n" +
      "Look for: the fresh leaves turn shaped within a few seconds; leaves with open air to their NORTH or SOUTH show small fill-ins sticking out a few pixels there (expected). Then walk to an OLDER tree: its leaves should still look right.\n" +
      "SHOT 1 the new leaf block from the north side. SHOT 2 an older tree.\nPASS = leaves look right. FAIL + note = what is off (and copy any leaf lines from the content log)."),
    setup: [{ cmd: CLEAR }, { daytime: "noon" },
      { rig: { mob: "minecraft:chicken", label: "chicken (scale)", half: 5, halfz: 4,
               boxes: [{ id: "pw:oak_leaves", from: [2, 0, -1], to: [4, 2, 1] }, { id: "minecraft:oak_log", from: [3, 0, 0], to: [3, 2, 0] }] } }] },
];

const Q0 = { id: "q0", group: "P14 SETUP", title: "P14: A COPY OF THE TEST WORLD, VERSIONS, FLAT, FACE NORTH",
  body: lines("Packs: RP-06 v1.4.24, RP-07 v1.4.31, BP-02 v1.3.195; this runner says v0.4.5 in the chat banner. Use a COPY of your test world (BP-02 changed the leaf blocks again).\n" +
        "Creative, EASY, a flat open spot, 14 blocks clear NORTH and 9 to each side.\n" +
        "PASS = versions right. FAIL + note = what differs (copy the line)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P14 DONE", title: "P14: ALL CLEAR - UPLOAD THE SHOTS",
  body: lines("The pens are removed.\n" +
        "Upload the screenshots / videos and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p14 and copy that.\nPASS = uploaded (or about to)."),
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P14_STEPS = [Q0, ...STEPS14, Q9];
export const P14_INDEX = Object.fromEntries(P14_STEPS.map((s, i) => [s.id, i]));
export const P14_MOBS = P14_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
