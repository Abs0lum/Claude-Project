// pw_testrunner_p0.js — the PHASE 0 lineup (PW-TestRunner BP v0.3.1 wording: pufferfish puff, fish size; v0.2.2, D-C257/D-C260): the rotation-law PROBE, then every RP-07
// mob in the WITNESS RIG, worst-first (MOB-CONVERSION-RESEARCH §5 / PHASE0-PROTOCOL §2–§3).  Start it with
// /scriptevent pw:test start p0 — the runner sets each step up by itself (probe / pen / pool / mob), you take the
// screenshots it names, tap the clicker: PASS = "shots taken" (FAIL/note = something was wrong with the setup).
//
// Setup actions used here (run automatically when the step starts, and on "Repeat setup"):
//   { probe: "static" | "anim" }   pw:probe 3 blocks NORTH of you at eye height, facing SOUTH (anim = pw:t6 playing)
//   { rig: { mob, water?, baby?, fly?, event?, label? } }   the pen 5 blocks NORTH, one mob held at its centre facing SOUTH
//   { rigclear: true } / { probeclear: true }
// The runner clears the previous probe/pen before each new one, and clears everything at the end / on stop / reset.

const SHOTS_FRONT_LEFT = "SHOT 1 FRONT: stand where you are (south of it), eye level, look NORTH (the bar shows your facing).\n" +
  "SHOT 2 LEFT FLANK: walk round to the EAST side and look WEST at it (the head will turn toward you - judge the body from this shot, the head from shot 1).\n";
const SHOT_TOP = "SHOT 3 TOP: fly straight above it and look DOWN (crosshair on its back).\n";
const PASS_LINE = "PASS = shots taken AND it looks PATRIX (fine detail, not blocky) AND one animal in one piece. " +
  "FAIL vanilla? = the blocky low-res look · FAIL magenta? = solid magenta · FAIL parts? = parts apart, floating or missing · FAIL + note = anything else.";

// worst-first (audit §5), then the rest of RP-07; water = 2-deep pool; top = ask for the top-down shot too
const MOBS = [
  ["turtle", "minecraft:turtle", { water: true, top: true }, "the shell, the head out front, the flippers flat"],
  ["salmon", "minecraft:salmon", { water: true, top: true }, "one long body, fins, tail - no gaps between the parts"],
  ["pufferfish", "minecraft:pufferfish", { water: true, top: true }, "small when calm; /gamemode s at the edge puffs it (/gamemode c after)"],
  ["dolphin", "minecraft:dolphin", { water: true, top: true }, "body, nose, dorsal fin, flukes - one animal, nothing floating apart"],
  ["cod", "minecraft:cod", { water: true, top: true }, "one long body, fins, tail"],
  ["axolotl", "minecraft:axolotl", { water: true, top: true }, "head with gills, body, four legs, flat tail"],
  ["horse", "minecraft:horse", { top: true }, "neck rising from the body, head on the neck, mane, tail, four legs under the body"],
  ["donkey", "minecraft:donkey", { top: true }, "same build as the horse, longer ears"],
  ["mule", "minecraft:mule", { top: true }, "same build as the horse"],
  ["wolf", "minecraft:wolf", { top: true }, "body on the legs, head forward, tail behind"],
  ["fox", "minecraft:fox", { top: true }, "low body, head with ears, bushy tail behind"],
  ["polar bear", "minecraft:polar_bear", { top: true }, "big body on four legs, head out front"],
  ["goat", "minecraft:goat", {}, "body on legs, horns, the head out front"],
  ["panda", "minecraft:panda", {}, "round body, head, four legs"],
  ["rabbit", "minecraft:rabbit", {}, "small body, long ears, back legs folded"],
  ["llama", "minecraft:llama", {}, "body on the legs, the neck RISING from the front of the body, ears up"],
  ["trader llama", "minecraft:trader_llama", {}, "the llama shape (RP-07 1.4.11 fix) plus the blanket and strap"],
  ["pig", "minecraft:pig", {}, "body, snout, four legs"],
  ["cat", "minecraft:cat", {}, "slim body, head, tail behind"],
  ["ocelot", "minecraft:ocelot", {}, "as the cat"],
  ["sheep", "minecraft:sheep", {}, "wool body, head, four legs"],
  ["camel", "minecraft:camel", {}, "tall body, hump, long neck, head"],
  ["zombified piglin", "minecraft:zombie_pigman", {}, "upright: head, body, two arms, two legs"],
  ["cow", "minecraft:cow", {}, "body on legs, head, horns; the UDDER at the back underneath"],
  ["mooshroom", "minecraft:mooshroom", {}, "as the cow with mushrooms on the back"],
  ["chicken", "minecraft:chicken", {}, "body, head, beak, wattle, two legs, wings at the sides"],
  ["frog", "minecraft:frog", {}, "wide body, eyes on top, legs folded"],
  ["tadpole", "minecraft:tadpole", { water: true, top: true }, "head and a wriggling tail"],
  ["squid", "minecraft:squid", { water: true }, "body with tentacles hanging below"],
  ["glow squid", "minecraft:glow_squid", { water: true }, "as the squid, glowing"],
  ["tropical fish", "minecraft:tropicalfish", { water: true, top: true }, "~1/3-block fish, head/fins/tail attached; judge size from afar"],
];

function rigStep(i, [name, id, flags, look]) {
  const water = !!flags.water;
  const where = water ? "in a 2-deep POOL inside an invisible pen 5 blocks NORTH of you" : "in an invisible pen 5 blocks NORTH of you";
  return {
    id: `r${String(i + 1).padStart(2, "0")}`, group: "P0 RIG", title: `RIG: ${name.toUpperCase()}`,
    body: `A ${name} is held still ${where}, facing SOUTH (toward you). Look for: ${look}.\n` +
          (water ? "Look IN from outside the pool at eye level - do not swim in.\n" : "") +
          SHOTS_FRONT_LEFT + (flags.top ? SHOT_TOP : "") + PASS_LINE,
    setup: [{ rig: { mob: id, water, label: name } }],
  };
}

export const P0_STEPS = [
  { id: "q0", group: "P0 SETUP", title: "P0: STAND, FACE NORTH, HUD ON",
    body: "An open FLAT spot, daylight, nothing in front of you for 8 blocks to the north.\n" +
          "Face NORTH: the bar at the bottom shows your facing (the compass points to the world spawn, not north - use the bar).\n" +
          "Turn the HUD position readout ON (Settings > Video > Position) so every screenshot carries the coordinates.\n" +
          "Set Difficulty to EASY (Settings > Game) - the zombified piglin cannot spawn on Peaceful; the bar says NO MOB if a spawn fails.\n" +
          "Every mob is rigged as an ADULT (the runner grows it up).\n" +
          "Each step from here sets itself up: a probe or a mob appears in front of you; take the shots it names; tap the clicker; PASS = shots taken.\n" +
          "At the end everything is removed by the runner. Then upload all the screenshots to the Drive (Packs > Screenshots-P0) and tell Claude.",
    setup: [{ daytime: "noon" }, { weather: "clear" }] },

  { id: "q1", group: "P0 PROBE", title: "PROBE: THE ROTATION-LAW CHART (STATIC)",
    body: "A floating colour chart is 3 blocks NORTH of you at eye height, its YELLOW nose toward you.\n" +
          "SHOT A FRONT: as you stand, facing NORTH, the whole chart in frame.\n" +
          "SHOT B EAST SIDE: walk to its EAST side, look WEST at it.\n" +
          "SHOT C TOP: fly straight above it, look DOWN with the crosshair on the yellow nose.\n" +
          "What each colour answers (say which you saw, or send the shots): RED cube = your RIGHT / your LEFT? · GREEN bar top leans toward RED / toward BLUE? · " +
          "ORANGE bar's free end comes TOWARD you / goes AWAY? · CYAN bar tip (pointing at you) DIPS DOWN / RISES? · " +
          "MAGENTA bar leans toward you AND to your left / toward you only?\n" +
          "PASS = shots A, B, C taken. FAIL + note = no chart appeared (then the RP or BP 0.2.2 is not attached).",
    setup: [{ probe: "static" }] },
  { id: "q2", group: "P0 PROBE", title: "PROBE: THE SAME CHART, ANIMATED",
    body: "The chart is replaced by one with an animation playing.\n" +
          "SHOT D FRONT: as you stand, facing NORTH.\n" +
          "Compare with shot A: does the CYAN bar dip TWICE as far (about 60 degrees instead of 30)? does the GREEN bar sit HALF A BLOCK HIGHER?\n" +
          "PASS = shot D taken. FAIL + note = no change at all / the chart vanished.",
    setup: [{ probe: "anim" }] },

  ...MOBS.map((m, i) => rigStep(i, m)),

  { id: "q9", group: "P0 DONE", title: "P0: ALL CLEAR - UPLOAD THE SHOTS",
    body: "The probe and the pen are removed and the ground is restored.\n" +
          "Upload every screenshot to the Drive: Packs > Screenshots-P0 (any folder is fine - tell Claude the name), then copy the content log (Settings > Creator > Content Log History > Copy to Clipboard).\n" +
          "PASS = uploaded (or about to).",
    setup: [{ probeclear: true }, { rigclear: true }] },
];

export const P0_INDEX = Object.fromEntries(P0_STEPS.map((s, i) => [s.id, i]));
export const P0_MOBS = MOBS.map(([name, id, flags]) => ({ name, id, water: !!flags.water, top: !!flags.top }));
