# Unified-Abs0lut-Claude v0.5.6-UV-DIAG — Project Handoff

**Built**: 2026-04-19  
**Iteration tag**: UV-DIAG  
**File**: `/mnt/user-data/outputs/Unified-Abs0lut-Claude-v0.5.6-UV-DIAG.mcaddon` (34.09 MB)  
**Supersedes**: v0.5.5-PATRIX-128  
**Purpose**: Two parallel tracks. (1) UV diagnostic tooling: 8×8 color-grid test patterns packaged as a toggleable diagnostic RP for broken-mob UV investigation. (2) Real leaf fix attempt #2 — addresses root cause of the spindly-outer/opaque-inner artifact.

---

## Pack load order — activate in this exact order

**Behavior Packs (top → bottom):**

| # | Pack |
|---|---|
| 1 | `PatrixWorld-Tectonic BP [VV TEST RUN v0.7.2]` |
| 2 | `FallingTree BP [VV TEST RUN v2.8.1]` |
| 3 | `PatrixCanopyGen [VV TEST RUN v0.1.2]` |
| 4 | `pw_variants BP [ZOMBIE-PROOF v0.1.1]` |

**Resource Packs (top → bottom):**

| # | Pack |
|---|---|
| 1 | `pw UV Diagnostic RP [GRID-8x8 v0.1.0]` ⭐ NEW — toggle ON/OFF as needed |
| 2 | `PatrixWorld-Tectonic RP [VV TEST RUN v0.7.2]` |
| 3 | `PatrixWorld Sampler [PAT+ALAC BLEND v0.5.1]` ← bumped |
| 4 | `FallingTree RP [VV TEST RUN v2.8.1]` |
| 5 | `pw_variants RP [ZOMBIE-PROOF v0.1.2]` |

**UV Diag pack behavior:**
- When ENABLED (top of RP list): replaces drowned, zombie, husk, zombie_villager, dolphin, squid, glow_squid, cod, salmon, tropical_a, tropical_b, pufferfish, and bee textures with 8×8 color-grid UV test patterns.
- When DISABLED (removed from list): normal Patrix textures apply.
- Recommended workflow: enable the diagnostic pack, enter world, screenshot broken mobs showing the grid. Compare captured colors against the reference card to identify which atlas UV region each body part samples from.

---

## Track 1 — UV test pattern tooling

### The 8×8 color grid palette

64 distinct colors, uniquely identifiable by (HUE, VALUE) coordinates:

- **8 columns (hues)**: RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, MAGENTA, GRAY
- **8 rows (value levels)**: V1 (brightest, row 1) → V8 (darkest, row 8)

Example: a cell at column 4, row 3 = `GREEN V3` = RGB(0, 188, 0).

### Target mobs covered

The diagnostic pack includes UV patterns sized to match each mob's Bedrock-expected texture dimensions:

| Mob | Expected dimensions | Pattern applied |
|---|---|---|
| drowned | 128×128 | 8×8 grid, 16px cells |
| zombie | 128×128 | 8×8 grid, 16px cells |
| husk | 128×128 | 8×8 grid, 16px cells |
| zombie_villager | 128×128 | 8×8 grid, 16px cells |
| dolphin | 128×128 | 8×8 grid, 16px cells |
| squid | 128×64 | 8×8 grid, 16×8 rectangular cells |
| glow_squid | 128×64 | 8×8 grid, 16×8 rectangular cells |
| cod | 64×64 | 8×8 grid, 8px cells |
| salmon | 64×64 | 8×8 grid, 8px cells |
| tropical_fish (a/b) | 32×32 | 8×8 grid, 4px cells |
| pufferfish | 64×64 | 8×8 grid, 8px cells |
| bee | 128×128 | 8×8 grid, 16px cells |

### Using the diagnostic workflow

1. Activate the UV Diagnostic RP at the top of your RP stack in the test world
2. Find or spawn the target mob
3. Screenshot showing which colors appear on which body parts
4. Compare against the reference card in `uv_grid_reference_card.png` inside the diagnostic pack (or use the one saved alongside handoffs)
5. Each body part's displayed color identifies the UV region it samples. Note: "head_front = RED V3, body = GREEN V5, tail = BLUE V7" etc.
6. Use this mapping to correct the Patrix atlas: reposition content at the correct UV coordinates so body parts sample the intended texture regions.
7. Disable the diagnostic RP. Test natural rendering. Iterate.

### Workflow for aquatic mobs (timing-constrained)

For mobs you can't easily engage (fast swimmers, dangerous hostiles):
- Broad-spectrum approach: enable the diagnostic pack, swim through affected biomes, capture as many UV shots as possible
- Decode the captures offline and apply fixes across the whole set at once
- Not as precise per-mob as the individual workflow, but faster overall

---

## Track 2 — Real leaf fix attempt #2

### Root cause identification

Pixel-analysis of Patrix leaf textures revealed the actual cause of the artifacts:

| Texture source | Opaque pixel percentage | Transparency |
|---|---|---|
| Patrix oak_leaves.png | 25.3% | 74.7% |
| Patrix birch_leaves.png | 31.0% | 69.0% |
| Patrix cherry_leaves.png | 38.8% | 61.2% |
| **Vanilla Bedrock oak_leaves** | **66.5%** | **33.5%** |
| **Vanilla Bedrock birch_leaves** | **51.7%** | **48.3%** |

**Patrix leaves are 2-3× more transparent than Bedrock vanilla leaves.** This is the source of the problem.

### Mechanism of the artifact

When you see a "solid opaque inner cube inside a stringy outer canopy," what's actually happening:
- Outer leaf texture is 70% transparent → you see through alpha gaps on the near face
- Through those gaps, you see the next leaf block's face — from the inside
- That inner face renders at ~70% transparent too, but from that viewing angle, the remaining 30% of the pixels LINE UP in a pattern that looks like a solid cube edge
- The "solid inner cube" is an illusion caused by overlapping alpha textures, not an actual rendering bug

### The fix applied

Alpha-dilation on all 11 leaf species to raise opaque pixel percentage to ~60% (matching Bedrock vanilla standard):

| Leaf | Before | After |
|---|---|---|
| oak_leaves | 25.3% | 60.7% |
| spruce_leaves | 24.2% | 60.2% |
| birch_leaves | 31.0% | 60.5% |
| jungle_leaves | 36.6% | 62.9% |
| acacia_leaves | 26.4% | 62.1% |
| dark_oak_leaves | 28.6% | 60.7% |
| cherry_leaves | 38.8% | 60.1% |
| mangrove_leaves | 38.9% | 62.5% |
| pale_oak_leaves | 44.0% | 62.7% |
| azalea_leaves | 37.8% | 60.7% |
| flowering_azalea_leaves | 42.2% | 62.0% |

**Dilation method**: For each transparent pixel, if it has 3+ opaque neighbors, make it opaque using averaged color from those neighbors. Iterate until target opacity reached. Preserves Patrix leaf shape aesthetics while adding density.

### Expected visual result

- Outer leaf silhouettes should look denser, less spindly/stringy
- You should no longer see "solid opaque cube" faces between outer leaves (inner alpha gaps now filled)
- Canopy should look more like a continuous mass of leaves, with subtle transparency at edges rather than large alpha gaps revealing whole faces of adjacent blocks

### If this fix doesn't fully resolve it

Possible follow-ups for v0.5.7:
- Target opacity 70% instead of 60% (closer to vanilla oak)
- Apply the fix to `_carried` leaves variants (for the hand-held leaves)
- Examine Bedrock's carried_leaves atlas mapping (might need to update blocks.json `carried_textures`)
- Investigate whether PatrixCanopyGen's canopy density per feature rule needs tuning (fewer canopy blocks per tree = less overlap)

---

## What to test

### Primary — leaves

1. Load v0.5.6 in a fresh world (with the UV Diag pack DISABLED initially)
2. Find a birch, oak, or jungle forest
3. Look up into canopies — should see denser outer foliage with less "see-through-to-solid-cube" effect
4. Stand inside a tree — should see normal leaf interior, not opaque cube walls
5. Screenshot for evidence of improvement

### Primary — UV diagnostic tooling

1. Enable the UV Diag pack at the top of your RP stack
2. Find the white-rendering mobs (drowned, dolphin, bee, squid, etc.)
3. Screenshot the mobs showing striped color patterns
4. (You'll use these for v0.5.7 mapping work — this iteration's goal is to capture the diagnostic data)
5. Disable the UV Diag pack when done
6. Re-load — normal textures should return

### Secondary — v0.5.5 deferred verifications

With the leaf fix attempted, re-verify these from v0.5.5 that were untested:
- Sheep 3-layer (any sheep visible)
- Sand/red_sand variation weighting (walk a desert/badlands)
- grass_block_side flip variations (place adjacent grass blocks)

---

## Critical / catastrophic failure recovery

- Rollback → `Unified-Abs0lut-Claude-v0.5.5-PATRIX-128.mcaddon` (still in outputs)
- Deeper rollbacks → v0.5.4, v0.5.3, v0.5.2, v0.5.1, v0.5.0 all remain

**If leaves STILL show artifacts after thickening**: the fix approach was wrong direction or insufficient. Next step is to investigate PatrixCanopyGen's feature-rule canopy density (may need fewer canopy blocks placed per tree) or examine the RP material/shader assignment for leaves.

**If UV Diag pack doesn't apply patterns**: check it's at the top of the RP list (must have higher priority than Sampler). If still not applying, check Bedrock paths — some mob textures may live at different paths than we targeted.

---

## Continuous Patrix porting mandate (per §16)

This iteration's port contribution: none specifically (focused on diagnostic tooling + leaf root-cause fix). The leaf thickening IS a Patrix-derived correction — using Patrix sources but with density adjustment.

**v0.5.7 port target**: resume Patrix 64→128 sweep. Target blocks: planks (all wood species), stripped logs (all wood species), and any remaining terrain basics the user flags as low-res.

---

## Pack UUID additions

UV Diagnostic pack UUIDs (locked):
- Header: `29f1bf9f-d7ab-4d58-b271-6dceca4fe580`
- Resources: `0b861e7d-aacb-4882-abff-d1d1a30e3474`

Backed up to `/home/claude/_reference_archive/uv_diag_uuids.json`.

Total unique UUIDs in unified bundle: 20 (up from 18 in v0.5.5).
