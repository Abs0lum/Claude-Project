// pw_testrunner_p5.js — lineup "p5" (PW-TestRunner BP v0.3.6, D-C284: the R6 fixes of RP-07 1.4.22 (= 1.4.21 + the enderman wins its
// identifier) + RP-06 1.4.15 + RP-08 1.4.8; first shipped in v0.3.5;
// his 09-29 03:03 "from now on, everything I need to test or witness, I want done via a scriptevent in testrunner").
// /scriptevent pw:test start p5    every change of this round, one pen at a time (20 steps)
// Needs: RP-07 v1.4.22, RP-06 v1.4.15, RP-08 v1.4.8 active (the first step says how to check), Creative, Difficulty EASY, flat ground.
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

// ------------------------------------------------------------------------------------------------ models + skins
const MODELS = [
  rigStep("b01", "P5 MODELS", "CHICKENS: WARM + COLD REBUILT",
    "Three chickens: WARM on the LEFT, the WHITE temperate one in the MIDDLE, COLD on the RIGHT. Last round only the white one was right: the other two were still the old conversion.\n" +
    "Look for: all three built the SAME way as the white one - wings flat against the body, tail low at the back, legs under the body. They are also smaller now (see the size steps).",
    { mob: "minecraft:chicken", label: "chicken (temperate) + warm + cold", props: { "minecraft:climate_variant": "temperate" },
      row: [{ mob: "minecraft:chicken", dx: -2, label: "warm chicken", event: "minecraft:hatch_warm" }, { mob: "minecraft:chicken", dx: 2, label: "cold chicken", event: "minecraft:hatch_cold" }] },
    `${SHOT_F}\n${SHOT_L}`,
    "PASS = all three built like the white one. FAIL + note = which one and what is off."),
  rigStep("b02", "P5 MODELS", "SPIDER: NO SQUARE HOLES",
    "A spider held in the pen. Your 'exact squares with no texture' were real: the converter shrank the body boxes to 80 % but kept the texture layout of the full-size boxes, so 90 faces reached into see-through parts of the sheet. Fixed: 0 see-through faces left.\n" +
    "Look for: the abdomen, the thorax around the leg roots and the head are covered all over - no square gaps, no inside visible.",
    { mob: "minecraft:spider", label: "spider" },
    "SHOT 1: from above and BEHIND (stand on a block north of the pen and look SOUTH down at its back). SHOT 2: from its side, eye level.",
    "PASS = no holes anywhere. FAIL + note = where a hole still shows."),
  rigStep("b03", "P5 MODELS", "CAVE SPIDER: TELL ME WHAT YOU SEE",
    "INFORMATION STEP. A cave spider held in the pen. None of our packs has a cave spider model: the game draws its own model under the Patrix cave spider skin, which was painted for a different model (the silverfish had the same mismatch).\n" +
    "Look for: does it look right, or are parts black / missing / patchy? Your answer decides whether it gets a Patrix model next round.",
    { mob: "minecraft:cave_spider", label: "cave spider" },
    "SHOT 1: from above and a little in front. SHOT 2: side-on, eye level.",
    "PASS = it looks right. FAIL + note = what is wrong with it."),
  rigStep("b04", "P5 MODELS", "SILVERFISH: PATRIX MODEL + ITS OWN MOTION",
    "A silverfish FREE in the pen. It was the vanilla model under the Patrix skin (the black slabs you saw). Now it is the Patrix model - jointed head, 5-segment tail, 6 legs, antennae - with the Patrix animation ported to Bedrock (tail wave, leg steps, antenna twitch, look).\n" +
    "Look for: no black slabs; the segments wave and the legs step as it crawls.",
    { mob: "minecraft:silverfish", label: "silverfish (free)", free: true },
    "A short VIDEO while it crawls (or SHOT 1 close from above, SHOT 2 side-on, low).",
    "PASS = right model and it moves well. FAIL + note."),
  rigStep("b05", "P5 MODELS", "ENDERMAN: PATRIX SKIN + MODEL",
    "An enderman held in the roofed pen. You were right to ask last round: the pack carried a plain old enderman skin that won over the Patrix one. It is gone, and the enderman is now the Patrix model with the same movement you liked.\n" +
    "Look for: the detailed Patrix skin; the face is painted on (no separate eyeballs now).",
    { mob: "minecraft:enderman", label: "enderman", roof: true, height: 4 },
    "SHOT 1 FRONT (do not look at its eyes in Survival - Creative is safe). SHOT 2 LEFT FLANK.",
    "PASS = Patrix skin and model. FAIL + note."),
  rigStep("b06", "P5 MODELS", "ENDERMAN: ANGRY JAW",
    "The same enderman, made ANGRY by the runner (minecraft:become_angry). The Patrix jaw is ported: when angry its mouth opens.\n" +
    "Look for: the lower jaw drops open; when it calms down (Repeat setup gives a calm one again after a while) the jaw closes.",
    { mob: "minecraft:enderman", label: "enderman (angry)", roof: true, height: 4, event: "minecraft:become_angry" },
    "SHOT 1: close, eye level, from the front.",
    "PASS = the jaw opens. FAIL + note = what happens instead."),
  rigStep("b07", "P5 MODELS", "EVOKER: PATRIX MODEL, ARMS CROSSED, CASTING",
    "An EVOKER held in the roofed pen, a VILLAGER held on the right. The game drew the vanilla evoker: our file used a name the game does not use. It is fixed, so the evoker is now the Patrix model with crossed arms.\n" +
    "Look for: the Patrix evoker, arms crossed. If it starts CASTING at the villager (arms up, spell particles from the hands) take a shot of that too. Nothing happens in 20 s? Just judge the idle look.",
    { mob: "minecraft:evocation_illager", label: "evoker + villager", roof: true, height: 4, half: 5, halfz: 2,
      row: [{ mob: "minecraft:villager_v2", dx: 3, label: "villager" }] },
    `${SHOT_F}\nSHOT 2: if it casts, the raised arms.`,
    "PASS = Patrix evoker (+ casting looks right if you saw it). FAIL + note.",
    [{ cmd: ["kill @e[type=vex,r=40]", "kill @e[type=evocation_fang,r=40]"] }]),
];

// ------------------------------------------------------------------------------------------------ log checks + the bow
const CHECKS = [
  rigStep("b08", "P5 CHECKS", "PILLAGER: NO LOG ERROR",
    "A pillager in the roofed pen. Last round the content log said it could not find anim_fall / anim_landing. Fixed; a new standing check now stops any build where an entity plays an animation that does not exist.\n" +
    "Look for: nothing new about the pillager in the content log (Settings > Creator > Content Log History).",
    { mob: "minecraft:pillager", label: "pillager", roof: true },
    "SHOT 1: the content log after 20 seconds.",
    "PASS = no pillager error. FAIL + note."),
  rigStep("b09", "P5 CHECKS", "SKELETON: THE LONGBOW, IDLE",
    "A skeleton in the roofed pen, and the runner put a BOW in your inventory. The realistic longbow only showed while drawing; the idle bow was the vanilla one. Now it shows idle too.\n" +
    "Look for: the skeleton holds the long realistic bow while standing; the bow in your hand and its inventory icon are the realistic one too.",
    { mob: "minecraft:skeleton", label: "skeleton", roof: true },
    "SHOT 1: the skeleton, close. SHOT 2: your hotbar + hand holding the bow.",
    "PASS = longbow idle everywhere. FAIL + note.",
    [{ cmd: ["give @s bow"] }]),
];

// ------------------------------------------------------------------------------------------------ motion + parts
const MOTION = [
  rigStep("b10", "P5 MOTION", "GUARDIAN: SPIKES COME OUT SMOOTHLY",
    "A guardian FREE in the 9 x 9 tank. Your 'out motion' (the spikes wobble as they come out after it stops) was real: its 'is it moving' reading flickered while it slowed down, so the spikes kept starting out and getting pulled back in.\n" +
    "Now it uses a steady moving signal and Java's exact speeds: in fast while it swims, out slowly (about 2 seconds) after it stops.\n" +
    "Look for: when it stops, the spikes glide OUT once, smoothly - no in-out wobble.",
    { mob: "minecraft:guardian", label: "guardian (free)", water: true, free: true, half: 4, depth: 3, height: 4 },
    "A VIDEO while it swims and stops is best.",
    "PASS = smooth, no wobble. FAIL + note."),
  rigStep("b11", "P5 MOTION", "DOLPHIN: FINS OUT",
    "A dolphin held in the pool. The April swim added a 120-degree twist that cancelled the Java flipper angle, so the fins lay flat on its sides. The twist is gone; the small flap stays.\n" +
    "Look for: the two side flippers angled OUT and DOWN like arms, flapping a little.",
    { mob: "minecraft:dolphin", label: "dolphin", water: true },
    `${SHOT_F}\nSHOT 2: from above and a little to the side.`,
    "PASS = flippers out. FAIL + note."),
  rigStep("b12", "P5 MOTION", "SQUID A/B: WHICH ONE LEANS THE RIGHT WAY?",
    "A SQUID and a GLOW SQUID FREE in the tank. In Java a swimming squid tips its body toward where it swims (the head end leads, the tentacles trail) and hangs upright when still. Ours never tipped.\n" +
    "One of them tips one way, the other the opposite way - only one is right. Look for: which one leads with its HEAD end when it swims sideways?",
    { mob: "minecraft:squid", label: "squid + glow squid (free)", water: true, free: true, half: 4, depth: 3, height: 4,
      row: [{ mob: "minecraft:glow_squid", dx: 2, label: "glow squid" }] },
    "A VIDEO while they swim is best.",
    "PASS + note = SQUID or GLOW SQUID is the right one (the other gets fixed to match). FAIL + note = neither tips."),
  rigStep("b13", "P5 MOTION", "RABBIT: HEAD ON THE BODY",
    "A rabbit held in the pen. Its head sat 2 px in front of where Java's rabbit head sits, leaving the gap you saw. The head (with ears and nose) moved back 2 px and up half a pixel.\n" +
    "Look for: the head against the front of the body, no gap. (It is also smaller now - see the size steps.)",
    { mob: "minecraft:rabbit", label: "rabbit" },
    `${SHOT_L}\nSHOT 2: low, side-on, at ground level.`,
    "PASS = no gap. FAIL + note."),
  rigStep("b14", "P5 MOTION", "MOOSHROOM PROBE: FOUR WAYS",
    "Four RED mooshrooms with name tags, LEFT to RIGHT: Moo A, Moo B, Moo C, Moo D. The tall, blocky, floating tier you saw is the game's OWN mushroom blocks (painted with the Patrix mushroom textures). Our model's mushrooms are the short ones on the back.\n" +
    "A = today's model (ours + the game's). B = ours removed, the game's alone, loose. C = ours removed, the game's alone, hung on a vanilla-style body bone. D = ours, with the game's hidden (if the game allows it).\n" +
    "Look for: which one looks right to you - and on each, where the mushrooms are (on the back / floating / none).",
    { mob: "minecraft:mooshroom", label: "Moo A-D", name: "Moo C", half: 8, halfz: 2,
      row: [{ mob: "minecraft:mooshroom", dx: -6, label: "Moo A", name: "Moo A" }, { mob: "minecraft:mooshroom", dx: -3, label: "Moo B", name: "Moo B" },
            { mob: "minecraft:mooshroom", dx: 3, label: "Moo D", name: "Moo D" }] },
    "SHOT 1: all four side-on, eye level, look NORTH. SHOT 2-5: each back from above, close.",
    "PASS + note = which letter is best (and anything odd). FAIL + note = none of them."),
];

// ------------------------------------------------------------------------------------------------ sizes (you are the 5'10" yardstick)
const SIZES = [
  rigStep("b15", "P5 SIZES", "SIZES 1: FOX, WOLF, SHEEP",
    "FOX (left), WOLF (middle), SHEEP (right), drawn at real-life proportion to your 5'10\" character. Fox about half the size it was, sheep 12 % smaller. The wolf is unchanged: at your height a grey wolf really is this size - it looked small because the fox and sheep were oversized.\n" +
    "Look for: next to you, they look like a real fox, wolf and sheep would. Step into the pen and stand beside them if it helps.",
    { mob: "minecraft:wolf", label: "fox + wolf + sheep", half: 5, halfz: 2,
      row: [{ mob: "minecraft:fox", dx: -3, label: "fox" }, { mob: "minecraft:sheep", dx: 3, label: "sheep" }] },
    "SHOT 1: all three side-on from the south, eye level. SHOT 2: you standing beside them (third person view, F5).",
    "PASS = the sizes feel right. FAIL + note = which one is too big / too small."),
  rigStep("b16", "P5 SIZES", "SIZES 2: CAT, OCELOT, RABBIT, CHICKEN",
    "CAT, OCELOT, RABBIT, CHICKEN, left to right, at real-life proportion to you: a house cat, a bigger wild ocelot, a rabbit and a hen all come up to about your knee or lower.\n" +
    "Look for: they look like the real animals next to you.",
    { mob: "minecraft:rabbit", label: "cat + ocelot + rabbit + chicken", half: 6, halfz: 2,
      row: [{ mob: "minecraft:cat", dx: -4, label: "cat" }, { mob: "minecraft:ocelot", dx: -2, label: "ocelot" }, { mob: "minecraft:chicken", dx: 2, label: "chicken" }] },
    "SHOT 1: all four side-on from the south, eye level. SHOT 2: you beside them (F5).",
    "PASS = the sizes feel right. FAIL + note."),
  rigStep("b17", "P5 SIZES", "SIZES 3: BEE AND FROG",
    "A BEE held in the air and a FROG on the right. The bee is about 30 % smaller again (a real bee is 1.5 cm - the smallest a mob gets is about a fifth of a block, so you can still see it). The frog is a little over half its old size.\n" +
    "Look for: small but visible.",
    { mob: "minecraft:bee", label: "bee + frog", fly: true, row: [{ mob: "minecraft:frog", dx: 2, label: "frog" }] },
    "SHOT 1: side-on, eye level, close.",
    "PASS = right. FAIL + note = bigger / smaller."),
  rigStep("b18", "P5 SIZES", "SIZES 4: IN THE WATER",
    "In the pool, left to right: TADPOLE, AXOLOTL, TROPICAL FISH, PUFFERFISH. The axolotl is now about the size the bee was, as you asked (a real one is about 9 inches). The tadpole and pufferfish are a little bigger, the tropical fish a little smaller.\n" +
    "Look for: sizes that feel right next to each other and to you.",
    { mob: "minecraft:axolotl", label: "tadpole + axolotl + tropical fish + pufferfish", water: true, half: 5, halfz: 2,
      row: [{ mob: "minecraft:tadpole", dx: -3, label: "tadpole" }, { mob: "minecraft:tropicalfish", dx: 2, label: "tropical fish" }, { mob: "minecraft:pufferfish", dx: 4, label: "pufferfish" }] },
    "SHOT 1: side-on from the pool edge, at water level.",
    "PASS = right. FAIL + note."),
];

const Q0 = { id: "q0", group: "P5 SETUP", title: "P5: VERSIONS, CREATIVE, EASY, FLAT, FACE NORTH",
  body: lines("Check the packs first: Settings > Global Resources > My Packs - RP-07 must say v1.4.22, RP-06 v1.4.15 and RP-08 (Items) v1.4.8 in their descriptions; this runner says v0.3.6 in the chat banner.\n" +
        "Creative mode, Difficulty EASY, an open FLAT spot with nothing for 14 blocks NORTH and 9 to each side, daylight, HUD position ON.\n" +
        "Each step pens its own mob(s) 5 blocks north and clears them as it goes. Videos are welcome where a step asks. Jump to a step: /scriptevent pw:test goto b10\n" +
        "PASS = versions right and you are set up. FAIL + note = a version is different (say which)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P5 DONE", title: "P5: ALL CLEAR - UPLOAD THE SHOTS",
  body: "The pens and pools are removed.\nUpload the screenshots/videos and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p5 and copy that.\nPASS = uploaded (or about to).",
  setup: [{ rigclear: true }, { cmd: CLEAR }, { cmd: ["kill @e[type=vex,r=60]"] }, { daytime: "noon" }] };

export const P5_STEPS = [Q0, ...MODELS, ...CHECKS, ...MOTION, ...SIZES, Q9];
export const P5_INDEX = Object.fromEntries(P5_STEPS.map((s, i) => [s.id, i]));
export const P5_MOBS = P5_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
