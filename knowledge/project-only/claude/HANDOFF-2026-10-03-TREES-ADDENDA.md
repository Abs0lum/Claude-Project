# HANDOFF ADDENDA — 2026-10-03 — TREES rounds 1 + 2 (BP-02 1.3.208 → 1.3.209, RP-01 1.3.118, TestRunner 0.5.16)

Supplement to `HANDOFF-2026-10-03-V6-CIVITAS.md` / `-DELIVERED.md`. Journal D-C502 + D-C503. All in gofile folder DoHcDxGx (AR-V6-CIVITAS-2026-10-03). Install over V6: BP-02 **1.3.209** (replaces 1.3.207), RP-01 **1.3.118** (replaces 1.3.117), TestRunner **0.5.16** (replaces 0.5.15). Lineup: `/scriptevent pw:test start p23`.

## Round 1 — BP-02 1.3.208 + RP-01 1.3.118 (D-C502)
1. **Roots for acacia / cherry / mangrove** (vanilla-log trunks had no root): `pw:<sp>_root`, a full cube on the vanilla log's textures, same loot/hardness, the template index + rotation states; at the base of all 96 templates; the felling rules know them. BDS 36/36 placements at 4 rotations.
2. **No floating trees**: tree rules placed templates at a random height with an air-permitting allowlist — a census found roots on air and water (in 1.3.207 too). Every template feature is now `grounded` + `unburied` and placed at the heightmap.
3. **Forests are ours**: vanilla's overworld trees come from 17 "legacy" feature rules (engine code behind a JSON rule); all 17 overridden by identifier (vanilla filters, our pools, Java-like densities — ASSUMPTION; 6 mix pools). **Grove and the other 1.18 biomes keep vanilla trees** — engine-internal; three probes (rule override, biome override, tag census) found no JSON handle. Ruling pending: accept / scripted sweep / weight our biomes.
4. **Root sounds** (RP-01 1.3.118): the 20 root blocks had none (stone by default) → wood / cherry wood.
5. **P-4 proven**: removing a block state keeps saved blocks + remaining states (40/40, kept-world probe) — the leaf-state simplification is safe when wanted.

## Round 2 — BP-02 1.3.209 + TestRunner 0.5.16 (D-C503)
- **T4 exact falling set**: a root tree falls by its template (cells rotated about the root by its facing): exactly its logs above the cut + its leaves; the neighbour's wood never; stump = the template's logs below the cut; legacy trees keep the BFS (`PW_TEMPLATE_FELL`). Mock 26/26. Needs his break: p23 t04/t05/t07.
- **T5 TREEGROW on templates**: saplings grow the T2 templates with the root on the sapling cell (old pools pointed nowhere; old placement put the corner on the sapling); clearance by the template's cells; pending saplings survive a reload; tool `/scriptevent pw:treegrow plant x y z [sapling]`. BDS 9/9 species.
- **Lineup p23** (9 steps): fresh forest look · grove note · break a root · survival chop (whole tree, only that tree) · branch/stump cuts never fell · nine saplings planted around you · chop a grown one.

## Tools new (tools/)
tree_roots_square.py · tree_legacy_rules.py · build_testrunner_0516.py · testrunner_src/pw_testrunner_p23.js · package_round_1003b.py / 1003c.py · probes (BDS job-only, never shipped): rootprobe, sprucecensus ×2, ruleprobe ×2, groveprobe, biomeprobe, migprobe A/B, growprobe · bds_civtest.py `--keep-world`.

## Frozen build dirs
bp02-207, bp02-208, bp02-209, rp01-118, rp07-1445, rp08-1414, testrunner-0.5.15, testrunner-0.5.16 (next: 210 / 1.3.119 / 0.5.17).
