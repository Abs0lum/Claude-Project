// pw_testrunner_p3.js — lineup "p3" + the short "p3n" (PW-TestRunner BP v0.3.2, D-C277, his 09-29 00:34 "create a new test in our
// testrunner BP with the mobs to check and we'll do it quickly").
// /scriptevent pw:test start p3n   ONLY what RP-07 1.4.19 + RP-06 1.4.12 changed (16 steps)
// /scriptevent pw:test start p3    that, then every Converter B mob from RP-07 1.4.16-1.4.18 not yet seen in game (33 steps)
// Needs: RP-07 v1.4.19 and RP-06 v1.4.12 active (the bar's first step says how to check), Creative, Difficulty EASY, flat ground.
const CLEAR = ["fill ~-6 ~ ~-12 ~6 ~5 ~-2 air"];                    // wide enough for the size rows (never the ground)
const SHOT_F = "SHOT 1 FRONT: as you stand (south of it), eye level, look NORTH.";
const SHOT_L = "SHOT 2 LEFT FLANK: walk round to the EAST side and look WEST.";
const PASS_M = "PASS = Patrix detail, one creature in one piece, and the point named above is right. FAIL vanilla? / FAIL magenta? / FAIL parts? / FAIL + note = anything else.";

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

// ------------------------------------------------------------------------------------------------ NEW in RP-07 1.4.19 / RP-06 1.4.12
const NEW = [
  rigStep("n01", "P3 SIZES", "SIZES: HORSE / DONKEY / MULE",
    "Three held side by side 5 blocks NORTH: DONKEY on the LEFT (west), HORSE in the MIDDLE, MULE on the RIGHT (east). RP-07 1.4.19 draws them at Java's sizes: horse 1.1x, donkey 0.87x, mule 0.92x.\n" +
    "Look for: the HORSE is clearly the biggest (ear tips about 2.3 blocks up), the MULE a little smaller (about 2.1), the DONKEY the smallest (about 2.0). Before this build the donkey stood TALLER than the horse.",
    { mob: "minecraft:horse", label: "horse + donkey + mule", half: 5, halfz: 2, row: [{ mob: "minecraft:donkey", dx: -3, label: "donkey" }, { mob: "minecraft:mule", dx: 3, label: "mule" }] },
    "SHOT 1 SIDE-ON ROW: step back until all three fit, eye level, look NORTH.",
    "PASS = horse biggest, then mule, then donkey. FAIL + note = the order or the sizes look wrong."),
  rigStep("n02", "P3 SIZES", "SIZES: CAT / OCELOT",
    "A CAT (left, west) and an OCELOT (right, east) side by side. Java draws the cat at 0.8x the ocelot; we drew the cat at 0.64x (too small) until this build.\n" +
    "Look for: the cat about FOUR FIFTHS of the ocelot's size - clearly smaller, but not tiny.",
    { mob: "minecraft:ocelot", label: "ocelot + cat", row: [{ mob: "minecraft:cat", dx: -2, label: "cat" }] },
    "SHOT 1 SIDE-ON: both in frame, eye level, look NORTH.",
    "PASS = cat about 4/5 of the ocelot. FAIL + note = too small / same size / anything else."),
  rigStep("n03", "P3 SIZES", "SIZES: HUSK / ZOMBIE",
    "A ZOMBIE (left, west) and a HUSK (right, east) in the roofed pen. Java draws the husk 1.0625x the zombie - a little taller.\n" +
    "Look for: the husk's head a little above the zombie's (about a pixel or two of the texture).",
    { mob: "minecraft:husk", label: "husk + zombie", roof: true, row: [{ mob: "minecraft:zombie", dx: -2, label: "zombie" }] },
    "SHOT 1 SIDE-ON: both in frame, eye level, look NORTH.",
    "PASS = husk slightly taller. FAIL + note."),
  rigStep("n04", "P3 GUARDIANS", "RIG: GUARDIAN (RESTING)",
    "A guardian held in the POOL 5 blocks NORTH. Look for: the Patrix guardian (the spike layout you approved in the preview) - 12 spikes, one at the middle of each edge, pointing OUT on the diagonals, fully out (it is resting). The TAIL sways slowly. Walk left and right in front of it: the EYE slides toward you and the whole body turns to look at you.",
    { mob: "minecraft:guardian", label: "guardian", water: true },
    `${SHOT_F}\n${SHOT_L}\nNOTE the eye: does it slide TOWARD you or AWAY when you step sideways?`,
    "PASS = spikes as the preview, tail swaying, eye + body follow you. FAIL + note = say which part (spikes / tail / eye / body)."),
  rigStep("n05", "P3 GUARDIANS", "SWIM TANK: GUARDIAN MOVING",
    "The same guardian FREE in a bigger, deeper tank (9 x 9, 3 deep, a little further north). It swims around on its own. Look for: while it SWIMS the spikes pull IN (almost hidden), when it STOPS they slide back OUT over about a second; the tail swings faster while swimming.",
    { mob: "minecraft:guardian", label: "guardian (free)", water: true, free: true, half: 4, depth: 3, height: 4 },
    "SHOT 1: while it swims (spikes in). SHOT 2: when it pauses (spikes out). A short video is even better.",
    "PASS = spikes go in when swimming, out when still; tail swings. FAIL + note = spikes never move / move the wrong way / jitter."),
  rigStep("n06", "P3 GUARDIANS", "RIG: ELDER GUARDIAN",
    "An ELDER guardian (2.35x) held in a bigger pool. Look for: the pale elder skin, the same spike layout (blue-grey spikes), tail swaying, eye following you.",
    { mob: "minecraft:elder_guardian", label: "elder guardian", water: true, half: 4, depth: 3, height: 4 }),
  rigStep("n07", "P3 REBUILT", "RIG: SPIDER",
    "A spider held in the pen. Look for: the Patrix spider - 8 long legs splayed out low around the body (not hanging straight down), a small head with two jaws and two palps in front, a big rounded abdomen behind; red eyes on the head.",
    { mob: "minecraft:spider", label: "spider" }),
  rigStep("n08", "P3 REBUILT", "PEN: SPIDER WALKING",
    "The spider FREE in the pen - it walks around. Look for: the legs step as it walks and stay attached at the body; no leg flies off or sinks deep into the ground.",
    { mob: "minecraft:spider", label: "spider (free)", free: true },
    "SHOT 1 (or a short video): while it walks.",
    "PASS = legs move and stay on the body. FAIL + note."),
  rigStep("n09", "P3 REBUILT", "RIG: BEE",
    "A bee held in the air in the pen. Look for: the Patrix bee - black head with antennae, striped thorax and abdomen with a stinger, SIX legs hanging, two clear wings FLAPPING. Last build it was in shreds (big grey sheets, floating strips).",
    { mob: "minecraft:bee", label: "bee", fly: true }),
  rigStep("n10", "P3 REBUILT", "RIG: TADPOLE",
    "A tadpole held in the pool. Look for: a SMALL rounded body (half the size it was) with the thin tail behind, tail wiggling.",
    { mob: "minecraft:tadpole", label: "tadpole", water: true },
    "SHOT 1: from above, close up, looking down at it.",
    "PASS = small body + tail, in one piece. FAIL + note."),
  rigStep("n11", "P3 REBUILT", "RIG: ZOMBIFIED PIGLIN (HEAD TILT)",
    "A zombified piglin in the roofed pen. Look for: the head now LEANS to one side and a little forward (the Java Patrix pose - its head hangs crooked), and still turns to look at you.",
    { mob: "minecraft:zombie_pigman", label: "zombified piglin", roof: true }),
  rigStep("n12", "P3 REBUILT", "RIG: PIGLIN",
    "A piglin in the pen. TAKE THE SHOTS WITHIN 15 SECONDS - in the Overworld a piglin shakes and turns into a zombified piglin (vanilla); use Repeat setup for a fresh one. Look for: the Patrix piglin - snout, ears, leather jerkin with the gold buckle, one piece.",
    { mob: "minecraft:piglin", label: "piglin" }),
  rigStep("n13", "P3 REBUILT", "RIG: PIGLIN BRUTE",
    "A piglin brute in the pen (also turns within 15 s - Repeat setup for a fresh one). Look for: the Patrix brute - bigger jaw, dark clothes, gold belt.",
    { mob: "minecraft:piglin_brute", label: "piglin brute" }),
  rigStep("n14", "P3 REBUILT", "RIG: BOGGED",
    "A bogged in the roofed pen. Look for: the mossy skeleton with red mushrooms on the head; the head tipped slightly forward; one piece.",
    { mob: "minecraft:bogged", label: "bogged", roof: true }),
];

// ------------------------------------------------------------------------------------------------ earlier Converter B (1.4.16-1.4.18)
const EARLIER = [
  ["turtle", "minecraft:turtle", { water: true }, "shell, head out front, four flat flippers; sits on the pool floor, not in it"],
  ["salmon", "minecraft:salmon", { water: true }, "one long body with fins and tail - no gaps between the parts"],
  ["dolphin", "minecraft:dolphin", { water: true }, "body, beak, dorsal fin, flukes - one animal"],
  ["axolotl", "minecraft:axolotl", { water: true }, "head with gills, body, FOUR legs (not eight), flat tail"],
  ["frog", "minecraft:frog", {}, "the Patrix frog, NO throat sac showing while it sits"],
  ["tropical fish", "minecraft:tropicalfish", { water: true }, "a small patterned fish, head joined to the body (no gap)"],
  ["panda", "minecraft:panda", {}, "round body, head with the eye patches, four legs"],
  ["mooshroom", "minecraft:mooshroom", {}, "red cow with mushrooms, head under the body line like the cow"],
  ["wolf", "minecraft:wolf", {}, "body on the legs, head forward, tail behind"],
  ["squid", "minecraft:squid", { water: true }, "mantle with the 8 tentacles in a RING below it (known: the tentacles do not pulse yet - that is next)"],
  ["glow squid", "minecraft:glow_squid", { water: true }, "as the squid, glowing (same known tentacle note)"],
  ["rabbit", "minecraft:rabbit", {}, "nose and mouth ON the face, ears on the head, feet under the body"],
  ["camel", "minecraft:camel", {}, "the ears stay on the head, hump, long legs"],
  ["chicken", "minecraft:chicken", {}, "TWO legs, wings as plates on the sides, comb and wattle"],
  ["llama", "minecraft:llama", {}, "the fur layers do NOT flicker on the rump/flank when you move around it"],
  ["trader llama", "minecraft:trader_llama", {}, "the blue blanket, tassels and halter clearly OVER the fur, no flicker"],
  ["ravager", "minecraft:ravager", { roof: true }, "one solid body, head low between the front legs, horns, four legs on the ground"],
];
const EARLY = EARLIER.map(([name, id, o, look], i) => rigStep(`e${String(i + 1).padStart(2, "0")}`, "P3 EARLIER REBUILDS", `RIG: ${name.toUpperCase()}`,
  `A ${name} held in the ${o.water ? "POOL" : o.roof ? "roofed pen" : "pen"} 5 blocks NORTH (rebuilt in RP-07 1.4.16-1.4.18, not yet seen in game). Look for: ${look}.`,
  { mob: id, label: name, ...o }));

const Q0 = { id: "q0", group: "P3 SETUP", title: "P3: VERSIONS, CREATIVE, EASY, FLAT, FACE NORTH",
  body: "Check the packs first: Settings > Global Resources > My Packs - RP-07 must say v1.4.19 and RP-06 v1.4.12 in their descriptions.\n" +
        "Creative mode (hostile mobs ignore you), Difficulty EASY, an open FLAT spot with nothing for 12 blocks NORTH and 6 to each side, daylight, HUD position ON.\n" +
        "Each step pens its own mob(s) 5 blocks north; the runner clears them as it goes. /scriptevent pw:stats off keeps the content log readable. Jump to a step: /scriptevent pw:test goto n05\n" +
        "PASS = both versions right and you are set up. FAIL + note = a version is different (say which).",
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P3 DONE", title: "P3: ALL CLEAR - UPLOAD THE SHOTS",
  body: "The pens and pools are removed. Upload the screenshots and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p3 and copy that.\nPASS = uploaded (or about to).",
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P3_STEPS = [Q0, ...NEW, ...EARLY, Q9];
export const P3_INDEX = Object.fromEntries(P3_STEPS.map((s, i) => [s.id, i]));
export const P3N_STEPS = [Q0, ...NEW, Q9];
export const P3N_INDEX = Object.fromEntries(P3N_STEPS.map((s, i) => [s.id, i]));
export const P3_MOBS = [...NEW, ...EARLY].map((s) => ({ id: s.id, rig: s.setup[1].rig }));
