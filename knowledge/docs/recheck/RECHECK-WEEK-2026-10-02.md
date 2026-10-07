# RECHECK-WEEK 2026-10-02 (his 21:45 "recheck all our work for the week") — FINDINGS
Scope: everything delivered or built Mon 09-28 → Fri 10-02 22:15 CT, judged against the CURRENT INSTALL SET
(HANDOFF-2026-10-02-ROUND-1002n-DELIVERED: the 10 packs of gofile JN156eFu + RP-05 1.3.58, RP-10 1.3.51, BP-01 1.3.35,
BP-03 1.3.34, Markers BP 0.2.1 / RP 0.2.2). Every earlier delivery of the week is superseded by this set, so the set is what
was re-checked; the week's tools and tests were re-run against it. Delivered builds were NOT modified (frozen); every fix is
queued for a new version number. Tools: tools/recheck_r1.py … recheck_r6.py (re-runnable; results in _docs/recheck/*.json).

## Verdict in one line
The installed set is sound: 16/16 archives intact and frozen, 0 server errors, 0 Molang errors, every mock suite green,
every subsystem audit at its known state. SIX defects found (none fatal, one visible): see §A. Thirteen tooling/doc hygiene
items: §B. Three facts the 20:13 handoff stated that were wrong: §C.

## A. Defects in the installed set (fix queue, by pack)
| # | Pack (delivered) | Defect | Effect in game | Fix (new version) |
|---|---|---|---|---|
| A1 | RP-07 1.4.44 | `entity/std/minecraft_cave_spider.entity.json` has no `min_engine_version`; vanilla's carries 1.8.0 → by L-ENT-PREC the vanilla definition wins | **our cave spider is never drawn** (vanilla model shows). Present since the std round; the PREC gate only compared packs above ours, never vanilla | RP-07 1.4.45: add `"min_engine_version": "1.21.0"`; gate now runs with vanilla in the order (tools/recheck_r6 PREC) |
| A2 | RP-07 1.4.44 / RP-08 1.4.13 | 13 Naturalist block terrain keys (sf_nba.ant_hill/_base, chrysalis_stage0-2, shellstone ×4, starfish_placeable_0-3) are declared in RP-07's terrain_texture.json while the images + texture sets live in RP-08 | none visible (the game resolves the path across the stack); breaks the one-pack ownership law (O1) | RP-08 1.4.14: take the 13 keys; RP-07 1.4.45: drop its terrain_texture.json |
| A3 | RP-07 1.4.44 | walrus declares `idle_event` → `animation.sf_nba.walrus.idle_event`; whale declares `baby_tilt_lerp` → `animation.sf_nba.whale_baby.tilt_lerp`; neither animation exists anywhere (came in with the Naturalist add-on; noted D-C283 09-29 as "latent", never cleaned) | nothing plays them; at worst a content-log "can't find animation" line | RP-07 1.4.45: remove the two map entries |
| A4 | BP-02 1.3.206 | recipe `pw:wall_oak_planks` (3 planks in a column) has the same ingredients as `pw:room_wall` — crafting_table AND pw:builders_table; backlog since D-C265 (09-28), never landed | the game registers both; the crafting grid shows one of them for the pattern | **DONE in BP-02 1.3.207**: wall panel = 2×3 planks → 6 |
| A5 | BP-02 1.3.206 | structures/pw/mvv_cottage_s_a_r1.mcstructure is the PRE-station-law cottage (stations beside their fixtures — his 20:21 "and the stations") | the 206 village clock's cottage carries wrong station markers | **DONE in BP-02 1.3.207** (corrected roster, 13 buildings) |
| A6 | TestRunner 0.5.13 | `RUNNER_VERSION = "0.5.11"` — the boot banner announces 0.5.11 inside the 0.5.13 build (0.5.12/13 bumps skipped the constant) | version-flag law broken: his content log cannot prove which runner loaded | TestRunner 0.5.14: bump + a packager assert (RUNNER_VERSION == manifest) |
Cosmetic (same fix round): RP-01 1.3.117 and RP-06 1.4.29 `header.description` lead with the previous version; PW-DEPENDENCIES.md
stamps stale in BP-02, RP-04, RP-06, RP-08, RP-10, Markers RP.

## B. Tooling / documentation hygiene (fixed where marked)
- B1 FIXED — fell-rules mock lacked BlockPermutation / BlockVolume / BlockTypes (added in T3 steps 2–3); the suite could not run on the shipped module. Stubs added; 12/12 on 206 and 207.
- B2 FIXED — TestRunner mock pinned `/home/claude/_build/bp02-197/scripts/main.js` (gone); now argv[3], default bp02-206. 344/344.
- B3 FIXED — hearth-fog test expected the pre-1.3.187 boot line; regex now accepts "(since vX)". 11/11.
- B4 FIXED — plank-grid + 3D-vine mocks lived only in the scratch area; preserved at tools/bp02_src/test_planks_vine (8/8, 4/4, 7/7). test.mjs there is the superseded first version (fails by design; test2.mjs is the live one).
- B5 FIXED — anim_resolve_lint must be run with `--stack` (RP-08's egg entities use RP-07's animations); the R4 first pass without it reported 37 false misses.
- B6 — spawn_group_audit reports from a cached census ("current" column); the live rules in 206 match "should" 43/43. Tool should read live rules.
- B7 — all_mob_size_census / face_alpha_census pin old build dirs by default (env overrides exist for some). Point them at the stack resolver.
- B8 — the standing script gate is now one command: `python3 tools/recheck_r5.py` (seven suites). Proposed as the ship-sequence gate.
- B9 — the PREC gate must include vanilla in the order (A1). recheck_r6 does.
- B10 — project tool mirror (claude/tools) stops at 09-30 14:40: nothing from the leaf pilot, menagerie, StripMine dissolve, trees T1/T2, roofs #174, placement #175, CIVITAS roster/stages/clock/probes, spawn_gen is in the project. Project knowledge is at 1.52 of 2.0 MB → curate: publish only standing gates + pipeline entry points (list in §E), not every build script.
- B11 — the project holds duplicate copies of the same handoff titles (HANDOFF-SESSION-2026-07-19-* ×7, 2026-08-09 ×2, PW-GIVE-LIST ×2, MOB-CONVERSION-PHASE0 ×2 …) eating the cap; his call to retire.
- B12 — Drive AR-Licensing holds 7+ files named RESTRICTED-ASSETS.md (each upload creates a new file; the ledger names the valid one: id 1rc4ZU7U…, md5 91fa96da == workspace copy ✅). Never-delete rule → his call to trash the old copies; gdrive_upload could update in place.
- B13 — two Naturalist recipe files start with a `/* … */` block comment (the game accepts; strict JSON tools must strip it) — no action.

## C. Handoff statements corrected
- "ownership O1 0" → O1 13 (A2). The gate was last run at 16:37Z (round 1002h), before the StripMine dissolve moved the sf_nba keys; it was not re-run for the final set (my gate skip, P8).
- "BDS 5 BPs 0 ERROR" → still true, and now 5 BP + 11 RP, 0 ERROR; the 2 recipe WARN lines (A4) were in the baseline.
- CIVITAS "cottage stages s0–s4" in 206 → the 206 cottage is the pre-station-law file (A5); 207 carries the corrected roster.

## D. What passed (so it is on record)
R1 16/16 archives == ledger md5, archive == build dir, < 250 MB · R2 UUIDs unique, deps resolve, versions == names · R3 server
start 0 ERROR · R4 Molang 0/57,967, FMT 0, RCV 0, ATT 0, game-log gates 0, anim-resolve (with stack) 0 new beyond A3 + 4 vanilla-sample
gaps (breeze ×2, warden ×2) · state enums ≤ 16 · api_audit 5 flags = plain-object members (spec.path, phase.count, pos, mobCollision.width)
+ `airSupply` guarded by `in` → accepted · R5 all suites green (B1–B4) · R6 roofs (seams ≤ 2.0, gusset 3.2), placement census notes
only (known offsets −90/180), markers 13/13, stage proof 65/65 byte-equal in 207, trees 544/544/24 pools/34 rules, precedence 74
shared ids (A1 the only loss), spawn groups 43/43, sizes/MERS/sounds reports (MERS: Naturalist insects/eel roughness 0.24–0.46 —
glossy; for his eyes) · R7 village probe 13/13 at two rotations + snapshot round-trip; civtest on 206 48/52 + 12/13 (all fails = A5)
· R8 handoff in project == local; RESTRICTED-ASSETS Drive == workspace; B1 quartz-ore and the dissolve note present; provenance
files ride in BP-02/RP-07.

## E. Publish list for the project tool mirror (curated, within the cap)
tools/recheck_r1..r6.py · civ_roster.py · civ_stages.py · civ_marker_audit.py · civ_village_data.py · civ_village_probe.py ·
civ_dump_render.py · bp02_src/pw_civ_clock.js · tree_gen.py · tree_gen_square.py · tree_roots.py · tree_wire_t2.py ·
roof_audit.py · roof_seams.py · roof_heightfield.py · roof_fix_174.py · block_placement_census.py · placement_fix_175.py ·
spawn_gen.py · spawn_group_audit.py · entity_precedence.py (unchanged) · this document.
