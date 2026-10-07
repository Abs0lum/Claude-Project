// pw_testrunner.js — PW TEST RUNNER (PW-TestRunner BP v0.3.4 — a job-only pack, attached at the BOTTOM of the list; D-C249, 2026-09-27)
// v0.5.11 (D-C417, 10-01): p20 / p21 rebuilt for RP-07 1.4.43 + RP-04 1.3.144 (his log 3).
// v0.5.10 (D-C416, 10-01): p20 / p21 rebuilt for RP-07 1.4.42 + RP-06 1.4.28 (his content log 2).
// v0.5.9 (D-C412, 10-01): p20 / p21 rebuilt for RP-07 1.4.41 + RP-06 1.4.27 (his content log 1); p21 steps name movement-only clips.
// v0.5.8 (D-C398, 10-01): THE JUDGING PASS — lineups "p20" (every entity, sized pens, unsafe ones listed not summoned), "p21" (every creature x
//   every animation: a row of copies, each PLAYING one clip, name tag = the clip), "bump" (the MR3 bump-map test, his BT1: its own lineup);
//   the rig plays animations (spec.play); + the sweep (48-block square) and BACK rebuilds the previous step's pen (his B1).
// v0.5.7 (D-C355, 09-30): p18 / p19 name RP-07 1.4.34 + StripMine BP 1.3.9 (the models fix: 1.4.32 / 1.4.33 ported animals were invisible); p19 adds the WWA seal.
// v0.5.6 (D-C353, 09-30): lineup "p19" — THE PICKS PARADE (menagerie wave P3: RP-07 1.4.33 + StripMine BP 1.3.8): every version he kept, by animal, name tags "Name (PACK)", + gorilla / boar / bear pens with ours; p18 q0 names the new packs.
// v0.5.5 (D-C351, 09-30): lineup "p18" (34 steps) — the NEW ANIMALS parade (menagerie wave P1: RP-07 1.4.32 + StripMine BP 1.3.7).
// v0.5.4 (D-C350, 09-30): 0.5.3 packaged, never delivered, retired; p17 f03 checks the z-clipping is gone (the leaf nudge).
// v0.5.3 (D-C350, 09-30): lineup "p17" (6 steps) — the p16 leaf fixes (BP-02 1.3.198 + RP-01 1.3.107) + the CULLING PROBE; notes get 3 boxes.
// v0.5.2 (D-C348, 09-30): p16 m01-m10, the 128 vs 256 leaf comparison (three copies per tree, same looks leaf for leaf, 22 pw:t256* test blocks).
// v0.5.1 (D-C347, 09-30): p16 targets BP-02 1.3.197 + RP-01 1.3.106, + n13 old trees (relook sweep); planted tree boxes survive a relog.
// v0.5.0 (D-C346, 09-30): lineup "p16" (14 steps) — the LEAF ROLLOUT test for BP-02 1.3.196 + RP-01 1.3.105; placeprobe + chop actions.
// v0.5.0 (D-C344, 09-30): trees grow via Dimension.placeFeature first, then /place feature; each refusal reason is logged once.
// v0.4.9 (D-C338, 09-30): independent-check fixes: whole-box leaf scan (diagonal fancy branches), ticking areas made in the job,
//   q9 clears every planted box before dropping the ticking areas.
// v0.4.8 (D-C336, 09-30): p15 = OUR trees, one species-AGE per step (21 steps: oak/birch/spruce/jungle young..elder, dark + pale oak
//   elders, acacia, mangrove, cherry, azalea); one tree grown per step, the others exact /clone copies (same shape for today vs pilot).
// v0.4.7 (D-C333, 09-30): p15 recognises BP-02 trunks (pw:<wood>_young|mature|old|elder), queues step jobs, anchors trees at step start.
// v0.4.6 (D-C332, 09-30): lineup "p15" (16 steps) — the LEAF PILOT: 11 Patrix 26.2 species on real trees (the game's own
//   tree features, leaves swapped for pw:pilot_* by position), today vs pilot vs biome colour, random turns, noon shade, far swap, grove.
// v0.4.5 (D-C317 / D-C318, 09-30): lineup "p14" (13 steps) — R17: golem hips (the whole motion script runs), vex item probe A/B,
//         fox pounce tilt + mouth item + sit settle, cod free from above, cat chase + tame/sit, leaves after the full state cut.
// v0.4.4 (D-C314, 09-30): lineup "p13" (12 steps) — R16b, the Patrix fidelity ports (fox, cat, ocelot, goat, cod, iron golem,
//   hoglin, zoglin moving with FreshLX's own animation).
// v0.4.3 (D-C310, 09-30): lineup "p12" (11 steps) — R16a (vex/allay hands, blaze/magma/glow-squid light, parrot/phantom
//   wing hinge, leaf state cut); the rig now PROVES a handed item with testfor hasitem ("CONFIRMED in" / "NOT in").
// v0.4.2 (D-C307, 09-30): lineup "p11" (14 steps) — the R14 fixes (RP-06 1.4.21 vex arms + sword + probes, blaze glow;
//   RP-07 1.4.27 allay arms, polar bear on the Patrix model; BP-02 1.3.193 dolphin / endermite; StripMine BP 1.3.6 grizzly / reptiles).
// v0.4.1 (D-C300, 09-29): lineup "p10" (19 steps) — FA-1 (RP-06 1.4.20 + RP-07 1.4.26: parrots per colour, bat, allay, vex, phantom,
//   warden, blaze, breeze, creaking, endermite, sniffer on their Patrix models) + SIZE ROUND 2 (BP-02 1.3.192 + StripMine BP 1.3.5 prime-male
//   predators); the rig re-rolls babies that cannot grow up and parrots of the wrong colour, places a jukebox (disc started by script when
//   the API allows), sweeps water left around an old pool, and notes when you stand in water. The banner drops p1r / p3n (subsets
//   of p1 / p3) to stay <= 120 characters.
// v0.4.0 (D-C292, 09-29): lineup "p9" (15 steps) — the SIZE ROUND parade (BP-02 1.3.190 real-life sizes, RP-06 1.4.19 warden x1.2, StripMine
//   BP 1.3.4 Naturalist sizes); rigged mobs grow up even when a step fires an event (the e03 wolf), and every rigged mob's age is logged.
// v0.3.9 (D-C288, 09-29): lineup "p8" (5 steps) — the R10 fixes of RP-06 1.4.18 + RP-07 1.4.25 (attachables switched on: the bogged's bow,
//         piglin crossbow + two probes, wolf armor + a zombified piglin probe); rig specs take body armor; the banner drops " - " and " help" to stay <= 120.
// v0.3.8 (D-C286, 09-29): lineup "p7" (5 steps) — the R9 fixes of RP-07 1.4.24 + RP-06 1.4.17 (enderman jaw opens, bows for skeleton /
//         stray / bogged, a squid tilt video); the banner drops its " - " before "pw:test help" to stay <= 120 characters.
// v0.3.7 (D-C285, 09-29): lineup "p6" (10 steps) — the R8 fixes of RP-07 1.4.23 + RP-06 1.4.16 (silverfish visible, squid tilt, enderman jaw,
//         tadpole upright, pufferfish spikes, skeleton grip, held-items check, fox/wolf/sheep); rig specs take a main-hand item.
// v0.3.6 (D-C284, 09-29): p5 q0 names RP-07 v1.4.22 (the enderman precedence fix).
// v0.3.5 (D-C284, 09-29): lineup "p5" (20 steps) — the R6 fixes of RP-07 1.4.21 + RP-06 1.4.15 + RP-08 1.4.8 (chickens, spider holes, cave spider
//   look, silverfish, enderman skin + angry jaw, evoker, pillager log, idle longbow, guardian spikes, dolphin fins, squid A/B, rabbit head,
//   mooshroom name-tag probe A-D, four size rows); rig specs take a name tag.
// v0.3.4 (D-C279, 09-29 09:36 his "it always spawns a brown chicken"): rig specs take `props` (entity properties via setProperty);
//   p4 a01 = the WHITE temperate chicken in the middle + warm / cold beside it.
// v0.3.3 (D-C278, 09-29): lineup "p4" (24 steps) — the R4 fixes of RP-07 1.4.20 + RP-06 1.4.13 (faces, spider, guardians, rabbit,
//   dolphin, mooshroom A/B, sizes, motion given back, regression rows); rig rows take an optional spawn event (brown mooshroom).
// v0.3.2 (D-C277, 09-29): lineups "p3" (33 steps) / "p3n" (16) — the mobs RP-07 1.4.19 + RP-06 1.4.12 changed (sizes side by side,
//         guardians resting + swimming, spider standing + walking, bee, tadpole, piglins, bogged) and the unwitnessed 1.4.16-1.4.18
//         Converter B mobs; rig rows / pen sizes / free mobs (pw_testrunner_rig.js).
// v0.3.1 (D-C267): lineup "p1r" (the 09-28 re-run list); block states in ['name'=value] syntax; every run is ARCHIVED per lineup
//         (`report p0` re-emits the last p0 run even after a p1 run); `runs` lists the archive; the report is ONE line per step
//         (the note rides on the verdict line); 'Repeat setup' is logged; rigged mobs are only grown up when they are babies.
// v0.3.0 (D-C264): lineup "p1" v2 (XPACK probe, sun/moon/clouds, leaves, dedupe regression) + lineup "p2" (REALM: sizes + Naturalist creatures)
// v0.2.2 (D-C263): lineup "p1" — the second-wave witness: hostile mobs in a ROOFED pen (no burning), block stations built by commands
//         (torches, lanterns, lit furnaces, lava flow, portal, fire, kelp, campfire smoke, the oak-log cross-pack experiment), sizes.
// v0.2.1 (D-C260, after the 176-shot P0 read): P0 verdicts mean something — PASS = Patrix quality AND one coherent animal; quick FAIL
//         tags vanilla? / magenta? / parts?; rigged mobs are adults; the bar says NO MOB (and why) when a spawn failed; the pool
//         re-melts its ice; the step title stays 1 s instead of 3 so it no longer covers the front shot.
// v0.2.0 (D-C257): LINEUPS — "start" walks the witness lineup (main), "start p0" walks the PHASE 0 lineup (the rotation-law
// PROBE entity, then every RP-07 mob held in the WITNESS RIG); new setup actions probe / rig / probeclear / rigclear
// (pw_testrunner_rig.js); the bar shows your FACING during a P0 run; probe + pen are cleared at the end / stop / reset.
// v0.1.2: the bar and the menu say 'you are in: <biome>' (the biome is information, never a requirement); flat-world guidance in the steps.
//
// One command walks the whole witness lineup (STEPS): each step sets itself up (time / weather / items / spawns),
// tells Abs0lum what to look at (title + a bar that stays on screen), then WAITS. He taps the CLICKER (a named
// stick, locked in the inventory) to open the menu: PASS · FAIL · PASS + note · FAIL + note · Repeat setup ·
// Build props · Skip · Back · Report · Stop. Every verdict goes to the content log as ONE line (<= 120 characters,
// prefix [PW-TEST]) and into a world dynamic property, so a relog or crash keeps the run; `report` re-emits the
// whole block ending with "[PW-TEST] END" — Settings > Creator > Content Log History > Copy to Clipboard.
//
// Commands: /scriptevent pw:test start [p0] | start! [p0] | resume | pass [note] | fail [note] | skip [note] | next | note <text>
//           | back | goto <id|n> | repeat | props | report [lineup] | runs | stop | list [p0] | where | clear | reset | help
// Nothing here touches the world while scripts load (early execution): state is read on the first command, the
// first player spawn, or the first heartbeat tick, whichever comes first.
import { world, system, ItemStack, ItemLockMode, WeatherType, GameMode, BlockTypes, EntityTypes, ItemTypes } from "@minecraft/server";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import { STEPS, STEP_INDEX } from "./pw_testrunner_steps.js";
import { P0_STEPS, P0_INDEX } from "./pw_testrunner_p0.js";
import { P1_STEPS, P1_INDEX, P1R_STEPS, P1R_INDEX } from "./pw_testrunner_p1.js";
import { P2_STEPS, P2_INDEX } from "./pw_testrunner_p2.js";
import { P3_STEPS, P3_INDEX, P3N_STEPS, P3N_INDEX } from "./pw_testrunner_p3.js";
import { P4_STEPS, P4_INDEX } from "./pw_testrunner_p4.js";
import { P5_STEPS, P5_INDEX } from "./pw_testrunner_p5.js";
import { P6_STEPS, P6_INDEX } from "./pw_testrunner_p6.js";
import { P7_STEPS, P7_INDEX } from "./pw_testrunner_p7.js";
import { P8_STEPS, P8_INDEX } from "./pw_testrunner_p8.js";
import { P9_STEPS, P9_INDEX } from "./pw_testrunner_p9.js";
import { P10_STEPS, P10_INDEX } from "./pw_testrunner_p10.js";
import { P11_STEPS, P11_INDEX } from "./pw_testrunner_p11.js";
import { P12_STEPS, P12_INDEX } from "./pw_testrunner_p12.js";
import { P13_STEPS, P13_INDEX } from "./pw_testrunner_p13.js";
import { P14_STEPS, P14_INDEX } from "./pw_testrunner_p14.js";
import { P15_STEPS, P15_INDEX, runLeafSetup } from "./pw_testrunner_p15.js";
import { P16_STEPS, P16_INDEX } from "./pw_testrunner_p16.js";
import { P17_STEPS, P17_INDEX } from "./pw_testrunner_p17.js";
import { P18_STEPS, P18_INDEX } from "./pw_testrunner_p18.js";
import { P19_STEPS, P19_INDEX } from "./pw_testrunner_p19.js";
import { P20_STEPS, P20_INDEX } from "./pw_testrunner_p20.js";
import { P21_STEPS, P21_INDEX } from "./pw_testrunner_p21.js";
import { BUMP_STEPS, BUMP_INDEX } from "./pw_testrunner_bump.js";
import { placeProbe, clearProbes, rigMob, clearRig, clearAll, facing, rigStatus } from "./pw_testrunner_rig.js";

export const RUNNER_VERSION = "0.5.11";
const LINEUPS = { main: { steps: STEPS, index: STEP_INDEX, label: "witness lineup" }, p0: { steps: P0_STEPS, index: P0_INDEX, label: "PHASE 0 (probe + rig)" }, p1: { steps: P1_STEPS, index: P1_INDEX, label: "P1 (hostile rig + block stations + probes)" }, p1r: { steps: P1R_STEPS, index: P1R_INDEX, label: "P1 RE-RUN (the 09-28 fixes + void stations)" }, p2: { steps: P2_STEPS, index: P2_INDEX, label: "P2 REALM (sizes + Naturalist creatures)" }, p3: { steps: P3_STEPS, index: P3_INDEX, label: "P3 (the 09-29 mob fixes + earlier rebuilds)" }, p3n: { steps: P3N_STEPS, index: P3N_INDEX, label: "P3 NEW ONLY (RP-07 1.4.19 + RP-06 1.4.12)" }, p4: { steps: P4_STEPS, index: P4_INDEX, label: "P4 (the R4 fixes: RP-07 1.4.20 + RP-06 1.4.13)" }, p5: { steps: P5_STEPS, index: P5_INDEX, label: "P5 (the R6 fixes: RP-07 1.4.22 + RP-06 1.4.15 + RP-08 1.4.8)" }, p6: { steps: P6_STEPS, index: P6_INDEX, label: "P6 (the R8 fixes: RP-07 1.4.23 + RP-06 1.4.16)" }, p7: { steps: P7_STEPS, index: P7_INDEX, label: "P7 (the R9 fixes: RP-07 1.4.24 + RP-06 1.4.17)" }, p8: { steps: P8_STEPS, index: P8_INDEX, label: "P8 (the R10 fixes: RP-06 1.4.18 + RP-07 1.4.25)" }, p9: { steps: P9_STEPS, index: P9_INDEX, label: "P9 SIZE PARADE (BP-02 1.3.190 + RP-06 1.4.19 + StripMine BP 1.3.4)" }, p10: { steps: P10_STEPS, index: P10_INDEX, label: "P10 FA-1 (RP-06 1.4.20 + RP-07 1.4.26) + PREDATOR SIZES (BP-02 1.3.192 + StripMine BP 1.3.5)" }, p11: { steps: P11_STEPS, index: P11_INDEX, label: "P11 THE R14 FIXES (RP-06 1.4.21 + RP-07 1.4.27 + BP-02 1.3.193 + StripMine BP 1.3.6)" }, p12: { steps: P12_STEPS, index: P12_INDEX, label: "P12 R16a (RP-06 1.4.22 + RP-07 1.4.28 + BP-02 1.3.194): hands, mob light, wing joints, leaves" }, p13: { steps: P13_STEPS, index: P13_INDEX, label: "P13 R16b (RP-06 1.4.23 + RP-07 1.4.29): the Patrix animation on fox, cat, ocelot, goat, cod, iron golem, hoglin, zoglin" }, p14: { steps: P14_STEPS, index: P14_INDEX, label: "P14 R17 (RP-06 1.4.24 + RP-07 1.4.31 + BP-02 1.3.195): golem hips, vex probe, fox pounce / mouth / sit, cod, cat, leaves" }, p15: { steps: P15_STEPS, index: P15_INDEX, label: "P15 LEAF PILOT (TestRunner RP 0.4.0): our trees, every species-age, today vs pilot vs biome colour on copies of one tree, random turns, shade, far swap, grove" }, p16: { steps: P16_STEPS, index: P16_INDEX, label: "P16 LEAF ROLLOUT (BP-02 1.3.197 + RP-01 1.3.106): new trees, look once, relog, far + shade, species + azalea, felling, decay, by hand, turns, forest, /place probe" }, p17: { steps: P17_STEPS, index: P17_INDEX, label: "P17 LEAF FIXES (BP-02 1.3.198 + RP-01 1.3.107): see-through falling canopy, shears give our leaves, 256 leaves, the culling probe" }, p18: { steps: P18_STEPS, index: P18_INDEX, label: "P18 NEW ANIMALS (RP-07 1.4.32+ + StripMine BP 1.3.7+): the 147 ported creatures in pens with name tags" }, p19: { steps: P19_STEPS, index: P19_INDEX, label: "P19 HIS PICKS (RP-07 1.4.34 + StripMine BP 1.3.9): every kept version by animal, name tags Name (PACK), + ours for gorilla / boar / bear" }, p20: { steps: P20_STEPS, index: P20_INDEX, label: "P20 JUDGING PASS: every entity in our packs, held in sized pens" }, p21: { steps: P21_STEPS, index: P21_INDEX, label: "P21 JUDGING PASS: every creature x every animation (one copy per clip)" }, bump: { steps: BUMP_STEPS, index: BUMP_INDEX, label: "BUMP: the bump-map test (same mob with / without the normal map)" } };
const RIG_LINEUPS = new Set(["p0", "p1", "p1r", "p2", "p3", "p3n", "p4", "p5", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13", "p14"]);   // the lineups that use the witness rig (quick tags, facing, NO MOB bar)
function isRigLineup() { return !!S && RIG_LINEUPS.has(S.lineup); }
const TAG = "[PW-TEST]";
const KEY = "pw:test_state";
const ARCHIVE = "pw:test_last_";                        // v0.3.1: + lineup id -> that lineup's latest run (JSON)
const ARCHIVE_MAX = 30000;                               // dynamic-property strings stop at 32767 characters
const MAXLINE = 120;
const CLICKER_ITEM = "minecraft:stick";
const CLICKER_NAME = "§aPW TEST CLICKER §7(tap in the air)";
const WX = { clear: WeatherType.Clear, rain: WeatherType.Rain, thunder: WeatherType.Thunder };
const TIMES = { noon: 6000, midnight: 18000 };
const CENSUS = [
  ["block", "pw:furn_chair_oak"], ["block", "pw:hearth_cobblestone"], ["block", "pw:slab_stone"], ["block", "pw:roof45_oak"],
  ["block", "pw:ramp_cobble_2_lo"], ["entity", "pw:seat"], ["block", "pw:zone_kitchen"], ["block", "pw:manhole_cover"],
  ["entity", "pw:marker"], ["item", "pw:hatch_lid"], ["entity", "sf_nba:firefly"], ["block", "minecraft:firefly_bush"],
];

// ---------------------------------------------------------------------------------------------------------------------
// state (world dynamic property; loaded lazily — never during early execution)
// ---------------------------------------------------------------------------------------------------------------------
let S = null;
let loaded = false;
export function _state() { return S; }
function lineup() { return LINEUPS[(S && S.lineup) || "main"] || LINEUPS.main; }
function steps() { return lineup().steps; }
function load() {
  if (loaded) return true;
  let raw;
  try { raw = world.getDynamicProperty(KEY); } catch { return false; }
  loaded = true;
  if (typeof raw === "string" && raw !== "") { try { S = JSON.parse(raw); } catch { S = null; } }
  return true;
}
function save() {
  try { world.setDynamicProperty(KEY, S ? JSON.stringify(S) : undefined); } catch (e) { logLine(`save failed: ${short(e, 60)}`); }
  if (S) archive(S);
}
/** Keep the latest run of each lineup, so `report <lineup>` can re-emit it after another lineup has run. Notes are clipped
 *  (first to 300, then 80 characters) only if the JSON would not fit one dynamic property. */
function archive(run) {
  let copy = run, s = JSON.stringify(copy);
  for (const lim of [300, 80]) {
    if (s.length <= ARCHIVE_MAX) break;
    copy = { ...run, verdicts: Object.fromEntries(Object.entries(run.verdicts).map(([k, e]) => [k, { ...e, n: short(e.n, lim) }])) };
    s = JSON.stringify(copy);
  }
  try { world.setDynamicProperty(ARCHIVE + (run.lineup || "main"), s.length <= ARCHIVE_MAX ? s : undefined); } catch (e) { logLine(`archive failed: ${short(e, 60)}`); }
}
function archived(which) {
  let raw; try { raw = world.getDynamicProperty(ARCHIVE + which); } catch { return null; }
  if (typeof raw !== "string" || raw === "") return null;
  try { return JSON.parse(raw); } catch { return null; }
}

// ---------------------------------------------------------------------------------------------------------------------
// text helpers — every content-log line is clipped to MAXLINE so the log panel's copy never truncates it
// ---------------------------------------------------------------------------------------------------------------------
function short(v, n) { const s = String(v ?? ""); return s.length <= n ? s : s.slice(0, n - 1) + "~"; }
export function clip(s, n = MAXLINE) { return short(s, n); }
function num(i) { return String(i + 1).padStart(2, "0"); }
export function stamp() {
  const d = new Date(); const p = (x) => String(x).padStart(2, "0");
  return `${p(d.getUTCHours())}:${p(d.getUTCMinutes())}:${p(d.getUTCSeconds())}`;
}
function runId() { const d = new Date(); return d.toISOString().slice(0, 16).replace("T", "_"); }
export function logLine(text) {
  const line = clip(`${TAG} ${text}`);
  try { console.warn(line); } catch { /* no console */ }
  return line;
}
/** Log a long text as several lines: "<prefix> <chunk>" then "<prefix>+ <chunk>"… */
function logLong(prefix, text) {
  const room = MAXLINE - TAG.length - 1 - prefix.length - 2;
  let s = String(text).replace(/\s+/g, " ").trim(); let first = true;
  while (s.length) { logLine(`${prefix}${first ? "" : "+"} ${s.slice(0, room)}`); s = s.slice(room); first = false; }
}
function tell(player, text) { try { if (player) player.sendMessage(text); } catch { /* ignore */ } }

// ---------------------------------------------------------------------------------------------------------------------
// player context
// ---------------------------------------------------------------------------------------------------------------------
function playerOf(ev) {
  try { if (ev && ev.sourceEntity && ev.sourceEntity.typeId === "minecraft:player") return ev.sourceEntity; } catch { /* ignore */ }
  try { return world.getAllPlayers()[0]; } catch { return undefined; }
}
export function where(player) {
  let xyz = "?", biome = "?";
  try { const l = player.location; xyz = `${Math.floor(l.x)},${Math.floor(l.y)},${Math.floor(l.z)}`; } catch { /* ignore */ }
  try {
    if (typeof player.dimension.getBiome === "function") biome = String(player.dimension.getBiome(player.location).id).replace(/^minecraft:/, "");
  } catch { biome = "?"; }
  return { xyz, biome };
}
function ahead(player, dist) {
  const l = player.location; const d = player.getViewDirection(); const h = Math.hypot(d.x, d.z) || 1;
  return { x: l.x + (d.x / h) * dist, y: l.y, z: l.z + (d.z / h) * dist };
}
function rnd(a, b) { return a + Math.random() * (b - a); }

// ---------------------------------------------------------------------------------------------------------------------
// the clicker
// ---------------------------------------------------------------------------------------------------------------------
function container(player) { try { const c = player.getComponent("minecraft:inventory"); return c && c.container; } catch { return undefined; } }
function hasClicker(player) {
  const inv = container(player); if (!inv) return false;
  for (let i = 0; i < inv.size; i++) { let s; try { s = inv.getItem(i); } catch { s = undefined; } if (s && s.nameTag === CLICKER_NAME) return true; }
  return false;
}
function giveClicker(player) {
  try {
    if (hasClicker(player)) return;
    const inv = container(player); if (!inv) return;
    const st = new ItemStack(CLICKER_ITEM, 1); st.nameTag = CLICKER_NAME; st.lockMode = ItemLockMode.inventory; st.keepOnDeath = true;
    let slot8; try { slot8 = inv.getItem(8); } catch { slot8 = undefined; }
    if (!slot8) inv.setItem(8, st); else inv.addItem(st);
  } catch (e) { logLine(`clicker: ${short(e, 60)}`); }
}
function removeClicker(player) {
  try {
    const inv = container(player); if (!inv) return;
    for (let i = 0; i < inv.size; i++) { const s = inv.getItem(i); if (s && s.nameTag === CLICKER_NAME) inv.setItem(i, undefined); }
  } catch { /* ignore */ }
}

// ---------------------------------------------------------------------------------------------------------------------
// setup + props
// ---------------------------------------------------------------------------------------------------------------------
function giveAll(player, list) {
  const inv = container(player); if (!inv) { logLine("give: no inventory"); return; }
  const ok = [], missing = [], full = [];
  for (const it of list) {
    const [rawId, n] = Array.isArray(it) ? it : [it, 1];
    const id = rawId.includes(":") ? rawId : `minecraft:${rawId}`;
    let type; try { type = ItemTypes.get(id); } catch { type = undefined; }
    if (!type) { missing.push(rawId); continue; }
    try { const left = inv.addItem(new ItemStack(type, n)); (left ? full : ok).push(rawId); } catch { missing.push(rawId); }
  }
  if (ok.length) logLong("gave", ok.join(" "));
  if (missing.length) logLong("MISSING (pack not loaded?)", missing.join(" "));
  if (full.length) logLong("inventory FULL, not given", full.join(" "));
}
function spawnAhead(player, id, n) {
  let made = 0;
  for (let k = 0; k < n; k++) {
    try { const p = ahead(player, 3 + Math.floor(k / 2)); p.x += (k % 2 ? 1 : -1); player.dimension.spawnEntity(id, p); made++; }
    catch (e) { logLine(`spawn FAILED ${id}: ${short(e, 50)}`); break; }
  }
  logLine(`spawned ${made} x ${id} ahead of ${where(player).xyz}`);
}
export function doSetup(player, st) {
  const leafActs = (st.setup || []).filter((a) => a.leaftree || a.leafclear || a.leafarea || a.leafreset || a.placeprobe || a.leafmark);   // p15: areas, clears, trees, reset = one ordered job
  if (leafActs.length) { try { runLeafSetup(player, leafActs, logLine); } catch (e) { logLine(`setup error ${st.id} (leaves): ${short(e, 60)}`); } }
  for (const a of st.setup || []) {
    try {
      if (a.daytime !== undefined) { world.setTimeOfDay(TIMES[a.daytime] ?? a.daytime); logLine(`setup time ${a.daytime}`); }
      if (a.weather) { player.dimension.setWeather(WX[a.weather], 24000); logLine(`setup weather ${a.weather}`); }
      if (a.give) giveAll(player, a.give);
      if (a.cmd) for (const c of a.cmd) { try { player.runCommand(c); logLine(`setup cmd ok: ${c}`); } catch (e) { logLine(`setup cmd FAILED: ${c} - ${short(e, 40)}`); } }
      if (a.spawn) spawnAhead(player, a.spawn[0], a.spawn[1] || 1);
      if (a.probeclear) clearProbes(player);
      if (a.rigclear) clearRig(player);
      if (a.sweep) sweepMobs(player, a.sweep);
      if (a.probe) { clearRig(player); placeProbe(player, a.probe); }
      if (a.rig) { clearProbes(player); rigMob(player, a.rig); }
    } catch (e) { logLine(`setup error ${st.id}: ${short(e, 60)}`); }
  }
}
/** v0.5.8 (his 02:06 CT 10-01): before each parade step, remove every wandering creature in a big square around him (they walked into
 *  his screenshots). Kept: players, anything named (his pets / the rig's own name-tagged animals), tamed animals, markers (CIVITAS,
 *  probes), armour stands, item frames, paintings, dropped items, xp, leash knots — only living, unnamed, untamed creatures go. */
const SWEEP_KEEP = /player|armor_stand|item|xp_orb|painting|leash_knot|marker|civ|probe|frame|minecart|boat|arrow|trident|fishing_hook|ender_crystal/;
export function sweepMobs(player, half) {
  let n = 0, kept = 0;
  try {
    const p = player.location;
    for (const e of player.dimension.getEntities({ location: p, maxDistance: Math.ceil(half * 1.42) })) {
      try {
        const l = e.location;
        if (Math.abs(l.x - p.x) > half || Math.abs(l.z - p.z) > half) continue;
        if (SWEEP_KEEP.test(e.typeId) || e.nameTag || !e.getComponent("minecraft:health")) { kept++; continue; }
        const tame = e.getComponent("minecraft:is_tamed"); if (tame) { kept++; continue; }
        e.remove(); n++;
      } catch { /* entity gone mid-sweep */ }
    }
  } catch (err) { logLine(`SWEEP failed: ${short(err, 60)}`); return; }
  logLine(`SWEEP ${n} creature(s) removed within ${half} blocks (square), ${kept} kept`);
}
function placeBush(player) {
  const c = ahead(player, 3); const dim = player.dimension;
  const cell = { x: Math.floor(c.x), y: Math.floor(c.y), z: Math.floor(c.z) };
  const b = dim.getBlock(cell); const below = dim.getBlock({ x: cell.x, y: cell.y - 1, z: cell.z });
  if (!b || !below) { logLine("props: bush spot not loaded"); return; }
  if (!b.isAir) { logLine(`props: bush spot occupied by ${b.typeId}`); return; }
  if (below.isAir || below.isLiquid) below.setType("minecraft:dirt");
  b.setType("minecraft:firefly_bush");
  logLine(`props: firefly_bush placed at ${cell.x},${cell.y},${cell.z}`);
}
export function doProps(player, st) {
  if (!st.props) { tell(player, `${TAG} this step has no props`); return; }
  for (const a of st.props) {
    try {
      if (a.bush) placeBush(player);
      if (a.particles) {
        const [id, n] = a.particles; const c = ahead(player, 3); let m = 0;
        for (let k = 0; k < n; k++) {
          try { player.dimension.spawnParticle(id, { x: c.x + rnd(-1.5, 1.5), y: c.y + rnd(0.3, 1.8), z: c.z + rnd(-1.5, 1.5) }); m++; }
          catch (e) { logLine(`particle FAILED ${id}: ${short(e, 50)}`); break; }
        }
        logLine(`props: ${m} x ${id} spawned ahead`);
      }
    } catch (e) { logLine(`props error: ${short(e, 60)}`); }
  }
}

// ---------------------------------------------------------------------------------------------------------------------
// the run
// ---------------------------------------------------------------------------------------------------------------------
function current() { return S && S.active ? steps()[S.i] : undefined; }
function census() {
  const ok = [], miss = [];
  for (const [kind, id] of CENSUS) {
    let found = false;
    try { found = !!(kind === "block" ? BlockTypes.get(id) : kind === "entity" ? EntityTypes.get(id) : ItemTypes.get(id)); } catch { found = false; }
    (found ? ok : miss).push(id);
  }
  logLong(`CENSUS ok ${ok.length}/${CENSUS.length}:`, ok.join(" "));
  if (miss.length) logLong("CENSUS MISSING:", miss.join(" "));
}
function rulesOff() {
  try {
    const g = world.gameRules; S.gr = { day: !!g.doDayLightCycle, wx: !!g.doWeatherCycle };
    g.doDayLightCycle = false; g.doWeatherCycle = false;
    logLine(`gamerules: daylight + weather cycles OFF for the run (were ${S.gr.day}/${S.gr.wx})`);
  } catch (e) { logLine(`gamerules unavailable: ${short(e, 50)}`); }
}
function rulesRestore() {
  try {
    if (!S || !S.gr) return;
    const g = world.gameRules; g.doDayLightCycle = !!S.gr.day; g.doWeatherCycle = !!S.gr.wx;
    logLine(`gamerules restored (daylight ${S.gr.day}, weather ${S.gr.wx})`); S.gr = null;
  } catch { /* ignore */ }
}
function showStep(player, st, i) {
  try { player.onScreenDisplay.setTitle(`§e${i + 1}/${steps().length}`, { subtitle: st.title, fadeInDuration: 5, stayDuration: 20, fadeOutDuration: 10 }); } catch { /* ignore */ }
  try { player.playSound("random.orb"); } catch { /* ignore */ }
  const firstLine = st.body.split("\n")[0];
  tell(player, `§e${TAG} step ${i + 1}/${steps().length} §f${st.title}\n§7${firstLine}\n§atap the clicker when you have looked (PASS / FAIL / note).`);
}
function beginStep(player, i, runSetup = true) {
  S.i = i; save();
  const st = steps()[i];
  logLine(`STEP #${num(i)} ${st.id} ${st.title} · ${stamp()} · ${where(player).biome}${isRigLineup() ? " · facing " + facing(player) : ""}`);
  showStep(player, st, i);
  if (runSetup) doSetup(player, st);
}
function record(player, v, note) {
  const st = current(); if (!st) return;
  const w = where(player);
  const e = { v, n: (note || "").trim(), t: stamp(), k: 0, p: w.xyz, b: w.biome };
  try { e.k = system.currentTick; } catch { /* ignore */ }
  S.verdicts[st.id] = e; save();
  logLine(`${v} #${num(S.i)} ${st.id} ${e.t} ${e.p} ${e.b}${e.n ? " +note" : ""}`);
  if (e.n) logLong(`NOTE ${st.id}:`, e.n);
  tell(player, `§a${TAG} ${v} recorded for step ${S.i + 1} (${st.id})${e.n ? " with your note" : ""}`);
}
function addNote(player, text) {
  const st = current(); if (!st || !text) return;
  const e = S.verdicts[st.id] || { v: "OPEN", n: "", t: stamp(), k: 0, p: where(player).xyz, b: where(player).biome };
  e.n = e.n ? `${e.n} | ${text}` : text; S.verdicts[st.id] = e; save();
  logLong(`NOTE ${st.id}:`, text); tell(player, `§a${TAG} note saved for ${st.id}`);
}
/** v0.5.8 (his B1 02:06: "it went back but the pen / animals didn't rebuild"): back used to show the previous step's text only.
 *  Now, when that step builds a pen (rig) or has setup, the current pen is cleared and the previous step's setup runs again. */
function goBack(player) {
  if (S.i <= 0) return;
  const prev = steps()[S.i - 1];
  const rebuild = (prev.setup || []).some((a) => a.rig || a.cmd || a.sweep || a.probe);
  if (rebuild) clearRig(player);
  beginStep(player, S.i - 1, rebuild);
}
function advance(player) {
  if (S.i + 1 >= steps().length) { finish(player, "DONE"); return; }
  beginStep(player, S.i + 1);
}
/** One line per step: "#07 r07 FAIL 17:45:12 1,173,-3 | the note…"; a note too long for the line continues on "NOTE r07+" lines.
 *  `which` = a lineup id: the current run if it is that lineup, else that lineup's archived last run. */
export function report(player, which) {
  let R = S, from = "current";
  if (which) {
    which = String(which).toLowerCase();
    if (!LINEUPS[which]) { tell(player, `${TAG} unknown lineup "${which}" - ${Object.keys(LINEUPS).join(" / ")}`); return; }
    if (!S || (S.lineup || "main") !== which) { R = archived(which); from = "archived"; }
  }
  if (!R) { tell(player, `${TAG} no ${which ? which + " " : ""}run recorded yet - /scriptevent pw:test start${which ? " " + which : ""}`); return; }
  const L = LINEUPS[R.lineup || "main"] || LINEUPS.main;
  const counts = { PASS: 0, FAIL: 0, SKIP: 0, OPEN: 0 };
  for (const st of L.steps) { const e = R.verdicts[st.id]; const v = e ? e.v : "OPEN"; counts[v] = (counts[v] || 0) + 1; }
  logLine(`REPORT run ${R.run} · ${R.lineup || "main"} (${from}) · runner v${RUNNER_VERSION} · ${L.steps.length} steps · PASS ${counts.PASS} FAIL ${counts.FAIL} SKIP ${counts.SKIP} open ${counts.OPEN}`);
  L.steps.forEach((st, i) => {
    const e = R.verdicts[st.id];
    if (!e) { logLine(`#${num(i)} ${st.id} OPEN`); return; }
    const head = `#${num(i)} ${st.id} ${e.v} ${e.t} ${e.p}`;
    if (!e.n) { logLine(head); return; }
    const room = MAXLINE - TAG.length - 1 - head.length - 3;
    const note = String(e.n).replace(/\s+/g, " ").trim();
    logLine(`${head} | ${note.slice(0, Math.max(0, room))}`);
    if (note.length > room) logLong(`NOTE ${st.id}+`, note.slice(Math.max(0, room)));
  });
  logLine("END");
  const fails = L.steps.filter((st) => R.verdicts[st.id] && R.verdicts[st.id].v === "FAIL").map((st) => st.id);
  tell(player, `§e${TAG} ${from} ${R.lineup || "main"} report written to the content log: PASS ${counts.PASS} · FAIL ${counts.FAIL} · SKIP ${counts.SKIP} · open ${counts.OPEN}` +
    (fails.length ? `\n§cFAIL: ${fails.join(", ")}` : "") +
    `\n§7Settings > Creator > Content Log History > Copy to Clipboard, then paste it to Claude.`);
}
function listRuns(player) {
  const rows = [];
  for (const id of Object.keys(LINEUPS)) {
    const R = (S && (S.lineup || "main") === id) ? S : archived(id); if (!R) continue;
    const L = LINEUPS[id]; const done = L.steps.filter((st) => R.verdicts[st.id]).length;
    rows.push(`${id}: run ${R.run} · ${done}/${L.steps.length} answered${R.active ? " · IN PROGRESS" : ""}`);
  }
  for (const r of rows) logLine(`RUNS ${r}`);
  tell(player, `§e${TAG} saved runs:\n§f` + (rows.length ? rows.join("\n") : "none yet") + `\n§7/scriptevent pw:test report <lineup> re-emits one.`);
}
function finish(player, how) {
  logLine(`${how} at step #${num(S.i)} · ${stamp()}`);
  S.active = false; rulesRestore(); save();
  removeClicker(player);
  try { clearAll(player); } catch (e) { logLine(`clear at ${how}: ${short(e, 50)}`); }
  report(player);
  try { player.onScreenDisplay.setTitle("§aTEST RUN " + how, { subtitle: "copy the content log for Claude", fadeInDuration: 5, stayDuration: 80, fadeOutDuration: 10 }); } catch { /* ignore */ }
}
function start(player, force, which) {
  if (S && S.active && !force) {
    tell(player, `§c${TAG} a run is already at step ${S.i + 1}/${steps().length} (${S.lineup || "main"}). §f/scriptevent pw:test resume §7to continue, §fstart! §7to restart.`);
    return;
  }
  const which2 = LINEUPS[which] ? which : "main";
  if (S && S.active) { try { clearAll(player); } catch { /* ignore */ } }
  S = { v: 2, run: runId(), lineup: which2, i: 0, active: true, started: Date.now(), verdicts: {}, gr: null };
  let mode = "?", dim = "?", tick = 0, day = 0, tod = 0, name = "?";
  try { mode = String(player.getGameMode()); } catch { /* ignore */ }
  try { dim = String(player.dimension.id).replace(/^minecraft:/, ""); } catch { /* ignore */ }
  try { tick = system.currentTick; } catch { /* ignore */ }
  try { day = world.getDay(); tod = world.getTimeOfDay(); } catch { /* ignore */ }
  try { name = player.name; } catch { /* ignore */ }
  logLine(`RUN START ${S.run} · ${S.lineup} (${lineup().label}) · runner v${RUNNER_VERSION} · ${steps().length} steps · ${name} · ${mode} · ${dim}`);
  logLine(`world day ${day} time ${tod} tick ${tick} · at ${where(player).xyz} ${where(player).biome} · times below are UTC`);
  census();
  rulesOff();
  giveClicker(player);
  tell(player, `§e${TAG} ${lineup().label}: ${steps().length} steps. §fThe CLICKER is in hotbar slot 9 - tap it in the air to open the menu.\n§7Commands: /scriptevent pw:test help`);
  beginStep(player, 0);
}
function resume(player) {
  if (!S || !S.active) { tell(player, `${TAG} no run in progress - /scriptevent pw:test start`); return; }
  giveClicker(player);
  logLine(`RESUME at step #${num(S.i)} ${steps()[S.i].id} · ${stamp()}`);
  showStep(player, steps()[S.i], S.i);
}
function gotoStep(player, arg) {
  let i = lineup().index[arg]; if (i === undefined) { const n = parseInt(arg, 10); if (n >= 1 && n <= steps().length) i = n - 1; }
  if (i === undefined) { tell(player, `${TAG} unknown step "${arg}" - /scriptevent pw:test list`); return; }
  beginStep(player, i);
}
function listSteps(player, which) {
  const L = LINEUPS[which] || (S && LINEUPS[S.lineup]) || LINEUPS.main;
  const lines = L.steps.map((st, i) => `§7${num(i)} §f${st.id} §7${st.title}`);
  tell(player, `§e${TAG} ${L.label}: ${L.steps.length} steps:\n` + lines.join("\n"));
}
const HELP = `§e${TAG} /scriptevent pw:test <verb>\n§fstart§7 begin the witness lineup · §fstart p0§7 begin PHASE 0 (probe + mob rig) · §fstart p1§7 hostile rig + block stations + probes · §fstart p1r§7 re-run the 09-28 fixes · §fstart p2§7 REALM: sizes + Naturalist creatures · §fstart p20§7 JUDGING: every entity · §fstart p21§7 JUDGING: every creature x every animation · §fstart bump§7 the bump-map test · §fstart p19§7 HIS PICKS parade · §fstart p18§7 NEW ANIMALS parade · §fstart p17§7 LEAF FIXES + the culling probe · §fstart p16§7 LEAF ROLLOUT: the new leaves in the main packs · §fstart p15§7 LEAF PILOT: every species-age on our trees · §fstart p14§7 R17: golem, vex probe, fox, cod, cat, leaves · §fstart p13§7 R16b: the Patrix animation on 8 mobs · §fstart p12§7 R16a: hands, mob light, wings, leaves · §fstart p11§7 the R14 fixes · §fstart p10§7 FA-1 + predator sizes · §fstart p9§7 the size parade · §fstart p8§7 the R10 fixes · §fstart p7§7 the R9 fixes · §fstart p6§7 the R8 fixes · §fstart p5§7 the R6 fixes · §fstart p4§7 the R4 fixes · §fstart p3n§7 the 09-29 fixes · §fstart p3§7 + earlier rebuilds · start! restarts · §fresume§7 after a relog · §fpass|fail|skip [note]§7 verdict + next\n` +
  `§fnote <text>§7 add a note · §fnext§7 no verdict, next · §fback§7 · §fgoto <id|n>§7 · §frepeat§7 setup again · §fprops§7 build props\n` +
  `§freport [lineup]§7 write the results block (a lineup id re-emits its last saved run) · §fruns§7 list saved runs · §fstop§7 end the run (probe + pen removed) · §flist [p0]§7 · §fwhere§7 · §fclear§7 empty inventory (creative) · §freset§7 forget the run`;

// ---------------------------------------------------------------------------------------------------------------------
// the menu (server-ui) — opened by the clicker
// ---------------------------------------------------------------------------------------------------------------------
async function noteForm(player, v) {
  const st = current(); if (!st) return;
  // v0.5.3 (his p16 ask: "a higher number of maximum characters per note"): THREE boxes, joined in order into one note
  const m = new ModalFormData().title(`${v} · ${st.id}`)
    .textField("What did you see? (box 1 of 3)", "e.g. clusters of balls / shelf sides flicker")
    .textField("…continued (box 2, optional)", "")
    .textField("…continued (box 3, optional)", "");
  let r; try { r = await m.show(player); } catch (e) { logLine(`note form: ${short(e, 60)}`); return; }
  if (!r || r.canceled) return;
  const note = (r.formValues || []).slice(0, 3).map((x) => String(x || "").trim()).filter(Boolean).join(" ");
  record(player, v, note); advance(player);
}
export async function menu(player) {
  const st = current(); if (!st) { tell(player, `${TAG} no run active - /scriptevent pw:test start`); return; }
  const i = S.i; const w = where(player);
  const f = new ActionFormData().title(`Step ${i + 1}/${steps().length} · ${st.id}`)
    .body(`§l${st.title}§r\n\n${st.body}\n\n§7you are in: ${w.biome} (information only)${isRigLineup() ? " · facing " + facing(player) : ""} · ${stamp()} UTC`)
    .button(isRigLineup() ? "§2PASS (Patrix + one animal)" : "§2PASS").button("§4FAIL");
  const p0 = isRigLineup();
  if (p0) f.button("§4FAIL: vanilla?").button("§4FAIL: magenta?").button("§4FAIL: parts?");   // the P0 quick tags (D-C260)
  f.button("PASS + note").button("FAIL + note").button("Repeat setup");
  const hasProps = !!st.props; if (hasProps) f.button("Build props here");
  f.button("Skip").button("Back").button("Report so far").button("Stop the run");
  let r; try { r = await f.show(player); } catch (e) { logLine(`menu: ${short(e, 60)}`); return; }
  if (!r || r.canceled || r.selection === undefined) return;
  if (!current() || S.i !== i) return;                                   // the step changed while the menu was open
  const order = ["pass", "fail", ...(p0 ? ["fail:vanilla?", "fail:magenta?", "fail:parts?"] : []), "pass+", "fail+", "repeat", ...(hasProps ? ["props"] : []), "skip", "back", "report", "stop"];
  const choice = order[r.selection];
  if (choice === "pass") { record(player, "PASS", ""); advance(player); }
  else if (choice === "fail") { record(player, "FAIL", ""); advance(player); }
  else if (choice && choice.startsWith("fail:")) { record(player, "FAIL", choice.slice(5)); advance(player); }
  else if (choice === "pass+") await noteForm(player, "PASS");
  else if (choice === "fail+") await noteForm(player, "FAIL");
  else if (choice === "repeat") { logLine(`SETUP REPEATED ${st.id} (by you) · ${stamp()}`); doSetup(player, st); tell(player, `${TAG} setup repeated`); }
  else if (choice === "props") doProps(player, st);
  else if (choice === "skip") { record(player, "SKIP", ""); advance(player); }
  else if (choice === "back") goBack(player);   // v0.5.8 his B1: rebuild the pen
  else if (choice === "report") report(player);
  else if (choice === "stop") finish(player, "STOPPED");
}

// ---------------------------------------------------------------------------------------------------------------------
// commands
// ---------------------------------------------------------------------------------------------------------------------
export function command(player, message) {
  load();
  const parts = (message || "").trim().split(/\s+/); const verb = (parts[0] || "help").toLowerCase(); const arg = parts.slice(1).join(" ");
  try {
    switch (verb) {
      case "start": start(player, false, (parts[1] || "main").toLowerCase()); break;
      case "start!": start(player, true, (parts[1] || "main").toLowerCase()); break;
      case "p0": start(player, false, "p0"); break;
      case "p0!": start(player, true, "p0"); break;
      case "resume": resume(player); break;
      case "pass": if (current()) { record(player, "PASS", arg); advance(player); } else tell(player, `${TAG} no run active`); break;
      case "fail": if (current()) { record(player, "FAIL", arg); advance(player); } else tell(player, `${TAG} no run active`); break;
      case "skip": if (current()) { record(player, "SKIP", arg); advance(player); } else tell(player, `${TAG} no run active`); break;
      case "next": if (current()) { logLine(`OPEN #${num(S.i)} ${steps()[S.i].id} (moved on without a verdict)`); advance(player); } else tell(player, `${TAG} no run active`); break;
      case "note": if (current()) addNote(player, arg); else tell(player, `${TAG} no run active`); break;
      case "back": if (current()) goBack(player); break;   // v0.5.8 his B1
      case "goto": if (current()) gotoStep(player, arg); else tell(player, `${TAG} no run active`); break;
      case "repeat": if (current()) { logLine(`SETUP REPEATED ${current().id} (by you) · ${stamp()}`); doSetup(player, current()); tell(player, `${TAG} setup repeated`); } break;
      case "props": if (current()) doProps(player, current()); break;
      case "report": report(player, parts[1]); break;
      case "runs": listRuns(player); break;
      case "stop": if (current()) finish(player, "STOPPED"); else tell(player, `${TAG} no run active`); break;
      case "list": listSteps(player, (parts[1] || "").toLowerCase()); break;
      case "where": { const w = where(player); logLine(`WHERE ${w.xyz} ${w.biome} · ${stamp()}`); tell(player, `${TAG} ${w.xyz} · you are in: ${w.biome} (logged)`); break; }
      case "clear": {
        let mode; try { mode = player.getGameMode(); } catch { mode = undefined; }
        if (mode !== GameMode.Creative) { tell(player, `${TAG} clear only works in creative`); break; }
        try { player.runCommand("clear @s"); } catch { /* ignore */ }
        if (current()) giveClicker(player); tell(player, `${TAG} inventory cleared`); break;
      }
      case "reset": if (S && S.active) rulesRestore(); S = null; save(); removeClicker(player); try { clearAll(player); } catch { /* ignore */ } tell(player, `${TAG} run forgotten`); break;
      default: tell(player, HELP);
    }
  } catch (e) { logLine(`command ${verb}: ${short(e, 70)}`); tell(player, `§c${TAG} error: ${short(e, 80)}`); }
}
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:test") return;
  const player = playerOf(ev); if (!player) return;
  command(player, ev.message);
}, { namespaces: ["pw"] });

world.afterEvents.itemUse.subscribe((ev) => {
  try {
    const it = ev.itemStack; if (!it || it.nameTag !== CLICKER_NAME) return;
    const p = ev.source; if (!p || p.typeId !== "minecraft:player") return;
    load();
    if (!S || !S.active) { tell(p, `${TAG} no run active - /scriptevent pw:test start`); return; }
    menu(p);
  } catch (e) { logLine(`clicker error: ${short(e, 60)}`); }
});

world.afterEvents.playerSpawn.subscribe((ev) => {
  if (!ev.initialSpawn) return;
  const p = ev.player;
  system.runTimeout(() => {
    try {
      if (!load() || !S || !S.active) return;
      giveClicker(p);
      logLine(`REJOIN at step #${num(S.i)} ${steps()[S.i].id} · ${stamp()}`);
      showStep(p, steps()[S.i], S.i);
      tell(p, `§e${TAG} your test run continues at step ${S.i + 1}/${steps().length} - tap the clicker.`);
    } catch (e) { logLine(`rejoin: ${short(e, 60)}`); }
  }, 40);
});

// the bar at the bottom of the screen, refreshed every second while a run is active
system.runInterval(() => {
  try {
    if (!load() || !S || !S.active) return;
    const st = steps()[S.i]; if (!st) return;
    for (const p of world.getAllPlayers()) {
      try {
        const fac = isRigLineup() ? ` · facing ${facing(p)}` : "";
        const rs = isRigLineup() ? rigStatus() : null;
        if (rs && rs.spawnError) p.onScreenDisplay.setActionBar(`§c${S.i + 1}/${steps().length} NO MOB (${rs.mob}): ${rs.spawnError}`);
        else p.onScreenDisplay.setActionBar(`§e${S.i + 1}/${steps().length} §f${st.title} §7· you are in: ${where(p).biome}${fac} · tap the clicker`);
      } catch { /* ignore */ }
    }
  } catch { /* ignore */ }
}, 20);

try { console.warn(`[PW-VERSION] PW Test Runner BP v${RUNNER_VERSION} · ${Object.keys(LINEUPS).length} lineups · main ${STEPS.length} p18 ${P18_STEPS.length} p19 ${P19_STEPS.length} p20 ${P20_STEPS.length} p21 ${P21_STEPS.length} bump ${BUMP_STEPS.length}`); } catch { /* no console */ }
