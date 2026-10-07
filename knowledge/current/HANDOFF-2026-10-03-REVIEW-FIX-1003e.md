# HANDOFF — 2026-10-03 — REVIEW-WINDOW FIX: BP-02 1.3.211 + TestRunner 0.5.18

SUPPLEMENT to `HANDOFF-2026-10-03-V6-FIX-1003d.md` (authoritative for everything not listed here). Journal: D-C508, D-C509 (+ D-C507 safety). Found and fixed INSIDE his 6-hour review window by the full CIVITAS evolution run with the new body gate.

## Install (replaces the earlier numbers)
| Pack | Version | Replaces |
|---|---|---|
| **BP-02 Tectonic BP** | **1.3.211** | 1.3.207 / 208 / 209 / 210 |
| **PW-TestRunner BP** | **0.5.18** | 0.5.17 (p22 / p23 setup texts name 1.3.211) |
| RP-01 1.3.118 · RP-07 1.4.45 · RP-08 1.4.14 · the rest | unchanged | |

Content log after load: `[PW-VERSION] BP-02 v1.3.211`, `[TREEGROW] BOOT v1.3.211`, `[CIV-CLOCK] village clock loaded — 38 staged building(s)`, `PW Test Runner BP v0.5.18`. **Your tests: p22 (CIVITAS) and p23 (TREES).**

## What 1.3.211 fixes (both server-proven, both found by the body gate)
1. **Roads laid from a stale map (D-C508).** The road survey is a job over many ticks, retried for days; it remembered the streets that existed when it *started*. Streets opened and plots staked meanwhile were not protected: a road cut through a later street. Now the road is laid against the streets and plots that exist when it *finishes*; a way that now runs through a plot is abandoned and searched again.
2. **A bridge deck re-laid as a road; surfaces over hollows (D-C509).** Where a jog's cross overlapped a run's body on a bridge, the second lay saw the fresh planks as "ground", turned the deck plank into a path hanging over the gully, the hardening made it gravel, and gravel falls — two holes in the deck. Elsewhere a path laid over a cave roof fell the same way. Now a cell that already carries this street's surface at the right height is left alone, and every normal street / yard surface is given support beneath (air or water under it filled down to solid, max 6).

## Proof
- Full evolution on 211 (evoprobe-0.0.19 + markers; civtest-20261003-030811): floating 0 / bigStep 0 / stoopBad 0 at every step; 92 plots / 84 finished / 72 verified; 3 settlements, roads, trade; **body gate 2234/2237, 0 bad** (3 benign near-misses where two keys' shapes overlap at a 1-step); 0 script errors. On 210 the same run gave 2228/2237 with the two defects.
- Kept-world inspection after the run: both bridge cells `spruce_planks@70` with the bridge air beneath; the granddaughter's cell `gravel@90` on dirt 88–89 (the hollow filled).
- Mechanism: a per-cell lay log (`bp02-211-laylog`, job-only) recorded every write to the cells in order — the evidence for D-C509 is in the journal.
- Lay unit test 169/169 · road test 9/9 · TestRunner mock 348/348 · load gate 211 + 0.5.18 together 0 ERROR; banners 1.3.211 / 0.5.18.
- NOT server-proven: nothing new beyond 1003d's list (an x-axis town WAS proven this window: 712/712).

## Known, by design
Where a jog corridor runs along the square's edge its cross reaches into the square's border row; the square's levelling wins (a 1-block kerb). Two keys' shapes overlapping at a 1-block step take the last writer's height (≤ 1 step, counted as near-misses).
