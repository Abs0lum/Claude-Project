# TREES notes — slice 2026-10-07 04:18-04:25 CT (task: his 04:12 spruce rulings, D-C1007-R231b)

## Rulings to implement
1. "tip height" = ONLY the trunk top (as already built: crown/tree height unchanged).
2. Spruce cap: wider/taller cone that reads as a separate cap, continuing the look of the existing crown TOP he likes
   ("The top ones finish nicely, already. Something that continues that look.") -> study the crown-top profile of the
   spruce templates (radius per layer down from the leader) and extend that SAME profile downward/outward over the
   lowered trunk top, instead of the current fixed-radius solid cone.
3. Lower mature/old trunks by >2 ONLY where needed, decided by the x-ray scan: lower only logs that stay visible
   through the crown, only as far as needed.
4. Seamless birch/oak bark: APPROVED — keep _staging/trees231/RP-01/textures/blocks/bark/ (54 files) as chosen version.

## Files
- tools/tree_gen.py — spruce_cone_tip() at line 314; flags DODECA_231 line 221; CONE_RISE/CONE_R lines 222-223;
  call site ~line 400; cone leaves full-cube look ~line 499.
- Backup before this slice's edits: _garbage/TREES-pre/tree_gen.cone1-before-0412.py (cone v1 = current staged spruce).
  Older: _garbage/TREES-pre/tree_gen.v5-before-cone.py; v5 spruce structures in _garbage/TREES-pre/trees231-v5-spruce.
- X-ray scan: tools/tree_trunk_sheet_228.py analyse(): for trunk logs with y >= leaf_top-3, "seen" if any of 5 rays
  (up, +x, -x, +z, -z) passes no cell. Earlier acacia work counted sky-visible logs the same way. NOTE: it only checks
  the top 4 layers — for "trunk shows as a dark stripe up the middle" (his/my 03:55 read) the scan must be run over
  ALL in-crown logs (y >= crown base), horizontal rays only + up; reuse its ray logic in a new measure step.
- Staging: _staging/trees231/{structures, regen_trees231.py, verify_trees231.py, measure_trees231.py,
  cone_sheet_trees231.py, tree_view.py, MD5SUMS-structures.txt, README.md}.

## Decisions (this slice)
- None applied yet; no code edited.

## Next steps (plan)
1. Measure: for each of 72 spruce templates, crown radius per layer from the leaf top downward (top ~5 layers) =
   the "profile he likes"; x-ray count of visible in-crown trunk logs per template (v5 and cone v1).
2. Replace spruce_cone_tip(): cap radius per layer = the crown-top profile continued (same slope r(y) fitted from the
   top layers, extended down to new_top-1 and a bit wider/taller per ruling 2); keep RNG-free, never above crown top.
3. X-ray-guided lowering (mature/old): after the base 1-2 lowering, while the top remaining trunk log is x-ray visible
   (horizontal/up rays escape) and new_top > crown_base+1, lower one more; record per template logs lowered + scan
   numbers before/after.
4. Regen spruce (72) into _staging/trees231/structures via regen_trees231.py; birch/oak must stay byte-identical
   (144/144); update MD5SUMS; verify_trees231.py.
5. Render before (cone v1) / after with cone_sheet_trees231.py; VIEW full-res; README + status; report table.

## Finding at 04:20 (numbers, pre-rescale, 18/72 sampled; script _staging/trees231/profile_spruce_top.py)
- Crown-top profile he likes: radius by layer from the leaf top ~0-1 | 1-1.4 | 1-1.4 | 1-2.2 | 1.4-2.2 -> slope ~0.3-0.4
  blocks of radius per layer. Leaf top minus trunk top: young 3, mature/old 4.
- X-ray visible in-crown trunk logs (v5): young 0-1/3-8, mature 1-5/15-20, old 5-10/21-26.
- Mechanism candidate for the "dark stripe": mature/old tiers are every 2 layers (step=2, tree_gen.py spruce()) and the
  tier ellipsoids have y-radius 0.7 -> the layer between two tiers has NO leaf next to the trunk (profile r=0 rows), so
  those logs are bare horizontally from crown base to top. Visible logs are spread down the whole crown, not just at
  the tip -> x-ray-guided tip lowering will remove only the top 1-3 of them. A fix for the rest needs a leaf collar on
  between-tier layers (ADD cells: a scope change -> ask Abs0lum / lead before applying).
- Must re-check these numbers on the RESCALED structures (regen pipeline rescales oak/spruce to frozen frames).

## Finding at 04:21 — x-ray on RESCALED structures (tool: _staging/trees231/xray_spruce.py DIR...)
- Dirs: v5 = _garbage/TREES-pre/trees231-v5-spruce ; cone v1 (staged) = _staging/trees231/structures/pw/trees
- in-crown logs / x-ray-visible / bare-ring: v5 mature 419/153/160, old 544/200/200, young 125/0/0;
  cone v1 mature 383/124/139, old 508/167/179, young 89/0/0.
- Bare-ring by depth below tip (cone v1): 0-1: 0 | 2-3: mature 3, old 3 | 4+: mature 136, old 176.
  Per template: mature 3-8, old 6-10.
- => Ruling 3 ("lower more only if necessary, use x-ray"): necessary in only a few templates, and only 1 extra log
  each; it does NOT fix the dark stripe. The stripe = between-tier bare layers (tier step 2, y-radius 0.7).
- QUESTION for Abs0lum (via lead): may I ADD a small leaf collar (ring of 8, or tier ellipsoid y-radius 0.7 -> 1.0)
  on the between-tier layers of mature/old spruce so the trunk is hidden inside the crown? Crown height/shape kept.

## Next steps (unchanged plan, reordered)
1. Rewrite spruce_cone_tip(): cap profile = the crown-top profile continued (slope ~0.3-0.4 radius/layer measured from
   top layers r ~0-1,1-1.4,1-1.4,1-2.2,1.4-2.2), wider/taller than cone v1 (CONE_RISE 3, CONE_R 1.6/2.4/2.8).
2. X-ray-guided extra lowering: while the top trunk log is bare-ring/x-ray visible and above crown_base+1, lower 1 more;
   log per template count (expect ~6 templates, 1 log each).
3. Pending answer: between-tier collar.
4. Regen (regen_trees231.py to a NEW dir, then swap spruce 72), birch/oak 144 must be byte-identical; MD5SUMS; verify;
   render before (cone v1) / after with cone_sheet_trees231.py; VIEW; README; per-template table.

## 04:25 — DONE cap v2 (this slice)
- Code: tools/tree_gen.py — CAP_R0 0.5 / CAP_SLOPE 0.38 / CAP_R {young 2.4, mature 3.2, old 3.5} after CONE_R (~l.224);
  _log_xray_visible() + spruce_cone_tip() v2 (~l.318-375) returns (trunk, cap, extra); spruce() stores info["xray_extra_lowered"].
  Backup before: _garbage/TREES-pre/tree_gen.cone1-before-0421.py. Cone v1 spruce structures: _garbage/TREES-pre/trees231-cone1-spruce/.
- X-ray lowering rule (cap-aware): lower 1 more only if the log just below the cap bottom has a horizontal ray escaping
  (mature/old) -> 13 templates x1 log. First naive rule (top log pre-cap) gave 24 -> rejected as over-lowering.
- Staging swapped (72 spruce), MD5SUMS 216 OK, verify only B2 x72 spruce (expected). birch/oak 144/144 identical.
- X-ray after: mature visible 124->106, old 167->140. Stripe remains = between-tier bare layers (collar AWAITING answer).
- Note: v2 slope (0.38) is narrower than cone v1 (~0.7/layer) in the top 2-3 cap layers, wider/taller below; some old
  templates net -15 leaves vs cone v1. Sheet header text in cone_sheet_trees231.py still says "BEFORE = tree_gen v5"
  (stale label; BEFORE here = cone v1).
- README section "Spruce cap v2" appended. NEXT: his answer on between-tier collar; in-game witness.

## 11:16 — DONE between-tier collar (his 11:12 ruling: YES)
- Code: tree_gen.py DODECA_231["SPRUCE_COLLAR"]=True; spruce(): step==2 -> ring of 8 leaves on each non-tier layer base+1..top-1 (RNG-free), before sink_tip/cap. md5 af76374d. Backup _garbage/TREES-pre/tree_gen.cap2-before-1112.py; cap2 spruce _garbage/TREES-pre/trees231-cap2-spruce/.
- Restaged 72 spruce (young identical), birch/oak 144 identical, MD5SUMS 216 OK, verify only B2 x72.
- X-ray mature 379/106/115 -> 382/45/27 (41 of 45 = forest bare bole, by design); old 499/140/168 -> 508/8/8.
- VIEWED sheets/collar_before_after.png + collar_far_zoom.png: stripe STILL visible from 9 S (cutout needles see-through; 1 ring is not opaque). x-ray overstates hiding. Option next: radius-2 collar (2 layers in front) — needs his call.
