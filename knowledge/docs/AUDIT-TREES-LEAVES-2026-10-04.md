# AUDIT — trees, leaves, worldgen and the falling tree (2026-10-04, 14:1x–14:4x CT)

Abs0lum's 14:09 ask: "Double check our tree structures and canopies as well as our world building logic. Make sure
everything is using our correct new leaves, that the canopies aren't stacked so large that they create opaque blocks,
that we're not allowing vanilla square species to spawn. Be THOROUGH." Plus 14:16: a broken oak log gave no fall.

Witness facts (his): leaves "not working" in a NEW world (seed unknown); the broken log's hover name was **"Oak Log"**;
he was in **Creative** at the break (survival world, switched to fly); the tree stayed standing; **"I noticed OUR oaks as
well, but a faulty oak was spawning as well"**; mangroves nearby showed the opaque look he remembers.

## 1. What is byte-identical between the good set (BP-02 1.3.218) and this one (1.3.219)
| Thing | Evidence |
|---|---|
| the 544 tree templates `structures/pw/trees/` | directory md5 c4bfdc02 in both (216/217 = the pre-rescale set ee984e64) |
| all 646 features, 51 feature rules, 19 biomes | combined md5 654ee367 in both |
| the 11 leaf block definitions (`blocks/*_leaves.json`) | md5 565469e5 since 1.3.204 (before any structure existed) |
| the felling rules (`pw_fell_rules.js`), the template index, the falling-tree entity | identical 217 → 219 |
| `main.js` | 218 → 219 differs only in the build number string and the companion banner |

So no file that generates, defines or fells a tree changed between the world that looked right and this one.

## 2. Templates (all 544, every cell read)
- Leaves: **only `pw:*_leaves`** (11 species, ~236,000 cells). **Vanilla leaves: 0.**
- Logs: pw dodecagon tiers (young / mature / old / elder) + pw roots (one per template). **Vanilla logs only in acacia
  (1,291), cherry (799) and mangrove (763)** — his D-C337 ruling: those three keep square vanilla trunks — plus
  mangrove roots.
- Canopy stacking (leaf cells enclosed on all six sides): oak_old 23 %, oak_mature 19 %, acacia 17 %, dark_oak_elder
  17 %, jungle 7–16 %, spruce 1–8 %, birch 0–5 %. A face between two leaf cubes is never drawn, so stacking cannot make
  OUR leaves opaque; and the colour under our textures' transparent texels is a light grey (181,176,168), so even the
  far "to-opaque" pass tints grey-green — never black.

## 3. Rules, features and scripts
- Every rule of ours places only our templates (plus lying spruce logs in the boreal / pale biomes, by design). Vanilla
  leaf ids appear only in the templates' replace-allowlists.
- TREEGROW grows saplings into our templates; CIVITAS park trees are our templates; CIVITAS woodcutters' saplings grow
  by random ticks into OUR trees (server test 12:1x: 50 `pw:oak_leaves`, 0 vanilla); the village clears leaves to air
  only. **No script converts leaves in either direction.** (The 10-03 note "the runtime leaf scanner converted them" was
  wrong — no such code exists; the flower forest's 64 oak logs are 15 fallen trunks.)
- RP-01 1.3.121: all 100 leaf texture keys used by the 11 leaf blocks resolve, every image is a square 256, every
  texture set uses matching 256 layers (the 128-px `_n` / `_mers` files beside them are unused leftovers).

## 4. Where VANILLA trees still spawn (server census, BP-02 1.3.219, one 96 × 96 sample per biome)
| Biome | vanilla leaves | vanilla logs | our tree blocks |
|---|---|---|---|
| **mangrove swamp** | **10,247** | mangrove 662 | 80 |
| **grove** | **3,506** | spruce 498 | 123 |
| **swamp** | **1,735** | **oak 87 (swamp oaks, with vines)** | 382 (ours too) |
| **old-growth pine taiga** | **989** | spruce 140 (the giants) | 947 (ours too) |
| forest · birch forest · taiga · dark forest · savanna · jungle · flower forest · windswept forest · snowy taiga · snowy slopes · meadow · plains | 0 | (savanna's 55 acacia logs and the flower forest's 64 oak logs are our acacias' square trunks and vanilla fallen trunks) | ours |
| cherry grove · pale garden · jagged / frozen / stony peaks | not located within range | | |

These four are placed by the engine itself (no feature rule exists to override — the open questions Q19 / Q20). A swamp
holds BOTH: our rules' trees and the engine's vanilla oaks with vines. That is the mix he saw.

## 5. What the vanilla trees wear in his stack — the actual defect
The vanilla leaf blocks (`minecraft:oak_leaves` …) take their textures from **RP-05 Flora 1.3.58**, which owns the keys:
- `oak_leaves` → `leaves_oak.png` **32 × 256**: an 8-frame wind strip from the old 32-px leaf era, with **no flipbook
  entry anywhere in the stack**. L-ATLAS-SQUARE (confirmed 09-20): a texture whose height is a whole multiple of its
  width is read as a flipbook and **only frame 0 survives** → vanilla oak leaves render at **32 texels per face**.
  Spruce, birch and pale oak: the same 32 × 256 strips.
- Its transparent texels are **black (0,0,0)** → wherever the engine draws leaves opaque (distance, the phone's leaf
  LOD, fancy off) the cube is **black with green blobs**.
- Mangrove, acacia, dark oak, cherry, azalea: 128-px textures, also black under alpha 0 → the dense mangrove canopy
  turns into black cubes at the opaque distance — the "mangrove opaque" look.
- This has been so in every delivered RP-05 from 1.3.47 (10-01) to 1.3.58. It is a **standing defect**, not a 1.3.219
  regression; it only shows where the engine places its own trees, and this seed put the village beside a swamp.

Screenshot match (113533, full resolution): near leaf faces ~32 texels per block (blotches ~12 px on a ~400-px face);
far cubes near-black with green blobs; bark (128) and our vines (256) sharp — so not an atlas-wide downscale; our 256-px
sprig nowhere. See `LEAF-EVIDENCE-2026-10-04.png` (his face · RP-05 frame 0 cut-out · his far cubes · frame 0 opaque ·
our oak f0).

## 6. The fall that did not happen
- The hover name "Oak Log" = `minecraft:oak_log` = a vanilla swamp oak.
- He was in Creative: `playerBreakBlock` → `isCreative(player)` → "creative -> skip" — by design, so structure editing
  never topples trees. Nothing else in the felling path changed.
- In Survival a vanilla (rootless) tree falls by the legacy BFS path (rule R3b "generated tree, no root") if R5 holds
  (≥ 3 natural leaves touching its logs) — his F3 retest and the content log lines after "broke minecraft:oak_log" decide.
- Still unproven on any device (P1): the carbon-copy fall of a template tree (RP-01 1.3.119+): 544 geometries, three
  render controllers, all ids resolve statically.

## 7. History other than the structures (BP-02 1.3.205 → 1.3.219), as asked
StripMine merged into BP-02 (206: menagerie entities / items / spawn rules / recipes / functions / scripts, incl. 15 egg
block jsons that do not parse); roots (20) + stumps (17) + gold coin pile blocks; crown ring / roof63 / spruce log
block edits; 7 of our biome jsons (tags); 5 sparse tree rules rewritten + 17 legacy-rule overrides + ponds + fallen
logs; the 20 tree feature pools; `main.js` (felling rules 206, template falling set 209, light fix 214, carbon copy
217, CIVITAS hooks 219), `pw_companion`, `pw_mob_light`; `falling_tree.json` (217: ft:tpl / lift / turn). None of it
touches the leaf blocks or RP-05's vanilla leaf textures. RP-01 1.3.118 → 1.3.121: the carbon copies only.

## 8. Proposed next steps (nothing built until he says so)
1. **RP-05 1.3.59 — proper vanilla leaf textures:** every vanilla leaf key gets a square 256-px texture made from our
   `pw_leaves2` face art (grey, tint-ready, for the biome-tinted species; pre-coloured for cherry / azalea / pale oak),
   transparent texels filled light, so every engine-placed tree wears the same leaf as ours. Effort S/M.
2. **Q19 / Q20 ruling** with the census list above: accept (with the textures fixed), a scripted chunk-load sweep that
   converts vanilla trees, or biome weights that make swamp / mangrove / grove / old-growth rarer.
3. **His tests:** `/give @s pw:oak_leaves` placed beside a bad tree (should look right); a Survival break of a swamp oak
   and the content log; the world seed for an exact server reproduction.
4. **A stack gate:** every vanilla leaf key must resolve to a square texture (with a flipbook entry if a strip).
