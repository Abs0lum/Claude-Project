# PROPOSALS for your rulings — question 7 (stray lights) and question 8 (trees in crowns)

Plan-first (Execution Law): nothing below is built. Each part says what it would do, how it works, the risks, the gates, the effort and the decision needed. Written during the review window's quiet hold, 2026-10-03.

## Q7 — clearing the light blocks our mobs and the golden crown left behind (D-C515)
**The situation.** BP-02 1.3.194 – 1.3.212 never removed a light block. So every blaze, magma cube and glow squid near you, and every step taken wearing the golden crown, may have left an invisible light block:
| Source | Level |
|---|---|
| blaze | 13 |
| magma cube | 10 |
| glow squid | 6 (waterlogged) |
| golden crown | 14 |

1.3.214 stops new ones. The old ones have no record left to find them by.

**The proposal.** A command you run when you want it: `/scriptevent pw:moblight sweep <radius>`, radius at most 64. Around you it:
- finds every block with id `minecraft:light_block_6`, `_10`, `_13` or `_14`;
- replaces each with air, or with a water source if the light was waterlogged;
- reports the count by level in chat.

It never runs by itself. `pw:moblight sweep <radius> dry` only counts.

**Risk.** A light block **you** placed at one of those four levels inside the radius would also go. The dry run shows the counts first.

**Gates:**
- a server test: lights of all 16 levels placed, the sweep removes exactly the 4 levels, and waterlogged ones turn back to water;
- the mob-light mock;
- load gates.

**Effort:** S (one scriptevent handler, about 40 lines).
**Decision needed:** yes or no; the radius limit; whether level 14 is included (the crown).

## Q8 — trees standing in another tree's crown (D-C520 / D-C521)
**The situation.** About 1 % of our worldgen trees (about 3 % in dense oak forest) stand on another tree's leaves, sometimes several blocks up with air below. The cause is the tree rule's heightmap: it is the top of an existing canopy, and `grounded` accepts leaves as ground. These did not work, so no fix at the rule level exists:
- a "topmost solid block" rule;
- a 12-block search;
- snap-to-surface.

**Option A — a check while you play (recommended if you want them gone).** When a chunk loads, the existing leaf-variant scanner already walks our trees. A small addition would:
- treat any `pw:*_root` with leaves, not ground, directly below it as a crown tree;
- rebuild its exact template from the root's own states (`pw:tpl` / `pw:tpl_hi` + facing → `templateCells` + `turnOffset`, the same code the T4 exact felling set uses);
- remove its logs and leaves;
- leave alone any cell that also belongs to the supporting tree's template (found the same way from that tree's root), so the lower crown keeps its leaves.

It runs once per tree, and a dynamic-property mark per chunk prevents repeats.

Risks:
- It removes trees that are in your world now, only the ones in crowns.
- A tree that you placed yourself on leaves (structure / creative) would also go, so only roots with worldgen template states qualify, and the mark makes it run once.

Gates:
- the rootcheck census before/after: 0 roots on leaves;
- the lower trees' leaf counts unchanged except the overlap;
- the two-run persistence of the per-chunk mark;
- load gates;
- your eyes in a dense oak forest.

Effort: M.

**Option B — a ground test before each tree (prevention).** Each template would be placed only where the cell under its root is a ground block, the way vanilla trees use "may grow on". With structure templates this needs a sequence feature: a one-block test at the root position, then the template. That means re-anchoring every template so the root sits at the placement point (`rotate_around_center`). Effort: M–L. It prevents new crown trees only, so existing chunks keep theirs.

**Option C — accept.** About 1 %; you may meet some in dense oak forest.

**Decision needed:** A, B, both, or C.

## Related: question 6 (b) — the held 1.3.215
1.3.215 is fully gated and only waits for your yes:
- tree census: 48 → 91;
- the floating gate shows the same crown caveat as 1.3.214;
- sapling restart test: pass;
- full stack: 0 errors;
- mock: 348/348.

It does not fix Q8, but the 2-block search does avoid low crowns (2 blocks up). Q8 option A would clean up whatever remains.
