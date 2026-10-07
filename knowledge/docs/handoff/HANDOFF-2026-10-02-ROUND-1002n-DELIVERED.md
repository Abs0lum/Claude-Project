# HANDOFF 2026-10-02 (evening) — ROUND 1002n COMPLETE SET DELIVERED
Supersedes HANDOFF-2026-10-02-ROUND-1002n.md as CURRENT-STATE. Append point for HISTORY-v4.

## Delivered — gofile JN156eFu (folder AR-1002n-complete-set, PUBLIC, 10/10 PASS, 20:1x CT)
| Pack | Version | md5 (first 8) | Size |
|---|---|---|---|
| BP-02 Tectonic BP | 1.3.206 | 17107f8f | 5.1 MB |
| RP-01 Tectonic RP | 1.3.117 | 90edff7f | 135.6 MB |
| RP-02 Atmospheric Effects | 2.0.7 | df643d6c | 92.7 MB |
| RP-03 PBR | 1.3.67 | 26a7eaec | 116.8 MB |
| RP-04 Basic | 1.3.156 | b7b3fa3d | 192.3 MB |
| RP-06 Hostile Mobs | 1.4.29 | 1f5573ce | 54.6 MB |
| RP-07 Neutral Mobs | 1.4.44 | 2678fe09 | 151.5 MB |
| RP-08 Items | 1.4.13 | bf8bf6e9 | 108.5 MB |
| RP-11 Ores | 1.3.40 | 81458944 | 15.1 MB |
| PW-TestRunner BP | 0.5.13 | 284b7c0a | 0.3 MB |
Unchanged (keep installed): RP-05 1.3.58 · RP-10 1.3.51 · BP-01 1.3.35 · BP-03 1.3.34 · Markers BP 0.2.1 / RP 0.2.2. REMOVE: PW StripMine RP + BP (merged).
Gates: BDS 5 BPs 0 ERROR · ownership O1 0 · permutations 34,182 · all < 250 MB. Test brief artifact v3 (areas A–P, M8–M10, O1 trees, P2–P5 roofs/walls/ramps).

## What this set carries (all "shipped, awaiting witness")
- StripMine dissolved into RP-07/RP-08/RP-02/BP-02; Naturalist textures unnested to textures/entity|blocks|items|particle/sf_nba (one copy, RP-08); Naturalist scripts ON (ants, despawn, hamsters, eggs, info book…); 15 egg block keys in RP-08.
- Creature maps: 2,197 textures OK (derived normals, fur strands N2 = b, Patrix normals where present); reach census tool.
- Spawning: 557 generated rules (groups by body, water animals, ants on hills, despawn on 160); biome fixes 206b; 59 Giant twins; 186 small mobs neutral; 34 size fixes; 6 sealed ponds with fish.
- Sound: 115 long sounds stream.
- CIVITAS: village clock + /scriptevent pw:clock (plot/step/skip/snapshot), cottage stages s0–s4, TestRunner pw:time forwarder.
- Trees (T1/T2/T5): 544 templates (oak/birch/spruce/jungle 24 per age; 5 elders + acacia/cherry/mangrove 32) in BP-02 structures/pw/trees, wired into every tree pool (vanilla chain intact; *_with_vines aggregates kept); root blocks pw:<tier>_root (pw:tpl 0..15 + pw:tpl_hi 0..1 — ENGINE LAW: a state enum holds ≤ 16 values); stumps with growth rings; scanner OFF; event-driven leaf decay; /scriptevent pw:leaf_finish; felling rules F1/F4–F9 (verdict, ledger, natural canopy, attached drops, lying log, stumps, crown lean).
- Roofs (#174, measured transformation law D-C487): hip, pyramidion (pointed), gussets, crown ring (2 geometries), roof63 upper map, ridge end rules; companion v7 (Rules A/B/C/G re-derived; D/E room walls fixed); roof kit 46×5×11 (6 assemblies).
- Placement census (#175): rafter45 slope, ramp snow uv windows, census tool + facings sheets.

## Engine laws learned this round (lesson candidates, witness pending)
- L-XFORM-LAW: minecraft:transformation rotates in WORLD space, right-handed, X→Y→Z, about the block centre; bone/cube rotations keep the file-space bone law (D-C255). (BDS-measured, 12/12.)
- L-STATE-16: a block state enum array holds at most 16 values (BDS error text).
- L-WG-STATES / L-SET-REACH / L-NAT-SCRIPTS / L-STREAM (see D-C477/470/471/475).

## Rulings in force (this round)
- 19:21 "check EVERYTHING there is to check about ANYTHING there is to see" = default on any 'looks wrong'.
- 20:04 "I defer to your discretion for all initial decisions – if based on research; no other questions before I can test CIVITAS as full functionality, including evolutions." → decisions logged as ASSUMPTIONs; no questions.
- Economy E1–E7 answered (all five ladder rungs; break-away rivals; ~60/~200 days; decline yes; CIVITAS coin + emerald exchange; all three thread channels; build order 1–8 + immigration); tier ladder village v1 → v2 → town → town II (multiple sellers of the same goods causes the city) → city.
- CT1 = d (my station/zone/decor proposals), CT2 = a (minimum village only), TC = my call (24/32), TP keep + TP4 realistic, SR = a, N1 = a (+backlog), NS1 = b.

## Open / next (in order)
1. CIVITAS build-out toward "full functionality incl. evolutions": cottage r1 stations/zones/sparse decor (CT1 d) → regenerate stages; village v1 generator (min requirements) + v2 diversification; town / town II / city tiers; clock-driven evolution; metabolism (ledger, day segments, stations) → production/stock/prices → competition → roads/wagons → ladder → population/immigration/decline → threads. Each phase: TestRunner lineup + BDS probe + delivery.
2. T4 exact falling models per template (template-exact falling set); TREEGROW sapling upgrade; P-4 state-migration probe; acacia/cherry/mangrove root blocks.
3. Open checks: t2b area showed 527 minecraft:spruce_log with no template spruce (fallen logs? a vanilla feature? a taiga village?) — next probe counts planks/leaves; companion Rules A–H runtime (needs a player → witness or mock); bone_visibility no longer relied on.
4. Backlog: N1 revisit on complaint; retro-sweep hits (onPlace re-roll audit, items/attachables reach census, geo_preview transformation law, lessons after witness); roof_ridge_end side uvs beyond 64 (witnessed clean, left).

## Amnesia anchors
_logs/phase_log.md (last: DELIVERED JN156eFu) · decision journal D-C486–D-C492 · _docs/ROUND-1002n-CHANGES.md · backups _docs/blocks/before_roof_fix_174, before_placement_fix_175, _docs/trees/before_t2.
Delivered dirs FROZEN: bp02-206 rp01-117 rp02-207 rp03-67 rp04-156 rp06-1429 rp07-1444 rp08-1413 rp11-140 testrunner-0.5.13 → next builds bp02-207, rp04-157, rp01-118 …
