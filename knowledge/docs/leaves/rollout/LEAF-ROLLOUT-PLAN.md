# LEAF ROLLOUT PLAN — the pilot leaves into the main packs (D-C343, 2026-09-30)

Status: **PLAN — waiting for Abs0lum's GO.** Nothing is built.
Basis: p15 27/27 PASS (D-C340); L-FAR-1 (D-C342); the leaf usage map `LEAF-USAGE-MAP.md` (constraints #1–#19 cited below as C1…C19).

## 1. The design in one paragraph
Keep today's nine block ids (`pw:<species>_leaves`) and today's five states, so worldgen features (C1–C3), felling (C9), decay (C12), loot (C15) and saved worlds (C17) keep working unchanged. Swap only what each `pw:variant` value LOOKS like: the seven variants become the pilot shapes (C-WH80). **v0, the one worldgen always places (his ruling + C1), becomes a real full leaf shape** instead of the old far cube, with `alpha_test_to_opaque`, so a freshly generated tree already looks right and the game itself turns it solid far away (L-FAR-1). The scanner stops re-rolling: it assigns each leaf's variant ONCE, from the leaf's position and its distance to the wood (the pilot rule), so the same leaf always gets the same look, even after a reload. The far reverter and re-applicator are removed (the game does the far swap).

## 2. Variant mapping (per species)
| `pw:variant` | today | new (pilot) | render method |
|---|---|---|---|
| 0 (worldgen default) | far cube, opaque | FULL shape A | alpha_test_to_opaque |
| 1 | v1 | FULL shape B (turned 90°) | alpha_test_to_opaque |
| 2 | v2 | FULL shape C (180°) | alpha_test_to_opaque |
| 3 | v3 | FULL shape D (270°) | alpha_test_to_opaque |
| 4 | v4 | FULL shape E | alpha_test_to_opaque |
| 5 | v5 | CARDS-ONLY A (touching wood) | alpha_test_to_opaque |
| 6 | v6 | CARDS-ONLY B | alpha_test_to_opaque |
Spruce: no cards-only (as in Java) → v5/v6 become full shapes too. Cherry, pale oak: untinted art.
Pilot had 6 full + 2 cards (pv 1–8); 7 slots → 5 full + 2 cards.

## 3. BP-02 1.3.196 (script + blocks)
- Blocks (9 files): same id, same states (C17: no save migration). Permutations v0–v6 → pilot geometry + materials (`*` face tile, `extra` card tile, `top` for spruce), `ambient_occlusion` false, `face_dimming` false, per-variant `minecraft:transformation` quarter turn, `tint_method` per his colour choice (Q1), `isotropic` on (his 18:14 "leave it on"). KEEP: loot, flammable 30/60, `tag:plant`, destroy time, map_color, `pw:randomize_variant` (C15).
- Scanner (main.js): `pickVariantForBlock` for leaves → position hash + distance-to-wood rule (touching wood → cards, 2..band → coin flip by position, farther → full); no `Math.random` (C5). Distance from Process A's trunk association (it already starts from logs, C4 §3.4). Classify-once kept (section_rolled flag). Far reverter + re-applicator + `_appliedRegistry` removed (C8). `endsWith("_leaves")` checks unaffected (ids unchanged, C10). Felling's `ft:leaf_variant` 0–6 unchanged (C9, C10).
- Azalea / flowering azalea: vanilla today (not in BP-02) — Q2.

## 4. RP-01 1.3.105 (render)
- Replace the leaf geometry files (C13) with the pilot geometries; replace the 180 leaf terrain keys with the pilot tiles (128 px, `_n` + MERS texture sets for every species incl. oak); blocks.json sound "grass" kept.
- Falling-tree entity + `pw_leaf_fall` particle (C14): repoint to the new face tiles.
- Flipbooks (C13): the pilot tiles are static — today's 8-frame animation stops (Q4; wind flipbooks later, D-C329).

## 5. Test (TestRunner p16, in a COPY of the test world, PS5 VV)
worldgen trees in fresh chunks (v0 everywhere before the scanner reaches them) · the same trees after the scanner (cards by the wood, no re-roll after a relog) · far swap + shadows at noon · felling (canopy colour) · decay · placing / breaking leaves by hand (loot, sapling drops) · iso re-check · performance in a forest · D probe: `/place feature` refusal text for pw: and minecraft: trees.

## 6. Questions (in the chat message)
Q1 pre-coloured or biome-tinted per species · Q2 azalea / flowering azalea: new pw ids + our azalea tree, or leave vanilla · Q3 GO on this design (v0 = real leaf, assign once by position, no far scanner) · Q4 static leaves until the wind work.
