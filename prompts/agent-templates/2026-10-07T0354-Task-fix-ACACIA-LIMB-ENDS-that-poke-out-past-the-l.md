Task: fix ACACIA LIMB ENDS that poke out past the leaf plates in our tree templates (AbsolutRealism BP-02). Known finding (/home/claude/_docs/program228/TREE-TRUNK-PLAN.md §8): "255 log cells across the 32 acacias are visible from the sky (secondary limbs reach pr x 0.5-0.9 from the limb tip while the plate is centred at 0.7 x tip — they run past the plate edge). Pre-existing." The owner wants it fixed now.

READ: /home/claude/_docs/program228/TREE-TRUNK-PLAN.md (whole — the tree pipeline: tools/tree_gen.py, tools/tree_gen_square.py, tools/tree_rescale.py, tools/regen_trees_228.py, tools/install_trees_228.py, the before/after sheet format, the RP-01 falling-tree carbon copies via tools/ft_tpl_gen_lite.py), /home/claude/_docs/program228/TREE-APPLIED-NOTES.md, and the acacia code in tools/tree_gen.py. Templates: /home/claude/_build/bp02-229/structures/pw/trees/ (read-only for you); mcstructure I/O: tools/mcstructure.py.

DO (work only in a NEW folder /home/claude/_staging/acacia_230/ and in COPIES of tools you change, e.g. tools/tree_gen_acacia230.py — never edit existing tools or anything in _build/_bds):
1. Find the exact mechanism (code placing secondary limbs and plates; numbers).
2. Change the generator copy so every acacia limb ends INSIDE its leaf plate (tip at least 1 cell inside the rim, covered from above), keeping the acacia silhouette (flat plates, forked trunk).
3. Regenerate ONLY the acacia templates into /home/claude/_staging/acacia_230/trees/ with the same names, through the pipeline's rescale step.
4. Measure before vs after: log cells visible from the sky (top-down to first non-air) per template and total; leaf counts; trunk unchanged.
5. Before/after sheets /home/claude/_docs/program228/ACACIA-LIMBS-BEFORE-AFTER-*.png in the TREE-TRUNK sheet style; view them (Read tool) and confirm by eye.
6. /home/claude/_staging/acacia_230/README.md: mechanism, change, numbers, exact commands to install the templates into a BP-02 build and regenerate the RP-01 falling-tree copies for acacia (do not run the install).
Return: mechanism in 3 lines, before/after visible-log totals, install commands.