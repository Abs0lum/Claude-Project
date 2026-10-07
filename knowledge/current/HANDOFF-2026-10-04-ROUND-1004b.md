# HANDOFF — 2026-10-04 — ROUND 1004b: trees, falling trees, civs, flooding, manhole (D-C563 … D-C568)

Supersedes `HANDOFF-2026-10-04-CIVITAS-CITY.md` as CURRENT-STATE. Delivery route: **Google Drive › My Drive › ClaudeUploads**
(every file md5 + size verified twice by `tools/drive_ship.py`; ledger `_logs/drive_ship_ledger.json`). Personal use only (§9).

## 1. Install set (replace these five; everything else unchanged)
| Pack | Version | Replaces | What changed |
|---|---|---|---|
| BP-02 Tectonic BP | **1.3.220** | 1.3.219 | everything in §2 |
| RP-01 Tectonic RP | **1.3.122** | 1.3.121 | the falling tree on physics (§2.7), the 72 birch copies |
| RP-05 Flora RP | **1.3.59** | 1.3.58 | vanilla leaf textures (§2.9) |
| PW Civitas Markers BP | **0.2.4** | 0.2.3 | manhole lift dwell |
| PW Civitas Markers RP | **0.2.3** | 0.2.2 | manhole lift-then-slide geometry |

World setup unchanged (Villager Trade Rebalancing stays OFF — answered 17:5x). New world recommended (the leaf/tree changes
are in the templates and the engine's own trees; an old world keeps its old leaves until chunks regenerate).

## 2. What this round changed (all shipped, all AWAITING YOUR VERIFICATION — P1)
1. **Felling by template (CIVITAS woodcutters).** `fellTree` takes a structure tree by its template's exact logs + leaves (a
   rootless tree by a log BFS + leaves within 8 steps, cap 1200). The 2-block leaf radius that left floating crowns (sim: oak
   80–84 %, birch 33–38 %) is gone.
2. **Floating-foliage sweep.** Leaves / vines not connected through leaves to a log column standing on the ground are removed:
   at founding, when a building completes (a 20-block margin), and daily over the whole influence (a chunk-by-chunk runJob).
   Gate run: "day 17: 76 floating leaves cleared (2 crowns, #3 cottage_s)".
3. **Flooding.** Streets and plots are drained before they are laid (to the pieces' depth; the ring sealed as a cofferdam with
   stone bricks); a daily flood watch drains water that reaches a street's surface and seals its source. The template's own
   water (a farm's irrigation, the well's shaft) is never touched (gate #1 caught the first cut doing exactly that; fixed).
4. **Mobs cleared** from every script-built structure's box at every stage and every street piece (players, civs, leads,
   markers, items stay).
5. **CIVS.** Vanilla trade / stroll / dwelling / breeding / job groups never reach a civ (every civ opens OUR window — no
   emerald menu); states STAND / IDLE / WALK / HOME (tags `civ:state:*`, events `pw:civ_*`); children never get a profession
   (the vanilla job claims are stripped); chimney flues are in the pathfinder's `blocks_to_avoid` (53 `pw:flue_*`); **civs walk
   at half speed** (movement 0.25; your 19:35) — the night watch gets a `pw:civ_brisk` group (0.5) only while on duty.
   Tunable in-game: `/scriptevent pw:clock pace 20|25|35|50` (25 = half, the default; 50 = the old vanilla pace) — applies to
   every civ at once and to new ones.
6. **Lectern** in the town hall faces the speaker's side (east in the r1 frame; 4 templates + their stages + the dir table).
7. **Falling trees on physics (R6).** The resting angle comes from the tree's OWN cells (logs above the cut + its leaves,
   leaves may crush 0.6 into the ground) rotated about the stump top's LEADING EDGE against the real ground (top faces;
   grass_block is ground — the old reader skipped it and read the block's y, two blocks low). Timing T = 1.10·√H from 2° to
   90° after a 0.15 s hold + 0.45 s creak ramp; the curve is Molang in RP-01 (`2 + 88·f^3.85`, continued past 90° downhill),
   identical to the script's curve to 1e-13; the impact cue, leaf bursts, trail, impact effects, sweep end and cleanup all sit
   on the impact frame; the rebound goes UP (+2.3°; the old rest key went 4° deeper into the ground). Every falling-tree
   geometry (28 legacy + 544 copies) hinges on the trunk's leading face. **The fall DIRECTION sign (July's open Phase-6) is
   closed by law (D-C565):** the trunk tips toward the entity's right = world (−cos yaw, −sin yaw); the old (−cos, +sin) was a
   reflection — south/north picks rendered opposite, diagonals a quarter turn off. The `[FELL]` line now prints the compass
   word (`dir yaw=90 N rest=-96 T=3.48s imp=4.06s`). The flat-ground rule (your F7: heavy side, else away from the chopper)
   now actually runs (R-54: the slope mode always won before).
8. **Birch templates v2** (your 15:27). Continuous egg crowns on slim trunks (54 / 323 / 389 leaves per age, was 26 / 157 /
   138; width ≤ 0.5 H; clump birches kept; 0 floating leaves). Sheet: `BIRCH-V2-SHEET-2026-10-04.png` — your eyes decide.
9. **Vanilla leaf textures (RP-05 1.3.59, R-52).** Every vanilla leaf key mirrors vanilla's own [cutout, opaque] pairs on our
   pw_leaves2 art (Patrix 26.2 256x; opaque 128). The engine's own swamp oaks / mangroves / grove spruces now wear our leaf;
   no 32-px strips, no black cubes at distance. Atlas +0.8 Mpx (if leaf faces go missing / magenta on the phone: say so — the
   fallback is 128 / 64).
10. **Vines:** the touch shake is off; the wind sway stays (your 17:38). Q10 retired.
11. **Manhole cover** (your 19:06): closed stays flush; on opening the plate lifts 1 px, dwells 4 ticks, then slides over the
    street at that height; closing slides back, dwells, drops.
12. Two latent lint errors in main.js fixed (`_slabQualify` used an undefined `dim` → a ReferenceError on the bridged-riser
    path of the slab scanner; a duplicate stats key).

## 3. Verification done here (static + server; nothing replaces your eyes)
- Unit: `pw_fall_physics` 43/43; the Molang fall curve == the JS curve (max 8.5e-14); ESLint clean on every touched script
  (main.js now 0 errors, was 2 pre-existing); every JSON parses; template index BP ↔ RP parity 544/544.
- Leaf verification (your 19:36): 544 templates = 229,918 leaf cells, 100 % `pw:*_leaves`, 0 vanilla, 0 missing baked states;
  RP-01 1.3.122: the 11 leaf blocks' 100 texture keys → 100 square 256-px images + 100 texture sets with 256 normal + MERS
  layers; art = Patrix 26.2 256x (build_leaf_v3). One nit: 0.7 % of trunk-touching leaves in the rescaled / square groups wear
  a far-look variant (R-55, Q35).
- BDS load gate (BP-02 220 + Markers BP 0.2.4 + the three RPs' manifests): 0 ERROR, all modules up.
- BDS village gate (probe kitvillage-0.0.29 on BP-02 220 + Markers BP 0.2.4): run 2 (after the drain-order fix) DONE, 0 ERROR: village → city, 36 plots / 33 finished / 32 verified (the one 'bad' is the probe's stale lectern manifest — it expects the old direction), 188 floating leaves swept, farm irrigation + well shafts intact, manholes 11/11, watch 7 on duty 3/3 kills (brisk), the woodcutter's lumberyard booked 7 units in the real-time window, market stocked 'ok' (3 counters), 0 script errors over 37 min. Walks: 46 arrived / 20 stuck by the bench stage against 219's 221 / 13 on the same site — the half pace halves what the civs get done per clock; `/scriptevent pw:clock pace 50` restores the old pace in-game (35 is the middle). Run 1 (before the fix) found the drained farm/wells; nothing else differed.

## 4. Your tests, in order (copy the lines you need)
1. **A fell on flat grass** (Survival, an axe, one of OUR oaks): read the `[FELL]` line — the compass word must match where the
   trunk lies and where the logs drop; the trunk must rest ON the ground (no clipping), bounce up once, and the sound land on
   the hit. Then one downhill, one against a bank.
2. **A birch forest look** (new world): complete crowns? Compare with the sheet.
3. **A swamp / mangrove / grove**: the engine's trees now wear our leaf (no 32-px blobs, no black cubes at distance).
4. **A village**: civs stroll at half speed; tap any civ → our window (never the emerald menu); no child with a trade; nobody
   walks through a chimney; the lectern faces the benches; the manhole lifts then slides; no floating crowns after the
   woodcutter fells; a settlement founded beside a pond keeps dry streets.
5. The content log after each (`[FELL]`, `[FALL] rest …`, `[CIV-CLOCK]` flood / sweep lines).

## 5. Open questions (copy-paste blocks in `QUESTIONS-AND-ASSUMPTIONS-2026-10-04.md`): Q32 manhole lift = 1 px? · Q33 the
ramp "4 horizontal per 1 vertical" (one collision box per block is an engine limit — what did you mean?) · Q34 the well over
the water (screenshot) · Q35 R-55 re-bake · Q19/Q20 the engine's own tree biomes · Q1–Q31 as before.

## 6. Docket (next rounds, your 17:59)
Palace program (life-size, secret doors / passages) · economy forward · the sophisticated purpose-driven civ logic (R7 P0–P4:
needs / utility, station records, pair conversations, stuck ladder — this round laid the state foundation) · R-51 bench→town
arrival step · manor glass · PS5 frame rate.

## 7. Delivery (Drive › ClaudeUploads; md5 = the ledger's, verified twice)
| File | Bytes | md5 |
|---|---|---|
| BP-02-AbsolutRealism-Tectonic-BP-v1_3_220.mcpack | 5,600,125 | 1875d6c3312ffc16acb6da6d7b0cc547 |
| RP-01-AbsolutRealism-Tectonic-RP-v1_3_122.mcpack | 138,510,638 | 4047224bea332496fb7542c387c49bb0 |
| RP-05-AbsolutRealism-Flora-RP-v1_3_59.mcpack | 47,003,345 | 0ee72980d6c70a87bd27e94375da90ad |
| PW-Civitas-Markers-BP-v0_2_4.mcpack | 47,401 | 312e927215a3c5a3c97e14203339be92 |
| PW-Civitas-Markers-RP-v0_2_3.mcpack | 106,297 | d6f28cd01950bfcd990cbb95ad94ed7e |
| ClaudeUploads/Sheets/BIRCH-V2-SHEET-2026-10-04.png | 217,044 | 9f012e1786481b52145006c9e6180103 |

## 8. Files
`tools/build_bp02_220.py` (stages 0–8, reproducible) · `tools/build_rp01_122.py` · `tools/build_rp05_59.py` ·
`tools/build_markers_024.py` · `tools/package_round_1004b.py` · `tools/bp02_src/pw_fall_physics.js` + `test_fall_physics.mjs` ·
`tools/ft_tpl_gen_lite.py` (pivot law) · `tools/tree_gen.py` (birch v2) · research `R6-FALLING-TREE-PHYSICS-AND-ANIMATION-2026-10-04.md`,
`R7-ADVANCED-VILLAGER-AI-2026-10-04.md` · `RESULTS-AND-IDEAS-2026-10-04.md` R-52…R-56 · journal D-C563…D-C568.
