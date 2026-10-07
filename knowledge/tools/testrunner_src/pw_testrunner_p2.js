// pw_testrunner_p2.js — lineup "p2" (PW-TestRunner BP v0.3.0, D-C264): the REALM half of the ownership-wave witness —
// /scriptevent pw:test start p2   (needs PW-StripMine BP + RP in the world: the Naturalist creatures live there)
//   S  size stations (D-C263 size curve): beetle · ant · sparrow · rat held in the pen next to a 1-block white post, plus a hit test.
//   R  three Naturalist creatures rendered from PW-StripMine RP alone (the ownership wave moved every sf_nba client file there):
//      deer · alligator · hammer-head shark (water pen). PASS = textured and animated; FAIL = magenta / invisible / vanilla-shaped.
// Every step first clears the station volume (feet level and up, never the ground) and the pen.
const CLEAR = ["fill ~-3 ~ ~-9 ~3 ~5 ~-2 air"];
const SIZES = [
  ["beetle", "sf_nba:beetle", "about 40 cm long - a bit under half the post's height"],
  ["ant", "sf_nba:ant", "about 22 cm - a quarter of the post"],
  ["sparrow", "sf_nba:sparrow", "a small bird, about 47 cm with the wings"],
  ["rat", "sf_nba:rat", "about 57 cm nose to tail-tip - over half the post"],
];
function sizeStep(i, [name, id, look]) {
  return { id: `s${String(i + 1).padStart(2, "0")}`, group: "P2 SIZES", title: `SIZE: ${name.toUpperCase()}`,
    body: `A ${name} is held in the pen 5 blocks NORTH next to a 1-BLOCK WHITE POST (1 m). Expected: ${look}.\n` +
          "Then walk up and HIT it once (creative hits register): the hitbox should be the creature, not the air around it - say if you have to aim at empty space.\n" +
          "PASS = size as expected AND hittable on its body. FAIL + note = too big / too small / hitbox off. (If the bar says NO MOB, this world has no PW-StripMine BP.)",
    setup: [{ cmd: CLEAR }, { rig: { mob: id, label: name } }, { cmd: ["setblock ~1 ~ ~-4 white_wool"] }] };
}
const RENDERS = [
  ["deer", "sf_nba:deer", false, "brown coat, antlers, long legs - about 2 m, taller than you"],
  ["alligator", "sf_nba:alligator", false, "dark scaled hide, long jaw, low body - about 3.5 m long"],
  ["hammer-head shark", "sf_nba:hammer_head_shark", true, "grey, the flat hammer head, swimming in the pool"],
];
function renderStep(i, [name, id, water, look]) {
  return { id: `r${String(i + 1).padStart(2, "0")}`, group: "P2 NATURALIST", title: `RIG: ${name.toUpperCase()} (from PW-StripMine RP)`,
    body: `A ${name} is held in the ${water ? "POOL" : "pen"} 5 blocks NORTH, facing SOUTH. Look for: ${look}.\n` +
          "SHOT 1 FRONT: as you stand, look NORTH. SHOT 2 LEFT FLANK: from the EAST side, look WEST.\n" +
          "PASS = textured and animated (breathing / tail / legs move). FAIL magenta? = pink-black checker · FAIL parts? = invisible or missing parts · FAIL vanilla? = a vanilla-shaped stand-in · FAIL + note.",
    setup: [{ cmd: CLEAR }, { rig: { mob: id, label: name, water } }] };
}
export const P2_STEPS = [
  { id: "q0", group: "P2 SETUP", title: "P2 (REALM): CREATIVE, FLAT, FACE NORTH",
    body: "On the Realm with PW-StripMine BP + RP active. Creative mode, an open FLAT spot with nothing for 10 blocks NORTH, daylight, HUD position ON.\n" +
          "Each step pens its own creature 5 blocks north; the runner clears it as it goes and at the end.\nType /scriptevent pw:stats off first so the content log stays readable.",
    setup: [{ daytime: "noon" }, { weather: "clear" }] },
  ...SIZES.map((s, i) => sizeStep(i, s)),
  ...RENDERS.map((r, i) => renderStep(i, r)),
  { id: "q9", group: "P2 DONE", title: "P2: ALL CLEAR - UPLOAD THE SHOTS",
    body: "The pen, the pool and the post are removed. Upload the screenshots to the Drive and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard).\nPASS = uploaded (or about to).",
    setup: [{ rigclear: true }, { cmd: CLEAR }] },
];
export const P2_INDEX = Object.fromEntries(P2_STEPS.map((s, i) => [s.id, i]));
export const P2_SIZES = SIZES.map(([name, id]) => ({ name, id }));
export const P2_RENDERS = RENDERS.map(([name, id, water]) => ({ name, id, water }));
