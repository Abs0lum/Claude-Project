// pw_testrunner_p6.js — lineup "p6" (PW-TestRunner BP v0.3.7, D-C285: the R8 fixes of RP-07 1.4.23 + RP-06 1.4.16;
// his 09-29 03:03 "from now on, everything I need to test or witness, I want done via a scriptevent in testrunner").
// /scriptevent pw:test start p6    every change of this round, one pen at a time (10 steps)
// Needs: RP-07 v1.4.23, RP-06 v1.4.16, RP-08 v1.4.8 active (the first step says how to check), Creative, Difficulty EASY, flat ground.
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

const STEPS6 = [
  rigStep("c01", "P6 FIXES", "SILVERFISH: VISIBLE AGAIN",
    "A silverfish FREE in the pen. Your 'invisible, but I can see his shadow' was real: it still used the game's own silverfish render controller, which hides every part except the vanilla model's part names - and the Patrix model has none of them, so everything was hidden. It now has its own controller.\n" +
    "Look for: the whole Patrix silverfish (segments, legs, antennae), no black slabs; it crawls with its tail wave.",
    { mob: "minecraft:silverfish", label: "silverfish (free)", free: true },
    "A short VIDEO while it crawls (or SHOT 1 close from above, SHOT 2 side-on, low).",
    "PASS = visible and right. FAIL + note."),
  rigStep("c02", "P6 FIXES", "SQUID A/B: THE TILT RUNS NOW",
    "A SQUID and a GLOW SQUID FREE in the tank. Last round the game threw the tilt animation away (the content log said so), so neither could tip. It runs now.\n" +
    "One of them tips one way, the other the opposite way - only one is right. Look for: which one leads with its HEAD end when it swims?",
    { mob: "minecraft:squid", label: "squid + glow squid (free)", water: true, free: true, half: 4, depth: 3, height: 4,
      row: [{ mob: "minecraft:glow_squid", dx: 2, label: "glow squid" }] },
    "A VIDEO while they swim is best.",
    "PASS + note = SQUID or GLOW SQUID is the right one (the other gets fixed to match). FAIL + note = neither tips / something else."),
  rigStep("c03", "P6 FIXES", "ENDERMAN: THE PATRIX JAW",
    "An enderman made ANGRY by the runner, held in the roofed pen. The Patrix jaw never actually ran before (the game refused the way it was attached - the log said so). It is attached the way this enderman's file accepts now.\n" +
    "Look for: when angry, the lower jaw drops open and the head shifts a little; judge it fresh - it may look different from last time.",
    { mob: "minecraft:enderman", label: "enderman (angry)", roof: true, height: 4, event: "minecraft:become_angry" },
    "SHOT 1: close, eye level, from the front (Creative is safe). A short VIDEO is welcome.",
    "PASS = the jaw looks right. FAIL + note."),
  rigStep("c04", "P6 FIXES", "TADPOLE: UPRIGHT IN THE WATER",
    "A tadpole held in the pool. It was the WHOLE tadpole on its side (head and tail rolled 70 degrees): Patrix makes a tadpole flop over when it is OUT of water, and the converter had built its resting pose from that dry-land setting. Rebuilt in the in-water pose.\n" +
    "Look for: body level, tail fin standing upright (thin from above, full from the side), wagging.",
    { mob: "minecraft:tadpole", label: "tadpole", water: true },
    "SHOT 1: side-on from the pool edge, at water level. SHOT 2: from above.",
    "PASS = upright. FAIL + note."),
  rigStep("c05", "P6 FIXES", "PUFFERFISH: SPIKES GROW FROM THE BODY",
    "A pufferfish held in the pool. The big and middle puffed-up forms were old conversions: each spike strip was mirrored, so its roots sat on the far edge and the strips floated beside the body. Both are rebuilt from the Patrix models.\n" +
    "Look for: stand at the pool edge close to it so it PUFFS UP - the spikes should grow straight out of every edge of the body, no gap.",
    { mob: "minecraft:pufferfish", label: "pufferfish", water: true },
    "SHOT 1: puffed up, from above and in front. SHOT 2: puffed up, side-on.",
    "PASS = spikes attached. FAIL + note."),
  rigStep("c06", "P6 FIXES", "SKELETON + WITHER SKELETON: WEAPON IN THE HAND",
    "A SKELETON (middle) and a WITHER SKELETON (right) in the roofed pen. The longbow sat below the hand: our skeleton's hold point was at its fingertips, 3 px lower than where the game's own skeleton holds things. Both now hold at the game's point.\n" +
    "Look for: the bow grip (and the wither skeleton's sword handle) inside the hand.",
    { mob: "minecraft:skeleton", label: "skeleton + wither skeleton", roof: true, height: 4, half: 5, halfz: 2,
      row: [{ mob: "minecraft:wither_skeleton", dx: 3, label: "wither skeleton" }] },
    "SHOT 1: both, close, eye level from the front. SHOT 2: the skeleton's bow hand, close.",
    "PASS = in the hand. FAIL + note = where it sits now."),
  rigStep("c07", "P6 CHECKS", "HELD ITEMS: WHO HOLDS WHAT",
    "INFORMATION STEP. Seven mobs in the roofed pen, each handed an item by the runner, LEFT to RIGHT: PILLAGER crossbow, STRAY bow, BOGGED bow, ZOMBIE iron sword, HUSK iron shovel, DROWNED trident, PIGLIN golden sword. The pillager is the control (its model has a hold point); the other six models have NONE.\n" +
    "Look for: on each, is the item in its hand, somewhere wrong (feet, floating), or missing? (The piglin starts shaking after a while in the Overworld - that is normal.)",
    { mob: "minecraft:zombie", label: "held-items row", roof: true, height: 4, half: 8, halfz: 2, item: "iron_sword",
      row: [{ mob: "minecraft:pillager", dx: -6, label: "pillager", item: "crossbow" }, { mob: "minecraft:stray", dx: -4, label: "stray", item: "bow" },
            { mob: "minecraft:bogged", dx: -2, label: "bogged", item: "bow" }, { mob: "minecraft:husk", dx: 2, label: "husk", item: "iron_shovel" },
            { mob: "minecraft:drowned", dx: 4, label: "drowned", item: "trident" }, { mob: "minecraft:piglin", dx: 6, label: "piglin", item: "golden_sword" }] },
    "SHOT 1: all seven from the front, eye level. SHOT 2-3: closer, left half and right half.",
    "PASS + note = which ones show the item right / wrong / not at all."),
  rigStep("c08", "P6 SIZES", "SIZES: FOX, WOLF, SHEEP AGAIN",
    "FOX (left), WOLF (middle), SHEEP (right). As you asked: the wolf is 10 % bigger, the sheep 8 % smaller than last time; the fox is unchanged (it passed).\n" +
    "Look for: next to you, they look like a real fox, wolf and sheep would.",
    { mob: "minecraft:wolf", label: "fox + wolf + sheep", half: 5, halfz: 2,
      row: [{ mob: "minecraft:fox", dx: -3, label: "fox" }, { mob: "minecraft:sheep", dx: 3, label: "sheep" }] },
    "SHOT 1: all three side-on from the south, eye level. SHOT 2: you standing beside them (F5).",
    "PASS = the sizes feel right. FAIL + note = which one is too big / too small."),
];

const Q0 = { id: "q0", group: "P6 SETUP", title: "P6: VERSIONS, CREATIVE, EASY, FLAT, FACE NORTH",
  body: lines("Check the packs first: Settings > Global Resources > My Packs - RP-07 must say v1.4.23, RP-06 v1.4.16 and RP-08 (Items) v1.4.8 in their descriptions; this runner says v0.3.7 in the chat banner.\n" +
        "Creative mode, Difficulty EASY, an open FLAT spot with nothing for 14 blocks NORTH and 9 to each side, daylight, HUD position ON.\n" +
        "Each step pens its own mob(s) 5 blocks north and clears them as it goes. Videos are welcome where a step asks. Jump to a step: /scriptevent pw:test goto c05\n" +
        "PASS = versions right and you are set up. FAIL + note = a version is different (say which)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P6 DONE", title: "P6: ALL CLEAR - UPLOAD THE SHOTS",
  body: "The pens and pools are removed.\nUpload the screenshots/videos and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p6 and copy that.\nPASS = uploaded (or about to).",
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P6_STEPS = [Q0, ...STEPS6, Q9];
export const P6_INDEX = Object.fromEntries(P6_STEPS.map((s, i) => [s.id, i]));
export const P6_MOBS = P6_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
