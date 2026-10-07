// pw_testrunner_p17.js — lineup "p17" LEAF FIXES + THE CULLING PROBE (PW-TestRunner BP v0.5.3, D-C350; his p16 results 20:52 CT 09-30).
// /scriptevent pw:test start p17 — BP-02 v1.3.198 + RP-01 v1.3.107: the p16 FAILs (falling canopy drawn as solid slabs, shears giving the
// old vanilla leaf block) and his picks (256 px leaves + MERS 64 everywhere, picture turns off, no relook sweep), then the CULLING PROBE
// that decides how the z-clipping fix is written: does a block's culling rule turn with the block's quarter turn?
// The tree jobs are the p15 ones (runLeafSetup in pw_testrunner_p15.js).

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
const NEAR = { leafarea: { name: "pw_p17_near", box: [-40, -5, -40, 40, 40, 2] } };
const T = (sp, age, dx, dz, extra) => ({ leaftree: { sp, age, dx, dz, keep: true, ...(extra || {}) } });
const PASSN = "PASS = right. FAIL + note = what is off (and where). Notes now have 3 boxes - use them all if you need to.";

// the culling probe: pairs of pw:cullprobe blocks (each face its own colour + letter: N red, E blue, S yellow, W green, top white,
// bottom black). Each pair = two blocks with the SAME quarter turn q. East pairs: A, then B one block EAST. South pairs: A, then B
// one block SOUTH. The rule culls a block's EAST face when the block east of it is a probe too, and its SOUTH face likewise.
//   If the rule turns with the block: every pair looks like one solid 2-block bar - no holes, no flicker on the shared face.
//   If it does not: pairs with q 1-3 show a HOLE (you see inside / the sky) on an OUTER side, and the shared face flickers.
export const PROBE_X = [-9, -5, -1, 3];                       // q 0..3, left to right, 4 blocks apart
export const PROBE_EAST_Z = -6, PROBE_SOUTH_Z = -12;
function probeCmds() {
  const c = [`fill ~-12 ~ ~-16 ~8 ~3 ~-3 air`];
  PROBE_X.forEach((x, q) => {
    c.push(`setblock ~${x} ~1 ~${PROBE_EAST_Z} pw:cullprobe ["pw:q"=${q}]`, `setblock ~${x + 1} ~1 ~${PROBE_EAST_Z} pw:cullprobe ["pw:q"=${q}]`);
    c.push(`setblock ~${x} ~1 ~${PROBE_SOUTH_Z} pw:cullprobe ["pw:q"=${q}]`, `setblock ~${x} ~1 ~${PROBE_SOUTH_Z + 1} pw:cullprobe ["pw:q"=${q}]`);
  });
  return c;
}

const Q0 = { id: "q0", group: "P17 SETUP", title: "P17 LEAF FIXES: COPY OF THE TEST WORLD, PHONE HOSTS, PS5 JOINS (VIBRANT VISUALS), FACE NORTH",
  body: lines("Packs (on the phone): BP-02 v1.3.198 + RP-01 v1.3.107 (they replace v1.3.197 / v1.3.106 - always together), PW-TestRunner BP v0.5.4 or newer at the bottom, " +
    "PW-TestRunner RP v0.6.0 at the TOP (replaces v0.5.0). Use a COPY of the test world; host on the phone, join on the PS5 with Vibrant Visuals ON.\n" +
    "Content log after load: '[PW-VERSION] BP-02 v1.3.198' and 'PW Test Runner BP v0.5.4' (or newer).\n" +
    "Stand on big FLAT open ground (40 blocks clear each side and NORTH) and FACE NORTH.\nPASS = ready. FAIL + note = versions or log differ."),
  setup: [{ daytime: "noon" }, { weather: "clear" }] };

const STEPS17 = [
  { id: "f01", group: "P17 FIXES", title: "FELLING (SURVIVAL): THE FALLING CANOPY IS LEAFY AGAIN",
    body: lines("SURVIVAL with an iron axe. An OAK grows 12 blocks NORTH and a BIRCH 12 blocks NORTH-EAST. Chop the bottom log of each.\n" +
      "Look for: the falling crown looks like LEAVES (see-through, leafy) while it falls - no solid green slabs, no thick green rods.\n" +
      "SHOT or VIDEO of a fall.\n" + PASSN),
    setup: [NEAR, { leafclear: { box: [-12, 26, -26, -2], h: 30 } }, { daytime: "noon" }, T("oak", "mature", 0, -14), T("birch", "mature", 16, -14),
      { cmd: ["gamemode survival @s"] }, { give: [["iron_axe", 1]] }] },
  { id: "f02", group: "P17 FIXES", title: "SHEARS GIVE OUR NEW LEAF BLOCK",
    body: lines("Still SURVIVAL, now with shears. An OAK and a SPRUCE grow 10 blocks NORTH.\n" +
      "1) Shear a few leaves of each: the dropped block and the one in your hotbar should look like the NEW leaves (not the old dark low-detail cube).\n" +
      "2) Place them: each placed leaf gets its look at once.\n" + PASSN),
    setup: [NEAR, { leafclear: { box: [-14, 14, -22, -2], h: 30 } }, { daytime: "noon" }, T("oak", "mature", -6, -12), T("spruce", "mature", 6, -12),
      { cmd: ["gamemode survival @s"] }, { give: [["shears", 1]] }] },
  { id: "f03", group: "P17 LEAVES 256", title: "THE 256 LEAVES ON REAL TREES + Z-CLIPPING GONE",
    body: lines("Back in CREATIVE. Four of our trees NORTH: OAK old, BIRCH old, SPRUCE old, CHERRY. Every leaf now uses the 256 picture with the 64 MERS map (your p16 pick).\n" +
      "Look for: the same sharpness you picked in p16; nothing missing; colours right; and NO z-clipping: walk up close and move around - no flicker where leaves meet (every leaf is now nudged a hair so touching leaves never share a plane).\n" + PASSN),
    setup: [{ cmd: ["gamemode creative @s"] }, NEAR, { leafclear: { box: [-36, 36, -24, -2], h: 30 } }, { daytime: "noon" },
      T("oak", "old", -27, -12), T("birch", "old", -9, -12), T("spruce", "old", 9, -12), { leaftree: { sp: "cherry", dx: 27, dz: -12, keep: true } }] },
  { id: "z01", group: "P17 CULLING PROBE", title: "THE CULLING PROBE: 8 PAIRS OF COLOURED BLOCKS",
    body: lines("Eight PAIRS of coloured test blocks NORTH of you (faces: North RED, East BLUE, South YELLOW, West GREEN, top WHITE, bottom BLACK). " +
      "From LEFT to RIGHT the 4 pairs in each row are turned 0, 1, 2 and 3 quarter turns.\n" +
      "Near row (6 blocks north): side-by-side pairs (the 2nd block is EAST of the 1st). Far row (12 blocks north): front-to-back pairs (the 2nd block is SOUTH, nearer you).\n" +
      "Walk ALL the way around each pair, look at every side and the top. Look for: a HOLE in a side (you see into the block or through to the sky) and FLICKER where two blocks touch.\n" +
      "Note it like: 'near 1 hole east, far 3 flicker' (pairs counted 1-4 from the left). SHOT of each row from both sides. (This decides how the leaves can skip drawing hidden faces - a speed-up, after this test.)\n" +
      "PASS = all 8 pairs solid, no holes, no flicker. FAIL + note = which pairs and sides."),
    setup: [NEAR, { daytime: "noon" }, { cmd: probeCmds() }, { leafmark: { dx: -2, dz: -8, r: 7, h: 4 } }] },
];
const Q9 = { id: "q9", group: "P17 DONE", title: "P17: ALL CLEAR - UPLOAD",
  body: lines("Every tree this run grew and the probe blocks are cleared, the ticking area is removed, CREATIVE is restored. Give it 15 seconds.\n" +
    "Upload any shots and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or /scriptevent pw:test report p17.\nPASS = uploaded (or about to)."),
  setup: [{ cmd: ["gamemode creative @s"] }, { leafreset: { areas: ["pw_p17_near"], box: [-38, 38, -38, -2], h: 40 } }, { daytime: "noon" }] };

export const P17_STEPS = [Q0, ...STEPS17, Q9];
export const P17_INDEX = Object.fromEntries(P17_STEPS.map((s, i) => [s.id, i]));
