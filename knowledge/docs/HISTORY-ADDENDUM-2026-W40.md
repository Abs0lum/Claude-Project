# HISTORY ADDENDUM — week 40 (2026-09-27 → 2026-10-03): the version chronicle, from the delivery ledger

Append point for HISTORY-v4 (post-07-07 handoffs). Every line below is read from `_logs/delivery_ledger.md` (md5-verified deliveries) and the handoffs of the week in the project; the per-round detail lives in those handoffs, not here. Personal use only (§9) throughout.

## 1. Versions delivered this week (first → last; number of distinct builds delivered)
| Pack | First this week | Last (= current) | Builds |
|---|---|---|---|
| BP-02 Tectonic BP | 1.3.187 (09-27) | **1.3.214** (10-03 06:13; 1.3.213 held, never delivered) | 25 |
| PW-TestRunner BP | 0.1.0 (09-27) | **0.5.20** (10-03 06:13) | 41 |
| PW-TestRunner RP | 0.2.0 (09-27) | 0.7.1 (10-01) | 9 |
| RP-01 Tectonic RP | 1.3.106 (09-30) | **1.3.118** (10-03 01:20) | 13 |
| RP-02 Atmospheric Effects | 2.0.5 (09-27) | 2.0.7 (10-02) | 3 |
| RP-03 PBR | 1.3.61 (10-01) | 1.3.67 (10-02) | 7 |
| RP-04 Basic | 1.3.139 (09-27) | 1.3.156 (10-02) | 16 |
| RP-05 Flora | 1.3.50 (09-27) | 1.3.58 (10-02) | 8 |
| RP-06 Hostile Mobs | 1.4.7 (09-27) | 1.4.29 (10-02) | 22 |
| RP-07 Neutral Mobs | 1.4.11 (09-27) | **1.4.45** (10-03 00:44) | 32 |
| RP-08 Items | 1.4.7 (09-27) | **1.4.14** (10-03 00:44) | 8 |
| RP-10 Terrain | 1.3.41 (09-27) | 1.3.51 (10-02) | 9 |
| RP-11 Ores | 1.3.36 (10-01) | 1.3.40 (10-02) | 5 |
| PW-Civitas-Markers BP / RP | 0.2.1 / 0.2.2 | 0.2.1 / 0.2.2 | 1 / 1 |
| PW-StripMine BP | 1.3.2 (09-27) | 1.3.13 (10-02; dissolved into the main packs afterwards) | 12 |
| test packs (GrassTint T1–T4, SandTest A/B/G1/G2, LightTest) | 10-01 / 10-02 | one-shot witness packs | — |

**The install set as of 10-03 06:13:** BP-01 1.3.35 · BP-02 1.3.214 · BP-03 1.3.34 · Markers BP 0.2.1 / RP 0.2.2 · TestRunner BP 0.5.20 · RP-01 1.3.118 · RP-02 2.0.7 · RP-03 1.3.67 · RP-04 1.3.156 · RP-05 1.3.58 · RP-06 1.4.29 · RP-07 1.4.45 · RP-08 1.4.14 · RP-10 1.3.51 · RP-11 1.3.40.

## 2. The week's arcs (pointers to the handoffs)
- **Mobs (RP-06 / RP-07 / RP-08, 22 + 32 + 8 builds):** the JEM→Bedrock conversion rounds, size law, textures / MERS, animation ports; the recheck-week fixes A1–A3 (cave spider pin, texture-key ownership, dangling animation names) landed in 1.4.45 / 1.4.14 (10-03). Handoffs: the mob rounds of 09-27 → 10-02, `RECHECK-WEEK-2026-10-02.md`.
- **Ores / terrain / PBR (RP-11, RP-10, RP-03, RP-04):** the ore rounds (RP-11 1.3.36 → 1.3.40), the strips and size rounds, the StripMine dissolve into the main packs (10-02). Handoff: `HANDOFF-2026-10-02-ROUND-1002n-DELIVERED.md`.
- **TestRunner (0.1.0 → 0.5.20, 41 builds):** the in-game witness-round runner — lineups p0 … p23; p22 CIVITAS (10-03) and p23 TREES (10-03) are the two awaiting his witness.
- **CIVITAS (BP-02 1.3.203 → 1.3.212):** the village clock from the pilot cottage (10-02) through V5 economy and **V6 "the living town on the land"** (1.3.207, 10-03 00:44) to the review-window fixes (1.3.210 GS-1 run-start body; 1.3.211 roads vs later streets + bridge decks + surfaces over hollows). Handoffs: `HANDOFF-2026-10-03-V6-CIVITAS.md`, `-V6-FIX-1003d.md`, `-REVIEW-WINDOW-1003e-f.md`.
- **TREES (BP-02 1.3.208 / 209 / 212, RP-01 1.3.118):** T2 roots for the square species + the 17 legacy tree-rule overrides + grounded templates; T4 the exact template falling set; T5 saplings grow our templates; the registry-reload regression fixed in 1.3.212. Handoffs: `HANDOFF-2026-10-03-TREES-ADDENDA.md`, `-TREEGROW-RELOAD-1003f.md`.
- **Light-block fix (BP-02 1.3.214, 10-03 06:13):** the review window's restart census proved that our mob lights (1.3.194) and the golden-crown light never removed a light block (1.26 reports `light_block_<level>`); fixed, proven by a two-run restart test. Handoff: `HANDOFF-2026-10-03-LIGHTFIX-1003g.md`.
- **Recheck week (10-02) and Review week 2 (10-03):** `RECHECK-WEEK-2026-10-02.md`, `REVIEW-WEEK-2026-10-03.md`.
- **Safety (10-03):** the recoverable-delete guard, the append-only failsafe, the Drive archive of the sandbox — `SANDBOX-SAFETY-PROTOCOL.md`.

## 3. Open at the end of the week
- **His witness rounds.** p22 (CIVITAS) and p23 (TREES), on BP-02 1.3.214 + TestRunner 0.5.20.
- **8 held questions** (REVIEW-WEEK §5 and HANDOFF-2026-10-03-REVIEW-WINDOW-CLOSE §5). Among them:
  - Q6, reframed: (a) tree rules for the grove, snowy slopes and peaks; (b) the forest-density fix.
  - Q7: clearing the stray lights left by 1.3.194 – 1.3.212.
  - Q8: trees standing in other trees' crowns, a defect in the delivered trees.
- **Held builds:**
  - 1.3.215 + TestRunner 0.5.21: 214 + the 2-block tree search, which roughly doubles forest density. Held for Q6(b).
  - 1.3.213: superseded; its number is never reused.
- **His eyes:** the golden-crown light check.
- The standing backlog in `STATUS-BOARD.md` §D.
