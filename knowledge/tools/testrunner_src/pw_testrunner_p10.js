// pw_testrunner_p10.js — lineup "p10" (PW-TestRunner BP v0.4.1, D-C300: FA-1 — the flyers and the mobs whose Patrix skins sat on
// Mojang's models, all on their Patrix models now; SIZE ROUND 2 — predators at prime-male size, the parrot per colour, the bat).
// /scriptevent pw:test start p10
// Needs: RP-06 v1.4.20, RP-07 v1.4.26, BP-02 v1.3.192 active; the Naturalist steps (w16-w17) only work where PW-StripMine BP 1.3.5
// is loaded (the Realm).
const CLEAR = ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"];
const SHOT_S = "SHOT 1 SIDE-ON: from the EAST side of the pen, level with them, looking WEST.";
const SHOT_F = "SHOT 2 FRONT: from the south, eye level.";
const PASS_M = "PASS = Patrix quality, one coherent creature, moving right. FAIL + note = what is off (parts, texture, motion, size).";
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
const REALM = "REALM ONLY: Naturalist creatures (PW-StripMine BP 1.3.5). Where it is not loaded the pen stays empty and the log says so - then just SKIP.\n";

const STEPS10 = [
  rigStep("f01", "P10 PARROTS", "PARROTS · FIVE COLOURS (PERCHED)",
    "LEFT to RIGHT: RED-BLUE, BLUE, GREEN, YELLOW-BLUE (four macaws, 0.89 block - a real macaw 0.84 m bill to tail), then the GREY one: an African grey (0.33 m in life), clearly SMALLER at 0.57 block - under 60 cm the size law keeps small animals a little bigger than life so they stay visible. The runner re-rolls each until it has the right colour (the log says).\n" +
    "Look for: Patrix feathers, folded wings, the tail hanging; head turning and bobbing on its own.",
    { mob: "minecraft:parrot", label: "green parrot", variant: 2, half: 6, halfz: 3, row: [
      { mob: "minecraft:parrot", dx: -4, label: "red-blue parrot", variant: 0 }, { mob: "minecraft:parrot", dx: -2, label: "blue parrot", variant: 1 },
      { mob: "minecraft:parrot", dx: 2, label: "yellow-blue parrot", variant: 3 }, { mob: "minecraft:parrot", dx: 4, label: "grey parrot", variant: 4 }] }),
  rigStep("f02", "P10 PARROTS", "PARROTS FLYING (FREE)",
    "Two parrots loose in a tall roofed pen: a RED-BLUE macaw and the GREY one. When they take off the folded wings are swapped for Patrix's second wing set (long flight feathers) and the legs tuck.\n" +
    "Look for: the flight wings flapping, no leftover folded wing, the landing swap back. A short VIDEO is the best witness.",
    { mob: "minecraft:parrot", label: "red-blue parrot", variant: 0, free: true, roof: true, height: 6, half: 4, halfz: 3, row: [{ mob: "minecraft:parrot", dx: 2, label: "grey parrot", variant: 4 }] },
    "SHOT / VIDEO: while one is in the air, from the south.", "PASS = the flight wings show in the air and fold back on landing. FAIL + note = what you saw."),
  rigStep("f03", "P10 DANCE", "PARROT + ALLAY DANCE TO A JUKEBOX",
    "A jukebox sits in the pen, just behind and right of the parrot (a parrot only dances within about 3 blocks of the music). The runner tries to start a disc by script; the log line 'RIG jukebox ...' says whether it could.\n" + DISC + "\n" +
    "Look for: the PARROT dancing (Patrix dance legs appear, body sways) and the ALLAY dancing (spins, wings beat, head sways).",
    { mob: "minecraft:parrot", label: "red-blue parrot", variant: 0, half: 4, halfz: 3, jukebox: { dx: 2, dz: -1, disc: "music_disc_cat" },
      row: [{ mob: "minecraft:allay", dx: -2, label: "allay" }] },
    "SHOT / VIDEO: from the south while the music plays.", "PASS = both dance. FAIL + note = which one does not (and whether the music played)."),
  rigStep("f04", "P10 BAT", "BAT · REAL SIZE",
    "One bat loose in a tall roofed pen (it flies, and may hang from the ceiling to rest). Its wingspan is 0.42 block now (it was 1.17 blocks) - your pick, between true-to-life 0.29 (a cave bat spans about 28 cm) and the small-animal curve's 0.56.\n" +
    "Look for: the Patrix bat (big ears, furry body, thin wing membranes), flapping on Mojang's flight animation; hanging upside down if it roosts.",
    { mob: "minecraft:bat", label: "bat", free: true, roof: true, height: 5, half: 3 },
    "SHOT: from the south, close to the pen.", "PASS = Patrix bat, the size looks right to you. FAIL + note (too big / too small)."),
  rigStep("f05", "P10 ALLAY", "ALLAY HOLDING AN ITEM",
    "The ALLAY is handed an amethyst shard (the runner puts it in its hand).\n" +
    "Look for: the Patrix allay (blue, see-through wings), its arms raised holding the shard in front of it; the wings beating.",
    { mob: "minecraft:allay", label: "allay", item: "amethyst_shard", roof: true, height: 5, fly: true }),
  rigStep("f06", "P10 VEX", "VEX WITH ITS SWORD",
    "The VEX, sword in hand (the runner gives it an iron sword). It only raises the sword to charge when it attacks - in creative it will not, so no need to wait for that.\n" +
    "Look for: the Patrix vex (grey ghost body, bony wings), the SWORD in its right hand (it had no hand points before), the wings flapping.",
    { mob: "minecraft:vex", label: "vex", item: "iron_sword", roof: true, height: 5, fly: true }),
  rigStep("f07", "P10 PHANTOM", "PHANTOM AT DUSK",
    "DUSK (the runner sets the time). The PHANTOM in a tall roofed pen, fire-resistant.\n" +
    "Look for: the Patrix phantom (ragged wings, bony tail), its EYES GLOWING green in the dusk, the wings beating and the body banking.",
    { mob: "minecraft:phantom", label: "phantom", roof: true, height: 6, half: 4, fly: true },
    "SHOT 1 from the south, SHOT 2 from the east side.", null, [{ daytime: 13000 }]),
  rigStep("f08", "P10 WARDEN", "THE WARDEN ON ITS PATRIX MODEL",
    "MIDNIGHT (the runner sets it) so the glow shows. The WARDEN, 20 % bigger than vanilla (your ruling), on the Patrix model now - the 'UV mapping error' was its Patrix skin drawn on Mojang's model.\n" +
    "Look for: antler-like glowing TENDRILS, the jaw-face head, the rib cage, bone spikes on the arms; the soul GLOW (rebuilt from Patrix's glow map - tell me if it is too strong or too weak); no content-log animation error.",
    { mob: "minecraft:warden", label: "warden", roof: true, height: 6, half: 4, halfz: 3 },
    "SHOT 1 FRONT: from the south, look UP at him. SHOT 2 SIDE: from the east.", null, [{ daytime: 18000 }]),
  rigStep("f09", "P10 FLAME", "BLAZE",
    "Back to noon. The BLAZE on its Patrix model: a flame-mask head, 12 rods in three rings that ORBIT and BOB (Java's own blaze math).\n" +
    "Look for: the rings turning around it, centred on its body (a converter bug had it 7 px off-centre - fixed), the head mask facing you.",
    { mob: "minecraft:blaze", label: "blaze", roof: true, height: 5, half: 3, fly: true },
    "SHOT 1 FRONT, SHOT 2 from the east. A short VIDEO shows the rings.", null, [{ daytime: "noon" }]),
  rigStep("f10", "P10 WIND", "BREEZE",
    "The BREEZE on its Patrix model: head and three rods, with the WIND SWIRL under it (three layers from Patrix's wind model, scrolling) and glowing eyes.\n" +
    "Look for: a whirling wind body under the head (not missing, not a solid block), the rods hanging, the eyes.",
    { mob: "minecraft:breeze", label: "breeze", roof: true, height: 5, half: 3 }),
  rigStep("f11", "P10 CREAKING", "CREAKING",
    "The CREAKING on its Patrix model (tree-bark body, branch crown, root feet) - it was drawn broken on Mojang's model before.\n" +
    "Look for: one coherent tree creature, no floating pieces; the orange eyes (they glow when it is active).",
    { mob: "minecraft:creaking", label: "creaking", roof: true, height: 5 }),
  rigStep("f12", "P10 ENDERMITE", "ENDERMITE (FREE)",
    "The ENDERMITE loose in the pen: Patrix's jointed body with FreshLX's own motion (legs scuttle, tail and head sway).\n" +
    "Look for: the legs moving as it crawls, the segments bending.",
    { mob: "minecraft:endermite", label: "endermite", free: true },
    "SHOT: crouch at the pen wall, level with it (a short VIDEO shows the legs)."),
  rigStep("f13", "P10 SNIFFER", "SNIFFER",
    "The SNIFFER on its Patrix model (mossy back, the long snout). It keeps Mojang's own motion (sniffing, digging, standing up) - Patrix's extra wobble comes later.\n" +
    "Look for: a level, coherent sniffer (no tilt), the head and ears; if it digs, the dig looks right.",
    { mob: "minecraft:sniffer", label: "sniffer", half: 5, halfz: 4, free: true }),
  rigStep("f14", "P10 SIZES", "PREDATORS AT PRIME-MALE SIZE: POLAR BEAR · FOX · OCELOT (+ WOLF)",
    "Your ruling: predators at the top of their adult-male range. LEFT to RIGHT: WOLF (unchanged - your calibration), POLAR BEAR (2.5 m -> 2.64 blocks, was 2.2), FOX (0.72 m body -> 0.76), OCELOT (1.0 m body -> 1.05, was 0.79).\n" +
    "Look for: a big male polar bear towering over the wolf; fox and ocelot a little bigger than before.",
    { mob: "minecraft:polar_bear", label: "polar bear", half: 8, halfz: 3, row: [{ mob: "minecraft:wolf", dx: -5, label: "wolf (reference)" },
      { mob: "minecraft:fox", dx: 4, label: "fox" }, { mob: "minecraft:ocelot", dx: 6, label: "ocelot" }] }),
  rigStep("f15", "P10 SIZES", "DOLPHIN · A BIG MALE (4 BLOCKS)",
    "In the pool: a DOLPHIN at a big male bottlenose's length, 3.8 m = 4.0 blocks (it was 2.6). Offshore males really reach this; if it feels too much, say so and I will use the typical male (3.1 m).\n" +
    "Look for: a dolphin clearly longer than two of you lying down.",
    { mob: "minecraft:dolphin", label: "dolphin", water: true, depth: 3, half: 6, halfz: 4 },
    "SHOT 1 SIDE-ON at the pool edge. SHOT 2 TOP: look down into the pool. (Tapping the invisible wall breaks it - the runner puts it back within half a second.)"),
  rigStep("w16", "P10 REALM", "GRIZZLY · BLACK BEAR · MALE LION (PRIME MALES)",
    REALM + "LEFT to RIGHT: BLACK BEAR (1.83 m -> 1.93 blocks), GRIZZLY (2.4 m -> 2.53), MALE LION (3.0 m nose to tail -> 3.19).",
    { mob: "sf_nba:grizzly_bear", label: "grizzly", half: 8, halfz: 3, row: [{ mob: "sf_nba:black_bear", dx: -4, label: "black bear" }, { mob: "sf_nba:male_lion", dx: 5, label: "male lion" }] }),
  rigStep("w17", "P10 REALM", "ALLIGATOR · KOMODO DRAGON · RAT SNAKE",
    REALM + "LEFT to RIGHT: KOMODO DRAGON (3.0 m -> 3.16 blocks), ALLIGATOR (a big male, 4.8 m -> 5.06 blocks), RAT SNAKE (2.07 m -> 2.18).",
    { mob: "sf_nba:alligator", label: "alligator", half: 8, halfz: 4, row: [{ mob: "sf_nba:komodo_dragon", dx: -5, label: "komodo dragon" }, { mob: "sf_nba:snake", dx: 5, label: "rat snake" }] }),
];

const Q0 = { id: "q0", group: "P10 SETUP", title: "P10: VERSIONS, CREATIVE, EASY, FLAT, FACE NORTH",
  body: lines("Check the packs first: RP-06 must say v1.4.20 and RP-07 v1.4.26 in their descriptions; the world's Behavior Packs: BP-02 v1.3.192 (the Realm: PW-StripMine BP v1.3.5); this runner says v0.4.1 in the chat banner.\n" +
        "After the world loads, glance at the content log: no entity / geometry / animation errors for parrot, bat, allay, sniffer, vex, phantom, warden, blaze, breeze, creaking, endermite.\n" +
        "Creative mode, Difficulty EASY, an open FLAT spot with nothing for 14 blocks NORTH and 9 to each side, daylight, HUD position ON. Every mob is grown up (babies that cannot grow are re-summoned) and logged.\n" +
        "PASS = versions right, log clean, you are set up. FAIL + note = a version differs or the log shows an error (copy it)."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P10 DONE", title: "P10: ALL CLEAR - UPLOAD THE SHOTS",
  body: lines("The pens are removed. The orca (8.4 blocks now) is too big for a pen: if you meet one, a screenshot next to it is welcome.\n" +
        "Upload the screenshots / videos and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or type /scriptevent pw:test report p10 and copy that.\nPASS = uploaded (or about to)."),
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };

export const P10_STEPS = [Q0, ...STEPS10, Q9];
export const P10_INDEX = Object.fromEntries(P10_STEPS.map((s, i) => [s.id, i]));
export const P10_MOBS = P10_STEPS.filter((s) => s.setup.some((a) => a.rig)).map((s) => ({ id: s.id, rig: s.setup.find((a) => a.rig).rig }));
