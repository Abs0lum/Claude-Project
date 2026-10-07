# HANDOFF — 2026-10-03 — REVIEW WINDOW: BP-02 1.3.211 → 1.3.212 + TestRunner 0.5.18 → 0.5.19

The two handoffs of his 6-hour review window (02:27 → ), merged for the project. The authoritative CURRENT-STATE is this file until the next handoff; `REVIEW-WEEK-2026-10-03.md` holds the full result table.

## Install (replaces every earlier number)
| Pack | Version | Replaces |
|---|---|---|
| **BP-02 Tectonic BP** | **1.3.212** | 1.3.207 … 1.3.211 |
| **PW-TestRunner BP** | **0.5.19** | 0.5.15 … 0.5.18 (p22 / p23 setup texts name 1.3.212) |
| RP-01 1.3.118 · RP-07 1.4.45 · RP-08 1.4.14 · the rest | unchanged | |

Content log: `[PW-VERSION] BP-02 v1.3.212`, `[TREEGROW] BOOT v1.3.212`, `[CIV-CLOCK] village clock loaded — 38 staged building(s)`, `PW Test Runner BP v0.5.19`. **Your tests: p22 (CIVITAS) and p23 (TREES).**

## 1.3.211 (D-C508 / D-C509) — found by the full CIVITAS evolution with the new body-vs-profile gate
1. **Roads laid from a stale map.** The road survey is a job over many ticks, retried for days; it remembered the streets that existed when it *started*. Streets opened and plots staked meanwhile were not protected. Now the road is laid against the streets and plots that exist when it *finishes*; a way that now runs through a plot is abandoned and searched again.
2. **A bridge deck re-laid as a road; surfaces over hollows.** Where a jog's cross overlapped a run's body on a bridge, the second lay saw the fresh planks as "ground", turned the deck plank into a path over the gully, the hardening made it gravel, and gravel falls. A path over a cave roof fell the same way. Now a cell that already carries this street's surface at the right height is left alone, and every normal street / yard surface is supported from below (air / water filled to solid, max 6). Evidence: a per-cell lay log of every write to the cells.
Proof: evolution on 211 — floating 0 / bigStep 0 / stoopBad 0 at every step; 92 plots / 84 finished / 72 verified; body gate 2234/2237, 0 bad; kept-world inspection: planks back on both bridge cells, the hollow filled.

## 1.3.212 (D-C511) — found by the two-run persistence probe I had listed as "not server-proven"
The compact sapling registry of 1.3.210 / 211 saved every pending sapling's type as −1 (`Object.keys` on a `Map` is empty), so **pending saplings were lost on every rejoin** in 210 / 211 (1.3.209 was fine). Fixed: the table is the Map's keys. Proof: restart → "6 pending sapling(s) restored". Along the way proven: world dynamic properties persist across a BDS restart and are **keyed per pack UUID**; the **CIVITAS clock state persists** (a founded village came back after a restart).

## Standing gates added
The body-vs-profile gate inside the evolution probe · the two-run persistence probe before every BP-02 packaging · `bds_load.install` refuses to run while a server is up.

## Held questions (5) — see REVIEW-WEEK-2026-10-03.md §5
Engine-internal vanilla trees (accept / scripted sweep / nothing) · swamp oaks · daughters distance · forest densities · the oak plank-wall recipe shape (it shares the vanilla oak door's 2×3).
