# HANDOFF 2026-10-07 — STATE AFTER ROUND 228/229, THE PS5 JOIN CRASH AND THE IMMEDIATE SET

This is the CURRENT-STATE as of 2026-10-07 ~01:00 CT. It extends `HANDOFF-2026-10-06-ROUND-228-COMBINED.md` (read that
first for the round-228 content) and the decision journal entries D-C1006-* (knowledge/logs/decision_journal.md).

## 1. What is in his world now (witnessed loading clean on the second load, 23:00 CT 10-06)
| Pack | Version | md5 (Drive == local) | Note |
|---|---|---|---|
| BP-02 AbsolutRealism Tectonic BP | 1.3.229 | 488305ee | 1.3.228 + spiral geometry ids lowercased |
| RP-13 AbsolutRealism Architecture RP | 1.0.1 | 271043dd | ramps-8 + spiral stairs; geo ids lowercase, format 1.16.0 |
| RP-04 AbsolutRealism Basic RP | 1.3.159 | 6e431653 | |
| RP-01 AbsolutRealism Tectonic RP | 1.3.125 | c9d3ae1b | |
| PW-Civitas-Markers BP | 0.2.4 | — | must stay attached (he asked 22:0x; yes) |
| RP-12 Gallery 1.0.1, RP-10 (pw_snowcap) | unchanged | — | |
- Witnessed: the "cannot find geometry.pw_spiral_*" errors are gone (D-C1006-GEO). Which difference caused it (case or
  geometry format 1.21.0) is NOT separated — both were removed together.
- Remaining content-log warnings (not errors): un-weighted `variations` arrays (spruce_planks on pw:jib_panel and
  pw:secret_painting; acacia/mangrove/cherry_log_top on the roots); the PW-C2 banner still says "pack v1.3.228 · expects
  RP-04 v1.3.156" (stale strings).

## 2. OPEN — PS5 crashes as soon as it joins (his 00:23 CT 10-07; error CE-108255-1; HIS FIRST PRIORITY)
- Setup: the phone hosts the world; the PS5 ("Alm1tr4") joins and crashes at once.
- Leading hypothesis (UNPROVEN): the world's block-permutation count. Our BPs define 57,512 permutations (BP-02 1.3.229
  55,891 + Markers 1,621; BP-02 1.3.227 had 34,536). Microsoft documents 65,536 for all blocks of a world; vanilla adds its
  own. The 266 ramp blocks alone are 21,760 (pw:var 4/8 x pw:snow 5 x 4 directions).
- Isolation build READY, NOT YET ON DRIVE: BP-02 1.3.230 SLIM = 1.3.229 with the ramps' pw:var state removed (variant 0
  kept) -> BP-02 36,571 permutations (+ markers = 38,192). `/mnt/user-data/outputs/BP-02-AbsolutRealism-Tectonic-BP-v1_3_230.mcpack`
  13,760,757 B md5 ee51154f. Builder `tools/build_slim_230.py`, packager `tools/package_slim_230.py`.
  Gate `bds_civtest --seconds 3000 _build/bp02-230` running (`_logs/gate_230s.out`): economy/built/people PASS, 0 hang/crash
  at the last read.
- Tests sent to him (answers pending): (a) Vibrant Visuals off on the PS5; (b) remove RP-12 Gallery; (c) the SLIM BP-02.
  Questions pending: did 1.3.227 join fine on the PS5? does the phone's content log say "over 65536 block permutations"?
- If the cap is confirmed: a permanent ramp-variant design (texture variety by other means) is an owner decision.

## 3. His 00:23 CT 10-07 report (46 screenshots, 46/46 viewed; ledger in logs/intake_ledger.md) — all OPEN
1. Inn: open 24 h / late, several employees; rooms of two 4-bed sets, 1 block apart, at least 6 rooms.
2. Ramp-8 slopes: dirt not removed above the slopes (could not break it in creative; maybe a load glitch) — investigate.
3. Civs struggle to slope up / grow on elevation: use 4-part slope switchbacks until the survey can run again; survey a
   MUCH larger area and plan for elevation.
4. Paintings: flush on N/S walls but not E/W (or the reverse) — investigate the facing transform.
5. Patrix bed legs clip through the north face.
6. Skyways "look amazing"; more angles later (the spiral gives ~360 degrees of directions) — prepare requirements.
7. Texture variants: grass, dirt, sand stay high; everything else 6–16 variants; count the savings; list what can drop to
   128x (incl. MERS + normals).
8. Can a resource pack be "parted out" (part 1/part 2, or multipart that recombines) keeping each part < 250 MB? — answer.
9. Academy II: a central building with many connected wings/auxiliaries, courtyards and outside hallways.
10. Trees: acacia better, but "the primary issues are with the dodecagon, primarily birch, oak and spruce".
11. Furniture: he wants them all, but check the skins — books on shelves render as wood; cosmetic accessories (books,
    pinned notes, lampshades) need their own textures. He tests tinting after.

## 4. The IMMEDIATE set (his 22:18 CT 10-06; he tests after ALL are done) — status
| # | Item | Status |
|---|---|---|
| 0 | Households & Dynasty | DONE in source (tools/bp02_src_228; test_households 95/95; all 25 suites pass); not built |
| 1 | Palace II (4x4 = 256x256, real blueprints, secret stairs design A, nursery for 4, secrets "1+3") | research done (_docs/palace/PALACE-II-RESEARCH-2026-10-06.md); generator agent launch was REJECTED by him once — re-propose |
| 2 | Skyways (option C) | rail family staged in _staging/skyway230 (BDS load 0 errors); not installed |
| 3 | Castles ("design everything we need") | design done (_docs/castle/CASTLE-DESIGN-COMPLETE-2026-10-06.md; castlegen cut() bug n = W // 64); generator fix launch REJECTED once — re-propose |
| 3b | Castle Academy II (6x6 = 384x384; new student + master roles) | design done (_docs/castle/ACADEMY-II-*); must be re-planned per his 00:23 item 9 |
| 4 | Furniture | 155 candidates, 12 sheets (_docs/furniture); skins check pending (item 11) |
| 5 | Grass skirt tint | findings done; needs his swamp screenshot (natural grass vs pw:grass_block vs pw:slab_grass) |
| 5 | Acacia limb ends | staged (_staging/acacia_230; sky-visible logs 255 -> 2); install into the next build |
| 5 | Frontage plateau | DONE in source (test_plateau 76/76); owner dial cutMax/fillMax 6 vs 9 PENDING |

## 5. Standing facts that matter for the next session
- Population goal: 5,000–10,000 EVENTUALLY; the capacity must exist in the packs now; tests do not push that far; memory
  and lag work later.
- Gate law: every gate report goes through `tools/gate_check.py` (wagons / economy / built / people / watch / health) —
  never staged "N building(s)" or forced tier names.
- Geometry law (lesson candidate): block geometry ids lowercase, geometry format 1.16.0; `tools/geo_ref_check.py` on every
  build (BDS never loads RP geometry, so no gate can catch it).
- Versions are never reused; every pack <= 250 MB; complete packs only (no hotfix overlays).
- claude.ai Project knowledge is FULL (1,999,094 / 2,000,000 B) — writes refused. Candidates to remove (only on his
  explicit ask): the ~280 `claude/tools/*` copies (all live in the knowledge mirror and the workspace) and duplicate
  handoffs.
- Knowledge mirror (from 10-07): `tools/knowledge_bundle.py` -> Drive `ClaudeUploads/knowledge/` + the GitHub repo
  (`knowledge/`, `prompts/`, `claude-settings/`).
