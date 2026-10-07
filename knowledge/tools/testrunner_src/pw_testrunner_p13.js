// pw_testrunner_p13.js — lineup "p13" (PW-TestRunner BP v0.4.4, D-C314: R16b — RP-06 1.4.23 + RP-07 1.4.29, the Patrix
// fidelity ports). /scriptevent pw:test start p13
// Needs: RP-06 v1.4.23, RP-07 v1.4.29 active (with the R16a packs: BP-02 v1.3.194). The copy of the test world from p12 is fine.
const CLEAR = ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"];
const WATCH = "SHOT 1 SIDE-ON: from the EAST side, level with it, looking WEST.\nSHOT 2 FRONT: from the south, eye level. A short VIDEO is even better.";
const PASS_M = "PASS = it moves like a living animal and no part comes loose. FAIL + note = what looks wrong.";

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
const NEW = "It now moves with the Patrix model's OWN animation (FreshLX's), not the borrowed walk.";

const STEPS13 = [
  rigStep("f01", "P13 FOX", "FOX · WALK, SIT, SLEEP (NOON)",
    "NOON. A FOX loose in the pen. " + NEW + "\nLook for: the walk and trot; ears flicking; it may SIT (tail curled round) or, by day, CURL UP ASLEEP on its side (legs tucked away). Give it a minute.",
    { mob: "minecraft:fox", label: "fox", half: 5, halfz: 4, free: true }, null,
    "PASS = walk / sit / sleep look right (say which you saw). FAIL + note.", [{ daytime: "noon" }]),
  rigStep("f02", "P13 FOX", "FOX · STALKING A CHICKEN",
    "A FOX loose, a CHICKEN held beside it (foxes hunt chickens).\nLook for: the fox CROUCHING low with its rear up and tail raised before it pounces.",
    { mob: "minecraft:fox", label: "fox", half: 6, halfz: 4, free: true, row: [{ mob: "minecraft:chicken", dx: 4, label: "chicken" }] }, null,
    "PASS = the crouch / pounce looks right (or it never stalked: say so). FAIL + note.", [{ daytime: "noon" }]),
  rigStep("c01", "P13 CATS", "CAT · WALK, SNEAK, SPRINT, SIT",
    "A CAT loose in the pen. " + NEW + "\nLook for: the walk, the low SNEAK, the stretched SPRINT, the tail. Optional: tame it (raw cod) and right-click it to make it SIT.",
    { mob: "minecraft:cat", label: "cat", half: 5, halfz: 4, free: true }, null,
    "PASS = it moves like a cat. FAIL + note. (Lying down on a bed with you asleep is also ported - try it if you have a bed.)"),
  rigStep("o01", "P13 CATS", "OCELOT · ITS OWN MODEL NOW",
    "An OCELOT loose in the pen - it has its own Patrix model now (it shared the cat's before).\nLook for: the walk and sprint; the spotted coat sits right on the new model.",
    { mob: "minecraft:ocelot", label: "ocelot", half: 5, halfz: 4, free: true }),
  rigStep("g01", "P13 GOAT", "GOAT · WALK, JUMP, RAM, NIBBLE",
    "A GOAT loose in the pen. " + NEW + "\nLook for: the walk, the JUMPS (legs tucked), the head going down for a RAM, and now and then a NIBBLE at the ground.",
    { mob: "minecraft:goat", label: "goat", half: 6, halfz: 4, free: true, height: 4 }, null,
    "PASS = it moves like a goat. FAIL + note. Question for you: goats nibble even on stone (Bedrock cannot tell grass from stone here) - keep or drop the nibble?"),
  rigStep("d01", "P13 COD", "COD · SWIMMING",
    "A COD in a 3-deep pool. " + NEW + "\nLook for: the body waving along its length, fins paddling, a slow bob.",
    { mob: "minecraft:cod", label: "cod", water: true, depth: 3, half: 4, halfz: 3 },
    "SHOT 1 at the pool edge. SHOT 2 TOP: look down into the pool."),
  rigStep("d02", "P13 COD", "COD · FLOPPING ON LAND",
    "A COD on dry ground in the pen.\nLook for: it FLOPS on its side like the Java fish (not standing upright, not upside down).",
    { mob: "minecraft:cod", label: "cod (on land)", half: 3, free: true },
    "SHOT: from the south, close.", "PASS = it flops on its side. FAIL + note."),
  rigStep("i01", "P13 IRON GOLEM", "IRON GOLEM · THE WALK",
    "An IRON GOLEM loose in a big pen. " + NEW + "\nLook for: the heavy sway from side to side as it walks, the head scanning, the arms swinging; its cracks (if hurt) drawn on the new model.",
    { mob: "minecraft:iron_golem", label: "iron golem", half: 7, halfz: 5, free: true, height: 5 }, null,
    "PASS = it moves like a heavy golem. FAIL + note."),
  rigStep("i02", "P13 IRON GOLEM", "IRON GOLEM · THE ATTACK (EASY)",
    "The IRON GOLEM loose, a ZOMBIE held beside it. Difficulty EASY.\nLook for: both arms swinging up to strike, the body leaning into it.",
    { mob: "minecraft:iron_golem", label: "iron golem", half: 7, halfz: 5, free: true, height: 5, row: [{ mob: "minecraft:zombie", dx: 4, label: "zombie" }] },
    "VIDEO from the south, or SHOT at the moment it strikes.", "PASS = the strike looks right. FAIL + note."),
  rigStep("h01", "P13 HOGLIN", "HOGLIN + ZOGLIN · WALK AND CHARGE",
    "A HOGLIN loose, a ZOGLIN held beside it (the zoglin attacks it). " + NEW + "\nLook for: the walk and trot, the head sniffing low, the ears, and the upward HEAD-TOSS of the attack.",
    { mob: "minecraft:hoglin", label: "hoglin", half: 7, halfz: 5, free: true, row: [{ mob: "minecraft:zoglin", dx: -4, label: "zoglin" }] },
    "VIDEO from the south, or two SHOTS.", "PASS = both move right. FAIL + note (which one)."),
];

const Q0 = { id: "q0", group: "P13 SETUP", title: "P13: VERSIONS, FLAT, FACE NORTH",
  body: lines("Packs: RP-06 v1.4.23, RP-07 v1.4.29 (and the R16a BP-02 v1.3.194); this runner says v0.4.4 in the chat banner. The p12 copy of your test world is fine.\n" +
        "Creative, EASY, a flat open spot, 14 blocks clear NORTH and 9 to each side.\n" +
        "Baby foxes, cats, goats and hoglins stay the adult pose made smaller, as before.\n" +
        "PASS = versions right. FAIL + note = what differs (copy the line)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P13 DONE", title: "P13: ALL CLEAR - UPLOAD THE SHOTS",
  body: lines("The pens are removed.\n" +
        "Upload the screenshots / videos and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p13 and copy that.\nPASS = uploaded (or about to)."),
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P13_STEPS = [Q0, ...STEPS13, Q9];
export const P13_INDEX = Object.fromEntries(P13_STEPS.map((s, i) => [s.id, i]));
export const P13_MOBS = P13_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
