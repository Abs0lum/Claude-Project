# Unified-Abs0lut-Claude v0.5.3-FIREFLY-FIX — Project Handoff

**Built**: 2026-04-19  
**Iteration tag**: FIREFLY-FIX  
**File**: `/mnt/user-data/outputs/Unified-Abs0lut-Claude-v0.5.3-FIREFLY-FIX.mcaddon` (32.56 MB)  
**Supersedes**: v0.5.2-ERRORS-FIXED  
**Purpose of this iteration**: zero-error load. The firefly_bush atlas error survived the v0.5.2 fix attempt; resolving it deeper this iteration.

---

## What changed from v0.5.2

| Pack | Version | Change |
|---|---|---|
| **PatrixWorld Sampler** | 0.4.1 → **0.4.2** | Removed firefly_bush from `terrain_texture.json` entirely; placed Patrix texture at default path |
| All other 7 packs | unchanged | — |

---

## Why the v0.5.2 fix didn't work, and what worked this time

**What I tried in v0.5.2**: Changed `terrain_texture.json` firefly_bush entry from the `variations` array form to a single-path string form:
```json
"firefly_bush": { "textures": "textures/blocks/firefly_bush_v0" }
```
Reasoning: other flower blocks (dandelion, poppy, etc.) use variations successfully, so the problem seemed to be firefly_bush rejecting that specific format. A single-path entry should look identical to how short_grass is declared (which works).

**Why it failed**: Bedrock's engine has an **internal atlas definition** for `firefly_bush` that expects a specific UV layout. ANY `terrain_texture.json` registration for this short-name — even a clean single-path one — conflicts with the engine's internal expectation, triggering `invalid atlas index 1 for the expected UV count 1`. The error is not about our file syntax; it's about the engine refusing to accept user-space registration for this specific block at all.

Evidence backing this theory:
- BDS 1.26.14.1's own `resource_packs/vanilla/terrain_texture.json` does **not** contain a firefly_bush entry
- Firefly bush was added in vanilla BP 1.21.70 (per `behavior_packs/vanilla_1.21.70/feature_rules/overworld_after_surface_firefly_bush_water_cluster.json`) — so it's a newer block with stricter engine-side registration handling
- We are the only place `firefly_bush` appears in the entire pack stack; no other mod, no other sampler file references it

**What worked in v0.5.3**:
1. Removed the `firefly_bush` entry entirely from `terrain_texture.json`
2. Placed the Patrix texture at the default path `textures/blocks/firefly_bush.png` (created as a copy of the existing `firefly_bush_v0.png`)

With no `terrain_texture.json` registration, Bedrock falls back to its default convention — looking for `textures/blocks/<block_name>.png`. The Patrix texture is now at that exact path, so the engine picks it up without us having to register it, and no atlas-index check is triggered.

`firefly_bush_v0.png`, `_v1.png`, `_v2.png` remain on disk (harmless, unused at runtime). Recoverable if the engine behavior changes or we want per-block-state variants in a future iteration.

---

## Pack load order after install

Installing this .mcaddon adds 8 packs to Minecraft's pack lists, split across **Behavior Packs** and **Resource Packs** pages.

**Behavior Packs (top of list → bottom):**
| # | Pack (in-game display name) |
|---|---|
| 1 | `FallingTree BP [VV TEST RUN v2.8.1]` |
| 2 | `PatrixCanopyGen [VV TEST RUN v0.1.2]` |
| 3 | `PatrixWorld-Tectonic BP [VV TEST RUN v0.7.2]` |
| 4 | `pw_variants BP [ZOMBIE-PROOF v0.1.1]` |

**Resource Packs (top of list → bottom):**
| # | Pack (in-game display name) |
|---|---|
| 1 | `PatrixWorld Sampler [PAT+ALAC BLEND v0.4.2]` |
| 2 | `FallingTree RP [VV TEST RUN v2.8.1]` |
| 3 | `PatrixWorld-Tectonic RP [VV TEST RUN v0.7.2]` |
| 4 | `pw_variants RP [ZOMBIE-PROOF v0.1.2]` |

(Bedrock stacks packs in activation order; entries at the top of the list override entries below when two packs touch the same texture/entity. For this bundle nothing overlaps — each pack owns its own content — so order has no visible effect, but this is what you'll see.)

---

## What to test in a fresh Realms world

Load `Unified-Abs0lut-Claude-v0.5.3-FIREFLY-FIX.mcaddon`, enable all 8 packs.

**Primary goal: zero-error load.**

### Content log expected output
- ✅ Two `[Scripting][warning]` load banners (BIGCANOPY + pw_variants) — these are script startup messages, not errors
- ✅ **Zero** `[Texture][error]` messages
- ✅ **Zero** `[Texture][warning]` messages
- ✅ **Zero** `[Animation][error]` messages

### Visual check
Natural-spawn firefly bushes (swamp biome) should render with the Patrix texture at the default path. If they look like plain vanilla instead of Patrix, the default-path lookup didn't pick up our file — escalate.

All other visuals from v0.5.1 / v0.5.2 remain: zombie variants, BIGCANOPY falling trees, PatrixCanopyGen tree shapes, Tectonic biome water profiles.

---

## Critical / catastrophic failure recovery

Same as prior iterations:
- Full rollback → load `Unified-Abs0lut-Claude-v0.5.2-ERRORS-FIXED.mcaddon` (still in outputs)
- Double rollback → `Unified-Abs0lut-Claude-v0.5.1-ZOMBIE-PROOF.mcaddon`
- Triple rollback → `Unified-Abs0lut-Claude-v0.5.0.mcaddon`

**If firefly_bush still errors after this fix:**
It would mean Bedrock triggers the atlas check even on default-path lookup. In that case: rename/delete the PNG so Bedrock can't find our override at all, falling back to the baseline Bedrock texture. Loses Patrix aesthetics for firefly_bush but eliminates the error.

**If firefly_bush renders as missing-texture magenta:**
The default path didn't resolve. Check the .mcaddon has `textures/blocks/firefly_bush.png` inside the Sampler mcpack. If yes, the PNG might need to be placed somewhere different — try `textures/blocks/firefly_bush_top.png` or similar naming variants.

---

## Turn 3 preview (unchanged)

Once this iteration loads cleanly, Turn 3 begins: subpack tier slider (32x / 64x / 128x / 256x / 512x) on the Sampler pack. Zombie textures populated across all 5 tiers as end-to-end validation. Then v0.5.x mob-by-mob expansion.
