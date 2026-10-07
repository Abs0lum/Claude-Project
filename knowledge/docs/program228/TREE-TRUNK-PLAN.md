# TREE TRUNK TIP — plan (program 228, cosmetic, low priority)

**Ask (Abs0lum, relayed):** do for ALL our custom trees what birch v3 did — "make sure the trunk isn't sticking out too high and
that it's not noticeable at the top of the tree".
**Status:** PROPOSAL ONLY. Nothing in `tools/`, `_build/`, `_bds/` or Drive was changed. The change was built and measured in a
scratch copy of the generators (since deleted); the diffs below are exact and were re-verified byte-for-byte (544/544) against
that scratch run. Static measurement only — rules things out, not in (P1); in-game look is his call.
**Date:** 2026-10-06. Baseline: BP-02 1.3.227 `structures/pw/trees/` (544 templates), RP-01 1.3.124.

## 1. What I measured, and how sure it is

* **The shipped templates come straight from the generators.** All 544 shipped templates are reproduced exactly (cells and
  block states) by the current generators: birch = `tree_gen.build()` (written by build 224); the other 472 =
  `tree_gen.build()` / `tree_gen_square.build()` → `tree_rescale.rescale()` (build 218). So a generator change plus the same
  pipeline regenerates exactly what ships, and nothing else moves.
* **Per template**, from the .mcstructure (read only, `tools/mcstructure.py`):
  * *trunk* = the root cell's footprint (2×2 for the elders), followed upward through wood within one column of it (this
    follows leans; on the elders it also picks up the first cell of a limb or stag limb that leaves the stem there);
  * *crown top* = the highest leaf; *crown base* = the lowest layer with ≥ 4 leaves (the same CBH as tree_rescale);
  * **gap** = crown top − trunk tip; **abv** = trunk logs above the crown top;
  * **seen** = trunk logs in the TOP 4 LAYERS (y ≥ crown top − 3) that can be seen from outside — either from the sky
    (nothing over them in their column) or along any of the 4 horizontal axes (no block between them and the bounding box).
    Leaves count as opaque. This is the "noticeable at the top of the tree" test;
  * **cov** = blocks stacked over the tip in its own column (≥ 2 = a leaf layer and more over the tip).
* **What makes me confident about the after-state:** every after-template was checked against its before-template:
  root cell (block, tpl, tpl_hi, rotation) and its position unchanged; x/z size unchanged; **every crown leaf of the before-
  template is still a leaf** (0 lost in 544); every new leaf sits on a former log; no wood added; mangrove roots and every
  other block unchanged; all remaining wood 26-connected to the root. 275 templates come out **byte-identical**.

## 2. The birch v3 rule, and how it generalises

Birch v3 (`BIRCH_TRUNK_INTO_CROWN = 1`): the trunk stops at **crown base + 1**; the column above it becomes **birch leaves**
(a leafy core); the crown is unchanged because nothing about the RNG changes. That is safe for birch because its crown is a
closed egg wrapped round the whole stem.

Applied literally (crown base + 1) to every species it would turn most of a spruce or a jungle emergent into a leaf pole
(their crown base is 0–2 / 15–19 with a visible stem between the tiers) and take most of the wood out of every tree. So the
proposal anchors the same idea at the **top** instead:

> **v4 rule (`sink_tip`):** apex = the highest leaf over the trunk's top cells (their column and the 8 around it), never
> above the crown's own top. **cut = max(crown base + 1, apex − TRUNK_TIP_DEPTH)** — birch v3's crown-base + 1 is kept as the
> floor. Trunk cells above the cut leave the trunk: **at or under the apex they become leaves of that species** (as birch
> v3), **above the apex they are removed** (no bare leader / stag head standing over the crown). It runs after the crown is
> built and draws no random numbers, so the RNG sequence — and every crown — is unchanged.

The depth is a constant per species × tier, chosen as the **smallest depth that gives 0 trunk logs above the crown and
0 seen in the top 4 layers** over all that group's templates (measured after the rescale, i.e. on what would ship). The depth
sweep (1–6) is summarised in §4.

## 3. Per-species proposal

| species / tier | depth | anchor | what the cut logs become | notes |
|---|---|---|---|---|
| oak young | 4 | stem | oak leaves | ovoid like young birch; tip was 1–2 under a ragged top (seen in 2) |
| oak mature | 5 | stem | oak leaves | tip under the cap dome; 3 seen through the dome's shell gaps |
| oak old | 5 | stem | oak leaves inside; **stag head removed** | the dead leader stood 1–3 above the crown in 19/24 (research §2.6 "stag head") |
| oak elder (2×2) | 5 | stem | oak leaves inside; leader over the crown removed | **its 1–2 stag limbs are not drawn** (`STAG_OVER_CROWN = False`; the RNG draws stay) |
| birch young/mature/old | — | — | — | **unchanged** (v3 already; 72/72 byte-identical) |
| spruce young / mature / old | 3 / 4 / 4 | stem | spruce leaves = a longer leaf spire | conifer leader: the top 2–3 logs become the spire; the double-leader fork (idx 7, 19) becomes leaves too |
| spruce elder (2×2→1) | 4 | stem | spruce leaves (spire) | tip was 2 under the spire with the stem seen between the top tiers in 32/32 |
| jungle young | 4 | stem | jungle leaves | only the 12 POLE forms change; the 12 cacao forms are unchanged (the floor stops it: their 3-block stem is the jorquette under the fans) |
| jungle mature / old | 3 | stem | — | no-op (tip already ≥ 4 under the dome, nothing seen); byte-identical |
| jungle elder (2×2) | 3 | stem | — | no-op; byte-identical |
| dark oak elder (2×2) | 3 | stem | — | no-op (the stem splits at 2–4 into leaders deep in the dome); byte-identical |
| pale oak elder (2×2) | 3 | **crown** | pale oak leaves (a 2×2 plug flush with the crown top) | open-centred crown with 20–40 % holes: nothing grows over the stem, so it is anchored at the crown's own top. The bare top (2–6 above the leaves) and **the 2–4 stag limbs go**; the stem ends under a 1–4-leaf plug — see decision 2 |
| acacia (1-wide vanilla log) | 3 | stem | — | no-op (the stem is the 2–4 block fork, deep under the plates); byte-identical |
| cherry (1-wide) | 3 | stem | — | no-op (the 2-block stem under the scaffolds); byte-identical |
| mangrove (1-wide) | 3 | stem | mangrove leaves inside; above the crown removed | 18/32 change; the log stood 1–3 above the crown in 8 |

## 4. Measurements (all 544, after = what would ship)

`B → A` = before (shipped 1.3.227) → after. Counts are "templates (logs)". Depth sweep, in brief: depth 1 already removes every
log above a crown (stag heads); the extra depth is what it takes to hide the tip from the sides in the top 4 layers
(oak young needs 4, oak mature/old 5, spruce 3–4, pole jungles 4). Deeper than needed only removes more wood.

| group | n | changed | trunk tip avg | crown top avg | crown base avg | gap min | logs above crown | trunk seen in top 4 layers | tips with cov < 2 | logs removed | logs → leaves |
|---|---|---|---|---|---|---|---|---|---|---|---|
| oak_young | 24 | 23 | 6.1 → 4.9 | 8.0 | 3.1 | 1 → 2 | 0 (0) → 0 (0) | 2 (2) → 0 (0) | 7 → 0 | 30 (1.2/tree of 7) | 30 |
| oak_mature | 24 | 24 | 10.2 → 8.2 | 14.0 | 4.1 | 2 → 4 | 0 (0) → 0 (0) | 3 (3) → 0 (0) | 6 → 0 | 47 (2.0/tree of 11) | 44 |
| oak_old | 24 | 24 | 15.0 → 7.8 | 13.4 | 4.8 | -3 → 4 | 19 (38) → 0 (0) | 24 (69) → 0 (0) | 24 → 0 | 174 (7.2/tree of 16) | 116 |
| oak_elder | 32 | 32 | 19.3 → 13.7 | 18.3 | 5.5 | -2 → 4 | 26 (49) → 0 (0) | 31 (89) → 0 (0) | 32 → 0 | 385 (12.0/tree of 78) | 200 |
| birch_young | 24 | 0 | 3.0 → 3.0 | 8.5 | 2.4 | 4 → 4 | 0 (0) → 0 (0) | 0 (0) → 0 (0) | 0 → 0 | 0 (0.0/tree of 4) | 0 |
| birch_mature | 24 | 0 | 6.7 → 6.7 | 17.8 | 5.5 | 8 → 8 | 0 (0) → 0 (0) | 0 (0) → 0 (0) | 0 → 0 | 0 (0.0/tree of 10) | 0 |
| birch_old | 24 | 0 | 7.5 → 7.5 | 18.6 | 6.2 | 6 → 6 | 0 (0) → 0 (0) | 0 (0) → 0 (0) | 0 → 0 | 0 (0.0/tree of 12) | 0 |
| spruce_young | 24 | 24 | 6.8 → 5.2 | 8.2 | 1.0 | 1 → 3 | 0 (0) → 0 (0) | 2 (4) → 0 (0) | 13 → 0 | 41 (1.7/tree of 8) | 41 |
| spruce_mature | 24 | 24 | 20.5 → 18.1 | 22.1 | 3.0 | 1 → 4 | 0 (0) → 0 (0) | 5 (9) → 0 (0) | 11 → 0 | 62 (2.6/tree of 22) | 62 |
| spruce_old | 24 | 24 | 25.3 → 22.7 | 26.7 | 1.0 | 1 → 4 | 0 (0) → 0 (0) | 2 (4) → 0 (0) | 17 → 0 | 68 (2.8/tree of 26) | 68 |
| spruce_elder | 32 | 32 | 28.8 → 26.8 | 30.8 | 1.0 | 2 → 4 | 0 (0) → 0 (0) | 32 (64) → 0 (0) | 0 → 0 | 64 (2.0/tree of 222) | 64 |
| jungle_young | 24 | 12 | 8.2 → 7.2 | 10.3 | 5.0 | 2 → 2 | 0 (0) → 0 (0) | 22 (36) → 11 (20) | 5 → 5 | 24 (1.0/tree of 9) | 24 |
| jungle_mature | 24 | 0 | 15.2 → 15.2 | 21.2 | 15.0 | 4 → 4 | 0 (0) → 0 (0) | 0 (0) → 0 (0) | 0 → 0 | 0 (0.0/tree of 16) | 0 |
| jungle_old | 24 | 0 | 16.8 → 16.8 | 22.8 | 16.0 | 4 → 4 | 0 (0) → 0 (0) | 0 (0) → 0 (0) | 1 → 1 | 0 (0.0/tree of 18) | 0 |
| jungle_elder | 32 | 0 | 20.1 → 20.1 | 25.0 | 19.0 | 3 → 3 | 0 (0) → 0 (0) | 0 (0) → 0 (0) | 6 → 6 | 0 (0.0/tree of 146) | 0 |
| dark_oak_elder | 32 | 0 | 7.2 → 7.2 | 14.4 | 2.8 | 4 → 4 | 0 (0) → 0 (0) | 0 (0) → 0 (0) | 0 → 0 | 0 (0.0/tree of 65) | 0 |
| pale_oak_elder | 32 | 32 | 10.1 → 5.0 | 7.0 | 3.5 | -6 → 1 | 32 (305) → 0 (0) | 32 (684) → 30 (197) | 32 → 20 | 740 (23.1/tree of 65) | 236 |
| acacia | 32 | 0 | 3.2 → 3.2 | 8.9 | 6.0 | 2 → 2 | 0 (0) → 0 (0) | 1 (2) → 1 (2) | 3 → 3 | 0 (0.0/tree of 41) | 0 |
| cherry | 32 | 0 | 4.7 → 4.7 | 9.0 | 3.9 | 3 → 3 | 0 (0) → 0 (0) | 0 (0) → 0 (0) | 7 → 7 | 0 (0.0/tree of 26) | 0 |
| mangrove | 32 | 18 | 9.1 → 7.6 | 10.6 | 4.9 | -3 → 2 | 8 (12) → 0 (0) | 10 (16) → 0 (0) | 16 → 3 | 49 (1.5/tree of 87) | 37 |

**What is still "seen" after, and why it is not the trunk:**
* *pale oak 30 (197)*: the horizontal LIMBS that run out to the clumps at the crown's top layer (the trunk-follow picks up their
  first cells). They were just as visible before; the crown is flat, open-centred and holey by design (§7.4 veteran).
* *jungle young 11 (20)*: the cacao forms (unchanged): the 3-block stem / jorquette 2 under the fan top in a 6–8 block tree.
* *acacia 1 (2)*: acacia_21's limb ends poking out at the plate rim (see §8).
* *cov < 2* left in cherry 7, jungle elder 6, acacia 3, mangrove 3, jungle old 1, jungle young 5 (cacao), pale oak 20: tips
  2–8 under the crown top inside an open-centred / hollow crown (top face reachable from straight above only through the
  centre); none is above the crown or seen in the top 4 layers except the pale-oak limbs above.

## 5. Decisions for Abs0lum (the proposal assumes the first option each time)

1. **Stag limbs** (oak elder 1–2, pale oak elder 2–4 dead diagonal log runs that rise 2–5 above the crown): **not drawn** (they
   are exactly "wood noticeable at the top"), or kept as deliberate dead wood (`STAG_OVER_CROWN = True`: drawn from the stem's
   new top, as before).
2. **Pale oak**: accept that the veteran loses its tall bare top — the stem now ends 1–3 under the crown's top under a 1–4-leaf plug,
   the template is 1–7 blocks shorter (height 12 → 5–11) and reads as a low flat crown (sheet `pale_oak_elder`) — or exempt pale oak from v4.
3. **Oak old**: its stag head (dead leader 2–4 above the crown) was a research choice (§2.6); v4 removes it, the same way birch
   v3 removed birch old's 1–2 block dead leader.

## 6. The exact code change

Three files. `tree_gen.py` gets the rule (`TRUNK_TIP_DEPTH`, `crown_base_of`, `sink_tip`) and calls it in oak / spruce /
jungle (birch untouched). `tree_gen_square.py` gets `sink_stem` (the w×w stem, contiguous from the ground) called at the end of
every species, and the two stag-limb loops record their endpoints (same RNG draws) and draw them after the cut only if
`STAG_OVER_CROWN`. **`tree_rescale.py` needs a `frame=` parameter** — without it, removing a stag head lowers the template's
measured height H0 and, for the groups with a FIXED target height (oak old 16, oak elder 22, pale oak 12.5, mangrove 12), the
whole crown is re-sampled with a new vertical scale (first attempt: oak old lost 2751 crown leaves and gained 5647 elsewhere;
mangrove 877 / 1124). Pinning each template to the H/CBH of its first rescale (build 218, stored as `before` in
`_docs/trees/rescale_report.json`) keeps every crown cell for cell.

```diff
--- a/tools/tree_gen.py
+++ b/tools/tree_gen.py
@@ -18,6 +18,7 @@
 Usage: tree_gen.py oak  -> _staging/trees/oak/<oak_age_nn>.mcstructure + TREE-PILOT-oak.png"""
 import json
 import math
+from collections import Counter
 import random
 import sys
 import zlib
@@ -135,6 +136,9 @@
         ellipsoid(leaves, (0, (trunk_top + 1) if not old else crown_top - 2, 0), dome_r, dome_r * (0.4 if old else 0.5),
                   dome_r * rnd.uniform(0.85, 1.15), shell=2.0, rnd=rnd)
         info = {"H": H, "crown_base": cb, "fork": fork, "radius": round(R, 1), "clumps": n, "trunk_top": trunk_top}
+    trunk, core, _gone = sink_tip(trunk, leaves, TRUNK_TIP_DEPTH["oak"][age])     # v4: the tip under the apex
+    leaves |= set(core)
+    info["trunk_top"] = max(c[1] for c in trunk)
     trunk_set = set(trunk)
     leaves = {c for c in leaves if c not in trunk_set and c[1] >= 1}
     # drop leaves that touch nothing (no face neighbour among leaves or trunk): no single floating cubes
@@ -153,6 +157,42 @@
     return leaves
 
 
+# v4 (10-06, his "make sure the trunk isn't sticking out too high and that it's not noticeable at the top of the tree"):
+# EVERY species' trunk tip sits TRUNK_TIP_DEPTH crown layers under the crown's own apex over the stem (birch v3's rule,
+# anchored at the apex instead of the crown base so conifers / emergents keep their visible stems); never cut lower than
+# one block into the crown (birch v3's floor). RNG-free: applied after the crown is built, so every crown keeps its cells.
+TRUNK_TIP_DEPTH = {"oak": {"young": 4, "mature": 5, "old": 5},
+                   "spruce": {"young": 3, "mature": 4, "old": 4},
+                   "jungle": {"young": 4, "mature": 3, "old": 3}}
+
+
+def crown_base_of(leaves):
+    """the lowest leaf layer with >= 4 leaves (tree_rescale / tree_proportions' CBH)."""
+    per = Counter(c[1] for c in leaves)
+    return min((y for y, c in per.items() if c >= 4), default=min(per) if per else 1)
+
+
+def sink_tip(trunk, leaves, depth, anchor="stem"):
+    """-> (kept, core, gone). apex = the highest leaf over the trunk's top cells (their column and the 8 around it), never
+    above the crown's own top (a tuft on a bare leader does not count); the crown's top when nothing is over the stem or
+    anchor == "crown" (an open-centred crown: pale oak); cut = max(crown base + 1, apex - depth). Trunk cells above the
+    cut leave the trunk: at or under the apex they become leaves (the crown's core, as birch v3), above the apex they are
+    dropped (no bare leader / stag head over the crown)."""
+    trunk = list(trunk)
+    if not trunk or not leaves:
+        return trunk, [], []
+    top = max(c[1] for c in trunk)
+    cols = {(c[0] + dx, c[2] + dz) for c in trunk if c[1] == top for dx in (-1, 0, 1) for dz in (-1, 0, 1)}
+    over = [c[1] for c in leaves if (c[0], c[2]) in cols]
+    crown_top = max(c[1] for c in leaves)
+    apex = crown_top if (anchor == "crown" or not over) else min(max(over), crown_top)
+    cut = max(crown_base_of(leaves) + 1, apex - depth)
+    kept = [c for c in trunk if c[1] <= cut]
+    core = [c for c in trunk if cut < c[1] <= apex]
+    gone = [c for c in trunk if c[1] > max(cut, apex)]
+    return kept, core, gone
+
+
 BIRCH_TRUNK_INTO_CROWN = 1     # v3 (10-05, his 16:50): the trunk ends this many blocks above the crown's base (was: to the top)
 
 
@@ -294,7 +334,10 @@
         leaves.add((0, y, 0))
     if old:                                              # blunter top
         ellipsoid(leaves, (0, H - 1, 0), 1.5, 1.5, 1.5, rnd=rnd, rough=0.2)
-    info = {"H": H, "crown_base": base, "radius": round(R0, 1), "tiers": len(tiers), "forest": forest, "double": double}
+    trunk, core, _gone = sink_tip(trunk, leaves, TRUNK_TIP_DEPTH["spruce"][age])  # v4: the leader is leaves
+    leaves |= set(core)
+    info = {"H": H, "crown_base": base, "radius": round(R0, 1), "tiers": len(tiers), "forest": forest, "double": double,
+            "trunk_top": max(c[1] for c in trunk)}
     return trunk, finish(trunk, leaves), info
 
 
@@ -354,6 +397,9 @@
         dome = R * 0.6
         ellipsoid(leaves, (0, bole + 4.5, 0), dome, dome * (0.35 if umbrella else 0.5), dome, shell=2.0, rnd=rnd)
         info = {"H": H, "crown_base": bole, "radius": round(R, 1), "limbs": n, "umbrella": umbrella, "dead": len(dead)}
+    trunk, core, _gone = sink_tip(trunk, leaves, TRUNK_TIP_DEPTH["jungle"][age])  # v4: the tip under the apex
+    leaves |= set(core)
+    info["trunk_top"] = max(c[1] for c in trunk)
     return trunk, finish(trunk, leaves), info
 
 
```

```diff
--- a/tools/tree_gen_square.py
+++ b/tools/tree_gen_square.py
@@ -31,6 +31,30 @@
 }
 
 
+# v4 (10-06): the stem's tip under the crown apex (tree_gen.sink_tip), per species. The oak / pale oak elders' dead stag
+# limbs keep their RNG draws but are drawn AFTER the cut: not at all (False), or from the stem's new top (True, as before)
+STAG_OVER_CROWN = False
+TRUNK_TIP_DEPTH = {"oak_elder": 5, "spruce_elder": 4, "jungle_elder": 3, "dark_oak_elder": 3, "pale_oak_elder": 3,
+                   "acacia": 3, "cherry": 3, "mangrove": 3}
+
+
+def sink_stem(logs, leaves, species, w, anchor="stem"):
+    """the stem = logs over the w x w footprint, contiguous from the ground; cut by tree_gen.sink_tip. Mutates logs /
+    leaves; returns the stem's new top y."""
+    foot = {(x, z) for x in range(w) for z in range(w)}
+    stem = set()
+    for (x, z) in foot:
+        y = 0
+        while (x, y, z) in logs:
+            stem.add((x, y, z))
+            y += 1
+    kept, core, gone = T.sink_tip(sorted(stem), leaves, TRUNK_TIP_DEPTH[species], anchor)
+    for c in core + gone:
+        logs.discard(c)
+    leaves |= set(core)
+    return max(c[1] for c in kept)
+
+
 def line(a, b):
     """3-D Bresenham (integer cells) from a to b inclusive."""
     a = tuple(int(round(v)) for v in a)
@@ -73,11 +97,15 @@
         limb(logs, (0.5, y0, 0.5), mid); limb(logs, mid, tip)
         rc = rnd.uniform(3.0, 4.0)
         T.ellipsoid(leaves, tip, rc, rc * 0.75, rc, shell=2.0, rnd=rnd)
+    stags = []
     for _ in range(rnd.randint(1, 2)):                     # stag limbs: bare logs above the crown
         az = rnd.uniform(0, 2 * math.pi)
-        limb(logs, (0.5, H - 5, 0.5), (0.5 + math.cos(az) * 3, H + rnd.randint(0, 2), 0.5 + math.sin(az) * 3))
+        stags.append((0.5 + math.cos(az) * 3, H + rnd.randint(0, 2), 0.5 + math.sin(az) * 3))
     T.ellipsoid(leaves, (0.5, H - 4, 0.5), R * 0.5, R * 0.3, R * 0.5, shell=2.0, rnd=rnd)
-    return logs, leaves, extra, {"H": H, "fork": fork, "radius": round(R, 1), "limbs": n}
+    top = sink_stem(logs, leaves, "oak_elder", 2)          # v4
+    for tip in stags if STAG_OVER_CROWN else ():
+        limb(logs, (0.5, min(H - 5, top), 0.5), tip)
+    return logs, leaves, extra, {"H": H, "fork": fork, "radius": round(R, 1), "limbs": n, "trunk_top": top}
 
 
 def spruce_elder(rnd, idx):
@@ -107,7 +135,8 @@
         leaves.add((0, y, 0))
     if idx % 4 == 0:
         T.ellipsoid(leaves, (0.5, H - 1, 0.5), 1.6, 1.6, 1.6, rnd=rnd, rough=0.2)
-    return logs, leaves, extra, {"H": H, "radius": round(R0, 1), "tiers": len(tiers), "missing_low": missing}
+    top = sink_stem(logs, leaves, "spruce_elder", 2)       # v4: the leader is leaves
+    return logs, leaves, extra, {"H": H, "radius": round(R0, 1), "tiers": len(tiers), "missing_low": missing, "trunk_top": top}
 
 
 def jungle_elder(rnd, idx):
@@ -134,6 +163,7 @@
         T.ellipsoid(leaves, tip, rc, rc * 0.6, rc, shell=2.0, rnd=rnd)
     dome = R * 0.6
     T.ellipsoid(leaves, (0.5, bole + 4.5, 0.5), dome, dome * 0.4, dome, shell=2.0, rnd=rnd)
+    sink_stem(logs, leaves, "jungle_elder", 2)             # v4
     return logs, leaves, extra, {"H": H, "bole": bole, "radius": round(R, 1), "limbs": n, "dead": len(dead)}
 
 
@@ -159,6 +189,7 @@
         limb(logs, (0.5, split, 0.5), low); limb(logs, low, tip)
         T.ellipsoid(leaves, tip, 2.5, 2.0, 2.5, shell=1.5, rnd=rnd)
     T.ellipsoid(leaves, (0.5, H * 0.65, 0.5), R * 0.8, (H * 0.5) * 0.45, R * 0.8, shell=2.5, rnd=rnd)
+    sink_stem(logs, leaves, "dark_oak_elder", 2)           # v4
     return logs, leaves, extra, {"H": H, "split": split, "radius": round(R, 1), "leaders": n}
 
 
@@ -183,15 +214,19 @@
         limb(logs, (0.5, first + rnd.uniform(0, 2), 0.5), tip)
         rc = rnd.uniform(2.5, 3.5)
         T.ellipsoid(leaves, tip, rc, rc * 0.7, rc, shell=2.0, rnd=rnd, rough=0.35)
+    stags = []
     for _ in range(rnd.randint(2, 4)):                     # stag limbs
         az = rnd.uniform(0, 2 * math.pi); up = rnd.randint(2, 5)
-        limb(logs, (0.5, H - 4, 0.5), (0.5 + math.cos(az) * rnd.uniform(2, 5), crown_top + up, 0.5 + math.sin(az) * rnd.uniform(2, 5)))
+        stags.append((0.5 + math.cos(az) * rnd.uniform(2, 5), crown_top + up, 0.5 + math.sin(az) * rnd.uniform(2, 5)))
     for _ in range(rnd.randint(2, 4)):                     # epicormic tufts on the trunk
         y = rnd.randint(2, max(3, H - 3)); az = rnd.uniform(0, 2 * math.pi)
         leaves.add((int(round(0.5 + math.cos(az) * 1.5)), y, int(round(0.5 + math.sin(az) * 1.5))))
     holes = rnd.uniform(0.2, 0.4)
     leaves = {c for c in leaves if rnd.random() > holes * 0.5}
-    return logs, leaves, extra, {"H": H, "radius": round(R, 1), "split": split, "crown_top": round(crown_top, 1)}
+    top = sink_stem(logs, leaves, "pale_oak_elder", 2, "crown")  # v4: open centre -> anchored at the crown's top
+    for tip in stags if STAG_OVER_CROWN else ():
+        limb(logs, (0.5, min(H - 4, top), 0.5), tip)
+    return logs, leaves, extra, {"H": H, "radius": round(R, 1), "split": split, "crown_top": round(crown_top, 1), "trunk_top": top}
 
 
 def acacia(rnd, idx):
@@ -218,6 +253,7 @@
     if old:
         az = rnd.uniform(0, 2 * math.pi)
         limb(logs, (0, fork, 0), (math.cos(az) * 4, fork + 3, math.sin(az) * 4))
+    sink_stem(logs, leaves, "acacia", 1)                   # v4
     return logs, leaves, extra, {"H": H, "fork": fork, "radius": round(R, 1), "limbs": n, "plates": plates, "old": old}
 
 
@@ -242,6 +278,7 @@
     if old:
         az = rnd.uniform(0, 2 * math.pi)
         limb(logs, (0, 2, 0), (math.cos(az) * 3, 5, math.sin(az) * 3))
+    sink_stem(logs, leaves, "cherry", 1)                   # v4
     return logs, leaves, extra, {"H": H, "radius": round(R, 1), "scaffolds": n, "layers": layers, "old": old}
 
 
@@ -282,6 +319,7 @@
                 if c not in logs:
                     extra.add(c)
     T.ellipsoid(leaves, (0, cb + 2.5, 0), R, R * (0.6 if old else 0.75), R, shell=2.0, rnd=rnd)
+    sink_stem(logs, leaves, "mangrove", 1)                 # v4
     return logs, leaves, extra, {"H": H, "radius": round(R, 1), "roots": nroots, "root_start": start, "old": old}
 
 
```

```diff
--- a/tools/tree_rescale.py
+++ b/tools/tree_rescale.py
@@ -89,13 +89,15 @@
     return {"H": top - base + 1, "CBH": crown_y - base, "CW": cw, "leaves": len(leaves), "woods": len(woods)}
 
 
-def rescale(path, out_path, dry=False):
+def rescale(path, out_path, dry=False, frame=None):
     name, root, names, cells = read(path)
     rootc = next(p for p, pi in cells.items() if names[pi].startswith("pw:") and names[pi].endswith("_root"))
     grp = group_of(path.stem)
     sw, h_new, cbh_new = TARGETS.get(grp, (1.0, None, None))
     m0 = metrics(cells, names, rootc)
     H0, C0 = m0["H"], max(1, m0["CBH"])
+    if frame:                                            # v4 (10-06): the frame of the template's FIRST rescale (D-C525),
+        H0, C0 = frame["H"], max(1, frame["CBH"])        # so a regenerated template maps its crown cell for cell
     # a new crown base without a new height SHIFTS the crown down (no stretch: a stretched crown repeats its layers)
     H1 = h_new if h_new else (H0 - (C0 - cbh_new) if cbh_new else H0)
     C1 = cbh_new if cbh_new else min(C0, max(1, round(C0 * H1 / H0)))
```

## 7. What must be regenerated, and what must be asserted unchanged

**Before anything:** freeze the frames — copy `_docs/trees/rescale_report.json` to e.g. `_docs/trees/rescale_frames_218.json`
and read frames from the copy (`tree_rescale.main()` rewrites `rescale_report.json`; the build must call `rescale()`
directly, never `main()`, and never `tree_gen.main()` — that writes `_staging/` and a PNG to outputs).

**BP-02 (next build from 1.3.227):** regenerate all 544 into a stage dir — birch: `tree_gen.build("birch", age, idx)` written
directly (as build 224); every other group: `build()` → `rescale(src, dst, frame=frames[stem])` (src file must be named
`<stem>.mcstructure`: rescale picks its target from the file name) — then install into `structures/pw/trees/`.
Assert:
* exactly 544 files, names unchanged; **275 byte-identical to 1.3.227** (all 72 birch, all jungle mature/old/elder, dark oak,
  acacia, cherry, 12 cacao jungle young, 14 mangrove, 1 oak young) — any other byte-identical / changed count is a failure;
* per changed template: root cell (block + `pw:tpl`, `pw:tpl_hi`, `minecraft:cardinal_direction`) and its local position
  unchanged; x/z size unchanged (y size shrinks in 91: mangrove, oak elder, oak old, pale oak — the
  `structure_template_feature` places from the corner, `grounded`/`unburied` test the base, so placement is unaffected);
  every before-leaf still a leaf; new leaves only on former logs; no log added; `minecraft:mangrove_roots` unchanged; all wood
  26-connected to the root; leaf `pw:variant` (the look band) differs only within Manhattan 3 of a removed log (4 where the
  rescale stretches vertically: 30 cells in oak young / mature / elder);
* per template: 0 trunk logs above the crown top; the §4 "seen in top 4 layers" numbers.
* Features, tree rules, `pw_ft_tpl_index.js` and every script unchanged (names and order are unchanged, so
  `FT_TPL_NAMES` / `FT_TPL_INDEX` stay byte-identical — assert it).

**RP-01 (next build from 1.3.124):** the falling-tree carbon copies — `tools/ft_tpl_gen_lite.py <DST> <new BP-02>` with 1.3.121's
meshing `--maxb=8 --clusters=12 --runfrom=3 --close=3` (the build_rp01_124 recipe). Assert the file set is unchanged and that
**only the 269 changed templates' copies** change; the other 275 byte-identical. The render-controller array order is untouched.

**Runtime side effects (no code change, worth knowing):** the felled log count drops by the "logs removed" column (oak old
−7 per tree, oak elder −12 incl. stag limbs, pale oak −23); the fall duration is `FALLPHYS.fallDuration(trunkH)` from the
logs, so shortened trunks fall a little faster; leaves count unchanged except the new core leaves.

## 8. Retro hits outside the trunk (not part of this change — backlog candidates)

* **Acacia limb ends at the plate rims:** 255 log cells across the 32 acacias are visible from the sky (secondary limbs reach
  `pr × 0.5–0.9` from the limb tip while the plate is centred at `0.7 × tip` — they run past the plate edge). Pre-existing.
* **Pale oak horizontal limbs** on top of the flat crown are visible from above / the side (holes 20–40 %, open centre).
* **Jungle elder** limb ends at the crown edge (e.g. jungle_elder_08), **cherry** fork visible through the open centre from
  straight above (5–6 under the top). Not tips over the crown; pre-existing.

## 9. Preview sheets (`_docs/program228/`)

Each template: **BEFORE side | BEFORE top | AFTER side | AFTER top**; side = orthographic from the south, top = from the sky;
red outline = trunk tip; white outline = trunk hidden behind leaves (x-ray); orange-red fill = wood seen in the top 4 layers;
`[UNCHANGED]` = byte-identical.
* `TREE-TRUNK-BEFORE-AFTER-OVERVIEW.png` — the worst-before template of each of the 20 groups.
* `TREE-TRUNK-BEFORE-AFTER-<group>.png` — every template of the 11 changed groups: oak_young, oak_mature, oak_old, oak_elder,
  spruce_young, spruce_mature, spruce_old, spruce_elder, jungle_young, mangrove, pale_oak_elder.

What they show (looked at full size): **oak old** — before, a white-outlined column rises through the crown and ends in 1–3
orange-red cells above the leaves; after, the red tip outline sits mid-crown 4–9 under the top and the top view is
unchanged green. **oak elder** — before, the 1-wide leader pokes out of the top dome with 1–3 orange-red cells (leader tip +
stag-limb runs); after, nothing orange at the top, the tip 4–7 under the dome, the brown side limbs unchanged. **mangrove** —
before (e.g. 02, 05, 08) a red-topped log column stands 1–3 above the round crown; after the tip is inside it; the 14
`[UNCHANGED]` ones were already hidden. **spruce** — before the tip is 1–2 under the spire top (2 cells wide at the double
leaders); after 3–4 under, the spire is leaves. **jungle young** — the pole forms' tip goes from 2 to 4 under the top cap;
the cacao forms are `[UNCHANGED]`. **pale oak** — before a 2×2 trunk 2–6 blocks above a flat, low crown with orange stag runs;
after a low flat crown with the stem ending at its top layer; orange limb bars still show on top (§4).

## 10. Per-template table (all 544)

trunk tip / crown top / crown base in blocks above the root; `seen` = trunk logs seen in the top 4 layers; `sky` = trunk logs
above the crown base with nothing over them; `ht` = template height.

| template | result | trunk tip | crown top | crown base | gap | abv | seen | sky | cov | logs removed | logs → leaves | ht |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| oak_young_00 | changed | 7→5 | 8→8 | 3 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 9→9 |
| oak_young_01 | changed | 7→5 | 8→8 | 2 | 1→3 | 0→0 | 1→0 | 1→0 | 0→2 | 2 | 2 | 9→9 |
| oak_young_02 | changed | 7→5 | 8→8 | 2 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 9→9 |
| oak_young_03 | changed | 6→5 | 8→8 | 4 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_04 | changed | 6→5 | 8→8 | 4 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_05 | changed | 7→5 | 8→8 | 2 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 9→9 |
| oak_young_06 | changed | 5→4 | 8→8 | 3 | 3→4 | 0→0 | 0→0 | 0→0 | 3→4 | 1 | 1 | 9→9 |
| oak_young_07 | changed | 7→6 | 8→8 | 3 | 1→2 | 0→0 | 0→0 | 0→0 | 1→2 | 1 | 1 | 9→9 |
| oak_young_08 | changed | 6→5 | 8→8 | 3 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_09 | changed | 6→5 | 8→8 | 2 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_10 | changed | 6→4 | 8→8 | 3 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 9→9 |
| oak_young_11 | changed | 6→5 | 8→8 | 3 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_12 | = | 5→5 | 8→8 | 4 | 3→3 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 9→9 |
| oak_young_13 | changed | 6→5 | 8→8 | 4 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_14 | changed | 6→5 | 8→8 | 4 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_15 | changed | 5→4 | 8→8 | 3 | 3→4 | 0→0 | 0→0 | 0→0 | 3→4 | 1 | 1 | 9→9 |
| oak_young_16 | changed | 6→5 | 8→8 | 4 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_17 | changed | 6→5 | 8→8 | 4 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_18 | changed | 6→4 | 8→8 | 3 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 9→9 |
| oak_young_19 | changed | 6→5 | 8→8 | 4 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_20 | changed | 6→5 | 8→8 | 3 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| oak_young_21 | changed | 5→4 | 8→8 | 3 | 3→4 | 0→0 | 0→0 | 0→0 | 3→4 | 1 | 1 | 9→9 |
| oak_young_22 | changed | 7→6 | 8→8 | 3 | 1→2 | 0→0 | 0→0 | 0→0 | 1→2 | 1 | 1 | 9→9 |
| oak_young_23 | changed | 7→5 | 8→8 | 2 | 1→3 | 0→0 | 1→0 | 1→0 | 0→2 | 2 | 2 | 9→9 |
| oak_mature_00 | changed | 10→8 | 14→14 | 4 | 4→6 | 0→0 | 0→0 | 0→0 | 3→5 | 2 | 2 | 15→15 |
| oak_mature_01 | changed | 9→7 | 14→14 | 4 | 5→7 | 0→0 | 0→0 | 0→0 | 4→6 | 2 | 2 | 15→15 |
| oak_mature_02 | changed | 8→6 | 14→14 | 4 | 6→8 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 15→15 |
| oak_mature_03 | changed | 10→9 | 14→14 | 4 | 4→5 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 15→15 |
| oak_mature_04 | changed | 11→9 | 14→14 | 4 | 3→5 | 0→0 | 0→0 | 0→0 | 3→5 | 2 | 2 | 15→15 |
| oak_mature_05 | changed | 10→8 | 14→14 | 4 | 4→6 | 0→0 | 0→0 | 0→0 | 2→3 | 2 | 1 | 15→15 |
| oak_mature_06 | changed | 11→10 | 14→14 | 4 | 3→4 | 0→0 | 0→0 | 0→0 | 1→2 | 1 | 1 | 15→15 |
| oak_mature_07 | changed | 11→9 | 14→14 | 5 | 3→5 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 15→15 |
| oak_mature_08 | changed | 11→9 | 14→14 | 4 | 3→5 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 15→15 |
| oak_mature_09 | changed | 11→9 | 14→14 | 4 | 3→5 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 15→15 |
| oak_mature_10 | changed | 8→6 | 14→14 | 4 | 6→8 | 0→0 | 0→0 | 0→0 | 4→6 | 2 | 2 | 15→15 |
| oak_mature_11 | changed | 10→8 | 14→14 | 5 | 4→6 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 15→15 |
| oak_mature_12 | changed | 10→8 | 14→14 | 4 | 4→6 | 0→0 | 0→0 | 0→0 | 3→5 | 2 | 2 | 15→15 |
| oak_mature_13 | changed | 12→8 | 14→14 | 4 | 2→6 | 0→0 | 1→0 | 0→0 | 1→5 | 4 | 4 | 15→15 |
| oak_mature_14 | changed | 11→10 | 14→14 | 5 | 3→4 | 0→0 | 0→0 | 0→0 | 1→2 | 1 | 1 | 15→15 |
| oak_mature_15 | changed | 11→9 | 14→14 | 4 | 3→5 | 0→0 | 1→0 | 0→0 | 2→3 | 2 | 1 | 15→15 |
| oak_mature_16 | changed | 9→7 | 14→14 | 4 | 5→7 | 0→0 | 0→0 | 0→0 | 3→5 | 2 | 2 | 15→15 |
| oak_mature_17 | changed | 11→9 | 14→14 | 4 | 3→5 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 15→15 |
| oak_mature_18 | changed | 10→7 | 14→14 | 4 | 4→7 | 0→0 | 0→0 | 0→0 | 2→5 | 3 | 3 | 15→15 |
| oak_mature_19 | changed | 12→10 | 14→14 | 4 | 2→4 | 0→0 | 1→0 | 0→0 | 1→2 | 2 | 1 | 15→15 |
| oak_mature_20 | changed | 10→9 | 14→14 | 4 | 4→5 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 15→15 |
| oak_mature_21 | changed | 10→9 | 14→14 | 4 | 4→5 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 15→15 |
| oak_mature_22 | changed | 8→5 | 14→14 | 4 | 6→9 | 0→0 | 0→0 | 0→0 | 3→6 | 3 | 3 | 15→15 |
| oak_mature_23 | changed | 10→8 | 14→14 | 4 | 4→6 | 0→0 | 0→0 | 0→0 | 3→5 | 2 | 2 | 15→15 |
| oak_old_00 | changed | 15→5 | 14→14 | 4 | -1→9 | 1→0 | 4→0 | 1→0 | 0→6 | 10 | 6 | 16→15 |
| oak_old_01 | changed | 15→8 | 12→12 | 5 | -3→4 | 3→0 | 4→0 | 1→0 | 0→4 | 7 | 4 | 16→13 |
| oak_old_02 | changed | 15→6 | 12→12 | 4 | -3→6 | 3→0 | 3→0 | 1→0 | 0→6 | 9 | 6 | 16→13 |
| oak_old_03 | changed | 15→9 | 14→14 | 4 | -1→5 | 1→0 | 2→0 | 1→0 | 0→5 | 6 | 5 | 16→15 |
| oak_old_04 | changed | 15→10 | 14→14 | 6 | -1→4 | 1→0 | 1→0 | 1→0 | 0→4 | 5 | 4 | 16→15 |
| oak_old_05 | changed | 15→5 | 13→13 | 4 | -2→8 | 2→0 | 4→0 | 1→0 | 0→6 | 10 | 6 | 16→14 |
| oak_old_06 | changed | 15→9 | 13→13 | 6 | -2→4 | 2→0 | 3→0 | 1→0 | 0→4 | 6 | 4 | 16→14 |
| oak_old_07 | changed | 15→7 | 12→12 | 5 | -3→5 | 3→0 | 3→0 | 1→0 | 0→5 | 8 | 5 | 16→13 |
| oak_old_08 | changed | 15→8 | 13→13 | 4 | -2→5 | 2→0 | 2→0 | 1→0 | 0→5 | 7 | 5 | 16→14 |
| oak_old_09 | changed | 15→9 | 14→14 | 5 | -1→5 | 1→0 | 2→0 | 1→0 | 0→4 | 6 | 4 | 16→15 |
| oak_old_10 | changed | 15→8 | 15→15 | 4 | 0→7 | 0→0 | 3→0 | 1→0 | 0→6 | 7 | 6 | 16→16 |
| oak_old_11 | changed | 15→6 | 13→13 | 5 | -2→7 | 2→0 | 3→0 | 1→0 | 0→6 | 9 | 6 | 16→14 |
| oak_old_12 | changed | 15→8 | 13→13 | 4 | -2→5 | 2→0 | 3→0 | 1→0 | 0→4 | 7 | 4 | 16→14 |
| oak_old_13 | changed | 15→8 | 13→13 | 6 | -2→5 | 2→0 | 4→0 | 1→0 | 0→4 | 7 | 4 | 16→14 |
| oak_old_14 | changed | 15→8 | 13→13 | 4 | -2→5 | 2→0 | 3→0 | 1→0 | 0→5 | 7 | 5 | 16→14 |
| oak_old_15 | changed | 15→8 | 13→13 | 6 | -2→5 | 2→0 | 4→0 | 1→0 | 0→4 | 7 | 4 | 16→14 |
| oak_old_16 | changed | 15→8 | 14→14 | 7 | -1→6 | 1→0 | 2→0 | 1→0 | 0→5 | 7 | 5 | 16→15 |
| oak_old_17 | changed | 15→5 | 12→12 | 4 | -3→7 | 3→0 | 4→0 | 1→0 | 0→6 | 10 | 6 | 16→13 |
| oak_old_18 | changed | 15→9 | 13→13 | 3 | -2→4 | 2→0 | 4→0 | 1→0 | 0→4 | 6 | 4 | 16→14 |
| oak_old_19 | changed | 15→10 | 15→15 | 7 | 0→5 | 0→0 | 1→0 | 1→0 | 0→4 | 5 | 4 | 16→16 |
| oak_old_20 | changed | 15→8 | 12→12 | 3 | -3→4 | 3→0 | 3→0 | 1→0 | 0→4 | 7 | 4 | 16→13 |
| oak_old_21 | changed | 15→10 | 15→15 | 5 | 0→5 | 0→0 | 2→0 | 1→0 | 0→4 | 5 | 4 | 16→16 |
| oak_old_22 | changed | 15→7 | 15→15 | 5 | 0→8 | 0→0 | 3→0 | 1→0 | 0→5 | 8 | 5 | 16→16 |
| oak_old_23 | changed | 15→7 | 15→15 | 6 | 0→8 | 0→0 | 2→0 | 1→0 | 0→6 | 8 | 6 | 16→16 |
| oak_elder_00 | changed | 19→14 | 20→20 | 5 | 1→6 | 0→0 | 0→0 | 0→0 | 1→6 | 9 | 5 | 22→21 |
| oak_elder_01 | changed | 20→14 | 18→18 | 5 | -2→4 | 2→0 | 2→0 | 1→0 | 0→4 | 9 | 5 | 22→19 |
| oak_elder_02 | changed | 20→13 | 19→19 | 4 | -1→6 | 1→0 | 1→0 | 1→0 | 0→6 | 11 | 8 | 22→20 |
| oak_elder_03 | changed | 19→12 | 17→17 | 6 | -2→5 | 2→0 | 3→0 | 2→0 | 0→5 | 10 | 6 | 22→18 |
| oak_elder_04 | changed | 19→15 | 20→20 | 7 | 1→5 | 0→0 | 1→0 | 1→0 | 0→4 | 14 | 6 | 22→21 |
| oak_elder_05 | changed | 20→14 | 19→19 | 7 | -1→5 | 1→0 | 2→0 | 2→0 | 0→5 | 10 | 7 | 22→20 |
| oak_elder_06 | changed | 19→14 | 19→19 | 4 | 0→5 | 0→0 | 1→0 | 1→0 | 0→5 | 10 | 6 | 22→20 |
| oak_elder_07 | changed | 20→15 | 19→19 | 5 | -1→4 | 2→0 | 5→0 | 3→0 | 0→4 | 13 | 5 | 22→20 |
| oak_elder_08 | changed | 20→14 | 18→18 | 2 | -2→4 | 4→0 | 6→0 | 3→0 | 0→4 | 17 | 8 | 22→19 |
| oak_elder_09 | changed | 19→14 | 18→18 | 6 | -1→4 | 2→0 | 5→0 | 3→0 | 0→4 | 14 | 5 | 22→19 |
| oak_elder_10 | changed | 18→13 | 20→20 | 7 | 2→7 | 0→0 | 1→0 | 1→0 | 0→5 | 9 | 6 | 22→21 |
| oak_elder_11 | changed | 19→14 | 19→19 | 6 | 0→5 | 0→0 | 1→0 | 1→0 | 0→5 | 10 | 5 | 22→20 |
| oak_elder_12 | changed | 19→14 | 18→18 | 3 | -1→4 | 1→0 | 1→0 | 1→0 | 0→4 | 10 | 4 | 22→19 |
| oak_elder_13 | changed | 20→14 | 19→19 | 6 | -1→5 | 1→0 | 2→0 | 1→0 | 0→5 | 10 | 7 | 22→20 |
| oak_elder_14 | changed | 20→14 | 18→18 | 3 | -2→4 | 4→0 | 5→0 | 3→0 | 0→4 | 17 | 8 | 22→19 |
| oak_elder_15 | changed | 19→13 | 17→17 | 8 | -2→4 | 4→0 | 4→0 | 2→0 | 0→4 | 14 | 6 | 22→18 |
| oak_elder_16 | changed | 19→14 | 18→18 | 5 | -1→4 | 2→0 | 4→0 | 2→0 | 0→4 | 13 | 3 | 22→19 |
| oak_elder_17 | changed | 19→13 | 17→17 | 3 | -2→4 | 2→0 | 4→0 | 3→0 | 0→4 | 11 | 6 | 22→18 |
| oak_elder_18 | changed | 19→12 | 17→17 | 4 | -2→5 | 4→0 | 6→0 | 4→0 | 0→5 | 18 | 9 | 22→18 |
| oak_elder_19 | changed | 20→15 | 19→19 | 8 | -1→4 | 1→0 | 2→0 | 2→0 | 0→4 | 8 | 4 | 22→20 |
| oak_elder_20 | changed | 19→14 | 18→18 | 6 | -1→4 | 1→0 | 1→0 | 1→0 | 0→4 | 8 | 4 | 22→19 |
| oak_elder_21 | changed | 19→13 | 17→17 | 6 | -2→4 | 3→0 | 4→0 | 3→0 | 0→4 | 12 | 6 | 22→18 |
| oak_elder_22 | changed | 19→14 | 18→18 | 8 | -1→4 | 1→0 | 2→0 | 1→0 | 0→4 | 9 | 4 | 22→19 |
| oak_elder_23 | changed | 19→13 | 18→18 | 7 | -1→5 | 1→0 | 3→0 | 2→0 | 0→4 | 14 | 6 | 22→19 |
| oak_elder_24 | changed | 20→13 | 19→19 | 8 | -1→6 | 1→0 | 2→0 | 1→0 | 0→6 | 10 | 8 | 22→20 |
| oak_elder_25 | changed | 19→14 | 18→18 | 6 | -1→4 | 1→0 | 3→0 | 3→0 | 0→4 | 13 | 7 | 22→19 |
| oak_elder_26 | changed | 19→12 | 18→18 | 6 | -1→6 | 1→0 | 2→0 | 2→0 | 0→6 | 18 | 12 | 22→19 |
| oak_elder_27 | changed | 19→13 | 18→18 | 6 | -1→5 | 2→0 | 3→0 | 3→0 | 0→5 | 14 | 8 | 22→19 |
| oak_elder_28 | changed | 19→15 | 19→19 | 5 | 0→4 | 0→0 | 2→0 | 1→0 | 0→4 | 8 | 6 | 22→20 |
| oak_elder_29 | changed | 19→14 | 18→18 | 6 | -1→4 | 1→0 | 3→0 | 3→0 | 0→4 | 12 | 7 | 22→19 |
| oak_elder_30 | changed | 20→14 | 18→18 | 4 | -2→4 | 2→0 | 4→0 | 3→0 | 0→4 | 14 | 6 | 22→19 |
| oak_elder_31 | changed | 20→13 | 19→19 | 5 | -1→6 | 2→0 | 4→0 | 3→0 | 0→6 | 16 | 7 | 22→20 |
| birch_young_00 | = | 3→3 | 9→9 | 3 | 6→6 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 10→10 |
| birch_young_01 | = | 3→3 | 9→9 | 3 | 6→6 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 10→10 |
| birch_young_02 | = | 3→3 | 8→8 | 2 | 5→5 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 9→9 |
| birch_young_03 | = | 3→3 | 7→7 | 2 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 8→8 |
| birch_young_04 | = | 3→3 | 7→7 | 3 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 8→8 |
| birch_young_05 | = | 3→3 | 8→8 | 3 | 5→5 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 9→9 |
| birch_young_06 | = | 3→3 | 9→9 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 10→10 |
| birch_young_07 | = | 3→3 | 9→9 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 10→10 |
| birch_young_08 | = | 3→3 | 9→9 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 10→10 |
| birch_young_09 | = | 3→3 | 8→8 | 3 | 5→5 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 9→9 |
| birch_young_10 | = | 3→3 | 8→8 | 3 | 5→5 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 9→9 |
| birch_young_11 | = | 3→3 | 9→9 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 10→10 |
| birch_young_12 | = | 3→3 | 9→9 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 10→10 |
| birch_young_13 | = | 3→3 | 8→8 | 3 | 5→5 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 9→9 |
| birch_young_14 | = | 3→3 | 7→7 | 2 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 8→8 |
| birch_young_15 | = | 3→3 | 9→9 | 3 | 6→6 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 10→10 |
| birch_young_16 | = | 3→3 | 7→7 | 2 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 8→8 |
| birch_young_17 | = | 3→3 | 7→7 | 2 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 8→8 |
| birch_young_18 | = | 3→3 | 8→8 | 2 | 5→5 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 9→9 |
| birch_young_19 | = | 3→3 | 10→10 | 3 | 7→7 | 0→0 | 0→0 | 0→0 | 7→7 | 0 | 0 | 11→11 |
| birch_young_20 | = | 3→3 | 10→10 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 7→7 | 0 | 0 | 11→11 |
| birch_young_21 | = | 3→3 | 10→10 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 7→7 | 0 | 0 | 11→11 |
| birch_young_22 | = | 3→3 | 10→10 | 3 | 7→7 | 0→0 | 0→0 | 0→0 | 7→7 | 0 | 0 | 11→11 |
| birch_young_23 | = | 3→3 | 9→9 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 10→10 |
| birch_mature_00 | = | 7→7 | 17→17 | 6 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 18→18 |
| birch_mature_01 | = | 6→6 | 18→18 | 5 | 12→12 | 0→0 | 0→0 | 0→0 | 12→12 | 0 | 0 | 19→19 |
| birch_mature_02 | = | 5→5 | 16→16 | 4 | 11→11 | 0→0 | 0→0 | 0→0 | 11→11 | 0 | 0 | 17→17 |
| birch_mature_03 | = | 5→5 | 21→21 | 4 | 16→16 | 0→0 | 0→0 | 0→0 | 16→16 | 0 | 0 | 22→22 |
| birch_mature_04 | = | 5→5 | 15→15 | 4 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 16→16 |
| birch_mature_05 | = | 8→8 | 20→20 | 6 | 12→12 | 0→0 | 0→0 | 0→0 | 9→9 | 0 | 0 | 21→21 |
| birch_mature_06 | = | 7→7 | 20→20 | 6 | 13→13 | 0→0 | 0→0 | 0→0 | 13→13 | 0 | 0 | 21→21 |
| birch_mature_07 | = | 8→8 | 18→18 | 7 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 19→19 |
| birch_mature_08 | = | 6→6 | 16→16 | 5 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 17→17 |
| birch_mature_09 | = | 6→6 | 18→18 | 5 | 12→12 | 0→0 | 0→0 | 0→0 | 12→12 | 0 | 0 | 19→19 |
| birch_mature_10 | = | 8→8 | 21→21 | 7 | 13→13 | 0→0 | 0→0 | 0→0 | 13→13 | 0 | 0 | 22→22 |
| birch_mature_11 | = | 6→6 | 17→17 | 4 | 11→11 | 0→0 | 0→0 | 0→0 | 8→8 | 0 | 0 | 18→18 |
| birch_mature_12 | = | 7→7 | 15→15 | 5 | 8→8 | 0→0 | 0→0 | 0→0 | 8→8 | 0 | 0 | 16→16 |
| birch_mature_13 | = | 7→7 | 18→18 | 6 | 11→11 | 0→0 | 0→0 | 0→0 | 11→11 | 0 | 0 | 19→19 |
| birch_mature_14 | = | 8→8 | 16→16 | 7 | 8→8 | 0→0 | 0→0 | 0→0 | 8→8 | 0 | 0 | 17→17 |
| birch_mature_15 | = | 8→8 | 17→17 | 7 | 9→9 | 0→0 | 0→0 | 0→0 | 9→9 | 0 | 0 | 18→18 |
| birch_mature_16 | = | 6→6 | 16→16 | 5 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 17→17 |
| birch_mature_17 | = | 7→7 | 19→19 | 5 | 12→12 | 0→0 | 0→0 | 0→0 | 11→11 | 0 | 0 | 20→20 |
| birch_mature_18 | = | 7→7 | 17→17 | 6 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 18→18 |
| birch_mature_19 | = | 7→7 | 21→21 | 6 | 14→14 | 0→0 | 0→0 | 0→0 | 11→11 | 0 | 0 | 22→22 |
| birch_mature_20 | = | 6→6 | 17→17 | 5 | 11→11 | 0→0 | 0→0 | 0→0 | 9→9 | 0 | 0 | 18→18 |
| birch_mature_21 | = | 6→6 | 19→19 | 5 | 13→13 | 0→0 | 0→0 | 0→0 | 13→13 | 0 | 0 | 20→20 |
| birch_mature_22 | = | 8→8 | 17→17 | 7 | 9→9 | 0→0 | 0→0 | 0→0 | 9→9 | 0 | 0 | 18→18 |
| birch_mature_23 | = | 6→6 | 19→19 | 5 | 13→13 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 20→20 |
| birch_old_00 | = | 8→8 | 20→20 | 7 | 12→12 | 0→0 | 0→0 | 0→0 | 12→12 | 0 | 0 | 21→21 |
| birch_old_01 | = | 6→6 | 18→18 | 5 | 12→12 | 0→0 | 0→0 | 0→0 | 12→12 | 0 | 0 | 19→19 |
| birch_old_02 | = | 9→9 | 19→19 | 8 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 20→20 |
| birch_old_03 | = | 7→7 | 17→17 | 6 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 18→18 |
| birch_old_04 | = | 6→6 | 19→19 | 5 | 13→13 | 0→0 | 0→0 | 0→0 | 13→13 | 0 | 0 | 20→20 |
| birch_old_05 | = | 8→8 | 19→19 | 6 | 11→11 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 20→20 |
| birch_old_06 | = | 6→6 | 19→19 | 5 | 13→13 | 0→0 | 0→0 | 0→0 | 13→13 | 0 | 0 | 20→20 |
| birch_old_07 | = | 6→6 | 21→21 | 5 | 15→15 | 0→0 | 0→0 | 0→0 | 15→15 | 0 | 0 | 22→22 |
| birch_old_08 | = | 9→9 | 21→21 | 8 | 12→12 | 0→0 | 0→0 | 0→0 | 11→11 | 0 | 0 | 22→22 |
| birch_old_09 | = | 9→9 | 16→16 | 7 | 7→7 | 0→0 | 0→0 | 0→0 | 7→7 | 0 | 0 | 17→17 |
| birch_old_10 | = | 8→8 | 17→17 | 7 | 9→9 | 0→0 | 0→0 | 0→0 | 9→9 | 0 | 0 | 18→18 |
| birch_old_11 | = | 8→8 | 16→16 | 6 | 8→8 | 0→0 | 0→0 | 0→0 | 6→6 | 0 | 0 | 17→17 |
| birch_old_12 | = | 6→6 | 21→21 | 5 | 15→15 | 0→0 | 0→0 | 0→0 | 15→15 | 0 | 0 | 22→22 |
| birch_old_13 | = | 8→8 | 18→18 | 7 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 19→19 |
| birch_old_14 | = | 9→9 | 15→15 | 7 | 6→6 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 16→16 |
| birch_old_15 | = | 6→6 | 19→19 | 5 | 13→13 | 0→0 | 0→0 | 0→0 | 13→13 | 0 | 0 | 20→20 |
| birch_old_16 | = | 8→8 | 21→21 | 7 | 13→13 | 0→0 | 0→0 | 0→0 | 13→13 | 0 | 0 | 22→22 |
| birch_old_17 | = | 8→8 | 22→22 | 6 | 14→14 | 0→0 | 0→0 | 0→0 | 12→12 | 0 | 0 | 23→23 |
| birch_old_18 | = | 9→9 | 19→19 | 8 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 20→20 |
| birch_old_19 | = | 7→7 | 16→16 | 6 | 9→9 | 0→0 | 0→0 | 0→0 | 9→9 | 0 | 0 | 17→17 |
| birch_old_20 | = | 6→6 | 17→17 | 5 | 11→11 | 0→0 | 0→0 | 0→0 | 9→9 | 0 | 0 | 18→18 |
| birch_old_21 | = | 6→6 | 16→16 | 5 | 10→10 | 0→0 | 0→0 | 0→0 | 10→10 | 0 | 0 | 17→17 |
| birch_old_22 | = | 8→8 | 21→21 | 7 | 13→13 | 0→0 | 0→0 | 0→0 | 13→13 | 0 | 0 | 22→22 |
| birch_old_23 | = | 8→8 | 20→20 | 6 | 12→12 | 0→0 | 0→0 | 0→0 | 9→9 | 0 | 0 | 21→21 |
| spruce_young_00 | changed | 6→5 | 8→8 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| spruce_young_01 | changed | 8→6 | 9→9 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 10→10 |
| spruce_young_02 | changed | 6→4 | 7→7 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 8→8 |
| spruce_young_03 | changed | 7→6 | 9→9 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 10→10 |
| spruce_young_04 | changed | 7→5 | 8→8 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 9→9 |
| spruce_young_05 | changed | 8→6 | 9→9 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 10→10 |
| spruce_young_06 | changed | 7→5 | 8→8 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 9→9 |
| spruce_young_07 | changed | 9→7 | 10→10 | 1 | 1→3 | 0→0 | 2→0 | 0→0 | 1→3 | 4 | 4 | 11→11 |
| spruce_young_08 | changed | 4→3 | 6→6 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 7→7 |
| spruce_young_09 | changed | 6→5 | 8→8 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 9→9 |
| spruce_young_10 | changed | 5→4 | 7→7 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 8→8 |
| spruce_young_11 | changed | 7→5 | 8→8 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 9→9 |
| spruce_young_12 | changed | 5→4 | 7→7 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 8→8 |
| spruce_young_13 | changed | 7→6 | 9→9 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 10→10 |
| spruce_young_14 | changed | 8→7 | 10→10 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 11→11 |
| spruce_young_15 | changed | 6→4 | 7→7 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 8→8 |
| spruce_young_16 | changed | 9→7 | 10→10 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 11→11 |
| spruce_young_17 | changed | 8→7 | 10→10 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 11→11 |
| spruce_young_18 | changed | 4→3 | 6→6 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 7→7 |
| spruce_young_19 | changed | 8→6 | 9→9 | 1 | 1→3 | 0→0 | 2→0 | 0→0 | 1→3 | 4 | 4 | 10→10 |
| spruce_young_20 | changed | 6→4 | 7→7 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 8→8 |
| spruce_young_21 | changed | 8→7 | 10→10 | 1 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 11→11 |
| spruce_young_22 | changed | 5→3 | 6→6 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 7→7 |
| spruce_young_23 | changed | 8→6 | 9→9 | 1 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 10→10 |
| spruce_mature_00 | changed | 20→17 | 21→21 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 22→22 |
| spruce_mature_01 | changed | 21→18 | 22→22 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 23→23 |
| spruce_mature_02 | changed | 17→15 | 19→19 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 20→20 |
| spruce_mature_03 | changed | 22→19 | 23→23 | 8 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 24→24 |
| spruce_mature_04 | changed | 22→19 | 23→23 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 24→24 |
| spruce_mature_05 | changed | 22→20 | 24→24 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 25→25 |
| spruce_mature_06 | changed | 22→20 | 24→24 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 25→25 |
| spruce_mature_07 | changed | 21→18 | 22→22 | 8 | 1→4 | 0→0 | 3→0 | 1→0 | 0→4 | 5 | 5 | 23→23 |
| spruce_mature_08 | changed | 19→16 | 20→20 | 1 | 1→4 | 0→0 | 1→0 | 0→0 | 1→4 | 3 | 3 | 21→21 |
| spruce_mature_09 | changed | 19→17 | 21→21 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 22→22 |
| spruce_mature_10 | changed | 20→18 | 22→22 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 23→23 |
| spruce_mature_11 | changed | 23→21 | 25→25 | 12 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 26→26 |
| spruce_mature_12 | changed | 20→18 | 22→22 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 23→23 |
| spruce_mature_13 | changed | 16→14 | 18→18 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 19→19 |
| spruce_mature_14 | changed | 23→20 | 24→24 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 25→25 |
| spruce_mature_15 | changed | 24→21 | 25→25 | 11 | 1→4 | 0→0 | 1→0 | 0→0 | 1→4 | 3 | 3 | 26→26 |
| spruce_mature_16 | changed | 19→16 | 20→20 | 1 | 1→4 | 0→0 | 1→0 | 0→0 | 1→4 | 3 | 3 | 21→21 |
| spruce_mature_17 | changed | 20→18 | 22→22 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 23→23 |
| spruce_mature_18 | changed | 21→19 | 23→23 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 24→24 |
| spruce_mature_19 | changed | 21→19 | 23→23 | 9 | 2→4 | 0→0 | 3→0 | 0→0 | 1→4 | 4 | 4 | 24→24 |
| spruce_mature_20 | changed | 20→18 | 22→22 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 23→23 |
| spruce_mature_21 | changed | 19→17 | 21→21 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 22→22 |
| spruce_mature_22 | changed | 25→22 | 26→26 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 27→27 |
| spruce_mature_23 | changed | 17→15 | 19→19 | 6 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 20→20 |
| spruce_old_00 | changed | 25→23 | 27→27 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 28→28 |
| spruce_old_01 | changed | 29→26 | 30→30 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 31→31 |
| spruce_old_02 | changed | 28→26 | 30→30 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 31→31 |
| spruce_old_03 | changed | 28→25 | 29→29 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 30→30 |
| spruce_old_04 | changed | 29→26 | 30→30 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 31→31 |
| spruce_old_05 | changed | 22→19 | 23→23 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 24→24 |
| spruce_old_06 | changed | 25→23 | 27→27 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 28→28 |
| spruce_old_07 | changed | 25→22 | 26→26 | 1 | 1→4 | 0→0 | 2→0 | 0→0 | 1→4 | 5 | 5 | 27→27 |
| spruce_old_08 | changed | 26→23 | 27→27 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 28→28 |
| spruce_old_09 | changed | 23→21 | 25→25 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 26→26 |
| spruce_old_10 | changed | 22→20 | 24→24 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 25→25 |
| spruce_old_11 | changed | 23→20 | 24→24 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 25→25 |
| spruce_old_12 | changed | 27→24 | 28→28 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 29→29 |
| spruce_old_13 | changed | 26→23 | 27→27 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 28→28 |
| spruce_old_14 | changed | 27→24 | 28→28 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 29→29 |
| spruce_old_15 | changed | 24→21 | 25→25 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 26→26 |
| spruce_old_16 | changed | 26→23 | 27→27 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 28→28 |
| spruce_old_17 | changed | 24→21 | 25→25 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 26→26 |
| spruce_old_18 | changed | 28→26 | 30→30 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 31→31 |
| spruce_old_19 | changed | 25→23 | 27→27 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 1→4 | 4 | 4 | 28→28 |
| spruce_old_20 | changed | 24→21 | 25→25 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 26→26 |
| spruce_old_21 | changed | 27→24 | 28→28 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 29→29 |
| spruce_old_22 | changed | 21→18 | 22→22 | 1 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 23→23 |
| spruce_old_23 | changed | 24→22 | 26→26 | 1 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 27→27 |
| spruce_elder_00 | changed | 29→27 | 31→31 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 32→32 |
| spruce_elder_01 | changed | 26→24 | 28→28 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 29→29 |
| spruce_elder_02 | changed | 27→25 | 29→29 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 30→30 |
| spruce_elder_03 | changed | 26→24 | 28→28 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 29→29 |
| spruce_elder_04 | changed | 29→27 | 31→31 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 32→32 |
| spruce_elder_05 | changed | 29→27 | 31→31 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 32→32 |
| spruce_elder_06 | changed | 32→30 | 34→34 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 35→35 |
| spruce_elder_07 | changed | 26→24 | 28→28 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 29→29 |
| spruce_elder_08 | changed | 27→25 | 29→29 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 30→30 |
| spruce_elder_09 | changed | 29→27 | 31→31 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 32→32 |
| spruce_elder_10 | changed | 28→26 | 30→30 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 31→31 |
| spruce_elder_11 | changed | 30→28 | 32→32 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 33→33 |
| spruce_elder_12 | changed | 27→25 | 29→29 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 30→30 |
| spruce_elder_13 | changed | 32→30 | 34→34 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 35→35 |
| spruce_elder_14 | changed | 31→29 | 33→33 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 34→34 |
| spruce_elder_15 | changed | 30→28 | 32→32 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 33→33 |
| spruce_elder_16 | changed | 30→28 | 32→32 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 33→33 |
| spruce_elder_17 | changed | 30→28 | 32→32 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 33→33 |
| spruce_elder_18 | changed | 27→25 | 29→29 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 30→30 |
| spruce_elder_19 | changed | 31→29 | 33→33 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 34→34 |
| spruce_elder_20 | changed | 30→28 | 32→32 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 33→33 |
| spruce_elder_21 | changed | 26→24 | 28→28 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 29→29 |
| spruce_elder_22 | changed | 27→25 | 29→29 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 30→30 |
| spruce_elder_23 | changed | 28→26 | 30→30 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 31→31 |
| spruce_elder_24 | changed | 32→30 | 34→34 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 35→35 |
| spruce_elder_25 | changed | 31→29 | 33→33 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 34→34 |
| spruce_elder_26 | changed | 26→24 | 28→28 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 29→29 |
| spruce_elder_27 | changed | 30→28 | 32→32 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 33→33 |
| spruce_elder_28 | changed | 28→26 | 30→30 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 31→31 |
| spruce_elder_29 | changed | 26→24 | 28→28 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 29→29 |
| spruce_elder_30 | changed | 31→29 | 33→33 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 34→34 |
| spruce_elder_31 | changed | 29→27 | 31→31 | 1 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 32→32 |
| jungle_young_00 | = | 6→6 | 8→8 | 5 | 2→2 | 0→0 | 2→2 | 0→0 | 2→2 | 0 | 0 | 9→9 |
| jungle_young_01 | changed | 13→11 | 15→15 | 5 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 16→16 |
| jungle_young_02 | = | 6→6 | 8→8 | 5 | 2→2 | 0→0 | 2→2 | 0→0 | 2→2 | 0 | 0 | 9→9 |
| jungle_young_03 | changed | 10→8 | 12→12 | 5 | 2→4 | 0→0 | 1→0 | 0→0 | 2→4 | 2 | 2 | 13→13 |
| jungle_young_04 | = | 6→6 | 8→8 | 5 | 2→2 | 0→0 | 2→2 | 0→0 | 2→2 | 0 | 0 | 9→9 |
| jungle_young_05 | changed | 9→7 | 11→11 | 5 | 2→4 | 0→0 | 1→0 | 0→0 | 2→4 | 2 | 2 | 12→12 |
| jungle_young_06 | = | 6→6 | 8→8 | 5 | 2→2 | 0→0 | 2→2 | 0→0 | 2→2 | 0 | 0 | 9→9 |
| jungle_young_07 | changed | 12→10 | 14→14 | 5 | 2→4 | 0→0 | 1→0 | 0→0 | 2→4 | 2 | 2 | 15→15 |
| jungle_young_08 | = | 6→6 | 8→8 | 5 | 2→2 | 0→0 | 2→2 | 0→0 | 2→2 | 0 | 0 | 9→9 |
| jungle_young_09 | changed | 13→11 | 15→15 | 5 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 16→16 |
| jungle_young_10 | = | 6→6 | 8→8 | 5 | 2→2 | 0→0 | 2→2 | 0→0 | 2→2 | 0 | 0 | 9→9 |
| jungle_young_11 | changed | 12→10 | 14→14 | 5 | 2→4 | 0→0 | 1→0 | 0→0 | 2→4 | 2 | 2 | 15→15 |
| jungle_young_12 | = | 6→6 | 8→8 | 5 | 2→2 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 9→9 |
| jungle_young_13 | changed | 11→9 | 13→13 | 5 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 14→14 |
| jungle_young_14 | = | 4→4 | 6→6 | 5 | 2→2 | 0→0 | 2→2 | 0→0 | 0→0 | 0 | 0 | 7→7 |
| jungle_young_15 | changed | 11→9 | 13→13 | 5 | 2→4 | 0→0 | 1→0 | 0→0 | 2→4 | 2 | 2 | 14→14 |
| jungle_young_16 | = | 4→4 | 7→7 | 5 | 3→3 | 0→0 | 1→1 | 0→0 | 0→0 | 0 | 0 | 8→8 |
| jungle_young_17 | changed | 13→11 | 15→15 | 5 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 16→16 |
| jungle_young_18 | = | 4→4 | 6→6 | 5 | 2→2 | 0→0 | 2→2 | 0→0 | 0→0 | 0 | 0 | 7→7 |
| jungle_young_19 | changed | 11→9 | 13→13 | 5 | 2→4 | 0→0 | 2→0 | 0→0 | 2→4 | 2 | 2 | 14→14 |
| jungle_young_20 | = | 4→4 | 7→7 | 5 | 3→3 | 0→0 | 1→1 | 0→0 | 0→0 | 0 | 0 | 8→8 |
| jungle_young_21 | changed | 10→8 | 12→12 | 5 | 2→4 | 0→0 | 1→0 | 0→0 | 2→4 | 2 | 2 | 13→13 |
| jungle_young_22 | = | 4→4 | 6→6 | 5 | 2→2 | 0→0 | 2→2 | 0→0 | 0→0 | 0 | 0 | 7→7 |
| jungle_young_23 | changed | 10→8 | 12→12 | 5 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 13→13 |
| jungle_mature_00 | = | 15→15 | 21→21 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 22→22 |
| jungle_mature_01 | = | 17→17 | 22→22 | 15 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 23→23 |
| jungle_mature_02 | = | 14→14 | 22→22 | 15 | 8→8 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 23→23 |
| jungle_mature_03 | = | 15→15 | 21→21 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 22→22 |
| jungle_mature_04 | = | 16→16 | 22→22 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 23→23 |
| jungle_mature_05 | = | 14→14 | 22→22 | 15 | 8→8 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 23→23 |
| jungle_mature_06 | = | 16→16 | 21→21 | 15 | 5→5 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 22→22 |
| jungle_mature_07 | = | 14→14 | 21→21 | 15 | 7→7 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 22→22 |
| jungle_mature_08 | = | 15→15 | 21→21 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 22→22 |
| jungle_mature_09 | = | 14→14 | 20→20 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 21→21 |
| jungle_mature_10 | = | 17→17 | 22→22 | 15 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 23→23 |
| jungle_mature_11 | = | 15→15 | 22→22 | 15 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 23→23 |
| jungle_mature_12 | = | 16→16 | 20→20 | 15 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 21→21 |
| jungle_mature_13 | = | 16→16 | 22→22 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 23→23 |
| jungle_mature_14 | = | 16→16 | 22→22 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 23→23 |
| jungle_mature_15 | = | 14→14 | 20→20 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 21→21 |
| jungle_mature_16 | = | 14→14 | 21→21 | 15 | 7→7 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 22→22 |
| jungle_mature_17 | = | 16→16 | 22→22 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 23→23 |
| jungle_mature_18 | = | 16→16 | 21→21 | 15 | 5→5 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 22→22 |
| jungle_mature_19 | = | 15→15 | 21→21 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 22→22 |
| jungle_mature_20 | = | 15→15 | 22→22 | 15 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 23→23 |
| jungle_mature_21 | = | 15→15 | 20→20 | 15 | 5→5 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 21→21 |
| jungle_mature_22 | = | 15→15 | 21→21 | 15 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 22→22 |
| jungle_mature_23 | = | 16→16 | 21→21 | 15 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 22→22 |
| jungle_old_00 | = | 16→16 | 22→22 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 23→23 |
| jungle_old_01 | = | 16→16 | 23→23 | 16 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 24→24 |
| jungle_old_02 | = | 16→16 | 23→23 | 16 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 24→24 |
| jungle_old_03 | = | 15→15 | 22→22 | 16 | 7→7 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 23→23 |
| jungle_old_04 | = | 18→18 | 24→24 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_old_05 | = | 17→17 | 23→23 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 24→24 |
| jungle_old_06 | = | 17→17 | 21→21 | 16 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 22→22 |
| jungle_old_07 | = | 17→17 | 23→23 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 24→24 |
| jungle_old_08 | = | 17→17 | 23→23 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 24→24 |
| jungle_old_09 | = | 18→18 | 22→22 | 16 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 23→23 |
| jungle_old_10 | = | 17→17 | 24→24 | 16 | 7→7 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_old_11 | = | 17→17 | 24→24 | 16 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 25→25 |
| jungle_old_12 | = | 18→18 | 22→22 | 16 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 23→23 |
| jungle_old_13 | = | 15→15 | 21→21 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 22→22 |
| jungle_old_14 | = | 17→17 | 23→23 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 24→24 |
| jungle_old_15 | = | 17→17 | 22→22 | 16 | 5→5 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 23→23 |
| jungle_old_16 | = | 16→16 | 23→23 | 16 | 7→7 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 24→24 |
| jungle_old_17 | = | 17→17 | 23→23 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 24→24 |
| jungle_old_18 | = | 16→16 | 22→22 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 23→23 |
| jungle_old_19 | = | 18→18 | 24→24 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_old_20 | = | 18→18 | 23→23 | 16 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 24→24 |
| jungle_old_21 | = | 16→16 | 22→22 | 16 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 23→23 |
| jungle_old_22 | = | 18→18 | 23→23 | 16 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 24→24 |
| jungle_old_23 | = | 17→17 | 24→24 | 16 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 25→25 |
| jungle_elder_00 | = | 20→20 | 26→26 | 19 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 27→27 |
| jungle_elder_01 | = | 20→20 | 24→24 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_elder_02 | = | 20→20 | 25→25 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 26→26 |
| jungle_elder_03 | = | 20→20 | 25→25 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 26→26 |
| jungle_elder_04 | = | 20→20 | 25→25 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 26→26 |
| jungle_elder_05 | = | 20→20 | 24→24 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_elder_06 | = | 21→21 | 25→25 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 26→26 |
| jungle_elder_07 | = | 20→20 | 25→25 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 26→26 |
| jungle_elder_08 | = | 22→22 | 25→25 | 19 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 26→26 |
| jungle_elder_09 | = | 21→21 | 25→25 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 26→26 |
| jungle_elder_10 | = | 21→21 | 26→26 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 27→27 |
| jungle_elder_11 | = | 20→20 | 24→24 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_elder_12 | = | 19→19 | 25→25 | 19 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 26→26 |
| jungle_elder_13 | = | 20→20 | 26→26 | 19 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 27→27 |
| jungle_elder_14 | = | 20→20 | 26→26 | 19 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 27→27 |
| jungle_elder_15 | = | 20→20 | 24→24 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_elder_16 | = | 19→19 | 24→24 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_elder_17 | = | 20→20 | 24→24 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_elder_18 | = | 20→20 | 26→26 | 19 | 6→6 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 27→27 |
| jungle_elder_19 | = | 20→20 | 25→25 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 26→26 |
| jungle_elder_20 | = | 21→21 | 25→25 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 26→26 |
| jungle_elder_21 | = | 20→20 | 24→24 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_elder_22 | = | 20→20 | 25→25 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 26→26 |
| jungle_elder_23 | = | 22→22 | 26→26 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 27→27 |
| jungle_elder_24 | = | 20→20 | 25→25 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 26→26 |
| jungle_elder_25 | = | 20→20 | 24→24 | 19 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 25→25 |
| jungle_elder_26 | = | 21→21 | 26→26 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 27→27 |
| jungle_elder_27 | = | 19→19 | 25→25 | 19 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 26→26 |
| jungle_elder_28 | = | 20→20 | 25→25 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 26→26 |
| jungle_elder_29 | = | 20→20 | 25→25 | 19 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 26→26 |
| jungle_elder_30 | = | 19→19 | 25→25 | 19 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 26→26 |
| jungle_elder_31 | = | 19→19 | 25→25 | 19 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 26→26 |
| dark_oak_elder_00 | = | 7→7 | 13→13 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 14→14 |
| dark_oak_elder_01 | = | 7→7 | 14→14 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 15→15 |
| dark_oak_elder_02 | = | 6→6 | 12→12 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 13→13 |
| dark_oak_elder_03 | = | 8→8 | 16→16 | 2 | 8→8 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 17→17 |
| dark_oak_elder_04 | = | 8→8 | 14→14 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 15→15 |
| dark_oak_elder_05 | = | 7→7 | 12→12 | 5 | 5→5 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 13→13 |
| dark_oak_elder_06 | = | 9→9 | 18→18 | 2 | 9→9 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 19→19 |
| dark_oak_elder_07 | = | 8→8 | 14→14 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 15→15 |
| dark_oak_elder_08 | = | 6→6 | 14→14 | 2 | 8→8 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 15→15 |
| dark_oak_elder_09 | = | 8→8 | 12→12 | 2 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 13→13 |
| dark_oak_elder_10 | = | 6→6 | 19→19 | 2 | 13→13 | 0→0 | 0→0 | 0→0 | 5→5 | 0 | 0 | 20→20 |
| dark_oak_elder_11 | = | 6→6 | 11→11 | 2 | 5→5 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 12→12 |
| dark_oak_elder_12 | = | 7→7 | 16→16 | 2 | 9→9 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 17→17 |
| dark_oak_elder_13 | = | 6→6 | 13→13 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 14→14 |
| dark_oak_elder_14 | = | 8→8 | 15→15 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 16→16 |
| dark_oak_elder_15 | = | 9→9 | 16→16 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 17→17 |
| dark_oak_elder_16 | = | 7→7 | 13→13 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 14→14 |
| dark_oak_elder_17 | = | 7→7 | 15→15 | 2 | 8→8 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 16→16 |
| dark_oak_elder_18 | = | 6→6 | 13→13 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 14→14 |
| dark_oak_elder_19 | = | 7→7 | 13→13 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 14→14 |
| dark_oak_elder_20 | = | 9→9 | 15→15 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 16→16 |
| dark_oak_elder_21 | = | 5→5 | 11→11 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 12→12 |
| dark_oak_elder_22 | = | 7→7 | 15→15 | 2 | 8→8 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 16→16 |
| dark_oak_elder_23 | = | 8→8 | 16→16 | 2 | 8→8 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 17→17 |
| dark_oak_elder_24 | = | 9→9 | 16→16 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 17→17 |
| dark_oak_elder_25 | = | 6→6 | 12→12 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 13→13 |
| dark_oak_elder_26 | = | 9→9 | 16→16 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 17→17 |
| dark_oak_elder_27 | = | 7→7 | 16→16 | 8 | 9→9 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 17→17 |
| dark_oak_elder_28 | = | 8→8 | 17→17 | 8 | 9→9 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 18→18 |
| dark_oak_elder_29 | = | 8→8 | 14→14 | 2 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 15→15 |
| dark_oak_elder_30 | = | 7→7 | 17→17 | 2 | 10→10 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 18→18 |
| dark_oak_elder_31 | = | 6→6 | 13→13 | 2 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 14→14 |
| pale_oak_elder_00 | changed | 10→4 | 5→5 | 3 | -5→1 | 14→0 | 22→8 | 9→4 | 0→0 | 25 | 3 | 12→6 |
| pale_oak_elder_01 | changed | 10→6 | 8→8 | 4 | -2→2 | 2→0 | 16→6 | 12→5 | 0→0 | 20 | 8 | 12→9 |
| pale_oak_elder_02 | changed | 11→3 | 5→5 | 3 | -6→2 | 19→0 | 27→7 | 9→2 | 0→0 | 29 | 8 | 12→6 |
| pale_oak_elder_03 | changed | 10→5 | 6→7 | 3 | -4→2 | 14→0 | 23→6 | 9→3 | 0→2 | 25 | 4 | 12→8 |
| pale_oak_elder_04 | changed | 10→5 | 7→7 | 4 | -3→2 | 15→0 | 31→10 | 9→3 | 0→2 | 28 | 8 | 12→8 |
| pale_oak_elder_05 | changed | 10→4 | 7→7 | 3 | -3→3 | 13→0 | 18→2 | 9→3 | 0→0 | 32 | 12 | 12→8 |
| pale_oak_elder_06 | changed | 10→3 | 4→4 | 2 | -6→1 | 16→0 | 29→11 | 8→3 | 0→0 | 24 | 2 | 12→5 |
| pale_oak_elder_07 | changed | 10→5 | 8→8 | 4 | -2→3 | 3→0 | 11→4 | 12→5 | 0→0 | 21 | 12 | 12→9 |
| pale_oak_elder_08 | changed | 8→3 | 5→5 | 2 | -3→2 | 10→0 | 23→8 | 8→4 | 0→0 | 23 | 8 | 12→6 |
| pale_oak_elder_09 | changed | 9→4 | 6→6 | 3 | -3→2 | 10→0 | 19→8 | 8→5 | 0→0 | 22 | 4 | 12→7 |
| pale_oak_elder_10 | changed | 11→6 | 8→8 | 4 | -3→2 | 7→0 | 22→9 | 11→2 | 0→0 | 20 | 4 | 12→9 |
| pale_oak_elder_11 | changed | 11→7 | 10→10 | 6 | -1→3 | 4→0 | 19→2 | 9→3 | 0→3 | 21 | 12 | 12→11 |
| pale_oak_elder_12 | changed | 10→6 | 6→8 | 3 | -4→2 | 15→0 | 28→4 | 11→7 | 0→2 | 22 | 4 | 12→9 |
| pale_oak_elder_13 | changed | 10→7 | 9→9 | 5 | -1→2 | 1→0 | 18→8 | 11→5 | 0→2 | 17 | 8 | 12→10 |
| pale_oak_elder_14 | changed | 11→6 | 9→10 | 5 | -2→4 | 10→0 | 16→0 | 9→3 | 0→0 | 23 | 17 | 12→11 |
| pale_oak_elder_15 | changed | 11→4 | 6→6 | 3 | -5→2 | 12→0 | 25→9 | 8→4 | 0→0 | 19 | 4 | 12→7 |
| pale_oak_elder_16 | changed | 11→4 | 6→6 | 3 | -5→2 | 16→0 | 34→11 | 10→3 | 0→0 | 34 | 8 | 12→7 |
| pale_oak_elder_17 | changed | 9→5 | 6→6 | 4 | -3→1 | 4→0 | 21→13 | 8→3 | 0→1 | 16 | 4 | 12→7 |
| pale_oak_elder_18 | changed | 10→5 | 8→8 | 4 | -2→3 | 4→0 | 14→5 | 10→6 | 0→0 | 22 | 6 | 12→9 |
| pale_oak_elder_19 | changed | 11→6 | 7→7 | 4 | -4→1 | 15→0 | 29→9 | 10→4 | 0→0 | 27 | 8 | 12→8 |
| pale_oak_elder_20 | changed | 10→6 | 8→8 | 5 | -2→2 | 2→0 | 22→9 | 8→1 | 0→2 | 22 | 8 | 12→9 |
| pale_oak_elder_21 | changed | 10→4 | 7→7 | 3 | -3→3 | 7→0 | 15→5 | 9→5 | 0→0 | 21 | 6 | 12→8 |
| pale_oak_elder_22 | changed | 9→5 | 6→6 | 3 | -3→1 | 12→0 | 20→5 | 8→2 | 0→0 | 26 | 8 | 12→7 |
| pale_oak_elder_23 | changed | 11→7 | 8→9 | 4 | -3→2 | 14→0 | 24→0 | 8→3 | 0→2 | 23 | 8 | 12→10 |
| pale_oak_elder_24 | changed | 9→2 | 4→4 | 1 | -5→2 | 14→0 | 24→6 | 5→2 | 0→0 | 27 | 6 | 12→5 |
| pale_oak_elder_25 | changed | 10→4 | 6→6 | 2 | -4→2 | 11→0 | 20→3 | 8→2 | 0→0 | 24 | 8 | 12→7 |
| pale_oak_elder_26 | changed | 10→7 | 9→9 | 3 | -1→2 | 1→0 | 18→8 | 9→3 | 0→2 | 13 | 8 | 12→10 |
| pale_oak_elder_27 | changed | 11→6 | 8→8 | 4 | -3→2 | 7→0 | 15→4 | 10→7 | 0→2 | 14 | 4 | 12→9 |
| pale_oak_elder_28 | changed | 9→6 | 8→8 | 4 | -1→2 | 2→0 | 14→2 | 11→3 | 0→2 | 17 | 8 | 12→9 |
| pale_oak_elder_29 | changed | 10→6 | 9→9 | 3 | -1→3 | 7→0 | 23→4 | 8→3 | 0→3 | 31 | 12 | 12→10 |
| pale_oak_elder_30 | changed | 11→5 | 7→7 | 4 | -4→2 | 12→0 | 25→9 | 7→5 | 0→2 | 21 | 4 | 12→8 |
| pale_oak_elder_31 | changed | 10→4 | 7→7 | 3 | -3→3 | 12→0 | 19→2 | 9→2 | 0→0 | 31 | 12 | 12→8 |
| acacia_00 | = | 2→2 | 9→9 | 6 | 7→7 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| acacia_01 | = | 5→5 | 9→9 | 6 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_02 | = | 2→2 | 9→9 | 6 | 7→7 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| acacia_03 | = | 3→3 | 9→9 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_04 | = | 4→4 | 9→9 | 6 | 5→5 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| acacia_05 | = | 2→2 | 9→9 | 6 | 7→7 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| acacia_06 | = | 3→3 | 9→9 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| acacia_07 | = | 5→5 | 9→9 | 6 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_08 | = | 3→3 | 9→9 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| acacia_09 | = | 2→2 | 9→9 | 6 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_10 | = | 3→3 | 9→9 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| acacia_11 | = | 2→2 | 9→9 | 6 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_12 | = | 2→2 | 8→8 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 9→9 |
| acacia_13 | = | 3→3 | 9→9 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| acacia_14 | = | 2→2 | 9→9 | 6 | 7→7 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_15 | = | 2→2 | 9→9 | 6 | 7→7 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| acacia_16 | = | 5→5 | 9→9 | 6 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| acacia_17 | = | 3→3 | 9→9 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_18 | = | 4→4 | 9→9 | 6 | 5→5 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| acacia_19 | = | 4→4 | 9→9 | 6 | 5→5 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_20 | = | 2→2 | 9→9 | 6 | 7→7 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| acacia_21 | = | 7→7 | 9→9 | 6 | 2→2 | 0→0 | 2→2 | 0→0 | 1→1 | 0 | 0 | 10→10 |
| acacia_22 | = | 5→5 | 9→9 | 6 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| acacia_23 | = | 3→3 | 9→9 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_24 | = | 2→2 | 8→8 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 9→9 |
| acacia_25 | = | 4→4 | 9→9 | 6 | 5→5 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| acacia_26 | = | 1→1 | 9→9 | 6 | 8→8 | 0→0 | 0→0 | 0→0 | 0→0 | 0 | 0 | 10→10 |
| acacia_27 | = | 3→3 | 9→9 | 6 | 6→6 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| acacia_28 | = | 6→6 | 9→9 | 6 | 3→3 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_29 | = | 2→2 | 9→9 | 6 | 7→7 | 0→0 | 0→0 | 0→0 | 0→0 | 0 | 0 | 10→10 |
| acacia_30 | = | 4→4 | 9→9 | 6 | 5→5 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| acacia_31 | = | 4→4 | 9→9 | 6 | 5→5 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| cherry_00 | = | 6→6 | 9→9 | 5 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_01 | = | 5→5 | 9→9 | 5 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| cherry_02 | = | 5→5 | 9→9 | 3 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_03 | = | 4→4 | 9→9 | 4 | 5→5 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| cherry_04 | = | 4→4 | 9→9 | 4 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 10→10 |
| cherry_05 | = | 5→5 | 9→9 | 4 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| cherry_06 | = | 5→5 | 9→9 | 5 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| cherry_07 | = | 4→4 | 9→9 | 4 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 10→10 |
| cherry_08 | = | 5→5 | 9→9 | 3 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| cherry_09 | = | 5→5 | 9→9 | 5 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| cherry_10 | = | 4→4 | 9→9 | 4 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_11 | = | 5→5 | 9→9 | 3 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_12 | = | 6→6 | 9→9 | 5 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_13 | = | 4→4 | 9→9 | 4 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 10→10 |
| cherry_14 | = | 5→5 | 9→9 | 3 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| cherry_15 | = | 5→5 | 9→9 | 5 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| cherry_16 | = | 4→4 | 9→9 | 4 | 5→5 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| cherry_17 | = | 6→6 | 9→9 | 4 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_18 | = | 4→4 | 9→9 | 4 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_19 | = | 3→3 | 9→9 | 4 | 6→6 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_20 | = | 5→5 | 9→9 | 3 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| cherry_21 | = | 3→3 | 9→9 | 3 | 6→6 | 0→0 | 0→0 | 1→1 | 0→0 | 0 | 0 | 10→10 |
| cherry_22 | = | 3→3 | 9→9 | 3 | 6→6 | 0→0 | 0→0 | 1→1 | 0→0 | 0 | 0 | 10→10 |
| cherry_23 | = | 6→6 | 9→9 | 3 | 3→3 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 10→10 |
| cherry_24 | = | 5→5 | 9→9 | 5 | 4→4 | 0→0 | 0→0 | 0→0 | 3→3 | 0 | 0 | 10→10 |
| cherry_25 | = | 4→4 | 9→9 | 3 | 5→5 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_26 | = | 5→5 | 9→9 | 3 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| cherry_27 | = | 5→5 | 9→9 | 5 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| cherry_28 | = | 5→5 | 9→9 | 5 | 4→4 | 0→0 | 0→0 | 0→0 | 4→4 | 0 | 0 | 10→10 |
| cherry_29 | = | 5→5 | 9→9 | 3 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_30 | = | 5→5 | 9→9 | 4 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 10→10 |
| cherry_31 | = | 4→4 | 9→9 | 4 | 5→5 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 10→10 |
| mangrove_00 | changed | 10→8 | 11→11 | 5 | 1→3 | 0→0 | 1→0 | 1→0 | 0→2 | 2 | 2 | 12→12 |
| mangrove_01 | = | 9→9 | 11→11 | 6 | 2→2 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_02 | changed | 11→6 | 8→8 | 3 | -3→2 | 3→0 | 4→0 | 1→0 | 0→2 | 5 | 2 | 12→9 |
| mangrove_03 | = | 8→8 | 11→11 | 5 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_04 | = | 7→7 | 11→11 | 4 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_05 | changed | 11→7 | 9→9 | 4 | -2→2 | 2→0 | 2→0 | 1→0 | 0→2 | 4 | 2 | 12→10 |
| mangrove_06 | changed | 9→8 | 11→11 | 5 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 12→12 |
| mangrove_07 | = | 7→7 | 11→11 | 6 | 4→4 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 12→12 |
| mangrove_08 | changed | 11→8 | 10→10 | 5 | -1→2 | 1→0 | 1→0 | 1→0 | 0→2 | 3 | 2 | 12→11 |
| mangrove_09 | = | 8→8 | 11→11 | 5 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_10 | = | 8→8 | 11→11 | 5 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_11 | changed | 11→8 | 11→11 | 5 | 0→3 | 0→0 | 1→0 | 1→0 | 0→3 | 3 | 3 | 12→12 |
| mangrove_12 | changed | 11→7 | 10→10 | 5 | -1→3 | 1→0 | 1→0 | 1→0 | 0→3 | 4 | 3 | 12→11 |
| mangrove_13 | = | 7→7 | 11→11 | 6 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_14 | changed | 10→8 | 11→11 | 5 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 12→12 |
| mangrove_15 | changed | 9→7 | 11→11 | 5 | 2→4 | 0→0 | 0→0 | 0→0 | 2→4 | 2 | 2 | 12→12 |
| mangrove_16 | = | 8→8 | 11→11 | 5 | 3→3 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 12→12 |
| mangrove_17 | changed | 10→8 | 11→11 | 5 | 1→3 | 0→0 | 0→0 | 0→0 | 1→3 | 2 | 2 | 12→12 |
| mangrove_18 | changed | 10→7 | 11→11 | 5 | 1→4 | 0→0 | 0→0 | 0→0 | 1→4 | 3 | 3 | 12→12 |
| mangrove_19 | = | 7→7 | 11→11 | 5 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_20 | changed | 11→7 | 10→10 | 4 | -1→3 | 1→0 | 1→0 | 1→0 | 0→3 | 4 | 3 | 12→11 |
| mangrove_21 | = | 7→7 | 11→11 | 6 | 4→4 | 0→0 | 0→0 | 0→0 | 1→1 | 0 | 0 | 12→12 |
| mangrove_22 | = | 8→8 | 11→11 | 5 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_23 | changed | 11→8 | 10→10 | 5 | -1→2 | 1→0 | 1→0 | 1→0 | 0→2 | 3 | 2 | 12→11 |
| mangrove_24 | changed | 9→8 | 11→11 | 5 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 12→12 |
| mangrove_25 | changed | 9→8 | 11→11 | 5 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 12→12 |
| mangrove_26 | changed | 11→7 | 10→10 | 4 | -1→3 | 1→0 | 2→0 | 1→0 | 0→3 | 4 | 3 | 12→11 |
| mangrove_27 | = | 7→7 | 11→11 | 5 | 4→4 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_28 | = | 8→8 | 11→11 | 5 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
| mangrove_29 | changed | 11→7 | 9→9 | 4 | -2→2 | 2→0 | 2→0 | 2→1 | 0→2 | 4 | 2 | 12→10 |
| mangrove_30 | changed | 9→8 | 11→11 | 4 | 2→3 | 0→0 | 0→0 | 0→0 | 2→3 | 1 | 1 | 12→12 |
| mangrove_31 | = | 8→8 | 11→11 | 6 | 3→3 | 0→0 | 0→0 | 0→0 | 2→2 | 0 | 0 | 12→12 |
