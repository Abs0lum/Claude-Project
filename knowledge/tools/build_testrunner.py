#!/usr/bin/env python3
"""build_testrunner.py — PW-TestRunner BP v0.5.3 (D-C350: lineup p17 — leaf fixes + the culling probe block; 3-box notes) — v0.5.2 (D-C348: p16 m01-m10, the 128 vs 256 leaf comparison; 22 t256 test blocks) — v0.5.1 (D-C347: p16 for BP-02 1.3.197 / RP-01 1.3.106, n13, persistent tree boxes) — v0.5.0 (D-C346: lineup p16 — the leaf rollout; placeFeature + refusal reasons) — v0.4.9 (D-C338: independent-check fixes) — v0.4.8 (D-C336: p15 every species-age on our trees, clone copies) — v0.4.7 (D-C333: p15 fixes from the independent check — BP-02 trunk ids, queued step jobs, trees anchored at step start) — v0.4.6 (D-C332: lineup p15 — the LEAF PILOT; the 24 pw:pilot_* leaf blocks from build_leaf_pilot_rp.py; pairs with RP v0.4.0) — v0.4.5 (D-C317 / D-C318: lineup p14 — R17: golem hips, vex probe, fox, cod, cat, leaves) — v0.4.4 (D-C314: lineup p13 — R16b, the Patrix fidelity ports) — v0.4.3 (D-C310: lineup p12 — R16a; the rig proves a handed item with testfor hasitem; spec.boxes) — v0.4.2 (D-C307: lineup p11 — the R14 fixes) — v0.4.1 (D-C300: lineup p10 — FA-1 + predator sizes; rig re-roll, jukebox, leftover-water sweep) — v0.4.0 (D-C292: lineup p9 — the size parade; grow-up after a step event + age log) — v0.3.9 (D-C288: lineup p8 — the R10 fixes; rig body armor) — v0.3.8 (D-C286: lineup p7 — the R9 fixes) — v0.3.7 (D-C285: lineup p6 — the R8 fixes; rig specs take a main-hand item) — v0.3.6 (D-C284: p5 q0 names RP-07 v1.4.22) — v0.3.5 (D-C284: lineup p5 — the R6 fixes; rig specs take a name tag) — earlier: v0.3.4 (D-C279: p4 a01 shows the white temperate chicken; rig specs take entity properties) — earlier: v0.3.3 (D-C278: lineup p4 — the R4 fixes; rig rows take a spawn event) — v0.3.2 (D-C277: lineups p3 / p3n — the 09-29 mob checks; rig rows, pen sizes, free mobs) — earlier: v0.3.1 (+ the UNCHANGED PW-TestRunner RP v0.3.0, rebuilt to a check dir and compared) (D-C267: lineup p1r, ["name"=value] block states,
the evocation_illager id, the run archive + report <lineup>, one line per step, baby-only grow-up; D-C264: lineup p1 v2 — the XPACK probe blocks pw:xprobe_a/b/c (BP blocks/ +
RP terrain_texture keys pointing OUTSIDE the RP), sun/moon/clouds, leaves, the dedupe-regression row — and lineup p2 (Realm: sizes + Naturalist renders); D-C263 adds lineup p1; 0.2.1 D-C260; 0.2.0 D-C257, Abs0lum 18:17 09-27 "Go for P0 … a script
command where it runs the commands while I take screenshots between phases/mobs").

BP (job-only, attach at the BOTTOM of the Behavior Packs list):
  manifest.json          header/script uuids unchanged since 0.1.0 (the saved run carries over) + a NEW data module (fixed uuid)
                         for entities/; pins @minecraft/server 2.3.0 + @minecraft/server-ui 2.0.0; NO pack-uuid dependencies
                         (a BP dep on an RP can disable VV — bridge lesson L-VV-2): he attaches the RP himself
  scripts/               main.js + pw_testrunner.js (lineups) + pw_testrunner_steps.js (witness lineup) +
                         pw_testrunner_p0.js (PHASE 0 lineup) + pw_testrunner_rig.js (probe + mob witness rig) — byte-identical to tools/testrunner_src
  entities/pw_probe.json the rotation-law chart entity (behaviour half)
RP (job-only, attach at the TOP of the Resource Packs list — it only adds pw:probe, nothing overlaps):
  manifest.json          new fixed uuids; entity/, models/entity/, textures/entity/, animations/, animation_controllers/, render_controllers/
Both: texts/, pack_icon.png, PW-DEPENDENCIES.md (provider-only note).
"""
import json, shutil, datetime, hashlib, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import probe_assets

ROOT = Path("/home/claude"); SRC = ROOT / "tools/testrunner_src"
VER = "0.5.11"; RP_VER = "0.3.0"; PILOT_RP_VER = "0.7.0"; DATE = "2026-10-01"; RP_DATE = "2026-09-28"   # the RP is unchanged since 0.3.0 (its own date)
BP = ROOT / f"_build/testrunner-{VER}"; RP = ROOT / f"_build/testrunner-rp-{RP_VER}-check"   # the RP is NOT re-shipped: rebuilt here only to prove it is unchanged
HEADER_UUID = "6b1f0c2e-9a47-4d3b-8e5c-2f7a9d1c4e60"      # BP header — fixed for the pack's life (since 0.1.0)
MODULE_UUID = "d4e8a1f2-3c6b-4b9e-a7d5-8f1e2c3b4a90"      # BP script module — fixed since 0.1.0
DATA_UUID = "9c2e7b41-5d3a-4f68-b1c9-2e8a4d7f6c13"        # BP data module — NEW in 0.2.0, fixed from now on
RP_HEADER_UUID = "3f8b6a2d-1c4e-4d7b-9a5f-6e2c8b1d4a37"   # RP header — fixed for the pack's life
RP_MODULE_UUID = "7a1d4c9e-8b2f-4e6a-a3d5-1f9c7e2b5d48"   # RP resources module — fixed
BP_DESC = (f"v{VER} ({DATE}) TEST RUNNER — v0.5.11: p20 / p21 rebuilt for RP-07 1.4.43 + RP-04 1.3.144 (his log 3). v0.5.10: p20 / p21 rebuilt for RP-07 1.4.42 + RP-06 1.4.28 (his content log 2 fixed). v0.5.9: p20 / p21 rebuilt for RP-07 1.4.41 + RP-06 1.4.27 (his content log 1 fixed); each p21 step names its movement-only clips. v0.5.8: /scriptevent pw:test start p20 = THE JUDGING PASS, every entity in our packs held in sized pens "
           "(the unsafe ones listed, not summoned); start p21 = every creature x every animation (a row of copies, each playing one clip, name tag = the clip; "
           "shared_<kind> = a same-species candidate); start bump = the bump-map test (8 copies, normal ON / OFF); BACK rebuilds the previous pen; the sweep "
           "clears a 48-block square. Pairs with PW-TestRunner RP v0.7.0 (pw:nbump). Earlier: /scriptevent pw:test start walks the witness lineup (48 steps); /scriptevent pw:test start p0 walks "
           "PHASE 0 (the rotation-law PROBE entity, then every RP-07 mob held still in an invisible WITNESS RIG, 35 steps): each step sets itself up, "
           "v0.2.1: P0 PASS = Patrix quality AND one coherent animal, quick FAIL tags vanilla? / magenta? / parts?; rigged mobs are adults; the bar says "
           "NO MOB (and why) when a spawn fails; the pool re-melts its ice; the step title stays 1 s. v0.2.2: /scriptevent pw:test start p1 = the SECOND-WAVE "
           "lineup (26 steps): 11 hostile mobs in a ROOFED pen (no burning), 9 block stations built by commands (torches, lanterns, lit furnaces, lava flow, "
           "nether portal, fire, kelp, campfire smoke, the oak-log cross-pack experiment), 4 size stations (Realm). v0.3.0: p1 v2 (27 steps) replaces the log experiment with the "
           "XPACK PROBE (three blocks pw:xprobe_a/b/c whose texture keys live only in PW-TestRunner RP and point at paths it does not hold - the L-DEDUP-4 decider), "
           "adds SUN / MOON / CLOUDS (RP-02 owns the sky), LEAVES (the 128 tier) and a DEDUPE REGRESSION row; /scriptevent pw:test start p2 = the REALM lineup (9 steps: "
           "4 size stations + deer / alligator / hammer-head shark rendered from PW-StripMine RP). v0.3.1: /scriptevent pw:test start p1r = the 09-28 RE-RUN (16 steps: the fixed hostiles + the void stations); "
           "block states in Bedrock [\"name\"=value] syntax (0.3.0's ':' form never placed); the evoker spawns as minecraft:evocation_illager; every run is saved per lineup - "
           "'report p0' re-emits the last p0 run after other runs, 'runs' lists them; the report is one line per step with the note on it; Repeat setup is logged; "
           "rigged mobs are grown up only when they are babies. v0.3.2: /scriptevent pw:test start p3n = the 09-29 checks (16 steps: horse / donkey / mule "
           "side by side, cat + ocelot, husk + zombie, guardian resting + swimming free in a tank, elder guardian, spider standing + walking, bee, tadpole, "
           "zombified piglin head tilt, piglin, piglin brute, bogged); start p3 adds the 17 unwitnessed RP-07 1.4.16-1.4.18 rebuilds (33 steps). "
           "v0.3.3: /scriptevent pw:test start p4 = the R4 fixes of RP-07 1.4.20 + RP-06 1.4.13 (24 steps: chicken/frog feet, panda rump, tropical fish fins, "
           "spider texture + walk, guardian resting + swimming, rabbit pose, dolphin flippers + steering, mooshroom red/brown A/B, bee + axolotl sizes, "
           "squid / glow squid / enderman / silverfish / tadpole motion, ravager log check, three regression rows seen from above). "
           "v0.3.4: p4 a01 = three chickens - the WHITE temperate one in the middle (entity property set by the runner; the biome gave the dark cold one), warm left, cold right. "
           "v0.3.5: /scriptevent pw:test start p5 = the R6 fixes of RP-07 1.4.21 + RP-06 1.4.15 + RP-08 1.4.8 (20 steps: warm/cold chickens, spider holes, cave spider look, "
           "silverfish model + motion, enderman skin + angry jaw, evoker, pillager log, idle longbow, guardian spikes, dolphin fins, squid A/B, rabbit head, "
           "the mooshroom NAME-TAG probe Moo A-D, four real-size rows); rig mobs can carry a name tag. "
           "v0.3.6: p5 checks RP-07 v1.4.22 (1.4.21 + the enderman wins over the April one in PW-StripMine RP). "
           "v0.3.7: /scriptevent pw:test start p6 = the R8 fixes of RP-07 1.4.23 + RP-06 1.4.16 (10 steps: silverfish visible, squid A/B tilt, enderman "
           "Patrix jaw, tadpole upright, pufferfish spikes, skeleton + wither skeleton grip, a HELD ITEMS row, fox / wolf / sheep); rig mobs can be handed an item. "
           "v0.3.8: /scriptevent pw:test start p7 = the R9 fixes of RP-07 1.4.24 + RP-06 1.4.17 (5 steps: the enderman jaw opens, bows for skeleton / stray / "
           "bogged, a squid tilt VIDEO). "
           "v0.3.9: /scriptevent pw:test start p8 = the R10 fixes of RP-06 1.4.18 + RP-07 1.4.25 (5 steps: the bogged's bow for real, piglin crossbow + "
           "brute / wither skeleton probes, a tamed wolf in wolf armor + a zombified piglin probe); rig mobs can wear body armor. "
           "v0.4.0: /scriptevent pw:test start p9 = the SIZE PARADE for BP-02 1.3.190 + RP-06 1.4.19 + StripMine BP 1.3.4 (15 steps: every animal "
           "resized to real life in a pen beside you, the warden x1.2, the Naturalist steps Realm-only); rigged mobs grow up even when a step fires an event, "
           "and every rigged mob's age is logged. "
           "v0.4.1: /scriptevent pw:test start p10 = FA-1 (RP-06 1.4.20 + RP-07 1.4.26: parrots in five colours + flying + dancing, bat, allay, vex, "
           "phantom, warden, blaze, breeze, creaking, endermite, sniffer on their Patrix models) + the prime-male predators (BP-02 1.3.192 + StripMine "
           "BP 1.3.5), 19 steps; the rig re-rolls babies that cannot grow up and parrots of the wrong colour, places a jukebox (disc by script when the "
           "game allows, else the step gives the commands), sweeps water left around an old pool, and notes when you stand in water. "
           "v0.4.2: /scriptevent pw:test start p11 = the R14 fixes (RP-06 1.4.21 + RP-07 1.4.27 + BP-02 1.3.193 + StripMine BP 1.3.6), 14 steps: "
           "the allay's arms while dancing / holding / flying, the vex's sword + two held-item probes (vex + shard, allay + sword), the blaze glow at "
           "midnight and noon, the polar bear on its Patrix model, the dolphin at 3.1 m, the endermite 25 % smaller, grizzly 2.8 m, alligator 5.5 m, "
           "komodo 3.45 m, rat snake 1.43 m. "
           "v0.4.3: /scriptevent pw:test start p12 = R16a (RP-06 1.4.22 + RP-07 1.4.28 + BP-02 1.3.194), 11 steps: the vex's sword and a shard "
           "(engine version fix), the allay's sword at 70 %, the blaze / magma cube / glow squid lighting their surroundings at midnight, the parrot "
           "and phantom wing joints (true hinge), and a leaf cube around an oak-log core after the leaf state cut (run it in a COPY of the test world); "
           "the rig now PROVES a handed item (testfor hasitem 2 ticks later: 'CONFIRMED in' / 'NOT in') and can set blocks inside the pen. "
           "v0.5.7: p18 / p19 name RP-07 1.4.34 + StripMine BP 1.3.9 (ported models moved under models/entity: 1.4.32 / 1.4.33 animals were "
           "invisible); p19 adds the World Wild Animals seal. 0.5.6 superseded. "
           "v0.5.6: /scriptevent pw:test start p19 = HIS PICKS parade (RP-07 1.4.33 + PW-StripMine BP 1.3.8): every version he kept, grouped by "
           "animal, five to a roofed pen (big ones fewer, swimmers in pools), name tags 'Name (PACK)', + our gorilla / boar / bears beside theirs; "
           "p18 now names the new packs (they hold all of P1). "
           "v0.5.5: /scriptevent pw:test start p18 = the NEW ANIMALS parade (RP-07 1.4.32 + PW-StripMine BP 1.3.7), 34 steps: the 147 creatures "
           "ported from his add-on collection, five to a roofed pen (water ones in pools), name tags on, held still. "
           "v0.5.4: 0.5.3 retired (packaged, never delivered); p17 f03 also checks the z-clipping is gone. "
           "v0.5.3: /scriptevent pw:test start p17 = the LEAF FIXES (BP-02 1.3.198 + RP-01 1.3.107; needs PW-TestRunner RP v0.6.0), 6 steps: "
           "the see-through falling canopy, shears giving our leaf block, the 256 leaves on real trees, and the CULLING PROBE (8 pairs of "
           "coloured test blocks: does a culling rule turn with the block?); notes now have 3 boxes. "
           "v0.5.2: p16 adds m01-m10, the 128 vs 256 LEAF COMPARISON (his 19:33 / 19:41): for 10 trees (all 11 leaf species) THREE identical "
           "copies side by side, WEST to EAST: 128 (BP-02 1.3.197 / RP-01 1.3.106) | 256 colour | 256 colour + MERS 64, every leaf given the same look in the same "
           "spot; the 22 test blocks pw:t256_* / pw:t256m_* need PW-TestRunner RP v0.5.0. "
           "v0.5.1: p16 targets BP-02 1.3.197 + RP-01 1.3.106 and adds n13 (old trees: the relook sweep); tree boxes survive a relog. "
           "v0.5.0: /scriptevent pw:test start p16 = the LEAF ROLLOUT test, 14 steps: new trees, each leaf's look "
           "once, relog, the far switch + shade, every species + the new azalea leaves, felling, decay, by hand, random turns, a forest, and the "
           "/place probe; trees grow by the script API first, then the command, every refusal reason logged. "
           "v0.4.9: every leaf in a tree's box is swapped (diagonal branches included), ticking areas are made inside the tree job, "
           "q9 clears every tree the run grew (wherever you stand) before removing the ticking areas. "
           "v0.4.8: p15 = OUR trees, one species-AGE per step (21: oak / birch / spruce / jungle young..elder, dark + pale oak elders, acacia, mangrove, cherry, azalea); "
           "one tree is grown per step and the others are exact copies (/clone), so today and pilot are judged on the same tree; 27 steps. "
           "v0.4.7: p15 grows its pilot leaves on BP-02 trunks too (pw:<wood>_young..elder), steps queue instead of overlapping, trees stay where the step began. "
           "v0.4.6: /scriptevent pw:test start p15 = the LEAF PILOT (needs PW-TestRunner RP v0.4.0), 16 steps: all 11 Patrix 26.2 leaf species on REAL trees "
           "(the game grows each tree, then its leaves are swapped for the pilot blocks by position), today's leaves beside the pilot and the biome-coloured "
           "pilot, random picture turns off / on, noon shade, the far swap (alpha_test_to_opaque, raw and painted) at 20-116 blocks, a grove for frame rate. "
           "v0.4.5: /scriptevent pw:test start p14 = R17 (RP-06 1.4.24 + RP-07 1.4.31 + BP-02 1.3.195), 13 steps: the iron golem walking from the hips "
           "and attacking, the vex item probe (sword: Mojang arm names; shard: hung on the body), the fox pounce tilt, an item in the fox mouth, "
           "the fox settling sit and daytime nap under a roof, the cod swimming free (view from above), a cat chasing a rabbit and a tame cat sitting, "
           "the leaves after the full state cut. "
           "v0.4.4: /scriptevent pw:test start p13 = R16b (RP-06 1.4.23 + RP-07 1.4.29), 12 steps: the fox (walk, sit, sleep, stalking a "
           "chicken), cat, ocelot (its own model), goat, cod (swimming, flopping on land), iron golem (walk, attack on a zombie), hoglin + "
           "zoglin, all moving with the Patrix model's own animation. "
           "names the screenshots to take, and waits; the CLICKER opens PASS / FAIL / note; every verdict is a [PW-TEST] line in the content log and "
           "'report' re-emits the block for Copy to Clipboard. Job-only: attach at the BOTTOM of the list while testing; pair with PW-TestRunner RP "
           f"v{PILOT_RP_VER} (the pilot leaves, the probe's model and the XPACK keys). Probe + pen are removed at the end of the run, on stop and on reset.")
RP_DESC = (f"v{RP_VER} ({RP_DATE}) TEST RUNNER RP — the pw:probe rotation-law chart entity (geometry, colour-chart texture, additivity animation) used by "
           f"PW-TestRunner BP v{RP_VER} step q1/q2, plus (v0.3.0) the three XPACK PROBE texture keys pw_xprobe_a/b/c in terrain_texture.json that point at paths this pack "
           "does NOT hold (textures/blocks/stone, textures/blocks/mushroom_stem_v3, and a path nobody holds) - p1 station b09 reads which the engine draws. "
           "Job-only: attach at the TOP of the Resource Packs list while testing; it adds one entity + three keys and overlaps nothing.")


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f:
        f.write(f"[{datetime.datetime.now().strftime('%H:%M')} CT {datetime.datetime.now().strftime('%m-%d')}] BUILD {m}\n")


def icon(path, big, small):
    im = Image.new("RGBA", (128, 128), (28, 30, 36, 255)); d = ImageDraw.Draw(im)
    d.rectangle([6, 6, 121, 121], outline=(230, 200, 80, 255), width=4)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    d.text((64, 50), big, fill=(230, 200, 80, 255), font=f, anchor="mm")
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    d.text((64, 88), small, fill=(200, 200, 200, 255), font=f2, anchor="mm")
    im.save(path)


def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()[:8]


SCRIPTS = ("pw_testrunner.js", "pw_testrunner_steps.js", "pw_testrunner_p0.js", "pw_testrunner_p1.js", "pw_testrunner_p2.js", "pw_testrunner_p3.js", "pw_testrunner_p4.js", "pw_testrunner_p5.js", "pw_testrunner_p6.js", "pw_testrunner_p7.js", "pw_testrunner_p8.js", "pw_testrunner_p9.js", "pw_testrunner_p10.js", "pw_testrunner_p11.js", "pw_testrunner_p12.js", "pw_testrunner_p13.js", "pw_testrunner_p14.js", "pw_testrunner_p15.js", "pw_testrunner_p16.js", "pw_testrunner_p17.js", "pw_testrunner_p18.js", "pw_testrunner_p19.js", "pw_testrunner_p20.js", "pw_testrunner_p21.js", "pw_testrunner_bump.js", "pw_testrunner_rig.js")


def build_bp():
    if BP.exists(): shutil.rmtree(BP)
    (BP / "scripts").mkdir(parents=True); (BP / "texts").mkdir()
    v = [int(x) for x in VER.split(".")]
    man = {
        "format_version": 2,
        "header": {"name": f"PW Test Runner BP v{VER}", "description": BP_DESC, "uuid": HEADER_UUID, "version": v, "min_engine_version": [1, 21, 120]},
        "modules": [{"description": "Test runner script — /scriptevent pw:test + the clicker menu", "type": "script", "language": "javascript",
                     "entry": "scripts/main.js", "uuid": MODULE_UUID, "version": v},
                    {"description": "pw:probe — the rotation-law chart entity (behaviour half)", "type": "data", "uuid": DATA_UUID, "version": v}],
        "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}, {"module_name": "@minecraft/server-ui", "version": "2.0.0"}],
        "metadata": {"authors": ["Abs0lum"], "product_type": "addon"},
    }
    (BP / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (BP / "scripts/main.js").write_text(
        f"// main.js — PW Test Runner BP v{VER} — a job-only pack: attach it at the BOTTOM of the Behavior Packs list while testing.\n"
        "// pw_testrunner.js (commands, clicker menu, lineups) · pw_testrunner_steps.js (the witness lineup) · pw_testrunner_p0.js (PHASE 0)\n"
        "// · pw_testrunner_p1.js (P1 v3 + the p1r re-run: hostile rig, stations, XPACK probe, sky, leaves, regression) · pw_testrunner_p2.js (REALM) · pw_testrunner_p3.js (P3 / P3N: the 09-29 mob checks) · pw_testrunner_p4.js (P4: the R4 fixes) · pw_testrunner_p5.js (P5: the R6 fixes) · pw_testrunner_p6.js (P6: the R8 fixes) · pw_testrunner_p7.js (P7: the R9 fixes) · pw_testrunner_p8.js (P8: the R10 fixes) · pw_testrunner_p9.js (P9: the size parade) · pw_testrunner_p10.js (P10: FA-1 + predator sizes) · pw_testrunner_p11.js (P11: the R14 fixes) · pw_testrunner_p12.js (P12: R16a) · pw_testrunner_p13.js (P13: R16b) · pw_testrunner_p14.js (P14: R17) · pw_testrunner_p15.js (P15: the LEAF PILOT + tree planter) · pw_testrunner_p16.js (P16: the LEAF ROLLOUT) · pw_testrunner_p17.js (P17: the LEAF FIXES + culling probe) · pw_testrunner_rig.js (the probe + the mob witness rig).\n"
        "import \"./pw_testrunner.js\";\n", encoding="utf-8")
    for f in SCRIPTS:
        shutil.copyfile(SRC / f, BP / "scripts" / f)
    write_probe_blocks(BP)
    pilot = sorted((ROOT / "_build/leaf-pilot-blocks").glob("pw_*.json")) or sorted((ROOT / "_build/leaf-pilot-blocks").glob("*.json"))
    assert len(pilot) == 24, f"run build_leaf_pilot_rp.py first ({len(pilot)} pilot blocks)"
    for f in pilot: shutil.copyfile(f, BP / "blocks" / ("pw_" + f.name if not f.name.startswith("pw_") else f.name))
    t256 = sorted((ROOT / "_build/t256-blocks").glob("*.json"))
    assert len(t256) == 22, f"run build_t256.py first ({len(t256)} t256 blocks)"
    for f in t256: shutil.copyfile(f, BP / "blocks" / ("pw_" + f.name))
    (BP / "entities").mkdir(exist_ok=True)                                 # v0.5.8: the bump-map test entity (behaviour half)
    shutil.copyfile(ROOT / "_staging/bump/bp/entities/pw_nbump.json", BP / "entities/pw_nbump.json")
    probe = ROOT / "_build/cullprobe-blocks/pw_cullprobe.json"
    assert probe.exists(), "run build_runner_rp060.py first"
    shutil.copyfile(probe, BP / "blocks/pw_cullprobe.json")
    (BP / "texts/en_US.lang").write_text("pack.name=PW Test Runner BP\npack.description=Walks the witness lineup or PHASE 0 (probe + mob rig) step by step. Attach at the BOTTOM of the list while testing; pair with PW Test Runner RP.\n", encoding="utf-8")
    (BP / "texts/languages.json").write_text('["en_US"]\n', encoding="utf-8")
    icon(BP / "pack_icon.png", "TEST", "runner BP")
    (BP / "PW-DEPENDENCIES.md").write_text("# PW-DEPENDENCIES — PW-TestRunner BP\n\nPersonal ledger FOR US (never an engine dependency).\n\n"
        "_Outbound: the P0 probe steps need **PW-TestRunner RP** of the same version attached (pw:probe's client entity); everything else is referenced by id at runtime "
        f"(ItemTypes / BlockTypes / EntityTypes) and reported when missing. No manifest dependency on purpose (L-VV-2). v{VER} pairs with PW-TestRunner RP v{PILOT_RP_VER} (the leaf pilot; built by build_leaf_pilot_rp.py)._\n\n"
        '```json\n{"needs_hash": "none", "external": {"PW-TestRunner RP": "same version (attach both)"}, "unresolved_or_vanilla": 0}\n```\n', encoding="utf-8")


PROBES = {"a": "textures/blocks/stone", "b": "textures/blocks/mushroom_stem_v3", "c": "textures/blocks/pw_xprobe_nowhere"}   # == P1_PROBES in pw_testrunner_p1.js


def write_probe_blocks(bp):
    """The XPACK PROBE blocks (D-C264): three 1.21.80 full-cube blocks; each face draws one terrain key that ONLY the TestRunner RP registers."""
    (bp / "blocks").mkdir(exist_ok=True)
    for k in PROBES:
        blk = {"format_version": "1.21.80",
               "minecraft:block": {"description": {"identifier": f"pw:xprobe_{k}", "menu_category": {"category": "construction"}},
                                   "components": {"minecraft:geometry": "minecraft:geometry.full_block",
                                                  "minecraft:material_instances": {"*": {"texture": f"pw_xprobe_{k}", "render_method": "opaque"}},
                                                  "minecraft:destructible_by_mining": {"seconds_to_destroy": 0.2},
                                                  "minecraft:destructible_by_explosion": {"explosion_resistance": 1},
                                                  "minecraft:friction": 0.6, "minecraft:light_dampening": 15}}}
        (bp / "blocks" / f"pw_xprobe_{k}.json").write_text(json.dumps(blk, indent=1) + "\n", encoding="utf-8")


def write_probe_keys(rp):
    (rp / "textures").mkdir(exist_ok=True)
    tt = {"resource_pack_name": "pw_testrunner", "texture_name": "atlas.terrain", "padding": 8, "num_mip_levels": 4,
          "texture_data": {f"pw_xprobe_{k}": {"textures": v} for k, v in PROBES.items()}}
    (rp / "textures/terrain_texture.json").write_text(json.dumps(tt, indent=1) + "\n", encoding="utf-8")


def build_rp():
    if RP.exists(): shutil.rmtree(RP)
    (RP / "texts").mkdir(parents=True)
    v = [int(x) for x in RP_VER.split(".")]
    man = {"format_version": 2,
           "header": {"name": f"PW Test Runner RP v{RP_VER}", "description": RP_DESC, "uuid": RP_HEADER_UUID, "version": v, "min_engine_version": [1, 21, 80]},
           "modules": [{"type": "resources", "uuid": RP_MODULE_UUID, "version": v}],
           "metadata": {"authors": ["Abs0lum"], "product_type": "addon"}}
    (RP / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (RP / "texts/en_US.lang").write_text("pack.name=PW Test Runner RP\npack.description=The pw:probe rotation-law chart entity for PW Test Runner BP (step q1/q2). Attach at the TOP of the list while testing.\nentity.pw:probe.name=PW Probe\n", encoding="utf-8")
    (RP / "texts/languages.json").write_text('["en_US"]\n', encoding="utf-8")
    with open(RP / "texts/en_US.lang", "a", encoding="utf-8") as f:
        f.write("tile.pw:xprobe_a.name=XPACK probe A (stone path)\ntile.pw:xprobe_b.name=XPACK probe B (RP-01-only path)\ntile.pw:xprobe_c.name=XPACK probe C (no such path)\n")
    icon(RP / "pack_icon.png", "TEST", "runner RP")
    write_probe_keys(RP)
    (RP / "PW-DEPENDENCIES.md").write_text("# PW-DEPENDENCIES — PW-TestRunner RP\n\nPersonal ledger FOR US (never an engine dependency).\n\n"
        "_Provides pw:probe (client entity, geometry.pw_probe, textures/entity/pw_probe, animation.pw_probe.t6, controller.animation.pw_probe, controller.render.pw_probe) "
        "for PW-TestRunner BP of the same version. Needs nothing._\n\n"
        '```json\n{"needs_hash": "none", "external": {}, "unresolved_or_vanilla": 0}\n```\n', encoding="utf-8")


def build_rp070():
    """PW-TestRunner RP 0.7.0 = RP 0.6.0 (the leaf pilot + culling probe, delivered) + the bump-map test's client half (pw:nbump)."""
    src, dst = ROOT / "_build/testrunner-rp-0.6.0", ROOT / f"_build/testrunner-rp-{PILOT_RP_VER}"
    assert not dst.exists(), f"{dst.name} exists — never rebuild a build dir"
    shutil.copytree(src, dst)
    for f in (ROOT / "_staging/bump/rp").rglob("*"):
        if f.is_file():
            t = dst / f.relative_to(ROOT / "_staging/bump/rp")
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, t)
    m = json.loads((dst / "manifest.json").read_text(encoding="utf-8-sig"))
    v = [int(x) for x in PILOT_RP_VER.split(".")]
    m["header"]["version"] = v
    for mod in m["modules"]: mod["version"] = v
    m["header"]["name"] = f"PW Test Runner RP v{PILOT_RP_VER}"
    m["header"]["description"] = f"v{PILOT_RP_VER} ({DATE}) + pw:nbump, the bump-map test (8 looks: warden / dolphin / turtle / parrot x normal ON / OFF). Includes all of v0.6.0."
    (dst / "manifest.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"PW-TestRunner RP v{PILOT_RP_VER} built ({dst.name})")


def main():
    build_bp(); build_rp()
    if not (ROOT / f"_build/testrunner-rp-{PILOT_RP_VER}").exists():   # 0.5.9: RP 0.7.0 is delivered — never rebuilt
        build_rp070()
    probe_assets.write_all(RP, BP)
    probe_assets.figure(ROOT / "_design/p0-probe-predicted.png")
    log(f"PW-TestRunner BP v{VER} built (_build/testrunner-{VER}) — scripts md5 " + "/".join(md5(BP / "scripts" / f) for f in SCRIPTS))
    shipped = ROOT / f"_build/testrunner-rp-{RP_VER}"
    a = {str(q.relative_to(RP)): hashlib.md5(q.read_bytes()).hexdigest() for q in RP.rglob("*") if q.is_file()}
    b = {str(q.relative_to(shipped)): hashlib.md5(q.read_bytes()).hexdigest() for q in shipped.rglob("*") if q.is_file()}
    diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    log(f"PW-TestRunner RP v{RP_VER} rebuilt to {RP.name}: {'IDENTICAL to the shipped RP v' + RP_VER + ' (no re-download needed)' if not diff else 'DIFFERS from the shipped RP: ' + ', '.join(diff[:6])}")


if __name__ == "__main__":
    main()
