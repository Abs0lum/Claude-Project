// pw_testrunner_p8.js — lineup "p8" (PW-TestRunner BP v0.3.9, D-C288: the R10 fixes of RP-06 1.4.18 + RP-07 1.4.25 — attachables switched on;
// his 09-29 03:03 "from now on, everything I need to test or witness, I want done via a scriptevent in testrunner").
// /scriptevent pw:test start p8    every change of this round, one pen at a time (5 steps)
// Needs: RP-06 v1.4.18, RP-07 v1.4.25, RP-08 v1.4.8 active (the first step says how to check), Creative, Difficulty EASY, flat ground.
const CLEAR = ["fill ~-9 ~ ~-14 ~9 ~5 ~-2 air"];
const SHOT_F = "SHOT 1 FRONT: as you stand (south of it), eye level, look NORTH.";
const SHOT_L = "SHOT 2 LEFT FLANK: walk round to the EAST side and look WEST.";
const PASS_M = "PASS = the point named above is right. FAIL + note = say what you see.";

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
  return { id, group, title, body: lines(`${look}\n${shots || `${SHOT_F}\n${SHOT_L}`}\n${pass || PASS_M}`),
           setup: [{ cmd: CLEAR }, ...(extra || []), { rig }] };
}

const STEPS8 = [
  rigStep("e01", "P8 FIXES", "BOGGED: THE BOW, FOR REAL",
    "A SKELETON (left, the reference) and the BOGGED (right), each handed a bow by the runner, in the roofed pen. You were right: the bogged never held its bow. The game only draws a bow on a mob whose model has 'attachables' switched on, and our bogged had that switch off - so the hand point I added last round was never used. Fixed.\n" +
    "Look for: the bogged holds its bow in its right hand, the same way the skeleton does.",
    { mob: "minecraft:bogged", label: "bogged", roof: true, height: 4, half: 5, halfz: 2, item: "bow",
      row: [{ mob: "minecraft:skeleton", dx: -3, label: "skeleton", item: "bow" }] },
    "SHOT 1 FRONT: as you stand (south of them), eye level, close.\nSHOT 2 SIDE: walk round to the EAST side and look WEST (from the front a bow is thin, edge-on).",
    "PASS = the bogged holds the bow in its hand. FAIL + note = what you see."),
  rigStep("e02", "P8 FIXES", "PIGLIN CROSSBOW + TWO PROBES",
    "Three mobs, LEFT to RIGHT: PIGLIN BRUTE handed a CROSSBOW (a probe - it normally carries an axe), PIGLIN with a CROSSBOW (its real ranged weapon), WITHER SKELETON handed a BOW (a probe - it normally carries a sword). All three had the same switch off, so a crossbow or bow in their hands was never drawn. Swords and axes are plain items, which is why they always showed.\n" +
    "Look for: each one holds its crossbow / bow in the hand.",
    { mob: "minecraft:piglin", label: "piglin", roof: true, height: 4, half: 5, halfz: 2, item: "crossbow",
      row: [{ mob: "minecraft:piglin_brute", dx: -3, label: "piglin brute", item: "crossbow" }, { mob: "minecraft:wither_skeleton", dx: 3, label: "wither skeleton", item: "bow" }] },
    "SHOT 1: all three from the front, eye level, close.",
    "PASS = all three hold it in the hand. FAIL + note = which one."),
  rigStep("e03", "P8 CHECKS", "WOLF ARMOR + ZOMBIFIED PIGLIN",
    "LEFT: a TAMED WOLF wearing WOLF ARMOR (the runner tames it and puts the armor on). RIGHT: a ZOMBIFIED PIGLIN handed a CROSSBOW (a probe). Both had the switch off, so the wolf's armor could never show. Mojang made that armor for the vanilla wolf's body and ours is the Patrix wolf, so it may sit wrong - that is exactly what I need to see.\n" +
    "Look for: is the armor on the wolf, and does it fit the body (or float, clip, sit sideways)? Does the zombified piglin hold the crossbow?",
    { mob: "minecraft:wolf", label: "wolf (tamed, armored)", roof: true, height: 4, half: 5, halfz: 2, event: "minecraft:on_tame", armor: "wolf_armor",
      row: [{ mob: "minecraft:zombie_pigman", dx: 3, label: "zombified piglin", item: "crossbow" }] },
    "SHOT 1 SIDE: walk round to the EAST side and look WEST (the wolf side-on).\nSHOT 2 FRONT: both, eye level.",
    "PASS = armor on and fitting + crossbow in the hand. FAIL + note = what is wrong (armor missing / floating / clipping, or no crossbow)."),
];

const Q0 = { id: "q0", group: "P8 SETUP", title: "P8: VERSIONS, CREATIVE, EASY, FLAT, FACE NORTH",
  body: lines("Check the packs first: Settings > Global Resources > My Packs - RP-06 must say v1.4.18 and RP-07 v1.4.25 in their descriptions (RP-08 stays v1.4.8); this runner says v0.3.9 in the chat banner.\n" +
        "Creative mode, Difficulty EASY, an open FLAT spot with nothing for 14 blocks NORTH and 9 to each side, daylight, HUD position ON.\n" +
        "Each step pens its own mob(s) 5 blocks north and clears them as it goes. Jump to a step: /scriptevent pw:test goto e03\n" +
        "PASS = versions right and you are set up. FAIL + note = a version is different (say which)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P8 DONE", title: "P8: ALL CLEAR - UPLOAD THE SHOTS",
  body: "The pens are removed.\nUpload the screenshots and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p8 and copy that.\nPASS = uploaded (or about to).",
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P8_STEPS = [Q0, ...STEPS8, Q9];
export const P8_INDEX = Object.fromEntries(P8_STEPS.map((s, i) => [s.id, i]));
export const P8_MOBS = P8_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
