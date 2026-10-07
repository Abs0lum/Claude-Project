# How Patrix (Java) builds its leaves, and what Bedrock can copy — study, 2026-09-30

Read-only study (LEAF PROTOCOL). No pack was changed. Source: the Patrix 1.21.11 128x basic zip on Drive (`1NCU1Co22xCPTG3Zn5uU6ZnC7abdswSpD`), range-read into `_intake/patrix128/leaf_pull/`. Tool: `tools/java_leaf_study.py`. Renders: `JAVA-LEAF-ONE-BLOCK.png`, `JAVA-LEAF-TREE.png`. Numbers: `STUDY-NUMBERS.json`. Journal: D-C323.

## 1. What Patrix does (oak)

| Piece | What it is | Source |
|---|---|---|
| Airy cube | A 16×16×16 cube with 5 faces (no bottom face). Each face shows a painted sprig; only 25–31 % of its pixels are drawn. | `models/block/leaves_extra1.json`, oak face tiles |
| Crossed cards | 3 flat, zero-thickness cards (26×28 px) cut diagonally through the block at 45°. They reach 4–6 px past the block's edges, so the canopy outline is ragged, not square. Only 11–13 % of a card's pixels are drawn. | same model, `#extra` texture |
| Thinning beside the wood | Uses vanilla's leaf `distance` (steps to the nearest log). Touching a log: cards only. 2–3 steps away: a coin flip between cards only and cube + cards. Farther away (or player-placed): cube + cards. The canopy is dense on the outside and hollow around the wood, so the tree's own logs show as its branches. | `blockstates/oak_leaves.json` (multipart), `leaves_extra3.json` |
| Randomness | Every block gets a random quarter-turn, a random face tile (6 choices) and a random card tile (4 choices). | blockstate `y` rotations; OptiFine CTM `method=random` |
| Light and colour | No side shading (`shade:false`), no ambient occlusion. The art is grey and the game multiplies it by the biome's foliage colour. LabPBR `_n` / `_s` maps are there for shaders. | model flags, `tintindex 0` |

Spruce differs: its cube has only east, west and top faces, it has 4 cards, and it has no distance rule. The side and top tiles are random separately.

The textures have no semi-transparent pixels. Every pixel is fully drawn or fully empty, so `alpha_test` is the correct method and `blend` is not needed.

## 2. Bedrock feasibility

| Patrix piece | Bedrock equivalent | Status |
|---|---|---|
| Cube with no bottom face | Per-face UVs with the `down` entry left out | ✓ direct |
| Zero-thickness cards | Size-0 cubes with ONE face each (single-face quad law; `alpha_test` draws both sides) | ✓ |
| Cards reaching past the block | Oversized geometry: the full model is 28 × 26 × 23.8 px, inside the 30×30×30 limit (Microsoft Learn, 2025-06-10) | ✓ measured |
| Two textures (face tile, card tile) | Custom material instance `extra` bound per face (Lesson #157) | ✓ |
| `shade:false`, no AO | `face_dimming: false`, `ambient_occlusion` off | ✓ |
| Biome-tinted grey art | `tint_method`: `default_foliage` / `birch_foliage` / `evergreen_foliage` (format 1.21.80+) | ✓ (FOUNDATION §5.4 open path) |
| Random quarter-turn | Bake the turns into the variant geometries, or `isotropic` UVs (1.21.80+) | ✓ |
| Random tile per FACE | Not portable: `terrain_texture` variations do not reach `material_instances` (L-VAR-1). Variety comes per variant only. | ≈ |
| Vanilla `distance` | Our classifier already reads each leaf's 6 neighbours once, so "touching wood" costs no extra reads. Distance 2–3 needs more reads, so it would be approximated. | ≈ |
| Full render distance | `alpha_test` is a near block, so it is drawn to half the render distance. The v0 far cube and the scanner stay (his 12:22 ruling). | unchanged |

Geometry cost: 8 quads per leaf block (4 for cards only), against 48–96 for our current variants (v1 84, v4/v5 96). Cost to measure in a pilot: alpha-test overdraw from large cards that are 88 % empty, mainly on mobile.

## 3. Shadows (his condition)

Our record (FOUNDATION §5.1/§5.2, HISTORY v1.1.3) says:
- plain `alpha_test` lets sunlight through the see-through pixels (dappled light);
- `alpha_test_to_opaque` cast solid cube shadows under Vibrant Visuals;
- `blend` casts no shadows.

The Microsoft docs say nothing about Vibrant Visuals shadows per render method. His witness decides.

## 4. Lesson conflict flagged (§7, not evaluated)

L9 / HISTORY II.7 says custom blocks have no near/far render swap. Three sources say otherwise:
- 1.21.100 changelog: "'alpha_test_to_opaque', 'alpha_test_single_sided_to_opaque', and 'blend_to_opaque' will now shift to 'opaque' in the distance again"
- Bedrock Wiki (block visuals): `alpha_test` before half render distance, `opaque` after
- Microsoft Learn `material_instances`: "turn only opaque on the far render"

Known cost from v1.1.3: solid shadows. The evaluation is parked with the render-distance work unless he asks for it now.
