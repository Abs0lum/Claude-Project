// pw_testrunner_p23.js — lineup "p23" TREES T2–T5 witness round (PW-TestRunner BP v0.5.16, D-C502/D-C503, 10-03).
// /scriptevent pw:test start p23 — BP-02 v1.3.209 + RP-01 v1.3.118: roots for acacia / cherry / mangrove, no floating
// trees, forests of our templates in every data-driven biome, the exact template falling set (T4), saplings that grow our
// templates with the root on the sapling (T5). BDS proved every mechanism except the one that needs a human: a player's
// own break (T4) — and the look of a forest is his to judge.

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
const PASSN = "PASS = right. FAIL + note = what is off (and where). Notes have 3 boxes - use them all if you need to.";
const SAPS = ["minecraft:oak_sapling", "minecraft:birch_sapling", "minecraft:spruce_sapling", "minecraft:jungle_sapling", "minecraft:acacia_sapling", "minecraft:dark_oak_sapling", "minecraft:cherry_sapling", "minecraft:pale_oak_sapling", "minecraft:mangrove_propagule"];
// nine saplings in a ring 14 blocks out (relative to the player: the runner resolves ~ for setup commands)
const plantCmds = SAPS.map((s, i) => { const a = (i / SAPS.length) * Math.PI * 2; const dx = Math.round(Math.cos(a) * 14), dz = Math.round(Math.sin(a) * 14); return `scriptevent pw:treegrow plant ~${dx} ~ ~${dz} ${s}`; });

const Q0 = { id: "q0", group: "P23 SETUP", title: "P23 TREES: BP-02 1.3.214 + RP-01 1.3.118, A FRESH WORLD OR FRESH CHUNKS, SURVIVAL AXE READY",
  body: lines("Packs: BP-02 v1.3.214 (replaces 1.3.207 … 212) + RP-01 v1.3.118 (replaces 1.3.117); PW-TestRunner BP v0.5.20 at the bottom. " +
    "Content log after load: '[PW-VERSION] BP-02 v1.3.214' and '[TREEGROW] BOOT v1.3.214'.\n" +
    "Trees are made when chunks are made: use a NEW world, or fly far (2,000+ blocks) into land you have never loaded. CREATIVE for now; an iron axe in the hotbar for the felling steps.\n" +
    "PASS = ready. FAIL + note = versions or log differ."),
  setup: [{ daytime: "noon" }, { weather: "clear" }, { cmd: ["gamemode creative @s"] }] };

const STEPS23 = [
  { id: "t01", group: "P23 FORESTS", title: "A FRESH FOREST OR TAIGA: EVERY TREE OURS, NONE FLOATING",
    body: lines("Fly over a forest, birch forest or taiga you have never loaded.\n" +
      "Look for: every tree is one of ours (round dodecagon trunks on oak / birch / spruce / jungle, our leaves; square trunks only on acacia / cherry / mangrove / the elders); " +
      "NO tree standing on air or on water (land beside each trunk, walk up to five); the density reads as a forest - say if too dense, too sparse, or the mix is wrong (forests are oak 4 : birch 1).\n" +
      "SHOT from above (40 blocks up) and one at ground level.\n" + PASSN),
    setup: [{ daytime: "noon" }] },
  { id: "t02", group: "P23 FORESTS", title: "A GROVE (SNOWY MOUNTAIN SPRUCES): VANILLA BY DESIGN - CONFIRM, DO NOT FAIL IT",
    body: lines("Find a snowy mountain slope with spruces (a GROVE) if one is near. Those trees are vanilla: the engine grows them from code no pack can reach (three probes). " +
      "This step only confirms what you see so we agree on the ruling (accept there / a scripted sweep / weight our biomes).\n" +
      "PASS = vanilla spruces there, as expected. Note = your preference."),
    setup: [{ daytime: "noon" }] },
  { id: "t03", group: "P23 ROOTS", title: "THE ROOT BLOCK: BREAK ONE AT A TREE'S BASE",
    body: lines("Still CREATIVE. At one of our trees, the lowest trunk block is the ROOT (it looks like the log). Break it: it must sound like wood, drop the vanilla log, and the tree above must NOT fall (creative never fells).\n" +
      "Do the same at an acacia or cherry or mangrove if one is near (their roots are new).\n" + PASSN),
    setup: [{ daytime: "noon" }] },
  { id: "t04", group: "P23 FELLING", title: "SURVIVAL: CHOP A WORLDGEN TREE - THE WHOLE TREE AND ONLY THAT TREE FALLS",
    body: lines("SURVIVAL with the iron axe. Pick one of our trees that has a NEIGHBOUR touching its canopy. Chop the trunk block just above the root.\n" +
      "Look for: the tree falls whole (trunk + branches + its leaves) - the exact template, no stray logs left hanging; the NEIGHBOUR keeps all its leaves and logs; the root stays as the stump; the fall direction is downhill / away from you as before.\n" +
      "Then chop a second tree of another species. VIDEO of one fall if you can.\n" + PASSN),
    setup: [{ daytime: "noon" }, { cmd: ["gamemode survival @s"] }, { give: [["iron_axe", 1]] }] },
  { id: "t05", group: "P23 FELLING", title: "A BRANCH CUT AND A STUMP CUT NEVER FELL",
    body: lines("Still SURVIVAL. On one of our old / elder trees cut a BRANCH log (one that leaves the trunk sideways): only that log breaks. Then on a stump left by t04, break a remaining stump log: nothing falls.\n" + PASSN),
    setup: [{ daytime: "noon" }] },
  { id: "t06", group: "P23 SAPLINGS", title: "NINE SAPLINGS PLANTED AROUND YOU - WAIT TWO MINUTES",
    body: lines("Back in CREATIVE, standing on open flat ground. Nine saplings are planted in a ring 14 blocks out (oak, birch, spruce, jungle, acacia, dark oak, cherry, pale oak, mangrove propagule), each due to grow NOW; the growth engine checks every 2 seconds.\n" +
      "Within a minute each becomes one of our young trees (dark oak and pale oak: elders) with its ROOT exactly on the sapling cell. Walk the ring.\n" +
      "Look for: every sapling grew; the trunk starts where the sapling stood (not shifted sideways); none overlaps another; they face different ways.\n" +
      "SHOT of the ring from above.\n" + PASSN),
    setup: [{ daytime: "noon" }, { cmd: ["gamemode creative @s"] }, { cmd: plantCmds }] },
  { id: "t07", group: "P23 SAPLINGS", title: "A GROWN TREE FELLS LIKE A WORLDGEN ONE",
    body: lines("SURVIVAL. Chop one of the trees you just grew, just above the root: it falls whole; the root stays.\n" +
      "Then plant a sapling by hand (it grows in 2-3 minutes on its own - leave it; q9 checks nothing about it).\n" + PASSN),
    setup: [{ daytime: "noon" }, { cmd: ["gamemode survival @s"] }, { give: [["iron_axe", 1], ["oak_sapling", 4]] }] },
];
const Q9 = { id: "q9", group: "P23 DONE", title: "P23: UPLOAD",
  body: lines("CREATIVE restored. Upload the shots / video and copy the content log (Settings > Creator > Content Log History > Copy to Clipboard), or /scriptevent pw:test report p23.\n" +
    "PASS = uploaded (or about to)."),
  setup: [{ cmd: ["gamemode creative @s"] }, { daytime: "noon" }] };

export const P23_STEPS = [Q0, ...STEPS23, Q9];
export const P23_INDEX = Object.fromEntries(P23_STEPS.map((s, i) => [s.id, i]));
