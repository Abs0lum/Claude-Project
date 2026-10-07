# TEXTURE VARIANT REDUCTION + 128 px — census and proposal (2026-10-07)

**Status: research only. No pack, build, tool or source file was changed.** Data: `TEXTURE-VARIANT-REDUCTION-2026-10-07.json`
(beside this file). Scripts that produced every number: `_docs/research/tvr_src/` (run order: `bpstates.py`, `tvr_census.py`,
`tvr_group2.py`, `tvr_plan.py`, `tvr_tables.py`; they read and write their json in their own folder).

**His ask (00:23 CT 10-07):** *"grass, dirt, sand stay high; everything else 6–16 variants; count the savings; list what can drop
to 128x (incl. MERS and normals)."* Plus the lead's add-on: count the block permutations each change removes (PS5 join crash
CE-108255-1 investigation; Microsoft's 65,536-per-world figure).

---

## 0. Headline numbers

1. **Almost nothing is above 16 today.** Of 303 multi-image families in the stack, the only ones above 16 are the ones his rule
   keeps high: `pw_sand` 24, `pw_red_sand` 24, `grass_block_top` 17. Every other family is already at 16 or below. So "6–16" in
   practice means choosing where inside 6–16 each family should sit.
2. **Recommended variant cut:** 60 families change, **191 images dropped, 15.72 MB saved** (colour + normal + MERS), **3.20 Mpx
   of terrain atlas** freed (colour tiles; the PBR layers free another 6.03 Mpx of layer pixels). Per pack: RP-04 11.07 MB,
   RP-05 2.41 MB, RP-01 1.13 MB, RP-10 1.10 MB (table T1).
3. **128 px is the bigger lever:** 463 used textures above 128 px can drop with their MERS + normal maps: **104.7 MB and
   19.7 Mpx of atlas.** Almost all of it is in three places: RP-13's 248 ramp cut-out fills at 256 px (48.1 MB, 12.2 Mpx),
   RP-01's vine wind strips (35.7 MB), RP-11's ores at 256 px (9.2 MB, 3.5 Mpx) (tables T4, T5).
4. **⚠ ATLAS ALARM (new finding).** The block textures his current stack actually uses add up to **70.0 Mpx** by the same
   method `tools/atlas_budget.py` used on 10-02 (it measured 60.8 then), or **74.8 Mpx** when blocks.json is merged field by field
   (§1.3). The terrain atlas is one 8192² sheet = **67.1 Mpx**. RP-13 1.0.0 (10-06) brought **21.7 Mpx**, 16.25 of it in the
   248 fill cut-outs at 256 px. By the Atlas Budget Law the engine then silently halves every block texture.
   **This is a static estimate (P1), not a witnessed fact.** Witness question for him: since RP-13 went in, has the world
   shown the frame-wide soft "16-px look" that comes and goes? Dropping only the RP-13 fills to 128 brings the total back to
   ~57.8 Mpx (62.6 field-merged).
5. **Permutations: the texture cut itself removes almost none** (256, only where a lattice state shrinks). The real permutation
   levers sit beside it (table T6):
   - **2,745 permutations are dead `pw:gvar` values on 31 slab blocks** — the only code that sets them (the slab smoother,
     BP-02 `scripts/main.js` 4873–4929) never reaches them, and the 16 terracotta slabs draw one texture whatever gvar is.
     Removing them changes nothing on screen.
   - Ramps: BP-02 1.3.230 SLIM removes 19,320 (matches the handoff's 55,891 → 36,571 exactly); keeping ramps but going 8 → 6
     variants on the 3 base stones removes 1,680.
   - **Do not raise the 4-variant ramps to the 6 floor:** that would ADD 8,960 permutations.

---

## 1. Method and scope

### 1.1 Stack censused (top first; current builds in `_build`, read-only)
Markers RP 0.2.3 · **RP-13 1.0.1** · RP-12 1.0.1 · RP-11 1.3.40 · RP-10 1.3.51 · RP-08 1.4.14 · RP-07 1.4.45 · RP-06 1.4.29 ·
RP-05 1.3.59 · **RP-04 1.3.159** · RP-03 1.3.67 · RP-02 2.0.7 · **RP-01 1.3.125** · vanilla (bedrock-samples 1.26.50.4).
- **ASSUMPTION:** his world file of 09-22 is the newest order on disk; RP-13 was placed directly above RP-04 and the latest
  build of every other RP was used. A different order only changes which pack "holds" a duplicated path, not the totals.

### 1.2 What a "family" is
- Every terrain key in every pack → its image paths → the top pack that holds each image → that pack's texture set → the
  normal / heightmap and MERS layers. Bytes = colour + layers + the set json.
- Images are grouped by **file stem** (the folder is kept; a trailing `_vN`, `_N` or `_gN` is removed). So `stone`, `stone_1`,
  `stone_v1` … are one family; `bark/oak_log_v*` (RP-01, the pw: trees) and `oak_log_v*` (RP-04) are two.
- Atlas cost = one square tile per image at its real size (a flipbook strip counts one frame) — the `atlas_budget.py` rule.

### 1.3 "Used" (and one correction to the old tool)
- A key is used if a block names it: the effective `blocks.json` (vanilla base, then every pack bottom → top), BP-02 1.3.229
  material instances (components and permutations), Markers BP 0.2.4.
- **Correction found during the census (P11):** `tools/block_pbr_census.used_keys` keeps only the TOP pack's blocks.json entry.
  RP-04 overrides e.g. `minecraft:orange_terracotta` with `{sound, isotropic}` only, so the old tool counted every terracotta
  (and similar blocks) as unused. This census merges entries field by field. Microsoft's docs found today do not state the
  blocks.json merge rule (PACK-SPLIT doc §2), so both atlas numbers are given.
- The census does not see engine-chosen state textures that no blocks.json names (lit candles, crop stages, copper bulbs…);
  those families are FUNCTIONAL here and never cut.

### 1.4 Premise audit (P11) — excluded spaces
| Space | Status |
|---|---|
| RP-02, RP-06, RP-07, RP-12 terrain textures | CENSUSED — none of them has a `terrain_texture.json` |
| RP-08 (28 keys, single images) | CENSUSED — no multi-image family |
| RP-03 (3 keys) | CENSUSED — 1 image counted (the rest of RP-03 is entity / PBR layers) |
| Entity / item / particle textures | EXCLUSION-VERIFIED — not on the terrain atlas; not part of the ask |
| Staged, not installed (skyway 7 keys, acacia limbs) | EXCLUDED on purpose — not in his world yet (skyway adds 0.11 Mpx) |

---

## 2. The rules used to pick each number

1. **Grass, dirt, sand: unchanged** (his rule). Families: `grass_block_top` 17, `grass_block_side` 16, `dirt` 16,
   `coarse_dirt` 16, `pw_sand` 24, `pw_red_sand` 24 (+ their 128 px status quo).
2. **Never add variants.** 72 used families already sit at 6 or fewer; they stay (raising them would cost bytes and, for ramps,
   permutations).
3. **The lattice floor is 8 for any family that has a `pw:` slab.** The ground and slab variants are placed by
   `index = (x + 2z) mod n`, slabs with `+ 4` (main.js 4882–4891). Checked in Python for n = 2…24: a block never matches any of
   its 8 neighbours for n ≥ 4, but **a slab never matches the block below it or its neighbours only for n ≥ 8** (n = 4…7 always
   leave a repeat; n = 6 fails at K + 2 = 6). So stone-type families with pw: slabs stay at 8.
4. **Not variant sets — never cut:**
   - plank grids (`pw_planks/<wood>` 16 tiles = one 4 × 4 continuous plank pattern placed by `pw:gx/gy/gz`);
   - the ramp faces (`pw_rampv4_*`, `pw_deck*_*`) — they follow the ramps' `pw:var` state, which the PS5 SLIM test decides;
   - growth stages, lit/unlit states, animations, the Markers digits.
5. **Per class inside 6–16** (the "why" column of T2 says which applied):
   - **12** — biome-floor covers seen in wide flat expanses like grass: podzol, mycelium, crimson / warped nylium.
   - **8** — patchy ground (gravel, mud, packed mud, muddy mangrove roots), natural stone in big exposures (stone,
     deepslate, andesite, granite, calcite, terracottas, netherrack, end stone, dripstone, cobblestone, snow), and pw: tree
     bark (each tree block draws 5 side variants, `pw:variant` 5).
   - **7** — log ends (`pw:top_variant` 7).
   - **6** — crafted / building materials (bricks, polished, quartz, smooth, sandstone tops, bamboo block, mud bricks) and
     small sprites (flowers, ferns, cave vines, hanging roots, mushroom stem).
6. Which images to drop inside a family is a build-time choice (keep the most different ones); this census assumes average
   bytes per image.

---

## 3. Tables

### T1. Variant cut — totals per pack (recommended picks)

| Pack | Images dropped | Bytes saved (colour + normal + MERS + set) | Colour atlas saved |
|---|---:|---:|---:|
| RP-04 1.3.159 | 125 | 11.07 MB | 2.095 Mpx |
| RP-05 1.3.59 | 36 | 2.41 MB | 0.586 Mpx |
| RP-01 1.3.125 | 21 | 1.13 MB | 0.341 Mpx |
| RP-10 1.3.51 | 9 | 1.10 MB | 0.174 Mpx |
| **Total** | **191** | **15.72 MB** | **3.196 Mpx** |

### T2. Every family that changes (60) — current count, resolution, bytes, proposal, savings

Bytes = colour + normal + MERS + texture_set json of the whole family today. Savings assume the dropped images are average for the family. Colour atlas = one square tile per image (`atlas_budget.py` rule).

| Family (textures/blocks/…) | Pack(s) | Res | Now | Proposed | Bytes now | Saved | Atlas saved | Why this number |
|---|---|---|---:|---:|---:|---:|---:|---|
| `gravel` | RP-04 | 128 | 16 | **8** | 1.58 MB | 0.79 MB | 0.131 | patchy ground (pits, swamp floor, mangrove roots); 8 = the lattice floor for slab families |
| `packed_mud` | RP-04 | 128 | 16 | **8** | 1.36 MB | 0.68 MB | 0.131 | patchy ground (pits, swamp floor, mangrove roots); 8 = the lattice floor for slab families |
| `mud` | RP-04 | 128 | 16 | **8** | 1.28 MB | 0.64 MB | 0.131 | patchy ground (pits, swamp floor, mangrove roots); 8 = the lattice floor for slab families |
| `muddy_mangrove_roots_side` | RP-05 | 128 | 15 | **8** | 1.37 MB | 0.64 MB | 0.115 | patchy ground (pits, swamp floor, mangrove roots); 8 = the lattice floor for slab families |
| `muddy_mangrove_roots_top` | RP-05 | 128 | 15 | **8** | 1.34 MB | 0.63 MB | 0.115 | patchy ground (pits, swamp floor, mangrove roots); 8 = the lattice floor for slab families |
| `mycelium_top` | RP-10 | 128 | 16 | **12** | 1.72 MB | 0.43 MB | 0.066 | biome-floor cover seen in wide expanses like grass; 12 keeps the (x+2z) lattice no-repeat guarantee (needs >= 8) |
| `mycelium_side` | RP-10 | 128 | 16 | **12** | 1.71 MB | 0.43 MB | 0.066 | biome-floor cover seen in wide expanses like grass; 12 keeps the (x+2z) lattice no-repeat guarantee (needs >= 8) |
| `dirt_podzol_side` | RP-04 | 128 | 16 | **12** | 1.68 MB | 0.42 MB | 0.066 | biome-floor cover seen in wide expanses like grass; 12 keeps the (x+2z) lattice no-repeat guarantee (needs >= 8) |
| `dirt_podzol_top` | RP-04 | 128 | 16 | **12** | 1.63 MB | 0.41 MB | 0.066 | biome-floor cover seen in wide expanses like grass; 12 keeps the (x+2z) lattice no-repeat guarantee (needs >= 8) |
| `pw_warped_nylium_top` | RP-04 | 128 | 16 | **12** | 1.37 MB | 0.34 MB | 0.066 | biome-floor cover seen in wide expanses like grass; 12 keeps the (x+2z) lattice no-repeat guarantee (needs >= 8) |
| `snow` | RP-10, RP-04 | 128/192 | 10 | **8** | 1.70 MB | 0.34 MB | 0.061 | natural stone / snow in large exposures; 8 is also the lattice floor wherever a pw: slab of it exists (n < 8 breaks the slab no-repeat rule) |
| `pw_crimson_nylium_top` | RP-04 | 128 | 16 | **12** | 1.33 MB | 0.33 MB | 0.066 | biome-floor cover seen in wide expanses like grass; 12 keeps the (x+2z) lattice no-repeat guarantee (needs >= 8) |
| `pw_warped_nylium_side` | RP-04 | 128 | 15 | **12** | 1.34 MB | 0.27 MB | 0.049 | biome-floor cover seen in wide expanses like grass; 12 keeps the (x+2z) lattice no-repeat guarantee (needs >= 8) |
| `pw_crimson_nylium_side` | RP-04 | 128 | 15 | **12** | 1.29 MB | 0.26 MB | 0.049 | biome-floor cover seen in wide expanses like grass; 12 keeps the (x+2z) lattice no-repeat guarantee (needs >= 8) |
| `mud_bricks` | RP-04 | 128 | 16 | **6** | 1.54 MB | 0.96 MB | 0.164 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `oak_log` | RP-01, RP-04 | 128/192 | 11 | **8** | 2.39 MB | 0.65 MB | 0.099 | pw: tree bark — each tree block draws 5 side variants (pw:variant 5); 8 keeps a margin across ages |
| `birch_log` | RP-01, RP-04 | 128 | 15 | **8** | 1.26 MB | 0.59 MB | 0.115 | pw: tree bark — each tree block draws 5 side variants (pw:variant 5); 8 keeps a margin across ages |
| `cave_vines_body` | RP-05 | 128 | 15 | **6** | 0.91 MB | 0.55 MB | 0.147 | small scattered sprites / rare blocks — repetition is not readable; 6 = the floor |
| `cave_vines_head` | RP-05 | 128 | 15 | **6** | 0.71 MB | 0.43 MB | 0.147 | small scattered sprites / rare blocks — repetition is not readable; 6 = the floor |
| `bamboo_block` | RP-04 | 128 | 12 | **6** | 0.70 MB | 0.35 MB | 0.098 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `jungle_log` | RP-01, RP-04 | 128 | 11 | **8** | 1.13 MB | 0.31 MB | 0.049 | pw: tree bark — each tree block draws 5 side variants (pw:variant 5); 8 keeps a margin across ages |
| `spruce_log` | RP-01, RP-04 | 128 | 11 | **8** | 1.09 MB | 0.30 MB | 0.049 | pw: tree bark — each tree block draws 5 side variants (pw:variant 5); 8 keeps a margin across ages |
| `mushroom_stem` | RP-05, RP-01 | 128 | 16 | **6** | 0.36 MB | 0.23 MB | 0.164 | small scattered sprites / rare blocks — repetition is not readable; 6 = the floor |
| `bark/jungle_log` | RP-01 | 128 | 10 | **8** | 1.03 MB | 0.21 MB | 0.033 | pw: tree bark — each tree block draws 5 side variants (pw:variant 5); 8 keeps a margin across ages |
| `bark/spruce_log` | RP-01 | 128 | 10 | **8** | 0.99 MB | 0.20 MB | 0.033 | pw: tree bark — each tree block draws 5 side variants (pw:variant 5); 8 keeps a margin across ages |
| `cobblestone` | RP-04 | 128 | 10 | **8** | 0.96 MB | 0.19 MB | 0.033 | natural stone / snow in large exposures; 8 is also the lattice floor wherever a pw: slab of it exists (n < 8 breaks the slab no-repeat rule) |
| `cracked_nether_bricks` | RP-04 | 128 | 8 | **6** | 0.75 MB | 0.19 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `mossy_stone_bricks` | RP-04 | 128 | 8 | **6** | 0.73 MB | 0.18 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `brick` | RP-04 | 128 | 8 | **6** | 0.71 MB | 0.18 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `cracked_stone_bricks` | RP-04 | 128 | 8 | **6** | 0.70 MB | 0.17 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `cracked_polished_blackstone_bricks` | RP-04 | 128 | 8 | **6** | 0.69 MB | 0.17 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `polished_tuff` | RP-04 | 128 | 8 | **6** | 0.68 MB | 0.17 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `tuff_bricks` | RP-04 | 128 | 8 | **6** | 0.67 MB | 0.17 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `polished_granite` | RP-04 | 128 | 8 | **6** | 0.67 MB | 0.17 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `stone_bricks` | RP-04 | 128 | 8 | **6** | 0.66 MB | 0.16 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `sandstone_top` | RP-04 | 128 | 8 | **6** | 0.66 MB | 0.16 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `red_sandstone_top` | RP-04 | 128 | 8 | **6** | 0.65 MB | 0.16 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `polished_andesite` | RP-04 | 128 | 8 | **6** | 0.65 MB | 0.16 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `polished_blackstone_bricks` | RP-04 | 128 | 8 | **6** | 0.64 MB | 0.16 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `polished_diorite` | RP-04 | 128 | 8 | **6** | 0.63 MB | 0.16 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `smooth_stone` | RP-04 | 128 | 8 | **6** | 0.62 MB | 0.15 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `polished_blackstone` | RP-04 | 128 | 8 | **6** | 0.60 MB | 0.15 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `smooth_quartz` | RP-04 | 128 | 8 | **6** | 0.55 MB | 0.14 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `polished_deepslate` | RP-04 | 128 | 8 | **6** | 0.50 MB | 0.12 MB | 0.033 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `torchflower` | RP-01 | 128 | 9 | **6** | 0.34 MB | 0.11 MB | 0.049 | small scattered sprites / rare blocks — repetition is not readable; 6 = the floor |
| `bark/oak_log` | RP-01 | 128 | 9 | **8** | 0.93 MB | 0.10 MB | 0.016 | pw: tree bark — each tree block draws 5 side variants (pw:variant 5); 8 keeps a margin across ages |
| `fern_small` | RP-05 | 128 | 8 | **6** | 0.38 MB | 0.09 MB | 0.033 | small scattered sprites / rare blocks — repetition is not readable; 6 = the floor |
| `warped_stem_top` | RP-04 | 128 | 8 | **7** | 0.74 MB | 0.09 MB | 0.016 | log ends — pw: trees draw 7 top variants (pw:top_variant 7); vanilla logs random |
| `bark/birch_log` | RP-01 | 128 | 9 | **8** | 0.81 MB | 0.09 MB | 0.016 | pw: tree bark — each tree block draws 5 side variants (pw:variant 5); 8 keeps a margin across ages |
| `stripped_warped_stem_top` | RP-04 | 128 | 8 | **7** | 0.69 MB | 0.09 MB | 0.016 | log ends — pw: trees draw 7 top variants (pw:top_variant 7); vanilla logs random |
| `stripped_crimson_stem_top` | RP-04 | 128 | 8 | **7** | 0.66 MB | 0.08 MB | 0.016 | log ends — pw: trees draw 7 top variants (pw:top_variant 7); vanilla logs random |
| `smooth_red_sandstone` | RP-04 | 128 | 7 | **6** | 0.57 MB | 0.08 MB | 0.016 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `smooth_sandstone` | RP-04 | 128 | 7 | **6** | 0.57 MB | 0.08 MB | 0.016 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `red_nether_brick` | RP-04 | 128 | 7 | **6** | 0.54 MB | 0.08 MB | 0.016 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `quartz_bricks` | RP-04 | 128 | 7 | **6** | 0.52 MB | 0.07 MB | 0.016 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `nether_brick` | RP-04 | 128 | 7 | **6** | 0.52 MB | 0.07 MB | 0.016 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |
| `rose_bush_top` | RP-05, RP-01 | 128 | 7 | **6** | 0.46 MB | 0.07 MB | 0.016 | small scattered sprites / rare blocks — repetition is not readable; 6 = the floor |
| `hanging_roots` | RP-05 | 128 | 7 | **6** | 0.40 MB | 0.06 MB | 0.016 | small scattered sprites / rare blocks — repetition is not readable; 6 = the floor |
| `hardened_clay` | RP-04 | 128 | 9 | **8** | 0.24 MB | 0.03 MB | 0.016 | natural stone / snow in large exposures; 8 is also the lattice floor wherever a pw: slab of it exists (n < 8 breaks the slab no-repeat rule) |
| `end_bricks` | RP-04 | 64 | 7 | **6** | 0.17 MB | 0.02 MB | 0.004 | crafted / building material (bricks, polished, quartz, smooth) — seen in walls at close range, mortar hides repeats; 6 = the floor |

### T3. Families that do NOT change (multi-image, used) — by reason

| Reason | Families | Examples (family count) |
|---|---:|---|
| bound to the ramps' pw:var state | 76 | `pw_deck14_cobble` 9, `pw_deck14_smooth_stone` 9, `pw_deck14_stonebrick` 9, `pw_deck26_cobble` 9, `pw_deck26_smooth_stone` 9, `pw_deck26_stonebrick` 9, `pw_rampv4_cobble` 9, `pw_rampv4_smooth_stone` 9 |
| already at or under the 6 floor (never add variants) | 72 | `basalt_top` 6, `bush` 6, `chiseled_nether_bricks` 6, `chiseled_polished_blackstone` 6, `chiseled_stone_bricks` 6, `lilac_top` 6, `peony_top` 6, `polished_basalt_top` 6 |
| natural stone / snow in large exposures | 23 | `andesite` 8, `blue_terracotta` 8, `brown_terracotta` 8, `calcite` 8, `cyan_terracotta` 8, `deepslate` 8, `dripstone_block` 8, `end_stone` 8 |
| a 4x4 continuous plank pattern cut into 16 tiles (pw:gx/gy/gz), not 16 variants | 11 | `acacia` 16, `birch` 16, `cherry` 16, `crimson` 16, `dark_oak` 16, `jungle` 16, `mangrove` 16, `oak` 16 |
| log ends — pw: trees draw 7 top variants (pw:top_variant 7) | 11 | `log_top_acacia` 7, `log_top_birch` 7, `log_top_jungle` 7, `log_top_oak` 7, `log_top_spruce` 7, `pw_birch_log_top` 7, `pw_dark_oak_log_top` 7, `pw_jungle_log_top` 7 |
| not a variant set (growth stages / states / animation / markers digits) | 8 | `pw_num` 64, `waterlily` 12, `pw_sweep` 8, `stage` 3, `stage` 3, `stage` 3, `stage` 3, `pw_disc` 2 |
| grass / dirt / sand | 6 | `pw_red_sand` 24, `pw_sand` 24, `grass_block_top` 17, `coarse_dirt` 16, `dirt` 16, `grass_block_side` 16 |
| natural stone / snow in large exposures; 8 is also the lattice floor wherever a pw: slab of it exists (n < 8 breaks the slab no-repeat rule) | 1 | `snow_layer` 8 |

### T4. What can drop to 128 px (colour + MERS + normal together) — every used block texture above 128 px

Bytes at 128 were MEASURED: each colour / normal / MERS image was resampled to 128 px wide (Lanczos; cut-outs: box-filtered alpha re-thresholded at 128 so edges stay hard) and re-encoded as PNG. Flipbook strips keep their frame count.

| Pack | Group | Images | Res now | Bytes now | Bytes at 128 | Saved | Colour atlas saved | Verdict |
|---|---|---:|---|---:|---:|---:|---:|---|
| RP-13 | `pw_fill* (ramp / roof cut-outs)` | 248 | 256x256 | 62.97 MB | 14.84 MB | 48.14 MB | 12.190 | can drop cut-out (hard alpha required; witness test) |
| RP-01 | `pw_vine/* wind strips (12 vines + extra, r/w)` | 27 | 192x3072, 192x192 | 69.36 MB | 33.72 MB | 35.65 MB | 0.553 | can drop vine flipbook strip |
| RP-11 | `ores (all 18 + deepslate)` | 72 | 256x256 | 14.92 MB | 5.77 MB | 9.15 MB | 3.539 | can drop ore |
| RP-04 | `pw_fill* (ramp / roof cut-outs)` | 32 | 256x256 | 6.09 MB | 1.94 MB | 4.16 MB | 1.573 | can drop cut-out (hard alpha required; witness test) |
| RP-05 | `kelp strips` | 6 | 192x3072 | 7.80 MB | 5.06 MB | 2.74 MB | 0.123 | can drop |
| RP-04 | `candles` | 16 | 192x192 | 1.90 MB | 0.68 MB | 1.22 MB | 0.328 | can drop |
| RP-10 | `snow` | 7 | 192x192 | 1.47 MB | 0.63 MB | 0.83 MB | 0.143 | can drop |
| RP-04 | `pw_mitre` | 2 | 256x256 | 0.29 MB | 0.08 MB | 0.21 MB | 0.098 | can drop cut-out (hard alpha required; witness test) |
| RP-01 | `pw_secret_painting` | 4 | 256x256 | 0.26 MB | 0.07 MB | 0.18 MB | 0.197 | can drop |
| RP-04 | `pw_mitre_thatch` | 1 | 256x256 | 0.05 MB | 0.01 MB | 0.03 MB | 0.049 | can drop cut-out (hard alpha required; witness test) |
| RP-04 | `(all)` | 17 | 192x192 | 4.88 MB | 4.88 MB | 0.00 MB | 0.000 | keep: grass (his 10-07 rule: grass stays high) |
| RP-10 | `(all)` | 16 | 192x192 | 4.24 MB | 4.24 MB | 0.00 MB | 0.000 | keep: grass (his 10-07 rule: grass stays high) |
| RP-05 | `(all)` | 12 | 256x256 | 0.78 MB | 0.78 MB | 0.00 MB | 0.000 | keep: leaf (his 10-02 ruling: leaves stay 256) |
| RP-01 | `(all)` | 1 | 192x192 | 0.15 MB | 0.15 MB | 0.00 MB | 0.000 | keep: grass (his 10-07 rule: grass stays high) |
| RP-01 | `(all)` | 100 | 256x256 | 16.18 MB | 16.18 MB | 0.00 MB | 0.000 | keep: leaf (his 10-02 ruling: leaves stay 256) |
| RP-04 | `(all)` | 48 | 256x256 | 8.66 MB | 8.66 MB | 0.00 MB | 0.000 | keep: sand (his 10-02 ruling: sand 256 on all maps) |
| RP-05 | `(all)` | 11 | 192x3072 | 14.77 MB | 14.77 MB | 0.00 MB | 0.000 | keep: grass (his 10-07 rule: grass stays high) |
| several | other 192/256 px singles (glowstone, tuff, soul sand, roof, furniture iron, secret painting, moss, lamps, ...) | 48 | 192x192, 192x768, 181x256, 192x135, 192x144, 192x24 | 4.42 MB | 1.99 MB | 2.43 MB | 0.927 | can drop (full list in the .json) |

### T5. 128 px — totals per pack (candidates only)

| Pack | Images | Bytes saved | Colour atlas saved |
|---|---:|---:|---:|
| RP-13 1.0.1 | 248 | 48.14 MB | 12.190 Mpx |
| RP-11 1.3.40 | 72 | 9.15 MB | 3.539 Mpx |
| RP-04 1.3.159 | 90 | 7.28 MB | 2.790 Mpx |
| RP-01 1.3.125 | 35 | 36.06 MB | 0.831 Mpx |
| RP-05 1.3.59 | 11 | 3.27 MB | 0.225 Mpx |
| RP-10 1.3.51 | 7 | 0.83 MB | 0.143 Mpx |
| **Total** | **463** | **104.72 MB** | **19.719 Mpx** |

### T6. Permutations each change removes (BP-02 1.3.229 = 55,948 by this census)

| Change | Blocks | Permutations now | After | Removed | Visual change |
|---|---:|---:|---:|---:|---|
| Dead `pw:gvar` values on slabs (the slab smoother never sets them) | 31 | 3,600 | 855 | **2,745** | none |
| Lattice families cut 16 → 12 / 8 (podzol, mycelium, nylium, gravel, mud) | 8 | 704 | 448 | 256 | the variant cut itself |
| Ramps `pw:var` 8 → 6 (cobble, stone bricks, smooth stone) | 42 | 6,720 | 5,040 | 1,680 | 2 fewer ramp variants |
| Ramps `pw:var` removed (BP-02 1.3.230 SLIM, the PS5 isolation build) | 266 | 24,640 | 5,320 | 19,320 | every ramp shows variant 0 |
| (cost, not saving) raising the 4-variant ramps to 6 to meet the floor | 224 | 17,920 | 26,880 | **+8,960** | — do NOT do this |
| Plank grids 4×4×4 → 2×2×2 (needs new 2×2 plank art) | 11 | 704 | 88 | 616 | larger repeat of the plank pattern |

Dead-gvar detail: `pw:slab_andesite` 160→80; `pw:slab_calcite` 160→80; `pw:slab_clay` 160→10; `pw:slab_deepslate` 160→80; `pw:slab_diorite` 160→80; `pw:slab_granite` 160→80; `pw:slab_moss` 160→10; `pw:slab_packed_ice` 160→10; `pw:slab_path` 160→10; `pw:slab_red_sandstone` 160→80; `pw:slab_sandstone` 160→80; `pw:slab_snow` 160→80; `pw:slab_stone` 160→80; `pw:slab_terracotta` 80→5; `pw:slab_terracotta_black` 80→5; `pw:slab_terracotta_blue` 80→5; `pw:slab_terracotta_brown` 80→5; `pw:slab_terracotta_cyan` 80→5; `pw:slab_terracotta_gray` 80→5; `pw:slab_terracotta_green` 80→5; `pw:slab_terracotta_light_blue` 80→5; `pw:slab_terracotta_light_gray` 80→5; `pw:slab_terracotta_lime` 80→5; `pw:slab_terracotta_magenta` 80→5; `pw:slab_terracotta_orange` 80→5; `pw:slab_terracotta_pink` 80→5; `pw:slab_terracotta_purple` 80→5; `pw:slab_terracotta_red` 80→5; `pw:slab_terracotta_white` 80→5; `pw:slab_terracotta_yellow` 80→5; `pw:slab_tuff` 160→10.

---

## 4. Notes on the 128 px list

- **Cut-outs (`pw_fill*`, `pw_mitre*`) need HARD alpha.** Round 1002f resampled them with soft edges and the cut lines moved
  (journal 2612–2613: restored at 256 with hard alpha). The 128 estimate above re-thresholds alpha at 128, so edges stay hard,
  but each cut line moves by up to 1/256 of a block. **Witness test before shipping:** one ramp-8 run and one roof gable at 128,
  checked for hairline gaps at the steps.
- **RP-13 fills are 75 % of the whole 128 saving.** They also explain most of the atlas jump since 10-02.
- **Vines** (`pw_vine/*`, 192 × 3072 wind strips with MERS + normal) are 69.4 MB — the largest single item in RP-01. At 128 they
  save 35.7 MB but only 0.55 Mpx of atlas (a strip counts one frame). They are a size lever, not an atlas lever.
- **Ores** were rebuilt at 256 in round 1.3.40 (Stratum chips). Dropping them is his call: 3.5 Mpx.
- **30 texture sets have 256 px normal + MERS under a 192 px colour** (glowstone, 16 candles, podzol_top in RP-10 and others;
  `json` → `res128` rows). Whatever he decides, those layers should at least match their colour (size mismatch).
- **Kept by ruling** (not candidates): leaves 256 (112 images, 7.3 Mpx), sand 256 (48 images), grass block 192 (34 images).
  **Ambiguity:** RP-05's 11 grass *plant* sway strips (192 × 3072, 14.8 MB) are kept here as "grass"; if he meant only the grass
  block, they can drop too (~7 MB).

## 5. What each change touches when it is built (for the lead; nothing was applied)

| Change | RP side | BP side |
|---|---|---|
| Variant cut on a vanilla-key family (random `variations`) | delete the dropped images + their `_n` / `_mer` / sets; shorten the `variations` array; repoint any `_gN` key that named a dropped image | none |
| Variant cut on a lattice family (podzol, mycelium, nylium, gravel, mud) | as above; `_g0…_g15` keys → `_g0…_g(n−1)` | `pw:gvar` enum 0…n−1, permutations rewritten, `PW_SLAB_VARN` / `gvarMosaic(…, n)` changed in main.js + pw_ground.js |
| pw: tree bark 15/11/10/9 → 8 | delete images; repoint `pw_<tree>_<age>_log_v0…v4` keys | none (`pw:variant` stays 5) |
| Dead gvar values | none | `pw:gvar` enum 16 → 8 (stone types, snow, sandstones) / removed (clay, moss, packed ice, path, tuff, 16 terracottas); permutations rewritten |
| 128 px | resample colour + normal (renormalise to unit length) + MERS together; cut-outs with hard alpha; `fix_layer_sizes` post-pass | none |
- Gates: `atlas_budget.py` (fix its blocks.json merge first, §1.3), `geo_ref_check.py`, the permutation count, the hard-alpha
  check, the normal-unit census.

## 6. Questions for Abs0lum

1. Since RP-13 went in (10-06), have you seen the whole world go soft / blurry (the "16-px look") on the PS5 or the phone? (The
   census says the atlas is now over its one-sheet limit.)
2. May the RP-13 ramp fills (and RP-04's roof cut-outs) go to 128 px? They are the single biggest saving, but they are the
   textures whose edges we restored at 256 on 10-02; a small test run first.
3. Are podzol, mycelium and the nylium "dirt" to you (stay at 16), or ground covers that can go to 12?
4. Does "grass stays high" mean only the grass block, or also the grass plants (RP-05 sway strips)?
5. The 4-variant ramps (16 stones) are below your 6 floor. Leave them at 4? (Raising them costs 8,960 permutations.)
6. May the dead gvar values be removed in the next BP-02 build? (No visual change; −2,745 permutations.)
7. Ores and vines to 128? (Ores −3.5 Mpx; vines −35.7 MB.)

## 7. Retro-Sweep (events: census pipeline built; a failed assumption corrected — `used_keys` blocks.json merge; atlas
over-budget discovered). Suggestions only — nothing implemented.

| Subsystem | What changes | Suggestion | Effort | Priority |
|---|---|---|---|---|
| PBR / textures | atlas is ~70–75 Mpx vs 67.1 cap | RP-13 fills → 128 hard alpha (−12.2 Mpx) first; then this doc's variant cut (−3.2) | M | **HIGH** |
| build / verification tooling | `block_pbr_census.used_keys` ignores lower-pack blocks.json fields; `atlas_budget.py` / `stack_now.py` have no current-stack entry and miss RP-13 | field-merge in `used_keys`; add a `PW_STACK=now` entry incl. RP-13; run the atlas budget in every RP gate | S | HIGH |
| custom blocks / permutations | 2,745 dead gvar permutations; 4-variant ramps set `pw:var` from `(x + 2z) mod 8` (main.js 5263–5268) — for a 4-value enum, `withState` throws on 4…7 and the catch keeps variant 0, so half of hand-placed 4-variant ramps never vary | remove dead gvar values; use `mod nvar` per ramp | S | HIGH (PS5) / MED |
| terrain caps / worldgen | lattice floor n ≥ 8 for slab families (proved in §2) | write it as a lesson candidate next to the lattice comment | S | MED |
| trees / canopy | bark families 9–15 images vs 5 drawn per block | cut to 8 (T2) | S | LOW |
| documentation / lessons | lesson candidates: L-ATLAS-RECHECK (every new RP gets an atlas re-count) · L-LATTICE-8 · blocks.json field merge (unverified) | add to LESSON-CANDIDATES | S | MED |

**No hit:** redwood biome · mobs (RP-07) · atmospherics / sky / fog · scripts beyond the two lines above · audio.
