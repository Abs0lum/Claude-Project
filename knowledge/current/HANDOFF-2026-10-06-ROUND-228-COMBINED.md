# HANDOFF 2026-10-06 — ROUND 228 COMBINED (the civ mods integrated; role beds; palace spirals; children's beds; fillers)

This document is the CURRENT-STATE after 2026-10-06 evening (CT). Read DECISIONS-2026-10-06.md (program 228) for every ruling.

## What ships (one combined test, his 15:23: "test all of the new implementations at once")
| Pack | Version | Notes |
|---|---|---|
| BP-02 AbsolutRealism Tectonic BP | 1.3.228 | B1–B12 civ mods + role beds + palace spirals + children's beds + street fillers; Script API 2.10.0 |
| RP-04 AbsolutRealism Basic RP | 1.3.159 | 1.3.158 + the silver nickel icon (192 MB) |
| RP-13 AbsolutRealism Architecture RP | 1.0.0 | NEW (his 250 MB rule): the 8-block ramps (19 stones) + the spiral stairs (A/B/C × stone/oak/spruce+plaster) |
| RP-01 AbsolutRealism Tectonic RP | 1.3.125 | tree trunk tips (trees 228) |
| unchanged | | PW-Civitas-Markers BP 0.2.4, RP-12 1.0.1, RP-10 (pw_snowcap) |
Remove: the AR Spiral Stairs Test packs (0.0.1–0.0.3) — the main packs carry pw:spiral_pad.

## Status: shipped to Drive ClaudeUploads 21:58 CT, awaiting his verification (P1)
- BP-02 1.3.228 md5 f146f7d3 (13,952,229 B) · RP-04 1.3.159 md5 6e431653 · RP-13 1.0.0 md5 2a0fbb64 · RP-01 1.3.125 md5 c9d3ae1b
  (Drive md5 == local for all four + TEST-CHECKLIST-228.md).
- GATE 228-13 PASS (tools/gate_check.py): economy PASS · built PASS (village built 5/14; City II 87/91) · people PASS (peak 176,
  142 at day 200) · watch PASS (on duty, 3 rounds, 2 sewer climbs) · 0 Hang · 0 Crash · palace 4/4 finished · court admitted 35
  (lord 1, nobles 11, servants 7, guards 4) · manholes 8/9 · walk 440 arrived.
- TWO REGRESSIONS FOUND AND FIXED in the final gates (both from this round):
  1. D-C1006-WAGONS: the async land survey (B1/TR4) let the economy open the ledger before founding -> settlers' wagons with
     no timber/planks -> the town never built (6 of 11 round-228 gates). Fix: no ledger until phase "built" (NOT st.planned:
     a kit founding never clears it — gate 228-12 ran with no economy at all).
  2. D-C1006-WATCH: B4's "nearest free job" dropped the town posts' priority -> no watchmen / sewer keeper ever hired.
     Fix: town posts (string ids) before shops, nearest within each class (test_shifts a2/a3).
- MY REPORTING ERRORS this evening: I read "N building(s)" (staged plots) and forced tier names as progress for 228-5 and
  228-9, and briefly reported 228-12's free (no-economy) building as a pass. gate_check.py now gates every report.
- Known, not a regression: the founding generation dies ~day 170-200 (lifespan 130-160 days) and the faucet (every 5 days)
  + births cannot replace it (228-10 the same) -> part of the HOUSEHOLDS & DYNASTY program and the population goal.

## The batches (FIT-MATRIX, fitted to OUR model)
- B5 voice: bubbles, PE11 stop-and-face, overheard talk at dusk, petitions + promise threads.
- B6 growth: weighted charter order, rest after failed searches, `pw:clock prio`, district skins, relief percentiles, TR1,
  GB14 headroom, GB9 local ground, EN2 weathering (fines + repairs), GB13 FILLERS (well/bench/cart/lamp in short gaps).
- B7/B8: silver nickel (1 p), exact prices, reserves, notices, carters, tax dial (free command), audit/board.
- B9: street names, town titles, "Now entering".
- B10 watch: posts paid first, morale + half rounds + leaving, crime MEASURED (OFF), bell alarm, civs band against monsters,
  watch lights, the chronicle (annals).
- B11 player: standing prices, talk fatigue + gifts, deeds BUILT/OFF, festivals (wedding, tier feast, monthly holiday),
  dusk speech, titles + district vote, the guide.
- B12: Script API 2.10.0 (BDS probe).
- ROLE BEDS (1.3.229 scope, folded in): palace beds by room role; couples = nobles (district reps first) + up to 2 children
  (children's beds, his 17:52/18:02); single watchmen/clerks/best cooks + tradesmen serve; reserved; `pw:clock beds`.
- PALACE SPIRALS (his 18:0x 'rework rooms now'): gatehouse A + C, prison tower C, 5 back stairs B, commons B (stair hall),
  coach house B; mid-floor doors beside the step (door piece), the floor in front at the top; solver-checked.

## Engine laws learned (lesson candidates — see decision journal LC-1006-SP)
- Structure rotation rotates custom cardinal states (90 = clockwise); mirror does not touch custom states -> never mirror.
- Block ids are lowercased at runtime.
- Stairs of custom blocks are laid LAST in generators.
- Spiral exits sit on faces fixed by the floor spacing mod 4: wells need floor on the sides the exits fall.

## Queued (his order)
0. HOUSEHOLDS & DYNASTY (his 21:39/21:47, next after this release): move out at adulthood into a better free home; dynasty link; heirs sell the parents' home; every move out/in restores the home from weathered to fresh (builders' job, money spent; sales repay it). See D-C1006-DYN.
1. PALACE II (his 18:22): enlarge from real blueprints — secret passages/doors/stairs, underground ways, children's rooms.
2. Diagonal catwalks/skyways (his 17:58): 45-degree pieces, structures only; images first.
3. Castles into the game (design now: A towers, C keeps/lodgings, thatch gables, caphouses); keep_4 8 cells to fix.
4. Furniture import (Feudal / Rustic / Medievalism shapes re-skinned) — needs his markup.
5. Low: grass skirt tint; acacia branch ends; frontage plateau.

## Witness items for him
- PS5 save-on-close; the spiral pad walk test (each stair ends flush, forward exit; mid-floor side exits in the palace);
  everything on TEST-CHECKLIST-228.md.
