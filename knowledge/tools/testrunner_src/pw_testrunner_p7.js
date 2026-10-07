// pw_testrunner_p7.js — lineup "p7" (PW-TestRunner BP v0.3.8, D-C286: the R9 fixes of RP-07 1.4.24 + RP-06 1.4.17;
// his 09-29 03:03 "from now on, everything I need to test or witness, I want done via a scriptevent in testrunner").
// /scriptevent pw:test start p7    every change of this round, one pen at a time (5 steps)
// Needs: RP-07 v1.4.24, RP-06 v1.4.17, RP-08 v1.4.8 active (the first step says how to check), Creative, Difficulty EASY, flat ground.
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

const STEPS7 = [
  rigStep("d01", "P7 FIXES", "ENDERMAN: THE JAW OPENS",
    "An enderman made ANGRY by the runner, held in the roofed pen. You were right that there was a jaw: it is a second head-sized block sitting exactly on the head, so it only shows when it opens - and it never opened. Its frame-to-frame values were read before they were set, which the game refuses (the 10 log errors). Fixed.\n" +
    "Look for: the lower jaw drops open while it is angry (a small tremble), and the content log shows NO 'unknown variable' lines.",
    { mob: "minecraft:enderman", label: "enderman (angry)", roof: true, height: 4, event: "minecraft:become_angry" },
    "SHOT 1: close, eye level, from the front (Creative is safe). A short VIDEO is best.",
    "PASS = the jaw opens. FAIL + note."),
  rigStep("d02", "P7 FIXES", "BOWS: SKELETON, STRAY, BOGGED",
    "Three archers in the roofed pen, LEFT to RIGHT: SKELETON (passed last round - the reference), STRAY, BOGGED, each handed a bow by the runner. The bogged had no hand point, so its bow was not drawn at all; the stray's bow lay flat at the hip. Both now have the skeleton's hand point.\n" +
    "Look for: all three hold the bow the same way, in the hand.",
    { mob: "minecraft:stray", label: "skeleton + stray + bogged", roof: true, height: 4, half: 5, halfz: 2, item: "bow",
      row: [{ mob: "minecraft:skeleton", dx: -3, label: "skeleton", item: "bow" }, { mob: "minecraft:bogged", dx: 3, label: "bogged", item: "bow" }] },
    "SHOT 1: all three from the front, eye level, close.",
    "PASS = all three in the hand. FAIL + note = which one."),
  rigStep("d03", "P7 CHECKS", "SQUID A/B: A VIDEO OF THE TILT",
    "A SQUID and a GLOW SQUID FREE in the tank. Both tip now ('both turn sideways'). To fix them properly I need to see which way the body leans compared with the way it swims.\n" +
    "Look for: while one swims across the tank, does its pointed top lean INTO the direction it is going, AWAY from it, or out to the SIDE of its path?",
    { mob: "minecraft:squid", label: "squid + glow squid (free)", water: true, free: true, half: 4, depth: 3, height: 4,
      row: [{ mob: "minecraft:glow_squid", dx: 2, label: "glow squid" }] },
    "A VIDEO (10-20 s) while they swim across the tank, from the side, is what I need.",
    "PASS + note = what you see for the squid and for the glow squid (into / away / side)."),
];

const Q0 = { id: "q0", group: "P7 SETUP", title: "P7: VERSIONS, CREATIVE, EASY, FLAT, FACE NORTH",
  body: lines("Check the packs first: Settings > Global Resources > My Packs - RP-07 must say v1.4.24 and RP-06 v1.4.17 in their descriptions (RP-08 stays v1.4.8); this runner says v0.3.8 in the chat banner.\n" +
        "Creative mode, Difficulty EASY, an open FLAT spot with nothing for 14 blocks NORTH and 9 to each side, daylight, HUD position ON.\n" +
        "Each step pens its own mob(s) 5 blocks north and clears them as it goes. Jump to a step: /scriptevent pw:test goto d03\n" +
        "PASS = versions right and you are set up. FAIL + note = a version is different (say which)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P7 DONE", title: "P7: ALL CLEAR - UPLOAD THE SHOTS",
  body: "The pens and pools are removed.\nUpload the screenshots/videos and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p7 and copy that.\nPASS = uploaded (or about to).",
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P7_STEPS = [Q0, ...STEPS7, Q9];
export const P7_INDEX = Object.fromEntries(P7_STEPS.map((s, i) => [s.id, i]));
export const P7_MOBS = P7_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
