# Task V: the Java tree port checked against the real Java game

**Result.** In the main run (Java trees grown at y = 70), no metric of any of the 18 features differs from the port at KS p < 0.01.
Seven flags in that run crossed the >10 % mean rule: fancy_oak ×2, jungle_tree ×2, mangrove ×1, orange_poplar ×2. Each pair is one quantity counted twice (branch_logs = horizontal_logs; for a straight trunk, trunk_top = logs). All of them fall within sampling noise once the port's own expected value is measured with 2000 seeds. Across 18 features × 8 metrics, the largest |z| is 2.29 (dark_oak leaves).
One real behaviour difference was found, but it comes from the **test rig, not the port**: below y = 0, Java's fancy oak grows more branches (`FancyTrunkPlacer.java:70` casts an absolute world Y with `(int)`). The port assumes saplings stand at y ≥ 0, so it matches Java only there (see D1).
Static and sampled evidence only: this is a statistical match of shapes and distributions, not a seed-for-seed match (the port uses Python's RNG).

## Setup
- **Game:** Minecraft Java 26.4-snapshot-2 dedicated server (sha1 e6cac6e2fa35d5847e60dede721ec75f7a28c34d). The chunk files carry DataVersion 5120 (both worlds). The JSON the port reads came from this same snapshot (misode/mcmeta), so the configs match. `orange_poplar` exists here.
- **Java runtime:** Temurin 25.0.1+8 JRE (version JSON javaVersion.majorVersion = 25). Fetched from Adoptium (GitHub release asset), sha256 checked. The system Java 21 is too old.
- **Server:** headless; `eula=true` (Abs0lum approved 2026-09-30 18:14 CT); `online-mode=false`; `spawn-protection=0`; `generate-structures=false`; RCON on 127.0.0.1 only; `-Xmx2G`.
  Gamerules: random ticks 0 (no leaf decay), no mob spawning, no daylight or weather cycle.
  One server session per feature: start, `/forceload` one grid row at a time, `/place feature`, `save-all flush`, `stop`.
  (A first attempt that held every feature in one session ran out of memory before saving; it was discarded.)
- **Grid:** 13 x 13 per feature, 40 blocks apart, /forceload per row, /place feature minecraft:<feature> x y z. 169 placements per feature per run.
- **Two runs:** **y70** (main) uses a custom flat world (bedrock, 130 stone, 2 dirt, grass at y 69; saplings at y 70, like a normal surface). **y-60** uses the default flat world (saplings at y -60).
- **Reading the world:** our own Anvil/NBT reader (`_work/jvalid/mca_reader.py`). It handles DataVersion 5120's new palette form (bare strings / `{"": name}` / `{id, properties}`), and properties are omitted for default states, so a log with no `axis` is `y`.
  Each cell is the box x-19..x+20 by z-19..z+20 around its placement point.
  Logs = `*_log|*_wood`, leaves = `*_leaves`, roots = `mangrove_roots|muddy_mangrove_roots`.
  Decorator blocks (vines, cocoa, bee nests, propagules, moss, podzol, shelf mushrooms, etc.) are counted separately in validation.json and are not compared.
- **Sanity checks:** every chunk read was `minecraft:full`. No tree reached its cell edge or the top of the read sections. No successful placement left an empty cell, and no failed placement left any blocks.
- **Port:** `JT.grow(feature, seed)` with seeds 1..169 (main comparison) and seeds 1..2000 (large-sample check). Imported read-only; not edited.
- **Metrics:** **height** = max y of any log/leaf block + 1 (sapling block = y 0); **trunk_top** = max y of any log + 1; **logs/leaves/roots** = block counts (*_log|*_wood; *_leaves; mangrove_roots|muddy_mangrove_roots); **radius** = max(|dx|,|dz|) over logs, leaves, roots; **branch_logs** = logs whose (x,z) column is not one of the columns holding the lowest log layer; **horizontal_logs** = logs with axis x or z. KS = scipy `ks_2samp` (with integer data, the p-value is approximate). Flag rule = |mean difference| > 10 % of the Java mean, or KS p < 0.01.

## Main comparison: Java y70 vs port seeds 1..169
J = real Java, P = port. Each cell shows mean±sd (min–max).

| Feature | Java grown / failed | Height J · P | Logs J · P | Leaves J · P | Radius J · P | KS p (h / logs / leaves / r) | Roots J · P | Branch logs J · P | Flag |
|---|---|---|---|---|---|---|---|---|---|
| oak | 169 / 0 | 6.0±0.8 (5–7) · 6.0±0.8 (5–7) | 5.0±0.8 (4–6) · 5.0±0.8 (4–6) | 55.0±1.7 (51–59) · 54.9±1.8 (50–60) | 2.0±0.0 (2–2) · 2.0±0.0 (2–2) | 0.79 / 0.79 / 0.99 / 1 | – | 0.0 · 0.0 | – |
| fancy_oak | 169 / 0 | 10.8±3.4 (5–16) · 10.5±3.2 (5–16) | 13.1±8.0 (4–31) · 11.9±7.6 (4–31) | 186.1±107.4 (69–422) · 169.0±104.1 (69–410) | 4.1±1.7 (2–7) · 3.8±1.6 (2–7) | 0.36 / 0.36 / 0.19 / 0.24 | – | 5.6 · 4.6 | branch_logs, horizontal_logs |
| birch | 169 / 0 | 6.9±0.8 (6–8) · 7.0±0.8 (6–8) | 5.9±0.8 (5–7) · 6.0±0.8 (5–7) | 55.0±1.7 (51–59) · 54.9±1.8 (50–60) | 2.0±0.0 (2–2) · 2.0±0.0 (2–2) | 0.97 / 0.97 / 0.79 / 1 | – | 0.0 · 0.0 | – |
| super_birch_bees | 169 / 0 | 10.2±2.2 (6–14) · 9.8±2.2 (6–14) | 9.2±2.2 (5–13) · 8.8±2.2 (5–13) | 55.0±1.7 (51–59) · 54.9±1.7 (50–59) | 2.0±0.0 (2–2) · 2.0±0.0 (2–2) | 0.52 / 0.52 / 0.93 / 1 | – | 0.0 · 0.0 | – |
| spruce | 169 / 0 | 8.6±1.2 (6–11) · 8.4±1.3 (6–11) | 6.6±0.9 (5–8) · 6.5±0.9 (5–8) | 69.2±26.1 (29–123) · 67.7±31.4 (29–167) | 2.3±0.5 (2–3) · 2.3±0.5 (2–3) | 0.79 / 0.52 / 0.79 / 1 | – | 0.0 · 0.0 | – |
| pine | 169 / 0 | 10.1±1.4 (8–12) · 10.1±1.3 (8–12) | 8.1±1.4 (6–10) · 8.1±1.3 (6–10) | 47.8±29.6 (10–90) · 47.9±29.0 (10–90) | 2.1±0.7 (1–3) · 2.2±0.6 (1–3) | 1 / 1 / 1 / 1 | – | 0.0 · 0.0 | – |
| mega_spruce | 169 / 0 | 22.6±4.2 (15–30) · 21.5±4.4 (14–30) | 83.3±17.0 (53–113) · 78.8±17.4 (49–113) | 321.0±37.8 (239–371) · 318.4±38.1 (187–371) | 4.9±0.3 (4–5) · 4.9±0.3 (4–5) | 0.049 / 0.049 / 0.44 / 1 | – | 0.0 · 0.0 | – |
| mega_pine | 169 / 0 | 22.2±4.4 (14–30) · 21.5±4.4 (14–30) | 81.7±17.7 (49–113) · 78.8±17.4 (49–113) | 109.5±37.3 (75–199) · 107.5±37.4 (75–199) | 4.1±0.3 (4–5) · 4.1±0.3 (4–5) | 0.36 / 0.36 / 0.61 / 1 | – | 0.0 · 0.0 | – |
| jungle_tree | 169 / 0 | 8.5±2.6 (5–13) · 9.2±2.4 (5–13) | 7.5±2.6 (4–12) · 8.2±2.4 (4–12) | 54.9±1.6 (51–60) · 54.8±1.8 (50–60) | 2.0±0.0 (2–2) · 2.0±0.0 (2–2) | 0.027 / 0.027 / 0.52 / 1 | – | 0.0 · 0.0 | trunk_top, logs |
| mega_jungle_tree | 169 / 0 | 21.5±5.9 (12–31) · 21.3±5.5 (11–32) | 86.6±26.4 (44–134) · 86.0±24.6 (37–131) | 272.9±36.4 (215–374) · 273.7±34.0 (203–370) | 7.1±0.8 (6–8) · 7.1±0.8 (6–8) | 0.61 / 0.44 / 0.79 / 1 | – | 7.6 · 7.6 | – |
| acacia | 169 / 0 | 7.9±1.1 (6–10) · 7.9±1.1 (6–10) | 8.2±1.5 (5–11) · 8.3±1.6 (5–12) | 75.7±11.6 (57–86) · 73.7±12.4 (57–86) | 4.8±0.7 (4–6) · 4.8±0.7 (4–6) | 1 / 1 / 0.24 / 1 | – | 3.8 · 4.0 | – |
| dark_oak | 169 / 0 | 9.0±1.1 (7–11) · 9.0±1.1 (7–11) | 41.4±6.8 (27–60) · 41.6±7.2 (24–58) | 120.1±6.0 (107–141) · 120.8±6.9 (107–143) | 4.4±0.7 (4–6) · 4.5±0.7 (4–6) | 1 / 0.87 / 0.7 / 1 | – | 14.2 · 14.3 | – |
| pale_oak | 169 / 0 | 8.9±1.1 (7–11) · 9.0±1.1 (7–11) | 41.5±5.7 (26–60) · 41.6±7.2 (24–58) | 120.9±6.6 (107–140) · 120.8±6.9 (107–143) | 4.4±0.7 (4–6) · 4.5±0.7 (4–6) | 1 / 0.11 / 1 / 0.87 | – | 14.3 · 14.3 | – |
| cherry | 169 / 0 | 10.2±0.6 (9–11) · 10.3±0.7 (9–11) | 16.8±4.8 (8–25) · 16.3±4.9 (8–25) | 264.4±86.6 (133–396) · 254.4±86.6 (132–396) | 7.0±0.9 (5–8) · 6.9±0.9 (5–8) | 0.44 / 0.44 / 0.36 / 0.44 | – | 11.4 · 11.0 | – |
| mangrove | 169 / 0 | 8.7±1.9 (5–14) · 8.8±1.9 (5–14) | 7.0±3.7 (2–19) · 6.6±3.1 (2–19) | 127.8±70.2 (31–323) · 117.1±63.4 (35–328) | 4.5±0.9 (2–7) · 4.5±1.0 (2–7) | 0.97 / 0.52 / 0.52 / 0.93 | 19.7 · 19.9 | 2.7 · 2.2 | branch_logs |
| tall_mangrove | 155 / 14 | 16.9±3.6 (9–25) · 16.9±3.4 (10–26) | 18.4±8.4 (4–42) · 18.4±8.0 (4–41) | 324.0±165.8 (35–780) · 324.5±156.8 (31–774) | 6.0±1.1 (3–7) · 6.2±0.9 (4–7) | 0.85 / 0.85 / 0.96 / 0.39 | 34.4 · 34.5 | 9.6 · 9.7 | – |
| azalea_tree | 169 / 0 | 7.0±0.8 (6–8) · 7.0±0.8 (6–8) | 7.5±1.0 (6–9) · 7.5±0.9 (6–9) | 89.0±18.4 (56–128) · 89.2±17.3 (56–125) | 5.0±0.7 (4–6) · 5.0±0.7 (3–6) | 0.99 / 0.97 / 0.79 / 1 | – | 4.0 · 4.0 | – |
| orange_poplar | 169 / 0 | 10.6±1.5 (8–13) · 10.5±1.4 (8–13) | 14.8±4.1 (8–27) · 15.7±4.2 (9–27) | 239.0±109.8 (130–563) · 259.8±116.5 (132–563) | 4.8±0.9 (4–7) · 5.0±1.0 (4–7) | 1 / 0.36 / 0.24 / 0.61 | – | 5.7 · 6.7 | branch_logs, horizontal_logs |

## Placement failures
Java itself refuses some placements. Only tall_mangrove failed: when its roots run out of length, `MangroveRootPlacer` returns false and `TreeFeature.java:111-112` aborts the tree.
The port's retry count (`java_trees.py:500`) shows the same rate: Java 30/338 = 8.9 % (12/169 more in the discarded first attempt, which logged its responses but never saved), port 189/2000 = 9.5 % of seeds.

| Feature | Java failed (y70 run) | Java failed (y-60 run) | Port seeds needing a retry (of 169 / of 2000) |
|---|---|---|---|
| oak | 0/169 | 0/169 | 0 / 0 |
| fancy_oak | 0/169 | 0/169 | 0 / 0 |
| birch | 0/169 | 0/169 | 0 / 0 |
| super_birch_bees | 0/169 | 0/169 | 0 / 0 |
| spruce | 0/169 | 0/169 | 0 / 0 |
| pine | 0/169 | 0/169 | 0 / 0 |
| mega_spruce | 0/169 | 0/169 | 0 / 0 |
| mega_pine | 0/169 | 0/169 | 0 / 0 |
| jungle_tree | 0/169 | 0/169 | 0 / 0 |
| mega_jungle_tree | 0/169 | 0/169 | 0 / 0 |
| acacia | 0/169 | 0/169 | 0 / 0 |
| dark_oak | 0/169 | 0/169 | 0 / 0 |
| pale_oak | 0/169 | 0/169 | 0 / 0 |
| cherry | 0/169 | 0/169 | 0 / 0 |
| mangrove | 0/169 | 0/169 | 0 / 0 |
| tall_mangrove | 14/169 | 16/169 | 16 / 189 |
| azalea_tree | 0/169 | 0/169 | 0 / 0 |
| orange_poplar | 0/169 | 0/169 | 0 / 0 |

## Every flag, and what caused it
| Run | Feature | Metric | Java mean | Port mean | Rule tripped | Tests |
|---|---|---|---|---|---|---|
| hi | fancy_oak | branch_logs | 5.56 | 4.64 | mean -16.4 % | KS D 0.101, p 0.36; Welch p 0.13 |
| hi | fancy_oak | horizontal_logs | 5.56 | 4.64 | mean -16.4 % | KS D 0.101, p 0.36; Welch p 0.13 |
| hi | jungle_tree | trunk_top | 7.48 | 8.24 | mean +10.1 % | KS D 0.160, p 0.027; Welch p 0.006 |
| hi | jungle_tree | logs | 7.48 | 8.24 | mean +10.1 % | KS D 0.160, p 0.027; Welch p 0.006 |
| hi | mangrove | branch_logs | 2.69 | 2.21 | mean -17.8 % | KS D 0.089, p 0.52; Welch p 0.062 |
| hi | orange_poplar | branch_logs | 5.72 | 6.65 | mean +16.2 % | KS D 0.101, p 0.36; Welch p 0.032 |
| hi | orange_poplar | horizontal_logs | 5.72 | 6.65 | mean +16.2 % | KS D 0.101, p 0.36; Welch p 0.032 |
| lo | fancy_oak | logs | 13.70 | 11.90 | mean -13.1 % | KS D 0.142, p 0.066; Welch p 0.05 |
| lo | fancy_oak | leaves | 201.78 | 168.96 | mean -16.3 %, KS p 0.00961 | KS D 0.178, p 0.0096; Welch p 0.0081 |
| lo | fancy_oak | branch_logs | 6.45 | 4.64 | mean -28.0 % | KS D 0.172, p 0.014; Welch p 0.0057 |
| lo | fancy_oak | horizontal_logs | 6.45 | 4.64 | mean -28.0 % | KS D 0.172, p 0.014; Welch p 0.0057 |
| lo | pine | leaves | 43.23 | 47.87 | mean +10.7 % | KS D 0.065, p 0.87; Welch p 0.14 |
| lo | mangrove | leaves | 133.37 | 117.06 | mean -12.2 % | KS D 0.160, p 0.027; Welch p 0.029 |
| lo | mangrove | branch_logs | 2.84 | 2.21 | mean -22.3 % | KS D 0.130, p 0.11; Welch p 0.014 |
| lo | orange_poplar | leaves | 232.48 | 259.78 | mean +11.7 % | KS D 0.118, p 0.19; Welch p 0.018 |
| lo | orange_poplar | branch_logs | 5.66 | 6.65 | mean +17.6 % | KS D 0.124, p 0.15; Welch p 0.018 |
| lo | orange_poplar | horizontal_logs | 5.66 | 6.65 | mean +17.6 % | KS D 0.124, p 0.15; Welch p 0.018 |

### D1: fancy_oak, y-60 run (more logs, leaves and branches in Java): a test-rig artefact of negative Y. Java is right, and the port does not model that case.
- **Java:** `FancyTrunkPlacer.java:69-70`. `branchHeight = checkStart.getY() - dist*0.381` uses the *absolute* world Y, then `int branchTop = ... (int)branchHeight`.
  `(int)` truncates toward zero, so below y = 0 it rounds **up**: at y -58.381 it gives -58, where floor would give -59.
  The branch base therefore sits one block higher. That base must pass `trimBranches` (`localY >= height*0.2`, `FancyTrunkPlacer.java:154-156` and `:85`), so more branches survive, and each kept branch adds a foliage cluster.
- **Port:** `java_trees.py:167-168` does the same sum in *local* coordinates (sapling at y 0, so always ≥ 0). There `int()` equals floor, which matches Java only when the absolute Y is ≥ 0.
- **Evidence:** at height 8, the port (and Java at y 70) can never keep a branch: 0 of 346 port trees, 0 of 11 Java-y70 trees. Java at y -60 kept one in 16 of 17 height-8 trees (1.5 branch logs on average).
  Dumped tree cell (10,0) shows a horizontal limb at local y 2 from base (0,2,0), which only the round-up allows. Moving the rig to y 70 removed the effect (Java branch logs 6.45 → 5.56; port 4.68).
- **Meaning for us:** for surface trees (y > 0) the port is right. A fancy oak grown below y 0 in Java (e.g. bonemeal in a deep cave) has extra branches that the port will not make. Shown as a limitation, not a bug.

### D2: fancy_oak, y70 run (branch_logs / horizontal_logs −16.4 %): within noise; a ~1.5 % remainder is unexplained.
- Against the port's 2000-seed mean, Java's y70 sample gives z +1.73 (logs), +1.80 (leaves), +1.83 (branch logs).
- Most of the raw gap comes from Java's own height draw. Height should be uniform over 5..16 (`TrunkPlacer.java:59-60`, base 3 + nextInt(12)), but this sample's χ² test against uniform gives p = 0.033, skewed toward the branch-rich tall trees.
- Comparing within each height leaves only logs +0.20 (z 1.81), leaves +2.1 (z 1.11) and radius +0.08 (z 2.14). That is 1–2 % and not significant.
- The per-height table matches structurally: 0 branches at heights 5–8 on both sides, and every tree of height ≥ 10 has branches on both.
- Tested and ruled out: Java's float32 maths in `makeLimb` / `treeShape` (`FancyTrunkPlacer.java:107-112, 176-190`). A float32 copy of the port's `limb`/`fancy_shape` (`java_trees.py:178-191, 272-278`), monkeypatched in `_work/jvalid/float32_probe.py`, gave 4000/4000 identical trees.
- Code compared line by line (`FancyTrunkPlacer.java:44-91` vs `java_trees.py:153-176`): no difference found.

### D3: mangrove (y70 branch_logs −17.8 %; y-60 leaves −12.2 %, branch_logs −22.3 %): sampling noise.
- Pooled Java (338 trees) vs port (2000 seeds): branch logs 2.76 vs 2.56 (z +1.40, KS p 0.75); leaves 130.6 vs 129.0 (z +0.39, KS p 0.86).
- An independent simulation of the rules alone (`UpwardsBranchingTrunkPlacer.java:76-135`) gives E[branch logs] = 2.53 and E[logs] = 7.03. In the y-60 run, each 169-tree sample landed about 1.7 SE from that, on opposite sides (Java 2.84, port 2.21).
- Code compared: `UpwardsBranchingTrunkPlacer.java:76-135` vs `java_trees.py:221-241`; `RandomSpreadFoliagePlacer.java:54-62` vs `java_trees.py:396-400`. They match.

### D4: orange_poplar (branch_logs / horizontal_logs +16.2 % y70, +17.6 % y-60; leaves +11.7 % y-60): sampling noise.
- Pooled Java (338) vs port (2000): branch logs 5.69 vs 5.99 (z −1.38, KS p 0.31); leaves 235.8 vs 245.7 (z −1.66, KS p 0.10).
- These metrics hinge on the rare wide crowns (weighted radius 5:5:1:1; only crown radius ≥ 6 makes spoke logs). The crown-radius distribution matches: Java 0.43/0.42/0.08/0.07 vs port 0.41/0.41/0.09/0.09 for r 4/5/6/7, χ² p 0.65.
- Code compared: `PoplarTrunkPlacer.java:57-72` vs `java_trees.py:262-269`; `PoplarFoliagePlacer.java:59-84, 102-123, 185-194, 210-233` vs `java_trees.py:407-437`. They match, including the spoke rule (a leaf becomes a log only where the cell still holds this tree's leaf: Java `tryPlaceLog`, `:128-139`; port `:436-437`).

### D5: jungle_tree, y70 run (trunk_top / logs +10.1 %): sampling noise in the Java sample.
- The two Java runs disagree with each other more than with the port: y70 mean 7.5, y-60 mean 8.2, port 8.2 (KS between the Java runs p 0.11).
- Pooled Java 7.82 vs port 7.97 (z −0.97, KS p 0.72). The rule is `StraightTrunkPlacer.java:38-39` + `TrunkPlacer.java:59-60` vs `java_trees.py:84-85, 97-99`.

### D6: pine, y-60 run (leaves +10.7 %): sampling noise.
- KS p 0.87 (the >10 % rule fired on a high-variance metric). Pooled Java 45.5 vs port 46.2 (z −0.40, KS p 1.0).

## Large-sample check (every metric, not only flagged ones)
Java is pooled over both runs, except fancy_oak (y70 only, because of D1). The port uses seeds 1..2000.
The table shows each feature's worst metric, the Java-vs-Java noise floor, and a per-layer leaf-count test.

| Feature | Java trees pooled | Worst metric | Java mean | Port mean (2000) | z | KS p | Java y-60 vs y70: min KS p | Leaf layers: max abs z (base / top-aligned) |
|---|---|---|---|---|---|---|---|---|
| oak | 338 (hi+lo) | height | 6.04 | 5.96 | +1.53 | 0.22 | 1 (leaves) | 2.22 / 0.66 |
| fancy_oak | 169 (hi) | radius | 4.14 | 3.84 | +2.21 | 0.27 | 0.29 (branch_logs) | 2.83 / 2.16 |
| birch | 338 (hi+lo) | height | 6.93 | 6.96 | -0.59 | 1 | 0.61 (leaves) | 0.71 / 0.36 |
| super_birch_bees | 338 (hi+lo) | height | 10.16 | 9.97 | +1.49 | 0.35 | 0.87 (leaves) | 1.88 / 1.07 |
| spruce | 338 (hi+lo) | leaves | 68.17 | 65.53 | +1.67 | 0.17 | 0.61 (leaves) | 4.80 / 4.46 |
| pine | 338 (hi+lo) | height | 10.10 | 9.95 | +1.93 | 0.28 | 0.87 (leaves) | 1.65 / 0.81 |
| mega_spruce | 338 (hi+lo) | leaves | 318.86 | 316.66 | +0.97 | 0.99 | 0.11 (leaves) | 1.50 / 1.31 |
| mega_pine | 338 (hi+lo) | radius | 4.08 | 4.10 | -1.42 | 1 | 0.87 (height) | 1.62 / 0.75 |
| jungle_tree | 338 (hi+lo) | height | 8.82 | 8.97 | -0.97 | 0.72 | 0.11 (height) | 1.66 / 0.77 |
| mega_jungle_tree | 338 (hi+lo) | height | 21.80 | 21.62 | +0.51 | 0.7 | 0.36 (height) | 2.37 / 1.73 |
| acacia | 338 (hi+lo) | branch_logs | 3.75 | 3.90 | -1.72 | 0.18 | 0.61 (height) | 1.60 / 1.49 |
| dark_oak | 338 (hi+lo) | leaves | 120.03 | 120.86 | -2.29 | 0.11 | 0.36 (branch_logs) | 1.59 / 1.68 |
| pale_oak | 338 (hi+lo) | height | 8.91 | 9.00 | -1.27 | 0.46 | 0.087 (logs) | 0.76 / 1.86 |
| cherry | 338 (hi+lo) | horizontal_logs | 6.22 | 5.92 | +2.17 | 0.043 | 0.79 (height) | 3.27 / 2.31 |
| mangrove | 338 (hi+lo) | height | 8.70 | 8.89 | -1.66 | 0.3 | 0.7 (leaves) | 2.09 / 1.96 |
| tall_mangrove | 308 (hi+lo) | radius | 6.03 | 6.14 | -1.81 | 0.81 | 0.54 (branch_logs) | 2.37 / 1.86 |
| azalea_tree | 338 (hi+lo) | radius | 4.95 | 4.98 | -0.79 | 1 | 0.52 (branch_logs) | 1.55 / 1.50 |
| orange_poplar | 338 (hi+lo) | leaves | 235.75 | 245.74 | -1.66 | 0.1 | 0.52 (trunk_top) | 2.41 / 1.91 |

- **Only per-layer outlier:** spruce's deepest leaf layer (10 below the top / y 10): Java 0.2 vs port 0.8 leaves per tree (z −4.5 / −4.8).
  That layer exists only for trunk 8 + offset 2 + foliage height 7 (about 1 tree in 36), so it rests on **5 Java trees**. The z-test is unreliable on such zero-heavy data.
  Each of the 5 Java trees has a row-by-row radius sequence the port also produces (e.g. Java cell y70 (1,4) = port seed 10 exactly).
  The port's larger mean comes from the 44-leaf radius-3 bottom row (start radius 1 with leaf radius 3, a 1-in-4 case), which none of the 5 Java trees drew: (3/4)^5 = 0.24.
  Code compared: `SpruceFoliagePlacer.java:41-56, 60` vs `java_trees.py:291, 362-367`; they match. Verdict: noise, not logic.
- Other layer tests: max |z| ≤ 3.27 (cherry y 5). With about 500 layer tests (layers × 2 alignments), that is within the normal range.

## Not covered (stated plainly)
- **MegaPine parity:** `MegaPineFoliagePlacer.java:49` uses absolute-Y parity `(yy & 1)`, while the port (`java_trees.py:378`) uses local yy. Both runs had even sapling Y (-60, 70), so the port is only shown to match for **even** ground heights. On odd Y, Java's jagged rows fall on the other layers.
- **Decorators** (vines, cocoa, bee nests, propagules, moss, pale moss, podzol, rooted dirt, shelf mushrooms) are not in the port and were not compared. Their counts are in validation.json.
- **Soil block** (`placeBelowTrunkBlock`) is not compared.
- **Leaf identity** is compared only as a mix of leaf types: azalea is 75.1 % plain / 24.9 % flowering in Java vs 74.8 / 25.2 in the port; every other feature uses one leaf type on both sides (`leaf_types_total`). Leaf `distance`/`persistent` states are not compared.
- **Ground:** grass on a flat plains world only. Mud, water and slopes were not tested (mangrove grew 169/169 on grass, so no mud patch was needed).

## Files
- `VALID-<FEATURE>.png` (18 sheets): the first 6 Java trees (y70 grid cells) vs port seeds 1–6, full and leaves-hidden, one scale per sheet.
- `validation.json`: per-tree metrics for both Java runs and port seeds 1..169; per-feature comparisons, large-sample checks, Java-vs-Java checks and leaf-layer tests.
- Working files (`/home/claude/_work/jvalid/`): `place_all.py` / `place_hi.py` (RCON placement), `placements*.json` (every /place response), `mca_reader.py`, `compare.py`, `compare2.py`, `extra_checks.py`, `layer_check.py`, `float32_probe.py`, `render_sheets.py`, `write_md.py`; both worlds are under `server/` (`world` = y-60, `world_hi` = y70).
