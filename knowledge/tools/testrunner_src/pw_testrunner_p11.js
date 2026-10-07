// pw_testrunner_p11.js — lineup "p11" (PW-TestRunner BP v0.4.2, D-C307: the R14 fixes — RP-06 1.4.21 + RP-07 1.4.27 +
// BP-02 1.3.193 + PW-StripMine BP 1.3.6). /scriptevent pw:test start p11
// Needs: RP-06 v1.4.21, RP-07 v1.4.27, BP-02 v1.3.193 active; the Naturalist steps (w11-w12) only work where PW-StripMine BP 1.3.6
// is loaded (the Realm).
const CLEAR = ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"];
const SHOT_S = "SHOT 1 SIDE-ON: from the EAST side of the pen, level with them, looking WEST.";
const SHOT_F = "SHOT 2 FRONT: from the south, eye level.";
const PASS_M = "PASS = it looks right to you. FAIL + note = what is off (parts, texture, motion, size).";
const DISC = "If the jukebox is silent: 1) type /give @s music_disc_cat  2) hold the disc and tap (use) the jukebox. Tap it again to stop the music.";

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
const REALM = "REALM ONLY: Naturalist creatures (PW-StripMine BP 1.3.6). Where it is not loaded the pen stays empty and the log says so - then just SKIP.\n";

const STEPS11 = [
  rigStep("g01", "P11 ALLAY", "ALLAY ARMS · DANCING TO A JUKEBOX",
    "The ALLAY next to a jukebox (the runner tries to start a disc; the log line 'RIG jukebox ...' says whether it could). Its arms now hang from its BODY - while it danced in R14 they floated beside its head (4 px off; now under 0.6 px).\n" + DISC + "\n" +
    "Look for: both arms staying on the body's sides the whole dance - spins, sways, head bobs.",
    { mob: "minecraft:allay", label: "allay", half: 4, halfz: 3, jukebox: { dx: 2, dz: -1, disc: "music_disc_cat" } },
    "SHOT / VIDEO: from the south while the music plays (a short video is the best witness).", "PASS = the arms stay on. FAIL + note = when they come off (dancing, turning, flying)."),
  rigStep("g02", "P11 ALLAY", "ALLAY ARMS · HOLDING + FLYING",
    "The ALLAY in a tall roofed pen, handed an amethyst shard, free to fly.\n" +
    "Look for: the arms raised to hold the shard and still attached to the body; the arms attached while it flies around.",
    { mob: "minecraft:allay", label: "allay", item: "amethyst_shard", roof: true, height: 5, half: 4, free: true }),
  rigStep("g03", "P11 VEX", "VEX · THE SWORD (THE FIX)",
    "The VEX with an iron sword (the runner gives it one). Its arms now hang from its body, its hand points were re-placed, and attachments are switched on - the allay had that switch and drew its shard; the vex did not.\n" +
    "Look for: the SWORD in its right hand; both arms on the body.\nIf there is still NO sword: open the content log and copy any line that mentions vex (that tells me the rest).",
    { mob: "minecraft:vex", label: "vex", item: "iron_sword", roof: true, height: 5, fly: true }),
  rigStep("g04", "P11 PROBE", "PROBE A · VEX HOLDING AN AMETHYST SHARD",
    "The same vex, handed the allay's item instead (an amethyst shard). This tells me whether the vex draws ANY held item, or only has trouble with swords.\n" +
    "Look for: a purple shard in its hand - or nothing.",
    { mob: "minecraft:vex", label: "vex", item: "amethyst_shard", roof: true, height: 5, fly: true },
    "SHOT: from the south, close.", "PASS = the shard shows. FAIL + note = no shard (say where the hand is)."),
  rigStep("g05", "P11 PROBE", "PROBE B · ALLAY HOLDING AN IRON SWORD",
    "The allay (which drew its shard in R14) handed an iron sword. This tells me whether swords draw at all on our models.\n" +
    "Look for: the sword held in front of the allay - or nothing.",
    { mob: "minecraft:allay", label: "allay", item: "iron_sword", roof: true, height: 5, fly: true },
    "SHOT: from the south, close.", "PASS = the sword shows. FAIL + note = no sword."),
  rigStep("g06", "P11 BLAZE", "BLAZE AT MIDNIGHT · THE GLOW",
    "MIDNIGHT (the runner sets it). The BLAZE glows again: Mojang's blaze lights itself through its texture (about 65 % self-lit, like Java's full-bright blaze) and ours had lost it - so its 'fire posts' looked dull. In Vibrant Visuals the Patrix fire glow is added on top (the first mob texture set in our packs).\n" +
    "Look for: head and rods bright against the dark sky, the fire streaks brightest. Too strong or too weak? Say so.",
    { mob: "minecraft:blaze", label: "blaze", roof: true, height: 5, half: 3, fly: true },
    "SHOT 1 FRONT, SHOT 2 from the east.", "PASS = it glows like fire. FAIL + note = dull, or too bright, or wrong colour.", [{ daytime: 18000 }]),
  rigStep("g07", "P11 BLAZE", "BLAZE AT NOON",
    "Back to noon: the same blaze in daylight (how you saw it in R14).\n" +
    "Look for: brighter, warmer rods than before; no black or white patches.",
    { mob: "minecraft:blaze", label: "blaze", roof: true, height: 5, half: 3, fly: true },
    "SHOT: from the south.", null, [{ daytime: "noon" }]),
  rigStep("g08", "P11 POLAR BEAR", "POLAR BEAR ON THE PATRIX MODEL",
    "The POLAR BEAR now wears Patrix's own model: the body 4 px lower with the legs sunk into it, the NECK block back, and the legs the right way round (our old model had the hind-leg shape on the front legs). Size kept at 2.5 m (it is re-measured on the new model). WOLF on the left for scale.\n" +
    "Look for: a long, low bear - no longer 'strangely tall'; the front legs under the chest; the neck turning a little with the head.",
    { mob: "minecraft:polar_bear", label: "polar bear", half: 7, halfz: 3, row: [{ mob: "minecraft:wolf", dx: -5, label: "wolf (reference)" }] }),
  rigStep("g09", "P11 SIZES", "DOLPHIN · A TYPICAL MALE (3.1 M)",
    "In the pool: the DOLPHIN at a typical adult male's length - 3.1 m = 3.3 blocks (it was 3.8 m = 4.0), your ruling.\n" +
    "Look for: a dolphin about one and three-quarters of you lying down.",
    { mob: "minecraft:dolphin", label: "dolphin", water: true, depth: 3, half: 6, halfz: 4 },
    "SHOT 1 SIDE-ON at the pool edge. SHOT 2 TOP: look down into the pool."),
  rigStep("g10", "P11 SIZES", "ENDERMITE · 25 % SMALLER",
    "The ENDERMITE loose in the pen, 25 % smaller (your 'maybe 20-30 %, I defer').\n" +
    "Look for: a tiny mite now; the legs still scuttle.",
    { mob: "minecraft:endermite", label: "endermite", free: true },
    "SHOT: crouch at the pen wall, level with it."),
  rigStep("w11", "P11 REALM", "GRIZZLY 2.8 M · BLACK BEAR · MALE LION",
    REALM + "LEFT to RIGHT: BLACK BEAR (1.83 m -> 1.93 blocks), GRIZZLY (now a big coastal brown-bear male: 2.8 m -> 2.95 blocks, was 2.53), MALE LION (unchanged: 3.02 m nose to TAIL TIP -> 3.19 blocks; about 0.9 m of that is tail).",
    { mob: "sf_nba:grizzly_bear", label: "grizzly", half: 8, halfz: 3, row: [{ mob: "sf_nba:black_bear", dx: -4, label: "black bear" }, { mob: "sf_nba:male_lion", dx: 5, label: "male lion" }] },
    null, "PASS = the grizzly now reads as the bigger animal. FAIL + note."),
  rigStep("w12", "P11 REALM", "ALLIGATOR 5.5 M · KOMODO 3.45 M · RAT SNAKE 1.43 M",
    REALM + "LEFT to RIGHT: KOMODO DRAGON (3.45 m -> 3.64 blocks, was 3.16), ALLIGATOR (5.5 m -> 5.8 blocks, was 5.06 - imposing, 15 % past the real top of range, your ruling), RAT SNAKE (an average adult male now: 1.43 m -> 1.51 blocks, was 2.18).",
    { mob: "sf_nba:alligator", label: "alligator", half: 8, halfz: 4, row: [{ mob: "sf_nba:komodo_dragon", dx: -5, label: "komodo dragon" }, { mob: "sf_nba:snake", dx: 5, label: "rat snake" }] },
    null, "PASS = reptiles imposing, snake right. FAIL + note."),
];

const Q0 = { id: "q0", group: "P11 SETUP", title: "P11: VERSIONS, CREATIVE, EASY, FLAT, FACE NORTH",
  body: lines("Check the packs first: RP-06 must say v1.4.21 and RP-07 v1.4.27 in their descriptions; the world's Behavior Packs: BP-02 v1.3.193 (the Realm: PW-StripMine BP v1.3.6); this runner says v0.4.2 in the chat banner.\n" +
        "After the world loads, glance at the content log: no entity / geometry / texture errors for vex, blaze, allay, polar bear.\n" +
        "Creative mode, Difficulty EASY, an open FLAT spot with nothing for 14 blocks NORTH and 9 to each side, daylight, HUD position ON. Every mob is grown up and logged.\n" +
        "PASS = versions right, log clean, you are set up. FAIL + note = a version differs or the log shows an error (copy it)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P11 DONE", title: "P11: ALL CLEAR - UPLOAD THE SHOTS",
  body: lines("The pens are removed.\n" +
        "Upload the screenshots / videos and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p11 and copy that.\nPASS = uploaded (or about to)."),
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P11_STEPS = [Q0, ...STEPS11, Q9];
export const P11_INDEX = Object.fromEntries(P11_STEPS.map((s, i) => [s.id, i]));
export const P11_MOBS = P11_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
