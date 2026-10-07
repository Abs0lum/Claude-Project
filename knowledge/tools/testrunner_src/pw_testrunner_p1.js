// pw_testrunner_p1.js — lineup "p1" v3 + the re-run lineup "p1r" (PW-TestRunner BP v0.3.1, D-C264/D-C266/D-C267).
// /scriptevent pw:test start p1    the whole test-world lineup (27 steps)
// /scriptevent pw:test start p1r   ONLY the steps the 09-28 round asked to re-run (the fixed mobs + the void stations)
//   H  the hostile mobs RP-06 rewired (+ creeper / evoker / ravager for the textures) in the WITNESS RIG under a barrier ROOF
//      (no sky = no burning) with fire resistance; adults; Creative so they ignore you.
//   B  block STATIONS built by commands 5 blocks NORTH of you: torches · lanterns · lit furnaces · flowing lava · nether portal ·
//      fire + soul fire · kelp tops · campfire · the XPACK PROBE (three blocks whose texture keys live ONLY in the TestRunner RP and
//      point at paths it does not hold — witnessed 09-28: A + B resolve across the stack, C checkers) · SUN · MOON · CLOUDS
//      (RP-02 owns the sky) · LEAVES (the before row) · the DEDUPE REGRESSION row.
// v0.3.1: block states use Bedrock's ["name"=value] syntax (the v0.3.0 ':' form never parsed — b03/b07/b13/b14 were void);
//         the evoker is minecraft:evocation_illager; step texts from the round-2 reads and the 1.4.9 / 1.4.14 / 1.3.142 fixes.
// Every station step first clears the station volume (feet level and up, 7 wide x 8 deep x 6 high, never the ground) and the pen.
const SHOTS = "SHOT 1 FRONT: as you stand (south of it), eye level, look NORTH.\nSHOT 2 LEFT FLANK: walk round to the EAST side and look WEST.\n";
const PASS_H = "PASS = a Patrix-textured mob with the Patrix shape (fine detail, articulated arms/legs, one piece). FAIL vanilla? = blocky low-res look · FAIL magenta? · FAIL parts? · FAIL + note = anything else.";
const ANGRY = "SHOT 3 ANGRY: type /gamemode s - within a few seconds it turns hostile (the pen holds it) - take the shot, then /gamemode c.\n";
const CLEAR = ["fill ~-3 ~ ~-9 ~3 ~5 ~-2 air"];                       // the station volume, feet level and up (the ground stays)
// [name, id, look-for, extra shot text]
const HOSTILES = [
  ["zombie", "minecraft:zombie", "green skin, blue shirt and trousers, arms out; forearms and shins are separate parts", ""],
  ["skeleton", "minecraft:skeleton", "a real ribcage and thin limbs (the Patrix skeleton), bow in hand", ""],
  ["drowned", "minecraft:drowned", "the PATRIX drowned now: teal-green skin with barnacles, weed and a detailed face (RP-07 1.4.14 removed the vanilla copy that sat above RP-06's skin)", ""],
  ["husk", "minecraft:husk", "sand-coloured wrapped mummy look WITH forearms and hands (RP-06 1.4.9 gave the limbs their texture maps)", ""],
  ["pillager", "minecraft:pillager", "grey illager face, dark red tunic with belt; the CROSSBOW now sits in its hand (RP-06 1.4.9 added the hand bones), not standing on end at the chest", ANGRY],
  ["stray", "minecraft:stray", "the PATRIX stray now: pale blue-grey skeleton, fine detail, ragged clothes overlay (RP-07 1.4.14 removed the vanilla copy, as for the drowned)", ""],
  ["vindicator", "minecraft:vindicator", "calm: grey illager face, dark robe, arms crossed, NO axe showing. Angry (shot 3): arms up and the axe IN ITS HAND - no handle through the chest", ANGRY],
  ["witch", "minecraft:witch", "black hat with a green gem, purple robe, and now her crossed ARMS in front of the robe (RP-06 1.4.9 converted the arms)", ""],
  ["creeper", "minecraft:creeper", "the green Patrix creeper skin, SOLID - no white glassy shell or blue veins (RP-06 1.4.9 shows the charged layer only on charged creepers)", ""],
  ["evoker", "minecraft:evocation_illager", "grey illager in dark robes, gold trim (last time it never spawned - my wrong id)", ""],
  ["ravager", "minecraft:ravager", "Patrix ravager skin on the vanilla shape (known mismatch until the converter runs - note anything NEW)", ""],
];
function hostileStep(i, [name, id, look, extra]) {
  return { id: `h${String(i + 1).padStart(2, "0")}`, group: "P1 HOSTILE", title: `RIG: ${name.toUpperCase()}`,
    body: `A ${name} is held still in the roofed pen 5 blocks NORTH, facing SOUTH. Look for: ${look}.\n${SHOTS}${extra}${PASS_H}`,
    setup: [{ cmd: CLEAR }, { rig: { mob: id, label: name, roof: true } }] };
}
// block stations: [id, title, look-for, commands, top-shot?, extra setup actions before the commands, PASS text] — all relative to
// where you stand, station centre ~ ~ ~-5.
const STATION_PASS = "PASS = crisp and animated as described. FAIL vanilla? = the vanilla look · FAIL smear? = blurry flat colour blocks · FAIL + note.";
const STATIONS = [
  ["b01", "TORCHES", "the flame flickers with fine detail (18 frames), the handle is wood-textured; soul torch blue; the copper torch has a COPPER handle by design",
    ["setblock ~-1 ~ ~-5 torch", "setblock ~ ~ ~-5 soul_torch", "setblock ~1 ~ ~-5 copper_torch"], false],
  ["b02", "LANTERNS", "the metal cage is crisp, the flame inside animates; soul lantern blue; the copper lantern family (4) beside them",
    ["setblock ~-3 ~ ~-5 lantern", "setblock ~-2 ~ ~-5 soul_lantern", "setblock ~-1 ~ ~-5 copper_lantern", "setblock ~ ~ ~-5 exposed_copper_lantern", "setblock ~1 ~ ~-5 weathered_copper_lantern", "setblock ~2 ~ ~-5 oxidized_copper_lantern"], false],
  ["b03", "LIT FURNACES", "the fire in the furnace / blast furnace / smoker fronts is a moving flame, not a smear; the stonecutter saw spins",
    ["setblock ~-2 ~ ~-5 lit_furnace [\"minecraft:cardinal_direction\"=\"south\"]", "setblock ~-1 ~ ~-5 lit_blast_furnace [\"minecraft:cardinal_direction\"=\"south\"]", "setblock ~ ~ ~-5 lit_smoker [\"minecraft:cardinal_direction\"=\"south\"]", "setblock ~1 ~ ~-5 stonecutter_block"], false],
  ["b04", "LAVA", "RP-04 1.3.142 put the Patrix timing on the lava: the FLOW down the pillar's side now cycles in about 2.5 seconds (last time 24 s), and the STILL lava on top is animated (8 frames blending over 4 s; last time it did not move at all). Say if the flow is too fast, right or too slow",
    ["fill ~ ~ ~-6 ~ ~1 ~-6 stone", "setblock ~ ~2 ~-6 lava"], true, [], "PASS = both move and the speed feels right. FAIL + note = too fast / too slow / not moving / anything else."],
  ["b05", "NETHER PORTAL", "a purple swirl with fine detail animating inside the obsidian frame (if the portal blocks are gone, light the frame with the flint and steel in your hand)",
    ["fill ~-2 ~ ~-6 ~1 ~4 ~-6 obsidian", "fill ~-1 ~1 ~-6 ~ ~3 ~-6 portal [\"portal_axis\"=\"x\"]", "give @s flint_and_steel 1"], false],
  ["b06", "FIRE + SOUL FIRE", "the fire is a detailed flame (30 frames); soul fire blue. All fires flicker IN STEP - that is the engine's single flipbook clock, not a fault",
    ["fill ~-2 ~ ~-5 ~1 ~ ~-5 netherrack", "fill ~-2 ~1 ~-5 ~1 ~1 ~-5 fire", "setblock ~2 ~ ~-5 soul_soil", "setblock ~2 ~1 ~-5 soul_fire"], true],
  ["b07", "KELP", "the kelp top (the bulb) is crisp and waves (20 frames); the stalk below it detailed",
    ["fill ~-1 ~ ~-6 ~1 ~4 ~-4 glass", "fill ~ ~ ~-5 ~ ~3 ~-5 water", "setblock ~ ~ ~-5 kelp [\"kelp_age\"=0]", "setblock ~ ~1 ~-5 kelp [\"kelp_age\"=1]", "setblock ~ ~2 ~-5 kelp [\"kelp_age\"=25]"], false],
  ["b08", "CAMPFIRE", "the flames are the Patrix tongues. The LOGS are still vanilla 16 px (known - Patrix has no campfire-log texture; a made-to-fit one comes later with a preview). The smoke is RP-02's plume - say whether it reads heavy/grey or soft",
    ["setblock ~ ~ ~-5 campfire", "setblock ~2 ~ ~-5 soul_campfire"], false, [], "PASS + note = flames right, and your word on the smoke. FAIL + note = anything else."],
  // the XPACK PROBE (D-C264): three TestRunner blocks. Their texture keys are registered ONLY in the TestRunner RP (at the TOP of the
  // list) and point at paths the TestRunner RP does NOT hold: A -> textures/blocks/stone (RP-04 holds the Patrix 128, vanilla the 16 px),
  // B -> textures/blocks/mushroom_stem_v3 (held by RP-01 only, a name vanilla does not have), C -> a path nobody holds (the control).
  // Witnessed 09-28 (D-C266): A = RP-04's stone, B = RP-01's stem, C = checker -> whole-stack lookup. Kept as a regression row.
  ["b09", "XPACK PROBE (A stone / B mushroom stem / C checker) + logs", "front row, left to right: A grey 128 stone, B pale cream mushroom stem, C the magenta/black checker (the known 09-28 result). Behind them oak / birch / spruce logs (all three Patrix bark)",
    ["setblock ~-2 ~ ~-5 pw:xprobe_a", "setblock ~ ~ ~-5 pw:xprobe_b", "setblock ~2 ~ ~-5 pw:xprobe_c", "setblock ~-1 ~ ~-7 oak_log", "setblock ~ ~ ~-7 birch_log", "setblock ~1 ~ ~-7 spruce_log"], false, [],
    "PASS = A stone, B stem, C checker, logs Patrix (the known result). FAIL + note = anything different (that would be news)."],
  ["b10", "SUN (RP-02 owns the sky)", "it is sunset. Look WEST at the sun on the horizon: PASS = RP-02's warm-halo sun with a soft glow. FAIL vanilla? = a plain white square; FAIL + note 'rays' = a white disc with rays (the old RP-04 sun)",
    [], false, [{ daytime: 12500 }, { weather: "clear" }], "PASS = the warm-halo sun. FAIL vanilla? / FAIL + note."],
  ["b11", "MOON (RP-02 owns the sky)", "it is midnight. Look UP at the moon: PASS = a textured moon with craters. FAIL vanilla? = the plain vanilla moon; FAIL + note 'flat' = a flat grey disc (the old RP-04 moon)",
    [], false, [{ daytime: 18000 }, { weather: "clear" }], "PASS = the textured moon. FAIL vanilla? / FAIL + note."],
  ["b12", "CLOUDS (RP-02 owns the sky)", "noon, clear. Look UP at the clouds: PASS = soft, detailed cloud shapes (the 256 cloud map). FAIL + note 'blocky' = coarse 1x1 blocks (the old RP-04 cloud map)",
    [], false, [{ daytime: "noon" }, { weather: "clear" }], "PASS = soft detailed clouds. FAIL + note."],
  ["b13", "LEAVES (the before row)", "a row of oak / birch / spruce / dark oak / pale oak leaves with two AbsolutRealism variant leaves above. This is the BEFORE row - today's 32 px leaves; the 128 x 8 leaves ship with the ownership wave. PASS + note '32' = all seven placed, soft 32 px, with a wind shimmer. FAIL + note = checker / black / missing / no shimmer",
    ["setblock ~-2 ~ ~-5 oak_leaves [\"persistent_bit\"=true]", "setblock ~-1 ~ ~-5 birch_leaves [\"persistent_bit\"=true]", "setblock ~ ~ ~-5 spruce_leaves [\"persistent_bit\"=true]", "setblock ~1 ~ ~-5 dark_oak_leaves [\"persistent_bit\"=true]", "setblock ~2 ~ ~-5 pale_oak_leaves [\"persistent_bit\"=true]",
     "setblock ~-1 ~1 ~-5 pw:oak_leaves [\"pw:variant\"=3]", "setblock ~1 ~1 ~-5 pw:spruce_leaves [\"pw:variant\"=5]"], false, [{ daytime: "noon" }], "PASS + note '32' = the before row placed and shimmering. FAIL + note."],
  ["b14", "DEDUPE REGRESSION (files that changed pack)", "back row: quartz block, LIT white candle, oxidized copper, podzol, mycelium, bricks, glass. Front row: allium, blue orchid, rose bush (both halves). Sides: two AbsolutRealism slabs (dirt, sand) - their SIDE faces must be textured. PASS = every block Patrix + PBR; FAIL + note = name any that is vanilla, checkered or black",
    ["setblock ~-3 ~ ~-6 quartz_block", "setblock ~-2 ~ ~-6 white_candle [\"lit\"=true]", "setblock ~-1 ~ ~-6 oxidized_copper", "setblock ~ ~ ~-6 podzol", "setblock ~1 ~ ~-6 mycelium", "setblock ~2 ~ ~-6 brick_block", "setblock ~3 ~ ~-6 glass",
     "setblock ~-1 ~ ~-4 allium", "setblock ~ ~ ~-4 blue_orchid", "setblock ~1 ~ ~-4 rose_bush", "setblock ~1 ~1 ~-4 rose_bush [\"upper_block_bit\"=true]",
     "setblock ~-3 ~ ~-3 pw:slab_dirt", "setblock ~3 ~ ~-3 pw:slab_sand"], true, [], "PASS = all Patrix + PBR. FAIL + note = name the odd ones."],
];
function stationStep([id, title, look, cmds, top, pre, passText]) {
  const setup = [{ rigclear: true }, ...(pre || []), { cmd: CLEAR.concat(cmds) }];
  return { id, group: "P1 BLOCKS", title: `STATION: ${title}`,
    body: `Built 5 blocks NORTH of you. Look for: ${look}.\nSHOT 1: from where you stand, close enough to fill the frame.\n${top ? "SHOT 2: from above, looking down at it.\n" : ""}${passText || STATION_PASS}`,
    setup };
}
const Q0 = { id: "q0", group: "P1 SETUP", title: "P1: CREATIVE, EASY, FLAT, FACE NORTH",
  body: "Creative mode (hostile mobs ignore you), Difficulty EASY (Settings > Game), an open FLAT spot with nothing for 10 blocks NORTH, daylight, HUD position ON.\n" +
        "PW-TestRunner RP must be at the TOP of the resource-pack list (the XPACK probe depends on it). Each step builds its own station or pens its own mob 5 blocks north; the runner clears them as it goes and at the end.\n" +
        "Type /scriptevent pw:stats off first so the content log stays readable. You can jump straight to a step: /scriptevent pw:test goto b03",
  setup: [{ daytime: "noon" }, { weather: "clear" }] };
const Q9 = { id: "q9", group: "P1 DONE", title: "P1: ALL CLEAR - UPLOAD THE SHOTS",
  body: "The pen and the stations are removed, time set back to noon. Upload the screenshots to the Drive and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard).\nPASS = uploaded (or about to).",
  setup: [{ rigclear: true }, { cmd: CLEAR }, { daytime: "noon" }] };
export const P1_STEPS = [Q0, ...HOSTILES.map((h, i) => hostileStep(i, h)), ...STATIONS.map(stationStep), Q9];
export const P1_INDEX = Object.fromEntries(P1_STEPS.map((s, i) => [s.id, i]));
export const P1_HOSTILES = HOSTILES.map(([name, id]) => ({ name, id }));
export const P1_STATIONS = STATIONS.map(([id, title]) => ({ id, title }));
export const P1_PROBES = { a: "textures/blocks/stone", b: "textures/blocks/mushroom_stem_v3", c: "textures/blocks/pw_xprobe_nowhere" };
// the RE-RUN lineup (09-28 round 3): the eight hostiles the fixes touched + the evoker that never spawned, and the stations that were
// void (my ':' syntax) or changed (lava, campfire text). The same step objects as p1, so ids and verdict keys match the full lineup.
export const P1R_IDS = ["q0", "h03", "h04", "h05", "h06", "h07", "h08", "h09", "h10", "b03", "b04", "b07", "b08", "b13", "b14", "q9"];
export const P1R_STEPS = P1R_IDS.map((id) => P1_STEPS[P1_INDEX[id]]);
export const P1R_INDEX = Object.fromEntries(P1R_STEPS.map((s, i) => [s.id, i]));
