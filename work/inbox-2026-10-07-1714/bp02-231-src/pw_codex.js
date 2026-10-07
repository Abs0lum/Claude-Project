import { world } from "@minecraft/server";
import { ActionFormData, MessageFormData } from "@minecraft/server-ui";
// ============================================================================
// BUILDER'S CODEX v2 — regenerated whole (T18 splice ate v1's handlers).
// Instrumented: every trigger and cancelation speaks. itemUseOn = touch fallback.
// ============================================================================
const say = (m) => { try { world.sendMessage(`\u00a79[CODEX]\u00a7r ${m}`); } catch {} };
const CATALOG = {
 "Roofs": [
  [
   "Roof45 Oak",
   "pw:roof45_oak",
   "[PPP] / [PPP] (P=oak planks) -> 6",
   "Rule A: run-meet folds into a Hip."
  ],
  [
   "Roof45 Ridge Oak",
   "pw:roof45_ridge_oak",
   "2x roof45 oak -> 2",
   "Rule A: run-meet folds into a Hip."
  ],
  [
   "Roof45 Ridge Spruce",
   "pw:roof45_ridge_spruce",
   "2x roof45 spruce -> 2",
   "Rule A: run-meet folds into a Hip."
  ],
  [
   "Roof45 Spruce",
   "pw:roof45_spruce",
   "[PPP] / [PPP] (P=spruce planks) -> 6",
   "Rule A: run-meet folds into a Hip."
  ],
  [
   "Roof63 Lower Oak",
   "pw:roof63_lower_oak",
   "1x roof45 oak + 1x oak planks -> 2",
   "PW-C2: Upper auto-places."
  ],
  [
   "Roof63 Lower Spruce",
   "pw:roof63_lower_spruce",
   "1x roof45 spruce + 1x spruce planks -> 2",
   "PW-C2: Upper auto-places."
  ],
  [
   "Roof63 Upper Oak",
   "pw:roof63_upper_oak",
   "1x roof45 oak + 1x stick -> 2",
   ""
  ],
  [
   "Roof63 Upper Spruce",
   "pw:roof63_upper_spruce",
   "1x roof45 spruce + 1x stick -> 2",
   ""
  ],
  [
   "Roof Gusset Lower Oak",
   "pw:roof_gusset_lower_oak",
   "2x roof63 lower oak -> 2",
   "PW-C2: Upper auto-places. Keystone fold, 2-cell climb."
  ],
  [
   "Roof Gusset Lower Spruce",
   "pw:roof_gusset_lower_spruce",
   "2x roof63 lower spruce -> 2",
   "PW-C2: Upper auto-places. Keystone fold, 2-cell climb."
  ],
  [
   "Roof Gusset Upper Oak",
   "pw:roof_gusset_upper_oak",
   "2x roof63 upper oak -> 2",
   ""
  ],
  [
   "Roof Gusset Upper Spruce",
   "pw:roof_gusset_upper_spruce",
   "2x roof63 upper spruce -> 2",
   ""
  ],
  [
   "Roof Hip Oak",
   "pw:roof_hip_oak",
   "[PP] / [P ] (P=oak planks) -> 2",
   "Rule C: 4 hips crown a Pyramidion. Rule F: auto-climb."
  ],
  [
   "Roof Hip Spruce",
   "pw:roof_hip_spruce",
   "[PP] / [P ] (P=spruce planks) -> 2",
   "Rule C: 4 hips crown a Pyramidion. Rule F: auto-climb."
  ],
  [
   "Roof Pyramidion Oak",
   "pw:roof_pyramidion_oak",
   "[ P ] / [PPP] (P=oak planks) -> 2",
   ""
  ],
  [
   "Roof Pyramidion Spruce",
   "pw:roof_pyramidion_spruce",
   "[ P ] / [PPP] (P=spruce planks) -> 2",
   ""
  ],
  [
   "Roof Ridge End Oak",
   "pw:roof_ridge_end_oak",
   "[PPP] / [P P] (P=oak planks) -> 2",
   ""
  ],
  [
   "Roof Ridge End Spruce",
   "pw:roof_ridge_end_spruce",
   "[PPP] / [P P] (P=spruce planks) -> 2",
   ""
  ]
 ],
 "Exterior Construction Walls": [
  [
   "Angled Wall",
   "pw:angled_wall",
   "(no recipe - /give or state cycle)",
   "13 materials via pw:material."
  ]
 ],
 "Interior Construction Walls": [
  [
   "Wall Prism",
   "pw:wall_prism",
   "[ P] / [PP] (P=oak planks) -> 2",
   "Rule H: interior liner twin auto-places. 13 materials (oak default)."
  ]
 ],
 "Interior Room Walls": [
  [
   "Room Wall",
   "pw:room_wall",
   "[P] / [P] / [P] (P=oak planks) -> 6",
   "Rule D: back-to-back -> full block. Rule E: perpendicular -> Corner."
  ],
  [
   "Room Wall Corner",
   "pw:room_wall_corner",
   "3x room wall -> 2",
   "Rule D: back-to-back -> full block. Rule E: perpendicular -> Corner."
  ]
 ],
 "Crown/Caps": [
  [
   "Crown Ring Oak",
   "pw:crown_ring_oak",
   "3x roof45 oak + 1x stone -> 4",
   "Rule G: corners self-form; ring closure = the keystone event."
  ],
  [
   "Crown Ring Spruce",
   "pw:crown_ring_spruce",
   "3x roof45 spruce + 1x stone -> 4",
   "Rule G: corners self-form; ring closure = the keystone event."
  ],
  [
   "Crown Ring Stone",
   "pw:crown_ring_stone",
   "3x stone + 1x stone slab -> 4",
   "Rule G: corners self-form; ring closure = the keystone event."
  ]
 ],
 "Terracotta Tiles": [
  [
   "Black Terracotta Tiles",
   "pw:black_terracotta_tiles",
   "[TT] / [TT] (P=black terracotta) -> 4",
   ""
  ],
  [
   "Blue Terracotta Tiles",
   "pw:blue_terracotta_tiles",
   "[TT] / [TT] (P=blue terracotta) -> 4",
   ""
  ],
  [
   "Brown Terracotta Tiles",
   "pw:brown_terracotta_tiles",
   "[TT] / [TT] (P=brown terracotta) -> 4",
   ""
  ],
  [
   "Cyan Terracotta Tiles",
   "pw:cyan_terracotta_tiles",
   "[TT] / [TT] (P=cyan terracotta) -> 4",
   ""
  ],
  [
   "Gray Terracotta Tiles",
   "pw:gray_terracotta_tiles",
   "[TT] / [TT] (P=gray terracotta) -> 4",
   ""
  ],
  [
   "Green Terracotta Tiles",
   "pw:green_terracotta_tiles",
   "[TT] / [TT] (P=green terracotta) -> 4",
   ""
  ],
  [
   "Light Blue Terracotta Tiles",
   "pw:light_blue_terracotta_tiles",
   "[TT] / [TT] (P=light blue terracotta) -> 4",
   ""
  ],
  [
   "Light Gray Terracotta Tiles",
   "pw:light_gray_terracotta_tiles",
   "[TT] / [TT] (P=light gray terracotta) -> 4",
   ""
  ],
  [
   "Lime Terracotta Tiles",
   "pw:lime_terracotta_tiles",
   "[TT] / [TT] (P=lime terracotta) -> 4",
   ""
  ],
  [
   "Magenta Terracotta Tiles",
   "pw:magenta_terracotta_tiles",
   "[TT] / [TT] (P=magenta terracotta) -> 4",
   ""
  ],
  [
   "Orange Terracotta Tiles",
   "pw:orange_terracotta_tiles",
   "[TT] / [TT] (P=orange terracotta) -> 4",
   ""
  ],
  [
   "Pink Terracotta Tiles",
   "pw:pink_terracotta_tiles",
   "[TT] / [TT] (P=pink terracotta) -> 4",
   ""
  ],
  [
   "Purple Terracotta Tiles",
   "pw:purple_terracotta_tiles",
   "[TT] / [TT] (P=purple terracotta) -> 4",
   ""
  ],
  [
   "Red Terracotta Tiles",
   "pw:red_terracotta_tiles",
   "[TT] / [TT] (P=red terracotta) -> 4",
   ""
  ],
  [
   "Terracotta Tiles",
   "pw:terracotta_tiles",
   "[TT] / [TT] (P=hardened clay) -> 4",
   ""
  ],
  [
   "White Terracotta Tiles",
   "pw:white_terracotta_tiles",
   "[TT] / [TT] (P=white terracotta) -> 4",
   ""
  ],
  [
   "Yellow Terracotta Tiles",
   "pw:yellow_terracotta_tiles",
   "[TT] / [TT] (P=yellow terracotta) -> 4",
   ""
  ]
 ],
 "Workshop": [
  [
   "Builders Codex",
   "pw:builders_codex",
   "1x book + 1x oak planks -> 1",
   ""
  ],
  [
   "Builders Table",
   "pw:builders_table",
   "[###] / [PTP] / [PPP] (P=paper) -> 1",
   ""
  ],
  [
   "Rotation Probe",
   "pw:rotation_probe",
   "(no recipe - /give or state cycle)",
   "COMPASS: glyph faces read every rotation; 8 modes x 4 facings compose."
  ]
 ]
};
let codexBusy = false;
function tryOpen(player, via) {
  say(`trigger: ${via} \u2014 opening\u2026`);
  if (codexBusy) { say("busy \u2014 previous form still pending"); return; }
  codexBusy = true;
  Promise.resolve(openRoot(player)).catch((e) => say(`open error: ${e}`)).finally(() => { codexBusy = false; });
}
world.afterEvents.itemUse.subscribe((ev) => {
  try {
    if (!ev.itemStack || ev.itemStack.typeId !== "pw:builders_codex") return;
    tryOpen(ev.source, "itemUse(air)");
  } catch (e) { say(`itemUse error: ${e}`); }
});
if (world.afterEvents.itemUseOn) world.afterEvents.itemUseOn.subscribe((ev) => {
  try {
    if (!ev.itemStack || ev.itemStack.typeId !== "pw:builders_codex") return;
    tryOpen(ev.source, "itemUseOn(block)");
  } catch (e) { say(`itemUseOn error: ${e}`); }
});
async function openRoot(player) {
  try {
    const fams = Object.keys(CATALOG);
    const f = new ActionFormData().title("Builder's Codex").body("The AbsolutRealism construction catalog.");
    for (const name of fams) f.button(`${name} (${CATALOG[name].length})`);
    const r = await f.show(player);
    if (r.canceled) { say(`root canceled: ${r.cancelationReason ?? "user"}`); return; }
    await openFamily(player, fams[r.selection]);
  } catch (e) { say(`root form error: ${e}`); }
}
async function openFamily(player, fam) {
  try {
    const f = new ActionFormData().title(fam).body("Pick a piece.");
    for (const e of CATALOG[fam]) f.button(e[0]);
    f.button("\u00ab Back");
    const r = await f.show(player);
    if (r.canceled) { say(`family canceled: ${r.cancelationReason ?? "user"}`); return; }
    if (r.selection === CATALOG[fam].length) return openRoot(player);
    const e = CATALOG[fam][r.selection];
    const body = [`ID: ${e[1]}`, ``, `Recipe: ${e[2]}`, e[3] ? `` : null, e[3] || null].filter((x) => x !== null).join("\n");
    const m = new MessageFormData().title(e[0]).body(body).button1("\u00ab Family").button2("Done");
    const mr = await m.show(player);
    if (!mr.canceled && mr.selection === 0) return openFamily(player, fam);
  } catch (e) { say(`family form error: ${e}`); }
}
console.warn("[CODEX] module loaded (v3, API-guarded)");
