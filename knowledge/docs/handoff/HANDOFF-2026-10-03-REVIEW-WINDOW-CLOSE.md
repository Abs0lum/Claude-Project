# HANDOFF — 2026-10-03 — REVIEW WINDOW CLOSED: current state for your return

This is the **current state**. It supersedes `HANDOFF-2026-10-03-LIGHTFIX-1003g.md` and `HANDOFF-2026-10-03-REVIEW-WINDOW-1003e-f.md` for everything listed here. The full review is in `REVIEW-WEEK-2026-10-03.md`; the reasoning is in journal entries D-C504 … D-C520. Personal use only (§9).

## 1. Install
| Pack | Version |
|---|---|
| **BP-02 Tectonic BP** | **1.3.214** (the light fix; replaces 1.3.207 … 1.3.212) |
| **PW-TestRunner BP** | **0.5.20** |
| BP-01 1.3.35 · BP-03 1.3.34 · Markers BP 0.2.1 / RP 0.2.2 | unchanged |
| RP-01 1.3.118 · RP-02 2.0.7 · RP-03 1.3.67 · RP-04 1.3.156 · RP-05 1.3.58 · RP-06 1.4.29 · RP-07 1.4.45 · RP-08 1.4.14 · RP-10 1.3.51 · RP-11 1.3.40 | unchanged |

Content log after loading: `[PW-VERSION] BP-02 v1.3.214` · `[TREEGROW] BOOT v1.3.214` · `[CIV-CLOCK] village clock loaded — 38 staged building(s)` · `PW Test Runner BP v0.5.20`.

## 2. Your tests: p22 (CIVITAS, 12 steps) and p23 (TREES, 9 steps)
`/scriptevent pw:test start p22`, then `p23`. Two things found during the window are relevant to p23 step t01. Both are context for what you may see, not answers:
- **Forest density.** Forests on 1.3.214 hold about half the trees the rules ask for (question 6 b). They may read as sparse.
- **Trees in other trees' crowns.** About 1 % of trees overall, about 3 % in dense oak forest, stand on another tree's canopy (question 8). If you see one, that is this known defect: FAIL t01 with a note.
- **t04 (felling a tree whose crown a neighbour touches).** If the tree you chop carries another tree standing in its crown, that upper tree is left hanging when the lower one falls. That is question 8, not a felling fault. Note it either way.
- **t02 (grove).** The census confirms it: the grove's spruces are the engine's own, and none of our rules reach the grove (question 6 a).
- **p22, the lumberyard clearing.** The same applies there: if the town fells a tree that carries another in its crown, the upper tree can be left hanging (question 8).

## 3. What the window did (02:27 → 08:30 CT)
- **Verified the whole week.** Delivery integrity 16/16; manifests 16/16; every static gate; CIVITAS on the server on both axes; the full evolution.
- **Delivered fixes:**
  - 1.3.211: roads vs later streets; bridge decks; surfaces over hollows.
  - 1.3.212: pending saplings survive a rejoin.
  - **1.3.214: our light blocks are removed again.** 1.26 reports `light_block_<level>`, so the mob lights and the golden-crown light had never removed a light.
- **Persistence census.** Proven across restarts: the hearth ledger, the weather cache, the sapling registry, and the CIVITAS clock and snapshot. The CIVITAS site map codec round-trips 80/80.
- **Other checks:**
  - Version banners: 11/16 packs consistent. The 4 RP lags are cosmetic.
  - Support rule: holds.
  - A sweep of every block id our scripts use against the engine's own list: the light id was the only one that broke behaviour.
- **Question 6 researched to its cause (§3c of REVIEW-WEEK).** It led to the 1.3.215 candidate and to question 8.
- **Safety.** The recoverable delete; the append-only failsafe on Drive (snapshots plus every frozen build); stopping points.

## 4. Held builds (nothing below is delivered)
| Build | What | Status |
|---|---|---|
| 1.3.213 | snow fix v3 (search + snow allowlist + solid-only intersection) | **superseded** by the question 6 analysis. Its useful part is the search step, which 1.3.215 carries alone. The number is never reused |
| **1.3.215** + TestRunner **0.5.21** | 214 + a 2-block search for the 23 tree rules (a grass tuft, fern, flower or thin snow layer no longer refuses a tree). Templates untouched | **built and gated, held for question 6 b**. Census: 48 → 91 trees on identical chunks. TestRunner mock 348/348. Same crown caveat as 214 (question 8): it avoids low crowns (2 up) but not high ones. Deliverable within minutes of a yes |

## 5. Questions (1–5 as in REVIEW-WEEK §5)
1. **Engine-internal vanilla trees** (grove, mangrove, swamp, old-growth giants, savanna acacias, flower-forest oaks, fallen trunks): accept them, convert them with a scripted chunk-load sweep, or do nothing?
2. **Swamp oaks:** keep vanilla (with vines) or convert?
3. **Daughter towns** are 170–230 blocks apart; your ruling said 120–200.
4. **Forest densities** (the Java-like assumption): keep? Read this together with 6 b.
5. **The oak wall recipe** shares its 2×3 shape with the vanilla oak door: which shape should the oak wall have?
6. **Trees and snow.**
   - (a) The grove, snowy slopes and alpine peaks have no tree rule of ours: add one?
   - (b) Take 1.3.215, about twice today's forest density?
7. **Lights already in your world.** Every mob light (1.3.194 → 1.3.212) and every crown light is still there. Should I add a command that clears light blocks of levels 6, 10, 13 and 14 within a radius of you? It would also take light blocks of those levels that you placed yourself.
8. **Trees in other trees' crowns** (a defect in the delivered trees, about 1 % overall and about 3 % in dense oak forest). No fix at the rule level works: I measured and rejected a 'topmost solid block' rule, a deeper search (more crown landings, and one tree on water) and snap-to-surface (it refuses plants too). The 2-block search in 1.3.215 only helps where the crown is low (2 blocks up). Options:
   - (a) a check while you play that removes any tree standing on leaves, using its exact template cells (it removes trees from your world);
   - (b) a design job: a ground test before each tree, like vanilla trees' 'may grow on' list;
   - (c) accept.

## 6. Your eyes (the server cannot check these)
- **Golden crown at night.** Walk 20 blocks and look back: no light should stay behind.
- **Mob lights.** Watch a blaze, magma cube or glow squid in a dark place: no lit cells should stay where it was.

## 7. Files
- **Gofile folder DoHcDxGx:**
  - BP-02 1.3.214 — 5,539,702 B — `a368dcd6b02169499395e5b0ff27358f`
  - TestRunner 0.5.20 — 313,451 B — `2461c3cc8bcd2973e881393e59fb9b5a`
  - the handoffs and REVIEW-WEEK
- **Next numbers:** BP-02 1.3.215 (the held candidate) · TestRunner 0.5.21 (held).
