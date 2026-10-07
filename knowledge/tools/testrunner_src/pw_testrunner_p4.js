// pw_testrunner_p4.js — lineup "p4" (PW-TestRunner BP v0.3.4 — v0.3.3 + a01 shows the white chicken; first shipped in v0.3.3, D-C278: the R4 fixes; his 09-29 03:03 "from now on, everything I
// need to test or witness, I want done via a scriptevent in testrunner").
// /scriptevent pw:test start p4    every RP-07 1.4.20 + RP-06 1.4.13 change, one pen at a time (24 steps)
// Needs: RP-07 v1.4.20 and RP-06 v1.4.13 active (the first step says how to check), Creative, Difficulty EASY, flat ground.
const CLEAR = ["fill ~-6 ~ ~-12 ~6 ~5 ~-2 air"];
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
function rigStep(id, group, title, look, rig, shots, pass) {
  return { id, group, title, body: lines(`${look}\n${shots || `${SHOT_F}\n${SHOT_L}`}\n${pass || PASS_M}`), setup: [{ cmd: CLEAR }, { rig }] };
}

// ------------------------------------------------------------------------------------------------ top/bottom faces (converter fix)
const FACES = [
  rigStep("a01", "P4 FACES", "CHICKEN: FEET + WINGS/TAIL",
    "Three chickens (v0.3.4: the biome picked the dark COLD chicken every time): WARM on the LEFT, the WHITE temperate one in the MIDDLE, COLD on the RIGHT. Judge the WHITE one; if the middle one is not white, say so (the runner could not set it).\n" +
    "Every top and bottom face of the Patrix mobs was drawn turned round (a converter bug) - the toes pointed BACKWARDS. Look for: the three long toes point FORWARD (the way the beak points), the short one back.\n" +
    "Then the WINGS and TAIL: I could not find what is wrong with them - the game draws exactly the Patrix model. Tell me in the note what they should look like.",
    { mob: "minecraft:chicken", label: "chicken (temperate) + warm + cold", props: { "minecraft:climate_variant": "temperate" },
      row: [{ mob: "minecraft:chicken", dx: -2, label: "warm chicken", event: "minecraft:hatch_warm" }, { mob: "minecraft:chicken", dx: 2, label: "cold chicken", event: "minecraft:hatch_cold" }] },
    `SHOT 1 FEET: crouch close on its left side, look at the feet. ${SHOT_L}`,
    "PASS = toes forward (and wings/tail fine). FAIL + note = toes still backwards / what is wrong with the wings or tail."),
  rigStep("a02", "P4 FACES", "FROG: FEET",
    "A frog held in the pen. Look for: the flat webbed feet spread OUT and FORWARD from the legs (they splayed backwards/sideways).",
    { mob: "minecraft:frog", label: "frog" },
    "SHOT 1: from above and a little in front, close, looking down at the feet. SHOT 2: from its side, low.",
    "PASS = feet the right way. FAIL + note."),
  rigStep("a03", "P4 FACES", "PANDA: RUMP (SOUTH FACE)",
    "A panda held in the pen. The rump is the TOP face of the turned body box, so it was upside down.\n" +
    "Look for: from BEHIND, the dark shading of the rump is DOWN next to the black legs, lighter toward the top (it was dark at the top).",
    { mob: "minecraft:panda", label: "panda" },
    "SHOT 1 REAR: walk round to the NORTH side and look SOUTH at its rump, eye level.",
    "PASS = the rump the right way up. FAIL + note."),
  rigStep("a04", "P4 FACES", "TROPICAL FISH: BOTTOM FINS",
    "A tropical fish held in the pool (Repeat setup gives another random type). Look for: the two small BOTTOM fins sit ON the belly (they floated about 2 px below it).",
    { mob: "minecraft:tropicalfish", label: "tropical fish", water: true },
    "SHOT 1: side-on, close, at the fish's height (crouch at the pool edge).",
    "PASS = fins attached. FAIL + note."),
];

// ------------------------------------------------------------------------------------------------ spider
const SPIDER = [
  rigStep("a05", "P4 SPIDER", "SPIDER: TEXTURE",
    "A spider held in the pen. The pack carried two spider textures and the game used the OLD one (the flat white leg segments and abdomen strips you saw). The old one is gone.\n" +
    "Look for: dark brown-black HAIRY legs and body all over, red eyes - no flat white faces anywhere.",
    { mob: "minecraft:spider", label: "spider" }),
  rigStep("a06", "P4 SPIDER", "SPIDER: WALKING",
    "The spider FREE in the pen. Its legs now use the Patrix spider's own walk (the knees and ankles bend in turn).\n" +
    "Look for: while it walks, two to four feet are always UP off the ground and swinging forward, in turn around the body - not sliding flat.",
    { mob: "minecraft:spider", label: "spider (free)", free: true },
    "A short VIDEO while it walks is best (or SHOT 1 side-on, low, while it walks).",
    "PASS = the feet lift and step. FAIL + note."),
];

// ------------------------------------------------------------------------------------------------ guardians
const GUARD = [
  rigStep("a07", "P4 GUARDIANS", "GUARDIAN: RESTING (NO SHAKE)",
    "A guardian held in the pool. Two things made the spikes rough: Bedrock's own guardian shakes every spike 5-6 times a second all the time (Java does not, in water), " +
    "and the game's 'is it moving' flag flickers when a guardian hovers, so the spikes twitched in and out. Both are fixed.\n" +
    "Look for: the spikes stay OUT and STILL (only a very slow tiny breathing), the tail sways slowly.",
    { mob: "minecraft:guardian", label: "guardian", water: true },
    "A 10-second VIDEO close up is best (or SHOT 1 FRONT).",
    "PASS = spikes calm and smooth. FAIL + note = still shaking / twitching / other."),
  rigStep("a08", "P4 GUARDIANS", "GUARDIAN: SWIMMING (SMOOTH IN AND OUT)",
    "The guardian FREE in the 9 x 9 tank. Look for: while it swims the spikes GLIDE in; when it stops they GLIDE back out over about a second - smooth, no jumps.",
    { mob: "minecraft:guardian", label: "guardian (free)", water: true, free: true, half: 4, depth: 3, height: 4 },
    "A VIDEO while it swims and stops is best.",
    "PASS = smooth in and out. FAIL + note."),
];

// ------------------------------------------------------------------------------------------------ pose + parts
const POSE = [
  rigStep("a09", "P4 POSE", "RABBIT: BACK FEET + JAVA POSE",
    "A rabbit held in the pen. The Patrix rabbit leaves its body, legs and feet to Java's own rabbit pose; we had them at the wrong height, so the back feet floated 3 px.\n" +
    "Look for: the long BACK FEET flat on the ground; the body now sits like the Java rabbit - front end higher, rump lower - with the front legs slanting.",
    { mob: "minecraft:rabbit", label: "rabbit" },
    `${SHOT_L}\nSHOT 2: low, side-on, at ground level.`,
    "PASS = feet on the ground and the pose looks right. FAIL + note = feet / pose (say what)."),
  rigStep("a10", "P4 POSE", "DOLPHIN: FLIPPERS + STEERING",
    "A dolphin held in the pool. My read of your 'parts?': the side flippers lay flat along the belly. Java angles them out and down, 60/120 degrees, and now so do we.\n" +
    "The body now tips and turns toward where it looks, as in vanilla. Walk around the pool edge and it follows you.\n" +
    "Look for: two flippers angled OUT and DOWN like arms; the whole dolphin turning toward you.",
    { mob: "minecraft:dolphin", label: "dolphin", water: true },
    `${SHOT_F}\nSHOT 2: from above and a little to the side.`,
    "PASS = flippers right and it turns. FAIL + note = which part (and was this the 'parts?' you meant)."),
  rigStep("a11", "P4 POSE", "MOOSHROOM A/B: THE FLOATING MUSHROOMS",
    "Two mooshrooms: RED on the LEFT (middle of the pen), BROWN on the RIGHT. The blocky floating mushrooms are the GAME's own mushroom blocks. It hangs them on the bones named body/head, where the vanilla cow's would be.\n" +
    "RED: those bones renamed, so the game should have nowhere to hang them. BROWN: new anchor bones placed so the game's blocks should sit ON our back and head.\n" +
    "Look for: on each, are there blocky mushrooms, and where (floating / on the back / gone)? The fine Patrix mushrooms stay on both. The brown one now has the BROWN skin (a bug drew it red).",
    { mob: "minecraft:mooshroom", label: "red + brown mooshroom", half: 4, halfz: 2, row: [{ mob: "minecraft:mooshroom", dx: 3, label: "brown mooshroom", event: "minecraft:become_brown" }] },
    "SHOT 1: both side-on, eye level, look NORTH. SHOT 2 + 3: close on each back from above.",
    "PASS = tell me which one you prefer. FAIL + note = what each one shows."),
];

// ------------------------------------------------------------------------------------------------ sizes
const SIZES = [
  rigStep("a12", "P4 SIZES", "BEE: HALF SIZE",
    "A bee held in the air, and a CHICKEN on the right for scale. Look for: the bee at HALF the size you saw last round (about a third of a block long).",
    { mob: "minecraft:bee", label: "bee + chicken", fly: true, row: [{ mob: "minecraft:chicken", dx: 2, label: "chicken" }] },
    "SHOT 1: side-on, eye level, both in frame.",
    "PASS = size looks right. FAIL + note = bigger / smaller."),
  rigStep("a13", "P4 SIZES", "AXOLOTL: 0.8x",
    "An axolotl held in the pool. It was drawn 1.19x the vanilla size, now 0.8x of that (just under vanilla).",
    { mob: "minecraft:axolotl", label: "axolotl", water: true },
    "SHOT 1: side-on, close.",
    "PASS = size looks right. FAIL + note = bigger / smaller."),
];

// ------------------------------------------------------------------------------------------------ motion given back
const MOTION = [
  rigStep("a14", "P4 MOTION", "SQUID: TENTACLES PULSE",
    "A squid FREE in the tank. The pack had switched its tentacle motion off; it now uses the game's own tentacle stroke on the Patrix tentacles.\n" +
    "Look for: the 8 tentacles spread OUT and close in rhythm as it swims (the stroke).",
    { mob: "minecraft:squid", label: "squid (free)", water: true, free: true, half: 4, depth: 3, height: 4 },
    "A VIDEO while it swims is best.",
    "PASS = tentacles pulse. FAIL + note."),
  rigStep("a15", "P4 MOTION", "GLOW SQUID: TENTACLES PULSE",
    "A glow squid FREE in the tank. Same as the squid.",
    { mob: "minecraft:glow_squid", label: "glow squid (free)", water: true, free: true, half: 4, depth: 3, height: 4 },
    "A VIDEO while it swims is best.",
    "PASS = tentacles pulse. FAIL + note."),
  rigStep("a16", "P4 MOTION", "ENDERMAN: WALK + TEXTURE",
    "An enderman FREE in the roofed pen (if it teleports out, Repeat setup). Its walk and attack swings were switched off by the pack; they are back.\n" +
    "Look for: arms and legs swing as it walks. ALSO tell me what the SKIN looks like - plain low-res vanilla-like, or detailed with purple markings? The pack has both; I think the game uses the plain one.",
    { mob: "minecraft:enderman", label: "enderman (free)", free: true, roof: true, height: 4 },
    "SHOT 1 (or a video) while it walks. Do not look it in the eyes.",
    "PASS = limbs swing (+ note the skin). FAIL + note."),
  rigStep("a17", "P4 MOTION", "SILVERFISH: WIGGLE",
    "A silverfish FREE in the pen. Its only motion (the body wiggle) was switched off; it is back.\n" +
    "Look for: the body segments wave side to side as it crawls.",
    { mob: "minecraft:silverfish", label: "silverfish (free)", free: true },
    "A short VIDEO while it crawls.",
    "PASS = it wiggles. FAIL + note."),
  rigStep("a18", "P4 MOTION", "TADPOLE: TAIL WAG",
    "A tadpole held in the pool. Look for: the tail wags side to side (the game's own wag is back on top of our small wiggle).",
    { mob: "minecraft:tadpole", label: "tadpole", water: true },
    "SHOT 1 (or a short video): from above, close.",
    "PASS = tail wags. FAIL + note."),
  rigStep("a19", "P4 MOTION", "RAVAGER: NO LOG ERROR",
    "A ravager in the roofed pen. Last round the content log said 'can't find animation anim_nose' here (the ravager borrows the villager's nose controller). Walk left and right in front of it so it turns its head.\n" +
    "Look for: nothing new in the content log (Settings > Creator > Content Log History).",
    { mob: "minecraft:ravager", label: "ravager", roof: true },
    "SHOT 1: the content log after walking around it.",
    "PASS = no anim_nose error. FAIL + note."),
];

// ------------------------------------------------------------------------------------------------ regression (the face fix touched them)
const REGRESS = [
  rigStep("a20", "P4 REGRESSION", "CHECK: HORSE / COW / PIG FROM ABOVE",
    "The top/bottom-face fix touched every Patrix-converted mob, including ones you already passed. Three in a row: PIG (left), HORSE (middle), COW (right).\n" +
    "Look for: nothing looks WORSE than before on their backs and heads - fur flows the same way, no face or eye painted where it should not be.",
    { mob: "minecraft:horse", label: "pig + horse + cow", half: 5, halfz: 2, row: [{ mob: "minecraft:pig", dx: -3, label: "pig" }, { mob: "minecraft:cow", dx: 3, label: "cow" }] },
    "SHOT 1: from above (stand on a block or fly), looking down at all three.",
    "PASS = nothing worse. FAIL + note = which one and where."),
  rigStep("a21", "P4 REGRESSION", "CHECK: WOLF / FOX / SHEEP FROM ABOVE",
    "Three more: FOX (left), WOLF (middle), SHEEP (right). Same check.",
    { mob: "minecraft:wolf", label: "fox + wolf + sheep", half: 5, halfz: 2, row: [{ mob: "minecraft:fox", dx: -3, label: "fox" }, { mob: "minecraft:sheep", dx: 3, label: "sheep" }] },
    "SHOT 1: from above, looking down at all three.",
    "PASS = nothing worse. FAIL + note."),
  rigStep("a22", "P4 REGRESSION", "CHECK: ZOMBIE / PILLAGER / PIGLIN FROM ABOVE",
    "Hostile row (Creative - they ignore you): PILLAGER (left), ZOMBIE (middle), PIGLIN (right; it may turn zombified after 15 s - fine).\n" +
    "Look for: head tops and shoulders look right - nothing worse than before.",
    { mob: "minecraft:zombie", label: "pillager + zombie + piglin", half: 5, halfz: 2, row: [{ mob: "minecraft:pillager", dx: -3, label: "pillager" }, { mob: "minecraft:piglin", dx: 3, label: "piglin" }] },
    "SHOT 1: from above, looking down at all three.",
    "PASS = nothing worse. FAIL + note."),
];

const Q0 = { id: "q0", group: "P4 SETUP", title: "P4: VERSIONS, CREATIVE, EASY, FLAT, FACE NORTH",
  body: "Check the packs first: Settings > Global Resources > My Packs - RP-07 must say v1.4.20 and RP-06 v1.4.13 in their descriptions; this runner says v0.3.4 in the chat banner.\n" +
        "Creative mode, Difficulty EASY, an open FLAT spot with nothing for 12 blocks NORTH and 6 to each side, daylight, HUD position ON.\n" +
        "Each step pens its own mob(s) 5 blocks north and clears them as it goes. Videos are welcome where a step asks. Jump to a step: /scriptevent pw:test goto a07\n" +
        "PASS = versions right and you are set up. FAIL + note = a version is different (say which).",
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P4 DONE", title: "P4: ALL CLEAR - UPLOAD THE SHOTS",
  body: "The pens and pools are removed.\nUpload the screenshots/videos and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p4 and copy that.\nPASS = uploaded (or about to).",
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P4_STEPS = [Q0, ...FACES, ...SPIDER, ...GUARD, ...POSE, ...SIZES, ...MOTION, ...REGRESS, Q9];
export const P4_INDEX = Object.fromEntries(P4_STEPS.map((s, i) => [s.id, i]));
export const P4_MOBS = P4_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
