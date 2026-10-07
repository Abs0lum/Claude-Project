# HANDOFF — 2026-10-02 evening — ROUND 1002n (complete-set build in progress, nothing delivered yet)

SUPPLEMENT to `HANDOFF-2026-10-01-STD-ROUND.md`, which stays authoritative for everything not listed here; this file is authoritative for round 1002n (2026-10-02) until the next full handoff. Journal: `_logs/decision_journal.md` D-C470 … D-C483 + RETRO-SWEEP 18:5x. Phase log: `_logs/phase_log.md`.

## 1. Undelivered builds (never rebuild once delivered; all accumulate into ONE gofile folder at the end)
| Pack | Build dir | Contents this round |
|---|---|---|
| BP-02 1.3.206 | `_build/bp02-206` | StripMine BP merged · biome fixes 206 + 206b · 557 generated spawn rules (`tools/spawn_gen.py`; 43 group fixes, ants on hills, 7 no-rule creatures, despawn on 160) · tiny-mobs round (186 neutral, 59 Giant twins, 34 size fixes) · 6 pond features · village clock + building stages (`pw_civ_clock.js`, `structures/pw/stages/`) · felling rules F1/F4/F5/F6/F7/F8/F9 (`pw_fell_rules.js`) · 17 root blocks + 17 stump blocks · randomizer guard (rseed) · scanner switch `PW_SCANNER_ON=true` (flip when T2 complete) · event-driven leaf decay · `/scriptevent pw:leaf_finish` · `structures/pw/roof_kit` |
| RP-07 1.4.44 | `_build/rp07-1444` | StripMine RP merged (sounds, defs, blocks, attachables) · 59 Giant client entities + lang + sounds · creature normals (staged, NOT applied) |
| RP-08 1.4.13 | `_build/rp08-1413` | StripMine icons · 15 Naturalist egg terrain keys (moved from RP-07) · 13 Naturalist block sets · creature normals (staged) |
| RP-02 2.0.7 | `_build/rp02-207` | StripMine VV globals · 115 ambience sounds `stream: true` (PS5 load candidate fix) |
| RP-01 1.3.117 | `_build/rp01-117` | 17 stump ring textures + keys (manifest NOT yet bumped) |
| RP-11 1.3.40 / RP-04 1.3.156 / RP-03 1.3.67 | | ore round + roof cut-outs restored (r1002m) |
| TestRunner BP 0.5.13 | `_build/testrunner-0.5.13` | `/scriptevent pw:time …` → BP-02 clock; StripMine lines annotated |
| (new needed) RP-06 1.4.29 | — | 5 creature normals (1.4.28 delivered) |
Change list for manifests: `_docs/ROUND-1002n-CHANGES.md`.

## 2. Open questions (his answers gate the rest)
- **TP1–TP4** oak pilot shapes + overall size (`outputs/TREE-PILOT-oak.png`) · **TC** 320 vs 528 tree templates → T2 all species, T4 exact falling models, flip scanner switch, template-exact falling set.
- **N1 / N2** creature normal strength / fur strands (`outputs/CREATURE-NORMALS-BEFORE-AFTER.png`) → task #172 apply.
- **CT1 / CT2** cottage contents + decor (`outputs/COTTAGE-r0-CENSUS.png`; his r0 has NO stations / zones / decor).
- **SR** stump rings (`outputs/STUMP-RINGS-PREVIEW.png`) · **RK1–RK6** roof pieces keep / fix / delete (`outputs/ROOF-KIT.png`).
- **NS1** Naturalist scripts off / on / partial (feasibility: loads with 0 errors once `@minecraft/` lib copied; 10 custom-component lines to restore).
- **E1–E7** economy (`_docs/civ/CIVITAS-LIVING-ECONOMY-v1-DRAFT-2026-10-02.md`).

## 3. Verified (static + BDS 1.26.52.3; P1: witness still decides)
Ownership O1 0 · block census final stack OK 3,817 · 5 BPs together 0 ERROR · .mcpack sizes < 250 MB (RP-04 190, RP-07 160→~178 with normals) · BDS probes: ponds hold water over air (6/6, after a seal-layer fix), Giants summon at scale, clock stages + snapshot, worldgen keeps custom states + rotates traits (T0), lying log / attached drops / stumps / crown lean, event decay 8/8.

## 4. Witness items (test brief artifact BUYCkYYg2izEcYSpgYGmDk, areas A–P)
Remove StripMine RP + BP · sound start time on PS5 · buffalo / anteater depth · ants at hills · animals thin out far away · ponds · Giants · time tool · felling (real player breaks) · leaf finisher · roof kit.

## 5. New tools (all in `tools/`)
mob_pbr_reach · mob_normals (+sheet) · spawn_group_audit · spawn_gen · biome_fixes_206b · tiny_mobs_round · lake_features · sound_load_census · sound_stream_fix · civ_stages · bp02_src/pw_civ_clock.js · tree_gen · tree_roots · tree_stumps · stump_textures · bp02_src/pw_fell_rules.js (+ test_fell mock 12/12) · cottage_census_sheet · roof_kit (+ render). BDS job-only probes: pondprobe, clockprobe, treeprobe, fellprobe, decayprobe, finishprobe (never shipped).
