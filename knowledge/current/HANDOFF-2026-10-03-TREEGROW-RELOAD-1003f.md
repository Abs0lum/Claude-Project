# HANDOFF — 2026-10-03 — TREEGROW RELOAD FIX: BP-02 1.3.212 + TestRunner 0.5.19

SUPPLEMENT to `HANDOFF-2026-10-03-REVIEW-FIX-1003e.md` (authoritative for everything not listed here). Journal D-C511.

## Install (replaces the earlier numbers)
| Pack | Version | Replaces |
|---|---|---|
| **BP-02 Tectonic BP** | **1.3.212** | 1.3.207 … 1.3.211 |
| **PW-TestRunner BP** | **0.5.19** | 0.5.18 (p22 / p23 setup texts name 1.3.212) |
| RP-01 1.3.118 · RP-07 1.4.45 · RP-08 1.4.14 · the rest | unchanged | |

Content log: `[PW-VERSION] BP-02 v1.3.212`, `[TREEGROW] BOOT v1.3.212`, `PW Test Runner BP v0.5.19`. **Your tests: p22 (CIVITAS) and p23 (TREES).**

## The defect (mine, shipped in 1.3.210 and 1.3.211)
The compact sapling registry (1.3.210) stored each pending sapling's type as an index into `Object.keys(PW_GROW_POOLS)` — but `PW_GROW_POOLS` is a `Map`, so that table was empty: every type was saved as **−1** and the loader skipped every entry. **Pending saplings were lost on every rejoin** in 210 / 211 (1.3.209's long form was fine). Found by the two-run persistence probe I had listed as "not server-proven" in the 1003d handoff.

## Proof
- Two-run probe (growpersist A → B, kept world): 211: 6 pending at stop → **0 restored**; **212: "6 pending sapling(s) restored", pending 6** (they then wait for room: `deniedSpace` is the neighbouring canopies, as designed).
- Along the way, two laws proven in the server: world dynamic properties persist across a BDS restart **and are keyed per pack UUID** (a probe with another UUID sees none of them); the **CIVITAS clock state persists** (a founded village came back after a restart with its 6,137-byte state).
- Load gate 212 + 0.5.19 together 0 ERROR; TestRunner mock 348/348; the clock / land / economy scripts byte-identical to 211's (the review-window fixes carry over).

## Standing gate from now on
Every BP-02 build runs `growpersist-A` → stop → `persist-B` (kept world) before packaging: the "restored" line is the pass.
