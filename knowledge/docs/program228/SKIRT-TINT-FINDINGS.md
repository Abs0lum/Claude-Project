# SKIRT-TINT FINDINGS — grass block skirt shows no biome tint

- Date: 2026-10-06 (program 228). Investigation only. No build, pack or tool was changed and no server was started.
- Witness (accepted as TRUE): Abs0lum, real PS5, 13:45 — "the tint on the grass block skirts is not working." He accepts either fix: engine tint, or a set of baked colours per biome.
- Picture: `_docs/program228/SKIRT-TINT-ANALYSIS.png` (1358×980). Viewed at full resolution, 1/1. The texture close-up `pw_grass_skirt.png` was viewed at 3× on blue, 1/1.

---

## 0. Bottom line

| # | Candidate | Status | Evidence |
|---|---|---|---|
| **H1** | **The "skirt" he sees is the band on the side of VANILLA `minecraft:grass_block`.** Natural ground is the vanilla block (his G1 = a, 10-01). RP-04 still gives that band its colour through `{overlay_color, variations[16]}`, and the engine ignores `overlay_color` in that form. The raw lavender-grey fringe (RGB ≈ 146,127,131) is drawn untinted on every natural grass block. | **Mechanism confirmed by an earlier witness test and still present in the latest build** | His T2 test on 10-01 at 22:51 ("untinted pink-grey"), compared with T1 (literal orange): the only difference between them was the form. RP-04 1.3.159 `terrain_texture.json` still has `grass_side` and `grass_block_side` = `{"overlay_color":"#79c05a","variations":[…16]}`. |
| **H2** | The `skirt` material instance on `pw:grass_block` / `pw:slab_grass` is not tinted by the engine. | **No mechanism found in the files.** Investigation incomplete (P2). One test settles it (§5 V1). | The docs say `tint_method` works on any named instance. Our own leaf `extra` instance (custom name, `tint_method`, alpha test, texture set, VV, PS5) was confirmed by his witness: "tinting works" (D-C340). |
| H3 | The tint is applied, but the texture colour cancels it. | **Ruled out** | The skirt and the grass top share the same lavender cast. Multiplied by plains grass they give nearly the same green (§3). |

**The question that settles it** (asking it is allowed by the witness rule; once he answers, the other branch is closed): *Were the skirts you saw on natural ground (blocks the world generated), or on our smoothed edges, slabs and placed grass blocks?* If he does not know, run the 2-minute test in §5 V1. That test answers the question without relying on memory.

**Recommended fix:** use the engine tint. Fix the vanilla band in RP-04 (route the side face to `grass_side` in vanilla's exact form; finish the T3/T4 test from 10-01). For the pw skirt, adopt the leaf `extra` recipe only if V1 shows the pw skirt is untinted. **Fallback:** baked colour variants per biome for the pw skirt (§4b), plus one fixed pre-coloured fringe for the vanilla band, because a resource pack cannot vary a vanilla texture by biome.

---

## 1. Our files: what the skirt is

**BP-02 1.3.229 (`_build/bp02-229/blocks/`)**, every block at `format_version` 1.21.80:

- `pw_grass_block.json` uses `geometry.pw_grass_block`. State `pw:gvar` has 16 values, with 16 permutations.
- Each permutation defines four instances:
  - `*` = `dirt_g<n>`
  - `up` = `grass_top_g<n>`, tinted `grass`
  - `down` = `dirt_g<n>`
  - `skirt` = `pw_grass_skirt_g<n>`, `render_method` `alpha_test`, `tint_method` `grass`, `face_dimming` true, `ambient_occlusion` true
- `pw_slab_grass.json` has states `pw:gvar` and `pw:snow`, with 85 permutations. The `skirt` instance has the same properties, with 81 tinted copies (the base set plus 80 permutations).
- Census of every instance using a skirt texture:

| Block | Skirt texture | Instances | Tinted? |
|---|---|---|---|
| pw_grass_block | pw_grass_skirt | 17 | yes, `grass` |
| pw_slab_grass | pw_grass_skirt | 81 | yes, `grass` |
| pw_mycelium | pw_mycelium_skirt | 17 | no (correct) |
| pw_podzol | pw_podzol_skirt | 17 | no (correct) |
| pw_crimson_nylium | pw_crimson_skirt | 17 | no (correct) |
| pw_warped_nylium | pw_warped_skirt | 17 | no (correct) |

- **Geometry** is in RP-01 1.3.125 `models/blocks/pw_grass_block.geo.json`:
  - Geometry format 1.16.0. The id `geometry.pw_grass_block` is all lowercase.
  - Bone `body`: one 16×16×16 cube with `up` and `down` named.
  - Bone `grass_skirt`: four zero-thickness planes, each 16.5 wide and 8 tall (y 8→16). Each sits 0.25 px outside the block face.
  - Each plane has exactly one face, bound to `"material_instance": "skirt"` with UV `[0,0]` size `[16,8]` in a declared 16×16 space. **Only the upper half of the 192-px texture is ever drawn** (rows 0–95).
- The slab geometries are `geometry.pw_slab_bottom_grass` (RP-01 `pw_slab.geo.json`) and `…_snow1..4` (RP-04 `pw_snowcaps.geo.json`). They are also 1.16.0, all lowercase, with a `grass_skirt` bone of four planes bound to `skirt`.
- **Tonight's spiral finding** (PS5 did not register ids written in mixed case with geometry format 1.21.0) **does not apply here.** Every grass id, bone and instance name is lowercase, and the format is 1.16.0. The skirt also renders: he sees it and judges its colour.

**Texture `pw_grass_skirt`** (RP-01 1.3.125):

- 192×192 RGBA with 256 alpha levels.
  - Alpha histogram: 15,463 pixels at 0, 15,311 at 255, about 6,100 between.
- Opaque mean RGB is 145, 127, 138. G − (R+B)/2 = −14 (a lavender cast).
- Coverage from top to bottom, in eighths: 1.00, 0.98, 0.86, 0.62 | 0.33, 0.16, 0.04, 0.00.
  - The drawn half ends at 62 % coverage, so the "drips" in rows 96–191 never show. The face ends in a straight line at mid-height. This is cosmetic, not tint.
- Texture set `pw_grass_skirt.texture_set.json` (format 1.21.30):
  - color `pw_grass_skirt`
  - normal `pw_grass_skirt_n` (mean 128, 130, 249)
  - MERS `pw_grass_skirt_mer` (R0 G0 B190 = roughness 0.75)

**Literal read of the texture close-up** (3×, on blue): the upper third is a solid mottled lavender-pink grass mat with a few white blobs. Below it, ragged drips of the same lavender hang down to about 80 % height. The bottom fifth is empty.

### 1.1 Who can override `pw_grass_skirt` (P11 premise audit)

Census of the latest build of every resource pack in his stack, plus the two test packs. Each pack was checked for `pw_grass_skirt*` files of any extension, for any `.json` referencing `pw_grass_skirt` (terrain_texture keys and texture sets), and for `subpacks/`:

| Space | Result |
|---|---|
| rp01-125 | **Owner:** 17 keys (`pw_grass_skirt`, `_g0.._g15`), PNG, `_n`, `_mer` and set. No subpacks. CENSUSED |
| rp02-207, rp03-67, rp04-159, rp05-59, rp06-1429, rp07-1445, rp08-1414, rp10-151, rp11-140, rp12-101, rp13-101 | 0 refs, 0 files, no subpacks. CENSUSED |
| markers-0.2.3-rp, testrunner-rp-0.7.1 | 0 refs, 0 files. CENSUSED |
| Other behaviour packs defining `pw:grass_block` / `pw:slab_grass` (a duplicate id could replace the instance) | bp01-135, bp03-134, stripmine-bp-1313, testrunner-0.5.24, markers-0.2.4-bp: none. CENSUSED |
| `blocks.json` entries for pw blocks | RP-01 `pw:slab_grass` = `{"sound":"grass"}` only. A resource-pack blocks.json cannot change a custom block's material instances anyway. CENSUSED |

**Result: nothing in our stack overrides the skirt texture or its texture set.** RP-03 has no copy of it.

### 1.2 The vanilla band (H1) in our files

- RP-04 1.3.159 `blocks.json` `"minecraft:grass_block"`: `side` → key **`grass_block_side`**, `up` → `grass_block_top`, `down` → `dirt`.
- RP-04 `terrain_texture.json`:
  - `grass_block_side` and `grass_side` are both `{"textures":{"overlay_color":"#79c05a","variations":[16 × grass_block_side_v0..v15]}}`.
  - The overlay sits beside `variations`. **This is the form the T2 witness showed is ignored.**
- Textures `grass_block_side_v0..15.tga` (192 px), each with a set (`_n_pbr` / `_mer_pbr`):
  - Alpha is the tint mask: 29 % of pixels. Coverage by eighth from the top: 0.99, 0.81, 0.52, 0.01, then 0.
  - Masked (fringe) RGB mean is 146, 127, 131 (lavender-grey). The unmasked dirt is 98, 76, 56.
- Vanilla 1.26.50.4 (Mojang bedrock-samples, dated 15-09-2026):
  - `blocks.json` `grass_block`: `side` → **`grass_side`**, `up` → `grass_top`, `down` → `grass_bottom`.
  - `grass_side` = `{"textures":[{"path":"textures/blocks/grass_side","overlay_color":"#df6827"}]}`, a **list** with a sentinel colour.
  - `grass_carried` = `{"path":…,"overlay_color":"#79c05a"}`, the static colour for the item.
- History, from our journal D-C434/D-C435:
  - T1 (vanilla's exact list form, routed through our `grass_block_side` key) → band **orange**, the literal #df6827.
  - T2 (our `variations` + #df6827) → **untinted pink-grey**. ESTABLISHED: the overlay beside `variations` is ignored.
  - T3 (route the side to `grass_side`, one texture) and T4 (a list of 16) were built and delivered on 10-01 at 23:48 (gofile qG1TnIVw). **No result is recorded.**
  - The 1.3.146 change (overlay beside variations) was made before T2 and was never reverted. It is still in 1.3.159.
- The analysis picture (§3) reproduces his 10-01 phone observation: "a lavender/pink-grey top band over moss" (D-C433). Column 5 shows exactly that.

---

## 2. What the engine documents say (question 1)

| Question | Answer | Source |
|---|---|---|
| Does `tint_method` apply to a **custom-named** instance referenced from geometry faces? | **Yes.** "Tinting is applied to textures by specifying the `tint_method` parameter for the relevant material instance. Different material instances of a block can use different tint methods." material_instances "Maps face or material_instance names in a geometry file to an actual material instance." | Bedrock Wiki, Block Tinting; MS Learn, material_instances |
| What does it do? | "Tint multiplied to the color … refers to the 'rain' and 'temperature' of the biome the block is placed in." Values: none, default_foliage, birch_foliage, evergreen_foliage, dry_foliage, grass, water. Held block items are tinted as in plains. | MS Learn; 1.21.70.24 preview changelog |
| Required `format_version` | **1.21.80** or later for `tint_method` (and `isotropic`). Ours = 1.21.80. ✓ | MS Learn |
| With `alpha_test`? | Nothing restricts `render_method`. The docs' own example, Leaf Pile, uses `alpha_test` + `default_foliage`. | MS Learn |
| `alpha_masked_tint` | `true` = alpha is used as the tint mask **and the texture becomes opaque**. That makes it **unusable for a cut-out skirt plane**: the drips would become a solid rectangle. | Bedrock Wiki |
| Under Vibrant Visuals with a texture set? | The docs say nothing. **In-house witness:** leaf blocks with custom instance `extra` + `tint_method` + a texture set in RP-01 + `alpha_test` (pilot) / `alpha_test_to_opaque` (main) on PS5 with VV → "tinting works" (D-C340, 10-01). | our journal |
| Known bugs | No Mojira report found for `tint_method` on custom instances. Nearby reports: **MCPE-190430**, "Secondary material in non-opaque custom blocks may not render" (mixing render methods; unresolved). This is visibility, not tint, and all our instances are `alpha_test`. **MCPE-102097**, grass side colour ≠ top colour (duplicate, 1.16.40). | Mojira |
| Format 1.26.20 note | `ambient_occlusion` must be a float from 1.26.20. Our boolean is legal at 1.21.80. | MS Learn |

**The only property differences between the pw skirt and the witnessed-working leaf `extra`:**

| Property | Leaf `extra` | Skirt |
|---|---|---|
| `face_dimming` | false | **true** |
| `ambient_occlusion` | false | **true** |
| Alpha | binary (cut-out art) | **256 levels** |

The leaf in the main pack also uses `alpha_test_to_opaque`. None of these properties is documented to affect tint. They are the axes for the H2 test matrix (§5 V2b).

---

## 3. Does the texture colour defeat the tint? (question 3) — NO

The engine multiplies texture RGB by the biome colour. Means are over the drawn pixels (alpha ≥ 0.5):

| | Texture mean | × plains #91BD59 | × forest #79C05A | × swamp #6A7039 |
|---|---|---|---|---|
| Grass top (`grass_block_top_v1`, RP-10) | 164, 143, 156 | **93, 106, 54** | 78, 107, 55 | 68, 63, 35 |
| Skirt, drawn half | 147, 130, 140 | **84, 96, 49** | 70, 97, 49 | 61, 57, 33 |

- The skirt is the same hue as the top, 0.90× as bright.
- On the block the skirt also gets side dimming: 0.8 on north/south and 0.6 on east/west in classic rendering.
- The lavender cast is deliberate. It is the complement that the green multiply turns into natural grass, and it is the same on the top, which he says is fine.

**Literal read of SKIRT-TINT-ANALYSIS.png** (4 biome rows × 6 columns, each tile 192 px):

| Column | Content | What it shows |
|---|---|---|
| 1 | Top, untinted | Pink-lavender grass in every row. |
| 2 | Top × tint | Plains olive-green, forest mid-green, swamp dark olive-brown, taiga blue-green. |
| 3 | pw side face, skirt untinted, dimmed 0.8 | Upper half a lavender mat with drips, ending in a straight line at mid-height. Lower half brown dirt. |
| 4 | Same face, skirt tinted | Upper half green, matching column 2's hue a little darker. Lower half dirt. |
| 5 | Vanilla side, overlay ignored | Top ~3/8 a lavender band, then a darker olive moss strip, then dirt with two pale roots. |
| 6 | Vanilla side, overlay applied | The band turns green per biome. |

- The bottom strip shows 8 swatch pairs (skirt mean × tint | top mean × tint) for plains, forest, swamp, taiga, snowy, jungle, savanna/desert and dark forest. Each pair is the same hue; the skirt is slightly darker.

**Conclusion:** if he sees **lavender or pink-grey** on a side, no tint is being applied there at all (H1 or H2). If he sees a **duller or darker green** than the top, the tint works and that is side dimming. The latter would be a brightness question, not this bug.

---

## 4. The fix

### 4a. RECOMMENDED — engine tint (biome-blended, zero per-biome assets)

**Part 1: vanilla `minecraft:grass_block` band (H1). Confirmed mechanism. RP-04 next version (1.3.160).**

1. **First, get his T3/T4 result.** The packs are already built (`_build/grasstint-t3-100`, `-t4-100`) and delivered (qG1TnIVw). Add one new test, **T5**:
   - `variations` with `overlay_color "#df6827"` on **each** variation entry (`{"path":…, "weight":9, "overlay_color":"#df6827"}`).
   - Route the side through `grass_side`.
   - It is the only untested form that could keep the 16-way random variety *and* the engine's biome mapping.
   - Note on T4: a `textures` **list** in terrain_texture is indexed by block data value, not chosen at random. `grass_block` has no data variants, so expect T4 to draw only entry 0. In practice, T4 = T3.
2. **Edit, if T3 (or T5) tints by biome:**
   - `RP-04/blocks.json` → `"minecraft:grass_block".textures.side`: `"grass_block_side"` → **`"grass_side"`**.
   - `RP-04/textures/terrain_texture.json` → `"grass_side"`, either:
     - T3 form: `{"textures":[{"path":"textures/blocks/grass_block_side_v0","overlay_color":"#df6827"}]}`, or
     - T5 form: `{"textures":{"variations":[{"path":"textures/blocks/grass_block_side_v0","weight":9,"overlay_color":"#df6827"}, … v15]}}`.
   - Leave `grass_block_side` in place but unused, or delete it. Leave `grass_carried` as it is.
   - Textures: no change. The `.tga` alpha mask is already Mojang's convention (alpha 0 = dirt, untouched).
3. **If T3 shows the literal orange** (the engine maps the sentinel only for its own file path), the engine path is closed for vanilla blocks. Go to 4b part 2.

**Part 2: pw skirt (H2). Only if V1 shows the pw skirt is lavender.** No mechanism is known, so build a test matrix first (V2b) and do not edit blind. The target recipe is the one witnessed working on the leaf `extra`:

- `pw_grass_block.json` (17 `skirt` entries) and `pw_slab_grass.json` (81 entries): `"face_dimming": false, "ambient_occlusion": false`, if V2b shows that is the axis. Keep `tint_method: "grass"` and `render_method: "alpha_test"`.
- If the alpha axis is the cause: a new RP-01 texture `pw_grass_skirt` with alpha thresholded to 0/255 at 128, a binary cut-out like the leaf art. Copy the set as it is.

### 4b. FALLBACK — baked colour variants per biome

**Part 1: pw skirt** (`pw:grass_block`, `pw:slab_grass`)

- **Variant count.**
  - Vanilla grass colours: 23 distinct values, from the Minecraft Wiki grass table (Bedrock):

| Biome | Grass colour |
|---|---|
| ocean / river / end | 8EB971 |
| plains / beach / deep dark | 91BD59 |
| snowy family (incl. grove / slopes / peaks, clamped) | 80B497 |
| desert / savanna / nether | BFB755 |
| badlands | 90814D |
| swamp / mangrove | 6A7039 |
| swamp, cold noise | 4C763C |
| forest | 79C05A |
| dark forest | 507A32 |
| birch | 88BB67 |
| taiga | 86B783 |
| old-growth pine | 86B87F |
| windswept | 8AB689 |
| jungle | 59C93C |
| sparse jungle | 64C73F |
| meadow | 83BB6D |
| cherry | B6DB61 |
| stony peaks | 9ABE4B |
| snowy beach | 83B593 |
| mushroom | 55C93F |
| lush caves (Bedrock) | B9B75B |
| dripstone (Bedrock) | 8BD58A |
| pale garden | 778272 |

  - Our 10 client biomes (RP-01 `biomes/client_biome/*.json`, `minecraft:grass_appearance`) add 5 new colours: 9FC78B, AEA42A, B5DB88, 8FB377, A8D4E0.
  - That gives 28 distinct colours. Merging colours closer than ΔE 8 (CIELAB) gives **17**.
  - **Proposal: 16 variants** (a 4-bit state). The cold-swamp noise colour and the cave biomes fold into their nearest neighbour.
- **State and selection.**
  - Add state `pw:gtint` (0–15) to both blocks.
  - The colour is chosen by **script** using `dimension.getBiome(loc)`. It is stable on our `@minecraft/server` 2.10.0 pin; main.js already uses it for fireflies.
  - Lookup table: biome id → variant.
  - Set at every script placement:
    - `pwConvertRiser`, spread in `onRandomTick` and the slab smoother: `BlockPermutation.resolve(id, {"pw:gvar":…, "pw:gtint":…})`.
    - The `onPlace` of `pw:ground_behaviour` for player and structure placement.
  - **Self-healing:** the existing `onRandomTick` re-checks `gtint` against the biome. Average delay is a few minutes per block. This also catches blocks placed by features or structures, which cannot read the biome.
  - Cache the biome per 4×4 column cell, because Bedrock biomes are 4×4×4.
  - The item form defaults to plains (variant of #91BD59).
- **Cost.**
  - `minecraft:material_instances` is a single component, and a later matching permutation replaces it whole. The skirt variant therefore multiplies with `gvar`:
    - `pw_grass_block`: 16 → **256** permutation entries
    - `pw_slab_grass`: 85 → about **1,360** entries (file about 76 KB → about 1.2 MB)
  - State space for the slab: gvar 16 × snow 5 × gtint 16 × half 2 = 2,560. Fine.
  - Textures: 16 pre-coloured skirt PNGs (192 px) in RP-01, plus 16 terrain keys (or 16 × 16 `_g` keys if the `_g` naming is kept; a single key per tint is enough). They reuse the existing `_n` / `_mer` through 16 texture sets.
  - Script: about 60 lines plus a test.
- **Visible trade-off:** the top tint is **blended** across biome borders by the engine; the baked skirt switches hard. Expect a mismatch strip a few blocks wide at every border, worst at swamp and desert edges.

**Part 2: vanilla band**

- A resource pack cannot vary a vanilla texture by biome: one key gives one texture everywhere. Per-biome colour is possible only by converting natural ground to `pw:grass_block`. His ruling limits conversion to risers, so that needs his decision.
- The fallback is a **fixed** colour, so the band is never lavender. Either:
  - T1 proved that list form with a literal `overlay_color` is applied. Use `[{path, "overlay_color":"#91BD59"}]` (plains). One texture. Variety lost.
  - Or bake the mask × #91BD59 into the 16 `.tga` RGB (alpha → 255) and keep `variations`. Variety kept. Wrong in swamp, snow and desert.

---

## 5. PS5 verification

**V1 — discriminator** (current packs, about 2 minutes; closes H1 versus H2)

1. Go to a **swamp**, where the tinted top is dark olive and the contrast is largest; plains is the second choice.
2. Stand on natural ground. From the creative inventory (Nature tab), place one **pw:grass_block** and one **pw:slab_grass** directly beside a **natural** grass block, all on the same row.
3. Stand 3 blocks south **facing north**, at eye height, and take a straight-on screenshot of the three side faces. Then take a second shot facing west.
4. Read the result:

| Side band of… | Lavender / pink-grey | Green / olive |
|---|---|---|
| Natural block | H1 confirmed → 4a part 1 | H1 closed |
| pw:grass_block / slab | H2 confirmed → V2b | H2 closed |

**V2a — vanilla route test.** Put T3, then T4, then T5, each **alone** at the top of the stack. Look at natural grass sides in plains, then swamp.

| Result | Meaning |
|---|---|
| Biome green (swamp darker than plains) | The route works → ship that form in RP-04. |
| Orange | Literal colour only → 4b part 2. |
| Pink-grey | Form ignored. |

**V2b — pw skirt matrix** (only if V1 shows pw lavender). A TestRunner BP + RP adds `pw:skirt_t0` … `pw:skirt_t4`, each a grass block that differs in one axis only:

| Block | Variation |
|---|---|
| t0 | Current recipe (control) |
| t1 | `face_dimming:false`, `ambient_occlusion:false` |
| t2 | Binary-alpha skirt texture |
| t3 | `render_method:"alpha_test_to_opaque"` |
| t4 | No texture set (plain PNG key) |

A `/scriptevent pw:test skirt` command places them in a row. Take a screenshot facing north in a swamp. The first green one names the axis.

**V3 — after the fix.** Repeat the V1 layout in plains, swamp, snowy plains and desert:

- The side band should match its own top's hue in every biome.
- Fly along one biome border:
  - With the engine path, the side should blend like the top.
  - With the baked fallback, a hard step is expected and accepted.

---

## 6. Side notes (not the bug)

- **Skirt cut line.** UV `[16,8]` draws only rows 0–95 of the skirt texture. The edge at mid-height is a straight line at 62 % coverage, and the drips in the lower half never show. If he wants hanging blades, use UV `[0,0]`–`[16,16]` on an 8-tall plane (squashes the art) or re-crop the art. Cosmetic.
- **`minecraft:map_color`** on pw grass is a fixed `"#8FB861"`. It could be `{"color":"#ffffff","tint_method":"grass"}` (Bedrock Wiki) so that maps follow the biome. Affects maps only.
- **Item tint.** Held items are tinted as plains (changelog). That is expected and not part of this report.

## 7. Retro-Sweep pointers (for the main session's journal)

| Subsystem | Finding | Effort / priority |
|---|---|---|
| PBR/textures | RP-04 1.3.146's overlay-beside-variations was falsified by T2 on 10-01 and never reverted. Any other `overlay_color` / `tint_color` sitting beside `variations` in RP-04 or RP-10 is suspect. Grep and list. | S / MED |
| custom blocks | pw:mycelium, podzol and nylium skirts: no tint (correct). No action. | — |
| build tooling | Add a verify gate: no terrain key may hold `overlay_color` or `tint_color` beside `variations`. | S / MED |
| documentation | Lesson candidate L-OVERLAY-FORM: "`overlay_color` beside `variations` is ignored. In list form it is applied literally. Biome mapping of the #df6827 sentinel is unproven outside vanilla's own `grass_side` route (T3 pending)." | S |

**No-hit:** terrain caps, trees/falling-tree, redwood, mobs, atmospherics, worldgen, audio.

## 8. Sources

- Microsoft Learn, `minecraft:material_instances` (ms.date 02/11/2025): https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraft_material_instances
- Bedrock Wiki, Block Tinting: https://wiki.bedrock.dev/blocks/block-tinting (source: https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/blocks/block-tinting.md)
- Minecraft Beta & Preview 1.21.70.24 changelog (tint_method introduced): https://feedback.minecraft.net/hc/en-us/articles/34396781018893
- Mojira MCPE-190430: https://bugs-legacy.mojang.com/browse/MCPE-190430
- Mojira MCPE-102097: https://bugs-legacy.mojang.com/browse/MCPE-102097
- Mojang bedrock-samples 1.26.50.4, `resource_pack/blocks.json` and `resource_pack/textures/terrain_texture.json`: https://github.com/Mojang/bedrock-samples
- Grass colour per biome: https://minecraft.fandom.com/wiki/Grass_Block. This is the older wiki mirror; verify the values against minecraft.wiki before baking.
- Script API TintMethod: https://jaylydev.github.io/scriptapi-docs/latest/enums/_minecraft_server.TintMethod.html
- In-house sources: decision journal D-C340 (leaf tint witness), D-C422, D-C433, D-C434, D-C435 (T1/T2 witness, H-ROUTE), phase_log 2181. The BedrockTweaks PR #997 claim (26.50 grass-side sentinel mapping) is cited from D-C434. It was not re-fetched: GitHub returned 403 here.
